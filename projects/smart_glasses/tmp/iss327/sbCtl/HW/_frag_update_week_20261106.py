#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_frag_update_week_20261106.py —— 2026-11-06 周更新窗口的分片原子写 (hw-lead)

--------------------------------------------------------------------------------
沿用 2026-11-01 同一条路径: state/frag_write.py 的 update_fragment()
(tmp + fsync + os.replace) ⇒ ★**不是** open(path,"w")。

★**本单为什么要用 Python API 而不是纯 CLI**:
  CLI 的 --add-* 只支持追加, 本单还需要两件 CLI 做不到的事:
    ① **更新已有 answer 的 value** (rk3572_official_datasheet 上周先给了"官方上限[待核]"
       的占位, 本周拿到官方 datasheet 了 ⇒ 要把占位换成真答案; 追加第二条会让
       合并器把两条都挂上去, 口径打架)
    ② **补 needs 的 due / waiting_on** (窗口纪律: 新加的 due 必填, 缺 due 的
       历史欠账也补齐 ⇒ 零僵尸)

边界: 只改**自己的**分片 state/fragments/hw.yaml。不碰别人的分片 / STATE.yaml /
      PROJECT_TRACKER.md / issue_log.yaml (issue_log 走 state/_hw_week_iss.py 单独原子写)。

用法: python3 HW/_frag_update_week_20261106.py [--dry-run]
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

# ================================================================= 1. answers
# ★**本单最大的价值: 把 main 的 `rk3572_official_datasheet` 这条高危阻塞的占位答案换成真答案**
ANSWER_UPDATE = {
    ("rk3572_official_datasheet", "main"): {
        "value": (
            "★**官方 datasheet 就在项目库里** (HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf · 47页 · 2,414,580B · "
            "md5 c0e3763036e2f6a3e8a2f68f2254851d · PDF元数据 Author=Rockchip · CreationDate=2026-04-14) ⇒ "
            "**本项证据等级从 [媒体]/[模组厂口径] 升到 [官方]** (未发邮件/未联系代理, 走开源渠道)。"
            "你问的 5 项逐条有官方口径: "
            "① **封装** = FCCSP550L, 本体 **14.3×15.5mm**, 球 0.25mm, **球间距 0.42/0.52/0.65mm 混合**, 550 球, MSL3, SnAgCu, 98PCS/Tray; "
            "球阵列图 = Fig 2-2/2-3/2-4/2-5 (p.19-21, 已渲染成 PNG 存 HW/RK3572_PIN_TABLE/figs/) ⇒ "
            "★**ISS-128『pitch 未知 ⇒ 板面积账与逃线层数只能 [推算]』这个前提作废** (最小 pitch 0.42mm ⇒ 落在我们自己定的 "
            "『≥0.4mm 可行 / 0.35mm 极限 / ≤0.3mm 须 HDI』的可行区间) ⇒ **ISS-128 要按 0.42mm 重算**。"
            "② **ISP MP/s 上限** = ISP V3.5 **单通道 12M pixels**, 最大输入 **4096×3072**, 最小 264×264 ⇒ "
            "★**官方没有直接给 MP/s** ⇒ 我按官方像素能力算: 1080p60 = 124.4 MPix/s ⇒ **对 12M 单帧余量 82.7%** ⇒ "
            "★**Q03 的『余量 1.9% vs 50.7%』两个矛盾口径都不是 RK3572 的数 (那套按 RK3576 16M 算的) ⇒ RK3572 是第三个值 82.7%**。"
            "③ **DDR** = **单通道 32bit**, LPDDR4/4X-4266, LPDDR5/5X-5500, 最大 16GB ⇒ "
            "★**订正**: CHIP_SHORTLIST_EVIDENCE 里 RK3576 那句『官方框图标 216bit』**是 RK3576 不是 RK3572** ⇒ "
            "DDR 带宽账必须按 32bit 重算。"
            "④ **VO 官方口径** = **DSI TX 和 DP 都有**: HDMI/eDP TX **combo PHY** (HDMI v2.1 4K@60 + **eDP v1.3, "
            "compliant with DisplayPort v1.2, 4lane, HBR2 5.4Gbps/lane, 4K@60**) + **MIPI DSI-1.2 4lane ≤2.5Gbps/lane** + "
            "并行 RGB/BT.656/BT.1120 ≤1920×1080@60 + EBC; 且官方写明 『Each Video Port may connect to any of "
            "HDMI/eDP/DSI/PARA interface』 ⇒ ★**Q16 对 RK3572 = 两者都有** ⇒ ★**打掉 CHIP_SELECTION_DECISION §12『无 DP』"
            "那个 [媒体] 口径** ⇒ ★**『因为无 DP 所以要加桥接芯片』那条推理链要重写**。"
            "★**但边界必须说清**: eDP 是 DP 的嵌入式封装形态 (主链路+AUX+HPD, 无独立 DP 连接器) ⇒ "
            "**能直插标准 DP 口的物理器件 = [0数据]**, 要看 FET3572-C 模组把哪几根 TX 引出来 ⇒ **须查 SoM 引脚图, 不是查 SoC**。"
            "⑤ **SoC 域功耗官方口径** = ★**官方自己也是 TBD**: Table 4-1 热阻 ψJT/θJA/θJB/θJC **四行全 TBD**, "
            "只给了 Tj≤125℃ ⇒ ★**别把『找到官方 datasheet』误当成『功耗账有官方依据』** ⇒ ISS-077/ISS-130 的皮肤 43℃ 结论 "
            "证据等级维持 [推算]。★**另外查到有用的**: PMU **支持 23 个可分别上下电的电源域** (软件控制) + CPU 每个核独立电源域 ⇒ "
            "对 SW 的『关机/深睡』与 PM 的降功耗有正面价值; 各轨推荐电压 Table 3-2 全有 (CPU_BIG_DVDD 0.675/0.75/**1.0**V, "
            "NPU_DVDD ≤0.918V, LOGIC_DVDD ≤0.825V, DDRPHY_VDDQ ≤0.95V)。"
            "★**本单没改任何网表/BOM/板** (只读 datasheet + 写事实卡) ⇒ 零投板风险。"
        ),
        "ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md (全文 8 节) + HW/rk3572_official_facts_check.py (rc=0, 22/22 断言命中)",
    },
    ("iss148_rk3572_gpio0_vccio_domain_check", "sw-lead"): {
        "value": (
            "★**这条不用查了 —— 我在官方 datasheet 里查到了, 而且推翻了我们之前的推断**。"
            "官方 Table 3-1 (p.39) 的分组 (★**渲染图核对, 不是扁平文本猜** ⇒ "
            "HW/RK3572_PIN_TABLE/figs/p39_gpio_crop2.png): "
            "① `1.8V only GPIO supply voltage` = **PMUIO0_VCC1V8 + VCCIO0_VCC1V8** (max **1.98V**) "
            "② `1.8V/3.3V GPIO supply voltage` = **PMUIO1_VCC + VCCIO1_VCC + VCCIO2_VCC + VCCIO3_VCC + "
            "VCCIO4_VCC + VCCIO5_VCC + VCCIO6_VCC** (max **3.63V**) "
            "③ `1.2V/1.8V supply voltage` = **VCCIO7_VCC** (max 1.98V)。"
            "★**⇒ 我 11-02 那条 need 里写的『VCCIO1_VCC 属 1.8V only ⇒ SoC 侧 GPIO0 只允许 1.98V』是错的** —— "
            "那是 **pdftotext -layout 把多行单元格错位**造成的排版假象 (★教训: 表格类断言不能靠文本层单点确认)。"
            "★**⇒ VCCIO1_VCC 能上 3.3V (max 3.63V) ⇒ I2C_A 走 3.3V 上拉在 SoC 侧不违规 ⇒ "
            "『整条 I2C_A 降 1.8V / 加电平转换』那条结论作废**。"
            "★**剩下什么没解决 (不夸大)**: datasheet **没有 GPIO bank → VCCIO 组的对应表** —— 它只说『VCCIO1_VCC 这个网名属于哪一档』。"
            "I2C0_SCL/SDA = **GPIO0_B0 (球 1K21) / GPIO0_B1 (球 U32)** (§2.6 引脚表 L1258-1260) ⇒ "
            "★**GPIO0_B0/B1 具体挂哪个 VCCIO 供电组 = [0数据]**, 仍须 SoM (FET3572-C) 的 IO 域文档或 BSP dtsi 佐证。"
            "★**⇒ 最终 I2C_A 上拉结论 = 2.8V, 但理由只剩 AR0234CS sensor 侧 abs-max 一条 (VIN ≤ VDD_IO+0.3 = 3.1V), "
            "SoC 侧那条不成立了**。"
        ),
        "ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md#5 + HW/RK3572_PIN_TABLE/figs/p39_gpio_crop2.png (p.39 渲染图) + HW/rk3572_official_facts_check.py",
    },
}

