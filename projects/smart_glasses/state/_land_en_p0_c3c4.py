#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""land_en_p0_and_c3c4.py —— EN P0 落账 + ISS-151 的 C3/C4 采购口径更正落进硬件方案文件

C3 ★公开现货 camera 模组的 FPC 实际是 31p/0.3mm (4-lane CSI) 或 RPi 15p/1.0mm (2-lane) 或 22p/0.5mm,
   ★**几乎没有 0.5mm/24p 现货** ⇒ 我们硬件方案里"0.5mm/24p"是**自研目标规格 (Step2)**, demo 阶段要用公开现货规格。
C4 ★公开现货 MIPI-DSI 一体屏最高只到 1200×1920 (Radxa 10 FHD) ⇒ ★**"1920×1080 视涯 SiOLED"没有公开对标品**
   ⇒ demo 用 8HD/10FHD 验链路即可, 视涯单列风险项。
★★C5(已修) EN P0: TPS7A20/TPS62130A 的 EN 脚全没画 ⇒ 悬空=关断 ⇒ 投板后 9 路全灭。
★★init sequence 现成范例: `rk3576-evb.dtsi` 里有 1080×1920 / 4-lane / RGB888 的完整 panel-init-sequence (与视涯屏分辨率最贴)。
"""
import os
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

# ══════ ① 硬件方案文件: FPC 针位口径 + 屏的 demo 替代口径 ══════
DOC = f'{PROJ}/HW/DEMO_BOARD_HW_DECISION.md'
d = open(DOC, encoding='utf-8').read()
old = "## 6. ★ 画板前必须闭合的 3 件事 (不闭合就别下单)"
new = """## 6. ★ 20:3x 两条采购口径更正 (来自 ISS-151 替代料清单, 实测公开现货)**:
- ★**C3: "0.5mm/24p" 在公开现货里基本不存在** —— 公开在售 camera 模组的 FPC 实际是 **31p/0.3mm (4-lane CSI)** / **RPi 15p/1.0mm (2-lane CSI)** / 22p/0.5mm ⇒ ★**本文件 §4 的两块 FPC 针位表是「自研目标规格 (Step2)」**; ★**demo 阶段 (Step1) 直接用公开现货规格的模组**, 两边对不上就以现货为准, 别硬凑。
- ★**C4: 公开现货的 MIPI-DSI 一体屏最高只到 1200×1920 (Radxa 10 FHD)** ⇒ ★**"1920×1080 视涯 SiOLED" 没有公开对标品** ⇒ ★**demo 阶段用 8HD / 10FHD 这类公开现货屏验链路即可, 视涯屏单列为风险项** (等 init code / 采购)。
- ★**init sequence 现成范例**: `rk3576-evb.dtsi` 里有 **1080×1920 / 4-lane / RGB888 的完整 panel-init-sequence** (与视崖屏分辨率最贴) ⇒ ★**面板这条路的起点不是"问厂家", 是"抄内核里的现成 dts"**。

