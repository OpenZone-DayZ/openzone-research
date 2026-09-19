// Типи балів: OZ_Research_PointTypes.json.
//
// Тип -- це категорія (біологія, аномалії, електроніка), рід (польові,
// лабораторні) і тір. Категорії й роди описані окремо, щоб інтерфейс мав
// людські імена й порядок; якщо адмін їх не описав, вони виводяться з самих
// типів, і жоден тип не зникає з екрана.

class OZL_PointType
{
    string Id        = "";
    string Name      = "";
    string Icon      = "";
    string Color     = "";
    int    SortOrder = 0;
    string Category  = "";
    string Kind      = "";
    int    Tier      = 1;

    OZL_PointType Copy()
    {
        OZL_PointType c = new OZL_PointType();
        c.Id        = Id;
        c.Name      = Name;
        c.Icon      = Icon;
        c.Color     = Color;
        c.SortOrder = SortOrder;
        c.Category  = Category;
        c.Kind      = Kind;
        c.Tier      = Tier;
        return c;
    }
}

class OZL_PointDimension
{
    string Id        = "";
    string Name      = "";
    int    SortOrder = 0;

    OZL_PointDimension Copy()
    {
        OZL_PointDimension c = new OZL_PointDimension();
        c.Id        = Id;
        c.Name      = Name;
        c.SortOrder = SortOrder;
        return c;
    }
}

class OZL_PointTypes : OZ_ConfigBase
{
    ref array<ref OZL_PointType>      PointTypes;
    ref array<ref OZL_PointDimension> Categories;
    ref array<ref OZL_PointDimension> Kinds;

    void OZL_PointTypes()
    {
        PointTypes = new array<ref OZL_PointType>();
        Categories = new array<ref OZL_PointDimension>();
        Kinds      = new array<ref OZL_PointDimension>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    // Умовчання ZP: три категорії, два роди, три тіри -- вісімнадцять типів.
    override void LoadDefaults()
    {
        super.LoadDefaults();
        PointTypes.Clear();
        Categories.Clear();
        Kinds.Clear();

        int order = 0;
        order = AddFamily(order, "bio",         "біології",    "#7CB342");
        order = AddFamily(order, "anomaly",     "аномалій",    "#AB47BC");
        order = AddFamily(order, "electronics", "електроніки", "#29B6F6");

        AddDimension(Categories, "bio",         "Біологія",    1);
        AddDimension(Categories, "anomaly",     "Аномалії",    2);
        AddDimension(Categories, "electronics", "Електроніка", 3);
        AddDimension(Kinds, "field", "польові",      1);
        AddDimension(Kinds, "lab",   "лабораторні",  2);
    }

    private int AddFamily(int order, string category, string genitive, string color)
    {
        order = AddKind(order, category, genitive, color, "field", "Польове");
        order = AddKind(order, category, genitive, color, "lab",   "Лабораторне");
        return order;
    }

    private int AddKind(int order, string category, string genitive, string color, string kind, string kindWord)
    {
        for (int tier = 1; tier <= 3; tier++)
        {
            order++;
            OZL_PointType p = new OZL_PointType();
            p.Id        = category + "_" + kind + "_t" + tier.ToString();
            p.Name      = kindWord + " дослідження " + genitive + " " + tier.ToString() + " тиру";
            p.Color     = color;
            p.SortOrder = order;
            p.Category  = category;
            p.Kind      = kind;
            p.Tier      = tier;
            PointTypes.Insert(p);
        }
        return order;
    }

    private void AddDimension(array<ref OZL_PointDimension> dims, string id, string name, int order)
    {
        OZL_PointDimension d = new OZL_PointDimension();
        d.Id        = id;
        d.Name      = name;
        d.SortOrder = order;
        dims.Insert(d);
    }

    static string DimensionName(array<ref OZL_PointDimension> dims, string id)
    {
        for (int i = 0; i < dims.Count(); i++)
        {
            if (dims[i] && dims[i].Id == id && dims[i].Name != "")
                return dims[i].Name;
        }
        return id;
    }

    static int DimensionOrder(array<ref OZL_PointDimension> dims, string id)
    {
        for (int i = 0; i < dims.Count(); i++)
        {
            if (dims[i] && dims[i].Id == id)
                return dims[i].SortOrder;
        }
        // Неописаний вимір іде в кінець, але не зникає.
        return 9999;
    }

    // Категорії й роди, яких адмін не описав, виводяться з типів.
    private void SeedDimensions()
    {
        int co = Categories.Count();
        int ko = Kinds.Count();
        for (int i = 0; i < PointTypes.Count(); i++)
        {
            OZL_PointType pt = PointTypes[i];
            if (!pt)
                continue;

            if (pt.Category != "" && DimensionOrder(Categories, pt.Category) == 9999)
            {
                co++;
                AddDimension(Categories, pt.Category, pt.Category, co);
            }
            if (pt.Kind != "" && DimensionOrder(Kinds, pt.Kind) == 9999)
            {
                ko++;
                AddDimension(Kinds, pt.Kind, pt.Kind, ko);
            }
        }
    }

    override void Validate(out int warnings)
    {
        warnings = 0;
        SeedDimensions();

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
            else if (pt.Tier < 0 || pt.Tier > 10)
                why = "type '" + pt.Id + "': Tier outside 0..10";

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
        int i;
        for (i = 0; i < PointTypes.Count(); i++)
        {
            if (PointTypes[i])
                c.PointTypes.Insert(PointTypes[i].Copy());
        }
        for (i = 0; i < Categories.Count(); i++)
        {
            if (Categories[i])
                c.Categories.Insert(Categories[i].Copy());
        }
        for (i = 0; i < Kinds.Count(); i++)
        {
            if (Kinds[i])
                c.Kinds.Insert(Kinds[i].Copy());
        }
        return c;
    }
}
