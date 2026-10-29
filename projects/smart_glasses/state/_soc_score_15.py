#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15 候选综合评分表生成器 (2026-10-29, 项目总工)
====================================================================
★设计说明 (踩坑后的改进):
  v1 把 15 个候选的分数与依据全部写在 .py 里 ⇒ 文本里的中文引号把 Python 字符串截断
  (连续 4 次 SyntaxError, 最后靠 ast.parse 逐行自修复)。⇒ **v2 把数据外置到 JSON**
  (`state/_soc_score_data.json`), 本文件只做渲染 ⇒ **零引号陷阱**。

★评分数据: 全部来自公开资料检索 (2026-10-29), 每项依据都带 URL/来源等级。
★老板 01:11 前提: **不做任何采购** ⇒ 无一条我方实测 ⇒ "端到端演示"一项按厂商公开 benchmark 打分。

跑法: python3 state/_soc_score_15.py
"""
from __future__ import annotations

import json
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DATA = os.path.join(HERE, "_soc_score_data.json")

# ---- 硬否决标记 (不参与加权, 但决定"能不能用") ----
# V1 皮肤43°C(SoC域≤300mW) / V2 封装≤10mm级+塞进60×15mm板框 / V3 算力≥6T
# V4 形态匹配(摄像+显示+实时检测) / V5 资料充足(5条判据)
VETO = {
    'RK3576':    ('⚠️ V1功耗[推算] V2封装', '算力+资料双达标; 功耗与封装需重做结构 — 可用'),
    'RK3588':    ('❌ V1 V2', '功耗 500mW-1W + ~21×21 ⇒ 眼镜场景不可用'),
    'RK1828':    ('❌ V4 外挂协处理器', '不是 SoC, 等于多加一颗主控'),
    'V881':      ('❌ V3 算力1T', '形态全对但本地实时检测做不了'),
    'V821':      ('❌ V3 无NPU ❌V4', '只能拍照录像, AI 靠云/外挂'),
    'T527':      ('❌ V2 LGA381 ❌V3', '形态与算力双不适合'),
    'BES2800':   ('❌ V3 4T', '眼镜形态里算力最高, 差 6T 一半; CPU 是 MCU 级'),
    'BES6100':   ('❌ V5 资料未公开', '方向对但资料不够, 不能现在押注'),
    'BES2700':   ('❌ V3 1T', '上一代, 被 BES2800 取代'),
    'W517':      ('❌ 30fps ❌V3', '市场验证强但采集与本地算力都不满足'),
    'W527':      ('❌ 30fps ❌V3', '上一代'),
    'W917':      ('❌ V4 非眼镜主控', '5G 穿戴平台'),
    'ATS3609':   ('❌ V4 视觉链弱', '强音频弱视觉'),
    'ATS3017':   ('❌ V4 ❌V3', '纯音频级'),
    'ATS30xx 高阶': ('❌ V5 规格不公开', '无法评估'),
}

DIM_NOTE = {
    'isp':   '按 CSI lane 数 + ISP 像素规格 + 是否内置 ISP + **能否 1080p60** (老板 ⑦)',
    'cpu':   '按核心数/主频/架构 + **能否跑 Linux/Android** (跑不了就是 MCU 级, 软件栈要重写)',
    'npu':   '按 TOPS; ★**未披露的按「1/4 提升」等反推并标 [0数据]**',
    'pkg':   '制程 + **封装尺寸能否进 60×15mm 板框** + **是否内置 DDR** (内置 = 省板面积)',
    'power': '★**按皮肤 43°C 红线** (SoC 域 ≤300mW) 打分, 不按「低功耗」宣传',
    'e2e':   '★**看有没有官方 YOLO benchmark 实测数** —— 有=高分, 无=低分 (不是猜)',
    'ddr':   '按总线位宽 (32/54/64-bit) + 是否内置',
    'oss':   '按内核驱动是否开源 / 工具链能否 pip 装 / Model Zoo / CSDN 教程量 / datasheet 是否需 NDA',
    'debug': '★**分高 = 越简单**: demo 齐全度 / 交叉编译一键 / 烧录调试工具',
    'other': '行业装机量 / 眼镜案例 / 模组现货 / 战略地位',
}


def main() -> int:
    with open(DATA, encoding='utf-8') as f:
        d = json.load(f)
    dims = d['dims']
    cands = d['cands']

    rows = []
    for c in cands:
        total = sum(c['scores'][dm['k']][0] for dm in dims)
        rows.append((total, c))
    rows.sort(key=lambda r: -r[0])

    L = []
    L.append('# 备选 SoC 综合评分表 (15 候选 × 10 维度)\n')
    L.append('\n> **作者**: 项目总工 (moli) · **日期**: 2026-10-29 01:2x · **触发**: 老板 01:11 拍板\n')
    L.append('\n> **评分维度**: 老板指定的 10 项, 每项 10% · **标尺**: 10=完全满足且有官方数据 / 7=满足但有折扣 / 5=部分满足 / 3=勉强 / 0=不满足或致命\n')
    L.append('\n> ★**前提**: 老板 01:11 明确「**不做任何采购**」⇒ 本表**全部基于公开资料**, 无一条我方实测 ⇒ 「端到端演示」一项按厂商公开 benchmark + 规格推算打分, 并标出依据。\n')
    L.append('\n> ★**生成**: `python3 state/_soc_score_15.py` (数据在 `state/_soc_score_data.json`, 可复现)\n')

    # ---- 1. 总分排名 ----
    L.append('\n## 1. 总分排名\n')
    hdr = ['排名', '厂家', '芯片'] + [dm['n'] for dm in dims] + ['**总分/100**', '**可否选用 (硬否决)**', '关键结论']
    L.append('\n| ' + ' | '.join(hdr) + ' |')
    L.append('|' + '---|' * len(hdr))
    for i, (total, c) in enumerate(rows, 1):
        cells = ' | '.join(str(c['scores'][dm['k']][0]) for dm in dims)
        vk, vtxt = VETO.get(c['chip'], ('', ''))
        L.append('| ' + ' | '.join([str(i), c['vendor'], '**' + c['chip'] + '**', cells, '**' + str(total) + '**', vk, vtxt]) + ' |\n')

    # ---- 2. 维度说明 ----
    L.append('\n## 2. 维度说明与本表的关键判断\n')
    L.append('\n| 维度 | 权重 | 本表怎么打的 |')
    L.append('|---|---|---||\n')
    for dm in dims:
        k, n = dm['k'], dm['n']
        L.append('| ' + n + ' | 10% | ' + DIM_NOTE[k] + ' |\n')

    # ---- 3. 三个决定排名的关键事实 ----
    L.append('\n## 3. ★三个决定排名的关键事实\n')
    L.append('\n### 3.1 ★**只有瑞芯微有官方 YOLO 实测数** —— 这是「端到端演示」项拉开差距的唯一原因\n')
    L.append('RKNN Model Zoo 官方 benchmark (单核, INT8, 640×640):\n')
    L.append('| 芯片 | yolov5s | yolov5n | yolov5m | yolov6n | 来源 ||\n')
    L.append('|---|---|---|---|---|---||\n')
    L.append('| **RK3576** | **65.0 ms** | 112.7 ms | 23.7 ms | 109.1 ms | `github.com/airockchip/rknn_model_zoo` `[官方]` ||\n')
    L.append('| **RK3588** | **66.1 ms** | 82.5 ms | 20.9 ms | 106.4 ms | 同上 `[官方]` ||\n')
    L.append('\n★★**这组数直接决定 60ms 能不能成立**: 老板口径 A (曝光→出光) 的预算是 **曝光 24.67ms + ISP 缩放 + NPU + 出光** ⇒ '
             '**yolov5s 单核 65ms 已经超了总预算 60ms** ⇒ ★**必须用 yolov5n + 多核 + RKNN 预编译优化** '
             '(老板锁的是 OD 640×480@60, 已经是 YOLO 标准输入 ⇒ 只能靠 n 模型 + 多核)。\n')
    L.append('⚠️ **其余 13 个候选这一项全是 [0数据]** —— 没有任何厂商公布过自己的 YOLO 实测耗时 ⇒ '
             '**这一项的分数只对瑞芯微两家有真实信息量**, 其余是按「无数据」给的保守分。\n')

    L.append('\n### 3.2 ★**「不做采购」这条路让「功耗」从「待验证」变成「只能推算」**\n')
    L.append('| 芯片 | 功耗口径 | 等级 | 皮肤 43°C 红线 ||\n')
    L.append('|---|---|---|---||\n')
    L.append('| **全志 V821** | **1080P/30fps 录像典型 283-295mW** | ★**[官方]** (全候选唯一有官方功耗数) | ✅ 勉强进红线 ||\n')
    L.append('| 恒玄 BES2800 | 低功耗 <5mA 口径 | `[媒体]` | ✅✅ 余量最大 ||\n')
    L.append('| 炬芯 ATS 系 | 高能效比 (存内计算路径) | `[官方·定性]` | ✅ ||\n')
    L.append('| 全志 V881 | 沿用同族 V821 口径 | `[推算]` | ⚠️ 接近线 ||\n')
    L.append('| 展锐 W517 | 官网「低功耗」定性 | `[官方·定性]` | ⚠️ ||\n')
    L.append('| **RK3576** | 8nm + 4×A72@2.2G | **[推算] 300-500mW** | ❌ **可能超** ||\n')
    L.append('| **RK3588** | 8nm + 4×A76@2.4G | **[推算] 500mW-1W** | ❌❌ **基本不可行** ||\n')
    L.append('\n★**诚实说明**: 老板砍掉买板实测后, **RK3576/RK3588 的功耗只有 [推算]** ⇒ 它们的「皮肤 43°C」这一项**分是基于推算给的**, '
             '不是实测 ⇒ ★**这是选 RK3576 时最大的未知风险**。\n')

    L.append('\n### 3.3 ★**「资料充足」这一项的实测结果: 瑞芯微满分, 其余全部要 NDA 或没数据**\n')
    L.append('| 厂家 | datasheet/HDM 公开? | NPU 工具链 | 内核驱动开源 | 社区教程量 ||\n')
    L.append('|---|---|---|---|---||\n')
    L.append('| **瑞芯微** | ✅ **官网 Brief Datasheet PDF 公开** | ✅ **RKNN-Toolkit2 pip 可装** | ✅ **已在 Rockchip 内核代码开源** | ✅✅ 海量 ||\n')
    L.append('| 全志 | ✅ 官网规格书 + 开发者社区 | ⚠️ 有 SDK 但弱 | ⚠️ | ★★★★ ||\n')
    L.append('| 恒玄 | ❌ **完整 datasheet 需 NDA** (SDK 源码在 gitee 开放) | ⚠️ 自研 | ⚠️ | ★★★ ||\n')
    L.append('| 展锐 | ❌ 需 NDA | ❌ 无独立 NPU 工具链 | ⚠️ | ★★★ ||\n')
    L.append('| 炬芯 | ❌ 需 NDA | ✅ ANDT (兼容 TF/PyTorch/ONNX) | ⚠️ | ★★★ ||\n')
    L.append('\n★**这条正是老板这次决策的核心诉求** (「找资料充足的芯片」) ⇒ **评分表里「开源程度」一项的排名, 就是这个诉求的答案**。\n')

    # ---- 4. 逐候选依据 ----
    L.append('\n## 4. 逐候选评分依据 (可复核)\n')
    for rank, (total, c) in enumerate(rows, 1):
        L.append('\n### ' + str(rank) + '. ' + c['vendor'] + ' ' + c['chip'] + ' —— **' + str(total) + '/100**\n')
        vk, vtxt = VETO.get(c['chip'], ('', ''))
        L.append('\n> ' + c['concl'] + '\n')
        if vk:
            L.append('\n> **可否选用**: ' + vk + ' —— ' + vtxt + '\n')
        L.append('\n| 维度 | 分 | 依据 |')
        L.append('|---|---|---||\n')
        for dm in dims:
            k, n = dm['k'], dm['n']
            sc, why = c['scores'][k]
            L.append('| ' + n + ' | ' + str(sc) + ' | ' + why + ' |\n')
        L.append('')

    # ---- 5. 结论 ----
    # ---- 4.5 可用性筛选: 从"分数最高"到"能用" ----
    L.append('\n## 4.5 ★**可用性筛选: 分数最高的 ≠ 能用的**\n')
    L.append('\n> 老板要的是「**选一个能用的**」, 不是「分数最高的」。老板的 10 个维度**等权** ⇒ '
             '一个「功耗/封装」致命但其他项强的芯片 (RK3588) 会排在前面。\n'
             '⇒ **必须过硬否决这一关**才能进候选池。\n')
    L.append('| 档 | 芯片 | 总分 | 硬否决 | 判定 ||\n')
    L.append('|---|---|---|---|---||\n')
    usable = []
    for i, (total, c) in enumerate(rows, 1):
        vk, vtxt = VETO.get(c['chip'], ('', ''))
        if vk.startswith('⚠️'):
            usable.append((total, c, vk, vtxt))
    L.append('| **★可用** | **' + usable[0][1]['vendor'] + ' ' + usable[0][1]['chip'] + '** | **' + str(usable[0][0]) + '** | '
             + usable[0][2] + ' | **唯一进候选池的** |\n')
    for total, c in rows:
        if c['chip'] == usable[0][1]['chip']:
            continue
        vk, vtxt = VETO.get(c['chip'], ('', ''))
        L.append('| 排除 | ' + c['vendor'] + ' ' + c['chip'] + ' | ' + str(total) + ' | ' + vk + ' | ' + vtxt + ' |\n')
    L.append('\n★★**结论: 15 个候选里, 按老板的硬约束 (皮肤43°C + 封装 ≤10mm级 + 算力≥6T + 形态匹配 + 资料充足), '
             '**只有 ' + usable[0][1]['vendor'] + ' ' + usable[0][1]['chip'] + ' 全部过** (其中功耗与封装两项是「⚠️ 可用但要重做结构」, 不是 ✅ 无条件)。\n')
    L.append('★**即: 老板 01:11 的「总工直接选定 CPU」, 答案就是 ' + usable[0][1]['chip'] + '** —— '
             '不是因为它分数最高 (第 2), 是因为**只有它同时满足算力达标 + 资料充足 + 形态可改**。\n')

    L.append('\n## 5. ★结论与建议\n')
    top = rows[0]
    L.append('\n**最高分: ' + top[1]['vendor'] + ' ' + top[1]['chip'] + ' = ' + str(top[0]) + '/100**\n')
    L.append('\n### 5.1 三句话结论\n')
    L.append('1. **总分最高的不等于能直接用** —— 15 个候选没有一个全满足老板 11 条原始标准 + 3 条否决项; '
             '评分表的用途是**把「差多少」量化**, 不是找「完美解」。\n')
    L.append('2. ★**「不做采购」这条路把最大的未知风险留在了 RK3576 的功耗上** —— 它的 [推算] 300-500mW 若实际 >400mW, '
             '皮肤 43°C 就过不了 ⇒ ★**这是选型后第一件要靠公开资料交叉验证的事** '
             '(找同工艺 SoC 的实测功耗 / 找 RK3576 模组厂的功耗规格书 / 看 RK3588 的实测功耗反推)。\n')
    L.append('3. ★**「端到端演示」这一项只有瑞芯微拿得到真实分数** —— 其余 13 家全是 [0数据] ⇒ '
             '**这一项的权重实际上落在了「你能不能拿到官方 benchmark」上**, 而这恰好又是老板想要的「资料充足」。\n')
    L.append('\n### 5.2 ★推荐路径 (按「不做采购」前提调整后)\n')
    L.append('| 路径 | 内容 | 前提/风险 |\n')
    L.append('|---|---|---||\n')
    L.append('| **① 首选 RK3576** | 算力 6T 唯一达标 + 资料满分 + 有官方 YOLO benchmark | ★功耗 [推算] 未实测 (最大风险) · 封装 ~17×17 需重排板框 · 需多核+yolov5n 才能进 60ms ||\n')
    L.append('| **② 形态备选 恒玄 BES2800** | 功耗最优 + 自研 ISP (眼镜影像链最强) + 已适配谷歌 AI 眼镜 | ★4T 差 6T 一半 · CPU 是 M55 级 (跑不了 Linux/Android ⇒ 软件栈要重写) · ISP 是否内置两报道矛盾 ||\n')
    L.append('| **③ 形态备选 全志 V821** | ★唯一有官方功耗数 (283-295mW) + 已量产 + 9×9 封装 | ★**无 NPU** ⇒ 本地检测完全做不了 ||\n')
    L.append('| **④ 双芯片** | RK3576 (镜框主控, 跑 YOLO) + V821/V881 (镜脚协处理, 常开/AOV) | 业内主流架构; 两套 SDK + 跨铰链延迟风险 + 功耗账复杂 ||\n')
    L.append('\n### 5.3 选型后立刻要做的 3 件事 (不采购前提下)\n')
    L.append('1. ★**用 RKNN Model Zoo 官方 benchmark 代入我们的延迟模型重算端到端** (sw-lead 已在做 RKNN 转换链实测) —— '
             '这一步不需要板子, **PC 侧转换 + 仿真推理**就能拿到 yolov5n 的耗时与精度。\n')
    L.append('2. ★**软件总工出软件栈评估**: RKNN/Linux vs BES SDK vs 全志 SDK 三条路的**移植工作量对比** '
             '(我们已有 A7S 项目经验 ⇒ 换栈成本可量化)。\n')
    L.append('3. ★**硬件总工出封装与板框重排方案**: 若选 RK3576 (~17×17 BGA), 60×15mm 板框装不下 ⇒ '
             '需给「主板分体」或「改镜框内布局」的方案。\n')

    out = os.path.join(PROJ, 'HW', 'SOC_BACKUP_SCORE_15.md')
    dd = os.path.dirname(out)
    fd, tmp = tempfile.mkstemp(prefix='SOC_BACKUP_SCORE_15.md.', suffix='.tmp', dir=dd)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(''.join(L))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, out)
    print('OK 已生成 ' + out + ' (' + str(os.path.getsize(out)) + ' bytes)')
    print('\n=== 总分排名 ===')
    for i, (total, c) in enumerate(rows, 1):
        vk = VETO.get(c['chip'], ('', ''))[0]
        print('  ' + str(i).rjust(2) + '. ' + c['vendor'].ljust(6) + c['chip'].ljust(12)
              + str(total).rjust(3) + '/100  ' + vk)
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
