// Панель «RESEARCH» в адмінському вікні OpenZone: фракції з пулами, сброс,
// нарахування, завершення вузла, перечитування конфігів, перехід до
// редактора конфігів ядра. Чіпляється вкладкою через modded class -- ядро
// про дослідження не знає й знати не мусить.
//
// Гарди: NO_GUI -- сервер компілює Mission без UI; AVPPAdminTools і
// OpenZone_VPP -- імена класів CfgMods (їх авто-дефайнить рушій).
//
// Розмітка -- з опису ui/OpenZone_Research_VPP/oz_research_vpp_pane.json
// (layout_build); тут лише імена віджетів. Незворотні дії -- у два
// натискання по тій самій фракції, як і всюди у вікні: модальні вікна у VPP
// -- пастка.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    private ref array<ref OZL_AdminOwner> m_ResOwners;
    private ref array<string> m_ResCfgNames;
    private int  m_ResPicked    = -1;
    private int  m_ResCfgPicked = -1;
    private bool m_ResResetArmed  = false;
    private bool m_ResReloadArmed = false;
    private string m_ResArmedOwner = "";
    // Перемальовування списку кличе SelectRow, рушій відповідає OnItemSelected
    // -- прапорець рве це коло (як у ядрі й у сусідніх панелях).
    private bool m_ResRepaint = false;

    override void OnCreate(Widget RootW)
    {
        super.OnCreate(RootW);
        if (!M_SUB_WIDGET)
            return;

        m_ResOwners   = new array<ref OZL_AdminOwner>();
        m_ResCfgNames = new array<string>();

        Widget pane = GetGame().GetWorkspace().CreateWidgets("OpenZone_Research_VPP/gui/layouts/oz_research_vpp_pane.layout", M_SUB_WIDGET);
        if (!pane)
        {
            OZL_Log.Error("research vpp pane: layout failed to load");
            return;
        }

        RegisterPane("research", "RESEARCH", pane, "ResHint");

        // Власний слухач відповідей: список і операції -- наші, ядро про них
        // не знає.
        OZ_ClientState.AdminWatch().Insert(this.OnResearchResponse);

        m_ResCfgNames.Insert(OZL_Config.TAG_SETTINGS);
        m_ResCfgNames.Insert(OZL_Config.TAG_POINT_TYPES);
        m_ResCfgNames.Insert(OZL_Config.TAG_OWNERS);
        m_ResCfgNames.Insert(OZL_Config.TAG_RULES);
        m_ResCfgNames.Insert(OZL_Config.TAG_TREE);
        m_ResCfgNames.Insert(OZL_Config.TAG_DATA_ITEMS);
        m_ResCfgNames.Insert(OZL_Config.TAG_MODULES);
        m_ResCfgNames.Insert(OZL_Config.TAG_SAMPLE_TYPES);
        m_ResCfgNames.Insert(OZL_Config.TAG_STATICS);
        RepaintConfigs();
    }

    void ~OZ_VppAdminMenu()
    {
        OZ_ClientState.AdminWatch().Remove(this.OnResearchResponse);
    }

    override void OnPaneShown(string id)
    {
        super.OnPaneShown(id);
        if (id == "research")
            AskResearchList();
    }

    protected void AskResearchList()
    {
        Ask(OZL_Const.SECTION, "list", "{}");
    }

    void OnResearchResponse(string section, string op, bool ok, string json, string error)
    {
        if (section != OZL_Const.SECTION)
            return;

        m_ResResetArmed  = false;
        m_ResReloadArmed = false;

        if (!ok)
        {
            Hint(op + ": " + Words(error));
            return;
        }

        OZL_AdminList l = new OZL_AdminList();
        string err;
        if (!JsonFileLoader<OZL_AdminList>.LoadData(json, l, err))
        {
            Hint("research: unreadable answer (" + err + ")");
            return;
        }

        // Копія, яку збудував скрипт: те, що приїхало, живе лише до розбору.
        m_ResOwners.Clear();
        for (int i = 0; i < l.Owners.Count(); i++)
        {
            OZL_AdminOwner src = l.Owners[i];
            if (!src)
                continue;
            OZL_AdminOwner o = new OZL_AdminOwner();
            o.Id        = src.Id;
            o.Name      = src.Name;
            o.Pool      = src.Pool;
            o.Completed = src.Completed;
            o.Active    = src.Active;
            o.Known     = src.Known;
            m_ResOwners.Insert(o);
        }
        if (m_ResPicked >= m_ResOwners.Count())
            m_ResPicked = -1;

        m_ResRepaint = true;
        RepaintOwners();
        m_ResRepaint = false;
        PaintPicked();

        TextWidget st = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("ResStatics"));
        if (st)
            st.SetText("statics: " + l.Statics);

        if (op == "list")
            Hint(m_ResOwners.Count().ToString() + " faction(s); " + l.Counters);
        else
            Hint(op + ": done");
    }

    protected void RepaintOwners()
    {
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("ResOwners"));
        if (!lb)
            return;
        lb.ClearItems();
        for (int i = 0; i < m_ResOwners.Count(); i++)
        {
            OZL_AdminOwner o = m_ResOwners[i];
            string line = "";
            if (i == m_ResPicked)
                line = "> ";
            line += o.Id;
            if (o.Name != "" && o.Name != o.Id)
                line += "  --  " + o.Name;
            if (o.Known == 1)
            {
                line += "  |  " + o.Pool;
                line += "  |  " + o.Completed.ToString() + " / " + o.Active.ToString();
            }
            else
            {
                line += "  |  (no state yet)";
            }
            lb.AddItem(line, NULL, 0);
            if (i == m_ResPicked)
                lb.SelectRow(i);
        }
    }

    protected void RepaintConfigs()
    {
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("ResConfigs"));
        if (!lb)
            return;
        lb.ClearItems();
        for (int i = 0; i < m_ResCfgNames.Count(); i++)
        {
            string line = "";
            if (i == m_ResCfgPicked)
                line = "> ";
            lb.AddItem(line + m_ResCfgNames[i], NULL, 0);
            if (i == m_ResCfgPicked)
                lb.SelectRow(i);
        }
    }

    protected void PaintPicked()
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("ResPicked"));
        if (!t)
            return;
        string owner = PickedOwner();
        if (owner == "")
            t.SetText("pick a faction on the list");
        else
            t.SetText("faction: " + owner);
    }

    protected string PickedOwner()
    {
        if (m_ResPicked < 0 || m_ResPicked >= m_ResOwners.Count())
            return "";
        return m_ResOwners[m_ResPicked].Id;
    }

    override bool OnItemSelected(Widget w, int x, int y, int row, int column, int oldRow, int oldColumn)
    {
        if (!M_SUB_WIDGET || m_ResRepaint || !w)
            return super.OnItemSelected(w, x, y, row, column, oldRow, oldColumn);

        string nm = w.GetName();
        if (nm == "ResOwners")
        {
            if (row >= 0 && row < m_ResOwners.Count())
            {
                m_ResPicked = row;
                m_ResResetArmed = false;
                m_ResRepaint = true;
                RepaintOwners();
                m_ResRepaint = false;
                PaintPicked();
                Hint("faction " + PickedOwner() + ": grant, complete a node, or reset (twice)");
            }
            return true;
        }
        if (nm == "ResConfigs")
        {
            if (row >= 0 && row < m_ResCfgNames.Count())
            {
                m_ResCfgPicked = row;
                m_ResRepaint = true;
                RepaintConfigs();
                m_ResRepaint = false;
                Hint("config " + m_ResCfgNames[row] + ": EDIT opens it in the CONFIG pane");
            }
            return true;
        }
        return super.OnItemSelected(w, x, y, row, column, oldRow, oldColumn);
    }

    override bool OnClick(Widget w, int x, int y, int button)
    {
        if (!M_SUB_WIDGET || !w)
            return super.OnClick(w, x, y, button);

        string nm = w.GetName();

        if (nm == "BtnRefresh")
        {
            AskResearchList();
            return true;
        }

        if (nm == "BtnReload")
        {
            if (!m_ResReloadArmed)
            {
                m_ResReloadArmed = true;
                Hint("press RELOAD CONFIGS again to re-read the nine files and the state folder");
                return true;
            }
            m_ResReloadArmed = false;
            Ask(OZL_Const.SECTION, "reload", "{}");
            Hint("reloading...");
            return true;
        }

        if (nm == "BtnReset")
        {
            string owner = PickedOwner();
            if (owner == "")
            {
                Hint("pick a faction on the list first");
                return true;
            }
            // Підтвердження ПО ТІЙ САМІЙ фракції: зміна вибору знімає курок.
            if (!m_ResResetArmed || m_ResArmedOwner != owner)
            {
                m_ResResetArmed = true;
                m_ResArmedOwner = owner;
                Hint("press RESET FACTION again to wipe the pool, nodes and projects of " + owner + " and stop its stations");
                return true;
            }
            m_ResResetArmed = false;
            Ask(OZL_Const.SECTION, "reset:" + owner, "{}");
            Hint("resetting " + owner + "...");
            return true;
        }

        if (nm == "BtnGrant")
        {
            string gOwner = PickedOwner();
            string type = GetEdit("GrantType");
            string n = GetEdit("GrantN");
            type.TrimInPlace();
            n.TrimInPlace();
            if (gOwner == "" || type == "" || n.ToInt() <= 0)
            {
                Hint("pick a faction, then a point type id and an amount above zero");
                return true;
            }
            Ask(OZL_Const.SECTION, "grant:" + gOwner + ":" + type + ":" + n.ToInt().ToString(), "{}");
            Hint("granting " + n + " " + type + " to " + gOwner + "...");
            return true;
        }

        if (nm == "BtnComplete")
        {
            string cOwner = PickedOwner();
            string node = GetEdit("NodeId");
            node.TrimInPlace();
            if (cOwner == "" || node == "")
            {
                Hint("pick a faction, then type the node id");
                return true;
            }
            Ask(OZL_Const.SECTION, "complete:" + cOwner + ":" + node, "{}");
            Hint("completing " + node + " for " + cOwner + "...");
            return true;
        }

        if (nm == "BtnEditCfg")
        {
            if (m_ResCfgPicked < 0 || m_ResCfgPicked >= m_ResCfgNames.Count())
            {
                Hint("pick a config on the list first");
                return true;
            }
            string name = m_ResCfgNames[m_ResCfgPicked];
            ShowPane("config");
            AskCfg(name);
            return true;
        }

        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
