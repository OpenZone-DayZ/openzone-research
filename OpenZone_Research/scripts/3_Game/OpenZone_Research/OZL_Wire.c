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
    string Id   = "";
    string Name = "";
    // Колір лінії з конфігу типів балів (Color "#RRGGBB") як ARGB: чіпи
    // лінії в пулі, у ціні вузла й у картці. 0 -- кольору не задано.
    int    Color = 0;
}

// Матеріал, якого коштує вузол: клас, ЙОГО ІГРОВА НАЗВА (сервер питає
// конфіг, клієнт не знає класів) і скільки штук.
class OZL_ItemView
{
    // Не `Class`: так зветься тип рушія, і поле з таким іменем не збереться.
    string Cls  = "";
    string Name = "";
    int    Qty  = 0;
    // Скільки таких предметів лежить у карго власного термінала поруч із
    // гравцем (той самий добір, що й при старті); -1 -- невідомо: відповідь
    // без гравця або без термінала поруч. Невідоме статус `short` не міняє.
    int    Have = -1;
}

class OZL_NodeView
{
    string Id       = "";
    string Name     = "";
    string Desc     = "";
    // Значок вузла з конфігу дерева ("set:<набір> image:<значок>"); порожньо
    // -- значка немає, картка лишає колонку під нього порожньою.
    string Icon     = "";
    // "locked" | "short" | "available" | "researching" | "completed".
    // `short` -- батьки виконані, а балів фракції чи матеріалів у терміналі
    // не вистачає. Це підказка екрану, а не дозвіл: старт перевіряє сам.
    string Status   = "locked";
    // Календарні секунди OZL_Clock, коли проєкт завершиться (лише researching).
    int    EndSec   = 0;
    // Скільки триває дослідження цього вузла; 0 -- миттєво.
    int    Duration = 0;
    // Рівень вузла: рядок екрана. Порядку в рядку немає -- він такий, яким
    // вузли йдуть у масиві, а розкладає їх рушій.
    int    Tier     = 1;
    // Місце вузла серед вузлів ЦІЄЇ гілки, що належать цьому власникові: з
    // нуля, у порядку конфігу. Номер "01" у реєстрі Долгу -- це Index + 1.
    int    Index    = 0;
    // ParentsMode == "any" (без огляду на регістр): вузол відкривається після
    // будь-якого з батьків, а не після всіх.
    bool   Any      = false;
    // Батьки в порядку конфігу. Id батька, якого цей власник зараз не бачить
    // (його приховав туман, або він чужий), не їде: на його місці порожній
    // рядок -- довжина й порядок збережено, щоб картка могла написати
    // «невідомо», не знаючи, хто це.
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

// Вузол, прихований туманом війни. Клієнт знає про нього рівно стільки, скільки
// треба, щоб показати «невідомо»: місце в гілці (Index, як у OZL_NodeView),
// рівень і тих батьків, яких бачить сам. Ані id, ані імені, ані опису, ані
// ціни; id прихованих батьків теж не їдуть -- вони лишаються на сервері.
class OZL_HiddenView
{
    int Index = 0;
    int Tier  = 1;
    ref array<string> Parents;

    void OZL_HiddenView()
    {
        Parents = new array<string>();
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
    // Вузли гілки, які належать власникові, але туман їх не показав. Разом із
    // Nodes дають рівно Total записів, а їхні Index -- числа 0..Total-1.
    ref array<ref OZL_HiddenView> Hidden;

    void OZL_BranchView()
    {
        Nodes  = new array<ref OZL_NodeView>();
        Hidden = new array<ref OZL_HiddenView>();
    }
}

class OZL_TreeView
{
    string Owner      = "";
    string OwnerName  = "";
    int    OwnerColor = 0;
    // Id вікна дерева, УЖЕ розв'язаний сервером (OZL_Owners.SkinOf): рівно
    // один із ecolog, clearsky, duty, freedom, sop, bandit, neutral. Клієнт
    // нічого не вирішує і порожнього id не отримує.
    string Skin       = "";
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
