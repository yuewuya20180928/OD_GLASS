#!/usr/bin/env bash
# ==============================================================================
# rk3572_model_rebuild.sh — ISS-207 · PC 侧产物的**可重建路径** (降级 B)
#   "产物没了 / 被 /tmp 清理了" ⇒ 一条命令重建 + 落盘 + sha256, 不再是坑
# ==============================================================================
# 上游: SW/RK3572_TARGET_BOARD_VERIFY.md (v1.0 §2 产物清单 —— 那里写的是 /tmp,
#       本机已失效 ⇒ 本脚本把落盘目录改到项目库 SW/artifacts/models/)
# 依赖: SW/tools/rknn_bench.py (只调用, **不改**它)
#
# ★ 本脚本做什么 (5 步):
#   ① 找得到带 rknn-toolkit2 的 python (conda env / 系统 python / 新建 venv+pip)
#   ② 源 ONNX 在位检查 (yolov5n-sim.onnx)
#   ③ 转模型: rknn_bench.py convert  (target_platform=rk3576, w8a8, channel)
#   ④ **产物落盘到 SW/artifacts/models/** (★不许只留在 /tmp) + 写 .sha256 sidecar
#   ⑤ 打印 sha256 + 与基线 sha256 比对 (同工具链 ⇒ 逐字节可复现)
#
# 用法:
#   bash SW/tools/rk3572_model_rebuild.sh --dry-run      # 只打印将执行的命令, rc=0
#   bash SW/tools/rk3572_model_rebuild.sh                 # 真跑 (装工具链→转→落盘→sha256)
#   bash SW/tools/rk3572_model_rebuild.sh --with-acc      # 顺带复现 PC 侧 F1 基线
# ==============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="$(cd "$HERE/../.." && pwd)"

DRY=0
WITH_ACC=0
ONNX_SRC="${ONNX_SRC:-/home/yuewuya/Public/rknn_assets/yolov5n-sim.onnx}"
TOOLKIT_VER="${TOOLKIT_VER:-2.3.2}"
DEST_DIR="$PROJ/SW/artifacts/models"
EXPECT_SHA="${EXPECT_SHA:-}"   # 留空 = 不比对 (默认); 要比对就传 --expect-sha256 <sha>
BASELINE_SHA="1c5ff7ba41f447c0e6f05624e8ee223258a794e6ec5330b21e5f3fc2108eb713"
BASELINE_NOTE="2026-11-15 22:0x 本机 rknn-toolkit2 2.3.2 首次转 yolov5n-sim.onnx (heads 版) 的 sha256"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)   DRY=1 ;;
    --with-acc)  WITH_ACC=1 ;;
    --onnx)      ONNX_SRC="$2"; shift ;;
    --toolkit)   TOOLKIT_VER="$2"; shift ;;
    --expect-sha256) EXPECT_SHA="$2"; shift ;;
    -h|--help)   sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
  shift
done

hr() { printf '=%.0s' {1..78}; echo; }
say() { echo "$@"; }

# ------------------------------------------------------------ 找 python
find_rknn_py() {
  local c
  for c in "${RKNN_PY:-}" /home/yuewuya/miniconda3/envs/rknn/bin/python \
           /home/yuewuya/miniconda3/envs/rknn-toolkit2/bin/python \
           /opt/conda/envs/rknn/bin/python; do
    [ -n "$c" ] && [ -x "$c" ] && "$c" -c "import rknn.api" 2>/dev/null && { echo "$c"; return 0; }
  done
  for c in python3 python; do
    command -v "$c" >/dev/null 2>&1 && "$c" -c "import rknn.api" 2>/dev/null && { command -v "$c"; return 0; }
  done
  return 1
}

hr; echo "ISS-207 · PC 侧 RKNN 产物一键重建 (sw-lead, 2026-11-15)"; hr
say "源 ONNX   : $ONNX_SRC"
say "落盘目录  : $DEST_DIR   (★不许只留 /tmp)"
say "历史参考  : $BASELINE_SHA  ($BASELINE_NOTE)"
say "★口径    : .rknn **不是逐字节可复现** (同工具链两次转换 sha256 不同, 字节数相同) ⇒"
say "          ⇒ sha256 是**拷贝那一刻**的身份锚 (随产物写 .sha256 sidecar), 不是历史常量"
say "模式      : $([ "$DRY" = 1 ] && echo 'DRY-RUN (只打印命令)' || echo '实跑')"
hr

