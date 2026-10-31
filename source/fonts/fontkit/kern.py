"""Kerning pairs straight from the font file (Pillow's BASIC layout applies none).

GPOS 'kern' feature, PairPos formats 1 and 2 (extension lookups included): first
matching subtable per pair inside a lookup, lookups summed.  The legacy 'kern' table
(format 0, horizontal) is used only when GPOS yields nothing.  Values in font units.
For a variable font these are the default instance's values (device and variation
tables are not read), so a heavier weight kerns like the regular one.
"""
import struct

from .sfnt import tables


def cmap_gids(buf, index=0):
    """{code point: glyph id}."""
    t = tables(buf, index)
    base = t["cmap"][0]
    n = struct.unpack_from(">H", buf, base + 2)[0]
    recs = []
    for k in range(n):
        pid, eid, off = struct.unpack_from(">HHI", buf, base + 4 + 8 * k)
        recs.append((pid, eid, struct.unpack_from(">H", buf, base + off)[0], base + off))
    for want in ((3, 10, 12), (0, 4, 12), (0, 6, 12), (3, 1, 4), (0, 3, 4), (0, 0, 4), (0, 1, 4)):
        for pid, eid, fmt, o in recs:
            if (pid, eid, fmt) == want:
                return _gids12(buf, o) if fmt == 12 else _gids4(buf, o)
    raise ValueError("no usable cmap")


def _gids4(buf, o):
    seg2 = struct.unpack_from(">H", buf, o + 6)[0]
    seg = seg2 // 2
    ends = struct.unpack_from(">%dH" % seg, buf, o + 14)
    starts = struct.unpack_from(">%dH" % seg, buf, o + 16 + seg2)
    deltas = struct.unpack_from(">%dh" % seg, buf, o + 16 + 2 * seg2)
    ro_pos = o + 16 + 3 * seg2
    ros = struct.unpack_from(">%dH" % seg, buf, ro_pos)
    out = {}
    for i in range(seg):
        s, e, d, ro = starts[i], ends[i], deltas[i], ros[i]
        if s == 0xFFFF:
            continue
        for c in range(s, e + 1):
            if ro == 0:
                gid = (c + d) & 0xFFFF
            else:
                gid = struct.unpack_from(">H", buf, ro_pos + 2 * i + ro + 2 * (c - s))[0]
                if gid:
                    gid = (gid + d) & 0xFFFF
            if gid:
                out[c] = gid
    return out


def _gids12(buf, o):
    n = struct.unpack_from(">I", buf, o + 12)[0]
    out = {}
    for k in range(n):
        s, e, g = struct.unpack_from(">III", buf, o + 16 + 12 * k)
        for c in range(s, e + 1):
            if g + (c - s):
                out[c] = g + (c - s)
    return out


def units_per_em(buf, index=0):
    return struct.unpack_from(">H", buf, tables(buf, index)["head"][0] + 18)[0]


def _coverage(buf, o):
    fmt = struct.unpack_from(">H", buf, o)[0]
    cov = {}
    if fmt == 1:
        n = struct.unpack_from(">H", buf, o + 2)[0]
        for i, g in enumerate(struct.unpack_from(">%dH" % n, buf, o + 4)):
            cov[g] = i
    elif fmt == 2:
        n = struct.unpack_from(">H", buf, o + 2)[0]
        for k in range(n):
            s, e, si = struct.unpack_from(">3H", buf, o + 4 + 6 * k)
            for g in range(s, e + 1):
                cov[g] = si + g - s
    return cov


def _class_def(buf, o):
    fmt = struct.unpack_from(">H", buf, o)[0]
    cls = {}
    if fmt == 1:
        start, n = struct.unpack_from(">HH", buf, o + 2)
        for i, c in enumerate(struct.unpack_from(">%dH" % n, buf, o + 6)):
            cls[start + i] = c
    elif fmt == 2:
        n = struct.unpack_from(">H", buf, o + 2)[0]
        for k in range(n):
            s, e, c = struct.unpack_from(">3H", buf, o + 4 + 6 * k)
            for g in range(s, e + 1):
                cls[g] = c
    return cls


def _vr_size(fmt):
    return 2 * bin(fmt & 0xFF).count("1")


def _x_advance(buf, o, fmt):
    """XAdvance of a ValueRecord at o (0 when the format has none)."""
    p = o
    for bit in (0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80):
        if fmt & bit:
            if bit == 0x4:
                return struct.unpack_from(">h", buf, p)[0]
            p += 2
    return 0


