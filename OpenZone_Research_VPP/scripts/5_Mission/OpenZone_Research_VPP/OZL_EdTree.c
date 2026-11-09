// Дерево в редакторі досліджень: гілка з ЧЕРНЕТКИ, намальована так, як її
// малює вікно гравця -- тим самим планом (OZL_TreePlan), тими самими лініями
// (OZL_TreeLines) і коміркою вузла того самого скіна. Хуки скінів PaintNode
// тут не кличуться: вони беруть OZL_TreeMenu (спека §5), тож комірку
// фарбує Paint нижче -- базова PaintNode без меню.
//
// Дизайн: docs/specs/2026-11-09-research-editor-vpp-design.md, §5.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

class OZL_EdTree
{
    // Розмір вікна дерева скіна в одиницях: TreeScroll його розмітки
    // (ui/OpenZone_Research/ozl_tree_<skin>.json) мінус 12, як у
    // OZL_TreeMenu.PaintTree. План розкладає гілку під цей розмір, тож у
    // редакторі вузли стоять там, де їх побачить гравець. Поля такого в скіні
    // немає -- числа дзеркалять розмітки вікон: змінюєш TreeScroll там, зміни
    // й тут.
    static void ViewSize(string skin, out float w, out float h)
    {
        w = 760;
        h = 818;
        if (skin == "clearsky")
        {
            w = 1576;
            h = 842;
        }
        else if (skin == "duty")
        {
            w = 573;
            h = 597;
        }
        else if (skin == "ecolog")
        {
            w = 1566;
            h = 474;
        }
        else if (skin == "freedom")
        {
            w = 796;
            h = 650;
        }
        else if (skin == "sop")
        {
            w = 1030;
            h = 642;
        }
        w -= 12;
        h -= 12;
    }

    // Гілка чернетки -> те, що вікно гравця отримало б від сервера, коли
    // видно все й стану немає: те саме відображення полів, що в
    // OZL_Tree.View (4_World/OZL_Tree.c, цикл по гілці), без туману й
    // статусів. Index -- порядок у конфігу серед вузлів власника.
    static OZL_BranchView View(OZL_TreeConfig tree, OZL_TreeBranch br, string owner)
    {
        OZL_BranchView bv = new OZL_BranchView();
        if (!br)
            return bv;
        bv.Id = br.Id;
        bv.Name = br.Name;

        int place = 0;
        for (int i = 0; i < br.Nodes.Count(); i++)
        {
            OZL_TreeNode n = br.Nodes[i];
            if (!n || !tree.NodeBelongsTo(n, owner))
                continue;

            OZL_NodeView v = new OZL_NodeView();
            v.Id = n.Id;
            v.Name = n.Name;
            v.Desc = n.Description;
            v.Icon = n.Icon;
            v.Duration = n.ResearchTimeSec;
            v.Index = place;
            place++;
            v.Tier = n.Tier;
            if (v.Tier < 1)
                v.Tier = 1;
            string mode = n.ParentsMode;
            mode.ToLower();
            v.Any = (mode == "any");
            int k;
            for (k = 0; k < n.Parents.Count(); k++)
                v.Parents.Insert(n.Parents[k]);
            for (k = 0; k < n.Cost.Count(); k++)
            {
                if (n.Cost[k])
                    v.Cost.Insert(new OZL_KV(n.Cost[k].Type, n.Cost[k].Amount));
            }
            v.Status = "available";
            bv.Nodes.Insert(v);
        }
        return bv;
    }

