// Вікно дерева однієї фракції ("скин"): дані й гачки.
//
// Меню одне на всі сім вікон (OZL_TreeMenu): воно знаходить віджети за
// ролями (TreeScroll, CardName, BtnResearch...), розкладає дерево
// (OZL_TreePlan), малює зв'язки (OZL_TreeLines) і заповнює картку. Чим вікна
// відрізняються -- розкладкою, формою вузла, напрямком дерева, палітрою,
// мітками, -- тим і є цей клас: поля з даними і віртуальні гачки, які
// працюють і без перекриття. Скин перекриває лише те, що в нього інакше.
// Повний опис ролей і гачків для авторів скинів -- source/ui/SKINS.md.
//
// Сервер шле вже розв'язаний id (OZL_TreeView.Skin), один із семи. Id, якого
// клієнт не знає, -- помилка в лозі й тетрадь neutral (захист, а не режим).
// Вікно, чия розкладка ще не існує (його задача не зроблена), теж падає на
// neutral -- це вирішує меню, бо лише воно бачить, чи розкладка дала віджети.
//
// Одиниці: усе в одиницях вікна 1600x900 (одиниці розкладки). Пікселі
// канви рахує меню; гачки малювання отримують одиниці і PxPerUnit.

#ifndef NO_GUI

class OZL_TreeSkin
{
    static const string LAYOUTS = "OpenZone_Research/gui/layouts/";

    // --- що це за вікно
    string Id = "neutral";
    // Розкладка вікна (корінь TreeWindow) і вузла (корінь NodeCell). Шаблони
    // рядків -- LAYOUTS + RowPrefix + назва рядка (ozl_neutral_pool_row).
    string WindowLayout = "";
    string NodeLayout   = "";
    string RowPrefix    = "";

    // --- геометрія дерева (мокап SKINS.<skin>, спека §3)
    // Куди росте дерево: "down", "up" або "right".
    string Dir   = "down";
    float  NodeW = 176;   // розмір форми вузла (точки прив'язки ліній)
    float  NodeH = 64;
    float  Keep  = 0;     // скільки місця тримати під підписом; 0 -- половина вузла
    float  Row   = 140;   // крок тирів уздовж
    float  Col   = 210;   // крок вузлів поперек
    float  Top   = 100;   // відступ до першого тиру (місце під шапку)
    float  Side  = 40;    // поля поперек
    float  Shift = 0;     // зсув групи поперек (clearsky -170)
    // Центр форми всередині NodeCell: меню ставить комірку в (x - AnchorX,
    // y - AnchorY), де (x, y) -- точка вузла з плану.
    float  AnchorX = 88;
    float  AnchorY = 32;

    // --- палітра (ARGB; CSS мокапа --txt --dim --acc --ok --bad --line-dim --lcd --fog)
    int Txt      = ARGB(255, 185, 214, 162);
    int Dim      = ARGB(255,  95, 122,  85);
    int Acc      = ARGB(255, 228, 163,  60);
    int Ok       = ARGB(255, 143, 211, 106);
    int Bad      = ARGB(255, 226,  99,  74);
    int LineDim  = ARGB(153,  95, 122,  85);
    int LineLit  = ARGB(255, 185, 214, 162);   // зазвичай = Txt
    int LineHl   = ARGB(255, 228, 163,  60);   // зазвичай = Acc
    int Lcd      = ARGB(255,  15,  26,  18);   // тло дерева: заливка ромба "АБО"
    int FogColor = ARGB(255,  14,  24,  17);

    // --- зв'язки
    string LineStyle = "plain";   // "plain" або "sketch" (від руки, бандити)
    float  LineW     = 2;         // товщина звичайна / підсвічена, одиниці
    float  LineWHl   = 2.5;
    float  DashOn    = 6;         // пунктир "будь-якого": 6 є, 5 нема
    float  DashOff   = 5;
    // Сітка паперу, що прокручується разом із деревом (мокап: .content .bg,
    // --grid і --grid-step). 0 -- без сітки.
    float  GridStep  = 0;
    int    GridColor = 0;
    float  GridX     = 0;   // зсув першої лінії
    float  GridY     = 0;
    float  GridW     = 1;   // товщина лінії, одиниці

