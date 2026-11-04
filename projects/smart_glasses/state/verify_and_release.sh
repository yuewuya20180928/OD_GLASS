#!/usr/bin/env bash
# verify_and_release.sh —— ★"我自己验 + 放行"一条龙 (2026-11-05 03:3x)
# 用法: bash state/verify_and_release.sh
# 目的: ① 不信子 agent 回执, 自己跑一遍 DRC + 全部门禁 ② 板子过了就重出投产资料包
#       ③ 用**实测值**写回 HW/PCB/.layout_done.json (阶段门靠它判 G1) ④ 跑阶段门
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
PCB=HW/PCB/demo_mainboard.kicad_pcb

echo "=========== 1. 板文件与布线留证 ==========="
ls -l --time-style=+%m-%d\ %H:%M:%S "$PCB" HW/PCB/.layout_done.json 2>/dev/null
echo "-- 走线/过孔计数 --"
echo "segment: $(grep -c '^\s*(segment' "$PCB")"
echo "via    : $(grep -c '^\s*(via' "$PCB")"

echo "=========== 2. DRC (含 unconnected) ==========="
bash state/kicad.sh pcb drc --output /tmp/_rel_drc.json --severity-error --severity-warning --format json "$PCB" >/dev/null 2>&1
python3 - <<'PY'
import json, collections, re
d = json.load(open('/tmp/_rel_drc.json'))
v = d.get('violations') or []
u = d.get('unconnected_items') or []
print(f"DRC violations = {len(v)}   unconnected items = {len(u)}")
for x in v[:8]:
    print("  -", x.get('type'), str(x.get('description'))[:100])
nets = collections.Counter()
for x in u:
    for it in (x.get('items') or []):
        for m in re.findall(r'\[([^\]]+)\]', str(it.get('description'))):
            nets[m] += 1
print("  未连接网 top12:", nets.most_common(12))
PY

echo "=========== 2b. 差分对全审计 (22 对: 缺铜/单边零铜/Δ/真实净距) ==========="
if [ -f /home/yuewuya/.openclaw/workspace/tools/diff_pair_audit.py ]; then
  python3 /home/yuewuya/.openclaw/workspace/tools/diff_pair_audit.py 2>&1 | head -40
else
  echo "  (审计工具未找到)"
fi

echo "=========== 3. 门禁 (全绿才算过) ==========="
python3 state/check_pcb_drc.py --strict; echo "  check_pcb_drc(--strict) rc=$?"
bash state/pcbnew_py.sh state/check_pcb_nets.py >/dev/null 2>&1; echo "  check_pcb_nets rc=$?"
python3 state/check_sch_loadable.py >/dev/null 2>&1; echo "  check_sch_loadable rc=$?"
python3 state/check_netlist.py >/dev/null 2>&1; echo "  check_netlist rc=$?"
python3 state/check_netlist_pins.py >/dev/null 2>&1; echo "  check_netlist_pins rc=$?"
python3 state/check_kicad_net.py >/dev/null 2>&1; echo "  check_kicad_net rc=$?"
python3 state/check_schematic_slots.py >/dev/null 2>&1; echo "  check_schematic_slots rc=$?"
python3 state/issue_check.py >/dev/null 2>&1; echo "  issue_check rc=$?"

echo "=========== 4. 重出投产资料包 (板变了 ⇒ 旧 Gerber 作废) ==========="
bash state/gen_production_pack.sh 2>&1 | tail -n 6

echo "=========== 5. 用实测值写回 .layout_done.json ==========="
python3 - <<'PY'
import json, time
d = json.load(open('/tmp/_rel_drc.json'))
v = len(d.get('violations') or [])
u = len(d.get('unconnected_items') or [])
pcb = 'HW/PCB/demo_mainboard.kicad_pcb'
seg = sum(1 for L in open(pcb, encoding='utf-8') if L.lstrip().startswith('(segment'))
via = sum(1 for L in open(pcb, encoding='utf-8') if L.lstrip().startswith('(via'))
out = {"unconnected": u, "drc_violations": v, "tracks": seg, "vias": via,
       "at": time.strftime('%Y-%m-%dT%H:%M:%S'), "verified_by": "main (verify_and_release.sh)"}
json.dump(out, open('HW/PCB/.layout_done.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
PY

echo "=========== 6. 生产链准入/准出 ==========="
python3 state/chain_gate.py --full; echo "  chain_gate rc=$?"

echo "=========== 7. 阶段门 ==========="
python3 state/stage_gate.py 2>&1 | grep -E "^【|当前在|已跳过|缺实测|未布线"; echo "  stage_gate rc=$?"
