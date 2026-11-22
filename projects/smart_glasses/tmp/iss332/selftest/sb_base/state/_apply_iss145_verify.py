#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_iss145_verify.py —— ISS-145 验收收口 + 新开 P0 单 (构建环境 / toolkit target) + demo 三线并行落账"""
import yaml

P = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/issue_log.yaml'
d = yaml.safe_load(open(P, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

# ── ISS-145 验收收口 ──
i = by['ISS-145']
i['status'] = 'fixed'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = ('SW/DEMO_OD_PIPELINE_SPEC.md (51KB / 624 行, 7 章 + 附录 A 待核 16 条 + 附录 B 下一步) '
                '· state/fragments/sw.yaml (原子写, 97 条 claims)')
i['note'] = (i.get('note') or '') + (
    " ★**2026-11-02 19:1x main 验收通过**: 规格 7 章齐全 (§1 模型 / §2 推理运行时 / §3 后处理与画框 / §4 显示通路 / "
    "§5 帧率与延迟打点 / §6 验收判据 / §7 两条路径对比) + 附录 A 待核 16 条 + 附录 B 下一步; 分片原子写可解析 ✔。"
    " ★**它纠正了我派单里的一个口径错误**: `SW/tools/timing_check.py` 是**硬件时序算术复核器** (复位 RC/I2C/ADC/TMP117/USB/热), "
    "★**不含端到端视频打点** ⇒ 真正的打点出处 = `SW/ARS45_INT8_CHAIN.md` §4 (B8 埋点表) + `SW/RKNN_BENCH.md` §4.1 (S4~S10 分段账) —— "
    "★**我派单时说的『复用 timing_check.py 打点』是错的, 规格已按正确出处写**。"
    " ★**它报的两条 P0 风险我已实测复核为真**: ①★**本机没有任何 RKNN 工具链** (`rknn/api/rknn.py` 全盘找不到) ⇒ "
    "『直接复用 A7S 的 .rknn』不成立, ★**rk3572 是否是 toolkit2 2.3.2 的合法 target 未证** (RKNN_BENCH.md 只证过 rk3576); "
    "②★**本机无源 ONNX / 无校准集 / 无 .rknn** (`~/Public/radxa_yolo` 已不存在, 全盘 find 无 .onnx/.rknn) ⇒ ★**下一步第 0 步是恢复构建环境, 不是写代码**。"
    " ⇒ 已新开 **ISS-147** (恢复构建环境 + 证 rk3572 target)。"
    " ★**它的路径判断**: 软件侧 **75% 与 sensor 无关** (工时口径 65%), 路径B 省 **10~14 人天 ≈ 2~3 周**; "
    "★**真瓶颈是面板 init code** (问询函未发) ⇒ 建议 **面板问询外发 + 路径B + AR0234CS 驱动/tuning 三线并行 (不是二选一)**。"
    " ★**关键技术判断 (可执行)**: 框画在 **NV12 的 Y 平面不碰 U/V** (否则色度错位) + **画框在缩放之前** (16:10→16:9 等比 letterbox k=0.9, 内容 1728×1080, 左右各 96px 黑边)。")

# ── 新开 ISS-147: P0 构建环境 ──
if not any(x['id'] == 'ISS-147' for x in iss):
    iss.append({
        'id': 'ISS-147',
        'title': '★★★[demo P0] 恢复 RKNN 构建环境 + 证明 rk3572 是 rknn-toolkit2 2.3.2 的合法 target —— 不解决这条, 软件侧一步都动不了',
        'severity': 'blocker', 'source_blocker': None, 'source_agent': 'main',
        'desc': (
            '★2026-11-02 19:1x ISS-145 交卷时实测发现 (main 已复核为真): '
            '①★**本机没有 RKNN 工具链** —— 全盘找不到 `rknn/api/rknn.py` (conda envs 也是空的) ⇒ ★**"直接复用 A7S 的 .rknn" 这条捷径不成立**; '
            '②★**rk3572 是否是 toolkit2 2.3.2 的合法 target 未证** (`RKNN_BENCH.md` 只证过含 rk3576) ⇒ ★**"模型零转换直接复用"归零**; '
            '③★**本机没有源 ONNX、没有校准集、没有 .rknn** —— `~/Public/radxa_yolo` 已不存在, 全盘 find 无 *.onnx / *.rknn。'
            '⇒ ★**这是 demo 链路的第 0 步 (软件侧)**: 恢复环境 + 证明 target, 否则 SW 侧连一个模型都产不出来。'
            '⇒ **要做**: ①**先找资产**: 板子 (Radxa Cubie A7S, 192.168.2.5) 上 / 备份 / 网盘里还有没有 `radxa_yolo` 的 ONNX 与校准集? '
            '⇒ ★**注意板子 SSH 密码认证 (sshpass -p <BOARD_SSH_PASSWORD>) 且 IP 会变 (先 `getent hosts radxa-cubie-a7s.local` 确认)**; '
            '②**装工具链**: rknn-toolkit2 2.3.2 (pip, 与板端 rknn-toolkit-lite2 版本对齐) + 目标平台确认 rk3572; '
            '③**若无 ONNX**: 从 yolov5 仓库导出 (★**注意 sw-lead 的发现: 仓库里唯一转换+实测过的是 yolov5s@640, yolov5n 本地无 ONNX**) ⇒ '
            '★**先确认到底用 n 还是 s** (n: 更快/更小但精度没在本机证过; s: 有实测 F1 0.3139) ⇒ **这是要老板/我拍的一个口径**; '
            '④**校准集**: 重建 (OD 场景实拍 300 张, 覆盖 80 类); ⑤**产出判据**: 能一条命令产出可上板的 .rknn + 板端 acc 复现链跑通。'),
        'owner': 'sw-lead', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-04',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'SW/DEMO_OD_PIPELINE_SPEC.md §2 + 附录 A (P0 ①②③) · SW/RKNN_BENCH.md · SW/ARS45_INT8_CHAIN.md',
        'verify_by': 'main', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 19:2x。★**这是 demo 板软件侧的第 0 步, 优先于一切写代码**。'
                 '★**建议打法**: 先跑 ①找资产 (板子/备份) —— 成本最低, 命中就省掉导出+装工具链的两天; 找不到再走 ②③。'
                 '★**板子 SSH 提醒**: 密码认证 (sshpass -p <BOARD_SSH_PASSWORD>), ★**IP 会变, 先 getent hosts radxa-cubie-a7s.local 确认, 不要用写死的**。'
                 '★**别把 yolov5n 当既定**: 本地无 ONNX 且未实测 ⇒ 规格里写的是 M1/M2 二选一。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(P, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('ok, issues =', len(iss))
