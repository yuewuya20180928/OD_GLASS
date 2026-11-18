#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/_append_decision_page_20261117_0855_r51.py

★main 2026-11-17 08:5x (cron 775d9893 继续执行后继计划)★ ⇒ ★**追加式**更新老板待拍板清单★
★**只加一节 §A-补13 · 老字一行不删** ★

★**为什么这一节**: ★本轮 main 把 ISS-279 (SW 侧腿) 与 ISS-280 (提交时序守卫) 独立复验后落 verified ★
⇒ ★**「板只改一次」那一趟的三条腿 (HW=ISS-277 / MECH=ISS-278 / SW=ISS-279) 齐了 + 改板次数从「靠人记着」变成「机器判 ≤1 次」** ★
⇒ ★**⇒ 老板那 4 条待拍 (P8/P9/P10/P11) 从「还缺前置」变成「唯一剩余卡点」★** ⇒ ★**这是决策状态的变化, 页面必须跟上** ★
★**纪律**: ★**本节不新增任何待拍项** ★ ⇒ ★**main 不代拍** ★
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
BAK = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md.bak_20261117_0855_r51")

NEW_SECTION = r"""

---

## §A-补13 · ★★r51 · 2026-11-17 08:5x · ★★★**「板只改一次」前置收口 ⇒ 你的那 4 条现在是唯一卡点**★★★ (★main 08:4x~08:5x 本机实跑复验★)

> ★**本节起因**: ★本轮 main 独立复验后把 **ISS-279 (SW 侧板侧输入)** 与 **ISS-280 (提交时序守卫)** 落 `verified` ★
> ⇒ ★**「板只改一次」那一趟 (S1~S13) 的三条腿现已齐**: HW 侧 = ISS-277 (已 verified) · MECH 侧 = ISS-278 (在飞, 08:4x 时仍在跑) · SW 侧 = ISS-279 (★本轮 verified★) ★
> ⇒ ★**外加一道【提交时序守卫】** (ISS-280, 本轮 verified) ⇒ ★**改板次数从「靠人记着」变成「机器判 ≤1 次」** ★
> ★**纪律**: ★**本节 0 条新增待拍** ⇒ ★**你的清单还是 P8 / P9 / P10 / P11 那 4 条 + 原页的 A1/A2/A3, 一个字没多** ★

### ★① 本轮两单已收口 (★main 本机实跑, 不抄交卷报告★)

| 单号 | owner | 状态 | main 本机复验 (★自己实跑★) |
|---|---|---|---|
| ★**ISS-279** (SW 侧板侧输入收口 + 闸) | sw-lead | ★**fixing → verified** ★ | ★`SW/tools/check_onepass_sw_sync.py` rc=0 (W1~W6 全 OK: 条目 8 条/9 字段齐 · 归属步 S2=1 S4=1 S8=1 S9=2 S10=3 · 判据脚本全在盘 · ①~⑧ 八条一条不缺 · **8 个现状探针与盘面一致** · 受保护 5 件 md5 不变) · ★`--selftest` rc=0 (**反向 9/9 全抓到**) ★ · ★**受保护 5 件 md5 = main 亲自跑 md5sum 逐字节核对 5/5 相同** ★ |
| ★**ISS-280** (提交时序守卫) | hw-lead | ★**fixing → verified** ★ | ★`HW/check_onepass_commit_order.py` rc=0 (D0/D1/D2/D3/D4/D4b/D5/D6 全 PASS: **变更区 0 行 = 板至今没变过** · D4 盘上板 md5 == 台账基线 · D4b `.kicad_pro` == 台账登记值) · ★`--selftest` rc=0 (**反向 11/11 全抓到**, 要求 ≥6) ★ · ★**板 mtime 仍 `2026-11-06 07:07:17` + md5 `611b869e…` 双重未变** ★ |

> ★**★受保护 5 件 md5 (★main 08:5x 亲自 md5sum, 5/5 逐字节相同★)★**:
> 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro 3e504d2be83152e337949723e909be1b` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607`
> ⇒ ★**⇒ 板没被碰过 (零写板) ⇒ G1 仍红 ⇒ 不许投板** ★

### ★② 「板只改一次」现在的真实状态 (★为什么这 4 条变成了唯一卡点★)

| | 现状 |
|---|---|
| ★**改板次数** ★ | ★**从「靠人记着」变成「机器判 ≤1 次」** ★ ⇒ `HW/check_onepass_commit_order.py` D5 判「变更区 ≤1 行」· D6 判「改了必须留证绑定」· D3 判「旧集合断言必须被后文显式撤回」⇒ ★**顺序错了当场红, 不用等人想起来** ★ |
| ★**板侧项有没有漏** ★ | ★**ISS-277 已 verified** (31 条板侧项 / 9 字段 / 覆盖度闸 P1~P6 rc=0 + 反向 8/8) ⇒ ★**漏项当场红, 不是漏到板改完才发现** ★ |
| ★**SW 侧会不会当场必红** ★ | ★**ISS-279 已 verified** ⇒ SW 侧板侧输入 8 条清单 + W1~W6 闸 + 反向 9/9 ⇒ ★**板改完那一刻 SW 侧不再是「必红且无路可走」** ★ |
| ★**MECH 侧** ★ | ★**ISS-278 在飞** (08:4x 实测会话仍在跑) ⇒ ★**交卷后我再复验, 齐了再说** ★ |
| ★**★你的那 4 条 (P8/P9/P10/P11)★** ★ | ★**★现在 = 唯一剩余卡点★** ★ ⇒ ★**拍完这 4 条 ⇒ A 类步 (S1/S2/S3/S4/S6/S7/S8) 同趟做完 → 板 md5 变一次 → B 类步 (S9/S10/S11/S12/S13) 最后跑一次** ★ ⇒ ★**正确时序已由 ISS-280 写进权威页 + 机器闸, 不靠人记** ★ |

### ★③ 本节 0 条新增待拍 (★不重复计数★)

| 本节 | 与原页的关系 |
|---|---|
| ★**① 两单收口** ★ | ★**是状态变化, 不是新决策** ★ ⇒ ★**P8 / P9 / P10 / P11 四条一条没动, 选项与代价一字未改 (★§A-补12 那节仍然有效★)** ★ |
| ★**② 状态表** ★ | ★**给你判断「还差多少」的背景, 不构成拍板项** ★ ⇒ ★**拍板码映射 (A1/A2/A3/V-2/V-3/V-4) 一律以 §A-补10 第 ① 条为准, 本节不重述也不改写** ★ |
| ★**`FSIN_OUT` 逃逸方向** ★ | ★**不上你的清单** ★ ⇒ ★**它是工程项不是决策项** (★作业包 §6.2 S8 行: 3.01 mm 布不通 · 疑似逃逸方向 bug ★ 归 hw + 路由器作者 ⇒ 找错方向白跑一轮路由★) ⇒ ★**由 main 自查, 查到需要老板拍架构再上页** ★ |

### ★★本轮 main 的内部推进 (★不进你的清单, 只给你看进度★) ★★

| 单号 | owner | 状态 | 说明 |
|---|---|---|---|
| ★**ISS-279** | sw-lead | ★**verified (本轮)** ★ | ★零写板 · 纯分析 + 作业包订正 + 机器闸类 ★ ⇒ ★**SW 侧那条腿齐了** ★ |
| ★**ISS-280** | hw-lead | ★**verified (本轮)** ★ | ★零写板 · 纯分析 + 作业包追加式订正 + 机器闸类 ★ ⇒ ★**「板只改一次」从此有机器闸守着** ★ |
| ★**ISS-278** | mech-lead | ★**在飞 (fixing)** ★ | ★会话实测仍在跑 (08:4x) ⇒ ★**MECH 侧那条腿未齐, 齐了我再报** ★ |

> ★**★本节数字出处 (★可复核★)★**:
> · ISS-279 ⇒ `HANDOFF/2026-11-17_sw-lead_ISS279_SW侧板侧输入收口.md` + `SW/BOARD_ONEPASS_SW_SYNC.md` + `SW/tools/check_onepass_sw_sync.py` (★main 08:4x~08:5x 实跑★)
> · ISS-280 ⇒ `HANDOFF/2026-11-17_hw-lead_ISS280_提交时序守卫.md` + `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` + `HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md` + `HW/check_onepass_commit_order.py` (★main 08:4x~08:5x 实跑★)
> · 板 md5 `611b869e…` + mtime `2026-11-06 07:07:17` ⇒ ★**板没被碰过** ★
"""


def main() -> int:
    with open(PAGE, encoding="utf-8") as f:
        txt = f.read()
    if "§A-补13" in txt:
        print("⚠ §A-补13 已在页上 ⇒ 不重复追加")
        return 0
    shutil.copy2(PAGE, BAK)
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(txt.rstrip("\n") + "\n" + NEW_SECTION)
    with open(PAGE, encoding="utf-8") as f:
        after = f.read()
    print("  追加前字节 = %d ⇒ 追加后字节 = %d" % (len(txt.encode("utf-8")), len(after.encode("utf-8"))))
    print("  §A-补13 在位 =", "§A-补13" in after)
    print("  老字未删 (原页头仍在) =", after.startswith(txt[:200].strip()[:80]))
    print("  BAK =", os.path.basename(BAK))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
