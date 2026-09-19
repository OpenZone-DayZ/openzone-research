// Живі конфіги мода: один синглтон, дев'ять файлів, один порядок читання.
//
// Кожен файл -- клас на OZ_ConfigBase, читається загальним завантажувачем
// ядра (OZ_ConfigLoader: бекап при записі, карантин битого файла, старт на
// умовчаннях із рядком ERROR) і реєструється в редакторі ядра
// (OZ_AdminCfg): розділ CONFIG у VPP показує текст, приймає правку й кличе
// застосувач, а той -- ті самі перевірки, що й завантажувач. Своїх операцій
// «upsert/delete» у мода немає: правити поля -- справа ядра.
//
// ПОРЯДОК ЗНАЧУЩИЙ: правила, дерево й заготовки перевіряються ПРОТИ типів
// балів і проти гри (класи предметів), тож Check() іде після того, як усе
// прочитано, і повторюється після кожної правки.

// Застосувач на кожен файл: розібрати в НОВИЙ об'єкт, перевірити, зберегти
// з бекапом, підмінити живий. Дев'ять однакових класів, а не один
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
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_TreeConfig>.Save(OZL_Const.TREE, OZL_Config.TAG_TREE, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_TREE, c);
    }
}

class OZL_DataItemsApplier : OZ_AdminCfgApplier
{
    override bool Apply(string json)
    {
        OZL_DataItems c = new OZL_DataItems();
        string err;
        if (!JsonFileLoader<OZL_DataItems>.LoadData(json, c, err))
            return OZL_Config.Rejected(OZL_Config.TAG_DATA_ITEMS, err);
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_DataItems>.Save(OZL_Const.DATA_ITEMS, OZL_Config.TAG_DATA_ITEMS, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_DATA_ITEMS, c);
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
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_Modules>.Save(OZL_Const.MODULES, OZL_Config.TAG_MODULES, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_MODULES, c);
    }
}

class OZL_SampleTypesApplier : OZ_AdminCfgApplier
{
    override bool Apply(string json)
    {
        OZL_SampleTypes c = new OZL_SampleTypes();
        string err;
        if (!JsonFileLoader<OZL_SampleTypes>.LoadData(json, c, err))
            return OZL_Config.Rejected(OZL_Config.TAG_SAMPLE_TYPES, err);
        int warnings;
        c.Validate(warnings);
        OZ_ConfigLoader<OZL_SampleTypes>.Save(OZL_Const.SAMPLE_TYPES, OZL_Config.TAG_SAMPLE_TYPES, c, true);
        return OZL_Config.Get().Replace(OZL_Config.TAG_SAMPLE_TYPES, c);
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
    static const string TAG_DATA_ITEMS   = "ResearchDataItems";
    static const string TAG_MODULES      = "ResearchModules";
    static const string TAG_SAMPLE_TYPES = "ResearchSampleTypes";
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
    private ref OZL_DataItems     m_DataItems;
    private ref OZL_Modules       m_Modules;
    private ref OZL_SampleTypes   m_SampleTypes;
    private ref OZL_StaticsConfig m_Statics;

    // Зростає на кожну правку: клієнтові, що тримає дерево, є з чим звірити.
    private int m_Revision = 0;

    OZL_Settings      Settings()    { return m_Settings; }
    OZL_PointTypes    PointTypes()  { return m_PointTypes; }
    OZL_Owners        Owners()      { return m_Owners; }
    OZL_Rules         Rules()       { return m_Rules; }
    OZL_TreeConfig    Tree()        { return m_Tree; }
    OZL_DataItems     DataItems()   { return m_DataItems; }
    OZL_Modules       Modules()     { return m_Modules; }
    OZL_SampleTypes   SampleTypes() { return m_SampleTypes; }
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

        OZL_DataItems data = new OZL_DataItems();
        OZ_ConfigLoader<OZL_DataItems>.Load(OZL_Const.DATA_ITEMS, TAG_DATA_ITEMS, data);
        m_DataItems = data.Copy();

        OZL_Modules modules = new OZL_Modules();
        OZ_ConfigLoader<OZL_Modules>.Load(OZL_Const.MODULES, TAG_MODULES, modules);
        m_Modules = modules.Copy();

        OZL_SampleTypes samples = new OZL_SampleTypes();
        OZ_ConfigLoader<OZL_SampleTypes>.Load(OZL_Const.SAMPLE_TYPES, TAG_SAMPLE_TYPES, samples);
        m_SampleTypes = samples.Copy();

        OZL_StaticsConfig statics = new OZL_StaticsConfig();
        OZ_ConfigLoader<OZL_StaticsConfig>.Load(OZL_Const.STATICS, TAG_STATICS, statics);
        m_Statics = statics.Copy();

        CheckAll();
        RefreshNames();
        m_Revision++;
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
        m_DataItems.Check(m_PointTypes, n);
        m_Problems += n;
        m_Modules.Check(n);
        m_Problems += n;
        m_SampleTypes.Check(n);
        m_Problems += n;
    }

