// Команди моста: розбір, виконання, відповідь листом result, пам'ять
// відповіданих токенів.
//
// cfg_apply читає кандидата з теки обміну штатним завантажувачем і
// застосовує його тим самим шляхом, що й редактор VPP (перевірка, бекап,
// підміна живого об'єкта, пересинк). Решта операцій -- ті самі рядки, що
// в адмінському розділі: журнал гри єдиний, лише ім'я -- bridge:<хто>.
// Повтор команди (міст переотправив після свого рестарту) отримує збережену
// відповідь без другого виконання.

class OZL_BridgeCommands
{
    private static const int REMEMBER = 100;

    private static ref array<string> s_Tokens = new array<string>();
    private static ref array<bool>   s_Oks    = new array<bool>();
    private static ref array<string> s_Whys   = new array<string>();
    private static ref array<string> s_Notes  = new array<string>();

    static void Run(string json)
    {
        OZL_BridgeCommand c = new OZL_BridgeCommand();
        string err;
        if (!JsonFileLoader<OZL_BridgeCommand>.LoadData(json, c, err) || !c || c.op == "")
        {
            OZL_Log.Warn("bridge: a research item that is not a command: " + err);
            return;
        }
        // Не команда, а прохання: міст хоче лист boot. Без токена й без
        // листа result -- відповіддю є сам boot.
        if (c.op == "hello")
        {
            OZL_Bridge.Get().Hello();
            return;
        }

        if (c.token == "")
        {
            OZL_Log.Warn("bridge: command '" + c.op + "' without a token, ignored");
            return;
        }

        int at = s_Tokens.Find(c.token);
        if (at > -1)
        {
            OZL_Log.Dbg("bridge: command " + c.token + " repeated, answering again");
            OZL_Bridge.Result(c.token, s_Oks[at], s_Whys[at], s_Notes[at]);
            return;
        }

        string who = "bridge:" + c.by;
        string why = "";
        string note = "";
        bool ok;
        if (c.op == "cfg_apply")
            ok = CfgApply(c, who, why, note);
        else
            ok = Admin(c, who, why, note);

        Remember(c.token, ok, why, note);
        if (ok)
            OZL_Log.Info("bridge: " + c.op + " by " + c.by + " done " + note);
        else
            OZL_Log.Warn("bridge: " + c.op + " by " + c.by + " refused: " + why);
        OZL_Bridge.Result(c.token, ok, why, note);
    }

    private static void Remember(string token, bool ok, string why, string note)
    {
        if (s_Tokens.Count() >= REMEMBER)
        {
            s_Tokens.RemoveOrdered(0);
            s_Oks.RemoveOrdered(0);
            s_Whys.RemoveOrdered(0);
            s_Notes.RemoveOrdered(0);
        }
        s_Tokens.Insert(token);
        s_Oks.Insert(ok);
        s_Whys.Insert(why);
        s_Notes.Insert(note);
    }

    // Ім'я файла кандидата: лише літери, цифри, крапка, підкреслення, дефіс,
    // закінчення .json -- без теки обміну нічого не читається.
    private static bool SafeFile(string file)
    {
        int n = file.Length();
        if (n < 6 || n > 96)
            return false;
        if (file.Substring(n - 5, 5) != ".json")
            return false;
        if (file.IndexOf("..") > -1)
            return false;
        for (int i = 0; i < n; i++)
        {
            int ch = file.Get(i).ToAscii();
            bool digit = ch >= 48 && ch <= 57;
            bool upper = ch >= 65 && ch <= 90;
            bool lower = ch >= 97 && ch <= 122;
            bool punct = ch == 46 || ch == 95 || ch == 45;
            if (!digit && !upper && !lower && !punct)
                return false;
        }
        return true;
    }

    private static bool CfgApply(OZL_BridgeCommand c, string who, out string why, out string note)
    {
        why = "";
        note = "";
        if (!SafeFile(c.file))
        {
            why = "bad candidate file name";
            return false;
        }
        if (!OZ_AdminCfg.Find(c.name))
        {
            why = "unknown config '" + c.name + "'";
            return false;
        }
        string path = OZL_Const.XCHG_DIR + "\\" + c.file;
        int warnings;
        if (!OZL_CfgFile.ApplyFile(c.name, path, who, why, warnings))
            return false;
        DeleteFile(path);
        note = "warnings=" + warnings.ToString() + " problems=" + OZL_Config.Get().Problems().ToString();
        return true;
    }

    private static bool Admin(OZL_BridgeCommand c, string who, out string why, out string note)
    {
        why = "";
        note = "";
        string op = "";
        if (c.op == "reset")
            op = "reset:" + c.owner;
        else if (c.op == "grant")
            op = "grant:" + c.owner + ":" + c.type + ":" + c.amount;
        else if (c.op == "complete")
            op = "complete:" + c.owner + ":" + c.node;
        else if (c.op == "reload")
            op = "reload";
        else if (c.op == "respawn")
            op = "respawn:" + c.id;
        else if (c.op == "list")
            op = "list";
        else
        {
            why = "unknown op '" + c.op + "'";
            return false;
        }

        bool ok;
        string err;
        OZL_Admin.Run(op, who, ok, err);
        if (!ok)
        {
            why = err;
            return false;
        }

        // Після reload міст мусить перечитати всі дев'ять файлів.
        if (c.op == "reload")
        {
            array<string> tags = new array<string>();
            OZL_Config.Tags(tags);
            for (int i = 0; i < tags.Count(); i++)
                OZL_Bridge.Changed(tags[i], who);
        }
        return true;
    }
}
