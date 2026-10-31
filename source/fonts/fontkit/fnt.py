"""Enfusion/DayZ .fnt reader/writer.

IFF container (chunk ids and sizes BIG-endian, payload LITTLE-endian):

  "FORM" u32be size(of everything after this field) "FNT2"|"FNT3"|"FNT5"
  then chunks, any order (vanilla FNT3: GLPS TCRD KERN HEAD; 7segment: HEAD first):
  "HEAD" u32be n  (FNT3/FNT5; FNT2 has none)
        u32 len, char name[len] (NUL included), u16 pixel size, u8 zero[6]
        FNT5 adds: u8 ?, u32 ?, f32 ?, f32 em, u16 sdf range, u8 ?, u8 ?, f32 ?
  "GLPS" u32be n
        u8 junk[8] (an uninitialised pointer in the exporter -- ignore)
        u32 glyph count, u32 range count
        ranges: FNT2/FNT3 {u16 first, u16 count}; FNT5 {u32 first, u16 count, u16 junk}
        glyph i <-> i-th code point when the ranges are expanded in order
  "TCRD" u32be n   one record per glyph, glyph order
        FNT3 (12 bytes): u16 x, u16 y, u16 w, u16 h, s16 pre, s16 post
        (pixel rectangle in the atlas, cell is full line height;
         advance = pre + w + post)
        FNT2 (8 bytes):  u16 x, u16 y, u16 w, u16 h (monospace cells)
  "KERN" u32be n   FNT3: 8-byte records {u16 left cp, u16 right cp, s32 dx px}
"""
import struct


class Glyph:
    __slots__ = ("cp", "x", "y", "w", "h", "pre", "post", "raw")

    def __init__(self, cp, x=0, y=0, w=0, h=0, pre=0, post=0, raw=None):
        self.cp, self.x, self.y, self.w, self.h, self.pre, self.post = cp, x, y, w, h, pre, post
        self.raw = raw

    @property
    def advance(self):
        return self.pre + self.w + self.post

    def __repr__(self):
        return "Glyph(U+%04X %r xywh=%d,%d,%d,%d pre=%d post=%d)" % (
            self.cp, chr(self.cp), self.x, self.y, self.w, self.h, self.pre, self.post)


class Font:
    def __init__(self):
        self.kind = "FNT3"
        self.chunk_order = ["GLPS", "TCRD", "KERN", "HEAD"]
        self.name = ""
        self.size = 0
        self.head_tail = b"\0" * 6      # FNT3: 6 zero bytes after size; FNT5: more
        self.glps_junk = b"\0" * 8
        self.glyphs = []                # in file order
        self.kern = []                  # [(left_cp, right_cp, dx)]
        self.has_head = True
        self.extra_chunks = {}

    def by_cp(self):
        return {g.cp: g for g in self.glyphs}

    @property
    def line_height(self):
        hs = [g.h for g in self.glyphs if g.h]
        return max(hs) if hs else 0


def iff_chunks(buf):
    if buf[:4] != b"FORM":
        raise ValueError("not an IFF FORM")
    total = struct.unpack(">I", buf[4:8])[0]
    if total + 8 != len(buf):
        raise ValueError("FORM size %d != file size %d - 8" % (total, len(buf)))
    kind = buf[8:12].decode("latin1")
    p = 12
    out = []
    while p < len(buf):
        cid = buf[p:p + 4].decode("latin1")
        sz = struct.unpack(">I", buf[p + 4:p + 8])[0]
        out.append((cid, buf[p + 8:p + 8 + sz]))
        p += 8 + sz
    if p != len(buf):
        raise ValueError("chunk overrun")
    return kind, out


def expand_ranges(ranges):
    cps = []
    for first, count in ranges:
        cps.extend(range(first, first + count))
    return cps


def make_ranges(cps):
    ranges = []
    for cp in cps:
        if ranges and ranges[-1][0] + ranges[-1][1] == cp:
            ranges[-1][1] += 1
        else:
            ranges.append([cp, 1])
    return [tuple(r) for r in ranges]