ANSWERS_NEW = [
    # ---- to mech-lead: 唯一一条还开着的 need ----
    {
        "key": "iss017_pcb_thickness_vs_service_port_clearance",
        "to": "mech-lead",
        "value": (
            "★**板厚档位我这边定了: demo 主板 = 8 层 1.600mm (总厚), 叠层 = PR2116 prepreg + FR4 core + ENIG, "
            "外铜 0.035 / 内铜 0.018** (已注入板文件, 规格书 HW/PCB/STACKUP_IMPEDANCE.md) ⇒ "
            "★**你的检修口净空公式代入后**: 7.30 − (0.80 皮肤壁 + 0.50 隔热垫 + 0.30 空气隙 + **1.60** 板厚) = **4.10mm** ⇒ "
            "**比你原来标 FAIL 的 1.22mm 情形还小 0.40mm** ⇒ ★**板厚 1.60 ⇒ 检修口净空只剩 4.10mm, 低于 ISS-085 的 4.50mm 判据**。"
            "★★**但这不影响你 B2 mock 板**: mock 板按的是**镜脚产品板**的档位, 不是 demo 主板 ⇒ "
            "★**镜脚产品板 = 6 层 1.00mm** (4 层在 4 组高速 + 62 net + 190 器件下无解) ⇒ 净空 = 7.30 − (0.80+0.50+0.30+**1.00**) = "
            "**4.70mm ≥ 4.50mm ✅** ⇒ ★**mock 板按 60×30×1.00mm 做, 检修口净空成立**。"
            "★**新增两个必须记的数**: ① 板重 = **3.33g** (60×30×1.00mm 6层), 旧口径 1.33g/1.67g 都作废; "
            "② ★**demo 主板 8 层 1.60mm 这个档位只对 demo 板成立, 别拿去当镜脚产品板** —— "
            "demo 板层数多是因为它要塞下 SoM 模组 + 190 器件的实验布局, **产品板层数要另外拍** "
            "(若产品板也上 8 层 ⇒ 镜腿 7.3mm 净高直接出局 ⇒ ★**这条是投板前必须由 PM/老板拍的一次**)。"
            "★**边界**: 层数/板厚档位属硬件侧, 我只交板厚数字 + 净空代入; "
            "**你的打印件与量测基准按 60×30×1.00mm (镜脚) / demo 板另算**。"
        ),
        "ref": "HW/PCB/STACKUP_IMPEDANCE.md + HW/PCB/demo_mainboard.kicad_pcb (setup/stackup 段) + HW/PCB_OUTLINE_60x15.md + HW/pcb60x30_check.json",
    },
]

