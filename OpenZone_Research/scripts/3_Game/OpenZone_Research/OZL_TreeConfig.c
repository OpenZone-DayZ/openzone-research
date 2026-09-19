// Дерево технологій: OZ_Research_Tree.json -- гілки з вузлами, дані.
//
// Гілка належить фракціям зі свого списку Owners (порожньо -- усім); вузол
// може звузити список власним RequiredFactions, а порожній список вузла
// успадковує гілку й НЕ тече всім. Це одне правило в одному місці:
// NodeBelongsTo. Статуси вузлів, старт і завершення проєктів -- в OZL_Tree
// (4_World), тут лише опис.

class OZL_TreeCost
{
    string Type   = "";
    int    Amount = 0;

    OZL_TreeCost Copy()
    {
        OZL_TreeCost c = new OZL_TreeCost();
        c.Type   = Type;
        c.Amount = Amount;
        return c;
    }
}

class OZL_TreeItemCost
{
    string Classname = "";
    int    Quantity  = 1;
    string Content   = "";

    OZL_TreeItemCost Copy()
    {
        OZL_TreeItemCost c = new OZL_TreeItemCost();
        c.Classname = Classname;
        c.Quantity  = Quantity;
        c.Content   = Content;
        return c;
    }
}

class OZL_TreeNode
{
    string Id          = "";
    string Name        = "";
    string Description = "";
    string Icon        = "";
    // Лише відображення: рядок на екрані дерева.
    int    Tier        = 1;
    ref array<string> Parents;
    // all | any
    string ParentsMode = "all";
    ref array<ref OZL_TreeCost>     Cost;
    ref array<ref OZL_TreeItemCost> ItemCost;
    // 0 -- миттєво, інакше проєкт на стільки секунд.
    int    ResearchTimeSec = 0;
    ref array<string> RequiredFactions;

    void OZL_TreeNode()
    {
        Parents          = new array<string>();
        Cost             = new array<ref OZL_TreeCost>();
        ItemCost         = new array<ref OZL_TreeItemCost>();
        RequiredFactions = new array<string>();
    }

    OZL_TreeNode Copy()
    {
        OZL_TreeNode c = new OZL_TreeNode();
        c.Id              = Id;
        c.Name            = Name;
        c.Description     = Description;
        c.Icon            = Icon;
        c.Tier            = Tier;
        c.ParentsMode     = ParentsMode;
        c.ResearchTimeSec = ResearchTimeSec;
        int i;
        for (i = 0; i < Parents.Count(); i++)
            c.Parents.Insert(Parents[i]);
        for (i = 0; i < Cost.Count(); i++)
        {
            if (Cost[i])
                c.Cost.Insert(Cost[i].Copy());
        }
        for (i = 0; i < ItemCost.Count(); i++)
        {
            if (ItemCost[i])
                c.ItemCost.Insert(ItemCost[i].Copy());
        }
        for (i = 0; i < RequiredFactions.Count(); i++)
            c.RequiredFactions.Insert(RequiredFactions[i]);
        return c;
    }
}

class OZL_TreeBranch
{
    string Id        = "";
    string Name      = "";
    string Icon      = "";
    int    SortOrder = 0;
    ref array<string> Owners;
    ref array<ref OZL_TreeNode> Nodes;

    void OZL_TreeBranch()
    {
        Owners = new array<string>();
        Nodes  = new array<ref OZL_TreeNode>();
    }

    OZL_TreeBranch Copy()
    {
        OZL_TreeBranch c = new OZL_TreeBranch();
        c.Id        = Id;
        c.Name      = Name;
        c.Icon      = Icon;
        c.SortOrder = SortOrder;
        int i;
        for (i = 0; i < Owners.Count(); i++)
            c.Owners.Insert(Owners[i]);
        for (i = 0; i < Nodes.Count(); i++)
        {
            if (Nodes[i])
                c.Nodes.Insert(Nodes[i].Copy());
        }
        return c;
    }