    // Комірка вузла: базова OZL_TreeSkin.PaintNode без меню. Назва йде
    // в NodeName (рядок) або в NodeName0/NodeName1 (два рядки по словах --
    // у вікні гравця це робить відкладене перенесення меню); ціна -- рядком
    // у NodePriceText (у вікні гравця -- фішки, вони меню).
    static void Paint(OZL_TreeSkin sk, Widget cell, OZL_NodeView node, string status, bool selected, int number, string price)
    {
        ImageWidget shape = ImageWidget.Cast(cell.FindAnyWidget("NodeShape"));
        if (shape)
        {
            int slot = sk.ShapeOfNode(node, status, selected);
            if (slot >= 0)
                shape.SetImage(slot);
            shape.SetColor(sk.ShapeColorOf(status));
        }
        Widget ring = cell.FindAnyWidget("NodeRing");
        if (ring)
            ring.Show(sk.RingShown(status, selected));
        Widget sel = cell.FindAnyWidget("NodeSel");
        if (sel)
            sel.Show(selected);

        ImageWidget icon = ImageWidget.Cast(cell.FindAnyWidget("NodeIcon"));
        if (icon)
        {
            if (node.Icon != "" && icon.LoadImageFile(0, node.Icon))
            {
                icon.SetImage(0);
                icon.SetColor(sk.IconColorOf(status));
                icon.Show(true);
            }
            else
            {
                icon.Show(false);
            }
        }

        PutName(cell.FindAnyWidget("NodeName"), sk.DataText(sk.NodeNameText(node.Name)), sk.NameColorOf(status));

        ImageWidget mark = ImageWidget.Cast(cell.FindAnyWidget("NodeMark"));
        if (mark)
        {
            int ms = sk.MarkOf(status);
            if (ms >= 0)
            {
                mark.SetImage(ms);
                mark.SetColor(sk.MarkColorOf(status));
                mark.Show(true);
            }
            else
            {
                mark.Show(false);
            }
        }
        TextWidget markText = TextWidget.Cast(cell.FindAnyWidget("NodeMarkText"));
        if (markText)
        {
            string mt = sk.MarkTextOf(status);
            markText.SetText(mt);
            markText.SetColor(sk.MarkColorOf(status));
            markText.Show(mt != "");
        }

        TextWidget num = TextWidget.Cast(cell.FindAnyWidget("NodeNum"));
        if (num)
            num.SetText(OZL_Text.Two(number));

        TextWidget pt = TextWidget.Cast(cell.FindAnyWidget("NodePriceText"));
        if (pt)
        {
            pt.SetText(price);
            pt.SetColor(sk.PriceColorOf(status));
            pt.Show(price != "");
        }
        Widget bar = cell.FindAnyWidget("NodeBar");
        if (bar)
            bar.Show(false);
    }

    // Назва у віджет назви: рядок -- як є; контейнер NodeName0/NodeName1 --
    // по словах на два рядки, розрив ближче до середини.
    static void PutName(Widget w, string text, int color)
    {
        if (!w)
            return;
        TextWidget t = TextWidget.Cast(w);
        if (t)
        {
            t.SetText(text);
            if (color != 0)
                t.SetColor(color);
            return;
        }

        TextWidget l0 = TextWidget.Cast(w.FindAnyWidget("NodeName0"));
        TextWidget l1 = TextWidget.Cast(w.FindAnyWidget("NodeName1"));
        string a = text;
        string b = "";
        int mid = text.Length() / 2;
        int best = -1;
        for (int i = 0; i < text.Length(); i++)
        {
            if (text.Get(i) != " ")
                continue;
            if (best < 0 || Math.AbsInt(i - mid) < Math.AbsInt(best - mid))
                best = i;
        }
        if (best > 0 && l1)
        {
            a = text.Substring(0, best);
            b = text.Substring(best + 1, text.Length() - best - 1);
        }
        if (l0)
        {
            l0.SetText(a);
            if (color != 0)
                l0.SetColor(color);
            l0.Show(true);
        }
        if (l1)
        {
            l1.SetText(b);
            if (color != 0)
                l1.SetColor(color);
            l1.Show(b != "");
        }
    }

    // Картинки станів у слоти, як OZL_TreeMenu.LoadSlots: форма й мітка.
    static void LoadSlots(OZL_TreeSkin sk, Widget cell)
    {
        int i;
        ImageWidget shape = ImageWidget.Cast(cell.FindAnyWidget("NodeShape"));
        if (shape)
        {
            for (i = 0; i < sk.Shapes.Count() && i < 8; i++)
                shape.LoadImageFile(i, sk.Shapes[i]);
        }
        ImageWidget mark = ImageWidget.Cast(cell.FindAnyWidget("NodeMark"));
        if (mark)
        {
            for (i = 0; i < sk.Marks.Count() && i < 8; i++)
                mark.LoadImageFile(i, sk.Marks[i]);
        }
    }

