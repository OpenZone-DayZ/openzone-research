// Вікно ecolog -- «Науковий термінал»: світлий лабораторний корпус навколо
// темного екрана з чотирьох плашок. Угорі шапка (назва, пристрій, гілка);
// під нею ряд приладів-показників пулу (назва лінії, велике число, колір
// лінії); посередині дерево вправо шестикутними датчиками на сітці 24; унизу
// на всю ширину -- протокол вузла в п'ять колонок (назва і статус, опис,
// вартість, тривалість з «Відкриває», кнопка з причиною).
//
// Розкладки: ozl_tree_ecolog, ozl_node_ecolog (ui/OpenZone_Research/);
// картинки: source/ui/ecolog/ (набір ozl_ecolog і текстури
// gui/textures/tree/ecolog/); кольори й шрифти: ui/tokens/ecolog.json. Числа
// кольорів нижче -- ті самі токени в ARGB. Шрифт -- ванільний Metron (howto
// мокапа; сам мокап малює на його місці Bahnschrift). Числа розкладки скін
// читає з віджетів (OnShow), а не тримає копій; сталі нижче -- лише міри
// шрифту й власні відступи скіна, яких розкладка не має.
//
// Понад дані клас робить:
// - великі літери (OZL_Text.Upper) і розрядку пробілами там, де мокап пише
//   letter-spacing від .16em (Spread: заголовки розділів, кнопка, тири) --
//   SetTextSpacing рушій не малює зовсім (скіл gui-layouts §32); назву й
//   пристрій (.14em) -- картинками мови гравця (рядки *_IMG), живі написи --
//   запас;
// - вузол: заливку шестикутника за статусом (NodeFill), шестерню мокапа,
//   коли значка нема, мітку проєкту, що блимає, ціну по центру під вузлом,
//   підкреслену назву вибраного (.node.sel .lbl);
// - прилади пулу -- власні (EcoPool0..): меню дає лінії через PaintPoolRow
//   у сховані рядки, а скін малює їх у приладах і ділить ширину порівну;
// - підписи тирів -- власні (EcoTier0..): точка на тирі, напис по центру;
// - протокол: «Лишилось» + годинник жирним + «з ...», рамки чіпів
//   «Відкриває» (пунктирні в заглушки туману), кнопку з причиною, притиснуті
//   донизу;
// - шапку: кнопку «Закрити», якої мокап не має, -- зліва від гілки, і
//   перемикач гілок (клік по назві гілки), коли їх кілька;
// - кириличну І даних -- латинською (DataText): ванільний Metron її не має
//   (скіл gui-layouts §25), а латинська виглядає так само.
//
// Рушій змішує кольори в ЛІНІЙНОМУ світлі (скіл §32): напівпрозоре виходить
// світлішим, ніж у мокапі. Тож альфи тут -- уже переведені: тьмяна лінія .4
// замість .6, сітка 5/255 замість .08, мерехтіння мітки .38 / .065 замість
// .6 / .2; сяйво дерева запечене непрозорим.

#ifndef NO_GUI

class OZL_TreeSkin_Ecolog : OZL_TreeSkin
{
    static const string SET    = "set:ozl_ecolog image:";
    static const string COMMON = "set:ozl_common image:";
    // Значок вузла без свого: шестерня, як iconOf() мокапа (ванільний dayz_gui).
    static const string GEAR   = "set:dayz_gui image:gear";

    // Скільки кадрів чекати, поки текст розкладеться (як LATER_TRIES меню).
    static const int   TRIES     = 12;
    // Міри шрифту: пробіл Metron22 при 14 (ціна: хвіст «+N предм.» -- той
    // самий рядок тексту через пробіл), пробіл Metron28 при 16 (рядок часу);
    // кожен наступний рядок причини (SDF Metron при 13) додає 13.
    static const float PRICE_SP  = 3.2;
    static const float SPACE     = 4;
    static const float WHY_LINE  = 13;
    // Власні відступи скіна (мокап не має ні кнопки «Закрити», ні знака
    // гілок): кнопка -- за 30 від ширшого з двох рядків гілки; знак -- за 6
    // перед назвою гілки.
    static const float CLOSE_GAP = 30;
    static const float MARK_GAP  = 6;

    // Кольори мокапа, яких нема в базовому класі (color-mix його CSS).
    int Faint;       // --faint: закритий вузол, неактивна кнопка, нуль пулу
    int Track;       // --track: порожні сегменти, доріжки смуг
    int EdgeColor;   // --edge: рамки плашок, кнопки, чіпів
    int Cell;        // --cell: середина шестикутника
    int DoneBg;      // --done-bg: середина дослідженого
    int ItemChip;    // квадратик рядка матеріалу (#9a957f мокапа)

    private static ref array<string> s_Letters;

    // Числа розкладки, прочитані з віджетів в OnShow (одиниці).
    private int    m_Pools;       // приладів пулу EcoPool<i>
    private int    m_Tiers;       // підписів тирів EcoTier<i>
    private float  m_PoolW;       // ряд приладів (EcoPools)
    private float  m_PoolGap;     // між приладами
    private float  m_PoolH;       // прилад
    private float  m_PoolEdgeW;   // правий край приладу
    private float  m_PoolChipR;   // квадратик лінії: від правого краю
    private float  m_PoolChipY;
    private float  m_HeadRight;   // правий край тексту гілки
    private float  m_CloseY;
    private float  m_CloseH;
    private float  m_ClosePad;    // поле слова в кнопці «Закрити»
    private float  m_MarkY;
    private float  m_MarkW;
    private float  m_NextY;
    private float  m_NextH;
    private float  m_BtnY;        // кнопка протоколу, коли причина в один рядок
    private float  m_WhyY;
    private float  m_WhyH;        // висота одного рядка причини

