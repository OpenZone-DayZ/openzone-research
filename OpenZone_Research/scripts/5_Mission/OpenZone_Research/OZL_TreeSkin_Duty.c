// Вікно duty -- «Реєстр досліджень» (Долг): армійський бланк на зеленому
// сукні. На аркуші -- реквізити (Долг, гриф «Для службового користування»,
// «Форма № 7-Д», «Затверджую»), заголовок розрядкою, «1. Перелік робіт» --
// реєстр-таблиця, «2. Фонди фракції» -- пул таблицею, «3. Схема послідовності
// робіт» -- дерево вниз у рамці, під нею легенда, внизу рядок виконавця.
// Праворуч на скріпці -- «Картка дослідження» з печаткою (ЗАТВЕРДЖЕНО /
// В РОБОТІ), підписом і полем «Закрити».
//
// Вузол -- графа бланка 160x50: номер у своїй клітинці, назва великими,
// ціна; закритий -- пунктир без заливки, доступний і в ділі -- подвійна
// червона рамка, досліджений -- сіріша заливка, вибраний -- червоний контур
// на 4 одиниці назовні, під мишею -- бліда червона облямівка; крапка проєкту
// блимає.
//
// Що робить цей клас понад дані: великі літери (CSS uppercase), розрядку
// (letter-spacing -- пробілами), жирний машинопис (SetBold на SDF-шрифті:
// на растровому він нічого не робить), друкарські вставки бланка, рядок
// «напрям:» під заголовком (із перемиканням гілок, коли їх кілька), реєстр
// (жирні рядки, сірий закритий, стан у два рядки, висота таблиці), край
// таблиці фондів і поле «Закрити».
//
// Розкладки: ozl_tree_duty, ozl_node_duty (ui/OpenZone_Research/);
// картинки: source/ui/duty/ (набір ozl_duty); кольори й шрифти:
// ui/tokens/duty.json. Числа нижче -- ті самі токени в ARGB.

#ifndef NO_GUI

// Шматок рядка бланка: друкарський (машинопис) чи бланковий, з пробілом
// перед ним чи без.
class OZL_DutyRun
{
    string Text;
    bool   Typed;
    bool   Space;

    void OZL_DutyRun(string text, bool typed, bool space)
    {
        Text  = text;
        Typed = typed;
        Space = space;
    }
}

// Написи, що стоять один за одним в одному контейнері: кожен -- за шириною
// свого тексту, з проміжком перед ним. Ставляться, щойно тексти мають
// ширину (наступні кадри).
class OZL_DutyLine
{
    static const float LETTER      = -1;   // проміжок завширшки з одну літеру GapRef
    static const float PREV_LETTER = -2;   // проміжок в одну літеру попереднього напису

    ref array<TextWidget> Parts;      // і порожні (null) -- щоб номери не з'їхали
    ref array<float>      Gaps;       // одиниці перед написом; LETTER, PREV_LETTER -- одна літера
    ref array<int>        Chars;      // скільки знаків у написі (моноширинний: ширина / знаки = літера)
    ref array<Widget>     Rules;      // лінійка під написом (порожня графа бланка) або null
    float      X;                     // лівий край рядка, коли Holder нема
    Widget     Holder;                // є -- рядок по центру цього контейнера
    TextWidget GapRef;                // напис з однієї літери: її ширина -- LETTER
    Widget     Hit;                   // кнопка поверх написів HitFrom..HitTo
    int        HitFrom;
    int        HitTo;
    int        Tries;

    void OZL_DutyLine(float x)
    {
        Parts   = new array<TextWidget>();
        Gaps    = new array<float>();
        Chars   = new array<int>();
        Rules   = new array<Widget>();
        X       = x;
        HitFrom = -1;
        HitTo   = -1;
        Tries   = 0;
    }

    void Add(TextWidget part, float gap, int chars, Widget rule)
    {
        Parts.Insert(part);
        Gaps.Insert(gap);
        Chars.Insert(chars);
        Rules.Insert(rule);
    }
}

class OZL_TreeSkin_Duty : OZL_TreeSkin
{
    static const string SET    = "set:ozl_duty image:";
    static const string COMMON = "set:ozl_common image:";

    // Скільки знаків жирного машинопису влазить у графу «Стан» (106 одиниць,
    // розмір 11: близько .59 S = 6.5 одиниці на знак).
    static const int   STATE_CHARS = 14;
    static const float ROW_H       = 24;   // рядок реєстру
    static const float ROW_H2      = 33;   // рядок зі станом у два рядки
    static const float REG_MAX     = 330;  // max-height реєстру мокапа
    static const float FUND_GAP    = 18;   // margin-top «2. Фонди фракції»

    int Faint;      // --faint: заглушка «??? невідомо», нуль пулу, замок
    int Edge;       // --edge: лінійки бланка, рамка чіпа
    int BtnOff;     // рамка неактивної кнопки (#b8b19c)
    int Glow;       // облямівка під мишею: --acc .25 мокапа, у лінійному світлі .42

    protected ref array<ref OZL_DutyLine> m_Lines;
    protected ref OZL_DutyLine m_SubLine;
    protected ref array<Widget> m_Blink;   // мітки проєктів, що блимають
    protected float m_Clock;
    protected int   m_BlinkStep;
    protected bool  m_CloseLit;            // «Закрити» під мишею
    protected bool  m_RegDirty;            // висота реєстру й місце фондів -- наступним кадром
    protected int   m_RegTries;
    protected bool  m_PoolDirty;           // нижній край таблиці фондів -- наступним кадром
    protected int   m_PoolTries;

