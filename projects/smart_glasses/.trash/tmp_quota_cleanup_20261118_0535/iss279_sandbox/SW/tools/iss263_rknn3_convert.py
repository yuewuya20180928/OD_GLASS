#!/usr/bin/env python3
# ★ISS-263 · rknn3-toolkit 1.2.0 · target_platform='rk3572' · INT8 真转 3 次 + 耗时 + 产物 md5/字节数★
# ★纪律: 每一步的 rc + 原文都落盘, 不许含糊★
import os, sys, time, hashlib, json, traceback

WORK = "/var/tmp/iss263_rknn3/work"
ONNX = os.path.join(WORK, "model_heads.onnx")
DATASET = os.path.join(WORK, "dataset.txt")
OUTDIR = os.path.join(WORK, "out")
TARGET = os.environ.get("ISS263_TARGET", "rk3572")
N = int(os.environ.get("ISS263_RUNS", "3"))
os.makedirs(OUTDIR, exist_ok=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def banner(t):
    print("\n" + "=" * 78)
    print("### %s" % t)
    print("=" * 78)


banner("ENV")
print("target_platform = %r" % TARGET)
print("onnx            = %s (%d B)" % (ONNX, os.path.getsize(ONNX)))
print("dataset         = %s (%d 行)" % (DATASET, sum(1 for _ in open(DATASET))))
print("python          =", sys.executable)

from rknn.api import RKNN
import rknn.api
print("toolkit         =", open(os.path.join(os.path.dirname(os.path.dirname(rknn.api.__file__)), "VERSION")).read().strip())

results = []
for i in range(1, N + 1):
    out = os.path.join(OUTDIR, "yolov5n_heads_int8_%s_run%d.rknn" % (TARGET, i))
    banner("RUN %d/%d  (target_platform=%s)" % (i, N, TARGET))
    rec = {"run": i, "target_platform": TARGET, "out": out}
    t_all = time.time()
    t0 = time.time()
    try:
        r = RKNN(verbose=True)
        rc_cfg = r.config(target_platform=TARGET,
                          quantized_dtype="w8a8",
                          quantized_algorithm="normal",
                          quantized_method="channel",
                          optimization_level=3,
                          mean_values=[[0, 0, 0]],
                          std_values=[[255, 255, 255]])
        rec["rc_config"] = int(rc_cfg)
        print(">>> rc_config =", rc_cfg)
    except Exception as e:
        rec["rc_config"] = "EXC"
        print(">>> CONFIG EXC:", repr(e))
        traceback.print_exc()
        results.append(rec)
        break
    rec["t_config"] = round(time.time() - t0, 3)

    t0 = time.time()
    try:
        rc_load = r.load_onnx(ONNX)
        rec["rc_load_onnx"] = int(rc_load)
        print(">>> rc_load_onnx =", rc_load)
    except Exception as e:
        rec["rc_load_onnx"] = "EXC"
        print(">>> LOAD EXC:", repr(e))
        traceback.print_exc()
        results.append(rec)
        break
    rec["t_load_onnx"] = round(time.time() - t0, 3)

    t0 = time.time()
    try:
        rc_build = r.build(do_quantization=True, dataset=DATASET)
        rec["rc_build"] = int(rc_build)
        print(">>> rc_build =", rc_build)
    except Exception as e:
        rec["rc_build"] = "EXC"
        print(">>> BUILD EXC:", repr(e))
        traceback.print_exc()
        results.append(rec)
        break
    rec["t_build"] = round(time.time() - t0, 3)

    t0 = time.time()
    try:
        rc_exp = r.export_rknn(out)
        rec["rc_export"] = int(rc_exp)
        print(">>> rc_export =", rc_exp)
    except Exception as e:
        rec["rc_export"] = "EXC"
        print(">>> EXPORT EXC:", repr(e))
        traceback.print_exc()
        results.append(rec)
        break
    rec["t_export"] = round(time.time() - t0, 3)

    try:
        r.release()
    except Exception:
        pass

    rec["t_total"] = round(time.time() - t_all, 3)
    if os.path.exists(out):
        rec["bytes"] = os.path.getsize(out)
        rec["md5"] = md5(out)
        print(">>> ARTIFACT %s  bytes=%d  md5=%s" % (out, rec["bytes"], rec["md5"]))
    else:
        rec["bytes"] = None
        rec["md5"] = None
        print(">>> ARTIFACT MISSING:", out)
    results.append(rec)

banner("SUMMARY json")
print(json.dumps(results, ensure_ascii=False, indent=2))
ok = [r for r in results if r.get("rc_build") == 0 and r.get("rc_export") == 0 and r.get("md5")]
if ok:
    ts = [r["t_total"] for r in ok]
    print("\n>>> CONVERT_TOTAL_S min=%.3f avg=%.3f max=%.3f  (target_platform=%s, n=%d)"
          % (min(ts), sum(ts) / len(ts), max(ts), TARGET, len(ts)))
    for r in ok:
        print(">>> RUN%d bytes=%d md5=%s t_total=%.3f (cfg=%.3f load=%.3f build=%.3f export=%.3f)"
              % (r["run"], r["bytes"], r["md5"], r["t_total"], r["t_config"], r["t_load_onnx"], r["t_build"], r["t_export"]))
else:
    print("\n>>> NO SUCCESSFUL CONVERSION")
with open(os.path.join(WORK, "results_%s.json" % TARGET), "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(">>> results json ->", os.path.join(WORK, "results_%s.json" % TARGET))
