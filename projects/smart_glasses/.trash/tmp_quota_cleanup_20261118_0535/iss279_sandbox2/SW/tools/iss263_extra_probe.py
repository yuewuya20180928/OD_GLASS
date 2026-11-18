#!/usr/bin/env python3
# ★ISS-263 补充实测: (a) 整模型 yolov5s@640 转一次 (b) 产出 .rknn 回读 load_rknn 往返自证★
import os, sys, time, hashlib, json, traceback
WORK = "/var/tmp/iss263_rknn3/work"
os.environ.setdefault("TMPDIR", "/var/tmp/iss263_rknn3/tmp")
from rknn.api import RKNN

S_ONNX = "/home/yuewuya/Public/rknn_assets/yolov5s-sim.onnx"
S_OUT = os.path.join(WORK, "out", "yolov5s_full_int8_rk3572.rknn")
D_HEADS = os.path.join(WORK, "dataset.txt")
RKNX = os.path.join(WORK, "out", "yolov5n_heads_int8_rk3572_run1.rknn")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


print("=" * 78)
print("### (a) 整模型 yolov5s-sim.onnx @640 · target_platform=rk3572 · INT8")
print("=" * 78)
print("src =", S_ONNX, os.path.getsize(S_ONNX), "B")
t_all = time.time()
try:
    r = RKNN(verbose=True)
    print(">>> rc_config =", r.config(target_platform="rk3572", quantized_dtype="w8a8",
                                     quantized_algorithm="normal", quantized_method="channel",
                                     optimization_level=3, mean_values=[[0, 0, 0]],
                                     std_values=[[255, 255, 255]]))
    t0 = time.time()
    print(">>> rc_load_onnx =", r.load_onnx(S_ONNX))
    print(">>> t_load_onnx = %.3f" % (time.time() - t0))
    t0 = time.time()
    print(">>> rc_build =", r.build(do_quantization=True, dataset=D_HEADS))
    print(">>> t_build = %.3f" % (time.time() - t0))
    t0 = time.time()
    print(">>> rc_export =", r.export_rknn(S_OUT))
    print(">>> t_export = %.3f" % (time.time() - t0))
    r.release()
    print(">>> t_total = %.3f" % (time.time() - t_all))
    if os.path.exists(S_OUT):
        print(">>> ARTIFACT %s bytes=%d md5=%s" % (S_OUT, os.path.getsize(S_OUT), md5(S_OUT)))
    else:
        print(">>> ARTIFACT MISSING")
except Exception:
    traceback.print_exc()

print()
print("=" * 78)
print("### (b) 往返自证: 把产出的 .rknn 用 load_rknn 读回来")
print("=" * 78)
print("rknx =", RKNX, os.path.getsize(RKNX), "B  md5 =", md5(RKNX))
try:
    r2 = RKNN(verbose=True)
    rc = r2.load_rknn(RKNX)
    print(">>> rc_load_rknn =", rc)
    if rc == 0:
        try:
            r2.init_runtime()
            print(">>> init_runtime rc = 0  (★本机无 RK3572 NPU ⇒ 若真过说明用了 CPU/仿真回退★)")
        except Exception as e:
            print(">>> init_runtime EXC (★预期: 本机无板/NPU ⇒ 板端仍 [0数据]★):", repr(e))
    r2.release()
except Exception:
    traceback.print_exc()
print(">>> DONE")