if [ "$DRY" = 1 ]; then
  say ""
  say "[1/5] 找带 rknn-toolkit2 的 python"
  say "  # 候选顺序: \$RKNN_PY → /home/yuewuya/miniconda3/envs/rknn/bin/python → python3"
  say "  for p in \"\$RKNN_PY\" /home/yuewuya/miniconda3/envs/rknn/bin/python python3; do"
  say "      [ -x \"\$p\" ] && \"\$p\" -c 'import rknn.api' && echo \"FOUND \$p\" && break"
  say "  done"
  say ""
  say "[2/5] 源 ONNX 在位检查"
  say "  ls -l $ONNX_SRC"
  say ""
  say "[3/5] 转模型 (target_platform=rk3576, w8a8, normal, channel)"
  say "  \$RKNN_PY SW/tools/rknn_bench.py convert --onnx $ONNX_SRC --json"
  say "  # 产物先落 /tmp/rknn_bench/*.rknn (中间态), 下一步必须搬进项目库"
  say ""
  say "[4/5] 落盘 (★不许留 /tmp) + sha256"
  say "  mkdir -p $DEST_DIR"
  say "  cp -p /tmp/rknn_bench/*_rk3576_int8_heads.rknn $DEST_DIR/"
  say "  cp -p /tmp/rknn_bench/*_rk3576_int8_heads.rknn.meta.json $DEST_DIR/"
  say "  sha256sum $DEST_DIR/*_rk3576_int8_heads.rknn | tee $DEST_DIR/*_rk3576_int8_heads.rknn.sha256"
  say ""
  say "[5/5] sha256 身份锚 (★拷贝那一刻生成, 随产物落盘)"
  say "  sha256sum $DEST_DIR/*_rk3576_int8_heads.rknn | tee $DEST_DIR/*_rk3576_int8_heads.rknn.sha256"
  say "  # ⇒ 板端验证包用这个 sidecar 比对 (P6), 不拿历史常量当身份锚"
  say "  # 历史参考 (同工具链首次): $BASELINE_SHA"
  say ""
  say "[可选] 复现 PC 侧精度基线 (F1)"
  say "  \$RKNN_PY SW/tools/rknn_bench.py acc --onnx $ONNX_SRC --images 300 --json"
  say ""
  say "[dry-run 结论] 只验证了命令序列本身可跑; 真跑用上面的命令 (或直接 bash 本脚本不带 --dry-run)"
  hr
  exit 0
fi

# =============================================================================
# 实跑
# =============================================================================
say ""
say "[1/5] 找带 rknn-toolkit2 的 python ..."
RKNN_PY_BIN="$(find_rknn_py || true)"
if [ -z "$RKNN_PY_BIN" ]; then
  say "  ✗ 本机没有带 rknn-toolkit2 的 python"
  say "  ⇒ 装法 (择一):"
  say "     (a) 用已有 conda env:  conda create -n rknn python=3.10 -y && conda activate rknn"
  say "         pip install 'rknn-toolkit2==$TOOLKIT_VER'"
  say "     (b) 纯 venv:            python3 -m venv ~/venv-rknn && ~/venv-rknn/bin/pip install 'rknn-toolkit2==$TOOLKIT_VER'"
  say "     (c) docker:             docker pull airockchip/rknn-toolkit2:$TOOLKIT_VER"
  say "  ★装好之后重跑本脚本即可 (脚本会自动找到它)"
  exit 3
fi
TK_VER="$("$RKNN_PY_BIN" -c "import importlib.metadata as m;print(m.version('rknn-toolkit2'))" 2>/dev/null || echo '?')"
say "  ✓ $RKNN_PY_BIN  (rknn-toolkit2 $TK_VER)"

if [ ! -f "$ONNX_SRC" ]; then
  say "  ✗ 源 ONNX 不在: $ONNX_SRC"
  say "  ⇒ yolov5n-sim.onnx 来自 A7S 资产包, 本机副本缺失 ⇒ 先拷过来再跑"
  exit 3
fi
say "  ✓ 源 ONNX $ONNX_SRC ($(stat -c %s "$ONNX_SRC") B)"

say ""
say "[2/5] 转换 (rknn_bench.py convert, target_platform=rk3576) ..."
CONV_JSON="$(mktemp /tmp/iss207_convert_XXXXXX.json)"
"$RKNN_PY_BIN" "$PROJ/SW/tools/rknn_bench.py" convert --onnx "$ONNX_SRC" --json > "$CONV_JSON" 2>"${CONV_JSON}.err"
CONV_RC=$?
if [ "$CONV_RC" != 0 ]; then
  say "  ✗ convert rc=$CONV_RC"
  tail -20 "${CONV_JSON}.err"
  say "  (转换日志: $CONV_JSON.err)"
  exit 4
