// Server-side glue between the research mod and the MCP bridge: the
// `oz_research` verb for world_exec (put an item into a station's cargo, read
// a station, read or grant a faction's points, reset a faction). A stand
// tool, never published. Requires @DZMCP_Bridge, which the stand loads via
// -serverMod; this pbo goes there too.

class CfgPatches
{
    class OpenZone_Research_Bridge
    {
        units[] = {};
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] =
        {
            "DZ_Data",
            "DZ_Scripts",
            "DZMCP_Bridge",
            "OpenZone_Factions",
            "OpenZone_Research"
        };
    };
};

class CfgMods
{
    class OpenZone_Research_Bridge
    {
        dir = "OpenZone_Research_Bridge";
        name = "OpenZone Research Bridge";
        author = "Zone Protocol";
        version = "0.1.0";
        type = "mod";

        dependencies[] = {"Game", "World", "Mission"};

        class defs
        {
            class missionScriptModule { value = ""; files[] = {"OpenZone_Research_Bridge/scripts/5_Mission"}; };
        };
    };
};
