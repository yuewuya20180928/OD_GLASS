#!/usr/bin/env bash
# =============================================================================
# s2_board_run.sh —— S2 救砖链路 · 板端一条命令跑测 (ISS-120)
# =============================================================================
#
# 用法:
#   bash SW/tools/s2_board_run.sh --config <cfg> --evidence-dir <dir> [选项]
#   bash SW/tools/s2_board_run.sh --selftest          # 无板自检 (期望 rc=0)
#   bash SW/tools/s2_board_run.sh --preflight --config <cfg>   # 只查参数齐不齐
#
# 这条命令把 ISS-080 的"方案"变成"照着敲一行就能跑":
#   ① 读 S2 配置 (P1..P4 齐不齐 → 不齐就明说差哪几个, 不假装能跑)
#   ② 跑 §4.5 的 4 步: 正常态基线 → 进 BOOT → 刷写 → 回读校验 → 板端自检 → 重启 3 次
#   ③ 每一步的证据自动落盘 (文件名与 EVT_TEMPLATE §11.7 对齐)
#   ④ ★ 任何一步失败 → 自动抓"失败现场": 串口日志 / 下载工具版本 / 电流表读数
#   ⑤ 跑完调 s2_board_judge.py 出 CB-01~CB-09 机械判定 + BR-01 总判定
#
# ★ 退出码:
#   0 = BR-01 判 ✅ (CB 9/9 全过)  —— 但"判过"仍由项目总工签 (修复人不能自验)
#   1 = BR-01 判 ❌ (至少 1 条 CB 不通过)
#   2 = BR-01 判 ⚠️ 未验 (有项没实测数据) —— ★ 此状态下该板不得进产线
#   3 = 参数不全 / 环境错误 (P1..P4 未齐 / 工具缺失) —— 还没到能跑的时候
#   4 = 自检失败 (脚本自身逻辑有问题)
#
# ★ 纪律 (沿用 ISS-080 口径):
#   - 参数没填齐 → rc=3 并列出缺哪几个, **不许降级成"能跑"**
#   - 通用示例签名 (source=generic-example) 不算真值 → 判定器会判未验
#   - 分区表是 [推算] 占位 (P4 未填) → CB-06 判未验, 不用占位表冒充实测
#   - 电流表读数没有仪器就读不到 → 记 [0数据] + 提示人工填, **不许编一个数**
set -u

cd "$(dirname "$0")/../.." || exit 2

CFG="SW/tools/s2_rescue_config.json"
EVDIR=""
DRYRUN=0
SELFTEST=0
PREFLIGHT=0
ONLY_STEP=""
SKIP_FLASH=0
CURRENT_MA=""          # ★ 电流表读数 (mA) —— 没有仪器就留空, 判定里记 [0数据]

# ------------------------------------------------------------------ 参数解析
while [ $# -gt 0 ]; do
  case "$1" in
    --config)       CFG="$2"; shift 2 ;;
    --evidence-dir) EVDIR="$2"; shift 2 ;;
    --only)         ONLY_STEP="$2"; shift 2 ;;
    --dry-run)      DRYRUN=1; shift ;;
    --skip-flash)   SKIP_FLASH=1; shift ;;
    --current-ma)   CURRENT_MA="$2"; shift 2 ;;
    --selftest)     SELFTEST=1; shift ;;
    --preflight)    PREFLIGHT=1; shift ;;
    -h|--help)      sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "❌ 未知参数: $1" >&2; exit 3 ;;
  esac
done

# ------------------------------------------------------------------ 小工具
say()  { printf '%s\n' "$*"; }
step() { printf '\n=== %s ===\n' "$*"; }
ok()   { printf '  ✅ %s\n' "$*"; }
warn() { printf '  ⚠️  %s\n' "$*"; }
bad()  { printf '  ❌ %s\n' "$*"; }

