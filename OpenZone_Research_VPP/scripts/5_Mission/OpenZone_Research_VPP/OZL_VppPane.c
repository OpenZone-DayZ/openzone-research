// Панель «RESEARCH» в адмінському вікні OpenZone. З 2026-11-09 це редактор
// досліджень (docs/specs/2026-11-09-research-editor-vpp-design.md): ряд
// підвкладок, по сторінці на підвкладку і смуга дій чернетки. ОГЛЯД -- те,
// чим панель була досі: фракції з пулами, нарахування, завершення вузла,
// скидання, перечитування конфігів. Чернетка семи файлів -- у OZL_EdDocs.
// Чіпляється вкладкою через modded class -- ядро про дослідження не знає й
// знати не мусить.
//
// Гарди: NO_GUI -- сервер компілює Mission без UI; AVPPAdminTools і
// OpenZone_VPP -- імена класів CfgMods (їх авто-дефайнить рушій).
//
// Розмітка -- з опису ui/OpenZone_Research_VPP/oz_research_vpp_pane.json
// (layout_build); тут лише імена віджетів. Незворотні дії -- у два
// натискання, як і всюди у вікні: модальні вікна у VPP -- пастка.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    private ref array<ref OZL_AdminOwner> m_ResOwners;
    private int  m_ResPicked    = -1;
    private bool m_ResResetArmed  = false;
    private bool m_ResReloadArmed = false;
    private string m_ResArmedOwner = "";
    // Перемальовування списку кличе SelectRow, рушій відповідає OnItemSelected
    // -- прапорець рве це коло (як у ядрі й у сусідніх панелях).
    private bool m_ResRepaint = false;

    // ------------------------------------------------- редактор
    private ref OZL_EdDocs m_Ed;

    // Відкрита підвкладка (ключ після "RzNav_") і чи поверх неї список
    // проблем.
    private string m_RzTab = "overview";
    private bool   m_RzProblems = false;

    // Сім cfg_get уже стоять у черзі ядра (раз на вікно; далі -- лише
    // перечитування застосованого).
    private bool m_RzAsked = false;

    // Скрипт пише поля форми сам: OnChange, що прилетить на це, -- не правка.
    private bool m_RzFill = false;

    private bool m_RzDiscardArmed = false;

    // Типи балів: вибраний рядок і курок видалення.
    private int  m_PtPicked = -1;
    private bool m_PtDelArmed = false;

    // Дерево: власник, гілка, вибраний вузол; курок видалення вузла.
    private string m_TrOwner  = "";
    private string m_TrBranch = "";
    private string m_TrSel    = "";
    private bool   m_TnDelArmed = false;

    // Id, на який зараз указують посилання, поки поле Id набирається:
    // посилання йдуть за вузлом лише на вільний Id (RenameTn).
    private string m_TnRefId = "";

    // Полотно: скін власника, план, вигляд гілки, комірки, мітки "АБО".
    private ref OZL_TreeSkin   m_TrSkin;
    private string             m_TrSkinId = "";
    private ref OZL_TreePlan   m_TrPlan;
    private ref OZL_BranchView m_TrView;
    private ref array<Widget>  m_TrCells;
    private ref array<ref OZL_TreeOrMark> m_TrOrs;
    private ref array<Widget>  m_TrOrLabels;

    // Контейнери фішок ціни, що чекають розкладки: тексти мають ширину лише
    // кадром пізніше (OnUpdate -> RunTrFlows).
    private ref array<Widget>  m_TrFlows;
    private int                m_TrFlowTries = 0;

    // Режим зв'язку: увімкнений і від якого вузла (порожньо -- батька ще не
    // вибрано).
    private bool   m_TrLink     = false;
    private string m_TrLinkFrom = "";

    // Перегляд гравця: демо-стан фракції (OZL_EdTree.DemoState).
    private int    m_TrDemo = 0;

    // Гілка: курок видалення.
    private bool   m_BrDelArmed = false;

    // Вузол, який тягнуть уздовж осі (тір), і полотно, яке тягнуть (прокрутка).
    // Миша опитується з OnUpdate, як у вікні гравця (OZL_TreeMenu.Drag): так
    // клік і перетягування не залежать від прапорця DRAGGABLE.
    private string m_TnDragId    = "";
    private bool   m_TnDragMoved = false;
    private int    m_TnDragX     = 0;
    private int    m_TnDragY     = 0;
    private float  m_TnCellX     = 0;
    private float  m_TnCellY     = 0;
    // Клік, що приходить разом із відпусканням після перетягування, -- не
    // вибір: кілька кадрів він ігнорується.
    private int    m_TnSkipClick = 0;
    private bool   m_TrPanDown   = false;
    private bool   m_TrPanMoved  = false;
    private int    m_TrPanX      = 0;
    private int    m_TrPanY      = 0;
    private float  m_TrPanH      = 0;
    private float  m_TrPanV      = 0;

    override void OnCreate(Widget RootW)
    {
        super.OnCreate(RootW);
        if (!M_SUB_WIDGET)
            return;

        m_ResOwners = new array<ref OZL_AdminOwner>();
        m_Ed        = new OZL_EdDocs();
        m_TrCells   = new array<Widget>();
        m_TrOrs     = new array<ref OZL_TreeOrMark>();
        m_TrOrLabels = new array<Widget>();
        m_TrFlows   = new array<Widget>();

        Widget pane = GetGame().GetWorkspace().CreateWidgets("OpenZone_Research_VPP/gui/layouts/oz_research_vpp_pane.layout", M_SUB_WIDGET);
        if (!pane)
        {
            OZL_Log.Error("research vpp pane: layout failed to load");
            return;
        }

        RegisterPane("research", "RESEARCH", pane, "ResHint");

        // Власний слухач відповідей: список і операції -- наші, ядро про них
        // не знає; а ще він бачить відповіді cfg_set на наші файли.
        OZ_ClientState.AdminWatch().Insert(this.OnResearchResponse);

        ShowRzTab("overview");
    }

    void ~OZ_VppAdminMenu()
    {
        OZ_ClientState.AdminWatch().Remove(this.OnResearchResponse);
    }

    override void OnPaneShown(string id)
    {
        super.OnPaneShown(id);
        if (id != "research")
            return;

        AskResearchList();

        // Сім файлів -- у чергу ядра, раз на вікно: AskCfg шле по одному.
        if (!m_RzAsked && m_Ed)
        {
            m_RzAsked = true;
            array<string> tags = m_Ed.Tags();
            for (int i = 0; i < tags.Count(); i++)
                AskCfg(tags[i]);
        }
        RepaintRz();
    }

    protected void AskResearchList()
    {
        Ask(OZL_Const.SECTION, "list", "{}");
    }

    // Рядок зі stringtable мода, перекладений мовою клієнта.
    protected string Tr(string key)
    {
        return Widget.TranslateString(key);
    }

    void OnResearchResponse(string section, string op, bool ok, string json, string error)
    {
        // Відповідь на ЗАСТОСУВАТИ: ядро вже сказало своє «applied» у рядок
        // підказки, а нам треба знати, ЯКИЙ файл, і слати наступний.
        if (section == OZ_AdminSect.CONFIG && op.IndexOf("cfg_set:") == 0)
        {
            string tag = op.Substring(8, op.Length() - 8);
            if (m_Ed && m_Ed.Owns(tag) && m_Ed.InFlight() == tag)
                OnRzApplied(tag, ok, error);
            return;
        }

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

        // Після «перечитати конфіги» файли на сервері, можливо, інші: чернетка
        // без правок бере їх, з правками -- рахує зміни від нових.
        if (op == "reload" && m_Ed)
        {
            array<string> tags = m_Ed.Tags();
            for (int t = 0; t < tags.Count(); t++)
                AskCfg(tags[t]);
        }

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

    protected void PaintPicked()
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("ResPicked"));
        if (!t)
            return;
        string owner = PickedOwner();
        if (owner == "")
            t.SetText("#STR_OZL_ED_OV_PICK");
        else
            t.SetText("faction: " + owner);
    }

    protected string PickedOwner()
    {
        if (m_ResPicked < 0 || m_ResPicked >= m_ResOwners.Count())
            return "";
        return m_ResOwners[m_ResPicked].Id;
    }

    // ================================================= редактор: оболонка

    // Підвкладка: своя сторінка, а для ще не написаних -- спільна «згодом».
    protected void ShowRzTab(string key)
    {
        m_RzTab = key;
        m_RzProblems = false;
        m_RzDiscardArmed = false;
        m_PtDelArmed = false;
        m_TnDelArmed = false;
        m_BrDelArmed = false;
        m_TrLink = false;
        m_TrLinkFrom = "";
        if (m_Ed)
            m_Ed.EndGesture();
        RepaintRz();
    }

    // Сторінка, яку показує відкрита підвкладка.
    protected string RzPageOf(string key)
    {
        if (key == "overview" || key == "points" || key == "tree")
            return key;
        return "soon";
    }

    protected void ShowRzPage(string page)
    {
        array<string> pages = {"overview", "points", "tree", "soon", "problems"};
        for (int i = 0; i < pages.Count(); i++)
        {
            Widget p = M_SUB_WIDGET.FindAnyWidget("RzPage_" + pages[i]);
            if (p)
                p.Show(pages[i] == page);
        }

        array<string> tabs = {"overview", "tree", "chains", "points", "owners", "modules", "statics", "settings"};
        for (int t = 0; t < tabs.Count(); t++)
        {
            TextWidget tx = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzNav_" + tabs[t] + "Text"));
            if (!tx)
                continue;
            if (tabs[t] == m_RzTab)
                tx.SetColor(OZ_Palette.ACCENT);
            else
                tx.SetColor(OZ_Palette.MUTED);
        }
    }

    // Усе, що залежить від чернетки: сторінка, смуга дій, підсумок.
    protected void RepaintRz()
    {
        if (!M_SUB_WIDGET || !m_Ed)
            return;

        if (m_RzProblems)
        {
            ShowRzPage("problems");
            RepaintProblems();
        }
        else
        {
            ShowRzPage(RzPageOf(m_RzTab));
            if (m_RzTab == "points")
                RepaintPoints(true);
            else if (m_RzTab == "tree")
                RepaintTree(true);
        }
        PaintRzBar();
        PaintSummary();
    }

    protected void SetBtnText(string btn, string text, int color)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(btn + "Text"));
        if (!t)
            return;
        t.SetText(text);
        t.SetColor(color);
    }

    protected void PaintRzBar()
    {
        TextWidget st = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzStatus"));
        int changed = m_Ed.Changed();
        if (st)
        {
            if (!m_Ed.AllLoaded())
                st.SetText(Tr("#STR_OZL_ED_STATUS_LOADING") + m_Ed.LoadedCount().ToString() + "/" + m_Ed.Tags().Count().ToString());
            else if (changed > 0)
                st.SetText(Tr("#STR_OZL_ED_STATUS_CHANGED") + changed.ToString());
            else
                st.SetText(Tr("#STR_OZL_ED_STATUS_CLEAN"));
        }

        int errs = m_Ed.Errors();
        int warns = m_Ed.Warnings();
        if (errs > 0)
        {
            string pe = Tr("#STR_OZL_ED_PROB_ERRORS") + errs.ToString();
            if (warns > 0)
                pe += " +" + warns.ToString();
            SetBtnText("BtnRzProblems", pe, OZ_Palette.BAD);
        }
        else if (warns > 0)
        {
            SetBtnText("BtnRzProblems", Tr("#STR_OZL_ED_PROB_WARNINGS") + warns.ToString(), OZ_Palette.ALERT);
        }
        else
        {
            SetBtnText("BtnRzProblems", Tr("#STR_OZL_ED_PROB_NONE"), OZ_Palette.OK);
        }

        int undoColor = OZ_Palette.FAINT;
        if (m_Ed.CanUndo())
            undoColor = OZ_Palette.TEXT;
        SetBtnText("BtnRzUndo", Tr("#STR_OZL_ED_BTN_UNDO"), undoColor);

        int redoColor = OZ_Palette.FAINT;
        if (m_Ed.CanRedo())
            redoColor = OZ_Palette.TEXT;
        SetBtnText("BtnRzRedo", Tr("#STR_OZL_ED_BTN_REDO"), redoColor);

        int discardColor = OZ_Palette.FAINT;
        if (changed > 0)
            discardColor = OZ_Palette.BAD;
        SetBtnText("BtnRzDiscard", Tr("#STR_OZL_ED_BTN_DISCARD"), discardColor);

        string apply = Tr("#STR_OZL_ED_BTN_APPLY");
        int applyColor = OZ_Palette.FAINT;
        if (changed > 0)
        {
            apply += " - " + changed.ToString();
            if (errs == 0)
                applyColor = OZ_Palette.OK;
            else
                applyColor = OZ_Palette.BAD;
        }
        SetBtnText("BtnRzApply", apply, applyColor);
    }

    // Підсумок для ОГЛЯДУ: скільки файлів приїхало й що в них.
    protected void PaintSummary()
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzSummary"));
        if (!t)
            return;
        if (!m_Ed.AllLoaded())
        {
            t.SetText(Tr("#STR_OZL_ED_STATUS_LOADING") + m_Ed.LoadedCount().ToString() + "/" + m_Ed.Tags().Count().ToString());
            return;
        }

        OZL_PointTypes pt = OZL_PointTypes.Cast(m_Ed.Doc(OZL_Config.TAG_POINT_TYPES).Obj);
        OZL_Owners     ow = OZL_Owners.Cast(m_Ed.Doc(OZL_Config.TAG_OWNERS).Obj);
        OZL_Rules      ru = OZL_Rules.Cast(m_Ed.Doc(OZL_Config.TAG_RULES).Obj);
        OZL_TreeConfig tr = OZL_TreeConfig.Cast(m_Ed.Doc(OZL_Config.TAG_TREE).Obj);
        OZL_Modules    mo = OZL_Modules.Cast(m_Ed.Doc(OZL_Config.TAG_MODULES).Obj);
        OZL_StaticsConfig sc = OZL_StaticsConfig.Cast(m_Ed.Doc(OZL_Config.TAG_STATICS).Obj);

        string s = "point types " + pt.PointTypes.Count().ToString();
        s += " | owners " + ow.Owners.Count().ToString();
        s += " | rules " + ru.Count().ToString();
        s += " | nodes " + tr.NodeCount().ToString();
        s += " | modules " + mo.Modules.Count().ToString();
        s += " | statics " + sc.Entries.Count().ToString();
        t.SetText(s);
    }

    protected void RepaintProblems()
    {
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzProbList"));
        if (!lb)
            return;
        lb.ClearItems();

        array<string> probs = m_Ed.Problems();
        if (probs.Count() == 0)
        {
            lb.AddItem(Tr("#STR_OZL_ED_PROB_CLEAN"), NULL, 0);
            return;
        }

        // Помилки -- вгорі: їх треба виправити, щоб застосувати.
        string markE = Tr("#STR_OZL_ED_PROB_MARK_ERROR");
        string markW = Tr("#STR_OZL_ED_PROB_MARK_WARN");
        int i;
        for (i = 0; i < probs.Count(); i++)
        {
            if (OZL_EdCodec.IsError(probs[i]))
                lb.AddItem(markE + probs[i], NULL, 0);
        }
        for (i = 0; i < probs.Count(); i++)
        {
            if (!OZL_EdCodec.IsError(probs[i]))
                lb.AddItem(markW + probs[i], NULL, 0);
        }
    }

    // Файл чернетки приїхав із сервера (cfg_get ядра).
    override void OnCfgText(string name, string body)
    {
        super.OnCfgText(name, body);
        if (!m_Ed || !m_Ed.Owns(name))
            return;

        string err;
        if (!m_Ed.OnFetched(name, body, err))
            Hint(Tr("#STR_OZL_ED_HINT_BAD_FILE") + name + " (" + err + ")");
        RepaintRz();
    }

    // ------------------------------------------------- дії чернетки

    protected void RzUndo(bool redo)
    {
        string tag;
        bool done;
        if (redo)
            done = m_Ed.Redo(tag);
        else
            done = m_Ed.Undo(tag);

        if (!done)
        {
            if (redo)
                Hint(Tr("#STR_OZL_ED_HINT_REDO_EMPTY"));
            else
                Hint(Tr("#STR_OZL_ED_HINT_UNDO_EMPTY"));
            return;
        }

        m_PtDelArmed = false;
        m_RzDiscardArmed = false;
        ClampPicked();
        RepaintRz();
        if (redo)
            Hint(Tr("#STR_OZL_ED_HINT_REDONE") + tag);
        else
            Hint(Tr("#STR_OZL_ED_HINT_UNDONE") + tag);
    }

    protected void RzDiscard()
    {
        if (m_Ed.Changed() == 0)
        {
            Hint(Tr("#STR_OZL_ED_HINT_NOTHING"));
            return;
        }
        if (!m_RzDiscardArmed)
        {
            m_RzDiscardArmed = true;
            Hint(Tr("#STR_OZL_ED_HINT_DISCARD_ARMED"));
            return;
        }
        m_RzDiscardArmed = false;
        m_Ed.Discard();
        ClampPicked();
        RepaintRz();
        Hint(Tr("#STR_OZL_ED_HINT_DISCARDED"));
    }

    // ЗАСТОСУВАТИ: змінені файли по одному, у порядку OZL_EdDocs; помилки
    // чернетки не пускають -- сервер викинув би те, що на них стоїть.
    protected void RzApply()
    {
        m_RzDiscardArmed = false;
        if (!m_Ed.AllLoaded())
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }
        if (m_Ed.Applying())
        {
            Hint(Tr("#STR_OZL_ED_HINT_BUSY"));
            return;
        }
        if (m_Ed.Changed() == 0)
        {
            Hint(Tr("#STR_OZL_ED_HINT_NOTHING"));
            return;
        }
        if (m_Ed.Errors() > 0)
        {
            Hint(Tr("#STR_OZL_ED_HINT_FIX_FIRST"));
            return;
        }

        m_Ed.EndGesture();
        m_Ed.ApplyStart();
        SendNextRz();
    }

    protected void SendNextRz()
    {
        string tag = m_Ed.ApplyNext();
        if (tag == "")
            return;
        SendCfg(tag, m_Ed.Doc(tag).Cur);
        Hint(Tr("#STR_OZL_ED_HINT_APPLYING") + tag);
    }

    protected void OnRzApplied(string tag, bool ok, string error)
    {
        m_Ed.ApplyDone(tag, ok);
        if (!ok)
        {
            Hint(tag + Tr("#STR_OZL_ED_HINT_REFUSED") + " (" + Words(error) + ")");
            RepaintRz();
            return;
        }

        SendNextRz();
        if (m_Ed.Applying())
        {
            RepaintRz();
            return;
        }

        // Усе пройшло. Сервер переписав файли з розібраного (Validate, бекап),
        // тож показуємо вже його текст: перечитуємо застосоване.
        array<string> done = m_Ed.Applied();
        Hint(Tr("#STR_OZL_ED_HINT_APPLIED") + done.Count().ToString());
        m_Ed.ClearHistory();
        for (int i = 0; i < done.Count(); i++)
            AskCfg(done[i]);
        RepaintRz();
    }

    // ================================================= типи балів

    protected OZL_PointTypes DraftPointTypes()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_POINT_TYPES);
        if (!d || !d.Loaded)
            return null;
        return OZL_PointTypes.Cast(d.Obj);
    }

    protected void ClampPicked()
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts || m_PtPicked >= pts.PointTypes.Count())
            m_PtPicked = -1;
    }

    // Список і, коли fillForm, поля вибраного. Під час набору поле не
    // переписується -- інакше курсор стрибав би в кінець на кожну літеру.
    protected void RepaintPoints(bool fillForm)
    {
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzPtList"));
        if (!lb)
            return;

        OZL_PointTypes pts = DraftPointTypes();
        m_ResRepaint = true;
        lb.ClearItems();
        if (pts)
        {
            // Маркер "> " -- вибраний рядок: список у стилі NoScrollBar
            // підсвічування рядка не малює (зміряно 2026-11-09), а червона смуга
            // прокрутки стилю за замовчуванням була гірша за маркер.
            for (int i = 0; i < pts.PointTypes.Count(); i++)
            {
                OZL_PointType p = pts.PointTypes[i];
                string line = "";
                if (i == m_PtPicked)
                    line = "> ";
                line += p.Id + "  -  " + p.Name + "  -  " + p.BasePurity.ToString();
                lb.AddItem(line, NULL, 0);
            }
            if (m_PtPicked >= 0 && m_PtPicked < pts.PointTypes.Count())
                lb.SelectRow(m_PtPicked);
        }
        m_ResRepaint = false;

        if (fillForm)
            FillPtForm();
    }

    protected void FillPtForm()
    {
        OZL_PointTypes pts = DraftPointTypes();
        OZL_PointType p = null;
        if (pts && m_PtPicked >= 0 && m_PtPicked < pts.PointTypes.Count())
            p = pts.PointTypes[m_PtPicked];

        TextWidget head = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzPtPicked"));
        if (head)
        {
            if (p)
                head.SetText(p.Id);
            else
                head.SetText("#STR_OZL_ED_PT_PICK");
        }

        m_RzFill = true;
        if (p)
        {
            SetEdit("RzPtId", p.Id);
            SetEdit("RzPtName", p.Name);
            SetEdit("RzPtColor", ColorShown(p.Color));
            SetEdit("RzPtSort", p.SortOrder.ToString());
            SetEdit("RzPtPurity", p.BasePurity.ToString());
            SetEdit("RzPtIcon", p.Icon);
        }
        else
        {
            SetEdit("RzPtId", "");
            SetEdit("RzPtName", "");
            SetEdit("RzPtColor", "");
            SetEdit("RzPtSort", "");
            SetEdit("RzPtPurity", "");
            SetEdit("RzPtIcon", "");
        }
        m_RzFill = false;
    }

    // КОЛІР БЕЗ "#" У ПОЛІ. Текст на "#" рушій читає як ключ stringtable:
    // SetText("#7CB342") показав "7CB342" (зміряно 2026-11-09), і поле, яке
    // потім правили, повертало колір без решітки. Тож поле показує шість
    // цифр, а у файл іде "#RRGGBB" -- як писав колір пакет і як читає
    // OZL_PointTypes.ColorArgb.
    protected string ColorShown(string stored)
    {
        string c = stored.Trim();
        if (c.IndexOf("#") == 0)
            c = c.Substring(1, c.Length() - 1);
        return c;
    }

    protected string ColorStored(string typed)
    {
        string c = typed.Trim();
        if (c == "" || c.IndexOf("#") == 0)
            return c;
        return "#" + c;
    }

    // Поле форми змінилось: правка вибраного типу, один знімок на поле.
    protected void OnPtField(string field)
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts || m_PtPicked < 0 || m_PtPicked >= pts.PointTypes.Count())
            return;

        string tag = OZL_Config.TAG_POINT_TYPES;
        m_Ed.BeginOnce(tag, "pt:" + m_PtPicked.ToString() + ":" + field);

        OZL_PointType p = pts.PointTypes[m_PtPicked];
        string v = GetEdit(field);
        if (field == "RzPtId")
            p.Id = v.Trim();
        else if (field == "RzPtName")
            p.Name = v;
        else if (field == "RzPtColor")
            p.Color = ColorStored(v);
        else if (field == "RzPtSort")
            p.SortOrder = v.ToInt();
        else if (field == "RzPtPurity")
            p.BasePurity = v.ToFloat();
        else if (field == "RzPtIcon")
            p.Icon = v.Trim();

        m_PtDelArmed = false;
        m_RzDiscardArmed = false;
        m_Ed.Commit(tag);
        RepaintPoints(false);
        PaintRzBar();
        PaintSummary();
    }

    protected void PtAdd()
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts)
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }

        string tag = OZL_Config.TAG_POINT_TYPES;
        m_Ed.BeginOnce(tag, "");

        // Нова лінія з вільним Id і порядком у кінці: адмін перейменує.
        int order = 0;
        int i;
        for (i = 0; i < pts.PointTypes.Count(); i++)
        {
            if (pts.PointTypes[i].SortOrder > order)
                order = pts.PointTypes[i].SortOrder;
        }
        string id = "new_line";
        int n = 1;
        while (pts.Find(id))
        {
            n++;
            id = "new_line_" + n.ToString();
        }

        OZL_PointType p = new OZL_PointType();
        p.Id = id;
        p.Name = id;
        p.Color = "#FFFFFF";
        p.SortOrder = order + 1;
        p.BasePurity = OZL_Const.DEFAULT_PURITY;
        pts.PointTypes.Insert(p);

        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        m_PtPicked = pts.PointTypes.Count() - 1;
        m_PtDelArmed = false;
        RepaintPoints(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_PT_ADDED") + id);
    }

    protected void PtDelete()
    {
        OZL_PointTypes pts = DraftPointTypes();
        if (!pts || m_PtPicked < 0 || m_PtPicked >= pts.PointTypes.Count())
        {
            Hint(Tr("#STR_OZL_ED_PT_PICK"));
            return;
        }

        string id = pts.PointTypes[m_PtPicked].Id;
        if (!m_PtDelArmed)
        {
            m_PtDelArmed = true;
            Hint(Tr("#STR_OZL_ED_PT_DEL_ARMED") + id);
            return;
        }

        m_PtDelArmed = false;
        string tag = OZL_Config.TAG_POINT_TYPES;
        m_Ed.BeginOnce(tag, "");
        pts.PointTypes.RemoveOrdered(m_PtPicked);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        if (m_PtPicked >= pts.PointTypes.Count())
            m_PtPicked = pts.PointTypes.Count() - 1;
        RepaintPoints(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_PT_DELETED") + id);
    }

    // ================================================= дерево

    protected OZL_TreeConfig DraftTree()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_TREE);
        if (!d || !d.Loaded)
            return null;
        return OZL_TreeConfig.Cast(d.Obj);
    }

    protected OZL_Owners DraftOwners()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_OWNERS);
        if (!d || !d.Loaded)
            return null;
        return OZL_Owners.Cast(d.Obj);
    }

    // Одиниця розмітки в пікселях: висота екрана на 1080 (SetPos і SetSize
    // беруть пікселі, dayz-modding gui-layouts §24).
    protected float Px()
    {
        int sw, sh;
        GetScreenSize(sw, sh);
        return sh / 1080.0;
    }

    protected OZL_TreeBranch TrBranch(OZL_TreeConfig tree)
    {
        if (!tree)
            return null;
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            if (tree.Branches[b] && tree.Branches[b].Id == m_TrBranch)
                return tree.Branches[b];
        }
        return null;
    }

    protected OZL_TreeNode TrNode(OZL_TreeConfig tree)
    {
        if (!tree || m_TrSel == "")
            return null;
        return tree.FindNode(m_TrSel);
    }

    // Гілки власника в порядку файла -- рядки списку гілок. Вибрана гілка,
    // якої власник уже не має (у полі власників набирають інший список),
    // лишається в кінці: інакше вибір стрибав би на іншу гілку посеред
    // набору.
    protected void TrBranchIds(OZL_TreeConfig tree, array<string> into)
    {
        into.Clear();
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            if (br && br.BelongsTo(m_TrOwner))
                into.Insert(br.Id);
        }
        if (m_TrBranch != "" && into.Find(m_TrBranch) < 0 && OZL_EdTree.FindBranch(tree, m_TrBranch))
            into.Insert(m_TrBranch);
    }

    // Списки ліворуч; вибір за замовчуванням -- перший власник і його перша
    // гілка.
    protected void RepaintTrLists(OZL_TreeConfig tree, OZL_Owners owners)
    {
        TextListboxWidget lo = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrOwners"));
        TextListboxWidget lb = TextListboxWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrBranches"));
        if (!lo || !lb)
            return;

        int i;
        bool ownerKnown = false;
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            if (owners.Owners[i] && owners.Owners[i].Id == m_TrOwner)
                ownerKnown = true;
        }
        if (!ownerKnown && owners.Owners.Count() > 0)
            m_TrOwner = owners.Owners[0].Id;

        array<string> ids = new array<string>();
        TrBranchIds(tree, ids);
        if (ids.Find(m_TrBranch) < 0)
        {
            m_TrBranch = "";
            if (ids.Count() > 0)
                m_TrBranch = ids[0];
            m_TrSel = "";
        }

        m_ResRepaint = true;
        lo.ClearItems();
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            OZL_OwnerDef o = owners.Owners[i];
            if (!o)
                continue;
            string ol = "";
            if (o.Id == m_TrOwner)
                ol = "> ";
            ol += o.Id + "  -  " + owners.SkinOf(o.Id);
            lo.AddItem(ol, NULL, 0);
        }

        lb.ClearItems();
        for (i = 0; i < ids.Count(); i++)
        {
            OZL_TreeBranch br = null;
            for (int b = 0; b < tree.Branches.Count(); b++)
            {
                if (tree.Branches[b] && tree.Branches[b].Id == ids[i])
                    br = tree.Branches[b];
            }
            if (!br)
                continue;
            string bl = "";
            if (br.Id == m_TrBranch)
                bl = "> ";
            string bn = br.Name;
            if (bn == "")
                bn = br.Id;
            bl += bn + "  (" + br.Nodes.Count().ToString() + ")";
            if (!br.BelongsTo(m_TrOwner))
                bl += Tr("#STR_OZL_ED_BR_OTHER");
            lb.AddItem(bl, NULL, 0);
        }
        m_ResRepaint = false;
    }

    protected void ClearTrCells()
    {
        for (int i = 0; i < m_TrCells.Count(); i++)
        {
            if (m_TrCells[i])
                m_TrCells[i].Unlink();
        }
        m_TrCells.Clear();
        m_TrFlows.Clear();
        ClearTrOrs();
    }

    protected void ClearTrOrs()
    {
        for (int i = 0; i < m_TrOrLabels.Count(); i++)
        {
            if (m_TrOrLabels[i])
                m_TrOrLabels[i].Unlink();
        }
        m_TrOrLabels.Clear();
    }

    // Мітки "АБО" на місцях, які OZL_TreeLines.Draw поклав у m_TrOrs: рядок
    // скіна or_label, текст і колір -- як у вікні гравця (DrawLines).
    protected void PaintTrOrs(float k)
    {
        ClearTrOrs();
        Widget nodes = M_SUB_WIDGET.FindAnyWidget("RzTrNodes");
        if (!nodes || !m_TrSkin)
            return;
        string path = m_TrSkin.RowLayout("or_label");
        for (int i = 0; i < m_TrOrs.Count(); i++)
        {
            Widget lab = GetGame().GetWorkspace().CreateWidgets(path, nodes);
            if (!lab)
                return;
            OZL_TreeMenu.IgnorePointer(lab, null);
            lab.ClearFlags(WidgetFlags.CLIPCHILDREN);
            TextWidget t = TextWidget.Cast(lab.FindAnyWidget("OrText"));
            if (t)
            {
                t.SetText(OZL_Text.Words("STR_OZL_TREE_OR"));
                t.SetColor(m_TrOrs[i].Color);
            }
            lab.SetPos(m_TrOrs[i].X * k, m_TrOrs[i].Y * k);
            m_TrOrLabels.Insert(lab);
        }
    }

    // Рядок під полотном: що зараз зробить клік чи перетягування.
    protected void PaintTrInfo()
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrInfo"));
        if (!t)
            return;
        if (m_TrLink && m_TrLinkFrom == "")
            t.SetText(Tr("#STR_OZL_ED_TR_LINK_FROM"));
        else if (m_TrLink)
            t.SetText(Tr("#STR_OZL_ED_TR_LINK_TO") + m_TrLinkFrom);
        else
            t.SetText(Tr("#STR_OZL_ED_TR_INFO"));
        if (m_TrLink)
            t.SetColor(OZ_Palette.ACCENT);
        else
            t.SetColor(OZ_Palette.MUTED);
    }

    protected void TrInfoText(string text)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrInfo"));
        if (!t)
            return;
        t.SetText(text);
        t.SetColor(OZ_Palette.ACCENT);
    }

    // Рамка ріже дітей по своєму краю (gui-layouts §31): комірка й
    // контейнери NodeHit пускають мітки й написи за край -- як
    // OZL_TreeMenu.Unclip.
    protected void UnclipCell(Widget cell, Widget hit)
    {
        cell.ClearFlags(WidgetFlags.CLIPCHILDREN);
        if (!hit)
            return;
        Widget p = hit.GetParent();
        while (p && p != cell)
        {
            p.ClearFlags(WidgetFlags.CLIPCHILDREN);
            p = p.GetParent();
        }
    }

    // Полотно. full -- заново план і комірки (структура змінилась: власник,
    // гілка, Id, тір, батьки, умова, новий чи прибраний вузол, скасування);
    // інакше -- лише фарба комірок і лінії (вибір, назва, ціна, іконка).
    // fillForm -- переписати поля інспектора; під час набору -- ні, бо
    // курсор у полі стрибав би в кінець.
    protected void RepaintTree(bool full, bool fillForm = true)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_Owners owners = DraftOwners();
        TextWidget skinLbl = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrSkin"));
        CanvasWidget lines = CanvasWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrLines"));
        PaintTrButtons();
        PaintTrInfo();
        if (!tree || !owners)
        {
            ClearTrCells();
            if (lines)
                lines.Clear();
            return;
        }

        RepaintTrLists(tree, owners);
        if (m_TrSel != "" && !tree.FindNode(m_TrSel))
            m_TrSel = "";
        if (m_TrLinkFrom != "" && !tree.FindNode(m_TrLinkFrom))
            m_TrLinkFrom = "";

        OZL_TreeBranch br = TrBranch(tree);
        if (!br)
        {
            ClearTrCells();
            m_TrPlan = null;
            if (lines)
                lines.Clear();
            if (skinLbl)
                skinLbl.SetText(Tr("#STR_OZL_ED_TR_NO_BRANCH"));
            if (fillForm)
                FillTnForm(null);
            return;
        }

        string skinId = owners.SkinOf(m_TrOwner);
        if (!m_TrSkin || skinId != m_TrSkinId)
        {
            m_TrSkin = OZL_TreeSkins.Make(skinId);
            m_TrSkinId = skinId;
            full = true;
        }
        float k = Px();
        m_TrSkin.PxPerUnit = k;

        m_TrView = OZL_EdTree.View(tree, br, m_TrOwner);
        if (full || !m_TrPlan || m_TrCells.Count() != m_TrView.Nodes.Count())
            BuildTrCells(k);

        PaintTrCells(tree);
        if (lines)
        {
            string focus = m_TrSel;
            if (m_TrLink && m_TrLinkFrom != "")
                focus = m_TrLinkFrom;
            OZL_TreeLines.Draw(lines, m_TrSkin, m_TrPlan, m_TrView, focus, m_TrOrs);
            PaintTrOrs(k);
        }

        if (skinLbl)
        {
            string dir = Tr("#STR_OZL_ED_TR_DIR_DOWN");
            if (m_TrSkin.Dir == "up")
                dir = Tr("#STR_OZL_ED_TR_DIR_UP");
            else if (m_TrSkin.Dir == "right")
                dir = Tr("#STR_OZL_ED_TR_DIR_RIGHT");
            skinLbl.SetText(skinId + " - " + dir);
        }

        if (fillForm)
            FillTnForm(TrNode(tree));
    }

    // План гілки під розмір вікна скіна і комірки на його місцях.
    protected void BuildTrCells(float k)
    {
        m_TrPlan = new OZL_TreePlan();
        float vw, vh;
        OZL_EdTree.ViewSize(m_TrSkinId, vw, vh);
        m_TrPlan.Build(m_TrSkin, m_TrView, vw, vh);

        Widget content = M_SUB_WIDGET.FindAnyWidget("RzTrContent");
        if (content)
            content.SetSize(m_TrPlan.W * k, m_TrPlan.H * k);
        ScrollWidget scroll = ScrollWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrScroll"));
        if (scroll)
            scroll.Update();

        ClearTrCells();
        Widget nodes = M_SUB_WIDGET.FindAnyWidget("RzTrNodes");
        if (!nodes)
            return;

        for (int i = 0; i < m_TrView.Nodes.Count(); i++)
        {
            OZL_NodeView nv = m_TrView.Nodes[i];
            int at = m_TrPlan.IndexOf(nv.Id);
            if (at < 0)
                continue;
            Widget cell = GetGame().GetWorkspace().CreateWidgets(m_TrSkin.NodeLayout, nodes);
            if (!cell)
                continue;
            cell.SetPos((m_TrPlan.X[at] - m_TrSkin.AnchorX) * k, (m_TrPlan.Y[at] - m_TrSkin.AnchorY) * k);
            OZL_EdTree.LoadSlots(m_TrSkin, cell);
            Widget hit = cell.FindAnyWidget("NodeHit");
            if (hit)
                hit.SetName("rznode:" + nv.Id);
            cell.SetName("rzcell:" + nv.Id);
            OZL_TreeMenu.IgnorePointer(cell, hit);
            UnclipCell(cell, hit);
            m_TrCells.Insert(cell);
        }
    }

    // Фарба комірок: стан "available" для всіх (редактор стану не має),
    // вибраний (і джерело зв'язку) -- виділений; ціна -- фішками з вузла
    // чернетки, як у вікні гравця, або рядком, якщо скін фішок не має.
    protected void PaintTrCells(OZL_TreeConfig tree)
    {
        OZL_PointTypes pts = DraftPointTypes();
        m_TrFlows.Clear();
        m_TrFlowTries = 0;
        for (int c = 0; c < m_TrCells.Count(); c++)
        {
            Widget cell = m_TrCells[c];
            if (!cell)
                continue;
            string nm = cell.GetName();
            string id = nm.Substring(7, nm.Length() - 7);
            for (int i = 0; i < m_TrView.Nodes.Count(); i++)
            {
                OZL_NodeView nv = m_TrView.Nodes[i];
                if (nv.Id != id)
                    continue;
                string price = "";
                OZL_TreeNode tn = tree.FindNode(id);
                Widget chips = null;
                if (tn)
                    chips = OZL_EdTree.PaintChips(m_TrSkin, cell, tn, pts, "available");
                if (tn && !chips)
                    price = OZL_EdTree.PriceText(tn, pts);
                bool picked = (id == m_TrSel);
                if (m_TrLink && m_TrLinkFrom != "")
                    picked = (id == m_TrLinkFrom);
                OZL_EdTree.Paint(m_TrSkin, cell, nv, "available", picked, nv.Index + 1, price);
                if (chips)
                    m_TrFlows.Insert(chips);
                break;
            }
        }
    }

    // Фішки, що чекають ширини тексту; після дванадцяти кадрів -- як є.
    protected void RunTrFlows()
    {
        if (m_TrFlows.Count() == 0)
            return;
        float k = Px();
        m_TrFlowTries++;
        bool force = m_TrFlowTries > 12;
        for (int i = m_TrFlows.Count() - 1; i >= 0; i--)
        {
            Widget box = m_TrFlows[i];
            if (!box)
            {
                m_TrFlows.RemoveOrdered(i);
                continue;
            }
            if (OZL_EdTree.FlowChips(m_TrSkin, box, k, force))
                m_TrFlows.RemoveOrdered(i);
        }
        if (m_TrFlows.Count() == 0)
            m_TrFlowTries = 0;
    }

    // Кнопки рядка полотна: ЗВ'ЯЗОК світиться, поки режим увімкнено; кнопка
    // демо-стану називає стан, з яким відкриється перегляд.
    protected void PaintTrButtons()
    {
        if (m_TrLink)
            SetBtnText("BtnRzTrLink", Tr("#STR_OZL_ED_TR_LINK"), OZ_Palette.ACCENT);
        else
            SetBtnText("BtnRzTrLink", Tr("#STR_OZL_ED_TR_LINK"), OZ_Palette.TEXT);

        string demo = "#STR_OZL_ED_TR_DEMO_NEW";
        if (m_TrDemo == 1)
            demo = "#STR_OZL_ED_TR_DEMO_FUNDED";
        else if (m_TrDemo == 2)
            demo = "#STR_OZL_ED_TR_DEMO_PROGRESS";
        SetBtnText("BtnRzTrDemo", Tr(demo), OZ_Palette.TEXT);
    }

    // Інспектор: поля вибраного вузла, а без вибраного вузла -- поля гілки.
    protected void FillTnForm(OZL_TreeNode n)
    {
        Widget tnForm = M_SUB_WIDGET.FindAnyWidget("RzTnForm");
        Widget brForm = M_SUB_WIDGET.FindAnyWidget("RzBrForm");
        if (tnForm)
            tnForm.Show(n != null);
        if (brForm)
            brForm.Show(n == null);
        if (!n)
        {
            FillBrForm(TrBranch(DraftTree()));
            return;
        }

        TextWidget head = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTnHead"));
        if (head)
        {
            if (n)
                head.SetText(n.Id);
            else
                head.SetText("#STR_OZL_ED_TN_PICK");
        }

        m_RzFill = true;
        if (n)
        {
            SetEdit("RzTnId", n.Id);
            SetEdit("RzTnName", n.Name);
            SetEdit("RzTnTier", n.Tier.ToString());
            SetEdit("RzTnParents", OZL_EdTree.ParentsText(n));
            SetEdit("RzTnCost", OZL_EdTree.CostText(n));
            SetEdit("RzTnItems", OZL_EdTree.ItemsText(n));
            SetEdit("RzTnTime", n.ResearchTimeSec.ToString());
            SetEdit("RzTnIcon", n.Icon);
            m_TnRefId = n.Id;
        }
        else
        {
            SetEdit("RzTnId", "");
            SetEdit("RzTnName", "");
            SetEdit("RzTnTier", "");
            SetEdit("RzTnParents", "");
            SetEdit("RzTnCost", "");
            SetEdit("RzTnItems", "");
            SetEdit("RzTnTime", "");
            SetEdit("RzTnIcon", "");
            m_TnRefId = "";
        }
        m_RzFill = false;

        string mode = "all";
        if (n)
        {
            mode = n.ParentsMode;
            mode.ToLower();
        }
        if (mode == "any")
            SetBtnText("BtnRzTnMode", Tr("#STR_OZL_ED_TN_ANY"), OZ_Palette.ALERT);
        else
            SetBtnText("BtnRzTnMode", Tr("#STR_OZL_ED_TN_ALL"), OZ_Palette.TEXT);
    }

    protected void FillBrForm(OZL_TreeBranch br)
    {
        TextWidget head = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzBrHead"));
        if (head)
        {
            if (br)
                head.SetText(Tr("#STR_OZL_ED_BR_HEAD") + " " + br.Id);
            else
                head.SetText(Tr("#STR_OZL_ED_TR_NO_BRANCH"));
        }
        m_RzFill = true;
        if (br)
        {
            SetEdit("RzBrId", br.Id);
            SetEdit("RzBrName", br.Name);
            SetEdit("RzBrOwners", OZL_EdTree.ListText(br.Owners));
            SetEdit("RzBrSort", br.SortOrder.ToString());
            SetEdit("RzBrIcon", br.Icon);
        }
        else
        {
            SetEdit("RzBrId", "");
            SetEdit("RzBrName", "");
            SetEdit("RzBrOwners", "");
            SetEdit("RzBrSort", "");
            SetEdit("RzBrIcon", "");
        }
        m_RzFill = false;
    }

    // Поле гілки змінилось: один знімок на поле, як у вузла.
    protected void OnBrField(string field)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeBranch br = TrBranch(tree);
        if (!br)
            return;

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "br:" + field);
        string v = GetEdit(field);
        if (field == "RzBrId")
        {
            br.Id = v.Trim();
            m_TrBranch = br.Id;
        }
        else if (field == "RzBrName")
            br.Name = v;
        else if (field == "RzBrOwners")
            OZL_EdTree.ParseList(v, br.Owners);
        else if (field == "RzBrSort")
            br.SortOrder = v.ToInt();
        else if (field == "RzBrIcon")
            br.Icon = v.Trim();

        m_BrDelArmed = false;
        m_RzDiscardArmed = false;
        m_Ed.Commit(tag);
        RepaintTree(true, false);
        TextWidget head = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzBrHead"));
        if (head)
            head.SetText(Tr("#STR_OZL_ED_BR_HEAD") + " " + br.Id);
        PaintRzBar();
        PaintSummary();
    }

    protected void BrAdd()
    {
        OZL_TreeConfig tree = DraftTree();
        if (!tree)
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }
        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        OZL_TreeBranch br = new OZL_TreeBranch();
        string base = m_TrOwner + "_branch";
        if (m_TrOwner == "")
            base = "branch";
        br.Id = OZL_EdTree.FreeBranchId(tree, base);
        br.Name = br.Id;
        if (m_TrOwner != "")
            br.Owners.Insert(m_TrOwner);
        tree.Branches.Insert(br);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();

        m_TrBranch = br.Id;
        m_TrSel = "";
        m_BrDelArmed = false;
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_BR_ADDED") + br.Id);
    }

    // Гілка йде разом зі своїми вузлами й усіма посиланнями на них.
    protected void BrDelete()
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeBranch br = TrBranch(tree);
        if (!br)
        {
            Hint(Tr("#STR_OZL_ED_TR_PICK_BRANCH"));
            return;
        }
        if (!m_BrDelArmed)
        {
            m_BrDelArmed = true;
            Hint(Tr("#STR_OZL_ED_BR_DEL_ARMED") + br.Id + " (" + br.Nodes.Count().ToString() + ")");
            return;
        }
        m_BrDelArmed = false;

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        string id = br.Id;
        array<string> gone = new array<string>();
        int i;
        for (i = 0; i < br.Nodes.Count(); i++)
        {
            if (br.Nodes[i])
                gone.Insert(br.Nodes[i].Id);
        }
        for (i = tree.Branches.Count() - 1; i >= 0; i--)
        {
            if (tree.Branches[i] == br)
                tree.Branches.RemoveOrdered(i);
        }
        for (i = 0; i < gone.Count(); i++)
            OZL_EdTree.DropRefs(tree, gone[i]);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();

        m_TrBranch = "";
        m_TrSel = "";
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_BR_DELETED") + id);
    }

    // ------------------------------------------------- зв'язки, тір, перегляд

    protected void TrLinkToggle()
    {
        m_TrLink = !m_TrLink;
        m_TrLinkFrom = "";
        if (m_TrLink && m_TrSel != "")
            m_TrLinkFrom = m_TrSel;
        m_Ed.EndGesture();
        RepaintTree(false);
    }

    // Клік по вузлу в режимі зв'язку: перший -- батько, далі -- діти; клік
    // по дитині, що вже має цей зв'язок, його прибирає; клік по самому
    // батькові -- вибрати іншого.
    protected void TrLinkClick(string id)
    {
        if (m_TrLinkFrom == "" )
        {
            m_TrLinkFrom = id;
            m_TrSel = id;
            RepaintTree(false);
            return;
        }
        if (id == m_TrLinkFrom)
        {
            m_TrLinkFrom = "";
            RepaintTree(false);
            return;
        }

        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode parent = tree.FindNode(m_TrLinkFrom);
        OZL_TreeNode child = tree.FindNode(id);
        if (!parent || !child)
            return;

        string tag = OZL_Config.TAG_TREE;
        int at = child.Parents.Find(m_TrLinkFrom);
        if (at >= 0)
        {
            m_Ed.BeginOnce(tag, "");
            child.Parents.RemoveOrdered(at);
            m_Ed.Commit(tag);
            m_Ed.EndGesture();
            Hint(Tr("#STR_OZL_ED_TR_UNLINKED") + m_TrLinkFrom + " -> " + id);
        }
        else
        {
            if (OZL_EdTree.DependsOn(tree, parent, id, 0))
            {
                Hint(Tr("#STR_OZL_ED_TR_CYCLE") + m_TrLinkFrom + " -> " + id);
                return;
            }
            m_Ed.BeginOnce(tag, "");
            child.Parents.Insert(m_TrLinkFrom);
            string note = "";
            if (child.Tier <= parent.Tier)
            {
                child.Tier = parent.Tier + 1;
                note = Tr("#STR_OZL_ED_TR_BUMPED") + child.Tier.ToString();
            }
            m_Ed.Commit(tag);
            m_Ed.EndGesture();
            Hint(Tr("#STR_OZL_ED_TR_LINKED") + m_TrLinkFrom + " -> " + id + note);
        }
        m_TnDelArmed = false;
        m_RzDiscardArmed = false;
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
    }

    // Тір під вузлом, зсунутим уздовж осі на along пікселів: ряд плану, у
    // який потрапив центр вузла. За останнім рядом -- новий тір, перед
    // першим -- на один менший (не нижче 1).
    protected int TierAt(string id, float along)
    {
        if (!m_TrPlan || !m_TrSkin)
            return 1;
        int at = m_TrPlan.IndexOf(id);
        int n = m_TrPlan.Tiers.Count();
        if (at < 0 || n == 0)
            return 1;
        float u = m_TrPlan.U[at];
        if (m_TrSkin.Dir == "up")
            u -= along / Px();
        else
            u += along / Px();
        float row = Math.Floor((u - m_TrSkin.Top) / m_TrSkin.Row);
        int ti = row;
        if (ti >= n)
            return m_TrPlan.Tiers[n - 1] + 1;
        if (ti < 0)
        {
            int first = m_TrPlan.Tiers[0] - 1;
            if (first < 1)
                first = 1;
            return first;
        }
        return m_TrPlan.Tiers[ti];
    }

    // Натиснули на вузлі й тягнуть: комірка їде за мишею вздовж осі, рядок
    // під полотном називає тір; відпустили -- тір вузла, один знімок.
    protected void TrackTnDrag()
    {
        if (m_TnDragId == "")
            return;
        int mx;
        int my;
        GetMousePos(mx, my);
        float dx = mx - m_TnDragX;
        float dy = my - m_TnDragY;
        bool horiz = (m_TrSkin && m_TrSkin.Dir == "right");
        float along = dy;
        if (horiz)
            along = dx;

        if (!(GetMouseState(MouseState.LEFT) & 0x80000000))
        {
            string id = m_TnDragId;
            m_TnDragId = "";
            if (m_TnDragMoved)
            {
                m_TnSkipClick = 3;
                DropTier(id, along);
            }
            return;
        }

        if (!m_TnDragMoved && Math.AbsFloat(along) > 6 * Px())
            m_TnDragMoved = true;
        if (!m_TnDragMoved)
            return;
        Widget cell = M_SUB_WIDGET.FindAnyWidget("rzcell:" + m_TnDragId);
        if (cell)
        {
            if (horiz)
                cell.SetPos(m_TnCellX + dx, m_TnCellY);
            else
                cell.SetPos(m_TnCellX, m_TnCellY + dy);
        }
        TrInfoText(Tr("#STR_OZL_ED_TR_DRAG_TIER") + TierAt(m_TnDragId, along).ToString());
    }

    protected void DropTier(string id, float along)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = null;
        if (tree)
            n = tree.FindNode(id);
        int tier = TierAt(id, along);
        if (!n || tier == n.Tier)
        {
            RepaintTree(true, false);
            return;
        }
        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        int was = n.Tier;
        n.Tier = tier;
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        m_TrSel = id;
        m_TnDelArmed = false;
        m_RzDiscardArmed = false;
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_TR_TIER_SET") + id + ": " + was.ToString() + " -> " + tier.ToString());
    }

    // Натиснули на порожньому полотні: тягнення прокручує, клік без руху --
    // зняти вибір вузла (інспектор показує гілку).
    protected void TrackTrPan()
    {
        if (!m_TrPanDown)
            return;
        int mx;
        int my;
        GetMousePos(mx, my);
        float dx = mx - m_TrPanX;
        float dy = my - m_TrPanY;
        if (!(GetMouseState(MouseState.LEFT) & 0x80000000))
        {
            m_TrPanDown = false;
            if (!m_TrPanMoved && m_TrSel != "" && !m_TrLink)
            {
                m_TrSel = "";
                m_TnDelArmed = false;
                m_Ed.EndGesture();
                RepaintTree(false);
            }
            return;
        }
        if (Math.AbsFloat(dx) + Math.AbsFloat(dy) > 4 * Px())
            m_TrPanMoved = true;
        if (!m_TrPanMoved)
            return;
        ScrollWidget sw = ScrollWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrScroll"));
        if (!sw)
            return;
        sw.HScrollToPos(m_TrPanH - dx);
        sw.VScrollToPos(m_TrPanV - dy);
    }

    // Чи натиснуто на смугу прокрутки полотна (10 одиниць біля правого й
    // нижнього краю, як у вікні гравця).
    protected bool OnTrScrollbar(int x, int y)
    {
        Widget sw = M_SUB_WIDGET.FindAnyWidget("RzTrScroll");
        if (!sw)
            return false;
        float sx;
        float sy;
        float sww;
        float swh;
        sw.GetScreenPos(sx, sy);
        sw.GetScreenSize(sww, swh);
        float bar = 10 * Px();
        bool onBar = false;
        if (x > sx + sww - bar || y > sy + swh - bar)
            onBar = true;
        return onBar;
    }

    // ЯК У ГРАВЦЯ: вікно дерева гравця поверх адмінського, з виглядом із
    // чернетки й демо-стану. Меню VPP лишається батьком (як записка над
    // інвентарем у ванілі): ESC закриває дерево й повертає сюди.
    protected void TrPreview()
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_Owners owners = DraftOwners();
        OZL_PointTypes pts = DraftPointTypes();
        OZL_Settings se = null;
        OZL_EdDoc sd = m_Ed.Doc(OZL_Config.TAG_SETTINGS);
        if (sd && sd.Loaded)
            se = OZL_Settings.Cast(sd.Obj);
        if (!tree || !owners || !pts || !se || m_TrOwner == "")
        {
            Hint(Tr("#STR_OZL_ED_HINT_LOADING"));
            return;
        }

        OZL_TreeView v = OZL_EdTree.PlayerView(tree, owners, pts, se, m_TrOwner, m_TrDemo);
        string json = JsonFileLoader<OZL_TreeView>.JsonMakeData(v);
        OZL_TreeMenu.PreviewNext(json);
        UIManager ui = GetGame().GetUIManager();
        UIScriptedMenu menu = ui.EnterScriptedMenu(OZL_Const.MENU_TREE, ui.GetMenu());
        if (!menu)
        {
            OZL_TreeMenu.PreviewNext("");
            Hint(Tr("#STR_OZL_ED_TR_VIEW_FAIL"));
            return;
        }
        Hint(Tr("#STR_OZL_ED_TR_VIEW_OPEN") + m_TrOwner);
    }

    override void OnUpdate(float timeslice)
    {
        super.OnUpdate(timeslice);
        if (!M_SUB_WIDGET || !m_TrFlows)
            return;
        RunTrFlows();
        TrackTnDrag();
        TrackTrPan();
        if (m_TnSkipClick > 0)
            m_TnSkipClick--;
    }

    override bool OnMouseButtonDown(Widget w, int x, int y, int button)
    {
        if (w && M_SUB_WIDGET && m_TrFlows && button == MouseState.LEFT && m_RzTab == "tree" && !m_RzProblems)
        {
            string nm = w.GetName();
            if (nm.IndexOf("rznode:") == 0)
            {
                m_TnDragMoved = false;
                if (!m_TrLink)
                {
                    m_TnDragId = nm.Substring(7, nm.Length() - 7);
                    GetMousePos(m_TnDragX, m_TnDragY);
                    Widget cell = M_SUB_WIDGET.FindAnyWidget("rzcell:" + m_TnDragId);
                    if (cell)
                        cell.GetPos(m_TnCellX, m_TnCellY);
                }
            }
            else if (nm == "RzTrNodes" || nm == "RzTrContent" || (nm == "RzTrScroll" && !OnTrScrollbar(x, y)))
            {
                ScrollWidget sw = ScrollWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTrScroll"));
                if (sw)
                {
                    m_TrPanDown = true;
                    m_TrPanMoved = false;
                    GetMousePos(m_TrPanX, m_TrPanY);
                    m_TrPanH = sw.GetHScrollPos();
                    m_TrPanV = sw.GetVScrollPos();
                }
            }
        }
        return super.OnMouseButtonDown(w, x, y, button);
    }

    // Поле інспектора змінилось: правка вибраного вузла, один знімок на поле.
    protected void OnTnField(string field)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = TrNode(tree);
        if (!n)
            return;

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "tn:" + field);

        string v = GetEdit(field);
        bool structural = false;
        if (field == "RzTnId")
        {
            RenameTn(tree, n, v.Trim());
            structural = true;
        }
        else if (field == "RzTnName")
            n.Name = v;
        else if (field == "RzTnTier")
        {
            n.Tier = v.ToInt();
            structural = true;
        }
        else if (field == "RzTnParents")
        {
            OZL_EdTree.ParseParents(v, n);
            structural = true;
        }
        else if (field == "RzTnCost")
            OZL_EdTree.ParseCost(v, n);
        else if (field == "RzTnItems")
            OZL_EdTree.ParseItems(v, n);
        else if (field == "RzTnTime")
            n.ResearchTimeSec = v.ToInt();
        else if (field == "RzTnIcon")
            n.Icon = v.Trim();

        m_TnDelArmed = false;
        m_RzDiscardArmed = false;
        m_Ed.Commit(tag);
        RepaintTree(structural, false);
        TextWidget head = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzTnHead"));
        if (head)
            head.SetText(n.Id);
        PaintRzBar();
        PaintSummary();
    }

    // Новий Id вузла. Посилання (батьки інших вузлів) ідуть за ним лише на
    // ВІЛЬНИЙ Id: проміжний Id, що збігся з чужим, під час набору лишає їх
    // на попередньому -- інакше вони перейшли б до чужого вузла назавжди.
    protected void RenameTn(OZL_TreeConfig tree, OZL_TreeNode n, string id)
    {
        n.Id = id;
        m_TrSel = id;
        if (id == "" || id == m_TnRefId)
            return;
        if (OZL_EdTree.CountId(tree, id) != 1)
            return;
        OZL_EdTree.RenameRefs(tree, m_TnRefId, id);
        m_TnRefId = id;
    }

    protected void TnAdd(bool child)
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeBranch br = TrBranch(tree);
        if (!br)
        {
            Hint(Tr("#STR_OZL_ED_TR_PICK_BRANCH"));
            return;
        }
        OZL_TreeNode parent = null;
        if (child)
        {
            parent = TrNode(tree);
            if (!parent)
            {
                Hint(Tr("#STR_OZL_ED_TN_PICK"));
                return;
            }
        }

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        OZL_TreeNode n = new OZL_TreeNode();
        n.Id = OZL_EdTree.FreeId(tree, br.Id + "_node");
        n.Name = n.Id;
        n.Tier = 1;
        if (parent)
        {
            n.Tier = parent.Tier + 1;
            n.Parents.Insert(parent.Id);
        }
        br.Nodes.Insert(n);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();

        m_TrSel = n.Id;
        m_TnDelArmed = false;
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_TR_ADDED") + n.Id);
    }

    protected void TnDelete()
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = TrNode(tree);
        if (!n)
        {
            Hint(Tr("#STR_OZL_ED_TN_PICK"));
            return;
        }
        if (!m_TnDelArmed)
        {
            m_TnDelArmed = true;
            Hint(Tr("#STR_OZL_ED_TN_DEL_ARMED") + n.Id);
            return;
        }
        m_TnDelArmed = false;

        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        string id = n.Id;
        for (int b = 0; b < tree.Branches.Count(); b++)
        {
            OZL_TreeBranch br = tree.Branches[b];
            for (int i = br.Nodes.Count() - 1; i >= 0; i--)
            {
                if (br.Nodes[i] == n)
                    br.Nodes.RemoveOrdered(i);
            }
        }
        OZL_EdTree.DropRefs(tree, id);
        m_Ed.Commit(tag);
        m_Ed.EndGesture();

        m_TrSel = "";
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
        Hint(Tr("#STR_OZL_ED_TR_DELETED") + id);
    }

    protected void TnMode()
    {
        OZL_TreeConfig tree = DraftTree();
        OZL_TreeNode n = TrNode(tree);
        if (!n)
        {
            Hint(Tr("#STR_OZL_ED_TN_PICK"));
            return;
        }
        string tag = OZL_Config.TAG_TREE;
        m_Ed.BeginOnce(tag, "");
        string mode = n.ParentsMode;
        mode.ToLower();
        if (mode == "any")
            n.ParentsMode = "all";
        else
            n.ParentsMode = "any";
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        RepaintTree(true);
        PaintRzBar();
        PaintSummary();
    }

    // ================================================= розмір вікна

    // Вікно змінило розмір (OZ_VppAdminMenu.ApplyWindowSize): панель тепер
    // w x h пікселів. Генератор розмітки поставив усе в точні місця, тож
    // каркас редактора -- рядок підвкладок, сторінки, смуга дій, підказка --
    // і колонки дерева перекладаються звідси; ОГЛЯД і ТИПИ БАЛІВ лишаються
    // своїх розмірів у лівому верхньому куті сторінки.
    override void OnWindowResized(float w, float h)
    {
        super.OnWindowResized(w, h);
        if (!M_SUB_WIDGET)
            return;

        float s = Px();
        float iw = w - 2 * 20 * s;
        float ih = h - 2 * 20 * s;
        if (iw < 300 * s || ih < 200 * s)
            return;

        Widget body = M_SUB_WIDGET.FindAnyWidget("RzBody");
        if (body)
            body.SetSize(iw, ih);

        // Підвкладки -- порівну на всю ширину.
        array<string> tabs = {"overview", "tree", "chains", "points", "owners", "modules", "statics", "settings"};
        Widget nav = M_SUB_WIDGET.FindAnyWidget("RzNav");
        if (nav)
            nav.SetSize(iw, 28 * s);
        float tw = (iw - 7 * 6 * s) / 8;
        int i;
        for (i = 0; i < tabs.Count(); i++)
            PlaceBtn("RzNav_" + tabs[i], i * (tw + 6 * s), 0, tw, 28 * s);

        // Сторінки -- усе, що лишається між рядком підвкладок і смугою дій.
        float ph = ih - (28 + 8 + 8 + 28 + 8 + 22) * s;
        Widget pages = M_SUB_WIDGET.FindAnyWidget("RzPages");
        if (pages)
            pages.SetSize(iw, ph);
        array<string> names = {"overview", "points", "tree", "soon", "problems"};
        for (i = 0; i < names.Count(); i++)
        {
            Widget pg = M_SUB_WIDGET.FindAnyWidget("RzPage_" + names[i]);
            if (pg)
                pg.SetSize(iw, ph);
        }

        // Смуга дій -- під сторінками, кнопки праворуч.
        float by = (28 + 8) * s + ph + 8 * s;
        Widget bar = M_SUB_WIDGET.FindAnyWidget("RzBar");
        if (bar)
        {
            bar.SetPos(0, by);
            bar.SetSize(iw, 28 * s);
        }
        array<string> btns = {"BtnRzApply", "BtnRzDiscard", "BtnRzRedo", "BtnRzUndo", "BtnRzProblems"};
        array<float> bws = {160.0, 120.0, 120.0, 120.0, 190.0};
        float x = iw;
        for (i = 0; i < btns.Count(); i++)
        {
            x -= bws[i] * s;
            PlaceBtn(btns[i], x, 0, bws[i] * s, 28 * s);
            x -= 6 * s;
        }
        Widget st = M_SUB_WIDGET.FindAnyWidget("RzStatus");
        if (st)
            st.SetSize(x, 28 * s);

        Widget hint = M_SUB_WIDGET.FindAnyWidget("ResHint");
        if (hint)
        {
            hint.SetPos(0, by + (28 + 8) * s);
            hint.SetSize(iw, 22 * s);
        }

        // Список проблем -- на всю сторінку.
        Widget probCol = M_SUB_WIDGET.FindAnyWidget("RzProbCol");
        if (probCol)
            probCol.SetSize(iw, ph);
        Widget probList = M_SUB_WIDGET.FindAnyWidget("RzProbList");
        if (probList)
            probList.SetSize(iw, ph - 28 * s);

        // Колонки дерева: бічна -- на всю висоту, полотно -- усе між нею й
        // інспектором, інспектор -- до правого краю. Спершу сама рамка
        // колонок: рамка ріже дітей по своєму краю (gui-layouts §31), і без
        // неї інспектор за старою шириною зникав.
        Widget cols = M_SUB_WIDGET.FindAnyWidget("RzTrCols");
        if (cols)
            cols.SetSize(iw, ph);
        // Бічна: списки згори, список гілок бере зайве, дві кнопки перегляду
        // -- внизу (місця з розмітки: шапки 22, власники 150, проміжки 6).
        Widget side = M_SUB_WIDGET.FindAnyWidget("RzTrSide");
        if (side)
            side.SetSize(200 * s, ph);
        float brH = ph - 280 * s;
        if (brH < 40 * s)
            brH = 40 * s;
        Widget brs = M_SUB_WIDGET.FindAnyWidget("RzTrBranches");
        if (brs)
            brs.SetSize(200 * s, brH);
        PlaceBtn("BtnRzTrView", 0, 212 * s + brH + 6 * s, 200 * s, 28 * s);
        PlaceBtn("BtnRzTrDemo", 0, 212 * s + brH + 40 * s, 200 * s, 28 * s);

        float mw = iw - (200 + 290 + 24) * s;
        if (mw < 100 * s)
            mw = 100 * s;
        Widget mid = M_SUB_WIDGET.FindAnyWidget("RzTrMid");
        if (mid)
            mid.SetSize(mw, ph);
        Widget trBar = M_SUB_WIDGET.FindAnyWidget("RzTrBar");
        if (trBar)
            trBar.SetSize(mw, 28 * s);
        PlaceBtn("BtnRzTrLink", mw - 110 * s, 0, 110 * s, 28 * s);
        PlaceBtn("BtnRzTrChild", mw - (110 + 6 + 110) * s, 0, 110 * s, 28 * s);
        PlaceBtn("BtnRzTrRoot", mw - (110 + 6 + 110 + 6 + 100) * s, 0, 100 * s, 28 * s);
        Widget skinLbl = M_SUB_WIDGET.FindAnyWidget("RzTrSkin");
        if (skinLbl)
            skinLbl.SetSize(mw - (110 + 6 + 110 + 6 + 100 + 6) * s, 28 * s);
        Widget host = M_SUB_WIDGET.FindAnyWidget("RzTrHost");
        if (host)
            host.SetSize(mw, ph - 62 * s);
        Widget scroll = M_SUB_WIDGET.FindAnyWidget("RzTrScroll");
        if (scroll)
            scroll.SetSize(mw, ph - 62 * s);
        Widget info = M_SUB_WIDGET.FindAnyWidget("RzTrInfo");
        if (info)
        {
            info.SetPos(0, ph - 22 * s);
            info.SetSize(mw, 22 * s);
        }
        Widget insp = M_SUB_WIDGET.FindAnyWidget("RzTrInsp");
        if (insp)
            insp.SetPos(iw - 290 * s, 0);

        ScrollWidget sw = ScrollWidget.Cast(scroll);
        if (sw)
            sw.Update();
    }

    // Кнопка генератора -- корінь і троє дітей тієї самої ширини: рамка на
    // одиницю ширша з кожного боку, тло й напис -- як корінь.
    protected void PlaceBtn(string name, float x, float y, float w, float h)
    {
        Widget b = M_SUB_WIDGET.FindAnyWidget(name);
        if (!b)
            return;
        float s = Px();
        b.SetPos(x, y);
        b.SetSize(w, h);
        Widget edge = b.FindAnyWidget(name + "Edge");
        if (edge)
            edge.SetSize(w + 2 * s, h + 2 * s);
        Widget bg = b.FindAnyWidget(name + "Bg");
        if (bg)
            bg.SetSize(w, h);
        Widget tx = b.FindAnyWidget(name + "Text");
        if (tx)
            tx.SetSize(w, h);
    }

    // ================================================= події

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
        if (nm == "RzTrOwners")
        {
            OZL_Owners owners = DraftOwners();
            if (owners && row >= 0 && row < owners.Owners.Count() && owners.Owners[row])
            {
                m_TrOwner = owners.Owners[row].Id;
                m_TrBranch = "";
                m_TrSel = "";
                m_TrLinkFrom = "";
                m_TnDelArmed = false;
                m_BrDelArmed = false;
                m_Ed.EndGesture();
                RepaintTree(true);
            }
            return true;
        }
        if (nm == "RzTrBranches")
        {
            OZL_TreeConfig tree = DraftTree();
            if (tree)
            {
                array<string> ids = new array<string>();
                TrBranchIds(tree, ids);
                if (row >= 0 && row < ids.Count())
                {
                    m_TrBranch = ids[row];
                    m_TrSel = "";
                    m_TrLinkFrom = "";
                    m_TnDelArmed = false;
                    m_BrDelArmed = false;
                    m_Ed.EndGesture();
                    RepaintTree(true);
                }
            }
            return true;
        }
        if (nm == "RzPtList")
        {
            OZL_PointTypes pts = DraftPointTypes();
            if (pts && row >= 0 && row < pts.PointTypes.Count())
            {
                m_PtPicked = row;
                m_PtDelArmed = false;
                m_Ed.EndGesture();
                RepaintPoints(true);
            }
            return true;
        }
        return super.OnItemSelected(w, x, y, row, column, oldRow, oldColumn);
    }

    override bool OnChange(Widget w, int x, int y, bool finished)
    {
        if (w && M_SUB_WIDGET && !m_RzFill && m_Ed)
        {
            string nm = w.GetName();
            if (nm == "RzPtId" || nm == "RzPtName" || nm == "RzPtColor" || nm == "RzPtSort" || nm == "RzPtPurity" || nm == "RzPtIcon")
            {
                OnPtField(nm);
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
            if (nm.IndexOf("RzTn") == 0)
            {
                OnTnField(nm);
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
            if (nm.IndexOf("RzBr") == 0)
            {
                OnBrField(nm);
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
        }
        return super.OnChange(w, x, y, finished);
    }

    override bool OnClick(Widget w, int x, int y, int button)
    {
        if (!M_SUB_WIDGET || !w)
            return super.OnClick(w, x, y, button);

        string nm = w.GetName();

        // Підвкладки: ім'я кнопки після "RzNav_" -- ключ сторінки.
        if (nm.IndexOf("RzNav_") == 0)
        {
            ShowRzTab(nm.Substring(6, nm.Length() - 6));
            return true;
        }

        // Вузол на полотні: NodeHit його комірки названий rznode:<id>. Клік,
        // що прийшов із відпусканням після перетягування, -- не вибір.
        if (nm.IndexOf("rznode:") == 0)
        {
            if (m_TnSkipClick > 0 || m_TnDragMoved)
                return true;
            string picked = nm.Substring(7, nm.Length() - 7);
            m_TnDelArmed = false;
            m_Ed.EndGesture();
            if (m_TrLink)
            {
                TrLinkClick(picked);
                return true;
            }
            m_TrSel = picked;
            RepaintTree(false);
            return true;
        }
        if (nm == "BtnRzTrRoot")
        {
            TnAdd(false);
            return true;
        }
        if (nm == "BtnRzTrChild")
        {
            TnAdd(true);
            return true;
        }
        if (nm == "BtnRzTrLink")
        {
            TrLinkToggle();
            return true;
        }
        if (nm == "BtnRzTrView")
        {
            TrPreview();
            return true;
        }
        if (nm == "BtnRzTrDemo")
        {
            m_TrDemo = (m_TrDemo + 1) % 3;
            PaintTrButtons();
            return true;
        }
        if (nm == "BtnRzBrAdd")
        {
            BrAdd();
            return true;
        }
        if (nm == "BtnRzBrDel")
        {
            BrDelete();
            return true;
        }
        if (nm == "BtnRzTnMode")
        {
            TnMode();
            return true;
        }
        if (nm == "BtnRzTnDel")
        {
            TnDelete();
            return true;
        }

        if (nm == "BtnRzProblems")
        {
            m_RzProblems = !m_RzProblems;
            RepaintRz();
            return true;
        }
        if (nm == "BtnRzUndo")
        {
            RzUndo(false);
            return true;
        }
        if (nm == "BtnRzRedo")
        {
            RzUndo(true);
            return true;
        }
        if (nm == "BtnRzDiscard")
        {
            RzDiscard();
            return true;
        }
        if (nm == "BtnRzApply")
        {
            RzApply();
            return true;
        }
        if (nm == "BtnRzPtAdd")
        {
            PtAdd();
            return true;
        }
        if (nm == "BtnRzPtDel")
        {
            PtDelete();
            return true;
        }

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
                Hint("press RELOAD CONFIGS again to re-read the seven files and the state folder");
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

        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
