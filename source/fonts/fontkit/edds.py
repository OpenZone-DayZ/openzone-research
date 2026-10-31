"""Enfusion .edds reader/writer (the subset DayZ fonts use).

Layout (all little-endian), measured on DayZ 1.30 gui.pbo fonts:

  0x00  "DDS "                         magic
  0x04  DDS_HEADER (124 bytes)         standard Microsoft layout
        dwReserved1[1] (file 0x24) = "ENF1"   Enfusion marker -- every vanilla
        file has it; the engine also draws a font whose texture is a plain
        single-level DDS without it (probe row R11, measured 2026-10-31)
  [0x80 DDS_HEADER_DXT10 (20 bytes)]   only when ddspf.dwFourCC == "DX10"
  then  block table: one 8-byte entry per mip, SMALLEST MIP FIRST
        char[4] codec ("COPY" | "LZ4 "), uint32 stored size of the block
  then  the blocks, in table order
        COPY: raw mip bytes
        LZ4 : uint32 decompressed size, then chunks:
              uint24 compressed size, uint8 flags (0x80 = last chunk),
              raw LZ4 block decoding to 64 KiB (last chunk: the rest);
              vanilla chunks are LINKED (stream mode: a chunk may reference
              the previous decoded bytes of the same mip, window 64 KiB);
              this writer emits standalone chunks by default (LINKED below)
  The engine's block switch also knows "LZO " and "ZLIB" (DayZDiag_x64.exe);
  no shipped file uses them, this module does not either.
"""
import struct

from .lz4blk import compress, decode_into

DDSD_CAPS, DDSD_HEIGHT, DDSD_WIDTH, DDSD_PITCH = 0x1, 0x2, 0x4, 0x8
DDSD_PIXELFORMAT, DDSD_MIPMAPCOUNT, DDSD_LINEARSIZE = 0x1000, 0x20000, 0x80000
DDPF_ALPHAPIXELS, DDPF_FOURCC, DDPF_RGB = 0x1, 0x4, 0x40
DDSCAPS_COMPLEX, DDSCAPS_TEXTURE, DDSCAPS_MIPMAP = 0x8, 0x1000, 0x400000
CHUNK = 65536


class Edds:
    def __init__(self):
        self.width = self.height = 0
        self.mipcount = 0
        self.header = {}
        self.dx10 = None
        self.table = []        # [(codec, stored_size)] smallest first
        self.mips = []         # decoded mip bytes, LARGEST first (DDS order)
        self.chunks = []       # per table entry: [(csize, flags, dsize)]


def read(path_or_bytes):
    buf = path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray)) else open(path_or_bytes, "rb").read()
    if buf[:4] != b"DDS ":
        raise ValueError("not a DDS/EDDS file")
    e = Edds()
    (size, flags, h, w, pitch, depth, mips) = struct.unpack_from("<7I", buf, 4)
    reserved1 = buf[32:76]
    pf = struct.unpack_from("<2I4s5I", buf, 76)
    caps = struct.unpack_from("<4I", buf, 108)
    e.header = dict(size=size, flags=flags, pitch=pitch, depth=depth, reserved1=reserved1,
                    pf_size=pf[0], pf_flags=pf[1], fourcc=pf[2], bits=pf[3],
                    masks=pf[4:8], caps=caps, reserved2=struct.unpack_from("<I", buf, 124)[0])
    e.width, e.height, e.mipcount = w, h, mips
    hdr = 128
    if pf[2] == b"DX10":
        e.dx10 = struct.unpack_from("<5I", buf, 128)
        hdr = 148
    n = max(1, mips)
    p = hdr
    for _ in range(n):
        cc, sz = struct.unpack_from("<4sI", buf, p)
        e.table.append((cc.decode("latin1"), sz))
        p += 8
    decoded = []
    for cc, sz in e.table:
        blk = buf[p:p + sz]
        p += sz
        if cc == "COPY":
            decoded.append(bytes(blk))
            e.chunks.append([])
        elif cc == "LZ4 ":
            usize = struct.unpack_from("<I", blk, 0)[0]
            q = 4
            out = bytearray()
            ch = []
            while q < len(blk):
                csz = blk[q] | (blk[q + 1] << 8) | (blk[q + 2] << 16)
                fl = blk[q + 3]
                q += 4
                before = len(out)
                decode_into(blk[q:q + csz], out, usize)
                ch.append((csz, fl, len(out) - before))
                q += csz
                if fl & 0x80:
                    break
            if len(out) != usize:
                raise ValueError("LZ4 mip size mismatch %d != %d" % (len(out), usize))
            decoded.append(bytes(out))
            e.chunks.append(ch)
        else:
            raise ValueError("unknown block codec %r" % cc)
    if p != len(buf):
        raise ValueError("trailing bytes: %d" % (len(buf) - p))
    e.mips = decoded[::-1]
    return e


