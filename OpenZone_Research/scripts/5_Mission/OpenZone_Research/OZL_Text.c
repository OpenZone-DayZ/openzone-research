// Текстові дрібниці екрана дерева.
//
// ВЕЛИКІ ЛІТЕРИ. Мокап робить багато написів великими через CSS
// (text-transform), а рушій так не вміє: ToUpper() знає лише ASCII, і
// кирилиця лишається малою. Upper() міняє ЦІЛІ ЛІТЕРИ заміною рядка --
// Length/Substring рахують байти, і різати UTF-8 посеред літери не можна
// (скіл, залізні правила). Заміна двобайтової літери на двобайтову безпечна:
// провідний байт кирилиці (D0/D1) ніколи не стоїть на місці байта
// продовження, тож збіг посеред іншої літери неможливий.
//
// Мала і стає ЛАТИНСЬКОЮ I: ванільні шрифти не мають кириличної І, а
// латинська виглядає так само (правило рядків серії). Кирилична І, якщо
// раптом прийде в даних, теж стає латинською.

class OZL_Text
{
    private static ref array<string> s_Lower;
    private static ref array<string> s_Upper;

    private static void Table()
    {
        if (s_Lower)
            return;
        s_Lower = new array<string>();
        s_Upper = new array<string>();
        Pair("а", "А"); Pair("б", "Б"); Pair("в", "В"); Pair("г", "Г"); Pair("ґ", "Ґ");
        Pair("д", "Д"); Pair("е", "Е"); Pair("є", "Є"); Pair("ж", "Ж"); Pair("з", "З");
        Pair("и", "И"); Pair("і", "I"); Pair("ї", "Ї"); Pair("й", "Й"); Pair("к", "К");
        Pair("л", "Л"); Pair("м", "М"); Pair("н", "Н"); Pair("о", "О"); Pair("п", "П");
        Pair("р", "Р"); Pair("с", "С"); Pair("т", "Т"); Pair("у", "У"); Pair("ф", "Ф");
        Pair("х", "Х"); Pair("ц", "Ц"); Pair("ч", "Ч"); Pair("ш", "Ш"); Pair("щ", "Щ");
        Pair("ь", "Ь"); Pair("ю", "Ю"); Pair("я", "Я"); Pair("І", "I");
    }

    private static void Pair(string lower, string upper)
    {
        s_Lower.Insert(lower);
        s_Upper.Insert(upper);
    }

    // Копія рядка великими літерами: латиниця й українська кирилиця.
    static string Upper(string s)
    {
        Table();
        string t = s;
        t.ToUpper();
        for (int i = 0; i < s_Lower.Count(); i++)
            t.Replace(s_Lower[i], s_Upper[i]);
        return t;
    }

    // Два знаки: 1 -> "01". Номер вузла в реєстрі Долгу, хвилини годинника.
    static string Two(int n)
    {
        if (n < 10 && n >= 0)
            return "0" + n.ToString();
        return n.ToString();
    }

    // Рядок із ключа stringtable; що не ключ -- як є (відмови сервера
    // приходять ключем, а інколи й готовим словом).
    static string Words(string key)
    {
        if (key.IndexOf("STR_") == 0)
            return Widget.TranslateString("#" + key);
        return key;
    }

    // Тривалість словами: "45 с", "1 хв 05 с", "2 год 05 хв". Одиниці --
    // ключі рядків, а не англійські літерали старого екрана.
    static string Duration(int sec)
    {
        if (sec < 0)
            sec = 0;
        string s = Words("STR_OZL_TREE_UNIT_S");
        string m = Words("STR_OZL_TREE_UNIT_MIN");
        if (sec < 60)
            return sec.ToString() + " " + s;
        if (sec < 3600)
        {
            int mm = sec / 60;
            return mm.ToString() + " " + m + " " + Two(sec - mm * 60) + " " + s;
        }
        int hh = sec / 3600;
        int rest = (sec - hh * 3600) / 60;
        return hh.ToString() + " " + Words("STR_OZL_TREE_UNIT_H") + " " + Two(rest) + " " + m;
    }

    // Годинник залишку: "0:41", "12:05"; від години -- "1:02:05". Мокап
    // зупиняється на хвилинах, а дослідження може тривати довше.
    static string Clock(int sec)
    {
        if (sec < 0)
            sec = 0;
        int hh = sec / 3600;
        int mm = (sec - hh * 3600) / 60;
        int ss = sec - hh * 3600 - mm * 60;
        if (hh > 0)
            return hh.ToString() + ":" + Two(mm) + ":" + Two(ss);
        return mm.ToString() + ":" + Two(ss);
    }

    // Римська цифра рівня, як підписи тирів мокапа (I..VII і далі).
    static string Roman(int n)
    {
        if (n < 1 || n > 39)
            return n.ToString();
        string rom = "";
        while (n >= 10)
        {
            rom += "X";
            n -= 10;
        }
        if (n == 9)
            return rom + "IX";
        if (n >= 5)
        {
            rom += "V";
            n -= 5;
        }
        if (n == 4)
            return rom + "IV";
        while (n > 0)
        {
            rom += "I";
            n--;
        }
        return rom;
    }
}