# ================================================================= 2. interface_claims
CLAIM_UPDATE = {
    "rk3572_pkg_official": {
        "value": "FCCSP550L/14.3x15.5mm/550球",
        "note": "★2026-11-06 升级到 [官方]: Rockchip RK3572 Datasheet Rev 1.1 §1.2 Package Type + §2 Package Information "
                "(本地 PDF md5 c0e3763036e2f6a3e8a2f68f2254851d)。★旧值标 [媒体] (CHIP_SELECTION_DECISION §43 / CHIP_SCORING_RESULT §175) "
                "⇒ 本周实为 [官方]。★边界: 这是**裸 SoC 封装**, demo 主板用的是 SoM 模组的 BTB (0.4mm pitch) ⇒ 两条 pitch 不要混。",
        "ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md#1",
    },
    "rk3572_ddr_width": {
        "value": "32bit单通道",
        "note": "★2026-11-06 新增 [官方]: LPDDR4/4X-4266 + LPDDR5/5X-5500, **单通道 32 bits**, 最大 16GB (datasheet L216-219)。"
                "★**订正 CHIP_SHORTLIST_EVIDENCE 里 RK3576 的『216bit』—— 那是 RK3576 不是 RK3572** ⇒ DDR 带宽账按 32bit 重算。",
        "ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md#2",
    },
    "rk3572_isp_pixels": {
        "value": "12M/4096x3072",
        "note": "★2026-11-06 新增 [官方]: ISP V3.5 **单通道**, **12M pixels**, 最大输入 4096×3072, 最小 264×264 (datasheet L488-491)。"
                "★官方没直接给 MP/s ⇒ 按官方像素能力算: 1080p60 = 124.4 MPix/s ⇒ **余量 82.7%** ⇒ "
                "★**Q03 的『1.9% vs 50.7%』两口径都不是 RK3572 的数 (那套按 RK3576 16M 算)**。",
        "ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md#3",
    },
    "rk3572_vo_tx": {
        "value": "DSI-1.2+HDMI2.1+eDP1.3",
        "note": "★2026-11-06 新增 [官方]: **HDMI/eDP TX combo PHY** (HDMI v2.1 4K@60 + eDP v1.3 compliant-with-DP-v1.2, "
                "4lane HBR2 5.4Gbps/lane) + **MIPI DSI-1.2 4lane ≤2.5Gbps/lane** + 并行 RGB/BT.656/BT.1120 ≤1080p60 + EBC; "
                "官方写明每个 Video Port 可复用到 HDMI/eDP/DSI/PARA 任一。★**⇒ Q16 对 RK3572 = DSI 与 DP 都有** ⇒ "
                "★**打掉『RK3572 无 DP』那个 [媒体] 口径** (CHIP_SELECTION_DECISION §12) ⇒ "
                "★**但『能直插标准 DP 口』= [0数据]** (eDP 是嵌入式形态) ⇒ 须查 SoM 引脚图。",
        "ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md#4",
    },
    "rk3572_fccsp_ball_pitch": {
        "value": "0.42/0.52/0.65mm混合",
        "note": "★2026-11-06 新增 [官方]: **球间距 0.42mm & 0.52mm & 0.65mm 混合** (datasheet L827-828), 球尺寸 0.25mm, "
                "本体 14.3×15.5mm, 550 球。★**⇒ ISS-128『pitch 未知 ⇒ 板面积账/逃线层数只能 [推算]』的前提作废** ⇒ "
                "最小 pitch **0.42mm** ⇒ 按项目自己定的判据落在『≥0.4mm 可行』区间 ⇒ **ISS-128 要按 0.42mm 重算**。",
        "ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md#1",
    },
    "vccio_gpio_domain": {
        "value": "VCCIO1-6可上3.3V(max3.63V)",
        "note": "★2026-11-06 新增 [官方, 渲染图核对]: Table 3-1 (p.39) 分组 —— `1.8V only` = PMUIO0_VCC1V8 + VCCIO0_VCC1V8 "
                "(max 1.98V); `1.8V/3.3V` = PMUIO1_VCC + VCCIO1~6_VCC (max **3.63V**); `1.2V/1.8V` = VCCIO7_VCC (max 1.98V)。"
                "★**订正**: 11-02 我写『VCCIO1_VCC 属 1.8V only』是 **pdftotext 多行单元格错位**造成的假象 ⇒ SoC 侧 I2C_A "
                "上 3.3V 不违规 ⇒ 『整条 I2C_A 降 1.8V / 加电平转换』结论作废。"
                "★**边界**: datasheet **无 GPIO bank → VCCIO 组对应表** ⇒ I2C0 (GPIO0_B0/B1) 挂哪组 = [0数据] ⇒ 须查 SoM/BSP。",
        "ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md#5 + HW/RK3572_PIN_TABLE/figs/p39_gpio_crop2.png",
    },
    "rk3572_thermal_official": {
        "value": "热阻全TBD/Tj125C",
        "note": "★2026-11-06 新增 [官方]: Table 4-1 Package Thermal Characteristics 的 **ψJT / θJA / θJB / θJC 四行全是 TBD** "
                "⇒ ★**SoC 域功耗/热阻没有官方数字** ⇒ ISS-077 / ISS-130 的皮肤 43℃ 结论证据等级**维持 [推算]** ⇒ "
                "★**别把『找到官方 datasheet』误当成『功耗账有官方依据了』**。可用的只有 Tj≤125℃ + Storage −40~125℃ + "
                "**PMU 支持 23 个可分别上下电的电源域** (对 SW 关机/深睡有正面价值)。",
        "ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md#6",
    },
}