cfg_get() {  # cfg_get <dotted.path>  → 打印值 (不存在打印空串)
  python3 - "$CFG" "$1" <<'PY' 2>/dev/null
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    sys.exit(0)
for k in sys.argv[2].split("."):
    if isinstance(d, list):
        try:
            d = d[int(k)]
        except Exception:
            sys.exit(0)
    elif isinstance(d, dict) and k in d:
        d = d[k]
    else:
        sys.exit(0)
print("" if d is None else (d if isinstance(d, str) else json.dumps(d, ensure_ascii=False)))
PY
}

cfg_has() {  # cfg_has <dotted.path> → 0=存在且非空
  [ -n "$(cfg_get "$1")" ]
}

# ------------------------------------------------------------------ 无板自检
if [ "$SELFTEST" = "1" ]; then
  step "S2 板端跑测脚本 · 自检 (无板)"
  RC=0
  check() {  # check <描述> <期望rc> <实际rc>
    if [ "$2" = "$3" ]; then ok "$1 (rc=$3, 期望 $2)"; else bad "$1 (rc=$3, 期望 $2)"; RC=1; fi
  }

  say ""
  say "[S1] 配置解析器可用"
  OUT=$(cfg_get "params.P1_BOOT_ENTER_SPEC")
  if [ -z "$OUT" ]; then ok "cfg_get 返回空串 (P1 未填, 符合预期)"; else ok "cfg_get 可解析 ($OUT)"; fi

  say ""
  say "[S2] 判定器自测 (期望 rc=0)"
  python3 SW/tools/s2_board_judge.py --selftest >/tmp/s2_judge_selftest.txt 2>&1
  check "s2_board_judge.py --selftest" 0 $?

  say ""
  say "[S3] 判定器在空证据目录上判未验 (期望 rc=2)"
  TMPD=$(mktemp -d)
  python3 SW/tools/s2_board_judge.py --evidence-dir "$TMPD" --config "$CFG" >/tmp/s2_judge_empty.txt 2>&1
  check "空证据目录 → rc=2 (⚠️未验, 不是 ✅)" 2 $?
  rm -rf "$TMPD"

  say ""
  say "[S4] 配置齐备性检查 (P1..P4 全未填 → 期望报缺 4 个)"
  bash SW/tools/s2_board_run.sh --preflight --config SW/tools/s2_rescue_config.json >/tmp/s2_pf.txt 2>&1
  PFRC=$?
  if [ "$PFRC" = "3" ]; then ok "未填参数 → rc=3 (明说差哪几个, 不降级)"; else bad "未填参数 → rc=$PFRC (期望 3)"; RC=1; fi
  grep -q "P1_BOOT_ENTER_SPEC" /tmp/s2_pf.txt && ok "preflight 明确列出了缺失的参数" || { bad "preflight 没列出缺失参数"; RC=1; }

  say ""
  say "[S5] 取证子命令可用 (失败现场: 串口/工具版本/电流表)"
  TMPD=$(mktemp -d)
  bash "$0" --config "$CFG" --evidence-dir "$TMPD" --only forensics >/tmp/s2_forensics.txt 2>&1
  check "forensics 子命令" 0 $?
  [ -f "$TMPD/s2_forensics.json" ] && ok "落了 s2_forensics.json" || { bad "没落 s2_forensics.json"; RC=1; }
  rm -rf "$TMPD"

  say ""
  say "[S6] 端到端链路自检 (合成证据, 期望 rc=0)"
  bash SW/tools/s2_board_e2e.sh >/tmp/s2_e2e.txt 2>&1
  check "s2_board_e2e.sh" 0 $?

  say ""
  say "=============================================================================="
  [ "$RC" = "0" ] && say "自检结论: PASS (rc=0)" || say "自检结论: FAIL"
  say "证据: [实测] PC 侧自检 (脚本逻辑), 不代表板端 S2 已实测通过"
  say "=============================================================================="
  exit $RC
fi

# ------------------------------------------------------------------ 前置检查
step "前置检查 (S2 配置 + 环境)"

