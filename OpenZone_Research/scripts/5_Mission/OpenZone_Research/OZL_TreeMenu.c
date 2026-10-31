// Екран дерева досліджень (меню 135): одне меню на сім вікон фракцій.
//
// Дані -- лише OZL_TreeView: меню не знає конфігів і не рахує статусів, воно
// показує те, що сказав сервер, і просить дослідити вузол. Відмова приходить
// ключем рядка -- її показує сповіщення, як і решту відповідей мода.
//
// ВІКНО ПРИХОДИТЬ ІЗ ВІДПОВІДДЮ. Init() ставить лише хост (ozl_tree_host:
// затемнення і "завантажується"); який скін -- каже сервер (OZL_TreeView.Skin),
// і тоді Take() створює вікно цього скіну в хості (OZL_TreeSkins, одне на скін;
// інший скін -- нове вікно). Вікно, чия розкладка ще не дає віджетів, падає на
// neutral з одним рядком у лозі. Далі меню шукає віджети за РОЛЯМИ -- іменами
// (TreeScroll, CardName, BtnResearch...; повний перелік і що з ними робиться --
// source/ui/SKINS.md) -- і малює те, що знайшло: роль, якої в розкладці нема,
// просто не малюється.
//
// ДЕРЕВО РОЗКЛАДАЄ СКРИПТ (OZL_TreePlan), ЛІНІЇ МАЛЮЄ КАНВА (OZL_TreeLines):
// комірки вузлів кладуться в TreeNodes через SetPos, розмір вмісту прокрутки
// ставить скрипт. ОДИНИЦІ: усе рахується в одиницях вікна 1600x900; скільки
// одиниць SetPos/SetSize на одиницю розкладки (m_K) і скільки пікселів екрана
// на одиницю (m_Px), меню ВИМІРЮЄ саме, двоточковою пробою в перших кадрах
// (скіл суперечив сам собі: "SetPos у пікселях" 2026-09-06 проти "SetPos в
// одиницях" 2026-09-20). Що вийшло -- рядок dbg у лозі й розділ скілу.
//
// ВІДКЛАДЕНЕ. Щойно створений віджет ще не розкладений і міряється нулями,
// тож усе, що залежить від ширини тексту (ціна вузла чіпами, "Відкриває",
// підказка, риски під текстом) і від розміру смуги, робиться наступним кадром
// (черги m_Flows, m_Fits, m_Bars). Лінії -- теж наступним кадром і лише коли
// щось змінилось (вибір, наведення, дані, розкладка), не щокадру.

#ifndef NO_GUI

// Розтягнути віджет на ширину тексту, щойно текст розкладено.
class OZL_TreeFit
{
    TextWidget Text;
    Widget     Target;
    float      Pad;
    int        Mode;    // 0 -- лишити x; 1 -- прив'язаний праворуч; 2 -- по центру батька
    int        Tries;

    void OZL_TreeFit(TextWidget text, Widget target, float pad, int mode)
    {
        Text   = text;
        Target = target;
        Pad    = pad;
        Mode   = mode;
        Tries  = 0;
    }
}

// Заповнити смугу на частку, щойно доріжка має розмір.
class OZL_TreeBarJob
{
    Widget Track;
    Widget Fill;
    float  Frac;
    int    Tries;

    void OZL_TreeBarJob(Widget track, Widget fill, float frac)
    {
        Track = track;
        Fill  = fill;
        Frac  = frac;
        Tries = 0;
    }
}

// Розкласти дітей контейнера рядком (з переносом чи без), щойно їхній текст
// має ширину.
class OZL_TreeFlow
{
    Widget Box;
    float  Gap;
    float  Pad;    // поле праворуч від тексту елемента, одиниці
    bool   Wrap;
    int    Tries;

    void OZL_TreeFlow(Widget box, float gap, float pad, bool wrap)
    {
        Box   = box;
        Gap   = gap;
        Pad   = pad;
        Wrap  = wrap;
        Tries = 0;
    }
}

// Текст, перенесений по словах у рядки-написи контейнера (<Name>0, <Name>1...).
class OZL_TreeWrap
{
    Widget Box;
    string Text;
    int    Color;
    int    Tries;

    void OZL_TreeWrap(Widget box, string text, int color)
    {
        Box   = box;
        Text  = text;
        Color = color;
        Tries = 0;
    }
}

class OZL_TreeMenu : UIScriptedMenu
{
    static const string HOST_LAYOUT = "OpenZone_Research/gui/layouts/ozl_tree_host.layout";
    // Стільки кадрів відкладене чекає, поки віджет розкладеться.
    static const int    LATER_TRIES = 12;

    private static OZL_TreeMenu s_Open;

    private ref OZL_TreeView m_View;
    private ref OZL_TreeSkin m_Skin;
    private string m_SkinAsked = "";   // id, який просив сервер (навіть якщо показано neutral)
    private Widget m_Window;
    private ref map<string, Widget> m_Roles;

    private string m_Branch = "";
    private string m_Node   = "";
    private string m_Hover  = "";

    // Коли приїхала відповідь: залишок проєкту -- від серверної секунди в ній.
    private float m_ViewAge  = 0;
    private float m_Tick     = 0;
    private float m_AskAgain = 0;
    private bool  m_Closing  = false;

    // --- виміряне
    private Widget m_Probe;
    private int    m_ProbeStep  = 0;
    private int    m_ProbeTries = 0;
    private float  m_ProbeX     = 0;
    private float  m_ProbeW     = 0;
    private float  m_K  = 0;   // одиниць SetPos/SetSize на одиницю розкладки
    private float  m_Px = 1;   // пікселів екрана на одиницю розкладки
    // Прокрутка -- у пікселях екрана (виміряно 2026-10-31, скіл gui-layouts
    // §31): позиції HScrollToPos/GetVScrollPos і зсув миші -- одні одиниці.

    // --- дерево
    private ref OZL_TreePlan m_Plan;
    private ref array<Widget> m_Cells;
    private ref array<Widget> m_TierPool;
    private ref array<Widget> m_OrPool;
    private ref array<ref OZL_TreeOrMark> m_Ors;
    private bool m_NeedTree  = false;
    private int  m_TreeWait  = 0;
    private bool m_NeedLines = false;
    private bool m_NeedHome  = false;
    private int  m_HomeWait  = 0;
    private bool m_TipPending = false;
    private int  m_TipTries   = 0;

    // --- рядки списків
    private ref array<Widget> m_BranchRows;
    private ref array<Widget> m_PoolRows;
    private ref array<Widget> m_CostRows;
    private ref array<Widget> m_RegRows;
    private ref array<Widget> m_OpenChips;

    // --- відкладене
    private ref array<ref OZL_TreeFlow>   m_Flows;
    private ref array<ref OZL_TreeFit>    m_Fits;
    private ref array<ref OZL_TreeBarJob> m_Bars;
    private ref array<ref OZL_TreeWrap>   m_Wraps;
    // Що вже розкладено в контейнер рядків: "текст|колір" (повтор не
    // перекладається). Чиститься разом із комірками й вікном.
    private ref map<Widget, string>       m_WrapShown;

    // --- перетягування
    private bool  m_DragDown  = false;
    private bool  m_DragMoved = false;
    private int   m_DragX = 0;
    private int   m_DragY = 0;
    private float m_DragH = 0;
    private float m_DragV = 0;

    void OZL_TreeMenu()
    {
        m_Roles      = new map<string, Widget>();
        m_Plan       = new OZL_TreePlan();
        m_Cells      = new array<Widget>();
        m_TierPool   = new array<Widget>();
        m_OrPool     = new array<Widget>();
        m_Ors        = new array<ref OZL_TreeOrMark>();
        m_BranchRows = new array<Widget>();
        m_PoolRows   = new array<Widget>();
        m_CostRows   = new array<Widget>();
        m_RegRows    = new array<Widget>();
        m_OpenChips  = new array<Widget>();
        m_Flows      = new array<ref OZL_TreeFlow>();
        m_Fits       = new array<ref OZL_TreeFit>();
        m_Bars       = new array<ref OZL_TreeBarJob>();
        m_Wraps      = new array<ref OZL_TreeWrap>();
        m_WrapShown  = new map<Widget, string>();
    }

    static OZL_TreeMenu Open()
    {
        return s_Open;
    }

    // Відповідь служби -- сюди з OZL_MissionGameplay, для відкритого меню.
    static void OnService(string serviceId, string op, bool ok, string json, string error)
    {
        if (serviceId != OZL_Const.SERVICE)
            return;
        if (!ok)
        {
            OZ_Notice.Take("research." + op, false, error);
            if (s_Open)
                s_Open.Say(OZL_Text.Words(error));
            return;
        }
        if (!s_Open)
            return;
        s_Open.Take(json);
        if (op == OZL_Const.OP_RESEARCH)
            OZ_Notice.Take("research." + op, true, "STR_OZL_TREE_STARTED");
    }

    static string Words(string key)
    {
        return OZL_Text.Words(key);
    }

    // ------------------------------------------------------------------
    // Життя меню
    // ------------------------------------------------------------------

    override Widget Init()
    {
        layoutRoot = GetGame().GetWorkspace().CreateWidgets(HOST_LAYOUT);
        if (!layoutRoot)
        {
            OZL_Log.Error("tree menu: the host layout produced no widgets");
            return null;
        }
        m_Probe = layoutRoot.FindAnyWidget("TreeProbe");
        return layoutRoot;
    }

    override bool UseMouse()
    {
        return true;
    }

    override bool UseKeyboard()
    {
        return true;
    }

    override void OnShow()
    {
        super.OnShow();
        if (!layoutRoot)
        {
            OZL_Log.Error("tree menu: no layout, closing");
            GetGame().GetUIManager().CloseMenu(OZL_Const.MENU_TREE);
            return;
        }
        s_Open = this;
        SetFocus(layoutRoot);
        LockControls();
        array<string> excludes = new array<string>();
        excludes.Insert("menu");
        // HUD ховається, поки екран відкритий (як мокап: лише вікно); кожен
        // крок -- через локальну, без ланцюжка GetMission().GetHud() (скіл §18).
        Mission mission = GetGame().GetMission();
        if (mission)
        {
            mission.AddActiveInputExcludes(excludes);
            Hud hud = mission.GetHud();
            if (hud)
                hud.Show(false);
        }

        m_ProbeStep  = 1;
        m_ProbeTries = 0;
        Widget loading = layoutRoot.FindAnyWidget("TreeLoading");
        if (loading)
            loading.Show(true);
        OZ_Rpc.ServiceRequest(OZL_Const.SERVICE, OZL_Const.OP_TREE, "{}");
    }

