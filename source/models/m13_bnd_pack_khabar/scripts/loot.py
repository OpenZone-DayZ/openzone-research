"""Where things lie on the M13 lid - shared by build_m13.py (geometry) and make_decals.py (decals are
turned the way the items lie: kmats projects decals from above, along the world axes).

Slots: front left - slot 1 (dosimeter M75), rear left - slot 3 (lead capsule M77), right - slot 2
(jeweller's loupe M76) in front of the heap of watches and chains; on the right - the loot, with a pager
in it ("work" look).

Sizes, m: money is hryvnias, the size and design of a banknote follow its denomination - uah.py (NBU:
20 UAH is 130 x 69 mm ... 500 UAH is 154 x 75 mm); bundles of 500, 200 and 100 UAH, loose notes of 50
and 20. A playing card is 58 x 88 mm (Soviet 36-card deck), a cigarette pack 88 x 55 x 22 mm (like the
M16 packs, DayZ "Chernomorka" texture), a carton is 10 packs in two layers; the digital pager is like
the Motorola Bravo (~62 x 45 x 16 mm, window 38 x 13 mm); a folded butterfly knife has 130 mm handles;
wristwatches - case dia. 34-40 mm, strap 18-20 mm; chains dia. ~2.4 mm.
"""
import uah

CARD = (0.058, 0.088)
CARD_T = 0.0008

# module places (proxy points, centre of the module bottom): slot 1 - M75, 2 - M76, 3 - M77
SLOTS = [(-0.42, -0.170), (0.22, -0.190), (-0.42, 0.175)]
# trace on the lead where the device lay (slot 1 is empty - a clean rectangle in the dust): x0, x1, y0, y1 -
# the M75 box (0.200 x 0.114, shifted forward by 15 mm)
DUST_CLEAN = (SLOTS[0][0] - 0.103, SLOTS[0][0] + 0.101, SLOTS[0][1] - 0.075, SLOTS[0][1] + 0.044)

# bundles of money under a rubber band: name, centre (x, y), rotation about z (degrees), height of the
# bottom above the lid (a bundle lies on two others), thickness. The notes are large (up to 154 x 75), so
# the lower bundles are spread 6 mm apart - they still tuck under each other beneath the top bundle
CASH = [
    ("cash0", (0.424, 0.020), 8.0, 0.0, 0.018),
    ("cash1", (0.554, 0.004), -12.0, 0.0, 0.018),
    ("cash2", (0.490, 0.044), 24.0, 0.018, 0.016),
    ("cash3", (0.420, -0.098), -5.0, 0.0, 0.012),
]
# loose: two notes fanned out, a pager on them (the upper one is turned 39 degrees, not 51, so that it
# does not reach into the bundle)
NOTES = [
    ("note0", (0.586, -0.125), 32.0, 0.0000),
    ("note1", (0.602, -0.109), 39.0, 0.0006),
]
NOTE_T = 0.0005
# denomination of each bundle and note, UAH
UAH = {"cash0": 500, "cash1": 200, "cash2": 100, "cash3": 500, "note0": 50, "note1": 20}


def note_size(nm):
    """Width and height of the banknote of a bundle or loose note nm, m."""
    return uah.SIZE[UAH[nm]]


# cards: a deck face down and a fan of three cards face up (suits and digits - no letters)
DECK = ("deck", (0.452, -0.252), 15.0, 0.0, 0.016)
FAN = [
    ("card0", (0.522, -0.262), -32.0, 0.0010, "7h"),
    ("card1", (0.565, -0.270), -10.0, 0.0022, "9s"),
    ("card2", (0.610, -0.262), 14.0, 0.0034, "10d"),
]

# "Chernomorka" packs (DayZ): the carton - lower layer 5, upper 4 (one taken out, it lies beside)
PACK = (0.088, 0.055, 0.022)                  # length, width, thickness
BLOCK = ((0.352, 0.236), 3.0)                 # carton centre, rotation: packs lengthwise along y
LOOSE_PACK = ((0.566, 0.205), 35.0)

# pager: centre, rotation (length along u); lies on a clip
PAGER = ((0.612, -0.098), -16.0)
PAGER_SIZE = (0.062, 0.045, 0.016)
# screen window on the face (offset from the centre along u, v): centre and size, m
PAGER_SCREEN = ((0.004, 0.006), (0.038, 0.013))

# folded butterfly knife: centre, rotation (length along u)
KNIFE = ((0.688, -0.205), 82.0)

# wristwatches in a heap (in order, bottom to top: the straps of the next ones lie on the previous): name,
# centre, rotation (12 o'clock along u), case radius, height, bracelet ("steel", "gold" - metal,
# "leather" - leather), dial (make_decals style), strap length at 12 and at 6 o'clock from the centre
WATCHES = [
    ("watch0", (0.212, 0.002), 25.0, 0.0190, 0.0105, "steel", "black", (0.066, 0.060)),
    ("watch3", (0.292, -0.030), 100.0, 0.0200, 0.0110, "steel", "blue", (0.064, 0.052)),
    ("watch1", (0.284, 0.058), -40.0, 0.0175, 0.0090, "gold", "gold", (0.060, 0.066)),
    ("watch2", (0.196, 0.080), 112.0, 0.0165, 0.0090, "leather", "white", (0.062, 0.066)),
]
# watch without a bracelet: one edge on the lid, the other on the case of watch0 (the generator works out the tilt)
WATCH_TILT = ("watch4", (0.239, 0.031), -15.0, 0.0180, 0.0095, "white2", "watch0")
# chains: anchor points over the lid (the heap under them sets the height) and rings (centre, radius, with a stone)
CHAINS = [
    [(0.166, -0.046), (0.186, -0.020), (0.210, 0.006), (0.246, 0.006), (0.270, -0.022), (0.300, -0.040),
     (0.330, -0.020), (0.326, 0.012)],
    [(0.250, 0.104), (0.226, 0.068), (0.252, 0.044), (0.292, 0.070), (0.304, 0.100), (0.272, 0.118),
     (0.240, 0.112)],
]
RINGS = [((0.330, 0.098), 0.0095, True), ((0.164, -0.066), 0.0090, False)]

# cigarette butts: centre, rotation, length (filter 0.020 + remainder 0.006..0.016)
BUTTS = [((0.372, -0.214), 40.0, 0.032), ((0.352, -0.188), 160.0, 0.026), ((0.676, -0.300), 75.0, 0.036),
         ((0.497, 0.150), 15.0, 0.030)]
