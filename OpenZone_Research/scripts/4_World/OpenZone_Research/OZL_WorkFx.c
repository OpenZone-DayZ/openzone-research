// Вигляд «робота» станції (R09, правила доведення docs/polish.md §3 у проєкті моделей): поки станція
// працює, на машині гравця крутиться луп -- екрани й лампи у вигляді «робота», кістки по колу, лампи
// блимають, стрілки хитаються, кадри екрана змінюються. Що саме -- опис class OZL_Work у config.cpp
// класу; коду на кожну станцію немає. Сервер не робить нічого: стан приходить netsync (m_OZL_State),
// це лише косметика, і кожен клієнт крутить свій луп сам (як BatteryCharger блимає лампами).
//
// Опис у config.cpp класу (усе необов'язкове):
//   class OZL_Work
//   {
//       onSelections[] = {"ozl_screen", "ozl_lamp"};  // з hiddenSelections: на час роботи - ці
//       onTextures[]   = {"..._on_co.paa", "..._on_co.paa"};   // текстури й матеріали, після -
//       onMaterials[]  = {"..._on.rvmat", "..._on.rvmat"};     // ті, що в hiddenSelectionsTextures/Materials
//       class Spin   { type = "loop";   source = "ozl_work"; };
//       class Lamp   { type = "blink";  selection = "ozl_lamp"; on = 0.5; off = 0.5; };
//       class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.6; amp = 0.08; period = 1.7; };
//       class Dump   { type = "frames"; selection = "ozl_screen"; period = 0.25; textures[] = {"...", "..."}; };
//       class Feed   { type = "pose";   source = "ozl_feed"; };
//   };
// loop: джерело AnimationSources (source = "user") іде 0 -> 1 за свій animPeriod і знову з 0; кістку
//   по колу крутить model.cfg: angle1 = 2 пі на maxValue < 1 і sourceAddress = "loop" -- кілька
//   обертів за один прохід (перевірено на стенді 26.10, тест T01). Ціле число обертів за прохід --
//   стик 1 -> 0 непомітний.
// wobble: фаза джерела = mid + amp * sin(2 пі t / period) -- стрілки, пера, що «живуть». Входить у хитання
//   і повертається в 0 плавно, за RAMP_SEC (без ривка на старті й зупинці).
// blink: виділення по черзі у вигляді «робота» (on секунд) і звичайному (off секунд).
// frames: текстури виділення по колу, кожна по period секунд (екран без власної кістки).
// pose: на час роботи джерело йде в 1 (рушій веде його за animPeriod: головка верстата опускається),
//   після роботи -- назад у 0 (піднімається); між ними нічого не робиться.
// ozlWorkFxAlways = 1 у класі -- луп завжди: тестові класи стенду показують «роботу» без запуску правила.

class OZL_WorkFxPart
{
    string Kind;
    string Src;
    string Sel;
    int    Idx = -1;
    float  OnSec;
    float  OffSec;
    float  Mid;
    float  Amp;
    float  PeriodSec;
    ref array<string> Textures;
    string LitTex;
    string LitMat;
    float  Elapsed;
    int    FrameNo;
    bool   Lit;
    float  From;       // wobble: фаза, з якої стрілка плавно входить у хитання або повертається в 0
    float  Last;       // wobble: остання поставлена фаза
    int    Ticks;          // frames: тіки від останнього кадру
    int    TicksPerFrame;  // frames: кадр міняється раз на стільки тіків (найменше k, що k * TICK >= period)
}

class OZL_WorkFx
{
    static const float TICK = 0.05;
    // далі від камери -- лише перезапуск петель (рух рахує рушій), без дрібних змін текстур і фаз
    static const float NEAR_M = 60.0;
    // стрілки (wobble) входять у хитання і повертаються в 0 плавно, за стільки секунд. Раніше на старті
    // фаза стрибала в mid за animPeriod (0,2 с), а на зупинці -- миттєво в 0 (відгук користувача 28.10, M30)
    static const float RAMP_SEC = 1.5;

    protected EntityAI m_Ent;
    protected string   m_Path;
    protected ref array<int>    m_OnIdx;
    protected ref array<string> m_OnTex;
    protected ref array<string> m_OnMat;
    protected ref array<ref OZL_WorkFxPart> m_Parts;
    protected ref Timer m_Timer;
    protected bool m_Running;
    protected bool m_Stopping;      // робота скінчилась, стрілки ще повертаються в 0
    protected float m_StopElapsed;
    protected bool m_WasClose;      // минулого тіку камера була ближче NEAR_M

    static bool Has(EntityAI ent)
    {
        return ent && GetGame().ConfigIsExisting("CfgVehicles " + ent.GetType() + " OZL_Work");
    }

