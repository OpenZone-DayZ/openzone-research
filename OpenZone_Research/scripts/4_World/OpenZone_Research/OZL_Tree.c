// Дерево на стані фракції: статуси вузлів, старт дослідження, завершення
// проєктів за часом, відповідь `tree` для клієнта.
//
// Порт вимог ZP_FactionDB/ZP_Factions.StartResearch: вартість списується
// цілком у мить старту (миттєвого чи проєкту), матеріали -- з карго ВЛАСНОГО
// термінала поруч, проєкт живе у файлі фракції й завершується опитуванням
// раз на десять секунд -- офлайновий стартер платить так само, як
// присутній. Скасування немає.

class OZL_Tree
{
    static const float TERMINAL_RANGE = 3.0;
    static const float POLL_SEC       = 10.0;

    // ---------- статуси ----------

    static bool ParentsSatisfied(OZL_FactionState st, OZL_TreeNode node)
    {
        if (node.Parents.Count() == 0)
            return true;
        string pm = node.ParentsMode;
        pm.ToLower();
        int okCount = 0;
        for (int i = 0; i < node.Parents.Count(); i++)
        {
            if (st && st.IsCompleted(node.Parents[i]))
                okCount++;
        }
        if (pm == "any")
            return okCount > 0;
        return okCount == node.Parents.Count();
    }

    // Належність власникові тут не питається: вузол, що не належить, у дерево
    // власника не потрапляє взагалі (OZL_TreeConfig.NodeBelongsTo).
    static string StatusOf(OZL_FactionState st, OZL_TreeNode node)
    {
        if (st && st.IsCompleted(node.Id))
            return "completed";
        if (st && st.ProjectOf(node.Id))
            return "researching";
        if (ParentsSatisfied(st, node))
            return "available";
        return "locked";
    }

    // ---------- старт ----------

    static bool Start(PlayerBase who, string owner, string nodeId, out string why)
    {
        why = "";
        if (!who || !GetGame().IsServer())
        {
            why = "STR_OZ_ERR_INTERNAL";
            return false;
        }
        string uid = "";
        if (who.GetIdentity())
            uid = who.GetIdentity().GetPlainId();

        if (!OZL_Access.MaySpend(uid))
        {
            why = "STR_OZL_ERR_NO_ACCESS";
            return false;
        }

        OZL_TreeConfig tree = OZL_Config.Get().Tree();
        OZL_TreeNode node = tree.FindNode(nodeId);
        if (!node)
        {
            why = "STR_OZL_ERR_UNKNOWN_NODE";
            return false;
        }
        if (!tree.NodeBelongsTo(node, owner))
        {
            why = "STR_OZL_ERR_NOT_OWNER";
            return false;
        }

        OZL_FactionState st = OZL_State.Get(owner);
        if (!st)
        {
            why = "STR_OZL_ERR_STATE";
            return false;
        }
        string status = StatusOf(st, node);
        if (status == "completed")
        {
            why = "STR_OZL_ERR_COMPLETED";
            return false;
        }
        if (status == "researching")
        {
            why = "STR_OZL_ERR_BUSY";
            return false;
        }
        if (status == "locked")
        {
            why = "STR_OZL_ERR_LOCKED";
            return false;
        }

        // Термінал своєї фракції поруч: саме в його карго лежать матеріали.
        EntityAI terminal = FindOwnTerminal(who, owner);
        if (!terminal)
        {
            why = "STR_OZL_ERR_NO_TERMINAL";
            return false;
        }

        // План матеріалів -- до будь-яких списань.
        array<ItemBase> planItems   = new array<ItemBase>();
        array<int>      planAmounts = new array<int>();
        string planWhy;
        if (!BuildItemPlan(terminal, node.ItemCost, planItems, planAmounts, planWhy))
        {
            why = "STR_OZL_ERR_NEED_ITEMS";
            OZL_Log.Dbg("research '" + nodeId + "' for " + owner + ": " + planWhy);
            return false;
        }

        // Бали: дублі типів зливаються, інакше кожен запис звірявся б із тим
        // самим балансом і списання завело б пул у мінус.
        array<ref OZL_TreeCost> cost = new array<ref OZL_TreeCost>();
        MergeCost(node.Cost, cost);
        if (!OZL_Points.Spend(owner, cost, why))
            return false;
        OZL_RuleEngine.ConsumePlan(planItems, planAmounts);

        if (node.ResearchTimeSec <= 0)
        {
            Complete(owner, node.Id);
            why = "STR_OZL_MSG_RESEARCHED";
            OZL_Log.Dbg("research '" + nodeId + "' done at once for " + owner + " by " + uid);
            return true;
        }

        OZL_Project p = new OZL_Project();
        p.NodeId     = node.Id;
        p.StarterUid = uid;
        p.EndSec     = OZL_Clock.NowSec() + node.ResearchTimeSec;
        st.ActiveProjects.Insert(p);
        OZL_State.Save(owner);
        why = "STR_OZL_MSG_PROJECT";
        OZL_Log.Dbg("research '" + nodeId + "' started for " + owner + " by " + uid + ", " + node.ResearchTimeSec.ToString() + " s");
        return true;
    }

