#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/_apply_20261117_0755_verify_iss275_open_iss279.py

★main 2026-11-17 07:5x (cron 775d9893 继续执行后继计划)★

★**为什么有这一趟**: ★`advance.py --json` 实测 `internal: []` / `approvals: []` ★
  ⇒ 根因 = ★**三个总工各被一条 `fixing` 单锁死 (in_flight 规则)★** ★
  ⇒ ★**其中 ISS-275 (sw-lead) 的会话实测 `status=done` (07:32 交卷完成) ⇒ 僵尸单 ★**
  ⇒ ⇒ ★**sw-lead 名额被一条已经干完的单占着 ⇒ 队列静默断线** ★

★**本脚本做两件事**: ①**ISS-275 落 verified** (★main 本机独立实跑复验, 不抄交卷报告★)
  ②**新开 ISS-279 (sw-lead)**: 「板只改一次」那一趟的【SW 侧板侧输入收口】★
  ⇒ ★**补上第三条腿**: ISS-277 = HW 侧 · ISS-278 = MECH 侧 · ★**ISS-279 = SW 侧 (本单)★** ★

★**边界**: 只写 state/issue_log.yaml + state/dispatch_log.yaml; 不碰板/网表/脚表/BOM;
  不写任何分片; 不替老板拍板; 零外发。★