    void OZL_WorkFx(EntityAI ent)
    {
        m_Ent = ent;
        m_Path = "CfgVehicles " + ent.GetType() + " OZL_Work";
        m_OnIdx = new array<int>();
        m_OnTex = new array<string>();
        m_OnMat = new array<string>();
        m_Parts = new array<ref OZL_WorkFxPart>();

        array<string> sels = new array<string>();
        GetGame().ConfigGetTextArray(m_Path + " onSelections", sels);
        GetGame().ConfigGetTextArray(m_Path + " onTextures", m_OnTex);
        GetGame().ConfigGetTextArray(m_Path + " onMaterials", m_OnMat);
        for (int i = 0; i < sels.Count(); i++)
            m_OnIdx.Insert(ent.GetHiddenSelectionIndex(sels[i]));

        int n = GetGame().ConfigGetChildrenCount(m_Path);
        for (int c = 0; c < n; c++)
        {
            string name;
            GetGame().ConfigGetChildName(m_Path, c, name);
            string p = m_Path + " " + name;
            if (!GetGame().ConfigIsExisting(p + " type"))
                continue;
            OZL_WorkFxPart part = new OZL_WorkFxPart();
            part.Kind      = GetGame().ConfigGetTextOut(p + " type");
            part.Src       = GetGame().ConfigGetTextOut(p + " source");
            part.Sel       = GetGame().ConfigGetTextOut(p + " selection");
            part.OnSec     = GetGame().ConfigGetFloat(p + " on");
            part.OffSec    = GetGame().ConfigGetFloat(p + " off");
            part.Mid       = GetGame().ConfigGetFloat(p + " mid");
            part.Amp       = GetGame().ConfigGetFloat(p + " amp");
            part.PeriodSec = GetGame().ConfigGetFloat(p + " period");
            part.Textures  = new array<string>();
            GetGame().ConfigGetTextArray(p + " textures", part.Textures);
            if (part.Sel != "")
            {
                part.Idx = ent.GetHiddenSelectionIndex(part.Sel);
                int k = sels.Find(part.Sel);
                if (k > -1 && k < m_OnTex.Count())
                    part.LitTex = m_OnTex[k];
                if (k > -1 && k < m_OnMat.Count())
                    part.LitMat = m_OnMat[k];
            }
            if (part.Kind == "loop")
            {
                // прохід петлі -- animPeriod самого джерела: рушій веде фазу 0 -> 1 рівно за нього
                part.PeriodSec = GetGame().ConfigGetFloat("CfgVehicles " + ent.GetType() + " AnimationSources " + part.Src + " animPeriod");
            }
            if (part.PeriodSec <= 0)
                part.PeriodSec = 1.0;
            if (part.OnSec <= 0)
                part.OnSec = 0.5;
            if (part.OffSec <= 0)
                part.OffSec = 0.5;
            part.TicksPerFrame = Math.Ceil(part.PeriodSec / TICK - 0.001);
            if (part.TicksPerFrame < 1)
                part.TicksPerFrame = 1;
            m_Parts.Insert(part);
        }
    }

    void ~OZL_WorkFx()
    {
        if (m_Timer)
            m_Timer.Stop();
    }

    bool IsRunning()
    {
        return m_Running;
    }

    void Start()
    {
        if (m_Running || !m_Ent)
            return;
        bool wasStopping = m_Stopping;
        m_Running = true;
        m_Stopping = false;
        for (int i = 0; i < m_OnIdx.Count(); i++)
            SetLook(m_OnIdx[i], Pick(m_OnTex, i), Pick(m_OnMat, i));
        foreach (OZL_WorkFxPart part : m_Parts)
        {
            part.Elapsed = 0;
            part.FrameNo = 0;
            part.Ticks = 0;
            part.Lit = true;
            if (part.Kind == "wobble")
            {
                // зі спокою -- від 0; якщо стрілка ще поверталась -- з того місця, де вона зараз
                if (!wasStopping)
                    part.Last = 0;
                part.From = part.Last;
            }
            else if (part.Kind == "loop")
            {
                m_Ent.ResetAnimationPhase(part.Src, 0);
                m_Ent.SetAnimationPhase(part.Src, 1);
            }
            else if (part.Kind == "pose")
                m_Ent.SetAnimationPhase(part.Src, 1);
            else if (part.Kind == "frames" && part.Textures.Count() > 0)
                SetLook(part.Idx, part.Textures[0], "");
        }
        if (!m_Timer)
            m_Timer = new Timer(CALL_CATEGORY_SYSTEM);
        m_Timer.Run(TICK, this, "Tick", null, true);
    }

    void Stop()
    {
        if (!m_Running)
            return;
        m_Running = false;
        if (!m_Ent)
        {
            if (m_Timer)
                m_Timer.Stop();
            return;
        }
        bool needles = false;
        foreach (OZL_WorkFxPart part : m_Parts)
        {
            if (part.Kind == "wobble")
            {
                // у 0 -- плавно, у Tick за RAMP_SEC
                part.From = part.Last;
                needles = true;
            }
            else if (part.Kind == "loop")
                m_Ent.ResetAnimationPhase(part.Src, 0);
            else if (part.Kind == "pose")
                m_Ent.SetAnimationPhase(part.Src, 0);
            else if (part.Idx > -1)
                Restore(part.Idx);
        }
        for (int i = 0; i < m_OnIdx.Count(); i++)
            Restore(m_OnIdx[i]);
        if (needles && m_Timer)
        {
            m_Stopping = true;
            m_StopElapsed = 0;
        }
        else if (m_Timer)
            m_Timer.Stop();
    }

