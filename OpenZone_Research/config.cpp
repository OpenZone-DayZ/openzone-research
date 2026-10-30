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
        // than a silent skip.
        requiredAddons[] =
        {
            "DZ_Data",
            "DZ_Scripts",
            "JM_CF_Scripts",
            "OpenZone_Core",
            // The vanilla pbos whose models and base classes the items below
            // borrow: the fridge, the briefcase, the lab furniture, the radar
            // console. Vanilla, so every server has them; the binariser still
            // needs the base classes declared before ours.
            "DZ_Gear_Containers",
            "DZ_Gear_Camping",
            "DZ_Structures_Furniture",
            "DZ_Radio"
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
        storageVersion = 2;

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

class CfgSlots
{
    class Slot_OZL_Tool1
    {
        name = "OZL_Tool1";
        displayName = "$STR_OZL_slot_tool";
        ghostIcon = "missing";
    };
    class Slot_OZL_Tool2
    {
        name = "OZL_Tool2";
        displayName = "$STR_OZL_slot_tool";
        ghostIcon = "missing";
    };
    class Slot_OZL_Tool3
    {
        name = "OZL_Tool3";
        displayName = "$STR_OZL_slot_tool";
        ghostIcon = "missing";
    };
};

// Модуль, вставлений у слот, видно на станку : у моделях пакувальників на місцях module_1..3 стоять
// проксі models\proxies\ozl_tool1..3. Рушій шукає клас проксі за ім'ям файлу ("Proxy" + ім'я p3d) і
// малює на його місці модель предмета зі слота inventorySlot; порожній слот не малюється. Решту
// (simulation = "ProxyInventory", autocenter = 0) дає ванільний ProxyAttachment.
class CfgNonAIVehicles
{
    class ProxyAttachment;
    class Proxyozl_tool1 : ProxyAttachment
    {
        scope = 2;
        inventorySlot[] = {"OZL_Tool1"};
        model = "\OpenZone_Research\models\proxies\ozl_tool1.p3d";
    };
    class Proxyozl_tool2 : ProxyAttachment
    {
        scope = 2;
        inventorySlot[] = {"OZL_Tool2"};
        model = "\OpenZone_Research\models\proxies\ozl_tool2.p3d";
    };
    class Proxyozl_tool3 : ProxyAttachment
    {
        scope = 2;
        inventorySlot[] = {"OZL_Tool3"};
        model = "\OpenZone_Research\models\proxies\ozl_tool3.p3d";
    };
};

class CfgVehicles
{
    class Inventory_Base;
    class Container_Base;

    // ---- СПІЛЬНА БАЗА СТАЦІОНАРНИХ ПРИЛАДІВ ----
    // Канон Bohemia для «ItemBase на будівельній моделі» — PowerGeneratorStatic
    // (structures_sakhal config.cpp:3543): physLayer=item_large + carveNavmesh + GlobalArmor damage=0.
    // physLayer КРИТИЧНИЙ: перешкодою рушій вважає ЛИШЕ item_large — дефолтний item_small
    // навмисне прохідний (FireplaceBase.c:2503, Environment.c:406).

    // ---- ІНСТРУМЕНТИ ПРИЛАДІВ ----
    // НЕ витрачаються: стоять у слоті й відкривають правила, що їх вимагають
    // (OZL_Rule.RequiredTools). Три різні моделі — щоб їх було видно в слотах.
    //
    // МОДЕЛІ ЗВІРЕНО ПО ТАБЛИЦЯХ ФАЙЛІВ ІГРОВИХ PBO. Спершу тут стояв
    // \dz\gear	ools\Toolbox.p3d — такого шляху в грі НЕМА ЖОДНОГО, і предмет без
    // моделі, узятий у руки, ронив КЛІЄНТ (ACCESS_VIOLATION, у скриптовому логу лише
    // ванільний шум). Перевірка одним рядком:
    //   grep -ail "<ім'я>" *.pbo   у теці DayZ\Addons
    // (контроль методу: Protector_Case знаходиться, Toolbox — ні).
    class OZL_Tool_Base : Inventory_Base
    {
        scope = 0;
        weight = 800;
        itemSize[] = {2, 2};
        spawnDamageRange[] = {0, 0};
        // У кожного модуля лінії свій слот (рішення користувача 26.10, R09): слот 1/2/3 = модуль
        // 1/2/3 лінії, і місце на станції зроблене під свій прилад (тиски -- де були вбудовані тиски).
        inventorySlot[] = {"OZL_Tool1", "OZL_Tool2", "OZL_Tool3"};
    };
    class OZL_Tool_Optics : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "bio";
        inventorySlot[] = {"OZL_Tool1"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_optics";
        descriptionShort = "$STR_OZL_tool_optics_desc";
        model = "\OpenZone_Research\models\m44_tool_optics\ozr_tool_optics.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m44_tool_optics\data\ozr_tool_optics_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m44_tool_optics\data\ozr_tool_optics.rvmat"
        };
        class AnimationSources
        {
            class ozl_focus
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m44_tool_optics\data\ozr_tool_optics_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m44_tool_optics\data\ozr_tool_optics_on.rvmat"};
            class Focus { type = "wobble"; source = "ozl_focus"; mid = 0.5; amp = 0.35; period = 4.0; };
        };
    };
    class OZL_Tool_Centrifuge : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "bio";
        inventorySlot[] = {"OZL_Tool2"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_centrifuge";
        descriptionShort = "$STR_OZL_tool_centrifuge_desc";
        model = "\OpenZone_Research\models\m45_centrifuge\ozr_centrifuge.p3d";
        hiddenSelections[] = {"ozl_lamp_work"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m45_centrifuge\data\ozr_centrifuge_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m45_centrifuge\data\ozr_centrifuge.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.8;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp_work"};
            onTextures[]   = {"\OpenZone_Research\models\m45_centrifuge\data\ozr_centrifuge_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m45_centrifuge\data\ozr_centrifuge_on.rvmat"};
            class Rotor  { type = "loop";   source = "ozl_work"; };
            class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.58; amp = 0.025; period = 2.3; };
        };
    };
    class OZL_Tool_Reagents : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "bio";
        inventorySlot[] = {"OZL_Tool3"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_reagents";
        descriptionShort = "$STR_OZL_tool_reagents_desc";
        model = "\OpenZone_Research\models\m46_reagents\ozr_reagents.p3d";
        hiddenSelections[] = {"ozl_sample"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample.rvmat"
        };
        class AnimationSources
        {
            class ozl_work
            {
                source = "user";
                animPeriod = 0.6;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            class Sample  { type = "frames"; selection = "ozl_sample"; period = 0.3;
                            textures[] = {
                                "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f0_co.paa", "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f1_co.paa",
                                "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f2_co.paa", "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f3_co.paa",
                                "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f4_co.paa", "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f5_co.paa",
                                "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f6_co.paa", "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f7_co.paa",
                                "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f8_co.paa", "\OpenZone_Research\models\m46_reagents\data\ozr_reagents_sample_f9_co.paa"}; };
            class Bubbles { type = "loop"; source = "ozl_work"; };
        };
    };
    // Модуль лінії Аномальне (M69): виносний сцинтиляційний блок детектування (вигляд СРП-68-01) на
    // двох V-подібних опорах, ~0.26 x 0.16 x 0.09. Спільний для пакувальників лінії всіх фракцій
    // (M03, M09).
    class OZL_Tool_AnomProbe : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "anomaly";
        inventorySlot[] = {"OZL_Tool1"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_anomprobe";
        descriptionShort = "$STR_OZL_tool_anomprobe_desc";
        model = "\OpenZone_Research\models\m69_anom_probe\ozr_anom_probe.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m69_anom_probe\data\ozr_anom_probe_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m69_anom_probe\data\ozr_anom_probe.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m69_anom_probe\data\ozr_anom_probe_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m69_anom_probe\data\ozr_anom_probe_on.rvmat"};
            class Pulse { type = "blink"; selection = "ozl_lamp"; on = 0.08; off = 0.30; };
        };
    };
    // Модуль лінії Аномальне (M70): лабораторний радіометр бета-випромінювання типу «Бета» (1987) —
    // свинцевий будиночок у сталевій обшивці з дверцятами, на даху пульт із РК-табло й кювета з
    // пробою, кабель до вводу збоку; ~0.18 x 0.20 x 0.24. Спільний для пакувальників лінії всіх
    // фракцій (M03, M09). ozl_screen (табло) і ozl_lamp_work (світлодіод) — вигляд «вимкнено»;
    // «робота» — атлас _on (тестовий клас OZR_Test_M70_On).
    class OZL_Tool_Radiometer : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "anomaly";
        inventorySlot[] = {"OZL_Tool2"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_radiometer";
        descriptionShort = "$STR_OZL_tool_radiometer_desc";
        model = "\OpenZone_Research\models\m70_radiometer\ozr_radiometer.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp_work"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_co.paa",
            "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd.rvmat",
            "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp_work"};
            onTextures[]   = {"\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_f0_co.paa", "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_on.rvmat", "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_on.rvmat"};
            class Count { type = "frames"; selection = "ozl_screen"; period = 0.9;
                          textures[] = {"\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_f0_co.paa", "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_f1_co.paa",
                                        "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_f2_co.paa", "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_f3_co.paa",
                                        "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_f4_co.paa", "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_f5_co.paa",
                                        "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_f6_co.paa", "\OpenZone_Research\models\m70_radiometer\data\ozr_radiometer_lcd_f7_co.paa"}; };
            class Led   { type = "blink";  selection = "ozl_lamp_work"; on = 0.08; off = 0.45; };
        };
    };
    // Модуль лінії Аномальне (M71): свинцевий «будиночок» — літера П у два ряди з цеглин 50 x 100 x
    // 200 (задня стінка — дві цілі, боковини — розпиляні половинки), зверху сталева плита з отвором
    // під датчик, усередині столик під пробу; ~0.21 x 0.16 x 0.21. Спільний для пакувальників лінії
    // всіх фракцій (M03, M09).
    class OZL_Tool_LeadShield : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "anomaly";
        inventorySlot[] = {"OZL_Tool3"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_leadshield";
        descriptionShort = "$STR_OZL_tool_leadshield_desc";
        model = "\OpenZone_Research\models\m71_lead_shield\ozr_lead_shield.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m71_lead_shield\data\ozr_lead_shield_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m71_lead_shield\data\ozr_lead_shield.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m71_lead_shield\data\ozr_lead_shield_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m71_lead_shield\data\ozr_lead_shield_on.rvmat"};
            class Beacon { type = "blink"; selection = "ozl_lamp"; on = 0.25; off = 0.55; };
        };
    };
    // Модуль лінії Електроніка (M72): малогабаритний осцилограф С1-94 (100 x 190 x 300 мм за описом
    // типу) — сіро-зелений кожух, екран ЕПТ із сіткою (погашений, видів «робота» модуль не має),
    // один щуп у вході Y і лежить на полиці, другий змотаний у бухту на даху, мережевий шнур; ~0.19
    // x 0.20 x 0.31 разом зі щупами. Стоїть уздовж глибини полиці (0,30 м). Спільний для
    // пакувальників лінії всіх фракцій (M05, M11).
    class OZL_Tool_Oscilloscope : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "electronics";
        inventorySlot[] = {"OZL_Tool1"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_oscilloscope";
        descriptionShort = "$STR_OZL_tool_oscilloscope_desc";
        model = "\OpenZone_Research\models\m72_oscilloscope\ozr_oscilloscope.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_co.paa",
            "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen.rvmat",
            "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            // шляхи -- як у install.json моделі (його пише генератор)
            onSelections[] = {"ozl_screen", "ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f0_co.paa", "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_on.rvmat", "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_on.rvmat"};
            class Trace { type = "frames"; selection = "ozl_screen"; period = 0.12;
                          textures[] = {
                              "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f0_co.paa", "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f1_co.paa",
                              "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f2_co.paa", "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f3_co.paa",
                              "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f4_co.paa", "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f5_co.paa",
                              "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f6_co.paa", "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f7_co.paa",
                              "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f8_co.paa", "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f9_co.paa",
                              "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f10_co.paa", "\OpenZone_Research\models\m72_oscilloscope\data\ozr_oscilloscope_screen_f11_co.paa"}; };
        };
    };
    // Модуль лінії Електроніка (M73): паяльна станція 1980–90-х із терморегулятором (вигляд Weller
    // WTCP-S, ручка 150–450 як у WECP-20) — блок у сіро-блакитній емалі з катушкою припою на даху,
    // праворуч підставка зі спіраллю й губкою, паяльник у спіралі; ~0.21 x 0.19 x 0.20 без шнурів.
    // Спільний для пакувальників лінії всіх фракцій (M05, M11). ozl_lamp_work (клавіша мережі й
    // лампа нагріву) — вигляд «вимкнено»; «робота» — атлас _on (тестовий клас OZR_Test_M73_On).
    class OZL_Tool_SolderStation : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "electronics";
        inventorySlot[] = {"OZL_Tool2"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_solderstation";
        descriptionShort = "$STR_OZL_tool_solderstation_desc";
        model = "\OpenZone_Research\models\m73_solder_station\ozr_solder_station.p3d";
        hiddenSelections[] = {"ozl_lamp_work", "ozl_lamp_heat"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m73_solder_station\data\ozr_solder_station_co.paa",
            "\OpenZone_Research\models\m73_solder_station\data\ozr_solder_station_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m73_solder_station\data\ozr_solder_station.rvmat",
            "\OpenZone_Research\models\m73_solder_station\data\ozr_solder_station.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp_work", "ozl_lamp_heat"};
            onTextures[]   = {"\OpenZone_Research\models\m73_solder_station\data\ozr_solder_station_on_co.paa",
                              "\OpenZone_Research\models\m73_solder_station\data\ozr_solder_station_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m73_solder_station\data\ozr_solder_station_on.rvmat",
                              "\OpenZone_Research\models\m73_solder_station\data\ozr_solder_station_on.rvmat"};
            class Heat { type = "blink"; selection = "ozl_lamp_heat"; on = 0.6; off = 0.9; };
        };
    };
    // Модуль лінії Електроніка (M74): саморобний програматор ПЗП (К573РФ) — алюмінієвий корпус із
    // гетинаксовою панеллю, зелена важільна ZIF-панель на 40 виводів із К573РФ5, тумблери,
    // світлодіоди, галетник типу мікросхеми, сірий шлейф гармошкою до роз'єму DB-25; поруч
    // ультрафіолетовий стирач — коробка у світлій емалі з лотком і віконцем УФС; ~0.21 x 0.20 x
    // 0.06. Спільний для пакувальників лінії всіх фракцій (M05, M11). ozl_lamp_work (червоний і
    // зелений світлодіоди, неонова лампа, віконце стирача) — вигляд «вимкнено»; «робота» — атлас
    // _on (тестовий клас OZR_Test_M74_On).
    class OZL_Tool_Programmer : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "electronics";
        inventorySlot[] = {"OZL_Tool3"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_programmer";
        descriptionShort = "$STR_OZL_tool_programmer_desc";
        model = "\OpenZone_Research\models\m74_programmer\ozr_programmer.p3d";
        hiddenSelections[] = {"ozl_lamp_work", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m74_programmer\data\ozr_programmer_co.paa",
            "\OpenZone_Research\models\m74_programmer\data\ozr_programmer_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m74_programmer\data\ozr_programmer.rvmat",
            "\OpenZone_Research\models\m74_programmer\data\ozr_programmer.rvmat"
        };
        class AnimationSources
        {
            class ozl_work
            {
                source = "user";
                animPeriod = 30;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp_work"};
            onTextures[]   = {"\OpenZone_Research\models\m74_programmer\data\ozr_programmer_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m74_programmer\data\ozr_programmer_on.rvmat"};
            class Timer { type = "loop";  source = "ozl_work"; };
            class Write { type = "blink"; selection = "ozl_lamp"; on = 0.15; off = 0.15; };
        };
    };
    // Модуль лінії Хабар (M75): дозиметр скупника — носимий ДРГ-01Т1 (175 x 85 x 46 мм,
    // сіро-зелений корпус) лежить табло догори в саморобному дерев'яному ящику з поролоновим
    // ложементом; кришка-екран відкинута назад, зсередини оббита свинцевим листом зі знаком
    // радіації; ~0.20 x 0.15 x 0.17. Спільний для пакувальників лінії всіх фракцій (M13, M18).
    // ozl_screen (табло) — вигляд «вимкнено»; «робота» — атлас _on (тестовий клас OZR_Test_M75_On).
    class OZL_Tool_Dosimeter : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "khabar";
        inventorySlot[] = {"OZL_Tool1"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_dosimeter";
        descriptionShort = "$STR_OZL_tool_dosimeter_desc";
        model = "\OpenZone_Research\models\m75_dosimeter\ozr_dosimeter.p3d";
        hiddenSelections[] = {"ozl_screen"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd.rvmat"
        };
        class AnimationSources
        {
            class ozl_switch
            {
                source = "user";
                animPeriod = 0.25;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen"};
            onTextures[]   = {"\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_f0_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_on.rvmat"};
            class Reading { type = "frames"; selection = "ozl_screen"; period = 0.8;
                            textures[] = {"\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_f0_co.paa", "\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_f1_co.paa",
                                          "\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_f2_co.paa", "\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_f3_co.paa",
                                          "\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_f4_co.paa", "\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_f5_co.paa",
                                          "\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_f6_co.paa", "\OpenZone_Research\models\m75_dosimeter\data\ozr_dosimeter_lcd_f7_co.paa"}; };
            class Power   { type = "pose"; source = "ozl_switch"; };   // як подача ozl_feed у M16
        };
    };
    // Модуль лінії Хабар (M76): штативна лупа годинникаря — чавунна основа-дзвін у чорній муаровій
    // емалі, воронена стійка з пружиною й хомутом, похила штанга з хромованою оправою (лінза Ø 65),
    // під нею темно-синя оксамитова підкладка з каблучкою на бирці, пінцет і папірець для каменів;
    // ~0.20 x 0.23 x 0.19. Спільний для пакувальників лінії всіх фракцій (M13, M18).
    class OZL_Tool_JewelerLoupe : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "khabar";
        inventorySlot[] = {"OZL_Tool2"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_jewelerloupe";
        descriptionShort = "$STR_OZL_tool_jewelerloupe_desc";
        model = "\OpenZone_Research\models\m76_jeweler_loupe\ozr_jeweler_loupe.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m76_jeweler_loupe\data\ozr_jeweler_loupe_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m76_jeweler_loupe\data\ozr_jeweler_loupe.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m76_jeweler_loupe\data\ozr_jeweler_loupe_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m76_jeweler_loupe\data\ozr_jeweler_loupe_on.rvmat"};
        };
    };
    // Модуль лінії Хабар (M77): свинцевий пенал — литий свинець 20 мм у звареній сталевій обоймі в
    // сірій емалі, свинцева кришка на двох петлях закрита натяжною засувкою, відкидні ручки з
    // боків, трилисник за трафаретом на кришці й спереду, порожній шильдик, бирка з номером на
    // ручці; ~0.20 x 0.16 x 0.12. Спільний для пакувальників лінії всіх фракцій (M13, M18).
    class OZL_Tool_LeadCapsule : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "khabar";
        inventorySlot[] = {"OZL_Tool3"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_leadcapsule";
        descriptionShort = "$STR_OZL_tool_leadcapsule_desc";
        model = "\OpenZone_Research\models\m77_lead_case\ozr_lead_case.p3d";
        class AnimationSources
        {
            class ozl_lid
            {
                source = "user";
                animPeriod = 1.2;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            class Lid { type = "pose"; source = "ozl_lid"; };   // як подача головки M16
        };
    };
    // Модуль лінії Стежки (M78): зчитувач КПК — кишеньковий комп'ютер кінця 90-х (Palm III, 119 x
    // 81 x 18 мм) у підставці для синхронізації з кнопкою; підставку притиснуто двома алюмінієвими
    // скобами до плити склотекстоліту на гумових ніжках, сірий кабель змотано в бухту з хомутом, на
    // кінці — роз'єм DE-9 до COM-порту; поруч стилус та інвентарна етикетка зі штрихкодом; ~0.18 x
    // 0.15 x 0.14. Спільний для пакувальників лінії всіх фракцій (M15, M20). ozl_screen (екран КПК)
    // — вигляд «вимкнено»; «робота» — атлас _on (тестовий клас OZR_Test_M78_On).
    class OZL_Tool_PdaReader : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "trails";
        inventorySlot[] = {"OZL_Tool1"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_pdareader";
        descriptionShort = "$STR_OZL_tool_pdareader_desc";
        model = "\OpenZone_Research\models\m78_pda_reader\ozr_pda_reader.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_co.paa",
            "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen.rvmat",
            "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_f0_co.paa",
                              "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_on.rvmat",
                              "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_on.rvmat"};
            class Sync { type = "frames"; selection = "ozl_screen"; period = 0.25;
                         textures[] = {"\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_f0_co.paa",
                                       "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_f1_co.paa",
                                       "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_f2_co.paa",
                                       "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_f3_co.paa",
                                       "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_f4_co.paa",
                                       "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_f5_co.paa",
                                       "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_f6_co.paa",
                                       "\OpenZone_Research\models\m78_pda_reader\data\ozr_pda_reader_screen_f7_co.paa"}; };
            class Led  { type = "blink"; selection = "ozl_lamp"; on = 0.08; off = 0.17; };
        };
    };
    // Модуль лінії Стежки (M79): радіосканер — настільний сканувальний приймач кінця 80-х (AOR
    // AR3000A, 138 x 80 x 200 мм) у темно-сірому корпусі: РК-табло з жовто-зеленим підсвічуванням,
    // клавіатура з помаранчевими цифрами, валкодер, ручки шумоподавлювача й гучності; ззаду
    // телескопічна антена на BNC із шарніром, мережевий адаптер 12 В на шнурі; у гнізді на лиці —
    // навушник-«крапля», на даху — малярна стрічка з частотами; ~0.17 x 0.29 x 0.25. Спільний для
    // пакувальників лінії всіх фракцій (M15, M20). ozl_screen (табло) — вигляд «вимкнено»; «робота»
    // — атлас _on (тестовий клас OZR_Test_M79_On).
    class OZL_Tool_RadioScanner : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "trails";
        inventorySlot[] = {"OZL_Tool2"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_radioscanner";
        descriptionShort = "$STR_OZL_tool_radioscanner_desc";
        model = "\OpenZone_Research\models\m79_radio_scanner\ozr_radio_scanner.p3d";
        hiddenSelections[] = {"ozl_screen"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen"};
            onTextures[]   = {"\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f0_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_on.rvmat"};
            class Scan
            {
                type = "frames";
                selection = "ozl_screen";
                period = 0.15;
                textures[] = {
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f0_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f1_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f2_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f3_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f4_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f5_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f6_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f7_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f8_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f9_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f10_co.paa",
                    "\OpenZone_Research\models\m79_radio_scanner\data\ozr_radio_scanner_lcd_f11_co.paa"};
            };
        };
    };
    // Модуль лінії Стежки (M80): планшет із мапами — фанерна дошка 206 x 200 мм під 20° на
    // сосновому пюпітрі з бортиком; топокарта під жовтуватим целулоїдом із маршрутом склографом,
    // боки прихоплено ізострічкою; угорі алюмінієва планка на барашках тримає зелену офіцерську
    // лінійку 200 x 100; біля бортика — курвіметр КУ-А і компас Адріанова, ремінець перекинуто
    // через бортик, пряжка спереду; ~0.21 x 0.21 x 0.10. Спільний для пакувальників лінії всіх
    // фракцій (M15, M20).
    class OZL_Tool_MapBoard : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "trails";
        inventorySlot[] = {"OZL_Tool3"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_mapboard";
        descriptionShort = "$STR_OZL_tool_mapboard_desc";
        model = "\OpenZone_Research\models\m80_map_board\ozr_map_board.p3d";
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.5; amp = 0.35; period = 1.4; };
        };
    };
    // Модуль лінії Балістика (M81): малі слюсарні лещата класу ТСС-63 (габарит за ТСС-80 у
    // пропорції 63/80) — литий корпус у сіро-бірюзовій емалі на плиті з двома вухами під болти,
    // наковаленка, шліфований повзун, воронований гвинт із воротком убік; на губках алюмінієві
    // накладки, між ними букові вкладиші з пазом, у них затиснуто обрізок ствола 7,62 з основою
    // мушки; ~0.20 x 0.20 x 0.11. Спільний для пакувальників лінії всіх фракцій (M23, M27, M32).
    class OZL_Tool_BarrelVise : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        inventorySlot[] = {"OZL_Tool1"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_barrelvise";
        descriptionShort = "$STR_OZL_tool_barrelvise_desc";
        model = "\OpenZone_Research\models\m81_barrel_vise\ozr_barrel_vise.p3d";
        class AnimationSources
        {
            class ozl_clamp
            {
                source = "user";
                animPeriod = 0.8;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            class Clamp { type = "pose"; source = "ozl_clamp"; };   // 0 -> 1 за 0,8 с в работе, обратно после
        };
    };
    // Модуль лінії Балістика (M82): жорсткий збройовий бороскоп типу Hawkeye у відкритому кейсі з
    // чорного ABS — окуляр із наглазником DIN 32, корпус зі штуцером світловода, зонд Ø 6,35; поруч
    // дзеркальна трубка, освітлювач на батарейках AA і дві батарейки в синьому поролоні; у кришці —
    // пам'ятка-схема без слів і пакет ватних паличок під гумкою; на ложементі зірвана пломба; ~0.22
    // x 0.20 x 0.18. Спільний для пакувальників лінії всіх фракцій (M23, M27, M32). ozl_lamp_work
    // (скло освітлювача) — вигляд «вимкнено»; «робота» — атлас _on (тестовий клас OZR_Test_M82_On).
    class OZL_Tool_Borescope : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        inventorySlot[] = {"OZL_Tool2"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_borescope";
        descriptionShort = "$STR_OZL_tool_borescope_desc";
        model = "\OpenZone_Research\models\m82_borescope\ozr_borescope.p3d";
        hiddenSelections[] = {"ozl_lamp_work"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m82_borescope\data\ozr_borescope_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m82_borescope\data\ozr_borescope.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp_work"};
            onTextures[]   = {"\OpenZone_Research\models\m82_borescope\data\ozr_borescope_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m82_borescope\data\ozr_borescope_on.rvmat"};
            class Flicker { type = "blink"; selection = "ozl_lamp_work"; on = 2.4; off = 0.06; };
        };
    };
    // Модуль лінії Балістика (M83): набір військових калібрів за зразком комплекту 56-И-01 до
    // АК/СКС/РПД, без приладу ПРБ-1 — ящик зі світлого дерева під рудим лаком, кришка на двох
    // петлях відкинута, пробій спереду; у вкладиші фрезеровані гнізда з виїмками під палець: калібр
    // каналу ствола, калібри-шашки прохідний / непрохідний (червона смуга) / бракувальний, пластини
    // виходу бойка, стрижні до зачепу викидача (один з накаткою); алюмінієві таблички груп лише з
    // цифрами, у кришці — опис цифрами; ~0.20 x 0.17 x 0.165. Спільний для пакувальників лінії всіх
    // фракцій (M23, M27, M32).
    class OZL_Tool_GaugeSet : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        inventorySlot[] = {"OZL_Tool3"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_gaugeset";
        descriptionShort = "$STR_OZL_tool_gaugeset_desc";
        model = "\OpenZone_Research\models\m83_gauge_set\ozr_gauge_set.p3d";
    };
    // Модуль лінії Захист (M84): ручний опресувальник у настільному виконанні — сталева плита на
    // двох швелерах, ліворуч бачок із заливною пробкою й алюмінієвою інвентарною біркою, праворуч
    // плунжерний насос, важіль із гумовою ручкою піднято над бачком; манометр Ø100 на стояку з
    // латунного колектора, вентиль із червоним маховиком, шланг високого тиску петлею з
    // накінечником; сіра емаль; ~0.19 x 0.18 x 0.24. Спільний для пакувальників лінії всіх фракцій
    // (M25, M29, M34). Стрілка манометра — кістка ozl_work (0 — на нулі, 1 — 8 із 16; тестовий клас
    // OZR_Test_M84_On).
    class OZL_Tool_Compressor : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "protection";
        inventorySlot[] = {"OZL_Tool1"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_compressor";
        descriptionShort = "$STR_OZL_tool_compressor_desc";
        model = "\OpenZone_Research\models\m84_test_pump\ozr_test_pump.p3d";
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            class Pump   { type = "wobble"; source = "ozl_work";   mid = 0.5;   amp = 0.5;  period = 1.6; };
            class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.625; amp = 0.02; period = 1.6; };
        };
    };
    // Модуль лінії Захист (M85): універсальний газоаналізатор УГ-2 у роботі — повітрозабірний
    // пристрій 110 x 105 x 200 у сірій молотковій емалі, кришка відкинута назад, у склянці зведений
    // шток із головкою «100», гумова трубка петлею до індикаторної трубки, що лежить на краю
    // відкритої коробки запасних трубок і ампул із порошком; у кришці — картка шкал лише з цифрами;
    // ~0.20 x 0.21 x 0.25. Спільний для пакувальників лінії всіх фракцій (M25, M29, M34).
    // ozl_screen (індикаторна трубка) — вигляд «вимкнено», чистий жовтий стовпчик; «робота» — атлас
    // _on, синій стовпчик; шток — кістка ozl_work, хід 25 мм (тестовий клас OZR_Test_M85_On).
    class OZL_Tool_GasAnalyzer : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "protection";
        inventorySlot[] = {"OZL_Tool2"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_gasanalyzer";
        descriptionShort = "$STR_OZL_tool_gasanalyzer_desc";
        model = "\OpenZone_Research\models\m85_gas_analyzer\ozr_gas_analyzer.p3d";
        hiddenSelections[] = {"ozl_screen"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m85_gas_analyzer\data\ozr_gas_analyzer_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m85_gas_analyzer\data\ozr_gas_analyzer.rvmat"
        };
        class AnimationSources
        {
            class ozl_work
            {
                source = "user";
                animPeriod = 4;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen"};                       // индикаторная трубка (столбик порошка)
            onTextures[]   = {"\OpenZone_Research\models\m85_gas_analyzer\data\ozr_gas_analyzer_on_co.paa"};   // та сама тека, що й у hiddenSelectionsTextures моделі
            onMaterials[]  = {"\OpenZone_Research\models\m85_gas_analyzer\data\ozr_gas_analyzer_on.rvmat"};
            class Pump { type = "loop"; source = "ozl_work"; };    // шток: підйом 0..0,8, повернення 0,8..1
        };
    };
    // Модуль лінії Захист (M86, рішення 23.10; варіант А — користувач просив обидва варіанти, щоб
    // вибрати кращий; варіант Б, зварний кутник із двома F-струбцинами, — тестовий клас
    // OZR_Test_M86_B у тестовому аддоні): ручний гвинтовий прес-струбцина — лита П-рама в синій
    // емалі на сталевій плиті з окалиною, лапи на болтах, на траверсі порожній шильдик; гвинт Tr20
    // із воротком убік, п'ята тисне через сталеву пластину на пакет кевлару, з якого вже вирізано
    // кружок, поруч маркером обведено наступний; ~0.20 x 0.135 x 0.16. Спільний для пакувальників
    // лінії всіх фракцій (M25, M29, M34).
    class OZL_Tool_PlateClamp : OZL_Tool_Base
    {
        scope = 2;
        ozlLine = "protection";
        inventorySlot[] = {"OZL_Tool3"};    // своє місце модуля на станції
        displayName = "$STR_OZL_tool_plateclamp";
        descriptionShort = "$STR_OZL_tool_plateclamp_desc";
        model = "\OpenZone_Research\models\m86_plate_clamp\ozr_plate_clamp.p3d";
        class AnimationSources
        {
            class ozl_work
            {
                source = "user";
                animPeriod = 1.5;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            class Clamp { type = "pose"; source = "ozl_work"; };   // 0 -> 1 на початку роботи, 1 -> 0 після (як подача M16)
        };
    };

    // Проби: одна на лінію (ozlLine), спільна для всіх фракцій лінії. Бали й чистоту несе рядок у
    // предметі (OZL_Payload); моделі M47-M53. Жодних quantity-ключів: рушій зливає стек одного
    // класу, не дивлячись на скриптові поля, і рядок другої проби зник би мовчки.
    class OZL_Sample_Base : Inventory_Base
    {
        scope = 0;
        displayName = "$STR_OZL_sample";
        descriptionShort = "$STR_OZL_sample_desc";
        model = "\dz\gear\medical\InjectionVial.p3d";
        itemSize[] = {1, 1};
        weight = 60;
        soundImpactType = "plastic";
        spawnDamageRange[] = {0, 0};
        rotationFlags = 1;
    };
    // M47: проба лінії «Біо»: термопенал із хладоелементом і двома пробірками. Пенал 20,5 см
    // завдовжки — предмет 1×2, вага з гелем і пробірками.
    class OZL_Sample_Bio : OZL_Sample_Base
    {
        scope = 2;
        ozlLine = "bio";
        displayName = "$STR_OZL_sample_bio";
        descriptionShort = "$STR_OZL_sample_bio_desc";
        model = "\OpenZone_Research\models\m47_sample_bio\ozr_sample_bio.p3d";
        itemSize[] = {1, 2};
        weight = 250;
    };
    // M48: проба лінії «Аномальне»: свинцевий стакан із пломбою.
    class OZL_Sample_Anom : OZL_Sample_Base
    {
        scope = 2;
        ozlLine = "anomaly";
        displayName = "$STR_OZL_sample_anom";
        descriptionShort = "$STR_OZL_sample_anom_desc";
        model = "\OpenZone_Research\models\m48_anomaly_sample\ozr_anomaly_sample.p3d";
    };
    // M50: проба лінії «Хабар»: жерстяна банка-закрутка з дротяною пломбою.
    class OZL_Sample_Khabar : OZL_Sample_Base
    {
        scope = 2;
        ozlLine = "khabar";
        displayName = "$STR_OZL_sample_khabar";
        descriptionShort = "$STR_OZL_sample_khabar_desc";
        model = "\OpenZone_Research\models\m50_khabar_sample\ozr_khabar_sample.p3d";
    };
    // M51: проба лінії «Стежки»: складений учетверо подвійний аркуш із зошита в клітинку з картою
    // від руки. Пакет 17 × 10 см — предмет 1×2; вага — загальна.
    class OZL_Sample_Trail : OZL_Sample_Base
    {
        scope = 2;
        ozlLine = "trails";
        displayName = "$STR_OZL_sample_trail";
        descriptionShort = "$STR_OZL_sample_trail_desc";
        model = "\OpenZone_Research\models\m51_trail_sample\ozr_trail_sample.p3d";
        itemSize[] = {1, 2};
    };
    // M52: проба лінії «Балістика»: малий захисний кейс із деталями зброї в поролоні, кришка
    // відкрита. Кейс 21 × 17 см — предмет 2×2, вага з деталями.
    class OZL_Sample_Ball : OZL_Sample_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        displayName = "$STR_OZL_sample_ball";
        descriptionShort = "$STR_OZL_sample_ball_desc";
        model = "\OpenZone_Research\models\m52_ball_sample\ozr_ball_sample.p3d";
        itemSize[] = {2, 2};
        weight = 750;
    };
    // M53: проба лінії «Захист»: відстріляна титанова бронеплита й шматок арамідного пакета зі
    // слідами кігтів під гумкою. Стос 15 × 11 см — предмет 2×2; вага — плита 93 г, кевлар 39 г,
    // гумка й бирка.
    class OZL_Sample_Prot : OZL_Sample_Base
    {
        scope = 2;
        ozlLine = "protection";
        displayName = "$STR_OZL_sample_prot";
        descriptionShort = "$STR_OZL_sample_prot_desc";
        model = "\OpenZone_Research\models\m53_prot_sample\ozr_prot_sample.p3d";
        itemSize[] = {2, 2};
        weight = 140;
    };
    // M49: проба лінії «Електроніка»: антистатичний пакет із платою і биркою. Пакет 10×15 см —
    // предмет 1×2. Модель стоїть, як ванільний Paper.p3d (лист у площині X-Y, початок у центрі);
    // rotationFlags = 16, як у Paper, — кинутий пакет лягає пласко.
    class OZL_Sample_Electro : OZL_Sample_Base
    {
        scope = 2;
        ozlLine = "electronics";
        displayName = "$STR_OZL_sample_electro";
        descriptionShort = "$STR_OZL_sample_electro_desc";
        model = "\OpenZone_Research\models\m49_tech_sample\ozr_tech_sample.p3d";
        itemSize[] = {1, 2};
        rotationFlags = 16;
    };

    // Носії: результат аналізу, один на лінію (ozlLine), моделі M62-M68. Бали несе рядок у предметі
    // (OZL_Payload); тип балів -- лінія класу.
    class OZL_Carrier_Base : Inventory_Base
    {
        scope = 0;
        displayName = "$STR_OZL_carrier_unknown";
        descriptionShort = "$STR_OZL_carrier_desc";
        model = "\DZ\gear\books\Book_kniga.p3d";
        itemSize[] = {2, 2};
        weight = 300;
        spawnDamageRange[] = {0, 0};
        rotationFlags = 1;
        hiddenSelections[] = {"camoGround"};
        hiddenSelectionsTextures[] = {"dz\gear\books\data\book_kniga_co.paa"};
    };
    // Носій лінії Біо (M62): картонна папка-швидкозшивач із бланками аналізу й термострічкою
    // аналізатора гармошкою (папка 0.305 x 0.22, зі стрічкою й бантом ~0.37 x 0.27). camoGround —
    // обкладинка (лицьова, корінець, задня) у колір лінії: типово запечений зелений атлас моделі;
    // адмін може дати свою текстуру або процедурний колір "#(argb,8,8,3)color(...)". Наліпка,
    // бланки, стрічка й зав'язки до camoGround не входять.
    class OZL_Carrier_Bio : OZL_Carrier_Base
    {
        scope = 2;
        ozlLine = "bio";
        displayName = "$STR_OZL_carrier_bio";
        model = "\OpenZone_Research\models\m62_carrier_bio\ozr_carrier_bio.p3d";
        hiddenSelections[] = {"camoGround"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m62_carrier_bio\data\ozr_carrier_bio_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m62_carrier_bio\data\ozr_carrier_bio.rvmat"
        };
    };
    // Носій лінії Аномальне (M63): крафт-конверт 7 x 10" на зав'язці «ґудзик і нитка», з нього
    // наполовину висунуто спектрограму на глянцевому фотопапері 13 x 18 (конверт 0.178 x 0.254, з
    // висунутим відбитком ~0.35 x 0.20). camoGround — увесь крафт конверта (спинка, клапан, низ,
    // крайки, горловина): типово запечений атлас моделі; адмін може дати свою текстуру або
    // процедурний колір "#(argb,8,8,3)color(...)". Відбиток, бирка, ґудзики й нитка до camoGround
    // не входять.
    class OZL_Carrier_Anom : OZL_Carrier_Base
    {
        scope = 2;
        ozlLine = "anomaly";
        displayName = "$STR_OZL_carrier_anom";
        model = "\OpenZone_Research\models\m63_carrier_anom\ozr_carrier_anom.p3d";
        hiddenSelections[] = {"camoGround"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m63_carrier_anom\data\ozr_carrier_anom_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m63_carrier_anom\data\ozr_carrier_anom.rvmat"
        };
    };
    // Носій лінії Електроніка (M64): синька — схема електрична принципова на А1, складена за ГОСТ
    // 2.501 до А4 (0.297 x 0.21), зверху компакт-диск без коробки, зсунутий до кута (разом ~0.30 x
    // 0.23). camoGround — паперова наліпка диска: процедурний колір на синьці стер би саму схему.
    // Типово — запечений атлас моделі (біла наліпка з помаранчевою смугою лінії); адмін може дати
    // свою текстуру або колір "#(argb,8,8,3)color(...)".
    class OZL_Carrier_Electro : OZL_Carrier_Base
    {
        scope = 2;
        ozlLine = "electronics";
        displayName = "$STR_OZL_carrier_electro";
        model = "\OpenZone_Research\models\m64_carrier_electro\ozr_carrier_electro.p3d";
        hiddenSelections[] = {"camoGround"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m64_carrier_electro\data\ozr_carrier_electro_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m64_carrier_electro\data\ozr_carrier_electro.rvmat"
        };
    };
    // Носій лінії Хабар (M65): прейскурант скупника — пачка аркушів А5 з блокнотів у клітинку й
    // лінійку, списаних від руки стовпцями з цінами, на картонній підкладці під чорним
    // затискачем-біндером 32 мм (підкладка 0.166 x 0.232, з ручкою затискача ~0.27). camoGround —
    // підкладка (лицьова, зворот, торці) у колір лінії: типово запечений бурий атлас моделі; адмін
    // може дати свою текстуру або процедурний колір "#(argb,8,8,3)color(...)". Аркуші, затискач і
    // ручки до camoGround не входять.
    class OZL_Carrier_Khabar : OZL_Carrier_Base
    {
        scope = 2;
        ozlLine = "khabar";
        displayName = "$STR_OZL_carrier_khabar";
        model = "\OpenZone_Research\models\m65_carrier_khabar\ozr_carrier_khabar.p3d";
        hiddenSelections[] = {"camoGround"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m65_carrier_khabar\data\ozr_carrier_khabar_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m65_carrier_khabar\data\ozr_carrier_khabar.rvmat"
        };
    };
    // Носій лінії Стежки (M66): чорний пластмасовий креслярський тубус під формат А2 з рифленням
    // «ромбом» (Ø 0.09 x 0.455) і ременем-ручкою на двох хомутах; торцеву кришку знято, вона стоїть
    // поруч на шнурку, з горловини на 0.08 висунуто згорнуту кальку з картою, нанесеною тушшю (з
    // кришкою ~0.55 x 0.18). Предмет 1x3. camoGround — пластмаса тубуса (корпус, денце, хомути з
    // вушками, кришка): типово запечений атлас моделі; адмін може дати свою текстуру або
    // процедурний колір "#(argb,8,8,3)color(...)". Калька, бирка, ремінь і шнурок до camoGround не
    // входять.
    class OZL_Carrier_Trail : OZL_Carrier_Base
    {
        scope = 2;
        ozlLine = "trails";
        displayName = "$STR_OZL_carrier_trail";
        model = "\OpenZone_Research\models\m66_carrier_trail\ozr_carrier_trail.p3d";
        hiddenSelections[] = {"camoGround"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m66_carrier_trail\data\ozr_carrier_trail_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m66_carrier_trail\data\ozr_carrier_trail.rvmat"
        };
        itemSize[] = {1, 3};
    };
    // Носій лінії Балістика (M67): спортивна мішень №4 (аркуш 0.5 x 0.5) з пробоїнами, складена
    // вчетверо (~0.257 x 0.26), до неї скріпкою приколото бланк протоколу стрільби А5 з графами й
    // цифрами. camoGround — кольорова смуга по діагоналі протоколу (синя, колір лінії): типово
    // запечений атлас моделі; адмін може дати свою текстуру або процедурний колір
    // "#(argb,8,8,3)color(...)". Мішень, решта протоколу й скріпка до camoGround не входять.
    class OZL_Carrier_Ball : OZL_Carrier_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        displayName = "$STR_OZL_carrier_ball";
        model = "\OpenZone_Research\models\m67_carrier_ball\ozr_carrier_ball.p3d";
        hiddenSelections[] = {"camoGround"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m67_carrier_ball\data\ozr_carrier_ball_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m67_carrier_ball\data\ozr_carrier_ball.rvmat"
        };
    };
    // Носій лінії Захист (M68): радянський офіцерський планшет 22 x 28, розкритий на дві стулки
    // (разом із клапаном і ременем ~0.49 x 0.46): ліворуч під подряпаним целулоїдом — бланк
    // протоколу випробувань захисту А5 поверх карти, праворуч — корпус із олівцями в петлях, клапан
    // відкинуто, з горловини стирчить куточок другого аркуша. camoGround — шкіра планшета (корпус,
    // стулка з рамкою вікна, згин, клапан із замшею, хлястики, петлі олівців, кишеня): типово
    // запечений атлас моделі; адмін може дати свою текстуру або процедурний колір
    // "#(argb,8,8,3)color(...)". Вікно з протоколом, аркуші, олівці, метал і плечовий ремінь до
    // camoGround не входять.
    class OZL_Carrier_Prot : OZL_Carrier_Base
    {
        scope = 2;
        ozlLine = "protection";
        displayName = "$STR_OZL_carrier_prot";
        model = "\OpenZone_Research\models\m68_carrier_prot\ozr_carrier_prot.p3d";
        hiddenSelections[] = {"camoGround"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m68_carrier_prot\data\ozr_carrier_prot_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m68_carrier_prot\data\ozr_carrier_prot.rvmat"
        };
    };

    class OZL_StaticDevice_Base : Inventory_Base
    {
        scope = 0;
        physLayer = "item_large";
        carveNavmesh = 1;              // зомбі/ШІ обходять прилад
        heavyItem = 1;
        itemBehaviour = 0;
        rotationFlags = 2;
        slopeTolerance = 0.4;
        overrideDrawArea = "8.0";      // великі предмети інакше зникають зблизька (як Fireplace)
        forceFarBubble = "true";
        canBeDigged = 0;
        spawnDamageRange[] = {0, 0};   // копії з CE не спавняться побитими
        class DamageSystem
        {
            // прилад не руйнується: зомбі/куля/вибух не мають його ламати (канон PowerGeneratorStatic)
            class GlobalArmor
            {
                class Projectile  { class Health { damage = 0; }; class Blood { damage = 0; }; class Shock { damage = 0; }; };
                class Melee       { class Health { damage = 0; }; class Blood { damage = 0; }; class Shock { damage = 0; }; };
                class FragGrenade { class Health { damage = 0; }; class Blood { damage = 0; }; class Shock { damage = 0; }; };
            };
        };
    };
    // Пакувальник: три місця під модулі своєї лінії (OZL_Modules.AllowedOn).
    class OZL_Packer_Base : OZL_StaticDevice_Base
    {
        attachments[] = {"OZL_Tool1", "OZL_Tool2", "OZL_Tool3"};
        class GUIInventoryAttachmentsProps
        {
            class Tools
            {
                name = "$STR_OZL_slot_tool";
                description = "";
                attachmentSlots[] = {"OZL_Tool1", "OZL_Tool2", "OZL_Tool3"};
                icon = "missing";
            };
        };
    };
    // Аналізатор і термінал: модулів немає.
    class OZL_Analyzer_Base : OZL_StaticDevice_Base {};
    class OZL_Terminal_Base : OZL_StaticDevice_Base {};

    // ---- СТАНЦІЇ ФРАКЦІЙ ----
    //
    // Схема імені: OZL_<фракція>_<Pack|Proc>_<лінія> і OZL_<фракція>_Terminal.
    //   Pack (пакувальник) — сировина -> проба лінії. Карго 10x10 (рішення власника
    //     2026-08-23): у меншому не вміщалися великі входи модпака, і правило мовчки
    //     не збирало план.
    //   Proc (аналізатор)  — проба -> носій лінії; карго 4x4, проба 1x1.
    //   Terminal           — приймає носії й відкриває дерево; карго 4x4.
    // Фракцію приладу задає OZ_Research_Owners.json, а не клас: ім'я класу — лише
    // підказка адмінові. Лінію задає ozlLine.
    //
    // spawnDamageRange, physLayer=item_large, carveNavmesh і незламність приходять з
    // OZL_StaticDevice_Base — тут лише те, чим прилади різняться. Габарити в коментарях —
    // ШИРИНА x ВИСОТА x ГЛИБИНА в метрах (вісь Y у рушія — вгору).

    // ---- Вчені (ecolog) ----

    // Пакувальник біоматеріалу: бокс біологічної безпеки (модель M01, models/m01_biosafety)
    class OZL_Eco_Pack_Bio : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "bio";
        displayName = "$STR_OZL_eco_pack_bio";
        descriptionShort = "$STR_OZL_eco_pack_bio_desc";
        model = "\OpenZone_Research\models\m01_biosafety\ozr_biosafety_cabinet.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_2"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_co.paa",
            "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_co.paa",
            "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen.rvmat",
            "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet.rvmat",
            "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet.rvmat"
        };
        class AnimationSources
        {
            class ozl_arm
            {
                source = "user";
                animPeriod = 0.8;
                initPhase = 0;
            };
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        weight = 45000;
        itemSize[] = {4, 4};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_2"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_f0_co.paa",
                "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_on_co.paa",
                "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_on.rvmat",
                "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_on.rvmat",
                "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_on.rvmat"
            };
            class Screen
            {
                type = "frames";
                selection = "ozl_screen";
                period = 0.25;
                textures[] =
                {
                    "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_f0_co.paa",
                    "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_f1_co.paa",
                    "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_f2_co.paa",
                    "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_f3_co.paa",
                    "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_f4_co.paa",
                    "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_f5_co.paa",
                    "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_f6_co.paa",
                    "\OpenZone_Research\models\m01_biosafety\data\ozr_biosafety_cabinet_screen_f7_co.paa"
                };
            };
            class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.55; amp = 0.03; period = 1.9; };
            class Heat   { type = "blink";  selection = "ozl_lamp_2"; on = 0.6; off = 0.6; };
            class Press  { type = "pose";   source = "ozl_arm"; };
        };
    };

    // Біоаналізатор: біохімічний аналізатор на лабораторній тумбі (M02, models/m02_bioanalyzer)
    class OZL_Eco_Proc_Bio : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "bio";
        displayName = "$STR_OZL_eco_proc_bio";
        descriptionShort = "$STR_OZL_eco_proc_bio_desc";
        model = "\OpenZone_Research\models\m02_bioanalyzer\ozr_bioanalyzer.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_co.paa",
            "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd.rvmat",
            "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer.rvmat"
        };
        class AnimationSources
        {
            class ozl_arm
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 6;
                initPhase = 0;
            };
        };
        weight = 40000;
        itemSize[] = {3, 6};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_f0_co.paa",
                "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_on.rvmat",
                "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_on.rvmat"
            };
            class Carousel { type = "loop"; source = "ozl_work"; };
            class Arm { type = "wobble"; source = "ozl_arm"; mid = 0.5; amp = 0.5; period = 3.2; };
            class Leds { type = "blink"; selection = "ozl_lamp"; on = 0.4; off = 0.4; };
            class Display
            {
                type = "frames";
                selection = "ozl_screen";
                period = 0.5;
                textures[] =
                {
                    "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_f0_co.paa",
                    "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_f1_co.paa",
                    "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_f2_co.paa",
                    "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_f3_co.paa",
                    "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_f4_co.paa",
                    "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_f5_co.paa",
                    "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_f6_co.paa",
                    "\OpenZone_Research\models\m02_bioanalyzer\data\ozr_bioanalyzer_vfd_f7_co.paa"
                };
            };
        };
    };

    // Пакувальник аномального: радіаційний рукавичний бокс (M03, models/m03_glovebox)
    class OZL_Eco_Pack_Anom : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "anomaly";
        displayName = "$STR_OZL_eco_pack_anom";
        descriptionShort = "$STR_OZL_eco_pack_anom_desc";
        model = "\OpenZone_Research\models\m03_glovebox\ozr_glovebox.p3d";
        hiddenSelections[] = {"ozl_lamp", "ozl_lamp_work"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m03_glovebox\data\ozr_glovebox_co.paa",
            "\OpenZone_Research\models\m03_glovebox\data\ozr_glovebox_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m03_glovebox\data\ozr_glovebox.rvmat",
            "\OpenZone_Research\models\m03_glovebox\data\ozr_glovebox.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        weight = 60000;
        itemSize[] = {7, 4};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp", "ozl_lamp_work"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m03_glovebox\data\ozr_glovebox_on_co.paa",
                "\OpenZone_Research\models\m03_glovebox\data\ozr_glovebox_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m03_glovebox\data\ozr_glovebox_on.rvmat",
                "\OpenZone_Research\models\m03_glovebox\data\ozr_glovebox_on.rvmat"
            };
            class Lamp  { type = "blink";  selection = "ozl_lamp_work"; on = 0.6; off = 0.6; };
            class Gauge { type = "wobble"; source = "ozl_needle"; mid = 0.5; amp = 0.35; period = 1.3; };
        };
    };

    // Аналізатор аномального: свинцева камера лічильника зі стійкою приладів (M04,
    // models/m04_anomaly_analyzer), кришка закрита
    class OZL_Eco_Proc_Anom : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "anomaly";
        displayName = "$STR_OZL_eco_proc_anom";
        descriptionShort = "$STR_OZL_eco_proc_anom_desc";
        model = "\OpenZone_Research\models\m04_anomaly_analyzer\ozr_anomaly_analyzer.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_lamp", "ozl_lamp_blink"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_co.paa",
            "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_co.paa",
            "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_co.paa",
            "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie.rvmat",
            "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart.rvmat",
            "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer.rvmat",
            "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer.rvmat"
        };
        class AnimationSources
        {
            class ozl_lid
            {
                source = "user";
                animPeriod = 1.8;
                initPhase = 0;
            };
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_needle_2
            {
                source = "user";
                animPeriod = 1.5;
                initPhase = 0;
            };
            class ozl_pen
            {
                source = "user";
                animPeriod = 0.15;
                initPhase = 0;
            };
            class ozl_pen_2
            {
                source = "user";
                animPeriod = 0.1;
                initPhase = 0;
            };
            class ozl_pen_3
            {
                source = "user";
                animPeriod = 0.1;
                initPhase = 0;
            };
        };
        weight = 30000;
        itemSize[] = {2, 4};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_blink"};
            onTextures[]   = {"\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f0_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_on_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_on.rvmat", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_on.rvmat", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_on.rvmat"};
            class Lid    { type = "pose";   source = "ozl_lid"; };
            class Pen    { type = "wobble"; source = "ozl_pen";   mid = 0.412; amp = 0.16; period = 3.6; };
            class Pen2   { type = "wobble"; source = "ozl_pen_2"; mid = 0.5;   amp = 0.5;  period = 1.44; };
            class Pen3   { type = "wobble"; source = "ozl_pen_3"; mid = 0.5;   amp = 0.5;  period = 0.654545; };
            class Rate   { type = "wobble"; source = "ozl_needle";   mid = 0.55; amp = 0.05; period = 0.9; };
            class HV     { type = "pose";   source = "ozl_needle_2"; };
            class Count  { type = "blink";  selection = "ozl_lamp_blink"; on = 0.08; off = 0.17; };
            class Digits { type = "frames"; selection = "ozl_screen";   period = 0.22; textures[] = {
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f0_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f1_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f2_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f3_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f4_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f5_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f6_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f7_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f8_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f9_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f10_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f11_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f12_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f13_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f14_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f15_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f16_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f17_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f18_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f19_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f20_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f21_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f22_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f23_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f24_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f25_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f26_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f27_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f28_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f29_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f30_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f31_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f32_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f33_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f34_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f35_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f36_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f37_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f38_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f39_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f40_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f41_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f42_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f43_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f44_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f45_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f46_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f47_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f48_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f49_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f50_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f51_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f52_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f53_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f54_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f55_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f56_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f57_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f58_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f59_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f60_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f61_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f62_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_nixie_f63_co.paa"}; };
            class Chart  { type = "frames"; selection = "ozl_screen_2"; period = 0.07; textures[] = {
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f0_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f1_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f2_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f3_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f4_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f5_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f6_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f7_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f8_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f9_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f10_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f11_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f12_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f13_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f14_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f15_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f16_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f17_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f18_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f19_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f20_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f21_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f22_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f23_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f24_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f25_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f26_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f27_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f28_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f29_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f30_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f31_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f32_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f33_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f34_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f35_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f36_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f37_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f38_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f39_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f40_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f41_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f42_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f43_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f44_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f45_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f46_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f47_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f48_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f49_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f50_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f51_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f52_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f53_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f54_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f55_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f56_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f57_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f58_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f59_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f60_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f61_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f62_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f63_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f64_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f65_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f66_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f67_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f68_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f69_co.paa",
                "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f70_co.paa", "\OpenZone_Research\models\m04_anomaly_analyzer\data\ozr_anomaly_analyzer_chart_f71_co.paa"}; };
        };
    };

    // Пакувальник електроніки: верстат монтажника електроніки (M05, models/m05_electro_pack)
    class OZL_Eco_Pack_Electro : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "electronics";
        displayName = "$STR_OZL_eco_pack_electro";
        descriptionShort = "$STR_OZL_eco_pack_electro_desc";
        model = "\OpenZone_Research\models\m05_electro_pack\ozr_electro_pack.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_2"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_co.paa",
            "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_co.paa",
            "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen.rvmat",
            "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack.rvmat",
            "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle_a
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_needle_v
            {
                source = "user";
                animPeriod = 0.3;
                initPhase = 0;
            };
        };
        weight = 50000;
        itemSize[] = {4, 5};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_2"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_f0_co.paa",
                "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_on_co.paa",
                "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_on.rvmat",
                "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_on.rvmat",
                "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_on.rvmat"
            };
            class NeedleV { type = "wobble"; source = "ozl_needle_v"; mid = 0.42; amp = 0.012; period = 2.3; };
            class NeedleA { type = "wobble"; source = "ozl_needle_a"; mid = 0.21; amp = 0.045; period = 0.65; };
            class Led { type = "blink"; selection = "ozl_lamp_2"; on = 0.12; off = 0.9; };
            class Eop
            {
                type = "frames";
                selection = "ozl_screen";
                period = 0.09;
                textures[] =
                {
                    "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_f0_co.paa",
                    "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_f1_co.paa",
                    "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_f2_co.paa",
                    "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_f3_co.paa",
                    "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_f4_co.paa",
                    "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_f5_co.paa",
                    "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_f6_co.paa",
                    "\OpenZone_Research\models\m05_electro_pack\data\ozr_electro_pack_screen_f7_co.paa"
                };
            };
        };
    };

    // Аналізатор електроніки: вимірювальна стійка приладів (M06, models/m06_electro_proc).
    // Екрани й лампи — секції ozl_screen / ozl_lamp, типовий вигляд — ВИМКНЕНО; робочий —
    // ozr_electro_proc_on_co.paa і ozr_electro_proc_on.rvmat через SetObjectTexture /
    // SetObjectMaterial. Перо самописця рухає джерело ozl_work. Кожна прихована секція
    // мусить мати текстуру, інакше рушій малює її порожньою.
    class OZL_Eco_Proc_Electro : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "electronics";
        displayName = "$STR_OZL_eco_proc_electro";
        descriptionShort = "$STR_OZL_eco_proc_electro_desc";
        model = "\OpenZone_Research\models\m06_electro_proc\ozr_electro_proc.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_screen_3", "ozl_lamp", "ozl_lamp_2", "ozl_screen_4"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_co.paa",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_co.paa",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_co.paa",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_co.paa",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_co.paa",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt.rvmat",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2.rvmat",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led.rvmat",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc.rvmat",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc.rvmat",
            "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_needle_2
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_pen
            {
                source = "user";
                animPeriod = 0.15;
                initPhase = 0;
            };
            class ozl_pen_2
            {
                source = "user";
                animPeriod = 0.1;
                initPhase = 0;
            };
            class ozl_pen_3
            {
                source = "user";
                animPeriod = 0.1;
                initPhase = 0;
            };
        };
        weight = 90000;
        itemSize[] = {3, 8};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_screen_3", "ozl_lamp", "ozl_lamp_2"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f0_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f0_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_f0_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_on_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_on.rvmat",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_on.rvmat",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_on.rvmat",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_on.rvmat",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_on.rvmat"
            };
            // кадри: ..._crt_f0_co.paa ... _crt_f11_co.paa, _crt2_f0..f11, _led_f0..f7, _chart_f0..f71 (тека та сама)
            class Scope   { type = "frames"; selection = "ozl_screen";   period = 0.09; textures[] = {
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f0_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f1_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f2_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f3_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f4_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f5_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f6_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f7_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f8_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f9_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f10_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt_f11_co.paa"}; };
            class Scope2  { type = "frames"; selection = "ozl_screen_2"; period = 0.10; textures[] = {
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f0_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f1_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f2_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f3_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f4_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f5_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f6_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f7_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f8_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f9_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f10_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_crt2_f11_co.paa"}; };
            class Counter { type = "frames"; selection = "ozl_screen_3"; period = 0.5;  textures[] = {
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_f0_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_f1_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_f2_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_f3_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_f4_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_f5_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_f6_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_led_f7_co.paa"}; };
            class Gate    { type = "blink";  selection = "ozl_lamp_2"; on = 0.15; off = 0.35; };
            class Volt    { type = "wobble"; source = "ozl_needle";   mid = 0.62; amp = 0.08;  period = 1.9; };
            class Gen     { type = "wobble"; source = "ozl_needle_2"; mid = 0.55; amp = 0.025; period = 3.1; };
            class Chart   { type = "frames"; selection = "ozl_screen_4"; period = 0.07; textures[] = {
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f0_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f1_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f2_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f3_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f4_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f5_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f6_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f7_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f8_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f9_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f10_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f11_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f12_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f13_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f14_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f15_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f16_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f17_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f18_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f19_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f20_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f21_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f22_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f23_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f24_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f25_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f26_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f27_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f28_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f29_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f30_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f31_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f32_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f33_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f34_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f35_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f36_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f37_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f38_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f39_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f40_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f41_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f42_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f43_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f44_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f45_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f46_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f47_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f48_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f49_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f50_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f51_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f52_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f53_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f54_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f55_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f56_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f57_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f58_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f59_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f60_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f61_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f62_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f63_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f64_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f65_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f66_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f67_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f68_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f69_co.paa",
                "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f70_co.paa", "\OpenZone_Research\models\m06_electro_proc\data\ozr_electro_proc_chart_f71_co.paa"}; };
            class Pen     { type = "wobble"; source = "ozl_pen";   mid = 0.432; amp = 0.128; period = 7.2; };
            class Pen2    { type = "wobble"; source = "ozl_pen_2"; mid = 0.5;   amp = 0.5;   period = 1.44; };
            class Pen3    { type = "wobble"; source = "ozl_pen_3"; mid = 0.5;   amp = 0.5;   period = 0.6; };
        };
    };
    // Термінал Вчених (M38, рішення 23.10): свій клас замість спільного OZL_LabComputer
    class OZL_Eco_Terminal : OZL_Terminal_Base
    {
        scope = 2;
        displayName = "$STR_OZL_eco_terminal";
        descriptionShort = "$STR_OZL_eco_terminal_desc";
        model = "\OpenZone_Research\models\m38_eco_terminal\ozr_eco_terminal.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp_work", "ozl_lamp_blink"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_co.paa",
            "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_co.paa",
            "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen.rvmat",
            "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal.rvmat",
            "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal.rvmat"
        };
        class AnimationSources
        {
            class ozl_head
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 3;
                initPhase = 0;
            };
        };
        weight = 150000;
        itemSize[] = {10, 9};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Термінал завжди «в роботі», стану спокою немає (відгук користувача 28.10: «у ВСІХ терміналів має
        // бути один стан „в роботі“»): клієнт крутить class OZL_Work весь час (OZL_Station.OZL_WorkFxOn)
        ozlWorkFxAlways = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp_work", "ozl_lamp_blink"};
            onTextures[]   = {"\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f0_co.paa", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_on_co.paa", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_on.rvmat", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_on.rvmat", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_on.rvmat"};
            class Reels  { type = "loop";   source = "ozl_work"; };
            class Head   { type = "wobble"; source = "ozl_head"; mid = 0.5; amp = 0.5; period = 1.6; };
            class Lamps  { type = "blink";  selection = "ozl_lamp_blink"; on = 0.38; off = 0.28; };
            class Screen { type = "frames"; selection = "ozl_screen"; period = 0.19;
                           textures[] = {
                               "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f0_co.paa", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f1_co.paa",
                               "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f2_co.paa", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f3_co.paa",
                               "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f4_co.paa", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f5_co.paa",
                               "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f6_co.paa", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f7_co.paa",
                               "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f8_co.paa", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f9_co.paa",
                               "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f10_co.paa", "\OpenZone_Research\models\m38_eco_terminal\data\ozr_eco_terminal_screen_f11_co.paa"}; };
        };
    };

    // ---- Чисте небо (clearsky) ----

    // Пакувальник біоматеріалу: морозильна скриня з плівковим ізолятором на кришці (M07,
    // models/m07_sky_pack_bio), 1.50 x 0.86 x 0.68, з ковпаком 1.55 заввишки. Табло термометра й
    // лампа компресора — секції ozl_screen / ozl_lamp_work (типово ВИМКНЕНО), лопаті вентилятора
    // крутить джерело ozl_work. Модулі видно на полиці на лівому торці (проксі ozl_tool1..3).
    class OZL_Sky_Pack_Bio : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "bio";
        displayName = "$STR_OZL_sky_pack_bio";
        descriptionShort = "$STR_OZL_sky_pack_bio_desc";
        model = "\OpenZone_Research\models\m07_sky_pack_bio\ozr_sky_pack_bio.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp_work", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen_co.paa",
            "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_co.paa",
            "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen.rvmat",
            "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio.rvmat",
            "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio.rvmat"
        };
        class AnimationSources
        {
            class ozl_work
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
        };
        weight = 55000;
        itemSize[] = {8, 5};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp_work", "ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen_f0_co.paa", "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_on_co.paa", "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen_on.rvmat", "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_on.rvmat", "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_on.rvmat"};
            class Fan  { type = "loop";  source = "ozl_work"; };
            class Lamp { type = "blink"; selection = "ozl_lamp"; on = 0.6; off = 0.6; };
            class Lcd
            {
                type = "frames"; selection = "ozl_screen"; period = 0.5;
                textures[] = {"\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen_f0_co.paa", "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen_f1_co.paa",
                              "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen_f2_co.paa", "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen_f3_co.paa",
                              "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen_f4_co.paa", "\OpenZone_Research\models\m07_sky_pack_bio\data\ozr_sky_pack_bio_screen_f5_co.paa"};
            };
        };
    };

    // Біоаналізатор: польовий автоклав (M08, models/m08_sky_proc_bio) — скороварка з манометром на
    // двоконфорковій плитці та фотоколориметр КФК-2 на дерев'яних ящиках, 1.05 x 1.13 x 0.48.
    // Спіралі конфорок і лампа плитки — ozl_lamp_work, вікно шкали КФК-2 — ozl_screen (типово
    // ВИМКНЕНО), стрілку манометра крутить джерело ozl_work (0 — на нулі).
    class OZL_Sky_Proc_Bio : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "bio";
        displayName = "$STR_OZL_sky_proc_bio";
        descriptionShort = "$STR_OZL_sky_proc_bio_desc";
        model = "\OpenZone_Research\models\m08_sky_proc_bio\ozr_sky_proc_bio.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp_work"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m08_sky_proc_bio\data\ozr_sky_proc_bio_co.paa",
            "\OpenZone_Research\models\m08_sky_proc_bio\data\ozr_sky_proc_bio_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m08_sky_proc_bio\data\ozr_sky_proc_bio.rvmat",
            "\OpenZone_Research\models\m08_sky_proc_bio\data\ozr_sky_proc_bio.rvmat"
        };
        class AnimationSources
        {
            class ozl_meter
            {
                source = "user";
                animPeriod = 1.5;
                initPhase = 0;
            };
            class ozl_needle
            {
                source = "user";
                animPeriod = 3;
                initPhase = 0;
            };
            class ozl_weight
            {
                source = "user";
                animPeriod = 0.1;
                initPhase = 0;
            };
        };
        weight = 45000;
        itemSize[] = {2, 3};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp_work"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m08_sky_proc_bio\data\ozr_sky_proc_bio_on_co.paa",
                "\OpenZone_Research\models\m08_sky_proc_bio\data\ozr_sky_proc_bio_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m08_sky_proc_bio\data\ozr_sky_proc_bio_on.rvmat",
                "\OpenZone_Research\models\m08_sky_proc_bio\data\ozr_sky_proc_bio_on.rvmat"
            };
            class Gauge  { type = "wobble"; source = "ozl_needle"; mid = 0.27; amp = 0.02;  period = 2.3; };
            class Weight { type = "wobble"; source = "ozl_weight"; mid = 0.5;  amp = 0.5;   period = 0.5; };
            class Meter  { type = "wobble"; source = "ozl_meter";  mid = 0.62; amp = 0.012; period = 3.1; };
        };
    };

    // Пакувальник аномального: металева шафа-контейнер (0.40 x 1.90 x 0.55)
    class OZL_Sky_Pack_Anom : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "anomaly";
        displayName = "$STR_OZL_sky_pack_anom";
        descriptionShort = "$STR_OZL_sky_pack_anom_desc";
        model = "\OpenZone_Research\models\m09_sky_pack_anom\ozr_sky_pack_anom.p3d";
        hiddenSelections[] = {"ozl_lamp", "ozl_light"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m09_sky_pack_anom\data\ozr_sky_pack_anom_co.paa",
            "\OpenZone_Research\models\m09_sky_pack_anom\data\ozr_sky_pack_anom_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m09_sky_pack_anom\data\ozr_sky_pack_anom.rvmat",
            "\OpenZone_Research\models\m09_sky_pack_anom\data\ozr_sky_pack_anom.rvmat"
        };
        class AnimationSources
        {
            class ozl_arm
            {
                source = "user";
                animPeriod = 1.5;
                initPhase = 0;
            };
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        weight = 50000;
        itemSize[] = {2, 8};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_light", "ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m09_sky_pack_anom\data\ozr_sky_pack_anom_on_co.paa",
                              "\OpenZone_Research\models\m09_sky_pack_anom\data\ozr_sky_pack_anom_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m09_sky_pack_anom\data\ozr_sky_pack_anom_on.rvmat",
                              "\OpenZone_Research\models\m09_sky_pack_anom\data\ozr_sky_pack_anom_on.rvmat"};
            class Lamp   { type = "blink";  selection = "ozl_lamp"; on = 0.5; off = 0.5; };
            class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.6; amp = 0.07; period = 2.3; };
            class Arm    { type = "pose";   source = "ozl_arm"; };
        };
    };

    // Аналізатор аномального: центрифуга з пральної машини (M10, models/m10_sky_proc_anom) —
    // двобакова «Сибір-5» (675 x 700 x 375) без задньої стінки на ящику, кришка центрифуги
    // відкинута, в барабані ротор із пробами; саморобний блок детектора з мікроамперметром,
    // антена, дозиметр; 0.72 x 1.40 x 0.42. Шкала приладу — ozl_screen, лампа блока —
    // ozl_lamp_work (типово ВИМКНЕНО); барабан і стрілку крутить джерело ozl_work (0 — стоїть).
    class OZL_Sky_Proc_Anom : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "anomaly";
        displayName = "$STR_OZL_sky_proc_anom";
        descriptionShort = "$STR_OZL_sky_proc_anom_desc";
        model = "\OpenZone_Research\models\m10_sky_proc_anom\ozr_sky_proc_anom.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp_work", "ozl_lcd"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_co.paa",
            "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_co.paa",
            "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom.rvmat",
            "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom.rvmat",
            "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd.rvmat"
        };
        class AnimationSources
        {
            class ozl_meter
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_pose
            {
                source = "user";
                animPeriod = 0.5;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
        };
        weight = 60000;
        itemSize[] = {3, 5};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp_work", "ozl_lcd"};
            onTextures[]   = {"\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_on_co.paa", "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_on_co.paa", "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_f0_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_on.rvmat", "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_on.rvmat", "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_on.rvmat"};
            class Drum   { type = "loop";   source = "ozl_work"; };
            class Needle { type = "wobble"; source = "ozl_meter"; mid = 0.62; amp = 0.07; period = 1.3; };
            class Count  { type = "blink";  selection = "ozl_lamp_work"; on = 0.08; off = 0.32; };
            class Lcd    { type = "frames"; selection = "ozl_lcd"; period = 0.6;
                           textures[] = {"\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_f0_co.paa", "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_f1_co.paa",
                                         "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_f2_co.paa", "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_f3_co.paa",
                                         "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_f4_co.paa", "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_f5_co.paa",
                                         "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_f6_co.paa", "\OpenZone_Research\models\m10_sky_proc_anom\data\ozr_sky_proc_anom_lcd_f7_co.paa"}; };
            class Start  { type = "pose";   source = "ozl_pose"; };
        };
    };

    // Пакувальник електроніки: польовий монтажний стіл (M11, models/m11_sky_pack_electro) —
    // сталевий стіл монтажника з тумбою, перефарбований у блакитний, зверху дошки; лещата,
    // розібрані ПНВ і ліхтарі, мультиметр, паяльник і лампа-переноска від автомобільного
    // акумулятора під столом, брезент; 1.60 x 1.57 x 0.72. Лампа — ozl_lamp, табло
    // мультиметра — ozl_screen (типово ВИМКНЕНО); модулі — на полиці надбудови.
    class OZL_Sky_Pack_Electro : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "electronics";
        displayName = "$STR_OZL_sky_pack_electro";
        descriptionShort = "$STR_OZL_sky_pack_electro_desc";
        model = "\OpenZone_Research\models\m11_sky_pack_electro\ozr_sky_pack_electro.p3d";
        hiddenSelections[] = {"ozl_lamp", "ozl_screen"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_co.paa",
            "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro.rvmat",
            "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_toggle
            {
                source = "user";
                animPeriod = 0.15;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
        };
        weight = 50000;
        itemSize[] = {7, 3};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd_f0_co.paa",
                "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd_on.rvmat",
                "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_on.rvmat"
            };
            class Fan    { type = "loop";   source = "ozl_work"; };
            class Volt   { type = "wobble"; source = "ozl_needle"; mid = 0.575; amp = 0.012; period = 1.3; };
            class Toggle { type = "pose";   source = "ozl_toggle"; };
            class Lcd
            {
                type = "frames";
                selection = "ozl_screen";
                period = 0.45;
                textures[] =
                {
                    "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd_f0_co.paa",
                    "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd_f1_co.paa",
                    "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd_f2_co.paa",
                    "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd_f3_co.paa",
                    "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd_f4_co.paa",
                    "\OpenZone_Research\models\m11_sky_pack_electro\data\ozr_sky_pack_electro_lcd_f5_co.paa"
                };
            };
        };
    };

    // Аналізатор електроніки: свердлильний верстат (0.76 x 0.83 x 0.41)
    class OZL_Sky_Proc_Electro : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "electronics";
        displayName = "$STR_OZL_sky_proc_electro";
        descriptionShort = "$STR_OZL_sky_proc_electro_desc";
        model = "\OpenZone_Research\models\m12_sky_proc_electro\ozr_sky_proc_electro.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_blink"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_co.paa",
            "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_co.paa",
            "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt.rvmat",
            "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro.rvmat",
            "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        weight = 40000;
        itemSize[] = {3, 3};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_blink"};
            onTextures[]   = {"\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f0_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_on_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_on.rvmat", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_on.rvmat", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_on.rvmat"};
            class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.55; amp = 0.05; period = 1.1; };
            class Leds   { type = "blink";  selection = "ozl_lamp_blink"; on = 0.4; off = 0.4; };
            class Scope  { type = "frames"; selection = "ozl_screen"; period = 0.05;
                           textures[] = {"\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f0_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f1_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f2_co.paa",
                           "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f3_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f4_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f5_co.paa",
                           "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f6_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f7_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f8_co.paa",
                           "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f9_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f10_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f11_co.paa",
                           "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f12_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f13_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f14_co.paa",
                           "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f15_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f16_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f17_co.paa",
                           "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f18_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f19_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f20_co.paa",
                           "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f21_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f22_co.paa", "\OpenZone_Research\models\m12_sky_proc_electro\data\ozr_sky_proc_electro_crt_f23_co.paa"}; };
        };
    };

    // Термінал ЧН: польовий штаб — стіл із дошок на ящиках, відкритий ноутбук і радіостанція, щогла на
    // розтяжках (стіл 1.60 x 0.80, дошки на 0.75, щогла до 2.30; новий клас, M60, рішення 23.10 замість
    // хімстенда). Екран ноутбука й лампа радіостанції — секції ozl_screen / ozl_lamp_work (типово ВИМКНЕНО).
    class OZL_Sky_Terminal : OZL_Terminal_Base
    {
        scope = 2;
        displayName = "$STR_OZL_sky_terminal";
        descriptionShort = "$STR_OZL_sky_terminal_desc";
        model = "\OpenZone_Research\models\m60_sky_terminal\ozr_sky_terminal.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_work"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_co.paa",
            "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_co.paa",
            "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen.rvmat",
            "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal.rvmat",
            "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal.rvmat"
        };
        weight = 60000;
        itemSize[] = {7, 4};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Термінал завжди «в роботі», стану спокою немає (відгук користувача 28.10: «у ВСІХ терміналів має
        // бути один стан „в роботі“»): клієнт крутить class OZL_Work весь час (OZL_Station.OZL_WorkFxOn)
        ozlWorkFxAlways = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_work"};
            onTextures[]   = {"\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f0_co.paa", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_on_co.paa", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_on.rvmat", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_on.rvmat", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_on.rvmat"};
            class Tx     { type = "blink";  selection = "ozl_lamp_work"; on = 0.44; off = 0.24; };
            class Screen { type = "frames"; selection = "ozl_screen"; period = 0.24;
                           textures[] = {
                               "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f0_co.paa", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f1_co.paa",
                               "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f2_co.paa", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f3_co.paa",
                               "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f4_co.paa", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f5_co.paa",
                               "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f6_co.paa", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f7_co.paa",
                               "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f8_co.paa", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f9_co.paa",
                               "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f10_co.paa", "\OpenZone_Research\models\m60_sky_terminal\data\ozr_sky_terminal_screen_f11_co.paa"}; };
        };
    };

    // ---- Бандити (bandit) ----

    // Пакувальник хабару Бандитів: свинцева скриня (M13, models/m13_bnd_pack_khabar) — ларь-морозильник
    // (1500 x 860 x 680), обшитий кривими свинцовими листами на заклепках, з ланцюгом і амбарним
    // замком; на кришці дозиметр (ozl_screen — табло) і три місця під модулі з проксі ozl_tool1..3
    // (слоти OZL_Tool1..3 — у OZL_StaticDevice_Base), поруч хабар
    class OZL_Bnd_Pack_Khabar : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "khabar";
        displayName = "$STR_OZL_bnd_pack_khabar";
        descriptionShort = "$STR_OZL_bnd_pack_khabar_desc";
        model = "\OpenZone_Research\models\m13_bnd_pack_khabar\ozr_bnd_pack_khabar.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_co.paa",
            "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen.rvmat",
            "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar.rvmat"
        };
        weight = 55000;
        itemSize[] = {8, 5};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_f0_co.paa", "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_on.rvmat", "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_on.rvmat"};
            class Led { type = "blink"; selection = "ozl_lamp"; on = 0.15; off = 0.55; };
            class Pager
            {
                type = "frames"; selection = "ozl_screen"; period = 0.35;
                textures[] = {"\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_f0_co.paa", "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_f1_co.paa",
                              "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_f2_co.paa", "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_f3_co.paa",
                              "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_f4_co.paa", "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_f5_co.paa",
                              "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_f6_co.paa", "\OpenZone_Research\models\m13_bnd_pack_khabar\data\ozr_bnd_pack_khabar_screen_f7_co.paa"};
            };
        };
    };

    // Аналізатор хабару Бандитів: магазинні підлогові ваги (0.41 x 0.97 x 0.80)
    class OZL_Bnd_Proc_Khabar : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "khabar";
        displayName = "$STR_OZL_bnd_proc_khabar";
        descriptionShort = "$STR_OZL_bnd_proc_khabar_desc";
        model = "\OpenZone_Research\models\m14_bnd_proc_khabar\ozr_bnd_proc_khabar.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_screen_2"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_co.paa",
            "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd.rvmat",
            "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_weigh
            {
                source = "user";
                animPeriod = 1.8;
                initPhase = 0;
            };
        };
        weight = 30000;
        itemSize[] = {2, 4};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen"};
            onTextures[]   = {"\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_f0_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_on.rvmat"};
            class Weigh  { type = "pose";   source = "ozl_weigh"; };
            class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.5; amp = 0.5; period = 1.7; };
            class Dose   { type = "frames"; selection = "ozl_screen";   period = 0.48;
                           textures[] = {
                               "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_f0_co.paa", "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_f1_co.paa",
                               "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_f2_co.paa", "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_f3_co.paa",
                               "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_f4_co.paa", "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_f5_co.paa",
                               "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_f6_co.paa", "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_lcd_f7_co.paa"}; };
            class Calc   { type = "frames"; selection = "ozl_screen_2"; period = 0.43;
                           textures[] = {
                               "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f0_co.paa", "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f1_co.paa",
                               "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f2_co.paa", "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f3_co.paa",
                               "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f4_co.paa", "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f5_co.paa",
                               "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f6_co.paa", "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f7_co.paa",
                               "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f8_co.paa", "\OpenZone_Research\models\m14_bnd_proc_khabar\data\ozr_bnd_proc_khabar_calc_f9_co.paa"}; };
        };
    };

    // Пакувальник стежок Бандитів: стіл навідника (M15, models/m15_bnd_pack_trail) — верстак Б1
    // (1600 x 1500 x 720) з дошкою, пофарбований брудно-чорним; на щиті мапа з булавками і червоними
    // нитками, на столі папери, КПК, флешки, болти-маркери; ozl_lamp — світильник під полицею,
    // ozl_screen — екрани КПК і пейджера; три місця під модулі на краю полиці з проксі ozl_tool1..3
    class OZL_Bnd_Pack_Trail : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "trails";
        displayName = "$STR_OZL_bnd_pack_trail";
        descriptionShort = "$STR_OZL_bnd_pack_trail_desc";
        model = "\OpenZone_Research\models\m15_bnd_pack_trail\ozr_bnd_pack_trail.p3d";
        hiddenSelections[] = {"ozl_lamp", "ozl_screen", "ozl_lamp_2"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_co.paa",
            "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_co.paa",
            "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail.rvmat",
            "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager.rvmat",
            "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail.rvmat"
        };
        class AnimationSources
        {
            class ozl_keys
            {
                source = "user";
                animPeriod = 0.15;
                initPhase = 0;
            };
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 6;
                initPhase = 0;
            };
        };
        weight = 50000;
        itemSize[] = {7, 3};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_2"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_f0_co.paa",
                "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_on_co.paa",
                "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_on.rvmat",
                "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_on.rvmat",
                "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_on.rvmat"
            };
            class Reels { type = "loop";   source = "ozl_work"; };
            class Vu    { type = "wobble"; source = "ozl_needle"; mid = 0.55; amp = 0.15; period = 0.45; };
            class Keys  { type = "pose";   source = "ozl_keys"; };
            class Led   { type = "blink";  selection = "ozl_lamp_2"; on = 0.15; off = 0.85; };
            class Pager
            {
                type = "frames";
                selection = "ozl_screen";
                period = 0.4;
                textures[] =
                {
                    "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_f0_co.paa",
                    "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_f1_co.paa",
                    "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_f2_co.paa",
                    "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_f3_co.paa",
                    "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_f4_co.paa",
                    "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_f5_co.paa",
                    "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_f6_co.paa",
                    "\OpenZone_Research\models\m15_bnd_pack_trail\data\ozr_bnd_pack_trail_pager_f7_co.paa"
                };
            };
        };
    };

    // Аналізатор стежок Бандитів: свердлильний верстат (0.76 x 0.83 x 0.41; без View/FireGeometry — тимчасово)
    class OZL_Bnd_Proc_Trail : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "trails";
        displayName = "$STR_OZL_bnd_proc_trail";
        descriptionShort = "$STR_OZL_bnd_proc_trail_desc";
        model = "\OpenZone_Research\models\m16_bnd_proc_trail\ozr_bnd_proc_trail.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_co.paa",
            "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen.rvmat",
            "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail.rvmat"
        };
        class AnimationSources
        {
            class ozl_feed
            {
                source = "user";
                animPeriod = 1.6;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
        };
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp"};
            onTextures[] = {"\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f0_co.paa", "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_on_co.paa"};
            onMaterials[] = {"\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_on.rvmat", "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_on.rvmat"};
            class Spindle { type = "loop"; source = "ozl_work"; };
            class Feed { type = "pose"; source = "ozl_feed"; };
            class Leds { type = "blink"; selection = "ozl_lamp"; on = 0.35; off = 0.25; };
            class Screen
            {
                type = "frames";
                selection = "ozl_screen";
                period = 0.12;
                textures[] =
                {
                    "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f0_co.paa", "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f1_co.paa",
                    "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f2_co.paa", "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f3_co.paa",
                    "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f4_co.paa", "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f5_co.paa",
                    "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f6_co.paa", "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f7_co.paa",
                    "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f8_co.paa", "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f9_co.paa",
                    "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f10_co.paa", "\OpenZone_Research\models\m16_bnd_proc_trail\data\ozr_bnd_proc_trail_screen_f11_co.paa"
                };
            };
        };
        weight = 40000;
        itemSize[] = {3, 3};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
    };

    // Термінал Бандитів: віконце обмінника (1,80 x 2,10 x 1,40, лоток касира, темне броньоване скло)
    class OZL_Bnd_Terminal : OZL_Terminal_Base
    {
        scope = 2;
        displayName = "$STR_OZL_bnd_terminal";
        descriptionShort = "$STR_OZL_bnd_terminal_desc";
        model = "\OpenZone_Research\models\m17_bnd_terminal\ozr_bnd_terminal.p3d";
        hiddenSelections[] = {"ozl_lamp_work", "ozl_glass", "ozl_screen"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_co.paa",
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_co.paa",
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal.rvmat",
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal.rvmat",
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen.rvmat"
        };
        class AnimationSources
        {
            class ozl_work
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
        };
        weight = 70000;
        itemSize[] = {8, 6};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Термінал завжди «в роботі», стану спокою немає (відгук користувача 28.10: «у ВСІХ терміналів має
        // бути один стан „в роботі“»): клієнт крутить class OZL_Work весь час (OZL_Station.OZL_WorkFxOn)
        ozlWorkFxAlways = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp_work", "ozl_screen"};
            onTextures[]   = {"\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_on_co.paa", "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f0_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_on.rvmat", "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_on.rvmat"};
            class Fan   { type = "loop";   source = "ozl_work"; };
            class Board { type = "frames"; selection = "ozl_screen"; period = 0.24;
                          textures[] = {
                              "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f0_co.paa", "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f1_co.paa",
                              "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f2_co.paa", "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f3_co.paa",
                              "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f4_co.paa", "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f5_co.paa",
                              "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f6_co.paa", "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f7_co.paa",
                              "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f8_co.paa", "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f9_co.paa",
                              "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f10_co.paa", "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_screen_f11_co.paa"}; };
        };
    };

    // Те саме віконце, скло зафарбоване зсередини: підмінена лише текстура виділення ozl_glass.
    // Термінал шукається через IsKindOf (OZL_Match), тож клас працює як OZL_Bnd_Terminal.
    class OZL_Bnd_Terminal_Painted : OZL_Bnd_Terminal
    {
        displayName = "$STR_OZL_bnd_terminal_painted";
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_co.paa",
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_painted_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal.rvmat",
            "\OpenZone_Research\models\m17_bnd_terminal\data\ozr_bnd_terminal_painted.rvmat"
        };
    };


    // ---- Нейтрали (neutral) ----

    // Пакувальник хабару Нейтралів: вогнетривкий сейф бармена (0.76 x 1.40 x 0.43, модулі на даху)
    class OZL_Lnr_Pack_Khabar : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "khabar";
        displayName = "$STR_OZL_lnr_pack_khabar";
        descriptionShort = "$STR_OZL_lnr_pack_khabar_desc";
        model = "\OpenZone_Research\models\m18_lnr_pack_khabar\ozr_lnr_pack_khabar.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m18_lnr_pack_khabar\data\ozr_lnr_pack_khabar_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m18_lnr_pack_khabar\data\ozr_lnr_pack_khabar.rvmat"
        };
        class AnimationSources
        {
            class ozl_wheel
            {
                source = "user";
                animPeriod = 1.2;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 0.25;
                initPhase = 0;
            };
        };
        weight = 50000;
        itemSize[] = {2, 8};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m18_lnr_pack_khabar\data\ozr_lnr_pack_khabar_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m18_lnr_pack_khabar\data\ozr_lnr_pack_khabar_on.rvmat"};
            class Dial  { type = "wobble"; source = "ozl_work"; mid = 0.12; amp = 0.09; period = 2.6; };
            class Wheel { type = "pose";   source = "ozl_wheel"; };
        };
    };

    // Аналізатор хабару Нейтралів: пральна машина (0.81 x 1.19 x 0.65)
    class OZL_Lnr_Proc_Khabar : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "khabar";
        displayName = "$STR_OZL_lnr_proc_khabar";
        descriptionShort = "$STR_OZL_lnr_proc_khabar_desc";
        model = "\OpenZone_Research\models\m19_lnr_proc_khabar\ozr_lnr_proc_khabar.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_co.paa",
            "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen.rvmat",
            "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 3;
                initPhase = 0;
            };
        };
        weight = 60000;
        itemSize[] = {3, 5};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f0_co.paa", "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_on.rvmat", "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_on.rvmat"};
            class Antenna { type = "loop";   source = "ozl_work"; };
            class Needle  { type = "wobble"; source = "ozl_needle"; mid = 0.55; amp = 0.08; period = 1.7; };
            class Count   { type = "blink";  selection = "ozl_lamp"; on = 0.08; off = 0.40; };
            class Trace   { type = "frames"; selection = "ozl_screen"; period = 0.1;
                            textures[] = {"\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f0_co.paa", "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f1_co.paa",
                                          "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f2_co.paa", "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f3_co.paa",
                                          "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f4_co.paa", "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f5_co.paa",
                                          "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f6_co.paa", "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f7_co.paa",
                                          "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f8_co.paa", "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f9_co.paa",
                                          "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f10_co.paa", "\OpenZone_Research\models\m19_lnr_proc_khabar\data\ozr_lnr_proc_khabar_screen_f11_co.paa"}; };
        };
    };

    // Пакувальник стежок Нейтралів: відкрита шкільна шафа (0.92 x 1.18 x 0.94)
    class OZL_Lnr_Pack_Trail : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "trails";
        displayName = "$STR_OZL_lnr_pack_trail";
        descriptionShort = "$STR_OZL_lnr_pack_trail_desc";
        model = "\OpenZone_Research\models\m20_lnr_pack_trail\ozr_lnr_pack_trail.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m20_lnr_pack_trail\data\ozr_lnr_pack_trail_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m20_lnr_pack_trail\data\ozr_lnr_pack_trail.rvmat"
        };
        weight = 50000;
        itemSize[] = {4, 5};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m20_lnr_pack_trail\data\ozr_lnr_pack_trail_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m20_lnr_pack_trail\data\ozr_lnr_pack_trail_on.rvmat"};
        };
    };

    // Аналізатор стежок Нейтралів: одиночна радарна стійка (0.77 x 1.99 x 0.66)
    class OZL_Lnr_Proc_Trail : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "trails";
        displayName = "$STR_OZL_lnr_proc_trail";
        descriptionShort = "$STR_OZL_lnr_proc_trail_desc";
        model = "\OpenZone_Research\models\m21_lnr_proc_trail\ozr_lnr_proc_trail.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_screen_3", "ozl_screen_4", "ozl_lamp", "ozl_lamp_2"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_co.paa",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf_co.paa",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_co.paa",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_co.paa",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_co.paa",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7.rvmat",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf.rvmat",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd.rvmat",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda.rvmat",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail.rvmat",
            "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_needle_2
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_needle_3
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_tune
            {
                source = "user";
                animPeriod = 0.5;
                initPhase = 0;
            };
        };
        weight = 90000;
        itemSize[] = {3, 8};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_screen_3", "ozl_screen_4", "ozl_lamp", "ozl_lamp_2"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_f0_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf_f0_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_f0_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f0_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_on_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_on.rvmat",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf_on.rvmat",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_on.rvmat",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_on.rvmat",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_on.rvmat",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_on.rvmat"
            };
            // кадри: ..._vfd7_f0_co.paa ... _vfd7_f7_co.paa, _vfdf_f0..f5, _lcd_f0..f7, _pda_f0..f11 (тека та сама)
            class Scan    { type = "frames"; selection = "ozl_screen";   period = 0.30; textures[] = {
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_f0_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_f1_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_f2_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_f3_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_f4_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_f5_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_f6_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfd7_f7_co.paa"}; };
            class Tune    { type = "frames"; selection = "ozl_screen_2"; period = 0.50; textures[] = {
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf_f0_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf_f1_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf_f2_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf_f3_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf_f4_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_vfdf_f5_co.paa"}; };
            class Search  { type = "frames"; selection = "ozl_screen_3"; period = 0.25; textures[] = {
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_f0_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_f1_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_f2_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_f3_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_f4_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_f5_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_f6_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_lcd_f7_co.paa"}; };
            class Water   { type = "frames"; selection = "ozl_screen_4"; period = 0.15; textures[] = {
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f0_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f1_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f2_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f3_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f4_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f5_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f6_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f7_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f8_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f9_co.paa",
                "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f10_co.paa", "\OpenZone_Research\models\m21_lnr_proc_trail\data\ozr_lnr_proc_trail_pda_f11_co.paa"}; };
            class Data    { type = "blink";  selection = "ozl_lamp_2"; on = 0.10; off = 0.25; };
            class Smeter  { type = "wobble"; source = "ozl_needle";   mid = 0.45; amp = 0.10; period = 1.3; };
            class Smeter2 { type = "wobble"; source = "ozl_needle_2"; mid = 0.55; amp = 0.18; period = 0.7; };
            class Smeter3 { type = "wobble"; source = "ozl_needle_3"; mid = 0.62; amp = 0.06; period = 2.1; };
            class Dial    { type = "wobble"; source = "ozl_tune";     mid = 0.50; amp = 0.40; period = 11.0; };
        };
    };

    // Термінал Нейтралів: лабораторна лава як барна стійка (1.70 x 0.95 x 0.77)
    class OZL_Lnr_Terminal : OZL_Terminal_Base
    {
        scope = 2;
        displayName = "$STR_OZL_lnr_terminal";
        descriptionShort = "$STR_OZL_lnr_terminal_desc";
        model = "\OpenZone_Research\models\m22_lnr_terminal\ozr_lnr_terminal.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_co.paa",
            "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_co.paa",
            "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal.rvmat",
            "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp.rvmat",
            "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal.rvmat"
        };
        class AnimationSources
        {
            class ozl_drawer
            {
                source = "user";
                animPeriod = 0.6;
                initPhase = 0;
            };
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        weight = 60000;
        itemSize[] = {7, 4};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Термінал завжди «в роботі», стану спокою немає (відгук користувача 28.10: «у ВСІХ терміналів має
        // бути один стан „в роботі“»): клієнт крутить class OZL_Work весь час (OZL_Station.OZL_WorkFxOn)
        ozlWorkFxAlways = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_on_co.paa", "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_f0_co.paa", "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_on.rvmat", "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_on.rvmat", "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_on.rvmat"};
            class Tuning  { type = "wobble"; source = "ozl_needle"; mid = 0.45; amp = 0.32; period = 7.0; };
            class Lamp    { type = "blink";  selection = "ozl_lamp"; on = 0.5; off = 0.5; };
            class Display { type = "frames"; selection = "ozl_screen_2"; period = 0.45;
                            textures[] = {
                                "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_f0_co.paa", "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_f1_co.paa",
                                "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_f2_co.paa", "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_f3_co.paa",
                                "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_f4_co.paa", "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_f5_co.paa",
                                "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_f6_co.paa", "\OpenZone_Research\models\m22_lnr_terminal\data\ozr_lnr_terminal_disp_f7_co.paa"}; };
            class Drawer  { type = "pose";   source = "ozl_drawer"; };
        };
    };


    // ---- Долг (duty) ----

    // Пакувальник балістики Долгу: лабораторна лава (1.70 x 0.95 x 0.77)
    class OZL_Dty_Pack_Ball : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        displayName = "$STR_OZL_dty_pack_ball";
        descriptionShort = "$STR_OZL_dty_pack_ball_desc";
        model = "\OpenZone_Research\models\m23_dty_pack_ball\ozr_dty_pack_ball.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m23_dty_pack_ball\data\ozr_dty_pack_ball_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m23_dty_pack_ball\data\ozr_dty_pack_ball.rvmat"
        };
        // Вигляд «робота» (OZL_WorkFx.c, R09): лампа над лещатами горить -- атлас _on; модулі в
        // слотах «працюють» разом зі станцією.
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[] = {"\OpenZone_Research\models\m23_dty_pack_ball\data\ozr_dty_pack_ball_on_co.paa"};
            onMaterials[] = {"\OpenZone_Research\models\m23_dty_pack_ball\data\ozr_dty_pack_ball_on.rvmat"};
        };
        weight = 60000;
        itemSize[] = {7, 4};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
    };

    // Аналізатор балістики Долгу: радарний пульт (габарити зняти на стенді)
    class OZL_Dty_Proc_Ball : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        displayName = "$STR_OZL_dty_proc_ball";
        descriptionShort = "$STR_OZL_dty_proc_ball_desc";
        model = "\OpenZone_Research\models\m24_dty_proc_ball\ozr_dty_proc_ball.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_lamp", "ozl_lamp_blink"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_co.paa",
            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_co.paa",
            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_co.paa",
            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt.rvmat",
            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led.rvmat",
            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball.rvmat",
            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle_1
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_needle_2
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_needle_3
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_pose
            {
                source = "user";
                animPeriod = 1;
                initPhase = 0;
            };
        };
        weight = 70000;
        itemSize[] = {3, 5};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_lamp", "ozl_lamp_blink"};
            onTextures[]   = {"\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f0_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f0_co.paa",
                              "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_on_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_on.rvmat", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_on.rvmat",
                              "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_on.rvmat", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_on.rvmat"};
            class Scope   { type = "frames"; selection = "ozl_screen"; period = 0.1;
                            textures[] = {"\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f0_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f1_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f2_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f3_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f4_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f5_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f6_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f7_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f8_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f9_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f10_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f10_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f11_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f12_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f12_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f13_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f13_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f14_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f14_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f15_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f15_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f16_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f17_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f18_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f19_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f16_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f17_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f18_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f19_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f16_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f17_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f18_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f19_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f16_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f17_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f18_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_crt_f19_co.paa"}; };
            class Counter { type = "frames"; selection = "ozl_screen_2"; period = 1.0;
                            textures[] = {"\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f0_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f5_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f5_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f5_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f5_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f1_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f6_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f6_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f6_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f6_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f2_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f7_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f7_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f7_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f7_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f3_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f8_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f8_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f8_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f8_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f4_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f9_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f9_co.paa", "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f9_co.paa",
                            "\OpenZone_Research\models\m24_dty_proc_ball\data\ozr_dty_proc_ball_led_f9_co.paa"}; };
            class Shot    { type = "blink";  selection = "ozl_lamp_blink"; on = 0.25; off = 4.75; };
            class Speed   { type = "wobble"; source = "ozl_needle_1"; mid = 0.715; amp = 0.012; period = 2.4; };
            class Volt    { type = "wobble"; source = "ozl_needle_2"; mid = 0.45;  amp = 0.004; period = 3.7; };
            class Press   { type = "wobble"; source = "ozl_needle_3"; mid = 0.52;  amp = 0.06;  period = 1.2; };
            class Arm     { type = "pose";   source = "ozl_pose"; };
        };
    };

    // Пакувальник захисту Долгу: пральна машина (0.81 x 1.19 x 0.65)
    class OZL_Dty_Pack_Prot : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "protection";
        displayName = "$STR_OZL_dty_pack_prot";
        descriptionShort = "$STR_OZL_dty_pack_prot_desc";
        model = "\OpenZone_Research\models\m25_dty_pack_prot\ozr_dty_pack_prot.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m25_dty_pack_prot\data\ozr_dty_pack_prot_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m25_dty_pack_prot\data\ozr_dty_pack_prot.rvmat"
        };
        class AnimationSources
        {
            class ozl_flow
            {
                source = "user";
                animPeriod = 0.35;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
        };
        weight = 60000;
        itemSize[] = {3, 5};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m25_dty_pack_prot\data\ozr_dty_pack_prot_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m25_dty_pack_prot\data\ozr_dty_pack_prot_on.rvmat"};
            class Fan  { type = "loop"; source = "ozl_work"; };
            class Flow { type = "pose"; source = "ozl_flow"; };
        };
    };

    // Аналізатор захисту Долгу: одиночна радарна стійка (0.77 x 1.99 x 0.66)
    class OZL_Dty_Proc_Prot : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "protection";
        displayName = "$STR_OZL_dty_proc_prot";
        descriptionShort = "$STR_OZL_dty_proc_prot_desc";
        model = "\OpenZone_Research\models\m26_dty_proc_prot\ozr_dty_proc_prot.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp", "ozl_power"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_co.paa",
            "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_co.paa",
            "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen.rvmat",
            "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot.rvmat",
            "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot.rvmat"
        };
        class AnimationSources
        {
            class ozl_meter
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        weight = 90000;
        itemSize[] = {3, 8};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp", "ozl_power"};
            onTextures[]   = {"\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f0_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_on_co.paa",
                              "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_on.rvmat", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_on.rvmat",
                              "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_on.rvmat"};
            class Needle  { type = "wobble"; source = "ozl_meter"; mid = 0.62; amp = 0.08; period = 1.4; };
            class Ready   { type = "blink";  selection = "ozl_lamp"; on = 0.10; off = 0.38; };
            class Display { type = "frames"; selection = "ozl_screen"; period = 0.24;
                            textures[] = {"\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f0_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f1_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f2_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f3_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f4_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f5_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f6_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f7_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f8_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f9_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f10_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f11_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f12_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f13_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f14_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f15_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f16_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f17_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f18_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f19_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f20_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f21_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f22_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f23_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f24_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f25_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f26_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f27_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f28_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f29_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f30_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f31_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f32_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f33_co.paa",
                                          "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f34_co.paa", "\OpenZone_Research\models\m26_dty_proc_prot\data\ozr_dty_proc_prot_screen_f35_co.paa"}; };
        };
    };

    // Термінал Долгу: штабний стіл командира (1.50 x 0.77 x 0.75, антена рації до 1.54; новий клас, M61)
    class OZL_Dty_Terminal : OZL_Terminal_Base
    {
        scope = 2;
        displayName = "$STR_OZL_dty_terminal";
        descriptionShort = "$STR_OZL_dty_terminal_desc";
        model = "\OpenZone_Research\models\m61_dty_terminal\ozr_dty_terminal.p3d";
        hiddenSelections[] = {"ozl_lamp", "ozl_lamp_2"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m61_dty_terminal\data\ozr_dty_terminal_co.paa",
            "\OpenZone_Research\models\m61_dty_terminal\data\ozr_dty_terminal_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m61_dty_terminal\data\ozr_dty_terminal.rvmat",
            "\OpenZone_Research\models\m61_dty_terminal\data\ozr_dty_terminal.rvmat"
        };
        weight = 60000;
        itemSize[] = {7, 4};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Термінал завжди «в роботі», стану спокою немає (відгук користувача 28.10: «у ВСІХ терміналів має
        // бути один стан „в роботі“»): клієнт крутить class OZL_Work весь час (OZL_Station.OZL_WorkFxOn)
        ozlWorkFxAlways = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp", "ozl_lamp_2"};
            onTextures[]   = {"\OpenZone_Research\models\m61_dty_terminal\data\ozr_dty_terminal_on_co.paa", "\OpenZone_Research\models\m61_dty_terminal\data\ozr_dty_terminal_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m61_dty_terminal\data\ozr_dty_terminal_on.rvmat", "\OpenZone_Research\models\m61_dty_terminal\data\ozr_dty_terminal_on.rvmat"};
            class Call { type = "blink"; selection = "ozl_lamp_2"; on = 0.49; off = 0.49; };
        };
    };


    // ---- Воля (freedom) ----

    // Пакувальник балістики Волі: офісний стіл (1.81 x 0.84 x 0.86)
    class OZL_Frd_Pack_Ball : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        displayName = "$STR_OZL_frd_pack_ball";
        descriptionShort = "$STR_OZL_frd_pack_ball_desc";
        model = "\OpenZone_Research\models\m27_frd_pack_ball\ozr_frd_pack_ball.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m27_frd_pack_ball\data\ozr_frd_pack_ball_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m27_frd_pack_ball\data\ozr_frd_pack_ball.rvmat"
        };
        class AnimationSources
        {
            class ozl_work
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
        };
        weight = 50000;
        itemSize[] = {7, 3};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m27_frd_pack_ball\data\ozr_frd_pack_ball_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m27_frd_pack_ball\data\ozr_frd_pack_ball_on.rvmat"};
            class Fan { type = "loop"; source = "ozl_work"; };
        };
    };

    // Аналізатор балістики Волі: свердлильний верстат (0.76 x 0.83 x 0.41; без ViewGeometry)
    class OZL_Frd_Proc_Ball : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        displayName = "$STR_OZL_frd_proc_ball";
        descriptionShort = "$STR_OZL_frd_proc_ball_desc";
        model = "\OpenZone_Research\models\m28_frd_proc_ball\ozr_frd_proc_ball.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_co.paa",
            "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen.rvmat",
            "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball.rvmat"
        };
        weight = 40000;
        itemSize[] = {3, 3};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f0_co.paa",
                "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_on.rvmat",
                "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_on.rvmat"
            };
            class Leds { type = "blink"; selection = "ozl_lamp"; on = 0.15; off = 0.45; };
            class Screen
            {
                type = "frames";
                selection = "ozl_screen";
                period = 0.6;
                textures[] =
                {
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f0_co.paa",
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f1_co.paa",
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f2_co.paa",
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f3_co.paa",
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f4_co.paa",
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f5_co.paa",
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f6_co.paa",
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f7_co.paa",
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f8_co.paa",
                    "\OpenZone_Research\models\m28_frd_proc_ball\data\ozr_frd_proc_ball_screen_f9_co.paa"
                };
            };
        };
    };

    // Пакувальник захисту Волі: магазинний ларь (1.95 x 1.24 x 0.95)
    class OZL_Frd_Pack_Prot : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "protection";
        displayName = "$STR_OZL_frd_pack_prot";
        descriptionShort = "$STR_OZL_frd_pack_prot_desc";
        model = "\OpenZone_Research\models\m29_frd_pack_prot\ozr_frd_pack_prot.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m29_frd_pack_prot\data\ozr_frd_pack_prot_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m29_frd_pack_prot\data\ozr_frd_pack_prot.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 1;
                initPhase = 0;
            };
        };
        weight = 55000;
        itemSize[] = {8, 5};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m29_frd_pack_prot\data\ozr_frd_pack_prot_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m29_frd_pack_prot\data\ozr_frd_pack_prot_on.rvmat"};
            class Fan    { type = "loop";   source = "ozl_work"; };
            class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.72; amp = 0.025; period = 1.2; };
        };
    };

    // Аналізатор захисту Волі: підлогові ваги (0.41 x 0.97 x 0.80)
    class OZL_Frd_Proc_Prot : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "protection";
        displayName = "$STR_OZL_frd_proc_prot";
        descriptionShort = "$STR_OZL_frd_proc_prot_desc";
        model = "\OpenZone_Research\models\m30_frd_proc_prot\ozr_frd_proc_prot.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_co.paa",
            "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd.rvmat",
            "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot.rvmat"
        };
        class AnimationSources
        {
            class ozl_breath
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
        };
        weight = 30000;
        itemSize[] = {2, 4};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_f0_co.paa", "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_on.rvmat", "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_on.rvmat"};
            class Fan     { type = "loop";   source = "ozl_work"; };
            class Needles { type = "wobble"; source = "ozl_needle"; mid = 0.40; amp = 0.012; period = 2.3; };
            class Breath  { type = "wobble"; source = "ozl_breath"; mid = 0.5; amp = 0.5; period = 3.2; };
            class Ready   { type = "blink";  selection = "ozl_lamp"; on = 0.6; off = 0.4; };
            class Readout { type = "frames"; selection = "ozl_screen"; period = 0.5;
                            textures[] = {"\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_f0_co.paa", "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_f1_co.paa",
                                          "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_f2_co.paa", "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_f3_co.paa",
                                          "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_f4_co.paa", "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_f5_co.paa",
                                          "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_f6_co.paa", "\OpenZone_Research\models\m30_frd_proc_prot\data\ozr_frd_proc_prot_lcd_f7_co.paa"}; };
        };
    };

    // Термінал Волі: комп'ютер на кейсах (M31, 1.22 x 1.40 x 0.66)
    class OZL_Frd_Terminal : OZL_Terminal_Base
    {
        scope = 2;
        displayName = "$STR_OZL_frd_terminal";
        descriptionShort = "$STR_OZL_frd_terminal_desc";
        model = "\OpenZone_Research\models\m31_frd_terminal\ozr_frd_terminal.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_blink"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_co.paa",
            "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_co.paa",
            "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen.rvmat",
            "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal.rvmat",
            "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal.rvmat"
        };
        class AnimationSources
        {
            class ozl_work
            {
                source = "user";
                animPeriod = 2.5;
                initPhase = 0;
            };
        };
        weight = 40000;
        itemSize[] = {3, 3};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Термінал завжди «в роботі», стану спокою немає (відгук користувача 28.10: «у ВСІХ терміналів має
        // бути один стан „в роботі“»): клієнт крутить class OZL_Work весь час (OZL_Station.OZL_WorkFxOn)
        ozlWorkFxAlways = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_blink"};
            onTextures[]   = {"\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f0_co.paa", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_on_co.paa", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_on.rvmat", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_on.rvmat", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_on.rvmat"};
            class Fan    { type = "loop";   source = "ozl_work"; };
            class Leds   { type = "blink";  selection = "ozl_lamp_blink"; on = 0.19; off = 0.34; };
            class Screen { type = "frames"; selection = "ozl_screen"; period = 0.24;
                           textures[] = {
                               "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f0_co.paa", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f1_co.paa",
                               "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f2_co.paa", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f3_co.paa",
                               "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f4_co.paa", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f5_co.paa",
                               "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f6_co.paa", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f7_co.paa",
                               "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f8_co.paa", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f9_co.paa",
                               "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f10_co.paa", "\OpenZone_Research\models\m31_frd_terminal\data\ozr_frd_terminal_screen_f11_co.paa"}; };
        };
    };


    // ---- СОП (sop) ----

    // Пакувальник балістики СОП: відкрита шафа (0.92 x 1.18 x 0.94)
    class OZL_Sop_Pack_Ball : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        displayName = "$STR_OZL_sop_pack_ball";
        descriptionShort = "$STR_OZL_sop_pack_ball_desc";
        model = "\OpenZone_Research\models\m32_sop_pack_ball\ozr_sop_pack_ball.p3d";
        hiddenSelections[] = {"ozl_lamp", "ozl_led"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m32_sop_pack_ball\data\ozr_sop_pack_ball_co.paa",
            "\OpenZone_Research\models\m32_sop_pack_ball\data\ozr_sop_pack_ball_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m32_sop_pack_ball\data\ozr_sop_pack_ball.rvmat",
            "\OpenZone_Research\models\m32_sop_pack_ball\data\ozr_sop_pack_ball.rvmat"
        };
        weight = 50000;
        itemSize[] = {4, 5};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp", "ozl_led"};
            onTextures[] =
            {
                "\OpenZone_Research\models\m32_sop_pack_ball\data\ozr_sop_pack_ball_on_co.paa",
                "\OpenZone_Research\models\m32_sop_pack_ball\data\ozr_sop_pack_ball_on_co.paa"
            };
            onMaterials[] =
            {
                "\OpenZone_Research\models\m32_sop_pack_ball\data\ozr_sop_pack_ball_on.rvmat",
                "\OpenZone_Research\models\m32_sop_pack_ball\data\ozr_sop_pack_ball_on.rvmat"
            };
            class Alarm { type = "blink"; selection = "ozl_led"; on = 0.5; off = 0.5; };
        };
    };

    // Аналізатор балістики СОП: радарна електроніка (шлях із device-assets §1; габарити зняти на стенді)
    class OZL_Sop_Proc_Ball : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "ballistics";
        displayName = "$STR_OZL_sop_proc_ball";
        descriptionShort = "$STR_OZL_sop_proc_ball_desc";
        model = "\OpenZone_Research\models\m33_sop_proc_ball\ozr_sop_proc_ball.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_2"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_co.paa",
            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_co.paa",
            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd.rvmat",
            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball.rvmat",
            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball.rvmat"
        };
        class AnimationSources
        {
            class ozl_fan
            {
                source = "user";
                animPeriod = 2;
                initPhase = 0;
            };
            class ozl_work
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work_2
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work_3
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_work_4
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        weight = 70000;
        itemSize[] = {3, 6};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_lamp", "ozl_lamp_2"};
            onTextures[]   = {"\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f0_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_on_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_on.rvmat", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_on.rvmat", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_on.rvmat"};
            class Readout { type = "frames"; selection = "ozl_screen"; period = 0.25;
                            textures[] = {"\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f0_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f0_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f1_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f2_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f3_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f4_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f4_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f4_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f4_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f4_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f4_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f4_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f0_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f0_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f5_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f6_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f7_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f8_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f8_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f8_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f8_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f8_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f8_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f8_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f0_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f0_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f9_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f10_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f11_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f12_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f12_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f12_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f12_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f12_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f12_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f12_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f0_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f0_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f13_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f14_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f15_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f16_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f16_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f16_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f16_co.paa",
                            "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f16_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f16_co.paa", "\OpenZone_Research\models\m33_sop_proc_ball\data\ozr_sop_proc_ball_lcd_f16_co.paa"}; };
            class Fan     { type = "loop";   source = "ozl_fan"; };
            class Lamps   { type = "blink";  selection = "ozl_lamp_2"; on = 0.45; off = 0.35; };
            class Needle1 { type = "wobble"; source = "ozl_work";   mid = 0.55; amp = 0.06;  period = 1.9; };
            class Needle2 { type = "wobble"; source = "ozl_work_2"; mid = 0.70; amp = 0.04;  period = 2.6; };
            class Needle3 { type = "wobble"; source = "ozl_work_3"; mid = 0.45; amp = 0.08;  period = 3.3; };
            class Needle4 { type = "wobble"; source = "ozl_work_4"; mid = 0.80; amp = 0.012; period = 0.7; };
        };
    };

    // Пакувальник захисту СОП: закритий локер (0.40 x 1.90 x 0.55)
    class OZL_Sop_Pack_Prot : OZL_Packer_Base
    {
        scope = 2;
        ozlLine = "protection";
        displayName = "$STR_OZL_sop_pack_prot";
        descriptionShort = "$STR_OZL_sop_pack_prot_desc";
        model = "\OpenZone_Research\models\m34_sop_pack_prot\ozr_sop_pack_prot.p3d";
        hiddenSelections[] = {"ozl_lamp"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m34_sop_pack_prot\data\ozr_sop_pack_prot_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m34_sop_pack_prot\data\ozr_sop_pack_prot.rvmat"
        };
        class AnimationSources
        {
            class ozl_work
            {
                source = "user";
                animPeriod = 60;
                initPhase = 0;
            };
        };
        weight = 50000;
        itemSize[] = {2, 8};
        itemsCargoSize[] = {10, 10};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp"};
            onTextures[]   = {"\OpenZone_Research\models\m34_sop_pack_prot\data\ozr_sop_pack_prot_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m34_sop_pack_prot\data\ozr_sop_pack_prot_on.rvmat"};
            class Stopwatch { type = "loop"; source = "ozl_work"; };
        };
    };

    // Аналізатор захисту СОП: муфельна піч на тумбі (0.90 x 1.57 x 0.83, модель M35)
    class OZL_Sop_Proc_Prot : OZL_Analyzer_Base
    {
        scope = 2;
        ozlLine = "protection";
        displayName = "$STR_OZL_sop_proc_prot";
        descriptionShort = "$STR_OZL_sop_proc_prot_desc";
        model = "\OpenZone_Research\models\m35_sop_proc_prot\ozr_sop_proc_prot.p3d";
        hiddenSelections[] = {"ozl_lamp", "ozl_lamp_2"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m35_sop_proc_prot\data\ozr_sop_proc_prot_co.paa",
            "\OpenZone_Research\models\m35_sop_proc_prot\data\ozr_sop_proc_prot_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m35_sop_proc_prot\data\ozr_sop_proc_prot.rvmat",
            "\OpenZone_Research\models\m35_sop_proc_prot\data\ozr_sop_proc_prot.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
            class ozl_needle_2
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        weight = 45000;
        itemSize[] = {2, 3};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_lamp", "ozl_lamp_2"};
            onTextures[]   = {"\OpenZone_Research\models\m35_sop_proc_prot\data\ozr_sop_proc_prot_on_co.paa", "\OpenZone_Research\models\m35_sop_proc_prot\data\ozr_sop_proc_prot_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m35_sop_proc_prot\data\ozr_sop_proc_prot_on.rvmat", "\OpenZone_Research\models\m35_sop_proc_prot\data\ozr_sop_proc_prot_on.rvmat"};
            class Heat { type = "blink";  selection = "ozl_lamp_2"; on = 1.6; off = 0.9; };
            class Pyro { type = "wobble"; source = "ozl_needle";   mid = 0.75; amp = 0.012; period = 4.0; };
            class Amps { type = "wobble"; source = "ozl_needle_2"; mid = 0.60; amp = 0.04;  period = 1.3; };
        };
    };

    // Термінал СОП: монітор на стійці (0.71 x 1.57 x 1.24)
    class OZL_Sop_Terminal : OZL_Terminal_Base
    {
        scope = 2;
        displayName = "$STR_OZL_sop_terminal";
        descriptionShort = "$STR_OZL_sop_terminal_desc";
        model = "\OpenZone_Research\models\m36_sop_terminal\ozr_sop_terminal.p3d";
        hiddenSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_lamp", "ozl_lamp_2"};
        hiddenSelectionsTextures[] =
        {
            "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_co.paa",
            "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_co.paa",
            "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_co.paa",
            "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_co.paa"
        };
        hiddenSelectionsMaterials[] =
        {
            "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen.rvmat",
            "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2.rvmat",
            "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal.rvmat",
            "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal.rvmat"
        };
        class AnimationSources
        {
            class ozl_needle
            {
                source = "user";
                animPeriod = 0.2;
                initPhase = 0;
            };
        };
        weight = 40000;
        itemSize[] = {3, 6};
        itemsCargoSize[] = {4, 4};
        rotatable = 1;
        // Термінал завжди «в роботі», стану спокою немає (відгук користувача 28.10: «у ВСІХ терміналів має
        // бути один стан „в роботі“»): клієнт крутить class OZL_Work весь час (OZL_Station.OZL_WorkFxOn)
        ozlWorkFxAlways = 1;
        // Вигляд «робота» (OZL_WorkFx.c): з превью доводки моделей, 27.10
        class OZL_Work
        {
            onSelections[] = {"ozl_screen", "ozl_screen_2", "ozl_lamp", "ozl_lamp_2"};
            onTextures[]   = {"\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f0_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f0_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_on_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_on_co.paa"};
            onMaterials[]  = {"\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_on.rvmat",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_on.rvmat",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_on.rvmat",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_on.rvmat"};
            class Crt
            {
                type = "frames"; selection = "ozl_screen"; period = 0.25;
                textures[] = {"\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f0_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f1_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f2_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f3_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f4_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f5_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f6_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f7_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f8_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f9_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f10_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_f11_co.paa"};
            };
            class Laptop
            {
                type = "frames"; selection = "ozl_screen_2"; period = 0.4;
                textures[] = {"\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f0_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f1_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f2_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f3_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f4_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f5_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f6_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f7_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f8_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f9_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f10_co.paa",
                              "\OpenZone_Research\models\m36_sop_terminal\data\ozr_sop_terminal_screen_2_f11_co.paa"};
            };
            class Leds   { type = "blink";  selection = "ozl_lamp_2"; on = 0.12; off = 0.35; };
            class Needle { type = "wobble"; source = "ozl_needle"; mid = 0.62; amp = 0.07; period = 1.3; };
        };
    };

};
