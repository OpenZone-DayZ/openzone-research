"""Where things sit on the M61 command desk, shared by build_m61.py (geometry) and make_decals.py (the
map under the glass, the folder covers and the open folder are decals placed at the same spots:
decal projection in kmats follows the world axes, without rotation).

Blender axes: X is width, Y is depth (the working side, with the pedestal drawers and the player,
is -Y), Z is up.
"""
# desk: Soviet two-pedestal writing desk, 1.50 x 0.75, top at 0.76 (GOST 13025.3-85 gives a desk
# height of 750 mm with a tolerance)
X0, X1, Y0, Y1 = -0.75, 0.75, -0.375, 0.375
ZT = 0.76                                                    # desktop surface height
TOP_T = 0.035                                                # desktop thickness
# thick glass on the desktop (8 mm), the map lies under it
GLASS = (-0.71, 0.71, -0.345, 0.345)
GLASS_T = 0.008
ZG = ZT + 0.0015 + GLASS_T                                  # top of the glass: props stand here
# map under the glass: 0.90 x 0.60 (the sheet is 1 mm thick so it does not z-fight with the desktop;
# the glass is above it)
MAP_C, MAP_S = (-0.02, 0.0), (0.90, 0.60)
ZM = ZT + 0.001

# case-file folders ("Delo"): 0.24 x 0.33, the thickness of one includes its papers
FOLDER_W, FOLDER_D = 0.24, 0.33
FOLDER_T = 0.012                                             # folder with papers (1 mm cardboard)
CARD_T = 0.001
# stacks: (x, y centre, folder count, seed); the top folder lies straight, unrotated: it carries the cover decal
STACKS = [(-0.575, -0.15, 7, 1), (-0.575, 0.18, 5, 2)]
# open folder: centre, size of the spread (two halves); lies on the glass over the edge of the map
OPEN_C = (0.14, -0.18)
OPEN_S = (2 * FOLDER_W, FOLDER_D)
OPEN_Z = ZG + 0.0045                                         # top of the sheets in the right half
OPEN_ZL = ZG + CARD_T                                        # top of the left (empty) half


def stack_top(n):
    """Top height of a stack of n folders."""
    return ZG + n * FOLDER_T

# props
LAMP_BASE = (-0.33, 0.25)                                    # gooseneck lamp
PHONE_C = (0.555, -0.03)                                     # TA-57 field telephone
RADIO_C = (0.60, 0.235)                                      # R-158 radio
ASHTRAY_C = (0.34, 0.255)
TEA_C = (0.22, 0.17)
STAMP_C = (0.455, -0.255)                                    # stamp and ink pad
# flags on stands across the map: (x, y, colour)
FLAGS = [(-0.30, 0.04, "red"), (-0.19, -0.06, "red"), (-0.06, 0.10, "red"), (0.07, 0.02, "blue"),
         (0.19, 0.12, "blue"), (-0.38, -0.15, "red"), (0.29, -0.02, "blue"), (0.02, 0.22, "red")]

# small own items and vanilla DayZ things (proxies, build_m61.DECOR)
PACK = (0.440, 0.250, -8.0)                                  # cigarette pack by the ashtray: centre, angle
PENCIL = (0.015, -0.255, 18.0)                               # red-blue pencil on the left half of the folder
PEN = (0.285, -0.245, -62.0)                                 # DayZ pen on a sheet of the open folder
COMPASS = (-0.15, 0.225)                                     # DayZ compass on the map behind the flags
MATCHES = (0.410, 0.155, 10.0)                               # DayZ matches by the ashtray
FLASHLIGHT = (-0.30, -0.268, 84.0)                           # DayZ flashlight at the front-left edge of the map
# DayZ binoculars sit on the top folder of the rear stack (STACKS[1])
