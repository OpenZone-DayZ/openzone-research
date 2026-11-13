// Редактор досліджень у вікні OpenZone: сім конфігів як ЧЕРНЕТКИ клієнта.
//
// Сервер віддає файл текстом (cfg_get ядра), редактор розбирає його у свій
// об'єкт, правки йдуть у той об'єкт, і лише ЗАСТОСУВАТИ шле файл назад
// (cfg_set) -- тим самим шляхом, що й сирий редактор ядра: розбір, Stale,
// Validate, бекап, живий підмін на сервері (OZL_Config.c).
//
// Чернетка тримається компактним JSON-рядком: з нього ж знімки для
// скасування (кілька кілобайт на знімок, і жодних глибоких копій), і ним же
// файл їде на сервер -- 256 КБ на потік у ядра, правила стиснуті ~98 КБ.
//
// Дизайн: docs/specs/2026-11-09-research-editor-vpp-design.md, §3-§4.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

// Сім типів, а шаблон Enforce не вміє `new T()` (шапка OZL_Config.c), тож
// по гілці на тег -- як у застосувачах сервера.
class OZL_EdCodec
{
    // Текст -> об'єкт, який збудував СКРИПТ: те, що виділив серіалізатор,
    // живе лише до розбору (шапка OZ_ConfigBase ядра), і вкладені поля без
    // ініціалізаторів Copy() теж лагодить.
    //
    // Файл старшої версії переводиться тут же, як це робить завантажувач
    // ядра: сервер приймає правку лише в найновішій версії (OZL_Config.Stale),
    // і без цього правка такого файла поверталась би відмовою.
    static OZ_ConfigBase Parse(string tag, string json, out string err)
    {
        if (tag == OZL_Config.TAG_SETTINGS)
        {
            OZL_Settings s = new OZL_Settings();
            if (!JsonFileLoader<OZL_Settings>.LoadData(json, s, err) || !Current(s, err))
                return null;
            return s.Copy();
        }
        if (tag == OZL_Config.TAG_POINT_TYPES)
        {
            OZL_PointTypes pt = new OZL_PointTypes();
            if (!JsonFileLoader<OZL_PointTypes>.LoadData(json, pt, err) || !Current(pt, err))
                return null;
            return pt.Copy();
        }
        if (tag == OZL_Config.TAG_OWNERS)
        {
            OZL_Owners ow = new OZL_Owners();
            if (!JsonFileLoader<OZL_Owners>.LoadData(json, ow, err) || !Current(ow, err))
                return null;
            return ow.Copy();
        }
        if (tag == OZL_Config.TAG_RULES)
        {
            OZL_Rules ru = new OZL_Rules();
            if (!JsonFileLoader<OZL_Rules>.LoadData(json, ru, err) || !Current(ru, err))
                return null;
            return ru.Copy();
        }
        if (tag == OZL_Config.TAG_TREE)
        {
            OZL_TreeConfig tr = new OZL_TreeConfig();
            if (!JsonFileLoader<OZL_TreeConfig>.LoadData(json, tr, err) || !Current(tr, err))
                return null;
            return tr.Copy();
        }
        if (tag == OZL_Config.TAG_MODULES)
        {
            OZL_Modules mo = new OZL_Modules();
            if (!JsonFileLoader<OZL_Modules>.LoadData(json, mo, err) || !Current(mo, err))
                return null;
            return mo.Copy();
        }
        if (tag == OZL_Config.TAG_STATICS)
        {
            OZL_StaticsConfig st = new OZL_StaticsConfig();
            if (!JsonFileLoader<OZL_StaticsConfig>.LoadData(json, st, err) || !Current(st, err))
                return null;
            return st.Copy();
        }
        err = "unknown config " + tag;
        return null;
    }

    // Версія файла -> найновіша, або відмова з причиною.
    protected static bool Current(OZ_ConfigBase c, out string err)
    {
        int from = c.Version;
        if (from == c.LatestVersion())
            return true;
        if (from > c.LatestVersion() || !c.Migrate(from))
        {
            err = "version " + from.ToString() + ", this build reads " + c.LatestVersion().ToString();
            return false;
        }
        return true;
    }

