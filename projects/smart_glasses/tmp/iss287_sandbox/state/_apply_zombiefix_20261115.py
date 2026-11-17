#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清 3 条僵尸 fixing + 退回 open 重派 (2026-11-15 20:5x, 项目总工 main)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· `state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 队列对三个总工全是空的
· ★**根因 = 3 条【僵尸 fixing 标记】** (★同病第 11~13 次复发★):
  - ISS-195 (hw-lead): 子会话 `agent:hw-lead:subagent:eba704c3` (sessionId `dc510f7c`) 2026-11-12 08:10 结束,
    status=**failed** ⇒ 交卷事件投给了已死的会话 ⇒ 没人落账 ⇒ status 停在 `fixing`
  - ISS-205 (sw-lead): 子会话 `agent:sw-lead:subagent:0795c93a` (sessionId `660e4fce`) 2026-11-12 08:24 结束,
    status=**failed** ⇒ 同上
  - ISS-206 (mech-lead): 子会话 `agent:mech-lead:subagent:00f7c6d7` (sessionId `d5a63589`) 2026-11-12 08:23 结束,
    status=**failed** ⇒ 同上
· ★**实测代价 (★本脚本用文件 mtime 逐个核过★)**: 2026-11-12 03:44 之后, 项目里**没有一个文件被写过**
  (板 / 网表 / 原理图 / 分片 / issue_log 全部停在 11-12 03:4x) ⇒ ★**队列停摆 3.5 天, 零产出★ ★
· ⇒ ★**`advance.py` 的 in_flight 规则 (★"该 agent 正在干别的, 本轮跳过"★) ⇒ 三个总工全被挡住 ⇒ A 段恒空** ★

★★**三条交卷我逐份独立复核过 (★不采信自述, 只看盘上实物★)** ★★:
· ISS-195 ⇒ ★**半交卷** ★: `HW/iss121_mic_magnet_check.py` mtime **2026-11-12 03:43:43** (★第 171~173 行已写
  "PIN-SET-2 孔位 = 现行 60×30 板 / 套 A (ISS-194 仲裁定版)"★ · 第 189 行 "J_CHG 座体 keep-out (现行 60×30 板)"★)
  · `HW/iss121_mic_magnet_check.json` mtime **2026-11-12 03:43:07** ★
  ⇒ ❌ `HW/ISS121_MIC_MAGNET_POSITION.md` mtime **2026-11-01 23:50** (★一字未动 ⇒ 三处 15mm 老口径还在★)
  ⇒ ❌ `HANDOFF/` 无 ISS-195 交卷报告 ⇒ ❌ 分片未登记
  ⇒ ★**处置 = 退回 open 重派【收尾】** (★brief 追加【已落盘文件 + 真正缺口清单】★)
· ISS-205 ⇒ ★**半交卷 (★核心产出在盘★)** ★: `state/gen_kicad_sch.py` mtime **2026-11-12 03:36:22**
  (★第 280~287 行 = 位号加 `_1` 后缀的生成逻辑★ · 第 553 行 = ISS-205 的图↔表 ref 精确映射★)
  · `HW/PCB/demo_mainboard.kicad_sch` + `demo_mainboard_p1..p10.kicad_sch` 全部 mtime **2026-11-12 03:36**
  ⇒ ★**实测图上位号**: `(property "Reference" ...)` 共 **218** 个, 其中带 `_1` 后缀 **187** 个
  ⇒ ★**实测 sheet_instances**: 根页 + 10 个子页 **11/11 都有** (★原缺件已补上★)
  ⇒ ❌ 问号归零**未实测** (投产包 BOM `HW/PCB/production/doc/demo_mainboard-kicad-bom.xml` 仍是 11-11 17:25 的旧件,
    带 `?` 的行 **186** ⇒ ★**这正是本单 ⑦ 说的"投产包变旧 = 预期中间态", 不是它没做完★**)
  ⇒ ❌ 无交卷报告 ⇒ ❌ 分片未登记
  ⇒ ★**处置 = 退回 open 重派【收尾 + 自证】** ★
· ISS-206 ⇒ ★**骨架级 0 产出** ★: `state/fragments/mech.yaml` mtime **2026-11-12 02:46:55** (★**早于**它 03:2x 的派活时间★)
  ⇒ ★**实测第 3 套 pin map 还在**: `state/fragments/mech.yaml` 第 1362 行 still 写着
  "§9 `mech_j_chg_pins` 行仍写 value = `8p@0.5mm`" ⇒ ★**本单一个字都没动★**
  ⇒ ★**处置 = 退回 open 重派 (★brief 已含 main 逐条裁完的裁决, 照做即可★)** ★

★★**落账纪律 (与项目既有范式一致)** ★★:
① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (⇒ 除本脚本要改的那几条外, 一个字节都不许动)
③ 原子写 (tmp → fsync → os.replace → fsync(dir))
④ 只改 3 条僵尸 (status/dispatched_at/note), 不动任何其它 issue

★**边界**: 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 /
不下采购单 · 板 / 网表 / 原理图 / BOM 一个字节不动
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

ZOMBIE_HEADER = (
    "\n★**2026-11-15 20:5x 项目总工 (main) 清僵尸 fixing (★同病第 11~13 次复发★)**:\n"
    "★**实测**: 子会话 %s 2026-11-12 %s 结束, status=**failed** ⇒ ★**交卷事件投给了已死的会话 ⇒ 没人落账 ⇒ "
    "status 停在 `fixing` ⇒ `advance.py` 的 in_flight 规则永久占住 %s 的名额 ⇒ A 段恒空** ★\n"
    "★**实测代价**: 2026-11-12 03:44 之后项目里**零文件改动** ⇒ ★**队列停摆 3.5 天, 零产出** ★\n"
)

