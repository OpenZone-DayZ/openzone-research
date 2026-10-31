// Вікно clearsky -- «Польовий КПК»: карта з ізолініями на все вікно, круглі мітки, плаваючі панелі.
//
// ПОКИ ЩО ЛИШЕ ДАНІ: геометрія (спека §3, мокап SKINS.clearsky), палітра (CSS
// мокапа body[data-f="clearsky"]; ті самі кольори -- у ui/tokens/clearsky.json), мітки (спека §3) і
// назви розкладок. Решту успадковано від OZL_TreeSkin. Поки розкладки
// ozl_tree_clearsky нема, меню показує це вікно зошитом neutral (один рядок у
// лозі). Свої частини і гачки допише задача цього вікна -- у цьому ж файлі
// (source/ui/SKINS.md).

#ifndef NO_GUI

class OZL_TreeSkin_Clearsky : OZL_TreeSkin
{
    static const string COMMON = "set:ozl_common image:";

    void OZL_TreeSkin_Clearsky()
    {
        Named("clearsky");
        Dir     = "down";
        NodeW   = 50;
        NodeH   = 50;
        Row     = 140;
        Col     = 230;
        Top     = 190;
        Side    = 80;
        Shift   = -170;
        // Центр форми в комірці -- поки комірка не намальована, форма в її куті.
        AnchorX = 25;
        AnchorY = 25;

        Txt      = ARGB(255, 195, 223, 240);
        Dim      = ARGB(255, 95, 138, 166);
        Acc      = ARGB(255, 111, 193, 255);
        Ok       = ARGB(255, 138, 215, 192);
        Bad      = ARGB(255, 255, 138, 92);
        LineDim  = ARGB(153, 95, 138, 166);
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255, 10, 24, 38);
        FogColor = ARGB(255, 9, 22, 35);

        // Сітка тла (.content .bg мокапа: --grid, --grid-step).
        GridStep  = 64;
        GridColor = ARGB(13, 110, 180, 240);

        // Мітки: замок / галка / крапка (спека §3) -- спільні фігури ozl_common.
        Marks.Insert(COMMON + "mark_lock");
        Marks.Insert(COMMON + "mark_check");
        Marks.Insert(COMMON + "mark_dot");

    }
}

#endif
