// Вікно clearsky -- «Польовий КПК» (Чисте небо): темно-синій корпус КПК зі
// світлими рядками розгортки; увесь екран -- карта (ізолінії поверх сітки 64),
// дерево на ній росте вниз, ліворуч від картки; над картою плавають три панелі:
// гілка, легенда з балами, картка вузла. Вузли -- круглі мітки 50 з назвою
// праворуч, ціною під нею і смугою проєкту під ціною; зв'язки -- маршрути.
//
// Розкладки: ozl_tree_clearsky, ozl_node_clearsky (ui/OpenZone_Research/);
// картинки: source/ui/clearsky/ (набір ozl_clearsky і текстури
// gui/textures/tree/clearsky/); кольори й шрифти: ui/tokens/clearsky.json.
// Числа нижче -- ті самі токени в ARGB.
//
// Понад дані клас робить:
// - вузол: заливку кола за статусом (NodeFill), край під мишею -- txt,
//   світіння доступного (NodeRing) і пунктир вибраного разом, мітку проєкту,
//   що блимає; вузол без власного значка -- шестерня мокапа (iconOf);
// - підписи тирів -- власні рядки вікна (CsTierRow0..39), не рядки меню: на
//   стенді CreateWidgets рядка тиру віддав чужий файл (плутанина розкладок
//   R7, SKINS.md); рядки «АБО» і ціни мають однакові віджети, і LabelTick
//   показує в кожному своє;
// - великі літери там, де мокап пише text-transform; розрядку від .16em --
//   пробілами між літерами (Spread): TextWidget розрядки не вміє (скіл §32);
// - заголовки розділів картки: «//» тьмяне окремим написом, слово -- acc;
// - чіпи «Відкриває» за мокапом: 9 + текст + 9 у рамці 1 (OpensPad), 6 між
//   ними вшир і вгору-вниз, під мишею рамка txt (OnRowHover), заглушка
//   туману -- пунктиром;
// - смужки туману під переходом TreeFogEdge;
// - кілька гілок (у мокапі одна): клік по назві гілки показує наступну, «»»
//   після назви.
// Альфи світлих шарів над темною картою розв'язано під лінійне змішування
// рушія (скіл gui-layouts §32): сітка, тьмяна лінія, світіння, растр.

#ifndef NO_GUI

class OZL_TreeSkin_Clearsky : OZL_TreeSkin
{
    static const string SET = "set:ozl_clearsky image:";

    // Скільки кадрів чекати, поки текст розкладеться (як LATER_TRIES меню).
    static const int   TRIES = 12;
    // «»» після назви гілки -- на стільки далі від кінця її тексту (у мокапі
    // гілка одна й знака нема; решта чисел -- з віджетів розкладки).
    static const float MARK_GAP = 10;

    // Кольори мокапа, яких нема в базовому класі (color-mix його CSS).
    int Faint;       // --faint: закритий вузол, нуль у пулі, неактивна кнопка
    int Track;       // --track: доріжки смуг, порожні сегменти
    int EdgeColor;   // --edge: рамки панелей, чіпів, неактивної кнопки
    int Cell;        // --cell: заливка мітки
    int CellEdge;    // --cell-edge: край мітки, на яку не вистачає
    int LockedBg;    // заливка закритої: screen 80 % з чорним
    int DoneBg;      // --done-bg
    int DoneEdge;    // --done-edge
    int ResEdge;     // --res-edge
    int ItemChip;    // квадратик матеріалу в картці: #9a957f мокапа (renderCard)

    private float m_Clock;
    private int   m_BlinkStep;
    private ref array<Widget> m_Blink;
    private string m_HoverSeen;
    private bool  m_ChipsDirty;
    private int   m_ChipTries;
    private int   m_ChipPasses;
    private bool  m_HeadDirty;
    private int   m_HeadTries;
    private float m_FogX;
    private float m_FogY;
    private float m_FogW;
    private float m_FogH;
    private int   m_OrSeen;