if [ ! -f "$CFG" ]; then
  bad "配置不存在: $CFG"
  exit 3
fi
say "配置: $CFG"

MISSING=""
for P in P1_BOOT_ENTER_SPEC P2_DL_TOOL P3_USB_PHY P4_BOOT_STORE; do
  VAL=$(cfg_get "params.$P.value")
  ST=$(cfg_get "params.$P.status")
  if [ -z "$VAL" ] || [ "$ST" != "DONE" ]; then
    MISSING="$MISSING $P"
  fi
done

# ★ 取证路径: 参数没填齐也要能跑 —— 出故障的时候, 现场证据恰恰是最缺的
FORENSICS_ONLY=0
if [ "$ONLY_STEP" = "forensics" ]; then
  FORENSICS_ONLY=1
  if [ -n "$MISSING" ]; then
    warn "注意: S2 配置里这 4 个 0 数据项还没到位 ($MISSING ) —— 取证照跑, 但 BR-01 判不了"
  fi
fi

if [ -n "$MISSING" ] && [ "$FORENSICS_ONLY" != "1" ]; then
  bad "S2 配置里这 4 个 0 数据项还没到位:$MISSING"
  say ""
  say "  ┌─ 这 4 项在原厂书面回复前一律留空 (ISS-080 口径)。没它们, 救砖链路跑不了。"
  say "  ├─ P1_BOOT_ENTER_SPEC → 问什么/填哪个字段: SW/S2_VENDOR_QUESTION_LIST.md §1"
  say "  ├─ P2_DL_TOOL         → SW/S2_VENDOR_QUESTION_LIST.md §2"
  say "  ├─ P3_USB_PHY         → SW/S2_VENDOR_QUESTION_LIST.md §3"
  say "  └─ P4_BOOT_STORE      → SW/S2_VENDOR_QUESTION_LIST.md §4"
  say ""
  say "  ★ 外发一律经项目总工 (sw-lead 不直接联系原厂)。填完用下面这条复核:"
  say "      python3 SW/tools/s2_board_run.sh --preflight --config $CFG"
  exit 3
fi
if [ "$FORENSICS_ONLY" != "1" ]; then
  ok "P1..P4 全部已填 (status=DONE)"
fi

if [ "$PREFLIGHT" = "1" ]; then
  say ""
  say "★ 还差哪些可执行件 (不阻塞参数齐备性, 但决定能不能真跑):"
  for F in board_test.detect.list_cmd board_test.flash.cmd board_test.verify.readback_cmd \
           board_test.selftest.ddr board_test.selftest.sensor board_test.selftest.i2c \
           board_test.selftest.npu board_test.selftest.od board_test.selftest.version \
           board_test.serial.device board_test.checks.calib_ledger; do
    if cfg_has "$F"; then ok "$F"; else warn "$F 未填 → 对应 CB 判未验"; fi
  done
  say ""
  say "preflight 结论: 参数齐备 ✅ (可执行件缺项见上, 缺的项对应判据会判 ⚠️未验)"
  exit 0
fi

if [ -z "$EVDIR" ]; then
  bad "缺 --evidence-dir (证据落盘目录)"
  exit 3
fi
mkdir -p "$EVDIR" || exit 3
say "证据目录: $EVDIR"

