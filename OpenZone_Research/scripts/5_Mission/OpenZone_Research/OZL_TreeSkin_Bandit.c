// Вікно bandit -- «Записи братви»: той самий зошит розворотом, що в neutral,
// але м'ятий, вигнутий і рваний. Ліва сторінка в лінійку: заголовок із
// закресленим словом, общак паличками, запис про вузол, що трохи «гуляє» по
// відступах; права в клітинку: дерево росте вниз клаптиками паперу, повернутими
// вразнобій, зв'язки від руки. Доступний обведено синьою ручкою, вибраний --
// червоним пунктиром, досліджений -- зелена галка, у ділі -- «в ділі»,
// закритий -- блідіший клапоть і «?». На полях -- клякси, череп, ніж, стрілка,
// «!!!», спіраль, зірка; кут сторінки прихоплено скотчем.
//
// Сторінки (м'ятість, вигин лінійки й клітинки, рвані краї, корінець на
// скріпках) -- одна запечена картинка під живими віджетами; клітинка тому
// не малюється на канві (GridStep 0) і не прокручується з деревом.
//
// ЛІНІЙНЕ СВІТЛО. Гра змішує інтерфейс у лінійному світлі, мокап -- в sRGB,
// тож напівпрозоре в грі блідіше. Прозорості тут і в картинках підняті до
// тих, що в грі дають кольори мокапа (у дужках -- мокапові).
//
// Розкладки: ozl_tree_bandit, ozl_node_bandit (ui/OpenZone_Research/);
// картинки: source/ui/bandit/ (набір ozl_bandit, текстури tree/bandit);
// кольори й шрифти: ui/tokens/bandit.json. Числа нижче -- ті самі токени в ARGB.

#ifndef NO_GUI

class OZL_TreeSkin_Bandit : OZL_TreeSkin
{
    static const string SET = "set:ozl_bandit image:";

    int Edge;
    int DimSoft;   // тьмяне з прозорістю .8 (.7): назва й ціна закритого вузла
    int Faint;     // --faint: нуль у пулі, "??? невідомо" серед "Відкриває"

    void OZL_TreeSkin_Bandit()
    {
        Named("bandit");
        Dir     = "down";
        NodeW   = 176;
        NodeH   = 64;
        Row     = 140;
        Col     = 210;
        Top     = 100;
        Side    = 40;
        AnchorX = 108;   // клапоть лежить у комірці з (20, 20)
        AnchorY = 52;

        Txt      = ARGB(255,  42,  32,  24);
        Dim      = ARGB(255, 111,  92,  66);
        Acc      = ARGB(255,  31,  63, 134);
        Ok       = ARGB(255,  47, 106,  42);
        Bad      = ARGB(255, 176,  42,  26);
        LineDim  = ARGB(184, 111,  92,  66);   // (.6)
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255, 214, 199, 160);
        // Туман -- м'ятий папір кольору --fog, запечений у самих картинках
        // TreeFog і TreeFogEdge, тож меню фарбує їх білим (не змінює).
        FogColor = ARGB(255, 255, 255, 255);
        Edge     = ARGB(255, 160, 138,  98);
        DimSoft  = ARGB(204, 111,  92,  66);   // (.7)
        Faint    = ARGB(255, 139, 121,  93);

        // Зв'язки від руки (sketch() мокапа), пунктир "будь-якого" -- 7/6.
        LineStyle = "sketch";
        DashOn    = 7;
        DashOff   = 6;

        // Клітинка -- у картинці сторінки, вигнута разом із папером.
        GridStep = 0;

        // П'ять повернутих клаптиків (правила nth-child мокапа); котрий --
        // каже ShapeOfNode. Тіні в них нема і під мишею вони не міняються:
        // мокапова box-shadow клаптя зрізана його ж clip-path. Закритий --
        // той самий клапоть, блідіший: color-mix(paper-hi 70 %, lcd).
        for (int s = 0; s < 5; s++)
            Shapes.Insert(SET + "scrap_" + s.ToString());
        ShapeHover = -1;
        ShapeColors.Set("locked", ARGB(255, 249, 248, 244));
        Marks.Insert(SET + "tick");   // 0 -- зелена галка

