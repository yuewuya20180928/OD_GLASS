#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_2215_open260.py
★main (moli) 开单 ISS-260 · 2026-11-16 22:15 (cron fb67af40 队列自动派活)★

★★**为什么开这一单 (★队列断线补位 + 一条实测到的真缺陷★)** ★★
· ★**队列侧**: `python3 state/advance.py --json` ⇒ `internal[]` = **0 条** ⇒ ★**三个总工名下已无 status=open 的单**
  ⇒ ★**hw-lead 名额是空的 (★ISS-257 21:35 交卷后已 verified★) · sw-lead 在跑 ISS-258 · mech-lead 在跑 ISS-259**
  ⇒ ★**队列名义断线 ⇒ 按本项目既有做法 main 自己开主线内的单补位** ★
· ★**缺陷侧 (★main 21:5x 本机实跑, 不是推测★)**: `python3 state/land_v_values.py --decision V-2=1` ⇒ **rc=3**
  ⇒ 「补丁对不上: state/gen_netlist.py · V2-1 USB ESD 段 ⇒ 旧值出现 0 次 (期望 1 次)」
  ⇒ ★**根因 = ISS-257 (21:22 落表) 把 `state/gen_netlist.py` 的 `D_ESD_USB_D` 那两行从 `[待选型]` 改成了真型号
  (`TPD1E05U06DPYR`), 而落表器 `state/land_v_values.py` 的 `V2_ESD_OLD` 仍硬编码着【改前】旧串** ★
  ⇒ ★**V-3 / V-4 干跑仍 rc=0 (实测) ⇒ 不是工具整体坏, 是 V-2 这一条漂了** ★
  ⇒ ★**后果 = 决策页 §A 承诺的「A1+A2+A3 一并拍 ⇒ 一条命令 ⇒ 15 条一次落」, 现在 A3 那一格当场 rc=3 失败** ★
· ★★**更深一层 (★本单真正的难点★)**: ★**光把锚点改回去【是错的】** ★
  ⇒ ★**V-2 配方把 ESD 架构写死成「3 脚双通道」, 但 ISS-241 矩阵硬发现① 说 ESD 4 件全是 2 焊盘占位 ⇒ 双通道 3 脚件物理落不下
  ⇒ 且 ISS-257 已按矩阵推荐把 `D_ESD_USB_D` 落成 2 脚单通道真型号** ★
  ⇒ ★**⇒ 锚点一改, 老板拍 A3=① 就会把 ISS-257 刚落下的真采购型号覆盖成判据串 ⇒ G1a-7 刚转绿的东西被自己 undo 掉** ★