BOARD_SN=$(cfg_get "board_test.board_sn")
OPERATOR=$(cfg_get "board_test.operator")
if [ -n "$BOARD_SN" ]; then ok "板卡 SN: $BOARD_SN"; else warn "board_sn 未填 → CB-02/03/07 的板级比对会判未验"; fi
if [ -n "$OPERATOR" ]; then ok "执行人: $OPERATOR"; else warn "operator 未填 → 证据追溯会缺一栏"; fi
# ------------------------------------------------------------------ 取证
collect_forensics() {
  step "★ 失败现场取证 (串口日志 / 下载工具版本 / 电流表读数)"
  FD="$EVDIR/s2_forensics.json"
  SER="$EVDIR/s2_forensics_serial.log"

  # --- 串口日志
  SERDEV=$(cfg_get "board_test.serial.device")
  SERBAUD=$(cfg_get "board_test.serial.baud")
  SERBAUD=${SERBAUD:-115200}
  SECS=$(cfg_get "board_test.serial.capture_seconds")
  SECS=${SECS:-20}
  if [ -n "$SERDEV" ] && [ -c "$SERDEV" ]; then
    say "抓串口 $SERDEV @ ${SERBAUD} (${SECS}s) ..."
    if command -v timeout >/dev/null 2>&1; then
      timeout "${SECS}" cat "$SERDEV" > "$SER" 2>/dev/null || true
    else
      ( cat "$SERDEV" > "$SER" & CPID=$!; sleep "${SECS}"; kill $CPID 2>/dev/null ) || true
    fi
    SZ=$(wc -c < "$SER" 2>/dev/null || echo 0)
    if [ "$SZ" -gt 0 ]; then ok "串口日志已落盘 $SER ($SZ B)"; else warn "串口没抓到数据 ($SER 为空) —— 检查波特率/线序"; fi
  else
    warn "串口设备不可用 (device=${SERDEV:-未配} 或不存在) → 串口日志记 [0数据]"
    : > "$SER"
  fi

  # --- 下载工具版本
  say "采下载工具版本 ..."
  TOOLS_JSON=$(python3 - "$CFG" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    d = {}
print(json.dumps(((d.get("board_test") or {}).get("tools") or {}).get("entries") or [], ensure_ascii=False))
PY
)
  TOOL_OUT=$(TOOLS_JSON="$TOOLS_JSON" python3 - <<'PY'
import json, os, shutil, subprocess
out = []
try:
    entries = json.loads(os.environ.get("TOOLS_JSON") or "[]")
except Exception:
    entries = []
for e in entries:
    name = e.get("name")
    cmd = e.get("version_cmd")
    rec = {"tool": name, "version": None, "status": "[0数据] 工具缺失"}
    if cmd:
        exe = cmd[0]
        if shutil.which(exe) is None:
            rec["status"] = f"[0数据] 命令 {exe} 不在 PATH"
        else:
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                txt = (p.stdout or "") + (p.stderr or "")
                rec["version"] = txt.strip().splitlines()[0] if txt.strip() else ""
                rec["status"] = "ok" if rec["version"] else "[0数据] 无版本输出"
            except Exception as ex:
                rec["status"] = f"[0数据] 取版本失败: {ex}"
    out.append(rec)
print(json.dumps(out, ensure_ascii=False))
PY
)
  printf '%s\n' "$TOOL_OUT" | python3 -c '
import json,sys
for r in json.load(sys.stdin):
    print(f"  {r[\"tool\"]}: {r[\"version\"] or r[\"status\"]}")
' 2>/dev/null || true

  # --- 电流表读数 (★ 没有仪器就是 [0数据], 不许编)
  if [ -n "$CURRENT_MA" ]; then
    CUR_JSON=$(python3 -c "import json,sys; print(json.dumps({'value_ma': sys.argv[1], 'source': 'operator-provided'}, ensure_ascii=False))" "$CURRENT_MA")
    ok "电流表读数: ${CURRENT_MA} mA (由 --current-ma 提供)"
  else
    CUR_JSON=$(python3 -c "import json; print(json.dumps({'value_ma': None, 'status': '[0数据] 未提供 (用 --current-ma <值> 补)'}, ensure_ascii=False))")
    warn "电流表读数 [0数据] —— 用 --current-ma <mA> 补上, 或人工填 s2_forensics.json"
  fi

  python3 - "$EVDIR/s2_forensics.json" "$TOOL_OUT" "$CUR_JSON" "$SER" <<'PY'
import json, os, sys
out, tools, cur, ser = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
try:
    tools = json.loads(tools)
except Exception:
    tools = []
try:
    cur = json.loads(cur)
except Exception:
    cur = {}
rec = {
    "tool": "s2_board_run.sh collect_forensics",
    "download_tool_versions": tools,
    "current_meter": cur,
    "serial_log_file": os.path.basename(ser) if ser else None,
    "serial_log_bytes": (os.path.getsize(ser) if ser and os.path.exists(ser) else 0),
    "note": ("★ 电流表读数没有仪器就读不到 —— 记 [0数据] 由人工补, 不许编数。"
             "★ 工具版本缺失也记 [0数据], 不许填猜测版本。"),
}
with open(out, "w", encoding="utf-8") as f:
    json.dump(rec, f, ensure_ascii=False, indent=2)
print(f"  → 取证已落盘 {out}")
PY
}

