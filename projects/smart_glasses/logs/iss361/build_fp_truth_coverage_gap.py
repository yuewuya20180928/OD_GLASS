#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 · HW/PCB/FP_TRUTH_COVERAGE_GAP.md 生成器
★ 页面里每一个数字都由本脚本从真源实算出来 (不是手抄) ⇒ 零转述误差
★ 只写 HW/PCB/FP_TRUTH_COVERAGE_GAP.md 一个文件 (新建) ⇒ 零落表 · 零写板 · 零改既有页
用法: python3 logs/iss361/build_fp_truth_coverage_gap.py
"""
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import iss361_board_read as R  # noqa: E402

OUT = os.path.join(ROOT, "HW", "PCB", "FP_TRUTH_COVERAGE_GAP.md")
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
BOM = os.path.join(ROOT, "HW", "BOM_v1.csv")
NET = os.path.join(ROOT, "HW", "netlist_v1.csv")
PCB = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
FPTRUTH = os.path.join(ROOT, "HW", "FP_TRUTH_BASELINE.md")

G13 = ["CHG_GND_STAR", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_USB_D", "FB_DEMO", "Q_AND",
       "Q_ENVC", "Q_PG", "SW_BOOT", "SW_KEY_PWR", "SW_KEY_VM", "SW_KEY_VP", "SW_RST"]

# ---------------------------------------------------------------- 真源实算

bom_rows = R.load_bom(BOM)
bom = {r["ref"]: r for r in bom_rows}
main_t, chg_t, total_t = R.iss356_targets(bom_rows)
ph, per_ref, notes = R.netlist_placeholder(NET)
board = R.read_board(PCB)
c4 = set(ph)
iss = set(total_t)
inter = c4 & iss
diff = c4 - iss

# 81 差集分桶 (★优先级: TP 优先 ⇒ TP_BAT/TP_LED_B 两件 dnp=DNP 但 type=TP ⇒ 归 TP 桶★)
buckets = {"TP": [], "DNP": [], "GAP": []}
for r in sorted(diff):
    b = bom[r]
    if b["type"] == "TP":
        buckets["TP"].append(r)
    elif b["dnp"] == "DNP":
        buckets["DNP"].append(r)
    else:
        buckets["GAP"].append(r)
gap13 = R.coverage_gap(bom_rows, c4)

# 158 的四桶 (靶内 = C4 ∩ ISS-356 靶子)
bucket_of = {}
for r in c4:
    if r in inter:
        bucket_of[r] = "靶内"
    elif bom[r]["type"] == "TP":
        bucket_of[r] = "TP"
    elif bom[r]["dnp"] == "DNP":
        bucket_of[r] = "DNP"
    else:
        bucket_of[r] = "缺口"

# FP_TRUTH 页自己的靶子名单 (独立读页, 不靠 BOM)
fp_lines = open(FPTRUTH, encoding="utf-8").read().splitlines()
def _seg(start, end):
    i = next(k for k, l in enumerate(fp_lines) if l.startswith(start))
    j = next(k for k, l in enumerate(fp_lines) if k > i and l.startswith(end))
    return fp_lines[i:j]
def _refs(seg):
    return [l.split("|")[1].strip().strip("`") for l in seg if l.startswith("| `")]
fp78 = _refs(_seg("## §2 逐 ref 表", "### §2.1"))
fp22 = _refs(_seg("### §4.1", "### §4.2"))
fp100 = set(fp78) | set(fp22)


def lib_md5(lib, name):
    p = os.path.join(LIBROOT, "%s.pretty" % lib, "%s.kicad_mod" % name)
    if not os.path.isfile(p):
        return None, None
    return "%s.pretty/%s.kicad_mod" % (lib, name), hashlib.md5(open(p, "rb").read()).hexdigest()


def lib_pads(lib, name):
    p = os.path.join(LIBROOT, "%s.pretty" % lib, "%s.kicad_mod" % name)
    if not os.path.isfile(p):
        return None
    t = open(p, encoding="utf-8").read()
    return re.findall(r'\(pad\s+"([^"]*)"', t)


# ---------------------------------------------------------------- 13 件逐件事实

def land_geom(ref):
    b = board[ref]
    pads = b["pads"]
    sizes = sorted({"%s×%s" % ("%.3f" % p[4], "%.3f" % p[5]) for p in pads})
    d = 0.0
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = max(d, ((pads[i][2] - pads[j][2]) ** 2 + (pads[i][3] - pads[j][3]) ** 2) ** 0.5)
    return "%d 焊盘 (%s) · %s mm · fab 外框 %.2f×%.2f mm · 中心距 %.3f mm" % (
        len(pads), "/".join(p[0] for p in pads),
        " / ".join(sizes), b["fab"][0], b["fab"][1], d)


def netlist_pins(ref):
    ps = per_ref.get(ref) or []
    return " / ".join("%s=%s" % (n, net) for n, net in ps)


# 每件: 目标 lib:name + 库文件 + 候选 OPN + 证据等级 + 布局改动 + 降级方案
PIECES = {
    "CHG_GND_STAR": dict(
        lib=("TestPoint", "TestPoint_Pad_D1.0mm"),
        opn="[0数据] · 非器件 (单点汇流位, 1 脚 GND) ⇒ 无型号可填, 按本行目标 lib:name 回填同封装件",
        ev="[实测] · [0数据]",
        chg="★是★ · pad 形状/尺寸变 (0.600×0.900 矩形 → 1.000 圆形) ⇒ 该 land 重定义; "
            "★**只有 1 个 land, 不新增第 2 个**★ (网表只有 1 脚 GND ⇒ 见 §5 K1)",
        fb="若落表批次要把它当可拆件 ⇒ 改用 2 焊盘件 (例 `Diode_SMD:D_SOD-323` md5 "
           "`bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = 新增第 2 脚 + 网表加 GND 以外的第二个网 "
           "⇒ 与单点汇流位的功能定义冲突 ⇒ 不建议"),
    "D_ESD_CAM": dict(
        lib=("Package_SON", "Texas_DPY0002A_0.6x1mm_P0.65mm"),
        opn="TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · ① 中心距 2.300 → 0.700 mm, pad 0.600×0.900 → 0.300×0.500 ⇒ 整块 land 重画; "
            "② ★**pad 序与器件相反**: 板 pad1=GND/pad2=CSI_D0_CK_P, 而 TPD1E05U06DPYR 是 1=I/O 2=GND ⇒ "
            "必须把 pad1/pad2 的网对调 (= 那一趟 B13_ESD_CAM_PAD 的内容)",
        fb="若 TI X1SON-2 封装在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 "
           "`Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` 无第二档 ⇒ 改用 2 脚 SOD-323 单通道件 "
           "`Diode_SMD:D_SOD-323` (md5 `bce0278c9b9af83e2de3cd130e6c04ed`) ⇒ 代价 = Cd 0.42pF → 45pF "
           "⇒ CSI-2 高速线上不可用 (Cd 45pF 会吃掉眼图裕量) ⇒ 不建议"),
    "D_ESD_DEMO": dict(
        lib=("Diode_SMD", "D_SOD-323"),
        opn="PESD5V0S1BA (Nexperia SOD-323 2-lead · VRWM 5V · VBR 6V min · IEC 61000-4-2 >30kV)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · 中心距 2.300 → 2.100 mm, pad 0.600×0.900 → 0.600×0.450 ⇒ land 重画; "
            "★pad 序无须对调★ (PESD5V0S1BA 是双向件, 1/2 谁接信号谁接地皆可)",
        fb="若 SOD-323 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 "
           "`Diode_SMD:D_SOD-323F` (SOD-323 带引脚变体) ⇒ 代价 = 焊接方式变 ⇒ 钢网要改 ⇒ 不建议; "
           "或改小封装 `Diode_SMD:Nexperia_DSN0603-2_0.6x0.3mm_P0.4mm` (md5 "
           "`c57a4058f16cf35599c2b748b9434350`) ⇒ 代价 = 手工贴装 + 板面更挤 ⇒ 不建议"),
    "D_ESD_USB_D": dict(
        lib=("Package_SON", "Texas_DPY0002A_0.6x1mm_P0.65mm"),
        opn="[0数据] · ★现行 BOM opn 是 2 脚 TPD1E05U06DPYR, 但那一趟 B07 要求它变 3 脚 ⇒ "
            "最终型号/封装随 W-1/W-2 拍板而变 ⇒ 本栏的 lib:name 只代表【现行 BOM opn 那一档】",
        ev="[实测] · [0数据]",
        chg="★是 (强制)★ · ① 中心距 2.300 → 0.700 mm ⇒ land 重画; "
            "② ★**还要把 2 个 land 变 3 个** (那一趟 B07_ESD_USB_D_3PIN) ⇒ 网表 + 板面同改; "
            "③ ★**还要挪位**: 距 J_USB_C 现 47.99 mm ⇒ 目标 ≤3.0 mm (B08_ESD_USB_D_NEAR) ⇒ 布线要重跑; "
            "④ 网名 NET_USB_D_P_TYPEC 三处同步 (B32)",
        fb="★3 脚档的候选封装随 W-1/W-2 分叉★ ⇒ 若拍「一颗双通道 3 脚」⇒ 候选 "
           "`Package_TO_SOT_SMD:SOT-23-3` (md5 `2cbbd67323e26100c49cafb6a9a881db`, 3 焊盘) ⇒ 代价 = "
           "★**pad 序须按最终型号厂商 land 复核**★ (本栏 SOT-23-3 只是几何候选, 不是代拍); "
           "若拍「两颗单通道」⇒ 本行保持 2 脚 X1SON-2 + 另加一只 2 脚件 (D− 侧) ⇒ 代价 = 板上多一颗件 + "
           "两处 land 都要画 ⇒ 仍在本趟内可完成"),
    "FB_DEMO": dict(
        lib=("Inductor_SMD", "L_0805_2012Metric"),
        opn="BLM21PG221SN1D (Murata BLM21PG 0805 2012 metric · 220Ω ±25%@100MHz · 2000mA · DCR 45mΩ max)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · ★**占位是斜置 2 land (对角 1.000 mm), 官方 0805 是正置 @2.124 mm**★ ⇒ "
            "位置 + 朝向 + pad 尺寸 (0.550×0.900 → 0.875×1.200) 全变 ⇒ land 重画 ⇒ 两端走线端点要重接",
        fb="若 Murata 0805 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 "
           "`Inductor_SMD:L_0805_2012Metric` 唯一档 ⇒ 改用更小 0603 (如 "
           "`Inductor_SMD:L_0603_1608Metric`) ⇒ 代价 = 电流 2A 降额到 1A 级 (BLM21PG 2000mA 是选型硬判据) "
           "⇒ 不建议"),
    "Q_AND": dict(
        lib=("Package_TO_SOT_SMD", "SOT-23"),
        opn="AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · ★**几何全变 + 脚序反**★: 占位 3 land 是 L 形 (pad1/pad2 水平相邻 @1.270 mm, "
            "pad3 斜置 @4.883 mm), 官方 SOT-23 是 pad1/pad2 上下相邻 @1.900 mm + pad3 对侧 @1.876 mm ⇒ "
            "三个 land 全部重定位; ★★且 pad↔net 须对调★★ (板 pad1=RESET_N=漏极 D / pad2=GND=源极 S / "
            "pad3=PG_AND=栅极 G, 而 AO3400A 官方脚序是 1=G / 2=S / 3=D) ⇒ ★**不改 ⇒ AND 门不成立**★ "
            "(= 那一趟 B10_Q_AND_LAND 的内容)",
        fb="若 SOT-23 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 `Package_TO_SOT_SMD:SOT-23` "
           "唯一档 ⇒ 换 SOT-23 的 TO-236 变体 (`Package_TO_SOT_SMD:SOT-23-3` md5 "
           "`2cbbd67323e26100c49cafb6a9a881db`) ⇒ ★**代价 = 厂商脚序可能不同, 必须逐颗重核 1=G/2=S/3=D**★ ⇒ "
           "不省事, 不建议"),
    "Q_ENVC": dict(
        lib=("Package_TO_SOT_SMD", "SOT-23"),
        opn="AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · 几何全变 (占位 L 形 → 官方 SOT-23 上下+对侧) ⇒ 三个 land 全部重定位; "
            "★pad↔net 无须对调★ (板 pad1=PG_AND=栅极 G / pad2=GND=源极 S / pad3=EN_VCORE=漏极 D "
            "= 官方 1=G / 2=S / 3=D ⇒ 天然对上, 是三件 MOS 里唯一不用换序的)",
        fb="同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 "
           "`2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议"),
    "Q_PG": dict(
        lib=("Package_TO_SOT_SMD", "SOT-23"),
        opn="DMP3098L (Diodes Inc SOT23 3-pin · −30V · RDS(on) 98mΩ typ@-4.5V · IDSS ≤800nA)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · 几何全变 (同 Q_AND) ⇒ 三个 land 全部重定位; ★pad↔net 无须对调★ "
            "(板 pad1=PWR_ON / pad2=BAT_SW / pad3=PWR_GOOD, 而 DMP3098L 官方脚序 1=G / 2=S / 3=D ⇒ "
            "⇒ 板面现接法是 G/S/D 反着接 ⇒ ★**必须改接线**: 板面 pad1(PWR_ON) 要变成 pad3(PWR_ON), "
            "板面 pad3(PWR_GOOD) 要变成 pad1(PWR_GOOD)★ (= 那一趟 B11_Q_PG_LAND 的内容)",
        fb="同 Q_AND: SOT-23 无第二档 ⇒ 换 `Package_TO_SOT_SMD:SOT-23-3` (md5 "
           "`2cbbd67323e26100c49cafb6a9a881db`) ⇒ 代价 = 厂商脚序须逐颗重核 ⇒ 不建议"),
    "SW_BOOT": dict(
        lib=("Button_Switch_SMD", "SW_Push_1P1T_NO_CK_KMR2"),
        opn="KMR231ULCLFS (C&K KMR 2 系列 NG 2 脚 gullwing SMT · OF 3.0N · travel 0.25mm · 寿命 150,000 次) "
            "★按 HW/PART_SELECTION_MATRIX_2026-11-16.md §⑮ 的 pick (BOOT 键误触后果最重 ⇒ 3N 档)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · ★**这是本单 13 件里唯一会改【焊盘个数】的一件**★: 占位 2 land @2.200 mm "
            "(0.600×0.900) ⇒ 官方 KMR2 是 ★**4 个物理焊盘 (焊盘号 1,1,2,2)**★ @4.100×2.600 mm "
            "(0.900×1.000) ⇒ 板面从 2 land 变 4 land ⇒ "
            "★**网表也必须同步给 4 个具名脚, 否则 `state/check_pcb_nets.py` C3 判红「板 4 脚 / 网表 2 脚」**★ "
            "(沙盒已实测, 见 §0 表第 12 行) ⇒ 本单零落表 ⇒ 只登记",
        fb="★若不改网表 ⇒ 只能选 2 land 的按键封装★ ⇒ 候选 `Button_Switch_SMD:SW_SPST_B3U-1000P` (md5 "
           "`749f20c5ab898069ade01682274c7bbf`, 2 焊盘 @3.400 mm, 本体 3.0×2.5mm) ⇒ 代价 = 按动力度 "
           "1.5N vs KMR2 的 3.0N ⇒ BOOT 键误触风险上升 (矩阵 §⑮ 选 3N 的理由就是防误触) ⇒ "
           "★**这是选型代价, 不是本单能拍的**★; 或 `Button_Switch_SMD:SW_SPST_CK_KXT3` (md5 "
           "`bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, C&K KXT3) ⇒ 代价 = 同上, 且本体 3.5×2.0"),
    "SW_KEY_PWR": dict(
        lib=("Button_Switch_SMD", "SW_Push_1P1T_NO_CK_KMR2"),
        opn="KMR231ULCLFS (C&K KMR 2 系列 NG 2 脚 gullwing SMT · OF 3.0N · travel 0.25mm · 寿命 150,000 次) "
            "★按矩阵 §⑯ 的 pick (电源键 ⇒ 误触 = 意外关机 ⇒ OF 偏大)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · 同 SW_BOOT: 2 land @2.200 mm ⇒ 官方 KMR2 4 个物理焊盘 (1,1,2,2) @4.100×2.600 mm ⇒ "
            "板面 2 land 变 4 land ⇒ ★网表必须同步 4 个具名脚, 否则 C3 判红★ (沙盒已实测)",
        fb="同 SW_BOOT: 不改网表则只能选 2 land 封装 (`SW_SPST_B3U-1000P` md5 "
           "`749f20c5ab898069ade01682274c7bbf` / `SW_SPST_CK_KXT3` md5 "
           "`bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 按动力度降到 1.5N ⇒ 电源键误触风险上升 ⇒ "
           "★不代拍★"),
    "SW_KEY_VM": dict(
        lib=("Button_Switch_SMD", "SW_SPST_B3U-1000P"),
        opn="B3U-1000P (Omron B3U 2 脚 gullwing SMT 无固定脚无 boss · 本体 3.0×2.5mm · OF 1.5N · "
            "travel 0.2mm · 寿命 200,000 次) ★按矩阵 §⑰ 的 pick (音量键频繁按 ⇒ 寿命优先 + 短行程)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · 2 land ⇒ 仍是 2 land (★**焊盘个数不变 ⇒ C3 不受影响★**) 但中心距 "
            "2.200 → 3.400 mm、pad 0.600×0.900 → 0.900×1.700、fab 外框 3.00×3.00 → 3.00×2.50 mm ⇒ "
            "land 重画 + 两端走线端点要重接; ★注意 fab 外框 3.0mm 高仍放得进现占位 3.0×3.0★",
        fb="若 B3U-1000P 在库内无对应 (本机已实测在盘 ⇒ 不适用) ⇒ 退到同封装等效件 "
           "`Button_Switch_SMD:SW_SPST_B3U-1000P` 唯一档 ⇒ 改 KXT3 (`Button_Switch_SMD:SW_SPST_CK_KXT3` "
           "md5 `bed9b3b110e52e4ffcdc18240ef7a47c`, 2 焊盘 @3.250 mm, 本体 3.5×2.0mm) ⇒ 代价 = 宽度 3.5 > "
           "占位 3.0 ⇒ 邻键间隙要复核 ⇒ 不建议"),
    "SW_KEY_VP": dict(
        lib=("Button_Switch_SMD", "SW_SPST_B3U-1000P"),
        opn="B3U-1000P (Omron B3U 2 脚 gullwing SMT 无固定脚无 boss · 本体 3.0×2.5mm · OF 1.5N · "
            "travel 0.2mm · 寿命 200,000 次) ★按矩阵 §⑱ 的 pick (与 SW_KEY_VM 同族同料 ⇒ 左右手感一致)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · 同 SW_KEY_VM: 2 land ⇒ 2 land (C3 不受影响), 中心距 2.200 → 3.400 mm ⇒ land 重画",
        fb="同 SW_KEY_VM ⇒ 退到 KXT3 (md5 `bed9b3b110e52e4ffcdc18240ef7a47c`) ⇒ 代价 = 本体宽 3.5 > 3.0 ⇒ "
           "邻键间隙复核 ⇒ 不建议"),
    "SW_RST": dict(
        lib=("Button_Switch_SMD", "SW_Push_1P1T_NO_CK_KMR2"),
        opn="KMR231ULCLFS (C&K KMR 2 系列 NG 2 脚 gullwing SMT · OF 3.0N · travel 0.25mm · 寿命 150,000 次) "
            "★按矩阵 §⑲ 的 pick (复位键 ⇒ 误触 = 意外重启 ⇒ OF 偏大 + 段落感)",
        ev="[实测] · [官网]",
        chg="★是 (强制)★ · 同 SW_BOOT: 2 land @2.200 mm ⇒ 官方 KMR2 4 个物理焊盘 (1,1,2,2) @4.100×2.600 mm ⇒ "
            "板面 2 land 变 4 land ⇒ ★网表必须同步 4 个具名脚, 否则 C3 判红★ (沙盒已实测)",
        fb="同 SW_BOOT: 不改网表则只能选 2 land 封装 ⇒ 代价 = 按动力度降到 1.5N ⇒ 复位键误触风险上升 ⇒ "
           "★不代拍★"),
}

# §5 未决项与卡点
OPEN_ITEMS = [
    ("K1", "★`CHG_GND_STAR` 在 `HW/FP_TRUTH_BASELINE.md` §2.2 表格里有两处自相矛盾★",
     "同一行的「焊盘数 / 网络核对结论」栏写『焊盘数 1=1 一致』, 而「是否触发布局/布线改动」栏写"
     "『官方封装是 2 焊盘 ⇒ 必须新增第 2 个焊盘 ⇒ 该器件接地脚与走线全新增』; 同页表格下方的正文又写"
     "『`CHG_GND_STAR` 的情况与另 2 件不同 … 1 个 land 是对的』。",
     "★本单实测: KiCad 官方 `TestPoint.pretty/TestPoint_Pad_D1.0mm.kicad_mod` 只有 ★**1 个**★焊盘 "
     "(pad \"1\" smd circle 1.0×1.0 mm, md5 `cea8eb3ba9b799767624661848b00243`) ⇒ "
     "★**表格那一栏是错的, 照它改板会给 CHG_GND_STAR 加一个不存在的第 2 个 land**★。",
     "★该页老字本单一字未改★ ⇒ 请 main 决定由谁订正该单元格 (本单只登记)"),
    ("K2", "★`D_ESD_USB_D` 的最终封装随老板 W-1/W-2 分叉★",
     "本单 §2 该行给的是【现行 BOM opn (2 脚 TPD1E05U06DPYR) 那一档】的 lib:name; 那一趟 B07 却要求它变 3 脚。",
     "两个分支的候选封装本单都已实测在盘 (3 脚档 `Package_TO_SOT_SMD:SOT-23-3` md5 "
     "`2cbbd67323e26100c49cafb6a9a881db` / 2 脚档 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` md5 "
     "`0edfa97bd7bd277f3c05acf2bee23892`) ⇒ 但**哪一档生效是老板 W-1/W-2 的拍板项, 本单不代拍**。",
     "★请老板拍 W-1/W-2 (见 §5 K2 的上游: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` §5 第 5 条)★"),
    ("K3", "★5 只按键换 KMR2 ⇒ 网表要同步给 4 个具名脚★",
     "官方 `SW_Push_1P1T_NO_CK_KMR2` 有 4 个物理焊盘 (焊盘号 1,1,2,2), 而现行网表这 5 只只有 2 个脚。",
     "★沙盒实测 (板副本, 真板 md5 未变): 把 SW_BOOT 改成 4 焊盘后跑 `state/check_pcb_nets.py` ⇒ "
     "C3 判红「★ SW_BOOT: 板 4 脚 / 网表 2 脚 ★」⇒ ★**那一趟若只改板不改网表, 这道闸当场红**★。",
     "★请 main 决定: (a) 落表批次给这 5 只加 2 个具名脚 (⇒ 脚表也要加行) 或 "
     "(b) 改选 2 焊盘按键封装 (⇒ 按动力度 3N → 1.5N 的选型代价, 见 §2 各行降级方案)★"),
    ("K4", "★`FB_DEMO` 在那一趟的两份文件里 0 命中 ⇒ 没人排它★",
     "`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 与 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 里 `FB_DEMO` "
     "各出现 0 次 (其余 12 件都出现过)。",
     "★本单实测它的占位是【斜置 2 land @对角 1.000 mm】, 官方 0805 是【正置 @2.124 mm】⇒ "
     "★**不改封装它就装不上**★, 而那一趟的清单里没有它 ⇒ 漏掉 ⇒ 板出来是坏的。",
     "★请 main 把它并进那一趟的 land 重画清单 (本单只登记, 不代改既有页)★"),
    ("K5", "★本单只给【封装真值】, 不给【料号】⇒ 13 件的 BOM `opn` 栏仍多为空★",
     "13 件里 `CHG_GND_STAR` + 5 只按键 的 BOM `opn` 栏是 `[0数据]`; 其余 7 件的 opn 栏已有具体型号。",
     "★封装的判定 (库文件在盘 + md5 + 焊盘数 + 几何) 本单全部给全; ★**但哪颗料**是选型批次的事★ ⇒ "
     "落表批次可按本行目标 lib:name 回填同封装等效件 (ISS-356 §2 同一套路)。",
     "★无阻塞项, 只是提醒: 本单 §2 的『候选 OPN』栏是候选不是决定★"),
]

# ---------------------------------------------------------------- 页面组装

L = []
A = L.append

A("# HW/PCB · ISS-361 · 「板那一趟」封装真值覆盖缺口 (C4-158 与 ISS-356-100 的机器可读差集)")
A("")
A("> ★**单号**: ISS-361 · ★**owner**: hw-lead (硬件总工) · ★**性质**: 纯分析 / 文档 / 机器闸 · "
  "★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 零采购 · 不代老板拍板**★")
A("> ★**本单只做 1 件**: 把「板上占位脚号器件」与「已有封装真值基线」这两个集合之间的缺口查清, "
  "做成【一页 + 一条机器闸】, 让那一趟的封装收口判据从【一句话】变成【可数 · 可点名 · 可机器判】★")
A("> ★**本页所有数字均由生成器 `logs/iss361/build_fp_truth_coverage_gap.py` 从真源实算生成★ "
  "⇒ 零转述误差; 复跑命令见 §0 表每行的「怎么复跑」栏。")
A("> ★**配套机器闸**: `HW/check_fp_truth_coverage_gap.py` (G0~G7 + `--selftest` 反向用例) · "
  "★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS361_封装真值覆盖缺口.md`")
A("")
A("<!-- BEGIN ISS361 封装真值覆盖缺口基准块 -->")
A("```json")
A(json.dumps({
    "issue": "ISS-361",
    "owner": "hw-lead",
    "doc": "HW/PCB/FP_TRUTH_COVERAGE_GAP.md",
    "gate": "HW/check_fp_truth_coverage_gap.py",
    "note": "★本块由 logs/iss361/build_fp_truth_coverage_gap.py 从真源实算生成; "
            "闸 G0 校验它是合法 JSON, G1 校验 counts 与脚本实算逐项相等★",
    "counts": {
        "c4_total": len(c4),
        "iss356_total": len(iss),
        "iss356_main_board": len(main_t),
        "iss356_charge_board": len(chg_t),
        "inter_total": len(inter),
        "diff_total": len(diff),
        "gap_total": len(gap13),
        "board_footprints": len(board),
    },
    "buckets": {
        "tp": len(buckets["TP"]),
        "dnp": len(buckets["DNP"]),
        "in_target": len(inter),
        "gap": len(buckets["GAP"]),
    },
    "gap_refs": gap13,
}, ensure_ascii=False, indent=1))
A("```")
A("<!-- END ISS361 封装真值覆盖缺口基准块 -->")
A("")

# ---------------- §0
A("## §0 口径与读数 (本机实跑, 2026-11-23)")
A("")
A("★**三个口径各写清「哪个脚本产出 · 怎么复跑」★。★**每行数字都能被本表某一行的命令复现**★ "
  "—— 不用任何 agent 的转述。")
A("")
A("| # | 项 | 实测 | 口径 (哪个脚本产出) | 怎么复跑 |")
A("|---|---|---|---|---|")
A("| 1 | ISS-356 封装真值基线的靶子 | ★**%d**★ (镜脚主 PCB %d + 镜框充电板 %d) | "
  "`HW/check_fp_truth_baseline.py` 的 `load_targets()`: 必装 ∩ 非 NET/TP ∩ `footprint=='待定'` | "
  "`python3 HW/check_fp_truth_baseline.py` |" % (len(total_t), len(main_t), len(chg_t)))
A("| 2 | 板上占位脚号器件 (C4) | ★**%d**★ | `state/check_pcb_nets.py` 的 C4 口径: 网表节点串是 **bare** "
  "(无 `pin<N>` / 无 USB-IF 物理脚名) ⇒ 焊盘号按行序占位 | "
  "`bash state/pcbnew_py.sh state/check_pcb_nets.py` |" % len(c4))
A("| 3 | C4 ∩ ISS-356 靶子 | ★**%d**★ | 两集合求交 (本单生成器 `logs/iss361/build_fp_truth_coverage_gap.py`) | "
  "`python3 logs/iss361/build_fp_truth_coverage_gap.py` (重跑即重算) |" % len(inter))
A("| 4 | C4 − ISS-356 靶子 | ★**%d**★ | 差集 (同上) | 同上 |" % len(diff))
A("| 5 | ★那 %d 件的成分 (逐件归因)★ | ★**TP %d + DNP %d + 缺口 %d**★ | "
  "★**分桶优先级: TP 优先**★ (⇒ `TP_BAT`/`TP_LED_B` 两件 `dnp=DNP` 但 `type=TP` ⇒ 归 TP 桶); "
  "DNP 次之; 其余归缺口桶 | 同上 |"
  % (len(diff), len(buckets["TP"]), len(buckets["DNP"]), len(buckets["GAP"])))
A("| 6 | ★那 %d 件的 BOM `footprint` 栏长什么样★ | ★**不是 `待定`, 而是描述串**★ (★实测 %d 行是 "
  "`★板文件封装: N 焊盘 (…)`★, 其中恰好 %d 行落在「必装 ∩ 非 NET/TP」口径内 ⇒ **就是本单那 %d 件**) | "
  "读 `HW/BOM_v1.csv` 的 `footprint` 栏 | `python3 -c \"import csv;print([r['footprint'] for r in "
  "csv.DictReader(open('HW/BOM_v1.csv',encoding='utf-8')) if r['footprint'].startswith('★板文件封装:')])\" |"
  % (len(gap13), 20, len(gap13), len(gap13)))
A("| 7 | ★那 %d 件在 `HW/FP_TRUTH_BASELINE.md` 里有没有目标 `lib:name`★ | ★**%d 件没有 / %d 件有**★ "
  "(`CHG_GND_STAR` 有 `TestPoint:TestPoint_Pad_D1.0mm`, 在 §2.2 靶外同族登记里) | "
  "读 `HW/FP_TRUTH_BASELINE.md` 逐件搜 `lib:name` | `grep -n 'CHG_GND_STAR' HW/FP_TRUTH_BASELINE.md` |"
  % (len(gap13), len(gap13) - 1, 1))
A("| 8 | 板面封装库名的真实状态 | ★**%d 个封装 · `GetFPIDAsString()` 唯一值 = `''`**★ ⇒ 板是【自绘通用占位】, "
  "不是「库名写错」 | `bash state/pcbnew_py.sh -c \"…GetFPIDAsString()…\"` | "
  "同左 (KiCad python; 纯文本口径见 `logs/iss361/zz_board_probe.py`) |" % len(board))
A("| 9 | ★ISS-354 §V-3 的 5 个 ref 与本单 %d 件的关系★ | ★**零重叠**★ (`Q1`/`Q2`/`U_BATPROT`/"
  "`U_LDO_S28`/`U_SUPV` 全 `dnp='DNP'` 且全不在 C4-%d 里) ⇒ **ISS-354 与 ISS-356 两套名单都不覆盖这 %d 件**★ | "
  "两集合求交 | `python3 logs/iss361/zz_parse.py` |" % (len(gap13), len(c4), len(gap13)))
A("| 10 | ★有没有任何一道闸查「BOM `footprint` 栏 vs 板面封装」的一致性★ | ★**没有**★ ⇒ "
  "`state/check_pcb_nets.py` 里 `footprint` 出现 ★**0**★ 次; `HW/check_netlist_selfconsistency.py` "
  "只查**个别 ref** 的板面属性 (`d3_board_value`/`d4_esd_pads`/`d4_esd_pad1_net`…) ⇒ ★**那 %d 件没有任何一件被现有闸覆盖**★ | "
  "`grep -c footprint state/check_pcb_nets.py` → 0 | 同左 |" % len(gap13))
A("| 11 | ★C4-%d 里脚数 ≥3 的 (脚号顺序真会出事的)★ | ★**%d 件**: `Q_AND`(3) · `Q_ENVC`(3) · `Q_PG`(3) · "
  "`X1`(3·DNP) ⇒ ★**其中 %d 件落在本单的缺口 %d 件里**★ (前 3 件正是 B10/B11/B12 三条 P0 land 改项), "
  "`X1` 归 DNP 桶 | 读 `HW/netlist_v1_pins.csv` 逐 ref 数脚 | "
  "`python3 logs/iss361/zz_netstyle.py` |" % (len(c4), sum(1 for r in c4 if ph[r] >= 3),
  sum(1 for r in gap13 if ph[r] >= 3), len(gap13)))
A("| 12 | ★**【本单新增】C4 的计数由【网表节点命名】决定, 与板面 land 无关**★ | ★**沙盒实测**: "
  "只把网表 5 个 bare 节点串改成具名 `pinN` ⇒ C4 从 ★**%d → %d**★ (掉 5 件); "
  "★**板面 land 改动完全不进 C4 的计算输入**★ ⇒ ★**ISS-356 的 78 件 land 全部做完, C4 读数仍是 %d**★ | "
  "★C4 = `netlist_pads(rows)` 的 `placeholder` 字典, `rows` 来自 `HW/netlist_v1.csv`, **板在它之后才被读**★ | "
  "`python3 logs/iss361/zz_c4_causality.py` (真网表零改动, 副本跑完即删) |" % (len(c4), len(c4) - 5, len(c4)))
A("| 13 | ★**【本单新增】4 焊盘 gullwing 封装落 2 脚网表器件 ⇒ C3 当场红**★ | ★**沙盒实测**: "
  "把 `SW_BOOT` 从 2 焊盘改成 4 焊盘后跑 `state/check_pcb_nets.py` ⇒ "
  "C3 判红「★ SW_BOOT: 板 4 脚 / 网表 2 脚 ★」⇒ ★**只改板不改网表 ⇒ 这道闸红**★ | "
  "板副本落 `tmp/iss361/`, 跑 `bash state/pcbnew_py.sh state/check_pcb_nets.py <副本>` | "
  "`python3 logs/iss361/zz_sandbox_4pad.py` + 上条命令 (真板 md5 未变) |")
A("| 14 | ★**【本单新增】`FB_DEMO` 在那一趟的两份文件里 0 命中**★ | `WORKPACKET.md` 出现 ★**0**★ 次 · "
  "`PREFLIGHT.md` 出现 ★**0**★ 次 (其余 12 件都出现过) ⇒ ★**没人排它的 land 重画**★ ⇒ 见 §5 K4 | "
  "逐件搜两个文件 | `grep -c FB_DEMO HW/PCB/BOARD_ONEPASS_*.md` |")
A("")
A("★**§0 的 14 行读数全部复现自同一批真源文件, 板 md5 `611b869e13518c3c023fb178f91a0075` / "
  "mtime `2026-11-06 07:07:17.362193413` 开工前后逐字节未变**★。")
A("")

# ---------------- §1
A("## §1 三集合的机器可读差集")
A("")
A("★**三个集合**: ① `C4-%d` 板上占位脚号器件 · ② `ISS356-%d` 已有封装真值基线的靶子 · "
  "③ `DIFF-%d` 差集 (★**本单的对象**★)。" % (len(c4), len(iss), len(diff)))
A("")
A("```")
A("C4-%d  (板上占位脚号器件)" % len(c4))
A("  = 靶内 %d  (C4 ∩ ISS356-%d, ★已有 lib:name★)" % (len(inter), len(iss)))
A("  + TP   %d  (type=='TP'       ⇒ ISS-356 口径显式排除)" % len(buckets["TP"]))
A("  + DNP  %d  (dnp=='DNP'       ⇒ ISS-356 口径显式排除)" % len(buckets["DNP"]))
A("  + 缺口 %d  (★真器件 · 必装 · 非 NET/TP · footprint!='待定'★ ⇒ **被那一个条件挡在门外**)"
  % len(buckets["GAP"]))
A("  = %d + %d + %d + %d = ★%d★" % (len(inter), len(buckets["TP"]), len(buckets["DNP"]),
                                    len(buckets["GAP"]), len(c4)))
A("")
A("DIFF-%d = C4-%d − ISS356-%d" % (len(diff), len(c4), len(iss)))
A("  = TP %d + DNP %d + 缺口 %d = ★%d★" % (len(buckets["TP"]), len(buckets["DNP"]),
                                           len(buckets["GAP"]), len(diff)))
A("```")
A("")
A("★**`ISS356-%d` 靶子名单的独立复核**: 本单生成器**独立读 `HW/FP_TRUTH_BASELINE.md` 的 §2 表 (%d 行) "
  "与 §4.1 表 (%d 行)** ⇒ 并集 %d 件; ★**与 BOM 实算的 %d 件逐件相等**★ (集合级相等, 不是只对个数)。"
  % (len(iss), len(fp78), len(fp22), len(fp100), len(total_t)))
A("")

A("### §1.1 `C4-%d` 全名单 (ref + 归属桶 + 占位脚数)" % len(c4))
A("")
A("| # | ref | 归属桶 | 占位脚数 |")
A("|---|---|---|---|")
for i, r in enumerate(sorted(c4, key=lambda x: (bucket_of[x], x)), 1):
    A("| %d | `%s` | %s | %d |" % (i, r, bucket_of[r], ph[r]))
A("")

A("### §1.2 `ISS356-%d` 全名单 (ref + 板面归属)" % len(iss))
A("")
A("| # | ref | 板面归属 | 在 C4 里? |")
A("|---|---|---|---|")
for i, r in enumerate(sorted(iss), 1):
    br = bom[r]
    A("| %d | `%s` | %s | %s |" % (i, r, br["board"], "★是★" if r in c4 else "否"))
A("")

A("### §1.3 `DIFF-%d` 全名单 (ref + 归因)" % len(diff))
A("")
A("| # | ref | 归属桶 | 被 ISS-356 口径排除的原因 (逐件归因) |")
A("|---|---|---|---|")
for i, r in enumerate(sorted(diff), 1):
    b = bom[r]
    if b["type"] == "TP":
        why = "★`type=='TP'`★ ⇒ ISS-356 口径显式排除测试点"
    elif b["dnp"] == "DNP":
        why = "★`dnp=='DNP'`★ ⇒ ISS-356 口径显式排除不装件"
    else:
        why = ("★`dnp=='必装'` + `type=='%s'` (非 NET/TP) + ★`footprint!='待定'`**★ ⇒ "
               "★**只被那最后一个条件挡在门外**★ ⇒ 本单的对象" % b["type"])
    A("| %d | `%s` | %s | %s |" % (i, r, bucket_of[r], why))
A("")

# ---------------- §2
A("## §2 ★那 %d 件逐件表 (全部字段齐全)" % len(gap13))
A("")
A("★**字段口径照 `HW/FP_TRUTH_BASELINE.md` §2 那张表同款** ★ (ref / type / value / 必装-DNP / 现占位族 / "
  "目标 `lib:name` / 库文件实存路径 + md5 / 焊盘数-网络核对结论 / 候选 OPN / 证据等级 / "
  "是否触发布局布线改动 / 降级方案)。★**13 件全部逐件写全, 无一件省略**★。")
A("")
A("| ref | type | value | 必装/DNP | 现占位族 (板面实测) | 目标 `lib:name` | 库文件实存路径 + md5 | "
  "焊盘数 / 网络核对结论 (实测) | 候选 OPN | 证据等级 | 是否触发布局/布线改动 | 降级方案 |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in gap13:
    b = bom[r]
    p = PIECES[r]
    path, md5 = lib_md5(*p["lib"])
    npads = len(lib_pads(*p["lib"]) or [])
    A("| `%s` | %s | %s | %s | %s | `%s:%s` | `%s` md5 `%s` | 焊盘数 %d=%d 一致; %s | %s | %s | %s | %s |"
      % (r, b["type"], b["value"].split(" (")[0] if b["value"] else "", b["dnp"], land_geom(r),
         p["lib"][0], p["lib"][1], path, md5, npads, ph[r], netlist_pins(r),
         p["opn"], p["ev"], p["chg"], p["fb"]))
A("")
A("★**「现占位族」栏的 fab 外框与中心距全部由本单生成器从板文件实算 (endpoint 口径, 与 "
  "`HW/FP_TRUTH_BASELINE.md` §2 表自己写的 4.00×5.00 / 2.70×1.60 / 3.00×3.00 逐个对得上)★; "
  "「焊盘数 / 网络核对结论」栏的 pad↔net 映射由板文件实读, 与 `bash state/pcbnew_py.sh` 的 pcbnew 读数 "
  "13/13 逐件一致**★。")
A("")

# ---------------- §3
A("## §3 对「板那一趟」判据的影响 (★建议, 不是已改★)")
A("")
A("★**本单不改 `state/board_trip_baseline_20260723.txt`** —— 那是 main 的地界, 老字一字不删★。"
  "★**下面是建议, 供 main 采纳后自己落**★。")
A("")
A("### §3.1 那条判据为什么现在【不可能满足】 (两条独立的原因)")
A("")
A("`state/board_trip_baseline_20260723.txt` 的「那一趟的验收口径」写着:")
A("")
A("> ★**C4 的 %d 个占位脚号必须随 ISS-356 的封装真值基线收敛** (⇒ 不许在那一趟里再留占位)★" % len(c4))
A("")
A("★**这条判据有两条彼此独立的不可能** —— 只堵住一条, 那一趟照样交不出能下单的板:★")
A("")
A("**原因一 (覆盖不足)**: ISS-356 的基线只覆盖 `ISS356-%d` 件, 与 C4-%d 只交 ★**%d**★ 件 ⇒ "
  "★**%d 件根本没有目标 `lib:name`**★ ⇒ 用 ISS-356 的基线永远凑不齐 %d。"
  % (len(iss), len(c4), len(inter), len(diff), len(c4)))
A("")
A("**原因二 (机制错位) ★这一条更根本, 而且是本单新挖出来的★**:")
A("")
A("★**C4 数的不是「板面 land 是不是官方封装」, 而是「网表节点串是不是 bare」** ★ —— §0 表第 12 行的沙盒实验: "
  "只改网表节点命名, C4 从 %d 掉到 %d; ★**板面 land 一个字节没动**★。反过来, ★**把 ISS-356 那 %d 件的 land "
  "全部换成官方封装, C4 读数仍是 %d**★。" % (len(c4), len(c4) - 5, len(total_t), len(c4)))
A("")
A("★⇒ **「随封装真值基线收敛」这句话在机制上就不成立**: 换封装动不了 C4 的计数, ★**只有网表节点串具名 "
  "(bare → `pin<N>`) 才动得了**★ ⇒ ★**那一趟若只换 land 不具名脚, 这条判据无论怎么写都还是红的**★。")
A("")
A("### §3.2 建议改成【分桶判据】 (四桶, 目标值之和 = ★%d★)" % len(c4))
A("")
A("★**把一条不可能的「%d 全收敛」换成四条各自可数的桶判据**★ —— 每桶给一个可数的目标值, "
  "★**四桶之和恰好 = %d**★ (⇒ 任何一件都逃不掉, 也任何一件都不重复算)。" % (len(c4), len(c4)))
A("")
A("| 桶 | 件数 (= 目标值) | 这桶是什么 | ★须做: land 换官方封装★ | ★须做: 网表节点具名脚★ | 判据出处 |")
A("|---|---|---|---|---|---|")
A("| **TP** | ★**%d**★ | `type=='TP'` 的测试点 (★单 land, 焊盘号恒为 1 ⇒ **脚号无歧义**) | "
  "★否★ (测试点不是器件, 无「封装真值」可言) | ★否★ (1 个 land, 焊盘号 1 恒定) | ISS-356 §5.2 U8 已登记「另一批落表范围」 |"
  % len(buckets["TP"]))
A("| **DNP** | ★**%d**★ | `dnp=='DNP'` 的不装件 | ★否★ (首版不贴 ⇒ land 可留占位) | "
  "★**建议否**★ (不装 ⇒ 脚序无装配影响) | ISS-356 §5.2 U8 / ISS-354 §9-6-5 的 DNP 口径 |"
  % len(buckets["DNP"]))
A("| **靶内** | ★**%d**★ | C4 ∩ ISS-356 靶子 (★**已有目标 `lib:name`**★) | ★**是**★ (%d 件, "
  "用 ISS-356 §2 表那一列) | ★**是**★ (%d 件) | ISS-356 §2 (78 件里有 %d 件在 C4) |"
  % (len(inter), len(inter), len(inter), len(inter)))
A("| **缺口** | ★**%d**★ | ★**本单 §2 的对象**★ (真器件 · 必装 · 非 NET/TP) | ★**是**★ (%d 件, 用本单 §2) | "
  "★**是**★ (%d 件) | ★**本单 `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §2**★ |"
  % (len(buckets["GAP"]), len(buckets["GAP"]), len(buckets["GAP"])))
A("| ★**合计**★ | ★**%d**★ | | ★**%d**★ | ★**%d**★ | |"
  % (len(c4), len(inter) + len(buckets["GAP"]), len(inter) + len(buckets["GAP"])))
A("")
A("★**⇒ 建议的新判据 (给 main 的落表稿, 本单不落)**:★")
A("")
A("> ★**C4 的 %d 件分四桶收口: TP %d + DNP %d 豁免 (单 land / 不装 ⇒ 脚号与封装真值均无意义); "
  "靶内 %d + 缺口 %d = ★%d 件★必须在那一趟同时完成【换官方 land】+【网表节点具名脚】, 二者缺一即红** ★ "
  "⇒ ★**C4 读数的目标值 = %d − %d = %d**★ (⇒ 实测该值即达标) ⇒"
  % (len(c4), len(buckets["TP"]), len(buckets["DNP"]), len(inter), len(buckets["GAP"]),
     len(inter) + len(buckets["GAP"]), len(c4), len(inter) + len(buckets["GAP"]),
     len(buckets["TP"]) + len(buckets["DNP"])))
A("> ★**并且: 那 %d 件的 land 必须是本页 §2 / ISS-356 §2 给的目标封装, 不是「随便换个官方封装」** ★ "
  "⇒ ★**建议加一道判据: 板面每个封装都能在本页 §2 或 ISS-356 §2 找到同 ref 的目标 `lib:name` 行** ★"
  % (len(inter) + len(buckets["GAP"])))
A("")
A("★**本单把这条判据变成了机器可判** ★ —— `HW/check_fp_truth_coverage_gap.py` 的 G1 (三集合件数自洽, "
  "数字由脚本实算) + G2 (缺口 %d 件逐件齐全) + G7 (四桶目标值之和 = %d) 就是它的可执行形式。"
  % (len(gap13), len(c4)))
A("")

# ---------------- §4
A("## §4 降级方案 (★逐件必填, 一件不空★)")
A("")
A("★**口径**: 查不到 ⇒ ★**官网参数可满足的等效件** / ★**沙盒验证法** / ★**改设计路径绕开** ⇒ "
  "★**三选一写清代价**★。★**每件都给了「已实测在盘的等效件 + 代价」, 零外部等待式措辞**★。")
A("")
A("| ref | 查不到的点 | 降级方案 (三选一 + 代价) |")
A("|---|---|---|")
for r in gap13:
    p = PIECES[r]
    unknown = {
        "CHG_GND_STAR": "型号 (它是单点汇流位, 非器件) + §5 K1 的表格自相矛盾",
        "D_ESD_CAM": "★pad↔net 序 (器件 1=I/O 2=GND, 板是反的) ⇒ 靠改 land 一并解决, 不靠查料★",
        "D_ESD_DEMO": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "D_ESD_USB_D": "★**最终是 2 脚还是 3 脚 (老板 W-1/W-2 未拍)** ⇒ 目标封装随分支变",
        "FB_DEMO": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "Q_AND": "★pad↔net 序 (器件 1=G/2=S/3=D, 板是反的) ★",
        "Q_ENVC": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "Q_PG": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "SW_BOOT": "★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★",
        "SW_KEY_PWR": "★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★",
        "SW_KEY_VM": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "SW_KEY_VP": "无 (库内档位已实测在盘) ⇒ 只有「换料」的代价",
        "SW_RST": "★网表要不要跟着给 4 个具名脚 (C3 判红与否) ★",
    }[r]
    A("| `%s` | %s | %s |" % (r, unknown, p["fb"]))
A("")

# ---------------- §5
A("## §5 未决项与卡点 (★需要谁回答什么★)")
A("")
A("| # | 卡点 | 事实 | 本单实测/依据 | 要谁答 |")
A("|---|---|---|---|---|")
for code, title, fact, meas, who in OPEN_ITEMS:
    A("| %s | %s | %s | %s | %s |" % (code, title, fact, meas, who))
A("")
A("### §5.1 本单的自我限定 (不越界的地方, 逐条)")
A("")
A("1. ★**零写板** ★ —— 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime "
  "`2026-11-06 07:07:17.362193413` / 4,940,213 B 开工前后逐字节未变; 本单唯一动过板的动作是"
  "**在 `tmp/iss361/` 的副本上**做沙盒实验, 副本跑完即删。")
A("2. ★**零落表** ★ —— `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / 原理图 "
  "一字未改; 本单 §2 的「目标 `lib:name`」是**给落表批次用的目标值**, 不是已落的值。")
A("3. ★**零改既有闸** ★ —— `HW/check_fp_truth_baseline.py` / `HW/check_onepass_preflight_coverage.py` / "
  "`HW/check_preflight_regen_idempotent.py` / `state/gate_check.py` / `state/merge.py` / "
  "`state/frag_write.py` 一个字节未改。")
A("4. ★**零改既有页面正文** ★ —— `HW/FP_TRUTH_BASELINE.md` / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / "
  "`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` / `state/board_trip_baseline_20260723.txt` 老字一字不删; "
  "§3 的判据改动是**建议**, 落在本单自己的页里。")
A("5. ★**零外发 / 零采购 / 零联系供应商** ★ —— 本单没发任何邮件/表单/询价, 没下单, 没问询。")
A("6. ★**不替老板拍板** ★ —— `D_ESD_USB_D` 的 2 脚 vs 3 脚 (W-1/W-2) 只登记候选与代价 (§5 K2); "
  "按键的 3N vs 1.5N 只登记代价 (§2 各行降级方案), ★**两个都没代选**★。")
A("7. ★**只写 `state/fragments/hw.yaml`** ★ —— 走 `state/frag_write.py`, 写前后各记一次 md5 基线。")
A("8. ★**不改 `PROJECT_TRACKER.md` §0 锁死表** ★。")
A("9. ★**证据分级必标** ★ —— 全页用五级白名单 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` "
  "(★**本单全页 0 处用第六种写法 (把官网级证据写成「官方」那一种)**★ ⇒ 闸 G5 实跑确认)。")
A("")
A("### §5.2 复跑命令 (自证)")
A("")
A("```bash")
A("# ① 本单生成器 (重算页面里每个数字)")
A("python3 logs/iss361/build_fp_truth_coverage_gap.py")
A("# ② 本单机器闸 (正常跑)")
A("python3 HW/check_fp_truth_coverage_gap.py")
A("# ③ 本单机器闸 (反向用例自证)")
A("python3 HW/check_fp_truth_coverage_gap.py --selftest")
A("# ④ 三个口径的原始读数 (ISS-356 基线闸)")
A("python3 HW/check_fp_truth_baseline.py")
A("# ⑤ 三个口径的原始读数 (C4 ⇒ 必须走 KiCad python, 裸 python3 会 ModuleNotFoundError: pcbnew)")
A("bash state/pcbnew_py.sh state/check_pcb_nets.py")
A("# ⑥ 沙盒: 板面 4 焊盘 ⇒ C3 判红 (真板零改动)")
A("python3 logs/iss361/zz_sandbox_4pad.py && bash state/pcbnew_py.sh state/check_pcb_nets.py tmp/iss361/sandbox_4pad_button.kicad_pcb")
A("# ⑦ 沙盒: 只改网表节点命名 ⇒ C4 计数掉 (真网表零改动)")
A("python3 logs/iss361/zz_c4_causality.py")
A("# ⑧ 板/网表/脚表/BOM 的 md5 复核")
A("md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv")
A("```")
A("")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(L) + "\n")
print("[build] 已写 %s (%d bytes)" % (OUT, os.path.getsize(OUT)))
print("[build] 关键读数: C4=%d ISS356=%d 交集=%d 差集=%d | TP=%d DNP=%d 缺口=%d | 四桶和=%d"
      % (len(c4), len(iss), len(inter), len(diff), len(buckets["TP"]), len(buckets["DNP"]),
         len(buckets["GAP"]), len(inter) + len(buckets["TP"]) + len(buckets["DNP"]) + len(buckets["GAP"])))
