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
    // ЗБИРАЧ ДЛЯ РЕДАКТОРА У VPP. Validate і Check конфігів кажуть про
    // знахідки лише цим Warn; редактор ганяє їх на копії свого чернетки ЩОРАЗУ,
    // як адмін щось змінить, і хоче не рядки в лозі клієнта, а список
    // проблем. Поки збирач стоїть, Warn пише туди й мовчить у лозі.
    private static ref array<string> s_Sink;

    static void CaptureBegin(array<string> sink)
    {
        s_Sink = sink;
    }

    static void CaptureEnd()
    {
        s_Sink = null;
    }

    static void Info(string msg)
    {
        Print(OZL_Const.LOG_PREFIX + msg);
    }

    static void Warn(string msg)
    {
        if (s_Sink)
        {
            s_Sink.Insert(msg);
            return;
        }
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
