"""Layout of the M35 SOP muffle furnace - shared by build_m35.py (geometry) and make_decals.py:
the scales, the regulator dial, the sign and the stencil lie on the same faces (kmats projects
decals along the world axes).

Axes: X - width, Y - depth (front at -Y), Z - up. Dimensions and their sources are in the
docstring of build_m35.py.
"""
import math

# --- Lab cabinet base: 0.90 x 0.70, worktop at 0.80 -------------------------------------------
X0, X1 = -0.45, 0.45
Y0, Y1 = -0.35, 0.35
TOP = 0.80
DOOR_Y = Y0 + 0.02 - 0.018                                   # front of the kfurn.lab_cabinet doors
ASB_T = 0.010                                                # asbestos-cement sheet under furnace

# --- Furnace of the MP-2 class: body 0.365 x 0.60 x 0.45 on 40 mm feet ------------------------
FX0, FX1 = -0.005, 0.360
FCX = (FX0 + FX1) / 2
FY0, FY1 = -0.30, 0.30
FEET = 0.040
FZ0 = TOP + ASB_T + FEET
FZ1 = FZ0 + 0.45
FRONT_T = 0.012                                              # front frame (protrudes)
# Door: slab 0.30 x 0.24, 0.065 thick (lining), closed; chamber 0.25 x 0.16 (MP-2/1200)
DW, DH, DT = 0.300, 0.240, 0.065
DZ0 = FZ0 + 0.075
DY = FY0 - FRONT_T                                           # the door presses against the frame
PEEP = dict(x=FCX, z=DZ0 + DH * 0.62, r=0.016)              # peephole with mica
# Regulator box on the right side (as on the MP-2U): 0.075 x 0.36
HX0, HX1 = FX1, FX1 + 0.075
HY0, HY1 = -0.17, 0.19
HZ0, HZ1 = FZ0 + 0.03, FZ1 - 0.07
DIAL = dict(y=0.03, z=HZ0 + 0.12, r=0.040)                   # regulator dial (faces +x)
HLAMP = dict(y=0.03, z=HZ0 + 0.225, r=0.007)                 # "heating" lamp above the regulator
# Exhaust: a stub on the roof, a dia 80 pipe going up and an elbow back toward the wall
EXH = dict(x=FCX + 0.02, y=0.10, r=0.040, top=1.53, back=0.42)
# thermocouple: a sleeve in the roof
TC = dict(x=FCX - 0.09, y=0.17)

# --- Control panel on the worktop, rear left --------------------------------------------------
SX0, SX1 = -0.43, -0.07
SY0, SY1 = 0.10, 0.30                                        # the panel face is at -Y, y = SY0
SZ0, SZ1 = TOP, TOP + 0.44
# Dial meters: window center x, window bottom z, window w x h, scale, bone (also the animation
# source); phase - where the needle sits while working (fraction of the scale: the middle of
# the wobble)
METERS = [
    dict(x=SX0 + 0.115, z=SZ0 + 0.250, w=0.120, h=0.090, flange=0.150, scale="t", bone="ozl_needle", phase=0.75),
    dict(x=SX1 - 0.085, z=SZ0 + 0.270, w=0.066, h=0.056, flange=0.080, scale="a", bone="ozl_needle_2", phase=0.60),
]
ARC_DEG = 90.0
# Needle pivot above the window bottom and needle length, as fractions of the window height.
PIVOT_K = 0.15
NEEDLE_K = 0.80

# --- Sample: a plate cools on two fireclay bricks, front left ---------------------------------
BRICK = (0.250, 0.123, 0.065)                                # ShA-5 (GOST 390): 250 x 123 x 65
PLATE = dict(x=-0.245, y=-0.15, w=0.250, d=0.300, t=0.008)   # 10 x 12 in plate (250 x 300 mm)

# --- Decals -----------------------------------------------------------------------------------
HEAT_SIGN = dict(x=FX1 - 0.045, z=FZ1 - 0.050, s=0.060)      # "hot" sign on the furnace front
STENCIL = dict(x=X0 + 0.22, z=0.62, w=0.22, h=0.06, text="0417")  # inventory no. on cabinet door
TAGS = [(SX0 + 0.055, SZ0 + 0.200, 0.08, 0.016), (SX1 - 0.085, SZ0 + 0.225, 0.06, 0.012)]


def needle_rest():
    return -math.radians(ARC_DEG / 2)
