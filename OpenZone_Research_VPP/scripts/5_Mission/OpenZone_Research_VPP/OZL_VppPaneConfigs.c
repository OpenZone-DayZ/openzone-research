// Сторінки ВЛАСНИКИ, МОДУЛІ й СТАТИКИ редактора досліджень: одна сторінка
// RzPage_cfg на три файли -- список записів файла ліворуч (новий запис
// додає дія в голові сторінки) і поля вибраного запису праворуч, з його
// ВИДАЛИТИ. Що за поля, як вони звуться й читаються, каже схема сторінки
// нижче (CfgFields, CfgGet, CfgSet). НАЛАШТУВАННЯ з 2026-11-12 -- окрема
// сторінка (OZL_VppPaneSettings.c): вона питає джерело фракцій, що воно знає.
//
// Переробка вікна (дизайн вікна §5.5): вікно дерева власника вибирається
// з семи скінів кнопками, а не набирається; позиція статики -- три поля
// x, y, z замість одного рядка.
//
// Окремий modded-шар OZ_VppAdminMenu, як і ЛАНЦЮГИ: ім'я файлу мусить
// сортуватися після OZL_VppPane.c (файли теки компілюються за абеткою).
//
// Дизайн: docs/specs/2026-11-09-research-editor-vpp-design.md, §8 фаза 5.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    static const int CFG_ROWS = 8;

    // Вибраний запис у списку сторінки (свій для кожної сторінки).
    private ref map<string, int> m_CfgPick;

    // What the confirm strip asked to delete: the page and the row as it read then.
    private string m_CfgDelTab = "";
    private string m_CfgDelWhat = "";

    // The tree windows the picker offers, in the order of its buttons; "" is "by the
    // faction's id". Their ways of growing come from the skins themselves, once.
    private ref array<string> m_CfgSkins;
    private ref array<string> m_CfgSkinDirs;

    override void OnCreate(Widget RootW)
    {
        m_CfgPick = new map<string, int>();
        m_CfgSkins = new array<string>();
        array<string> skins = {"", "neutral", "ecolog", "clearsky", "duty", "freedom", "sop", "bandit"};
        for (int i = 0; i < skins.Count(); i++)
            m_CfgSkins.Insert(skins[i]);
        m_CfgSkinDirs = new array<string>();
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
        if (IsCfgTab(tab))
        {
            RepaintCfg(true);
            return;
        }
        super.RepaintRzPage(tab);
    }

    // ------------------------------------------------- схема сторінок

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

    // Рядок списку для запису i.
    protected string CfgRow(int i)
    {
        OZ_ConfigBase c = CfgObj();
        if (m_RzTab == "owners")
        {
            OZL_Owners ow = OZL_Owners.Cast(c);
            OZL_OwnerDef o = ow.Owners[i];
            if (!o)
                return "?";
            return o.Id + "  -  " + ow.SkinOf(o.Id) + "  (" + o.DeviceClasses.Count().ToString() + ")";
        }
        if (m_RzTab == "modules")
        {
            OZL_ModuleDef m = OZL_Modules.Cast(c).Modules[i];
            if (!m)
                return "?";
            return m.Classname + "  +" + OZL_EdChains.Pct(m.PurityBonus);
        }
        OZL_StaticEntry e = OZL_StaticsConfig.Cast(c).Entries[i];
        if (!e)
            return "?";
        return e.Id + "  -  " + e.ClassName;
    }

    // Ключі stringtable назв полів і підказок, у порядку рядків форми.
    protected void CfgFields(array<string> labels, array<string> hints)
    {
        labels.Clear();
        hints.Clear();
        if (m_RzTab == "owners")
        {
            labels.Insert("#STR_OZL_ED_CFG_OW_ID");       hints.Insert("#STR_OZL_ED_CFG_OW_ID_H");
            labels.Insert("#STR_OZL_ED_CFG_OW_TERMS");    hints.Insert("#STR_OZL_ED_CFG_LIST_H");
            labels.Insert("#STR_OZL_ED_CFG_OW_DEVICES");  hints.Insert("#STR_OZL_ED_CFG_LIST_H");
        }
        else if (m_RzTab == "modules")
        {
            labels.Insert("#STR_OZL_ED_CFG_MO_CLASS");    hints.Insert("#STR_OZL_ED_CFG_MO_CLASS_H");
            labels.Insert("#STR_OZL_ED_CFG_MO_PURITY");   hints.Insert("#STR_OZL_ED_CFG_FRAC_H");
            labels.Insert("#STR_OZL_ED_CFG_MO_DOUBLE");   hints.Insert("#STR_OZL_ED_CFG_FRAC_H");
            labels.Insert("#STR_OZL_ED_CFG_NOTES");       hints.Insert("");
        }
        else
        {
            labels.Insert("#STR_OZL_ED_CFG_ST_ID");       hints.Insert("");
            labels.Insert("#STR_OZL_ED_CFG_ST_CLASS");    hints.Insert("#STR_OZL_ED_CFG_ST_CLASS_H");
            labels.Insert("#STR_OZL_VPP_ST_X");           hints.Insert("#STR_OZL_VPP_ST_M_H");
            labels.Insert("#STR_OZL_VPP_ST_Y");           hints.Insert("#STR_OZL_VPP_ST_M_H");
            labels.Insert("#STR_OZL_VPP_ST_Z");           hints.Insert("#STR_OZL_VPP_ST_M_H");
            labels.Insert("#STR_OZL_ED_CFG_ST_YAW");      hints.Insert("#STR_OZL_ED_CFG_ST_YAW_H");
            labels.Insert("#STR_OZL_ED_CFG_NOTES");       hints.Insert("");
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

    // ------------------------------------------------- сторінка

    protected void RepaintCfg(bool fillForm)
    {
        if (!M_SUB_WIDGET || !m_CfgPick || !IsCfgTab(m_RzTab))
            return;

        string key = CfgHeadKey();
        SetLabel("RzCfgListHead", Tr("#STR_OZL_VPP_CFG_COLS_" + key), 0);

        OZ_ConfigBase c = CfgObj();
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzCfgList"));
        int pick = CfgPicked();
        int n = CfgCount();
        if (lb)
        {
            m_ResRepaint = true;
            lb.ClearItems();
            for (int i = 0; i < n; i++)
            {
                string row = "";
                if (i == pick)
                    row = "> ";
                lb.AddItem(row + CfgRow(i), NULL, 0);
            }
            if (n == 0)
                lb.AddItem(Tr("#STR_OZL_ED_CFG_EMPTY"), NULL, 0);
            m_ResRepaint = false;
        }
        string entries = Tr("#STR_OZL_VPP_CFG_COUNT");
        SetLabel("RzCfgCount", entries + n.ToString(), 0);

        array<string> labels = new array<string>();
        array<string> hints = new array<string>();
        CfgFields(labels, hints);
        bool have = (c && n > 0);
        string head = Tr("#STR_OZL_ED_CFG_EMPTY");
        if (have)
            head = CfgRow(pick);
        SetLabel("RzCfgHead", head, 0);
        ShowW("BtnRzCfgDel", have);
        if (have)
            SetBtnText("BtnRzCfgDel", Tr("#STR_OZL_VPP_CFG_DEL_" + key), OZL_Metal.BAD);

        if (fillForm)
            m_RzFill = true;
        for (int f = 0; f < CFG_ROWS; f++)
        {
            bool shown = (f < labels.Count() && have);
            ShowW("RzCfgRow" + f.ToString(), shown);
            if (!shown)
                continue;
            SetLabel("RzCfgLbl" + f.ToString(), Tr(labels[f]), OZL_Metal.MUTED);
            string hint = "";
            if (hints[f] != "")
                hint = Tr(hints[f]);
            SetLabel("RzCfgHint" + f.ToString(), hint, OZL_Metal.FAINT);
            if (fillForm)
                SetEdit("RzCfgFld" + f.ToString(), CfgGet(pick, f));
        }
        if (fillForm)
            m_RzFill = false;

        // Under the last shown row: the page's own block -- WHERE I STAND on
        // STATICS, the tree window picker on OWNERS, what the module does on
        // MODULES -- and the note.
        int shownRows = 0;
        if (have)
            shownRows = labels.Count();
        float s = Px();
        float y = (40 + shownRows * 32 + 6) * s;

        bool hasAct = (m_RzTab == "statics" && have);
        ShowW("BtnRzCfgAct", hasAct);
        MoveW("BtnRzCfgAct", 0, y);
        if (hasAct)
        {
            SetBtnText("BtnRzCfgAct", Tr("#STR_OZL_ED_CFG_ST_HERE"), OZL_Metal.ACCENT);
            y += 38 * s;
        }

        bool skins = (m_RzTab == "owners" && have);
        ShowW("RzCfgSkins", skins);
        MoveW("RzCfgSkins", 0, y);
        if (skins)
        {
            PaintSkins(pick);
            y += 126 * s;
        }

        bool facts = (m_RzTab == "modules" && have);
        ShowW("RzCfgFacts", facts);
        MoveW("RzCfgFacts", 0, y);
        if (facts)
        {
            OZL_ModuleDef md = OZL_Modules.Cast(c).Modules[pick];
            if (md)
                SetLabel("RzCfgFacts", ModuleFacts(md), 0);
            y += 28 * s;
        }

        MoveW("RzCfgNote", 0, y);
        SetLabel("RzCfgNote", Tr("#STR_OZL_ED_CFG_NOTE_" + key), OZL_Metal.MUTED);
    }

    // Суфікс ключів stringtable сторінки: OW, MO, ST.
    protected string CfgHeadKey()
    {
        if (m_RzTab == "owners")
            return "OW";
        if (m_RzTab == "modules")
            return "MO";
        return "ST";
    }

    // The tree window picker of the picked owner: one button per skin and one for
    // "by the faction's id", the one in force lit. A skin's caption says which way
    // its tree grows.
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
                string dir = "";
                if (m_CfgSkins[d] != "")
                    dir = OZL_TreeSkins.Make(m_CfgSkins[d]).Dir;
                m_CfgSkinDirs.Insert(dir);
            }
        }
        string byId = Tr("#STR_OZL_VPP_SKIN_BY_ID");
        for (int i = 0; i < m_CfgSkins.Count(); i++)
        {
            string btn = "BtnRzSkin_" + i.ToString();
            string caption = byId;
            if (m_CfgSkins[i] != "")
            {
                string way = SkinDir(m_CfgSkinDirs[i]);
                caption = m_CfgSkins[i] + " - " + way;
            }
            SetBtnText(btn, caption, OZL_Metal.TEXT);
            PaintToggle(btn, o.Skin == m_CfgSkins[i]);
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
        RepaintCfg(false);
        PaintRzBar();
        PaintSummary();
    }

    // What the picked module does to its line's sample: the purity before and after
    // it, its chance of two, how many modules the line has.
    protected string ModuleFacts(OZL_ModuleDef m)
    {
        string line = OZL_Lines.LineOf(m.Classname);
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
        array<OZL_ModuleDef> mods = new array<OZL_ModuleDef>();
        OZL_EdChains.ModulesOf(DraftModules(), line, mods);
        string purityWord = Tr("#STR_OZL_VPP_MO_PURITY");
        string doubleWord = Tr("#STR_OZL_VPP_MO_DOUBLE");
        string countWord = Tr("#STR_OZL_VPP_MO_IN_LINE");
        string s = purityWord + OZL_EdChains.Pct(base) + " -> " + OZL_EdChains.Pct(after);
        s += "  |  " + doubleWord + OZL_EdChains.Pct(m.DoubleChance);
        s += "  |  " + countWord + mods.Count().ToString();
        return s;
    }

    protected void OnCfgField(int f)
    {
        if (!CfgObj() || CfgCount() == 0)
            return;
        string tag = CfgTag();
        m_Ed.BeginOnce(tag, "cfg:" + m_RzTab + ":" + f.ToString());
        CfgSet(CfgPicked(), f, GetEdit("RzCfgFld" + f.ToString()));
        m_Ed.Commit(tag);
        RepaintCfg(false);
        PaintRzBar();
        PaintSummary();
    }

    // Вільний Id для нового запису: <база>, <база>_2, ... (поле 0 -- Id).
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

    protected void CfgAdd()
    {
        OZ_ConfigBase c = CfgObj();
        if (!c)
            return;
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
        if (action.IndexOf("rz:cfgdel:") == 0)
        {
            CfgDeleteNow(action.Substring(10, action.Length() - 10).ToInt());
            return;
        }
        super.OnConfirmed(action);
    }

    // Позиція й напрям адміна -- у запис статики.
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
        RepaintCfg(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_CFG_ST_PLACED") + e.Id);
    }

    // ------------------------------------------------- розмір і події

    // The config page in the page area pw x ph (pixels; nothing is read back): the
    // list takes what the form leaves, the form keeps its 636 units.
    override void RzLayPages(float pw, float ph)
    {
        super.RzLayPages(pw, ph);
        if (!M_SUB_WIDGET)
            return;
        float s = Px();
        float gap = 16 * s;
        float formW = 636 * s;
        float listW = pw - formW - gap;
        if (listW < 220 * s)
            listW = 220 * s;
        SizeW("RzCfgSide", listW, ph);
        SizeW("RzCfgListHead", listW, 16 * s);
        float listH = ph - (20 + 24) * s;
        if (listH < 40 * s)
            listH = 40 * s;
        SizeW("RzCfgList", listW, listH);
        SizeW("RzCfgCount", listW, 18 * s);
        PlaceW("RzCfgForm", listW + gap, 0, formW, ph);
    }

    override bool OnItemSelected(Widget w, int x, int y, int row, int column, int oldRow, int oldColumn)
    {
        if (w && M_SUB_WIDGET && !m_ResRepaint && m_CfgPick && w.GetName() == "RzCfgList")
        {
            if (row >= 0 && row < CfgCount())
            {
                m_CfgPick.Set(m_RzTab, row);
                m_Ed.EndGesture();
                RepaintCfg(true);
            }
            return true;
        }
        return super.OnItemSelected(w, x, y, row, column, oldRow, oldColumn);
    }

    override bool OnChange(Widget w, int x, int y, bool finished)
    {
        if (w && M_SUB_WIDGET && !m_RzFill && m_Ed && m_CfgPick)
        {
            string nm = w.GetName();
            if (nm.IndexOf("RzCfgFld") == 0)
            {
                OnCfgField(nm.Substring(8, nm.Length() - 8).ToInt());
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
        }
        return super.OnChange(w, x, y, finished);
    }

    override bool OnClick(Widget w, int x, int y, int button)
    {
        if (w && M_SUB_WIDGET && m_CfgPick)
        {
            string nm = w.GetName();
            // The page head's action is a new entry on OWNERS, MODULES and STATICS.
            if (nm == "BtnRzHdAct" && IsCfgTab(m_RzTab))
            {
                CfgAdd();
                return true;
            }
            if (nm == "BtnRzCfgDel")
            {
                CfgDelete();
                return true;
            }
            if (nm == "BtnRzCfgAct")
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
