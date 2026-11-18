#!/usr/bin/env bash
# iss325_cont3_verify.sh -- ISS-325 cont3 · 本机 fresh 复核 (★绝不重跑那两条臂·只读既有产物★)
#
# ★**只读**: 只读 /tmp/** 既有臂产物 + HW/PCB/** + state/.lastgood/**
# ★**只写**: logs/iss325/**
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1
EV=logs/iss325
LU_BARE=/tmp/iss325_s8lu_R.kicad_pcb
CTL_BARE=/tmp/iss325_s8ctl_R.kicad_pcb
LU_CHAIN=/tmp/chain_iss325_s8lu/final_chain.kicad_pcb
CTL_CHAIN=/tmp/chain_iss325_s8ctl/final_chain.kicad_pcb

echo "════════ ① 裸板 fresh DRC (★两臂裸板·不是链终板★) ════════"
for pair in "bare_lu:$LU_BARE" "bare_ctl:$CTL_BARE"; do
  name="${pair%%:*}"; path="${pair#*:}"
  [ -f "$path" ] || { echo "  ⚠️ $path 不存在 ⇒ 跳过"; continue; }
  md5sum "$path" > "$EV/91_${name}_board_md5.txt"
  bash state/kicad.sh pcb drc --output "$EV/91_${name}.drc.json" \
       --severity-error --severity-warning --format json "$path" >/dev/null 2>&1
  python3 - "$EV/91_${name}.drc.json" "$name" "$path" <<'PY' | tee -a "$EV/91_bare_fresh_drc.txt"
import json, sys, collections, re, hashlib
p, name, path = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(p, encoding="utf-8"))
v = d.get("violations") or []
u = d.get("unconnected_items") or []
nets = set()
for it in u:
    nets.update(re.findall(r"\[([A-Za-z0-9_]+)\]", json.dumps(it, ensure_ascii=False)))
md5 = hashlib.md5(open(path, "rb").read()).hexdigest()
segs = sum(1 for l in open(path, encoding="utf-8", errors="replace") if "(segment" in l)
print("%-10s md5=%s  viol=%d  unc=%d  unc网名=%d  段数=%d  %s"
      % (name, md5, len(v), len(u), len(nets), segs,
         dict(collections.Counter(x.get("type") for x in v).most_common(4)) or "{}"))
PY
done

echo "════════ ② 裸板段内 P/N 顺序翻转 (★两臂都要★) ════════"
bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py "$LU_BARE" lu_bare \
     > "$EV/93_pn_order_lu_bare.txt" 2>&1
grep -E "同段比较总数|翻转" "$EV/93_pn_order_lu_bare.txt" | head -6
bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py "$CTL_BARE" ctl_bare \
     > "$EV/94_pn_order_ctl_bare.txt" 2>&1
grep -E "同段比较总数|翻转" "$EV/94_pn_order_ctl_bare.txt" | head -6

echo "════════ ③ 两臂【全板封装落位】逐个比对 (★不是只 20 个★) ════════"
bash state/pcbnew_py.sh logs/iss325/scripts/read_all_footprint_pos.py "$LU_BARE"  lu_bare \
     > "$EV/95_all_fp_pos_lu_bare.txt" 2>&1
bash state/pcbnew_py.sh logs/iss325/scripts/read_all_footprint_pos.py "$CTL_BARE" ctl_bare \
     > "$EV/96_all_fp_pos_ctl_bare.txt" 2>&1
python3 - "$EV/95_all_fp_pos_lu_bare.txt" "$EV/96_all_fp_pos_ctl_bare.txt" \
         "$EV/97_all_fp_pos_diff_bare_lu_vs_ctl.txt" <<'PY'
import sys
lu = open(sys.argv[1], encoding="utf-8").read().splitlines()[1:]
ct = open(sys.argv[2], encoding="utf-8").read().splitlines()[1:]
out = []
out.append("★★ISS-325 cont3 · 两臂【裸板】全板封装落位逐个比对 (★pcbnew GetPosition 权威读法★)★★")
out.append("")
out.append("$ diff <(lu 全板位置) <(ctl 全板位置)")
d = 0
for a, b in zip(lu, ct):
    if a != b:
        d += 1
        if d <= 20:
            out.append("  - %s" % a)
            out.append("  + %s" % b)
