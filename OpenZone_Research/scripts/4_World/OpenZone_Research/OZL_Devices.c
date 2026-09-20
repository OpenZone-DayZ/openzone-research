// Класи приладів: порожні двійники config-класів.
//
// Кожен клас потрібен окремо, порожній чи ні: рушій шукає скрипт-клас,
// піднімаючись config-ієрархією, а config-предок OZL_StaticDevice_Base
// скрипт-двійника не має -- без цих оголошень прилад мовчки став би
// звичайним ItemBase, без карго-логіки й дій. Уся поведінка живе в
// OZL_Station/OZL_StaticStation, різниця між приладами -- у конфігах:
// модель у config.cpp, належність фракції в Owners, правила в Rules.
// Список згенеровано з config.cpp; змінюючи класи там, змініть і тут.

// ---- переносні ----

class OZL_PetriDishKit : OZL_Station
{
}

class OZL_FieldCase : OZL_Station
{
}

// ---- стаціонарні ----

class OZL_Microscope : OZL_StaticStation
{
}

class OZL_LabComputer : OZL_StaticStation
{
}

class OZL_ChemBench : OZL_StaticStation
{
}

class OZL_ServerRack : OZL_StaticStation
{
}

class OZL_Eco_Pack_Bio : OZL_StaticStation
{
}

class OZL_Eco_Proc_Bio : OZL_StaticStation
{
}

class OZL_Eco_Pack_Anom : OZL_StaticStation
{
}

class OZL_Eco_Proc_Anom : OZL_StaticStation
{
}

class OZL_Eco_Pack_Electro : OZL_StaticStation
{
}

class OZL_Eco_Proc_Electro : OZL_StaticStation
{
}

class OZL_Sky_Pack_Bio : OZL_StaticStation
{
}

class OZL_Sky_Proc_Bio : OZL_StaticStation
{
}

class OZL_Sky_Pack_Anom : OZL_StaticStation
{
}

class OZL_Sky_Proc_Anom : OZL_StaticStation
{
}

class OZL_Sky_Pack_Electro : OZL_StaticStation
{
}

class OZL_Sky_Proc_Electro : OZL_StaticStation
{
}

class OZL_Bnd_Pack_Khabar : OZL_StaticStation
{
}

class OZL_Bnd_Proc_Khabar : OZL_StaticStation
{
}

class OZL_Bnd_Pack_Trail : OZL_StaticStation
{
}

class OZL_Bnd_Proc_Trail : OZL_StaticStation
{
}

class OZL_Bnd_Terminal : OZL_StaticStation
{
}

class OZL_Lnr_Pack_Khabar : OZL_StaticStation
{
}

class OZL_Lnr_Proc_Khabar : OZL_StaticStation
{
}

class OZL_Lnr_Pack_Trail : OZL_StaticStation
{
}

class OZL_Lnr_Proc_Trail : OZL_StaticStation
{
}

class OZL_Lnr_Terminal : OZL_StaticStation
{
}

class OZL_Dty_Pack_Ball : OZL_StaticStation
{
}

class OZL_Dty_Proc_Ball : OZL_StaticStation
{
}

class OZL_Dty_Pack_Prot : OZL_StaticStation
{
}

class OZL_Dty_Proc_Prot : OZL_StaticStation
{
}

class OZL_Frd_Pack_Ball : OZL_StaticStation
{
}

class OZL_Frd_Proc_Ball : OZL_StaticStation
{
}

class OZL_Frd_Pack_Prot : OZL_StaticStation
{
}

class OZL_Frd_Proc_Prot : OZL_StaticStation
{
}

class OZL_Frd_Terminal : OZL_StaticStation
{
}

class OZL_Sop_Pack_Ball : OZL_StaticStation
{
}

class OZL_Sop_Proc_Ball : OZL_StaticStation
{
}

class OZL_Sop_Pack_Prot : OZL_StaticStation
{
}

class OZL_Sop_Proc_Prot : OZL_StaticStation
{
}

class OZL_Sop_Terminal : OZL_StaticStation
{
}

class OZL_SampleFridge : OZL_StaticStation
{
}
