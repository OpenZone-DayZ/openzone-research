// Екран дерева досліджень (меню 135): відповідь служби `tree` як вона є,
// намальована по описах oz_research_tree.json і oz_research_node.json.
//
// Дані -- лише OZL_TreeView: меню не знає конфігів і не рахує статусів, воно
// показує те, що сказав сервер, і просить дослідити вузол. Відмова
// приходить ключем рядка -- її показує сповіщення, як і решту відповідей
// мода. Escape закриває. Ані пікселів у коді, ані власних кольорів: імена
// віджетів з опису, кольори -- палітра ядра.

#ifndef NO_GUI

class OZL_TreeMenu : UIScriptedMenu
{
    static const string LAYOUT      = "OpenZone_Research/gui/layouts/oz_research_tree.layout";
    static const string ROW_LAYOUT  = "OpenZone_Research/gui/layouts/oz_research_branch_row.layout";
    static const string NODE_LAYOUT = "OpenZone_Research/gui/layouts/oz_research_node.layout";

    // Крок сітки вузлів у одиницях розкладки: вузол 176 x 64, проміжок 44
    // під лінії між стовпцями.
    static const float NODE_W    = 176;
    static const float NODE_H    = 64;
    static const float COL_STEP  = 220;
    static const float ROW_STEP  = 84;
    static const float LINE_W    = 2;

    private static OZL_TreeMenu s_Open;

    private ref OZL_TreeView m_View;
    private string m_Branch = "";
    private string m_Node   = "";
    // Коли приїхала відповідь -- залишок проєкту рахується від серверної
    // секунди в ній, а не від годинника клієнта.
    private float m_ViewAge = 0;
    private bool  m_NeedLines = false;
    private float m_Tick = 0;

    private Widget       m_Chip;
    private TextWidget   m_OwnerName;
    private TextWidget   m_PoolLine;
    private Widget       m_BranchList;
    private Widget       m_TreeArea;
    private ImageWidget  m_TreeBg;
    private CanvasWidget m_Lines;
    private TextWidget   m_CardName;
    private TextWidget   m_CardDesc;
    private TextWidget   m_CardCost;
    private TextWidget   m_CardItems;
    private TextWidget   m_CardTime;
    private TextWidget   m_CardStatus;
    private Widget       m_ProgressBox;
    private Widget       m_Progress;
    private Widget       m_BtnResearch;
    private TextWidget   m_Hint;

    private ref array<Widget> m_RowWidgets;
    private ref array<Widget> m_NodeWidgets;
    private ref array<string> m_NodeIds;

