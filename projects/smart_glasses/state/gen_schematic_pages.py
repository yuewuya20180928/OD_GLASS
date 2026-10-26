#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原理图 V1 图页生成器 (gen_schematic_pages) —— 从 netlist_v1.csv 生成 8 页图页
================================================================================
★为什么是脚本生成而不是手写:
  2026-10-26 19:26-19:44, hw-lead 那一轮把 8 页正文写在**聊天回复里**而不是落盘 →
  19:44 网关重启(机器睡了 4 小时) → 产物随 /tmp 一起没了, 净网也回到我生成的 108 行版。
  教训: **图页正文必须落盘, 且器件表必须由 netlist 机械生成** (人写的部分只留"判断/说明")。
  → 本脚本: 器件表 = 从 CSV 机械生成 (不会漂) · 每页叙述 = 项目总工写的判断 (在下面 NARRATIVE 里)

用法:  python3 state/gen_schematic_pages.py
产出:  HW/SCHEMATIC_V1.md (8 页: P1 电源树 / P2 SoC 主控 / P3 启动存储 / P4 显示双出口 /
                     P5 MIPI-CSI 传感器 / P6 高速差分与连接器 / P7 板级接口与测试点 / P8 时钟·复位·调试)
"""
from __future__ import annotations

import csv
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CSV_P = os.path.join(PROJ, "HW", "netlist_v1.csv")
OUT = os.path.join(PROJ, "HW", "SCHEMATIC_V1.md")

PAGES = OrderedDict([
    ("P1", ("电源树", "13 电源域 + Type-C 充电链 + 3 路 LDO + 2 路 DC-DC")),
    ("P2", ("SoC 主控", "低速控制 / ADC 检测 / I2C / FSIN — SoC 侧全部 TBD-01 占位")),
    ("P3", ("启动存储", "★ 只留焊盘位 + 串阻位, 不画存储芯片 (内置 DRAM 已确认, 启动介质必然外挂)")),
    ("P4", ("显示双出口", "DSI 原生 / 桥接 互斥 8 个 0Ω 位; 走鹃Ⅱ 原生 800×600 (上采样 ×1.25)")),
    ("P5", ("MIPI-CSI 传感器", "CONN_CAM 40p 跨铰链; 4-lane 预留; AC 耦合 + 对地端接")),
    ("P6", ("高速差分与连接器", "DP_TX 4 lane / USB 2.0 / Type-C CC")),
    ("P7", ("板级接口与测试点", "13 个测试点 + 3 按键 + 3 LED + ID 跳线")),
    ("P8", ("时钟 · 复位 · 调试", "XTAL 两套方案 (内部RC不装 / 外部晶振焊盘位不装) + RESET/BOOT + JTAG/UART")),
])

# ★ 每页叙述 = 项目总工的判断 (不是从 CSV 来的, 是设计决定)
NARRATIVE = {
"P1": """**这张页是整个方案的电源账, 也是散热账的起点。**