NOTES = {
    "ISS-195": (
        "agent:hw-lead:subagent:eba704c3 (sessionId `dc510f7c`)", "08:10", "hw-lead",
        "★**半交卷 (★产物在盘, 收尾没做★)**:\n"
        "  ✅ `HW/iss121_mic_magnet_check.py` mtime **2026-11-12 03:43:43** (★第 171~173 行已写\"PIN-SET-2 孔位 = "
        "现行 60×30 板 / 套 A (ISS-194 仲裁定版)\"★ · 第 189 行 \"J_CHG 座体 keep-out (现行 60×30 板)\"★)\n"
        "  ✅ `HW/iss121_mic_magnet_check.json` mtime **2026-11-12 03:43:07**\n"
        "  ❌ `HW/ISS121_MIC_MAGNET_POSITION.md` mtime **2026-11-01 23:50** (★一字未动 ⇒ 三处 15mm 老口径还在★)\n"
        "  ❌ `HANDOFF/` 无 ISS-195 交卷报告 ⇒ ❌ `state/fragments/hw.yaml` 未登记本单\n"
        "⇒ ★**处置 = 退回 open 重派【收尾】** (★新 brief 追加【已落盘文件 + 真正缺口清单】★)\n"
    ),
    "ISS-205": (
        "agent:sw-lead:subagent:0795c93a (sessionId `660e4fce`)", "08:24", "sw-lead",
        "★**半交卷 (★核心产出在盘, 差自证与交卷★)**:\n"
        "  ✅ `state/gen_kicad_sch.py` mtime **2026-11-12 03:36:22** (★第 280~287 行 = 位号加 `_1` 后缀的生成逻辑★ · "
        "第 553 行 = ISS-205 的图↔表 ref 精确映射★)\n"
        "  ✅ `HW/PCB/demo_mainboard.kicad_sch` + `demo_mainboard_p1..p10.kicad_sch` 全部 mtime **2026-11-12 03:36**\n"
        "  ✅ ★**实测图上位号**: `(property \"Reference\" ...)` 共 **218** 个, 其中带 `_1` 后缀 **187** 个\n"
        "  ✅ ★**实测 sheet_instances**: 根页 + 10 个子页 **11/11 都有** (★原缺件已补上★)\n"
        "  ❌ 问号归零**未实测** (投产包 BOM `HW/PCB/production/doc/demo_mainboard-kicad-bom.xml` 仍是 11-11 17:25 的旧件, "
        "带 `?` 的行 **186** ⇒ ★**这是 brief ⑦ 说的\"投产包变旧 = 预期中间态\", 不是没做完★**)\n"
        "  ❌ 无交卷报告 ⇒ ❌ `state/fragments/sw.yaml` 未登记本单\n"
        "⇒ ★**处置 = 退回 open 重派【收尾 + 自证】** ★\n"
    ),
    "ISS-206": (
        "agent:mech-lead:subagent:00f7c6d7 (sessionId `d5a63589`)", "08:23", "mech-lead",
        "★**骨架级 0 产出**:\n"
        "  ❌ `state/fragments/mech.yaml` mtime **2026-11-12 02:46:55** (★**早于**它 03:2x 的派活时间 ⇒ 本单没写过它★)\n"
        "  ❌ ★**实测第 3 套 pin map 还在**: `state/fragments/mech.yaml` 第 1362 行仍写着 \"§9 `mech_j_chg_pins` 行仍写 "
        "value = `8p@0.5mm`\" ⇒ ★**本单一个字都没动**★\n"
        "  ❌ 无交卷报告\n"
        "⇒ ★**处置 = 退回 open 重派 (★brief 已含 main 逐条裁完的裁决, 照做即可★)** ★\n"
    ),
}


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".zombiefix.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        issues = doc["issues"]

        # ---- 自证: yaml 往返必须逐字节相同 (除本脚本要改的, 一个字节都不许动) ----
        rt = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        if rt != raw:
            print("★自证失败: yaml.safe_dump(整份 doc) 与原文件不一致 ⇒ 拒绝写 (防口径漂移)")
            print("   原文件 %d B / 往返 %d B" % (len(raw), len(rt)))
            return 2

        by_id = {i["id"]: i for i in issues}
        changed = []
        for iid, (sess, when, agent, detail) in NOTES.items():
            it = by_id.get(iid)
            if not it:
                print("★找不到 %s ⇒ 拒绝写" % iid)
                return 2
            if it.get("status") != "fixing":
                print("★%s 的 status 不是 fixing (是 %r) ⇒ 拒绝写" % (iid, it.get("status")))
                return 2
            it["status"] = "open"
            it["dispatched_at"] = ""
            note = it.get("note") or ""
            it["note"] = (note + ZOMBIE_HEADER % (sess, when, agent) + detail).lstrip("\n")
            changed.append(iid)

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, out)
        print("★已清僵尸 fixing 并退回 open: %s" % ", ".join(changed))
        print("★issue_log.yaml %d B → %d B (只改这 3 条的 status/dispatched_at/note)" % (len(raw), len(out)))
        return 0


if __name__ == "__main__":
    sys.exit(main())
