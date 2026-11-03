#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_land_20261103_c.py —— 落盘老板 2026-11-03 09:54 的四条口径 + "模块内置能力"清单

★ 老板四条:
  ① pin1 在哪一排: "这个芯片的手套上肯定是有的, 你先去网上找找芯片的手册" ⇒ 已派两路查证 (Hirose 原厂 + Forlinx §2.6.1 引脚原理图)
  ② 整机/镜脚: "没有整机, 没有镜脚, demo/主板用 type-c 供电" ⇒ **这块板子就是 demo 主板** ⇒ 板级过滤 + 网表口径改写
  ③ 14 个 IC 的封装/脚号: "找下 IC 的手册和资料" ⇒ 已派 hw 调研 (只出规格表, 我改网表)
  ④ "SoM 自带 PMIC 这条要推广: 经评估之后如果对项目的整体质量和进度有帮助就推行" ⇒ **本脚本就是"推行"**
"""
import os
import sys

import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_netlist.py'
LOG = f'{PROJ}/state/issue_log.yaml'
TRK = f'{PROJ}/PROJECT_TRACKER.md'
CAP = f'{PROJ}/HW/PCB/SOM_BUILTIN_CAPABILITY.md'
AGENTS = '/home/yuewuya/.openclaw/workspace/AGENTS.md'
MEM = '/home/yuewuya/.openclaw/workspace/memory/2026-11-03.md'

CAP_TXT = '''# ★ 模块/模组"内置能力"清单 —— 母板一律不重复做

> ★**为什么有这张表**: 2026-11-03 发现 **SoM 自带 PMIC** ⇒ 主板上两颗给 SoC 核心/IO 轨供电的
> DC-DC 是纯浪费 (连带整条上电时序链 5 个件) ⇒ ★**这类"模块内部已解决、母板又做一遍"的项,
> 在本项目里不只一处** ⇒ ⇒ 落一张清单, 换料/换模组时**先查这张表**, 避免重复造。
> ★**每一条都要有手册出处** ⇒ 没有出处的**不许砍** (砍错了就是板子不工作)。

## A. Forlinx FET3572-C (RK3572 SoM) 自带

| # | 能力 | 依据 (原厂手册) | ⇒ 母板**不该再做**的项 | 落地状态 |
|---|---|---|---|---|
| A1 | **PMIC** (V_CORE / V_SOC_IO / 1.8V / 3.3V I/O 域) | 引脚表 `P3_10 = PMIC_VDC` | 主板**不产** SoC 的核心/IO 轨 | ✅ `U_DCDC_VCORE` / `U_DCDC_VIO` + 整条时序链 (Q_ENVC/Q_AND/R_EN_VCORE/R_PG_PULL/TP_PG_*) **全 DNP** |
| A2 | **主晶振** | 引脚表里**没有** XTAL_0/XTAL_1 ⇒ 未引出 | 主板不接晶振 | ✅ `X1` + 2 只 12pF **DNP** |
| A3 | **板载存储** (eMMC / SD) | 引脚表里**没有** SPI 脚 ⇒ 未引出 | 主板不挂 SPI-NOR 启动存储 | ✅ `J_BOOT1` (4p SPI + 2p 电源) **DNP** (焊盘位留作扩展) |
| A4 | **USB 2.0 OTG×2** (含 VBUS 检测 / ID) | `USB_DRD0/1` + `VBUSDET`/`ID` 脚 | 主板不另加 USB PHY / 不另做 VBUS 检测电路 | ✅ 走 `USB_DRD1` (P1_92/94/100) |
| A5 | **camera MCLK 输出** | `CAM_CLK0/1/2_OUT_M0` (P2_45/41/37) | 主板**不自己产** MCLK | ✅ 走 `CAM_CLK0_OUT_M0` ⇒ 上一版"主板自己产 MCLK"结论**作废** |
| A6 | **上电复位 (内部 PMIC 复位链)** | Forlinx 官方载板复位电路 = **按键 + 100nF + ESD**, ★**没有电压监督器** | 主板不装上电监督器 | ✅ `U_SUPV` + `C_SUPV` **DNP** (复位 = 10k 上拉 + RC + 按键) |
| A7 | **4×100pin BTB 载板接口** | §2.3 尺寸 / §5 连接器尺寸 | 主板只需摆座, 不需转接/排线 | ✅ `J_SOM_P1..P4` (各 100 焊盘) |
| A8 | **MIPI CSI 4-lane + DSI 4-lane** | §3.5.16 (CSI0+CSI1 拼 4-lane) / 引脚表 DSI_TX | 主板**不需要桥接芯片** | ✅ 方案B 已整条删除 (RK3572 无 DP TX) |

## B. Radxa Camera 4K (IMX415) 模组自带

| # | 能力 | 依据 | ⇒ 母板**不该再做**的项 | 落地状态 |
|---|---|---|---|---|
| B1 | **传感器级稳压** (模组只要 3.3V / 5V) | 模组 FPC pin28/29=VCC3.3V, pin30/31=VCC5V | 主板不产 SENSOR_AVDD / VDD_IO / CORE | ✅ `U_LDO_S28` / `U_LDO_S18B` / `U_LDO_S12` **全 DNP** |
| B2 | **4-lane MIPI + I2C5 + MCLK 输入** | 模组 FPC pin2/3/5/6/11/12/14/15/17/18/20/24/25 | 主板不产 SCCB 上拉以外的任何东西 | ✅ 走 `I2C5` (1.8V 域) ⇒ **I2C_A 上拉改 1.8V** |

## C. demo 主板本身的边界 (老板 2026-11-03 09:54)

| # | 口径 | 落地 |
|---|---|---|
| C1 | ★**没有整机, 没有镜脚; 这块板子就是 demo 主板** | 板生成器按 `board=MAIN_PCB` 过滤 ⇒ 充电链那套 (CHG_BOARD) 与跨铰链两座 (HINGE) **不上这块板** |
| C2 | ★**demo 主板用 Type-C 供电** | `J_USB_C` (16p Type-C, 受电端 UFP) = 主板**唯一**电源入口 + USB 数据口 ⇒ 5V 轨 → SoM 的 VCC_DCIN (5~13V) + `U_EN_SW` |
| C3 | **不装电池 / 不上充电链** | 电池 + 保护 IC + MOS + NTC + 分压 一律 **DNP** |
| C4 | ★**SoM 的底板主电源必须由它放行** (F13) | `CARRIER_BOARD_EN` (P3_87) → `U_EN_SW` → `RAIL_BOARD_5V`; ★**SoM 自己的 VCC_DCIN 直供 5V 不受门控** |

## D. ★ 这张表怎么用 (下一步该干什么)

1. **换料/换模组时**: 先查本表 ⇒ 能砍的项先砍 ⇒ 板面积/BOM/热/电源树直接受益
2. **网表改版时**: 本表里的"已砍"项, 若网表里又出现 ⇒ 算**回归缺陷**, 要写理由
3. **要新增一条**: 必须同时给出**原厂手册出处** ⇒ 否则不许进表
4. ★**还欠的账** (module 内置 ⇒ 也要重算):
   - `skin_temp_duty_b = 41.4°C` (RK3572 原厂 670mW vs 当时假设 500mW, +34%) ⇒ **可能破 43°C 皮肤红线** ⇒ 须实测重算
   - `soc_power_budget_v3` / `temple_heat_v3` / `battery_cap_1h_v3` / `temple_thickness_v3` / `isp_throughput_req` ⇒ 全部要按 RK3572 重算
'''


def main():
    # ── ① 网表: U_SUPV / C_SUPV 也 DNP (Forlinx 载板复位电路没有监督器) ──
    src = open(GEN, encoding='utf-8').read()
    if '"U_SUPV":' not in src:
        src = src.replace(
            '    "X1": "★晶振在 SoM 板上 ⇒ 主板不接",',
            '    "X1": "★晶振在 SoM 板上 ⇒ 主板不接",\n'
            '    "U_SUPV": "★SoM 内部 PMIC 已做上电复位 (Forlinx 官方载板复位电路 = 按键+100nF+ESD, 无监督器) ⇒ 主板不装监督器",\n'
            '    "C_SUPV": "同上 (监督器去耦电容)",')
        open(GEN, 'w', encoding='utf-8').write(src)
        print('✅ 网表: U_SUPV / C_SUPV 改 DNP')

    # ── ② 能力清单落盘 ──
    open(CAP, 'w', encoding='utf-8').write(CAP_TXT)
    print(f'✅ 能力清单已落: {CAP}')

    # ── ③ AGENTS 铁律: 加一条"模块内置能力" ──
    ag = open(AGENTS, encoding='utf-8').read()
    rule = '''
## 【铁律】模块/模组内部已实现的项, 母板一律不重复做 (2026-11-03)

★**来源**: 2026-11-03 发现 **Forlinx FET3572-C 自带 PMIC** ⇒ 主板上两颗给 SoC 核心/IO 轨供电的 DC-DC
是纯浪费 (连带整条上电时序链 5 个件) ⇒ ★**这不是孤例** ⇒ 已落清单:
`projects/smart_glasses/HW/PCB/SOM_BUILTIN_CAPABILITY.md`

**规则**:
1. **加任何"供电/时钟/存储/复位/信号生成"件之前, 先查那份清单** ⇒ 模块里已有的 ⇒ 母板不重复做
2. ★**砍之前必须有原厂手册出处** (没出处的**不许砍** —— 砍错了就是板子不工作)
3. 清单里"已砍"的项若又出现在网表里 ⇒ 算**回归缺陷**, 必须写理由
4. 换料/换模组时先过一遍清单 ⇒ 直接影响板面积 / BOM / 热 / 电源树 / 进度
'''
    if '模块/模组内部已实现的项' not in ag:
        ag = ag.rstrip() + '\n' + rule
        open(AGENTS, 'w', encoding='utf-8').write(ag)
        print('✅ AGENTS.md 已加铁律')

    # ── ④ tracker: 老板四条口径 + 推广 ──
    s = open(TRK, encoding='utf-8').read()
    sec = '''
#### (1.73) ★★★★ 2026-11-03 09:54: ★★**老板四条口径落地 + "模块内置能力"推广**

> **落账**: `HW/PCB/SOM_BUILTIN_CAPABILITY.md` (能力清单) · `AGENTS.md` (新增铁律) · `HW/PCB/som_btb_params.json` ·
> `state/gen_netlist.py` (`J_USB_C` + `DEMO_DNP` 覆盖) · `state/gen_pcb_netlist_board.py` + `state/check_pcb_nets.py` (板级过滤)

★**老板 2026-11-03 09:54 的四条, 逐条落地**:

**① "pin1 在哪一排 —— 芯片的手册上肯定是有的, 你先去网上找找芯片的手册"**
⇒ 已派**两路独立查证**: (a) **Hirose DF40C-100DS/100DP 原厂资料** (产品页 ECAD / 工程图 / 3D / 分销商镜像)
(b) **Forlinx OK3572-C 手册 §2.6.1 的 4 张引脚原理图** (★官方手册直接画了每个座的脚号排布:
左列 = 1,3,5…99 / 右列 = 2,4,6…100 ⇒ ★"哪一排"就靠它 + 底面尺寸图的方位对齐定死)
⇒ 两路结论交叉一致才落 `som_btb_params.json`; ★**错一排 = 该座 100 根网络全部对调** ⇒ 属"下单前必查"。

**② "没有整机, 没有镜脚, demo/主板用 type-c 供电"** ⇒ ★**这块板子就是 demo 主板**
⇒ ① 网表里 `J_DEMO_USB` 改名 **`J_USB_C`** = 主板的 Type-C 电源入口 (受电端 UFP: VBUS→5V 轨 → SoM 的
VCC_DCIN + `U_EN_SW`; D+/D-→SoM USB; CC1/CC2→5.1k 下拉) ② **板生成器按 `board=MAIN_PCB` 过滤**
⇒ 充电链那套 (CHG_BOARD) 与跨铰链两座 (HINGE) **不上这块板** ⇒ 板子从 213 器件降到 **181 器件**
③ 电池 + 保护 IC + MOS + NTC + 分压 一律 **DNP** (demo 不装电池) ④ **J_BOOT1 (SPI-NOR 焊盘位) 也 DNP**
(SoM 板载 eMMC) ⇒ ★**"镜脚主板/镜框充电板"这套表述从 demo 语境里去掉** (整机是后面的事)。

**③ "找下 IC 的手册和资料, 手册中应该有"** ⇒ 已派 hw 调研 **15 个命名脚器件** (4 颗 TPS7A20 / U_SUPV /
U_PWR_SW / U_EN_SW / U_BATPROT / Q1 / BT_432243 / J_TYPE_C / 2 颗 TPS62130A) + 两个 FPC 座
(★`CONN_CAM` = FH35C-31S-0.3SHW(50) 型号已定要封装图; ★`CONN_LIGHT` 40p/0.5mm **型号还没定** ⇒ 要 ≥3 个公开在售候选)
⇒ ★**只出规格表** (`HW/PCB/PINOUT_FOOTPRINT_SPEC.md` + `pinout_footprint.json`), **不许改网表** ——
我改网表 ⇒ ★**因为历史上让子 agent 直接改网表, 三次 0 产出**。

**④ "SoM 自带 PMIC 这条要推广, 经评估后如果对整体质量和进度有帮助就推行"** ⇒ **评估结论: 有帮助, 已推行**
⇒ ★**已砍掉的"重复造"清单** (共 11 类): SoM 自带 PMIC ⇒ 2 颗 DC-DC + 5 个时序链件 DNP ·
SoM 自带晶振 ⇒ X1 + 2 只 12pF DNP · SoM 板载 eMMC ⇒ J_BOOT1 DNP · 相机模组自带稳压 ⇒ 3 颗 sensor LDO DNP ·
Forlinx 载板复位电路无监督器 ⇒ **U_SUPV + C_SUPV DNP** · demo 不装电池 ⇒ 电池侧 10 个件 DNP
⇒ ★**推行方式**: ① 落 **`HW/PCB/SOM_BUILTIN_CAPABILITY.md`** (每条带手册出处) ② ★**写进 AGENTS 铁律**
(加任何供电/时钟/存储/复位/信号生成件之前先查清单; **砍之前必须有原厂出处**) ③ 网表里"已砍"的项再出现 = **回归缺陷**
⇒ ★**直接收益**: 板面积 / BOM / 热 / 电源树 / 进度 —— ★**顺带发现 §1 的欠账**:
`skin_temp_duty_b=41.4°C` 那条 (RK3572 原厂 670mW 比原假设 500mW 高 34%) **可能破 43°C 皮肤红线** ⇒ 须实测重算。
'''
    if '(1.73)' not in s:
        s = s.rstrip() + '\n' + sec
        open(TRK, 'w', encoding='utf-8').write(s)
        print('✅ tracker 已加 §(1.73)')

    # ── ⑤ issue_log: ISS-169 更新 (边界改了) ──
    d = yaml.safe_load(open(LOG, encoding='utf-8'))
    by = {i['id']: i for i in d['issues']}
    i169 = by.get('ISS-169')
    if i169:
        i169['title'] = ('★★[demo 板可制造性] demo 主板的边界已定 (Type-C 供电 · 不装电池 · 板上只有这一块) + '
                         'SoM 座的 pin1 排向待查证 + 15 个器件的封装脚号待落定')
        i169['note'] += (' ★★2026-11-03 09:54 老板口径落地: ① **这块板子就是 demo 主板** (没有整机/没有镜脚) ⇒ '
                         '板生成器按 board=MAIN_PCB 过滤 (充电链/铰链件不上板) ⇒ 板 213→181 器件; '
                         '② **J_DEMO_USB 改名 J_USB_C** = 主板 Type-C 电源入口 (唯一 5V 入口); '
                         '③ 电池侧 + J_BOOT1 + X1 + U_SUPV + 两颗 DC-DC 等 11 类"模块已内置"的项全 DNP '
                         '(⇒ 清单落 HW/PCB/SOM_BUILTIN_CAPABILITY.md + AGENTS 铁律); '
                         '④ ★**pin1 排向**: 已派两路查证 (Hirose 原厂 + Forlinx §2.6.1 引脚原理图) ⇒ '
                         '**错一排 = 该座 100 根网络全对调** ⇒ 属"下单前必查"; '
                         '⑤ ★**15 个器件的封装/脚号** 已派 hw 调研 (只出规格表, 我改网表)。')
        yaml.safe_dump(d, open(LOG, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False,
                       default_flow_style=False, width=10000)
        print('✅ issue_log ISS-169 已更新')

    # ── ⑥ 记忆 ──
    m = open(MEM, encoding='utf-8').read()
    m += '''
## ★★ 09:54 老板四条口径 (全部落地)

1. **"芯片的手册上肯定有"** ⇒ pin1 排向派两路查证 (Hirose 原厂 ECAD/工程图 + Forlinx §2.6.1 引脚原理图 4 张)
2. ★★**"没有整机, 没有镜脚, demo/主板用 type-c 供电"** ⇒ **这块板子就是 demo 主板**:
   `J_DEMO_USB` → **`J_USB_C`** (主板唯一 5V 入口) · 板生成器按 `board=MAIN_PCB` 过滤 (充电链/铰链不上板)
   · 电池侧 + SPI-NOR 焊盘位 + 晶振 + 监督器 + 两颗 DC-DC 全 DNP ⇒ 板 213→181 器件
3. **"找下 IC 的手册"** ⇒ 派 hw 调研 15 个器件的封装/脚号 (只出规格表, 我改网表)
4. ★★**"SoM 自带 PMIC 这条要推广"** ⇒ 评估结论**有帮助, 已推行**: 落
   `HW/PCB/SOM_BUILTIN_CAPABILITY.md` (11 类已砍项, 每条带手册出处) + **写进 AGENTS 铁律**
   (加供电/时钟/存储/复位/信号生成件之前先查清单; 砍之前必须有原厂出处; 已砍项再出现 = 回归缺陷)
   ⇒ ★**直接收益**: 板面积 / BOM / 热 / 电源树 / 进度
'''
    open(MEM, 'w', encoding='utf-8').write(m)
    print('✅ memory 已追加')
    return 0


if __name__ == '__main__':
    sys.exit(main())
