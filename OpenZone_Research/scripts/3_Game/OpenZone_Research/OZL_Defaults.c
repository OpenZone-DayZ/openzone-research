// Конфіги, з якими стартує свіжий сервер.
//
// Мод везе в собі пакет прикладів (examples/example у репозиторії) у теці
// OpenZone_Research/defaults. Файл, якого в профілі ще немає, копіюється
// звідти ДО того, як його прочитає завантажувач. Файл, що вже лежить у
// профілі, -- змінений, зламаний чи іншої версії -- не чіпається: що з ним
// робити, і далі вирішує OZ_ConfigLoader.
//
// Один виняток -- порожній набір (OZL_Config.LoadAll): ні власників, ні правил,
// ні дерева. Саме його записував свіжий старт, поки мод не віз пакета, і
// сервер, що вже так стартував, отримує пакет поверх; старі файли спершу йдуть
// у Backup під іменем before-defaults.<файл>.
//
// Без цього свіжий сервер піднімався порожнім (owners=0 rules=0 nodes=0), і
// для того, хто ставив мод уперше, це виглядало як мод, що не завантажився.
//
// Копія рядок за рядком: OpenFile відкриває упаковані файли модів, а FGets
// віддає рядок до 8198 символів цілим (виміряно 2026-09-20, OZ_StringTables);
// найдовший рядок пакета -- 780 символів.

class OZL_Defaults
{
    static const string DIR = "OpenZone_Research/defaults/";

    // Шість файлів пакета. Налаштувань серед них немає: ті створює OZL_Settings.
    static void SeedAll()
    {
        Seed(OZL_Const.POINT_TYPES, "OZ_Research_PointTypes.json");
        Seed(OZL_Const.OWNERS, "OZ_Research_Owners.json");
        Seed(OZL_Const.TREE, "OZ_Research_Tree.json");
        Seed(OZL_Const.RULES, "OZ_Research_Rules.json");
        Seed(OZL_Const.MODULES, "OZ_Research_Modules.json");
        Seed(OZL_Const.STATICS, "OZ_Research_Statics.json");
    }

    // Пакет поверх порожнього набору. Повертає, чи записано бодай один файл.
    static bool ReplaceAll()
    {
        OZL_Log.Info("the profile holds no owners, rules or tree - writing the mod's default pack over it, the old files go to Backup");
        bool any = false;
        if (Replace(OZL_Const.POINT_TYPES, "OZ_Research_PointTypes.json"))
            any = true;
        if (Replace(OZL_Const.OWNERS, "OZ_Research_Owners.json"))
            any = true;
        if (Replace(OZL_Const.TREE, "OZ_Research_Tree.json"))
            any = true;
        if (Replace(OZL_Const.RULES, "OZ_Research_Rules.json"))
            any = true;
        if (Replace(OZL_Const.MODULES, "OZ_Research_Modules.json"))
            any = true;
        if (Replace(OZL_Const.STATICS, "OZ_Research_Statics.json"))
            any = true;
        return any;
    }

    private static bool Replace(string profilePath, string fileName)
    {
        if (FileExist(profilePath))
        {
            OZ_Json.EnsureDir(OZ_Const.BACKUP_DIR);
            string bak = OZ_Const.BACKUP_DIR + "\\before-defaults." + fileName;
            if (!CopyFile(profilePath, bak))
            {
                OZL_Log.Error("cannot back up " + profilePath + " - leaving it as it is");
                return false;
            }
            if (!DeleteFile(profilePath))
            {
                OZL_Log.Error("cannot replace " + profilePath + " - leaving it as it is");
                return false;
            }
        }
        return Seed(profilePath, fileName);
    }

    // Повертає, чи записано файл.
    static bool Seed(string profilePath, string fileName)
    {
        if (FileExist(profilePath))
            return false;

        FileHandle src = OpenFile(DIR + fileName, FileMode.READ);
        if (src == 0)
        {
            OZL_Log.Warn("the mod carries no default " + fileName + " - starting without it");
            return false;
        }

        OZ_Json.EnsureDir(OZL_Const.PROFILE_DIR);
        FileHandle dst = OpenFile(profilePath, FileMode.WRITE);
        if (dst == 0)
        {
            CloseFile(src);
            OZL_Log.Error("cannot write " + profilePath + " - starting without the default " + fileName);
            return false;
        }

        string line;
        int lines = 0;
        while (FGets(src, line) >= 0)
        {
            FPrintln(dst, line);
            lines++;
        }
        CloseFile(src);
        CloseFile(dst);

        string msg = "wrote the mod's default " + fileName + " into the profile, ";
        msg += lines.ToString() + " lines";
        OZL_Log.Info(msg);
        return true;
    }
}
