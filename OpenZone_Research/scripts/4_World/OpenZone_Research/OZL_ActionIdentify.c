// Коротке F на терміналі з носієм у руках: що саме в носії -- тип балів,
// тир, кількість. Єдине місце, де гравець це дізнається: клієнтові стан
// носія не синхронізується за задумом. Відповідь -- рядок статусу від
// сервера (у ньому імена з JSON адміна) і звістка ключем.

class OZL_ActionIdentify : ActionInteractBase
{
    void OZL_ActionIdentify()
    {
        m_CommandUID = DayZPlayerConstants.CMD_ACTIONMOD_INTERACTONCE;
        m_StanceMask = DayZPlayerConstants.STANCEMASK_ERECT | DayZPlayerConstants.STANCEMASK_CROUCH;
        m_Text = "#STR_OZL_action_identify";
    }

    override void CreateConditionComponents()
    {
        m_ConditionItem   = new CCINonRuined();
        m_ConditionTarget = new CCTObject(UAMaxDistances.DEFAULT);
    }

    override bool ActionCondition(PlayerBase player, ActionTarget target, ItemBase item)
    {
        if (!target || !OZL_Terminal.IsTerminalTarget(target.GetObject()))
            return false;
        return OZL_Terminal.IsCarrier(item) && !item.IsRuined();
    }

    override void OnExecuteServer(ActionData action_data)
    {
        if (!action_data || !action_data.m_Target)
            return;
        PlayerBase player = action_data.m_Player;
        string why;
        string line;
        bool ok = OZL_Terminal.Identify(player, action_data.m_Target.GetObject(), action_data.m_MainItem, why, line);
        if (ok && line != "")
            player.MessageStatus(line);
        OZL_Actions.Tell(player, "research.identify", ok, why);
    }
}
