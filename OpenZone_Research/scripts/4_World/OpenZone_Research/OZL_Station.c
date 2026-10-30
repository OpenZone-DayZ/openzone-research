// Станція: сировина в карго, запуск дією, робота за календарною міткою,
// результат у карго. Машина станів у netsync: 0 вільна, 1 працює, 2 стоїть
// із незакладеним результатом.
//
// Входи й витратні матеріали списуються ПРИ СТАРТІ, тоді ж заморожується
// чистота циклу; кидок шансу йде наприкінці -- можливо, після рестарту, коли
// з'їдених предметів давно немає. Дедлайн -- OZL_Clock (календар), таймер
// лише звіряється з ним. Це порт вимог ZP_Devices.c на службах ядра:
// власник -- OZL_Owner, стан фракції -- OZL_State, конфіги -- OZL_Config.
//
// Карго не блокується ніколи: вхід спожито при старті, заморожувати нічого,
// а заборона приймання в хуку загрожувала б вмісту карго при завантаженні
// зі сховища (itembase.c: Bohemia вимкнула власну перевірку з тієї ж
// причини). Замість цього працюючу станцію не можна нести й брати в руки.

class OZL_Station : ItemBase
{
    static const int STATE_IDLE    = 0;
    static const int STATE_RUNNING = 1;
    static const int STATE_DONE    = 2;

    // Таймер планується на залишок часу; стеля лишає точку перевірки для
    // крайових випадків (правило вимкнули, конфіг ще не прочитано).
    private static const int POLL_MAX_SEC = 60;

    protected int    m_OZL_State;
    protected string m_OZL_RuleId;
    protected int    m_OZL_EndSec;
    protected string m_OZL_StarterUid;     // лише мітка для логів
    protected string m_OZL_StarterOwner;   // власник на момент старту: гейти автоциклу, сброс

    // Те, чому не знайшлося місця в карго: запис у станції, а не річ у світі.
    // Два паралельні масиви -- класи й рядки предметів (OZL_Payload).
    protected ref array<string> m_OZL_PendingItems;
    protected ref array<string> m_OZL_PendingPayloads;

    // Заморожені при старті. Пакувальник: чистота проб циклу й шанс подвійного
    // виходу від модулів. Аналізатор: множник шансу (чистота проби) і бали, що
    // перейдуть у носій.
    protected float m_OZL_CyclePurity;
    protected float m_OZL_ChanceMul;
    protected float m_OZL_DoubleChance;
    protected int   m_OZL_CyclePoints;

    // Вироблене останнім циклом -- щоб автопродовження не взяло власний
    // вихід за сировину.
    protected ref array<string> m_OZL_ExcludeCls;

    protected ref Timer m_OZL_Timer;

    // Вигляд «робота» на клієнті (OZL_WorkFx.c): луп, поки стан RUNNING.
    protected ref OZL_WorkFx m_OZL_WorkFx;

    // Усі живі станції, не лише статики: сброс фракції має зупиняти й
    // переносні, інакше запущена до сбросу станція доробить і заллє носій у
    // щойно обнулений пул.
    static ref array<OZL_Station> s_All = new array<OZL_Station>();

    void OZL_Station()
    {
        // Реєстрація лише в конструкторі -- пізніша мовчки не працює.
        RegisterNetSyncVariableInt("m_OZL_State", 0, 2);
        m_OZL_PendingItems    = new array<string>();
        m_OZL_PendingPayloads = new array<string>();
        m_OZL_ChanceMul = 1.0;
    }

    void ~OZL_Station()
    {
        OZL_StopTimer();
        if (m_OZL_WorkFx)
            m_OZL_WorkFx.Stop();
        if (GetGame())
        {
            GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(OZL_ResumeAfterLoad);
            GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(OZL_TryAutoContinue);
            GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(OZL_UpdateWorkFx);
        }
    }

