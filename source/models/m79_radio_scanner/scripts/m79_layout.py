"""Layout of the M79 radio scanner (AOR AR3000A), shared by build_m79.py (Blender) and
make_decals.py (system Python + Pillow): knobs, keys and sockets sit exactly on their ticks,
digits and icons.

Metres, instrument axes: x is width (0 is the middle of the case), z is height from the shelf, the
front faces -Y (the front panel is the plane y = BEZ_Y[0]). The whole model is shifted by (OX, OY)
- see build_m79.py.

Positions are taken from a nearly front-on photo (the panel measures 790 x 485 px for 138 x 78 mm:
5.72 px/mm across and 6.22 px/mm in height) and cross-checked with a second photo (8.78 and
10 px/mm); a disagreement of up to 3 mm is the perspective of the protruding dial.
"""

W, H, D = 0.138, 0.080, 0.200          # AR3000A datasheet: 138 x 80 x 200 mm without protrusions
FOOT_H = 0.003                          # rubber feet
BEZ_Y = (-0.100, -0.092)                # front bezel (plastic), 8 mm
BEZ_Z = (0.002, 0.080)
CASE_X = 0.0685                         # U-shaped cover, 0.5 mm narrower than the bezel
CASE_Z = (0.003, 0.0795)
REAR_Y = 0.100

# left column: power button, squelch, volume, the headphone jack at the bottom
LEFT_X = (-0.069, -0.0405)
POWER, POWER_WH = (-0.0545, 0.0655), (0.0130, 0.0075)
SQL, VOL = (-0.0545, 0.0480), (-0.0545, 0.0280)
KNOB_R, SKIRT_R = 0.0068, 0.0086
PHONE_DIV_Z = 0.0170
JACK, JACK_R = (-0.0500, 0.0095), 0.0034
PHONE_ICON = (-0.0618, 0.0095)

# right part: nameplate (blank), LCD window, two buttons right of the display, keypad, dial
PLATE_X, PLATE_Z = (-0.0375, 0.0655), (0.0705, 0.0770)
LCD_X, LCD_Z = (-0.0370, 0.0510), (0.0465, 0.0675)
LCD_DEPTH = 0.0015                      # the display is sunk into the bezel
SMALL_BTN, SMALL_R = [(0.0575, 0.0615), (0.0575, 0.0515)], 0.0024
KEYPAD_X, KEYPAD_Z = (-0.0375, 0.0660), (0.0045, 0.0445)
KEYPAD_DEPTH = 0.0008
KEY_COLS = [-0.0305, -0.0169, -0.0034, 0.0102, 0.0238]
KEY_ROWS = [0.0340, 0.0263, 0.0189, 0.0115]
KEY_EXTRA = [(0.0394, 0.0345), (0.0534, 0.0345)]          # "down", "up"
KEY_WH, KEY_H = (0.0105, 0.0050), 0.0025
# digits by the keys (right of the key): (column, row, character)
KEY_DIGITS = [(1, 0, "1"), (2, 0, "2"), (3, 0, "3"), (1, 1, "4"), (2, 1, "5"), (3, 1, "6"),
              (1, 2, "7"), (2, 2, "8"), (3, 2, "9"), (1, 3, "0"), (2, 3, ".")]
DIAL, DIAL_R, GRIP_R = (0.0500, 0.0170), 0.0122, 0.0094

# rear panel (x in instrument axes; seen from behind +x is on the left): antenna BNC, RS-232 port
# (DB-25), 12 V power, external speaker and record jacks, a blank label with a number
BNC = (0.045, 0.058)
DB25, DB25_WH = (-0.005, 0.050), (0.041, 0.011)
DCJ, EXTSP, RECJ = (0.022, 0.018), (-0.012, 0.018), (-0.032, 0.018)
LABEL, LABEL_WH = (-0.050, 0.056), (0.026, 0.015)

# a strip of masking tape with frequencies on the roof
TAPE_C, TAPE_WH, TAPE_ROT = (0.012, -0.045), (0.064, 0.024), -4.0

# "work" look - a loop of display frames (OZL_WorkFx frames): (frequency - seven characters, the dot
# after the third, a space is a blanked digit; S-meter bars; whether the search icon is lit).
# The receiver sits on 145.5250 and listens (the S-meter dances, the signal goes away), then the
# search steps through the bank channels - the frequencies from the tape on the roof - and catches
# 145.5250 again. Frame 0 is decal_lcd_on.png, the others decal_lcd_f01..f11.png (make_decals.py).
LCD_FRAMES = [("1455250", 11, False), ("1455250", 9, False), ("1455250", 12, False), ("1455250", 10, False),
              ("1455250", 6, False), ("1455250", 2, False), ("4339200", 0, True), (" 270650", 1, True),
              ("1455000", 0, True), ("4339200", 0, True), (" 270650", 0, True), ("1455125", 1, True)]
LCD_PERIOD = 0.15                       # seconds per frame: 12 frames - 1.8 s per loop
