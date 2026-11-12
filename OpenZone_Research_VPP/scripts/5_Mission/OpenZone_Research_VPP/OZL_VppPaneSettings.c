// Сторінка НАЛАШТУВАННЯ редактора досліджень (переробка вікна VPP
// 2026-11-12, дизайн вікна §5.5): OZ_Research_Settings.json -- один об'єкт
// для всіх фракцій. Ліворуч поля: типовий власник пулу, хто тратить пул
// (пост дослідника й базовий пост), глибина туману дерева з кроками -/+;
// праворуч -- хто тратить пул на цьому сервері рядками й що каже туман.
// До 2026-11-12 ці чотири поля жили на спільній сторінці конфігів.
//
// Окремий modded-шар OZ_VppAdminMenu: ім'я файлу сортується після
// OZL_VppPane.c, OZL_VppPaneChains.c й OZL_VppPaneConfigs.c (файли теки
// компілюються за абеткою, шар, що перекриває, мусить іти пізніше).

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    override void RepaintRzPage(string tab)
    {
        if (tab == "settings")
        {
            RepaintSettings(true);
            return;
        }
        super.RepaintRzPage(tab);
    }

    protected OZL_Settings DraftSettings()
    {
        if (!m_Ed)
            return null;
        OZL_EdDoc d = m_Ed.Doc(OZL_Config.TAG_SETTINGS);
        if (!d || !d.Loaded)
            return null;
        return OZL_Settings.Cast(d.Obj);
    }

    // The page from the draft; fillForm writes the fields too (not while one is typed
    // in: the cursor would jump to the end).
    protected void RepaintSettings(bool fillForm)
    {
        OZL_Settings se = DraftSettings();
        if (!se)
        {
            SetLabel("RzSeFogHead", Tr("#STR_OZL_ED_HINT_LOADING"), 0);
            return;
        }
        if (fillForm)
        {
            m_RzFill = true;
            SetEdit("RzSeOwner", se.DefaultOwner);
            SetEdit("RzSeRPost", se.ResearchPost);
            SetEdit("RzSeBPost", se.BasePost);
            SetEdit("RzSeDepth", se.TreeVisibilityDepth.ToString());
            m_RzFill = false;
        }
        string fogWord = Tr("#STR_OZL_VPP_SE_FOG_HEAD");
        SetLabel("RzSeFogHead", fogWord + se.TreeVisibilityDepth.ToString(), 0);
        PaintSpenders(se);
    }

    // Who spends the pool, as the research mod decides it (OZL_Access.MaySpend): the
    // faction's leader always, then whoever holds the post -- the research post in a
    // group, the base post on the base axis; an empty post means nobody but the
    // leader. Three rows, the ones in force lit.
    //
    // Every translated piece is taken into a local before it meets another: a
    // translation on the left of "+" (or beside another as an argument) is lost when
    // the right part translates too (dayz-modding mod-structure.md, "Reading strings
    // from SCRIPT").
    protected void PaintSpenders(OZL_Settings se)
    {
        string tail = PostsTail(se);
        string leader = Tr("#STR_OZL_VPP_SE_LEADER");
        SetLabel("RzSeWhoMain", leader + tail, 0);
        SetLabel("RzSeWhoWhy", Tr("#STR_OZL_ED_CFG_NOTE_SE"), 0);

        string whoLeader = Tr("#STR_OZL_VPP_SE_ROW_LEADER");
        string always = Tr("#STR_OZL_VPP_SE_ALWAYS");
        SpenderRow(0, whoLeader, always, true);
        string whoResearch = Tr("#STR_OZL_VPP_SE_ROW_RPOST");
        string ruleResearch = PostRule(se.ResearchPost);
        SpenderRow(1, whoResearch, ruleResearch, se.ResearchPost != "");
        string whoBase = Tr("#STR_OZL_VPP_SE_ROW_BPOST");
        string ruleBase = PostRule(se.BasePost);
        SpenderRow(2, whoBase, ruleBase, se.BasePost != "");
    }

    // "; далі -- хто має пост «research»" for the posts that are set; nothing when
    // neither is.
    protected string PostsTail(OZL_Settings se)
    {
        string posts = "";
        if (se.ResearchPost != "")
            posts = se.ResearchPost;
        if (se.BasePost != "" && se.BasePost != se.ResearchPost)
        {
            if (posts != "")
                posts += ", ";
            posts += se.BasePost;
        }
        if (posts == "")
            return "";
        string thenWord = Tr("#STR_OZL_VPP_SE_THEN_POST");
        return thenWord + posts;
    }

    // What one post row says: who holds it spends, or nobody but the leader.
    protected string PostRule(string post)
    {
        if (post == "")
            return Tr("#STR_OZL_VPP_SE_POST_EMPTY");
        string holds = Tr("#STR_OZL_VPP_SE_POST_HOLDS");
        return holds + post;
    }

    // One row of the who-spends list: its number lit when the row is in force.
    protected void SpenderRow(int i, string who, string rule, bool on)
    {
        string n = i.ToString();
        int mark = OZL_Metal.FAINT;
        int ink = OZL_Metal.MUTED;
        if (on)
        {
            mark = OZL_Metal.OK;
            ink = OZL_Metal.TEXT;
        }
        SetColorOf("RzSeMark" + n, mark);
        SetLabel("RzSeWho" + n, who, OZL_Metal.TEXT);
        SetLabel("RzSeRule" + n, rule, ink);
    }

    protected void OnSeField(string field)
    {
        OZL_Settings se = DraftSettings();
        if (!se)
            return;
        string tag = OZL_Config.TAG_SETTINGS;
        m_Ed.BeginOnce(tag, "se:" + field);
        string v = GetEdit(field);
        string vt = v.Trim();
        if (field == "RzSeOwner")
            se.DefaultOwner = vt;
        else if (field == "RzSeRPost")
            se.ResearchPost = vt;
        else if (field == "RzSeBPost")
            se.BasePost = vt;
        else if (field == "RzSeDepth")
            se.TreeVisibilityDepth = vt.ToInt();
        m_Ed.Commit(tag);
        RepaintSettings(false);
        PaintRzBar();
        PaintSummary();
    }

    // The fog depth one step down or up, kept in 0..10 as the server keeps it.
    protected void SeDepthBy(int delta)
    {
        OZL_Settings se = DraftSettings();
        if (!se)
            return;
        int depth = se.TreeVisibilityDepth + delta;
        if (depth < 0)
            depth = 0;
        if (depth > 10)
            depth = 10;
        if (depth == se.TreeVisibilityDepth)
            return;
        string tag = OZL_Config.TAG_SETTINGS;
        m_Ed.BeginOnce(tag, "");
        se.TreeVisibilityDepth = depth;
        m_Ed.Commit(tag);
        m_Ed.EndGesture();
        RepaintSettings(true);
        PaintRzBar();
        PaintSummary();
    }

    // The settings page in the page area pw x ph (pixels): two columns of fixed
    // width; the right one follows the left.
    override void RzLayPages(float pw, float ph)
    {
        super.RzLayPages(pw, ph);
        if (!M_SUB_WIDGET)
            return;
        float s = Px();
        SizeW("RzSeLeft", 500 * s, ph);
        float rightW = pw - 516 * s;
        if (rightW < 300 * s)
            rightW = 300 * s;
        if (rightW > 600 * s)
            rightW = 600 * s;
        PlaceW("RzSeRight", 516 * s, 0, rightW, ph);
    }

    override bool OnChange(Widget w, int x, int y, bool finished)
    {
        if (w && M_SUB_WIDGET && !m_RzFill && m_Ed)
        {
            string nm = w.GetName();
            if (nm == "RzSeOwner" || nm == "RzSeRPost" || nm == "RzSeBPost" || nm == "RzSeDepth")
            {
                OnSeField(nm);
                if (finished)
                    m_Ed.EndGesture();
                return true;
            }
        }
        return super.OnChange(w, x, y, finished);
    }

    override bool OnClick(Widget w, int x, int y, int button)
    {
        if (w && M_SUB_WIDGET && m_Ed)
        {
            string nm = w.GetName();
            if (nm == "BtnRzSeDepthDn")
            {
                SeDepthBy(-1);
                return true;
            }
            if (nm == "BtnRzSeDepthUp")
            {
                SeDepthBy(1);
                return true;
            }
        }
        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
