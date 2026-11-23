#!/usr/bin/env python3
"""ISS-354 只读测量: demo_mainboard.kicad_pcb 里指定 ref 的封装焊盘/外形实测.
不写板, 只读 + 打印. 输出落 tmp/iss354/."""
import re, sys, json

PCB = 'HW/PCB/demo_mainboard.kicad_pcb'

def blocks(txt):
    res = []
    i = 0
    while True:
        j = txt.find('(footprint ', i)
        if j < 0:
            break
        depth = 0
        k = j
        while k < len(txt):
            c = txt[k]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        res.append(txt[j:k+1])
        i = k + 1
    return res

def sub_blocks(b, keyword):
    """取 footprint 块内 keyword 开头的顶层子块 (括号配对)."""
    res = []
    i = 0
    while True:
        j = b.find('(' + keyword, i)
        if j < 0:
            break
        # 确认是 '(keyword' 后跟空白或 (
        after = b[j+1+len(keyword):j+2+len(keyword)]
        if after not in (' ', '\t', '\n', '(', '"'):
            i = j + 1
            continue
        depth = 0
        k = j
        while k < len(b):
            c = b[k]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        res.append(b[j:k+1])
        i = k + 1
    return res

def num(s):
    return float(s)

def measure(txt, targets):
    out = {}
    for b in blocks(txt):
        m = re.search(r'\(property "Reference" "([^"]+)"', b)
        if not m:
            continue
        ref = m.group(1)
        if ref not in targets:
            continue
        d = {'ref': ref}
        mv = re.search(r'\(property "Value" "([^"]*)"', b)
        d['value'] = mv.group(1) if mv else None
        # 位置
        mp = re.search(r'\n\t\t\(at ([-\d\.]+) ([-\d\.]+)\)', b)
        d['at'] = [float(mp.group(1)), float(mp.group(2))] if mp else None
        # pads
        pads = []
        for pb in sub_blocks(b, 'pad '):
            pn = re.match(r'\(pad "([^"]*)"', pb)
            pt = re.search(r'\(pad "([^"]*)" (\w+) (\w+)', pb)
            pa = re.search(r'\(at ([-\d\.]+) ([-\d\.]+)', pb)
            ps = re.search(r'\(size ([-\d\.]+) ([-\d\.]+)\)', pb)
            pn_ = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pb)
            pads.append({
                'num': pt.group(1) if pt else None,
                'type': pt.group(2) if pt else None,
                'shape': pt.group(3) if pt else None,
                'at': [float(pa.group(1)), float(pa.group(2))] if pa else None,
                'size': [float(ps.group(1)), float(ps.group(2))] if ps else None,
                'net': pn_.group(1) if pn_ else None,
            })
        d['pads'] = pads
        d['pad_numbers'] = [p['num'] for p in pads]
        # fp_line / fp_rect 图形 => 外形 bbox (按 layer 分组)
        layer_pts = {}
        for lb in sub_blocks(b, 'fp_line'):
            st = re.search(r'\(start ([-\d\.]+) ([-\d\.]+)\)', lb)
            en = re.search(r'\(end ([-\d\.]+) ([-\d\.]+)\)', lb)
            ly = re.search(r'\(layer "([^"]+)"\)', lb)
            if not (st and en and ly):
                continue
            layer_pts.setdefault(ly.group(1), []).extend([
                (float(st.group(1)), float(st.group(2))),
                (float(en.group(1)), float(en.group(2)))])
        for lb in sub_blocks(b, 'fp_rect'):
            st = re.search(r'\(start ([-\d\.]+) ([-\d\.]+)\)', lb)
            en = re.search(r'\(end ([-\d\.]+) ([-\d\.]+)\)', lb)
            ly = re.search(r'\(layer "([^"]+)"\)', lb)
            if not (st and en and ly):
                continue
            layer_pts.setdefault(ly.group(1), []).extend([
                (float(st.group(1)), float(st.group(2))),
                (float(en.group(1)), float(en.group(2)))])
        bbox = {}
        for ly, pts in layer_pts.items():
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            bbox[ly] = {'x': [min(xs), max(xs)], 'w': round(max(xs)-min(xs), 4),
                        'y': [min(ys), max(ys)], 'h': round(max(ys)-min(ys), 4)}
        d['outline_bbox'] = bbox
        # 焊盘整体 bbox
        if pads and all(p['at'] for p in pads):
            xs = [p['at'][0] for p in pads]
            ys = [p['at'][1] for p in pads]
            d['pad_bbox'] = {'x': [min(xs), max(xs)], 'w': round(max(xs)-min(xs), 4),
                             'y': [min(ys), max(ys)], 'h': round(max(ys)-min(ys), 4)}
        else:
            d['pad_bbox'] = None
        out[ref] = d
    return out

if __name__ == '__main__':
    targets = sys.argv[1:] or ['Q1', 'Q2', 'U_BATPROT', 'U_LDO_S28', 'U_SUPV']
    txt = open(PCB, encoding='utf-8').read()
    res = measure(txt, set(targets))
    for ref in targets:
        d = res.get(ref)
        print('=' * 72)
        if not d:
            print(f'REF {ref}: ★板文件里找不到该 ref 的 footprint 块★')
            continue
        print(f"REF {ref}  Value={d['value']!r}  at={d['at']}")
        print(f"  焊盘数={len(d['pads'])}  焊盘编号={d['pad_numbers']}")
        for p in d['pads']:
            print(f"    pad {p['num']:>3s} {p['type']:<6s} {p['shape']:<6s} at={p['at']} size={p['size']} net={p['net']!r}")
        if d['pad_bbox']:
            print(f"  焊盘组 bbox: w={d['pad_bbox']['w']} h={d['pad_bbox']['h']}  x={d['pad_bbox']['x']} y={d['pad_bbox']['y']}")
        for ly, bb in sorted(d['outline_bbox'].items()):
            print(f"  外形 {ly:<12s} w={bb['w']} h={bb['h']}")
