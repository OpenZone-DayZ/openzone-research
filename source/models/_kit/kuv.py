"""UV unwrap: projection of faces by side into rectangles of one atlas, and a flat 0..1 unwrap
for the glass section.

A rectangle is keyed by part (uv_name) / region / side (+x, -y ...). Identical parts sharing a
uv_name take the atlas once. The texel density is found by binary search so that everything
fits; a region scale (Part.regions[i][2]) gives the region more or less room.
"""
import math

from mathutils import Vector

PLANE = {0: (1, 2), 1: (0, 2), 2: (0, 1)}   # normal axis -> projection axes (u, v)


def face_dir(n):
    ax = max(range(3), key=lambda i: abs(n[i]))
    return ax, (1 if n[ax] >= 0 else -1)


def face_key(p, f):
    rname = p.regions[f[p.reg]][0]
    ax, sg = face_dir(f.normal)
    return "%s/%s/%s%s" % (p.uv_name, rname, "+" if sg > 0 else "-", "xyz"[ax])


class Layout:
    """Atlas rectangles: key -> (x, y, w, h in px, projection bounds (a0, a1, b0, b1))."""

    def __init__(self, atlas=2048, gutter=6, pad=2, bottom_scale=0.25, scale_fn=None):
        self.atlas, self.gut, self.pad = atlas, gutter, pad
        self.bottom_scale = bottom_scale
        self.scale_fn = scale_fn
        self.rects = {}
        self.density = 0.0

    def face_scale(self, p, f, key):
        s = p.regions[f[p.reg]][2]
        if key.endswith("/-z"):
            s *= self.bottom_scale        # the bottom: nobody looks at it
        if self.scale_fn:
            s *= self.scale_fn(p, f, key)
        return s

    def build(self, parts):
        bounds, scale = {}, {}
        for p in parts:
            if p.section != "atlas":
                continue
            for f in p.bm.faces:
                k = face_key(p, f)
                ax, _ = face_dir(f.normal)
                ia, ib = PLANE[ax]
                b = bounds.setdefault(k, [1e9, -1e9, 1e9, -1e9])
                for v in f.verts:
                    co = v.co - p.uv_origin
                    b[0] = min(b[0], co[ia])
                    b[1] = max(b[1], co[ia])
                    b[2] = min(b[2], co[ib])
                    b[3] = max(b[3], co[ib])
                scale[k] = max(scale.get(k, 0.0), self.face_scale(p, f, k))
        lo, hi = 20.0, 6000.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if self._pack(bounds, scale, mid) is None:
                hi = mid
            else:
                lo = mid
        self.rects = self._pack(bounds, scale, lo)
        self.density = lo
        used = sum(w * h for x, y, w, h, _ in self.rects.values())
        print("atlas %d: %d rects, %.0f px/m, %.0f%% used" % (self.atlas, len(self.rects), lo,
                                                            100.0 * used / self.atlas ** 2))

    def _pack(self, bounds, scale, dens):
        A, G, P = self.atlas, self.gut, self.pad
        items = []
        for k, (a0, a1, b0, b1) in bounds.items():
            w = max(4, int(math.ceil((a1 - a0) * dens * scale[k])) + 2 * P)
            h = max(4, int(math.ceil((b1 - b0) * dens * scale[k])) + 2 * P)
            items.append((h, w, k))
        items.sort(reverse=True)
        x = y = G
        shelf = 0
        out = {}
        for h, w, k in items:
            if w + 2 * G > A:
                return None
            if x + w + G > A:
                x = G
                y += shelf + G
                shelf = 0
            if y + h + G > A:
                return None
            out[k] = (x, y, w, h, tuple(bounds[k]))
            x += w + G
            shelf = max(shelf, h)
        return out

    def lookup(self, key):
        if key in self.rects:
            return self.rects[key]
        # A face of a far LOD can look in a direction the near LOD does not have.
        base = "/".join(key.split("/")[:2])
        for k in self.rects:
            if k.startswith(base + "/"):
                return self.rects[k]
        part, region = key.split("/")[:2]
        for k in self.rects:
            if k.startswith(part + "/"):
                return self.rects[k]
        # A simplified far-LOD part missing from the near LOD: any part of the same region has
        # the same material, hence the same kind of texture.
        side = key.split("/")[2]
        for k in self.rects:
            if k.split("/")[1] == region and k.endswith("/" + side):
                return self.rects[k]
        for k in self.rects:
            if k.split("/")[1] == region:
                return self.rects[k]
        raise KeyError(key)

    def uv(self, key, co, ax):
        x, y, w, h, (a0, a1, b0, b1) = self.lookup(key)
        ia, ib = PLANE[ax]
        fa = min(max((co[ia] - a0) / max(a1 - a0, 1e-6), 0.0), 1.0)
        fb = min(max((co[ib] - b0) / max(b1 - b0, 1e-6), 0.0), 1.0)
        u = (x + self.pad + fa * (w - 2 * self.pad)) / self.atlas
        v_img = (y + self.pad + (1.0 - fb) * (h - 2 * self.pad)) / self.atlas   # top to bottom
        return u, v_img


