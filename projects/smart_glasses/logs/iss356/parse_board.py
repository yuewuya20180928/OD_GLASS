#!/usr/bin/env python3
"""ISS-356 只读板面解析器: 读 HW/PCB/demo_mainboard.kicad_pcb, 输出每个封装的
库名 / ref / value / 焊盘编号+尺寸+网络 / fab bbox / 位置。
零写板: 本脚本只 open(..., 'r')。
"""
import re, sys, json, collections

BOARD = 'HW/PCB/demo_mainboard.kicad_pcb'


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
                    buf.append(s[j:j+2]); j += 2; continue
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
    s = sym(x)
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def load():
    txt = open(BOARD, encoding='utf-8').read()
    root = parse(tokenize(txt))[0]
    fps = []
    for node in root:
        if isinstance(node, list) and sym(node[0]) == 'footprint':
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
                    pname = sym(sub[1]); pval = sym(sub[2])
                    if pname == 'Reference': ref = pval
                    if pname == 'Value': val = pval
                elif h == 'at' and len(sub) >= 3:
                    pos = (num(sub[1]), num(sub[2]))
                elif h == 'layer':
                    layer = sym(sub[1])
                elif h == 'pad':
                    pnum = sym(sub[1]); ptype = sym(sub[2])
                    size = None; net = None; shape = None
                    for psub in sub:
                        if not isinstance(psub, list): continue
                        ph = sym(psub[0])
                        if ph == 'size' and len(psub) >= 3: size = (num(psub[1]), num(psub[2]))
                        elif ph == 'net' and len(psub) >= 3: net = sym(psub[2])
                        elif ph == 'shape' and len(psub) >= 2: shape = sym(psub[1])
                    pads.append(dict(num=pnum, type=ptype, size=size, net=net, shape=shape))
            # fab bbox (fp_line + fp_rect on F.Fab)
            xs, ys = [], []
            def _add(ax, ay, bx, by):
                if None in (ax, ay, bx, by): return
                xs.extend([ax, bx]); ys.extend([ay, by])
            def _pt(sub):
                for c in sub:
                    if isinstance(c, list) and sym(c[0]) in ('start', 'end', 'center') and len(c) >= 3:
                        return (num(c[1]), num(c[2]))
                return (None, None)
            for sub in node:
                if not isinstance(sub, list): continue
                h = sym(sub[0])
                if h in ('fp_line', 'fp_rect'):
                    (ax, ay), (bx, by) = _pt(sub), _pt(sub[1:])
                    if bx is None:
                        bx, by = ax, ay
                    _add(ax, ay, bx, by)
                elif h == 'fp_circle' and len(sub) >= 3:
                    (ax, ay) = _pt(sub)
                    if ax is not None:
                        xs.append(ax); ys.append(ay)
            bbox = (round(max(xs)-min(xs), 3), round(max(ys)-min(ys), 3)) if xs else None
            fps.append(dict(lib=lib, ref=ref, value=val, pads=pads,
                            bbox=bbox, pos=pos, layer=layer, npad=len(pads)))
    return fps


if __name__ == '__main__':
    fps = load()
    print("TOTAL_FOOTPRINTS=%d" % len(fps))
    print("LIB_NONEMPTY=%d" % len([f for f in fps if (f['lib'] or '').strip()]))
    json.dump(fps, open('logs/iss356/board_footprints.json', 'w'), ensure_ascii=False, indent=1)
    print("wrote logs/iss356/board_footprints.json")
