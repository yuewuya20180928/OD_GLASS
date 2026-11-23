#!/usr/bin/env python3
"""ISS-356 只读探针: 量 KiCad 官方库 .kicad_mod 的真实焊盘几何 (pad 编号/尺寸/at 偏移) + fab bbox,
用于和 demo_mainboard.kicad_pcb 上的占位族做「焊盘数 / 焊盘网络 / 本体+land pattern 能否落进 bbox」三判据。
零写板: 只读。
"""
import os, sys, json

FP = '/home/yuewuya/kicad/AppDir/share/kicad/footprints'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_board import tokenize, parse, sym, num


def measure(lib, name):
    path = os.path.join(FP, '%s.pretty' % lib, '%s.kicad_mod' % name)
    if not os.path.isfile(path):
        return None
    txt = open(path, encoding='utf-8').read()
    root = parse(tokenize(txt))[0]
    pads = []
    xs, ys = [], []
    for node in root:
        if not isinstance(node, list):
            continue
        if sym(node[0]) == 'pad':
            at = None; size = None; lay = None
            for sub in node:
                if isinstance(sub, list):
                    h = sym(sub[0])
                    if h == 'at' and len(sub) >= 3: at = (num(sub[1]), num(sub[2]))
                    elif h == 'size' and len(sub) >= 3: size = (num(sub[1]), num(sub[2]))
                    elif h == 'layers' and len(sub) >= 2: lay = sym(sub[1])
            pads.append(dict(num=sym(node[1]), at=at, size=size, layer=lay))
        elif sym(node[0]) in ('fp_line', 'fp_rect', 'fp_circle', 'fp_poly'):
            def pt(sub):
                for c in sub:
                    if isinstance(c, list) and sym(c[0]) in ('start', 'end', 'center', 'xy') and len(c) >= 3:
                        return (num(c[1]), num(c[2]))
                return (None, None)
            if sym(node[0]) in ('fp_line', 'fp_rect'):
                a = pt(node)
                b = (None, None)
                for c in node:
                    if isinstance(c, list) and sym(c[0]) in ('end', 'start') and len(c) >= 3:
                        b = (num(c[1]), num(c[2]))
                if None not in (a[0], a[1], b[0], b[1]):
                    xs.extend([a[0], b[0]]); ys.extend([a[1], b[1]])
    bbox = (round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)) if xs else None
    md5 = os.popen('md5sum %s' % path).read().split()[0]
    return dict(lib=lib, name=name, path=path, pads=pads, bbox=bbox, md5=md5,
                npad=len(pads))


CANDS = [
    ('Resistor_SMD', 'R_0402_1005Metric'),
    ('Resistor_SMD', 'R_0603_1608Metric'),
    ('Resistor_SMD', 'R_0805_2012Metric'),
    ('Resistor_SMD', 'R_1206_3216Metric'),
    ('Capacitor_SMD', 'C_0402_1005Metric'),
    ('Capacitor_SMD', 'C_0603_1608Metric'),
    ('Capacitor_SMD', 'C_0805_2012Metric'),
    ('Capacitor_SMD', 'C_1206_3216Metric'),
    ('LED_SMD', 'LED_0603_1608Metric'),
    ('LED_SMD', 'LED_0805_2012Metric'),
    ('Inductor_SMD', 'L_0603_1608Metric'),
    ('Inductor_SMD', 'L_0805_2012Metric'),
    ('Inductor_SMD', 'L_1206_3216Metric'),
    ('Diode_SMD', 'D_SOD-523'),
    ('Diode_SMD', 'D_SOD-123'),
    ('Diode_SMD', 'D_SMB'),
    ('Package_TO_SOT_SMD', 'SOT-23'),
    ('Package_TO_SOT_SMD', 'SOT-143'),
    ('Connector_PinHeader_1.27mm', 'PinHeader_1x04_P1.27mm_Vertical'),
    ('Connector_PinHeader_2.54mm', 'PinHeader_1x04_P2.54mm_Vertical'),
]

if __name__ == '__main__':
    out = {}
    for lib, name in CANDS:
        m = measure(lib, name)
        if m is None:
            print('MISS  %s:%s' % (lib, name)); continue
        out['%s:%s' % (lib, name)] = m
        print('OK    %s:%s  npad=%d bbox=%s md5=%s' % (lib, name, m['npad'], m['bbox'], m['md5']))
        for p in m['pads']:
            print('        pad %-4s at=%-22s size=%s' % (p['num'], p['at'], p['size']))
    json.dump(out, open('logs/iss356/lib_cand_geometry.json', 'w'), ensure_ascii=False, indent=1)
    print('wrote logs/iss356/lib_cand_geometry.json')
