#!/usr/bin/env bash
# ==============================================================================
# rk3572_model_rebuild.sh — PC 侧 RKNN 产物的可重建路径 (降级 B)
#   "产物没了 / 被系统清理了" ⇒ 一条命令重建 + 落盘 + sha256, 不再是坑
#
# ★★ v2.0 (2026-11-23 · ISS-355) · ★默认路线已迁到主路线★ ★★
#
#   ★主路线 (默认)★    : rknn3-toolkit 1.2.0 + target_platform='rk3572'
#       依据 [实测] : ISS-263 (rknn3-toolkit 1.2.0: config rc=0 / 转换四步 rc 全 0 /
#                     产物 249,360 B / 跨 3 会话 9/9 逐字节相同)
#       依据 [官网] : rknn3-toolkit README「Supported Platforms: RK1820 / RK1828 / RK3572」
#   ★次要路线① (保留)★ : rknn-toolkit2 2.3.2 + target_platform='rk3576' ⇒ ROUTE=legacy 切回
#       ★定位★ : 历史对照 / 复现 2026-11-15 的 2.3.2 基线 (历史留档)
#       ★代价★ : 板端 runtime 是否接受该路线的产物 = [0数据]
#                 (官方把 RK3572(librknn3_api_native.so) 与 RK3576(librknn3_api_rkcp.so)
#                  分成两条 runtime ⇒ 官方层无互换表述)
#
#   ★产物形态 (主路线)★ : rknn3-toolkit 一次导出 **.rknn + 同名 .weight 两件套**
#       (板端 load_rknn(model_path, weight_path) 要两个参数 ⇒ 只拷 .rknn 一定失败)
#       ⇒ 本脚本落盘段强制两件套同时到位, 缺 .weight ⇒ 直接失败退出 (rc≠0)
#
# 上游 (只读引用): SW/RKNN_BENCH.md §5 (v2.1 追加段) · SW/RK3572_TARGET_COMPAT_V2.md §8
#                 · HANDOFF/2026-11-23_sw-lead_ISS353_rk3572目标口径清账.md
# 依赖 (只调用, **不改**它们): SW/tools/rknn_bench.py (次要路线①) ·
#                 SW/tools/cut_postprocessor.py (切 head) · SW/tools/iss263_rknn3_install.sh (装环境)
#
# 用法:
#   bash SW/tools/rk3572_model_rebuild.sh --print-route      # ★机器可读: 打印生效路线
#   bash SW/tools/rk3572_model_rebuild.sh --dry-run           # 只打印将执行的命令, rc=0
#   bash SW/tools/rk3572_model_rebuild.sh                     # 真跑 (准备→转换→两件套→sha256)
#   ROUTE=legacy bash SW/tools/rk3572_model_rebuild.sh        # ★次要路线① (旧链, 代价见上)
#   bash SW/tools/rk3572_model_rebuild.sh --copy-only SRC DST # ★只跑两件套拷贝段 (闸的自测缝)
# ==============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="$(cd "$HERE/../.." && pwd)"

# ─────────────────────────────────────────────────────────────────────────────
# ★★ 路线默认值 (机器可读 · 闸 SW/tools/check_iss355_convert_route.py 读这一段) ★★
#     ★这里的字面量 = 「当下执行口径」★ ⇒ 闸读的是值, 不是注释
# ─────────────────────────────────────────────────────────────────────────────
ROUTE_DEFAULT="rknn3"                      # ★主路线★
TARGET_PLATFORM_DEFAULT="rk3572"           # ★主路线 target★
TOOLKIT_PKG_DEFAULT="rknn3-toolkit"        # ★主路线工具链★
TOOLKIT_VER_DEFAULT="1.2.0"                # ★主路线工具链版本★
LEGACY_ROUTE_NAME="legacy"                 # ★次要路线① 的名字★
LEGACY_TARGET_PLATFORM_DEFAULT="rk3576"   # ISS355-SECONDARY-ROUTE-① (历史留档: 2026-11-15 的 2.3.2 基线)
LEGACY_TOOLKIT_PKG_DEFAULT="rknn-toolkit2"
LEGACY_TOOLKIT_VER_DEFAULT="2.3.2"

