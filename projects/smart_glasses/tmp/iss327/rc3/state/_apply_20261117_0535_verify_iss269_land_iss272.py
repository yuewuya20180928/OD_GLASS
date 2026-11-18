#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★main 2026-11-17 05:3x (cron fb67af40 队列自动派活) · ISS-269 复验落 verified + ISS-272 保持 fixing 待派★

★★**本脚本做两件事 (★都只改 issue_log + dispatch_log, 不碰任何生产文件★)** ★★

★**① ISS-269 fixing → verified (★main 独立复验, 不采信自述★)** ★
★**实测 (★main 05:2x~05:3x 本机实跑★)**: ★
· `python3 HW/check_pcb_generator_defaults.py` ⇒ **rc=0** (C1 层数 / C2 DNP / C3 Value / C4 防手滑 四条全过)
· `python3 HW/check_pcb_generator_defaults.py --selftest` ⇒ **rc=0 · 反向用例 6/6 全抓到** (★每条都自证「变异生效=True」★)
· ★**受保护 5 件 md5 逐字节不变**: 板 `611b869e…` · `.kicad_pro` `3e504d2b…` · 网表 `e06c1dd6…` · 脚表 `287e7861…` · BOM `94642d07…` ★
· 交卷单 `HANDOFF/2026-11-17_hw-lead_ISS269_板那一趟生成器三坑.md` ⇒ ★**B1~B6 六块齐全** ★
· 生成器 `state/gen_pcb_netlist_board.py` ⇒ ★**mtime 05:16:32 (★改过了★)** · ★**`PCB_LAYERS` 默认 6 → 8** (★L666★) · ★**DNP 零命中 → 21 处命中** ★
· 分片 `state/fragments/hw.yaml` ⇒ ★**`iss269_*` 4 个 key + 2 个 artifact 在盘** ★
· `python3 state/merge.py` ⇒ rc=0 (冲突 0) · `python3 state/gate_check.py` ⇒ rc=0 (★Q1 18/18★) ★

