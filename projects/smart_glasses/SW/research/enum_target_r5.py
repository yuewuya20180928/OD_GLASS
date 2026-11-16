#!/usr/bin/env python3
# ★ISS-250 第5轮 · 独立复核 (★2026-11-17 04:5x★)
# 目的: 自己实跑一遍两个工具链的 target_platform 合法性, 不抄上一轮报告
# 用法: <conda env python> SW/research/enum_target_r5.py
import sys, os, json, time
import rknn as _r
from rknn.api.rknn import RKNN

CAND = ["rk3572","rk3572b","rk3576","rk3588","rk3562","rk3566","rk3568","rk3568b",
        "rk2118","rk2108","rk3516","rk3506","rk1820","rk1828","gongga2",
        "rv1103","rv1103b","rv1103c","rv1106","rv1106b","rv1109","rv1126","rv1126b",
        "rv1209","rv1210","rk1806","rk1808","rk3399","rk3399pro","rk3288"]
vpath = os.path.join(_r.__path__[0], "VERSION")
ver = open(vpath).read().strip() if os.path.exists(vpath) else "?"
print("PKG_PATH:", os.path.abspath(_r.__path__[0]))
print("VERSION:", ver)
print("PY:", sys.version.split()[0])
print("CAND_COUNT:", len(CAND))
ok, bad = [], []
t0 = time.time()
for t in CAND:
    r = RKNN(verbose=False)
    try:
        ret = r.config(target_platform=t)
        (ok if ret == 0 else bad).append((t, "ret=%r" % (ret,)))
    except Exception as e:
        bad.append((t, "%s: %s" % (type(e).__name__, str(e)[:120])))
    finally:
        try: r.release()
        except Exception: pass
print("ELAPSED_S: %.3f" % (time.time() - t0))
print("ACCEPTED_COUNT:", len(ok), "ACCEPTED:", ",".join(t for t, _ in ok))
print("REJECTED_COUNT:", len(bad))
for t, why in bad:
    print("  REJ ", t, "->", why)
