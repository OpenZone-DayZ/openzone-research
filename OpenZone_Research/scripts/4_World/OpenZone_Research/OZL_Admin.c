// Адмінський розділ `research` у реєстрі ядра: список фракцій із пулами,
// сброс, нарахування, завершення вузла, перечитування конфігів, повторний
// спавн статика.
//
// Права перевірив диспетчер ядра (OZ_Perm.IsAdmin) до розбору операції --
// тут їх не перевіряємо, друге місце перевірки означало б друге місце, де її
// можна забути. Операція з аргументами їде рядком "op:arg:arg", як у ядра
// (wipe:<uid>); тіло порожнє. Кожна вдала операція повертає свіжий список,
// щоб панель перемалювалась одним конвертом. Той самий контракт пізніше
// слухає рід research моста.

class OZL_AdminOwner
{
    string Id        = "";
    string Name      = "";
    string Pool      = "";
    int    Completed = 0;
    int    Active    = 0;
    // 1 -- файл стану є, 0 -- фракція лише в конфігу, стану ще не було.
    int    Known     = 0;
}

class OZL_AdminList
{
    ref array<ref OZL_AdminOwner> Owners;
    string Statics = "";
    string Counters = "";

    void OZL_AdminList()
    {
        Owners = new array<ref OZL_AdminOwner>();
    }
}

class OZL_Admin : OZ_AdminSection
{
    override string Handle(string op, string json, PlayerIdentity sender, out bool ok, out string error)
    {
        string who = "?";
        if (sender)
            who = sender.GetPlainId();
        return Run(op, who, ok, error);
    }

    // Тіло розділу без відправника: той самий рядок операції приходить з
    // панелі VPP, від моста (who = bridge:<хто>) і зі стендового verb.
    static string Run(string op, string who, out bool ok, out string error)
    {
        ok = false;
        error = "STR_OZ_ERR_UNKNOWN_OP";

        array<string> parts = new array<string>();
        op.Split(":", parts);
        if (parts.Count() == 0)
            return "";
        string verb = parts[0];

        if (verb == "list")
        {
            ok = true;
            error = "";
            return ListJson();
        }

        if (verb == "reload")
        {
            OZL_Config.Reload();
            int states = OZL_State.Scan();
            OZL_Log.Info("admin " + who + ": configs reloaded, " + states.ToString() + " owner file(s) read");
            ok = true;
            error = "";
            return ListJson();
        }

        if (verb == "reset")
        {
            if (parts.Count() < 2)
                return "";
            string why;
            if (!OZL_State.Reset(parts[1], why))
            {
                error = why;
                return "";
            }
            OZL_Log.Info("admin " + who + ": owner '" + parts[1] + "' reset");
            ok = true;
            error = "";
            return ListJson();
        }

        if (verb == "grant")
        {
            if (parts.Count() < 4)
                return "";
            string gwhy;
            if (!OZL_Points.Grant(parts[1], parts[2], parts[3].ToInt(), gwhy))
            {
                error = gwhy;
                return "";
            }
            OZL_Log.Info("admin " + who + ": owner '" + parts[1] + "' granted " + parts[3] + " " + parts[2]);
            ok = true;
            error = "";
            return ListJson();
        }

        if (verb == "complete")
        {
            if (parts.Count() < 3)
                return "";
            if (!OZL_Ids.IsPathSafe(parts[1]))
            {
                error = "STR_OZL_ERR_BAD_OWNER";
                return "";
            }
            if (!OZL_Config.Get().Tree().FindNode(parts[2]))
            {
                error = "STR_OZL_ERR_UNKNOWN_NODE";
                return "";
            }
            OZL_Tree.Complete(parts[1], parts[2]);
            OZL_Log.Info("admin " + who + ": owner '" + parts[1] + "' node '" + parts[2] + "' completed");
            ok = true;
            error = "";
            return ListJson();
        }

        if (verb == "respawn")
        {
            if (parts.Count() < 2)
                return "";
            string swhy;
            if (!OZL_StaticSpawner.Respawn(parts[1], swhy))
            {
                error = swhy;
                return "";
            }
            OZL_Log.Info("admin " + who + ": static '" + parts[1] + "' respawned");
            ok = true;
            error = "";
            return ListJson();
        }

        return "";
    }

    // Фракції з конфігу власників і ті, в кого вже є файл стану, разом.
    // Файл для фракції без стану СПИСОК НЕ ЗАВОДИТЬ: він з'явиться від
    // першої дії гравця, а не від погляду адміна.
    static string ListJson()
    {
        OZL_AdminList l = new OZL_AdminList();
        array<string> ids = new array<string>();
        OZL_Owners owners = OZL_Config.Get().Owners();
        int i;
        for (i = 0; i < owners.Owners.Count(); i++)
        {
            if (owners.Owners[i] && ids.Find(owners.Owners[i].Id) < 0)
                ids.Insert(owners.Owners[i].Id);
        }
        array<string> known;
        OZL_State.Owners(known);
        for (i = 0; i < known.Count(); i++)
        {
            if (ids.Find(known[i]) < 0)
                ids.Insert(known[i]);
        }

        OZ_IdentityService id = OZ_Identity.Get();
        for (i = 0; i < ids.Count(); i++)
        {
            OZL_AdminOwner o = new OZL_AdminOwner();
            o.Id   = ids[i];
            o.Name = id.FactionName(ids[i]);
            if (OZL_State.Known(ids[i]))
            {
                OZL_FactionState st = OZL_State.Get(ids[i]);
                if (st)
                {
                    o.Known     = 1;
                    o.Pool      = OZL_Points.Describe(ids[i]);
                    o.Completed = st.CompletedNodes.Count();
                    o.Active    = st.ActiveProjects.Count();
                }
            }
            l.Owners.Insert(o);
        }
        l.Statics  = OZL_StaticSpawner.Describe();
        l.Counters = OZL_Config.Get().Counters();
        return JsonFileLoader<OZL_AdminList>.JsonMakeData(l);
    }
}
