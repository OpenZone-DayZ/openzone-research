// The module «Дослідження» of the OpenZone admin window: the research editor
// (docs/specs/2026-11-09-research-editor-vpp-design.md). Since 2026-11-13 every page of the
// rail is a pane of its own, converted from its mockup board
// (docs/specs/2026-11-13-openzone-vpp-page-guide.md): eight layouts ozl_vpp_<page>, and two
// strips that exist once and lie over the bottom of whichever research page is open -- the
// draft bar (ozl_vpp_bar) and, above it while it is open, the problems panel (ozl_vpp_probs).
//
// THIS FILE IS THE FRAME and two of the pages. The frame: the eight panes are created and
// registered here (a pane whose layout is missing is left out with an error line), the draft
// of the seven files (OZL_EdDocs) is fetched, checked, undone, discarded and applied here,
// and the bar and the panel are painted here. The pages: Огляд (factions and their pools,
// grants, a node completed, a reset, the configs read again) and Дерево (a branch drawn in
// its owner's skin, with the editor's handles). Ланцюги lives in OZL_VppPaneChains.c; Типи
// балів, Власники, Модулі, Статики and Налаштування in OZL_VppPaneConfigs.c and
// OZL_VppPaneSettings.c. Each of those is a later modded layer of the same class.
//
// What a page layer takes from the frame:
//   RepaintRzPage(tab)   override, call super: fill page `tab` from the draft. Called when
//                        the page is shown and after a fetch, an undo, a redo, a discard, an
//                        apply -- only while a research page is on screen;
//   RzLayPages(pw, ph)   override, call super: the open page (m_RzTab) changed its size, or
//                        its texts have their widths now: fit the lists, place what follows
//                        a text. Called after a resize and two frames after every repaint
//                        and every PaintRzBar. pw x ph is the content area in pixels;
//   OnRzConfigAnswer     override, call super: an answer of the core's config section
//                        other than cfg_set;
//   OnConfirmed(action)  override: take your own "rz:..." actions, hand the rest to super;
//   m_Ed, m_RzTab, m_RzFill; PaintRzBar() and PaintSummary() after every edit of the draft;
//   RzSay / RzHint / Hint for a line on the bar; the Draft* getters; the small widget
//   helpers below (SetLabel, SetColorOf, ShowW, RzFitText, RzFlowAfter, RzFitLegend,
//   RzPaintTick, RzSeg ...).
//
// Guards: NO_GUI -- the server compiles Mission without UI; AVPPAdminTools and OpenZone_VPP
// are CfgMods class names (the engine defines them).

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    // The page ids of the rail are "research." + the page's key.
    static const string RZ_PAGE = "research.";

    // The strips, in layout units (ozl_vpp_bar and ozl_vpp_probs as converted: convert
    // again, check these). The problems panel is drawn for six rows; a row and its gap
    // are 31 units, and the panel shows eight rows at most before its list scrolls.
    static const float RZ_BAR_H    = 60;
    static const float RZ_PROBS_H  = 244;
    static const int   RZ_PROBS_ROWS = 8;

    // A list draws at most this many rows.
    static const int RZ_LIST_MAX = 300;

    // ------------------------------------------------- the frame
    protected ref OZL_EdDocs m_Ed;

    // The open page (its key after "research."), whether the problems panel is open, and
    // whether the seven files were asked for (once per window).
    protected string m_RzTab;
    protected bool   m_RzProblems;
    protected bool   m_RzAsked;

    // The script is writing the fields of a form: an OnChange that comes of it is no edit.
    protected bool   m_RzFill;

    // The open pane in pixels, as the shell last sized it.
    protected float  m_RzW;
    protected float  m_RzH;

    // The two strips, the rows of the problems panel, the line the bar shows and its
    // level (0 plain, 1 done, 2 failed), the level of the Hint under way, and the frames
    // left until the open page is fitted once more (texts made this frame have their
    // widths by then).
    protected Widget m_RzBar;
    protected Widget m_RzProbs;
    protected ref OZ_VppFlexRows m_RzProbRows;
    protected string m_RzSaid;
    protected int    m_RzSaidLevel;
    protected int    m_RzSayLevel;
    protected int    m_RzRefit;

    // ------------------------------------------------- Огляд
    // The last list answer as copies made by script, the picked faction (its id), whether
    // the list was asked for, and what the answer said besides the factions.
    protected ref array<ref OZL_AdminOwner> m_ResOwners;
    protected string m_ResPick;
    protected bool   m_ResAsked;
    protected string m_ResCounters;
    protected string m_ResStatics;
    protected ref OZ_VppFlexRows m_OvFacRows;
    protected ref OZ_VppFlexRows m_OvStRows;
    protected ref array<Widget>  m_OvPickChips;
    protected string m_OvPickRest;

    // ------------------------------------------------- Дерево
    // The owner, the branch, the picked node.
    protected string m_TrOwner;
    protected string m_TrBranch;
    protected string m_TrSel;

    // The id the links point at while the id field is typed in: they follow the node to
    // a free id only (RenameTn).
    protected string m_TnRefId;

    // The canvas: the owner's skin, the plan, the branch as the player's window would get
    // it, the cells, the OR marks and their labels, the handle that adds a child.
    protected ref OZL_TreeSkin   m_TrSkin;
    protected string             m_TrSkinId;
    protected ref OZL_TreePlan   m_TrPlan;
    protected ref OZL_BranchView m_TrView;
    protected ref array<Widget>  m_TrCells;
    protected ref array<ref OZL_TreeOrMark> m_TrOrs;
    protected ref array<Widget>  m_TrOrLabels;
    protected Widget             m_TrPlus;

    // Price chips of the cells that wait for their texts' widths (a frame later).
    protected ref array<Widget>  m_TrFlows;
    protected int                m_TrFlowTries;

    // The link mode: on, and from which node ("" -- the parent is not picked yet).
    protected bool   m_TrLink;
    protected string m_TrLinkFrom;

    // The player's preview: the demo state of the faction (OZL_EdTree.DemoState).
    protected int    m_TrDemo;

    // A node dragged along the axis (its tier), and the canvas dragged (its scroll). The
    // mouse is polled from OnUpdate, as the player's window does.
    protected string m_TnDragId;
    protected bool   m_TnDragMoved;
    protected int    m_TnDragX;
    protected int    m_TnDragY;
    protected float  m_TnCellX;
    protected float  m_TnCellY;
    // A click that comes with the release after a drag is no pick: ignored for a few frames.
    protected int    m_TnSkipClick;
    protected bool   m_TrPanDown;
    protected bool   m_TrPanMoved;
    protected int    m_TrPanX;
    protected int    m_TrPanY;
    protected float  m_TrPanH;
    protected float  m_TrPanV;

    // The side lists, the chips of the picked node's price, and where the tail of the
    // node's form stands when the chips take one line (read once, in pixels).
    protected ref OZ_VppFlexRows m_TrOwRows;
    protected ref OZ_VppFlexRows m_TrBrRows;
    protected ref array<Widget>  m_TnChips;
    protected float  m_TnTailY;
    protected float  m_TnFormW;
    protected float  m_TnFormH;

    override void OnCreate(Widget RootW)
    {
        super.OnCreate(RootW);
        if (!M_SUB_WIDGET)
            return;

        m_Ed = new OZL_EdDocs();
        m_RzTab = "";
        m_RzProblems = false;
        m_RzAsked = false;
        m_RzFill = false;
        // The content area as the shell opens the window; OnWindowResized keeps it.
        m_RzW = m_WinW - (DEF_W - CONTENT_W) * UnitScale();
        m_RzH = m_WinH - (DEF_H - CONTENT_H) * UnitScale();
        m_RzSaid = "";
        m_RzSaidLevel = 0;
        m_RzSayLevel = 0;
        m_RzRefit = 0;

        m_ResOwners = new array<ref OZL_AdminOwner>();
        m_ResPick = "";
        m_ResAsked = false;
        m_ResCounters = "";
        m_ResStatics = "";
        m_OvPickChips = new array<Widget>();
        m_OvPickRest = "";

        m_TrOwner = "";
        m_TrBranch = "";
        m_TrSel = "";
        m_TnRefId = "";
        m_TrSkinId = "";
        m_TrCells = new array<Widget>();
        m_TrOrs = new array<ref OZL_TreeOrMark>();
        m_TrOrLabels = new array<Widget>();
        m_TrFlows = new array<Widget>();
        m_TrFlowTries = 0;
        m_TrLink = false;
        m_TrLinkFrom = "";
        m_TrDemo = 0;
        m_TnDragId = "";
        m_TnDragMoved = false;
        m_TnSkipClick = 0;
        m_TrPanDown = false;
        m_TrPanMoved = false;
        m_TnChips = new array<Widget>();
        m_TnTailY = 0;
        m_TnFormW = 0;
        m_TnFormH = 0;

        RzMakeStrips();

        // The rail's pages of the module, each a pane of its own.
        array<string> keys = new array<string>();
        array<string> labels = new array<string>();
        array<string> roots = new array<string>();
        RzPageList(keys, labels, roots);
        for (int k = 0; k < keys.Count(); k++)
        {
            Widget pane = RzMakePane(keys[k], roots[k]);
            if (!pane)
                continue;
            RegisterPage("research", "#STR_OZL_VPP_MOD", RZ_PAGE + keys[k], labels[k], pane, "");
        }

        // A listener of our own: the list and the operations are ours, the core knows
        // nothing of them; it also sees the answers of cfg_set for our files.
        OZ_ClientState.AdminWatch().Insert(this.OnResearchResponse);
    }

    void ~OZ_VppAdminMenu()
    {
        OZ_ClientState.AdminWatch().Remove(this.OnResearchResponse);
    }

    // The rail's pages in their order: key, caption, the root of the page's layout.
    protected void RzPageList(array<string> keys, array<string> labels, array<string> roots)
    {
        keys.Clear();
        labels.Clear();
        roots.Clear();
        keys.Insert("overview");
        labels.Insert("#STR_OZL_VPP_PAGE_OVERVIEW");
        roots.Insert("PaneRzOverview");
        keys.Insert("tree");
        labels.Insert("#STR_OZL_VPP_PAGE_TREE");
        roots.Insert("PaneRzTree");
        keys.Insert("chains");
        labels.Insert("#STR_OZL_VPP_PAGE_CHAINS");
        roots.Insert("PaneRzChains");
        keys.Insert("points");
        labels.Insert("#STR_OZL_VPP_PAGE_POINTS");
        roots.Insert("PaneRzPoints");
        keys.Insert("owners");
        labels.Insert("#STR_OZL_VPP_PAGE_OWNERS");
        roots.Insert("PaneRzOwners");
        keys.Insert("modules");
        labels.Insert("#STR_OZL_VPP_PAGE_MODULES");
        roots.Insert("PaneRzModules");
        keys.Insert("statics");
        labels.Insert("#STR_OZL_VPP_PAGE_STATICS");
        roots.Insert("PaneRzStatics");
        keys.Insert("settings");
        labels.Insert("#STR_OZL_VPP_PAGE_SETTINGS");
        roots.Insert("PaneRzSettings");
    }

    // A page's pane from its layout; null (and a line in the log) when the layout is
    // missing or another file's widgets came for it.
    protected Widget RzMakePane(string key, string rootName)
    {
        string layout = "OpenZone_Research_VPP/gui/layouts/ozl_vpp_" + key + ".layout";
        Widget pane = OZ_VppFlex.Create(layout, M_SUB_WIDGET, rootName);
        if (!pane)
        {
            OZL_Log.Error("research vpp: the page '" + key + "' is left out, its layout did not load: " + layout);
            return null;
        }
        if (pane.GetName() != rootName)
        {
            OZL_Log.Error("research vpp: the page '" + key + "' is left out, " + layout + " gave the root '" + pane.GetName() + "' instead of '" + rootName + "'");
            pane.Unlink();
            return null;
        }
        return pane;
    }

    protected bool IsRzPage(string id)
    {
        return id.IndexOf(RZ_PAGE) == 0;
    }

    // Is one of the module's pages on screen: answers that come while another page is
    // shown must not write into this module's bar.
    protected bool RzShown()
    {
        return IsRzPage(CurrentPane());
    }

    // A stringtable key of the mod in the client's language.
    protected string Tr(string key)
    {
        return Widget.TranslateString(key);
    }

    // Pixels in a layout unit (the shell's UnitScale under the name the pages use).
    protected float Px()
    {
        return UnitScale();
    }

    // ================================================= the strips

    // The draft bar and the problems panel: made once, moved into the content frame beside
    // the pages and laid over them (a page's root has priority 100, the window's confirm
    // strip 200).
    protected void RzMakeStrips()
    {
        m_RzBar = OZ_VppFlex.Create("OpenZone_Research_VPP/gui/layouts/ozl_vpp_bar.layout", M_SUB_WIDGET, "OZL_VppBar");
        if (m_RzBar)
        {
            if (m_Content)
                m_Content.AddChild(m_RzBar);
            m_RzBar.SetSort(150);
            m_RzBar.Show(false);
        }
        else
            OZL_Log.Error("research vpp: the draft bar's layout did not load; the draft cannot be applied from the window");

        m_RzProbs = OZ_VppFlex.Create("OpenZone_Research_VPP/gui/layouts/ozl_vpp_probs.layout", M_SUB_WIDGET, "OZL_VppProbs");
        if (m_RzProbs)
        {
            if (m_Content)
                m_Content.AddChild(m_RzProbs);
            m_RzProbs.SetSort(150);
            m_RzProbs.Show(false);
        }
        else
            OZL_Log.Error("research vpp: the problems panel's layout did not load");
    }

    protected void RzShowStrips(bool on)
    {
        if (m_RzBar)
            m_RzBar.Show(on);
        bool panel = false;
        if (on && m_RzProblems)
            panel = true;
        if (m_RzProbs)
            m_RzProbs.Show(panel);
    }

    // How tall the problems panel is, in units: as many rows as it has problems, one at
    // least and RZ_PROBS_ROWS at most, and two units more, so that a list that fits draws
    // no scrollbar (a scroll area exactly as tall as its content draws one).
    protected float RzProbsHeight()
    {
        int rows = 1;
        if (m_RzProbRows)
            rows = m_RzProbRows.Count();
        if (rows < 1)
            rows = 1;
        if (rows > RZ_PROBS_ROWS)
            rows = RZ_PROBS_ROWS;
        return RZ_PROBS_H - (6 - rows) * 31 + 2;
    }

    // The strips at the bottom of the content area, as wide as it. The window's confirm
    // strip stands above the bar (ConfirmLift).
    protected void RzPlaceStrips()
    {
        if (!M_SUB_WIDGET || !m_Flex)
            return;
        float s = UnitScale();
        float cw = m_WinW - (DEF_W - CONTENT_W) * s;
        float ch = m_WinH - (DEF_H - CONTENT_H) * s;
        if (m_RzBar)
        {
            m_Flex.Resize(m_RzBar, cw, RZ_BAR_H * s, PAGE_W * s, RZ_BAR_H * s);
            m_RzBar.SetPos(0, ch - RZ_BAR_H * s);
            RzFlowBar();
        }
        if (m_RzProbs)
        {
            float ph = RzProbsHeight() * s;
            m_Flex.Resize(m_RzProbs, cw, ph, PAGE_W * s, RZ_PROBS_H * s);
            m_RzProbs.SetPos(0, ch - RZ_BAR_H * s - ph);
            if (m_RzProbRows)
                m_RzProbRows.Fit();
        }
    }

    override float ConfirmLift()
    {
        if (IsRzPage(m_Shown))
            return RZ_BAR_H;
        return super.ConfirmLift();
    }

    // The window changed its size: the content area is w x h pixels now and the shell has
    // sized every pane. The strips follow; the open page fits its lists.
    override void OnWindowResized(float w, float h)
    {
        super.OnWindowResized(w, h);
        if (!M_SUB_WIDGET || !m_Ed)
            return;

        m_RzW = w;
        m_RzH = h;

        RzPlaceStrips();
        if (IsRzPage(m_Shown))
            RzLayPages(m_RzW, m_RzH);
    }

    // The open page after a resize, and once more two frames after it was painted (a text
    // made this frame has its width by then): fit the lists, place what follows a text.
    // This layer: Огляд and Дерево; the later layers add theirs after super.
    protected void RzLayPages(float pw, float ph)
    {
        if (m_RzTab == "overview")
        {
            if (m_OvFacRows)
            {
                m_OvFacRows.Fit();
                OvLayFacRows();
            }
            if (m_OvStRows)
            {
                m_OvStRows.Fit();
                OvLayStatics();
            }
            OvLayPickLine();
            OvLayHeads();
        }
        else if (m_RzTab == "tree")
        {
            if (m_TrOwRows)
                m_TrOwRows.Fit();
            if (m_TrBrRows)
                m_TrBrRows.Fit();
            RzLayTrRows();
            RzLayTree();
            FlowTrSkin();
            LayTnChips();
            RzFitLegend("RzBrLegend", "RzBrGap");
        }
    }

    // A page of the module was shown on the rail.
    override void OnPaneShown(string id)
    {
        super.OnPaneShown(id);
        if (!m_Ed)
            return;
        if (!IsRzPage(id))
        {
            RzShowStrips(false);
            return;
        }

        // The seven files into the core's queue, once per window: AskCfg sends one at a time.
        if (!m_RzAsked)
        {
            m_RzAsked = true;
            array<string> tags = m_Ed.Tags();
            for (int i = 0; i < tags.Count(); i++)
                AskCfg(tags[i]);
        }

        string prefix = RZ_PAGE;
        int skip = prefix.Length();
        m_RzTab = id.Substring(skip, id.Length() - skip);
        m_TrLink = false;
        m_TrLinkFrom = "";
        m_Ed.EndGesture();

        RzShowStrips(true);
        RzPlaceStrips();

        // The factions: Огляд lists them; Дерево and Ланцюги take their names from the answer.
        if (m_RzTab == "overview" || !m_ResAsked)
        {
            m_ResAsked = true;
            AskResearchList();
        }
        RepaintRz();
    }

    protected void AskResearchList()
    {
        Ask(OZL_Const.SECTION, "list", "{}");
    }

    // ================================================= lines for the admin

    // Every line the window says while a research page is open is shown on the draft bar
    // too (the journal and the status bar get it from the shell).
    override void Hint(string t)
    {
        super.Hint(t);
        if (!m_Ed || !RzShown())
            return;
        // An error key of a stringtable (a refusal the shell passes on) is said in red,
        // as the journal files it.
        int level = m_RzSayLevel;
        if (level == 0 && t.IndexOf("#STR_") == 0 && t.IndexOf("ERR") > 0)
            level = 2;
        RzBarSay(t, level);
    }

    // A line with its colour on the bar: 0 plain, 1 done (green, a check), 2 failed (red).
    protected void RzSay(string text, int level)
    {
        m_RzSayLevel = level;
        Hint(text);
        m_RzSayLevel = 0;
    }

    // A line written only while a research page is shown.
    protected void RzHint(string text)
    {
        if (RzShown())
            Hint(text);
    }

    protected void RzHintLevel(string text, int level)
    {
        if (RzShown())
            RzSay(text, level);
    }

    protected void RzBarSay(string text, int level)
    {
        m_RzSaid = text;
        m_RzSaidLevel = level;
        PaintRzSaid();
        RzFlowBar();
    }

    // ================================================= answers

    // An answer of the core's config section other than cfg_set; the later layers take
    // theirs (the settings page: `identity`).
    protected void OnRzConfigAnswer(string op, bool ok, string json, string error)
    {
    }

    void OnResearchResponse(string section, string op, bool ok, string json, string error)
    {
        // The answer to APPLY: the core has said its "applied" already; we need to know
        // WHICH file, and send the next.
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
            RzHintLevel(op + ": " + Words(error), 2);
            return;
        }

        OZL_AdminList l = new OZL_AdminList();
        string err;
        if (!JsonFileLoader<OZL_AdminList>.LoadData(json, l, err))
        {
            string unreadable = Tr("#STR_OZL_VPP_HINT_UNREADABLE");
            RzHintLevel(unreadable + " (" + err + ")", 2);
            return;
        }

        // The strings are taken at once: rows are built below, and the envelope was made
        // by the serializer (the header of the core's OZ_ConfigBase).
        string statics = l.Statics;
        string counters = l.Counters;

        // A copy made by script: what came lives only until it is parsed. The names as
        // they were, to tell whether the side lists of the other pages must follow.
        string namesWere = RzOwnerNames();
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
        if (!PickedOwnerRow())
            m_ResPick = "";
        m_ResCounters = counters;
        m_ResStatics = statics;

        if (RzShown())
        {
            if (m_RzTab == "overview")
                RepaintOverview();
            else if (RzOwnerNames() != namesWere)
                RepaintRzPage(m_RzTab);
        }

        // After "reload the configs" the files on the server may be others: a draft with
        // no edits takes them, one with edits counts its changes from the new ones.
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
            RzHintLevel(op + ": " + said, 1);
        }
    }

    // A file of the draft came from the server (the core's cfg_get).
    override void OnCfgText(string name, string body)
    {
        super.OnCfgText(name, body);
        if (!m_Ed || !m_Ed.Owns(name))
            return;

        string err;
        if (!m_Ed.OnFetched(name, body, err))
        {
            string bad = Tr("#STR_OZL_ED_HINT_BAD_FILE");
            RzHintLevel(bad + name + " (" + err + ")", 2);
        }
        RepaintRz();
    }

    // ================================================= the pages

    // Fills the open page. The later layers (chains, the config files, settings) take
    // their keys and hand the rest to super.
    protected void RepaintRzPage(string tab)
    {
        if (tab == "overview")
            RepaintOverview();
        else if (tab == "tree")
            RepaintTree(true);
    }

    // Everything that depends on the draft: the open page, the bar, the overview's line.
    protected void RepaintRz()
    {
        if (!M_SUB_WIDGET || !m_Ed)
            return;

        if (RzShown())
        {
            RepaintRzPage(m_RzTab);
            m_RzRefit = 2;
        }
        PaintRzBar();
        PaintSummary();
    }

    // ------------------------------------------------- small things for widgets

    protected void SetBtnText(string btn, string text, int color)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(btn + "Text"));
        if (!t)
            return;
        t.SetText(text);
        t.SetColor(color);
    }

    // A button's caption, ground and frame (<btn>Text, <btn>Bg, <btn>Edge); a colour of 0
    // leaves that part as it is.
    protected void PaintBtn(string btn, string text, int textColor, int bgColor, int edgeColor)
    {
        SetBtnText(btn, text, textColor);
        if (bgColor != 0)
            OZ_VppFlex.Paint(M_SUB_WIDGET, btn + "Bg", bgColor);
        if (edgeColor != 0)
            OZ_VppFlex.Paint(M_SUB_WIDGET, btn + "Edge", edgeColor);
    }

    // One half of a pair that says which of two values is in force (on the head ground):
    // the one in force on the accent's soft ground with bright words.
    protected void RzSeg(string btn, bool on)
    {
        if (on)
        {
            OZ_VppFlex.Paint(M_SUB_WIDGET, btn + "Bg", OZL_Metal.PICK_HEAD);
            SetColorOf(btn + "Text", OZL_Metal.TEXT);
            return;
        }
        OZ_VppFlex.Paint(M_SUB_WIDGET, btn + "Bg", OZL_Metal.HEAD);
        SetColorOf(btn + "Text", OZL_Metal.MUTED);
    }

    // A tick box of a converted page: a button with its frame (<name>Edge), its ground
    // (<name>Bg) and its mark (<name>Mark). On: filled in `lit` (the colour the board
    // draws that box in), the mark shown; off: the cell's ground in a faint frame, no mark.
    protected void RzPaintTick(string name, bool on, int lit)
    {
        Widget box = M_SUB_WIDGET.FindAnyWidget(name);
        if (!box)
            return;
        int rim = OZL_Metal.FAINT;
        int ground = OZL_Metal.CELL;
        if (on)
        {
            rim = lit;
            ground = lit;
        }
        string markName = name + "Mark";
        if (box.FindAnyWidget(name + "Edge"))
        {
            OZ_VppFlex.Paint(box, name + "Edge", rim);
            OZ_VppFlex.Paint(box, name + "Bg", ground);
            Widget mark = box.FindAnyWidget(markName);
            if (mark)
                mark.Show(on);
            return;
        }

        // A layout written before the parts had names: the frame is the first child, the
        // ground the next.
        int n = 0;
        Widget part = box.GetChildren();
        while (part)
        {
            if (part.GetName() == markName)
            {
                part.Show(on);
            }
            else
            {
                if (n == 0)
                    part.SetColor(rim);
                else
                    part.SetColor(ground);
                n++;
            }
            part = part.GetSibling();
        }
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

    // The same inside a row (or any part of the window).
    protected void RzRowText(Widget row, string name, string text, int color)
    {
        if (!row)
            return;
        TextWidget t = TextWidget.Cast(row.FindAnyWidget(name));
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

    // A widget's place in pixels.
    protected void MoveW(string name, float x, float y)
    {
        Widget m = M_SUB_WIDGET.FindAnyWidget(name);
        if (m)
            m.SetPos(x, y);
    }

    // A widget moved along its line: its height on the line stays.
    protected void RzSetX(Widget w, float x)
    {
        if (!w)
            return;
        float px;
        float py;
        w.GetPos(px, py);
        w.SetPos(x, py);
    }

    // A text as wide as its words (a TextWidget cuts its text at its own box); returns the
    // width of the words in pixels.
    protected int RzFitText(TextWidget t)
    {
        if (!t)
            return 0;
        int tw = OZ_VppFlex.TextWidth(t);
        float w;
        float h;
        t.GetSize(w, h);
        t.SetSize(tw + 2, h);
        return tw;
    }

    // Two texts of one line and one parent: the first as wide as its words (the layout
    // sized it for the board's sample), the second `gap` units after its last letter and
    // ending where it ended. A text that has no width yet leaves both as they are.
    protected void RzFlowAfter(string first, string second, float gap)
    {
        TextWidget a = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(first));
        Widget b = M_SUB_WIDGET.FindAnyWidget(second);
        if (!a || !b)
            return;
        if (OZ_VppFlex.TextWidth(a) <= 0)
            return;
        float ax;
        float ay;
        float bx;
        float by;
        float bw;
        float bh;
        a.GetPos(ax, ay);
        b.GetPos(bx, by);
        b.GetSize(bw, bh);
        float end = bx + bw;
        int tw = RzFitText(a);
        float at = ax + tw + gap * UnitScale();
        float room = end - at;
        if (room < 1)
            room = 1;
        b.SetPos(at, by);
        b.SetSize(room, bh);
    }

    // A caption that stands on a box's frame (a legend): as wide as its words, and the
    // frame is broken under it -- the gap is the words and six units of air on each side.
    // The gap is the frame <gapName> with its ground <gapName>Bg.
    protected void RzFitLegend(string capName, string gapName)
    {
        TextWidget cap = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(capName));
        Widget gap = M_SUB_WIDGET.FindAnyWidget(gapName);
        if (!cap)
            return;
        if (OZ_VppFlex.TextWidth(cap) <= 0)
            return;
        int tw = RzFitText(cap);
        if (!gap)
            return;
        float w;
        float h;
        gap.GetSize(w, h);
        w = tw + 12 * UnitScale();
        gap.SetSize(w, h);
        Widget ground = M_SUB_WIDGET.FindAnyWidget(gapName + "Bg");
        if (ground)
            ground.SetSize(w, h);
    }

    // A converted button made as wide as its caption: the caption stands textX pixels in,
    // pad pixels stay after it. Its parts are <name>Edge, <name>Bg and <name>Text. Returns
    // the button's width.
    protected float RzHugBtn(string name, float textX, float pad)
    {
        Widget b = M_SUB_WIDGET.FindAnyWidget(name);
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(name + "Text"));
        if (!b || !t)
            return 0;
        float s = UnitScale();
        float w;
        float h;
        b.GetSize(w, h);
        int tw = RzFitText(t);
        RzSetX(t, textX);
        w = textX + tw + pad;
        b.SetSize(w, h);
        Widget edge = M_SUB_WIDGET.FindAnyWidget(name + "Edge");
        if (edge)
            edge.SetSize(w, h);
        Widget bg = M_SUB_WIDGET.FindAnyWidget(name + "Bg");
        if (bg)
            bg.SetSize(w - 2 * s, h - 2 * s);
        return w;
    }

    // A row of a side list (owners, branches, lines): its ground and its accent bar. A
    // button always keeps an opaque child over it (a bare one paints a light box under the
    // pointer), so the ground of a row that is not picked takes the column's colour.
    protected void RzLitRow(Widget row, string rootName, bool picked)
    {
        if (!row)
            return;
        Widget bar = row.FindAnyWidget(rootName + "Bar");
        if (bar)
            bar.Show(picked);
        if (picked)
            OZ_VppFlex.Paint(row, rootName + "Bg", OZL_Metal.PICK_PANEL);
        else
            OZ_VppFlex.Paint(row, rootName + "Bg", OZL_Metal.PANEL);
    }

    // The words of a side row along its line: the id, a dash and a name from the left, a
    // tail (a count, a window's name) written from the right; the name takes what is left.
    // rowW is the row's width in units; a part that the row has not is "".
    protected void RzLaySideRow(Widget row, string idName, string dashName, string nameName, string tailName, float rowW)
    {
        if (!row)
            return;
        float s = UnitScale();
        float x = 10 * s;
        int tw;
        TextWidget id = TextWidget.Cast(row.FindAnyWidget(idName));
        if (id)
        {
            tw = RzFitText(id);
            RzSetX(id, x);
            x = x + tw + 6 * s;
        }
        Widget dash = row.FindAnyWidget(dashName);
        if (dash && dash.IsVisible())
        {
            RzSetX(dash, x);
            x = x + 17 * s;
        }
        float right = (rowW - 10) * s;
        TextWidget tail = TextWidget.Cast(row.FindAnyWidget(tailName));
        if (tail)
        {
            tw = RzFitText(tail);
            right = right - tw;
            RzSetX(tail, right);
            right = right - 8 * s;
        }
        TextWidget name = TextWidget.Cast(row.FindAnyWidget(nameName));
        if (name)
        {
            float w;
            float h;
            name.GetSize(w, h);
            w = right - x;
            if (w < 0)
                w = 0;
            RzSetX(name, x);
            name.SetSize(w, h);
        }
    }

    // A faction's name as the server last told it (the list answer), else as the client's
    // own source of factions knows it; "" when nobody names it.
    protected string RzOwnerName(string id)
    {
        for (int i = 0; i < m_ResOwners.Count(); i++)
        {
            if (m_ResOwners[i] && m_ResOwners[i].Id == id)
            {
                if (m_ResOwners[i].Name == id)
                    return "";
                return m_ResOwners[i].Name;
            }
        }
        OZ_IdentityService svc = OZ_Identity.Get();
        if (!svc)
            return "";
        string name = svc.FactionName(id);
        if (name == id)
            return "";
        return name;
    }

    // Every faction's id and name in one string: two answers that name the same compare equal.
    protected string RzOwnerNames()
    {
        string all = "";
        for (int i = 0; i < m_ResOwners.Count(); i++)
        {
            if (m_ResOwners[i])
                all = all + m_ResOwners[i].Id + "=" + m_ResOwners[i].Name + ";";
        }
        return all;
    }

    // A dashed line on a canvas (pixels).
    protected void RzDashLine(CanvasWidget cv, float x1, float y1, float x2, float y2, float width, int color, float dashOn, float dashOff)
    {
        float dx = x2 - x1;
        float dy = y2 - y1;
        float len = Math.Sqrt(dx * dx + dy * dy);
        if (!cv || len <= 0 || dashOn <= 0)
            return;
        float ux = dx / len;
        float uy = dy / len;
        float at = 0;
        int guard = 0;
        while (at < len && guard < 600)
        {
            float stop = at + dashOn;
            if (stop > len)
                stop = len;
            cv.DrawLine(x1 + ux * at, y1 + uy * at, x1 + ux * stop, y1 + uy * stop, width, color);
            at = at + dashOn + dashOff;
            guard++;
        }
    }

    // ================================================= the draft bar

    // The bar from the draft: how many files changed, the problems, what each button
    // would do now.
    protected void PaintRzBar()
    {
        if (!M_SUB_WIDGET || !m_Ed)
            return;

        // Every edit of the draft ends here: the open page is fitted once more two frames
        // on (RzLayPages), when the texts it wrote have their widths.
        if (RzShown())
            m_RzRefit = 2;
        if (!m_RzBar)
            return;

        int changed = m_Ed.Changed();
        string state;
        int stateColor = OZL_Metal.TEXT;
        bool dot = false;
        string word;
        if (!m_Ed.AllLoaded())
        {
            word = Tr("#STR_OZL_ED_STATUS_LOADING");
            state = word + m_Ed.LoadedCount().ToString() + "/" + m_Ed.Tags().Count().ToString();
            stateColor = OZL_Metal.MUTED;
        }
        else if (changed > 0)
        {
            word = Tr("#STR_OZL_ED_STATUS_CHANGED");
            state = word + changed.ToString();
            stateColor = OZL_Metal.ALERT;
            dot = true;
        }
        else
        {
            state = Tr("#STR_OZL_ED_STATUS_CLEAN");
        }
        SetLabel("RzStatus", state, stateColor);
        Widget dotW = M_SUB_WIDGET.FindAnyWidget("RzStatusDot");
        if (dotW)
        {
            dotW.Show(dot);
            dotW.SetColor(stateColor);
        }

        // The problems button: clean, warnings, errors; its frame takes the words' colour
        // while the panel is open.
        int errs = m_Ed.Errors();
        int warns = m_Ed.Warnings();
        string probs;
        int probInk = OZL_Metal.OK;
        int probRim = OZL_Metal.EDGE;
        int probGround = OZL_Metal.HEAD;
        if (errs > 0)
        {
            word = Tr("#STR_OZL_ED_PROB_ERRORS");
            probs = word + errs.ToString();
            if (warns > 0)
                probs = probs + " +" + warns.ToString();
            probInk = OZL_Metal.BAD;
            probRim = OZL_Metal.BAD;
            probGround = OZL_Metal.BAD_SOFT;
        }
        else if (warns > 0)
        {
            word = Tr("#STR_OZL_ED_PROB_WARNINGS");
            probs = word + warns.ToString();
            probInk = OZL_Metal.ALERT;
        }
        else
        {
            probs = Tr("#STR_OZL_ED_PROB_NONE");
        }
        if (m_RzProblems)
            probRim = probInk;
        PaintBtn("BtnRzProblems", probs, probInk, probGround, probRim);
        bool clean = (errs == 0 && warns == 0);
        ShowW("RzProbSignOk", clean);
        ShowW("RzProbSignBad", !clean);
        SetColorOf("RzProbSignBadIcon", probInk);

        // Undo and redo: raised while there is a step to take.
        RzPaintStep("BtnRzUndo", m_Ed.CanUndo());
        RzPaintStep("BtnRzRedo", m_Ed.CanRedo());

        int discardInk = OZL_Metal.FAINT;
        int discardRim = OZL_Metal.EDGE;
        if (changed > 0)
        {
            discardInk = OZL_Metal.BAD;
            discardRim = OZL_Metal.BAD;
        }
        SetColorOf("BtnRzDiscardText", discardInk);
        OZ_VppFlex.Paint(M_SUB_WIDGET, "BtnRzDiscardEdge", discardRim);

        // APPLY is the one lit button: the accent while there is something to send and
        // nothing stops it, a lock in a red frame while errors keep it shut, plain with
        // nothing to do.
        string apply = Tr("#STR_OZL_ED_BTN_APPLY");
        int applyInk = OZL_Metal.FAINT;
        int applyGround = OZL_Metal.RAISED;
        int applyRim = OZL_Metal.EDGE;
        bool locked = false;
        if (changed > 0)
        {
            apply = apply + " · " + changed.ToString();
            if (errs == 0)
            {
                applyInk = OZL_Metal.INK;
                applyGround = OZL_Metal.ACCENT;
                applyRim = OZL_Metal.ACCENT;
            }
            else
            {
                applyInk = OZL_Metal.MUTED;
                applyGround = OZL_Metal.HEAD;
                applyRim = OZL_Metal.BAD;
                locked = true;
            }
        }
        PaintBtn("BtnRzApply", apply, applyInk, applyGround, applyRim);
        ShowW("BtnRzApplyLock", locked);
        SetColorOf("BtnRzApplyLockIcon", applyInk);

        PaintRzSaid();
        RzFlowBar();

        // The panel follows every edit while it is open: the pages stay usable under it,
        // so the draft changes while it is read.
        RepaintProblems();
    }

    protected void RzPaintStep(string btn, bool can)
    {
        int ink = OZL_Metal.FAINT;
        int ground = OZL_Metal.HEAD;
        if (can)
        {
            ink = OZL_Metal.TEXT;
            ground = OZL_Metal.RAISED;
        }
        SetColorOf(btn + "Text", ink);
        SetColorOf(btn + "Icon", ink);
        OZ_VppFlex.Paint(M_SUB_WIDGET, btn + "Bg", ground);
    }

    // The line in the middle of the bar: the last thing said on a research page, or what
    // the bar is for while nothing was said.
    protected void PaintRzSaid()
    {
        if (!m_RzBar)
            return;
        string text = m_RzSaid;
        int ink = OZL_Metal.MUTED;
        if (text == "")
            text = "#STR_OZL_VPP_BAR_IDLE";
        else if (m_RzSaidLevel == 1)
            ink = OZL_Metal.OK;
        else if (m_RzSaidLevel == 2)
            ink = OZL_Metal.BAD;
        SetLabel("ResHint", text, ink);
        bool check = false;
        if (m_RzSaidLevel == 1 && m_RzSaid != "")
            check = true;
        ShowW("RzHintOk", check);
    }

    // The bar's parts along it: the state and the problems button from the left, each as
    // wide as its words; the four buttons from the right, the last as wide as its words;
    // the line takes what is between. The numbers are ozl_vpp_bar.layout's, in units.
    protected void RzFlowBar()
    {
        if (!m_RzBar)
            return;
        float s = UnitScale();
        float bw;
        float bh;
        m_RzBar.GetSize(bw, bh);
        if (bw <= 0)
            return;

        // From the right: apply (its lock, when shown, stands before its words), discard,
        // redo, undo, 12 units apart, 24 from the edge.
        float lead = 19 * s;
        Widget shut = M_SUB_WIDGET.FindAnyWidget("BtnRzApplyLock");
        if (shut && shut.IsVisible())
            lead = 40 * s;
        float w = RzHugBtn("BtnRzApply", lead, 19 * s);
        float right = bw - 24 * s;
        MoveW("BtnRzApply", right - w, 13 * s);
        right = right - w - 12 * s;
        right = RzBarPut("BtnRzDiscard", right);
        right = RzBarPut("BtnRzRedo", right);
        right = RzBarPut("BtnRzUndo", right);

        // From the left: the state under its caption (a dot before it while files are
        // changed), then the problems button.
        TextWidget state = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzStatus"));
        Widget dot = M_SUB_WIDGET.FindAnyWidget("RzStatusDot");
        float left = 24 * s;
        if (state)
        {
            float sx = 24 * s;
            if (dot && dot.IsVisible())
                sx = 36 * s;
            int stateW = RzFitText(state);
            RzSetX(state, sx);
            left = sx + stateW;
        }
        if (left < 164 * s)
            left = 164 * s;
        left = left + 12 * s;
        w = RzHugBtn("BtnRzProblems", 37 * s, 13 * s);
        MoveW("BtnRzProblems", left, 13 * s);
        left = left + w + 12 * s;

        // The line: its check, when shown, before its words.
        Widget box = M_SUB_WIDGET.FindAnyWidget("RzHintBox");
        TextWidget hint = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("ResHint"));
        if (!box || !hint)
            return;
        float room = right - left;
        if (room < 0)
            room = 0;
        box.SetPos(left, 21 * s);
        box.SetSize(room, 20 * s);
        float hx = 0;
        Widget check = M_SUB_WIDGET.FindAnyWidget("RzHintOk");
        if (check && check.IsVisible())
            hx = 23 * s;
        float hw;
        float hh;
        hint.GetSize(hw, hh);
        RzSetX(hint, hx);
        hw = room - hx;
        if (hw < 0)
            hw = 0;
        hint.SetSize(hw, hh);
    }

    // A button of the bar put with its right edge at `right`; returns where the next one's
    // right edge is.
    protected float RzBarPut(string name, float right)
    {
        Widget b = M_SUB_WIDGET.FindAnyWidget(name);
        if (!b)
            return right;
        float w;
        float h;
        b.GetSize(w, h);
        RzSetX(b, right - w);
        return right - w - 12 * UnitScale();
    }

    // What the draft holds, for Огляд (what the server reads is in the tiles above it).
    protected void PaintSummary()
    {
        if (!M_SUB_WIDGET || !m_Ed)
            return;
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzSummary"));
        if (!t)
            return;
        string word;
        if (!m_Ed.AllLoaded())
        {
            word = Tr("#STR_OZL_ED_STATUS_LOADING");
            t.SetText(word + m_Ed.LoadedCount().ToString() + "/" + m_Ed.Tags().Count().ToString());
            return;
        }

        OZL_PointTypes pt = OZL_PointTypes.Cast(m_Ed.Doc(OZL_Config.TAG_POINT_TYPES).Obj);
        OZL_Owners     ow = OZL_Owners.Cast(m_Ed.Doc(OZL_Config.TAG_OWNERS).Obj);
        OZL_Rules      ru = OZL_Rules.Cast(m_Ed.Doc(OZL_Config.TAG_RULES).Obj);
        OZL_TreeConfig tr = OZL_TreeConfig.Cast(m_Ed.Doc(OZL_Config.TAG_TREE).Obj);
        OZL_Modules    mo = OZL_Modules.Cast(m_Ed.Doc(OZL_Config.TAG_MODULES).Obj);
        OZL_StaticsConfig sc = OZL_StaticsConfig.Cast(m_Ed.Doc(OZL_Config.TAG_STATICS).Obj);
        if (!pt || !ow || !ru || !tr || !mo || !sc)
            return;

        // The order of the tiles: types, owners, rules, nodes, modules, statics.
        word = Tr("#STR_OZL_VPP_OV_DRAFT_SHORT");
        string sum = word + pt.PointTypes.Count().ToString() + " / " + ow.Owners.Count().ToString();
        sum = sum + " / " + ru.Count().ToString() + " / " + tr.NodeCount().ToString();
        sum = sum + " / " + mo.Modules.Count().ToString() + " / " + sc.Entries.Count().ToString();
        t.SetText(sum);
    }

    // ================================================= the problems panel

    // The problems of the draft, errors first (they keep APPLY shut), a row each.
    protected void RepaintProblems()
    {
        if (!m_RzProblems || !m_RzProbs || !m_Ed)
            return;
        Widget host = m_RzProbs.FindAnyWidget("RzProbRows");
        if (!host)
            return;
        if (!m_RzProbRows)
            m_RzProbRows = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_prob_row.layout", "OZL_VppProbRow", 1312, 28);

        m_RzProbRows.Clear();
        array<string> probs = m_Ed.Problems();
        Widget row;
        if (probs.Count() == 0)
        {
            row = m_RzProbRows.Add("");
            if (row)
            {
                Widget badge = row.FindAnyWidget("ProbBadge");
                if (badge)
                    badge.Show(false);
                RzRowText(row, "ProbText", "#STR_OZL_ED_PROB_CLEAN", OZL_Metal.OK);
            }
        }
        else
        {
            string markE = Tr("#STR_OZL_ED_PROB_MARK_ERROR");
            markE = markE.Trim();
            string markW = Tr("#STR_OZL_ED_PROB_MARK_WARN");
            markW = markW.Trim();
            int i;
            int shown = 0;
            for (i = 0; i < probs.Count(); i++)
            {
                if (!OZL_EdCodec.IsError(probs[i]) || shown >= RZ_LIST_MAX)
                    continue;
                row = m_RzProbRows.Add(i.ToString());
                if (row)
                    RzProbRow(row, markE, probs[i], OZL_Metal.BAD, OZL_Metal.BAD_CHIP);
                shown++;
            }
            for (i = 0; i < probs.Count(); i++)
            {
                if (OZL_EdCodec.IsError(probs[i]) || shown >= RZ_LIST_MAX)
                    continue;
                row = m_RzProbRows.Add(i.ToString());
                if (row)
                    RzProbRow(row, markW, probs[i], OZL_Metal.ALERT, OZL_Metal.WARN_CHIP);
                shown++;
            }
        }

        // The panel is as tall as its rows: placed again, then the rows fitted.
        RzPlaceStrips();
    }

    protected void RzProbRow(Widget row, string mark, string text, int ink, int ground)
    {
        RzRowText(row, "ProbMark", mark, ink);
        OZ_VppFlex.Paint(row, "ProbBadgeBg", ground);
        RzRowText(row, "ProbText", text, OZL_Metal.TEXT);
    }

    // The problems button and the panel's own close: the panel opens over the bottom of
    // the open page, or goes.
    protected void RzShowProblems(bool open)
    {
        m_RzProblems = open;
        bool panel = false;
        if (open && IsRzPage(m_Shown))
            panel = true;
        if (m_RzProbs)
            m_RzProbs.Show(panel);
        PaintRzBar();
    }

    // ================================================= the draft's actions

    protected void RzUndo(bool redo)
    {
        string tag;
        bool done;
        if (redo)
            done = m_Ed.Redo(tag);
        else
            done = m_Ed.Undo(tag);

        string word;
        if (!done)
        {
            if (redo)
                Hint(Tr("#STR_OZL_ED_HINT_REDO_EMPTY"));
            else
                Hint(Tr("#STR_OZL_ED_HINT_UNDO_EMPTY"));
            return;
        }

        RepaintRz();
        if (redo)
            word = Tr("#STR_OZL_ED_HINT_REDONE");
        else
            word = Tr("#STR_OZL_ED_HINT_UNDONE");
        Hint(word + tag);
    }

    // DISCARD asks on the window's confirm strip and says which files lose their edits;
    // the yes comes to OnConfirmed -> RzDiscardNow.
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
        RepaintRz();
        Hint(Tr("#STR_OZL_ED_HINT_DISCARDED"));
    }

    // The confirm strip's yes. Research's actions start with "rz:"; the later layers take
    // theirs (rz:rudel:, rz:ptdel:, rz:cfgdel:) before they call super.
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
        string word;
        if (action.IndexOf("rz:reset:") == 0)
        {
            string owner = action.Substring(9, action.Length() - 9);
            Ask(OZL_Const.SECTION, "reset:" + owner, "{}");
            word = Tr("#STR_OZL_VPP_RESETTING");
            Hint(word + owner);
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

    // APPLY: the changed files one at a time, in the order of OZL_EdDocs; the draft's
    // errors keep it shut -- the server would drop what stands on them.
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
            RzSay(Tr("#STR_OZL_ED_HINT_FIX_FIRST"), 2);
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
        string word = Tr("#STR_OZL_ED_HINT_APPLYING");
        RzHint(word + tag);
    }

    protected void OnRzApplied(string tag, bool ok, string error)
    {
        m_Ed.ApplyDone(tag, ok);
        string word;
        if (!ok)
        {
            word = Tr("#STR_OZL_ED_HINT_REFUSED");
            RzHintLevel(tag + word + " (" + Words(error) + ")", 2);
            RepaintRz();
            return;
        }

        SendNextRz();
        if (m_Ed.Applying())
        {
            RepaintRz();
            return;
        }

        // All of them went. The server wrote the files again from what it parsed
        // (Validate, a backup), so its text is shown: what was applied is read again.
        array<string> done = m_Ed.Applied();
        m_Ed.ClearHistory();
        string names = "";
        for (int i = 0; i < done.Count(); i++)
        {
            AskCfg(done[i]);
            if (names != "")
                names = names + ", ";
            names = names + done[i];
        }
        RepaintRz();
        word = Tr("#STR_OZL_ED_HINT_APPLIED");
        string reread = Tr("#STR_OZL_VPP_BAR_REREAD");
        RzHintLevel(word + done.Count().ToString() + " · " + names + reread, 1);
    }

    // ================================================= the draft's files

    protected OZL_PointTypes DraftPointTypes()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_POINT_TYPES);
        if (!d || !d.Loaded)
            return null;
        return OZL_PointTypes.Cast(d.Obj);
    }

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

    // ================================================= Огляд

    protected OZL_AdminOwner PickedOwnerRow()
    {
        if (m_ResPick == "")
            return null;
        for (int i = 0; i < m_ResOwners.Count(); i++)
        {
            if (m_ResOwners[i] && m_ResOwners[i].Id == m_ResPick)
                return m_ResOwners[i];
        }
        return null;
    }

    protected string PickedOwner()
    {
        if (!PickedOwnerRow())
            return "";
        return m_ResPick;
    }

    // The page from the last list answer and the draft's point types (the colours of the
    // pools).
    protected void RepaintOverview()
    {
        if (!M_SUB_WIDGET)
            return;
        RepaintOwners();
        PaintPicked();
        PaintCounters(m_ResCounters);
        PaintStatics(m_ResStatics);
        PaintSummary();
        OvLayHeads();
    }

    // "anomaly=4, protection=2" (OZL_Points.Describe) into types and amounts; "empty" and
    // "?" give none.
    protected void OvPool(string pool, array<string> types, array<string> amounts)
    {
        types.Clear();
        amounts.Clear();
        if (pool == "" || pool == "empty" || pool == "?")
            return;
        array<string> parts = new array<string>();
        pool.Split(",", parts);
        for (int i = 0; i < parts.Count(); i++)
        {
            string p = parts[i];
            p = p.Trim();
            int eq = p.IndexOf("=");
            if (eq <= 0)
                continue;
            types.Insert(p.Substring(0, eq));
            amounts.Insert(p.Substring(eq + 1, p.Length() - eq - 1));
        }
    }

    // A chip of a pool into `box`: a square in the type's colour and "type amount". A type
    // the draft's point types have not is a hollow square; type "" is words alone. The
    // chip's userID says which: 0 words, 1 a known type, 2 a type that is gone.
    protected Widget OvAddChip(Widget box, string type, string text, int ink)
    {
        Widget chip = OZ_VppFlex.Create("OpenZone_Research_VPP/gui/layouts/ozl_vpp_pool_chip.layout", box, "OZL_PoolChip");
        if (!chip)
            return null;
        chip.SetFlags(WidgetFlags.IGNOREPOINTER);
        RzRowText(chip, "PoolText", text, ink);
        int mark = 0;
        if (type == "")
        {
            Widget dot = chip.FindAnyWidget("PoolDot");
            if (dot)
                dot.Show(false);
        }
        else
        {
            OZL_PointTypes pts = DraftPointTypes();
            OZL_PointType pt = null;
            if (pts)
                pt = pts.Find(type);
            mark = 2;
            if (pt)
            {
                int c = OZL_PointTypes.ColorArgb(pt.Color);
                OZ_VppFlex.Paint(chip, "PoolDotEdge", c);
                OZ_VppFlex.Paint(chip, "PoolDotBg", c);
                mark = 1;
            }
            else
                OZ_VppFlex.Paint(chip, "PoolDotEdge", OZL_Metal.MUTED);
        }
        chip.SetUserID(mark);
        return chip;
    }

    // One chip as wide as its words; returns its width in pixels. `ground` is what shows
    // through a hollow square.
    protected float OvHugChip(Widget chip, int ground)
    {
        float s = UnitScale();
        float lead = 16 * s;
        if (chip.GetUserID() == 0)
            lead = 0;
        if (chip.GetUserID() == 2)
            OZ_VppFlex.Paint(chip, "PoolDotBg", ground);
        TextWidget t = TextWidget.Cast(chip.FindAnyWidget("PoolText"));
        int tw = 0;
        if (t)
        {
            tw = RzFitText(t);
            RzSetX(t, lead);
        }
        float w = lead + tw + 2;
        chip.SetSize(w, 15 * s);
        return w;
    }

    protected void RepaintOwners()
    {
        Widget host = M_SUB_WIDGET.FindAnyWidget("RzOvFacRows");
        if (!host)
            return;
        if (!m_OvFacRows)
            m_OvFacRows = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_ov_fac_row.layout", "OZL_OvFacRow", 567, 69);

        m_OvFacRows.Clear();
        int shown = 0;
        for (int i = 0; i < m_ResOwners.Count(); i++)
        {
            OZL_AdminOwner o = m_ResOwners[i];
            if (!o || shown >= RZ_LIST_MAX)
                continue;
            Widget row = m_OvFacRows.Add(o.Id);
            if (!row)
                break;
            OvFillFacRow(row, o);
            shown++;
        }
        m_OvFacRows.Fit();
        OvLayFacRows();

        string entries = Tr("#STR_OZL_VPP_OV_FAC_COUNT");
        string who = Tr("#STR_OZL_VPP_OV_FAC_WHO");
        string count = entries + m_ResOwners.Count().ToString() + who;
        if (m_ResOwners.Count() > shown)
        {
            string first = Tr("#STR_OZL_VPP_SHOWN_FIRST");
            count = count + first + shown.ToString();
        }
        SetLabel("RzOvFacCount", count, 0);
    }

    // A faction's row: its id and name, its pool as chips, its done nodes and its
    // projects under way.
    protected void OvFillFacRow(Widget row, OZL_AdminOwner o)
    {
        RzRowText(row, "OvFacSlug", o.Id, OZL_Metal.TEXT);
        // A faction nobody names (the registry answers with the id itself, or with
        // nothing) says so in the name's place.
        bool unnamed = false;
        if (o.Name == "" || o.Name == o.Id)
            unnamed = true;
        if (unnamed)
            RzRowText(row, "OvFacName", "#STR_OZL_VPP_OV_NO_NAME", OZL_Metal.MUTED);
        else
            RzRowText(row, "OvFacName", o.Name, OZL_Metal.TEXT);

        string done = "-";
        string active = "-";
        if (o.Known == 1)
        {
            done = o.Completed.ToString();
            active = o.Active.ToString();
        }
        RzRowText(row, "OvFacDone", done, OZL_Metal.TEXT);
        RzRowText(row, "OvFacActive", active, OZL_Metal.MUTED);

        Widget pool = row.FindAnyWidget("OvFacPool");
        if (!pool)
            return;
        if (o.Known != 1)
        {
            OvAddChip(pool, "", "#STR_OZL_VPP_OV_NO_STATE", OZL_Metal.FAINT);
            return;
        }
        array<string> types = new array<string>();
        array<string> amounts = new array<string>();
        OvPool(o.Pool, types, amounts);
        if (types.Count() == 0)
        {
            OvAddChip(pool, "", "#STR_OZL_VPP_OV_EMPTY", OZL_Metal.MUTED);
            return;
        }
        for (int i = 0; i < types.Count(); i++)
            OvAddChip(pool, types[i], types[i] + " " + amounts[i], OZL_Metal.TEXT);
    }

    // Every faction's row laid out: the pool's chips wrap inside their column and the row
    // is as tall as they need (42 units at least), its words stand in the middle of it;
    // the picked row is lit. The numbers are ozl_vpp_ov_fac_row.layout's, in units.
    protected void OvLayFacRows()
    {
        if (!m_OvFacRows)
            return;
        for (int i = 0; i < m_OvFacRows.Count(); i++)
            OvLayFacRow(m_OvFacRows.Row(i), m_OvFacRows.Key(i) == m_ResPick);

        Widget host = m_OvFacRows.Host();
        if (!host)
            return;
        host.Update();
        ScrollWidget sc = ScrollWidget.Cast(host.GetParent());
        if (sc)
            sc.Update();
    }

    protected void OvLayFacRow(Widget row, bool picked)
    {
        if (!row)
            return;
        float s = UnitScale();
        int rim = OZL_Metal.HEAD;
        int ground = OZL_Metal.HEAD;
        if (picked)
        {
            rim = OZL_Metal.ACCENT;
            ground = OZL_Metal.PICK_PANEL;
        }
        OZ_VppFlex.Paint(row, "OZL_OvFacRowEdge", rim);
        OZ_VppFlex.Paint(row, "OZL_OvFacRowBg", ground);

        // The chips of the pool, wrapped at the column's 200 units.
        Widget pool = row.FindAnyWidget("OvFacPool");
        int lines = 1;
        float x = 0;
        float y = 0;
        if (pool)
        {
            Widget chip = pool.GetChildren();
            while (chip)
            {
                float cw = OvHugChip(chip, ground);
                if (x > 0 && x + cw > 200 * s)
                {
                    x = 0;
                    y = y + 19 * s;
                    lines++;
                }
                chip.SetPos(x, y);
                x = x + cw + 12 * s;
                chip = chip.GetSibling();
            }
        }
        float poolH = (lines * 15 + (lines - 1) * 4) * s;
        float h = poolH + 16 * s;
        if (h < 42 * s)
            h = 42 * s;

        float rowW;
        float rowH;
        row.GetSize(rowW, rowH);
        row.SetSize(rowW, h);
        Widget edge = row.FindAnyWidget("OZL_OvFacRowEdge");
        if (edge)
            edge.SetSize(rowW, h);
        Widget bg = row.FindAnyWidget("OZL_OvFacRowBg");
        if (bg)
            bg.SetSize(rowW - 2 * s, h - 2 * s);
        if (pool)
        {
            pool.SetPos(194 * s, (h - poolH) / 2);
            pool.SetSize(200 * s, poolH);
        }

        // The words: id, dash and name from the left (the name cut where the pool
        // begins), the two counts written from the right.
        float ty = (h - 17 * s) / 2;
        float tx = 13 * s;
        int tw;
        TextWidget slug = TextWidget.Cast(row.FindAnyWidget("OvFacSlug"));
        if (slug)
        {
            tw = RzFitText(slug);
            slug.SetPos(tx, ty);
            tx = tx + tw + 8 * s;
        }
        Widget dash = row.FindAnyWidget("OvFacDash");
        if (dash && dash.IsVisible())
        {
            dash.SetPos(tx, ty);
            tx = tx + 19 * s;
        }
        Widget name = row.FindAnyWidget("OvFacName");
        if (name)
        {
            float nameW = 186 * s - tx;
            if (nameW < 0)
                nameW = 0;
            name.SetPos(tx, ty);
            name.SetSize(nameW, 17 * s);
        }
        TextWidget done = TextWidget.Cast(row.FindAnyWidget("OvFacDone"));
        if (done)
        {
            tw = RzFitText(done);
            done.SetPos(468 * s - tw, ty);
        }
        TextWidget active = TextWidget.Cast(row.FindAnyWidget("OvFacActive"));
        if (active)
        {
            tw = RzFitText(active);
            active.SetPos(554 * s - tw, ty);
        }
    }

    // The picked faction beside the list: its id and name, its pool on one line (the
    // chips that fit, and how many do not), its done nodes and projects.
    protected void PaintPicked()
    {
        int i;
        for (i = 0; i < m_OvPickChips.Count(); i++)
        {
            if (m_OvPickChips[i])
                m_OvPickChips[i].Unlink();
        }
        m_OvPickChips.Clear();
        m_OvPickRest = "";

        OZL_AdminOwner o = PickedOwnerRow();
        if (!o)
        {
            SetLabel("ResPicked", "#STR_OZL_ED_OV_PICK", OZL_Metal.MUTED);
            ShowW("RzOvPoolTag", false);
            SetLabel("RzOvPoolRest", "", 0);
            return;
        }

        string who = o.Id;
        if (o.Name != "" && o.Name != o.Id)
            who = o.Id + " — " + o.Name;
        SetLabel("ResPicked", who, OZL_Metal.TEXT);
        ShowW("RzOvPoolTag", true);

        Widget line = M_SUB_WIDGET.FindAnyWidget("RzOvPoolLine");
        if (o.Known != 1)
        {
            m_OvPickRest = Tr("#STR_OZL_VPP_OV_NO_STATE");
            OvLayPickLine();
            return;
        }

        array<string> types = new array<string>();
        array<string> amounts = new array<string>();
        OvPool(o.Pool, types, amounts);
        Widget chip;
        if (line)
        {
            if (types.Count() == 0)
            {
                chip = OvAddChip(line, "", "#STR_OZL_VPP_OV_EMPTY", OZL_Metal.MUTED);
                if (chip)
                    m_OvPickChips.Insert(chip);
            }
            for (i = 0; i < types.Count(); i++)
            {
                chip = OvAddChip(line, types[i], types[i] + " " + amounts[i], OZL_Metal.TEXT);
                if (chip)
                    m_OvPickChips.Insert(chip);
            }
        }
        string doneWord = Tr("#STR_OZL_VPP_OV_DONE");
        string runWord = Tr("#STR_OZL_VPP_OV_RUNNING");
        m_OvPickRest = doneWord + o.Completed.ToString() + " · " + runWord + o.Active.ToString();
        OvLayPickLine();
    }

    // The picked faction's line: "Пул", the chips that fit, then the rest of the words.
    // The chips that do not fit are hidden and counted before the words ("+2").
    protected void OvLayPickLine()
    {
        Widget line = M_SUB_WIDGET.FindAnyWidget("RzOvPoolLine");
        TextWidget rest = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzOvPoolRest"));
        if (!line || !rest)
            return;
        float s = UnitScale();
        float lw;
        float lh;
        line.GetSize(lw, lh);

        float x = 0;
        TextWidget tag = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzOvPoolTag"));
        if (tag && tag.IsVisible())
        {
            int tagW = RzFitText(tag);
            x = tagW + 6 * s;
        }

        rest.SetText(m_OvPickRest);
        int restW = OZ_VppFlex.TextWidth(rest);
        int n = m_OvPickChips.Count();
        int hidden = 0;
        for (int i = 0; i < n; i++)
        {
            Widget chip = m_OvPickChips[i];
            if (!chip)
                continue;
            if (hidden > 0)
            {
                chip.Show(false);
                hidden++;
                continue;
            }
            float cw = OvHugChip(chip, OZL_Metal.HEAD);
            // Room for the words after it, and for "+N · " while chips are still to come.
            float need = x + cw + 14 * s + restW;
            if (i < n - 1)
                need = need + 34 * s;
            if (i > 0 && need > lw)
            {
                chip.Show(false);
                hidden = 1;
                continue;
            }
            chip.Show(true);
            chip.SetPos(x, 1 * s);
            x = x + cw + 12 * s;
        }
        if (hidden > 0)
            rest.SetText("+" + hidden.ToString() + " · " + m_OvPickRest);
        if (n > 0)
            x = x + 2 * s;
        float rw = lw - x;
        if (rw < 0)
            rw = 0;
        rest.SetPos(x, 1 * s);
        rest.SetSize(rw, 15 * s);
    }

    // The confirm strip's words for a reset: whose pool and nodes go.
    protected string ResetAsk(string owner)
    {
        string who = owner;
        OZL_AdminOwner o = PickedOwnerRow();
        if (o && o.Id == owner && o.Name != "" && o.Name != owner)
            who = owner + " - " + o.Name;
        string ask = Tr("#STR_OZL_VPP_ASK_RESET");
        string tail = Tr("#STR_OZL_VPP_ASK_RESET2");
        return ask + who + tail;
    }

    // The server's counters from the list answer ("owners=7 pointTypes=7 ... problems=0"):
    // what the server reads now, a tile each, and its count of problems beside the heading.
    protected void PaintCounters(string counters)
    {
        array<string> keys = {"pointTypes", "owners", "rules", "nodes", "modules", "statics", "problems"};
        array<string> parts = new array<string>();
        counters.Split(" ", parts);
        string word = Tr("#STR_OZL_VPP_OV_PROBLEMS");
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
            if (keys[k] != "problems")
            {
                SetLabel("RzOvV" + k.ToString(), value, OZL_Metal.TEXT);
                continue;
            }
            int color = OZL_Metal.MUTED;
            if (value != "-")
            {
                color = OZL_Metal.OK;
                if (value.ToInt() > 0)
                    color = OZL_Metal.BAD;
            }
            SetLabel("RzOvProblems", word + value, color);
            RzFitText(TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzOvProblems")));
        }
    }

    // The heading over the statics is as wide as its words in the client's language; the
    // count beside it stands ten units after it.
    protected void OvLayHeads()
    {
        RzFlowAfter("RzOvStHead", "RzOvStCount", 10);
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

    // The static spawner's line from the list answer, a row per entry, placed or waiting.
    // A line of another shape (no entries, a broken state file) is shown as it came. String
    // values of a parsed answer stop at 1023 bytes, so a long list can end cut: its broken
    // last entry becomes "...", and the count says so.
    protected void PaintStatics(string statics)
    {
        Widget host = M_SUB_WIDGET.FindAnyWidget("RzOvStRows");
        if (!host)
            return;
        if (!m_OvStRows)
            m_OvStRows = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_ov_static_row.layout", "OZL_OvStRow", 339, 30);

        m_OvStRows.Clear();
        array<string> parts = new array<string>();
        statics.Split(" ", parts);
        bool shaped = false;
        if (parts.Count() > 0)
            shaped = StaticShaped(parts[0]);
        Widget row;
        if (!shaped)
        {
            if (statics != "")
            {
                row = m_OvStRows.Add("");
                OvFillStatic(row, statics, "", 0);
            }
            m_OvStRows.Fit();
            OvLayStatics();
            SetLabel("RzOvStCount", "", 0);
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
                row = m_OvStRows.Add("");
                OvFillStatic(row, "...", "", 0);
                break;
            }
            int eq = token.IndexOf("=");
            int br = token.IndexOf("[");
            string id = token.Substring(0, eq);
            string flag = token.Substring(br + 1, token.Length() - br - 2);
            total++;
            bool placedNow = (flag == "spawned");
            if (placedNow)
                spawned++;
            if (total > RZ_LIST_MAX)
                continue;
            row = m_OvStRows.Add(id);
            if (placedNow)
                OvFillStatic(row, id, spawnedWord, 1);
            else
                OvFillStatic(row, id, pendingWord, 2);
        }
        m_OvStRows.Fit();
        OvLayStatics();

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

    // A static's row: its id and a chip that says whether it stands (state 1) or waits
    // (state 2); state 0 is words alone.
    protected void OvFillStatic(Widget row, string id, string word, int state)
    {
        if (!row)
            return;
        RzRowText(row, "OvStId", id, OZL_Metal.TEXT);
        Widget chip = row.FindAnyWidget("OvStChip");
        if (chip)
            chip.Show(state != 0);
        if (state == 0)
            return;
        int ink = OZL_Metal.OK;
        int ground = OZL_Metal.OK_CHIP;
        if (state == 2)
        {
            ink = OZL_Metal.ALERT;
            ground = OZL_Metal.WARN_CHIP;
        }
        RzRowText(row, "OvStState", word, ink);
        OZ_VppFlex.Paint(row, "OvStChipBg", ground);
    }

    // Every static's chip as wide as its word, at the row's right end.
    protected void OvLayStatics()
    {
        if (!m_OvStRows)
            return;
        float s = UnitScale();
        float w = m_OvStRows.Width();
        for (int i = 0; i < m_OvStRows.Count(); i++)
        {
            Widget row = m_OvStRows.Row(i);
            if (!row)
                continue;
            Widget chip = row.FindAnyWidget("OvStChip");
            TextWidget t = TextWidget.Cast(row.FindAnyWidget("OvStState"));
            if (!chip || !t)
                continue;
            float cw = OZ_VppFlex.Hug(chip, row.FindAnyWidget("OvStChipBg"), t, 8 * s);
            chip.SetPos(w - 10 * s - cw, 6 * s);
        }
    }

    // ================================================= Дерево

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

    // The owner's branches in the file's order -- the rows of the branch list. A picked
    // branch the owner no longer has (another list is being typed into the owners field)
    // stays at the end: the pick would jump to another branch in the middle of typing.
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

    // The lists on the left; the default pick is the first owner and its first branch.
    protected void RepaintTrLists(OZL_TreeConfig tree, OZL_Owners owners)
    {
        Widget hostO = M_SUB_WIDGET.FindAnyWidget("RzTrOwRows");
        Widget hostB = M_SUB_WIDGET.FindAnyWidget("RzTrBrRows");
        if (!hostO || !hostB)
            return;
        if (!m_TrOwRows)
            m_TrOwRows = new OZ_VppFlexRows(m_Flex, hostO, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_tr_owner_row.layout", "OZL_TrOwnerRow", 251, 32);
        if (!m_TrBrRows)
            m_TrBrRows = new OZ_VppFlexRows(m_Flex, hostB, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_tr_branch_row.layout", "OZL_TrBranchRow", 251, 34);

        int i;
        bool ownerKnown = false;
        string firstOwner = "";
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            if (!owners.Owners[i])
                continue;
            if (firstOwner == "")
                firstOwner = owners.Owners[i].Id;
            if (owners.Owners[i].Id == m_TrOwner)
                ownerKnown = true;
        }
        if (!ownerKnown)
            m_TrOwner = firstOwner;

        array<string> ids = new array<string>();
        TrBranchIds(tree, ids);
        if (ids.Find(m_TrBranch) < 0)
        {
            m_TrBranch = "";
            if (ids.Count() > 0)
                m_TrBranch = ids[0];
            m_TrSel = "";
        }

        Widget row;
        m_TrOwRows.Clear();
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            OZL_OwnerDef o = owners.Owners[i];
            if (!o || m_TrOwRows.Count() >= RZ_LIST_MAX)
                continue;
            row = m_TrOwRows.Add(o.Id);
            if (!row)
                break;
            string ownerName = RzOwnerName(o.Id);
            RzRowText(row, "TrOwId", o.Id, OZL_Metal.TEXT);
            RzRowText(row, "TrOwName", ownerName, OZL_Metal.TEXT);
            RzRowText(row, "TrOwSkin", owners.SkinOf(o.Id), OZL_Metal.MUTED);
            Widget dash = row.FindAnyWidget("TrOwDash");
            if (dash)
                dash.Show(ownerName != "");
            RzLitRow(row, "OZL_TrOwnerRow", o.Id == m_TrOwner);
        }
        m_TrOwRows.Fit();

        string nodesWord = Tr("#STR_OZL_VPP_TR_NODES_N");
        string otherWord = Tr("#STR_OZL_ED_BR_OTHER");
        m_TrBrRows.Clear();
        for (i = 0; i < ids.Count(); i++)
        {
            OZL_TreeBranch br = OZL_EdTree.FindBranch(tree, ids[i]);
            if (!br || m_TrBrRows.Count() >= RZ_LIST_MAX)
                continue;
            row = m_TrBrRows.Add(br.Id);
            if (!row)
                break;
            string bn = br.Name;
            if (bn == "")
                bn = br.Id;
            if (!br.BelongsTo(m_TrOwner))
                bn = bn + otherWord;
            RzRowText(row, "TrBrName", bn, OZL_Metal.TEXT);
            RzRowText(row, "TrBrCount", nodesWord + br.Nodes.Count().ToString(), OZL_Metal.MUTED);
            RzLitRow(row, "OZL_TrBranchRow", br.Id == m_TrBranch);
        }
        m_TrBrRows.Fit();
        RzLayTrRows();
    }

    // The words of the side rows along their lines (251 units a row).
    protected void RzLayTrRows()
    {
        int i;
        if (m_TrOwRows)
        {
            for (i = 0; i < m_TrOwRows.Count(); i++)
                RzLaySideRow(m_TrOwRows.Row(i), "TrOwId", "TrOwDash", "TrOwName", "TrOwSkin", 251);
        }
        if (m_TrBrRows)
        {
            for (i = 0; i < m_TrBrRows.Count(); i++)
                RzLaySideRow(m_TrBrRows.Row(i), "", "", "TrBrName", "TrBrCount", 251);
        }
    }

    // The inside of the canvas (a scroll area with both bars, a canvas for the links, a
    // frame for the cells): made once into the page's RzTrHost.
    protected void RzTrEnsureCanvas()
    {
        Widget host = M_SUB_WIDGET.FindAnyWidget("RzTrHost");
        if (!host)
            return;
        if (!M_SUB_WIDGET.FindAnyWidget("RzTrScroll"))
        {
            Widget made = OZ_VppFlex.Create("OpenZone_Research_VPP/gui/layouts/ozl_vpp_tree_canvas.layout", host, "RzTrScroll");
            if (!made)
            {
                OZL_Log.Error("research vpp: the tree canvas did not load (ozl_vpp_tree_canvas.layout); the tree page draws no branch");
                return;
            }
        }
        RzLayTree();
    }

    // The scroll area as large as its host inside the host's one-unit frame.
    protected void RzLayTree()
    {
        Widget host = M_SUB_WIDGET.FindAnyWidget("RzTrHost");
        ScrollWidget scroll = ScrollWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrScroll"));
        if (!host || !scroll)
            return;
        float s = UnitScale();
        float hw;
        float hh;
        host.GetSize(hw, hh);
        if (hw <= 4 * s || hh <= 4 * s)
            return;
        scroll.SetPos(s, s);
        scroll.SetSize(hw - 2 * s, hh - 2 * s);
        scroll.Update();
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
        if (m_TrPlus)
        {
            m_TrPlus.Unlink();
            m_TrPlus = null;
        }
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

    // The OR labels at the places OZL_TreeLines.Draw put into m_TrOrs: the skin's or_label
    // row, its text and colour as in the player's window.
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

    // The line under the canvas: what a click or a drag does right now.
    protected void PaintTrInfo()
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrInfo"));
        if (!t)
            return;
        string word;
        if (m_TrLink && m_TrLinkFrom == "")
            t.SetText(Tr("#STR_OZL_ED_TR_LINK_FROM"));
        else if (m_TrLink)
        {
            word = Tr("#STR_OZL_ED_TR_LINK_TO");
            t.SetText(word + m_TrLinkFrom);
        }
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

    // A frame cuts its children at its edge: the cell and the containers of NodeHit let
    // marks and names reach past it, as OZL_TreeMenu.Unclip does.
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

    // The page. full -- the plan and the cells again (the structure changed: owner, branch,
    // id, tier, parents, condition, a node added or gone, an undo); otherwise only the
    // cells' paint and the links (the pick, a name, a price, an icon). fillForm -- write
    // the fields of the two forms; not while one is typed in, the cursor would jump.
    protected void RepaintTree(bool full, bool fillForm = true)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_Owners owners = DraftOwners();
        RzTrEnsureCanvas();
        CanvasWidget lines = CanvasWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrLines"));
        SetLabel("RzTrTitle", "#STR_OZL_VPP_H_TREE", 0);
        RzFitLegend("RzBrLegend", "RzBrGap");
        PaintTrButtons();
        PaintTrInfo();
        if (!tree || !owners)
        {
            ClearTrCells();
            if (lines)
                lines.Clear();
            PaintTrSkin("", "", Tr("#STR_OZL_ED_HINT_LOADING"));
            if (fillForm)
            {
                FillTnForm(null);
                FillBrForm(null);
            }
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
            PaintTrSkin("", "", Tr("#STR_OZL_ED_TR_NO_BRANCH"));
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

        // The canvas takes the ground of the owner's window.
        OZ_VppFlex.Paint(M_SUB_WIDGET, "RzTrHostBg", m_TrSkin.Lcd);

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
            DrawTrPick(lines, k);
        }
        PlaceTrPlus(k);
        PaintTrSkin(skinId, m_TrSkin.Dir, "");

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

    // The line over the canvas: whose window draws the branch and which way its tree grows
    // (an arrow, the skin's id, the way and the shape of its nodes), or `instead` -- why
    // there is nothing to draw.
    protected void PaintTrSkin(string skinId, string dir, string instead)
    {
        ImageWidget arrow = ImageWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrDirIcon"));
        bool has = (skinId != "");
        if (arrow)
        {
            arrow.Show(has);
            // The arrow is drawn pointing right; a positive yaw turns it clockwise.
            float yaw = 0;
            if (dir == "down")
                yaw = 90;
            else if (dir == "up")
                yaw = 270;
            arrow.SetRotation(0, 0, yaw);
        }
        ShowW("RzTrSkinTag", has);
        if (!has)
        {
            SetLabel("RzTrSkinId", instead, OZL_Metal.MUTED);
            SetLabel("RzTrSkinDir", "", 0);
            FlowTrSkin();
            return;
        }

        SetLabel("RzTrSkinId", skinId, OZL_Metal.TEXT);
        string way = SkinDir(dir);
        string tail = "· " + way;
        // The shape of the skin's nodes, when the stringtable names it.
        string shapeKey = skinId;
        shapeKey.ToUpper();
        string shape = Tr("#STR_OZL_VPP_SKIN_S_" + shapeKey);
        if (shape != "" && shape.IndexOf("STR_") == -1)
            tail = tail + " · " + shape;
        SetLabel("RzTrSkinDir", tail, OZL_Metal.MUTED);
        FlowTrSkin();
    }

    // The words of that line one after another (the page's units: the arrow at 294, the
    // words from 318, at 100 down).
    protected void FlowTrSkin()
    {
        TextWidget tag = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrSkinTag"));
        TextWidget id = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrSkinId"));
        TextWidget way = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrSkinDir"));
        if (!id || !way)
            return;
        float s = UnitScale();
        float x = 294 * s;
        int tw;
        if (tag && tag.IsVisible())
        {
            x = 318 * s;
            tw = RzFitText(tag);
            RzSetX(tag, x);
            x = x + tw + 4 * s;
        }
        tw = RzFitText(id);
        RzSetX(id, x);
        x = x + tw + 5 * s;
        RzFitText(way);
        RzSetX(way, x);
    }

    // The branch's plan for the size of the skin's own window, and the cells at its places.
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

        // The editor's handle that adds a child to the picked node: made after the cells,
        // so it lies over them.
        m_TrPlus = OZ_VppFlex.Create("OpenZone_Research_VPP/gui/layouts/ozl_vpp_tree_plus.layout", nodes, "BtnRzTrPlus");
        if (m_TrPlus)
            m_TrPlus.Show(false);
    }

    // The cells' paint: the state "available" for all (the editor has no state), the
    // picked one (and the source of a link) marked; the price as chips from the draft's
    // node, as the player's window does, or as a line when the skin has no chips.
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

    // Chips that wait for their texts' widths; after twelve frames -- as they are.
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

    // The node the editor's handles stand at: the picked one, or the source of a link.
    protected string TrMarked()
    {
        if (m_TrLink && m_TrLinkFrom != "")
            return m_TrLinkFrom;
        return m_TrSel;
    }

    // The editor's own mark of that node: a dashed orange frame around its cell, drawn
    // on the links' canvas after the links (the player's window has none).
    protected void DrawTrPick(CanvasWidget cv, float k)
    {
        string id = TrMarked();
        if (!cv || id == "")
            return;
        Widget cell = M_SUB_WIDGET.FindAnyWidget("rzcell:" + id);
        if (!cell)
            return;
        float cx, cy, cw, ch;
        cell.GetPos(cx, cy);
        cell.GetSize(cw, ch);
        float m = 4 * k;
        float x1 = cx - m;
        float y1 = cy - m;
        float x2 = cx + cw + m;
        float y2 = cy + ch + m;
        float wd = 1.5 * k;
        int ink = OZL_Metal.ACCENT;
        RzDashLine(cv, x1, y1, x2, y1, wd, ink, 5 * k, 4 * k);
        RzDashLine(cv, x2, y1, x2, y2, wd, ink, 5 * k, 4 * k);
        RzDashLine(cv, x2, y2, x1, y2, wd, ink, 5 * k, 4 * k);
        RzDashLine(cv, x1, y2, x1, y1, wd, ink, 5 * k, 4 * k);
    }

    // The handle that adds a child, at the top right corner of that frame; hidden while
    // no node is picked and in the link mode.
    protected void PlaceTrPlus(float k)
    {
        if (!m_TrPlus)
            return;
        Widget cell = null;
        if (m_TrSel != "" && !m_TrLink)
            cell = M_SUB_WIDGET.FindAnyWidget("rzcell:" + m_TrSel);
        if (!cell)
        {
            m_TrPlus.Show(false);
            return;
        }
        float cx, cy, cw, ch;
        cell.GetPos(cx, cy);
        cell.GetSize(cw, ch);
        m_TrPlus.SetPos(cx + cw + 4 * k - 11.5 * k, cy - 4 * k - 11 * k);
        m_TrPlus.Show(true);
    }

    // The canvas's buttons: LINK is lit while the mode is on; the select of the page's
    // head names the state the preview opens with.
    protected void PaintTrButtons()
    {
        int ink = OZL_Metal.TEXT;
        int rim = OZL_Metal.EDGE;
        if (m_TrLink)
        {
            ink = OZL_Metal.ACCENT;
            rim = OZL_Metal.ACCENT;
        }
        SetColorOf("BtnRzTrLinkText", ink);
        SetColorOf("BtnRzTrLinkIcon", ink);
        OZ_VppFlex.Paint(M_SUB_WIDGET, "BtnRzTrLinkEdge", rim);

        string demo = "#STR_OZL_ED_TR_DEMO_NEW";
        if (m_TrDemo == 1)
            demo = "#STR_OZL_ED_TR_DEMO_FUNDED";
        else if (m_TrDemo == 2)
            demo = "#STR_OZL_ED_TR_DEMO_PROGRESS";
        SetLabel("BtnRzTrDemoText", demo, OZL_Metal.TEXT);
    }

    // The node's form: the picked node's fields, and without one a line that says how to
    // pick. The branch has its own form on the left.
    protected void FillTnForm(OZL_TreeNode n)
    {
        ShowW("RzTnForm", n != null);
        if (!n)
        {
            SetLabel("RzTnHead", "#STR_OZL_ED_TN_PICK", OZL_Metal.MUTED);
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

    // The node's head (its name; id, tier and branch under it), its condition pair and
    // its price as chips in the lines' own names -- painted on every keystroke too.
    protected void PaintTnHead(OZL_TreeNode n)
    {
        if (!n)
            return;
        string name = n.Name;
        if (name == "")
            name = n.Id;
        SetLabel("RzTnHead", name, OZL_Metal.TEXT);
        string tierWord = Tr("#STR_OZL_VPP_TN_TIER");
        string branchWord = Tr("#STR_OZL_VPP_TN_BRANCH");
        string sub = n.Id + " · " + tierWord + n.Tier.ToString();
        sub = sub + " · " + branchWord + m_TrBranch;
        SetLabel("RzTnSub", sub, 0);

        string mode = n.ParentsMode;
        mode.ToLower();
        bool anyMode = (mode == "any");
        RzSeg("BtnRzTnModeAll", !anyMode);
        RzSeg("BtnRzTnModeAny", anyMode);

        PaintTnChips(n);
    }

    // The node's price as chips under its field: a square in the line's colour, the
    // line's name and the amount; a type the draft has not is a hollow square under its id.
    protected void PaintTnChips(OZL_TreeNode n)
    {
        int i;
        for (i = 0; i < m_TnChips.Count(); i++)
        {
            if (m_TnChips[i])
                m_TnChips[i].Unlink();
        }
        m_TnChips.Clear();
        Widget box = M_SUB_WIDGET.FindAnyWidget("RzTnPrice");
        if (!box || !n)
            return;

        OZL_PointTypes pts = DraftPointTypes();
        for (i = 0; i < n.Cost.Count(); i++)
        {
            OZL_TreeCost c = n.Cost[i];
            if (!c || m_TnChips.Count() >= 12)
                continue;
            Widget chip = OZ_VppFlex.Create("OpenZone_Research_VPP/gui/layouts/ozl_vpp_cost_chip.layout", box, "OZL_CostChip");
            if (!chip)
                break;
            OZL_PointType pt = null;
            if (pts)
                pt = pts.Find(c.Type);
            string shownName = c.Type;
            if (pt)
            {
                int ink = OZL_PointTypes.ColorArgb(pt.Color);
                OZ_VppFlex.Paint(chip, "CostDotEdge", ink);
                OZ_VppFlex.Paint(chip, "CostDotBg", ink);
                if (pt.Name != "")
                    shownName = pt.Name;
            }
            else
            {
                OZ_VppFlex.Paint(chip, "CostDotEdge", OZL_Metal.MUTED);
                OZ_VppFlex.Paint(chip, "CostDotBg", OZL_Metal.CELL);
            }
            RzRowText(chip, "CostName", shownName, OZL_Metal.TEXT);
            RzRowText(chip, "CostAmount", c.Amount.ToString(), OZL_Metal.TEXT);
            m_TnChips.Insert(chip);
        }
        LayTnChips();
    }

    // The chips in their box, two lines at most (what does not fit is hidden: the field
    // above holds the whole price); the fields under the box move down by the second
    // line. The numbers are ozl_vpp_cost_chip.layout's, in units.
    protected void LayTnChips()
    {
        Widget box = M_SUB_WIDGET.FindAnyWidget("RzTnPrice");
        Widget tail = M_SUB_WIDGET.FindAnyWidget("RzTnTail");
        Widget form = M_SUB_WIDGET.FindAnyWidget("RzTnForm");
        if (!box || !tail || !form)
            return;
        float s = UnitScale();
        float bw;
        float bh;
        box.GetSize(bw, bh);
        if (bw <= 0)
            return;

        // Where the tail stands with one line of chips: read once, before it is moved.
        float tx;
        float ty;
        if (m_TnTailY <= 0)
        {
            tail.GetPos(tx, ty);
            m_TnTailY = ty;
            form.GetSize(m_TnFormW, m_TnFormH);
        }
        if (m_TnTailY <= 0)
            return;

        float x = 0;
        float y = 0;
        int lines = 1;
        for (int i = 0; i < m_TnChips.Count(); i++)
        {
            Widget chip = m_TnChips[i];
            if (!chip)
                continue;
            TextWidget nm = TextWidget.Cast(chip.FindAnyWidget("CostName"));
            TextWidget am = TextWidget.Cast(chip.FindAnyWidget("CostAmount"));
            int nw = RzFitText(nm);
            int aw = RzFitText(am);
            float ax = 23 * s + nw + 4 * s;
            RzSetX(am, ax);
            float cw = ax + aw + 8 * s;
            chip.SetSize(cw, 24 * s);
            Widget bg = chip.FindAnyWidget("OZL_CostChipBg");
            if (bg)
                bg.SetSize(cw, 24 * s);
            if (x > 0 && x + cw > bw)
            {
                x = 0;
                y = y + 30 * s;
                lines++;
            }
            if (lines > 2)
            {
                chip.Show(false);
                continue;
            }
            chip.Show(true);
            chip.SetPos(x, y);
            x = x + cw + 6 * s;
        }
        float extra = 0;
        if (lines > 1)
            extra = 30 * s;
        box.SetSize(bw, 24 * s + extra);
        tail.SetPos(0, m_TnTailY + extra);
        form.SetSize(m_TnFormW, m_TnFormH + extra);
    }

    // The branch's form on the left: the picked branch's fields, empty without one.
    protected void FillBrForm(OZL_TreeBranch br)
    {
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

    // A field of the branch changed: one undo step per field, as for a node.
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
        string word = Tr("#STR_OZL_ED_BR_ADDED");
        Hint(word + br.Id);
    }

    // A branch goes with its nodes and every link to them -- after the yes on the
    // window's confirm strip.
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
        string word;
        if (!br)
        {
            word = Tr("#STR_OZL_VPP_GONE");
            Hint(word + branchId);
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
        word = Tr("#STR_OZL_ED_BR_DELETED");
        Hint(word + id);
    }

    // ------------------------------------------------- links, tiers, the preview

    protected void TrLinkToggle()
    {
        m_TrLink = !m_TrLink;
        m_TrLinkFrom = "";
        if (m_TrLink && m_TrSel != "")
            m_TrLinkFrom = m_TrSel;
        m_Ed.EndGesture();
        RepaintTree(false);
    }

    // A click on a node in the link mode: the first is the parent, the next are children;
    // a click on a child that has this link takes it away; a click on the parent itself
    // lets another be picked.
    protected void TrLinkClick(string id)
    {
        if (m_TrLinkFrom == "")
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
        if (!tree)
            return;
        OZL_TreeNode parent = tree.FindNode(m_TrLinkFrom);
        OZL_TreeNode child = tree.FindNode(id);
        if (!parent || !child)
            return;

        string tag = OZL_Config.TAG_TREE;
        string word;
        int at = child.Parents.Find(m_TrLinkFrom);
        if (at >= 0)
        {
            m_Ed.BeginOnce(tag, "");
            child.Parents.RemoveOrdered(at);
            m_Ed.Commit(tag);
            m_Ed.EndGesture();
            word = Tr("#STR_OZL_ED_TR_UNLINKED");
            Hint(word + m_TrLinkFrom + " -> " + id);
        }
        else
        {
            if (OZL_EdTree.DependsOn(tree, parent, id, 0))
            {
                word = Tr("#STR_OZL_ED_TR_CYCLE");
                RzSay(word + m_TrLinkFrom + " -> " + id, 2);
                return;
            }
            m_Ed.BeginOnce(tag, "");
            child.Parents.Insert(m_TrLinkFrom);
            string note = "";
            if (child.Tier <= parent.Tier)
            {
                child.Tier = parent.Tier + 1;
                string bumped = Tr("#STR_OZL_ED_TR_BUMPED");
                note = bumped + child.Tier.ToString();
            }
            m_Ed.Commit(tag);
            m_Ed.EndGesture();
            word = Tr("#STR_OZL_ED_TR_LINKED");
            Hint(word + m_TrLinkFrom + " -> " + id + note);
        }
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
    }

    // The tier under a node moved along the axis by `along` pixels: the row of the plan
    // the node's centre fell into. Past the last row -- a new tier, before the first --
    // one less (not below 1).
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

    // A node is pressed and dragged: its cell follows the mouse along the axis, the line
    // under the canvas names the tier; released -- the node's tier, one undo step.
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
        string word = Tr("#STR_OZL_ED_TR_DRAG_TIER");
        TrInfoText(word + TierAt(m_TnDragId, along).ToString());
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
        string word = Tr("#STR_OZL_ED_TR_TIER_SET");
        Hint(word + id + ": " + was.ToString() + " -> " + tier.ToString());
    }

    // The empty canvas is pressed: a drag scrolls it, a click without a move drops the
    // picked node.
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

    // Whether the press is on the canvas's scrollbars (10 units at its right and bottom
    // edges, as in the player's window).
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

    // AS THE PLAYER SEES IT: the player's tree window over the admin one, with a view made
    // of the draft and the demo state. The VPP menu stays its parent: ESC closes the tree
    // and comes back here.
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
            RzSay(Tr("#STR_OZL_ED_TR_VIEW_FAIL"), 2);
            return;
        }
        string word = Tr("#STR_OZL_ED_TR_VIEW_OPEN");
        Hint(word + m_TrOwner);
    }

    // A field of the node's form changed: an edit of the picked node, one undo step per field.
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

    // A node's new id. The links (other nodes' parents) follow it to a FREE id only: an
    // id that meets another node's on the way stays behind, or the links would go over
    // to that node for good.
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
        string word = Tr("#STR_OZL_ED_TR_ADDED");
        Hint(word + n.Id);
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

    // The strip's yes: the node is found again by its id, every link to it goes too.
    protected void TnDeleteNow(string nodeId)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = null;
        if (tree)
            n = tree.FindNode(nodeId);
        string word;
        if (!n)
        {
            word = Tr("#STR_OZL_VPP_GONE");
            Hint(word + nodeId);
            return;
        }

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        string id = n.Id;
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            if (!br)
                continue;
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
        word = Tr("#STR_OZL_ED_TR_DELETED");
        Hint(word + id);
    }

    // The node's condition from its pair of buttons: any parent, or all of them. A press
    // on the one in force changes nothing and takes no undo step.
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

    // ================================================= events

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

        // The open page fitted once more, two frames after it was painted.
        if (m_RzRefit > 0)
        {
            m_RzRefit--;
            if (m_RzRefit == 0 && RzShown())
            {
                RzFlowBar();
                RzLayPages(m_RzW, m_RzH);
            }
        }
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

    override bool OnChange(Widget w, int x, int y, bool finished)
    {
        if (w && M_SUB_WIDGET && !m_RzFill && m_Ed)
        {
            string nm = w.GetName();
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
        if (!M_SUB_WIDGET || !w || !m_Ed)
            return super.OnClick(w, x, y, button);

        string nm = w.GetName();

        // ---- the strips
        // The problems panel above the draft bar opens and closes here and on its own
        // close button.
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

        // ---- Дерево
        // A node on the canvas: the NodeHit of its cell is named rznode:<id>. A click that
        // came with the release after a drag is no pick.
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
        if (nm == "BtnRzTrChild" || nm == "BtnRzTrPlus")
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
        // The preview's state, a select of three: a press steps on.
        if (nm == "BtnRzTrDemo")
        {
            m_TrDemo = (m_TrDemo + 1) % 3;
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

        // ---- Огляд
        if (nm == "BtnRzOvRefresh")
        {
            AskResearchList();
            return true;
        }

        // The reload and the reset ask on the window's confirm strip; the yes sends the
        // operation from OnConfirmed.
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

        // ---- rows of the lists (a row, or anything inside one)
        int at;
        if (m_OvFacRows && m_RzTab == "overview")
        {
            at = m_OvFacRows.IndexOf(w);
            if (at != -1)
            {
                m_ResPick = m_OvFacRows.Key(at);
                OvLayFacRows();
                PaintPicked();
                string pickedHint = Tr("#STR_OZL_VPP_HINT_FACTION");
                Hint(pickedHint + m_ResPick);
                return true;
            }
        }
        if (m_TrOwRows && m_RzTab == "tree")
        {
            at = m_TrOwRows.IndexOf(w);
            if (at != -1)
            {
                m_TrOwner = m_TrOwRows.Key(at);
                m_TrBranch = "";
                m_TrSel = "";
                m_TrLinkFrom = "";
                m_Ed.EndGesture();
                RepaintTree(true);
                return true;
            }
        }
        if (m_TrBrRows && m_RzTab == "tree")
        {
            at = m_TrBrRows.IndexOf(w);
            if (at != -1)
            {
                m_TrBranch = m_TrBrRows.Key(at);
                m_TrSel = "";
                m_TrLinkFrom = "";
                m_Ed.EndGesture();
                RepaintTree(true);
                return true;
            }
        }

        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
