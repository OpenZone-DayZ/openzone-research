"""Shared M04 numbers for make_decals.py (system Python) and build_m04.py (Blender): the recorder tape,
the pen and the "work" frames.

The recorder in "work": the pen writes while the tape creeps down. The pen is one bone ozl_pen with
three translations on it from three sources (ozl_pen, ozl_pen_2, ozl_pen_3): translations of one
bone add up in model.cfg (the rotation of the OpenZone_StorageCases box lid is assembled the same
way from pieces on two sources). Each source is driven by OZL_WorkFx wobble: phase = mid + amp *
sin(2 pi t / period), period = CYCLE / n. The pen is a sum of three sines with multiple frequencies
(n = 2, 5, 11): the curve is irregular, like a radiometer record with statistical scatter, and
repeats only after CYCLE (odd 1, 3, 7 gave a square wave - the Fourier series of a rectangular
wave). Over CYCLE the tape (the frames of its texture, OZL_WorkFx frames) moves by TAPE_RUN: frame k
shows the tape at the middle of its time t_k = (k + 1/2) * CHART_SEC, with the trace under the pen
line: the point d below the pen was written at t_k - d / v, v = TAPE_RUN / CYCLE. Over CYCLE the tape
moves by a whole number of grid cells (50 mm) and perforation steps (10 mm), so the seam between the
last frame and the first is invisible, and the curve in the window (204 mm below the pen) is almost
the whole loop, so the repeat is not noticeable by eye.

Time in OZL_WorkFx is a count of 0.05 s ticks, the same for the pen and the frames (they run in
step). A frame changes once at least a period has accumulated: 0.07 -> 2 ticks = 0.1 s, 0.22 -> 5
ticks = 0.25 s (exactly 0.1 or 0.25 could become an extra tick on the boundary because of float
rounding). In the config period = *_CFG, the frame length is *_SEC.
"""
import math

TICK = 0.05

# tape in the recorder window (m): tape width, visible height (from the window bottom to the scale), recording field
CHART_W, CHART_H = 0.280, 0.234
FIELD_X0, FIELD_W = 0.015, 0.250   # left edge of the field from the tape edge, field width (250 mm, KSP4)
PEN_D = 0.030                      # pen line below the top of the visible tape
SCALE_W = 0.340                    # scale above the window (build_m04 SCALE): 0..100 exactly above the field

CHART_FRAMES = 72
CHART_CFG, CHART_SEC = 0.07, 0.10  # period in class OZL_Work and the real frame length (2 ticks)
CYCLE = CHART_FRAMES * CHART_SEC   # 7.2 s: tape and pen loop
TAPE_RUN = 0.200                   # the tape moves this far per CYCLE (27.8 mm/s, 2.8 mm per frame)

# pen: (source, mid, amp, n, travel D, m) - the contribution to the pen position from the field zero:
# D * (mid + amp * sin(2 pi n t / CYCLE)); at rest all phases are 0 - the pen is at the field zero
PEN = (
    ("ozl_pen", 0.412, 0.16, 2, FIELD_W),      # main travel: 40 mm each way, period 3.6 s
    ("ozl_pen_2", 0.5, 0.5, 5, 0.032),         # 16 mm, 1.44 s
    ("ozl_pen_3", 0.5, 0.5, 11, 0.012),        # 6 mm, 0.65 s; on average the pen is at the middle of the field
)
PEN_ANIM_PERIOD = {"ozl_pen": 0.15, "ozl_pen_2": 0.1, "ozl_pen_3": 0.1}


def pen_period(n):
    return CYCLE / n


def pen_x(t):
    """Pen at work time t (s), m from the field zero."""
    return sum(d * (mid + amp * math.sin(2 * math.pi * n * t / CYCLE)) for _, mid, amp, n, d in PEN)


def frame_time(k):
    """Middle of the time of tape frame k, s."""
    return (k + 0.5) * CHART_SEC


# gas-discharge digits of the analyzer: frame 0 is a reset, then the count grows for 16 s (64 frames of 0.25 s)
NIXIE_FRAMES = 64
NIXIE_CFG, NIXIE_SEC = 0.22, 0.25

# chamber lid: open at rest, closes in "work" (OZL_WorkFx pose), opens afterwards
LID_PERIOD = 1.8
