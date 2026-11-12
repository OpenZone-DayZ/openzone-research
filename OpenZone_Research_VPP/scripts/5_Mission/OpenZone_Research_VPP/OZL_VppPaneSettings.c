// Сторінка НАЛАШТУВАННЯ редактора досліджень (переробка вікна VPP
// 2026-11-12, дизайн вікна §5.5): OZ_Research_Settings.json -- один об'єкт
// для всіх фракцій. Ліворуч поля: типовий власник пулу, хто тратить пул
// (пост дослідника й базовий пост), глибина туману дерева з кроками -/+;
// праворуч -- хто тратить пул на цьому сервері рядками й що каже туман.
// До 2026-11-12 ці чотири поля жили на спільній сторінці конфігів.
//
// ХТО ТРАТИТЬ ПУЛ, ВИРІШУЄ ДЖЕРЕЛО ФРАКЦІЙ, а не цей мод: OZL_Access.MaySpend
// питає OZ_Identity.IsLeader і HasPost. Тож сторінка питає ядро, хто дає
// фракції й що воно знає (Ask config identity -> OZ_AdminIdentity), і
// показує це: OpenZone Factions -- лідер, далі власники постів; OpenZone
// Identity FFR -- будь-який член групи або ніхто (її власне налаштування),
// постів там немає; інший мод -- що він сам каже; лише ядро -- фракцій
// немає, пул іде типовому власнику. Поля постів, яких джерело не знає,
// гаснуть із поясненням. Сумісно з Міражем (FFR), з нашими фракціями й з
// чужими (власник, 2026-11-12).
//
// Окремий modded-шар OZ_VppAdminMenu: ім'я файлу сортується після
// OZL_VppPane.c, OZL_VppPaneChains.c й OZL_VppPaneConfigs.c (файли теки
// компілюються за абеткою, шар, що перекриває, мусить іти пізніше).

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    // The core's answer about the source of factions, copied out of the parsed
    // envelope: asked once per window, known when it came, failed when the core
    // could not answer (a core older than the question).
    private bool   m_SeIdAsked   = false;
    private bool   m_SeIdKnown   = false;
    private bool   m_SeIdFailed  = false;
    private bool   m_SeIdPresent = false;
    private string m_SeIdSource  = "";
    private bool   m_SeIdLeaders = false;
    private bool   m_SeIdPosts   = false;
    private string m_SeIdMeans   = "";

    override void RepaintRzPage(string tab)
    {
        if (tab == "settings")
        {
            RepaintSettings(true);
            return;
        }
        super.RepaintRzPage(tab);
    }

    // The settings page shown: the source of factions is asked once per window (it
    // cannot change while the server runs).
    override void OnPaneShown(string id)
    {
        super.OnPaneShown(id);
        string page = RZ_PAGE;
        if (id != page + "settings" || m_SeIdAsked)
            return;
        m_SeIdAsked = true;
        Ask(OZ_AdminSect.CONFIG, "identity", "{}");
    }

    // A question, not an action: it does not open a line of the window's journal.
    override bool IsReadOp(string op)
    {
        if (op == "identity")
            return true;
        return super.IsReadOp(op);
    }

    override void OnRzConfigAnswer(string op, bool ok, string json, string error)
    {
        super.OnRzConfigAnswer(op, ok, json, error);
        if (op != "identity")
            return;

        m_SeIdKnown = true;
        bool failed = true;
        if (ok)
        {
            // Root made by the script, every field taken out at once (the core's
            // OZ_ConfigBase header): the envelope lives only until it is parsed.
            OZ_AdminIdentity info = new OZ_AdminIdentity();
            string err;
            if (JsonFileLoader<OZ_AdminIdentity>.LoadData(json, info, err))
            {
                bool present = info.Present;
                string source = info.Source;
                bool leaders = info.HasLeaders;
                bool posts = info.HasPosts;
                string means = info.LeaderMeans;
                m_SeIdPresent = present;
                m_SeIdSource = source;
                m_SeIdLeaders = leaders;
                m_SeIdPosts = posts;
                m_SeIdMeans = means;
                failed = false;
            }
        }
        m_SeIdFailed = failed;
        if (m_RzTab == "settings")
            RepaintSettings(false);
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
        PaintSource();
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

    // ------------------------------------------------- the source of factions

    // Do we know what the source can say? Not while the answer is on its way, not
    // when the core could not answer, not from a provider that names nothing (one that
    // predates the question keeps the defaults, which would read as "knows nothing").
    protected bool SeIdTold()
    {
        if (!m_SeIdKnown || m_SeIdFailed)
            return false;
        if (m_SeIdPresent && m_SeIdSource == "")
            return false;
        return true;
    }

    // "Factions come from": the source's name and what it knows.
    protected void PaintSource()
    {
        string line;
        int ink = OZL_Metal.TEXT;
        if (!m_SeIdKnown)
        {
            line = Tr("#STR_OZL_VPP_SE_SRC_ASKING");
            ink = OZL_Metal.MUTED;
        }
        else if (m_SeIdFailed)
        {
            line = Tr("#STR_OZL_VPP_SE_SRC_FAILED");
            ink = OZL_Metal.ALERT;
        }
        else if (!m_SeIdPresent)
        {
            line = Tr("#STR_OZL_VPP_SE_SRC_NONE");
            ink = OZL_Metal.ALERT;
        }
        else if (m_SeIdSource == "")
        {
            string nameless = Tr("#STR_OZL_VPP_SE_SRC_NAMELESS");
            string untold = Tr("#STR_OZL_VPP_SE_CAPS_UNKNOWN");
            line = nameless + "  |  " + untold;
        }
        else
        {
            // What the source calls its leader, in its own words, says more than "has
            // leaders" (FFR: any member of a group).
            string leaderPart = Tr("#STR_OZL_VPP_SE_NO_LEADERS");
            if (m_SeIdLeaders && m_SeIdMeans != "")
                leaderPart = m_SeIdMeans;
            else if (m_SeIdLeaders)
                leaderPart = Tr("#STR_OZL_VPP_SE_HAS_LEADERS");
            string postPart = Tr("#STR_OZL_VPP_SE_NO_POSTS");
            if (m_SeIdPosts)
                postPart = Tr("#STR_OZL_VPP_SE_HAS_POSTS");
            line = m_SeIdSource + "  |  " + leaderPart + ", " + postPart;
        }
        SetLabel("RzSeSource", line, ink);
    }

    // Who spends the pool on this server, as the research mod decides it
    // (OZL_Access.MaySpend) with what the source of factions knows: the leader --
    // or what the source calls its leader -- always, then whoever holds the post: the
    // research post in a group, the base post on the base axis; an empty post means
    // nobody but the leader. Three rows, the ones in force lit; the post fields go
    // dim when the source has no posts.
    //
    // Every translated piece is taken into a local before it meets another: a
    // translation on the left of "+" (or beside another as an argument) is lost when
    // the right part translates too (dayz-modding mod-structure.md, "Reading strings
    // from SCRIPT").
    protected void PaintSpenders(OZL_Settings se)
    {
        bool told = SeIdTold();
        bool none = (told && !m_SeIdPresent);
        bool leaders = true;
        bool posts = true;
        if (told)
        {
            leaders = m_SeIdLeaders;
            posts = m_SeIdPosts;
        }
        if (none)
        {
            leaders = false;
            posts = false;
        }

        // The leader row: what the source calls its leader, or the leader.
        string leaderWho = Tr("#STR_OZL_VPP_SE_ROW_LEADER");
        if (told && m_SeIdMeans != "")
            leaderWho = m_SeIdMeans;
        string leaderRule = Tr("#STR_OZL_VPP_SE_ALWAYS");
        if (none)
            leaderRule = Tr("#STR_OZL_VPP_SE_OFF_NONE");
        else if (!leaders)
            leaderRule = Tr("#STR_OZL_VPP_SE_OFF_LEADERS");
        SpenderRow(0, leaderWho, leaderRule, leaders);

        // The post rows.
        string offPosts = Tr("#STR_OZL_VPP_SE_OFF_POSTS");
        if (none)
            offPosts = Tr("#STR_OZL_VPP_SE_OFF_NONE");
        string whoResearch = Tr("#STR_OZL_VPP_SE_ROW_RPOST");
        string ruleResearch = offPosts;
        if (posts)
            ruleResearch = PostRule(se.ResearchPost);
        bool researchOn = (posts && se.ResearchPost != "");
        SpenderRow(1, whoResearch, ruleResearch, researchOn);
        string whoBase = Tr("#STR_OZL_VPP_SE_ROW_BPOST");
        string ruleBase = offPosts;
        if (posts)
            ruleBase = PostRule(se.BasePost);
        bool baseOn = (posts && se.BasePost != "");
        SpenderRow(2, whoBase, ruleBase, baseOn);

        // The post fields: dim where the source has no posts, with what holds instead.
        string postHint = Tr("#STR_OZL_ED_CFG_SE_POST_H");
        if (none)
            postHint = Tr("#STR_OZL_VPP_SE_NO_SOURCE_H");
        else if (!posts)
            postHint = Tr("#STR_OZL_VPP_SE_NO_POSTS_H");
        DimPostField("RzSeRPost", !posts, postHint);
        DimPostField("RzSeBPost", !posts, postHint);

        // The callout: who spends, in one line, and why.
        string tail = "";
        if (posts)
            tail = PostsTail(se);
        string whoLine = "";
        if (leaders)
        {
            whoLine = Tr("#STR_OZL_VPP_SE_LEADER");
            if (told && m_SeIdMeans != "")
                whoLine = m_SeIdMeans;
            whoLine += tail;
        }
        else if (tail != "")
        {
            string holders = Tr("#STR_OZL_VPP_SE_POST_HOLDS");
            whoLine = holders + PostsList(se);
        }
        else
        {
            whoLine = Tr("#STR_OZL_VPP_SE_NOBODY");
        }
        SetLabel("RzSeWhoMain", whoLine, 0);
        SetLabel("RzSeWhoWhy", SpendWhy(told, none, leaders, tail != ""), 0);
    }

    // Why the callout says what it says.
    protected string SpendWhy(bool told, bool none, bool leaders, bool posts)
    {
        if (!told)
            return Tr("#STR_OZL_VPP_SE_WHY_UNKNOWN");
        if (none)
            return Tr("#STR_OZL_VPP_SE_WHY_NONE");
        if (!leaders && !posts)
            return Tr("#STR_OZL_VPP_SE_WHY_NOBODY");
        string fromWord = Tr("#STR_OZL_VPP_SE_WHY_FROM");
        string rest = Tr("#STR_OZL_VPP_SE_WHY_TAIL");
        return fromWord + m_SeIdSource + ". " + rest;
    }

    // A post field and its label in the page's ink, or dim and closed to typing.
    protected void DimPostField(string name, bool dim, string hint)
    {
        Widget field = M_SUB_WIDGET.FindAnyWidget(name);
        int ink = OZL_Metal.TEXT;
        int labelInk = OZL_Metal.MUTED;
        int hintInk = OZL_Metal.FAINT;
        if (dim)
        {
            ink = OZL_Metal.FAINT;
            labelInk = OZL_Metal.FAINT;
            hintInk = OZL_Metal.ALERT;
        }
        bool open = !dim;
        if (field)
        {
            field.Enable(open);
            field.SetColor(ink);
        }
        SetColorOf(name + "Lbl", labelInk);
        SetLabel(name + "H", hint, hintInk);
    }

    // "; далі -- хто має пост research, base" for the posts that are set; nothing
    // when neither is.
    protected string PostsTail(OZL_Settings se)
    {
        string posts = PostsList(se);
        if (posts == "")
            return "";
        string thenWord = Tr("#STR_OZL_VPP_SE_THEN_POST");
        return thenWord + posts;
    }

    // The posts that are set, comma-separated.
    protected string PostsList(OZL_Settings se)
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
        return posts;
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
