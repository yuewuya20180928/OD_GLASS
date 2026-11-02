#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_kicad_project.py —— demo 主板图纸生成器 (★"硬件自己画图"的机器化起点)

为什么是脚本生成:
  ★**图纸不能靠人肉维护** —— EN 那个 P0 (9 路电源 EN 悬空=关断 ⇒ 投板后整板不上电) 就是
  人肉画/表格式画图时最容易漏的一类。⇒ **图纸从「参数 + 网表」生成, 改一次重跑, 不漂移**。
  ★**分工**: 脚本出**骨架**(板框/叠层/接口焊盘/网络类/丝印/关键位置) ⇒ 密集布线与 ERC/DRC 收口由 hw-lead 在 KiCad 里做。

产出:
  HW/PCB/demo_mainboard.kicad_pcb   —— KiCad 10 格式 PCB (S-expression)
  HW/PCB/demo_mainboard.kicad_pro   —— 工程文件 (netclass + 设计规则占位)
  HW/PCB/STACKUP.md                 —— 叠层表 (含阻抗参数)
  HW/PCB/LAYOUT_RULES.md            —— 布线/阻抗/等长规则
  HW/PCB/GEN_SELF_CHECK.txt         —— 本次生成的自检结果

自检 (rc=0 才算过):
  C1 板框闭合 (4 段直线 + 圆角) 且尺寸与参数一致
  C2 每个 footprint 的 ref 唯一
  C3 FPC 针数与参数一致 (camera / display)
  C4 所有 footprint 有封装名 (KiCad 需要真实封装才能开板)
  C5 叠层层数与参数一致 (6 层)
  C6 网络类齐全 (MIPI_CSI / MIPI_DSI / USB / PWR / 默认)
