// Правила переробки: OZ_Research_Rules.json -- дані, без логіки станції.
//
// Правило каже: на ЯКОМУ приладі, з ЯКОГО входу (клас, кількість), за ЯКИЙ
// час і (за бажання) з ЯКОЮ власною чистотою виходять ЯКІ предмети; що при
// цьому витрачається; хто має право (вузол дерева, фракції, одяг, інструменти
// в слотах). Без власної чистоти проба стартує з BasePurity своєї лінії
// (OZL_PointType). Групи -- один файл, атомарний бекап ядра, одна реєстрація
// в редакторі.
// Вміст проб і носіїв -- рядок у предметі (OZL_Payload), не поле правила.

class OZL_RuleInput
{
    string Classname           = "";
    int    Quantity            = 1;
    bool   ConsumeInput        = true;
    bool   RequireFullQuantity = false;

    OZL_RuleInput Copy()
    {
        OZL_RuleInput c = new OZL_RuleInput();
        c.Classname           = Classname;
        c.Quantity            = Quantity;
        c.ConsumeInput        = ConsumeInput;
        c.RequireFullQuantity = RequireFullQuantity;
        return c;
    }
}

class OZL_RuleOutput
{
    string Classname = "";
    int    Quantity  = 1;
    float  Chance    = 1.0;
    // Лише для проби: скільки балів вона несе (рідкість сировини).
    int    Points    = 0;

    OZL_RuleOutput Copy()
    {
        OZL_RuleOutput c = new OZL_RuleOutput();
        c.Classname = Classname;
        c.Quantity  = Quantity;
        c.Chance    = Chance;
        c.Points    = Points;
        return c;
    }
}

class OZL_RuleConsumable
{
    string Classname = "";
    int    Quantity  = 1;

    OZL_RuleConsumable Copy()
    {
        OZL_RuleConsumable c = new OZL_RuleConsumable();
        c.Classname = Classname;
        c.Quantity  = Quantity;
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
    // Початкова чистота проби пакувальника. 0..1 -- власна чистота цього
    // правила; менше нуля (типово -1) -- взяти BasePurity лінії станка
    // (OZL_Rules.StartPurity). Модулі лінії додають своє зверху.
    float  Purity        = -1;
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
        c.Purity        = Purity;
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
        return 3;
    }