    // Літери, після яких Spread ставить пробіл (цілими літерами: UTF-8 різати
    // по байтах не можна).
    private static ref array<string> s_Letters;

    void OZL_TreeSkin_Clearsky()
    {
        Named("clearsky");
        Dir     = "down";
        NodeW   = 50;
        NodeH   = 50;
        Row     = 140;
        Col     = 230;
        Top     = 190;
        Side    = 80;
        Shift   = -170;
        // Точка вузла в комірці 226x72 (ozl_node_clearsky): коло 50 від (11, 11).
        AnchorX = 36;
        AnchorY = 36;

        Txt       = ARGB(255, 195, 223, 240);
        Dim       = ARGB(255,  95, 138, 166);
        Acc       = ARGB(255, 111, 193, 255);
        Ok        = ARGB(255, 138, 215, 192);
        Bad       = ARGB(255, 255, 138,  92);
        // --line-dim (dim 60 %) у лінійному світлі рушія: .4.
        LineDim   = ARGB(102,  95, 138, 166);
        LineLit   = Txt;
        LineHl    = Acc;
        Lcd       = ARGB(255,  10,  24,  38);
        FogColor  = ARGB(255,   9,  22,  35);
        Faint     = ARGB(255,  74, 109, 133);
        Track     = ARGB(255,  28,  39,  51);
        EdgeColor = ARGB(255,  36,  66,  92);
        Cell      = ARGB(255,  20,  31,  42);
        CellEdge  = ARGB(255,  51,  65,  78);
        LockedBg  = ARGB(255,   9,  17,  26);
        DoneBg    = ARGB(255,  29,  48,  54);
        DoneEdge  = ARGB(255,  74, 118, 112);
        ResEdge   = ARGB(255,  66, 116, 155);
        ItemChip  = ARGB(255, 154, 149, 127);

        // Сітка карти (.content .bg мокапа: --grid, --grid-step), лінії від 0;
        // ізолінії й світіння екрана -- непрозора текстура CsMap під канвою.
        // --grid .05 у лінійному світлі рушія -- .012 (3/255): так на темній
        // карті вийде той самий відтінок, що в мокапі.
        GridStep  = 64;
        GridColor = ARGB(3, 110, 180, 240);

        // Край мітки: суцільний і пунктирний (закрита); заливку фарбує PaintNode.
        Shapes.Insert(SET + "node_ring");        // 0
        Shapes.Insert(SET + "node_ring_dash");   // 1
        ShapeColors.Set("locked", Faint);
        ShapeColors.Set("short", CellEdge);
        ShapeColors.Set("available", Acc);
        ShapeColors.Set("researching", ResEdge);
        ShapeColors.Set("completed", DoneEdge);

        // Мітки мокапа 12px: замок / галка / крапка (спека §3).
        Marks.Insert(SET + "mark_lock");
        Marks.Insert(SET + "mark_check");
        Marks.Insert(SET + "mark_dot");

        SegOn    = Acc;
        SegOff   = Track;
        TipPadX  = 10;   // рамка 1 + поле 9 (.tip мокапа)
        OpensGap = 6;    // .opens gap 6
        OpensPad = 9;    // текст чіпа від 9 (рамка 1 + поле 8), праворуч -- ті самі 9

        m_Blink     = new array<Widget>();
        m_BlinkStep = -1;
        m_HoverSeen = "";
        m_OrSeen    = -1;
    }

    // ------------------------------------------------------------------
    // Вузол
    // ------------------------------------------------------------------

    override int ShapeOf(string status, bool selected)
    {
        if (status == "locked")
            return 1;
        return 0;
    }

    // Світіння доступного (box-shadow 6) є й тоді, коли його вибрано: пунктир
    // вибраного ляже поверх світіння, як у мокапі.
    override bool RingShown(string status, bool selected)
    {
        return status == "available";
    }

    override int NameColorOf(string status)
    {
        if (status == "locked")
            return Faint;
        return Txt;
    }

