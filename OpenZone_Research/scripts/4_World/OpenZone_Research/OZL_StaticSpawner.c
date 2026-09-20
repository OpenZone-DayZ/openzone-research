// Спавнер стаціонарних станцій: записи з OZ_Research_Statics.json, дедуп по
// OZ_Research_Statics_State.json.
//
// Статик спавниться один раз і далі живе в хайві. Дедуп не через реєстр живих
// об'єктів: сховище сутностей вантажиться після старту місії, і на буті
// реєстр порожній -- тому персистентний список SpawnedIds. Файл стану
// читається САМОСТІЙНО, а не завантажувачем ядра: той на битому файлі
// винесе його в карантин і дасть порожній список, тобто заспавнить усе
// вдруге. Битий стан -- автоспавн стоїть, ERROR у лог, файл на місці.

class OZL_StaticSpawner
{
    private static ref OZL_StaticsState s_State;
    private static bool s_Broken = false;

    static bool Ready()
    {
        return s_State != null;
    }

    private static bool LoadState()
    {
        s_State = null;
        s_Broken = false;
        OZL_StaticsState st = new OZL_StaticsState();
        string path = OZL_Const.STATICS_STATE;
        if (FileExist(path))
        {
            string err;
            if (!JsonFileLoader<OZL_StaticsState>.LoadFile(path, st, err))
            {
                s_Broken = true;
                OZL_Log.Error("statics: the state file " + path + " is unreadable (" + err + ") - auto-spawn is off, fix or delete the file");
                return false;
            }
        }
        else
        {
            st.LoadDefaults();
        }
        s_State = st;
        return true;
    }

    private static void SaveState()
    {
        if (!s_State)
            return;
        OZ_ConfigLoader<OZL_StaticsState>.Save(OZL_Const.STATICS_STATE, "research statics state", s_State, true);
    }

    // Старт місії: спавнимо лише записи, яких ще немає у стані.
    static void SpawnAll()
    {
        if (!LoadState())
            return;
        OZL_StaticsConfig cfg = OZL_Config.Get().Statics();
        int spawned = 0;
        int skipped = 0;
        for (int i = 0; i < cfg.Entries.Count(); i++)
        {
            OZL_StaticEntry e = cfg.Entries[i];
            if (!e)
                continue;
            if (s_State.SpawnedIds.Find(e.Id) > -1)
                continue;
            if (SpawnEntry(e))
                spawned++;
            else
                skipped++;
        }
        if (spawned > 0)
            SaveState();
        string line = "statics: entries=" + cfg.Entries.Count().ToString();
        line += " spawned=" + spawned.ToString() + " skipped=" + skipped.ToString();
        OZL_Log.Info(line);
    }

    private static bool SpawnEntry(OZL_StaticEntry e)
    {
        if (!OZL_Match.ClassExists(e.ClassName))
        {
            OZL_Log.Warn("statics '" + e.Id + "': unknown class '" + e.ClassName + "', skipped");
            return false;
        }
        vector pos = Vector(e.Pos[0], e.Pos[1], e.Pos[2]);
        // Поруч уже стоїть такий самий (сховище встигло завантажитись, або
        // адмін поставив руками) -- не дублюємо, а лише позначаємо.
        if (OZL_StaticStation.FindNear(e.ClassName, pos, 1.0))
        {
            OZL_Log.Warn("statics '" + e.Id + "': a " + e.ClassName + " already stands there, marked as spawned");
            s_State.SpawnedIds.Insert(e.Id);
            return false;
        }

        Object obj = GetGame().CreateObjectEx(e.ClassName, pos, ECE_PLACE_ON_SURFACE | ECE_CREATEPHYSICS | ECE_NOLIFETIME);
        if (!obj)
        {
            OZL_Log.Error("statics '" + e.Id + "': CreateObjectEx returned null for '" + e.ClassName + "'");
            return false;
        }
        // Лише наші статики: Land_*/House не персистяться, звичайні предмети
        // беруться в руки й невидимі дедупу.
        if (!OZL_StaticStation.Cast(obj))
        {
            GetGame().ObjectDelete(obj);
            OZL_Log.Error("statics '" + e.Id + "': '" + e.ClassName + "' is not a static station of this mod, spawn cancelled");
            return false;
        }
        obj.SetOrientation(Vector(e.Yaw, 0, 0));
        s_State.SpawnedIds.Insert(e.Id);

        // Фактична позиція, а не запрошена: «прилад пішов у землю» має бути
        // видно в лозі.
        vector actual = obj.GetPosition();
        string where = actual.ToString();
        if (vector.Distance(actual, pos) > 0.01)
            where += " (asked " + pos.ToString() + ")";
        OZL_Log.Info("statics '" + e.Id + "' (" + e.ClassName + ") spawned at " + where);
        return true;
    }

    // Зняти позначку й заспавнити заново -- після ручного видалення приладу.
    // Для адмінського розділу.
    static bool Respawn(string id, out string why)
    {
        why = "";
        if (!s_State)
        {
            why = "STR_OZL_ERR_STATICS_OFF";
            return false;
        }
        OZL_StaticsConfig cfg = OZL_Config.Get().Statics();
        OZL_StaticEntry found;
        for (int i = 0; i < cfg.Entries.Count(); i++)
        {
            if (cfg.Entries[i] && cfg.Entries[i].Id == id)
                found = cfg.Entries[i];
        }
        if (!found)
        {
            why = "STR_OZL_ERR_NO_STATIC";
            return false;
        }
        // Стоїть -- значить, видаляти не було чого: окрема відмова, бо
        // «спавн не вдався» посилає адміна шукати в лозі те, чого там немає.
        vector pos = Vector(found.Pos[0], found.Pos[1], found.Pos[2]);
        if (OZL_StaticStation.FindNear(found.ClassName, pos, 1.0))
        {
            if (s_State.SpawnedIds.Find(id) < 0)
            {
                s_State.SpawnedIds.Insert(id);
                SaveState();
            }
            why = "STR_OZL_ERR_STATIC_STANDS";
            return false;
        }
        int idx = s_State.SpawnedIds.Find(id);
        if (idx > -1)
            s_State.SpawnedIds.RemoveOrdered(idx);
        bool ok = SpawnEntry(found);
        SaveState();
        if (!ok)
        {
            why = "STR_OZL_ERR_SPAWN_FAILED";
            return false;
        }
        return true;
    }

    // Рядок для адмінського списку: id=клас [spawned|pending].
    static string Describe()
    {
        if (s_Broken)
            return "state file broken, auto-spawn off";
        OZL_StaticsConfig cfg = OZL_Config.Get().Statics();
        if (cfg.Entries.Count() == 0)
            return "no entries";
        string s = "";
        for (int i = 0; i < cfg.Entries.Count(); i++)
        {
            OZL_StaticEntry e = cfg.Entries[i];
            if (!e)
                continue;
            string flag = "pending";
            if (s_State && s_State.SpawnedIds.Find(e.Id) > -1)
                flag = "spawned";
            if (s != "")
                s += " ";
            s += e.Id + "=" + e.ClassName + "[" + flag + "]";
        }
        return s;
    }
}
