#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-174 / ISS-209 落 verified + 放行 hw-lead / mech-lead 名额 (2026-11-15 22:4x, 项目总工 main)

★★**为什么要有这次落盘 (★实测, 不是推测★)** ★★:
· `state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 三个总工全被挡住
· ★**根因 = 2 条【僵尸 fixing 标记】**(★同病第 15 次复发★):
  · ISS-174 (hw-lead): 子会话 `agent:hw-lead:subagent:90b2b61e` (sessionId `0b291773`) **2026-11-15
    22:17:10 结束, status=done** ⇒ ★**交卷已投递、文件已落盘** ⇒ 但 ★**brief 明写「不许碰
    state/issue_log.yaml (改 issue 状态是 main 的活)」⇒ 子 agent 没落账 ⇒ status 停在 `fixing`** ★
  · ISS-209 (mech-lead): 子会话 `agent:mech-lead:subagent:732b1fa4` (sessionId `a5d32db3`) **2026-11-15
    22:21:57 结束, status=done** ⇒ ★**同上** ★
· ⇒ ★**`advance.py` 的 in_flight 规则 (★"该 agent 正在干别的, 本轮跳过"★) ⇒ hw-lead / mech-lead 名额被占住**
· ★**ISS-210 (sw-lead) 不是僵尸** —— 会话 `agent:sw-lead:subagent:b37f1504` **仍在跑** (★22:20 起 status=running★)
  ⇒ ★**本脚本绝不碰它** ★

★★**两条交卷我逐份独立复核过 (★不采信自述, 只看盘上实物 + 自己跑门禁★)** ★★:
· ISS-174 (hw-lead · TP_INT 改脚规格) ⇒ ★**真交卷** ★:
  ✅ 交付物齐: `HW/PCB/TP_INT_REMAP_SPEC.md` (44,194 B · 22:16) + `HW/check_tp_int_gap.py` (20,827 B · 22:08)
     + `HANDOFF/2026-11-15_hw-lead_ISS174_TPINT改脚规格.md` (10,129 B · 22:16)
  ✅ `python3 HW/check_tp_int_gap.py` **rc=0** (★"现状与 TP_INT_REMAP_SPEC.md 一致": CONN_LIGHT 22 脚齐 /
     网表无 TP_INT 网 / TP_RESET 仍挂 RESET_N / GPIO 池 36 脚 / 候选脚全空★)
  ✅ `python3 HW/check_tp_int_gap.py --selftest` **rc=0** (★5/5 含反向用例: 备选脚被占 ⇒ 池容量 -1 ⇒ rc=1★)
  ✅ md5 两件一字未变: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075`
  ✅ ★**本单只出规格, 不改网表/板/原理图** ⇒ 下游 `check_netlist_pins` / `check_pcb_nets` 链未被破坏 ★
