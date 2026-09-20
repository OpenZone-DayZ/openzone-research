// Здача носія або даних на терміналі -- остання ланка ланцюжка: сировина ->
// зразок -> носій -> бали в пул фракції того, хто здає. Утримання три
// секунди, щоб дія читалась як передача, а не як клік.
//
// Вхід -- ContinuousInteractActionInput, а не типовий для тривалих дій: інакше
// здача сиділа б на іншій клавіші, ніж дерево, і термінал із носієм у руках
// був би мертвим (ваніль так само перевизначає вхід у десятках дій).

class OZL_ActionDepositCB : ActionContinuousBaseCB
{
    override void CreateActionComponent()
    {
        m_ActionData.m_ActionComponent = new CAContinuousTime(OZL_Terminal.DEPOSIT_SEC);
    }
}

class OZL_ActionDeposit : ActionContinuousBase
{
    void OZL_ActionDeposit()
    {
        m_CallbackClass = OZL_ActionDepositCB;
        m_CommandUID = DayZPlayerConstants.CMD_ACTIONFB_INTERACT;
        m_FullBody = true;
        m_StanceMask = DayZPlayerConstants.STANCEMASK_ERECT | DayZPlayerConstants.STANCEMASK_CROUCH;
        m_Text = "#STR_OZL_action_deposit";
    }

    override typename GetInputType()
    {
        return ContinuousInteractActionInput;
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
        return OZL_Terminal.IsDepositable(item);
    }

    override void OnFinishProgressServer(ActionData action_data)
    {
        if (!action_data || !action_data.m_Target)
            return;
        PlayerBase player = action_data.m_Player;
        string why;
        string line;
        bool ok = OZL_Terminal.Deposit(player, action_data.m_Target.GetObject(), action_data.m_MainItem, why, line);
        if (ok && line != "")
            player.MessageStatus(line);
        OZL_Actions.Tell(player, "research.deposit", ok, why);
    }
}