    // .node .icon: тьмяний; доступний -- acc, досліджений -- ok, закритий --
    // faint (у ділі мокап значок не підсвічує).
    override int IconColorOf(string status)
    {
        if (status == "available")
            return Acc;
        if (status == "completed")
            return Ok;
        if (status == "locked")
            return Faint;
        return Dim;
    }

    override int MarkColorOf(string status)
    {
        if (status == "completed")
            return Ok;
        if (status == "researching")
            return Acc;
        return Faint;
    }

    // Розділи картки -- великими, розряджено (.sec .16em); «// » перед ними --
    // окремий тьмяний напис (OnShow).
    override string SectionText(string key)
    {
        return Spread(OZL_Text.Upper(OZL_Text.Words(key)));
    }

    // Слово статусу в картці -- великими (.cstat; його .12em пробілом не
    // передати -- пробіл etelka ширший за дві такі розрядки).
    override string CardStatusText(string status)
    {
        return OZL_Text.Upper(StatusText(status));
    }

    // Кнопка -- великими, розряджено (.go .18em).
    override string ButtonText(string status, bool enabled)
    {
        return Spread(OZL_Text.Upper(super.ButtonText(status, enabled)));
    }

    // Римська цифра тиру розряджено (.tierlab .2em): «I I».
    override string TierText(int tier)
    {
        return Spread(super.TierText(tier));
    }

    // Заливка мітки за статусом (.node .cell мокапа).
    int FillOf(string status)
    {
        if (status == "locked")
            return LockedBg;
        if (status == "completed")
            return DoneBg;
        return Cell;
    }

    override void PaintNode(OZL_TreeMenu menu, Widget cell, OZL_NodeView node, string status, bool selected)
    {
        super.PaintNode(menu, cell, node, status, selected);

        Widget fill = cell.FindAnyWidget("NodeFill");
        if (fill)
            fill.SetColor(FillOf(status));
        Widget shape = cell.FindAnyWidget("NodeShape");
        if (shape && node.Id == menu.HoveredId())
            shape.SetColor(Txt);

        // Вузол без власного значка (чи значок не завантажився) -- шестерня:
        // iconOf() мокапа так само падає на ICON.gear.
        ImageWidget icon = ImageWidget.Cast(cell.FindAnyWidget("NodeIcon"));
        if (icon && !icon.IsVisible() && icon.LoadImageFile(0, SET + "icon_gear"))
        {
            icon.SetImage(0);
            icon.SetColor(IconColorOf(status));
            icon.Show(true);
        }

        // Мітка проєкту блимає (OnUpdate); решта -- рівна: альфу мітці вже
        // повернув SetColor базового класу.
        Widget mark = cell.FindAnyWidget("NodeMark");
        if (mark)
        {
            int at = IndexIn(m_Blink, mark);
            if (status == "researching")
            {
                if (at < 0)
                    m_Blink.Insert(mark);
            }
            else if (at >= 0)
            {
                m_Blink.Remove(at);
            }
        }
    }

    // ------------------------------------------------------------------
    // Пул, картка, кнопка
    // ------------------------------------------------------------------

    // Рядок пулу: назва й число -- txt, нуль -- faint (.prow.zero).
    override void PaintPoolRow(OZL_TreeMenu menu, Widget row, int index, string line, int have, int color)
    {
        super.PaintPoolRow(menu, row, index, line, have, color);
        int ink = Txt;
        if (have <= 0)
            ink = Faint;
        Tint(row, "PoolName", ink);
        Tint(row, "PoolValue", ink);
    }

    // Рядок вартості -- як у базовому класі; квадратик матеріалу (рядок у
    // CardItemList) -- #9a957f мокапа, а не тьмяний скіну, що дає меню.
    override void PaintCostRow(OZL_TreeMenu menu, Widget row, string label, string text, int verdict)
    {
        super.PaintCostRow(menu, row, label, text, verdict);
        Widget items = menu.Role("CardItemList");
        if (items && row.GetParent() == items)
            Tint(row, "CostChip", ItemChip);
    }

