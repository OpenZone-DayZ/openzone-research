"""KSP4 recorder tape of M06 - numbers shared by make_decals.py (system Python) and build_m06.py
(Blender): the tape, the pen and the "work" frames. The design is the same as in M04 (layout.py of
m04_anomaly_analyzer).

In "work" the pen writes while the tape creeps down. The pen is one bone ozl_pen with three
translations on it from three sources (ozl_pen, ozl_pen_2, ozl_pen_3): translations of one bone add
up in model.cfg. Each source is driven by OZL_WorkFx wobble: phase = mid + amp * sin(2 pi t /
period), period = CYCLE / n. The pen is a sum of three sines of multiple frequencies (n = 1, 5, 12 -
not those of M04): a slow drift of the board output with oscillations; it repeats only after CYCLE.
Over CYCLE the tape (the frames of its texture, OZL_WorkFx frames) moves by TAPE_RUN: frame k shows
the tape at the middle of its time t_k = (k + 1/2) * CHART_SEC, with the trace under the pen line:
the point d below the pen was written at t_k - d / v, v = TAPE_RUN / CYCLE. Over CYCLE the tape moves
by a whole number of grid cells (50 mm) and perforation steps (10 mm), so the seam between the last
frame and the first is invisible.

Time in OZL_WorkFx is a count of 0.05 s ticks, the same for the pen and the frames (they run in
step). A frame changes once at least a period has accumulated: 0.07 -> 2 ticks = 0.1 s (exactly 0.1
could become an extra tick on the boundary because of float rounding). In the config period =
CHART_CFG, the frame length is CHART_SEC.
"""
import math

# tape in the window (m): width, visible height (from the window bottom to the scale), recording
# field; the pen line is below the top
CHART_W, CHART_H = 0.280, 0.234
FIELD_X0, FIELD_W = 0.015, 0.250
PEN_D = 0.030
SCALE_W = 0.340                    # scale above the window (build_m06 SCALE): 0..100 exactly above the field

CHART_FRAMES = 72
CHART_CFG, CHART_SEC = 0.07, 0.10
CYCLE = CHART_FRAMES * CHART_SEC   # 7.2 s: tape and pen loop
TAPE_RUN = 0.200                   # the tape moves this far per CYCLE (27.8 mm/s, 2.8 mm per frame)

# pen: (source, mid, amp, n, travel D, m) - the contribution to the pen position from the field zero:
# D * (mid + amp * sin(2 pi n t / CYCLE)); at rest all phases are 0 - the pen is at the field zero
PEN = (
    ("ozl_pen", 0.432, 0.128, 1, FIELD_W),     # drift: 32 mm each way, period 7.2 s
    ("ozl_pen_2", 0.5, 0.5, 5, 0.024),         # 12 mm, 1.44 s
    ("ozl_pen_3", 0.5, 0.5, 12, 0.010),        # 5 mm, 0.6 s; on average the pen is at the middle of the field
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