    private float  m_Clock;
    private int    m_BlinkStep;
    private ref array<Widget> m_Blink;
    private ref array<Widget> m_Prices;
    private ref array<int>    m_PriceTries;
    private bool   m_ChipsDirty;
    private int    m_ChipTries;
    private int    m_ChipPasses;
    private int    m_TimerLeft;
    private int    m_TimerTries;
    private float  m_FogX;
    private float  m_FogW;
    private float  m_FogH;
    private bool   m_HeadDirty;
    private int    m_HeadTries;
    private bool   m_CloseLit;
    private int    m_WhyLines;
    private int    m_PoolCount;
    private bool   m_PoolWarned;
    private bool   m_TierWarned;
    private Widget m_SelCell;
    private int    m_SelW0;
    private int    m_SelW1;

    void OZL_TreeSkin_Ecolog()
    {
        Named("ecolog");
        Dir     = "right";
        NodeW   = 60;
        NodeH   = 60;
        Keep    = 78;
        Row     = 240;
        Col     = 150;
        Top     = 90;
        Side    = 10;
        // Точка вузла в комірці 150x120 (ozl_node_ecolog): центр шестикутника.
        AnchorX = 75;
        AnchorY = 36;

        Txt       = ARGB(255, 212, 236, 245);
        Dim       = ARGB(255, 111, 147, 163);
        Acc       = ARGB(255,  73, 194, 240);
        Ok        = ARGB(255, 114, 219, 160);
        Bad       = ARGB(255, 255, 123, 107);
        // Мокап: dim 60 % над екраном; у лінійному світлі той самий вигляд дає .4.
        LineDim   = ARGB(102, 111, 147, 163);
        LineLit   = Txt;
        LineHl    = Acc;
        Lcd       = ARGB(255,  11,  26,  34);
        FogColor  = ARGB(255,  10,  24,  31);
        Faint     = ARGB(255,  86, 116, 129);
        Track     = ARGB(255,  30,  41,  47);
        EdgeColor = ARGB(255,  36,  65,  78);
        Cell      = ARGB(255,  22,  33,  39);
        DoneBg    = ARGB(255,  26,  50,  46);
        ItemChip  = ARGB(255, 154, 149, 127);

        // Сітка екрана (.content .bg мокапа: --grid, --grid-step 24): смужка в 1
        // одиницю на початку кожної клітинки -- лінія з центром на 0.5. Мокап:
        // rgba(120,200,240,.08) над екраном = (20,40,50); у лінійному світлі
        // це альфа 5/255 (з .08 на стенді вийшло (36,66,80)).
        GridStep  = 24;
        GridColor = ARGB(5, 120, 200, 240);
        GridX     = 0.5;
        GridY     = 0.5;

        // Шестикутник -- одна картинка, тонована статусом (--st мокапа);
        // середину (NodeFill) фарбує PaintNode.
        Shapes.Insert(SET + "hex_edge");   // 0
        ShapeColors.Set("locked", Faint);
        ShapeColors.Set("short", Bad);
        ShapeColors.Set("available", Acc);
        ShapeColors.Set("researching", Acc);
        ShapeColors.Set("completed", Ok);

        // Мітки: замок / галка / крапка (спека §3) -- спільні фігури ozl_common.
        Marks.Insert(COMMON + "mark_lock");
        Marks.Insert(COMMON + "mark_check");
        Marks.Insert(COMMON + "mark_dot");

        SegOn   = Acc;
        SegOff  = Track;
        TipPadX = 10;   // рамка 1 + поле 9 (.tip мокапа)
        // Чіпи «Відкриває»: 8 поля після тексту + рамка 1 (.opens a), через 6.
        OpensGap = 6;
        OpensPad = 9;

        m_Blink      = new array<Widget>();
        m_Prices     = new array<Widget>();
        m_PriceTries = new array<int>();
        m_BlinkStep  = -1;
        m_TimerLeft  = -1;
        m_WhyLines   = -1;
    }

    // ------------------------------------------------------------------
    // Тексти
    // ------------------------------------------------------------------

    // Кожен текст із конфігу проходить тут останнім кроком: кирилична велика І
    // (U+0406, байти D0 86) стає латинською I -- ванільні Metron її не мають.
    // Заміна двобайтової літери однобайтовою безпечна: провідний байт D0 ніколи
    // не стоїть на місці байта продовження (як OZL_Text.Upper).
    override string DataText(string text)
    {
        string t = text;
        t.Replace("І", "I");
        return t;
    }

    // Розділи протоколу -- великими й розряджено (.sec: uppercase, .16em);
    // «◆ » перед ними -- спрайт sec_diamond.
    override string SectionText(string key)
    {
        return Spread(OZL_Text.Upper(OZL_Text.Words(key)));
    }

    // Статус у протоколі -- великими (.cstat: uppercase; .12em -- без розрядки).
    override string CardStatusText(string status)
    {
        return OZL_Text.Upper(StatusText(status));
    }

    // Слово кнопки -- великими й розряджено (.go: uppercase, .18em).
    override string ButtonText(string status, bool enabled)
    {
        return Spread(OZL_Text.Upper(super.ButtonText(status, enabled)));
    }

    // «тир I» розряджено (.tierlab .2em); підписи -- власні (PlaceTiers).
    override string TierText(int tier)
    {
        return Spread(super.TierText(tier));
    }

    // ------------------------------------------------------------------
    // Вузол
    // ------------------------------------------------------------------

    // Доступний вузол мокап виділяє самим краєм шестикутника (acc), окремого
    // кільця нема.
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

