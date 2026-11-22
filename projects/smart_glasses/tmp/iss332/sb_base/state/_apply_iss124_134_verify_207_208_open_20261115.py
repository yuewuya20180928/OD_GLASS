#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-15 21:4x 队列自动派活 · 项目总工 (main/moli) 落账 + 开新单
================================================================================
★★**这一脚本干两件事 (★都是"让内部待办不断线"的必要动作★)** ★★:

【A】★**清 2 条僵尸 fixing** (★同病第 14 次复发★) ——
  · ISS-124 (sw-lead): 子会话 `agent:sw-lead:subagent:dec79f44` 2026-11-15 21:39 结束, status=**done**
    ⇒ ★**交卷已投递、文件已落盘** ⇒ 但 brief 明写「不许碰 state/issue_log.yaml (改 issue 状态是 main 的活)」
    ⇒ 没人落账 ⇒ status 停在 `fixing` ⇒ ★**`advance.py` 的 in_flight 规则永久占住 sw-lead 的名额** ★
  · ISS-134 (mech-lead): 子会话 `agent:mech-lead:subagent:5a211ee3` 2026-11-15 21:36 结束, status=**done** ⇒ 同病
  ⇒ ★**后果 (★实测★)**: `python3 state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ ★**队列对三个总工全空**
    ⇒ ★**sw-lead / mech-lead 本轮实际是空闲的, 却因为这 2 条僵尸进不了候选** ★

  ★**两条交卷我逐份独立复核过 (★不采信自述, 只看盘上实物★)** ★★:
  · ISS-124 ⇒ ✅ 四件交付物在盘 (md/sch md+json / 反解器 / 交卷单, mtime 21:29~21:39)
    · ✅ `python3 SW/tools/timing_check.py` 本机实跑 rc=0, SELFTEST **55/55** 通过
    · ✅ `python3 SW/tools/isp_budget_solve.py` 本机实跑 rc=0, SELFTEST **11/11** 通过
    · ✅ 受保护文件 md5 一字未变 (网表 / 板 / timing_check.py / p10_rows.json)
    · ✅ 分片已登记 (`state/fragments/sw.yaml` artifacts 59 条, 含本单 3 条)
  · ISS-134 ⇒ ✅ 三件交付物在盘 (判据 V2 / 角色收窄 / 交卷单, mtime 21:32~21:36)
    · ✅ 关键量复核: `L_eye,max = 0.1234 / A_e` 与「A_e ≤ 62 mm² (≈8×7.7 mm)」在 `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` C-4/C-5 里逐字在
    · ✅ 「走鹃」计数复核: 旧 5 份文档 21+6+3+2+1 = **33 处** (与交卷件自述一致) ⇒ **本单遗留 need 已登记在 mech.yaml**
    · ✅ 分片已登记 (`state/fragments/mech.yaml` artifacts 64 条, 含本单 2 条; needs_from 含 `iss134_mech_close_legacy_zoujuan_refs`)
  · ★**门禁 (main 自己跑的)**: `python3 state/merge.py` rc=0 (产出 200 · 阻塞 43 · 冲突 0) · `python3 state/gate_check.py` rc=0
    (【Q1】18/18 · 【Q2】3/3 · 【Q6】硬件真源闸 ✅)

【B】★**开 2 条新内部单 (把两个空闲总工的产能接回主线)** ——
  · ★**ISS-207 → sw-lead** (源自 ISS-155, demo 头号卡点): ★**板子不可达 ⇒ 按老板 2026-11-12 02:02 新口径,
    不许把外部依赖挂着当阻塞项** ⇒ 改成【自己查官方口径 + 板端到手 30 分钟可跑的验证包 + PC 侧产物可重建路径】
  · ★**ISS-208 → mech-lead** (源自 ISS-134 遗留 need): ★**33 处「走鹃」旧口径收口 + 眼盒面积 A_e ≤ 62 mm²
    落进结构真源** ⇒ ★**显示件硬约束进结构侧, 不留"以后再说"**
  · ★**两条都零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料)
  · ★**两条都不是 PCB 布线/布局类** (老板 2026-11-11 10:07 主线: 先原理图) ⇒ ★**本轮按主线口径跳过 PCB 类 = 0 条**

★★**落账纪律 (与项目既有范式一致)** ★★:
① flock(state/.issue_log.lock) + 锁内重读
② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (⇒ 除本脚本要改的那几条外, 一个字节都不许动)
③ 原子写 (tmp → fsync → os.replace → fsync(dir))
④ 只动 ISS-124 / ISS-134 两条 (落账) + 新增 ISS-207 / ISS-208 两条 (开单), 不动任何其它 issue

★★**边界** ★★: 不改 `PROJECT_TRACKER.md` §0 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 / 不下采购单 ·
板 / 网表 / 原理图 / BOM 一个字节不动 · ★**不改 ISSUE-155 本体** (★它仍是 main 名下的头号卡点, 本单只把它拆出一块可执行的内部活★)
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
BRIEF_207 = os.path.join(HERE, "_brief_iss207.txt")
BRIEF_208 = os.path.join(HERE, "_brief_iss208.txt")

NOW = "2026-11-15 21:4x"

VERIFY_124 = (
    "pass · %s 项目总工独立复核 (★不采信自述, 只看盘上实物★)\n"
    "★**① 交付物四件齐全 (main 实测 mtime)**: `SW/ISP_CAPABILITY_RESEARCH.md` (23249 B, 21:38) · "
    "`SW/ISP_CAPABILITY_RESEARCH.json` (4779 B, 21:38) · `SW/tools/isp_budget_solve.py` (24345 B, 21:29) · "
    "`HANDOFF/2026-11-15_sw-lead_ISS124_ISP能力与功耗自查.md` (3445 B, 21:39)\n"
    "★**② 自证脚本本机实跑 (main 自己跑的, 不是采信自述)**: `python3 SW/tools/timing_check.py` ⇒ rc=0, SELFTEST **55/55** 通过 · "
    "`python3 SW/tools/isp_budget_solve.py` ⇒ rc=0, SELFTEST **11/11** 通过 (含敏感性带 γ=0.8/1.2 与「满载 10/10 档位仍超 43°C 红线 ⇒ 结论不翻案」两条断言)\n"
    "★**③ 受保护文件 md5 一字未变**: 网表 `c78f991283cc82d56c8e3dd31657c785` · 板 `611b869e13518c3c023fb178f91a0075` · "
    "`SW/tools/timing_check.py` `cdc59f554fc6c82fe2588c2845b08977` · `state/p10_rows.json` `c2dc73fe1e9fbd8edec68828dec81c36`\n"
    "★**④ 分片已登记 (main 复核)**: `state/fragments/sw.yaml` artifacts = 59 条 (含本单 3 条: ISP_CAPABILITY_RESEARCH.md / .json / isp_budget_solve.py) · "
    "answers = 6 ⇒ ★**走 state/frag_write.py, 未动他人 key** ★\n"
    "★**⑤ 门禁 (main 自己跑的)**: `python3 state/merge.py` rc=0 (产出 200 · 阻塞 43 · 冲突 0) · `python3 state/gate_check.py` rc=0 (【Q1】18/18 · 【Q2】3/3 · 【Q6】硬件真源闸 ✅)\n"
    "★**⑥ 本单真正留下的东西 (★不是「官方没给」三个字★)**: ★**官方从未给过 ISP 的 MP/s 吞吐上限, 也未给过 ISP 功耗** ⇒ 03a/03b' 的「等原厂回信」外发依赖已被"
    "【自己查 + [0数据] + 降级 A/B/C】替换 ⇒ ★**这条假阻塞被消解, 队列里不再挂外部依赖** ⇒ ⇒ ★**反解数字: ISP 段在 60ms 硬线下最多能占 15.10 ms (模式A) / 17.33 ms (模式B)** "
    "⇒ **现占 8.00 ms ⇒ 余量 +7.09 / +9.33 ms ⇒ ISP 最多能慢到现值的 1.89×/2.17× 才破线** ★\n"
    "★**⑦ 残留 (只报不改, 归 main / 另派)**: 降级方案 C 仍需一块**可达**的 RK357x 板 (本机此刻无可达板 ⇒ **不许写「等板子回来」**) · "
    "`SW/SW_REQUIREMENTS.md` §10.6 的 S3「相对最强」排序需重定 (★属 main 地界, 只报不改★) · `SW/DEMO_OD_TIMING_SPEC.md` §2 的 11 段表缺 ISP 段打点 (⇒ 另派)\n"
    "★**⑧ 与口径纪律的符合性**: 本单**零外发** · 全文没有 [实测] 冒充实测 (板端结论一律 [0数据]/[推算]) · ★**没有把「查不到」留成阻塞项** ⇒ 给了算值反解 / 出瞳实测 / 换板三档降级 ★"
) % NOW

VERIFY_134 = (
    "pass · %s 项目总工独立复核 (★不采信自述, 只看盘上实物★)\n"
    "★**① 交付物三件齐全 (main 实测 mtime)**: `MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md` (36292 B, 21:32) · "
    "`MECH/JBD_ROLE_NARROWING.md` (21512 B, 21:35) · `HANDOFF/2026-11-15_mech-lead_ISS134_显示口径与光生物安全V2.md` (4159 B, 21:36)\n"
    "★**② 关键量逐字复核 (main 自己 grep 的)**: `L_eye,max = 0.1234 / A_e` 与「A_e=150 mm²→823 cd/m² · 64→1928 · 25→4936」与"
    "「**要入眼 2000 cd/m² ⇒ 眼盒必须 ≤ 62 mm² (≈8×7.7 mm)**」⇒ ★**在 C-4 / C-5 两行里逐字在** ⇒ ★**结论不是自述, 是盘上实物** ★\n"
    "★**③ 「走鹃」计数复核 (main 自己 grep 的)**: 旧 5 份文档 `MECH_BUDGET.md` 21 · `PROTOTYPE_PLAN.md` 6 · `SOC_CARRIER_EVAL.md` 3 · "
    "`STRUCT_REVIEW_ISS065.md` 2 · `CLEARANCE_FIX.md` 1 = ★**33 处** ⇒ 与交卷件自述一致 ⇒ ★**这 33 处就是本单的遗留 (已另开 ISS-208)** ★\n"
    "★**④ 分片已登记 (main 复核)**: `state/fragments/mech.yaml` artifacts = 64 条 (含本单 2 条) · answers = 25 · "
    "needs_from 含 ★**`iss134_mech_close_legacy_zoujuan_refs`**★ ⇒ ★**遗留已进台账, 不是口头交接** ★\n"
    "★**⑤ 门禁 (main 自己跑的)**: `python3 state/merge.py` rc=0 (产出 200 · 阻塞 43 · 冲突 0) · `python3 state/gate_check.py` rc=0 (【Q1】18/18 · 【Q2】3/3 · 【Q6】✅)\n"
    "★**⑥ 本单真正留下的东西**: ★**光生物安全不是 ARS45 的风险源** (最坏 L_B ≈ 264 W/(m²·sr), 距 RG2 差 4 个数量级) · "
    "★**「波导必须找 JBD」不成立** (公开在售/量产 ≥11 家) ⇒ ⇒ ★**ISS-004/013 的真阻塞是「缺 2D 外形图」而不是「等 JBD」⇒ 镜框不必等 JBD 就能开工** ★\n"
    "★**⑦ 残留 (只报不改)**: 5 份旧文档的 33 处「走鹃」活动口径 (⇒ 已另开 ISS-208) · 波导归属 + FOV 目标 (⇒ 老板待拍板, 已进 C 段决策页) · "
    "预存量 33 处旧口径引用在 5 份 MECH 文档里 (⇒ 同上, ISS-208 收口)\n"
    "★**⑧ 与口径纪律的符合性**: 本单**零外发** · 全文没有把「查不到」留成阻塞项 (12 个 [0数据] 全部配了降级) · ★**板端实测 = 0 条已如实标** ★"
) % NOW

NEW_207 = {
    "id": "ISS-207",
    "title": "★★★★[demo 头号卡点·自己查版] ISS-155 拆块: rknn-toolkit2 最新版到底支不支持 rk3572 target + RK3572 runtime 认不认 rk3576-target 产物 + 板端到手 30 分钟可跑的验证包",
    "severity": "blocker",
    "source_blocker": "ISS-155",
    "source_agent": "main",
    "desc": (
        "★2026-11-15 21:4x main 拆自 ISS-155 (demo 头号卡点) 的【内部可执行块】。★**ISS-155 本体不动** (仍是 main 名下头号卡点) ⇒ "
        "本单只做三件本机就能交的事: ①★**官方口径自己查**★ (rknn-toolkit2 最新版合法 `target_platform` 列表里到底有没有 rk3572 · "
        "RK3572 BSP 的 runtime 在官方层认不认 rk3576-target 产出的 .rknn) ②★**板端到手 30 分钟跑完的验证包 (★可执行脚本, 本机 `--dry-run` 必须 rc=0★)**★ "
        "③★**PC 侧产物的可重建路径 (落盘目录 + sha256 + 一键重建)**★。★**按老板 2026-11-12 02:02 新口径: 不许把「等一块能跑的板」挂着当阻塞项** ⇒ "
        "★**把「必须实测」变成「拿到任意一块 RK357x 板就能自动跑完」**★。★**本机现状 (main 实测)**: `import rknn_toolkit2` ⇒ ModuleNotFoundError · "
        "`pip show rknn-toolkit2` ⇒ not found · `conda` 不存在 ⇒ ⇒ **PC 侧转换链现在跑不起来 ⇒ 本单的价值在「可执行性」, 不在「再跑一遍」** ★"
    ),
    "owner": "sw-lead",
    "reporter": "main",
    "raised": "2026-11-15",
    "due": "2026-11-18",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": "",
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "★2026-11-15 21:4x main 开单。★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ "
        "★**全部对外信息自己上网查官方页面, 查不到标 [0数据] + 写降级方案** ⇒ **没有「等原厂回信/等板子回来」这个选项** ★"
        "★**本单不是 PCB 布线/布局类** (老板 2026-11-11 10:07 主线: 先原理图) ★"
        "★**派活前已过命令存在性闸**: `python3 state/check_brief_commands.py --brief-file state/_brief_iss207.txt` ⇒ rc=0 ★"
    ),
    "dispatched_at": None,
    "task_brief": "@@BRIEF_207@@",
}

NEW_208 = {
    "id": "ISS-208",
    "title": "★★[主线内·显示侧·内部活] ISS-134 遗留: 旧 MECH 文档 33 处「走鹃」活动口径收口 + 光生物安全 V2 的眼盒约束 (A_e ≤ 62 mm²) 落进结构真源",
    "severity": "medium",
    "source_blocker": "ISS-134",
    "source_agent": "main",
    "desc": (
        "★2026-11-15 21:4x main 拆自 ISS-134 的【遗留收口单】。★**ISS-134 已闭死** (光生物安全不是风险源 · 「波导必须找 JBD」不成立 · "
        "公开在售/量产 ≥11 家) ⇒ 但 ★**5 份旧 MECH 文档里还有 33 处「走鹃」活动口径** (main 实测: MECH_BUDGET 21 · PROTOTYPE_PLAN 6 · "
        "SOC_CARRIER_EVAL 3 · STRUCT_REVIEW_ISS065 2 · CLEARANCE_FIX 1) ⇒ ⇒ ★**留着就是错口径在流, 后面的镜框/光机会照着错的做** ★"
        "★**本单第二件事**: 把 V2 判据 C-4/C-5 的硬约束 (★**入眼 2000 cd/m² ⇒ 波导眼盒面积 A_e ≤ 62 mm² (≈8×7.7 mm) ⇒ 直接夹住镜框上沿厚度 + 鼻梁区光件空间★**) "
        "落进结构真源 ⇒ ★**不留成「以后再说」** ★"
    ),
    "owner": "mech-lead",
    "reporter": "main",
    "raised": "2026-11-15",
    "due": "2026-11-18",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": "",
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "★2026-11-15 21:4x main 开单。★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ 查不到标 [0数据] + 写降级方案 ★"
        "★**本单不是 PCB 布线/布局类** (老板 2026-11-11 10:07 主线: 先原理图) ★"
        "★**派活前已过命令存在性闸**: `python3 state/check_brief_commands.py --brief-file state/_brief_iss208.txt` ⇒ rc=0 ★"
    ),
    "dispatched_at": None,
    "task_brief": "@@BRIEF_208@@",
}


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".iss207208.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    brief_207 = open(BRIEF_207, encoding="utf-8").read().strip()
    brief_208 = open(BRIEF_208, encoding="utf-8").read().strip()

    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
        raw = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(raw)
        issues = doc.get("issues") or []

        # ★自证 1: 未改动前, safe_dump 必须与原文件逐字节相同 ⇒ 证明 yaml 往返无损
        if yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200) != raw:
            print("★落盘中止: yaml 往返不是逐字节相同 ⇒ 原文件里有 safe_dump 会改写的结构 ⇒ 拒绝写")
            return 2

        by_id = {i.get("id"): i for i in issues}
        changed = []

        # ---------- A. 落账: ISS-124 / ISS-134 (僵尸 fixing → verified) ----------
        for iid, ver in (("ISS-124", VERIFY_124), ("ISS-134", VERIFY_134)):
            it = by_id.get(iid)
            if not it:
                print("★%s 不在 issue_log 里 ⇒ 拒绝写" % iid)
                return 2
            if it.get("status") not in ("fixing", "open"):
                print("★%s 的 status 是 %r (不是 fixing) ⇒ 拒绝写" % (iid, it.get("status")))
                return 2
            it["status"] = "verified"
            it["verify_by"] = "main"
            it["verify_result"] = ver
            it["verify_date"] = NOW
            it["fixed_at"] = "2026-11-15"
            it["dispatched_at"] = it.get("dispatched_at") or "2026-11-15"
            it["fix_ref"] = it.get("fix_ref") or ""
            changed.append("%s → verified (main 独立复核)" % iid)

        # ---------- B. 开新单: ISS-207 / ISS-208 ----------
        for tmpl, brief, tag in ((NEW_207, brief_207, "207"), (NEW_208, brief_208, "208")):
            iid = tmpl["id"]
            if iid in by_id:
                print("★%s 已存在 ⇒ 拒绝重开" % iid)
                return 2
            new = dict(tmpl)
            new["task_brief"] = brief
            issues.append(new)
            changed.append("%s → 新开 (owner=%s, status=open)" % (iid, tmpl["owner"]))

        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)

        # ★自证 2: 除了这 4 条, 其它条目一个字节都不许动
        before = yaml.safe_load(raw)
        after = yaml.safe_load(out)
        b = {i["id"]: i for i in before["issues"]}
        a = {i["id"]: i for i in after["issues"]}
        if set(a) != set(b) | {"ISS-207", "ISS-208"}:
            print("★落盘中止: 进出条目集合对不上 ⇒ 拒绝写")
            return 2
        for iid in b:
            if iid in ("ISS-124", "ISS-134"):
                continue
            if b[iid] != a[iid]:
                print("★落盘中止: %s 被意外改动 ⇒ 拒绝写" % iid)
                return 2

        atomic_write(LOG, out)
        print("★issue_log.yaml %d B → %d B" % (len(raw), len(out)))
        for c in changed:
            print("  · %s" % c)
        print("★自证: yaml 往返逐字节相同 ✓ · 其它 198 条一字未动 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
