#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-192 状态复位 (fixing → open) + 派活理由落账 (2026-11-11 16:4x, 项目总工 main)

★**为什么需要这一步 (★实测, 不是推测★)**:
  ISS-192 (owner=mech-lead) 13:4x~14:2x 派出 ⇒ 会话 `agent:mech-lead:subagent:4e582941-...`
  于 14:30 起跑、★**15:30 被 provider 请求超时中断** (实测末条 = `openclaw:prompt-error`
  `request timed out | request timed out`; runtimeMs=3600005 ≈ 整 60 分钟 ⇒ ★**撞 1 小时上限**;
  sessions_list 报 `abortedLastRun: true` / status=done) ⇒ ★**它没交卷**:
    · ★**没有** `HANDOFF/2026-11-11_mech-lead_ISS192_*.md` (实测 `ls HANDOFF/` 只有 ISS191 那份)
    · ★**没有** `MECH/BOARD_GEOM_30MM.md` (交付物 A)
    · ★**没有** `state/fragments/mech.yaml` 写入 (实测 mtime 仍 **Nov 6 11:17** ⇒ 交付物 G 也没做)
    · 只落了 `MECH/pinset2_mech_check.json` (15:02) ⇒ 交付物 B/C/D/E/F 全部未做
  ⇒ ★**`status=fixing` 成了【假标记】** ⇒ ★**这是 ISS-181 同一个病 (第 2 次出现)**:
    `advance.py` 的 in_flight 代理判据 = 「owner 名下已有 status==fixing 的 issue ⇒ 本轮跳过该 agent」
    ⇒ ★**mech-lead 的名额被一条【已经死掉】的单永久占住** ⇒ ★**A 段会一直派不出活**。

★**为什么这次要【重派】而不是像 ISS-181 那样改成 deferred (★两者病同因不同药★)**:
  · ISS-181 = ★**PCB 布线/布局类** ⇒ 按老板 11-11 10:07 口径【一律不派】⇒ 改 `deferred` (排队) ✔
  · ISS-192 = ★**结构 (MECH) 类 + 孔位仲裁** ⇒ ★**不在【不派】名单里** ⇒ ★**它是本该继续干的活**
    ⇒ 改成 `deferred` 会把它【永久排队】⇒ ★**但它有真实现物理后果** (主线实测):
    打印包 (Rev B 笼 + 量测清单) 已按【套 A】做出, 而 `HW/pcb60x30_check.py/.json` 发的是【套 B】
    ⇒ ★**两套互斥口径差 7.50mm** ⇒ ★**若 PCB 按套 B 钻 ⇒ 螺钉与笼差 7.50mm ⇒ 板装不进骨架**
    ⇒ ★**这是真缺陷, 不是记账问题** ⇒ ★**该干完**
  ⇒ ★**处置 = 复位成 `open` 让 advance.py 自己吐出来 (走标准流程) + 本轮重派**
    ⇒ ★**状态机允许 `fixing → open`** (issue_check 的 ALLOWED_NEXT["fixing"] 含 "open") ✔

★**重派时给 mech-lead 的两条追加说明 (★不改任务范围, 只补执行方式★)**:
  ① ★**上一轮是被 60 分钟上限掐断的** (不是被 scope 驳回) ⇒ 本轮 runTimeout 给足, 且
     ★**按 A→B→C→D→E→F→G 顺序逐件落盘, 每件交付完立刻写文件 (不要攒到最后一起写)** ⇒
     ★**宁可交一半 (A/B/G), 也不要交零** ⇒ ★**这是上一轮交零的根因 (只落了 1/7)**
  ② ★**范围与边界一字未改** ⇒ 仍只写 `MECH/**` + `HANDOFF/**` + `state/fragments/mech.yaml`
     ⇒ ★**仍不许碰 `HW/**` / 网表 / 板 / 原理图 / 生成器 / 别人的分片** ⇒ ★**板 md5 611b869e 一字不许动**

★**落账纪律 (与项目既有范式一致)**:
  ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** ⇒ 通过才写
  ③ 原子写: tmp (同目录) → fsync → os.replace → fsync(dir)
  ④ ★**只改 ISS-192 这一条 dict 的字段** (status / note) ⇒ 别的 188 条一个字节不动

★**边界**: 不改 §0 锁死表 · 不改任何已发布数字 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 / 不下采购单
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
TARGET = "ISS-192"
TODAY = "2026-11-11"