    // Чіп «Відкриває» в рамці 1 (.opens a); заглушка туману -- faint і рамка
    // пунктиром (.fogged). Ряди з проміжком 6 ставить OnUpdate.
    override void PaintOpenChip(OZL_TreeMenu menu, Widget chip, string text, bool fogged)
    {
        super.PaintOpenChip(menu, chip, text, fogged);
        if (fogged)
            Tint(chip, "ChipText", Faint);
        ShowIn(chip, "ChipDashLine", fogged);
        ShowIn(chip, "ChipTopLine", !fogged);
        ShowIn(chip, "ChipBottomLine", !fogged);
        ShowIn(chip, "CsChipLeft", !fogged);
        ShowIn(chip, "CsChipRight", !fogged);
        TintChip(chip, EdgeColor);
        m_ChipsDirty = true;
        m_ChipTries = 0;
        m_ChipPasses = 3;
    }

    // Рамка чіпа під мишею -- txt (.opens a:hover); заглушка туману ChipHit не
    // має і під мишу не потрапляє.
    override void OnRowHover(OZL_TreeMenu menu, Widget row, string kind, string id, bool on)
    {
        super.OnRowHover(menu, row, kind, id, on);
        if (kind != "open" || !row)
            return;
        if (on)
            TintChip(row, Txt);
        else
            TintChip(row, EdgeColor);
    }

    // .go: доступна -- acc і acc-рамка, неактивна -- faint і рамка --edge. Слово
    // (ButtonText) уже поставило меню; під мишею воно ж темне на acc
    // (BtnResearchHover).
    override void PaintButton(OZL_TreeMenu menu, Widget btn, bool enabled)
    {
        int color = Faint;
        int edge = EdgeColor;
        if (enabled)
        {
            color = Acc;
            edge = Acc;
        }
        TextWidget text = TextWidget.Cast(menu.Role("BtnResearchText"));
        if (text)
            text.SetColor(color);
        string status = "";
        OZL_NodeView n = menu.NodeOf(menu.SelectedId());
        if (n)
            status = n.Status;
        TextWidget hover = TextWidget.Cast(menu.Role("CsBtnHoverText"));
        if (hover)
            hover.SetText(ButtonText(status, enabled));
        TintRole(menu, "CsBtnTop", edge);
        TintRole(menu, "CsBtnBottom", edge);
        TintRole(menu, "CsBtnLeft", edge);
        TintRole(menu, "CsBtnRight", edge);
    }

    // ------------------------------------------------------------------
    // Події
    // ------------------------------------------------------------------

    override void OnShow(OZL_TreeMenu menu)
    {
        // .dev .14em і .bname .1em розрядки не мають: пробіл etelka вдвічі ширший.
        SetRole(menu, "DevName", OZL_Text.Upper(OZL_Text.Words("STR_OZL_SKIN_CLEARSKY_DEV")));
        SetRole(menu, "BtnCloseText", OZL_Text.Upper(OZL_Text.Words("STR_OZL_TREE_CLOSE")));
        SetRole(menu, "CsLegendHead", Spread(OZL_Text.Upper(OZL_Text.Words("STR_OZL_SKIN_CLEARSKY_LEGEND_POOL"))));
        // «// » перед заголовками розділів -- теж розряджено (.sec::before
        // успадковує .16em): «/ / », слово стоїть за ним у розкладці.
        string mark = Spread(OZL_Text.Words("STR_OZL_SKIN_CLEARSKY_SEC_MARK"));
        SetRole(menu, "CsCostMark", mark);
        SetRole(menu, "CsItemsMark", mark);
        SetRole(menu, "CsTimeMark", mark);
        SetRole(menu, "CsOpensMark", mark);

        // Легенда -- рядом за шириною текстів, 14 між ними (англійські слова довші).
        menu.FlowLater(menu.Role("LegendRow"), 14, 0, false);

        m_Clock = 0;
        m_BlinkStep = -1;
        m_HoverSeen = "";
        m_ChipsDirty = false;
        m_HeadDirty = false;
        m_OrSeen = -1;
        m_Blink.Clear();
    }

