#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-19 01:1x · 派 ISS-338 (sw-lead)** ★

★★**先落 fixing 再 spawn (★硬规则: 反过来会留窗口让下一轮 cron 重复派同一 agent★)★★

★**为什么本轮 advance.py 的 A 段是空的, 还是要派 ISS-338 (★全部本机实读·不抄任何 agent 报告★)**:
  ① `python3 state/advance.py --json` ⇒ ★**`internal: []`** ⇒ 三个总工各被一条 `fixing` 占位 ⇒ ★**A 段自己派不出** ★
  ② ★**sw-lead 的占位 = ISS-335 (fixing)** ⇒ 但 ★**本机实读: 那条会话 `e6b0cd42` 已于 00:51:40 结束 (status=timeout·abortedLastRun=true)·★sw-lead 名下零运行中会话★** ⇒ ★**占位是「已死但已交卷」不是「还在飞」** ★
  ③ ★**按兄弟 job 775d9893 00:55 记进 CROSS_SESSION_NOTE 的「签收三件套」逐件核对 ISS-335 (★不抄 agent 报告★)★**:
     · ★**产物在盘**: 交卷页 `HANDOFF/2026-11-19_sw-lead_ISS335_SW侧准出汇总闸.md` = 33,586 B @00:47 · ★**B0~B6 七块齐全** (★L10 B0 / L38 B1 / L50 B2 / L95 B3 / L118 B4 / L133 B5 / L254 B6★) · ★**占位符 2 处命中 = 两条 grep 命令行本身 (★非占位符★)** ★
     · ★**分片写了**: `grep -c iss335 state/fragments/sw.yaml` = ★**17** (★needs_from 1 条 `iss335_ref_gate_v1_or_v2` + interface_claims 6 条 + 其余命中★) ★
     · ★**闸实测绿 (★本 job 01:1x 本机独立实跑·不是抄它的日志★)★**: `TMPDIR=<项目内> python3 SW/tools/check_onepass_sw_release.py` ⇒ ★**rc=0 (10 道闸 绿 10 / 红 0)★** ⇒ ★**注: 裸跑 rc=2 是本机 `/tmp` 配额到顶的 EDQUOT 假红 (★ISS-318 已记·与本单无关★)⇒ 必须带项目内 TMPDIR★** ★
     · ★**日志在盘**: `logs/iss335/` = 7 件 (00_boundary_before / 01_main_run / 02_selftest / 03_json_run.{json,err} / 04_boundary_after / 05_ref_gate_v2 / 06_final_verify) ★
     · ★**板零变化**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ ★**逐字节未动 (12 天)★** ★
  ④ ★**⇒ 结论: sw-lead 的名额【事实】上空 ⇒ 本轮可派 ⇒ ★但 ISS-335 的 `fixing` 由 main 签收时清 (★签收是 main 的地界·本 job 不签·签两次会让审计出现两条 verified 记录★)★** ★
  ⑤ ★**mech-lead 不碰**: ISS-336 的会话 `83b02df7-c67c…` ★**01:1x 本机实读仍在 running** (★`MECH/check_board_frame_freeze_gate.py` mtime 01:11 还在动★) ⇒ ★**还在飞 ⇒ 本轮不碰** ★
  ⑥ ★**hw-lead 不派**: ISS-337 的会话 `af6f2b4a-a469…` 01:08 已交卷 (★交卷页 21,043 B @01:03★) ⇒ ★**但 hw-lead 名下零 `open` 项 ⇒ 本轮无活可派** ⇒ ★**等 main 签收后才有名额** ★

★**派活前命令存在性守卫**: ★**`python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-338_sw_zero_copper_single_end_fw.md` ⇒ rc=0** ★
  ★**brief 原稿有 2 处必须改 (★不改就不许派·闸已点名★)★**:
    · ★**① §⑤ 标题 `交付物 + 必跑命令` → `交卷物 (4 件) + 必跑命令`**: ★**闸只认「交卷物 (N 件)」口径才把列表项里的路径当【本单产出物】豁免 ⇒ 改之前闸把两条【待新建的产出物】误报成「引用了不存在的路径」** ★
    · ★**② 末句「你名下此刻还有 ISS-335 在跑 ⇒ 本单会等它交卷才轮到你 ⇒ 不许自己去抢」已过期** (★ISS-335 会话 00:51:40 就结束了★) ⇒ ★**照抄这句会让 agent 自己挂起一条 (★白烧一轮预算★)⇒ 改为带时间戳的状态订正 (★ISS-335 已交卷 + 闸 rc=0 的实读证据 + 「不许开第二条 sw-lead 写会话」的纪律照旧保留★)★** ★
  ★**⇒ 除这两处外 brief 全文逐字未改** ★

★**边界 (★ISS-338 自己的 brief §④ 已写死·本 job 不加码也不减码★)★**: ★**零写板 · 零落表 · 零改固件本体 · 零改闸 · 只写 `state/fragments/sw.yaml` (走 `frag_write.py --agent sw-lead`) · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02·不再发信·全靠自己查★) · 不代拍 (★老板那 8 个字母★)** ★
★**本单 = PCB 线·纯分析类·零写板 ⇒ 符合老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」+ 「板只改一次」铁律 (★不碰板·不动网表真源★)★**
★**零写板 · 零落表 · 零改闸 · 零改 agent 分片 · 零外发 · 本 job 全程未调用 message 工具★**
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
STAMP = "20261119_0115_cronfb67_dispatch_iss338"
IID = "ISS-338"
OWNER = "sw-lead"

