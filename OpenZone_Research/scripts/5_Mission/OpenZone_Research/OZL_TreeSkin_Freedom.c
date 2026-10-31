// Вікно freedom -- «ВОЛЯ.narod»: саморобний фан-сайт початку двотисячних. Плитка з
// пацифіками й листочками на все тло; банер із райдужним заголовком «ВордАрт», пацифіком,
// що крутиться, і листком; бігучий рядок; ліворуч рамка «ridge» з меню гілок-посилань, балами
// на червоних табло і табличкою «Сторінка в розробці!», поверх неї -- помічник-листик із
// хмаркою підказок; посередині дерево, що росте знизу вгору, на зоряному небі; праворуч
// вікно info.exe з кнопками Windows 98; унизу лічильник відвідувачів. Вузол -- кнопка
// Windows 98 180x64, статус каже колір кнопки: закритий сірий із тисненою назвою, не
// вистачає -- рожевий, доступний -- жовтий з червоним «NEW!», що блимає, у ділі -- блакитний
// з пісочним годинником, досліджений -- зелений з галкою; вибраний -- жовта пунктирна рамка.
//
// Розкладки: ozl_tree_freedom, ozl_node_freedom (ui/OpenZone_Research/); картинки:
// source/ui/freedom/ (набір ozl_freedom і текстура плитки); кольори й шрифти:
// ui/tokens/freedom.json. Числа нижче -- ті самі токени в ARGB.
//
// Анімації -- в OnUpdate: бігучий рядок, кадри пацифіка, блимання «NEW» і пісочного годинника,
// помічник (гойдання, моргання, «Відчепись» на 10 с), світліший вузол під мишею, натиснуті
// кнопки. Жирний, курсив і світіння рушій дає лише SDF-шрифтам (SetBold / SetItalic / тінь
// тексту на бітмапових нічого не роблять, виміряно 2026-10-31), тож жирний Comic (назви
// вузлів, статус, кнопка, «Сторінка в розробці!»), жирний і курсивний Times, жирний Courier
// табло і підписи тирів (PT Mono) та Impact назви гілки зі світінням -- шрифти ozl_sdf_*.
// Напівпрозорі кольори виправлено під лінійне змішування рушія (чорний шар a -> 1 - (1 - a)^2.2,
// світлий на темному -> a^2.2). Що скін рухає чи розтягує, він міряє в самій розкладці (Measure,
// щойно її розкладено); сталі нижче -- числа мокапа, не розкладки, або поряд названо, звідки вони.

#ifndef NO_GUI

class OZL_TreeSkin_Freedom : OZL_TreeSkin
{
    static const string SET = "set:ozl_freedom image:";
    static const float MARQUEE_SEC  = 26;     // прохід бігучого рядка (f-marquee)
    static const float PEACE_SEC    = 6;      // оберт пацифіка (f-spin)
    static const int   PEACE_FRAMES = 16;
    static const float BOB_SEC      = 2.4;    // гойдання листика (f-bob)
    static const float BOB          = 6;      // ...на 6 угору (translateY(-6px))
    static const float WINK_SEC     = 5;      // моргання (f-wink)
    static const float HIDE_SEC     = 10;     // «Відчепись»
    static const float FADE_SEC     = 0.3;    // .fhelp { transition: .3s }
    static const float HELP_DROP    = 20;     // .fhelp.hide: translateY(20px)
    static const float LEAF_GAP     = 4;      // листик під хмаркою (margin-top 4)
    static const float TIP_LINE     = 18.2;   // рядок хмарки: Verdana 14 / 1.3
    static const float TITLE_GAP    = 4;      // заголовок підказки -> текст
    static const float TEXT_GAP     = 8;      // текст -> кнопки
    static const float BTN_PAD      = 24;     // кнопка хмарки: слово + padding 0 12px
    static const float BTN_GAP      = 8;      // між кнопками хмарки
    static const float BEVEL_W      = 2;      // фаска кнопки Windows 98
    static const float NAME_LINE    = 37;     // рядок назви в картці (Impact 30)
    static const int   TIPS         = 6;      // своя підказка вузла + п'ять загальних
    static const float BRANCH_ROW   = 24;     // рядок гілки в меню (рядок ozl_freedom_branch_row)
    static const float LINK_GAP     = 9.5;    // «»», назва і «← ти тут» у рядку гілки
    static const float COUNT_GAP    = 8;      // «ти тут» -> лічильник гілки: не ближче
    static const float LEGEND_GAP   = 14;     // пункти легенди (.legend gap 14)
    static const float TAG_PAD      = 12;     // табличка розділу: слово + padding 0 6px
    static const float NEW_EDGE_PAD = 10;     // «NEW!»: рамка і поле навколо слова
    static const float NEW_FILL_PAD = 8;
    static const float POOL_GAP     = 8;      // меню гілок -> смуга «БАЛИ»
    static const float POOL_CLEAR   = 3;      // низ балів -- на 3 вище хмарки помічника
    static const float POOL_MIN     = 110;    // бали показують щонайменше три рядки
    // Заголовок «ВордАрт»: половина ширини напису в запеченій картинці (мокап: 637.08 укр.,
    // 450.95 англ.) і відстань до символів обабіч (margin 0 26px).
    static const float ART_HALF_UA  = 318.54;
    static const float ART_HALF_EN  = 225.475;
    static const float ART_GAP      = 26;
    // Підвал (.ffoot): проміжок 18, пробіл шрифту 4, ширина ★ і ☮ у Verdana 13.
    static const float FOOT_GAP     = 18;
    static const float FOOT_SPACE   = 4;
    static const float STAR_W       = 10.84;
    static const float PEACE_W      = 11.2;
    // Табло пулу -- числа рядка ozl_freedom_pool_row (рядок вимальовує меню, тож у PaintPoolRow
    // він ще не розкладений і не міряється): PoolLed 232..296 з рамкою 4, цифри між 236 і 292;
    // PoolDigit0 на 272.6, 14 завширшки (центр 279.6), слоти через 13.8, верх цифри -0.75.
    static const float LED_PITCH    = 13.8;
    static const float LED_RIGHT    = 279.6;
    static const float LED_EDGE     = 292;
    static const float LED_SPAN     = 56;
    static const float DIGIT_HALF   = 7;
    static const float LED_Y        = -0.75;
    // Блимання мокапа (blink 1s steps(2)): 1, .6, .2, .6 по чверть секунди. Рушій змішує
    // лінійно, тож світле на темному -- a^2.2: .6 -> .325, .2 -> .03.
    static const float BLINK_MID    = 0.325;
    static const float BLINK_LOW    = 0.03;
    // Світіння (тінь тексту SDF): табло -- 0 0 6px rgba(255,48,48,.8) мокапа, назва гілки --
    // 0 0 8px #ff00ff. Розмір і непрозорість -- з виміру СОП (4/.45 ледь, 8/1.0 сильно).
    static const int   LED_GLOW     = 5;
    static const float LED_GLOW_A   = 0.6;
    static const int   NAME_GLOW    = 7;
    static const float NAME_GLOW_A  = 0.75;