    override void OnHide()
    {
        super.OnHide();
        array<string> excludes = new array<string>();
        excludes.Insert("menu");
        Mission mission = GetGame().GetMission();
        if (mission)
        {
            mission.RemoveActiveInputExcludes(excludes, true);
            Hud hud = mission.GetHud();
            if (hud)
                hud.Show(true);
        }
        UnlockControls();
        if (s_Open == this)
            s_Open = null;
    }

    override bool OnKeyPress(Widget w, int x, int y, int key)
    {
        if (key == KeyCode.KC_ESCAPE)
        {
            CloseTree();
            return true;
        }
        return super.OnKeyPress(w, x, y, key);
    }

    void CloseTree()
    {
        if (m_Closing)
            return;
        m_Closing = true;
        Close();
    }

    override void Update(float timeslice)
    {
        super.Update(timeslice);
        if (!layoutRoot || m_Closing)
            return;
        if (GetUApi().GetInputByID(UAUIBack).LocalPress())
        {
            CloseTree();
            return;
        }
        m_ViewAge += timeslice;
        if (m_AskAgain > 0)
            m_AskAgain -= timeslice;

        Probe();
        if (m_NeedTree && m_K > 0 && m_View && m_Skin)
            PaintTree();
        RunWraps();
        RunBars();
        RunFits();
        RunFlows();
        RunTip();
        if (m_NeedLines)
        {
            m_NeedLines = false;
            DrawLines();
        }
        if (m_NeedHome)
            Home();
        Drag();

        m_Tick += timeslice;
        if (m_Tick >= 1.0)
        {
            m_Tick = 0;
            PaintProgress();
        }
        if (m_Skin && m_Window)
            m_Skin.OnUpdate(this, timeslice);
    }

    // ------------------------------------------------------------------
    // Для скінів: ролі, одиниці, дані
    // ------------------------------------------------------------------

    // Віджет ролі у вікні скіну (null -- такої ролі нема). Шукається раз.
    Widget Role(string name)
    {
        Widget w;
        if (m_Roles.Find(name, w))
            return w;
        w = null;
        if (m_Window)
            w = m_Window.FindAnyWidget(name);
        m_Roles.Set(name, w);
        return w;
    }

    OZL_TreeSkin Skin()
    {
        return m_Skin;
    }

    OZL_TreeView View()
    {
        return m_View;
    }

    string SelectedId()
    {
        return m_Node;
    }

    string HoveredId()
    {
        return m_Hover;
    }

    float Px()
    {
        return m_Px;
    }

    // Поставити / розтягнути віджет в одиницях розкладки (множник виміряно;
    // до кінця проби -- пікселі на одиницю, бо Set* беруть пікселі).
    void PlaceUnits(Widget w, float x, float y)
    {
        if (!w)
            return;
        float k = m_K;
        if (k <= 0)
            k = m_Px;
        w.SetPos(x * k, y * k);
    }

    void SizeUnits(Widget w, float width, float height)
    {
        if (!w)
            return;
        float k = m_K;
        if (k <= 0)
            k = m_Px;
        if (width < 0)
            width = 0;
        if (height < 0)
            height = 0;
        w.SetSize(width * k, height * k);
    }

    // Розмір віджета на екрані, одиниці.
    void UnitsOf(Widget w, out float width, out float height)
    {
        width = 0;
        height = 0;
        if (!w)
            return;
        float pw;
        float ph;
        w.GetScreenSize(pw, ph);
        width = pw / m_Px;
        height = ph / m_Px;
    }

    // Наступним кадром: ширина `target` = ширина тексту `text` + pad
    // (режими -- див. OZL_TreeFit).
    void FitLater(TextWidget text, Widget target, float pad, int mode)
    {
        if (!text || !target)
            return;
        m_Fits.Insert(new OZL_TreeFit(text, target, pad, mode));
    }

    void BarLater(Widget track, Widget fill, float frac)
    {
        if (!track || !fill)
            return;
        if (frac < 0)
            frac = 0;
        if (frac > 1)
            frac = 1;
        m_Bars.Insert(new OZL_TreeBarJob(track, fill, frac));
    }

    void FlowLater(Widget box, float gap, float pad, bool wrap)
    {
        if (!box)
            return;
        m_Flows.Insert(new OZL_TreeFlow(box, gap, pad, wrap));
    }

    // Текст у роль. TextWidget отримує його цілим (MultilineTextWidget сам
    // переносить -- але лише зі шрифтами, що чують "exact text size": SDF і
    // ванільні; з бітмаповими шрифтами мода він малює клітинкою атласу,
    // виміряно 2026-10-31). Контейнер отримує його, перенесеним по словах, у
    // свої написи <Name>0, <Name>1... (наступним кадром, коли написи мають
    // ширину); зайві ховаються, останній бере решту. color 0 -- не фарбувати.
    void PutText(Widget w, string text, int color)
    {
        if (!w)
            return;
        TextWidget t = TextWidget.Cast(w);
        if (t)
        {
            t.SetText(text);
            if (color != 0)
                t.SetColor(color);
            return;
        }
        bool pending = false;
        for (int i = m_Wraps.Count() - 1; i >= 0; i--)
        {
            if (m_Wraps[i].Box == w)
            {
                m_Wraps.RemoveOrdered(i);
                pending = true;
            }
        }
        // Той самий текст тим самим кольором уже розкладено -- не перекладати
        // (вибір вузла перемальовує його комірку, а назва в ній та сама).
        string sig = text + "|" + color.ToString();
        string was;
        if (!pending && m_WrapShown.Find(w, was) && was == sig)
            return;
        m_WrapShown.Remove(w);
        m_Wraps.Insert(new OZL_TreeWrap(w, text, color));
    }

    // Id з імені "<tag><id>" на віджеті або будь-якому його предку: клік по
    // дитині рядка-кнопки теж знаходить свій рядок (як NodeIdAt для вузлів).
    string TaggedAt(Widget w, string tag)
    {
        int n = tag.Length();
        Widget cur = w;
        while (cur)
        {
            string nm = cur.GetName();
            if (nm.IndexOf(tag) == 0)
                return nm.Substring(n, nm.Length() - n);
            cur = cur.GetParent();
        }
        return "";
    }

    int BranchCount()
    {
        if (!m_View)
            return 0;
        return m_View.Branches.Count();
    }

    OZL_BranchView CurrentBranch()
    {
        return BranchOf(m_Branch);
    }

    OZL_BranchView BranchOf(string id)
    {
        if (!m_View)
            return null;
        for (int i = 0; i < m_View.Branches.Count(); i++)
        {
            if (m_View.Branches[i] && m_View.Branches[i].Id == id)
                return m_View.Branches[i];
        }
        return null;
    }

    OZL_NodeView NodeOf(string id)
    {
        OZL_BranchView b = CurrentBranch();
        if (!b || id == "")
            return null;
        for (int i = 0; i < b.Nodes.Count(); i++)
        {
            if (b.Nodes[i] && b.Nodes[i].Id == id)
                return b.Nodes[i];
        }
        return null;
    }

    // Вузол у будь-якій гілці відповіді (батько з іншої гілки).
    OZL_NodeView AnyNodeOf(string id)
    {
        if (!m_View || id == "")
            return null;
        for (int b = 0; b < m_View.Branches.Count(); b++)
        {
            OZL_BranchView br = m_View.Branches[b];
            if (!br)
                continue;
            for (int i = 0; i < br.Nodes.Count(); i++)
            {
                if (br.Nodes[i] && br.Nodes[i].Id == id)
                    return br.Nodes[i];
            }
        }
        return null;
    }

    // Назва лінії ("Хабар").
    string PointName(string line)
    {
        if (m_View)
        {
            for (int i = 0; i < m_View.Names.Count(); i++)
            {
                OZL_PointName n = m_View.Names[i];
                if (n && n.Id == line)
                {
                    if (n.Name != "")
                        return n.Name;
                    return n.Id;
                }
            }
        }
        return line;
    }

    // Колір лінії з конфігу типів балів; нема -- тьмяний скіну.
    int PointColor(string line)
    {
        if (m_View)
        {
            for (int i = 0; i < m_View.Names.Count(); i++)
            {
                OZL_PointName n = m_View.Names[i];
                if (n && n.Id == line && n.Color != 0)
                    return n.Color;
            }
        }
        if (m_Skin)
            return m_Skin.Dim;
        return ARGB(255, 128, 128, 128);
    }

    int PoolOf(string line)
    {
        if (!m_View)
            return 0;
        for (int i = 0; i < m_View.Pool.Count(); i++)
        {
            if (m_View.Pool[i] && m_View.Pool[i].Key == line)
                return m_View.Pool[i].Value;
        }
        return 0;
    }

    // Назва предмета мовою ГРАВЦЯ. Сервер кладе свою здогадку в Name, але
    // ConfigGetTextOut на сервері розв'язує $STR_ мовою СЕРВЕРА (виміряно на
    // стенді 2026-09-20: англійський сервер відповідає "Paper" там, де
    // гравець має бачити "Папір"), тож клієнт питає свій конфіг сам.
    string ItemLabel(OZL_ItemView iv)
    {
        if (!iv)
            return "";
        string name = "";
        if (iv.Cls != "")
        {
            name = GetGame().ConfigGetTextOut("CfgVehicles " + iv.Cls + " displayName");
            if (name == "")
                name = GetGame().ConfigGetTextOut("CfgMagazines " + iv.Cls + " displayName");
            if (name == "")
                name = GetGame().ConfigGetTextOut("cfgWeapons " + iv.Cls + " displayName");
            if (name == "")
                name = GetGame().ConfigGetTextOut("CfgAmmo " + iv.Cls + " displayName");
        }
        if (name == "" || name.IndexOf("$") == 0 || name.IndexOf("STR_") == 0)
            name = iv.Name;
        if (name == "")
            name = iv.Cls;
        return name;
    }

    // Скільки секунд лишилось проєкту -- від серверного часу відповіді.
    int LeftOf(OZL_NodeView n)
    {
        if (!m_View || !n)
            return 0;
        int age = m_ViewAge;
        int left = n.EndSec - m_View.Now - age;
        if (left < 0)
            left = 0;
        return left;
    }

    // ------------------------------------------------------------------
    // Дані
    // ------------------------------------------------------------------

