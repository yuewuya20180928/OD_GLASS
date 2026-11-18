#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打印包自检 (verify_print_pack) —— 校验"打印机能识别的配置文件"自洽
================================================================================
老板 10-25 19:23: "当前先输出打印机能识别的配置文件即可"
→ 所以这个包必须**机器可校验**: 3MF 能解、JSON 合法、STL 尺寸在规格内、三者一致。

用法:  python3 PRINT/verify_print_pack.py [--json]
退出码: 0=自洽  1=有问题  2=文件缺失
"""
from __future__ import annotations

import argparse
import json
import os
import re
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PRINT = HERE
STL_DIR = os.path.join(PROJ, "MECH", "print")

# 规格 (来自 MECH/print/README.md + MECH_BUDGET v1.1 §5.4)
SPEC = {
    "fit_coupon_340.stl": (150.0, 90.0, 22.0, 0.5),
    "temple_cage_340.stl": (60.0, 123.0, 28.0, 1.0),
}
ITEMS = {"fit_coupon_340": "fit_coupon_340.stl", "temple_cage_340": "temple_cage_340.stl"}


def stl_bbox(path: str):
    raw = open(path, "rb").read()
    if len(raw) < 84:
        raise ValueError("STL 太短")
    off, xs, ys, zs, n = 84, [], [], [], 0
    while off + 50 <= len(raw):
        f = struct.unpack_from("<12fH", raw, off)
        off += 50
        for b in (3, 6, 9):
            xs.append(f[b]); ys.append(f[b + 1]); zs.append(f[b + 2])
        n += 1
    if not n:
        raise ValueError("STL 无三角形")
    return (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)), n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    R = []

    def chk(name, ok, detail=""):
        R.append({"name": name, "ok": bool(ok), "detail": detail})

    # 1) 三个 JSON 配置
    for f, must in [("bambu_p2s_machine.json", ["nozzle_diameter", "printable_area"]),
                    ("pa_cf_filament.json", ["filament_type", "nozzle_temperature"]),
                    ("print_profile.json", ["layer_height", "wall_loops", "support_enable"])]:
        p = os.path.join(PRINT, f)
        try:
            d = json.load(open(p, encoding="utf-8"))
            miss = [k for k in must if k not in d]
            chk(f"{f} 合法且键齐全", not miss, f"缺 {miss}" if miss else f"{len(d)} 键")
        except Exception as e:  # noqa: BLE001
            chk(f"{f} 合法且键齐全", False, str(e))

    # 2) 打印参数必须符合 MECH §5.4
    try:
        pr = json.load(open(os.path.join(PRINT, "print_profile.json"), encoding="utf-8"))
        fl = json.load(open(os.path.join(PRINT, "pa_cf_filament.json"), encoding="utf-8"))
        chk("层高 = 0.2mm (§5.4)", pr.get("layer_height") == "0.2", str(pr.get("layer_height")))
        chk("壁圈 = 4 (§5.4 最小壁厚 0.8mm)", pr.get("wall_loops") == "4", str(pr.get("wall_loops")))
        chk("悬空阈值 = 45° (§5.4)", pr.get("support_threshold") == "45", str(pr.get("support_threshold")))
        chk("耗材 = PA-CF (禁 PLA, 55-60°C 即软)", fl.get("filament_type") == "PA-CF", str(fl.get("filament_type")))
        chk("打印温度 = 260℃", fl.get("nozzle_temperature") == "260", str(fl.get("nozzle_temperature")))
    except Exception as e:  # noqa: BLE001
        chk("打印参数可读", False, str(e))

    # 3) STL 存在 + 尺寸符合规格
    for fn, (ex, ey, ez, tol) in SPEC.items():
        p = os.path.join(STL_DIR, fn)
        if not os.path.exists(p):
            chk(f"{fn} 存在", False, p)
            continue
        try:
            (x, y, z), n = stl_bbox(p)
            ok = abs(x - ex) <= tol and abs(y - ey) <= tol and abs(z - ez) <= tol
            chk(f"{fn} 尺寸符合规格", ok,
                f"实测包围盒 {x:.1f}×{y:.1f}×{z:.1f} (期望 {ex}×{ey}×{ez} ±{tol}), {n} 三角面")
        except Exception as e:  # noqa: BLE001
            chk(f"{fn} 可解析", False, str(e))

    # 4) 3MF 可解 + 单位 mm + build item 数对得上
    p3 = os.path.join(PRINT, "ars45_print_pack.3mf")
    if not os.path.exists(p3):
        chk("3MF 存在", False, p3)
    else:
        try:
            with zipfile.ZipFile(p3) as z:
                names = z.namelist()
                chk("3MF 是合法 OPC 包", "[Content_Types].xml" in names and "3D/3dmodel.model" in names,
                    ", ".join(names))
                m = z.read("3D/3dmodel.model").decode("utf-8")
                chk("3MF 单位 = millimeter", 'unit="millimeter"' in m, "缺单位 → 切片软件会按 inch 读, 尺寸差 25.4 倍")
                chk("3MF build item 数 = 2", m.count("<item ") == len(ITEMS), f"{m.count('<item ')} 个")
                chk("3MF 顶点/三角面非空", m.count("<vertex ") > 100 and m.count("<triangle ") > 100,
                    f"{m.count('<vertex ')} 顶点 / {m.count('<triangle ')} 三角面")
                for nm in ITEMS:
                    chk(f"3MF 含 {nm}", f'name="{nm}"' in m, "")
        except Exception as e:  # noqa: BLE001
            chk("3MF 可解析", False, str(e))

    # 5) 测量清单 + 打印卡在位
    chk("测量清单在位 (41 项)",
        os.path.exists(os.path.join(STL_DIR, "MEASURE_CHECKLIST.md")), "MECH/print/MEASURE_CHECKLIST.md")
    chk("打印执行卡在位", os.path.exists(os.path.join(PRINT, "PRINTER_SETUP.md")), "PRINT/PRINTER_SETUP.md")

    bad = [r for r in R if not r["ok"]]
    if args.json:
        print(json.dumps({"total": len(R), "passed": len(R) - len(bad), "failed": len(bad),
                          "criteria": R}, ensure_ascii=False, indent=2))
        return 1 if bad else 0

    print("=" * 70)
    print("  打印包自检 · 打印机能认的配置")
    print("=" * 70)
    for r in R:
        print(f"  {'✅' if r['ok'] else '❌'} {r['name']}")
        if r["detail"]:
            print(f"       {r['detail']}")
    print()
    print(f"  {'✅ 自洽 — 可直接导入打印机软件切片打印' if not bad else f'❌ {len(bad)} 项不通过'}")
    print("=" * 70)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
