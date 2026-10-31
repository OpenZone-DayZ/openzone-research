// Вікно duty -- «Реєстр досліджень» (Долг): армійський бланк на зеленому
// сукні. На аркуші -- реквізити (Долг, гриф «Для службового користування»,
// «Форма № 7-Д», «Затверджую»), заголовок розрядкою, «1. Перелік робіт» --
// реєстр-таблиця, «2. Фонди фракції» -- пул таблицею, «3. Схема послідовності
// робіт» -- дерево вниз у рамці, внизу рядок виконавця. Праворуч на скріпці --
// «Картка дослідження» з печаткою (ЗАТВЕРДЖЕНО / В РОБОТІ) і підписом.
//
// Вузол -- графа бланка 160x50: номер у своїй клітинці, назва великими,
// ціна; закритий -- пунктир без заливки, доступний і в ділі -- подвійна
// червона рамка, досліджений -- сіріша заливка, вибраний -- червоний контур
// на 4 одиниці назовні, під мишею -- бліда червона облямівка.
//
// Що робить цей клас понад дані: великі літери (CSS uppercase), розрядку
// (letter-spacing -- пробілами), друкарські вставки бланка (машинопис у
// рядках «Вих. № 0417/Д», «Командир ___», дата, виконавець), рядок «напрям:»
// під заголовком, реєстр (сірі рядки, стан у два рядки, висота таблиці) і
// печатку.
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
    ref array<TextWidget> Parts;
    ref array<float>      Gaps;
    float X;        // лівий край або центр рядка, одиниці контейнера
    bool  Center;
    int   Tries;

    void OZL_DutyLine(float x, bool center)
    {
        Parts  = new array<TextWidget>();
        Gaps   = new array<float>();
        X      = x;
        Center = center;
        Tries  = 0;
    }

    void Add(TextWidget part, float gap)
    {
        if (!part)
            return;
        Parts.Insert(part);
        Gaps.Insert(gap);
    }
}

class OZL_TreeSkin_Duty : OZL_TreeSkin
{
    static const string SET    = "set:ozl_duty image:";
    static const string COMMON = "set:ozl_common image:";

    // Скільки знаків машинопису влазить у графу «Стан» (106 одиниць, розмір
    // 12, крок PT Mono 16/30 клітинки = 6.4 одиниці).
    static const int   STATE_CHARS = 16;
    static const float ROW_H       = 24;   // рядок реєстру
    static const float ROW_H2      = 33;   // рядок зі станом у два рядки
    static const float REG_TOP     = 276;  // реєстр на аркуші (RegScroll)
    static const float REG_MAX     = 330;  // max-height реєстру мокапа
    static const float FUND_GAP    = 18;   // margin-top «2. Фонди фракції»
    static const float POOL_ROW_H  = 26;

    int Faint;      // --faint: заглушка «??? невідомо», нуль пулу, замок
    int BtnOff;     // рамка неактивної кнопки (#b8b19c)
    int Glow;       // облямівка під мишею (--acc .25)
    int SealDone;   // печатка ЗАТВЕРДЖЕНО: чорнило --ok, opacity .72
    int SealWork;   // печатка В РОБОТІ: те саме чорнило --ok -- мокап так і малює
                    // (.c-stamp.on { color: var(--ok) !important } бере гору над stCol)

    protected ref array<ref OZL_DutyLine> m_Lines;
    protected ref OZL_DutyLine m_SubLine;

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
        AnchorX = 100;   // графа лежить у комірці з (20, 20)
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
        BtnOff   = ARGB(255, 184, 177, 156);
        Glow     = ARGB( 64, 165,  36,  26);
        SealDone = ARGB(184,  58,  53, 137);
        SealWork = ARGB(184,  58,  53, 137);

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

        m_Lines = new array<ref OZL_DutyLine>();
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

