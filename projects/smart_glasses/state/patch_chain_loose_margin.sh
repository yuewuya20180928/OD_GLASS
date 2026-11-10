#!/usr/bin/env bash
# ★★★【★补丁: 让 `replay_patch_chain.sh` 的 loose 步 margin 可参数化 (★默认 0.0625 ⇒ 逐位不变★)★★★ ★
#
# ★★**为什么需要 (★2026-11-11 04:0x 实测★)**: ★★
#   ★**实测**: loose 步 margin 从 0.0625 → 0.03125 ⇒ ★**unc 29 → 27 (多接通 2 个网)** ★★
#     ⇒ ★**代价 = 4 条 clearance, 全是 0.1937mm 的【边际违规】⇒ ⇒ 由 `state/fix_clearance_width.py` 迭代清理 ⇒ ⇒ 【DRC 0】** ★★
#   ★★**⇒ ⇒ 【两个机制互补】⇒ ⇒ ⇒ 不开新臂也能把 unc 往下压 ⇒ ⇒ ⇒ 但【必须可复现】⇒ ⇒ ⇒ 链脚本要能复现这条链** ★★★
#
# ★**用法**: ★**`PCB_CHAIN_LOOSE_MARGIN=0.03125 bash state/replay_patch_chain.sh <板> <标签>`** ★
#   ★**默认 0.0625 (★与官方链一致 ⇒ 逐位不变★)** ★
# ★**配套**: 跑完链后跑 `bash state/clrfix_iter.sh <终板> <终板>.drc.json --tag <标签>` ⇒ 清掉边际违规 ★★
set -u
F=state/replay_patch_chain.sh
if grep -q "PCB_CHAIN_LOOSE_MARGIN" "$F"; then
  echo "✓ 已打过补丁 (PCB_CHAIN_LOOSE_MARGIN) ⇒ 跳过"
  exit 0
fi
if ! grep -q 'step_nostub "\$WORK/s2_combo.kicad_pcb" "\$WORK/final_chain.kicad_pcb" 0.125 0.0625' "$F"; then
  echo "❌ 没找到 loose 步那一行 ⇒ ★**链脚本结构变了? ★** ⇒ 收工 (别盲改)"
  exit 3
fi
cp -f "$F" "${F}.bak_$(date +%Y%m%d_%H%M%S)"
python3 - "$F" <<'PY'
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
old = 'step_nostub "$WORK/s2_combo.kicad_pcb" "$WORK/final_chain.kicad_pcb" 0.125 0.0625'
new = ('# ★★2026-11-11 04:3x 【loose 步 margin 可参数化·默认 0.0625 ⇒ 逐位不变】★★\n'
       '#   ★依据: margin 0.03125 ⇒ unc 29→27 ⇒ 代价是 0.1937mm 边际违规 ⇒ 由 clrfix_iter 清理 ⇒ DRC 0\n'
       '_LOOSE_MARGIN="${PCB_CHAIN_LOOSE_MARGIN:-0.0625}"\n'
       'step_nostub "$WORK/s2_combo.kicad_pcb" "$WORK/final_chain.kicad_pcb" 0.125 "$_LOOSE_MARGIN"')
if old not in s:
    print("❌ 没找到目标行"); sys.exit(3)
open(p, 'w', encoding='utf-8').write(s.replace(old, new, 1))
print("✓ 已打补丁")
PY
bash -n "$F" && echo "✓ bash -n 通过" || { echo "❌ 语法错 ⇒ 回滚"; cp -f "${F}.bak_"* "$F"; exit 4; }
grep -n "_LOOSE_MARGIN" "$F" | head -4
