// Правила переробки: OZ_Research_Rules.json -- дані, без логіки станції.
//
// Правило каже: на ЯКОМУ приладі, з ЯКОГО входу (клас, кількість, вміст
// зразка), за ЯКИЙ час і з ЯКОЮ базовою чистотою виходять ЯКІ предмети; що
// при цьому витрачається; хто має право (вузол дерева, фракції, одяг,
// інструменти в слотах). Групи -- це колишні файли теки ProcessingRules ZP:
// один файл, атомарний бекап ядра, одна реєстрація в редакторі.

class OZL_RuleInput
{
    string Classname           = "";
    int    Quantity            = 1;
    bool   ConsumeInput        = true;
    string Content             = "";
    bool   RequireFullQuantity = false;

    OZL_RuleInput Copy()
    {
        OZL_RuleInput c = new OZL_RuleInput();
        c.Classname           = Classname;
        c.Quantity            = Quantity;
        c.ConsumeInput        = ConsumeInput;
        c.Content             = Content;
        c.RequireFullQuantity = RequireFullQuantity;
        return c;
    }
}

class OZL_RuleOutput
{
    string Classname = "";
    int    Quantity  = 1;
    float  Chance    = 1.0;
    string Content   = "";

    OZL_RuleOutput Copy()
    {
        OZL_RuleOutput c = new OZL_RuleOutput();
        c.Classname = Classname;
        c.Quantity  = Quantity;
        c.Chance    = Chance;
        c.Content   = Content;
        return c;
    }
}

class OZL_RuleConsumable
{
    string Classname = "";
    int    Quantity  = 1;
    string Content   = "";

    OZL_RuleConsumable Copy()
    {
        OZL_RuleConsumable c = new OZL_RuleConsumable();
        c.Classname = Classname;
        c.Quantity  = Quantity;
        c.Content   = Content;
        return c;
    }
}

class OZL_Rule
{
    string Id      = "";
    bool   Enabled = true;
    // Клас приладу; суфікс "|1" -- рівно цей клас.
    string Device  = "";
    ref OZL_RuleInput InputItem;
    float  BasePurityMin = 0.5;
    float  BasePurityMax = 0.5;
    float  TimeSec       = 10;
    ref array<ref OZL_RuleConsumable> Consumables;
    ref array<ref OZL_RuleOutput>     Outputs;
    // Єдиний гейт правила деревом: вузол має бути завершений у власника.
    string RequiredNode = "";
    ref array<string> RequiredFactions;
    ref array<string> RequiredWorn;
    ref array<string> RequiredTools;
    string Notes = "";

    void OZL_Rule()
    {
        InputItem        = new OZL_RuleInput();
        Consumables      = new array<ref OZL_RuleConsumable>();
        Outputs          = new array<ref OZL_RuleOutput>();
        RequiredFactions = new array<string>();
        RequiredWorn     = new array<string>();
        RequiredTools    = new array<string>();
    }

    OZL_Rule Copy()
    {
        OZL_Rule c = new OZL_Rule();
        c.Id            = Id;
        c.Enabled       = Enabled;
        c.Device        = Device;
        if (InputItem)
            c.InputItem = InputItem.Copy();
        c.BasePurityMin = BasePurityMin;
        c.BasePurityMax = BasePurityMax;
        c.TimeSec       = TimeSec;
        c.RequiredNode  = RequiredNode;
        c.Notes         = Notes;
        int i;
        for (i = 0; i < Consumables.Count(); i++)
        {
            if (Consumables[i])
                c.Consumables.Insert(Consumables[i].Copy());
        }
        for (i = 0; i < Outputs.Count(); i++)
        {
            if (Outputs[i])
                c.Outputs.Insert(Outputs[i].Copy());
        }
        for (i = 0; i < RequiredFactions.Count(); i++)
            c.RequiredFactions.Insert(RequiredFactions[i]);
        for (i = 0; i < RequiredWorn.Count(); i++)
            c.RequiredWorn.Insert(RequiredWorn[i]);
        for (i = 0; i < RequiredTools.Count(); i++)
            c.RequiredTools.Insert(RequiredTools[i]);
        return c;
    }
}

class OZL_RuleGroup
{
    string Id = "";
    ref array<ref OZL_Rule> Rules;

    void OZL_RuleGroup()
    {
        Rules = new array<ref OZL_Rule>();
    }

    OZL_RuleGroup Copy()
    {
        OZL_RuleGroup c = new OZL_RuleGroup();
        c.Id = Id;
        for (int i = 0; i < Rules.Count(); i++)
        {
            if (Rules[i])
                c.Rules.Insert(Rules[i].Copy());
        }
        return c;
    }
}

class OZL_Rules : OZ_ConfigBase
{
    // Менше п'яти секунд станція не працює: коротший цикл -- це не переробка,
    // а конвеєр, який ніхто не встигає побачити.
    static const float MIN_TIME_SEC = 5;

