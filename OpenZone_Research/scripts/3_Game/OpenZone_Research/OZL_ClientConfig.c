// Те небагато з конфігів, що клієнт мусить знати для підказок дій: класи
// терміналів. Їде додатком пакета синхронізації ядра (як імена предметів),
// а живе в 3_Game, бо умови дій -- 4_World, і до OZ_ClientState (5_Mission)
// їм не дотягнутись.
//
// Належність термінала фракції клієнт не знає й не має знати: підказка
// показується на будь-якому терміналі мода, а судить сервер.

class OZL_ClientConfig
{
    // Об'єднання списків терміналів усіх власників, порціями: кожне значення
    // додатка коротше за 1023 байти, бо довше рушій ріже мовчки.
    static const string SYNC_TERMINALS   = "research.terminals.";
    static const string SYNC_TERMINALS_N = "research.terminals";
    static const int    CHUNK_CHARS      = 900;

    private static ref array<string> s_Terminals = new array<string>();

    static void Clear()
    {
        s_Terminals.Clear();
    }

    // Один шматок "клас,клас,..." -- дописується до вже прочитаних.
    static void AddTerminals(string csv)
    {
        if (csv == "")
            return;
        array<string> parts = new array<string>();
        csv.Split(",", parts);
        for (int i = 0; i < parts.Count(); i++)
        {
            string cls = parts[i].Trim();
            if (cls != "" && s_Terminals.Find(cls) < 0)
                s_Terminals.Insert(cls);
        }
    }

    static bool IsTerminal(string classname)
    {
        return OZL_Match.InList(classname, s_Terminals);
    }

    static int TerminalCount()
    {
        return s_Terminals.Count();
    }
}