    // Назва гілки великими (.bname); підписи тирів; кілька гілок -- кнопка на
    // всю назву і «»» за нею.
    override void OnPaint(OZL_TreeMenu menu)
    {
        OZL_BranchView b = menu.CurrentBranch();
        TextWidget name = TextWidget.Cast(menu.Role("BranchName"));
        if (name && b)
            name.SetText(DataText(OZL_Text.Upper(b.Name)));
        PaintTiers(menu, b);
        bool many = menu.BranchCount() > 1;
        ShowRole(menu, "CsBranchNext", many);
        ShowRole(menu, "CsBranchMark", false);
        m_HeadDirty = many;
        m_HeadTries = 0;
    }

    override void OnSelect(OZL_TreeMenu menu, OZL_NodeView node, string status, bool canResearch)
    {
        if (!node)
            return;
        // Рядок заголовка з «//» ховається разом із написом, що сховало меню.
        Follow(menu, "CsItemsHeadRow", "CardItemsHead");
        Follow(menu, "CsOpensHeadRow", "CardOpensHead");
        menu.RefreshCard();
    }

    // Назва гілки перемикає гілки по колу, коли їх більше однієї (у мокапі гілка одна).
    override bool OnClick(OZL_TreeMenu menu, Widget w)
    {
        if (!w || w.GetName() != "CsBranchNext")
            return false;
        OZL_TreeView view = menu.View();
        OZL_BranchView cur = menu.CurrentBranch();
        if (!view || !cur || view.Branches.Count() < 2)
            return true;
        int count = view.Branches.Count();
        int at = 0;
        for (int i = 0; i < count; i++)
        {
            if (view.Branches[i] && view.Branches[i].Id == cur.Id)
                at = i;
        }
        int next = (at + 1) % count;
        if (view.Branches[next])
            menu.PickBranch(view.Branches[next].Id);
        return true;
    }

    override void OnUpdate(OZL_TreeMenu menu, float dt)
    {
        m_Clock += dt;
        BlinkTick();
        HoverTick(menu);
        ChipTick(menu);
        HeadTick(menu);
        FogTick(menu);
        LabelTick(menu);
    }

    // ------------------------------------------------------------------
    // Підписи тирів
    // ------------------------------------------------------------------

    // Тири видимих вузлів за зростанням; i-й -- рядок вікна CsTierRow<i>
    // кутом на (0, Top + Row x (i + 1/2)), де OZL_TreePlan ставить тир дерева
    // вниз (план меню назовні не видно -- прохання в звіті). Де в рядку
    // напис і скільки рядків -- каже розкладка.
    private void PaintTiers(OZL_TreeMenu menu, OZL_BranchView b)
    {
        array<int> tiers = new array<int>();
        int i;
        if (b)
        {
            for (i = 0; i < b.Nodes.Count(); i++)
            {
                OZL_NodeView n = b.Nodes[i];
                if (!n)
                    continue;
                int t = OZL_TreePlan.TierOf(n);
                if (tiers.Find(t) < 0)
                    tiers.Insert(t);
            }
        }
        tiers.Sort();
        i = 0;
        Widget row = menu.Role("CsTierRow0");
        while (row)
        {
            // Рамка в одиницю заввишки інакше ріже напис до смужки в піксель
            // (скіл gui-layouts) і бере мишу -- як меню зі своїми рядками пулу.
            row.ClearFlags(WidgetFlags.CLIPCHILDREN);
            row.SetFlags(WidgetFlags.IGNOREPOINTER);
            bool used = i < tiers.Count();
            if (used)
            {
                TextWidget lab = TextWidget.Cast(row.FindAnyWidget("CsTier" + i.ToString()));
                if (lab)
                    lab.SetText(TierText(tiers[i]));
                menu.PlaceUnits(row, 0, Top + Row * (i + 0.5));
            }
            row.Show(used);
            i++;
            row = menu.Role("CsTierRow" + i.ToString());
        }
        if (tiers.Count() > i)
            OZL_Log.Warn("tree clearsky: " + tiers.Count().ToString() + " tiers, but the window has numerals for " + i.ToString());
    }