    void Take(string json)
    {
        OZL_TreeView v = new OZL_TreeView();
        string err;
        if (!JsonFileLoader<OZL_TreeView>.LoadData(json, v, err))
        {
            OZL_Log.Warn("tree menu: unreadable tree (" + err + ")");
            Say(Words("STR_OZL_ERR_STATE"));
            return;
        }
        m_View = v;
        m_ViewAge = 0;

        string want = v.Skin;
        if (want == "")
            want = OZL_TreeSkins.FALLBACK;
        if (!m_Window || want != m_SkinAsked)
        {
            if (!BuildWindow(want))
                return;
        }

        if (m_Branch == "" || !BranchOf(m_Branch))
        {
            m_Branch = "";
            if (v.Branches.Count() > 0 && v.Branches[0])
                m_Branch = v.Branches[0].Id;
            m_Node = "";
            m_NeedHome = true;
        }
        if (m_Node != "" && !NodeOf(m_Node))
            m_Node = "";
        if (m_Node == "")
            m_Node = DefaultNode();
        PaintAll();
    }

    // Вибір за замовчуванням, як pickOwner() мокапа: проєкт, що йде, інакше
    // доступний, інакше перший.
    private string DefaultNode()
    {
        OZL_BranchView b = CurrentBranch();
        if (!b)
            return "";
        int i;
        for (i = 0; i < b.Nodes.Count(); i++)
        {
            if (b.Nodes[i] && b.Nodes[i].Status == "researching")
                return b.Nodes[i].Id;
        }
        for (i = 0; i < b.Nodes.Count(); i++)
        {
            if (b.Nodes[i] && b.Nodes[i].Status == "available")
                return b.Nodes[i].Id;
        }
        if (b.Nodes.Count() > 0 && b.Nodes[0])
            return b.Nodes[0].Id;
        return "";
    }

    // Вікно скіну в хості. Скін, чия розкладка ще не дає віджетів (його
    // задача не зроблена), -- тетрадь neutral з одним рядком у лозі.
    private bool BuildWindow(string id)
    {
        if (m_Window)
        {
            m_Window.Unlink();
            m_Window = null;
        }
        m_Roles.Clear();
        m_Cells.Clear();
        m_TierPool.Clear();
        m_OrPool.Clear();
        m_BranchRows.Clear();
        m_PoolRows.Clear();
        m_CostRows.Clear();
        m_RegRows.Clear();
        m_OpenChips.Clear();
        m_Flows.Clear();
        m_Fits.Clear();
        m_Bars.Clear();
        m_Wraps.Clear();
        m_WrapShown.Clear();
        m_Hover = "";
        m_TipPending = false;

        OZL_TreeSkin skin = OZL_TreeSkins.Make(id);
        Widget win = null;
        // Розкладки, якої ще немає, не чіпаємо: CreateWidgets на відсутній
        // файл пише два рядки SCRIPT (E) "Cannot load layout" на кожне
        // відкриття. FileExist бачить і файли в pbo -- виведено, не виміряно
        // напряму (ванільний ParticleList так перевіряє .ptc і мовчить), тож
        // запасне вікно від нього не залежить: його розкладку пробуємо завжди.
        bool tryOwn = skin.WindowLayout != "";
        if (tryOwn && skin.Id != OZL_TreeSkins.FALLBACK && !FileExist(skin.WindowLayout))
            tryOwn = false;
        if (tryOwn)
            win = GetGame().GetWorkspace().CreateWidgets(skin.WindowLayout, layoutRoot);
        if (!win && skin.Id != OZL_TreeSkins.FALLBACK)
        {
            OZL_Log.Info("tree: window '" + skin.Id + "' has no layout yet (" + skin.WindowLayout + "), showing " + OZL_TreeSkins.FALLBACK);
            skin = OZL_TreeSkins.Make(OZL_TreeSkins.FALLBACK);
            win = GetGame().GetWorkspace().CreateWidgets(skin.WindowLayout, layoutRoot);
        }
        if (!win)
        {
            OZL_Log.Error("tree: the window layout " + skin.WindowLayout + " produced no widgets");
            return false;
        }
        m_Skin = skin;
        m_Window = win;
        m_SkinAsked = id;
        m_NeedHome = true;

        Widget loading = layoutRoot.FindAnyWidget("TreeLoading");
        if (loading)
            loading.Show(false);
        Widget tip = Role("TreeTip");
        if (tip)
        {
            tip.Show(false);
            IgnorePointer(tip, null);
        }
        OZL_Log.Dbg("tree: window " + m_Skin.Id + " for '" + id + "'");
        m_Skin.OnShow(this);
        return true;
    }

    // ------------------------------------------------------------------
    // Малювання
    // ------------------------------------------------------------------

    void PaintAll()
    {
        if (!m_View || !m_Skin)
            return;
        PaintHeader();
        PaintBranches();
        PaintPool();
        PaintTree();
        PaintRegistry();
        PaintCard();
        m_Skin.OnPaint(this);
    }

    private void SetText(string role, string text)
    {
        TextWidget t = TextWidget.Cast(Role(role));
        if (t)
            t.SetText(text);
    }

    private void PaintHeader()
    {
        OZL_BranchView b = CurrentBranch();
        string name = "";
        string sub = m_View.OwnerName;
        if (b)
        {
            name = b.Name;
            int done = DoneOf(b);
            sub += " · " + Words("STR_OZL_TREE_RESEARCHED") + " " + done.ToString() + " " + Words("STR_OZL_TREE_OF") + " " + TotalOf(b).ToString();
        }
        SetText("BranchName", name);
        SetText("BranchSub", sub);
    }

    private int DoneOf(OZL_BranchView b)
    {
        int done = 0;
        for (int i = 0; i < b.Nodes.Count(); i++)
        {
            if (b.Nodes[i] && b.Nodes[i].Status == "completed")
                done++;
        }
        return done;
    }

    private int TotalOf(OZL_BranchView b)
    {
        int total = b.Total;
        int seen = b.Nodes.Count() + b.Hidden.Count();
        if (total < seen)
            total = seen;
        return total;
    }

    private void Unlink(array<Widget> list)
    {
        for (int i = 0; i < list.Count(); i++)
        {
            if (list[i])
                list[i].Unlink();
        }
        list.Clear();
    }

    private Widget Row(string row, Widget parent)
    {
        if (!parent || !m_Skin)
            return null;
        return GetGame().GetWorkspace().CreateWidgets(m_Skin.RowLayout(row), parent);
    }

    private void PaintBranches()
    {
        Unlink(m_BranchRows);
        Widget list = Role("BranchList");
        if (!list)
            return;
        for (int i = 0; i < m_View.Branches.Count(); i++)
        {
            OZL_BranchView b = m_View.Branches[i];
            if (!b)
                continue;
            Widget row = Row("branch_row", list);
            if (!row)
                break;
            // Клацається RowHit (кнопка зі style Empty), або сам рядок -- тоді
            // він сам має бути такою кнопкою (рамка кліку не отримує). Решта
            // рядка мишу пропускає (правило миші, як у вузлі).
            Widget rowHit = row.FindAnyWidget("RowHit");
            if (!rowHit)
                rowHit = row;
            rowHit.SetName("branch:" + b.Id);
            IgnorePointer(row, rowHit);
            TextWidget name = TextWidget.Cast(row.FindAnyWidget("RowName"));
            if (name)
                name.SetText(b.Name);
            int done = DoneOf(b);
            int total = TotalOf(b);
            TextWidget count = TextWidget.Cast(row.FindAnyWidget("RowCount"));
            if (count)
                count.SetText(done.ToString() + " / " + total.ToString());
            bool picked = b.Id == m_Branch;
            Widget pick = row.FindAnyWidget("RowPick");
            if (pick)
                pick.Show(picked);
            float frac = 0;
            if (total > 0)
            {
                frac = done;
                frac = frac / total;
            }
            BarLater(row.FindAnyWidget("RowBar"), row.FindAnyWidget("RowBarFill"), frac);
            m_BranchRows.Insert(row);
        }
        list.Update();
    }

    // Пул: кожна лінія, яку витрачають видимі вузли гілок фракції або яка
    // є в пулі (renderPool() мокапа). need -- найбільша ціна одного вузла по
    // лінії, для сегментів.
    private void PaintPool()
    {
        Unlink(m_PoolRows);
        Widget list = Role("PoolList");
        if (!list)
            return;
        map<string, int> need = new map<string, int>();
        int b;
        int i;
        for (b = 0; b < m_View.Branches.Count(); b++)
        {
            OZL_BranchView br = m_View.Branches[b];
            if (!br)
                continue;
            for (i = 0; i < br.Nodes.Count(); i++)
            {
                OZL_NodeView n = br.Nodes[i];
                if (!n)
                    continue;
                for (int c = 0; c < n.Cost.Count(); c++)
                {
                    OZL_KV kv = n.Cost[c];
                    if (!kv)
                        continue;
                    int had = 0;
                    need.Find(kv.Key, had);
                    if (kv.Value > had)
                        need.Set(kv.Key, kv.Value);
                }
            }
        }
        int shown = 0;
        for (i = 0; i < m_View.Names.Count(); i++)
        {
            OZL_PointName pn = m_View.Names[i];
            if (!pn)
                continue;
            int have = PoolOf(pn.Id);
            int most = 0;
            bool spent = need.Find(pn.Id, most);
            if (have <= 0 && !spent)
                continue;
            Widget row = Row("pool_row", list);
            if (!row)
                break;
            m_Skin.PaintPoolRow(this, row, pn.Id, have, most, PointColor(pn.Id));
            m_PoolRows.Insert(row);
            shown++;
        }
        Widget empty = Role("PoolEmpty");
        if (empty)
            empty.Show(shown == 0);
        list.Update();
    }

    // ---------- дерево ----------

