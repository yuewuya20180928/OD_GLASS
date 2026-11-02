#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_boss_1945.py —— 老板 2026-11-02 19:45 指示落账

老板原话: "数量太少了, 走不了大批量采购的方案, 还是那句话, 所有需要厂家给的信息都先去网上找,
网上找不到再换一个替换方案, 所有的元件都试了之后还找不到, 再考虑采购方案咨询厂家"

⇒ ① 修正 19:25 的"一律不发" ⇒ 改成**四级阶梯**, 厂商咨询排最后
⇒ ② demo 量少 ⇒ 不走批量定制采购, 走**公开现货/样品渠道**
⇒ ③ "所有元件都试过了" 要可核查 ⇒ 建**替代料候选清单** (每类 ≥3 个公开在售替代品)
"""
import os
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

# ══════════════ tracker ══════════════
P = f'{PROJ}/PROJECT_TRACKER.md'
s = open(P, encoding='utf-8').read()

# 变量 45: 改口径 (检索 → 换料 → 全部试过 → 才咨询厂家)
i = s.index("| **45** | ★**信息获取规则")
end = s.index("\n", i)
new45 = ("| **45** | ★**信息获取四级阶梯 (19:25 → ★19:45 修正)** | ①★**先上网找** (公开 datasheet / 公开 panel 驱动树 / 开源驱动源码 / 公开在售模组页 / 社区实测贴) "
 "②★**网上找不到 ⇒ 换一个替代料** (公开在售的同类件, ★**不联系厂家**) ③★**所有元件都试过之后仍找不到 ⇒ 才走采购渠道咨询厂家** "
 "⇒ ★**19:45 修正**: 19:25 落的「一律不发邮件」改成**厂商咨询排最后一级** (不是永不问, 是**先把能自己解决的解决掉**) ⇒ "
 "★**配套**: 每一级都要有可核查凭证 ⇒ 替代料候选清单 (`HW/PART_ALTERNATIVES_REGISTRY.md`, 每类 ≥3 个公开在售替代品) ⇒ ★**\"都试过了\" 不是形容词, 是清单** | ★**11-02 19:45** |")
s = s[:i] + new45 + s[end:]

# 新增变量 47
i = s.index("| **46** | ★**demo 阶段 sensor 判据收敛成两条")
end = s.index("\n", i)
new47 = ("| **47** | ★**demo 阶段物料走公开现货/样品渠道, 不走批量定制采购** | ★**\"数量太少了, 走不了大批量采购的方案\"** (老板 19:45) ⇒ "
 "★**demo 阶段(1 台样机)的物料一律**: ①**公开在售现货** (公开电商现货的 camera 模组 / MIPI-DSI 屏模组 / RK357x SBC) ②**样品/单件渠道** (模组厂样品) "
 "③★**不做批量定制采购** (MOQ/阶梯价/定制开模那条路 demo 阶段走不通) ⇒ ★**与 §0 变量 45 的四级阶梯配套**: "
 "★**\"公开现货\"本身就是二级 (换替代料) 的落地形式** —— 优先用**别人已经量产在卖**的模组, 而不是我们去定制 | ★**11-02 19:45** |")
s = s[:end] + "\n" + new47 + s[end:]

# 决策节 (1.62)
anchor2 = "#### (1.61) ★★★★ 2026-11-02 19:4x: **demo 硬件方案定案**"
sec = """#### (1.62) ★★★★ 2026-11-02 19:45: **信息获取四级阶梯 + demo 走公开现货** (厂家咨询挪到最后)

> **老板原话**: "数量太少了, 走不了大批量采购的方案, 还是那句话, 所有需要厂家给的信息都先去网上找, 网上找不到再换一个替换方案, 所有的元件都试了之后还找不到, 再考虑采购方案咨询厂家"
> **落账**: §0 **变量 45 修正** + 新增 **变量 47** · **ISS-142 由 closed 改 deferred (排最后一级)** · `state/outbox/` 草稿标注由"作废"改为"暂不发, 排最后" · 新开 **ISS-151** (替代料候选清单)