CLAIM_NEW = [
    {
        "key": "demo_board_unc",
        "value": "45",
        "note": "★2026-11-06 实测 (官方板 HW/PCB/demo_mainboard.kicad_pcb · md5 611b869e · 18092 段 / 433 孔): "
                "**unconnected = 45** (KiCad DRC JSON 的 unconnected_items 条数)。★目标 0 (G1 阶段门) ⇒ **未达标**。"
                "★本周实测结论: 45 条里 **23 条是 DSI/CSI 差分腿**, 器件参与 = CONN 21 / SOM_BTB 17 / RES 12 / CAP 10 / JST 5; "
                "★**几何真值**: SoM BTB **0.4mm pitch · 0.2mm 焊盘 ⇒ 相邻焊盘间隙仅 0.200mm** ⇒ "
                "0.20mm 线 + 两侧 0.20mm 净距 = 需 0.600mm > 0.400mm pitch ⇒ **沿排方向物理穿不过去** ⇒ "
                "★**这是物理约束不是算法问题** (自研 A* 与 freerouting 2.1.0 两个独立引擎撞同一堵墙 = 三重实证)。"
                "★**本周实测的三条真实前进**: ① 0.0625mm 网格阶梯 (0.125 → 0.0625) ⇒ **unc 45→42** 且退铜名单 0 / 差分死腿 0 / "
                "逐网孤岛不变多 (Δ 侧全部达标) ⇒ **只差 DRC 12→0**; ② v57 臂 (BTB 出脚线宽 0.20→0.15mm, 6mil 行业标准) ⇒ "
                "**REJECT** (DRC 115 = 108 条 track_width 板规则 0.2 vs 实际 0.15 + 7 条真 clearance; unc 60; 退铜 8 网; "
                "孤岛变多 17) ⇒ **单改线宽这条路判死**; ③ 0.15mm 线的 DRC 红**不是几何红是板规则红** ⇒ 须同时改板规则 + FAB 口径。",
        "ref": "HANDOFF/2026-11-06_hw-lead_周更新.md#B2 + state/compare_arm_official.py 名单制闸输出",
    },
    {
        "key": "demo_board_drc",
        "value": "0",
        "note": "★2026-11-06 实测 (官方板 fresh DRC): **violations = 0** (KiCad 10.0.8, --severity-error --severity-warning)。"
                "★**parity 板↔网表逐焊盘等价 = True** (check_pcb_nets rc=0, 缺失 0 / 多余 0 / 同号异网 0)。"
                "★**Gerber = 30 个** (HW/PCB/gerbers/) + 投产资料包 51 文件 (HW/PCB/production/)。★布了: USB 差分对 + "
                "15 条电源网 + L2/L6 完整 GND 平面 + GND 下拉通孔 + 14 条时序线 + CSI/DSI 差分主干。",
        "ref": "HANDOFF/2026-11-06_hw-lead_周更新.md#B2 + HW/PCB/ROUTING_REPORT.md",
    },
    {
        "key": "demo_board_parity",
        "value": "482/482逐焊盘等价",
        "note": "★2026-11-06 实测: 板↔网表**逐焊盘等价 482/482** (check_pcb_nets rc=0) ⇒ ★**布线不许改网表绑定这条守住了**。",
        "ref": "HW/PCB/ROUTING_REPORT.md + state/check_pcb_nets.py",
    },
    {
        "key": "demo_board_zero_copper",
        "value": "24",
        "note": "★2026-11-06 实测 (官方板): **零铜网 (≥2 焊盘但 0 段铜) = 24**。★这是判据里的**硬指标** (不许拿别的换) ⇒ "
                "★**任何候选板若零铜网数变多 ⇒ 直接拒** (v57 臂实测 24→27 ⇒ 拒)。",
        "ref": "state/compare_arm_official.py (名单制闸 · zero_copper)",
    },
    {
        "key": "demo_board_diff_half",
        "value": "11",
        "note": "★2026-11-06 实测 (官方板): **差分单边零铜对数 = 11**。★**这是判据里的硬指标** ⇒ "
                "★任何候选板若单边零铜对变多 ⇒ 直接拒 (v57 实测 11→9 看着更好, 但它同时把 8 个网打成零铜 ⇒ 净账更差 ⇒ 拒)。",
        "ref": "state/compare_arm_official.py (名单制闸 · diff_half)",
    },
    {
        "key": "demo_board_gerbers",
        "value": "30gerber+1drl+1gbrjob=32",
        "note": "★2026-11-06 实测: `HW/PCB/gerbers/` 共 **32 个文件** = **30 个 Gerber 图形** (F.Cu/B.Cu + In1~In6 + "
                "Mask/Paste/Silk/Fab/Edge/Margin/Courtyard/User×4) + **1 个钻孔 `.drl`** + **1 个作业 `.gbrjob`** "
                "(★**两者都不是图形层, 算图形的只有 30**) ⇒ 投产包 `HW/PCB/production/gerbers/` 同 32 个, `production/` 全目录 51 文件。",
        "ref": "HW/PCB/gerbers/ + HW/PCB/production/",
    },
]