- 电源链: Type-C 5V → ESD + π 滤波 → `VBUS_5V` (2.0A) → 电池充放 (BQ25896 + BQ2970 + 2×MOS) → `BAT` → `SYS` (3.0-4.2V, 0.55A 上限) → 2 路 DC-DC (TPS62130A) + 6 路 LDO (TPS7A20 系列) 分出 13 条轨。
- ★**R-F1 硬伤已裁决**: `SYS` 下限 3.0V 与 3.3V 轨的 dropout (110mV typ [官方]) 冲突 → 放电末段 12-15% 电量时 3.3V 轨失效 = **用��快没电突然黑屏**。**基线方案: UVP 抬到 3.5V + 3.3V 改由 TPS62130A 供** (代价 12-15% 容量不可用 → 电池容量与续航口径要重算)。第三条路 (更低 dropout 的 LDO / IO 轨直吃 SYS / 加 buck-boost) 正在评估 (ISS-067)。
- ★**V_CORE 上界按 1.0V** (网上查证: 工作电压范围 0.65-1V, DVFS [媒体·百科]) → DC-DC 输出范围与压差核算要覆盖 1.0V, 不是我们原假设的 0.9V。
- **散热账**: 满载镜腿内发热量 0.90W → 皮肤侧 **80.1°C** (镜腿内主口径) / 96.1°C (整机上界), vs ISO 13732-1 的 43°C 红线 → **贴皮肤镜腿只能承受 0.15-0.2W**。⇒ 这页的每个电流数字都要跟"按需触发"口径一起看, 不然整机方案会被温度否掉。
- **[待原厂]**: 各电源域的**标称电压 / 典型电流 / 最大电流 / 上电时序 / 是否需外部 LDO** (TBD-02)。`V_CORE` 与 `V_SOC_IO` 的电压现在都还是待定 → DC-DC 只是"IC 可画, 电压待定"。""",
"P2": """**SoC 侧的脚全是 TBD 占位 —— 这页是"原厂回信后只填球号就能投板"的关键。**

- SoC 侧节点统一写成 `SoC[TBD-01].<信号名>`: **原厂引脚表/球位图未回 (第 5 天)**, 所以本页**不写一个球号**。
- 本页信号: I2C_A (总线 A, 接 sensor / NTC / 桥接 / 充电 IC) · 充电状态回读 (`CHG_STAT` / `PWR_GOOD` / `VBUS_DET` / `BAT_DET`) · `FSIN` 帧同步 (引到测试点, 若 SoC 无此脚则 DNP) · `ID_DETECT` (焊盘跳线)。
- ★**充电状态读回有兜底**: 即使 SoC 读不到充电 IC 状态, 也有 `TP_CHG_STAT` + `TP_VBUS` → "充电时禁 OD" 门禁不会瞎 (M-CHRG 判未验, 但不至于误判)。
- ★**USB PHY 基本确认存在** (官网智能可穿戴页列 USB 3.0) → `USB_D+/D-` 走 Type-C 这条路**有依据了**; 但版本 (2.0/3.0) 与 PHY 数量仍要问 (影响引脚预算)。
- **[待原厂]**: 引脚表与球位图 (TBD-01) · USB PHY 版本与引脚数 (TBD-10) · 帧同步能否引出/能否输入 (TBD-07 / TBD-13) · I2C 从设备地址是否可配 (TBD-09)。""",
"P3": """**这一页故意"空着" —— 但它是有依据的空, 不是漏画。**

- ★**官网已确认 ARS45 内置 512MB DRAM 且已量产** (另有 ARS48 1GB 已送样 / ARS41 128MB Q3 送样) → **启动介质必然外挂**。所以本页只画 **4 条 SPI 信号 + 串阻位 + 焊盘位**, **不画存储芯片**。
- 两种外挂形态的代价差别很大: **SPI-NOR** (小, 省板宽, 兆易创新是酷芯微第二大股东 → 生态顺) vs **eMMC** (容量大但吃板面积 → 我们评估板宽 12→15mm) ⇒ **这个选择直接顶到板宽**, 而板宽又被官网"宽度≤8mm"卡着 (见 §(1.25))。
- 串阻位 (0Ω) 的作用: 让 SoC 的启动介质可以换 NOR/eMMC 而**不改板** —— 两种都留位, 装配时决定。
- **[待原厂]**: 外挂是 SPI-NOR 还是 eMMC (TBD-06) · 挂在哪个接口 (SPI 控制器? eMMC/NAND 控制器?) (TBD-11) · 上电时序要求 (TBD-12)。""",
"P4": """**这一页决定要不要多一颗桥接芯片 (100-300mW + 4-8 周采购 + PCB 面积)。**

