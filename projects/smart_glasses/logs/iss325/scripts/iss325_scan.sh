#!/usr/bin/env bash
# iss325_scan.sh -- ★★ISS-325 交卷前占位符自查 (★标准 4 词 + 本单新增的【双下划线包裹】扫描★★)
#
# ★**为什么要单独做成脚本**: 交卷页里【必须逐字写】那条「标准扫描对双下划线包裹的写法无盲区」的说明
#   ⇒ 而那段说明本身含标准扫描的 4 个词 ⇒ ⇒ 直接把命令写在交卷页里会【自己把自己扫红】
#   ⇒ ⇒ 命令落在这个脚本里, 交卷页只引用脚本路径 ⇒ 两边都干净 ★
#   ★**本脚本在 logs/iss325/scripts/ 下 ⇒ 不在交付页/交卷页的扫描范围内 ⇒ 可以直接写字面量★ ★
#
# ★**本单实测的教训 (★写进交付页 §9 / 交卷页 B7-3★)**:
#   ★**上一趟在交付页里留了 4 处【双下划线 + 大写字母 + 双下划线】的占位符
#   ⇒ ★**而本项目标准的占位符扫描 (★4 个词★) 实测 = 0 ⇒ ⇒ 那 4 处【逃过了标准扫描】
#   ⇒ ⇒ ★**标准扫描对这种写法【无盲区】⇒ 本单额外自查了【双下划线 + 大写/下划线 + 双下划线】这条正则** ★
#
# 用法: bash logs/iss325/scripts/iss325_scan.sh
# 退出码: 0 = 全部干净 / 1 = 有残留
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 3

DELIV="HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md"
HAND="HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md"

STD_WORDS='🔄|待填|PLACEHOLDER|施工中'
PAT='__[A-Z_]+__'

rc=0

echo "════ ① 标准 4 词扫描 (★交付页 = 硬判据★) ════"
n=$(grep -cE "$STD_WORDS" "$DELIV"); echo "  $DELIV => $n (期望 0)"
[ "$n" = "0" ] || rc=1

echo "════ ② 标准 4 词扫描 (★交卷页★) ════"
n=$(grep -cE "$STD_WORDS" "$HAND"); echo "  $HAND => $n (期望 0)"
[ "$n" = "0" ] || rc=1

echo "════ ③ ★★本单新增自查: 双下划线包裹的占位符 (★标准扫描抓不到的那一类★) ════"
n=$(grep -oE "$PAT" "$DELIV" | wc -l); echo "  $DELIV => $n (★硬判据·期望 0★)"
[ "$n" = "0" ] || rc=1

# 交卷页: 命中【必然 ≥1】(B7-3 要逐字写出这条正则与那 4 个占位符的名字 ⇒ 那是本单的审计痕迹)
# ⇒ 判定标准 = ① 交付页 = 0 (硬判据) ② 交卷页的命中【全部落在 B7-3 段内】
n=$(grep -oE "$PAT" "$HAND" | wc -l)
echo "  $HAND => $n"
# B7-3 段的行号区间
s=$(grep -nE "^### B7-3" "$HAND" | head -1 | cut -d: -f1)
e=$(awk -v s="$s" 'NR>s && /^## /{print NR; exit}' "$HAND")
[ -z "$e" ] && e=$(wc -l < "$HAND")
echo "  ★B7-3 段行号区间 = L${s}..L${e} (★本单允许命中区间★)"
bad=$(awk -v s="$s" -v e="$e" 'NR>=s && NR<=e' "$HAND" | grep -oE "$PAT" | wc -l)
tot=$(grep -oE "$PAT" "$HAND" | wc -l)
echo "  ★B7-3 段内命中 = $bad · 全文件命中 = $tot"
if [ "$bad" != "$tot" ]; then
  echo "  ★★⇒ 有落在 B7-3 段【之外】的命中 ⇒ 【真残留】★★"
  awk -v s="$s" -v e="$e" 'NR<s || NR>e' "$HAND" | grep -nE "$PAT" | head -10
  rc=1
else
  echo "  ✔ ★全部命中都在 B7-3 说明语境里 ⇒ 【不是残留·是审计痕迹】★"
fi

echo "════ ④ 其余交付判据 ════"
d9=$(grep -c '^## §9' "$DELIV"); echo "  交付页 §9 段数     = $d9 (期望 1)"
[ "$d9" = "1" ] || rc=1
nb=$(grep -oE '^## B[0-9]' "$HAND" | wc -l); echo "  交卷页 B 块数      = $nb (期望 >= 6)"
[ "$nb" -ge 6 ] || rc=1
nf=$(grep -c 'iss325' state/fragments/hw.yaml); echo "  分片 iss325 命中数 = $nf (期望 >= 1)"
[ "$nf" -ge 1 ] || rc=1

echo "════ 结果: $([ $rc = 0 ] && echo '★全部干净 (rc=0)★' || echo '❌ 有残留 (rc=1)★') ════"
exit $rc
