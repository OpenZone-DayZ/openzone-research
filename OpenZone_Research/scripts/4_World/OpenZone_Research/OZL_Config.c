// Живі конфіги мода: один синглтон, сім файлів, один порядок читання.
//
// Кожен файл -- клас на OZ_ConfigBase, читається загальним завантажувачем
// ядра (OZ_ConfigLoader: бекап при записі, карантин битого файла, старт на
// умовчаннях із рядком ERROR) і реєструється в редакторі ядра
// (OZ_AdminCfg): розділ CONFIG у VPP показує текст, приймає правку й кличе
// застосувач, а той -- ті самі перевірки, що й завантажувач. Своїх операцій
// «upsert/delete» у мода немає: правити поля -- справа ядра.
//
// ПОРЯДОК ЗНАЧУЩИЙ: правила, дерево й модулі перевіряються ПРОТИ типів
// балів і проти гри (класи предметів, лінії в config.cpp), тож Check() іде
// після того, як усе прочитано, і повторюється після кожної правки.

// Застосувач на кожен файл: розібрати в НОВИЙ об'єкт, перевірити, зберегти
// з бекапом, підмінити живий. Сім однакових класів, а не один
// узагальнений: `new T()` у шаблоні Enforce не компілюється (Bad type 'T',
// зміряно 2026-09-20), тож узагальнити можна лише те, що не створює.
// Спільне -- відмова з причиною в лог -- у OZL_Config.Rejected.

class OZL_SettingsApplier : OZ_AdminCfgApplier
{
    override bool Apply(string json)
    {
        OZL_Settings c = new OZL_Settings();
        string err;
        if (!JsonFileLoader<OZL_Settings>.LoadData(json, c, err))
            return OZL_Config.Rejected(OZL_Config.TAG_SETTINGS, err);
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_Settings>.Save(OZL_Const.SETTINGS, OZL_Config.TAG_SETTINGS, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_SETTINGS, c);
    }
}

class OZL_PointTypesApplier : OZ_AdminCfgApplier
{
    override bool Apply(string json)
    {
        OZL_PointTypes c = new OZL_PointTypes();
        string err;
        if (!JsonFileLoader<OZL_PointTypes>.LoadData(json, c, err))
            return OZL_Config.Rejected(OZL_Config.TAG_POINT_TYPES, err);
        if (OZL_Config.Stale(OZL_Config.TAG_POINT_TYPES, c))
            return false;
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_PointTypes>.Save(OZL_Const.POINT_TYPES, OZL_Config.TAG_POINT_TYPES, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_POINT_TYPES, c);
    }
}

class OZL_OwnersApplier : OZ_AdminCfgApplier
{
    override bool Apply(string json)
    {
        OZL_Owners c = new OZL_Owners();
        string err;
        if (!JsonFileLoader<OZL_Owners>.LoadData(json, c, err))
            return OZL_Config.Rejected(OZL_Config.TAG_OWNERS, err);
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_Owners>.Save(OZL_Const.OWNERS, OZL_Config.TAG_OWNERS, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_OWNERS, c);
    }
}

class OZL_RulesApplier : OZ_AdminCfgApplier
{
    override bool Apply(string json)
    {
        OZL_Rules c = new OZL_Rules();
        string err;
        if (!JsonFileLoader<OZL_Rules>.LoadData(json, c, err))
            return OZL_Config.Rejected(OZL_Config.TAG_RULES, err);
        if (OZL_Config.Stale(OZL_Config.TAG_RULES, c))
            return false;
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_Rules>.Save(OZL_Const.RULES, OZL_Config.TAG_RULES, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_RULES, c);
    }
}

class OZL_TreeApplier : OZ_AdminCfgApplier
{
    override bool Apply(string json)
    {
        OZL_TreeConfig c = new OZL_TreeConfig();
        string err;
        if (!JsonFileLoader<OZL_TreeConfig>.LoadData(json, c, err))
            return OZL_Config.Rejected(OZL_Config.TAG_TREE, err);
        if (OZL_Config.Stale(OZL_Config.TAG_TREE, c))
            return false;
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_TreeConfig>.Save(OZL_Const.TREE, OZL_Config.TAG_TREE, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_TREE, c);
    }
}