    private void PaintTree()
    {
        if (m_K <= 0)
        {
            m_NeedTree = true;
            return;
        }
        Widget scroll = Role("TreeScroll");
        Widget content = Role("TreeContent");
        Widget nodes = Role("TreeNodes");
        float viewW = 0;
        float viewH = 0;
        UnitsOf(scroll, viewW, viewH);
        if (scroll && viewW <= 0 && m_TreeWait < LATER_TRIES)
        {
            // Вікно щойно створене і ще не розкладене -- наступним кадром.
            m_TreeWait++;
            m_NeedTree = true;
            return;
        }
        m_NeedTree = false;
        m_TreeWait = 0;
        // Мокап віднімає 12 під смуги прокрутки.
        viewW -= 12;
        viewH -= 12;

        // Комірки йдуть -- з ними й пам'ять про розкладені в них назви.
        m_WrapShown.Clear();
        Unlink(m_Cells);
        HidePool(m_TierPool);
        HidePool(m_OrPool);
        SetHover("");

        OZL_BranchView b = CurrentBranch();
        m_Plan.Build(m_Skin, b, viewW, viewH);
        if (content)
            SizeUnits(content, m_Plan.W, m_Plan.H);
        if (scroll)
            scroll.Update();

        // Підписи тирів: римські цифри біля краю, де починається рядок.
        Widget tiers = Role("TreeTiers");
        int i;
        for (i = 0; i < m_Plan.Tiers.Count() && tiers; i++)
        {
            Widget lab = Pooled(m_TierPool, "tier_label", tiers, i);
            if (!lab)
                break;
            TextWidget lt = TextWidget.Cast(lab.FindAnyWidget("TierText"));
            if (lt)
                lt.SetText(m_Skin.TierText(m_Plan.Tiers[i]));
            float tx;
            float ty;
            m_Plan.XY(m_Skin.Top + m_Skin.Row * (i + 0.5), 22, tx, ty);
            PlaceUnits(lab, tx, ty);
            lab.Show(true);
        }

        // Комірки вузлів.
        for (i = 0; i < m_Plan.Ids.Count() && nodes && b; i++)
        {
            OZL_NodeView n = NodeOf(m_Plan.Ids[i]);
            Widget cell = GetGame().GetWorkspace().CreateWidgets(m_Skin.NodeLayout, nodes);
            if (!cell)
            {
                OZL_Log.Error("tree: the node layout " + m_Skin.NodeLayout + " produced no widgets");
                break;
            }
            m_Cells.Insert(cell);
            PlaceUnits(cell, m_Plan.X[i] - m_Skin.AnchorX, m_Plan.Y[i] - m_Skin.AnchorY);
            LoadSlots(cell);
            Widget hit = cell.FindAnyWidget("NodeHit");
            if (hit)
                hit.SetName("node:" + n.Id);
            cell.SetName("cell:" + n.Id);
            PaintCell(cell, n);
            // Миша -- лише NodeHit (і контейнери, що його тримають, під ним); мітки
            // й підписи можуть виступати за комірку.
            IgnorePointer(cell, hit);
            Unclip(cell, hit);
        }
        PaintFog();
        m_NeedLines = true;
        OZL_Log.Dbg("tree: " + m_Plan.Ids.Count().ToString() + " node(s), " + m_Plan.Tiers.Count().ToString() + " tier(s), content " + m_Plan.W.ToString() + " x " + m_Plan.H.ToString() + " units, view " + viewW.ToString() + " x " + viewH.ToString());
    }

    private Widget Pooled(array<Widget> pool, string row, Widget parent, int index)
    {
        if (index < pool.Count())
            return pool[index];
        Widget w = Row(row, parent);
        if (w)
        {
            pool.Insert(w);
            IgnorePointer(w, null);
            w.ClearFlags(WidgetFlags.CLIPCHILDREN);
        }
        return w;
    }

    // ПРАВИЛО МИШІ (стенд 2026-10-31: наведення працювало лише біля краю
    // вузла). FrameWidget без ignorepointer бере мишу на себе, тож рамка з
    // назвою посеред картки ковтала наведення й клік, і до NodeHit під нею
    // доходив лише обідок. Тут усе в `root`, крім `keep` і контейнерів, що
    // його тримають (вони під ним і бачать лише поля), мишу пропускає.
    static void IgnorePointer(Widget root, Widget keep)
    {
        if (!root)
            return;
        if (root != keep && !Holds(root, keep))
            root.SetFlags(WidgetFlags.IGNOREPOINTER);
        Widget c = root.GetChildren();
        while (c)
        {
            IgnorePointer(c, keep);
            c = c.GetSibling();
        }
    }

    // Чи `outer` -- предок `inner`.
    static bool Holds(Widget outer, Widget inner)
    {
        if (!outer || !inner)
            return false;
        Widget p = inner.GetParent();
        while (p)
        {
            if (p == outer)
                return true;
            p = p.GetParent();
        }
        return false;
    }

    // Рамка ріже дітей по своєму краю, якщо не сказано clipchildren 0
    // (виміряно 2026-10-31): комірка й контейнери NodeHit пускають мітки й
    // написи за край.
    private static void Unclip(Widget cell, Widget hit)
    {
        cell.ClearFlags(WidgetFlags.CLIPCHILDREN);
        if (!hit)
            return;
        Widget p = hit.GetParent();
        while (p && p != cell)
        {
            p.ClearFlags(WidgetFlags.CLIPCHILDREN);
            p = p.GetParent();
        }
    }

    // Вузол, якому належить віджет: NodeHit (node:<id>) або будь-що в
    // комірці (cell:<id>) -- окрім самих контейнерів NodeHit: вони бачать
    // лише поля комірки, а це ще не вузол.
    string NodeIdAt(Widget w)
    {
        Widget cur = w;
        while (cur)
        {
            string nm = cur.GetName();
            if (nm.IndexOf("node:") == 0)
                return nm.Substring(5, nm.Length() - 5);
            if (nm.IndexOf("cell:") == 0)
            {
                string id = nm.Substring(5, nm.Length() - 5);
                if (w.FindAnyWidget("node:" + id))
                    return "";
                return id;
            }
            cur = cur.GetParent();
        }
        return "";
    }

    private void HidePool(array<Widget> pool)
    {
        for (int i = 0; i < pool.Count(); i++)
        {
            if (pool[i])
                pool[i].Show(false);
        }
    }

    // Картинки станів у слоти: форма (Shapes) і мітка (Marks), раз на комірку.
    private void LoadSlots(Widget cell)
    {
        int i;
        ImageWidget shape = ImageWidget.Cast(cell.FindAnyWidget("NodeShape"));
        if (shape)
        {
            for (i = 0; i < m_Skin.Shapes.Count() && i < 8; i++)
                shape.LoadImageFile(i, m_Skin.Shapes[i]);
        }
        ImageWidget mark = ImageWidget.Cast(cell.FindAnyWidget("NodeMark"));
        if (mark)
        {
            for (i = 0; i < m_Skin.Marks.Count() && i < 8; i++)
                mark.LoadImageFile(i, m_Skin.Marks[i]);
        }
    }

    private Widget CellOf(string id)
    {
        int at = m_Plan.IndexOf(id);
        if (at < 0 || at >= m_Cells.Count())
            return null;
        return m_Cells[at];
    }

    private void PaintCell(Widget cell, OZL_NodeView n)
    {
        if (!cell || !n)
            return;
        bool picked = n.Id == m_Node;
        m_Skin.PaintNode(this, cell, n, n.Status, picked);
        PaintPrice(cell, n);
        PaintNodeBar(cell, n);
    }

    // Ціна в комірці (priceLine() мокапа): чіпи лінії з числами і хвіст
    // "+N предм."; досліджений -- "Досліджено", у ділі -- "Лишилось m:ss".
    private void PaintPrice(Widget cell, OZL_NodeView n)
    {
        Widget box = cell.FindAnyWidget("NodePrice");
        TextWidget plain = TextWidget.Cast(cell.FindAnyWidget("NodePriceText"));
        int color = m_Skin.PriceColorOf(n.Status);
        if (box)
        {
            Widget child = box.GetChildren();
            while (child)
            {
                Widget next = child.GetSibling();
                child.Unlink();
                child = next;
            }
        }
        string word = "";
        if (n.Status == "completed")
            word = Words("STR_OZL_TREE_COMPLETED");
        else if (n.Status == "researching")
            word = Words("STR_OZL_TREE_LEFT") + " " + OZL_Text.Clock(LeftOf(n));
        int qty = 0;
        int i;
        for (i = 0; i < n.Items.Count(); i++)
        {
            if (n.Items[i])
                qty += n.Items[i].Qty;
        }
        string tail = "";
        if (qty > 0)
            tail = "+" + qty.ToString() + " " + Words("STR_OZL_TREE_ITEMS_TAIL");

        // Без контейнера чіпів чи без шаблону -- ціна простим текстом.
        bool chips = box && word == "";
        if (chips)
        {
            for (i = 0; i < n.Cost.Count(); i++)
            {
                OZL_KV kv = n.Cost[i];
                if (!kv)
                    continue;
                Widget chip = Row("price_chip", box);
                if (!chip)
                {
                    chips = false;
                    break;
                }
                IgnorePointer(chip, null);
                Widget dot = chip.FindAnyWidget("PriceChip");
                if (dot)
                    dot.SetColor(PointColor(kv.Key));
                TextWidget amount = TextWidget.Cast(chip.FindAnyWidget("PriceText"));
                if (amount)
                {
                    amount.SetText(kv.Value.ToString());
                    amount.SetColor(color);
                }
            }
            if (chips && tail != "")
            {
                Widget more = Row("price_chip", box);
                if (more)
                {
                    IgnorePointer(more, null);
                    Widget moreDot = more.FindAnyWidget("PriceChip");
                    if (moreDot)
                        moreDot.Show(false);
                    TextWidget moreText = TextWidget.Cast(more.FindAnyWidget("PriceText"));
                    if (moreText)
                    {
                        moreText.SetText(tail);
                        moreText.SetColor(color);
                    }
                }
            }
        }
        if (chips)
        {
            if (box)
                box.Show(true);
            if (plain)
                plain.Show(false);
            FlowLater(box, 6, 0, false);
            return;
        }
        if (box)
            box.Show(false);
        if (!plain)
            return;
        if (word == "")
        {
            for (i = 0; i < n.Cost.Count(); i++)
            {
                if (n.Cost[i])
                    word += n.Cost[i].Value.ToString() + " ";
            }
            word += tail;
        }
        plain.SetText(word);
        plain.SetColor(color);
        plain.Show(true);
    }

    private void PaintNodeBar(Widget cell, OZL_NodeView n)
    {
        Widget bar = cell.FindAnyWidget("NodeBar");
        if (!bar)
            return;
        bool going = n.Status == "researching";
        bar.Show(going);
        if (going)
            BarLater(bar, cell.FindAnyWidget("NodeBarFill"), ProgressOf(n));
    }

