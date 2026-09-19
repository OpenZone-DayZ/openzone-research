// Пул балів фракції: нарахувати, перевірити, списати.
//
// Три дії й жодного резерву: вартість вузла списується цілком у мить старту
// (миттєвого чи проєкту), як TrySpendCost у ZP, а входи станції йдуть при її
// старті -- це і є антифарм. Кожна зміна пулу проходить через OZL_State.Save.

class OZL_Points
{
    static bool Grant(string owner, string type, int amount, out string why)
    {
        why = "";
        if (amount <= 0)
        {
            why = "STR_OZL_ERR_AMOUNT";
            return false;
        }
        if (!OZL_Config.Get().PointTypes().Find(type))
        {
            why = "STR_OZL_ERR_UNKNOWN_TYPE";
            return false;
        }

        OZL_FactionState st = OZL_State.Get(owner);
        if (!st)
        {
            why = "STR_OZL_ERR_BAD_OWNER";
            return false;
        }

        st.SetPoints(type, st.PointsOf(type) + amount);
        OZL_State.Save(owner);
        OZL_Log.Dbg("points: " + owner + " +" + amount.ToString() + " " + type + " = " + st.PointsOf(type).ToString());
        return true;
    }

    static bool Has(string owner, array<ref OZL_TreeCost> cost)
    {
        OZL_FactionState st = OZL_State.Get(owner);
        if (!st)
            return false;
        for (int i = 0; i < cost.Count(); i++)
        {
            if (cost[i] && st.PointsOf(cost[i].Type) < cost[i].Amount)
                return false;
        }
        return true;
    }

    // Списати всю вартість або нічого: перевірка перед першим списанням, щоб
    // не лишити пул наполовину сплаченим.
    static bool Spend(string owner, array<ref OZL_TreeCost> cost, out string why)
    {
        why = "";
        OZL_FactionState st = OZL_State.Get(owner);
        if (!st)
        {
            why = "STR_OZL_ERR_BAD_OWNER";
            return false;
        }
        if (!Has(owner, cost))
        {
            why = "STR_OZL_ERR_POINTS";
            return false;
        }

        for (int i = 0; i < cost.Count(); i++)
        {
            if (!cost[i])
                continue;
            st.SetPoints(cost[i].Type, st.PointsOf(cost[i].Type) - cost[i].Amount);
        }
        OZL_State.Save(owner);
        return true;
    }

    // Пул рядком -- для лога й адмінського списку.
    static string Describe(string owner)
    {
        OZL_FactionState st = OZL_State.Get(owner);
        if (!st)
            return "?";
        string s = "";
        for (int i = 0; i < st.Points.Count(); i++)
        {
            if (!st.Points[i] || st.Points[i].Value == 0)
                continue;
            if (s != "")
                s += ", ";
            s += st.Points[i].Key + "=" + st.Points[i].Value.ToString();
        }
        if (s == "")
            return "empty";
        return s;
    }
}
