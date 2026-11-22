#!/usr/bin/env bash
# ISS-328 · measure_ru_arm.sh -- ★右上臂收链读数采集器 (★口径照抄 ISS-325★)
#
# ★★★ 采集 6 条读数 (★任务书 §B-1 逐条·不许自创口径★) ★★★
#   ① 裸板 (排版阶段) DRC viol 数 + unc 条数 + unc 网名集合
#   ② 链终板 DRC viol 数 + unc 条数 + unc 网名集合
#   ③ 全板 185 封装落位 diff (右上臂 vs ★基线臂同链终板★ · 禁拿官方板比★)
#   ④ 链终几何: 走线段数 / 过孔数 / 铜皮区数 (state/cmp_pcb_geom.py 口径)
#   ⑤ 段内 P/N 顺序翻转数 (ISS-325 口径 · 分母 47)
#   ⑥ 名单制闸 rc (退铜名单 + 差分死腿 + 逐网孤岛)
#
# ★写盘只落 logs/iss328/ + tmp/iss328/ ⇒ 官方板一个字节都不碰 ★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1
SBX=$PROJ/tmp/iss328
LOGD=$PROJ/logs/iss328
FINAL=$SBX/chain_iss328_s8ru/final_chain.kicad_pcb
CLR=$SBX/_clrfix_iss328_s8ru_final.kicad_pcb
BASE=$SBX/baseline_ctl_chain.kicad_pcb
mkdir -p "$LOGD"

echo "=== ISS-328 右上臂 收链读数采集 $(date '+%F %T') ==="
[ -f "$FINAL" ] || { echo "❌ 没有链终板: $FINAL"; exit 2; }
[ -f "$BASE" ] || { echo "❌ 没有基线臂链终板: $BASE"; exit 2; }

echo "── 真板 md5/mtime (收数时) ──"
md5sum "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" | tee "$LOGD/30_zero_write_proof_post.txt"
stat -c '%y' "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" | tee -a "$LOGD/30_zero_write_proof_post.txt"

# ── ① 裸板 (排版阶段) fresh DRC ──
echo "── ① 裸板 (排版阶段) fresh DRC ──"
for t in base ru; do
  b="$SBX/bare_${t}.kicad_pcb"
  j="$LOGD/10_bare_${t}.drc.json"
  bash state/kicad.sh pcb drc --output "$j" --severity-error --severity-warning --format json "$b" >/dev/null 2>&1
done
python3 - "$LOGD/10_bare_base.drc.json" "$LOGD/10_bare_ru.drc.json" "$SBX/bare_base.kicad_pcb" "$SBX/bare_ru.kicad_pcb" <<'PY' | tee "$LOGD/11_bare_fresh_drc.txt"
import json, sys, collections, hashlib, re
def md5(p):
    h=hashlib.md5()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(1<<20), b''): h.update(b)
    return h.hexdigest()
for jp, bp in zip(sys.argv[1:3], sys.argv[3:5]):
    d=json.load(open(jp,encoding='utf-8'))
    v=d.get('violations') or []
    u=d.get('unconnected_items') or []
    nets=set()
    for it in u:
        s=json.dumps(it,ensure_ascii=False)
        nets |= set(re.findall(r"\[([A-Za-z0-9_]+)\]", s))
    segs=sum(1 for l in open(bp,encoding='utf-8',errors='ignore') if '(segment' in l)
    print("%-10s md5=%s  viol=%d  unc=%d  unc网名=%d  段数=%d  %s" % (
        bp.split('/')[-1].replace('.kicad_pcb',''), md5(bp), len(v), len(u), len(nets), segs,
        dict(collections.Counter(x.get('type') for x in v).most_common(6))))
    print("           unc网名集合 = %s" % (",".join(sorted(nets))))
PY

# ── ② 链终板 fresh DRC (右上臂 + 基线臂) ──
echo "── ② 链终板 fresh DRC ──"
for pair in "ru:$FINAL" "ctl:$BASE"; do
  tag="${pair%%:*}"; p="${pair#*:}"
  bash state/kicad.sh pcb drc --output "$LOGD/12_chain_${tag}.drc.json" --severity-error --severity-warning --format json "$p" >/dev/null 2>&1
done
if [ -f "$CLR" ]; then
  bash state/kicad.sh pcb drc --output "$LOGD/12_chain_ru_clrfix.drc.json" --severity-error --severity-warning --format json "$CLR" >/dev/null 2>&1
fi
python3 - "$LOGD/12_chain_ru.drc.json" "$LOGD/12_chain_ctl.drc.json" "$FINAL" "$BASE" "$LOGD/12_chain_ru_clrfix.drc.json" "$CLR" <<'PY' | tee "$LOGD/13_chain_fresh_drc.txt"
import json, sys, collections, hashlib, re, os
def md5(p):
    h=hashlib.md5()
    with open(p,'rb') as f:
        for b in iter(lambda: f.read(1<<20), b''): h.update(b)
    return h.hexdigest()
