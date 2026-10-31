// Зв'язки дерева на канві: перенос renderLines() мокапа (спека §5.3).
//
// Для дитини c з батьками: точка входу ju = u(c) - hu - 12; "смуга"
// lane = u(c) - keep - 14 - 7 x (номер дитини серед дітей свого тиру, що
// мають батьків) -- у кожної дитини своя, тож горизонталі різних дітей не
// лягають одна на одну; ламана (u(p)+hu, v(p)) -> (lane, v(p)) -> (lane, v(c))
// -> (ju, v(c)) на кожного батька і хвіст (ju) -> (u(c) - hu). Колір -- від
// батька: підсвітка (фокус на батькові чи дитині; фокус -- вузол під мишею,
// інакше вибраний), горить (батько досліджений), тьмяний. Батько в тумані чи в
// іншій гілці -- лінії немає. "Будь-який" -- пунктир у ромб з написом АБО;
// "всі" з двома й більше батьками -- квадрат 10 одиниць.
//
// Канва малює в пікселях від свого кута; координати тут -- одиниці вмісту,
// множить скін (OZL_TreeSkin.Line, PxPerUnit). Перемальовується на вибір,
// наведення, нові дані й нову розкладку -- не щокадру.

#ifndef NO_GUI

// Де поставити напис "АБО" біля ромба: точка ромба (одиниці вмісту) і колір.
class OZL_TreeOrMark
{
    float X;
    float Y;
    int   Color;

    void OZL_TreeOrMark(float x, float y, int color)
    {
        X = x;
        Y = y;
        Color = color;
    }
}

class OZL_TreeLines
{
    static void Draw(CanvasWidget canvas, OZL_TreeSkin sk, OZL_TreePlan plan, OZL_BranchView b, string focus, array<ref OZL_TreeOrMark> ors)
    {
        canvas.Clear();
        ors.Clear();
        if (sk.GridStep > 0)
            DrawGrid(canvas, sk, plan.W, plan.H);
        if (!b)
            return;

        float hu = plan.Hu;
        float keep = sk.Keep;
        if (keep <= 0)
            keep = hu;
        array<float> xs = new array<float>();
        array<float> ys = new array<float>();
        int i;
        for (i = 0; i < b.Nodes.Count(); i++)
        {
            OZL_NodeView n = b.Nodes[i];
            if (!n || n.Parents.Count() == 0)
                continue;
            int ci = plan.IndexOf(n.Id);
            if (ci < 0)
                continue;
            float cu = plan.U[ci];
            float cv = plan.V[ci];
            float ju = cu - hu - 12;
            bool nodeHl = focus != "" && focus == n.Id;
            float lane = cu - keep - 14 - 7 * LaneIndex(b, n, plan);

            for (int p = 0; p < n.Parents.Count(); p++)
            {
                string pid = n.Parents[p];
                int pi = plan.IndexOf(pid);
                if (pi < 0)
                    continue;   // батько в тумані або в іншій гілці -- лінії немає
                float pu = plan.U[pi];
                float pv = plan.V[pi];
                bool hl = nodeHl || (focus != "" && focus == pid);
                int color = sk.LineDim;
                if (hl)
                    color = sk.LineHl;
                else if (StatusOf(b, pid) == "completed")
                    color = sk.LineLit;
                float width = sk.LineW;
                if (hl)
                    width = sk.LineWHl;
                xs.Clear();
                ys.Clear();
                Point(plan, pu + hu, pv, xs, ys);
                Point(plan, lane, pv, xs, ys);
                Point(plan, lane, cv, xs, ys);
                Point(plan, ju, cv, xs, ys);
                sk.DrawStroke(canvas, xs, ys, width, color, n.Any, pid + ">" + n.Id);
            }

            int jc = sk.LineDim;
            if (nodeHl)
                jc = sk.LineHl;
            else if (n.Status != "locked")
                jc = sk.LineLit;
            float jw = sk.LineW;
            if (nodeHl)
                jw = sk.LineWHl;
            xs.Clear();
            ys.Clear();
            Point(plan, ju, cv, xs, ys);
            Point(plan, cu - hu, cv, xs, ys);
            sk.DrawStroke(canvas, xs, ys, jw, jc, false, n.Id);

            float jx;
            float jy;
            plan.XY(ju, cv, jx, jy);
            if (n.Any)
            {
                sk.DrawOrKnot(canvas, jx, jy, jc);
                ors.Insert(new OZL_TreeOrMark(jx, jy, jc));
            }
            else if (n.Parents.Count() > 1)
            {
                sk.DrawAllKnot(canvas, jx, jy, jc);
            }
        }
    }

    // Номер вузла серед вузлів свого тиру, що мають батьків, у порядку
    // відповіді (мокап: sib.indexOf(n) над VIS).
    static int LaneIndex(OZL_BranchView b, OZL_NodeView n, OZL_TreePlan plan)
    {
        int tier = OZL_TreePlan.TierOf(n);
        int k = 0;
        for (int i = 0; i < b.Nodes.Count(); i++)
        {
            OZL_NodeView m = b.Nodes[i];
            if (!m || m.Parents.Count() == 0 || plan.IndexOf(m.Id) < 0)
                continue;
            if (OZL_TreePlan.TierOf(m) != tier)
                continue;
            if (m == n)
                return k;
            k++;
        }
        return k;
    }

    static string StatusOf(OZL_BranchView b, string id)
    {
        for (int i = 0; i < b.Nodes.Count(); i++)
        {
            if (b.Nodes[i] && b.Nodes[i].Id == id)
                return b.Nodes[i].Status;
        }
        return "";
    }

    // Сітка паперу: лінії через GridStep від (GridX, GridY) на весь вміст.
    static void DrawGrid(CanvasWidget canvas, OZL_TreeSkin sk, float w, float h)
    {
        float step = sk.GridStep;
        float x = sk.GridX;
        while (x <= w)
        {
            sk.GridLine(canvas, x, 0, x, h);
            x += step;
        }
        float y = sk.GridY;
        while (y <= h)
        {
            sk.GridLine(canvas, 0, y, w, y);
            y += step;
        }
    }

    private static void Point(OZL_TreePlan plan, float u, float v, array<float> xs, array<float> ys)
    {
        float x;
        float y;
        plan.XY(u, v, x, y);
        xs.Insert(x);
        ys.Insert(y);
    }
}

#endif
