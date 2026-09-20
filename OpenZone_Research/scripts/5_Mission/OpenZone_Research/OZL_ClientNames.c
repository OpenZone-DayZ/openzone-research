// Клієнтська дорога наповнення довідника імен: з пакета синхронізації ядра.
//
// У 5_Mission, бо пакет живе в OZ_ClientState (5_Mission ядра). Кличеться на
// кожен пакет, перший і повторний: після правки конфігу сервер шле пакет
// знову, і назви на екрані інвентаря міняються без перезаходу.

class OZL_ClientNames
{
    static void Apply()
    {
        OZL_Names.Clear();
        Take(OZL_Names.SYNC_SAMPLES, OZL_Names.SYNC_SAMPLE);
        Take(OZL_Names.SYNC_DATA_N, OZL_Names.SYNC_DATA);
        OZL_Log.Dbg("names: " + OZL_Names.Count().ToString() + " item name(s) from the sync packet");

        OZL_ClientConfig.Clear();
        int chunks = OZ_ClientState.Extra(OZL_ClientConfig.SYNC_TERMINALS_N, "0").ToInt();
        for (int c = 0; c < chunks; c++)
            OZL_ClientConfig.AddTerminals(OZ_ClientState.Extra(OZL_ClientConfig.SYNC_TERMINALS + c.ToString(), ""));
        OZL_Log.Dbg("terminals: " + OZL_ClientConfig.TerminalCount().ToString() + " class(es) from the sync packet");
    }

    private static void Take(string countKey, string prefix)
    {
        int total = OZ_ClientState.Extra(countKey, "0").ToInt();
        for (int i = 0; i < total; i++)
        {
            string json = OZ_ClientState.Extra(prefix + i.ToString(), "");
            if (json == "")
                continue;

            // Корінь створює скрипт; поля -- рядки, копіювати нема чого, Set
            // переписує їх у власний запис.
            OZL_NameEntry e = new OZL_NameEntry();
            string err;
            if (!JsonFileLoader<OZL_NameEntry>.LoadData(json, e, err))
            {
                OZL_Log.Warn("names: entry " + i.ToString() + " unreadable: " + err);
                continue;
            }
            OZL_Names.Set(e.Id, e.Name, e.Desc);
        }
    }
}