def _pairpos_subtables(buf, gpos):
    _maj, _min, _sl, fl, ll = struct.unpack_from(">5H", buf, gpos)
    fl += gpos
    ll += gpos
    nfeat = struct.unpack_from(">H", buf, fl)[0]
    lookup_idx = set()
    for k in range(nfeat):
        tag, off = struct.unpack_from(">4sH", buf, fl + 2 + 6 * k)
        if tag == b"kern":
            f = fl + off
            n = struct.unpack_from(">H", buf, f + 2)[0]
            lookup_idx.update(struct.unpack_from(">%dH" % n, buf, f + 4))
    nl = struct.unpack_from(">H", buf, ll)[0]
    loffs = struct.unpack_from(">%dH" % nl, buf, ll + 2)
    for li in sorted(lookup_idx):
        lo = ll + loffs[li]
        ltype, _flag, nsub = struct.unpack_from(">3H", buf, lo)
        for so in struct.unpack_from(">%dH" % nsub, buf, lo + 6):
            st = lo + so
            if ltype == 9:
                _f, ext_type, ext_off = struct.unpack_from(">HHI", buf, st)
                if ext_type != 2:
                    continue
                st += ext_off
            elif ltype != 2:
                continue
            yield li, st


def kerning(path, cps, index=0):
    """{(left cp, right cp): font units} restricted to code points `cps`."""
    buf = open(path, "rb").read()
    t = tables(buf, index)
    gid = cmap_gids(buf, index)
    g2c = {}
    for c in cps:
        if c in gid:
            g2c.setdefault(gid[c], []).append(c)
    gids = sorted(g2c)
    gset = set(gids)
    out = {}
    if "GPOS" in t:
        done = {}
        for li, st in _pairpos_subtables(buf, t["GPOS"][0]):
            seen = done.setdefault(li, set())
            fmt = struct.unpack_from(">H", buf, st)[0]
            cov = _coverage(buf, st + struct.unpack_from(">H", buf, st + 2)[0])
            vf1, vf2 = struct.unpack_from(">HH", buf, st + 4)
            s1, s2 = _vr_size(vf1), _vr_size(vf2)
            if fmt == 1:
                nsets = struct.unpack_from(">H", buf, st + 8)[0]
                set_offs = struct.unpack_from(">%dH" % nsets, buf, st + 10)
                rec = 2 + s1 + s2
                for a in gids:
                    ci = cov.get(a)
                    if ci is None:
                        continue
                    ps = st + set_offs[ci]
                    npv = struct.unpack_from(">H", buf, ps)[0]
                    for k in range(npv):
                        p = ps + 2 + rec * k
                        b = struct.unpack_from(">H", buf, p)[0]
                        if b in gset and (a, b) not in seen:
                            seen.add((a, b))
                            v = _x_advance(buf, p + 2, vf1)
                            if v:
                                out[(a, b)] = out.get((a, b), 0) + v
            elif fmt == 2:
                cd1 = _class_def(buf, st + struct.unpack_from(">H", buf, st + 8)[0])
                cd2 = _class_def(buf, st + struct.unpack_from(">H", buf, st + 10)[0])
                c2n = struct.unpack_from(">H", buf, st + 14)[0]
                rec = s1 + s2
                for a in gids:
                    if a not in cov:
                        continue
                    row = st + 16 + cd1.get(a, 0) * c2n * rec
                    for b in gids:
                        if (a, b) in seen:
                            continue
                        seen.add((a, b))
                        v = _x_advance(buf, row + cd2.get(b, 0) * rec, vf1)
                        if v:
                            out[(a, b)] = out.get((a, b), 0) + v
    if not out and "kern" in t:
        ko = t["kern"][0]
        ver, ntab = struct.unpack_from(">HH", buf, ko)
        p = ko + 4
        if ver == 0:
            for _ in range(ntab):
                _sv, length, coverage = struct.unpack_from(">3H", buf, p)
                if (coverage >> 8) == 0 and (coverage & 1) and not (coverage & 4):
                    npairs = struct.unpack_from(">H", buf, p + 6)[0]
                    for k in range(npairs):
                        a, b, v = struct.unpack_from(">HHh", buf, p + 14 + 6 * k)
                        if a in gset and b in gset and v:
                            out[(a, b)] = out.get((a, b), 0) + v
                p += length
    res = {}
    for (a, b), v in out.items():
        for ca in g2c[a]:
            for cb in g2c[b]:
                res[(ca, cb)] = v
    return res, units_per_em(buf, index)
