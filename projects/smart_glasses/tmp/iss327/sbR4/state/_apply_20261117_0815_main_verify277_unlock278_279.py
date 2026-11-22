#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 08:1x · job 775d9893「ARS45 继续执行后继计划」
★(1) ISS-277 独立复验 ⇒ 落 verified (★main 自己实跑 14 条 rc, 不抄交卷报告★)★
★(2) ISS-278 / ISS-279 僵尸解锁: fixing → open (★07:53:40 网关重载把会话截断, 盘上零产物★)★
★    并给两份任务书补上【纪律块】(★先落盘骨架 / nohup 后台 / 单条 exec ≤120 秒 / 每 10 分钟写盘★)★
★**只动 3 个文件: state/issue_log.yaml + state/dispatch_briefs/ISS-278_*.md + ISS-279_*.md★★
★**不碰真源 / 分片 / 板 / 网表 / 脚表 / BOM / 任何既有门禁脚本**★
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0815_main_verify277_unlock278_279"
TODAY = "2026-11-17"

BRIEF_278 = os.path.join(PROJ, "state", "dispatch_briefs", "ISS-278_mech_onepass_sync.md")
BRIEF_279 = os.path.join(PROJ, "state", "dispatch_briefs", "ISS-279_sw_board_side_input_sync.md")

DISC = """

---

## ★★⑧ 续做纪律 (★2026-11-17 08:1x main 补写 · ★★本单上一趟就是这么死的★★)

★**上一趟 (07:3x 那一派) 被 07:53:40 的网关重载整段截断 ⇒ 盘上零产物 ⇒ 白跑一轮** ★
⇒ ★**所以这一条是硬要求, 不是建议**: ★**第一件事 = 用 `write` 把交卷单骨架落盘 (★哪怕只写 3 行标题 + 交付物清单★)** ★
⇒ ★**长任务一律 `nohup ... > logs/<iss号>/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★
⇒ ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**不许攒在内存里最后一次性写** ★
⇒ ★**每落一件交付物就把 rc 追加进交卷单 (★这样再被重载也能续做★)** ★
⇒ ★**分片写完必须 `grep` 校验自己的 key 在不在 (★`frag_write.py` 无锁 ⇒ 并发写会 lost-update★)** ★
"""


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


VERIFY_277 = {
    "fix_ref": ("HANDOFF/2026-11-17_hw-lead_ISS277_板侧漏项覆盖度收口.md · "
                "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md (md5 205ac2e4c0e3aeceff42533c9b3a5ba1) · "
                "HW/check_onepass_preflight_coverage.py (md5 ba38f50e76fd9bc710cc9167d539d472) · "
                "state/_iss277_build_preflight.py (md5 0767fcc5471249d1f533e2e45394d96d)"),
    "verify_note": (
        "★**main 2026-11-17 08:0x~08:1x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
        "① `HW/check_onepass_preflight_coverage.py` ⇒ **rc=0 (P1~P6 全 PASS)** ★实测摘要: P1 条目 31 条/9 字段齐 · "
        "P2 S1~S13 步覆盖 (S1=1 S2=3 S3=2 S4=3 S5=1 S6=9 S7=2 S8=1 S9=1 S10=5 S11=1 S12=1 S13=1) · P3 判据脚本全在盘 · "
        "P4 26 个标记全覆盖 · P5 5 个现状探针与盘面一致 · P6 受保护 5 件 md5 逐字节不变 ② `--selftest` ⇒ **rc=0 (反向 8/8 全抓到)** ★"
        "(★含两条超出要求的新增: ⑦ source_iss 改成来源不明 ⇒ P4 红 + 基线全绿★) ③ 既有闸复跑全绿: `check_board_frame_caliber.py` rc=0 + "
        "`--selftest` rc=0 · `check_step1_parts_spec.py` rc=0 · `check_part_selection_matrix.py` rc=0 · `check_iss247_f1_landed.py` rc=0 · "
        "`check_land_row_anchors.py` rc=0 ④ `check_netlist_selfconsistency.py --expect-resolved` ⇒ **rc=1 (仍 18 条, 一条没变 = 既有状态)** ⑤ "
        "`state/check_pcb_drc.py` ⇒ **rc=0 (unconnected=45 · DRC=0 · Gerber 32 · C1~C7 全过)** ⑥ **受保护 5 件 md5 逐字节不变**: "
        "板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro 3e504d2be83152e337949723e909be1b` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · "
        "脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` ⇒ ★**只新增文件 + 追加式订正, 判据逻辑 0 改动, 零落表** ⇒ 落 verified ★ "
        "★**本单的价值 (★记一笔★)**: 从此「板只改一次」那一趟开工前多了一道【覆盖度保险】⇒ ★**漏项当场红, 而不是漏到板子改完才发现**★"
    ),
}