    override void EEInit()
    {
        super.EEInit();
        if (GetGame().IsDedicatedServer())
        {
            if (s_All.Find(this) < 0)
                s_All.Insert(this);
            // Початковий пуш стану: сервер позначає змінну брудною лише при
            // старті, сбросі й відновленні, а вільний статик не проходить
            // жодну з цих точок -- без пушу підказка дії не з'являлась би до
            // першого запуску.
            SetSynchDirty();
        }
        else
        {
            // Стан може не змінитися ніколи (тестовий клас із ozlWorkFxAlways), а
            // OnVariablesSynchronized -- не прийти: перевірка після ініціалізації.
            GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(OZL_UpdateWorkFx, 500, false);
        }
    }

    override void OnVariablesSynchronized()
    {
        super.OnVariablesSynchronized();
        OZL_UpdateWorkFx();
    }

    // Клієнт: луп вигляду «робота», поки станція працює (class OZL_Work у
    // config.cpp класу, OZL_WorkFx.c), разом із модулями в слотах. Сервер не
    // робить нічого -- косметика.
    bool OZL_WorkFxOn()
    {
        return m_OZL_State == STATE_RUNNING || ConfigGetBool("ozlWorkFxAlways");
    }

    void OZL_UpdateWorkFx()
    {
        if (!GetGame() || GetGame().IsDedicatedServer())
            return;
        bool on = OZL_WorkFxOn();
        for (int i = 1; i <= 3; i++)
        {
            int slot = InventorySlots.GetSlotIdFromString("OZL_Tool" + i.ToString());
            OZL_Tool_Base tool = OZL_Tool_Base.Cast(GetInventory().FindAttachment(slot));
            if (tool)
                tool.OZL_SetWorking(on);
        }
        if (on && !m_OZL_WorkFx)
        {
            if (!OZL_WorkFx.Has(this))
                return;
            m_OZL_WorkFx = new OZL_WorkFx(this);
        }
        if (!m_OZL_WorkFx)
            return;
        if (on)
            m_OZL_WorkFx.Start();
        else
            m_OZL_WorkFx.Stop();
    }

    // Модуль, вставлений у працюючу станцію, одразу «працює» з нею; вийнятий -- гасне.
    override void EEItemAttached(EntityAI item, string slot_name)
    {
        super.EEItemAttached(item, slot_name);
        OZL_Tool_Base tool = OZL_Tool_Base.Cast(item);
        if (tool && GetGame() && !GetGame().IsDedicatedServer())
            tool.OZL_SetWorking(OZL_WorkFxOn());
    }

    override void EEItemDetached(EntityAI item, string slot_name)
    {
        super.EEItemDetached(item, slot_name);
        OZL_Tool_Base tool = OZL_Tool_Base.Cast(item);
        if (tool && GetGame() && !GetGame().IsDedicatedServer())
            tool.OZL_SetWorking(false);
    }

    override void EEDelete(EntityAI parent)
    {
        OZL_StopTimer();
        if (m_OZL_WorkFx)
            m_OZL_WorkFx.Stop();
        int idx = s_All.Find(this);
        if (idx > -1)
            s_All.Remove(idx);
        if (GetGame())
        {
            GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(OZL_ResumeAfterLoad);
            GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(OZL_TryAutoContinue);
        }
        super.EEDelete(parent);
    }

    int OZL_GetState()
    {
        return m_OZL_State;
    }

    string OZL_RuleId()
    {
        return m_OZL_RuleId;
    }

    int OZL_EndSec()
    {
        return m_OZL_EndSec;
    }

    string OZL_StarterOwner()
    {
        return m_OZL_StarterOwner;
    }

    // «Зайнята» = працює або стоїть із незакладеним виходом.
    bool OZL_IsBusy()
    {
        return m_OZL_State == STATE_RUNNING || m_OZL_State == STATE_DONE;
    }

    bool OZL_HasPending()
    {
        return m_OZL_PendingItems.Count() > 0;
    }

