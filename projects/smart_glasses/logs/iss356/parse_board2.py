#!/usr/bin/env python3
"""ISS-356 cont2 · 板面解析器 v2 (修正 net 丢失 + 补 pad at / fab bbox)
只读: open(BOARD, 'r')。零写板。
"""
import json
import collections

BOARD = 'HW/PCB/demo_mainboard.kicad_pcb'
OUT = 'logs/iss356/board_footprints_v2.json'


def tokenize(s):
    i, n = 0, len(s)
    out = []
    while i < n:
        c = s[i]
        if c in '()':
            out.append(c); i += 1
        elif c == '"':
            j = i + 1
            buf = []
            while j < n:
                if s[j] == '\\':
                    buf.append(s[j:j + 2]); j += 2; continue
                if s[j] == '"':
                    break
                buf.append(s[j]); j += 1
            out.append(('str', ''.join(buf)))
            i = j + 1
        elif c in ' \t\r\n':
            i += 1
        else:
            j = i
            while j < n and s[j] not in ' \t\r\n()':
                j += 1
            out.append(('sym', s[i:j])); i = j
    return out


def parse(toks):
    pos = 0

    def rd():
        nonlocal pos
        t = toks[pos]
        if t == '(':
            pos += 1
            lst = []
            while toks[pos] != ')':
                lst.append(rd())
            pos += 1
            return lst
        pos += 1
        return t
    res = []
    while pos < len(toks):
        res.append(rd())
    return res


def sym(x):
    return x[1] if isinstance(x, tuple) else None


def num(x):
    try:
        return float(sym(x))
    except (TypeError, ValueError):
        return None


def load():
    txt = open(BOARD, encoding='utf-8').read()
    root = parse(tokenize(txt))[0]
    fps = []
    for node in root:
        if not (isinstance(node, list) and sym(node[0]) == 'footprint'):
            continue
        lib = sym(node[1])
        ref = val = None
        pads = []
        pos = None
        layer = None
        for sub in node:
            if not isinstance(sub, list):
                continue
            h = sym(sub[0])
            if h == 'property' and len(sub) >= 3:
                pname, pval = sym(sub[1]), sym(sub[2])
                if pname == 'Reference':
                    ref = pval
                if pname == 'Value':
                    val = pval
            elif h == 'at' and len(sub) >= 3:
                pos = (num(sub[1]), num(sub[2]))
            elif h == 'layer':
                layer = sym(sub[1])
            elif h == 'pad':
                pnum, ptype = sym(sub[1]), sym(sub[2])
                size = net = shape = None
                at = None
                for psub in sub:
                    if not isinstance(psub, list):
                        continue
                    ph = sym(psub[0])
                    if ph == 'size' and len(psub) >= 3:
                        size = (num(psub[1]), num(psub[2]))
                    elif ph == 'net':
                        # (net "NAME")  或 (net 5 "NAME")
                        strs = [sym(c) for c in psub[1:] if isinstance(c, tuple)]
                        if strs:
                            net = strs[-1]
                    elif ph == 'shape' and len(psub) >= 2:
                        shape = sym(psub[1])
                    elif ph == 'at' and len(psub) >= 3:
                        at = (num(psub[1]), num(psub[2]))
                pads.append(dict(num=pnum, type=ptype, size=size, net=net, shape=shape, at=at))
        # fab bbox
        xs, ys = [], []

        def _pt(sub):
            for c in sub:
                if isinstance(c, list) and sym(c[0]) in ('start', 'end', 'center') and len(c) >= 3:
                    return (num(c[1]), num(c[2]))
            return (None, None)

        for sub in node:
            if not isinstance(sub, list):
                continue
            h = sym(sub[0])
            if h in ('fp_line', 'fp_rect'):
                (ax, ay) = _pt(sub)
                (bx, by) = _pt(sub[1:])
                if bx is None:
                    bx, by = ax, ay
                if None not in (ax, ay, bx, by):
                    xs.extend([ax, bx]); ys.extend([ay, by])
            elif h == 'fp_circle' and len(sub) >= 3:
                (ax, ay) = _pt(sub)
                if ax is not None:
                    xs.append(ax); ys.append(ay)
        bbox = (round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)) if xs else None
        fps.append(dict(lib=lib, ref=ref, value=val, pads=pads, bbox=bbox,
                        pos=pos, layer=layer, npad=len(pads)))
    return fps


if __name__ == '__main__':
    fps = load()
    print("TOTAL_FOOTPRINTS=%d" % len(fps))
    print("LIB_NONEMPTY=%d" % len([f for f in fps if (f['lib'] or '').strip()]))
    one = [f for f in fps if f['npad'] == 1]
    print("NPAD1_TOTAL=%d" % len(one))
    print("NPAD1_TP=%d" % len([f for f in one if (f['ref'] or '').startswith('TP_')]))
    print("NPAD1_REAL=%d" % len([f for f in one if not (f['ref'] or '').startswith('TP_')]))
    print("NPAD1_REAL_REFS=%s" % sorted(f['ref'] for f in one if not (f['ref'] or '').startswith('TP_')))
    print("PADS_WITH_NET=%d / %d" % (sum(1 for f in fps for p in f['pads'] if p['net']),
                                     sum(f['npad'] for f in fps)))
    json.dump(fps, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print("wrote " + OUT)