    override void PaintNode(OZL_TreeMenu menu, Widget cell, OZL_NodeView node, string status, bool selected)
    {
        super.PaintNode(menu, cell, node, status, selected);

        // Середина шестикутника (.cell::before): cell, у дослідженого -- done-bg.
        Widget fill = cell.FindAnyWidget("NodeFill");
        if (fill)
        {
            if (status == "completed")
                fill.SetColor(DoneBg);
            else
                fill.SetColor(Cell);
        }

        // Без свого значка (чи свій не завантажився) -- шестерня, як мокап.
        ImageWidget icon = ImageWidget.Cast(cell.FindAnyWidget("NodeIcon"));
        if (icon && !icon.IsVisible() && icon.LoadImageFile(0, GEAR))
        {
            icon.SetImage(0);
            icon.SetColor(IconColorOf(status));
            icon.Show(true);
        }

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

        // Вибраний -- підкреслена назва (.node.sel .lbl), кольором назви; риски
        // на ширину рядків ставить SelTick, щойно текст розкладено.
        Tint(cell, "NodeUnder0", NameColorOf(status));
        Tint(cell, "NodeUnder1", NameColorOf(status));
        if (selected)
        {
            m_SelCell = cell;
            m_SelW0 = -1;
            m_SelW1 = -1;
        }
        else if (cell == m_SelCell)
        {
            m_SelCell = null;
        }

        // Ціну меню покладе слідом -- поставити й центрувати, коли її текст
        // розкладеться.
        if (IndexIn(m_Prices, cell) < 0)
        {
            m_Prices.Insert(cell);
            m_PriceTries.Insert(0);
        }
    }

    // ------------------------------------------------------------------
    // Пул, протокол, кнопка
    // ------------------------------------------------------------------

    // Лінія пулу: меню створило для неї рядок у СХОВАНОМУ PoolList -- скін
    // малює її у приладі EcoPool<index> (.prow): назва великими (тьмяна),
    // число -- txt, нуль -- faint (.prow.zero), квадратик кольору лінії.
    // Ширину й місце приладам дає OnPaint. Ліній більше, ніж приладів, --
    // зайві не видно, і про це раз на вікно каже лог.
    override void PaintPoolRow(OZL_TreeMenu menu, Widget row, int index, string line, int have, int color)
    {
        if (index < 0)
            return;
        if (index >= m_Pools)
        {
            if (!m_PoolWarned)
            {
                m_PoolWarned = true;
                OZL_Log.Warn("tree: ecolog: more pool lines than the " + m_Pools.ToString() + " instruments of ozl_tree_ecolog (EcoPool<n>) -- the rest are not shown");
            }
            return;
        }
        string slot = "EcoPool" + index.ToString();
        TextWidget name = TextWidget.Cast(menu.Role(slot + "Name"));
        if (name)
            name.SetText(DataText(OZL_Text.Upper(menu.PointName(line))));
        TextWidget value = TextWidget.Cast(menu.Role(slot + "Value"));
        if (value)
        {
            value.SetText(have.ToString());
            if (have > 0)
                value.SetColor(Txt);
            else
                value.SetColor(Faint);
        }
        Widget chip = menu.Role(slot + "Chip");
        if (chip)
            chip.SetColor(color);
        if (index + 1 > m_PoolCount)
            m_PoolCount = index + 1;
    }

    // Рядок вартості (.crow): у рядка матеріалу квадратик #9a957f мокапа, а не
    // тьмяний.
    override void PaintCostRow(OZL_TreeMenu menu, Widget row, string label, string text, int verdict)
    {
        super.PaintCostRow(menu, row, label, text, verdict);
        Widget items = menu.Role("CardItemList");
        Widget chip = row.FindAnyWidget("CostChip");
        if (chip && items && row.GetParent() == items)
            chip.SetColor(ItemChip);
    }

    // Чіп «Відкриває» в рамці 1 (.opens a); заглушка туману -- faint і рамка
    // пунктиром (.opens a.fogged). Розкладає чіпи меню; рамку на ширину чіпа
    // ставить OnUpdate.
    override void PaintOpenChip(OZL_TreeMenu menu, Widget chip, string text, bool fogged)
    {
        super.PaintOpenChip(menu, chip, text, fogged);
        if (fogged)
        {
            Widget t = chip.FindAnyWidget("ChipText");
            if (t)
                t.SetColor(Faint);
        }
        ShowIn(chip, "ChipTop", !fogged);
        ShowIn(chip, "ChipBottom", !fogged);
        ShowIn(chip, "ChipLeft", !fogged);
        ShowIn(chip, "ChipRight", !fogged);
        ShowIn(chip, "ChipDashTop", fogged);
        ShowIn(chip, "ChipDashBottom", fogged);
        ShowIn(chip, "ChipDashLeft", fogged);
        ShowIn(chip, "ChipDashRight", fogged);
        m_ChipsDirty = true;
        m_ChipTries = 0;
        m_ChipPasses = 2;
    }

    // Рамка чіпа «Відкриває» під мишею -- txt (.opens a:hover).
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

