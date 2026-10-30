// Модулі: OZ_Research_Modules.json -- інструменти у слотах пакувальника.
//
// Модуль працює лише на пакувальнику своєї лінії (ozlLine у config.cpp): на
// чужий він не ставиться й нічого не дає. Кожен цілий модуль додає до
// чистоти проби PurityBonus і до шансу подвійного виходу DoubleChance.

class OZL_ModuleDef
{
    string Classname    = "";
    float  PurityBonus  = 0.1;
    float  DoubleChance = 0.1;
    string Notes        = "";

    OZL_ModuleDef Copy()
    {
        OZL_ModuleDef c = new OZL_ModuleDef();
        c.Classname    = Classname;
        c.PurityBonus  = PurityBonus;
        c.DoubleChance = DoubleChance;
        c.Notes        = Notes;
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
        return 2;
    }

    // Версія 1 мала списки приладів: лінію тепер каже config.cpp.
    override bool Migrate(int from)
    {
        return false;
    }

    override void LoadDefaults()
    {
        super.LoadDefaults();
        Modules.Clear();
        Add("OZL_Tool_Optics");
        Add("OZL_Tool_Centrifuge");
        Add("OZL_Tool_Reagents");
        Add("OZL_Tool_AnomProbe");
        Add("OZL_Tool_Radiometer");
        Add("OZL_Tool_LeadShield");
        Add("OZL_Tool_Oscilloscope");
        Add("OZL_Tool_SolderStation");
        Add("OZL_Tool_Programmer");
        Add("OZL_Tool_Dosimeter");
        Add("OZL_Tool_JewelerLoupe");
        Add("OZL_Tool_LeadCapsule");
        Add("OZL_Tool_PdaReader");
        Add("OZL_Tool_RadioScanner");
        Add("OZL_Tool_MapBoard");
        Add("OZL_Tool_BarrelVise");
        Add("OZL_Tool_Borescope");
        Add("OZL_Tool_GaugeSet");
        Add("OZL_Tool_Compressor");
        Add("OZL_Tool_GasAnalyzer");
        Add("OZL_Tool_PlateClamp");
    }

    private void Add(string cls)
    {
        OZL_ModuleDef m = new OZL_ModuleDef();
        m.Classname = cls;
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
            else if (m.PurityBonus < 0 || m.PurityBonus > 1)
                why = "PurityBonus of '" + m.Classname + "' outside 0..1";
            else if (m.DoubleChance < 0 || m.DoubleChance > 1)
                why = "DoubleChance of '" + m.Classname + "' outside 0..1";
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
            string cls = OZL_Match.StripExact(m.Classname);
            if (!OZL_Match.ClassExists(cls) || !OZL_Lines.IsModule(cls) || OZL_Lines.LineOf(cls) == "")
            {
                OZL_Log.Warn("Modules: '" + m.Classname + "' is not a line module of this mod, dropped");
                Modules.RemoveOrdered(i);
                problems++;
            }
        }
    }

    OZL_ModuleDef Find(string classname)
    {
        for (int i = 0; i < Modules.Count(); i++)
        {
            OZL_ModuleDef m = Modules[i];
            if (m && OZL_Match.MatchClass(classname, m.Classname))
                return m;
        }
        return null;
    }

    // Модуль -- лише на пакувальник своєї лінії; решта вкладень -- як у рушія.
    // Відповідь із config.cpp, тож однакова на сервері й клієнті.
    static bool AllowedOn(string attachmentClass, string deviceClass)
    {
        if (!OZL_Lines.IsModule(attachmentClass))
            return true;
        return OZL_Lines.IsPacker(deviceClass) && OZL_Lines.SameLine(attachmentClass, deviceClass);
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