if [ "$ONLY_STEP" = "forensics" ]; then
  collect_forensics
  exit 0
fi

# ------------------------------------------------------------------ 步骤 0
run_step0() {
  step "步骤 0: 正常态基线 (BR-02) —— 进 BOOT 之前必须先采基线"
  OUT="$EVDIR/s2_step0_normal.json"
  python3 SW/tools/boot_rescue_probe.py --config "$CFG" --out "$OUT" >/dev/null 2>&1
  RC=$?
  VID=$(python3 - "$OUT" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    print(""); raise SystemExit
best = ""
for dev in d.get("devices") or []:
    v = f"{dev.get('vid','')}:{dev.get('pid','')}"
    if v and v != "::":
        best = v
        break
print(best)
PY
)
  if [ -n "$VID" ]; then ok "正常态 VID:PID = $VID (基线)"; else warn "没枚举到 USB 设备 → 基线为空, CB-01 无从比对"; fi
  python3 - "$OUT" "$VID" <<'PY'
import json, sys
p, vid = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(p, encoding="utf-8"))
except Exception:
    d = {}
d["vidpid"] = vid or None
d["_note"] = "正常态基线 (BR-02)。刷完后重跑探针与本文件的 vidpid 比对 → CB-01"
with open(p, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
PY
}

# ------------------------------------------------------------------ 步骤 1
run_step1() {
  step "步骤 1: 进 BOOT 识别 (BR-03/04/05) —— ★ 操作员先按 SOP 把板子进 BOOT"
  say "  此刻请按 SW/S2_BOARD_TEST_CHECKLIST.md §3 的进 BOOT SOP 操作 (跳线/按键组合), 然后回车继续。"
  if [ "$DRYRUN" = "1" ]; then warn "--dry-run: 跳过实际操作"; return 0; fi
  read -r -p "  已进 BOOT? (y/N) " A || A="N"
  case "$A" in y|Y|yes|YES) ;; *) warn "未确认进 BOOT → BR-03/04/05 判未验"; return 1 ;; esac

  OUT="$EVDIR/s2_step1_boot.json"
  LISTCMD=$(cfg_get "board_test.detect.list_cmd")
  if [ -n "$LISTCMD" ]; then
    say "  用原厂工具列设备: $LISTCMD"
    python3 - "$CFG" "$OUT" "$LISTCMD" <<'PY'
import json, subprocess, sys
cfgp, outp, cmdstr = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    cfg = json.load(open(cfgp, encoding="utf-8"))
except Exception:
    cfg = {}
cmd = json.loads(cmdstr) if cmdstr.strip().startswith("[") else cmdstr.split()
try:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    text = (p.stdout or "") + (p.stderr or "")
    rc = p.returncode
except Exception as e:
    text = f"[调用失败] {e}"
    rc = 127
markers = ((cfg.get("board_test") or {}).get("detect") or {}).get("boot_markers") or []
hit = [m for m in markers if m in text]
rec = {"tool": "vendor list_cmd", "cmd": cmd, "rc": rc, "raw": text,
       "boot_markers_hit": hit,
       "verdict": "BOOT_IDENTIFIED" if hit else "NOT_IDENTIFIED"}