    // Плавний крок 0..1 (smoothstep): стрілка рушає і стає без ривка.
    protected static float Smooth(float x)
    {
        x = Math.Clamp(x, 0, 1);
        return x * x * (3 - 2 * x);
    }

    // Після роботи: стрілки за RAMP_SEC повертаються з того місця, де були, у 0, потім таймер стає.
    protected void TickStopping()
    {
        m_StopElapsed = m_StopElapsed + TICK;
        float k = Smooth(m_StopElapsed / RAMP_SEC);
        foreach (OZL_WorkFxPart part : m_Parts)
        {
            if (part.Kind != "wobble")
                continue;
            part.Last = part.From * (1 - k);
            m_Ent.SetAnimationPhase(part.Src, part.Last);
        }
        if (m_StopElapsed >= RAMP_SEC)
        {
            m_Stopping = false;
            if (m_Timer)
                m_Timer.Stop();
        }
    }

    // Кличеться таймером на ім'я -- мусить бути видимим.
    void Tick()
    {
        if (!m_Ent)
        {
            Stop();
            if (m_Timer)
                m_Timer.Stop();
            return;
        }
        if (m_Stopping)
        {
            TickStopping();
            return;
        }
        bool close = vector.Distance(GetGame().GetCurrentCameraPosition(), m_Ent.GetPosition()) < NEAR_M;
        // гравець щойно підійшов: кадри показати ті, що набігли, поки був далеко
        bool refresh = close && !m_WasClose;
        m_WasClose = close;
        foreach (OZL_WorkFxPart part : m_Parts)
        {
            part.Elapsed = part.Elapsed + TICK;
            if (part.Kind == "pose")
                continue;
            if (part.Kind == "loop")
            {
                if (part.Elapsed >= part.PeriodSec)
                {
                    part.Elapsed = part.Elapsed - part.PeriodSec;
                    m_Ent.ResetAnimationPhase(part.Src, 0);
                    m_Ent.SetAnimationPhase(part.Src, 1);
                }
            }
            else if (part.Kind == "frames" && part.Textures.Count() > 0)
            {
                // кадри рахуються тіками й далеко від камери (текстура міняється лише поблизу): стрічка самописця
                // M04, M06 і перо (wobble рахує той самий час) не розходяться, коли гравець повертається
                part.Ticks = part.Ticks + 1;
                int steps = part.Ticks / part.TicksPerFrame;
                if (steps > 0)
                {
                    part.Ticks = part.Ticks - steps * part.TicksPerFrame;
                    part.FrameNo = (part.FrameNo + steps) % part.Textures.Count();
                }
                if (close && (steps > 0 || refresh))
                    SetLook(part.Idx, part.Textures[part.FrameNo], "");
            }
            else if (!close)
                continue;
            else if (part.Kind == "wobble")
            {
                // перші RAMP_SEC -- від From до хитання плавно, далі просто хитання
                float sway = part.Mid + part.Amp * Math.Sin(Math.PI2 * part.Elapsed / part.PeriodSec);
                part.Last = part.From + (sway - part.From) * Smooth(part.Elapsed / RAMP_SEC);
                m_Ent.SetAnimationPhase(part.Src, part.Last);
            }
            else if (part.Kind == "blink")
            {
                float span = part.OffSec;
                if (part.Lit)
                    span = part.OnSec;
                if (part.Elapsed >= span)
                {
                    part.Elapsed = 0;
                    part.Lit = !part.Lit;
                    if (part.Lit)
                        SetLook(part.Idx, part.LitTex, part.LitMat);
                    else
                        Restore(part.Idx);
                }
            }
        }
    }

    protected static string Pick(array<string> arr, int i)
    {
        if (i < arr.Count())
            return arr[i];
        return "";
    }

    protected void SetLook(int index, string tex, string mat)
    {
        if (index < 0)
            return;
        if (tex != "")
            m_Ent.SetObjectTexture(index, tex);
        if (mat != "")
            m_Ent.SetObjectMaterial(index, mat);
    }

    // Назад до вигляду з конфігу класу (hiddenSelectionsTextures / Materials).
    protected void Restore(int index)
    {
        if (index < 0 || !m_Ent.GetHiddenSelectionsData())
            return;
        TStringArray tex = m_Ent.GetHiddenSelectionsData().GetHiddenSelectionsTextures();
        TStringArray mat = m_Ent.GetHiddenSelectionsData().GetHiddenSelectionsMaterials();
        if (index < tex.Count())
            m_Ent.SetObjectTexture(index, tex[index]);
        if (index < mat.Count())
            m_Ent.SetObjectMaterial(index, mat[index]);
    }
}