    // Модуль ставиться лише на пакувальник своєї лінії (OZL_Modules.AllowedOn):
    // відповідь -- з config.cpp, однакова на сервері й клієнті. Перекриваємо саме
    // ручну вставку, а не CanLoadAttachment: той рушій кличе при завантаженні
    // зі сховища, і відмова там позбавила б прилад модуля після рестарту.
    override bool CanReceiveAttachment(EntityAI attachment, int slotId)
    {
        if (attachment && !OZL_Modules.AllowedOn(attachment.GetType(), GetType()))
            return false;
        return super.CanReceiveAttachment(attachment, slotId);
    }

    // Інструмент, потрібний правилу, не виймається, поки йде робота:
    // сировину списано при старті, і зупинка означала б тиху втрату
    // матеріалу через випадкове перетягування. Точково -- лише інструменти
    // правила, що зараз виконується; правило зникло -- не блокуємо взагалі.
    override bool CanReleaseAttachment(EntityAI attachment)
    {
        if (m_OZL_State == STATE_RUNNING && attachment && OZL_Config.Get().Revision() > 0)
        {
            OZL_Rule running = OZL_Config.Get().Rules().Find(m_OZL_RuleId);
            if (running && OZL_Match.InList(attachment.GetType(), running.RequiredTools))
                return false;
        }
        return super.CanReleaseAttachment(attachment);
    }

    // Зайняту станцію не носять: у чужому контейнері спавн у її карго не
    // працює, і результат нікуди було б видати.
    override bool CanPutInCargo(EntityAI parent)
    {
        if (OZL_IsBusy())
            return false;
        return super.CanPutInCargo(parent);
    }

    override bool CanPutIntoHands(EntityAI parent)
    {
        if (OZL_IsBusy())
            return false;
        return super.CanPutIntoHands(parent);
    }

    // ---------- таймер ----------

    protected void OZL_StartTimer()
    {
        if (!m_OZL_Timer)
            m_OZL_Timer = new Timer(CALL_CATEGORY_SYSTEM);
        if (m_OZL_Timer.IsRunning())
            m_OZL_Timer.Stop();
        int left = m_OZL_EndSec - OZL_Clock.NowSec();
        if (left < 1)
            left = 1;
        if (left > POLL_MAX_SEC)
            left = POLL_MAX_SEC;
        m_OZL_Timer.Run(left, this, "OZL_Poll", null, true);
    }

    protected void OZL_StopTimer()
    {
        if (m_OZL_Timer)
            m_OZL_Timer.Stop();
    }

    // Кличеться таймером на ім'я -- мусить бути видимим.
    void OZL_Poll()
    {
        if (m_OZL_State != STATE_RUNNING)
        {
            OZL_StopTimer();
            return;
        }
        int now = OZL_Clock.NowSec();
        if (now >= m_OZL_EndSec)
        {
            OZL_Complete();
            return;
        }
        OZL_Log.Dbg("station " + GetType() + " poll early: now=" + now.ToString() + " end=" + m_OZL_EndSec.ToString());
    }

    // ---------- старт ----------

    // Сервер: запуск за правилом, знайденим у карго. Відповідь -- ключ рядка
    // в обох випадках; той, хто кликав, шле його гравцеві звісткою.
    bool OZL_Start(PlayerBase who, out string why)
    {
        why = "";
        if (!GetGame().IsServer())
        {
            why = "STR_OZ_ERR_INTERNAL";
            return false;
        }
        if (m_OZL_State == STATE_DONE)
        {
            why = "STR_OZL_ERR_STATION_DONE";
            return false;
        }
        if (m_OZL_State != STATE_IDLE)
        {
            why = "STR_OZL_ERR_STATION_BUSY";
            return false;
        }
        if (!who)
        {
            why = "STR_OZ_ERR_INTERNAL";
            return false;
        }

        string owner = OZL_Owner.OfPlayer(who);
        if (!OZL_Config.Get().Owners().IsDeviceFor(owner, GetType()))
        {
            OZL_Log.Dbg("station " + GetType() + ": owner '" + owner + "' does not own it");
            why = "STR_OZL_ERR_NOT_YOUR_DEVICE";
            return false;
        }

        OZL_Rule rule = OZL_RuleEngine.FindStartable(this, who, owner, why);
        if (!rule)
            return false;

        string uid = "";
        if (who.GetIdentity())
            uid = who.GetIdentity().GetPlainId();

        if (!OZL_Begin(rule, owner, uid, why))
            return false;

        why = "STR_OZL_MSG_STARTED";
        return true;
    }

