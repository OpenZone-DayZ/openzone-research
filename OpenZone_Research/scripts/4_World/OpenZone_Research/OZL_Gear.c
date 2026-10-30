// Спорядження й вкладення: що стоїть у слотах приладу, що вдягнено на гравця.
//
// Три запитання, які ставлять правила: чи є на приладі всі потрібні
// інструменти, скільки чистоти й шансу подвійного виходу додають модулі
// пакувальника, чи вдягнено на гравця все зі списку. Клас без стану -- лише
// обхід вкладень.

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

    // Бонуси цілих модулів своєї лінії в слотах пакувальника: чистота й шанс
    // подвійного виходу. Зламаний модуль не дає нічого; кожен клас -- один раз.
    static void ModuleBonuses(EntityAI device, out float purity, out float doubleChance)
    {
        purity = 0;
        doubleChance = 0;
        if (!device || !device.GetInventory())
            return;
        OZL_Modules modules = OZL_Config.Get().Modules();
        array<string> seen = new array<string>();
        int count = device.GetInventory().AttachmentCount();
        for (int i = 0; i < count; i++)
        {
            EntityAI att = device.GetInventory().GetAttachmentFromIndex(i);
            if (!att || att.IsRuined())
                continue;
            string cls = att.GetType();
            if (!OZL_Modules.AllowedOn(cls, device.GetType()))
                continue;
            bool dup = false;
            for (int s = 0; s < seen.Count(); s++)
            {
                if (seen[s] == cls)
                    dup = true;
            }
            OZL_ModuleDef def = modules.Find(cls);
            if (dup || !def)
                continue;
            seen.Insert(cls);
            purity += def.PurityBonus;
            doubleChance += def.DoubleChance;
        }
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
