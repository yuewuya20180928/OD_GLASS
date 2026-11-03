#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_land_20261103.py —— 把 2026-11-03 上午的发现与修复落盘 (台账 + tracker + 记忆)

★★ 这次要落的**核心事实** (全部可复算, 别再走回头路):
  ① ★★**RK3572 与 RK3576 的引脚功能不同** (226/398 脚球号不同) ⇒ 上一版分配表 (基于 3576) 作废
     ⇒ 重新抓 Forlinx **OK3572-C** 手册 (§2.6.2/§2.7) 重建 399 行逐针表, 并与 Forlinx 载板原理图
     的球号逐脚互证 (12/12 对上)
  ② ★★**网表的连接器脚位有 12+9 处一个脚挂多个网** (短路级) —— A1 段改了针位却留着旧 18p/22p 跨铰链版的行
  ③ ★★**板生成器按 CSV 行序给焊盘编号** ⇒ 连接器脚位全错; 而"板↔网表等价性"门禁比的是 (ref,net) 集合 ⇒ **假绿**
  ④ ★★**FET3572-C 未引出 SPI / JTAG / FSIN**; camera MCLK 其实**由 SoM 出** (CAM_CLK0_OUT_M0)
  ⑤ ★★相机 SCCB 走 **I2C5 (1.8V 域)** ⇒ 旧网表把 I2C_A 上拉到 3.3V ⇒ **SoM 的 1.8V 脚被灌 3.3V**
