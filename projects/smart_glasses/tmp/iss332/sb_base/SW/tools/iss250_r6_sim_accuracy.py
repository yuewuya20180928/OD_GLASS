#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-250 · 第 6 轮 (sw-lead 独立复核补充) —— ★板不可达时的「精度掉点」本机模拟器实测★

★为什么做这个★:
  ISS-250 前 5 轮的板端判据 N1~N5 里, 「精度掉点」一直写的是【板端测】⇒ 板不可达 ⇒ 该格永远 [0数据]。
  本轮实测发现: ★rknn-toolkit2 2.3.2 与 rknn3-toolkit 1.2.0 都自带【NPU 模拟器】★
  (init_runtime(target=None) => simulator; rknn3 另有 accuracy_analysis) ⇒ ★板不可达也能把
  「INT8 相对 FP32 的掉点」量出来★ (★是【同图同预处理的一致性代理】, 不是 mAP★)。

★为什么分 4 步 (★关键工程约束★)★:
  ★两套 toolkit 的 import 名【都叫 rknn】⇒ 同进程会互相覆盖 ⇒ 只能分进程跑, 靠 .npy 中转★。
  (★rknn3-toolkit 1.2.0 的包名就是 rknn, 与 toolkit2 2.3.2 同名——这正是 ISS-263 建独立 env 的原因★)

★步骤 (★每步单独一个 python 解释器★)★:
  MODE=ref   (env rknn3) onnxruntime CPU EP 跑源 ONNX (FP32)          ⇒ out/float.npy
  MODE=rknn3 (env rknn3) 载入 rk3572 产物 (.rknn+.weight) + 模拟器      ⇒ out/rknn3.npy
  MODE=tk2   (env rknn)  载入 rk3576 产物 (.rknn)     + 模拟器         ⇒ out/tk2.npy
  MODE=cmp   (env rknn3) 三路对比 + 检测级代理                        ⇒ out/sim_accuracy.json

★口径铁律 (SOUL.md)★:
  · 模拟器耗时 = CPU 模拟耗时, ★绝不可当板端 NPU 耗时报★
  · 任何一步失败 ⇒ 记失败原文, 不许静默跳过