    // Графа за статусом (NodeForm) і колір номера; решту робить база.
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
        TextWidget num = TextWidget.Cast(cell.FindAnyWidget("NodeNum"));
        if (num)
        {
            if (status == "locked")
                num.SetColor(Dim);
            else
                num.SetColor(Txt);
        }
    }

    // ------------------------------------------------------------------
    // Пул, вартість, «Відкриває», кнопка
    // ------------------------------------------------------------------

    // Фонди: назва великими; нуль -- сірий рядок, число ще блідіше
    // (.prow.zero, .prow.zero .pv).
    override void PaintPoolRow(OZL_TreeMenu menu, Widget row, string line, int have, int need, int color)
    {
        super.PaintPoolRow(menu, row, line, have, need, color);
        TextWidget name = TextWidget.Cast(row.FindAnyWidget("PoolName"));
        if (name)
            name.SetText(OZL_Text.Upper(menu.PointName(line)));
        if (have <= 0)
            Tint(row, "PoolValue", Faint);
    }

    // Рядок вартості -- машинописом великими (.crow).
    override void PaintCostRow(OZL_TreeMenu menu, Widget row, string label, string text, int verdict)
    {
        super.PaintCostRow(menu, row, OZL_Text.Upper(label), text, verdict);
    }

    // Чіп «Відкриває»: великими, у рамці; заглушка туману -- блідо і рамка
    // пунктиром (.opens a.fogged). Пробіл у кінці -- поле праворуч від тексту:
    // меню додає до ширини чіпа лише 4 одиниці, а мокап -- 8.
    override void PaintOpenChip(OZL_TreeMenu menu, Widget chip, string text, bool fogged)
    {
        super.PaintOpenChip(menu, chip, OZL_Text.Upper(text) + " ", fogged);
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
        int edge = BtnOff;
        if (enabled)
        {
            text = Acc;
            edge = Acc;
        }
        TextWidget t = TextWidget.Cast(menu.Role("BtnResearchText"));
        if (t)
            t.SetColor(text);
        Widget frame = menu.Role("BtnResearchFrame");
        if (frame)
            frame.SetColor(edge);
    }

    // Печатка: ЗАТВЕРДЖЕНО на дослідженому, В РОБОТІ на тому, що в ділі.
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
    // мови гравця; друкарські вставки; легенда рядком.
    override void OnShow(OZL_TreeMenu menu)
    {
        SetTo(menu, "OrgName", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_ORG_NAME"))));
        SetTo(menu, "OrgUnit", OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_ORG_UNIT")));
        SetTo(menu, "ApproveHead", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_APPROVE"))));
        SetTo(menu, "RegHead", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_REGISTRY_HEAD"))));
        SetTo(menu, "FundHead", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_FUND_HEAD"))));
        SetTo(menu, "DevName", Spread(OZL_Text.Upper(Words("STR_OZL_SKIN_DUTY_SCHEME_HEAD"))));
        SetTo(menu, "CardHeadText", Spread(Words("STR_OZL_SKIN_DUTY_CARD_HEAD")));

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

        // Підпис: CSS згортає подвійний пробіл ключа в один.
        string sign = Words("STR_OZL_SKIN_DUTY_SIGN");
        sign.Replace("  ", " ");
        SetTo(menu, "CardSign", sign);

        // Гриф -- картинка мови гравця; заголовок -- теж, коли рядок
        // STR_OZL_SKIN_DUTY_TITLE_IMG уже є (запит до контролера), інакше
        // живий текст розрядкою.
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

        // Друкарські вставки: пробіл бланка -- 6/28 клітинки вузького шрифту.
        float sp17 = 17 * 6.0 / 28.0;
        float sp14 = 14 * 6.0 / 28.0;
        PutRuns(menu, "OrgRef", SplitLast(Words("STR_OZL_SKIN_DUTY_ORG_REF"), true), sp17);
        PutRuns(menu, "ApproveCmd", SplitFirst(Words("STR_OZL_SKIN_DUTY_APPROVE_CMD"), true), sp17);
        PutRuns(menu, "ApproveDate", SplitBlanks(Words("STR_OZL_SKIN_DUTY_APPROVE_DATE"), true), sp17);
        PutRuns(menu, "Executor", SplitExecutor(Words("STR_OZL_SKIN_DUTY_EXECUTOR")), sp14);

        // Легенда -- рядом за шириною текстів, 14 одиниць між пунктами.
        menu.FlowLater(menu.Role("LegendRow"), 14, 0, false);
    }

    // Після кожного повного малювання: рядок «напрям:» під заголовком (назва
    // гілки й лічильник -- від меню) і нижній край таблиці фондів.
    override void OnPaint(OZL_TreeMenu menu)
    {
        if (m_SubLine)
            m_Lines.RemoveItem(m_SubLine);
        // Один знак машинопису (PT Mono, розмір 18: 16/30 клітинки) між
        // частинами: "напрям: <гілка> · <фракція · досліджено N з M>".
        float ch = 18 * 16.0 / 30.0;
        m_SubLine = new OZL_DutyLine(552, true);
        m_SubLine.Add(TextWidget.Cast(menu.Role("SubDir")), 0);
        m_SubLine.Add(TextWidget.Cast(menu.Role("BranchName")), ch);
        m_SubLine.Add(TextWidget.Cast(menu.Role("SubDot")), ch);
        m_SubLine.Add(TextWidget.Cast(menu.Role("BranchSub")), ch);
        m_Lines.Insert(m_SubLine);

        PoolEdge(menu);
    }

    // Меню щойно перемалювало реєстр і картку (PaintRegistry завжди йде перед
    // PaintCard, а той кличе OnSelect).
    override void OnSelect(OZL_TreeMenu menu, OZL_NodeView node, string status, bool canResearch)
    {
        FixRegistry(menu);
        if (!node)
            return;

        // Статус -- великими, розрядкою (.cstat); колір уже поставило меню.
        SetTo(menu, "CardStatus", Spread(OZL_Text.Upper(StatusText(status))));
        // Кнопка: той самий вибір слова, що в меню, -- великими, розрядкою (.go).
        string key = "STR_OZL_TREE_RESEARCH";
        if (status == "completed")
            key = "STR_OZL_TREE_COMPLETED";
        SetTo(menu, "BtnResearchText", Spread(OZL_Text.Upper(Words(key)), 4));

        ImageWidget seal = ImageWidget.Cast(menu.Role("CardStampImg"));
        if (seal)
        {
            if (status == "researching")
                seal.SetColor(SealWork);
            else
                seal.SetColor(SealDone);
        }

        // Лінійка під «Матеріали» і «Відкриває» -- разом із заголовком, який
        // меню ховає, коли розділ порожній.
        Follow(menu, "CardItemsRule", "CardItemsHead");
        Follow(menu, "CardOpensRule", "CardOpensHead");
        Widget flow = menu.Role("CardFlow");
        if (flow)
            flow.Update();
    }

    override void OnUpdate(OZL_TreeMenu menu, float dt)
    {
        for (int i = m_Lines.Count() - 1; i >= 0; i--)
        {
            if (LayLine(menu, m_Lines[i]))
                m_Lines.RemoveOrdered(i);
        }
    }

    // ------------------------------------------------------------------
    // Реєстр і фонди
    // ------------------------------------------------------------------

    // Рядки реєстру після меню: великі літери стану, сірий рядок закритого
    // вузла (.rrow.st-locked) і прихованого (.fogrow), стан у два рядки, коли
    // не влазить. Далі -- висота таблиці (до 330, далі прокрутка) і фонди на
    // 18 одиниць під нею.
    protected void FixRegistry(OZL_TreeMenu menu)
    {
        Widget list = menu.Role("Registry");
        if (!list)
            return;
        float total = 0;
        Widget row = list.GetChildren();
        while (row)
        {
            total += FixRegRow(menu, row);
            row = row.GetSibling();
        }
        list.Update();

        float shown = total;
        if (shown > REG_MAX)
            shown = REG_MAX;
        Widget scroll = menu.Role("RegScroll");
        if (scroll)
            menu.SizeUnits(scroll, 440, shown);
        Widget fund = menu.Role("FundBlock");
        if (fund)
            menu.PlaceUnits(fund, 40, REG_TOP + shown + FUND_GAP);
    }

    // Один рядок; повертає його висоту.
    protected float FixRegRow(OZL_TreeMenu menu, Widget row)
    {
        string id = TagOf(row, "reg:");
        OZL_NodeView n = null;
        if (id != "")
            n = menu.NodeOf(id);
        int ink = Txt;
        int stateInk = Dim;
        string state = "—";
        if (n)
        {
            if (n.Status == "locked")
                ink = Dim;
            state = OZL_Text.Upper(StatusText(n.Status));
            stateInk = StatusColorOf(n.Status);
        }
        else
        {
            ink = Dim;
            TextWidget fogName = TextWidget.Cast(row.FindAnyWidget("RegName"));
            if (fogName)
                fogName.SetText(OZL_Text.Upper(Words("STR_OZL_TREE_UNKNOWN_ROW")));
        }
        Tint(row, "RegNum", ink);
        Tint(row, "RegName", ink);
        Tint(row, "RegTier", ink);

        string first = state;
        string second = "";
        if (state.LengthUtf8() > STATE_CHARS)
            SplitState(state, first, second);
        TextWidget st = TextWidget.Cast(row.FindAnyWidget("RegState"));
        if (st)
        {
            st.SetText(first);
            st.SetColor(stateInk);
        }
        TextWidget st2 = TextWidget.Cast(row.FindAnyWidget("RegState2"));
        if (st2)
        {
            st2.SetText(second);
            st2.SetColor(stateInk);
            st2.Show(second != "");
        }
        float h = ROW_H;
        if (second != "")
            h = ROW_H2;
        // Ширина рядка пропорційна (1 = уся таблиця), висота -- пікселі
        // екрана (SetSize бере пікселі, SKINS.md "Units").
        row.SetSize(1, h * menu.Px());
        return h;
    }

    // Id рядка списку: меню перейменовує його ...Hit (або сам рядок) на
    // <tag><id> -- reg:; рядок прихованого вузла лишається без
    // імені -- "".
    protected static string TagOf(Widget row, string tag)
    {
        int n = tag.Length();
        string own = row.GetName();
        if (own.IndexOf(tag) == 0)
            return own.Substring(n, own.Length() - n);
        Widget c = row.GetChildren();
        while (c)
        {
            string nm = c.GetName();
            if (nm.IndexOf(tag) == 0)
                return nm.Substring(n, nm.Length() - n);
            c = c.GetSibling();
        }
        return "";
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

    // Нижній край таблиці фондів -- 1.5, як боки, поверх межі останнього
    // рядка; порожній пул -- лише рамка з написом (PoolEmpty, показує меню).
    protected void PoolEdge(OZL_TreeMenu menu)
    {
        Widget pool = menu.Role("PoolList");
        Widget edge = menu.Role("PoolBottom");
        if (!pool || !edge)
            return;
        int rows = 0;
        Widget c = pool.GetChildren();
        while (c)
        {
            rows++;
            c = c.GetSibling();
        }
        edge.Show(rows > 0);
        if (rows > 0)
            menu.PlaceUnits(edge, 0, 25.5 + POOL_ROW_H * rows - 1);
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
    // слова до останнього підкреслення -- друкарське (звання і графа).
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
        runs.Insert(new OZL_DutyRun(rest.Substring(0, blank + 1), true, true));
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

    // Шматки -- у написи контейнера: бланкові в <Line>N0, N1..., друкарські в
    // <Line>T0, T1...; зайві ховаються; ставить OnUpdate.
    protected void PutRuns(OZL_TreeMenu menu, string line, array<ref OZL_DutyRun> runs, float space)
    {
        Widget box = menu.Role(line);
        if (!box)
            return;
        OZL_DutyLine job = new OZL_DutyLine(0, false);
        int nextN = 0;
        int nextT = 0;
        for (int i = 0; i < runs.Count(); i++)
        {
            OZL_DutyRun run = runs[i];
            string slotName = line + "N" + nextN.ToString();
            if (run.Typed)
                slotName = line + "T" + nextT.ToString();
            TextWidget t = TextWidget.Cast(box.FindAnyWidget(slotName));
            if (!t)
                continue;
            if (run.Typed)
                nextT++;
            else
                nextN++;
            t.SetText(run.Text);
            t.Show(true);
            float gap = 0;
            if (run.Space && job.Parts.Count() > 0)
                gap = space;
            job.Add(t, gap);
        }
        HideFrom(box, line + "N", nextN);
        HideFrom(box, line + "T", nextT);
        m_Lines.Insert(job);
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

    // Поставити рядок, коли всі його видимі написи мають ширину тексту;
    // true -- поставлено (чи чекати вже годі).
    protected bool LayLine(OZL_TreeMenu menu, OZL_DutyLine line)
    {
        float px = menu.Px();
        if (px <= 0)
            return false;
        array<float> widths = new array<float>();
        float total = 0;
        int i;
        for (i = 0; i < line.Parts.Count(); i++)
        {
            TextWidget t = line.Parts[i];
            float w = 0;
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
                w = pw / px;
                total += line.Gaps[i] + w;
            }
            widths.Insert(w);
        }
        float x = line.X;
        if (line.Center)
            x = line.X - total / 2;
        for (i = 0; i < line.Parts.Count(); i++)
        {
            TextWidget p = line.Parts[i];
            if (!p || !p.IsVisible())
                continue;
            x += line.Gaps[i];
            menu.PlaceUnits(p, x, 0);
            x += widths[i];
        }
        return true;
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
