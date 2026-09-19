// Логер мода досліджень.
//
// Свій префікс, а не ядерний: у лозі сервера з тридцятьма модами треба одразу
// бачити, ЧИЙ це рядок, і вердикт стенда шукає саме префікс.
//
// WARNING і ERROR пишуться повними словами: вердикт шукає \bWARNING\b і рядок
// `[OpenZone/Research] ERROR` (error_regex у dayz-mcp.toml), і скорочення під
// них не підпадають.
//
// РІВЕНЬ ВІДЛАДКИ -- У ЯДРА. Власного прапорця немає навмисно: ядро тут стоїть
// завжди (requiredAddons), його DebugMode їде клієнтові пакетом синхронізації,
// і другий вимикач був би другим місцем, де рівні розходяться.

class OZL_Log
{
    static void Info(string msg)
    {
        Print(OZL_Const.LOG_PREFIX + msg);
    }

    static void Warn(string msg)
    {
        Print(OZL_Const.LOG_PREFIX + "WARNING: " + msg);
    }

    static void Error(string msg)
    {
        Print(OZL_Const.LOG_PREFIX + "ERROR: " + msg);
    }

    static bool IsDebug()
    {
        return OZ_Log.IsDebug();
    }

    static void Dbg(string msg)
    {
        if (!OZ_Log.IsDebug())
            return;
        Print(OZL_Const.LOG_PREFIX + "dbg: " + msg);
    }
}