def apply_uv(parts, layout, glass_frames=None):
    """Atlas parts follow the layout; glass parts get a flat 0..1 unwrap over their own frame
    (Part.glass_frame = (Frame, a0, a1, b0, b1)) or over their extents in the x-z plane."""
    for p in parts:
        uvl = p.bm.loops.layers.uv.get("UVMap") or p.bm.loops.layers.uv.new("UVMap")
        if getattr(p, "fixed_uv", False):
            continue                          # the generator set the UV (a part with a vanilla texture)
        if p.section != "atlas":
            gf = getattr(p, "glass_frame", None)
            for f in p.bm.faces:
                for lp in f.loops:
                    co = lp.vert.co
                    if gf:
                        fr, a0, a1, b0, b1 = gf
                        d = co - fr.o
                        a, b = d.dot(fr.u), d.dot(fr.v)
                    else:
                        a0, a1 = min(v.co.x for v in p.bm.verts), max(v.co.x for v in p.bm.verts)
                        b0, b1 = min(v.co.z for v in p.bm.verts), max(v.co.z for v in p.bm.verts)
                        a, b = co.x, co.z
                    u = (a - a0) / max(a1 - a0, 1e-6)
                    v = (b - b0) / max(b1 - b0, 1e-6)
                    lp[uvl].uv = (u, v)
            continue
        for f in p.bm.faces:
            k = face_key(p, f)
            ax, _ = face_dir(f.normal)
            for lp in f.loops:
                u, v = layout.uv(k, lp.vert.co - p.uv_origin, ax)
                lp[uvl].uv = (u, 1.0 - v)


def uv_hash(parts, layout):
    """Fingerprint of the unwrap: the atlas rectangles (key, position, size, projection bounds) and,
    per part, the name, section, triangle count and extents (rounded to 1e-5). The UV of a point is
    set by the rectangle of its side, so the same layout on the same parts gives the same unwrap.
    The UV of each corner is not hashed: a boolean difference (EXACT) can cut the same surface into
    different triangles from run to run (seen on the socket strip of m05) although the unwrap is the
    same. The same Blender and the same scripts give the same fingerprint on any machine; if it does
    not match, an atlas baked elsewhere does not fit this model."""
    import hashlib

    def r5(x):
        return "%.5f" % (round(x, 5) + 0.0)      # + 0.0: -0.0 and 0.0 give one string

    h = hashlib.sha256()
    h.update(("atlas %d\n" % layout.atlas).encode())
    for k in sorted(layout.rects):
        x, y, w, hh, b = layout.rects[k]
        h.update(("%s %d %d %d %d %s\n" % (k, x, y, w, hh, " ".join(r5(c) for c in b))).encode())
    for p in parts:
        tris = sum(len(f.verts) - 2 for f in p.bm.faces)
        box = [r5(f(v.co[i] for v in p.bm.verts)) for i in range(3) for f in (min, max)] if p.bm.verts else []
        h.update(("%s %s %d %s\n" % (p.name, p.section, tris, " ".join(box))).encode())
    return h.hexdigest()
