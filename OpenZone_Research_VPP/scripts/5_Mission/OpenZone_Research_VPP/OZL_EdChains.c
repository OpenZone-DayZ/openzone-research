// Ланцюги переробки в редакторі досліджень: правила власника, розкладені по
// лініях. Лінія -- поле ozlLine у config.cpp (OZL_Lines): у проб, носіїв,
// пакувальників і аналізаторів. Рядок лінії -- конвеєр: сировина ->
// пакувальник -> проба -> аналізатор -> носій -> термінал і пул.
//
// Правило належить власникові, якщо його станок -- у DeviceClasses власника
// (OZ_Research_Owners.json), або якщо власник названий у RequiredFactions
// правила. Аналізатор -- правило, чий вхід проба; пакувальник -- правило,
// чий вихід проба. Решта правил власника лінії не має.
//
// Дизайн: docs/specs/2026-11-09-research-editor-vpp-design.md, §1 п. 4.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

class OZL_EdLine
{
    string Line    = "";   // id типу балів = ozlLine
    string Sample  = "";
    string Carrier = "";
    string GroupId = "";   // група, куди йдуть нові правила лінії
    ref array<string> Packers;     // id правил-пакувальників
    ref array<string> Analyzers;   // id правил-аналізаторів

    void OZL_EdLine()
    {
        Packers   = new array<string>();
        Analyzers = new array<string>();
    }
}

class OZL_EdChains
{
    static OZL_OwnerDef OwnerDef(OZL_Owners owners, string owner)
    {
        if (!owners)
            return null;
        for (int i = 0; i < owners.Owners.Count(); i++)
        {
            if (owners.Owners[i] && owners.Owners[i].Id == owner)
                return owners.Owners[i];
        }
        return null;
    }

    static bool RuleOf(OZL_Rule r, OZL_OwnerDef def, string owner)
    {
        if (!r)
            return false;
        if (def && def.DeviceClasses.Find(OZL_Match.StripExact(r.Device)) > -1)
            return true;
        return r.RequiredFactions.Find(owner) > -1;
    }

    // Лінії власника в порядку першої появи в файлі правил.
    static void Lines(OZL_Rules rules, OZL_Owners owners, string owner, array<ref OZL_EdLine> into)
    {
        into.Clear();
        if (!rules)
            return;
        OZL_OwnerDef def = OwnerDef(owners, owner);
        for (int g = 0; g < rules.Groups.Count(); g++)
        {
            OZL_RuleGroup grp = rules.Groups[g];
            if (!grp)
                continue;
            for (int k = 0; k < grp.Rules.Count(); k++)
            {
                OZL_Rule r = grp.Rules[k];
                if (!RuleOf(r, def, owner) || !r.InputItem)
                    continue;
                string input = OZL_Match.StripExact(r.InputItem.Classname);
                if (input != "" && OZL_Lines.IsSample(input))
                {
                    OZL_EdLine la = LineFor(into, OZL_Lines.LineOf(input), grp.Id);
                    la.Sample = input;
                    if (r.Outputs.Count() > 0 && r.Outputs[0])
                        la.Carrier = OZL_Match.StripExact(r.Outputs[0].Classname);
                    la.Analyzers.Insert(r.Id);
                    continue;
                }
                string sample = SampleOut(r);
                if (sample == "")
                    continue;
                OZL_EdLine lp = LineFor(into, OZL_Lines.LineOf(sample), grp.Id);
                if (lp.Sample == "")
                    lp.Sample = sample;
                lp.Packers.Insert(r.Id);
            }
        }
    }

    protected static OZL_EdLine LineFor(array<ref OZL_EdLine> lines, string line, string groupId)
    {
        for (int i = 0; i < lines.Count(); i++)
        {
            if (lines[i].Line == line)
                return lines[i];
        }
        OZL_EdLine l = new OZL_EdLine();
        l.Line = line;
        l.GroupId = groupId;
        lines.Insert(l);
        return l;
    }

    // Клас проби на виході правила (перший такий), або порожньо.
    static string SampleOut(OZL_Rule r)
    {
        for (int i = 0; i < r.Outputs.Count(); i++)
        {
            OZL_RuleOutput o = r.Outputs[i];
            if (o && OZL_Lines.IsSample(o.Classname))
                return OZL_Match.StripExact(o.Classname);
        }
        return "";
    }

