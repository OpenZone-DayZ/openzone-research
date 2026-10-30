"""Layout of the Freedom chest with a work board M29, shared by build_m29.py (geometry) and
make_decals.py (decals lie on the same faces: decals are projected in kmats along the world axes).

Axes: X is width, Y is depth (the face looks to -Y), Z is up. The sizes and their sources are in the
docstring of build_m29.py.
"""
import math

# chest: 1.22 x 0.61, a body on runners, the lid is thrown back
CX0, CX1 = -0.61, 0.61
CY0, CY1 = -0.17, 0.44
ZSK = 0.022                                                  # runner height
ZR = 0.455                                                   # top of the body walls (the rim)
WALL = 0.016                                                 # wall (5/8 inch plywood)
ZF = ZSK + 0.016                                             # floor inside
LID_H = 0.07                                                 # lid height (with the rim)
LID_DEG = 102.0                                              # the lid is open by this many degrees
HINGE = (CY1, ZR)                                            # hinge axis: (y, z) at the rear edge


def lid_point(y, z):
    """A lid point in the closed position (y, z) -> open: rotation about the hinge axis (along x)."""
    a = -math.radians(LID_DEG)                               # the front edge goes up and back
    dy, dz = y - HINGE[0], z - HINGE[1]
    return (HINGE[0] + dy * math.cos(a) - dz * math.sin(a), HINGE[1] + dy * math.sin(a) + dz * math.cos(a))


# folding board in front on two brackets: x0, x1, y0 (front), y1 (at the chest), top, thickness
BX0, BX1 = -0.68, 0.68
BY0, BY1 = -0.57, CY0 - 0.004
BT = 0.022
BZ = ZR - 0.012                                              # the board top is slightly below the rim

# module places: slot N is module N of the "Protection" line: 1 - the pressure tester M84 on the left by
# the mannequin (the hose from the mask goes to it), 2 - the gas analyzer M85 between the mannequin and
# the helmet, 3 - the plate clamp M86 on the right. The pad is ~0.21 x 0.21, 0.25 clear above it
MOD_X, PAD = (-0.555, -0.03, 0.53), 0.21
MOD_Y = -0.345

# mannequin head with a GP-5 gas mask (vanilla) and a PASGT helmet (vanilla) on the board
HEAD_XY = (-0.30, -0.30)
HEAD_DEG = 20.0                                              # facing forward and left, toward the pressure tester
HELM_XY = (0.235, -0.335)

# compressor under the board on the right, on the floor: center x, y; the receiver along x
COMP_XY = (0.40, -0.40)
GAUGE_D = 0.056                                              # receiver gauge (dial)

# faces for decals
LID_IN = (CX0 + 0.06, CX1 - 0.06, 0.07, CY1 - CY0 - 0.06)    # inside of the lid: x, distance from the hinges
LID_SIN = math.sin(math.radians(LID_DEG))                    # inside of the lid in height: z = ZR + d * LID_SIN
END_R = (CY0 + 0.05, CY1 - 0.05, ZSK + 0.05, ZR - 0.05)      # right end, face x = CX1
END_L = END_R                                                # left end, face x = CX0
FRONT = (CX0 + 0.05, CX1 - 0.05, ZSK + 0.04, BZ - 0.14)      # face under the board, y = CY0
