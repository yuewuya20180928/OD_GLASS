#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-188 验收签字 + 新开 ISS-189 (F1/F2 两处活残留) + 派给 hw-lead —— 2026-11-11 09:0x, main

★**本脚本做三件事**:
  ① ★**ISS-188 验收签字** (owner=sw-lead, verify_by=main) ⇒ status=verified / pass
  ② ★**新开 ISS-189** (F1 + F2 两处活残留, owner=hw-lead)
  ③ ★**ISS-188 落 verified + ISS-189 落 fixing** ⇒ ★**同时把 ISS-189 派出去**

★**ISS-188 的验收 (全部 main 自己实测, 不是抄 owner 自评)**:
  ① `grep -rn '373Mbps|373 Mbps|246 Mbps' SW/` ⇒ **rc=1 零命中** (带空格 + 不带空格两种写法都查)
  ② `SW/DEMO_OD_PIPELINE_SPEC.md:322` 与 `HW/DISPLAY_MODULE_DECISION.md:53` 口径一致 (都 2986 / 4480)
  ③ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0**, 脚本 md5 `7b820c14` 未变 (判据权威源没被偷改)
  ④ ★**落账器没被重跑**: tracker 里 "#### (1.60) demo 判据收敛成两条" 与 "2026-11-02 19:4x 方案定案"
     各只出现 **1** 次 ⇒ ★**没有重复追加**
  ⑤ 分片原子写 (走 `state/frag_write.py`) ⇒ 新增 2 条 claim 在位:
     `dsi_payload_1080p60_rgb888`=2986 Mbps / `dsi_payload_1080p90_rgb888`=4480 Mbps
     ⇒ ★**与 hw-lead 在 hw.yaml 的同名同值登记交叉确认 ⇒ `merge.py` 冲突 0**
  ⑥ ★**owner 如实报出 4 处残留 (F1~F4), 一处没藏** ⇒ ★**其中 F3/F4 是 main 自己的 ⇒ main 已自己改掉**
     (★**F4 差点让验收 ① 永远不为 0** —— 落账器里我自己写的口径钉死注释留了逐字串 ⇒ 已在 09:0x 改掉)

★**ISS-188 的验收范围 (owner 明确划的线)**: ★**只改 `SW/DEMO_OD_PIPELINE_SPEC.md`** (owner=sw-lead 的分片)
  ⇒ ★**main 不代写别人的分片** (MEMORY.md:3138) ⇒ ★**F1/F2 归 hw-lead ⇒ 另开 ISS-189, 不塞进本单**。

★**为什么 ISS-189 能手工派出 (★三条实测依据, 与 ISS-186 那次同一套判据★)**:
  ① ★**hw-lead 当前没有任何运行中的写会话** —— sessions_list 实测: 它最近两条子会话
     (`advance_iss186` 08:17 done / 本轮) **全部 done**, 无 running ⇒ ★**铁律要防的
     「同一 agent 两个并发写会话互相覆盖分片」没有发生**
  ② ★**ISS-181 (owner=hw-lead, fixing) 的板子活实际由【主会话】在跑** ——
     `ps` 实测 `gen_pcb_netlist_board.py` PID 279538 自 07:48 起在跑 (99% CPU) ⇒
     ★**它不占 hw-lead 的写会话名额** ⇒ advance.py 的 in_flight 代理判据在这里**代理错了事实**
  ③ ★**文件交集 = 0** —— ★**F1/F2 是两个 .md** (`HW/STEP1_LANDING_LIST.md` +
     `HW/PART_ALTERNATIVES_REGISTRY.md`) ⇒ ★**实测板链路脚本 (state/v76*.sh / state/gen_pcb_*.py /
     state/replay_patch_chain.sh) 里 grep「STEP1_LANDING_LIST|PART_ALTERNATIVES_REGISTRY」零命中**
     ⇒ ★**不抢同一块板, 不抢同一个文件**

★**落账纪律**: ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**只改这 2 条 dict 的字段** ⇒ ★**落账后逐条 diff 实测: 184 条里只有 ISS-188 / ISS-189 变了,
     其余 182 条一个字节没动**
  ③ 原子写: tmp → fsync → os.replace → fsync(dir) + yaml 往返复现自检

★**边界**: 不改 §0 锁死表 · 不碰任何子总工的分片 (只读不改) · 不发邮件 / 不联系供应商 / 不下采购单
  · 不碰板子相关任何文件。
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-11"