★★**边界**: 本单 = 内部活 · 原理图/网表/选型侧 · 不是 PCB 布线/布局类 · 不许落任何 V 值 · 零外发 · 不许代拍 A3/W-1
"""
import os
import shutil
import datetime as dt
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-260_hw_land_v_values_v2_anchor_drift.md")


def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log["issues"]
    by_id = {i.get("id"): i for i in issues}
    assert "ISS-260" not in by_id, "ISS-260 已存在"

    with open(BRIEF, "r", encoding="utf-8") as f:
        brief = f.read()

    issues.append({
        "id": "ISS-260",
        "title": ("★★[主线内·原理图/网表/选型侧·工具自测·内部活] ★★"
                  "★**`state/land_v_values.py` 的 V-2 落表路径在 ISS-257 落表后已失效** ★★"
                  "(★`--decision V-2=1` ⇒ **rc=3**「旧值出现 0 次 (期望 1 次)」⇒ 决策页承诺的"
                  "「A1+A2+A3 一并拍 ⇒ 一条命令 ⇒ 15 条一次落」**A3 那格当场失败**★) "
                  "★ + ★★**补 `--selftest` (★本项目所有闸都有, 只有落表器没有 ⇒ 上游落表把锚点打漂这类漂移"
                  "没有任何机器会主动报★)★ + ★★**出 A3/W-1 语义冲突的选项表 (★「光把锚点改回去」是错的:"
                  "会把 ISS-257 刚落下的真型号覆盖成判据串 ⇒ G1a-7 刚转绿被自己 undo★)★**"),
        "severity": "high",
        "source_blocker": "ISS-257",
        "desc": ("★**main 2026-11-16 21:5x 本机实跑 (★不是抄交卷报告★)**:\n"
                 "· `python3 state/land_v_values.py --decision V-2=1` ⇒ **rc=3** ⇒ 「补丁对不上: "
                 "state/gen_netlist.py · V2-1 USB ESD 段 ⇒ 旧值出现 0 次 (期望 1 次)」\n"
                 "· ★**同一条命令的其它取值仍过 (⇒ 不是工具整体坏, 是 V-2 这一条漂了)** ★: "
                 "`--decision V-3=E` rc=0 · `--decision V-4=680` rc=0 · `--decision V-2=2` rc=2 (打回) · "
                 "`--decision V-3=E --apply` rc=2 (缺 --boss-decision 拒绝执行)\n"
                 "· ★**根因 = 锚点硬编码的旧串已被上游落表作废** ★: 落表器 `state/land_v_values.py` 的 `V2_ESD_OLD` "
                 "写的是 ISS-257 之前那串 `\"ESD 阵列 [待选型] (USB 2.0 双通道)\"` / `\"ESD 阵列 [待选型]\"`, "
                 "而 ISS-257 (21:22 落表, 已 verified) 已把 `state/gen_netlist.py` L1454-L1459 改成真型号 "
                 "`TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)` + evidence `[官方]` "
                 "⇒ ★**main 实测旧串在当前 `state/gen_netlist.py` 里出现 0 次** ★\n"
                 "· ★**后果**: 决策页 `DECISION_PENDING_2026-11-16.md` §A 承诺「A1+A2+A3 一并拍 ⇒ 一条命令 ⇒ 15 条一次落」"
                 "⇒ ★**现在老板拍完 A3, 那条命令当场 rc=3 失败 ⇒ A3 = V-2 这一格【当前不可兑现】** ★\n"
                 "· ★★**更深一层 (★本单真正的难点★)**: 光把锚点改回去【是错的】 ★\n"
                 "  ① ★**ISS-241 矩阵硬发现①**: ESD 4 件全是 2 焊盘占位 ⇒ 双通道 3 脚件 (`TPD2E2U06` DCK/SC70-3=3脚 / "
                 "DRL/SOT-5=5脚) 物理落不下 ⇒ 只能选 2 脚单通道器件 ★\n"
                 "  ② ★**ISS-257 已按这条把 `D_ESD_USB_D` 落成 2 脚单通道真型号** (= 矩阵 ③ 的推荐项) ★\n"
                 "  ③ ★**而 V-2 配方把架构写死成「3 脚双通道」** ⇒ ★**⇒ 锚点一改, 老板拍 A3=① 就会把 ISS-257 刚落的"
                 "真采购型号覆盖成判据串 ⇒ G1a-7 刚转绿被自己 undo 掉 ⇒ 与 ISS-257 的交付目标直接相反** ★\n"
                 "· ★**本单 = 内部活 · 零外发 · 不许落任何 V 值 · 不许代拍 A3/W-1** ★"),
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": ("2026-11-16 22:15 (cron fb67af40 队列自动派活) 新开 ★**依据 = main 本轮自己实跑落表器"
                 "(`--decision V-2=1` rc=3) + 自己逐字读 `state/land_v_values.py` 的 `V2_ESD_OLD` vs "
                 "`state/gen_netlist.py` L1454-L1459 + 自己读 ISS-241 矩阵硬发现① + 读 ISS-257 交卷单★** ★\n"
                 "★**队列侧**: `advance.py --json` ⇒ `internal[]` = 0 条 (★三个总工名下已无 open 单★) ⇒ "
                 "hw-lead 名额空着 (ISS-257 21:35 交卷后 verified) ⇒ ★**按本项目既有做法 main 自己开主线内的单补位** ★\n"
                 "★**边界**: 只改 `state/land_v_values.py` (★不许推倒重来: V-3/V-4 两套配方已自证过★) · "
                 "不许落任何 V 值 · 不许改网表/脚表/BOM/板/原理图/EXPECT 断言 · 不许碰 SW/MECH (★ISS-258/259 在跑★) · "
                 "不碰板 (B-1~B-8 继续排队) · 零外发 · 不自签 issue_log · 不代拍 A3/W-1 ★"),
        "task_brief": brief,
        "dispatched_at": None,
    })

    shutil.copy2(LOG, LOG + ".bak_20261116_2215_open260")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("OK: ISS-260 新开 (owner=hw-lead, status=open)")
    print("issues total:", len(log["issues"]))


if __name__ == "__main__":
    main()
