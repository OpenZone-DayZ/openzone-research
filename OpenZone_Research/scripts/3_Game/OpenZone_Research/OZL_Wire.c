// Провід служби research: що їде клієнтові у відповідь на `tree` і `research`,
// і що клієнт шле в `research`. У 3_Game, бо обидва боки читають ті самі
// класи: сервер їх наповнює, меню дерева їх малює.
//
// Корінь кожного класу створює скрипт, масиви -- в конструкторах: рідний
// JsonFileLoader сам полів не ініціалізує. Рядкові значення коротші за 1023
// байти (рушій ріже довші мовчки), тож опис вузла -- одна фраза, а не
// сторінка.

class OZL_PointName
{
    string Id       = "";
    string Name     = "";
    string Category = "";
    string Kind     = "";
    int    Tier     = 1;
}

// Матеріал, якого коштує вузол: клас, ЙОГО ІГРОВА НАЗВА (сервер питає
// конфіг, клієнт не знає класів) і скільки штук.
class OZL_ItemView
{
    // Не `Class`: так зветься тип рушія, і поле з таким іменем не збереться.
    string Cls  = "";
    string Name = "";
    int    Qty  = 0;
}

class OZL_NodeView
{
    string Id       = "";
    string Name     = "";
    string Desc     = "";
    // Значок вузла з конфігу дерева ("set:<набір> image:<значок>"); порожньо
    // -- значка немає, картка лишає колонку під нього порожньою.
    string Icon     = "";
    // "locked" | "available" | "researching" | "completed"
    string Status   = "locked";
    // Календарні секунди OZL_Clock, коли проєкт завершиться (лише researching).
    int    EndSec   = 0;
    // Скільки триває дослідження цього вузла; 0 -- миттєво.
    int    Duration = 0;
    // Рівень вузла: рядок екрана. Порядку в рядку немає -- він такий, яким
    // вузли йдуть у масиві, а розкладає їх рушій.
    int    Tier     = 1;
    ref array<string>         Parents;
    ref array<ref OZL_KV>     Cost;
    ref array<ref OZL_ItemView> Items;

    void OZL_NodeView()
    {
        Parents = new array<string>();
        Cost    = new array<ref OZL_KV>();
        Items   = new array<ref OZL_ItemView>();
    }
}

class OZL_BranchView
{
    string Id   = "";
    string Name = "";
    // Скільки вузлів у гілці НАСПРАВДІ: те, що нижче, -- лише видимі, а
    // лічильник "досліджено N / M" має рахувати все дерево, інакше він
    // росте, коли туман війни відступає.
    int    Total = 0;
    ref array<ref OZL_NodeView> Nodes;

    void OZL_BranchView()
    {
        Nodes = new array<ref OZL_NodeView>();
    }
}

class OZL_TreeView
{
    string Owner      = "";
    string OwnerName  = "";
    int    OwnerColor = 0;
    string Background = "";
    bool   MaySpend   = false;
    // Календарна секунда сервера в мить відповіді: клієнт рахує залишок
    // проєктів від неї, а не від власного годинника.
    int    Now        = 0;
    ref array<ref OZL_KV>         Pool;
    ref array<ref OZL_PointName>  Names;
    ref array<ref OZL_BranchView> Branches;

    void OZL_TreeView()
    {
        Pool     = new array<ref OZL_KV>();
        Names    = new array<ref OZL_PointName>();
        Branches = new array<ref OZL_BranchView>();
    }
}

class OZL_ResearchReq
{
    string NodeId = "";
}
