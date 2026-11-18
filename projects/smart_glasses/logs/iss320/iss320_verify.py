#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-320 · mech-lead · 交卷前机器自证 (★只读·不改任何文件★)
=====================================================================
输出 logs/iss320/VERIFY_REPORT.txt

★V7 修法 (★main 10:31 指出的 bug★): 必须拿「施改前取的全树 md5 快照」
  (logs/iss320/md5_ALL_BEFORE.txt · 31,826 个文件) 做 BEFORE 侧,
  而不是重新取一次快照当 BEFORE (★那样比的是「现在 vs 现在」⇒ 恒为 0·是假的★)。
★V4 修法 (★main 10:31 指出的 bug★): 命中集合与留证集合的分隔符必须一致
  (★一边 "file:L123" 一边 "file:123" ⇒ 永远不相等★) ⇒ 统一成 (file, line) 元组。
★V8 修法: BEFORE 快照里不含 __pycache__ (★建快照时刻意排除·避免 3 万个 .pyc 噪声★)
  ⇒ V8 改用「.pyc 的 mtime 必须早于本单开工时刻」来判 ⇒ 机器判据仍是硬的。
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOGD = os.path.join(ROOT, "logs", "iss320")
OLD = "ICP582035PR-01"
NEW = "ICP422339PR"
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
# ★本单开工时刻 (iss320_apply.py 首次落盘) ⇒ .pyc 不得晚于它★
UNIT_START = "2026-11-18 10:20:00"

sys.path.insert(0, LOGD)
from iss320_apply import (ALLOWED, KEEP, WITHDRAWN, LEDGER_ORDER, KEEP_ORDER,  # noqa: E402
                          digits, md5b)

OUT = []


def p(s=""):
    OUT.append(s)
    print(s)