    // --- вузол
    // Картинки форми вузла (NodeShape) за слотами 0..7; ShapeOf каже, який
    // слот показати. Порожньо -- лишається image0 із розкладки.
    ref array<string> Shapes;
    // Слот форми під мишею (-1 -- не міняти).
    int ShapeHover = -1;
    // Картинки мітки (NodeMark) за слотами; MarkOf каже слот (-1 -- нема).
    ref array<string> Marks;
    // Кольори форми за статусом; нема в таблиці -- білий.
    ref map<string, int> ShapeColors;

    // --- картка
    int SegOn  = 0;   // сегмент смуги проєкту (CardSeg0..19): зроблено / ні;
    int SegOff = 0;   // 0 -- взяти Acc / LineDim
    // Скільки одиниць поля між краєм підказки і текстом.
    float TipPadX = 9;

    // Пікселів на одиницю -- меню ставить перед кожним малюванням канви.
    float PxPerUnit = 1;

    void OZL_TreeSkin()
    {
        Shapes      = new array<string>();
        Marks       = new array<string>();
        ShapeColors = new map<string, int>();
    }

    // Назви розкладок за id, як їх пише генератор: ozl_tree_<id>,
    // ozl_node_<id>, ozl_<id>_<рядок>.
    protected void Named(string id)
    {
        Id           = id;
        WindowLayout = LAYOUTS + "ozl_tree_" + id + ".layout";
        NodeLayout   = LAYOUTS + "ozl_node_" + id + ".layout";
        RowPrefix    = "ozl_" + id + "_";
    }

    string RowLayout(string row)
    {
        return LAYOUTS + RowPrefix + row + ".layout";
    }

    bool Horizontal()
    {
        return Dir == "right";
    }

    // ------------------------------------------------------------------
    // Гачки. Кожен працює й так; скин перекриває тільки своє.
    // ------------------------------------------------------------------

    // Слот NodeShape для статусу (locked / short / available / researching /
    // completed) і вибраності; -1 -- не чіпати картинку.
    int ShapeOf(string status, bool selected)
    {
        if (Shapes.Count() == 0)
            return -1;
        return 0;
    }

    int ShapeColorOf(string status)
    {
        int c;
        if (ShapeColors.Find(status, c))
            return c;
        return ARGB(255, 255, 255, 255);
    }

    // Обведення доступного (NodeRing) і вибраного (NodeSel).
    bool RingShown(string status, bool selected)
    {
        return status == "available" && !selected;
    }

    int NameColorOf(string status)
    {
        if (status == "locked")
            return Dim;
        return Txt;
    }

    int PriceColorOf(string status)
    {
        if (status == "short")
            return Bad;
        if (status == "available" || status == "researching")
            return Acc;
        if (status == "completed")
            return Ok;
        return Dim;
    }

    int IconColorOf(string status)
    {
        if (status == "available" || status == "researching")
            return Acc;
        if (status == "completed")
            return Ok;
        return Dim;
    }

    // Колір слова статусу в картці (мокап stCol).
    int StatusColorOf(string status)
    {
        if (status == "short")
            return Bad;
        if (status == "available" || status == "researching")
            return Acc;
        if (status == "completed")
            return Ok;
        return Dim;
    }

    // Мітка вузла: слот картинки в NodeMark (-1 -- нема) і текст у
    // NodeMarkText ("" -- нема). Типово: замок / галка / крапка ozl_common,
    // якщо скин поклав їх у Marks у порядку lock, check, dot.
    int MarkOf(string status)
    {
        if (Marks.Count() < 3)
            return -1;
        if (status == "locked")
            return 0;
        if (status == "completed")
            return 1;
        if (status == "researching")
            return 2;
        return -1;
    }

    string MarkTextOf(string status)
    {
        return "";
    }