    private static void MergeCost(array<ref OZL_TreeCost> src, array<ref OZL_TreeCost> dst)
    {
        for (int i = 0; i < src.Count(); i++)
        {
            OZL_TreeCost c = src[i];
            if (!c || c.Type == "" || c.Amount <= 0)
                continue;
            bool merged = false;
            for (int j = 0; j < dst.Count(); j++)
            {
                if (dst[j].Type == c.Type)
                {
                    dst[j].Amount = dst[j].Amount + c.Amount;
                    merged = true;
                    break;
                }
            }
            if (!merged)
                dst.Insert(c.Copy());
        }
    }

    // Термінал власної фракції в межах TERMINAL_RANGE: клас звіряється тим
    // самим джерелом, що й дія відкриття дерева, тож чужий не потрапляє.
    static EntityAI FindOwnTerminal(PlayerBase player, string owner)
    {
        array<Object> objects = new array<Object>();
        array<CargoBase> proxies = new array<CargoBase>();
        GetGame().GetObjectsAtPosition3D(player.GetPosition(), TERMINAL_RANGE, objects, proxies);
        OZL_Owners owners = OZL_Config.Get().Owners();
        for (int i = 0; i < objects.Count(); i++)
        {
            Object o = objects[i];
            if (!o || o == player)
                continue;
            EntityAI e = EntityAI.Cast(o);
            if (!e || e.IsDamageDestroyed())
                continue;
            if (!owners.IsTerminalClass(o.GetType()))
                continue;
            if (owners.IsTerminalFor(owner, o.GetType()))
                return e;
        }
        return null;
    }

