// Календарні секунди для строків, що переживають рестарт.
//
// GetGame().GetTime() рахує від старту місії, тож дедлайн станції на ньому
// після рестарту або протух би, або став вічним. Ядро дає календар рядком
// (OZ_Time.NowUtc); станціям і проєктам потрібне ЧИСЛО -- відняти,
// порівняти, записати в потік CF. Нуль -- 2020-01-01 00:00:00 UTC, int
// уміщує 68 років.

class OZL_Clock
{
    static int NowSec()
    {
        int y, mo, d, h, mi, s;
        GetYearMonthDayUTC(y, mo, d);
        GetHourMinuteSecondUTC(h, mi, s);

        int days = 0;
        for (int yy = 2020; yy < y; yy++)
        {
            days += 365;
            if (OZ_Time.DaysIn(yy, 2) == 29)
                days += 1;
        }
        for (int mm = 1; mm < mo; mm++)
            days += OZ_Time.DaysIn(y, mm);
        days += d - 1;

        int secs = days * 86400;
        secs += h * 3600;
        secs += mi * 60;
        secs += s;
        return secs;
    }
}
