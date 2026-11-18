#!/usr/bin/env bash
# ==============================================================================
# rk3572_target_smoke.sh — ISS-207 · 板端一次性验证包
#   "rk3576-target 转出来的 .rknn, 能不能在 RK3572 板上跑通" ⇒ 一条命令出 PASS/FAIL
# ==============================================================================
# 上游: SW/RK3572_TARGET_BOARD_VERIFY.md (v1.0, 只读引用) · SW/RKNN_BENCH.md
# 本单: SW/RK3572_TARGET_COMPAT_V2.md (v2.0)
#
# ★ 本脚本干什么 (三段):
#   ① 前置条件 P1~P6 自动核对 (含 device-tree / librknnrt 版本 / 板端 lite2 /
#      产物 sha256 比对 / COCO 数据集)
#   ② 跑精度步 (acc) —— 与 PC 侧**同一口径** (逐类 IoU 贪心匹配, score_thr 0.3,
#      eval_iou 0.5), 再跑 NPU 耗时采样
#   ③ 按 5 条判据 (N1~N5) 输出 PASS/FAIL/INDET + 数值 + 失败原因 + JSON
#
# ★★ 铁律:
#   · **板端不许重转** —— 本脚本**没有任何** convert/build 路径, 只 load_rknn。
#     (P6 = 板端产物 sha256 必须等于 PC 侧基线 sha256, 否则测的不是同一个产物)
#   · **纯硬件耗时 vs SDK 总耗时分开报** (SOUL.md 铁律) —— 本脚本默认报
#     t_sdk_total (lite2 端到端 wall time); 纯 NPU 时间用 --npu-ms 传入
#     (来自 C API RKNN_QUERY_PERF_DETAIL), 没传就标 INDET, 不许混着报一个数。
#   · 本机无板 ⇒ --dry-run 只做本地能做的检查 + 打印板端将执行的命令, rc=0。
#
# 用法:
#   bash SW/tools/rk3572_target_smoke.sh --dry-run
#   scp SW/tools/rk3572_target_smoke.sh <board>:/tmp/ && ssh <board> \
#       'cd <proj> && bash SW/tools/rk3572_target_smoke.sh \
#          --artifact ./yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn \
#          --expect-sha256 1c5ff7ba... --images 300 --out ./evidence/ISS207_$(date +%Y%m%d)'
# ==============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="$(cd "$HERE/../.." && pwd)"

DRY=0
ARTIFACT=""
EXPECT_SHA=""
IMAGES=300
OUT=""
COCO_ROOT="${COCO_ROOT:-/work/object_detection/data/coco/raw}"
ONNX="${ONNX:-/home/yuewuya/Public/rknn_assets/yolov5n-sim.onnx}"
SCORE_THR=0.3
NMS_IOU=0.45
EVAL_IOU=0.5
IMGSZ=640
NPU_MS=""            # 纯 NPU 耗时 (ms), 由 C API RKNN_QUERY_PERF_DETAIL 取得后传入
POWER_NOTE=""        # 供电方式 (N5 需要)
INPUT_DTYPE="int8"   # 板端喂给 runtime 的输入 dtype (int8 = 本产物默认, 见 §4.2)
RETRIES=3

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)      DRY=1 ;;
    --artifact)     ARTIFACT="$2"; shift ;;
    --expect-sha256) EXPECT_SHA="$2"; shift ;;
    --images)       IMAGES="$2"; shift ;;
    --out)          OUT="$2"; shift ;;
    --coco-root)    COCO_ROOT="$2"; shift ;;
    --onnx)         ONNX="$2"; shift ;;
    --npu-ms)       NPU_MS="$2"; shift ;;
    --power-note)   POWER_NOTE="$2"; shift ;;
    --input-dtype)  INPUT_DTYPE="$2"; shift ;;
    --retries)      RETRIES="$2"; shift ;;
    -h|--help)      sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
  shift
done

# ---------------------------------------------------------------- 输出helpers
RES_NAME=(); RES_STATE=(); RES_DETAIL=()
record() { RES_NAME+=("$1"); RES_STATE+=("$2"); RES_DETAIL+=("$3"); }
hr() { printf '=%.0s' {1..78}; echo; }
say() { echo "$@"; }

