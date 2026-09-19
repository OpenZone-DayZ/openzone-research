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
        if (OZ_ClientState.Ready())
            OZL_ClientNames.Apply();
    }

    void OZL_Sync(OZ_SyncPayload p)
    {
        OZL_ClientNames.Apply();
    }

    override void OnMissionFinish()
    {
        // Дзеркало підписки з OnInit: інвокер ядра статичний і переживе місію.
        OZ_ClientState.SyncWatch().Remove(OZL_Sync);
        super.OnMissionFinish();
    }
}