    ref array<ref OZL_RuleGroup> Groups;

    void OZL_Rules()
    {
        Groups = new array<ref OZL_RuleGroup>();
    }

    override int LatestVersion()
    {
        return 1;
    }

    // Порожньо: правила посилаються на класи предметів, а порожній файл --
    // чесна відповідь «сервер ще нічого не описав». Стартовий пакет -- у
    // examples/.
    override void LoadDefaults()
    {
        super.LoadDefaults();
        Groups.Clear();
    }

    static float EffectiveTimeSec(float configured)
    {
        if (configured < MIN_TIME_SEC)
            return MIN_TIME_SEC;
        return configured;
    }

    // Структурні перевірки: групи з Id, правила з Id, без дублів. Усе, що
    // потребує гри (класи, типи балів), робить Check() після завантаження
    // всіх конфігів.
    override void Validate(out int warnings)
    {
        warnings = 0;
        array<string> seenGroups = new array<string>();
        array<string> seenRules  = new array<string>();

        for (int g = Groups.Count() - 1; g >= 0; g--)
        {
            OZL_RuleGroup grp = Groups[g];
            if (!grp || grp.Id == "" || seenGroups.Find(grp.Id) > -1)
            {
                OZL_Log.Warn("Rules: a group with no Id or a duplicate Id, dropped");
                Groups.RemoveOrdered(g);
                warnings++;
                continue;
            }
            seenGroups.Insert(grp.Id);

            for (int r = grp.Rules.Count() - 1; r >= 0; r--)
            {
                OZL_Rule rule = grp.Rules[r];
                if (!rule || rule.Id == "" || seenRules.Find(rule.Id) > -1)
                {
                    OZL_Log.Warn("Rules: group '" + grp.Id + "': a rule with no Id or a duplicate Id, dropped");
                    grp.Rules.RemoveOrdered(r);
                    warnings++;
                    continue;
                }
                seenRules.Insert(rule.Id);
            }
        }
    }

    // Перевірка проти гри й типів балів. Правило, яке не пройшло, ВИМИКАЄТЬСЯ
    // (Enabled = false), а не викидається: адмін бачить його в редакторі й
    // причину в лозі, а файл лишається його файлом.
    void Check(OZL_PointTypes pointTypes, out int problems)
    {
        problems = 0;
        for (int g = 0; g < Groups.Count(); g++)
        {
            OZL_RuleGroup grp = Groups[g];
            for (int r = 0; r < grp.Rules.Count(); r++)
            {
                OZL_Rule rule = grp.Rules[r];
                if (!rule.Enabled)
                    continue;
                string why = Problem(rule, pointTypes);
                if (why == "")
                    continue;
                OZL_Log.Warn("Rules: '" + rule.Id + "' disabled: " + why);
                rule.Enabled = false;
                problems++;
            }
        }
    }

    static string Problem(OZL_Rule r, OZL_PointTypes pointTypes)
    {
        if (r.TimeSec < MIN_TIME_SEC)
            return "TimeSec below the minimum of " + MIN_TIME_SEC.ToString() + " s";
        if (r.TimeSec > 604800)
            return "TimeSec above 7 days";
        if (r.BasePurityMin < 0 || r.BasePurityMin > 2 || r.BasePurityMax < 0 || r.BasePurityMax > 2)
            return "BasePurity outside 0..2";
        if (r.BasePurityMax < r.BasePurityMin)
            return "BasePurityMax below BasePurityMin";
        if (r.Device == "" || !OZL_Match.ClassExists(OZL_Match.StripExact(r.Device)))
            return "unknown Device '" + r.Device + "'";
        if (!r.InputItem || r.InputItem.Classname == "")
            return "no InputItem.Classname";
        if (!OZL_Match.ClassExists(OZL_Match.StripExact(r.InputItem.Classname)))
            return "unknown Input '" + r.InputItem.Classname + "'";
        if (r.InputItem.Quantity < 1 || r.InputItem.Quantity > 100)
            return "InputItem.Quantity outside 1..100";
        if (!r.InputItem.ConsumeInput)
            return "ConsumeInput=false would make an endless conveyor";
        if (GetGame().ConfigIsExisting("CfgMagazines " + OZL_Match.StripExact(r.InputItem.Classname)))
            return "an input from CfgMagazines is not supported";

        string err = ContentProblem("InputItem", r.InputItem.Classname, r.InputItem.Content, pointTypes);
        if (err != "")
            return err;

        int i;
        for (i = 0; i < r.RequiredTools.Count(); i++)
        {
            if (!OZL_Match.ClassExists(OZL_Match.StripExact(r.RequiredTools[i])))
                return "unknown class in RequiredTools: '" + r.RequiredTools[i] + "'";
        }
        for (i = 0; i < r.RequiredWorn.Count(); i++)
        {
            if (!OZL_Match.ClassExists(OZL_Match.StripExact(r.RequiredWorn[i])))
                return "unknown class in RequiredWorn: '" + r.RequiredWorn[i] + "'";
        }
        for (i = 0; i < r.Consumables.Count(); i++)
        {
            OZL_RuleConsumable c = r.Consumables[i];
            if (!c || !OZL_Match.ClassExists(OZL_Match.StripExact(c.Classname)))
                return "unknown Consumable";
            if (c.Quantity < 1 || c.Quantity > 100)
                return "Consumable.Quantity outside 1..100";
            if (GetGame().ConfigIsExisting("CfgMagazines " + OZL_Match.StripExact(c.Classname)))
                return "a consumable from CfgMagazines is not supported";
            err = ContentProblem("Consumable", c.Classname, c.Content, pointTypes);
            if (err != "")
                return err;
        }
        for (i = 0; i < r.Outputs.Count(); i++)
        {
            OZL_RuleOutput o = r.Outputs[i];
            if (!o || !OZL_Match.ClassExists(o.Classname))
                return "unknown Output";
            if (o.Chance < 0 || o.Chance > 1)
                return "Output.Chance outside 0..1";
            if (o.Quantity < 1 || o.Quantity > 100)
                return "Output.Quantity outside 1..100";
            err = ContentProblem("Output", o.Classname, o.Content, pointTypes);
            if (err != "")
                return err;
            if (IsSampleClass(o.Classname) && o.Content == "")
                return "output '" + o.Classname + "' has no Content: no rule could ever take that sample";
        }
        return "";
    }

