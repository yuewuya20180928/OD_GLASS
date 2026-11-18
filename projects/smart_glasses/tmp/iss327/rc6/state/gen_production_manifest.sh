#!/usr/bin/env bash
# gen_production_manifest.sh —— ★S10 投产包 md5 清单生成器 (ISS-281 格式契约) ★
# ==============================================================================
# ★★为什么单独一个文件 (★不是偷懒, 是为了让「产物」和「生成器」都只有一处★★):
#   ★格式契约的权威 = HW/PCB/BOARD_ONEPASS_S10_MANIFEST_SPEC.md (ISS-281) ★
#   ★机器闸 = HW/check_onepass_s10_manifest.py (M1 格式 / M2 板 md5 / M3 逐文件 md5 / M4 文件集合) ★
#   ★调用方 = state/gen_production_pack.sh (★rm -rf 重建【之后】写 ⇒ 清单必是这一包自己的★) ★
#
# 用法: bash state/gen_production_manifest.sh <投产包目录> <板文件>
#   例: bash state/gen_production_manifest.sh HW/PCB/production HW/PCB/demo_mainboard.kicad_pcb
#
# ★★三条不变量 (★破了就是「僵尸清单」/「旧货冒充新货」/「漏件偷渡」★★):
#   ① 清单必须写在**投产包内** (HW/PCB/production/MANIFEST.md5)
#      ⇒ 放外面 = 描述旧包的僵尸清单 (比没有清单更危险: 它看着像有)
#   ② 清单自己**不进数据行** (数据行 = 包内除清单自身外的全部普通文件)
#      ⇒ 但 FILE_COUNT 把它算进去 (= 数据行数 + 1) ⇒ 与闸的 M4 口径一致
#   ③ 数据行里的 md5 必须与**盘上当时的字节**逐字相同 ⇒ 闸的 M3 才能判「产物没被动过」
#
# ★★零副作用: 本脚本只写 <投产包>/MANIFEST.md5 一个文件 (先写 .tmp 再 mv ⇒ 原子替换) ★★
set -u

OUT="${1:-}"
PCB="${2:-}"

if [ -z "$OUT" ] || [ -z "$PCB" ]; then
    echo "★用法: bash state/gen_production_manifest.sh <投产包目录> <板文件>" >&2
    exit 2
fi
if [ ! -d "$OUT" ]; then
    echo "★投产包目录不存在: $OUT" >&2
    exit 2
fi
if [ ! -f "$PCB" ]; then
    echo "★板文件不存在: $PCB" >&2
    exit 2
fi

MANIFEST="$OUT/MANIFEST.md5"
TMP="$OUT/.MANIFEST.md5.tmp"

# ★头注释 (★闸把 '#' 开头的行整行跳过 ⇒ 不参与判定★)
{
    echo "# ARS45 · S10 投产包 md5 清单"
    echo "# ★格式契约: HW/PCB/BOARD_ONEPASS_S10_MANIFEST_SPEC.md (ISS-281) ★"
    echo "# ★生成器: state/gen_production_pack.sh → state/gen_production_manifest.sh ★"
    echo "# ★板源: ${PCB} ★"
    echo "# ★数据行: <相对路径> | <md5 32hex> | <字节数> ★"
} > "$TMP"

n=0
# ★排序用 LC_ALL=C (★与闸的 Python sorted() 同为字节序 ⇒ 两侧顺序逐字一致★)
while IFS= read -r f; do
    rel="${f#"$OUT"/}"
    [ "$rel" = ".MANIFEST.md5.tmp" ] && continue
    [ "$rel" = "MANIFEST.md5" ] && continue
    md5="$(md5sum "$f" | cut -d' ' -f1)"
    size="$(stat -c %s "$f")"
    printf '%s | %s | %s\n' "$rel" "$md5" "$size" >> "$TMP"
    n=$((n + 1))
done < <(find "$OUT" -type f ! -name 'MANIFEST.md5' ! -name '.MANIFEST.md5.tmp' | LC_ALL=C sort)

printf 'BOARD_MD5 | %s | -\n'    "$(md5sum "$PCB" | cut -d' ' -f1)" >> "$TMP"
printf 'GENERATED_AT | %s | -\n' "$(date -Iseconds)" >> "$TMP"
printf 'FILE_COUNT | %s | -\n'   "$((n + 1))" >> "$TMP"      # ★+1 = 清单自身 (与闸的 M4 同口径) ★

mv -f "$TMP" "$MANIFEST"
echo "  清单: $MANIFEST (数据行 $n 行 + 清单自身 = $((n + 1)) 个文件)"
exit 0
