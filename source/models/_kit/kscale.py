"""Platform scale base: a floor-standing mobile dial scale of the Soviet pattern.

Sized after the RP-150Ts13 (max load 150 kg): platform 630 x 800 mm, height 1680 mm, mass up to
185 kg (from its specification table). The design follows photos of the RP-2Ts13M of the same
Ts13 series: a frame on two wheels at the back and two supports at the front, a platform with a
ribbed deck, a lever box on the frame at the back, a column rising from it, and on top a round
dial head with glass in a chrome ring held by screws. The head is 0.41 m in diameter over the
ring (dial 0.36 m); no datasheet size of the head exists for the RP-150Ts13, so it is taken from
photo proportions (the head is slightly narrower than the frame) and is unverified.

    parts = kscale.platform_scale(M, spec, needle_group="ozl_work")
    lay = kscale.layout()     # where things are - for the model's props

The model defines its own regions: regions=dict(body=..., dial=...) over DEFAULT_REGIONS. The
dial scale (the dial sticker) and the colors belong to the model; only the shape is here. The
needle is its own group (a bone), points up at zero, and rotates around an axis pointing to the
player through layout()["pivot"].

Blender axes: X - width, Y - depth (the front at -Y), Z - up. The column is at the back (+Y),
the dial face looks forward, over the platform.
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g

# --- dimensions, m --------------------------------------------------------------------------
W, D, H = 0.63, 0.80, 1.68                       # platform (frame) and the height from the datasheet
X0, X1, Y0, Y1 = -W / 2, W / 2, -D / 2, D / 2
FOOT_H = 0.02                                    # front supports
FRAME_Z = (FOOT_H, 0.075)                        # frame made of channel steel
RAIL = 0.05
DECK = (-0.300, 0.300, Y0 + 0.008, 0.225, 0.078, 0.120)   # platform: x0, x1, y0, y1, z0, z1
HOUSING = (-0.170, 0.170, 0.235, Y1, 0.0, 0.320)          # lever box
COLUMN = (-0.050, 0.050, 0.270, 0.370, 0.320, 1.220)
HEAD_C = (0.0, 0.320, H - 0.205)                 # head center: the top of the ring is at height H
HEAD_R, RING_R0, DIAL_R = 0.195, 0.180, 0.182    # drum, inner radius of the ring, dial
RING_R1 = 0.205
RING_Y = (0.236, 0.262)
DIAL_Y = 0.249                                   # dial face
GLASS_Y = 0.240
NEEDLE_Y = (0.2440, 0.2455)
NEEDLE_L = 0.165
DRUM_Y = (0.255, 0.385)
WHEEL_R, WHEEL_W, WHEEL_Y = 0.055, 0.030, 0.330
ADJUST = (0.105, HOUSING[2], 0.215)              # zero adjustment screw on the box face

DEFAULT_REGIONS = dict(body="sc_body", frame="sc_frame", deck="sc_deck", chrome="chrome", dial="sc_dial",
                       needle="sc_needle", inner="sc_inner", rubber="rubber", steel="steel")


def layout():
    """Where things are: for the model's props and memory points."""
    return dict(deck=DECK, housing=HOUSING, column=COLUMN, head_c=HEAD_C, head_r=RING_R1, dial_r=DIAL_R,
                dial_y=DIAL_Y, glass_y=GLASS_Y, needle_y=sum(NEEDLE_Y) / 2, pivot=(HEAD_C[0], HEAD_C[2]),
                needle_l=NEEDLE_L, adjust=ADJUST, top=H, bounds=(X0 - 0.035, X1 + 0.035, Y0, Y1, 0.0, H))


