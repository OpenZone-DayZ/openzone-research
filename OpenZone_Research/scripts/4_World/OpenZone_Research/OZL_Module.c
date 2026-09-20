// Серверна половина мода досліджень: порядок старту й рядок готовності.
//
// Порядок значущий: конфіги читаються до стану, стан -- до статиків, а служба
// й розділ реєструються до того, як з'явиться перший клієнт. Рядок готовності
// друкується останнім і у формі `ключ=значення`: вердикт стенда читає
// лічильники саме з нього.

[CF_RegisterModule(OZL_Module)]
class OZL_Module : CF_ModuleWorld
{
    override void OnInit()
    {
        super.OnInit();

        // Спершу super, потім підписки: інакше CF не встигає зареєструвати
        // модуль, і подія приходить у порожнечу.
        EnableMissionStart();
        EnableMissionFinish();
    }

    override void OnMissionStart(Class sender, CF_EventArgs args)
    {
        super.OnMissionStart(sender, args);

        if (!GetGame().IsServer())
            return;

        // Дерево каталогів профілю -- ПЕРШИМ рядком, до будь-якого читання чи
        // запису. Ядро будує його у своєму OnMissionStart, але порядок
        // CF-модулів не гарантований, і на цьому стенді сусіди вже
        // відпрацьовували раніше за ядро. Ідемпотентно.
        OZ_Json.EnsureTree();
        OZ_Json.EnsureDir(OZL_Const.STATE_DIR);

        // Конфіги -- до всього, що їх читає; редактор ядра -- після першого
        // читання, щоб застосувач підміняв живий об'єкт, а не порожнечу.
        OZL_Config.ServerLoad();
        OZL_Config.RegisterEditors();

        // Стан фракцій -- усі файли з теки одразу, а не при першому гравцеві
        // кожної: проєкти офлайнових фракцій мають завершуватись по часу.
        int states = OZL_State.Scan();
        OZL_Log.Info("state: " + states.ToString() + " owner file(s) read");

        // Статики -- після конфігів (їхній список звідти) і стану.
        OZL_StaticSpawner.SpawnAll();

        // Сброс фракції зупиняє її станції: станції не знають про стан, стан
        // не знає про станції, зв'язок -- подія.
        OZL_Events.OnOwnerReset.Insert(OZL_OwnerReset);

        // Служба дерева -- до першого клієнта; проєкти завершуються
        // опитуванням, бо їхній строк живе у файлі, а не в таймері.
        OZ_ServiceRegistry.Register(OZL_Const.SERVICE, new OZL_Service());
        OZ_AdminRegistry.Register(OZL_Const.SECTION, new OZL_Admin());
        m_PollTimer = new Timer(CALL_CATEGORY_SYSTEM);
        m_PollTimer.Run(OZL_Tree.POLL_SEC, this, "OZL_PollProjects", NULL, true);

        // Імена предметів з JSON їдуть клієнтові додатками пакета ядра:
        // ядро кличе цей інвокер на кожну відправку пакета.
        OZ_SyncExtras.OnFill().Insert(OZL_NamesFill);

        // РЯДОК ГОТОВНОСТІ -- ТІКОМ ПІЗНІШЕ, і це не косметика. Порядок
        // CF-модулів не гарантований: на першому буті цей модуль відпрацював
        // раніше за мод фракцій і чесно написав `identity=absent` про службу,
        // яку фракції підставили п'ятнадцятьма рядками нижче. Один тік
        // затримки гарантує, що OnMissionStart відпрацював у всіх (той самий
        // прийом, що в ядра з мостом).
        m_ReadyTimer = new Timer(CALL_CATEGORY_SYSTEM);
        m_ReadyTimer.Run(READY_DELAY, this, "Ready", NULL, false);
    }

    private ref Timer m_ReadyTimer;
    private ref Timer m_PollTimer;
    private static const float READY_DELAY = 1.0;

    // Кличеться таймером на ім'я -- метод мусить бути видимим (не private).
    void Ready()
    {
        OZL_Log.Info(ReadyLine());
    }

    // Кличе таймер на ім'я -- метод мусить бути видимим (не private).
    void OZL_PollProjects()
    {
        OZL_Tree.Poll();
    }
    // Кличе інвокер OZL_Events -- метод мусить бути видимим (не private).
    void OZL_OwnerReset(string owner)
    {
        int n = OZL_Station.CancelAllOf(owner);
        OZL_Log.Info("owner '" + owner + "' reset: " + n.ToString() + " station(s) stopped");
    }
    // Кличе інвокер OZ_SyncExtras -- метод мусить бути видимим (не private).
    void OZL_NamesFill(OZ_SyncPayload p)
    {
        OZL_Config.FillNames(p);
    }

    override void OnMissionFinish(Class sender, CF_EventArgs args)
    {
        super.OnMissionFinish(sender, args);

        if (m_ReadyTimer)
            m_ReadyTimer.Stop();
        if (m_PollTimer)
            m_PollTimer.Stop();

        // Дзеркало підписки: інвокер ядра статичний і переживе місію.
        OZ_SyncExtras.OnFill().Remove(OZL_NamesFill);
        OZL_Events.OnOwnerReset.Remove(OZL_OwnerReset);
    }

    // РЯДОК ЗБИРАЄМО ПООПЕРАТОРНО, а не одним ланцюжком «+»: компілятор
    // Enforce має межу складності виразу й падає з «Formula too complex» --
    // у ZP_Research це знайшли на восьмому доданку.
    static string ReadyLine()
    {
        string s = "research loaded: " + OZL_Config.Get().Counters();

        // Чи стоїть мод фракцій: без нього кожен гравець -- типовий власник, і
        // адмін мусить бачити це тут, а не шукати, чому в усіх одне дерево.
        if (OZ_Identity.Present())
            s += " identity=present";
        else
            s += " identity=absent";
        return s;
    }
}