    // ------------------------------------------------------------------
    // Кожен кадр
    // ------------------------------------------------------------------

    // Мітка проєкту: blink 1 s steps(2) мокапа -- 1, .6, .2, .6 по чверті секунди.
    private void BlinkTick()
    {
        int step = Math.Floor(Math.ModFloat(m_Clock, 1) * 4);
        if (step == m_BlinkStep)
            return;
        m_BlinkStep = step;
        float a = 1;
        if (step == 1 || step == 3)
            a = 0.6;
        else if (step == 2)
            a = 0.2;
        for (int i = m_Blink.Count() - 1; i >= 0; i--)
        {
            Widget w = m_Blink[i];
            if (!w)
            {
                m_Blink.Remove(i);
                continue;
            }
            w.SetAlpha(a);
        }
    }

    // Край мітки під мишею -- txt (.node:hover .cell); меню наведення не
    // перемальовує, тож тут стежимо, чий вузол під мишею.
    private void HoverTick(OZL_TreeMenu menu)
    {
        string id = menu.HoveredId();
        if (id == m_HoverSeen)
            return;
        string was = m_HoverSeen;
        m_HoverSeen = id;
        EdgeOf(menu, was, false);
        EdgeOf(menu, id, true);
    }

    private void EdgeOf(OZL_TreeMenu menu, string id, bool hovered)
    {
        if (id == "")
            return;
        Widget nodes = menu.Role("TreeNodes");
        OZL_NodeView n = menu.NodeOf(id);
        if (!nodes || !n)
            return;
        Widget cell = nodes.FindAnyWidget("cell:" + id);
        if (!cell)
            return;
        Widget shape = cell.FindAnyWidget("NodeShape");
        if (!shape)
            return;
        if (hovered)
            shape.SetColor(Txt);
        else
            shape.SetColor(ShapeColorOf(n.Status));
    }

    // «Відкриває» (.opens): меню розкладає чіпи рядом (текст + OpensPad,
    // OpensGap між ними) і тягне ChipHit та ...Line на ширину; ряди воно
    // ставить упритул, а мокап -- через той самий gap 6 (flex-wrap). Тут --
    // ряди за мокапом (OpensGap і вшир, і вгору-вниз; висота ряду -- висота
    // чіпа з розкладки), права рамка чіпа і висота списку, після меню
    // (OnUpdate іде після RunFlows) і ще двічі, якщо меню розкладе їх
    // кадром пізніше.
    private void ChipTick(OZL_TreeMenu menu)
    {
        if (!m_ChipsDirty)
            return;
        Widget list = menu.Role("CardOpensList");
        if (!list || !list.IsVisible())
        {
            m_ChipsDirty = false;
            return;
        }
        float px = menu.Px();
        array<Widget> chips = new array<Widget>();
        array<float> widths = new array<float>();
        bool ready = true;
        Widget chip = list.GetChildren();
        while (chip)
        {
            TextWidget t = TextWidget.Cast(chip.FindAnyWidget("ChipText"));
            if (t && chip.IsVisible())
            {
                int tw;
                int th;
                t.GetTextSize(tw, th);
                if (tw <= 0)
                    ready = false;
                // Ширина -- як у меню (від лівого краю чіпа до кінця тексту
                // і OpensPad): тоді права рамка сходиться з ...Line, які
                // меню розтягнуло.
                float tx;
                float ty;
                float ix;
                float iy;
                t.GetScreenPos(tx, ty);
                chip.GetScreenPos(ix, iy);
                chips.Insert(chip);
                widths.Insert((tx - ix + tw) / px + OpensPad);
            }
            chip = chip.GetSibling();
        }
        if (!ready && m_ChipTries < TRIES)
        {
            m_ChipTries++;
            return;
        }
        m_ChipPasses--;
        if (m_ChipPasses <= 0)
            m_ChipsDirty = false;
        float boxW;
        float boxH;
        menu.UnitsOf(list, boxW, boxH);
        float x = 0;
        float y = 0;
        float rowH = 0;
        for (int i = 0; i < chips.Count(); i++)
        {
            Widget c = chips[i];
            float w = widths[i];
            float cw;
            float ch;
            menu.UnitsOf(c, cw, ch);
            if (x > 0 && x + w > boxW)
            {
                x = 0;
                y += rowH + OpensGap;
                rowH = 0;
            }
            if (ch > rowH)
                rowH = ch;
            menu.PlaceUnits(c, x, y);
            Widget right = c.FindAnyWidget("CsChipRight");
            if (right)
            {
                float rw;
                float rh;
                menu.UnitsOf(right, rw, rh);
                menu.PlaceUnits(right, w - rw, 0);
            }
            x += w + OpensGap;
        }
        menu.HeightUnits(list, y + rowH);
        menu.RefreshCard();
    }