    // Об'єкт -> компактний JSON: так файл їде на сервер і так лежать знімки.
    static string Write(string tag, OZ_ConfigBase c)
    {
        string txt = "";
        string err;
        if (!c)
            return txt;
        if (tag == OZL_Config.TAG_SETTINGS)
            JsonFileLoader<OZL_Settings>.MakeData(OZL_Settings.Cast(c), txt, err, false);
        else if (tag == OZL_Config.TAG_POINT_TYPES)
            JsonFileLoader<OZL_PointTypes>.MakeData(OZL_PointTypes.Cast(c), txt, err, false);
        else if (tag == OZL_Config.TAG_OWNERS)
            JsonFileLoader<OZL_Owners>.MakeData(OZL_Owners.Cast(c), txt, err, false);
        else if (tag == OZL_Config.TAG_RULES)
            JsonFileLoader<OZL_Rules>.MakeData(OZL_Rules.Cast(c), txt, err, false);
        else if (tag == OZL_Config.TAG_TREE)
            JsonFileLoader<OZL_TreeConfig>.MakeData(OZL_TreeConfig.Cast(c), txt, err, false);
        else if (tag == OZL_Config.TAG_MODULES)
            JsonFileLoader<OZL_Modules>.MakeData(OZL_Modules.Cast(c), txt, err, false);
        else if (tag == OZL_Config.TAG_STATICS)
            JsonFileLoader<OZL_StaticsConfig>.MakeData(OZL_StaticsConfig.Cast(c), txt, err, false);
        return txt;
    }

    // Знахідка перевірок -- ПОМИЛКА, коли сервер викине чи вимкне те, що
    // написано (dropped, disabled, unreachable, невідомий тип балів): таке
    // ЗАСТОСУВАТИ не шле. Решта -- попередження: сервер підправить сам
    // (cleared, using ...), або це перевірка класу, а клієнт не знає класів
    // модів, що стоять лише на сервері (§4 спеки: такий клас -- ніколи не
    // помилка).
    static bool IsError(string msg)
    {
        if (msg.IndexOf("unknown point type") > -1)
            return true;
        if (msg.IndexOf("unknown ") > -1 || msg.IndexOf("not a line module") > -1)
            return false;
        if (msg.IndexOf(" dropped") > -1 || msg.IndexOf(" disabled") > -1)
            return true;
        if (msg.IndexOf("unreachable") > -1)
            return true;
        return false;
    }
}

class OZL_EdDoc
{
    string Tag;

    // Компактний текст файла сервера, ПЕРЕПИСАНИЙ нами: інакше відступи
    // вихідного файла рахувались би зміною ще до першої правки.
    string Base = "";

    // Компактний текст чернетки.
    string Cur = "";

    bool Loaded = false;

    // Розібраний Cur. Вигляди правлять його й кличуть OZL_EdDocs.Commit.
    ref OZ_ConfigBase Obj;

    void OZL_EdDoc(string tag)
    {
        Tag = tag;
    }

    bool Dirty()
    {
        return Loaded && Cur != Base;
    }
}

// Знімок для скасування: який файл і яким він був.
class OZL_EdSnap
{
    string Tag;
    string Json;

    void OZL_EdSnap(string tag, string json)
    {
        Tag  = tag;
        Json = json;
    }
}

class OZL_EdDocs
{
    static const int UNDO_MAX = 200;

    protected ref map<string, ref OZL_EdDoc> m_Docs;

    // ПОРЯДОК ЗАСТОСУВАННЯ (§4 спеки): Check на сервері звіряє правила й
    // дерево з тим, що вже живе, тож типи балів ідуть першими, власники й
    // модулі -- до правил і дерева.
    protected ref array<string> m_Order;

    protected ref array<ref OZL_EdSnap> m_Undo;
    protected ref array<ref OZL_EdSnap> m_Redo;

    // Ключ поточного «жесту» правки: знімок робиться раз на жест, а не на
    // кожну літеру в полі (BeginOnce).
    protected string m_GestureKey = "";

    protected ref array<string> m_Problems;
    protected int m_Errors = 0;
    protected int m_Warnings = 0;

    // Застосування: файли в черзі й той, що в польоті.
    protected ref array<string> m_ApplyQ;
    protected ref array<string> m_Applied;
    protected string m_Applying = "";

    void OZL_EdDocs()
    {
        m_Docs     = new map<string, ref OZL_EdDoc>();
        m_Order    = new array<string>();
        m_Undo     = new array<ref OZL_EdSnap>();
        m_Redo     = new array<ref OZL_EdSnap>();
        m_Problems = new array<string>();
        m_ApplyQ   = new array<string>();
        m_Applied  = new array<string>();

        m_Order.Insert(OZL_Config.TAG_POINT_TYPES);
        m_Order.Insert(OZL_Config.TAG_OWNERS);
        m_Order.Insert(OZL_Config.TAG_MODULES);
        m_Order.Insert(OZL_Config.TAG_SETTINGS);
        m_Order.Insert(OZL_Config.TAG_TREE);
        m_Order.Insert(OZL_Config.TAG_RULES);
        m_Order.Insert(OZL_Config.TAG_STATICS);

        for (int i = 0; i < m_Order.Count(); i++)
            m_Docs.Set(m_Order[i], new OZL_EdDoc(m_Order[i]));
    }

