// Рід `research` у мостовому клієнті ядра: підписка, три листи вгору,
// команди вниз, повтор boot, поки міст не відповість.
//
// Повтор boot -- з подвоєнням паузи (5 с ... 5 хв), а не раз на п'ять
// секунд: кожен невдалий переліт перемикає в ядрі засув «міст відповідає»,
// і міст без роду research коштував би два рядки ядра кожні п'ять секунд
// (зміряно 2026-09-20: WARNING «failed, code 5» плюс «answering again»).
// Міст, який знає рід, сам просить boot елементом опиту {op:"hello"}
// після свого рестарту -- тоді пауза скидається і лист іде негайно.
//
// Ядро возить конверти й не заглядає всередину; кому вони адресовані,
// вирішує підписка за іменем роду. Дороги оголошені нейтральними: дорога,
// не названа ані читальною, ані нейтральною, скидає кеш читання всіх модів.
// Секрет моста -- єдине повноваження команд, як і в ящиків: OZ_Perm.IsAdmin
// тут не бере участі.

class OZL_BridgeSink : OZ_BridgeSink
{
    override void Neutral(array<string> routes)
    {
        routes.Insert(OZL_Const.ROUTE_BOOT);
        routes.Insert(OZL_Const.ROUTE_CHANGED);
        routes.Insert(OZL_Const.ROUTE_RESULT);
    }

    override void Deliver(string json)
    {
        OZL_BridgeCommands.Run(json);
    }
}

// Дорога «вистрілив і забув»: рядка варта лише відмова.
class OZL_AckReply : OZ_BridgeReply
{
    protected string m_What;

    void OZL_AckReply(string what)
    {
        m_What = what;
    }

    override void OnBody(string json)
    {
        OZL_BridgeAnswer a = new OZL_BridgeAnswer();
        string err;
        if (JsonFileLoader<OZL_BridgeAnswer>.LoadData(json, a, err) && a && !a.ok)
            OZL_Log.Warn("bridge refused " + m_What + ": " + a.why);
    }

    override void OnFail(int code)
    {
        OZL_Log.Warn("bridge did not answer " + m_What + " (code " + code.ToString() + ")");
    }
}

class OZL_BootReply : OZ_BridgeReply
{
    override void OnBody(string json)
    {
        OZL_BridgeAnswer a = new OZL_BridgeAnswer();
        string err;
        if (!JsonFileLoader<OZL_BridgeAnswer>.LoadData(json, a, err) || !a)
        {
            OZL_Bridge.Get().OnBootFail("unreadable answer: " + err);
            return;
        }
        if (!a.ok)
        {
            OZL_Bridge.Get().OnBootFail(a.why);
            return;
        }
        OZL_Bridge.Get().OnBootOk();
    }

    override void OnFail(int code)
    {
        OZL_Bridge.Get().OnBootFail("code " + code.ToString());
    }
}

class OZL_Bridge
{
    static const int BOOT_RETRY_MS     = 5000;
    static const int BOOT_RETRY_MAX_MS = 300000;

    private static ref OZL_Bridge s_Inst;
    private static ref OZL_BridgeSink s_Sink;

    private bool   m_Booted   = false;
    private bool   m_Retrying = false;
    private string m_LastFail = "";
    private int    m_Letters  = 0;
    private int    m_Answered = 0;
    private string m_LastToken = "";
    private int    m_RetryMs  = BOOT_RETRY_MS;

    static OZL_Bridge Get()
    {
        if (!s_Inst)
            s_Inst = new OZL_Bridge();
        return s_Inst;
    }

    // До Start() ядра: воно відкладає старт на тік саме заради підписок.
    static void Subscribe()
    {
        if (s_Sink)
            return;
        s_Sink = new OZL_BridgeSink();
        OZ_BridgeClient.Subscribe(OZL_Const.BRIDGE_KIND, s_Sink);
    }

    static bool Enabled()
    {
        return OZ_Settings.Get().Bridge.Enabled;
    }

    // Міст відповідав протягом останньої хвилини.
    static bool Up()
    {
        return OZ_BridgeClient.Alive();
    }

    static bool Post(string route, string letter, OZ_BridgeReply reply)
    {
        if (!Up())
        {
            if (reply)
                reply.OnFail(0);
            return false;
        }
        OZ_BridgeClient.Call(route, letter, reply);
        Get().m_Letters++;
        return true;
    }