    bool BelongsTo(string owner)
    {
        if (Owners.Count() == 0)
            return true;
        return Owners.Find(owner) > -1;
    }
}

class OZL_TreeConfig : OZ_ConfigBase
{
    ref array<ref OZL_TreeBranch> Branches;

    void OZL_TreeConfig()
    {
        Branches = new array<ref OZL_TreeBranch>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        Branches.Clear();
    }

    // Структура: гілки з Id, вузли з Id, без дублів, ParentsMode відомий.
    override void Validate(out int warnings)
    {
        warnings = 0;
        array<string> seenBranches = new array<string>();
        array<string> seenNodes    = new array<string>();

        for (int b = Branches.Count() - 1; b >= 0; b--)
        {
            OZL_TreeBranch br = Branches[b];
            if (!br || br.Id == "" || seenBranches.Find(br.Id) > -1)
            {
                OZL_Log.Warn("Tree: a branch with no Id or a duplicate Id, dropped");
                Branches.RemoveOrdered(b);
                warnings++;
                continue;
            }
            seenBranches.Insert(br.Id);

            for (int n = br.Nodes.Count() - 1; n >= 0; n--)
            {
                OZL_TreeNode node = br.Nodes[n];
                string why = "";
                if (!node || node.Id == "")
                    why = "a node with no Id";
                else if (seenNodes.Find(node.Id) > -1)
                    why = "duplicate node Id '" + node.Id + "'";
                else if (node.Name == "")
                    why = "node '" + node.Id + "' has no Name";
                else
                {
                    string pm = node.ParentsMode;
                    pm.ToLower();
                    if (pm != "all" && pm != "any")
                        why = "node '" + node.Id + "': ParentsMode must be all or any";
                    else if (node.ResearchTimeSec < 0 || node.ResearchTimeSec > 2592000)
                        why = "node '" + node.Id + "': ResearchTimeSec outside 0..30 days";
                }

                if (why != "")
                {
                    OZL_Log.Warn("Tree: branch '" + br.Id + "': " + why + ", dropped");
                    br.Nodes.RemoveOrdered(n);
                    warnings++;
                    continue;
                }
                seenNodes.Insert(node.Id);
            }
        }
    }

    // Перевірка проти гри й типів балів, плюс граф: невідомий батько чи
    // цикл -- недосяжний вузол. Вузол, який не пройшов, викидається з живої
    // копії: дерево з вузлом, який неможливо оплатити, гірше за коротше.
    void Check(OZL_PointTypes pointTypes, out int problems)
    {
        problems = 0;
        int b;
        for (b = 0; b < Branches.Count(); b++)
        {
            OZL_TreeBranch br = Branches[b];
            for (int n = br.Nodes.Count() - 1; n >= 0; n--)
            {
                string why = NodeProblem(br.Nodes[n], pointTypes);
                if (why == "")
                    continue;
                OZL_Log.Warn("Tree: node '" + br.Nodes[n].Id + "' dropped: " + why);
                br.Nodes.RemoveOrdered(n);
                problems++;
            }
        }

        array<string> unreachable = new array<string>();
        Unreachable(unreachable);
        for (int u = 0; u < unreachable.Count(); u++)
        {
            OZL_Log.Warn("Tree: node '" + unreachable[u] + "' is unreachable (a cycle or a missing parent)");
            problems++;
        }
    }

    static string NodeProblem(OZL_TreeNode n, OZL_PointTypes pointTypes)
    {
        array<string> seenCost = new array<string>();
        int i;
        for (i = 0; i < n.Cost.Count(); i++)
        {
            OZL_TreeCost c = n.Cost[i];
            if (!c || !pointTypes.Find(c.Type))
                return "unknown point type in Cost";
            if (c.Amount < 0 || c.Amount > 1000000)
                return "Cost.Amount outside 0..1000000";
            if (seenCost.Find(c.Type) > -1)
                return "point type '" + c.Type + "' twice in Cost";
            seenCost.Insert(c.Type);
        }
        for (i = 0; i < n.ItemCost.Count(); i++)
        {
            OZL_TreeItemCost ic = n.ItemCost[i];
            if (!ic || ic.Classname == "" || !OZL_Match.ClassExists(OZL_Match.StripExact(ic.Classname)))
                return "unknown class in ItemCost";
            if (ic.Quantity < 1 || ic.Quantity > 100)
                return "ItemCost.Quantity outside 1..100";
            string err = OZL_Rules.ContentProblem("ItemCost", ic.Classname, ic.Content, pointTypes);
            if (err != "")
                return err;
        }
        return "";
    }