- 走鹃Ⅱ 是 **800×600 原生** (官网+LEDinside+EET 三源一致) → 我们的链路是 **ISP 640×480 → OD letterbox → 640×640 → 显示上采样 ×1.25 → 800×600**, 正好对上; 老板锁的显示分辨率 800×600 与光引擎原生一致 ✅。
- ★**30° 是对角 FOV** (自洽校验: 对角 1000px ÷ 30° = 33.3 PPD) → 显示端原生角分辨率 0.030°/px 对角。显示端映射 (采集 120° → 显示 30°) 是 **Q23** 待老板拍板: (a) 全幅压进 30° (看得广但糊) (b) 30° 中心窗口 (看得清但窄, 但显示侧要 crop)。
- ★**8 个 0Ω 位 = 两条互斥路**: `R_SEL_*` (SoC 原生 DSI TX 直连光机) 与 `BR_*` (经桥接芯片) **不得同时装** (否则两个驱动源打架) → BOM 分两组列, 由装配决定。`R_SEL_D2/D3` 与 `R_TERM_*` 永远 DNP (2 lane 不够时再装; 端接 100Ω 对地, 0402 手工可补)。
- ★**显示 TX 的新证据**: 官网原文 "支持端到端 **3-4ms** 超低延迟显示链路" + "多屏异显" → **芯片内部确有显示输出通路**; 官网另有 "集成 Display Port 1.4" (但**没写方向**, 而媒体写 DP1.4 RX) ⇒ **推断: 极可能有显示 TX, 具体接口待定** → 所以**双出口必须都留**。
- **[待原厂]**: 有无 MIPI-DSI TX / DP1.4 是否有 TX / 能否同时工作 / lane 数与速率 (TBD-04) · DSI DDC I2C 是否独立于 SoC 通用 I2C (TBD-09)。""",
"P5": """**传感器侧: 跨铰链的差分对, 全部 100Ω 差分 + AC 耦合位 + 对地端接位。**

- 4-lane CSI: `A-01..A-10` (CK + D0..D3), 其中 **D2/D3 是 DNP (预留 4-lane)** —— 我们只用 1080p60 单路, 2-lane 就够, 但**预留 4-lane 是为了让"以后换高分辨率 sensor"不用改板**。
- 跨铰链是这里最脆的一环: `CONN_CAM` 40p 走铰链 → 阻抗连续性、AC 耦合电容位置、对地端接位置都要跟结构侧的铰链行程对齐 (ISS-065 的结构建议里提了这一条)。
- 传感器电源 3 条轨 (`SENSOR_AVDD` 2.8V / `SENSOR_VDD_IO` 1.8V / `SENSOR_CORE` 1.2V) 由 3 路 TPS7A20 LDO 供, **都在镜框侧** (不进镜腿皮肤路径) → 这也是散热账里"镜腿内发热量 0.90W"能成立的原因。
- ★**传感器选型还锁着 3 件事** (Q16 宽高比 / Q24 准入线 / sensor 必须支持**全幅**输出模式): 裸 1080p 对 OV04C10 就是 ROI 模式 (对角 FOV 120°→85.61°), 违反我们"禁 ROI"的硬约束 → **只有 1080p ROI 模式的 sensor 一票否决**。
- **[待原厂]**: CSI lane 数 / 每 lane 速率 / 电压域 / AC 耦合是否内置 / MCLK 电压 (TBD-03)。""",
"P6": """**高速差分与连接器: 板宽与 pitch 的风险都集中在这几页。**

- `A-21` DP_TX 4 lane: 主 PCB 内部走线 + redriver 位 (0402 串阻 ×4 + 对地电容位) —— 走线是 8×10mm 芯片**逃线**的主要出口, 也是"宽度≤8mm 硬约束"最吃紧的地方。
- `USB_D+/D-` (Type-C → 主 PCB, 跨铰链则经 `CONN_USB`) + `USB_CC1/CC2` (Type-C 方向检测) —— 我们**第一版不上无线**, USB 只做调试/烧录通道。
- ★**本轮网上查证标红的一条**: 官网说"封装尺寸须压缩至**宽度≤8mm**" + 8×10mm FCCSP **集成 DRAM** 的球间距通常 0.4-0.5mm [推算] → **我们 12mm 板宽 + 4-6 层叠层假设可能过于乐观** ⇒ **ISS-078 (blocker) 要按 pitch 0.3/0.4/0.5mm 三档重算**。这页的走线密度在 pitch 变大时会先崩。
- **[待原厂]**: FCCSP pitch + 完整球位图 + 逃线参考布局 (TBD-05) + AR9481 同 Die 代理资料。""",
"P7": """**测试点是这台样机的"仪器接口" —— 13 个点决定了我们能不能在 G3 测出真数。**