        SegOn  = Bad;
        SegOff = Edge;
        TipPadX = 9;
    }

    override int MarkOf(string status)
    {
        if (status == "completed")
            return 0;
        return -1;
    }

    override string MarkTextOf(string status)
    {
        if (status == "researching")
            return OZL_Text.Words("STR_OZL_TREE_MARK_WORK");
        return "";
    }

    override int MarkColorOf(string status)
    {
        if (status == "completed")
            return Ok;
        if (status == "researching")
            return Bad;
        return Dim;
    }

    override int NameColorOf(string status)
    {
        if (status == "completed")
            return Ok;
        if (status == "locked")
            return DimSoft;
        return Txt;
    }

    override int PriceColorOf(string status)
    {
        if (status == "short" || status == "researching")
            return Bad;
        if (status == "available")
            return Acc;
        if (status == "locked")
            return DimSoft;
        return Dim;
    }

    // Розділи картки -- з двокрапкою (.sec::after мокапа).
    override string SectionText(string key)
    {
        return OZL_Text.Words(key) + OZL_Text.Words("STR_OZL_SKIN_BANDIT_SEC_MARK");
    }

    // ------------------------------------------------------------------
    // Вузол
    // ------------------------------------------------------------------

    // Повернутий клапоть вузла -- за його id, тож клапоть не повертається
    // інакше, коли туман відступає (Index тепер зсувається разом із ним).
    override int ShapeOfNode(OZL_NodeView node, string status, bool selected)
    {
        if (!node)
            return ShapeOf(status, selected);
        return Turn(node.Id);
    }

    // Правила nth-child мокапа для k = 1..60 з хешу id: 5n (4.5°), 4n (-1° і 4
    // ліворуч), 3n (2.8° і 3 вниз), непарний (-3.5°), решта рівно. Перше
    // правило, що збіглося, -- останнє в CSS, тобто те, що там і перемагає.
    static int Turn(string id)
    {
        int k = (id.Hash() & 0x7FFFFFFF) % 60 + 1;
        if (k % 5 == 0)
            return 4;
        if (k % 4 == 0)
            return 3;
        if (k % 3 == 0)
            return 2;
        if (k % 2 == 1)
            return 0;
        return 1;
    }

    // Знак питання закритого вузла -- менший і нижчий за інші мітки, тож має
    // власний віджет (NodeMarkQuery). Слово мітки («в ділі») у мокапі стоїть
    // у .mark без ширини, тож переноситься на кожному пробілі: перше слово --
    // у NodeMarkText, решта -- рядком нижче, у NodeMarkText2. Різати рядок
    // можна лише на пробілі: Substring рахує байти, пробіл -- один байт.
    override void PaintNode(OZL_TreeMenu menu, Widget cell, OZL_NodeView node, string status, bool selected)
    {
        super.PaintNode(menu, cell, node, status, selected);
        Widget query = cell.FindAnyWidget("NodeMarkQuery");
        if (query)
            query.Show(status == "locked");
        TextWidget first = TextWidget.Cast(cell.FindAnyWidget("NodeMarkText"));
        TextWidget second = TextWidget.Cast(cell.FindAnyWidget("NodeMarkText2"));
        if (!first || !second)
            return;
        string mark = MarkTextOf(status);
        int cut = mark.IndexOf(" ");
        if (cut <= 0)
        {
            second.Show(false);
            return;
        }
        first.SetText(mark.Substring(0, cut));
        second.SetText(mark.Substring(cut + 1, mark.Length() - cut - 1));
        second.SetColor(MarkColorOf(status));
        second.Show(true);
    }

    // Зв'язок від руки (sketch() мокапа): штрих 0.85 ширини, а поверх тонкий
    // 0.45 з прозорістю .45 -- у лінійному світлі гри це 166 для повного
    // кольору і 94 для тьмяного (мокапові .6 x .45). Не "sketch" -- як у базі.
    override void DrawStroke(CanvasWidget canvas, array<float> xs, array<float> ys, float width, int color, bool dashed, string seed)
    {
        if (LineStyle != "sketch")
        {
            super.DrawStroke(canvas, xs, ys, width, color, dashed, seed);
            return;
        }
        Sketch(canvas, xs, ys, width * 0.85, color, seed, dashed);
        int alpha = 166;
        if (color == LineDim)
            alpha = 94;
        int faint = (alpha << 24) | (color & 0x00FFFFFF);
        Sketch(canvas, xs, ys, width * 0.45, faint, seed + "~", false);
    }

    // ------------------------------------------------------------------
    // Общак паличками (tally() мокапа)
    // ------------------------------------------------------------------

    // Рядок пулу: назва, палички, число. Нуль закреслено й бліде, понад 60 --
    // лише число, велике й двічі підкреслене. Рядки «гуляють» по відступах, як
    // у мокапа: кожен парний -- на 7 праворуч, кожен третій -- на 2 праворуч і
    // на 2 нижче (і все, що під ним, теж). Зсуваються лише рамки, що стоять у
    // (0, 0): PoolLine униз, PoolShift (назва, її риска, палички) убік -- число
    // праворуч лишається на місці, як від padding-left мокапа.
    override void PaintPoolRow(OZL_TreeMenu menu, Widget row, int index, string line, int have, int color)
    {
        // Чужий файл замість рядка (SKINS.md, "Layout mix-up"): меню вже
        // пробувало вдруге й попередило в лозі; такий рядок не показуємо.
        if (!row.FindAnyWidget("PoolLine"))
        {
            row.Show(false);
            return;
        }
        super.PaintPoolRow(menu, row, index, line, have, color);
        // Велике число підкреслене під рядком, а рядки зсунуті донизу: рамки
        // рядка не обрізають того, що виходить за його 32 одиниці.
        row.ClearFlags(WidgetFlags.CLIPCHILDREN);
        Widget lineBox = row.FindAnyWidget("PoolLine");
        Widget shift = row.FindAnyWidget("PoolShift");
        Unclip(lineBox);
        Unclip(shift);
        Unclip(row.FindAnyWidget("PoolTally"));

        int k = index + 1;
        float dx = 0;
        if (k % 3 == 0)
            dx = 2;
        else if (k % 2 == 0)
            dx = 7;
        int down = 2 * (k / 3);
        menu.PlaceUnits(lineBox, 0, down);
        menu.PlaceUnits(shift, dx, 0);

        bool zero = have <= 0;
        bool many = have > 60;
        TextWidget value = TextWidget.Cast(row.FindAnyWidget("PoolValue"));
        TextWidget big = TextWidget.Cast(row.FindAnyWidget("PoolValueBig"));
        if (value)
        {
            value.Show(!many);
            if (zero)
                value.SetColor(Faint);
        }
        if (big)
        {
            big.Show(many);
            if (many)
            {
                big.SetText(have.ToString());
                big.SetColor(Txt);
            }
        }

        // Нуль закреслено -- окремо назву і число, як text-decoration мокапа;
        // довжину рисок міряє меню, коли текст уже розкладено.
        Widget nameStrike = row.FindAnyWidget("PoolNameStrike");
        if (nameStrike)
        {
            nameStrike.Show(zero);
            if (zero)
                menu.FitLater(TextWidget.Cast(row.FindAnyWidget("PoolName")), nameStrike, 0, 0);
        }
        Widget valueStrike = row.FindAnyWidget("PoolValueStrike");
        if (valueStrike)
        {
            valueStrike.Show(zero);
            if (zero)
                menu.FitLater(value, valueStrike, 0, 1);
        }
        for (int u = 1; u <= 2; u++)
        {
            Widget under = row.FindAnyWidget("PoolValueLine" + u.ToString());
            if (!under)
                continue;
            under.Show(many);
            if (many)
                menu.FitLater(big, under, 0, 1);
        }

        Tally(menu, row, have);
    }

    protected static void Unclip(Widget w)
    {
        if (w)
            w.ClearFlags(WidgetFlags.CLIPCHILDREN);
    }

    // Десятки -- перехрещені квадрати, п'ятірка -- чотири палички навскіс
    // перекреслені, решта -- палички; між знаками 10 одиниць (рядок flex мокапа:
    // квадрат 20 і по 2 поля з боків, палички Caveat 26 по 6.6).
    protected void Tally(OZL_TreeMenu menu, Widget row, int have)
    {
        int tens = 0;
        int fives = 0;
        int rest = 0;
        if (have > 0 && have <= 60)
        {
            tens = have / 10;
            fives = (have % 10) / 5;
            rest = have % 5;
        }
        float x = 0;
        int slot = 0;
        for (int t = 0; t < tens; t++)
        {
            Mark(menu, row, slot, "tally_ten", x + 2, 6, 20, 20, 2);
            x += 34;
            slot++;
        }
        if (fives > 0)
        {
            Mark(menu, row, slot, "tally_five", x, -0.5, 26.4, 33, 8);
            x += 36.4;
            slot++;
        }
        if (rest > 0)
        {
            Mark(menu, row, slot, "tally_" + rest.ToString(), x, -0.5, 6.6 * rest, 33, 8);
            slot++;
        }
        // Решту знаків рядка (скільки їх у розкладці) сховати.
        Widget spare = row.FindAnyWidget("TallyMark" + slot.ToString());
        while (spare)
        {
            spare.Show(false);
            slot++;
            spare = row.FindAnyWidget("TallyMark" + slot.ToString());
        }
    }

    // Знак: картинка з полем `pad` навколо рамки (x, y, w, h) мокапа.
    protected void Mark(OZL_TreeMenu menu, Widget row, int slot, string image, float x, float y, float w, float h, float pad)
    {
        ImageWidget m = ImageWidget.Cast(row.FindAnyWidget("TallyMark" + slot.ToString()));
        if (!m)
            return;
        if (m.LoadImageFile(0, SET + image))
            m.SetImage(0);
        m.SetColor(Txt);
        menu.PlaceUnits(m, x - pad, y - pad);
        menu.SizeUnits(m, w + 2 * pad, h + 2 * pad);
        m.Show(true);
    }

    // ------------------------------------------------------------------
    // Картка
    // ------------------------------------------------------------------

    // Чого не вистачає -- підкреслено (.crow.bad .cv мокапа).
    override void PaintCostRow(OZL_TreeMenu menu, Widget row, string label, string text, int verdict)
    {
        super.PaintCostRow(menu, row, label, text, verdict);
        Widget line = row.FindAnyWidget("CostValueLine");
        if (line)
        {
            line.Show(verdict < 0);
            if (verdict < 0)
                menu.FitLater(TextWidget.Cast(row.FindAnyWidget("CostValue")), line, 0, 1);
        }
    }

    // Заглушка туману серед "Відкриває" -- блідим (--faint) і без пунктиру:
    // мокап для паперу пише .opens a.fogged { border: none }.
    override void PaintOpenChip(OZL_TreeMenu menu, Widget chip, string text, bool fogged)
    {
        super.PaintOpenChip(menu, chip, text, fogged);
        if (fogged)
        {
            TextWidget t = TextWidget.Cast(chip.FindAnyWidget("ChipText"));
            if (t)
                t.SetColor(Faint);
        }
        Widget line = chip.FindAnyWidget("ChipLine");
        if (line)
            line.Show(!fogged);
    }

    // Обведена ручкою кнопка; неактивна -- без обведення, тьмяна й закреслена.
    override void PaintButton(OZL_TreeMenu menu, Widget btn, bool enabled)
    {
        super.PaintButton(menu, btn, enabled);
        Widget ring = menu.Role("BtnResearchRing");
        if (ring)
            ring.Show(enabled);
        Widget strike = menu.Role("BtnResearchStrike");
        if (strike)
        {
            strike.Show(!enabled);
            if (!enabled)
                menu.FitLater(TextWidget.Cast(menu.Role("BtnResearchText")), strike, 0, 2);
        }
    }

    // Хвилясті риски під назвою і під заголовками розділів -- завдовжки з
    // текст (рамка, що їх обрізає, стає шириною тексту); тримачі заголовків
    // "Матеріали" й "Відкриває" -- видимі разом із ними.
    override void OnSelect(OZL_TreeMenu menu, OZL_NodeView node, string status, bool canResearch)
    {
        if (!node)
            return;
        Fit(menu, "CardName", "CardNameWave");
        Fit(menu, "CardCostHead", "CardCostHeadWave");
        Fit(menu, "CardItemsHead", "CardItemsHeadWave");
        Fit(menu, "CardTimeHead", "CardTimeHeadWave");
        Fit(menu, "CardOpensHead", "CardOpensHeadWave");
        Follow(menu, "CardItemsHeadRow", "CardItemsHead");
        Follow(menu, "CardOpensHeadRow", "CardOpensHead");
        menu.RefreshCard();
    }

    // Опис щойно перенесено по рядках: тримачі рядків (CardDescRow0, 1, ... --
    // стос не зсуває дитину вбік, тож рядки на 9 одиниць углиб сидять у
    // тримачах) видимі разом зі своїми рядками, а тоді стос і прокрутка.
    override void OnWrapped(OZL_TreeMenu menu, Widget box)
    {
        Widget desc = menu.Role("CardDesc");
        if (!box || box != desc)
            return;
        int i = 0;
        Widget holder = menu.Role("CardDescRow0");
        Widget text = menu.Role("CardDesc0");
        while (holder && text)
        {
            holder.Show(text.IsVisible());
            i++;
            holder = menu.Role("CardDescRow" + i.ToString());
            text = menu.Role("CardDesc" + i.ToString());
        }
        desc.Update();
        menu.RefreshCard();
    }

    protected static void Fit(OZL_TreeMenu menu, string text, string target)
    {
        menu.FitLater(TextWidget.Cast(menu.Role(text)), menu.Role(target), 0, 0);
    }

    // `what` видно тоді й лише тоді, коли видно `leader`.
    protected static void Follow(OZL_TreeMenu menu, string what, string leader)
    {
        Widget w = menu.Role(what);
        Widget h = menu.Role(leader);
        if (w && h)
            w.Show(h.IsVisible());
    }

    // ------------------------------------------------------------------
    // Події вікна
    // ------------------------------------------------------------------

    // Заголовок і «Общак» -- картинки мови гравця (рядки *_IMG); не
    // завантажились -- живий текст (заголовок тоді без закресленого слова).
    // Легенда -- рядом за шириною текстів: її написи ширші за текст, бо
    // напис, що сам міряє себе по тексту, зрізає верхівку похилої останньої
    // літери. Проміжок 13, не мокапові 14: Caveat гри на 20 довший за
    // Chrome на ~1 одиницю на пункт, і шість пунктів упиралися в рваний край
    // (стенд 2026-10-31); так кожен пункт починається в межах 2 від мокапа.
    // Хвиля під заголовком розділу виходить нижче за його 30-одиничного
    // тримача (стенд 2026-10-31: тримач-панель її зрізав до верхніх дужок).
    override void OnShow(OZL_TreeMenu menu)
    {
        Unclip(menu.Role("CardCostHeadRow"));
        Unclip(menu.Role("CardItemsHeadRow"));
        Unclip(menu.Role("CardTimeHeadRow"));
        Unclip(menu.Role("CardOpensHeadRow"));
        bool title = Picture(menu, "TitleImg", OZL_Text.Words("STR_OZL_SKIN_BANDIT_TITLE_IMG"));
        Shown(menu, "TitleImg", title);
        TextWidget titleText = TextWidget.Cast(menu.Role("TitleText"));
        if (titleText)
        {
            titleText.SetText(OZL_Text.Words("STR_OZL_SKIN_BANDIT_TITLE_PRE") + " " + OZL_Text.Words("STR_OZL_SKIN_BANDIT_TITLE_POST"));
            titleText.Show(!title);
        }
        bool head = Picture(menu, "PoolHeadImg", OZL_Text.Words("STR_OZL_SKIN_BANDIT_POOL_IMG"));
        Shown(menu, "PoolHeadImg", head);
        Shown(menu, "PoolHeadText", !head);
        menu.FlowLater(menu.Role("LegendRow"), 13, 0, false);
    }

    // Список гілок -- лише коли їх більше однієї. Прокрутка пулу -- сира
    // ScrollWidget, а меню оновлює лише стос PoolList: прокрутка сама не
    // бачить, що рядків стало більше (скіл gui-layouts §31), тож оновити її тут.
    override void OnPaint(OZL_TreeMenu menu)
    {
        Widget branches = menu.Role("BranchScroll");
        if (branches)
            branches.Show(menu.BranchCount() > 1);
        Widget pool = menu.Role("PoolScroll");
        if (pool)
            pool.Update();
    }

    // ------------------------------------------------------------------
    // Дрібниці
    // ------------------------------------------------------------------

    // Картинка мови гравця в ImageWidget (рядок *_IMG stringtable).
    protected static bool Picture(OZL_TreeMenu menu, string role, string image)
    {
        ImageWidget w = ImageWidget.Cast(menu.Role(role));
        if (!w || image.IndexOf("set:") != 0)
            return false;
        if (!w.LoadImageFile(0, image))
            return false;
        w.SetImage(0);
        return true;
    }

    protected static void Shown(OZL_TreeMenu menu, string role, bool on)
    {
        Widget w = menu.Role(role);
        if (w)
            w.Show(on);
    }
}

#endif
