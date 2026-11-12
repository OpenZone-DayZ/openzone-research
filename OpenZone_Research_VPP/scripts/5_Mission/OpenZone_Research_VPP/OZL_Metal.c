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
    static const int SCREEN = 0xF7090909;   // vppScreen  0.035 @ 0.97
    static const int PANEL  = 0xFF0C0C0C;   // vppPanel   0.047
    static const int HEAD   = 0xFF131312;   // vppHead    0.075 0.075 0.071
    static const int RAISED = 0xFF1E1E1D;   // vppRaised  0.118 0.118 0.114
    static const int CELL   = 0xFF070707;   // vppCell    0.027
    static const int EDGE   = 0xFF3C3C3A;   // vppEdge    0.235 0.235 0.227

    // --- text
    static const int TEXT   = 0xFFE0DFDA;   // vppText    0.88  0.875 0.855
    static const int MUTED  = 0xFFA09F99;   // vppMuted   0.627 0.624 0.6
    static const int FAINT  = 0xFF5C5A58;   // vppFaint   0.36  0.353 0.345

    // --- states
    static const int ACCENT = 0xFFE8782B;   // vppAccent  0.91  0.47  0.17
    static const int ALERT  = 0xFFF5C740;   // vppAlert   0.96  0.78  0.25
    static const int OK     = 0xFF66C75C;   // vppOk      0.4   0.78  0.36
    static const int BAD    = 0xFFE0524A;   // vppBad     0.88  0.32  0.29

    // --- see-through
    static const int PICK   = 0x29E8782B;   // vppPick    accent @ 0.16
}

#endif
#endif
#endif
