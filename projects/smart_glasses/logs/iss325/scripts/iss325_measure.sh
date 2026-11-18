#!/usr/bin/env bash
# iss325_measure.sh -- ISS-325 交卷前测量总驱动 (★逐条读数·输出全部落盘★)
#
# ★**只读沙盒**: 只读 HW/PCB/** 与 state/.lastgood/** · 只写 logs/iss325/ 与 /tmp/**
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1
EV=logs/iss325
TAG=iss325_s8lu
CAND_CHAIN=/tmp/chain_${TAG}/final_chain.kicad_pcb
CAND_CLR=/tmp/_clrfix_${TAG}_final.kicad_pcb
CTL_TAG=iss325_s8ctl
CTL_CHAIN=/tmp/chain_${CTL_TAG}/final_chain.kicad_pcb
CTL_CLR=/tmp/_clrfix_${CTL_TAG}_final.kicad_pcb
OFFICIAL=HW/PCB/demo_mainboard.kicad_pcb
BEST23=state/.lastgood/best_unc23_clrfix.kicad_pcb

mkdir -p "$EV"

echo "════════ ① 零写板双证 ════════"
md5sum "$OFFICIAL" | tee "$EV/08_zero_write_proof.txt"
stat -c "%y" "$OFFICIAL" | tee -a "$EV/08_zero_write_proof.txt"

echo "════════ ② 三方 fresh DRC ════════"
for pair in "official:$OFFICIAL" "best23:$BEST23" "cand_chain:$CAND_CHAIN" "cand_clrfix:$CAND_CLR" "ctl_chain:$CTL_CHAIN" "ctl_clrfix:$CTL_CLR"; do
  name="${pair%%:*}"; path="${pair#*:}"
  if [ ! -f "$path" ]; then echo "  ⚠️ $name: 板不存在 ($path) ⇒ 跳过"; continue; fi
  md5sum "$path" > "$EV/09_${name}_board_md5.txt"
  bash state/kicad.sh pcb drc --output "$EV/09_${name}.drc.json" --severity-error --severity-warning --format json "$path" >/dev/null 2>&1
  python3 - "$EV/09_${name}.drc.json" "$name" "$path" <<'PY' | tee -a "$EV/09_threeway_fresh_drc.txt"
import json, sys, collections, os, hashlib
p, name, path = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(p, encoding="utf-8"))
v = d.get("violations") or []
u = d.get("unconnected_items") or []
nets = set()
for it in u:
    import re
    nets.update(re.findall(r"\[([A-Za-z0-9_]+)\]", json.dumps(it, ensure_ascii=False)))
md5 = hashlib.md5(open(path, "rb").read()).hexdigest()
segs = sum(1 for l in open(path, encoding="utf-8", errors="replace") if "(segment" in l)
print("%-12s md5=%s  viol=%d  unc=%d  unc网名=%d  段数=%d  %s"
      % (name, md5, len(v), len(u), len(nets), segs,
         dict(collections.Counter(x.get("type") for x in v).most_common(4)) or "{}"))
PY
done

echo "════════ ③ 名单制闸 (compare_arm_official) ════════"
python3 state/compare_arm_official.py --self-test > "$EV/10_compare_arm_official_selftest.txt" 2>&1
echo "  self-test rc=$? (★必须 0·ALL TESTS PASS★)"
tail -3 "$EV/10_compare_arm_official_selftest.txt"
if [ -f "$CAND_CLR" ]; then
  python3 state/compare_arm_official.py "$CAND_CLR" "$OFFICIAL" > "$EV/10_compare_arm_official_cand_vs_official.txt" 2>&1
  echo "  ★候选板 vs 官方板 rc=$?"
elif [ -f "$CAND_CHAIN" ]; then
  python3 state/compare_arm_official.py "$CAND_CHAIN" "$OFFICIAL" > "$EV/10_compare_arm_official_cand_vs_official.txt" 2>&1
  echo "  ★候选板(链终板) vs 官方板 rc=$?"
fi
if [ -f "$CTL_CLR" ] || [ -f "$CTL_CHAIN" ]; then
  CC="$CTL_CLR"; [ -f "$CC" ] || CC="$CTL_CHAIN"
  python3 state/compare_arm_official.py "$CC" "$OFFICIAL" > "$EV/10b_compare_arm_official_ctl_vs_official.txt" 2>&1
  echo "  ★对照臂 vs 官方板 rc=$?"
  python3 state/compare_arm_official.py "$CC" "$CAND_CLR" > "$EV/10c_compare_arm_official_ctl_vs_cand.txt" 2>&1
  echo "  ★对照臂 vs 左上限臂 rc=$?"
fi

