#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
接手指南生成器 (gen_start_here) —— 让「只从 GitHub 同步」的人 30 秒知道: 现在在哪、要什么、下一步做什么
================================================================================
★为什么要有这个: 老板 01:25 问"下次从 GitHub 同步是不是就知道当前的目标、计划"。
  实测当时的仓库: README 里的数字还是 10-25 的 (写着 51 条 issue, 实际 86 条)、
  TODO 里「已开工」和「可派」混在一起、tracker 156KB 没有索引 → **答案是"不知道"**。
  ⇒ 本脚本把「接手指南」也变成**自动生成** (数字全部来自真源) → 从此 README/指南永不过期。

用法:  python3 state/gen_start_here.py [--out docs/START_HERE.md]
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ★ 项目总工维护的"下一步 3 件事" (叙述, 每次发布刷新)
NEXT3 = [
    ("① **打印包开打** (不等任何人)", "`PRINT/ars45_print_pack.3mf` → 你那侧切片 → 量 49 项 → 回填 `state/measurements.yaml` 的 M-PRINT。**这是把「设计态推算」变成「实物实测」的唯一入口**, 也是三个硬指标唯一能拿真数的路 (打印机跨网段, G-code 只能在你那侧切一次)"),
    ("② **原理图交叉评审 + 投板前网表重整** (mech 挑机械/热/装配 · sw 挑时序/信号/电源时序)", "原理图 **V1.4 已交卷** (9 页图页 / netlist 397 行 13 列 / BOM 293 位号 / `check_netlist` 28 条 + `check_kicad_net` 5 条全过 / 生成器幂等) → 两方挑刺 → 我裁决 → 闭掉 `HW/ERC_DRC_CHECKLIST.md` §D 的 2/3 项。★另外 ISS-094: 投板前网表要做 **pin-centric 重整** (现在是『连接清单』模型, 导出后仍有 6 个单点网)"),
    ("③ **老板拍板: 板宽 12 vs 15mm + 跨铰链大电流 + 催原厂**", "① **板宽**: hw-lead 实算 12mm 对逃线带误差只剩 0.20-0.30mm → 建议第一台锁 **15mm** (顺带 SoC 横向热扩散 2→3.5mm)。② **跨铰链大电流**: 电池在镜脚 (体积硬约束) → **1.5A 充电电流过铰链**; 若拍板『按需触发 130mAh』→ 电池可能装进镜框 → 跨铰链降回 **0.55A** (跟 Q4 续航口径耦合)。③ **原厂那封催信**: 第一封已 6 天未回, 追加问 (封装总球数 ≥72 / DP1.4 是 TX 还是 RX / 有无 DSI TX / USB3.0 是否引出) 已拟好, **你说一声我就发**"),
]