def read(path_or_bytes):
    buf = path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray)) else open(path_or_bytes, "rb").read()
    kind, chunks = iff_chunks(buf)
    f = Font()
    f.kind = kind
    f.chunk_order = [c for c, _ in chunks]
    d = dict(chunks)
    if "HEAD" in d:
        h = d["HEAD"]
        n = struct.unpack_from("<I", h, 0)[0]
        f.name = h[4:4 + n].rstrip(b"\0").decode("latin1")
        f.size = struct.unpack_from("<H", h, 4 + n)[0]
        f.head_tail = h[4 + n + 2:]
    else:
        f.has_head = False
    g = d["GLPS"]
    f.glps_junk = g[:8]
    ng, nr = struct.unpack_from("<II", g, 8)
    ranges = []
    if kind == "FNT5":
        for k in range(nr):
            s, c = struct.unpack_from("<IH", g, 16 + 8 * k)
            ranges.append((s, c))
        rec_ranges = 16 + 8 * nr
    else:
        for k in range(nr):
            ranges.append(struct.unpack_from("<HH", g, 16 + 4 * k))
        rec_ranges = 16 + 4 * nr
    if rec_ranges != len(g):
        raise ValueError("GLPS size mismatch %d != %d" % (rec_ranges, len(g)))
    cps = expand_ranges(ranges)
    if len(cps) != ng:
        raise ValueError("glyph count %d != expanded ranges %d" % (ng, len(cps)))
    t = d["TCRD"]
    rec = len(t) // ng if ng else 12
    if rec * ng != len(t):
        raise ValueError("TCRD not a multiple of glyph count")
    for i, cp in enumerate(cps):
        r = t[i * rec:(i + 1) * rec]
        if rec == 12:
            x, y, w, h, pre, post = struct.unpack("<4H2h", r)
            f.glyphs.append(Glyph(cp, x, y, w, h, pre, post, r))
        elif rec == 8:  # FNT2 (system.fnt): fixed cells, no bearings
            x, y, w, h = struct.unpack("<4H", r)
            f.glyphs.append(Glyph(cp, x, y, w, h, 0, 0, r))
        else:
            f.glyphs.append(Glyph(cp, raw=r))
    k = d.get("KERN", b"")
    if kind == "FNT3":
        for o in range(0, len(k), 8):
            f.kern.append(struct.unpack_from("<HHi", k, o))
    else:
        f.extra_chunks["KERN"] = k
    for cid, data in chunks:
        if cid not in ("HEAD", "GLPS", "TCRD", "KERN"):
            f.extra_chunks[cid] = data
    return f


def _chunk(cid, data):
    return cid.encode("latin1") + struct.pack(">I", len(data)) + data


def write(f, path=None):
    """Serialise an FNT3 (bitmap) font."""
    if f.kind != "FNT3":
        raise ValueError("writer supports FNT3 only")
    cps = [g.cp for g in f.glyphs]
    if cps != sorted(cps) or len(set(cps)) != len(cps):
        raise ValueError("glyphs must be sorted by code point, no duplicates")
    if cps and cps[-1] > 0xFFFF:
        raise ValueError("FNT3 ranges are 16-bit: BMP code points only")
    ranges = make_ranges(cps)
    parts = {}
    name = f.name.encode("latin1") + b"\0"
    parts["HEAD"] = struct.pack("<I", len(name)) + name + struct.pack("<H", f.size) + bytes(f.head_tail)
    glps = bytearray(f.glps_junk[:8].ljust(8, b"\0"))
    glps += struct.pack("<II", len(cps), len(ranges))
    for s, c in ranges:
        if c > 0xFFFF:
            raise ValueError("range too long")
        glps += struct.pack("<HH", s, c)
    parts["GLPS"] = bytes(glps)
    parts["TCRD"] = b"".join(struct.pack("<4H2h", g.x, g.y, g.w, g.h, g.pre, g.post) for g in f.glyphs)
    # vanilla KERN is sorted by (left, right) -- keep it so (the reader may bisect)
    parts["KERN"] = b"".join(struct.pack("<HHi", a, b, dx) for a, b, dx in sorted(f.kern, key=lambda t: (t[0], t[1])))
    order = [c for c in f.chunk_order if c in parts] or ["GLPS", "TCRD", "KERN", "HEAD"]
    if not f.has_head and "HEAD" in order:
        order.remove("HEAD")
    body = b"FNT3" + b"".join(_chunk(c, parts[c]) for c in order)
    data = b"FORM" + struct.pack(">I", len(body)) + body
    if path:
        with open(path, "wb") as fh:
            fh.write(data)
    return data
