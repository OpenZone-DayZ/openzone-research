// Лінія -- властивість класу в config.cpp (поле ozlLine): у проб, носіїв,
// пакувальників, аналізаторів і модулів. Роль станка -- за його базою в
// конфігу. Терміналів лінія не стосується.

class OZL_Lines
{
    static string LineOf(string classname)
    {
        string path = "CfgVehicles " + OZL_Match.StripExact(classname) + " ozlLine";
        if (!GetGame().ConfigIsExisting(path))
            return "";
        return GetGame().ConfigGetTextOut(path);
    }

    static bool SameLine(string a, string b)
    {
        string la = LineOf(a);
        return la != "" && la == LineOf(b);
    }

    static bool IsSample(string classname)
    {
        return GetGame().IsKindOf(OZL_Match.StripExact(classname), "OZL_Sample_Base");
    }

    static bool IsCarrier(string classname)
    {
        return GetGame().IsKindOf(OZL_Match.StripExact(classname), "OZL_Carrier_Base");
    }

    static bool IsPacker(string classname)
    {
        return GetGame().IsKindOf(OZL_Match.StripExact(classname), "OZL_Packer_Base");
    }

    static bool IsAnalyzer(string classname)
    {
        return GetGame().IsKindOf(OZL_Match.StripExact(classname), "OZL_Analyzer_Base");
    }

    static bool IsModule(string classname)
    {
        return GetGame().IsKindOf(OZL_Match.StripExact(classname), "OZL_Tool_Base");
    }
}