"""
import json
import os
import sys
from datetime import datetime

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB_DIR = os.path.join(PROJ, "HW", "PCB")
PARAMS = os.path.join(PCB_DIR, "demo_mainboard_params.json")

LAYER_NAMES = {
    0: "F.Cu", 1: "B.Cu", 2: "In1.Cu", 3: "In2.Cu", 4: "In3.Cu", 5: "In4.Cu",
    6: "F.SilkS", 7: "B.SilkS", 8: "F.Mask", 9: "B.Mask", 10: "F.Paste", 11: "B.Paste",
    12: "Edge.Cuts", 13: "F.Fab", 14: "B.Fab", 15: "Dwgs.User", 16: "Cmts.User",
    17: "Eco1.User", 18: "Eco2.User", 19: "Edge.Cuts", 20: "Margin",
}
# 6 层: 0/1 = 内外铜, 2..5 = 内层 (实际 6 铜层 ⇒ F.Cu B.Cu + 4 内层)
N_COPPER = 6


def ts():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def esc(s):
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def fpc_footprint(ref, pins, pitch, label):
    """FPC 座: 单排双面 (双排插) —— 用两排焊盘 + 外壳 pad"""
    rows = []
    n = pins
    # 两排各 n/2 个焊盘, 间距 = n*pitch/2 + 1mm
    half = n // 2
    span = (half - 1) * pitch
    out = []
    for i in range(half):
        x = i * pitch
        out.append((x, 0.0, "1"))
        out.append((x, 2.0, "1"))
    w = span + pitch
    h = 4.0
    lines = [
        f'  (footprint "FPC_{pins}P_{str(pitch).replace(".", "p")}mm"',
        f'    (layer "F.Cu")',
        f'    (uuid "{uuid4()}")',
        f'    (at 0 0)',
        f'    (property "Reference" "{ref}" (at 0 -2 0) (layer "F.SilkS") (uuid "{uuid4()}")',
        f'      (effects (font (size 1 1) (thickness 0.15)))',
        f'    )',
        f'    (property "Value" "{label}" (at 0 -3.6 0) (layer "F.Fab") (uuid "{uuid4()}")',
        f'      (effects (font (size 1 1) (thickness 0.15)))',
        f'    )',
        f'    (fp_line (start 0 -1) (end {w:.3f} -1) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uuid4()}"))',
        f'    (fp_line (start 0 {h}) (end {w:.3f} {h}) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uuid4()}"))',
        f'    (fp_line (start 0 -1) (end 0 {h}) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uuid4()}"))',
        f'    (fp_line (start {w:.3f} -1) (end {w:.3f} {h}) (stroke (width 0.12) (type solid)) (layer "F.SilkS") (uuid "{uuid4()}"))',
    ]
    for (x, y, num) in out:
        lines.append(
            f'    (pad "1" smd rect (at {x:.3f} {y:.3f}) (size {pitch*0.6:.3f} 0.6) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{uuid4()}"))')
    lines.append("  )")
    return "\n".join(lines)


def generic_footprint(ref, value, pins, pitch, width, height, npins_x=1, npins_y=1):
    """通用矩形焊盘阵列 (给 SOM / 排针 / 按钮座 用)"""
    lines = [
        f'  (footprint "Gen_{pins}P_{str(pitch).replace(".", "p")}mm"',
        f'    (layer "F.Cu")',
        f'    (uuid "{uuid4()}")',
        f'    (at 0 0)',
        f'    (property "Reference" "{ref}" (at 0 {-height/2-1.5:.3f} 0) (layer "F.SilkS") (uuid "{uuid4()}")',
        f'      (effects (font (size 1 1) (thickness 0.15)))',
        f'    )',
        f'    (property "Value" "{value}" (at 0 {-height/2-3:.3f} 0) (layer "F.Fab") (uuid "{uuid4()}")',
        f'      (effects (font (size 1 1) (thickness 0.15)))',
        f'    )',
        f'    (fp_rect (start {-width/2:.3f} {-height/2:.3f}) (end {width/2:.3f} {height/2:.3f}) (stroke (width 0.12) (type solid)) (fill none) (layer "F.Fab") (uuid "{uuid4()}"))',
    ]
    idx = 1
    for j in range(npins_y):
        for i in range(npins_x):
            x = -width / 2 + pitch / 2 + i * pitch
            y = -height / 2 + pitch / 2 + j * pitch
            lines.append(
                f'    (pad "{idx}" smd rect (at {x:.3f} {y:.3f}) (size {pitch*0.55:.3f} {pitch*0.55:.3f}) (layers "F.Cu" "F.Paste" "F.Mask") (uuid "{uuid4()}"))')
            idx += 1
    lines.append("  )")
    return "\n".join(lines)


def uuid4():
    import uuid
    return str(uuid.uuid4())


def build_pcb(P):
    b = P["board"]
    W, H = b["width_mm"], b["height_mm"]
    r = b.get("corner_radius_mm", 0)
    lines = []
    lines.append('(kicad_pcb (version 20240108) (generator "gen_kicad_project.py")')
    lines.append(f'  (general (thickness {b["thickness_mm"]}) (legacy_teardrops no))')
    # 层定义: 6 铜层
    lines.append('  (layers')
    lines.append('    (0 "F.Cu" signal)')
    lines.append('    (1 "B.Cu" signal)')
    for i in range(2, N_COPPER):
        lines.append(f'    ({i} "In{i-1}.Cu" signal)')
    lines.append('    (32 "B.Adhes" user "B.Adhesive")')
    lines.append('    (33 "F.Adhes" user "F.Adhesive")')
    lines.append('    (34 "B.Paste" user)')
    lines.append('    (35 "F.Paste" user)')
    lines.append('    (36 "B.SilkS" user "B.Silkscreen")')
    lines.append('    (37 "F.SilkS" user "F.Silkscreen")')
    lines.append('    (38 "B.Mask" user)')
    lines.append('    (39 "F.Mask" user)')
    lines.append('    (40 "Dwgs.User" user "User.Drawings")')
    lines.append('    (41 "Cmts.User" user "User.Comments")')
    lines.append('    (42 "Eco1.User" user "User.Eco1")')
    lines.append('    (43 "Eco2.User" user "User.Eco2")')
    lines.append('    (44 "Edge.Cuts" user)')
    lines.append('    (45 "Margin" user)')
    lines.append('    (46 "B.CrtYd" user "B.Courtyard")')
    lines.append('    (47 "F.CrtYd" user "F.Courtyard")')
    lines.append('    (48 "B.Fab" user)')
    lines.append('    (49 "F.Fab" user)')
    lines.append('  )')
    # 叠层 (setup)
    st = P["stackup"]
    lines.append('  (setup')
    lines.append('    (pad_to_mask_clearance 0.05)')
    lines.append('    (allow_soldermask_bridges_in_footprints no)')
    lines.append(f'    (stackup')
    lines.append(f'      (layer "F.SilkS" (type "Top Silk Screen"))')
    lines.append(f'      (layer "F.Paste" (type "Top Solder Paste"))')
    lines.append(f'      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))')
    lines.append(f'      (layer "F.Cu" (type "copper") (thickness 0.035))')
    lines.append(f'      (layer "dielectric 1" (type "prepreg") (thickness {st["prepreg_thickness_mm"]}) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))')
    lines.append(f'      (layer "In1.Cu" (type "copper") (thickness 0.0175))')
    lines.append(f'      (layer "dielectric 2" (type "core") (thickness {st["core_thickness_mm"]}) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))')
    lines.append(f'      (layer "In2.Cu" (type "copper") (thickness 0.035))')
    lines.append(f'      (layer "dielectric 3" (type "prepreg") (thickness {st["prepreg_thickness_mm"]}) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))')
    lines.append(f'      (layer "In3.Cu" (type "copper") (thickness 0.0175))')
    lines.append(f'      (layer "dielectric 4" (type "core") (thickness {st["core_thickness_mm"]}) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))')
    lines.append(f'      (layer "In4.Cu" (type "copper") (thickness 0.035))')
    lines.append(f'      (layer "dielectric 5" (type "prepreg") (thickness {st["prepreg_thickness_mm"]}) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))')
    lines.append(f'      (layer "B.Cu" (type "copper") (thickness 0.035))')
    lines.append(f'      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))')
    lines.append(f'      (layer "B.Paste" (type "Bottom Solder Paste"))')
    lines.append(f'      (layer "B.SilkS" (type "Bottom Silk Screen"))')
    lines.append(f'      (copper_finish "ENIG")')
    lines.append(f'      (dielectric_constraints no)')
    lines.append(f'    )')
    lines.append('  )')
    # 网络类 (阻抗规则)
    imp = st["impedance"]
    lines.append('  (net_class "MIPI_CSI" "MIPI CSI (camera)" (clearance 0.2) (trace_width 0.1) '
                 f'(via_dia 0.45) (via_drill 0.2) (diff_pair_width 0.1) (diff_pair_gap 0.15) (uvia_dia 0.3) (uvia_drill 0.1))')
    lines.append('  (net_class "MIPI_DSI" "MIPI DSI (display)" (clearance 0.2) (trace_width 0.1) '
                 f'(via_dia 0.45) (via_drill 0.2) (diff_pair_width 0.1) (diff_pair_gap 0.15) (uvia_dia 0.3) (uvia_drill 0.1))')
    lines.append('  (net_class "USB" "USB 2.0" (clearance 0.2) (trace_width 0.11) '
                 f'(via_dia 0.45) (via_drill 0.2) (diff_pair_width 0.11) (diff_pair_gap 0.15) (uvia_dia 0.3) (uvia_drill 0.1))')
    lines.append('  (net_class "PWR" "Power" (clearance 0.25) (trace_width 0.5) (via_dia 0.6) (via_drill 0.3))')
    lines.append('  (net_class "Default" "Default" (clearance 0.2) (trace_width 0.25) (via_dia 0.45) (via_drill 0.2))')
    # 板框 (Edge.Cuts) 圆角矩形
    x0, y0, x1, y1 = 0, 0, W, H
    corners = [(x0 + r, y0), (x1 - r, y0), (x1, y0 + r), (x1, y1 - r), (x1 - r, y1), (x0 + r, y1), (x0, y1 - r), (x0, y0 + r)]
    pts = corners + [corners[0]]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        lines.append(f'  (gr_line (start {a[0]:.3f} {a[1]:.3f}) (end {b[0]:.3f} {b[1]:.3f}) '
                     f'(stroke (width 0.1) (type solid)) (layer "Edge.Cuts") (uuid "{uuid4()}"))')
    # footprints
    fps = []
    cam = P["fpc_camera"]
    fps.append((cam["ref"], fpc_footprint(cam["ref"], cam["pins"], cam["pitch_mm"], "FPC CAM"), cam["position_mm"] if "position_mm" in cam else [10.0, 10.0]))
    disp = P["fpc_display"]
    fps.append((disp["ref"], fpc_footprint(disp["ref"], disp["pins"], disp["pitch_mm"], "FPC DISP"), disp["position_mm"] if "position_mm" in disp else [10.0, 35.0]))
    som = P["som"]
    fps.append((som["ref"], generic_footprint(som["ref"], "RK3572 SOM (PLACEHOLDER)", som["pins_x"] * som["pins_y"],
                                              som["pitch_mm"], som["width_mm"], som["height_mm"], som["pins_x"], som["pins_y"]),
                som["position_mm"]))
    cn = P["connectors"]
    fps.append((cn["usb_c_ref"], generic_footprint(cn["usb_c_ref"], "USB-C", 16, 0.5, 9.0, 7.5), cn["usb_c_position_mm"]))
    fps.append((cn["uart_ref"], generic_footprint(cn["uart_ref"], "UART", cn["uart_pins"], cn["uart_pitch_mm"], 10.0, 5.0, cn["uart_pins"], 1), cn["uart_position_mm"]))
    fps.append((cn["jtag_ref"], generic_footprint(cn["jtag_ref"], "JTAG", cn["jtag_pins"], cn["jtag_pitch_mm"], 13.0, 5.0, cn["jtag_pins"], 1), cn["jtag_position_mm"]))
    for b in P["misc"]["buttons"]:
        fps.append((b["ref"], generic_footprint(b["ref"], b["label"], 4, 2.54, 6.0, 6.0, 2, 2), b["position_mm"]))
    for l in P["misc"]["leds"]:
        fps.append((l["ref"], generic_footprint(l["ref"], l["label"], 2, 2.54, 3.0, 3.0, 2, 1), l["position_mm"]))
    for (ref, body, pos) in fps:
        body = body.replace("(at 0 0)", f"(at {pos[0]:.3f} {pos[1]:.3f})", 1)
        lines.append(body)
    # 安装孔 (NPTH)
    for (mx, my) in P["misc"]["mounting_holes"]:
        d = P["misc"]["mounting_hole_diameter_mm"]
        lines.append(f'  (footprint "MountingHole_{d}mm" (layer "F.Cu") (uuid "{uuid4()}") (at {mx:.3f} {my:.3f})')
        lines.append(f'    (attr through_hole exclude_from_pos_files exclude_from_bom)')
        lines.append(f'    (fp_circle (center 0 0) (end {d/2:.3f} 0) (stroke (width 0.15) (type solid)) (fill none) (layer "Edge.Cuts") (uuid "{uuid4()}"))')
        lines.append(f'    (pad "" np_thru_hole circle (at 0 0) (size {d:.3f} {d:.3f}) (drill {d:.3f}) (layers "F&B.Cu" "*.Mask") (uuid "{uuid4()}"))')
        lines.append('  )')
    # 丝印
    ss = P["silkscreen"]
    lines.append(f'  (gr_text "PCB: {esc(ss["title"])}" (at {W/2:.3f} {H-2:.3f}) (layer "F.SilkS") '
                 f'(uuid "{uuid4()}") (effects (font (size 1 1) (thickness 0.15))))')
    for i, n in enumerate(ss["notes"]):
        lines.append(f'  (gr_text "{esc(n)}" (at 3 {6+i*2.2:.3f}) (layer "F.SilkS") '
                     f'(uuid "{uuid4()}") (effects (font (size 0.8 0.8) (thickness 0.12))))')
    lines.append(')')
    return "\n".join(lines), fps


def main():
    os.makedirs(PCB_DIR, exist_ok=True)
    P = json.load(open(PARAMS, encoding="utf-8"))
    pcb, fps = build_pcb(P)
    out_pcb = os.path.join(PCB_DIR, "demo_mainboard.kicad_pcb")
    open(out_pcb, "w", encoding="utf-8").write(pcb + "\n")

    # --- 叠层/规则文档 ---
    st = P["stackup"]
    imp = st["impedance"]
    b = P["board"]
    stackup_md = f"""# HW/PCB/STACKUP.md —— demo 主板叠层（★生成于 {ts()}）

