// Підвкладка ЛАНЦЮГИ редактора досліджень: правила переробки власника по
// лініях (OZL_EdChains). Конвеєр лінії -- шість карток; під ними сировина
// (правила пакувальника) за тирами вузлів із масовою правкою тіру, або
// станок таким, яким його бачить гравець; праворуч -- поля вибраного
// правила.
//
// Окремий modded-шар того самого OZ_VppAdminMenu, що й OZL_VppPane.c:
// сторінку він додає через RzHasPage / RepaintRzPage, розкладає в
// OnWindowResized. Ім'я файлу мусить сортуватися після OZL_VppPane.c --
// файли теки компілюються за абеткою, і шар, що перекриває, мусить іти
// пізніше.
//
// Дизайн: docs/specs/2026-11-09-research-editor-vpp-design.md, §1 п. 4.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    private string m_ChOwner = "";
    private string m_ChLine  = "";
    private string m_ChRule  = "";
    // Вибрана картка конвеєра: raw, packer, sample, analyzer, carrier, terminal.
    private string m_ChCard  = "raw";
    // Під картками -- станок, як його бачить гравець, а не список сировини.
    private bool   m_ChPlayer = false;
    private bool   m_RuDelArmed = false;
    private ref array<ref OZL_EdLine> m_ChLines;
    // Id правил у рядках списку сировини, у порядку рядків.
    private ref array<string> m_ChRawIds;

    override void OnCreate(Widget RootW)
    {
        m_ChLines  = new array<ref OZL_EdLine>();
        m_ChRawIds = new array<string>();
        super.OnCreate(RootW);
    }

    override bool RzHasPage(string key)
    {
        if (key == "chains")
            return true;
        return super.RzHasPage(key);
    }

    override void RepaintRzPage(string tab)
    {
        if (tab == "chains")
        {
            RepaintChains(true);
            return;
        }
        super.RepaintRzPage(tab);
    }

    override void ShowRzTab(string key)
    {
        m_RuDelArmed = false;
        super.ShowRzTab(key);
    }

    protected OZL_Rules DraftRules()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_RULES);
        if (!d || !d.Loaded)
            return null;
        return OZL_Rules.Cast(d.Obj);
    }

    protected OZL_Modules DraftModules()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_MODULES);
        if (!d || !d.Loaded)
            return null;
        return OZL_Modules.Cast(d.Obj);
    }

    protected OZL_EdLine ChLine()
    {
        for (int i = 0; i < m_ChLines.Count(); i++)
        {
            if (m_ChLines[i].Line == m_ChLine)
                return m_ChLines[i];
        }
        if (m_ChLines.Count() > 0)
            return m_ChLines[0];
        return null;
    }

    protected string LineName(OZL_PointTypes pts, string line)
    {
        if (pts)
        {
            OZL_PointType pt = pts.Find(line);
            if (pt && pt.Name != "")
                return pt.Name;
        }
        if (line == "")
            return "?";
        return line;
    }

    protected int LineColor(OZL_PointTypes pts, string line)
    {
        if (pts)
        {
            OZL_PointType pt = pts.Find(line);
            if (pt)
                return OZL_PointTypes.ColorArgb(pt.Color);
        }
        return OZ_Palette.TEXT;
    }

    protected void SetLabel(string name, string text, int color)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(name));
        if (!t)
            return;
        t.SetText(text);
        if (color != 0)
            t.SetColor(color);
    }

    // Правило, яке показує інспектор: вибране, а без нього -- за карткою.
    protected OZL_Rule CardRule(OZL_Rules rules, OZL_EdLine line)
    {
        if (m_ChRule != "")
        {
            OZL_Rule picked = rules.Find(m_ChRule);
            if (picked)
                return picked;
        }
        if (!line)
            return null;
        if (m_ChCard == "analyzer" || m_ChCard == "carrier")
        {
            if (line.Analyzers.Count() > 0)
                return rules.Find(line.Analyzers[0]);
            return null;
        }
        if (m_ChCard == "terminal")
            return null;
        if (line.Packers.Count() > 0)
            return rules.Find(line.Packers[0]);
        return null;
    }

    protected bool IsExact(OZL_Rule r)
    {
        if (!r || !r.InputItem)
            return false;
        string c = r.InputItem.Classname;
        if (c.Length() < 3)
            return false;
        return c.Substring(c.Length() - 2, 2) == "|1";
    }

    protected string Secs(float s)
    {
        int n = Math.Round(s);
        return n.ToString() + " " + Tr("#STR_OZL_ED_CH_SEC");
    }

    // ------------------------------------------------- сторінка

    // fillForm -- переписати поля правила; під час набору -- ні, бо курсор у
    // полі стрибав би в кінець.
    protected void RepaintChains(bool fillForm)
    {
        OZL_Rules rules = DraftRules();
        OZL_Owners owners = DraftOwners();
        TextListboxWidget lo = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzChOwners"));
        TextListboxWidget ll = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzChLines"));
        if (!rules || !owners || !lo || !ll)
            return;

        int i;
        bool known = false;
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            if (owners.Owners[i] && owners.Owners[i].Id == m_ChOwner)
                known = true;
        }
        if (!known && owners.Owners.Count() > 0 && owners.Owners[0])
        {
            m_ChOwner = owners.Owners[0].Id;
            m_ChLine = "";
            m_ChRule = "";
        }

        OZL_EdChains.Lines(rules, owners, m_ChOwner, m_ChLines);
        OZL_EdLine line = ChLine();
        if (line)
            m_ChLine = line.Line;
        else
            m_ChLine = "";
        if (m_ChRule != "" && !rules.Find(m_ChRule))
            m_ChRule = "";

        OZL_PointTypes pts = DraftPointTypes();
        array<ref OZL_EdLine> tmp = new array<ref OZL_EdLine>();
        m_ResRepaint = true;
        lo.ClearItems();
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            OZL_OwnerDef o = owners.Owners[i];
            if (!o)
                continue;
            OZL_EdChains.Lines(rules, owners, o.Id, tmp);
            string ol = "";
            if (o.Id == m_ChOwner)
                ol = "> ";
            ol += o.Id + "  (" + tmp.Count().ToString() + ")";
            lo.AddItem(ol, NULL, 0);
        }

        ll.ClearItems();
        for (i = 0; i < m_ChLines.Count(); i++)
        {
            OZL_EdLine l = m_ChLines[i];
            string lt = "";
            if (l.Line == m_ChLine)
                lt = "> ";
            lt += LineName(pts, l.Line) + "  (" + l.Packers.Count().ToString() + " + " + l.Analyzers.Count().ToString() + ")";
            ll.AddItem(lt, NULL, 0);
            ll.SetItemColor(i, 0, LineColor(pts, l.Line));
        }
        if (m_ChLines.Count() == 0)
            ll.AddItem(Tr("#STR_OZL_ED_CH_NO_LINES"), NULL, 0);
        m_ResRepaint = false;

        PaintChCards(line, rules, owners, pts);
        PaintChRaw(line, rules);
        if (fillForm)
            PaintChBulk(rules);
        PaintRuForm(rules, line, owners, pts, fillForm);
        bool station = PaintStation(line, rules, pts);
        ShowChMode(station);
    }

    // Під картками: сировина (редагування) або станок (як бачить гравець);
    // станка без правила -- картка терміналу -- немає, тоді рядок каже, які
    // картки його показують.
    protected void ShowChMode(bool station)
    {
        Widget raw = M_SUB_WIDGET.FindAnyWidget("RzChRaw");
        if (raw)
            raw.Show(!m_ChPlayer);
        Widget st = M_SUB_WIDGET.FindAnyWidget("RzChStation");
        bool showSt = false;
        if (m_ChPlayer && station)
            showSt = true;
        if (st)
            st.Show(showSt);
        Widget bulk = M_SUB_WIDGET.FindAnyWidget("RzChBulk");
        if (bulk)
            bulk.Show(!m_ChPlayer);
        if (m_ChPlayer && !station)
        {
            SetLabel("RzChRawHead", Tr("#STR_OZL_ED_CH_ST_NONE"), 0);
            SetBtnText("BtnRzChMode", Tr("#STR_OZL_ED_CH_MODE_EDIT"), OZ_Palette.ACCENT);
        }
        else if (m_ChPlayer)
        {
            SetLabel("RzChRawHead", Tr("#STR_OZL_ED_CH_ST_HEAD"), 0);
            SetBtnText("BtnRzChMode", Tr("#STR_OZL_ED_CH_MODE_EDIT"), OZ_Palette.ACCENT);
        }
        else
        {
            SetLabel("RzChRawHead", Tr("#STR_OZL_ED_CH_RAW_HEAD"), 0);
            SetBtnText("BtnRzChMode", Tr("#STR_OZL_ED_TR_VIEW"), OZ_Palette.ACCENT);
        }
    }

    protected void ChCard(string k, string v, string c, string s, int vColor)
    {
        SetLabel("RzChV_" + k, v, vColor);
        SetLabel("RzChC_" + k, c, OZ_Palette.MUTED);
        SetLabel("RzChS_" + k, s, OZ_Palette.MUTED);
        int kc = OZ_Palette.MUTED;
        if (k == m_ChCard)
            kc = OZ_Palette.ACCENT;
        TextWidget kind = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzChK_" + k));
        if (kind)
            kind.SetColor(kc);
    }

    protected void PaintChCards(OZL_EdLine line, OZL_Rules rules, OZL_Owners owners, OZL_PointTypes pts)
    {
        if (!line)
        {
            array<string> keys = {"raw", "packer", "sample", "analyzer", "carrier", "terminal"};
            for (int k = 0; k < keys.Count(); k++)
                ChCard(keys[k], "-", "", "", OZ_Palette.FAINT);
            return;
        }
        OZL_TreeConfig tree = DraftTree();
        int i;

        // СИРОВИНА: скільки видів і як вони лягли по тирах.
        array<int> tiers = new array<int>();
        array<int> counts = new array<int>();
        for (i = 0; i < line.Packers.Count(); i++)
        {
            int t = OZL_EdChains.TierOf(rules.Find(line.Packers[i]), tree);
            int at = tiers.Find(t);
            if (at < 0)
            {
                tiers.Insert(t);
                counts.Insert(1);
            }
            else
            {
                counts.Set(at, counts[at] + 1);
            }
        }
        string spread = "";
        for (int lo = 0; lo <= 10; lo++)
        {
            int ti = tiers.Find(lo);
            if (ti < 0)
                continue;
            if (spread != "")
                spread += "  ";
            spread += Tr("#STR_OZL_ED_CH_T") + lo.ToString() + ": " + counts[ti].ToString();
        }
        if (line.Packers.Count() > 0)
            ChCard("raw", Tr("#STR_OZL_ED_CH_KINDS") + line.Packers.Count().ToString(), spread, "", OZ_Palette.TEXT);
        else
            ChCard("raw", Tr("#STR_OZL_ED_CH_WORLD_ONLY"), "", Tr("#STR_OZL_ED_CH_NO_PACKER"), OZ_Palette.TEXT);

        // ПАКУВАЛЬНИК: станок першого правила, межі часу.
        string packDev = "";
        float tMin = -1;
        float tMax = -1;
        array<int> pointSet = new array<int>();
        for (i = 0; i < line.Packers.Count(); i++)
        {
            OZL_Rule pr = rules.Find(line.Packers[i]);
            if (!pr)
                continue;
            if (packDev == "")
                packDev = OZL_Match.StripExact(pr.Device);
            if (tMin < 0 || pr.TimeSec < tMin)
                tMin = pr.TimeSec;
            if (pr.TimeSec > tMax)
                tMax = pr.TimeSec;
            OZL_RuleOutput so = OZL_EdChains.SampleOutput(pr);
            if (so && pointSet.Find(so.Points) < 0)
                pointSet.Insert(so.Points);
        }
        if (packDev != "")
        {
            string times = Secs(tMin);
            if (tMax > tMin)
                times = Secs(tMin) + " - " + Secs(tMax);
            ChCard("packer", OZL_EdChains.ItemName(packDev), packDev, times, OZ_Palette.TEXT);
        }
        else
        {
            ChCard("packer", "-", "", Tr("#STR_OZL_ED_CH_NO_PACKER"), OZ_Palette.FAINT);
        }

        // ПРОБА: клас і бали, які несуть проби цієї лінії.
        pointSet.Sort();
        string ptsText = "";
        for (i = 0; i < pointSet.Count(); i++)
        {
            if (ptsText != "")
                ptsText += " / ";
            ptsText += "+" + pointSet[i].ToString();
        }
        if (ptsText != "")
            ptsText += " " + Tr("#STR_OZL_ED_CH_PTS");
        ChCard("sample", OZL_EdChains.ItemName(line.Sample), line.Sample, ptsText, LineColor(pts, line.Line));

        // АНАЛІЗАТОР і НОСІЙ -- з правила аналізу.
        OZL_Rule an = null;
        if (line.Analyzers.Count() > 0)
            an = rules.Find(line.Analyzers[0]);
        array<OZL_ModuleDef> mods = new array<OZL_ModuleDef>();
        OZL_EdChains.ModulesOf(DraftModules(), line.Line, mods);
        if (an)
        {
            string anDev = OZL_Match.StripExact(an.Device);
            ChCard("analyzer", OZL_EdChains.ItemName(anDev), anDev, Secs(an.TimeSec) + "  " + Tr("#STR_OZL_ED_CH_MODS") + mods.Count().ToString(), OZ_Palette.TEXT);
        }
        else
        {
            ChCard("analyzer", "-", "", "", OZ_Palette.FAINT);
        }
        if (line.Carrier != "")
            ChCard("carrier", OZL_EdChains.ItemName(line.Carrier), line.Carrier, Tr("#STR_OZL_ED_CH_CHANCE"), LineColor(pts, line.Line));
        else
            ChCard("carrier", "-", "", "", OZ_Palette.FAINT);

        // ТЕРМІНАЛ -> ПУЛ: термінал власника й тип балів лінії.
        OZL_OwnerDef def = OZL_EdChains.OwnerDef(owners, m_ChOwner);
        string term = "-";
        if (def && def.TerminalClasses.Count() > 0)
            term = def.TerminalClasses[0];
        ChCard("terminal", LineName(pts, line.Line), term, Tr("#STR_OZL_ED_CH_POOL") + m_ChOwner, LineColor(pts, line.Line));
    }

    protected void PaintChRaw(OZL_EdLine line, OZL_Rules rules)
    {
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzChRaw"));
        if (!lb)
            return;
        m_ChRawIds.Clear();
        m_ResRepaint = true;
        lb.ClearItems();
        if (!line)
        {
            m_ResRepaint = false;
            return;
        }
        OZL_TreeConfig tree = DraftTree();
        OZL_EdChains.SortedPackers(rules, tree, line, m_ChRawIds);
        for (int i = 0; i < m_ChRawIds.Count(); i++)
        {
            OZL_Rule r = rules.Find(m_ChRawIds[i]);
            if (!r)
                continue;
            string row = "";
            if (r.Id == m_ChRule)
                row = "> ";
            if (!r.Enabled)
                row += Tr("#STR_OZL_ED_CH_OFF");
            int t = OZL_EdChains.TierOf(r, tree);
            row += Tr("#STR_OZL_ED_CH_T") + t.ToString() + "    " + r.InputItem.Classname;
            if (r.InputItem.Quantity != 1)
                row += " x" + r.InputItem.Quantity.ToString();
            OZL_RuleOutput so = OZL_EdChains.SampleOutput(r);
            if (so)
                row += "    +" + so.Points.ToString() + " " + Tr("#STR_OZL_ED_CH_PTS");
            row += "    " + Secs(r.TimeSec) + "    ";
            if (r.RequiredNode == "")
            {
                row += Tr("#STR_OZL_ED_CH_NO_NODE");
            }
            else
            {
                OZL_TreeNode n = null;
                if (tree)
                    n = tree.FindNode(r.RequiredNode);
                if (n)
                    row += Tr("#STR_OZL_ED_CH_NODE") + n.Name;
                else
                    row += r.RequiredNode + Tr("#STR_OZL_ED_CH_NODE_MISSING");
            }
            lb.AddItem(row, NULL, 0);
            if (!r.Enabled)
                lb.SetItemColor(lb.GetNumItems() - 1, 0, OZ_Palette.BAD);
        }
        if (m_ChRawIds.Count() == 0)
            lb.AddItem(Tr("#STR_OZL_ED_CH_NO_RAW"), NULL, 0);
        m_ResRepaint = false;
    }

    // Рядок масової правки: тір вибраного рядка сировини, і спільні для
    // його тіру бали й вузол (різні -- поле порожнє).
    protected void PaintChBulk(OZL_Rules rules)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_Rule r = null;
        if (m_ChRawIds.Find(m_ChRule) > -1)
            r = rules.Find(m_ChRule);
        m_RzFill = true;
        if (!r)
        {
            SetLabel("RzChBulkTier", Tr("#STR_OZL_ED_CH_TIER") + "-", OZ_Palette.MUTED);
            SetEdit("RzChBulkPts", "");
            SetEdit("RzChBulkNode", "");
            m_RzFill = false;
            return;
        }
        int t = OZL_EdChains.TierOf(r, tree);
        int n = 0;
        int pts0 = -1;
        bool samePts = true;
        string node0 = "";
        bool sameNode = true;
        for (int i = 0; i < m_ChRawIds.Count(); i++)
        {
            OZL_Rule rr = rules.Find(m_ChRawIds[i]);
            if (!rr || OZL_EdChains.TierOf(rr, tree) != t)
                continue;
            OZL_RuleOutput so = OZL_EdChains.SampleOutput(rr);
            int p = 0;
            if (so)
                p = so.Points;
            if (n == 0)
            {
                pts0 = p;
                node0 = rr.RequiredNode;
            }
            else
            {
                if (p != pts0)
                    samePts = false;
                if (rr.RequiredNode != node0)
                    sameNode = false;
            }
            n++;
        }
        SetLabel("RzChBulkTier", Tr("#STR_OZL_ED_CH_TIER") + t.ToString() + " (" + n.ToString() + ")", OZ_Palette.TEXT);
        if (samePts)
            SetEdit("RzChBulkPts", pts0.ToString());
        else
            SetEdit("RzChBulkPts", "");
        if (sameNode)
            SetEdit("RzChBulkNode", node0);
        else
            SetEdit("RzChBulkNode", "");
        m_RzFill = false;
    }

    // Інспектор: поля правила, а для картки терміналу чи без правила --
    // пояснення.
    protected void PaintRuForm(OZL_Rules rules, OZL_EdLine line, OZL_Owners owners, OZL_PointTypes pts, bool fillForm)
    {
        Widget form = M_SUB_WIDGET.FindAnyWidget("RzRuForm");
        TextWidget info = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzRuInfo"));
        OZL_Rule r = CardRule(rules, line);
        if (!r)
        {
            if (form)
                form.Show(false);
            if (!info)
                return;
            info.Show(true);
            if (m_ChCard == "terminal" && line)
            {
                OZL_OwnerDef def = OZL_EdChains.OwnerDef(owners, m_ChOwner);
                string terms = "-";
                if (def)
                    terms = OZL_EdTree.ListText(def.TerminalClasses);
                float base = OZL_Const.DEFAULT_PURITY;
                OZL_PointType pt = null;
                if (pts)
                    pt = pts.Find(line.Line);
                if (pt && pt.BasePurity > 0)
                    base = pt.BasePurity;
                info.SetText(Tr("#STR_OZL_ED_CH_INFO_TERM") + terms + "\n" + Tr("#STR_OZL_ED_CH_INFO_PURITY") + OZL_EdChains.Pct(base) + "\n\n" + Tr("#STR_OZL_ED_CH_INFO_WHERE"));
            }
            else
            {
                info.SetText(Tr("#STR_OZL_ED_CH_INFO_PICK"));
            }
            return;
        }
        if (form)
            form.Show(true);
        if (info)
            info.Show(false);

        string where = "";
        OZL_RuleGroup grp = OZL_EdChains.GroupOf(rules, r.Id);
        if (grp)
            where = "   (" + grp.Id + ")";
        SetLabel("RzRuHead", r.Id + where, OZ_Palette.ACCENT);
        if (r.Enabled)
            SetBtnText("BtnRzRuEnabled", Tr("#STR_OZL_ED_RU_ON"), OZ_Palette.OK);
        else
            SetBtnText("BtnRzRuEnabled", Tr("#STR_OZL_ED_RU_OFF"), OZ_Palette.BAD);
        if (IsExact(r))
            SetBtnText("BtnRzRuExact", Tr("#STR_OZL_ED_RU_EXACT"), OZ_Palette.ALERT);
        else
            SetBtnText("BtnRzRuExact", Tr("#STR_OZL_ED_RU_KIN"), OZ_Palette.TEXT);
        if (m_RuDelArmed)
            SetBtnText("BtnRzRuDel", Tr("#STR_OZL_ED_RU_DEL_AGAIN"), OZ_Palette.BAD);
        else
            SetBtnText("BtnRzRuDel", Tr("#STR_OZL_ED_RU_DEL"), OZ_Palette.BAD);
        if (!fillForm)
            return;

        m_RzFill = true;
        SetEdit("RzRuDevice", r.Device);
        SetEdit("RzRuInput", OZL_Match.StripExact(r.InputItem.Classname));
        SetEdit("RzRuInQty", r.InputItem.Quantity.ToString());
        int ts = Math.Round(r.TimeSec);
        SetEdit("RzRuTime", ts.ToString());
        SetEdit("RzRuPurity", r.Purity.ToString());
        OZL_RuleOutput o = null;
        if (r.Outputs.Count() > 0)
            o = r.Outputs[0];
        if (o)
        {
            SetEdit("RzRuOut", o.Classname);
            SetEdit("RzRuOutPts", o.Points.ToString());
            SetEdit("RzRuOutChance", o.Chance.ToString());
        }
        else
        {
            SetEdit("RzRuOut", "");
            SetEdit("RzRuOutPts", "");
            SetEdit("RzRuOutChance", "");
        }
        SetEdit("RzRuNode", r.RequiredNode);
        SetEdit("RzRuFactions", OZL_EdTree.ListText(r.RequiredFactions));
        SetEdit("RzRuNotes", r.Notes);
        m_RzFill = false;
    }

    // Станок, як його бачить гравець: назви й описи предметів -- з
    // config.cpp і stringtable мода мовою клієнта, дія -- та, що в меню дій
    // гравця. Час, вузол і чистота -- рядком для адміна: гравець їх не бачить.
    protected bool PaintStation(OZL_EdLine line, OZL_Rules rules, OZL_PointTypes pts)
    {
        OZL_Rule r = null;
        if (line)
            r = CardRule(rules, line);
        if (!r)
            return false;
        bool analysis = (line.Analyzers.Find(r.Id) > -1);
        string dev = OZL_Match.StripExact(r.Device);
        string kind = Tr("#STR_OZL_ED_CH_K_PACKER");
        if (analysis)
            kind = Tr("#STR_OZL_ED_CH_K_ANALYZER");
        SetLabel("RzStHead", kind + "   " + OZL_EdChains.ItemName(dev), 0);

        string inName = OZL_EdChains.ItemName(r.InputItem.Classname);
        if (r.InputItem.Quantity > 1)
            inName += " x" + r.InputItem.Quantity.ToString();
        SetLabel("RzStSlotK0", Tr("#STR_OZL_ED_ST_SLOT_IN"), 0);
        SetLabel("RzStSlotV0", inName, 0);
        string outCls = "";
        if (r.Outputs.Count() > 0 && r.Outputs[0])
            outCls = r.Outputs[0].Classname;
        SetLabel("RzStSlotK1", Tr("#STR_OZL_ED_ST_SLOT_OUT"), 0);
        SetLabel("RzStSlotV1", OZL_EdChains.ItemName(outCls), LineColor(pts, line.Line));
        array<OZL_ModuleDef> mods = new array<OZL_ModuleDef>();
        OZL_EdChains.ModulesOf(DraftModules(), line.Line, mods);
        for (int m = 0; m < 2; m++)
        {
            string mv = "-";
            if (m < mods.Count())
                mv = OZL_EdChains.ItemName(mods[m].Classname);
            SetLabel("RzStSlotK" + (m + 2).ToString(), Tr("#STR_OZL_ED_ST_SLOT_MOD"), 0);
            SetLabel("RzStSlotV" + (m + 2).ToString(), mv, 0);
        }

        SetLabel("RzStAction", "[F]  " + Tr("#STR_OZL_action_start"), 0);
        // Спершу права частина: TranslateString ліворуч від "+" затирається,
        // коли права частина сама кличе переклад (Secs перекладає "с"), --
        // виміряно 2026-11-09, dayz-modding mod-structure.md, "Reading
        // strings from SCRIPT".
        string secs = Secs(r.TimeSec);
        string admin = Tr("#STR_OZL_ED_ST_ADMIN") + secs;
        if (r.RequiredNode != "")
            admin += "  -  " + Tr("#STR_OZL_ED_CH_NODE") + r.RequiredNode;
        if (!analysis)
            admin += "  -  " + Tr("#STR_OZL_ED_RU_PURITY") + " " + OZL_EdChains.Pct(OZL_Rules.StartPurity(r, dev, pts));
        SetLabel("RzStAdmin", admin, 0);

        SetLabel("RzStTipName", OZL_EdChains.ItemName(outCls), LineColor(pts, line.Line));
        string desc = OZL_EdChains.ItemDesc(outCls);
        if (desc == "")
            desc = "-";
        SetLabel("RzStTipDesc", desc, 0);
        return true;
    }

    // ------------------------------------------------- дії

    protected void ChPickCard(string k)
    {
        OZL_Rules rules = DraftRules();
        OZL_EdLine line = ChLine();
        m_ChCard = k;
        m_RuDelArmed = false;
        m_Ed.EndGesture();
        if (!rules || !line)
        {
            m_ChRule = "";
            RepaintChains(true);
            return;
        }
        if (k == "terminal")
        {
            m_ChRule = "";
        }
        else if (k == "analyzer" || k == "carrier")
        {
            m_ChRule = "";
            if (line.Analyzers.Count() > 0)
                m_ChRule = line.Analyzers[0];
        }
        else if (line.Packers.Find(m_ChRule) < 0)
        {
            m_ChRule = "";
            if (line.Packers.Count() > 0)
                m_ChRule = line.Packers[0];
        }
        RepaintChains(true);
    }

    // Масова правка тіру: бали за пробу й вузол -- усім правилам сировини
    // того тіру, що й вибраний рядок. Порожнє поле не чіпається; "-" у полі
    // вузла знімає вузол.
    protected void ChBulk()
    {
        OZL_Rules rules = DraftRules();
        OZL_TreeConfig tree = DraftTree();
        OZL_Rule r = null;
        if (rules && m_ChRawIds.Find(m_ChRule) > -1)
            r = rules.Find(m_ChRule);
        if (!r)
        {
            Hint(Tr("#STR_OZL_ED_CH_BULK_PICK"));
            return;
        }
        int t = OZL_EdChains.TierOf(r, tree);
        string pts = GetEdit("RzChBulkPts");
        string node = GetEdit("RzChBulkNode");
        pts.TrimInPlace();
        node.TrimInPlace();
        array<string> group = new array<string>();
        int i;
        for (i = 0; i < m_ChRawIds.Count(); i++)
        {
            OZL_Rule rr = rules.Find(m_ChRawIds[i]);
            if (rr && OZL_EdChains.TierOf(rr, tree) == t)
                group.Insert(rr.Id);
        }

        string tag = OZL_Config.TAG_RULES;
        m_Ed.BeginOnce(tag, "");
        for (i = 0; i < group.Count(); i++)
        {
            OZL_Rule g = rules.Find(group[i]);
            if (pts != "")
            {
                OZL_RuleOutput so = OZL_EdChains.SampleOutput(g);
                if (so)
                    so.Points = pts.ToInt();
            }
            if (node == "-")
                g.RequiredNode = "";
            else if (node != "")
                g.RequiredNode = node;
        }
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        m_RzDiscardArmed = false;
        RepaintChains(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_CH_BULK_DONE") + group.Count().ToString());
    }

    // + СИРОВИНА: копія вибраного (чи першого) правила сировини лінії з
    // порожнім входом -- адмін вписує клас; без пакувальника в лінії --
    // нове правило з пробою лінії на виході.
    protected void ChRawAdd()
    {
        OZL_Rules rules = DraftRules();
        OZL_EdLine line = ChLine();
        if (!rules || !line)
        {
            Hint(Tr("#STR_OZL_ED_CH_NO_LINES"));
            return;
        }
        OZL_Rule tmpl = null;
        if (line.Packers.Find(m_ChRule) > -1)
            tmpl = rules.Find(m_ChRule);
        if (!tmpl && line.Packers.Count() > 0)
            tmpl = rules.Find(line.Packers[0]);
        OZL_RuleGroup grp = null;
        if (tmpl)
            grp = OZL_EdChains.GroupOf(rules, tmpl.Id);
        if (!grp)
            grp = OZL_EdChains.FindGroup(rules, line.GroupId);
        if (!grp)
            return;

        string tag = OZL_Config.TAG_RULES;
        m_Ed.BeginOnce(tag, "");
        OZL_Rule r;
        if (tmpl)
        {
            r = tmpl.Copy();
            r.InputItem.Classname = "";
            r.Notes = "";
        }
        else
        {
            r = new OZL_Rule();
            OZL_RuleOutput o = new OZL_RuleOutput();
            o.Classname = line.Sample;
            o.Points = 1;
            r.Outputs.Insert(o);
            if (m_ChOwner != "")
                r.RequiredFactions.Insert(m_ChOwner);
        }
        r.Id = OZL_EdChains.FreeRuleId(rules, grp.Id + "_raw");
        grp.Rules.Insert(r);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();

        m_ChRule = r.Id;
        m_ChCard = "raw";
        m_RzDiscardArmed = false;
        RepaintChains(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_CH_RAW_ADDED") + r.Id);
    }

    protected OZL_RuleOutput FirstOutput(OZL_Rule r)
    {
        if (r.Outputs.Count() == 0)
            r.Outputs.Insert(new OZL_RuleOutput());
        if (!r.Outputs[0])
            r.Outputs.Set(0, new OZL_RuleOutput());
        return r.Outputs[0];
    }

    protected void OnRuField(string field)
    {
        OZL_Rules rules = DraftRules();
        if (!rules)
            return;
        OZL_Rule r = rules.Find(m_ChRule);
        if (!r)
            r = CardRule(rules, ChLine());
        if (!r)
            return;
        m_ChRule = r.Id;

        string tag = OZL_Config.TAG_RULES;
        m_Ed.BeginOnce(tag, "ru:" + field);
        string v = GetEdit(field);
        string vt = v.Trim();
        if (field == "RzRuDevice")
            r.Device = vt;
        else if (field == "RzRuInput")
        {
            bool exact = IsExact(r);
            r.InputItem.Classname = vt;
            if (exact && vt != "")
                r.InputItem.Classname = vt + "|1";
        }
        else if (field == "RzRuInQty")
            r.InputItem.Quantity = vt.ToInt();
        else if (field == "RzRuTime")
            r.TimeSec = vt.ToFloat();
        else if (field == "RzRuPurity")
            r.Purity = vt.ToFloat();
        else if (field == "RzRuOut")
            FirstOutput(r).Classname = vt;
        else if (field == "RzRuOutPts")
            FirstOutput(r).Points = vt.ToInt();
        else if (field == "RzRuOutChance")
            FirstOutput(r).Chance = vt.ToFloat();
        else if (field == "RzRuNode")
            r.RequiredNode = vt;
        else if (field == "RzRuFactions")
            OZL_EdTree.ParseList(v, r.RequiredFactions);
        else if (field == "RzRuNotes")
            r.Notes = v;

        m_RuDelArmed = false;
        m_RzDiscardArmed = false;
        m_Ed.Commit(tag);
        RepaintChains(false);
        PaintRzBar();
        PaintSummary();
    }

    // Перемикачі й кнопки правила: один знімок на натискання.
    protected void RuToggle(bool exact)
    {
        OZL_Rules rules = DraftRules();
        OZL_Rule r = null;
        if (rules)
            r = rules.Find(m_ChRule);
        if (!r && rules)
            r = CardRule(rules, ChLine());
        if (!r)
            return;
        m_ChRule = r.Id;
        string tag = OZL_Config.TAG_RULES;
        m_Ed.BeginOnce(tag, "");
        if (exact)
        {
            string c = OZL_Match.StripExact(r.InputItem.Classname);
            if (IsExact(r) || c == "")
                r.InputItem.Classname = c;
            else
                r.InputItem.Classname = c + "|1";
        }
        else
        {
            r.Enabled = !r.Enabled;
        }
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        m_RzDiscardArmed = false;
        RepaintChains(true);
        PaintRzBar();
        PaintSummary();
    }

    protected void RuDuplicate()
    {
        OZL_Rules rules = DraftRules();
        OZL_Rule r = null;
        if (rules)
            r = rules.Find(m_ChRule);
        if (!r && rules)
            r = CardRule(rules, ChLine());
        if (!r)
            return;
        OZL_RuleGroup grp = OZL_EdChains.GroupOf(rules, r.Id);
        if (!grp)
            return;
        string tag = OZL_Config.TAG_RULES;
        m_Ed.BeginOnce(tag, "");
        OZL_Rule c = r.Copy();
        c.Id = OZL_EdChains.FreeRuleId(rules, r.Id);
        int at = grp.Rules.Find(r);
        if (at < 0)
            grp.Rules.Insert(c);
        else
            grp.Rules.InsertAt(c, at + 1);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        m_ChRule = c.Id;
        m_RzDiscardArmed = false;
        RepaintChains(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_RU_DUPED") + c.Id);
    }

    protected void RuDelete()
    {
        OZL_Rules rules = DraftRules();
        OZL_Rule r = null;
        if (rules)
            r = rules.Find(m_ChRule);
        if (!r)
        {
            Hint(Tr("#STR_OZL_ED_CH_INFO_PICK"));
            return;
        }
        if (!m_RuDelArmed)
        {
            m_RuDelArmed = true;
            Hint(Tr("#STR_OZL_ED_RU_DEL_ARMED") + r.Id);
            RepaintChains(false);
            return;
        }
        m_RuDelArmed = false;
        OZL_RuleGroup grp = OZL_EdChains.GroupOf(rules, r.Id);
        if (!grp)
            return;
        string id = r.Id;
        string tag = OZL_Config.TAG_RULES;
        m_Ed.BeginOnce(tag, "");
        for (int i = grp.Rules.Count() - 1; i >= 0; i--)
        {
            if (grp.Rules[i] == r)
                grp.Rules.RemoveOrdered(i);
        }
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        m_ChRule = "";
        m_RzDiscardArmed = false;
        RepaintChains(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_RU_DELETED") + id);
    }

    // ------------------------------------------------- розмір і події

    // The page's size comes from the first layer (m_RzPageW / m_RzPageH); nothing
    // is read back: on the first show the widgets still measure 0 x 0.
    override void OnWindowResized(float w, float h)
    {
        super.OnWindowResized(w, h);
        if (!M_SUB_WIDGET || m_RzPageW <= 0)
            return;
        float s = Px();
        float iw = m_RzPageW;
        float ph = m_RzPageH;

        Widget cols = M_SUB_WIDGET.FindAnyWidget("RzChCols");
        if (cols)
            cols.SetSize(iw, ph);
        Widget side = M_SUB_WIDGET.FindAnyWidget("RzChSide");
        if (side)
            side.SetSize(200 * s, ph);
        float lh = ph - 246 * s;
        if (lh < 40 * s)
            lh = 40 * s;
        Widget lines = M_SUB_WIDGET.FindAnyWidget("RzChLines");
        if (lines)
            lines.SetSize(200 * s, lh);
        PlaceBtn("BtnRzChMode", 0, ph - 28 * s, 200 * s, 28 * s);

        float mw = iw - (200 + 290 + 24) * s;
        if (mw < 300 * s)
            mw = 300 * s;
        Widget mid = M_SUB_WIDGET.FindAnyWidget("RzChMid");
        if (mid)
            mid.SetSize(mw, ph);

        // Картки: в один ряд, коли влазять по 146, інакше по три.
        array<string> keys = {"raw", "packer", "sample", "analyzer", "carrier", "terminal"};
        int perRow = 3;
        if (mw >= (6 * 146 + 5 * 4) * s)
            perRow = 6;
        float cw = (mw - (perRow - 1) * 4 * s) / perRow;
        int rows = 6 / perRow;
        float pipeH = (rows * 64 + (rows - 1) * 6) * s;
        Widget pipe = M_SUB_WIDGET.FindAnyWidget("RzChPipe");
        if (pipe)
            pipe.SetSize(mw, pipeH);
        for (int i = 0; i < keys.Count(); i++)
        {
            int col = i % perRow;
            int row = i / perRow;
            Widget card = M_SUB_WIDGET.FindAnyWidget("RzChCard_" + keys[i]);
            if (!card)
                continue;
            card.SetPos(col * (cw + 4 * s), row * 70 * s);
            card.SetSize(cw, 64 * s);
            PlaceBtn("BtnRzChCard_" + keys[i], 0, 0, cw, 64 * s);
            // The card's four lines keep the layout's heights (14, 18, 14, 14).
            array<string> parts = {"RzChK_", "RzChV_", "RzChC_", "RzChS_"};
            array<float> partH = {14.0, 18.0, 14.0, 14.0};
            for (int p = 0; p < parts.Count(); p++)
            {
                Widget lab = M_SUB_WIDGET.FindAnyWidget(parts[p] + keys[i]);
                if (lab)
                    lab.SetSize(cw - 12 * s, partH[p] * s);
            }
        }

        Widget head = M_SUB_WIDGET.FindAnyWidget("RzChRawHead");
        if (head)
        {
            head.SetPos(0, pipeH + 6 * s);
            head.SetSize(mw, 22 * s);
        }
        float bodyY = pipeH + 6 * s + 22 * s + 6 * s;
        Widget body = M_SUB_WIDGET.FindAnyWidget("RzChBody");
        if (body)
        {
            body.SetPos(0, bodyY);
            body.SetSize(mw, ph - bodyY - 34 * s);
        }
        Widget bulk = M_SUB_WIDGET.FindAnyWidget("RzChBulk");
        if (bulk)
        {
            bulk.SetPos(0, ph - 28 * s);
            bulk.SetSize(mw, 28 * s);
        }
        Widget insp = M_SUB_WIDGET.FindAnyWidget("RzChInsp");
        if (insp)
            insp.SetPos(iw - 290 * s, 0);

        // Станок: слоти й підказка -- за шириною колонки (слот не ширший за
        // 220, підказка -- за 700); рамка панелі -- сусід на одиницю ширший.
        float slotW = (mw - 12 * s) / 4;
        if (slotW > 220 * s)
            slotW = 220 * s;
        for (int sl = 0; sl < 4; sl++)
        {
            string sn = "RzStSlot" + sl.ToString();
            float sx = sl * (slotW + 4 * s);
            Widget slot = M_SUB_WIDGET.FindAnyWidget(sn);
            if (slot)
            {
                slot.SetPos(sx, 24 * s);
                slot.SetSize(slotW, 44 * s);
            }
            Widget edge = M_SUB_WIDGET.FindAnyWidget(sn + "Edge");
            if (edge)
            {
                edge.SetPos(sx - s, 23 * s);
                edge.SetSize(slotW + 2 * s, 46 * s);
            }
            Widget kl = M_SUB_WIDGET.FindAnyWidget("RzStSlotK" + sl.ToString());
            if (kl)
                kl.SetSize(slotW - 10 * s, 14 * s);
            Widget vl = M_SUB_WIDGET.FindAnyWidget("RzStSlotV" + sl.ToString());
            if (vl)
                vl.SetSize(slotW - 10 * s, 22 * s);
        }
        float tipW = mw;
        if (tipW > 700 * s)
            tipW = 700 * s;
        Widget tip = M_SUB_WIDGET.FindAnyWidget("RzStTip");
        if (tip)
            tip.SetSize(tipW, 64 * s);
        Widget tipEdge = M_SUB_WIDGET.FindAnyWidget("RzStTipEdge");
        if (tipEdge)
            tipEdge.SetSize(tipW + 2 * s, 66 * s);
        Widget tipName = M_SUB_WIDGET.FindAnyWidget("RzStTipName");
        if (tipName)
            tipName.SetSize(tipW - 12 * s, 18 * s);
        Widget tipDesc = M_SUB_WIDGET.FindAnyWidget("RzStTipDesc");
        if (tipDesc)
            tipDesc.SetSize(tipW - 12 * s, 42 * s);
        // The station's three lines keep the layout's heights (20, 20, 16).
        array<string> wide = {"RzStHead", "RzStAction", "RzStAdmin"};
        array<float> wideH = {20.0, 20.0, 16.0};
        for (int wd = 0; wd < wide.Count(); wd++)
        {
            Widget wl = M_SUB_WIDGET.FindAnyWidget(wide[wd]);
            if (wl)
                wl.SetSize(mw, wideH[wd] * s);
        }
    }

    override bool OnItemSelected(Widget w, int x, int y, int row, int column, int oldRow, int oldColumn)
    {
        if (!M_SUB_WIDGET || m_ResRepaint || !w || !m_ChLines)
            return super.OnItemSelected(w, x, y, row, column, oldRow, oldColumn);
        string nm = w.GetName();
        if (nm == "RzChOwners")
        {
            OZL_Owners owners = DraftOwners();
            if (owners && row >= 0 && row < owners.Owners.Count() && owners.Owners[row])
            {
                m_ChOwner = owners.Owners[row].Id;
                m_ChLine = "";
                m_ChRule = "";
                m_RuDelArmed = false;
                m_Ed.EndGesture();
                RepaintChains(true);
            }
            return true;
        }
        if (nm == "RzChLines")
        {
            if (row >= 0 && row < m_ChLines.Count())
            {
                m_ChLine = m_ChLines[row].Line;
                m_ChRule = "";
                m_RuDelArmed = false;
                m_Ed.EndGesture();
                ChPickCard(m_ChCard);
            }
            return true;
        }
        if (nm == "RzChRaw")
        {
            if (row >= 0 && row < m_ChRawIds.Count())
            {
                m_ChRule = m_ChRawIds[row];
                m_ChCard = "raw";
                m_RuDelArmed = false;
                m_Ed.EndGesture();
                RepaintChains(true);
            }
            return true;
        }
        return super.OnItemSelected(w, x, y, row, column, oldRow, oldColumn);
    }

    override bool OnChange(Widget w, int x, int y, bool finished)
    {
        if (w && M_SUB_WIDGET && !m_RzFill && m_Ed && m_ChLines)
        {
            string nm = w.GetName();
            if (nm.IndexOf("RzRu") == 0)
            {
                OnRuField(nm);
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
            if (nm == "RzChBulkPts" || nm == "RzChBulkNode")
                return true;
        }
        return super.OnChange(w, x, y, finished);
    }

    override bool OnClick(Widget w, int x, int y, int button)
    {
        if (!M_SUB_WIDGET || !w || !m_ChLines)
            return super.OnClick(w, x, y, button);
        string nm = w.GetName();
        if (nm.IndexOf("BtnRzChCard_") == 0)
        {
            ChPickCard(nm.Substring(12, nm.Length() - 12));
            return true;
        }
        if (nm == "BtnRzChMode")
        {
            m_ChPlayer = !m_ChPlayer;
            RepaintChains(true);
            return true;
        }
        if (nm == "BtnRzChBulk")
        {
            ChBulk();
            return true;
        }
        if (nm == "BtnRzChRawAdd")
        {
            ChRawAdd();
            return true;
        }
        if (nm == "BtnRzRuEnabled")
        {
            RuToggle(false);
            return true;
        }
        if (nm == "BtnRzRuExact")
        {
            RuToggle(true);
            return true;
        }
        if (nm == "BtnRzRuDup")
        {
            RuDuplicate();
            return true;
        }
        if (nm == "BtnRzRuDel")
        {
            RuDelete();
            return true;
        }
        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