    // Один файл із редактора ядра: підмінити за тегом, перевірити все знову.
    // Копія знову, бо застосувач віддає об'єкт, який щойно зробив
    // серіалізатор.
    bool Replace(string tag, OZ_ConfigBase cfg)
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
        else if (tag == TAG_DATA_ITEMS)
            m_DataItems = OZL_DataItems.Cast(cfg).Copy();
        else if (tag == TAG_MODULES)
            m_Modules = OZL_Modules.Cast(cfg).Copy();
        else if (tag == TAG_SAMPLE_TYPES)
            m_SampleTypes = OZL_SampleTypes.Cast(cfg).Copy();
        else if (tag == TAG_STATICS)
            m_Statics = OZL_StaticsConfig.Cast(cfg).Copy();
        else
        {
            OZL_Log.Error("config replace: unknown tag " + tag);
            return false;
        }

        CheckAll();
        RefreshNames();
        m_Revision++;
        OZL_Log.Info("config " + tag + " replaced, revision " + m_Revision.ToString());

        // Імена предметів у клієнтів беруться з пакета синхронізації ядра;
        // після правки той пакет треба надіслати знову всім, хто в грі.
        OZ_SyncSender.SendAll("research configs edited");
        return true;
    }

    // Серверна дорога наповнення довідника імен (OZL_Names): з живих конфігів,
    // після кожного читання й кожної правки.
    private void RefreshNames()
    {
        OZL_Names.Clear();
        int i;
        for (i = 0; i < m_SampleTypes.Items.Count(); i++)
        {
            OZL_SampleTypeDef s = m_SampleTypes.Items[i];
            if (s && s.Enabled)
                OZL_Names.Set(s.Id, s.Name, s.Description);
        }
        for (i = 0; i < m_DataItems.Items.Count(); i++)
        {
            OZL_DataDef d = m_DataItems.Items[i];
            if (d && d.Enabled)
                OZL_Names.Set(d.Id, d.Name, d.Description);
        }
    }

    // Імена -- у пакет синхронізації ядра, по додатку на предмет. Кличе
    // інвокер OZ_SyncExtras через OZL_Module на кожну відправку пакета.
    static void FillNames(OZ_SyncPayload p)
    {
        OZL_Config cfg = Get();
        int i;
        int n = 0;
        for (i = 0; i < cfg.m_SampleTypes.Items.Count(); i++)
        {
            OZL_SampleTypeDef s = cfg.m_SampleTypes.Items[i];
            if (!s || !s.Enabled)
                continue;
            OZL_Names.PutEntry(p, OZL_Names.SYNC_SAMPLE + n.ToString(), s.Id, s.Name, s.Description);
            n++;
        }
        OZ_SyncExtras.Put(p, OZL_Names.SYNC_SAMPLES, n.ToString());

        n = 0;
        for (i = 0; i < cfg.m_DataItems.Items.Count(); i++)
        {
            OZL_DataDef d = cfg.m_DataItems.Items[i];
            if (!d || !d.Enabled)
                continue;
            OZL_Names.PutEntry(p, OZL_Names.SYNC_DATA + n.ToString(), d.Id, d.Name, d.Description);
            n++;
        }
        OZ_SyncExtras.Put(p, OZL_Names.SYNC_DATA_N, n.ToString());
    }

    // Реєстрація в редакторі ядра -- по рядку на файл, після першого читання.
    static void RegisterEditors()
    {
        OZ_AdminCfg.Register(TAG_SETTINGS, OZL_Const.SETTINGS, new OZL_SettingsApplier(), "research");
        OZ_AdminCfg.Register(TAG_POINT_TYPES, OZL_Const.POINT_TYPES, new OZL_PointTypesApplier(), "research");
        OZ_AdminCfg.Register(TAG_OWNERS, OZL_Const.OWNERS, new OZL_OwnersApplier(), "research");
        OZ_AdminCfg.Register(TAG_RULES, OZL_Const.RULES, new OZL_RulesApplier(), "research");
        OZ_AdminCfg.Register(TAG_TREE, OZL_Const.TREE, new OZL_TreeApplier(), "research");
        OZ_AdminCfg.Register(TAG_DATA_ITEMS, OZL_Const.DATA_ITEMS, new OZL_DataItemsApplier(), "research");
        OZ_AdminCfg.Register(TAG_MODULES, OZL_Const.MODULES, new OZL_ModulesApplier(), "research");
        OZ_AdminCfg.Register(TAG_SAMPLE_TYPES, OZL_Const.SAMPLE_TYPES, new OZL_SampleTypesApplier(), "research");
        OZ_AdminCfg.Register(TAG_STATICS, OZL_Const.STATICS, new OZL_StaticsApplier(), "research");
    }

    // Лічильники рядка готовності, у формі `ключ=значення`.
    string Counters()
    {
        string s = "owners=" + m_Owners.Owners.Count().ToString();
        s += " pointTypes=" + m_PointTypes.PointTypes.Count().ToString();
        s += " rules=" + m_Rules.Count().ToString();
        s += " nodes=" + m_Tree.NodeCount().ToString();
        s += " dataItems=" + m_DataItems.Items.Count().ToString();
        s += " modules=" + m_Modules.Modules.Count().ToString();
        s += " sampleTypes=" + m_SampleTypes.Items.Count().ToString();
        s += " statics=" + m_Statics.Entries.Count().ToString();
        s += " problems=" + m_Problems.ToString();
        return s;
    }
}
