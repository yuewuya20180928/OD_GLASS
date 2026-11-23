#!/usr/bin/env python3
"""ISS-354 cont2 · BOM opn 列仍 [0数据] 的 ref 名单 (只读)."""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = list(csv.DictReader(open(os.path.join(ROOT, 'HW', 'BOM_v1.csv'), encoding='utf-8')))
z = [r for r in rows if (r.get('opn') or '').strip() == '[0数据]']
print(f'BOM 总行数 = {len(rows)}   opn == [0数据] 的 ref 数 = {len(z)}')
for r in z:
    print(f"  {r.get('ref'):<16s} 装={r.get('dnp',''):<6s} {(r.get('footprint') or '')[:46]}")
