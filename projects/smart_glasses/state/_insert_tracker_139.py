#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 §(1.39) 插进 PROJECT_TRACKER.md (最新在最前, 插在 (1.38) 之前)。

★写文件铁律: 先整体读进内存再写 (禁止 open(p,'w').write(open(p).read()+x) 那种截断写法) +
  原子写 (tmp + fsync + os.replace)。幂等: 已存在 (1.39) 就退出。
"""
from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TRK = os.path.join(os.path.dirname(HERE), "PROJECT_TRACKER.md")
ANCHOR = "#### (1.38) ★★ 主控选型改令"

SECTION = """#### (1.39) ★★★ 断点恢复 + 批量验收: 5 条关单 / 4 条新登记 / 3 个翻案 (2026-10-29 09:0x)

> **背景**: 10-29 01:11 队列派活后 **token 耗尽把会话掐断** ⇒ 三个总工的交卷 (sw 的 RKNN 交接单 01:08 / hw 的 ISS-067 交接单 00:21 / mech 的 ISS-107 交接单 00:17 / hw 的 ISS-068 01:18 / mech 的 ISS-052 01:15) **全部没被验收、没关单**。本段是恢复后的亲核记录 —— **全部结论由我本轮亲自跑脚本复算, 不是抄回执**。

**★ 批量验收结果 (5 条 fixing/fixed → verified, verify_by=main)**:

| issue | owner | 我跑的复现命令 | 结果 |
|---|---|---|---|
| ISS-067 电源拓扑 R-F1 | hw-lead | `HW/calc_rf1_3v3v_uvp.py` | rc=0 · 三条路对比表逐条吻合 |
| ISS-107 PCB 定位 PIN-SET-2 | mech-lead | `MECH/pinset2_mech_check.py` + `state/merge.py` | rc=0 · 复算项 31 / FAIL 0 / WARN 3 · **冲突 0** |
| ISS-052 镜头窗口规格 | mech-lead | `MECH/camera_window_check.py` | rc=0 · **FAIL 0 / WARN 0** |
| ISS-068 绝对最大额定+降额 | hw-lead | `HW/calc_absmax_derating.py` | rc=0 · MTBF 表 + 结温边界表全部复现 |
| **ISS-110 RKNN 转换链实测 (新登记)** | sw-lead | `rknn_bench.py e2e` + `calib` + `acc` | rc=0 · 数字逐个吻合 (见下) |

**★ 翻案 1: RK3576 的 "资料充足" 从纸面变成实测 —— A 方案的前置闸门过了 (ISS-110)**
- **[实测]** RKNN INT8 转换 (target=rk3576) **零报错**, 产物 **10.09 MiB**, build 36.2s; **COCO val2017 F1: INT8 0.3139 vs FP32 0.3182 ⇒ 量化损失仅 −0.0043 (−1.4%)** (我复跑 N=300 得 F1 0.3129 / 0.3172 / −0.0044, 同口径同结论) ⇒ ★**"资料充足" 这条机械判据在 RKNN 维度是真的过了**。
- **[推算]** 端到端 ≤60ms: **模式 A PASS (54.98~56.99ms @ 24.8~26.1fps)** / **模式 B (异步 60fps) FAIL 67.01ms** ⇒ ★**切 RK3576 不会让延迟更糟** (与老板 10-25 已授权的兜底 55.7ms@25.6fps 一致), 但 **"60fps 显示" 在 RK3576+640×640 下达不成** ⇒ 要 60fps 只能换 yolov5n (NPU 8.87ms) 或降分辨率 (后者动 §0 锁死项)。
- **诚实边界**: **板端一次都没测** (adb 空) ⇒ S5 纯 NPU / 板端精度 / S10 光机延迟 三项 **[0数据]**; 投板后第一件事就是打 S5 (**≤20.33ms**)。
- ⚠️ **AGPL-3.0 许可阻断项在 RK3576 上原样存在** —— 换芯片不换许可 (ISS-087/101 未被本单消解)。

