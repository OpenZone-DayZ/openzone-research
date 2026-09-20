// Екран дерева досліджень (меню 135): відповідь служби `tree` як вона є,
// намальована по описах oz_research_tree.json і oz_research_node.json.
//
// Дані -- лише OZL_TreeView: меню не знає конфігів і не рахує статусів, воно
// показує те, що сказав сервер, і просить дослідити вузол. Відмова приходить
// ключем рядка -- її показує сповіщення, як і решту відповідей мода. Escape
// закриває. Ані власних кольорів (палітра ядра), ані власних координат:
//
// ДЕРЕВО РОСТЕ ВНИЗ І РОЗКЛАДАЄТЬСЯ РУШІЄМ. Рівень -- рядок; рядок -- це
// WrapSpacer (oz_research_tier.layout), у який меню кладе комірки вузлів
// (oz_research_node.layout) і більше нічого з ними не робить: проміжок
// вбудований у комірку, центрування вмикає SetContentAlignmentH, перенос на
// другу лінію робить сам спейсер. Тому вузол можна додати чи прибрати в
// конфігу, і дерево не розлазиться: жодне число тут не знає, скільки вузлів
// у рівні. Єдине, що меню малює саме, -- лінії батько->дитина, і ті по
// прямокутниках, які дав рушій.

#ifndef NO_GUI

class OZL_TreeMenu : UIScriptedMenu
{
    static const string LAYOUT      = "OpenZone_Research/gui/layouts/oz_research_tree.layout";
    static const string ROW_LAYOUT  = "OpenZone_Research/gui/layouts/oz_research_branch_row.layout";
    static const string NODE_LAYOUT = "OpenZone_Research/gui/layouts/oz_research_node.layout";
    static const string TIER_LAYOUT = "OpenZone_Research/gui/layouts/oz_research_tier.layout";
    static const string POINT_LAYOUT = "OpenZone_Research/gui/layouts/oz_research_point_row.layout";
    static const string COST_LAYOUT = "OpenZone_Research/gui/layouts/oz_research_cost_row.layout";

    static const float LINE_W = 2;
    // Скільки рівнів дерево може мати: захист від конфігу з дикою Tier.
    static const int   MAX_TIER = 40;

    private static OZL_TreeMenu s_Open;

    private ref OZL_TreeView m_View;
    private string m_Branch = "";
    private string m_Node   = "";
    // Коли приїхала відповідь -- залишок проєкту рахується від серверної
    // секунди в ній, а не від годинника клієнта.
    private float m_ViewAge = 0;
    private bool  m_NeedLines = false;
    private float m_Tick = 0;
    // Екранна позиція ПЕРШОЇ картки в мить, коли лінії малювалися востаннє.
    // Два випадки, і обидва виміряні на стенді 2026-09-20: щойно створена
    // комірка ще не розкладена, і GetScreenPos віддає її МІСЦЕВІ координати
    // (10,0 замість 1655,228) -- лінії за ними лягли б купою в кутку; а коли
    // гравець крутить колесо, картки їдуть, і подій прокрутки віджет не дає.
    // Тому лінії перемальовуються, щойно перша картка опинилась не там, де
    // була: це покриває і перший кадр, і прокрутку.
    private float m_LinesAtX = -99999;
    private float m_LinesAtY = -99999;

    private Widget       m_Chip;
    private TextWidget   m_OwnerName;
    private TextWidget   m_PoolLine;
    private Widget       m_BranchList;
    private Widget       m_PointList;
    private Widget       m_TreeArea;
    private ImageWidget  m_TreeBg;
    private CanvasWidget m_Lines;
    private Widget       m_TierStack;
    private TextWidget   m_CardName;
    private TextWidget   m_CardMeta;
    private TextWidget   m_CardDesc;
    private Widget       m_CostList;
    private TextWidget   m_CardTime;
    private TextWidget   m_CardStatus;
    private Widget       m_BtnResearch;
    private TextWidget   m_Hint;

    private ref array<Widget> m_RowWidgets;
    private ref array<Widget> m_PointWidgets;
    private ref array<Widget> m_CostWidgets;
    private ref array<Widget> m_TierWidgets;
    // Комірки вузлів і їхні id -- паралельні масиви: по id меню знаходить
    // вузол у відповіді, по комірці -- прямокутник для ліній.
    private ref array<Widget> m_NodeWidgets;
    private ref array<string> m_NodeIds;

    void OZL_TreeMenu()
    {
        m_RowWidgets   = new array<Widget>();
        m_PointWidgets = new array<Widget>();
        m_CostWidgets  = new array<Widget>();
        m_TierWidgets  = new array<Widget>();
        m_NodeWidgets  = new array<Widget>();
        m_NodeIds      = new array<string>();
    }

    static OZL_TreeMenu Open()
    {
        return s_Open;
    }

