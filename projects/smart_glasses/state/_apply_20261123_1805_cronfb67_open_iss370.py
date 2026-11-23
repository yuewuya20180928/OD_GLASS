#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 18:05 · 新开 ISS-370 (sw-lead · 腿B 对 SW 侧影响面) 并【落 open 排队·不派】** ★

★**为什么只开单不派 (★逐条本机实读·不猜★)**:
  ① `python3 state/advance.py --json` ⇒ ★**`internal: []`** ⇒ 三个总工名下零 open 可派 ⇒ 队列真空 ★
  ② ★**三个总工槽位此刻【全部被占】(★本机 18:0x 实测 transcript mtime 仍在长★)**:
     sw-lead = ★**兄弟 job 775d9893 的 ISS-368 在飞** (★会话 `a5195022…` 17:58:21 仍在写★) ·
     mech-lead = ★**兄弟 job 的 ISS-367 在飞** (★会话 `3e07fa0e…` 17:58:30 仍在写★) ·
     hw-lead = ★**ISS-366 在飞** (★会话 `2dfd93c9…` 17:59:19 仍在写★) ⇒ ★**⇒ 铁律「一个 agent 同时只允许一个写会话」⇒ 本轮【一条都不派】★**
  ③ ★**⇒ 所以本单落 `open` 排队 (★照兄弟 job 开 ISS-369 的同一手法★) ⇒ 下一轮 `state/advance.py --json` 会把本单列进 internal (★sw-lead 槽位空出来那一轮·由 A 段自动派·两个 job 都按「该 agent 无 running 写会话」判定 ⇒ 不会撞车★)★**

★**★本单为什么值得存在 (★main 2026-11-23 17:4x~17:5x 本机实跑·不抄任何 agent 报告·★三组对照★)★**:
  ★**① 腿 B = `HW/netlist_v1.csv` 的 200 条指令 (改名 196 + 补行 4) ⇒ main 逐格比对: 196 格改动全在 `node1`(120)/`node2`(76) 两栏, `net`/`ref`/`value`/`type`/`dnp`/`board` 一格未动, 行数 513→517** ★
  ★**② ★★把腿 B 的网表喂给 SW 侧闸 ⇒ `SW/tools/timing_check.py` 从 85/85 全过掉到 70/85 (rc=1 · 15 条红)★★** ★
  ★**③ 对照组 (★同内容换路径 `tmp/iss370_sbx/netlist_REAL_copy.csv`) 仍 85/85 ⇒ 红是【内容】造成的·不是路径** ★
  ★**④ 再拆: 只改名 = 14 红 / 只补行 = 2 红 ⇒ 那 2 条全是【落表义务】(行数 + md5 登记)⇒ 语义破坏与落表义务是两件事** ★
  ★**⑤ 根因 (★main 读源码定位★): `SW/tools/timing_check.py` 的 `resolve_chain_landing()` (★L1013★) 判中点网用 `{node1,node2} == {上臂位号,下臂位号}` 的【精确字符串相等】⇒ 改名后节点串变成 `R_BAT_DET_1 pin1` ⇒ 精确相等不成立 ⇒ 中点网取不到 ⇒ 落点/判决对象/源阻抗/τ 一整串 ADC 判据塌** ★
  ★**⑥ ★★不查清的后果: 腿 B 是【C4 158→68 的唯一杠杆】(★ISS-364 沙盒已证明·腿A 换 land 对 C4 贡献 = 0★) ⇒ 那一趟必须做 ⇒ 而它会让 SW 门禁当场红 ⇒ 要么硬改闸 (把红项调没·★ISS-273/275/284 堵过的漏洞★) 要么板 md5 变第二次 (违「板只改一次」)★★** ★
  ★**⑦ 第二处同批必须动的: `SW/tools/check_demo_panel_spec.py` 的 R6 在腿 B 网表下红 (`盘上真源 md5 HW/netlist_v1.csv = 724f0bf71cb7 ≠ 台账最新记录 6aee500e60ba`) ⇒ 必须同批【落表 + 重锚】(★那是 hw-lead 的地界·本单只给改法与时序★)** ★
  ★**⑧ negative 结论 (★main 实跑·★沙盒=腿B 网表★): `check_shutdown_semantics.py` rc=0 · `check_sw_ref_reachability_v2.py` rc=0 · `check_load_switch_selection.py` rc=0 · `check_landing_trace_obligation.py` rc=0 ⇒ 这四道不受腿 B 影响** ★

