"""Layout of the M85 gas analyzer (UG-2), shared by build_m85.py (Blender) and make_decals.py
(system Python + Pillow): the plates, the rod label, the scales in the lid and the box label lie
exactly on their parts.

Metres, module axes: x is width, y is depth (the face at -Y), z is up from the shelf; the origin is
the middle of the module_N place at the base (autocenter = 0 in Geometry).

The air intake device UG-2 follows the datasheet "not more than 110 x 105 x 200 mm, 1.5 kg" (see
the docstring of build_m85.py); the panel layout follows a photo (a numbered plate on the left by
the hinge, a second plate to the right, in the middle the rod sleeve with a stop on the left, the
hose fitting at the left rear corner).

The sizes of the decals (PLATE1, PLATE2, LABEL_W, CARD_WH, BOX_LABEL) are fixed: make_decals.py
draws them by these numbers. Also here: roundings of the body and lid, a strap on brackets, the
hose and the indicator tube along arcs (hose_route); the tube lies on the box edge farther from the
body, so that the hose runs to it without a kink.
"""
import math

# --- air intake device: body and lid ------------------------------------------------------------
DW, DD = 0.110, 0.105                   # datasheet: 110 x 105 mm in plan
DX0, DY0 = -0.100, -0.100               # left front corner
DX1, DY1 = DX0 + DW, DY0 + DD
DCX, DCY = (DX0 + DX1) / 2, (DY0 + DY1) / 2
LID_H = 0.024                           # the lid is a box (shallow in the photo)
ZS = 0.200 - LID_H                      # joint of body and lid: 0.200 is the closed height
LIP_IN, LIP_T = 0.0012, 0.0010          # flange under the lid: sunk by 1.2 mm, wall 1 mm
ZP = ZS + 0.005                         # top panel - inside the flange
ZL = ZS + 0.008                         # top of the flange
LID_T = 0.0010                          # lid wall
HINGE_Y, HINGE_Z = DY1 + 0.0025, ZS + 0.0010    # piano hinge axis at the back
LID_DEG = -140.0                        # the lid is opened back by 140 degrees (in the photo, past vertical)
# roundings of the stamped body (photo): vertical ribs, bottom and top edges, lid top
CORNER_R = 0.0055
EDGE_RB, EDGE_RT, LID_RT = 0.0016, 0.0006, 0.0030
HINGE_W, HINGE_KN = 0.094, 5            # piano hinge: length, number of knuckles (3 on the body, 2 on the lid)

# --- panel: rod sleeve, stop, fitting, plates, screws -------------------------------------------
SX, SY = DCX + 0.006, DCY + 0.004       # axis of the sleeve and rod
SLEEVE_R, SLEEVE_H = 0.0105, 0.016
FLANGE_R, FLANGE_H = 0.0140, 0.0020
BORE_R = 0.0058
STOP_Z = ZP + 0.0100                    # stop - a screw with a knurled head left of the sleeve
NIP = (DX0 + 0.020, DY1 - 0.024)        # bellows fitting
PLATE1 = ((-0.072, -0.044), (-0.0135, -0.0035))     # numbered plate: x, y
PLATE2 = ((-0.035, -0.012), (-0.0135, -0.0035))     # second plate - blank
PLATE_T = 0.0006
SCREWS = [(SX + 0.021, SY - 0.019), (SX + 0.024, SY + 0.021)]

# --- rod (bone ozl_work) -------------------------------------------------------------------------
ROD_A, ROD_CH = 0.0080, 0.0015          # 8 mm square with the corners cut: four faces with grooves
ROD_OUT = 0.018                         # cocked (bellows compressed): 18 mm above the sleeve
ROD_STROKE = 0.025                      # travel for a "100" sample: the rod rises in the work look
ROD_Z0 = ZP + SLEEVE_H - 0.030          # rod bottom - in the sleeve even with the rod raised
NECK_R, NECK_H = 0.0050, 0.0030
HEAD_R, HEAD_H = 0.0125, 0.0035
HEAD_Z0 = ZP + SLEEVE_H + ROD_OUT + NECK_H          # head bottom
HEAD_TOP = HEAD_Z0 + HEAD_H
LABEL_W = 0.0120                        # white label "100" on the head (photo)

# --- strap brackets and strap (photo: a leather strap on brackets at the sides) ------------------
LUG_Y, LUG_Z = DCY + 0.022, ZS - 0.032  # bracket middle
LUG_OUT = 0.0050                        # bracket crossbar is 5 mm from the wall
STRAP_W, STRAP_T = 0.0110, 0.0020       # strap 11 x 2 mm: sewn into the bracket, hangs down and goes under the body

# --- indicator tube box (kit datasheet: 140 x 75 x 30 mm): the lid is tucked under the bottom -----
BX0, BX1 = 0.0240, 0.0980
BY0, BY1 = -0.0400, 0.1000
BH = 0.0290
LIDB_PAD, LIDB_H, LIDB_T = 0.0015, 0.0120, 0.0010
CARD_T = 0.0012                         # cardboard
INSERT_Z = 0.0040                       # corrugated cardboard of the insert
DIV_Y = 0.0560                          # divider: tubes in front, ampoules behind
SPARE_N, SPARE_X0, SPARE_PITCH = 8, 0.0337, 0.0078
SPARE_Y = (-0.0335, 0.0515)             # spare tubes 85 mm
TUBE_R, TUBE_L = 0.0025, 0.090          # indicator tube: glass 5 x 90 mm
TUBE_RI = 0.0019                        # powder column and swabs inside the glass
SPARE_Z = INSERT_Z + TUBE_R + 0.0012
AMP_R, AMP_X = 0.0042, (0.0300, 0.0920)
AMP_Y = (0.0650, 0.0780, 0.0910)
AMP_Z = INSERT_Z + AMP_R + 0.0002
# spare tube powders (sRGB) - from the UG-2 indicator powder tables: ammonia is yellow, hydrogen
# sulphide white, sulphur dioxide bluish, carbon monoxide whitish grey, chlorine pale pink, etc.
SPARE_COLORS = [(214, 190, 70), (232, 230, 220), (176, 196, 214), (226, 176, 182), (214, 190, 70),
                (226, 170, 96), (196, 214, 170), (222, 220, 206)]