    // «»» за назвою гілки, коли гілок більше однієї: на рядку назви (шрифт
    // той самий), MARK_GAP після кінця її тексту. Де назва -- питаємо її
    // віджет; знак і назва -- діти однієї панелі.
    private void HeadTick(OZL_TreeMenu menu)
    {
        if (!m_HeadDirty)
            return;
        TextWidget name = TextWidget.Cast(menu.Role("BranchName"));
        Widget mark = menu.Role("CsBranchMark");
        Widget box = null;
        if (mark)
            box = mark.GetParent();
        if (!name || !box)
        {
            m_HeadDirty = false;
            return;
        }
        int nw;
        int nh;
        name.GetTextSize(nw, nh);
        if (nw <= 0 && m_HeadTries < TRIES)
        {
            m_HeadTries++;
            return;
        }
        m_HeadDirty = false;
        float nx;
        float ny;
        float bx;
        float by;
        name.GetScreenPos(nx, ny);
        box.GetScreenPos(bx, by);
        float px = menu.Px();
        menu.PlaceUnits(mark, (nx - bx + nw) / px + MARK_GAP, (ny - by) / px);
        mark.Show(true);
    }

    // Смужки туману (135 градусів, txt 4 % мокапа) -- під переходом
    // TreeFogEdge, на його прямокутнику: видно їх лише крізь перехід, як у мокапі.
    private void FogTick(OZL_TreeMenu menu)
    {
        Widget stripes = menu.Role("CsFogStripes");
        if (!stripes)
            return;
        Widget edge = menu.Role("TreeFogEdge");
        Widget content = menu.Role("TreeContent");
        if (!edge || !content || !edge.IsVisible())
        {
            if (stripes.IsVisible())
                stripes.Show(false);
            return;
        }
        float ex;
        float ey;
        float cx;
        float cy;
        edge.GetScreenPos(ex, ey);
        content.GetScreenPos(cx, cy);
        float ew;
        float eh;
        menu.UnitsOf(edge, ew, eh);
        float px = menu.Px();
        float x = (ex - cx) / px;
        float y = (ey - cy) / px;
        bool same = Math.AbsFloat(x - m_FogX) < 0.5 && Math.AbsFloat(y - m_FogY) < 0.5 && Math.AbsFloat(ew - m_FogW) < 0.5 && Math.AbsFloat(eh - m_FogH) < 0.5;
        if (same && stripes.IsVisible())
            return;
        m_FogX = x;
        m_FogY = y;
        m_FogW = ew;
        m_FogH = eh;
        menu.PlaceUnits(stripes, x, y);
        menu.SizeUnits(stripes, ew, eh);
        stripes.Show(true);
    }

