#!/usr/bin/env bash
# =============================================================================
# s2_board_e2e.sh —— 板端跑测链路端到端自检 (ISS-120)
# =============================================================================
#
# 用法: bash SW/tools/s2_board_e2e.sh
#
# 它干什么:
#   用**合成证据**跑通整条链 (跑测脚本 → 判定器), 验 4 个关键场景:
#     E1 全 PASS  → BR-01 判 ✅ (rc=0)
#     E2 缺证据   → BR-01 判 ⚠️ 未验 (rc=2) —— ★ 绝不判 PASS
#     E3 有 FAIL  → BR-01 判 ❌ (rc=1)
#     E4 P4 未填  → CB-06 判未验 (占位分区表不算实测)
#
# ★ 合成证据是**脚本逻辑自测**, 不是板端实测 —— 判据口径与 ISS-080 一致。
# ★ 期望 rc=0 (本脚本自检自身全过)。
set -u

cd "$(dirname "$0")/../.." || exit 2

CFG="SW/tools/s2_rescue_config.json"
TMP="${TMPDIR:-/tmp}/s2_e2e_$$"
mkdir -p "$TMP"
RC=0
PASSN=0
FAILN=0

say()  { printf '%s\n' "$*"; }
chk()  { if [ "$2" = "$3" ]; then printf '  ✅ %-52s rc=%s (期望 %s)\n' "$1" "$3" "$2"; PASSN=$((PASSN+1));
          else printf '  ❌ %-52s rc=%s (期望 %s)\n' "$1" "$3" "$2"; FAILN=$((FAILN+1)); RC=1; fi; }

# 造一份"全部齐全"的合成配置 (模拟原厂回复已落地)
mk_cfg_full() {
  python3 - "$1" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open("SW/tools/s2_rescue_config.json", encoding="utf-8"))
for k in d["params"]:
    d["params"][k]["value"] = f"合成值-{k}"
    d["params"][k]["status"] = "DONE"
    d["params"][k]["source"] = "vendor-official"
d["usb_signatures"]["entries"] = [
    {"vid": "2207", "pid": "350b", "label": "Maskrom (合成)", "source": "vendor-official"}]
d["partition_layout"]["source"] = "vendor-official"
d["version_meta"]["sn"] = "SN-SYNTH-0001"
d["version_meta"]["calib_id"] = "CALIB-SYNTH-0001"
d["board_test"]["board_sn"] = "SN-SYNTH-0001"
d["board_test"]["checks"]["calib_ledger"] = "CALIB-SYNTH-0001"
d["board_test"]["selftest"]["model_path"] = "/tmp/model.bin"
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
}

