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
// Не витрачаються. Поведінка -- ванільна; своє -- лише вигляд «робота».
class OZL_Tool_Base : ItemBase
{
    // Вигляд «робота» модуля (OZL_WorkFx.c, class OZL_Work у config.cpp класу): вмикає станція,
    // у слоті якої модуль стоїть, поки вона працює (рішення користувача 26.10, R09). Лише клієнт.
    protected ref OZL_WorkFx m_OZL_WorkFx;

    void OZL_SetWorking(bool on)
    {
        if (!GetGame() || GetGame().IsDedicatedServer())
            return;
        if (on && !m_OZL_WorkFx)
        {
            if (!OZL_WorkFx.Has(this))
                return;
            m_OZL_WorkFx = new OZL_WorkFx(this);
        }
        if (!m_OZL_WorkFx)
            return;
        if (on)
            m_OZL_WorkFx.Start();
        else
            m_OZL_WorkFx.Stop();
    }

    override void EEDelete(EntityAI parent)
    {
        if (m_OZL_WorkFx)
            m_OZL_WorkFx.Stop();
        super.EEDelete(parent);
    }
}