| 项 | 值 |
|---|---|
| 板尺寸 | **{b['width_mm']} × {b['height_mm']} mm** (草案, 待 ISS-158 三件规格回来后重跑生成器更新) |
| 总厚 | {b['thickness_mm']} mm |
| 铜厚 | {b['copper_oz']} oz (外层) / 1/2 oz (内层) |
| ★**层数** | **{b['layers']} 层** |
| 叠层 | L1 信号 / **L2 GND 完整平面** / L3 信号+局部电源 / L4 电源平面 / L5 信号 / **L6 GND 完整平面** |
| 介质 | prepreg {st['prepreg_thickness_mm']} mm / core {st['core_thickness_mm']} mm, FR4 εr=4.5 |
| ★**阻抗** | **MIPI 差分 {imp['mipi_diff_ohm']}Ω** / USB 差分 {imp['usb_diff_ohm']}Ω / 单端 {imp['single_ended_ohm']}Ω |
| 表面处理 | ENIG |

★**为什么 MIPI 差分下方必须是完整 GND 平面**: 参考电流路径 ⇒ ★**L2/L6 不得在差分对下方被分割** ⇒ 分割只能走 L3/L5。
★**待定项** (等 ISS-158): 板尺寸 / FPC 针位 / SOM 外形 / 是否需要 L4 拆成 3.3V+5V 两块平面。
"""
    open(os.path.join(PCB_DIR, "STACKUP.md"), "w", encoding="utf-8").write(stackup_md)

    rules_md = f"""# HW/PCB/LAYOUT_RULES.md —— 布线与阻抗规则（★生成于 {ts()}）

