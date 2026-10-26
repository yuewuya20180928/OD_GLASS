#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打印包打包器 (build_print_pack) —— 把 MECH/print/ 的 STL 打成 3MF
================================================================================
★ 本脚本是**项目总工的活** (ISS-058 第 2 步收尾): mech-lead 负责生成几何, 我负责打包。
  mech-lead 只允许改 MECH/print/gen_print_pack.py + 两个 STL, 不许碰 PRINT/。

为什么需要它:
  10-25 那个 3MF 是手工脚本临时打的, 没有留下可复现的打包器 → 几何一改就得重打,
  而且没人说得清"包里的网格 = 现在的 STL"。本脚本把这条链固定下来:
    MECH/print/*.stl  →  本脚本  →  PRINT/ars45_print_pack.3mf  →  PRINT/verify_print_pack.py

★ 只打两个件:
  fit_coupon_340 (检具 coupon) / temple_cage_340 (镜腿骨架)
  optical_cage_TEMPLATE **不进包** —— 走鹃Ⅱ 三维尺寸未到 (u1), 参数全 [推算], 先别打。

用法:  python3 PRINT/build_print_pack.py
自证:  python3 PRINT/verify_print_pack.py
退出码: 0=打包成功  1=失败
"""
from __future__ import annotations

import hashlib
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
STL_DIR = os.path.join(PROJ, "MECH", "print")
OUT = os.path.join(HERE, "ars45_print_pack.3mf")

ITEMS = [("fit_coupon_340", "fit_coupon_340.stl"), ("temple_cage_340", "temple_cage_340.stl")]
SKIPPED = [
    ("optical_cage_TEMPLATE.stl", "走鹃Ⅱ 三维尺寸未到 (u1), 参数全 [推算] → 模板不进包, 先别打"),
]

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>"""


def read_binary_stl(path: str):
    """读二进制 STL → (顶点列表, 三角面索引列表)"""
    raw = open(path, "rb").read()
    if len(raw) < 84:
        raise ValueError(f"{path}: 太短, 不是 STL")
    n = struct.unpack_from("<I", raw, 80)[0]
    if 84 + 50 * n != len(raw):
        raise ValueError(f"{path}: 长度与三角面数不符 ({len(raw)} vs {84 + 50 * n})")
    verts: list[tuple[float, float, float]] = []
    tris: list[tuple[int, int, int]] = []
    index: dict[tuple[float, float, float], int] = {}
    off = 84
    for _ in range(n):
        f = struct.unpack_from("<12fH", raw, off)
        off += 50
        ids = []
        for b in (3, 6, 9):
            p = (round(f[b], 6), round(f[b + 1], 6), round(f[b + 2], 6))
            i = index.get(p)
            if i is None:
                i = len(verts)
                index[p] = i
                verts.append(p)
            ids.append(i)
        tris.append((ids[0], ids[1], ids[2]))
    return verts, tris


def object_xml(obj_id: int, name: str, verts, tris) -> str:
    v = "".join(f'<vertex x="{x}" y="{y}" z="{z}"/>' for x, y, z in verts)
    t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tris)
    return (f'<object id="{obj_id}" type="model" name="{name}">'
            f"<mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>")


def main() -> int:
    parts: list[str] = []
    stats: list[str] = []
    for obj_id, (name, fn) in enumerate(ITEMS, start=1):
        p = os.path.join(STL_DIR, fn)
        if not os.path.exists(p):
            print(f"❌ 缺 STL: {p}", file=sys.stderr)
            return 1
        verts, tris = read_binary_stl(p)
        md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
        parts.append(object_xml(obj_id, name, verts, tris))
        stats.append(f"  {fn:<28} 顶点 {len(verts):>6}  三角面 {len(tris):>6}  md5 {md5}")

    model = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        '<metadata name="Application">ARS45 print pack</metadata>'
        '<metadata name="Title">ARS45 P2S PA-CF 检具打印包 (Rev A, ISS-058)</metadata>'
        "<resources>" + "".join(parts) + "</resources>"
        '<build>' + "".join(
            f'<item objectid="{i}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'
            for i in range(1, len(ITEMS) + 1)) + "</build></model>"
    )

    tmp = OUT + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("3D/3dmodel.model", model)
    os.replace(tmp, OUT)  # 原子替换, 不留半截包

    print("=" * 70)
    print("  打印包打包完成 (Rev A)")
    print("=" * 70)
    print("\n".join(stats))
    for fn, why in SKIPPED:
        print(f"  {fn:<28} 跳过: {why}")
    print(f"  → {OUT}  ({os.path.getsize(OUT)} bytes)")
    print("  自证: python3 PRINT/verify_print_pack.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
