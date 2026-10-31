// Дерево на стані фракції: статуси вузлів, старт дослідження, завершення
// проєктів за часом, відповідь `tree` для клієнта.
//
// Вартість списується
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

    // Статус для екрана дерева. StatusOf лишається, як був: ним живуть старт,
    // туман і адмінка. Екрану потрібен ще один: «не вистачає» (short) --
    // батьки виконані, а пул фракції чи матеріали в терміналі не покривають
    // вартість. Це підказка, а не дозвіл: Start перевіряє все сам, як і досі.
    //
    // items -- матеріали вузла з уже порахованим Have. Have < 0 (невідомо:
    // відповідь без гравця чи без термінала) статусу не міняє, бо відсутність
    // відомостей не є нестачею.
    static string ViewStatus(OZL_FactionState st, OZL_TreeNode node, array<ref OZL_ItemView> items)
    {
        string status = StatusOf(st, node);
        if (status != "available")
            return status;

        // Бали: дублі типів зливаються, як при списанні -- інакше вузол з двома
        // записами одного типу виглядав би посильним, а Start його не пустив би.
        array<ref OZL_TreeCost> cost = new array<ref OZL_TreeCost>();
        MergeCost(node.Cost, cost);
        for (int i = 0; i < cost.Count(); i++)
        {
            int pool = 0;
            if (st)
                pool = st.PointsOf(cost[i].Type);
            if (pool < cost[i].Amount)
                return "short";
        }

        if (items)
        {
            for (int k = 0; k < items.Count(); k++)
            {
                OZL_ItemView iv = items[k];
                if (iv && iv.Have >= 0 && iv.Have < iv.Qty)
                    return "short";
            }
        }
        return "available";
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
                if (!OZL_RuleEngine.MatchInput(ib.GetType(), ic.Classname))
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

    // Глибина вузла для туману війни: скільки кроків від виконаного. Виконаний
    // -- 0; вузол без батьків -- 1; решта -- 1 + найменша глибина батьків (батько,
    // якого немає в конфігу, не рахується; якщо не знайдено жодного -- 1).
    // Settings.TreeVisibilityDepth каже, скільки кроків показувати; решту
    // клієнт отримує безіменними заглушками -- туман рахує сервер, бо клієнтові
    // нічого знати про прихований вузол.
    static int FogDepth(OZL_FactionState st, OZL_TreeConfig tree, OZL_TreeNode node, map<string, int> memo, int guard)
    {
        if (st && st.IsCompleted(node.Id))
            return 0;
        if (node.Parents.Count() == 0)
            return 1;
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
            int d = FogDepth(st, tree, par, memo, guard + 1) + 1;
            if (best < 0 || d < best)
                best = d;
        }
        if (best < 0)
            best = 1;
        memo.Set(node.Id, best);
        return best;
    }

    // Чи показує туман вузол: корінь, виконаний і той, що в роботі, видно
    // завжди; решту -- якщо глибина в межах. При limit = 1 це рівно правило
    // мокапа: корені, виконані, ті, що в роботі, і вузли, у яких виконано
    // хоча б одного батька.
    static bool NodeVisible(OZL_FactionState st, OZL_TreeConfig tree, OZL_TreeNode node, map<string, int> memo, int limit)
    {
        if (node.Parents.Count() == 0)
            return true;
        if (st && st.IsCompleted(node.Id))
            return true;
        if (st && st.ProjectOf(node.Id))
            return true;
        return FogDepth(st, tree, node, memo, 0) <= limit;
    }

    // Чи вузол є в цій відповіді й видимий: щойно його немає в shown (чужий
    // власникові або зниклий із конфігу), він не видимий.
    private static bool IsShown(map<string, bool> shown, string nodeId)
    {
        bool vis;
        if (!shown.Find(nodeId, vis))
            return false;
        return vis;
    }

    // Скільки предметів, що підходять під classname, лежить у карго holder.
    // Добір той самий, що в BuildItemPlan: MatchInput, зіпсовані не рахуються,
    // стек дає свою кількість, решта -- по одному.
    private static int CountInCargo(array<EntityAI> cargo, EntityAI holder, string classname)
    {
        int total = 0;
        for (int c = 0; c < cargo.Count(); c++)
        {
            ItemBase ib = ItemBase.Cast(cargo[c]);
            if (!ib || ib == holder || ib.IsRuined())
                continue;
            if (!OZL_RuleEngine.MatchInput(ib.GetType(), classname))
                continue;
            int amount = 1;
            if (ib.ConfigGetBool("canBeSplit"))
                amount = ib.GetQuantity();
            if (amount > 0)
                total += amount;
        }
        return total;
    }

    // Дерево власника для екрана. player -- той, хто питає: від нього шукається
    // термінал власної фракції, у чиєму карго рахуються матеріали (Have). Без
    // гравця (дамп моста) чи без термінала поруч Have = -1.
    static OZL_TreeView View(string owner, string uid, PlayerBase player)
    {
        OZL_Config cfg = OZL_Config.Get();
        OZ_IdentityService id = OZ_Identity.Get();
        OZL_FactionState st = OZL_State.Get(owner);

        OZL_TreeView v = new OZL_TreeView();
        v.Owner      = owner;
        v.OwnerName  = id.FactionName(owner);
        v.OwnerColor = id.FactionColor(owner, 255);
        v.Background = cfg.Owners().BackgroundOf(owner);
        v.Skin       = cfg.Owners().SkinOf(owner);
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
            pn.Id   = pt.Id;
            pn.Name = pt.Name;
            v.Names.Insert(pn);
        }

        OZL_TreeConfig tree = cfg.Tree();

        // Матеріали рахуються по карго власного термінала поруч із гравцем --
        // один раз на відповідь, а не на кожен вузол. Нема гравця чи термінала
        // -- terminal лишається порожнім, і в усіх матеріалів Have = -1.
        EntityAI terminal;
        array<EntityAI> cargo = new array<EntityAI>();
        if (player)
            terminal = FindOwnTerminal(player, owner);
        if (terminal)
            terminal.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, cargo);

        // Перший прохід -- туман: які вузли власника видно. Другий збирає
        // відповідь, і йому треба знати це наперед: прихованому вузлові й
        // видимому з прихованим батьком дозволено згадати лише видимих батьків.
        // Пам'ять глибин одна на весь обхід -- батько з іншої гілки рахується раз.
        int depthLimit = cfg.Settings().TreeVisibilityDepth;
        map<string, int> depthMemo = new map<string, int>();
        map<string, bool> shown = new map<string, bool>();
        for (int b1 = 0; b1 < tree.Branches.Count(); b1++)
        {
            OZL_TreeBranch br1 = tree.Branches[b1];
            if (!br1 || !br1.BelongsTo(owner))
                continue;
            for (int n1 = 0; n1 < br1.Nodes.Count(); n1++)
            {
                OZL_TreeNode node1 = br1.Nodes[n1];
                if (!node1 || !tree.NodeBelongsTo(node1, owner))
                    continue;
                bool vis = NodeVisible(st, tree, node1, depthMemo, depthLimit);
                shown.Set(node1.Id, vis);
            }
        }

        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            if (!br || !br.BelongsTo(owner))
                continue;
            OZL_BranchView bv = new OZL_BranchView();
            bv.Id   = br.Id;
            bv.Name = br.Name;
            // Місце вузла рахується серед вузлів гілки, що належать власникові,
            // видимих і прихованих разом -- тож Index не стрибає, коли туман
            // відступає.
            int place = 0;
            for (int n = 0; n < br.Nodes.Count(); n++)
            {
                OZL_TreeNode node = br.Nodes[n];
                if (!node || !shown.Contains(node.Id))
                    continue;
                int index = place;
                place++;
                int tier = node.Tier;
                if (tier < 1)
                    tier = 1;

                if (!IsShown(shown, node.Id))
                {
                    OZL_HiddenView hv = new OZL_HiddenView();
                    hv.Index = index;
                    hv.Tier  = tier;
                    for (i = 0; i < node.Parents.Count(); i++)
                    {
                        if (IsShown(shown, node.Parents[i]))
                            hv.Parents.Insert(node.Parents[i]);
                    }
                    bv.Hidden.Insert(hv);
                    continue;
                }

                OZL_NodeView nv = new OZL_NodeView();
                nv.Id       = node.Id;
                nv.Name     = node.Name;
                nv.Desc     = node.Description;
                nv.Icon     = node.Icon;
                nv.Duration = node.ResearchTimeSec;
                nv.Index    = index;
                nv.Tier     = tier;
                if (st)
                {
                    OZL_Project pr = st.ProjectOf(node.Id);
                    if (pr)
                        nv.EndSec = pr.EndSec;
                }
                // Булеве значення йде в поле лише з локальної змінної.
                string pm = node.ParentsMode;
                pm.ToLower();
                bool anyParent = false;
                if (pm == "any")
                    anyParent = true;
                nv.Any = anyParent;
                // Батько, якого власник не бачить, їде порожнім рядком: його id
                // (а за ним і назва вузла) клієнтові знати не треба.
                for (i = 0; i < node.Parents.Count(); i++)
                {
                    if (IsShown(shown, node.Parents[i]))
                        nv.Parents.Insert(node.Parents[i]);
                    else
                        nv.Parents.Insert("");
                }
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
                    iv.Qty   = ic.Quantity;
                    if (terminal)
                        iv.Have = CountInCargo(cargo, terminal, ic.Classname);
                    nv.Items.Insert(iv);
                }
                nv.Status = ViewStatus(st, node, nv.Items);
                bv.Nodes.Insert(nv);
            }
            // Усього вузлів гілки в цього власника -- і показаних, і ні:
            // лічильник "досліджено N / M" не росте, коли туман відступає.
            bv.Total = place;
            v.Branches.Insert(bv);
        }
        return v;
    }

    static string ViewJson(string owner, string uid, PlayerBase player)
    {
        OZL_TreeView v = View(owner, uid, player);
        return JsonFileLoader<OZL_TreeView>.JsonMakeData(v);
    }
}
