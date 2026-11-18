#!/usr/bin/env python3
# ★ISS-263 第2趟 · 往返自证 (authoritative)★
# 真签名 (inspect 实测): load_rknn(self, model_path, weight_path, lora_weight_path=None, load_ctx=False, **kwargs)
#                     init_runtime(self, target=None, device_id=None, perf_debug=False, eval_mem=False,
#                                  async_mode=False, core_mask=-1, fallback_prior_device='cpu', ...)
# 判据 (不许改): load_rknn rc 必须 = 0 才算「往返自证过」
import os, sys, time, hashlib, inspect, traceback
WORK = "/var/tmp/iss263_rknn3/work"
os.environ.setdefault("TMPDIR", "/var/tmp/iss263_rknn3/tmp")
from rknn.api import RKNN

OUT2 = os.path.join(WORK, "out", "roundtrip_reexport.rknn")
PAIRS = [(os.path.join(WORK, "out", "yolov5n_heads_int8_rk3572_run1.rknn"), "heads_run1"),
         (os.path.join(WORK, "out", "yolov5s_full_int8_rk3572.rknn"), "full_yolov5s")]


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def banner(t):
    print()
    print("=" * 78)
    print("### " + t)
    print("=" * 78)
    sys.stdout.flush()


print("HOST time =", time.strftime("%Y-%m-%dT%H:%M:%S%z"))
print("rknn pkg  =", os.path.dirname(os.path.dirname(inspect.getfile(RKNN))))
print("load_rknn    SIGNATURE =", str(inspect.signature(RKNN.load_rknn)))
print("init_runtime SIGNATURE =", str(inspect.signature(RKNN.init_runtime)))
print("list_devices SIGNATURE =", str(inspect.signature(RKNN.list_devices)))
sys.stdout.flush()

for rknx, tag in PAIRS:
    wgt = rknx[:-5] + ".weight"
    banner("ROUNDTRIP[%s]: load_rknn(model_path=%s, weight_path=%s)" % (tag, os.path.basename(rknx), os.path.basename(wgt)))
    print("rknn  = %s  %d B  md5=%s" % (rknx, os.path.getsize(rknx), md5(rknx)))
    print("weight= %s  %d B  md5=%s" % (wgt, os.path.getsize(wgt), md5(wgt)))
    r = None
    try:
        r = RKNN(verbose=True)
        t0 = time.time()
        rc = r.load_rknn(rknx, wgt)
        print(">>> rc_load_rknn = %r   t=%.3fs" % (rc, time.time() - t0))
        sys.stdout.flush()
        if rc == 0:
            try:
                rc2 = r.export_rknn(OUT2)
                print(">>> rc_export_rknn = %r" % (rc2,))
                if rc2 == 0 and os.path.exists(OUT2):
                    print(">>> REEXPORT %s bytes=%d md5=%s" % (OUT2, os.path.getsize(OUT2), md5(OUT2)))
                    print(">>> REEXPORT_MD5_MATCH_ORIG = %s" % (md5(OUT2) == md5(rknx)))
            except Exception as e:
                print(">>> export_rknn EXC:", repr(e))
            try:
                rci = r.init_runtime()
                print(">>> init_runtime() rc = %r" % (rci,))
                if rci == 0:
                    print(">>> ★init_runtime 过了 ⇒ 板端可达? 需复核★")
            except Exception as e:
                print(">>> init_runtime() EXC:", repr(e))
            try:
                rci2 = r.init_runtime(target="rk3572", core_mask=RKNN.RKNN3_NPU_CORE_0)
                print(">>> init_runtime(target='rk3572', core_mask=NPU_CORE_0) rc = %r" % (rci2,))
            except Exception as e:
                print(">>> init_runtime(target='rk3572', core_mask=NPU_CORE_0) EXC:", repr(e))
    except Exception:
        traceback.print_exc()
    finally:
        try:
            if r is not None:
                r.release()
        except Exception:
            pass
    sys.stdout.flush()

banner("DEVICE 枚举 (板端可达性)")
try:
    devs = RKNN(verbose=False).list_devices()
    print(">>> list_devices() = %r" % (devs,))
except Exception as e:
    print(">>> list_devices() EXC:", repr(e))
sys.stdout.flush()

banner("SUMMARY")
print("ROUNDTRIP_DONE")
sys.stdout.flush()
