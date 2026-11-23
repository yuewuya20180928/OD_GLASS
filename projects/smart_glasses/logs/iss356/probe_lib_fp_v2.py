#!/usr/bin/env python3
"""ISS-356 只读探针 v2: 分层量 KiCad 官方库 .kicad_mod 的几何。
★F.Fab = 本体外形 (用来判「本体尺寸能否落进现占位 fab bbox」)
★F.CrtYd = courtyard (真实占位, 用来判间距)
★pads = land pattern (焊盘号/尺寸/at 偏移)
零写板: 只读。
"""
import os, sys, json

FP = '/home/yuewuya/kicad/AppDir/share/kicad/footprints'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_board import tokenize, parse, sym, num


def _pts_of(node):
    """取一个 fp_* 节点的所有坐标点"""
    out = []
    for c in node:
        if isinstance(c, list) and sym(c[0]) in ('start', 'end', 'center', 'xy', 'mid'):
            if len(c) >= 3:
                out.append((num(c[1]), num(c[2])))
            elif len(c) == 2 and isinstance(c[1], list):
                pass
    return out


def measure(lib, name):
    path = os.path.join(FP, '%s.pretty' % lib, '%s.kicad_mod' % name)
    if not os.path.isfile(path):
        return None
    root = parse(tokenize(open(path, encoding='utf-8').read()))[0]
    pads, fab, crtyd, silk = [], [], [], []
    for node in root:
        if not isinstance(node, list):
            continue
        h = sym(node[0])
        if h == 'pad':
            at = size = None
            for sub in node:
                if isinstance(sub, list):
                    sh = sym(sub[0])
                    if sh == 'at' and len(sub) >= 3: at = (num(sub[1]), num(sub[2]))
                    elif sh == 'size' and len(sub) >= 3: size = (num(sub[1]), num(sub[2]))
            pads.append(dict(num=sym(node[1]), at=at, size=size))
        elif h in ('fp_line', 'fp_rect', 'fp_circle', 'fp_poly', 'fp_arc'):
            pts = _pts_of(node)
            lay = None
            for sub in node:
                if isinstance(sub, list) and sym(sub[0]) == 'layer' and len(sub) >= 2:
                    lay = sym(sub[1])
            for p in pts:
                if lay == 'F.Fab': fab.append(p)
                elif lay == 'F.CrtYd': crtyd.append(p)
                elif lay == 'F.SilkS': silk.append(p)

    def bbox(pts):
        if not pts: return None
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        return (round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3))

    md5 = os.popen('md5sum %s' % path).read().split()[0]
    return dict(lib=lib, name=name, path=path, md5=md5, npad=len(pads), pads=pads,
                fab=bbox(fab), crtyd=bbox(crtyd), silk=bbox(silk),
                pad_pitch=(round(abs(pads[1]['at'][0] - pads[0]['at'][0]), 3)
                           if len(pads) == 2 and pads[0]['at'] and pads[1]['at'] else None))


CANDS = [
    ('Resistor_SMD', 'R_0402_1005Metric'), ('Resistor_SMD', 'R_0603_1608Metric'),
    ('Resistor_SMD', 'R_0805_2012Metric'), ('Resistor_SMD', 'R_1206_3216Metric'),
    ('Capacitor_SMD', 'C_0402_1005Metric'), ('Capacitor_SMD', 'C_0603_1608Metric'),
    ('Capacitor_SMD', 'C_0805_2012Metric'), ('Capacitor_SMD', 'C_1206_3216Metric'),
    ('LED_SMD', 'LED_0603_1608Metric'), ('LED_SMD', 'LED_0805_2012Metric'),
    ('Inductor_SMD', 'L_0603_1608Metric'), ('Inductor_SMD', 'L_0805_2012Metric'),
    ('Inductor_SMD', 'L_1206_3216Metric'), ('Inductor_SMD', 'L_6.3x6.3_H3'),
    ('Inductor_SMD_Wurth', 'L_Wurth_WE-LQSH-4020'),
    ('Diode_SMD', 'D_SOD-523'), ('Diode_SMD', 'D_SOD-323'), ('Diode_SMD', 'D_SOD-123'),
    ('Diode_SMD', 'D_SMB'),
    ('Package_TO_SOT_SMD', 'SOT-23'), ('Package_TO_SOT_SMD', 'SOT-143'),
    ('Package_SON', 'Texas_X2SON-4_1x1mm_P0.65mm'),
    ('Package_SON', 'WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm'),
    ('Package_DFN_QFN', 'UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm'),
    ('Package_DFN_QFN', 'QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm'),
    ('Package_DFN_QFN', 'Texas_RGE0024C_VQFN-24-1EP_4x4mm_P0.5mm_EP2.1x2.1mm'),
    ('Connector_PinHeader_1.27mm', 'PinHeader_1x04_P1.27mm_Vertical'),
    ('Connector_PinHeader_2.54mm', 'PinHeader_1x04_P2.54mm_Vertical'),
    ('Connector_FFC-FPC', 'Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal'),
    ('Connector_USB', 'USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal'),
    ('Button_Switch_SMD', 'SW_SPST_B3U-1000P'),
    ('NetTie', 'NetTie-2_SMD_Pad2.0mm'),
    ('TestPoint', 'TestPoint_Pad_D1.0mm'),
]

if __name__ == '__main__':
    out = {}
    for lib, name in CANDS:
        m = measure(lib, name)
        if not m:
            print('MISS  %s:%s' % (lib, name)); continue
        out['%s:%s' % (lib, name)] = m
        print('OK  %-52s npad=%-3d F.Fab=%-14s CrtYd=%-14s pitch=%s' % (
            lib + ':' + name, m['npad'], m['fab'], m['crtyd'], m['pad_pitch']))
        for p in m['pads']:
            print('        pad %-4s at=%-20s size=%s' % (p['num'], p['at'], p['size']))
    json.dump(out, open('logs/iss356/lib_cand_geometry_v2.json', 'w'), ensure_ascii=False, indent=1)
    print('wrote logs/iss356/lib_cand_geometry_v2.json')
