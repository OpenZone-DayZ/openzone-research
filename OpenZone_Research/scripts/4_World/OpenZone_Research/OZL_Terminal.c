// Термінал: одна умова на три дії й серверне виконання здачі та опознання.
//
// Три дії на одній цілі й одній клавіші розходяться УМОВОЮ, а не порядком
// реєстрації: з носієм у руках коротке F -- опознати, утримання -- здати; з
// порожніми руками F -- відкрити дерево. Умова на обох боках структурна (клас
// цілі, клас предмета в руках); чи термінал свій і чи носій повний -- судить
// сервер при виконанні й відповідає звісткою ключем рядка.
//
// Здати можна БУДЬ-ЯКИЙ носій, і це навмисно: бали йдуть у пул того, ХТО
// ЗДАЄ. Дефіцит створює гейт на виробництві, а не заборона на здачу --
// інакше трофейний носій був би сміттям. Тип балів -- лінія класу носія.

class OZL_Terminal
{
    static const float DEPOSIT_SEC = 3.0;

    // Ціль -- живий термінал мода. Сервер питає конфіг, клієнт -- список,
    // що приїхав пакетом синхронізації.
    static bool IsTerminalTarget(Object obj)
    {
        if (!obj)
            return false;
        EntityAI ent = EntityAI.Cast(obj);
        if (!ent || ent.IsDamageDestroyed())
            return false;
        if (GetGame().IsServer())
            return OZL_Config.Get().Owners().IsTerminalClass(obj.GetType());
        return OZL_ClientConfig.IsTerminal(obj.GetType());
    }

    static bool IsCarrier(ItemBase item)
    {
        return item && GetGame().IsKindOf(item.GetType(), "OZL_Carrier_Base");
    }

    // Те, що можна здати: носій, не зруйнований.
    static bool IsDepositable(ItemBase item)
    {
        if (!item || item.IsRuined())
            return false;
        return IsCarrier(item);
    }

    // ---------- здача ----------

    // Сервер. Порядок: усе прочитати, перевірити, потім видалити предмет, і
    // лише потім нарахувати -- жоден порядок не дає ані подвоєння балів, ані
    // зникнення предмета без нарахування. Повертає ключ звістки; `line` --
    // рядок статусу з числами для гравця.
    static bool Deposit(PlayerBase who, Object obj, ItemBase item, out string why, out string line)
    {
        why = "";
        line = "";
        if (!who || !GetGame().IsServer() || !IsTerminalTarget(obj) || !IsDepositable(item))
        {
            why = "STR_OZ_ERR_INTERNAL";
            return false;
        }
        string owner = OZL_Owner.OfPlayer(who);
        if (!OZL_Config.Get().Owners().IsTerminalFor(owner, obj.GetType()))
        {
            why = "STR_OZL_ERR_NOT_YOUR_TERMINAL";
            return false;
        }
        string uid = "";
        if (who.GetIdentity())
            uid = who.GetIdentity().GetPlainId();

        OZL_PointTypes pts = OZL_Config.Get().PointTypes();
        string ptId = OZL_Lines.LineOf(item.GetType());
        int amount;
        OZL_Carrier_Base car = OZL_Carrier_Base.Cast(item);
        if (!car || !car.OZL_Read(amount))
        {
            why = "STR_OZL_ERR_CARRIER_EMPTY";
            return false;
        }
        if (!pts.Find(ptId))
        {
            why = "STR_OZL_ERR_UNKNOWN_TYPE";
            return false;
        }

        string itemType = item.GetType();
        GetGame().ObjectDelete(item);

        string gwhy;
        OZL_Points.Grant(owner, ptId, amount, gwhy);
        line = pts.NameOf(ptId) + " +" + amount.ToString();
        why = "STR_OZL_MSG_DEPOSITED";
        OZL_Log.Dbg("deposit: " + uid + " " + itemType + " -> " + owner + ": " + line);
        return true;
    }

    // ---------- опознання ----------

    // Сервер. Людський рядок про носій: лінія словами й кількість балів.
    static bool Identify(PlayerBase who, Object obj, ItemBase item, out string why, out string line)
    {
        why = "";
        line = "";
        if (!who || !GetGame().IsServer() || !IsTerminalTarget(obj) || !IsCarrier(item))
        {
            why = "STR_OZ_ERR_INTERNAL";
            return false;
        }
        string owner = OZL_Owner.OfPlayer(who);
        if (!OZL_Config.Get().Owners().IsTerminalFor(owner, obj.GetType()))
        {
            why = "STR_OZL_ERR_NOT_YOUR_TERMINAL";
            return false;
        }
        int amount;
        OZL_Carrier_Base car = OZL_Carrier_Base.Cast(item);
        if (!car || !car.OZL_Read(amount))
        {
            why = "STR_OZL_ERR_CARRIER_EMPTY";
            return false;
        }
        OZL_PointType pt = OZL_Config.Get().PointTypes().Find(OZL_Lines.LineOf(item.GetType()));
        if (!pt)
        {
            why = "STR_OZL_ERR_UNKNOWN_TYPE";
            return false;
        }
        line = item.GetDisplayName() + ": " + pt.Name + " +" + amount.ToString();
        why = "STR_OZL_MSG_IDENTIFIED";
        return true;
    }

    // ---------- дерево ----------

    // Сервер: чи відкривати цьому гравцеві дерево на цьому терміналі.
    static bool MayOpenTree(PlayerBase who, Object obj, out string why)
    {
        why = "";
        if (!who || !GetGame().IsServer() || !IsTerminalTarget(obj))
        {
            why = "STR_OZ_ERR_INTERNAL";
            return false;
        }
        string owner = OZL_Owner.OfPlayer(who);
        if (!OZL_Config.Get().Owners().IsTerminalFor(owner, obj.GetType()))
        {
            why = "STR_OZL_ERR_NOT_YOUR_TERMINAL";
            return false;
        }
        return true;
    }
}
