// Реєстрація дій мода й відповідь гравцеві.
//
// Реєстрація в ActionConstructor обов'язкова: без неї AddAction кидає
// стек-трейс «Function AddAction», бо дія не відома менеджерові. Відповідь --
// звістка ядра (OZ_Rpc.Notice) ключем рядка; клієнтська половина мода
// показує її сповіщенням. Гравець без identity (бот стенда) відповіді не
// отримує, дія від цього не ламається.

class OZL_Actions
{
    static void Tell(PlayerBase player, string op, bool ok, string why)
    {
        if (!player || !player.GetIdentity())
            return;
        OZ_Rpc.Notice(player.GetIdentity(), op, ok, why);
    }
}

modded class ActionConstructor
{
    override void RegisterActions(TTypenameArray actions)
    {
        super.RegisterActions(actions);
        actions.Insert(OZL_ActionStart);
        actions.Insert(OZL_ActionCollect);
        actions.Insert(OZL_ActionDeposit);
        actions.Insert(OZL_ActionIdentify);
        actions.Insert(OZL_ActionOpenTree);
    }
}

modded class PlayerBase
{
    override void SetActions(out TInputActionMap InputActionMap)
    {
        super.SetActions(InputActionMap);
        AddAction(OZL_ActionStart, InputActionMap);
        AddAction(OZL_ActionCollect, InputActionMap);
        AddAction(OZL_ActionDeposit, InputActionMap);
        AddAction(OZL_ActionIdentify, InputActionMap);
        AddAction(OZL_ActionOpenTree, InputActionMap);
    }
}
