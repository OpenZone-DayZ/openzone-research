"""Vanilla items as proxies in our models: a catalog of paths, the extents of the near LOD taken
from the ODOL, and placing an item on a table, shelf or board.

The engine itself draws the proxy of a vanilla p3d in our MLOD with the native textures and LODs,
provided the file has NO Proxy<name> class in CfgNonAIVehicles. We neither read nor copy the
vanilla geometry (ODOL is not decompiled): from the file we take only the extents of the near
LOD - the six numbers of the LOD header (bMin, bMax) - so that an item lies on a table instead of
sinking into it, and so that the preview without baking shows a box of its size in its place
(vanilla has no shape of its own in Blender).

Item axes are the p3d axes: +Y is up (for a tool - along the handle to the working end), +Z is
forward, +X is sideways. A proxy rotation is given by two Blender vectors: up - where the item's
+Y points, fwd - where its +Z points (kexport.proxy_points); the item's +X is then fwd x up (the
Blender -> p3d transition is a reflection, kexport.conv). Flat items (paper, rags, a cleaning
kit, an electrician's case) lie in the item's X-Y plane - their normal is +Z: to put one on a
table, fwd = up (0, 0, 1).

    import kvanilla as kv
    DECOR = [kv.put("pliers", (x, y, ZT), up=(1, 0, 0), fwd=(0, 0, 1), lods=(0, 1))]
    kmodel.Model(..., decor=DECOR)
"""
import math
import os
import struct

import ksettings

P_ROOT = ksettings.PDRIVE

# short name -> p3d path from P:\ without the extension (the items that can be proxied)
ITEMS = {
    "pliers": r"dz\gear\tools\Pliers",
    "screwdriver": r"dz\gear\tools\Screwdriver",
    "wrench": r"dz\gear\tools\Wrench",
    "lugwrench": r"dz\gear\tools\Lug_wrench",
    "hammer": r"dz\gear\tools\Hammer",
    "hacksaw": r"dz\gear\tools\hacksaw",
    "handsaw": r"dz\gear\tools\handsaw",
    "crowbar": r"dz\gear\tools\Crowbar",
    "pipe": r"dz\gear\tools\metal_pipe",
    "electrickit": r"dz\gear\tools\electronicCase",
    "epoxy": r"dz\gear\tools\epoxy_putty",
    "flashlight": r"dz\gear\tools\flashlight",
    "cleaningkit": r"dz\gear\tools\cleaning_kit_wood",
    "sewingkit": r"dz\gear\tools\sewing_kit",
    "whetstone": r"dz\gear\tools\whetstone",
    "pen": r"dz\gear\tools\Pen",
    "cassette": r"dz\gear\tools\cassette",
    # Weapon parts without a Proxy<name> class. Compensators, bayonets, the PSO-1 and AKM magazines
    # do have such a class, so they are not drawn in a foreign model. Sights (PSO-6, "Kobra") have no
    # such class but are drawn white: their texture comes from the config (hiddenSelectionsTextures)
    # and a proxy has none - so they are not in the catalog; the PSO on m23 is a custom shape that
    # references the sight texture by path.
    # The parts below are drawn with their textures and are laid flat (kv.flat).
    "akstock": r"dz\weapons\attachments\support\buttstock_ak_folding",
    "akrail": r"dz\weapons\attachments\support\handguard_ak_rail",
    "pbsupp": r"dz\weapons\attachments\muzzle\suppressor_pb6p9",
    "sksclip": r"dz\weapons\attachments\magazine\clip_762x39_10rnd",
    "rpkmag": r"dz\weapons\attachments\magazine\magazine_ak74_45rnd",
    "ammobox762": r"dz\weapons\ammunition\762x39_20RoundBox",
    "rounds762": r"dz\weapons\ammunition\762x39_LooseRounds",
    "radio": r"dz\gear\radio\unitra_wilga",
    "battery9v": r"dz\gear\consumables\9v_battery",
    "batteryd": r"dz\gear\consumables\BatteryD",
    "ducttape": r"dz\gear\consumables\DuctTape",
    "nailbox": r"dz\gear\consumables\Nails_box",
    "rags": r"dz\gear\consumables\Rags",
    "oilbottle": r"dz\gear\consumables\oil_bottle",
    "paper": r"dz\gear\consumables\Paper",
    "punchedcard": r"dz\gear\consumables\PunchedCard",
    "matchbox": r"dz\gear\consumables\Matchbox",
    "vodka": r"dz\gear\drinks\VodkaBottles",
    "waterbottle": r"dz\gear\drinks\WaterBottle",
    "foodcan": r"dz\gear\food\FoodCan_250g",
    "sardines": r"dz\gear\food\can_sardines",
    "thermometer": r"dz\gear\medical\med_tmeter",
    "gp5": r"dz\characters\masks\GP5GasMask_g",
    "gasmask": r"dz\characters\masks\GasMask_g",
    "gp5filter": r"dz\characters\masks\GP5GasMask_filter",
    "ssh68": r"dz\characters\headgear\Ssh68Helmet_g",
    "mich": r"dz\characters\headgear\HelmetMich_g",
}

_BOX = {}
# A remote bake machine has no drive P:, so it takes the extents from this file instead (printed by
# kmodel --uv-hash on the machine that has P: and placed next to this module in the kit snapshot);
# the machine that has P: does not have the file and does not need it.
BOX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vanilla_boxes.json")


def path(key):
    """Proxy path in the MLOD: \\dz\\...\\name without .p3d."""
    return "\\" + ITEMS.get(key, key).lstrip("\\")