NOTE_ADD = (
    "\n\n★2026-11-11 16:4x 项目总工**状态复位 + 重派** (★**实测: 上一轮是被 provider 请求超时掐断的, 不是被 scope 驳回★)**。"
    "★**事实**: 会话 `agent:mech-lead:subagent:4e582941-...` 14:30 起跑 ⇒ ★**15:30 撞 1 小时上限被中断**"
    "(实测末条 = `openclaw:prompt-error: request timed out`; runtimeMs=3600005 ≈ 整 60 分钟; "
    "sessions_list 报 abortedLastRun=true) ⇒ ★**它没交卷**: 实测 **没有** `HANDOFF/…mech-lead_ISS192_*.md`、"
    "**没有** `MECH/BOARD_GEOM_30MM.md` (交付物 A)、**没有**写 `state/fragments/mech.yaml` (mtime 仍 Nov 6 11:17 ⇒ 交付物 G 也没做)"
    " ⇒ 只落了 `MECH/pinset2_mech_check.json` (15:02) ⇒ ★**交付物 B/C/D/E/F 全未做**。"
    "★**因此 `status=fixing` 是【假标记】⇒ 这是 ISS-181 同一个病第 2 次出现** ⇒ ★**mech-lead 的名额被一条死单永久占住** ⇒ "
    "★**A 段会一直派不出活** (实测本轮 `advance.py --json` 的 internal=[] 就有它一份)。"
    "★**为什么【重派】而不是像 ISS-181 那样改 deferred (★病同因不同药★)**: ISS-181 是 ★**PCB 布线/布局类** ⇒ "
    "按老板 11-11 10:07【一律不派】⇒ deferred 正确; ★**但 ISS-192 是结构 (MECH) 类 + 孔位仲裁 ⇒ 不在【不派】名单里** ⇒ "
    "★**它是本该干完的活**, 且有★**真实现物理后果**: 打印包 (Rev B 笼 + 量测清单) 已按【套 A】做出, 而 "
    "`HW/pcb60x30_check.py/.json` 发的是【套 B】⇒ ★**两套互斥口径差 7.50mm** ⇒ ★**若 PCB 按套 B 钻 ⇒ 螺钉与笼差 7.50mm ⇒ "
    "板装不进骨架** ⇒ ★**这是真缺陷不是记账问题**。"
    "★**处置**: `fixing → open` (状态机允许, issue_check ALLOWED_NEXT[\"fixing\"] 含 \"open\") ⇒ 让 `advance.py` "
    "自己把它吐出来走标准流程 ⇒ 本轮重派。"
    "★**重派时给 mech-lead 的两条追加说明 (★不改任务范围★)**: ① ★**上一轮是被 60 分钟上限掐断的** ⇒ 本轮超时给足, 且"
    "★**按 A→B→C→D→E→F→G 逐件落盘, 每件交付完立刻写文件 (不要攒到最后一起写)** ⇒ ★**宁可交一半 (A/B/G) 也不要交零** ⇒ "
    "★**这是上一轮交零的根因 (只落 1/7)** ② ★**范围与边界一字未改**: 仍只写 `MECH/**` + `HANDOFF/**` + "
    "`state/fragments/mech.yaml` ⇒ ★**仍不许碰 `HW/**` / 网表 / 板 / 原理图 / 生成器 / 别人的分片** ⇒ "
    "★**板 md5 `611b869e…` 一字不许动**。"
)

NEW_STATUS = "open"


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "a+", encoding="utf-8") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        orig = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(orig)

        items = doc["issues"] if isinstance(doc.get("issues"), list) else list(doc["issues"].values())
        target = next((i for i in items if i.get("id") == TARGET), None)
        if target is None:
            print(f"❌ {TARGET} 不在 issue_log.yaml 里")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1
        if target.get("status") == NEW_STATUS:
            print(f"ℹ️ {TARGET} 已经是 {NEW_STATUS} ⇒ 幂等跳过")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 0
        if target.get("status") != "fixing":
            print(f"❌ {TARGET} 当前 status={target.get('status')} (不是 fixing) ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1

        probe = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        if probe != orig:
            print("❌ 中止: yaml 往返与原文件不逐字节相同 ⇒ 整份改写会动到别人的行 ⇒ 不写")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1

        target["status"] = NEW_STATUS
        target["note"] = (target.get("note") or "") + NOTE_ADD

        new_text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, new_text)

    print(f"✅ {TARGET} → status={NEW_STATUS} (等待 advance.py 吐出来) + note 已追加")
    print(f"   issue_log.yaml: {len(orig)} → {len(new_text)} 字符 (只改 ISS-192 一条)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
