"""Minimal sfnt reader: which code points a TTF/OTF/TTC face maps, and its names.

Pillow renders .notdef for a missing character without telling us, so coverage
comes from the cmap table (formats 4 and 12, the ones Windows fonts use).
"""
import struct


def _face_offset(buf, index):
    tag = buf[:4]
    if tag == b"ttcf":
        n = struct.unpack_from(">I", buf, 8)[0]
        if index >= n:
            raise ValueError("TTC has %d faces, asked for %d" % (n, index))
        return struct.unpack_from(">I", buf, 12 + 4 * index)[0]
    return 0


def tables(buf, index=0):
    off = _face_offset(buf, index)
    num = struct.unpack_from(">H", buf, off + 4)[0]
    out = {}
    for k in range(num):
        tag, _cs, toff, tlen = struct.unpack_from(">4sIII", buf, off + 12 + 16 * k)
        out[tag.decode("latin1")] = (toff, tlen)
    return out


def _cmap_fmt4(buf, o):
    seg2 = struct.unpack_from(">H", buf, o + 6)[0]
    seg = seg2 // 2
    ends = struct.unpack_from(">%dH" % seg, buf, o + 14)
    starts = struct.unpack_from(">%dH" % seg, buf, o + 16 + seg2)
    deltas = struct.unpack_from(">%dh" % seg, buf, o + 16 + 2 * seg2)
    ro_pos = o + 16 + 3 * seg2
    ros = struct.unpack_from(">%dH" % seg, buf, ro_pos)
    cps = set()
    for i in range(seg):
        s, e, d, ro = starts[i], ends[i], deltas[i], ros[i]
        if s == 0xFFFF:
            continue
        for c in range(s, e + 1):
            if ro == 0:
                gid = (c + d) & 0xFFFF
            else:
                p = ro_pos + 2 * i + ro + 2 * (c - s)
                gid = struct.unpack_from(">H", buf, p)[0]
                if gid:
                    gid = (gid + d) & 0xFFFF
            if gid:
                cps.add(c)
    return cps


def _cmap_fmt12(buf, o):
    n = struct.unpack_from(">I", buf, o + 12)[0]
    cps = set()
    for k in range(n):
        s, e, g = struct.unpack_from(">III", buf, o + 16 + 12 * k)
        for c in range(s, e + 1):
            if g + (c - s):
                cps.add(c)
    return cps


def coverage(path, index=0):
    buf = open(path, "rb").read()
    t = tables(buf, index)
    if "cmap" not in t:
        raise ValueError("no cmap table")
    base = t["cmap"][0]
    n = struct.unpack_from(">H", buf, base + 2)[0]
    recs = []
    for k in range(n):
        pid, eid, off = struct.unpack_from(">HHI", buf, base + 4 + 8 * k)
        fmt = struct.unpack_from(">H", buf, base + off)[0]
        recs.append((pid, eid, fmt, base + off))
    # prefer full-repertoire Unicode subtables
    for want in ((3, 10, 12), (0, 4, 12), (0, 6, 12), (3, 1, 4), (0, 3, 4), (0, 0, 4), (0, 1, 4)):
        for pid, eid, fmt, o in recs:
            if (pid, eid, fmt) == want:
                return _cmap_fmt12(buf, o) if fmt == 12 else _cmap_fmt4(buf, o)
    for pid, eid, fmt, o in recs:
        if fmt == 4:
            return _cmap_fmt4(buf, o)
    raise ValueError("no usable Unicode cmap subtable: %s" % [(r[0], r[1], r[2]) for r in recs])


def names(path, index=0):
    """{nameID: string} from the Windows/Unicode records of the name table."""
    buf = open(path, "rb").read()
    t = tables(buf, index)
    if "name" not in t:
        return {}
    base = t["name"][0]
    _fmt, count, soff = struct.unpack_from(">HHH", buf, base)
    out = {}
    for k in range(count):
        pid, eid, lang, nid, ln, off = struct.unpack_from(">6H", buf, base + 6 + 12 * k)
        raw = buf[base + soff + off: base + soff + off + ln]
        if pid == 3 and lang in (0x409, 0):
            out.setdefault(nid, raw.decode("utf-16-be", "replace"))
        elif pid == 0:
            out.setdefault(nid, raw.decode("utf-16-be", "replace"))
        elif pid == 1 and nid not in out:
            out[nid] = raw.decode("latin1")
    return out


def fs_type(path, index=0):
    """OS/2 fsType embedding bits (0 = installable; 2 = restricted; 4 = preview&print; 8 = editable)."""
    buf = open(path, "rb").read()
    t = tables(buf, index)
    if "OS/2" not in t:
        return None
    return struct.unpack_from(">H", buf, t["OS/2"][0] + 8)[0]
