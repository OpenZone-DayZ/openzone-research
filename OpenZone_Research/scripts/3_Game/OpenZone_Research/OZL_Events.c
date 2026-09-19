// Події мода -- інвокери, на які підписуються сусідні одиниці.
//
// Станція з правилом «потрібен вузол» слухає завершення вузлів; сброс фракції
// зупиняє її станції. Інвокер, а не прямий виклик: той, хто завершує вузол,
// не мусить знати, кому це цікаво.

class OZL_Events
{
    // (string owner, string nodeId)
    static ref ScriptInvoker OnNodeCompleted = new ScriptInvoker();

    // (string owner)
    static ref ScriptInvoker OnOwnerReset = new ScriptInvoker();
}