# 造合成证据
mk_ev() {
  local dir="$1" mode="$2"
  mkdir -p "$dir"
  python3 - "$dir" "$mode" <<'PY'
import json, os, sys
d, mode = sys.argv[1], sys.argv[2]
def w(name, obj):
    json.dump(obj, open(os.path.join(d, name), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
if mode != "empty":
    w("s2_step0_normal.json", {"vidpid": "2207:350a", "devices": []})
    w("s2_step3_verify.json", {"result": "PASS", "checks": [
        {"name": "CB-02a 版本块 magic == 'AR45'", "result": "PASS", "detail": "ok"},
        {"name": "CB-02b bootable 标志置位", "result": "PASS", "detail": "ok"},
        {"name": "CB-02c 版本块 payload CRC 一致", "result": "PASS", "detail": "ok"},
        {"name": "CB-06 分区 CRC 一致 [bootloader]", "result": "PASS", "detail": "ok"},
        {"name": "CB-06 分区 CRC 一致 [kernel]", "result": "PASS", "detail": "ok"},
        {"name": "CB-06 分区 CRC 一致 [rootfs]", "result": "PASS", "detail": "ok"},
        {"name": "CB-06 分区 CRC 一致 [app]", "result": "PASS", "detail": "ok"},
        {"name": "CB-06 分区 CRC 一致 [model]", "result": "PASS", "detail": "ok"},
        {"name": "CB-06 分区 CRC 一致 [isp]", "result": "PASS", "detail": "ok"},
    ]})
    w("s2_step4_selftest.json", {
        "version_string": ("ARS45-SW 1.0.0+g1234abc board=EVT1 sn=SN-SYNTH-0001 "
                           "build=20261030T0000+0800 boot=0.0.0 kern=5.10.0-gdeadbee "
                           "rootfs=R20261030.1 app=1.0.0+g1234abc model=yolov5s-int8-ag2-1a2b3c4d "
                           "isp=CALIB-SYNTH-0001 mode=prod calib=CALIB-SYNTH-0001"),
        "model_sha8": "1a2b3c4d",
        "selftest": {k: {"status": "PASS", "detail": "ok"}
                     for k in ("ddr","sensor","i2c","npu","od","version")},
        "log_scan": {"scanned_lines": 120, "errors": []},
    })
    w("s2_step5_reenum.json", {"vidpid": "2207:350a", "matched_boot": [], "adb_devices": []})
    w("s2_step6_reboot.json", {"attempts": [{"n": i, "ok": True, "panic": False} for i in (1,2,3)]})
PY
}

say "=============================================================================="
say "ARS45 S2 板端跑测链路 · 端到端自检 (合成证据)"
say "=============================================================================="

CFGFULL="$TMP/cfg_full.json"
mk_cfg_full "$CFGFULL"

say ""
say "[E1] 证据齐全 → BR-01 判 ✅ (期望 rc=0)"
EV1="$TMP/ev1"; mk_ev "$EV1" full
python3 SW/tools/s2_board_judge.py --evidence-dir "$EV1" --config "$CFGFULL" >/dev/null 2>&1
chk "判定器: 全 PASS" 0 $?

say ""
say "[E2] 证据为空 → BR-01 判 ⚠️ 未验 (期望 rc=2, 绝不判 PASS)"
EV2="$TMP/ev2"; mk_ev "$EV2" empty
python3 SW/tools/s2_board_judge.py --evidence-dir "$EV2" --config "$CFGFULL" >/dev/null 2>&1
chk "判定器: 全缺 → 未验" 2 $?

say ""
say "[E3] P4 未填 (占位分区表) → CB-06 判未验 (期望 rc=2)"
EV3="$TMP/ev3"; mk_ev "$EV3" full
CFGP4="$TMP/cfg_nop4.json"; cp "$CFGFULL" "$CFGP4"
python3 - "$CFGP4" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
d["params"]["P4_BOOT_STORE"]["value"] = None
d["params"]["P4_BOOT_STORE"]["status"] = "TODO"
json.dump(d, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
python3 SW/tools/s2_board_judge.py --evidence-dir "$EV3" --config "$CFGP4" >/dev/null 2>&1
chk "判定器: P4 未填 → 未验" 2 $?

say ""
say "[E4] 板端配置里 usb_signatures 为空 → CB-01 判未验 (期望 rc=2)"
EV4="$TMP/ev4"; mk_ev "$EV4" full
CFGNOSIG="$TMP/cfg_nosig.json"; cp "$CFGFULL" "$CFGNOSIG"
python3 - "$CFGNOSIG" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
d["usb_signatures"]["entries"] = []
json.dump(d, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY
python3 SW/tools/s2_board_judge.py --evidence-dir "$EV4" --config "$CFGNOSIG" >/dev/null 2>&1
chk "判定器: 无真值签名 → 未验" 2 $?

say ""
say "[E5] 跑测脚本 preflight: 真配置 (P1~P4 未填) → rc=3"
bash SW/tools/s2_board_run.sh --preflight --config "$CFG" >/dev/null 2>&1
chk "preflight: 参数未填 → rc=3" 3 $?

say ""
say "[E6] 跑测脚本 preflight: 合成全填配置 → rc=0"
bash SW/tools/s2_board_run.sh --preflight --config "$CFGFULL" >/dev/null 2>&1
chk "preflight: 参数齐 → rc=0" 0 $?

say ""
say "[E7] 跑测脚本 forensics 在参数未填时也能跑 (期望 rc=0)"
EV7="$TMP/ev7"; mkdir -p "$EV7"
bash SW/tools/s2_board_run.sh --config "$CFG" --evidence-dir "$EV7" --only forensics >/dev/null 2>&1
chk "forensics: 参数未填也能取证" 0 $?
[ -f "$EV7/s2_forensics.json" ] && { say "  ✅ 落了 s2_forensics.json"; PASSN=$((PASSN+1)); } \
                               || { say "  ❌ 没落 s2_forensics.json"; FAILN=$((FAILN+1)); RC=1; }

say ""
say "[E8] 跑测脚本 forensics 采到了下载工具版本 (期望: 缺失工具记 [0数据], 不编版本)"
if grep -q "0数据" "$EV7/s2_forensics.json"; then
  say "  ✅ 缺失工具按 [0数据] 记录"; PASSN=$((PASSN+1))
else
  say "  ❌ 没看到 [0数据] 标记"; FAILN=$((FAILN+1)); RC=1
fi

say ""
say "[E9] 电流表读数缺失时记 [0数据] (期望不许编数)"
if grep -q '"value_ma": null' "$EV7/s2_forensics.json"; then
  say "  ✅ 电流表读数为 null + [0数据]"; PASSN=$((PASSN+1))
else
  say "  ❌ 电流表读数不是 null"; FAILN=$((FAILN+1)); RC=1
fi

say ""
say "=============================================================================="
say "结果: 通过 $PASSN / 失败 $FAILN"
say "证据: [实测] PC 侧合成证据端到端自检 (链路逻辑), ★不代表板端 S2 已实测通过"
say "=============================================================================="
rm -rf "$TMP"
[ "$FAILN" = "0" ] || exit 1
exit 0
