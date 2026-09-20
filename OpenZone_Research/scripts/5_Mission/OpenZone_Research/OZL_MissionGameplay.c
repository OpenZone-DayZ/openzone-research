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
        if (OZ_ClientState.Ready())
            OZL_ClientNames.Apply();
    }

    void OZL_Notice(string op, bool ok, string why)
    {
        if (op.IndexOf("research.") != 0)
            return;
        NotificationSystem.AddNotificationExtended(4, "#STR_OZL_modname", OZ_Notice.Text(), "");
    }
    void OZL_Sync(OZ_SyncPayload p)
    {
        OZL_ClientNames.Apply();
    }

    override void OnMissionFinish()
    {
        // Дзеркало підписки з OnInit: інвокер ядра статичний і переживе місію.
        OZ_ClientState.SyncWatch().Remove(OZL_Sync);
        OZ_Notice.OnAnswer.Remove(OZL_Notice);
        super.OnMissionFinish();
    }
}