with open(outp, "w", encoding="utf-8") as f:
    json.dump(rec, f, ensure_ascii=False, indent=2)
print(f"  → 工具输出 {len(text)} 字节, 命中 BOOT 标志 {hit}")
PY
  else
    say "  用 boot_rescue_probe.py 探测 (依赖 usb_signatures.entries —— 未填则判不出)"
    python3 SW/tools/boot_rescue_probe.py --config "$CFG" --out "$OUT" >/dev/null 2>&1
    RC=$?
    V=$(python3 -c "
import json,sys
try: print(json.load(open(sys.argv[1],encoding='utf-8')).get('verdict',''))
except Exception: print('')" "$OUT")
    [ "$RC" = "0" ] && ok "BOOT 识别: $V" || warn "BOOT 识别: ${V:-未知} (rc=$RC) → BR-03/04/05 判未验"
  fi
}

# ------------------------------------------------------------------ 步骤 2
run_step2() {
  step "步骤 2: 全量刷写 (BR-06) —— ★ 由 P2 决定的原厂下载工具执行"
  if [ "$SKIP_FLASH" = "1" ]; then warn "--skip-flash: 跳过刷写 → BR-06 判未验"; return 1; fi
  if [ "$DRYRUN" = "1" ]; then warn "--dry-run: 跳过刷写"; return 0; fi
  FLASHCMD=$(cfg_get "board_test.flash.cmd")
  if [ -z "$FLASHCMD" ]; then
    bad "board_test.flash.cmd 未配 (P2 未落地) → BR-06 判未验"
    return 1
  fi
  LOG="$EVDIR/s2_step2_flash.log"
  say "  执行刷写: $FLASHCMD"
  python3 - "$FLASHCMD" "$LOG" "$EVDIR/s2_step2_flash.json" <<'PY'
import json, subprocess, sys
cmd = json.loads(sys.argv[1])
logp, outp = sys.argv[2], sys.argv[3]
try:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    text, rc = (p.stdout or "") + (p.stderr or ""), p.returncode
except Exception as e:
    text, rc = f"[调用失败] {e}", 127
open(logp, "w", encoding="utf-8").write(text)
ok = (rc == 0) and ("fail" not in text.lower() or "failed partitions: 0" in text.lower())
rec = {"cmd": cmd, "rc": rc, "log_file": logp.split("/")[-1],
       "log_bytes": len(text), "ok": ok,
       "note": "ok 由返回码 + 日志关键字判; 刷写日志本身是最终证据, 人工复核分区级结果"}
json.dump(rec, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"  → 刷写 rc={rc}, 日志 {len(text)} 字节 → {logp}")
PY
  local R=$?
  [ "$R" = "0" ] && ok "刷写步骤结束" || bad "刷写步骤异常"
  return $R
}

# ------------------------------------------------------------------ 步骤 3
run_step3() {
  step "步骤 3: 回读校验 (BR-07, CB-02/06/07) —— 读回整片 flash 后用 flash_writer verify 判"
  OUT="$EVDIR/s2_step3_verify.json"
  if [ "$DRYRUN" = "1" ]; then warn "--dry-run: 跳过回读"; return 0; fi
  RB=$(cfg_get "board_test.verify.readback_cmd")
  TGT=$(cfg_get "board_test.verify.readback_target")
  if [ -z "$RB" ]; then
    bad "board_test.verify.readback_cmd 未配 → CB-02/06 判未验"
    return 1
  fi
  TGT=${TGT:-$EVDIR/s2_readback.img}
  say "  回读: $RB → $TGT"
  python3 - "$RB" "$TGT" <<'PY'
import json, subprocess, sys
cmd = json.loads(sys.argv[1]) if sys.argv[1].strip().startswith("[") else sys.argv[1].split()
try:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    print(f"  → readback rc={p.returncode}")
except Exception as e:
    print(f"  → readback 失败: {e}")
PY
  [ -f "$TGT" ] || { bad "回读没产出文件 $TGT → CB-02/06 判未验"; return 1; }
  python3 SW/tools/flash_writer.py verify --config "$CFG" --target "$TGT" --json > "$OUT" 2>/dev/null
  RC=$?
  if [ "$RC" = "0" ]; then ok "回读校验全过 (PC 侧判定逻辑)"; else warn "回读校验未全过 (rc=$RC) → 判定器会看 CB-02/06 细节"; fi
  return 0
}

