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
// Анімації -- в OnUpdate: бігучий рядок, кадри пацифіка, блимання «NEW», помічник
// (гойдання, моргання, «Відчепись» на 10 с), світліший вузол під мишею, натиснуті кнопки.
// Жирний, курсив і світіння рушій дає лише SDF-шрифтам (SetBold / SetItalic / тінь тексту на
// бітмапових нічого не роблять, виміряно 2026-10-31), тож жирний Comic (назви вузлів, статус,
// кнопка, «Сторінка в розробці!»), жирний і курсивний Times, жирний Courier табло (PT Mono) і
// Impact назви гілки зі світінням -- шрифти ozl_sdf_*. Напівпрозорі кольори виправлено під
// лінійне змішування рушія (чорний шар a -> 1 - (1 - a)^2.2, світлий на темному -> a^2.2).

#ifndef NO_GUI

class OZL_TreeSkin_Freedom : OZL_TreeSkin
{
    static const string SET = "set:ozl_freedom image:";
    static const float MARQUEE_SEC  = 26;     // прохід бігучого рядка (f-marquee)
    static const float MARQUEE_Y    = -2.62;  // верх рядка в рамці: SDF-напис 1.562 x 20 заввишки
    static const float PEACE_SEC    = 6;      // оберт пацифіка (f-spin)
    static const int   PEACE_FRAMES = 16;
    static const float BOB_SEC      = 2.4;    // гойдання листика (f-bob)
    static const float WINK_SEC     = 5;      // моргання (f-wink)
    static const float HIDE_SEC     = 10;     // «Відчепись»
    static const float FADE_SEC     = 0.3;    // .fhelp { transition: .3s }
    static const float TIP_LINE     = 18.2;   // рядок хмарки: Verdana 14 / 1.3
    static const float NAME_LINE    = 37;     // рядок назви в картці (Impact 30)
    static const int   TIPS         = 6;      // своя підказка вузла + п'ять загальних
    static const float LED_Y        = -0.75;  // верх цифри табло в рядку пулу (SDF PT Mono 20)
    static const float BRANCH_ROW   = 24;     // рядок гілки в меню
    // Блимання мокапа гасить до прозорості .2; рушій змішує лінійно, тож світле на темному
    // треба .2^2.2 = .03, щоб видно було стільки ж.
    static const float BLINK_DIM    = 0.03;
    // Світіння (тінь тексту SDF): табло -- 0 0 6px rgba(255,48,48,.8) мокапа, назва гілки --
    // 0 0 8px #ff00ff. Розмір і непрозорість -- з виміру СОП (4/.45 ледь, 8/1.0 сильно).
    static const int   LED_GLOW     = 5;
    static const float LED_GLOW_A   = 0.6;
    static const int   NAME_GLOW    = 7;
    static const float NAME_GLOW_A  = 0.75;