for jp, bp in zip(sys.argv[1:3], sys.argv[3:5]):
    d=json.load(open(jp,encoding='utf-8'))
    v=d.get('violations') or []
    u=d.get('unconnected_items') or []
    nets=set()
    for it in u:
        s=json.dumps(it,ensure_ascii=False)
        nets |= set(re.findall(r"\[([A-Za-z0-9_]+)\]", s))
    segs=sum(1 for l in open(bp,encoding='utf-8',errors='ignore') if '(segment' in l)
    print("%-12s md5=%s  viol=%d  unc=%d  unc网名=%d  段数=%d  %s" % (
        os.path.basename(bp), md5(bp), len(v), len(u), len(nets), segs,
        dict(collections.Counter(x.get('type') for x in v).most_common(6))))
    print("             unc网名集合 = %s" % (",".join(sorted(nets))))
for jp, bp in ((sys.argv[5], sys.argv[6]),):
    if os.path.isfile(jp) and os.path.isfile(bp):
        d=json.load(open(jp,encoding='utf-8'))
        v=d.get('violations') or []
        u=d.get('unconnected_items') or []
        nets=set()
        for it in u:
            s=json.dumps(it,ensure_ascii=False)
            nets |= set(re.findall(r"\[([A-Za-z0-9_]+)\]", s))
        segs=sum(1 for l in open(bp,encoding='utf-8',errors='ignore') if '(segment' in l)
        print("%-12s md5=%s  viol=%d  unc=%d  unc网名=%d  段数=%d  %s" % (
            os.path.basename(bp), md5(bp), len(v), len(u), len(nets), segs,
            dict(collections.Counter(x.get('type') for x in v).most_common(6))))
        print("             unc网名集合 = %s" % (",".join(sorted(nets))))
PY

# ── ③ 全板 185 封装落位 diff (右上臂链终 vs ★基线臂同链终★) ──
echo "── ③ 全板封装落位 diff (右上臂链终 vs 基线臂链终) ──"
bash state/pcbnew_py.sh "$SBX/dump_fp_pos.py" "$FINAL" > "$LOGD/14_all_fp_pos_ru_chain.tsv" 2>&1
bash state/pcbnew_py.sh "$SBX/dump_fp_pos.py" "$BASE"  > "$LOGD/15_all_fp_pos_ctl_chain.tsv" 2>&1
diff <(grep -v '^#' "$LOGD/15_all_fp_pos_ctl_chain.tsv") <(grep -v '^#' "$LOGD/14_all_fp_pos_ru_chain.tsv") > "$LOGD/16_all_fp_pos_diff_chain_ru_vs_ctl.txt"
D=$(grep -c '^[<>]' "$LOGD/16_all_fp_pos_diff_chain_ru_vs_ctl.txt")
echo "  ★差异行数 = $D (★涉及 $(grep '^[<>]' "$LOGD/16_all_fp_pos_diff_chain_ru_vs_ctl.txt" | awk '{print $2}' | sort -u | wc -l) 个 ref★)"
echo "  差异行数 = $D" > "$LOGD/16b_fp_diff_count.txt"

# ── ④ 链终几何 (cmp_pcb_geom.py 口径) ──
echo "── ④ 链终几何 (cmp_pcb_geom.py) ──"
python3 state/cmp_pcb_geom.py "$FINAL" "$BASE" --fast --vias --zones 2>&1 | tee "$LOGD/17_cmp_pcb_geom_chain_ru_vs_ctl.txt"

# ── ⑤ 段内 P/N 顺序翻转 (ISS-325 口径 · 分母 47) ──
echo "── ⑤ 段内 P/N 翻转 (ISS-325 口径) ──"
bash state/pcbnew_py.sh "$SBX/probe_pn_order.py" "$FINAL" "右上臂链终" > "$LOGD/18_pn_order_ru_chain.txt" 2>&1
bash state/pcbnew_py.sh "$SBX/probe_pn_order.py" "$BASE"  "基线臂链终" > "$LOGD/19_pn_order_ctl_chain.txt" 2>&1
grep -E "同段比较总数|ISS-325 读数|翻转明细|Δx=" "$LOGD/18_pn_order_ru_chain.txt" | head -12
grep -E "同段比较总数|ISS-325 读数" "$LOGD/19_pn_order_ctl_chain.txt" | head -4

# ── ⑥ 名单制闸 (rc) ──
echo "── ⑥ 名单制闸 (★成功判据 = rc 0 + DRC 0★) ──"
{
  echo "── 名单制闸 ⑥-1: 右上臂链终 vs 官方板 (state/compare_arm_official.py) ──"
  python3 state/compare_arm_official.py "$FINAL" "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" 2>&1
  echo "  ★名单制闸 rc=$?"
  if [ -f "$CLR" ]; then
    echo "── 名单制闸 ⑥-2: clrfix 终板 vs 官方板 ──"
    python3 state/compare_arm_official.py "$CLR" "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" 2>&1
    echo "  ★名单制闸 rc=$?"
  fi
} 2>&1 | tail -120 | tee "$LOGD/20_namelist_gate_ru_vs_official.txt"

{
  echo "── 臂间对照闸 ⑥-3: 右上臂链终 vs ★基线臂同链终★ (state/compare_arm_baseline.sh) ──"
  bash "$SBX/compare_arm_baseline_sbx.sh" "$FINAL" --baseline "$BASE" 2>&1
  echo "  ★对照闸 rc=$?"
} 2>&1 | tail -120 | tee "$LOGD/21_compare_arm_baseline_ru_vs_ctl.txt"

echo "=== ISS-328 收数完成 $(date '+%F %T') ==="
