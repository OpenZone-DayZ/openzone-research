// Заготовка даних: результат дослідження, звичайний предмет.
//
// Один скрипт-клас на дев'яносто config-класів. Назва прямо каже, що це, тож
// ані прихованих полів, ані визначення не потрібно: назва, опис і бали при
// здачі беруться з OZ_Research_DataItems.json.

class OZL_Data_Base : ItemBase
{
    override string GetDisplayName()
    {
        string name;
        string desc;
        if (OZL_Names.Lookup(GetType(), name, desc) && name != "")
            return name;
        return super.GetDisplayName();
    }

    override bool DescriptionOverride(out string output)
    {
        string name;
        string desc;
        if (OZL_Names.Lookup(GetType(), name, desc) && desc != "")
        {
            output = desc;
            return true;
        }
        return false;
    }
}

// Інструменти станцій: стоять у слотах і відкривають правила, що їх вимагають.
// Не витрачаються. Скрипт-клас потрібен лише щоб клас існував для дерева
// успадкування; поведінка -- ванільна.
class OZL_Tool_Base : ItemBase
{
}
