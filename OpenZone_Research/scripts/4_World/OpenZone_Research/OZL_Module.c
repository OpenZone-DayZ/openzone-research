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
    private static const float READY_DELAY = 1.0;

    // Кличеться таймером на ім'я -- метод мусить бути видимим (не private).
    void Ready()
    {
        OZL_Log.Info(ReadyLine());
    }

    override void OnMissionFinish(Class sender, CF_EventArgs args)
    {
        super.OnMissionFinish(sender, args);

        if (m_ReadyTimer)
            m_ReadyTimer.Stop();
    }

    // РЯДОК ЗБИРАЄМО ПООПЕРАТОРНО, а не одним ланцюжком «+»: компілятор
    // Enforce має межу складності виразу й падає з «Formula too complex» --
    // у ZP_Research це знайшли на восьмому доданку.
    static string ReadyLine()
    {
        string s = "research loaded: owners=0 pointTypes=0 rules=0 nodes=0";
        s += " dataItems=0 modules=0 sampleTypes=0 statics=0";

        // Чи стоїть мод фракцій: без нього кожен гравець -- типовий власник, і
        // адмін мусить бачити це тут, а не шукати, чому в усіх одне дерево.
        if (OZ_Identity.Present())
            s += " identity=present";
        else
            s += " identity=absent";
        return s;
    }
}