★**纪律**: ★**status 落 `open` 而非 `fixing` (★本轮【不派】⇒ 不能落 fixing·★落 fixing 会让下一轮 in_flight 规则误判「已在飞」而永久压住这一单★)★** ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·本 job 自己也不发★)**
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261123_1805_cronfb67_open_iss370"
BRIEF370 = "ISS-370_sw_legb_node_rename_sw_impact.md"

B370 = open(os.path.join(HERE, "dispatch_briefs", BRIEF370), encoding="utf-8").read()

TITLE370 = (
    "★★[★新主线·PCB 线·SW 侧「腿 B 网表节点具名」对 SW 判据链的影响面·纯分析+作业包+新建闸+沙盒预演·零写板] ★★"
    "【ISS-364 (hw-lead) 已把腿 B 的 200 条指令 (改名 196 + 补行 4) 做成逐条可执行作业包, 并用沙盒证明 C4 158→68 只靠腿 B (腿 A 换 land 贡献实测为 0); "
    "而 main 2026-11-23 17:4x~17:5x 本机实跑发现: ★★把腿 B 的网表喂给 SW 侧闸, `SW/tools/timing_check.py` 从 85/85 全过掉到 70/85 (15 条红)★★ "
    "⇒ 对照组 (同内容换路径) 85/85 ⇒ 是内容不是路径; 再拆: 只改名 = 14 条红 / 只补行 = 2 条红 (且那 2 条是【落表义务】不是语义破坏) "
    "⇒ 根因 = 腿 B 把节点串从裸位号改成 `ref pinN`, 而 timing_check 的 `resolve_chain_landing()` 判中点网用的是【精确字符串相等】★ "
    "⇒ ⇒ ★★不查清 ⇒ 那一趟开工当天 SW 门禁当场红 ⇒ 要么硬改闸 (把红项调没·正是 ISS-273/275/284 堵过的漏洞) 要么板 md5 变第二次 (违「板只改一次」)★★ "
    "⇒ ★★本单 = ① 15 条红逐条表 (红因/归类/修法/自证回绿) ② 「腿 B ⇒ SW 侧必须同批改的活」逐件清单 (照 ISS-323 范本) "
    "③ 一条机器闸 (含「语义红 vs 落表义务红 可分离」判据) + 沙盒三组对照预演 + 一页 + 交卷页 + 分片 + 留证** "
    "★【纯分析 + 作业包 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★"
)

