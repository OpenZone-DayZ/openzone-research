// OpenZone Research for VPP Admin Tools -- the RESEARCH pane of the OpenZone
// tab. Glue: it knows the research mod and the VPP tab at once, so it lives
// apart from both and requires both hard. A server without VPP runs the
// research mod as if this pbo never existed.
//
// DZM_VPPAdminToolsScripts is the CfgPatches class of VPP's script pbo. The
// code guards on AVPPAdminTools: the engine auto-defines CfgMods class names,
// not CfgPatches ones (measured 2026-07-31 on 1.29 diag).

class CfgPatches
{
    class OpenZone_Research_VPP
    {
        units[] = {};
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] =
        {
            "DZ_Data",
            "DZ_Scripts",
            "JM_CF_Scripts",
            "OpenZone_Core",
            "OpenZone_VPP",
            "OpenZone_Research",
            "DZM_VPPAdminToolsScripts"
        };
    };
};

class CfgMods
{
    class OpenZone_Research_VPP
    {
        dir        = "OpenZone_Research_VPP";
        name       = "OpenZone Research for VPP Admin Tools";
        credits    = "Zone Protocol";
        author     = "Zone Protocol";
        version    = "0.1.0";
        type       = "mod";

        dependencies[] = {"World", "Mission"};

        class defs
        {
            class worldScriptModule
            {
                value = "";
                files[] = {"OpenZone_Research_VPP/scripts/4_World"};
            };
            class missionScriptModule
            {
                value = "";
                files[] = {"OpenZone_Research_VPP/scripts/5_Mission"};
            };
        };
    };
};