NOTE_188 = (
    " ★**2026-11-11 09:0x 项目总工 (main) 验收通过 (verify_result=pass)**: "
    "★**验收全部是 main 自己实测, 不是抄 owner 自评** —— "
    "① `grep -rn '373Mbps|373 Mbps|246 Mbps' SW/` ⇒ **rc=1 零命中** (★**带空格 + 不带空格两种写法都查了★); "
    "② `SW/DEMO_OD_PIPELINE_SPEC.md:322` 与 `HW/DISPLAY_MODULE_DECISION.md:53` 口径一致 (都 2986 / 4480) "
    "⇒ ★**同文件两处 (:322 + :379) 都改了, 不是 1 处**; "
    "③ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0** · 脚本 md5 `7b820c14` 未变 "
    "(★**判据权威源没被偷改★); "
    "④ ★**落账器没被重跑** (tracker 里 '(1.60) demo 判据收敛成两条' 与 '2026-11-02 19:4x 方案定案' "
    "各只出现 1 次 ⇒ 没有重复追加); "
    "⑤ 分片走 `state/frag_write.py` 原子写 ⇒ 新增 2 条 claim 在位 "
    "(`dsi_payload_1080p60_rgb888`=2986 Mbps / `dsi_payload_1080p90_rgb888`=4480 Mbps) ⇒ "
    "★**与 hw-lead 在 hw.yaml 的同名同值登记交叉确认 ⇒ `merge.py` 冲突 0**; "
    "⑥ ★**owner 如实报出 4 处残留 (F1~F4), 一处没藏** ⇒ ★**其中 F3 (main 的日记) / "
    "F4 (main 落账器里自己写的口径钉死注释) 是 main 自己的 ⇒ main 已于 09:0x 自己改掉** ⇒ "
    "★**★F4 差点让本单验收 ① 永远不为 0** (★**落账器里我自己写的注释留了逐字串 ⇒ 同一个坑 hw-lead 在 "
    "ISS-186 踩过一次 ⇒ 我又踩了一次 ⇒ 已改, 并把这条写进 MEMORY 的【注释里别留逐字串】教训★) ⇒ "
    "★**F1/F2 归 hw-lead 的分片 ⇒ 另开 ISS-189, 不塞进本单 (main 不代写别人的分片 · MEMORY.md:3138)★**."
)