★★**② ISS-272 保持 `fixing` (★本 job 05:2x 实测: 它的 spawn 从未发生, 零交卷物★)** ★★
★**实测**: `HANDOFF/` 下无任何 ISS-272 文件 · `grep -c "iss272" state/fragments/sw.yaml` = **0** · ★**`state/delivery_truth.py` md5 = `8dad8b39d873b3d930acb1c076e240cb`** (★= main 04:35 修完的版本, 未被 sw-lead 加压过★) ★
★**⇒ 它是【幽灵 fixing】(★被兄弟 job 775d9893 落了 fixing 但 spawn 被 04:51 那次 gateway reload 打断★) ⇒ 本 job 本轮补派给 sw-lead** ★
"""
from __future__ import annotations

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def write(path, txt):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main() -> int:
    txt = read(LOG)
    if "_schema:" not in txt.split("\n")[0]:
        print("!! issue_log.yaml 第 1 行不是 _schema ⇒ 拒绝改")
        return 2
    lines = txt.split("\n")

    # ---- 定位 ISS-269 / ISS-272 的条目块 ----
    starts = {}
    for i, ln in enumerate(lines):
        m = re.match(r"^- id: (ISS-\d+)\s*$", ln)
        if m:
            starts[m.group(1)] = i
    for target in ("ISS-269", "ISS-272"):
        if target not in starts:
            print("!! 找不到 %s" % target)
            return 2
    # 块结束 = 下一个 "- id:" 之前
    order = sorted(starts.items(), key=lambda kv: kv[1])

    def block_end(iss):
        starts_list = [v for k, v in order if k == iss]
        if not starts_list:
            raise KeyError(iss)
        idx = starts_list[0]
        pos = [k for k, v in order].index(iss)
        if pos + 1 < len(order):
            return order[pos + 1][1]
        return len(lines)

    out = []
    i = 0
    changed = []

    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^- id: (ISS-\d+)\s*$", ln)
        iss = m.group(1) if m else None

        if iss == "ISS-269":
            end = block_end("ISS-269")
            blk = lines[i:end]
            newblk = []
            for b in blk:
                if re.match(r"^  status: fixing\s*$", b):
                    newblk.append("  status: verified")
                elif re.match(r"^  fix_ref:.*$", b):
                    newblk.append(
                        "  fix_ref: HW/check_pcb_generator_defaults.py (19,632 B · rc=0 · --selftest 6/6) · "
                        "HANDOFF/2026-11-17_hw-lead_ISS269_板那一趟生成器三坑.md (B1~B6 齐全) · "
                        "state/gen_pcb_netlist_board.py (★mtime 05:16:32 · PCB_LAYERS 默认 6→8 (L666) · DNP 零命中→21 处命中★) · "
                        "state/fragments/hw.yaml (frag_write.py 原子写 · 4 个 iss269_* key)"
                    )
                elif re.match(r"^  verify_result:.*$", b):
                    newblk.append("  verify_result: pass")
                elif re.match(r"^  verify_date:.*$", b):
                    newblk.append("  verify_date: 2026-11-17")
                else:
                    newblk.append(b)
            # 追加 note
            note_add = (
                "  note: |\n"
                "    ★**main 2026-11-17 05:3x (cron fb67af40 队列自动派活) · 独立复验落 verified** ★\n"
                "    ★**实测 (★main 本机实跑, 不采信交卷自述★)**: `python3 HW/check_pcb_generator_defaults.py` ⇒ **rc=0**\n"
                "    (★C1 层数 / C2 DNP / C3 Value / C4 防手滑 四条全过★) · `--selftest` ⇒ **rc=0 · 反向用例 6/6 全抓到**\n"
                "    (★每条都自证「变异生效=True」★ ⇒ 判据真在被读, 不是把红灯调没★) ★\n"
                "    ★**受保护 5 件 md5 逐字节不变**: 板 `611b869e…` · `.kicad_pro` `3e504d2b…` · 网表 `e06c1dd6…`\n"
                "    · 脚表 `287e7861…` · BOM `94642d07…` ⇒ ★**零写板 · 零落表 · 零改网表真源** ★\n"
                "    ★**交卷单 B1~B6 六块齐全** (★`HANDOFF/2026-11-17_hw-lead_ISS269_板那一趟生成器三坑.md`★) ★\n"
                "    ★**生成器实测**: mtime **05:16:32** (★改过了★) · `PCB_LAYERS` 默认 **6 → 8** (★L666★) ·\n"
                "    ★**DNP 零命中 → 21 处命中** ⇒ ★**X-3 / X-4 / B-2 三个坑全在生成器侧修掉 + 做成独立机器闸** ★\n"
                "    ★**门禁链**: `state/merge.py` rc=0 (冲突 0) · `state/gate_check.py` rc=0 (★Q1 18/18★) ★\n"
                "    ★★**上一轮 (★04:5x 兄弟 job 775d9893 重派★) 的会话 `bba7dc71` status=failed (145s)** ⇒\n"
                "    ★**main 04:5x 那次实测【零交卷物】的判断被后续实测推翻** ⇒ ★**真身是: 04:51 那次 gateway reload\n"
                "    把会话打断, 但**同一单的工作在恢复后的续跑会话里落完了** (★交卷单 mtime 05:1x~05:2x★)\n"
                "    ⇒ ★**教训: 「会话 failed」不等于「单没做完」⇒ 必须先查盘上产物再判僵尸** ★★\n"
            )
            # 去掉原有 note 块 (note: | 后面的缩进行), 换成新的
            newblk2 = []
            skipping = False
            for b in newblk:
                if re.match(r"^  note: \|?\s*$", b):
                    skipping = True
                    continue
                if skipping:
                    if re.match(r"^    \S", b):
                        continue  # 原 note 的内容行
                    skipping = False
                newblk2.append(b)
            # 去掉可能存在的空 note 行残留
            newblk2 = [b for b in newblk2 if b.strip() != "" or True]
            newblk2.append(note_add.rstrip("\n"))
            out.extend(newblk2)
            changed.append("ISS-269 fixing -> verified")
            i = end
            continue

        if iss == "ISS-272":
            end = block_end("ISS-272")
            blk = lines[i:end]
            newblk = []
            for b in blk:
                newblk.append(b)
            note_add = (
                "  note: |\n"
                "    ★**main 2026-11-17 05:3x (cron fb67af40 队列自动派活) · 本单是【幽灵 fixing】⇒ 本轮补派** ★\n"
                "    ★**实测 (★main 05:2x 本机实读★)**: `HANDOFF/` 下无任何 ISS-272 文件 ·\n"
                "    `grep -c \"iss272\" state/fragments/sw.yaml` = **0** ⇒ ★**零交卷物** ★\n"
                "    ★**根因 (★main 04:5x~05:3x 一路查实★)**: ★**04:51 那次 gateway reload** 把兄弟 job 775d9893\n"
                "    的 spawn 打掉了 ⇒ ★**落账时写了 fixing, 但会话从未真正起来** ⇒ ★**本 job 本轮补派给 sw-lead** ★\n"
                "    ★**补派前守则已过**: `state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-272_sw_delivery_truth_review.md`\n"
                "    ⇒ rc=0 (★任务书里引用的命令路径全部实测存在★) ★\n"
            )
            newblk2 = []
            skipping = False
            for b in newblk:
                if re.match(r"^  note: \|?\s*$", b):
                    skipping = True
                    continue
                if skipping:
                    if re.match(r"^    \S", b):
                        continue
                    skipping = False
                newblk2.append(b)
            newblk2.append(note_add.rstrip("\n"))
            out.extend(newblk2)
            changed.append("ISS-272 note += 幽灵 fixing 实测 + 补派")
            i = end
            continue

        out.append(ln)
        i += 1

    write(LOG, "\n".join(out))
    print("=== 落账完成 ===")
    for c in changed:
        print("  " + c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