class OZL_ModulesApplier : OZ_AdminCfgApplier
{
    override bool Apply(string json)
    {
        OZL_Modules c = new OZL_Modules();
        string err;
        if (!JsonFileLoader<OZL_Modules>.LoadData(json, c, err))
            return OZL_Config.Rejected(OZL_Config.TAG_MODULES, err);
        if (OZL_Config.Stale(OZL_Config.TAG_MODULES, c))
            return false;
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_Modules>.Save(OZL_Const.MODULES, OZL_Config.TAG_MODULES, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_MODULES, c);
    }
}

class OZL_StaticsApplier : OZ_AdminCfgApplier
{
    override bool Apply(string json)
    {
        OZL_StaticsConfig c = new OZL_StaticsConfig();
        string err;
        if (!JsonFileLoader<OZL_StaticsConfig>.LoadData(json, c, err))
            return OZL_Config.Rejected(OZL_Config.TAG_STATICS, err);
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_StaticsConfig>.Save(OZL_Const.STATICS, OZL_Config.TAG_STATICS, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_STATICS, c);
    }
}

class OZL_Config
{
    static const string TAG_SETTINGS     = "ResearchSettings";
    static const string TAG_POINT_TYPES  = "ResearchPointTypes";
    static const string TAG_OWNERS       = "ResearchOwners";
    static const string TAG_RULES        = "ResearchRules";
    static const string TAG_TREE         = "ResearchTree";
    static const string TAG_MODULES      = "ResearchModules";
    static const string TAG_STATICS      = "ResearchStatics";

    private static ref OZL_Config s_Inst;

    static OZL_Config Get()
    {
        if (!s_Inst)
            s_Inst = new OZL_Config();
        return s_Inst;
    }

    private ref OZL_Settings      m_Settings;
    private ref OZL_PointTypes    m_PointTypes;
    private ref OZL_Owners        m_Owners;
    private ref OZL_Rules         m_Rules;
    private ref OZL_TreeConfig    m_Tree;
    private ref OZL_Modules       m_Modules;
    private ref OZL_StaticsConfig m_Statics;

    // Зростає на кожну правку: клієнтові, що тримає дерево, є з чим звірити.
    private int m_Revision = 0;

    OZL_Settings      Settings()    { return m_Settings; }
    OZL_PointTypes    PointTypes()  { return m_PointTypes; }
    OZL_Owners        Owners()      { return m_Owners; }
    OZL_Rules         Rules()       { return m_Rules; }
    OZL_TreeConfig    Tree()        { return m_Tree; }
    OZL_Modules       Modules()     { return m_Modules; }
    OZL_StaticsConfig Statics()     { return m_Statics; }
    int               Revision()    { return m_Revision; }

    // Скільки перевірок відхилили на останньому читанні -- для рядка
    // готовності: «правил 43» нічого не каже, «правил 43, проблем 2» каже.
    private int m_Problems = 0;
    int Problems() { return m_Problems; }

    // Відхилений текст файла не торкається; причина -- у лог, редакторові --
    // ключ STR_OZ_ERR_CFG_REJECTED від ядра.
    static bool Rejected(string tag, string err)
    {
        OZL_Log.Warn("config " + tag + " rejected: " + err);
        return false;
    }

    // Правка зі старою версією файла (редактор, що не знає ліній) не приймається:
    // завантажувач при наступному старті або відправив би такий файл у карантин,
    // або мігрував би його сам (типи балів і правила версії 2) -- правка мусить
    // прийти вже в найновішій версії.
    static bool Stale(string tag, OZ_ConfigBase c)
    {
        if (c.Version == c.LatestVersion())
            return false;
        Rejected(tag, "version " + c.Version.ToString() + ", this build reads " + c.LatestVersion().ToString());
        return true;
    }

    static void ServerLoad()
    {
        Get().LoadAll();
    }

