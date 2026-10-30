// Клієнтська дорога списку терміналів: з пакета синхронізації ядра.
//
// У 5_Mission, бо пакет живе в OZ_ClientState (5_Mission ядра). Кличеться на
// кожен пакет, перший і повторний: після правки власників сервер шле пакет
// знову, і дії термінала на клієнті бачать новий список без перезаходу.

class OZL_ClientTerminals
{
    static void Apply()
    {
        OZL_ClientConfig.Clear();
        int chunks = OZ_ClientState.Extra(OZL_ClientConfig.SYNC_TERMINALS_N, "0").ToInt();
        for (int c = 0; c < chunks; c++)
            OZL_ClientConfig.AddTerminals(OZ_ClientState.Extra(OZL_ClientConfig.SYNC_TERMINALS + c.ToString(), ""));
        OZL_Log.Dbg("terminals: " + OZL_ClientConfig.TerminalCount().ToString() + " class(es) from the sync packet");
    }
}
