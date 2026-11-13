// The SETTINGS page of the research editor: OZ_Research_Settings.json, one object for
// every faction. A pane of its own since 2026-11-13, converted from its mockup board
// (css2layout, layout ozl_vpp_settings). On the left the fields: the default owner of
// the pool, who spends the pool (the research post and the base post), the depth of the
// tree's fog with its -/+ steps; on the right who spends the pool on this server, row by
// row, and the fog drawn as the player meets it.
//
// WHO SPENDS THE POOL IS DECIDED BY THE SOURCE OF FACTIONS, not by this mod:
// OZL_Access.MaySpend asks OZ_Identity.IsLeader and HasPost. So the page asks the core
// who gives the factions and what it knows (Ask config identity -> OZ_AdminIdentity) and
// shows that: OpenZone Factions -- the leader, then the post holders; OpenZone Identity
// FFR -- any member of a group or nobody (its own setting), it has no posts; another mod
// -- what it says itself; the core alone -- no factions, the pool goes to the default
// owner. The post fields the source does not know go dim, with what holds instead.
//
// ONE LAYOUT SERVES EVERY SOURCE (the boards ResearchSettings and ResearchSettingsFfr are
// one page in two states): what differs is text and colour, written here from the
// `identity` answer.
//
// What the frame calls here (the hooks of OZL_VppPane.c, each handed on with super):
//   RepaintRzPage("settings")   fill the page from the draft;
//   RzLayPages(pw, ph)          through CfgLayOpen of OZL_VppPaneConfigs.c: the words
//                               fitted to their text are fitted again;
//   OnRzConfigAnswer(...)       the `identity` answer;
//   OnPaneShown, OnClick, OnChange.
//
// A separate modded layer of OZ_VppAdminMenu: the file name sorts after OZL_VppPane.c,
// OZL_VppPaneChains.c and OZL_VppPaneConfigs.c (the files of a folder compile in
// alphabetical order, and the layer that overrides comes later); it uses the small
// things of OZL_VppPaneConfigs.c (CfgFitText, CfgPutAfter, CfgElide, CfgRefitSoon) and
// extends its CfgLayOpen.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    // The core's answer about the source of factions, copied out of the parsed
    // envelope: asked once per window, known when it came, failed when the core could
    // not answer (a core older than the question). Declared bare: they start as false
    // and "".
    private bool   m_SeIdAsked;
    private bool   m_SeIdKnown;
    private bool   m_SeIdFailed;
    private bool   m_SeIdPresent;
    private string m_SeIdSource;
    private bool   m_SeIdLeaders;
    private bool   m_SeIdPosts;
    private string m_SeIdMeans;

    // The source's line as PaintSource wrote it, whole: SePlace cuts it to the room it
    // has (a TextWidget does not give its text back).
    private string m_SeSourceLine;

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
    // cannot change while the server runs), unless its answer is here already.
    override void OnPaneShown(string id)
    {
        super.OnPaneShown(id);
        string page = RZ_PAGE;
        if (id != page + "settings" || m_SeIdAsked)
            return;
        m_SeIdAsked = true;
        if (m_SeIdKnown && !m_SeIdFailed)
            return;
        Ask(OZ_AdminSect.CONFIG, "identity", "{}");
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
        if (!M_SUB_WIDGET || !m_Ed)
            return;
        PaintSource();
        OZL_Settings se = DraftSettings();
        CfgRefitSoon();
        if (!se)
        {
            SetLabel("RzSeFogHead", Tr("#STR_OZL_ED_HINT_LOADING"), 0);
            ShowW("RzSeFogChanged", false);
            SePlace();
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

        // "Changed in the draft" beside the fog's head while this file differs from the
        // server's.
        OZL_EdDoc doc = m_Ed.Doc(OZL_Config.TAG_SETTINGS);
        bool dirty = false;
        if (doc)
            dirty = doc.Dirty();
        ShowW("RzSeFogChanged", dirty);

        PaintSpenders(se);
        PaintFog(se.TreeVisibilityDepth);
        SePlace();
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

    // Is the source the FFR glue (the core names it: the glue is a server mod, the
    // client never sees its class).
    protected bool SeIsFfr()
    {
        if (!SeIdTold())
            return false;
        return m_SeIdSource == FFR_SOURCE;
    }

    // What the source calls its leader, in its own words: a stringtable key (FFR) or
    // plain text; nothing when it does not say.
    protected string SeMeans()
    {
        if (m_SeIdMeans.IndexOf("#") == 0)
            return Tr(m_SeIdMeans);
        return m_SeIdMeans;
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
            line = nameless + " · " + untold;
        }
        else
        {
            // What the source calls its leader, in its own words, says more than "has
            // leaders" (FFR: any member of a group).
            string leaderPart = Tr("#STR_OZL_VPP_SE_NO_LEADERS");
            if (m_SeIdLeaders && m_SeIdMeans != "")
                leaderPart = SeMeans();
            else if (m_SeIdLeaders)
                leaderPart = Tr("#STR_OZL_VPP_SE_HAS_LEADERS");
            string postPart = Tr("#STR_OZL_VPP_SE_NO_POSTS");
            if (m_SeIdPosts)
                postPart = Tr("#STR_OZL_VPP_SE_HAS_POSTS");
            line = m_SeIdSource + " · " + leaderPart + ", " + postPart;
        }
        m_SeSourceLine = line;
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
        string means = "";
        if (told)
            means = SeMeans();

        // The leader row: what the source calls its leader, or the leader.
        string leaderWho = Tr("#STR_OZL_VPP_SE_ROW_LEADER");
        if (means != "")
            leaderWho = means;
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
        string hintResearch = Tr("#STR_OZL_VPP_SE_RPOST_H");
        string hintBase = Tr("#STR_OZL_VPP_SE_BPOST_H");
        if (none)
        {
            hintResearch = Tr("#STR_OZL_VPP_SE_NO_SOURCE_H");
            hintBase = hintResearch;
        }
        else if (!posts)
        {
            hintResearch = Tr("#STR_OZL_VPP_SE_NO_POSTS_H");
            hintBase = hintResearch;
        }
        DimPostField("RzSeRPost", !posts, hintResearch);
        DimPostField("RzSeBPost", !posts, hintBase);

        // The callout: who spends, in one line, and why.
        string tail = "";
        if (posts)
            tail = PostsTail(se);
        string whoLine = "";
        if (leaders)
        {
            whoLine = Tr("#STR_OZL_VPP_SE_LEADER");
            if (means != "")
                whoLine = means;
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
        CfgElide("RzSeWhoMain", whoLine);
        SetLabel("RzSeWhoWhy", SpendWhy(told, none, leaders, tail != ""), 0);

        // Where the leaders and posts themselves are edited: the factions module's
        // page, FFR's groups when the FFR glue gives the factions; no link when this
        // window has no such page.
        string linkPage = SeLinkPage();
        ShowW("BtnRzSeLink", linkPage != "");
        if (linkPage != "")
        {
            string linkWords = "#STR_OZL_VPP_SE_LINK_FACTIONS";
            if (linkPage == "ffr")
                linkWords = "#STR_OZL_VPP_SE_LINK_FFR";
            SetLabel("BtnRzSeLinkText", Tr(linkWords), 0);
        }

        // The note under the rows: FFR's own switch when FFR gives the factions.
        string note = "#STR_OZL_VPP_SE_SPEND_NOTE";
        if (SeIsFfr())
            note = "#STR_OZL_VPP_SE_SPEND_NOTE_FFR";
        SetLabel("RzSeSpendNote", Tr(note), 0);
    }

    // The page of this window where the source's leaders and posts are edited; nothing
    // when there is none.
    protected string SeLinkPage()
    {
        if (!SeIdTold() || !m_SeIdPresent)
            return "";
        if (SeIsFfr() && m_Panes.Contains("ffr"))
            return "ffr";
        return FirstPageOf("factions");
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

    // A post field with its label, frame and hint in the page's ink, or dim and closed
    // to typing; its placeholder says which.
    protected void DimPostField(string name, bool dim, string hint)
    {
        Widget field = M_SUB_WIDGET.FindAnyWidget(name);
        int ink = OZL_Metal.TEXT;
        int labelInk = OZL_Metal.MUTED;
        int ground = ARGB(255, 7, 7, 7);
        string empty = "#STR_OZL_VPP_SE_POST_PH";
        if (dim)
        {
            ink = OZL_Metal.FAINT;
            labelInk = OZL_Metal.FAINT;
            ground = ARGB(255, 19, 19, 18);
            empty = "#STR_OZL_VPP_SE_POST_PH_OFF";
        }
        bool open = !dim;
        if (field)
        {
            field.Enable(open);
            field.SetColor(ink);
        }
        SetColorOf(name + "Lbl", labelInk);
        SetLabel(name + "H", hint, labelInk);
        OZ_VppFlex.Paint(M_SUB_WIDGET, name + "BoxBg", ground);
        SetLabel(name + "Ph", Tr(empty), 0);
    }

    // "; then whoever holds the post «research», «base»" for the posts that are set;
    // nothing when neither is.
    protected string PostsTail(OZL_Settings se)
    {
        string posts = PostsList(se);
        if (posts == "")
            return "";
        string thenWord = Tr("#STR_OZL_VPP_SE_THEN_POST");
        return thenWord + posts;
    }

    // The posts that are set, each in quotes, comma-separated.
    protected string PostsList(OZL_Settings se)
    {
        string posts = "";
        if (se.ResearchPost != "")
            posts = "«" + se.ResearchPost + "»";
        if (se.BasePost != "" && se.BasePost != se.ResearchPost)
        {
            if (posts != "")
                posts += ", ";
            posts += "«" + se.BasePost + "»";
        }
        return posts;
    }

    // What one post row says: who holds it spends, or nobody but the leader.
    protected string PostRule(string post)
    {
        if (post == "")
            return Tr("#STR_OZL_VPP_SE_POST_EMPTY");
        string holds = Tr("#STR_OZL_VPP_SE_POST_HOLDS");
        return holds + "«" + post + "»";
    }

    // One row of the who-spends list: its number lit when the row is in force.
    protected void SpenderRow(int i, string who, string rule, bool on)
    {
        string n = i.ToString();
        int markInk = OZL_Metal.MUTED;
        int markGround = ARGB(255, 30, 30, 29);
        int ink = OZL_Metal.MUTED;
        if (on)
        {
            markInk = OZL_Metal.OK;
            markGround = ARGB(255, 32, 48, 30);
            ink = OZL_Metal.TEXT;
        }
        OZ_VppFlex.Paint(M_SUB_WIDGET, "RzSeMark" + n + "Bg", markGround);
        SetColorOf("RzSeMarkText" + n, markInk);
        SetLabel("RzSeWho" + n, who, OZL_Metal.TEXT);
        SetLabel("RzSeRule" + n, rule, ink);
    }

    // A box as wide as its caption in the client's language (a legend on its frame's top
    // line, a tag): the caption stands `pad` units in. Its parts are <name>Bg and
    // <name>Text.
    protected void SeHug(string name, float pad)
    {
        Widget box = M_SUB_WIDGET.FindAnyWidget(name);
        Widget ground = M_SUB_WIDGET.FindAnyWidget(name + "Bg");
        TextWidget caption = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(name + "Text"));
        if (box && caption && OZ_VppFlex.TextWidth(caption) > 0)
            OZ_VppFlex.Hug(box, ground, caption, pad * Px());
    }

    // What is fitted to its words: the two legends and the tag hug their captions, the
    // source's line ends at the box's right edge with the tag before it, "changed in the
    // draft" follows the fog's head, the link is as wide as its words.
    protected void SePlace()
    {
        float s = Px();
        SeHug("RzSeLegPool", 6);
        SeHug("RzSeLegFog", 6);
        SeHug("RzSeSourceTag", 8);
        Widget row = M_SUB_WIDGET.FindAnyWidget("RzSeSpendRow");
        Widget source = M_SUB_WIDGET.FindAnyWidget("RzSeSource");
        Widget tag = M_SUB_WIDGET.FindAnyWidget("RzSeSourceTag");
        if (row && source && tag)
        {
            float rw;
            float rh;
            row.GetSize(rw, rh);
            float sx;
            float sy;
            source.GetPos(sx, sy);
            float sw;
            float sh;
            source.GetSize(sw, sh);
            float tx;
            float ty;
            tag.GetPos(tx, ty);
            float tagW;
            float tagH;
            tag.GetSize(tagW, tagH);

            // The line has the row less the head's words (170 units hold them in both
            // languages), the tag and the gaps; a longer line is cut short with a mark.
            float room = rw - tagW - 190 * s;
            if (room < 60 * s)
                room = 60 * s;
            source.SetSize(room, sh);
            CfgElide("RzSeSource", m_SeSourceLine);
            float tw = OZ_VppFlex.TextWidth(TextWidget.Cast(source));
            if (tw > 0)
            {
                source.SetPos(rw - tw - 2, sy);
                source.SetSize(tw + 2, sh);
                tag.SetPos(rw - tw - 2 - 10 * s - tagW, ty);
            }
            else
                source.SetPos(rw - room, sy);
        }

        CfgPutAfter(M_SUB_WIDGET.FindAnyWidget("RzSeFogHead"), M_SUB_WIDGET.FindAnyWidget("RzSeFogChanged"), 10);

        Widget link = M_SUB_WIDGET.FindAnyWidget("BtnRzSeLink");
        Widget linkText = M_SUB_WIDGET.FindAnyWidget("BtnRzSeLinkText");
        float lw = CfgFitText(linkText);
        if (link && linkText && lw > 0)
        {
            float bw;
            float bh;
            link.GetSize(bw, bh);
            link.SetSize(lw + 2, bh);
        }
    }

    // ------------------------------------------------- the fog, drawn
    //
    // A done node and the four steps after it, as the player's tree shows them at this
    // depth: the steps within the depth with their names, the rest as nameless stubs,
    // the fog's edge between the two. Numbers are the board's, in layout units: the
    // nodes stand 140 apart from 40, 46 down, 16 in radius.

    protected void PaintFog(int depth)
    {
        int cText = ARGB(255, 224, 223, 218);
        int cMuted = ARGB(255, 160, 159, 153);
        int cOk = ARGB(255, 102, 199, 92);
        int cAlert = ARGB(255, 245, 199, 64);
        float s = Px();

        int seen = depth;
        if (seen > 4)
            seen = 4;
        if (seen < 0)
            seen = 0;

        // The words under the nodes.
        string doneWord = Tr("#STR_OZL_VPP_SE_FOG_DONE");
        string seenWord = Tr("#STR_OZL_VPP_SE_FOG_SEEN");
        string stubWord = Tr("#STR_OZL_VPP_SE_FOG_STUB");
        string namedWord = Tr("#STR_OZL_VPP_SE_FOG_NAMED");
        string namelessWord = Tr("#STR_OZL_VPP_SE_FOG_NAMELESS");
        string edgeWord = Tr("#STR_OZL_VPP_SE_FOG_EDGE");
        SeFogWord("RzSeFogLab0", doneWord, 40, 73, 80, cText);
        int i;
        for (i = 1; i <= 4; i++)
        {
            float cx = 40 + 140 * i;
            if (i <= seen)
                SeFogWord("RzSeFogLab" + i.ToString(), seenWord + i.ToString(), cx, 73, 120, cText);
            else
                SeFogWord("RzSeFogLab" + i.ToString(), stubWord, cx, 73, 120, cMuted);
        }

        // The second line: "with a name" under every step that is seen, one "no name"
        // under the middle of the stubs. Four labels serve any depth.
        int used = 0;
        for (i = 1; i <= seen; i++)
        {
            SeFogWord("RzSeFogSub" + used.ToString(), namedWord, 40 + 140 * i, 91, 120, cMuted);
            used++;
        }
        if (seen < 4)
        {
            float mid = (40 + 140 * (seen + 1) + 600) / 2.0;
            SeFogWord("RzSeFogSub" + used.ToString(), namelessWord, mid, 91, 120, cMuted);
            used++;
        }
        for (i = used; i < 4; i++)
            ShowW("RzSeFogSub" + i.ToString(), false);

        // The fog's edge: between the last step that is seen and the first stub.
        float edgeX = 110 + 140 * seen;
        ShowW("RzSeFogEdge", seen < 4);
        if (seen < 4)
            SeFogWord("RzSeFogEdge", edgeWord, edgeX + 6 + 60, 7, 120, cAlert);

        CanvasWidget cv = CanvasWidget.Cast(M_SUB_WIDGET.FindAnyWidget("RzSeFogCanvas"));
        if (!cv)
            return;
        cv.Clear();
        float cy = 46 * s;
        float r = 16 * s;

        // The links: done to the first step in the done colour, between steps that are
        // seen in the page's ink, to a stub dashed.
        for (i = 0; i < 4; i++)
        {
            float x1 = (56 + 140 * i) * s;
            float x2 = (164 + 140 * i) * s;
            if (i + 1 > seen)
                SeDash(cv, x1, cy, x2, cy, 5 * s, 5 * s, 2 * s, cMuted);
            else if (i == 0)
                cv.DrawLine(x1, cy, x2, cy, 2 * s, cOk);
            else
                cv.DrawLine(x1, cy, x2, cy, 2 * s, cText);
        }
        if (seen < 4)
            SeDash(cv, edgeX * s, 8 * s, edgeX * s, 104 * s, 4 * s, 4 * s, 1.5 * s, cAlert);

        // The nodes: done with its tick, the seen ones whole, the stubs dashed.
        SeDisc(cv, 40 * s, cy, r, ARGB(255, 28, 46, 26));
        SeRing(cv, 40 * s, cy, r, 2 * s, cOk, false);
        cv.DrawLine(33 * s, 46.5 * s, 38 * s, 51.5 * s, 2.2 * s, cOk);
        cv.DrawLine(38 * s, 51.5 * s, 47 * s, 41.5 * s, 2.2 * s, cOk);
        for (i = 1; i <= 4; i++)
        {
            float nx = (40 + 140 * i) * s;
            if (i <= seen)
            {
                SeDisc(cv, nx, cy, r, ARGB(255, 19, 19, 18));
                SeRing(cv, nx, cy, r, 2 * s, cText, false);
            }
            else
                SeRing(cv, nx, cy, r, 2 * s, cMuted, true);
        }
    }

    // A word of the fog's scheme: centred on cx, w wide, y down (layout units).
    protected void SeFogWord(string name, string text, float cx, float y, float w, int color)
    {
        TextWidget t = TextWidget.Cast(M_SUB_WIDGET.FindAnyWidget(name));
        if (!t)
            return;
        float s = Px();
        t.Show(true);
        t.SetText(text);
        t.SetColor(color);
        t.SetPos((cx - w / 2) * s, y * s);
        t.SetSize(w * s, 14 * s);
    }

    // A dashed line: `on` drawn, `off` skipped, in pixels.
    protected void SeDash(CanvasWidget cv, float x1, float y1, float x2, float y2, float on, float off, float width, int color)
    {
        float dx = x2 - x1;
        float dy = y2 - y1;
        float len = Math.Sqrt(dx * dx + dy * dy);
        if (len <= 0 || on <= 0)
            return;
        float ux = dx / len;
        float uy = dy / len;
        float at = 0;
        while (at < len)
        {
            float to = at + on;
            if (to > len)
                to = len;
            cv.DrawLine(x1 + ux * at, y1 + uy * at, x1 + ux * to, y1 + uy * to, width, color);
            at = at + on + off;
        }
    }

    // A circle as 32 strokes; every other one left out when dashed.
    protected void SeRing(CanvasWidget cv, float cx, float cy, float r, float width, int color, bool dashed)
    {
        int n = 32;
        float px = cx + r;
        float py = cy;
        for (int i = 1; i <= n; i++)
        {
            float a = i * Math.PI2 / n;
            float x = cx + r * Math.Cos(a);
            float y = cy + r * Math.Sin(a);
            int odd = i % 2;
            if (!dashed || odd == 1)
                cv.DrawLine(px, py, x, y, width, color);
            px = x;
            py = y;
        }
    }

    // A filled circle: a stroke per pixel row.
    protected void SeDisc(CanvasWidget cv, float cx, float cy, float r, int color)
    {
        int rows = r;
        for (int j = -rows; j <= rows; j++)
        {
            float rest = r * r - j * j;
            if (rest <= 0)
                continue;
            float half = Math.Sqrt(rest);
            cv.DrawLine(cx - half, cy + j, cx + half, cy + j, 1.5, color);
        }
    }

    // ------------------------------------------------- edits

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

    // The open page is laid again (a resize, the second pass after a repaint): what this
    // page fitted to its words is fitted again.
    override void CfgLayOpen()
    {
        super.CfgLayOpen();
        if (!M_SUB_WIDGET || m_RzTab != "settings")
            return;
        SePlace();
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
            // The callout's link: the page where the source's leaders and posts live.
            if (nm == "BtnRzSeLink")
            {
                string linkPage = SeLinkPage();
                if (linkPage != "")
                    ShowPane(linkPage);
                return true;
            }
            // The fog's link: the tree page, where "as the player sees it" shows it.
            if (nm == "BtnRzSeFogLink")
            {
                string treePage = RZ_PAGE;
                ShowPane(treePage + "tree");
                return true;
            }
        }
        return super.OnClick(w, x, y, button);
    }
}

#endif
#endif
#endif