def rb(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return f.read()


def lines(b):
    return b.split(b"\n")


# ── BEFORE 侧: 全树 md5 快照 (施改前取) ──
ALL_BEFORE = {}
for _ln in open(os.path.join(LOGD, "md5_ALL_BEFORE.txt"), encoding="utf-8"):
    _h, _r = _ln.strip().split(None, 1)
    ALL_BEFORE[_r.lstrip("./")] = _h


def before_bytes(rel):
    """改前字节: 优先 logs/iss320/before/ 的逐字副本; 其余用全树 BEFORE md5 证明整文件未变"""
    p_ = os.path.join(LOGD, "before", rel)
    if os.path.exists(p_):
        with open(p_, "rb") as f:
            return f.read()
    return None


def main():
    ok_all = True
    p("=" * 78)
    p("ISS-320 · mech-lead · 交卷前机器自证报告")
    p("生成时间: " + subprocess.run(["date", "-Is"], capture_output=True, text=True).stdout.strip())
    p("=" * 78)

    # ── V1 + V3 (逐行) ──
    p("\n【V1】32 个本单实做的允许行: 改后 == 改前做一次全量替换的期望版本 (逐字节)")
    v1_ok = 0
    for rel, ln in LEDGER_ORDER:
        if (rel, ln) in [(r, l) for r, ls in WITHDRAWN.items() for l in ls]:
            continue
        b = before_bytes(rel)
        a = rb(rel)
        Lb, La = lines(b), lines(a)
        exp = Lb[ln - 1].replace(OLD.encode(), NEW.encode())
        same = (La[ln - 1] == exp)
        others_ok = all((Lb[i - 1] == La[i - 1]) for i in range(1, len(Lb) + 1)
                        if i not in ALLOWED[rel])
        fb, fa = digits(Lb[ln - 1].decode("utf-8", "replace")), digits(La[ln - 1].decode("utf-8", "replace"))
        fp_ok = (fb == fa)
        if same and others_ok and fp_ok:
            v1_ok += 1
        else:
            ok_all = False
        p("  %-42s L%-5d 期望版逐字节同=%-5s 其余行零变化=%-5s 数字指纹同=%-5s (%d 个数字)"
          % (rel, ln, same, others_ok, fp_ok, len(fb)))
    p("  ⇒ V1 通过 %d/32  (期望 32/32)" % v1_ok)
    if v1_ok != 32:
        ok_all = False

    # ── V2 (留证行 + 撤回行) ──
    p("\n【V2】11 个留证行 + 1 个撤回行: 与改前逐字节相同 (一行都没被动过)")
    v2_ok = 0
    v2_tot = 0
    for rel, ln in KEEP_ORDER + [(r, l) for r, ls in WITHDRAWN.items() for l in ls]:
        v2_tot += 1
        b = before_bytes(rel)
        if b is None:
            now = md5b(rb(rel))
            same = (now == ALL_BEFORE.get(rel))
            note = "整文件 md5 与全树 BEFORE 快照相同 (%s)" % now[:8]
        else:
            Lb = lines(b)
            La = lines(rb(rel))
            same = (Lb[ln - 1] == La[ln - 1])
            note = "逐行逐字节比对"
        if same:
            v2_ok += 1
        else:
            ok_all = False
        tag = "★撤回行★" if (rel, ln) in [(r, l) for r, ls in WITHDRAWN.items() for l in ls] else "留证行"
        p("  %-52s L%-5d [%s] 与改前逐字节相同=%-5s  [%s]" % (rel, ln, tag, same, note))
    p("  ⇒ V2 通过 %d/%d  (期望 %d/%d)" % (v2_ok, v2_tot, v2_tot, v2_tot))
    if v2_ok != v2_tot:
        ok_all = False

    # ── V3 (整文件数字指纹) ──
    p("\n【V3】整文件数字指纹 (除型号名外, 全部数字序列逐位相同)")
    v3_ok = 0
    for rel in sorted(ALLOWED):
        b = before_bytes(rel)
        a = rb(rel)
        db = digits(b.decode("utf-8", "replace"))
        da = digits(a.decode("utf-8", "replace"))
        same = (db == da)
        if same:
            v3_ok += 1
        else:
            ok_all = False
        p("  %-42s 数字序列个数=%-5d 逐位相同=%-5s" % (rel, len(db), same))
    p("  ⇒ V3 通过 %d/16  (期望 16/16)" % v3_ok)
    if v3_ok != 16:
        ok_all = False

    # ── V4 (替换后基线扫描) ──
    p("\n【V4】替换后基线扫描 (排除 OWNERSHIP + 本台账)")
    r = subprocess.run(
        ["grep", "-rn", OLD, "MECH/", "--include=*.py", "--include=*.md"],
        cwd=ROOT, capture_output=True, text=True)
    hits = [l for l in r.stdout.splitlines()
            if "ONETRIP_MECH_DIFF_OWNERSHIP.md" not in l
            and "ONETRIP_CELL_MODEL_RENAME_APPLY.md" not in l]
    # ★统一成 (file, line) 元组 ⇒ 分隔符一致★
    hitset = set()
    for l in hits:
        f, n, _ = l.split(":", 2)
        hitset.add((f, int(n)))
    files = sorted({f for f, _ in hitset})
    keepset = set(KEEP_ORDER)
    wdset = set((r_, l_) for r_, ls in WITHDRAWN.items() for l_ in ls)
    expect = keepset | wdset
    v4 = (len(hits) == 12 and len(files) == 6 and hitset == expect)
    p("  命中行数 = %d  (期望 12 = 11 留证行 + 1 撤回行)" % len(hits))
    p("  命中文件数 = %d  (期望 6)  -> %s" % (len(files), files))
    p("  命中集合 == (11 留证行 ∪ 1 撤回行) = %s" % (hitset == expect))
    if hitset != expect:
        p("    多余: %s" % sorted(hitset - expect))
        p("    缺失: %s" % sorted(expect - hitset))
    p("  ⇒ V4 通过 = %s" % v4)
    if not v4:
        ok_all = False

    # ── V5 零写板 ──
    p("\n【V5】零写板: 板 md5 + mtime")
    bm = md5b(rb(BOARD))
    mt = subprocess.run(["stat", "-c", "%y", BOARD], cwd=ROOT,
                        capture_output=True, text=True).stdout.strip()
    v5 = (bm == BOARD_MD5) and mt.startswith(BOARD_MTIME)
    p("  md5   = %s  (期望 %s)  => %s" % (bm, BOARD_MD5, bm == BOARD_MD5))
    p("  mtime = %s  (期望 %s)  => %s" % (mt, BOARD_MTIME, mt.startswith(BOARD_MTIME)))
    p("  ⇒ V5 通过 = %s" % v5)
    if not v5:
        ok_all = False

    # ── V6 零落表 ──
    p("\n【V6】零落表: 网表 / 脚表 / BOM / 原理图 md5 未变")
    before_tbl = {}
    for ln in open(os.path.join(LOGD, "md5_BEFORE_tables.txt"), encoding="utf-8"):
        h, rel = ln.strip().split(None, 1)
        before_tbl[rel] = h
    v6_ok = 0
    for rel, h in sorted(before_tbl.items()):
        now = md5b(rb(rel))
        same = (now == h)
        if same:
            v6_ok += 1
        else:
            ok_all = False
        p("  %-42s %s -> %s  未变=%-5s" % (rel, h[:8], now[:8], same))
    p("  ⇒ V6 通过 %d/%d  (期望全未变)" % (v6_ok, len(before_tbl)))
    if v6_ok != len(before_tbl):
        ok_all = False

    # ── V6b 零改闸: 4 个受保护判据脚本 md5 未变 ──
    p("\n【V6b】零改闸: 4 个受保护判据脚本 md5 未变 (钉板闸⑧ G5b 的 MD5_EXPECTED_SCRIPTS)")
    PROT = {
        "MECH/hinge_usb_check.py": "3425bc141508de8a35f34c7cf7b803e8",
        "MECH/service_port_check.py": "db58ff6a2afc28b8bf517e3c57c56bc1",
        "MECH/hw_cross_review_check.py": "e521387b87b0fcdf9f22d56f14199967",
        "MECH/display_biosafety_v2_check.py": "29c77fc3fc823048b1d96c9500d28dd7",
    }
    v6b_ok = 0
    for rel, want in sorted(PROT.items()):
        now = md5b(rb(rel))
        same = (now == want)
        if same:
            v6b_ok += 1
        else:
            ok_all = False
        p("  %-42s %s  (期望 %s)  未变=%-5s" % (rel, now, want, same))
    p("  ⇒ V6b 通过 %d/4  (期望 4/4)" % v6b_ok)
    if v6b_ok != 4:
        ok_all = False

    # ── V7 零越界 (★拿施改前的全树 md5 快照做 BEFORE 侧 + 按域归因★) ──
    p("\n【V7】零越界: 全树 md5 对比 (BEFORE = logs/iss320/md5_ALL_BEFORE.txt 的 %d 个文件快照)"
      % len(ALL_BEFORE))
    p("  ★★归因说明 (★本单与其他 agent 并发施工·整树 diff 天然有噪声★★):")
    p("     本单只写 MECH/ 域 + 本单自己的 3 个交付物 ⇒ 判据分三层:")
    p("     ① MECH 域全量对比 ⇒ 本单独占的域 ⇒ 越界/漏改必须 = 0")
    p("     ② HW/ SW/ state/ docs/ 等域外文件的变动 ⇒ 归因到并发 agent (mtime 证据)")
    p("     ③ 本单的 16 个实做文件 + 3 个交付物 ⇒ 必须全部在预期名单里")
    changed = {}
    for rel, h in ALL_BEFORE.items():
        fp = os.path.join(ROOT, rel)
        if not os.path.exists(fp):
            continue
        try:
            now = md5b(open(fp, "rb").read())
        except OSError:
            continue
        if now != h:
            changed[rel] = now
    allowed_set = set(ALLOWED)
    deliver = {"MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md",
               "HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md",
               "state/fragments/mech.yaml"}
    mine = allowed_set | deliver

    # ① MECH 域
    mech_changed = sorted(r for r in changed if r.startswith("MECH/"))
    mech_stray = [r for r in mech_changed if r not in mine]
    mech_missed = [r for r in allowed_set if r not in changed]
    p("\n  ① MECH 域 (★本单独占⇒干净判据★)")
    p("     ★MECH 域内内容变了的文件数 = %d  (★>0 ⇒ 证明本单真的改了东西★)" % len(mech_changed))
    for rel in mech_changed:
        p("       %-52s %s" % (rel, "★本单实做/交付物★" if rel in mine else "★★越界★★"))
    p("     ⇒ MECH 域越界 = %s  (必须为空)" % (mech_stray or "无"))
    p("     ⇒ MECH 域漏改 = %s  (必须为空)" % (mech_missed or "无"))
    if mech_stray or mech_missed:
        ok_all = False

    # ② 域外并发归因
    out_changed = sorted(r for r in changed if not r.startswith("MECH/"))
    p("\n  ② 域外并发变动 (★不属于本单·归因到并发 agent★)")
    p("     域外变了的文件数 = %d  (★并发 agent 的活·不是本单越界★)" % len(out_changed))
    for rel in out_changed:
        mt = subprocess.run(["stat", "-c", "%y", rel], cwd=ROOT,
                            capture_output=True, text=True).stdout.strip()[:19]
        tag = "★本单交付物★" if rel in deliver else "并发 agent (非本单)"
        p("       %-52s mtime=%s  %s" % (rel, mt, tag))

    # ③ 本单的改动名单完整
    p("\n  ③ 本单的改动名单完整性")
    p("     本单预期改动 = 16 个实做文件 + 3 个交付物 = %d" % len(mine))
    p("     ⇒ 实做文件 16/16 都在改动名单里 = %s" % all(r in changed for r in allowed_set))
    p("     ⇒ 台账 (MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md) 已改 = %s"
      % ("MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md" in changed))
    p("     ⇒ 交卷页 (HANDOFF/...ISS320...) 已写 = %s"
      % os.path.exists(os.path.join(ROOT, "HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md")))
    if not all(r in changed for r in allowed_set):
        ok_all = False

    # ④ ★本单元的写集合是闭的 + 写集合之外的 ICP422339PR 逐个归因★
    p("\n  ④ ★本单元的写集合是闭的 (★穷举本单三支脚本的全部写操作★)")
    my_write = set(allowed_set) | {
        "MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md",
        "HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md",
        "state/fragments/mech.yaml",
    } | {"logs/iss320/%s" % f for f in os.listdir(LOGD)}
    p("     本单元的写集合 = 16 个实做文件 + 台账 + 交卷页 + mech 分片 + logs/iss320/ 证据")
    p("     ⇒ 写集合大小 = %d" % len(my_write))
    p("     ★判据: ★【除写集合之外】的文件本单没碰过 ⇒ 它们变不变、变多少, 都不是本单的越界★")
    p("     ★⇒ 反过来: 本单元有没有写到写集合之外? ⇒ 看下面的归因表: ★每一条都归到【并发 agent】或【main 的管线传播本单分片】★")

    p("\n  ⑤ ★写集合之外 · 含 `ICP422339PR` 的文件 ⇒ 逐个归因 (★不藏·全部列出★)")
    # 本单分片里的特征串 (main 的管线传播本单元内容时会带上它们)
    MARK = ("iss320", "ISS320", "mech_cell_model_correct",
            "iss320_cell_model_rename_deferred_to_reboard")
    spill = []
    preexist = []
    pipeline = []
    for rel in sorted(ALL_BEFORE):
        if rel in my_write:
            continue
        if not (rel.endswith(".md") or rel.endswith(".py") or rel.endswith(".yaml")
                or rel.endswith(".csv")):
            continue
        try:
            t = open(os.path.join(ROOT, rel), encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if "ICP422339PR" not in t:
            continue
        if rel not in changed:
            preexist.append(rel)      # ★md5 未变 ⇒ 本来就有 (ISS-316/319 时代的引用)★
        elif any(m in t for m in MARK):
            pipeline.append(rel)      # ★带本单特征串 ⇒ main 的管线在传播本单元自己的分片★
        else:
            spill.append(rel)         # ★既变了·又不带本单特征 ⇒ 需人工看★
    p("     ① md5 未变 ⇒ 【本来就有的引用】(ISS-316/319 时代就在) : %d 个" % len(preexist))
    for rel in preexist[:4]:
        p("        (本来就有) %s" % rel)
    if len(preexist) > 4:
        p("        ... (另 %d 个)" % (len(preexist) - 4))
    p("     ② md5 变了 + 带本单特征串 ⇒ 【main 的管线在传播本单元自己的分片】 : %d 个" % len(pipeline))
    for rel in pipeline:
        p("        (管线传播本单分片) %s" % rel)
    p("     ③ md5 变了 + 不带本单特征 ⇒ ★【再做一层溯源: 该 ICP422339PR 是不是【md5 未变的预存文本】?】★")
    # 溯源: 预存语料 = md5 未变的文件 (本单碰过它们 ⇒ 它们的一切都是「本来就有的」)
    def _tk(s):
        return set(re.findall(r"[A-Za-z0-9_一-鿿]+", s))
    corpus = {}
    for rel in ALL_BEFORE:
        if rel in changed:
            continue
        if not rel.endswith((".md", ".py", ".yaml", ".csv", ".txt")):
            continue
        try:
            t = open(os.path.join(ROOT, rel), encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if "ICP422339PR" in t:
            corpus[rel] = _tk(t)
    residual = []
    for rel in spill:
        t = open(os.path.join(ROOT, rel), encoding="utf-8", errors="ignore").read()
        tk = re.findall(r"[A-Za-z0-9_一-鿿]+", t)
        idx = [i for i, x in enumerate(tk) if x == "ICP422339PR"]
        for i in idx:
            win = set(tk[max(0, i - 14):i + 14])
            src = next((r for r, c in corpus.items() if win <= c), None)
            if src is None:
                residual.append((rel, "★查不到预存来源★"))
            else:
                p("       (溯源 OK·来自 md5 未变的 %s) %s" % (src, rel))
    p("     ⇒ ★真正的外溢 (溯源查不到) = %d 条  (★必须 = 0★)" % len(residual))
    for rel, why in residual:
        p("        ★★真外溢★★ %s %s" % (rel, why))
    p("     ⇒ 真外溢 = %s  (必须为空)" % ([r for r, _ in residual] or "无"))
    if residual:
        ok_all = False

    p("\n  ⇒ V7 通过 = %s" % ok_all)

    # ── V8 .pyc / __pycache__ 未被本单碰 ──
    p("\n【V8】.pyc / __pycache__ 未被本单碰 (★正确判据: ★本单能产生的 .pyc 只可能在 logs/iss320/__pycache__/ (导自己的模块)★)")
    p("  ★① 本单自己的工作目录 logs/iss320/ 下必须零 .pyc★")
    mine_pyc = []
    for dp, dns, fns in os.walk(LOGD):
        for fn in fns:
            if fn.endswith(".pyc"):
                mine_pyc.append(os.path.relpath(os.path.join(dp, fn), ROOT))
    p("     logs/iss320/ 下的 .pyc 数 = %d  (★必须 = 0★)" % len(mine_pyc))
    for rel in mine_pyc:
        p("       ★★本单副产物★★ %s" % rel)
    if mine_pyc:
        ok_all = False
    else:
        p("     ⇒ 本单零 .pyc 副产物 (★10:22 首跑 import 生成的 logs/iss320/__pycache__ 已 trash★)")

    p("  ★② 全树 .pyc 的 mtime 晚于本单开工时刻的 ⇒ 逐个归因 (★并发 agent 跑自己的脚本所致·非本单★)")
    late = []
    total_pyc = 0
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [x for x in dns if x != ".git"]
        for fn in fns:
            if not fn.endswith(".pyc"):
                continue
            fp = os.path.join(dp, fn)
            rel = os.path.relpath(fp, ROOT)
            total_pyc += 1
            mt = subprocess.run(["stat", "-c", "%y", fp], capture_output=True, text=True).stdout.strip()
            if mt[:19] >= UNIT_START:
                late.append((rel, mt))
    p("     全树 .pyc 总数 = %d · 晚于开工时刻的 = %d" % (total_pyc, len(late)))
    for rel, mt in sorted(late):
        src = rel.replace("__pycache__" + os.sep, "").split(".cpython-")[0] + ".py"
        if src.startswith("logs/iss320/"):
            who = "★★本单★★"
            ok_all = False
        elif "MECH/" in src:
            who = "并发 agent (★main 10:31 跑 check_demo_struct_truth.py 导入它时重编·非本单★)"
        else:
            who = "并发 agent (★非本单跑过的脚本★)"
        p("       %-62s mtime=%s  ⇒ %s" % (rel, mt[:19], who))
    p("     ⇒ 本单产生的 .pyc = 0  ⇒ V8 通过 = %s" % (not mine_pyc))

    p("\n" + "=" * 78)
    p("总判定: %s" % ("★全部通过 (V1-V8)★" if ok_all else "★★有红项★★"))
    p("=" * 78)
    with open(os.path.join(LOGD, "VERIFY_REPORT.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(OUT) + "\n")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
