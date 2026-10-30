// Типи балів: OZ_Research_PointTypes.json.
//
// Тип балів -- це лінія (біологія, хабар, балістика...): його Id збігається з
// ozlLine проб, носіїв і станків у config.cpp. Тирів і родів немає: рідкість
// сировини -- це число балів, яке пакувальник пише в пробу.

class OZL_PointType
{
    string Id        = "";
    string Name      = "";
    string Icon      = "";
    string Color     = "";
    int    SortOrder = 0;

    OZL_PointType Copy()
    {
        OZL_PointType c = new OZL_PointType();
        c.Id        = Id;
        c.Name      = Name;
        c.Icon      = Icon;
        c.Color     = Color;
        c.SortOrder = SortOrder;
        return c;
    }
}

class OZL_PointTypes : OZ_ConfigBase
{
    ref array<ref OZL_PointType> PointTypes;

    void OZL_PointTypes()
    {
        PointTypes = new array<ref OZL_PointType>();
    }

    override int LatestVersion()
    {
        return 2;
    }

    // Версія 1 мала тири й роди: переносити нічого, файл іде в карантин ядра.
    override bool Migrate(int from)
    {
        return false;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        PointTypes.Clear();
        Add("bio",         "Біологія",    "#7CB342", 1);
        Add("anomaly",     "Аномалії",    "#AB47BC", 2);
        Add("electronics", "Електроніка", "#29B6F6", 3);
        Add("khabar",      "Хабар",       "#FFB300", 4);
        Add("trails",      "Стежки",      "#26A69A", 5);
        Add("ballistics",  "Балістика",   "#C62828", 6);
        Add("protection",  "Захист",      "#78909C", 7);
    }

    private void Add(string id, string name, string color, int order)
    {
        OZL_PointType p = new OZL_PointType();
        p.Id        = id;
        p.Name      = name;
        p.Color     = color;
        p.SortOrder = order;
        PointTypes.Insert(p);
    }

    override void Validate(out int warnings)
    {
        warnings = 0;
        array<string> seen = new array<string>();
        for (int i = PointTypes.Count() - 1; i >= 0; i--)
        {
            OZL_PointType pt = PointTypes[i];
            string why = "";
            if (!pt || pt.Id == "")
                why = "a point type with no Id";
            else if (seen.Find(pt.Id) > -1)
                why = "duplicate Id '" + pt.Id + "'";
            else if (pt.Name == "")
                why = "type '" + pt.Id + "' has no Name";

            if (why != "")
            {
                OZL_Log.Warn("PointTypes: " + why + ", dropped");
                PointTypes.RemoveOrdered(i);
                warnings++;
                continue;
            }
            seen.Insert(pt.Id);
        }
    }

    OZL_PointType Find(string id)
    {
        for (int i = 0; i < PointTypes.Count(); i++)
        {
            if (PointTypes[i] && PointTypes[i].Id == id)
                return PointTypes[i];
        }
        return null;
    }

    string NameOf(string id)
    {
        OZL_PointType pt = Find(id);
        if (pt && pt.Name != "")
            return pt.Name;
        return id;
    }

    OZL_PointTypes Copy()
    {
        OZL_PointTypes c = new OZL_PointTypes();
        c.Version = Version;
        for (int i = 0; i < PointTypes.Count(); i++)
        {
            if (PointTypes[i])
                c.PointTypes.Insert(PointTypes[i].Copy());
        }
        return c;
    }
}