    // Спільний шлях ручного запуску й автопродовження: план, знімок чистоти,
    // списання, дедлайн, таймер. Сировина зникає ПРИ СТАРТІ: скасування або
    // вимкнення правила адміном її не повертає.
    protected bool OZL_Begin(OZL_Rule rule, string owner, string uid, out string why)
    {
        array<ItemBase> planItems   = new array<ItemBase>();
        array<int>      planAmounts = new array<int>();
        array<int>      planInputs  = new array<int>();
        string planWhy;
        if (!OZL_RuleEngine.BuildCargoPlan(this, rule, planItems, planAmounts, planInputs, planWhy))
        {
            why = "STR_OZL_ERR_NEED_INPUT";
            OZL_Log.Dbg("station " + GetType() + " '" + rule.Id + "': " + planWhy);
            return false;
        }

        // Знімок до списання: після нього предметів уже немає.
        m_OZL_CyclePurity  = rule.Purity;
        m_OZL_ChanceMul    = 1.0;
        m_OZL_DoubleChance = 0;
        m_OZL_CyclePoints  = 0;
        int samplePct;
        if (OZL_RuleEngine.PlanSample(planItems, planInputs, m_OZL_CyclePoints, samplePct))
        {
            // Аналіз: чистота проби -- шанс, її бали перейдуть у носій.
            m_OZL_ChanceMul = samplePct / 100.0;
        }
        else
        {
            // Пакування: модулі лінії додають чистоти й шансу подвійного виходу.
            float bonusPurity;
            float bonusDouble;
            OZL_Gear.ModuleBonuses(this, bonusPurity, bonusDouble);
            m_OZL_CyclePurity += bonusPurity;
            m_OZL_DoubleChance = bonusDouble;
        }
        OZL_RuleEngine.ConsumePlan(planItems, planAmounts);

        // ЦІЛІ СЕКУНДИ, І ЛИШЕ ЦІЛІ. Календарні секунди -- число близько
        // 2^28, а float має 24 біти мантиси: `NowSec() + time` з float time
        // округлювалось до кратного шістнадцяти, і дедлайн їхав на 0..16 с
        // (виміряно 2026-09-20: end - now = 16 при time = 10).
        float time = OZL_Rules.EffectiveTimeSec(rule.TimeSec);
        int timeSec = time;
        m_OZL_RuleId       = rule.Id;
        m_OZL_StarterUid   = uid;
        m_OZL_StarterOwner = owner;
        m_OZL_EndSec       = OZL_Clock.NowSec() + timeSec;
        m_OZL_State        = STATE_RUNNING;
        SetSynchDirty();
        OZL_StartTimer();

        string line = "station " + GetType() + " started rule '" + rule.Id + "'";
        line += " owner=" + owner + " by=" + uid;
        line += " purity=" + m_OZL_CyclePurity.ToString() + " points=" + m_OZL_CyclePoints.ToString();
        line += " chanceMul=" + m_OZL_ChanceMul.ToString() + " double=" + m_OZL_DoubleChance.ToString();
        line += " time=" + timeSec.ToString() + "s";
        line += " end=" + m_OZL_EndSec.ToString() + " now=" + OZL_Clock.NowSec().ToString();
        OZL_Log.Dbg(line);
        return true;
    }

    // ---------- завершення ----------

