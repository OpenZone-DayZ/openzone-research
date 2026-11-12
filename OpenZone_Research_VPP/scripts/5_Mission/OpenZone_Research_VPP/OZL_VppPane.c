// Модуль «ДОСЛІДЖЕННЯ» в адмінському вікні OpenZone. З 2026-11-09 це редактор
// досліджень (docs/specs/2026-11-09-research-editor-vpp-design.md): по
// сторінці на розділ і смуга дій чернетки. З 2026-11-12 (переробка вікна VPP,
// дизайн §5.5) розділи -- це сторінки рейки вікна: вісім сторінок модуля
// "research" показують ОДНУ панель, а сторінку всередині перемикає
// OnPaneShown. ОГЛЯД -- те, чим панель була досі: фракції з пулами,
// нарахування, завершення вузла, скидання, перечитування конфігів. Чернетка
// семи файлів -- у OZL_EdDocs. Чіпляється через modded class -- ядро про
// дослідження не знає й знати не мусить.
//
// Гарди: NO_GUI -- сервер компілює Mission без UI; AVPPAdminTools і
// OpenZone_VPP -- імена класів CfgMods (їх авто-дефайнить рушій).
//
// Розмітка -- з опису ui/OpenZone_Research_VPP/oz_research_vpp_pane.json
// (layout_build); тут лише імена віджетів. Незворотні дії -- у два
// натискання, як і всюди у вікні: модальні вікна у VPP -- пастка.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    // The page ids of the rail are "research." + the key of the page inside the pane.
    static const string RZ_PAGE = "research.";

    private ref array<ref OZL_AdminOwner> m_ResOwners;
    private int  m_ResPicked    = -1;
    // Перемальовування списку кличе SelectRow, рушій відповідає OnItemSelected
    // -- прапорець рве це коло (як у ядрі й у сусідніх панелях).
    private bool m_ResRepaint = false;

    // ------------------------------------------------- редактор
    private ref OZL_EdDocs m_Ed;

    // Відкрита сторінка (ключ сторінки рейки після "research.") і чи відкрита
    // над смугою чернетки панель проблем.
    private string m_RzTab = "overview";
    private bool   m_RzProblems = false;

    // The content area the shell gave the pane (OnWindowResized), and the page area
    // inside it as RzLayout left it, in pixels: every layer lays its page out from
    // these instead of reading sizes back.
    private float m_RzW = 0;
    private float m_RzH = 0;
    private float m_RzPageW = 0;
    private float m_RzPageH = 0;

    // Сім cfg_get уже стоять у черзі ядра (раз на вікно; далі -- лише
    // перечитування застосованого).
    private bool m_RzAsked = false;

    // Скрипт пише поля форми сам: OnChange, що прилетить на це, -- не правка.
    private bool m_RzFill = false;

    // Типи балів: вибраний рядок.
    private int  m_PtPicked = -1;

    // Дерево: власник, гілка, вибраний вузол.
    private string m_TrOwner  = "";
    private string m_TrBranch = "";
    private string m_TrSel    = "";

    // Id, на який зараз указують посилання, поки поле Id набирається:
    // посилання йдуть за вузлом лише на вільний Id (RenameTn).
    private string m_TnRefId = "";

    // Полотно: скін власника, план, вигляд гілки, комірки, мітки "АБО".
    private ref OZL_TreeSkin   m_TrSkin;
    private string             m_TrSkinId = "";
    private ref OZL_TreePlan   m_TrPlan;
    private ref OZL_BranchView m_TrView;
    private ref array<Widget>  m_TrCells;
    private ref array<ref OZL_TreeOrMark> m_TrOrs;
    private ref array<Widget>  m_TrOrLabels;

    // Контейнери фішок ціни, що чекають розкладки: тексти мають ширину лише
    // кадром пізніше (OnUpdate -> RunTrFlows).
    private ref array<Widget>  m_TrFlows;
    private int                m_TrFlowTries = 0;

    // Режим зв'язку: увімкнений і від якого вузла (порожньо -- батька ще не
    // вибрано).
    private bool   m_TrLink     = false;
    private string m_TrLinkFrom = "";

    // Перегляд гравця: демо-стан фракції (OZL_EdTree.DemoState).
    private int    m_TrDemo = 0;

    // Вузол, який тягнуть уздовж осі (тір), і полотно, яке тягнуть (прокрутка).
    // Миша опитується з OnUpdate, як у вікні гравця (OZL_TreeMenu.Drag): так
    // клік і перетягування не залежать від прапорця DRAGGABLE.
    private string m_TnDragId    = "";
    private bool   m_TnDragMoved = false;
    private int    m_TnDragX     = 0;
    private int    m_TnDragY     = 0;
    private float  m_TnCellX     = 0;
    private float  m_TnCellY     = 0;
    // Клік, що приходить разом із відпусканням після перетягування, -- не
    // вибір: кілька кадрів він ігнорується.
    private int    m_TnSkipClick = 0;
    private bool   m_TrPanDown   = false;
    private bool   m_TrPanMoved  = false;
    private int    m_TrPanX      = 0;
    private int    m_TrPanY      = 0;
    private float  m_TrPanH      = 0;
    private float  m_TrPanV      = 0;

    override void OnCreate(Widget RootW)
    {
        super.OnCreate(RootW);
        if (!M_SUB_WIDGET)
            return;

        m_ResOwners = new array<ref OZL_AdminOwner>();
        m_Ed        = new OZL_EdDocs();
        m_TrCells   = new array<Widget>();
        m_TrOrs     = new array<ref OZL_TreeOrMark>();
        m_TrOrLabels = new array<Widget>();
        m_TrFlows   = new array<Widget>();

        Widget pane = GetGame().GetWorkspace().CreateWidgets("OpenZone_Research_VPP/gui/layouts/oz_research_vpp_pane.layout", M_SUB_WIDGET);
        if (!pane)
        {
            OZL_Log.Error("research vpp pane: layout failed to load");
            return;
        }

        // The rail's pages of the module (design 5.5): one pane registered under
        // each page id; the shell shows it for any of them, OnPaneShown picks the
        // page inside it.
        array<string> keys = new array<string>();
        array<string> labels = new array<string>();
        RzPageList(keys, labels);
        for (int k = 0; k < keys.Count(); k++)
            RegisterPage("research", "#STR_OZL_VPP_MOD", RZ_PAGE + keys[k], labels[k], pane, "ResHint");

        // Власний слухач відповідей: список і операції -- наші, ядро про них
        // не знає; а ще він бачить відповіді cfg_set на наші файли.
        OZ_ClientState.AdminWatch().Insert(this.OnResearchResponse);

        ShowRzTab("overview");
    }

    // The rail's pages in their order, with their captions (the in-game page names).
    protected void RzPageList(array<string> keys, array<string> labels)
    {
        keys.Clear();
        labels.Clear();
        keys.Insert("overview");
        labels.Insert("#STR_OZL_VPP_PAGE_OVERVIEW");
        keys.Insert("tree");
        labels.Insert("#STR_OZL_VPP_PAGE_TREE");
        keys.Insert("chains");
        labels.Insert("#STR_OZL_VPP_PAGE_CHAINS");
        keys.Insert("points");
        labels.Insert("#STR_OZL_VPP_PAGE_POINTS");
        keys.Insert("owners");
        labels.Insert("#STR_OZL_VPP_PAGE_OWNERS");
        keys.Insert("modules");
        labels.Insert("#STR_OZL_VPP_PAGE_MODULES");
        keys.Insert("statics");
        labels.Insert("#STR_OZL_VPP_PAGE_STATICS");
        keys.Insert("settings");
        labels.Insert("#STR_OZL_VPP_PAGE_SETTINGS");
    }

    protected bool IsRzPage(string id)
    {
        return id.IndexOf(RZ_PAGE) == 0;
    }

    // Is one of the module's pages on screen: answers that come while another page is
    // shown must not write into that page's hint line.
    protected bool RzShown()
    {
        return IsRzPage(CurrentPane());
    }

    // A line for the admin, written only while a research page is shown.
    protected void RzHint(string text)
    {
        if (RzShown())
            Hint(text);
    }

    void ~OZ_VppAdminMenu()
    {
        OZ_ClientState.AdminWatch().Remove(this.OnResearchResponse);
    }

    // The shell repaints the shown pane from the series palette to the window's metal
    // shortly after each event and answer (OZ_VppPaint). This pane is metal already --
    // its description takes the vpp* tokens, its script OZL_Metal -- and its tree
    // canvas holds the skins' own node cells, which must keep the colours the player
    // sees: a skin colour that happens to equal a series colour would turn to metal.
    // So the pane is repainted once, when it registers (the field frames and panel
    // borders the generator writes in the series colours), and never after.
    override void RepaintSoon()
    {
        if (IsRzPage(m_Shown))
            return;
        super.RepaintSoon();
    }

    // A page of the module was shown on the rail: the page inside the pane follows.
    override void OnPaneShown(string id)
    {
        super.OnPaneShown(id);
        if (!IsRzPage(id) || !m_Ed)
            return;

        // A repaint asked for on the page before (the click on the rail asks first)
        // would land on this pane: it is dropped (RepaintSoon above).
        GetGame().GetCallQueue(CALL_CATEGORY_GUI).Remove(this.RepaintShown);
        m_RepaintQueued = false;

        // Сім файлів -- у чергу ядра, раз на вікно: AskCfg шле по одному.
        if (!m_RzAsked)
        {
            m_RzAsked = true;
            array<string> tags = m_Ed.Tags();
            for (int i = 0; i < tags.Count(); i++)
                AskCfg(tags[i]);
        }

        string prefix = RZ_PAGE;
        int skip = prefix.Length();
        string key = id.Substring(skip, id.Length() - skip);
        if (key == "overview")
            AskResearchList();
        ShowRzTab(key);
    }

    protected void AskResearchList()
    {
        Ask(OZL_Const.SECTION, "list", "{}");
    }

    // An answer of the core's config section other than cfg_set; the later layers take
    // theirs (the settings page: `identity`).
    protected void OnRzConfigAnswer(string op, bool ok, string json, string error)
    {
    }

    // Рядок зі stringtable мода, перекладений мовою клієнта.
    protected string Tr(string key)
    {
        return Widget.TranslateString(key);
    }

    void OnResearchResponse(string section, string op, bool ok, string json, string error)
    {
        // Відповідь на ЗАСТОСУВАТИ: ядро вже сказало своє «applied» у рядок
        // підказки, а нам треба знати, ЯКИЙ файл, і слати наступний.
        if (section == OZ_AdminSect.CONFIG && op.IndexOf("cfg_set:") == 0)
        {
            string tag = op.Substring(8, op.Length() - 8);
            if (m_Ed && m_Ed.Owns(tag) && m_Ed.InFlight() == tag)
                OnRzApplied(tag, ok, error);
            return;
        }

        // The core's other config answers: the settings page takes `identity`.
        if (section == OZ_AdminSect.CONFIG)
        {
            OnRzConfigAnswer(op, ok, json, error);
            return;
        }

        if (section != OZL_Const.SECTION)
            return;

        if (!ok)
        {
            RzHint(op + ": " + Words(error));
            return;
        }

        OZL_AdminList l = new OZL_AdminList();
        string err;
        if (!JsonFileLoader<OZL_AdminList>.LoadData(json, l, err))
        {
            string unreadable = Tr("#STR_OZL_VPP_HINT_UNREADABLE");
            RzHint(unreadable + " (" + err + ")");
            return;
        }

        // Рядки знімаємо одразу: далі будуються рядки списку, а конверт
        // розібрав серіалізатор (шапка OZ_ConfigBase ядра).
        string statics = l.Statics;
        string counters = l.Counters;

        // Копія, яку збудував скрипт: те, що приїхало, живе лише до розбору.
        m_ResOwners.Clear();
        for (int i = 0; i < l.Owners.Count(); i++)
        {
            OZL_AdminOwner src = l.Owners[i];
            if (!src)
                continue;
            OZL_AdminOwner o = new OZL_AdminOwner();
            o.Id        = src.Id;
            o.Name      = src.Name;
            o.Pool      = src.Pool;
            o.Completed = src.Completed;
            o.Active    = src.Active;
            o.Known     = src.Known;
            m_ResOwners.Insert(o);
        }
        if (m_ResPicked >= m_ResOwners.Count())
            m_ResPicked = -1;

        m_ResRepaint = true;
        RepaintOwners();
        m_ResRepaint = false;
        PaintPicked();

        PaintCounters(counters);
        PaintStatics(statics);

        // Після «перечитати конфіги» файли на сервері, можливо, інші: чернетка
        // без правок бере їх, з правками -- рахує зміни від нових.
        if (op == "reload" && m_Ed)
        {
            array<string> tags = m_Ed.Tags();
            for (int t = 0; t < tags.Count(); t++)
                AskCfg(tags[t]);
        }

        string said;
        if (op == "list")
        {
            said = Tr("#STR_OZL_VPP_HINT_FACTIONS");
            RzHint(said + m_ResOwners.Count().ToString() + "; " + counters);
        }
        else
        {
            said = Tr("#STR_OZL_VPP_HINT_DONE");
            RzHint(op + ": " + said);
        }
    }

    // ================================================= огляд

    protected void RepaintOwners()
    {
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("ResOwners"));
        if (!lb)
            return;
        lb.ClearItems();
        string noState = Tr("#STR_OZL_VPP_OV_NO_STATE");
        for (int i = 0; i < m_ResOwners.Count(); i++)
        {
            OZL_AdminOwner o = m_ResOwners[i];
            string line = "";
            if (i == m_ResPicked)
                line = "> ";
            line += o.Id;
            if (o.Name != "" && o.Name != o.Id)
                line += "  -  " + o.Name;
            if (o.Known == 1)
            {
                line += "  |  " + o.Pool;
                line += "  |  " + o.Completed.ToString() + " / " + o.Active.ToString();
            }
            else
            {
                line += "  |  " + noState;
            }
            lb.AddItem(line, NULL, 0);
            if (o.Known != 1)
                lb.SetItemColor(lb.GetNumItems() - 1, 0, OZL_Metal.MUTED);
            if (i == m_ResPicked)
                lb.SelectRow(i);
        }
        string entries = Tr("#STR_OZL_VPP_OV_FAC_COUNT");
        SetLabel("RzOvFacCount", entries + m_ResOwners.Count().ToString(), 0);
    }

    // The picked faction: its id and name, and its pool on the line under them.
    protected void PaintPicked()
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("ResPicked"));
        TextWidget pool = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzOvPool"));
        OZL_AdminOwner o = null;
        if (m_ResPicked >= 0 && m_ResPicked < m_ResOwners.Count())
            o = m_ResOwners[m_ResPicked];
        if (!o)
        {
            if (t)
                t.SetText("#STR_OZL_ED_OV_PICK");
            if (pool)
                pool.SetText("");
            return;
        }

        string who = o.Id;
        if (o.Name != "" && o.Name != o.Id)
            who = o.Id + " - " + o.Name;
        if (t)
            t.SetText(who);
        if (!pool)
            return;
        if (o.Known != 1)
        {
            pool.SetText(Tr("#STR_OZL_VPP_OV_NO_STATE"));
            return;
        }
        string poolWord = Tr("#STR_OZL_VPP_OV_POOL");
        string doneWord = Tr("#STR_OZL_VPP_OV_DONE");
        string runWord = Tr("#STR_OZL_VPP_OV_RUNNING");
        string line = poolWord + o.Pool + "  |  " + doneWord + o.Completed.ToString();
        line += "  |  " + runWord + o.Active.ToString();
        pool.SetText(line);
    }

    protected string PickedOwner()
    {
        if (m_ResPicked < 0 || m_ResPicked >= m_ResOwners.Count())
            return "";
        return m_ResOwners[m_ResPicked].Id;
    }

    // The confirm strip's words for a reset: whose pool and nodes go.
    protected string ResetAsk(string owner)
    {
        string who = owner;
        if (m_ResPicked >= 0 && m_ResPicked < m_ResOwners.Count())
        {
            OZL_AdminOwner o = m_ResOwners[m_ResPicked];
            if (o && o.Id == owner && o.Name != "" && o.Name != owner)
                who = owner + " - " + o.Name;
        }
        string ask = Tr("#STR_OZL_VPP_ASK_RESET");
        string tail = Tr("#STR_OZL_VPP_ASK_RESET2");
        return ask + who + tail;
    }

    // The server's counters from the list answer ("owners=7 pointTypes=7 ... problems=0"):
    // what the server reads now, one cell each.
    protected void PaintCounters(string counters)
    {
        array<string> keys = {"pointTypes", "owners", "rules", "nodes", "modules", "statics", "problems"};
        array<string> parts = new array<string>();
        counters.Split(" ", parts);
        for (int k = 0; k < keys.Count(); k++)
        {
            string value = "-";
            for (int p = 0; p < parts.Count(); p++)
            {
                string kv = parts[p];
                int eq = kv.IndexOf("=");
                if (eq <= 0)
                    continue;
                if (kv.Substring(0, eq) == keys[k])
                    value = kv.Substring(eq + 1, kv.Length() - eq - 1);
            }
            int color = OZL_Metal.TEXT;
            if (keys[k] == "problems" && value != "-")
            {
                color = OZL_Metal.OK;
                if (value.ToInt() > 0)
                    color = OZL_Metal.BAD;
            }
            SetLabel("RzOvV" + k.ToString(), value, color);
        }
    }

    // One entry of the static spawner's line: "id=Class[spawned]".
    protected bool StaticShaped(string token)
    {
        int eq = token.IndexOf("=");
        if (eq <= 0)
            return false;
        int br = token.IndexOf("[");
        if (br <= eq)
            return false;
        int n = token.Length();
        return token.Substring(n - 1, 1) == "]";
    }

    // The static spawner's line from the list answer, one row per entry, spawned or
    // waiting. A line of another shape (no entries, a broken state file) is shown as
    // it came. String values of a parsed answer stop at 1023 bytes (dayz-modding
    // persistence-networking), so a long list can end cut: its broken last entry
    // becomes "...", and the count says so.
    protected void PaintStatics(string statics)
    {
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzOvStList"));
        if (!lb)
            return;
        m_ResRepaint = true;
        lb.ClearItems();
        array<string> parts = new array<string>();
        statics.Split(" ", parts);
        bool shaped = false;
        if (parts.Count() > 0)
            shaped = StaticShaped(parts[0]);
        if (!shaped)
        {
            if (statics != "")
                lb.AddItem(statics, NULL, 0);
            SetLabel("RzOvStCount", "", 0);
            m_ResRepaint = false;
            return;
        }

        string spawnedWord = Tr("#STR_OZL_VPP_OV_ST_SPAWNED");
        string pendingWord = Tr("#STR_OZL_VPP_OV_ST_PENDING");
        int total = 0;
        int spawned = 0;
        bool cut = false;
        for (int i = 0; i < parts.Count(); i++)
        {
            string token = parts[i];
            if (!StaticShaped(token))
            {
                cut = true;
                lb.AddItem("...", NULL, 0);
                break;
            }
            int eq = token.IndexOf("=");
            int br = token.IndexOf("[");
            string id = token.Substring(0, eq);
            string flag = token.Substring(br + 1, token.Length() - br - 2);
            total++;
            string word = pendingWord;
            int color = OZL_Metal.ALERT;
            if (flag == "spawned")
            {
                spawned++;
                word = spawnedWord;
                color = OZL_Metal.OK;
            }
            lb.AddItem(id + "   " + word, NULL, 0);
            lb.SetItemColor(lb.GetNumItems() - 1, 0, color);
        }
        m_ResRepaint = false;

        string placed = Tr("#STR_OZL_VPP_OV_ST_PLACED");
        string ofWord = Tr("#STR_OZL_VPP_OV_ST_OF");
        string countText = placed + spawned.ToString() + ofWord + total.ToString();
        if (cut)
            countText += "+";
        int countColor = OZL_Metal.OK;
        if (spawned < total || cut)
            countColor = OZL_Metal.ALERT;
        SetLabel("RzOvStCount", countText, countColor);
    }

    // ================================================= редактор: оболонка

    // A page of the module shown: its head, its page, the draft bar. The problems
    // panel stays open from page to page -- it is about the whole draft.
    protected void ShowRzTab(string key)
    {
        m_RzTab = key;
        m_TrLink = false;
        m_TrLinkFrom = "";
        if (m_Ed)
            m_Ed.EndGesture();
        RzLayHead();
        RepaintRz();
    }

    // The page inside the pane that shows a rail page: OWNERS, MODULES and STATICS
    // share one (cfg); every other page has its own.
    protected string RzPageOf(string key)
    {
        if (key == "owners" || key == "modules" || key == "statics")
            return "cfg";
        return key;
    }

    // Fills the open page. The later layers (chains, the config files, settings)
    // take their keys and hand the rest to super.
    protected void RepaintRzPage(string tab)
    {
        if (tab == "points")
            RepaintPoints(true);
        else if (tab == "tree")
            RepaintTree(true);
    }

    // The open page of the pane; the rail marks which one it is (the row of sub-tabs
    // that did it here went with the rework, design 5.5).
    protected void ShowRzPage(string page)
    {
        array<string> pages = {"overview", "points", "tree", "chains", "cfg", "settings"};
        for (int i = 0; i < pages.Count(); i++)
        {
            Widget p = M_SUB_WIDGET.FindAnyWidget("RzPage_" + pages[i]);
            if (p)
                p.Show(pages[i] == page);
        }
    }

    // Усе, що залежить від чернетки: сторінка, смуга дій, підсумок, проблеми.
    protected void RepaintRz()
    {
        if (!M_SUB_WIDGET || !m_Ed)
            return;

        ShowRzPage(RzPageOf(m_RzTab));
        RepaintRzPage(m_RzTab);
        PaintRzBar();
        PaintSummary();
        RepaintProblems();
    }

    // ------------------------------------------------- дрібне для віджетів

    protected void SetBtnText(string btn, string text, int color)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(btn + "Text"));
        if (!t)
            return;
        t.SetText(text);
        t.SetColor(color);
    }

    // A generated button's caption, ground and border (Text, Bg, Edge); a colour of 0
    // leaves that part as it is.
    protected void PaintBtn(string btn, string text, int textColor, int bgColor, int edgeColor)
    {
        SetBtnText(btn, text, textColor);
        Widget bg = M_SUB_WIDGET.FindAnyWidget(btn + "Bg");
        if (bg && bgColor != 0)
            bg.SetColor(bgColor);
        Widget edge = M_SUB_WIDGET.FindAnyWidget(btn + "Edge");
        if (edge && edgeColor != 0)
            edge.SetColor(edgeColor);
    }

    // One button of a pair that says which of two values is in force: lit when on.
    protected void PaintToggle(string btn, bool on)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(btn + "Text"));
        Widget edge = M_SUB_WIDGET.FindAnyWidget(btn + "Edge");
        int ink = OZL_Metal.MUTED;
        int rim = OZL_Metal.EDGE;
        if (on)
        {
            ink = OZL_Metal.ACCENT;
            rim = OZL_Metal.ACCENT;
        }
        if (t)
            t.SetColor(ink);
        if (edge)
            edge.SetColor(rim);
    }

    // A label's text, and its colour unless the colour is 0.
    protected void SetLabel(string name, string text, int color)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(name));
        if (!t)
            return;
        t.SetText(text);
        if (color != 0)
            t.SetColor(color);
    }

    protected void SetColorOf(string name, int color)
    {
        Widget w = M_SUB_WIDGET.FindAnyWidget(name);
        if (w)
            w.SetColor(color);
    }

    protected void ShowW(string name, bool show)
    {
        Widget w = M_SUB_WIDGET.FindAnyWidget(name);
        if (w)
            w.Show(show);
    }

    // Size and place in pixels (SetPos and SetSize of an exact-size widget take pixels,
    // dayz-modding gui-layouts §24).
    protected void SizeW(string name, float w, float h)
    {
        Widget x = M_SUB_WIDGET.FindAnyWidget(name);
        if (x)
            x.SetSize(w, h);
    }

    protected void MoveW(string name, float x, float y)
    {
        Widget m = M_SUB_WIDGET.FindAnyWidget(name);
        if (m)
            m.SetPos(x, y);
    }

    protected void PlaceW(string name, float x, float y, float w, float h)
    {
        Widget p = M_SUB_WIDGET.FindAnyWidget(name);
        if (!p)
            return;
        p.SetPos(x, y);
        p.SetSize(w, h);
    }

    // ------------------------------------------------- смуга чернетки

    protected void PaintRzBar()
    {
        int changed = m_Ed.Changed();
        string state;
        int stateColor = OZL_Metal.MUTED;
        if (!m_Ed.AllLoaded())
        {
            state = Tr("#STR_OZL_ED_STATUS_LOADING") + m_Ed.LoadedCount().ToString() + "/" + m_Ed.Tags().Count().ToString();
        }
        else if (changed > 0)
        {
            state = Tr("#STR_OZL_ED_STATUS_CHANGED") + changed.ToString();
            stateColor = OZL_Metal.ALERT;
        }
        else
        {
            state = Tr("#STR_OZL_ED_STATUS_CLEAN");
        }
        SetLabel("RzStatus", state, stateColor);
        SetColorOf("RzStatusDot", stateColor);

        int errs = m_Ed.Errors();
        int warns = m_Ed.Warnings();
        string probs;
        int probInk = OZL_Metal.OK;
        int probRim = OZL_Metal.EDGE;
        if (errs > 0)
        {
            probs = Tr("#STR_OZL_ED_PROB_ERRORS") + errs.ToString();
            if (warns > 0)
                probs += " +" + warns.ToString();
            probInk = OZL_Metal.BAD;
            probRim = OZL_Metal.BAD;
        }
        else if (warns > 0)
        {
            probs = Tr("#STR_OZL_ED_PROB_WARNINGS") + warns.ToString();
            probInk = OZL_Metal.ALERT;
        }
        else
        {
            probs = Tr("#STR_OZL_ED_PROB_NONE");
        }
        if (m_RzProblems)
            probRim = probInk;
        PaintBtn("BtnRzProblems", probs, probInk, OZL_Metal.RAISED, probRim);

        int undoInk = OZL_Metal.FAINT;
        if (m_Ed.CanUndo())
            undoInk = OZL_Metal.TEXT;
        SetBtnText("BtnRzUndo", Tr("#STR_OZL_ED_BTN_UNDO"), undoInk);

        int redoInk = OZL_Metal.FAINT;
        if (m_Ed.CanRedo())
            redoInk = OZL_Metal.TEXT;
        SetBtnText("BtnRzRedo", Tr("#STR_OZL_ED_BTN_REDO"), redoInk);

        int discardInk = OZL_Metal.FAINT;
        int discardRim = OZL_Metal.EDGE;
        if (changed > 0)
        {
            discardInk = OZL_Metal.BAD;
            discardRim = OZL_Metal.BAD;
        }
        PaintBtn("BtnRzDiscard", Tr("#STR_OZL_ED_BTN_DISCARD"), discardInk, OZL_Metal.RAISED, discardRim);

        // APPLY is the one lit button: accent while there is something to send and
        // nothing stops it, red while errors keep it shut, plain with nothing to do.
        string apply = Tr("#STR_OZL_ED_BTN_APPLY");
        int applyInk = OZL_Metal.FAINT;
        int applyGround = OZL_Metal.RAISED;
        int applyRim = OZL_Metal.EDGE;
        if (changed > 0)
        {
            apply += " - " + changed.ToString();
            if (errs == 0)
            {
                applyInk = OZL_Metal.SCREEN;
                applyGround = OZL_Metal.ACCENT;
                applyRim = OZL_Metal.ACCENT;
            }
            else
            {
                applyInk = OZL_Metal.BAD;
                applyRim = OZL_Metal.BAD;
            }
        }
        PaintBtn("BtnRzApply", apply, applyInk, applyGround, applyRim);
    }

    // Підсумок для ОГЛЯДУ: що тримає чернетка (сервер -- у клітинках над ним).
    protected void PaintSummary()
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzSummary"));
        if (!t)
            return;
        if (!m_Ed.AllLoaded())
        {
            t.SetText(Tr("#STR_OZL_ED_STATUS_LOADING") + m_Ed.LoadedCount().ToString() + "/" + m_Ed.Tags().Count().ToString());
            return;
        }

        OZL_PointTypes pt = OZL_PointTypes.Cast(m_Ed.Doc(OZL_Config.TAG_POINT_TYPES).Obj);
        OZL_Owners     ow = OZL_Owners.Cast(m_Ed.Doc(OZL_Config.TAG_OWNERS).Obj);
        OZL_Rules      ru = OZL_Rules.Cast(m_Ed.Doc(OZL_Config.TAG_RULES).Obj);
        OZL_TreeConfig tr = OZL_TreeConfig.Cast(m_Ed.Doc(OZL_Config.TAG_TREE).Obj);
        OZL_Modules    mo = OZL_Modules.Cast(m_Ed.Doc(OZL_Config.TAG_MODULES).Obj);
        OZL_StaticsConfig sc = OZL_StaticsConfig.Cast(m_Ed.Doc(OZL_Config.TAG_STATICS).Obj);

        string s = Tr("#STR_OZL_VPP_OV_DRAFT_SUM");
        s += pt.PointTypes.Count().ToString() + " / " + ow.Owners.Count().ToString();
        s += " / " + ru.Count().ToString() + " / " + tr.NodeCount().ToString();
        s += " / " + mo.Modules.Count().ToString() + " / " + sc.Entries.Count().ToString();
        t.SetText(s);
    }

    // ------------------------------------------------- панель проблем

    // The problems of the draft, errors first (they keep APPLY shut), in a panel
    // above the draft bar while it is open.
    protected void RepaintProblems()
    {
        if (!m_RzProblems)
            return;
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzProbList"));
        if (!lb)
            return;
        m_ResRepaint = true;
        lb.ClearItems();

        array<string> probs = m_Ed.Problems();
        if (probs.Count() == 0)
        {
            lb.AddItem(Tr("#STR_OZL_ED_PROB_CLEAN"), NULL, 0);
            lb.SetItemColor(0, 0, OZL_Metal.OK);
            m_ResRepaint = false;
            return;
        }

        string markE = Tr("#STR_OZL_ED_PROB_MARK_ERROR");
        string markW = Tr("#STR_OZL_ED_PROB_MARK_WARN");
        int i;
        for (i = 0; i < probs.Count(); i++)
        {
            if (!OZL_EdCodec.IsError(probs[i]))
                continue;
            lb.AddItem(markE + probs[i], NULL, 0);
            lb.SetItemColor(lb.GetNumItems() - 1, 0, OZL_Metal.BAD);
        }
        for (i = 0; i < probs.Count(); i++)
        {
            if (OZL_EdCodec.IsError(probs[i]))
                continue;
            lb.AddItem(markW + probs[i], NULL, 0);
            lb.SetItemColor(lb.GetNumItems() - 1, 0, OZL_Metal.ALERT);
        }
        m_ResRepaint = false;
    }

    // The problems button and the panel's own close: the panel opens or closes, and
    // the pages above it get their height back or give it.
    protected void RzShowProblems(bool open)
    {
        m_RzProblems = open;
        RzLayout();
        RepaintProblems();
        PaintRzBar();
    }

    // ------------------------------------------------- голова сторінки

    // The shown page's title, its line and its actions; the title is clipped short of
    // the actions.
    protected void RzLayHead()
    {
        if (!M_SUB_WIDGET)
            return;
        string up = m_RzTab;
        up.ToUpper();
        string title = Tr("#STR_OZL_VPP_H_" + up);
        string sub = Tr("#STR_OZL_VPP_HS_" + up);
        SetLabel("RzHeadTitle", title, 0);
        SetLabel("RzHeadSub", sub, 0);

        string act = "";
        if (m_RzTab == "overview")
            act = "#STR_OZL_ED_OV_REFRESH";
        else if (m_RzTab == "points")
            act = "#STR_OZL_VPP_PT_ADD";
        else if (m_RzTab == "owners")
            act = "#STR_OZL_VPP_OW_ADD";
        else if (m_RzTab == "modules")
            act = "#STR_OZL_VPP_MO_ADD";
        else if (m_RzTab == "statics")
            act = "#STR_OZL_VPP_ST_ADD";
        bool hasAct = (act != "");
        ShowW("BtnRzHdAct", hasAct);
        if (hasAct)
            SetBtnText("BtnRzHdAct", Tr(act), OZL_Metal.TEXT);

        bool tree = (m_RzTab == "tree");
        array<string> treeActs = {"RzTrDemoLbl", "BtnRzTrDemoPrev", "BtnRzTrDemo", "BtnRzTrDemoNext", "BtnRzTrView"};
        for (int i = 0; i < treeActs.Count(); i++)
            ShowW(treeActs[i], tree);

        if (m_RzW <= 0)
            return;
        float s = Px();
        float acts = 0;
        if (hasAct)
            acts = (220 + 16) * s;
        if (tree)
            acts = (594 + 16) * s;
        float clipW = m_RzW - 48 * s - acts;
        if (clipW < 100 * s)
            clipW = 100 * s;
        SizeW("RzHead", m_RzW, 60 * s);
        SizeW("RzHeadClip", clipW, 59 * s);
        SizeW("RzHeadRule", m_RzW, s);
    }

    // ------------------------------------------------- розкладка

    // The pane laid out in the content area the shell gave it (m_RzW x m_RzH): the
    // head, the pages between it and the draft bar -- shorter while the problems panel
    // is open over the bar --, the panel and the bar; then the pages themselves
    // (RzLayPages, which the later layers extend). Nothing is read back.
    protected void RzLayout()
    {
        if (!M_SUB_WIDGET || m_RzW <= 0 || m_RzH <= 0)
            return;
        float s = Px();
        float w = m_RzW;
        float h = m_RzH;
        float barH = 56 * s;
        float probH = 150 * s;
        float top = 72 * s;
        float bottom = h - barH - 12 * s;
        if (m_RzProblems)
            bottom = bottom - probH;
        float pw = w - 48 * s;
        float ph = bottom - top;
        if (ph < 120 * s)
            ph = 120 * s;
        m_RzPageW = pw;
        m_RzPageH = ph;

        RzLayHead();

        SizeW("RzPages", pw, ph);
        array<string> pages = {"overview", "points", "tree", "chains", "cfg", "settings"};
        for (int i = 0; i < pages.Count(); i++)
            SizeW("RzPage_" + pages[i], pw, ph);

        PlaceW("RzProbs", 0, h - barH - probH, w, probH);
        ShowW("RzProbs", m_RzProblems);
        SizeW("RzProbLine", w, s);
        SizeW("RzProbList", w - 48 * s, 102 * s);
        float subW = w - (270 + 64 + 300 + 12) * s;
        if (subW < 0)
            subW = 0;
        SizeW("RzProbSub", subW, 20 * s);

        PlaceW("RzBar", 0, h - barH, w, barH);
        SizeW("RzBarLine", w, s);
        float hintW = w - (338 + 500) * s;
        if (hintW < 0)
            hintW = 0;
        SizeW("ResHint", hintW, 32 * s);

        RzLayPages(pw, ph);
    }

    // Each page in the page area pw x ph (pixels). This layer: overview, point types
    // and the tree; the later layers add theirs after super.
    protected void RzLayPages(float pw, float ph)
    {
        float s = Px();
        float gap = 16 * s;

        // Overview: the factions take what the two fixed columns leave.
        float colW = 290 * s;
        float leftW = pw - 2 * colW - 2 * gap;
        if (leftW < 300 * s)
            leftW = 300 * s;
        SizeW("RzOvLeft", leftW, ph);
        SizeW("RzOvFacCols", leftW, 16 * s);
        SizeW("RzOvFacCount", leftW - 136 * s, 18 * s);
        float ownersH = ph - (48 + 46) * s;
        if (ownersH < 40 * s)
            ownersH = 40 * s;
        SizeW("ResOwners", leftW, ownersH);
        SizeW("RzOvFacNote", leftW, 40 * s);
        PlaceW("RzOvMid", leftW + gap, 0, colW, ph);
        PlaceW("RzOvRight", leftW + colW + 2 * gap, 0, colW, ph);
        float staticsH = ph - 294 * s;
        if (staticsH < 40 * s)
            staticsH = 40 * s;
        SizeW("RzOvStList", colW, staticsH);

        // Point types: the list takes what the form leaves.
        float formW = 616 * s;
        float listW = pw - formW - gap;
        if (listW < 220 * s)
            listW = 220 * s;
        SizeW("RzPtLeft", listW, ph);
        SizeW("RzPtHead", listW, 16 * s);
        float typesH = ph - (20 + 24) * s;
        if (typesH < 40 * s)
            typesH = 40 * s;
        SizeW("RzPtList", listW, typesH);
        SizeW("RzPtCount", listW, 18 * s);
        PlaceW("RzPtForm", listW + gap, 0, formW, ph);

        RzLayTree(pw, ph);
    }

    // Файл чернетки приїхав із сервера (cfg_get ядра).
    override void OnCfgText(string name, string body)
    {
        super.OnCfgText(name, body);
        if (!m_Ed || !m_Ed.Owns(name))
            return;

        string err;
        if (!m_Ed.OnFetched(name, body, err))
            RzHint(Tr("#STR_OZL_ED_HINT_BAD_FILE") + name + " (" + err + ")");
        RepaintRz();
    }

    // ------------------------------------------------- дії чернетки

    protected void RzUndo(bool redo)
    {
        string tag;
        bool done;
        if (redo)
            done = m_Ed.Redo(tag);
        else
            done = m_Ed.Undo(tag);

        if (!done)
        {
            if (redo)
                Hint(Tr("#STR_OZL_ED_HINT_REDO_EMPTY"));
            else
                Hint(Tr("#STR_OZL_ED_HINT_UNDO_EMPTY"));
            return;
        }

        ClampPicked();
        RepaintRz();
        if (redo)
            Hint(Tr("#STR_OZL_ED_HINT_REDONE") + tag);
        else
            Hint(Tr("#STR_OZL_ED_HINT_UNDONE") + tag);
    }

    // ВІДКИНУТИ питає рядком підтвердження вікна (дизайн вікна §3.4) і каже,
    // які файли пропадуть; «так» приходить у OnConfirmed -> RzDiscardNow.
    protected void RzDiscard()
    {
        if (m_Ed.Changed() == 0)
        {
            Hint(Tr("#STR_OZL_ED_HINT_NOTHING"));
            return;
        }
        string ask = Tr("#STR_OZL_VPP_ASK_DISCARD");
        string files = RzChangedFiles();
        Confirm(ask + files, "#STR_OZL_VPP_YES_DISCARD", "rz:discard");
    }

    // "2 (Settings, Tree)": how many files the draft changed, and which.
    protected string RzChangedFiles()
    {
        array<string> tags = m_Ed.Tags();
        string names = "";
        int n = 0;
        for (int i = 0; i < tags.Count(); i++)
        {
            OZL_EdDoc d = m_Ed.Doc(tags[i]);
            if (!d || !d.Dirty())
                continue;
            string shortName = tags[i];
            if (shortName.IndexOf("Research") == 0)
                shortName = shortName.Substring(8, shortName.Length() - 8);
            if (names != "")
                names += ", ";
            names += shortName;
            n++;
        }
        return n.ToString() + " (" + names + ")";
    }

    protected void RzDiscardNow()
    {
        if (m_Ed.Changed() == 0)
            return;
        m_Ed.Discard();
        ClampPicked();
        RepaintRz();
        Hint(Tr("#STR_OZL_ED_HINT_DISCARDED"));
    }

    // The confirm strip's "yes" (design 3.4). Research's actions start with "rz:";
    // the later layers take theirs (rz:rudel:, rz:cfgdel:) before they call super.
    override void OnConfirmed(string action)
    {
        if (action.IndexOf("rz:") != 0)
        {
            super.OnConfirmed(action);
            return;
        }
        if (action == "rz:discard")
        {
            RzDiscardNow();
            return;
        }
        if (action == "rz:reload")
        {
            Ask(OZL_Const.SECTION, "reload", "{}");
            Hint(Tr("#STR_OZL_VPP_RELOADING"));
            return;
        }
        if (action.IndexOf("rz:reset:") == 0)
        {
            string owner = action.Substring(9, action.Length() - 9);
            Ask(OZL_Const.SECTION, "reset:" + owner, "{}");
            Hint(Tr("#STR_OZL_VPP_RESETTING") + owner);
            return;
        }
        if (action.IndexOf("rz:ptdel:") == 0)
        {
            PtDeleteNow(action.Substring(9, action.Length() - 9));
            return;
        }
        if (action.IndexOf("rz:tndel:") == 0)
        {
            TnDeleteNow(action.Substring(9, action.Length() - 9));
            return;
        }
        if (action.IndexOf("rz:brdel:") == 0)
        {
            BrDeleteNow(action.Substring(9, action.Length() - 9));
            return;
        }
        super.OnConfirmed(action);
    }

    // ЗАСТОСУВАТИ: змінені файли по одному, у порядку OZL_EdDocs; помилки
    // чернетки не пускають -- сервер викинув би те, що на них стоїть.
    protected void RzApply()
    {
        if (!m_Ed.AllLoaded())
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }
        if (m_Ed.Applying())
        {
            Hint(Tr("#STR_OZL_ED_HINT_BUSY"));
            return;
        }
        if (m_Ed.Changed() == 0)
        {
            Hint(Tr("#STR_OZL_ED_HINT_NOTHING"));
            return;
        }
        if (m_Ed.Errors() > 0)
        {
            Hint(Tr("#STR_OZL_ED_HINT_FIX_FIRST"));
            return;
        }

        m_Ed.EndGesture();
        m_Ed.ApplyStart();
        SendNextRz();
    }

    protected void SendNextRz()
    {
        string tag = m_Ed.ApplyNext();
        if (tag == "")
            return;
        SendCfg(tag, m_Ed.Doc(tag).Cur);
        RzHint(Tr("#STR_OZL_ED_HINT_APPLYING") + tag);
    }

    protected void OnRzApplied(string tag, bool ok, string error)
    {
        m_Ed.ApplyDone(tag, ok);
        if (!ok)
        {
            RzHint(tag + Tr("#STR_OZL_ED_HINT_REFUSED") + " (" + Words(error) + ")");
            RepaintRz();
            return;
        }

        SendNextRz();
        if (m_Ed.Applying())
        {
            RepaintRz();
            return;
        }

        // Усе пройшло. Сервер переписав файли з розібраного (Validate, бекап),
        // тож показуємо вже його текст: перечитуємо застосоване.
        array<string> done = m_Ed.Applied();
        RzHint(Tr("#STR_OZL_ED_HINT_APPLIED") + done.Count().ToString());
        m_Ed.ClearHistory();
        for (int i = 0; i < done.Count(); i++)
            AskCfg(done[i]);
        RepaintRz();
    }

    // ================================================= типи балів

    protected OZL_PointTypes DraftPointTypes()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_POINT_TYPES);
        if (!d || !d.Loaded)
            return null;
        return OZL_PointTypes.Cast(d.Obj);
    }

    protected void ClampPicked()
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts || m_PtPicked >= pts.PointTypes.Count())
            m_PtPicked = -1;
    }

    // Список і, коли fillForm, поля вибраного. Під час набору поле не
    // переписується -- інакше курсор стрибав би в кінець на кожну літеру.
    protected void RepaintPoints(bool fillForm)
    {
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzPtList"));
        if (!lb)
            return;

        OZL_PointTypes pts = DraftPointTypes();
        m_ResRepaint = true;
        lb.ClearItems();
        if (pts)
        {
            // Маркер "> " -- вибраний рядок: список у стилі NoScrollBar
            // підсвічування рядка не малює (зміряно 2026-11-09), а червона смуга
            // прокрутки стилю за замовчуванням була гірша за маркер.
            for (int i = 0; i < pts.PointTypes.Count(); i++)
            {
                OZL_PointType p = pts.PointTypes[i];
                string line = "";
                if (i == m_PtPicked)
                    line = "> ";
                line += p.Id + "  -  " + p.Name;
                line += "  -  " + p.SortOrder.ToString() + "  -  " + p.BasePurity.ToString();
                lb.AddItem(line, NULL, 0);
            }
            if (m_PtPicked >= 0 && m_PtPicked < pts.PointTypes.Count())
                lb.SelectRow(m_PtPicked);
            string inDraft = Tr("#STR_OZL_VPP_PT_COUNT");
            SetLabel("RzPtCount", inDraft + pts.PointTypes.Count().ToString(), 0);
        }
        m_ResRepaint = false;

        PaintPtHead();
        if (fillForm)
            FillPtForm();
    }

    protected OZL_PointType PickedPointType()
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (pts && m_PtPicked >= 0 && m_PtPicked < pts.PointTypes.Count())
            return pts.PointTypes[m_PtPicked];
        return null;
    }

    // The form's head: the picked type's id, its name and its own colour -- painted on
    // every keystroke, the fields only when a row is picked.
    protected void PaintPtHead()
    {
        OZL_PointType p = PickedPointType();
        Widget swatch = M_SUB_WIDGET.FindAnyWidget("RzPtSwatch");
        if (!p)
        {
            SetLabel("RzPtPicked", "#STR_OZL_ED_PT_PICK", 0);
            SetLabel("RzPtPickedName", "", 0);
            if (swatch)
                swatch.Show(false);
            return;
        }
        SetLabel("RzPtPicked", p.Id, 0);
        SetLabel("RzPtPickedName", p.Name, 0);
        if (swatch)
        {
            swatch.SetColor(OZL_PointTypes.ColorArgb(p.Color));
            swatch.Show(true);
        }
    }

    protected void FillPtForm()
    {
        OZL_PointType p = PickedPointType();

        m_RzFill = true;
        if (p)
        {
            SetEdit("RzPtId", p.Id);
            SetEdit("RzPtName", p.Name);
            SetEdit("RzPtColor", ColorShown(p.Color));
            SetEdit("RzPtSort", p.SortOrder.ToString());
            SetEdit("RzPtPurity", p.BasePurity.ToString());
            SetEdit("RzPtIcon", p.Icon);
        }
        else
        {
            SetEdit("RzPtId", "");
            SetEdit("RzPtName", "");
            SetEdit("RzPtColor", "");
            SetEdit("RzPtSort", "");
            SetEdit("RzPtPurity", "");
            SetEdit("RzPtIcon", "");
        }
        m_RzFill = false;
    }

    // КОЛІР БЕЗ "#" У ПОЛІ. Текст на "#" рушій читає як ключ stringtable:
    // SetText("#7CB342") показав "7CB342" (зміряно 2026-11-09), і поле, яке
    // потім правили, повертало колір без решітки. Тож поле показує шість
    // цифр, а у файл іде "#RRGGBB" -- як писав колір пакет і як читає
    // OZL_PointTypes.ColorArgb.
    protected string ColorShown(string stored)
    {
        string c = stored.Trim();
        if (c.IndexOf("#") == 0)
            c = c.Substring(1, c.Length() - 1);
        return c;
    }

    protected string ColorStored(string typed)
    {
        string c = typed.Trim();
        if (c == "" || c.IndexOf("#") == 0)
            return c;
        return "#" + c;
    }

    // Поле форми змінилось: правка вибраного типу, один знімок на поле.
    protected void OnPtField(string field)
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts || m_PtPicked < 0 || m_PtPicked >= pts.PointTypes.Count())
            return;

        string tag = OZL_Config.TAG_POINT_TYPES;
        m_Ed.BeginOnce(tag, "pt:" + m_PtPicked.ToString() + ":" + field);

        OZL_PointType p = pts.PointTypes[m_PtPicked];
        string v = GetEdit(field);
        if (field == "RzPtId")
            p.Id = v.Trim();
        else if (field == "RzPtName")
            p.Name = v;
        else if (field == "RzPtColor")
            p.Color = ColorStored(v);
        else if (field == "RzPtSort")
            p.SortOrder = v.ToInt();
        else if (field == "RzPtPurity")
            p.BasePurity = v.ToFloat();
        else if (field == "RzPtIcon")
            p.Icon = v.Trim();

        m_Ed.Commit(tag);
        RepaintPoints(false);
        PaintRzBar();
        PaintSummary();
    }

    protected void PtAdd()
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts)
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }

        string tag = OZL_Config.TAG_POINT_TYPES;
        m_Ed.BeginOnce(tag, "");

        // Нова лінія з вільним Id і порядком у кінці: адмін перейменує.
        int order = 0;
        int i;
        for (i = 0; i < pts.PointTypes.Count(); i++)
        {
            if (pts.PointTypes[i].SortOrder > order)
                order = pts.PointTypes[i].SortOrder;
        }
        string id = "new_line";
        int n = 1;
        while (pts.Find(id))
        {
            n++;
            id = "new_line_" + n.ToString();
        }

        OZL_PointType p = new OZL_PointType();
        p.Id = id;
        p.Name = id;
        p.Color = "#FFFFFF";
        p.SortOrder = order + 1;
        p.BasePurity = OZL_Const.DEFAULT_PURITY;
        pts.PointTypes.Insert(p);

        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        m_PtPicked = pts.PointTypes.Count() - 1;
        RepaintPoints(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_PT_ADDED") + id);
    }

    protected void PtDelete()
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts || m_PtPicked < 0 || m_PtPicked >= pts.PointTypes.Count())
        {
            Hint(Tr("#STR_OZL_ED_PT_PICK"));
            return;
        }

        string id = pts.PointTypes[m_PtPicked].Id;
        string ask = Tr("#STR_OZL_VPP_ASK_DEL_PT");
        string tail = Tr("#STR_OZL_VPP_ASK_DRAFT");
        Confirm(ask + id + "? " + tail, "#STR_OZL_VPP_YES_DELETE", "rz:ptdel:" + id);
    }

    // The strip's "yes": the type is found again by its id -- the picked row may
    // have moved while the strip was open.
    protected void PtDeleteNow(string id)
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts)
            return;
        int at = -1;
        int i;
        for (i = 0; i < pts.PointTypes.Count(); i++)
        {
            if (at < 0 && pts.PointTypes[i] && pts.PointTypes[i].Id == id)
                at = i;
        }
        OZL_PointType picked = null;
        if (m_PtPicked >= 0 && m_PtPicked < pts.PointTypes.Count())
            picked = pts.PointTypes[m_PtPicked];
        if (picked && picked.Id == id)
            at = m_PtPicked;
        if (at < 0)
        {
            Hint(Tr("#STR_OZL_VPP_GONE") + id);
            return;
        }

        string tag = OZL_Config.TAG_POINT_TYPES;
        m_Ed.BeginOnce(tag, "");
        pts.PointTypes.RemoveOrdered(at);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        if (at < m_PtPicked)
            m_PtPicked--;
        if (m_PtPicked >= pts.PointTypes.Count())
            m_PtPicked = pts.PointTypes.Count() - 1;
        RepaintPoints(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_PT_DELETED") + id);
    }

    // ================================================= дерево

    protected OZL_TreeConfig DraftTree()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_TREE);
        if (!d || !d.Loaded)
            return null;
        return OZL_TreeConfig.Cast(d.Obj);
    }

    protected OZL_Owners DraftOwners()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_OWNERS);
        if (!d || !d.Loaded)
            return null;
        return OZL_Owners.Cast(d.Obj);
    }

    // Одиниця розмітки в пікселях: висота екрана на 1080 (SetPos і SetSize
    // беруть пікселі, dayz-modding gui-layouts §24).
    protected float Px()
    {
        int sw, sh;
        GetScreenSize(sw, sh);
        return sh / 1080.0;
    }

    protected OZL_TreeBranch TrBranch(OZL_TreeConfig tree)
    {
        if (!tree)
            return null;
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            if (tree.Branches[b] && tree.Branches[b].Id == m_TrBranch)
                return tree.Branches[b];
        }
        return null;
    }

    protected OZL_TreeNode TrNode(OZL_TreeConfig tree)
    {
        if (!tree || m_TrSel == "")
            return null;
        return tree.FindNode(m_TrSel);
    }

    // Гілки власника в порядку файла -- рядки списку гілок. Вибрана гілка,
    // якої власник уже не має (у полі власників набирають інший список),
    // лишається в кінці: інакше вибір стрибав би на іншу гілку посеред
    // набору.
    protected void TrBranchIds(OZL_TreeConfig tree, array<string> into)
    {
        into.Clear();
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            if (br && br.BelongsTo(m_TrOwner))
                into.Insert(br.Id);
        }
        if (m_TrBranch != "" && into.Find(m_TrBranch) < 0 && OZL_EdTree.FindBranch(tree, m_TrBranch))
            into.Insert(m_TrBranch);
    }

    // Списки ліворуч; вибір за замовчуванням -- перший власник і його перша
    // гілка.
    protected void RepaintTrLists(OZL_TreeConfig tree, OZL_Owners owners)
    {
        TextListboxWidget lo = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrOwners"));
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrBranches"));
        if (!lo || !lb)
            return;

        int i;
        bool ownerKnown = false;
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            if (owners.Owners[i] && owners.Owners[i].Id == m_TrOwner)
                ownerKnown = true;
        }
        if (!ownerKnown && owners.Owners.Count() > 0)
            m_TrOwner = owners.Owners[0].Id;

        array<string> ids = new array<string>();
        TrBranchIds(tree, ids);
        if (ids.Find(m_TrBranch) < 0)
        {
            m_TrBranch = "";
            if (ids.Count() > 0)
                m_TrBranch = ids[0];
            m_TrSel = "";
        }

        m_ResRepaint = true;
        lo.ClearItems();
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            OZL_OwnerDef o = owners.Owners[i];
            if (!o)
                continue;
            string ol = "";
            if (o.Id == m_TrOwner)
                ol = "> ";
            ol += o.Id + "  -  " + owners.SkinOf(o.Id);
            lo.AddItem(ol, NULL, 0);
        }

        lb.ClearItems();
        for (i = 0; i < ids.Count(); i++)
        {
            OZL_TreeBranch br = null;
            for (int b = 0; b < tree.Branches.Count(); b++)
            {
                if (tree.Branches[b] && tree.Branches[b].Id == ids[i])
                    br = tree.Branches[b];
            }
            if (!br)
                continue;
            string bl = "";
            if (br.Id == m_TrBranch)
                bl = "> ";
            string bn = br.Name;
            if (bn == "")
                bn = br.Id;
            bl += bn + "  (" + br.Nodes.Count().ToString() + ")";
            if (!br.BelongsTo(m_TrOwner))
                bl += Tr("#STR_OZL_ED_BR_OTHER");
            lb.AddItem(bl, NULL, 0);
        }
        m_ResRepaint = false;
    }

    protected void ClearTrCells()
    {
        for (int i = 0; i < m_TrCells.Count(); i++)
        {
            if (m_TrCells[i])
                m_TrCells[i].Unlink();
        }
        m_TrCells.Clear();
        m_TrFlows.Clear();
        ClearTrOrs();
    }

    protected void ClearTrOrs()
    {
        for (int i = 0; i < m_TrOrLabels.Count(); i++)
        {
            if (m_TrOrLabels[i])
                m_TrOrLabels[i].Unlink();
        }
        m_TrOrLabels.Clear();
    }

    // Мітки "АБО" на місцях, які OZL_TreeLines.Draw поклав у m_TrOrs: рядок
    // скіна or_label, текст і колір -- як у вікні гравця (DrawLines).
    protected void PaintTrOrs(float k)
    {
        ClearTrOrs();
        Widget nodes = M_SUB_WIDGET.FindAnyWidget("RzTrNodes");
        if (!nodes || !m_TrSkin)
            return;
        string path = m_TrSkin.RowLayout("or_label");
        for (int i = 0; i < m_TrOrs.Count(); i++)
        {
            Widget lab = GetGame().GetWorkspace().CreateWidgets(path, nodes);
            if (!lab)
                return;
            OZL_TreeMenu.IgnorePointer(lab, null);
            lab.ClearFlags(WidgetFlags.CLIPCHILDREN);
            TextWidget t = TextWidget.Cast(lab.FindAnyWidget("OrText"));
            if (t)
            {
                t.SetText(OZL_Text.Words("STR_OZL_TREE_OR"));
                t.SetColor(m_TrOrs[i].Color);
            }
            lab.SetPos(m_TrOrs[i].X * k, m_TrOrs[i].Y * k);
            m_TrOrLabels.Insert(lab);
        }
    }

    // Рядок під полотном: що зараз зробить клік чи перетягування.
    protected void PaintTrInfo()
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrInfo"));
        if (!t)
            return;
        if (m_TrLink && m_TrLinkFrom == "")
            t.SetText(Tr("#STR_OZL_ED_TR_LINK_FROM"));
        else if (m_TrLink)
            t.SetText(Tr("#STR_OZL_ED_TR_LINK_TO") + m_TrLinkFrom);
        else
            t.SetText(Tr("#STR_OZL_ED_TR_INFO"));
        if (m_TrLink)
            t.SetColor(OZL_Metal.ACCENT);
        else
            t.SetColor(OZL_Metal.MUTED);
    }

    protected void TrInfoText(string text)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrInfo"));
        if (!t)
            return;
        t.SetText(text);
        t.SetColor(OZL_Metal.ACCENT);
    }

    // Рамка ріже дітей по своєму краю (gui-layouts §31): комірка й
    // контейнери NodeHit пускають мітки й написи за край -- як
    // OZL_TreeMenu.Unclip.
    protected void UnclipCell(Widget cell, Widget hit)
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

    // Полотно. full -- заново план і комірки (структура змінилась: власник,
    // гілка, Id, тір, батьки, умова, новий чи прибраний вузол, скасування);
    // інакше -- лише фарба комірок і лінії (вибір, назва, ціна, іконка).
    // fillForm -- переписати поля інспектора; під час набору -- ні, бо
    // курсор у полі стрибав би в кінець.
    protected void RepaintTree(bool full, bool fillForm = true)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_Owners owners = DraftOwners();
        TextWidget skinLbl = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrSkin"));
        CanvasWidget lines = CanvasWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrLines"));
        PaintTrButtons();
        PaintTrInfo();
        if (!tree || !owners)
        {
            ClearTrCells();
            if (lines)
                lines.Clear();
            return;
        }

        RepaintTrLists(tree, owners);
        if (m_TrSel != "" && !tree.FindNode(m_TrSel))
            m_TrSel = "";
        if (m_TrLinkFrom != "" && !tree.FindNode(m_TrLinkFrom))
            m_TrLinkFrom = "";

        OZL_TreeBranch br = TrBranch(tree);
        if (!br)
        {
            ClearTrCells();
            m_TrPlan = null;
            if (lines)
                lines.Clear();
            if (skinLbl)
                skinLbl.SetText(Tr("#STR_OZL_ED_TR_NO_BRANCH"));
            if (fillForm)
            {
                FillTnForm(null);
                FillBrForm(null);
            }
            return;
        }

        string skinId = owners.SkinOf(m_TrOwner);
        if (!m_TrSkin || skinId != m_TrSkinId)
        {
            m_TrSkin = OZL_TreeSkins.Make(skinId);
            m_TrSkinId = skinId;
            full = true;
        }
        float k = Px();
        m_TrSkin.PxPerUnit = k;

        m_TrView = OZL_EdTree.View(tree, br, m_TrOwner);
        if (full || !m_TrPlan || m_TrCells.Count() != m_TrView.Nodes.Count())
            BuildTrCells(k);

        PaintTrCells(tree);
        if (lines)
        {
            string focus = m_TrSel;
            if (m_TrLink && m_TrLinkFrom != "")
                focus = m_TrLinkFrom;
            OZL_TreeLines.Draw(lines, m_TrSkin, m_TrPlan, m_TrView, focus, m_TrOrs);
            PaintTrOrs(k);
        }

        if (skinLbl)
        {
            string dir = SkinDir(m_TrSkin.Dir);
            string windowWord = Tr("#STR_OZL_VPP_TR_WINDOW");
            skinLbl.SetText(windowWord + skinId + " - " + dir);
        }

        if (fillForm)
        {
            FillTnForm(TrNode(tree));
            FillBrForm(br);
        }
    }

    // The way a skin's tree grows, in the client's language.
    protected string SkinDir(string dir)
    {
        if (dir == "up")
            return Tr("#STR_OZL_ED_TR_DIR_UP");
        if (dir == "right")
            return Tr("#STR_OZL_ED_TR_DIR_RIGHT");
        return Tr("#STR_OZL_ED_TR_DIR_DOWN");
    }

    // План гілки під розмір вікна скіна і комірки на його місцях.
    protected void BuildTrCells(float k)
    {
        m_TrPlan = new OZL_TreePlan();
        float vw, vh;
        OZL_EdTree.ViewSize(m_TrSkinId, vw, vh);
        m_TrPlan.Build(m_TrSkin, m_TrView, vw, vh);

        Widget content = M_SUB_WIDGET.FindAnyWidget("RzTrContent");
        if (content)
            content.SetSize(m_TrPlan.W * k, m_TrPlan.H * k);
        ScrollWidget scroll = ScrollWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrScroll"));
        if (scroll)
            scroll.Update();

        ClearTrCells();
        Widget nodes = M_SUB_WIDGET.FindAnyWidget("RzTrNodes");
        if (!nodes)
            return;

        for (int i = 0; i < m_TrView.Nodes.Count(); i++)
        {
            OZL_NodeView nv = m_TrView.Nodes[i];
            int at = m_TrPlan.IndexOf(nv.Id);
            if (at < 0)
                continue;
            Widget cell = GetGame().GetWorkspace().CreateWidgets(m_TrSkin.NodeLayout, nodes);
            if (!cell)
                continue;
            cell.SetPos((m_TrPlan.X[at] - m_TrSkin.AnchorX) * k, (m_TrPlan.Y[at] - m_TrSkin.AnchorY) * k);
            OZL_EdTree.LoadSlots(m_TrSkin, cell);
            Widget hit = cell.FindAnyWidget("NodeHit");
            if (hit)
                hit.SetName("rznode:" + nv.Id);
            cell.SetName("rzcell:" + nv.Id);
            OZL_TreeMenu.IgnorePointer(cell, hit);
            UnclipCell(cell, hit);
            m_TrCells.Insert(cell);
        }
    }

    // Фарба комірок: стан "available" для всіх (редактор стану не має),
    // вибраний (і джерело зв'язку) -- виділений; ціна -- фішками з вузла
    // чернетки, як у вікні гравця, або рядком, якщо скін фішок не має.
    protected void PaintTrCells(OZL_TreeConfig tree)
    {
        OZL_PointTypes pts = DraftPointTypes();
        m_TrFlows.Clear();
        m_TrFlowTries = 0;
        for (int c = 0; c < m_TrCells.Count(); c++)
        {
            Widget cell = m_TrCells[c];
            if (!cell)
                continue;
            string nm = cell.GetName();
            string id = nm.Substring(7, nm.Length() - 7);
            for (int i = 0; i < m_TrView.Nodes.Count(); i++)
            {
                OZL_NodeView nv = m_TrView.Nodes[i];
                if (nv.Id != id)
                    continue;
                string price = "";
                OZL_TreeNode tn = tree.FindNode(id);
                Widget chips = null;
                if (tn)
                    chips = OZL_EdTree.PaintChips(m_TrSkin, cell, tn, pts, "available");
                if (tn && !chips)
                    price = OZL_EdTree.PriceText(tn, pts);
                bool picked = (id == m_TrSel);
                if (m_TrLink && m_TrLinkFrom != "")
                    picked = (id == m_TrLinkFrom);
                OZL_EdTree.Paint(m_TrSkin, cell, nv, "available", picked, nv.Index + 1, price);
                if (chips)
                    m_TrFlows.Insert(chips);
                break;
            }
        }
    }

    // Фішки, що чекають ширини тексту; після дванадцяти кадрів -- як є.
    protected void RunTrFlows()
    {
        if (m_TrFlows.Count() == 0)
            return;
        float k = Px();
        m_TrFlowTries++;
        bool force = m_TrFlowTries > 12;
        for (int i = m_TrFlows.Count() - 1; i >= 0; i--)
        {
            Widget box = m_TrFlows[i];
            if (!box)
            {
                m_TrFlows.RemoveOrdered(i);
                continue;
            }
            if (OZL_EdTree.FlowChips(m_TrSkin, box, k, force))
                m_TrFlows.RemoveOrdered(i);
        }
        if (m_TrFlows.Count() == 0)
            m_TrFlowTries = 0;
    }

    // Кнопки полотна: ЗВ'ЯЗОК світиться, поки режим увімкнено; поле стану
    // перегляду в голові сторінки називає стан, з яким відкриється перегляд.
    protected void PaintTrButtons()
    {
        PaintToggle("BtnRzTrLink", m_TrLink);

        string demo = "#STR_OZL_ED_TR_DEMO_NEW";
        if (m_TrDemo == 1)
            demo = "#STR_OZL_ED_TR_DEMO_FUNDED";
        else if (m_TrDemo == 2)
            demo = "#STR_OZL_ED_TR_DEMO_PROGRESS";
        SetBtnText("BtnRzTrDemo", Tr(demo), OZL_Metal.TEXT);
    }

    // Інспектор вузла: поля вибраного вузла, а без нього -- рядок, як вибрати.
    // Гілка має свою форму ліворуч, поруч (дизайн вікна §5.5).
    protected void FillTnForm(OZL_TreeNode n)
    {
        ShowW("RzTnForm", n != null);
        ShowW("RzTnEmpty", n == null);
        if (!n)
        {
            SetLabel("RzTnHead", "#STR_OZL_ED_TN_PICK", 0);
            SetLabel("RzTnSub", "", 0);
            m_TnRefId = "";
            return;
        }

        PaintTnHead(n);

        m_RzFill = true;
        SetEdit("RzTnId", n.Id);
        SetEdit("RzTnName", n.Name);
        SetEdit("RzTnTier", n.Tier.ToString());
        SetEdit("RzTnParents", OZL_EdTree.ParentsText(n));
        SetEdit("RzTnCost", OZL_EdTree.CostText(n));
        SetEdit("RzTnItems", OZL_EdTree.ItemsText(n));
        SetEdit("RzTnTime", n.ResearchTimeSec.ToString());
        SetEdit("RzTnIcon", n.Icon);
        m_TnRefId = n.Id;
        m_RzFill = false;
    }

    // The node's head (its name; id, tier and branch under it), its condition pair
    // and its cost in the lines' own names -- painted on every keystroke too.
    protected void PaintTnHead(OZL_TreeNode n)
    {
        if (!n)
            return;
        string name = n.Name;
        if (name == "")
            name = n.Id;
        SetLabel("RzTnHead", name, 0);
        string tierWord = Tr("#STR_OZL_VPP_TN_TIER");
        string branchWord = Tr("#STR_OZL_VPP_TN_BRANCH");
        string sub = n.Id + "  |  " + tierWord + n.Tier.ToString();
        sub += "  |  " + branchWord + m_TrBranch;
        SetLabel("RzTnSub", sub, 0);

        string mode = n.ParentsMode;
        mode.ToLower();
        bool anyMode = (mode == "any");
        PaintToggle("BtnRzTnModeAll", !anyMode);
        PaintToggle("BtnRzTnModeAny", anyMode);

        SetLabel("RzTnPrice", OZL_EdTree.PriceText(n, DraftPointTypes()), 0);
    }

    // Форма гілки ліворуч: поля вибраної гілки, порожні без неї.
    protected void FillBrForm(OZL_TreeBranch br)
    {
        string head = Tr("#STR_OZL_ED_TR_NO_BRANCH");
        if (br)
        {
            string branchWord = Tr("#STR_OZL_ED_BR_HEAD");
            head = branchWord + " " + br.Id;
        }
        SetLabel("RzBrHead", head, 0);
        m_RzFill = true;
        if (br)
        {
            SetEdit("RzBrId", br.Id);
            SetEdit("RzBrName", br.Name);
            SetEdit("RzBrOwners", OZL_EdTree.ListText(br.Owners));
            SetEdit("RzBrSort", br.SortOrder.ToString());
            SetEdit("RzBrIcon", br.Icon);
        }
        else
        {
            SetEdit("RzBrId", "");
            SetEdit("RzBrName", "");
            SetEdit("RzBrOwners", "");
            SetEdit("RzBrSort", "");
            SetEdit("RzBrIcon", "");
        }
        m_RzFill = false;
    }

    // Поле гілки змінилось: один знімок на поле, як у вузла.
    protected void OnBrField(string field)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeBranch br = TrBranch(tree);
        if (!br)
            return;

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "br:" + field);
        string v = GetEdit(field);
        if (field == "RzBrId")
        {
            br.Id = v.Trim();
            m_TrBranch = br.Id;
        }
        else if (field == "RzBrName")
            br.Name = v;
        else if (field == "RzBrOwners")
            OZL_EdTree.ParseList(v, br.Owners);
        else if (field == "RzBrSort")
            br.SortOrder = v.ToInt();
        else if (field == "RzBrIcon")
            br.Icon = v.Trim();

        m_Ed.Commit(tag);
        RepaintTree(true, false);
        string branchWord = Tr("#STR_OZL_ED_BR_HEAD");
        SetLabel("RzBrHead", branchWord + " " + br.Id, 0);
        PaintRzBar();
        PaintSummary();
    }

    protected void BrAdd()
    {
        OZL_TreeConfig tree = DraftTree();
        if (!tree)
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }
        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        OZL_TreeBranch br = new OZL_TreeBranch();
        string base = m_TrOwner + "_branch";
        if (m_TrOwner == "")
            base = "branch";
        br.Id = OZL_EdTree.FreeBranchId(tree, base);
        br.Name = br.Id;
        if (m_TrOwner != "")
            br.Owners.Insert(m_TrOwner);
        tree.Branches.Insert(br);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();

        m_TrBranch = br.Id;
        m_TrSel = "";
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_BR_ADDED") + br.Id);
    }

    // Гілка йде разом зі своїми вузлами й усіма посиланнями на них -- після
    // «так» у рядку підтвердження вікна.
    protected void BrDelete()
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeBranch br = TrBranch(tree);
        if (!br)
        {
            Hint(Tr("#STR_OZL_ED_TR_PICK_BRANCH"));
            return;
        }
        string ask = Tr("#STR_OZL_VPP_ASK_DEL_BRANCH");
        string mid = Tr("#STR_OZL_VPP_ASK_DEL_BRANCH2");
        string tail = Tr("#STR_OZL_VPP_ASK_DEL_BRANCH3");
        string nodes = br.Nodes.Count().ToString();
        Confirm(ask + br.Id + mid + nodes + tail, "#STR_OZL_VPP_YES_DELETE", "rz:brdel:" + br.Id);
    }

    protected void BrDeleteNow(string branchId)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeBranch br = null;
        if (tree)
            br = OZL_EdTree.FindBranch(tree, branchId);
        if (!br)
        {
            Hint(Tr("#STR_OZL_VPP_GONE") + branchId);
            return;
        }

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        string id = br.Id;
        array<string> gone = new array<string>();
        int i;
        for (i = 0; i < br.Nodes.Count(); i++)
        {
            if (br.Nodes[i])
                gone.Insert(br.Nodes[i].Id);
        }
        for (i = tree.Branches.Count() - 1; i >= 0; i--)
        {
            if (tree.Branches[i] == br)
                tree.Branches.RemoveOrdered(i);
        }
        for (i = 0; i < gone.Count(); i++)
            OZL_EdTree.DropRefs(tree, gone[i]);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();

        // RepaintTree drops a picked node that is gone with the branch.
        if (m_TrBranch == id)
        {
            m_TrBranch = "";
            m_TrSel = "";
        }
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_BR_DELETED") + id);
    }

    // ------------------------------------------------- зв'язки, тір, перегляд

    protected void TrLinkToggle()
    {
        m_TrLink = !m_TrLink;
        m_TrLinkFrom = "";
        if (m_TrLink && m_TrSel != "")
            m_TrLinkFrom = m_TrSel;
        m_Ed.EndGesture();
        RepaintTree(false);
    }

    // Клік по вузлу в режимі зв'язку: перший -- батько, далі -- діти; клік
    // по дитині, що вже має цей зв'язок, його прибирає; клік по самому
    // батькові -- вибрати іншого.
    protected void TrLinkClick(string id)
    {
        if (m_TrLinkFrom == "" )
        {
            m_TrLinkFrom = id;
            m_TrSel = id;
            RepaintTree(false);
            return;
        }
        if (id == m_TrLinkFrom)
        {
            m_TrLinkFrom = "";
            RepaintTree(false);
            return;
        }

        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode parent = tree.FindNode(m_TrLinkFrom);
        OZL_TreeNode child = tree.FindNode(id);
        if (!parent || !child)
            return;

        string tag = OZL_Config.TAG_TREE;
        int at = child.Parents.Find(m_TrLinkFrom);
        if (at >= 0)
        {
            m_Ed.BeginOnce(tag, "");
            child.Parents.RemoveOrdered(at);
            m_Ed.Commit(tag);
            m_Ed.EndGesture();
            Hint(Tr("#STR_OZL_ED_TR_UNLINKED") + m_TrLinkFrom + " -> " + id);
        }
        else
        {
            if (OZL_EdTree.DependsOn(tree, parent, id, 0))
            {
                Hint(Tr("#STR_OZL_ED_TR_CYCLE") + m_TrLinkFrom + " -> " + id);
                return;
            }
            m_Ed.BeginOnce(tag, "");
            child.Parents.Insert(m_TrLinkFrom);
            string note = "";
            if (child.Tier <= parent.Tier)
            {
                child.Tier = parent.Tier + 1;
                note = Tr("#STR_OZL_ED_TR_BUMPED") + child.Tier.ToString();
            }
            m_Ed.Commit(tag);
            m_Ed.EndGesture();
            Hint(Tr("#STR_OZL_ED_TR_LINKED") + m_TrLinkFrom + " -> " + id + note);
        }
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
    }

    // Тір під вузлом, зсунутим уздовж осі на along пікселів: ряд плану, у
    // який потрапив центр вузла. За останнім рядом -- новий тір, перед
    // першим -- на один менший (не нижче 1).
    protected int TierAt(string id, float along)
    {
        if (!m_TrPlan || !m_TrSkin)
            return 1;
        int at = m_TrPlan.IndexOf(id);
        int n = m_TrPlan.Tiers.Count();
        if (at < 0 || n == 0)
            return 1;
        float u = m_TrPlan.U[at];
        if (m_TrSkin.Dir == "up")
            u -= along / Px();
        else
            u += along / Px();
        float row = Math.Floor((u - m_TrSkin.Top) / m_TrSkin.Row);
        int ti = row;
        if (ti >= n)
            return m_TrPlan.Tiers[n - 1] + 1;
        if (ti < 0)
        {
            int first = m_TrPlan.Tiers[0] - 1;
            if (first < 1)
                first = 1;
            return first;
        }
        return m_TrPlan.Tiers[ti];
    }

    // Натиснули на вузлі й тягнуть: комірка їде за мишею вздовж осі, рядок
    // під полотном називає тір; відпустили -- тір вузла, один знімок.
    protected void TrackTnDrag()
    {
        if (m_TnDragId == "")
            return;
        int mx;
        int my;
        GetMousePos(mx, my);
        float dx = mx - m_TnDragX;
        float dy = my - m_TnDragY;
        bool horiz = (m_TrSkin && m_TrSkin.Dir == "right");
        float along = dy;
        if (horiz)
            along = dx;

        if (!(GetMouseState(MouseState.LEFT) & 0x80000000))
        {
            string id = m_TnDragId;
            m_TnDragId = "";
            if (m_TnDragMoved)
            {
                m_TnSkipClick = 3;
                DropTier(id, along);
            }
            return;
        }

        if (!m_TnDragMoved && Math.AbsFloat(along) > 6 * Px())
            m_TnDragMoved = true;
        if (!m_TnDragMoved)
            return;
        Widget cell = M_SUB_WIDGET.FindAnyWidget("rzcell:" + m_TnDragId);
        if (cell)
        {
            if (horiz)
                cell.SetPos(m_TnCellX + dx, m_TnCellY);
            else
                cell.SetPos(m_TnCellX, m_TnCellY + dy);
        }
        TrInfoText(Tr("#STR_OZL_ED_TR_DRAG_TIER") + TierAt(m_TnDragId, along).ToString());
    }

    protected void DropTier(string id, float along)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = null;
        if (tree)
            n = tree.FindNode(id);
        int tier = TierAt(id, along);
        if (!n || tier == n.Tier)
        {
            RepaintTree(true, false);
            return;
        }
        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        int was = n.Tier;
        n.Tier = tier;
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        m_TrSel = id;
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_TR_TIER_SET") + id + ": " + was.ToString() + " -> " + tier.ToString());
    }

    // Натиснули на порожньому полотні: тягнення прокручує, клік без руху --
    // зняти вибір вузла (інспектор показує гілку).
    protected void TrackTrPan()
    {
        if (!m_TrPanDown)
            return;
        int mx;
        int my;
        GetMousePos(mx, my);
        float dx = mx - m_TrPanX;
        float dy = my - m_TrPanY;
        if (!(GetMouseState(MouseState.LEFT) & 0x80000000))
        {
            m_TrPanDown = false;
            if (!m_TrPanMoved && m_TrSel != "" && !m_TrLink)
            {
                m_TrSel = "";
                m_Ed.EndGesture();
                RepaintTree(false);
            }
            return;
        }
        if (Math.AbsFloat(dx) + Math.AbsFloat(dy) > 4 * Px())
            m_TrPanMoved = true;
        if (!m_TrPanMoved)
            return;
        ScrollWidget sw = ScrollWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrScroll"));
        if (!sw)
            return;
        sw.HScrollToPos(m_TrPanH - dx);
        sw.VScrollToPos(m_TrPanV - dy);
    }

    // Чи натиснуто на смугу прокрутки полотна (10 одиниць біля правого й
    // нижнього краю, як у вікні гравця).
    protected bool OnTrScrollbar(int x, int y)
    {
        Widget sw = M_SUB_WIDGET.FindAnyWidget("RzTrScroll");
        if (!sw)
            return false;
        float sx;
        float sy;
        float sww;
        float swh;
        sw.GetScreenPos(sx, sy);
        sw.GetScreenSize(sww, swh);
        float bar = 10 * Px();
        bool onBar = false;
        if (x > sx + sww - bar || y > sy + swh - bar)
            onBar = true;
        return onBar;
    }

    // ЯК У ГРАВЦЯ: вікно дерева гравця поверх адмінського, з виглядом із
    // чернетки й демо-стану. Меню VPP лишається батьком (як записка над
    // інвентарем у ванілі): ESC закриває дерево й повертає сюди.
    protected void TrPreview()
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_Owners owners = DraftOwners();
        OZL_PointTypes pts = DraftPointTypes();
        OZL_Settings se = null;
        OZL_EdDoc sd = m_Ed.Doc(OZL_Config.TAG_SETTINGS);
        if (sd && sd.Loaded)
            se = OZL_Settings.Cast(sd.Obj);
        if (!tree || !owners || !pts || !se || m_TrOwner == "")
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }

        OZL_TreeView v = OZL_EdTree.PlayerView(tree, owners, pts, se, m_TrOwner, m_TrDemo);
        string json = JsonFileLoader<OZL_TreeView>.JsonMakeData(v);
        OZL_TreeMenu.PreviewNext(json);
        UIManager ui = GetGame().GetUIManager();
        UIScriptedMenu menu = ui.EnterScriptedMenu(OZL_Const.MENU_TREE, ui.GetMenu());
        if (!menu)
        {
            OZL_TreeMenu.PreviewNext("");
            Hint(Tr("#STR_OZL_ED_TR_VIEW_FAIL"));
            return;
        }
        Hint(Tr("#STR_OZL_ED_TR_VIEW_OPEN") + m_TrOwner);
    }

    override void OnUpdate(float timeslice)
    {
        super.OnUpdate(timeslice);
        if (!M_SUB_WIDGET || !m_TrFlows)
            return;
        RunTrFlows();
        TrackTnDrag();
        TrackTrPan();
        if (m_TnSkipClick > 0)
            m_TnSkipClick--;
    }

    override bool OnMouseButtonDown(Widget w, int x, int y, int button)
    {
        if (w && M_SUB_WIDGET && m_TrFlows && button == MouseState.LEFT && m_RzTab == "tree" && RzShown())
        {
            string nm = w.GetName();
            if (nm.IndexOf("rznode:") == 0)
            {
                m_TnDragMoved = false;
                if (!m_TrLink)
                {
                    m_TnDragId = nm.Substring(7, nm.Length() - 7);
                    GetMousePos(m_TnDragX, m_TnDragY);
                    Widget cell = M_SUB_WIDGET.FindAnyWidget("rzcell:" + m_TnDragId);
                    if (cell)
                        cell.GetPos(m_TnCellX, m_TnCellY);
                }
            }
            else if (nm == "RzTrNodes" || nm == "RzTrContent" || (nm == "RzTrScroll" && !OnTrScrollbar(x, y)))
            {
                ScrollWidget sw = ScrollWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrScroll"));
                if (sw)
                {
                    m_TrPanDown = true;
                    m_TrPanMoved = false;
                    GetMousePos(m_TrPanX, m_TrPanY);
                    m_TrPanH = sw.GetHScrollPos();
                    m_TrPanV = sw.GetVScrollPos();
                }
            }
        }
        return super.OnMouseButtonDown(w, x, y, button);
    }

    // Поле інспектора змінилось: правка вибраного вузла, один знімок на поле.
    protected void OnTnField(string field)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = TrNode(tree);
        if (!n)
            return;

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "tn:" + field);

        string v = GetEdit(field);
        bool structural = false;
        if (field == "RzTnId")
        {
            RenameTn(tree, n, v.Trim());
            structural = true;
        }
        else if (field == "RzTnName")
            n.Name = v;
        else if (field == "RzTnTier")
        {
            n.Tier = v.ToInt();
            structural = true;
        }
        else if (field == "RzTnParents")
        {
            OZL_EdTree.ParseParents(v, n);
            structural = true;
        }
        else if (field == "RzTnCost")
            OZL_EdTree.ParseCost(v, n);
        else if (field == "RzTnItems")
            OZL_EdTree.ParseItems(v, n);
        else if (field == "RzTnTime")
            n.ResearchTimeSec = v.ToInt();
        else if (field == "RzTnIcon")
            n.Icon = v.Trim();

        m_Ed.Commit(tag);
        RepaintTree(structural, false);
        PaintTnHead(n);
        PaintRzBar();
        PaintSummary();
    }

    // Новий Id вузла. Посилання (батьки інших вузлів) ідуть за ним лише на
    // ВІЛЬНИЙ Id: проміжний Id, що збігся з чужим, під час набору лишає їх
    // на попередньому -- інакше вони перейшли б до чужого вузла назавжди.
    protected void RenameTn(OZL_TreeConfig tree, OZL_TreeNode n, string id)
    {
        n.Id = id;
        m_TrSel = id;
        if (id == "" || id == m_TnRefId)
            return;
        if (OZL_EdTree.CountId(tree, id) != 1)
            return;
        OZL_EdTree.RenameRefs(tree, m_TnRefId, id);
        m_TnRefId = id;
    }

    protected void TnAdd(bool child)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeBranch br = TrBranch(tree);
        if (!br)
        {
            Hint(Tr("#STR_OZL_ED_TR_PICK_BRANCH"));
            return;
        }
        OZL_TreeNode parent = null;
        if (child)
        {
            parent = TrNode(tree);
            if (!parent)
            {
                Hint(Tr("#STR_OZL_ED_TN_PICK"));
                return;
            }
        }

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        OZL_TreeNode n = new OZL_TreeNode();
        n.Id = OZL_EdTree.FreeId(tree, br.Id + "_node");
        n.Name = n.Id;
        n.Tier = 1;
        if (parent)
        {
            n.Tier = parent.Tier + 1;
            n.Parents.Insert(parent.Id);
        }
        br.Nodes.Insert(n);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();

        m_TrSel = n.Id;
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_TR_ADDED") + n.Id);
    }

    protected void TnDelete()
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = TrNode(tree);
        if (!n)
        {
            Hint(Tr("#STR_OZL_ED_TN_PICK"));
            return;
        }
        string ask = Tr("#STR_OZL_VPP_ASK_DEL_NODE");
        string tail = Tr("#STR_OZL_VPP_ASK_DEL_NODE2");
        Confirm(ask + n.Id + tail, "#STR_OZL_VPP_YES_DELETE", "rz:tndel:" + n.Id);
    }

    // The strip's "yes": the node is found again by its id, every link to it goes too.
    protected void TnDeleteNow(string nodeId)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = null;
        if (tree)
            n = tree.FindNode(nodeId);
        if (!n)
        {
            Hint(Tr("#STR_OZL_VPP_GONE") + nodeId);
            return;
        }

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        string id = n.Id;
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            for (int i = br.Nodes.Count() - 1; i >= 0; i--)
            {
                if (br.Nodes[i] == n)
                    br.Nodes.RemoveOrdered(i);
            }
        }
        OZL_EdTree.DropRefs(tree, id);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();

        if (m_TrSel == id)
            m_TrSel = "";
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_TR_DELETED") + id);
    }

    // The node's condition from its pair of buttons: any parent, or all of them. A
    // press on the one in force changes nothing and takes no undo step.
    protected void TnSetMode(bool anyParent)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = TrNode(tree);
        if (!n)
        {
            Hint(Tr("#STR_OZL_ED_TN_PICK"));
            return;
        }
        string mode = n.ParentsMode;
        mode.ToLower();
        bool wasAny = (mode == "any");
        if (wasAny == anyParent)
            return;
        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        if (anyParent)
            n.ParentsMode = "any";
        else
            n.ParentsMode = "all";
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
    }

    // ================================================= розмір вікна

    // Вікно змінило розмір (OZ_VppAdminMenu.ApplyWindowSize): панель тепер
    // w x h пікселів -- область вмісту праворуч від рейки (1060 x 680 одиниць
    // за замовчуванням). Генератор розмітки поставив усе в точні місця, тож
    // голова, сторінки, панель проблем і смуга чернетки перекладаються звідси
    // (RzLayout): списки, полотно дерева й сировина тягнуться, форми лишаються
    // своєї ширини.
    //
    // NOTHING IS READ BACK: the shell lays the window out once before the engine's
    // first layout pass (the first show), and a widget measured then reads 0 x 0
    // (dayz-modding gui-layouts §23a). Every size comes from w, h and the layout's own
    // numbers.
    override void OnWindowResized(float w, float h)
    {
        super.OnWindowResized(w, h);
        if (!M_SUB_WIDGET)
            return;
        m_RzW = w;
        m_RzH = h;
        RzLayout();
    }

    // The tree page: the side column (owners, branches, the branch's form at the
    // bottom), the canvas taking what is left, the node's form on the right.
    protected void RzLayTree(float pw, float ph)
    {
        float s = Px();
        float gap = 16 * s;
        float sideW = 250 * s;
        float inspW = 300 * s;
        float midW = pw - sideW - inspW - 2 * gap;
        if (midW < 160 * s)
            midW = 160 * s;

        // The side column: the branch's form keeps its 250 units at the bottom, the two
        // lists share the rest (the owners a little less), each at least 40.
        SizeW("RzTrSide", sideW, ph);
        float avail = ph - (18 + 8 + 30) * s - 250 * s - 8 * s;
        float ownersH = avail * 0.45;
        if (ownersH < 40 * s)
            ownersH = 40 * s;
        float branchesH = avail - ownersH;
        if (branchesH < 40 * s)
            branchesH = 40 * s;
        SizeW("RzTrOwners", sideW, ownersH);
        float headY = 18 * s + ownersH + 8 * s;
        MoveW("RzTrBrHead", 0, headY);
        MoveW("BtnRzBrAdd", 150 * s, headY);
        PlaceW("RzTrBranches", 0, headY + 30 * s, sideW, branchesH);

        // The canvas.
        PlaceW("RzTrMid", sideW + gap, 0, midW, ph);
        SizeW("RzTrBar", midW, 32 * s);
        float skinW = midW - (318 + 8) * s;
        if (skinW < 0)
            skinW = 0;
        SizeW("RzTrSkin", skinW, 32 * s);
        float canvasH = ph - (36 + 26) * s;
        if (canvasH < 60 * s)
            canvasH = 60 * s;
        SizeW("RzTrHost", midW, canvasH);
        SizeW("RzTrScroll", midW, canvasH);
        SizeW("RzTrInfo", midW, 22 * s);

        // The node's form.
        PlaceW("RzTrInsp", pw - inspW, 0, inspW, ph);
        float formH = ph - 66 * s;
        if (formH < 40 * s)
            formH = 40 * s;
        SizeW("RzTnForm", inspW, formH);

        ScrollWidget sw = ScrollWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrScroll"));
        if (sw)
            sw.Update();
    }

    // Кнопка генератора -- корінь і троє дітей тієї самої ширини: рамка на
    // одиницю ширша з кожного боку, тло й напис -- як корінь.
    protected void PlaceBtn(string name, float x, float y, float w, float h)
    {
        Widget b = M_SUB_WIDGET.FindAnyWidget(name);
        if (!b)
            return;
        float s = Px();
        b.SetPos(x, y);
        b.SetSize(w, h);
        Widget edge = b.FindAnyWidget(name + "Edge");
        if (edge)
            edge.SetSize(w + 2 * s, h + 2 * s);
        Widget bg = b.FindAnyWidget(name + "Bg");
        if (bg)
            bg.SetSize(w, h);
        Widget tx = b.FindAnyWidget(name + "Text");
        if (tx)
            tx.SetSize(w, h);
    }

    // ================================================= події

    override bool OnItemSelected(Widget w, int x, int y, int row, int column, int oldRow, int oldColumn)
    {
        if (!M_SUB_WIDGET || m_ResRepaint || !w)
            return super.OnItemSelected(w, x, y, row, column, oldRow, oldColumn);

        string nm = w.GetName();
        if (nm == "ResOwners")
        {
            if (row >= 0 && row < m_ResOwners.Count())
            {
                m_ResPicked = row;
                m_ResRepaint = true;
                RepaintOwners();
                m_ResRepaint = false;
                PaintPicked();
                string pickedHint = Tr("#STR_OZL_VPP_HINT_FACTION");
                Hint(pickedHint + PickedOwner());
            }
            return true;
        }
        if (nm == "RzTrOwners")
        {
            OZL_Owners owners = DraftOwners();
            if (owners && row >= 0 && row < owners.Owners.Count() && owners.Owners[row])
            {
                m_TrOwner = owners.Owners[row].Id;
                m_TrBranch = "";
                m_TrSel = "";
                m_TrLinkFrom = "";
                m_Ed.EndGesture();
                RepaintTree(true);
            }
            return true;
        }
        if (nm == "RzTrBranches")
        {
            OZL_TreeConfig tree = DraftTree();
            if (tree)
            {
                array<string> ids = new array<string>();
                TrBranchIds(tree, ids);
                if (row >= 0 && row < ids.Count())
                {
                    m_TrBranch = ids[row];
                    m_TrSel = "";
                    m_TrLinkFrom = "";
                    m_Ed.EndGesture();
                    RepaintTree(true);
                }
            }
            return true;
        }
        if (nm == "RzPtList")
        {
            OZL_PointTypes pts = DraftPointTypes();
            if (pts && row >= 0 && row < pts.PointTypes.Count())
            {
                m_PtPicked = row;
                m_Ed.EndGesture();
                RepaintPoints(true);
            }
            return true;
        }
        return super.OnItemSelected(w, x, y, row, column, oldRow, oldColumn);
    }

    override bool OnChange(Widget w, int x, int y, bool finished)
    {
        if (w && M_SUB_WIDGET && !m_RzFill && m_Ed)
        {
            string nm = w.GetName();
            if (nm == "RzPtId" || nm == "RzPtName" || nm == "RzPtColor" || nm == "RzPtSort" || nm == "RzPtPurity" || nm == "RzPtIcon")
            {
                OnPtField(nm);
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
            if (nm.IndexOf("RzTn") == 0)
            {
                OnTnField(nm);
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
            if (nm.IndexOf("RzBr") == 0)
            {
                OnBrField(nm);
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
        }
        return super.OnChange(w, x, y, finished);
    }

    override bool OnClick(Widget w, int x, int y, int button)
    {
        if (!M_SUB_WIDGET || !w)
            return super.OnClick(w, x, y, button);

        string nm = w.GetName();

        // Вузол на полотні: NodeHit його комірки названий rznode:<id>. Клік,
        // що прийшов із відпусканням після перетягування, -- не вибір.
        if (nm.IndexOf("rznode:") == 0)
        {
            if (m_TnSkipClick > 0 || m_TnDragMoved)
                return true;
            string picked = nm.Substring(7, nm.Length() - 7);
            m_Ed.EndGesture();
            if (m_TrLink)
            {
                TrLinkClick(picked);
                return true;
            }
            m_TrSel = picked;
            RepaintTree(false);
            return true;
        }
        if (nm == "BtnRzTrRoot")
        {
            TnAdd(false);
            return true;
        }
        if (nm == "BtnRzTrChild")
        {
            TnAdd(true);
            return true;
        }
        if (nm == "BtnRzTrLink")
        {
            TrLinkToggle();
            return true;
        }
        if (nm == "BtnRzTrView")
        {
            TrPreview();
            return true;
        }
        // The preview's state, a select of three: the value steps on, the arrows
        // step either way.
        if (nm == "BtnRzTrDemo" || nm == "BtnRzTrDemoNext")
        {
            m_TrDemo = (m_TrDemo + 1) % 3;
            PaintTrButtons();
            return true;
        }
        if (nm == "BtnRzTrDemoPrev")
        {
            m_TrDemo = (m_TrDemo + 2) % 3;
            PaintTrButtons();
            return true;
        }
        if (nm == "BtnRzBrAdd")
        {
            BrAdd();
            return true;
        }
        if (nm == "BtnRzBrDel")
        {
            BrDelete();
            return true;
        }
        if (nm == "BtnRzTnModeAll" || nm == "BtnRzTnModeAny")
        {
            bool anyParent = (nm == "BtnRzTnModeAny");
            TnSetMode(anyParent);
            return true;
        }
        if (nm == "BtnRzTnDel")
        {
            TnDelete();
            return true;
        }

        // The problems panel above the draft bar opens and closes here and on its
        // own close button.
        if (nm == "BtnRzProblems")
        {
            RzShowProblems(!m_RzProblems);
            return true;
        }
        if (nm == "BtnRzProbClose")
        {
            RzShowProblems(false);
            return true;
        }
        if (nm == "BtnRzUndo")
        {
            RzUndo(false);
            return true;
        }
        if (nm == "BtnRzRedo")
        {
            RzUndo(true);
            return true;
        }
        if (nm == "BtnRzDiscard")
        {
            RzDiscard();
            return true;
        }
        if (nm == "BtnRzApply")
        {
            RzApply();
            return true;
        }
        if (nm == "BtnRzPtDel")
        {
            PtDelete();
            return true;
        }

        // The page head's one action: refresh on the overview, a new point type here;
        // the config layer takes it for owners, modules and statics.
        if (nm == "BtnRzHdAct" && m_RzTab == "overview")
        {
            AskResearchList();
            return true;
        }
        if (nm == "BtnRzHdAct" && m_RzTab == "points")
        {
            PtAdd();
            return true;
        }

        // Перечитування й скидання питають рядком підтвердження вікна (дизайн
        // вікна §3.4); «так» шле операцію з OnConfirmed.
        if (nm == "BtnReload")
        {
            Confirm(Tr("#STR_OZL_VPP_ASK_RELOAD"), "#STR_OZL_VPP_YES_RELOAD", "rz:reload");
            return true;
        }

        if (nm == "BtnReset")
        {
            string owner = PickedOwner();
            if (owner == "")
            {
                Hint(Tr("#STR_OZL_ED_OV_PICK"));
                return true;
            }
            Confirm(ResetAsk(owner), "#STR_OZL_VPP_YES_RESET", "rz:reset:" + owner);
            return true;
        }

        if (nm == "BtnGrant")
        {
            string gOwner = PickedOwner();
            string type = GetEdit("GrantType");
            string n = GetEdit("GrantN");
            type.TrimInPlace();
            n.TrimInPlace();
            if (gOwner == "" || type == "" || n.ToInt() <= 0)
            {
                Hint(Tr("#STR_OZL_VPP_HINT_GRANT_NEED"));
                return true;
            }
            string grantOp = "grant:" + gOwner + ":" + type + ":" + n.ToInt().ToString();
            Ask(OZL_Const.SECTION, grantOp, "{}");
            string granting = Tr("#STR_OZL_VPP_HINT_GRANTING");
            Hint(granting + n + " " + type + " -> " + gOwner);
            return true;
        }

        if (nm == "BtnComplete")
        {
            string cOwner = PickedOwner();
            string node = GetEdit("NodeId");
            node.TrimInPlace();
            if (cOwner == "" || node == "")
            {
                Hint(Tr("#STR_OZL_VPP_HINT_COMPLETE_NEED"));
                return true;
            }
            Ask(OZL_Const.SECTION, "complete:" + cOwner + ":" + node, "{}");
            string completing = Tr("#STR_OZL_VPP_HINT_COMPLETING");
            Hint(completing + node + " -> " + cOwner);
            return true;
        }

        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