    // Кольори поза базовою палітрою (ARGB; токени freedom_* у ui/tokens/freedom.json).
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
    protected float  m_MarqueeW;
    protected int    m_PeaceFrame;
    protected bool   m_BlinkOn;
    protected string m_HoverShown;
    protected bool   m_BtnOn;
    protected bool   m_BtnDown;
    protected bool   m_NextDown;
    protected bool   m_HideDown;
    protected bool   m_FootPending;
    protected int    m_FootTries;
    protected int    m_NameLines;
    protected float  m_SkyH;

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
                menu.FitLater(word, cell.FindAnyWidget("NodeNewEdge"), 10, 0);
                menu.FitLater(word, cell.FindAnyWidget("NodeNewFill"), 8, 0);
                BlinkTag(cell);
            }
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

    // Цифри табло справа наліво по слотах PoolDigit0.. (0 -- крайній правий) через 13.8
    // одиниці, як жирний Courier 18 з letter-spacing 3 у мокапі (тут жирний PT Mono SDF); від
    // п'яти цифр -- тісніше, у ту саму коробку. Сяйво (text-shadow мокапа) -- тінь тексту SDF.
    protected void LedDigits(OZL_TreeMenu menu, Widget row, string digits, int ink, bool lit)
    {
        int n = digits.Length();
        if (n > 6)
        {
            digits = "999999";
            n = 6;
        }
        float pitch = 13.8;
        float right = 279.6;
        if (n > 4)
        {
            pitch = 56.0 / n;
            right = 292 - pitch / 2;
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
            if (n > 4)
                menu.PlaceUnits(digit, right - pitch * i - 7, LED_Y);
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
        m_BlinkOn        = true;
        m_HoverShown     = "";
        m_BtnDown        = false;
        m_NextDown       = false;
        m_HideDown       = false;
        m_NameLines      = 1;
        m_TitleLines     = 0;
        m_TextLines      = 0;
        m_ButtonsPending = true;
        m_BubbleH        = 130.34;
        m_LeafFrame      = 0;
        m_HelpState      = 0;
        m_HelpClock      = 0;
        m_TipKey         = "-";
        m_TipIndex       = 0;

        // Заголовок мовою гравця і символи обабіч нього на відстані 26: ширина напису в
        // мокапі -- 637.08 (укр.) і 450.95 (англ.), центр -- 800.
        string art = OZL_Text.Words("STR_OZL_SKIN_FREEDOM_WORDART_IMG");
        ImageWidget wordart = ImageWidget.Cast(menu.Role("WordArt"));
        if (wordart && wordart.LoadImageFile(0, art))
            wordart.SetImage(0);
        float half = 318.54;
        if (art.IndexOf("wordart_en") >= 0)
            half = 225.475;
        menu.PlaceUnits(menu.Role("Peace"), 800 - half - 26 - 66, 13);
        menu.PlaceUnits(menu.Role("Leaf"), 800 + half + 26, 13);

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

        menu.FlowLater(menu.Role("LegendRow"), 14, 0, false);

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
                menu.FlowLater(row.FindAnyWidget("RowFlow"), 9.5, 0, false);
                row = row.GetSibling();
            }
        }
        // Список гілок -- на стільки рядків, скільки гілок (24 одиниці), далі проміжок 8 і бали;
        // низ балів -- над хмаркою помічника.
        int n = menu.BranchCount();
        if (n < 1)
            n = 1;
        menu.SizeUnits(menu.Role("BranchScroll"), 308, BRANCH_ROW * n);
        Widget branches = menu.Role("BranchScroll");
        if (branches)
            branches.Update();
        float top = 40 + BRANCH_ROW * n + 8;
        menu.PlaceUnits(menu.Role("PoolSection"), 5, top);
        float room = 357 - top - 35;
        if (room < 110)
            room = 110;
        menu.SizeUnits(menu.Role("PoolScroll"), 308, room);

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
        m_NameLines = n;
        menu.SizeUnits(menu.Role("CardNameBox"), 382, NAME_LINE * n);
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
        RunMarquee(menu);
        RunPeace(menu);
        RunBlink(menu);
        RunHelper(menu, dt);
        RunHover(menu);
        RunPress(menu);
        if (m_FootPending)
            RunFooter(menu);
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
        float width = m_MarqueeW;
        if (width <= 0)
            width = 1532;
        float t = m_Time / MARQUEE_SEC;
        t = t - Math.Floor(t);
        menu.PlaceUnits(text, 1600 - (1600 + width) * t, MARQUEE_Y);
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

    // Блимання мокапа (blink 1s steps(2)): пів секунди видно, пів -- прозорість .2 (тут
    // BLINK_DIM: лінійне змішування).
    protected void RunBlink(OZL_TreeMenu menu)
    {
        float f = m_Time - Math.Floor(m_Time);
        bool on = f < 0.5;
        if (on == m_BlinkOn)
            return;
        m_BlinkOn = on;
        float a = BLINK_DIM;
        if (on)
            a = 1;
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
            cell = cell.GetSibling();
        }
    }

    protected void BlinkTag(Widget cell)
    {
        float a = BLINK_DIM;
        if (m_BlinkOn)
            a = 1;
        Fade(cell.FindAnyWidget("NodeNewEdge"), a);
        Fade(cell.FindAnyWidget("NodeNewFill"), a);
        Fade(cell.FindAnyWidget("NodeMarkText"), a);
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
    // гойдається на 6 одиниць (f-bob) і моргає раз на 5 с (f-wink: 92 %..100 %), «Відчепись»
    // -- згасає й опускається на 20 за 0.3 с і через 10 с від кліку повертається.
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
            drop = 20 * (1 - k);
            menu.PlaceUnits(root, 40, 500 + drop);
        }
        if (!root.IsVisible())
            return;

        int titles = VisibleLines(menu, "HelperTitle", 3);
        int texts = VisibleLines(menu, "HelperText", 5);
        if (titles != m_TitleLines || texts != m_TextLines || m_ButtonsPending)
            LayHelper(menu, titles, texts);

        float bob = 3 - 3 * Math.Cos(2 * Math.PI * m_Time / BOB_SEC);
        menu.PlaceUnits(menu.Role("HelperLeaf"), 138, m_BubbleH + 4 - 6 - bob);

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

    // Хмарка: 1 рамка + 10 поля, заголовок, 4, текст, 8, кнопки 23.6, 10 + 1 знизу (.fbubble).
    protected void LayHelper(OZL_TreeMenu menu, int titles, int texts)
    {
        float next = TextUnits(menu, "HelperNextText");
        float hide = TextUnits(menu, "HelperHideText");
        if (next <= 0 || hide <= 0)
            return;
        m_ButtonsPending = false;
        m_TitleLines = titles;
        m_TextLines = texts;
        float textY = 11 + titles * TIP_LINE + 4;
        menu.PlaceUnits(menu.Role("HelperText"), 13, textY);
        float by = textY + texts * TIP_LINE + 8;
        float hideW = hide + 24;
        float nextW = next + 24;
        float hideX = 249 - hideW;
        LayButton(menu, "HelperHide", hideX, by, hideW);
        LayButton(menu, "HelperNext", hideX - 8 - nextW, by, nextW);
        m_BubbleH = by + 23.6 + 11;
        menu.SizeUnits(menu.Role("BubbleMid"), 266, m_BubbleH - 24);
        menu.PlaceUnits(menu.Role("BubbleBot"), 0, m_BubbleH - 12);
    }

    // Кнопка хмарки: тло, фаска 2 (світла згори й зліва), слово, клік -- на ширину слова + 24.
    protected void LayButton(OZL_TreeMenu menu, string prefix, float x, float y, float width)
    {
        float h = 23.6;
        menu.PlaceUnits(menu.Role(prefix + "Box"), x, y);
        menu.SizeUnits(menu.Role(prefix + "Box"), width, h);
        Part(menu, prefix + "Face", 0, 0, width, h);
        Part(menu, prefix + "Top", 0, 0, width, 2);
        Part(menu, prefix + "Left", 0, 0, 2, h);
        Part(menu, prefix + "Bottom", 0, h - 2, width, 2);
        Part(menu, prefix + "Right", width - 2, 0, 2, h);
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
        for (int i = 0; i < 3; i++)
        {
            TextWidget line = TextWidget.Cast(menu.Role("HelperTitle" + i.ToString()));
            if (line)
                line.SetBold(true);
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

    // Підвал -- один ряд по центру з проміжком 18 (.ffoot): лічильник, «★ NEW ★», два
    // посилання, копірайт із пацифіком. Ширини -- з текстів, раз, коли вони розкладені.
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
        float sp = 4;          // пробіл шрифту підвалу
        float star = 10.84;    // ★ Verdana 13
        float counter = label + sp + 98;
        float blink = star + sp + word + sp + star;
        float tail = copy + sp + 11.2;
        float x = (1600 - counter - blink - guest - links - tail - 4 * 18) / 2;
        menu.PlaceUnits(menu.Role("FootCounterLabel"), x, 16.5);
        menu.PlaceUnits(menu.Role("FootCounter"), x + label + sp, 13);
        x += counter + 18;
        menu.PlaceUnits(menu.Role("FootNew"), x, 16.5);
        menu.PlaceUnits(menu.Role("FootNewText"), star + sp, 0);
        menu.PlaceUnits(menu.Role("FootStarR"), star + sp + word + sp, -0.5);
        x += blink + 18;
        menu.PlaceUnits(menu.Role("FootGuest"), x, 17);
        menu.SizeUnits(menu.Role("FootGuestLine"), guest, 1);
        x += guest + 18;
        menu.PlaceUnits(menu.Role("FootLinks"), x, 17);
        menu.SizeUnits(menu.Role("FootLinksLine"), links, 1);
        x += links + 18;
        menu.PlaceUnits(menu.Role("FootCopy"), x, 16.5);
        menu.PlaceUnits(menu.Role("FootPeace"), copy + sp, -0.5);
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
            menu.FitLater(word, menu.Role(tag + "Bg"), 12, 0);
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
