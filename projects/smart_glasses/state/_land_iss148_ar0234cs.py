#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""land_iss148_ar0234cs.py —— ISS-148 收口 + 整机阶段三条"投板后必改"立项 + tracker 落账

hw-lead 19:5x~20:1x 交卷 (513 行): ★**四个未知量全部用开源途径查实, 0 次对外通信**
  路径: onsemi 官网 PDF 直链被 Akamai 403 ⇒ 走 **LCSC + Sunnywale 两个授权分销镜像** (Rev 3 / Rev 0, 同一 Publication Order Number)
  U1 功耗: Table 1 p.1 抬头 "<395 mW @120 FPS Full Resolution"; Table 16 p.18 分轨求和 Typ 372.6 / Max 646.4 mW
       ⇒ ★**datasheet 没有 60fps 电流行** ⇒ 60fps 值按物理依据取 120fps 的行为上界并标 [推算] ~300mW, 精确值留 [待核] 等 EVT
  U2 abs-max: Table 14 p.17: **VIN ≤ VDD_IO + 0.3 = 3.1V** ⇒ ★**3.3V I2C 上拉违反绝对最大额定值** ⇒ 必须改 2.8V (零 BOM 增量: 顶网换到 RAIL_SENSOR_VDD_IO, 同在 MAIN_PCB)
  U3 CRA: Table 1 p.1: **0° 或 28° 两个 PN 变体**; Figure 19 p.23 给 28° 完整曲线 (角落 27.97°)
  U4 模拟轨: 5 组供电, 含 **VDDIO_PHY 1.8V only** (Note 10) ⇒ ★**网表缺这条轨, 且 CONN_CAM 18p 已 18/18 占满 ⇒ 不供电就出不了图**
  ★口径修正: 0.92W 是 e-CAM **模组级含板载 ISP**, 本项目 ISP 在 RK3572 ⇒ POWER_BUDGET_V3 里"拒绝 AR0234CS"的否决理由**口径不成立**