    static void Reload()
    {
        Get().LoadAll();
        OZL_Log.Info("configs reloaded, revision " + Get().Revision().ToString());
    }

    private void LoadAll()
    {
        OZL_Settings settings = new OZL_Settings();
        OZ_ConfigLoader<OZL_Settings>.Load(OZL_Const.SETTINGS, TAG_SETTINGS, settings);
        m_Settings = settings.Copy();

        // Свіжий профіль отримує повний пакет, який мод везе в собі; наявний
        // файл не чіпається (OZL_Defaults).
        OZL_Defaults.SeedAll();
        LoadPack();

        // Порожній набір -- ні власників, ні правил, ні дерева -- записував свіжий
        // старт, поки мод не віз пакета. Такий профіль отримує пакет поверх (старі
        // файли -- у Backup). Заповнене бодай щось із трьох -- сервер налаштований,
        // і його файли не чіпаються.
        if (m_Owners.Owners.Count() == 0 && m_Rules.Count() == 0 && m_Tree.NodeCount() == 0)
        {
            if (OZL_Defaults.ReplaceAll())
                LoadPack();
        }

        CheckAll();
        m_Revision++;
    }

    // Шість конфігів пакета, у тому порядку, в якому їх читав LoadAll.
    private void LoadPack()
    {
        OZL_PointTypes pt = new OZL_PointTypes();
        OZ_ConfigLoader<OZL_PointTypes>.Load(OZL_Const.POINT_TYPES, TAG_POINT_TYPES, pt);
        m_PointTypes = pt.Copy();

        OZL_Owners owners = new OZL_Owners();
        OZ_ConfigLoader<OZL_Owners>.Load(OZL_Const.OWNERS, TAG_OWNERS, owners);
        m_Owners = owners.Copy();

        OZL_TreeConfig tree = new OZL_TreeConfig();
        OZ_ConfigLoader<OZL_TreeConfig>.Load(OZL_Const.TREE, TAG_TREE, tree);
        m_Tree = tree.Copy();

        OZL_Rules rules = new OZL_Rules();
        OZ_ConfigLoader<OZL_Rules>.Load(OZL_Const.RULES, TAG_RULES, rules);
        m_Rules = rules.Copy();

        OZL_Modules modules = new OZL_Modules();
        OZ_ConfigLoader<OZL_Modules>.Load(OZL_Const.MODULES, TAG_MODULES, modules);
        m_Modules = modules.Copy();

        OZL_StaticsConfig statics = new OZL_StaticsConfig();
        OZ_ConfigLoader<OZL_StaticsConfig>.Load(OZL_Const.STATICS, TAG_STATICS, statics);
        m_Statics = statics.Copy();
    }

    // Перевірки проти гри й один одного -- після того, як усе прочитано.
    private void CheckAll()
    {
        int n;
        m_Problems = 0;
        m_Rules.Check(m_PointTypes, n);
        m_Problems += n;
        m_Tree.Check(m_PointTypes, n);
        m_Problems += n;
        m_Modules.Check(n);
        m_Problems += n;
    }

    // Один файл із редактора ядра: підмінити за тегом, перевірити все знову.
    // Копія знову, бо застосувач віддає об'єкт, який щойно зробив
    // серіалізатор.
    bool Replace(string tag, OZ_ConfigBase cfg, string by = "vpp")
    {
        if (tag == TAG_SETTINGS)
            m_Settings = OZL_Settings.Cast(cfg).Copy();
        else if (tag == TAG_POINT_TYPES)
            m_PointTypes = OZL_PointTypes.Cast(cfg).Copy();
        else if (tag == TAG_OWNERS)
            m_Owners = OZL_Owners.Cast(cfg).Copy();
        else if (tag == TAG_RULES)
            m_Rules = OZL_Rules.Cast(cfg).Copy();
        else if (tag == TAG_TREE)
            m_Tree = OZL_TreeConfig.Cast(cfg).Copy();
        else if (tag == TAG_MODULES)
            m_Modules = OZL_Modules.Cast(cfg).Copy();
        else if (tag == TAG_STATICS)
            m_Statics = OZL_StaticsConfig.Cast(cfg).Copy();
        else
        {
            OZL_Log.Error("config replace: unknown tag " + tag);
            return false;
        }

        CheckAll();
        m_Revision++;
        OZL_Log.Info("config " + tag + " replaced, revision " + m_Revision.ToString());

        // Класи терміналів у клієнтів беруться з пакета синхронізації ядра;
        // після правки той пакет треба надіслати знову всім, хто в грі.
        OZ_SyncSender.SendAll("research configs edited");

        // Міст перечитує файл із профілю сам; лист лише каже, який і хто.
        OZL_Bridge.Changed(tag, by);
        return true;
    }

