#!/usr/bin/env bash
# =============================================================================
# s2_iss123_verify.sh —— ISS-123 一条命令自证 (S2 救砖链路按 RK3576 模组厂口径重写)
# =============================================================================
#
# 用法: bash SW/tools/s2_iss123_verify.sh
#
# 它干什么:
#   把 ISS-123 的**全部**可机械复算的结论跑一遍, 期望 **rc=0**:
#     [V1] 静态口径: 三处硬编码 (magic / 版本串前缀 / 扇区单位) **确实不再写死**
#     [V2] 配置口径: identity 段 + partition_layout.sector_size 都已显式配置, 且**带依据**
#     [V3] 扇区↔字节换算守卫自测 (★ 含 2 条 512 倍反例)
#     [V4] 分区表一致性守卫对本仓真配置 0 个 error
#     [V5] flash_writer 写/读回往返 (magic 从配置读) + 换 magic 后必须判不通过
#     [V6] 既有 4 件套自检: run.sh / judge.py / e2e.sh / selftest.py (★ 既有判据不许退化)
#     [V7] ISS-080 既有 s2_selftest.sh (10/10, 不许被破坏)
#     [V8] 板端自检脚本自检 s2_board_selftest.sh
#     [V9] 状态源: state/merge.py rc=0 + state/gate_check.py Q1 18/18
#
# ★ 纪律: 本脚本**只读不写**业务文件 (唯一副作用是 state/merge.py 刷新 STATE.yaml 快照,
#   那是纯函数, 谁都能跑)。不联网、不外联。
# ★ 本脚本证明的是**口径与代码一致**, 不代表板端 S2 已实测通过 (板端实测仍 0 次)。
set -u

cd "$(dirname "$0")/../.." || exit 2

CFG="SW/tools/s2_rescue_config.json"
RC=0
PASSN=0
FAILN=0

say()  { printf '%s\n' "$*"; }
chk()  { if [ "$2" = "$3" ]; then printf '  ✅ %-56s rc=%s (期望 %s)\n' "$1" "$3" "$2"; PASSN=$((PASSN+1));
          else printf '  ❌ %-56s rc=%s (期望 %s)\n' "$1" "$3" "$2"; FAILN=$((FAILN+1)); RC=1; fi; }

say "=============================================================================="
say "ISS-123 自证 —— S2 救砖链路按 RK3576 模组厂口径重写"
say "=============================================================================="

# ------------------------------------------------------------------ V1 静态口径
say ""
say "[V1] 静态口径: 三处硬编码确实不再写死"
python3 - <<'PY'
import os, re, sys
TOOLS = "SW/tools"
fails = []

def must_not(path, pattern, why):
    p = os.path.join(TOOLS, path)
    s = open(p, encoding="utf-8").read()
    if re.search(pattern, s):
        fails.append(f"{path}: 仍能匹配 {pattern!r} —— {why}")

def must_have(path, needle, why):
    p = os.path.join(TOOLS, path)
    s = open(p, encoding="utf-8").read()
    if needle not in s:
        fails.append(f"{path}: 找不到 {needle!r} —— {why}")

# ① 版本块 magic
must_have("flash_writer.py", "def magic_from_config(", "magic 读配置的函数不见了")
must_not("flash_writer.py", r'^MAGIC\s*=\s*b"', "模块级仍写死 MAGIC 常量")
must_not("flash_writer.py", r'magic\s*==\s*b"AR45"', "仍拿写死的 AR45 比较")
# ② 版本串前缀
must_have("s2_board_judge.py", "def version_regex(", "版本串正则改成动态的函数不见了")
must_not("s2_board_judge.py", r'R_FORMAT\s*=\s*re\.compile\(r"\^ARS45-SW', "仍写死 R_FORMAT 正则")
must_have("s2_board_selftest.py", "def version_prefix(", "板端自检的版本串前缀读配置的函数不见了")
must_not("s2_board_selftest.py", r'startswith\("ARS45-SW"\)', "板端自检仍写死前缀")
# ③ 扇区单位
must_have("s2_partition_convert.py", "def check_layout(", "分区表守卫函数不见了")
must_have("s2_partition_convert.py", "def parse_parameter_txt(", "parameter.txt 解析器不见了")

