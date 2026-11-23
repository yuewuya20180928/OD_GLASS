#!/usr/bin/env python3
"""ISS-356 cont2 · 逐 ref 事实抽取 (只读) ⇒ 供 FP_TRUTH_BASELINE.md §2 表生成
输出: logs/iss356/target78_facts.json
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
LIBROOT = '/home/yuewuya/kicad/AppDir/share/kicad/footprints'

def load():
    bom = list(csv.DictReader(open(os.path.join(ROOT, 'HW/BOM_v1.csv'), encoding='utf-8')))
    pins = list(csv.DictReader(open(os.path.join(ROOT, 'HW/netlist_v1_pins.csv'), encoding='utf-8')))
    fps = json.load(open(os.path.join(ROOT, 'logs/iss356/board_footprints_v2.json'), encoding='utf-8'))
    return bom, pins, fps

def targets(bom):
    return [r for r in bom
            if r['dnp'] == '必装' and r['type'] not in ('NET', 'TP')
            and r['footprint'] == '待定' and r['board'] == '镜脚主 PCB']

def main():
    bom, pins, fps = load()
    byref = {f['ref']: f for f in fps}
    pinmap = {}
    for p in pins:
        pinmap.setdefault(p['ref'], []).append(p)
    tg = targets(bom)
    out = []
    for r in tg:
        f = byref.get(r['ref'])
        pl = sorted(pinmap.get(r['ref'], []), key=lambda x: str(x['pin']))
        # 网表 pin 排序: 数字优先, 其次 pinN
        def key(p):
            s = str(p['pin'])
            return (0, int(s)) if s.isdigit() else (1, s)
        pl = sorted(pinmap.get(r['ref'], []), key=key)
        board_pads = [(p['num'], p['net'], p['size'], p['at']) for p in f['pads']] if f else []
        nl_pins = [(str(p['pin']), p['net']) for p in pl]
        out.append(dict(
            ref=r['ref'], type=r['type'], value=r['value'], dnp=r['dnp'],
            board=r['board'], page=r['page'], opn=r['opn'], evidence=r['evidence'],
            footprint_col=r['footprint'], memo=r['memo'][:160],
            on_board=bool(f),
            npad_board=f['npad'] if f else None,
            pad_nums=[p['num'] for p in f['pads']] if f else [],
            pad_sizes=[p['size'] for p in f['pads']] if f else [],
            pad_nets=[p['net'] for p in f['pads']] if f else [],
            fab_bbox=f['bbox'] if f else None,
            nl_pins=nl_pins,
            nl_count=len(nl_pins),
        ))
    json.dump(out, open(os.path.join(ROOT, 'logs/iss356/target78_facts.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('TARGETS=%d' % len(out))
    mism = [o for o in out if o['nl_count'] != o['npad_board']]
    print('PADCOUNT_MISMATCH=%d' % len(mism))
    for m in mism:
        print('  ', m['ref'], 'board_npad=', m['npad_board'], 'nl_pins=', m['nl_count'],
              'board_nets=', m['pad_nets'], 'nl=', m['nl_pins'])
    # 网络逐位核对 (板面 pad 序 vs 网表 pin 序)
    netdiff = []
    for o in out:
        if o['npad_board'] is None:
            continue
        bn = [n for _, n in [(p['num'], p['net']) for p in byref[o['ref']]['pads']]]
        nn = [n for _, n in o['nl_pins']]
        if len(bn) == len(nn) and bn != nn:
            netdiff.append((o['ref'], bn, nn))
    print('NET_ORDER_DIFF=%d' % len(netdiff))
    for d in netdiff:
        print('  ', d)

if __name__ == '__main__':
    main()