    // Частка зробленого. Тривалість 0 у проєкту, що йде (демо стенда ставить
    // 600 с вузлові без тривалості), -- поступ невідомий: 0.
    private float ProgressOf(OZL_NodeView n)
    {
        if (n.Duration <= 0)
            return 0;
        float left = LeftOf(n);
        return 1.0 - left / n.Duration;
    }

    // Туман за останнім видимим тиром: смуга-перехід TreeFogEdge (якщо є)
    // і суцільне TreeFog далі, обидва -- кольору FogColor скіну. Напрямок --
    // від скіну; картинку переходу меню не повертає: вона намальована вже в
    // напрямку дерева (SKINS.md).
    private void PaintFog()
    {
        Widget fog = Role("TreeFog");
        Widget edge = Role("TreeFogEdge");
        if (!m_Plan.HasFog)
        {
            if (fog)
                fog.Show(false);
            if (edge)
                edge.Show(false);
            return;
        }
        if (fog)
            fog.SetColor(m_Skin.FogColor);
        if (edge)
            edge.SetColor(m_Skin.FogColor);
        float depth = 80;
        if (!edge)
            depth = 0;
        float along = m_Plan.H;
        if (m_Plan.Horiz)
            along = m_Plan.W;
        float start = m_Plan.FogU;
        if (start > along)
            start = along;
        float edgeLen = depth;
        if (start + edgeLen > along)
            edgeLen = along - start;
        float rest = along - start - edgeLen;
        if (m_Plan.Dir == "right")
        {
            FogPart(edge, start, 0, edgeLen, m_Plan.H);
            FogPart(fog, start + edgeLen, 0, rest, m_Plan.H);
        }
        else if (m_Plan.Dir == "up")
        {
            FogPart(edge, 0, along - start - edgeLen, m_Plan.W, edgeLen);
            FogPart(fog, 0, 0, m_Plan.W, rest);
        }
        else
        {
            FogPart(edge, 0, start, m_Plan.W, edgeLen);
            FogPart(fog, 0, start + edgeLen, m_Plan.W, rest);
        }
    }

    private void FogPart(Widget w, float x, float y, float width, float height)
    {
        if (!w)
            return;
        if (width <= 0 || height <= 0)
        {
            w.Show(false);
            return;
        }
        PlaceUnits(w, x, y);
        SizeUnits(w, width, height);
        w.Show(true);
    }

    private void DrawLines()
    {
        CanvasWidget canvas = CanvasWidget.Cast(Role("TreeLines"));
        if (!canvas || !m_Skin)
            return;
        m_Skin.PxPerUnit = m_Px;
        string focus = m_Hover;
        if (focus == "")
            focus = m_Node;
        OZL_TreeLines.Draw(canvas, m_Skin, m_Plan, CurrentBranch(), focus, m_Ors);
        HidePool(m_OrPool);
        Widget nodes = Role("TreeNodes");
        for (int i = 0; i < m_Ors.Count() && nodes; i++)
        {
            Widget lab = Pooled(m_OrPool, "or_label", nodes, i);
            if (!lab)
                break;
            TextWidget t = TextWidget.Cast(lab.FindAnyWidget("OrText"));
            if (t)
            {
                t.SetText(Words("STR_OZL_TREE_OR"));
                t.SetColor(m_Ors[i].Color);
            }
            PlaceUnits(lab, m_Ors[i].X, m_Ors[i].Y);
            lab.Show(true);
        }
    }

    // ---------- реєстр (Долг): усі вузли гілки за тирами, приховані -- "невідомо" ----------

    // Тир за тиром, а в тирі -- за Index (порядок конфігу), заглушки туману
    // на своїх місцях: № іде підряд, як у конфігу, а не "видимі, потім
    // приховані".
    private void PaintRegistry()
    {
        Unlink(m_RegRows);
        Widget list = Role("Registry");
        OZL_BranchView b = CurrentBranch();
        if (!list || !b)
            return;
        int top = MaxIndex(b);
        if (top < 0)
        {
            list.Update();
            return;
        }
        array<OZL_NodeView> nodeAt = new array<OZL_NodeView>();
        array<OZL_HiddenView> stubAt = new array<OZL_HiddenView>();
        nodeAt.Resize(top + 1);
        stubAt.Resize(top + 1);
        int i;
        for (i = 0; i < b.Nodes.Count(); i++)
        {
            OZL_NodeView n = b.Nodes[i];
            if (n && n.Index >= 0 && n.Index <= top)
                nodeAt[n.Index] = n;
        }
        for (i = 0; i < b.Hidden.Count(); i++)
        {
            OZL_HiddenView h = b.Hidden[i];
            if (h && h.Index >= 0 && h.Index <= top)
                stubAt[h.Index] = h;
        }
        for (int tier = 1; tier <= OZL_TreePlan.MAX_TIER; tier++)
        {
            for (int index = 0; index <= top; index++)
            {
                OZL_NodeView vn = nodeAt[index];
                if (vn)
                {
                    if (OZL_TreePlan.TierOf(vn) == tier)
                        RegRow(list, vn.Id, vn.Index, tier, m_Skin.NodeNameText(vn.Name), m_Skin.StatusText(vn.Status), vn.Status);
                    continue;
                }
                OZL_HiddenView vh = stubAt[index];
                if (vh && StubTier(vh) == tier)
                    RegRow(list, "", vh.Index, tier, Words("STR_OZL_TREE_UNKNOWN_ROW"), "—", "");
            }
        }
        list.Update();
    }

    private static int StubTier(OZL_HiddenView h)
    {
        int t = h.Tier;
        if (t < 1)
            t = 1;
        if (t > OZL_TreePlan.MAX_TIER)
            t = OZL_TreePlan.MAX_TIER;
        return t;
    }

    private void RegRow(Widget list, string id, int index, int tier, string name, string state, string status)
    {
        Widget row = Row("registry_row", list);
        if (!row)
            return;
        // Клацається RegHit (кнопка зі style Empty), або сам рядок -- тоді він
        // сам має бути такою кнопкою. Рядок заглушки не клацається зовсім.
        Widget hit = row.FindAnyWidget("RegHit");
        if (!hit)
            hit = row;
        if (id != "")
        {
            hit.SetName("reg:" + id);
            IgnorePointer(row, hit);
        }
        else
        {
            if (hit != row)
                hit.Show(false);
            IgnorePointer(row, null);
        }
        SetRowText(row, "RegNum", OZL_Text.Two(index + 1));
        SetRowText(row, "RegName", name);
        SetRowText(row, "RegTier", tier.ToString());
        SetRowText(row, "RegState", state);
        TextWidget st = TextWidget.Cast(row.FindAnyWidget("RegState"));
        if (st && status != "")
            st.SetColor(m_Skin.StatusColorOf(status));
        Widget pick = row.FindAnyWidget("RegPick");
        if (pick)
            pick.Show(id != "" && id == m_Node);
        m_RegRows.Insert(row);
    }

    private void SetRowText(Widget row, string name, string text)
    {
        TextWidget t = TextWidget.Cast(row.FindAnyWidget(name));
        if (t)
            t.SetText(text);
    }

    // ---------- картка (renderCard() мокапа) ----------

    private void PaintCard()
    {
        Unlink(m_CostRows);
        Unlink(m_OpenChips);
        OZL_NodeView n = NodeOf(m_Node);
        Widget empty = Role("CardEmpty");
        Widget body = Role("CardBody");
        if (empty)
            empty.Show(!n);
        if (body)
            body.Show(n != null);
        if (!n)
        {
            m_Skin.OnSelect(this, null, "", false);
            return;
        }
        string st = n.Status;
        bool paid = st == "completed" || st == "researching";

        PutText(Role("CardName"), m_Skin.NodeNameText(n.Name), 0);
        PutText(Role("CardMeta"), MetaOf(n), 0);
        TextWidget status = TextWidget.Cast(Role("CardStatus"));
        if (status)
        {
            status.SetText(m_Skin.StatusText(st));
            status.SetColor(m_Skin.StatusColorOf(st));
        }
        PutText(Role("CardDesc"), n.Desc, 0);
        SetText("CardDescHead", m_Skin.SectionText("STR_OZL_TREE_DESC"));
        SetText("CardCostHead", m_Skin.SectionText("STR_OZL_TREE_COST"));
        SetText("CardItemsHead", m_Skin.SectionText("STR_OZL_TREE_ITEMS"));
        SetText("CardTimeHead", m_Skin.SectionText("STR_OZL_TREE_TIME"));
        SetText("CardOpensHead", m_Skin.SectionText("STR_OZL_TREE_OPENS"));

        // Вартість по лініях і матеріали: "є / треба" і смужка.
        Widget costs = Role("CardCostList");
        int i;
        for (i = 0; i < n.Cost.Count() && costs; i++)
        {
            OZL_KV kv = n.Cost[i];
            if (kv)
                CostRow(costs, PointColor(kv.Key), PointName(kv.Key), PoolOf(kv.Key), kv.Value, paid, true);
        }
        Widget items = Role("CardItemList");
        Widget itemsHead = Role("CardItemsHead");
        if (itemsHead)
            itemsHead.Show(n.Items.Count() > 0);
        if (items)
            items.Show(n.Items.Count() > 0);
        for (i = 0; i < n.Items.Count() && items; i++)
        {
            OZL_ItemView iv = n.Items[i];
            if (iv)
                CostRow(items, m_Skin.Dim, ItemLabel(iv), iv.Have, iv.Qty, paid, iv.Have >= 0);
        }

        PaintTime(n);
        PaintOpens(n);

        // Кнопка видна завжди; неактивна -- з причиною під нею (спека §5.4).
        bool can = st == "available" && m_View.MaySpend;
        string label = Words("STR_OZL_TREE_RESEARCH");
        if (st == "completed")
            label = Words("STR_OZL_TREE_COMPLETED");
        SetText("BtnResearchText", label);
        Widget btn = Role("BtnResearch");
        if (btn)
        {
            btn.Show(true);
            m_Skin.PaintButton(this, btn, can);
        }
        Widget hover = Role("BtnResearchHover");
        if (hover)
            hover.Show(false);
        SetText("CardWhy", WhyOf(n));

        // Печатка (Долг): картинка, яку скажe скін; нема -- схована.
        Widget stamp = Role("CardStamp");
        if (stamp)
        {
            string seal = m_Skin.StampOf(st);
            ImageWidget sealImg = ImageWidget.Cast(Role("CardStampImg"));
            bool sealOn = seal != "" && sealImg && sealImg.LoadImageFile(0, seal);
            if (sealOn)
                sealImg.SetImage(0);
            stamp.Show(sealOn);
        }

        UpdateRole("CardCostList");
        UpdateRole("CardItemList");
        UpdateRole("CardFlow");
        ScrollWidget cardScroll = ScrollWidget.Cast(Role("CardScroll"));
        if (cardScroll)
            cardScroll.VScrollToPos(0);
        m_Skin.OnSelect(this, n, st, can);
    }