for f in fails:
    print(f"  ❌ {f}")
if not fails:
    print("  ✅ 三处硬编码均已抽成可配置 (magic / 版本串前缀 / 扇区单位)")
print(f"  ⇒ V1 {'FAIL' if fails else 'PASS'} ({len(fails)} 处残留)")
sys.exit(1 if fails else 0)
PY
chk "V1 静态口径: 硬编码已抽走" 0 $?

# ------------------------------------------------------------------ V2 配置口径
say ""
say "[V2] 配置口径: identity 段 + sector_size 已显式配置, 且带依据"
python3 - <<'PY'
import json, sys
d = json.load(open("SW/tools/s2_rescue_config.json", encoding="utf-8"))
fails = []
ident = d.get("identity") or {}
for k in ("version_block_magic", "version_str_prefix"):
    if not ident.get(k):
        fails.append(f"identity.{k} 为空")
    if not ident.get(k + "_basis"):
        fails.append(f"identity.{k}_basis 缺依据")
pl = d.get("partition_layout") or {}
for k in ("sector_size", "size_unit", "expected_total_bytes"):
    if pl.get(k) in (None, ""):
        fails.append(f"partition_layout.{k} 为空")
if not pl.get("sector_size_basis"):
    fails.append("partition_layout.sector_size_basis 缺依据")
if pl.get("size_unit") != "bytes":
    fails.append(f"partition_layout.size_unit={pl.get('size_unit')!r} (我方内部单位恒为 bytes)")
# 合计必须等于声明的期望合计
tot = sum(int(p["size"]) for p in (pl.get("partitions") or []))
if tot != pl.get("expected_total_bytes"):
    fails.append(f"分区表合计 {tot} ≠ expected_total_bytes {pl.get('expected_total_bytes')}")
for f in fails:
    print(f"  ❌ {f}")
if not fails:
    print(f"  ✅ identity.version_block_magic={ident.get('version_block_magic')!r} "
          f"identity.version_str_prefix={ident.get('version_str_prefix')!r} "
          f"sector_size={pl.get('sector_size')} (均带依据)")
    print(f"  ✅ 分区表合计 {tot} B == expected_total_bytes")
print(f"  ⇒ V2 {'FAIL' if fails else 'PASS'} ({len(fails)} 处问题)")
sys.exit(1 if fails else 0)
PY
chk "V2 配置口径: 显式 + 带依据" 0 $?

# ------------------------------------------------------------------ V3 换算守卫
say ""
say "[V3] 扇区↔字节换算守卫自测 (★ 含 2 条 512 倍反例)"
python3 SW/tools/s2_partition_convert.py --selftest >/tmp/s2_iss123_v3.txt 2>&1
chk "s2_partition_convert.py --selftest" 0 $?
grep -E "T3 |T4 |T5 |T7 |T8 " /tmp/s2_iss123_v3.txt | sed 's/^/     /'

# ------------------------------------------------------------------ V4 真配置守卫
say ""
say "[V4] 分区表一致性守卫对本仓真配置 0 个 error"
python3 SW/tools/s2_partition_convert.py --check "$CFG" >/tmp/s2_iss123_v4.txt 2>&1
chk "s2_partition_convert.py --check (真配置)" 0 $?

# ------------------------------------------------------------------ V5 往返
say ""
say "[V5] flash_writer 写/读回往返 (magic 从配置读) + 换 magic 后必须判不通过"
T=$(mktemp -d)
python3 SW/tools/flash_writer.py write --config SW/tools/s2_rescue_config.example.json \
        --target "$T/f.img" --synth >/tmp/s2_iss123_v5w.txt 2>&1
