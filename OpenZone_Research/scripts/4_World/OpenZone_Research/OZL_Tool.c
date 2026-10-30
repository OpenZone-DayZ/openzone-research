// Модуль: інструмент у слоті пакувальника своєї лінії. Не витрачається;
// поведінка ванільна, своє -- лише вигляд «робота».

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
