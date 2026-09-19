// Панель RESEARCH у вкладці OpenZone адмінки VPP.
//
// Приходить із планом T8 (спека серії 2026-09-20-openzone-research-design,
// §13): modded OZ_VppAdminMenu під #ifdef AVPPAdminTools / #ifdef OpenZone_VPP /
// #ifndef NO_GUI, RegisterPane("research", "RESEARCH", ...), операції розділу
// через OZ_Rpc.AdminRequest. До того файл лишається порожнім, щоб модуль
// місії цього pbo мав що компілювати.
