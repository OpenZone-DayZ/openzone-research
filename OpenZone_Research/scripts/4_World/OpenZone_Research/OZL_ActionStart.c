// Миттєва дія «запустити станцію» на приладі у стані «вільна».
//
// CCINone, не CCIDummy: у CCIDummy Can() = (item != null), і підказка не
// з'являлась би з порожніми руками. Умова на обох боках -- лише ціль і її
// netsync-стан; власника, правило й карго судить сервер, а відповідь їде
// звісткою ядра ключем рядка (успіх і відмова однаково).

class OZL_ActionStart : ActionInteractBase
{
    void OZL_ActionStart()
    {
        m_CommandUID = DayZPlayerConstants.CMD_ACTIONMOD_INTERACTONCE;
        m_Text = "#STR_OZL_action_start";
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
        if (!st || st.IsDamageDestroyed())
            return false;
        return st.OZL_GetState() == OZL_Station.STATE_IDLE;
    }

    override void OnExecuteServer(ActionData action_data)
    {
        OZL_Station st = OZL_Station.Cast(action_data.m_Target.GetObject());
        if (!st)
            return;
        string why;
        bool ok = st.OZL_Start(action_data.m_Player, why);
        OZL_Actions.Tell(action_data.m_Player, "research.start", ok, why);
    }
}
