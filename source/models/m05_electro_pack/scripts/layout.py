"""M05: sizes shared by build_m05.py (Blender) and make_decals.py (system Python + Pillow): the scales
of the supply's pointer meters (the needle is its own part and bone, it is not in the image) and the
EOP screen. Pure Python, no bpy.
"""
# meter scale window, m, and an image of the same proportions
DIAL_W, DIAL_H = 0.072, 0.050
DIAL_PX = (360, 250)
# needle axis - fractions of the window: x left to right, y top to bottom (the axis is near the bottom edge, as in
# the M4200)
PIVOT = (0.5, 0.92)
ARC_R = 0.70                      # scale arc radius - fraction of the window height
NEEDLE_R = 0.76                   # needle from the axis to the tip - fraction of the window height
NEEDLE_TAIL = 0.12                # tail behind the axis
# scale arc: from zero (left) to the end (right), degrees counter-clockwise from +x; the needle at rest is on zero
ARC_DEG = (130.0, 50.0)
SWEEP_DEG = ARC_DEG[0] - ARC_DEG[1]
# meters: scale digits and the needle's "life" at work (OZL_WorkFx wobble: phase = mid + amp sin(2 pi t / period))
METERS = {
    "v": dict(labels=["0", "10", "20", "30"], minor=5, mid=0.42, amp=0.012, period=2.3),
    "a": dict(labels=["0", "1", "2", "3"], minor=5, mid=0.21, amp=0.045, period=0.65),
}
# 18 mm EOP: the working field of the screen; phosphor glow frames ("snow")
EOP_SCREEN_R = 0.009
EOP_FRAMES = 8
EOP_PX = 128
# rosin stains and solder drops on the bench sheet where the soldering station stands (slot 2): field, m
ROSIN_SIZE = (0.30, 0.28)
ROSIN_PX = (600, 560)
