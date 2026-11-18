#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★main 2026-11-17 05:4x (cron fb67af40 队列自动派活) · ISS-272 复验落 verified + ISS-261 fixed→verified (★靠 sw-lead 的独立复核结论·验证分离★)★

★★**本脚本做两件事 (★只改 issue_log, 不碰任何生产文件★)** ★★

★**① ISS-272 fixing → verified (★main 独立复验, 不采信交卷自述★)** ★
★**实测 (★main 05:4x 本机实跑★)**: ★
· `python3 state/delivery_truth.py --selftest` ⇒ ★**rc=0 · 44 条断言** (★main 04:35 版是 31 条 ⇒ sw-lead 加压 +13★) ★
· ★**main 亲自 swap 修前/修后做 diff** ⇒ ★**`2,5c2,5`** (★只 4 行口径① 变★) · ★**第 1 行 (健康结论) + 第 6 行 (口径②) 逐字节不变** ★
· ★**文件复原实测**: swap 完 `md5sum state/delivery_truth.py` ⇒ ★**`a4cb793c41f33ee1681d46023c2ac2a7`** (★= sw-lead 交卷时的值, main 自己复原后逐字节相同★) ★
· ★**判据未被改动**: ★**`classify_run` 函数体 sha256 `77c5d00a4fc796fe` (882 B)** · ★**`runs_view` sha256 `620f1d3488a46538` (743 B)** ★
  ⇒ ★**sw-lead 只加了 `--selftest` 用例, 判据一个字节没动 (★任务书明令「判据一个字不许改」·已核★)** ★
