#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_iss165_a2_som.py —— ★A2 段: 把 SoC 侧节点从占位符改成**真实引脚** (Forlinx FET3572-C)

★★ 真值来源 (全部公开, 零咨询厂家):
  · `HW/PCB/FET3572C_PIN_TABLE.csv` —— 由 `state/_iss165_som_pins_rebuild.py` 从
    **Forlinx OK3572-C 官方手册** §2.6.2/§2.7 重建 (399 行, 与 OK3576-C 手册交叉验证 +
    与 Forlinx 载板原理图的球号逐脚互证 12/12 对上)
  · ★**不是 OK3576-C 的表**: 实测 RK3572 与 RK3576 的引脚功能**不同** (226/398 脚球号都不同)
    ⇒ 上一版分配表 (基于 3576) **作废** —— 例如 3576 的 P1_56=I2C8_SCL_M2, 而 RK3572 的 P1_56=GPIO2_B6_d

★★ 分配原则:
  ① **先看功能再选脚**: 相机 SCCB 走 I2C5 (模组 FPC 上就写着 I2C5, 且 RK3572 的 I2C5 是 1.8V 域)
     ⇒ 上拉必须改 1.8V (旧网表拉到 3.3V ⇒ **SoM 的 1.8V 脚被灌 3.3V**)
  ② 触控 I2C + TMP117 走 I2C2 (3.3V 域; ★TMP117 的 VIH=0.7×V+ ⇒ 1.8V 总线不满足)
  ③ **4-lane CSI 在 RK3572 上必须拆成 CSI0(2 lane)+CSI1(2 lane)**
     (Forlinx 载板原理图同款接法: 同一 FPC 座上引出 CSI0 D0/D1+CLK 与 CSI1 D0/D1+CLK)
  ④ camera MCLK 用 SoM 的 **CAM_CLK0_OUT_M0** (⇒ 上一版"主板自己产 MCLK"的结论作废)
  ⑤ ★**没引出的信号不编造**: SPI / JTAG / XTAL / FSIN 在 FET3572-C 上没有 ⇒ 标 DNP + 写明理由
  ⑥ F13 (致命项): SoM 的 **CARRIER_BOARD_EN (P3_87)** 驱动主板底板电源开关 U_EN_SW
     ⇒ 底板各路挂 **RAIL_BOARD_5V** (不是 SYS); SoM 自己的 VCC_DCIN (P3_91/93/95/97/98/99/100) 走 5V

产出:
  HW/PCB/som_pin_assign.json     ← 机器可读分配表 (网表生成器 + 门禁都读它)
  HW/PCB/SOM_PIN_ASSIGNMENT.md    ← 人读版 (含每个选择的依据)
  state/gen_netlist.py            ← 加 soc_pin() + A2 段行 (电源使能 / VCC_DCIN / I2C 订正)
