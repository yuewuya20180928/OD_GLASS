#!/usr/bin/env bash
# board_report.sh —— ★**落板后一键取证** (2026-11-05 07:40)
# 用法: bash state/board_report.sh [板路径]   (默认官方板)
# 输出: ① 板上图元数 ② 日志三看 ③ GND 未连核对 ④ 22 对差分全审计 ⑤ 失败脚数 ⑥ 门禁 rc
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
PCB="${1:-HW/PCB/demo_mainboard.kicad_pcb}"
LOG="${2:-/tmp/gen_v25.log}"

echo "══════ ① 板上图元 (机器读数) ══════"
printf "板文件      : %s\n" "$PCB"
printf "mtime/size  : %s\n" "$(ls -la --time-style=+%H:%M:%S "$PCB" | awk '{print $6, $5"字节"}')"
printf "走线段数    : %s\n" "$(grep -c '(segment' "$PCB")"
printf "过孔数      : %s\n" "$(grep -c '(via' "$PCB")"

echo "══════ ② 落板三看 (日志) ══════"
grep -E "\[CLEAN\]|落板自检|\[SUM \]|已原子替换|判定:|EXIT=" "$LOG" | tail -8

echo "══════ ③ GND 未连核对 ══════"
grep -E "\[GND \]" "$LOG" | tail -2
cat > /tmp/_gnd_nocopper.py <<'PY'
import pcbnew, collections
mm=1e6
b = pcbnew.LoadBoard("HW/PCB/demo_mainboard.kicad_pcb")
ends=collections.defaultdict(list); vias=collections.defaultdict(list)
for t in b.GetTracks():
    n=t.GetNetname()
    if t.Type()==pcbnew.PCB_VIA_T:
        p=t.GetPosition(); vias[n].append((p.x/mm,p.y/mm))
    else:
        a=t.GetStart(); e=t.GetEnd()
        ends[n].append((a.x/mm,a.y/mm)); ends[n].append((e.x/mm,e.y/mm))
noc=0; names=[]
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname().upper()!="GND": continue
        bb=p.GetBoundingBox(); x0,y0,x1,y1 = bb.GetLeft()/mm,bb.GetTop()/mm,bb.GetRight()/mm,bb.GetBottom()/mm
        hit=any(x0-.01<=vx<=x1+.01 and y0-.01<=vy<=y1+.01 for vx,vy in vias.get("GND",[])) or \
            any(x0-.01<=tx<=x1+.01 and y0-.01<=ty<=y1+.01 for tx,ty in ends.get("GND",[]))
        if not hit: noc+=1; names.append("%s.%s"%(fp.GetReference(),p.GetNumber()))
print("  GND 焊盘无铜数: %d (目标 0)  %s" % (noc, names[:12]))
PY
bash state/pcbnew_py.sh /tmp/_gnd_nocopper.py 2>&1 | tail -2

echo "══════ ④ 差分对全审计 (22 对) ══════"
python3 ../../tools/diff_pair_audit.py "$PCB" 2>&1 | tail -14

echo "══════ ⑤ 失败脚 (state/_fail_detail.json) ══════"
python3 -c "
import json,collections
d=json.load(open('state/_fail_detail.json'))
print('  布不动的脚: %d' % len(d))
c=collections.Counter(e['net'] for e in d)
print('  最差 6 个网:', c.most_common(6))
"

echo "══════ ⑥ 门禁 rc ══════"
bash state/pcbnew_py.sh state/check_pcb_nets.py "$PCB" >/tmp/_c1.log 2>&1; echo "  check_pcb_nets  rc=$?"
bash state/pcbnew_py.sh state/check_pcb_drc.py "$PCB" >/tmp/_c2.log 2>&1; echo "  check_pcb_drc   rc=$?"
grep -E "unconnected|violations" /tmp/_c2.log | tail -3
python3 state/chain_gate.py >/tmp/_c3.log 2>&1; echo "  chain_gate      rc=$?"
python3 state/stage_gate.py >/tmp/_c4.log 2>&1; echo "  stage_gate      rc=$?"
ls -la --time-style=+%H:%M:%S state/.auto_release_done 2>/dev/null || echo "  ★放行章 .auto_release_done 不存在 ⇒ 未放行"