· 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS272_投递口径mode_none归类独立复核.md` ⇒ ★**B1~B6 六块齐全** (25,980 B) ★
· 分片 `state/fragments/sw.yaml` ⇒ ★**5 个 `iss272_*` key 在盘** (走 frag_write.py 原子写) ★
· `python3 state/merge.py` ⇒ rc=0 (冲突 0) · `python3 state/gate_check.py` ⇒ rc=0 (★Q1 18/18★) · `python3 state/issue_check.py` ⇒ ★**全过** ★

★★**② ISS-261 fixed → verified (★★靠 sw-lead 的独立复核签字·C3 验证分离·owner=main 不能自签★)** ★
★**sw-lead 交卷单 §B1 的复核结论一句话 (★main 实读原文★)**: ★
★「main 的改判 = 对 (判据正确) + 有 3 个缺口 (缺口 1 已由本单补上, 缺口 2/3/4 待 main 拍板)」 ★
★**⇒ 判据本身经独立复核 = 正确 ⇒ ISS-261 的口径① 改判成立 ⇒ 可从 fixed 落 verified** ★
★**★但 sw-lead 报了 4 条缺口 (★其中缺口 2/3/4 是【改判据】的建议·按「不许代拍」纪律不由它改★)** ★
★**⇒ main 本轮不开单改判据 (★那要老板口径 + 另一趟动代码★) ⇒ ★**只把 3 条缺口登记成 main 的待办 (★不占三个总工的名额★)** ★
★**⇒ 缺口 2 (mode 水位线) / 缺口 3 (status 白名单→黑名单) / 缺口 4 (A 类三分 A/B/U) 三条 ★★**各自独立可判·且都属「会骗到老板」那一类** ⇒ ★**登记进 pm 分片当 main 的 need (★走 frag_write.py★)** ★
"""
from __future__ import annotations

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
LOG = os.path.join(HERE, "issue_log.yaml")


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


NOTE_272 = """  note: |
    ★**main 2026-11-17 05:4x (cron fb67af40 队列自动派活) · 独立复验落 verified** ★
    ★**实测 (★main 本机实跑, 不采信交卷自述★)**: `python3 state/delivery_truth.py --selftest`
    ⇒ ★**rc=0 · 44 条断言** (★main 04:35 版是 31 条 ⇒ sw-lead 加压 +13★) ★
    ★**main 亲自 swap 修前/修后做 diff** ⇒ ★**`2,5c2,5`** (★只 4 行口径① 变★) ·
    ★**第 1 行 (健康结论) + 第 6 行 (口径②) 逐字节不变** ⇒ ★**A/B/D 三类与结论行没被牵连** ★
    ★**文件复原实测**: swap 完 `md5sum` ⇒ ★**`a4cb793c41f33ee1681d46023c2ac2a7`** (★= sw-lead 交卷时的值·main 自己复原后逐字节相同★) ★
    ★**★判据未被改动 (★本单最关键的一条核验★)**: `classify_run` 函数体 sha256 `77c5d00a4fc796fe` (882 B) ·
    `runs_view` sha256 `620f1d3488a46538` (743 B) ⇒ ★**sw-lead 只加了 `--selftest` 用例, 判据一个字节没动** ★
    ★**交卷单 B1~B6 六块齐全** (25,980 B) · ★**分片 5 个 `iss272_*` key 在盘** (走 frag_write.py 原子写) ★
    ★**门禁链**: `state/merge.py` rc=0 (冲突 0) · `state/gate_check.py` rc=0 (★Q1 18/18★) · `state/issue_check.py` 全过 ★
    ★**★sw-lead 的复核结论 (★main 实读原文★)**: 「main 的改判 = 对 (判据正确) + 有 3 个缺口
    (★缺口 1 已由本单补上, 缺口 2/3/4 待 main 拍板★)」 ★
    ★★**⇒ 验证分离 (C3: verify_by ≠ owner) 成立**: owner=main ⇒ ★**main 不能自签 · sw-lead 已签** ⇒ ★**本单 verified** ★★
    ★★**但 sw-lead 报了 4 条缺口, 其中 3 条是【改判据】的建议 (★按「不许代拍」纪律它没改★)** ★
    ⇒ ★**缺口 2 (mode 水位线) / 缺口 3 (status 白名单→黑名单) / 缺口 4 (A 类三分 A/B/U) ⇒ main 本轮只登记成待办, 不动判据** ★
    ★★**★本 job 本轮最重要的一条教训 (★写进 MEMORY★)**: ★**「会话 status=failed」≠「单没做完」** ⇒
    ★**main 04:5x 那次实测【零交卷物】的判断被 05:2x 后续实测推翻 (★真身 = 04:51 那次 gateway reload 打断了会话,
    但同一单的工作在恢复后的续跑会话里落完了★) ⇒ ★★**⇒ 判僵尸前必须先查盘上产物四项:
    ① 交卷单 mtime ② 门禁脚本存在+rc ③ 生产文件 mtime ④ frag grep★ ⇒ 不许只凭会话状态** ★★"""

NOTE_261 = """  note: |
    ★**main 2026-11-17 05:4x (cron fb67af40 队列自动派活) · fixed → verified (★靠 sw-lead 的独立复核签字·C3 验证分离★)** ★
    ★**★为什么 main 不能自己签**: `state/issue_check.py` 的 C3 规定 ★**`verify_by` 不得等于 `owner`** ★
    ⇒ ★**本单 owner = main ⇒ main 不能自签 verified ⇒ 必须 sw-lead 签** ★
    ★**★sw-lead 已签 (★ISS-272 交卷单 §B1 原文·main 实读★)**: ★
    ★「main 的改判 = 对 (判据正确) + 有 3 个缺口 (★缺口 1 已由本单补上, 缺口 2/3/4 待 main 拍板★)」 ★
    ★**⇒ 口径① 的 mode=none 归类改判本身 = 经独立复核成立 ⇒ 本单可落 verified** ★
    ★**复核手段 (★sw-lead 独立做的·不是抄 main 的·★)**: ★
    ★① 自己 swap 盘上备份做修前/修后 diff ⇒ 只 4 行口径① 变 · 第 1/6 行逐字节不变 ★
    ★② ★**变异测试 (mutation testing)**: 把判据逐条改坏 (M1~M6 六种) ⇒ ★**M1~M5 全被抓到 (rc=1)** ★
    ★③ ★**发现 M6 没抓到 ⇒ 端到端 announce 分支在盘上零覆盖 (★盘上 9 个 job 的 mode 全是 none·该分支是死代码★)** ★
    ★④ ⇒ ★**补合成 run 记录用例组覆盖 announce 分支 ⇒ 断言 31 → 44 (★判据逐字节未动★)** ★
    ★★**⇒ 交卷质量: ★这不是「跑一遍 selftest 交差」, 是★【把判据改坏看闸抓不抓得住】★★** ★
    ★**★遗留 3 条缺口 (★main 本轮只登记·不改判据·那是老板口径 + 另一趟动代码★)**: ★
    ★**缺口 2** (sw-lead 建议补 mode 变更水位线) · ★**缺口 3** (建议 `status` 白名单→黑名单, fail-closed) ·
    ★**缺口 4** (建议 A 类三分 A/B/U, 让「认不出来的错误」不受 mode=none 过滤) ★
    ★★**★缺口 4 是唯一一条「真故障零告警」的路 ⇒ 代价最高 ⇒ ★main 已登记成待办 (★pm 分片 need·不走三个总工名额·不占「板只改一次」那一趟★)** ★★"""


def main() -> int:
    txt = read(LOG)
    lines = txt.split("\n")
    starts = {}
    for i, ln in enumerate(lines):
        m = re.match(r"^- id: (ISS-\d+)\s*$", ln)
        if m:
            starts[m.group(1)] = i
    order = sorted(starts.items(), key=lambda kv: kv[1])

    def block_end(iss):
        if iss not in starts:
            raise KeyError(iss)
        idx = starts[iss]
        pos = [k for k, v in order].index(iss)
        if pos + 1 < len(order):
            return order[pos + 1][1]
        return len(lines)

    notes = {"ISS-272": NOTE_272, "ISS-261": NOTE_261}
    statuses = {"ISS-272": ("fixing", "verified"), "ISS-261": ("fixed", "verified")}
    out = []
    i = 0
    changed = []

    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^- id: (ISS-\d+)\s*$", ln)
        iss = m.group(1) if m else None
        if iss in notes:
            end = block_end(iss)
            blk = lines[i:end]
            old, new = statuses[iss]
            nb = []
            skipping = False
            for b in blk:
                if re.match(r"^  note: \|?\s*$", b):
                    skipping = True
                    continue
                if skipping:
                    if re.match(r"^    \S", b):
                        continue
                    skipping = False
                if re.match(r"^  status: %s\s*$" % old, b):
                    nb.append("  status: %s" % new)
                elif re.match(r"^  verify_result:.*$", b):
                    nb.append("  verify_result: pass")
                elif re.match(r"^  verify_date:.*$", b):
                    nb.append("  verify_date: 2026-11-17")
                elif re.match(r"^  fix_ref:.*$", b) and iss == "ISS-272":
                    nb.append(
                        "  fix_ref: HANDOFF/2026-11-17_sw-lead_ISS272_投递口径mode_none归类独立复核.md (25,980 B · B1~B6 齐全) · "
                        "state/delivery_truth.py (★selftest 31→44 条断言·rc=0·判据 classify_run sha256 77c5d00a… 逐字节未动★) · "
                        "state/fragments/sw.yaml (frag_write.py 原子写 · 5 个 iss272_* key)"
                    )
                elif re.match(r"^  fix_ref:.*$", b) and iss == "ISS-261":
                    nb.append(
                        "  fix_ref: state/delivery_truth.py (★classify_run + runs_view + collect + --selftest★) · "
                        "HANDOFF/2026-11-17_main_ISS261_投递口径mode_none归类修复.md (★main 的修法交卷单★) · "
                        "★**独立复核 = HANDOFF/2026-11-17_sw-lead_ISS272_投递口径mode_none归类独立复核.md (★C3 验证分离·sw-lead 签★)★"
                    )
                else:
                    nb.append(b)
            nb.append(notes[iss].rstrip("\n"))
            out.extend(nb)
            changed.append("%s %s -> %s" % (iss, old, new))
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