    int MarkColorOf(string status)
    {
        if (status == "completed")
            return Ok;
        if (status == "researching")
            return Acc;
        return Dim;
    }

    // Ключ слова статусу і саме слово (картка, підказка, реєстр).
    static string StatusKey(string status)
    {
        if (status == "completed")
            return "STR_OZL_TREE_COMPLETED";
        if (status == "researching")
            return "STR_OZL_TREE_RESEARCHING";
        if (status == "available")
            return "STR_OZL_TREE_AVAILABLE";
        if (status == "short")
            return "STR_OZL_TREE_SHORT";
        return "STR_OZL_TREE_LOCKED";
    }

    string StatusText(string status)
    {
        return OZL_Text.Words(StatusKey(status));
    }

    // Заголовок розділу картки (Опис, Вартість, Матеріали, Тривалість,
    // Відкриває). Папір дописує ":", Чисте небо ставить "// " попереду, СОП
    // і Долг пишуть великими -- кожен у своєму класі.
    string SectionText(string key)
    {
        return OZL_Text.Words(key);
    }

    // Назва вузла в комірці (СОП і Долг -- великими).
    string NodeNameText(string name)
    {
        return name;
    }

    // Підпис тиру: "I", "II"...; дерево вправо пише "тир I".
    string TierText(int tier)
    {
        if (Horizontal())
            return OZL_Text.Words("STR_OZL_TREE_TIER") + " " + OZL_Text.Roman(tier);
        return OZL_Text.Roman(tier);
    }

