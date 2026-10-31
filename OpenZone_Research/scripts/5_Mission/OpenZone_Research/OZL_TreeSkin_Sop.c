// Вікно sop -- «Тактичний планшет»: старий ламповий монітор. Товста округла
// рамка кінескопа, рядки розгортки, темні кути, мерехтіння і смуга, що біжить
// згори вниз; на екрані -- армійський HUD: позивний гілки і пул (назва лінії
// над її числом) під попереджувальною смугою, дерево вправо великими ромбами
// на бурштиновій сітці, праворуч рамка цілі з даними вузла і великим
// 7-сегментним годинником проєкту.
//
// Відблиску на склі нема -- рішення власника 2026-10-31 (на стенді він
// малювався кільцями).
//
// Розкладки: ozl_tree_sop, ozl_node_sop (ui/OpenZone_Research/); картинки:
// source/ui/sop/ (набір ozl_sop і текстури gui/textures/tree/sop/); кольори й
// шрифти: ui/tokens/sop.json. Числа нижче -- ті самі токени в ARGB, а там, де
// клас малює сам (заливки й краї ромбів, тьмяна лінія, сітка), -- з поправкою
// на лінійне змішування.
//
// Понад дані клас робить:
// - кінескоп: альфа скла (CrtGlow, CrtLines) крокує, як crt-flicker мокапа;
//   смуга CrtRoll їде згори вниз за 7 с;
// - вузол: заливку ромба за статусом (NodeFill), край вузла під мишею -- txt,
//   мітку проєкту, що блимає, ціну по центру під вузлом;
// - великі літери (OZL_Text.Upper) і розрядку пробілами там, де мокап пише
//   text-transform і широкий letter-spacing;
// - HUD: BranchSub -- за ширшим рядком позивного, рядки пулу -- справа наліво;
// - картку: «Лишилось» + 7-сегментний годинник + «з 1 хв 00 с», чіпи
//   «Відкриває» в рамках за шириною тексту.

#ifndef NO_GUI

class OZL_TreeSkin_Sop : OZL_TreeSkin
{
    static const string SET    = "set:ozl_sop image:";
    static const string COMMON = "set:ozl_common image:";

    // Світіння тексту мокапа (text-shadow, бурштиновий ореол) тут нема: рушій
    // малює тінь TextWidget лише шрифтам SDF, а вікно написане бітмаповими
    // (скіл gui-layouts.md §32, стенд 2026-10-31).

    // Чіп «Відкриває» (.opens a мокапа): поле 12 від рамки до тексту, рамка 2,
    // проміжок між чіпами 6 -- і вбік, і між рядками. Висоту чіпа й ширину
    // ряду ChipTick бере з самих віджетів (ozl_sop_opens_chip, CardOpensList).
    static const float CHIP_PAD  = 12;
    static const float CHIP_EDGE = 2;
    static const float CHIP_GAP  = 6;

    // Чіп ціни під вузлом (ozl_sop_price_chip, .price b мокапа): квадрат 7 і 3
    // до числа -- PriceText стоїть на 10; між чіпами 6 (FlowLater меню).
    static const float PRICE_LEAD = 10;
    static const float PRICE_GAP  = 6;

    // Крок цифри годинника: ванільний 7segment48 моноширинний, 24 px на
    // клітинку 40, тож при "exact text size" 26 цифра -- 15.6 одиниці.
    // Двокрапки у шрифті нема -- це спрайт timer_colon завширшки 8.
    static const float DIGIT = 15.6;
    static const float COLON = 8;
    // Пробіл 18-піксельного Oswald у рядку часу.
    static const float SPACE = 4.1;
    // Скільки кадрів чекати, поки текст розкладеться (як LATER_TRIES меню).
    static const int   TRIES = 12;

    // Кольори мокапа, яких нема в базовому класі (color-mix його CSS).
    int Faint;       // --faint: закритий вузол, неактивна кнопка
    int Track;       // --track: порожні сегменти, доріжки смуг
    int EdgeColor;   // --edge: рамка кнопки, чіпів
    int Cell;        // --cell: ромб, на який не вистачає
    int CellEdge;    // --cell-edge
    int AvailBg;     // ромб доступного й у ділі: acc 14 %
    int LockedBg;    // ромб закритого: screen 80 % з чорним
    int DoneBg;      // --done-bg
    int DoneEdge;    // --done-edge
    int ResEdge;     // --res-edge

