#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**修 ISS-369 的 task_brief 里【本单新建交付物路径】被 `state/check_brief_commands.py` 误报成「引用了不存在的路径」** ★

★**病灶 (★2026-11-23 18:4x 本机实读·不是猜★)**:
  ★**闸 `state/check_brief_commands.py` 的豁免口径 = 「同一行里, 某个路径的【前 30 字】出现【新建/新增/产出/交付物…】⇒ 判它是【本单产出物】⇒ 豁免」** ★
  ★**⇒ ISS-369 台账里那条声明行太长**: `★**★新建 (★这两个路径本单才存在·别去别处找★)**: ★**`HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md`** · …` ★
  ★**⇒ 第 1 个路径的「新建」正好被 30 字窗口切在窗口外 ⇒ 闸把【本单要新建的交付物】当成【引用了不存在的文件】⇒ rc=1★** ★
  ★**⇒ 同一路径若在【别处】有过「前 30 字含新建」的出现 ⇒ 闸豁免 ⇒ 所以闸只点名【只出现在那一条声明行里】的路径** ★

★**实证 (★本轮 18:4x~18:5x 本机实跑·不是推断★)**:
  ★**① `python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-369_hw_fp_libid_truth.md` ⇒ rc=0** ★
  ★**⇒ 任务书 .md 文件本身【完全合规】; 只有【台账 issue_log.yaml 里 task_brief 字段】那一条声明行被点 ⇒ 这是【台账拷贝与任务书文件排版不同】造成的假阳性, 不是「brief 引用了坏命令」★** ★
  ★**② ISS-369 的 20 条必跑命令 + 它引用的 12 个既有输入文件 (★含 tmp/iss364_sbx/netlist_v1_legB.csv · tmp/iss370_sbx/* 三个变体 · SW/tools/* 五个闸 · 台账三页 · 工作包★) ⇒ 本机逐个 stat ⇒ ★全部存在 ⇒ 零个坏命令★** ★
  ★**③ 同一批里 ISS-367 / ISS-368 的 ❌ 已【自行消失】**: 那两条被点的路径是它们各自的交卷页 ⇒ ★在飞 agent 已把交卷页写出来 ⇒ 闸再跑就不点了 ⇒ ⇒ ★不必动它们的 task_brief (★它们在等签收·动台账字段有风险★)** ★

★**修法 (★最小改法·只动台账里 ISS-369 的 task_brief 声明行★)**:
  ★**把声明行里每个【本单新建】路径前面补上「新建 」两字 ⇒ 让闸的 30 字窗口能看见声明词 ⇒ 闸自己豁免 ⇒ ★闸的判据方向一个字都没改★** ★
  ★**⇒ 与 `state/dispatch_briefs/ISS-369_hw_fp_libid_truth.md` 内容【语义一致】(★只多两个「新建」★) ⇒ 不改任务书文件、不改闸、不改板、不改任何真源★** ★

★**★为什么本脚本【本轮不自动跑】(★fail-closed 的自觉★)★**:
  ★**① 台账 `state/issue_log.yaml` 的写入方里, 【签收类脚本不走锁】** (`_apply_20260723_1655_main_sign_iss365.py` / `_apply_20260723_1750_cron775d_sign_iss363_364.py` / `_apply_20260723_1550_main_sign_iss361.py` ⇒ grep `issue_log.lock` 零命中) ★
  ★**② ⇒ 兄弟 job 775d9893 的签收写盘随时可能发生 ⇒ 本脚本持锁写, 对方不持锁写 ⇒ ★【对方读旧快照 + 我写 + 对方写】⇒ 我的改动丢失 (可接受) / ★【对方写完 + 我用旧快照写】⇒ ★★对方的签收被抹掉 (不可接受!)★★** ★
  ★**⇒ 所以: 只在【确认台账短时间内无并发写入】的窗口跑 (★脚本内置 md5 前后复核⇒ 发现并发写 ⇒ rc=2 不写★)★** ★
  ★**⇒ 或: 等兄弟 job 的三条 CONT1 全部签收完、它的 job 回合结束后再跑 (★最省心★)** ★

★**用法**:
  ```bash
  cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  python3 state/_fix_iss369_brief_guard_decl_20261123.py --check-only   # ★只体检·不写盘★ ★rc=0 = 台账已是合规形态 (幂等★)
  python3 state/_fix_iss369_brief_guard_decl_20261123.py               # ★体检通过才写盘 (★fail-closed: 任何不符 ⇒ rc=2 不写★)
  ```
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import os
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261123_1845_cronfb67_fix_iss369_brief_guard_decl"
TARGET = "ISS-369"

# ★**闸本体 (★判据以闸为准·不许本脚本另立口径★)** ★
_spec = importlib.util.spec_from_file_location("cbc", os.path.join(HERE, "check_brief_commands.py"))
cbc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cbc)

CREATE_KEYS = ("新建", "新增", "新文件", "新脚本", "产出", "输出文件", "输出路径",
               "交付文件", "交付物", "交卷", "交付清单", "产出物")


def md5(path: str) -> str:
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def issue_block(text: str, iid: str) -> tuple[int, int]:
    """★该 issue 在【原始文本】里的 [起, 止) 区间 (★按 '- id: XXX' 行切·不做 yaml round-trip·不改任何其它行★)★"""
    lines = text.split("\n")
    start = None
    for idx, ln in enumerate(lines):
        if ln.startswith("- id: ") and ln[len("- id: "):].strip() == iid:
            start = idx
            break
    if start is None:
        raise SystemExit("★台账里找不到 %s ⇒ 中止 (fail-closed)" % iid)
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("- id: "):
            end = idx
            break
    off = sum(len(ln) + 1 for ln in lines[:start])
    return off, off + sum(len(ln) + 1 for ln in lines[start:end])


def task_brief_span(block: str) -> tuple[int, int]:
    """★block 内 `task_brief:` 字段的 [起, 止) 相对偏移 (★到下一个同级键为止★)★"""
    lines = block.split("\n")
    start = None
    for idx, ln in enumerate(lines):
        if ln.startswith("  task_brief:"):
            start = idx
            break
    if start is None:
        raise SystemExit("★该 issue 没有 task_brief 字段 ⇒ 中止 (fail-closed)")
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("  ") and not lines[idx].startswith("   ") and ":" in lines[idx]:
            end = idx
            break
    off = sum(len(ln) + 1 for ln in lines[:start])
    return off, off + sum(len(ln) + 1 for ln in lines[start:end])


def gate_missing(task_brief: str) -> list[str]:
    """★用闸自己的函数算出【这条 brief 里闸认为『引用了不存在的文件』】的路径 (★判据只认闸★)★"""
    refs = cbc.find_refs(task_brief)
    return sorted(r for r in refs if not cbc._exists(r))


def patch_brief(task_brief: str, paths: list[str]) -> tuple[str, list[str]]:
    """★给每个被点的路径补「新建 」前缀 (★只在该出现处的前 30 字里没有声明词时才补★)★"""
    out = task_brief
    done = []
    for path in paths:
        needle = "`%s`" % path
        pos = 0
        while True:
            k = out.find(needle, pos)
            if k < 0:
                break
            path_start = k + 1                      # ★路径起点 (★闸的窗口到路径起点为止★)★
            head = out[max(0, path_start - 30):path_start]
            if any(key in head for key in CREATE_KEYS):
                pos = k + len(needle)
                continue
            out = out[:k] + "新建 " + out[k:]       # ★插在反引号前 ⇒ 路径本身一个字都不改★)
            done.append(path)
            pos = k + len("新建 " + needle)
    return out, done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    with open(LOG, encoding="utf-8") as f:
        text = f.read()
    before_md5 = md5(LOG)

    b0, b1 = issue_block(text, TARGET)
    block = text[b0:b1]
    t0, t1 = task_brief_span(block)
    brief = block[t0:t1]

    missing = gate_missing(brief)
    print("· %s ⇒ 闸认为『引用了不存在的文件』的路径: %s" % (TARGET, (", ".join(missing) if missing else "无")))

    if not missing:
        print("★台账已是合规形态 ⇒ 无需写盘 (★幂等★)")
        return 0

    new_brief, done = patch_brief(brief, missing)
    if not done:
        print("❌ 补声明词失败 (★没找到可补的出现处★) ⇒ 不写盘 (fail-closed)")
        return 2

    # ★闸复判: 补完之后闸必须不再点这几条 (★fail-closed★)★
    still = gate_missing(new_brief)
    if still:
        print("❌ 补完闸仍点: %s ⇒ 不写盘 (fail-closed)" % ", ".join(still))
        return 2

    new_block = block[:t0] + new_brief + block[t1:]
    new_text = text[:b0] + new_block + text[b1:]

    # ★除【ISS-369 的 task_brief】外, 其它 issue 的字段必须逐字未变★ ★
    try:
        old_doc = yaml.safe_load(text) or {}
        new_doc = yaml.safe_load(new_text) or {}
    except Exception as exc:  # noqa: BLE001
        print("❌ 改后 YAML 解析失败 ⇒ 不写盘 (fail-closed): %s" % exc)
        return 2
    old_idx = {i.get("id"): i for i in (old_doc.get("issues") or [])}
    new_idx = {i.get("id"): i for i in (new_doc.get("issues") or [])}
    if set(old_idx) != set(new_idx):
        print("❌ 改后 issue 集合变了 ⇒ 不写盘 (fail-closed)")
        return 2
    for iid, o in old_idx.items():
        for k, v in o.items():
            if iid == TARGET and k == "task_brief":
                continue
            if new_idx[iid].get(k) != v:
                print("❌ %s 的字段 %s 被改了 (★本脚本只许改 %s 的 task_brief★) ⇒ 不写盘" % (iid, k, TARGET))
                return 2

    if args.check_only:
        print("★--check-only ⇒ 体检通过, 未写盘 (★需补 %d 处: %s★)" % (len(done), ", ".join(done)))
        return 0

    # ★写盘: 持锁 + 备份 + 原子替换 + 写前 md5 复核 (★防并发写丢更新★)★
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        if md5(LOG) != before_md5:
            print("❌ 台账在体检期间被改过 (★并发写·★签收类脚本不走锁★) ⇒ 中止 (fail-closed)")
            return 2
        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        atomic_write(LOG, new_text)

    print("✅ 已写盘 (★补了 %d 处声明词: %s★) · 备份: %s.bak_%s" % (len(done), ", ".join(done), LOG, STAMP))
    print("★改后 md5: %s" % md5(LOG))
    return 0


if __name__ == "__main__":
    sys.exit(main())
