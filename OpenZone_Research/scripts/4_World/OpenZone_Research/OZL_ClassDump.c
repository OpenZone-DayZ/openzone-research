// Перелік класів сервера для редактора моста: усі п'ять коренів, які
// перевіряє OZL_Match.ClassExists, по рядку на клас -- корінь, ім'я,
// базовий клас і назва двома мовами. Пишеться раз на старт; редактор
// перевіряє «клас існує» і родину (IsKindOf) проти ЖИВОГО сервера, а не
// проти офлайн-індексу з PBO, і показує імена гри без жодного розбору
// архівів поза сервером (рішення власника 2026-09-20: «вивантажуй усе з
// сервера»).
//
// Формат рядка: <корінь>\t<ім'я>\t<база>\t<original>\t<english>. Порядок
// коренів збігається з індексом класів моста (0..4). Назви: ключ
// displayName розв'язується таблицями рядків, які сервер читає з архівів
// (OZL_StringTables); ключ, якого там немає, і буквальна назва без ключа
// дають текст мовою сервера в обидві колонки. Табуляції й переноси в назві
// замінюються пробілом.

class OZL_ClassDump
{
    private static int s_LastCount = 0;
    private static int s_Resolved = 0;
    private static int s_Ms = 0;

    // Порядок = індекс кореня в мостовому індексі класів.
    static const string ROOT_0 = "CfgVehicles";
    static const string ROOT_1 = "CfgMagazines";
    static const string ROOT_2 = "CfgNonAIVehicles";
    static const string ROOT_3 = "CfgAmmo";
    static const string ROOT_4 = "cfgWeapons";

    static int Write(string path)
    {
        int t0 = GetGame().GetTime();
        OZL_StringTables.Load();
        FileHandle f = OpenFile(path, FileMode.WRITE);
        if (f == 0)
        {
            OZL_Log.Warn("classes: cannot write " + path);
            OZL_StringTables.Release();
            return 0;
        }
        s_Resolved = 0;
        int written = 0;
        written += WriteRoot(f, 0, ROOT_0);
        written += WriteRoot(f, 1, ROOT_1);
        written += WriteRoot(f, 2, ROOT_2);
        written += WriteRoot(f, 3, ROOT_3);
        written += WriteRoot(f, 4, ROOT_4);
        CloseFile(f);
        OZL_StringTables.Release();
        s_LastCount = written;
        s_Ms = GetGame().GetTime() - t0;
        return written;
    }

    private static int WriteRoot(FileHandle f, int rootIdx, string root)
    {
        int n = GetGame().ConfigGetChildrenCount(root);
        int written = 0;
        string tab = "\t";
        string prefix = rootIdx.ToString() + tab;
        for (int i = 0; i < n; i++)
        {
            string name;
            if (!GetGame().ConfigGetChildName(root, i, name))
                continue;
            if (name == "")
                continue;
            string path = root + " " + name;
            string base = "";
            GetGame().ConfigGetBaseName(path, base);
            string raw = "";
            GetGame().ConfigGetTextRaw(path + " displayName", raw);
            string original;
            string english;
            if (OZL_StringTables.Resolve(raw, original, english))
            {
                s_Resolved++;
            }
            else
            {
                original = GetGame().ConfigGetTextOut(path + " displayName");
                english = original;
            }
            FPrintln(f, prefix + name + tab + base + tab + Clean(original) + tab + Clean(english));
            written++;
        }
        return written;
    }

    private static string Clean(string s)
    {
        string cleaned = s;
        cleaned.Replace("\t", " ");
        cleaned.Replace("\r", "");
        cleaned.Replace("\n", " ");
        return cleaned;
    }

    static int LastCount()
    {
        return s_LastCount;
    }

    // Один рядок для журналу: скільки класів, скільки назв розв'язано
    // таблицями, скільки таблиць і ключів, скільки часу.
    static string Summary()
    {
        return s_LastCount.ToString() + " written, " + s_Resolved.ToString() + " named from " + OZL_StringTables.Tables().ToString() + " stringtable(s) with " + OZL_StringTables.Keys().ToString() + " key(s), " + s_Ms.ToString() + " ms";
    }
}