echo "════════ ④ 网名集合三层口径 (cmp_unc_sets) ════════"
if [ -f "$EV/09_cand_clrfix.drc.json" ] || [ -f "$EV/09_cand_chain.drc.json" ]; then
  C="$EV/09_cand_clrfix.drc.json"; [ -f "$C" ] || C="$EV/09_cand_chain.drc.json"
  python3 state/cmp_unc_sets.py "$C" "$EV/09_official.drc.json" > "$EV/11_cmp_unc_cand_vs_official.txt" 2>&1
  echo "  cand vs official rc=$?"
  python3 state/cmp_unc_sets.py "$EV/09_best23.drc.json" "$EV/09_official.drc.json" > "$EV/11_cmp_unc_best23_vs_official.txt" 2>&1
  echo "  best23 vs official rc=$?"
  python3 state/cmp_unc_sets.py "$C" "$EV/09_best23.drc.json" > "$EV/11_cmp_unc_cand_vs_best23.txt" 2>&1
  echo "  cand vs best23 rc=$?"
  if [ -f "$EV/09_ctl_clrfix.drc.json" ] || [ -f "$EV/09_ctl_chain.drc.json" ]; then
    CC="$EV/09_ctl_clrfix.drc.json"; [ -f "$CC" ] || CC="$EV/09_ctl_chain.drc.json"
    python3 state/cmp_unc_sets.py "$CC" "$EV/09_official.drc.json" > "$EV/11b_cmp_unc_ctl_vs_official.txt" 2>&1
    echo "  ctl vs official rc=$?"
    python3 state/cmp_unc_sets.py "$C" "$CC" > "$EV/11c_cmp_unc_cand_vs_ctl.txt" 2>&1
    echo "  cand vs ctl rc=$?"
  fi
fi

echo "════════ ⑤ 段内 P/N 顺序翻转 ════════"
CAND="$CAND_CLR"; [ -f "$CAND" ] || CAND="$CAND_CHAIN"
if [ -f "$CAND" ]; then
  bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py "$CAND" cand > "$EV/12_pn_order_candidate.txt" 2>&1
  grep -E "同段比较总数|ISS-325 读数" "$EV/12_pn_order_candidate.txt"
fi
CC2="$CTL_CLR"; [ -f "$CC2" ] || CC2="$CTL_CHAIN"
if [ -f "$CC2" ]; then
  bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py "$CC2" ctl > "$EV/12b_pn_order_control.txt" 2>&1
  grep -E "同段比较总数|ISS-325 读数" "$EV/12b_pn_order_control.txt"
fi

echo "════════ ⑥ 图纸门禁 (候选板) ════════"
if [ -f "$CAND" ]; then
  python3 state/check_pcb_drc.py "$CAND" > "$EV/13_check_pcb_drc_candidate.txt" 2>&1
  echo "  rc=$?"
  grep -E "C3 |C4 |C7 |查板" "$EV/13_check_pcb_drc_candidate.txt"
fi

echo "════════ ⑦ 目标坐标复核 (候选板上 20 个器件真落位了吗) ════════"
if [ -f "$CAND" ]; then
  bash state/pcbnew_py.sh logs/iss325/scripts/read_part_pos_pcbnew.py "$CAND" "$EV/14_candidate_partpos_readback.tsv" 2>&1 | tail -25
fi

echo "════════ ⑧ 高速网机制级读数 (零铜 vs 长了一半) ════════"
if [ -f "$CAND" ]; then
  bash state/pcbnew_py.sh logs/iss325/scripts/hs_copper_amount_cand.py "$CAND" > "$EV/15_hs_copper_candidate.txt" 2>&1
  tail -40 "$EV/15_hs_copper_candidate.txt"
fi

echo "════════ ⑨ SoM 主体区逐层占布 ════════"
if [ -f "$CAND" ]; then
  bash state/pcbnew_py.sh logs/iss325/scripts/probe_som_body_cand.py "$CAND" > "$EV/16_som_body_candidate.txt" 2>&1
  tail -25 "$EV/16_som_body_candidate.txt"
fi

echo "════════ ⑩ 门禁链 ════════"
python3 state/merge.py > "$EV/17_gate_chain.txt" 2>&1; echo "  merge rc=$?" | tee -a "$EV/17_gate_chain.txt"
python3 state/gate_check.py >> "$EV/17_gate_chain.txt" 2>&1; echo "  gate_check rc=$?" | tee -a "$EV/17_gate_chain.txt"
python3 state/issue_check.py >> "$EV/17_gate_chain.txt" 2>&1; echo "  issue_check rc=$?" | tee -a "$EV/17_gate_chain.txt"
echo "=== ISS-325 测量总驱动结束 $(date '+%F %T') ==="