    array<string> Tags()
    {
        return m_Order;
    }

    bool Owns(string tag)
    {
        return m_Docs.Contains(tag);
    }

    OZL_EdDoc Doc(string tag)
    {
        return m_Docs.Get(tag);
    }

    int LoadedCount()
    {
        int n = 0;
        for (int i = 0; i < m_Order.Count(); i++)
        {
            if (m_Docs.Get(m_Order[i]).Loaded)
                n++;
        }
        return n;
    }

    bool AllLoaded()
    {
        return LoadedCount() == m_Order.Count();
    }

    // Файл прийшов із сервера. Чернетка без правок бере його цілком; з
    // правками -- лишає свої, а міняється лише Base: зміна рахується від
    // того, що тепер лежить на сервері.
    bool OnFetched(string tag, string body, out string err)
    {
        OZL_EdDoc d = m_Docs.Get(tag);
        if (!d)
        {
            err = "not a research config";
            return false;
        }

        OZ_ConfigBase c = OZL_EdCodec.Parse(tag, body, err);
        if (!c)
            return false;

        string norm = OZL_EdCodec.Write(tag, c);
        bool keep = d.Dirty();
        d.Base   = norm;
        d.Loaded = true;
        if (!keep)
        {
            d.Cur = norm;
            d.Obj = c;
        }
        Recheck();
        return true;
    }

    // Перед правкою: знімок файла в стек скасування, раз на жест. Інший ключ
    // -- інший жест (інше поле чи інший рядок списку).
    void BeginOnce(string tag, string key)
    {
        if (key != "" && key == m_GestureKey)
            return;
        m_GestureKey = key;

        OZL_EdDoc d = m_Docs.Get(tag);
        if (!d || !d.Loaded)
            return;

        m_Undo.Insert(new OZL_EdSnap(tag, d.Cur));
        if (m_Undo.Count() > UNDO_MAX)
            m_Undo.RemoveOrdered(0);
        m_Redo.Clear();
    }

    // Наступна правка -- новий жест, навіть у тому самому полі.
    void EndGesture()
    {
        m_GestureKey = "";
    }

    // Після правки: Obj -> Cur, перевірка всього.
    void Commit(string tag)
    {
        OZL_EdDoc d = m_Docs.Get(tag);
        if (!d || !d.Obj)
            return;
        d.Cur = OZL_EdCodec.Write(tag, d.Obj);
        Recheck();
    }

    bool CanUndo()
    {
        return m_Undo.Count() > 0;
    }

    bool CanRedo()
    {
        return m_Redo.Count() > 0;
    }

    // Знімок -> чернетка; що було, іде в протилежний стек.
    protected bool Swap(array<ref OZL_EdSnap> from, array<ref OZL_EdSnap> to, out string tag)
    {
        m_GestureKey = "";
        if (from.Count() == 0)
            return false;

        OZL_EdSnap s = from[from.Count() - 1];
        from.Remove(from.Count() - 1);

        OZL_EdDoc d = m_Docs.Get(s.Tag);
        if (!d)
            return false;

        string err;
        OZ_ConfigBase c = OZL_EdCodec.Parse(s.Tag, s.Json, err);
        if (!c)
            return false;

        to.Insert(new OZL_EdSnap(s.Tag, d.Cur));
        d.Cur = s.Json;
        d.Obj = c;
        tag = s.Tag;
        Recheck();
        return true;
    }

    bool Undo(out string tag)
    {
        return Swap(m_Undo, m_Redo, tag);
    }

    bool Redo(out string tag)
    {
        return Swap(m_Redo, m_Undo, tag);
    }

    // Чернетки -> файли сервера, стеки порожні.
    void Discard()
    {
        m_GestureKey = "";
        m_Undo.Clear();
        m_Redo.Clear();
        for (int i = 0; i < m_Order.Count(); i++)
        {
            OZL_EdDoc d = m_Docs.Get(m_Order[i]);
            if (!d.Loaded || !d.Dirty())
                continue;
            string err;
            OZ_ConfigBase c = OZL_EdCodec.Parse(d.Tag, d.Base, err);
            if (!c)
                continue;
            d.Cur = d.Base;
            d.Obj = c;
        }
        Recheck();
    }

