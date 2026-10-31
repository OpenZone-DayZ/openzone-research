// Вікно freedom -- «ВОЛЯ.narod»: саморобний сайт, кнопки Windows 98, бігучий рядок, помічник-листик.
//
// ПОКИ ЩО ЛИШЕ ДАНІ: геометрія (спека §3, мокап SKINS.freedom), палітра (CSS
// мокапа body[data-f="freedom"]; ті самі кольори -- у ui/tokens/freedom.json), мітки (спека §3) і
// назви розкладок. Решту успадковано від OZL_TreeSkin. Поки розкладки
// ozl_tree_freedom нема, меню показує це вікно тетрадю neutral (один рядок у
// лозі). Свої частини і гачки допише задача цього вікна -- у цьому ж файлі
// (source/ui/SKINS.md).

#ifndef NO_GUI

class OZL_TreeSkin_Freedom : OZL_TreeSkin
{
    static const string COMMON = "set:ozl_common image:";

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
        // Центр форми в комірці -- поки комірка не намальована, форма в її куті.
        AnchorX = 90;
        AnchorY = 32;

        Txt      = ARGB(255, 204, 255, 102);
        Dim      = ARGB(255, 143, 174, 90);
        Acc      = ARGB(255, 255, 255, 0);
        Ok       = ARGB(255, 51, 255, 102);
        Bad      = ARGB(255, 255, 79, 160);
        LineDim  = ARGB(255, 79, 122, 53);
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255, 3, 8, 2);
        FogColor = ARGB(255, 3, 8, 2);

        // Мітки: замок / галка / пісочний годинник і слово «NEW!» доступного (спека §3).
        Marks.Insert(COMMON + "mark_lock");
        Marks.Insert(COMMON + "mark_check");
        Marks.Insert(COMMON + "mark_wait");

    }

    override string MarkTextOf(string status)
    {
        if (status == "available")
            return OZL_Text.Words("STR_OZL_TREE_MARK_NEW");
        return "";
    }
}

#endif
