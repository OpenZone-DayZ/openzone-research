"""Layout of the M33 SOP ballistic rack case - shared by build_m33.py (geometry) and
make_decals.py: the scales, displays and stencils lie on the same faces (kmats projects
decals along the world axes).

Axes: X - width, Y - depth (front at -Y), Z - up. Dimensions and their sources are in the
docstring of build_m33.py.
"""
import math

# Rack case 0.60 x 1.20 x 0.60, shifted left: tripod on the right, the lid leans on the left
CX = -0.12
X0, X1 = CX - 0.30, CX + 0.30
Y0, Y1 = -0.30, 0.30
H = 1.20
SKID_H = 0.045                                               # skids under the bottom
ZB0 = SKID_H                                                 # bottom of the body
WALL = 0.015                                                 # double wall
RIM_W = 0.035                                                # rim of the openings (for lids)

# 19 in rack (GOST 28601.2-90 / IEC 60297: panel 482.6, 1U pitch = 44.45 mm)
U = 0.04445
PANEL_W = 0.4826
PX0, PX1 = CX - PANEL_W / 2, CX + PANEL_W / 2
YP = -0.262                                                  # panel face
PANEL_T = 0.003
RAIL_Y = (YP + PANEL_T, YP + PANEL_T + 0.012)                # front posts with threaded holes
RAIL_BACK_Y = (0.235, 0.247)
UNIT_Y1 = 0.215                                              # rear wall of the units
Z_STACK = 0.080                                              # bottom of the first unit


def _stack():
    z = Z_STACK
    out = {}
    for name, n in (("psu", 4), ("drawer", 3), ("timer", 5), ("amp", 4), ("ctrl", 5), ("shelf", 3)):
        out[name] = (z, z + n * U)
        z += n * U
    return out


UNITS = _stack()                                             # unit -> (bottom, top) along z
DRAWER_OUT = 0.24                                            # sample shelf pulled out

# Dial meters of the M4200 class (80 x 80 case): window center x, window bottom z, window w x h,
# scale (look for make_decals), bone (None - does not move). The power meter has a bone too:
# while working its needle goes to the operating voltage and trembles slightly.
MW, MH = 0.066, 0.056                                        # scale window
FLANGE = 0.080
METERS = [
    dict(x=CX - 0.150, z=UNITS["amp"][0] + 0.060, scale="a", bone="ozl_work"),
    dict(x=CX - 0.055, z=UNITS["amp"][0] + 0.060, scale="b", bone="ozl_work_2"),
    dict(x=CX - 0.130, z=UNITS["ctrl"][0] + 0.095, scale="c", bone="ozl_work_3"),
    dict(x=CX - 0.150, z=UNITS["psu"][0] + 0.060, scale="d", bone="ozl_work_4"),
]
PIVOT_DZ = 0.008                                             # needle pivot above the window bottom
NEEDLE_L = 0.044
ARC_DEG = 90.0                                               # 90 degree scale, symmetric about up
NEEDLE_PHASE1 = 1.0                                          # phase 1 = full scale

# Digital readouts (ozl_screen): center x, z, size w x h, digit places n, decimal point after
# place `point` (None - no point). The time meter shows the flight time over the sensor base
# (0.30 m) in microseconds, "00419.6"; the control unit shows the speed, m/s.
READOUTS = {
    "timer": dict(x=CX - 0.060, z=UNITS["timer"][0] + 0.150, w=0.160, h=0.050, n=6, point=4),
    "speed": dict(x=CX + 0.075, z=UNITS["ctrl"][0] + 0.155, w=0.090, h=0.036, n=4, point=None),
}
SENSOR_BASE = 0.30                                           # speed sensor base, m (the coils)
# Both readouts are one LCD_PX x LCD_PX picture with its own unwrap (the work frames cycle it):
# the time meter window is at the top, the speed window at the bottom, with an 8 px gap
# between them (mip levels do not blend the windows); x0, y0, x1, y1 in pixels, y down.
LCD_PX = 512
LCD_RECTS = {"timer": (0, 0, 512, 252), "speed": (0, 260, 288, 512)}


def lcd_uv(key):
    """UV of a readout window in the picture: u0, u1, v0, v1 (v is up, as in Blender)."""
    x0, y0, x1, y1 = LCD_RECTS[key]
    return x0 / LCD_PX, x1 / LCD_PX, 1.0 - y1 / LCD_PX, 1.0 - y0 / LCD_PX

# Stencils: number and stripes on the right side (faces +x); stripes on the lid (faces -x).
SIDE_NUM = dict(text="2531", y=0.0, z=0.42, w=0.30, h=0.10)
SIDE_BAND = dict(y=0.0, z=0.28, w=0.42, h=0.06)
# The lid leans on the left side: the bottom of its outer face stands LID_OUT away, the top
# touches the wall.
LID_T = 0.055
LID_H = H - ZB0 - 0.02
LID_OUT = 0.22
LID_DEG = math.degrees(math.atan2(LID_OUT, LID_H))
LID_DECAL = dict(y=0.0, z=0.62, w=0.46, h=0.30)

# Tripod with the sensor on the right
TRI_X, TRI_Y = CX + 0.62, -0.18
TRI_HEAD = 0.52                                              # tripod head
TRI_R = 0.24                                                 # leg spread on the floor
SENSOR_Z = 0.62                                              # sensor axis
SENSOR_L = 0.34                                              # tube length (base 0.30 between coils)