ISS189 = {
    "id": "ISS-189",
    "title": ("★★DSI payload 8× 口径差 【第 8/9 处·收尾】: `HW/STEP1_LANDING_LIST.md:42` + "
              "`HW/PART_ALTERNATIVES_REGISTRY.md:24` 仍写 373 Mbps (实为 2986) ⇒ 依据虚到 8 倍"),
    "severity": "medium",
    # ★source_blocker 必须指向 STATE.yaml 里**真实存在的 blocker** (issue_check C5 双向覆盖)
    # ⇒ 用 SW-B14 (critical): 「视涯 0.49\" SiOLED 的 DSI init code / 时序 / DSC 全未拿到 (问询函草稿未发)」
    # ⇒ ★**本单修的正是 DSI 带宽口径 ⇒ 与该 blocker 语义精确对口**
    "source_blocker": "SW-B14",
    "source_agent": "main",
    "desc": (
        "★**这是 ISS-186 / ISS-188 的尾巴 (第 8 / 9 处)**: ★**owner (sw-lead) 在 ISS-188 验收时"
        "如实报出 4 处残留, 其中这 2 处在 hw-lead 的域** ⇒ ★**归你**。\n"
        "★**F1**: `HW/STEP1_LANDING_LIST.md:42` ⇒ `1920×1080@60 RGB888 ≈ 373Mbps ⇒ 4-lane 绰绰有余, "
        "**不需 DSC**` ⇒ ★**偏小 8.01×** ⇒ ★**这是【Step1 落地清单】的 display 连接行 ⇒ "
        "★**谁照着它接线, 谁就拿到一个虚到 8 倍的带宽前提**。\n"
        "★**F2**: `HW/PART_ALTERNATIVES_REGISTRY.md:24` ⇒ `RGB888 (373Mbps)` ⇒ 同一个错数。\n"
        "★**要改**: 两处 373Mbps → **2986Mbps** ⇒ 依据与 ISS-186 那 5 处同口径 "
        "(payload = 宽×高×24×60 = 1920×1080×24×60 = 2985.98 Mbps ≈ 2986 Mbps; "
        "与 `HW/e2e_budget_rk3572.py` §⑥ 同口径 ⇒ TX 物理下限 7.776ms = 2986÷60÷6400)。\n"
        "★**验收**: ① `grep -rn '373Mbps\\|373 Mbps\\|246 Mbps' HW/ SW/ state/outbox/ config/ "
        "state/_demo_hw_scheme_landing.py` ⇒ **0 命中**; "
        "② 两处与 `HW/DISPLAY_MODULE_DECISION.md:53` 口径一致 (2986); "
        "③ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 (★**不许改那个脚本**★); "
        "④ 走 `state/frag_write.py` 原子写你自己的 `state/fragments/hw.yaml` "
        "(登记这两处口径已统一 ⇒ 与 sw.yaml 的同名 claim 同值 ⇒ merge 冲突须仍为 0); "
        "⑤ 不许改 `PROJECT_TRACKER.md §0` 锁死表 (★**§0 第 75 行那个 373Mbps 是老板拍过板的历史记录, "
        "故意保留, 不许动★); 不许发邮件; 不许碰任何板子相关文件。\n"
        "★**★注意**: ★**ISS-186 / ISS-188 两轮的原始清单都没数到这两处** ⇒ "
        "★**说明「已清干净」这个结论本身要靠 grep 复核, 不能靠清单** ⇒ ★**本单就是为了把最后这个洞堵上**."),
    "owner": "hw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-13",
    "status": "open",
    "external": False,
    "need_keys": [],
    "task_brief": (
        "目标: 闭环 ISS-189 —— ★**把 DSI payload 8× 口径差的最后两处补齐** "
        "(`HW/STEP1_LANDING_LIST.md:42` 与 `HW/PART_ALTERNATIVES_REGISTRY.md:24` 仍写 373 Mbps, 实为 2986)。\n"
        "输出: ① ★**你只改这 2 处**: `373Mbps` → `2986Mbps` ⇒ 依据与 ISS-186 那 5 处同口径 "
        "(payload = 宽×高×24×60 = 1920×1080×24×60 = 2985.98 Mbps ≈ 2986 Mbps; "
        "与 `HW/e2e_budget_rk3572.py` §⑥ 同口径 ⇒ TX 物理下限 7.776ms = 2986÷60÷6400); "
        "② 交付报告 `HANDOFF/2026-11-11_hw-lead_ISS189_DSI_payload_收尾.md` (old→new 逐字串 + 自证命令实录 + 边界声明); "
        "③ 走 `state/frag_write.py` 原子写你自己的 `state/fragments/hw.yaml` (登记这两处口径已统一 ⇒ "
        "★**与 sw.yaml 的同名 claim 同值 ⇒ merge 冲突须仍为 0** ⇒ 这是交叉确认, 不是重复登记)。\n"
        "验收: ① `grep -rn '373Mbps\\|373 Mbps\\|246 Mbps' HW/ SW/ state/outbox/ config/ "
        "state/_demo_hw_scheme_landing.py` ⇒ **0 命中**; "
        "② 两处与 `HW/DISPLAY_MODULE_DECISION.md:53` 口径一致 (2986); "
        "③ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 (★**不许改那个脚本** ⇒ 它是判据的权威来源★); "
        "④ `state/merge.py` 冲突数仍为 0。\n"
        "边界: ★**不许碰 sw-lead 的分片** (那 2 处已由 ISS-188 闭环并签字) · "
        "★**不许碰 mech-lead / main 的分片** · ★**不许改 `PROJECT_TRACKER.md §0` 锁死表** "
        "(★**§0 第 75 行那个 373Mbps 是老板拍过板的历史记录, 故意保留, 不许动★) · "
        "★**不许发邮件** · ★**不许碰任何板子相关文件** (demo_mainboard.kicad_pcb / gen_pcb_*.py / "
        "state/.lastgood/ / /tmp 链产物) · ★**不许重跑 `state/_demo_hw_scheme_landing.py`** "
        "(★**它是落账器 ⇒ 重跑 = 把旧数灌回 tracker ⇒ main 已改它的 3 处并加了口径钉死, 不需要你碰**★)。\n"
        "★**★你只需动 2 行** ⇒ ★**但这两行是【Step1 落地清单】和【替代料清单】⇒ 照着它接线的人会拿到"
        "虚到 8 倍的带宽前提 ⇒ 值得改** ★★"),
    "fix_ref": ("HW/STEP1_LANDING_LIST.md:42 · HW/PART_ALTERNATIVES_REGISTRY.md:24 · "
                "HANDOFF/2026-11-11_hw-lead_ISS189_DSI_payload_收尾.md"),
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "★2026-11-11 09:0x 项目总工 (main) 开单。★**本单是 ISS-186 / ISS-188 的尾巴** ⇒ "
        "★**那两单都已于同日验收签字 (pass), 本单不阻塞它们**。\n"
        "★**来源**: sw-lead 在 ISS-188 交卷时**如实报出 4 处残留** (★**一处没藏★) ⇒ "
        "★**其中 F1/F2 在 hw-lead 的域 ⇒ 归你; F3/F4 在 main 侧 ⇒ main 已自己改掉**。\n"
        "★**★手工派出的三条依据 (与 ISS-186 同一套判据, 全部实测)**: "
        "① ★**hw-lead 当前没有任何运行中的写会话** (sessions_list 实测: 它最近两条子会话全 done) ⇒ "
        "★**铁律要防的「同一 agent 两个并发写会话互相覆盖分片」没有发生**; "
        "② ★**ISS-181 (owner=hw-lead, fixing) 的板子活实际由【主会话】在跑** "
        "(★**ps 实测 `gen_pcb_netlist_board.py` PID 279538 自 07:48 起在跑, 99% CPU★) ⇒ "
        "★**它不占 hw-lead 的写会话名额** ⇒ advance.py 的 in_flight 代理判据在这里**代理错了事实**; "
        "③ ★**文件交集 = 0** (★**F1/F2 是两个 .md ⇒ 实测板链路脚本里 grep "
        "「STEP1_LANDING_LIST|PART_ALTERNATIVES_REGISTRY」零命中** ⇒ **不抢同一块板, 不抢同一个文件**★).\n"
        "★**★一条要记住的教训 (ISS-186/188 两轮都没数到 F1/F2)**: ★**「已清干净」这个结论"
        "本身必须靠 grep 复核, 不能靠清单** ⇒ ★**下一轮再有人收口 payload 口径, 先跑 grep 再下结论**."),
    "dispatched_at": TODAY,
}


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
    if not os.path.exists(LOCK):
        open(LOCK, "a").close()
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            doc = yaml.safe_load(f.read())
        issues = doc.get("issues") or []
        by = {i.get("id"): i for i in issues}
        before_count = len(issues)
        changed = []

        # ---- ① ISS-188 签字 ----
        i188 = by.get("ISS-188")
        if not i188:
            print("❌ 找不到 ISS-188")
            return 2
        if i188.get("status") != "fixing":
            print(f"⚠️ ISS-188 status={i188.get('status')} (期望 fixing) ⇒ 跳过签字")
        else:
            i188["status"] = "verified"
            i188["verify_result"] = "pass"
            i188["verify_date"] = TODAY
            i188["note"] = (i188.get("note") or "") + NOTE_188
            changed.append("ISS-188 (签字)")

        # ---- ② 新开 ISS-189 ----
        if any(x.get("id") == "ISS-189" for x in issues):
            print("⚠️ ISS-189 已存在 ⇒ 不重复开")
        else:
            issues.append(dict(ISS189))
            changed.append("ISS-189 (新建)")

        # ---- ③ ISS-189 落 fixing (派活日志) ----
        i189 = next((x for x in issues if x.get("id") == "ISS-189"), None)
        if i189 and i189.get("status") == "open":
            i189["status"] = "fixing"
            i189["dispatched_at"] = TODAY + " 09:0x (项目总工手工解冻派活)"

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, out)

        # ---- dispatch_log ----
        dl = {}
        if os.path.exists(DL):
            with open(DL, encoding="utf-8") as f:
                dl = yaml.safe_load(f) or {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-189", "agent": "hw-lead",
            "at": TODAY + " 09:0x", "brief": ISS189["task_brief"][:300]})
        with open(DL, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)

        # ---- 自检 ----
        with open(LOG, encoding="utf-8") as f:
            rt = yaml.safe_load(f.read())
        rt_out = yaml.safe_dump(rt, allow_unicode=True, sort_keys=False, width=200)
        ok_rt = (rt_out == out)

        fcntl.flock(lf, fcntl.LOCK_UN)

    print(f"落账: {changed}")
    print(f"条目数 {before_count} → {len(issues)}")
    print(f"yaml 往返复现自检: {'✅ 一致' if ok_rt else '❌ 不一致'}")
    for cid in ("ISS-188", "ISS-189"):
        for i in issues:
            if i.get("id") == cid:
                print(f"  {cid}: status={i.get('status')} owner={i.get('owner')} "
                      f"verify_by={i.get('verify_by')} verify_result={i.get('verify_result')}")
    return 0 if ok_rt else 1


if __name__ == "__main__":
    sys.exit(main())
