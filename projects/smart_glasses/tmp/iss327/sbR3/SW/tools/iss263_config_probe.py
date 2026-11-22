#!/usr/bin/env python3
# ISS-263 · rknn3-toolkit 1.2.0 实跑: import + config(target_platform) 正/反向自证
import sys, time, traceback, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def show(tag):
    print("\n" + "="*70)
    print("### %s" % tag)
    print("="*70)

show("T0: import rknn.api.RKNN")
rc_import = 0
try:
    from rknn.api import RKNN
    print("IMPORT_OK  from rknn.api import RKNN")
except Exception:
    traceback.print_exc(); rc_import = 1
if rc_import:
    sys.exit(rc_import)

import rknn
print("rknn.__path__ =", list(getattr(rknn, "__path__", [])))
try:
    import rknn.api as _api
    apifile = getattr(_api, "__file__", None)
    print("rknn.api.__file__ =", apifile)
    if apifile:
        vfile = os.path.join(os.path.dirname(os.path.dirname(apifile)), "VERSION")
        print("VERSION file =", open(vfile).read().strip() if os.path.exists(vfile) else "n/a @ %s" % vfile)
except Exception:
    traceback.print_exc()
try:
    import importlib.metadata as md
    print("dist version  =", md.version("rknn3-toolkit"))
except Exception as e:
    print("dist version  = ERR", e)

for target in ("rk3572", "rk3576"):
    show("T1: config(target_platform='%s')" % target)
    t0 = time.time()
    try:
        r = RKNN(verbose=True)
        ret = r.config(target_platform=target)
        print("CONFIG_RETURN type=%s repr=%r" % (type(ret).__name__, ret))
        print("CONFIG_OK target=%s elapsed=%.3fs" % (target, time.time()-t0))
        try:
            r.release()
        except Exception:
            pass
    except Exception:
        traceback.print_exc()
        print("CONFIG_EXC target=%s elapsed=%.3fs" % (target, time.time()-t0))

show("T2: 反向自证 —— RKNN 类方法清单 (证明 config 真读 target_platform)")
import inspect
names = [n for n in dir(RKNN) if not n.startswith("_")]
print("RKNN methods:", names)
print("\nCONFIG_SIG:", inspect.signature(RKNN.config))
