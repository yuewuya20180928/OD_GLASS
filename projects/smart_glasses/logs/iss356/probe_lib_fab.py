#!/usr/bin/env python3
"""ISS-356 cont2 · 库封装 F.Fab / F.CrtYd 实测 (s-expr 解析, 只读)
输出 logs/iss356/lib_fab_geom.json
"""
import hashlib
import json
import os

LIBROOT = '/home/yuewuya/kicad/AppDir/share/kicad/footprints'

CANDS = [
    'Resistor_SMD:R_0402_1005Metric',
    'Resistor_SMD:R_0603_1608Metric',
    'Resistor_SMD:R_0805_2012Metric',
    'Resistor_SMD:R_1206_3216Metric',
    'Capacitor_SMD:C_0402_1005Metric',
    'Capacitor_SMD:C_0603_1608Metric',
    'Capacitor_SMD:C_0805_2012Metric',
    'Capacitor_SMD:C_1206_3216Metric',
    'LED_SMD:LED_0603_1608Metric',
    'LED_SMD:LED_0805_2012Metric',
    'Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical',
    'Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Horizontal',
    'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
]


def tokenize(s):
    i, n, out = 0, len(s), []
    while i < n:
        c = s[i]
        if c in '()':
            out.append(c)
            i += 1
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


def bbox_of(node, layer):
    xs, ys = [], []
    for sub in node:
        if not isinstance(sub, list):
            continue
        h = sym(sub[0])
        if h not in ('fp_line', 'fp_rect', 'fp_circle'):
            continue
        lay = None
        for s2 in sub:
            if isinstance(s2, list) and sym(s2[0]) == 'layer':
                lay = sym(s2[1])
        if lay != layer:
            continue
        for s2 in sub:
            if isinstance(s2, list) and sym(s2[0]) in ('start', 'end', 'center') and len(s2) >= 3:
                x, y = num(s2[1]), num(s2[2])
                if x is not None and y is not None:
                    xs.append(x); ys.append(y)
    if not xs:
        return None
    return [round(max(xs) - min(xs), 4), round(max(ys) - min(ys), 4)]


def probe(path):
    root = parse(tokenize(open(path, encoding='utf-8').read()))[0]
    fabpts = []
    crtpts = []
    pads = []
    for node in root:
        if isinstance(node, list) and sym(node[0]) in ('fp_line', 'fp_rect', 'fp_circle'):
            lay = None
            for s2 in node:
                if isinstance(s2, list) and sym(s2[0]) == 'layer':
                    lay = sym(s2[1])
            pts = []
            for s2 in node:
                if isinstance(s2, list) and sym(s2[0]) in ('start', 'end', 'center') and len(s2) >= 3:
                    x, y = num(s2[1]), num(s2[2])
                    if x is not None and y is not None:
                        pts.append((x, y))
            if not pts:
                continue
            if lay == 'F.Fab':
                fabpts.extend(pts)
            elif lay == 'F.CrtYd':
                crtpts.extend(pts)
        if isinstance(node, list) and sym(node[0]) == 'pad':
            pnum, ptype, pshape = sym(node[1]), sym(node[2]), sym(node[3])
            at = size = None
            layers = []
            for s2 in node:
                if not isinstance(s2, list):
                    continue
                sh = sym(s2[0])
                if sh == 'at' and len(s2) >= 3:
                    at = (num(s2[1]), num(s2[2]))
                elif sh == 'size' and len(s2) >= 3:
                    size = (num(s2[1]), num(s2[2]))
                elif sh == 'layers':
                    layers = [sym(c) for c in s2[1:] if isinstance(c, tuple)]
            pads.append(dict(num=pnum, type=ptype, shape=pshape, at=at, size=size, layers=layers))

    def bb(pts):
        if not pts:
            return None
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return [round(max(xs) - min(xs), 4), round(max(ys) - min(ys), 4)]
    return bb(fabpts), bb(crtpts), pads


def main():
    out = {}
    for key in CANDS:
        lib, name = key.split(':', 1)
        path = os.path.join(LIBROOT, lib + '.pretty', name + '.kicad_mod')
        if not os.path.isfile(path):
            out[key] = {'exists': False, 'path': path}
            print('MISS', key)
            continue
        fab, crt, pads = probe(path)
        md5 = hashlib.md5(open(path, 'rb').read()).hexdigest()
        out[key] = {'exists': True, 'path': path, 'md5': md5,
                    'fab_bbox': fab, 'courtyard_bbox': crt, 'npad': len(pads),
                    'pad_centers': [p['at'] for p in pads],
                    'pad_sizes': [p['size'] for p in pads],
                    'pad_types': [p['type'] for p in pads],
                    'pad_nums': [p['num'] for p in pads]}
        print('%-58s npad=%d fab=%s crtyd=%s' % (key, len(pads), fab, crt))
    json.dump(out, open('logs/iss356/lib_fab_geom.json', 'w'), ensure_ascii=False, indent=1)
    print('wrote logs/iss356/lib_fab_geom.json')


if __name__ == '__main__':
    main()