    // Відповідь служби -- сюди з OZL_MissionGameplay, для відкритого меню.
    static void OnService(string serviceId, string op, bool ok, string json, string error)
    {
        if (serviceId != OZL_Const.SERVICE)
            return;
        if (!ok)
        {
            OZ_Notice.Take("research." + op, false, error);
            if (s_Open)
                s_Open.Hint(Words(error));
            return;
        }
        if (!s_Open)
            return;
        s_Open.Take(json);
        if (op == OZL_Const.OP_RESEARCH)
            OZ_Notice.Take("research." + op, true, "STR_OZL_TREE_STARTED");
    }

    static string Words(string key)
    {
        if (key.IndexOf("STR_") == 0)
            return Widget.TranslateString("#" + key);
        return key;
    }

    override Widget Init()
    {
        layoutRoot = GetGame().GetWorkspace().CreateWidgets(LAYOUT);
        if (!layoutRoot)
        {
            OZL_Log.Error("tree menu: the layout produced no widgets");
            return null;
        }

        m_Chip        = layoutRoot.FindAnyWidget("OwnerChip");
        m_OwnerName   = TextWidget.Cast(layoutRoot.FindAnyWidget("OwnerName"));
        m_PoolLine    = TextWidget.Cast(layoutRoot.FindAnyWidget("PoolLine"));
        m_BranchList  = layoutRoot.FindAnyWidget("BranchList");
        m_PointList   = layoutRoot.FindAnyWidget("PointList");
        m_TreeArea    = layoutRoot.FindAnyWidget("TreeArea");
        m_TreeBg      = ImageWidget.Cast(layoutRoot.FindAnyWidget("TreeBg"));
        m_Lines       = CanvasWidget.Cast(layoutRoot.FindAnyWidget("TreeLines"));
        m_TierStack   = layoutRoot.FindAnyWidget("TierStack");
        m_CardName    = TextWidget.Cast(layoutRoot.FindAnyWidget("CardName"));
        m_CardMeta    = TextWidget.Cast(layoutRoot.FindAnyWidget("CardMeta"));
        m_CardDesc    = TextWidget.Cast(layoutRoot.FindAnyWidget("CardDesc"));
        m_CostList    = layoutRoot.FindAnyWidget("CardCostList");
        m_CardTime    = TextWidget.Cast(layoutRoot.FindAnyWidget("CardTime"));
        m_CardStatus  = TextWidget.Cast(layoutRoot.FindAnyWidget("CardStatus"));
        m_BtnResearch = layoutRoot.FindAnyWidget("BtnResearch");
        m_Hint        = TextWidget.Cast(layoutRoot.FindAnyWidget("TreeHint"));

        return layoutRoot;
    }

    override bool UseMouse()
    {
        return true;
    }

    override bool UseKeyboard()
    {
        return true;
    }

    override void OnShow()
    {
        super.OnShow();
        if (!layoutRoot)
        {
            OZL_Log.Error("tree menu: no layout, closing");
            GetGame().GetUIManager().CloseMenu(OZL_Const.MENU_TREE);
            return;
        }
        s_Open = this;
        SetFocus(layoutRoot);
        LockControls();
        array<string> excludes = new array<string>();
        excludes.Insert("menu");
        GetGame().GetMission().AddActiveInputExcludes(excludes);

        ClearCard();
        Hint(Words("STR_OZL_TREE_LOADING"));
        OZ_Rpc.ServiceRequest(OZL_Const.SERVICE, OZL_Const.OP_TREE, "{}");
    }

    override void OnHide()
    {
        super.OnHide();
        array<string> excludes = new array<string>();
        excludes.Insert("menu");
        GetGame().GetMission().RemoveActiveInputExcludes(excludes, true);
        UnlockControls();
        if (s_Open == this)
            s_Open = null;
    }

    override bool OnKeyPress(Widget w, int x, int y, int key)
    {
        if (key == KeyCode.KC_ESCAPE)
        {
            Close();
            return true;
        }
        return super.OnKeyPress(w, x, y, key);
    }

    override void Update(float timeslice)
    {
        super.Update(timeslice);
        m_ViewAge += timeslice;
        if (m_NeedLines)
        {
            m_NeedLines = false;
            DrawLines();
        }
        else if (LinesMoved())
        {
            DrawLines();
        }
        m_Tick += timeslice;
        if (m_Tick >= 1.0)
        {
            m_Tick = 0;
            PaintProgress();
        }
    }

    // ---------- дані ----------

    void Take(string json)
    {
        OZL_TreeView v = new OZL_TreeView();
        string err;
        if (!JsonFileLoader<OZL_TreeView>.LoadData(json, v, err))
        {
            OZL_Log.Warn("tree menu: unreadable tree (" + err + ")");
            Hint("?");
            return;
        }
        m_View = v;
        m_ViewAge = 0;

        if (m_Branch == "" || !BranchOf(m_Branch))
        {
            m_Branch = "";
            if (v.Branches.Count() > 0)
                m_Branch = v.Branches[0].Id;
        }
        PaintHeader();
        PaintBranches();
        PaintPoints();
        PaintTree();
        if (m_Node != "" && !NodeOf(m_Node))
            m_Node = "";
        PaintCard();
        Hint(Words("STR_OZL_TREE_HINT"));
    }

