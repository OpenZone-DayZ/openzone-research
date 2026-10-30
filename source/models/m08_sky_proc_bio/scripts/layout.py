"""Shared M08 numbers for make_decals.py (system Python) and build_m08.py (Blender): where the knobs,
lamps, the scale window and the KFK-2 needle, the hotplate knobs are - so that the decals (digits at
the knobs, panel outlines, the scale) lie exactly under the parts. Blender axes: X is width, Y is
depth (face toward -Y), Z is up; metres.
"""
# crates: A under the hotplate, B under the KFK-2
XA0, XA1, YA0, YA1, ZA = -0.52, 0.04, -0.23, 0.23, 0.56
XB0, XB1, YB0, YB1, ZB = 0.08, 0.53, -0.20, 0.20, 0.40

# hotplate EPCh-2: 505 x 285 x 96
XP, YP, PW, PD = -0.24, -0.01, 0.505, 0.285
ZP0, ZPT = ZA + 0.012, ZA + 0.096                       # bottom of the body (on feet), top
PY0 = YP - PD / 2                                       # hotplate face
BURN = [(XP - 0.125, 0.0725), (XP + 0.115, 0.090)]      # (x, radius): left is free, the cooker is on the right
PKNOB_Z = (ZP0 + ZPT) / 2 - 0.004                       # axis of the switch knobs
PKNOB_R = 0.017
PILOT = (XP, (ZP0 + ZPT) / 2 + 0.006)                   # hotplate lamp (x, z)

# KFK-2 photocolorimeter: 435 x 355 x 330, base 165
XK, YK = (XB0 + XB1) / 2, 0.0
KW, KD, KH, KB = 0.435, 0.355, 0.33, 0.165
ZK0 = ZB + 0.008
KY0 = YK - KD / 2                                       # face of the base
CUV = (XK - 0.075, XK + 0.075)                          # cuvette compartment x0, x1
# knobs on the face (x, z, radius, name): filters at the left; sensitivity and "set 100" (coarse,
# fine) at the right - as in the photo
KNOBS = [(XK - 0.135, ZK0 + 0.058, 0.019, "filter"), (XK + 0.122, ZK0 + 0.055, 0.019, "sens"),
         (XK + 0.172, ZK0 + 0.112, 0.0125, "fine"), (XK + 0.172, ZK0 + 0.062, 0.0125, "coarse")]
KLAMP = (XK - 0.135, ZK0 + 0.125)                       # power indicator above the filter knob
# face panels (the outline is a decal): at the left of the cuvette compartment and at the right of it
KR = 0.022                                              # rounding of the base corners in plan
PANEL_L = (XK - KW / 2 + KR + 0.002, CUV[0] - 0.014, ZK0 + 0.014, ZK0 + KB - 0.016)
PANEL_R = (CUV[1] + 0.014, XK + KW / 2 - KR - 0.002, ZK0 + 0.014, ZK0 + KB - 0.016)
# scale housing and window: x0, x1, z0, z1; the housing face
HOUSE_W = 0.24
WIN = (XK - 0.105, XK + 0.105, ZK0 + 0.235, ZK0 + 0.305)
YWIN = YK + 0.015
# microammeter scale (the decal_scale_* decals): an arc of radius SCALE_R of the window width, the top
# of the arc SCALE_TOP of the window height below its top, from SCALE_A[0] to SCALE_A[1] degrees (as in
# the picture: y down)
SCALE_R, SCALE_TOP, SCALE_A = 0.62, 0.36, (-125.0, -55.0)
_W, _H = WIN[1] - WIN[0], WIN[3] - WIN[2]
METER_R = SCALE_R * _W                                  # arc radius, m
METER_PIVOT = ((WIN[0] + WIN[1]) / 2, WIN[3] - SCALE_TOP * _H - METER_R)   # needle axis (x, z) - under the window
METER_WORK = 0.62                                       # reading in "work" (fraction of the scale)

# cooker gauge: scale 0-4 kgf/cm2 over 270 degrees, zero at the left-bottom (225 degrees)
GAUGE_ZERO, GAUGE_SPAN = 225.0, 270.0
GAUGE_WORK = 0.27                                       # ~1.1 kgf/cm2 (15 psi of the autoclave)