**★ 画板前必须闭合的 3 件事 (不闭合就别下单)**"""
assert old in d
d = d.replace(old, new, 1)

old2 = "## 4. ★ 两块 FPC 的针位总表 (画板/采购直接照抄)"
new2 = """## 4. ★ 两块 FPC 的针位总表 (**自研目标规格, Step2 用; demo 阶段以公开现货为准 —— 见 §6 的 C3 更正**)
"""
assert old2 in d
d = d.replace(old2, new2, 1)
open(DOC, 'w', encoding='utf-8').write(d)
print('[1] HW/DEMO_BOARD_HW_DECISION.md: C3/C4 口径更正已写')

# ══════ ② issue_log ══════
IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

i = by['ISS-151']
i['note'] = (i.get('note') or '') + (
    " ★★**20:3x 项目总工采纳 C5 并已修网表 (P0)**: ★**TPS7A20 / TPS62130A 都有 EN 脚 (TPS7A20 内部 500kΩ 下拉 ⇒ 悬空=关断)**, "
    "而原网表 **9 路电源 IC 全没有 EN 网络** ⇒ 投板后 9 路全灭 = 整板不上电 = 2~4 周返工; ★**BOM footprint/opn 全是\"待定\" ⇒ 现在改成本≈0** ⇒ "
    "★**已修**: ①除 SENSOR_AVDD 外, 每颗 IC 的 EN **直连 RAIL_SYS** (3.5-4.2V ≫ VEN(HIGH) 0.9V ⇒ 永远使能, 零新增器件) ②**SENSOR_AVDD 的 EN 走 RC 延时** (R 100k SYS→EN + C 1µF EN→GND, t=(100k‖500k)×1µF≈83ms) ⇒ **AVDD 最后上电 ⇒ 满足 IMX415 的 DVDD→OVDD→AVDD 顺序 ⇒ 顺手解掉 ISS-152 (不用换 LDO 家族)**。"
    "★**另两条采购口径更正 (已写进硬件方案文件)**: **C3** 公开现货 camera 模组 FPC 是 31p/0.3mm 或 RPi 15p/1.0mm 或 22p/0.5mm ⇒ ★**几乎没有 0.5mm/24p 现货** ⇒ 我们那套 24p 针位是**自研目标规格 (Step2)**, demo 用现货; "
    "**C4** 公开现货 MIPI-DSI 一体屏最高只到 1200×1920 (Radxa 10 FHD) ⇒ ★**\"1920×1080 视涯 SiOLED\"没有公开对标品** ⇒ demo 用 8HD/10FHD 验链路, 视涯单列风险项。"
    "★**init sequence 现成范例**: `rk3576-evb.dtsi` 里有 **1080×1920 / 4-lane / RGB888 的完整 panel-init-sequence** (与视涯屏分辨率最贴) ⇒ ★**面板这条路起点是\"抄内核现成 dts\", 不是\"问厂家\"**。"
    "★**L3 状态自评**: 全库 `grep -rnE \"已购|已下单|已到手\"` **零命中** ⇒ ★**\"所有元件都试过了\"这个条件目前不成立 ⇒ L4 (咨询厂家) 现在不该触发**。")

i = by['ISS-152']
i['status'] = 'closed'
i['verify_by'] = 'main'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = 'state/gen_netlist.py (SENSOR_AVDD 的 EN RC 延时: R_EN_AVDD 100k + C_EN_AVDD 1µF) · HW/IMX415_DEMO_SENSOR_FACTS.md §1.3 · HW/PART_ALTERNATIVES_REGISTRY.md §6'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 20:3x 闭环**: ★**TPS7A20 实测有 EN 脚** ⇒ 本单不再是风险项: ★**已用网表解掉** —— "
    "除 SENSOR_AVDD 外全部 EN 直连 RAIL_SYS (永远使能), ★**SENSOR_AVDD 的 EN 走 RC 延时 (R 100k + C 1µF, t≈83ms) ⇒ AVDD 最后上电 ⇒ 满足 IMX415 的 DVDD→OVDD→AVDD 顺序** ⇒ "
    "★**不用换 LDO 家族, 不用改板层数, 零 BOM 增量 (1R+1C)** ⇒ 网表已改 + 4 个生成器 rc=0 + check_netlist 31 条全过 + check_kicad_net 5 条全过。"
    "★**唯一剩余的整机级尾巴**: EN 接哪儿 (用 SOM 的 EN 脚 还是 RC) 在 Step2 画板时定; demo 阶段三轨同跑。")

if not any(x['id'] == 'ISS-156' for x in iss):
    iss.append({
        'id': 'ISS-156',
        'title': '★★[demo 供应链] 公开现货清单的采购口径: camera 模组 FPC 无 0.5mm/24p 现货 + 1920×1080 视涯 SiOLED 无公开对标品 ⇒ demo 走什么料',
        'severity': 'high', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 20:3x ISS-151 实测出的两条采购口径问题 (影响 demo 到底买什么): '
            '**C3** 公开在售 camera 模组的 FPC 实际规格 = **31p/0.3mm (4-lane CSI, 型号 FH35C-31S-0.3SHW)** / **RPi 15p/1.0mm (2-lane, 型号 FPC1030-15S-TAG)** / 22p/0.5mm ⇒ ★**几乎没有 0.5mm/24p 现货** ⇒ '
            '★**我们硬件方案里的 0.5mm/24p 是自研目标规格 (Step2), demo 阶段必须改用公开现货规格** ⇒ ⇒ **两条路**: ①demo 用公开现货模组 (针数/针位随模组, 主板侧不画) ②自研主板时按 24p 画 (与公开现货对不上, 要么定制排线要么改针数)。'
            '**C4** 公开在售 MIPI-DSI 一体屏最高只到 **1200×1920 (Radxa 10 FHD)** ⇒ ★**"1920×1080 视涯 SiOLED"没有公开对标品** ⇒ '
            '⇒ **demo 用 8HD / 10FHD 这类公开现货屏验链路** (分辨率不同但链路一样: CSI→ISP→OD→画框→DSI→屏), ★**视涯屏单列为风险项** (等 init code / 采购)。'
            '⇒ ★**顺带一条好消息**: `rk3576-evb.dtsi` 里有 **1080×1920 / 4-lane / RGB888 的完整 panel-init-sequence** (与视涯屏分辨率最贴) ⇒ ★**面板这条路的起点是抄内核现成 dts, 不是问厂家**。'),
        'owner': 'main', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-04',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'HW/PART_ALTERNATIVES_REGISTRY.md §3/§5 · HW/DEMO_BOARD_HW_DECISION.md §4/§6',
        'verify_by': 'hw-lead', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 20:3x。★**这是"demo 到底买什么"的最后一道口径** ⇒ 定了就能出 Step1 采购单。'
                 '★**默认建议 (未拍板)**: ①camera 用**公开现货的 IMX415 模组** (针数随模组, 主板侧不画) ②屏用**公开现货 8HD/10FHD DSI 一体屏** (先验链路) ③视涯 0.49\" 只在整机阶段用 ⇒ ★**这样 demo 完全不依赖任何定制件**。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[2] issue_log: ISS-151 note 追加 / ISS-152 closed / 新开 ISS-156')

# ══════ ③ tracker ══════
TP = f'{PROJ}/PROJECT_TRACKER.md'
t = open(TP, encoding='utf-8').read()
anchor = "⇒ ★**现在的头号卡点只剩一个**"
i = t.index(anchor)
add = """**★ 20:3x 追加: 一个 P0 已修 (现在改成本≈0, 再晚就贵了) + 两条采购口径更正**
| 项 | 内容 | 处置 |
|---|---|---|
| ★★**P0: 9 路电源 IC 的 EN 脚全没画** | ★**TPS7A20 / TPS62130A 都有 EN 脚**, TPS7A20 内部 **500kΩ 下拉** ⇒ datasheet 原文 "keeps the LDO disabled even when the EN pin is left floating" ⇒ ★**悬空 = 关断** ⇒ 原网表 **7 LDO + 2 DC-DC 全无 EN 网络** ⇒ ★**投板后 9 路全灭 = 整板不上电 = 2~4 周返工** | ✅ **已修**: 除 SENSOR_AVDD 外 EN 直连 RAIL_SYS (永远使能, 零新增器件); ★**SENSOR_AVDD 的 EN 走 RC 延时** (R 100k + C 1µF, t≈83ms) ⇒ **AVDD 最后上电 ⇒ 满足 IMX415 的 DVDD→OVDD→AVDD 顺序** ⇒ ★**ISS-152 顺手闭环 (不用换 LDO 家族, 不改板层数, 零 BOM 增量)**; 网表已改 + 4 生成器 rc=0 + check_netlist 31 条 / check_kicad_net 5 条全过 |
| ★**C3** | 公开现货 camera 模组 FPC = **31p/0.3mm / RPi 15p/1.0mm / 22p/0.5mm** ⇒ ★**几乎没有 0.5mm/24p 现货** ⇒ ★**我们的 24p 针位是"自研目标规格 (Step2)"**, demo 用现货 | ✅ 已写进 `HW/DEMO_BOARD_HW_DECISION.md` §4/§6 + 新开 **ISS-156** |
| ★**C4** | 公开现货 MIPI-DSI 一体屏最高只到 **1200×1920** ⇒ ★**"1920×1080 视涯 SiOLED" 没有公开对标品** | ✅ demo 用 8HD/10FHD 验链路, 视涯单列风险项 (**ISS-156**) |
| ★**好消息** | `rk3576-evb.dtsi` 里有 **1080×1920 / 4-lane / RGB888 的完整 panel-init-sequence** | ★**面板这条路起点是"抄内核现成 dts", 不是"问厂家"** |
| ★**L3 状态** | 全库 `grep -rnE "已购\\|已下单\\|已到手"` **零命中** | ★**"所有元件都试过了"目前不成立 ⇒ L4 (咨询厂家) 现在不该触发** |

