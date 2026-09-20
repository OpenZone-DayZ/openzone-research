// The `oz_research` verb, following the bridge's contract for project verbs.
// A stand tool: it reaches what no world_* verb can -- the cargo of a station
// that cannot be held, the faction pool, the owner the core reports.
//
//   world_exec verb=oz_research args={"op":"owner"}
//   world_exec verb=oz_research args={"op":"put","item":"Apple","target":"OZL_SampleFridge"}
//   world_exec verb=oz_research args={"op":"put","item":"OZL_Sample_01","content":"Apple","purity":"0.8","target":"OZL_Microscope"}
//   world_exec verb=oz_research args={"op":"fill","item":"Rag","target":"OZL_SampleFridge"}
//   world_exec verb=oz_research args={"op":"take","item":"Rag","target":"OZL_SampleFridge"}
//   world_exec verb=oz_research args={"op":"station","target":"OZL_SampleFridge"}
//   world_exec verb=oz_research args={"op":"points","owner":"mercenary"}
//   world_exec verb=oz_research args={"op":"grant","owner":"mercenary","type":"bio","amount":"5"}
//   world_exec verb=oz_research args={"op":"reset","owner":"mercenary"}
//   world_exec verb=oz_research args={"op":"reload"}
//   world_exec verb=oz_research args={"op":"tree","as":"post"}          (as=post: stand only, see OZL_Pretend)
//   world_exec verb=oz_research args={"op":"research","node":"pb_osnovy","as":"post"}
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
            string content = OZL_Arg(args, "content", "");
            float purity = OZL_Arg(args, "purity", "1").ToFloat();
            OZL_Sample_Base.ApplyFields(created, content, purity);
            OZL_Carrier_Base.ApplyState(created, content);
            detail = "created " + item + " in " + st.GetType() + " cargo";
            if (content != "")
                detail += " content=" + content + " purity=" + purity.ToString();
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
            // Create an item in the player's hands, with a sample content or a
            // carrier state: what a deposit or an identify test needs held.
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
            string giveContent = OZL_Arg(args, "content", "");
            float givePurity = OZL_Arg(args, "purity", "1").ToFloat();
            OZL_Sample_Base.ApplyFields(held, giveContent, givePurity);
            OZL_Carrier_Base.ApplyState(held, giveContent);
            detail = "created " + giveCls + " in hands";
            if (giveContent != "")
                detail += " content=" + giveContent;
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
            if (OZL_Arg(args, "as", "") == "post")
                OZL_Pretend(pt);
            detail = OZL_Tree.ViewJson(OZL_Owner.OfPlayer(pt), tuid);
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
        if (op == "reload")
        {
            OZL_Config.Reload();
            detail = "reloaded: " + OZL_Config.Get().Counters();
            return true;
        }

        detail = "oz_research: unknown op '" + op + "' (owner, put, fill, take, give, station, points, grant, reset, reload, tree, research)";
        return false;
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
        // Compact: each distinct class[:content@purity] once, with a count.
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
            string content = OZL_Sample_Base.ContentOf(e);
            if (content != "")
                key += ":" + content + "@" + OZL_Sample_Base.PurityOf(e).ToString();
            string carrier = OZL_Carrier_Base.StateOf(e);
            if (carrier != "")
                key += ":" + carrier;
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
