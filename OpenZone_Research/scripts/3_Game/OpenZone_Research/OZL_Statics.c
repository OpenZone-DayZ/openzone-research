// Статичні станції: OZ_Research_Statics.json (де стоять) і
// OZ_Research_Statics_State.json (що вже поставлено).
//
// Два файли, а не один: перелік -- конфіг адміністратора, а стан -- те, що
// пише гра. Стан потрібен, бо сховище сутностей грузиться ПІСЛЯ
// OnMissionStart, і живий реєстр у ту мить порожній: без файла кожен старт
// ставив би другу копію.

class OZL_StaticEntry
{
    string Id    = "";
    // ClassName, а не Class: `Class` -- ім'я типу рушія, поле з ним не компілюється.
    string ClassName = "";
    ref array<float> Pos;
    float  Yaw   = 0;
    string Note  = "";

    void OZL_StaticEntry()
    {
        Pos = new array<float>();
    }

    OZL_StaticEntry Copy()
    {
        OZL_StaticEntry c = new OZL_StaticEntry();
        c.Id    = Id;
        c.ClassName = ClassName;
        c.Yaw   = Yaw;
        c.Note  = Note;
        for (int i = 0; i < Pos.Count(); i++)
            c.Pos.Insert(Pos[i]);
        return c;
    }
}

class OZL_StaticsConfig : OZ_ConfigBase
{
    ref array<ref OZL_StaticEntry> Entries;

    void OZL_StaticsConfig()
    {
        Entries = new array<ref OZL_StaticEntry>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        Entries.Clear();
    }

    override void Validate(out int warnings)
    {
        warnings = 0;
        array<string> seen = new array<string>();
        for (int i = Entries.Count() - 1; i >= 0; i--)
        {
            OZL_StaticEntry e = Entries[i];
            string why = "";
            if (!e || e.Id == "")
                why = "an entry with no Id";
            else if (seen.Find(e.Id) > -1)
                why = "duplicate Id '" + e.Id + "'";
            else if (e.ClassName == "")
                why = "'" + e.Id + "' has no ClassName";
            else if (e.Pos.Count() != 3)
                why = "'" + e.Id + "' needs Pos of three numbers";
            if (why != "")
            {
                OZL_Log.Warn("Statics: " + why + ", dropped");
                Entries.RemoveOrdered(i);
                warnings++;
                continue;
            }
            seen.Insert(e.Id);
        }
    }

    OZL_StaticsConfig Copy()
    {
        OZL_StaticsConfig c = new OZL_StaticsConfig();
        c.Version = Version;
        for (int i = 0; i < Entries.Count(); i++)
        {
            if (Entries[i])
                c.Entries.Insert(Entries[i].Copy());
        }
        return c;
    }
}

class OZL_StaticsState : OZ_ConfigBase
{
    ref array<string> SpawnedIds;

    void OZL_StaticsState()
    {
        SpawnedIds = new array<string>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        SpawnedIds.Clear();
    }

    OZL_StaticsState Copy()
    {
        OZL_StaticsState c = new OZL_StaticsState();
        c.Version = Version;
        for (int i = 0; i < SpawnedIds.Count(); i++)
            c.SpawnedIds.Insert(SpawnedIds[i]);
        return c;
    }
}
