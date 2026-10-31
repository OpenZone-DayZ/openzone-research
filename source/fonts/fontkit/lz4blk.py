"""Pure-Python LZ4 *block* codec (no frame format), enough for Enfusion .edds.

decode_into(src, out, end_size) appends to `out`; back-references may reach into
bytes already in `out`, so decoding chunk after chunk into one buffer handles
both independent and linked (dictionary = previous 64 KiB) blocks.

compress(data, dict_bytes=b"") returns one raw LZ4 block.  With dict_bytes the
block may reference the tail of the dictionary (linked-block mode, like
LZ4_compress_fast_continue).  Greedy hash matcher, min match 4, keeps the
spec's end-of-block rules (last 5 bytes literals, no match starting in the
last 12 bytes).
"""

MINMATCH = 4
LASTLITERALS = 5
MFLIMIT = 12
MAX_OFFSET = 65535


def decode_into(src, out, end_size=None):
    """Decode one raw LZ4 block `src` and append the result to bytearray `out`."""
    i = 0
    n = len(src)
    while i < n:
        token = src[i]
        i += 1
        lit = token >> 4
        if lit == 15:
            while True:
                b = src[i]
                i += 1
                lit += b
                if b != 255:
                    break
        if lit:
            out += src[i:i + lit]
            i += lit
        if i >= n:
            break  # last sequence: literals only
        off = src[i] | (src[i + 1] << 8)
        i += 2
        if off == 0:
            raise ValueError("lz4: zero offset")
        ml = token & 15
        if ml == 15:
            while True:
                b = src[i]
                i += 1
                ml += b
                if b != 255:
                    break
        ml += MINMATCH
        start = len(out) - off
        if start < 0:
            raise ValueError("lz4: offset %d reaches before buffer start" % off)
        if off >= ml:
            out += out[start:start + ml]
        else:  # overlapping copy (run)
            for k in range(ml):
                out.append(out[start + k])
        if end_size is not None and len(out) > end_size:
            raise ValueError("lz4: output overrun")
    return out


def _put_len(buf, v):
    while v >= 255:
        buf.append(255)
        v -= 255
    buf.append(v)


def compress(data, dict_bytes=b""):
    """Greedy LZ4 block compressor. Returns bytes of one raw block."""
    dict_bytes = bytes(dict_bytes[-65536:])
    base = len(dict_bytes)
    buf = dict_bytes + bytes(data)
    end = len(buf)
    out = bytearray()
    table = {}
    # seed the hash table with dictionary positions
    for p in range(0, max(0, base - 3)):
        table[buf[p:p + 4]] = p
    anchor = base
    p = base
    match_limit = end - MFLIMIT
    while p < match_limit:
        key = buf[p:p + 4]
        cand = table.get(key)
        table[key] = p
        if cand is None or p - cand > MAX_OFFSET:
            p += 1
            continue
        # extend match forward (stop before LASTLITERALS)
        m_end_limit = end - LASTLITERALS
        q = p + 4
        c = cand + 4
        while q < m_end_limit and buf[q] == buf[c]:
            q += 1
            c += 1
        # extend backward into pending literals
        while p > anchor and cand > 0 and buf[p - 1] == buf[cand - 1]:
            p -= 1
            cand -= 1
        lit_len = p - anchor
        ml = q - p
        tok_lit = 15 if lit_len >= 15 else lit_len
        tok_ml = 15 if ml - 4 >= 15 else ml - 4
        out.append((tok_lit << 4) | tok_ml)
        if lit_len >= 15:
            _put_len(out, lit_len - 15)
        out += buf[anchor:p]
        off = p - cand
        out.append(off & 255)
        out.append(off >> 8)
        if ml - 4 >= 15:
            _put_len(out, ml - 4 - 15)
        # index a couple of positions inside the match for better ratio
        for r in range(p + 1, min(q, match_limit), 3):
            table[buf[r:r + 4]] = r
        p = q
        anchor = p
    lit_len = end - anchor
    tok_lit = 15 if lit_len >= 15 else lit_len
    out.append(tok_lit << 4)
    if lit_len >= 15:
        _put_len(out, lit_len - 15)
    out += buf[anchor:end]
    return bytes(out)


if __name__ == "__main__":
    import os
    import random
    random.seed(1)
    for trial in range(200):
        size = random.choice([0, 1, 5, 13, 100, 4096, 70000])
        alphabet = random.choice([b"ab", b"abcdefgh", bytes(range(256))])
        data = bytes(random.choice(alphabet) for _ in range(size))
        if random.random() < 0.3:
            data = data[: size // 2] * 2
        d = bytes(random.choice(alphabet) for _ in range(random.choice([0, 100, 70000])))
        blk = compress(data, d)
        out = bytearray(d[-65536:])
        decode_into(blk, out)
        assert bytes(out[len(d[-65536:]):]) == data, trial
    big = os.urandom(1000) * 50
    assert bytes(decode_into(compress(big), bytearray())) == big
    print("lz4blk self-test OK")