    private void UpdateRole(string role)
    {
        Widget w = Role(role);
        if (w)
            w.Update();
    }

    // "тир 2 · після: Назва" / "після всіх: А, невідомо" / "після будь-якого з: ...".
    private string MetaOf(OZL_NodeView n)
    {
        string meta = Words("STR_OZL_TREE_TIER") + " " + n.Tier.ToString();
        int count = n.Parents.Count();
        if (count == 0)
            return meta;
        string key = "STR_OZL_TREE_AFTER_ONE";
        if (count > 1)
        {
            key = "STR_OZL_TREE_AFTER_ALL";
            if (n.Any)
                key = "STR_OZL_TREE_AFTER_ANY";
        }
        string names = "";
        for (int i = 0; i < count; i++)
        {
            if (i > 0)
                names += ", ";
            names += ParentName(n.Parents[i]);
        }
        return meta + " · " + Words(key) + " " + names;
    }

    private string ParentName(string id)
    {
        OZL_NodeView p = AnyNodeOf(id);
        if (p)
            return p.Name;
        return Words("STR_OZL_TREE_UNKNOWN");
    }

    private string WhyOf(OZL_NodeView n)
    {
        string st = n.Status;
        if (st == "researching")
            return Words("STR_OZL_TREE_WHY_BUSY");
        if (st == "locked")
        {
            if (n.Any)
                return Words("STR_OZL_TREE_WHY_LOCKED_ANY");
            return Words("STR_OZL_TREE_WHY_LOCKED_ALL");
        }
        if (st == "short")
            return Words("STR_OZL_TREE_WHY_SHORT");
        if (st == "available" && !m_View.MaySpend)
            return Words("STR_OZL_TREE_WHY_LEADER");
        return "";
    }

    // Рядок вартості: назва, "є / треба" (заплачено -- лише "треба"; Have
    // невідомий -- лише "треба", без вироку), смужка.
    private void CostRow(Widget list, int chipColor, string label, int have, int need, bool paid, bool known)
    {
        Widget row = Row("cost_row", list);
        if (!row)
            return;
        m_CostRows.Insert(row);
        Widget chip = row.FindAnyWidget("CostChip");
        if (chip)
            chip.SetColor(chipColor);
        string text = have.ToString() + " / " + need.ToString();
        if (paid || !known)
            text = need.ToString();
        int verdict = 0;
        if (paid || (known && have >= need))
            verdict = 1;
        else if (known)
            verdict = -1;
        float frac = 1;
        if (!paid && need > 0)
        {
            frac = have;
            frac = frac / need;
        }
        if (!known && !paid)
            frac = 0;
        m_Skin.PaintCostRow(this, row, label, text, verdict);
        Widget bar = row.FindAnyWidget("CostBar");
        if (bar)
        {
            bar.Show(known || paid);
            BarLater(bar, row.FindAnyWidget("CostBarFill"), frac);
        }
    }

    private void PaintTime(OZL_NodeView n)
    {
        bool going = n.Status == "researching";
        string time;
        if (going)
        {
            int left = LeftOf(n);
            time = Words("STR_OZL_TREE_LEFT") + " " + OZL_Text.Clock(left);
            if (n.Duration > 0)
                time += " " + Words("STR_OZL_TREE_OF") + " " + OZL_Text.Duration(n.Duration);
            SetText("CardTimer", OZL_Text.Clock(left));
        }
        else if (n.Duration > 0)
        {
            time = Words("STR_OZL_TREE_TIME") + ": " + OZL_Text.Duration(n.Duration);
        }
        else
        {
            time = Words("STR_OZL_TREE_INSTANT");
        }
        SetText("CardTime", time);
        Widget timer = Role("CardTimer");
        if (timer)
            timer.Show(going);
        PaintSegments(going, ProgressOf(n));
    }

    // 20 сегментів (CardSeg0..19) або смуга CardBar -- що є в розкладці.
    private void PaintSegments(bool going, float frac)
    {
        Widget segs = Role("CardSegs");
        if (segs)
            segs.Show(going);
        int on = Math.Round(20 * frac);
        int onColor = m_Skin.SegOn;
        if (onColor == 0)
            onColor = m_Skin.Acc;
        int offColor = m_Skin.SegOff;
        if (offColor == 0)
            offColor = m_Skin.LineDim;
        for (int i = 0; i < 20; i++)
        {
            Widget seg = Role("CardSeg" + i.ToString());
            if (!seg)
                break;
            if (i < on)
                seg.SetColor(onColor);
            else
                seg.SetColor(offColor);
        }
        Widget bar = Role("CardBar");
        if (bar)
        {
            bar.Show(going);
            if (going)
                BarLater(bar, Role("CardBarFill"), frac);
        }
    }

    // "Відкриває": діти вузла серед видимих вузлів і заглушок туману, у
    // порядку гілки; заглушки -- "??? невідомо", не клацаються.
    private void PaintOpens(OZL_NodeView n)
    {
        Widget list = Role("CardOpensList");
        Widget head = Role("CardOpensHead");
        OZL_BranchView b = CurrentBranch();
        int count = 0;
        for (int index = 0; b && index <= MaxIndex(b); index++)
        {
            OZL_NodeView kid = KidAt(b, index, n.Id);
            if (kid)
            {
                string tag = "";
                if (kid.Any)
                    tag = " " + Words("STR_OZL_TREE_OR_TAG");
                else if (kid.Parents.Count() > 1)
                    tag = " " + Words("STR_OZL_TREE_MORE_TAG");
                OpenChip(list, kid.Id, kid.Name + tag);
                count++;
            }
            else if (StubAt(b, index, n.Id))
            {
                OpenChip(list, "", Words("STR_OZL_TREE_UNKNOWN_OPENS"));
                count++;
            }
        }
        if (head)
            head.Show(count > 0);
        if (list)
        {
            list.Show(count > 0);
            if (count > 0)
                FlowLater(list, 6, 4, true);
        }
    }

    private int MaxIndex(OZL_BranchView b)
    {
        int most = -1;
        int i;
        for (i = 0; i < b.Nodes.Count(); i++)
        {
            if (b.Nodes[i] && b.Nodes[i].Index > most)
                most = b.Nodes[i].Index;
        }
        for (i = 0; i < b.Hidden.Count(); i++)
        {
            if (b.Hidden[i] && b.Hidden[i].Index > most)
                most = b.Hidden[i].Index;
        }
        return most;
    }

    private OZL_NodeView KidAt(OZL_BranchView b, int index, string parent)
    {
        for (int i = 0; i < b.Nodes.Count(); i++)
        {
            OZL_NodeView k = b.Nodes[i];
            if (!k || k.Index != index)
                continue;
            for (int p = 0; p < k.Parents.Count(); p++)
            {
                if (k.Parents[p] == parent)
                    return k;
            }
        }
        return null;
    }

    private bool StubAt(OZL_BranchView b, int index, string parent)
    {
        for (int i = 0; i < b.Hidden.Count(); i++)
        {
            OZL_HiddenView h = b.Hidden[i];
            if (!h || h.Index != index)
                continue;
            for (int p = 0; p < h.Parents.Count(); p++)
            {
                if (h.Parents[p] == parent)
                    return true;
            }
        }
        return false;
    }

    // Чіп "Відкриває". Клацається ChipHit (кнопка зі style Empty), або сам
    // рядок -- тоді він сам має бути такою кнопкою; решта чіпа мишу
    // пропускає. Заглушка туману (id "") не клацається зовсім; як вона
    // виглядає -- каже скін (PaintOpenChip: колір, підкреслення).
    private void OpenChip(Widget list, string id, string text)
    {
        if (!list)
            return;
        Widget chip = Row("opens_chip", list);
        if (!chip)
            return;
        m_OpenChips.Insert(chip);
        Widget hit = chip.FindAnyWidget("ChipHit");
        if (!hit)
            hit = chip;
        bool fogged = id == "";
        if (!fogged)
        {
            hit.SetName("open:" + id);
            IgnorePointer(chip, hit);
        }
        else
        {
            if (hit != chip)
                hit.Show(false);
            IgnorePointer(chip, null);
        }
        m_Skin.PaintOpenChip(this, chip, text, fogged);
    }

    // Кожну секунду: залишок і смуга проєктів, що йдуть; таймер картки.
    // Проєкт, що мав би вже скінчитись, -- привід спитати свіже дерево.
    private void PaintProgress()
    {
        if (!m_View || !m_Plan)
            return;
        bool ended = false;
        for (int i = 0; i < m_Cells.Count() && i < m_Plan.Ids.Count(); i++)
        {
            OZL_NodeView n = NodeOf(m_Plan.Ids[i]);
            Widget cell = m_Cells[i];
            if (!n || !cell || n.Status != "researching")
                continue;
            int left = LeftOf(n);
            if (left <= 0)
                ended = true;
            TextWidget plain = TextWidget.Cast(cell.FindAnyWidget("NodePriceText"));
            if (plain)
                plain.SetText(Words("STR_OZL_TREE_LEFT") + " " + OZL_Text.Clock(left));
            PaintNodeBar(cell, n);
        }
        OZL_NodeView picked = NodeOf(m_Node);
        if (picked && picked.Status == "researching")
            PaintTime(picked);
        if (ended && m_AskAgain <= 0)
        {
            m_AskAgain = 5;
            OZ_Rpc.ServiceRequest(OZL_Const.SERVICE, OZL_Const.OP_TREE, "{}");
        }
    }

    // Рядок під кнопкою: відповідь на запит, відмова. Вікна ще нема
    // (відмова чи нечитана відповідь до першого дерева) -- текст стає на
    // місце «Дерево завантажується...» хоста, а не зникає.
    void Say(string text)
    {
        TextWidget why = TextWidget.Cast(Role("CardWhy"));
        if (why)
        {
            why.SetText(text);
            return;
        }
        if (m_Window || !layoutRoot)
            return;
        TextWidget loading = TextWidget.Cast(layoutRoot.FindAnyWidget("TreeLoading"));
        if (loading)
        {
            loading.SetText(text);
            loading.Show(true);
        }
    }

