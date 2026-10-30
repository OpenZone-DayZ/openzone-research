// Класи приладів: порожні двійники config-класів.
//
// Кожен клас потрібен окремо, порожній чи ні: рушій шукає скрипт-клас,
// піднімаючись config-ієрархією, а config-предки (OZL_StaticDevice_Base і
// бази пакувальника, аналізатора й термінала) скрипт-двійників не мають --
// без цих оголошень прилад мовчки став би звичайним ItemBase, без
// карго-логіки й дій. Уся поведінка живе в OZL_StaticStation, різниця між
// приладами -- у конфігах: модель і лінія в config.cpp, належність фракції в
// Owners, правила в Rules. Змінюючи класи в config.cpp, змініть і тут.

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

class OZL_Eco_Terminal : OZL_StaticStation
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

class OZL_Sky_Terminal : OZL_StaticStation
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

class OZL_Dty_Terminal : OZL_StaticStation
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
