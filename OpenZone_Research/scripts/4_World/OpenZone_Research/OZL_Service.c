// Служба `research` у реєстрі ядра: дерево власника й старт дослідження.
//
// Ворота ядра (прилад, права адміна) до неї не стосуються -- і саме тому вона
// служба, а не сторінка: дерево дивиться будь-який член фракції, а хто може
// тратити, вирішує OZL_Access при старті. Відповідь `tree` -- JSON
// OZL_TreeView, ядро ріже його на частини саме; відмова -- ключ рядка.

class OZL_Service : OZ_ServiceHandler
{
    override string Handle(string op, string json, PlayerIdentity sender, out bool ok, out string error)
    {
        ok = false;
        error = "STR_OZ_ERR_UNKNOWN_OP";
        if (!sender)
            return "";

        string uid = sender.GetPlainId();
        PlayerBase player = PlayerBase.Cast(sender.GetPlayer());
        string owner;
        if (player)
            owner = OZL_Owner.OfPlayer(player);
        else
            owner = OZL_Owner.Of(uid);

        if (op == OZL_Const.OP_TREE)
        {
            ok = true;
            error = "";
            OZL_Log.Dbg("tree for " + uid + " (" + owner + ")");
            return OZL_Tree.ViewJson(owner, uid);
        }

        if (op == OZL_Const.OP_RESEARCH)
        {
            OZL_ResearchReq req = new OZL_ResearchReq();
            string err;
            if (!JsonFileLoader<OZL_ResearchReq>.LoadData(json, req, err))
            {
                OZL_Log.Dbg("research refused: unreadable body (" + err + ")");
                error = "STR_OZ_ERR_INTERNAL";
                return "";
            }
            string why;
            if (!OZL_Tree.Start(player, owner, req.NodeId, why))
            {
                error = why;
                return "";
            }
            // Удача -- свіже дерево: статуси й пул змінились у той самий момент.
            ok = true;
            error = "";
            return OZL_Tree.ViewJson(owner, uid);
        }

        return "";
    }
}
