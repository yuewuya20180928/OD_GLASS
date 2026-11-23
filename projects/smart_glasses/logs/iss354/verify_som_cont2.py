#!/usr/bin/env python3
"""ISS-354 cont2 独立复算 (只读): SoM 4 座排向/镜像兼容/几何 + 官方库逐焊盘比对 + 脚表判据."""
import re, os, csv, json

ROOT = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
PCB = os.path.join(ROOT, 'HW/PCB/demo_mainboard.kicad_pcb')
KICAD_FP = '/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_Hirose_DF40.pretty'

def blocks(txt, kw='(footprint '):
    res, i = [], 0
    while True:
        j = txt.find(kw, i)
        if j < 0: break
        d, k = 0, j
        while k < len(txt):
            if txt[k] == '(': d += 1
            elif txt[k] == ')':
                d -= 1
                if d == 0: break
            k += 1
        res.append(txt[j:k+1]); i = k+1
    return res

def sub_blocks(b, keyword):
    res, i = [], 0
    while True:
        j = b.find('(' + keyword, i)
        if j < 0: break
        after = b[j+1+len(keyword):j+2+len(keyword)]
        if after not in (' ', '\t', '\n', '(', '"'):
            i = j+1; continue
        d, k = 0, j
        while k < len(b):
            if b[k] == '(': d += 1
            elif b[k] == ')':
                d -= 1
                if d == 0: break
            k += 1
        res.append(b[j:k+1]); i = k+1
    return res

txt = open(PCB, encoding='utf-8').read()
som_refs = ['J_SOM_P1','J_SOM_P2','J_SOM_P3','J_SOM_P4']
data = {}
for b in blocks(txt):
    m = re.search(r'\(property "Reference" "([^"]+)"', b)
    if not m or m.group(1) not in som_refs: continue
    ref = m.group(1)
    rot = re.search(r'\n\t\t\(at ([-\d\.]+) ([-\d\.]+)\)', b)
    val = re.search(r'\(property "Value" "([^"]*)"', b)
    pads = []
    for pb in sub_blocks(b, 'pad '):
        num = re.match(r'\(pad "([^"]*)"', pb).group(1)
        at  = re.search(r'\(at ([-\d\.]+) ([-\d\.]+)', pb)
        sz  = re.search(r'\(size ([-\d\.]+) ([-\d\.]+)\)', pb)
        net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pb)
        pads.append((num, float(at.group(1)), float(at.group(2)),
                     float(sz.group(1)), float(sz.group(2)), net.group(1) if net else None))
    data[ref] = {'rot': rot.groups() if rot else None, 'pads': pads,
                 'val': val.group(1) if val else None}

odd_all, even_all = {}, {}
print('='*78)
for ref in som_refs:
    d = data[ref]
    withnet = [p for p in d['pads'] if p[5]]
    od = [p for p in withnet if int(p[0]) % 2 == 1]
    ev = [p for p in withnet if int(p[0]) % 2 == 0]
    print(f"{ref}: 焊盘总数={len(d['pads'])}  带网={len(withnet)}  at={d['rot']}")
    print(f"   Value = {d['val']}")
    print(f"   奇数脚 {len(od)} @ y={sorted(set(round(p[2],3) for p in od))}   偶数脚 {len(ev)} @ y={sorted(set(round(p[2],3) for p in ev))}")
    for p in od: odd_all.setdefault(p[5], []).append(f'{ref}.{p[0]}')
    for p in ev: even_all.setdefault(p[5], []).append(f'{ref}.{p[0]}')

both = sorted(set(odd_all) & set(even_all))
only_odd = sorted(set(odd_all) - set(even_all))
only_even = sorted(set(even_all) - set(odd_all))
allnet = sorted(set(odd_all) | set(even_all))
print('='*78)
print(f'唯一网名总数 = {len(allnet)}')
print(f'  奇数排独占 = {len(only_odd)}   偶数排独占 = {len(only_even)}   两排都出现 = {len(both)} -> {both}')
print(f'  => 单排独占合计 = {len(only_odd)+len(only_even)} / 总 {len(allnet)}')
for n in both:
    print(f'     {n}: 奇排 {odd_all[n]}  偶排 {even_all[n]}')