    void OZL_TreeSkin_Duty()
    {
        Named("duty");
        Dir     = "down";
        NodeW   = 160;
        NodeH   = 50;
        Row     = 118;
        Col     = 178;
        Top     = 86;
        Side    = 24;
        AnchorX = 86;    // графа лежить у комірці 172x90 з (6, 20)
        AnchorY = 45;

        Txt      = ARGB(255,  30,  28,  25);
        Dim      = ARGB(255, 107, 101,  88);
        Acc      = ARGB(255, 165,  36,  26);
        Ok       = ARGB(255,  58,  53, 137);
        Bad      = ARGB(255, 184,  86,  15);
        LineDim  = ARGB(255, 163, 156, 138);
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255, 235, 230, 213);
        FogColor = ARGB(255, 220, 214, 194);
        Faint    = ARGB(255, 138, 133, 118);
        Edge     = ARGB(255,  60,  56,  48);
        BtnOff   = ARGB(255, 184, 177, 156);
        Glow     = ARGB(107, 165,  36,  26);

        // NodeShape -- не графа, а лише облямівка під мишею: слот 0 порожній,
        // слот 1 -- облямівка. Саму графу за статусом кладе PaintNode у NodeForm.
        Shapes.Insert(SET + "blank");
        Shapes.Insert(SET + "node_glow");
        ShapeHover = 1;
        // Мітки: замок / галка / крапка (спека §3) -- спільні фігури ozl_common.
        Marks.Insert(COMMON + "mark_lock");
        Marks.Insert(COMMON + "mark_check");
        Marks.Insert(COMMON + "mark_dot");

        // Смуга проєкту: зроблена клітинка заштрихована червоним, решта
        // порожня. Прозорий -- не 0: нуль меню читає як "узяти LineDim".
        SegOn  = Acc;
        SegOff = ARGB(0, 1, 0, 0);
        TipPadX = 9;
        // Чіп «Відкриває»: текст із 9 одиниць від лівого краю (рамка й поле
        // мокапа). Праворуч меню докладає 5 до ширини тексту, яку GetTextSize
        // жирного машинопису дає точно за кроками літер (стенд 2026-10-31:
        // чіп 97.2 = 9 + 11 x .583 x 13 + 5); після рамки це поле 5.4
        // одиниці чорнила проти 6 у мокапі.
        OpensPad = 5;

