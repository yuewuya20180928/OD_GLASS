#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_2005_dedup_note_250_254.py
★main (moli) 2026-11-16 20:0x (cron fb67af40 ARS45 队列自动派活)★

★★★**本脚本只做一件事: 给 ISS-250 / ISS-254 补【重复派活】留痕 (★不改任何 status★)** ★★★
★**背景 (★main 本机实测, 不靠猜★)**: ★**20:01:47 与 20:02:02 两条 sw-lead 子会话被派了【完全相同】的任务书**
  (★`state/dispatch_briefs/ISS-250_part1_reanchor_and_close.md` 全文 · ★标题「ISS-250 · 续做 (第 3 轮) · ① 先把两个红闸修绿 + ② 查证表收尾」★
   ⇒ ★brief 里明写「+ ISS-254 (★SW 侧重锚, 与本单同一会话一起做★)」★)
  ⇒ ★**两个任务书逐字相同, 不是两个不同任务** ★
★**处理**: ★**保留先起的 `b082e4ae`** (★20:01:47·范围完全覆盖: ① 重锚 + ② 查证表收尾 + ISS-254★) ·
  ★**向后起的 `3082f8a5` 发停止指令** (★★实测两条会话 tool_use 都是 0 ⇒ 盘上零写入 ⇒ 停掉零损失★) ★
  ⇒ ★**恢复「同一 agent 同时只允许一个写会话」铁律** (★MEMORY: 两个写会话会互相覆盖 fragments, 实测合并丢失 12%~38%★) ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml` 的 ISS-250 / ISS-254 两条 note (★status 一个字没动·verify_result 一个字没动★)** ★
· ★**不改任何交付物 / 不碰板 / 不碰网表 / 不碰任何分片** · ★**零外发** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
IL_LOCK = os.path.join(HERE, ".issue_log.lock")
BACKUP_DIR = os.path.join(HERE, ".bak_iss251")
STAMP = "20261116_2005"

NOTE_250 = (
    "\n\n★2026-11-16 20:0x (cron fb67af40 队列自动派活) ★**重复派活留痕 (★status 未动★)** ★\n"
    "· ★**实测**: 20:01:47 (`b082e4ae`) 与 20:02:02 (`3082f8a5`) 两条 sw-lead 子会话被派了**逐字相同**的任务书 "
    "(★`state/dispatch_briefs/ISS-250_part1_reanchor_and_close.md` 全文, 标题「ISS-250 · 续做 (第 3 轮) · ① 先把两个红闸修绿 + ② 查证表收尾」★)\n"
    "· ★**处理**: 保留先起的 `b082e4ae` (★范围完全覆盖: ① SW 侧重锚 = ISS-254 + ② ISS-250 查证表收尾★) · "
    "向后起的 `3082f8a5` 发**停止指令** (★★实测两条 tool_use 均为 0 ⇒ 盘上零写入 ⇒ 停掉零损失★) ★\n"
    "· ★**理由**: ★**同一 agent 同时只允许一个写会话** ⇒ 两个写会话会互相覆盖 `state/fragments/sw.yaml` (★实测合并丢失 12%~38%★) ★\n"
    "· ★**下一轮 cron 动作**: ★**先 `sessions_list` 核对 sw-lead 只有 1 条 running** ★; 本单交卷后 ★main 独立复验** ⇒ "
    "★**收口时按【交卷单必须同时写清 ISS-250 + ISS-254 两条】来收** (★rknn3-toolkit 这条线索若成立 ⇒ ISS-155 当场解除★) ★"
)

NOTE_254 = (
    "\n\n★2026-11-16 20:0x (cron fb67af40 队列自动派活) ★**并单留痕 (★status 未动★)** ★\n"
    "· ★**本单 (SW 侧重锚) 与 ISS-250 合到同一条 sw-lead 会话一起做** (★会话 `b082e4ae` · 20:01:47 起·★范围完全覆盖两单★)\n"
    "· ★**重复派活的那一条 (`3082f8a5` · 20:02:02) 已被停止** (★零 tool_use·零写入★) ⇒ ★**一 agent 一写会话铁律恢复** ★\n"
    "· ★**重锚口径不变**: ★**只改【网表那一条锚点】** → `md5=16ac89f77c25a3f61834cc7ebcd78a7f` · "
    "★**留 `prev_md5=611c3ba3db3dc7de7213063375b96d01`** · ★**脚表 / BOM / 板 / `.kicad_pro` 四件逐字节不动** · "
    "★**判据逻辑 0 改动** · ★**必须留反向用例 (锚点改回旧 md5 ⇒ 必须变红)** ★\n"
    "· ★**验收**: `SW/tools/check_demo_panel_spec.py` rc=0 · `SW/tools/timing_check.py` rc=0 (★自测 **71/71**★) ★"
)


def main() -> int:
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copy2(IL, os.path.join(BACKUP_DIR, f"issue_log.yaml.bak_{STAMP}"))

    with open(IL_LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        doc = yaml.safe_load(open(IL, encoding="utf-8"))
        items = doc["issues"] if isinstance(doc.get("issues"), dict) else (doc.get("issues") or [])
        byid = {it.get("id"): it for it in items}
        for iid, note in (("ISS-250", NOTE_250), ("ISS-254", NOTE_254)):
            if iid not in byid:
                raise SystemExit(f"✗ 台账里没有 {iid} ⇒ 不写")
            if note[:60] in (byid[iid].get("note") or ""):
                print(f"· {iid}: note 已存在 ⇒ 跳过 (幂等)")
                continue
            byid[iid]["note"] = (byid[iid].get("note") or "") + note
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=HERE, delete=False, suffix=".tmp") as tf:
            yaml.safe_dump(doc, tf, allow_unicode=True, sort_keys=False, width=100000)
            tmp = tf.name
        os.replace(tmp, IL)
        fcntl.flock(lk, fcntl.LOCK_UN)

    doc2 = yaml.safe_load(open(IL, encoding="utf-8"))
    items2 = doc2["issues"] if isinstance(doc2.get("issues"), dict) else (doc2.get("issues") or [])
    byid2 = {it.get("id"): it for it in items2}
    assert byid2["ISS-250"]["status"] == "fixing", byid2["ISS-250"]["status"]
    assert byid2["ISS-254"]["status"] == "fixing", byid2["ISS-254"]["status"]
    assert "重复派活留痕" in byid2["ISS-250"]["note"]
    assert "并单留痕" in byid2["ISS-254"]["note"]
    print("✅ ISS-250 / ISS-254 note 已补 (status 未动 · 重读自证过)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