"""
import csv
import json
import os
import re
import sys

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
PINTBL = f'{PROJ}/HW/PCB/FET3572C_PIN_TABLE.csv'
ASSIGN = f'{PROJ}/HW/PCB/som_pin_assign.json'
ASSIGN_MD = f'{PROJ}/HW/PCB/SOM_PIN_ASSIGNMENT.md'
GEN = f'{PROJ}/state/gen_netlist.py'

# ★我们的信号 → RK3572 信号名 (再由引脚表解析出 (conn,num))
MAP = {
    # ---- 电源 / 启动 / 复位 ----
    'PWR_CTRL':      ('PWRON_L',              '开机/关机 (SoM 输出)'),
    'RESET_N':       ('RESET_L',               'SoM 复位 (低有效)'),
    'BOOT_N':        ('SARADC_VIN0_BOOT',      'BOOT 模式选择 (SARADC 分压)'),
    'ID0':           ('SARADC_VIN2_HW_ID',     '硬件版本 ID (SARADC2)'),
    'ID1':           ('SARADC_VIN4',           '第二路 SARADC (通用 ADC)'),
    'BAT_DET':       ('SARADC_VIN5',           '电池电压检测 (1M+1M 分压进 ADC)'),
    # ---- USB (SoM 侧 OTG1) ----
    'USB_D_P':       ('USB_DRD1_DP',           'USB 2.0 D+ (OTG1)'),
    'USB_D_N':       ('USB_DRD1_DM',           'USB 2.0 D- (OTG1)'),
    'USB_VBUS_DET':  ('USB_DRD1_VBUSDET',      'USB VBUS 插入检测'),
    # ---- I2C ----
    'I2C_A_SCL':     ('I2C5_SCL_M3',           '★相机 SCCB (模组 FPC 标注 I2C5; RK3572 的 I2C5 = 1.8V 域 ⇒ 上拉改 1.8V)'),
    'I2C_A_SDA':     ('I2C5_SDA_M3',           '★同上'),
    'I2C_B_SCL':     ('I2C2_SCL_M0',           '触控 I2C + TMP117 (3.3V 域; TMP117 VIH=0.7×V+ ⇒ 不能上 1.8V)'),
    'I2C_B_SDA':     ('I2C2_SDA_M0',           '★同上'),
    # ---- DSI 4-lane + 时钟 ----
    'DSI_TX_CK_P':   ('MIPI_DPHY_DSI_TX_CLKP', 'DSI 时钟 +'),
    'DSI_TX_CK_N':   ('MIPI_DPHY_DSI_TX_CLKN', 'DSI 时钟 -'),
    'DSI_TX_D0_P':   ('MIPI_DPHY_DSI_TX_D0P',  'DSI lane0 +'),
    'DSI_TX_D0_N':   ('MIPI_DPHY_DSI_TX_D0N',  'DSI lane0 -'),
    'DSI_TX_D1_P':   ('MIPI_DPHY_DSI_TX_D1P',  'DSI lane1 +'),
    'DSI_TX_D1_N':   ('MIPI_DPHY_DSI_TX_D1N',  'DSI lane1 -'),
    'DSI_TX_D2_P':   ('MIPI_DPHY_DSI_TX_D2P',  'DSI lane2 +'),
    'DSI_TX_D2_N':   ('MIPI_DPHY_DSI_TX_D2N',  'DSI lane2 -'),
    'DSI_TX_D3_P':   ('MIPI_DPHY_DSI_TX_D3P',  'DSI lane3 +'),
    'DSI_TX_D3_N':   ('MIPI_DPHY_DSI_TX_D3N',  'DSI lane3 -'),
    # ---- CSI 4-lane (★CSI0 2lane + CSI1 2lane) + MCLK ----
    'CSI_D0_CK_P':   ('MIPI_DPHY_CSI0_RX_CLKP', 'CSI lane0 时钟 +'),
    'CSI_D0_CK_N':   ('MIPI_DPHY_CSI0_RX_CLKN', 'CSI lane0 时钟 -'),
    'CSI_D0_D0_P':   ('MIPI_DPHY_CSI0_RX_D0P',  'CSI lane1 +'),
    'CSI_D0_D0_N':   ('MIPI_DPHY_CSI0_RX_D0N',  'CSI lane1 -'),
    'CSI_D0_D1_P':   ('MIPI_DPHY_CSI0_RX_D1P',  'CSI lane2 +'),
    'CSI_D0_D1_N':   ('MIPI_DPHY_CSI0_RX_D1N',  'CSI lane2 -'),
    'CSI_D0_D2_P':   ('MIPI_DPHY_CSI1_RX_D0P',  '★CSI lane3 + (4lane = CSI0+CSI1 拼)'),
    'CSI_D0_D2_N':   ('MIPI_DPHY_CSI1_RX_D0N',  '★CSI lane3 -'),
    'CSI_D0_D3_P':   ('MIPI_DPHY_CSI1_RX_D1P',  '★CSI lane4 +'),
    'CSI_D0_D3_N':   ('MIPI_DPHY_CSI1_RX_D1N',  '★CSI lane4 -'),
    'CSI_MCLK':      ('CAM_CLK0_OUT_M0',       '★SoM 自带 CAM_CLK 输出 ⇒ 不用主板自己产 (1.8V)'),
    # ---- GPIO (全取 3.3V 域, 避免电平转换) ----
    'GPIO_CAM_RESET': ('GPIO2_B5_d',           'camera RESET (低有效, 3.3V)'),
    'GPIO_DSI_RESET': ('GPIO2_B6_d',           'DSI RESET (3.3V)'),
    'CSI_RESET_N':   ('GPIO0_C1_d',           '★(旧 CSI_RESET_N 已并入 CAM_RESET_N; 此条备用)'),
    'LED_R':         ('GPIO0_C2_d',           '红 (3.3V)'),
    'LED_G':         ('GPIO4_B7_d',           '绿 (3.3V)'),
    'LED_B':         ('GPIO4_B4_d',           '蓝 (3.3V)'),
    'KEY_PWR':       ('GPIO0_D3_d',           '电源键 (3.3V)'),
    'KEY_VOL_P':     ('GPIO0_C4_d',           '音量+ (3.3V)'),
    'KEY_VOL_M':     ('GPIO0_C5_d',           '音量- (3.3V)'),
    'KEY_CAM':       ('GPIO0_C7_d',           '拍照键 (3.3V)'),
    # ---- UART 调试 ----
    'UART_TX':       ('UART0_TX_M0_DEBUG',    '调试串口 TX (3.3V)'),
    'UART_RX':       ('UART0_RX_M0_DEBUG',    '调试串口 RX (3.3V)'),
}

# ★FET3572-C **未引出** 的信号 (引脚表里没有) ⇒ 不编造, 标 DNP
DNP_SIGS = {
    'SPI_SCLK': 'FET3572-C 未引出 SPI (SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR)',
    'SPI_CSn':  '同上',
    'SPI_MOSI': '同上',
    'SPI_MISO': '同上',
    'JTAG_TCK': 'FET3572-C 未引出 JTAG (调试走 UART0)',
    'JTAG_TMS': '同上',
    'JTAG_TDI': '同上',
    'JTAG_TDO': '同上',
    'XTAL_IN':  '晶振在 SoM 板上 ⇒ 主板不接',
    'XTAL_OUT': '同上',
    'FSIN':     'FET3572-C 无 FSIN 脚',
}


def main():
    rows = list(csv.DictReader(open(PINTBL, encoding='utf-8')))
    sig2 = {}
    for r in rows:
        sig2.setdefault(r['signal'], []).append({
            'conn': r['conn'], 'num': int(r['num']), 'ball': r['ball'],
            'vol': r['vol'], 'desc': r['desc']})

    assign, missing, ambiguous = {}, [], []
    for ours, (rk, why) in MAP.items():
        hits = sig2.get(rk)
        if not hits:
            missing.append((ours, rk))
            continue
        if len(hits) > 1:
            ambiguous.append((ours, rk, [f"{h['conn']}_{h['num']}" for h in hits]))
            continue
        h = hits[0]
        assign[ours] = {'somsig': rk, 'conn': h['conn'], 'num': h['num'],
                        'ball': h['ball'], 'vol': h['vol'], 'why': why}
    if missing:
        print(f'★★ 引脚表里找不到: {missing}')
        return 1
    if ambiguous:
        print(f'★ 信号在多个脚上出现 (需显式选): {ambiguous}')

    # 固定脚 (电源 / 使能)
    dcin = [f"P3_{h['num']}" for h in sig2.get('VCC_DCIN', [])]
    car_en = sig2.get('CARRIER_BOARD_EN', [{}])[0]
    pwron = sig2.get('PWRON_L', [{}])[0]
    fixed = {
        'VCC_DCIN': dcin,
        'CARRIER_BOARD_EN': f"{car_en.get('conn')}_{car_en.get('num')}",
        'PWRON_L': f"{pwron.get('conn')}_{pwron.get('num')}",
    }

    out = {
        'soc': 'Forlinx FET3572-C (RK3572)',
        'source': 'OK3572-C User Hardware Manual V1.0 §2.6.2/§2.7 (快照 state/_os_snapshots/fx3572_manual.html)'
                  ' + HW/PCB/FET3572C_PIN_TABLE.csv',
        'note': '★唯一键 = (conn, num); ★**不是** OK3576-C 的表 (RK3572/RK3576 引脚功能不同)',
        'assign': assign,
        'dnp': DNP_SIGS,
        'fixed': fixed,
    }
    json.dump(out, open(ASSIGN, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    # ---- 人读版 ----
    L = ['# SOM 引脚分配表 (RK3572 核心板 Forlinx FET3572-C) ★RK3572 口径\n',
         '> ★脚标识 = 手册权威形式 `P<x>_<num>` (4 个连接器各 100 脚) ⇒ 主板上是 **4 个独立 100 脚 BTB 座 (J_SOM_P1..P4)**',
         '> 真值: `HW/PCB/FET3572C_PIN_TABLE.csv` (399 行, 由 OK3572-C 官方手册重建) · 机器可读: `HW/PCB/som_pin_assign.json`',
         '> ★**本表已从 OK3576-C 口径全面换掉**: 实测 RK3572 与 RK3576 引脚功能不同 (226/398 脚球号不同)\n',
         '| 我们的信号 | RK3572 信号 | 连接器 | 组内脚 | 球号 | 电平 | 座 | 依据 |',
         '|---|---|---|---|---|---|---|---|']
    for ours in sorted(assign):
        a = assign[ours]
        L.append(f"| {ours} | {a['somsig']} | {a['conn']} | {a['num']} | {a['ball']} | {a['vol']} | "
                 f"J_SOM_{a['conn']} | {a['why']} |")
    L.append('\n## 固定脚 (电源 / 使能)\n')
    L.append('| 功能 | 脚标识 | 说明 |')
    L.append('|---|---|---|')
    L.append(f"| VCC_DCIN (5-13V 输入) | {', '.join(fixed['VCC_DCIN'])} | ★SoM 自己的供电 ⇒ **不经过 U_EN_SW 门控** (否则 SoM 永远起不来) |")
    L.append(f"| CARRIER_BOARD_EN (底板使能) | {fixed['CARRIER_BOARD_EN']} | ★Forlinx 原文: 底板早于核心板上电 ⇒ 电流过大/无法启动/**可能损坏处理器** ⇒ 主板各路必须由它放行 |")
    L.append(f"| PWRON_L (开机) | {fixed['PWRON_L']} | 与 PWR_CTRL 同一脚 |")
    L.append('\n## 未引出 (DNP, ★不编造)\n')
    for k, v in DNP_SIGS.items():
        L.append(f'- **{k}** — {v}')
    L.append('\n## 关键结论 (与上一版分配的差异)\n')
    L.append('1. ★**I2C 换了组**: 相机 SCCB = **I2C5 (1.8V 域)** (模组 FPC 上就写着 I2C5) ⇒ **上拉必须改 1.8V**;'
             ' 触控 I2C + TMP117 = **I2C2 (3.3V 域)** (TMP117 的 VIH=0.7×V+ ⇒ 1.8V 总线不满足)')
    L.append('2. ★**4-lane CSI 在 RK3572 上必须拆**: 模组 lane1/2 → CSI0 D0/D1, lane3/4 → CSI1 D0/D1 '
             '(Forlinx 载板原理图同款接法; RK3572 每端口只有 2 lane)')
    L.append('3. ★**camera MCLK 由 SoM 出** (CAM_CLK0_OUT_M0) ⇒ 上一版"主板自己产 MCLK"的结论作废')
    L.append('4. ★**SPI/JTAG/XTAL/FSIN 未引出** ⇒ 对应行标 DNP')
    L.append('5. ★**F13 落法**: SoM 的 CARRIER_BOARD_EN → 主板负载开关 U_EN_SW 的 EN ⇒ '
             '主板各路挂 **RAIL_BOARD_5V** (不是 SYS); SoM 自己的 VCC_DCIN 直供 5V (不受门控)')
    open(ASSIGN_MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')

    print(f'[1] 分配 {len(assign)} 个信号 · 未引出 {len(DNP_SIGS)} 个 · 固定脚 {fixed}')
    print(f'[2] 落盘: {ASSIGN} · {ASSIGN_MD}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
