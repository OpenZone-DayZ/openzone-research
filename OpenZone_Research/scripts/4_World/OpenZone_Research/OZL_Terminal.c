// Термінал: одна умова на три дії й серверне виконання здачі та опознання.
//
// Три дії на одній цілі й одній клавіші розходяться УМОВОЮ, а не порядком
// реєстрації: з носієм або даними в руках коротке F -- опознати, утримання
// -- здати; з порожніми руками F -- відкрити дерево. Умова на обох боках
// структурна (клас цілі, клас предмета в руках); чи термінал свій, чи носій
// повний, чи дані описані -- судить сервер при виконанні й відповідає
// звісткою ключем рядка.
//
// Здати можна БУДЬ-ЯКИЙ носій, і це навмисно (ZP §5c): бали йдуть у пул того,
// ХТО ЗДАЄ. Дефіцит створює гейт на виробництві, а не заборона на здачу --
// інакше трофейний носій був би сміттям.

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

    static bool IsData(ItemBase item)
    {
        return item && GetGame().IsKindOf(item.GetType(), "OZL_Data_Base");
    }

    // Те, що можна здати: носій або дані, не зруйноване.
    static bool IsDepositable(ItemBase item)
    {
        if (!item || item.IsRuined())
            return false;
        return IsCarrier(item) || IsData(item);
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
        array<string> types   = new array<string>();
        array<int>    amounts = new array<int>();

        if (IsCarrier(item))
        {
            string ptId;
            int amount;
            if (!OZL_CarrierState.Parse(OZL_Carrier_Base.StateOf(item), ptId, amount))
            {
                why = "STR_OZL_ERR_CARRIER_EMPTY";
                return false;
            }
            if (!pts.Find(ptId))
            {
                why = "STR_OZL_ERR_UNKNOWN_TYPE";
                return false;
            }
            types.Insert(ptId);
            amounts.Insert(amount);
        }
        else
        {
            OZL_DataDef def = OZL_Config.Get().DataItems().Find(item.GetType());
            if (!def || !def.Enabled)
            {
                why = "STR_OZL_ERR_DATA_UNKNOWN";
                return false;
            }
            for (int r = 0; r < def.Points.Count(); r++)
            {
                OZL_DataReward rw = def.Points[r];
                if (!rw || rw.Type == "" || rw.Amount <= 0)
                    continue;
                if (!pts.Find(rw.Type))
                {
                    OZL_Log.Warn("deposit: data '" + item.GetType() + "' promises point type '" + rw.Type + "', which PointTypes does not know, skipped");
                    continue;
                }
                types.Insert(rw.Type);
                amounts.Insert(rw.Amount);
            }
            if (types.Count() == 0)
            {
                why = "STR_OZL_ERR_DATA_UNKNOWN";
                return false;
            }
        }

        string itemType = item.GetType();
        GetGame().ObjectDelete(item);

        string granted = "";
        for (int i = 0; i < types.Count(); i++)
        {
            string gwhy;
            OZL_Points.Grant(owner, types[i], amounts[i], gwhy);
            if (granted != "")
                granted += ", ";
            granted += pts.NameOf(types[i]) + " +" + amounts[i].ToString();
        }
        line = granted;
        why = "STR_OZL_MSG_DEPOSITED";
        OZL_Log.Dbg("deposit: " + uid + " " + itemType + " -> " + owner + ": " + granted);
        return true;
    }

    // ---------- опознання ----------

    // Сервер. Людський рядок про стан носія: тип балів словами, тир, кількість.
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
        string ptId;
        int amount;
        if (!OZL_CarrierState.Parse(OZL_Carrier_Base.StateOf(item), ptId, amount))
        {
            why = "STR_OZL_ERR_CARRIER_EMPTY";
            return false;
        }
        OZL_PointTypes pts = OZL_Config.Get().PointTypes();
        OZL_PointType pt = pts.Find(ptId);
        if (!pt)
        {
            why = "STR_OZL_ERR_UNKNOWN_TYPE";
            return false;
        }
        line = item.GetDisplayName() + ": " + pt.Name;
        line += " (" + OZL_PointTypes.DimensionName(pts.Categories, pt.Category);
        line += ", " + OZL_PointTypes.DimensionName(pts.Kinds, pt.Kind);
        line += ", T" + pt.Tier.ToString() + ") +" + amount.ToString();
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
