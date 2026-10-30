"""Geometry shared by build_m26.py and make_decals.py: the armor plate, hits on it, misses on the
frame and on the bullet-trap shield, and the face of the registration unit. Blender axes: x is
width, y is depth (the face looks to -y), z is up, meters. Pure Python, so both Blender and the
system Python with Pillow can import it.
"""
# plate 0.25 x 0.30 m, 8 mm thick (between the S 222 x 298 and M 241 x 318 mm sizes of SAPI/ESAPI plates)
PX0, PX1, PZ0, PZ1 = -0.125, 0.125, 0.90, 1.20
PY0, PY1 = 0.0, 0.008
PC = ((PX0 + PX1) / 2, (PZ0 + PZ1) / 2)

# hits on the plate: (x, z, crater radius). Six shots of a series, none closer than ~50 mm to an edge
# or to each other, as in plate test standards; the index is the shot order in the series
HITS = [(-0.062, 1.128, 0.0065), (0.058, 1.137, 0.0070), (-0.004, 1.052, 0.0075),
        (-0.066, 0.968, 0.0065), (0.061, 0.975, 0.0070), (-0.002, 0.944, 0.0060)]
PIERCED = (5,)                                   # pierced through: dark hole, mark on the shield

# misses on the frame (x, z, radius) - on the angle faces (y = FY) and on the mounting frames
FY = 0.020
FRAME_HITS = [(-0.31, 0.822, 0.006), (0.37, 0.815, 0.005), (-0.20, 1.33, 0.006), (0.27, 1.335, 0.005),
              (-0.137, 1.25, 0.005), (0.14, 0.87, 0.005)]

# bullet-trap shield (plywood on the box face, y = BY): holes from pierced shots and from misses past the plate
BY = 0.094
BACKER_HITS = [(-0.004, 0.951, 0.006), (-0.17, 1.20, 0.005), (0.15, 1.23, 0.005), (-0.16, 0.90, 0.005),
               (0.18, 0.93, 0.004), (0.02, 1.235, 0.005), (-0.02, 0.87, 0.004)]

# face of the registration unit: a is world x, b is height from the case bottom; the case is 0.28 x 0.12,
# the face before the chamfer is 0.10. Top: the display and a needle gauge of the frame signal level;
# bottom: two channel toggles in guards, a threshold knob with a scale ring, a mains lamp; below them
# a strip of marks (decal)
UNIT_A = (0.05, 0.33)
DISP = (0.075, 0.225, 0.050, 0.093)              # display a0 a1 b0 b1
# display frames in "operation": a series of six shots, six stages per shot - ready, two counting
# frames, result, two hold frames (make_decals.py draws them, build_m26.py assigns them to the panel)
SCREEN_SHOTS, SCREEN_STAGES = 6, 6
SCREEN_FRAMES = SCREEN_SHOTS * SCREEN_STAGES
METER = (0.244, 0.318, 0.046, 0.097)             # gauge body
METER_WIN = (0.251, 0.311, 0.052, 0.090)         # scale window
METER_PIVOT = (0.281, 0.055)                     # needle pivot
METER_R = 0.029                                  # scale arc radius
METER_REST, METER_SWEEP = 135.0, 90.0            # needle at zero is 135 degrees from +a, the scale spans 90 degrees
TOGS, TOG_B = (0.090, 0.135), 0.024              # toggles
KNOB, KNOB_R = (0.192, 0.024), 0.011             # threshold knob
LAMP = (0.298, 0.026)                            # mains lamp
PANEL = (0.06, 0.32, 0.004, 0.044)               # strip of marks (decal_unit decal)
