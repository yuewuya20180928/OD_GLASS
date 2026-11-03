#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_land_20261103_b.py —— 落盘 A2 段完成 + 焊盘编号修正的验收结果

★★ 验收证据 (全部机器复算, 已在本机跑过):
  · 网表: `state/check_netlist.py` ✅ · `state/check_netlist_pins.py` ✅ (针脚冲突 0 / SoC 节点全部落到真实引脚)
  · 板: `state/check_pcb_nets.py` ✅ (焊盘级等价 550/550 · 4 个 SOM 座各 100 焊盘 · C3 不符 0)
        ★`--selftest` ✅ (故意对调 CONN_CAM pin2/pin3 ⇒ 门禁 rc=1 ⇒ 不是假绿)
  · DRC: `state/check_pcb_drc.py` ✅ (violations = 0 · Gerber 30 + 钻孔已按新板重出)
  · 项目门: merge / issue_check / daily_check ✅ (无漂移)
"""
import os
import sys

import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
LOG = f'{PROJ}/state/issue_log.yaml'
TRK = f'{PROJ}/PROJECT_TRACKER.md'

VERIFY = ('机跑验收 2026-11-03 09:4x: check_netlist ✅ + check_netlist_pins ✅ (C1 冲突 0 · C5b 未分配 0) + '
          'check_pcb_nets ✅ (焊盘级 550/550 · C2 4 个 SOM 座各 100 焊盘 · C3 不符 0 · --selftest ✅ 脚位对调被抓) + '
          'check_pcb_drc ✅ (DRC violations = 0 · Gerber 30 + 钻孔) + merge/issue_check/daily_check ✅ 无漂移')


def main():
    d = yaml.safe_load(open(LOG, encoding='utf-8'))
    by_id = {i['id']: i for i in d['issues']}

    i165 = by_id.get('ISS-165')
    if i165:
        i165['status'] = 'fixed'
        i165['fix_ref'] = ('HW/PCB/FET3572C_PIN_TABLE.csv (399 行 · RK3572 口径) · HW/PCB/som_pin_assign.json · '
                           'HW/PCB/SOM_PIN_ASSIGNMENT.md · HW/PCB/som_btb_params.json · '
                           'state/som_btb_footprint.py (BTB 座封装模块) · state/_iss165_a2_som.py · '
                           'state/_patch_a2_som_netlist.py · state/check_netlist_pins.py · '
                           'HW/PCB/demo_mainboard.kicad_pcb (204 器件 / 905 焊盘 / 4×100pin BTB)')
        i165['verify_result'] = 'pass'
        i165['verify_date'] = '2026-11-03'
        i165['verify_by'] = 'main'
        i165['note'] = (i165.get('note', '') +
                        ' ★★2026-11-03 09:4x **A2 段完成**: ① **4 组 100pin BTB 座已上板** '
                        '(Hirose DF40C-100DS-0.4V(51), 0.4mm pitch / 0.2mm 焊盘 / 行距 2.38mm; '
                        '脚号=网表真实针号, 奇数脚一排偶数脚一排 ⇒ 对插 SoM 的 n 脚); '
                        '实际用到 45 脚 (P1=11/P2=9/P3=11/P4=14) ⇒ 板 400 个焊盘 (355 个 NC) ✓; '
                        '② **SoC 节点全部落到真实引脚** (`soc_pin()` 查分配表, 未分配直接报错 ⇒ 占位符物理上进不了网表); '
                        '③ **F13 落地**: CARRIER_BOARD_EN(P3_87) → U_EN_SW → RAIL_BOARD_5V, 底板各路改挂 RAIL_BOARD_5V, '
                        'SoM 自己的 VCC_DCIN(P3_91/93/95/97/98/99/100) 直供 5V 不受门控; '
                        '④ **camera MCLK 走 SoM 的 CAM_CLK0_OUT_M0**; ⑤ **I2C_A 改 1.8V 域** (I2C5) + TMP117 挪 I2C_B; '
                        '⑥ **SPI/JTAG/FSIN 未引出 ⇒ DNP**; ⑦ demo 板自带 Type-C (J_DEMO_USB) 进网表 (SoM 要 5~13V). '
                        '★**遗留 (⇒ 板子还不能下单)**: (a) 4 个座的**机械位置与 pin1 方向**只从手册底面图读出, '
                        '未与原厂 DXF/实物核对 (ISS-169); (b) 14 个 IC 的真实封装/脚号未落定 (焊盘号仍是行序占位, '
                        '见 check_pcb_nets C4 的 191 个占位器件清单); (c) **板子目前是连通性骨架, 未布线** '
                        '(unconnected 401, 骨架阶段允许). ' + VERIFY)

    i167 = by_id.get('ISS-167')
    if i167:
        i167['status'] = 'fixed'
        i167['fix_ref'] = ('state/gen_pcb_netlist_board.py (derive_pads: 焊盘号=网表真实针号) · '
                           'state/check_pcb_nets.py (焊盘级门禁 + --selftest + NC 焊盘规则) · '
                           'state/som_btb_footprint.py · HW/PCB/demo_mainboard.kicad_pcb')
        i167['verify_result'] = 'pass'
        i167['verify_date'] = '2026-11-03'
        i167['verify_by'] = 'main'
        i167['note'] = (i167.get('note', '') +
                        ' ★★2026-11-03 09:3x-09:4x 已修: ① 生成器改成按**网表节点里的真实针号**建焊盘 '
                        '(归属以节点串里的器件名为准; 命名脚 IC 仍按行序并出占位清单) ⇒ '
                        '焊盘 393 → **905** (204 器件), 带网绑定 **550**, 缺失 0 多余 0 同号异网 0; '
                        '② 门禁升级成**焊盘级** (ref,pad)→net 比对 + 连接器针号集合 + 器件焊盘数 + '
                        '**NC 焊盘白名单** (只允许 SOM 的 4 组 100 脚座未用脚) + `--selftest` 自检; '
                        '③ ★**反证**: 新门禁查旧板 ⇒ rc=1 (缺 168/多 21/同号异网 165) ⇒ 旧门禁确为假绿; '
                        '自检里对调 CONN_CAM pin2/pin3 ⇒ C1 报"同号异网 2" ⇒ 脚位对调抓得住; '
                        '④ 骨架生成器 gen_kicad_project.py 改为写 _frame_reference.kicad_pcb ⇒ '
                        '**两个生成器不再抢同一个板文件** (原顺序决定结果 = 第三个假绿来源); '
                        '⑤ 器件排布区 x0 从 72 挪到 78 (避开 SOM 承载区 8..76)。 ' + VERIFY)

    i169 = by_id.get('ISS-169')
    if i169:
        i169['note'] = (i169.get('note', '') +
                        ' ★★2026-11-03 09:4x 更新: ① 4 个 BTB 座**已上板**(几何参数集中在 '
                        '`HW/PCB/som_btb_params.json`: pitch 0.4 / 焊盘 0.2×1.4 / 行距 2.38 / 座 22.6×3.2); '
                        '★**行距与焊盘长度是按 Hirose 目录的 2.38/3.78 两个综合尺寸取自洽解, 未与原厂工程图核对** '
                        '⇒ ★**采购硬判据: 下料前必须用 DF40C-100DS 工程图/实物核对行距、焊盘长度、pin1 方向**; '
                        '② demo 板自带 Type-C (J_DEMO_USB) 已进网表 (SoM 的 VCC_DCIN 要 5~13V ⇒ 主板必须有 5V 入口) '
                        '⇒ 整机阶段这块 DNP (整机走跨铰链 USB + 充电板) ⇒ **整机要不要在镜脚也留 Type-C 需老板拍板**; '
                        '③ ★**SoM 自带 PMIC** (P3_10 = PMIC_VDC) ⇒ 主板**不产** SoC 的核心/IO 轨 '
                        '(U_DCDC_VCORE/U_DCDC_VIO 已标 DNP, 连带 Q_ENVC/Q_AND/R_EN_VCORE 整条时序链 DNP) '
                        '⇒ 板子上的电源树少了一半; ④ 14 个 IC 的真实封装/脚号仍未落定 ⇒ 板子还是"连通性骨架"。')

    yaml.safe_dump(d, open(LOG, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False,
                   default_flow_style=False, width=10000)
    print(f'✅ issue_log.yaml 已落盘 (ISS-165/167 → fixed, ISS-169 更新)')

    # ---- tracker ----
    s = open(TRK, encoding='utf-8').read()
    sec = '''
#### (1.70) ★★★★ 2026-11-03 09:3x-09:4x: ★★**A2 段完成 —— 4 组 100pin BTB 座上板 + 三道门禁全绿**

> **落账**: `HW/PCB/som_btb_params.json` (BTB 几何参数 · 可核可改) · `state/som_btb_footprint.py` (封装模块) ·
> `state/check_netlist_pins.py` (针脚级门禁) · `state/check_pcb_nets.py` (焊盘级门禁 + `--selftest`) ·
> `HW/PCB/demo_mainboard.kicad_pcb` (204 器件 / 905 焊盘 / 4×100pin BTB / DRC 0 / Gerber 30)

★**A2 段交付的四件事**:
① **4 组 100pin BTB 座上板** —— Hirose `DF40C-100DS-0.4V(51)` (载板侧插座; SoM 侧是 100DP);
   手册 §5 的 "A=22.6 B=19.6 C=3.2 D=1.45" 与 Hirose 目录 `DF40C-100DS` 行**逐字一致** ⇒ 型号认定成立;
   几何: pitch 0.4 / 焊盘 0.2×1.4 / 行距 2.38 / 脚号=网表真实针号 (**奇数脚一排、偶数脚一排** ⇒ 对插 SoM 的 n 脚)
   ⇒ 实际用到 45 脚 (P1=11 · P2=9 · P3=11 · P4=14), 板上 400 焊盘 (355 个 NC)
② **SoC 节点全部落到真实引脚** —— 新增 `soc_pin()`: 查 `HW/PCB/som_pin_assign.json`, **未分配引脚直接报错退出**
   ⇒ ★**`SoC[RK3572].<信号>` 这种占位符从物理上不可能再进网表**
③ **F13 底板电源使能** —— `CARRIER_BOARD_EN (P3_87)` → 负载开关 `U_EN_SW` → `RAIL_BOARD_5V`;
   底板 4 颗 LDO 的输入与 EN 全部改挂 RAIL_BOARD_5V; ★**SoM 自己的 VCC_DCIN (P3_91/93/95/97/98/99/100)
   直供 5V, 不受门控** (否则 SoM 永远起不来)
④ **demo 板自带 Type-C** (`J_DEMO_USB`) —— SoM 的 VCC_DCIN 要 5~13V ⇒ 主板必须有 5V 入口
   (老板 11-02 19:25: "demo 直接 USB-C 5V 供电, 不装电池、不上充电链"); 整机阶段这块 DNP

★★ **顺带查实并改掉的四条** (都是"照旧做就会错"的级别):
① **SoM 自带 PMIC** (P3_10 = `PMIC_VDC`) ⇒ 主板**不产** SoC 的核心/IO 轨 ⇒ `U_DCDC_VCORE`/`U_DCDC_VIO`
   及其整条时序链 (Q_ENVC / Q_AND / R_EN_VCORE / R_PG_PULL) **全部 DNP** ⇒ 板子电源树少一半
② **camera MCLK 由 SoM 出** (`CAM_CLK0_OUT_M0` = P2_45) ⇒ 上一版"主板自己产 MCLK"作废
③ **相机 SCCB 走 I2C5 (1.8V 域)** ⇒ ★**I2C_A 上拉必须 1.8V** (旧写法 3.3V ⇒ SoM 的 1.8V 脚过压);
   TMP117 (VIH = 0.7×V+) 挪到 3.3V 的 I2C2 (触控那条)
④ **SPI / JTAG / FSIN 在 FET3572-C 上未引出** ⇒ 标 DNP (不编造); 调试走 UART0

★★★ **三道门禁全绿** (每道都机器可复算):
| 门禁 | 判据 | 结果 |
|---|---|---|
| `check_netlist_pins.py` | C1 一个针脚只能属于一个网 · C2/C3 连接器针数与针号 · C4 同件同板 · C5 SoC 节点落到真实引脚 | ✅ 冲突 0 · 31/31 · 40/40 · 未分配 0 |
| `check_pcb_nets.py` | C1 **(ref,pad)→net 焊盘级等价** · C2 针号集合 · C3 焊盘数 · NC 白名单 | ✅ 550/550 · 缺失 0 · 多余 0 · 同号异网 0 |
| `check_pcb_drc.py` | DRC violations = 0 · 生产文件齐 | ✅ 0 违规 · Gerber 30 + 钻孔 |

★**★ 假绿的三个来源都被堵上了** (这才是今天最值钱的东西):
① 门禁比 **(ref,net) 集合** ⇒ 脚位对调免疫 ⇒ 改成比 **(ref,pad)→net**, 并加 `--selftest`
   (故意对调 CONN_CAM pin2/pin3 ⇒ 必须 rc=1) ⇒ ★**新门禁查旧板 ⇒ rc=1 (缺 168/多 21/同号异网 165)** ⇒ 旧门禁确为假绿
② 两个生成器**抢同一个板文件** ⇒ 门禁顺序决定结果 ⇒ 骨架生成器改写 `_frame_reference.kicad_pcb`
③ 补丁脚本改结构化文本时**子串拼接** (`"REF pin11"REF pin20"`) ⇒ 新门禁的正则匹配不上 ⇒ **静默漏过**
   ⇒ ★**教训**: 门禁要能抓"格式非法", 不只抓"值不对"

★★ **诚实结论 (板子还不能下单)**: ① 4 个座的**行距/焊盘长度/pin1 方向**是按 Hirose 目录的 2.38/3.78
两个综合尺寸取的自洽解, **未与原厂工程图/实物核对** ⇒ 采购硬判据; ② 14 个 IC 的真实封装/脚号未落定
(焊盘号仍是行序占位, 191 个占位器件清单见 `check_pcb_nets` C4) ⇒ 板子目前是**连通性骨架**, 未布线
(unconnected 401); ③ ★**整机要不要在镜脚也留一个 Type-C, 需要老板拍板** (demo 版主板自带, 整机版 DNP)。
'''
    if '(1.70)' not in s:
        s = s.rstrip() + '\n' + sec
        open(TRK, 'w', encoding='utf-8').write(s)
        print('✅ PROJECT_TRACKER.md 已加 §(1.70)')

    # ---- 记忆追加 ----
    mem = '/home/yuewuya/.openclaw/workspace/memory/2026-11-03.md'
    m = open(mem, encoding='utf-8').read()
    m += '''
## ★★ 09:4x A2 段完成 (板子这一侧)

· **4 组 100pin BTB 座上板**: Hirose DF40C-100DS-0.4V(51) (载板侧) / DF40C-100DP (SoM 侧);
  手册 §5 的 A/B/C/D 与 Hirose 目录逐字一致 ⇒ 型号认定; 几何参数集中在 `HW/PCB/som_btb_params.json`
  (pitch 0.4 / 焊盘 0.2×1.4 / 行距 2.38) ⇒ ★**行距与焊盘长度是自洽解, 下料前必须用原厂工程图核对**
· **SoC 节点全部落到真实引脚**: 新增 `soc_pin()` ⇒ 未分配引脚直接报错 ⇒ 占位符物理上进不了网表
· **F13 落地**: CARRIER_BOARD_EN(P3_87) → U_EN_SW → RAIL_BOARD_5V; SoM 自己的 VCC_DCIN 直供 5V 不受门控
· **SoM 自带 PMIC** ⇒ 主板不产 SoC 核心/IO 轨 ⇒ 两颗 DC-DC + 整条时序链 DNP ⇒ 电源树少一半
· 三道门禁全绿 (针脚级 / 焊盘级 / DRC=0) + Gerber 30 重出

★**三条可复用的方法论**:
1. ★★**假绿有三个来源**: ① 门禁比集合而不是比"带键的映射" ⇒ 脚位对调免疫;
   ② 两个生成器抢同一个产物文件 ⇒ 门禁顺序决定结果; ③ 补丁脚本子串拼接 ⇒ 门禁正则匹配不上 ⇒ 静默漏过
   ⇒ **每个都要单独堵**, 而且要有"故意做错 ⇒ 门禁必须失败"的自检
2. ★★**换料/换代型时要查"自己那颗料"的手册** —— RK3572 与 RK3576 同名接口的球号都不同
3. ★★**SOM 自带 PMIC ⇒ 主板不用产 SoC 的核心/IO 轨** —— 这类"模块已经内部解决"的项要主动砍, 板子电源树会小一半
'''
    open(mem, 'w', encoding='utf-8').write(m)
    print('✅ memory/2026-11-03.md 已追加')
    return 0


if __name__ == '__main__':
    sys.exit(main())
