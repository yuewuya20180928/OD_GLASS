#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""写 HEARTBEAT.md (新条目插到最前) + 追加 memory/2026-10-29.md (只追加, 绝不覆盖)。

★写文件铁律: 先整体读进内存再写 + 原子写 (tmp + fsync + os.replace)。
  ⚠️ 绝不写 open(p,'w').write(open(p).read()+x) 那种会截断的写法 (10-27 踩过, 差点清零 3 个文件)。
"""
from __future__ import annotations

import os
import sys
import tempfile

WS = "/home/yuewuya/.openclaw/workspace"
HB = os.path.join(WS, "HEARTBEAT.md")
MEM = os.path.join(WS, "memory", "2026-10-29.md")

HB_ENTRY = """# 2026-10-29 09:05-09:25 GMT+8 — 断点恢复: 批量验收 5 条 + 3 个翻案 + 4 条新登记 + 2 个运维坑

**唯一跟踪表**: `PROJECT_TRACKER.md` §(1.39) · **状态源**: `STATE.yaml` (09:12 刷新)

**发生了什么**: 昨晚 01:11 派完活 **token 耗尽把会话掐断** ⇒ 三个总工的交卷全部躺在盘上没人验收。
09:02 老板说"token已恢复, 继续分析之前的任务" ⇒ 我按项目总工的规矩 **亲自跑复现脚本, 不抄回执**。

**★ 批量验收 (5 条 fixing/fixed → verified, verify_by=main)**:
| issue | owner | 我跑的复现命令 | 结果 |
|---|---|---|---|
| ISS-067 电源拓扑 R-F1 | hw-lead | `HW/calc_rf1_3v3v_uvp.py` | rc=0 ✅ 三条路对比表吻合 |
| ISS-107 PCB 定位 PIN-SET-2 | mech-lead | `MECH/pinset2_mech_check.py` + `merge.py` | rc=0 ✅ 31项/FAIL 0 · **冲突 0** |
| ISS-052 镜头窗口规格 | mech-lead | `MECH/camera_window_check.py` | rc=0 ✅ **FAIL 0 / WARN 0** |
| ISS-068 绝对最大额定+降额 | hw-lead | `HW/calc_absmax_derating.py` | rc=0 ✅ MTBF+结温表全复现 |
| **ISS-110 RKNN 转换链实测 (新登记)** | sw-lead | `rknn_bench.py e2e` + `calib` + `acc` | rc=0 ✅ 数字逐个吻合 |

**★ 翻案 1 — RK3576 的"资料充足"从纸面变实测 (ISS-110)**: 转换零报错 / 产物 10.09MiB / **COCO F1 INT8 0.3139 vs FP32 0.3182 ⇒ 量化损失仅 −1.4%** (我复跑同结论) ⇒ **A 方案的前置闸门过了**。★**"切 RK3576 不会更糟"** (模式A 55~57ms@25fps, 与老板已授权的兜底一致), 但 **60fps 显示达不成 (67.0ms)** ⇒ 要 60fps 只能换 yolov5n 或降分辨率 (后者动 §0 锁死项)。**板端一次没测** ⇒ S5/板端精度/S10 三项 [0数据]。⚠️ **AGPL 许可阻断项原样存在**。

**★ 翻案 2 — BQ25896 封装写错了, 而且错得更离谱 (ISS-068 R-F6 ⇒ ISS-112)**: 我独立查 TI 官网三方确认 ⇒ **BQ25896 只有 WQFN(RTW) 24pin 4×4mm=16mm² 一种封装**, 在售型号全为 RTWR/RTWT/RTWR.A/RTWR.B ⇒ 库内 "**VQFN-16 3×3mm (RGT)**" **这个封装根本不存在**; 而库内网表本来就是 24 脚 ⇒ **文档与网表互相矛盾 + 占板面积少算 7mm²**。同单另两条热学硬约束: **R-F4** BQ25896 REC TA 只到 85°C (充电板环境 >56.4°C 即 Tj 超标) · **R-F5** TPS25730D 真值占用率 76.6% 不是 41%。**降额判据升级成 L1/L2/L3 三层 + J1/J2/J3 三类** (BQ25896 4.2V 按 J1 直比 = 91.1% 不是"超标 113.9%")。