def mip_sizes(w, h, n):
    out = []
    for _ in range(n):
        out.append((w, h))
        w, h = max(1, w // 2), max(1, h // 2)
    return out


def to_rgba_images(e):
    """Decoded mips of an A8R8G8B8 edds as Pillow RGBA images (largest first)."""
    from PIL import Image
    if e.header["fourcc"] != b"\0\0\0\0" or e.header["bits"] != 32:
        raise ValueError("only uncompressed 32-bit BGRA is supported here")
    imgs = []
    for (w, h), data in zip(mip_sizes(e.width, e.height, max(1, e.mipcount)), e.mips):
        imgs.append(Image.frombuffer("RGBA", (w, h), data, "raw", "BGRA", 0, 1).copy())
    return imgs


LINKED = False   # True = chunks may reference the previous 64 KiB, like vanilla files.
                 # Default False: every chunk standalone -- valid for ANY LZ4 decoder,
                 # streaming or not, at a few % of size.


def _lz4_block(raw, linked=None):
    linked = LINKED if linked is None else linked
    out = bytearray(struct.pack("<I", len(raw)))
    prev = b""
    for k in range(0, len(raw), CHUNK):
        part = raw[k:k + CHUNK]
        c = compress(part, prev if linked else b"")
        last = k + CHUNK >= len(raw)
        out += struct.pack("<I", len(c) | ((0x80 if last else 0) << 24))
        out += c
        prev = (prev + part)[-CHUNK:]
    return bytes(out)


def write_plain_dds(path, image):
    """A standard single-level A8R8G8B8 DDS (no ENF1, no block table); kept for probes."""
    img = image.convert("RGBA")
    w, h = img.size
    hdr = bytearray(b"DDS ")
    hdr += struct.pack("<7I", 124, DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PITCH | DDSD_PIXELFORMAT,
                       h, w, w * 4, 0, 0)
    hdr += bytes(44)
    hdr += struct.pack("<2I4s5I", 32, DDPF_RGB | DDPF_ALPHAPIXELS, b"\0\0\0\0", 32,
                       0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    hdr += struct.pack("<4I", DDSCAPS_TEXTURE, 0, 0, 0) + struct.pack("<I", 0)
    data = bytes(hdr) + img.tobytes("raw", "BGRA")
    with open(path, "wb") as f:
        f.write(data)
    return data


def write(path, image, mipmaps=True, lz4_min=512, levels=None):
    """Write a Pillow image as an A8R8G8B8 .edds the way the vanilla font atlases are.

    mipmaps: build a full chain (box filter) like 7segment/sdf_* fonts; False = one level
             like Metron22/system ("GenerateMips 0" in their .meta).
    lz4_min: mips whose raw size is below this are stored COPY (vanilla: 1x1..8x8 COPY,
             16x16 and up LZ4).
    levels:  explicit mip images, largest first (round-trip tests); overrides mipmaps.
    """
    from PIL import Image
    img = (levels[0] if levels else image).convert("RGBA")
    w, h = img.size
    if w & (w - 1) or h & (h - 1):
        raise ValueError("power-of-two sizes only (vanilla atlases are)")
    if levels:
        levels = [lv.convert("RGBA") for lv in levels]
    else:
        levels = [img]
    if mipmaps and len(levels) == 1:
        while levels[-1].size != (1, 1):
            lw, lh = levels[-1].size
            levels.append(levels[-1].resize((max(1, lw // 2), max(1, lh // 2)), Image.BOX))
    n = len(levels)
    flags = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PITCH | DDSD_PIXELFORMAT | DDSD_MIPMAPCOUNT
    caps1 = DDSCAPS_TEXTURE | ((DDSCAPS_COMPLEX | DDSCAPS_MIPMAP) if n > 1 else 0)
    hdr = bytearray(b"DDS ")
    hdr += struct.pack("<7I", 124, flags, h, w, w * 4, 0, n)
    reserved1 = bytearray(44)
    reserved1[4:8] = b"ENF1"
    hdr += reserved1
    hdr += struct.pack("<2I4s5I", 32, DDPF_RGB | DDPF_ALPHAPIXELS, b"\0\0\0\0", 32,
                       0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    hdr += struct.pack("<4I", caps1, 0, 0, 0)
    hdr += struct.pack("<I", 0)
    assert len(hdr) == 128
    blocks = []
    for lvl in reversed(levels):                       # smallest first
        raw = lvl.tobytes("raw", "BGRA")
        if len(raw) >= lz4_min:
            blk = _lz4_block(raw)
            if len(blk) < len(raw):
                blocks.append(("LZ4 ", blk))
                continue
        blocks.append(("COPY", raw))
    table = b"".join(struct.pack("<4sI", cc.encode(), len(b)) for cc, b in blocks)
    data = bytes(hdr) + table + b"".join(b for _, b in blocks)
    if path:
        with open(path, "wb") as f:
            f.write(data)
    return data
