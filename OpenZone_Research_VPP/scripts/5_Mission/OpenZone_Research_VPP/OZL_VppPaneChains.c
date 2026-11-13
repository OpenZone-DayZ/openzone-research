// The page ЛАНЦЮГИ of the research editor: the owner's processing rules by line
// (OZL_EdChains). A line's conveyor is six cards; under them the raw items (the packer's
// rules) by the tier of their node, with a bulk edit of a whole tier, and beside them the
// station as the player meets it; on the right the fields of the picked rule.
//
// The page is the pane ozl_vpp_chains, converted from its mockup board (css2layout) with its
// four row templates; this file fills it from the draft and writes edits back. A separate
// modded layer of the same OZ_VppAdminMenu as OZL_VppPane.c (the frame): the frame calls
// RepaintRzPage and RzLayPages, and this layer takes the page "chains". The file name must
// sort after OZL_VppPane.c -- the files of a folder compile in alphabetical order, and the
// layer that overrides comes later.
//
// Design: docs/specs/2026-11-09-research-editor-vpp-design.md, section 1 item 4; the page as
// drawn: docs/specs/2026-11-13-openzone-vpp-page-guide.md.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    // The picked owner, line and rule.
    protected string m_ChOwner;
    protected string m_ChLine;
    protected string m_ChRule;
    // The picked card of the conveyor: raw, packer, sample, analyzer, carrier, terminal.
    protected string m_ChCard;
    protected ref array<ref OZL_EdLine> m_ChLines;
    // The ids of the rules in the raw list, in the order of its rows.
    protected ref array<string> m_ChRawIds;

    // The lists: owners, lines, and the raw items -- two kinds of rows in one list (a
    // caption per tier, the tier's rules under it).
    protected ref OZ_VppFlexRows m_ChOwRows;
    protected ref OZ_VppFlexRows m_ChLnRows;
    protected ref OZ_VppFlexRows m_ChTierRows;
    protected ref OZ_VppFlexRows m_ChRawRows;

    // Where the note under the rule's form stands (read once, in pixels): the same text
    // widget says what a card without a rule is, in the form's place.
    protected float m_RuInfoX;
    protected float m_RuInfoY;
    protected float m_RuInfoW;
    protected float m_RuInfoH;

    override void OnCreate(Widget RootW)
    {
        m_ChOwner = "";
        m_ChLine = "";
        m_ChRule = "";
        m_ChCard = "raw";
        m_ChLines  = new array<ref OZL_EdLine>();
        m_ChRawIds = new array<string>();
        m_RuInfoX = 0;
        m_RuInfoY = 0;
        m_RuInfoW = 0;
        m_RuInfoH = 0;
        super.OnCreate(RootW);
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
        return OZL_Metal.TEXT;
    }

    // The rule the form shows: the picked one, and without it the card's.
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
        string unit = Tr("#STR_OZL_ED_CH_SEC");
        return n.ToString() + " " + unit;
    }

    // ------------------------------------------------- the page

    // fillForm -- write the fields of the rule and of the bulk edit; not while one is
    // typed in, the cursor would jump to the end.
    protected void RepaintChains(bool fillForm)
    {
        OZL_Rules rules = DraftRules();
        OZL_Owners owners = DraftOwners();
        Widget hostO = M_SUB_WIDGET.FindAnyWidget("RzChOwRows");
        Widget hostL = M_SUB_WIDGET.FindAnyWidget("RzChLnRows");
        if (!rules || !owners || !hostO || !hostL)
            return;
        if (!m_ChOwRows)
            m_ChOwRows = new OZ_VppFlexRows(m_Flex, hostO, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_ch_owner_row.layout", "OZL_ChOwnerRow", 225, 32);
        if (!m_ChLnRows)
            m_ChLnRows = new OZ_VppFlexRows(m_Flex, hostL, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_ch_line_row.layout", "OZL_ChLineRow", 225, 32);

        int i;
        bool known = false;
        string firstOwner = "";
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            if (!owners.Owners[i])
                continue;
            if (firstOwner == "")
                firstOwner = owners.Owners[i].Id;
            if (owners.Owners[i].Id == m_ChOwner)
                known = true;
        }
        if (!known)
        {
            m_ChOwner = firstOwner;
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

        // The owners, each with how many lines it has.
        OZL_PointTypes pts = DraftPointTypes();
        array<ref OZL_EdLine> tmp = new array<ref OZL_EdLine>();
        Widget row;
        m_ChOwRows.Clear();
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            OZL_OwnerDef o = owners.Owners[i];
            if (!o || m_ChOwRows.Count() >= RZ_LIST_MAX)
                continue;
            row = m_ChOwRows.Add(o.Id);
            if (!row)
                break;
            OZL_EdChains.Lines(rules, owners, o.Id, tmp);
            string ownerName = RzOwnerName(o.Id);
            RzRowText(row, "ChOwId", o.Id, OZL_Metal.TEXT);
            RzRowText(row, "ChOwName", ownerName, OZL_Metal.TEXT);
            RzRowText(row, "ChOwLines", tmp.Count().ToString(), OZL_Metal.MUTED);
            Widget dash = row.FindAnyWidget("ChOwDash");
            if (dash)
                dash.Show(ownerName != "");
            RzLitRow(row, "OZL_ChOwnerRow", o.Id == m_ChOwner);
        }
        m_ChOwRows.Fit();

        // The owner's lines: the line's colour and name, its packer and analyzer rules.
        m_ChLnRows.Clear();
        for (i = 0; i < m_ChLines.Count(); i++)
        {
            OZL_EdLine l = m_ChLines[i];
            row = m_ChLnRows.Add(l.Line);
            if (!row)
                break;
            RzRowText(row, "ChLnName", LineName(pts, l.Line), OZL_Metal.TEXT);
            RzRowText(row, "ChLnCount", l.Packers.Count().ToString() + " + " + l.Analyzers.Count().ToString(), OZL_Metal.MUTED);
            OZ_VppFlex.Paint(row, "ChLnDotBg", LineColor(pts, l.Line));
            RzLitRow(row, "OZL_ChLineRow", l.Line == m_ChLine);
        }
        m_ChLnRows.Fit();
        ChLaySideRows();
        if (m_ChLines.Count() == 0)
            SetLabel("RzChSideNote", "#STR_OZL_ED_CH_NO_LINES", OZL_Metal.ALERT);
        else
            SetLabel("RzChSideNote", "#STR_OZL_VPP_CH_SIDE_NOTE", OZL_Metal.MUTED);

        PaintChCards(line, rules, owners, pts);
        PaintChRaw(line, rules);
        PaintChBulk(rules, fillForm);
        PaintRuForm(rules, line, owners, pts, fillForm);
        PaintStation(line, rules, pts);
    }

    // The words of the two side lists along their rows (225 units a row): the owner's
    // lines and the line's rules are written from the right.
    protected void ChLaySideRows()
    {
        int i;
        if (m_ChOwRows)
        {
            for (i = 0; i < m_ChOwRows.Count(); i++)
                RzLaySideRow(m_ChOwRows.Row(i), "ChOwId", "ChOwDash", "ChOwName", "ChOwLines", 225);
        }
        if (!m_ChLnRows)
            return;
        float s = UnitScale();
        for (i = 0; i < m_ChLnRows.Count(); i++)
        {
            Widget row = m_ChLnRows.Row(i);
            if (!row)
                continue;
            float right = 215 * s;
            TextWidget count = TextWidget.Cast(row.FindAnyWidget("ChLnCount"));
            if (count)
            {
                int tw = RzFitText(count);
                right = right - tw;
                RzSetX(count, right);
                right = right - 8 * s;
            }
            Widget name = row.FindAnyWidget("ChLnName");
            if (name)
            {
                float w;
                float h;
                name.GetSize(w, h);
                w = right - 26 * s;
                if (w < 0)
                    w = 0;
                name.SetSize(w, h);
            }
        }
    }

    // A card of the conveyor: its value and two lines under it, its line's colour as a
    // square before the value (the cards that have one), lit when it is the picked card.
    protected void ChCard(string k, string v, string c, string sub, int ink, int dotColor)
    {
        SetLabel("RzChV_" + k, v, ink);
        SetLabel("RzChC_" + k, c, OZL_Metal.MUTED);
        SetLabel("RzChS_" + k, sub, OZL_Metal.MUTED);
        if (dotColor != 0)
            OZ_VppFlex.Paint(M_SUB_WIDGET, "RzChD_" + k + "Bg", dotColor);
        else
            OZ_VppFlex.Paint(M_SUB_WIDGET, "RzChD_" + k + "Bg", OZL_Metal.FAINT);

        int rim = OZL_Metal.EDGE;
        int ground = OZL_Metal.HEAD;
        int badge = OZL_Metal.RAISED;
        int number = OZL_Metal.MUTED;
        int kind = OZL_Metal.MUTED;
        if (k == m_ChCard)
        {
            rim = OZL_Metal.ACCENT;
            ground = OZL_Metal.PICK_PANEL;
            badge = OZL_Metal.ACCENT;
            number = OZL_Metal.INK;
            kind = OZL_Metal.ACCENT;
        }
        OZ_VppFlex.Paint(M_SUB_WIDGET, "BtnRzChCard_" + k + "Edge", rim);
        OZ_VppFlex.Paint(M_SUB_WIDGET, "BtnRzChCard_" + k + "Bg", ground);
        OZ_VppFlex.Paint(M_SUB_WIDGET, "RzChN_" + k + "Bg", badge);
        SetColorOf("RzChNT_" + k, number);
        SetColorOf("RzChK_" + k, kind);
    }

    protected void PaintChCards(OZL_EdLine line, OZL_Rules rules, OZL_Owners owners, OZL_PointTypes pts)
    {
        if (!line)
        {
            array<string> keys = {"raw", "packer", "sample", "analyzer", "carrier", "terminal"};
            for (int k = 0; k < keys.Count(); k++)
                ChCard(keys[k], "-", "", "", OZL_Metal.FAINT, 0);
            return;
        }
        OZL_TreeConfig tree = DraftTree();
        int lineInk = LineColor(pts, line.Line);
        int i;

        // RAW ITEMS: how many kinds, and how they lie over the tiers.
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
        // Every translated piece goes into a local before it meets another (two
        // translations in one expression lose one).
        string tierMark = Tr("#STR_OZL_ED_CH_T");
        string spread = "";
        for (int lo = 0; lo <= 10; lo++)
        {
            int ti = tiers.Find(lo);
            if (ti < 0)
                continue;
            if (spread != "")
                spread += "  ";
            spread += tierMark + lo.ToString() + ": " + counts[ti].ToString();
        }
        string noPacker = Tr("#STR_OZL_ED_CH_NO_PACKER");
        if (line.Packers.Count() > 0)
        {
            string kinds = Tr("#STR_OZL_ED_CH_KINDS");
            string packerRules = Tr("#STR_OZL_VPP_CH_RAW_CARD");
            ChCard("raw", kinds + line.Packers.Count().ToString(), spread, packerRules, OZL_Metal.TEXT, 0);
        }
        else
        {
            string worldOnly = Tr("#STR_OZL_ED_CH_WORLD_ONLY");
            ChCard("raw", worldOnly, "", noPacker, OZL_Metal.TEXT, 0);
        }

        // PACKER: the station of the first rule, the span of the times.
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
            {
                string upTo = Secs(tMax);
                times = times + " - " + upTo;
            }
            ChCard("packer", OZL_EdChains.ItemName(packDev), packDev, times, OZL_Metal.TEXT, 0);
        }
        else
        {
            ChCard("packer", "-", "", noPacker, OZL_Metal.FAINT, 0);
        }

        // SAMPLE: its class and the points the samples of this line carry.
        pointSet.Sort();
        string ptsText = "";
        for (i = 0; i < pointSet.Count(); i++)
        {
            if (ptsText != "")
                ptsText += " / ";
            ptsText += "+" + pointSet[i].ToString();
        }
        if (ptsText != "")
        {
            string ptsWord = Tr("#STR_OZL_ED_CH_PTS");
            ptsText = ptsText + " " + ptsWord;
        }
        ChCard("sample", OZL_EdChains.ItemName(line.Sample), line.Sample, ptsText, OZL_Metal.TEXT, lineInk);

        // ANALYZER and CARRIER -- from the analysis rule.
        OZL_Rule an = null;
        if (line.Analyzers.Count() > 0)
            an = rules.Find(line.Analyzers[0]);
        array<OZL_ModuleDef> mods = new array<OZL_ModuleDef>();
        OZL_EdChains.ModulesOf(DraftModules(), line.Line, mods);
        if (an)
        {
            string anDev = OZL_Match.StripExact(an.Device);
            string anName = OZL_EdChains.ItemName(anDev);
            string anTime = Secs(an.TimeSec);
            string modsWord = Tr("#STR_OZL_ED_CH_MODS");
            string anSub = anTime + " · " + modsWord + mods.Count().ToString();
            ChCard("analyzer", anName, anDev, anSub, OZL_Metal.TEXT, 0);
        }
        else
        {
            ChCard("analyzer", "-", "", "", OZL_Metal.FAINT, 0);
        }
        if (line.Carrier != "")
        {
            string carrierName = OZL_EdChains.ItemName(line.Carrier);
            string chanceWord = Tr("#STR_OZL_ED_CH_CHANCE");
            ChCard("carrier", carrierName, line.Carrier, chanceWord, OZL_Metal.TEXT, lineInk);
        }
        else
        {
            ChCard("carrier", "-", "", "", OZL_Metal.FAINT, 0);
        }

        // TERMINAL - POOL: the owner's terminal and the line's point type.
        OZL_OwnerDef def = OZL_EdChains.OwnerDef(owners, m_ChOwner);
        string term = "-";
        if (def && def.TerminalClasses.Count() > 0)
            term = def.TerminalClasses[0];
        string poolWord = Tr("#STR_OZL_ED_CH_POOL");
        ChCard("terminal", LineName(pts, line.Line), term, poolWord + m_ChOwner, OZL_Metal.TEXT, lineInk);
    }

    // The raw items of the line: the packer's rules by the tier of their node, a caption
    // per tier (how many kinds; the node when the tier's rules share one) and a row per
    // rule under it.
    protected void PaintChRaw(OZL_EdLine line, OZL_Rules rules)
    {
        Widget host = M_SUB_WIDGET.FindAnyWidget("RzChRawRows");
        if (!host)
            return;
        if (!m_ChTierRows)
            m_ChTierRows = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_ch_tier_row.layout", "OZL_ChTierRow", 325, 29);
        if (!m_ChRawRows)
            m_ChRawRows = new OZ_VppFlexRows(m_Flex, host, "OpenZone_Research_VPP/gui/layouts/ozl_vpp_ch_raw_row.layout", "OZL_ChRawRow", 325, 36);

        m_ChRawIds.Clear();
        m_ChTierRows.Clear();
        m_ChRawRows.Clear();
        if (!line)
        {
            SetLabel("RzChRawSub", "#STR_OZL_VPP_CH_RAW_SUB", OZL_Metal.MUTED);
            m_ChTierRows.Fit();
            m_ChRawRows.Fit();
            return;
        }
        OZL_TreeConfig tree = DraftTree();
        OZL_EdChains.SortedPackers(rules, tree, line, m_ChRawIds);
        if (m_ChRawIds.Count() == 0)
            SetLabel("RzChRawSub", "#STR_OZL_VPP_CH_NO_RAW2", OZL_Metal.ALERT);
        else
            SetLabel("RzChRawSub", "#STR_OZL_VPP_CH_RAW_SUB", OZL_Metal.MUTED);

        string tierWord = Tr("#STR_OZL_ED_CH_TIER");
        string kindsWord = Tr("#STR_OZL_ED_CH_KINDS");
        string noNode = Tr("#STR_OZL_ED_CH_NO_NODE");
        string nodeWord = Tr("#STR_OZL_ED_CH_NODE");
        string missing = Tr("#STR_OZL_ED_CH_NODE_MISSING");
        string offWord = Tr("#STR_OZL_ED_CH_OFF");
        string ptsWord = Tr("#STR_OZL_ED_CH_PTS");

        int lastTier = -1;
        Widget row;
        for (int i = 0; i < m_ChRawIds.Count(); i++)
        {
            OZL_Rule r = rules.Find(m_ChRawIds[i]);
            if (!r || m_ChRawRows.Count() >= RZ_LIST_MAX)
                continue;
            int t = OZL_EdChains.TierOf(r, tree);
            if (t != lastTier)
            {
                // A new tier: its caption, with what the tier's rules share.
                lastTier = t;
                int inTier = 0;
                string sameNode = r.RequiredNode;
                for (int k = 0; k < m_ChRawIds.Count(); k++)
                {
                    OZL_Rule rr = rules.Find(m_ChRawIds[k]);
                    if (!rr || OZL_EdChains.TierOf(rr, tree) != t)
                        continue;
                    inTier++;
                    if (rr.RequiredNode != sameNode)
                        sameNode = "?";
                }
                string tierSub = kindsWord + inTier.ToString();
                if (sameNode == "")
                    tierSub = tierSub + " · " + noNode;
                else if (sameNode != "?")
                    tierSub = tierSub + " · " + nodeWord + ChNodeName(tree, sameNode);
                row = m_ChTierRows.Add("t" + t.ToString());
                if (row)
                {
                    RzRowText(row, "ChTierName", tierWord + t.ToString(), OZL_Metal.TEXT);
                    RzRowText(row, "ChTierSub", tierSub, OZL_Metal.MUTED);
                }
            }

            row = m_ChRawRows.Add(r.Id);
            if (!row)
                break;
            string input = r.InputItem.Classname;
            if (r.InputItem.Quantity != 1)
                input = input + " x" + r.InputItem.Quantity.ToString();
            int inputInk = OZL_Metal.TEXT;
            if (!r.Enabled)
            {
                input = offWord + input;
                inputInk = OZL_Metal.BAD;
            }
            if (r.InputItem.Classname == "")
                inputInk = OZL_Metal.BAD;
            RzRowText(row, "ChRawIn", input, inputInk);
            string points = "";
            OZL_RuleOutput so = OZL_EdChains.SampleOutput(r);
            if (so)
                points = "+" + so.Points.ToString() + " " + ptsWord;
            RzRowText(row, "ChRawPts", points, OZL_Metal.TEXT);
            RzRowText(row, "ChRawTime", Secs(r.TimeSec), OZL_Metal.MUTED);
            if (r.RequiredNode == "")
                RzRowText(row, "ChRawNode", noNode, OZL_Metal.MUTED);
            else if (tree && tree.FindNode(r.RequiredNode))
                RzRowText(row, "ChRawNode", ChNodeName(tree, r.RequiredNode), OZL_Metal.MUTED);
            else
                RzRowText(row, "ChRawNode", r.RequiredNode + missing, OZL_Metal.BAD);
        }
        m_ChTierRows.Fit();
        m_ChRawRows.Fit();
        ChLayRawRows();
    }

    // A node's name for a row: its name in the draft's tree, else its id.
    protected string ChNodeName(OZL_TreeConfig tree, string nodeId)
    {
        OZL_TreeNode n = null;
        if (tree)
            n = tree.FindNode(nodeId);
        if (n && n.Name != "")
            return n.Name;
        return nodeId;
    }

    // The rows of the raw list: the picked rule's row is lit; the points and the time are
    // written from the right (their cells end 127 and 79 units before the row's end); a
    // tier's caption is as wide as its words, what it says stands after them.
    protected void ChLayRawRows()
    {
        float s = UnitScale();
        int i;
        Widget row;
        int tw;
        if (m_ChTierRows)
        {
            for (i = 0; i < m_ChTierRows.Count(); i++)
            {
                row = m_ChTierRows.Row(i);
                if (!row)
                    continue;
                TextWidget tier = TextWidget.Cast(row.FindAnyWidget("ChTierName"));
                Widget sub = row.FindAnyWidget("ChTierSub");
                if (!tier || !sub)
                    continue;
                tw = RzFitText(tier);
                float sw;
                float sh;
                sub.GetSize(sw, sh);
                float sx = 2 * s + tw + 8 * s;
                RzSetX(sub, sx);
                sw = m_ChTierRows.Width() - sx - 2 * s;
                if (sw < 0)
                    sw = 0;
                sub.SetSize(sw, sh);
            }
        }
        if (!m_ChRawRows)
            return;
        float w = m_ChRawRows.Width();
        for (i = 0; i < m_ChRawRows.Count(); i++)
        {
            row = m_ChRawRows.Row(i);
            if (!row)
                continue;
            int rim = OZL_Metal.HEAD;
            int ground = OZL_Metal.HEAD;
            if (m_ChRawRows.Key(i) == m_ChRule)
            {
                rim = OZL_Metal.ACCENT;
                ground = OZL_Metal.PICK_PANEL;
            }
            OZ_VppFlex.Paint(row, "OZL_ChRawRowEdge", rim);
            OZ_VppFlex.Paint(row, "OZL_ChRawRowBg", ground);
            TextWidget points = TextWidget.Cast(row.FindAnyWidget("ChRawPts"));
            if (points)
            {
                tw = RzFitText(points);
                RzSetX(points, w - 127 * s - tw);
            }
            TextWidget secs = TextWidget.Cast(row.FindAnyWidget("ChRawTime"));
            if (secs)
            {
                tw = RzFitText(secs);
                RzSetX(secs, w - 79 * s - tw);
            }
        }
    }

    // The bulk edit under the raw list: the tier of the picked raw row, and the points
    // and the node its tier's rules share (a field is empty when they differ).
    protected void PaintChBulk(OZL_Rules rules, bool fillForm)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_Rule r = null;
        if (m_ChRawIds.Find(m_ChRule) > -1)
            r = rules.Find(m_ChRule);
        if (!r)
        {
            SetLabel("RzChBulkTier", "#STR_OZL_VPP_CH_BULK_NONE", OZL_Metal.MUTED);
            ChLayBulk();
            if (fillForm)
            {
                m_RzFill = true;
                SetEdit("RzChBulkPts", "");
                SetEdit("RzChBulkNode", "");
                m_RzFill = false;
            }
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
        string toTier = Tr("#STR_OZL_VPP_CH_BULK_TO");
        string rulesWord = Tr("#STR_OZL_VPP_CH_BULK_N");
        SetLabel("RzChBulkTier", toTier + t.ToString() + " · " + rulesWord + n.ToString(), OZL_Metal.MUTED);
        ChLayBulk();
        if (!fillForm)
            return;
        m_RzFill = true;
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

    // The bulk box's caption stands on the box's frame: it is as wide as its words, and
    // the frame is broken under it (six units of air on each side).
    protected void ChLayBulk()
    {
        RzFitLegend("RzChBulkTier", "RzChBulkGap");
    }

    // The rule's form: the fields of the rule, and for the terminal card or without a
    // rule the note under the form says what there is, in the form's place.
    protected void PaintRuForm(OZL_Rules rules, OZL_EdLine line, OZL_Owners owners, OZL_PointTypes pts, bool fillForm)
    {
        OZL_Rule r = CardRule(rules, line);
        ShowW("BtnRzRuEnabled", r != null);
        ShowW("RzRuForm", r != null);
        string word;
        if (!r)
        {
            SetLabel("RzRuHead", "-", OZL_Metal.FAINT);
            SetLabel("RzRuSub", "", 0);
            RuPlaceInfo(true);
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
                string termWord = Tr("#STR_OZL_ED_CH_INFO_TERM");
                string purityWord = Tr("#STR_OZL_ED_CH_INFO_PURITY");
                string whereWord = Tr("#STR_OZL_ED_CH_INFO_WHERE");
                string info = termWord + terms + "\n" + purityWord + OZL_EdChains.Pct(base);
                info = info + "\n\n" + whereWord;
                SetLabel("RzRuInfo", info, OZL_Metal.MUTED);
            }
            else
            {
                SetLabel("RzRuInfo", "#STR_OZL_ED_CH_INFO_PICK", OZL_Metal.MUTED);
            }
            return;
        }
        RuPlaceInfo(false);
        SetLabel("RzRuInfo", "#STR_OZL_VPP_RU_NOTE1", OZL_Metal.MUTED);

        // The head: the rule's id; its group and the line it feeds under it; the switch
        // that turns it on or off beside the tag.
        SetLabel("RzRuHead", r.Id, OZL_Metal.TEXT);
        string sub = "";
        OZL_RuleGroup grp = OZL_EdChains.GroupOf(rules, r.Id);
        if (grp)
        {
            word = Tr("#STR_OZL_VPP_RU_GROUP");
            sub = word + grp.Id;
        }
        if (line)
        {
            word = Tr("#STR_OZL_VPP_RU_LINE");
            string lineName = LineName(pts, line.Line);
            if (sub != "")
                sub += " · ";
            sub += word + lineName;
        }
        SetLabel("RzRuSub", sub, 0);
        if (r.Enabled)
            SetLabel("RzRuEnabledText", "#STR_OZL_ED_RU_ON", OZL_Metal.OK);
        else
            SetLabel("RzRuEnabledText", "#STR_OZL_ED_RU_OFF", OZL_Metal.BAD);
        RzPaintTick("BtnRzRuEnabledBox", r.Enabled, OZL_Metal.OK);
        RuLayEnabled();
        bool exact = IsExact(r);
        RzSeg("BtnRzRuKin", !exact);
        RzSeg("BtnRzRuExact", exact);
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

    // The rule's switch is as wide as its word and ends where it was drawn to end.
    protected void RuLayEnabled()
    {
        Widget b = M_SUB_WIDGET.FindAnyWidget("BtnRzRuEnabled");
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzRuEnabledText"));
        if (!b || !t)
            return;
        float s = UnitScale();
        float x;
        float y;
        float w;
        float h;
        b.GetPos(x, y);
        b.GetSize(w, h);
        float right = x + w;
        int tw = RzFitText(t);
        w = 24 * s + tw + 2;
        b.SetSize(w, h);
        b.SetPos(right - w, y);
        Widget ground = M_SUB_WIDGET.FindAnyWidget("BtnRzRuEnabledBg");
        if (ground)
            ground.SetSize(w, h);
    }

    // The note under the form: in the form's place and as tall as a few lines while no
    // rule is shown, back under the form otherwise.
    protected void RuPlaceInfo(bool up)
    {
        Widget info = M_SUB_WIDGET.FindAnyWidget("RzRuInfo");
        Widget form = M_SUB_WIDGET.FindAnyWidget("RzRuForm");
        if (!info || !form)
            return;
        if (m_RuInfoW <= 0)
        {
            info.GetPos(m_RuInfoX, m_RuInfoY);
            info.GetSize(m_RuInfoW, m_RuInfoH);
        }
        if (m_RuInfoW <= 0)
            return;
        if (!up)
        {
            info.SetPos(m_RuInfoX, m_RuInfoY);
            info.SetSize(m_RuInfoW, m_RuInfoH);
            return;
        }
        float fx;
        float fy;
        form.GetPos(fx, fy);
        info.SetPos(m_RuInfoX, fy);
        info.SetSize(m_RuInfoW, 240 * UnitScale());
    }

    // The station as the player meets it: the names and descriptions of the items come
    // from config.cpp and the mod's stringtable in the client's language, the action is
    // the one of the player's action menu. The time, the node and the purity are a line
    // for the admin: the player does not see them. The terminal card has no station.
    protected void PaintStation(OZL_EdLine line, OZL_Rules rules, OZL_PointTypes pts)
    {
        OZL_Rule r = null;
        if (line)
            r = CardRule(rules, line);
        ShowW("RzChStBody", r != null);
        if (!r)
        {
            SetLabel("RzChStSub", "#STR_OZL_ED_CH_ST_NONE", OZL_Metal.MUTED);
            return;
        }
        SetLabel("RzChStSub", "#STR_OZL_VPP_CH_ST_SUB", OZL_Metal.MUTED);

        bool analysis = (line.Analyzers.Find(r.Id) > -1);
        string dev = OZL_Match.StripExact(r.Device);
        int lineInk = LineColor(pts, line.Line);
        if (analysis)
            SetLabel("RzStKind", "#STR_OZL_ED_CH_K_ANALYZER", OZL_Metal.MUTED);
        else
            SetLabel("RzStKind", "#STR_OZL_ED_CH_K_PACKER", OZL_Metal.MUTED);
        SetLabel("RzStName", OZL_EdChains.ItemName(dev), OZL_Metal.TEXT);
        ChLayStation();

        string inName = OZL_EdChains.ItemName(r.InputItem.Classname);
        if (r.InputItem.Quantity > 1)
            inName += " x" + r.InputItem.Quantity.ToString();
        SetLabel("RzStSlotK0", "#STR_OZL_ED_ST_SLOT_IN", 0);
        SetLabel("RzStSlotV0", inName, 0);
        string outCls = "";
        if (r.Outputs.Count() > 0 && r.Outputs[0])
            outCls = r.Outputs[0].Classname;
        SetLabel("RzStSlotK1", "#STR_OZL_ED_ST_SLOT_OUT", 0);
        SetLabel("RzStSlotV1", OZL_EdChains.ItemName(outCls), 0);
        OZ_VppFlex.Paint(M_SUB_WIDGET, "RzStSlotD1Bg", lineInk);
        array<OZL_ModuleDef> mods = new array<OZL_ModuleDef>();
        OZL_EdChains.ModulesOf(DraftModules(), line.Line, mods);
        for (int m = 0; m < 2; m++)
        {
            string mv = "-";
            if (m < mods.Count())
                mv = OZL_EdChains.ItemName(mods[m].Classname);
            SetLabel("RzStSlotK" + (m + 2).ToString(), "#STR_OZL_ED_ST_SLOT_MOD", 0);
            SetLabel("RzStSlotV" + (m + 2).ToString(), mv, 0);
        }

        SetLabel("RzStKey", "F", 0);
        SetLabel("RzStAction", "#STR_OZL_action_start", 0);
        // Each translated piece into a local first (Secs translates its unit).
        string secs = Secs(r.TimeSec);
        string adminWord = Tr("#STR_OZL_ED_ST_ADMIN");
        string admin = adminWord + secs;
        if (r.RequiredNode != "")
        {
            string nodeWord = Tr("#STR_OZL_ED_CH_NODE");
            admin = admin + " · " + nodeWord + r.RequiredNode;
        }
        if (!analysis)
        {
            string purityWord = Tr("#STR_OZL_ED_RU_PURITY");
            admin = admin + " · " + purityWord + " " + OZL_EdChains.Pct(OZL_Rules.StartPurity(r, dev, pts));
        }
        SetLabel("RzStAdmin", admin, 0);

        SetLabel("RzStTipName", OZL_EdChains.ItemName(outCls), OZL_Metal.TEXT);
        OZ_VppFlex.Paint(M_SUB_WIDGET, "RzStTipDotBg", lineInk);
        string desc = OZL_EdChains.ItemDesc(outCls);
        if (desc == "")
            desc = "-";
        SetLabel("RzStTipDesc", desc, 0);
    }

    // The station's name stands after its kind: the kind's caption is as wide as its
    // word, and the box that holds the name begins 8 units after it and keeps its end.
    protected void ChLayStation()
    {
        TextWidget kind = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzStKind"));
        Widget name = M_SUB_WIDGET.FindAnyWidget("RzStName");
        Widget box = M_SUB_WIDGET.FindAnyWidget("RzStNameBox");
        if (!kind || !name || !box)
            return;
        float s = UnitScale();
        int tw = RzFitText(kind);
        float kx;
        float ky;
        kind.GetPos(kx, ky);
        float bx;
        float by;
        float bw;
        float bh;
        box.GetPos(bx, by);
        box.GetSize(bw, bh);
        float right = bx + bw;
        float nx = kx + tw + 8 * s;
        bw = right - nx;
        if (bw < 0)
            bw = 0;
        box.SetPos(nx, by);
        box.SetSize(bw, bh);
        float nw;
        float nh;
        name.GetSize(nw, nh);
        name.SetSize(bw, nh);
    }

    // ------------------------------------------------- actions

    protected void ChPickCard(string k)
    {
        OZL_Rules rules = DraftRules();
        OZL_EdLine line = ChLine();
        m_ChCard = k;
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

    // The bulk edit of a tier: the points per sample and the node go to every raw rule of
    // the picked row's tier. An empty field touches nothing; "-" in the node field takes
    // the node away.
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
            if (!g)
                continue;
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
        RepaintChains(true);
        PaintRzBar();
        PaintSummary();
        string word = Tr("#STR_OZL_ED_CH_BULK_DONE");
        Hint(word + group.Count().ToString());
    }

    // + RAW ITEM: a copy of the picked (or the first) raw rule of the line with an empty
    // input -- the admin types the class; a line with no packer gets a new rule with the
    // line's sample as its output.
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
        RepaintChains(true);
        PaintRzBar();
        PaintSummary();
        string word = Tr("#STR_OZL_ED_CH_RAW_ADDED");
        Hint(word + r.Id);
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

        m_Ed.Commit(tag);
        RepaintChains(false);
        PaintRzBar();
        PaintSummary();
    }

    // The rule's switches: one undo step per press. exact -- which classes the input
    // takes; otherwise the rule is turned on or off.
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
        RepaintChains(true);
        PaintRzBar();
        PaintSummary();
        string word = Tr("#STR_OZL_ED_RU_DUPED");
        Hint(word + c.Id);
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
        string ask = Tr("#STR_OZL_VPP_ASK_DEL_RULE");
        string tail = Tr("#STR_OZL_VPP_ASK_DRAFT");
        Confirm(ask + r.Id + "? " + tail, "#STR_OZL_VPP_YES_DELETE", "rz:rudel:" + r.Id);
    }

    // The strip's yes: the rule is found again by its id.
    protected void RuDeleteNow(string ruleId)
    {
        OZL_Rules rules = DraftRules();
        OZL_Rule r = null;
        if (rules)
            r = rules.Find(ruleId);
        string word;
        if (!r)
        {
            word = Tr("#STR_OZL_VPP_GONE");
            Hint(word + ruleId);
            return;
        }
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
        if (m_ChRule == id)
            m_ChRule = "";
        RepaintChains(true);
        PaintRzBar();
        PaintSummary();
        word = Tr("#STR_OZL_ED_RU_DELETED");
        Hint(word + id);
    }

    override void OnConfirmed(string action)
    {
        if (action.IndexOf("rz:rudel:") == 0)
        {
            RuDeleteNow(action.Substring(9, action.Length() - 9));
            return;
        }
        super.OnConfirmed(action);
    }

    // ------------------------------------------------- size and events

    // The rule the form shows: the picked one, or the card's.
    protected OZL_Rule CurrentRule()
    {
        OZL_Rules rules = DraftRules();
        if (!rules)
            return null;
        OZL_Rule r = rules.Find(m_ChRule);
        if (!r)
            r = CardRule(rules, ChLine());
        return r;
    }

    // The page changed its size, or its texts have their widths now: the lists are fitted
    // and what follows a text is placed again. The page itself follows the window by the
    // rule its layout carries.
    override void RzLayPages(float pw, float ph)
    {
        super.RzLayPages(pw, ph);
        if (!M_SUB_WIDGET || m_RzTab != "chains")
            return;
        if (m_ChOwRows)
            m_ChOwRows.Fit();
        if (m_ChLnRows)
            m_ChLnRows.Fit();
        ChLaySideRows();
        if (m_ChTierRows)
            m_ChTierRows.Fit();
        if (m_ChRawRows)
            m_ChRawRows.Fit();
        ChLayRawRows();
        ChLayBulk();
        ChLayStation();
        RuLayEnabled();
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
        if (!M_SUB_WIDGET || !w || !m_ChLines || !m_Ed)
            return super.OnClick(w, x, y, button);
        string nm = w.GetName();
        if (nm.IndexOf("BtnRzChCard_") == 0)
        {
            ChPickCard(nm.Substring(12, nm.Length() - 12));
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
        // The rule's switch: its box or its word.
        if (nm == "BtnRzRuEnabled" || nm == "BtnRzRuEnabledBox")
        {
            RuToggle(false);
            return true;
        }
        // Which classes the input takes, as a pair: a press on the one in force
        // changes nothing.
        if (nm == "BtnRzRuKin" || nm == "BtnRzRuExact")
        {
            OZL_Rule cur = CurrentRule();
            bool wantExact = (nm == "BtnRzRuExact");
            if (cur && IsExact(cur) != wantExact)
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

        // The rows of the three lists (a row, or anything inside one).
        if (m_RzTab != "chains")
            return super.OnClick(w, x, y, button);
        int at;
        if (m_ChOwRows)
        {
            at = m_ChOwRows.IndexOf(w);
            if (at != -1)
            {
                m_ChOwner = m_ChOwRows.Key(at);
                m_ChLine = "";
                m_ChRule = "";
                m_Ed.EndGesture();
                RepaintChains(true);
                return true;
            }
        }
        if (m_ChLnRows)
        {
            at = m_ChLnRows.IndexOf(w);
            if (at != -1)
            {
                m_ChLine = m_ChLnRows.Key(at);
                m_ChRule = "";
                m_Ed.EndGesture();
                ChPickCard(m_ChCard);
                return true;
            }
        }
        if (m_ChRawRows)
        {
            at = m_ChRawRows.IndexOf(w);
            if (at != -1)
            {
                m_ChRule = m_ChRawRows.Key(at);
                m_ChCard = "raw";
                m_Ed.EndGesture();
                RepaintChains(true);
                return true;
            }
        }
        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