    // .go: доступна -- acc і acc-рамка 2, неактивна -- faint і рамка --edge.
    // Слово ставить меню (ButtonText); те саме слово -- на BtnResearchHover
    // (acc, слово кольору екрана), який меню показує під мишею.
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
        TextWidget hover = TextWidget.Cast(menu.Role("EcoBtnHoverText"));
        if (hover)
            hover.SetText(ButtonText(status, enabled));
        TintRole(menu, "EcoBtnTop", edge);
        TintRole(menu, "EcoBtnBottom", edge);
        TintRole(menu, "EcoBtnLeft", edge);
        TintRole(menu, "EcoBtnRight", edge);
    }

    // ------------------------------------------------------------------
    // Події
    // ------------------------------------------------------------------

    override void OnShow(OZL_TreeMenu menu)
    {
        ReadLayout(menu);

        // Точка тиру -- 1 x 1, її напис висить за її краєм; панель, як і рамка,
        // ріже дітей по своєму краю, поки не сказано інакше (стенд 2026-10-31:
        // від «тир III» лишалась крапка в 1 піксель, від «тир I» -- нічого).
        for (int i = 0; i < m_Tiers; i++)
        {
            Widget point = menu.Role("EcoTier" + i.ToString());
            if (point)
                point.ClearFlags(WidgetFlags.CLIPCHILDREN);
        }

        // Назва і пристрій -- картинки мови гравця з розрядкою мокапа (.title,
        // .dev: .14em; рядки *_IMG). Рядок не називає картинки -- живі написи
        // великими (без розрядки: пробіл Metron ширший за всю розрядку мокапа),
        // пристрій через 18 за назвою за шириною тексту.
        bool pics = Picture(menu, "EcoTitleImg", OZL_Text.Words("STR_OZL_SKIN_ECOLOG_TITLE_IMG"));
        if (pics)
            pics = Picture(menu, "EcoDevImg", OZL_Text.Words("STR_OZL_SKIN_ECOLOG_DEV_IMG"));
        ShowRole(menu, "EcoTitleImg", pics);
        ShowRole(menu, "EcoDevImg", pics);
        ShowRole(menu, "EcoTitleRow", !pics);
        if (!pics)
        {
            SetUpper(menu, "EcoTitle", "STR_OZL_SKIN_ECOLOG_TITLE");
            SetUpper(menu, "DevName", "STR_OZL_SKIN_ECOLOG_DEV");
            menu.FlowLater(menu.Role("EcoTitleRow"), 18, 0, false);
        }
        SetUpper(menu, "BtnCloseText", "STR_OZL_TREE_CLOSE");

        // Вертикальне «Бали» -- картинка мовою гравця (рядок stringtable каже, яка).
        Picture(menu, "EcoPoolLabel", OZL_Text.Words("STR_OZL_SKIN_ECOLOG_POOL_VERTICAL_IMG"));

        // Легенда -- рядком через 14 за шириною текстів.
        menu.FlowLater(menu.Role("LegendRow"), 14, 0, false);

        m_Clock = 0;
        m_BlinkStep = -1;
        m_TimerLeft = -1;
        m_WhyLines = -1;
        m_PoolCount = 0;
        m_PoolWarned = false;
        m_TierWarned = false;
        m_HeadDirty = true;
        m_HeadTries = 0;
        m_CloseLit = false;
        m_SelCell = null;
        m_Blink.Clear();
        m_Prices.Clear();
        m_PriceTries.Clear();
    }

    // Гілка великими (.bname); прилади пулу -- порівну по ширині ряду; підписи
    // тирів.
    override void OnPaint(OZL_TreeMenu menu)
    {
        OZL_BranchView b = menu.CurrentBranch();
        TextWidget name = TextWidget.Cast(menu.Role("BranchName"));
        if (name && b)
            name.SetText(DataText(OZL_Text.Upper(b.Name)));
        LayPool(menu);
        PlaceTiers(menu, b);
        m_HeadDirty = true;
        m_HeadTries = 0;
    }

    override void OnSelect(OZL_TreeMenu menu, OZL_NodeView node, string status, bool canResearch)
    {
        if (!node)
        {
            // .empty: риска зліва від блоку, блок -- завширшки з підказку + 19.
            Widget box = menu.Role("EcoEmptyBox");
            if (box)
                menu.FitLater(TextWidget.Cast(menu.Role("CardEmptyHint")), box, 19, 2);
            return;
        }

        // Рядок заголовка з ромбиком ховається разом із написом, що сховало меню.
        Follow(menu, "EcoItemsHeadRow", "CardItemsHead");
        Follow(menu, "EcoOpensHeadRow", "CardOpensHead");

        // Рядок часу: у проєкті -- «Лишилось» + годинник жирним + «з ...».
        bool going = status == "researching";
        ShowRole(menu, "CardTime", !going);
        ShowRole(menu, "EcoTimeLeft", going);
        ShowRole(menu, "EcoTimeTail", going);
        m_TimerLeft = -1;
        m_TimerTries = 0;

        UpdateRole(menu, "EcoCostStack");
        UpdateRole(menu, "EcoTimeStack");
        m_WhyLines = -1;
    }

    // Назва гілки перемикає гілки по колу, коли їх більше однієї (у мокапі гілка
    // одна, тож і перемикача нема).
    override bool OnClick(OZL_TreeMenu menu, Widget w)
    {
        if (!w || w.GetName() != "EcoBranchNext")
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
        PriceTick(menu);
        ChipTick(menu);
        TimerTick(menu);
        FogTick(menu);
        SelTick(menu);
        HeadTick(menu);
        CloseHoverTick(menu);
        FootTick(menu);
    }

    // ------------------------------------------------------------------
    // Числа розкладки (OnShow)
    // ------------------------------------------------------------------

    // Що скін ставить сам, ставиться за числами самої розкладки: їх
    // прочитано тут, до першого малювання, поки віджети стоять, як у файлі.
    // Get* дають екранні пікселі (скіл gui-layouts: «every position and size
    // API is in SCREEN PIXELS»); одиниця -- висота екрана / 1080, як у меню.
    private void ReadLayout(OZL_TreeMenu menu)
    {
        int sw;
        int sh;
        GetScreenSize(sw, sh);
        float s = 1;
        if (sh > 0)
            s = sh / 1080.0;

        m_Pools = CountRoles(menu, "EcoPool", "");
        m_Tiers = CountRoles(menu, "EcoTier", "Text");

        float x;
        float y;
        float w;
        float h;
        float x1;
        float y1;
        UnitsSize(menu.Role("EcoPools"), s, m_PoolW, h);
        Widget pool = menu.Role("EcoPool0");
        UnitsPos(pool, s, x, y);
        UnitsSize(pool, s, w, m_PoolH);
        UnitsPos(menu.Role("EcoPool1"), s, x1, y1);
        m_PoolGap = x1 - x - w;
        UnitsSize(menu.Role("EcoPool0EdgeR"), s, m_PoolEdgeW, h);
        UnitsPos(menu.Role("EcoPool0Chip"), s, x1, m_PoolChipY);
        m_PoolChipR = w - x1;

        Widget branch = menu.Role("BranchName");
        UnitsPos(branch, s, x, y);
        UnitsSize(branch, s, w, h);
        m_HeadRight = x + w;
        UnitsPos(menu.Role("BtnClose"), s, x, m_CloseY);
        UnitsSize(menu.Role("BtnClose"), s, w, m_CloseH);
        UnitsPos(menu.Role("BtnCloseText"), s, m_ClosePad, y);
        UnitsPos(menu.Role("EcoBranchMark"), s, x, m_MarkY);
        UnitsSize(menu.Role("EcoBranchMark"), s, m_MarkW, h);
        UnitsPos(menu.Role("EcoBranchNext"), s, x, m_NextY);
        UnitsSize(menu.Role("EcoBranchNext"), s, w, m_NextH);

        UnitsPos(menu.Role("EcoBtnBox"), s, x, m_BtnY);
        UnitsPos(menu.Role("CardWhy"), s, x, m_WhyY);
        UnitsSize(menu.Role("CardWhy"), s, w, m_WhyH);

        // Одним виразом рядок не складається: рушій каже "Formula too complex".
        string readLine = "tree: ecolog: layout read -- " + m_Pools.ToString() + " pool instruments, row " + m_PoolW.ToString() + " gap " + m_PoolGap.ToString();
        readLine = readLine + " height " + m_PoolH.ToString() + ", chip " + m_PoolChipR.ToString() + " from the right at " + m_PoolChipY.ToString();
        readLine = readLine + "; " + m_Tiers.ToString() + " tier labels; branch right edge " + m_HeadRight.ToString();
        readLine = readLine + ", close key at " + m_CloseY.ToString() + " x " + m_CloseH.ToString() + " pad " + m_ClosePad.ToString();
        readLine = readLine + "; button at " + m_BtnY.ToString() + ", reason at " + m_WhyY.ToString() + " x " + m_WhyH.ToString();
        OZL_Log.Dbg(readLine);
    }

    // Скільки віджетів <stem>0, <stem>1... (з суфіксом -- <stem>0<suffix>...).
    private static int CountRoles(OZL_TreeMenu menu, string stem, string suffix)
    {
        int n = 0;
        while (menu.Role(stem + n.ToString() + suffix))
            n++;
        return n;
    }

    private static void UnitsPos(Widget w, float s, out float x, out float y)
    {
        x = 0;
        y = 0;
        if (!w)
            return;
        w.GetPos(x, y);
        x = x / s;
        y = y / s;
    }

    private static void UnitsSize(Widget w, float s, out float width, out float height)
    {
        width = 0;
        height = 0;
        if (!w)
            return;
        w.GetSize(width, height);
        width = width / s;
        height = height / s;
    }

    // ------------------------------------------------------------------
    // Кожен кадр
    // ------------------------------------------------------------------

    // Мітка проєкту: blink 1 s steps(2) мокапа -- непрозорість 1, .6, .2, .6 по
    // чверті секунди; у лінійному світлі той самий вигляд над екраном дають
    // 1, .38, .065, .38.
    private void BlinkTick()
    {
        int step = Math.Floor(Math.ModFloat(m_Clock, 1) * 4);
        if (step == m_BlinkStep)
            return;
        m_BlinkStep = step;
        float a = 1;
        if (step == 1 || step == 3)
            a = 0.38;
        else if (step == 2)
            a = 0.065;
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

    private void PriceTick(OZL_TreeMenu menu)
    {
        for (int i = m_Prices.Count() - 1; i >= 0; i--)
        {
            Widget cell = m_Prices[i];
            bool last = m_PriceTries[i] >= TRIES;
            if (!cell || LayPrice(menu, cell, last))
            {
                m_Prices.Remove(i);
                m_PriceTries.Remove(i);
                continue;
            }
            m_PriceTries[i] = m_PriceTries[i] + 1;
        }
    }

    // Ціна під вузлом (.price): чіпи ліній рядком кладе меню (FlowLater, через 6)
    // тим самим кадром раніше (RunFlows іде перед OnUpdate). Тут -- за мокапом:
    // хвіст «+N предм.» (чіп без квадратика) -- той самий рядок тексту через
    // пробіл, а не ще один чіп; і весь рядок -- по центру під вузлом. false --
    // текст ще не розкладено.
    private bool LayPrice(OZL_TreeMenu menu, Widget cell, bool force)
    {
        Widget box = cell.FindAnyWidget("NodePrice");
        if (!box || !box.IsVisible())
            return true;
        float px = menu.Px();
        array<Widget> items = new array<Widget>();
        array<float> widths = new array<float>();
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
                items.Insert(chip);
                widths.Insert(pw / px);
            }
            chip = chip.GetSibling();
        }
        if (items.Count() == 0)
            return true;
        // Відступ тексту в чіпі -- з самого чіпа.
        float tx;
        float ty;
        Widget first = items[0].FindAnyWidget("PriceText");
        first.GetPos(tx, ty);
        tx = tx / px;
        float end = 0;
        for (int i = 0; i < items.Count(); i++)
        {
            float x;
            float y;
            items[i].GetPos(x, y);
            x = x / px;
            Widget dot = items[i].FindAnyWidget("PriceChip");
            // Через локальну: складений булевий вираз просто в аргумент
            // псує купу рушія (скіл, залізні правила).
            bool tail = false;
            if (i > 0 && dot && !dot.IsVisible())
                tail = true;
            if (tail)
            {
                x = end + PRICE_SP - tx;
                menu.PlaceUnits(items[i], x, y / px);
            }
            end = x + tx + widths[i];
        }
        float bx;
        float by;
        box.GetPos(bx, by);
        menu.PlaceUnits(box, AnchorX - end / 2, by / px);
        return true;
    }

    // Рамки чіпів «Відкриває» (.opens a: 1 + 8 + текст + 8 + 1): чіпи кладе й
    // розтягує їм ChipHit меню (FlowLater з OpensGap / OpensPad); тут -- рамка на
    // ту саму ширину: від лівого краю чіпа до кінця тексту + OpensPad, як
    // міряє меню. Двічі: якщо меню перемалює чіпи кадром пізніше, друга
    // розкладка поставить рамки й на них.
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
                float cx;
                float cy;
                float tx;
                float ty;
                chip.GetScreenPos(cx, cy);
                t.GetScreenPos(tx, ty);
                chips.Insert(chip);
                widths.Insert((tx + tw - cx) / px + OpensPad);
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
        for (int i = 0; i < chips.Count(); i++)
        {
            Widget c = chips[i];
            float w = widths[i];
            Stretch(menu, c, "ChipTop", w);
            Stretch(menu, c, "ChipBottom", w);
            Stretch(menu, c, "ChipDashTop", w);
            Stretch(menu, c, "ChipDashBottom", w);
            ToRight(menu, c, "ChipRight", w);
            ToRight(menu, c, "ChipDashRight", w);
        }
        UpdateRole(menu, "EcoTimeStack");
    }

    // Годинник проєкту (.tmr, жирний): за «Лишилось» через пробіл, далі
    // «з 1 хв 00 с», на рядку слова. Меню пише CardTimer щосекунди; тут --
    // місця і хвіст.
    private void TimerTick(OZL_TreeMenu menu)
    {
        OZL_NodeView n = menu.NodeOf(menu.SelectedId());
        if (!n || n.Status != "researching")
            return;
        int left = menu.LeftOf(n);
        if (left == m_TimerLeft)
            return;
        TextWidget word = TextWidget.Cast(menu.Role("EcoTimeLeft"));
        TextWidget clock = TextWidget.Cast(menu.Role("CardTimer"));
        TextWidget tail = TextWidget.Cast(menu.Role("EcoTimeTail"));
        if (!word || !clock || !tail)
            return;
        clock.SetText(OZL_Text.Clock(left));
        clock.Update();
        int ww;
        int wh;
        int cw;
        int ch;
        word.GetTextSize(ww, wh);
        clock.GetTextSize(cw, ch);
        if ((ww <= 0 || cw <= 0) && m_TimerTries < TRIES)
        {
            m_TimerTries++;
            return;
        }
        m_TimerLeft = left;
        string rest = "";
        if (n.Duration > 0)
            rest = OZL_Text.Words("STR_OZL_TREE_OF") + " " + OZL_Text.Duration(n.Duration);
        tail.SetText(rest);
        float px = menu.Px();
        float x;
        float y;
        word.GetPos(x, y);
        x = x / px;
        y = y / px;
        float at = x + ww / px + SPACE;
        menu.PlaceUnits(clock, at, y);
        menu.PlaceUnits(tail, at + cw / px + SPACE, y);
    }

    // Смужки туману (135 градусів) -- під переходом TreeFogEdge, на його
    // прямокутнику: видно їх лише крізь перехід, як у мокапі.
    private void FogTick(OZL_TreeMenu menu)
    {
        Widget stripes = menu.Role("EcoFogStripes");
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

    // Риски під назвою вибраного (NodeUnder0/1 у NodeSel): кожна -- на ширину
    // тексту свого рядка, по центру напису. Меню переносить назву кадром
    // пізніше, тож ширину тексту видно не відразу -- риска стає, коли вона є, і
    // переставляється, коли змінюється.
    private void SelTick(OZL_TreeMenu menu)
    {
        if (!m_SelCell)
            return;
        Widget sel = m_SelCell.FindAnyWidget("NodeSel");
        if (!sel || !sel.IsVisible())
            return;
        m_SelW0 = Underline(menu, sel, "NodeName0", "NodeUnder0", m_SelW0);
        m_SelW1 = Underline(menu, sel, "NodeName1", "NodeUnder1", m_SelW1);
    }

    // Повертає ширину тексту (пікселі), під яку стоїть риска; -1 -- риски нема.
    private int Underline(OZL_TreeMenu menu, Widget sel, string labelName, string lineName, int was)
    {
        Widget line = sel.FindAnyWidget(lineName);
        if (!line)
            return was;
        TextWidget t = TextWidget.Cast(m_SelCell.FindAnyWidget(labelName));
        int pw = 0;
        int ph = 0;
        if (t && t.IsVisible())
            t.GetTextSize(pw, ph);
        if (pw <= 0)
        {
            if (line.IsVisible())
                line.Show(false);
            return -1;
        }
        if (pw == was && line.IsVisible())
            return was;
        float px = menu.Px();
        float lx;
        float ly;
        float lw;
        float lh;
        float sx;
        float sy;
        t.GetScreenPos(lx, ly);
        t.GetScreenSize(lw, lh);
        sel.GetScreenPos(sx, sy);
        float gx;
        float gy;
        float gw;
        float gh;
        line.GetPos(gx, gy);
        line.GetSize(gw, gh);
        menu.PlaceUnits(line, (lx + (lw - pw) / 2 - sx) / px, gy / px);
        menu.SizeUnits(line, pw / px, gh / px);
        line.Show(true);
        return pw;
    }

    // Шапка праворуч (мокап має лише гілку): кілька гілок -- знак ▸ перед назвою
    // і кнопка на весь блок гілки, що відкриває наступну; «Закрити» -- клавіша
    // завширшки зі слово + поля по боках, правим краєм за CLOSE_GAP від блоку
    // гілки.
    private void HeadTick(OZL_TreeMenu menu)
    {
        if (!m_HeadDirty)
            return;
        Widget btn = menu.Role("BtnClose");
        TextWidget word = TextWidget.Cast(menu.Role("BtnCloseText"));
        TextWidget name = TextWidget.Cast(menu.Role("BranchName"));
        TextWidget sub = TextWidget.Cast(menu.Role("BranchSub"));
        if (!btn || !word)
        {
            m_HeadDirty = false;
            return;
        }
        int ww;
        int wh;
        int nw = 0;
        int nh;
        int sw = 0;
        int sh;
        word.GetTextSize(ww, wh);
        if (name)
            name.GetTextSize(nw, nh);
        if (sub)
            sub.GetTextSize(sw, sh);
        if ((ww <= 0 || (nw <= 0 && sw <= 0)) && m_HeadTries < TRIES)
        {
            m_HeadTries++;
            return;
        }
        m_HeadDirty = false;
        float px = menu.Px();
        float left = m_HeadRight - Math.Max(nw, sw) / px;
        bool many = menu.BranchCount() > 1;
        Widget mark = menu.Role("EcoBranchMark");
        if (mark)
        {
            mark.Show(many);
            if (many)
            {
                left = m_HeadRight - Math.Max(nw / px + m_MarkW + MARK_GAP, sw / px);
                menu.PlaceUnits(mark, m_HeadRight - nw / px - m_MarkW - MARK_GAP, m_MarkY);
            }
        }
        Widget next = menu.Role("EcoBranchNext");
        if (next)
        {
            next.Show(many);
            if (many)
            {
                menu.PlaceUnits(next, left, m_NextY);
                menu.SizeUnits(next, m_HeadRight - left, m_NextH);
            }
        }
        float w = ww / px + 2 * m_ClosePad;
        menu.PlaceUnits(btn, left - CLOSE_GAP - w, m_CloseY);
        menu.SizeUnits(btn, w, m_CloseH);
        Stretch(menu, btn, "EcoCloseTop", w);
        Stretch(menu, btn, "EcoCloseBottom", w);
        ToRight(menu, btn, "EcoCloseRight", w);
    }

    // Під мишею «Закрити» світлішає -- як рамка чіпа (txt).
    private void CloseHoverTick(OZL_TreeMenu menu)
    {
        Widget btn = menu.Role("BtnClose");
        if (!btn)
            return;
        bool lit = GetWidgetUnderCursor() == btn;
        if (lit == m_CloseLit)
            return;
        m_CloseLit = lit;
        int edge = EdgeColor;
        int text = Dim;
        if (lit)
        {
            edge = Txt;
            text = Txt;
        }
        Tint(btn, "EcoCloseTop", edge);
        Tint(btn, "EcoCloseBottom", edge);
        Tint(btn, "EcoCloseLeft", edge);
        Tint(btn, "EcoCloseRight", edge);
        Tint(btn, "BtnCloseText", text);
    }

    // Підвал протоколу притиснутий донизу (.c-foot: justify-content flex-end):
    // кожен зайвий рядок причини піднімає і її, і кнопку (EcoBtnBox) на рядок.
    // Причину пише й меню (Say: запит, відмова), тож лічимо рядки щокадру, а
    // рухаємо -- коли їх число змінилось.
    private void FootTick(OZL_TreeMenu menu)
    {
        TextWidget why = TextWidget.Cast(menu.Role("CardWhy"));
        if (!why)
            return;
        int pw;
        int ph;
        why.GetTextSize(pw, ph);
        int lines = 1;
        if (pw > 0)
        {
            float h = ph / menu.Px();
            lines = Math.Round((h - m_WhyH) / WHY_LINE) + 1;
            if (lines < 1)
                lines = 1;
            if (lines > 4)
                lines = 4;
        }
        if (lines == m_WhyLines)
            return;
        m_WhyLines = lines;
        float lift = (lines - 1) * WHY_LINE;
        menu.PlaceUnits(why, 0, m_WhyY - lift);
        Place(menu, "EcoBtnBox", 0, m_BtnY - lift);
    }

    // ------------------------------------------------------------------
    // Розкладка власних частин (OnPaint)
    // ------------------------------------------------------------------

    // Прилади пулу -- порівну по ширині ряду (.pool gap, .prow flex 1):
    // стільки, скільки ліній дав PaintPoolRow за це малювання; решта схована
    // (нема ліній -- меню показує PoolEmpty).
    private void LayPool(OZL_TreeMenu menu)
    {
        int count = m_PoolCount;
        m_PoolCount = 0;
        if (m_PoolW <= 0)
            return;
        if (count > m_Pools)
            count = m_Pools;
        float w = m_PoolW;
        if (count > 0)
            w = (m_PoolW - m_PoolGap * (count - 1)) / count;
        for (int i = 0; i < m_Pools; i++)
        {
            string p = "EcoPool" + i.ToString();
            Widget slot = menu.Role(p);
            if (!slot)
                continue;
            bool used = i < count;
            slot.Show(used);
            if (!used)
                continue;
            menu.PlaceUnits(slot, i * (w + m_PoolGap), 0);
            menu.SizeUnits(slot, w, m_PoolH);
            Stretch(menu, slot, p + "EdgeT", w);
            Stretch(menu, slot, p + "EdgeB", w);
            ToRight(menu, slot, p + "EdgeR", w);
            Move(menu, slot, p + "Chip", w - m_PoolChipR, m_PoolChipY);
        }
    }

    // Підписи тирів «тир I»: тири видимих вузлів гілки за зростанням, кожен --
    // на точці тиру вздовж (Top + Row x (i + 1/2), як кладе свої рядки меню:
    // OZL_TreePlan, PaintTree); глибину точці дає розкладка, напис висить на
    // ній по центру.
    private void PlaceTiers(OZL_TreeMenu menu, OZL_BranchView b)
    {
        array<int> tiers = new array<int>();
        int i;
        if (b)
        {
            for (i = 0; i < b.Nodes.Count(); i++)
            {
                if (!b.Nodes[i])
                    continue;
                int t = OZL_TreePlan.TierOf(b.Nodes[i]);
                if (tiers.Find(t) < 0)
                    tiers.Insert(t);
            }
        }
        tiers.Sort();
        if (tiers.Count() > m_Tiers && !m_TierWarned)
        {
            m_TierWarned = true;
            OZL_Log.Warn("tree: ecolog: " + tiers.Count().ToString() + " tiers, ozl_tree_ecolog has " + m_Tiers.ToString() + " tier labels (EcoTier<n>) -- the rest are not shown");
        }
        float px = menu.Px();
        for (i = 0; i < m_Tiers; i++)
        {
            Widget point = menu.Role("EcoTier" + i.ToString());
            TextWidget lab = TextWidget.Cast(menu.Role("EcoTier" + i.ToString() + "Text"));
            if (!point || !lab)
                continue;
            bool used = i < tiers.Count();
            point.Show(used);
            if (!used)
                continue;
            lab.SetText(TierText(tiers[i]));
            float x;
            float y;
            point.GetPos(x, y);
            menu.PlaceUnits(point, Top + Row * (i + 0.5), y / px);
        }
    }

    // ------------------------------------------------------------------
    // Дрібниці
    // ------------------------------------------------------------------

    // Розрядка пробілами (letter-spacing мокапа від .16em): після кожної цілої
    // літери чи цифри -- пробіл, крім останньої (слово по центру стоїть рівно).
    // Замінюються цілі літери, не байти: текст -- UTF-8.
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
        int n = t.Length();
        if (n > 0 && t.Substring(n - 1, 1) == " ")
            t = t.Substring(0, n - 1);
        return t;
    }

    // Картинка мови гравця в ImageWidget ролі (рядок *_IMG stringtable): true --
    // рядок назвав картинку набору і вона стала.
    private static bool Picture(OZL_TreeMenu menu, string role, string image)
    {
        ImageWidget w = ImageWidget.Cast(menu.Role(role));
        if (!w || image.IndexOf("set:") != 0)
            return false;
        if (!w.LoadImageFile(0, image))
            return false;
        w.SetImage(0);
        return true;
    }

    private static void SetUpper(OZL_TreeMenu menu, string role, string key)
    {
        TextWidget t = TextWidget.Cast(menu.Role(role));
        if (t)
            t.SetText(OZL_Text.Upper(OZL_Text.Words(key)));
    }

    private static void TintChip(Widget chip, int color)
    {
        Tint(chip, "ChipTop", color);
        Tint(chip, "ChipBottom", color);
        Tint(chip, "ChipLeft", color);
        Tint(chip, "ChipRight", color);
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

    private static void ShowIn(Widget root, string name, bool on)
    {
        Widget w = root.FindAnyWidget(name);
        if (w)
            w.Show(on);
    }

    private static void UpdateRole(OZL_TreeMenu menu, string role)
    {
        Widget w = menu.Role(role);
        if (w)
            w.Update();
    }

    private static void Follow(OZL_TreeMenu menu, string row, string head)
    {
        Widget r = menu.Role(row);
        Widget h = menu.Role(head);
        if (r && h)
            r.Show(h.IsVisible());
    }

    private static void Place(OZL_TreeMenu menu, string role, float x, float y)
    {
        Widget w = menu.Role(role);
        if (w)
            menu.PlaceUnits(w, x, y);
    }

    private static void Move(OZL_TreeMenu menu, Widget root, string name, float x, float y)
    {
        Widget w = root.FindAnyWidget(name);
        if (w)
            menu.PlaceUnits(w, x, y);
    }

    // Смужка рамки на ширину `width`; її товщина -- своя, з розкладки.
    private static void Stretch(OZL_TreeMenu menu, Widget root, string name, float width)
    {
        Widget w = root.FindAnyWidget(name);
        if (!w)
            return;
        float gw;
        float gh;
        w.GetSize(gw, gh);
        menu.SizeUnits(w, width, gh / menu.Px());
    }

    // Права смужка рамки -- впритул до правого краю ширини `width`, на своїй
    // висоті; її товщина -- своя, з розкладки.
    private static void ToRight(OZL_TreeMenu menu, Widget root, string name, float width)
    {
        Widget w = root.FindAnyWidget(name);
        if (!w)
            return;
        float px = menu.Px();
        float x;
        float y;
        float gw;
        float gh;
        w.GetPos(x, y);
        w.GetSize(gw, gh);
        menu.PlaceUnits(w, width - gw / px, y / px);
    }
}

#endif
