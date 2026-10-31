// Розкладка дерева БЕЗ віджетів: перенос layout() і xy() мокапа для однієї
// групи -- вибраної гілки.
//
// Рахується в осях дерева: u -- уздовж (тири), v -- поперек (порядок у тирі);
// потім (u, v) -> (x, y) за напрямком скину. Тири видимих вузлів -- за
// зростанням; ширина групи = Col x найширший тир; порядок у тирі -- за
// середньою позицією вже розставлених батьків (рівні -- за Index, порядком
// конфігу), щоб лінії менше перетиналися. Одиниці -- одиниці вікна 1600x900;
// у пікселі переводить меню.
//
// Туман: якщо в гілці є заглушки прихованих вузлів (Hidden), за останнім
// видимим тиром лишається 170 одиниць під затемнення, і FogU каже, де воно
// починається (мокап: lastU).

#ifndef NO_GUI

class OZL_TreePlan
{
    // Скільки рівнів дерево може мати: захист від конфігу з дикою Tier.
    static const int MAX_TIER = 40;

    // Видимі вузли гілки в порядку відповіді й їхні координати.
    ref array<string> Ids;
    ref array<float>  U;
    ref array<float>  V;
    ref array<float>  X;
    ref array<float>  Y;
    // Рівні, що є серед видимих вузлів, за зростанням.
    ref array<int>    Tiers;
    // id -> місце в Ids. Мапа, а не array.Find: на стенді 2026-09-20
    // array<string>.Find повертав -1 для рядка, що в масиві лежав.
    ref map<string, int> At;

    string Dir   = "down";
    bool   Horiz = false;
    float  W  = 0;    // розмір вмісту дерева, одиниці
    float  H  = 0;
    float  Hu = 0;    // половина вузла вздовж (точки прив'язки ліній)
    bool   HasFog = false;
    float  FogU   = 0;   // де вздовж починається туман

    void OZL_TreePlan()
    {
        Ids   = new array<string>();
        U     = new array<float>();
        V     = new array<float>();
        X     = new array<float>();
        Y     = new array<float>();
        Tiers = new array<int>();
        At    = new map<string, int>();
    }

    static int TierOf(OZL_NodeView n)
    {
        int t = n.Tier;
        if (t < 1)
            t = 1;
        if (t > MAX_TIER)
            t = MAX_TIER;
        return t;
    }

