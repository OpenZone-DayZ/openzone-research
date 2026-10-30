// Проба: проміжний предмет лінії, одна на лінію (config.cpp, ozlLine).
//
// Бали й чистоту несе рядок m_OZL_Payload (OZL_Payload); читає його прилад,
// а не гравець, тож на клієнт він не їде. ЖОДНОГО quantity в конфігу і
// заборона стеків і поділу: рушій зливає стек одного класу, не дивлячись на
// скриптові поля, і рядок другої проби зник би мовчки.

class OZL_Sample_Base : ItemBase
{
    protected string m_OZL_Payload;

    // Проба з чинним рядком: порожню аналізатор не бере.
    static bool HasPayload(EntityAI e)
    {
        OZL_Sample_Base s = OZL_Sample_Base.Cast(e);
        if (!s)
            return false;
        int points;
        int pct;
        return s.OZL_Read(points, pct);
    }

    void OZL_SetPayload(string payload)
    {
        m_OZL_Payload = payload;
        OZL_Log.Dbg("sample " + GetType() + ": payload '" + m_OZL_Payload + "'");
    }

    string OZL_GetPayload()
    {
        return m_OZL_Payload;
    }

    bool OZL_Read(out int points, out int purityPct)
    {
        return OZL_Payload.DecodeSample(m_OZL_Payload, points, purityPct);
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
        ctx.Write(m_OZL_Payload);
    }

    override bool CF_OnStoreLoad(CF_ModStorageMap storage)
    {
        if (!super.CF_OnStoreLoad(storage))
            return false;
        auto ctx = storage["OpenZone_Research"];
        if (!ctx)
            return true;   // сейв старіший за мод: CF пише лише моди з даними
        if (!ctx.Read(m_OZL_Payload))
        {
            m_OZL_Payload = "";
            return false;
        }
        return true;
    }
}