    // Класи терміналів -- у пакет синхронізації ядра, порціями, коротшими за
    // межу рядка рушія. Кличе інвокер OZ_SyncExtras через OZL_Module.
    static void FillTerminals(OZ_SyncPayload p)
    {
        OZL_Config cfg = Get();
        int i;
        array<string> terms;
        cfg.m_Owners.TerminalUnion(terms);
        string chunk = "";
        int chunks = 0;
        for (i = 0; i < terms.Count(); i++)
        {
            if (chunk != "" && chunk.Length() + terms[i].Length() + 1 > OZL_ClientConfig.CHUNK_CHARS)
            {
                OZ_SyncExtras.Put(p, OZL_ClientConfig.SYNC_TERMINALS + chunks.ToString(), chunk);
                chunks++;
                chunk = "";
            }
            if (chunk != "")
                chunk += ",";
            chunk += terms[i];
        }
        if (chunk != "")
        {
            OZ_SyncExtras.Put(p, OZL_ClientConfig.SYNC_TERMINALS + chunks.ToString(), chunk);
            chunks++;
        }
        OZ_SyncExtras.Put(p, OZL_ClientConfig.SYNC_TERMINALS_N, chunks.ToString());
    }

    // Реєстрація в редакторі ядра -- по рядку на файл, після першого читання.
    // Сім тегів у порядку файлів -- для листа boot і для reload.
    static void Tags(array<string> outTags)
    {
        outTags.Insert(TAG_SETTINGS);
        outTags.Insert(TAG_POINT_TYPES);
        outTags.Insert(TAG_OWNERS);
        outTags.Insert(TAG_RULES);
        outTags.Insert(TAG_TREE);
        outTags.Insert(TAG_MODULES);
        outTags.Insert(TAG_STATICS);
    }
    static void RegisterEditors()
    {
        OZ_AdminCfg.Register(TAG_SETTINGS, OZL_Const.SETTINGS, new OZL_SettingsApplier(), "research");
        OZ_AdminCfg.Register(TAG_POINT_TYPES, OZL_Const.POINT_TYPES, new OZL_PointTypesApplier(), "research");
        OZ_AdminCfg.Register(TAG_OWNERS, OZL_Const.OWNERS, new OZL_OwnersApplier(), "research");
        OZ_AdminCfg.Register(TAG_RULES, OZL_Const.RULES, new OZL_RulesApplier(), "research");
        OZ_AdminCfg.Register(TAG_TREE, OZL_Const.TREE, new OZL_TreeApplier(), "research");
        OZ_AdminCfg.Register(TAG_MODULES, OZL_Const.MODULES, new OZL_ModulesApplier(), "research");
        OZ_AdminCfg.Register(TAG_STATICS, OZL_Const.STATICS, new OZL_StaticsApplier(), "research");
    }

    // Лічильники рядка готовності, у формі `ключ=значення`.
    string Counters()
    {
        string s = "owners=" + m_Owners.Owners.Count().ToString();
        s += " pointTypes=" + m_PointTypes.PointTypes.Count().ToString();
        s += " rules=" + m_Rules.Count().ToString();
        s += " nodes=" + m_Tree.NodeCount().ToString();
        s += " modules=" + m_Modules.Modules.Count().ToString();
        s += " statics=" + m_Statics.Entries.Count().ToString();
        s += " problems=" + m_Problems.ToString();
        return s;
    }
}
