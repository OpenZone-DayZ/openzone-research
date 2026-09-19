// Три довідники предметів: OZ_Research_DataItems.json, OZ_Research_Modules.json,
// OZ_Research_SampleTypes.json.
//
// Заготовки даних (що дає здача) і типи зразків (як вони звуться) -- це
// імена й описи для класів, які приносить сам мод (OZL_Data_NN, OZL_Sample_NN):
// класи фіксовані збіркою, а зміст -- адміністратора. Модулі -- інструменти
// в слотах станції, що додають чистоти.

class OZL_DataReward
{
    string Type   = "";
    int    Amount = 0;

    OZL_DataReward Copy()
    {
        OZL_DataReward c = new OZL_DataReward();
        c.Type   = Type;
        c.Amount = Amount;
        return c;
    }
}

class OZL_DataDef
{
    string Id          = "";
    bool   Enabled     = true;
    string Name        = "";
    string Description = "";
    ref array<ref OZL_DataReward> Points;

    void OZL_DataDef()
    {
        Points = new array<ref OZL_DataReward>();
    }

    OZL_DataDef Copy()
    {
        OZL_DataDef c = new OZL_DataDef();
        c.Id          = Id;
        c.Enabled     = Enabled;
        c.Name        = Name;
        c.Description = Description;
        for (int i = 0; i < Points.Count(); i++)
        {
            if (Points[i])
                c.Points.Insert(Points[i].Copy());
        }
        return c;
    }
}

class OZL_DataItems : OZ_ConfigBase
{
    ref array<ref OZL_DataDef> Items;

    void OZL_DataItems()
    {
        Items = new array<ref OZL_DataDef>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        Items.Clear();
    }

    override void Validate(out int warnings)
    {
        warnings = 0;
        array<string> seen = new array<string>();
        for (int i = Items.Count() - 1; i >= 0; i--)
        {
            OZL_DataDef d = Items[i];
            string why = "";
            if (!d || d.Id == "")
                why = "an entry with no Id";
            else
            {
                string key = d.Id;
                key.ToLower();
                if (seen.Find(key) > -1)
                    why = "duplicate Id '" + d.Id + "'";
                else if (d.Name == "")
                    why = "'" + d.Id + "' has no Name";
                else
                    seen.Insert(key);
            }
            if (why != "")
            {
                OZL_Log.Warn("DataItems: " + why + ", dropped");
                Items.RemoveOrdered(i);
                warnings++;
            }
        }
    }

    // Проти гри й типів балів: невідомий клас -- запис геть; невідомий тип
    // балів у нагороді -- лише попередження, нагорода просто не нарахується.
    void Check(OZL_PointTypes pointTypes, out int problems)
    {
        problems = 0;
        for (int i = Items.Count() - 1; i >= 0; i--)
        {
            OZL_DataDef d = Items[i];
            if (!GetGame().ConfigIsExisting("CfgVehicles " + d.Id) || !GetGame().IsKindOf(d.Id, "OZL_Data_Base"))
            {
                OZL_Log.Warn("DataItems: '" + d.Id + "' is not a data item class of this mod, dropped");
                Items.RemoveOrdered(i);
                problems++;
                continue;
            }
            for (int p = 0; p < d.Points.Count(); p++)
            {
                OZL_DataReward r = d.Points[p];
                if (!r || r.Type == "")
                    continue;
                if (!pointTypes.Find(r.Type))
                {
                    OZL_Log.Warn("DataItems: '" + d.Id + "' rewards unknown point type '" + r.Type + "'");
                    problems++;
                }
                if (r.Amount < 0 || r.Amount > 1000000)
                {
                    OZL_Log.Warn("DataItems: '" + d.Id + "': Amount outside 0..1000000");
                    problems++;
                }
            }
        }
    }

    OZL_DataDef Find(string classname)
    {
        string want = classname;
        want.ToLower();
        for (int i = 0; i < Items.Count(); i++)
        {
            OZL_DataDef d = Items[i];
            if (!d || !d.Enabled)
                continue;
            string have = d.Id;
            have.ToLower();
            if (have == want)
                return d;
        }
        return null;
    }