    static OZL_RuleOutput SampleOutput(OZL_Rule r)
    {
        for (int i = 0; i < r.Outputs.Count(); i++)
        {
            OZL_RuleOutput o = r.Outputs[i];
            if (o && OZL_Lines.IsSample(o.Classname))
                return o;
        }
        return null;
    }

    static OZL_RuleGroup GroupOf(OZL_Rules rules, string ruleId)
    {
        for (int g = 0; g < rules.Groups.Count(); g++)
        {
            OZL_RuleGroup grp = rules.Groups[g];
            for (int k = 0; k < grp.Rules.Count(); k++)
            {
                if (grp.Rules[k] && grp.Rules[k].Id == ruleId)
                    return grp;
            }
        }
        return null;
    }

    static OZL_RuleGroup FindGroup(OZL_Rules rules, string groupId)
    {
        for (int g = 0; g < rules.Groups.Count(); g++)
        {
            if (rules.Groups[g] && rules.Groups[g].Id == groupId)
                return rules.Groups[g];
        }
        return null;
    }

    static string FreeRuleId(OZL_Rules rules, string base)
    {
        string id = base;
        int n = 1;
        while (rules.Find(id))
        {
            n++;
            id = base + "_" + n.ToString();
        }
        return id;
    }

    // Тір сировини -- тір вузла, якого правило вимагає; без вузла чи з
    // вузлом, якого в дереві немає, -- 0.
    static int TierOf(OZL_Rule r, OZL_TreeConfig tree)
    {
        if (!r || r.RequiredNode == "" || !tree)
            return 0;
        OZL_TreeNode n = tree.FindNode(r.RequiredNode);
        if (!n)
            return 0;
        if (n.Tier < 1)
            return 1;
        return n.Tier;
    }

    // Пакувальники лінії, упорядковані за тіром; у тірі -- як у файлі.
    static void SortedPackers(OZL_Rules rules, OZL_TreeConfig tree, OZL_EdLine line, array<string> into)
    {
        into.Clear();
        array<int> tiers = new array<int>();
        for (int i = 0; i < line.Packers.Count(); i++)
        {
            OZL_Rule r = rules.Find(line.Packers[i]);
            if (!r)
                continue;
            int t = TierOf(r, tree);
            int at = into.Count();
            for (int k = 0; k < into.Count(); k++)
            {
                if (t < tiers[k])
                {
                    at = k;
                    break;
                }
            }
            into.InsertAt(r.Id, at);
            tiers.InsertAt(t, at);
        }
    }

    // ------------------------------------------------- як бачить гравець

    // Назва предмета з config.cpp мовою клієнта: displayName, а для ключа
    // stringtable ($STR_...) -- переклад. Без назви -- сам клас.
    static string ItemName(string cls)
    {
        return ConfigText(cls, "displayName", cls);
    }

    static string ItemDesc(string cls)
    {
        return ConfigText(cls, "descriptionShort", "");
    }

    protected static string ConfigText(string cls, string field, string fallback)
    {
        string c = OZL_Match.StripExact(cls);
        if (c == "")
            return fallback;
        array<string> roots = {"CfgVehicles", "CfgWeapons", "CfgMagazines"};
        for (int i = 0; i < roots.Count(); i++)
        {
            string path = roots[i] + " " + c + " " + field;
            if (!GetGame().ConfigIsExisting(path))
                continue;
            string v = GetGame().ConfigGetTextOut(path);
            if (v == "")
                continue;
            if (v.IndexOf("$") == 0)
                return Widget.TranslateString("#" + v.Substring(1, v.Length() - 1));
            if (v.IndexOf("#") == 0)
                return Widget.TranslateString(v);
            if (v.IndexOf("STR_") == 0)
                return Widget.TranslateString("#" + v);
            return v;
        }
        return fallback;
    }

    // Модулі лінії: класи з OZ_Research_Modules.json, чия лінія -- ця.
    static void ModulesOf(OZL_Modules mods, string line, array<OZL_ModuleDef> into)
    {
        into.Clear();
        if (!mods || line == "")
            return;
        for (int i = 0; i < mods.Modules.Count(); i++)
        {
            OZL_ModuleDef m = mods.Modules[i];
            if (m && OZL_Lines.LineOf(m.Classname) == line)
                into.Insert(m);
        }
    }

    // Частка 0..1 як відсотки цілим: 0.7 -> "70%".
    static string Pct(float f)
    {
        int p = Math.Round(f * 100);
        return p.ToString() + "%";
    }
}

#endif
#endif
#endif
