#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_demo_board_priority.py —— 老板 2026-11-02 19:07 新指示落账 (预研 demo 板方案优先)"""
import yaml

P = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/issue_log.yaml'
d = yaml.safe_load(open(P, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

# ── ISS-139 (ISP tuning) 升为关键路径 ──
i = by['ISS-139']
i['severity'] = 'blocker'
i['due'] = '2026-11-05'
i['note'] = (i.get('note') or '') + (
    " ★★**2026-11-02 19:07 老板新指示后升级为 demo 板关键路径**: demo 要跑通「sensor→RK→OD(80类)→画框→屏」, "
    "★**ISP tuning 是这条链上的必经一环** (rkaiq 没现成 IQ ⇒ 必须自己做)。★**但它有硬前置**: 要先有 AR0234CS 在 RK3572 上的驱动能出 RAW (ISS-144), "
    "且要等镜头/模组定版才能标定 ⇒ ★**排期上与 ISS-144 并行准备, 不等它**。★**同时建议 (见 ISS-145)**: demo 板先用一个有现成 BSP 驱动+现成 IQ 的 sensor "
    "(IMX415 / OV02B10) 把链路打通, AR0234CS 驱动与 tuning 后补 —— ★**因为链路的 90% 是软件与接口, 与 sensor 无关**。")

# ── ISS-143 (结构) 暂缓 ──
i = by['ISS-143']
i['due'] = '2026-11-16'
i['note'] = (i.get('note') or '') + (
    " ★**2026-11-02 19:07 老板指示『暂时不考虑结构设计』⇒ 本单暂缓** (due 推到 11-16), 但 ★**口径结论已定 (判据 B': 有效余量 ≥4° ⇒ 俯角 ≤25.89°, 设计 25°) 继续有效**, "
    "demo 板阶段不消耗结构资源, 等整机方案重启时直接用。")

# ── 新开三条 ──
if not any(x['id'] == 'ISS-144' for x in iss):
    iss.append({
        'id': 'ISS-144',
        'title': '★★★★[demo 关键路径 #1] AR0234CS → RK3572 rkisp3 驱动移植 (★先出规格, 不出代码)',
        'severity': 'blocker', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 19:07 老板定的 demo 板方案 = RK3572 + AR0234CS + 视涯 0.49" ⇒ **采集链第一步就是「AR0234CS 在 RK3572 上出 RAW」**, '
            '★**而 AR0234CS 在 Rockchip 侧没有任何现成驱动** (实测: 上游主线无 · Rockchip BSP kernel 363 个 sensor 驱动里无 · rkaiq 无 IQ 文件 —— 见 `HW/OPEN_SOURCE_AVAILABILITY.md` §2)。'
            '⇒ **这是整条 demo 链的头号风险与最长路径**。'
            '⇒ ★**本单只要「规格」, 不要代码** (铁律: 大任务拆两步, 先出规格再出文件): '
            '①**移植起点**: 公开可用的完整 GPL 驱动 (RPi 版 `Kurokesu/ar0234-rpi-driver` 42KB + Jetson Orin 版 + ★**RK3588 同族 bringup `opensource206/UC788_AR0234_SENSOR_TO_RK3588`**) ⇒ ★**RK3588 那份最贴近 (同 ISP3 代, 同 SoC 家族)**; '
            '②**要改什么**: V4L2 subdev 骨架 + 寄存器时序 + 曝光/增益/帧长控制 + **DT overlay** + **rkisp3 的 format/帧率协商** (RK3572 用 rkisp3, 不是 rkisp1); '
            '③**rkaiq 侧要注册什么** (sensor 名/模式表, ISP3 的 drv 对接); '
            '④**验收判据**: ①v4l2-ctl 能 enumerate 到 subdev ②media-ctl 链路通 ③能拿到 1920×1200@60 RAW10 ④`rk_aiq_uapi2_sysctl_start` 不报错 ⑤抽帧亮度/行数/时间戳正确。'
            '⇒ ★**第一步先做「能不能出 RAW」的最小验证** (能枚举 + 能出帧), 调色/tuning 归 ISS-139。'),
        'owner': 'hw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-05',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'HW/OPEN_SOURCE_AVAILABILITY.md §2 · HW/DISPLAY_SENSOR_CHAIN.md §2.5',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:2x。★**先出规格不出代码** (上次派活两次 0 产出的教训: 任务书必须短、结论必须给全)。'
                 '★**规格写在 `HW/AR0234CS_RK3572_PORT_SPEC.md`** (新建), 字段: 移植起点/改动清单/DT/验收判据/工作量估计/卡点。'
                 '★**并给一条平行建议**: demo 板若被这条路径卡住, 用现成 BSP 驱动 + 现成 IQ 的 sensor (IMX415 / OV02B10) 先打通链路 ⇒ 见 ISS-145。'),
        'dispatched_at': None,
    })