⇒ ★**换料触发条件不成立 ⇒ AR0234CS 保留 (整机方案 sensor 不换)**
"""
import os
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

# ── ISS-148 收口 ──
i = by['ISS-148']
i['status'] = 'fixed'
i['owner'] = 'main'
i['verify_by'] = 'hw-lead'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = ('HW/AR0234CS_OPEN_SOURCE_FACTS.md (513 行: 四个未知量全查实 + datasheet 镜像路径 + 三条投板后必改 + 诚实边界) · '
                'HW/IMX415_DEMO_SENSOR_FACTS.md (demo sensor 侧) · ISS-154 (整机阶段新增项)')
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 20:1x 交卷并收口: 四个未知量全部用开源途径查实, 0 次对外通信** ⇒ ★**onsemi 官网 PDF 被 Akamai 403 ⇒ 走 LCSC + Sunnywale 两个授权分销镜像** (Rev 3 / Rev 0, 同一 Publication Order Number)。"
    "★**U1 功耗**: Table 1 p.1 '<395 mW @120 FPS' + Table 16 p.18 分轨 Typ **372.6** / Max **646.4 mW** ⇒ ★**datasheet 无 60fps 电流行** ⇒ 60fps 取 120fps 行为上界并标 [推算] ~300mW, 精确值留 [待核] 等 EVT。"
    "★**U2 abs-max**: Table 14 p.17 **VIN ≤ VDD_IO+0.3 = 3.1V** ⇒ ★**3.3V I2C 上拉违反绝对最大额定值** ⇒ 整机阶段必须改 2.8V (零 BOM 增量)。"
    "★**U3 CRA**: Table 1 p.1 **0° / 28° 两个 PN 变体** + Figure 19 p.23 28° 完整曲线 (角落 27.97°) ⇒ ★**CRA 查到了** (⇒ 120° 鱼眼需 ISP 鱼眼校正)。"
    "★**U4**: 5 组供电含 **VDDIO_PHY 1.8V only** (Note 10) ⇒ ★**网表缺这条轨 + CONN_CAM 18p 已占满 ⇒ 不供电就出不了图** (⇒ ISS-154)。"
    "★**口径修正**: 0.92W 是 e-CAM 模组级含板载 ISP, 我们 ISP 在 RK3572 ⇒ POWER_BUDGET_V3 里『拒绝 AR0234CS』的否决理由**口径不成立** (⇒ 已登记 PM 复算)。"
    "★**结论: 换料触发条件不成立 ⇒ AR0234CS 保留, 整机方案 sensor 不换**。★AND9658-D 在付费墙后 ⇒ 判『查不到』, 按老板规矩永久放弃该文档, 改问自家镜头厂要 CRA 曲线 (不违反禁令)。")

# ── ISS-153 追加: 换料必改项 ──
i = by['ISS-153']
i['desc'] = (i.get('desc') or '') + (
    " ★★**2026-11-02 20:1x 追加 (ISS-148 查实后)**: AR0234CS 的 abs-max **VIN ≤ VDD_IO+0.3 = 3.1V** ⇒ ★**AR0234CS 那版 I2C 上拉必须 2.8V** (零 BOM 增量: 顶网换到 RAIL_SENSOR_VDD_IO, 同在 MAIN_PCB) ⇒ ★**与 IMX415 相反** (IMX415 VI ≤3.3V ⇒ 3.3V 合法) ⇒ "
    "★**两条路的上拉电压差 0.5V, 换 sensor 时这条轨 + 上拉目标必须一起改**。")

# ── 新开 ISS-154: 整机阶段 AR0234CS 的 VDDIO_PHY 轨 + 上拉 ──
if not any(x['id'] == 'ISS-154' for x in iss):
    iss.append({
        'id': 'ISS-154',
        'title': '★★[整机阶段] AR0234CS 的 VDDIO_PHY 1.8V 轨缺失 + CONN_CAM 18p 占满 ⇒ 不供电就出不了图 (A/B/C 三方案待选)',
        'severity': 'high', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 20:1x ISS-148 查实 (公开 datasheet, Note 10): **AR0234CS 的供电是 5 组**, 其中含 **VDDIO_PHY 1.8V only** ⇒ '
            '⇒ ★**我们网表只有三条 sensor 轨 (CORE 1.2V / VDD_IO 2.8V / AVDD 2.8V), 没有 PHY 1.8V 轨** ⇒ ★**不供电 ⇒ sensor 出不了图**。'
            '⇒ ★**第二个障碍**: `CONN_CAM` 18p 已 18/18 占满 (18 脚全被引用) ⇒ **加不出第 4 条轨** ⇒ 必须在三个方案里选一个: '
            '**A** 换更大 pin 数的 FPC 座 (24p/30p, ★**与硬件方案定的 0.5mm/24p 正好一致**) + 加 PHY 1.8V 轨 (零 BOM 增量: 顶网换到现成的 LIGHT_1V8 轨, 同在 MAIN_PCB) '
            '**B** 用双电压轨的 PHY 供电方案 (若 datasheet 允许 PHY 与 IO 共轨) ⇒ ★**已被官方 Note 10 排除** '
            '**C** 把 PHY 1.8V 与其它信号共脚 (牺牲一个 I2C/复位脚) —— 需重排 FPC 针位。'
            '⇒ ★**注意**: 这条是**整机阶段 (AR0234CS) 的事** ⇒ demo 阶段 (IMX415) 不涉及 ⇒ **deferred 到整机阶段**, 但 ★**Step2 自研主板时就要按 24p 留余量**, 别再把 CONN_CAM 做成 18p 满。'),
        'owner': 'hw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-12',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'HW/AR0234CS_OPEN_SOURCE_FACTS.md (U4 + Note 10) · HW/DEMO_BOARD_HW_DECISION.md §4',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 20:1x。★**整机阶段项, demo 不卡**。★**Step2 画主板时的动作**: CONN_CAM 直接按 24p 画 (别 18p 满), 第四条轨 (1.8V PHY) 预留在同一 FPC 上。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[issue_log] ISS-148 fixed / ISS-153 追加 / 新开 ISS-154')

# ── tracker: (1.62) 补 AR0234CS 查实结果 ──
TP = f'{PROJ}/PROJECT_TRACKER.md'
t = open(TP, encoding='utf-8').read()
anchor = "**★ 19:5x 追加: IMX415 的硬件数据已落网表"
i = t.index(anchor)
add = """**★ 20:1x 追加: AR0234CS 的四个未知量 ★**全部用开源途径查实** (0 次对外通信; onsemi 官网 PDF 被 Akamai 403 ⇒ 走 **LCSC + Sunnywale 两个授权分销镜像**) ⇒ ★**换料触发条件不成立 ⇒ AR0234CS 保留, 整机方案 sensor 不换**:
| 未知量 | 查实结果 | 出处 |
|---|---|---|
| U1 裸片功耗 | Typ **372.6** / Max **646.4 mW** (120fps 全分辨); 抬头 "<395 mW @120 FPS" | Table 1 p.1 + Table 16 p.18 |
| U2 VDD_IO abs max | ★**VIN ≤ VDD_IO + 0.3 = 3.1V** ⇒ ★**3.3V I2C 上拉违规** ⇒ 整机阶段改 2.8V (零 BOM 增量) | Table 14 p.17 |
| U3 CRA | ★**0° / 28° 两个 PN 变体**, 28° 变体有完整曲线 (角落 27.97°) | Table 1 p.1 + Figure 19 p.23 |
| U4 模拟轨 | **5 组供电**, 含 **VDDIO_PHY 1.8V only** ⇒ ★**网表缺这条轨 + CONN_CAM 18p 满 ⇒ 不供电出不了图** | Note 10 |

