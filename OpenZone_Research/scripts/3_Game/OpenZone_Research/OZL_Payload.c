// Рядок у предметі: версія й поля фіксованої ширини шістнадцятковими цифрами.
//
// Проба -- VV PPPP QQ: версія, бали (1..1000), чистота у відсотках (0..200).
// Носій -- VV PPPP: версія, бали. Сирі байти не годяться: Enforce не тримає в
// рядку нульового байта й міряє довжину в байтах. Шістнадцяткові цифри --
// ASCII, тож Length і Substring тут чесні. Рядок читає лише сервер.

class OZL_Payload
{
    static const int    VERSION    = 1;
    static const int    MAX_POINTS = 1000;
    static const int    MAX_PURITY = 200;
    static const string DIGITS     = "0123456789ABCDEF";

    static string EncodeSample(int points, int purityPct)
    {
        return Hex(VERSION, 2) + Hex(points, 4) + Hex(purityPct, 2);
    }

    static bool DecodeSample(string s, out int points, out int purityPct)
    {
        points = 0;
        purityPct = 0;
        if (s.Length() != 8 || Unhex(s.Substring(0, 2)) != VERSION)
            return false;
        int p = Unhex(s.Substring(2, 4));
        int q = Unhex(s.Substring(6, 2));
        if (p < 1 || p > MAX_POINTS || q < 0 || q > MAX_PURITY)
            return false;
        points = p;
        purityPct = q;
        return true;
    }

    static string EncodeCarrier(int points)
    {
        return Hex(VERSION, 2) + Hex(points, 4);
    }

    static bool DecodeCarrier(string s, out int points)
    {
        points = 0;
        if (s.Length() != 6 || Unhex(s.Substring(0, 2)) != VERSION)
            return false;
        int p = Unhex(s.Substring(2, 4));
        if (p < 1 || p > MAX_POINTS)
            return false;
        points = p;
        return true;
    }

    // Чистота -- у цілі відсотки, у межах поля.
    static int PurityPct(float purity)
    {
        int pct = Math.Round(purity * 100.0);
        if (pct < 0)
            return 0;
        if (pct > MAX_PURITY)
            return MAX_PURITY;
        return pct;
    }

    // Рівно `digits` цифр, старша перша.
    static string Hex(int v, int digits)
    {
        string s = "";
        for (int i = 0; i < digits; i++)
        {
            s = DIGITS.Substring(v & 15, 1) + s;
            v = v >> 4;
        }
        return s;
    }

    // -1 на будь-якій чужій цифрі, і на малих літерах теж: пишемо лише великі.
    static int Unhex(string s)
    {
        int v = 0;
        for (int i = 0; i < s.Length(); i++)
        {
            int d = DIGITS.IndexOf(s.Substring(i, 1));
            if (d < 0)
                return -1;
            v = (v << 4) | d;
        }
        return v;
    }
}
