"""M49 - shared sizes for build_m49.py (Blender) and make_decals.py (system Python + Pillow): the bag,
the seams, the board and the parts on it, the tag. No dependencies - both import it.

Axes as in the generator: X is the bag width, Z is the height (the bag stands, like the vanilla
Paper.p3d), Y is the thickness, the front faces -Y. The origin is the bag centre. The board uses its own
millimetres: x from -40 to 40 (as model X), z' from 0 (the lower edge with the edge connector) to 100.
"""

# --- bag: 3M SCC 1000 Static Shielding Bag 4 x 6", 101.6 x 152.4 mm inside ----------------
BAG_W, BAG_H = 0.1016, 0.1524
HX, HZ = BAG_W / 2, BAG_H / 2
SIDE_SEAM = 0.0040                  # welded side seams and the bottom
SEAL_Z0, SEAL_Z1 = 0.0600, 0.0660   # cross weld below the neck (sealed, like a sample)

# --- board: half-size Eurocard 100 x 80 x 1.6 mm ------------------------------------------
PCB_W, PCB_H, PCB_T = 0.080, 0.100, 0.0016
PCB_Z0 = -0.0690                    # lower edge of the board (3 mm above the bottom seam)
PCB_Y0 = 0.0004                     # board front face (parts go towards -Y), the back is PCB_Y0 + PCB_T
LEADS = 0.0015                      # leads under the board

# parts on the board: (kind, cx, cz', length along x, width along z', height above the board), mm DIP
# per JEDEC MS-001: pitch 2.54, rows 7.62 (300 mil) and 15.24 (600 mil)
PARTS = [
    ("dip", -21.0, 20.0, 19.3, 6.4, 4.2, 16),
    ("dip", 3.0, 20.0, 19.3, 6.4, 4.2, 16),
    ("cap", 26.0, 20.0, 13.0, 6.3, 6.3, 0),      # axial electrolytic, lying down (like K50-6)
    ("dip", -8.0, 38.0, 52.3, 13.7, 4.4, 40),    # DIP-40 processor
    ("xtal", 29.0, 38.0, 13.5, 11.0, 4.7, 0),    # HC-49/U crystal, lying down
    ("eprom", -17.0, 58.0, 32.0, 15.2, 4.6, 24), # ROM in ceramic with a window (like K573RF2 / 2716)
    ("dip", 20.0, 58.0, 19.3, 6.4, 4.2, 16),
    ("dip", -24.0, 77.0, 19.0, 6.4, 4.2, 14),
    ("dip", -1.0, 77.0, 19.0, 6.4, 4.2, 14),
    ("dip", 22.0, 77.0, 19.0, 6.4, 4.2, 14),
    ("cap", -23.0, 91.0, 13.0, 6.3, 6.3, 0),
]
ROW_300, ROW_600 = 7.62, 15.24
FINGERS = (0.0, 8.0, -32.0, 32.0, 2.54, (6.0, 8.6))   # z'0, z'1, x0, x1, pitch, key (x)
HOLES = [(-36.0, 95.5), (36.0, 95.5), (-36.0, 13.0), (36.0, 13.0)]
RESISTORS = [(-6.0, 89.0), (2.0, 89.0), (10.0, 89.0), (18.0, 89.0), (26.0, 89.0),
             (2.0, 94.0), (10.0, 94.0), (18.0, 94.0)]     # MLT resistors, lying along x, as a drawing
CERAMIC = [(-33.0, 27.0), (14.0, 27.0), (-36.0, 48.0), (33.0, 49.0), (8.0, 67.0), (33.0, 68.0),
           (-36.0, 84.0), (11.0, 84.0)]                      # disc capacitors, as a drawing


def row_spacing(pins):
    return ROW_600 if pins >= 24 else ROW_300


def pcb_x(x_mm):
    return x_mm / 1000.0


def pcb_z(z_mm):
    return PCB_Z0 + z_mm / 1000.0


# --- tag: manila 46 x 28 mm, stapled to the weld -------------------------------------------
TAG_W, TAG_H = 0.046, 0.028
TAG_TOP = 0.0035                    # tag edge above the staple
TAG_PIN = (0.012, 0.0630)           # staple (x, z) - in the middle of the weld
TAG_ROT = -7.0                      # rotation in the bag plane, degrees (clockwise)

# --- ESD mark on the front film (a drawing, no text) -----------------------------------------
ESD_C, ESD_SIZE = (0.028, -0.052), 0.019

# film fold across the free space above the board: from (x, z) to (x, z)
CREASE = ((-0.0508, 0.0470), (0.0508, 0.0375))
# dog-eared corner of the neck on the right: fold line from (x, z) to (x, z)
DOGEAR = ((0.0355, 0.0762), (0.0508, 0.0640))