# ------------------------------------------------------------------ 步骤 4
run_step4() {
  step "步骤 4: 板端自检 6 项 + 版本串 (BR-08/09/12, CB-03/04/07/09)"
  LOG="$EVDIR/s2_step4_selftest.log"
  OUT="$EVDIR/s2_step4_selftest.json"
  if [ "$DRYRUN" = "1" ]; then warn "--dry-run: 跳过板端自检"; return 0; fi
  SEL=$(cfg_get "board_test.selftest")
  say "  板端自检配置: $SEL"
  say "  ★ 这一步要在板子上跑 (adb shell) —— 具体命令由 SW/tools/s2_board_selftest.sh 封装"
  if [ ! -f SW/tools/s2_board_selftest.sh ]; then
    bad "缺 SW/tools/s2_board_selftest.sh (板端自检脚本) → CB-03/04/07/09 判未验"
    return 1
  fi
  bash SW/tools/s2_board_selftest.sh --config "$CFG" --out "$OUT" --log "$LOG"
  RC=$?
  [ "$RC" = "0" ] && ok "板端自检完成" || warn "板端自检未全过 (rc=$RC)"
  return 0
}

# ------------------------------------------------------------------ 步骤 5
run_step5() {
  step "步骤 5: 重启 3 次 (BR-10, CB-05)"
  OUT="$EVDIR/s2_step6_reboot.json"
  if [ "$DRYRUN" = "1" ]; then warn "--dry-run: 跳过重启"; return 0; fi
  RCBOOT=$(cfg_get "board_test.reboot.cmd")
  WAITCMD=$(cfg_get "board_test.reboot.wait_cmd")
  TMO=$(cfg_get "board_test.reboot.timeout_s")
  TMO=${TMO:-120}
  python3 - "$RCBOOT" "$WAITCMD" "$TMO" "$OUT" <<'PY'
import json, subprocess, sys, time
rcboot = json.loads(sys.argv[1]) if sys.argv[1].strip().startswith("[") else sys.argv[1].split()
waitcmd = json.loads(sys.argv[2]) if sys.argv[2].strip().startswith("[") else (sys.argv[2].split() or [])
tmo = int(sys.argv[3] or 120)
outp = sys.argv[4]
attempts = []
for n in (1, 2, 3):
    try:
        subprocess.run(rcboot, capture_output=True, text=True, timeout=60)
    except Exception as e:
        attempts.append({"n": n, "ok": False, "panic": False, "error": str(e)})
        continue
    t0 = time.time()
    ok = False
    panic = False
    while time.time() - t0 < tmo:
        if waitcmd:
            try:
                p = subprocess.run(waitcmd, capture_output=True, text=True, timeout=30)
                if p.returncode == 0:
                    ok = True
                    if "panic" in ((p.stdout or "") + (p.stderr or "")).lower():
                        panic = True
                    break
            except Exception:
                pass
        else:
            ok = True
            break
        time.sleep(2)
    attempts.append({"n": n, "ok": ok, "panic": panic, "wait_s": round(time.time() - t0, 1)})
    print(f"  重启 {n}/3: {'进系统 ✅' if ok else '超时 ❌'}")
rec = {"attempts": attempts, "passed": sum(1 for a in attempts if a["ok"]),
       "note": "★ 未配 wait_cmd 时只判'命令已发出', 进系统与否靠串口首行人工确认 (见 checklist)"}
json.dump(rec, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
  return 0
}

# ------------------------------------------------------------------ 步骤 6
run_step6() {
  step "步骤 6: 刷完后重新枚举 (BR-02 的对照, CB-01)"
  OUT="$EVDIR/s2_step5_reenum.json"
  if [ "$DRYRUN" = "1" ]; then warn "--dry-run: 跳过重新枚举"; return 0; fi
  python3 SW/tools/boot_rescue_probe.py --config "$CFG" --out "$OUT" >/dev/null 2>&1
  python3 - "$OUT" "$CFG" <<'PY'
import json, subprocess, sys
outp, cfgp = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(outp, encoding="utf-8"))
except Exception:
    d = {}
try:
    cfg = json.load(open(cfgp, encoding="utf-8"))
except Exception:
    cfg = {}
entries = ((cfg.get("usb_signatures") or {}).get("entries") or [])
matched = []
for dev in d.get("devices") or []:
    for e in entries:
        if str(e.get("vid","")).lower() == str(dev.get("vid","")).lower() and \
           str(e.get("pid","")).lower() == str(dev.get("pid","")).lower():
            m = dict(e); m["source"] = e.get("source", "")
            matched.append(m)
vidpid = None
for dev in d.get("devices") or []:
    v = f"{dev.get('vid','')}:{dev.get('pid','')}"
    if v and v != "::":
        vidpid = v
        break
adb = None
try:
    p = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=20)
    adb = [l.split("\t")[0] for l in (p.stdout or "").splitlines()[1:] if l.strip()]
