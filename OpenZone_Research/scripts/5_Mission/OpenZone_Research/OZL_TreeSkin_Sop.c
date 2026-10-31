// Вікно sop -- «Тактичний планшет»: кінескоп, HUD з позивним і шкалами-боєкомплектом, рамка цілі.
//
// ПОКИ ЩО ЛИШЕ ДАНІ: геометрія (спека §3, мокап SKINS.sop), палітра (CSS
// мокапа body[data-f="sop"]; ті самі кольори -- у ui/tokens/sop.json), мітки (спека §3) і
// назви розкладок. Решту успадковано від OZL_TreeSkin. Поки розкладки
// ozl_tree_sop нема, меню показує це вікно тетрадю neutral (один рядок у
// лозі). Свої частини і гачки допише задача цього вікна -- у цьому ж файлі
// (source/ui/SKINS.md).

#ifndef NO_GUI

class OZL_TreeSkin_Sop : OZL_TreeSkin
{
    static const string COMMON = "set:ozl_common image:";

    void OZL_TreeSkin_Sop()
    {
        Named("sop");
        Dir     = "right";
        NodeW   = 88;
        NodeH   = 88;
        Keep    = 98;
        Row     = 235;
        Col     = 180;
        Top     = 90;
        Side    = 60;
        // Центр форми в комірці -- поки комірка не намальована, форма в її куті.
        AnchorX = 44;
        AnchorY = 44;

        Txt      = ARGB(255, 236, 223, 174);
        Dim      = ARGB(255, 154, 141, 92);
        Acc      = ARGB(255, 255, 185, 53);
        Ok       = ARGB(255, 180, 220, 106);
        Bad      = ARGB(255, 255, 106, 74);
        LineDim  = ARGB(153, 154, 141, 92);
        LineLit  = Txt;
        LineHl   = Acc;
        Lcd      = ARGB(255, 18, 17, 9);
        FogColor = ARGB(255, 17, 16, 8);

        // Сітка тла (.content .bg мокапа: --grid, --grid-step).
        GridStep  = 56;
        GridColor = ARGB(18, 255, 200, 110);

        // Мітки: замок / галка / крапка (спека §3) -- спільні фігури ozl_common.
        Marks.Insert(COMMON + "mark_lock");
        Marks.Insert(COMMON + "mark_check");
        Marks.Insert(COMMON + "mark_dot");

    }
}

#endif
