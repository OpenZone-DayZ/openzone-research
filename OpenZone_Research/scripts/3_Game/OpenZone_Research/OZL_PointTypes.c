// Типи балів: OZ_Research_PointTypes.json.
//
// Тип балів -- це лінія (біологія, хабар, балістика...): його Id збігається з
// ozlLine проб, носіїв і станків у config.cpp. Тирів і родів немає: рідкість
// сировини -- це число балів, яке пакувальник пише в пробу. Чистота проби теж
// на лінії: BasePurity -- з якою чистотою стартує кожна проба лінії, поки
// правило не задало свою (OZL_Rule.Purity).

class OZL_PointType
{
    string Id         = "";
    string Name       = "";
    string Icon       = "";
    string Color      = "";
    int    SortOrder  = 0;
    // Початкова чистота кожної проби цієї лінії, 0..1; модулі пакувальника
    // додають своє зверху. Правило може задати свою (OZL_Rule.Purity).
    float  BasePurity = OZL_Const.DEFAULT_PURITY;

    OZL_PointType Copy()
    {
        OZL_PointType c = new OZL_PointType();
        c.Id         = Id;
        c.Name       = Name;
        c.Icon       = Icon;
        c.Color      = Color;
        c.SortOrder  = SortOrder;
        c.BasePurity = BasePurity;
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
        return 3;
    }

    // Версія 1 мала тири й роди: переносити нічого, файл іде в карантин ядра.
    // Версія 2 не знала BasePurity, а серіалізатор не виконує ініціалізаторів
    // вкладених полів: ненаписаний ключ читається нулем, і кожна лінія
    // стартувала б з нульовою чистотою. Тому кожна лінія отримує стару
    // типову, 0,7, -- нічого не змінюється, доки адмін не змінить сам.
    override bool Migrate(int from)
    {
        if (from != 2)
            return false;
        for (int i = 0; i < PointTypes.Count(); i++)
        {
            if (PointTypes[i])
                PointTypes[i].BasePurity = OZL_Const.DEFAULT_PURITY;
        }
        Version = LatestVersion();
        return true;
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
        p.Id         = id;
        p.Name       = name;
        p.Color      = color;
        p.SortOrder  = order;
        p.BasePurity = OZL_Const.DEFAULT_PURITY;
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

            // Чистота поза 0..1 не має сенсу ні як шанс, ні як відсоток у пробі:
            // стискаємо в межі, одне попередження на тип.
            if (pt.BasePurity < 0 || pt.BasePurity > 1)
            {
                float clamped = Math.Clamp(pt.BasePurity, 0, 1);
                string said = "PointTypes: type '" + pt.Id + "' BasePurity " + pt.BasePurity.ToString();
                said += " is outside 0..1, set to " + clamped.ToString();
                OZL_Log.Warn(said);
                pt.BasePurity = clamped;
                warnings++;
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

    // BasePurity лінії; -1, коли лінії немає (порожній рядок), типу з таким Id
    // немає чи його значення не з 0..1 (Validate такого не лишає, але відповідь
    // «-1 -- не знаю» чесніша, ніж від'ємна чистота).
    float BasePurityOf(string line)
    {
        if (line == "")
            return -1;
        OZL_PointType pt = Find(line);
        if (!pt || pt.BasePurity < 0 || pt.BasePurity > 1)
            return -1;
        return pt.BasePurity;
    }

    // "#7CB342" (чи "7CB342") -> ARGB з повною непрозорістю; порожньо чи
    // криво -- 0, і екран бере свій колір. Для проводу (OZL_PointName.Color).
    static int ColorArgb(string hex)
    {
        string h = hex.Trim();
        if (h.IndexOf("#") == 0)
            h = h.Substring(1, h.Length() - 1);
        if (h.Length() != 6)
            return 0;
        string digits = "0x" + h;
        int v = digits.HexToInt();
        return ARGB(255, (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF);
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