    private OZL_BranchView BranchOf(string id)
    {
        if (!m_View)
            return null;
        for (int i = 0; i < m_View.Branches.Count(); i++)
        {
            if (m_View.Branches[i] && m_View.Branches[i].Id == id)
                return m_View.Branches[i];
        }
        return null;
    }

    private OZL_NodeView NodeOf(string id)
    {
        OZL_BranchView b = BranchOf(m_Branch);
        if (!b)
            return null;
        for (int i = 0; i < b.Nodes.Count(); i++)
        {
            if (b.Nodes[i] && b.Nodes[i].Id == id)
                return b.Nodes[i];
        }
        return null;
    }

    // Коротка назва типу балів: "Біологія Т1" -- категорія й тир із
    // відповіді. Повне ім'я ("Польове дослідження біології 1 тиру")
    // адміністратор пише для картки, а в комірку вузла й у колонку балів воно
    // не влазить -- і саме воно обрізалося на старому екрані.
    private string ShortPointName(string type)
    {
        if (m_View)
        {
            for (int i = 0; i < m_View.Names.Count(); i++)
            {
                OZL_PointName n = m_View.Names[i];
                if (n && n.Id == type)
                {
                    string s = n.Category;
                    if (s == "")
                        s = n.Name;
                    if (s == "")
                        s = n.Id;
                    // Вид і тир дописуються цілим словом. ЧОМУ НЕ ПЕРША
                    // ЛІТЕРА: Substring у Enforce ріже БАЙТИ, і кирилична
                    // літера (два байти UTF-8) розпадається навпіл --
                    // рядок після такого обрізка не малюється взагалі
                    // (стенд 2026-09-20: замість "Біологія п1" лишалося
                    // саме "Біологія").
                    if (n.Kind != "")
                        s += ", " + n.Kind;
                    if (n.Tier > 0)
                        s += " " + n.Tier.ToString();
                    return s;
                }
            }
        }
        return type;
    }

    // Те саме для комірки вузла, де на весь рядок ціни лишається близько
    // 136 одиниць: категорія і тир, без виду. Вид -- єдине, що тут
    // відрізається, і він є повністю в картці праворуч.
    private string TinyPointName(string type)
    {
        if (m_View)
        {
            for (int i = 0; i < m_View.Names.Count(); i++)
            {
                OZL_PointName n = m_View.Names[i];
                if (n && n.Id == type)
                {
                    string s = n.Category;
                    if (s == "")
                        s = n.Name;
                    if (s == "")
                        s = n.Id;
                    if (n.Tier > 0)
                        s += " " + n.Tier.ToString();
                    return s;
                }
            }
        }
        return type;
    }

    private string PointName(string type)
    {
        if (m_View)
        {
            for (int i = 0; i < m_View.Names.Count(); i++)
            {
                OZL_PointName n = m_View.Names[i];
                if (n && n.Id == type)
                {
                    if (n.Name != "")
                        return n.Name;
                    return n.Id;
                }
            }
        }
        return type;
    }

    // Назва предмета мовою ГРАВЦЯ. Сервер кладе свою здогадку в Name, але
    // ConfigGetTextOut на сервері розв'язує $STR_ мовою СЕРВЕРА (виміряно на
    // стенді 2026-09-20: англійський сервер відповідає "Paper" там, де
    // гравець має бачити "Папір"), тож клієнт питає свій конфіг сам.
    private string ItemLabel(OZL_ItemView iv)
    {
        if (!iv)
            return "";
        string name = "";
        if (iv.Cls != "")
        {
            name = GetGame().ConfigGetTextOut("CfgVehicles " + iv.Cls + " displayName");
            if (name == "")
                name = GetGame().ConfigGetTextOut("CfgMagazines " + iv.Cls + " displayName");
            if (name == "")
                name = GetGame().ConfigGetTextOut("cfgWeapons " + iv.Cls + " displayName");
            if (name == "")
                name = GetGame().ConfigGetTextOut("CfgAmmo " + iv.Cls + " displayName");
        }
        if (name == "" || name.IndexOf("$") == 0 || name.IndexOf("STR_") == 0)
            name = iv.Name;
        if (name == "")
            name = iv.Cls;
        return name;
    }

    private int PoolOf(string type)
    {
        if (!m_View)
            return 0;
        for (int i = 0; i < m_View.Pool.Count(); i++)
        {
            if (m_View.Pool[i] && m_View.Pool[i].Key == type)
                return m_View.Pool[i].Value;
        }
        return 0;
    }

    private static int StatusColor(string status)
    {
        if (status == "completed")
            return OZ_Palette.OK;
        if (status == "researching")
            return OZ_Palette.ALERT;
        if (status == "available")
            return OZ_Palette.ACCENT;
        return OZ_Palette.MUTED;
    }

