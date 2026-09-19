// Стан фракції: пул балів, завершені вузли, проєкти в роботі -- один файл на
// власника, $profile:OpenZone\research\<id>.json.
//
// Не конфіг, а те, що змінює гра, тому власна підтека; читається тим самим
// завантажувачем ядра (бекап при записі, карантин битого файла), бо форма
// в нього та сама: версія, умовчання, перевірка. Про гравців тут нічого:
// бали належать фракції.
//
// Id -- ім'я файла, і перевіряється перед кожним зверненням до диска:
// непридатний id -- відмова, а не підміна на "default".

class OZL_Project
{
    string NodeId     = "";
    string StarterUid = "";
    int    EndSec     = 0;
}

class OZL_FactionState : OZ_ConfigBase
{
    ref array<ref OZL_KV>      Points;
    ref array<string>          CompletedNodes;
    ref array<ref OZL_Project> ActiveProjects;

    void OZL_FactionState()
    {
        Points         = new array<ref OZL_KV>();
        CompletedNodes = new array<string>();
        ActiveProjects = new array<ref OZL_Project>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        Points.Clear();
        CompletedNodes.Clear();
        ActiveProjects.Clear();
    }

    override void Validate(out int warnings)
    {
        warnings = 0;
        for (int i = Points.Count() - 1; i >= 0; i--)
        {
            if (!Points[i] || Points[i].Key == "" || Points[i].Value < 0)
            {
                Points.RemoveOrdered(i);
                warnings++;
            }
        }
        for (int p = ActiveProjects.Count() - 1; p >= 0; p--)
        {
            if (!ActiveProjects[p] || ActiveProjects[p].NodeId == "")
            {
                ActiveProjects.RemoveOrdered(p);
                warnings++;
            }
        }
    }

    int PointsOf(string type)
    {
        for (int i = 0; i < Points.Count(); i++)
        {
            if (Points[i] && Points[i].Key == type)
                return Points[i].Value;
        }
        return 0;
    }

    void SetPoints(string type, int value)
    {
        for (int i = 0; i < Points.Count(); i++)
        {
            if (Points[i] && Points[i].Key == type)
            {
                Points[i].Value = value;
                return;
            }
        }
        Points.Insert(new OZL_KV(type, value));
    }

    bool IsCompleted(string nodeId)
    {
        return CompletedNodes.Find(nodeId) > -1;
    }

    OZL_Project ProjectOf(string nodeId)
    {
        for (int i = 0; i < ActiveProjects.Count(); i++)
        {
            if (ActiveProjects[i] && ActiveProjects[i].NodeId == nodeId)
                return ActiveProjects[i];
        }
        return null;
    }
}

class OZL_State
{
    private static ref map<string, ref OZL_FactionState> s_Cache = new map<string, ref OZL_FactionState>();

    static string PathOf(string owner)
    {
        return OZL_Const.STATE_DIR + "\\" + owner + ".json";
    }

    // Лениво: файл читається при першому зверненні; фракція без файла
    // отримує порожній стан, і завантажувач одразу кладе його на диск.
    //
    // Null -- відмова: непридатний id або файл, якого не вдалося ні прочитати,
    // ні винести в карантин (завантажувач повертає false). У другому разі
    // нічого не кешуємо, щоб наступний запис не затер єдиний примірник того,
    // чого ми не зрозуміли; кожен виклик пробує знову, доки адмін не полагодить.
    static OZL_FactionState Get(string owner)
    {
        if (!OZL_Ids.IsPathSafe(owner))
        {
            OZL_Log.Warn("state: owner id '" + owner + "' is not safe as a file name, refused");
            return null;
        }

        OZL_FactionState cached;
        if (s_Cache.Find(owner, cached) && cached)
            return cached;

        OZL_FactionState loaded = new OZL_FactionState();
        if (!OZ_ConfigLoader<OZL_FactionState>.Load(PathOf(owner), "research state " + owner, loaded, true, false))
        {
            OZL_Log.Error("state: owner '" + owner + "' is unreadable and stays untouched on disk - research is off for it until an admin fixes the file");
            return null;
        }
        s_Cache.Set(owner, loaded);
        return loaded;
    }

    static void Save(string owner)
    {
        OZL_FactionState st;
        if (!s_Cache.Find(owner, st) || !st)
            return;
        OZ_ConfigLoader<OZL_FactionState>.Save(PathOf(owner), "research state " + owner, st, true);
    }

    // При старті: прочитати все, що лежить у теці, щоб проєкти офлайнових
    // фракцій завершувались по часу, а не при першому їхньому гравцеві.
    // Повертає, скільки файлів прочитано.
    static int Scan()
    {
        s_Cache.Clear();
        int n = 0;
        string name;
        FileAttr attr;
        FindFileHandle h = FindFile(OZL_Const.STATE_DIR + "\\*", name, attr, FindFileFlags.ALL);
        if (h == 0)
            return 0;

        bool more = true;
        while (more)
        {
            int len = name.Length();
            if (len > 5 && name.Substring(len - 5, 5) == ".json")
            {
                string owner = name.Substring(0, len - 5);
                if (OZL_Ids.IsPathSafe(owner) && Get(owner))
                    n++;
            }
            more = FindNextFile(h, name, attr);
        }
        CloseFindFile(h);
        return n;
    }

    // Сброс: бекап старого файла, порожній стан на диску й у кеші, подія --
    // станції фракції на неї зупиняються.
    static bool Reset(string owner, out string why)
    {
        why = "";
        if (!OZL_Ids.IsPathSafe(owner))
        {
            why = "STR_OZL_ERR_BAD_OWNER";
            return false;
        }

        OZL_FactionState fresh = new OZL_FactionState();
        fresh.LoadDefaults();
        OZ_ConfigLoader<OZL_FactionState>.Save(PathOf(owner), "research state " + owner, fresh, true);
        s_Cache.Set(owner, fresh);
        OZL_Log.Info("state: owner '" + owner + "' reset");
        OZL_Events.OnOwnerReset.Invoke(owner);
        return true;
    }

    static int Count()
    {
        return s_Cache.Count();
    }

    // Усі відомі власники -- для адмінського списку.
    static void Owners(out array<string> outIds)
    {
        outIds = new array<string>();
        for (int i = 0; i < s_Cache.Count(); i++)
            outIds.Insert(s_Cache.GetKey(i));
    }
}