    protected void OZL_Complete()
    {
        OZL_StopTimer();
        // Конфіг ще не прочитано (ранній бут): не скасовувати легітимний
        // процес, повторити на наступному тіку.
        if (OZL_Config.Get().Revision() == 0)
        {
            OZL_Log.Warn("station " + GetType() + ": configs not loaded yet, completion deferred");
            OZL_StartTimer();
            return;
        }
        OZL_Rule rule = OZL_Config.Get().Rules().Find(m_OZL_RuleId);
        if (!rule)
        {
            OZL_Cancel("rule '" + m_OZL_RuleId + "' is gone from the configs");
            return;
        }
        if (!rule.Enabled)
        {
            OZL_Cancel("rule '" + m_OZL_RuleId + "' was disabled");
            return;
        }

        // Цикл закінчується: кидки шансу один раз, вихід одразу в карго.
        array<string> items    = new array<string>();
        array<string> payloads = new array<string>();
        OZL_RuleEngine.ResolveResult(rule, m_OZL_ChanceMul, m_OZL_DoubleChance, m_OZL_CyclePoints, OZL_Payload.PurityPct(m_OZL_CyclePurity), items, payloads);

        array<string> producedCls = new array<string>();
        int placed = 0;
        while (items.Count() > 0)
        {
            if (!OZL_RuleEngine.SpawnOneToCargo(this, items[0], payloads[0]))
                break;
            producedCls.Insert(items[0]);
            items.RemoveOrdered(0);
            payloads.RemoveOrdered(0);
            placed++;
        }
        int stuck = items.Count();
        for (int s = 0; s < stuck; s++)
        {
            m_OZL_PendingItems.Insert(items[s]);
            m_OZL_PendingPayloads.Insert(payloads[s]);
        }

        string line = "station " + GetType() + " cycle '" + rule.Id + "' done:";
        line += " placed=" + placed.ToString() + " stuck=" + stuck.ToString();
        line += " owner=" + m_OZL_StarterOwner;
        OZL_Log.Dbg(line);

        // Виключення -- до перевірки на застрягання: інакше конвеєр,
        // відновлений забором, узяв би власний вихід за сировину.
        m_OZL_ExcludeCls = producedCls;

        if (stuck > 0)
        {
            m_OZL_State = STATE_DONE;
            SetSynchDirty();
            OZL_Log.Warn("station " + GetType() + ": cargo is full, the line stopped with " + stuck.ToString() + " item(s) pending");
            return;
        }

        // Наступний цикл не в цьому кадрі: ObjectDelete відкладений до кінця
        // кадру, і негайне пересканування побачило б з'їдену сировину.
        m_OZL_State = STATE_IDLE;
        SetSynchDirty();
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(OZL_TryAutoContinue, 1000, false);
    }

    // Поки в карго лишається придатна сировина, станція бере наступну партію
    // сама. Гравця немає -- гейти йдуть за замороженим власником.
    void OZL_TryAutoContinue()
    {
        if (!GetGame() || !GetGame().IsServer())
            return;
        if (m_OZL_State != STATE_IDLE || IsDamageDestroyed())
            return;
        string owner = m_OZL_StarterOwner;
        if (owner == "")
            owner = OZL_Owner.Fallback();

        string why;
        OZL_Rule next = OZL_RuleEngine.FindAutoContinue(this, owner, m_OZL_ExcludeCls, why);
        if (!next)
        {
            OZL_Log.Dbg("station " + GetType() + ": the line stops, " + why);
            m_OZL_ExcludeCls = null;
            return;
        }
        if (!OZL_Begin(next, owner, m_OZL_StarterUid, why))
        {
            m_OZL_ExcludeCls = null;
        }
    }

    // ---------- забір ----------

    protected void OZL_AlignPending()
    {
        while (m_OZL_PendingPayloads.Count() < m_OZL_PendingItems.Count())
        {
            OZL_Log.Warn("station " + GetType() + ": pending payloads shorter than pending items, padded");
            m_OZL_PendingPayloads.Insert("");
        }
    }