**★ 我要纠正自己 19:25 落的那条**: 当时把「不发邮件」落成「**一封不发 / ISS-142 closed**」⇒ ★**现在按老板 19:45 的措辞改成四级阶梯**: **厂商咨询不是永不问, 是排最后一级** ⇒ ISS-142 改 deferred, 草稿保留不删。

**★ 四级阶梯 (每一级都要留凭证)**:
| 级 | 动作 | 凭证落在哪 | 本项目当前的实例 |
|---|---|---|---|
| **L1 网上找** | 公开 datasheet PDF / 公开 panel 驱动树 / 开源驱动源码 / 公开在售模组页 / 社区实测贴 | `HW/OPEN_SOURCE_AVAILABILITY.md` 的五数据源快照 + 各 facts 文档的"证据 URL/行号" | ★IMX415 三轨与 1080p60 模式 (ISS-148 在跑); RK357x SOM 公开引脚定义 |
| **L2 换替代料** | ★**换公开在售的同类件** | ★**`HW/PART_ALTERNATIVES_REGISTRY.md`** (每类 ≥3 个公开在售替代品 + 来源 + 规格 + 数据来源评分) | ★**公开现货 MIPI-DSI 屏模组大量存在且驱动 IC 公开** (ST7701 / EK79007+EK73217 等 ⇒ ★**Rockchip 内核里有它们的 panel 驱动与时序** ⇒ ★**面板 init code 大概率不必问厂家**) |
| **L3 全部试过** | ★**清单里每一项都试过/查过** | ★**同一份替代料清单的"已试/未试"栏** | ISS-151 |
| **L4 才咨询厂家** | 走**采购方案**咨询 (不是发邮件) | ISS-142 (deferred) | 面板厂商专属参数等 L1~L3 都不出结果时 |

**★ 与"量少"的配套 (变量 47)**: demo 阶段 1 台样机 ⇒ ★**物料一律走公开现货/样品渠道** (公开电商现货模组 + 模组厂样品) ⇒ ★**不做批量定制/开模采购** ⇒ ★**这条同时给 L2 提供了现成货架**: ★**优先用"别人已经量产在卖"的模组** (公开在售 MIPI-CSI camera 模组、公开在售 MIPI-DSI 屏模组、公开在售 RK357x SBC) ⇒ ★**Step1 用公开 SBC + 公开在售模组 = 零 PCB 零定制, 本周就能跑**。