    // Кольори поза базовою палітрою (ARGB; ті, що є й у розкладці, -- токени freedom_* у
    // ui/tokens/freedom.json; Grey, LedOff і CostOk -- лише тут).
    int Ink;          // чорний текст на світлому
    int White;
    int WinLo;        // #404040: темний бік кнопки Windows 98
    int Grey;         // #808080: закритий вузол, неактивна кнопка, туманний чіп
    int Emboss;       // #e8e8e8: світла тінь назви закритого вузла
    int Faint;        // --faint: назва лінії, де балів нема
    int MenuLink;     // #66ccff: гілка-посилання (не Link: так зветься ванільний клас)
    int MenuHere;     // #ff66ff: відкрита гілка
    int Led;          // #ff3030: табло балів
    int LedOff;       // #6a1010: нуль на табло
    int Navy;         // #000080: у ділі, сегменти, кнопка під мишею
    int DoneInk;      // #004d00: ціна й значок дослідженого
    int ShortInk;     // #c00060: ціна, на яку не вистачає
    int CostOk;       // #008000
    int CostBad;      // #c00000
    int OpensBlue;    // #0000ee: «Відкриває»
    int NewRed;       // #ff0000: «NEW!»
    int CNameShadow;  // #ff99ff: тінь назви в картці
    // Слово статусу в картці: колір мокапа, пропущений через filter: brightness(.55)
    // saturate(1.6) (.card .cstat), виміряно в Chrome.
    int StatLocked;
    int StatShort;
    int StatOpen;
    int StatDone;
    int StarA;        // зоряне небо: rgba(255, 255, 255, .7) кожні 90 x 70 (лінійно: .7^2.2)
    int StarB;        // rgba(255, 255, 170, .45) кожні 53 x 61 (лінійно: .45^2.2)
    int Magenta;      // #ff00ff: світіння назви гілки

    protected float  m_Time;
    protected float  m_MarqueeW;    // ширина тексту бігучого рядка
    protected int    m_PeaceFrame;
    protected int    m_BlinkStep;   // чверть секунди блимання: 0..3, -1 -- ще не було
    protected string m_HoverShown;
    protected bool   m_BtnOn;
    protected bool   m_BtnDown;
    protected bool   m_NextDown;
    protected bool   m_HideDown;
    protected bool   m_FootPending;
    protected int    m_FootTries;
    protected int    m_NameLines;
    protected float  m_SkyH;
    protected bool   m_LeftPending;   // меню гілок і бали чекають розкладки
    protected bool   m_BannerPending; // символи обабіч заголовка -- теж
    protected bool   m_TiersDirty;    // меню переписало підписи тирів: зробити жирними
    protected bool   m_RowsPending;   // нові рядки гілок: чи влізло «ти тут»
    protected int    m_RowsTries;
    protected float  m_ArtHalf;

    // Числа розкладки, виміряні в ній самій (Measure), одиниці.
    protected bool   m_Measured;
    protected int    m_MeasureTries;
    protected float  m_StripW;     // рамка бігучого рядка
    protected float  m_TickerY;    // верх рядка в ній
    protected float  m_ArtMid;     // середина заголовка
    protected float  m_PeaceW;     // символ обабіч нього
    protected float  m_FootW;      // підвал
    protected float  m_CounterW;   // табло лічильника
    protected float  m_ListY;      // меню гілок у рамці
    protected float  m_PoolTop;    // список балів під своєю смугою
    protected float  m_PoolFloor;  // нижче балам не можна: хмарка помічника
    protected float  m_HelpX;      // помічник на своєму місці
    protected float  m_HelpY;
    protected float  m_LeafX;
    protected float  m_Pad;        // хмарка: рамка + поле, згори й знизу
    protected float  m_InnerR;     // правий край тексту в хмарці
    protected float  m_Slice;      // верхній і нижній зрізи хмарки
    protected float  m_BtnH;       // кнопка хмарки

    // Помічник.
    protected string m_TipKey;
    protected int    m_TipIndex;
    protected string m_TipStatus;
    protected bool   m_TipNode;
    protected bool   m_TipCan;
    protected int    m_HelpState;   // 0 видно, 1 зникає, 2 сховано, 3 з'являється
    protected float  m_HelpClock;   // секунди від «Відчепись»
    protected int    m_TitleLines;
    protected int    m_TextLines;
    protected bool   m_ButtonsPending;
    protected float  m_BubbleH;
    protected int    m_LeafFrame;
    protected ref array<Widget> m_HelpWidgets;
    protected ref array<float>  m_HelpAlphas;

    void OZL_TreeSkin_Freedom()
    {
        Named("freedom");
        Dir     = "up";
        NodeW   = 180;
        NodeH   = 64;
        Row     = 150;
        Col     = 214;
        Top     = 70;
        Side    = 40;
        AnchorX = 110;   // кнопка лежить у комірці 220x112 з (20, 36)
        AnchorY = 68;

        Txt      = ARGB(255, 204, 255, 102);
        Dim      = ARGB(255, 143, 174,  90);
        Acc      = ARGB(255, 255, 255,   0);
        Ok       = ARGB(255,  51, 255, 102);
        Bad      = ARGB(255, 255,  79, 160);
        LineDim  = ARGB(255,  79, 122,  53);
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255,   3,   8,   2);
        FogColor = ARGB(255,   3,   8,   2);

        Ink         = ARGB(255,   0,   0,   0);
        White       = ARGB(255, 255, 255, 255);
        WinLo       = ARGB(255,  64,  64,  64);
        Grey        = ARGB(255, 128, 128, 128);
        Emboss      = ARGB(255, 232, 232, 232);
        Faint       = ARGB(255, 110, 135,  69);
        MenuLink    = ARGB(255, 102, 204, 255);
        MenuHere    = ARGB(255, 255, 102, 255);
        Led         = ARGB(255, 255,  48,  48);
        LedOff      = ARGB(255, 106,  16,  16);
        Navy        = ARGB(255,   0,   0, 128);
        DoneInk     = ARGB(255,   0,  77,   0);
        ShortInk    = ARGB(255, 192,   0,  96);
        CostOk      = ARGB(255,   0, 128,   0);
        CostBad     = ARGB(255, 192,   0,   0);
        OpensBlue   = ARGB(255,   0,   0, 238);
        NewRed      = ARGB(255, 255,   0,   0);
        CNameShadow = ARGB(255, 255, 153, 255);
        StatLocked  = ARGB(255,  73, 100,  26);
        StatShort   = ARGB(255, 184,  29, 100);
        StatOpen    = ARGB(255, 146, 146,   0);
        StatDone    = ARGB(255,   0, 158,  24);
        StarA       = ARGB(116, 255, 255, 255);
        StarB       = ARGB( 44, 255, 255, 170);
        Magenta     = ARGB(255, 255,   0, 255);

        // Зоряне небо (.tree .content .bg) малює GridLine: крок сітки -- смуга, у якій
        // кожна горизонталь ставить свої крапки.
        GridStep = 90;
        GridX    = 45;
        GridY    = 45;

        // Вигляд кнопки за статусом (ShapeOf) і мітки в порядку типового MarkOf:
        // замок, галка, пісочний годинник (емодзі й гліф мокапа, запечені).
        Shapes.Insert(SET + "face_locked");
        Shapes.Insert(SET + "face_short");
        Shapes.Insert(SET + "face_available");
        Shapes.Insert(SET + "face_researching");
        Shapes.Insert(SET + "face_completed");
        Marks.Insert(SET + "mark_lock");
        Marks.Insert(SET + "mark_check");
        Marks.Insert(SET + "mark_wait");

        SegOn   = Navy;
        SegOff  = White;
        TipPadX = 9;