# ================================================================= 3. needs (本周新增)
NEEDS_NEW = [
    {
        "key": "iss181_btb_escape_three_paths",
        "to": "main",
        "item": (
            "★**ISS-181 本周结论: 45 条未连接里 23 条是差分腿, 根因是物理约束不是算法** —— "
            "SoM BTB **0.4mm pitch · 0.2mm 焊盘 ⇒ 间隙 0.200mm**; "
            "0.20mm 线 + 两侧 0.20mm 净距 = 需 **0.600mm > 0.400mm pitch** ⇒ **沿排方向物理穿不过去**。 "
            "★**自研 A* 与 freerouting 2.1.0 两个独立引擎撞同一堵墙 (三重实证)** ⇒ **不是算法不够好**。"
            "★**三条出路, 按代价排序, 都需要设计变更 (要你拍板哪条)**: "
            "**① 改布局 (建议先做, 不动网表不动封装)** —— 挪 R_SEL/串阻/连接器腾出脚与走廊 "
            "(v56 实测: 只挪 R_SEL 而不挪配套 TP ⇒ 配套 TP 被挤到 y=8.80 正好堵在 BTB 焊盘排上方 0.84mm ⇒ 反而更差; "
            "★**⇒ R_SEL 与它的 TP 必须一起钉位**); "
            "**② 改封装** —— SoM BTB 换 dog-bone / 换 pitch (0.4 → 0.5mm) ⇒ ★**但 FET3572-C 模组是外购件 ⇒ "
            "换 BTB = 换模组或换转接板, 周期与成本要你核**; "
            "**③ 改工艺** —— BTB 出脚线宽 0.20 → **0.15mm (6mil, 行业标准, 板厂几乎都能做)** ⇒ "
            "★**但实测这一条单独走不通**: v57 臂 DRC=115 (108 条 track_width 是**板规则** 0.2 vs 实际 0.15 + 7 条真 clearance) "
            "⇒ **必须同时改板规则 min_width + FAB_ORDER_NOTES 的 0.20mm 口径**, 不是只改路由器。"
            "★**另有一条好消息**: 0.0625mm 网格阶梯已把 **unc 45→42** 且**零退铜/零差分死腿/零孤岛变多** "
            "⇒ ★**只差把 DRC 12 条清零就能晋级** ⇒ ★**这是本周离『可下单』最近的一步** ⇒ 请给路线拍板 + 板规则/工艺变更的批准。"
        ),
        "since": "2026-11-06",
        "due": "2026-11-09",
    },
    {
        "key": "iss181_fab_min_width_decision",
        "to": "main",
        "item": (
            "★**投板工艺参数需拍板 (零板费, 但要板厂确认)**: ① **最小线宽 0.20 → 0.15mm (6mil)** —— "
            "BTB 出脚线宽, ★**这是 45 条里 23 条差分腿能否出来的物理前提** (0.4mm pitch 下 0.20mm 线余量 = 0.0000mm, "
            "0.15mm 余量 = 0.0250mm); ② **板规则 min_width 同步改 0.15** (否则 KiCad DRC 报 track_width 红 —— "
            "v57 实测 108 条, ★**这是规则红不是几何红**); ③ **最小净距维持 0.20mm 不动** (不动就是稳妥); "
            "④ **FCCSP 球间距 0.42/0.52/0.65mm 混合** ⇒ 裸 SoC 逃线落在『≥0.4mm 可行』区间 ⇒ **不需要 HDI** ⇒ "
            "§0『4-6 层』锁死**不需要为此破例**。★**本单未改任何 FAB 文件/板规则** (改要跟板厂确认, 且超出本单边界) "
            "⇒ 请拍板后由项目总工转达板厂 (★**我方不发邮件/不联系供应商**)。"
        ),
        "since": "2026-11-06",
        "due": "2026-11-09",
    },
    {
        "key": "iss128_recalc_by_042mm_pitch",
        "to": "main",
        "item": (
            "★**ISS-128 的前提作废, 请按官方 pitch 重算**: ISS-128 原话『证据等级 [媒体]/[模组厂口径], **无官方 Brief Datasheet**』 "
            "⇒ ★**官方 datasheet 就在项目库里** (Rockchip RK3572 Datasheet Rev 1.1, 本地 PDF md5 c0e3763036e2f6a3e8a2f68f2254851d) ⇒ "
            "**FCCSP550L / 14.3×15.5mm / 550 球 / 球间距 0.42·0.52·0.65mm 混合** (球 0.25mm)。"
            "★**⇒ 『板面积账与逃线层数只能 [推算]』这个前提没了** ⇒ ★**ISS-118 (60×30 面积账) 与 ISS-122 (逃线层数 vs 4-6 层锁死) "
            "两条都必须按 0.42mm 重算** ⇒ ★**最小 pitch 0.42mm 落在项目自定判据的『≥0.4mm 可行』区间 ⇒ "
            "★**ISS-122『逃线 9 层破锁死』很可能是按 pitch 未知的保守值算出来的 ⇒ 要重核, 不要继续挂着**。"
            "★**边界**: 本单只交官方数字 (HW/RK3572_OFFICIAL_DATASHEET_FACTS.md, 自证 rc=0 22/22), "
            "**板面积账与层数账是 main/PM 侧的活** (改 PROJECT_TRACKER §0 锁死变量表是项目总工权限)。"
        ),
        "since": "2026-11-06",
        "due": "2026-11-09",
    },
    {
        "key": "iss167_som_io_domain_check",
        "to": "main",
        "item": (
            "★**还差一个 SoM 侧的问题, 请转 sw-lead/查 SoM 文档 (不是查 SoC)**: "
            "官方 RK3572 datasheet **没有 GPIO bank → VCCIO 供电组的对应表** —— 它只说『VCCIO1_VCC 这个网名属哪一档电压』。"
            "★**已知**: `1.8V only` = PMUIO0_VCC1V8 + VCCIO0_VCC1V8 (max 1.98V); "
            "`1.8V/3.3V` = PMUIO1_VCC + VCCIO1~6_VCC (max **3.63V**); `1.2V/1.8V` = VCCIO7_VCC (max 1.98V)。"
            "★**我们关心的 I2C0_SCL/SDA = GPIO0_B0 (球 1K21) / GPIO0_B1 (球 U32)** ⇒ ★**这两脚挂哪个 VCCIO 组 = [0数据]** ⇒ "
            "★**须查 FET3572-C 模组的 IO 域文档或 BSP rk3572.dtsi 的 io-domains / rockchip,pins 里的 VCCIO 网名**。"
            "★**为什么还要查**: 结论虽已从『I2C_A 整条降 1.8V』改成『2.8V, 理由只剩 sensor 侧 abs-max』, "
            "但**若 GPIO0 实际挂在 VCCIO0 (1.8V only) ⇒ 2.8V 仍违规** ⇒ ★**这条不查, I2C_A 的 2.8V 就只是『大概率成立』不是『已成立』**。"
            "★**纠正一条旧记录**: 我 11-02 写的『VCCIO1_VCC 属 1.8V only ⇒ I2C_A 要整条降 1.8V』是 **pdftotext 多行单元格错位**造成的"
            "⇒ 11-06 已用 p.39 渲染图核对推翻 (见 HW/RK3572_PIN_TABLE/figs/p39_gpio_crop2.png) ⇒ "
            "★**sw-lead 的 `iss148_rk3572_gpio0_vccio_domain_check` 这条 need 我已在本周直接答复** (见我方 answers)。"
        ),
        "since": "2026-11-06",
        "due": "2026-11-09",
    },
    {
        "key": "iss105_bom_generator_qty_override",
        "to": "main",
        "item": (
            "★**ISS-105 衍生 · 工具缺口 (本周第二次提醒, due 已过)**: `HW/BOM_v1.csv` 的 J_CHG 备料口径『**实物一对 (框侧座 + 脚侧座), "
            "备料按 2 只**』已写进 memo 列 (第 12 行), ★但 `state/gen_bom.py` 的自检**强制所有 ref 的 qty==1** 且 memo 由 "
            "`procurement_status()` 生成 ⇒ ★**下次重生成网表/BOM 时这行备注会被覆盖掉**。★**请在生成器里加一张『备料倍数/实物件数』"
            "覆盖表 (至少 J_CHG=2) 或改自检口径** ⇒ 否则我们的备料口径随时蒸发 (原 due 11-06 = 今天, 本周未动 ⇒ 顺延到 11-09)。"
        ),
        "since": "2026-11-06",
        "due": "2026-11-09",
    },
]

