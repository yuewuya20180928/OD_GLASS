#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""land_iss148_150.py —— ISS-148 验收 + ISS-150 网表落地 + 新开 ISS-152 (上电顺序/2.9V 轨)"""
import os
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

# ── issue_log ──
IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

i = by['ISS-148']
i['status'] = 'fixed'
i['owner'] = 'main'
i['verify_by'] = 'hw-lead'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = ('HW/IMX415_DEMO_SENSOR_FACTS.md (26KB: 电源域/1080p60 出法/IQ 适用性/采购硬判据) · '
                'HW/AR0234CS_OPEN_SOURCE_FACTS.md (16KB: U2/U4 硬件数据) · 配套网表改动见 HW/DEMO_BOARD_HW_DECISION.md')
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:5x 交卷, 已按 IMX415 facts 落网表 (ISS-150)**: "
    "**① 电源域 (公开 datasheet)**: DVDD1 1.00~1.20V typ 1.10 / OVDD 1.70~1.90V typ 1.80 (IOVDD 3mA) / AVDD1 2.80~3.00V typ 2.90 (IAVDD max 156mA) ⇒ "
    "★★**网表三条轨实测结论**: `SENSOR_VDD_IO` **2.8V → 1.8V** (★**不改会直接烧 sensor**: VI 绝对最大 ≤3.3V 而 OVDD max 1.90V) · "
    "`SENSOR_CORE` **1.2V 保持** (在 DVDD1 范围内) 只把电流规格 50→250mA · `SENSOR_AVDD` **2.8V 保持** (落 Min 边界) 电流规格 30→156mA ⇒ "
    "★**轨数/LDO 型号/封装全不变 ⇒ 仍是「换料不换板」**; "
    "**② 1080p60 怎么出**: ★★**走 sensor 侧 2/2 行 binning (不是 crop ⇒ 不违反 10-25 禁 ROI)** ⇒ ★**Rockchip BSP `imx415.c` 已经带这个模式** "
    "(1944×1097, 寄存器 0x3020=0x01), ★**60fps 只需改 VMAX 一个数 (0x0C5D→0x062E) ⇒ \"改一行\"不是\"移植驱动\"** ⇒ **零移植确认**; "
    "**③ 现成 IQ**: `imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json` 里 resolution 与 mesh 文件名**都锁死 3840×2160** ⇒ 1080p 档缺 mesh ⇒ "
    "★**demo 唯一要做的 tuning = 补一套 1920×1080 mesh + AE 曝光表换算, 1~2 人日 (暗室/灰卡)** —— 不是人周级。")

i = by['ISS-150']
i['status'] = 'fixed'
i['owner'] = 'main'
i['verify_by'] = 'hw-lead'
i['fix_ref'] = ('HW/SCHEMATIC_V1_SPEC.json (power_rails: SENSOR_VDD_IO 1.8V/TPS7A20-18/3mA, SENSOR_CORE 250mA, SENSOR_AVDD 156mA) · '
                'state/gen_netlist.py (U_LDO_S28B→U_LDO_S18B + 三条轨电流规格 + I2C_A 上拉 4.7k→2.2k) · '
                'state/_iss150_imx415_rails.py · HW/IMX415_DEMO_SENSOR_FACTS.md §1')
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:5x 项目总工已改完并全绿** (gen_netlist/gen_kicad_net/gen_netlist_pins/gen_bom rc=0; check_netlist 31 条全过; check_kicad_net 5 条全过): "
    "①`SENSOR_VDD_IO` 2.8V → **1.8V** (U_LDO_S28B → U_LDO_S18B, TPS7A20-18) —— ★**这是会烧 sensor 的级别** (19:3x 我按 AR0234CS 改的 2.8V, 现按 IMX415 datasheet 改回 ⇒ 净变化 0); "
    "②`SENSOR_CORE` 1.2V 保持, 电流 50→250mA; ③`SENSOR_AVDD` 2.8V 保持, 电流 30→156mA; "
    "④★**I2C_A 上拉 4.7k → 2.2k** (IMX415 的 IOL 只允许 3mA ⇒ R ≥ (3.3-0.4)/3mA = 967Ω; 取 2.2k ⇒ 灌 1.5mA ✔, t_r≈186ns ✔) —— "
    "★**上拉电压仍留 3.3V** (IMX415 VI 绝对最大 ≤3.3V ⇒ 合法) ⇒ ★**TBD-05 对 IMX415 这一侧不成立**。")

