// Зразок: проміжний предмет ланцюжка з прихованим вмістом.
//
// Один скрипт-клас на тридцять config-класів (OZL_Sample_01..30 різняться лише
// моделлю): усі зразки з однаковим Content поводяться однаково, а різницю
// несуть приховані поля Content і Purity на самій сутності. Читає їх ПРИЛАД,
// а не гравець, тож ані видимої назви вмісту, ані дії «визначити» тут немає.
//
// ЖОДНОГО quantity в конфігу, і тут -- заборона стеків і поділу: рушій зливає
// стек одного класу, не дивлячись на скриптові поля, і вміст другого зразка
// зник би мовчки.
//
// На клієнт їде лише хеш вмісту (netsync): клієнт відрізняє «той самий» від
// «інший», не знаючи, який саме. Хеш не зберігається -- рахується з вмісту
// при завантаженні.

class OZL_Sample_Base : ItemBase
{
    protected string m_OZL_Content;
    protected float  m_OZL_Purity;
    protected int    m_OZL_ContentId;

    void OZL_Sample_Base()
    {
        RegisterNetSyncVariableInt("m_OZL_ContentId");
    }

    static string ContentOf(EntityAI e)
    {
        OZL_Sample_Base s = OZL_Sample_Base.Cast(e);
        if (!s)
            return "";
        return s.OZL_Content();
    }

    static float PurityOf(EntityAI e)
    {
        OZL_Sample_Base s = OZL_Sample_Base.Cast(e);
        if (!s)
            return 0;
        return s.OZL_Purity();
    }

    // Правило-пакувальник кладе вміст у щойно створений зразок.
    static void ApplyFields(EntityAI created, string content, float purity)
    {
        if (content == "")
            return;
        OZL_Sample_Base s = OZL_Sample_Base.Cast(created);
        if (!s)
            return;
        s.OZL_Set(content, purity);
    }

    void OZL_Set(string content, float purity)
    {
        m_OZL_Content   = content;
        m_OZL_Purity    = purity;
        m_OZL_ContentId = OZL_Hash.Of(content);
        SetSynchDirty();
        OZL_Log.Dbg("sample " + GetType() + ": content='" + m_OZL_Content + "' purity=" + m_OZL_Purity.ToString() + " id=" + m_OZL_ContentId.ToString());
    }

    string OZL_Content()
    {
        return m_OZL_Content;
    }

    float OZL_Purity()
    {
        return m_OZL_Purity;
    }

    int OZL_ContentId()
    {
        return m_OZL_ContentId;
    }

    // Ім'я з JSON адміністратора, а не з config.cpp. GetDisplayName, а не
    // NameOverride: рушій проганяє NameOverride через TranslateString, і
    // текст, який не є ключем таблиці рядків, псується.
    override string GetDisplayName()
    {
        string name;
        string desc;
        if (OZL_Names.Lookup(GetType(), name, desc) && name != "")
            return name;
        return super.GetDisplayName();
    }

    override bool DescriptionOverride(out string output)
    {
        string name;
        string desc;
        if (OZL_Names.Lookup(GetType(), name, desc) && desc != "")
        {
            output = desc;
            return true;
        }
        return false;
    }

    override void InitItemVariables()
    {
        super.InitItemVariables();
        can_this_be_combined = false;
        m_CanThisBeSplit     = false;
    }

    override bool CanBeCombined(EntityAI other_item, bool reservation_check = true, bool stack_max_limit = false)
    {
        return false;
    }

    override bool CanBeSplit()
    {
        return false;
    }

    override bool IsSplitable()
    {
        return false;
    }

    // Поток v1: вміст і чистота. Хеш не пишеться -- рахується при читанні.
    override void CF_OnStoreSave(CF_ModStorageMap storage)
    {
        super.CF_OnStoreSave(storage);
        auto ctx = storage["OpenZone_Research"];
        if (!ctx)
            return;
        ctx.Write(m_OZL_Content);
        ctx.Write(m_OZL_Purity);
    }

    override bool CF_OnStoreLoad(CF_ModStorageMap storage)
    {
        if (!super.CF_OnStoreLoad(storage))
            return false;
        auto ctx = storage["OpenZone_Research"];
        if (!ctx)
            return true;   // сейв старіший за мод: CF пише лише моди з даними

        if (!ctx.Read(m_OZL_Content) || !ctx.Read(m_OZL_Purity))
        {
            m_OZL_Content   = "";
            m_OZL_Purity    = 0;
            m_OZL_ContentId = 0;
            return false;
        }
        m_OZL_ContentId = OZL_Hash.Of(m_OZL_Content);
        return true;
    }

    override void EEInit()
    {
        super.EEInit();
        if (GetGame().IsDedicatedServer())
            SetSynchDirty();
    }
}