    private static string StatusKey(string status)
    {
        if (status == "completed")
            return "STR_OZL_TREE_COMPLETED";
        if (status == "researching")
            return "STR_OZL_TREE_RESEARCHING";
        if (status == "available")
            return "STR_OZL_TREE_AVAILABLE";
        return "STR_OZL_TREE_LOCKED";
    }

    // ---------- малювання ----------

    private void PaintHeader()
    {
        if (m_OwnerName)
            m_OwnerName.SetText(m_View.OwnerName);
        if (m_Chip)
        {
            m_Chip.SetColor(m_View.OwnerColor);
            m_Chip.Show(true);
        }
        if (m_PoolLine)
        {
            OZL_BranchView b = BranchOf(m_Branch);
            string line = "";
            if (b)
            {
                int done = 0;
                int work = 0;
                for (int i = 0; i < b.Nodes.Count(); i++)
                {
                    OZL_NodeView n = b.Nodes[i];
                    if (!n)
                        continue;
                    if (n.Status == "completed")
                        done++;
                    else if (n.Status == "researching")
                        work++;
                }
                int total = b.Total;
                if (total < b.Nodes.Count())
                    total = b.Nodes.Count();
                line = b.Name + "   " + Words("STR_OZL_TREE_COMPLETED") + " " + done.ToString() + " / " + total.ToString();
                if (work > 0)
                    line += "   " + Words("STR_OZL_TREE_RESEARCHING") + " " + work.ToString();
            }
            m_PoolLine.SetText(line);
        }
        if (m_TreeBg)
        {
            if (m_View.Background != "")
            {
                m_TreeBg.LoadImageFile(0, m_View.Background);
                m_TreeBg.Show(true);
            }
            else
            {
                m_TreeBg.Show(false);
            }
        }
    }

    private void PaintBranches()
    {
        int i;
        for (i = 0; i < m_RowWidgets.Count(); i++)
        {
            if (m_RowWidgets[i])
                m_RowWidgets[i].Unlink();
        }
        m_RowWidgets.Clear();
        if (!m_BranchList)
            return;

        for (i = 0; i < m_View.Branches.Count(); i++)
        {
            OZL_BranchView b = m_View.Branches[i];
            if (!b)
                continue;
            Widget row = GetGame().GetWorkspace().CreateWidgets(ROW_LAYOUT, m_BranchList);
            if (!row)
                continue;
            row.SetName("branch:" + b.Id);
            TextWidget name = TextWidget.Cast(row.FindAnyWidget("RowName"));
            if (name)
                name.SetText(b.Name);
            TextWidget count = TextWidget.Cast(row.FindAnyWidget("RowCount"));
            if (count)
            {
                int done = 0;
                for (int n = 0; n < b.Nodes.Count(); n++)
                {
                    if (b.Nodes[n] && b.Nodes[n].Status == "completed")
                        done++;
                }
                int total = b.Total;
                if (total < b.Nodes.Count())
                    total = b.Nodes.Count();
                count.SetText(done.ToString() + " / " + total.ToString());
            }
            bool picked = b.Id == m_Branch;
            Widget pick = row.FindAnyWidget("RowPick");
            if (pick)
                pick.Show(picked);
            Widget bar = row.FindAnyWidget("RowBar");
            if (bar)
                bar.Show(picked);
            m_RowWidgets.Insert(row);
        }
        m_BranchList.Update();
    }

    // Бали фракції: рядок на кожен тип, якого коштує ЦЯ гілка, з тим, що в
    // пулі. Типів у конфігу може бути три десятки -- показувати всі означає
    // показувати нулі, яких дерево не просить.
    private void PaintPoints()
    {
        int i;
        for (i = 0; i < m_PointWidgets.Count(); i++)
        {
            if (m_PointWidgets[i])
                m_PointWidgets[i].Unlink();
        }
        m_PointWidgets.Clear();
        if (!m_PointList)
            return;

        OZL_BranchView b = BranchOf(m_Branch);
        if (!b)
        {
            m_PointList.Update();
            return;
        }

        array<string> types = new array<string>();
        for (i = 0; i < b.Nodes.Count(); i++)
        {
            OZL_NodeView n = b.Nodes[i];
            if (!n)
                continue;
            for (int c = 0; c < n.Cost.Count(); c++)
            {
                OZL_KV kv = n.Cost[c];
                if (kv && IndexOfId(types, kv.Key) < 0)
                    types.Insert(kv.Key);
            }
        }

        for (i = 0; i < types.Count(); i++)
        {
            Widget row = GetGame().GetWorkspace().CreateWidgets(POINT_LAYOUT, m_PointList);
            if (!row)
                continue;
            TextWidget name = TextWidget.Cast(row.FindAnyWidget("PointName"));
            if (name)
                name.SetText(ShortPointName(types[i]));
            TextWidget have = TextWidget.Cast(row.FindAnyWidget("PointHave"));
            if (have)
            {
                int amount = PoolOf(types[i]);
                have.SetText(amount.ToString());
                if (amount > 0)
                    have.SetColor(OZ_Palette.OK);
                else
                    have.SetColor(OZ_Palette.FAINT);
            }
            m_PointWidgets.Insert(row);
        }
        m_PointList.Update();
    }