        m_Lines = new array<ref OZL_DutyLine>();
        m_Blink = new array<Widget>();
    }

    // ------------------------------------------------------------------
    // Текст
    // ------------------------------------------------------------------

    protected static string Words(string key)
    {
        return OZL_Text.Words(key);
    }

    // Розрядка: пробіл між знаками, `gap` пробілів -- між словами. Мокап дає
    // шапкам letter-spacing .12-.14em (між словами тоді ~.5em -- два
    // пробіли), заголовку й кнопці -- .3em (~.8em -- чотири), а пробіл
    // вузького шрифту -- близько .2em; так і друкували бланки. Знаки беремо
    // UTF-8 (SubstringUtf8): літеру не розірвати.
    static string Spread(string s, int gap = 2)
    {
        string res = "";
        int n = s.LengthUtf8();
        string prev = " ";
        for (int i = 0; i < n; i++)
        {
            string ch = s.SubstringUtf8(i, 1);
            if (ch == " ")
            {
                for (int g = 0; g < gap; g++)
                    res += " ";
                prev = ch;
                continue;
            }
            if (i > 0 && prev != " ")
                res += " ";
            res += ch;
            prev = ch;
        }
        return res;
    }

    protected static void SetTo(OZL_TreeMenu menu, string role, string text)
    {
        TextWidget t = TextWidget.Cast(menu.Role(role));
        if (t)
            t.SetText(text);
    }

    protected static void Tint(Widget root, string name, int color)
    {
        Widget w = root.FindAnyWidget(name);
        if (w)
            w.SetColor(color);
    }

    // Жирний машинопис (font-weight 700 мокапа). Працює лише на SDF-шрифті
    // (ozl_sdf_type32, токени duty_tb*): на растровому SetBold нічого не
    // робить (виміряно на стенді 2026-10-31).
    protected static void Bold(Widget root, string name, bool on)
    {
        if (!root)
            return;
        TextWidget t = TextWidget.Cast(root.FindAnyWidget(name));
        if (t)
            t.SetBold(on);
    }

    protected static void BoldRole(OZL_TreeMenu menu, string role)
    {
        TextWidget t = TextWidget.Cast(menu.Role(role));
        if (t)
            t.SetBold(true);
    }

    // Назва вузла -- великими (вузол, реєстр, картка): .lbl, .rrow, .cname.
    override string NodeNameText(string name)
    {
        return OZL_Text.Upper(name);
    }

    // Розділи картки -- великими, розрядкою (.sec: letter-spacing .14em).
    override string SectionText(string key)
    {
        return Spread(OZL_Text.Upper(Words(key)));
    }

    // Статус у картці -- великими, розрядкою (.cstat); підказка й реєстр
    // лишаються зі StatusText.
    override string CardStatusText(string status)
    {
        return Spread(OZL_Text.Upper(StatusText(status)));
    }

    // Слово кнопки -- те саме, що в меню, великими, розрядкою .3em (.go).
    override string ButtonText(string status, bool enabled)
    {
        return Spread(OZL_Text.Upper(super.ButtonText(status, enabled)), 4);
    }

    // Підписи тирів -- римські, розрядкою (.tierlab: letter-spacing .2em).
    override string TierText(int tier)
    {
        return Spread(OZL_Text.Roman(tier));
    }

    // ------------------------------------------------------------------
    // Вузол
    // ------------------------------------------------------------------

    override int ShapeColorOf(string status)
    {
        return Glow;
    }

    override int MarkColorOf(string status)
    {
        if (status == "locked")
            return Faint;
        return super.MarkColorOf(status);
    }

    // Графа за статусом (NodeForm), номер і назва жирні (закритий -- звичайні
    // й сірі, .st-locked), крапка проєкту блимає; решту робить база.
    override void PaintNode(OZL_TreeMenu menu, Widget cell, OZL_NodeView node, string status, bool selected)
    {
        super.PaintNode(menu, cell, node, status, selected);
        ImageWidget form = ImageWidget.Cast(cell.FindAnyWidget("NodeForm"));
        if (form)
        {
            string pic = "form_plain";
            if (status == "locked")
                pic = "form_locked";
            else if (status == "available" || status == "researching")
                pic = "form_open";
            else if (status == "completed")
                pic = "form_done";
            if (form.LoadImageFile(0, SET + pic))
                form.SetImage(0);
        }
        bool locked = status == "locked";
        TextWidget num = TextWidget.Cast(cell.FindAnyWidget("NodeNum"));
        if (num)
        {
            if (locked)
                num.SetColor(Dim);
            else
                num.SetColor(Txt);
            num.SetBold(!locked);
        }
        Bold(cell, "NodeName0", !locked);
        Bold(cell, "NodeName1", !locked);

        // Крапка проєкту блимає (.st-research .mark: blink 1s steps(2));
        // решта міток рівні.
        Widget mark = cell.FindAnyWidget("NodeMark");
        if (mark)
        {
            int at = BlinkIndex(mark);
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
    }

    protected int BlinkIndex(Widget w)
    {
        for (int i = 0; i < m_Blink.Count(); i++)
        {
            if (m_Blink[i] == w)
                return i;
        }
        return -1;
    }

    // ------------------------------------------------------------------
    // Реєстр, пул, вартість, «Відкриває», кнопка
    // ------------------------------------------------------------------

    // Рядок реєстру (лише видимі вузли, щільний номер -- база): усе жирним
    // машинописом великими; закритий -- сірий і звичайний (.rrow.st-locked);
    // стан, що не влазить, -- у два рядки (НЕ ВИСТАЧАЄ / РЕСУРСІВ), і тоді
    // рядок 33 одиниці. Висоту таблиці й місце фондів ставить OnUpdate.
    override void PaintRegistryRow(OZL_TreeMenu menu, Widget row, OZL_NodeView node, int number, int tier, bool selected)
    {
        super.PaintRegistryRow(menu, row, node, number, tier, selected);
        if (!node)
            return;
        bool locked = node.Status == "locked";
        int ink = Txt;
        if (locked)
            ink = Dim;
        Tint(row, "RegNum", ink);
        Tint(row, "RegName", ink);
        Tint(row, "RegTier", ink);
        Bold(row, "RegNum", !locked);
        Bold(row, "RegName", !locked);
        Bold(row, "RegTier", !locked);
        Bold(row, "RegState", !locked);
        Bold(row, "RegState2", !locked);

        string state = OZL_Text.Upper(StatusText(node.Status));
        string first = state;
        string second = "";
        if (state.LengthUtf8() > STATE_CHARS)
            SplitState(state, first, second);
        TextWidget st = TextWidget.Cast(row.FindAnyWidget("RegState"));
        if (st)
            st.SetText(first);
        TextWidget st2 = TextWidget.Cast(row.FindAnyWidget("RegState2"));
        if (st2)
        {
            st2.SetText(second);
            st2.SetColor(StatusColorOf(node.Status));
            st2.Show(second != "");
        }
        float h = ROW_H;
        if (second != "")
            h = ROW_H2;
        // Ширина рядка пропорційна (1 = уся таблиця), висота -- пікселі
        // екрана (SetSize бере пікселі, SKINS.md "Units").
        row.SetSize(1, h * menu.Px());
        m_RegDirty = true;
        m_RegTries = 0;
    }

    // Під мишею рядок реєстру тоне блідо-червоним (.rrow:hover), але не
    // вибраний: у мокапі .rrow.sel перекриває :hover. Рамка чіпа
    // «Відкриває» під мишею темніє до чорнила (.opens a:hover).
    override void OnRowHover(OZL_TreeMenu menu, Widget row, string kind, string id, bool on)
    {
        if (kind == "reg" && on && id == menu.SelectedId())
            on = false;
        super.OnRowHover(menu, row, kind, id, on);
        if (kind != "open" || !row)
            return;
        int chipInk = Edge;
        if (on)
            chipInk = Txt;
        Tint(row, "ChipBoxTop", chipInk);
        Tint(row, "ChipBoxBottom", chipInk);
        Tint(row, "ChipBoxLeft", chipInk);
        Tint(row, "ChipBoxRight", chipInk);
    }

    // Фонди: назва великими, рядок жирний; нуль -- сірий і звичайний, число
    // ще блідіше (.prow.zero, .prow.zero .pv).
    override void PaintPoolRow(OZL_TreeMenu menu, Widget row, int index, string line, int have, int color)
    {
        super.PaintPoolRow(menu, row, index, line, have, color);
        TextWidget name = TextWidget.Cast(row.FindAnyWidget("PoolName"));
        if (name)
            name.SetText(DataText(OZL_Text.Upper(menu.PointName(line))));
        if (have <= 0)
            Tint(row, "PoolValue", Faint);
        Bold(row, "PoolName", have > 0);
        Bold(row, "PoolValue", have > 0);
        m_PoolDirty = true;
        m_PoolTries = 0;
    }

    // Рядок вартості -- жирним машинописом великими (.crow).
    override void PaintCostRow(OZL_TreeMenu menu, Widget row, string label, string text, int verdict)
    {
        super.PaintCostRow(menu, row, DataText(OZL_Text.Upper(label)), text, verdict);
        Bold(row, "CostName", true);
        Bold(row, "CostValue", true);
    }

    // Чіп «Відкриває»: жирні великі в рамці; заглушка туману -- блідо і
    // рамка пунктиром (.opens a.fogged).
    override void PaintOpenChip(OZL_TreeMenu menu, Widget chip, string text, bool fogged)
    {
        super.PaintOpenChip(menu, chip, DataText(OZL_Text.Upper(text)), fogged);
        Bold(chip, "ChipText", true);
        if (fogged)
            Tint(chip, "ChipText", Faint);
        Widget box = chip.FindAnyWidget("ChipBoxLine");
        if (box)
            box.Show(!fogged);
        Widget dash = chip.FindAnyWidget("ChipDashLine");
        if (dash)
            dash.Show(fogged);
    }

    // Кнопка: подвійна рамка і текст червоні; неактивна -- сірі (.go:disabled).
    override void PaintButton(OZL_TreeMenu menu, Widget btn, bool enabled)
    {
        int text = LineDim;
        int frameInk = BtnOff;
        if (enabled)
        {
            text = Acc;
            frameInk = Acc;
        }
        TextWidget t = TextWidget.Cast(menu.Role("BtnResearchText"));
        if (t)
            t.SetColor(text);
        Widget frame = menu.Role("BtnResearchFrame");
        if (frame)
            frame.SetColor(frameInk);
    }

    // Печатка: ЗАТВЕРДЖЕНО на дослідженому, В РОБОТІ на тому, що в ділі;
    // обидві чорнилом --ok (колір у розкладці, $duty_seal).
    override string StampOf(string status)
    {
        if (status == "completed")
            return Words("STR_OZL_SKIN_DUTY_SEAL_DONE_IMG");
        if (status == "researching")
            return Words("STR_OZL_SKIN_DUTY_SEAL_WORK_IMG");
        return "";
    }

    // ------------------------------------------------------------------
    // Події
    // ------------------------------------------------------------------

    // Статичні тексти бланка: великими й розрядкою, де так у мокапі; картинки
    // мови гравця; жирний машинопис; друкарські вставки; легенда рядком.
    override void OnShow(OZL_TreeMenu menu)
    {
        SetTo(menu, "OrgName", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_ORG_NAME"))));
        SetTo(menu, "OrgUnit", OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_ORG_UNIT")));
        SetTo(menu, "ApproveHead", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_APPROVE"))));
        SetTo(menu, "RegHead", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_REGISTRY_HEAD"))));
        SetTo(menu, "FundHead", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_FUND_HEAD"))));
        SetTo(menu, "DevName", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_SCHEME_HEAD"))));
        SetTo(menu, "CardHeadText", Spread(Words("STR_OZL_SKIN_DUTY_CARD_HEAD")));
        // «Закрити» (мокап його не має; на прохання власника) -- як шапки
        // розділів: великими, розрядкою; рамка й слово -- чорнилом.
        SetTo(menu, "BtnCloseText", Spread(OZL_Text.Upper(Words("STR_OZL_TREE_CLOSE"))));
        PaintClose(menu, false);

        // Шапка реєстру: «№ п/п» мокап ламає після №.
        string num = OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_COL_NUM"));
        int cut = num.IndexOf(" ");
        if (cut > 0)
        {
            SetTo(menu, "ColNum0", num.Substring(0, cut));
            SetTo(menu, "ColNum1", num.Substring(cut + 1, num.Length() - cut - 1));
        }
        else
        {
            SetTo(menu, "ColNum0", num);
            SetTo(menu, "ColNum1", "");
        }
        SetTo(menu, "ColName", OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_COL_NAME")));
        SetTo(menu, "ColTier", OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_COL_TIER")));
        SetTo(menu, "ColState", OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_COL_STATE")));


        // Гриф і заголовок -- картинки мови гравця (рядки *_IMG); заголовок
        // живим текстом розрядкою лишається на випадок рядка не "set:...".
        Picture(menu, "Grif", Words("STR_OZL_SKIN_DUTY_GRIF_IMG"));
        string title = Words("STR_OZL_SKIN_DUTY_TITLE_IMG");
        bool pic = false;
        if (title.IndexOf("set:") == 0)
            pic = Picture(menu, "TitleImg", title);
        Widget titleImg = menu.Role("TitleImg");
        if (titleImg)
            titleImg.Show(pic);
        TextWidget titleText = TextWidget.Cast(menu.Role("TitleText"));
        if (titleText)
        {
            titleText.SetText(Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_TITLE")), 4));
            titleText.Show(!pic);
        }

        // Жирний машинопис, який не перемальовується: підказка, «напрям»,
        // час і причина в картці, порожня картка (рядки -- у своїх гачках).
        BoldRole(menu, "TreeTipText");
        BoldRole(menu, "BranchName");
        BoldRole(menu, "BranchSub");
        BoldRole(menu, "CardTime");
        BoldRole(menu, "CardWhy");
        BoldRole(menu, "CardEmptyText");
        BoldRole(menu, "CardEmptyHint");

        // Друкарські вставки: пробіл бланка -- 6/28 клітинки вузького шрифту;
        // порожня графа -- лінійкою (PutRuns).
        float sp17 = 17 * 6.0 / 28.0;
        float sp14 = 14 * 6.0 / 28.0;
        PutRuns(menu, "OrgRef", SplitLast(Words("STR_OZL_SKIN_DUTY_ORG_REF"), true), sp17);
        PutRuns(menu, "ApproveCmd", SplitFirst(Words("STR_OZL_SKIN_DUTY_APPROVE_CMD"), true), sp17);
        PutRuns(menu, "ApproveDate", SplitBlanks(Words("STR_OZL_SKIN_DUTY_APPROVE_DATE"), true), sp17);
        PutRuns(menu, "Executor", SplitExecutor(Words("STR_OZL_SKIN_DUTY_EXECUTOR")), sp14);
        // Підпис: CSS згортає подвійний пробіл ключа в один; уся стрічка --
        // машинопис 14, тож проміжок -- одна його літера (16/30 клітинки), а
        // графа підпису -- лінійкою, як графи бланка.
        string sign = Words("STR_OZL_SKIN_DUTY_SIGN");
        sign.Replace("  ", " ");
        PutRuns(menu, "CardSign", SplitBlanks(sign, false), 14 * 16.0 / 30.0);

        // Легенда -- рядом за шириною текстів, 14 одиниць між пунктами.
        menu.FlowLater(menu.Role("LegendRow"), 14, 0, false);

        m_Clock = 0;
        m_BlinkStep = -1;
        m_Blink.Clear();
        m_RegDirty = false;
        m_PoolDirty = false;
    }

    // Після кожного повного малювання: рядок «напрям:» під заголовком (назва
    // гілки й лічильник -- від меню; », коли гілок кілька) і край таблиці
    // фондів (OnUpdate).
    override void OnPaint(OZL_TreeMenu menu)
    {
        bool many = menu.BranchCount() > 1;
        Widget mark = menu.Role("BranchMark");
        if (mark)
            mark.Show(many);
        Widget next = menu.Role("DutyBranchNext");
        if (next)
            next.Show(many);

        if (m_SubLine)
            m_Lines.RemoveItem(m_SubLine);
        // "напрям: <гілка> [»] · <фракція · досліджено N з M>": по одній
        // літері машинопису між частинами (ширина SubDot), по центру рядка.
        m_SubLine = new OZL_DutyLine(0);
        m_SubLine.Holder = menu.Role("SubLine");
        m_SubLine.GapRef = TextWidget.Cast(menu.Role("SubDot"));
        m_SubLine.Add(TextWidget.Cast(menu.Role("SubDir")), 0, 0, null);
        m_SubLine.Add(TextWidget.Cast(menu.Role("BranchName")), OZL_DutyLine.LETTER, 0, null);
        m_SubLine.Add(TextWidget.Cast(mark), OZL_DutyLine.LETTER, 0, null);
        m_SubLine.Add(TextWidget.Cast(menu.Role("SubDot")), OZL_DutyLine.LETTER, 0, null);
        m_SubLine.Add(TextWidget.Cast(menu.Role("BranchSub")), OZL_DutyLine.LETTER, 0, null);
        if (many)
        {
            m_SubLine.Hit = next;
            m_SubLine.HitFrom = 1;
            m_SubLine.HitTo = 2;
        }
        m_Lines.Insert(m_SubLine);

        m_PoolDirty = true;
        m_PoolTries = 0;
    }

    // Меню щойно перемалювало картку (і перед нею -- реєстр).
    override void OnSelect(OZL_TreeMenu menu, OZL_NodeView node, string status, bool canResearch)
    {
        m_RegDirty = true;
        m_RegTries = 0;
        if (!node)
            return;
        // Лінійка під «Матеріали» і «Відкриває» -- разом із заголовком, який
        // меню ховає, коли розділ порожній.
        Follow(menu, "CardItemsRule", "CardItemsHead");
        Follow(menu, "CardOpensRule", "CardOpensHead");
        menu.RefreshCard();
    }

    // «Напрям» із » перемикає гілки по колу, коли їх більше однієї (у мокапі
    // гілка одна).
    override bool OnClick(OZL_TreeMenu menu, Widget w)
    {
        if (!w || w.GetName() != "DutyBranchNext")
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
        int nextAt = (at + 1) % count;
        if (view.Branches[nextAt])
            menu.PickBranch(view.Branches[nextAt].Id);
        return true;
    }

    override void OnUpdate(OZL_TreeMenu menu, float dt)
    {
        m_Clock += dt;
        for (int i = m_Lines.Count() - 1; i >= 0; i--)
        {
            if (LayLine(menu, m_Lines[i]))
                m_Lines.RemoveOrdered(i);
        }
        if (m_RegDirty && LayRegistry(menu))
            m_RegDirty = false;
        if (m_PoolDirty && LayPoolEdge(menu))
            m_PoolDirty = false;
        BlinkTick();
        CloseHover(menu);
    }

    // Крапка проєкту: blink 1 s steps(2) мокапа -- 1, .6, .2, .6 по чверті
    // секунди (як у Чистого неба); у лінійному світлі рушія ті ступені на
    // папері дають .8 і .35 (скіл gui-layouts §32).
    protected void BlinkTick()
    {
        int step = Math.Floor(Math.ModFloat(m_Clock, 1) * 4);
        if (step == m_BlinkStep)
            return;
        m_BlinkStep = step;
        float a = 1;
        if (step == 1 || step == 3)
            a = 0.8;
        else if (step == 2)
            a = 0.35;
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

    // Меню не повідомляє, коли миша над BtnClose, тож питаємо щокадру.
    protected void CloseHover(OZL_TreeMenu menu)
    {
        Widget btn = menu.Role("BtnClose");
        if (!btn)
            return;
        bool lit = GetWidgetUnderCursor() == btn;
        if (lit != m_CloseLit)
            PaintClose(menu, lit);
    }

    // Поле «Закрити»: чорнило, під мишею -- червоне з блідою червоною
    // заливкою, як кнопка «Дослідити» під мишею.
    protected void PaintClose(OZL_TreeMenu menu, bool lit)
    {
        m_CloseLit = lit;
        Widget closeBox = menu.Role("CloseBox");
        if (!closeBox)
            return;
        int ink = Txt;
        if (lit)
            ink = Acc;
        Tint(closeBox, "CloseTop", ink);
        Tint(closeBox, "CloseBottom", ink);
        Tint(closeBox, "CloseLeft", ink);
        Tint(closeBox, "CloseRight", ink);
        Tint(closeBox, "BtnCloseText", ink);
        Widget closeFill = closeBox.FindAnyWidget("CloseHover");
        if (closeFill)
            closeFill.Show(lit);
    }

    // ------------------------------------------------------------------
    // Реєстр і фонди: місця -- з самих віджетів
    // ------------------------------------------------------------------

    // Таблиця реєстру завширшки як у розкладці, заввишки -- сума рядків (до
    // 330, далі прокрутка); фонди -- на 18 під нею, на своєму x. Місця читає
    // з екрана, тож чекає, доки віджети розкладено; true -- готово.
    protected bool LayRegistry(OZL_TreeMenu menu)
    {
        Widget list = menu.Role("Registry");
        Widget scroll = menu.Role("RegScroll");
        if (!list || !scroll || !scroll.GetParent())
            return true;
        float px = menu.Px();
        float sw;
        float sh;
        menu.UnitsOf(scroll, sw, sh);
        if ((px <= 0 || sw <= 0) && m_RegTries < 60)
        {
            m_RegTries++;
            return false;
        }
        float total = 0;
        Widget row = list.GetChildren();
        while (row)
        {
            total += ROW_H;
            Widget two = row.FindAnyWidget("RegState2");
            if (two && two.IsVisible())
                total += ROW_H2 - ROW_H;
            row = row.GetSibling();
        }
        list.Update();
        float shown = total;
        if (shown > REG_MAX)
            shown = REG_MAX;
        menu.SizeUnits(scroll, sw, shown);

        Widget fund = menu.Role("FundBlock");
        if (!fund || px <= 0)
            return true;
        float ox;
        float oy;
        float sx;
        float sy;
        float fx;
        float fy;
        scroll.GetParent().GetScreenPos(ox, oy);
        scroll.GetScreenPos(sx, sy);
        fund.GetScreenPos(fx, fy);
        // Ще не розкладено: таблиця стоїть нижче верху аркуша, не на ньому.
        if (sy <= oy && m_RegTries < 60)
        {
            m_RegTries++;
            return false;
        }
        menu.PlaceUnits(fund, (fx - ox) / px, (sy - oy) / px + shown + FUND_GAP);
        return true;
    }

    // Нижній край таблиці фондів -- 1.5, як боки, поверх межі останнього
    // рядка (на одиницю вище його низу); порожній пул -- лише рамка з
    // написом (PoolEmpty, показує меню). true -- готово.
    protected bool LayPoolEdge(OZL_TreeMenu menu)
    {
        Widget pool = menu.Role("PoolList");
        Widget bottom = menu.Role("PoolBottom");
        if (!pool || !bottom || !bottom.GetParent())
            return true;
        Widget last = null;
        Widget c = pool.GetChildren();
        while (c)
        {
            last = c;
            c = c.GetSibling();
        }
        bottom.Show(last != null);
        if (!last)
            return true;
        float px = menu.Px();
        float lw;
        float lh;
        menu.UnitsOf(last, lw, lh);
        float ox;
        float oy;
        float lx;
        float ly;
        float ex;
        float ey;
        bottom.GetParent().GetScreenPos(ox, oy);
        last.GetScreenPos(lx, ly);
        bottom.GetScreenPos(ex, ey);
        // Рядок ще не розкладено (нуль заввишки чи на верху блоку, хоча
        // перший рядок стоїть під шапкою): наступного кадру.
        if ((px <= 0 || lh <= 0 || ly <= oy) && m_PoolTries < 60)
        {
            m_PoolTries++;
            return false;
        }
        if (px <= 0)
            return true;
        menu.PlaceUnits(bottom, (ex - ox) / px, (ly - oy) / px + lh - 1);
        return true;
    }

    // Стан у два рядки по словах: скільки слів влазить у перший.
    protected static void SplitState(string state, out string first, out string second)
    {
        array<string> parts = new array<string>();
        state.Split(" ", parts);
        first = "";
        second = "";
        for (int i = 0; i < parts.Count(); i++)
        {
            string cand = parts[i];
            if (first != "")
                cand = first + " " + parts[i];
            if (second == "" && (first == "" || cand.LengthUtf8() <= STATE_CHARS))
            {
                first = cand;
                continue;
            }
            if (second != "")
                second += " ";
            second += parts[i];
        }
    }

    // ------------------------------------------------------------------
    // Друкарські вставки бланка
    // ------------------------------------------------------------------

    // "Вих. № 0417/Д": останнє слово друкарське.
    protected static array<ref OZL_DutyRun> SplitLast(string text, bool upper)
    {
        array<ref OZL_DutyRun> runs = new array<ref OZL_DutyRun>();
        int at = text.LastIndexOf(" ");
        if (at < 0)
        {
            runs.Insert(new OZL_DutyRun(Form(text, upper), false, false));
            return runs;
        }
        runs.Insert(new OZL_DutyRun(Form(text.Substring(0, at), upper), false, false));
        runs.Insert(new OZL_DutyRun(text.Substring(at + 1, text.Length() - at - 1), true, true));
        return runs;
    }

    // "Командир ___________": усе після першого слова друкарське.
    protected static array<ref OZL_DutyRun> SplitFirst(string text, bool upper)
    {
        array<ref OZL_DutyRun> runs = new array<ref OZL_DutyRun>();
        int at = text.IndexOf(" ");
        if (at < 0)
        {
            runs.Insert(new OZL_DutyRun(Form(text, upper), false, false));
            return runs;
        }
        runs.Insert(new OZL_DutyRun(Form(text.Substring(0, at), upper), false, false));
        runs.Insert(new OZL_DutyRun(text.Substring(at + 1, text.Length() - at - 1), true, true));
        return runs;
    }

    // "«__» __________ р.": кожен відрізок підкреслень друкарський, решта --
    // бланк; пробіли на межах стають проміжками.
    protected static array<ref OZL_DutyRun> SplitBlanks(string text, bool upper)
    {
        array<ref OZL_DutyRun> runs = new array<ref OZL_DutyRun>();
        int n = text.Length();
        int start = 0;
        bool space = false;
        while (start < n)
        {
            bool typed = false;
            if (text.Get(start) == "_")
                typed = true;
            int end = start + 1;
            while (end < n)
            {
                bool blank = false;
                if (text.Get(end) == "_")
                    blank = true;
                if (blank != typed)
                    break;
                end++;
            }
            string piece = text.Substring(start, end - start);
            if (typed)
            {
                runs.Insert(new OZL_DutyRun(piece, true, space));
                space = false;
            }
            else
            {
                // Пробіл на початку -- проміжок перед шматком, у кінці -- перед
                // наступним (байти пробілу й "_" ніколи не стоять усередині
                // UTF-8 літери).
                if (piece.IndexOf(" ") == 0)
                    space = true;
                bool tail = false;
                if (piece.LastIndexOf(" ") == piece.Length() - 1)
                    tail = true;
                piece = piece.Trim();
                if (piece != "")
                    runs.Insert(new OZL_DutyRun(Form(piece, upper), false, space));
                space = tail;
            }
            start = end;
        }
        return runs;
    }

    // "Виконавець ст. сержант ________ · тел. 2-14 · прим. № 1": від другого
    // слова до останнього підкреслення -- друкарське: звання і порожня графа
    // окремими шматками (графу PutRuns малює лінійкою).
    protected static array<ref OZL_DutyRun> SplitExecutor(string text)
    {
        array<ref OZL_DutyRun> runs = new array<ref OZL_DutyRun>();
        int at = text.IndexOf(" ");
        if (at < 0)
        {
            runs.Insert(new OZL_DutyRun(text, false, false));
            return runs;
        }
        runs.Insert(new OZL_DutyRun(text.Substring(0, at), false, false));
        string rest = text.Substring(at + 1, text.Length() - at - 1);
        int blank = rest.LastIndexOf("_");
        if (blank < 0)
        {
            runs.Insert(new OZL_DutyRun(rest, false, true));
            return runs;
        }
        int blankFrom = rest.IndexOf("_");
        string rank = rest.Substring(0, blankFrom);
        rank = rank.Trim();
        if (rank != "")
            runs.Insert(new OZL_DutyRun(rank, true, true));
        runs.Insert(new OZL_DutyRun(rest.Substring(blankFrom, blank - blankFrom + 1), true, true));
        string tail = rest.Substring(blank + 1, rest.Length() - blank - 1);
        bool space = false;
        if (tail.IndexOf(" ") == 0)
            space = true;
        tail = tail.Trim();
        if (tail != "")
            runs.Insert(new OZL_DutyRun(tail, false, space));
        return runs;
    }

    protected static string Form(string text, bool upper)
    {
        if (upper)
            return OZL_Text.Upper(text);
        return text;
    }

    // Шматки -- у написи контейнера: бланкові в <Line>N0, N1..., друкарські
    // (жирний машинопис) в <Line>T0, T1...; зайві ховаються; ставить
    // OnUpdate. Порожня графа (самі підкреслення) -- прозорий напис і
    // лінійка <Line>R<n> під ним: підкреслення PT Mono, на відміну від
    // Courier мокапа, у лінію не зливаються. Проміжок між двома
    // друкарськими шматками -- одна їхня літера, між іншими -- space.
    protected void PutRuns(OZL_TreeMenu menu, string line, array<ref OZL_DutyRun> runs, float space)
    {
        Widget box = menu.Role(line);
        if (!box)
            return;
        OZL_DutyLine job = new OZL_DutyLine(0);
        int nextN = 0;
        int nextT = 0;
        bool placed = false;
        bool prevTyped = false;
        for (int i = 0; i < runs.Count(); i++)
        {
            OZL_DutyRun run = runs[i];
            string slotName = line + "N" + nextN.ToString();
            if (run.Typed)
                slotName = line + "T" + nextT.ToString();
            TextWidget t = TextWidget.Cast(box.FindAnyWidget(slotName));
            if (!t)
                continue;
            Widget rule = null;
            if (run.Typed)
            {
                rule = box.FindAnyWidget(line + "R" + nextT.ToString());
                nextT++;
                t.SetBold(true);
                bool blank = IsBlank(run.Text);
                if (blank)
                    t.SetAlpha(0);
                else
                    t.SetAlpha(1);
                if (rule)
                {
                    rule.Show(blank);
                    if (!blank)
                        rule = null;
                }
            }
            else
            {
                nextN++;
            }
            t.SetText(run.Text);
            t.Show(true);
            float gap = 0;
            if (run.Space && placed)
            {
                gap = space;
                if (run.Typed && prevTyped)
                    gap = OZL_DutyLine.PREV_LETTER;
            }
            job.Add(t, gap, run.Text.LengthUtf8(), rule);
            placed = true;
            prevTyped = run.Typed;
        }
        HideFrom(box, line + "N", nextN);
        HideFrom(box, line + "T", nextT);
        HideFrom(box, line + "R", nextT);
        m_Lines.Insert(job);
    }

    // Порожня графа: самі підкреслення.
    protected static bool IsBlank(string text)
    {
        if (text == "")
            return false;
        for (int i = 0; i < text.Length(); i++)
        {
            if (text.Get(i) != "_")
                return false;
        }
        return true;
    }

    protected static void HideFrom(Widget box, string stem, int from)
    {
        for (int i = from; i < 8; i++)
        {
            Widget w = box.FindAnyWidget(stem + i.ToString());
            if (!w)
                return;
            w.Show(false);
        }
    }

    // Поставити рядок, коли всі його видимі написи (і контейнер, і літера
    // проміжку) мають ширину; true -- поставлено (чи чекати вже годі). Кожен
    // напис лишається на своїй висоті з розкладки; лінійка графи лягає під
    // свій напис на всю його ширину; кнопка Hit -- на написи HitFrom..HitTo.
    protected bool LayLine(OZL_TreeMenu menu, OZL_DutyLine line)
    {
        float px = menu.Px();
        if (px <= 0)
            return false;
        float letter = 0;
        if (line.GapRef)
        {
            int lw;
            int lh;
            line.GapRef.GetTextSize(lw, lh);
            if (lw <= 0 && line.Tries < 60)
            {
                line.Tries++;
                return false;
            }
            letter = lw / px;
        }
        float boxW = 0;
        if (line.Holder)
        {
            float boxH;
            menu.UnitsOf(line.Holder, boxW, boxH);
            if (boxW <= 0 && line.Tries < 60)
            {
                line.Tries++;
                return false;
            }
        }
        array<float> widths = new array<float>();
        array<float> gaps = new array<float>();
        float total = 0;
        bool first = true;
        float prevW = 0;
        int prevChars = 0;
        int i;
        for (i = 0; i < line.Parts.Count(); i++)
        {
            TextWidget t = line.Parts[i];
            float w = 0;
            float g = 0;
            if (t && t.IsVisible())
            {
                float sw;
                float sh;
                t.GetScreenSize(sw, sh);
                int pw;
                int ph;
                t.GetTextSize(pw, ph);
                if ((sw <= 0 || pw <= 0) && line.Tries < 60)
                {
                    line.Tries++;
                    return false;
                }
                // Лінійку, яку щойно показали, теж треба розкласти: висота
                // береться з неї.
                Widget ruled = line.Rules[i];
                if (ruled && ruled.IsVisible() && line.Tries < 60)
                {
                    float uw;
                    float uh;
                    menu.UnitsOf(ruled, uw, uh);
                    if (uh <= 0)
                    {
                        line.Tries++;
                        return false;
                    }
                }
                w = pw / px;
                if (!first)
                {
                    g = line.Gaps[i];
                    if (g == OZL_DutyLine.PREV_LETTER)
                    {
                        // Моноширинний шрифт: ширина / знаки = одна літера.
                        g = letter;
                        if (prevChars > 0)
                            g = prevW / prevChars;
                    }
                    else if (g < 0)
                    {
                        g = letter;
                    }
                }
                first = false;
                total += g + w;
                prevW = w;
                prevChars = line.Chars[i];
            }
            widths.Insert(w);
            gaps.Insert(g);
        }
        float x = line.X;
        if (line.Holder)
            x = boxW / 2 - total / 2;
        float hitL = -1;
        float hitR = -1;
        for (i = 0; i < line.Parts.Count(); i++)
        {
            TextWidget p = line.Parts[i];
            if (!p || !p.IsVisible())
                continue;
            x += gaps[i];
            menu.PlaceUnits(p, x, YIn(p, px));
            Widget rule = line.Rules[i];
            if (rule && rule.IsVisible())
            {
                float rw;
                float rh;
                menu.UnitsOf(rule, rw, rh);
                menu.PlaceUnits(rule, x, YIn(rule, px));
                if (rh > 0)
                    menu.SizeUnits(rule, widths[i], rh);
            }
            if (i == line.HitFrom)
                hitL = x;
            x += widths[i];
            if (i == line.HitTo)
                hitR = x;
        }
        if (line.Hit && hitL >= 0 && hitR > hitL)
        {
            float hitW;
            float hitH;
            menu.UnitsOf(line.Parts[line.HitFrom], hitW, hitH);
            menu.PlaceUnits(line.Hit, hitL, YIn(line.Hit, px));
            menu.SizeUnits(line.Hit, hitR - hitL, hitH);
        }
        return true;
    }

    // Висота віджета в батьку, одиниці: з екрана (SetPos і GetScreenPos --
    // пікселі, SKINS.md "Units"), тож читається, коли віджет розкладено.
    protected static float YIn(Widget w, float px)
    {
        Widget up = w.GetParent();
        if (!up || px <= 0)
            return 0;
        float wx;
        float wy;
        float ox;
        float oy;
        w.GetScreenPos(wx, wy);
        up.GetScreenPos(ox, oy);
        return (wy - oy) / px;
    }

    // ------------------------------------------------------------------
    // Дрібниці
    // ------------------------------------------------------------------

    // Картинка мови гравця в ImageWidget ролі (рядок *_IMG stringtable).
    protected static bool Picture(OZL_TreeMenu menu, string role, string image)
    {
        ImageWidget w = ImageWidget.Cast(menu.Role(role));
        if (!w || image == "")
            return false;
        if (!w.LoadImageFile(0, image))
            return false;
        w.SetImage(0);
        return true;
    }

    // `what` видно тоді й лише тоді, коли видно `leader`.
    protected static void Follow(OZL_TreeMenu menu, string what, string leader)
    {
        Widget w = menu.Role(what);
        Widget h = menu.Role(leader);
        if (w && h)
            w.Show(h.IsVisible());
    }
}

#endif