# ================================================================= 4. artifacts
ARTIFACTS = [
    {
        "path": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md",
        "kind": "spec",
        "version": "1.0",
        "updated_at": "2026-11-06",
        "summary": "★**本周最高价值产出**: RK3572 官方 datasheet Rev 1.1 事实卡 (8 节) —— "
                   "★**证伪 STATE 里『RK3572 无官方 Brief Datasheet』那条高危阻塞** (官方 PDF 就在项目库, md5 c0e3763036e2f6a3e8a2f68f2254851d) ⇒ "
                   "证据等级 [媒体]/[模组厂口径] → **[官方]**。8 节: ①封装 FCCSP550L/14.3×15.5mm/球0.25/pitch 0.42·0.52·0.65/550球/MSL3 "
                   "②内存 单通道32bit/LPDDR4X-4266·LPDDR5X-5500/16GB ③ISP 单通道12M/4096×3072/264×264 "
                   "④VO DSI-1.2 4lane2.5Gbps + HDMI2.1 + eDP1.3(DP1.2 compliant) + 并行 + EBC ⇒ **Q16=两者都有** "
                   "⑤电源域 Table3-1 分组 (VCCIO1-6 max 3.63V) ⇒ **I2C_A 降 1.8V 的结论作废** "
                   "⑥散热 ψJT/θJA/θJB/θJC **官方全 TBD** ⇒ 功耗账维持 [推算] ⑦没答上的 4 项 ⑧一条命令自证。",
    },
    {
        "path": "HW/rk3572_official_facts_check.py",
        "kind": "script",
        "version": "1.0",
        "updated_at": "2026-11-06",
        "summary": "事实卡自证脚本 (rc=0, **22/22 断言命中**): 每条断言带 PDF 文本层行号 ⇒ 任何人 `sed -n 'Np'` 可复核; "
                   "另查 2 张渲染图存在性 (Table 3-1 行×列对应只能靠图)。★**踩坑记录**: pdftotext 输出带分页符 ⇒ "
                   "必须 split(\"\\n\") 不能 splitlines() ⇒ 否则行号与 sed 差一截, 人工复核扑空。",
    },
    {
        "path": "HW/RK3572_PIN_TABLE/figs/",
        "kind": "data",
        "version": "1.0",
        "updated_at": "2026-11-06",
        "summary": "官方 datasheet 渲染图 3 张: p-20 (Fig 2-3 封装底视图 + Fig 2-4 侧视图) / p-21 (Fig 2-5 封装尺寸) / "
                   "p39_gpio_crop2 (Table 3-1 GPIO 供电分组行×列对应) ⇒ ★**表格类断言的唯一可靠来源** (扁平文本会错位)。",
    },
    {
        "path": "HANDOFF/2026-11-06_hw-lead_周更新.md",
        "kind": "handoff",
        "version": "1.0",
        "updated_at": "2026-11-06",
        "summary": "2026-11-06 周更新交接单 (B1-B6 六块齐): ISS-181 布线轮实测 (unc 45 / DRC 0 / parity 482-482 / 零铜 24 / "
                   "单边零铜 11 / Gerber 30) + 三臂实测判据 (0.0625 网格 unc 42 只差 DRC / v57 W_MIN=0.15 REJECT / "
                   "v58-v60 在跑) + RK3572 官方 datasheet 事实卡 + 逾期 issue 收口。",
    },
]