if not any(x['id'] == 'ISS-152' for x in iss):
    iss.append({
        'id': 'ISS-152',
        'title': '★★[硬件] IMX415 上电顺序 (DVDD→OVDD→AVDD) 与 AVDD typ 2.9V: 现网表三轨同起 + LDO 无 EN ⇒ 顺序不保证',
        'severity': 'medium', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 19:5x IMX415 facts 带出的两条硬件账 (demo 不阻塞, 但必须挂账): '
            '**① 上电顺序**: 公开 datasheet 要求 **DVDD(1.1V) 先 → OVDD(1.8V) 再 → AVDD(2.9V) 最后**, 三轨须在 **200ms 内**全部到位; '
            '⇒ ★**现网表三条 LDO 全部同时接 RAIL_SYS 且都没有使能脚 (TPS7A20 是固定输出无 EN)** ⇒ 顺序**不保证** ⇒ 若 AVDD 先到而 DVDD 还是 0V, 违 datasheet。'
            '⇒ ★**对策 (整机阶段)**: ①换带 EN 的低噪声 LDO (AVDD 那条) + RC 延时 ②或加 supervisor/顺序控制器; ★**demo 阶段按"三轨同时上电"跑** (公开在售的 IMX415 模组都是这么做的) ⇒ ★**不卡 demo, 但不能带进量产**。'
            '**② AVDD 想用 typ 2.9V**: TPS7A20 固定档**没有 2.9V** (覆盖 0.8~5.5V 的 30 档里没有) ⇒ 现状 2.8V 落 AVDD1 Min 边界 ⇒ '
            '⇒ 若要 typ 值 ⇒ 换可调 LDO (或改用 3.0V 档 = 落在 Max 边界, 不推荐)。★**决策**: 现状保留 2.8V, 整机阶段再评。'),
        'owner': 'hw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-12',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'HW/IMX415_DEMO_SENSOR_FACTS.md §1.1 / §1.3 · HW/SCHEMATIC_V1_SPEC.json (power_rails)',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:5x。★**demo 阶段不阻塞** (按三轨同时上电跑) ⇒ ★**但绝不能带进量产** ⇒ 整机阶段必须闭环。'
                 '★**顺带**: 这条也是"替代料清单"里每个 sensor 都要重核的一项 (不同 sensor 的电源域与上电顺序都不同 ⇒ ★**换 sensor 时这条轨必须跟着改**)。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[issue_log] ISS-148 fixed / ISS-150 fixed / 新开 ISS-152')