    // Дерево: рядок на рівень, комірки вузлів у рядок. Порядок рівнів --
    // зростання Tier; рівні без вузлів не створюються взагалі.
    private void PaintTree()
    {
        int i;
        for (i = 0; i < m_TierWidgets.Count(); i++)
        {
            if (m_TierWidgets[i])
                m_TierWidgets[i].Unlink();
        }
        m_TierWidgets.Clear();
        m_NodeWidgets.Clear();
        m_NodeIds.Clear();
        if (m_Lines)
            m_Lines.Clear();
        m_LinesAtX = -99999;
        m_LinesAtY = -99999;

        OZL_BranchView b = BranchOf(m_Branch);
        if (!b || !m_TierStack)
            return;

        // Які рівні взагалі є, за зростанням: беремо їх з вузлів, а не з
        // припущення "від 1 до N".
        array<int> tiers = new array<int>();
        for (i = 0; i < b.Nodes.Count(); i++)
        {
            OZL_NodeView seen = b.Nodes[i];
            if (!seen)
                continue;
            int tier = TierOf(seen);
            if (tiers.Find(tier) < 0)
                tiers.Insert(tier);
        }
        SortTiers(tiers);

        for (int t = 0; t < tiers.Count(); t++)
        {
            Widget rowRoot = GetGame().GetWorkspace().CreateWidgets(TIER_LAYOUT, m_TierStack);
            if (!rowRoot)
                continue;
            SpacerWidget row = SpacerWidget.Cast(rowRoot);
            if (row)
                row.SetContentAlignmentH(WidgetAlignment.WA_CENTER);
            m_TierWidgets.Insert(rowRoot);

            for (i = 0; i < b.Nodes.Count(); i++)
            {
                OZL_NodeView n = b.Nodes[i];
                if (!n)
                    continue;
                if (TierOf(n) != tiers[t])
                    continue;
                Widget cell = GetGame().GetWorkspace().CreateWidgets(NODE_LAYOUT, rowRoot);
                if (!cell)
                    continue;
                PaintNode(cell, n);
                m_NodeWidgets.Insert(cell);
                m_NodeIds.Insert(n.Id);
            }
            rowRoot.Update();
        }
        m_TierStack.Update();
        // Лінії -- наступним кадром: щойно створені віджети ще не розкладені,
        // і їхні екранні координати нульові.
        m_NeedLines = true;
    }

    // Місце рядка в масиві. ЧОМУ НЕ array.Find: на стенді 2026-09-20 воно
    // повертало -1 для рядка, який у масиві лежав (жодної лінії між вузлами,
    // хоча батьки приїхали) -- порівняння йде не по значенню. ZP обходив
    // масив руками з тієї ж причини.
    private static int IndexOfId(array<string> ids, string id)
    {
        for (int i = 0; i < ids.Count(); i++)
        {
            if (ids[i] == id)
                return i;
        }
        return -1;
    }

    // Рівень вузла в межах, які екран уміє показати.
    private static int TierOf(OZL_NodeView n)
    {
        int tier = n.Tier;
        if (tier < 1)
            tier = 1;
        if (tier > MAX_TIER)
            tier = MAX_TIER;
        return tier;
    }

    // Порядок рівнів. Масив короткий (рівнів одиниці), тому бульбашка --
    // і вона не залежить від того, чи має Enforce свій sort для int.
    private static void SortTiers(array<int> tiers)
    {
        for (int i = 0; i < tiers.Count(); i++)
        {
            for (int j = i + 1; j < tiers.Count(); j++)
            {
                if (tiers[j] < tiers[i])
                {
                    int swap = tiers[i];
                    tiers[i] = tiers[j];
                    tiers[j] = swap;
                }
            }
        }
    }

    private void PaintNode(Widget cell, OZL_NodeView n)
    {
        Widget hit = cell.FindAnyWidget("NodeHit");
        if (hit)
            hit.SetName("node:" + n.Id);

        TextWidget name = TextWidget.Cast(cell.FindAnyWidget("NodeName"));
        if (name)
        {
            name.SetText(n.Name);
            if (n.Status == "locked")
                name.SetColor(OZ_Palette.MUTED);
            else
                name.SetColor(OZ_Palette.TEXT);
        }

        Widget top = cell.FindAnyWidget("NodeTop");
        if (top)
            top.SetColor(StatusColor(n.Status));

        ImageWidget icon = ImageWidget.Cast(cell.FindAnyWidget("NodeIcon"));
        if (icon)
        {
            if (n.Icon != "")
            {
                icon.LoadImageFile(0, n.Icon);
                icon.SetColor(StatusColor(n.Status));
                icon.Show(true);
            }
            else
            {
                icon.Show(false);
            }
        }

        TextWidget cost = TextWidget.Cast(cell.FindAnyWidget("NodeCost"));
        if (cost)
        {
            if (n.Status == "completed")
            {
                cost.SetText(Words("STR_OZL_TREE_COMPLETED"));
                cost.SetColor(OZ_Palette.OK);
            }
            else if (n.Status == "researching")
            {
                cost.SetText(Words("STR_OZL_TREE_LEFT") + " " + Duration(LeftOf(n)));
                cost.SetColor(OZ_Palette.ALERT);
            }
            else
            {
                cost.SetText(ShortCost(n));
                cost.SetColor(OZ_Palette.MUTED);
            }
        }

        Widget bar = cell.FindAnyWidget("NodeProgress");
        if (bar)
            bar.Show(n.Status == "researching");
        PaintNodeProgress(cell, n);
    }