STATUS = {
    "phase": "P3(画板前致命项清零)+PCB布线收官",
    "progress_pct": 92,
    "health": "yellow",
    "summary": (
        "2026-11-06 周更新 (项目总工派, 本周唯一写会话窗口)。"
        "★**① ISS-181 布线轮实测 (官方板 md5 611b869e)**: unconnected **45** / DRC **0** / 板↔网表逐焊盘等价 **482/482** / "
        "零铜网 **24** / 差分单边零铜 **11** / Gerber **30** + 投产包 51 文件 ⇒ **G1 仍未开 (unc≠0), 不许投板**。"
        "★**② 本周三条真实推进 (都是实测, 不是推断)**: "
        "**(a) 0.0625mm 网格阶梯** (0.125 → 0.0625, margin 取半格 0.03125) ⇒ **unc 45→42** 且 **退铜名单 0 / 差分死腿 0 / "
        "逐网孤岛不变多** (Δ 侧全达标) ⇒ ★**只差 DRC 12 条清零就能晋级** ⇒ **本周离可下单最近的一步**; "
        "**(b) v57 臂 (BTB 出脚线宽 0.20→0.15mm) ⇒ REJECT**: DRC 115 (108 条 track_width 是**板规则**红 0.2 vs 实际 0.15 + 7 条真 clearance) "
        "+ unc 60 + 退铜 8 网 + 孤岛变多 17 ⇒ ★**单改线宽这条路判死**; "
        "**(c) 根因定量**: SoM BTB 0.4mm pitch · 0.2mm 焊盘 ⇒ 间隙 0.200mm ⇒ 0.20mm 线 + 两侧 0.20 净距 = 需 0.600 > 0.400 pitch ⇒ "
        "**沿排方向物理穿不过去** ⇒ ★**自研 A\\* 与 freerouting 2.1.0 两个独立引擎撞同一堵墙 ⇒ 物理约束, 不是算法问题** ⇒ "
        "三条出路 (改布局/改封装/改工艺) 已登记 needs 请项目总工拍板。"
        "★**③ 本周最高价值产出: 证伪 STATE 里『RK3572 无官方 Brief Datasheet』那条高危阻塞** —— 官方 datasheet **就在项目库里** "
        "(Rockchip RK3572 Rev 1.1, 47 页, md5 c0e3763036e2f6a3e8a2f68f2254851d) ⇒ 证据等级 [媒体] → **[官方]** ⇒ "
        "出 HW/RK3572_OFFICIAL_DATASHEET_FACTS.md (8 节) + 自证脚本 (rc=0, **22/22 断言命中**): "
        "封装 FCCSP550L/14.3×15.5mm/**pitch 0.42·0.52·0.65mm 混合**/550球 (⇒ **ISS-128『pitch 未知只能 [推算]』前提作废**, "
        "最小 0.42mm 落在 ≥0.4mm 可行区间 ⇒ 不需 HDI); 内存 **单通道 32bit** (⇒ 订正 CHIP_SHORTLIST_EVIDENCE 的 RK3576 216bit 误用); "
        "ISP **单通道 12M**/4096×3072 (⇒ **Q03 的『余量 1.9% vs 50.7%』两口径都不是 RK3572 的数**, RK3572 按官方像素能力算余量 **82.7%**); "
        "VO **DSI-1.2 + HDMI2.1 + eDP1.3(DP1.2 compliant) 都有** (⇒ **Q16 对 RK3572 = 两者都有**, 并打掉『RK3572 无 DP』那个 [媒体] 口径 ⇒ "
        "『因为无 DP 要加桥接芯片』的推理链要重写; 但『能直插标准 DP 口』= [0数据], eDP 是嵌入式形态, 须查 SoM 引脚图); "
        "电源域 Table 3-1 (p.39 渲染图核对) ⇒ **VCCIO1~6 max 3.63V** ⇒ ★**推翻我 11-02 那条『VCCIO1 属 1.8V only ⇒ I2C_A 整条降 1.8V』** "
        "(根因: pdftotext 多行单元格错位) ⇒ **I2C_A 上拉 = 2.8V, 理由只剩 sensor 侧 abs-max 一条**; 散热 **官方热阻四行全 TBD** ⇒ "
        "**功耗账维持 [推算]** (别把找到 datasheet 误当成功耗有官方依据)。"
        "★**④ 逾期 issue 收口**: 逾期 13 条里 12 条已 verified (含 vr=pass 的 10 条) ⇒ 已按『verified→closed 需 verify_by 那侧写 "
        "verify_result=pass + verify_date』的规则, 全部写 **fixed/等 main 验** 或 **转 deferred 并写清新 due**, **没有一条自验自签**。"
        "★**⑤ 本周新增 5 条 needs** (ISS-181 三条出路 / 板规则+工艺参数拍板 / ISS-128 按 0.42mm 重算 / SoM IO 域映射 / BOM 生成器备料倍数)。"
        "★**⑥ 边界**: 未发邮件 / 未联系供应商 / 未放行 RFQ / 未下单; 未改 sw.yaml·mech.yaml·pm.yaml / 别人的 issue / "
        "SW/ / MECH/ / PROJECT_TRACKER.md 锁死变量表; 未改网表生成器与 BOM 生成器 (走 needs); 官方板**本窗口未动** (md5 仍 611b869e)。"
    ),
}