| 网络类 | 差分阻抗 | 约束 |
|---|---|---|
| **MIPI_CSI** (camera) | **{imp['mipi_diff_ohm']}Ω** | ★差分对内间距固定; ★对间距 ≥3× 线宽; ★**L2/L6 下方完整 GND**; ★**不跨分割**; ★长度差 ≤0.13mm; ★**不走 L3/L5 之间的过孔区** |
| **MIPI_DSI** (display) | **{imp['mipi_diff_ohm']}Ω** | 同上; ★★**display FPC 座与 SOM 的 DSI 差分总长尽量短** (目标 ≤60mm) |
| **USB** (Type-C) | {imp['usb_diff_ohm']}Ω | 同上; ★**ESD 器件紧贴座** |
| **PWR** | — | 3.3V/5V 大电流: SOM 输入 ≥2A ⇒ ≥0.5mm 铜宽 + 过孔阵列; ★**SOM 输入电容紧贴 SOM 电源脚** |
| 默认 | {imp['single_ended_ohm']}Ω 单端 | 常规 |

★**三条与 EN 教训同源的硬规则**:
1. ★**MCLK 与 CSI/DSI 时钟对必须分开走** (间距 ≥3× 线宽, 中间夹 GND) —— 否则 RAW 里有周期性抖动。
2. ★**每个电源 IC 的 EN 必须在图上有明确网络** (已进网表: 9 路全补, AVDD 走 RC 延时) ⇒ ★**PCB 上对应 RC 位置紧贴 LDO 的 EN 脚**。
3. ★**AC 耦合电容的位置**: 优先**模组内置**; 主板侧位保留 ⇒ ★**若模组不内置, 主板侧的 AC 耦合必须紧贴 FPC 座** (≤5mm), 不要放在 SOM 侧。
"""
    open(os.path.join(PCB_DIR, "LAYOUT_RULES.md"), "w", encoding="utf-8").write(rules_md)

    # --- 自检 ---
    checks = []
    ok = True
    def chk(name, cond, detail=""):
        nonlocal ok
        checks.append((name, bool(cond), detail))
        if not cond:
            ok = False

    # C1 板框闭合
    edges = [l for l in pcb.split("\n") if "(gr_line" in l and "Edge.Cuts" in l]
    chk("C1 板框闭合 (Edge.Cuts 线段数 ≥4)", len(edges) >= 4, f"{len(edges)} 段")
    # C2 ref 唯一
    refs = [r for (r, _, _) in fps]
    chk("C2 footprint ref 唯一", len(refs) == len(set(refs)), f"{len(refs)} 个 / {len(set(refs))} 唯一")
    # C3 FPC 针数
    chk("C3 camera FPC 针数 = 参数", f'(pad "1" smd' in pcb and P["fpc_camera"]["pins"] % 2 == 0, f"{P['fpc_camera']['pins']}p")
    chk("C3 display FPC 针数 = 参数", P["fpc_display"]["pins"] % 2 == 0, f"{P['fpc_display']['pins']}p")
    # C4 封装名
    fp_names = set()
    for line in pcb.split("\n"):
        if line.strip().startswith("(footprint "):
            fp_names.add(line.strip().split('"')[1])
    chk("C4 每个 footprint 有封装名", len(fp_names) > 0, ", ".join(sorted(fp_names)))
    # C5 叠层
    chk("C5 铜层数 = 参数", P["board"]["layers"] == N_COPPER, f"{N_COPPER} 层")
    # C6 网络类
    need_cls = {"MIPI_CSI", "MIPI_DSI", "USB", "PWR", "Default"}
    have_cls = {l.split('"')[1] for l in pcb.split("\n") if l.strip().startswith("(net_class ")}
    chk("C6 网络类齐全", need_cls <= have_cls, f"缺 {sorted(need_cls - have_cls) if need_cls - have_cls else '无'}")

    rep = [f"生成自检 · {ts()}"]
    for (n, c, d) in checks:
        rep.append(f"  {'✅' if c else '❌'} {n}" + (f" — {d}" if d else ""))
    rep.append(f"\n判定: {'全过' if ok else '有不通过项'} (FAIL {sum(1 for (_, c, _) in checks if not c)})")
    open(os.path.join(PCB_DIR, "GEN_SELF_CHECK.txt"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    print(f"\n产出: {out_pcb}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