# ── tracker: (1.62) 补一段 IMX415 落地 ──
TP = f'{PROJ}/PROJECT_TRACKER.md'
t = open(TP, encoding='utf-8').read()
anchor = "**★ 两步走 (不冲突)**:"
i = t.index(anchor)
add = """**★ 19:5x 追加: IMX415 的硬件数据已落网表 (ISS-150)** —— ★**三条 sensor 轨按公开 datasheet 重核, 其中一条是会烧件的级别**:
| 轨 | 现状 → 定案 | 依据 (IMX415 公开 datasheet) |
|---|---|---|
| `SENSOR_VDD_IO` | ★**2.8V → 1.8V** (U_LDO_S28B → **U_LDO_S18B**, TPS7A20-18) | OVDD 1.70~1.90V typ 1.80, IOVDD 3mA; ★**VI 绝对最大 ≤3.3V ⇒ 2.8V 会直接超规格** |
| `SENSOR_CORE` | 1.2V **保持**, 电流 50 → **250mA** | DVDD1 1.00~1.20V typ 1.10 (1.2V 合法) |
| `SENSOR_AVDD` | 2.8V **保持**, 电流 30 → **156mA** | AVDD1 2.80~3.00V typ 2.90 (2.8V 落 Min 边界) |
| `I2C_A` 上拉 | ★**4.7k → 2.2k** (电压仍 3.3V) | ★**IMX415 IOL 只允许 3mA** ⇒ R ≥ (3.3-0.4)/3mA = 967Ω ⇒ 取 2.2k (灌 1.5mA, t_r≈186ns); ★**VI ≤3.3V ⇒ 上拉留 3.3V 合法** ⇒ ★**TBD-05 对 IMX415 不成立** |

⇒ ★**轨数 3 条不变、LDO 型号家族不变、封装不变 ⇒ 仍是「换料不换板」**; ★**1080p60 = sensor 侧 2/2 行 binning (不是 crop) + 改 VMAX 一个数 (0x0C5D→0x062E), BSP `imx415.c` 已带该模式 ⇒ 零移植**; ★**demo 唯一要做的 tuning = 补 1920×1080 mesh + AE 表换算, 1~2 人日** (不是人周) ⇒ ★**另挂 ISS-152: 上电顺序 (DVDD→OVDD→AVDD) 现网表保证不了, demo 不卡, 量产必须闭环**。

"""
t = t[:i] + add + t[i:]
open(TP, 'w', encoding='utf-8').write(t)
print('[tracker] (1.62) 已补 IMX415 轨落地段')

# ── 分片 ──
def mutate(d):
    claims = d.setdefault("interface_claims", [])
    def add(key, value, note, ref):
        for c in claims:
            if c.get("key") == key:
                c.update({"value": value, "note": note, "ref": ref}); return
        claims.append({"key": key, "value": value, "note": note, "ref": ref})
    add("sensor_rails_imx415", "1.1V/1.8V/2.9V",
        "★IMX415 三轨 (公开 datasheet, ISS-148 facts §1): 数字 DVDD1 1.00~1.20V typ 1.10 / IO OVDD 1.70~1.90V typ 1.80 (IOVDD 3mA) / 模拟 AVDD1 2.80~3.00V typ 2.90 (IAVDD max 156mA) ⇒ 网表: SENSOR_CORE 1.2V 保持(250mA) · ★**SENSOR_VDD_IO 2.8V→1.8V** (TPS7A20-18, ★不改会烧件) · SENSOR_AVDD 2.8V 保持(156mA) · ★I2C_A 上拉 4.7k→2.2k (IOL≤3mA ⇒ R≥967Ω) 且 ★**上拉电压仍 3.3V 合法 (VI≤3.3V)** ⇒ ★**TBD-05 对 IMX415 不成立**; ★轨数/LDO 家族/封装不变 ⇒ 换料不换板。",
        "HW/IMX415_DEMO_SENSOR_FACTS.md §1 + HW/SCHEMATIC_V1_SPEC.json")
    add("sensor_1080p60_mode", "binning_2x2_vmax",
        "★IMX415 出 1080p60 = **sensor 侧 2/2 行 binning** (1944×1097, 寄存器 0x3020=0x01, ★**不是 crop ⇒ 不违反 10-25 禁 ROI**) ⇒ ★**Rockchip BSP `imx415.c` 已带该模式** ⇒ 60fps 只需改 VMAX (0x0C5D→0x062E) ⇒ **零驱动移植**; ★现成 IQ 锁死 3840×2160 (mesh 文件名也锁) ⇒ 1080p 档需补 mesh + AE 表 ⇒ 1~2 人日。",
        "HW/IMX415_DEMO_SENSOR_FACTS.md §2/§3")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d
update_fragment("hw-lead", mutate)
print('[分片] hw.yaml 已更新 (2 claims)')