    // Ціна в комірці мусить лишатися ОДНИМ рядком: під неї в картці вузла
    // близько 136 одиниць, і рядок, довший за них, рушій не переносить і не
    // стискає -- він його просто ріже (стенд 2026-09-20: "15 Біологія,
    // лабораторні 2" обірвалося на "15 Біологія, лаборато"). Тому тут лише
    // перша складова коротким іменем і лічильник решти; увесь перелік
    // гравець читає в картці праворуч, де місця вистачає.
    private string ShortCost(OZL_NodeView n)
    {
        string s = "";
        int rest = 0;
        int i;
        for (i = 0; i < n.Cost.Count(); i++)
        {
            OZL_KV kv = n.Cost[i];
            if (!kv)
                continue;
            if (s == "")
                s = kv.Value.ToString() + " " + TinyPointName(kv.Key);
            else
                rest++;
        }
        for (i = 0; i < n.Items.Count(); i++)
        {
            OZL_ItemView iv = n.Items[i];
            if (!iv)
                continue;
            if (s == "")
                s = iv.Qty.ToString() + " " + ItemLabel(iv);
            else
                rest++;
        }
        if (rest > 0)
            s += " +" + rest.ToString();
        return s;
    }

    private int LeftOf(OZL_NodeView n)
    {
        if (!m_View)
            return 0;
        int now = m_View.Now + m_ViewAge;
        int left = n.EndSec - now;
        if (left < 0)
            left = 0;
        return left;
    }

    private void PaintNodeProgress(Widget cell, OZL_NodeView n)
    {
        if (n.Status != "researching" || n.Duration <= 0)
            return;
        Widget bar = cell.FindAnyWidget("NodeProgress");
        Widget fill = cell.FindAnyWidget("NodeProgressFill");
        if (!bar || !fill)
            return;
        float frac = 1.0 - LeftOf(n) / n.Duration;
        if (frac < 0)
            frac = 0;
        if (frac > 1)
            frac = 1;
        float bw;
        float bh;
        bar.GetSize(bw, bh);
        fill.SetSize(bw * frac, bh);
    }

    // Лінії батько -> дитина на канві, у пікселях відносно її кута: низ
    // батька (посередині) до верху дитини -- дерево росте згори вниз, рівень
    // = рядок. Прямокутники беруться в рушія, тож лінії йдуть за будь-якою
    // розкладкою, яку він дав рядкам.
    private void DrawLines()
    {
        if (!m_Lines)
            return;
        m_Lines.Clear();
        FirstCardPos(m_LinesAtX, m_LinesAtY);
        OZL_BranchView b = BranchOf(m_Branch);
        if (!b)
            return;

        float cx;
        float cy;
        float cw;
        float ch;
        m_Lines.GetScreenPos(cx, cy);
        m_Lines.GetScreenSize(cw, ch);
        int drawn = 0;

        for (int i = 0; i < m_NodeIds.Count(); i++)
        {
            OZL_NodeView child = NodeOf(m_NodeIds[i]);
            Widget cellChild = null;
            if (i < m_NodeWidgets.Count())
                cellChild = m_NodeWidgets[i];
            Widget cardChild = null;
            if (cellChild)
                cardChild = cellChild.FindAnyWidget("NodeCard");
            if (!child || !cellChild || !cardChild)
                continue;
            float x1;
            float y1;
            float w1;
            float h1;
            cardChild.GetScreenPos(x1, y1);
            cardChild.GetScreenSize(w1, h1);

            for (int p = 0; p < child.Parents.Count(); p++)
            {
                int at = IndexOfId(m_NodeIds, child.Parents[p]);
                if (at < 0)
                    continue;   // батька не видно (інша гілка або туман) -- лінії немає
                Widget cellParent = m_NodeWidgets[at];
                if (!cellParent)
                    continue;
                Widget cardParent = cellParent.FindAnyWidget("NodeCard");
                if (!cardParent)
                    continue;
                float x0;
                float y0;
                float w0;
                float h0;
                cardParent.GetScreenPos(x0, y0);
                cardParent.GetScreenSize(w0, h0);

                float px = x0 + w0 / 2 - cx;
                float py = y0 + h0 - cy;
                float qx = x1 + w1 / 2 - cx;
                float qy = y1 - cy;
                // Обидва кінці поза полотном -- лінія не потрібна; один за
                // краєм -- обрізаємо по краю, бо канва не клацає сама.
                bool above = py < 0 && qy < 0;
                bool below = py > ch && qy > ch;
                if (above || below)
                    continue;
                py = Math.Clamp(py, 0, ch);
                qy = Math.Clamp(qy, 0, ch);
                int colour = StatusColor(child.Status);
                if (child.Status == "locked")
                    colour = OZ_Palette.EDGE;
                float midY = (py + qy) / 2;
                m_Lines.DrawLine(px, py, px, midY, LINE_W, colour);
                m_Lines.DrawLine(px, midY, qx, midY, LINE_W, colour);
                m_Lines.DrawLine(qx, midY, qx, qy, LINE_W, colour);
                drawn++;
            }
        }
        OZL_Log.Dbg("tree: " + m_NodeIds.Count().ToString() + " node(s), " + m_TierWidgets.Count().ToString() + " tier(s), " + drawn.ToString() + " line(s)");
    }