    void OZL_TreeMenu()
    {
        m_RowWidgets  = new array<Widget>();
        m_NodeWidgets = new array<Widget>();
        m_NodeIds     = new array<string>();
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
        m_TreeArea    = layoutRoot.FindAnyWidget("TreeArea");
        m_TreeBg      = ImageWidget.Cast(layoutRoot.FindAnyWidget("TreeBg"));
        m_Lines       = CanvasWidget.Cast(layoutRoot.FindAnyWidget("TreeLines"));
        m_CardName    = TextWidget.Cast(layoutRoot.FindAnyWidget("CardName"));
        m_CardDesc    = TextWidget.Cast(layoutRoot.FindAnyWidget("CardDesc"));
        m_CardCost    = TextWidget.Cast(layoutRoot.FindAnyWidget("CardCost"));
        m_CardItems   = TextWidget.Cast(layoutRoot.FindAnyWidget("CardItems"));
        m_CardTime    = TextWidget.Cast(layoutRoot.FindAnyWidget("CardTime"));
        m_CardStatus  = TextWidget.Cast(layoutRoot.FindAnyWidget("CardStatus"));
        m_ProgressBox = layoutRoot.FindAnyWidget("CardProgressBox");
        m_Progress    = layoutRoot.FindAnyWidget("CardProgress");
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
        PaintNodes();
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
            string line = "";
            for (int i = 0; i < m_View.Pool.Count(); i++)
            {
                OZL_KV kv = m_View.Pool[i];
                if (!kv || kv.Value <= 0)
                    continue;
                if (line != "")
                    line += "   ";
                line += PointName(kv.Key) + " " + kv.Value.ToString();
            }
            if (line == "")
                line = Words("STR_OZL_TREE_POOL_EMPTY");
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
                count.SetText(done.ToString() + " / " + b.Nodes.Count().ToString());
            }
            Widget pick = row.FindAnyWidget("RowPick");
            if (pick)
                pick.Show(b.Id == m_Branch);
            m_RowWidgets.Insert(row);
        }
        m_BranchList.Update();
    }

    private void PaintNodes()
    {
        int i;
        for (i = 0; i < m_NodeWidgets.Count(); i++)
        {
            if (m_NodeWidgets[i])
                m_NodeWidgets[i].Unlink();
        }
        m_NodeWidgets.Clear();
        m_NodeIds.Clear();
        if (m_Lines)
            m_Lines.Clear();

        OZL_BranchView b = BranchOf(m_Branch);
        if (!b || !m_TreeArea)
            return;

        for (i = 0; i < b.Nodes.Count(); i++)
        {
            OZL_NodeView n = b.Nodes[i];
            if (!n)
                continue;
            Widget w = GetGame().GetWorkspace().CreateWidgets(NODE_LAYOUT, m_TreeArea);
            if (!w)
                continue;
            w.SetName("node:" + n.Id);
            w.SetPos(n.Col * COL_STEP, n.Row * ROW_STEP);
            TextWidget name = TextWidget.Cast(w.FindAnyWidget("NodeName"));
            if (name)
                name.SetText(n.Name);
            TextWidget cost = TextWidget.Cast(w.FindAnyWidget("NodeCost"));
            if (cost)
                cost.SetText(CostLine(n, true));
            Widget bar = w.FindAnyWidget("NodeBar");
            if (bar)
                bar.SetColor(StatusColor(n.Status));
            m_NodeWidgets.Insert(w);
            m_NodeIds.Insert(n.Id);
        }
        // Лінії -- наступним кадром: щойно створені віджети ще не розкладені,
        // і їхні екранні координати нульові.
        m_NeedLines = true;
    }

    // Вартість рядком: "<ім'я типу> <n>" через дві пробіли; коротко -- без
    // імен, лише числа, для картки вузла в сітці.
    private string CostLine(OZL_NodeView n, bool shortForm)
    {
        string s = "";
        for (int i = 0; i < n.Cost.Count(); i++)
        {
            OZL_KV kv = n.Cost[i];
            if (!kv)
                continue;
            if (s != "")
            {
                if (shortForm && n.Cost.Count() > 1)
                    s += " + ";
                else
                    s += "  ";
            }
            if (shortForm)
            {
                // У вузлі сітки місця на 156 одиниць: один тип -- число з id,
                // кілька -- лише числа, імена скаже картка.
                if (n.Cost.Count() == 1)
                    s += kv.Value.ToString() + " " + kv.Key;
                else
                    s += kv.Value.ToString();
            }
            else
                s += PointName(kv.Key) + " " + kv.Value.ToString() + " (" + PoolOf(kv.Key).ToString() + ")";
        }
        return s;
    }

    // Лінії батько -> дитина на канві, у пікселях відносно її кута: правий
    // край батька (посередині) до лівого краю дитини, кольором статусу дитини --
    // дерево росте зліва направо, рівень = стовпець.
    private void DrawLines()
    {
        if (!m_Lines)
            return;
        m_Lines.Clear();
        OZL_BranchView b = BranchOf(m_Branch);
        if (!b)
            return;
        float cx;
        float cy;
        m_Lines.GetScreenPos(cx, cy);

        for (int i = 0; i < m_NodeIds.Count(); i++)
        {
            OZL_NodeView child = NodeOf(m_NodeIds[i]);
            Widget cw = m_NodeWidgets[i];
            if (!child || !cw)
                continue;
            float x1;
            float y1;
            float w1;
            float h1;
            cw.GetScreenPos(x1, y1);
            cw.GetScreenSize(w1, h1);
            for (int p = 0; p < child.Parents.Count(); p++)
            {
                int at = m_NodeIds.Find(child.Parents[p]);
                if (at < 0)
                    continue;   // батько в іншій гілці -- лінії немає
                Widget pw = m_NodeWidgets[at];
                if (!pw)
                    continue;
                float x0;
                float y0;
                float w0;
                float h0;
                pw.GetScreenPos(x0, y0);
                pw.GetScreenSize(w0, h0);
                m_Lines.DrawLine(x0 + w0 - cx, y0 + h0 / 2 - cy, x1 - cx, y1 + h1 / 2 - cy, LINE_W, StatusColor(child.Status));
            }
        }
    }

    private void ClearCard()
    {
        if (m_CardName)
            m_CardName.SetText(Words("STR_OZL_TREE_PICK"));
        if (m_CardDesc)
            m_CardDesc.SetText("");
        if (m_CardCost)
            m_CardCost.SetText("");
        if (m_CardItems)
            m_CardItems.SetText("");
        if (m_CardTime)
            m_CardTime.SetText("");
        if (m_CardStatus)
            m_CardStatus.SetText("");
        if (m_ProgressBox)
            m_ProgressBox.Show(false);
        if (m_BtnResearch)
            m_BtnResearch.Show(false);
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
        if (m_CardDesc)
            m_CardDesc.SetText(n.Desc);
        if (m_CardCost)
            m_CardCost.SetText(Words("STR_OZL_TREE_COST") + ": " + CostLine(n, false));
        if (m_CardItems)
        {
            string items = "";
            for (int i = 0; i < n.Items.Count(); i++)
            {
                if (items != "")
                    items += ", ";
                items += n.Items[i];
            }
            if (items == "")
                m_CardItems.SetText("");
            else
                m_CardItems.SetText(Words("STR_OZL_TREE_ITEMS") + ": " + items);
        }
        if (m_CardTime)
        {
            if (n.Duration > 0)
                m_CardTime.SetText(Words("STR_OZL_TREE_TIME") + ": " + Duration(n.Duration));
            else
                m_CardTime.SetText(Words("STR_OZL_TREE_INSTANT"));
        }
        if (m_CardStatus)
        {
            m_CardStatus.SetText(Words(StatusKey(n.Status)));
            m_CardStatus.SetColor(StatusColor(n.Status));
        }
        if (m_ProgressBox)
            m_ProgressBox.Show(n.Status == "researching");
        PaintProgress();
        if (m_BtnResearch)
            m_BtnResearch.Show(n.Status == "available" && m_View.MaySpend);
    }

    // Смуга проєкту: частка часу, що минула, від відповіді сервера плюс
    // секунди, які клієнт відрахував сам.
    private void PaintProgress()
    {
        OZL_NodeView n = NodeOf(m_Node);
        if (!n || n.Status != "researching" || !m_Progress || !m_ProgressBox || n.Duration <= 0)
            return;
        int now = m_View.Now + m_ViewAge;
        int left = n.EndSec - now;
        if (left < 0)
            left = 0;
        float frac = 1.0 - left / n.Duration;
        if (frac < 0)
            frac = 0;
        if (frac > 1)
            frac = 1;
        float bw;
        float bh;
        m_ProgressBox.GetScreenSize(bw, bh);
        float pw = bw * frac;
        if (pw < 1)
            pw = 1;
        m_Progress.SetScreenSize(pw, bh);
        if (m_CardTime)
            m_CardTime.SetText(Words("STR_OZL_TREE_LEFT") + ": " + Duration(left));
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
            PaintBranches();
            PaintNodes();
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
