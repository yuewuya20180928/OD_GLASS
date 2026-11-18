#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_boss_1925_directives.py —— 老板 2026-11-02 19:25 四条指示落账

① 优先硬件, 软件次之, 结构不考虑
② demo 主板 = 一块主板 + sensor 模组 + 屏幕驱动板模组, 两者用 FPC 软排连主板
③ 不发任何邮件给厂家, 不再考虑问询函
④ 先查主流开源网站/社区; 查完仍需厂家解答 ⇒ **放弃该物料, 直接换友商**
"""
import yaml

P = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/issue_log.yaml'
d = yaml.safe_load(open(P, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

# ── ISS-142 (onsemi 问询) → 不外发, 作废 ──
i = by['ISS-142']
i['status'] = 'closed'
i['fix_ref'] = '无 (按老板 19:25 指示取消外发)'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:25 老板指示: 不会发任何邮件给任何厂家, 后面不考虑任何问询函 ⇒ 本单作废 (草稿不外发)**。"
    "★**它原本卡的 4 条 (ISS-139 tuning IQ / ISS-141 功耗 / ISS-144 VDD_IO abs max 与 I2C 电平 / ISS-145 面板 init code) "
    "改按老板规则处理**: ①**先查主流开源网站/社区/交流社区** (公开 datasheet PDF、开源驱动源码、开源 sensor 库、模组厂公开规格、"
    "Issue/论坛/开源硬件社区) ②**查完一轮仍需厂家解答 ⇒ 该物料/器件方案直接放弃, 直接考虑友商替换** ⇒ 落到 **ISS-148** (AR0234CS 四个厂家专属未知量的开源检索 + 换料判据)。")

# ── ISS-146 (demo 板形态) → 已定 ──
i = by['ISS-146']
i['status'] = 'verified'
i['verify_by'] = 'main'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = 'PROJECT_TRACKER.md §(1.59) + §0 变量 44 · state/gen_netlist.py (FPC 连接器方案见 ISS-149)'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:25 老板直接给了形态** (不是模组+转接板, 是更细的版本): ★**一块主板 + sensor 画成模组 + 屏幕驱动板也画成模组, "
    "sensor 模组与屏幕模组各用 FPC 软排连到主板** ⇒ ★**这条不再是待拍板项, 已定**。"
    "★**对硬件的影响 (交给 ISS-149)**: 主板上要有两个 FPC 连接器 (camera FPC + display FPC) + sensor 模组侧供电/控制 + 屏模组侧供电/控制; "
    "★**屏的 init code 变成模组的采购硬判据** (模组必须随货提供 init code/时序, 否则不买) ⇒ ★**这样就不需要发问询函了** —— "
    "★**规则落地**: 厂家专属信息一律**写进采购硬判据** (随货必须给), 而不是发邮件去问。")

# ── ISS-143 (结构) → 直接不考虑 ──
i = by['ISS-143']
i['status'] = 'closed'
i['fix_ref'] = 'MECH/ISS047_FOV_TABLE.md (口径结论保留, 供整机阶段复用)'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:25 老板指示: 结构问题直接不考虑 ⇒ 本单关闭**。"
    "★**保留**: ISS-047 的口径结论 (判据 B' 有效余量 ≥4° ⇒ 俯角 ≤25.89°, 设计 25°, h_max(d=35)=16.32mm; 边框遮挡 1.91°) "
    "★**不是作废, 是冻结** ⇒ 等整机阶段重启时直接接着用, 不重复推导。")

# ── 新开 ISS-148: AR0234CS 厂家专属未知量 → 开源检索轮 + 换料判据 (硬件优先) ──
if not any(x['id'] == 'ISS-148' for x in iss):
    iss.append({
        'id': 'ISS-148',
        'title': '★★★[硬件优先 #1] AR0234CS 四个厂家专属未知量: 开源检索一轮 ⇒ 查不到就**换友商 sensor** (老板 19:25 规则四)',
        'severity': 'blocker', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 19:25 老板规则: ①优先硬件 ②**不发邮件给厂家, 不考虑问询函** ③**先查主流开源网站/社区/交流社区** '
            '④**查了一圈之后若仍需厂家解答 ⇒ 该物料/器件方案直接放弃, 直接考虑友商替换**。'
            '⇒ 本单 = 把 AR0234CS 上**必须问厂家**的 4 个未知量, **用开源途径各查一轮**, 并给出**换料判据**。'
            '★**四个未知量 (按"查不到就换料"的严重度排序)**: '
            '**U1 裸片 active 功耗 @1920×1200@60** (直接决定整机功耗/皮肤 43°C/电池/镜腿厚度; ★**替代来源: onsemi 公开 datasheet PDF '
            '(不是问询函, 是公开资料) + 各模组厂公开 spec + 开源驱动/评测文章里的实测值**); '
            '**U2 VDD_IO 绝对最大额定值** (决定 I2C_A 上拉能不能留 3.3V; ★**替代来源: 公开 datasheet + RPi/Jetson 驱动源码里的电压假设 + 社区实测**); '
            '**U3 CRA / 光学规格** (决定 120° 鱼眼能不能配直线镜; ★**替代来源: 公开的 AND9658-D 引用/模组厂公开镜头配对/机器视觉相机厂公开规格**); '
            '**U4 有无独立模拟轨 (VAA 类)** (决定网表里 SENSOR_AVDD 那条 2.8V 轨与一颗 LDO 留不留)。'
            '⇒ ★**换料判据 (写死)**: ①**U1 查不到** ⇒ AR0234CS 功耗不可知 ⇒ **换** (整机功耗与皮肤温度是红线, 不能带 [0数据] 上板); '
            '②**U2 查不到** ⇒ I2C 电平无解 ⇒ ★**先改设计** (I2C 上拉改 2.8V + 逐个核同总线从设备) 而不是换料; '
            '③**U3 查不到** ⇒ 走**鱼眼 + ISP 鱼眼校正** (可接受, 老板 10-25 原则) 不换料; '
            '④**U4 查不到** ⇒ 按"最保守"设计: 保留 2.8V 轨 (多一颗 LDO 的成本 ≪ 缺轨的风险)。'
            '⇒ ★**真正的换料触发条件只有 U1** ⇒ ★**本单第一优先是把 U1 查实**。'
            '⇒ ★**友商候选 (若 U1 查不到, 按"≥1080p60 + 有现成 BSP 驱动 + 有现成 rkaiq IQ"排序)**: '
            'IMX415 (★RK BSP 驱动 `imx415.c` ✔ + rkaiq isp3x IQ ✔, ★但 1/1.8" 太大 + 滚动快门 + 8MP) · OV02B10 (✔ 驱动 + ✔ IQ, ★但 1600×1200@30 不达标) · '
            'IMX296 / IMX327 (全局快门, ★但 1280×800 / 1440×1080 宽高不够) ⇒ ★**结论: 若 U1 查不到, 候选池很窄 ⇒ '
            '★换料前必须先把"≥1080p60"这条硬指标与"有现成驱动+IQ"这条软偏好分开看** —— 宁可做一次驱动移植 (5.5 人日, ISS-144 已算清), 也不要带一个不可知的功耗上板。'),
        'owner': 'hw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-04',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'HW/AR0234CS_RK3572_PORT_SPEC.md §5 (卡点 R2/R3/R4) · HW/OPEN_SOURCE_AVAILABILITY.md · HW/POWER_BUDGET_V3.md',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:3x。★**硬件优先的第一条** (老板 19:25 指示①)。'
                 '★**检索范围写死**: ①上游/主线内核源码 ②GitHub 开源驱动源码 (RPi/Jetson/RK3588 三份) ③**公开 datasheet PDF** '
                 '(onsemi 官网 PDF / Mouser / DigiKey 公开镜像 —— ★**这是公开资料, 不是问询函, 允许用**) ④openipc / 公开 sensor 库 '
                 '⑤机器视觉相机厂/模组厂**公开**规格页 (Arducam / Vadzo / e-CAM 等) ⑥开源硬件社区/论坛/Issue 里的实测贴 '
                 '⑦★**不要去查任何"需要厂家回复才能拿到"的东西** (不要找代理、不要发邮件、不要在社区发帖问厂家)。'
                 '★**交卷**: 每个未知量写 ①结论 (查到/查不到) ②**证据 URL + 引用的具体行/表** ③查不到时的处置 (按上面判据) '
                 '④**若判据命中换料 ⇒ 给出候选排序与推荐**。★**不许写"应该可以"** —— 查不到就写查不到。'),
        'dispatched_at': None,
    })

# ── 新开 ISS-149: demo 硬件形态落地 (主板 + 两模组 + FPC) ──
if not any(x['id'] == 'ISS-149' for x in iss):
    iss.append({
        'id': 'ISS-149',
        'title': '★★★[硬件优先 #2] demo 硬件形态落地: 一块主板 + sensor 模组 + 屏幕驱动板模组 + FPC 软排 ⇒ 出网表级方案',
        'severity': 'blocker', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 19:25 老板给定形态: ★**主板 = 一块板; sensor 画成模组; 屏幕驱动板也画成模组; '
            'sensor 模组与屏幕模组各用 FPC 软排连到主板上** ⇒ 本单把它落成**网表级方案** (不是画图, 是把网表改对)。'
            '⇒ ★**要改的东西**: '
            '①**连接器**: 主板上两个 FPC 连接器 (camera FPC + display FPC) ⇒ ★**规格要定**: 针数/间距 (0.5mm 主流)/ 翻盖式或非触式 / 额定电流 / FPC 弯折寿命 '
            '(★**跨铰链不做了** —— 老板 19:25 说不考虑结构 ⇒ ★**camera FPC 与 display FFC 都走板内/短距**, 不跨铰链 ⇒ ★**原 CONN_CAM/CONN_LIGHT 的"跨铰链"属性要去掉**); '
            '②**sensor 模组侧**: AR0234CS + 镜头 (贴片模组) + FPC 出线 + 供电 (3.3V? ★**模组自带 LDO 还是主板供 1.2V/2.8V 要定**) + I2C (SCCB) + MCLK + RESET + CSI 差分 (★**模组自带 AC 耦合电容吗? 要在采购规格里写死**); '
            '③**屏幕模组侧**: 视涯 0.49" 1920×1080 SiOLED + **驱动板** + FPC 出线 + 供电 + I2C (DDC) + DSI 差分 + ★**init code/时序必须随模组提供** (采购硬判据, 不用问询函); '
            '④**主板**: RK3572 (★**是 RK3572 模组还是裸芯片焊上去? 老板说"主板一个板子" ⇒ 我按"裸芯片 + 主板自绘"理解, ★**但 RK3572 的球位图官方未到 (TBD-01) ⇒ 主板画不出来** ⇒ ★**这一条要么等公开资料, 要么按老板规则换主控** ⇒ 单独列判据); '
            '⑤**去掉跨铰链后的连带影响**: 原网表里 CONN_CAM/CONN_LIGHT 走铰链 + 充电板在镜框 (J_CHG 跨铰链) ⇒ ★**demo 板是一块板 ⇒ 充电板也要并进主板** (或 demo 阶段直接 USB 供电不装电池) ⇒ ★**这两条都要给方案**; '
            '⑥**电源**: demo 板供电 (USB-C 5V → BQ25896 → 电池? ★**demo 阶段建议直接 USB 供电 + 保留充电电路占位**, 减少一块板)。'
            '⇒ ★**本单要交**: `HW/DEMO_BOARD_HW_SPEC.md` (形态/连接器/三个模组的采购硬判据/主板上要有哪些轨与接口/去跨铰链后的网表改动清单) '
            '+ **直接改 `state/gen_netlist.py`** (这是机械活, 能自己做完就做完) + 跑三个生成器 + 两个门禁 rc=0。'
            '⇒ ★**TBD-01 (RK3572 球位图) 是硬卡点**: 拿不到公开资料 ⇒ 按老板规则换主控 —— 但换主控会把 ISP3/NPU/DSI 全部重来 ⇒ '
            '★**本单先给"TBD-01 走开源渠道能否拿到"的结论** (公开渠道: 瑞芯微官网 datasheet / 公开模组厂原理图 / 开源硬件项目的 RK3572 原理图), 拿不到再谈换料。'),
        'owner': 'hw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-05',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'PROJECT_TRACKER.md §(1.59) + §0 变量 44 · state/gen_netlist.py · HW/DISPLAY_SENSOR_CHAIN.md',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:3x。★**硬件优先的第二条**。★**与 ISS-148 的关系**: ISS-148 决定 sensor 留不留 (U1 功耗查不到就换料) ⇒ '
                 '★**本单先按 AR0234CS 做, 但 sensor 模组的采购硬判据要写成可替换的** (靶面/功耗/供电/接口都列清, 换料时只改这几项)。'
                 '★**本单自己动手的部分** (能机械做完的做完): 网表里的跨铰链属性去掉 + FPC 连接器位 + 充电板并板方案 + USB 供电方案。'
                 '★**TBD-01 若查不到 ⇒ 按老板规则处理 (换主控), 但换主控代价极大 ⇒ 先穷尽公开渠道。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(P, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('ok, issues =', len(iss))
