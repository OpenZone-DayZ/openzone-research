// Носій балів: результат аналізу, один на лінію (config.cpp, ozlLine). Тип
// балів -- лінія класу, кількість -- у рядку m_OZL_Payload (OZL_Payload), який
// читає термінал. Нічого не синхронізується; стеки й поділ заборонені з тієї ж
// причини, що в проби.

class OZL_Carrier_Base : ItemBase
{
    protected string m_OZL_Payload;

    void OZL_SetPayload(string payload)
    {
        m_OZL_Payload = payload;
        OZL_Log.Dbg("carrier " + GetType() + ": payload '" + m_OZL_Payload + "'");
    }

    string OZL_GetPayload()
    {
        return m_OZL_Payload;
    }

    bool OZL_Read(out int points)
    {
        return OZL_Payload.DecodeCarrier(m_OZL_Payload, points);
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
            return true;
        if (!ctx.Read(m_OZL_Payload))
        {
            m_OZL_Payload = "";
            return false;
        }
        return true;
    }
}