- 13 个 TP 覆盖: 5 条电源 (VBUS / SYS / BAT / VCORE / VIO) + 3 条传感器轨 + 3 条光机轨 + 光机 DDC 相关的 2 条 (TBD-09 未确认前按"若 DDC 独立"预留)。**每个 TP 都在 §位置 写明"量哪个脚、离多远"**。
- 3 个按键 (PWR / VOL+ / VOL-) + 3 个 LED (R/G/B; **B 是 DNP —— 第一版不上无线**) + `ID_DETECT` 焊盘跳线 (主板/副板识别)。
- ★**这一页决定了三个硬指标能不能从"推算"变成"实测"**: 端到端 (`TP_FSIN` + 串口打点) · 皮肤温度 (热电偶) · 充电态温度 (`TP_CHG_STAT` + `TP_VBUS`)。**没这些点, EVT 只能写"未验"**。
- 全部测点走 **测试点 + π 滤波后** 的形式 → 第一台样机不贴这些点会返工 (后续加板要重来), 所以清单里明确标"第一台样机没有这些, 后期加板要重来"。
- **[待原厂]**: 帧同步能否引出 (TBD-07) · 充电状态能否读回 (TBD-08, 已有 TP 兜底, 不卡项目)。""",
"P8": """**时钟 / 复位 / 调试 —— 看着不起眼, 但这里有两个"必须双份"的决定。**

