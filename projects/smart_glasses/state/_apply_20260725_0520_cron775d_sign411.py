#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★_apply_20260725_0520_cron775d_sign411.py★

★**job**: cron `775d9893` (ARS45 继续执行后继计划 · 每 20 分钟) · 2026-11-25 05:11~05:3x
★**做什么**: ① 签收 ISS-411 (sw-lead) —— main 本机独立复核, 不抄任何 agent 报告

★**铁律**:
  - ① 零写板 / 零落表 (只动 issue_log) / 零改既有闸 / 零改既有页正文 / 零挂链 / 零外发
  - ② CAS 守卫 A (★本单自身★): ISS-411 条目 md5 必须 == EXPECT_ENTRY_MD5 且 status == `fixing`
        ⇒ 若兄弟 job fb67af40 已抢先签收 (status 变 verified) 或改了本条 ⇒ **本脚本当场放弃写入并报「不重复签收」**
        ⇒ ★**绝不覆盖别人的签收内容**★
  - ③ CAS 守卫 B (★其余全部条目★): 逐条 yaml 序列化 md5 必须逐字不变
  - ④ 原子写: 先写 .tmp 再 os.replace + 备份
  - ⑤ 幂等: 已 verified ⇒ 跳过
"""
import hashlib
import os
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

NOW = "2026-11-25 05:2x"

# ★★CAS 守卫 A 的锚点 (★main 05:1x 本机实读的 ISS-411 条目 md5★)
EXPECT_ENTRY_MD5 = "1c3e7f44c1ac0c3172765dfca38bf507"

VERIFY_RESULT = (
    "✅ verified (★main 2026-11-25 05:1x~05:2x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
    "★**新闸 `SW/tools/check_sw_mustchange_face_impact.py` `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` "
    "(★反向用例 15/15 通过·main 实跑末两行逐字为「反向用例: 15/15 通过 (★每条都自证『红的集合 == {目标那一条}』★) / ALL TESTS PASS」★)** ★ ⇒ "
    "★**裸跑 rc=1 = 【红的是现状】(★判据结果 8/9 通过 · 唯一 FAIL = T4 命门: 链上两道闸硬编位号字面量 "
    "check_onepass_sw_sync.py(20 处) / check_sw_ref_reachability.py(55 处) ⇒ 位号改名那一趟一落地它们的判据就失效★)** ★ ⇒ "
    "★★**上一轮 (03:4x) 本 job 亲自记下的链上红已被本单修回绿**: `python3 SW/tools/check_sw_ref_reachability.py` ⇒ "
    "**rc=0** (★真隐患 C14 实测 3 条 = 基线上限 3 条 ⇒ 在基线内·判决行逐字「【判决】 ✔ 绿 (rc=0): SW 侧引用的位号全部可达, 真隐患在基线内」★) "
    "⇒ ★**处置方式合规**: 只改本单自建真相页的写法 (3 个沙盒合成 token 改写成 `TP_INT_ISS_x`/`TP_TEMP_ISS_x`/`U_TEMP_` ⇒ 闸按 C7/C8 判成 DOC_INTERNAL) "
    "⇒ ★**零放宽 BASELINE_COUNT · 零往 BASELINE_TOKENS 塞新 token · 零改那道闸的任何判据**★ ★ ⇒ "
    "★**三件交付物在盘**: 交卷页 `HANDOFF/2026-11-25_sw-lead_ISS411_SW必改面影响面清账与闸.md` (31,039 B @03:41 · B1~B6 必填验收块齐全) + "
    "真相页 `SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md` (66,301 B @03:35 · cont1 的 66,293 B → cont2 的 66,301 B) + "
    "新闸 `SW/tools/check_sw_mustchange_face_impact.py` (39,727 B)★ ⇒ "
    "★**自有分片** `state/fragments/sw.yaml` 命中 7 处 (★走 frag_write.py 原子写·YAML 仍合法·键组 artifacts/interface_claims/needs_open_ledger/needs_from/answers★) + "
    "留证 `logs/iss411/` 21 件 (selftest / bare / merge / frag_selfcheck / probe_token_spelling / truth_page_before·after …)★ ⇒ "
    "★**板三证逐字节未动**: md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / mtime 2026-11-06 07:07:17.362193413 ⇒ 19 天未动 ⇒ "
    "★**零写板** · 网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 三表 md5 逐字未动 ⇒ **零落表** · "
    "`grep -c check_sw_mustchange_face_impact state/gate_check.py` = **0** ⇒ **零挂链** · `state/outbox/` 最新文件仍是 11-11 ⇒ **零外发**★ ⇒ "
    "★**本轮 main 实跑链上读数**: `state/merge.py` rc=0 (★产出 933 · 阻塞 43 · 冲突 0·本单新增 0 条阻塞★) · "
    "`state/gate_check.py` **rc=0** (★Q1 18/18 · Q2 3/3 · Q7 钉板 md5 闸链 10/10 · 缺口清单 3 条全是「需求还没人答」的计数项★) · "
    "`state/check_brief_commands.py --brief-file …cont2.md` rc=0 ★ ⇒ "
    "★★**签收只解「这一条已交卷 + 那条链上红已修回绿」, 不解「这道新闸已挂链」** ⇒ ★**挂链是 main 的地界 (零挂链是本单纪律·下一轮要么挂要么写清为什么不挂)** ★"
)

FIX_REF = (
    "main 2026-11-25 05:2x 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·零挂链·零外发·未代老板拍板★)"
)

NOTE_ADDENDUM = (
    "★★2026-11-25 05:2x cron 775d9893 (ARS45 继续执行后继计划) · main 独立复核签收 (★追加式·老字一字未删★)★★\n"
    "★本机实跑读数 (★不抄任何 agent 报告★)★: 新闸 `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` (反向 15/15) · "
    "★裸跑 rc=1 (★红的是现状: 8/9 通过 · 唯一 FAIL = T4 命门·设计意图★) · "
    "★`SW/tools/check_sw_ref_reachability.py` **rc=0** (★上一轮本 job 记下的那条链上红已修回绿·真隐患 3 = 基线内★) · "
    "★`state/gate_check.py` **rc=0** (Q1 18/18 · Q7 10/10) · `state/merge.py` rc=0 · brief 守卫 rc=0 · "
    "★交卷页 31,039 B + 真相页 66,301 B + 新闸 39,727 B + 自有分片 sw.yaml 命中 7 + 留证 logs/iss411/ 21 件 · "
    "★板 md5/mtime/size 三证与基线逐字相同 (19 天未动) ⇒ 零写板 · 零落表 · 零挂链 · 零外发 · 不代拍 · 不自签★\n"
    "★**签收只解「这一条已交卷 + 那条链上红已修回绿」, 不解「这道新闸已挂链」** ⇒ ★**挂链是 main 的地界 (三道新闸都写死零挂链·本轮未挂·下一轮要么挂要么写清为什么不挂)** ★"
)


def atomic_write(path, content):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def entry_md5(it):
    return hashlib.md5(
        yaml.safe_dump(it, allow_unicode=True, sort_keys=True, width=100).encode("utf-8")
    ).hexdigest()


def main():
    if not os.path.exists(LOG):
        print("FATAL: issue_log.yaml 不在", file=sys.stderr)
        return 2

    raw = open(LOG, encoding="utf-8").read()
    log = yaml.safe_load(raw)
    items = log if isinstance(log, list) else log.get("issues", [])
    before = {it.get("id"): entry_md5(it) for it in items if isinstance(it, dict)}

    # ---------- CAS 守卫 A ----------
    target = None
    for it in items:
        if isinstance(it, dict) and it.get("id") == "ISS-411":
            target = it
            break
    if target is None:
        print("FATAL: 台账里找不到 ISS-411", file=sys.stderr)
        return 3
    if target.get("status") == "verified":
        print("★ 跳过: ISS-411 已是 verified (★大概率已被兄弟 job fb67af40 签收 ⇒ 本轮不重复签、不覆盖★)")
        return 0
    cur_md5 = entry_md5(target)
    if cur_md5 != EXPECT_ENTRY_MD5:
        print(
            "★ 跳过: ISS-411 条目已被别人改动 (md5 %s ≠ 锚点 %s) ⇒ 本轮不写入、不覆盖 (★零破坏★)"
            % (cur_md5, EXPECT_ENTRY_MD5)
        )
        return 0

    # ---------- 签收 ----------
    target["status"] = "verified"
    target["verify_result"] = VERIFY_RESULT
    target["verify_date"] = NOW
    target["fix_ref"] = FIX_REF
    na = target.get("note_addendum")
    if not isinstance(na, list):
        na = []
    na.append(NOTE_ADDENDUM)
    target["note_addendum"] = na

    after = {it.get("id"): entry_md5(it) for it in items if isinstance(it, dict)}
    changed = sorted(k for k in before if before.get(k) != after.get(k))
    if changed != ["ISS-411"]:
        print(f"FATAL: CAS 守卫 B 失败 · 预期只动 ['ISS-411'] · 实际动了 {changed}", file=sys.stderr)
        return 3
    if set(before) != set(after):
        print("FATAL: 条目集合变了 (有增有删)", file=sys.stderr)
        return 3

    shutil.copy2(LOG, LOG + ".bak_20260725_0520_cron775d_sign411")
    atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=True, width=100))
    print(
        "★ issue_log.yaml: 签收 ISS-411 (★其余 %d 条逐条 md5 未变·备份 .bak_20260725_0520_cron775d_sign411★)"
        % (len(before) - 1)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