    // ---------- boot ----------

    // Лист після старту: ревізія, лічильники, теги конфігів. Перелік класів
    // сервера тепер пише ядро (OZ_ClassDump), міст читає його сам.
    // Міст сам читає конфіги з профілю й переотправляє невідповідані команди.
    void Boot()
    {
        if (!Enabled())
            return;
        OZL_BootLetter l = new OZL_BootLetter();
        l.Revision   = OZL_Config.Get().Revision();
        l.Counters   = OZL_Config.Get().Counters();
        OZL_Config.Tags(l.Names);

        string json;
        string err;
        if (!JsonFileLoader<OZL_BootLetter>.MakeData(l, json, err, false))
        {
            OZL_Log.Error("bridge: boot letter cannot be made: " + err);
            return;
        }
        if (!Post(OZL_Const.ROUTE_BOOT, json, new OZL_BootReply()))
            OnBootFail("bridge client not up yet");
    }

    void OnBootOk()
    {
        m_Booted = true;
        m_Retrying = false;
        m_RetryMs = BOOT_RETRY_MS;
        m_LastFail = "";
        OZL_Log.Info("bridge: boot accepted, revision " + OZL_Config.Get().Revision().ToString());
    }

    // Один рядок на зміну причини, не на кожен повтор; пауза подвоюється
    // до п'яти хвилин (див. шапку файла).
    void OnBootFail(string why)
    {
        if (why != m_LastFail)
        {
            OZL_Log.Info("bridge: boot refused (" + why + "), retrying with a pause of " + (m_RetryMs / 1000).ToString() + " s doubling up to " + (BOOT_RETRY_MAX_MS / 1000).ToString() + " s");
            m_LastFail = why;
        }
        if (m_Retrying)
            return;
        m_Retrying = true;
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(BootRetry, m_RetryMs, false);
        m_RetryMs = m_RetryMs * 2;
        if (m_RetryMs > BOOT_RETRY_MAX_MS)
            m_RetryMs = BOOT_RETRY_MAX_MS;
    }

    // Міст попросив boot (після свого рестарту або першого знайомства з
    // родом): забути невдачі й написати негайно.
    void Hello()
    {
        Stop();
        m_Booted = false;
        m_RetryMs = BOOT_RETRY_MS;
        m_LastFail = "";
        OZL_Log.Info("bridge: hello from the bridge, sending boot");
        Boot();
    }

    void BootRetry()
    {
        m_Retrying = false;
        if (!m_Booted)
            Boot();
    }

    void Stop()
    {
        if (GetGame())
            GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(BootRetry);
        m_Retrying = false;
    }

    // ---------- changed / result ----------

    static void Changed(string tag, string by)
    {
        if (!Enabled())
            return;
        OZL_ChangedLetter l = new OZL_ChangedLetter();
        l.Name     = tag;
        l.Revision = OZL_Config.Get().Revision();
        l.By       = by;
        string json;
        string err;
        if (!JsonFileLoader<OZL_ChangedLetter>.MakeData(l, json, err, false))
            return;
        Post(OZL_Const.ROUTE_CHANGED, json, new OZL_AckReply("changed " + tag));
    }

    static void Result(string token, bool ok, string why, string note)
    {
        OZL_ResultLetter l = new OZL_ResultLetter();
        l.Token    = token;
        l.Ok       = ok;
        l.Why      = why;
        l.Note     = note;
        l.Counters = OZL_Config.Get().Counters();
        string json;
        string err;
        if (!JsonFileLoader<OZL_ResultLetter>.MakeData(l, json, err, false))
            return;
        Get().m_Answered++;
        Get().m_LastToken = token;
        Post(OZL_Const.ROUTE_RESULT, json, new OZL_AckReply("result " + token));
    }

    // Для стендового verb і адмінського списку.
    static string Describe()
    {
        OZL_Bridge b = Get();
        string s = "enabled=" + Enabled().ToString() + " up=" + Up().ToString();
        s += " booted=" + b.m_Booted.ToString();
        s += " letters=" + b.m_Letters.ToString();
        s += " answered=" + b.m_Answered.ToString();
        if (b.m_LastToken != "")
            s += " last=" + b.m_LastToken;
        if (b.m_LastFail != "")
            s += " lastFail=" + b.m_LastFail;
        return s;
    }
}