    // План матеріалів по карго термінала: стаки резервуються, вкладені
    // конфлікти тут не потрібні -- у карго термінала лежать окремі предмети.
    private static bool BuildItemPlan(EntityAI holder, array<ref OZL_TreeItemCost> itemCost, array<ItemBase> planItems, array<int> planAmounts, out string why)
    {
        why = "";
        if (!itemCost || itemCost.Count() == 0)
            return true;
        array<EntityAI> cargo = new array<EntityAI>();
        holder.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, cargo);
        for (int k = 0; k < itemCost.Count(); k++)
        {
            OZL_TreeItemCost ic = itemCost[k];
            if (!ic)
                continue;
            int remaining = ic.Quantity;
            for (int c = 0; c < cargo.Count(); c++)
            {
                if (remaining <= 0)
                    break;
                ItemBase ib = ItemBase.Cast(cargo[c]);
                if (!ib || ib == holder || ib.IsRuined())
                    continue;
                if (!OZL_RuleEngine.MatchInput(ib.GetType(), OZL_Sample_Base.ContentOf(ib), ic.Classname, ic.Content))
                    continue;
                int already = 0;
                int idx = planItems.Find(ib);
                if (idx > -1)
                    already = planAmounts[idx];
                int avail = 1;
                if (ib.ConfigGetBool("canBeSplit"))
                    avail = ib.GetQuantity();
                avail -= already;
                if (avail <= 0)
                    continue;
                int take = avail;
                if (take > remaining)
                    take = remaining;
                if (idx > -1)
                {
                    planAmounts[idx] = already + take;
                }
                else
                {
                    planItems.Insert(ib);
                    planAmounts.Insert(take);
                }
                remaining -= take;
            }
            if (remaining > 0)
            {
                why = "short of " + remaining.ToString() + " x " + ic.Classname + " in the terminal cargo";
                return false;
            }
        }
        return true;
    }

    // ---------- завершення ----------

    static void Complete(string owner, string nodeId)
    {
        OZL_FactionState st = OZL_State.Get(owner);
        if (!st)
            return;
        if (!st.IsCompleted(nodeId))
            st.CompletedNodes.Insert(nodeId);
        for (int i = st.ActiveProjects.Count() - 1; i >= 0; i--)
        {
            if (st.ActiveProjects[i] && st.ActiveProjects[i].NodeId == nodeId)
                st.ActiveProjects.RemoveOrdered(i);
        }
        OZL_State.Save(owner);
        OZL_Log.Info("node '" + nodeId + "' completed for owner '" + owner + "'");
        OZL_Events.OnNodeCompleted.Invoke(owner, nodeId);
    }

    // Раз на POLL_SEC: проєкти всіх відомих власників, чий строк минув.
    // Вузол, що зник із конфігу, знімається з попередженням.
    static void Poll()
    {
        if (OZL_Config.Get().Revision() == 0)
            return;
        int now = OZL_Clock.NowSec();
        array<string> owners;
        OZL_State.Owners(owners);
        for (int o = 0; o < owners.Count(); o++)
        {
            string owner = owners[o];
            OZL_FactionState st = OZL_State.Get(owner);
            if (!st)
                continue;
            for (int i = st.ActiveProjects.Count() - 1; i >= 0; i--)
            {
                OZL_Project p = st.ActiveProjects[i];
                if (!p)
                {
                    st.ActiveProjects.RemoveOrdered(i);
                    continue;
                }
                if (now < p.EndSec)
                    continue;
                if (!OZL_Config.Get().Tree().FindNode(p.NodeId))
                {
                    OZL_Log.Warn("project '" + p.NodeId + "' of owner '" + owner + "': the node is gone from the tree, project dropped");
                    st.ActiveProjects.RemoveOrdered(i);
                    OZL_State.Save(owner);
                    continue;
                }
                Complete(owner, p.NodeId);
            }
        }
    }

    // ---------- відповідь клієнтові ----------

    // Ігрова назва класу: рушій знає її на сервері так само, як на клієнті
    // (ConfigGetTextOut розв'язує $STR_ мовою сервера). П'ять коренів у тому
    // ж порядку, що в дампі класів ядра; класу без назви лишається сам клас,
    // бо порожній рядок у картці гірший за ім'я класу.
    static string ItemName(string cls)
    {
        if (cls == "")
            return "";
        string name = GetGame().ConfigGetTextOut("CfgVehicles " + cls + " displayName");
        if (name == "")
            name = GetGame().ConfigGetTextOut("CfgMagazines " + cls + " displayName");
        if (name == "")
            name = GetGame().ConfigGetTextOut("cfgWeapons " + cls + " displayName");
        if (name == "")
            name = GetGame().ConfigGetTextOut("CfgAmmo " + cls + " displayName");
        if (name == "" || name.IndexOf("$") == 0 || name.IndexOf("STR_") == 0)
            return cls;
        return name;
    }

    // Наскільки глибоко закритий вузол лежить за межею відкритого: 0 --
    // вузол не закритий, 1 -- його батько відкритий, 2 -- батько закритий і
    // сам лежить на глибині 1, і так далі. Вузол без батьків, який закрито,
    // має глибину 1: він на самій межі. Settings.TreeVisibilityDepth каже,
    // скільки таких рівнів показувати; глибші клієнт не отримує взагалі --
    // туман війни рахує сервер, бо клієнтові нічого знати про них.
    static int LockedDepth(OZL_FactionState st, OZL_TreeConfig tree, OZL_TreeNode node, map<string, int> memo, int guard)
    {
        if (StatusOf(st, node) != "locked")
            return 0;
        int known;
        if (memo.Find(node.Id, known))
            return known;
        if (guard > 32)
            return 1;
        // Поки глибина рахується, вузол уже "в роботі": цикл у батьках не
        // має ганяти рекурсію по колу.
        memo.Set(node.Id, 1);
        int best = -1;
        for (int i = 0; i < node.Parents.Count(); i++)
        {
            OZL_TreeNode par = tree.FindNode(node.Parents[i]);
            if (!par)
                continue;
            int d = LockedDepth(st, tree, par, memo, guard + 1) + 1;
            if (best < 0 || d < best)
                best = d;
        }
        if (best < 0)
            best = 1;
        memo.Set(node.Id, best);
        return best;
    }

    static OZL_TreeView View(string owner, string uid)
    {
        OZL_Config cfg = OZL_Config.Get();
        OZ_IdentityService id = OZ_Identity.Get();
        OZL_FactionState st = OZL_State.Get(owner);

        OZL_TreeView v = new OZL_TreeView();
        v.Owner      = owner;
        v.OwnerName  = id.FactionName(owner);
        v.OwnerColor = id.FactionColor(owner, 255);
        v.Background = cfg.Owners().BackgroundOf(owner);
        v.MaySpend   = OZL_Access.MaySpend(uid);
        v.Now        = OZL_Clock.NowSec();

        OZL_PointTypes pts = cfg.PointTypes();
        int i;
        for (i = 0; i < pts.PointTypes.Count(); i++)
        {
            OZL_PointType pt = pts.PointTypes[i];
            if (!pt)
                continue;
            int have = 0;
            if (st)
                have = st.PointsOf(pt.Id);
            v.Pool.Insert(new OZL_KV(pt.Id, have));
            OZL_PointName pn = new OZL_PointName();
            pn.Id       = pt.Id;
            pn.Name     = pt.Name;
            pn.Category = OZL_PointTypes.DimensionName(pts.Categories, pt.Category);
            pn.Kind     = OZL_PointTypes.DimensionName(pts.Kinds, pt.Kind);
            pn.Tier     = pt.Tier;
            v.Names.Insert(pn);
        }

        OZL_TreeConfig tree = cfg.Tree();
        // Туман війни: скільки рівнів закритих вузлів показувати за межею
        // відкритого. Пам'ять глибин одна на весь обхід -- вузол спільний для
        // двох гілок рахується раз.
        int depthLimit = cfg.Settings().TreeVisibilityDepth;
        map<string, int> depthMemo = new map<string, int>();
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            if (!br || !br.BelongsTo(owner))
                continue;
            OZL_BranchView bv = new OZL_BranchView();
            bv.Id   = br.Id;
            bv.Name = br.Name;
            for (int all = 0; all < br.Nodes.Count(); all++)
            {
                if (br.Nodes[all] && tree.NodeBelongsTo(br.Nodes[all], owner))
                    bv.Total++;
            }
            for (int n = 0; n < br.Nodes.Count(); n++)
            {
                OZL_TreeNode node = br.Nodes[n];
                if (!node || !tree.NodeBelongsTo(node, owner))
                    continue;
                if (LockedDepth(st, tree, node, depthMemo, 0) > depthLimit)
                    continue;
                OZL_NodeView nv = new OZL_NodeView();
                nv.Id       = node.Id;
                nv.Name     = node.Name;
                nv.Desc     = node.Description;
                nv.Icon     = node.Icon;
                nv.Status   = StatusOf(st, node);
                nv.Duration = node.ResearchTimeSec;
                if (st)
                {
                    OZL_Project pr = st.ProjectOf(node.Id);
                    if (pr)
                        nv.EndSec = pr.EndSec;
                }
                nv.Tier = node.Tier;
                if (nv.Tier < 1)
                    nv.Tier = 1;
                for (i = 0; i < node.Parents.Count(); i++)
                    nv.Parents.Insert(node.Parents[i]);
                for (i = 0; i < node.Cost.Count(); i++)
                {
                    if (node.Cost[i])
                        nv.Cost.Insert(new OZL_KV(node.Cost[i].Type, node.Cost[i].Amount));
                }
                for (i = 0; i < node.ItemCost.Count(); i++)
                {
                    OZL_TreeItemCost ic = node.ItemCost[i];
                    if (!ic)
                        continue;
                    OZL_ItemView iv = new OZL_ItemView();
                    iv.Cls   = ic.Classname;
                    iv.Name  = ItemName(ic.Classname);
                    if (ic.Content != "")
                        iv.Name += " [" + ic.Content + "]";
                    iv.Qty   = ic.Quantity;
                    nv.Items.Insert(iv);
                }
                bv.Nodes.Insert(nv);
            }
            v.Branches.Insert(bv);
        }
        return v;
    }

    static string ViewJson(string owner, string uid)
    {
        OZL_TreeView v = View(owner, uid);
        return JsonFileLoader<OZL_TreeView>.JsonMakeData(v);
    }
}
