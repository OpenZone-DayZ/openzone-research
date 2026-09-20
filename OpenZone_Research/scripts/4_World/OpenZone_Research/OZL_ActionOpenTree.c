// Миттєва дія «відкрити дерево» на терміналі з порожніми руками.
//
// Із носієм чи даними в руках та сама клавіша означає здачу (утримання) або
// опознання (коротке), тож тут -- заперечення тієї умови. Сервер перевіряє
// належність термінала й шле клієнтові OZ_Show: клієнтська половина
// відкриває меню дерева й сама запитує службу.

class OZL_ActionOpenTree : ActionInteractBase
{
    void OZL_ActionOpenTree()
    {
        m_CommandUID = DayZPlayerConstants.CMD_ACTIONMOD_INTERACTONCE;
        m_Text = "#STR_OZL_action_tree";
    }

    override void CreateConditionComponents()
    {
        m_ConditionItem   = new CCINone();
        m_ConditionTarget = new CCTObject(UAMaxDistances.DEFAULT);
    }

    override bool ActionCondition(PlayerBase player, ActionTarget target, ItemBase item)
    {
        if (!target || !OZL_Terminal.IsTerminalTarget(target.GetObject()))
            return false;
        return !OZL_Terminal.IsDepositable(item);
    }

    // Ціль у цю мить може бути порожньою: виконання йде з події анімації, не
    // з того кадру, де діяла умова. Тоді судимо без неї: Can() на сервері
    // термінал уже звірив.
    override void OnExecuteServer(ActionData action_data)
    {
        if (!action_data)
            return;
        PlayerBase player = action_data.m_Player;
        if (!player || !player.GetIdentity())
            return;
        if (action_data.m_Target)
        {
            Object obj = action_data.m_Target.GetObject();
            string why;
            if (obj && !OZL_Terminal.MayOpenTree(player, obj, why))
            {
                OZL_Actions.Tell(player, "research.tree", false, why);
                return;
            }
        }
        OZL_Log.Dbg("show " + OZL_Const.SHOW_TREE + " to " + player.GetIdentity().GetPlainId());
        OZ_Rpc.Show(player.GetIdentity(), OZL_Const.SHOW_TREE);
    }
}