# 生效值 (环境变量可覆盖; 默认值 = 上面那组 ⇒ 默认必须是新链)
ROUTE="${ROUTE:-$ROUTE_DEFAULT}"
TARGET_PLATFORM="${TARGET_PLATFORM:-$TARGET_PLATFORM_DEFAULT}"
TOOLKIT_PKG="${TOOLKIT_PKG:-$TOOLKIT_PKG_DEFAULT}"
TOOLKIT_VER="${TOOLKIT_VER:-$TOOLKIT_VER_DEFAULT}"

DRY=0
PRINT_ROUTE=0
COPY_ONLY=0
COPY_SRC=""
COPY_DST=""
WITH_ACC=0
ONNX_SRC="${ONNX_SRC:-/home/yuewuya/Public/rknn_assets/yolov5n-sim.onnx}"
CALIB_DIR="${CALIB_DIR:-/home/yuewuya/Public/radxa_yolo/calib_yolov5_100}"
DEST_DIR="${DEST_DIR:-$PROJ/SW/artifacts/models}"
LEGACY_DEST_DIR="${LEGACY_DEST_DIR:-$PROJ/SW/artifacts/models}"
WORK_DIR="${WORK_DIR:-$PROJ/tmp/iss355/rknn3}"     # ★scratch 一律落项目盘 (/tmp 配额已打满)★
EXPECT_SHA="${EXPECT_SHA:-}"
EXPECT_WEIGHT_SHA="${EXPECT_WEIGHT_SHA:-}"
CUT_HEADS="${CUT_HEADS:-1}"
IMGSZ=640
LEGACY_BASELINE_SHA="1c5ff7ba41f447c0e6f05624e8ee223258a794e6ec5330b21e5f3fc2108eb713"
LEGACY_BASELINE_NOTE="2026-11-15 22:0x 本机 rknn-toolkit2 2.3.2 首次转 yolov5n-sim.onnx (heads 版) 的 sha256"

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)      DRY=1 ;;
    --print-route)  PRINT_ROUTE=1 ;;
    --with-acc)     WITH_ACC=1 ;;
    --copy-only)    COPY_ONLY=1; COPY_SRC="$2"; COPY_DST="$3"; shift 2 ;;
    --onnx)         ONNX_SRC="$2"; shift ;;
    --calib-dir)    CALIB_DIR="$2"; shift ;;
    --dest)         DEST_DIR="$2"; shift ;;
    --work-dir)     WORK_DIR="$2"; shift ;;
    --route)        ROUTE="$2"; shift ;;
    --target)       TARGET_PLATFORM="$2"; shift ;;
    --toolkit-pkg)  TOOLKIT_PKG="$2"; shift ;;
    --toolkit)      TOOLKIT_VER="$2"; shift ;;
    --expect-sha256) EXPECT_SHA="$2"; shift ;;
    --expect-weight-sha256) EXPECT_WEIGHT_SHA="$2"; shift ;;
    -h|--help)      sed -n '2,32p' "$0"; exit 0 ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
  shift
done

hr() { printf '=%.0s' {1..78}; echo; }
say() { echo "$@"; }
sha() { sha256sum "$1" 2>/dev/null | awk '{print $1}'; }

# =============================================================================
# ★--print-route : 机器可读 (闸靠它读「当下的默认路线」, 不靠注释) ★
# =============================================================================
if [ "$PRINT_ROUTE" = "1" ]; then
  if [ "$ROUTE" = "$LEGACY_ROUTE_NAME" ]; then
    EFF_TARGET="$LEGACY_TARGET_PLATFORM_DEFAULT"
    EFF_PKG="$LEGACY_TOOLKIT_PKG_DEFAULT"
    EFF_VER="$LEGACY_TOOLKIT_VER_DEFAULT"
  else
    EFF_TARGET="$TARGET_PLATFORM"
    EFF_PKG="$TOOLKIT_PKG"
    EFF_VER="$TOOLKIT_VER"
  fi
  echo "# ISS-355 · rk3572_model_rebuild.sh · 生效路线 (机器可读)"
  echo "route=$ROUTE"
  echo "effective_target_platform=$EFF_TARGET"
  echo "effective_toolkit_pkg=$EFF_PKG"
  echo "effective_toolkit_version=$EFF_VER"
  echo "target_platform=$TARGET_PLATFORM"
  echo "toolkit_pkg=$TOOLKIT_PKG"
  echo "toolkit_version=$TOOLKIT_VER"
  echo "legacy_route=$LEGACY_ROUTE_NAME"
  echo "legacy_target_platform=$LEGACY_TARGET_PLATFORM_DEFAULT"
  echo "legacy_toolkit_pkg=$LEGACY_TOOLKIT_PKG_DEFAULT"
  echo "legacy_toolkit_version=$LEGACY_TOOLKIT_VER_DEFAULT"
  echo "route_default=$ROUTE_DEFAULT"
  echo "target_platform_default=$TARGET_PLATFORM_DEFAULT"
  echo "toolkit_pkg_default=$TOOLKIT_PKG_DEFAULT"
  echo "toolkit_version_default=$TOOLKIT_VER_DEFAULT"
  echo "artifact_pair=2"      # ★两件套: .rknn + 同名 .weight★
  exit 0