"""
import datetime
import os
import sys

import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
LOG = f'{PROJ}/state/issue_log.yaml'
TODAY = '2026-11-03'
NOW = '2026-11-03 10:4x'

NEW_ISSUES = [
    {
        'id': 'ISS-166',
        'title': '★★★[P0 · 短路级] 网表连接器脚位: 一个脚挂多个网 (CONN_CAM 12 处 / CONN_LIGHT 9 处) ⇒ 投板即短路',
        'severity': 'blocker',
        'source_blocker': None,
        'source_agent': 'main',
        'desc': '★2026-11-03 09:3x 实测: A1 段 (11-02 20:5x) 把 FPC 座针位改成模组原厂表 '
                '(Radxa Camera 4K 31 针 / Display 40 针), **但没删掉 A1 之前的 18p/22p 跨铰链版的行** '
                '⇒ 同一个脚上挂着 2~4 个网 (例: CSI_D0_CK_P 同时在 CONN_CAM pin1 与 pin18; '
                'CSI_MCLK 同时在 pin11 与 pin20; I2C_A_SDA 同时在 pin14 与 pin25; '
                'SENSOR_AVDD 在 pin15 (而 pin15 其实是 MDP1); CSI_RESET_N 在 pin12 (其实是 MDP2)) '
                '⇒ **板子上就是短路** ⇒ 相机/屏模组一插就烧。',
        'owner': 'main',
        'reporter': 'main',
        'raised': TODAY,
        'due': '2026-11-03',
        'status': 'fixed',
        'external': False,
        'need_keys': [],
        'fix_ref': 'state/_patch_netlist_fpc_pins.py + state/_patch_netlist_pins2.py + state/_patch_netlist_tp_concat.py '
                   '· HW/PCB/FPC_PIN_TABLES.md (模组原厂针位表) · state/check_netlist_pins.py (新门禁)',
        'verify_by': 'hw-lead',
        'verify_result': None,
        'verify_date': None,
        'note': '★已修: 删旧行 15 处 + 测试点改挂真实针脚 13 处 + 连接器声明行不再占脚 5 处 + '
                '新增**针脚级门禁** `state/check_netlist_pins.py` (C1 一个针脚只能属于一个网 / C2 针数 / '
                'C3 针号连续 / C4 同件同板 / C5 SoC 节点落到真实引脚) ⇒ 现在 **C1 冲突 0 处**, '
                'CONN_CAM 31/31 · CONN_LIGHT 40/40。★**教训**: 改针位表时必须同时删旧行, '
                '而且要有"一个脚一个网"的门禁兜底 —— 原来的门禁只看连接关系, 看不出脚位冲突。',
        'dispatched_at': TODAY,
    },
    {
        'id': 'ISS-167',
        'title': '★★★[P0 · 假绿] 板生成器按 CSV 行序给焊盘编号 ⇒ 连接器脚位全错; 等价性门禁比集合 ⇒ 报绿',
        'severity': 'blocker',
        'source_blocker': None,
        'source_agent': 'main',
        'desc': '★2026-11-03 09:2x 实测: `state/gen_pcb_netlist_board.py` 的 group_refs() '
                '**按 (ref,net) 去重 + 按 CSV 行序编号** ⇒ (a) 连接器上多个同网脚 (CONN_CAM 8 个 GND 脚) '
                '被合并成 1 个焊盘 (31 脚只剩 21 个); (b) 焊盘号 ≠ 网表里的真实针号 '
                '(实测板上 CONN_LIGHT pad2=GND 而网表要求 pad2=DSI_D0_CK_N; U_TEMP pad1/pad2 的 SCL/SDA 相反) '
                '⇒ ★**而 `state/check_pcb_nets.py` 比的是 (ref,net) 集合** ⇒ 这种错误它照样报绿 '
                '⇒ **"板子 ↔ 网表逐点等价" 这条验收线一直是假绿** ⇒ 若照此下单 = 白板 + 短路。',
        'owner': 'main',
        'reporter': 'main',
        'raised': TODAY,
        'due': '2026-11-03',
        'status': 'fixing',
        'external': False,
        'need_keys': [],
        'fix_ref': 'state/gen_pcb_netlist_board.py · state/check_pcb_nets.py (焊盘级门禁, 派 hw 子 agent 改)',
        'verify_by': 'hw-lead',
        'verify_result': None,
        'verify_date': None,
        'note': '★修法: ① 生成器按**网表节点里的真实针号**建焊盘 (node1/node2 形如 "<COMP> pin<N>"), '
                '命名脚 IC 仍按行序并出"占位清单"; ② 门禁改成比 **(ref, pad号) → net** 集合, '
                '并加"脚位对调"必挂的检查; ③ 另: `state/gen_kicad_project.py` (骨架生成器) 与 '
                'gen_pcb_netlist_board.py **抢同一个板文件** ⇒ DRC 门禁的 C5 一跑就把网表板覆盖成 10 脚骨架 '
                '⇒ **门禁顺序决定结果 = 又一个假绿来源** ⇒ 要把骨架生成器改写到别的文件名。',
        'dispatched_at': TODAY,
    },
    {
        'id': 'ISS-168',
        'title': '★★★[P0] RK3572 与 RK3576 引脚功能不同 ⇒ 上一版 SoM 引脚分配表作废 (226/398 脚球号不同)',
        'severity': 'blocker',
        'source_blocker': None,
        'source_agent': 'main',
        'desc': '★2026-11-03 09:1x 实测: 上一版 SoM 引脚分配用的是 **OK3576-C 手册** (FET3576-C) 的逐针表 '
                '⇒ 但我们是 **FET3572-C (RK3572)** ⇒ 两只 SoM 的**同一连接器脚位上球号都不同** (226/398) '
                '⇒ 例: P1_56 在 3576 是 I2C8_SCL_M2, 在 3572 是 GPIO2_B6_d; P1_50 在 3576 是 GPIO2_B5_d, '
                '在 3572 是 GPIO2_B0_d ⇒ **照旧表画板 = 接错功能**。'
                '⇒ "FET3572-C 与 FET3576-C 引脚兼容" 的说法只在**机械/连接器**层面成立, **电气功能不通用**。',
        'owner': 'main',
        'reporter': 'main',
        'raised': TODAY,
        'due': '2026-11-03',
        'status': 'fixed',
        'external': False,
        'need_keys': [],
        'fix_ref': 'state/_iss165_som_pins_rebuild.py · HW/PCB/FET3572C_PIN_TABLE.csv (399 行) · '
                   'HW/PCB/SOM_PIN_VERIFY.md · HW/PCB/som_pin_assign.json · HW/PCB/SOM_PIN_ASSIGNMENT.md · '
                   'state/_os_snapshots/fx3572_manual.html (手册快照)',
        'verify_by': 'hw-lead',
        'verify_result': None,
        'verify_date': None,
        'note': '★已修: 重新抓 Forlinx **OK3572-C** 官方手册 (github pages, 公开) ⇒ §2.6.2 八张引脚表 '
                '(4 连接器 × 奇/偶脚表) + §2.7 功能表 ⇒ 重建 399 行逐针表 (表序→连接器 + 功能表反查互证) '
                '⇒ 与 OK3576-C 手册交叉验证 + ★**与 Forlinx 载板原理图 SoM 球号逐脚互证 12/12 对上** '
                '(B19/A19/1B14/1C14/A20/B20/A22/B22/A23/B23/1B16/1C16 全中) ⇒ 分配表按 RK3572 口径重做 (46 个信号)。'
                '★**教训**: "引脚兼容" 要分清**机械兼容**与**电气功能兼容** —— 后者必须查**自己那颗料**的手册。',
        'dispatched_at': TODAY,
    },
    {
        'id': 'ISS-169',
        'title': '★★[demo 板可制造性] demo 主板的供电/USB 入口缺失 + SoM 4×100pin BTB 座待画 (机械位置未核实)',
        'severity': 'high',
        'source_blocker': None,
        'source_agent': 'main',
        'desc': '★2026-11-03 10:0x 盘板子可制造性时暴露三件事: '
                '① **SoM 的 VCC_DCIN 要 5~13V** (手册 §2.4.2) ⇒ 主板必须有 5V 输入 ⇒ demo 板必须自带 Type-C '
                '(老板 11-02 19:25 已拍板"demo 直接 USB-C 5V 供电, 不装电池、不上充电链") '
                '⇒ 本轮已在网表里加 J_DEMO_USB + VBUS 检测分压 + U_EN_SW 门控; '
                '② **4 个 100pin BTB 座的机械位置/pin1 方向**只从手册底面尺寸图读出 (2×2, 中心距 34×43mm), '
                '**未与原厂 DXF/实物核对** ⇒ ★**下料前必须核** (子 agent 在查公开载板工程, 结果见 '
                'HW/PCB/SOM_CONNECTOR_GEOMETRY_PROBE.md); '
                '③ 主板上 14 个 IC 的**真实封装/脚号**仍未落定 (BOM 里 OPN 多为"待选型") ⇒ 板子目前只能算'
                '"连通性骨架", **不能下单**。',
        'owner': 'main',
        'reporter': 'main',
        'raised': TODAY,
        'due': '2026-11-05',
        'status': 'open',
        'external': False,
        'need_keys': [],
        'fix_ref': 'HW/PCB/SOM_CONNECTOR_GEOMETRY_PROBE.md (待子 agent 交) · HW/PCB/SOM_PIN_ASSIGNMENT.md',
        'verify_by': 'hw-lead',
        'verify_result': None,
        'verify_date': None,
        'note': '★给老板的一句: **这块板子现在还不能下单** —— ① 4 个 BTB 座的机械位置与 pin1 方向要核实; '
                '② IC 封装/脚号没落定 (现在是占位); ③ 相机 4-lane 在 RK3572 上是 CSI0+CSI1 拼, 需软件侧配对。',
        'dispatched_at': TODAY,
    },
]


def main():
    d = yaml.safe_load(open(LOG, encoding='utf-8'))
    issues = d['issues']
    by_id = {i['id']: i for i in issues}

    # ---- 更新 ISS-165 ----
    i165 = by_id.get('ISS-165')
    if i165:
        i165['status'] = 'fixing'
        i165['dispatched_at'] = TODAY
        i165['fix_ref'] = ('HW/PCB/FET3572C_PIN_TABLE.csv (399 行 · RK3572 口径) · HW/PCB/som_pin_assign.json · '
                           'HW/PCB/SOM_PIN_ASSIGNMENT.md · state/_iss165_a2_som.py (分配表生成) · '
                           'state/_patch_a2_som_netlist.py (网表改挂 + F13 电源使能) · '
                           'state/check_netlist_pins.py (新门禁)')
        i165['note'] = (i165.get('note', '') +
                        ' ★★2026-11-03 10:4x 续作结论: ① **真值换了** —— RK3572 与 RK3576 引脚功能不同 '
                        '(226/398 脚球号不同) ⇒ 上一版分配表作废, 改用 **OK3572-C 手册**重建 399 行逐针表 '
                        '(与 Forlinx 载板原理图球号互证 12/12); ② **SoC 节点已全部改挂真实引脚** '
                        '(网表里 `SoC[RK3572].X` 占位符**物理上不可能再出现**, 未分配引脚会直接报错退出); '
                        '③ **F13 已落**: CARRIER_BOARD_EN (P3_87) → 负载开关 U_EN_SW → RAIL_BOARD_5V, '
                        '底板各路改挂 RAIL_BOARD_5V, SoM 自己的 VCC_DCIN (P3_91/93/95/97/98/99/100) 直供 5V 不受门控; '
                        '④ **camera MCLK 走 SoM 的 CAM_CLK0_OUT_M0** ⇒ 上一版"主板自己产 MCLK"作废; '
                        '⑤ **SPI/JTAG/FSIN 未引出** ⇒ 标 DNP; ⑥ **相机 SCCB 走 I2C5 (1.8V 域)** ⇒ '
                        'I2C_A 上拉改 1.8V (旧写法 3.3V ⇒ SoM 1.8V 脚过压), TMP117 挪到 I2C_B (3.3V, VIH=0.7×V+). '
                        '★**遗留**: 4 个 BTB 座的机械位置/pin1 方向待核实 (ISS-169) ⇒ **板子还不能下单**。')

    # ---- 新开 ----
    for ni in NEW_ISSUES:
        if ni['id'] not in by_id:
            issues.append(ni)
            print(f'  [新开] {ni["id"]} · {ni["title"][:60]}')

    yaml.safe_dump(d, open(LOG, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False,
                   default_flow_style=False, width=10000)
    print(f'✅ issue_log.yaml 已落盘 (共 {len(issues)} 条)')

    # ---- tracker ----
    tr = f'{PROJ}/PROJECT_TRACKER.md'
    s = open(tr, encoding='utf-8').read()
    sec = '''
#### (1.69) ★★★★ 2026-11-03 09:0x-10:4x: ★★**"板子能下单"这件事被重新审了一遍 —— 查出 3 个 P0 (含 2 个假绿)**

> **落账**: `HW/PCB/FET3572C_PIN_TABLE.csv` (399 行 · RK3572 口径) · `HW/PCB/SOM_PIN_VERIFY.md` ·
> `HW/PCB/som_pin_assign.json` + `HW/PCB/SOM_PIN_ASSIGNMENT.md` · `state/check_netlist_pins.py` (针脚级门禁) ·
> `HW/PCB/GEN_SELF_CHECK.txt` · 新开 ISS-166/167/168/169

★**背景**: 11-03 09:05 token 恢复 ⇒ 续作 ISS-165 (A2 段: SOM 座接入)。续作时先按"恢复协议"读了
`PROGRESS_SNAPSHOT.md` + `memory/2026-11-02.md` 的交接 (明早第一件事 = `check_pcb_nets` 判"不等价 ⇒ 板子不能下单")。

★★★ **查实并修掉的三个 P0** (全部有可复算证据, 不是推测):

**P0-1 ★★网表里连接器脚位短路 (ISS-166)**
· 证据: `state/check_netlist_pins.py` 跑出 **CONN_CAM 12 个脚 / CONN_LIGHT 9 个脚各挂 2~4 个网**
  (例: `CSI_D0_CK_P` 同时在 pin1 与 pin18 · `CSI_MCLK` 同时在 pin11 与 pin20 · `SENSOR_AVDD` 在 pin15
  —— 而 **31 针表里 pin15 = MDP1 (MIPI 数据正脚)**, `CSI_RESET_N` 在 pin12 —— 而 pin12 = **MDP2**)
· 根因: A1 段 (11-02 20:5x) 改了针位, **没删 A1 之前 18p/22p 跨铰链版的行**
· 修: 删 15 处旧行 + 测试点改挂真实针脚 13 处 + 连接器"声明行"不再占脚 5 处 ⇒ **冲突 0 处**
· ★**新门禁**: `state/check_netlist_pins.py` —— C1 一个针脚只能属于一个网 / C2 针数 / C3 针号连续 /
  C4 同件同板 / C5 SoC 节点必须落到真实引脚 (未分配直接报错)

**P0-2 ★★板生成器按 CSV 行序编号 ⇒ 脚位全错, 而等价性门禁比集合 ⇒ 假绿 (ISS-167)**
· 证据: 板上 `CONN_LIGHT pad2 = GND` 而网表要求 `pad2 = DSI_D0_CK_N`; `U_TEMP pad1/pad2` 的 SCL/SDA 相反;
  CONN_CAM 31 脚只剩 21 个焊盘 (8 个 GND 脚被 (ref,net) 去重合并成 1 个)
· 根因: `gen_pcb_netlist_board.py` 的 `group_refs()` ① 按 (ref,net) 去重 ② 按行序编号
· 而 `check_pcb_nets.py` 比的是 **(ref,net) 集合** ⇒ 脚位对调它照样报绿 ⇒ ★**"板子↔网表逐点等价"这条验收线一直是假绿**
· ★**同类**: `gen_kicad_project.py` (骨架生成器) 与网表生成器**抢同一个板文件** ⇒ DRC 门禁的 C5 一跑就把
  网表板覆盖成 10 脚骨架 ⇒ **门禁顺序决定结果** ⇒ 又一个假绿来源

**P0-3 ★★RK3572 与 RK3576 引脚功能不同 ⇒ 上一版 SoM 分配表作废 (ISS-168)**
· 证据: 重新解析两份手册 ⇒ 同一连接器脚位上 **226/398 脚球号都不同** (P1_56: 3576=I2C8_SCL_M2 vs
  3572=GPIO2_B6_d; P1_50: 3576=GPIO2_B5_d vs 3572=GPIO2_B0_d)
· ⇒ ★**"FET3572-C 与 FET3576-C 引脚兼容"只在机械层成立, 电气功能不通用** ⇒ 必须查自己那颗料的手册
· 修: 抓 **OK3572-C** 官方手册 (github pages 公开) 重建 399 行 (4 座 × 奇/偶脚表) ⇒
  ★**与 Forlinx 载板原理图的 SoM 球号逐脚互证 12/12 对上** ⇒ 分配表按 RK3572 口径重做 (46 个信号)

★★★ **A2 段同时落地的四条结论**:
① **camera MCLK 由 SoM 出** (`CAM_CLK0_OUT_M0` = P2_45) ⇒ 上一版"主板自己产 MCLK"作废
② **相机 SCCB 走 I2C5 (RK3572 的 I2C5 是 1.8V 域)** ⇒ ★**I2C_A 上拉必须 1.8V** (旧写法 3.3V ⇒ SoM 的
   1.8V 脚被灌 3.3V); TMP117 (VIH=0.7×V+) 挪到 3.3V 的 I2C2 (触控那条)
③ **4-lane CSI 在 RK3572 上必须拆成 CSI0(2)+CSI1(2)** (Forlinx 载板同款接法; 每端口只有 2 lane)
④ **SPI / JTAG / FSIN 在 FET3572-C 上未引出** ⇒ 对应行标 DNP (不编造); 调试走 UART0

★★ **F13 (底板电源使能) 落法**: `CARRIER_BOARD_EN (P3_87)` → 负载开关 `U_EN_SW` → `RAIL_BOARD_5V`
⇒ 底板 4 颗 LDO 的输入与 EN 全部改挂 RAIL_BOARD_5V (不是 SYS); ★**SoM 自己的 VCC_DCIN
(P3_91/93/95/97/98/99/100) 直供 5V, 不受门控** (否则 SoM 永远起不来)。

★**给老板的实话**: ★**这块板子现在还不能下单** —— ① 4 个 BTB 座的机械位置/pin1 方向只从手册图读出,
**未与原厂 DXF/实物核对** (ISS-169); ② 主板 14 个 IC 的真实封装/脚号没落定 (BOM 里 OPN 多为"待选型")
⇒ 现在只能算"**连通性骨架**"; ③ demo 板自带 Type-C 已进网表 (SoM 要 5~13V ⇒ 必须有 5V 入口),
整机阶段这块是 DNP (整机走跨铰链 USB + 充电板) ⇒ **整机要不要在镜脚也留一个 Type-C, 需要你拍板**。
'''
    if '(1.69)' not in s:
        s = s.rstrip() + '\n' + sec
        open(tr, 'w', encoding='utf-8').write(s)
        print('✅ PROJECT_TRACKER.md 已加 §(1.69)')

    # ---- 记忆 ----
    mem = '/home/yuewuya/.openclaw/workspace/memory/2026-11-03.md'
    m = '''# 2026-11-03 (ARS45 智能眼镜 · demo 主板)

## 09:05 token 恢复 ⇒ 续作 ISS-165 (A2 段: SoM 座接入)

★**恢复协议有效**: 先读 `PROGRESS_SNAPSHOT.md` + `memory/2026-11-02.md` 的交接 ⇒ 知道"明早第一件事 =
check_pcb_nets 判不等价 ⇒ 板子不能下单"。但**真正的问题比交接里写的更早** ⇒ 续作时先做了"针脚级"审查。

## ★★★ 今天查实并修掉的三个 P0

① **网表连接器脚位短路** (ISS-166): CONN_CAM 12 脚 / CONN_LIGHT 9 脚各挂 2~4 个网
   (A1 段改了针位却没删旧 18p/22p 行) ⇒ 已删 15 处旧行 + 测试点改挂 13 处 ⇒ 新门禁 `state/check_netlist_pins.py`
② **板生成器按 CSV 行序编号 ⇒ 脚位全错; 等价性门禁比集合 ⇒ 假绿** (ISS-167): 板上 CONN_LIGHT pad2=GND
   而网表要求 DSI_D0_CK_N; U_TEMP 的 SCL/SDA 相反; CONN_CAM 31 脚只剩 21 个焊盘
③ **RK3572 与 RK3576 引脚功能不同** (ISS-168): 226/398 脚球号不同 ⇒ "引脚兼容"只在机械层成立
   ⇒ 重新抓 Forlinx **OK3572-C** 手册重建 399 行逐针表 (与载板原理图球号互证 12/12) ⇒ 分配表作废重做

## ★★ 方法论沉淀 (三条)

1. ★★**"等价性门禁"要比 (ref, pad号) → net, 不能比 (ref, net) 集合** —— 后者对"脚位对调"完全免疫
   (这跟 ISS-157 的 rknn_bench 缓存 bug 是同一类: **绿灯测的不是要测的东西**)
2. ★★**改针位表必须同时删旧行, 并且要有"一个脚一个网"的门禁兜底** —— 只查连接关系的门禁看不出脚位冲突
3. ★★**"引脚兼容"要分机械兼容与电气功能兼容** —— 后者必须查自己那颗料的手册 (RK3572 vs RK3576)

## ★★ 补丁脚本自身的坑 (自己踩的)

★`_patch_netlist_fpc_pins.py` 里用 `old[:old.rfind('"')] + new + '"'` 做替换 ⇒ **rfind 找的是整条 tuple 的
最后一个引号, 不是目标字段的引号** ⇒ 拼出 `"CONN_CAM pin11"CONN_CAM pin20"` 这种**两串粘连**的垃圾节点
⇒ 而且**新门禁也没抓住** (正则 `^REF pin\d+$` 匹配不上 ⇒ 当成"不是针脚" ⇒ 静默漏过)
⇒ ★**教训**: ① 补丁脚本改结构化文本要**按字段/按语句**改, 不要按子串切; ② ★**门禁要能抓"格式非法"**,
不只是"值不对" ⇒ 已补 C6 节点串格式检查。
'''
    open(mem, 'w', encoding='utf-8').write(m)
    print('✅ memory/2026-11-03.md 已落盘')
    return 0


if __name__ == '__main__':
    sys.exit(main())