def _lod_extents(buf, after, n):
    """Starts and ends of the LODs in the file: two uint[n] arrays one after another; the LODs
    follow the header and abut each other - otherwise random header numbers pass for arrays."""
    size = len(buf)
    for off in range(after, min(size - 8 * n, after + 400000)):
        s = struct.unpack_from("<%dI" % n, buf, off)
        e = struct.unpack_from("<%dI" % n, buf, off + 4 * n)
        if all(off < a < b <= size for a, b in zip(s, e)):
            iv = sorted(zip(s, e))
            if all(iv[i][1] == iv[i + 1][0] for i in range(n - 1)):
                return list(zip(s, e))
    raise ValueError("LOD extents not found")


def box(key):
    """Extents of the item's near visual LOD in its p3d axes: ((x0, y0, z0), (x1, y1, z1)), m.
    The ODOL v5x LOD header: proxies (name, 4x3 matrix, four uints), two skeleton arrays, the
    vertex count, the area, two flags - and then bMin, bMax."""
    if key in _BOX:
        return _BOX[key]
    fn = os.path.join(P_ROOT, ITEMS.get(key, key).lstrip("\\") + ".p3d")
    if not os.path.exists(fn) and os.path.exists(BOX_FILE):
        import json
        with open(BOX_FILE, encoding="utf-8") as fh:
            saved = json.load(fh)
        if key in saved:
            _BOX[key] = tuple(tuple(v) for v in saved[key])
            return _BOX[key]
    buf = open(fn, "rb").read()
    if buf[:4] != b"ODOL":
        raise ValueError("not ODOL: " + fn)
    n = struct.unpack_from("<I", buf, 8)[0]
    res = struct.unpack_from("<%df" % n, buf, 12)
    ext = _lod_extents(buf, 12 + 4 * n, n)
    o = ext[[i for i, r in enumerate(res) if r < 1000.0][0]][0]
    nprox = struct.unpack_from("<I", buf, o)[0]
    o += 4
    for _ in range(nprox):
        o = buf.index(b"\0", o) + 1 + 48 + 16
    n1 = struct.unpack_from("<I", buf, o)[0]
    o += 4 + 4 * n1
    n2 = struct.unpack_from("<I", buf, o)[0]
    o += 4
    for _ in range(n2):
        o += 4 + 4 * struct.unpack_from("<I", buf, o)[0]
    o += 16                                                   # vertices, area, flags
    lo, hi = struct.unpack_from("<3f", buf, o), struct.unpack_from("<3f", buf, o + 12)
    # A LOD with proxies (a blowtorch with a gas cylinder) includes the proxy triangle in its extents - 2 m and 1 m.
    if not all(-1.0 < a <= b < 1.0 for a, b in zip(lo, hi)):
        raise ValueError("LOD box of %s not usable (proxies: %d): %s %s" % (fn, nprox, lo, hi))
    _BOX[key] = (lo, hi)
    return _BOX[key]


def _norm(v):
    m = math.sqrt(sum(c * c for c in v))
    return tuple(c / m for c in v)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def axes(up, fwd):
    """Item axes in Blender: the item's (+X, +Y, +Z); fwd is straightened to a right angle to up."""
    u = _norm(up)
    f = _norm(tuple(a - _dot(fwd, u) * b for a, b in zip(fwd, u)))
    return _cross(f, u), u, f


def to_blender(local, origin, up, fwd):
    X, U, F = axes(up, fwd)
    return tuple(origin[i] + local[0] * X[i] + local[1] * U[i] + local[2] * F[i] for i in range(3))


def corners(key, origin, up, fwd):
    """The eight corners of the item's extents in Blender (the placeholder box of the preview)."""
    lo, hi = box(key)
    return [to_blender((x, y, z), origin, up, fwd) for x in (lo[0], hi[0]) for y in (lo[1], hi[1])
            for z in (lo[2], hi[2])]


def put(key, at, up=(0, 0, 1), fwd=(0, -1, 0), normal=(0, 0, 1), lods=(0, 1), lift=0.0):
    """Place an item: the middle of its extents is above the point at (along the support plane),
    its bottom (along normal - outward from the support) is on the plane through at, plus lift.
    Returns a decor entry for kmodel.Model: (path, proxy origin, up, fwd, LODs, key). A table is
    normal (0, 0, 1); a board facing -Y is (0, -1, 0)."""
    lo, hi = box(key)
    c = tuple((a + b) / 2 for a, b in zip(lo, hi))
    o0 = tuple(at[i] - (to_blender(c, (0, 0, 0), up, fwd)[i]) for i in range(3))
    n = _norm(normal)
    low = min(_dot(tuple(q[i] - at[i] for i in range(3)), n) for q in corners(key, o0, up, fwd))
    origin = tuple(o0[i] + (lift - low) * n[i] for i in range(3))
    return (path(key), origin, tuple(up), tuple(fwd), tuple(lods), key)


def flat(deg):
    """Lies flat (the item's X-Y plane is on the table): up runs along the table at angle deg from
    Blender +X, fwd points up. For a tool lying on its side: the handle (the item's +Y) points toward deg."""
    a = math.radians(deg)
    return dict(up=(math.cos(a), math.sin(a), 0.0), fwd=(0.0, 0.0, 1.0))


def hung(deg=90.0, face=(0.0, -1.0, 0.0)):
    """Hangs on a board facing face: the item's X-Y plane runs along the board, the item's +Y is at
    angle deg from Blender +X in the board plane (90 - up, -90 - down), the item's +Z points toward the person."""
    a = math.radians(deg)
    return dict(up=(math.cos(a), 0.0, math.sin(a)), fwd=tuple(face), normal=tuple(face))
