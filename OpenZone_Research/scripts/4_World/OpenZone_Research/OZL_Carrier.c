// Носій балів: один предмет на супертип, значення сховане до опознання.
//
// Видно лише супертип (наукові, бойові, сталкерські -- клас і колір), а тип
// балів і кількість -- рядок стану «<тип>:<n>», який читає термінал. Нічого не
// синхронізується: клієнтові нема що знати до здачі. Стеки й поділ заборонені
// з тієї ж причини, що в зразка.

class OZL_Carrier_Base : ItemBase
{
    protected string m_OZL_State;

    static string StateOf(EntityAI e)
    {
        OZL_Carrier_Base c = OZL_Carrier_Base.Cast(e);
        if (!c)
            return "";
        return c.OZL_State();
    }

    static void ApplyState(EntityAI created, string state)
    {
        if (state == "")
            return;
        OZL_Carrier_Base c = OZL_Carrier_Base.Cast(created);
        if (!c)
            return;
        c.OZL_SetState(state);
    }

    void OZL_SetState(string state)
    {
        m_OZL_State = state;
        OZL_Log.Dbg("carrier " + GetType() + ": state='" + m_OZL_State + "'");
    }

    string OZL_State()
    {
        return m_OZL_State;
    }

    // Супертип -- за класом, не за станом: він видимий, стан -- ні.
    static string SupertypeOf(string classname)
    {
        if (GetGame().IsKindOf(classname, "OZL_Carrier_Science"))
            return "science";
        if (GetGame().IsKindOf(classname, "OZL_Carrier_Combat"))
            return "combat";
        if (GetGame().IsKindOf(classname, "OZL_Carrier_Stalker"))
            return "stalker";
        return "";
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

    override void CF_OnStoreSave(CF_ModStorageMap storage)
    {
        super.CF_OnStoreSave(storage);
        auto ctx = storage["OpenZone_Research"];
        if (!ctx)
            return;
        ctx.Write(m_OZL_State);
    }

    override bool CF_OnStoreLoad(CF_ModStorageMap storage)
    {
        if (!super.CF_OnStoreLoad(storage))
            return false;
        auto ctx = storage["OpenZone_Research"];
        if (!ctx)
            return true;
        if (!ctx.Read(m_OZL_State))
        {
            m_OZL_State = "";
            return false;
        }
        return true;
    }
}