# --- hose and indicator tube in the work look ----------------------------------------------------
# The hose (6 mm rubber) goes over the right edge of the flange from the panel and down the right
# wall; at the shelf an arc down (R3), along the shelf an arc forward and to the right (R1), a rise
# to the tube (R2), a straight end of 10 mm, the tube enters it by 8 mm. The tube lies on the front
# edge of the box (TUBE_REST). Everything is along tangents, no kinks.
HOSE_R = 0.0030
HOSE_X, HOSE_Y = DX1 + HOSE_R + 0.0002, -0.0800    # descent along the right wall
HOSE_R1, HOSE_R2, HOSE_R3 = 0.010, 0.012, 0.010
TUBE_HEAD, TUBE_ELEV = 20.0, 32.0       # tube: from +y toward +x, elevation above the shelf, degrees
TUBE_IN, HOSE_END = 0.008, 0.010        # tube in the hose; the straight end of the hose


def hose_route():
    """Lower part of the hose and the tube: (D, A, R, arc points). D is the tube axis, A its lower end (in
    the hose), R the tube centre above the box edge; the points go from the bottom of the descent along
    the wall to the end of the hose.
    """
    hx, hy = math.sin(math.radians(TUBE_HEAD)), math.cos(math.radians(TUBE_HEAD))
    ce, se = math.cos(math.radians(TUBE_ELEV)), math.sin(math.radians(TUBE_ELEV))
    d = (hx * ce, hy * ce, se)
    r1, r2, r3 = HOSE_R1, HOSE_R2, HOSE_R3
    # the tube touches the front edge of the box (y = BY0, z = top of the wall) with its lower
    # surface
    ry, rz = BY0 - TUBE_R * se * hy, LIDB_T + BH + TUBE_R * ce
    k = HOSE_END - TUBE_IN                                   # from the end of the hose rise to the lower end of the tube
    az = HOSE_R + r2 * (1 - ce) + k * d[2]
    s = (rz - az) / d[2]
    ay = ry - s * d[1]
    t1y = ay - k * d[1] - r2 * se * hy
    cy = t1y + r1 * hx                                       # centre of the arc along the shelf
    m, beta = math.hypot(r1, r3), math.atan2(r3, r1)
    alpha = beta - math.acos(max(-1.0, min(1.0, (cy - HOSE_Y) / m)))
    h0 = (math.cos(alpha), math.sin(alpha))                  # where the hose leaves the wall along the shelf
    cx = HOSE_X + r3 * h0[0] - r1 * h0[1]
    t1x = cx + r1 * hy
    ax = t1x + k * d[0] + r2 * se * hx
    a = (ax, ay, az)
    rx = ax + s * d[0]
    pts = []
    # arc down at the wall: from vertical to h0
    for i in range(1, 4):
        f = math.radians(90.0 * i / 4)
        pts.append((HOSE_X + r3 * (1 - math.cos(f)) * h0[0], HOSE_Y + r3 * (1 - math.cos(f)) * h0[1],
                    HOSE_R + r3 - r3 * math.sin(f)))
    # arc along the shelf, counter-clockwise
    th0, th1 = alpha - math.pi / 2, math.atan2(-hx, hy)
    while th1 < th0:
        th1 += 2 * math.pi
    n = max(3, int(math.degrees(th1 - th0) / 22.0))
    for i in range(n + 1):
        th = th0 + (th1 - th0) * i / n
        pts.append((cx + r1 * math.cos(th), cy + r1 * math.sin(th), HOSE_R))
    t1 = pts[-1]
    # rise to the tube axis and the straight end
    for i in range(1, 3):
        f = math.radians(TUBE_ELEV * i / 2)
        pts.append((t1[0] + hx * r2 * math.sin(f), t1[1] + hy * r2 * math.sin(f), t1[2] + r2 * (1 - math.cos(f))))
    t2 = pts[-1]
    pts.append(tuple(t2[i] + d[i] * HOSE_END for i in range(3)))
    return d, a, (rx, ry, rz), pts


TUBE_D, TUBE_A, TUBE_REST, HOSE_LOW = hose_route()
TUBE_B = tuple(TUBE_A[i] + TUBE_D[i] * TUBE_L for i in range(3))
# powder column between the cotton swabs, from the lower end (s along the tube axis)
TUBE_PLUG = 0.004
TUBE_POWDER = (0.016, 0.082)
TUBE_STAIN = 0.030                      # work look: a stained column on the inlet side (the upper end)

# --- labels and scales -------------------------------------------------------------------------
BOX_LABEL = (0.050, 0.016)              # on the front end of the box (w, h), above the lid lip
BOX_LABEL_C = ((BX0 + BX1) / 2, 0.0215)
CARD_WH = (0.084, 0.072)                # scale card in the lid (along the width, along the lid depth)