        m_HelpWidgets = new array<Widget>();
        m_HelpAlphas  = new array<float>();
    }

    // ------------------------------------------------------------------
    // Вузол
    // ------------------------------------------------------------------

    override int ShapeOf(string status, bool selected)
    {
        if (status == "short")
            return 1;
        if (status == "available")
            return 2;
        if (status == "researching")
            return 3;
        if (status == "completed")
            return 4;
        return 0;
    }

    override int NameColorOf(string status)
    {
        if (status == "locked")
            return Grey;
        return Ink;
    }

    override int PriceColorOf(string status)
    {
        if (status == "locked")
            return Grey;
        if (status == "short")
            return ShortInk;
        if (status == "researching")
            return Navy;
        if (status == "completed")
            return DoneInk;
        return Ink;
    }

    override int IconColorOf(string status)
    {
        if (status == "locked")
            return Grey;
        if (status == "completed")
            return DoneInk;
        return Ink;
    }

    override int StatusColorOf(string status)
    {
        if (status == "locked")
            return StatLocked;
        if (status == "short")
            return StatShort;
        if (status == "completed")
            return StatDone;
        return StatOpen;
    }

    override string MarkTextOf(string status)
    {
        if (status == "available")
            return OZL_Text.Words("STR_OZL_TREE_MARK_NEW");
        return "";
    }

    // Мітки-картинки мають свої кольори; «NEW!» -- червоне.
    override int MarkColorOf(string status)
    {
        if (status == "available")
            return NewRed;
        return White;
    }

    // Таблички розділів -- великими (.sec мокапа: text-transform uppercase).
    override string SectionText(string key)
    {
        return OZL_Text.Upper(OZL_Text.Words(key));
    }

    // Підписи тирів -- жирний PT Mono (SDF): його «I» із засічками, як у жирної Verdana мокапа.
    // Меню щойно переписало підпис -- OnUpdate зробить його жирним.
    override string TierText(int tier)
    {
        m_TiersDirty = true;
        return super.TierText(tier);
    }

    // Назва жирним Comic, у закритого -- над світлою тінню (той самий текст, перенесений так
    // само: свій контейнер рядків); доступний -- з табличкою «NEW!» на ширину слова.
    override void PaintNode(OZL_TreeMenu menu, Widget cell, OZL_NodeView node, string status, bool selected)
    {
        super.PaintNode(menu, cell, node, status, selected);
        BoldLines(cell, "NodeName", 2);
        bool locked = status == "locked";
        Widget shade = cell.FindAnyWidget("NodeNameShadow");
        if (shade)
        {
            shade.Show(locked);
            if (locked)
            {
                BoldLines(cell, "NodeNameShadow", 2);
                menu.PutText(shade, DataText(NodeNameText(node.Name)), Emboss);
            }
        }
        bool fresh = status == "available";
        Widget tag = cell.FindAnyWidget("NodeNew");
        if (tag)
        {
            tag.Show(fresh);
            if (fresh)
            {
                TextWidget word = TextWidget.Cast(cell.FindAnyWidget("NodeMarkText"));
                menu.FitLater(word, cell.FindAnyWidget("NodeNewEdge"), NEW_EDGE_PAD, 0);
                menu.FitLater(word, cell.FindAnyWidget("NodeNewFill"), NEW_FILL_PAD, 0);
                BlinkTag(cell);
            }
        }
        // Пісочний годинник у ділі блимає (.st-research .mark); інша мітка -- повна.
        Widget mark = cell.FindAnyWidget("NodeMark");
        if (mark)
        {
            float shown = 1;
            if (status == "researching")
                shown = BlinkAlpha();
            mark.SetAlpha(shown);
        }
        // Світлішу кнопку під мишею ставить OnUpdate; перемальована комірка починає без неї.
        Widget hover = cell.FindAnyWidget("NodeHoverFace");
        if (hover)
            hover.Show(false);
        if (node.Id == m_HoverShown)
            m_HoverShown = "";
    }

    // Рядок пулу: назва (тьмяна, коли балів нема) і табло -- червоні цифри, нуль темно-червоний.
    override void PaintPoolRow(OZL_TreeMenu menu, Widget row, int index, string line, int have, int color)
    {
        super.PaintPoolRow(menu, row, index, line, have, color);
        bool lit = have > 0;
        TextWidget name = TextWidget.Cast(row.FindAnyWidget("PoolName"));
        if (name)
        {
            if (lit)
                name.SetColor(Txt);
            else
                name.SetColor(Faint);
        }
        int ink = LedOff;
        if (lit)
            ink = Led;
        LedDigits(menu, row, have.ToString(), ink, lit);
    }

    // Цифри табло справа наліво по слотах PoolDigit0.. (0 -- крайній правий) через LED_PITCH,
    // як жирний Courier 18 з letter-spacing 3 у мокапі (тут жирний PT Mono SDF); від п'яти
    // цифр -- тісніше, у ту саму коробку. Сяйво (text-shadow мокапа) -- тінь тексту SDF.
    protected void LedDigits(OZL_TreeMenu menu, Widget row, string digits, int ink, bool lit)
    {
        int n = digits.Length();
        if (n > 6)
        {
            digits = "999999";
            n = 6;
        }
        float pitch = LED_PITCH;
        float right = LED_RIGHT;
        if (n > 4)
        {
            pitch = LED_SPAN / n;
            right = LED_EDGE - pitch / 2;
        }
        for (int i = 0; i < 6; i++)
        {
            bool used = i < n;
            TextWidget digit = TextWidget.Cast(row.FindAnyWidget("PoolDigit" + i.ToString()));
            if (!digit)
                continue;
            digit.Show(used);
            if (!used)
                continue;
            digit.SetBold(true);
            digit.SetText(digits.Substring(n - 1 - i, 1));
            digit.SetColor(ink);
            if (lit)
                digit.SetShadow(LED_GLOW, Led, LED_GLOW_A, 0, 0);
            // Завжди на місце: рядок, який колись мав п'ять цифр, не лишає їх тісними.
            menu.PlaceUnits(digit, right - pitch * i - DIGIT_HALF, LED_Y);
        }
    }

    // Рядок вартості: чорна назва, «є / треба» зеленим або червоним; смужка -- темно-сині
    // риски за будь-якого вироку (.crow .cbar i).
    override void PaintCostRow(OZL_TreeMenu menu, Widget row, string label, string text, int verdict)
    {
        super.PaintCostRow(menu, row, label, text, verdict);
        TextWidget name = TextWidget.Cast(row.FindAnyWidget("CostName"));
        if (name)
            name.SetColor(Ink);
        int color = Ink;
        if (verdict > 0)
            color = CostOk;
        else if (verdict < 0)
            color = CostBad;
        TextWidget value = TextWidget.Cast(row.FindAnyWidget("CostValue"));
        if (value)
            value.SetColor(color);
        Widget fill = row.FindAnyWidget("CostBarFill");
        if (fill)
            fill.SetColor(White);
    }

    // «Відкриває» -- сині підкреслені посилання; туманний вузол -- сірий.
    override void PaintOpenChip(OZL_TreeMenu menu, Widget chip, string text, bool fogged)
    {
        super.PaintOpenChip(menu, chip, text, fogged);
        int color = OpensBlue;
        if (fogged)
            color = Grey;
        TextWidget t = TextWidget.Cast(chip.FindAnyWidget("ChipText"));
        if (!t)
            return;
        t.SetColor(color);
        Widget under = chip.FindAnyWidget("ChipUnder");
        if (under)
        {
            under.SetColor(color);
            menu.FitLater(t, under, 0, 0);
        }
    }

    // Кнопка Windows 98: чорне слово; неактивна -- сіре з білою тінню (тиснення). Натиснуту
    // показує OnUpdate, слово під мишею (BtnResearchHover) -- меню. Обидва двійники пишуть те
    // саме слово, що меню в BtnResearchText: ButtonText.
    override void PaintButton(OZL_TreeMenu menu, Widget btn, bool enabled)
    {
        m_BtnOn = enabled;
        string status = "";
        OZL_NodeView n = menu.NodeOf(menu.SelectedId());
        if (n)
            status = n.Status;
        string word = ButtonText(status, enabled);
        TextWidget text = TextWidget.Cast(menu.Role("BtnResearchText"));
        if (text)
        {
            text.SetBold(true);
            if (enabled)
                text.SetColor(Ink);
            else
                text.SetColor(Grey);
        }
        TextWidget hover = TextWidget.Cast(menu.Role("BtnResearchHover"));
        if (hover)
        {
            hover.SetBold(true);
            hover.SetText(word);
        }
        TextWidget emboss = TextWidget.Cast(menu.Role("BtnResearchShadow"));
        if (emboss)
        {
            emboss.SetBold(true);
            emboss.SetText(word);
            emboss.Show(!enabled);
        }
    }

    // ------------------------------------------------------------------
    // Зоряне небо: дві решітки крапок на канві, разом із деревом
    // ------------------------------------------------------------------

    // Вертикалі сітки лише кажуть висоту вмісту; кожна горизонталь малює крапки своєї смуги
    // [y - 45, y + 45), остання -- до низу. Крапка -- товста коротка лінія (квадрат 2.2).
    override void GridLine(CanvasWidget canvas, float x1, float y1, float x2, float y2)
    {
        if (x1 == x2)
        {
            m_SkyH = y2;
            return;
        }
        float top = y1 - GridStep / 2;
        float bottom = y1 + GridStep / 2;
        if (y1 + GridStep > m_SkyH)
            bottom = m_SkyH + 1;
        Stars(canvas, 45, 35, 90, 70, top, bottom, x2, StarA);
        Stars(canvas, 46.5, 60.5, 53, 61, top, bottom, x2, StarB);
    }

    protected void Stars(CanvasWidget canvas, float x0, float y0, float dx, float dy, float top, float bottom, float width, int color)
    {
        float y = y0;
        if (top > y0)
            y = y0 + Math.Ceil((top - y0) / dy) * dy;
        while (y < bottom)
        {
            float x = x0;
            while (x <= width)
            {
                Line(canvas, x - 1.1, y, x + 1.1, y, 2.2, color);
                x += dx;
            }
            y += dy;
        }
    }

    // ------------------------------------------------------------------
    // Події
    // ------------------------------------------------------------------

    override void OnShow(OZL_TreeMenu menu)
    {
        m_Time           = 0;
        m_MarqueeW       = 0;
        m_PeaceFrame     = -1;
        m_BlinkStep      = -1;
        m_HoverShown     = "";
        m_BtnDown        = false;
        m_NextDown       = false;
        m_HideDown       = false;
        m_NameLines      = 1;
        m_TitleLines     = 0;
        m_TextLines      = 0;
        m_ButtonsPending = true;
        m_BubbleH        = 0;
        m_LeafFrame      = 0;
        m_HelpState      = 0;
        m_HelpClock      = 0;
        m_TipKey         = "-";
        m_TipIndex       = 0;
        m_Measured       = false;
        m_MeasureTries   = 0;
        m_LeftPending    = false;
        m_BannerPending  = true;
        m_TiersDirty     = true;

        // Заголовок мовою гравця; символи обабіч нього ставить LayBanner за його шириною.
        string art = OZL_Text.Words("STR_OZL_SKIN_FREEDOM_WORDART_IMG");
        ImageWidget wordart = ImageWidget.Cast(menu.Role("WordArt"));
        if (wordart && wordart.LoadImageFile(0, art))
            wordart.SetImage(0);
        m_ArtHalf = ART_HALF_UA;
        if (art.IndexOf("wordart_en") >= 0)
            m_ArtHalf = ART_HALF_EN;

        // Times курсивом і жирним, Comic жирним (шрифти SDF), назва гілки світиться пурпуром.
        TextWidget dev = TextWidget.Cast(menu.Role("DevName"));
        if (dev)
            dev.SetItalic(true);
        BoldRole(menu, "MarqueeText");
        BoldRole(menu, "UcText");
        BoldRole(menu, "CardStatus");
        TextWidget branch = TextWidget.Cast(menu.Role("BranchName"));
        if (branch)
            branch.SetShadow(NAME_GLOW, Magenta, NAME_GLOW_A, 0, 0);

        menu.FlowLater(menu.Role("LegendRow"), LEGEND_GAP, 0, false);

        // Лічильник відвідувачів: цифра на слот (letter-spacing мокапа). Ряд підвалу
        // розставляє OnUpdate, щойно тексти мають ширину.
        string count = OZL_Text.Words("STR_OZL_SKIN_FREEDOM_COUNTER_VALUE");
        for (int i = 0; i < 6; i++)
        {
            TextWidget digit = TextWidget.Cast(menu.Role("FootDigit" + i.ToString()));
            if (!digit)
                continue;
            digit.SetBold(true);
            if (i < count.Length())
                digit.SetText(count.Substring(i, 1));
            else
                digit.SetText("");
        }
        m_FootPending = true;
        m_FootTries   = 0;

        // Усе, що зникає разом із помічником, і прозорість кожного з розкладки.
        m_HelpWidgets.Clear();
        m_HelpAlphas.Clear();
        Collect(menu.Role("HelperRoot"));
    }

    // Після кожного повного малювання: відкрита гілка рожева з «ти тут», кожен рядок меню
    // розкладено за текстами; бали -- під списком гілок; тінь назви гілки.
    override void OnPaint(OZL_TreeMenu menu)
    {
        Widget list = menu.Role("BranchList");
        if (list)
        {
            Widget row = list.GetChildren();
            while (row)
            {
                Widget pick = row.FindAnyWidget("RowPick");
                int color = MenuLink;
                if (pick && pick.IsVisible())
                    color = MenuHere;
                Paint(row.FindAnyWidget("RowName"), color);
                Paint(row.FindAnyWidget("RowNameLine"), color);
                menu.FlowLater(row.FindAnyWidget("RowFlow"), LINK_GAP, 0, false);
                row = row.GetSibling();
            }
        }
        m_RowsPending = true;
        m_RowsTries = 0;
        m_LeftPending = true;
        LayLeft(menu);

        TextWidget shade = TextWidget.Cast(menu.Role("BranchNameShadow"));
        if (shade)
        {
            OZL_BranchView b = menu.CurrentBranch();
            if (b)
                shade.SetText(DataText(b.Name));
            else
                shade.SetText("");
        }
    }

    override void OnSelect(OZL_TreeMenu menu, OZL_NodeView node, string status, bool canResearch)
    {
        // Помічник: той самий вузол у тому самому стані -- та сама підказка; інший -- з початку.
        string can = "0";
        if (canResearch)
            can = "1";
        string key = "none";
        if (node)
            key = node.Id + ":" + status + ":" + can;
        if (key != m_TipKey)
        {
            m_TipKey = key;
            m_TipIndex = 0;
        }
        m_TipNode = false;
        if (node)
            m_TipNode = true;
        m_TipCan = canResearch;
        m_TipStatus = status;
        ShowTip(menu);

        if (!node)
            return;
        // Рожева тінь назви -- той самий текст, перенесений так само.
        menu.PutText(menu.Role("CardNameShadow"), DataText(NodeNameText(node.Name)), CNameShadow);
        // Таблички розділів ідуть за своїми заголовками (меню ховає «Матеріали» й
        // «Відкриває»), кожна завширшки зі слово + 12.
        SectionTag(menu, "CardDescTag", "CardDescHead");
        SectionTag(menu, "CardCostTag", "CardCostHead");
        SectionTag(menu, "CardItemsTag", "CardItemsHead");
        SectionTag(menu, "CardTimeTag", "CardTimeHead");
        SectionTag(menu, "CardOpensTag", "CardOpensHead");
        menu.RefreshCard();
    }

    // Назва в картці перенеслася (меню вже оновило картку): коробка з тінню -- на стільки
    // рядків, скільки їх видно, і картку -- ще раз, бо коробка змінила висоту.
    override void OnWrapped(OZL_TreeMenu menu, Widget box)
    {
        if (!box || box != menu.Role("CardName"))
            return;
        int n = 1;
        Widget second = menu.Role("CardName1");
        if (second && second.IsVisible())
            n = 2;
        if (n == m_NameLines)
            return;
        // Ширину коробки HeightUnits бере з екрана: ще не розкладена -- наступне перенесення.
        Widget nameBox = menu.Role("CardNameBox");
        float boxW;
        float boxH;
        menu.UnitsOf(nameBox, boxW, boxH);
        if (boxW <= 0)
            return;
        m_NameLines = n;
        menu.HeightUnits(nameBox, NAME_LINE * n);
        menu.RefreshCard();
    }

    // Кнопки помічника: «Ага» -- наступна підказка, «Відчепись» -- сховатись на 10 с.
    override bool OnClick(OZL_TreeMenu menu, Widget w)
    {
        string nm = w.GetName();
        if (nm == "HelperNext")
        {
            m_TipIndex++;
            ShowTip(menu);
            return true;
        }
        if (nm != "HelperHide")
            return false;
        if (m_HelpState == 0 || m_HelpState == 3)
        {
            // З'являвся -- зникає з того місця, де був.
            float shown = 1;
            if (m_HelpState == 3)
                shown = Math.Clamp((m_HelpClock - HIDE_SEC) / FADE_SEC, 0, 1);
            m_HelpClock = (1 - shown) * FADE_SEC;
            m_HelpState = 1;
            HelperHits(menu, false);
        }
        return true;
    }

    override void OnUpdate(OZL_TreeMenu menu, float dt)
    {
        m_Time += dt;
        RunPeace(menu);
        RunBlink(menu);
        RunHover(menu);
        RunPress(menu);
        if (m_TiersDirty)
            BoldTiers(menu);
        if (m_RowsPending)
            FitRows(menu);
        // Далі -- те, що стоїть за числами розкладки: до її першого кадру -- як у файлі.
        if (!m_Measured && !Measure(menu))
            return;
        if (m_BannerPending)
            LayBanner(menu);
        if (m_LeftPending)
            LayLeft(menu);
        RunMarquee(menu);
        RunHelper(menu, dt);
        if (m_FootPending)
            RunFooter(menu);
    }

    // ------------------------------------------------------------------
    // Розкладка
    // ------------------------------------------------------------------

    // Числа розкладки, за якими скін рухає й розтягує віджети, -- з самих віджетів, раз на
    // відкриття, щойно вони розкладені (до того віджет міряється нулями).
    protected bool Measure(OZL_TreeMenu menu)
    {
        if (m_MeasureTries > 600)
            return false;
        m_MeasureTries++;
        float stripW = WidthOf(menu, menu.Role("Marquee"));
        float footW = WidthOf(menu, menu.Role("Footer"));
        float counterW = WidthOf(menu, menu.Role("FootCounter"));
        float peaceW = WidthOf(menu, menu.Role("Peace"));
        float artW = WidthOf(menu, menu.Role("WordArt"));
        float textW = WidthOf(menu, menu.Role("HelperText"));
        float slice = HeightOf(menu, menu.Role("BubbleTop"));
        float btnH = HeightOf(menu, menu.Role("HelperNextBox"));
        if (stripW <= 0 || footW <= 0 || counterW <= 0 || peaceW <= 0)
            return false;
        if (artW <= 0 || textW <= 0 || slice <= 0 || btnH <= 0)
            return false;
        m_StripW   = stripW;
        m_FootW    = footW;
        m_CounterW = counterW;
        m_PeaceW   = peaceW;
        m_Slice    = slice;
        m_BtnH     = btnH;
        m_ArtMid   = XOf(menu, menu.Role("WordArt")) + artW / 2;
        m_TickerY  = YOf(menu, menu.Role("MarqueeText"));
        m_ListY    = YOf(menu, menu.Role("BranchScroll"));
        m_PoolTop  = YOf(menu, menu.Role("PoolScroll"));
        m_HelpX    = XOf(menu, menu.Role("HelperRoot"));
        m_HelpY    = YOf(menu, menu.Role("HelperRoot"));
        m_PoolFloor = m_HelpY - YOf(menu, menu.Role("LeftBox")) - POOL_CLEAR;
        m_LeafX    = XOf(menu, menu.Role("HelperLeaf"));
        m_Pad      = YOf(menu, menu.Role("HelperTitle"));
        m_InnerR   = XOf(menu, menu.Role("HelperText")) + textW;
        if (m_BubbleH <= 0)
            m_BubbleH = YOf(menu, menu.Role("BubbleBot")) + slice;
        m_Measured = true;
        return true;
    }

    // Пацифік і листок обабіч заголовка мовою гравця (margin 0 26px мокапа).
    protected void LayBanner(OZL_TreeMenu menu)
    {
        m_BannerPending = false;
        PlaceX(menu, menu.Role("Peace"), m_ArtMid - m_ArtHalf - ART_GAP - m_PeaceW);
        PlaceX(menu, menu.Role("Leaf"), m_ArtMid + m_ArtHalf + ART_GAP);
    }

    // Меню гілок -- на стільки рядків, скільки гілок, під ним проміжок і бали; низ балів --
    // над хмаркою помічника, але щонайменше POOL_MIN.
    protected void LayLeft(OZL_TreeMenu menu)
    {
        if (!m_Measured)
            return;
        m_LeftPending = false;
        int n = menu.BranchCount();
        if (n < 1)
            n = 1;
        Widget branches = menu.Role("BranchScroll");
        menu.HeightUnits(branches, BRANCH_ROW * n);
        if (branches)
            branches.Update();
        float top = m_ListY + BRANCH_ROW * n + POOL_GAP;
        PlaceY(menu, menu.Role("PoolSection"), top);
        float room = m_PoolFloor - top - m_PoolTop;
        if (room < POOL_MIN)
            room = POOL_MIN;
        menu.HeightUnits(menu.Role("PoolScroll"), room);
    }

    // «← ти тут» не налазить на лічильник «2 / 4»: коли не влазить (англійське «you are
    // here», довга назва гілки), лишається сама стрілка. Права межа -- як її рахує FlowLater
    // меню: пункти «»», назва, «ти тут», кожен від свого лівого краю до правого краю тексту,
    // через LINK_GAP; лічильник вирівняно праворуч. Раз на нові рядки, щойно тексти мають ширину.
    protected void FitRows(OZL_TreeMenu menu)
    {
        Widget list = menu.Role("BranchList");
        if (!list)
        {
            m_RowsPending = false;
            return;
        }
        m_RowsTries++;
        Widget row = list.GetChildren();
        while (row)
        {
            Widget pick = row.FindAnyWidget("RowPick");
            TextWidget word = TextWidget.Cast(row.FindAnyWidget("RowPickText"));
            Widget count = row.FindAnyWidget("RowCount");
            if (pick && word && count && pick.IsVisible() && word.IsVisible())
            {
                float markW = TextOf(menu, row.FindAnyWidget("RowMark"));
                float nameW = TextOf(menu, row.FindAnyWidget("RowName"));
                float wordW = TextOf(menu, word);
                float countW = TextOf(menu, count);
                bool ready = true;
                if (markW <= 0 || nameW <= 0 || wordW <= 0 || countW <= 0)
                    ready = false;
                if (!ready && m_RowsTries < 60)
                    return;
                if (ready)
                {
                    float right = XOf(menu, row.FindAnyWidget("RowFlow")) + markW + LINK_GAP + nameW + LINK_GAP;
                    right += XOf(menu, word) + wordW;
                    float left = XOf(menu, count) + WidthOf(menu, count) - countW;
                    if (right + COUNT_GAP > left)
                        word.Show(false);
                }
            }
            row = row.GetSibling();
        }
        m_RowsPending = false;
    }

    // Підписи тирів, які меню щойно переписало, -- жирні (PT Mono SDF).
    protected void BoldTiers(OZL_TreeMenu menu)
    {
        m_TiersDirty = false;
        Widget tiers = menu.Role("TreeTiers");
        if (!tiers)
            return;
        Widget lab = tiers.GetChildren();
        while (lab)
        {
            TextWidget t = TextWidget.Cast(lab.FindAnyWidget("TierText"));
            if (t)
                t.SetBold(true);
            lab = lab.GetSibling();
        }
    }

    // ------------------------------------------------------------------
    // Анімації
    // ------------------------------------------------------------------

    // Рядок з'являється з правого краю і йде, доки не зникне за лівим, 26 с на прохід
    // (padding-left 100% і translateX(-100%) мокапа).
    protected void RunMarquee(OZL_TreeMenu menu)
    {
        TextWidget text = TextWidget.Cast(menu.Role("MarqueeText"));
        if (!text)
            return;
        if (m_MarqueeW <= 0)
        {
            int pw;
            int ph;
            text.GetTextSize(pw, ph);
            if (pw > 0)
                m_MarqueeW = pw / menu.Px();
        }
        // Ширини ще нема -- рядок лишається за правим краєм, де його поставила розкладка.
        float width = m_MarqueeW;
        if (width <= 0)
            return;
        float t = m_Time / MARQUEE_SEC;
        t = t - Math.Floor(t);
        menu.PlaceUnits(text, m_StripW - (m_StripW + width) * t, m_TickerY);
    }

    protected void RunPeace(OZL_TreeMenu menu)
    {
        float turns = m_Time / PEACE_SEC;
        turns = turns - Math.Floor(turns);
        int frame = turns * PEACE_FRAMES;
        if (frame >= PEACE_FRAMES)
            frame = 0;
        if (frame == m_PeaceFrame)
            return;
        m_PeaceFrame = frame;
        ImageWidget peace = ImageWidget.Cast(menu.Role("Peace"));
        if (peace && peace.LoadImageFile(0, SET + "peace_" + OZL_Text.Two(frame)))
            peace.SetImage(0);
    }

    // Блимання мокапа (blink 1s steps(2): 1 -> .6 -> .2 -> .6, чверть секунди кожне):
    // «★ NEW ★» підвалу, табличка «NEW!» доступного вузла і пісочний годинник того, що в ділі.
    protected void RunBlink(OZL_TreeMenu menu)
    {
        float f = m_Time - Math.Floor(m_Time);
        int step = f * 4;
        if (step > 3)
            step = 3;
        if (step == m_BlinkStep)
            return;
        m_BlinkStep = step;
        float a = BlinkAlpha();
        Fade(menu.Role("FootStarL"), a);
        Fade(menu.Role("FootNewText"), a);
        Fade(menu.Role("FootStarR"), a);
        Widget nodes = menu.Role("TreeNodes");
        if (!nodes)
            return;
        Widget cell = nodes.GetChildren();
        while (cell)
        {
            Widget tag = cell.FindAnyWidget("NodeNew");
            if (tag && tag.IsVisible())
                BlinkTag(cell);
            else if (Researching(menu, cell))
                Fade(cell.FindAnyWidget("NodeMark"), a);
            cell = cell.GetSibling();
        }
    }

    protected float BlinkAlpha()
    {
        if (m_BlinkStep <= 0)
            return 1;
        if (m_BlinkStep == 2)
            return BLINK_LOW;
        return BLINK_MID;
    }

    protected void BlinkTag(Widget cell)
    {
        float a = BlinkAlpha();
        Fade(cell.FindAnyWidget("NodeNewEdge"), a);
        Fade(cell.FindAnyWidget("NodeNewFill"), a);
        Fade(cell.FindAnyWidget("NodeMarkText"), a);
    }

    // Комірка cell:<id> вузла, що досліджується.
    protected bool Researching(OZL_TreeMenu menu, Widget cell)
    {
        string nm = cell.GetName();
        if (nm.IndexOf("cell:") != 0)
            return false;
        OZL_NodeView n = menu.NodeOf(nm.Substring(5, nm.Length() - 5));
        if (!n)
            return false;
        if (n.Status == "researching")
            return true;
        return false;
    }

    // Вузол під мишею -- та сама кнопка, на 8 % світліша (.node:hover .cell).
    protected void RunHover(OZL_TreeMenu menu)
    {
        string id = menu.HoveredId();
        if (id == m_HoverShown)
            return;
        Widget old = HoverFace(menu, m_HoverShown);
        if (old)
            old.Show(false);
        m_HoverShown = id;
        ImageWidget face = ImageWidget.Cast(HoverFace(menu, id));
        OZL_NodeView n = menu.NodeOf(id);
        if (!face || !n)
            return;
        if (face.LoadImageFile(0, SET + "face_" + n.Status + "_hover"))
        {
            face.SetImage(0);
            face.Show(true);
        }
    }

    protected Widget HoverFace(OZL_TreeMenu menu, string id)
    {
        Widget nodes = menu.Role("TreeNodes");
        if (!nodes || id == "")
            return null;
        Widget cell = nodes.FindAnyWidget("cell:" + id);
        if (!cell)
            return null;
        return cell.FindAnyWidget("NodeHoverFace");
    }

    // Натиснуті кнопки (:active мокапа): поки ліва кнопка миші тримається над кнопкою,
    // фаска навпаки -- у «Дослідити» (лише активної) і в обох кнопках помічника.
    protected void RunPress(OZL_TreeMenu menu)
    {
        int state = GetMouseState(MouseState.LEFT);
        bool held = false;
        if ((state & 0x80000000) != 0)
            held = true;
        bool down = false;
        if (held && m_BtnOn)
            down = Under(menu.Role("BtnResearch"));
        if (down != m_BtnDown)
        {
            m_BtnDown = down;
            Widget up = menu.Role("BtnUp");
            if (up)
                up.Show(!down);
            Widget pressed = menu.Role("BtnDown");
            if (pressed)
                pressed.Show(down);
        }
        bool next = false;
        if (held)
            next = Under(menu.Role("HelperNext"));
        if (next != m_NextDown)
        {
            m_NextDown = next;
            Bevel(menu, "HelperNext", next);
        }
        bool hide = false;
        if (held)
            hide = Under(menu.Role("HelperHide"));
        if (hide != m_HideDown)
        {
            m_HideDown = hide;
            Bevel(menu, "HelperHide", hide);
        }
    }

    protected void Bevel(OZL_TreeMenu menu, string prefix, bool down)
    {
        int hi = White;
        int lo = WinLo;
        if (down)
        {
            hi = WinLo;
            lo = White;
        }
        Paint(menu.Role(prefix + "Top"), hi);
        Paint(menu.Role(prefix + "Left"), hi);
        Paint(menu.Role(prefix + "Bottom"), lo);
        Paint(menu.Role(prefix + "Right"), lo);
    }

    // Помічник: хмарка за рядками підказки, кнопки за ширинами слів, листик під хмаркою
    // гойдається на BOB (f-bob) і моргає раз на 5 с (f-wink: 92 %..100 %), «Відчепись» --
    // згасає й опускається на HELP_DROP за 0.3 с і через 10 с від кліку повертається.
    protected void RunHelper(OZL_TreeMenu menu, float dt)
    {
        Widget root = menu.Role("HelperRoot");
        if (!root)
            return;
        float drop = 0;
        if (m_HelpState != 0)
        {
            m_HelpClock += dt;
            float k = 1;
            if (m_HelpState == 1)
            {
                k = 1 - m_HelpClock / FADE_SEC;
                if (k <= 0)
                {
                    k = 0;
                    m_HelpState = 2;
                    root.Show(false);
                }
            }
            else if (m_HelpState == 2)
            {
                k = 0;
                if (m_HelpClock >= HIDE_SEC)
                {
                    m_HelpState = 3;
                    root.Show(true);
                    HelperHits(menu, true);
                }
            }
            else
            {
                k = (m_HelpClock - HIDE_SEC) / FADE_SEC;
                if (k >= 1)
                {
                    k = 1;
                    m_HelpState = 0;
                }
                if (k < 0)
                    k = 0;
            }
            HelperAlpha(k);
            drop = HELP_DROP * (1 - k);
            menu.PlaceUnits(root, m_HelpX, m_HelpY + drop);
        }
        if (!root.IsVisible())
            return;

        int titles = VisibleLines(menu, "HelperTitle", 3);
        int texts = VisibleLines(menu, "HelperText", 5);
        if (titles != m_TitleLines || texts != m_TextLines || m_ButtonsPending)
            LayHelper(menu, titles, texts);

        float bob = BOB / 2 - BOB / 2 * Math.Cos(2 * Math.PI * m_Time / BOB_SEC);
        menu.PlaceUnits(menu.Role("HelperLeaf"), m_LeafX, m_BubbleH + LEAF_GAP - BOB - bob);

        float wink = m_Time / WINK_SEC;
        wink = (wink - Math.Floor(wink)) * WINK_SEC;
        int frame = 0;
        if (wink >= 4.6375 && wink < 4.7125)
            frame = 1;
        else if (wink >= 4.7125 && wink < 4.8125)
            frame = 2;
        else if (wink >= 4.8125 && wink < 4.9375)
            frame = 1;
        if (frame == m_LeafFrame)
            return;
        m_LeafFrame = frame;
        string pic = "leaf_open";
        if (frame == 1)
            pic = "leaf_half";
        else if (frame == 2)
            pic = "leaf_shut";
        ImageWidget leaf = ImageWidget.Cast(menu.Role("HelperLeaf"));
        if (leaf && leaf.LoadImageFile(0, SET + pic))
            leaf.SetImage(0);
    }

    // Хмарка (.fbubble): рамка й поле (m_Pad), заголовок, TITLE_GAP, текст, TEXT_GAP, кнопки,
    // знову рамка й поле. Середній зріз заходить на одиницю під обидва крайні (рядки там
    // однакові): стики, що лише торкаються, при 1.48 px на одиницю розходяться темною рискою.
    protected void LayHelper(OZL_TreeMenu menu, int titles, int texts)
    {
        float next = TextUnits(menu, "HelperNextText");
        float hide = TextUnits(menu, "HelperHideText");
        if (next <= 0 || hide <= 0)
            return;
        m_ButtonsPending = false;
        m_TitleLines = titles;
        m_TextLines = texts;
        float textY = m_Pad + titles * TIP_LINE + TITLE_GAP;
        PlaceY(menu, menu.Role("HelperText"), textY);
        float by = textY + texts * TIP_LINE + TEXT_GAP;
        float hideW = hide + BTN_PAD;
        float nextW = next + BTN_PAD;
        float hideX = m_InnerR - hideW;
        LayButton(menu, "HelperHide", hideX, by, hideW);
        LayButton(menu, "HelperNext", hideX - BTN_GAP - nextW, by, nextW);
        m_BubbleH = by + m_BtnH + m_Pad;
        Widget mid = menu.Role("BubbleMid");
        PlaceY(menu, mid, m_Slice - 1);
        menu.HeightUnits(mid, m_BubbleH - 2 * m_Slice + 2);
        PlaceY(menu, menu.Role("BubbleBot"), m_BubbleH - m_Slice);
    }

    // Кнопка хмарки: тло, фаска (світла згори й зліва), слово, клік -- на ширину слова + поле.
    protected void LayButton(OZL_TreeMenu menu, string prefix, float x, float y, float width)
    {
        float h = m_BtnH;
        menu.PlaceUnits(menu.Role(prefix + "Box"), x, y);
        menu.SizeUnits(menu.Role(prefix + "Box"), width, h);
        Part(menu, prefix + "Face", 0, 0, width, h);
        Part(menu, prefix + "Top", 0, 0, width, BEVEL_W);
        Part(menu, prefix + "Left", 0, 0, BEVEL_W, h);
        Part(menu, prefix + "Bottom", 0, h - BEVEL_W, width, BEVEL_W);
        Part(menu, prefix + "Right", width - BEVEL_W, 0, BEVEL_W, h);
        Part(menu, prefix + "Text", 0, 0, width, h);
        Part(menu, prefix, 0, 0, width, h);
    }

    protected void Part(OZL_TreeMenu menu, string role, float x, float y, float width, float height)
    {
        Widget part = menu.Role(role);
        menu.PlaceUnits(part, x, y);
        menu.SizeUnits(part, width, height);
    }

    protected void HelperHits(OZL_TreeMenu menu, bool on)
    {
        Widget next = menu.Role("HelperNext");
        if (next)
            next.Show(on);
        Widget hide = menu.Role("HelperHide");
        if (hide)
            hide.Show(on);
    }

    protected void HelperAlpha(float k)
    {
        for (int i = 0; i < m_HelpWidgets.Count(); i++)
        {
            Widget w = m_HelpWidgets[i];
            if (w)
                w.SetAlpha(m_HelpAlphas[i] * k);
        }
    }

    // Підказка: спершу своя -- за статусом вибраного вузла (renderHelper мокапа), далі
    // загальні по колу.
    protected void ShowTip(OZL_TreeMenu menu)
    {
        int at = m_TipIndex % TIPS;
        string title;
        string text;
        if (at == 0)
        {
            string own = OwnTip();
            title = OZL_Text.Words(own + "_TITLE");
            text = OZL_Text.Words(own + "_TEXT");
        }
        else
        {
            string general = "STR_OZL_SKIN_FREEDOM_HELP_GENERAL" + at.ToString();
            title = OZL_Text.Words(general + "_TITLE");
            text = OZL_Text.Words(general + "_TEXT");
        }
        menu.PutText(menu.Role("HelperTitle"), title, Ink);
        menu.PutText(menu.Role("HelperText"), text, Ink);
    }

    protected string OwnTip()
    {
        string stem = "STR_OZL_SKIN_FREEDOM_HELP_";
        if (!m_TipNode)
            return stem + "NONE";
        if (m_TipStatus == "available")
        {
            if (m_TipCan)
                return stem + "AVAILABLE";
            return stem + "NOLEADER";
        }
        if (m_TipStatus == "short")
            return stem + "SHORT";
        if (m_TipStatus == "locked")
            return stem + "LOCKED";
        if (m_TipStatus == "researching")
            return stem + "RESEARCHING";
        if (m_TipStatus == "completed")
            return stem + "DONE";
        return stem + "NONE";
    }

    // Підвал -- один ряд по центру з проміжком FOOT_GAP (.ffoot): лічильник, «★ NEW ★», два
    // посилання, копірайт із пацифіком. Ширини -- з текстів, раз, коли вони розкладені; кожна
    // частина -- завширшки зі свій текст (англійський копірайт довший за рамку файлу, і ☮
    // обрізало навпіл). Висоти й верхи -- з розкладки: ряд рухається лише вбік.
    protected void RunFooter(OZL_TreeMenu menu)
    {
        float label = TextUnits(menu, "FootCounterLabel");
        float word = TextUnits(menu, "FootNewText");
        float guest = TextUnits(menu, "FootGuestText");
        float links = TextUnits(menu, "FootLinksText");
        float copy = TextUnits(menu, "FootCopyText");
        bool ready = false;
        if (label > 0 && word > 0 && guest > 0 && links > 0 && copy > 0)
            ready = true;
        m_FootTries++;
        if (!ready && m_FootTries < 30)
            return;
        m_FootPending = false;
        float counter = label + FOOT_SPACE + m_CounterW;
        float blink = STAR_W + FOOT_SPACE + word + FOOT_SPACE + STAR_W;
        float tail = copy + FOOT_SPACE + PEACE_W;
        float x = (m_FootW - counter - blink - guest - links - tail - 4 * FOOT_GAP) / 2;
        PlaceX(menu, menu.Role("FootCounterLabel"), x);
        PlaceX(menu, menu.Role("FootCounter"), x + label + FOOT_SPACE);
        x += counter + FOOT_GAP;

        Widget fresh = menu.Role("FootNew");
        PlaceX(menu, fresh, x);
        PlaceX(menu, menu.Role("FootNewText"), STAR_W + FOOT_SPACE);
        Widget star = menu.Role("FootStarR");
        float starX = STAR_W + FOOT_SPACE + word + FOOT_SPACE;
        PlaceX(menu, star, starX);
        WidthUnits(menu, fresh, starX + WidthOf(menu, star));
        x += blink + FOOT_GAP;

        Widget guestBox = menu.Role("FootGuest");
        PlaceX(menu, guestBox, x);
        WidthUnits(menu, guestBox, guest);
        WidthUnits(menu, menu.Role("FootGuestLine"), guest);
        x += guest + FOOT_GAP;

        Widget linksBox = menu.Role("FootLinks");
        PlaceX(menu, linksBox, x);
        WidthUnits(menu, linksBox, links);
        WidthUnits(menu, menu.Role("FootLinksLine"), links);
        x += links + FOOT_GAP;

        Widget copyBox = menu.Role("FootCopy");
        PlaceX(menu, copyBox, x);
        Widget peace = menu.Role("FootPeace");
        PlaceX(menu, peace, copy + FOOT_SPACE);
        WidthUnits(menu, copyBox, copy + FOOT_SPACE + WidthOf(menu, peace));
    }

    // ------------------------------------------------------------------
    // Дрібниці
    // ------------------------------------------------------------------

    protected void SectionTag(OZL_TreeMenu menu, string tag, string head)
    {
        Widget box = menu.Role(tag);
        TextWidget word = TextWidget.Cast(menu.Role(head));
        if (!box || !word)
            return;
        bool shown = word.IsVisible();
        box.Show(shown);
        if (shown)
            menu.FitLater(word, menu.Role(tag + "Bg"), TAG_PAD, 0);
    }

    protected void Collect(Widget root)
    {
        if (!root)
            return;
        Widget c = root.GetChildren();
        while (c)
        {
            m_HelpWidgets.Insert(c);
            m_HelpAlphas.Insert(c.GetAlpha());
            Collect(c);
            c = c.GetSibling();
        }
    }

    protected int VisibleLines(OZL_TreeMenu menu, string stem, int most)
    {
        int n = 0;
        for (int i = 0; i < most; i++)
        {
            Widget line = menu.Role(stem + i.ToString());
            if (line && line.IsVisible())
                n++;
        }
        return n;
    }

    protected float TextUnits(OZL_TreeMenu menu, string role)
    {
        TextWidget t = TextWidget.Cast(menu.Role(role));
        if (!t)
            return 0;
        int pw;
        int ph;
        t.GetTextSize(pw, ph);
        return pw / menu.Px();
    }

    // Ширина тексту напису в одиницях (не напису: тексту в ньому).
    protected float TextOf(OZL_TreeMenu menu, Widget w)
    {
        TextWidget t = TextWidget.Cast(w);
        if (!t || menu.Px() <= 0)
            return 0;
        int pw;
        int ph;
        t.GetTextSize(pw, ph);
        return pw / menu.Px();
    }

    // Розмір і місце віджета в одиницях розкладки -- з екрана (до першого кадру там нулі).
    protected float WidthOf(OZL_TreeMenu menu, Widget w)
    {
        float width;
        float height;
        menu.UnitsOf(w, width, height);
        return width;
    }

    protected float HeightOf(OZL_TreeMenu menu, Widget w)
    {
        float width;
        float height;
        menu.UnitsOf(w, width, height);
        return height;
    }

    // Місце віджета в батькові: різниця їхніх екранних кутів.
    protected float XOf(OZL_TreeMenu menu, Widget w)
    {
        float x;
        float y;
        Offset(menu, w, x, y);
        return x;
    }

    protected float YOf(OZL_TreeMenu menu, Widget w)
    {
        float x;
        float y;
        Offset(menu, w, x, y);
        return y;
    }

    protected void Offset(OZL_TreeMenu menu, Widget w, out float x, out float y)
    {
        x = 0;
        y = 0;
        if (!w || menu.Px() <= 0)
            return;
        Widget parent = w.GetParent();
        if (!parent)
            return;
        float wx;
        float wy;
        float px;
        float py;
        w.GetScreenPos(wx, wy);
        parent.GetScreenPos(px, py);
        x = (wx - px) / menu.Px();
        y = (wy - py) / menu.Px();
    }

    // Посунути лише вбік або лише вгору-вниз: друга координата лишається з розкладки.
    protected void PlaceX(OZL_TreeMenu menu, Widget w, float x)
    {
        if (w)
            menu.PlaceUnits(w, x, YOf(menu, w));
    }

    protected void PlaceY(OZL_TreeMenu menu, Widget w, float y)
    {
        if (w)
            menu.PlaceUnits(w, XOf(menu, w), y);
    }

    // Нова ширина за тієї самої висоти; нерозкладений віджет (висота нуль) не чіпати.
    protected void WidthUnits(OZL_TreeMenu menu, Widget w, float width)
    {
        float oldW;
        float oldH;
        menu.UnitsOf(w, oldW, oldH);
        if (oldH > 0)
            menu.SizeUnits(w, width, oldH);
    }

    protected void BoldRole(OZL_TreeMenu menu, string role)
    {
        TextWidget t = TextWidget.Cast(menu.Role(role));
        if (t)
            t.SetBold(true);
    }

    protected static void BoldLines(Widget root, string stem, int most)
    {
        for (int i = 0; i < most; i++)
        {
            TextWidget t = TextWidget.Cast(root.FindAnyWidget(stem + i.ToString()));
            if (t)
                t.SetBold(true);
        }
    }

    protected static void Fade(Widget w, float a)
    {
        if (w)
            w.SetAlpha(a);
    }

    protected static void Paint(Widget w, int color)
    {
        if (w)
            w.SetColor(color);
    }

    // Чи миша над віджетом (екранні пікселі).
    protected static bool Under(Widget w)
    {
        if (!w || !w.IsVisibleHierarchy())
            return false;
        int mx;
        int my;
        GetMousePos(mx, my);
        float x;
        float y;
        float sw;
        float sh;
        w.GetScreenPos(x, y);
        w.GetScreenSize(sw, sh);
        if (mx < x || my < y)
            return false;
        if (mx >= x + sw || my >= y + sh)
            return false;
        return true;
    }
}

#endif
