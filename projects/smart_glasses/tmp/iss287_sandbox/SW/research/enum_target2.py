import sys, traceback
from rknn.api.rknn import RKNN
import rknn as _r
print("VERSION_FILE:", open(_r.__path__[0] + "/VERSION").read().strip())
for tgt in ["rk3572","rk3576","rk2118","rk3568","rk1808","rk3399pro","rv1126","rv1109"]:
    r = RKNN(verbose=False)
    try:
        ret = r.config(target_platform=tgt)
        print(f"[{tgt}] config() -> ret={ret}  ==> ACCEPTED")
    except Exception as e:
        print(f"[{tgt}] config() -> {type(e).__name__}: {e}")
    finally:
        try: r.release()
        except Exception: pass
