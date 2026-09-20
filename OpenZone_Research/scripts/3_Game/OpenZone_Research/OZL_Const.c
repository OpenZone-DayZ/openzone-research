// Константи мода досліджень.
//
// Префікс OZL_ (laboratory): OZR_ носить рація, OZS_ -- сховище. Усе, що
// мод називає на проводі чи на диску, зібране тут, щоб рядок, набраний двічі
// в двох файлах, не розійшовся мовчки.

class OZL_Const
{
    static const string LOG_PREFIX = "[OpenZone/Research] ";

    // Файли конфігів -- у теці ядра, за зразком серії (OZ_Radio_*, OZ_PDA_*).
    // Стан фракцій -- у власній підтеці: це не конфіг, а те, що змінює гра.
    static const string PROFILE_DIR = "$profile:OpenZone";
    static const string STATE_DIR   = "$profile:OpenZone\\research";

    static const string SETTINGS     = "$profile:OpenZone\\OZ_Research_Settings.json";
    static const string POINT_TYPES  = "$profile:OpenZone\\OZ_Research_PointTypes.json";
    static const string OWNERS       = "$profile:OpenZone\\OZ_Research_Owners.json";
    static const string RULES        = "$profile:OpenZone\\OZ_Research_Rules.json";
    static const string TREE         = "$profile:OpenZone\\OZ_Research_Tree.json";
    static const string DATA_ITEMS   = "$profile:OpenZone\\OZ_Research_DataItems.json";
    static const string MODULES      = "$profile:OpenZone\\OZ_Research_Modules.json";
    static const string SAMPLE_TYPES = "$profile:OpenZone\\OZ_Research_SampleTypes.json";
    static const string STATICS      = "$profile:OpenZone\\OZ_Research_Statics.json";
    static const string STATICS_STATE = "$profile:OpenZone\\OZ_Research_Statics_State.json";

    // Ім'я служби в реєстрі ядра (OZ_ServiceRegistry) і розділу в адмінському
    // реєстрі (OZ_AdminRegistry). Одне слово на обидва: це один мод.
    static const string SERVICE = "research";
    static const string SECTION = "research";

    // Операції служби (клієнт -> сервер).
    static const string OP_TREE     = "tree";
    static const string OP_RESEARCH = "research";

    // Що сервер каже показати (OZ_Show): екран дерева.
    static const string SHOW_TREE = "research_tree";

    // Рід у мостовому клієнті ядра, його дороги й тека обміну (міст пише
    // кандидатів конфігів, гра пише перелік класів).
    static const string BRIDGE_KIND   = "research";
    static const string ROUTE_BOOT    = "v1/research/boot";
    static const string ROUTE_CHANGED = "v1/research/changed";
    static const string ROUTE_RESULT  = "v1/research/result";
    static const string XCHG_DIR      = "$profile:OpenZone\\research\\xchg";

    // Ідентифікатор меню дерева. МАЄ БУТИ МАЛИМ (див. OZ_PdaConst: із великим
    // числом EnterScriptedMenu мовчки віддає NULL). Зайнято родиною OpenZone:
    // 131 КПК, 132 його HUD-редактор, 133 прив'язка, 134 клавіатура рації.
    static const int MENU_TREE = 135;
}
