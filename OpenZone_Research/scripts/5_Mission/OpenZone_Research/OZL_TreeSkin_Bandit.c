// Вікно bandit -- «Записи братви»: та сама тетрадь, що в neutral, але м'ята й рвана; бали паличками, зв'язки від руки.
//
// ПОКИ ЩО ЛИШЕ ДАНІ: геометрія (спека §3, мокап SKINS.bandit), палітра (CSS
// мокапа спільного паперового блоку і body[data-f="bandit"]; ті самі кольори -- у ui/tokens/bandit.json), мітки (спека §3) і
// назви розкладок. Решту успадковано від OZL_TreeSkin. Поки розкладки
// ozl_tree_bandit нема, меню показує це вікно тетрадю neutral (один рядок у
// лозі). Свої частини і гачки допише задача цього вікна -- у цьому ж файлі
// (source/ui/SKINS.md).

#ifndef NO_GUI

class OZL_TreeSkin_Bandit : OZL_TreeSkin
{
    static const string COMMON = "set:ozl_common image:";

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
        // Центр форми в комірці -- поки комірка не намальована, форма в її куті.
        AnchorX = 88;
        AnchorY = 32;

        Txt      = ARGB(255, 42, 32, 24);
        Dim      = ARGB(255, 111, 92, 66);
        Acc      = ARGB(255, 31, 63, 134);
        Ok       = ARGB(255, 47, 106, 42);
        Bad      = ARGB(255, 176, 42, 26);
        LineDim  = ARGB(153, 111, 92, 66);
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255, 214, 199, 160);
        FogColor = ARGB(255, 201, 184, 143);

        // Зв'язки від руки (sketch() мокапа).
        LineStyle = "sketch";

        // Сітка тла (.content .bg мокапа: --grid, --grid-step).
        GridStep  = 20;
        GridColor = ARGB(115, 38, 92, 196);
        GridX     = 6;
        GridY     = 6;
        GridW     = 1.5;

        // Мітки паперу: галка; «?» закритого й «в ділі» -- текстом (спека §3).
        Marks.Insert(COMMON + "mark_check");

    }

    override int MarkOf(string status)
    {
        if (status == "completed")
            return 0;
        return -1;
    }

    override string MarkTextOf(string status)
    {
        if (status == "locked")
            return "?";
        if (status == "researching")
            return OZL_Text.Words("STR_OZL_TREE_MARK_WORK");
        return "";
    }
}

#endif
