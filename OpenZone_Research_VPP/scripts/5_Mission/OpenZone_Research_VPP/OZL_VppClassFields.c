// The research pages' class fields in the window's live class search (the core's
// OZ_ClassPick, design docs/specs/2026-11-13-openzone-vpp-class-search-design.md in the
// series' docs): what each edit box takes, and whether it holds a list.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

modded class OZ_VppAdminMenu
{
    override void ClassFields(OZ_ClassPick pick)
    {
        super.ClassFields(pick);
        // A rule: what goes in, what comes out, and the device it runs in (an item or a
        // static object).
        pick.Bind("RzRuInput", OZ_ClassIndex.ITEM);
        pick.Bind("RzRuOut", OZ_ClassIndex.ITEM);
        pick.Bind("RzRuDevice", OZ_ClassIndex.ITEM + OZ_ClassIndex.OBJECT);
        // A module's class; a static: the series' stations and terminals are items by config
        // (OZL_StaticDevice_Base : Inventory_Base), a map object is not.
        pick.Bind("RzMoClass", OZ_ClassIndex.ITEM);
        pick.Bind("RzStcClass", OZ_ClassIndex.ITEM + OZ_ClassIndex.OBJECT);
        // A tree node's items (class:quantity); an owner's terminals and stations (classes,
        // comma between; the stations' box has many lines).
        pick.Bind("RzTnItems", OZ_ClassIndex.ITEM, true);
        pick.Bind("RzOwTerms", OZ_ClassIndex.ITEM + OZ_ClassIndex.OBJECT, true);
        pick.Bind("RzOwDevices", OZ_ClassIndex.ITEM + OZ_ClassIndex.OBJECT, true);
    }
}

#endif
#endif
#endif