    // Сервер: дозакласти в карго те, що не вмістилось, і повести конвеєр
    // далі. Штатно тут порожньо -- вихід лягає сам одразу після циклу.
    bool OZL_Collect(PlayerBase who, out string why)
    {
        why = "";
        if (!GetGame().IsServer() || !who)
        {
            why = "STR_OZ_ERR_INTERNAL";
            return false;
        }
        string owner = OZL_Owner.OfPlayer(who);
        if (!OZL_Config.Get().Owners().IsDeviceFor(owner, GetType()))
        {
            OZL_Log.Dbg("station " + GetType() + ": owner '" + owner + "' does not own it");
            why = "STR_OZL_ERR_NOT_YOUR_DEVICE";
            return false;
        }
        if (m_OZL_PendingItems.Count() == 0)
        {
            why = "STR_OZL_ERR_NOTHING_PENDING";
            return false;
        }

        OZL_AlignPending();
        int handed = 0;
        int dropped = 0;
        while (m_OZL_PendingItems.Count() > 0)
        {
            string cls = m_OZL_PendingItems[0];
            // Клас міг зникнути з гри, поки запис лежав у сховищі: інакше
            // спавн вічно повертав би null і станція назавжди стояла б.
            if (!OZL_Match.ClassExists(cls))
            {
                OZL_Log.Warn("station " + GetType() + ": class '" + cls + "' is gone from the game, pending entry dropped");
                OZL_DropPending();
                dropped++;
                continue;
            }
            if (!OZL_RuleEngine.SpawnOneToCargo(this, cls, m_OZL_PendingPayloads[0]))
                break;
            if (!m_OZL_ExcludeCls)
                m_OZL_ExcludeCls = new array<string>();
            m_OZL_ExcludeCls.Insert(cls);
            OZL_DropPending();
            handed++;
        }

        int left = m_OZL_PendingItems.Count();
        string line = "station " + GetType() + " collect: handed=" + handed.ToString();
        line += " left=" + left.ToString() + " dropped=" + dropped.ToString();
        OZL_Log.Dbg(line);
        if (left > 0)
        {
            // Нічого не вклалось -- це відмова, а не частковий успіх.
            if (handed == 0)
            {
                why = "STR_OZL_ERR_NO_ROOM";
                return false;
            }
            why = "STR_OZL_MSG_COLLECT_PARTIAL";
            return true;
        }
        m_OZL_State = STATE_IDLE;
        SetSynchDirty();
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(OZL_TryAutoContinue, 1000, false);
        why = "STR_OZL_MSG_COLLECTED";
        return true;
    }

    protected void OZL_DropPending()
    {
        m_OZL_PendingItems.RemoveOrdered(0);
        m_OZL_PendingPayloads.RemoveOrdered(0);
    }

    // ---------- скасування ----------

    protected void OZL_Cancel(string reason)
    {
        OZL_StopTimer();
        OZL_Log.Warn("station " + GetType() + " rule '" + m_OZL_RuleId + "' cancelled: " + reason);
        OZL_ClearState();
        SetSynchDirty();
    }

    // Без SetSynchDirty -- для збоїв завантаження, коли netsync ще не активний.
    protected void OZL_ClearState()
    {
        m_OZL_State        = STATE_IDLE;
        m_OZL_RuleId       = "";
        m_OZL_EndSec       = 0;
        m_OZL_StarterUid   = "";
        m_OZL_StarterOwner = "";
        m_OZL_PendingItems.Clear();
        m_OZL_PendingPayloads.Clear();
        m_OZL_CyclePurity  = 0;
        m_OZL_ChanceMul    = 1.0;
        m_OZL_DoubleChance = 0;
        m_OZL_CyclePoints  = 0;
    }