    // Скільки ЧИННИХ нагород у заготовки: нуль означає, що здавати її нема
    // куди -- і термінал має це знати до того, як гравець потримає F.
    static int CountGrantable(OZL_DataDef def, OZL_PointTypes pointTypes)
    {
        if (!def)
            return 0;
        int n = 0;
        for (int i = 0; i < def.Points.Count(); i++)
        {
            OZL_DataReward r = def.Points[i];
            if (!r || r.Type == "" || r.Amount <= 0)
                continue;
            if (pointTypes && !pointTypes.Find(r.Type))
                continue;
            n++;
        }
        return n;
    }

    OZL_DataItems Copy()
    {
        OZL_DataItems c = new OZL_DataItems();
        c.Version = Version;
        for (int i = 0; i < Items.Count(); i++)
        {
            if (Items[i])
                c.Items.Insert(Items[i].Copy());
        }
        return c;
    }
}

class OZL_ModuleDef
{
    // Клас вкладення (MatchClass, суфікс "|1" -- рівно цей клас).
    string Classname   = "";
    // Додається до чистоти ОДИН раз, скільки б однакових не стояло.
    float  PurityBonus = 0;
    ref array<string> Devices;
    string Notes = "";

    void OZL_ModuleDef()
    {
        Devices = new array<string>();
    }

    OZL_ModuleDef Copy()
    {
        OZL_ModuleDef c = new OZL_ModuleDef();
        c.Classname   = Classname;
        c.PurityBonus = PurityBonus;
        c.Notes       = Notes;
        for (int i = 0; i < Devices.Count(); i++)
            c.Devices.Insert(Devices[i]);
        return c;
    }
}

class OZL_Modules : OZ_ConfigBase
{
    ref array<ref OZL_ModuleDef> Modules;

    void OZL_Modules()
    {
        Modules = new array<ref OZL_ModuleDef>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        Modules.Clear();
        Add("OZL_Tool_Optics",     0.2,  "OZL_Microscope",   "optics: the microscope only");
        Add("OZL_Tool_Centrifuge", 0.3,  "OZL_SampleFridge", "centrifuge: the sample fridge only");
        Add("OZL_Tool_Reagents",   0.25, "OZL_ChemBench",    "reagents: the chemistry bench only");
    }

    private void Add(string cls, float bonus, string device, string notes)
    {
        OZL_ModuleDef m = new OZL_ModuleDef();
        m.Classname   = cls;
        m.PurityBonus = bonus;
        m.Devices.Insert(device);
        m.Notes       = notes;
        Modules.Insert(m);
    }

    override void Validate(out int warnings)
    {
        warnings = 0;
        array<string> seen = new array<string>();
        for (int i = Modules.Count() - 1; i >= 0; i--)
        {
            OZL_ModuleDef m = Modules[i];
            string why = "";
            if (!m || m.Classname == "")
                why = "a module with no Classname";
            else if (seen.Find(m.Classname) > -1)
                why = "duplicate class '" + m.Classname + "'";
            else if (m.PurityBonus < 0 || m.PurityBonus > 2)
                why = "PurityBonus of '" + m.Classname + "' outside 0..2";
            if (why != "")
            {
                OZL_Log.Warn("Modules: " + why + ", dropped");
                Modules.RemoveOrdered(i);
                warnings++;
                continue;
            }
            seen.Insert(m.Classname);
        }
    }

    void Check(out int problems)
    {
        problems = 0;
        for (int i = Modules.Count() - 1; i >= 0; i--)
        {
            OZL_ModuleDef m = Modules[i];
            if (!OZL_Match.ClassExists(OZL_Match.StripExact(m.Classname)))
            {
                OZL_Log.Warn("Modules: class '" + m.Classname + "' is not in the game, dropped");
                Modules.RemoveOrdered(i);
                problems++;
                continue;
            }
            for (int d = 0; d < m.Devices.Count(); d++)
            {
                if (!OZL_Match.ClassExists(OZL_Match.StripExact(m.Devices[d])))
                {
                    OZL_Log.Warn("Modules: unknown device class '" + m.Devices[d] + "' in module '" + m.Classname + "'");
                    problems++;
                }
            }
        }
    }