"""
t = t[:i] + add + t[i:]
open(TP, 'w', encoding='utf-8').write(t)
print('[3] tracker: 20:3x 段已写')

# ══════ ④ 分片 ══════
def mutate(d):
    claims = d.setdefault("interface_claims", [])
    def add(key, value, note, ref):
        for c in claims:
            if c.get("key") == key:
                c.update({"value": value, "note": note, "ref": ref}); return
        claims.append({"key": key, "value": value, "note": note, "ref": ref})
    add("ldo_en_net", "SYS+RC_AVDD",
        "★★2026-11-02 20:3x P0 修复 (原网表缺 EN ⇒ 悬空=关断 ⇒ 投板后 9 路全灭): ★TPS7A20/TPS62130A 都有 EN 脚 (TPS7A20 内部 500kΩ 下拉) ⇒ 现网表: ①除 SENSOR_AVDD 外 **EN 直连 RAIL_SYS** (永远使能, 零新增器件) ②**SENSOR_AVDD 的 EN 走 RC 延时** (R_EN_AVDD 100k SYS→EN + C_EN_AVDD 1µF EN→GND, t=(100k‖500k)×1µF≈83ms) ⇒ **AVDD 最后上电 ⇒ 满足 IMX415 DVDD→OVDD→AVDD** ⇒ ISS-152 闭环 (零换料/零改板层数)。",
        "state/gen_netlist.py (P1 电源树 EN 行) + ISS-152")
    add("demo_fpc_spec", "public_stock_only",
        "★2026-11-02 20:3x (ISS-151 C3): 公开现货 camera 模组 FPC = **31p/0.3mm (FH35C-31S-0.3SHW)** / **RPi 15p/1.0mm (FPC1030-15S-TAG)** / 22p/0.5mm ⇒ ★**几乎没有 0.5mm/24p 现货** ⇒ ★**我们硬件方案里的 0.5mm/24p 是自研目标规格 (Step2)**, demo 阶段直接用公开现货模组 (针数随模组, 主板侧不画)。",
        "HW/DEMO_BOARD_HW_DECISION.md §4/§6 + ISS-156")
    add("panel_init_sequence_source", "rk3576-evb.dtsi",
        "★2026-11-02 20:3x: Rockchip `rk3576-evb.dtsi` 里有 **1080×1920 / 4-lane / RGB888 的完整 panel-init-sequence** (与视涯 0.49\" 1920×1080 分辨率最贴) ⇒ ★**面板 init code 的起点是\"抄内核现成 dts\", 不是\"问厂家\"**; ★另: 内核 79 个 panel 文件里**确实有** ST7701/ST7703/ILI9881C/NV3052C 的现成驱动, ★**但 EK79007/EK73217/NV3049 内核里没有**。",
        "HW/PART_ALTERNATIVES_REGISTRY.md §3 + ISS-156")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d
update_fragment("hw-lead", mutate)
print('[4] hw.yaml 已更新 (3 claims)')
