#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-22 22:3x · cron 775d9893 (ARS45 继续执行后继计划) · 项目总工 (moli)
开单 ISS-341 (mech-lead) = 【「板那一趟」画哪块板 的相容性机器判定闸】
(PCB 线 · 纯分析 + 新建闸 + 一页决策口径 · 零写板)

★**为什么 status 直接落 fixing (不过 open 窗口)**:
  ⇒ ★**兄弟 job fb67af40 的 advance.py 只捞 status=open 的单 ⇒ 先落 fixing ⇒ 兄弟 job 看不见 ⇒ 不会重复派** ★
  ⇒ ★**铁律: 一个 agent 同时只允许一个写会话 ⇒ mech-lead 名额由本单占住 (hw-lead 名额被 ISS-340 cont1 占着)** ★
幂等: ISS-341 已存在则退出
"""
import io, os, shutil, sys, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "state", "issue_log.yaml")
DISPATCH = os.path.join(ROOT, "state", "dispatch_log.yaml")
BRIEF = os.path.join(ROOT, "state", "dispatch_briefs",
                     "ISS-341_mech_frame_candidate_compat_gate.md")
BAK = LOG + ".bak_20261122_2230_cron775d_open_iss341"
BAK2 = DISPATCH + ".bak_20261122_2230_cron775d_open_iss341"

ISS = "ISS-341"
OWNER = "mech-lead"

TITLE = (
    "★★[★新主线·PCB 线·纯分析+新建判定闸·零写板] ★★【「板那一趟」画哪块板: U-1 板框冻结三候选 (B160x100 / F30A 60×30 / P60×15) × 现役板 的相容性机器判定 "
    "⇒ 现役板 = 160×100 / 8 铜层 / 1.60mm / 186 封装 / RK3572-SOM 承载区 (J_SOM_P1..P4 占位 53.60×46.08mm) "
    "⇒ 承载区高 46mm ≫ F30A 板高 30 (超 +16.08) ≫ P60×15 板高 15 (超 +31.08) ⇒ ②/③ 候选装不进现役板 ⇒ "
    "拍 ②/③ = 【重画一块新板】而不是【改现役板一次】⇒ 「板只改一次」的口径会当场失效 ⇒ "
    "须把「这一趟画哪块物理产品」(上位) 与「那块板用哪个框」(下位, U-1) 分两层分开】★★ "
    "★**纯分析 / 新建闸类 · 零写板 · 零改既有 MECH 文件 · 零改 HW 文件 · 零落表 · 零重生成 · 零外发 · 不替老板拍板** ★"
)

DESC = (
    "★**main 2026-11-22 22:2x 本机实读 (不抄任何 agent 报告)★** ⇒ ★**6 条事实**: "
    "① 现役板 Edge.Cuts = 4 条 gr_line (0,0)-(160,0)-(160,100)-(0,100) ⇒ **160×100mm**; "
    "② `(layers)` = F.Cu + In1..In6 + B.Cu ⇒ **8 铜层** + `(general (thickness 1.6))` ⇒ **1.60mm** + footprint 块数 **186**; "
    "③ `HW/PCB/BOARD_FRAME_CALIBER.md` §2 ```json cal:FRAMES``` ⇒ `current_frame = B160x100` (三帧里只有它 current=true); "
    "④ 4 个 J_SOM_P* 封装 pad 绝对坐标并集 = x 15.20..68.80 / y 7.96..54.04 ⇒ **SoM 承载区 53.60 × 46.08mm** (按 pad 外形算 = 53.80×46.78, ISS-274 §3); "
    "⑤ ⇒ **承载区高 46.08mm ≫ F30A 板高 30mm (超 +16.08) / ≫ P60×15 板高 15mm (超 +31.08)** ⇒ 现有这两个候选框装不下现役板; "
    "⑥ `MECH/BOARD_GEOM_30MM.md` = **RK3576 口径 (grep: RK3576 ×14 / RK3572 ×0)** 而主控 2026-11-02 已换 RK3572 ⇒ **②/③ 候选隐含的是另一种物理产品 (RK3576 SoC 直上板), 不是现役板换个尺寸** ★ "
    "⇒ ★**所以 U-1 现在这个问法本身有洞**: ★**ISS-310 落表的建议默认值 = F30A, 理由是「36 档里唯一在【结构外形判据】上全绿」—— 但那 36 档判的是「台架板装不进眼镜」, 而台架板本来就是台架板 (ISS-169: 不装电池 · Type-C · 板上只有这一块) ⇒ 「装不进眼镜」≠「这一趟画不了」⇒ 「唯一全绿 ⇒ 这一趟该画 F30A」这个推理跳了一步** ★ "
    "⇒ ★**本单的任务 = 把这一跳补成机器可判的相容性矩阵, 并把 U-1 的题面从「三选一」升级成「上位: 这一趟画哪块物理产品 / 下位: 那块板用哪个框·层数·板厚」** ★ "
    "⇒ ★**只有这条被判出来, 「板只改一次」这条主线才有个站得住的前提; 判不出来的, 如实写「判不出来」, 不许凑** ★"
)

NOTE = (
    "★★2026-11-22 22:3x · cron 775d9893 开单并派出 (★项目总工 main★) ★★ "
    "★**开单依据 (main 本机实读·不抄任何 agent 报告)★**: ① `python3 state/advance.py --json` ⇒ internal=[] / approvals=[] / waiting=0 / decisions=40 ⇒ **队列排空** ⇒ 按「开新单」处理 "
    "② ★**hw-lead 名额被 ISS-340 占着** (★兄弟 job fb67af40 22:16 派 cont1, 子会话 `agent:hw-lead:subagent:a493c424` status=running ⇒ 本轮 22:2x `sessions_list` 实查: **hw-lead 在跑, mech-lead 零在跑** ⇒ 本单派 mech-lead, 不碰 hw-lead★) "
    "③ ★**为什么是 mech-lead**: 本单是 U-1 板框冻结的判定闸, 而 `MECH/check_board_frame_freeze_gate.py` (ISS-336) 已在 mech-lead 名下 ⇒ 属地正确 + 不与 ISS-340 抢写 "
    "④ ★**为什么必须是本单**: `DECISION_ONE_PAGER_2026-11-22.md` §① 第 5 项 (U-1) 写着建议默认值 = F30A ⇒ **若这个默认值站不住, 老板拍的第一个字就把整条主线带偏** ⇒ 必须先有机器判据 ★ "
    "★**先落 fixing 再 spawn (★沿用 ISS-337/339/340 的老规矩★)**: ⇒ **兄弟 job 的 advance.py 只捞 status=open ⇒ 看不见本单 ⇒ 不会重复派** ★ "
    "★**brief**: `state/dispatch_briefs/ISS-341_mech_frame_candidate_compat_gate.md` (6,947 B · ★`check_brief_commands.py --brief-file` rc=0★) ★ "
    "★**边界**: 零写板 (md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 双证) · 零改既有 MECH 文件 (check_board_frame_freeze_gate.py / board_frame_feasibility.py / BOARD_GEOM_30MM.md / pinset2_mech_check.py) · 零改 HW 文件 · 零落表 (agent 不许自签 issue_log) · 零重生成 · 只写自己分片 (frag_write.py --agent mech-lead) · 零外发 · 不替老板拍板 · 不改 PROJECT_TRACKER.md §0 ★ "
    "★**签收口径**: ★**只有「三候选 × 现役板」的相容性矩阵 + 「改一次 / 重画新板」的机器判决 + U-1 题面该不该改写 这三件事被机器判出来, 本单才算有值** ★"
)


def load(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump(doc, path):
    tmp = path + ".tmp_iss341"
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
        "source_blocker": "ISS-310 (U-1 板框冻结) · DECISION_ONE_PAGER_2026-11-22.md §① 第 5 项",
        "source_agent": "main",
        "desc": DESC,
        "owner": OWNER,
        "reporter": "main",
        "raised": "2026-11-22",
        "due": "2026-11-23",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss310_main_board_frame_u1_decision"],
        "task_brief": brief,
        "dispatched_at": "2026-11-22",
        "verify_by": "main",
        "verify_result": None,
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
        "at": "2026-11-22 22:3x",
        "brief": "★★PCB 线·纯分析+新建判定闸·零写板: **「板那一趟」画哪块板** ⇒ U-1 三候选 (B160x100 / F30A 60×30 / P60×15) × 现役板 (160×100 / 8层 / 1.60mm / 186封装 / RK3572-SOM 承载区 46.08mm 高) 的相容性矩阵 + 「改一次 / 重画新板」机器判决 + U-1 题面该不该改写 ⇒ 交付 `MECH/check_board_frame_candidate_compat_gate.py` (+--selftest ≥6 用例, 末行 ALL TESTS PASS) + `MECH/BOARD_TRIP_FRAME_DECISION_MATRIX.md` + 交卷页 B0~B7 + logs/iss341/ + mech.yaml 分片 ★ "
                  "★**开单依据**: advance.py internal=[] (队列排空) + hw-lead 被 ISS-340 cont1 占着 (在跑) ⇒ 派 mech-lead (零在跑) + U-1 的建议默认值 (F30A) 用「36 档结构判据唯一全绿」推出 ⇒ 跳了一步 (台架板装不进眼镜 ≠ 这一趟画不了) ★ "
                  "★**先落 fixing 再 spawn ⇒ 兄弟 job fb67af40 的 advance.py 看不见 ⇒ 不重复派 mech-lead** ★ "
                  "★**边界**: 零写板 · 零改既有 MECH 文件 · 零改 HW 文件 · 零落表 · 零重生成 · 只写自己分片 · 零外发 · 不代拍 ★ "
                  "★**任务书全文**: `state/dispatch_briefs/ISS-341_mech_frame_candidate_compat_gate.md` (★check_brief_commands.py --brief-file rc=0★)★",
    })
    ddoc["entries"] = entries
    dump(ddoc, DISPATCH)

    print("OK: %s opened (status=fixing) owner=%s" % (ISS, OWNER))
    print("    brief: %s (%d B)" % (os.path.relpath(BRIEF, ROOT), os.path.getsize(BRIEF)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