    // ------------------------------------------------- поля інспектора

    // "bio:3, anomaly:2" <-> ціна вузла.
    static string CostText(OZL_TreeNode n)
    {
        string s = "";
        for (int i = 0; i < n.Cost.Count(); i++)
        {
            if (!n.Cost[i])
                continue;
            if (s != "")
                s += ", ";
            s += n.Cost[i].Type + ":" + n.Cost[i].Amount.ToString();
        }
        return s;
    }

    static void ParseCost(string text, OZL_TreeNode n)
    {
        n.Cost.Clear();
        array<string> parts = new array<string>();
        text.Split(",", parts);
        for (int i = 0; i < parts.Count(); i++)
        {
            string p = parts[i].Trim();
            if (p == "")
                continue;
            OZL_TreeCost c = new OZL_TreeCost();
            int colon = p.IndexOf(":");
            if (colon < 0)
            {
                c.Type = p;
                c.Amount = 0;
            }
            else
            {
                c.Type = p.Substring(0, colon).Trim();
                c.Amount = p.Substring(colon + 1, p.Length() - colon - 1).Trim().ToInt();
            }
            if (c.Type != "")
                n.Cost.Insert(c);
        }
    }

    // "Class:2, Other:1" <-> предмети вузла; кількість за замовчуванням 1.
    static string ItemsText(OZL_TreeNode n)
    {
        string s = "";
        for (int i = 0; i < n.ItemCost.Count(); i++)
        {
            if (!n.ItemCost[i])
                continue;
            if (s != "")
                s += ", ";
            s += n.ItemCost[i].Classname + ":" + n.ItemCost[i].Quantity.ToString();
        }
        return s;
    }

    static void ParseItems(string text, OZL_TreeNode n)
    {
        n.ItemCost.Clear();
        array<string> parts = new array<string>();
        text.Split(",", parts);
        for (int i = 0; i < parts.Count(); i++)
        {
            string p = parts[i].Trim();
            if (p == "")
                continue;
            OZL_TreeItemCost c = new OZL_TreeItemCost();
            int colon = p.IndexOf(":");
            if (colon < 0)
            {
                c.Classname = p;
                c.Quantity = 1;
            }
            else
            {
                c.Classname = p.Substring(0, colon).Trim();
                c.Quantity = p.Substring(colon + 1, p.Length() - colon - 1).Trim().ToInt();
            }
            if (c.Classname != "")
                n.ItemCost.Insert(c);
        }
    }

    static string ParentsText(OZL_TreeNode n)
    {
        string s = "";
        for (int i = 0; i < n.Parents.Count(); i++)
        {
            if (s != "")
                s += ", ";
            s += n.Parents[i];
        }
        return s;
    }

    static void ParseParents(string text, OZL_TreeNode n)
    {
        n.Parents.Clear();
        array<string> parts = new array<string>();
        text.Split(",", parts);
        for (int i = 0; i < parts.Count(); i++)
        {
            string p = parts[i].Trim();
            if (p != "")
                n.Parents.Insert(p);
        }
    }

    // Ціна рядком для комірки: "3 Біологія + 2 Аномалії".
    static string PriceText(OZL_TreeNode n, OZL_PointTypes pts)
    {
        string s = "";
        for (int i = 0; i < n.Cost.Count(); i++)
        {
            if (!n.Cost[i])
                continue;
            if (s != "")
                s += " + ";
            string nm = n.Cost[i].Type;
            if (pts)
                nm = pts.NameOf(n.Cost[i].Type);
            s += n.Cost[i].Amount.ToString() + " " + nm;
        }
        return s;
    }