"""
s = s.replace(anchor2, sec + anchor2, 1)
open(P, 'w', encoding='utf-8').write(s)
print('[tracker] 变量 45 修正 + 变量 47 新增 + (1.62) 已写')

# ══════════════ issue_log ══════════════
IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

i = by['ISS-142']
i['status'] = 'deferred'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:45 修正 (老板新措辞)**: 「不发邮件」不是永不问, 而是**排最后一级** ⇒ 本单由 closed 改 **deferred**: "
    "★**触发条件 = 替代料清单 (ISS-151) 里每一类都试过、网上与公开现货都找不到, 才走采购渠道咨询厂家** ⇒ ★**在那之前一封不发**。"
    "★**onsemi 这封的四个未知量 (U2 abs max / U4 模拟轨) 当前都走 L1 网上找** (ISS-148 在跑) ⇒ ★**优先看公开 datasheet PDF 与开源驱动源码**。")

if not any(x['id'] == 'ISS-151' for x in iss):
    iss.append({
        'id': 'ISS-151',
        'title': '★★[硬件优先] 替代料候选清单: 每类物料 ≥3 个公开在售替代品 + 来源/规格/数据来源评分 ⇒ 让「都试过了」可核查',
        'severity': 'high', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 19:45 老板定四级阶梯: **L1 网上找 → L2 换替代料 → L3 全部试过 → L4 才咨询厂家** ⇒ '
            '★**"所有元件都试了" 必须有可核查的凭证, 否则这级阶梯就是句空话** ⇒ 本单 = 建**替代料候选清单**。'
            '⇒ ★**要交的**: `HW/PART_ALTERNATIVES_REGISTRY.md` —— **每个物料类别**一行一个候选, 字段: '
            '**类别 / 候选名 / 公开在售渠道(链接) / 关键规格 / ①能否满足 demo 硬指标 ②数据来源是否充足 (D1~D5 评分) / 已试-未试 / 备注**。'
            '⇒ ★**必列的类别 (按 demo 链路)**: '
            '**①主控载体** (RK3572 公开 SBC / RK3576 SBC / 公开核心板模组 —— Forlinx / ArmSoM / DFRobot 等公开现货) '
            '**②camera 模组** (公开在售 MIPI-CSI 模组: Arducam / Waveshare / Radxa 等公开现货, IMX415/IMX219/OV5647 等) '
            '**③屏幕模组** (公开在售 MIPI-DSI 屏模组, ★**驱动 IC 公开的优先**: ST7701 / EK79007+EK73217 等 ⇒ ★**Rockchip 内核里就有这些 panel 的驱动与时序 ⇒ init code 不必问厂家**) '
            '**④sensor 裸件** (IMX415 / AR0234CS / AR0521 / OV04C10 —— 已有的实测来源评分表直接复用 `HW/open_source_rank.py`) '
            '**⑤FPC 连接器与排线** (公开规格: 0.5mm 24p/20p / 31p 0.3mm / 15p 1.0mm 等) '
            '**⑥电源** (BQ25896 / BQ2970 / 公开 LDO 现货) '
            '**⑦调试与接口** (USB-UART/JTAG 公开模块)。'
            '⇒ ★**纪律**: ①每条都要**公开可点的链接** (不许写"听说有") ②**没查到的写"未查"**, 不许猜价格与库存 '
            '③★**不写任何"联系厂家"的动作** (L4 还没到) ④**已试/未试栏要真的动** (这是 L3 的凭证) '
            '⑤★**优先选"别人已经量产在卖"的** (公开现货 ⇒ 零定制, 契合 demo 量少的前提)。'),
        'owner': 'hw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-04',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'PROJECT_TRACKER.md §(1.62) + §0 变量 45/47 · HW/OPEN_SOURCE_AVAILABILITY.md',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:5x。★**硬件优先**。★**这份清单是四级阶梯的凭证**, 也是 ISS-142 (厂商咨询) 的放行前提。'
                 '★**顺带收益**: 清单里 ★**公开现货的 MIPI-DSI 屏模组驱动 IC 是公开的 (ST7701 / EK79007+EK73217)** ⇒ '
                 '★**面板 init code 很可能不用问厂家** —— Rockchip 内核自带这些 panel 的驱动与时序 ⇒ ★**这条能直接解掉 ISS-145 的"面板 init code 是真瓶颈"**。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[issue_log] ISS-142 → deferred + 新开 ISS-151')

# ══════════════ outbox 标注修正 (作废 → 暂不发, 排最后) ══════════════
OB = f'{PROJ}/state/outbox/README.md'
t = open(OB, encoding='utf-8').read()
t = t.replace('> ★★★ **2026-11-02 19:25 老板指示: 不会发任何邮件给任何厂家, 后面不考虑任何问询函 ⇒ 本目录全部草稿一律不外发** (一封不发)。',
              '> ★★★ **2026-11-02 19:25 → ★19:45 修正**: 老板先说「不发任何邮件给任何厂家」, 19:45 补充「★**所有元件都试了之后还找不到, 再考虑采购方案咨询厂家**」 ⇒ '
              '★**本目录草稿改为「暂不发, 排在最后一级 (L4)」** —— 不是永不问, 是**先把 L1 网上找 / L2 换替代料走完**。\n'
              '> ★**当前 L1/L2 的进展**: IMX415 数据 → L1 (公开 datasheet/BSP 驱动, ISS-148); 面板 init code → ★**L2 有戏** (公开在售 MIPI-DSI 模组的驱动 IC 是公开的: ST7701 / EK79007+EK73217 ⇒ Rockchip 内核自带 panel 驱动与时序 ⇒ **多半不用问厂家**); '
              'RK357x SOM 引脚定义 → L1 (公开 SBC/核心板原理图)。')
open(OB, 'w', encoding='utf-8').write(t)
print('[outbox] README 标注已由「作废」改为「暂不发, 排最后」')

for fn, old, new in [
    ('onsemi_ar0234cs_query.md',
     '> ★★**2026-11-02 19:25 老板指示: 不再外发任何问询函 ⇒ 本草稿作废 (一封不发)**。',
     '> ★★**2026-11-02 19:25 → 19:45 修正: 本草稿改为「暂不发, 排在最后一级 (L4)」** —— 触发条件 = 替代料清单 (ISS-151) 里每一类都试过、公开渠道都找不到, 才走采购渠道咨询厂家。'),
    ('visionox_display_inquiry.md',
     '> ★★**2026-11-02 19:25 老板指示: 不再外发任何问询函 ⇒ 本草稿作废 (一封不发)**。',
     '> ★★**2026-11-02 19:25 → 19:45 修正: 本草稿改为「暂不发, 排在最后一级 (L4)」** —— ★**且优先走 L2**: 公开在售 MIPI-DSI 屏模组的驱动 IC 公开 (ST7701 / EK79007+EK73217) ⇒ Rockchip 内核自带 panel 驱动与时序 ⇒ **多半不用问厂家**。'),
]:
    fp = f'{PROJ}/state/outbox/{fn}'
    try:
        c = open(fp, encoding='utf-8').read()
        if old in c:
            c = c.replace(old, new, 1)
            open(fp, 'w', encoding='utf-8').write(c)
            print(f'[outbox] {fn} 标注已修正')
    except FileNotFoundError:
        pass

# ══════════════ 分片 ══════════════
def mutate(d):
    claims = d.setdefault("interface_claims", [])
    def add(key, value, note, ref):
        for c in claims:
            if c.get("key") == key:
                c.update({"value": value, "note": note, "ref": ref}); return
        claims.append({"key": key, "value": value, "note": note, "ref": ref})
    add("info_lookup_ladder", "L1网→L2换料→L3全试→L4问厂",
        "★★2026-11-02 19:45 老板定四级阶梯 (信息获取): ①**先上网找** (公开 datasheet / 公开 panel 驱动树 / 开源驱动源码 / 公开在售模组页 / 社区实测) ②**找不到就换替代料** (公开在售同类件) ③**所有元件都试过仍找不到** ④**才走采购渠道咨询厂家** ⇒ ★**纠正 19:25 落的「一律不发」** (ISS-142 由 closed 改 deferred) ⇒ 每级都要凭证, ★**\"都试过了\" = 替代料清单 (ISS-151)**。",
        "PROJECT_TRACKER.md#(1.62) + §0 变量 45")
    add("demo_procurement_channel", "public_stock",
        "★2026-11-02 19:45: demo 量少 (1 台) ⇒ **不走批量定制采购** ⇒ 物料走**公开现货/样品渠道** (公开在售 camera 模组 / MIPI-DSI 屏模组 / RK357x SBC) ⇒ ★**优先用别人已量产在卖的模组** ⇒ ★**Step1 = 公开 SBC + 公开在售模组, 零 PCB 零定制**。",
        "PROJECT_TRACKER.md#0 (变量 47)")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d
update_fragment("hw-lead", mutate)
print('[分片] hw.yaml 已更新 (2 claims)')
