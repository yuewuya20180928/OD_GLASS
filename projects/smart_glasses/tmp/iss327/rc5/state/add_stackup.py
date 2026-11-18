#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_stackup.py —— ★★给 .kicad_pcb 注入 (stackup ...) 叠层/介质规格 (2026-11-05)

★**为什么必须有**: 投板文件里没有叠层 ⇒ 板厂只能按"默认 1.6mm 8层 FR4"猜
  ⇒ ① 高速差分对 (USB 90Ω / MIPI DSI·CSI 100Ω) **阻抗无从控制**
  ⇒ ② 层间介质厚度不明 ⇒ 阻抗/串扰不可算
  ⇒ ③ ★这是**投板交付项** (G1 之外但同属"可下单")

★**不碰布线**: 本脚本只在 `(setup ...)` 里插一段 `(stackup ...)` ⇒ 铜/走线/焊盘一律不动
★**幂等**: 已经注入过就跳过 (用标记行 `-- STACKUP-INJECTED --` 判定)

用法:
    python3 state/add_stackup.py <board.kicad_pcb> [--inplace]
    (默认写 <board>.stackup.kicad_pcb; 加 --inplace 才原地覆盖)
"""
import os
import re
import sys

MARK = "STACKUP-INJECTED"   # ★只写在控制台/日志, **不进文件** (裸文本行会让 KiCad 解析失败)


# ---------------------------------------------------------------- 叠层参数
# ★铜厚: 外层 1oz (0.035mm) / 内层 0.5oz (0.018mm) —— demo 台架板走线密, 内层薄铜省成本
CU_OUT = 0.035
CU_IN = 0.018
MASK = 0.010
TOTAL = 1.600          # ★总板厚目标 (mm)
PREPREG = "PR2116"    # ★低损耗 prepreg (εr 4.1)
CORE = "FR4"          # ★芯板 (εr 4.3)
EPS_PREPREG = 4.1
EPS_CORE = 4.3
LOSS = 0.02


def _cu_layers(board_text):
    """从 (layers ...) 段里读出真实铜层名 (按 KiCad 顺序: F.Cu, In1.Cu, ... B.Cu)"""
    m = re.search(r"\(layers\s*(.*?)\n\t\)", board_text, re.S)
    if not m:
        raise SystemExit("✗ 板文件里找不到 (layers ...) 段")
    out = []
    for line in m.group(1).splitlines():
        mm = re.match(r'\s*\((\d+)\s+"([^"]+)"\s+(\w+)', line)
        if mm and mm.group(3) == "signal":
            out.append(mm.group(2))
    # ★KiCad 的 (layers) 段里铜层是按数字 id 排的, 不是物理顺序 ⇒ 手工排
    order = []
    for nm in out:
        if nm == "F.Cu":
            order.append(nm)
        elif nm == "B.Cu":
            order.append(nm)
        elif nm.startswith("In") and nm.endswith(".Cu"):
            order.append(nm)
    if not order:
        raise SystemExit("✗ 没解析出铜层")
    order.sort(key=lambda n: (0 if n == "F.Cu" else 2 if n == "B.Cu" else 1,
                              int(re.match(r"In(\d+)\.Cu", n).group(1))
                              if n.startswith("In") else 0))
    return order


def _dielectric_plan(n_cu):
    """返回 [(type, material, eps, thickness), ...] —— n_cu-1 段, 总厚凑到 TOTAL"""
    n_d = n_cu - 1
    # ★prepreg (外侧/内层之间) 与 core (中央大芯) 交替: prepreg 薄、core 厚
    pattern = []
    for i in range(n_d):
        # ★从两端往中间: 两端是 prepreg, 中间是 core
        edge = min(i, n_d - 1 - i)
        pattern.append("prepreg" if edge % 2 == 0 else "core")
    # ★core 占比 0.70
    n_core = sum(1 for p in pattern if p == "core")
    n_pre = n_d - n_core
    cu_sum = 2 * CU_OUT + (n_cu - 2) * CU_IN
    d_total = TOTAL - 2 * MASK - cu_sum
    if n_core == 0:
        d_each = d_total / max(n_pre, 1)
        plan = [("prepreg", PREPREG, EPS_PREPREG, d_each)] * n_d
    else:
        core_t = d_total * 0.70 / n_core
        pre_t = (d_total - core_t * n_core) / max(n_pre, 1) if n_pre else 0.0
        plan = []
        for p in pattern:
            if p == "core":
                plan.append(("core", CORE, EPS_CORE, core_t))
            else:
                plan.append(("prepreg", PREPREG, EPS_PREPREG, pre_t))
    return [(t, m, e, round(th, 4)) for (t, m, e, th) in plan]


def build_stackup(cu):
    """生成 (stackup ...) 文本块"""
    n = len(cu)
    plan = _dielectric_plan(n)
    L = []
    L.append("\t\t(stackup")
    L.append('\t\t\t(layer "F.SilkS"')
    L.append('\t\t\t\t(type "Top Silk Screen")')
    L.append('\t\t\t)')
    L.append('\t\t\t(layer "F.Paste"')
    L.append('\t\t\t\t(type "Top Solder Paste")')
    L.append('\t\t\t)')
    L.append('\t\t\t(layer "F.Mask"')
    L.append('\t\t\t\t(type "Top Solder Mask")')
    L.append('\t\t\t\t(color "Black")')
    L.append("\t\t\t\t(thickness %.3f)" % MASK)
    L.append("\t\t\t)")
    for i, nm in enumerate(cu):
        th = CU_OUT if nm in ("F.Cu", "B.Cu") else CU_IN
        L.append('\t\t\t(layer "%s"' % nm)
        L.append('\t\t\t\t(type "copper")')
        L.append("\t\t\t\t(thickness %.3f)" % th)
        L.append("\t\t\t)")
        if i < len(plan):
            dtype, mat, eps, dth = plan[i]
            L.append('\t\t\t(layer "dielectric %d"' % (i + 1))
            L.append('\t\t\t\t(type "%s")' % dtype)
            L.append("\t\t\t\t(thickness %.4f)" % dth)
            L.append('\t\t\t\t(material "%s")' % mat)
            L.append("\t\t\t\t(epsilon_r %.2f)" % eps)
            L.append("\t\t\t\t(loss_tangent %.3f)" % LOSS)
            L.append("\t\t\t)")
    L.append('\t\t\t(layer "B.Mask"')
    L.append('\t\t\t\t(type "Bottom Solder Mask")')
    L.append('\t\t\t\t(color "Black")')
    L.append("\t\t\t\t(thickness %.3f)" % MASK)
    L.append("\t\t\t)")
    L.append('\t\t\t(layer "B.Paste"')
    L.append('\t\t\t\t(type "Bottom Solder Paste")')
    L.append("\t\t\t)")
    L.append('\t\t\t(layer "B.SilkS"')
    L.append('\t\t\t\t(type "Bottom Silk Screen")')
    L.append("\t\t\t)")
    L.append('\t\t\t(copper_finish "ENIG")')
    L.append("\t\t\t(dielectric_constraints no)")
    L.append("\t\t)")
    return "\n".join(L)


def inject(path, inplace=False):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    if re.search(r"^\t\t\(stackup\s*$", txt, re.M):
        print("ℹ️ 已经有叠层段 ⇒ 跳过 (%s)" % MARK)
        return txt, False
    cu = _cu_layers(txt)
    blk = build_stackup(cu)
    m = re.search(r"^\t\(setup\s*$", txt, re.M)
    if not m:
        raise SystemExit("✗ 找不到 (setup ...) 段")
    out = txt[:m.end()] + "\n" + blk + "\n" + txt[m.end():]
    dst = path if inplace else path.replace(".kicad_pcb", "") + ".stackup.kicad_pcb"
    open(dst, "w", encoding="utf-8").write(out)
    tot = 2 * MASK + 2 * CU_OUT + (len(cu) - 2) * CU_IN + \
        sum(p[3] for p in _dielectric_plan(len(cu)))
    print("✅ 注入叠层: %d 层铜 (%s)" % (len(cu), " / ".join(cu)))
    print("   总厚 %.3f mm · 外铜 %.3f / 内铜 %.3f · 介质 %d 段" %
          (tot, CU_OUT, CU_IN, len(cu) - 1))
    print("   输出: %s" % dst)
    return out, True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    inplace = "--inplace" in sys.argv
    if not os.path.exists(src):
        print("✗ 文件不存在: %s" % src)
        sys.exit(1)
    inject(src, inplace)
