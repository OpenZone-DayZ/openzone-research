// Клієнтська точка входу мода досліджень.
//
// Слухає пакет синхронізації ядра: у ньому їдуть імена предметів з JSON
// адміністратора (OZL_Names). Меню дерева й відповіді служби -- з планом T9.
//
// На виділеному сервері MissionGameplay не створюється взагалі (там
// MissionServer), тож цей код туди не потрапляє.

modded class MissionGameplay
{
    override void OnInit()
    {
        super.OnInit();

        // На кожен пакет, перший і повторний, і одразу, якщо пакет випередив
        // місію. Той самий візерунок, що в КПК і рації.
        OZ_ClientState.SyncWatch().Insert(OZL_Sync);

        // Відповіді сервера на дії мода (старт, забір, здача...): ключ рядка
        // їде звісткою ядра, показуємо її сповіщенням -- гравець стоїть у
        // світі, а не в меню. Той самий візерунок, що в КПК.
        OZ_Notice.OnAnswer.Insert(OZL_Notice);

        // Дерево: сервер каже «покажи» після дії на терміналі, відповіді
        // служби йдуть у відкрите меню.
        OZ_Show.OnShow.Insert(OZL_Show);
        OZ_ClientState.ServiceWatch().Insert(OZL_SvcRes);
        if (OZ_ClientState.Ready())
            OZL_ClientNames.Apply();
    }

    void OZL_Notice(string op, bool ok, string why)
    {
        if (op.IndexOf("research.") != 0)
            return;
        NotificationSystem.AddNotificationExtended(4, "#STR_OZL_modname", OZ_Notice.Text(), "");
    }
    void OZL_Show(string what)
    {
        if (what != OZL_Const.SHOW_TREE)
            return;
        // Не в цьому кадрі: стек меню в мить дії ще зайнятий (той самий
        // прийом, що в ZP і в КПК).
        GetGame().GetCallQueue(CALL_CATEGORY_GUI).CallLater(OZL_OpenTree, 100, false);
    }

    void OZL_OpenTree()
    {
        UIManager ui = GetGame().GetUIManager();
        if (ui.FindMenu(OZL_Const.MENU_TREE))
            return;
        ui.EnterScriptedMenu(OZL_Const.MENU_TREE, null);
    }

    void OZL_SvcRes(string serviceId, string op, bool ok, string json, string error)
    {
#ifndef NO_GUI
        OZL_TreeMenu.OnService(serviceId, op, ok, json, error);
#endif
    }
    void OZL_Sync(OZ_SyncPayload p)
    {
        OZL_ClientNames.Apply();
    }

    override UIScriptedMenu CreateScriptedMenu(int id)
    {
        // super ПЕРШИЙ і вихід одразу, якщо він щось віддав: так живуть
        // поруч інші моди, що чіпали той самий клас.
        UIScriptedMenu menu = super.CreateScriptedMenu(id);
        if (menu)
            return menu;
#ifndef NO_GUI
        if (id == OZL_Const.MENU_TREE)
        {
            menu = new OZL_TreeMenu();
            menu.SetID(id);
            return menu;
        }
#endif
        return null;
    }
    override void OnMissionFinish()
    {
        // Дзеркало підписки з OnInit: інвокер ядра статичний і переживе місію.
        OZ_ClientState.SyncWatch().Remove(OZL_Sync);
        OZ_Notice.OnAnswer.Remove(OZL_Notice);
        OZ_Show.OnShow.Remove(OZL_Show);
        OZ_ClientState.ServiceWatch().Remove(OZL_SvcRes);
        GetGame().GetCallQueue(CALL_CATEGORY_GUI).Remove(OZL_OpenTree);
        super.OnMissionFinish();
    }
}
