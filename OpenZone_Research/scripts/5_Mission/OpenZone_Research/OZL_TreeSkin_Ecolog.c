// Вікно ecolog -- «Науковий термінал»: світлий лабораторний корпус, шестикутні датчики, протокол вузла в п'ять колонок.
//
// ПОКИ ЩО ЛИШЕ ДАНІ: геометрія (спека §3, мокап SKINS.ecolog), палітра (CSS
// мокапа body[data-f="ecolog"]; ті самі кольори -- у ui/tokens/ecolog.json), мітки (спека §3) і
// назви розкладок. Решту успадковано від OZL_TreeSkin. Поки розкладки
// ozl_tree_ecolog нема, меню показує це вікно зошитом neutral (один рядок у
// лозі). Свої частини і гачки допише задача цього вікна -- у цьому ж файлі
// (source/ui/SKINS.md).

#ifndef NO_GUI

class OZL_TreeSkin_Ecolog : OZL_TreeSkin
{
    static const string COMMON = "set:ozl_common image:";

    void OZL_TreeSkin_Ecolog()
    {
        Named("ecolog");
        Dir     = "right";
        NodeW   = 60;
        NodeH   = 60;
        Keep    = 78;
        Row     = 240;
        Col     = 150;
        Top     = 90;
        Side    = 10;
        // Центр форми в комірці -- поки комірка не намальована, форма в її куті.
        AnchorX = 30;
        AnchorY = 30;

        Txt      = ARGB(255, 212, 236, 245);
        Dim      = ARGB(255, 111, 147, 163);
        Acc      = ARGB(255, 73, 194, 240);
        Ok       = ARGB(255, 114, 219, 160);
        Bad      = ARGB(255, 255, 123, 107);
        LineDim  = ARGB(153, 111, 147, 163);
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255, 11, 26, 34);
        FogColor = ARGB(255, 10, 24, 31);

        // Сітка тла (.content .bg мокапа: --grid, --grid-step).
        GridStep  = 24;
        GridColor = ARGB(20, 120, 200, 240);

        // Мітки: замок / галка / крапка (спека §3) -- спільні фігури ozl_common.
        Marks.Insert(COMMON + "mark_lock");
        Marks.Insert(COMMON + "mark_check");
        Marks.Insert(COMMON + "mark_dot");

    }
}

#endif
