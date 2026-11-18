# -*- coding: utf-8 -*-
"""★_test_esc_dir.py -- 证明 escape 规则的"方向"选项正确, 且默认 (ANY) 逐位一致"""
import os, sys, ast, importlib

SRC = "state/gen_pcb_routing.py"
src = open(SRC, encoding="utf-8").read()
ast.parse(src)

# ★源码级: 方向分支存在 + 默认 ANY
assert "CONN_GND_ESC_DIR = {}" in src
assert '_dir == "DOWN"' in src and '_dir == "UP"' in src
assert 'CONN_GND_ESC_DIR.get(ref, "ANY")' in src

# ★把解析+判据抽出来单独跑 (不 import 整个路由器, 免得副作用)
def build(env_val):
    esc, direc = {}, {}
    for grp in (env_val or "").split(";"):
        grp = grp.strip()
        if not grp or ":" not in grp:
            continue
        try:
            parts = grp.split(":")
            r = parts[0].strip()
            esc[r] = float(parts[1])
            d = (parts[2].strip().upper() if len(parts) > 2 else "ANY")
            direc[r] = d if d in ("UP", "DOWN", "ANY") else "ANY"
        except Exception:
            continue
    return esc, direc

def ok(esc, direc, ref, pad_y, via_y):
    if not esc or not ref:
        return True
    m = esc.get(ref)
    if m is None:
        return True
    d = direc.get(ref, "ANY")
    if d == "DOWN":
        return (via_y - pad_y) >= m
    if d == "UP":
        return (pad_y - via_y) >= m
    return abs(via_y - pad_y) >= m

# ---- 1) 旧语法必须逐位一致 (ANY) ----
e, d = build("CONN_CAM:4.0")
assert e == {"CONN_CAM": 4.0} and d == {"CONN_CAM": "ANY"}
assert ok(e, d, "CONN_CAM", 52.80, 56.80) is True
assert ok(e, d, "CONN_CAM", 52.80, 55.00) is False
assert ok(e, d, "OTHER", 52.80, 52.80) is True
print("✔ 旧语法 'REF:MIN' => ANY (对称) ⇒ 与历史逐位一致")

# ---- 2) DOWN: 只许往 y 增大方向躲 ----
e, d = build("CONN_LIGHT:1.5:DOWN")
assert d["CONN_LIGHT"] == "DOWN"
PAD = 60.15
assert ok(e, d, "CONN_LIGHT", PAD, 61.70) is True, "★下方 1.55mm 应放行 (= 旧的无害下排)"
assert ok(e, d, "CONN_LIGHT", PAD, 58.70) is False, "★上方 1.45mm 必须被拒 (这才是拦路的)"
assert ok(e, d, "CONN_LIGHT", PAD, 57.00) is False, "★上方 3.15mm 也必须被拒 (DOWN 只许往下)"
assert ok(e, d, "CONN_LIGHT", PAD, 60.15) is False
print("✔ DOWN: 上方 (y 变小) 一律拒, 下方 >= MIN 才放行")

# ---- 3) UP: 反向 ----
e, d = build("CONN_LIGHT:1.5:UP")
assert ok(e, d, "CONN_LIGHT", PAD, 58.10) is True
assert ok(e, d, "CONN_LIGHT", PAD, 62.20) is False
print("✔ UP: 反向正确")

# ---- 4) 多组共存 (CONN_CAM 旧语法 + CONN_LIGHT 新语法) ----
e, d = build("CONN_CAM:4.0;CONN_LIGHT:1.5:DOWN")
assert e == {"CONN_CAM": 4.0, "CONN_LIGHT": 1.5}
assert d == {"CONN_CAM": "ANY", "CONN_LIGHT": "DOWN"}
assert ok(e, d, "CONN_CAM", 52.80, 56.90) is True
assert ok(e, d, "CONN_LIGHT", PAD, 58.70) is False
print("✔ 多组共存: 旧组保持 ANY, 新组带方向")

# ---- 5) 非法方向退回 ANY ----
e, d = build("CONN_LIGHT:2.0:SIDEWAYS")
assert d["CONN_LIGHT"] == "ANY"
print("✔ 非法方向名退回 ANY (不炸)")

# ---- 6) ★★**关键场景**: CONN_LIGHT 的 13 个栅栏孔 (y=58.70 上排 / 61.70 下排) ----
e, d = build("CONN_CAM:4.0;CONN_LIGHT:1.5:DOWN")
up_row = [(27.70, 58.70), (28.45, 58.70), (29.20, 58.70), (29.95, 58.70), (30.70, 58.70),
          (31.45, 58.70), (32.45, 58.70), (33.20, 58.70), (33.95, 58.70)]
dn_row = [(27.70, 61.70), (28.45, 61.70), (29.20, 61.70), (29.95, 61.70), (33.70, 61.70)]
n_up_ok = sum(1 for x, y in up_row if ok(e, d, "CONN_LIGHT", PAD, y))
n_dn_ok = sum(1 for x, y in dn_row if ok(e, d, "CONN_LIGHT", PAD, y))
assert n_up_ok == 0, "★上排 9 个孔必须全被拒 (它们是拦路的)"
assert n_dn_ok == 5, "★下排 5 个孔应放行 (它们无害)"
print("✔ 栅栏实测: 上排 %d/%d 放行 (应 0) · 下排 %d/%d 放行 (应 5)"
      % (n_up_ok, len(up_row), n_dn_ok, len(dn_row)))

# ---- 7) 对称规则下上排会怎样 (对照: v45 就是这么打坏 CSI_D0_CK 的) ----
e2, d2 = build("CONN_LIGHT:2.0")
n_up_any = sum(1 for x, y in up_row if ok(e2, d2, "CONN_LIGHT", PAD, y))
print("★对照: 对称规则 (v45) 下上排放行 %d/%d ⇒ 它们只会被赶到 y<=58.15 (更堵)" % (n_up_any, len(up_row)))
assert n_up_any == 0

print("ALL TESTS PASS")