    // Перейменувати посилання на вузол у батьках усіх вузлів дерева
    // (батьки з іншої гілки законні, спека §5).
    static void RenameRefs(OZL_TreeConfig tree, string from, string to)
    {
        if (from == "" || from == to)
            return;
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            for (int n = 0; n < br.Nodes.Count(); n++)
            {
                OZL_TreeNode node = br.Nodes[n];
                for (int p = 0; p < node.Parents.Count(); p++)
                {
                    if (node.Parents[p] == from)
                        node.Parents.Set(p, to);
                }
            }
        }
    }

    // Прибрати вузол і всі посилання на нього.
    static void DropRefs(OZL_TreeConfig tree, string id)
    {
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            for (int n = 0; n < br.Nodes.Count(); n++)
            {
                OZL_TreeNode node = br.Nodes[n];
                for (int p = node.Parents.Count() - 1; p >= 0; p--)
                {
                    if (node.Parents[p] == id)
                        node.Parents.RemoveOrdered(p);
                }
            }
        }
    }

    // Скільки вузлів дерева мають цей Id (дубль -- 2 і більше).
    static int CountId(OZL_TreeConfig tree, string id)
    {
        int n = 0;
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            for (int i = 0; i < br.Nodes.Count(); i++)
            {
                if (br.Nodes[i] && br.Nodes[i].Id == id)
                    n++;
            }
        }
        return n;
    }

    // Вільний Id для нового вузла: <база>, <база>_2, ...
    static string FreeId(OZL_TreeConfig tree, string base)
    {
        string id = base;
        int n = 1;
        while (tree.FindNode(id))
        {
            n++;
            id = base + "_" + n.ToString();
        }
        return id;
    }

    // ------------------------------------------------- гілки й зв'язки

    static OZL_TreeBranch FindBranch(OZL_TreeConfig tree, string id)
    {
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            if (tree.Branches[b] && tree.Branches[b].Id == id)
                return tree.Branches[b];
        }
        return null;
    }

    static string FreeBranchId(OZL_TreeConfig tree, string base)
    {
        string id = base;
        int n = 1;
        while (FindBranch(tree, id))
        {
            n++;
            id = base + "_" + n.ToString();
        }
        return id;
    }

    // "a, b" <-> список рядків (власники гілки).
    static string ListText(array<string> list)
    {
        string s = "";
        for (int i = 0; i < list.Count(); i++)
        {
            if (s != "")
                s += ", ";
            s += list[i];
        }
        return s;
    }

    static void ParseList(string text, array<string> into)
    {
        into.Clear();
        array<string> parts = new array<string>();
        text.Split(",", parts);
        for (int i = 0; i < parts.Count(); i++)
        {
            string p = parts[i].Trim();
            if (p != "")
                into.Insert(p);
        }
    }

    // Чи залежить вузол (крізь батьків, на будь-яку глибину) від вузла id:
    // зв'язок id -> node у зворотний бік замкнув би коло, і сервер оголосив
    // би обидва недосяжними. Ліміт глибини -- на випадок кола, що вже є.
    static bool DependsOn(OZL_TreeConfig tree, OZL_TreeNode node, string id, int guard)
    {
        if (!node || guard > 64)
            return false;
        for (int i = 0; i < node.Parents.Count(); i++)
        {
            if (node.Parents[i] == id)
                return true;
            if (DependsOn(tree, tree.FindNode(node.Parents[i]), id, guard + 1))
                return true;
        }
        return false;
    }

    // ------------------------------------------------- ціна фішками

    // Ціна в комірці фішками, як OZL_TreeMenu.PaintPrice: рядок скіна
    // price_chip на тип балів (крапка кольору типу й число) і хвіст
    // "+N предм.". Повертає контейнер NodePrice, якщо фішки є, -- його
    // розкладає FlowChips кадром пізніше, коли тексти мають ширину; null --
    // скін без контейнера чи шаблону, тоді ціна лишається рядком.
    static Widget PaintChips(OZL_TreeSkin sk, Widget cell, OZL_TreeNode n, OZL_PointTypes pts, string status)
    {
        Widget box = cell.FindAnyWidget("NodePrice");
        if (!box)
            return null;
        Widget child = box.GetChildren();
        while (child)
        {
            Widget next = child.GetSibling();
            child.Unlink();
            child = next;
        }

        int color = sk.PriceColorOf(status);
        string path = sk.RowLayout("price_chip");
        int i;
        int made = 0;
        for (i = 0; i < n.Cost.Count(); i++)
        {
            OZL_TreeCost c = n.Cost[i];
            if (!c)
                continue;
            Widget chip = GetGame().GetWorkspace().CreateWidgets(path, box);
            if (!chip)
            {
                box.Show(false);
                return null;
            }
            OZL_TreeMenu.IgnorePointer(chip, null);
            Widget dot = chip.FindAnyWidget("PriceChip");
            if (dot && pts)
            {
                OZL_PointType pt = pts.Find(c.Type);
                if (pt)
                    dot.SetColor(OZL_PointTypes.ColorArgb(pt.Color));
            }
            TextWidget amount = TextWidget.Cast(chip.FindAnyWidget("PriceText"));
            if (amount)
            {
                amount.SetText(c.Amount.ToString());
                amount.SetColor(color);
            }
            made++;
        }

        int qty = 0;
        for (i = 0; i < n.ItemCost.Count(); i++)
        {
            if (n.ItemCost[i])
                qty += n.ItemCost[i].Quantity;
        }
        if (qty > 0)
        {
            Widget more = GetGame().GetWorkspace().CreateWidgets(path, box);
            if (more)
            {
                OZL_TreeMenu.IgnorePointer(more, null);
                Widget moreDot = more.FindAnyWidget("PriceChip");
                if (moreDot)
                    moreDot.Show(false);
                TextWidget moreText = TextWidget.Cast(more.FindAnyWidget("PriceText"));
                if (moreText)
                {
                    moreText.SetText("+" + qty.ToString() + " " + OZL_Text.Words("STR_OZL_TREE_ITEMS_TAIL"));
                    moreText.SetColor(color);
                }
                made++;
            }
        }

        box.Show(made > 0);
        if (made == 0)
            return null;
        Widget plain = cell.FindAnyWidget("NodePriceText");
        if (plain)
            plain.Show(false);
        return box;
    }

    // Фішки рядком зліва направо, як OZL_TreeMenu.RunFlows без переносу:
    // ширина фішки -- від її лівого краю до правого краю тексту, плюс 6
    // одиниць. Екологи й ЧН потім ставлять рядок по центру під вузлом (їхні
    // OZL_TreeSkin_Ecolog.LayPrice і OZL_TreeSkin_Sop.CenterPrice -- гачки,
    // яким потрібне меню), екологи ще й тягнуть хвіст "+N предм." за
    // попереднім числом через 3,2 одиниці, без квадратика: те саме тут.
    // false -- тексти ще не розкладені (ширина 0), спитати кадром пізніше;
    // force -- розкласти, як є.
    static bool FlowChips(OZL_TreeSkin sk, Widget box, float k, bool force)
    {
        Widget item = box.GetChildren();
        int pw;
        int ph;
        if (!force)
        {
            while (item)
            {
                TextWidget probe = TextWidget.Cast(item.FindAnyWidget("PriceText"));
                if (probe && item.IsVisible())
                {
                    probe.GetTextSize(pw, ph);
                    if (pw <= 0)
                        return false;
                }
                item = item.GetSibling();
            }
        }

        bool ecolog = (sk && sk.Id == "ecolog");
        bool centre = (ecolog || (sk && sk.Id == "sop"));
        float x = 0;
        float end = 0;
        int placed = 0;
        item = box.GetChildren();
        while (item)
        {
            if (item.IsVisible())
            {
                float lead = 0;
                float tw = 0;
                TextWidget t = TextWidget.Cast(item.FindAnyWidget("PriceText"));
                if (t)
                {
                    float ix;
                    float iy;
                    item.GetScreenPos(ix, iy);
                    float tx;
                    float ty;
                    t.GetScreenPos(tx, ty);
                    t.GetTextSize(pw, ph);
                    lead = (tx - ix) / k;
                    tw = pw / k;
                }
                Widget dot = item.FindAnyWidget("PriceChip");
                bool tail = false;
                if (ecolog && placed > 0 && dot && !dot.IsVisible())
                    tail = true;
                if (tail)
                    x = end + 3.2 - lead;
                item.SetPos(x * k, 0);
                end = x + lead + tw;
                x = end + 6;
                placed++;
            }
            item = item.GetSibling();
        }

        if (centre && placed > 0)
        {
            float bx;
            float by;
            box.GetPos(bx, by);
            box.SetPos((sk.AnchorX - end / 2) * k, by);
        }
        return true;
    }

    // ------------------------------------------------- як бачить гравець

    // Серверна секунда перегляду: вікно рахує залишок проєкту як EndSec мінус
    // вона, тож число довільне, важить лише різниця.
    static const int PREVIEW_NOW = 1000000;

    // Демо-стан фракції для перегляду. 0 -- нова: пул порожній, нічого не
    // зроблено (так дерево бачить фракція першого дня). 1 -- з балами: пул
    // покриває ціну всіх вузлів власника. 2 -- у роботі: з балами, корені
    // виконано, перший вузол, що став доступним, -- проєкт із половиною часу
    // (не менше хвилини).
    static OZL_FactionState DemoState(OZL_TreeConfig tree, string owner, int demo, int now)
    {
        OZL_FactionState st = new OZL_FactionState();
        if (demo <= 0)
            return st;

        map<string, int> need = new map<string, int>();
        array<OZL_TreeNode> mine = new array<OZL_TreeNode>();
        int i;
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            if (!br || !br.BelongsTo(owner))
                continue;
            for (int n = 0; n < br.Nodes.Count(); n++)
            {
                OZL_TreeNode node = br.Nodes[n];
                if (!node || !tree.NodeBelongsTo(node, owner))
                    continue;
                mine.Insert(node);
                for (i = 0; i < node.Cost.Count(); i++)
                {
                    OZL_TreeCost c = node.Cost[i];
                    if (!c)
                        continue;
                    int have = 0;
                    need.Find(c.Type, have);
                    need.Set(c.Type, have + c.Amount);
                }
            }
        }
        for (i = 0; i < need.Count(); i++)
            st.SetPoints(need.GetKey(i), need.GetElement(i));
        if (demo < 2)
            return st;

        for (i = 0; i < mine.Count(); i++)
        {
            if (mine[i].Parents.Count() == 0)
                st.CompletedNodes.Insert(mine[i].Id);
        }
        for (i = 0; i < mine.Count(); i++)
        {
            OZL_TreeNode next = mine[i];
            if (st.IsCompleted(next.Id) || !OZL_Tree.ParentsSatisfied(st, next))
                continue;
            OZL_Project pr = new OZL_Project();
            pr.NodeId = next.Id;
            int half = next.ResearchTimeSec / 2;
            if (half < 60)
                half = 60;
            pr.EndSec = now + half;
            st.ActiveProjects.Insert(pr);
            break;
        }
        return st;
    }

    // Те, що вікно дерева гравця отримало б від сервера, якби файли вже
    // були такими, як чернетка, а фракція -- у демо-стані: та сама
    // OZL_Tree.Fill, що складає відповідь сервера (туман, заглушки,
    // статуси), без термінала поруч і без права витрачати.
    static OZL_TreeView PlayerView(OZL_TreeConfig tree, OZL_Owners owners, OZL_PointTypes pts, OZL_Settings se, string owner, int demo)
    {
        OZL_TreeView v = new OZL_TreeView();
        v.Owner = owner;
        OZ_IdentityService id = OZ_Identity.Get();
        v.OwnerName = id.FactionName(owner);
        if (v.OwnerName == "")
            v.OwnerName = owner;
        v.OwnerColor = id.FactionColor(owner, 255);
        v.Skin = owners.SkinOf(owner);
        v.MaySpend = false;
        v.Now = PREVIEW_NOW;
        OZL_FactionState st = DemoState(tree, owner, demo, v.Now);
        OZL_Tree.Fill(v, owner, st, pts, tree, se.TreeVisibilityDepth, null, null);
        return v;
    }
}

#endif
#endif
#endif
