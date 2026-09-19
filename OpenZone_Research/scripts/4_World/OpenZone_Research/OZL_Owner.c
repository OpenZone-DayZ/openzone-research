// Хто власник пулу й дерева для цього гравця -- єдине місце, де мод питає
// фракцію.
//
// Дві осі ядра (ТЗ-1 §2): угруповання, якщо гравець у ньому стоїть, інакше
// базова фракція. У Долгу своє дерево, в одинака -- дерево сталкерів, у
// бандита -- дерево бандитів. Коли ядро не знає гравця зовсім (не заходив,
// або мода фракцій немає), власник -- типовий із налаштувань.
//
// Нашивки, хук на слот і досинхронізація через чотири секунди пішли разом із
// власним визначенням фракції: ядро відповідає в будь-яку мить.

class OZL_Owner
{
    static string Of(string uid)
    {
        if (uid == "")
            return Fallback();

        OZ_IdentityService id = OZ_Identity.Get();
        string org = id.OrgOf(uid);
        if (org != "")
            return org;

        string base = id.BaseOf(uid);
        if (base != "")
            return base;

        return Fallback();
    }

    // Жива сутність дозволяє відповісти й тоді, коли за uid ще нічого не
    // відомо: контракт чужого провайдера (Expansion) віддає угруповання за
    // гравцем.
    static string OfPlayer(PlayerBase p)
    {
        if (!p || !p.GetIdentity())
            return Fallback();

        string uid = p.GetIdentity().GetPlainId();
        string org = OZ_Identity.Get().OrgOfPlayer(p, uid);
        if (org != "")
            return org;

        return Of(uid);
    }

    // Чи стоїть гравець на базовій осі (без угруповання): тоді право тратити
    // дає інший пост.
    static bool IsBaseAxis(string uid)
    {
        return OZ_Identity.Get().OrgOf(uid) == "";
    }

    static string Fallback()
    {
        OZL_Settings s = OZL_Config.Get().Settings();
        if (s)
            return s.DefaultOwner;
        return "loner";
    }
}

// Хто може тратити пул: лідер завжди, далі -- пост із налаштувань. Порожнє
// ім'я поста означає «ніхто, крім лідера» (рішення власника 2026-09-20).
// Класти носії в термінал і запускати станції може будь-який член -- це не
// тут.
class OZL_Access
{
    static bool MaySpend(string uid)
    {
        if (uid == "")
            return false;

        OZ_IdentityService id = OZ_Identity.Get();
        if (id.IsLeader(uid))
            return true;

        OZL_Settings s = OZL_Config.Get().Settings();
        if (!s)
            return false;

        string post = s.ResearchPost;
        if (OZL_Owner.IsBaseAxis(uid))
            post = s.BasePost;

        if (post == "")
            return false;
        return id.HasPost(uid, post);
    }
}