    // Чи можна цей інструмент на цей прилад: модуль без списку приймають усі.
    bool AllowedOn(string attachmentClass, string deviceClass)
    {
        for (int i = 0; i < Modules.Count(); i++)
        {
            OZL_ModuleDef m = Modules[i];
            if (!m || !OZL_Match.MatchClass(attachmentClass, m.Classname))
                continue;
            if (m.Devices.Count() == 0)
                return true;
            return OZL_Match.InList(deviceClass, m.Devices);
        }
        return true;
    }

    // Сума бонусів чистоти від вкладень: кожен модуль рахується один раз.
    float SumBonus(array<string> attachmentClasses)
    {
        float total = 0;
        for (int i = 0; i < Modules.Count(); i++)
        {
            OZL_ModuleDef m = Modules[i];
            if (!m || m.Classname == "")
                continue;
            for (int a = 0; a < attachmentClasses.Count(); a++)
            {
                if (OZL_Match.MatchClass(attachmentClasses[a], m.Classname))
                {
                    total += m.PurityBonus;
                    break;
                }
            }
        }
        return total;
    }

    OZL_Modules Copy()
    {
        OZL_Modules c = new OZL_Modules();
        c.Version = Version;
        for (int i = 0; i < Modules.Count(); i++)
        {
            if (Modules[i])
                c.Modules.Insert(Modules[i].Copy());
        }
        return c;
    }
}

class OZL_SampleTypeDef
{
    string Id          = "";
    bool   Enabled     = true;
    string Name        = "";
    string Description = "";

    OZL_SampleTypeDef Copy()
    {
        OZL_SampleTypeDef c = new OZL_SampleTypeDef();
        c.Id          = Id;
        c.Enabled     = Enabled;
        c.Name        = Name;
        c.Description = Description;
        return c;
    }
}

class OZL_SampleTypes : OZ_ConfigBase
{
    ref array<ref OZL_SampleTypeDef> Items;

    void OZL_SampleTypes()
    {
        Items = new array<ref OZL_SampleTypeDef>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        Items.Clear();
    }

    override void Validate(out int warnings)
    {
        warnings = 0;
        array<string> seen = new array<string>();
        for (int i = Items.Count() - 1; i >= 0; i--)
        {
            OZL_SampleTypeDef d = Items[i];
            string why = "";
            if (!d || d.Id == "")
                why = "an entry with no Id";
            else
            {
                string key = d.Id;
                key.ToLower();
                if (seen.Find(key) > -1)
                    why = "duplicate Id '" + d.Id + "'";
                else if (d.Name == "")
                    why = "sample type '" + d.Id + "' has no Name";
                else
                    seen.Insert(key);
            }
            if (why != "")
            {
                OZL_Log.Warn("SampleTypes: " + why + ", dropped");
                Items.RemoveOrdered(i);
                warnings++;
            }
        }
    }

    void Check(out int problems)
    {
        problems = 0;
        for (int i = Items.Count() - 1; i >= 0; i--)
        {
            OZL_SampleTypeDef d = Items[i];
            if (!GetGame().ConfigIsExisting("CfgVehicles " + d.Id) || !GetGame().IsKindOf(d.Id, "OZL_Sample_Base"))
            {
                OZL_Log.Warn("SampleTypes: '" + d.Id + "' is not a sample class of this mod, dropped");
                Items.RemoveOrdered(i);
                problems++;
            }
        }
    }

    OZL_SampleTypeDef Find(string classname)
    {
        string want = classname;
        want.ToLower();
        for (int i = 0; i < Items.Count(); i++)
        {
            OZL_SampleTypeDef d = Items[i];
            if (!d || !d.Enabled)
                continue;
            string have = d.Id;
            have.ToLower();
            if (have == want)
                return d;
        }
        return null;
    }

    OZL_SampleTypes Copy()
    {
        OZL_SampleTypes c = new OZL_SampleTypes();
        c.Version = Version;
        for (int i = 0; i < Items.Count(); i++)
        {
            if (Items[i])
                c.Items.Insert(Items[i].Copy());
        }
        return c;
    }
}
