#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 08:2x · job 775d9893「ARS45 继续执行后继计划」
★把 ISS-278 / ISS-279 的【note + task_brief】换成"单行 JSON 字符串"形态, 并把续做纪律块 + 僵尸留痕写进去★
★(★原因: 那两个键在 issue_log.yaml 里是 PyYAML 折行的多行标量 ⇒ 行级脚本改不动 ⇒ 换形态 ★)★
★**只动 state/issue_log.yaml 两个块里的 4 个键 (note/task_brief × 2)★ 其余一个字节都不许动**★
★**手法: 先 yaml.safe_load 取旧值 → 新值 = 旧值 + 追加段 → 用 json.dumps 写成单行双引号标量 → 再 yaml.safe_load 复核**★
★**复核: 除这两个 issue 的 note/task_brief 外, 全文件其余所有 issue 的全部字段逐字相同**★
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0820_main_inline_brief_278_279"
IIDS = ("ISS-278", "ISS-279")

ZOMBIE_NOTE = (
    " ★**2026-11-17 08:1x 追加 (main)**: ① ★**上一趟 (07:3x 那一派) 于 07:53:40 被网关重载整段截断 ⇒ 盘上零产物 "
    "(★交卷单 / 规格页 / 闸 三件全无★) ⇒ status 停在 fixing 却是【僵尸 in_flight 锁】⇒ 本单已解锁 (fixing → open) 让队列重派**★ "
    "② ★**重派时必须先看任务书末尾的【⑧ 续做纪律】**: 第一件事 = `write` 落交卷单骨架 (★哪怕只写 3 行标题 + 交付物清单★) ⇒ "
    "长任务 `nohup` 后台 + 单条 exec ≤120 秒 ⇒ 每 10 分钟至少写盘一次 ⇒ 每落一件交付物就把 rc 追加进交卷单 ⇒ 分片写完 grep 校验 "
    "(★`frag_write.py` 无锁 ⇒ 并发写会 lost-update★)★ ③ ★**边界不变**: 零写板 · 零落表 · 零改对方域的文件 · 只写自己分片 · 零外发 · 不替老板拍板 ★"
)

DISC = """

---

## ★★⑧ 续做纪律 (★2026-11-17 08:1x main 补写 · ★★上一趟就是这么死的★★)

★**上一趟 (07:3x 那一派) 被 07:53:40 的网关重载整段截断 ⇒ 盘上零产物 ⇒ 白跑一轮** ★
⇒ ★**所以这一条是硬要求, 不是建议**: ★**第一件事 = 用 `write` 把交卷单骨架落盘 (★哪怕只写 3 行标题 + 交付物清单★)** ★
⇒ ★**长任务一律 `nohup ... > logs/iss2xx/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★
⇒ ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**不许攒在内存里最后一次性写** ★
⇒ ★**每落一件交付物就把 rc 追加进交卷单 (★这样再被重载也能续做★)** ★
⇒ ★**分片写完必须 `grep` 校验自己的 key 在不在 (★`frag_write.py` 无锁 ⇒ 并发写会 lost-update★)** ★
"""


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


def main() -> int:
    shutil.copy2(LOG, BAK)
    raw = open(LOG, encoding="utf-8").read()
    lines = raw.split("\n")
    before = yaml.safe_load(raw) or {}
    before_map = {it["id"]: it for it in before.get("issues", [])}

    def block_range(iid):
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

    for iid in IIDS:
        s, e = block_range(iid)
        if s is None:
            print("❌ 找不到 %s" % iid)
            return 2
        blk = lines[s:e]
        old_note = before_map[iid].get("note") or ""
        old_tb = before_map[iid].get("task_brief") or ""
        new_note = old_note if "僵尸 in_flight 锁" in old_note else old_note + ZOMBIE_NOTE
        new_tb = old_tb if "⑧ 续做纪律" in old_tb else old_tb + DISC

        for key, newval in (("note", new_note), ("task_brief", new_tb)):
            ki = None
            for j, ln in enumerate(blk):
                if ln.strip().startswith(key + ":"):
                    ki = j
                    break
            if ki is None:
                print("❌ %s 块内找不到 %s" % (iid, key))
                return 2
            # 收集续行 (★规则: 标量一直延续到【下一个 indent==2 的键】或【下一个 '- id: ' 块】为止;
            #   ★中间的空行属于标量本身 (plain scalar 的折行里就有空行) ⇒ 不许拿空行当终止符★)
            k = ki + 1
            while k < len(blk):
                ln = blk[k]
                if ln.startswith("- id: "):
                    break
                ind = len(ln) - len(ln.lstrip(" "))
                if ind == 2 and ":" in ln:
                    break
                k += 1
            blk[ki:k] = ["  %s: %s" % (key, q(newval))]
        lines[s:e] = blk

    out = "\n".join(lines)
    open(LOG, "w", encoding="utf-8").write(out)

    # ---------- 复核 ----------
    after = yaml.safe_load(out) or {}
    after_map = {it["id"]: it for it in after.get("issues", [])}
    ok = True
    if set(before_map) != set(after_map):
        print("❌ issue 集合变了")
        ok = False
    for iid, it in before_map.items():
        a = after_map.get(iid, {})
        for k, v in it.items():
            av = a.get(k)
            if iid in IIDS and k in ("note", "task_brief"):
                continue
            if av != v:
                print("❌ %s 的 %s 变了" % (iid, k))
                ok = False
    for iid in IIDS:
        it = after_map[iid]
        print("  %s -> %s | note+僵尸=%s | tb+纪律=%s | tb len=%d" % (
            iid, it["status"],
            "僵尸 in_flight 锁" in (it.get("note") or ""),
            "⑧ 续做纪律" in (it.get("task_brief") or ""),
            len(it.get("task_brief") or "")))
    print("  其余 issue 全部字段逐字相同 =", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
