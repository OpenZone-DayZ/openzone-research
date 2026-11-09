// Підвкладки ВЛАСНИКИ, МОДУЛІ, СТАТИКИ й НАЛАШТУВАННЯ редактора досліджень:
// одна сторінка RzPage_cfg на чотири файли -- список записів файла з
// ДОДАТИ й ВИДАЛИТИ ліворуч і поля вибраного запису праворуч. Що за поля,
// як вони звуться й читаються, каже схема вкладки нижче (CfgFields,
// CfgGet, CfgSet). НАЛАШТУВАННЯ -- один об'єкт: списку немає.
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

    // Вибраний запис у списку вкладки (свій для кожної вкладки).
    private ref map<string, int> m_CfgPick;
    private bool m_CfgDelArmed = false;

    override void OnCreate(Widget RootW)
    {
        m_CfgPick = new map<string, int>();
        super.OnCreate(RootW);
    }

    protected bool IsCfgTab(string key)
    {
        if (key == "owners" || key == "modules" || key == "statics" || key == "settings")
            return true;
        return false;
    }

    override string RzPageOf(string key)
    {
        if (IsCfgTab(key))
            return "cfg";
        return super.RzPageOf(key);
    }

    override bool RzHasPage(string key)
    {
        if (IsCfgTab(key))
            return true;
        return super.RzHasPage(key);
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

    override void ShowRzTab(string key)
    {
        m_CfgDelArmed = false;
        super.ShowRzTab(key);
    }

    // ------------------------------------------------- схема вкладок

    protected string CfgTag()
    {
        if (m_RzTab == "owners")
            return OZL_Config.TAG_OWNERS;
        if (m_RzTab == "modules")
            return OZL_Config.TAG_MODULES;
        if (m_RzTab == "statics")
            return OZL_Config.TAG_STATICS;
        return OZL_Config.TAG_SETTINGS;
    }

    protected OZ_ConfigBase CfgObj()
    {
        if (!m_Ed)
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
        if (m_RzTab == "statics")
            return OZL_StaticsConfig.Cast(c).Entries.Count();
        return 1;
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
        if (m_RzTab == "statics")
        {
            OZL_StaticEntry e = OZL_StaticsConfig.Cast(c).Entries[i];
            if (!e)
                return "?";
            return e.Id + "  -  " + e.ClassName;
        }
        return "Settings";
    }

    // Ключі stringtable назв полів і підказок, у порядку рядків форми.
    protected void CfgFields(array<string> labels, array<string> hints)
    {
        labels.Clear();
        hints.Clear();
        if (m_RzTab == "owners")
        {
            labels.Insert("#STR_OZL_ED_CFG_OW_ID");       hints.Insert("#STR_OZL_ED_CFG_OW_ID_H");
            labels.Insert("#STR_OZL_ED_CFG_OW_SKIN");     hints.Insert("#STR_OZL_ED_CFG_OW_SKIN_H");
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
        else if (m_RzTab == "statics")
        {
            labels.Insert("#STR_OZL_ED_CFG_ST_ID");       hints.Insert("");
            labels.Insert("#STR_OZL_ED_CFG_ST_CLASS");    hints.Insert("#STR_OZL_ED_CFG_ST_CLASS_H");
            labels.Insert("#STR_OZL_ED_CFG_ST_POS");      hints.Insert("#STR_OZL_ED_CFG_ST_POS_H");
            labels.Insert("#STR_OZL_ED_CFG_ST_YAW");      hints.Insert("#STR_OZL_ED_CFG_ST_YAW_H");
            labels.Insert("#STR_OZL_ED_CFG_NOTES");       hints.Insert("");
        }
        else
        {
            labels.Insert("#STR_OZL_ED_CFG_SE_OWNER");    hints.Insert("#STR_OZL_ED_CFG_SE_OWNER_H");
            labels.Insert("#STR_OZL_ED_CFG_SE_RPOST");    hints.Insert("#STR_OZL_ED_CFG_SE_POST_H");
            labels.Insert("#STR_OZL_ED_CFG_SE_BPOST");    hints.Insert("#STR_OZL_ED_CFG_SE_POST_H");
            labels.Insert("#STR_OZL_ED_CFG_SE_DEPTH");    hints.Insert("#STR_OZL_ED_CFG_SE_DEPTH_H");
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
                return o.Skin;
            if (f == 2)
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
        if (m_RzTab == "statics")
        {
            OZL_StaticEntry e = OZL_StaticsConfig.Cast(c).Entries[i];
            if (!e)
                return "";
            if (f == 0)
                return e.Id;
            if (f == 1)
                return e.ClassName;
            if (f == 2)
            {
                string p = "";
                for (int k = 0; k < e.Pos.Count(); k++)
                {
                    if (p != "")
                        p += " ";
                    p += e.Pos[k].ToString();
                }
                return p;
            }
            if (f == 3)
                return e.Yaw.ToString();
            return e.Note;
        }
        OZL_Settings s = OZL_Settings.Cast(c);
        if (f == 0)
            return s.DefaultOwner;
        if (f == 1)
            return s.ResearchPost;
        if (f == 2)
            return s.BasePost;
        return s.TreeVisibilityDepth.ToString();
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
                o.Skin = vt;
            else if (f == 2)
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
        if (m_RzTab == "statics")
        {
            OZL_StaticEntry e = OZL_StaticsConfig.Cast(c).Entries[i];
            if (!e)
                return;
            if (f == 0)
                e.Id = vt;
            else if (f == 1)
                e.ClassName = vt;
            else if (f == 2)
                ParsePos(v, e.Pos);
            else if (f == 3)
                e.Yaw = vt.ToFloat();
            else
                e.Note = v;
            return;
        }
        OZL_Settings s = OZL_Settings.Cast(c);
        if (f == 0)
            s.DefaultOwner = vt;
        else if (f == 1)
            s.ResearchPost = vt;
        else if (f == 2)
            s.BasePost = vt;
        else
            s.TreeVisibilityDepth = vt.ToInt();
    }

    // "x y z" або "x, y, z" -> три числа.
    protected void ParsePos(string text, array<float> into)
    {
        into.Clear();
        string t = text;
        t.Replace(",", " ");
        array<string> parts = new array<string>();
        t.Split(" ", parts);
        for (int i = 0; i < parts.Count(); i++)
        {
            string p = parts[i].Trim();
            if (p != "")
                into.Insert(p.ToFloat());
        }
    }

    // ------------------------------------------------- сторінка

    protected void RepaintCfg(bool fillForm)
    {
        if (!M_SUB_WIDGET || !m_CfgPick)
            return;
        bool list = (m_RzTab != "settings");
        Widget side = M_SUB_WIDGET.FindAnyWidget("RzCfgSide");
        if (side)
            side.Show(list);
        LayoutCfg();

        SetLabel("RzCfgListHead", Tr("#STR_OZL_ED_CFG_HEAD_" + CfgHeadKey()), OZ_Palette.ACCENT);

        OZ_ConfigBase c = CfgObj();
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzCfgList"));
        int pick = CfgPicked();
        int n = CfgCount();
        if (lb && list)
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

        array<string> labels = new array<string>();
        array<string> hints = new array<string>();
        CfgFields(labels, hints);
        bool have = (c && n > 0);
        string head = Tr("#STR_OZL_ED_CFG_HEAD_" + CfgHeadKey());
        if (have && list)
            head = CfgRow(pick);
        SetLabel("RzCfgHead", head, OZ_Palette.ACCENT);

        if (fillForm)
            m_RzFill = true;
        for (int f = 0; f < CFG_ROWS; f++)
        {
            Widget rowW = M_SUB_WIDGET.FindAnyWidget("RzCfgRow" + f.ToString());
            bool shown = (f < labels.Count() && have);
            if (rowW)
                rowW.Show(shown);
            if (!shown)
                continue;
            SetLabel("RzCfgLbl" + f.ToString(), Tr(labels[f]), OZ_Palette.MUTED);
            string hint = "";
            if (hints[f] != "")
                hint = Tr(hints[f]);
            SetLabel("RzCfgHint" + f.ToString(), hint, OZ_Palette.FAINT);
            if (fillForm)
                SetEdit("RzCfgFld" + f.ToString(), CfgGet(pick, f));
        }
        if (fillForm)
            m_RzFill = false;

        Widget act = M_SUB_WIDGET.FindAnyWidget("BtnRzCfgAct");
        bool hasAct = (m_RzTab == "statics" && have);
        if (act)
            act.Show(hasAct);
        if (hasAct)
            SetBtnText("BtnRzCfgAct", Tr("#STR_OZL_ED_CFG_ST_HERE"), OZ_Palette.ACCENT);

        // Кнопка й примітка -- одразу під останнім показаним полем: рядки
        // стоять на місцях, які дав генератор (шапка 22, рядок 28 + 4).
        int shownRows = 0;
        if (have)
            shownRows = labels.Count();
        float s = Px();
        float y = (26 + shownRows * 32) * s;
        if (act)
            act.SetPos(0, y);
        if (hasAct)
            y += 34 * s;
        Widget note = M_SUB_WIDGET.FindAnyWidget("RzCfgNote");
        if (note)
            note.SetPos(0, y);

        if (m_CfgDelArmed)
            SetBtnText("BtnRzCfgDel", Tr("#STR_OZL_ED_RU_DEL_AGAIN"), OZ_Palette.BAD);
        else
            SetBtnText("BtnRzCfgDel", Tr("#STR_OZL_ED_PT_DEL"), OZ_Palette.BAD);
        SetLabel("RzCfgNote", Tr("#STR_OZL_ED_CFG_NOTE_" + CfgHeadKey()), OZ_Palette.MUTED);
    }

    // Суфікс ключів stringtable вкладки: OW, MO, ST, SE.
    protected string CfgHeadKey()
    {
        if (m_RzTab == "owners")
            return "OW";
        if (m_RzTab == "modules")
            return "MO";
        if (m_RzTab == "statics")
            return "ST";
        return "SE";
    }

    protected void OnCfgField(int f)
    {
        if (!CfgObj() || CfgCount() == 0)
            return;
        string tag = CfgTag();
        m_Ed.BeginOnce(tag, "cfg:" + m_RzTab + ":" + f.ToString());
        CfgSet(CfgPicked(), f, GetEdit("RzCfgFld" + f.ToString()));
        m_CfgDelArmed = false;
        m_RzDiscardArmed = false;
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
        if (!c || m_RzTab == "settings")
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
        m_CfgDelArmed = false;
        m_RzDiscardArmed = false;
        RepaintCfg(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_CFG_ADDED") + added);
    }

    protected void CfgDelete()
    {
        OZ_ConfigBase c = CfgObj();
        int n = CfgCount();
        if (!c || m_RzTab == "settings" || n == 0)
            return;
        int at = CfgPicked();
        string what = CfgRow(at);
        if (!m_CfgDelArmed)
        {
            m_CfgDelArmed = true;
            Hint(Tr("#STR_OZL_ED_RU_DEL_ARMED") + what);
            RepaintCfg(false);
            return;
        }
        m_CfgDelArmed = false;
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
        m_RzDiscardArmed = false;
        RepaintCfg(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_CFG_DELETED") + what);
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
        m_RzDiscardArmed = false;
        RepaintCfg(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_CFG_ST_PLACED") + e.Id);
    }

    // ------------------------------------------------- розмір і події

    override void OnWindowResized(float w, float h)
    {
        super.OnWindowResized(w, h);
        if (!M_SUB_WIDGET)
            return;
        float s = Px();
        float iw = w - 2 * 20 * s;
        float ih = h - 2 * 20 * s;
        if (iw < 300 * s || ih < 200 * s)
            return;
        float ph = ih - (28 + 8 + 8 + 28 + 8 + 22) * s;
        Widget cols = M_SUB_WIDGET.FindAnyWidget("RzCfgCols");
        if (cols)
            cols.SetSize(iw, ph);
        Widget side = M_SUB_WIDGET.FindAnyWidget("RzCfgSide");
        if (side)
            side.SetSize(300 * s, ph);
        Widget list = M_SUB_WIDGET.FindAnyWidget("RzCfgList");
        if (list)
            list.SetSize(300 * s, ph - (22 + 6 + 6 + 28) * s);
        Widget bar = M_SUB_WIDGET.FindAnyWidget("RzCfgListBar");
        if (bar)
            bar.SetPos(0, ph - 28 * s);
        LayoutCfg();
    }

    // Форма -- уся ширина праворуч від списку, а без списку (НАЛАШТУВАННЯ) --
    // від лівого краю; підказки й примітка беруть те, що лишилось.
    protected void LayoutCfg()
    {
        Widget cols = M_SUB_WIDGET.FindAnyWidget("RzCfgCols");
        Widget form = M_SUB_WIDGET.FindAnyWidget("RzCfgForm");
        if (!cols || !form)
            return;
        float s = Px();
        float cw;
        float ch;
        cols.GetSize(cw, ch);
        float fx = 312 * s;
        if (m_RzTab == "settings")
            fx = 0;
        float fw = cw - fx;
        if (fw < 470 * s)
            fw = 470 * s;
        form.SetPos(fx, 0);
        form.SetSize(fw, ch);
        for (int f = 0; f < CFG_ROWS; f++)
        {
            Widget row = M_SUB_WIDGET.FindAnyWidget("RzCfgRow" + f.ToString());
            if (row)
                row.SetSize(fw, 28 * s);
            Widget hint = M_SUB_WIDGET.FindAnyWidget("RzCfgHint" + f.ToString());
            if (hint)
                hint.SetSize(fw - 470 * s, 28 * s);
        }
        Widget note = M_SUB_WIDGET.FindAnyWidget("RzCfgNote");
        if (note)
            note.SetSize(fw, 120 * s);
    }

    override bool OnItemSelected(Widget w, int x, int y, int row, int column, int oldRow, int oldColumn)
    {
        if (w && M_SUB_WIDGET && !m_ResRepaint && m_CfgPick && w.GetName() == "RzCfgList")
        {
            if (row >= 0 && row < CfgCount())
            {
                m_CfgPick.Set(m_RzTab, row);
                m_CfgDelArmed = false;
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
            if (nm == "BtnRzCfgAdd")
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
        }
        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