    // Рядки «АБО» (усе в TreeNodes, що не комірка вузла) мають ті самі віджети,
    // що й рядки ціни (плутанина розкладок R7): тут кожен такий рядок показує
    // OrText і ховає частини ціни -- хоч би який із двох файлів дав рушій.
    // Рядки лише додаються (пул меню), тож досить стежити за їхньою кількістю.
    private void LabelTick(OZL_TreeMenu menu)
    {
        Widget nodes = menu.Role("TreeNodes");
        if (!nodes)
            return;
        int rows = 0;
        Widget c = nodes.GetChildren();
        while (c)
        {
            string nm = c.GetName();
            if (nm.IndexOf("cell:") != 0)
                rows++;
            c = c.GetSibling();
        }
        if (rows == m_OrSeen)
            return;
        m_OrSeen = rows;
        c = nodes.GetChildren();
        while (c)
        {
            string cn = c.GetName();
            if (cn.IndexOf("cell:") != 0)
            {
                ShowIn(c, "OrText", true);
                ShowIn(c, "PriceChip", false);
                ShowIn(c, "PriceText", false);
            }
            c = c.GetSibling();
        }
    }

    // ------------------------------------------------------------------
    // Дрібниці
    // ------------------------------------------------------------------

    // Розрядка пробілами: пробіл після кожної літери, цифри, «·» і «/»
    // (letter-spacing мокапа ставить її й після останньої). TextWidget
    // розрядки не вміє -- "text spacing" і SetTextSpacing не малюють нічого
    // (скіл gui-layouts §32). Заміна цілої літери безпечна для UTF-8, як у
    // OZL_Text.Upper.
    static string Spread(string text)
    {
        if (!s_Letters)
        {
            s_Letters = new array<string>();
            string all = "А Б В Г Ґ Д Е Є Ж З И І Ї Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ь Ю Я ";
            all += "а б в г ґ д е є ж з и і ї й к л м н о п р с т у ф х ц ч ш щ ь ю я ";
            all += "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z ";
            all += "a b c d e f g h i j k l m n o p q r s t u v w x y z 0 1 2 3 4 5 6 7 8 9 · /";
            all.Split(" ", s_Letters);
        }
        string t = text;
        for (int i = 0; i < s_Letters.Count(); i++)
        {
            if (s_Letters[i] != "")
                t.Replace(s_Letters[i], s_Letters[i] + " ");
        }
        return t;
    }

    private static void TintChip(Widget chip, int color)
    {
        Tint(chip, "ChipTopLine", color);
        Tint(chip, "ChipBottomLine", color);
        Tint(chip, "CsChipLeft", color);
        Tint(chip, "CsChipRight", color);
    }

    private static int IndexIn(array<Widget> list, Widget w)
    {
        for (int i = 0; i < list.Count(); i++)
        {
            if (list[i] == w)
                return i;
        }
        return -1;
    }

    private static void Tint(Widget root, string name, int color)
    {
        Widget w = root.FindAnyWidget(name);
        if (w)
            w.SetColor(color);
    }

    private static void ShowIn(Widget root, string name, bool on)
    {
        Widget w = root.FindAnyWidget(name);
        if (w)
            w.Show(on);
    }

    private static void SetRole(OZL_TreeMenu menu, string role, string text)
    {
        TextWidget t = TextWidget.Cast(menu.Role(role));
        if (t)
            t.SetText(text);
    }

    private static void TintRole(OZL_TreeMenu menu, string role, int color)
    {
        Widget w = menu.Role(role);
        if (w)
            w.SetColor(color);
    }

    private static void ShowRole(OZL_TreeMenu menu, string role, bool on)
    {
        Widget w = menu.Role(role);
        if (w)
            w.Show(on);
    }

    private static void Follow(OZL_TreeMenu menu, string row, string head)
    {
        Widget r = menu.Role(row);
        Widget h = menu.Role(head);
        if (r && h)
            r.Show(h.IsVisible());
    }
}

#endif