    private float m_Clock;
    private float m_FlickerAt;
    private float m_FlickerShown;
    private int   m_BlinkStep;
    private ref array<Widget> m_Blink;
    private string m_HoverSeen;
    private ref array<Widget> m_Prices;
    private ref array<int>    m_PriceTries;
    private bool  m_PoolDirty;
    private int   m_PoolTries;
    private bool  m_HudDirty;
    private int   m_HudTries;
    private bool  m_ChipsDirty;
    private int   m_ChipTries;
    private int   m_ChipPasses;
    private Widget m_ChipLit;   // чіп «Відкриває» під мишею (рамка txt)
    private int   m_TimerLeft;
    private int   m_TimerTries;
    private float m_FogX;
    private float m_FogW;
    private float m_FogH;

    void OZL_TreeSkin_Sop()
    {
        Named("sop");
        Dir     = "right";
        NodeW   = 88;
        NodeH   = 88;
        Keep    = 98;
        Row     = 235;
        Col     = 180;
        Top     = 90;
        Side    = 60;
        // Точка вузла в комірці 200x176 (ozl_node_sop): ромб 88x88 від (56, 12).
        AnchorX = 100;
        AnchorY = 56;

        Txt       = ARGB(255, 236, 223, 174);
        Dim       = ARGB(255, 154, 141,  92);
        Acc       = ARGB(255, 255, 185,  53);
        Ok        = ARGB(255, 180, 220, 106);
        Bad       = ARGB(255, 255, 106,  74);
        LineDim   = ARGB( 97, 154, 141,  92);   // --line-dim .6, для лінійного змішування -- .38
        LineLit   = Txt;
        LineHl    = Acc;
        Lcd       = ARGB(255,  18,  17,   9);
        FogColor  = ARGB(255,  17,  16,   8);
        Faint     = ARGB(255, 121, 110,  72);
        Track     = ARGB(255,  39,  37,  26);
        EdgeColor = ARGB(255,  90,  82,  50);
        Cell      = ARGB(255,  31,  29,  19);
        CellEdge  = ARGB(255,  68,  64,  47);
        AvailBg   = ARGB(255,  53,  42,  17);
        LockedBg  = ARGB(255,  16,  15,   9);
        DoneBg    = ARGB(255,  42,  47,  24);
        DoneEdge  = ARGB(255, 100, 120,  59);
        ResEdge   = ARGB(255, 149, 110,  34);

        // Сітка екрана (.content .bg мокапа: --grid, --grid-step), лінії від 0.
        // Альфа 3, а не 18 (.07): інтерфейс змішується в лінійному світлі, і
        // світла лінія на темному з .07 удвічі яскравіша, ніж у браузері
        // (стенд 2026-10-31); 3 дає ті самі ~(35, 30, 16) на #121109.
        GridStep  = 56;
        GridColor = ARGB(3, 255, 200, 110);

        // Край ромба: суцільний і пунктирний (закритий); заливку фарбує PaintNode.
        Shapes.Insert(SET + "diamond_edge");   // 0
        Shapes.Insert(SET + "diamond_dash");   // 1
        ShapeColors.Set("locked", Faint);
        ShapeColors.Set("short", CellEdge);
        ShapeColors.Set("available", Acc);
        ShapeColors.Set("researching", ResEdge);
        ShapeColors.Set("completed", DoneEdge);

        // Мітки: замок / галка / крапка (спека §3) -- спільні фігури ozl_common.
        Marks.Insert(COMMON + "mark_lock");
        Marks.Insert(COMMON + "mark_check");
        Marks.Insert(COMMON + "mark_dot");

        SegOn   = Acc;
        SegOff  = Track;
        TipPadX = 10;   // рамка 1 + поле 9 (.tip мокапа)

        m_Blink      = new array<Widget>();
        m_Prices     = new array<Widget>();
        m_PriceTries = new array<int>();
        m_FlickerShown = -1;
        m_BlinkStep  = -1;
        m_TimerLeft  = -1;
        m_HoverSeen  = "";
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

    // Доступний вузол мокап обводить самим краєм ромба (acc), окремого кільця нема.
    override bool RingShown(string status, bool selected)
    {
        return false;
    }

    override int NameColorOf(string status)
    {
        if (status == "locked")
            return Faint;
        return Txt;
    }

    // .node .icon: тьмяний; доступний -- acc, досліджений -- ok, закритий -- faint
    // (у ділі мокап значок не підсвічує).
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

    // Розділи картки -- великими й розряджено (.sec: uppercase, .16em), «▸ »
    // перед ними -- спрайт.
    override string SectionText(string key)
    {
        return Spread(OZL_Text.Upper(OZL_Text.Words(key)));
    }

    // Підпис тиру розряджено (.tierlab .2em): «т и р  I I».
    override string TierText(int tier)
    {
        return Spread(super.TierText(tier));
    }

    // Назва вузла і ціль у картці -- великими (.lbl, .cname).
    override string NodeNameText(string name)
    {
        return OZL_Text.Upper(name);
    }

    // Заливка ромба за статусом (.node .cell мокапа).
    int FillOf(string status)
    {
        if (status == "locked")
            return LockedBg;
        if (status == "available" || status == "researching")
            return AvailBg;
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

        // Мітка проєкту блимає (OnUpdate); решта -- рівна.
        Widget mark = cell.FindAnyWidget("NodeMark");
        if (mark)
        {
            int at = IndexIn(m_Blink, mark);
            if (status == "researching")
            {
                if (at < 0)
                    m_Blink.Insert(mark);
            }
            else
            {
                if (at >= 0)
                    m_Blink.Remove(at);
                mark.SetAlpha(1);
            }
        }

        // Ціну меню покладе слідом -- центрувати, коли її текст розкладеться.
        if (IndexIn(m_Prices, cell) < 0)
        {
            m_Prices.Insert(cell);
            m_PriceTries.Insert(0);
        }
    }

    // ------------------------------------------------------------------
    // Пул, картка, кнопка
    // ------------------------------------------------------------------

    // Рядок пулу в HUD: назва лінії великими й число під нею, без шкали
    // (рішення власника 2026-10-31: сегменти читались як щось окреме від
    // числа). Базовий метод не кличемо: рядок -- лише назва й число.
    // Розставляє рядки PoolTick.
    override void PaintPoolRow(OZL_TreeMenu menu, Widget row, int index, string line, int have, int color)
    {
        TextWidget name = TextWidget.Cast(row.FindAnyWidget("PoolName"));
        if (name)
        {
            name.SetText(OZL_Text.Upper(menu.PointName(line)));
            name.SetColor(Dim);
        }
        TextWidget value = TextWidget.Cast(row.FindAnyWidget("PoolValue"));
        if (value)
        {
            value.SetText(have.ToString());
            value.SetColor(Txt);
        }
        m_PoolDirty = true;
        m_PoolTries = 0;
    }

    // Чіп «Відкриває» в рамці 2 (.opens a); заглушка туману -- faint (у мокапі
    // ще й пунктир; тут суцільна faint-рамка). Рамку під текст ставить OnUpdate.
    override void PaintOpenChip(OZL_TreeMenu menu, Widget chip, string text, bool fogged)
    {
        super.PaintOpenChip(menu, chip, text, fogged);
        int edge = EdgeColor;
        if (fogged)
        {
            edge = Faint;
            Widget t = chip.FindAnyWidget("ChipText");
            if (t)
                t.SetColor(Faint);
        }
        TintChip(chip, edge);
        m_ChipsDirty = true;
        m_ChipTries = 0;
        m_ChipPasses = 2;
    }

    // .go: великими, розряджено (.24em); доступна -- acc і acc-рамка, неактивна -- faint
    // і рамка --edge. Під мишею меню показує BtnResearchHover (acc, слово темне).
    override void PaintButton(OZL_TreeMenu menu, Widget btn, bool enabled)
    {
        int color = Faint;
        int edge = EdgeColor;
        if (enabled)
        {
            color = Acc;
            edge = Acc;
        }
        string key = "STR_OZL_TREE_RESEARCH";
        OZL_NodeView n = menu.NodeOf(menu.SelectedId());
        if (n && n.Status == "completed")
            key = "STR_OZL_TREE_COMPLETED";
        string word = Spread(OZL_Text.Upper(OZL_Text.Words(key)));
        TextWidget text = TextWidget.Cast(menu.Role("BtnResearchText"));
        if (text)
        {
            text.SetText(word);
            text.SetColor(color);
        }
        TextWidget hover = TextWidget.Cast(menu.Role("SopBtnHoverText"));
        if (hover)
            hover.SetText(word);
        TintRole(menu, "SopBtnTop", edge);
        TintRole(menu, "SopBtnBottom", edge);
        TintRole(menu, "SopBtnLeft", edge);
        TintRole(menu, "SopBtnRight", edge);
    }

    // ------------------------------------------------------------------
    // Події
    // ------------------------------------------------------------------

    override void OnShow(OZL_TreeMenu menu)
    {
        TextWidget dev = TextWidget.Cast(menu.Role("DevName"));
        if (dev)
            dev.SetText(OZL_Text.Upper(OZL_Text.Words("STR_OZL_SKIN_SOP_DEV")));
        TextWidget closer = TextWidget.Cast(menu.Role("BtnCloseText"));
        if (closer)
            closer.SetText(OZL_Text.Upper(OZL_Text.Words("STR_OZL_TREE_CLOSE")));
        // «ЦІЛЬ» розряджено (.3em); ромбик перед ним -- спрайт.
        TextWidget target = TextWidget.Cast(menu.Role("SopTargetText"));
        if (target)
            target.SetText(Spread(OZL_Text.Words("STR_OZL_SKIN_SOP_TARGET")));

        // Легенда -- рядом за шириною текстів (англійські слова довші).
        menu.FlowLater(menu.Role("LegendRow"), 14, 0, false);

        m_Clock = 0;
        m_FlickerAt = 0;
        m_FlickerShown = -1;
        m_HudDirty = true;
        m_HudTries = 0;
        m_HoverSeen = "";
        m_Blink.Clear();
        m_Prices.Clear();
        m_PriceTries.Clear();
    }

    // Позивний -- назва гілки великими (.bname); її ширина зсуває BranchSub.
    override void OnPaint(OZL_TreeMenu menu)
    {
        OZL_BranchView b = menu.CurrentBranch();
        TextWidget name = TextWidget.Cast(menu.Role("BranchName"));
        if (name && b)
            name.SetText(OZL_Text.Upper(b.Name));
        m_HudDirty = true;
        m_HudTries = 0;
    }

    override void OnSelect(OZL_TreeMenu menu, OZL_NodeView node, string status, bool canResearch)
    {
        if (!node)
            return;
        TextWidget stat = TextWidget.Cast(menu.Role("CardStatus"));
        if (stat)
            stat.SetText(OZL_Text.Upper(StatusText(status)));

        // Рядок заголовка зі стрілкою ховається разом із написом, що сховало меню.
        Follow(menu, "SopItemsHeadRow", "CardItemsHead");
        Follow(menu, "SopOpensHeadRow", "CardOpensHead");

        // Рядок часу: у проєкті -- «Лишилось» + годинник + «з ...» (47 заввишки).
        bool going = status == "researching";
        ShowRole(menu, "CardTime", !going);
        ShowRole(menu, "SopTimeLeft", going);
        ShowRole(menu, "SopTimeTail", going);
        float h = 34;
        if (going)
            h = 47;
        // Лише висота: HeightUnits лишає ширину рядка стосу (370) як є.
        menu.HeightUnits(menu.Role("SopTimeRow"), h);
        m_TimerLeft = -1;
        m_TimerTries = 0;
        RefreshCard(menu);
    }

    // Позивний перемикає гілки по колу, коли їх більше однієї (у мокапі гілка одна).
    override bool OnClick(OZL_TreeMenu menu, Widget w)
    {
        if (!w || w.GetName() != "SopBranchNext")
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
        CrtTick(menu);
        BlinkTick();
        HoverTick(menu);
        ChipHoverTick();
        PriceTick(menu);
        PoolTick(menu);
        HudTick(menu);
        ChipTick(menu);
        TimerTick(menu);
        FogTick(menu);
        LabelTick(menu);
    }

    // ------------------------------------------------------------------
    // Кожен кадр
    // ------------------------------------------------------------------

    // Мерехтіння: crt-flicker мокапа, 3.2 с, steps(1) -- 1 до 47 %, .86 до 48 %,
    // 1 до 81 %, .93 до 82 %, далі 1. Провал -- 32 мс, тож кадр, що перескочив
    // його, однаково показує провал. Мерехтить скло (#stage::after): кути й
    // рядки. Смуга розгортки: crt-roll, від -160 до 900 за 7 с.
    private void CrtTick(OZL_TreeMenu menu)
    {
        float t = Math.ModFloat(m_Clock, 3.2);
        float alpha = 1;
        if (t >= 1.504 && t < 1.536)
            alpha = 0.86;
        else if (t >= 2.592 && t < 2.624)
            alpha = 0.93;
        else if (t > m_FlickerAt && m_FlickerAt < 1.504 && t >= 1.536)
            alpha = 0.86;
        else if (t > m_FlickerAt && m_FlickerAt < 2.592 && t >= 2.624)
            alpha = 0.93;
        m_FlickerAt = t;
        if (alpha != m_FlickerShown)
        {
            m_FlickerShown = alpha;
            Widget glass = menu.Role("CrtGlow");
            if (glass)
                glass.SetAlpha(alpha);
            Widget lines = menu.Role("CrtLines");
            if (lines)
                lines.SetAlpha(alpha);
        }
        Widget roll = menu.Role("CrtRoll");
        if (roll)
            menu.PlaceUnits(roll, 0, -160 + Math.ModFloat(m_Clock, 7) / 7 * 1060);
    }

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

    // Край вузла під мишею -- txt (.node:hover .cell); меню наведення не
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

    // Рамка чіпа «Відкриває» під мишею -- txt (.opens a:hover). Меню чіпів не
    // підсвічує; кнопку чіпа воно назвало open:<id>, її батько -- сам чіп.
    // Заглушка туману ChipHit не має і під мишу не потрапляє.
    private void ChipHoverTick()
    {
        Widget chip = null;
        Widget under = GetWidgetUnderCursor();
        if (under)
        {
            string nm = under.GetName();
            if (nm.IndexOf("open:") == 0)
                chip = under.GetParent();
        }
        if (chip == m_ChipLit)
            return;
        if (m_ChipLit)
            TintChip(m_ChipLit, EdgeColor);
        m_ChipLit = chip;
        if (chip)
            TintChip(chip, Txt);
    }

    private static void TintChip(Widget chip, int color)
    {
        Tint(chip, "ChipTopLine", color);
        Tint(chip, "ChipBottomLine", color);
        Tint(chip, "ChipLeftEdge", color);
        Tint(chip, "ChipRightEdge", color);
    }

    private void PriceTick(OZL_TreeMenu menu)
    {
        for (int i = m_Prices.Count() - 1; i >= 0; i--)
        {
            Widget cell = m_Prices[i];
            bool last = m_PriceTries[i] >= TRIES;
            if (!cell || CenterPrice(menu, cell, last))
            {
                m_Prices.Remove(i);
                m_PriceTries.Remove(i);
                continue;
            }
            m_PriceTries[i] = m_PriceTries[i] + 1;
        }
    }

    // Ціна по центру під вузлом (.price text-align: center): меню кладе чіпи
    // зліва в NodePrice (чіп 7 + 3 до числа, 6 між чіпами -- PRICE_LEAD і
    // PRICE_GAP), тож посередині стає сам контейнер. Висота -- та, що дала
    // розкладка (ozl_node_sop: .price мокапа, 96 під точкою вузла); зсуваємо
    // лише вбік. false -- текст ще не розкладено.
    private bool CenterPrice(OZL_TreeMenu menu, Widget cell, bool force)
    {
        Widget box = cell.FindAnyWidget("NodePrice");
        if (!box || !box.IsVisible() || !box.GetParent())
            return true;
        float px = menu.Px();
        float total = 0;
        int count = 0;
        Widget chip = box.GetChildren();
        while (chip)
        {
            TextWidget t = TextWidget.Cast(chip.FindAnyWidget("PriceText"));
            if (t && chip.IsVisible())
            {
                int pw;
                int ph;
                t.GetTextSize(pw, ph);
                if (pw <= 0 && !force)
                    return false;
                total += PRICE_LEAD + pw / px;
                count++;
            }
            chip = chip.GetSibling();
        }
        if (count > 1)
            total += PRICE_GAP * (count - 1);
        float bx;
        float by;
        float ox;
        float oy;
        box.GetScreenPos(bx, by);
        box.GetParent().GetScreenPos(ox, oy);
        menu.PlaceUnits(box, AnchorX - total / 2, (by - oy) / px);
        return true;
    }

    // Пул у HUD (.hud .pool): рядки поруч, справа до краю PoolList; ширина
    // рядка -- ширша з назви й числа. Проміжок 32 замість мокапових 18: без
    // шкали (118 одиниць на рядок) колонки вужчі, і з 18 вони злипались у
    // купку. Не влазять -- проміжки тіснішають до 6.
    private void PoolTick(OZL_TreeMenu menu)
    {
        if (!m_PoolDirty)
            return;
        Widget list = menu.Role("PoolList");
        if (!list)
        {
            m_PoolDirty = false;
            return;
        }
        float px = menu.Px();
        array<Widget> rows = new array<Widget>();
        array<float> widths = new array<float>();
        bool ready = true;
        float sum = 0;
        Widget row = list.GetChildren();
        while (row)
        {
            TextWidget name = TextWidget.Cast(row.FindAnyWidget("PoolName"));
            TextWidget value = TextWidget.Cast(row.FindAnyWidget("PoolValue"));
            if (name && value && row.IsVisible())
            {
                int nw;
                int nh;
                int vw;
                int vh;
                name.GetTextSize(nw, nh);
                value.GetTextSize(vw, vh);
                if (nw <= 0 || vw <= 0)
                    ready = false;
                float w = Math.Max(nw / px, vw / px);
                rows.Insert(row);
                widths.Insert(w);
                sum += w;
            }
            row = row.GetSibling();
        }
        if (!ready && m_PoolTries < TRIES)
        {
            m_PoolTries++;
            return;
        }
        m_PoolDirty = false;
        int count = rows.Count();
        if (count == 0)
            return;
        float boxW;
        float boxH;
        menu.UnitsOf(list, boxW, boxH);
        float gapW = 32;
        if (count > 1 && sum + gapW * (count - 1) > boxW)
            gapW = Math.Max(6, (boxW - sum) / (count - 1));
        // Не влізли й з 6: від лівого краю PoolList, а не поверх позивного.
        float x = Math.Max(0, boxW - sum - gapW * (count - 1));
        for (int i = 0; i < count; i++)
        {
            menu.PlaceUnits(rows[i], x, 0);
            x += widths[i] + gapW;
        }
    }

    // HUD: BranchSub через 30 за ширшим із двох рядків позивного (.call), а з
    // кількома гілками -- ще й знак «▸» після назви і кнопка на весь позивний.
    private void HudTick(OZL_TreeMenu menu)
    {
        if (!m_HudDirty)
            return;
        TextWidget dev = TextWidget.Cast(menu.Role("DevName"));
        TextWidget name = TextWidget.Cast(menu.Role("BranchName"));
        if (!dev || !name)
        {
            m_HudDirty = false;
            return;
        }
        int dw;
        int dh;
        int nw;
        int nh;
        dev.GetTextSize(dw, dh);
        name.GetTextSize(nw, nh);
        if ((dw <= 0 || nw <= 0) && m_HudTries < TRIES)
        {
            m_HudTries++;
            return;
        }
        m_HudDirty = false;
        float px = menu.Px();
        float nameW = nw / px;
        float callW = Math.Max(dw / px, nameW);
        bool many = menu.BranchCount() > 1;
        Widget mark = menu.Role("SopBranchMark");
        if (mark)
        {
            mark.Show(many);
            if (many)
            {
                menu.PlaceUnits(mark, 27 + nameW + 4, 49);
                callW = Math.Max(callW, nameW + 4 + 16);
            }
        }
        Widget next = menu.Role("SopBranchNext");
        if (next)
        {
            next.Show(many);
            if (many)
                menu.SizeUnits(next, callW, 67);
        }
        menu.PlaceUnits(menu.Role("BranchSub"), 27 + callW + 30, 40.5);
    }

    // «Відкриває» (.opens): чіпи зліва направо через CHIP_GAP з переносом на
    // ширині CardOpensList, кожен -- CHIP_PAD + текст + CHIP_PAD у рамці
    // CHIP_EDGE, заввишки зі свій рядок (ozl_sop_opens_chip). Меню розкладає їх
    // своїм кроком (текст + 4) і тягне кнопку open:<id> лише на свою ширину;
    // тут -- за мокапом, після нього (OnUpdate іде після RunFlows), і кнопку теж,
    // бо інакше праві 8 одиниць рамки не клацались і не світились.
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
                chips.Insert(chip);
                widths.Insert(2 * CHIP_PAD + tw / px);
            }
            chip = chip.GetSibling();
        }
        float rowW;
        float listH;
        menu.UnitsOf(list, rowW, listH);
        if ((!ready || rowW <= 0) && m_ChipTries < TRIES)
        {
            m_ChipTries++;
            return;
        }
        // Двічі: якщо меню розкладе чіпи своїм кроком кадром пізніше, друга
        // розкладка його виправить.
        m_ChipPasses--;
        if (m_ChipPasses <= 0)
            m_ChipsDirty = false;
        float x = 0;
        float y = 0;
        float chipH = 0;
        for (int i = 0; i < chips.Count(); i++)
        {
            Widget c = chips[i];
            float cw;
            float ch;
            menu.UnitsOf(c, cw, ch);
            if (ch > chipH)
                chipH = ch;
            float w = widths[i];
            if (x > 0 && x + w > rowW)
            {
                x = 0;
                y += chipH + CHIP_GAP;
            }
            menu.PlaceUnits(c, x, y);
            Widget hit = HitOf(c);
            if (hit)
                menu.SizeUnits(hit, w, ch);
            Resize(menu, c, "ChipTopLine", w, CHIP_EDGE);
            Resize(menu, c, "ChipBottomLine", w, CHIP_EDGE);
            Widget right = c.FindAnyWidget("ChipRightEdge");
            if (right)
                menu.PlaceUnits(right, w - CHIP_EDGE, 0);
            x += w + CHIP_GAP;
        }
        float h = 0;
        if (chips.Count() > 0)
            h = y + chipH;
        // Лише висота: HeightUnits лишає ширину рядка стосу (370) як є.
        menu.HeightUnits(list, h);
        RefreshCard(menu);
    }

    // Кнопка чіпа: меню перейменовує ChipHit на open:<id> ще до PaintOpenChip
    // (OZL_TreeMenu.OpenChip), тож шукаємо за початком імені серед дітей; у
    // заглушки туману вона лишається ChipHit (схована).
    private static Widget HitOf(Widget chip)
    {
        Widget c = chip.GetChildren();
        while (c)
        {
            string nm = c.GetName();
            if (nm.IndexOf("open:") == 0)
                return c;
            c = c.GetSibling();
        }
        return chip.FindAnyWidget("ChipHit");
    }

    // Годинник проєкту (.tmr): у 7segment нема двокрапки, тож групи
    // OZL_Text.Clock -- у SopTimerG0..2, між ними спрайти SopTimerC0..1; за
    // «Лишилось» через пробіл, далі «з 1 хв 00 с».
    private void TimerTick(OZL_TreeMenu menu)
    {
        OZL_NodeView n = menu.NodeOf(menu.SelectedId());
        if (!n || n.Status != "researching")
            return;
        int left = menu.LeftOf(n);
        if (left == m_TimerLeft)
            return;
        TextWidget word = TextWidget.Cast(menu.Role("SopTimeLeft"));
        Widget clockBox = menu.Role("CardTimer");
        if (!word || !clockBox)
            return;
        int ww;
        int wh;
        word.GetTextSize(ww, wh);
        if (ww <= 0 && m_TimerTries < TRIES)
        {
            m_TimerTries++;
            return;
        }
        m_TimerLeft = left;
        string clock = OZL_Text.Clock(left);
        array<string> parts = new array<string>();
        clock.Split(":", parts);
        float x = 0;
        for (int g = 0; g < 3; g++)
        {
            TextWidget digits = TextWidget.Cast(menu.Role("SopTimerG" + g.ToString()));
            bool used = g < parts.Count();
            if (digits)
            {
                digits.Show(used);
                if (used)
                {
                    digits.SetText(parts[g]);
                    menu.PlaceUnits(digits, x, 0);
                    x += parts[g].Length() * DIGIT;
                }
            }
            Widget colon = menu.Role("SopTimerC" + g.ToString());
            bool between = g + 1 < parts.Count();
            if (colon)
            {
                colon.Show(between);
                if (between)
                {
                    menu.PlaceUnits(colon, x, 0);
                    x += COLON;
                }
            }
        }
        float at = ww / menu.Px() + SPACE;
        menu.PlaceUnits(clockBox, at, 17.2);
        TextWidget tail = TextWidget.Cast(menu.Role("SopTimeTail"));
        if (tail)
        {
            string rest = "";
            if (n.Duration > 0)
                rest = OZL_Text.Words("STR_OZL_TREE_OF") + " " + OZL_Text.Duration(n.Duration);
            tail.SetText(rest);
            menu.PlaceUnits(tail, at + x + SPACE, 20.23);
        }
    }

    // Смужки туману (135 градусів, txt 4 %) -- під переходом TreeFogEdge, на
    // його прямокутнику: видно їх лише крізь перехід, як у мокапі.
    private void FogTick(OZL_TreeMenu menu)
    {
        Widget stripes = menu.Role("SopFogStripes");
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
        float x = (ex - cx) / menu.Px();
        bool same = Math.AbsFloat(x - m_FogX) < 0.5 && Math.AbsFloat(ew - m_FogW) < 0.5 && Math.AbsFloat(eh - m_FogH) < 0.5;
        if (same && stripes.IsVisible())
            return;
        m_FogX = x;
        m_FogW = ew;
        m_FogH = eh;
        menu.PlaceUnits(stripes, x, 0);
        menu.SizeUnits(stripes, ew, eh);
        stripes.Show(true);
    }

    // WORKAROUND (скіл gui-layouts.md §32; прибрати, коли рушій виправлять --
    // разом зі спільними частинами ozl_sop_or_label / ozl_sop_price_chip у
    // make-описі). Рушій віддавав за шляхом ozl_sop_or_label розкладку чіпа ціни
    // (стенд 2026-10-31, двічі на свіжому клієнті; копія під іншою назвою
    // вантажилась правильно), тож обидві розкладки несуть обидві частини, а тут
    // рядок «АБО» -- прямий нащадок TreeNodes із власним OrText -- показує напис
    // і ховає квадрат із числом, байдуже, яку з двох розкладок дав рушій. Чіпи
    // цін лежать глибше, у NodePrice комірки, і їхній OrText лишається схованим.
    private void LabelTick(OZL_TreeMenu menu)
    {
        Widget nodes = menu.Role("TreeNodes");
        if (!nodes)
            return;
        Widget c = nodes.GetChildren();
        while (c)
        {
            Widget orText = ChildNamed(c, "OrText");
            if (orText && !orText.IsVisible())
            {
                orText.Show(true);
                Widget dot = ChildNamed(c, "PriceChip");
                if (dot)
                    dot.Show(false);
                Widget amount = ChildNamed(c, "PriceText");
                if (amount)
                    amount.Show(false);
            }
            c = c.GetSibling();
        }
    }

    private static Widget ChildNamed(Widget w, string name)
    {
        Widget c = w.GetChildren();
        while (c)
        {
            if (c.GetName() == name)
                return c;
            c = c.GetSibling();
        }
        return null;
    }

    // ------------------------------------------------------------------
    // Дрібниці
    // ------------------------------------------------------------------

    // Розрядка (letter-spacing) пробілами. TextWidget.SetTextSpacing і
    // "text spacing" розкладки рушій не малює -- ні бітмаповим, ні SDF-шрифтам,
    // ні ванільному Metron (стенд 2026-10-31: та сама ширина тексту й та сама
    // картинка за 0, 7 і 20). Пробіл Oswald -- .23 em, як розрядка кнопки
    // (.24em), «ЦІЛЬ» (.3em), тирів (.2em) і заголовків розділів (.16em), тож
    // між літерами йде звичайний пробіл; вужчу розрядку (.04-.14em) так не
    // зробити, і там її нема. Літери замінюються цілими рядками, як в
    // OZL_Text.Upper: різати UTF-8 по байтах не можна.
    private static ref array<string> s_Letters;

    static string Spread(string text)
    {
        if (!s_Letters)
        {
            s_Letters = new array<string>();
            string all = "А Б В Г Ґ Д Е Є Ж З И І Ї Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ь Ю Я ";
            all += "а б в г ґ д е є ж з и і ї й к л м н о п р с т у ф х ц ч ш щ ь ю я ";
            all += "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z ";
            all += "a b c d e f g h i j k l m n o p q r s t u v w x y z 0 1 2 3 4 5 6 7 8 9";
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

    // Стос картки змінився: оновити його, а тоді прокрутку (як RefreshCard
    // меню: прокрутка сама не бачить, що стос виріс).
    private static void RefreshCard(OZL_TreeMenu menu)
    {
        Widget flow = menu.Role("CardFlow");
        if (flow)
            flow.Update();
        Widget scroll = menu.Role("CardScroll");
        if (scroll)
            scroll.Update();
    }

    private static void Resize(OZL_TreeMenu menu, Widget root, string name, float width, float height)
    {
        Widget w = root.FindAnyWidget(name);
        if (w)
            menu.SizeUnits(w, width, height);
    }
}

#endif