    OZL_TreeNode FindNode(string id)
    {
        for (int b = 0; b < Branches.Count(); b++)
        {
            OZL_TreeBranch br = Branches[b];
            for (int n = 0; n < br.Nodes.Count(); n++)
            {
                if (br.Nodes[n] && br.Nodes[n].Id == id)
                    return br.Nodes[n];
            }
        }
        return null;
    }

    OZL_TreeBranch BranchOf(string nodeId)
    {
        for (int b = 0; b < Branches.Count(); b++)
        {
            OZL_TreeBranch br = Branches[b];
            for (int n = 0; n < br.Nodes.Count(); n++)
            {
                if (br.Nodes[n] && br.Nodes[n].Id == nodeId)
                    return br;
            }
        }
        return null;
    }

    // Гілка -- власникові, вузол -- ще й своїм RequiredFactions.
    bool NodeBelongsTo(OZL_TreeNode node, string owner)
    {
        if (!node)
            return false;
        OZL_TreeBranch br = BranchOf(node.Id);
        if (br && !br.BelongsTo(owner))
            return false;
        if (node.RequiredFactions.Count() > 0 && node.RequiredFactions.Find(owner) < 0)
            return false;
        return true;
    }

    int NodeCount()
    {
        int n = 0;
        for (int b = 0; b < Branches.Count(); b++)
            n += Branches[b].Nodes.Count();
        return n;
    }

    // Досяжність: вузол без батьків досяжний; з батьками -- за ParentsMode.
    // Ітерація до нерухомої точки, циклу нема з чого досягти.
    void Unreachable(out array<string> outIds)
    {
        outIds = new array<string>();
        map<string, bool> reachable = new map<string, bool>();
        bool changed = true;
        while (changed)
        {
            changed = false;
            for (int b = 0; b < Branches.Count(); b++)
            {
                OZL_TreeBranch br = Branches[b];
                for (int n = 0; n < br.Nodes.Count(); n++)
                {
                    OZL_TreeNode node = br.Nodes[n];
                    if (reachable.Contains(node.Id))
                        continue;
                    if (ReachableGiven(node, reachable))
                    {
                        reachable.Set(node.Id, true);
                        changed = true;
                    }
                }
            }
        }
        for (int b2 = 0; b2 < Branches.Count(); b2++)
        {
            OZL_TreeBranch br2 = Branches[b2];
            for (int n2 = 0; n2 < br2.Nodes.Count(); n2++)
            {
                if (!reachable.Contains(br2.Nodes[n2].Id))
                    outIds.Insert(br2.Nodes[n2].Id);
            }
        }
    }

    static bool ReachableGiven(OZL_TreeNode n, map<string, bool> reachable)
    {
        if (n.Parents.Count() == 0)
            return true;
        int okCount = 0;
        for (int i = 0; i < n.Parents.Count(); i++)
        {
            if (reachable.Contains(n.Parents[i]))
                okCount++;
        }
        string pm = n.ParentsMode;
        pm.ToLower();
        if (pm == "any")
            return okCount > 0;
        return okCount == n.Parents.Count();
    }

    OZL_TreeConfig Copy()
    {
        OZL_TreeConfig c = new OZL_TreeConfig();
        c.Version = Version;
        for (int b = 0; b < Branches.Count(); b++)
        {
            if (Branches[b])
                c.Branches.Insert(Branches[b].Copy());
        }
        return c;
    }
}
