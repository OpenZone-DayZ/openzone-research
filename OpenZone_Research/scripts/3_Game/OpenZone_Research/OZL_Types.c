// Спільні маленькі типи: пара «ключ -- число», перевірка id як імені файла,
// збіг класу з налаштованим ім'ям.
//
// У 3_Game, бо ними користуються обидва боки: конфіги (сервер), відповідь
// служби (клієнт) і меню дерева.

// map через RPC й JSON не їде, масив пар їде як звичайний JSON.
class OZL_KV
{
    string Key   = "";
    int    Value = 0;

    void OZL_KV(string k = "", int v = 0)
    {
        Key   = k;
        Value = v;
    }
}

class OZL_Ids
{
    // Id власника стає ім'ям файла стану, тому лише латиниця, цифри, '_' і
    // '-', непорожньо, не довше 64. Слаги ядра народжуються в боті -- перевірка
    // стоїть перед кожним зверненням до диска, а не довіряє реєстру.
    static bool IsPathSafe(string id)
    {
        int n = id.Length();
        if (n == 0 || n > 64)
            return false;

        for (int i = 0; i < n; i++)
        {
            int c = id.Get(i).ToAscii();
            bool digit = c >= 48 && c <= 57;
            bool upper = c >= 65 && c <= 90;
            bool lower = c >= 97 && c <= 122;
            bool punct = c == 95 || c == 45;
            if (!digit && !upper && !lower && !punct)
                return false;
        }
        return true;
    }
}

class OZL_Match
{
    // Налаштоване ім'я класу: голе -- родина (IsKindOf), із суфіксом "|1" --
    // рівно цей клас. Так адмін відрізняє «будь-який зразок» від «саме цей».
    static bool MatchClass(string actualType, string configured)
    {
        if (configured == "")
            return false;

        int sep = configured.IndexOf("|");
        if (sep > -1)
        {
            string exact = configured.Substring(0, sep);
            exact.ToLower();
            string actual = actualType;
            actual.ToLower();
            return actual == exact;
        }
        return GetGame().IsKindOf(actualType, configured);
    }

    static string StripExact(string configured)
    {
        int sep = configured.IndexOf("|");
        if (sep > -1)
            return configured.Substring(0, sep);
        return configured;
    }

    static bool ClassExists(string cls)
    {
        if (cls == "")
            return false;
        if (GetGame().ConfigIsExisting("CfgVehicles " + cls))
            return true;
        if (GetGame().ConfigIsExisting("CfgAmmo " + cls))
            return true;
        if (GetGame().ConfigIsExisting("CfgMagazines " + cls))
            return true;
        if (GetGame().ConfigIsExisting("cfgWeapons " + cls))
            return true;
        if (GetGame().ConfigIsExisting("CfgNonAIVehicles " + cls))
            return true;
        return false;
    }

    static bool InList(string actualType, array<string> configured)
    {
        if (!configured)
            return false;
        for (int i = 0; i < configured.Count(); i++)
        {
            if (MatchClass(actualType, configured[i]))
                return true;
        }
        return false;
    }
}