    // Версія 1 мала мітки вмісту й тири: переносити нічого, файл -- у карантин.
    // Версія 2 писала Purity 0,7 у кожне правило: це була типова, тобто
    // «нічого не вибрано». Тепер типове -- чистота лінії (-1), тож 0,7 стає -1;
    // будь-яке інше значення -- вибір адміна, чистота самого предмета, і
    // лишається. Порівняння з допуском: 0,7 у float не точне.
    override bool Migrate(int from)
    {
        if (from != 2)
            return false;
        for (int g = 0; g < Groups.Count(); g++)
        {
            OZL_RuleGroup grp = Groups[g];
            if (!grp || !grp.Rules)
                continue;
            for (int r = 0; r < grp.Rules.Count(); r++)
            {
                OZL_Rule rule = grp.Rules[r];
                if (rule && Math.AbsFloat(rule.Purity - OZL_Const.DEFAULT_PURITY) < 0.001)
                    rule.Purity = -1;
            }
        }
        Version = LatestVersion();
        return true;
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

    // Початкова чистота проби цього циклу -- єдине місце, де її беруть.
    // Власна чистота правила (0..1) перемагає. Менше нуля -- «чистота лінії»:
    // BasePurity типу балів, чий Id -- лінія станка (ozlLine його класу), а як
    // такого типу немає -- лінія проби на виході правила; і лише тоді стала
    // типова. Від'ємне звідси не виходить ніколи: у пробу йде число з 0..1,
    // модулі станка додаються зверху вже в станції.
    static float StartPurity(OZL_Rule rule, string deviceType, OZL_PointTypes pointTypes)
    {
        if (rule && rule.Purity >= 0)
            return rule.Purity;
        if (pointTypes)
        {
            float found = pointTypes.BasePurityOf(OZL_Lines.LineOf(deviceType));
            if (found >= 0)
                return found;
            if (rule)
            {
                for (int i = 0; i < rule.Outputs.Count(); i++)
                {
                    OZL_RuleOutput o = rule.Outputs[i];
                    if (!o || !OZL_Lines.IsSample(o.Classname))
                        continue;
                    found = pointTypes.BasePurityOf(OZL_Lines.LineOf(o.Classname));
                    if (found >= 0)
                        return found;
                }
            }
        }
        return OZL_Const.DEFAULT_PURITY;
    }

    // Структурні перевірки: групи з Id, правила з Id, без дублів. Усе, що
    // потребує гри (класи, лінії, типи балів), робить Check() після
    // завантаження всіх конфігів.
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
                if (why == "" && pointTypes && rule.Outputs.Count() == 1 && OZL_Lines.IsCarrier(rule.Outputs[0].Classname))
                {
                    // Не вимикаємо: правило вірне, бракує типу балів -- носій
                    // вийде, але термінал його не прийме.
                    string carrierLine = OZL_Lines.LineOf(rule.Outputs[0].Classname);
                    if (!pointTypes.Find(carrierLine))
                        OZL_Log.Warn("Rules: '" + rule.Id + "': line '" + carrierLine + "' has no point type, its carriers cannot be deposited");
                }
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
        if (r.Purity > 1)
            return "Purity above 1 (below 0 means the BasePurity of the line)";
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
            if (OZL_Lines.IsSample(c.Classname) || OZL_Lines.IsCarrier(c.Classname))
                return "a sample or a carrier cannot be a consumable";
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
        }
        return LineProblem(r);
    }

    // Лінії: проба -- лише з пакувальника своєї лінії й лише в аналізатор своєї
    // лінії; носій -- лише з аналізу проби тієї ж лінії, і рівно один.
    static string LineProblem(OZL_Rule r)
    {
        string dev = OZL_Match.StripExact(r.Device);
        string input = OZL_Match.StripExact(r.InputItem.Classname);
        if (OZL_Lines.IsSample(input))
        {
            if (!OZL_Lines.IsAnalyzer(dev) || !OZL_Lines.SameLine(dev, input))
                return "sample '" + input + "' goes into '" + dev + "', which is not an analyzer of its line";
            if (r.InputItem.Quantity != 1)
                return "an analysis takes exactly one sample";
            if (r.Outputs.Count() != 1 || !OZL_Lines.IsCarrier(r.Outputs[0].Classname) || !OZL_Lines.SameLine(r.Outputs[0].Classname, input))
                return "an analysis gives exactly one carrier of the sample's line";
            if (r.Outputs[0].Points != 0)
                return "Points on an analysis output: a carrier takes the points of its sample";
            return "";
        }
        for (int k = 0; k < r.Outputs.Count(); k++)
        {
            OZL_RuleOutput o = r.Outputs[k];
            string cls = OZL_Match.StripExact(o.Classname);
            if (OZL_Lines.IsCarrier(cls))
                return "carrier '" + cls + "' comes out of something other than the analysis of a sample";
            if (OZL_Lines.IsSample(cls))
            {
                if (!OZL_Lines.IsPacker(dev) || !OZL_Lines.SameLine(dev, cls))
                    return "sample '" + cls + "' comes out of '" + dev + "', which is not a packer of its line";
                if (o.Points < 1 || o.Points > OZL_Payload.MAX_POINTS)
                    return "sample output '" + cls + "' needs Points 1.." + OZL_Payload.MAX_POINTS.ToString();
            }
            else if (o.Points != 0)
            {
                return "Points given for '" + cls + "', which is not a sample";
            }
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
