// Спорядження й вкладення: що стоїть у слотах приладу, що вдягнено на гравця.
//
// Три запитання, які ставлять правила: чи є на приладі всі потрібні
// інструменти, скільки чистоти додають модулі в його слотах, чи вдягнено на
// гравця все зі списку. Клас без стану -- лише обхід вкладень.

class OZL_Gear
{
    static bool DeviceHasTools(EntityAI device, array<string> required, out string missing)
    {
        missing = "";
        if (!required || required.Count() == 0)
            return true;
        if (!device || !device.GetInventory())
            return false;

        for (int r = 0; r < required.Count(); r++)
        {
            if (!HasAttachment(device, required[r]))
            {
                missing = required[r];
                return false;
            }
        }
        return true;
    }

    // Зламаний інструмент не додає нічого: бонус рахується з живих вкладень.
    static float DeviceModuleBonus(EntityAI device)
    {
        if (!device || !device.GetInventory())
            return 0;

        array<string> classes = new array<string>();
        int count = device.GetInventory().AttachmentCount();
        for (int i = 0; i < count; i++)
        {
            EntityAI att = device.GetInventory().GetAttachmentFromIndex(i);
            if (!att || att.IsRuined())
                continue;
            classes.Insert(att.GetType());
        }
        return OZL_Config.Get().Modules().SumBonus(classes);
    }

    static bool WearsAll(PlayerBase player, array<string> required, out string missing)
    {
        missing = "";
        if (!required || required.Count() == 0)
            return true;
        if (!player || !player.GetInventory())
            return false;

        for (int r = 0; r < required.Count(); r++)
        {
            if (!HasAttachment(player, required[r]))
            {
                missing = required[r];
                return false;
            }
        }
        return true;
    }

    private static bool HasAttachment(EntityAI host, string configured)
    {
        int count = host.GetInventory().AttachmentCount();
        for (int i = 0; i < count; i++)
        {
            EntityAI att = host.GetInventory().GetAttachmentFromIndex(i);
            if (att && OZL_Match.MatchClass(att.GetType(), configured))
                return true;
        }
        return false;
    }
}