    int Changed()
    {
        int n = 0;
        for (int i = 0; i < m_Order.Count(); i++)
        {
            if (m_Docs.Get(m_Order[i]).Dirty())
                n++;
        }
        return n;
    }

    // ------------------------------------------------- перевірка

    array<string> Problems()
    {
        return m_Problems;
    }

    int Errors()
    {
        return m_Errors;
    }

    int Warnings()
    {
        return m_Warnings;
    }

    // Те, що сервер зробить на завантаженні (OZL_Config.LoadAll/CheckAll):
    // Validate кожного файла, потім правила й дерево проти типів балів і
    // модулі проти гри. На КОПІЯХ -- вони викидають і вимикають -- і під
    // збирачем OZL_Log, тож знахідки стають списком, а не рядками в лозі.
    void Recheck()
    {
        m_Problems.Clear();
        m_Errors = 0;
        m_Warnings = 0;
        if (!AllLoaded())
            return;

        OZL_PointTypes pt = OZL_PointTypes.Cast(Doc(OZL_Config.TAG_POINT_TYPES).Obj).Copy();
        OZL_Owners     ow = OZL_Owners.Cast(Doc(OZL_Config.TAG_OWNERS).Obj).Copy();
        OZL_Rules      ru = OZL_Rules.Cast(Doc(OZL_Config.TAG_RULES).Obj).Copy();
        OZL_TreeConfig tr = OZL_TreeConfig.Cast(Doc(OZL_Config.TAG_TREE).Obj).Copy();
        OZL_Modules    mo = OZL_Modules.Cast(Doc(OZL_Config.TAG_MODULES).Obj).Copy();
        OZL_Settings   se = OZL_Settings.Cast(Doc(OZL_Config.TAG_SETTINGS).Obj).Copy();
        OZL_StaticsConfig st = OZL_StaticsConfig.Cast(Doc(OZL_Config.TAG_STATICS).Obj).Copy();

        int n;
        OZL_Log.CaptureBegin(m_Problems);
        se.Validate(n);
        pt.Validate(n);
        ow.Validate(n);
        tr.Validate(n);
        ru.Validate(n);
        mo.Validate(n);
        st.Validate(n);
        ru.Check(pt, n);
        tr.Check(pt, n);
        mo.Check(n);
        OZL_Log.CaptureEnd();

        for (int i = 0; i < m_Problems.Count(); i++)
        {
            if (OZL_EdCodec.IsError(m_Problems[i]))
                m_Errors++;
            else
                m_Warnings++;
        }
    }

    // ------------------------------------------------- застосування

    // Черга змінених файлів у порядку m_Order. Порожньо -- нема чого.
    int ApplyStart()
    {
        m_ApplyQ.Clear();
        m_Applied.Clear();
        m_Applying = "";
        for (int i = 0; i < m_Order.Count(); i++)
        {
            if (m_Docs.Get(m_Order[i]).Dirty())
                m_ApplyQ.Insert(m_Order[i]);
        }
        return m_ApplyQ.Count();
    }

    bool Applying()
    {
        return m_Applying != "";
    }

    string InFlight()
    {
        return m_Applying;
    }

    // Наступний файл у політ; порожньо -- черга скінчилась.
    string ApplyNext()
    {
        m_Applying = "";
        if (m_ApplyQ.Count() == 0)
            return "";
        m_Applying = m_ApplyQ[0];
        // RemoveOrdered: Remove() fills the hole with the LAST entry, which applied three
        // or more changed files out of their declared order.
        m_ApplyQ.RemoveOrdered(0);
        return m_Applying;
    }

    // Сервер прийняв файл: він тепер Base. Відмова -- черга стоїть, решта
    // лишається чернеткою, і стеки цілі: правку можна виправити й слати ще.
    void ApplyDone(string tag, bool ok)
    {
        if (tag != m_Applying)
            return;
        if (!ok)
        {
            m_ApplyQ.Clear();
            m_Applying = "";
            return;
        }
        OZL_EdDoc d = m_Docs.Get(tag);
        if (d)
            d.Base = d.Cur;
        m_Applied.Insert(tag);
        m_Applying = "";
    }

    array<string> Applied()
    {
        return m_Applied;
    }

    // Після ЗАСТОСУВАТИ стеки порожні: знімки до застосованого файла вже не
    // відкочують нічого на сервері, а лише заплутують.
    void ClearHistory()
    {
        m_GestureKey = "";
        m_Undo.Clear();
        m_Redo.Clear();
    }
}

#endif
#endif
#endif
