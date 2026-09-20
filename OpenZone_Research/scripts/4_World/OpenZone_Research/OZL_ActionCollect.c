// Миттєва дія «забрати результат» на приладі, що стоїть із незакладеним
// виходом. По результат приходять із порожніми руками -- тому CCINone.

class OZL_ActionCollect : ActionInteractBase
{
    void OZL_ActionCollect()
    {
        m_CommandUID = DayZPlayerConstants.CMD_ACTIONMOD_INTERACTONCE;
        m_Text = "#STR_OZL_action_collect";
    }

    override void CreateConditionComponents()
    {
        m_ConditionItem   = new CCINone();
        m_ConditionTarget = new CCTObject(UAMaxDistances.DEFAULT);
    }

    override bool ActionCondition(PlayerBase player, ActionTarget target, ItemBase item)
    {
        if (!target)
            return false;
        OZL_Station st = OZL_Station.Cast(target.GetObject());
        if (!st)
            return false;
        // Стан у netsync: клієнт гейтить підказку тим самим полем, що й
        // сервер, конфіг для цього не потрібен.
        return st.OZL_GetState() == OZL_Station.STATE_DONE;
    }

    override void OnExecuteServer(ActionData action_data)
    {
        OZL_Station st = OZL_Station.Cast(action_data.m_Target.GetObject());
        if (!st)
            return;
        string why;
        bool ok = st.OZL_Collect(action_data.m_Player, why);
        OZL_Actions.Tell(action_data.m_Player, "research.collect", ok, why);
    }
}
