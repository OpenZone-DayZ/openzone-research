// Вікно neutral -- «Записник сталкера» (у мокапі -- loner): тетрадь
// розворотом на дерев'яному столі. Ліва сторінка в лінійку: заголовок, бали
// числами, запис про вузол; права в клітинку: дерево росте вниз. Вузли --
// рівні картки 176x64, доступний обведено синьою ручкою, вибраний -- червоним
// пунктиром, досліджений -- зелена галка, у ділі -- «в ділі» червоним,
// закритий -- блідіша картка і «?». Зв'язки прямі.
//
// Це й запасне вікно: на нього падає фракція, чиє вікно ще не намальоване,
// тож тут є список гілок (у мокапі його нема -- в одинаків одна гілка), який
// з'являється, коли гілок більше однієї.
//
// Розкладки: ozl_tree_neutral, ozl_node_neutral (ui/OpenZone_Research/);
// картинки: source/ui/neutral/ (набір ozl_neutral); кольори й шрифти:
// ui/tokens/neutral.json. Числа нижче -- ті самі токени в ARGB.

#ifndef NO_GUI

class OZL_TreeSkin_Neutral : OZL_TreeSkin
{
    static const string SET = "set:ozl_neutral image:";

    int CardColor;
    int CardLocked;
    int Edge;
    int DimSoft;   // тьмяне з прозорістю .7: назва й ціна закритого вузла
    int Faint;     // --faint: "??? невідомо" серед "Відкриває"

    void OZL_TreeSkin_Neutral()
    {
        Named("neutral");
        Dir     = "down";
        NodeW   = 176;
        NodeH   = 64;
        Row     = 140;
        Col     = 210;
        Top     = 100;
        Side    = 40;
        AnchorX = 108;   // картка лежить у комірці з (20, 20)
        AnchorY = 52;

        Txt      = ARGB(255,  42,  32,  24);
        Dim      = ARGB(255, 111,  92,  66);
        Acc      = ARGB(255,  31,  63, 134);
        Ok       = ARGB(255,  47, 106,  42);
        Bad      = ARGB(255, 176,  42,  26);
        LineDim  = ARGB(153, 111,  92,  66);
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255, 228, 219, 192);
        FogColor = ARGB(255, 221, 210, 178);
        Edge       = ARGB(255, 160, 138,  98);
        CardColor  = ARGB(255, 246, 241, 226);
        CardLocked = ARGB(255, 241, 234, 216);
        DimSoft    = ARGB(179, 111,  92,  66);
        Faint      = ARGB(255, 142, 126, 100);

        // Клітинка 20 одиниць, лінії від (6, 6), синя (.content .bg мокапа).
        GridStep  = 20;
        GridColor = ARGB(71, 38, 92, 196);
        GridX     = 6;
        GridY     = 6;

        Shapes.Insert(SET + "card");        // 0 -- звичайна картка
        Shapes.Insert(SET + "card_hover");  // 1 -- під мишею, тінь глибша
        Shapes.Insert(SET + "card_flat");   // 2 -- закрита, без тіні
        ShapeHover = 1;
        Marks.Insert(SET + "tick");         // 0 -- зелена галка
        ShapeColors.Set("locked", CardLocked);
        ShapeColors.Set("short", CardColor);
        ShapeColors.Set("available", CardColor);
        ShapeColors.Set("researching", CardColor);
        ShapeColors.Set("completed", CardColor);

        SegOn  = Bad;
        SegOff = Edge;
        TipPadX = 9;
    }

    override int ShapeOf(string status, bool selected)
    {
        if (status == "locked")
            return 2;
        return 0;
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
        return OZL_Text.Words(key) + OZL_Text.Words("STR_OZL_SKIN_NEUTRAL_SEC_MARK");
    }

    // Знак питання закритого вузла -- менший і нижчий за інші мітки, тож має
    // власний віджет (NodeMarkQuery); у ділі -- NodeMarkText.
    override void PaintNode(OZL_TreeMenu menu, Widget cell, OZL_NodeView node, string status, bool selected)
    {
        super.PaintNode(menu, cell, node, status, selected);
        Widget query = cell.FindAnyWidget("NodeMarkQuery");
        if (query)
            query.Show(status == "locked");
    }

    // Нуль у пулі закреслено -- окремо назву і число, як text-decoration
    // мокапа; довжину рисок міряє меню, коли текст уже розкладено.
    override void PaintPoolRow(OZL_TreeMenu menu, Widget row, string line, int have, int need, int color)
    {
        super.PaintPoolRow(menu, row, line, have, need, color);
        Widget nameStrike = row.FindAnyWidget("PoolNameStrike");
        Widget valueStrike = row.FindAnyWidget("PoolValueStrike");
        bool zero = have <= 0;
        if (nameStrike)
        {
            nameStrike.Show(zero);
            if (zero)
                menu.FitLater(TextWidget.Cast(row.FindAnyWidget("PoolName")), nameStrike, 0, 0);
        }
        if (valueStrike)
        {
            valueStrike.Show(zero);
            if (zero)
                menu.FitLater(TextWidget.Cast(row.FindAnyWidget("PoolValue")), valueStrike, 0, 1);
        }
    }

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

    // Список гілок -- лише коли їх більше однієї; хвиляста риска -- під
    // назвою вибраного вузла, завдовжки з назву.
    override void OnPaint(OZL_TreeMenu menu)
    {
        Widget branches = menu.Role("BranchScroll");
        if (branches)
            branches.Show(menu.BranchCount() > 1);
    }

    override void OnSelect(OZL_TreeMenu menu, OZL_NodeView node, string status, bool canResearch)
    {
        Widget wave = menu.Role("CardNameWave");
        if (wave && node)
            menu.FitLater(TextWidget.Cast(menu.Role("CardName")), wave, 0, 0);
    }

    // Риска під «Бали» -- завдовжки з напис, якою б мовою він не був.
    // Легенда -- рядом за шириною текстів: її написи ширші за текст, бо
    // напис, що сам міряє себе по тексту, зрізає верхівку похилої останньої
    // літери (англійське "locked" ставало "lockea").
    override void OnShow(OZL_TreeMenu menu)
    {
        Widget line = menu.Role("PoolHeadLine");
        if (line)
            menu.FitLater(TextWidget.Cast(menu.Role("PoolHead")), line, 0, 0);
        menu.FlowLater(menu.Role("LegendRow"), 14, 0, false);
    }
}

#endif