**★ 翻案 3 — 结构侧可以不等镜头定档就开模 (ISS-052)**: 前后厚度 10.11/10.26/10.41mm (俯角 25/28/32°) 落在 10-12mm 带内, **俯角 20°→32° 只变 0.60mm**; ★**新硬约束**: 垂直净高 10.36/10.53mm 比前后厚度还紧 = **外观代价, 要老板/PM 认**; ★**纠正 hw-lead 口径**: "径向余量 2.5-4.5mm" 是把 10-12mm 当**直径**比出来的, 按厚度口径单边只有 **1.25-2.25mm**。

**★ 新登记 4 条**: ISS-110 (RKNN 实测, 已 verified) · ISS-111 (EVT 实测项清单 —— ISS-068 引用的文件**不存在**) · ISS-112 (BQ25896 footprint + 充电板面积重算) · ISS-113 (RKNN_BENCH §7 的 `acc` 步单独跑会崩 —— **我亲自踩了**)。

**⚠️ 两个运维坑 (都记进 AGENTS.md 了)**:
1. **01:19→09:00 三个 cron 停 7.8 小时** (队列派活/GitHub 同步/每日巡检都没跑) ⇒ 期间交卷无人验收 ⇒ **token 配额是根因 (子 agent 默认 M3 挂在 token plan 上限)** ⇒ ★**派活必须显式钉 `minimax/MiniMax-M3.1-Flash`**。
2. **微信推送连挂 15+ 次**: `sendMessage ret=-2 errmsg=prepare failed` ⇒ 根因 = **context token 停在 7-21 没刷新** ⇒ ★**老板在微信上给机器人发一句话即可恢复** (job 本身一直正常跑, 只是收不到报告)。

**🔴 等老板**: ① **微信发一句话恢复推送** ② **RK3576 核心板买不买** (唯一能把功耗从推算变实测的路, 决定 A 方案生死) ③ 4 封非酷芯微草稿放行 + 打印包开打 + 测试设备预算 (逾期) ④ **充电板垂直净高 10.36mm 的外观代价要不要认**

"""

MEM_ENTRY = """
---

## 2026-10-29 09:02-09:25 — 断点恢复 + 批量验收 (项目总工)

### 背景
昨晚 01:11 队列派完 ISS-068/ISS-052, 之后 **token 耗尽把会话掐断** ⇒ 三个总工的交卷全在盘上没人验收。
09:02 老板说"token已恢复, 继续分析之前的任务" ⇒ 我做的是**验收**, 不是继续往下堆活。

### 我做了什么 (全部亲自跑复现脚本, 不抄回执)
| issue | 复现命令 | 结果 |
|---|---|---|
| ISS-067 | `python3 HW/calc_rf1_3v3v_uvp.py` | rc=0, §5/§6 表逐条吻合 |
| ISS-107 | `python3 MECH/pinset2_mech_check.py` + `state/merge.py` | rc=0, 31项/FAIL 0/WARN 3, 冲突 0 |
| ISS-052 | `python3 MECH/camera_window_check.py` | rc=0, FAIL 0 / WARN 0 |
| ISS-068 | `python3 HW/calc_absmax_derating.py` | rc=0, MTBF + 结温边界表全复现 |
| ISS-110 (新) | `rknn_bench.py e2e` + `calib` + `acc --images 300` | rc=0, 台阶表/三个档位/F1 全部吻合 |

⇒ **5 条 fixing/fixed → verified (verify_by=main)**, 另新登记 **ISS-110/111/112/113**。
⇒ 门禁: merge rc=0 (冲突 0) · gate_check rc=0 · issue_check rc=0 · daily_check rc=0 (无漂移) · stage_gate rc=1 (G1 还差 8 项, 正常)。