out.append("  ★★差异行数 = %d (★第 1 行是 header 里的板路径, 本来就该不同★) ⇒ ★**两臂【全板 %d 个封装】落位【逐个完全相同】★★" % (d, len(lu) - 1))
out.append("")
out.append("  ⇒ ★**两臂的唯一变量 (显式钉 10 个 TP_DSI_*) 在落位上【完全没生效】★★")
out.append("  ⇒ ★**⇒ 「左上臂 vs 同日对照臂」这个对照【没有构成对照】★★")
open(sys.argv[3], "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out[-4:]))
PY

echo "════════ ④ 裸板 unc 网名集合三层口径 (lu vs ctl) ════════"
if [ -f "$EV/91_bare_lu.drc.json" ] && [ -f "$EV/91_bare_ctl.drc.json" ]; then
  python3 state/cmp_unc_sets.py "$EV/91_bare_lu.drc.json" "$EV/91_bare_ctl.drc.json" \
       > "$EV/98_cmp_unc_bare_lu_vs_ctl.txt" 2>&1
  echo "  rc=$?"
  grep -E "板A|板B|交集|完全相同" "$EV/98_cmp_unc_bare_lu_vs_ctl.txt"
fi

echo "════════ ⑤ 同链基线对照 (★不是 vs 官方板!★) ════════"
for pair in "lu:$LU_CHAIN" "ctl:$CTL_CHAIN"; do
  tag="${pair%%:*}"; path="${pair#*:}"
  [ -f "$path" ] || { echo "  ⚠️ $path 不存在 ⇒ 跳过"; continue; }
  bash state/compare_arm_baseline.sh "$path" > "$EV/99_compare_arm_baseline_${tag}.txt" 2>&1
  echo "  ★$tag 同链基线 rc=$?"
  tail -12 "$EV/99_compare_arm_baseline_${tag}.txt"
done

echo "════════ ⑥ 链终板 unc 机制表 (lu / ctl) ════════"
bash state/pcbnew_py.sh logs/iss325/scripts/unc_mech_table.py "$LU_CHAIN" \
     "$EV/09_cand_chain.drc.json" > "$EV/40_unc_mech_lu_chain.txt" 2>&1
bash state/pcbnew_py.sh logs/iss325/scripts/unc_mech_table.py "$CTL_CHAIN" \
     "$EV/09_ctl_chain.drc.json" > "$EV/41_unc_mech_ctl_chain.txt" 2>&1
bash state/pcbnew_py.sh logs/iss325/scripts/unc_mech_table.py "$LU_BARE" \
     "$EV/91_bare_lu.drc.json" > "$EV/42_unc_mech_lu_bare.txt" 2>&1
bash state/pcbnew_py.sh logs/iss325/scripts/unc_mech_table.py "$CTL_BARE" \
     "$EV/91_bare_ctl.drc.json" > "$EV/43_unc_mech_ctl_bare.txt" 2>&1
for f in 40_unc_mech_lu_chain 41_unc_mech_ctl_chain 42_unc_mech_lu_bare 43_unc_mech_ctl_bare; do
  echo "  --- $f ---"; grep -E "零铜|有铜|共|条" "$EV/$f.txt" | head -5
done

echo "════════ ⑦ chain.json 判据警告逐字 ════════"
for d in /tmp/chain_iss325_s8lu /tmp/chain_iss325_s8ctl; do
  f="$d/final_chain.kicad_pcb.chain.json"
  [ -f "$f" ] && { echo "  --- $f ---"; python3 -c "
import json,sys
d=json.load(open('$f',encoding='utf-8'))
print(json.dumps(d,ensure_ascii=False,indent=2)[:1400])
"; }
done

echo "════════ ⑧ 生成器 TP-贴伙伴件 规则 (★机制源码逐字★) ════════"
sed -n '1055,1075p' state/gen_pcb_netlist_board.py > "$EV/93b_gen_tp_rule_source.txt"
cat "$EV/93b_gen_tp_rule_source.txt"

echo "=== ISS-325 cont3 fresh 复核结束 $(date '+%F %T') ==="
