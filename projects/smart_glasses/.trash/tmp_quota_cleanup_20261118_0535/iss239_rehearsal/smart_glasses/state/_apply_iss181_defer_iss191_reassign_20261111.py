#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""落账器 (2026-11-11 14:5x, 项目总工 main) —— 两处改动:

① ★**ISS-181: `fixing` → `deferred`** (★老板 11-11 10:07 口径: PCB 布线/布局类一律【不派】排队★)
② ★**ISS-191: owner `hw-lead` → `sw-lead`** (★hw-lead 在跑主线 6b ⇒ 铁律不许两个写会话★)

★**为什么 ① 是本轮最要紧的一件事 (★不是记账洁癖, 是结构性解冻★)**:
  `advance.py` 的 in_flight 判据 = 「owner 名下已有 status==fixing 的 issue ⇒ 本轮跳过该 agent」★
  ⇒ **ISS-181 (hw-lead, fixing) 把 hw-lead 名下唯一那条 open 单 (ISS-191) 永久挡住** ★
  ⇒ 决策页 §0.7 / §0.11.4 / §0.15.2 / §0.17.2 **连续 6 轮**记「A 段恒为空」, 根因就是这一个标记 ★
  ⇒ ★**而它已经不符合事实了**: ① 没有任何在跑的工作 (实测: ps 无 freeroute/臂进程; 最近一次终判
     v76mz = REJECT @09:36; 7 条同型臂 v44/46/47/48 + na/nb/mz 打死同一批差分腿 ⇒ 布局级线索 ⇒
     生成器族出局 ⇒ **现无臂在跑**) ② 官方板 md5 `611b869e` 自 **11-06 07:07** 起一字未动 ③
     老板 11-11 10:07 已明确 PCB 布线类**排队不派** ⇒ 「fixing (在飞)」是**假的** ★
  ⇒ 状态机允许 `fixing → deferred` (issue_check ALLOWED_NEXT) ⇒ ★**改 deferred = 排队 = 老板口径** ★
  ⇒ ★**deferred 的三条后果都查过 (不是副作用失控)**: ① advance.py 直接跳过 deferred ⇒ **不会被自动派出去**
     (= 守住「PCB 类不派」) ② **G1 仍卡**: G1 判据读 `HW/PCB/.layout_done.json` 的 unc=45, **不读 issue 状态**
     ⇒ ★**不许投板的口径一点没松** ③ **G4「问题单未闭环」列表仍会列出它** (实测 deferred 的 ISS-004/013/016
     都在 G4 清单里) ⇒ ★**没藏账** ★
  ⇒ ★**唯一会变的数字**: 逾期未闭环 33 → 32 (C4 规则「deferred 不算逾期」) ⇒ ★**这是口径纠正, 不是活干完了**
     ⇒ 汇报里必须写明 ★