fi

# =============================================================================
# ★两件套拷贝段 (★主路线专用 · 缺 .weight ⇒ 失败, 不许只拷 .rknn★)
#   $1 = 源 .rknn 路径, $2 = 落盘目录, $3 = 产物基名 (可选, 默认取源 basename 去后缀)
# =============================================================================
copy_two_piece() {
  local src_rknn="$1" dest_dir="$2" base="${3:-}"
  local src_weight="${src_rknn%.rknn}.weight"
  [ -n "$base" ] || base="$(basename "${src_rknn%.rknn}")"
  if [ ! -f "$src_rknn" ]; then
    say "  ✗ 源产物不在: $src_rknn"
    return 1
  fi
  if [ ! -f "$src_weight" ]; then
    say "  ✗ 两件套不齐: 缺 $src_weight"
    say "    ★rknn3-toolkit 的产物是 .rknn + 同名 .weight 两件套 ⇒ 只拷 .rknn 一定失败★"
    say "    (板端 load_rknn(model_path, weight_path) 要两个参数)"
    return 1
  fi
  mkdir -p "$dest_dir"
  local dst_rknn="$dest_dir/$base.rknn" dst_weight="$dest_dir/$base.weight"
  cp -p "$src_rknn" "$dst_rknn"
  cp -p "$src_weight" "$dst_weight"
  local s1 s2
  s1="$(sha "$dst_rknn")"; s2="$(sha "$dst_weight")"
  printf '%s  %s\n' "$s1" "$base.rknn"  > "$dst_rknn.sha256"
  printf '%s  %s\n' "$s2" "$base.weight" > "$dst_weight.sha256"
  say "  ✓ .rknn   $dst_rknn ($(stat -c%s "$dst_rknn") B)"
  say "  ✓ .weight $dst_weight ($(stat -c%s "$dst_weight") B)"
  say "  ✓ sha256  rknn=$s1"
  say "  ✓ sha256  weight=$s2"
  if [ -n "$EXPECT_SHA" ] && [ "$EXPECT_SHA" != "$s1" ]; then
    say "  ! .rknn sha256 与 --expect-sha256 给的值不同 (本轮 $s1 / 给定 $EXPECT_SHA)"
  fi
  if [ -n "$EXPECT_WEIGHT_SHA" ] && [ "$EXPECT_WEIGHT_SHA" != "$s2" ]; then
    say "  ! .weight sha256 与 --expect-weight-sha256 给的值不同 (本轮 $s2 / 给定 $EXPECT_WEIGHT_SHA)"
  fi
  return 0
}