### ★ 三个翻案
1. **RK3576 "资料充足" 从纸面变实测** (ISS-110): RKNN 转换零报错 / 产物 10.09MiB / **COCO F1 INT8 0.3139 vs FP32 0.3182 = 量化损失仅 −1.4%** ⇒ **A 方案前置闸门过了**。★"切 RK3576 不会更糟" (模式A 55~57ms@25fps); ★但 **60fps 达不成 (67.0ms)**。**板端一次没测** ⇒ S5 [0数据]。
2. **BQ25896 封装不存在** (R-F6): 我独立查 TI 官网三方 ⇒ **只有 WQFN RTW 24pin 4×4mm**, 在售型号全 RTWR/RTWT/RTWR.A/RTWR.B ⇒ 库内 "VQFN-16 3×3mm" **不是型号写错, 是这个封装不存在**; 而库内网表本来就是 24 脚 ⇒ 文档与网表矛盾 + 面积少算 7mm² ⇒ 开 ISS-112。
3. **结构侧可以不等镜头定档开模** (ISS-052): 厚度 10.11/10.26/10.41mm, 俯角 20°→32° 只变 0.60mm; 新硬约束 = **垂直净高 10.36/10.53mm** (外观代价); 纠正 hw-lead "径向余量 2.5-4.5mm" 口径错误 (单边只有 1.25-2.25mm)。

### ★ 两个新坑 (已写进 AGENTS.md)
1. **手动派活与队列 cron 会撞车**: 09:11-09:12 我手动派 ISS-112/113, 同一分钟队列 cron 也派了同一批 ⇒ **hw-lead/sw-lead 各开 2 个写会话** (AGENTS.md 那条"两个写会话互相覆盖"的老铁律) ⇒ 我 kill 了自己那两条, 保 cron 的 (M3.1-Flash), 并把被 kill 的 brief 增量**写回 issue_log 的 task_brief** (`state/_patch_briefs_20261029.py`) 供下一轮队列派活用。
2. **子 agent 默认模型 MiniMax-M3 会挂 token plan 上限** (cron 查出来的) ⇒ ★**派活必须显式钉 `minimax/MiniMax-M3.1-Flash`**; 我手动派的两条正是用了默认 M3, 日志里看到 `LLM request timed out` + AbortError。

### 运维
- **微信推送连挂 15+ 次** `sendMessage ret=-2 errmsg=prepare failed` ⇒ 根因 **context token 停在 2026-07-21 没刷新** ⇒ **老板在微信给机器人发一句话即可恢复**; job 本身一直正常跑, 只是收不到报告。
- **GitHub 推送**: 01:19→09:00 三个 cron 全停 7.8h, 09:00 那次还超时 (600s) ⇒ 09:18 手动重跑 `publish_github.sh`, 生成阶段全过, 卡在 git fetch。
"""


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main() -> int:
    dry = "--dry-run" in sys.argv
    before = {}

    # ── HEARTBEAT: 新条目插最前 ──
    with open(HB, encoding="utf-8") as f:
        hb = f.read()
    before["HEARTBEAT.md"] = len(hb)
    if "断点恢复: 批量验收 5 条" in hb:
        print("[skip] HEARTBEAT 已含本轮条目")
    else:
        hb = HB_ENTRY + hb
        if not dry:
            atomic_write(HB, hb)
        print(f"[ok] HEARTBEAT.md {before['HEARTBEAT.md']} → {len(hb)} B (新条目插最前)")

    # ── memory: 只追加 ──
    with open(MEM, encoding="utf-8") as f:
        mem = f.read()
    before["memory"] = len(mem)
    if "断点恢复 + 批量验收 (项目总工)" in mem:
        print("[skip] memory 已含本轮记录")
    else:
        mem = mem.rstrip("\n") + "\n" + MEM_ENTRY
        if not dry:
            atomic_write(MEM, mem)
        print(f"[ok] memory/2026-10-29.md {before['memory']} → {len(mem)} B (只追加)")

    if dry:
        print("[dry-run] 未落盘")
    return 0


if __name__ == "__main__":
    sys.exit(main())