    static bool IsSampleClass(string configured)
    {
        return GetGame().IsKindOf(OZL_Match.StripExact(configured), "OZL_Sample_Base");
    }

    static bool IsCarrierClass(string configured)
    {
        return GetGame().IsKindOf(OZL_Match.StripExact(configured), "OZL_Carrier_Base");
    }

    // Вміст мають лише зразки (рядок-ярлик) і носії (стан «<тип балів>:<n>»).
    static string ContentProblem(string where, string classname, string content, OZL_PointTypes pointTypes)
    {
        bool carrier = IsCarrierClass(classname);
        if (content == "")
        {
            if (carrier)
                return where + ": carrier '" + classname + "' needs Content of the form <point type>:<amount>";
            return "";
        }
        if (!IsSampleClass(classname) && !carrier)
            return where + ": Content given for '" + classname + "', but only samples and carriers carry content";
        if (content.Length() > 64)
            return where + ": Content longer than 64 characters";
        string trimmed = content.Trim();
        if (trimmed != content)
            return where + ": Content '" + content + "' has leading or trailing spaces";
        if (carrier)
        {
            string ptId;
            int amount;
            if (!OZL_CarrierState.Parse(content, ptId, amount))
                return where + ": carrier state '" + content + "' must be <point type>:<1.." + OZL_CarrierState.MAX_AMOUNT.ToString() + ">";
            if (pointTypes && !pointTypes.Find(ptId))
                return where + ": carrier promises point type '" + ptId + "', which PointTypes does not know";
        }
        return "";
    }

    OZL_Rule Find(string id)
    {
        for (int g = 0; g < Groups.Count(); g++)
        {
            OZL_RuleGroup grp = Groups[g];
            for (int r = 0; r < grp.Rules.Count(); r++)
            {
                if (grp.Rules[r] && grp.Rules[r].Id == id)
                    return grp.Rules[r];
            }
        }
        return null;
    }

    int Count()
    {
        int n = 0;
        for (int g = 0; g < Groups.Count(); g++)
            n += Groups[g].Rules.Count();
        return n;
    }

    OZL_Rules Copy()
    {
        OZL_Rules c = new OZL_Rules();
        c.Version = Version;
        for (int g = 0; g < Groups.Count(); g++)
        {
            if (Groups[g])
                c.Groups.Insert(Groups[g].Copy());
        }
        return c;
    }
}

// Стан носія балів -- один рядок «<тип балів>:<кількість>», прихований до
// опознання. У 3_Game, бо його читають і правила (перевірка), і предмет.
class OZL_CarrierState
{
    // Тисяча, як у ZP: носій на більше -- не результат переробки, а помилка правила.
    static const int MAX_AMOUNT = 1000;

    static bool Parse(string state, out string pointType, out int amount)
    {
        pointType = "";
        amount = 0;
        int sep = state.IndexOf(":");
        if (sep < 1 || sep >= state.Length() - 1)
            return false;
        pointType = state.Substring(0, sep);
        string tail = state.Substring(sep + 1, state.Length() - sep - 1);
        amount = tail.ToInt();
        if (amount < 1 || amount > MAX_AMOUNT)
            return false;
        // ToInt мовчки дає 0 на сміття; «0» уже відкинуто вище, а «12abc»
        // мусить відкинутись тут: назад число має друкуватись тим самим рядком.
        return amount.ToString() == tail;
    }

    static string Make(string pointType, int amount)
    {
        return pointType + ":" + amount.ToString();
    }
}
