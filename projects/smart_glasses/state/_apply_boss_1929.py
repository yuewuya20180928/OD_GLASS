#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_boss_1929.py —— 老板 2026-11-02 19:29 指示落账: demo 判据收敛成两条, sensor 重排

老板原话: "当前demo不考虑功耗, sensor你只要考虑sensor能够输出1920*1080@60fps的规格就行, 不用考虑曝光方式,
只考虑规格能够做到60帧就行, sensor选型你考虑的太多了, 只考虑规格和数据(硬件数据、软件配置数据)来源是否充足就行"
"""
import yaml

P = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/issue_log.yaml'
d = yaml.safe_load(open(P, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

# ── ISS-141 (功耗账) → demo 不考虑功耗, 移到整机阶段 ──
i = by['ISS-141']
i['status'] = 'deferred'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:29 老板指示: 当前 demo 不考虑功耗 ⇒ 本单 defer 到整机阶段** (demo 板本来就不贴皮肤、不进皮肤温度账)。"
    "★**连带**: AR0234CS 的裸片功耗(U1)也不再是换料判据 ⇒ ISS-148 的 U1 检索取消。"
    "★**整机阶段再开时**: 要把 sensor 功耗并进整机功耗模型 ⇒ 皮肤 43°C / 电池 / 镜腿厚度三个联动量 (那时 AR0234CS 可能是主选)。")

# ── ISS-144 (AR0234CS 驱动移植) → defer 到整机阶段 ──
i = by['ISS-144']
i['status'] = 'deferred'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:29 老板把 demo 判据收敛成『规格 + 数据来源』两条后, demo sensor 改用 IMX415** "
    "(规格 3840×2160@60 可裁 1080p60 ✔ + 数据来源 10/10: 主线驱动 + RK BSP 驱动 + rkaiq isp3x 现成 IQ) "
    "⇒ ★**AR0234CS 的驱动移植不再是 demo 关键路径** ⇒ 本单 defer 到整机阶段 (AR0234CS 光学更好: 1/2.6\" 全局快门 + 120° 鱼眼 f=3.2432mm, 届时再付 5.5 人日 + 1~2 人周 tuning 的账)。"
    "★**规格文件保留** (`HW/AR0234CS_RK3572_PORT_SPEC.md`), 整机阶段直接接着做。")

# ── ISS-148 → 裁剪范围 (只留硬件数据) ──
i = by['ISS-148']
i['title'] = '★★[硬件] AR0234CS 硬件数据 (U2 VDD_IO abs max / U4 有无独立模拟轨) + ★demo sensor 改 IMX415 的四问'
i['due'] = '2026-11-04'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:29 范围收缩**: ①**U1 裸片功耗 —— 不查** (demo 不考虑功耗) ②**U3 CRA/光学 —— 不查** (demo 不追镜头/不暴露光方式) "
    "⇒ 只保留 **U2 (VDD_IO abs max ⇒ I2C_A 上拉 3.3V 还是 2.8V)** 与 **U4 (有无独立模拟轨 ⇒ 网表 SENSOR_AVDD 轨与 LDO 留不留)**; "
    "★**并追加 demo 真正要用的 IMX415 四问** (电源域 / 1080p60 怎么出 / 现成 IQ 适用哪个分辨率 / 模组采购硬判据) ⇒ 交两个文件: "
    "`HW/AR0234CS_OPEN_SOURCE_FACTS.md` (只留 U2/U4) + ★**`HW/IMX415_DEMO_SENSOR_FACTS.md`**。")

# ── ISS-149 → demo 硬件形态: sensor 模组改 IMX415 ──
i = by['ISS-149']
i['title'] = '★★★[硬件优先] demo 硬件形态落地: 一块主板 + **IMX415 sensor 模组** + 屏幕驱动板模组 + FPC 软排 ⇒ 网表级方案'
i['due'] = '2026-11-05'
i['desc'] = (i.get('desc') or '') + (
    " ★★**2026-11-02 19:29 变更: demo sensor 改 IMX415** (替代 AR0234CS) ⇒ 本单第 ② 段 (sensor 模组侧) 改为 **IMX415 模组**: "
    "★**供电轨要按 IMX415 重核** (现在是按 AR0234CS 写的 SENSOR_CORE 1.2V / SENSOR_VDD_IO 2.8V / SENSOR_AVDD 2.8V) ⇒ 等 `HW/IMX415_DEMO_SENSOR_FACTS.md` 出来后改; "
    "★**1080p60 输出方式** (sensor 窗口化 vs ISP crop) 也要在本单里落到网表 (是 sensor 侧配 ROI 还是 ISP 侧裁) ⇒ ★**注意与老板 10-25「禁止 ROI/crop」的边界**: "
    "那条禁的是「裁画面取景导致 FOV 变小」; ★**这里降 sensor 输出分辨率是为满足 ISP 吞吐 (8.4MP@60 = 505 MP/s 会超 250 口径), 不影响 FOV** ⇒ "
    "★**判据: 1080p60 = 124 MP/s, 余量充足**。★**其余各段不变** (主板一块 / 屏驱动板模组 / FPC / 去跨铰链 / 充电板并板或 USB 供电 / TBD-01 RK3572 球位图走开源渠道)。")
i['note'] = (i.get('note') or '') + (" ★**19:29 变更**: sensor 模组改 IMX415 ⇒ 供电轨与 1080p60 模式要重核 (等 ISS-148 的 IMX415 facts)。")

# ── 新开 ISS-150: IMX415 进 demo 的硬件规格 (netlist 改轨 + 模式) ──
if not any(x['id'] == 'ISS-150' for x in iss):
    iss.append({
        'id': 'ISS-150',
        'title': '★★★[硬件优先 #3] demo sensor 换 IMX415 ⇒ 网表三条电源轨要重核 + 1080p60 输出模式定案',
        'severity': 'high', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 19:29 老板把 demo 判据收敛成"规格 + 数据来源"两条后, **demo sensor 定 IMX415** '
            '(3840×2160@60 可裁 1080p60 ✔ + 数据来源 10/10: 主线驱动 + RK BSP 驱动 + rkaiq isp3x 现成 IQ) ⇒ **零移植零自研 tuning**。'
            '⇒ ★**本单 = 把 IMX415 落进硬件**: '
            '①**电源轨重核**: 现网表三条 sensor 轨 (SENSOR_CORE 1.2V / SENSOR_VDD_IO 2.8V / SENSOR_AVDD 2.8V) 是按 AR0234CS 写的 ⇒ ★**按 IMX415 的公开 datasheet 重核并改** (VDD / VDD_IO / VAA / VAA_PIX), '
            '改在 `HW/SCHEMATIC_V1_SPEC.json` 的 power_rails + `state/gen_netlist.py` (★**规格 JSON 是真源, 网表是生成物, 不要手改 CSV**); '
            '②**1080p60 输出模式定案**: IMX415 默认 8.4MP@60 = **505 MP/s 会超 ISP 250 口径** ⇒ 必须降分辨率 ⇒ 定案是**sensor 侧窗口化 (IMX415 支持 ROI) 还是 ISP 侧 crop** ⇒ ★**判据: 1080p60 = 124 MP/s 余量充足**; '
            '⚠️★**与老板 10-25「禁止 ROI/crop」的边界要说清**: 那条禁的是「裁画面取景导致 FOV 变小」; ★**这里是降 sensor 输出分辨率以满足 ISP 吞吐, 不改 FOV** ⇒ **不违反**; '
            '③**现成 IQ 文件适用分辨率**: `imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json` 是 8M 档 ⇒ 裁到 1080p60 能否直接用 / 要不要重调 (★**这是 demo 唯一可能的 tuning 工作**); '
            '④**I2C_A 上拉电平** 按 IMX415 的 VDD_IO 重核 (现在 3.3V 是按 AR0234CS 留的, 且有未闭环的 TBD-05)。'
            '⇒ **交卷**: 改完网表 + 三个生成器 + 两个门禁 rc=0 + `HW/IMX415_DEMO_SENSOR_FACTS.md` 的四条结论落账到 `state/fragments/hw.yaml` + tracker §(1.60)。'),
        'owner': 'hw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-05',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'PROJECT_TRACKER.md §(1.60) + §0 变量 46 · HW/SCHEMATIC_V1_SPEC.json · state/gen_netlist.py',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:3x。★**硬件优先** (老板 19:25 指示①)。★**依赖 ISS-148 的 IMX415 facts** (电源域 + 模式表 + IQ 适用性)。'
                 '★**与 ISS-149 的分工**: ISS-149 = 形态与连接器方案 (主板/FPC/模组/去跨铰链), ★本单 = sensor 侧电源轨与输出模式的**网表级改动**。'
                 '★**别改判据**: check_netlist 31 条 / check_kicad_net 5 条不许放松。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(P, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('ok, issues =', len(iss))