    // Адмінське скасування: і ГОТОВО теж -- інакше незабраний результат було
    // б неможливо прибрати, а сброс фракції лишив би носій у світі.
    bool OZL_AdminCancel(out string why)
    {
        why = "";
        if (!OZL_IsBusy())
        {
            why = "STR_OZL_ERR_STATION_IDLE";
            return false;
        }
        OZL_Cancel("by admin");
        return true;
    }

    // Сброс фракції зупиняє всі її станції: працюючі й ті, що стоять із
    // результатом. Повертає, скільки зупинено.
    static int CancelAllOf(string owner)
    {
        int n = 0;
        for (int i = 0; i < s_All.Count(); i++)
        {
            OZL_Station st = s_All[i];
            if (!st || !st.OZL_IsBusy() || st.OZL_StarterOwner() != owner)
                continue;
            st.OZL_Cancel("owner '" + owner + "' reset");
            n++;
        }
        return n;
    }

    // ---------- сховище (CF, storageVersion 2 у CfgMods) ----------
    //
    // Потік v2: стан, правило, дедлайн, стартер, власник, кількість
    // незакладених, їхні класи й рядки, чистота циклу, множник шансу, шанс
    // подвійного виходу, бали циклу. Потік v1 (до ліній) не читається: станція
    // стає вільною. Записи CF позиційні: наступна версія лише дописує в кінець
    // і гейтить читання за ctx.GetVersion().

    override void CF_OnStoreSave(CF_ModStorageMap storage)
    {
        super.CF_OnStoreSave(storage);
        auto ctx = storage["OpenZone_Research"];
        if (!ctx)
            return;
        OZL_AlignPending();
        ctx.Write(m_OZL_State);
        ctx.Write(m_OZL_RuleId);
        ctx.Write(m_OZL_EndSec);
        ctx.Write(m_OZL_StarterUid);
        ctx.Write(m_OZL_StarterOwner);
        int count = m_OZL_PendingItems.Count();
        ctx.Write(count);
        int i;
        for (i = 0; i < count; i++)
            ctx.Write(m_OZL_PendingItems[i]);
        for (i = 0; i < count; i++)
            ctx.Write(m_OZL_PendingPayloads[i]);
        ctx.Write(m_OZL_CyclePurity);
        ctx.Write(m_OZL_ChanceMul);
        ctx.Write(m_OZL_DoubleChance);
        ctx.Write(m_OZL_CyclePoints);
    }

    override bool CF_OnStoreLoad(CF_ModStorageMap storage)
    {
        if (!super.CF_OnStoreLoad(storage))
            return false;
        auto ctx = storage["OpenZone_Research"];
        if (!ctx)
            return true;   // сейв старіший за мод: CF пише лише моди з даними

        // Потік чужої версії: у простій, предмети цілі, попередження в лог.
        // Читати його наосліп означало б з'їсти записи сусідніх модів.
        if (ctx.GetVersion() != 2)
        {
            OZL_Log.Warn("station " + GetType() + ": stream v" + ctx.GetVersion().ToString() + " is not v2, state reset to idle");
            OZL_ClearState();
            return true;
        }

        // Пошкоджений потік: CF на false сутність не видаляє -- без сбросу
        // станція лишилася б назавжди зайнятою.
        if (!OZL_ReadStream(ctx))
        {
            OZL_Log.Warn("station " + GetType() + ": stream is damaged, state reset to idle");
            OZL_ClearState();
            return false;
        }

        if (m_OZL_State == STATE_RUNNING || m_OZL_State == STATE_DONE)
        {
            if (GetGame().IsDedicatedServer())
            {
                // Карго і світ мають дозавантажитись; далі -- за міткою часу.
                GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(OZL_ResumeAfterLoad, 2000, false);
            }
            else
            {
                // Офлайн (діаг): відновлення не планується, інакше станція
                // назавжди лишилась би зайнятою.
                OZL_ClearState();
            }
        }
        return true;
    }