DESC370 = (
    "★**main 2026-11-23 17:4x~17:5x 本机实读 (不抄任何 agent 报告)★** ⇒ "
    "★**① 腿 B 只改两栏**: main 逐格比对 `HW/netlist_v1.csv` vs `tmp/iss364_sbx/netlist_v1_legB.csv` ⇒ ★**196 格改动全在 `node1` (120) + `node2` (76)** · "
    "`net`/`ref`/`value`/`type`/`dnp`/`board`/`footprint` 一格未动 · ★**行数 513 → 517** ★ "
    "★**② ★★三组对照 (★main 本机实跑·★可复跑★)★★**: 基线真网表 = ★**85/85 · rc=0** ★; 对照组 (真内容换路径 `tmp/iss370_sbx/netlist_REAL_copy.csv`) = ★**85/85 · rc=0** ★ "
    "⇒ ★**⇒ 红不是路径造成的** ★; 腿 B 全量 = ★**70/85 · rc=1 · 15 条红** ★ "
    "★**③ 再拆一层 (★把改名与补行分开·★否则只能拿到症状拿不到根因★)★**: 只改名 (196 格·513 行·main 已落 `tmp/iss370_sbx/netlist_v1_rename_only.csv`) = ★**71/85 · 14 红** ★; "
    "只补行 (4 行·0 改名·main 已落 `tmp/iss370_sbx/netlist_v1_rowadd_only.csv`) = ★**73/85 · 2 红** ★ ⇒ ★**那 2 条全是【锚点/行数】类 (落表义务)·不是语义破坏** ★ "
    "★**④ 根因 (★main 读源码定位★)**: `SW/tools/timing_check.py` 的 `resolve_chain_landing()` (★L1013★) 判中点网用 ★**`{node1,node2} == {上臂位号,下臂位号}` 的精确字符串相等** ★ "
    "⇒ 改名后 node1/node2 变成 `R_BAT_DET_1 pin1` / `R_BAT_DET_2 pin1` ⇒ 精确相等不成立 ⇒ 中点网取不到 ⇒ 落点/判决对象/源阻抗/τ 一整串 ADC 判据塌 (★13 条语义红·★4 条是反向用例随正向一起塌★) ★ "
    "★**⑤ 15 条红逐条 (★main 实跑原文·★不是推测★)★**: ADC 源阻抗 37.5k / ADC tau 3.75ms / ADC 12bit 建立 33.8ms / ADC 漏电偏移 37.5mV / "
    "网表锚点 513 数据行 / 网表锚点 md5 ∈ 落表台账登记状态 / F4' 判决对象 = BAT_DET 链 / F4 漏电偏移 2.1% FS / F4 判决源 = SoM 脚表 signal 列 / "
    "F4 ADC 节点 @4.2V = 1.575V / F4D VBUS_DET_D 落点 = J_SOM_P1 pin100 / REV-12 / REV-13 / REV-14 / REV-15 (★四条反向用例★) ★ "
    "★**⑥ 第二处同批必须动的 (★main 实跑★)**: `SW/tools/check_demo_panel_spec.py` 的 R6 在腿 B 网表下红 ⇒ ★**`R6 台账链: 盘上真源 md5 HW/netlist_v1.csv = 724f0bf71cb7 ≠ 台账最新记录 6aee500e60ba`** ★ "
    "⇒ ★**⇒ 腿 B 一落地网表 md5 必变 ⇒ R6 三方对账必红 ⇒ 必须同批【落表 + 重锚】(★那是 hw-lead 的地界·本单只给改法与时序★)★ ★ "
    "★**⑦ negative 结论也要写 (★main 实跑·★沙盒 = 腿 B 网表·`--root` 指沙盒根★)★**: `check_shutdown_semantics.py` rc=0 · `check_sw_ref_reachability_v2.py` rc=0 · "
    "`check_load_switch_selection.py` rc=0 · `check_landing_trace_obligation.py` rc=0 ⇒ ★**这四道不受腿 B 影响** ★ "
    "★**⑧ 已有范本**: `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (★ISS-323 · S1 改名那一趟的 7 件必须同批改的活·逐字可执行清单★) ⇒ ★**本单 = 腿 B 那一趟的同款清单★ ★ "
    "★**⑨ 台账**: `SW/SW_MD5_BASELINE_LEDGER.md` (★R6 锚点 + 落表台账链 + H-1 重锚机制★) · `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★落表台账本体★) · "
    "`SW/BOARD_ONEPASS_SW_SYNC.md` (★SW 侧板侧输入收口·§2 8 条逐条表·★只登记不许改正文★) ★ "
    "★**⑩ 沙盒落项目盘 `tmp/iss370_sbx/` (★不许写 /tmp: 2026-11-23 04:4x 实测系统 /tmp 配额已满·写 /tmp 会让闸拿到假读数★)** ★ "
    "★**⇒ 本单只出【纯分析 + 作业包 + 新建闸 + 沙盒预演】, 一个字节都不许写板** ★"
)

