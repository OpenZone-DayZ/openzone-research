// Власники: OZ_Research_Owners.json -- що фракція ядра має у грі.
//
// Id -- слаг фракції з реєстру ядра (Factions.json мода фракцій). Імені,
// кольору й нашивок тут немає: ім'я та колір знає ядро (OZ_Identity), а
// нашивка перестала бути ознакою фракції -- нею стала сама фракція.
//
// ПРАВИЛО СПИСКІВ, успадковане від ZP: список фракції перемагає; якщо хоч
// одна фракція оголосила список, фракція без списку не отримує НІЧОГО; якщо
// списків немає ні в кого, поділу немає взагалі -- усім усе.

class OZL_OwnerDef
{
    string Id = "";
    ref array<string> TerminalClasses;
    ref array<string> DeviceClasses;
    string TreeBackground = "";

    void OZL_OwnerDef()
    {
        TerminalClasses = new array<string>();
        DeviceClasses   = new array<string>();
    }

    OZL_OwnerDef Copy()
    {
        OZL_OwnerDef c = new OZL_OwnerDef();
        c.Id             = Id;
        c.TreeBackground = TreeBackground;
        int i;
        for (i = 0; i < TerminalClasses.Count(); i++)
            c.TerminalClasses.Insert(TerminalClasses[i]);
        for (i = 0; i < DeviceClasses.Count(); i++)
            c.DeviceClasses.Insert(DeviceClasses[i]);
        return c;
    }
}

class OZL_Owners : OZ_ConfigBase
{
    ref array<ref OZL_OwnerDef> Owners;

    void OZL_Owners()
    {
        Owners = new array<ref OZL_OwnerDef>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    // Порожньо навмисно: перелік фракцій належить ядру, а списки приладів --
    // стартовому пакету або адмінові. Порожній файл означає «поділу немає».
    override void LoadDefaults()
    {
        super.LoadDefaults();
        Owners.Clear();
    }

    override void Validate(out int warnings)
    {
        warnings = 0;

        array<string> seen = new array<string>();
        for (int i = Owners.Count() - 1; i >= 0; i--)
        {
            OZL_OwnerDef o = Owners[i];
            string why = "";
            if (!o || o.Id == "")
                why = "an owner with no Id";
            else if (!OZL_Ids.IsPathSafe(o.Id))
                why = "Id '" + o.Id + "' is not safe as a file name";
            else if (seen.Find(o.Id) > -1)
                why = "duplicate Id '" + o.Id + "'";

            if (why != "")
            {
                OZL_Log.Warn("Owners: " + why + ", dropped");
                Owners.RemoveOrdered(i);
                warnings++;
                continue;
            }
            seen.Insert(o.Id);

            int j;
            for (j = o.TerminalClasses.Count() - 1; j >= 0; j--)
            {
                if (o.TerminalClasses[j] == "")
                {
                    o.TerminalClasses.RemoveOrdered(j);
                    warnings++;
                }
            }
            for (j = o.DeviceClasses.Count() - 1; j >= 0; j--)
            {
                if (o.DeviceClasses[j] == "")
                {
                    o.DeviceClasses.RemoveOrdered(j);
                    warnings++;
                }
            }
        }

        // Спільні прилади й термінали -- не помилка, а те, про що адмін має
        // знати: дві фракції з одним терміналом бачать дерева одна одної.
        // Це попередження не рахується як виправлення файла.
        WarnShared();
    }

    private void WarnShared()
    {
        for (int i = 0; i < Owners.Count(); i++)
        {
            OZL_OwnerDef a = Owners[i];
            for (int j = i + 1; j < Owners.Count(); j++)
            {
                OZL_OwnerDef b = Owners[j];
                int k;
                for (k = 0; k < a.TerminalClasses.Count(); k++)
                {
                    if (b.TerminalClasses.Find(a.TerminalClasses[k]) > -1)
                        OZL_Log.Warn("Owners: terminal '" + a.TerminalClasses[k] + "' belongs to both '" + a.Id + "' and '" + b.Id + "' - they will see each other's trees");
                }
                for (k = 0; k < a.DeviceClasses.Count(); k++)
                {
                    if (b.DeviceClasses.Find(a.DeviceClasses[k]) > -1)
                        OZL_Log.Warn("Owners: device '" + a.DeviceClasses[k] + "' belongs to both '" + a.Id + "' and '" + b.Id + "' - they will share it");
                }
            }
        }

        bool anyT = AnyDeclaresTerminals();
        bool anyD = AnyDeclaresDevices();
        for (int m = 0; m < Owners.Count(); m++)
        {
            OZL_OwnerDef o = Owners[m];
            if (anyT && o.TerminalClasses.Count() == 0)
                OZL_Log.Warn("Owners: '" + o.Id + "' owns no terminals while others do - its players will open no tree");
            if (anyD && o.DeviceClasses.Count() == 0)
                OZL_Log.Warn("Owners: '" + o.Id + "' owns no devices while others do - its players will run no station");
        }
    }

    OZL_OwnerDef Find(string id)
    {
        for (int i = 0; i < Owners.Count(); i++)
        {
            if (Owners[i] && Owners[i].Id == id)
                return Owners[i];
        }
        return null;
    }

    bool AnyDeclaresTerminals()
    {
        for (int i = 0; i < Owners.Count(); i++)
        {
            if (Owners[i] && Owners[i].TerminalClasses.Count() > 0)
                return true;
        }
        return false;
    }

    bool AnyDeclaresDevices()
    {
        for (int i = 0; i < Owners.Count(); i++)
        {
            if (Owners[i] && Owners[i].DeviceClasses.Count() > 0)
                return true;
        }
        return false;
    }

    // Чи цей термінал -- цього власника. Списків немає ні в кого -- так;
    // є в когось, а в нього немає -- ні; є в нього -- за списком.
    bool IsTerminalFor(string owner, string classname)
    {
        if (!AnyDeclaresTerminals())
            return true;
        OZL_OwnerDef o = Find(owner);
        if (!o)
            return false;
        return OZL_Match.InList(classname, o.TerminalClasses);
    }

    bool IsDeviceFor(string owner, string classname)
    {
        if (!AnyDeclaresDevices())
            return true;
        OZL_OwnerDef o = Find(owner);
        if (!o)
            return false;
        return OZL_Match.InList(classname, o.DeviceClasses);
    }

    string BackgroundOf(string owner)
    {
        OZL_OwnerDef o = Find(owner);
        if (o)
            return o.TreeBackground;
        return "";
    }

    OZL_Owners Copy()
    {
        OZL_Owners c = new OZL_Owners();
        c.Version = Version;
        for (int i = 0; i < Owners.Count(); i++)
        {
            if (Owners[i])
                c.Owners.Insert(Owners[i].Copy());
        }
        return c;
    }
}