# --copy-only: ★只跑两件套拷贝段★ (闸的自测缝: 有 .weight ⇒ 必须两件套都到位;
#              没有 .weight ⇒ 必须失败)
if [ "$COPY_ONLY" = "1" ]; then
  hr; say "ISS-355 · 两件套拷贝段 (--copy-only)"; hr
  say "SRC : $COPY_SRC"
  say "DST : $COPY_DST"
  found=""
  if [ -d "$COPY_SRC" ]; then
    for f in "$COPY_SRC"/*.rknn; do
      [ -e "$f" ] || continue
      found="$f"; break
    done
  elif [ -f "$COPY_SRC" ]; then
    found="$COPY_SRC"
  fi
  if [ -z "$found" ]; then
    say "✗ 在 $COPY_SRC 里找不到 .rknn"
    exit 3
  fi
  copy_two_piece "$found" "$COPY_DST"
  rc=$?
  [ "$rc" = "0" ] && say "★两件套拷贝 OK (两件都在位)" || say "★两件套拷贝 FAIL (rc=$rc)"
  exit "$rc"
fi

# =============================================================================
# 找 python (★按【已安装的发行包】判, 不靠 import rknn.api —— 两代工具链都提供它★)
# =============================================================================
find_py_for_pkg() {
  local pkg="$1" want_ver="$2" c
  for c in "${RKNN_PY:-}" "$HOME/miniconda3/envs/rknn3/bin/python" \
           "$HOME/miniconda3/envs/rknn/bin/python" \
           "$HOME/miniconda3/envs/rknn-toolkit2/bin/python" \
           "/opt/conda/envs/rknn3/bin/python" "/opt/conda/envs/rknn/bin/python"; do
    [ -n "$c" ] && [ -x "$c" ] || continue
    "$c" - "$pkg" "$want_ver" <<'PY' 2>/dev/null && { echo "$c"; return 0; }
import importlib.metadata as m, sys
pkg, want = sys.argv[1], sys.argv[2]
try:
    v = m.version(pkg)
except Exception:
    sys.exit(1)
sys.exit(0 if v == want else 1)
PY
  done
  for c in python3 python; do
    command -v "$c" >/dev/null 2>&1 || continue
    "$c" - "$pkg" "$want_ver" <<'PY' 2>/dev/null && { command -v "$c"; return 0; }
import importlib.metadata as m, sys
pkg, want = sys.argv[1], sys.argv[2]
try:
    v = m.version(pkg)
except Exception:
    sys.exit(1)
sys.exit(0 if v == want else 1)
PY
  done
  return 1
}

hr; echo "ISS-355 · PC 侧 RKNN 产物一键重建 (sw-lead · 主路线迁移版 · 2026-11-23)"; hr
say "生效路线    : $ROUTE  (target_platform=$TARGET_PLATFORM · $TOOLKIT_PKG $TOOLKIT_VER)"
if [ "$ROUTE" = "$LEGACY_ROUTE_NAME" ]; then
  say "★路线定位  : 次要路线① (历史对照 / 复现 2026-11-15 的 2.3.2 基线)"
  say "★路线代价  : 板端 runtime 是否接受该路线的产物 = [0数据] (官方把 RK3572 与 RK3576 分成两条 runtime)"
else
  say "★路线定位  : 主路线 (rknn3-toolkit 1.2.0 · ISS-263 实测 rc=0 · 产物逐字节可复现)"
fi
say "源 ONNX     : $ONNX_SRC"
say "校准集源    : $CALIB_DIR"
say "落盘目录    : $DEST_DIR   (★不许只留临时目录★)"
say "scratch     : $WORK_DIR   (★项目盘·不许写 /tmp★)"
say "★产物形态  : 主路线 = .rknn + 同名 .weight **两件套** ⇒ 落盘段强制成对, 缺一即失败"
say "模式        : $([ "$DRY" = 1 ] && echo 'DRY-RUN (只打印命令)' || echo '实跑')"
hr

if [ "$DRY" = 1 ]; then
  say ""
  say "[1/5] 找带 $TOOLKIT_PKG $TOOLKIT_VER 的 python"
  say "  # ★按已安装发行包判版本 (两代工具链都提供 rknn.api ⇒ 不能靠 import 判)★"
  say "  \$RKNN_PY_BIN -c \"import importlib.metadata as m; print(m.version('$TOOLKIT_PKG'))\""
  say ""
  say "[2/5] 源 ONNX 在位检查"
  say "  ls -l $ONNX_SRC"
  say ""
  say "[3/5] 准备 (切 head + 量化校准集)"
  say "  # 切 head: 复用 SW/tools/cut_postprocessor.py (板端真正能用的 3 路 raw head 版本)"
  say "  \$RKNN_PY_BIN $PROJ/SW/tools/cut_postprocessor.py $ONNX_SRC \\"
  say "      $WORK_DIR/model_heads.onnx --keep 350 498 646"
  say "  # 校准集: letterbox ${IMGSZ}x${IMGSZ} (与 SW/tools/rknn_bench.py calib 步同口径)"
  say "  #   ⇒ $WORK_DIR/calib/*.png + $WORK_DIR/dataset.txt"
  say ""
  say "[4/5] 转换 (★主路线★: $TOOLKIT_PKG $TOOLKIT_VER · target_platform=$TARGET_PLATFORM · w8a8 · channel)"
  say "  # 调用序列与 SW/tools/iss263_rknn3_convert.py 已实测的那条逐字相同:"
  say "  #   config(target_platform=...) → load_onnx → build(do_quantization=True, dataset=) → export_rknn"
  say "  # ★export_rknn 一次产出 .rknn + 同名 .weight 两件套★"
  say ""
  say "[5/5] 落盘 (★两件套一起拷, 缺 .weight 直接失败★) + sha256"
  say "  cp -p <out>/<stem>_int8_heads.rknn   $DEST_DIR/"
  say "  cp -p <out>/<stem>_int8_heads.weight $DEST_DIR/"
  say "  sha256sum $DEST_DIR/*_int8_heads.rknn   | tee ...rknn.sha256"
  say "  sha256sum $DEST_DIR/*_int8_heads.weight | tee ...weight.sha256"
  say ""
  say "[板端] 板到手时一条命令出 PASS/FAIL (ISS-250 降级 A):"
  say "  bash SW/tools/rk3572_rknn3_board_smoke.sh --rknn <.rknn> --weight <.weight> \\"
  say "      --expect-sha256 <sha> --expect-weight-sha256 <sha> --out ./evidence/"
  say ""
  say "[dry-run 结论] 只验证了命令序列本身; 真跑用上面的命令 (或直接 bash 本脚本不带 --dry-run)"
  hr
  exit 0
fi

# =============================================================================
# 实跑
# =============================================================================
say ""
say "[1/5] 找带 $TOOLKIT_PKG $TOOLKIT_VER 的 python ..."
if [ "$ROUTE" = "$LEGACY_ROUTE_NAME" ]; then
  TOOLKIT_PKG="$LEGACY_TOOLKIT_PKG_DEFAULT"
  TOOLKIT_VER="$LEGACY_TOOLKIT_VER_DEFAULT"
  TARGET_PLATFORM="$LEGACY_TARGET_PLATFORM_DEFAULT"
  say "  ★次要路线①: 工具链 = $TOOLKIT_PKG $TOOLKIT_VER · target_platform=$TARGET_PLATFORM"
fi
RKNN_PY_BIN="$(find_py_for_pkg "$TOOLKIT_PKG" "$TOOLKIT_VER" || true)"
if [ -z "$RKNN_PY_BIN" ]; then
  say "  ✗ 本机没有带 $TOOLKIT_PKG $TOOLKIT_VER 的 python"
  say "  ⇒ 装法 (★主路线★):"
  say "     (a) 用已有 conda env:  conda create -n rknn3 python=3.10 -y && conda activate rknn3"
  say "         pip install 'rknn3-toolkit==$TOOLKIT_VER'    ★官方 wheel 在 GitHub Releases★"
  say "     (b) 复用现成脚本:    bash $PROJ/SW/tools/iss263_rknn3_install.sh"
  say "  ⇒ 装好之后重跑本脚本即可 (脚本会自动找到它)"
  exit 3
fi
TK_VER="$("$RKNN_PY_BIN" -c "import importlib.metadata as m;print(m.version('$TOOLKIT_PKG'))" 2>/dev/null || echo '?')"
say "  ✓ $RKNN_PY_BIN  ($TOOLKIT_PKG $TK_VER)"

if [ ! -f "$ONNX_SRC" ]; then
  say "  ✗ 源 ONNX 不在: $ONNX_SRC"
  say "  ⇒ yolov5n-sim.onnx 来自 A7S 资产包, 本机副本缺失 ⇒ 先拷过来再跑"
  exit 3
fi
say "  ✓ 源 ONNX $ONNX_SRC ($(stat -c%s "$ONNX_SRC") B)"

if [ "$ROUTE" = "$LEGACY_ROUTE_NAME" ]; then
  # ── 次要路线①: 旧链 (rknn-toolkit2 2.3.2) · 直接调 SW/tools/rknn_bench.py convert ──
  say ""
  say "[2/5] 转换 (★次要路线①: rknn_bench.py convert · $TOOLKIT_PKG $TOOLKIT_VER) ..."
  LEGACY_WORK="$PROJ/tmp/iss355/legacy_rknn_bench"
  mkdir -p "$LEGACY_WORK"
  CONV_JSON="$WORK_DIR/legacy_convert.json"
  mkdir -p "$WORK_DIR"
  "$RKNN_PY_BIN" "$PROJ/SW/tools/rknn_bench.py" convert --onnx "$ONNX_SRC" --json > "$CONV_JSON" 2>"${CONV_JSON}.err"
  CONV_RC=$?
  if [ "$CONV_RC" != 0 ]; then
    say "  ✗ convert rc=$CONV_RC"; tail -20 "${CONV_JSON}.err"; exit 4
  fi
  ART="$(python3 - "$CONV_JSON" <<'PY'
import json, sys
t = open(sys.argv[1], encoding="utf-8").read()
d = json.loads(t[t.find("{"):])
print((d.get("convert") or {}).get("artifact") or "")
PY
)"
  [ -z "$ART" ] || [ ! -f "$ART" ] && { say "  ✗ 解析不到产物路径 (见 $CONV_JSON)"; exit 4; }
  say "  ✓ 产物: $ART ($(stat -c%s "$ART") B)"
  say ""
  say "[3/5] 落盘 (★该路线只有 .rknn, 无 .weight ⇒ 板端走 toolkit-lite2 那套★) ..."
  mkdir -p "$LEGACY_DEST_DIR"
  DEST="$LEGACY_DEST_DIR/$(basename "$ART")"
  cp -p "$ART" "$DEST"
  [ -f "$ART.meta.json" ] && cp -p "$ART.meta.json" "$DEST.meta.json"
  SHA="$(sha "$DEST")"
  printf '%s  %s\n' "$SHA" "$(basename "$DEST")" > "$DEST.sha256"
  say "  ✓ $DEST"
  say "  ✓ sha256 = $SHA   (sidecar: $DEST.sha256)"
  say ""
  say "[4/5] 身份锚"
  say "  ✓ 本轮 sha256 = $SHA (已写 sidecar, 即刻的身份锚)"
  say "    ★历史参考 (同 2.3.2 首次转换): $LEGACY_BASELINE_SHA"
  say "    ★.rknn 非逐字节可复现 ⇒ 板端比对请用 sidecar, 不要用历史常量"
  say ""
  say "[5/5] ★路线代价 (必读) ★"
  say "  ★本路线产物在 RK3572 板端是否被接受 = [0数据]★"
  say "  (官方把 RK3572(librknn3_api_native.so) 与 RK3576(librknn3_api_rkcp.so) 分成两条 runtime)"
  say "  ⇒ 板端验证请走 ISS-250 的降级 A: bash SW/tools/rk3572_rknn3_board_smoke.sh (那是主路线那条)"
  hr
  say "次要路线① 完成 ⇒ 落盘目录: $LEGACY_DEST_DIR"
  hr
  exit 0
fi

# ── 主路线 (rknn3-toolkit 1.2.0 · target_platform=rk3572) ──────────────────────
say ""
say "[2/5] 准备 (切 head + 量化校准集) ..."
mkdir -p "$WORK_DIR" "$WORK_DIR/out"
CUT_ONNX="$WORK_DIR/$(basename "${ONNX_SRC%.onnx}")_heads.onnx"
if [ "$CUT_HEADS" = "1" ]; then
  if [ -f "$CUT_ONNX" ] && [ "$CUT_ONNX" -nt "$ONNX_SRC" ]; then
    say "  ✓ 切好的 head 模型在位 (缓存命中): $CUT_ONNX"
  else
    "$RKNN_PY_BIN" "$PROJ/SW/tools/cut_postprocessor.py" "$ONNX_SRC" "$CUT_ONNX" \
      --keep 350 498 646 2>&1 | sed 's/^/    /'
    [ -f "$CUT_ONNX" ] || { say "  ✗ 切 head 失败"; exit 4; }
  fi
  CONVERT_ONNX="$CUT_ONNX"
  VARIANT="heads"
else
  CONVERT_ONNX="$ONNX_SRC"
  VARIANT="full"
fi
say "  ✓ 待转 ONNX: $CONVERT_ONNX ($(stat -c%s "$CONVERT_ONNX") B)"

DATASET_TXT="$WORK_DIR/dataset.txt"
if [ -f "$DATASET_TXT" ] && [ "$DATASET_TXT" -nt "$CONVERT_ONNX" ]; then
  say "  ✓ 校准集清单在位 (缓存命中): $DATASET_TXT ($(wc -l < "$DATASET_TXT") 行)"
else
  CALIB_DIR="$CALIB_DIR" IMGSZ="$IMGSZ" WORK_DIR="$WORK_DIR" "$RKNN_PY_BIN" - <<'PY'
import os, sys
import cv2
import numpy as np

src_dir = os.environ["CALIB_DIR"]
imgsz = int(os.environ["IMGSZ"])
work = os.environ["WORK_DIR"]
if not os.path.isdir(src_dir):
    print("✗ 校准集源目录不存在: %s" % src_dir); sys.exit(3)
outdir = os.path.join(work, "calib")
os.makedirs(outdir, exist_ok=True)


def letterbox(img, new_size):
    h0, w0 = img.shape[:2]
    scale = min(new_size / h0, new_size / w0)
    new_h, new_w = int(h0 * scale), int(w0 * scale)
    r = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    px = (new_size - new_w) // 2
    py = (new_size - new_h) // 2
    canvas = np.zeros((new_size, new_size, 3), dtype=np.uint8)
    canvas[py:py + new_h, px:px + new_w] = r
    return canvas


files = sorted(f for f in os.listdir(src_dir) if f.lower().endswith(".jpg"))
lines = []
for fn in files:
    img = cv2.imread(os.path.join(src_dir, fn))
    if img is None:
        continue
    canvas = letterbox(img, imgsz)
    dst = os.path.join(outdir, os.path.splitext(fn)[0] + ".png")
    cv2.imwrite(dst, canvas)
    lines.append(dst)
if not lines:
    print("✗ 校准集源目录里的 jpg 全部读不出来: %s" % src_dir); sys.exit(3)
ds = os.path.join(work, "dataset.txt")
with open(ds, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("  ✓ 校准集: %d 张 → %s" % (len(lines), ds))
PY
  [ $? = 0 ] || exit 3
fi

say ""
say "[3/5] 转换 (★主路线★: $TOOLKIT_PKG $TOOLKIT_VER · target_platform=$TARGET_PLATFORM · w8a8 · channel) ..."
STEM="$(basename "${CONVERT_ONNX%.onnx}")"
OUT_RKNN="$WORK_DIR/out/${STEM}_${TARGET_PLATFORM}_int8_${VARIANT}.rknn"
rm -f "$OUT_RKNN" "${OUT_RKNN%.rknn}.weight"
CONV_LOG="$WORK_DIR/convert_${TARGET_PLATFORM}.log"
ONNX_IN="$CONVERT_ONNX" DS_TXT="$DATASET_TXT" OUT_RKNN="$OUT_RKNN" \
TARGET_PLATFORM="$TARGET_PLATFORM" "$RKNN_PY_BIN" - > "$CONV_LOG" 2>&1 <<'PY'
import json, os, time
from rknn.api import RKNN

onnx = os.environ["ONNX_IN"]
ds = os.environ["DS_TXT"]
out = os.environ["OUT_RKNN"]
target = os.environ["TARGET_PLATFORM"]
rec = {"target_platform": target, "onnx": onnx, "dataset": ds, "out": out}
t_all = time.time()
r = RKNN(verbose=True)
t0 = time.time()
rec["rc_config"] = int(r.config(target_platform=target,
                                quantized_dtype="w8a8",
                                quantized_algorithm="normal",
                                quantized_method="channel",
                                optimization_level=3,
                                mean_values=[[0, 0, 0]],
                                std_values=[[255, 255, 255]]))
rec["t_config"] = round(time.time() - t0, 3)
t0 = time.time()
rec["rc_load_onnx"] = int(r.load_onnx(onnx))
rec["t_load_onnx"] = round(time.time() - t0, 3)
t0 = time.time()
rec["rc_build"] = int(r.build(do_quantization=True, dataset=ds))
rec["t_build"] = round(time.time() - t0, 3)
t0 = time.time()
rec["rc_export"] = int(r.export_rknn(out))
rec["t_export"] = round(time.time() - t0, 3)
try:
    r.release()
except Exception:
    pass
rec["t_total"] = round(time.time() - t_all, 3)
weight = out[:-5] + ".weight" if out.endswith(".rknn") else out + ".weight"
rec["weight"] = weight
rec["weight_exists"] = os.path.exists(weight)
rec["bytes"] = os.path.getsize(out) if os.path.exists(out) else 0
rec["weight_bytes"] = os.path.getsize(weight) if os.path.exists(weight) else 0
print("ISS355_RKNN3_JSON " + json.dumps(rec, ensure_ascii=False))
ok = (rec.get("rc_config") == 0 and rec.get("rc_load_onnx") == 0
      and rec.get("rc_build") == 0 and rec.get("rc_export") == 0
      and rec.get("weight_exists"))
raise SystemExit(0 if ok else 1)
PY
CONV_RC=$?
tail -5 "$CONV_LOG" | sed 's/^/    /'
if [ "$CONV_RC" != 0 ]; then
  say "  ✗ 转换失败 rc=$CONV_RC (完整日志: $CONV_LOG)"
  exit 4
fi
say "  ✓ 产物: $OUT_RKNN ($(stat -c%s "$OUT_RKNN") B) + 同名 .weight ($(stat -c%s "${OUT_RKNN%.rknn}.weight") B)"

say ""
say "[4/5] 落盘到项目库 (★两件套一起拷, 缺 .weight 直接失败★) ..."
copy_two_piece "$OUT_RKNN" "$DEST_DIR"
COPY_RC=$?
if [ "$COPY_RC" != 0 ]; then
  say "  ✗ 两件套落盘失败 ⇒ 停止 (★不许只拷 .rknn 上板★)"
  exit 5
fi

say ""
say "[5/5] 身份锚 (sha256 sidecar · 两件套各一份) ..."
BASE="$(basename "${OUT_RKNN%.rknn}")"
say "  ★落地目录: $DEST_DIR"
say "  ★板端验证包 (ISS-250 降级 A · 板到手一条命令):"
say "    bash SW/tools/rk3572_rknn3_board_smoke.sh \\"
say "      --rknn $DEST_DIR/$BASE.rknn --weight $DEST_DIR/$BASE.weight \\"
say "      --expect-sha256 \"\$(cat $DEST_DIR/$BASE.rknn.sha256)\" \\"
say "      --expect-weight-sha256 \"\$(cat $DEST_DIR/$BASE.weight.sha256)\" \\"
say "      --power-note \"<供电方式>\" --out ./evidence/"

if [ "$WITH_ACC" = "1" ]; then
  say ""
  say "[可选] 复现 PC 侧精度基线 (acc 步 · 与板端同口径) ..."
  ACC_PY="$(find_py_for_pkg "$LEGACY_TOOLKIT_PKG_DEFAULT" "$LEGACY_TOOLKIT_VER_DEFAULT" || true)"
  if [ -z "$ACC_PY" ]; then
    say "  ! 本机没有带 $LEGACY_TOOLKIT_PKG_DEFAULT $LEGACY_TOOLKIT_VER_DEFAULT 的 python"
    say "    ⇒ acc 步的评测器 (rknn-toolkit-lite2) 侧缺依赖 ⇒ 本次跳过 (★不假装测过★)"
  else
    ACC_JSON="$WORK_DIR/acc.json"
    "$ACC_PY" "$PROJ/SW/tools/rknn_bench.py" acc --onnx "$ONNX_SRC" --images 300 --json > "$ACC_JSON" 2>&1
    ACC_RC=$?
    if [ "$ACC_RC" != 0 ]; then
      say "  ! acc 步 rc=$ACC_RC (详见 $ACC_JSON)"
    else
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
  fi
fi

hr
say "重建完成 ⇒ 落盘目录: $DEST_DIR   (下板前直接拷这两件, 不用碰临时目录)"
hr
exit 0
