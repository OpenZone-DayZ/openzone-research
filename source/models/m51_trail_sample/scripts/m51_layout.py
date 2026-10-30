"""M51 - shared sizes for build_m51.py (Blender) and make_decals.py (system Python + Pillow): a double
sheet from the middle of a school exercise book, folds, staples. No dependencies - both import it.

The sheet has its own coordinates (s, t), metres: the front side of the spread (the map is on it), s
runs left to right, t bottom to top; s = 0 is the outer edge of the left page, s = SHEET_W that of the
right one, the spine (fold 1) is at s = SPINE. Fold 2 runs across, at t = FOLD2; the old, flattened fold
3 runs through the middle of the pages, s = OLD_FOLD.

Folded with the map outside (fold 1 is a mountain, so the drawing shows without unfolding), then in half
(fold 2): a 170 x 102.5 mm packet of four layers. Two flaps of two layers: the lower (B) lies, the upper
(A) is turned back on fold 2. In the generator axes (X is the packet length, fold 1 is at x = -HX; fold
2 runs along X at the back, y = +HY; b is the distance from fold 2 to the free edge):
    flap B, top    (inside)  - left page:  s = SPINE/2 - x,  t = FOLD2 + b
    flap B, bottom (outside) - right page: s = 1.5*SPINE + x, t = FOLD2 + b
    flap A, bottom (inside)  - left page:  s = SPINE/2 - x,  t = FOLD2 - b
    flap A, top    (outside) - right page: s = 1.5*SPINE + x, t = FOLD2 - b
The winding is checked: on every face the drawing is not mirrored ((ds x dt) . n > 0).
"""

# --- sheet: GOST 12063-89 school exercise books - 170 x 205 mm, 5 mm grid --------------------
PAGE_W, PAGE_H = 0.170, 0.205
SHEET_W, SHEET_H = 2 * PAGE_W, PAGE_H       # double sheet from the middle of the book (stapled)
SPINE = PAGE_W                              # fold 1 is the spine, the staple punctures are on it
FOLD2 = PAGE_H / 2                          # fold 2 is across
OLD_FOLD = (PAGE_W / 2, PAGE_W * 1.5)       # fold 3 was there, flattened: the middles of the pages

CELL = 0.005
GRID_SPINE = 0.005                          # the grid stops one cell short of the spine
GRID_TB = 0.010                             # and two cells short of the top and bottom
MARGIN = 0.020                              # margins of 4 cells, the red line at the outer edge

# staples: two, at the quarters of the height, 12 mm legs (punctures on the spine)
STAPLES = (PAGE_H * 0.25, PAGE_H * 0.75)
STAPLE_LEG = 0.006

# --- packet ----------------------------------------------------------------------------------
L = PAGE_W                                  # 0.170 - along X
W = FOLD2                                   # 0.1025 - along Y
HX, HY = L / 2, W / 2