    private bool OZL_ReadStream(CF_ModStorage ctx)
    {
        if (!ctx.Read(m_OZL_State))
            return false;
        if (!ctx.Read(m_OZL_RuleId))
            return false;
        if (!ctx.Read(m_OZL_EndSec))
            return false;
        if (!ctx.Read(m_OZL_StarterUid))
            return false;
        if (!ctx.Read(m_OZL_StarterOwner))
            return false;
        int count;
        if (!ctx.Read(count))
            return false;
        if (count < 0 || count > 1000)
            return false;
        m_OZL_PendingItems.Clear();
        m_OZL_PendingPayloads.Clear();
        int i;
        string s;
        for (i = 0; i < count; i++)
        {
            if (!ctx.Read(s))
                return false;
            m_OZL_PendingItems.Insert(s);
        }
        for (i = 0; i < count; i++)
        {
            if (!ctx.Read(s))
                return false;
            m_OZL_PendingPayloads.Insert(s);
        }
        if (!ctx.Read(m_OZL_CyclePurity))
            return false;
        if (!ctx.Read(m_OZL_ChanceMul))
            return false;
        if (!ctx.Read(m_OZL_DoubleChance))
            return false;
        if (!ctx.Read(m_OZL_CyclePoints))
            return false;
        return true;
    }

    void OZL_ResumeAfterLoad()
    {
        if (m_OZL_State == STATE_DONE)
        {
            SetSynchDirty();
            OZL_Log.Dbg("station " + GetType() + " restored '" + m_OZL_RuleId + "': the line stands, pending=" + m_OZL_PendingItems.Count().ToString());
            return;
        }
        if (m_OZL_State != STATE_RUNNING)
            return;
        SetSynchDirty();
        OZL_StartTimer();
        int left = m_OZL_EndSec - OZL_Clock.NowSec();
        OZL_Log.Dbg("station " + GetType() + " resumed '" + m_OZL_RuleId + "', " + left.ToString() + " s left");
    }
}

// Стаціонарна станція: лишається ItemBase (карго, netsync, сховище CF,
// персистентність хайву), але взяти її не можна ніколи. Канон Bohemia --
// PowerGeneratorStatic; House/Land_ як носій стану відкинуто, бо будівлі не
// персистяться.
class OZL_StaticStation : OZL_Station
{
    // Живі статики -- для списків і перевірки «поруч уже стоїть»; для
    // дедупу на буті не годиться, бо сховище сутностей вантажиться після
    // старту місії -- це робить файл стану спавнера.
    static ref array<OZL_StaticStation> s_Statics = new array<OZL_StaticStation>();

    override void EEInit()
    {
        super.EEInit();
        if (GetGame().IsDedicatedServer() && s_Statics.Find(this) < 0)
            s_Statics.Insert(this);
    }

    override void EEDelete(EntityAI parent)
    {
        int idx = s_Statics.Find(this);
        if (idx > -1)
            s_Statics.Remove(idx);
        super.EEDelete(parent);
    }

    override bool IsTakeable()
    {
        return false;
    }

    override bool CanPutIntoHands(EntityAI parent)
    {
        return false;
    }

    override bool CanPutInCargo(EntityAI parent)
    {
        return false;
    }

    override bool CanRemoveFromCargo(EntityAI parent)
    {
        return false;
    }

    // ItemBase з IsTakeable=false ховає віджет прицілу -- повертаємо показ,
    // інакше дій станції не видно. Доступ до карго -- через панель околиці.
    override bool IsActionTargetVisible()
    {
        return true;
    }

    static OZL_StaticStation FindNear(string classname, vector pos, float tolerance)
    {
        for (int i = 0; i < s_Statics.Count(); i++)
        {
            OZL_StaticStation dev = s_Statics[i];
            if (!dev)
                continue;
            if (classname != "" && dev.GetType() != classname)
                continue;
            if (vector.Distance(dev.GetPosition(), pos) <= tolerance)
                return dev;
        }
        return null;
    }
}