"""
import os
import sys
import json
import time
import hashlib
import traceback

WORK = "/var/tmp/iss263_rknn3/work"
ONNX = os.path.join(WORK, "model_heads.onnx")
CALIB_DIR = os.path.join(WORK, "calib")
MODE = os.environ.get("R6_MODE", "cmp")
N_IMG = int(os.environ.get("R6_NIMG", "30"))
ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
ARCH = os.path.join(ROOT, "SW/artifacts/models")
RKNN3_DIR = os.path.join(ARCH, "rk3572_rknn3")
RKNN3_MODEL = os.path.join(RKNN3_DIR, "yolov5n-sim_heads_rk3572_int8_heads.rknn")
RKNN3_WEIGHT = os.path.join(RKNN3_DIR, "yolov5n-sim_heads_rk3572_int8_heads.weight")
TK2_MODEL = os.path.join(ARCH, "yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn")
OUTDIR = os.path.join(ROOT, "logs/iss250_r6")
OUT = os.path.join(OUTDIR, "sim_accuracy.json")
MODE_LOG = os.path.join(OUTDIR, "sim_accuracy_%s.log" % (os.environ.get("R6_TAG") or MODE))

log_lines = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    log_lines.append(s)


def banner(t):
    log("")
    log("=" * 78)
    log("### " + t)
    log("=" * 78)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def img_list():
    return sorted([f for f in os.listdir(CALIB_DIR) if f.endswith(".png")])[:N_IMG]


def load_rgb(fn):
    import cv2
    import numpy as np
    bgr = cv2.imread(os.path.join(CALIB_DIR, fn))
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return cv2.resize(rgb, (640, 640)), np


# ---------------- 指标 ----------------
ANCHORS = [(10, 13, 16, 30, 33, 23), (30, 61, 62, 45, 59, 119), (116, 90, 156, 198, 373, 326)]
STRIDES = [8, 16, 32]
CONF = 0.25


def stats(a, b):
    import numpy as np
    fa = np.asarray(a).reshape(-1).astype("float64")
    fb = np.asarray(b).reshape(-1).astype("float64")
    n = min(fa.size, fb.size)
    fa, fb = fa[:n], fb[:n]
    na = float(np.linalg.norm(fa))
    nb = float(np.linalg.norm(fb))
    cos = float(np.dot(fa, fb) / (na * nb)) if na > 0 and nb > 0 else float("nan")
    maxabs = float(np.max(np.abs(fa - fb))) if n else float("nan")
    rel = float(np.linalg.norm(fa - fb) / na) if na > 0 else float("nan")
    return {"cos": round(cos, 6), "max_abs_diff": round(maxabs, 6), "rel_l2": round(rel, 6),
            "n": int(n), "float_absmax": round(float(np.max(np.abs(fa))), 6),
            "int8_absmax": round(float(np.max(np.abs(fb))), 6)}


def decode(outs, conf=CONF, topk=100):
    import numpy as np
    boxes = []
    for oi, o in enumerate(outs):
        a = np.asarray(o)
        if a.ndim != 5:
            continue
        _, _, S, _, C = a.shape
        st = STRIDES[oi]
        anchor = ANCHORS[oi]
        pred = a[0].transpose(0, 2, 3, 1).reshape(3, S, S, C)
        for ai in range(3):
            p = pred[ai]
            obj = 1.0 / (1.0 + np.exp(-p[..., 4]))
            cls = 1.0 / (1.0 + np.exp(-p[..., 5:]))
            score = obj * cls.max(axis=-1)
            ys, xs = np.nonzero(score > conf)
            for y, x in zip(ys, xs):
                sc = float(score[y, x])
                cid = int(np.argmax(cls[y, x]))
                bx = (p[y, x, 0] * st ** 2 + x * st) / st
                by = (p[y, x, 1] * st ** 2 + y * st) / st
                bw = np.exp(p[y, x, 2]) * anchor[ai * 2] / st
                bh = np.exp(p[y, x, 3]) * anchor[ai * 2 + 1] / st
                boxes.append([bx - bw / 2, by - bh / 2, bw, bh, sc, cid])
    boxes.sort(key=lambda x: -x[4])
    return boxes[:topk]


def iou(a, b):
    ax1, ay1, aw, ah = a[0], a[1], a[2], a[3]
    bx1, by1, bw, bh = b[0], b[1], b[2], b[3]
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax1 + aw, bx1 + bw), min(ay1 + ah, by1 + bh)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    ua = aw * ah + bw * bh - inter
    return inter / ua if ua > 0 else 0.0


def det_stats(fb, ib):
    import numpy as np
    if not fb and not ib:
        return {"float_n": 0, "int8_n": 0, "matched": 0, "mean_iou": None,
                "float_only_missed": 0, "int8_only_spurious": 0}
    fb_s = sorted(fb, key=lambda x: -x[4])
    ib_s = sorted(ib, key=lambda x: -x[4])
    used, matched, ious = set(), 0, []
    for b in fb_s:
        best, bj = 0.0, None
        for j, c in enumerate(ib_s):
            if j in used:
                continue
            v = iou(b, c)
            if v > best:
                best, bj = v, j
        if bj is not None and best >= 0.5:
            used.add(bj)
            matched += 1
            ious.append(best)
    return {"float_n": len(fb_s), "int8_n": len(ib_s), "matched": matched,
            "mean_iou": round(float(np.mean(ious)), 6) if ious else None,
            "max_iou": round(float(np.max(ious)), 6) if ious else None,
            "float_only_missed": len(fb_s) - matched,
            "int8_only_spurious": len(ib_s) - len(used)}


# ---------------- 三个 producer ----------------
def mode_ref():
    import numpy as np
    import onnxruntime as ort
    banner("① FLOAT 参考 (onnxruntime CPU EP, env rknn3)")
    so = ort.SessionOptions()
    if hasattr(so, "log_severity_level"):
        so.log_severity_level = 3
    sess = ort.InferenceSession(ONNX, so, providers=["CPUExecutionProvider"])
    iname = sess.get_inputs()[0].name
    onames = [o.name for o in sess.get_outputs()]
    log("input =", iname, sess.get_inputs()[0].shape, sess.get_inputs()[0].type)
    log("outputs =", onames)
    imgs = img_list()
    log("样本 =", len(imgs), "张")
    outs = []
    t0 = time.time()
    for fn in imgs:
        u8, np_ = load_rgb(fn)
        x = u8.astype(np_.float32).transpose(2, 0, 1)[None] / 255.0
        outs.append(sess.run(None, {iname: x}))
    dt = time.time() - t0
    log("跑完 %d 张, 总 %.3f s, 单张 %.2f ms (★CPU EP★)" % (len(outs), dt, dt / max(1, len(outs)) * 1000))
    import pickle
    pickle.dump(outs, open(os.path.join(OUTDIR, "float.pkl"), "wb"))
    meta = {"n": len(outs), "total_s": round(dt, 3),
            "per_img_ms": round(dt / max(1, len(outs)) * 1000, 2),
            "onnx_md5": md5(ONNX), "outputs": onames,
            "input_preproc": "uint8 RGB -> resize(640,640) -> /255 -> NCHW float32"}
    json.dump(meta, open(os.path.join(OUTDIR, "float.json"), "w"), ensure_ascii=False, indent=2)
    log("落盘 float.pkl + float.json")


def mode_sim(env_tag, model, weight=None):
    import numpy as np
    from rknn.api import RKNN
    banner("② INT8 模拟器 · %s · %s" % (env_tag, os.path.basename(model)))
    import rknn.api
    ver = open(os.path.join(os.path.dirname(os.path.dirname(rknn.api.__file__)), "VERSION")).read().strip()
    log("toolkit =", ver)
    r = RKNN(verbose=False)
    t0 = time.time()
    rc_load = r.load_rknn(model, weight) if weight else r.load_rknn(model)
    log("load_rknn rc =", rc_load, " (%.3f s)" % (time.time() - t0))
    t0 = time.time()
    rc_init = r.init_runtime(target=None)       # ★None = simulator★
    log("init_runtime(target=None=simulator) rc =", rc_init, " (%.3f s)" % (time.time() - t0))
    if rc_init != 0:
        raise SystemExit("init_runtime rc=%s" % rc_init)
    imgs = img_list()
    outs = []
    t0 = time.time()
    for fn in imgs:
        u8, np_ = load_rgb(fn)
        outs.append(r.inference(inputs=[u8[None, ...]]))
    dt = time.time() - t0
    log("跑完 %d 张, 总 %.3f s, 单张 %.2f ms (★CPU 模拟, 不是板端 NPU★)" % (
        len(outs), dt, dt / max(1, len(outs)) * 1000))
    import pickle
    pickle.dump(outs, open(os.path.join(OUTDIR, "%s.pkl" % env_tag), "wb"))
    json.dump({"n": len(outs), "total_s": round(dt, 3),
               "per_img_ms": round(dt / max(1, len(outs)) * 1000, 2),
               "toolkit": ver, "model": model, "model_md5": md5(model),
               "weight": weight, "weight_md5": md5(weight) if weight else None,
               "load_rc": int(rc_load), "init_rc": int(rc_init),
               "note": "★耗时是 CPU 模拟器耗时, 不可当板端 NPU 耗时★"},
              open(os.path.join(OUTDIR, "%s.json" % env_tag), "w"), ensure_ascii=False, indent=2)
    log("落盘 %s.pkl + %s.json" % (env_tag, env_tag))


def mode_sim_build():
    """★实测发现 (2026-11-17 05:3x): 两套 toolkit 都【拒绝】对 load_rknn 载入的模型跑模拟器★
    官方报错原文: 'RKNN model that loaded by load_rknn not support inference on the simulator,
    please set target first! If you really want to inference on the simulator,
    use load_xxx & build instead of load_rknn!'
    ⇒ 模拟器只能吃【本会话 load_onnx + build 出来】的模型 ⇒ 这里重跑一次 build (~35 s) 再跑模拟器★"""
    import numpy as np
    from rknn.api import RKNN
    target = os.environ.get("R6_TARGET", "rk3572")
    dataset = os.path.join(WORK, "dataset.txt")
    banner("②' INT8 模拟器 (build 路径) · target_platform=%r" % target)
    import rknn.api
    ver = open(os.path.join(os.path.dirname(os.path.dirname(rknn.api.__file__)), "VERSION")).read().strip()
    log("toolkit =", ver, " target =", target)
    r = RKNN(verbose=False)
    t0 = time.time()
    kw = dict(target_platform=target,
              quantized_dtype="w8a8",
              quantized_algorithm="normal",
              quantized_method="channel",
              optimization_level=3,
              mean_values=[[0, 0, 0]],
              std_values=[[255, 255, 255]])
    lut = os.environ.get("R6_SIMULATE_LUT", "0") == "1"
    if lut:
        kw["simulate_lut"] = True      # ★rknn3 专有: 模拟器用 LUT 做激活, 更贴近 NPU 真实结果★
    try:
        rc_cfg = r.config(**kw)
    except TypeError as e:
        log("!! config 带 simulate_lut 被拒 (本 toolkit 无此参数):", repr(e))
        kw.pop("simulate_lut", None)
        rc_cfg = r.config(**kw)
    log("simulate_lut =", lut)
    log("config rc =", rc_cfg, " (%.3f s)" % (time.time() - t0))
    t0 = time.time()
    rc_load = r.load_onnx(ONNX)
    log("load_onnx rc =", rc_load, " (%.3f s)" % (time.time() - t0))
    t0 = time.time()
    rc_build = r.build(do_quantization=True, dataset=dataset)
    t_build = time.time() - t0
    log("build rc =", rc_build, " (%.3f s) ★与 ISS-263 的 33~41 s 同量级, 说明复现一致★" % t_build)
    if rc_build != 0:
        raise SystemExit("build rc=%s" % rc_build)
    t0 = time.time()
    rc_init = r.init_runtime(target=None)      # ★None = simulator★
    log("init_runtime(target=None=simulator) rc =", rc_init, " (%.3f s)" % (time.time() - t0))
    if rc_init != 0:
        raise SystemExit("init_runtime rc=%s" % rc_init)
    imgs = img_list()
    outs = []
    t0 = time.time()
    for fn in imgs:
        u8, np_ = load_rgb(fn)
        outs.append(r.inference(inputs=[u8[None, ...]]))
    dt = time.time() - t0
    log("跑完 %d 张, 总 %.3f s, 单张 %.2f ms (★CPU 模拟, 不是板端 NPU★)" % (
        len(outs), dt, dt / max(1, len(outs)) * 1000))
    tag = os.environ.get("R6_TAG", "rknn3")
    import pickle
    pickle.dump(outs, open(os.path.join(OUTDIR, "%s.pkl" % tag), "wb"))
    json.dump({"n": len(outs), "total_s": round(dt, 3),
               "per_img_ms": round(dt / max(1, len(outs)) * 1000, 2),
               "toolkit": ver, "target_platform": target,
               "build_s": round(t_build, 3), "config_rc": int(rc_cfg),
               "load_rc": int(rc_load), "build_rc": int(rc_build), "init_rc": int(rc_init),
               "source": "★build 路径 (load_onnx+build), 因为 load_rknn 不许跑模拟器★",
               "note": "★耗时是 CPU 模拟器耗时, 不可当板端 NPU 耗时★"},
              open(os.path.join(OUTDIR, "%s.json" % tag), "w"), ensure_ascii=False, indent=2)
    log("落盘 %s.pkl + %s.json" % (tag, tag))


def mode_cmp():
    import numpy as np
    banner("④ 三路对比 (float vs rknn3/rk3572-模拟 vs tk2/rk3576-模拟)")
    fmeta = json.load(open(os.path.join(OUTDIR, "float.json")))
    res = {"ts": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
           "n_img": fmeta["n"], "float": fmeta,
           "compare": {}, "detail": {}}

    def load(tag):
        import pickle
        p = os.path.join(OUTDIR, "%s.pkl" % tag)
        if not os.path.exists(p):
            return None
        return pickle.load(open(p, "rb"))

    fl = load("float")
    for tag, label in (("rknn3", "rknn3/rk3572"), ("rknn3_lut", "rknn3/rk3572+LUT"), ("tk2", "tk2/rk3576")):
        mp = os.path.join(OUTDIR, "%s.json" % tag)
        ints = load(tag)
        if ints is None or fl is None:
            res["compare"][tag] = {"status": "NO_DATA"}
            log("[%s] 无数据" % label)
            continue
        m = json.load(open(mp))
        res.setdefault("meta", {})[tag] = m
        n = min(len(fl), len(ints))
        per_head = []
        for h in range(3):
            cs, ms, rl = [], [], []
            for i in range(n):
                st = stats(fl[i][h], ints[i][h])
                cs.append(st["cos"])
                ms.append(st["max_abs_diff"])
                rl.append(st["rel_l2"])
            per_head.append({"head": h, "cos_mean": round(float(np.mean(cs)), 6),
                             "cos_min": round(float(np.min(cs)), 6),
                             "max_abs_diff_mean": round(float(np.mean(ms)), 6),
                             "rel_l2_mean": round(float(np.mean(rl)), 6)})
        det = []
        for i in range(n):
            det.append(det_stats(decode(fl[i]), decode(ints[i])))
        det_sweep = {}
        for c in (0.25, 0.5, 0.75):
            dd = []
            for i in range(n):
                dd.append(det_stats(decode(fl[i], conf=c), decode(ints[i], conf=c)))
            mi = [x["mean_iou"] for x in dd if x.get("mean_iou") is not None]
            det_sweep["conf_%.2f" % c] = {
                "float_boxes_per_img": round(float(np.mean([x["float_n"] for x in dd])), 3),
                "int8_boxes_per_img": round(float(np.mean([x["int8_n"] for x in dd])), 3),
                "matched_per_img": round(float(np.mean([x["matched"] for x in dd])), 3),
                "mean_iou_mean": round(float(np.mean(mi)), 6) if mi else None,
                "float_only_missed_per_img": round(float(np.mean([x["float_only_missed"] for x in dd])), 3),
                "int8_only_spurious_per_img": round(float(np.mean([x["int8_only_spurious"] for x in dd])), 3),
                "imgs_with_boxes": len(mi), "imgs_total": len(dd)}
        mious = [d["mean_iou"] for d in det if d.get("mean_iou") is not None]
        summ = {"label": label, "n": n, "per_head": per_head, "det_sweep": det_sweep,
                "det": {"float_boxes_per_img": round(float(np.mean([d["float_n"] for d in det])), 3),
                        "int8_boxes_per_img": round(float(np.mean([d["int8_n"] for d in det])), 3),
                        "matched_per_img": round(float(np.mean([d["matched"] for d in det])), 3),
                        "mean_iou_mean": round(float(np.mean(mious)), 6) if mious else None,
                        "imgs_with_boxes": len(mious), "imgs_total": len(det),
                        "float_only_missed_mean": round(float(np.mean([d["float_only_missed"] for d in det])), 3),
                        "int8_only_spurious_mean": round(float(np.mean([d["int8_only_spurious"] for d in det])), 3)}}
        res["compare"][tag] = summ
        res["detail"][tag] = det
        log("[%s] n=%d" % (label, n))
        for p in per_head:
            log("   head%d cos mean %.6f min %.6f | maxabs %.6f | relL2 %.6f" % (
                p["head"], p["cos_mean"], p["cos_min"], p["max_abs_diff_mean"], p["rel_l2_mean"]))
        log("   检测级: float %.2f 框/张, int8 %.2f 框/张, 匹配 %.2f/张, 平均IoU %s (%d/%d 张有框)" % (
            summ["det"]["float_boxes_per_img"], summ["det"]["int8_boxes_per_img"],
            summ["det"]["matched_per_img"], summ["det"]["mean_iou_mean"],
            summ["det"]["imgs_with_boxes"], summ["det"]["imgs_total"]))
        for ck, cv in sorted(summ["det_sweep"].items()):
            log("   %s : float %.2f 框/张 | int8 %.2f 框/张 | 匹配 %.2f/张 | 平均IoU %s | 漏 %.2f | 多 %.2f" % (
                ck, cv["float_boxes_per_img"], cv["int8_boxes_per_img"], cv["matched_per_img"],
                cv["mean_iou_mean"], cv["float_only_missed_per_img"], cv["int8_only_spurious_per_img"]))
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=2)
    log("落盘", OUT)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    banner("ISS-250 第6轮 · 模拟器掉点实测 · MODE=%s" % MODE)
    log("python =", sys.executable)
    log("ts =", time.strftime("%Y-%m-%d %H:%M:%S %Z"))
    try:
        if MODE == "ref":
            mode_ref()
        elif MODE == "rknn3":
            mode_sim("rknn3", RKNN3_MODEL, RKNN3_WEIGHT)
        elif MODE == "tk2":
            mode_sim("tk2", TK2_MODEL, None)
        elif MODE == "sim_build":
            mode_sim_build()
        elif MODE == "cmp":
            mode_cmp()
        else:
            raise SystemExit("unknown MODE=%s" % MODE)
    except Exception:
        log("!! 异常:")
        log(traceback.format_exc())
    with open(MODE_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))


if __name__ == "__main__":
    main()