    // viewW / viewH -- видима частина прокрутки, одиниці (мокап віднімає 12
    // під смуги прокрутки -- це робить меню).
    void Build(OZL_TreeSkin sk, OZL_BranchView b, float viewW, float viewH)
    {
        Ids.Clear();
        U.Clear();
        V.Clear();
        X.Clear();
        Y.Clear();
        Tiers.Clear();
        At.Clear();
        Dir   = sk.Dir;
        Horiz = sk.Horizontal();

        array<OZL_NodeView> nodes = new array<OZL_NodeView>();
        int i;
        if (b)
        {
            for (i = 0; i < b.Nodes.Count(); i++)
            {
                OZL_NodeView n = b.Nodes[i];
                if (!n || At.Contains(n.Id))
                    continue;
                At.Set(n.Id, nodes.Count());
                nodes.Insert(n);
                Ids.Insert(n.Id);
                U.Insert(0);
                V.Insert(0);
                X.Insert(0);
                Y.Insert(0);
                int t = TierOf(n);
                if (Tiers.Find(t) < 0)
                    Tiers.Insert(t);
            }
        }
        SortInts(Tiers);

        // Найширший тир -- ширина групи.
        int widest = 1;
        int ti;
        for (ti = 0; ti < Tiers.Count(); ti++)
        {
            int count = 0;
            for (i = 0; i < nodes.Count(); i++)
            {
                if (TierOf(nodes[i]) == Tiers[ti])
                    count++;
            }
            if (count > widest)
                widest = count;
        }
        float used = sk.Col * widest;
        float crossView = viewW;
        float alongView = viewH;
        if (Horiz)
        {
            crossView = viewH;
            alongView = viewW;
        }
        float vTotal = Math.Max(crossView, sk.Side * 2 + used);
        float uTotal = Math.Max(alongView, sk.Top + Tiers.Count() * sk.Row + 40);
        float left = Math.Max(sk.Side, (vTotal - used) / 2 + sk.Shift);

        // Порядок у тирі -- за середнім уже розставлених батьків.
        map<string, float> order = new map<string, float>();
        for (ti = 0; ti < Tiers.Count(); ti++)
        {
            array<int> inTier = new array<int>();
            array<float> keyMean = new array<float>();
            for (i = 0; i < nodes.Count(); i++)
            {
                OZL_NodeView m = nodes[i];
                if (TierOf(m) != Tiers[ti])
                    continue;
                float sum = 0;
                int placed = 0;
                for (int p = 0; p < m.Parents.Count(); p++)
                {
                    float pv;
                    if (m.Parents[p] != "" && order.Find(m.Parents[p], pv))
                    {
                        sum += pv;
                        placed++;
                    }
                }
                float mean = 0;
                if (placed > 0)
                    mean = sum / placed;
                inTier.Insert(i);
                keyMean.Insert(mean);
            }
            // Вставками: тир -- одиниці вузлів. Рівні -- за Index.
            for (int a = 1; a < inTier.Count(); a++)
            {
                int ia = inTier[a];
                float ka = keyMean[a];
                int c = a - 1;
                while (c >= 0 && Before(ka, nodes[ia].Index, keyMean[c], nodes[inTier[c]].Index))
                {
                    inTier[c + 1] = inTier[c];
                    keyMean[c + 1] = keyMean[c];
                    c--;
                }
                inTier[c + 1] = ia;
                keyMean[c + 1] = ka;
            }
            float v0 = left + (used - inTier.Count() * sk.Col) / 2;
            for (i = 0; i < inTier.Count(); i++)
            {
                int at = inTier[i];
                float v = v0 + sk.Col * (i + 0.5);
                order.Set(nodes[at].Id, v);
                U[at] = sk.Top + sk.Row * (ti + 0.5);
                V[at] = v;
            }
        }

        Hu = sk.NodeH / 2;
        if (Horiz)
            Hu = sk.NodeW / 2;
        // Через локальну змінну: складений булевий вираз просто в поле
        // псує купу рушія (скіл, залізні правила).
        bool fog = false;
        if (b && b.Hidden.Count() > 0)
            fog = true;
        HasFog = fog;
        FogU = sk.Top + sk.Row * Tiers.Count() - sk.Row / 2 + Hu + 46;
        if (HasFog)
            uTotal = Math.Max(uTotal, FogU + 170);
        W = vTotal;
        H = uTotal;
        if (Horiz)
        {
            W = uTotal;
            H = vTotal;
        }
        for (i = 0; i < Ids.Count(); i++)
        {
            float x;
            float y;
            XY(U[i], V[i], x, y);
            X[i] = x;
            Y[i] = y;
        }
    }

    // Осі дерева -> вміст: вниз (v, u), вгору (v, H - u), вправо (u, v).
    void XY(float u, float v, out float x, out float y)
    {
        if (Dir == "right")
        {
            x = u;
            y = v;
            return;
        }
        if (Dir == "up")
        {
            x = v;
            y = H - u;
            return;
        }
        x = v;
        y = u;
    }

    int IndexOf(string id)
    {
        int at;
        if (id != "" && At.Find(id, at))
            return at;
        return -1;
    }

    private static bool Before(float ka, int ia, float kb, int ib)
    {
        if (ka < kb)
            return true;
        if (ka > kb)
            return false;
        return ia < ib;
    }

    private static void SortInts(array<int> a)
    {
        for (int i = 1; i < a.Count(); i++)
        {
            int v = a[i];
            int j = i - 1;
            while (j >= 0 && a[j] > v)
            {
                a[j + 1] = a[j];
                j--;
            }
            a[j + 1] = v;
        }
    }
}

#endif
