#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-240 交卷单追加: 2026-11-17 04:5x 续做复核 (交付物复验 + 受保护基线漂移登记)
只加不删 · 原子写 (tmp + os.replace) · 先备份
"""
import os, shutil, sys, time

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
REL = "HANDOFF/2026-11-16_mech-lead_ISS240_跨铰链FPC几何三口径收口.md"
p = os.path.join(PROJ, REL)

MARK = "## 附2: 本轮 (2026-11-17 04:5x) 续做复核"

BLOCK = r"""
## 附2: 本轮 (2026-11-17 04:5x) 续做复核 —— 交付物复验 + ★受保护基线漂移登记★

> ★**本节是续做复核 (gateway reload 后重跑一遍), 不是新交付** —— ★**五件交付物一个没重做, 一个字节没改** ★
> ★**唯一新增动作 = 把「受保护 11 个 md5」里 5 个漂移的事实登记进来 (不是我改的, 是交付之后上游并发会话改的) ★**

### 附2.1 五件交付物复验 (全在位; 门禁重跑全绿; rc 全 0)

| # | 交付物 | 复验方式 | 结果 |
|---|---|---|---|
| 1 | `MECH/HINGE_FPC_GEOMETRY_TRUTH.md` | 4 张表齐 (T1 §2 / T2 §3 / T3 §4 / T4 §5) + 机器块 §6 + §2.2 旧口径留痕表 | ✅ 在位 (mtime 2026-11-16 13:09:34) |
| 2 | `MECH/USB_HINGE_STRUCTURE.md` | ★**行数 512 = 标注前后同值** (只加不删) + 作废标注 **54** 处 + 现行口径行 **L94** (31p/0.3mm + 22p/0.5mm) + demo 口径行 **L121** (5.00 / 3.35 ⇒ 余 33.00 / 2.05) | ✅ 只加不删 |
| 3 | `MECH/check_hinge_fpc_truth.py` | 本轮实跑 9/9 PASS + `--selftest` 10/10 全抓到 | ✅ rc=0 (mtime 2026-11-16 12:57:34) |
| 4 | `HANDOFF/2026-11-16_mech-lead_ISS240_跨铰链FPC几何三口径收口.md` | 本文件 | ✅ |
| 5 | `state/fragments/mech.yaml` | 2 条新 claim 在位 (`mech_hinge_stack_truth_mm` = 25.30 / `mech_hinge_stack_demo_mm` = 5.00) + ★**旧 claim 一个字没改** ★ | ✅ |

★**门禁重跑 (本轮 2026-11-17 04:5x 实跑, 原样结论) ★**

| 命令 | 结果 | rc |
|---|---|---|
| `python3 MECH/check_hinge_fpc_truth.py` | ★**9/9 PASS · FAIL 0** ★ | **0** |
| `python3 MECH/check_hinge_fpc_truth.py --selftest` | ★**10/10 全抓到 (每条自证)** ★ | **0** |
| `python3 MECH/hinge_usb_check.py` | FAIL 0 (★**没碰它, 只是证明没碰坏它** ★) | **0** |
| `python3 MECH/check_demo_struct_truth.py` | ★**23/23** (★阈值一个没放松★) | **0** |
| `python3 state/merge.py` | STATE.yaml 已刷新 | **0** |
| `python3 state/gate_check.py` | 通过 | **0** |

★**新门禁重算的网表事实 (与本单交付时逐位一致 ⇒ 4 小时里网表实质没变) ★**

```
网表 board 分布 = {'CHG_BOARD': 94, 'HINGE': 15, 'MAIN_PCB': 404}
FPC 座 CONN_CAM   = 31p @ 0.3 mm  board=MAIN_PCB  (网表行 L290…) 逐脚行数=31
FPC 座 CONN_LIGHT = 22p @ 0.5 mm  board=MAIN_PCB  (网表行 L237…) 逐脚行数=22
FPC 座 J_CHG      = 10p @ 0.5 mm  board=HINGE     (网表行 L38…)  逐脚行数=10
```

### 附2.2 ★受保护 11 个 md5: 5 个漂了 —— ★不是我改的·是交付之后上游并发会话改的★