⇒ ★**三条"投板后必改"已立项**: **ISS-153** (换 sensor 必改 I2C 上拉: IMX415 3.3V 合法 / AR0234CS 3.3V 违规) · **ISS-154** (整机阶段加 PHY 1.8V 轨 + FPC 改 24p) · ★**口径修正**: 0.92W 是 e-CAM 模组级含板载 ISP, 我们 ISP 在 RK3572 ⇒ `POWER_BUDGET_V3` 里「拒绝 AR0234CS」的否决理由**不成立** (⇒ PM 复算)。
⇒ ★**两条诚实边界**: ①datasheet **没有 60fps 电流行** ⇒ 60fps 值取 120fps 行为上界的 [推算] ~300mW, 精确值留 [待核] 等 EVT ②**AND9658-D 在付费墙后 ⇒ 判「查不到」**, 按老板规矩永久放弃该文档, 改问自家镜头厂要 CRA 曲线 (不违反禁令)。

"""
t = t[:i] + add + t[i:]
open(TP, 'w', encoding='utf-8').write(t)
print('[tracker] (1.62) 已补 AR0234CS 查实段')

# ── 分片 ──
def mutate(d):
    claims = d.setdefault("interface_claims", [])
    def add(key, value, note, ref):
        for c in claims:
            if c.get("key") == key:
                c.update({"value": value, "note": note, "ref": ref}); return
        claims.append({"key": key, "value": value, "note": note, "ref": ref})
    add("ar0234cs_power_120fps", "372.6/646.4mW",
        "★AR0234CS 裸片功耗 (公开 datasheet, ISS-148): Typ **372.6 mW** / Max **646.4 mW** @120fps 全分辨 (Table 16 p.18), Table 1 p.1 抬头 '<395 mW @120 FPS' ⇒ ★**datasheet 无 60fps 电流行** ⇒ 60fps 取行为上界 [推算] ~300mW, 精确值 [待核] 等 EVT。★口径修正: 第三方 0.92W 是**模组级含板载 ISP**, 我们 ISP 在 RK3572 ⇒ POWER_BUDGET_V3 里『拒绝 AR0234CS』的理由不成立。",
        "HW/AR0234CS_OPEN_SOURCE_FACTS.md §2")
    add("ar0234cs_vin_max", "3.1V",
        "★AR0234CS VIN 绝对最大 = **VDD_IO + 0.3 = 3.1V** (Table 14 p.17) ⇒ ★**3.3V I2C 上拉违规** ⇒ 整机阶段改 2.8V (零 BOM 增量: 顶网换到 RAIL_SENSOR_VDD_IO, 同 MAIN_PCB) ⇒ ★与 IMX415 相反 (IMX415 VI ≤3.3V ⇒ 3.3V 合法)。",
        "ISS-153 + HW/AR0234CS_OPEN_SOURCE_FACTS.md §3")
    add("ar0234cs_cra_variants", "0deg/28deg",
        "★AR0234CS 有 **0° 与 28° 两个 PN 变体** (Table 1 p.1), 28° 变体给完整 CRA 曲线 (角落 27.97°, Figure 19 p.23) ⇒ ★**CRA 查到了** ⇒ 120° 鱼眼需配 28° 变体 + ISP 鱼眼校正 (老板 10-25 已接受畸变)。★AND9658-D 正文在付费墙后 ⇒ 判『查不到』, 永久放弃该文档, 改问自家镜头厂要 CRA 曲线。",
        "HW/AR0234CS_OPEN_SOURCE_FACTS.md §4")
    add("ar0234cs_rail_count", "5rails_1v8phy",
        "★AR0234CS 供电 **5 组**, 含 **VDDIO_PHY 1.8V only** (Note 10) ⇒ ★**我们网表只有 3 条 sensor 轨 ⇒ 缺这条 ⇒ 不供电出不了图**; 且 CONN_CAM 18p 已 18/18 占满 ⇒ 整机阶段必须 FPC 改 24p + 预留 1.8V PHY 轨 (ISS-154)。",
        "ISS-154 + HW/AR0234CS_OPEN_SOURCE_FACTS.md §5")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d
update_fragment("hw-lead", mutate)
print('[分片] hw.yaml 已更新 (4 claims)')