**★ 翻案 2: BQ25896 封装 —— 库内写的封装根本不存在 (ISS-068 R-F6 ⇒ ISS-112)**
- **[官方·我独立查证]** TI 官网产品页 + 订购页 + datasheet 封装附录三方一致: **BQ25896 只有 WQFN(RTW) 24pin 4×4mm = 16mm² 一种封装**, 在售型号全为 BQ25896RTWR/RTWT/RTWR.A/RTWR.B ⇒ 库内 "**VQFN-16 3×3mm (RGT)**" (CHARGE_BOARD_SPEC.md:486 / RELIABILITY_DESIGN.md:103,506) **不是型号写错, 是这个封装不存在**。
- 而库内**网表/原理图本来就是 24 脚** (SCHEMATIC_V1.md "全 24 脚对照" + U_CHG pin24 NC) ⇒ **文档与网表互相矛盾** + **占板面积少算 7mm²** (充电板面积本就紧张) ⇒ 已开 **ISS-112** (改文档 + 落 BOM OPN + 重算充电板面积 + 复核 24 脚 pinout)。
- 同单另两个热学硬约束: **R-F4** BQ25896 REC TA 只有 **-40~85°C** ⇒ 充电板环境 **>56.4°C 即 Tj 超标**, >41.9°C 已过 80% 占用率; **R-F5** TPS25730D REC TA **-40~45°C(@≤7A)/-40~65°C(@≤6A)** ⇒ 原表算出的 41% 占用率是错的, 真值 **76.6%**, TA>55°C 直接 FAIL。
- **降额判据升级 (本批最有价值的结构性产出)**: 一刀切 ×0.8/×0.85 → **L1 绝对最大红线 / L2 推荐工作区 / L3 系统占用率** 三层 + **J1 额定直比 / J2 降额 / J3 规范值** 三类 ⇒ 例: BQ25896 BAT/SYS 4.2V 按 J2 卡 = "超标 113.9%" 是误判, 按 J1 直比 = **91.1% ⚠️** (4.2V 是锂电满充规范值, 不是对充电 IC 的应力)。⚠️ **降额系数本身仍标 [推算]** (未逐条核对 IPC-9701 / GJB/Z 35A 原文) ⇒ **不可对外称"符合 IPC-9701"**。

**★ 翻案 3: 结构侧可以不等镜头定档就开模 (ISS-052)**
- **[推算]** 镜框上沿摄像头位前后厚度需求 **10.11mm(俯角25°)/10.26mm(28°)/10.41mm(32°)**, 落在 §1.4.5 的 10-12mm 带内余量 1.6-1.9mm; **俯角 20°→32° 只变 0.60mm** ⇒ 俯角收窄不吃厚度预算; 三档 (100/110/120°) 需求只差 **≤0.9mm**。
- ★**新硬约束 (MECH 原表没有)**: 垂直净高需求 **10.36mm(25°)/10.53mm(28°)** —— 比前后厚度还紧 ⇒ 是**外观代价**, 要老板/PM 认。
- ★**纠正 hw-lead 的口径错误**: "径向余量 2.5-4.5mm" 是把 10-12mm 当**直径**比净空 ⌀7.5 得来的, 但 §1.4.5 的 10-12mm 是**前后方向厚度**口径 ⇒ 按直径算单边余量只有 **1.25-2.25mm** (ISS-047 同源口径混用在结构侧的第二次出现)。
- 凸出 ≤2.5mm 从"临界"变"通过" (最坏 2.44mm→2.16mm, 余量 0.06→0.34mm); 前顶点凹进基准由 ≤1.5mm **收紧到 ≤1.0mm** (1.5mm 要吃掉 2.9° 视场)。

**★ 本批新登记的 4 条 issue**: ISS-110 (RKNN 实测, 已 verified) · **ISS-111** (EVT 可靠性实测项清单 —— ISS-068 的 (b) 部分引用的 `HW/EVT_RELIABILITY_TEST_ITEMS.md` **文件不存在**, 拆出来单独补交, owner=hw-lead) · **ISS-112** (BQ25896 footprint + 充电板面积重算, owner=hw-lead) · **ISS-113** (RKNN_BENCH §7 的 B6 复现缺陷: `acc` 步依赖 calib 步的 dataset.txt, 干净机器上直接跑会 AssertionError 崩掉 —— 我第一次就踩了, owner=sw-lead)。

**⚠️ 运维事实 (必须记)**: 10-29 **01:19 → 09:00 三个 cron 全停 7.8 小时** (队列派活 / GitHub 同步 / 每日巡检都没跑), 期间三个总工的活全部落盘但无人验收; 且队列派活 cron 的 WeChat 投递**连续失败 15 次** (`OutboundDeliveryError: sendMessage ret=-2 errmsg=prepare failed`) ⇒ **job 本身在跑, 但老板收不到报告**。

"""


def main() -> int:
    dry = "--dry-run" in sys.argv
    with open(TRK, encoding="utf-8") as f:
        text = f.read()

    if "#### (1.39)" in text:
        print("§(1.39) 已存在, 不重复插入")
        return 0
    if ANCHOR not in text:
        print(f"❌ 锚点未找到: {ANCHOR!r}")
        return 2

    idx = text.index(ANCHOR)
    new_text = text[:idx] + SECTION + text[idx:]

    if dry:
        print(f"[dry-run] 将插入 {len(SECTION)} B, 文件 {len(text)} → {len(new_text)} B")
        return 0

    fd, tmp = tempfile.mkstemp(prefix="PROJECT_TRACKER.md.", suffix=".tmp", dir=os.path.dirname(TRK))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, TRK)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    print(f"✅ §(1.39) 已插入 ({len(text)} → {len(new_text)} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
