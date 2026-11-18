from rknn.api.rknn import RKNN
CAND = ["rk1808","rk3399pro","rv1103","rv1103b","rv1106","rv1106b","rv1109","rv1126","rv1126b",
        "rk2118","rk2108","rk3562","rk3566","rk3568","rk3572","rk3576","rk3588","rk3572b",
        "rk3516","rk3506","rv1210","rv1209","rk1806","rk3399","rk3288","rk3568b","rv1103c"]
ok, bad = [], []
for t in CAND:
    r = RKNN(verbose=False)
    try:
        ret = r.config(target_platform=t)
        (ok if ret==0 else bad).append((t, f"ret={ret}"))
    except Exception as e:
        bad.append((t, type(e).__name__))
    finally:
        try: r.release()
        except Exception: pass
print("ACCEPTED_COUNT:", len(ok))
for t,r in ok: print("  OK  ", t, r)
print("REJECTED_COUNT:", len(bad))
print("REJECTED:", ",".join(t for t,_ in bad))