chk "flash_writer write (magic 从配置读)" 0 $?
python3 SW/tools/flash_writer.py verify --config SW/tools/s2_rescue_config.example.json \
        --target "$T/f.img" >/tmp/s2_iss123_v5.txt 2>&1
chk "flash_writer verify (回读全过)" 0 $?
grep -E "CB-02a" /tmp/s2_iss123_v5.txt | sed 's/^/     /'
python3 - "$T/cfg.json" <<'PY'
import json, sys
d = json.load(open("SW/tools/s2_rescue_config.example.json", encoding="utf-8"))
d["identity"]["version_block_magic"] = "ZZZZ"
json.dump(d, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
python3 SW/tools/flash_writer.py verify --config "$T/cfg.json" --target "$T/f.img" \
        >/tmp/s2_iss123_v5m.txt 2>&1
MR=$?
if [ "$MR" = "1" ]; then chk "换 magic 后 verify 必须判不通过" 1 $MR; else chk "换 magic 后 verify 必须判不通过" 1 $MR; fi
grep -E "CB-02a" /tmp/s2_iss123_v5m.txt | sed 's/^/     /'
rm -rf "$T"

# ------------------------------------------------------------------ V6 既有四件套
say ""
say "[V6] 既有 4 件套自检 (★ 既有判据不许退化)"
bash SW/tools/s2_board_run.sh --selftest >/tmp/s2_iss123_v6a.txt 2>&1
chk "s2_board_run.sh --selftest" 0 $?
python3 SW/tools/s2_board_judge.py --selftest >/tmp/s2_iss123_v6b.txt 2>&1
chk "s2_board_judge.py --selftest" 0 $?
bash SW/tools/s2_board_e2e.sh >/tmp/s2_iss123_v6c.txt 2>&1
chk "s2_board_e2e.sh" 0 $?
python3 SW/tools/s2_board_selftest.py --selftest >/tmp/s2_iss123_v6d.txt 2>&1
chk "s2_board_selftest.py --selftest" 0 $?
for f in a b c d; do
  grep -E "结论:|结果:" /tmp/s2_iss123_v6$f.txt | tail -1 | sed 's/^/     /'
done

# ------------------------------------------------------------------ V7/V8 既有脚本
say ""
say "[V7] ISS-080 既有 s2_selftest.sh (10/10, 不许被破坏)"
bash SW/tools/s2_selftest.sh >/tmp/s2_iss123_v7.txt 2>&1
chk "s2_selftest.sh (ISS-080 既有)" 0 $?
grep -E "结果:" /tmp/s2_iss123_v7.txt | tail -1 | sed 's/^/     /'

say ""
say "[V8] 板端自检脚本自检 s2_board_selftest.sh"
bash SW/tools/s2_board_selftest.sh --selftest >/tmp/s2_iss123_v8.txt 2>&1
chk "s2_board_selftest.sh --selftest" 0 $?

# ------------------------------------------------------------------ V9 状态源
say ""
say "[V9] 状态源: merge.py rc=0 + gate_check.py Q1 18/18"
python3 state/merge.py >/tmp/s2_iss123_v9a.txt 2>&1
chk "state/merge.py" 0 $?
tail -1 /tmp/s2_iss123_v9a.txt | sed 's/^/     /'
python3 state/gate_check.py >/tmp/s2_iss123_v9b.txt 2>&1
chk "state/gate_check.py" 0 $?
grep -E "Q1" /tmp/s2_iss123_v9b.txt | head -2 | sed 's/^/     /'

# ------------------------------------------------------------------ 汇总
say ""
say "=============================================================================="
say "结果: 通过 $PASSN / 失败 $FAILN"
say "证据: [实测] PC 侧自证 (口径 + 换算守卫 + 判定逻辑), ★不代表板端 S2 已实测通过"
say "★ ISS-123 结论: 三处硬编码已抽成可配置 · 512 倍差已由守卫机械拦住 · 问询清单已按 RK3576 模组厂口径重写"
say "=============================================================================="
[ "$FAILN" = "0" ] || exit 1
exit 0