- ★**XTAL 双方案**: 参考版**同时**给 "内部 RC (不装)" 与 "外部晶振 (焊盘位 + 2×12pF, **不装**)" 两套 —— 因为**原厂一句话就能定生死** (ARS45 到底要不要外部晶振, 同 Die 的 AR9481 也不能确定)。焊盘位先留, 装配时按原厂确认选。
- `RESET_N` / `BOOT_N` 走按键到 GND (软上电/进下载模式), **释放时序**待原厂 (TBD-12) → 这决定我们按键电容与上电电阻怎么配。
- `JTAG` 4 线 + `UART` 2 线 复用 1×4 1.27mm 排针 (**不装贴片**, 手工可焊) —— 调试/烧录通道, 与 USB 二选一。
- **[待原厂]**: 上下电/复位时序要求 (TBD-12, 含 RESET 释放时机与内部 DCDC 同步机制) · 是否有 USB PHY 及其版本 (TBD-10) · 启动介质与挂载接口 (TBD-06/11)。""",
}


def main() -> int:
    if not os.path.exists(CSV_P):
        print(f"❌ 缺 netlist: {CSV_P}", file=sys.stderr)
        return 2
    rows = list(csv.DictReader(open(CSV_P, encoding="utf-8")))
    by_page: "OrderedDict[str, list]" = OrderedDict((p, []) for p in PAGES)
    for r in rows:
        by_page.setdefault(r["page"], []).append(r)

    out = [
        "# HW/SCHEMATIC_V1.md —— ARS45 硬件原理图 V1 (8 页图页)\n",
        "> **生成方式**: 器件表由 `state/gen_schematic_pages.py` 从 `HW/netlist_v1.csv` **机械生成** (不会与 netlist 漂移); "
        "每页叙述是**项目总工的判断** (写在生成脚本的 NARRATIVE 里)。\n",
        "> **本版不是投板文件** —— SoC 侧球位图未回 (原厂, 第 5 天), 全部写成 `SoC[TBD-01].<信号>` 占位; "
        "原厂回信后**只填球号 + 改 TBD 项**即可进 PCB。\n",
        "> **门禁**: `python3 state/check_netlist.py` (12 条机械判据, 项目总工的验收器) + 本文件的 8 页完整性由\n"
        "> `grep -o '^## P[0-9]' HW/SCHEMATIC_V1.md | sort -u` 机械核对。\n",
        "> **相关**: 图纸规格 `HW/SCHEMATIC_V1_SPEC.json` · netlist `HW/netlist_v1.csv` · KiCad 可导入 `HW/netlist_v1.net` ·\n"
        "> 顶层接口 `HW/SCHEMATIC_L1.md` · 连接表 `HW/INTERFACE_TABLE.md` · 查证结果 `HW/ONLINE_FINDINGS_2026-10-26.md`\n",
        "---\n",
    ]
    for pg, (title, sub) in PAGES.items():
        rs = by_page.get(pg, [])
        out.append(f"\n## {pg} {title}\n")
        out.append(f"> {sub}\n")
        out.append("\n### 功能块与判断\n")
        out.append(NARRATIVE.get(pg, "") + "\n")
        out.append(f"\n### 器件表 ({len(rs)} 行 netlist 记录)\n")
        out.append("| net | 节点1 | 节点2 | 位号 | 值 | 类型 | DNP | 证据 | TBD | 说明 |\n")
        out.append("|---|---|---|---|---|---|---|---|---|---|\n")
        for r in rs:
            out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n" % (
                r.get("net", ""), r.get("node1", ""), r.get("node2", ""), r.get("ref", ""),
                r.get("value", ""), r.get("type", ""), r.get("dnp", ""), r.get("evidence", ""),
                r.get("tbd", ""), str(r.get("note", ""))[:90].replace("|", "/")))
    out.append("\n---\n\n")
    out.append("## 附: 本版与投板版还差什么 (缺口清单)\n")
    out.append("| # | 缺什么 | 卡住谁 | 怎么解 |\n|---|---|---|---|\n")
    for i, (a, b, c) in enumerate([
        ("SoC 引脚表 / 球位图 / FCCSP pitch", "原理图定版 + PCB 逃线 + 板宽 (blocker)", "原厂 (TBD-01/05) —— **网上确认拿不到** (官网无下载区)"),
        ("各电源域标称电压/最大电流/上电时序", "P1 电源页定版 + DC-DC 选型", "原厂 (TBD-02)"),
        ("MIPI-CSI lane 数/速率/AC 耦合是否内置", "P5 传感器页 (AC 耦合位/端接位)", "原厂 (TBD-03)"),
        ("显示 TX 接口类型 (DSI / DP / 两者)", "P4 显示页 + 要不要桥接芯片", "原厂 (TBD-04) + **JBD 开发套件接口定义** (可能更快)"),
        ("启动存储形态 (SPI-NOR vs eMMC) 与挂载口", "P3 启动存储页 + 板宽", "原厂 (TBD-06/11)"),
        ("球位号 (全部 SoC 侧节点)", "8 页全部", "原厂 (TBD-01)"),
    ], start=1):
        out.append(f"| {i} | {a} | {b} | {c} |\n")
    out.append("\n> ★**并行风险**: 官网「宽度≤8mm」+ FCCSP 集成 DRAM 的 pitch 通常 0.4-0.5mm [推算] → **12mm 板宽与 4-6 层假设可能被推翻** (ISS-078, blocker)。\n")

    open(OUT, "w", encoding="utf-8").write("".join(out))
    print(f"✅ 已生成 {OUT} ({os.path.getsize(OUT)} bytes, 8 页)")
    for pg in PAGES:
        print(f"   {pg} {PAGES[pg][0]:<22} {len(by_page.get(pg, [])):>3} 行")
    return 0


if __name__ == "__main__":
    sys.exit(main())