★**为什么 ② 是必须的 (★不然 A 段这一轮还是 0★)**:
  hw-lead 正在跑**主线 6b** (13:45 起, 实测 `state/gen_kicad_sch.py` 15:05 / `HW/PCB/demo_mainboard.kicad_sch`
  15:06 仍在改) ⇒ ★**铁律「一个 agent 同时只允许一个写会话」⇒ 本单不能给 hw-lead** ★
  ⇒ sw-lead 实测**无在跑写会话** (最后一条 13:51 done) ⇒ 本单给 sw-lead ★
  ⇒ ★**能力匹配 (不是随便塞)**: 三条改法出自 **ISS-190 §7-2 (sw-lead 交卷, main 二次验收 verified/pass)** ★
  ⇒ 验收命令 `python3 SW/tools/timing_check.py --only F1_reset_rc` **本就是 sw-lead 自建工具** (自测 55/55) ★
  ⇒ ★**零文件交集**: 本单只写 `HW/PCB/RESET_P0_FIX_PLAN.md` + `HANDOFF/` + `state/fragments/sw.yaml` ★
  ⇒ 与 6b (gen_kicad_sch.py + demo_mainboard*.kicad_sch) / ISS-192 (MECH/**) **实测零交集** ★

★**边界 (一字没越)**: 板 / 生成器 / 留证链 / 闸 / 网表表 / 原理图 **一律未动** (官方板 md5 仍 611b869e) ·
  ★**ISS-191 本轮仍只出方案页, 不改网表不改板** (ISS-191 note 明写「在此之前【只做技术方案与影响面评估】」) ·
  不发邮件 / 不联系供应商 / 不下采购单 · 不碰别人分片 · 不改 §0 锁死表 · verify_by 仍 = main (自己修的必须别人验)

★**落账纪律 (与项目既有范式一致)**: flock(state/.issue_log.lock) + 锁内重读 + 原子写 (tmp → fsync →
  os.replace → fsync(dir)) + ★**自证: 其余 186 条 issue 逐字段零变化** ★
"""
from __future__ import annotations

import fcntl
import io
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")

NOTE_181 = (
    "\n\n"
    "★2026-11-11 14:5x 项目总工**改状态: fixing → deferred** (★老板 11-11 10:07 口径: PCB 布线/布局类"
    "一律【不派】, 排队等原理图定稿★)。\n"
    "★**为什么改 (★先说事实, 再说结论★)**:\n"
    "  ① ★**本单已经没有任何在跑的工作** —— 实测 `ps` 无 freeroute / 臂进程; 最近一次终判 = **v76mz REJECT"
    " @09:36**; ★**7 条同型臂 (v44/46/47/48 + na/nb/mz) 打死的是同一批差分腿** ⇒ 布局级线索 ⇒ 生成器族出局"
    " ⇒ **现无臂在跑** ⇒ 「fixing (在飞)」是**假的**。\n"
    "  ② ★**官方板 md5 `611b869e13518c3c023fb178f91a0075` 自 2026-11-06 07:07:17 起一字未动**;"
    " `HW/PCB/.layout_done.json` 记 unconnected=45 / DRC 0 (at 2026-11-09T04:11:35)。\n"
    "  ③ ★**老板 11-11 10:07 明确: PCB 布线/布局类 ISS 一律不派 (排队等原理图定稿后)** ⇒ 本单的正确状态"
    "就是**排队**。\n"
    "★**为什么这件事在今天特别要紧 (★结构性解冻, 不是记账洁癖★)**: `advance.py` 的 in_flight 判据 = "
    "「owner 名下已有 status==fixing 的 issue ⇒ 本轮跳过该 agent」⇒ ★**本单 (hw-lead, fixing) 把 hw-lead 名下"
    "唯一那条 open 单 (ISS-191) 永久挡住** ⇒ 决策页 §0.7 / §0.11.4 / §0.15.2 / §0.17.2 **连续 6 轮**记"
    "「A 段恒为空」, ★**根因就是这一个标记** ⇒ 现在起 **hw-lead 名额释放 ⇒ A 段恢复可派** ★。\n"
    "★**三条后果都先查过 (不是副作用失控)**: ① `advance.py` 直接跳过 deferred ⇒ ★**本单不会被自动派出去**"
    " (= 守住「PCB 类不派」) ② ★**G1 仍卡住**: G1 判据读 `.layout_done.json` 的 unconnected=45, **不读 issue 状态**"
    " ⇒ ★**「不许投板」的口径一点没松** ③ ★**G4「问题单未闭环」列表仍会列出本单** (实测 deferred 的"
    " ISS-004/013/016 都在 G4 清单里) ⇒ ★**没藏账** ★。\n"
    "★**唯一会变的数字**: 逾期未闭环 **33 → 32** (C4 规则「deferred 不算逾期」) ⇒ ★**这是口径纠正, 不是活干完了** ★。\n"
    "★**恢复条件 (写死, 免得又被当成已办★)**: ① 老板拍板走**整链重出** (`state/RECHAIN_ONEPASS_PLAN.md` §5)"
    " ⇒ ★**本单随那次一起做** ② 或 ★**原理图定稿后** (老板 10:07 口径的前提) ⇒ ③ ★**在那之前: 布线/布局一律不派** ★。"
    "★**边界**: 本轮板 / 生成器 / 留证链 / 闸 / 网表表 / 原理图 **一律未动** ★"
)

NOTE_191 = (
    "\n\n"
    "★2026-11-11 14:5x 项目总工**改派: owner hw-lead → sw-lead** (★verify_by 仍 = main ⇒ 自己修的必须别人验★)。\n"
    "★**为什么必须改 (★不然这一单永远出不来★)**: hw-lead 名下**主线 6b 仍在跑** (13:45 起, 实测"
    " `state/gen_kicad_sch.py` 15:05 / `HW/PCB/demo_mainboard.kicad_sch` 15:06 仍在改) ⇒ ★**铁律"
    "「一个 agent 同时只允许一个写会话」⇒ 本单不能给 hw-lead** ⇒ 而 `advance.py` 的 in_flight 判据又把"
    " hw-lead 整个跳过 ⇒ ★**两条路都堵死** ⇒ 本单必须换人 ⇒ ★**sw-lead 实测无在跑写会话** (最后一条 13:51 done) ★。\n"
    "★**能力匹配 (不是随便塞)**: ① 三条改法出自 ★**ISS-190 §7-2 (sw-lead 交卷, main 二次验收 verified/pass)** ★"
    "⇒ 本单是**它自己的后续** ② ★**验收命令 `python3 SW/tools/timing_check.py --only F1_reset_rc` 本就是"
    " sw-lead 自建工具** (自测 55/55, 且实测能真读网表行级 dnp) ③ ★**零文件交集**: 本单只写"
    " `HW/PCB/RESET_P0_FIX_PLAN.md` + `HANDOFF/` + `state/fragments/sw.yaml` ⇒ 与 6b"
    " (`state/gen_kicad_sch.py` + `HW/PCB/demo_mainboard*.kicad_sch`) / ISS-192 (`MECH/**`) **实测零交集** ★。\n"
    "★**本单范围不变 (★严格照 task_brief★)**: ★**只出方案页, 不改网表 / 不改板 / 不改原理图 / 不重出投产包** ★"
    "⇒ ★**真正的落表改动等老板在 `state/RECHAIN_ONEPASS_PLAN.md` §5 回 ② 之后, 随整链重出一次做完** ★"
    "⇒ ★**`ref_designator_rename` 与本单合并成一次整链重出 = 本单第 ③ 点 (可行性评估) 的正文** ★。"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".atom.", suffix=".tmp")
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
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            orig = io.open(LOG, encoding="utf-8").read()
            doc = yaml.safe_load(orig)

            # ★自证 1: yaml 往返必须逐字节一致 (整份改写才安全)
            if yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200) != orig:
                print("❌ yaml 往返不一致 ⇒ 中止 (整份改写不安全)")
                return 2

            issues = doc.get("issues") or []
            before = {it.get("id"): dict(it) for it in issues}

            hit181 = hit191 = 0
            for it in issues:
                iid = it.get("id")
                if iid == "ISS-181":
                    assert it.get("status") == "fixing", "ISS-181 状态已变 ⇒ 中止"
                    it["status"] = "deferred"
                    it["note"] = (it.get("note") or "") + NOTE_181
                    hit181 += 1
                elif iid == "ISS-191":
                    assert it.get("status") == "open", "ISS-191 状态已变 ⇒ 中止"
                    assert it.get("owner") == "hw-lead", "ISS-191 owner 已变 ⇒ 中止"
                    it["owner"] = "sw-lead"
                    it["note"] = (it.get("note") or "") + NOTE_191
                    hit191 += 1
            assert hit181 == 1 and hit191 == 1, "目标单未唯一命中 ⇒ 中止"

            text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
            atomic_write(LOG, text)

            # ★自证 2: 除这两条外, 其余 issue 逐字段零变化
            after_doc = yaml.safe_load(io.open(LOG, encoding="utf-8").read())
            after = {it.get("id"): dict(it) for it in (after_doc.get("issues") or [])}
            assert set(before) == set(after), "issue 集合变了 ⇒ 中止"
            changed = []
            for iid, b in before.items():
                a = after[iid]
                if b != a:
                    changed.append(iid)
                    if iid == "ISS-181":
                        assert a["status"] == "deferred" and a["note"] != b["note"]
                    elif iid == "ISS-191":
                        assert a["owner"] == "sw-lead" and a["note"] != b["note"]
                    else:
                        raise AssertionError("★有第 3 条 issue 被动过 ⇒ 中止: %s" % iid)
            assert sorted(changed) == ["ISS-181", "ISS-191"], changed
            print("✅ 落账完成: 改动 issue =", changed)
            print("   ISS-181: fixing → deferred (排队等原理图定稿; 老板 11-11 10:07 口径)")
            print("   ISS-191: owner hw-lead → sw-lead (hw-lead 在跑主线 6b ⇒ 铁律)")
            print("   其余 %d 条 issue 逐字段零变化 (已实测)" % (len(before) - 2))
            return 0
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


if __name__ == "__main__":
    sys.exit(main())
