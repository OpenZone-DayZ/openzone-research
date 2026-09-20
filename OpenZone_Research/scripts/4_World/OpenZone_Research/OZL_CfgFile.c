// Застосування конфігу з ФАЙЛА -- дорога моста.
//
// Редактор VPP віддає текст, і аппликатор розбирає його рядком; кандидат
// моста лежить файлом у теці обміну, і читається штатним завантажувачем,
// якому байдуже до розміру (правила бойового пакета -- півтора мегабайти).
// Далі хвіст той самий, що в аппликаторів: перевірка, ОДИН запис із бекапом,
// підміна живого об'єкта, яка сама перевіряє все проти гри й пересилає
// пакет синхронізації. Файл новішої версії, ніж знає цей білд, відкидається
// -- як і при завантаженні на старті.

class OZL_CfgFile
{
    static bool ApplyFile(string tag, string path, string by, out string why, out int warnings)
    {
        why = "";
        warnings = 0;
        if (!FileExist(path))
        {
            why = "no such file";
            return false;
        }
        string err;
        OZL_Config cfg = OZL_Config.Get();

        if (tag == OZL_Config.TAG_SETTINGS)
        {
            OZL_Settings c1 = new OZL_Settings();
            if (!JsonFileLoader<OZL_Settings>.LoadFile(path, c1, err))
                return Unreadable(tag, err, why);
            if (c1.Version > c1.LatestVersion())
                return Newer(tag, c1.Version, why);
            c1.Validate(warnings);
            OZ_ConfigLoader<OZL_Settings>.Save(OZL_Const.SETTINGS, tag, c1, true);
            return cfg.Replace(tag, c1, by);
        }
        if (tag == OZL_Config.TAG_POINT_TYPES)
        {
            OZL_PointTypes c2 = new OZL_PointTypes();
            if (!JsonFileLoader<OZL_PointTypes>.LoadFile(path, c2, err))
                return Unreadable(tag, err, why);
            if (c2.Version > c2.LatestVersion())
                return Newer(tag, c2.Version, why);
            c2.Validate(warnings);
            OZ_ConfigLoader<OZL_PointTypes>.Save(OZL_Const.POINT_TYPES, tag, c2, true);
            return cfg.Replace(tag, c2, by);
        }
        if (tag == OZL_Config.TAG_OWNERS)
        {
            OZL_Owners c3 = new OZL_Owners();
            if (!JsonFileLoader<OZL_Owners>.LoadFile(path, c3, err))
                return Unreadable(tag, err, why);
            if (c3.Version > c3.LatestVersion())
                return Newer(tag, c3.Version, why);
            c3.Validate(warnings);
            OZ_ConfigLoader<OZL_Owners>.Save(OZL_Const.OWNERS, tag, c3, true);
            return cfg.Replace(tag, c3, by);
        }
        if (tag == OZL_Config.TAG_RULES)
        {
            OZL_Rules c4 = new OZL_Rules();
            if (!JsonFileLoader<OZL_Rules>.LoadFile(path, c4, err))
                return Unreadable(tag, err, why);
            if (c4.Version > c4.LatestVersion())
                return Newer(tag, c4.Version, why);
            c4.Validate(warnings);
            OZ_ConfigLoader<OZL_Rules>.Save(OZL_Const.RULES, tag, c4, true);
            return cfg.Replace(tag, c4, by);
        }
        if (tag == OZL_Config.TAG_TREE)
        {
            OZL_TreeConfig c5 = new OZL_TreeConfig();
            if (!JsonFileLoader<OZL_TreeConfig>.LoadFile(path, c5, err))
                return Unreadable(tag, err, why);
            if (c5.Version > c5.LatestVersion())
                return Newer(tag, c5.Version, why);
            c5.Validate(warnings);
            OZ_ConfigLoader<OZL_TreeConfig>.Save(OZL_Const.TREE, tag, c5, true);
            return cfg.Replace(tag, c5, by);
        }
        if (tag == OZL_Config.TAG_DATA_ITEMS)
        {
            OZL_DataItems c6 = new OZL_DataItems();
            if (!JsonFileLoader<OZL_DataItems>.LoadFile(path, c6, err))
                return Unreadable(tag, err, why);
            if (c6.Version > c6.LatestVersion())
                return Newer(tag, c6.Version, why);
            c6.Validate(warnings);
            OZ_ConfigLoader<OZL_DataItems>.Save(OZL_Const.DATA_ITEMS, tag, c6, true);
            return cfg.Replace(tag, c6, by);
        }
        if (tag == OZL_Config.TAG_MODULES)
        {
            OZL_Modules c7 = new OZL_Modules();
            if (!JsonFileLoader<OZL_Modules>.LoadFile(path, c7, err))
                return Unreadable(tag, err, why);
            if (c7.Version > c7.LatestVersion())
                return Newer(tag, c7.Version, why);
            c7.Validate(warnings);
            OZ_ConfigLoader<OZL_Modules>.Save(OZL_Const.MODULES, tag, c7, true);
            return cfg.Replace(tag, c7, by);
        }
        if (tag == OZL_Config.TAG_SAMPLE_TYPES)
        {
            OZL_SampleTypes c8 = new OZL_SampleTypes();
            if (!JsonFileLoader<OZL_SampleTypes>.LoadFile(path, c8, err))
                return Unreadable(tag, err, why);
            if (c8.Version > c8.LatestVersion())
                return Newer(tag, c8.Version, why);
            c8.Validate(warnings);
            OZ_ConfigLoader<OZL_SampleTypes>.Save(OZL_Const.SAMPLE_TYPES, tag, c8, true);
            return cfg.Replace(tag, c8, by);
        }
        if (tag == OZL_Config.TAG_STATICS)
        {
            OZL_StaticsConfig c9 = new OZL_StaticsConfig();
            if (!JsonFileLoader<OZL_StaticsConfig>.LoadFile(path, c9, err))
                return Unreadable(tag, err, why);
            if (c9.Version > c9.LatestVersion())
                return Newer(tag, c9.Version, why);
            c9.Validate(warnings);
            OZ_ConfigLoader<OZL_StaticsConfig>.Save(OZL_Const.STATICS, tag, c9, true);
            return cfg.Replace(tag, c9, by);
        }

        why = "unknown config '" + tag + "'";
        return false;
    }

    private static bool Unreadable(string tag, string err, out string why)
    {
        why = "unreadable: " + err;
        OZL_Log.Warn("config " + tag + " from the bridge rejected: " + why);
        return false;
    }

    private static bool Newer(string tag, int version, out string why)
    {
        why = "version " + version.ToString() + " is newer than this build knows";
        OZL_Log.Warn("config " + tag + " from the bridge rejected: " + why);
        return false;
    }
}
