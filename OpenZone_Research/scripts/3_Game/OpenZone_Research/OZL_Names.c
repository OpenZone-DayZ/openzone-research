// Імена й описи предметів з JSON -- на обох боках, у 3_Game, бо їх питають
// предмети (4_World) на сервері й на клієнті однаково.
//
// Клас зразка чи заготовки фіксований збіркою (OZL_Sample_07), а те, ЧИМ він
// є на цьому сервері, каже адміністратор у OZ_Research_SampleTypes.json і
// OZ_Research_DataItems.json. Сервер кладе імена сюди при кожному читанні
// конфігів (OZL_Config); клієнтові конфіги не їдуть -- йому їдуть лише
// імена, додатками до пакета синхронізації ядра, і він кладе їх сюди ж
// (OZL_ClientNames у 5_Mission). Один довідник, дві дороги наповнення.
//
// Ключі додатків: research.samples = N, research.sample.<i> = JSON
// OZL_NameEntry; те саме для data. По одному додатку на предмет: одне
// строкове значення JSON рушій ріже на 1023 байтах, а список імен у цю межу
// не вміщається.

class OZL_NameEntry
{
    string Id   = "";
    string Name = "";
    string Desc = "";
}

class OZL_Names
{
    static const string SYNC_SAMPLES = "research.samples";
    static const string SYNC_SAMPLE  = "research.sample.";
    static const string SYNC_DATA_N  = "research.datas";
    static const string SYNC_DATA    = "research.data.";

    // Ключ -- клас у нижньому регістрі: config-класи гра порівнює без регістру.
    private static ref map<string, ref OZL_NameEntry> s_Names = new map<string, ref OZL_NameEntry>();

    static void Clear()
    {
        s_Names.Clear();
    }

    static void Set(string id, string name, string desc)
    {
        if (id == "")
            return;
        OZL_NameEntry e = new OZL_NameEntry();
        e.Id   = id;
        e.Name = name;
        e.Desc = desc;
        string key = id;
        key.ToLower();
        s_Names.Set(key, e);
    }

    static int Count()
    {
        return s_Names.Count();
    }

    // Порожньо, коли адмін цей клас не описав: тоді предмет показує ім'я з
    // config.cpp, і це видно як «(not configured)».
    static bool Lookup(string classname, out string name, out string desc)
    {
        name = "";
        desc = "";
        if (classname == "")
            return false;

        string key = classname;
        key.ToLower();
        OZL_NameEntry e;
        if (!s_Names.Find(key, e) || !e)
            return false;
        name = e.Name;
        desc = e.Desc;
        return true;
    }

    // Один запис -- один додаток пакета. Кличе сервер (OZL_Config.FillNames).
    static void PutEntry(OZ_SyncPayload p, string key, string id, string name, string desc)
    {
        OZL_NameEntry e = new OZL_NameEntry();
        e.Id   = id;
        e.Name = name;
        e.Desc = desc;
        string json;
        string err;
        if (!JsonFileLoader<OZL_NameEntry>.MakeData(e, json, err, false))
        {
            OZL_Log.Warn("names: cannot serialise " + id + ": " + err);
            return;
        }
        OZ_SyncExtras.Put(p, key, json);
    }
}