# ── 官方 KiCad 专用库 (Connector_Hirose_DF40.pretty) 逐焊盘比对 ──
lib = os.path.join(KICAD_FP, 'Hirose_DF40C-100DS-0.4V_2x50_P0.4mm.kicad_mod')
print('='*78)
print('官方专用库封装:', lib, '存在 =', os.path.exists(lib))
if os.path.exists(lib):
    off = open(lib, encoding='utf-8').read()
    opads = {}
    for pb in sub_blocks(off, 'pad '):
        num = re.match(r'\(pad "([^"]*)"', pb).group(1)
        at  = re.search(r'\(at ([-\d\.]+) ([-\d\.]+)(?: ([-\d\.]+))?\)', pb)
        sz  = re.search(r'\(size ([-\d\.]+) ([-\d\.]+)\)', pb)
        opads[num] = (float(at.group(1)), float(at.group(2)),
                      float(sz.group(1)), float(sz.group(2)),
                      float(at.group(3)) if at.group(3) else 0.0)
    print(f'  官方封装焊盘数 = {len(opads)}  官方 F.Fab 外形: ', end='')
    fab=[]
    for lb in sub_blocks(off,'fp_line'):
        ly=re.search(r'\(layer "([^"]+)"\)',lb)
        if ly and ly.group(1)=='F.Fab':
            st=re.search(r'\(start ([-\d\.]+) ([-\d\.]+)\)',lb); en=re.search(r'\(end ([-\d\.]+) ([-\d\.]+)\)',lb)
            fab.extend([(float(st.group(1)),float(st.group(2))),(float(en.group(1)),float(en.group(2)))])
    if fab:
        xs=[p[0] for p in fab]; ys=[p[1] for p in fab]
        print(f'{round(max(xs)-min(xs),4)} x {round(max(ys)-min(ys),4)}')
    for ref in som_refs:
        d = data[ref]
        bp = {p[0]: (p[1], p[2], p[3], p[4]) for p in d['pads']}
        ok = 0; bad = []
        for num, (ox, oy, ox2, oy2, orot) in opads.items():
            want = (-ox, -oy)          # 板面是 180° 旋转
            if num in bp:
                bxx, byy, bsx, bsy = bp[num]
                if abs(bxx-want[0])<1e-6 and abs(byy-want[1])<1e-6 and abs(bsx-ox2)<1e-6 and abs(bsy-oy2)<1e-6:
                    ok += 1
                else:
                    bad.append((num,(bxx,byy),(bsx,bsy),'want',want,(ox2,oy2)))
            else:
                bad.append((num,'MISSING_ON_BOARD',None,None,None,None))
        print(f'  {ref}: 与官方库 (180° 旋转) 逐焊盘一致 {ok}/{len(opads)}   不一致 {len(bad)}')
        if bad[:4]: print('     样例:', bad[:4])
    # 几何
    xs = sorted(set(round(p[1],4) for p in data['J_SOM_P1']['pads']))
    ys = sorted(set(round(p[2],4) for p in data['J_SOM_P1']['pads']))
    print(f'  板面 J_SOM_P1: x 跨距={round(xs[-1]-xs[0],4)} 脚距={round(xs[1]-xs[0],4)} y={ys} 排中心距={round(ys[-1]-ys[0],4)}')
    print(f'  板面焊盘尺寸 = {data["J_SOM_P1"]["pads"][0][3]} x {data["J_SOM_P1"]["pads"][0][4]}')
    print(f'  Hirose 原厂图: 焊盘宽 0.2 · 焊盘长 (3.78-2.38)/2={round((3.78-2.38)/2,3)} · 排中心距 (3.78+2.38)/2={round((3.78+2.38)/2,3)} · 跨距 19.6')

# ── FET3572C 脚表判据 ──
print('='*78)
rows = list(csv.DictReader(open(os.path.join(ROOT,'HW/PCB/FET3572C_PIN_TABLE.csv'), encoding='utf-8')))
for r in rows:
    if r['conn']=='P2' and r['num'] in ('1','2'):
        print(f"  官方脚表 P2 pin{r['num']}: signal={r['signal']}  vol={r['vol']}  desc={r['desc']}")
