// The research editor's script colours: the palette of the OpenZone admin window as the
// mockup of 2026-11-12 has it (docs/specs/2026-11-13-openzone-vpp-page-guide.md, section 2.3).
// The pages are converted from the mockup and carry their colours in their layouts; these
// are for what the script paints itself: a picked row, a state, a chip.
//
// Written as numbers: a constant made by a call (ARGB) reads 0 in a Mission-module class
// (measured on the stand 2026-11-12). The engine blends in linear light, so a see-through
// colour of the mockup is written as the opaque colour it comes to over its ground.

#ifdef AVPPAdminTools
#ifdef OpenZone_VPP
#ifndef NO_GUI

class OZL_Metal
{
    // --- grounds
    static const int PANEL  = 0xFF0C0C0C;
    static const int HEAD   = 0xFF131312;
    static const int RAISED = 0xFF1E1E1D;
    static const int CELL   = 0xFF070707;
    static const int EDGE   = 0xFF3C3C3A;

    // --- text
    static const int TEXT   = 0xFFE0DFDA;
    static const int MUTED  = 0xFFA09F99;
    static const int FAINT  = 0xFF5C5A58;
    // on the accent
    static const int INK    = 0xFF140A02;

    // --- states
    static const int ACCENT = 0xFFE8782B;
    static const int ALERT  = 0xFFF5C740;
    static const int OK     = 0xFF66C75C;
    static const int BAD    = 0xFFE0524A;

    // --- a picked row or segment: the accent at 0.16 over the panel, over the head
    static const int PICK_PANEL = 0xFF2F1D11;
    static const int PICK_HEAD  = 0xFF352316;

    // --- soft grounds over the head: bad at 0.14 (a lit button), bad at 0.16, alert at
    //     0.12 and ok at 0.12 (chips)
    static const int BAD_SOFT  = 0xFF301C1A;
    static const int BAD_CHIP  = 0xFF341D1B;
    static const int WARN_CHIP = 0xFF2E2918;
    static const int OK_CHIP   = 0xFF1D291B;
}

#endif
#endif
#endif
