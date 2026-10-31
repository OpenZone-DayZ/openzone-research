// The `oz_research` verb, following the bridge's contract for project verbs.
// A stand tool: it reaches what no world_* verb can -- the cargo of a station
// that cannot be held, the faction pool, the owner the core reports.
//
//   world_exec verb=oz_research args={"op":"owner"}
//   world_exec verb=oz_research args={"op":"put","item":"Rag","target":"OZL_Bnd_Pack_Khabar"}
//   world_exec verb=oz_research args={"op":"put","item":"OZL_Sample_Khabar","points":"9","purity":"70","target":"OZL_Bnd_Proc_Khabar"}
//   world_exec verb=oz_research args={"op":"cargo","target":"OZL_Bnd_Proc_Khabar"}
//   world_exec verb=oz_research args={"op":"roll","target":"OZL_Dty_Pack_Ball","n":"1000"}
//   world_exec verb=oz_research args={"op":"payload_selftest"}
//   world_exec verb=oz_research args={"op":"purity_selftest"}          (the starting purity of a cycle and the two version-2 migrations, in memory)
//   world_exec verb=oz_research args={"op":"fill","item":"Rag","target":"OZL_Bnd_Pack_Khabar"}
//   world_exec verb=oz_research args={"op":"take","item":"Rag","target":"OZL_Bnd_Pack_Khabar"}
//   world_exec verb=oz_research args={"op":"station","target":"OZL_Bnd_Pack_Khabar"}
//   world_exec verb=oz_research args={"op":"give","item":"OZL_Carrier_Khabar","points":"9"}
//   world_exec verb=oz_research args={"op":"points","owner":"bandit"}
//   world_exec verb=oz_research args={"op":"grant","owner":"bandit","type":"khabar","amount":"5"}
//   world_exec verb=oz_research args={"op":"reset","owner":"bandit"}
//   world_exec verb=oz_research args={"op":"demo","owner":"duty"}      (stand only: that faction into the tree-screen mockup's demo state, see OZL_Demo)
//   world_exec verb=oz_research args={"op":"reload"}
//   world_exec verb=oz_research args={"op":"bridge"}
//   world_exec verb=oz_research args={"op":"admin","cmd":"grant:neutral:khabar:5"}
//   world_exec verb=oz_research args={"op":"tree","as":"post"}          (as=post: stand only, see OZL_Pretend)
//   world_exec verb=oz_research args={"op":"tree","owner":"duty"}       (the JSON the tree screen gets, as that faction: stand only, see OZL_PretendOrg;
//                                                                        Have needs the player within 3 m of that faction's terminal)
//   world_exec verb=oz_research args={"op":"tree","owner":"duty","file":"duty"}   (the same, written whole to <profile>\oz_research_duty.json: an answer of the
//                                                                        bridge is cut at 400 characters, a tree is not that short)
//   world_exec verb=oz_research args={"op":"treeui"}                     (opens the tree SCREEN on the connected client)
//   world_exec verb=oz_research args={"op":"treeui","owner":"duty"}      (…as that faction: stand only, see OZL_PretendOrg)
//   world_exec verb=oz_research args={"op":"research","node":"ts_bnd_1","as":"post"}
//
// `target` names a station class; the nearest one to the player within
// `radius` (default 30 m) is taken. Items are CREATED in the station's cargo,
// never moved there: a script move into a container is the ghost-item trap.
modded class DZMCP_BridgeCore
{
    override protected string KnownVerbs()
    {
        return super.KnownVerbs() + ", oz_research";
    }

    override protected bool IsKnownVerb(string verb)
    {
        if (verb == "oz_research")
            return true;
        return super.IsKnownVerb(verb);
    }

    override protected void Dispatch(string verb, string raw)
    {
        if (verb != "oz_research")
        {
            super.Dispatch(verb, raw);
            return;
        }

        DZMCP_CommandFull full = new DZMCP_CommandFull();
        string parseError;
        if (!m_Json.ReadFromString(full, raw, parseError))
        {
            FinishCommand(DZMCP_STATUS_FAILED, "oz_research: the args block could not be parsed -- every value must be a string: " + Excerpt(parseError));
            return;
        }

        map<string, string> args = full.args;
        string op = OZL_Arg(args, "op", "owner");
        string detail;
        bool ok = OZL_Run(op, args, detail);
        if (ok)
            FinishCommand(DZMCP_STATUS_DONE, detail);
        else
            FinishCommand(DZMCP_STATUS_FAILED, detail);
    }

    protected string OZL_Arg(map<string, string> args, string key, string fallback)
    {
        if (!args)
            return fallback;
        string v;
        if (args.Find(key, v))
            return v;
        return fallback;
    }

    protected bool OZL_Run(string op, map<string, string> args, out string detail)
    {
        if (op == "owner")
        {
            PlayerBase p = OZL_FirstPlayer();
            if (!p)
            {
                detail = "nobody is connected";
                return false;
            }
            string uid = "";
            if (p.GetIdentity())
                uid = p.GetIdentity().GetPlainId();
            string owner = OZL_Owner.OfPlayer(p);
            detail = "uid=" + uid + " owner=" + owner;
            detail += " base=" + OZ_Identity.Get().BaseOf(uid);
            detail += " org=" + OZ_Identity.Get().OrgOf(uid);
            if (OZL_Access.MaySpend(uid))
                detail += " maySpend=1";
            else
                detail += " maySpend=0";
            if (OZ_Identity.Present())
                detail += " identity=present";
            else
                detail += " identity=absent";
            return true;
        }

        if (op == "put")
        {
            string item = OZL_Arg(args, "item", "");
            if (item == "" || !OZL_Match.ClassExists(item))
            {
                detail = "put needs item=<an existing class>";
                return false;
            }
            OZL_Station st = OZL_FindStation(args, detail);
            if (!st)
                return false;
            EntityAI created = st.GetInventory().CreateInInventory(item);
            if (!created)
            {
                detail = "no room for " + item + " in the cargo of " + st.GetType();
                return false;
            }
            int putPoints = OZL_Arg(args, "points", "0").ToInt();
            int putPct = OZL_Arg(args, "purity", "70").ToInt();
            string putPay = "";
            if (OZL_Lines.IsSample(item))
                putPay = OZL_Payload.EncodeSample(putPoints, putPct);
            else if (OZL_Lines.IsCarrier(item))
                putPay = OZL_Payload.EncodeCarrier(putPoints);
            OZL_Sample_Base putS = OZL_Sample_Base.Cast(created);
            if (putS)
                putS.OZL_SetPayload(putPay);
            OZL_Carrier_Base putC = OZL_Carrier_Base.Cast(created);
            if (putC)
                putC.OZL_SetPayload(putPay);
            detail = "created " + item + " in " + st.GetType() + " cargo";
            if (putPay != "")
                detail += " payload=" + putPay;
            return true;
        }

        if (op == "station")
        {
            OZL_Station st2 = OZL_FindStation(args, detail);
            if (!st2)
                return false;
            detail = OZL_Describe(st2);
            return true;
        }

        if (op == "points")
        {
            string owner2 = OZL_Arg(args, "owner", "");
            OZL_FactionState fs = OZL_State.Get(owner2);
            if (!fs)
            {
                detail = "no state for owner '" + owner2 + "'";
                return false;
            }
            detail = "owner=" + owner2 + " points=" + OZL_Points.Describe(owner2);
            detail += " completed=" + fs.CompletedNodes.Count().ToString();
            detail += " projects=" + fs.ActiveProjects.Count().ToString();
            return true;
        }

        if (op == "grant")
        {
            string owner3 = OZL_Arg(args, "owner", "");
            string type = OZL_Arg(args, "type", "");
            int amount = OZL_Arg(args, "amount", "0").ToInt();
            string why;
            if (!OZL_Points.Grant(owner3, type, amount, why))
            {
                detail = "grant refused: " + why;
                return false;
            }
            detail = "owner=" + owner3 + " points=" + OZL_Points.Describe(owner3);
            return true;
        }

        if (op == "reset")
        {
            string owner4 = OZL_Arg(args, "owner", "");
            string why2;
            if (!OZL_State.Reset(owner4, why2))
            {
                detail = "reset refused: " + why2;
                return false;
            }
            detail = "owner '" + owner4 + "' reset";
            return true;
        }

        if (op == "demo")
        {
            string demoOwner = OZL_Arg(args, "owner", "");
            if (demoOwner == "")
            {
                detail = "demo needs owner=<faction id>";
                return false;
            }
            return OZL_Demo(demoOwner, detail);
        }

        if (op == "fill")
        {
            // Create `item` in the station's cargo until nothing more fits:
            // the way to make an output get stuck (state DONE) on a stand.
            string fillCls = OZL_Arg(args, "item", "Rag");
            if (!OZL_Match.ClassExists(fillCls))
            {
                detail = "fill needs item=<an existing class>";
                return false;
            }
            OZL_Station st4 = OZL_FindStation(args, detail);
            if (!st4)
                return false;
            int made = 0;
            while (made < 200)
            {
                if (!st4.GetInventory().CreateInInventory(fillCls))
                    break;
                made++;
            }
            detail = "created " + made.ToString() + " x " + fillCls + " in " + st4.GetType() + " cargo, now full";
            return true;
        }
        if (op == "take")
        {
            // Delete one item of `item` from the station's cargo: the way to
            // free a slot on a stand with no inventory screen to drag from.
            string cls = OZL_Arg(args, "item", "");
            OZL_Station st3 = OZL_FindStation(args, detail);
            if (!st3)
                return false;
            array<EntityAI> cargo = new array<EntityAI>();
            st3.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, cargo);
            for (int c = 0; c < cargo.Count(); c++)
            {
                EntityAI e = cargo[c];
                if (!e || e == st3)
                    continue;
                if (cls != "" && e.GetType() != cls)
                    continue;
                string gone = e.GetType();
                GetGame().ObjectDelete(e);
                detail = "deleted " + gone + " from " + st3.GetType() + " cargo";
                return true;
            }
            detail = "no '" + cls + "' in the cargo of " + st3.GetType();
            return false;
        }
        if (op == "give")
        {
            // Create an item in the player's hands, with the payload of a sample
            // or a carrier: what a deposit or an identify test needs held.
            PlayerBase pg = OZL_FirstPlayer();
            if (!pg || !pg.GetHumanInventory())
            {
                detail = "nobody is connected";
                return false;
            }
            string giveCls = OZL_Arg(args, "item", "");
            if (giveCls == "" || !OZL_Match.ClassExists(giveCls))
            {
                detail = "give needs item=<an existing class>";
                return false;
            }
            EntityAI held = pg.GetHumanInventory().CreateInHands(giveCls);
            if (!held)
            {
                detail = "the hands are not free for " + giveCls;
                return false;
            }
            int givePoints = OZL_Arg(args, "points", "0").ToInt();
            int givePct = OZL_Arg(args, "purity", "70").ToInt();
            string givePay = "";
            if (OZL_Lines.IsSample(giveCls))
                givePay = OZL_Payload.EncodeSample(givePoints, givePct);
            else if (OZL_Lines.IsCarrier(giveCls))
                givePay = OZL_Payload.EncodeCarrier(givePoints);
            OZL_Sample_Base giveS = OZL_Sample_Base.Cast(held);
            if (giveS)
                giveS.OZL_SetPayload(givePay);
            OZL_Carrier_Base giveC = OZL_Carrier_Base.Cast(held);
            if (giveC)
                giveC.OZL_SetPayload(givePay);
            detail = "created " + giveCls + " in hands";
            if (givePay != "")
                detail += " payload=" + givePay;
            return true;
        }

        if (op == "tree")
        {
            PlayerBase pt = OZL_FirstPlayer();
            if (!pt)
            {
                detail = "nobody is connected";
                return false;
            }
            string tuid = "";
            if (pt.GetIdentity())
                tuid = pt.GetIdentity().GetPlainId();
            string treeOwner = OZL_Arg(args, "owner", "");
            if (treeOwner != "")
                OZL_PretendOrg(pt, treeOwner);
            if (OZL_Arg(args, "as", "") == "post")
                OZL_Pretend(pt);
            string dumpName = OZL_Arg(args, "file", "");
            if (dumpName != "")
            {
                if (!OZL_Ids.IsPathSafe(dumpName))
                {
                    detail = "tree: file must be letters, digits, _ and - only";
                    return false;
                }
                OZL_TreeView dumpView = OZL_Tree.View(OZL_Owner.OfPlayer(pt), tuid, pt);
                string dumpPath = "$profile:oz_research_" + dumpName + ".json";
                string dumpErr;
                if (!JsonFileLoader<OZL_TreeView>.SaveFile(dumpPath, dumpView, dumpErr))
                {
                    detail = "tree: " + dumpErr;
                    return false;
                }
                detail = "tree of '" + dumpView.Owner + "' (skin " + dumpView.Skin + ") written to " + dumpPath;
                // What the player's view carries per branch: shown nodes and
                // next-step stubs, Index dense over both (no branch total).
                for (int db = 0; db < dumpView.Branches.Count(); db++)
                {
                    OZL_BranchView dumpBr = dumpView.Branches[db];
                    if (dumpBr)
                        detail += "; " + dumpBr.Id + ": " + dumpBr.Nodes.Count().ToString() + " shown + " + dumpBr.Hidden.Count().ToString() + " next-step stubs";
                }
                return true;
            }
            detail = OZL_Tree.ViewJson(OZL_Owner.OfPlayer(pt), tuid, pt);
            return true;
        }

        // The tree screen without a terminal: the same show the terminal's
        // action sends, straight to the connected player. The screen is the
        // one thing on this mod that a bridge verb cannot inspect -- it lives
        // on the client -- so opening it from here is how it gets looked at
        // at all (`ui_tree`, `ui_click`, `client_shot` take over from there).
        if (op == "treeui")
        {
            PlayerBase pu = OZL_FirstPlayer();
            if (!pu)
            {
                detail = "nobody is connected";
                return false;
            }
            if (!pu.GetIdentity())
            {
                detail = "the player has no identity yet";
                return false;
            }
            string wantOwner = OZL_Arg(args, "owner", "");
            if (wantOwner != "")
                OZL_PretendOrg(pu, wantOwner);
            if (OZL_Arg(args, "as", "") == "post")
                OZL_Pretend(pu);
            OZ_Rpc.Show(pu.GetIdentity(), OZL_Const.SHOW_TREE);
            detail = "show " + OZL_Const.SHOW_TREE + " sent to " + pu.GetIdentity().GetPlainId() + ", owner " + OZL_Owner.OfPlayer(pu);
            return true;
        }

        if (op == "research")
        {
            PlayerBase pr = OZL_FirstPlayer();
            if (!pr)
            {
                detail = "nobody is connected";
                return false;
            }
            if (OZL_Arg(args, "as", "") == "post")
                OZL_Pretend(pr);
            string rwhy;
            if (!OZL_Tree.Start(pr, OZL_Owner.OfPlayer(pr), OZL_Arg(args, "node", ""), rwhy))
            {
                detail = "research refused: " + rwhy;
                return false;
            }
            detail = "research started: " + rwhy;
            return true;
        }
        if (op == "admin")
        {
            // Drive the admin section the way the VPP pane does, minus the
            // permission gate (the dispatcher's job, not the section's).
            string cmd = OZL_Arg(args, "cmd", "list");
            OZ_AdminSection sec = OZ_AdminRegistry.Get(OZL_Const.SECTION);
            if (!sec)
            {
                detail = "no admin section '" + OZL_Const.SECTION + "' registered";
                return false;
            }
            bool aok;
            string aerr;
            PlayerIdentity ident;
            PlayerBase pa = OZL_FirstPlayer();
            if (pa)
                ident = pa.GetIdentity();
            string body = sec.Handle(cmd, "{}", ident, aok, aerr);
            if (!aok)
            {
                detail = "admin " + cmd + " refused: " + aerr;
                return false;
            }
            detail = "admin " + cmd + ": " + body;
            return true;
        }
        if (op == "bridge")
        {
            detail = OZL_Bridge.Describe();
            return true;
        }
        if (op == "reload")
        {
            OZL_Config.Reload();
            detail = "reloaded: " + OZL_Config.Get().Counters();
            return true;
        }

        if (op == "cargo")
        {
            OZL_Station stc = OZL_FindStation(args, detail);
            if (!stc)
                return false;
            array<EntityAI> cinv = new array<EntityAI>();
            stc.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, cinv);
            detail = stc.GetType() + " cargo:";
            int cpts;
            int cpct;
            for (int ci = 0; ci < cinv.Count(); ci++)
            {
                EntityAI ce = cinv[ci];
                if (!ce || ce == stc)
                    continue;
                detail += " " + ce.GetType();
                OZL_Sample_Base cs = OZL_Sample_Base.Cast(ce);
                if (cs && cs.OZL_Read(cpts, cpct))
                    detail += "[points=" + cpts.ToString() + " purity=" + cpct.ToString() + "]";
                OZL_Carrier_Base cc = OZL_Carrier_Base.Cast(ce);
                if (cc && cc.OZL_Read(cpts))
                    detail += "[points=" + cpts.ToString() + "]";
            }
            return true;
        }

        if (op == "roll")
        {
            OZL_Station str = OZL_FindStation(args, detail);
            if (!str)
                return false;
            int rn = OZL_Arg(args, "n", "1000").ToInt();
            float rp;
            float rd;
            OZL_Gear.ModuleBonuses(str, rp, rd);
            OZL_Rule rr = new OZL_Rule();
            OZL_RuleOutput ro = new OZL_RuleOutput();
            ro.Classname = "Rag";
            rr.Outputs.Insert(ro);
            int rdoubled = 0;
            for (int ri = 0; ri < rn; ri++)
            {
                array<string> ritems = new array<string>();
                array<string> rpays = new array<string>();
                OZL_RuleEngine.ResolveResult(rr, 1.0, rd, 0, 70, ritems, rpays);
                if (ritems.Count() == 2)
                    rdoubled++;
            }
            detail = str.GetType() + ": purity bonus " + rp.ToString() + ", double chance " + rd.ToString();
            detail += ", doubled " + rdoubled.ToString() + "/" + rn.ToString();
            return true;
        }

        if (op == "purity_selftest")
            return OZL_PuritySelftest(detail);

        if (op == "payload_selftest")
        {
            array<string> pfails = new array<string>();
            int ppts;
            int ppct;
            if (OZL_Payload.EncodeSample(9, 70) != "01000946")
                pfails.Insert("encode sample 9/70");
            if (!OZL_Payload.DecodeSample("01000946", ppts, ppct) || ppts != 9 || ppct != 70)
                pfails.Insert("decode sample 9/70");
            if (OZL_Payload.EncodeSample(1000, 200) != "0103E8C8")
                pfails.Insert("encode sample 1000/200");
            if (!OZL_Payload.DecodeSample("0103E8C8", ppts, ppct) || ppts != 1000 || ppct != 200)
                pfails.Insert("decode sample 1000/200");
            if (OZL_Payload.EncodeCarrier(9) != "010009")
                pfails.Insert("encode carrier 9");
            if (!OZL_Payload.DecodeCarrier("010009", ppts) || ppts != 9)
                pfails.Insert("decode carrier 9");
            if (OZL_Payload.DecodeSample("", ppts, ppct))
                pfails.Insert("empty sample accepted");
            if (OZL_Payload.DecodeSample("02000946", ppts, ppct))
                pfails.Insert("foreign version accepted");
            if (OZL_Payload.DecodeSample("0100094", ppts, ppct))
                pfails.Insert("short sample accepted");
            if (OZL_Payload.DecodeSample("01000046", ppts, ppct))
                pfails.Insert("zero points accepted");
            if (OZL_Payload.DecodeSample("0103E9C8", ppts, ppct))
                pfails.Insert("1001 points accepted");
            if (OZL_Payload.DecodeSample("0100094G", ppts, ppct))
                pfails.Insert("bad digit accepted");
            if (OZL_Payload.DecodeSample("0103e8c8", ppts, ppct))
                pfails.Insert("lower case accepted");
            if (OZL_Payload.DecodeCarrier("01000946", ppts))
                pfails.Insert("sample read as carrier");
            if (OZL_Payload.PurityPct(0.7) != 70 || OZL_Payload.PurityPct(1.3) != 130 || OZL_Payload.PurityPct(2.5) != 200 || OZL_Payload.PurityPct(-1) != 0)
                pfails.Insert("purity percent");
            int ptotal = 15;
            detail = "payload selftest: " + (ptotal - pfails.Count()).ToString() + "/" + ptotal.ToString() + " ok";
            for (int pf = 0; pf < pfails.Count(); pf++)
                detail += "; FAIL " + pfails[pf];
            return pfails.Count() == 0;
        }

        detail = "oz_research: unknown op '" + op + "' (owner, put, fill, take, give, station, cargo, roll, points, grant, reset, demo, reload, tree, treeui, research, admin, bridge, payload_selftest, purity_selftest)";
        return false;
    }

    protected int m_OZL_Checks;

    protected void OZL_ExpectFloat(array<string> fails, string what, float got, float want)
    {
        m_OZL_Checks++;
        if (Math.AbsFloat(got - want) > 0.0001)
            fails.Insert(what + ": got " + got.ToString() + ", want " + want.ToString());
    }

    protected void OZL_ExpectTrue(array<string> fails, string what, bool ok)
    {
        m_OZL_Checks++;
        if (!ok)
            fails.Insert(what);
    }

    // STAND ONLY. The starting purity of a cycle and the two version-2
    // migrations, against objects built in memory: the live configs are not
    // touched (the clamp of Validate does write two WARNING lines, on purpose).
    // The cases are the contract of OZL_Rules.StartPurity: an own purity wins; a
    // negative one takes the BasePurity of the station's line, then of the line
    // of the sample the rule makes, then the named default; nothing negative
    // comes out.
    protected bool OZL_PuritySelftest(out string detail)
    {
        array<string> fails = new array<string>();
        m_OZL_Checks = 0;

        OZL_PointTypes pts = new OZL_PointTypes();
        OZL_PointType bio = new OZL_PointType();
        bio.Id = "bio";
        bio.Name = "Bio";
        bio.BasePurity = 0.5;
        pts.PointTypes.Insert(bio);

        OZL_PointTypes other = new OZL_PointTypes();
        OZL_PointType khabar = new OZL_PointType();
        khabar.Id = "khabar";
        khabar.Name = "Khabar";
        khabar.BasePurity = 0.3;
        other.PointTypes.Insert(khabar);

        OZL_Rule rule = new OZL_Rule();
        OZL_RuleOutput made = new OZL_RuleOutput();
        made.Classname = "OZL_Sample_Bio";
        made.Points = 1;
        rule.Outputs.Insert(made);

        // The default of a rule made by script is "take the line's".
        OZL_ExpectFloat(fails, "a new rule has Purity -1", rule.Purity, -1);
        OZL_ExpectFloat(fails, "the line of the station", OZL_Rules.StartPurity(rule, "OZL_Eco_Pack_Bio", pts), 0.5);
        OZL_ExpectFloat(fails, "no line on the station, the line of the sample", OZL_Rules.StartPurity(rule, "Rag", pts), 0.5);
        OZL_ExpectFloat(fails, "no point type for either line, the named default", OZL_Rules.StartPurity(rule, "OZL_Eco_Pack_Bio", other), OZL_Const.DEFAULT_PURITY);
        OZL_ExpectFloat(fails, "no point types at all, the named default", OZL_Rules.StartPurity(rule, "OZL_Eco_Pack_Bio", null), OZL_Const.DEFAULT_PURITY);
        rule.Purity = -0.25;
        OZL_ExpectFloat(fails, "any negative takes the line's", OZL_Rules.StartPurity(rule, "OZL_Eco_Pack_Bio", pts), 0.5);
        rule.Purity = 0.9;
        OZL_ExpectFloat(fails, "an own purity wins", OZL_Rules.StartPurity(rule, "OZL_Eco_Pack_Bio", pts), 0.9);
        rule.Purity = 0;
        OZL_ExpectFloat(fails, "an own zero is a purity, not the line's", OZL_Rules.StartPurity(rule, "OZL_Eco_Pack_Bio", pts), 0);

        // A value that never passed Validate must not come out as the line's.
        rule.Purity = -1;
        bio.BasePurity = -2;
        OZL_ExpectFloat(fails, "BasePurity -2 is not taken", OZL_Rules.StartPurity(rule, "OZL_Eco_Pack_Bio", pts), OZL_Const.DEFAULT_PURITY);
        bio.BasePurity = 3;
        OZL_ExpectFloat(fails, "BasePurity 3 is not taken", OZL_Rules.StartPurity(rule, "OZL_Eco_Pack_Bio", pts), OZL_Const.DEFAULT_PURITY);
        bio.BasePurity = 0.5;

        // Nothing negative, whatever the rule and the types hold.
        array<float> sweep = new array<float>();
        sweep.Insert(-5);
        sweep.Insert(-1);
        sweep.Insert(-0.001);
        sweep.Insert(0);
        sweep.Insert(0.3);
        sweep.Insert(1);
        int negative = 0;
        for (int s = 0; s < sweep.Count(); s++)
        {
            rule.Purity = sweep[s];
            if (OZL_Rules.StartPurity(rule, "OZL_Eco_Pack_Bio", pts) < 0)
                negative++;
            if (OZL_Rules.StartPurity(rule, "Rag", other) < 0)
                negative++;
            if (OZL_Rules.StartPurity(rule, "", null) < 0)
                negative++;
        }
        OZL_ExpectTrue(fails, "a negative purity came out " + negative.ToString() + " time(s)", negative == 0);

        // Rules, version 2 -> 3: 0.7 (the old default) becomes -1, the rest stays.
        OZL_Rules oldRules = new OZL_Rules();
        oldRules.Version = 2;
        OZL_RuleGroup oldGroup = new OZL_RuleGroup();
        oldGroup.Id = "g";
        oldRules.Groups.Insert(oldGroup);
        array<float> wasPurity = new array<float>();
        wasPurity.Insert(0.7);
        wasPurity.Insert(0.69999);
        wasPurity.Insert(0.5);
        wasPurity.Insert(0.9);
        wasPurity.Insert(0);
        wasPurity.Insert(0.71);
        for (int w = 0; w < wasPurity.Count(); w++)
        {
            OZL_Rule oldRule = new OZL_Rule();
            oldRule.Id = "r" + w.ToString();
            oldRule.Purity = wasPurity[w];
            oldGroup.Rules.Insert(oldRule);
        }
        OZL_ExpectTrue(fails, "rules: Migrate(1) refuses", !oldRules.Migrate(1));
        OZL_ExpectTrue(fails, "rules: Migrate(2) accepts", oldRules.Migrate(2));
        OZL_ExpectTrue(fails, "rules: the version is the latest", oldRules.Version == oldRules.LatestVersion());
        OZL_ExpectFloat(fails, "rules: 0.7 -> -1", oldGroup.Rules[0].Purity, -1);
        OZL_ExpectFloat(fails, "rules: 0.69999 -> -1", oldGroup.Rules[1].Purity, -1);
        OZL_ExpectFloat(fails, "rules: 0.5 stays", oldGroup.Rules[2].Purity, 0.5);
        OZL_ExpectFloat(fails, "rules: 0.9 stays", oldGroup.Rules[3].Purity, 0.9);
        OZL_ExpectFloat(fails, "rules: 0 stays", oldGroup.Rules[4].Purity, 0);
        OZL_ExpectFloat(fails, "rules: 0.71 stays", oldGroup.Rules[5].Purity, 0.71);

        // Point types, version 2 -> 3: an unwritten key reads as 0, and becomes 0.7.
        OZL_PointTypes oldTypes = new OZL_PointTypes();
        oldTypes.Version = 2;
        for (int t = 0; t < 2; t++)
        {
            OZL_PointType oldType = new OZL_PointType();
            oldType.Id = "t" + t.ToString();
            oldType.Name = "T";
            oldType.BasePurity = 0;
            oldTypes.PointTypes.Insert(oldType);
        }
        OZL_ExpectTrue(fails, "point types: Migrate(1) refuses", !oldTypes.Migrate(1));
        OZL_ExpectTrue(fails, "point types: Migrate(2) accepts", oldTypes.Migrate(2));
        OZL_ExpectTrue(fails, "point types: the version is the latest", oldTypes.Version == oldTypes.LatestVersion());
        OZL_ExpectFloat(fails, "point types: first gets 0.7", oldTypes.PointTypes[0].BasePurity, OZL_Const.DEFAULT_PURITY);
        OZL_ExpectFloat(fails, "point types: second gets 0.7", oldTypes.PointTypes[1].BasePurity, OZL_Const.DEFAULT_PURITY);

        // Validate clamps into 0..1, one warning per type.
        OZL_PointTypes wide = new OZL_PointTypes();
        wide.Version = wide.LatestVersion();
        array<float> widths = new array<float>();
        widths.Insert(1.5);
        widths.Insert(-0.2);
        widths.Insert(0.4);
        for (int v = 0; v < widths.Count(); v++)
        {
            OZL_PointType wt = new OZL_PointType();
            wt.Id = "w" + v.ToString();
            wt.Name = "W";
            wt.BasePurity = widths[v];
            wide.PointTypes.Insert(wt);
        }
        int clampWarnings;
        wide.Validate(clampWarnings);
        OZL_ExpectTrue(fails, "validate: two warnings, got " + clampWarnings.ToString(), clampWarnings == 2);
        OZL_ExpectFloat(fails, "validate: 1.5 -> 1", wide.PointTypes[0].BasePurity, 1);
        OZL_ExpectFloat(fails, "validate: -0.2 -> 0", wide.PointTypes[1].BasePurity, 0);
        OZL_ExpectFloat(fails, "validate: 0.4 stays", wide.PointTypes[2].BasePurity, 0.4);

        // The defaults carry 0.7 on every line.
        OZL_PointTypes fresh = new OZL_PointTypes();
        fresh.LoadDefaults();
        int off = 0;
        for (int d = 0; d < fresh.PointTypes.Count(); d++)
        {
            if (Math.AbsFloat(fresh.PointTypes[d].BasePurity - OZL_Const.DEFAULT_PURITY) > 0.0001)
                off++;
        }
        OZL_ExpectTrue(fails, "defaults: " + off.ToString() + " of " + fresh.PointTypes.Count().ToString() + " line(s) off 0.7", off == 0 && fresh.PointTypes.Count() > 0);
        OZL_ExpectTrue(fails, "defaults: the version is the latest", fresh.Version == fresh.LatestVersion());

        // Problem(): above 1 is refused as a purity; a negative one is not a purity complaint.
        OZL_Rule probe = new OZL_Rule();
        probe.Purity = 1.5;
        string why = OZL_Rules.Problem(probe, pts);
        OZL_ExpectTrue(fails, "problem: 1.5 refused as a purity", why.IndexOf("Purity") == 0);
        probe.Purity = -1;
        why = OZL_Rules.Problem(probe, pts);
        OZL_ExpectTrue(fails, "problem: -1 is not a purity complaint", why.IndexOf("Purity") != 0);
        probe.Purity = 1;
        why = OZL_Rules.Problem(probe, pts);
        OZL_ExpectTrue(fails, "problem: 1 is not a purity complaint", why.IndexOf("Purity") != 0);

        detail = "purity selftest: " + (m_OZL_Checks - fails.Count()).ToString() + "/" + m_OZL_Checks.ToString() + " ok";
        for (int f = 0; f < fails.Count(); f++)
            detail += "; FAIL " + fails[f];
        return fails.Count() == 0;
    }

    protected int OZL_IndexOf(array<string> list, string value)
    {
        for (int i = 0; i < list.Count(); i++)
        {
            if (list[i] == value)
                return i;
        }
        return -1;
    }

    // STAND ONLY. The demo state of the tree-screen mockup (its demoState(), the
    // case for the factions without a script of their own), so that every status
    // of the screen can be looked at without playing the tree:
    //   - in every branch of the owner, each tier-1 node and the first tier-2 node
    //     are done;
    //   - the pool of each line is 80% (rounded up) of what ALL the owner's tier-2
    //     nodes cost in that line;
    //   - one project, paid for by nobody, runs on the first other tier-2 node
    //     that the done ones have opened -- for its ResearchTimeSec, 600 s when
    //     that is 0 -- if there is such a node.
    // The owner's old state goes through the admin reset (a backed-up file, the
    // stations of the faction stop), exactly as after `reset`; the demo state is
    // then written in one save. Events of completion are not raised: nobody
    // listens to them and nothing here is a real completion.
    protected bool OZL_Demo(string owner, out string detail)
    {
        OZL_TreeConfig tree = OZL_Config.Get().Tree();

        // One pass over the owner's nodes: what to complete, what the tier-2
        // nodes cost per line, and the tier-2 nodes themselves in config order.
        array<string>       doneIds   = new array<string>();
        array<string>       lineTypes = new array<string>();
        array<int>          lineSums  = new array<int>();
        array<OZL_TreeNode> second    = new array<OZL_TreeNode>();
        int mine = 0;
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            if (!br || !br.BelongsTo(owner))
                continue;
            bool firstSecond = true;
            for (int n = 0; n < br.Nodes.Count(); n++)
            {
                OZL_TreeNode node = br.Nodes[n];
                if (!node || !tree.NodeBelongsTo(node, owner))
                    continue;
                mine++;
                int tier = node.Tier;
                if (tier < 1)
                    tier = 1;
                if (tier == 1)
                    doneIds.Insert(node.Id);
                if (tier != 2)
                    continue;
                second.Insert(node);
                if (firstSecond)
                {
                    doneIds.Insert(node.Id);
                    firstSecond = false;
                }
                for (int c = 0; c < node.Cost.Count(); c++)
                {
                    OZL_TreeCost cost = node.Cost[c];
                    if (!cost || cost.Type == "" || cost.Amount <= 0)
                        continue;
                    int at = OZL_IndexOf(lineTypes, cost.Type);
                    if (at < 0)
                    {
                        lineTypes.Insert(cost.Type);
                        lineSums.Insert(cost.Amount);
                    }
                    else
                    {
                        lineSums[at] = lineSums[at] + cost.Amount;
                    }
                }
            }
        }
        // A mistyped owner must not leave a state file behind.
        if (mine == 0)
        {
            detail = "demo: owner '" + owner + "' has no nodes in the tree";
            return false;
        }

        string why;
        if (!OZL_State.Reset(owner, why))
        {
            detail = "demo refused: " + why;
            return false;
        }
        OZL_FactionState st = OZL_State.Get(owner);
        if (!st)
        {
            detail = "demo: no state for owner '" + owner + "'";
            return false;
        }

        for (int d = 0; d < doneIds.Count(); d++)
        {
            if (!st.IsCompleted(doneIds[d]))
                st.CompletedNodes.Insert(doneIds[d]);
        }
        // ceil(0.8 * sum) in integers: (8 * sum + 9) / 10.
        for (int l = 0; l < lineTypes.Count(); l++)
        {
            int sum = lineSums[l];
            st.SetPoints(lineTypes[l], (sum * 8 + 9) / 10);
        }

        string project = "none";
        for (int s = 0; s < second.Count(); s++)
        {
            if (OZL_Tree.StatusOf(st, second[s]) != "available")
                continue;
            int span = second[s].ResearchTimeSec;
            if (span <= 0)
                span = 600;
            OZL_Project pr = new OZL_Project();
            pr.NodeId     = second[s].Id;
            pr.StarterUid = "demo";
            pr.EndSec     = OZL_Clock.NowSec() + span;
            st.ActiveProjects.Insert(pr);
            project = pr.NodeId + " (" + span.ToString() + " s)";
            break;
        }
        OZL_State.Save(owner);

        detail = "demo owner=" + owner + " done=" + st.CompletedNodes.Count().ToString();
        detail += " points=" + OZL_Points.Describe(owner) + " project=" + project;
        return true;
    }

    protected string OZL_Describe(OZL_Station st)
    {
        string s = st.GetType() + " state=" + st.OZL_GetState().ToString();
        s += " rule=" + st.OZL_RuleId();
        int left = st.OZL_EndSec() - OZL_Clock.NowSec();
        if (st.OZL_GetState() == OZL_Station.STATE_RUNNING)
            s += " left=" + left.ToString() + "s";
        s += " owner=" + st.OZL_StarterOwner();
        s += " now=" + OZL_Clock.NowSec().ToString() + " end=" + st.OZL_EndSec().ToString();
        if (st.OZL_HasPending())
            s += " pending=1";
        else
            s += " pending=0";

        array<EntityAI> cargo = new array<EntityAI>();
        st.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, cargo);
        // Compact: each distinct class[:payload] once, with a count.
        array<string> keys   = new array<string>();
        array<int>    counts = new array<int>();
        int total = 0;
        for (int i = 0; i < cargo.Count(); i++)
        {
            EntityAI e = cargo[i];
            if (!e || e == st)
                continue;
            total++;
            string key = e.GetType();
            string dpay = "";
            OZL_Sample_Base ds = OZL_Sample_Base.Cast(e);
            if (ds)
                dpay = ds.OZL_GetPayload();
            OZL_Carrier_Base dc = OZL_Carrier_Base.Cast(e);
            if (dc)
                dpay = dc.OZL_GetPayload();
            if (dpay != "")
                key += ":" + dpay;
            int k = keys.Find(key);
            if (k > -1)
                counts[k] = counts[k] + 1;
            else
            {
                keys.Insert(key);
                counts.Insert(1);
            }
        }
        string inside = "";
        for (int j = 0; j < keys.Count(); j++)
        {
            if (inside != "")
                inside += ",";
            inside += keys[j] + "x" + counts[j].ToString();
        }
        s += " cargo=" + total.ToString() + "[" + inside + "]";
        return s;
    }

    // The nearest station of `target` within `radius` of the player (or of
    // `pos`). Registered live stations only -- what the mod itself knows.
    protected OZL_Station OZL_FindStation(map<string, string> args, out string detail)
    {
        string target = OZL_Arg(args, "target", "");
        float radius = OZL_Arg(args, "radius", "30").ToFloat();
        vector pos;
        string posText = OZL_Arg(args, "pos", "");
        if (posText != "")
        {
            pos = posText.ToVector();
        }
        else if (!OZL_PlayerPos(pos))
        {
            detail = "target needs pos=\"x y z\" when nobody is connected";
            return null;
        }

        OZL_Station best;
        float bestDist = radius;
        for (int i = 0; i < OZL_Station.s_All.Count(); i++)
        {
            OZL_Station st = OZL_Station.s_All[i];
            if (!st)
                continue;
            if (target != "" && st.GetType() != target)
                continue;
            float d = vector.Distance(st.GetPosition(), pos);
            if (d <= bestDist)
            {
                best = st;
                bestDist = d;
            }
        }
        if (!best)
        {
            detail = "no station '" + target + "' within " + radius.ToString() + " m";
            return null;
        }
        return best;
    }

    // STAND ONLY. Pretend the connected player holds the post that lets them
    // spend (BasePost on the base axis, ResearchPost in an org) by applying a
    // role projection the way the Discord bridge does. The next bridge poll
    // (a few seconds) puts the real roles back, so it holds for THIS call:
    // the gate itself (OZL_Access -> OZ_Identity -> OZ_Roles) runs unchanged.
    protected void OZL_Pretend(PlayerBase p)
    {
        if (!p || !p.GetIdentity())
            return;
        string uid = p.GetIdentity().GetPlainId();
        OZL_Settings st = OZL_Config.Get().Settings();
        OZ_RoleView v = new OZ_RoleView();
        OZ_RoleView had = OZ_Roles.Of(uid);
        v.Uid = uid;
        if (had)
        {
            v.Base  = had.Base;
            v.Org   = had.Org;
            v.Rank  = had.Rank;
            v.FRank = had.FRank;
        }
        else
        {
            v.Base = OZ_Identity.Get().BaseOf(uid);
            v.Org  = OZ_Identity.Get().OrgOf(uid);
        }
        string post = st.ResearchPost;
        if (v.Org == "")
            post = st.BasePost;
        if (post != "" && v.Posts.Find(post) < 0)
            v.Posts.Insert(post);
        OZ_Roles.Apply(v);
    }
    // STAND ONLY. Pretend the connected player belongs to one faction, so the
    // tree screen can be looked at as every faction in turn without seven
    // characters and seven characters' worth of Discord roles. Same road as
    // OZL_Pretend -- a role projection, which the next bridge poll undoes by
    // itself -- and the same reason: nothing downstream is special-cased, the
    // owner is still resolved by OZ_Identity from the roles it finds.
    protected void OZL_PretendOrg(PlayerBase p, string org)
    {
        if (!p || !p.GetIdentity())
            return;
        string uid = p.GetIdentity().GetPlainId();
        OZ_RoleView v = new OZ_RoleView();
        OZ_RoleView had = OZ_Roles.Of(uid);
        v.Uid = uid;
        if (had)
        {
            v.Base  = had.Base;
            v.Rank  = had.Rank;
            v.FRank = had.FRank;
            for (int i = 0; i < had.Posts.Count(); i++)
                v.Posts.Insert(had.Posts[i]);
        }
        else
        {
            v.Base = OZ_Identity.Get().BaseOf(uid);
        }
        v.Org = org;
        OZ_Roles.Apply(v);
    }

    protected PlayerBase OZL_FirstPlayer()
    {
        array<Man> players = new array<Man>();
        GetGame().GetPlayers(players);
        if (players.Count() == 0)
            return null;
        return PlayerBase.Cast(players.Get(0));
    }

    protected bool OZL_PlayerPos(out vector pos)
    {
        PlayerBase p = OZL_FirstPlayer();
        if (!p)
            return false;
        pos = p.GetPosition();
        return true;
    }
}
