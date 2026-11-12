// The research editor's script colours: the OpenZone admin window's metal (VPP rework
// 2026-11-12, design §2.3), the same values as the vpp* names of the core's tokens
// (openzone-core\ui\tokens.json, group `color`), which the pane's layout description
// takes. OZ_Palette is the PDA's palette -- the PDA as a device keeps its own look --
// so nothing of the window paints from it any more. The engine does not read the
// tokens file: change a vpp* token there, change it here too.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

class OZL_Metal
{
    // --- grounds
    static const int SCREEN = ARGB(247,   9,   9,   9);   // vppScreen  0.035 @ 0.97
    static const int PANEL  = ARGB(255,  12,  12,  12);   // vppPanel   0.047
    static const int HEAD   = ARGB(255,  19,  19,  18);   // vppHead    0.075 0.075 0.071
    static const int RAISED = ARGB(255,  30,  30,  29);   // vppRaised  0.118 0.118 0.114
    static const int CELL   = ARGB(255,   7,   7,   7);   // vppCell    0.027
    static const int EDGE   = ARGB(255,  60,  60,  58);   // vppEdge    0.235 0.235 0.227

    // --- text
    static const int TEXT   = ARGB(255, 224, 223, 218);   // vppText    0.88  0.875 0.855
    static const int MUTED  = ARGB(255, 160, 159, 153);   // vppMuted   0.627 0.624 0.6
    static const int FAINT  = ARGB(255,  92,  90,  88);   // vppFaint   0.36  0.353 0.345

    // --- states
    static const int ACCENT = ARGB(255, 232, 120,  43);   // vppAccent  0.91  0.47  0.17
    static const int ALERT  = ARGB(255, 245, 199,  64);   // vppAlert   0.96  0.78  0.25
    static const int OK     = ARGB(255, 102, 199,  92);   // vppOk      0.4   0.78  0.36
    static const int BAD    = ARGB(255, 224,  82,  74);   // vppBad     0.88  0.32  0.29

    // --- see-through
    static const int PICK   = ARGB( 41, 232, 120,  43);   // vppPick    accent @ 0.16
}

#endif
#endif
#endif