# ---------------------------------------------------------------- 默认产物定位
if [ -z "$ARTIFACT" ]; then
  # 优先取项目库里已落盘的那个 (降级 B 的产物), 否则取本机默认
  for cand in "$PROJ"/SW/artifacts/models/*_rk3576_int8_heads.rknn; do
    [ -f "$cand" ] && ARTIFACT="$cand" && break
  done
fi
if [ -z "$ARTIFACT" ] && [ -f "/tmp/rknn_bench/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn" ]; then
  ARTIFACT="/tmp/rknn_bench/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn"
fi
if [ -z "$EXPECT_SHA" ] && [ -n "$ARTIFACT" ] && [ -f "$ARTIFACT.sha256" ]; then
  EXPECT_SHA="$(awk '{print $1}' "$ARTIFACT.sha256" | head -1)"
fi
if [ -z "$OUT" ]; then
  OUT="/tmp/iss207_smoke_$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p "$OUT"

hr; echo "ISS-207 · RK3572 目标兼容性板端验证包 (sw-lead, 2026-11-15)"; hr
say "产物      : ${ARTIFACT:-<未找到>}"
say "期望sha256: ${EXPECT_SHA:-<未指定>}"
say "COCO 根   : $COCO_ROOT"
say "输出目录  : $OUT"
say "模式      : $([ "$DRY" = 1 ] && echo 'DRY-RUN (本机无板)' || echo '板端实跑')"
hr

# =============================================================================
# --dry-run: 只做本地能做的检查 + 打印板端将执行的命令, rc=0
# =============================================================================
if [ "$DRY" = 1 ]; then
  say ""
  say "[本地检查 L1] 产物存在性"
  if [ -n "$ARTIFACT" ] && [ -f "$ARTIFACT" ]; then
    SHA="$(sha256sum "$ARTIFACT" | awk '{print $1}')"
    SZ="$(stat -c %s "$ARTIFACT" 2>/dev/null || echo '?')"
    say "  PASS  产物存在: $ARTIFACT"
    say "        大小 $SZ B | sha256 $SHA"
    if [ -n "$EXPECT_SHA" ]; then
      if [ "$SHA" = "$EXPECT_SHA" ]; then say "  PASS  sha256 == 基线 (与 PC 侧产物同一份)"
      else say "  FAIL  sha256 != 基线 (期望 $EXPECT_SHA)"; fi
    else
      say "  SKIP  未给 --expect-sha256 / 无 .sha256 sidecar ⇒ 不判 sha256"
    fi
  else
    say "  SKIP  本机没有 .rknn 产物 ⇒ 先跑 SW/tools/rk3572_model_rebuild.sh"
  fi

  say ""
  say "[本地检查 L2] 本机 PC 侧工具链 (板端用不到, 只是确认重建路径可用)"
  if python3 -c "import rknn.api" 2>/dev/null; then
    say "  PASS  当前 python3 有 rknn-toolkit2 (板端**不需要**它)"
  else
    say "  INFO  当前 python3 无 rknn-toolkit2 ⇒ 板端路径本就不依赖它 (板端只装 lite2)"
  fi

  say ""
  say "[本地检查 L3] 板端将执行的命令 (逐条 = 板端手敲也一样)"
  cat <<EOF
  # --- 前置条件 P1~P6 ---
  P1 cat /proc/device-tree/compatible | tr '\\0' ' '        # 必须含 rk3572
  P2 strings /usr/lib/librknnrt.so | grep -i 'librknnrt version'   # runtime 版本
  P3 python3 -c "import rknnlite, importlib.metadata as m; print(m.version('rknn-toolkit-lite2'))"
  P4 ls -l <artifact>.rknn && sha256sum <artifact>.rknn
  P5 ls $COCO_ROOT/val2017 | wc -l ; ls -l $COCO_ROOT/annotations/instances_val2017.json
  P6 sha256sum <artifact>.rknn | cut -d' ' -f1   # 必须 == PC 侧基线 sha256 (板端**不许重转**)
  # --- 判据 N1~N5 (由本脚本自动跑, 板端只需把命令跑完) ---
  N1 RKNNLite().load_rknn(<artifact>.rknn)  ret 必须 == 0   # 跨平台兼容命题本体
  N2 acc 步 F1 >= 0.2427                                   # PC 基线 0.2927 - 0.05
  N3 t_sdk_total(avg) <= 13.30 ms ; 或用 --npu-ms 传纯 NPU 时间
  N4 t_sdk_total 与 t_npu 分开报 (缺纯 NPU ⇒ INDET, 不许合并成一个数)
  N5 记录 thermal_zone0 温度 / cpufreq / 供电方式
EOF
  say ""
  say "[dry-run 结论] 本机无板 ⇒ 板端结论一律 [0数据]; 本次只验证了本包自身可执行。"
  say "  本机 rc=0 (dry-run 不判 PASS/FAIL, 只报 '能不能跑')"
  hr
  exit 0
fi

# =============================================================================
# 板端实跑
# =============================================================================
BAIL=""
fail_hard() { BAIL="$1"; record "$2" FAIL "$1"; }

# ---- P1 板子身份 -----------------------------------------------------------
COMPAT="$(cat /proc/device-tree/compatible 2>/dev/null | tr '\0' ' ')"
if [ -z "$COMPAT" ]; then
  fail_hard "读不到 /proc/device-tree/compatible (不是 Linux 板子? 没权限?)" "P1 板子身份"
elif echo "$COMPAT" | grep -q rk3572; then
  record "P1 板子身份(rk3572)" PASS "compatible=$COMPAT"
else
  fail_hard "compatible 不含 rk3572: $COMPAT  ⇒ 这不是 RK3572 板, N1 不构成跨平台证据" "P1 板子身份(rk3572)"
fi
say "uname -a: $(uname -a 2>/dev/null)"

# ---- P2 librknnrt 版本 -----------------------------------------------------
RT=""
for c in /usr/lib/librknnrt.so /usr/lib/aarch64-linux-gnu/librknnrt.so /usr/lib/librknnrt.so.0; do
  [ -f "$c" ] && RT="$c" && break
done
RTVER=""
if [ -n "$RT" ]; then
  RTVER="$(strings "$RT" 2>/dev/null | grep -iE "librknnrt version" | head -1)"
  [ -z "$RTVER" ] && RTVER="$(strings "$RT" 2>/dev/null | grep -oE "1\.[0-9]+\.[0-9]+" | head -1)"
fi
if [ -n "$RT" ]; then
  record "P2 librknnrt 版本" PASS "$RT | ${RTVER:-版本串未读到}"
else
  fail_hard "板端没有 librknnrt.so ⇒ 装不了 RKNN runtime" "P2 librknnrt 版本"
fi
say "librknnrt: ${RT:-无} ${RTVER}"

# ---- P3 板端 python + lite2 ------------------------------------------------
LITE_VER="$(python3 -c "
import importlib.metadata as m
try: print('rknn-toolkit-lite2', m.version('rknn-toolkit-lite2'))
except Exception: print('rknn-toolkit-lite2 metadata 缺失')
" 2>/dev/null)"
LITE_OK="$(python3 -c "import rknnlite; print('ok')" 2>/dev/null)"
if [ "$LITE_OK" = "ok" ]; then
  record "P3 板端 lite2" PASS "${LITE_VER:-rknnlite 可导入}"
else
  fail_hard "板端 import rknnlite 失败 ⇒ 装 rknn-toolkit-lite2" "P3 板端 lite2"
fi
say "lite2: ${LITE_VER:-不可导入}"

# ---- P4 产物在位 -----------------------------------------------------------
if [ -n "$ARTIFACT" ] && [ -f "$ARTIFACT" ]; then
  SZ="$(stat -c %s "$ARTIFACT")"
  SHA="$(sha256sum "$ARTIFACT" | awk '{print $1}')"
  record "P4 产物在位" PASS "$ARTIFACT | $SZ B"
else
  fail_hard "板上没有 .rknn 产物: ${ARTIFACT:-<未指定>}" "P4 产物在位"
  SHA=""
fi

# ---- P5 COCO 数据集 --------------------------------------------------------
VAL_DIR="$COCO_ROOT/val2017"
ANN="$COCO_ROOT/annotations/instances_val2017.json"
NIMG="$(ls "$VAL_DIR" 2>/dev/null | wc -l)"
if [ -d "$VAL_DIR" ] && [ -f "$ANN" ] && [ "$NIMG" -ge "$IMAGES" ]; then
  record "P5 COCO 数据集" PASS "val2017 $NIMG 张 (>= $IMAGES) | $ANN"
else
  fail_hard "COCO 数据不齐: val2017 $NIMG 张 (要 >= $IMAGES) | 标注 $ANN" "P5 COCO 数据集"
fi

# ---- P6 sha256 与 PC 侧基线一致 (**板端不许重转**) -------------------------
if [ -n "$SHA" ] && [ -n "$EXPECT_SHA" ]; then
  if [ "$SHA" = "$EXPECT_SHA" ]; then
    record "P6 产物同一性(sha256)" PASS "sha256=$SHA == PC 侧基线 (板端未重转)"
  else
    fail_hard "sha256 不匹配: 板端 $SHA != PC 基线 $EXPECT_SHA ⇒ 测的不是同一个产物" "P6 产物同一性(sha256)"
  fi
else
  record "P6 产物同一性(sha256)" INDET "缺期望 sha256 (--expect-sha256 / <artifact>.sha256) ⇒ 不判"
fi

# =============================================================================
# 板端 acc 步 (精度 + 耗时) —— 嵌入式 lite2 评测器, 与 PC 侧同口径
# =============================================================================
ACC_PY="$OUT/board_acc.py"
cat > "$ACC_PY" <<'PYEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-207 板端 acc 步 (rknn-toolkit-lite2) —— 口径与 SW/tools/rknn_bench.py 一致:
   逐类 IoU 贪心匹配 (eval_iou) + score_thr + NMS, 同一套 COCO 前 N 张。
   ★ 只 load_rknn, **不做任何转换** (板端不许重转)。
   解码参数 (grid / anchor) 与 rknn_bench.decode_raw_heads 同源:
     grid[y][x] = [x, y]      anchor = yolov5 标准锚框 (本机已对 ONNX initializer 逐位核对)
"""
import argparse, json, os, sys, time, collections
import numpy as np
from rknnlite.api import RKNNLite

ANCHORS = {8:  np.array([[10, 13], [16, 30], [33, 23]]),
           16: np.array([[30, 61], [62, 45], [59, 119]]),
           32: np.array([[116, 90], [156, 198], [373, 326]])}

def letterbox(img, size):
    import cv2
    h0, w0 = img.shape[:2]
    scale = min(size / h0, size / w0)
    nh, nw = int(h0 * scale), int(w0 * scale)
    r = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
    px, py = (size - nw) // 2, (size - nh) // 2
    canvas = np.zeros((size, size, 3), dtype=np.uint8)
    canvas[py:py + nh, px:px + nw] = r
    return canvas, scale, px, py

def nms(boxes, scores, iou_thr):
    if len(boxes) == 0:
        return []
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]; keep.append(int(i))
        if order.size == 1:
            break
        xx1 = np.maximum(x1[i], x1[order[1:]]); yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]]); yy2 = np.minimum(y2[i], y2[order[1:]])
        inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
        iou = inter / (areas[i] + areas[order[1:]] - inter + 1e-9)
        order = order[1:][iou < iou_thr]
    return keep

def decode(outs, ga, conf_thr, iou_thr, max_det, scale, px, py, H, W):
    all_b, all_s, all_c = [], [], []
    for stride, head in ((8, ga['h80']), (16, ga['h40']), (32, ga['h20'])):
        if head is None:
            continue
        head = head[0]
        grid = ga['grid'][stride]; anch = ga['anchor'][stride]
        for a in range(head.shape[0]):
            r = head[a]
            s = 1.0 / (1.0 + np.exp(-r[..., 0:4]))
            cx = (s[..., 0] * 2 - 0.5 + grid[a, ..., 0]) * stride
            cy = (s[..., 1] * 2 - 0.5 + grid[a, ..., 1]) * stride
            bw = (s[..., 2] * 2) ** 2 * anch[a, ..., 0]
            bh = (s[..., 3] * 2) ** 2 * anch[a, ..., 1]
            obj = 1.0 / (1.0 + np.exp(-r[..., 4]))
            cls = 1.0 / (1.0 + np.exp(-r[..., 5:]))
            score = obj * cls.max(-1)
            mask = score > conf_thr
            if not mask.any():
                continue
            xywh = np.stack([cx, cy, bw, bh], -1)[mask]
            b = xywh.copy()
            b[:, [0, 2]] = b[:, [0, 2]] - b[:, [2, 3]] / 2
            b[:, [1, 3]] = b[:, [1, 3]] - b[:, [2, 3]] / 2
            b[:, [0, 2]] = b[:, [0, 2]] + b[:, [2, 3]] / 2
            b[:, [1, 3]] = b[:, [1, 3]] + b[:, [2, 3]] / 2
            all_b.append(b); all_s.append(score[mask]); all_c.append(cls[mask].argmax(1))
    if not all_b:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0, dtype=int)
    boxes = np.concatenate(all_b); scores = np.concatenate(all_s); classes = np.concatenate(all_c).astype(int)
    boxes[:, [0, 2]] = (boxes[:, [0, 2]] - px) / scale
    boxes[:, [1, 3]] = (boxes[:, [1, 3]] - py) / scale
    boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, W)
    boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, H)
    fb, fs, fc = [], [], []
    for c in np.unique(classes):
        idx = np.where(classes == c)[0]
        keep = nms(boxes[idx], scores[idx], iou_thr)
        for k in idx[keep][:max_det]:
            fb.append(boxes[k]); fs.append(scores[k]); fc.append(c)
    if not fb:
        return np.zeros((0, 4)), np.zeros(0), np.zeros(0, dtype=int)
    return np.array(fb), np.array(fs), np.array(fc, dtype=int)

def iou_xyxy(b1, b2):
    ix = max(0.0, min(b1[2], b2[2]) - max(b1[0], b2[0]))
    iy = max(0.0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
    inter = ix * iy
    ua = ((b1[2] - b1[0]) * (b1[3] - b1[1]) + (b2[2] - b2[0]) * (b2[3] - b2[1]) - inter)
    return inter / ua if ua > 0 else 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rknn", required=True)
    ap.add_argument("--coco-root", required=True)
    ap.add_argument("--images", type=int, default=300)
    ap.add_argument("--score-thr", type=float, default=0.3)
    ap.add_argument("--nms-iou", type=float, default=0.45)
    ap.add_argument("--eval-iou", type=float, default=0.5)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--input-dtype", default="int8", choices=["int8", "float32"])
    ap.add_argument("--out-json", required=True)
    a = ap.parse_args()

    import cv2
    val_dir = os.path.join(a.coco_root, "val2017")
    ann_path = os.path.join(a.coco_root, "annotations", "instances_val2017.json")

    # ---- N1 加载探针 (跨平台兼容命题本体) --------------------------------
    m = RKNNLite()
    ret_load = m.load_rknn(a.rknn)
    res = {"rknn": a.rknn, "load_rknn_ret": int(ret_load), "input_dtype": a.input_dtype}
    if ret_load != 0:
        res["ok"] = False
        res["stage"] = "load_rknn"
        res["error"] = "load_rknn ret=%s" % ret_load
        json.dump(res, open(a.out_json, "w"), ensure_ascii=False, indent=2)
        print("[acc] load_rknn 失败 ret=%s" % ret_load); return 3
    ret_init = m.init_runtime()
    res["init_runtime_ret"] = int(ret_init)
    if ret_init != 0:
        res["ok"] = False; res["stage"] = "init_runtime"
        res["error"] = "init_runtime ret=%s" % ret_init
        json.dump(res, open(a.out_json, "w"), ensure_ascii=False, indent=2)
        print("[acc] init_runtime 失败 ret=%s" % ret_init); return 3

    # ---- 解码参数 (grid/anchor) --------------------------------------------
    ga = {"grid": {}, "anchor": {}}
    for stride, g in ((8, a.imgsz // 8), (16, a.imgsz // 16), (32, a.imgsz // 32)):
        xx, yy = np.meshgrid(np.arange(g), np.arange(g))
        ga["grid"][stride] = np.stack([xx, yy], -1).astype(np.float32)[None]
        ga["anchor"][stride] = np.repeat(ANCHORS[stride][None, :, None, None, :], g, axis=2).astype(np.float32)

    ann = json.load(open(ann_path, encoding="utf-8"))
    gt = collections.defaultdict(list)
    for x in ann["annotations"]:
        bx, by, bw, bh = x["bbox"]
        gt[x["image_id"]].append((x["category_id"], bx, by, bw, bh))

    files = sorted(os.listdir(val_dir))[: a.images]
    preds = {}
    t_sdk = []
    n_img = 0
    for fn in files:
        iid = int(fn.split(".")[0])
        if not gt.get(iid):
            continue
        img = cv2.imread(os.path.join(val_dir, fn))
        if img is None:
            continue
        H, W = img.shape[:2]
        canvas, scale, px, py = letterbox(img, a.imgsz)
        rgb = canvas[..., ::-1]
        f = np.ascontiguousarray(rgb.transpose(2, 0, 1)).astype(np.float32) / 255.0
        if a.input_dtype == "int8":
            # ★ 本产物 build 时 mean=0/std=255 ⇒ runtime 输入是 int8: q = round(x01 * 127)
            blob = np.expand_dims(np.round(f * 127.0).astype(np.int8), 0)
        else:
            blob = np.expand_dims(f, 0)
        t0 = time.perf_counter()
        outs = m.inference(inputs=[blob], data_format="nchw")
        t_sdk.append((time.perf_counter() - t0) * 1000.0)
        outs = list(outs)
        by_shape = {}
        for o in outs:
            sh = np.asarray(o).shape
            if len(sh) == 5:
                by_shape[sh[2]] = np.asarray(o)
        ga2 = {"grid": ga["grid"], "anchor": ga["anchor"],
               "h80": by_shape.get(a.imgsz // 8), "h40": by_shape.get(a.imgsz // 16),
               "h20": by_shape.get(a.imgsz // 32)}
        b, s, c = decode(outs, ga2, a.score_thr, a.nms_iou, 100, scale, px, py, H, W)
        n_img += 1
        if len(s):
            preds[iid] = (b, s, c)
    m.release()

    tp = collections.defaultdict(int); fp = collections.defaultdict(int); fn_ = collections.defaultdict(int)
    for iid, (boxes, scores, classes) in preds.items():
        g = gt.get(iid, [])
        used = set()
        for k in range(len(scores)):
            c = int(classes[k]); best, bi = -1.0, -1
            for j, (gc, gx, gy, gw, gh) in enumerate(g):
                if gc - 1 != c or j in used:
                    continue
                v = iou_xyxy(boxes[k], (gx, gy, gx + gw, gy + gh))
                if v > best:
                    best, bi = v, j
            if best >= a.eval_iou:
                used.add(bi); tp[c] += 1
            else:
                fp[c] += 1
        for j, (gc, *_r) in enumerate(g):
            if j not in used:
                fn_[gc - 1] += 1
    A, B, C = sum(tp.values()), sum(fp.values()), sum(fn_.values())
    P = A / max(1, A + B); R = A / max(1, A + C); F1 = 2 * A / max(1, 2 * A + B + C)
    ts = sorted(t_sdk)
    res.update({
        "ok": True,
        "tp": A, "fp": B, "fn": C,
        "precision": P, "recall": R, "f1": F1,
        "n_images": n_img, "images_requested": a.images,
        "score_thr": a.score_thr, "nms_iou": a.nms_iou, "eval_iou": a.eval_iou,
        "caliber": "逐类 IoU 贪心匹配 (同 SW/tools/rknn_bench.py acc 步) —— 非官方 mAP",
        "t_sdk_total_ms": {"min": round(ts[0], 2) if ts else None,
                           "avg": round(sum(ts) / len(ts), 2) if ts else None,
                           "max": round(ts[-1], 2) if ts else None,
                           "p90": round(ts[int(len(ts) * 0.9)], 2) if ts else None,
                           "n": len(ts)},
        "evidence": "[实测] 板端 rknn-toolkit-lite2 实跑 (load_rknn + init_runtime + 逐帧推理)",
    })
    json.dump(res, open(a.out_json, "w"), ensure_ascii=False, indent=2)
    print("[acc] n_images=%d TP=%d FP=%d FN=%d P=%.4f R=%.4f F1=%.4f" % (n_img, A, B, C, P, R, F1))
    if ts:
        print("[acc] t_sdk_total ms: avg=%.2f min=%.2f max=%.2f (n=%d)" %
              (sum(ts) / len(ts), ts[0], ts[-1], len(ts)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
PYEOF

say ""
say "[acc 步] 起板端评测器 (lite2, 只 load_rknn, 不重转) ..."
ACC_JSON="$OUT/acc.json"
ACC_RC=0
for try in $(seq 1 "$RETRIES"); do
  python3 "$ACC_PY" --rknn "$ARTIFACT" --coco-root "$COCO_ROOT" --images "$IMAGES" \
      --score-thr "$SCORE_THR" --nms-iou "$NMS_IOU" --eval-iou "$EVAL_IOU" \
      --imgsz "$IMGSZ" --input-dtype "$INPUT_DTYPE" --out-json "$ACC_JSON" 2>&1 | tee "$OUT/acc.log"
  ACC_RC=${PIPESTATUS[0]}
  [ "$ACC_RC" = 0 ] && break
  say "  (第 $try 次 acc 步 rc=$ACC_RC ⇒ 重试; 若反复失败见 $OUT/acc.log)"
  sleep 2
done

# =============================================================================
# 5 条判据 → PASS/FAIL/INDET
# =============================================================================
say ""
hr; echo "判据判定 (N1~N5)"; hr

ACC_F1=""; ACC_N=""; LOAD_RET=""; INIT_RET=""; TSDK_AVG=""; TSDK_MIN=""; TSDK_MAX=""
if [ -f "$ACC_JSON" ]; then
  ACC_F1="$(python3 -c "import json;print(json.load(open('$ACC_JSON')).get('f1',''))" 2>/dev/null)"
  ACC_N="$(python3 -c "import json;print(json.load(open('$ACC_JSON')).get('n_images',''))" 2>/dev/null)"
  LOAD_RET="$(python3 -c "import json;print(json.load(open('$ACC_JSON')).get('load_rknn_ret',''))" 2>/dev/null)"
  INIT_RET="$(python3 -c "import json;print(json.load(open('$ACC_JSON')).get('init_runtime_ret',''))" 2>/dev/null)"
  TSDK_AVG="$(python3 -c "import json;d=json.load(open('$ACC_JSON')).get('t_sdk_total_ms') or {};print(d.get('avg',''))" 2>/dev/null)"
  TSDK_MIN="$(python3 -c "import json;d=json.load(open('$ACC_JSON')).get('t_sdk_total_ms') or {};print(d.get('min',''))" 2>/dev/null)"
  TSDK_MAX="$(python3 -c "import json;d=json.load(open('$ACC_JSON')).get('t_sdk_total_ms') or {};print(d.get('max',''))" 2>/dev/null)"
fi

# N1 能加载 (跨平台兼容命题本体)
if [ "$LOAD_RET" = "0" ] && [ "$INIT_RET" = "0" ]; then
  record "N1 能加载(load_rknn+init_runtime)" PASS "load_rknn=0 init_runtime=0 ⇒ RK3572 runtime 接受 rk3576-target 产物"
elif [ -n "$LOAD_RET" ]; then
  fail_hard "load_rknn ret=$LOAD_RET init_runtime=$INIT_RET ⇒ ★跨平台兼容命题被否* (详见 $OUT/acc.log 的错误串)" "N1 能加载(load_rknn+init_runtime)"
else
  record "N1 能加载(load_rknn+init_runtime)" INDET "acc 步没跑起来 ⇒ N1 无数据"
fi

# N2 精度不塌 (PC 基线 F1=0.2927 ⇒ 通过线 0.2427)
F1_MIN=0.2427
if [ -n "$ACC_F1" ]; then
  OKF1="$(python3 -c "print(1 if float('$ACC_F1') >= $F1_MIN else 0)")"
  if [ "$OKF1" = "1" ]; then
    record "N2 精度不塌" PASS "F1=$ACC_F1 (>= $F1_MIN) | n=$ACC_N 张 | PC 基线 0.2927"
  else
    record "N2 精度不塌" FAIL "F1=$ACC_F1 < $F1_MIN (PC 基线 0.2927) ⇒ 掉 $ACC_F1 ⇒ 量化在不同 NPU 实现上有偏"
  fi
else
  record "N2 精度不塌" INDET "无 F1 数据 (acc 步没跑成)"
fi

# N3 NPU 耗时对得上 (t_npu <= 13.30ms [推算]; t_sdk_total <= 13.30 ⇒ 必然 PASS)
T_NPU_TH=13.30
T_T2=20.33
if [ -n "$NPU_MS" ]; then
  OKT="$(python3 -c "print(1 if float('$NPU_MS') <= $T_NPU_TH else 0)")"
  if [ "$OKT" = "1" ]; then
    record "N3 NPU 耗时对得上" PASS "t_npu=$NPU_MS ms <= $T_NPU_TH ms (纯 NPU, C API perf detail)"
  else
    record "N3 NPU 耗时对得上" FAIL "t_npu=$NPU_MS ms > $T_NPU_TH ms ⇒ $(python3 -c "print('★命中 T2 翻案条件 (60ms 不保)' if float('$NPU_MS') > $T_T2 else '未过 13.30 但未过 20.33')")"
  fi
elif [ -n "$TSDK_AVG" ]; then
  OKS="$(python3 -c "print(1 if float('$TSDK_AVG') <= $T_NPU_TH else 0)")"
  if [ "$OKS" = "1" ]; then
    record "N3 NPU 耗时对得上" PASS "t_sdk_total avg=$TSDK_AVG ms <= $T_NPU_TH ⇒ t_npu 必然 <= $T_NPU_TH (t_npu <= t_sdk_total)"
  else
    record "N3 NPU 耗时对得上" INDET "t_sdk_total avg=$TSDK_AVG ms > $T_NPU_TH ⇒ ★不能据此判 FAIL* (SDK 总耗时含搬运/反量化); 需 C API RKNN_QUERY_PERF_DETAIL 取纯 NPU 时间后 --npu-ms 传入"
  fi
else
  record "N3 NPU 耗时对得上" INDET "无耗时数据"
fi

# N4 两个数都报且分开
if [ -n "$NPU_MS" ] && [ -n "$TSDK_AVG" ]; then
  record "N4 纯硬件/SDK 总耗时分开报" PASS "t_npu=$NPU_MS ms | t_sdk_total avg=$TSDK_AVG ms (min=$TSDK_MIN max=$TSDK_MAX)"
elif [ -n "$TSDK_AVG" ]; then
  record "N4 纯硬件/SDK 总耗时分开报" INDET "只拿到 t_sdk_total avg=$TSDK_AVG ms (min=$TSDK_MIN max=$TSDK_MAX); 纯 NPU 未取 ⇒ 未满足'两个数都报'"
else
  record "N4 纯硬件/SDK 总耗时分开报" FAIL "没有耗时数据"
fi

# N5 散热/供电条件已记录
TEMP="$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null)"
FREQ="$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null)"
RKNPU_LOAD=""
for f in /sys/kernel/debug/rknpu/load /sys/kernel/debug/rknn/load; do
  [ -r "$f" ] && RKNPU_LOAD="$(cat "$f" 2>/dev/null | head -1)" && break
done
if [ -n "$TEMP" ] || [ -n "$FREQ" ] || [ -n "$POWER_NOTE" ]; then
  record "N5 散热/供电已记录" PASS "temp=${TEMP:-未读} (mC) | cpu0=${FREQ:-未读} kHz | power=${POWER_NOTE:-未记} | rknpu_load=${RKNPU_LOAD:-n/a}"
else
  record "N5 散热/供电已记录" FAIL "温度/频率/供电方式都没记 ⇒ N3 的数没有可比性"
fi

# ---------------------------------------------------------------- 汇总
hr; echo "汇总"; hr
NP=0; NF=0; NI=0
for i in "${!RES_NAME[@]}"; do
  printf '%-34s %-6s %s\n' "${RES_NAME[$i]}" "${RES_STATE[$i]}" "${RES_DETAIL[$i]}"
  case "${RES_STATE[$i]}" in PASS) NP=$((NP+1));; FAIL) NF=$((NF+1));; INDET) NI=$((NI+1));; esac
done
hr
echo "PASS=$NP FAIL=$NF INDET=$NI | 硬失败: ${BAIL:-无}"

# 把结果写成 JSON (用 python 拼, 避免 shell 转义地狱)
{
  printf '{\n  "pkg": "rk3572_target_smoke.sh",\n  "artifact": %s,\n' "$(python3 -c "import json,sys;print(json.dumps(sys.argv[1]))" "${ARTIFACT:-}")"
  printf '  "pass": %s, "fail": %s, "indet": %s,\n' "$NP" "$NF" "$NI"
  printf '  "acc": %s,\n' "$(python3 -c "
import json,os
p=os.path.join('$OUT','acc.json')
print(json.dumps(json.load(open(p)),ensure_ascii=False) if os.path.exists(p) else '{}')")"
  printf '  "checks": [\n'
  first=1
  for i in "${!RES_NAME[@]}"; do
    [ $first = 1 ] || printf ',\n'; first=0
    printf '    {"name": %s, "state": %s, "detail": %s}' \
      "$(python3 -c "import json,sys;print(json.dumps(sys.argv[1],ensure_ascii=False))" "${RES_NAME[$i]}")" \
      "$(python3 -c "import json,sys;print(json.dumps(sys.argv[1]))" "${RES_STATE[$i]}")" \
      "$(python3 -c "import json,sys;print(json.dumps(sys.argv[1],ensure_ascii=False))" "${RES_DETAIL[$i]}")"
  done
  printf '\n  ]\n}\n'
} > "$OUT/summary.json"

say ""
say "证据文件: $OUT/summary.json · $OUT/acc.json · $OUT/acc.log"
say "口径: 精度 = 逐类 IoU 贪心匹配 (同 PC 侧 acc 步); 耗时 = t_sdk_total (lite2 wall) 与 t_npu 分开报"
if [ "$NF" -gt 0 ]; then
  say "★结论: 有 $NF 条硬失败 ⇒ 见上面 FAIL 行的原因"
  exit 1
fi
if [ "$NI" -gt 0 ]; then
  say "★结论: 无硬失败, 但有 $NI 条 INDET ⇒ 证据不足以判通过, 补齐对应数据后重跑"
  exit 1
fi
say "★结论: N1~N5 全过 ⇒ rk3576-target 产物在 RK3572 上成立"
exit 0