except Exception:
    pass
d["vidpid"] = vidpid
d["matched_boot"] = matched
d["adb_devices"] = adb
d["_note"] = "刷完后重新枚举 → CB-01 (VID:PID 与基线一致 + 不匹配 BOOT 签名 + prod 下 adb 为空)"
json.dump(d, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"  → VID:PID={vidpid}, 匹配 BOOT 签名 {len(matched)} 条, adb 设备 {adb}")
PY
  return 0
}

# ------------------------------------------------------------------ 主流程
FAILED_STEP=""
if [ -z "$ONLY_STEP" ] || [ "$ONLY_STEP" = "all" ]; then
  run_step0 || FAILED_STEP="step0"
  if [ -z "$FAILED_STEP" ]; then run_step1 || FAILED_STEP="step1"; fi
  if [ -z "$FAILED_STEP" ]; then run_step2 || FAILED_STEP="step2"; fi
  if [ -z "$FAILED_STEP" ]; then run_step3 || FAILED_STEP="step3"; fi
  if [ -z "$FAILED_STEP" ]; then run_step4 || FAILED_STEP="step4"; fi
  if [ -z "$FAILED_STEP" ]; then run_step5 || FAILED_STEP="step5"; fi
  if [ -z "$FAILED_STEP" ]; then run_step6 || FAILED_STEP="step6"; fi
else
  case "$ONLY_STEP" in
    step0) run_step0 ;; step1) run_step1 ;; step2) run_step2 ;; step3) run_step3 ;;
    step4) run_step4 ;; step5) run_step5 ;; step6) run_step6 ;;
    *) bad "未知步骤: $ONLY_STEP"; exit 3 ;;
  esac
fi

if [ -n "$FAILED_STEP" ]; then
  bad "步骤 $FAILED_STEP 未通过 → 自动抓失败现场"
  collect_forensics
fi

step "机械判定 (CB-01 ~ CB-09 → BR-01)"
python3 SW/tools/s2_board_judge.py --evidence-dir "$EVDIR" --config "$CFG" \
        --out "$EVDIR/s2_br01_verdict.json"
JRC=$?
say ""
say "判定结果已落盘: $EVDIR/s2_br01_verdict.json"
say "★ BR-01 是否判过, 由**项目总工**签 (修复人不能自验; issue_log ISS-120 verify_by=main)"
exit $JRC
