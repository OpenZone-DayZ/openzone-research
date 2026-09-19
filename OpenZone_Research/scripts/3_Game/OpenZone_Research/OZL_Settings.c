// Налаштування мода: OZ_Research_Settings.json.
//
// Чотири поля, і це не бідність. Права адміна -- у ядра (OZ_Perm), рівень
// відладки -- у ядра, термінали й фон дерева -- у власників (OZ_Research_Owners),
// тож тут лишилось те, що стосується ВСІХ фракцій одразу.

class OZL_Settings : OZ_ConfigBase
{
    // Кому йде пул, коли ядро не знає гравця (ще не заходив, або мода фракцій
    // немає зовсім). Має бути придатним для імені файла.
    string DefaultOwner = "loner";

    // Хто тратить пул: лідер завжди, далі -- власники поста. Порожньо означає
    // «ніхто, крім лідера». ResearchPost -- для угруповань, BasePost -- для
    // власників на базовій осі (у сталкерів лідера немає, є, скажімо, староста).
    string ResearchPost = "";
    string BasePost     = "";

    // Скільки рівнів дерева вище доступного показувати замкненими.
    int TreeVisibilityDepth = 1;

    override int LatestVersion()
    {
        return 1;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        DefaultOwner        = "loner";
        ResearchPost        = "";
        BasePost            = "";
        TreeVisibilityDepth = 1;
    }

    override void Validate(out int warnings)
    {
        warnings = 0;

        if (!OZL_Ids.IsPathSafe(DefaultOwner))
        {
            OZL_Log.Warn("Settings: DefaultOwner '" + DefaultOwner + "' is not safe as a file name, using 'loner'");
            DefaultOwner = "loner";
            warnings++;
        }

        if (TreeVisibilityDepth < 0 || TreeVisibilityDepth > 10)
        {
            OZL_Log.Warn("Settings: TreeVisibilityDepth " + TreeVisibilityDepth.ToString() + " is outside 0..10, using 1");
            TreeVisibilityDepth = 1;
            warnings++;
        }
    }

    // Копія в об'єкт, зроблений скриптом: те, що прочитав серіалізатор, живе
    // рівно до кінця розбору (шапка OZ_ConfigBase).
    OZL_Settings Copy()
    {
        OZL_Settings c = new OZL_Settings();
        c.Version             = Version;
        c.DefaultOwner        = DefaultOwner;
        c.ResearchPost        = ResearchPost;
        c.BasePost            = BasePost;
        c.TreeVisibilityDepth = TreeVisibilityDepth;
        return c;
    }
}