ZOMBIE = (
    " ★**2026-11-17 08:1x 追加 (main)**: ① ★**上一趟 (07:3x 那一派) 于 07:53:40 被网关重载整段截断 ⇒ 盘上零产物 (★交卷单/规格页/闸 全无★) "
    "⇒ status 停在 fixing 却是【僵尸 in_flight 锁】⇒ 本单已解锁 (fixing → open) 让队列重派**★ ② ★**重派时必须先看【⑧ 续做纪律】(★已补进任务书★): "
    "第一件事 = `write` 落交卷单骨架 ⇒ 长任务 nohup 后台 + 单条 exec ≤120 秒 ⇒ 每 10 分钟至少写盘一次 ⇒ 每落一件交付物就把 rc 追加进交卷单 ⇒ "
    "分片写完 grep 校验 (★frag_write.py 无锁, 并发写会 lost-update★)★** ③ ★**边界不变**: 零写板 · 零落表 · 零改对方域的文件 · 只写自己分片 · 零外发 · 不替老板拍板 ★"
)


def main() -> int:
    shutil.copy2(LOG, BAK)
    lines = open(LOG, encoding="utf-8").read().split("\n")

    def bounds(iid):
        start = end = None
        for i, ln in enumerate(lines):
            if ln.startswith("- id: "):
                if start is not None:
                    end = i
                    break
                if ln[len("- id: "):].strip() == iid:
                    start = i
        if start is None:
            return None, None
        if end is None:
            end = len(lines)
        return start, end

    # ---------- 1) ISS-277 → verified ----------
    s, e = bounds("ISS-277")
    if s is None:
        print("❌ 找不到 ISS-277")
        return 2
    blk = lines[s:e]
    for j, ln in enumerate(blk):
        if ln.strip() in ('status: fixing', 'status: "fixing"'):
            blk[j] = '  status: "verified"'
        elif ln.strip().startswith("fix_ref:") and ln.strip() in ("fix_ref: null", 'fix_ref: "null"'):
            blk[j] = "  fix_ref: %s" % q(VERIFY_277["fix_ref"])
        elif ln.strip().startswith("verify_result:") and "null" in ln:
            blk[j] = '  verify_result: "pass"'
        elif ln.strip().startswith("verify_date:") and "null" in ln:
            blk[j] = "  verify_date: %s" % q(TODAY)
    while blk and blk[-1].strip() == "":
        blk.pop()
    blk.append("  verify_note: %s" % q(VERIFY_277["verify_note"]))
    lines[s:e] = blk

    # ---------- 2) ISS-278 / ISS-279 → open (解锁僵尸) + 任务书补纪律块 ----------
    for iid in ("ISS-278", "ISS-279"):
        s, e = bounds(iid)
        if s is None:
            print("❌ 找不到 %s" % iid)
            return 2
        blk = lines[s:e]
        changed = False
        for j, ln in enumerate(blk):
            if ln.strip() in ('status: fixing', 'status: "fixing"'):
                blk[j] = '  status: "open"'
                changed = True
            elif ln.strip().startswith("note:") and ln.strip().startswith('note: "'):
                try:
                    cur = json.loads(ln.strip()[len("note: "):])
                except Exception:
                    cur = None
                if isinstance(cur, str):
                    blk[j] = "  note: %s" % q(cur + ZOMBIE)
        while blk and blk[-1].strip() == "":
            blk.pop()
        # 任务书末尾补纪律块 (task_brief 是单行 JSON 字符串)
        for j, ln in enumerate(blk):
            if ln.strip().startswith("task_brief:"):
                raw = ln.strip()[len("task_brief:"):].strip()
                try:
                    tb = json.loads(raw)
                except Exception:
                    tb = None
                if isinstance(tb, str):
                    blk[j] = "  task_brief: %s" % q(tb + DISC)
        lines[s:e] = blk
        if not changed:
            print("⚠ %s 没找到 status: fixing 行 (可能已被人改过)" % iid)

    open(LOG, "w", encoding="utf-8").write("\n".join(lines))

    # ---------- 3) 任务书文件也补纪律块 ----------
    for path in (BRIEF_278, BRIEF_279):
        txt = open(path, encoding="utf-8").read()
        if "⑧ 续做纪律" not in txt:
            open(path, "w", encoding="utf-8").write(txt.rstrip("\n") + "\n" + DISC)

    # ---------- 4) 自检 ----------
    d2 = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    ids = {it["id"]: it for it in d2["issues"]}
    for iid in ("ISS-277", "ISS-278", "ISS-279"):
        it = ids[iid]
        print("  %s -> %-9s owner=%-9s verify_by=%-6s verify_result=%s" % (
            iid, it["status"], it.get("owner"), it.get("verify_by"), it.get("verify_result")))
    print("  brief 278 纪律块 =", "⑧ 续做纪律" in open(BRIEF_278, encoding="utf-8").read())
    print("  brief 279 纪律块 =", "⑧ 续做纪律" in open(BRIEF_279, encoding="utf-8").read())
    print("  task_brief 278 含纪律块 =", "⑧ 续做纪律" in (ids["ISS-278"].get("task_brief") or ""))
    print("  task_brief 279 含纪律块 =", "⑧ 续做纪律" in (ids["ISS-279"].get("task_brief") or ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