    // ------------------------------------------------------------------
    // Вибір, наведення, підказка
    // ------------------------------------------------------------------

    // Вибір міняє дві комірки -- стару й нову вибрану; решта не
    // перемальовується (і не перекладає назв).
    void Select(string id)
    {
        if (!NodeOf(id))
            return;
        string was = m_Node;
        m_Node = id;
        RepaintCell(was);
        if (id != was)
            RepaintCell(id);
        if (m_Hover != "")
            HoverShape(m_Hover, true);
        PaintRegistry();
        PaintCard();
        m_NeedLines = true;
    }

    private void RepaintCell(string id)
    {
        OZL_NodeView n = NodeOf(id);
        Widget cell = CellOf(id);
        if (n && cell)
            m_Skin.PaintNode(this, cell, n, n.Status, n.Id == m_Node);
    }

    void PickBranch(string id)
    {
        if (!BranchOf(id) || id == m_Branch)
            return;
        m_Branch = id;
        m_Node = DefaultNode();
        m_NeedHome = true;
        PaintAll();
    }

    private void SetHover(string id)
    {
        if (id == m_Hover)
            return;
        if (m_Hover != "")
            HoverShape(m_Hover, false);
        m_Hover = id;
        if (m_Hover != "")
            HoverShape(m_Hover, true);
        Widget tip = Role("TreeTip");
        if (tip)
            tip.Show(false);
        // Через локальну: складений булевий вираз просто в поле псує купу.
        bool pending = false;
        if (m_Hover != "" && tip)
            pending = true;
        m_TipPending = pending;
        m_TipTries = 0;
        if (m_TipPending)
        {
            OZL_NodeView n = NodeOf(m_Hover);
            if (n)
                SetText("TreeTipText", n.Name + " · " + m_Skin.StatusText(n.Status));
        }
        m_NeedLines = true;
    }

    private void HoverShape(string id, bool on)
    {
        if (!m_Skin || m_Skin.ShapeHover < 0)
            return;
        Widget cell = CellOf(id);
        OZL_NodeView n = NodeOf(id);
        if (!cell || !n)
            return;
        ImageWidget shape = ImageWidget.Cast(cell.FindAnyWidget("NodeShape"));
        if (!shape)
            return;
        int slot = m_Skin.ShapeOf(n.Status, n.Id == m_Node);
        if (on)
            slot = m_Skin.ShapeHover;
        if (slot >= 0)
            shape.SetImage(slot);
    }

    // Підказка над вузлом: ширина -- за текстом, тож ставиться, коли текст
    // розкладено (наступним кадром).
    private void RunTip()
    {
        if (!m_TipPending)
            return;
        Widget tip = Role("TreeTip");
        TextWidget text = TextWidget.Cast(Role("TreeTipText"));
        int at = m_Plan.IndexOf(m_Hover);
        if (!tip || !text || at < 0)
        {
            m_TipPending = false;
            return;
        }
        int pw;
        int ph;
        text.GetTextSize(pw, ph);
        if (pw <= 0 && m_TipTries < LATER_TRIES)
        {
            m_TipTries++;
            return;
        }
        m_TipPending = false;
        float boxW;
        float boxH;
        UnitsOf(tip, boxW, boxH);
        float w = pw / m_Px + 2 * m_Skin.TipPadX;
        // Над вузлом, по центру, не ближче 120 одиниць до країв вмісту.
        float x = Math.Clamp(m_Plan.X[at], 120, m_Plan.W - 120) - w / 2;
        float y = m_Plan.Y[at] - m_Skin.NodeH / 2 - 36;
        SizeUnits(tip, w, boxH);
        Widget bg = tip.FindAnyWidget("TreeTipBg");
        if (bg)
            SizeUnits(bg, w - 2, boxH - 2);
        PlaceUnits(tip, x, y);
        tip.Show(true);
    }

    // ------------------------------------------------------------------
    // Відкладене: смуги, риски під текстом, ряди чіпів
    // ------------------------------------------------------------------

    // Перенос по словах: перший напис -- і мірило (SetText + GetTextSize,
    // як ванільні actiontargetscursor.c і tabberui.c роблять в одному кадрі).
    private void RunWraps()
    {
        if (m_Wraps.Count() == 0)
            return;
        // Стос картки оновлюється раз за кадр і лише якщо переклали щось у ній.
        Widget flow = Role("CardFlow");
        bool cardDone = false;
        for (int j = m_Wraps.Count() - 1; j >= 0; j--)
        {
            OZL_TreeWrap job = m_Wraps[j];
            if (!job.Box)
            {
                m_Wraps.RemoveOrdered(j);
                continue;
            }
            string stem = job.Box.GetName();
            array<TextWidget> lines = new array<TextWidget>();
            for (int k = 0; k < 32; k++)
            {
                TextWidget line = TextWidget.Cast(job.Box.FindAnyWidget(stem + k.ToString()));
                if (!line)
                    break;
                lines.Insert(line);
            }
            if (lines.Count() == 0)
            {
                m_Wraps.RemoveOrdered(j);
                continue;
            }
            float lw;
            float lh;
            lines[0].GetScreenSize(lw, lh);
            if (lw <= 0 && job.Tries < LATER_TRIES)
            {
                job.Tries++;
                continue;
            }
            array<string> words = new array<string>();
            job.Text.Split(" ", words);
            array<string> rows = new array<string>();
            string cur = "";
            for (int w = 0; w < words.Count(); w++)
            {
                if (words[w] == "")
                    continue;
                string cand = words[w];
                if (cur != "")
                    cand = cur + " " + words[w];
                int pw;
                int ph;
                lines[0].SetText(cand);
                lines[0].Update();
                lines[0].GetTextSize(pw, ph);
                // Останній напис бере решту цілою -- обріже рушій.
                if (pw > lw && cur != "" && rows.Count() < lines.Count() - 1)
                {
                    rows.Insert(cur);
                    cur = words[w];
                }
                else
                {
                    cur = cand;
                }
            }
            if (cur != "")
                rows.Insert(cur);
            for (int n = 0; n < lines.Count(); n++)
            {
                bool used = n < rows.Count();
                if (used)
                    lines[n].SetText(rows[n]);
                else
                    lines[n].SetText("");
                if (job.Color != 0)
                    lines[n].SetColor(job.Color);
                lines[n].Show(used);
            }
            job.Box.Update();
            m_WrapShown.Set(job.Box, job.Text + "|" + job.Color.ToString());
            if (flow && Holds(flow, job.Box))
                cardDone = true;
            m_Wraps.RemoveOrdered(j);
        }
        if (cardDone)
            flow.Update();
    }

    private void RunBars()
    {
        for (int i = m_Bars.Count() - 1; i >= 0; i--)
        {
            OZL_TreeBarJob job = m_Bars[i];
            if (!job.Track || !job.Fill)
            {
                m_Bars.RemoveOrdered(i);
                continue;
            }
            float tw;
            float th;
            UnitsOf(job.Track, tw, th);
            if (tw <= 0 && job.Tries < LATER_TRIES)
            {
                job.Tries++;
                continue;
            }
            float fw;
            float fh;
            UnitsOf(job.Fill, fw, fh);
            if (fh <= 0)
                fh = th;
            SizeUnits(job.Fill, tw * job.Frac, fh);
            m_Bars.RemoveOrdered(i);
        }
    }

    private void RunFits()
    {
        for (int i = m_Fits.Count() - 1; i >= 0; i--)
        {
            OZL_TreeFit fit = m_Fits[i];
            if (!fit.Text || !fit.Target)
            {
                m_Fits.RemoveOrdered(i);
                continue;
            }
            int pw;
            int ph;
            fit.Text.GetTextSize(pw, ph);
            if (pw <= 0 && fit.Tries < LATER_TRIES)
            {
                fit.Tries++;
                continue;
            }
            float w = pw / m_Px + fit.Pad;
            float tw;
            float th;
            UnitsOf(fit.Target, tw, th);
            SizeUnits(fit.Target, w, th);
            if (fit.Mode == 2)
            {
                // По центру батька, на тій самій висоті.
                Widget parent = fit.Target.GetParent();
                float pwU;
                float phU;
                UnitsOf(parent, pwU, phU);
                float px;
                float py;
                float qx;
                float qy;
                parent.GetScreenPos(px, py);
                fit.Target.GetScreenPos(qx, qy);
                PlaceUnits(fit.Target, (pwU - w) / 2, (qy - py) / m_Px);
            }
            m_Fits.RemoveOrdered(i);
        }
    }

    // Діти контейнера -- рядком зліва направо: ширина елемента -- від його
    // лівого краю до правого краю його тексту (+ Pad); проміжок Gap; з
    // переносом -- новий рядок, коли не влазить. Віджети елемента з назвою на
    // ...Hit і ...Line розтягуються на його ширину (клік і підкреслення).
    private void RunFlows()
    {
        for (int f = m_Flows.Count() - 1; f >= 0; f--)
        {
            OZL_TreeFlow flow = m_Flows[f];
            if (!flow.Box)
            {
                m_Flows.RemoveOrdered(f);
                continue;
            }
            if (!FlowReady(flow.Box) && flow.Tries < LATER_TRIES)
            {
                flow.Tries++;
                continue;
            }
            float boxW;
            float boxH;
            UnitsOf(flow.Box, boxW, boxH);
            float bx;
            float by;
            flow.Box.GetScreenPos(bx, by);
            float x = 0;
            float y = 0;
            float lineH = 0;
            Widget item = flow.Box.GetChildren();
            while (item)
            {
                if (item.IsVisible())
                {
                    float iw;
                    float ih;
                    ItemExtent(item, iw, ih);
                    iw += flow.Pad;
                    if (flow.Wrap && x > 0 && x + iw > boxW)
                    {
                        x = 0;
                        y += lineH;
                        lineH = 0;
                    }
                    PlaceUnits(item, x, y);
                    StretchParts(item, iw, ih);
                    x += iw + flow.Gap;
                    if (ih > lineH)
                        lineH = ih;
                }
                item = item.GetSibling();
            }
            if (flow.Wrap)
            {
                SizeUnits(flow.Box, boxW, y + lineH);
                UpdateRole("CardFlow");
            }
            m_Flows.RemoveOrdered(f);
        }
    }

    // Чи розкладено тексти елементів (ширина тексту вже не нуль).
    private bool FlowReady(Widget box)
    {
        Widget item = box.GetChildren();
        while (item)
        {
            TextWidget t = FirstText(item);
            if (t && item.IsVisible())
            {
                int pw;
                int ph;
                t.GetTextSize(pw, ph);
                if (pw <= 0)
                    return false;
            }
            item = item.GetSibling();
        }
        return true;
    }