    // Де зараз перша картка дерева (екранні координати). Без вузлів -- нікуди.
    private void FirstCardPos(out float x, out float y)
    {
        x = -99999;
        y = -99999;
        if (m_NodeWidgets.Count() == 0 || !m_NodeWidgets[0])
            return;
        Widget card = m_NodeWidgets[0].FindAnyWidget("NodeCard");
        if (!card)
            return;
        card.GetScreenPos(x, y);
    }

    private bool LinesMoved()
    {
        float x;
        float y;
        FirstCardPos(x, y);
        if (x < -99998)
            return false;
        bool movedX = Math.AbsFloat(x - m_LinesAtX) > 0.5;
        bool movedY = Math.AbsFloat(y - m_LinesAtY) > 0.5;
        return movedX || movedY;
    }

    private void ClearCard()
    {
        if (m_CardName)
            m_CardName.SetText(Words("STR_OZL_TREE_PICK"));
        if (m_CardMeta)
            m_CardMeta.SetText("");
        if (m_CardDesc)
            m_CardDesc.SetText("");
        ClearCostRows();
        if (m_CardTime)
            m_CardTime.SetText("");
        if (m_CardStatus)
            m_CardStatus.SetText("");
        if (m_BtnResearch)
            m_BtnResearch.Show(false);
    }

    private void ClearCostRows()
    {
        for (int i = 0; i < m_CostWidgets.Count(); i++)
        {
            if (m_CostWidgets[i])
                m_CostWidgets[i].Unlink();
        }
        m_CostWidgets.Clear();
        if (m_CostList)
            m_CostList.Update();
    }

    private void PaintCard()
    {
        OZL_NodeView n = NodeOf(m_Node);
        if (!n)
        {
            ClearCard();
            return;
        }
        if (m_CardName)
            m_CardName.SetText(n.Name);
        if (m_CardMeta)
        {
            OZL_BranchView b = BranchOf(m_Branch);
            string meta = "";
            if (b)
                meta = b.Name + " · ";
            meta += Words("STR_OZL_TREE_TIER") + " " + n.Tier.ToString();
            string after = ParentNames(n);
            if (after != "")
                meta += " · " + Words("STR_OZL_TREE_AFTER") + " " + after;
            m_CardMeta.SetText(meta);
        }
        if (m_CardDesc)
            m_CardDesc.SetText(n.Desc);

        PaintCost(n);

        if (m_CardTime)
        {
            if (n.Status == "researching")
                m_CardTime.SetText(Words("STR_OZL_TREE_LEFT") + " " + Duration(LeftOf(n)));
            else if (n.Duration > 0)
                m_CardTime.SetText(Words("STR_OZL_TREE_TIME") + ": " + Duration(n.Duration));
            else
                m_CardTime.SetText(Words("STR_OZL_TREE_INSTANT"));
        }
        if (m_CardStatus)
        {
            m_CardStatus.SetText(Words(StatusKey(n.Status)));
            m_CardStatus.SetColor(StatusColor(n.Status));
        }
        if (m_BtnResearch)
            m_BtnResearch.Show(n.Status == "available" && m_View.MaySpend);
    }

    private string ParentNames(OZL_NodeView n)
    {
        string s = "";
        for (int i = 0; i < n.Parents.Count(); i++)
        {
            OZL_NodeView p = NodeOf(n.Parents[i]);
            if (!p)
                continue;
            if (s != "")
                s += ", ";
            s += p.Name;
        }
        return s;
    }