    // Вузол цілком: форма, обведення, значок, назва, ціна, смуга, мітка,
    // номер. Ціну й смугу кладе меню (вони спільні для всіх), решту -- тут.
    void PaintNode(OZL_TreeMenu menu, Widget cell, OZL_NodeView node, string status, bool selected)
    {
        ImageWidget shape = ImageWidget.Cast(cell.FindAnyWidget("NodeShape"));
        if (shape)
        {
            int slot = ShapeOf(status, selected);
            if (slot >= 0)
                shape.SetImage(slot);
            shape.SetColor(ShapeColorOf(status));
        }
        Widget ring = cell.FindAnyWidget("NodeRing");
        if (ring)
            ring.Show(RingShown(status, selected));
        Widget sel = cell.FindAnyWidget("NodeSel");
        if (sel)
            sel.Show(selected);

        ImageWidget icon = ImageWidget.Cast(cell.FindAnyWidget("NodeIcon"));
        if (icon)
        {
            if (node.Icon != "" && icon.LoadImageFile(0, node.Icon))
            {
                icon.SetImage(0);
                icon.SetColor(IconColorOf(status));
                icon.Show(true);
            }
            else
            {
                icon.Show(false);
            }
        }

        // Напис або контейнер рядків NodeName0, NodeName1 (перенос по словах).
        Widget name = cell.FindAnyWidget("NodeName");
        if (name)
            menu.PutText(name, NodeNameText(node.Name), NameColorOf(status));

        ImageWidget mark = ImageWidget.Cast(cell.FindAnyWidget("NodeMark"));
        if (mark)
        {
            int ms = MarkOf(status);
            if (ms >= 0)
            {
                mark.SetImage(ms);
                mark.SetColor(MarkColorOf(status));
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
            string mt = MarkTextOf(status);
            markText.SetText(mt);
            markText.SetColor(MarkColorOf(status));
            markText.Show(mt != "");
        }

        TextWidget num = TextWidget.Cast(cell.FindAnyWidget("NodeNum"));
        if (num)
            num.SetText(OZL_Text.Two(node.Index + 1));
    }

    // Рядок пулу: назва лінії, скільки є, і чим заповнити сегменти
    // (need -- найбільша ціна одного вузла по цій лінії).
    void PaintPoolRow(OZL_TreeMenu menu, Widget row, string line, int have, int need, int color)
    {
        TextWidget name = TextWidget.Cast(row.FindAnyWidget("PoolName"));
        if (name)
        {
            name.SetText(menu.PointName(line));
            if (have > 0)
                name.SetColor(Txt);
            else
                name.SetColor(Dim);
        }
        TextWidget value = TextWidget.Cast(row.FindAnyWidget("PoolValue"));
        if (value)
        {
            value.SetText(have.ToString());
            if (have > 0)
                value.SetColor(Txt);
            else
                value.SetColor(Dim);
        }
        Widget chip = row.FindAnyWidget("PoolChip");
        if (chip)
            chip.SetColor(color);
        if (need < 1)
            need = 10;
        // Крізь float: int / int в Enforce -- ціле ділення.
        float frac = have;
        frac = frac / need;
        if (frac > 1)
            frac = 1;
        int on = Math.Round(10 * frac);
        for (int i = 0; i < 10; i++)
        {
            Widget seg = row.FindAnyWidget("PoolSeg" + i.ToString());
            if (!seg)
                break;
            if (i < on)
                seg.SetColor(Acc);
            else
                seg.SetColor(LineDim);
        }
    }

    // Рядок вартості картки (лінія чи матеріал): назва, текст "є / треба" чи
    // "треба", вирок 1 -- вистачає (або заплачено), -1 -- ні, 0 -- невідомо
    // (Have = -1: без вироку). Смужку CostBar/CostBarFill заповнює меню.
    void PaintCostRow(OZL_TreeMenu menu, Widget row, string label, string text, int verdict)
    {
        TextWidget name = TextWidget.Cast(row.FindAnyWidget("CostName"));
        if (name)
        {
            name.SetText(label);
            name.SetColor(Txt);
        }
        int color = Txt;
        if (verdict > 0)
            color = Ok;
        else if (verdict < 0)
            color = Bad;
        TextWidget value = TextWidget.Cast(row.FindAnyWidget("CostValue"));
        if (value)
        {
            value.SetText(text);
            value.SetColor(color);
        }
        Widget fill = row.FindAnyWidget("CostBarFill");
        if (fill)
            fill.SetColor(color);
    }

    // Печатка картки (CardStamp/CardStampImg, Долг): картинка для статусу,
    // "" -- печатки нема.
    string StampOf(string status)
    {
        return "";
    }

    // Кнопка "Дослідити": доступна чи ні. Під мишею меню показує
    // BtnResearchHover, якщо такий є.
    void PaintButton(OZL_TreeMenu menu, Widget btn, bool enabled)
    {
        TextWidget text = TextWidget.Cast(menu.Role("BtnResearchText"));
        if (text)
        {
            if (enabled)
                text.SetColor(Acc);
            else
                text.SetColor(Dim);
        }
    }

    // ------------------------------------------------------------------
    // Малювання на канві. Координати -- одиниці вмісту дерева; Px() множить.
    // ------------------------------------------------------------------

    protected void Line(CanvasWidget canvas, float x1, float y1, float x2, float y2, float width, int color)
    {
        float k = PxPerUnit;
        canvas.DrawLine(x1 * k, y1 * k, x2 * k, y2 * k, width * k, color);
    }

    // Один прямий відрізок: суцільний або пунктир 6/5 (фаза -- з `phase`,
    // одиниці від початку ламаної; повертає фазу в кінці відрізка, щоб
    // пунктир ішов ламаною без розривів).
    float DrawSegment(CanvasWidget canvas, float x1, float y1, float x2, float y2, float width, int color, bool dashed, float phase)
    {
        float dx = x2 - x1;
        float dy = y2 - y1;
        float len = Math.Sqrt(dx * dx + dy * dy);
        if (!dashed)
        {
            if (len > 0.01)
                Line(canvas, x1, y1, x2, y2, width, color);
            return phase + len;
        }
        if (len < 0.01)
            return phase;
        float period = DashOn + DashOff;
        float ux = dx / len;
        float uy = dy / len;
        float t = 0;
        while (t < len)
        {
            float inPeriod = phase + t;
            inPeriod = inPeriod - Math.Floor(inPeriod / period) * period;
            float piece;
            if (inPeriod < DashOn)
            {
                piece = DashOn - inPeriod;
                if (t + piece > len)
                    piece = len - t;
                Line(canvas, x1 + ux * t, y1 + uy * t, x1 + ux * (t + piece), y1 + uy * (t + piece), width, color);
            }
            else
            {
                piece = period - inPeriod;
            }
            if (piece < 0.01)
                piece = 0.01;
            t += piece;
        }
        return phase + len;
    }

    // Ламана (xs, ys -- точки в одиницях). Типово -- відрізки DrawSegment із
    // наскрізною фазою пунктиру; LineStyle "sketch" -- перенос sketch() мокапа:
    // кожен відрізок дрібниться на штрихи ~14 одиниць зі зсувом поперек і
    // вигином, з заходом за кути, а поверх -- другий тонкий штрих
    // напівпрозоро. Зсуви -- від seed (id ребра), тож між кадрами нічого не
    // тремтить.
    void DrawStroke(CanvasWidget canvas, array<float> xs, array<float> ys, float width, int color, bool dashed, string seed)
    {
        if (LineStyle == "sketch")
        {
            Sketch(canvas, xs, ys, width * 0.85, color, seed, dashed);
            int faint = (((color >> 24) & 0xFF) * 45 / 100) << 24 | (color & 0x00FFFFFF);
            Sketch(canvas, xs, ys, width * 0.45, faint, seed + "~", false);
            return;
        }
        float phase = 0;
        for (int i = 0; i + 1 < xs.Count(); i++)
            phase = DrawSegment(canvas, xs[i], ys[i], xs[i + 1], ys[i + 1], width, color, dashed, phase);
    }

    // Лінія сітки паперу (GridStep): колір і товщина -- GridColor, GridW.
    void GridLine(CanvasWidget canvas, float x1, float y1, float x2, float y2)
    {
        Line(canvas, x1, y1, x2, y2, GridW, GridColor);
    }

    // Ромб "АБО": заповнений тлом (Lcd), обведений кольором лінії. Товста
    // лінія канви -- це заповнений прямокутник, тож діагональна лінія завдовжки
    // і завширшки a*sqrt2 -- це ромб з напівдіагоналлю a.
    void DrawOrKnot(CanvasWidget canvas, float x, float y, int color)
    {
        Diamond(canvas, x, y, 8 + 1.41, color);
        Diamond(canvas, x, y, 8 - 1.41, Lcd);
    }

    // Квадратний вузлик "після всіх" (10 одиниць).
    void DrawAllKnot(CanvasWidget canvas, float x, float y, int color)
    {
        Line(canvas, x - 5, y, x + 5, y, 10, color);
    }

    protected void Diamond(CanvasWidget canvas, float x, float y, float half, int color)
    {
        float a = half / 2;
        Line(canvas, x - a, y - a, x + a, y + a, half * 1.41421, color);
    }

    // ---------- sketch() мокапа ----------

    private int m_Rng;

    // FNV-1a від рядка, далі xorshift -- рівно як rng() мокапа (32-бітні цілі).
    protected void RngSeed(string seed)
    {
        int h = -2128831035;   // 2166136261
        for (int i = 0; i < seed.Length(); i++)
        {
            h = h ^ seed.Get(i).ToAscii();
            h = Mul32(h, 16777619);
        }
        m_Rng = h;
    }

    protected float Rng()
    {
        int h = m_Rng;
        h = h ^ (h << 13);
        h = h ^ ((h >> 17) & 0x7FFF);
        h = h ^ (h << 5);
        m_Rng = h;
        // (h >>> 0) % 1000: беззнакова остача від знакового h.
        int r = h % 1000;
        if (h < 0)
        {
            r = (r + 296) % 1000;
            if (r < 0)
                r += 1000;
        }
        return r / 1000.0;
    }

    // Множення по модулю 2^32 без переповнення проміжних: половинами по 16 біт.
    protected static int Mul32(int a, int b)
    {
        int al = a & 0xFFFF;
        int ah = (a >> 16) & 0xFFFF;
        int bl = b & 0xFFFF;
        int bh = (b >> 16) & 0xFFFF;
        int lo = al * bl;
        int mid = ((ah * bl) & 0xFFFF) + ((al * bh) & 0xFFFF);
        return lo + (mid << 16);
    }

    protected void Sketch(CanvasWidget canvas, array<float> xs, array<float> ys, float width, int color, string seed, bool dashed)
    {
        RngSeed(seed);
        int n = xs.Count();
        float phase = 0;
        for (int i = 0; i + 1 < n; i++)
        {
            float x1 = xs[i];
            float y1 = ys[i];
            float x2 = xs[i + 1];
            float y2 = ys[i + 1];
            float len = Math.Sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
            if (len < 1)
                len = 1;
            float ux = (x2 - x1) / len;
            float uy = (y2 - y1) / len;
            float o1 = 0;
            if (i > 0)
                o1 = 2 + Rng() * 5;
            float o2 = 0;
            if (i < n - 2)
                o2 = 2 + Rng() * 5;
            float sx = x1 - ux * o1;
            float sy = y1 - uy * o1;
            float ex = x2 + ux * o2;
            float ey = y2 + uy * o2;
            int pieces = Math.Round(len / 14);
            if (pieces < 2)
                pieces = 2;
            float bend = (Rng() - 0.5) * 5;
            float px = sx;
            float py = sy;
            for (int k = 1; k <= pieces; k++)
            {
                float t = k;
                t = t / pieces;
                float j = (Rng() - 0.5) * 2.2 + bend * Math.Sin(Math.PI * t);
                float qx = sx + (ex - sx) * t - uy * j;
                float qy = sy + (ey - sy) * t + ux * j;
                if (dashed)
                    phase = DrawSegment(canvas, px, py, qx, qy, width, color, true, phase);
                else
                    Line(canvas, px, py, qx, qy, width, color);
                px = qx;
                py = qy;
            }
        }
    }

    // ------------------------------------------------------------------
    // Події. Меню кличе їх у свій час; типово нічого не роблять.
    // ------------------------------------------------------------------

    // Вікно щойно створене і ролі знайдені: тут скин ставить свої статичні
    // тексти, запускає свої частини (бігучий рядок, помічник).
    void OnShow(OZL_TreeMenu menu)
    {
    }

    // Кожен кадр: анімації (мерехтіння, бігучий рядок, кадри).
    void OnUpdate(OZL_TreeMenu menu, float dt)
    {
    }

    // Після кожного повного малювання (нова відповідь, інша гілка, вибір).
    void OnPaint(OZL_TreeMenu menu)
    {
    }

    // Вибрано вузол (або null -- нічого не вибрано).
    void OnSelect(OZL_TreeMenu menu, OZL_NodeView node, string status, bool canResearch)
    {
    }

    // Клік, який меню не впізнало (кнопки помічника тощо). true -- з'їдено.
    bool OnClick(OZL_TreeMenu menu, Widget w)
    {
        return false;
    }
}

// Таблиця семи вікон. Нове вікно -- новий рядок тут і свій клас поруч.
class OZL_TreeSkins
{
    static const string FALLBACK = "neutral";

    static bool Known(string id)
    {
        return id == "ecolog" || id == "clearsky" || id == "duty" || id == "freedom" || id == "sop" || id == "bandit" || id == "neutral";
    }

    static OZL_TreeSkin Make(string id)
    {
        if (id == "ecolog")
            return new OZL_TreeSkin_Ecolog();
        if (id == "clearsky")
            return new OZL_TreeSkin_Clearsky();
        if (id == "duty")
            return new OZL_TreeSkin_Duty();
        if (id == "freedom")
            return new OZL_TreeSkin_Freedom();
        if (id == "sop")
            return new OZL_TreeSkin_Sop();
        if (id == "bandit")
            return new OZL_TreeSkin_Bandit();
        if (id != FALLBACK)
            OZL_Log.Error("tree: the server sent an unknown window '" + id + "', showing " + FALLBACK);
        return new OZL_TreeSkin_Neutral();
    }
}

#endif
