// The research module's card on Ядро › Огляд (the core's OZ_AdminFacts, VPP
// rework 2026-11-12, design §4.3): owners, nodes, rules and statics; the
// problems of its seven files and of their cross-checks. "Reload every
// module" reads the files and the owners' states again, as the editor's own
// `reload` does (OZL_Admin).
class OZL_Facts : OZ_AdminFactsProvider
{
    override void Fill(OZ_AdminModuleCard card)
    {
        OZL_Config cfg = OZL_Config.Get();
        card.Id = "research";
        card.Name = "#STR_OZL_VPP_MOD";

        // Pages in the window come with the VPP glue of this repo; a server
        // that loads no VPP has the card without them.
        card.Pages = 0;
#ifdef OpenZone_Research_VPP
        card.Pages = 1;
#endif

        int found = cfg.Problems();
        array<string> tags = new array<string>();
        OZL_Config.Tags(tags);
        for (int i = 0; i < tags.Count(); i++)
            found += OZ_ConfigProblems.Of(tags[i]);
        card.Problems = found;

        card.Add("#STR_OZL_FACT_OWNERS", cfg.Owners().Owners.Count().ToString());
        card.Add("#STR_OZL_FACT_NODES", cfg.Tree().NodeCount().ToString());
        card.Add("#STR_OZL_FACT_RULES", cfg.Rules().Count().ToString());
        card.Add("#STR_OZL_FACT_STATICS", cfg.Statics().Entries.Count().ToString());
    }

    override bool Reload(array<string> said)
    {
        OZL_Config.Reload();
        int states = OZL_State.Scan();
        OZL_Log.Info("overview: configs reloaded, " + states.ToString() + " owner file(s) read");
        return true;
    }
}