if not any(x['id'] == 'ISS-145' for x in iss):
    iss.append({
        'id': 'ISS-145',
        'title': '★★★★[demo 关键路径 #2] demo 板 OD 管线打通规格: yolov5n INT8 → RKNN → 画框 → 视涯 049 显示',
        'severity': 'blocker', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 19:07 老板定的 demo 板链路: **sensor → RK3572 → OD 目标检测 (80 个常见目标类) → 画框 → 送到视涯 0.49" 1920×1080 屏显示**。'
            '⇒ **本单出「打通规格 + 验收判据」, 不写代码** (铁律: 先出规格)。'
            '★**已有可复用的基线** (A7S OD 项目): `SW/tools/timing_check.py` / RKNN_BENCH 复现链 (calib/acc 两步) / yolov5n INT8 量化流程 / 端到端打点口径。'
            '⇒ ★**规格要回答**: '
            '①**模型**: 直接复用 A7S 的 yolov5n INT8 (80 类) 还是重训/换版本? ★**先复用, 不重训** (时间不够, 且 80 类口径一致); '
            '②**后处理**: 画框在 CPU 还是 NPU 后? ★**建议 CPU (OpenCV/自研)**: 框数少, 不值得为它上 NPU; '
            '③**颜色/格式**: AR0234CS 输出 RAW10 → ISP3 处理 → YUV/NV12 → 送 DSI; ★**画框要画在 NV12/RGB 上, 不能画在 YUV420 上** (色度分量错位) ⇒ 画框前后置顺序要写死; '
            '④**显示**: 视涯 0.49" 1920×1080 MIPI-DSI + I2C ⇒ DRM/KMS plane 通路 + ★**面板 init code 与时序 (ISS-142 问询) 是硬前置**; '
            '⑤**分辨率链**: 相机 1920×1200 (16:10) → 屏 1920×1080 (16:9) ⇒ ★**letterbox 还是裁切** (boss 10-25「不裁剪」原则) ⇒ 建议 letterbox 上下加黑边; '
            '⑥**帧率与延迟**: OD 目标 60fps (OD 640×480) + 屏 60Hz; ★**60ms 硬指标 (ISS-129/137) 在 demo 阶段先不卡, 但要留打点**; '
            '⑦**验收判据**: 端到端真值 —— ①能出图 ②80 类检测框正确 ③框画在物体上不错位 ④屏上画面正常 (无色偏/撕裂) ⑤延迟有数 (先记, 不设门限)。'),
        'owner': 'sw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-05',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'SW/tools/timing_check.py · PROJECT_TRACKER.md §0 变量 42',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:2x。★**出规格, 不写代码** (同 ISS-144 的教训)。规格写到 `SW/DEMO_OD_PIPELINE_SPEC.md` (新建)。'
                 '★**依赖**: ①ISS-144 (采集) ②ISS-139 (ISP tuning) ③ISS-142 (面板 init code) —— ★**但规格本身现在就能写, 不等**。'
                 '★**并行建议**: 链路里 90% 与 sensor 无关 ⇒ ★**可用现成 BSP 驱动 + 现成 IQ 的 sensor 先把链路跑通** (IMX415 / OV02B10), AR0234CS 后补 ⇒ 这条建议要写进规格的"两条路径"章节。'),
        'dispatched_at': None,
    })

if not any(x['id'] == 'ISS-146' for x in iss):
    iss.append({
        'id': 'ISS-146',
        'title': '★★[等老板一句] demo 板形态: 模组+转接板 (我的建议) 还是 自制整板? —— 决定 PCB 与周期',
        'severity': 'high', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 19:07 老板指示做 demo 板, 但**没定 demo 板做成什么样** ⇒ 这一条直接决定周期与工作量, 必须先定。'
            '★**建议默认 = 模组 + 转接板** (不是自制整板): '
            '①**RK3572 模组** (现成, MIPI-CSI×2 + MIPI-DSI 4-lane + 电源已解决) '
            '②**AR0234CS 摄像头模组** (舜宇/欧菲 贴片模组, 镜头一并解决 ⇒ 顺便解掉 CRA/畸变/MTF 三笔账) '
            '③**视涯 0.49" 模组** (MIPI-DSI + I2C) '
            '④**一块转接板** (只走线: 模组↔模组 + 供电 + 调试口) —— ★**不做镜腿/镜框结构** (老板 19:07 明确暂不考虑结构)。'
            '⇒ ★**好处**: 不做 PCB 全板设计/DRC/打样 ⇒ 周期从"月"降到"周"; ★**坏处**: 体积大 (不是眼镜形态), 但 ★**demo 阶段本来就不追求形态**。'
            '⇒ ★**代价与风险**: 转接板仍要过一遍 DRC + 打样 (走 `state/gen_netlist.py` → `check_netlist` 那条链); '
            '★**供电**: BQ25896 充电 + 保护 + 电池接口沿用现成设计 (TPS7A20 系列 LDO 已在网表里)。'),
        'owner': 'boss', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-03',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'HW/DISPLAY_SENSOR_CHAIN.md §2.5 · state/gen_netlist.py',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:2x。★**建议默认值 = 模组+转接板**; 若老板说"要自制整板", 我按同一份需求重排 netlist 与打样计划。'
                 '★**这一条卡住 ISS-144/145 的硬件侧** (转接板网表要按它画) ⇒ ★**优先级最高的一问**。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(P, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('ok, issues =', len(iss))