# ★ 不可信的数字 (老板/接手人最容易踩的坑)
TRAPS = [
    "**README 不含任何会过期的数字** —— 只做导航; 一切状态看 `docs/STATUS_SUMMARY.md` 与 `docs/PROJECT_STATUS.md` (自动生成)",
    "**2026-10-25 之前的 issue 数 (51 条 / 内部 28 / 等外部 18) 全部作废** —— 现在是 86 条, 以 `state/issue_log.yaml` 为准",
    "**任何 `[媒体]` 级规格不能当芯片级规格用** —— 尤其显示 TX: 官网写「集成 DP1.4」但**没写方向**, 媒体写「DP1.4 RX」→ **不许据此断定是 TX** (见 §(1.25) 的证据分级)",
    "**`HW/netlist_v1.csv` 是生成物, 不是真源** —— 真源是 `state/gen_netlist.py`; 手改 CSV 会被下次生成覆盖 (10-27 发生过: 276 行手改版差点被 108 行生成器冲掉)",
    "**实测数据 0/10 项** —— 两个硬指标目前全是推算, 任何「达标」结论都必须等实物",
    "**`HW/netlist_v1.net` 不是投板文件** —— 导出器已重写 (引脚号取自 node 名里的引脚提示; 无 pin 冲突/无幽灵器件/无隐式短路; `state/check_kicad_net.py` 5 条全过), 但网表模型仍是『一行=一根连接』, **投板前要做 pin-centric 重整** (ISS-094)",
    "**10-27 09:0x 复审挖出的 4 类缺陷** (BAT_PROT 节点悬空 / 电池保护并联+无栅极+无电芯负极 / 网名复用致 KiCad 短路 / .net 引脚号是编的) 已修 —— **说明『图画完了』这句话必须配门禁数字, 不能只凭肉眼**",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(PROJ, "docs", "START_HERE.md"))
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    log = yaml.safe_load(open(os.path.join(HERE, "issue_log.yaml"), encoding="utf-8")) or {}
    issues = log.get("issues") or []
    state = yaml.safe_load(open(os.path.join(PROJ, "STATE.yaml"), encoding="utf-8")) or {}
    summ = state.get("summary") or {}
    open_i = [i for i in issues if i.get("status") not in ("closed", "deferred", "wontfix")]
    inflight = [i for i in issues if i.get("status") in ("fixing", "fixed")]
    by_own = collections.Counter(i.get("owner") for i in open_i)
    boss = [i for i in open_i if i.get("owner") == "boss"]
    nm = state.get("needs_matrix") or {}

    stage = "G0 纸面冻结"
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "stage_gate.py")], capture_output=True, text=True, timeout=120)
        for line in (r.stdout or "").split("\n"):
            if "当前在「 in line and 」还差" in line:
                stage = line.strip()
                break
    except Exception:
        pass

    L = []
    L.append("# START_HERE · 接手指南 (自动生成)\n")
    L.append(f"> 生成 **{now}** | 数据源: `state/issue_log.yaml` + `state/STATE.yaml` + 门禁实时输出\n")
    L.append("> ★**本文件是自动生成的, 数字不会过期** —— 老板 01:25 提的需求: 下次只从 GitHub 同步, 就能知道当前目标与计划。\n")

    L.append("\n## 0. 30 秒现状\n")
    L.append("| 问 | 答 |\n|---|---|\n")
    L.append(f"| **现在在哪个阶段?** | {stage} |\n")
    L.append(f"| **这一阶段的目标?** | **G1 = 硬件原理图/PCB 定稿**。G0 的准出判据全是数字, 差 4 项 |\n")
    L.append(f"| **产出物 / 阻塞 / 未闭合需求?** | {summ.get('artifacts','?')} 件产出 · {summ.get('blockers','?')} 条阻塞 (高危 {summ.get('high_blockers','?')}) · 未闭合需求 {nm.get('total',0)-nm.get('answered_count',0) if isinstance(nm.get('total'),int) else '?'} 条 · 冲突 {summ.get('conflicts','?')} |\n")
    L.append(f"| **issue 账?** | 共 {len(issues)} 条 · 已闭环 {len(issues)-len(open_i)} · 未闭环 {len(open_i)} (blocker {sum(1 for i in open_i if i.get('severity')=='blocker')} · high {sum(1 for i in open_i if i.get('severity')=='high')}) |\n")
    L.append(f"| **未闭环按责任方?** | " + " · ".join(f"{k} {v}" for k, v in by_own.most_common()) + " |\n")
    L.append(f"| **正在跑 (已开工, 别重复派)?** | **{len(inflight)}** 条 (见 §3) |\n")
    L.append(f"| **等你一句话的?** | **{len(boss)}** 条 (见 §4) |\n")
    L.append(f"| **健康度?** | {summ.get('health','?')} (外部阻塞未清) |\n")

    L.append("\n## 1. 从哪读起 (5 分钟)\n")
    L.append("| 顺序 | 文件 | 什么时候看 |\n|---|---|---|\n")
    L.append("| ① | **`docs/STATUS_SUMMARY.md`** | 一页看懂: 现状 / 闭环了什么 / 三个硬指标真状态 / 待办分桶 / 风险 Top3 |\n")
    L.append("| ② | **`docs/TODO.md`** | 接下来干什么 (A 内部可派 / B 等你拍板 / C 等外部 / D 依赖关系 / E 复现命令) |\n")
    L.append("| ③ | **`docs/PROJECT_STATUS.md`** | 8 节状态快照 (质量门 / 阶段门 / 就绪度 / 配置审计 / 决策账) |\n")
    L.append("| ④ | **`projects/smart_glasses/PROJECT_TRACKER.md`** | **唯一真源** (156KB, 有章节地图; 结论与理由都在这) |\n")
    L.append("| ⑤ | **`projects/smart_glasses/HW/ERC_DRC_CHECKLIST.md`** | 原理图投板前检查清单 (§A 机械 24 / §B 电气 16 / §C 布线 12 / §D 人工签字 3) |\n")

    L.append("\n## 2. 下一步 3 件事 (项目总工维护, 每次发布刷新)\n")
    for t, d in NEXT3:
        L.append(f"- {t}\n  {d}\n")

    L.append("\n## 3. 正在跑 (已开工, **别重复派**)\n")
    L.append("| id | 状态 | owner | 事项 | due |\n|---|---|---|---|---|\n")
    for i in inflight:
        L.append(f"| {i.get('id')} | {i.get('status')} | {i.get('owner')} | {str(i.get('title'))[:60]} | {i.get('due')} |\n")

    L.append("\n## 4. 等你拍板 (回一句就能解锁下游)\n")
    L.append("| id | 事项 | 我的建议默认值 |\n|---|---|---|\n")
    SUG = {"ISS-038": "OPC 一个人扛不住 ID/CMF → 建议外包/暂缓, **别开第 4 个 agent**",
           "ISS-040": "打印包已就绪 → **你那边切一次片 + 量 49 项**",
           "ISS-041": "同上, G3 判定依赖这些设备",
           "ISS-060": "① 电芯公差收紧 ±0.10 ② 非对称按厚度向 ③ 压垫槽背胶贴面",
           "ISS-063": "倾向 (a) 全幅压进 30° (角分辨率代价比原估小 ~1.7 倍)"}
    for i in boss:
        L.append(f"| {i.get('id')} | {str(i.get('title'))[:70]} | {SUG.get(i.get('id'),'—')} |\n")

    L.append("\n## 5. ★哪些数字/结论不能信 (最容易踩的坑)\n")
    for t in TRAPS:
        L.append(f"- {t}\n")

    L.append("\n## 6. 三个硬指标的真状态 (别被「达标」结论误导)\n")
    L.append("| 硬指标 | 目标 | 现状 | 杠杆在哪 |\n|---|---|---|---|\n")
    L.append("| 端到端延迟 | < 60ms | 口径未拍板 → 60fps 异步 67ms 超预算, 兜底 25.6fps 可 55.7ms | **Q1 口径** + Q17 显示帧率 |\n")
    L.append("| 皮肤侧温度 | ≤ 43°C | 满载 **78.6-88.6°C ❌** (镜腿内 80.1°C) | 只能**降功耗** (按需触发 + 待机 0.05W → 41.6-42.6°C); **挪到镜框 ≠ 安全** (鼻梁皮肤同样 43°C) |\n")
    L.append("| 续航 | ≥ 60min | 口径未拍板 → 持续满载 441mAh(形态崩) vs 按需 47-83mAh(形态 OK) | **Q4 续航口径** |\n")

    L.append("\n## 7. 复现命令 (全部可跑, 不需要额外环境)\n")
    L.append("```bash\ncd /home/yuewuya/.openclaw/workspace/projects/smart_glasses\n./status.sh                      # 一屏: 进展 / 待办(5桶) / 卡点 / 风险\n"
             "python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py && python3 state/daily_check.py\n"
             "python3 state/stage_gate.py      # 阶段门 (当前 G0, 差几项进 G1)\n"
             "python3 state/check_netlist.py   # 原理图 netlist 门禁 (12 条)\n"
             "bash state/publish_github.sh \"说明\"   # 同步 GitHub (真值反查脱敏 + SHA 校验)\n```\n")

    L.append("\n---\n\n")
    L.append("> **一句话**: 纸面阶段已做到滴水不漏, 但**实测数据 0/10 项** —— 真正的下一步是**打印包开打 + 原理图交叉评审 + 老板 5 条口径**。\n")

    open(args.out, "w", encoding="utf-8").write("".join(L))
    print(f"✅ 已生成 {args.out} (在飞 {len(inflight)} 条 / 等老板 {len(boss)} 条)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