BRIEF_FILE = os.path.join(HERE, "dispatch_briefs", "ISS-338_sw_zero_copper_single_end_fw.md")
BRIEF = open(BRIEF_FILE, encoding="utf-8").read()

SUMMARY = (
    "★★**派出 (★status 直接落 fixing ⇒ 无 open 窗口 ⇒ 下一轮 in_flight 规则会跳过 sw-lead ⇒ 兄弟 job 775d9893 不会重复派★)** ★ "
    "★**派活依据 (★2026-11-19 01:1x 本机实读★)**: "
    "★**① `advance.py --json` ⇒ `internal: []` (三个总工各被一条 fixing 占位) ⇒ A 段自己派不出** ★ "
    "★**② sw-lead 的占位 ISS-335 的会话 `e6b0cd42` 已于 00:51:40 结束 (status=timeout) ⇒ sw-lead 名下零运行中会话** ★ "
    "★**③ 按 775d9893 00:55 记的「签收三件套」逐件核对 ISS-335: 交卷页 33,586 B @00:47 (B0~B6 齐全) + "
    "`grep -c iss335 state/fragments/sw.yaml` = 17 + `logs/iss335/` 7 件 + 板 md5/mtime 逐字节未动** ★ "
    "★**④ 本 job 01:1x 本机独立实跑 `TMPDIR=<项目内> python3 SW/tools/check_onepass_sw_release.py` ⇒ rc=0 (10 道闸绿 10/红 0) "
    "⇒ 裸跑 rc=2 是本机 /tmp 配额到顶的 EDQUOT 假红 (ISS-318 已记) ⇒ 与本单无关** ★ "
    "★**⇒ sw-lead 名额事实为空 ⇒ 本轮可派 (★ISS-335 的 fixing 由 main 签收时清·本 job 不签·避免两条 verified 记录★)** ★ "
    "★**⑤ mech-lead 不碰 (ISS-336 会话 `83b02df7` 01:1x 仍在 running)** ★ "
    "★**⑥ hw-lead 无 open 项 (ISS-337 会话 01:08 已交卷·等 main 签收才有名额)** ★ "
    "★**⑦ 派活前守卫: `check_brief_commands.py --brief-file state/dispatch_briefs/ISS-338_sw_zero_copper_single_end_fw.md` ⇒ rc=0** ★ "
    "★**brief 只改 2 处 (★§⑤ 标题改「交卷物 (4 件)」让闸认这是本单产出物 + 末句「ISS-335 在跑」状态订正·其余逐字未改★)** ★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · 零落表 · "
    "零改固件本体 (SW/** 既有文件 md5 不变) · 零改闸 · 只写 `state/fragments/sw.yaml` (走 `frag_write.py --agent sw-lead`) · "
    "零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不代拍那 8 个字母 · 不自签 issue_log ★"
)


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

        it = idx.get(IID)
        if it is None:
            applied.append("★★ %s 不存在 ⇒ 中止 (不新建) ★★" % IID)
            return 2

        if it.get("status") == "open":
            it["status"] = "fixing"
            applied.append("%s status: open → fixing (★先落 fixing 再 spawn★)" % IID)
        elif it.get("status") == "fixing":
            applied.append("%s 已是 fixing ⇒ 幂等跳过" % IID)
        else:
            applied.append("★★ %s status=%s (≠open) ⇒ 中止 (绝不重复派) ★★" % (IID, it.get("status")))
            return 2

        it["dispatched_at"] = "2026-11-19"
        it["task_brief"] = BRIEF
        applied.append("%s task_brief ⇒ 指向 dispatch_briefs 文件全文 (★与落盘 brief 同一份真源★)" % IID)
        it["note"] = (
            "★2026-11-19 01:1x cron fb67af40 派出 (★先落 fixing 再 spawn ⇒ 无 open 窗口·下一轮 in_flight 会跳过 sw-lead★)★ "
            "★**依据**: advance.py A 段 internal=[] (三个总工各被 fixing 占位) + "
            "sw-lead 的占位 ISS-335 会话已于 00:51:40 结束 (产物齐全 + 闸实测 rc=0 ⇒ 名额事实为空) + "
            "mech-lead 的 ISS-336 会话 01:1x 仍在跑 (不碰) + hw-lead 名下零 open (等 main 签收)★ "
            "★**任务书全文**: `state/dispatch_briefs/ISS-338_sw_zero_copper_single_end_fw.md` "
            "(★`check_brief_commands.py --brief-file` rc=0★)★ "
            "★**上游** = ISS-334 (verified) need-4a (★口径见 `state/fragments/pm.yaml` 的 answers 里 "
            "`iss334_need4a_single_end_net_usage`·已核存在★)★"
        )
        applied.append("%s note ⇒ 换成本轮派活依据" % IID)

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10 ** 6))

        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or {}
        entries = dlog.get("dispatches") or []
        if not any(e.get("issue") == IID for e in entries):
            entries.append({
                "issue": IID,
                "agent": OWNER,
                "at": "2026-11-19",
                "brief": SUMMARY,
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-19 01:1x · "
                    "★**先落 fixing 再 spawn ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"
                ),
            })
            applied.append("dispatch_log.yaml += %s %s 1 条" % (IID, OWNER))
            atomic_write(DLOG, yaml.safe_dump(dlog, allow_unicode=True, sort_keys=False, width=10 ** 6))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