| 文件 | ISS-240 交付时基线 | 本轮实测 (11-17 04:5x) | 漂? | 文件 mtime | 谁动的 |
|---|---|---|---|---|---|
| `MECH/hinge_usb_check.py` | `3425bc14…` | `3425bc14…` | 否 | 11-12 03:32 | — |
| `MECH/hw_cross_review_check.py` | `e521387b…` | `e521387b…` | 否 | — | — |
| `MECH/display_biosafety_v2_check.py` | `29c77fc3…` | `29c77fc3…` | 否 | — | — |
| `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` | `96239070…` | `96239070…` | 否 | — | — |
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e…` | `611b869e…` | 否 | — | — |
| `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2b…` | `3e504d2b…` | 否 | — | — |
| `MECH/service_port_check.py` | `9b24bf98…` | ★**`db58ff6a…`** ★ | ★**漂** ★ | **11-17 02:35** | ★**别的会话 (ISS-264 检修口常量迁 30mm 套A)** ★ |
| `MECH/check_demo_struct_truth.py` | `fa9b59e5…` | ★**`4ae5827e…`** ★ | ★**漂** ★ | **11-17 02:33** | ★**别的会话 (ISS-264)** ★ |
| `HW/netlist_v1.csv` | `34132f7e…` | ★**`e06c1dd6…`** ★ | ★**漂** ★ | **11-16 22:25** | ★**hw-lead 重生成网表** ★ |
| `HW/netlist_v1_pins.csv` | `b21b743a…` | ★**`287e7861…`** ★ | ★**漂** ★ | **11-16 22:25** | 同上 |
| `HW/BOM_v1.csv` | `c195a117…` | ★**`94642d07…`** ★ | ★**漂** ★ | **11-16 22:25** | 同上 |

★**证据链**: 5 个漂了文件的 mtime **全部晚于** ISS-240 交付时刻 (交卷单 `13:08:59` · 收口页 `13:09:34` · 正文 `12:59:15` · 新门禁 `12:57:34`) ⇒ ★**不是本单改的** ★
★**本单四个交付文件的 mtime 全部落在 2026-11-16 12:57~13:09 窗口内, 此后一个字节没动** ★

★**后果 = 零 (三条) ★**

1. ★**新门禁不受影响** —— 它**现场解析**网表 (★**不 pin 网表 md5** ★) ⇒ 漂了之后重跑仍 **9/9 PASS rc=0** ✓ (本轮实跑)
2. ★**G9 仍绿** —— G9 只 pin **受保护脚本** `MECH/hinge_usb_check.py` 的 md5, 而该脚本本身**没被改** (`3425bc14…` 一字未变) ⇒ ★**G9 的设计意图 (脚本被改 ⇒ legacy 口径要重核) 没被误触发** ✓
3. ★**G7 的假绿依旧存在** —— 本轮实读 `MECH/check_demo_struct_truth.py` L589~L600:
   `g("G7", "分片 claim mech_hinge_stack_fixed_mm = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)", fixed == "25.00", …)`
   ⇒ ★**判据文字一字未动 ⇒ U-1 仍开着, 仍需 main 裁 (本单一个字没代拍) ★**

### 附2.3 ★一条值得记的坑 (★并发会话会改本域受保护面 ⇒ 门禁不能 pin 网表 md5★) ★

★**坑**: 新门禁若 pin 住网表 md5, 上游一改网表就红 (★假红, 且不是自己改坏的★) ⇒ 本单的门禁**只 pin 受保护脚本 md5 (G9), 网表一律现场解析** ⇒ ★**这是设计选择, 不是偷懒** ★
★**复核**: 本轮网表 md5 已从 `34132f7e…` 漂到 `e06c1dd6…`, ★**新门禁照样 9/9 绿** ⇒ ★**这个选择被现实验证有效** ★

### 附2.4 ★架构裁定复核 (★本轮重新实读 PROJECT_TRACKER.md §0 锁死表, 4 小时后仍成立★) ★

| 锁死表行 | 内容 (本轮实读) | 出处 |
|---|---|---|
| **第 43 行** (文件 L74) | ★**优先级: 硬件 > 软件, 结构不考虑** ★ —— 2026-11-02 19:25 老板指示①: ★**结构问题直接不考虑** ★ ⇒ ★**本单属【结构侧判据/文档口径】, 不做新结构设计, 不出结构方案** ★ | `PROJECT_TRACKER.md` §0 锁死表 #43 |
| **第 44 行** (文件 L75) | ★**demo 硬件形态 (已定, 不是待拍板)** ★ —— 2026-11-02 19:25 老板指示②: 主板 = 一块板; sensor/屏幕各画成模组; FPC 软排短距连到主板 ⇒ ★**跨铰链取消** ★ ⇒ 连带: CONN_CAM/CONN_LIGHT 跨铰链属性要去掉, 充电板 J_CHG 要并进主板或 demo 直接 USB 供电 ⇒ 落 ISS-149 | `PROJECT_TRACKER.md` §0 锁死表 #44 |

★**⇒ 收口页 §0 的核心结论 4 小时后仍然成立: 25.00 与 31.50 都不是 demo 板的现行值; demo 板现行口径 = J_CHG 单链 (高度 5.00 / 径向 3.35 ⇒ 余 33.00 / 2.05)** ★
★**⇒ 网表 board 栏实测仍 = MAIN_PCB 404 / CHG_BOARD 94 / HINGE 15, board==HINGE 的座只有 J_CHG** ★

★**本轮零新增动作清单**: 未改任何受保护脚本 / 判据阈值 / 网表 / 脚表 / BOM / 板 · 未写 issue_log · 未写别人的分片 · 未外发任何消息 · 未代拍 U-1~U-4 ★
"""


def main():
    with open(p, "r", encoding="utf-8") as f:
        cur = f.read()
    if MARK in cur:
        print("SKIP: 附2 段已存在, 不重复追加")
        return 0
    bak = p + ".bak_" + time.strftime("%Y%m%d_%H%M%S") + "_r2"
    shutil.copy2(p, bak)
    tmp = p + ".tmp_r2"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(cur.rstrip("\n") + "\n" + BLOCK.lstrip("\n"))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)
    print("OK: 已原子追加 附2 段")
    print("备份:", os.path.relpath(bak, PROJ))
    print("新行数:", sum(1 for _ in open(p, encoding="utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
