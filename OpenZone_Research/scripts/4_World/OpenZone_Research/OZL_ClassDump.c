// Перелік класів сервера для редактора моста: імена CfgVehicles по одному на
// рядок у файл теки обміну. Пишеться раз на старт; редактор перевіряє
// «клас існує» проти живого сервера, а не проти офлайн-індексу з PBO.

class OZL_ClassDump
{
    private static int s_LastCount = 0;

    static int Write(string path)
    {
        FileHandle f = OpenFile(path, FileMode.WRITE);
        if (f == 0)
        {
            OZL_Log.Warn("classes: cannot write " + path);
            return 0;
        }
        int n = GetGame().ConfigGetChildrenCount("CfgVehicles");
        int written = 0;
        for (int i = 0; i < n; i++)
        {
            string name;
            if (!GetGame().ConfigGetChildName("CfgVehicles", i, name))
                continue;
            if (name == "")
                continue;
            FPrintln(f, name);
            written++;
        }
        CloseFile(f);
        s_LastCount = written;
        return written;
    }

    static int LastCount()
    {
        return s_LastCount;
    }
}