def ring(part, center, r_in, r_out, y0, y1, sides):
    """Flat ring (rim) around the y axis: a rectangular section r_in..r_out x y0..y1."""
    bm = part.bm
    cx, cz = center
    rings = []
    for k in range(sides):
        a = 2 * math.pi * k / sides
        c, s = math.cos(a), math.sin(a)
        rings.append([bm.verts.new(Vector((cx + r * c, y, cz + r * s)))
                      for r, y in ((r_in, y0), (r_out, y0), (r_out, y1), (r_in, y1))])
    new = []
    for k in range(sides):
        r0, r1 = rings[k], rings[(k + 1) % sides]
        for q in range(4):
            new.append(bm.faces.new([r0[q], r0[(q + 1) % 4], r1[(q + 1) % 4], r1[q]]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def platform_scale(M, spec, needle_group, regions=None, adjust=True):
    """The whole scale: frame, supports, wheels, platform, box, column, head with a ring, a dial,
    glass (the glass section, near LOD only) and a needle (group needle_group). adjust=False -
    without the adjustment screw (the model adds its own)."""
    R = dict(DEFAULT_REGIONS, **(regions or {}))
    P = M.part
    lod, sd = spec["lod"], spec["sides"]
    bev = dict(r=0.004, seg=1) if lod == 0 else {}
    parts = []
    # frame and supports
    fr = P("sc_frame", R["frame"])
    if lod < 2:
        z0, z1 = FRAME_Z
        g.box(fr, X0, X1, Y0, Y0 + RAIL, z0, z1)
        for xa, xb in ((X0, X0 + RAIL), (X1 - RAIL, X1)):
            g.box(fr, xa, xb, Y0 + RAIL, HOUSING[2] + 0.02, z0, z1)
        for x in (X0 + 0.045, X1 - 0.045):
            g.cyl(fr, (x, Y0 + 0.03, FOOT_H / 2), "z", 0.024, FOOT_H, (10, 6)[lod])
        inner = P("sc_pan", R["inner"])
        g.box(inner, X0 + RAIL, X1 - RAIL, Y0 + RAIL, HOUSING[2], z0, z1 - 0.004)
        parts.append(inner)
    else:
        g.box(fr, X0, X1, Y0, HOUSING[2], 0.0, FRAME_Z[1])
    parts.append(fr)
    # Wheels at the back: on the frame sides, the axle runs through the box.
    wh = P("sc_wheels", R["rubber"])
    for s in (-1, 1):
        g.cyl(wh, (s * (X1 + 0.003 + WHEEL_W / 2), WHEEL_Y, WHEEL_R), "x", WHEEL_R, WHEEL_W, (16, 10, 6)[lod])
    parts.append(wh)
    if lod < 2:
        ax = P("sc_axle", R["steel"])
        g.cyl(ax, (0.0, WHEEL_Y, WHEEL_R), "x", 0.012, W + 2 * WHEEL_W + 0.03, (8, 6)[lod])
        if lod == 0:
            for s in (-1, 1):
                g.cyl(ax, (s * (X1 + WHEEL_W + 0.008), WHEEL_Y, WHEEL_R), "x", 0.022, 0.012, 8)
        parts.append(ax)
    # platform: ribbed deck
    dk = P("sc_deck", R["deck"])
    g.box(dk, *DECK, **bev)
    parts.append(dk)
    # lever box and column
    bd = P("sc_housing", R["body"])
    g.box(bd, *HOUSING, **(dict(r=0.018, seg=2) if lod == 0 else {}))
    g.box(bd, *COLUMN, **(dict(r=0.010, seg=1) if lod == 0 else {}))
    if lod == 0:
        # inspection door on the box face and the column flange
        g.box(bd, -0.120, 0.060, HOUSING[2] - 0.004, HOUSING[2] + 0.01, 0.060, 0.170, r=0.003, seg=1)
        g.box(bd, COLUMN[0] - 0.02, COLUMN[1] + 0.02, COLUMN[2] - 0.02, COLUMN[3] + 0.02, COLUMN[4],
              COLUMN[4] + 0.03, r=0.004, seg=1)
    # neck and drum of the head
    hc = HEAD_C
    g.cyl(bd, (hc[0], hc[1], COLUMN[5] + 0.03), "z", 0.050, 0.08, (16, 10, 6)[lod])
    hs = (32, 20, 12)[lod]
    g.cyl(bd, (hc[0], (DRUM_Y[0] + DRUM_Y[1]) / 2, hc[2]), "y", HEAD_R, DRUM_Y[1] - DRUM_Y[0], hs)
    if lod < 2:
        g.cyl(bd, (hc[0], DRUM_Y[1] + 0.006, hc[2]), "y", HEAD_R - 0.012, 0.012, hs)
    parts.append(bd)
    # chrome ring with screws
    ch = P("sc_ring", R["chrome"])
    if lod < 2:
        ring(ch, (hc[0], hc[2]), RING_R0, RING_R1, RING_Y[0], RING_Y[1], hs)
        if lod == 0:
            for k in range(8):
                a = 2 * math.pi * (k + 0.5) / 8
                g.cyl(ch, (hc[0] + 0.193 * math.cos(a), RING_Y[0] - 0.002, hc[2] + 0.193 * math.sin(a)), "y",
                      0.0045, 0.004, 6)
    else:
        g.cyl(ch, (hc[0], (RING_Y[0] + DRUM_Y[0]) / 2, hc[2]), "y", RING_R1, DRUM_Y[0] - RING_Y[0], hs)
    parts.append(ch)
    # dial, glass
    dl = P("sc_dial", R["dial"])
    g.cyl(dl, (hc[0], (DIAL_Y + DRUM_Y[0]) / 2 + 0.0005, hc[2]), "y", DIAL_R, DRUM_Y[0] - DIAL_Y + 0.001, hs)
    parts.append(dl)
    if lod == 0:
        gl = P("sc_glass", R["steel"], section="glass")
        g.cyl(gl, (hc[0], GLASS_Y, hc[2]), "y", RING_R0 + 0.001, 0.0012, hs)
        parts.append(gl)
    # Needle: up at zero; a trapezoid blade, a counterweight, an axis cap.
    nd = P("sc_needle", R["needle"], group=needle_group)
    f = g.Frame((hc[0], NEEDLE_Y[0], hc[2]), (0, 0, 1), (1, 0, 0), (0, 1, 0))
    g.prism(nd, [(-0.032, -0.0045), (NEEDLE_L, -0.0008), (NEEDLE_L, 0.0008), (-0.032, 0.0045)], (0, 1),
            0.0, NEEDLE_Y[1] - NEEDLE_Y[0], frame=f)
    if lod < 2:
        g.cyl(nd, (hc[0], (NEEDLE_Y[0] + NEEDLE_Y[1]) / 2, hc[2] - 0.036), "y", 0.011, NEEDLE_Y[1] - NEEDLE_Y[0],
              (12, 8)[lod])
        g.cyl(nd, (hc[0], NEEDLE_Y[0] - 0.0015, hc[2]), "y", 0.008, 0.003, (10, 6)[lod])
    parts.append(nd)
    # zero adjustment screw: a wing screw on the box face
    if adjust and lod < 2:
        ad = P("sc_adjust", R["steel"])
        x, y, z = ADJUST
        g.cyl(ad, (x, y - 0.012, z), "y", 0.008, 0.024, 8)
        g.box(ad, x - 0.022, x + 0.022, y - 0.028, y - 0.020, z - 0.006, z + 0.006)
        parts.append(ad)
    return parts
