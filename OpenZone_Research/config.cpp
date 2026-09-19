// OpenZone Research -- research points and a technology tree, on the core.
//
// WHAT THIS PBO IS. Samples, stations, processing rules, point carriers, the
// faction terminal, the faction pool and the technology tree. Every chain,
// point type, owner and node is the administrator's JSON in $profile:OpenZone.
//
// WHAT IT STANDS ON. OpenZone_Core, hard: configs (OZ_ConfigBase and the
// core's editor), the faction of a player (OZ_Identity), the transport
// (the service pair, OZ_Show, OZ_Notice) and the admin sections. The factions
// themselves come from OpenZone_Factions through the core's identity contract;
// without that mod every player is the default owner from the settings.
//
// WHAT IT IS NOT. The RESEARCH pane of the VPP tab lives in
// @OpenZone_Research_VPP, a separate pbo of this repository that requires the
// OpenZone VPP tab and VPPAdminTools hard.

class CfgPatches
{
    class OpenZone_Research
    {
        units[] = {};
        weapons[] = {};
        requiredVersion = 0.1;
        // Hard dependencies: a blocking window before the game loads rather
        // than a silent skip. The vanilla model pbos join this list together
        // with CfgVehicles (plan T5), not before.
        requiredAddons[] =
        {
            "DZ_Data",
            "DZ_Scripts",
            "JM_CF_Scripts",
            "OpenZone_Core"
        };
    };
};

class CfgMods
{
    class OpenZone_Research
    {
        dir        = "OpenZone_Research";
        name       = "OpenZone Research";
        credits    = "Zone Protocol";
        author     = "Zone Protocol";
        version    = "0.1.0";
        type       = "mod";

        // The class NAME above is the CF ModStorage key of every station,
        // sample and carrier; renaming it after release orphans their state.
        // storageVersion must be above 0 or ModStorage does nothing at all.
        storageVersion = 1;

        dependencies[] = {"Game", "World", "Mission"};

        class defs
        {
            class gameScriptModule
            {
                value = "";
                files[] = {"OpenZone_Research/scripts/3_Game"};
            };
            class worldScriptModule
            {
                value = "";
                files[] = {"OpenZone_Research/scripts/4_World"};
            };
            class missionScriptModule
            {
                value = "";
                files[] = {"OpenZone_Research/scripts/5_Mission"};
            };
        };
    };
};