    private TextWidget FirstText(Widget item)
    {
        Widget c = item.GetChildren();
        while (c)
        {
            TextWidget t = TextWidget.Cast(c);
            if (t && c.IsVisible())
                return t;
            c = c.GetSibling();
        }
        return null;
    }

    // Ширина елемента в одиницях: від його лівого краю до правого краю
    // ТЕКСТУ (GetTextSize, текст -- від лівого краю напису), а не напису;
    // висота -- його власна. TextWidget обрізає свій текст своїм краєм, а
    // "size to text h" дає суму кроків гліфів: похилий останній гліф
    // рукописного шрифту (d, l у Caveat) втрачає верхівку (виміряно
    // 2026-10-31). Напис ширший за текст її зберігає, і ряд лягає так само.
    private void ItemExtent(Widget item, out float w, out float h)
    {
        float ix;
        float iy;
        item.GetScreenPos(ix, iy);
        float iw;
        float ih;
        item.GetScreenSize(iw, ih);
        h = ih / m_Px;
        w = 0;
        TextWidget t = FirstText(item);
        if (!t)
            return;
        float tx;
        float ty;
        t.GetScreenPos(tx, ty);
        int pw;
        int ph;
        t.GetTextSize(pw, ph);
        w = (tx + pw - ix) / m_Px;
    }

    private void StretchParts(Widget item, float w, float h)
    {
        Widget c = item.GetChildren();
        while (c)
        {
            string nm = c.GetName();
            bool hit = nm.Length() > 3 && nm.IndexOf("Hit") == nm.Length() - 3;
            bool line = nm.Length() > 4 && nm.IndexOf("Line") == nm.Length() - 4;
            if (hit || line || nm.IndexOf("open:") == 0)
            {
                float cw;
                float ch;
                UnitsOf(c, cw, ch);
                SizeUnits(c, w, ch);
            }
            c = c.GetSibling();
        }
    }

    // ------------------------------------------------------------------
    // Виміри (R6): одиниці SetPos/SetSize, прокрутки, канви
    // ------------------------------------------------------------------

    // Двоточкова проба на невидимій рамці хоста: SetPos(0) і SetPos(100) з
    // кадром між ними (віджет до першого розкладання міряється нулями). Без
    // рамки чи без руху -- виміряне 2026-10-31: Set* беруть пікселі, K = Px.
    private void Probe()
    {
        if (m_ProbeStep == 0)
            return;
        float x;
        float y;
        float w;
        float h;
        if (m_ProbeStep == 1)
        {
            int sw;
            int sh;
            GetScreenSize(sw, sh);
            if (sh > 0)
                m_Px = sh / 1080.0;
            if (!m_Probe)
            {
                m_K = m_Px;
                m_ProbeStep = 0;
                OZL_Log.Warn("tree: the host has no TreeProbe, taking SetPos/SetSize in screen pixels (measured 2026-10-31)");
                return;
            }
            m_Probe.SetPos(0, 0);
            m_Probe.SetSize(100, 100);
            m_ProbeStep = 2;
            return;
        }
        if (m_ProbeStep == 2)
        {
            m_Probe.GetScreenPos(x, y);
            m_Probe.GetScreenSize(w, h);
            m_ProbeX = x;
            m_ProbeW = w;
            m_Probe.SetPos(100, 0);
            m_ProbeStep = 3;
            return;
        }
        m_Probe.GetScreenPos(x, y);
        float perSet = (x - m_ProbeX) / 100;
        if (perSet < 0.2 || perSet > 8)
        {
            m_ProbeTries++;
            if (m_ProbeTries < 10)
            {
                m_ProbeStep = 1;
                return;
            }
            OZL_Log.Warn("tree: the SetPos probe read no movement, taking screen pixels (measured 2026-10-31)");
            perSet = 1;
        }
        m_K = m_Px / perSet;
        m_ProbeStep = 0;
        int scrW;
        int scrH;
        GetScreenSize(scrW, scrH);
        OZL_Log.Dbg("tree: measured screen " + scrW.ToString() + "x" + scrH.ToString() + ", " + m_Px.ToString() + " px per layout unit; SetPos moves " + perSet.ToString() + " px per unit given, SetSize(100) is " + m_ProbeW.ToString() + " px; so K = " + m_K.ToString() + " Set-units per layout unit");
    }

    // "Додому": вниз -- до початку, вгору -- до кінця, вправо -- до лівого
    // краю; поперек -- до середини (scrollHome() мокапа). Кадр після розміру
    // вмісту: прокрутка бачить новий розмір не одразу. Колишня проба
    // прокрутки (VScrollToPos01(0), потім (1)) на кожному відкритті кидала
    // дерево в кінець на кілька кадрів; одиниці прокрутки вже виміряно.
    private void Home()
    {
        if (m_NeedTree)
            return;
        if (m_HomeWait < 1)
        {
            m_HomeWait++;
            return;
        }
        m_NeedHome = false;
        m_HomeWait = 0;
        ScrollWidget sw = ScrollWidget.Cast(Role("TreeScroll"));
        if (!sw || !m_Skin)
            return;
        if (m_Skin.Dir == "right")
        {
            sw.HScrollToPos01(0);
            sw.VScrollToPos01(0.5);
        }
        else
        {
            if (m_Skin.Dir == "up")
                sw.VScrollToPos01(1);
            else
                sw.VScrollToPos01(0);
            sw.HScrollToPos01(0.5);
        }
    }

    // ------------------------------------------------------------------
    // Миша
    // ------------------------------------------------------------------

    private bool InTree(Widget w)
    {
        Widget scroll = Role("TreeScroll");
        while (w && scroll)
        {
            if (w == scroll)
                return true;
            w = w.GetParent();
        }
        return false;
    }

    // Натиск на самому TreeScroll -- це його смуга прокрутки (вміст закривають
    // TreeNodes та інші рамки): її тягне рушій, вміст за мишею не їде.
    override bool OnMouseButtonDown(Widget w, int x, int y, int button)
    {
        Widget scroll = Role("TreeScroll");
        if (button == MouseState.LEFT && w && w != scroll && InTree(w))
        {
            ScrollWidget sw = ScrollWidget.Cast(Role("TreeScroll"));
            if (sw)
            {
                m_DragDown = true;
                m_DragMoved = false;
                GetMousePos(m_DragX, m_DragY);
                m_DragH = sw.GetHScrollPos();
                m_DragV = sw.GetVScrollPos();
            }
        }
        return super.OnMouseButtonDown(w, x, y, button);
    }

    // Натиснули на дереві й тягнуть: прокрутка йде за мишею; зсув більше 4
    // одиниць -- і відпускання вже не вибирає вузол.
    private void Drag()
    {
        if (!m_DragDown)
            return;
        if (!(GetMouseState(MouseState.LEFT) & 0x80000000))
        {
            m_DragDown = false;
            return;
        }
        int mx;
        int my;
        GetMousePos(mx, my);
        float dx = mx - m_DragX;
        float dy = my - m_DragY;
        if (Math.AbsFloat(dx) + Math.AbsFloat(dy) > 4 * m_Px)
            m_DragMoved = true;
        if (!m_DragMoved)
            return;
        ScrollWidget sw = ScrollWidget.Cast(Role("TreeScroll"));
        if (!sw)
            return;
        // Прокрутка в пікселях, як і миша: 300 x 200 px тягнення зсувають
        // вміст рівно на 300 x 200 px (виміряно 2026-10-31).
        sw.HScrollToPos(m_DragH - dx);
        sw.VScrollToPos(m_DragV - dy);
    }

    override bool OnMouseEnter(Widget w, int x, int y)
    {
        if (w)
        {
            string id = NodeIdAt(w);
            if (id != "")
                SetHover(id);
            else if (w.GetName() == "BtnResearch")
                HoverButton(true);
        }
        return super.OnMouseEnter(w, x, y);
    }

    override bool OnMouseLeave(Widget w, Widget enterW, int x, int y)
    {
        if (w)
        {
            string from = NodeIdAt(w);
            if (from != "" && from == m_Hover)
            {
                string to = "";
                if (enterW)
                    to = NodeIdAt(enterW);
                if (to != m_Hover)
                    SetHover(to);
            }
            else if (w.GetName() == "BtnResearch")
            {
                HoverButton(false);
            }
        }
        return super.OnMouseLeave(w, enterW, x, y);
    }

    private void HoverButton(bool on)
    {
        Widget hover = Role("BtnResearchHover");
        if (!hover)
            return;
        OZL_NodeView n = NodeOf(m_Node);
        bool can = n && n.Status == "available" && m_View && m_View.MaySpend;
        hover.Show(on && can);
    }

    override bool OnClick(Widget w, int x, int y, int button)
    {
        if (!w)
            return super.OnClick(w, x, y, button);
        // Клік наприкінці перетягування -- не вибір.
        if (m_DragMoved && InTree(w))
        {
            m_DragMoved = false;
            return true;
        }
        string nm = w.GetName();
        if (nm == "BtnClose")
        {
            CloseTree();
            return true;
        }
        if (nm == "BtnResearch")
        {
            Research();
            return true;
        }
        // Рядки й чіпи -- за іменем на віджеті або на його предку (RowHit,
        // ChipHit, RegHit чи сам рядок-кнопка).
        string branch = TaggedAt(w, "branch:");
        if (branch != "")
        {
            PickBranch(branch);
            return true;
        }
        string opened = TaggedAt(w, "open:");
        if (opened != "")
        {
            Select(opened);
            return true;
        }
        string listed = TaggedAt(w, "reg:");
        if (listed != "")
        {
            Select(listed);
            return true;
        }
        string clicked = NodeIdAt(w);
        if (clicked != "")
        {
            Select(clicked);
            return true;
        }
        if (m_Skin && m_Skin.OnClick(this, w))
            return true;
        return super.OnClick(w, x, y, button);
    }

    private void Research()
    {
        OZL_NodeView n = NodeOf(m_Node);
        if (!n || n.Status != "available" || !m_View.MaySpend)
            return;
        OZ_Rpc.ServiceRequest(OZL_Const.SERVICE, OZL_Const.OP_RESEARCH, "{\"NodeId\":\"" + n.Id + "\"}");
        Say(Words("STR_OZL_TREE_ASKING"));
    }
}

#endif