    // Ціна в картці: рядок на кожен тип балів і на кожен матеріал, з тим, що
    // фракція має. Рядків рівно стільки, скільки коштує вузол.
    private void PaintCost(OZL_NodeView n)
    {
        ClearCostRows();
        if (!m_CostList)
            return;
        int i;
        for (i = 0; i < n.Cost.Count(); i++)
        {
            OZL_KV kv = n.Cost[i];
            if (!kv)
                continue;
            int have = PoolOf(kv.Key);
            AddCostRow(PointName(kv.Key), kv.Value.ToString() + " / " + have.ToString(), have >= kv.Value);
        }
        for (i = 0; i < n.Items.Count(); i++)
        {
            OZL_ItemView iv = n.Items[i];
            if (!iv)
                continue;
            AddCostRow(ItemLabel(iv), iv.Qty.ToString(), true);
        }
        m_CostList.Update();
    }

    private void AddCostRow(string label, string value, bool enough)
    {
        Widget row = GetGame().GetWorkspace().CreateWidgets(COST_LAYOUT, m_CostList);
        if (!row)
            return;
        TextWidget name = TextWidget.Cast(row.FindAnyWidget("CostName"));
        if (name)
            name.SetText(label);
        TextWidget need = TextWidget.Cast(row.FindAnyWidget("CostNeed"));
        Widget bar = row.FindAnyWidget("CostBar");
        int colour = OZ_Palette.OK;
        if (!enough)
            colour = OZ_Palette.BAD;
        if (need)
        {
            need.SetText(value);
            need.SetColor(colour);
        }
        if (bar)
            bar.SetColor(colour);
        m_CostWidgets.Insert(row);
    }

    // Смуга проєкту в комірці вузла й залишок у картці -- раз на секунду.
    private void PaintProgress()
    {
        int i;
        for (i = 0; i < m_NodeIds.Count(); i++)
        {
            OZL_NodeView n = NodeOf(m_NodeIds[i]);
            Widget cell = m_NodeWidgets[i];
            if (!n || !cell || n.Status != "researching")
                continue;
            PaintNodeProgress(cell, n);
            TextWidget cost = TextWidget.Cast(cell.FindAnyWidget("NodeCost"));
            if (cost)
                cost.SetText(Words("STR_OZL_TREE_LEFT") + " " + Duration(LeftOf(n)));
        }
        OZL_NodeView picked = NodeOf(m_Node);
        if (picked && picked.Status == "researching" && m_CardTime)
            m_CardTime.SetText(Words("STR_OZL_TREE_LEFT") + " " + Duration(LeftOf(picked)));
    }

    private static string Duration(int sec)
    {
        if (sec < 60)
            return sec.ToString() + " s";
        if (sec < 3600)
            return (sec / 60).ToString() + " min";
        int h = sec / 3600;
        int m = (sec - h * 3600) / 60;
        return h.ToString() + " h " + m.ToString() + " min";
    }

    private void Hint(string text)
    {
        if (m_Hint)
            m_Hint.SetText(text);
    }

    // ---------- миша ----------

    override bool OnMouseEnter(Widget w, int x, int y)
    {
        TintNode(w, true);
        return super.OnMouseEnter(w, x, y);
    }

    override bool OnMouseLeave(Widget w, Widget enterW, int x, int y)
    {
        TintNode(w, false);
        return super.OnMouseLeave(w, enterW, x, y);
    }

    // Підсвітка картки під мишею. Кнопка лежить ПІД карткою, тож фарбуємо не
    // її, а тло картки поруч.
    private void TintNode(Widget w, bool on)
    {
        if (!w)
            return;
        if (w.GetName().IndexOf("node:") != 0)
            return;
        Widget cell = w.GetParent();
        if (!cell)
            return;
        Widget bg = cell.FindAnyWidget("NodeBg");
        if (!bg)
            return;
        if (on)
            bg.SetColor(OZ_Palette.PICK);
        else
            bg.SetColor(OZ_Palette.RAISED);
    }

    // ---------- клавіші ----------

    override bool OnClick(Widget w, int x, int y, int button)
    {
        if (!w)
            return super.OnClick(w, x, y, button);
        string nm = w.GetName();

        if (nm == "BtnClose")
        {
            Close();
            return true;
        }

        if (nm == "BtnResearch")
        {
            OZL_NodeView n = NodeOf(m_Node);
            if (!n || n.Status != "available")
                return true;
            OZ_Rpc.ServiceRequest(OZL_Const.SERVICE, OZL_Const.OP_RESEARCH, "{\"NodeId\":\"" + n.Id + "\"}");
            Hint(Words("STR_OZL_TREE_ASKING"));
            return true;
        }

        if (nm.IndexOf("branch:") == 0)
        {
            m_Branch = nm.Substring(7, nm.Length() - 7);
            m_Node = "";
            PaintHeader();
            PaintBranches();
            PaintPoints();
            PaintTree();
            PaintCard();
            return true;
        }

        if (nm.IndexOf("node:") == 0)
        {
            m_Node = nm.Substring(5, nm.Length() - 5);
            PaintCard();
            return true;
        }

        return super.OnClick(w, x, y, button);
    }
}

#endif
