// Провід між модом і мостом (Node): три листи вгору, одна команда вниз.
//
// Листи йдуть тілом виклику ядра (до 1 МіБ), тож у них є місце для
// лічильників і переліків. Команда приїжджає елементом опиту, і її рядок
// рушій ріже близько кілобайта -- тому вона коротка: op, token, by і
// аргументи; конфіг ніколи не їде командою, лише файлом обміну.
//
// Об'єкти для розбору створює скрипт: рідний завантажувач не виконує
// ініціалізаторів полів об'єкта, який створив сам.

class OZL_BootLetter
{
    int    Revision   = 0;
    string Counters   = "";
    string Classes    = "";
    int    ClassCount = 0;
    ref array<string> Names;

    void OZL_BootLetter()
    {
        Names = new array<string>();
    }
}

class OZL_ChangedLetter
{
    string Name     = "";
    int    Revision = 0;
    string By       = "";
}

class OZL_ResultLetter
{
    string Token    = "";
    bool   Ok       = false;
    string Why      = "";
    string Note     = "";
    string Counters = "";
}

// Відповідь моста на будь-який лист: {ok, why}.
class OZL_BridgeAnswer
{
    bool   ok  = false;
    string why = "";
}

// Команда моста. Поля, яких операція не потребує, лишаються порожніми.
class OZL_BridgeCommand
{
    string op     = "";
    string token  = "";
    string by     = "";
    string name   = "";
    string file   = "";
    string owner  = "";
    string type   = "";
    string amount = "";
    string node   = "";
    string id     = "";
}