def main() -> int:
    dry = "--dry-run" in sys.argv

    def mutate(d: dict) -> None:
        # --- 1. answers: 更新已有 (占位 → 真答案) + 新增 ---
        ans = d.setdefault("answers", [])
        idx = {(a.get("key"), a.get("to")): a for a in ans}
        for kk, payload in ANSWER_UPDATE.items():
            a = idx.get(kk)
            if a is None:
                ans.append({"key": kk[0], "to": kk[1], **payload})
            else:
                a["value"] = payload["value"]
                a["ref"] = payload["ref"]
        have = {(a.get("key"), a.get("to")) for a in ans}
        for a in ANSWERS_NEW:
            if (a["key"], a["to"]) in have:
                continue
            ans.append({"key": a["key"], "to": a["to"], "value": a["value"], "ref": a["ref"]})

        # --- 2. claims: 更新 + 新增 (去重复 key, 保留最后一条 = merge.py 口径) ---
        claims = d.get("interface_claims") or []
        seen = {}
        for c in claims:
            if c.get("key"):
                seen[c["key"]] = c
        out = []
        for c in claims:
            k = c.get("key")
            if k is None:
                continue
            if seen.get(k) is not c:
                continue
            if k in CLAIM_UPDATE:
                p = CLAIM_UPDATE[k]
                c["value"] = p["value"]
                c["note"] = p["note"]
                c["ref"] = p["ref"]
            out.append(c)
        have_c = {c.get("key") for c in out}
        # ★★2026-11-06 修 bug: CLAIM_UPDATE 里的 key (rk3572_* / vccio_*) 在盘上是**新增**的
        #   (旧分片里没有这些 key) ⇒ 上一版只对"已存在的 claim"做更新 ⇒ ★**这 7 条根本没写进去**
        #   (实测: claims 179 = 173 + 6, 缺的正是 CLAIM_UPDATE 的 7 条)
        #   ⇒ 修法: CLAIM_UPDATE 的 key 若不在盘上 ⇒ 按"新增"补进去 (值/note/ref 与更新同源)
        for k, p in CLAIM_UPDATE.items():
            if k in have_c:
                continue
            out.append({"key": k, "value": p["value"], "note": p["note"], "ref": p["ref"]})
            have_c.add(k)
        for nc in CLAIM_NEW:
            ex = next((c for c in out if c.get("key") == nc["key"]), None)
            if ex is not None:
                # ★★2026-11-06 修 bug 2: 盘上已有这个 key 时, CLAIM_NEW 原来只**跳过**不更新
                #   ⇒ 改过的值写不进去 (实测: demo_board_gerbers 口径改了仍是旧值)
                #   ⇒ 改成: 已有则**更新** value/note/ref (与 CLAIM_UPDATE 同语义)
                ex["value"] = nc["value"]
                ex["note"] = nc["note"]
                if nc.get("ref"):
                    ex["ref"] = nc["ref"]
                continue
            out.append(dict(nc))
        d["interface_claims"] = out

        # --- 3. needs: 新增 ---
        needs = d.setdefault("needs_from", [])
        have_n = {n.get("key") for n in needs}
        for n in NEEDS_NEW:
            if n["key"] in have_n:
                continue
            needs.append({"key": n["key"], "to": n["to"], "item": n["item"],
                           "since": n.get("since", "2026-11-06"),
                           "waiting_on": n.get("waiting_on", "agent"),
                           "due": n.get("due")})

        # --- 4. artifacts ---
        arts = d.setdefault("artifacts", [])
        have_a = {a.get("path") for a in arts}
        for a in ARTIFACTS:
            if a["path"] in have_a:
                continue
            arts.append(dict(a))

        # --- 5. status ---
        st = d.setdefault("status", {})
        st.update(STATUS)
        d["updated_at"] = "2026-11-06"
        d["updated_by"] = "hw-lead"

    if dry:
        from frag_write import load_fragment
        import copy
        d = copy.deepcopy(load_fragment("hw-lead"))
        mutate(d)
        print("[dry-run] 将要写入的统计:")
        print(f"  interface_claims: {len(d.get('interface_claims') or [])}")
        print(f"  answers: {len(d.get('answers') or [])}")
        print(f"  needs_from: {len(d.get('needs_from') or [])}")
        print(f"  artifacts: {len(d.get('artifacts') or [])}")
        return 0

    update_fragment("hw-lead", mutate)
    print("[frag_write] ✅ hw.yaml 已原子更新 (claims/answers/needs/artifacts/status)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
