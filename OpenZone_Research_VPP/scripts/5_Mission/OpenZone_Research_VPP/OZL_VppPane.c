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

    override void OnCreate(Widget RootW)
    {
        super.OnCreate(RootW);
        if (!M_SUB_WIDGET)
            return;

        m_ResOwners = new array<ref OZL_AdminOwner>();
        m_Ed        = new OZL_EdDocs();

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
        if (m_Ed)
            m_Ed.EndGesture();
        RepaintRz();
    }

    // Сторінка, яку показує відкрита підвкладка.
    protected string RzPageOf(string key)
    {
        if (key == "overview" || key == "points")
            return key;
        return "soon";
    }

    protected void ShowRzPage(string page)
    {
        array<string> pages = {"overview", "points", "soon", "problems"};
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
            for (int i = 0; i < pts.PointTypes.Count(); i++)
            {
                OZL_PointType p = pts.PointTypes[i];
                string line = p.Id + "  -  " + p.Name + "  -  " + p.BasePurity.ToString();
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
        if (nm == "RzPtList")
        {
            OZL_PointTypes pts = DraftPointTypes();
            if (pts && row >= 0 && row < pts.PointTypes.Count())
            {
                m_PtPicked = row;
                m_PtDelArmed = false;
                m_Ed.EndGesture();
                FillPtForm();
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