NOTE370 = (
    "★2026-11-23 18:05 cron fb67af40 新开 · ★★落 open 排队, 不派 (★18:0x 本机实读: sw-lead / mech-lead / hw-lead 三个会话 transcript mtime 全部仍在长 ⇒ 三个槽位全被占·★铁律「一个 agent 同时只允许一个写会话」★)★★ "
    "★⇒ 下一轮 `state/advance.py --json` 会把本单列进 internal (★sw-lead 槽位空出来那一轮·A 段自动派·★两个 job 都按「该 agent 无 running 写会话」判定 ⇒ 不会撞车★)★ "
    "★**开单依据**: ① `state/advance.py --json` ⇒ internal=[] (三个总工名下零 open 可派) "
    "② ★**本单是新发现·不是重复**: 兄弟 job 17:5x 开的 ISS-367 (mech · E-9 LED 窗口规格同趟重算) 与 ISS-368 (sw-lead · SW09 三处同批落地补丁) ★**都不含腿 B 对 SW 判据链的影响面**★ "
    "(★已 grep 兄弟 job 的 ISS-368 brief 确认「腿B/具名/timing_check」零命中★) ⇒ ★**⇒ 与在飞单零重叠 ⇒ 可以安全排队** ★ "
    "③ ★**leg B 是 C4 158→68 的唯一杠杆** (★ISS-364 沙盒已证明·腿A 换 land 对 C4 贡献 = 0★) ⇒ ★**那一趟必须做 ⇒ 而它会让 SW 门禁当场红 ⇒ 不预先查清 = 板 md5 要变第二次** ★ "
    "④ 派活前置闸 `state/check_brief_commands.py --brief-file` ⇒ ★**本 brief rc=0** ★ "
    "★**任务书全文**: `state/dispatch_briefs/%s` (20,062 B)★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · "
    "零落表 (网表/脚表/BOM/落表台账/issue_log 一字不改) · 零改既有闸 (timing_check.py / check_demo_panel_spec.py / check_shutdown_semantics.py / "
    "check_sw_ref_reachability_v2.py / check_onepass_sw_sync.py / check_fp_truth_read.py / check_sw_fp_truth_impact.py / gate_check.py / merge.py / frag_write.py 一字不改) · "
    "零改既有页面 (SW/BOARD_ONEPASS_SW_SYNC.md / SW/SW_MD5_BASELINE_LEDGER.md / SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md / "
    "HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md 老字零改动) · 零挂链 · 只写自己的分片 state/fragments/sw.yaml (只走 frag_write.py) · "
    "沙盒只落 tmp/iss370_sbx/ + logs/iss370/ · 不替老板拍板 · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log★"
) % BRIEF370


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


NEW = {
    "id": "ISS-370",
    "title": TITLE370,
    "severity": "high",
    "source_blocker": "ISS-364",
    "source_agent": "main",
    "desc": DESC370,
    "owner": "sw-lead",
    "reporter": "main",
    "raised": "2026-11-23",
    "due": "2026-11-25",
    "status": "open",
    "external": False,
    "need_keys": [],
    "task_brief": B370,
    "note": NOTE370,
    "dispatched_at": None,
}


def main() -> int:
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        iid = NEW["id"]
        if iid in idx:
            it = idx[iid]
            it["status"] = "open"
            it["task_brief"] = NEW["task_brief"]
            it["note"] = NEW["note"]
            it["dispatched_at"] = None
            applied.append("%s 已存在 ⇒ status→open + brief/note 刷新 (幂等)" % iid)
        else:
            issues.append(dict(NEW))
            applied.append("新开 %s (%s) · status 落 open (排队·不派·三个槽位全被占)" % (iid, NEW["owner"]))

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        if isinstance(dlog, dict):
            entries = dlog.get("dispatches") or []
            dlog_is_dict = True
        else:
            entries = dlog
            dlog_is_dict = False
        if not any(e.get("issue") == iid for e in entries):
            entries.append({
                "issue": iid,
                "agent": NEW["owner"],
                "at": "2026-11-23",
                "brief": NEW["note"],
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★开单时刻 2026-11-23 18:05 · "
                    "★**落 open 排队不派 (三个槽位全被占) ⇒ 下一轮 A 段按 advance.py 的 internal 自动派** ★"
                ),
            })
            applied.append("dispatch_log.yaml += %s %s 1 条" % (iid, NEW["owner"]))
        else:
            applied.append("dispatch_log.yaml: %s 已有记录 ⇒ 不重复追加" % iid)
        out = dlog
        if dlog_is_dict:
            out["dispatches"] = entries
        else:
            out = entries
        atomic_write(DLOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=10**6))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