"""
import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_P = os.path.join(HERE, "issue_log.yaml")
DL_P = os.path.join(HERE, "dispatch_log.yaml")
TODAY = "2026-11-17"


def main() -> int:
    # ---------- 备份 ----------
    bak = os.path.join(HERE, ".bak_iss279")
    os.makedirs(bak, exist_ok=True)
    for p in (LOG_P, DL_P):
        shutil.copy2(p, os.path.join(bak, os.path.basename(p) + ".bak_iss279"))

    log = yaml.safe_load(open(LOG_P, encoding="utf-8"))
    issues = log["issues"]
    by_id = {it["id"]: it for it in issues}

    def brief(name):
        p = os.path.join(HERE, "dispatch_briefs", name)
        return open(p, encoding="utf-8").read()

    changed = []

    # ---------- ① ISS-275 落 verified (main 本机独立复验) ----------
    i275 = by_id["ISS-275"]
    assert i275["status"] == "fixing", i275["status"]
    i275["status"] = "verified"
    i275["verify_by"] = "main"
    i275["verify_date"] = TODAY
    i275["fix_ref"] = "HANDOFF/2026-11-17_sw-lead_ISS275_SW侧R6判决源同构收口.md"
    i275["verify_result"] = (
        "★main 2026-11-17 07:3x~07:5x 本机独立实跑复验 (不抄交卷报告)★ "
        "⇒ `python3 SW/tools/check_demo_panel_spec.py` rc=0 (R1~R7 全过, 实读输出含 "
        "『R6 受保护真源三方对账 (锚点 ↔ 落表台账 ↔ 盘上真源) 一致』+ 『R7 已修复 (留痕) 在场』) "
        "⇒ `--selftest` rc=0 (16/16, 与基线同数 ⇒ 反向用例一条没删) "
        "⇒ `SW/tools/check_demo_panel_spec_r6_selftest.py` rc=0 (7/7) "
        "⇒ `SW/tools/timing_check.py` rc=0 (71/71) "
        "⇒ `HW/check_step1_parts_spec.py` rc=0 (8/8, ISS-237 的闸没被改红) "
        "⇒ 受保护 5 件 md5 实测 = 基线 (板 611b869e… / .kicad_pro 3e504d2b… / 网表 e06c1dd6… / "
        "脚表 287e7861… / BOM 94642d07…) ⇒ 板零变化, 仍不许投板 "
        "⇒ 交付物 5 件全在盘 (SW/tools/check_demo_panel_spec.py md5 d8248eca… (★未动★) · "
        "SW/tools/check_demo_panel_spec_r6_selftest.py fd4b2009… (新建) · "
        "SW/SW_MD5_BASELINE_LEDGER.md 160df540… (纯追加) · 交卷单 41840 B · 分片 2 claim+4 artifact+1 need) "
        "⇒ 台账 §3 留痕 R-01~R-10 连续无缺口 (★6 跳历史一条没删★) · 交卷单 B1~B6 六块齐全且 0 处「施工中·待填」残留 "
        "⇒ ★**R6 判决源已从「域侧锚点副本」换成「落表台账链头」⇒ 合法落表不再红, 悄悄换真源照样红 (R1 红/R2 绿/R3 红/R4 绿/R5a 红/R5b 红/R6 红)★ "
        "⇒ ★**注: 本单只解决了「台账管的两个文件 (网表/脚表)」, `hard_protected` 的板/.kicad_pro 仍走【纯 md5 分支】 "
        "(check_demo_panel_spec.py L459~L472) ⇒ 板一改就红 ⇒ 该缺口已登记为 ISS-279 (SW 侧板侧输入收口)★** ★"
    )
    i275["note"] = (i275.get("note") or "") + (
        " | 2026-11-17 07:5x (cron 775d9893) ★main 独立复验通过 ⇒ 落 verified★ "
        "⇒ 依据 = 本机实跑 check_demo_panel_spec.py rc=0 + --selftest 16/16 + r6_selftest 7/7 + timing_check 71/71 "
        "+ 受保护 5 件 md5 与基线逐字节一致 "
        "⇒ sw-lead 名额已释放 (下一轮可接新单) ⇒ ★**遗留: hard_protected 那两个件不在链头机制内 ⇒ 归 ISS-279** ★"
    )
    changed.append("ISS-275 fixing → verified")

    # ---------- ② 新开 ISS-279 (sw-lead) ----------
    assert "ISS-279" not in by_id
    issues.append({
        "id": "ISS-279",
        "title": "★★[主线内·SW 侧·纯分析+作业包订正+机器闸类] ★★「板只改一次」那一趟的【SW 侧板侧输入收口】★★ ⇒ ★**ISS-277 = HW 侧 · ISS-278 = MECH 侧 · 这一条 = SW 侧 (第三条腿), 目前没人认领** ★ ⇒ ★**★板那一趟一旦改板, SW 侧门禁【当场必红】且【无路可走】★★ ⇒ ★**SW 台账 `hard_protected` 钉的板/.kicad_pro 走【纯 md5 比对】, 不在落表台账链头机制内 ⇒ 板一改就红; 而手改 md5 正是 ISS-273/ISS-275 花大力气堵掉的「悄悄换真源」漏洞 ⇒ ★**⇒ 不先做这一单, 那一趟落地当天 SW 侧必然二选一: 假红 或 挖坑** ★",
        "severity": "high",
        "source_blocker": None,
        "source_agent": "main",
        "desc": (
            "★main 2026-11-17 07:3x~07:5x 本机实读 + 实跑 (不抄交卷报告)★\n"
            "★**① 「板只改一次」那一趟的第三条腿缺人** ★: 已有 ISS-277 (hw-lead, 在飞) 做 HW 侧板侧项全集 + 覆盖度闸 · "
            "ISS-278 (mech-lead, 在飞) 做 MECH 侧板侧输入规格 + 闸 ⇒ ★**main 实读 ISS-277 任务书全文 9151 字: "
            "`sw-lead` 命中 0 次 / `跨域` 0 次 / `全域` 0 次 ⇒ ISS-277 明面上就不管 SW 侧** ★\n"
            "★**② ★★最硬的一条: 板那一趟改板 ⇒ SW 侧 R6 当场必红, 且无路可走★★** ★ (本机实读): "
            "台账 `SW/SW_MD5_BASELINE_LEDGER.md` §1 `hard_protected[0]` 钉死板 md5 `611b869e13518c3c023fb178f91a0075` · "
            "`hard_protected[1]` 钉死 `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ "
            "`SW/tools/check_demo_panel_spec.py` L459~L472 对这两个件走【独立纯 md5 分支】(got != want 即红, "
            "**不经过链头机制**) ⇒ ★**而 `source_ledger.entries[]` 只管网表 + 脚表两个文件** ⇒ "
            "★**板 md5 变 ⇒ SW R6 必红; 合法落表能自动前移链头, 合法改板没有 ⇒ 无路** ★ ⇒ "
            "★**手改 `hard_protected` 里的 md5 = 把 ISS-273/ISS-275 刚堵掉的「悄悄换真源」又挖开 ⇒ 二选一: 假红 或 挖坑** ★\n"
            "★**③ 那一趟会动的板面东西里, SW 侧有话说的 8 条 (main 本机实测)** ★: "
            "① 板 md5 本身 (必红) ② `.kicad_pro` md5 (必红) "
            "③ 8 个落表残项位号 (`D_CHG_LED`/`D_LED_G`/`D_LED_R`/`SW_BOOT`/`SW_KEY_PWR`/`SW_KEY_VM`/`SW_KEY_VP`/`SW_RST`) "
            "★**脚表里各 2 行 / 脚数 584 全过 ⇒ 不是缺脚, 是 value 仍写「待选型」+ land 要同批重画** ⇒ "
            "`SW/tools/timing_check.py:922` `sw_rst_row_dnp` 读 SW_RST 的 DNP 状态 ⇒ 那 8 行落表后断言期望值要跟着定 "
            "④ `D_CHG_LED` 在网表里挂 `board=CHG_BOARD` 且★**板上无此封装** ⇒ 而 `SW/SHUTDOWN_SEMANTICS_SPEC.md` 写的是 "
            "`Q_CHG_LED` ⇒ 两个位号口径必须对齐 "
            "⑤ 5 颗按键的板侧网名 ≠ 位号 (`SW_BOOT`→`BOOT_N` · `SW_KEY_PWR`→`KEY_PWR` · `SW_KEY_VM`→`KEY_VOL_M` · "
            "`SW_KEY_VP`→`KEY_VOL_P` · `SW_RST`→`RESET_N`) ⇒ `timing_check.py:1264`/`:1491` 两条断言期望值会变 "
            "⑥ ★**`TP_INT` 网表 0 行 + 板上 0 行** ⇒ 触控中断那条线根本没画 ⇒ SW 若按「有触控中断」写代码 = 写到不存在的网上 "
            "⑦ `C_VBUS_GND` 两个多余焊盘 (pad1=GND / pad2=VBUS_5V_CHG) ⇒ 拿掉后 SW 侧 USB/救砖前提判据跟着变 "
            "⑧ `D_ESD_USB_D` 只有 2 焊盘 + 距 `J_USB_C` 47.99mm (R4/R9 未落表项)\n"
            "★**④ 交卷物** ★: ① 新建 `SW/BOARD_ONEPASS_SW_SYNC.md` (SW 侧板侧输入清单 · 9 字段逐条表 + 机器可读 JSON + "
            "§3 SW→板 输入清单 + ★§4「板改过一次 SW 侧怎么合法跟上」设计页★) "
            "② 追加式订正 `SW/SW_MD5_BASELINE_LEDGER.md` (§3 追加 R-11 留痕行 + §4 新增设计节, ★**老字一行不删 + "
            "§1 锚点块一个字节不许动**) ③ 新建 `SW/tools/check_onepass_sw_sync.py` (W1 字段齐 / W2 归属步合法 / "
            "W3 判据命令真存在 / W4 ①~⑧ 八条一条不缺 / W5 现状一致 / W6 保护件 md5 + 台账锚点未动 + ≥6 条反向 selftest) "
            "④ 交卷单 B1~B6 ⑤ 分片\n"
            "★**⑤ 核心设计题 (只列方案+代价, 不许自己拍)** ★: 「hard_protected 那两个件怎么合法跟上」三选一 ⇒ "
            "① 给板也建链头 (同构网表) ② 保留纯 md5 + 合法改板做成单号背书的显式动作 ③ 拆两层 (SW 只判「变没变」, "
            "真判据交板侧闸) ⇒ ★**归 main→老板** ★\n"
            "★**类别**: 内部活 · SW 侧 · 纯分析 + 作业包订正 + 机器闸类 · **零写板 · 零落表 · 零改既有判据阈值** ⇒ "
            "**不是老板级拍板** ★"
        ),
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "2026-11-17 07:5x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮 07:3x~07:5x 本机实读 "
            "台账 §1 锚点块 + 实读 check_demo_panel_spec.py R6 实现 (L459~L472) + 实读板/网表/脚表** ★\n"
            "⇒ ★**任务书 `state/dispatch_briefs/ISS-279_sw_board_side_input_sync.md`** ★\n"
            "★**sw-lead 名额本轮真空 (ISS-275 已于 07:5x 落 verified ⇒ 释放; 会话实测无 running) ⇒ 本单是本轮给 sw-lead 的活** ★\n"
            "★**★为什么排第一 (老板 2026-11-17 00:43 主线 = 绘制 PCB 图)★**: ★**它是「板只改一次」那一趟开工前的"
            "【SW 侧后果预警】⇒ 不做这一单, 那一趟落地当天 SW 侧必然二选一 (假红 / 挖坑)** ★\n"
            "★**与 ISS-277 (hw-lead) / ISS-278 (mech-lead) 的分界**: ★**277 = HW 侧板侧项全集 + 覆盖度闸 · "
            "278 = MECH 侧板侧输入规格 + 闸 · 279 = SW 侧板侧输入清单 + 闸** ★ ⇒ ★**三边各写各的域, 只交叉引用, "
            "不许改对方的文件** ★\n"
            "★**边界**: 零写板 · 零落表 · 零改既有 SW 判据脚本 · ★**零改台账 §1 锚点块 (手改 md5 凑绿 = 本单最严重的失败模式)** ★ · "
            "零改 HW/ 与 MECH/ · 只写自己分片 · 零外发 · 不替老板拍板"
        ),
        "dispatched_at": None,
        "task_brief": brief("ISS-279_sw_board_side_input_sync.md"),
    })
    changed.append("ISS-279 新开 (owner=sw-lead, status=open)")

    # ---------- 落盘 ----------
    with open(LOG_P, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)

    dl = yaml.safe_load(open(DL_P, encoding="utf-8")) if os.path.exists(DL_P) else {"dispatches": []}
    dl.setdefault("dispatches", []).extend([
        {"issue": "ISS-275", "agent": "sw-lead", "at": TODAY,
         "brief": "★main 07:5x 独立复验 rc=0 + selftest 16/16 + r6_selftest 7/7 + timing_check 71/71 ⇒ 落 verified "
                  "(释放 sw-lead 名额) ⇒ ★**遗留: hard_protected 板/.kicad_pro 不在链头机制内 ⇒ 归 ISS-279** ★"},
    ])
    with open(DL_P, "w", encoding="utf-8") as f:
        yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)

    print("=== 已落 ===")
    for c in changed:
        print(" ·", c)
    print("备份 →", bak)
    return 0


if __name__ == "__main__":
    sys.exit(main())