· ISS-209 (mech-lead · 正中区腔体按眼盒 62mm² 重排) ⇒ ★**真交卷** ★:
  ✅ 交付物齐: `MECH/CENTER_CAVITY_RECALC.md` (24,293 B · 22:32) + `MECH/cavity_recalc_check.py` (32,023 B · 22:33)
     + `HANDOFF/2026-11-15_mech-lead_ISS209_正中区腔体重排.md` (5,526 B · 22:33)
  ✅ `python3 MECH/cavity_recalc_check.py` **rc=0** (★12/12: 含 C8 四个受保护 check 脚本 md5 未变 ·
     C9 分片 `mech_hinge_stack_fixed_mm` = 25.00 (U-3 已收) · C10 结构真源阈值未松 (0.1234/1500/4000/62/15-20/0.011) ·
     C11 分光件冲突量一致 (A_e=62 ⇒ 0.97 cc) · C12 边界声明齐全★)
  ✅ `python3 MECH/cavity_recalc_check.py --selftest` **rc=0** (★10/10 含反向 8/9: 篡改受保护脚本 / 改 ±3mm 带 均被抓★)
  ✅ md5 两件一字未变: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075`
  ✅ ★**未决 = d 取 15/18/20 需老板/判据侧拍** ⇒ ★**已由 main 升级进 C 段 (key `iss209_mech_d_value_decision`) ★
⇒ ★**处置 = 落 `verified` (★不是 closed★ ⇒ 留给 QA/verify 环节) ⇒ 放出 hw-lead / mech-lead 名额** ★

★★**落账纪律 (照 `state/_apply_iss199_fixed_20261115.py` 的同一套) ★★:
① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (★实测本文件往返一致 = True★)
③ 原子写 (tmp → fsync → os.replace → fsync(dir))
④ ★**只改 ISS-174 / ISS-209 两条**, 不动任何其它 issue (★ISS-210 绝不碰★)

★**边界**: 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 /
不下采购单 · 板 / 网表 / 原理图 / BOM 一个字节不动 · ★**只落 issue 状态, 不改任何设计产物** ★
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261115_2240_verify_174_209"

VERIFY = {
    "ISS-174": {
        "fix_ref": "HANDOFF/2026-11-15_hw-lead_ISS174_TPINT改脚规格.md",
        "res": (
            "pass · 2026-11-15 22:4x 项目总工独立复核 (★不采信自述★)\n"
            "★**① 交付物齐** [实测]: `HW/PCB/TP_INT_REMAP_SPEC.md` (44,194 B · 22:16) · "
            "`HW/check_tp_int_gap.py` (20,827 B · 22:08) · "
            "`HANDOFF/2026-11-15_hw-lead_ISS174_TPINT改脚规格.md` (10,129 B · 22:16)\n"
            "★**② 机器门禁** [实测]: `python3 HW/check_tp_int_gap.py` **rc=0** "
            "(★现状与规格一致: CONN_LIGHT 22 脚齐 / 网表无 TP_INT 网 / TP_RESET 仍挂 RESET_N / "
            "GPIO 池 36 脚 / 候选脚全空★) · `--selftest` **rc=0** (★5/5 含反向: 备选脚被占 ⇒ 池容量 -1 ⇒ rc=1★)\n"
            "★**③ 受保护文件 md5 一字未变** [实测]: 网表 `c78f991283cc82d56c8e3dd31657c785` · "
            "板 `611b869e13518c3c023fb178f91a0075`\n"
            "★**④ 边界**: 本单只出规格, 未改网表/板/原理图 ⇒ 下游 `check_netlist_pins` / `check_pcb_nets` 链未被破坏"
        ),
    },
    "ISS-209": {
        "fix_ref": "HANDOFF/2026-11-15_mech-lead_ISS209_正中区腔体重排.md",
        "res": (
            "pass · 2026-11-15 22:4x 项目总工独立复核 (★不采信自述★)\n"
            "★**① 交付物齐** [实测]: `MECH/CENTER_CAVITY_RECALC.md` (24,293 B · 22:32) · "
            "`MECH/cavity_recalc_check.py` (32,023 B · 22:33) · "
            "`HANDOFF/2026-11-15_mech-lead_ISS209_正中区腔体重排.md` (5,526 B · 22:33)\n"
            "★**② 机器门禁** [实测]: `python3 MECH/cavity_recalc_check.py` **rc=0** (★12/12: 含 C8 四个受保护 "
            "check 脚本 md5 未变 · C9 分片 `mech_hinge_stack_fixed_mm` = 25.00 (U-3 已收) · C10 结构真源阈值未松 "
            "(0.1234/1500/4000/62/15-20/0.011) · C11 分光件冲突量一致 (A_e=62 ⇒ 0.97 cc) · C12 边界声明齐全★) · "
            "`--selftest` **rc=0** (★10/10 含反向 8/9: 篡改受保护脚本 / 改 ±3mm 带 均被抓★)\n"
            "★**③ 受保护文件 md5 一字未变** [实测]: 网表 `c78f991283cc82d56c8e3dd31657c785` · "
            "板 `611b869e13518c3c023fb178f91a0075`\n"
            "★**④ 未决** = d 取 15/18/20 需老板/判据侧拍 ⇒ ★**已由 main 升级进 C 段 "
            "(key `iss209_mech_d_value_decision`) ★"
        ),
    },
}

NOTE = (
    "\n★**2026-11-15 22:4x 项目总工 (main) 落 `verified` (★清僵尸 fixing 第 15 次复发★)**:\n"
    "★**实测**: 子会话 status=**done** 且交卷文件已落盘 ⇒ ★**但 brief 不许子 agent 改 issue_log "
    "(改 issue 状态是 main 的活) ⇒ status 停在 `fixing`** ⇒ ★**`advance.py` 的 in_flight 规则 ⇒ "
    "该 agent 名额被永久占住** ⇒ ★**main 独立复核 (只看盘上实物 + 自己跑门禁) 通过 ⇒ 本单转 `verified`** ★\n"
    "★**边界**: 不改 §0 锁死表 · 不写别人的分片 · 不发信 · 板/网表/原理图/BOM 一个字节未动 ★\n"
)


def atomic_write(path: str, data: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".issue_log.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            raw = f.read()
        log = yaml.safe_load(raw)

        # ★自证: yaml 往返必须逐字节一致 (否则说明本文件格式与 safe_dump 不同 ⇒ 拒绝落盘, 不重排整份文件)
        rt = yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200)
        if rt != raw:
            print("❌ yaml 往返不一致 (%.d vs %d B) ⇒ 拒绝落盘" % (len(rt), len(raw)))
            return 2
        print("✅ yaml 往返逐字节一致 (自证通过)")

        issues = log.get("issues") or []
        by_id = {i.get("id"): i for i in issues}
        out = []
        for iid, rec in VERIFY.items():
            it = by_id.get(iid)
            assert it is not None, "%s 不存在" % iid
            assert it.get("status") == "fixing", "%s status=%s 非 fixing" % (iid, it.get("status"))
            assert it.get("owner") != "main", "%s owner=main 不能自验" % iid
            it["status"] = "verified"
            it["verify_by"] = "main"
            it["verify_result"] = rec["res"]
            it["verify_date"] = "2026-11-15 22:4x"
            it["fixed_at"] = "2026-11-15"
            it["fix_ref"] = rec["fix_ref"]
            it["note"] = (it.get("note") or "") + NOTE
            out.append("%s (%s) → verified (main 独立复核)" % (iid, it.get("owner")))

        # ★ISS-210 明确不碰 (真在飞)
        i210 = by_id.get("ISS-210")
        assert i210 is not None and i210.get("status") == "fixing", "ISS-210 状态异常, 拒绝落盘"
        out.append("ISS-210 (sw-lead) → 保持 fixing (★会话真在跑, 不碰★)")

        log["issues"] = issues
        shutil.copy2(LOG, BAK)
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        print("备份:", BAK)
        for line in out:
            print(" -", line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
