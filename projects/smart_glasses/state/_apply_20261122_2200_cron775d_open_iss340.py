#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-22 21:5x · cron 775d9893 (ARS45 继续执行后继计划) · 项目总工 (moli)
开单 ISS-340 (hw-lead) = 【板↔网表 C1 红根因归属判定】(PCB 线 · 纯分析 + 新建判别闸 · 零写板)

★**为什么 status 直接落 fixing (不过 open 窗口)**:
  ⇒ ★**兄弟 job fb67af40 的 advance.py 只捞 status=open 的单 ⇒ 先落 fixing ⇒ 兄弟 job 看不见 ⇒ 不会重复派 hw-lead** ★
  ⇒ ★**铁律: 一个 agent 同时只允许一个写会话 ⇒ hw-lead 名额由本单占住** ★
幂等: ISS-340 已存在则退出
"""
import io, os, shutil, sys, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "state", "issue_log.yaml")
DISPATCH = os.path.join(ROOT, "state", "dispatch_log.yaml")
BRIEF = os.path.join(ROOT, "state", "dispatch_briefs", "ISS-340_hw_c1_divergence_attribution.md")
BAK = LOG + ".bak_20261122_2200_cron775d_open_iss340"
BAK2 = DISPATCH + ".bak_20261122_2200_cron775d_open_iss340"

ISS = "ISS-340"
OWNER = "hw-lead"

TITLE = (
    "★★[★新主线·PCB 线·纯分析+新建判别闸·零写板] ★★【板↔网表 C1 红根因归属判定: chain_gate ③ PCB 准入 ❌ = C1 焊盘级等价 网表 480 / 板上(带网) 482 ⇒ 多余 2 (`C_VBUS_GND` pad1=GND · pad2=VBUS_5V_CHG) + 同号异网 3 (`Q_PG` pad1 应 PWR_GOOD 实际 PWR_ON · `Q_PG` pad3 应 PWR_ON 实际 PWR_GOOD · `D_ESD_USB_D` pad1 应 NET_USB_D_P_TYPEC 实际 USB_D_P_SRC) ⇒ ★逐条判 [A 网表侧错→改网表就够·板 md5 不用动] / [B 板侧错→必须动板·进板那一趟 B-清单] / [C 等老板拍板→进待拍板页] ★★】★★ ★**板只改一次 ⇒ 这一趟没开工 ⇒ 本单只出【归属判定 + 判别闸】, 一个字节都不许碰板**★ ★**纯分析 / 新建闸类 · 零写板 · 零改网表 · 零落表 · 零改闸 · 零重生成 · 零外发 · 不替老板拍板** ★"
)

DESC = (
    "★**main 2026-11-22 21:5x 本机实读 (`state/chain_gate.py` + `bash state/pcbnew_py.sh state/check_pcb_nets.py` rc=1)★** "
    "⇒ ★**生产链 2 个环节没过 ⇒ 下游产物不许用**: ③ PCB 准入 ❌ (板与网表不等价 ⇒ 板是 11-06 的板, 网表/原理图/BOM 是 11-18 的) + ⑤ 投产包 ❌ (比原理图旧 + doc/sch_src 11 个文件内容不一致)★ "
    "⇒ ★**板只改一次 ⇒ 开工前必须先知道 C1 这 5 条差异各自归谁**: 归网表侧的 ⇒ **板 md5 一个字节都不用动**; 归板侧的 ⇒ 进板那一趟 B-清单 (那一趟一次做完); 归老板拍板侧的 ⇒ 进待拍板页 (本单不代拍)★ "
    "⇒ ★**main 已核出 5 条差异 ↔ 3 条待拍板项的对应关系** (`C_VBUS_GND` ↔ `boss_c_vbus_gnd_reserve_pad_20261117` · `Q_PG` ↔ `boss_shutdown_semantics_and_loadswitch_20261117` + 队列外 `W-4 Q_PG.3 极性` · `D_ESD_USB_D` ↔ `iss260_boss_a3_arch_and_model` / `boss_esd_model_axis_pending_20261117`) ⇒ ★**本单的任务 = 证实或推翻这条对应, 并把它变成机器可判的闸**★ "
    "⇒ ★**注意 C2/C3 全绿** (逐器件脚数 29 个全对 · 器件 185 个不符 0) ⇒ ★**差异不在布局布线, 在网表侧改了 5 行 ⇒ 这正是「板只改一次」最该先查清的地方**★"
)

NOTE = (
    "★★2026-11-22 22:0x · cron 775d9893 开单并派出 (★项目总工 main★) ★★"
    "★**开单依据 (main 本机实读·不抄任何 agent 报告)★**: ① `state/advance.py --json` ⇒ internal=[] / approvals=[] / waiting=0 ⇒ **队列排空** ⇒ 按「开新单」处理 "
    "② ★**ISS-339 已由 main 签收 (fixing→verified·21:51)** ⇒ hw-lead 名额释放 (交卷会话 `agent:hw-lead:subagent:35c16b5d` 于 21:35:46 status=done·runtime 622 s·**不是僵尸单**)★ "
    "③ ★**兄弟 job fb67af40 21:5x 与本 job 同时签 ISS-339 ⇒ 它自己发现「已被签」并**没有覆盖**本 job 的记录 ⇒ 双方结论一致, 无冲突**★ "
    "④ ★**开单动机 = 板那一趟的下一个真前置**: `state/chain_gate.py` 实跑 ⇒ ③ PCB 准入 ❌ (板↔网表不等价) ⇒ ★**这 5 条差异必须先分清归属, 否则板那一趟会改两次**★ ★"
    "★**先落 fixing 再 spawn (★沿用 ISS-337 的老规矩★)**: ⇒ **兄弟 job 的 advance.py 只捞 status=open ⇒ 看不见本单 ⇒ 不会重复派 hw-lead** ⇒ **一个 agent 同时只允许一个写会话**★ ★"
    "★**brief**: `state/dispatch_briefs/ISS-340_hw_c1_divergence_attribution.md` (★`check_brief_commands.py --brief-file` rc=0★) ★ "
    "★**边界**: 零写板 (md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 双证) · 零改网表/原理图/BOM/脚表 (A 桶修法只许写进交付页, 不许真改文件) · 零落表 (agent 不许自签 issue_log) · 零改闸 · 零重生成 (禁 gen_pcb_netlist_board.py 等) · 只写自己分片 (frag_write.py --agent hw-lead) · 零外发 · 不替老板拍板 · 不改 PROJECT_TRACKER.md §0★ ★"
    "★**签收口径**: ★**只有「A 桶 = 只改网表就够 ⇒ 板 md5 不用动」这件事被机器判出来, 本单才算有值** ★ ⇒ ★**判不出来的, 如实写「判不出来」, 不许凑**★"
)

VERIFY_STUB = None


def load(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump(doc, path):
    tmp = path + ".tmp_iss340"
    with io.open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    os.replace(tmp, path)


def main():
    doc = load(LOG)
    issues = doc.get("issues") or []
    for i in issues:
        if i.get("id") == ISS:
            print("IDEMPOTENT: %s already exists (status=%s)" % (ISS, i.get("status")))
            return 0

    if not os.path.exists(BRIEF):
        print("FATAL: brief missing: %s" % BRIEF)
        return 2
    with io.open(BRIEF, "r", encoding="utf-8") as f:
        brief = f.read()

    if not os.path.exists(BAK):
        shutil.copy2(LOG, BAK)

    issues.append({
        "id": ISS,
        "title": TITLE,
        "severity": "high",
        "source_blocker": "ISS-339 · chain_gate ③ PCB 准入 ❌ (板↔网表 C1 不等价)",
        "source_agent": "main",
        "desc": DESC,
        "owner": OWNER,
        "reporter": "main",
        "raised": "2026-11-22",
        "due": "2026-11-23",
        "status": "fixing",
        "external": False,
        "need_keys": [],
        "task_brief": brief,
        "dispatched_at": "2026-11-22",
        "verify_by": "main",
        "verify_result": VERIFY_STUB,
        "note": NOTE,
    })
    doc["issues"] = issues
    dump(doc, LOG)

    ddoc = load(DISPATCH)
    entries = ddoc.get("entries")
    if entries is None:
        entries = []
    if not os.path.exists(BAK2):
        shutil.copy2(DISPATCH, BAK2)
    entries.append({
        "issue": ISS,
        "agent": OWNER,
        "at": "2026-11-22 22:0x",
        "brief": "★★PCB 线·纯分析+新建判别闸·零写板: **板↔网表 C1 红根因归属判定** ⇒ 5 条差异 (多余 2 + 同号异网 3) 逐条判 [A 网表侧错→板 md5 不用动] / [B 板侧错→进板那一趟 B-清单] / [C 等老板拍板] ⇒ 交付 `HW/check_board_netlist_divergence_gate.py` (+--selftest) + `HW/PCB/BOARD_TRIP_NETLIST_DIVERGENCE.md` + 交卷页 + logs/iss340/ + hw.yaml 分片 ★ "
                  "★**开单依据**: advance.py internal=[] (队列排空) + ISS-339 已签收 (21:51) + chain_gate ③ PCB 准入 ❌ (板↔网表不等价, 5 条差异) ★ "
                  "★**先落 fixing 再 spawn ⇒ 兄弟 job fb67af40 的 advance.py 看不见 ⇒ 不重复派 hw-lead** ★ "
                  "★**边界**: 零写板 · 零改网表 · 零落表 · 零改闸 · 零重生成 · 只写自己分片 · 零外发 · 不代拍 ★ "
                  "★**任务书全文**: `state/dispatch_briefs/ISS-340_hw_c1_divergence_attribution.md` (★check_brief_commands.py rc=0★)★",
    })
    ddoc["entries"] = entries
    dump(ddoc, DISPATCH)

    print("OK: %s opened (status=fixing) owner=%s" % (ISS, OWNER))
    print("    brief: %s (%d B)" % (os.path.relpath(BRIEF, ROOT), os.path.getsize(BRIEF)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