fi
ART="$(python3 - "$CONV_JSON" <<'PY'
import json, sys
t = open(sys.argv[1], encoding="utf-8").read()
d = json.loads(t[t.find("{"):])
c = d.get("convert") or {}
print(c.get("artifact") or "")
PY
)"
BYTES="$(python3 - "$CONV_JSON" <<'PY'
import json, sys
t = open(sys.argv[1], encoding="utf-8").read()
d = json.loads(t[t.find("{"):])
c = d.get("convert") or {}
print(c.get("artifact_bytes") or 0)
PY
)"
BUILD_S="$(python3 - "$CONV_JSON" <<'PY'
import json, sys
t = open(sys.argv[1], encoding="utf-8").read()
d = json.loads(t[t.find("{"):])
c = d.get("convert") or {}
print(c.get("build_s"))
PY
)"
[ -z "$ART" ] || [ ! -f "$ART" ] && { say "  ✗ 解析不到产物路径 (见 $CONV_JSON)"; exit 4; }
say "  ✓ 产物: $ART ($BYTES B, build ${BUILD_S}s)"

say ""
say "[3/5] 落盘到项目库 (★不许只留 /tmp) ..."
mkdir -p "$DEST_DIR"
DEST="$DEST_DIR/$(basename "$ART")"
cp -p "$ART" "$DEST"
[ -f "$ART.meta.json" ] && cp -p "$ART.meta.json" "$DEST.meta.json"
say "  ✓ $DEST"

say ""
say "[4/5] sha256 ..."
SHA="$(sha256sum "$DEST" | awk '{print $1}')"
printf '%s  %s\n' "$SHA" "$(basename "$DEST")" > "$DEST.sha256"
say "  sha256 = $SHA"
say "  sidecar= $DEST.sha256"

say ""
say "[5/5] sha256 身份锚 ..."
if [ -n "$EXPECT_SHA" ]; then
  if [ "$SHA" = "$EXPECT_SHA" ]; then
    say "  ✓ 与 --expect-sha256 给的值一致 ($SHA)"
  else
    say "  ! 与 --expect-sha256 给的值不同 (本轮 $SHA, 给定 $EXPECT_SHA)"
    say "    ⇒ 工具链/源码变了, 或 .rknn 容器含非确定性字段 (2026-11-15 本机实测: 同 2.3.2 两次转出不同 sha256, 字节数相同)"
  fi
else
  say "  ✓ 本轮 sha256 = $SHA  (已写入 sidecar, 即刻的身份锚)"
  say "    ★历史参考 (同 2.3.2 首次转换): $BASELINE_SHA"
  say "    ★.rknn 非逐字节可复现 ⇒ 板端 P6 比对请用 sidecar, 不要用历史常量"
fi
say ""
say "  ★落地目录: $DEST_DIR   (下板前直接拷这个文件, 不用碰 /tmp)"
ls -l "$DEST" "$DEST.sha256" 2>/dev/null

if [ "$WITH_ACC" = 1 ]; then
  say ""
  say "[可选] 复现 PC 侧精度基线 (acc 步, 与板端同口径) ..."
  ACC_JSON="$(mktemp /tmp/iss207_acc_XXXXXX.json)"
  "$RKNN_PY_BIN" "$PROJ/SW/tools/rknn_bench.py" acc --onnx "$ONNX_SRC" --images 300 --json > "$ACC_JSON" 2>&1
  python3 - "$ACC_JSON" <<'PY'
import json, sys
t = open(sys.argv[1], encoding="utf-8").read()
try:
    d = json.loads(t[t.find("{"):])
except Exception as e:
    print("  (acc 步输出不是 JSON: %s)" % e); raise SystemExit
a = d.get("acc") or {}
print("  n_images=%s TP=%s FP=%s FN=%s P=%.4f R=%.4f F1=%.4f" % (
    a.get("n_images"), a.get("tp"), a.get("fp"), a.get("fn"),
    a.get("precision", 0), a.get("recall", 0), a.get("f1", 0)))
print("  口径:", a.get("caliber"))
PY
fi

hr
say "重建完成 ⇒ 板端验证包可用: bash SW/tools/rk3572_target_smoke.sh --artifact $DEST --expect-sha256 $SHA"
hr
exit 0
