// Вікно duty -- «Реєстр досліджень»: бланк на сукні, реєстр-таблиця, схема по лінійці, картка на скріпці з печаткою.
//
// ПОКИ ЩО ЛИШЕ ДАНІ: геометрія (спека §3, мокап SKINS.duty), палітра (CSS
// мокапа body[data-f="duty"]; ті самі кольори -- у ui/tokens/duty.json), мітки (спека §3) і
// назви розкладок. Решту успадковано від OZL_TreeSkin. Поки розкладки
// ozl_tree_duty нема, меню показує це вікно тетрадю neutral (один рядок у
// лозі). Свої частини і гачки допише задача цього вікна -- у цьому ж файлі
// (source/ui/SKINS.md).

#ifndef NO_GUI

class OZL_TreeSkin_Duty : OZL_TreeSkin
{
    static const string COMMON = "set:ozl_common image:";

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
        // Центр форми в комірці -- поки комірка не намальована, форма в її куті.
        AnchorX = 80;
        AnchorY = 25;

        Txt      = ARGB(255, 30, 28, 25);
        Dim      = ARGB(255, 107, 101, 88);
        Acc      = ARGB(255, 165, 36, 26);
        Ok       = ARGB(255, 58, 53, 137);
        Bad      = ARGB(255, 184, 86, 15);
        LineDim  = ARGB(255, 163, 156, 138);
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255, 235, 230, 213);
        FogColor = ARGB(255, 220, 214, 194);

        // Мітки: замок / галка / крапка (спека §3) -- спільні фігури ozl_common.
        Marks.Insert(COMMON + "mark_lock");
        Marks.Insert(COMMON + "mark_check");
        Marks.Insert(COMMON + "mark_dot");

    }
}

#endif
