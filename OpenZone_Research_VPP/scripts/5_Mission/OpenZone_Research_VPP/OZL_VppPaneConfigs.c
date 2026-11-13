// The pages TYPES OF POINTS, OWNERS, MODULES and STATICS of the research editor: a pane
// each since 2026-11-13, converted from its mockup board (css2layout; the layouts
// ozl_vpp_points, ozl_vpp_owners, ozl_vpp_modules and ozl_vpp_statics with their row
// templates). The frame -- OZL_VppPane.c -- creates and registers the panes and owns the
// draft, its bar and the problems panel; this layer fills the four pages from the draft
// and writes their edits back into it.
//
// Every page is the same thing over another file of the draft: the file's entries as a
// list of rows on the left (the head's button adds one), the picked entry's fields on
// the right with its delete. A field writes the draft as it is typed, one undo step per
// field; a delete is asked on the window's confirm strip. What the pages share lives in
// the Cfg* functions (which file, which entry, its fields by number); what a page draws
// of its own -- the tree window picker of OWNERS, what a module does on MODULES, WHERE I
// STAND on STATICS, the colour of a type -- lives beside them.
//
// What the frame calls here (the hooks of OZL_VppPane.c, each handed on with super):
//   RepaintRzPage(tab)   fill page `tab` from the draft: shown, fetched, undone, applied;
//   RzLayPages(pw, ph)   the open page changed its size: its rows and heads follow
//                        (CfgLayOpen, which the settings layer extends);
//   OnClick, OnChange    the pages' own buttons, rows and fields, by widget name;
//   OnConfirmed(action)  "rz:ptdel:<id>" and "rz:cfgdel:<row>", the confirm strip's yes;
//   Tick()               the core's frame tick: the stations box of OWNERS is followed by
//                        polling, and a page painted by this layer is laid once more two
//                        frames later (a text written this frame may have its width only
//                        then).
//
// A separate modded layer of OZ_VppAdminMenu: the file name must sort after
// OZL_VppPane.c (the files of a folder compile in alphabetical order, and the layer
// that overrides comes later).
//
// Design: docs/specs/2026-11-13-openzone-vpp-page-guide.md; the editor itself:
// docs/specs/2026-11-09-research-editor-vpp-design.md.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    // A list draws at most this many rows; the count line says when it left some out.
    static const int CFG_LIST_MAX = 300;

    // The picked entry of OWNERS, MODULES and STATICS (its place in the file), by page.
    private ref map<string, int> m_CfgPick;

    // The picked type of points (its place in the file).
    private int m_PtPick;

    // What the confirm strip asked to delete: the page and the entry as it read then.
    private string m_CfgDelTab;
    private string m_CfgDelWhat;

    // The tree windows the picker offers, in the order of its buttons; "" is "by the
    // faction's id". Their ways of growing come from the skins themselves, once.
    private ref array<string> m_CfgSkins;
    private ref array<string> m_CfgSkinDirs;

    // The lists: rows made from the row templates, one set per page (MODULES has two
    // kinds of rows in one list: a caption per line and the modules under it).
    private ref OZ_VppFlexRows m_PtRows;
    private ref OZ_VppFlexRows m_OwRows;
    private ref OZ_VppFlexRows m_MoHeads;
    private ref OZ_VppFlexRows m_MoRows;
    private ref OZ_VppFlexRows m_StcRows;

    // The stations box of OWNERS as the script last saw it (a multiline edit box tells
    // nobody that it was typed in: Tick compares).
    private string m_OwDevSeen;

    // What the search boxes of MODULES and STATICS filter by (lower case, trimmed).
    private string m_MoFind;
    private string m_StcFind;

    // Whether the picked module has a line: its chip then begins with the line's dot.
    private bool m_MoHasLine;

    // Frames left until the open page is laid once more (CfgLayOpen): a text written
    // this frame may have its width only then.
    private int m_CfgRefit;

    override void OnCreate(Widget RootW)
    {
        m_CfgPick = new map<string, int>();
        m_PtPick = 0;
        m_CfgDelTab = "";
        m_CfgDelWhat = "";
        m_CfgSkins = new array<string>();
        array<string> skins = {"", "ecolog", "clearsky", "duty", "freedom", "sop", "bandit", "neutral"};
        for (int i = 0; i < skins.Count(); i++)
            m_CfgSkins.Insert(skins[i]);
        m_CfgSkinDirs = new array<string>();
        m_OwDevSeen = "";
        m_MoFind = "";
        m_StcFind = "";
        m_MoHasLine = false;
        m_CfgRefit = 0;
        super.OnCreate(RootW);
    }

    protected bool IsCfgTab(string key)
    {
        if (key == "owners" || key == "modules" || key == "statics")
            return true;
        return false;
    }

    override void RepaintRzPage(string tab)
    {
        if (tab == "points")
        {
            PtFill(true);
            return;
        }
        if (IsCfgTab(tab))
        {
            RepaintCfg(true);
            return;
        }
        super.RepaintRzPage(tab);
    }

    // ================================================= what the four pages share

    // A row's frame and ground: the picked one as its template drew it (the accent on
    // its soft ground), the others plain.
    protected void CfgRowPick(Widget row, string root, bool picked)
    {
        int rim = ARGB(255, 19, 19, 18);
        int ground = ARGB(255, 19, 19, 18);
        if (picked)
        {
            rim = ARGB(255, 232, 120, 43);
            ground = ARGB(255, 47, 29, 17);
        }
        OZ_VppFlex.Paint(row, root + "Edge", rim);
        OZ_VppFlex.Paint(row, root + "Bg", ground);
    }

    // A text of a row.
    protected void CfgPart(Widget row, string name, string text)
    {
        TextWidget t = TextWidget.Cast(row.FindAnyWidget(name));
        if (t)
            t.SetText(text);
    }

    // A text made as wide as its words (a TextWidget cuts its text at its own width);
    // returns the words' width in pixels. A text with no width yet -- an empty one, or
    // one written this frame on a page that is not laid out -- is left as it is.
    protected float CfgFitText(Widget w)
    {
        TextWidget t = TextWidget.Cast(w);
        if (!t)
            return 0;
        float tw = OZ_VppFlex.TextWidth(t);
        if (tw <= 0)
            return 0;
        float ww;
        float hh;
        t.GetSize(ww, hh);
        t.SetSize(tw + 2, hh);
        return tw;
    }

    // `second` put `gap` units after the words of `first`; both stand in one parent.
    // Returns where `second` now begins, in pixels.
    protected float CfgPutAfter(Widget first, Widget second, float gap)
    {
        if (!first || !second)
            return 0;
        float tw = CfgFitText(first);
        float x;
        float y;
        first.GetPos(x, y);
        float nx;
        float ny;
        second.GetPos(nx, ny);
        float at = x + tw + gap * Px();
        second.SetPos(at, ny);
        return at;
    }

    // A text written whole when its widget has the room, else cut short with a mark: a
    // TextWidget cuts its text at its own width.
    protected void CfgElide(string name, string text)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(name));
        if (!t)
            return;
        t.SetText(text);
        float w;
        float h;
        t.GetSize(w, h);
        float tw = OZ_VppFlex.TextWidth(t);
        if (w <= 0 || tw <= w)
            return;
        int n = text.LengthUtf8();
        float f = n;
        int keep = f * w / tw;
        keep = keep - 2;
        if (keep < 1)
            keep = 1;
        if (keep < n)
            t.SetText(text.SubstringUtf8(0, keep) + "…");
    }

    // The open page is laid once more two frames from now.
    protected void CfgRefitSoon()
    {
        m_CfgRefit = 2;
    }

    // "; the first shown: 300" when a list is longer than it draws, else nothing.
    protected string CfgCutNote(int total)
    {
        if (total <= CFG_LIST_MAX)
            return "";
        string cut = Tr("#STR_OZL_VPP_LIST_CUT");
        int most = CFG_LIST_MAX;
        return cut + most.ToString();
    }

    // A share 0..1 in whole per cent, as the pages write it: 0.7 -> "70 %".
    protected string CfgPct(float f)
    {
        int p = Math.Round(f * 100);
        return p.ToString() + " %";
    }

    // The line's own name and colour from the types of points of the draft; the id and
    // the page's ink when no type names the line.
    protected string CfgLineName(string line)
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (pts)
        {
            OZL_PointType pt = pts.Find(line);
            if (pt && pt.Name != "")
                return pt.Name;
        }
        return line;
    }

    protected int CfgLineInk(string line)
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (pts)
        {
            OZL_PointType pt = pts.Find(line);
            if (pt)
                return PtInk(pt.Color);
        }
        return ARGB(255, 92, 90, 88);
    }

    // What a search box holds, as the filter takes it.
    // OZ_VppFold (the core window's), not ToLower: the engine's ToLower makes every
    // Cyrillic byte a space, and in-game names are searched here too.
    protected string CfgFindText(string box)
    {
        string t = GetEdit(box);
        t = t.Trim();
        return OZ_VppFold.Lower(t);
    }

    protected bool CfgHas(string text, string find)
    {
        string low = OZ_VppFold.Lower(text);
        return low.IndexOf(find) != -1;
    }

    // ================================================= TYPES OF POINTS

    protected OZL_PointType PtPicked()
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts || m_PtPick < 0 || m_PtPick >= pts.PointTypes.Count())
            return null;
        return pts.PointTypes[m_PtPick];
    }

    // A type's colour as a widget takes it; the frame's grey for a colour that does not
    // read as #RRGGBB.
    protected int PtInk(string hex)
    {
        int c = OZL_PointTypes.ColorArgb(hex);
        if (c == 0)
            return ARGB(255, 60, 60, 58);
        return c;
    }

    // The list and the head from the draft and, when fillForm, the picked type's
    // fields. While a field is typed in the fields are left alone: the cursor would
    // jump to the end on every letter.
    protected void PtFill(bool fillForm)
    {
        if (!M_SUB_WIDGET || !m_Ed)
            return;
        OZL_PointTypes pts = DraftPointTypes();
        int n = 0;
        if (pts)
            n = pts.PointTypes.Count();
        if (m_PtPick >= n)
            m_PtPick = n - 1;
        if (m_PtPick < 0)
            m_PtPick = 0;

        PtRebuild(pts);
        PtPaintHead();
        if (fillForm)
            PtFillForm();
    }

    protected void PtRebuild(OZL_PointTypes pts)
    {
        if (!m_PtRows)
        {
            Widget host = M_SUB_WIDGET.FindAnyWidget("RzPtListRows");
            if (!host)
                return;
            m_PtRows = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_pt_row.layout", "OZL_VppPtRow", 527, 42);
        }

        m_PtRows.Clear();
        if (!pts)
        {
            SetLabel("RzPtCount", Tr("#STR_OZL_ED_HINT_LOADING"), 0);
            return;
        }
        int n = pts.PointTypes.Count();
        for (int i = 0; i < n && i < CFG_LIST_MAX; i++)
        {
            Widget row = m_PtRows.Add(i.ToString());
            if (row)
                PtPaintRow(row, pts.PointTypes[i], i == m_PtPick);
        }
        m_PtRows.Fit();

        string inDraft = Tr("#STR_OZL_VPP_PT_COUNT");
        string cut = CfgCutNote(n);
        SetLabel("RzPtCount", inDraft + n.ToString() + cut, 0);
    }

    protected void PtPaintRow(Widget row, OZL_PointType p, bool picked)
    {
        CfgRowPick(row, "OZL_VppPtRow", picked);
        if (!p)
            return;
        OZ_VppFlex.Paint(row, "PtRowSwatchBg", PtInk(p.Color));
        CfgPart(row, "PtRowId", p.Id);
        CfgPart(row, "PtRowName", p.Name);
        CfgPart(row, "PtRowSort", p.SortOrder.ToString());
        CfgPart(row, "PtRowPurity", p.BasePurity.ToString());
    }

    // The picked row again from the draft (a field of it was typed in).
    protected void PtRepaintPicked()
    {
        OZL_PointType p = PtPicked();
        if (m_PtRows && p)
        {
            Widget row = m_PtRows.Row(m_PtRows.Find(m_PtPick.ToString()));
            if (row)
                PtPaintRow(row, p, true);
        }
        PtPaintHead();
    }

    // The form's head: the picked type's colour, id and name -- painted on every
    // keystroke, the fields only when a row is picked. With no type to show the head
    // says why and the fields go.
    protected void PtPaintHead()
    {
        OZL_PointType p = PtPicked();
        bool have = (p != null);
        ShowW("RzPtSwatch", have);
        ShowW("BtnRzPtDel", have);
        ShowW("RzPtGrid", have);
        if (have)
        {
            OZ_VppFlex.Paint(M_SUB_WIDGET, "RzPtSwatchBg", PtInk(p.Color));
            SetLabel("RzPtPicked", p.Id, 0);
            SetLabel("RzPtPickedName", p.Name, 0);
            // The swatch beside the colour field: the colour as typed, the field's own
            // ground while it does not read as a colour.
            int typed = OZL_PointTypes.ColorArgb(p.Color);
            if (typed == 0)
                typed = ARGB(255, 7, 7, 7);
            OZ_VppFlex.Paint(M_SUB_WIDGET, "RzPtColorSwBg", typed);
        }
        else
        {
            string why = "#STR_OZL_ED_CFG_EMPTY";
            if (!DraftPointTypes())
                why = "#STR_OZL_ED_HINT_LOADING";
            SetLabel("RzPtPicked", Tr(why), 0);
            SetLabel("RzPtPickedName", "", 0);
        }
        PtPlace(have);
        CfgRefitSoon();
    }

    // The head's words stand one after another whatever their length: the id after the
    // swatch (at the row's start without one), the name after the id.
    protected void PtPlace(bool have)
    {
        Widget id = M_SUB_WIDGET.FindAnyWidget("RzPtPicked");
        Widget name = M_SUB_WIDGET.FindAnyWidget("RzPtPickedName");
        Widget head = M_SUB_WIDGET.FindAnyWidget("RzPtHeadRow");
        if (!id || !name || !head)
            return;
        float s = Px();
        float x;
        float y;
        id.GetPos(x, y);
        x = 0;
        if (have)
            x = 38 * s;
        id.SetPos(x, y);
        float at = CfgPutAfter(id, name, 12);

        // The name takes the room up to the delete button (120 units wide, 12 before it).
        float hw;
        float hh;
        head.GetSize(hw, hh);
        float nw;
        float nh;
        name.GetSize(nw, nh);
        float room = hw - at - 132 * s;
        if (room < 0)
            room = 0;
        name.SetSize(room, nh);
    }

    protected void PtFillForm()
    {
        OZL_PointType p = PtPicked();
        if (!p)
            return;
        m_RzFill = true;
        SetEdit("RzPtId", p.Id);
        SetEdit("RzPtName", p.Name);
        SetEdit("RzPtColor", PtColorShown(p.Color));
        SetEdit("RzPtSort", p.SortOrder.ToString());
        SetEdit("RzPtPurity", p.BasePurity.ToString());
        SetEdit("RzPtIcon", p.Icon);
        m_RzFill = false;
    }

    // THE COLOUR WITHOUT ITS "#" IN THE FIELD. A text that starts with "#" is read by
    // the engine as a stringtable key: SetText("#7CB342") showed "7CB342" (measured
    // 2026-11-09), and a field edited after that gave the colour back without the sign.
    // So the field shows six digits (the "#" is drawn before it) and the file gets
    // "#RRGGBB", as the pack wrote it and as OZL_PointTypes.ColorArgb reads it.
    protected string PtColorShown(string stored)
    {
        string c = stored.Trim();
        if (c.IndexOf("#") == 0)
            c = c.Substring(1, c.Length() - 1);
        return c;
    }

    protected string PtColorStored(string typed)
    {
        string c = typed.Trim();
        if (c == "" || c.IndexOf("#") == 0)
            return c;
        return "#" + c;
    }

    // A field of the form changed: an edit of the picked type, one snapshot per field.
    protected void PtOnField(string field)
    {
        OZL_PointType p = PtPicked();
        if (!p)
            return;

        string tag = OZL_Config.TAG_POINT_TYPES;
        m_Ed.BeginOnce(tag, "pt:" + m_PtPick.ToString() + ":" + field);

        string v = GetEdit(field);
        if (field == "RzPtId")
            p.Id = v.Trim();
        else if (field == "RzPtName")
            p.Name = v;
        else if (field == "RzPtColor")
            p.Color = PtColorStored(v);
        else if (field == "RzPtSort")
            p.SortOrder = v.ToInt();
        else if (field == "RzPtPurity")
            p.BasePurity = v.ToFloat();
        else if (field == "RzPtIcon")
            p.Icon = v.Trim();

        m_Ed.Commit(tag);
        PtRepaintPicked();
        PaintRzBar();
        PaintSummary();
    }

    // A row of the list was clicked: that type is the picked one.
    protected void PtPick(int at)
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts || at < 0 || at >= pts.PointTypes.Count())
            return;
        m_PtPick = at;
        m_Ed.EndGesture();
        if (m_PtRows)
        {
            for (int i = 0; i < m_PtRows.Count(); i++)
                CfgRowPick(m_PtRows.Row(i), "OZL_VppPtRow", m_PtRows.Key(i) == at.ToString());
        }
        PtPaintHead();
        PtFillForm();
    }

    // The head's button: a new line with a free id and its place at the end of the
    // order; the admin renames it.
    protected void PtNew()
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts)
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }

        string tag = OZL_Config.TAG_POINT_TYPES;
        m_Ed.BeginOnce(tag, "");

        int order = 0;
        for (int i = 0; i < pts.PointTypes.Count(); i++)
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
        m_PtPick = pts.PointTypes.Count() - 1;
        PtFill(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_PT_ADDED") + id);
    }

    protected void PtAskDelete()
    {
        OZL_PointType p = PtPicked();
        if (!p)
        {
            Hint(Tr("#STR_OZL_ED_PT_PICK"));
            return;
        }
        string id = p.Id;
        string ask = Tr("#STR_OZL_VPP_ASK_DEL_PT");
        string tail = Tr("#STR_OZL_VPP_ASK_DRAFT");
        Confirm(ask + id + "? " + tail, "#STR_OZL_VPP_YES_DELETE", "rz:ptdel:" + id);
    }

    // The strip's "yes": the type is found again by its id -- the picked row may have
    // moved while the strip was open.
    protected void PtDeleteYes(string id)
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts)
            return;
        int at = -1;
        for (int i = 0; i < pts.PointTypes.Count(); i++)
        {
            if (at < 0 && pts.PointTypes[i] && pts.PointTypes[i].Id == id)
                at = i;
        }
        OZL_PointType picked = PtPicked();
        if (picked && picked.Id == id)
            at = m_PtPick;
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
        if (at < m_PtPick)
            m_PtPick--;
        PtFill(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_PT_DELETED") + id);
    }

    // ================================================= OWNERS, MODULES, STATICS: the file

    protected string CfgTag()
    {
        if (m_RzTab == "owners")
            return OZL_Config.TAG_OWNERS;
        if (m_RzTab == "modules")
            return OZL_Config.TAG_MODULES;
        return OZL_Config.TAG_STATICS;
    }

    protected OZ_ConfigBase CfgObj()
    {
        if (!m_Ed || !IsCfgTab(m_RzTab))
            return null;
        OZL_EdDoc d = m_Ed.Doc(CfgTag());
        if (!d || !d.Loaded)
            return null;
        return d.Obj;
    }

    protected int CfgCount()
    {
        OZ_ConfigBase c = CfgObj();
        if (!c)
            return 0;
        if (m_RzTab == "owners")
            return OZL_Owners.Cast(c).Owners.Count();
        if (m_RzTab == "modules")
            return OZL_Modules.Cast(c).Modules.Count();
        return OZL_StaticsConfig.Cast(c).Entries.Count();
    }

    protected int CfgPicked()
    {
        int at = 0;
        if (!m_CfgPick.Find(m_RzTab, at))
            at = 0;
        int n = CfgCount();
        if (at >= n)
            at = n - 1;
        if (at < 0)
            at = 0;
        return at;
    }

    // Entry i in words: what the confirm strip asks about, and what tells it that the
    // row still holds the same entry when the yes comes.
    protected string CfgRow(int i)
    {
        OZ_ConfigBase c = CfgObj();
        if (m_RzTab == "owners")
        {
            OZL_OwnerDef o = OZL_Owners.Cast(c).Owners[i];
            if (!o)
                return "?";
            return o.Id;
        }
        if (m_RzTab == "modules")
        {
            OZL_ModuleDef m = OZL_Modules.Cast(c).Modules[i];
            if (!m)
                return "?";
            return m.Classname;
        }
        OZL_StaticEntry e = OZL_StaticsConfig.Cast(c).Entries[i];
        if (!e)
            return "?";
        return e.Id + " (" + e.ClassName + ")";
    }

    // The edit boxes of the open page, in the order of the entry's fields.
    protected void CfgFields(array<string> names)
    {
        names.Clear();
        if (m_RzTab == "owners")
        {
            names.Insert("RzOwId");
            names.Insert("RzOwTerms");
            names.Insert("RzOwDevices");
        }
        else if (m_RzTab == "modules")
        {
            names.Insert("RzMoClass");
            names.Insert("RzMoPurity");
            names.Insert("RzMoDouble");
            names.Insert("RzMoNotes");
        }
        else
        {
            names.Insert("RzStcId");
            names.Insert("RzStcClass");
            names.Insert("RzStcX");
            names.Insert("RzStcY");
            names.Insert("RzStcZ");
            names.Insert("RzStcYaw");
            names.Insert("RzStcNote");
        }
    }

    protected string CfgGet(int i, int f)
    {
        OZ_ConfigBase c = CfgObj();
        if (!c)
            return "";
        if (m_RzTab == "owners")
        {
            OZL_OwnerDef o = OZL_Owners.Cast(c).Owners[i];
            if (!o)
                return "";
            if (f == 0)
                return o.Id;
            if (f == 1)
                return OZL_EdTree.ListText(o.TerminalClasses);
            return OZL_EdTree.ListText(o.DeviceClasses);
        }
        if (m_RzTab == "modules")
        {
            OZL_ModuleDef m = OZL_Modules.Cast(c).Modules[i];
            if (!m)
                return "";
            if (f == 0)
                return m.Classname;
            if (f == 1)
                return m.PurityBonus.ToString();
            if (f == 2)
                return m.DoubleChance.ToString();
            return m.Notes;
        }
        OZL_StaticEntry e = OZL_StaticsConfig.Cast(c).Entries[i];
        if (!e)
            return "";
        if (f == 0)
            return e.Id;
        if (f == 1)
            return e.ClassName;
        if (f >= 2 && f <= 4)
        {
            int axis = f - 2;
            if (axis < e.Pos.Count())
                return e.Pos[axis].ToString();
            return "";
        }
        if (f == 5)
            return e.Yaw.ToString();
        return e.Note;
    }

    protected void CfgSet(int i, int f, string v)
    {
        OZ_ConfigBase c = CfgObj();
        if (!c)
            return;
        string vt = v.Trim();
        if (m_RzTab == "owners")
        {
            OZL_OwnerDef o = OZL_Owners.Cast(c).Owners[i];
            if (!o)
                return;
            if (f == 0)
                o.Id = vt;
            else if (f == 1)
                OZL_EdTree.ParseList(v, o.TerminalClasses);
            else
                OZL_EdTree.ParseList(v, o.DeviceClasses);
            return;
        }
        if (m_RzTab == "modules")
        {
            OZL_ModuleDef m = OZL_Modules.Cast(c).Modules[i];
            if (!m)
                return;
            if (f == 0)
                m.Classname = vt;
            else if (f == 1)
                m.PurityBonus = vt.ToFloat();
            else if (f == 2)
                m.DoubleChance = vt.ToFloat();
            else
                m.Notes = v;
            return;
        }
        OZL_StaticEntry e = OZL_StaticsConfig.Cast(c).Entries[i];
        if (!e)
            return;
        if (f == 0)
            e.Id = vt;
        else if (f == 1)
            e.ClassName = vt;
        else if (f >= 2 && f <= 4)
            SetAxis(e, f - 2, vt.ToFloat());
        else if (f == 5)
            e.Yaw = vt.ToFloat();
        else
            e.Note = v;
    }

    // One coordinate of a static's position; a shorter list grows to x, y, z first.
    protected void SetAxis(OZL_StaticEntry e, int axis, float value)
    {
        while (e.Pos.Count() < 3)
            e.Pos.Insert(0);
        e.Pos.Set(axis, value);
    }

    // ------------------------------------------------- the page

    // The open page from the draft: its list, its head and what it draws of its own;
    // with fillForm the picked entry's fields too (not while one is typed in).
    protected void RepaintCfg(bool fillForm)
    {
        if (!M_SUB_WIDGET || !m_CfgPick || !m_Ed || !IsCfgTab(m_RzTab))
            return;

        if (m_RzTab == "owners")
            OwRebuild();
        else if (m_RzTab == "modules")
            MoRebuild();
        else
            StcRebuild();

        CfgPaintHead();
        if (fillForm)
            CfgFillForm();
    }

    // Suffix of the page's stringtable keys: OW, MO, ST.
    protected string CfgHeadKey()
    {
        if (m_RzTab == "owners")
            return "OW";
        if (m_RzTab == "modules")
            return "MO";
        return "ST";
    }

    // The right half above the fields: who is picked and what the page says of it.
    // With no entry to show the head says why and the fields go.
    protected void CfgPaintHead()
    {
        CfgRefitSoon();
        bool loaded = (CfgObj() != null);
        bool have = (loaded && CfgCount() > 0);
        int pick = CfgPicked();
        string why = "#STR_OZL_ED_CFG_EMPTY";
        if (!loaded)
            why = "#STR_OZL_ED_HINT_LOADING";

        if (m_RzTab == "owners")
        {
            ShowW("RzOwBody", have);
            ShowW("BtnRzOwDel", have);
            ShowW("RzOwChip", have);
            SetLabel("BtnRzOwDelText", Tr("#STR_OZL_VPP_CFG_DEL_OW"), 0);
            if (have)
            {
                OwPaintHead(pick);
                PaintSkins(pick);
            }
            else
                SetLabel("RzOwHead", Tr(why), 0);
            OwPlace();
            return;
        }
        if (m_RzTab == "modules")
        {
            ShowW("RzMoBody", have);
            ShowW("BtnRzMoDel", have);
            ShowW("RzMoSub", have);
            ShowW("RzMoLine", have);
            SetLabel("BtnRzMoDelText", Tr("#STR_OZL_VPP_CFG_DEL_MO"), 0);
            if (have)
                MoPaintHead(pick);
            else
                SetLabel("RzMoHead", Tr(why), 0);
            MoPlace();
            return;
        }
        ShowW("RzStcBody", have);
        ShowW("BtnRzStcDel", have);
        ShowW("RzStcSub", have);
        SetLabel("BtnRzStcDelText", Tr("#STR_OZL_VPP_CFG_DEL_ST"), 0);
        if (have)
            StcPaintHead(pick);
        else
            SetLabel("RzStcHead", Tr(why), 0);
    }

    protected void CfgFillForm()
    {
        if (!CfgObj() || CfgCount() == 0)
            return;
        int pick = CfgPicked();
        array<string> names = new array<string>();
        CfgFields(names);
        m_RzFill = true;
        for (int f = 0; f < names.Count(); f++)
        {
            if (names[f] == "RzOwDevices")
                OwDevFill(CfgGet(pick, f));
            else
                SetEdit(names[f], CfgGet(pick, f));
        }
        m_RzFill = false;
    }

    // The picked row of the open page's list: its frame, and the others plain.
    protected void CfgMark(OZ_VppFlexRows rows, string root)
    {
        if (!rows)
            return;
        string pick = CfgPicked().ToString();
        for (int i = 0; i < rows.Count(); i++)
            CfgRowPick(rows.Row(i), root, rows.Key(i) == pick);
    }

    // A row of the open page's list was clicked: that entry is the picked one.
    protected void CfgPick(int at)
    {
        if (at < 0 || at >= CfgCount())
            return;
        m_CfgPick.Set(m_RzTab, at);
        m_Ed.EndGesture();
        if (m_RzTab == "owners")
            CfgMark(m_OwRows, "OZL_VppOwRow");
        else if (m_RzTab == "modules")
            CfgMark(m_MoRows, "OZL_VppMoRow");
        else
            CfgMark(m_StcRows, "OZL_VppStcRow");
        CfgPaintHead();
        CfgFillForm();
    }

    // ================================================= OWNERS

    // The faction's name as the source of factions gives it (the window asks once,
    // `identity`); nothing when the source does not know the id or names it by its id.
    protected string OwName(string id)
    {
        if (!m_IdFactions || !m_IdNames)
            return "";
        int at = m_IdFactions.Find(id);
        if (at < 0 || at >= m_IdNames.Count())
            return "";
        string named = m_IdNames[at];
        if (named == id)
            return "";
        return named;
    }

    protected void OwRebuild()
    {
        if (!m_OwRows)
        {
            Widget host = M_SUB_WIDGET.FindAnyWidget("RzOwListRows");
            if (!host)
                return;
            m_OwRows = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_ow_row.layout", "OZL_VppOwRow", 387, 54);
        }

        m_OwRows.Clear();
        OZL_Owners ow = OZL_Owners.Cast(CfgObj());
        if (!ow)
        {
            SetLabel("RzOwCount", Tr("#STR_OZL_ED_HINT_LOADING"), 0);
            return;
        }
        int pick = CfgPicked();
        int n = ow.Owners.Count();
        int i;
        for (i = 0; i < n && i < CFG_LIST_MAX; i++)
        {
            Widget row = m_OwRows.Add(i.ToString());
            if (row)
                OwPaintRow(row, ow, i, i == pick);
        }
        m_OwRows.Fit();
        for (i = 0; i < m_OwRows.Count(); i++)
            OwPlaceRow(m_OwRows.Row(i));

        string inDraft = Tr("#STR_OZL_VPP_OW_COUNT");
        string cut = CfgCutNote(n);
        SetLabel("RzOwCount", inDraft + n.ToString() + cut, 0);
    }

    // A row: the faction's id and name, its tree window and first terminal, how many
    // stations it runs.
    protected void OwPaintRow(Widget row, OZL_Owners ow, int i, bool picked)
    {
        CfgRowPick(row, "OZL_VppOwRow", picked);
        OZL_OwnerDef o = ow.Owners[i];
        if (!o)
            return;
        string named = OwName(o.Id);
        CfgPart(row, "OwRowId", o.Id);
        CfgPart(row, "OwRowName", named);
        Widget dash = row.FindAnyWidget("OwRowDash");
        if (dash)
            dash.Show(named != "");

        string windowWord = Tr("#STR_OZL_VPP_OW_ROW_WINDOW");
        string sub = windowWord + ow.SkinOf(o.Id) + " · ";
        if (o.TerminalClasses.Count() == 0)
        {
            string none = Tr("#STR_OZL_VPP_OW_ROW_NO_TERMINAL");
            sub = sub + none;
        }
        else
        {
            string terminalWord = Tr("#STR_OZL_VPP_OW_ROW_TERMINAL");
            sub = sub + terminalWord + o.TerminalClasses[0];
            int more = o.TerminalClasses.Count() - 1;
            if (more > 0)
                sub = sub + " +" + more.ToString();
        }
        CfgPart(row, "OwRowSub", sub);
        CfgPart(row, "OwRowCount", o.DeviceClasses.Count().ToString());
    }

    // The row's first line: the dash after the id's words, the name after the dash.
    protected void OwPlaceRow(Widget row)
    {
        if (!row)
            return;
        Widget id = row.FindAnyWidget("OwRowId");
        Widget dash = row.FindAnyWidget("OwRowDash");
        Widget name = row.FindAnyWidget("OwRowName");
        if (!id || !dash || !name)
            return;
        float s = Px();
        float at = CfgPutAfter(id, dash, 8);
        float nx;
        float ny;
        name.GetPos(nx, ny);
        name.SetPos(at + 19 * s, ny);

        // The name has the room up to the count on the right.
        Widget count = row.FindAnyWidget("OwRowCount");
        if (count)
        {
            float cx;
            float cy;
            count.GetPos(cx, cy);
            float nw;
            float nh;
            name.GetSize(nw, nh);
            float room = cx - at - 25 * s;
            if (room < 0)
                room = 0;
            name.SetSize(room, nh);
        }
    }

    // The picked row again from the draft (a field of it was typed in).
    protected void OwRepaintPicked()
    {
        OZL_Owners ow = OZL_Owners.Cast(CfgObj());
        if (!ow || !m_OwRows)
            return;
        int pick = CfgPicked();
        Widget row = m_OwRows.Row(m_OwRows.Find(pick.ToString()));
        if (!row)
            return;
        OwPaintRow(row, ow, pick, true);
        OwPlaceRow(row);
    }

    protected void OwPaintHead(int pick)
    {
        OZL_OwnerDef o = OZL_Owners.Cast(CfgObj()).Owners[pick];
        if (!o)
            return;
        string head = o.Id;
        string named = OwName(o.Id);
        if (named != "")
            head = head + " — " + named;
        SetLabel("RzOwHead", head, 0);

        string termsWord = Tr("#STR_OZL_VPP_OW_CHIP_TERMS");
        string devsWord = Tr("#STR_OZL_VPP_OW_CHIP_DEVICES");
        string chip = termsWord + o.TerminalClasses.Count().ToString() + " · ";
        chip = chip + devsWord + o.DeviceClasses.Count().ToString();
        SetLabel("RzOwChipText", chip, 0);
    }

    // The chip hugs its words and stands 12 units after the head's.
    protected void OwPlace()
    {
        Widget head = M_SUB_WIDGET.FindAnyWidget("RzOwHead");
        Widget chip = M_SUB_WIDGET.FindAnyWidget("RzOwChip");
        Widget chipBg = M_SUB_WIDGET.FindAnyWidget("RzOwChipBg");
        TextWidget chipText = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzOwChipText"));
        if (!head || !chip || !chipText)
            return;
        if (OZ_VppFlex.TextWidth(chipText) > 0)
            OZ_VppFlex.Hug(chip, chipBg, chipText, 8 * Px());
        CfgPutAfter(head, chip, 12);
    }

    // The tree window picker of the picked owner: a button per window and one for "by
    // the faction's id", the one in force lit. A window's second line says what its
    // nodes look like and which way its tree grows.
    protected void PaintSkins(int pick)
    {
        OZ_ConfigBase c = CfgObj();
        if (!c)
            return;
        OZL_OwnerDef o = OZL_Owners.Cast(c).Owners[pick];
        if (!o)
            return;
        if (m_CfgSkinDirs.Count() != m_CfgSkins.Count())
        {
            m_CfgSkinDirs.Clear();
            for (int d = 0; d < m_CfgSkins.Count(); d++)
            {
                // The skin made into a local first: Make returns a new object from a
                // non-ref function, and a field is not read off it in one chain.
                string dir = "";
                if (m_CfgSkins[d] != "")
                {
                    OZL_TreeSkin sk = OZL_TreeSkins.Make(m_CfgSkins[d]);
                    if (sk)
                        dir = sk.Dir;
                }
                m_CfgSkinDirs.Insert(dir);
            }
        }
        for (int i = 0; i < m_CfgSkins.Count(); i++)
        {
            string n = i.ToString();
            string caption = Tr("#STR_OZL_VPP_SKIN_BY_ID");
            string how = Tr("#STR_OZL_VPP_SKIN_EMPTY");
            if (m_CfgSkins[i] != "")
            {
                caption = m_CfgSkins[i];
                string up = m_CfgSkins[i];
                up.ToUpper();
                string shape = Tr("#STR_OZL_VPP_SKIN_S_" + up);
                string way = SkinDir(m_CfgSkinDirs[i]);
                how = shape + " · " + way;
            }
            SetLabel("RzSkinName" + n, caption, 0);
            SetLabel("RzSkinHow" + n, how, 0);

            int rim = ARGB(255, 60, 60, 58);
            int ground = ARGB(255, 19, 19, 18);
            if (o.Skin == m_CfgSkins[i])
            {
                rim = ARGB(255, 232, 120, 43);
                ground = ARGB(255, 53, 35, 22);
            }
            OZ_VppFlex.Paint(M_SUB_WIDGET, "BtnRzSkin_" + n + "Edge", rim);
            OZ_VppFlex.Paint(M_SUB_WIDGET, "BtnRzSkin_" + n + "Bg", ground);
        }
    }

    // The picker's button i: that window for the picked owner, one undo step.
    protected void CfgPickSkin(int i)
    {
        OZ_ConfigBase c = CfgObj();
        if (!c || m_RzTab != "owners" || CfgCount() == 0 || i < 0 || i >= m_CfgSkins.Count())
            return;
        OZL_OwnerDef o = OZL_Owners.Cast(c).Owners[CfgPicked()];
        if (!o || o.Skin == m_CfgSkins[i])
            return;
        string tag = CfgTag();
        m_Ed.BeginOnce(tag, "");
        o.Skin = m_CfgSkins[i];
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        PaintSkins(CfgPicked());
        OwRepaintPicked();
        PaintRzBar();
        PaintSummary();
    }

    // ------------------------------------------------- the stations box
    //
    // A multiline edit box (the board's three rows). Two things it does not do by itself
    // (dayz-modding gui-layouts.md, "MultilineEditBox"): text put in by script is never
    // wrapped, and nobody is told that it was typed in. So the list goes in with a line
    // break after a comma wherever the next class would not fit, a line break reads
    // back as a comma, and Tick compares the text with what was last seen.

    protected MultilineEditBoxWidget OwDevBox()
    {
        return MultilineEditBoxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzOwDevices"));
    }

    protected string OwDevText()
    {
        string text = "";
        MultilineEditBoxWidget box = OwDevBox();
        if (box)
            box.GetText(text);
        return text;
    }

    // "a, b, c" into the box, broken into lines that fit it: an edit box draws its
    // face at the atlas's own size, about 7 pixels a letter, whatever the screen.
    protected void OwDevFill(string list)
    {
        MultilineEditBoxWidget box = OwDevBox();
        if (!box)
            return;
        float w;
        float h;
        box.GetSize(w, h);
        int perLine = (w - 16) / 7.2;
        if (perLine < 40)
            perLine = 40;
        if (perLine > 190)
            perLine = 190;

        array<string> items = new array<string>();
        OZL_EdTree.ParseList(list, items);
        string text = "";
        int col = 0;
        for (int i = 0; i < items.Count(); i++)
        {
            string item = items[i];
            if (i < items.Count() - 1)
                item = item + ",";
            int len = item.LengthUtf8();
            if (col > 0 && col + 1 + len > perLine)
            {
                text = text + "\n";
                col = 0;
            }
            else if (col > 0)
            {
                text = text + " ";
                col++;
            }
            text = text + item;
            col = col + len;
        }
        box.SetText(text);
        m_OwDevSeen = OwDevText();
    }

    // What the box holds as one comma-separated line. A line break stands for a comma,
    // except after a line of 200 letters: there the engine broke a long line itself,
    // maybe inside a class name.
    protected string OwDevFlat(string raw)
    {
        array<string> lines = new array<string>();
        raw.Split("\n", lines);
        string flat = "";
        for (int i = 0; i < lines.Count(); i++)
        {
            string line = lines[i];
            flat = flat + line;
            if (line.LengthUtf8() < 200)
                flat = flat + ",";
        }
        return flat;
    }

    // Every frame while the window is open (the core's Tick): the open page laid once
    // more when its second pass is due, and the stations box of the open OWNERS page
    // followed.
    override void Tick()
    {
        super.Tick();
        if (!M_SUB_WIDGET || !m_Ed || !m_CfgPick)
            return;
        if (m_CfgRefit > 0)
        {
            m_CfgRefit--;
            if (m_CfgRefit == 0 && RzShown())
                CfgLayOpen();
        }
        if (m_RzFill || m_RzTab != "owners" || !RzShown())
            return;
        if (OwDevText() == m_OwDevSeen)
            return;
        OnCfgField(2);
    }

    // ================================================= MODULES

    protected void MoRebuild()
    {
        Widget host = M_SUB_WIDGET.FindAnyWidget("RzMoListRows");
        if (!host)
            return;
        if (!m_MoHeads)
            m_MoHeads = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_mo_group.layout", "OZL_VppMoGroup", 427, 30);
        if (!m_MoRows)
            m_MoRows = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_mo_row.layout", "OZL_VppMoRow", 427, 46);

        m_MoHeads.Clear();
        m_MoRows.Clear();
        OZL_Modules mo = OZL_Modules.Cast(CfgObj());
        if (!mo)
        {
            SetLabel("RzMoCount", Tr("#STR_OZL_ED_HINT_LOADING"), 0);
            return;
        }

        // The lines in the order of the types of points, then the lines no type names,
        // the modules with no line last; each module's line read once.
        int n = mo.Modules.Count();
        array<string> lineOf = new array<string>();
        array<string> lines = new array<string>();
        int i;
        OZL_PointTypes pts = DraftPointTypes();
        if (pts)
        {
            for (i = 0; i < pts.PointTypes.Count(); i++)
            {
                if (pts.PointTypes[i] && lines.Find(pts.PointTypes[i].Id) == -1)
                    lines.Insert(pts.PointTypes[i].Id);
            }
        }
        bool loose = false;
        for (i = 0; i < n; i++)
        {
            string line = "";
            if (mo.Modules[i])
                line = OZL_Lines.LineOf(mo.Modules[i].Classname);
            lineOf.Insert(line);
            if (line == "")
                loose = true;
            else if (lines.Find(line) == -1)
                lines.Insert(line);
        }
        if (loose)
            lines.Insert("");

        int pick = CfgPicked();
        int shown = 0;
        int linesWith = 0;
        for (int g = 0; g < lines.Count(); g++)
        {
            // Only a line that has modules counts; a filter may leave it none to show.
            int inLine = 0;
            int inShown = 0;
            for (i = 0; i < n; i++)
            {
                if (lineOf[i] != lines[g] || !mo.Modules[i])
                    continue;
                inLine++;
                if (MoMatches(mo.Modules[i]))
                    inShown++;
            }
            if (inLine > 0)
                linesWith++;
            if (inShown == 0 || shown >= CFG_LIST_MAX)
                continue;

            Widget head = m_MoHeads.Add("g:" + lines[g]);
            if (head)
            {
                string caption = Tr("#STR_OZL_VPP_MO_GROUP_NONE");
                if (lines[g] != "")
                    caption = CfgLineName(lines[g]);
                OZ_VppFlex.Paint(head, "MoGroupDotBg", CfgLineInk(lines[g]));
                CfgPart(head, "MoGroupName", caption);
                CfgPart(head, "MoGroupCount", "· " + inLine.ToString());
            }
            for (i = 0; i < n; i++)
            {
                if (lineOf[i] != lines[g] || !mo.Modules[i] || !MoMatches(mo.Modules[i]))
                    continue;
                if (shown >= CFG_LIST_MAX)
                    continue;
                Widget row = m_MoRows.Add(i.ToString());
                if (row)
                    MoPaintRow(row, mo.Modules[i], i == pick);
                shown++;
            }
        }
        m_MoHeads.Fit();
        m_MoRows.Fit();
        MoPlaceHeads();

        // The count's line is short (it stands beside the search box): every module and
        // how many lines they make, or how many of the modules the list shows -- after a
        // search, or when it draws its most.
        string count;
        if (m_MoFind == "" && shown >= n)
        {
            string modsWord = Tr("#STR_OZL_VPP_MO_COUNT");
            string linesWord = Tr("#STR_OZL_VPP_MO_COUNT_LINES");
            count = modsWord + n.ToString() + linesWord + linesWith.ToString();
        }
        else
        {
            string ofWord = Tr("#STR_OZL_VPP_FOUND_OF");
            count = shown.ToString() + ofWord + n.ToString();
        }
        SetLabel("RzMoCount", count, 0);
    }

    // Does the search box keep this module: its class or its name in the game holds
    // what was typed.
    protected bool MoMatches(OZL_ModuleDef m)
    {
        if (m_MoFind == "")
            return true;
        if (CfgHas(m.Classname, m_MoFind))
            return true;
        return CfgHas(OZL_EdChains.ItemName(m.Classname), m_MoFind);
    }

    // A caption row's count stands after its line's name.
    protected void MoPlaceHeads()
    {
        if (!m_MoHeads)
            return;
        for (int i = 0; i < m_MoHeads.Count(); i++)
        {
            Widget head = m_MoHeads.Row(i);
            if (!head)
                continue;
            CfgPutAfter(head.FindAnyWidget("MoGroupName"), head.FindAnyWidget("MoGroupCount"), 8);
        }
    }

    // A class's name in the game; nothing when the client does not know the class.
    protected string CfgItemName(string cls)
    {
        if (cls == "")
            return "";
        string named = OZL_EdChains.ItemName(cls);
        if (named == cls)
            return "";
        return named;
    }

    protected void MoPaintRow(Widget row, OZL_ModuleDef m, bool picked)
    {
        CfgRowPick(row, "OZL_VppMoRow", picked);
        string cls = m.Classname;
        if (cls == "")
            cls = Tr("#STR_OZL_VPP_NO_CLASS");
        CfgPart(row, "MoRowClass", cls);
        CfgPart(row, "MoRowName", CfgItemName(m.Classname));
        CfgPart(row, "MoRowPurity", "+" + CfgPct(m.PurityBonus));
        string twoWord = Tr("#STR_OZL_VPP_MO_ROW_DOUBLE");
        CfgPart(row, "MoRowDouble", twoWord + CfgPct(m.DoubleChance));
    }

    // The head of the picked module: its class, its name in the game, the line its
    // ozlLine names; and the three facts under the fields -- the line's sample purity
    // before and after this module, its chance of two, how many modules the line has.
    protected void MoPaintHead(int pick)
    {
        OZL_Modules mo = OZL_Modules.Cast(CfgObj());
        OZL_ModuleDef m = mo.Modules[pick];
        if (!m)
            return;
        string cls = m.Classname;
        if (cls == "")
            cls = Tr("#STR_OZL_VPP_NO_CLASS");
        SetLabel("RzMoHead", cls, 0);
        SetLabel("RzMoSub", CfgItemName(m.Classname), 0);

        string line = OZL_Lines.LineOf(m.Classname);
        string lineName = CfgLineName(line);
        string chip = Tr("#STR_OZL_VPP_MO_NO_LINE");
        if (line != "")
        {
            string lineWord = Tr("#STR_OZL_VPP_MO_LINE");
            string fromWord = Tr("#STR_OZL_VPP_MO_LINE_FROM");
            chip = lineWord + "«" + lineName + "»" + fromWord;
        }
        SetLabel("RzMoLineText", chip, 0);
        bool hasLine = (line != "");
        m_MoHasLine = hasLine;
        ShowW("RzMoLineDot", hasLine);
        OZ_VppFlex.Paint(M_SUB_WIDGET, "RzMoLineDotBg", CfgLineInk(line));

        float base = OZL_Const.DEFAULT_PURITY;
        OZL_PointTypes pts = DraftPointTypes();
        OZL_PointType pt = null;
        if (pts)
            pt = pts.Find(line);
        if (pt && pt.BasePurity > 0)
            base = pt.BasePurity;
        float after = base + m.PurityBonus;
        if (after > 1)
            after = 1;
        SetLabel("RzMoFactPurity", CfgPct(base) + " → " + CfgPct(after), 0);
        SetLabel("RzMoFactDouble", CfgPct(m.DoubleChance), 0);

        int inLine = 0;
        for (int i = 0; i < mo.Modules.Count(); i++)
        {
            if (mo.Modules[i] && OZL_Lines.LineOf(mo.Modules[i].Classname) == line)
                inLine++;
        }
        string inWord = Tr("#STR_OZL_VPP_MO_T_NO_LINE");
        if (line != "")
        {
            string countWord = Tr("#STR_OZL_VPP_MO_T_COUNT");
            inWord = countWord + "«" + lineName + "»";
        }
        SetLabel("RzMoFactLine", inWord, 0);
        SetLabel("RzMoFactCount", inLine.ToString(), 0);
    }

    // The line's chip hugs its words (a dot before them when the module has a line) and
    // stands 10 units after the module's name.
    protected void MoPlace()
    {
        Widget sub = M_SUB_WIDGET.FindAnyWidget("RzMoSub");
        Widget chip = M_SUB_WIDGET.FindAnyWidget("RzMoLine");
        Widget chipBg = M_SUB_WIDGET.FindAnyWidget("RzMoLineBg");
        Widget dot = M_SUB_WIDGET.FindAnyWidget("RzMoLineDot");
        Widget text = M_SUB_WIDGET.FindAnyWidget("RzMoLineText");
        if (!sub || !chip || !text)
            return;
        float s = Px();
        float lead = 8 * s;
        if (dot && m_MoHasLine)
            lead = 23 * s;
        float tw = CfgFitText(text);
        float x;
        float y;
        text.GetPos(x, y);
        text.SetPos(lead, y);
        if (tw > 0)
        {
            float w;
            float h;
            chip.GetSize(w, h);
            w = lead + tw + 8 * s;
            chip.SetSize(w, h);
            if (chipBg)
                chipBg.SetSize(w, h);
        }

        // With no name before it the chip starts the line.
        float sx;
        float sy;
        sub.GetPos(sx, sy);
        float sw = CfgFitText(sub);
        float cx;
        float cy;
        chip.GetPos(cx, cy);
        if (sw > 0)
            chip.SetPos(sx + sw + 10 * s, cy);
        else
            chip.SetPos(sx, cy);
    }

    // ================================================= STATICS

    protected void StcRebuild()
    {
        if (!m_StcRows)
        {
            Widget host = M_SUB_WIDGET.FindAnyWidget("RzStcListRows");
            if (!host)
                return;
            m_StcRows = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_stc_row.layout", "OZL_VppStcRow", 427, 44);
        }

        m_StcRows.Clear();
        OZL_StaticsConfig sc = OZL_StaticsConfig.Cast(CfgObj());
        if (!sc)
        {
            SetLabel("RzStcCount", Tr("#STR_OZL_ED_HINT_LOADING"), 0);
            return;
        }
        int pick = CfgPicked();
        int n = sc.Entries.Count();
        for (int i = 0; i < n; i++)
        {
            OZL_StaticEntry e = sc.Entries[i];
            if (!e || !StcMatches(e))
                continue;
            if (m_StcRows.Count() >= CFG_LIST_MAX)
                continue;
            Widget row = m_StcRows.Add(i.ToString());
            if (row)
                StcPaintRow(row, e, i == pick);
        }
        m_StcRows.Fit();

        // The count's line is short (it stands beside the search box): every entry, or
        // how many of them the list shows -- after a search, or when it draws its most.
        int drawn = m_StcRows.Count();
        string count;
        if (m_StcFind == "" && drawn >= n)
        {
            string entries = Tr("#STR_OZL_VPP_CFG_COUNT");
            count = entries + n.ToString();
        }
        else
        {
            string ofWord = Tr("#STR_OZL_VPP_FOUND_OF");
            count = drawn.ToString() + ofWord + n.ToString();
        }
        SetLabel("RzStcCount", count, 0);
    }

    protected bool StcMatches(OZL_StaticEntry e)
    {
        if (m_StcFind == "")
            return true;
        if (CfgHas(e.Id, m_StcFind))
            return true;
        return CfgHas(e.ClassName, m_StcFind);
    }

    protected void StcPaintRow(Widget row, OZL_StaticEntry e, bool picked)
    {
        CfgRowPick(row, "OZL_VppStcRow", picked);
        CfgPart(row, "StcRowId", e.Id);
        string cls = e.ClassName;
        if (cls == "")
            cls = Tr("#STR_OZL_VPP_NO_CLASS");
        CfgPart(row, "StcRowClass", cls);
    }

    // The head of the picked static: its id, its class and the class's name in the game.
    protected void StcPaintHead(int pick)
    {
        OZL_StaticEntry e = OZL_StaticsConfig.Cast(CfgObj()).Entries[pick];
        if (!e)
            return;
        SetLabel("RzStcHead", e.Id, 0);
        string sub = e.ClassName;
        if (sub == "")
            sub = Tr("#STR_OZL_VPP_NO_CLASS");
        string named = CfgItemName(e.ClassName);
        if (named != "")
            sub = sub + " · " + named;
        SetLabel("RzStcSub", sub, 0);
    }

    // The admin's position and heading into a static's entry.
    protected void HereInto(OZL_StaticEntry e)
    {
        PlayerBase p = PlayerBase.Cast(GetGame().GetPlayer());
        if (!p)
            return;
        vector pos = p.GetPosition();
        e.Pos.Clear();
        e.Pos.Insert(pos[0]);
        e.Pos.Insert(pos[1]);
        e.Pos.Insert(pos[2]);
        vector ori = p.GetOrientation();
        e.Yaw = ori[0];
    }

    // WHERE I STAND: the picked static takes the admin's place, one undo step.
    protected void CfgHere()
    {
        OZ_ConfigBase c = CfgObj();
        if (!c || m_RzTab != "statics" || CfgCount() == 0)
            return;
        OZL_StaticEntry e = OZL_StaticsConfig.Cast(c).Entries[CfgPicked()];
        if (!e)
            return;
        string tag = CfgTag();
        m_Ed.BeginOnce(tag, "");
        HereInto(e);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        CfgFillForm();
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_CFG_ST_PLACED") + e.Id);
    }

    // ================================================= OWNERS, MODULES, STATICS: edits

    // Field f of the picked entry changed: one snapshot per field, the row and the head
    // follow; the fields themselves are left as typed.
    protected void OnCfgField(int f)
    {
        if (!CfgObj() || CfgCount() == 0)
            return;
        array<string> names = new array<string>();
        CfgFields(names);
        if (f < 0 || f >= names.Count())
            return;
        string value;
        if (names[f] == "RzOwDevices")
        {
            m_OwDevSeen = OwDevText();
            value = OwDevFlat(m_OwDevSeen);
        }
        else
            value = GetEdit(names[f]);

        string tag = CfgTag();
        m_Ed.BeginOnce(tag, "cfg:" + m_RzTab + ":" + f.ToString());
        CfgSet(CfgPicked(), f, value);
        m_Ed.Commit(tag);

        if (m_RzTab == "owners")
            OwRepaintPicked();
        else if (m_RzTab == "modules")
        {
            // A module's class names its line: the list is grouped by it.
            if (f == 0)
                MoRebuild();
            else if (m_MoRows)
            {
                Widget row = m_MoRows.Row(m_MoRows.Find(CfgPicked().ToString()));
                OZL_ModuleDef m = OZL_Modules.Cast(CfgObj()).Modules[CfgPicked()];
                if (row && m)
                    MoPaintRow(row, m, true);
            }
        }
        else if (m_StcRows)
        {
            Widget srow = m_StcRows.Row(m_StcRows.Find(CfgPicked().ToString()));
            OZL_StaticEntry e = OZL_StaticsConfig.Cast(CfgObj()).Entries[CfgPicked()];
            if (srow && e)
                StcPaintRow(srow, e, true);
        }
        CfgPaintHead();
        PaintRzBar();
        PaintSummary();
    }

    // A search box was typed in: the list keeps what fits, and the first of it is
    // picked when the picked entry is no longer on the list.
    protected void CfgFindChanged()
    {
        if (m_RzTab == "modules")
            m_MoFind = CfgFindText("RzMoFind");
        else if (m_RzTab == "statics")
            m_StcFind = CfgFindText("RzStcFind");
        else
            return;
        m_Ed.EndGesture();

        RepaintCfg(false);
        OZ_VppFlexRows rows = m_StcRows;
        if (m_RzTab == "modules")
            rows = m_MoRows;
        if (!rows || rows.Count() == 0)
            return;
        if (rows.Find(CfgPicked().ToString()) != -1)
            return;
        CfgPick(rows.Key(0).ToInt());
    }

    // A free Id for a new entry: <base>, <base>_2, ... (field 0 is the Id).
    protected string FreeCfgId(string base)
    {
        int count = CfgCount();
        for (int n = 1; n < 1000; n++)
        {
            string id = base;
            if (n > 1)
                id = base + "_" + n.ToString();
            bool taken = false;
            for (int i = 0; i < count; i++)
            {
                if (CfgGet(i, 0) == id)
                    taken = true;
            }
            if (!taken)
                return id;
        }
        return base + "_new";
    }

    // The head's button: a new entry at the end of the file, picked at once. A search
    // that would hide it is cleared.
    protected void CfgAdd()
    {
        OZ_ConfigBase c = CfgObj();
        if (!c)
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }
        string tag = CfgTag();
        m_Ed.BeginOnce(tag, "");
        string added = "";
        if (m_RzTab == "owners")
        {
            OZL_OwnerDef o = new OZL_OwnerDef();
            o.Id = FreeCfgId("owner");
            OZL_Owners.Cast(c).Owners.Insert(o);
            added = o.Id;
        }
        else if (m_RzTab == "modules")
        {
            OZL_ModuleDef m = new OZL_ModuleDef();
            OZL_Modules.Cast(c).Modules.Insert(m);
            added = "module";
        }
        else
        {
            OZL_StaticEntry e = new OZL_StaticEntry();
            e.Id = FreeCfgId("static");
            HereInto(e);
            OZL_StaticsConfig.Cast(c).Entries.Insert(e);
            added = e.Id;
        }
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        m_CfgPick.Set(m_RzTab, CfgCount() - 1);

        m_RzFill = true;
        if (m_RzTab == "modules")
        {
            m_MoFind = "";
            SetEdit("RzMoFind", "");
        }
        else if (m_RzTab == "statics")
        {
            m_StcFind = "";
            SetEdit("RzStcFind", "");
        }
        m_RzFill = false;

        RepaintCfg(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_CFG_ADDED") + added);
    }

    protected void CfgDelete()
    {
        OZ_ConfigBase c = CfgObj();
        int n = CfgCount();
        if (!c || n == 0)
            return;
        int at = CfgPicked();
        m_CfgDelTab = m_RzTab;
        m_CfgDelWhat = CfgRow(at);
        string ask = Tr("#STR_OZL_VPP_ASK_DEL_" + CfgHeadKey());
        string tail = Tr("#STR_OZL_VPP_ASK_DRAFT");
        Confirm(ask + m_CfgDelWhat + "? " + tail, "#STR_OZL_VPP_YES_DELETE", "rz:cfgdel:" + at.ToString());
    }

    // The strip's "yes": the entry it asked about, if the list still holds it at that
    // row (the strip closes when the page changes, an edit may have moved the rows).
    protected void CfgDeleteNow(int at)
    {
        OZ_ConfigBase c = CfgObj();
        string what = m_CfgDelWhat;
        bool same = (c != null && m_RzTab == m_CfgDelTab);
        if (same && (at < 0 || at >= CfgCount()))
            same = false;
        if (same && CfgRow(at) != what)
            same = false;
        if (!same)
        {
            Hint(Tr("#STR_OZL_VPP_GONE") + what);
            return;
        }
        string tag = CfgTag();
        m_Ed.BeginOnce(tag, "");
        if (m_RzTab == "owners")
            OZL_Owners.Cast(c).Owners.RemoveOrdered(at);
        else if (m_RzTab == "modules")
            OZL_Modules.Cast(c).Modules.RemoveOrdered(at);
        else
            OZL_StaticsConfig.Cast(c).Entries.RemoveOrdered(at);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        RepaintCfg(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_CFG_DELETED") + what);
    }

    override void OnConfirmed(string action)
    {
        if (action.IndexOf("rz:ptdel:") == 0)
        {
            PtDeleteYes(action.Substring(9, action.Length() - 9));
            return;
        }
        if (action.IndexOf("rz:cfgdel:") == 0)
        {
            CfgDeleteNow(action.Substring(10, action.Length() - 10).ToInt());
            return;
        }
        super.OnConfirmed(action);
    }

    // ================================================= size and events

    // The open page changed its size (the frame's hook). The panes follow the window by
    // the rule their layouts carry; what this layer sized itself is sized again.
    override void RzLayPages(float pw, float ph)
    {
        super.RzLayPages(pw, ph);
        CfgLayOpen();
    }

    // What this layer fits by script on the open page: the rows of its list as wide as
    // the list, the words of its head one after another. Called after a resize and two
    // frames after a repaint; the settings layer adds its page.
    protected void CfgLayOpen()
    {
        if (!M_SUB_WIDGET || !m_CfgPick)
            return;
        int i;
        if (m_RzTab == "points")
        {
            if (m_PtRows)
                m_PtRows.Fit();
            PtPlace(PtPicked() != null);
        }
        else if (m_RzTab == "owners")
        {
            if (m_OwRows)
            {
                m_OwRows.Fit();
                for (i = 0; i < m_OwRows.Count(); i++)
                    OwPlaceRow(m_OwRows.Row(i));
            }
            OwPlace();
        }
        else if (m_RzTab == "modules")
        {
            if (m_MoHeads)
                m_MoHeads.Fit();
            if (m_MoRows)
                m_MoRows.Fit();
            MoPlaceHeads();
            MoPlace();
        }
        else if (m_RzTab == "statics")
        {
            if (m_StcRows)
                m_StcRows.Fit();
        }
    }

    override bool OnChange(Widget w, int x, int y, bool finished)
    {
        if (w && M_SUB_WIDGET && !m_RzFill && m_Ed && m_CfgPick)
        {
            string nm = w.GetName();
            if (nm == "RzPtId" || nm == "RzPtName" || nm == "RzPtColor" || nm == "RzPtSort" || nm == "RzPtPurity" || nm == "RzPtIcon")
            {
                PtOnField(nm);
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
            if (nm == "RzMoFind" || nm == "RzStcFind")
            {
                CfgFindChanged();
                return true;
            }
            if (IsCfgTab(m_RzTab) && (nm.IndexOf("RzOw") == 0 || nm.IndexOf("RzMo") == 0 || nm.IndexOf("RzStc") == 0))
            {
                array<string> names = new array<string>();
                CfgFields(names);
                int f = names.Find(nm);
                if (f != -1)
                {
                    OnCfgField(f);
                    if (finished)
                        m_Ed.EndGesture();
                    return true;
                }
            }
        }
        return super.OnChange(w, x, y, finished);
    }

    override bool OnClick(Widget w, int x, int y, int button)
    {
        if (w && M_SUB_WIDGET && m_Ed && m_CfgPick)
        {
            string nm = w.GetName();
            int at;

            // A row of a list: the rows are buttons, what they hold lets the pointer
            // through to them.
            if (nm == "OZL_VppPtRow" && m_PtRows)
            {
                at = m_PtRows.IndexOf(w);
                if (at != -1)
                    PtPick(m_PtRows.Key(at).ToInt());
                return true;
            }
            if (nm == "OZL_VppOwRow" && m_OwRows)
            {
                at = m_OwRows.IndexOf(w);
                if (at != -1)
                    CfgPick(m_OwRows.Key(at).ToInt());
                return true;
            }
            if (nm == "OZL_VppMoRow" && m_MoRows)
            {
                at = m_MoRows.IndexOf(w);
                if (at != -1)
                    CfgPick(m_MoRows.Key(at).ToInt());
                return true;
            }
            if (nm == "OZL_VppStcRow" && m_StcRows)
            {
                at = m_StcRows.IndexOf(w);
                if (at != -1)
                    CfgPick(m_StcRows.Key(at).ToInt());
                return true;
            }

            // The page heads' buttons: a new entry of the page's file.
            if (nm == "BtnRzPtAdd")
            {
                PtNew();
                return true;
            }
            if (nm == "BtnRzOwAdd" || nm == "BtnRzMoAdd" || nm == "BtnRzStcAdd")
            {
                if (IsCfgTab(m_RzTab))
                    CfgAdd();
                return true;
            }
            if (nm == "BtnRzPtDel")
            {
                PtAskDelete();
                return true;
            }
            if (nm == "BtnRzOwDel" || nm == "BtnRzMoDel" || nm == "BtnRzStcDel")
            {
                CfgDelete();
                return true;
            }
            if (nm == "BtnRzStcHere")
            {
                CfgHere();
                return true;
            }
            if (nm.IndexOf("BtnRzSkin_") == 0)
            {
                CfgPickSkin(nm.Substring(10, nm.Length() - 10).ToInt());
                return true;
            }
        }
        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
