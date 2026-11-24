#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-25 03:15 · job fb67af40「ARS45 队列自动派活」
★生成 ISS-409 / ISS-410 / ISS-411 的 cont1 续派 brief (★断点续做头 + 原 brief 全文★)
=========================================================================================
★**为什么是 cont1 而不是从零重开 (★main 本机实读, 不抄任何 agent 报告★)**:
  · `~/.openclaw/subagents/runs.json` 实读: 三条 run 的 `runTimeoutSeconds` **都是 5400 (90 分钟)**
  · 三条却都在起后 ~11 分钟、且在【同一 1.2 秒窗口 03:03:28.846~03:03:29.972】一起死
    (ISS-410 03:03:28.846 / ISS-409 03:03:29.730 / ISS-411 03:03:29.972)
  · ⇒ ★**死因 = 外部共因中断 (与 2026-11-23 21:51:49、2026-11-25 02:07:37~02:07:40 同型) ⇒ 不是自己超时★**
  · ⇒ ★**上一趟不是空壳**: 真相页/新闸/部分分片【已经在盘】⇒ 本趟 = 从断点接着做 ⇒ 不许推倒重写★**
★**本脚本边界**: ★**只写 3 个 cont1 brief 文件 + 原子追加 3 条 dispatch_log** ⇒
  ★**不碰 issue_log (status 保持 fixing ⇒ advance.py in_flight 继续挡住下一轮重复派) ★**
  ★**不碰分片 / 板 / 网表 / 脚表 / BOM / outbox / 决策页 ★**
"""
import os
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEFS = os.path.join(HERE, "dispatch_briefs")
DL = os.path.join(HERE, "dispatch_log.yaml")

TS = "2026-11-25 03:15"
JOB = "cron fb67af40 (ARS45 队列自动派活)"

# ★★★ 共因死因段 (三条共用, 逐字一致) ★★★
COMMON_DEATH = """★★【★★★ cont1 · 断点续做 · 上一趟被【共因掐死】★★★】★★
★**死因 (main 本机实读 `~/.openclaw/subagents/runs.json` + 三个 transcript 末条, 不抄任何 agent 报告)**:
  · 上一趟的 `runTimeoutSeconds` = **5400 (90 分钟)**, **没到** ⇒ **不是你超时**
  · 三条会话 (ISS-409 / ISS-410 / ISS-411) 在起后 ~11 分钟、且在【**同一 1.2 秒窗口 03:03:28.846~03:03:29.972**】一起死
    ⇒ **共因中断** (与 2026-11-23 21:51:49、2026-11-25 02:07:37~02:07:40 同型)
  · ⇒ **本趟 = 从【已在盘的东西】接着做, 不是从零做 ⇒ 已在盘的读数直接用, 不要重跑** (★重跑一遍要几分钟到几十分钟, 而你可能又被掐★)
★★**三条硬纪律 (★因为【你随时可能被掐】★★)**:
  ① ★**先落盘, 后汇报**★ —— 每完成一件交付物**立刻**写盘 (★别攒到最后一起写★)
  ② ★**交卷页 + 自有分片 优先**★ —— 这两个是 main 签收的凭据 ⇒ **先把它们写完**, 其余往后排
  ③ ★**如果你感觉时间紧 ⇒ 交卷页 + 分片 + 一份短报告交上来, 剩下的写进交卷页的「未完成」段**★ ⇒ ★**不许交半份然后什么都不留★**
★★**不许做的事 (★与原 brief 一致, 本头不放松★)**:
  ★**零写板 · 零落表 (除自有分片) · 零改既有闸判据 · 零改既有脚本 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml` ★**
★★**已在盘的真相页/新闸 ⇒ 【不许推倒重写】, 只许【追加式】补 (★补之前先记下它现在的字节数 + md5, 补之后记补后的, 两组数字都写进交卷页★)** ★
"""

STD_TAIL = """★额外纪律: ① 写分片必须用 state/frag_write.py (禁止 open(p,"w")) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ⑤ 交卷前跑 python3 state/merge.py (rc 必须 0) && python3 state/gate_check.py (Q1 必须 18/18) 并把输出贴进回复
"""

SPECS = {
    "ISS-409": {
        "agent": "hw-lead",
        "role": "硬件总工",
        "src": "ISS-409_hw_release_chain_teeth_audit.md",
        "dst": "ISS-409_hw_release_chain_teeth_audit_cont1.md",
        "task_name": "queue_iss409_cont1",
        "landed": """★★【已在盘 (★main 本机实测, 直接用, 不要重做★)】★★
| 交付物 | 状态 |
|---|---|
| ★**① 真相页 `HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md`** ★ | ★**已在盘 · 58,163 B @ 02:58:55** ★ |
| ★**② 新闸 `HW/check_onepass_release_chain_teeth.py`** ★ | ★**已在盘 · 58,081 B @ 02:57:23** ★ · ★**main 本机实测裸跑 rc=1 (★红的是现状, 不是闸故障★)** ★ |
| ★**③ `state/fragments/hw.yaml` 收口** ★ | ★**已在盘 (★mtime 02:59:51 · 命中 ISS-409 17 处★)** ★ |
★★【本趟【还缺】的 (★这才是你的活★)】★★
| # | 待补 | 说明 |
|---|---|---|
| ★**④ 交卷页** ★ | ★**新建 `HANDOFF/2026-11-25_hw-lead_ISS409_放行链牙齿清账与闸.md`** ★ | ★**main 实测: 不在盘 ⇒ 上一趟被掐在写交卷页之前★** · ★**B1~B7 全填 (★`state/gate_check.py` Q1 六块齐全★) ★** |
| ★**⑤ `--selftest` 实跑留证 + merge / gate_check 终跑 + 边界自证表** ★ | ★**上一趟的最后一条工具调用是在跑 `state/gate_check.py` 时被掐的 ⇒ merge 已 rc=0 (★产出 927★) 但 gate_check 的终跑输出【没进交卷页】★★ ⇒ ★**必跑一次并把输出逐字贴进交卷页★** ★ |
| ★**⑥ 交卷报告 (回复正文)** ★ | ★**按 main 的验收口径写: 读数 / 交付物 / rc 逐条 / 边界自证 / 留给 main 的问句 (★一条都不代拍★) ★** |
★★**两条特别提醒**★★
  · ★**真相页/新闸已经 58 KB 级, 是上一趟的成果 ⇒ 本趟只许追加式补 (★不许推倒重写★) ★**
  · ★**板 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` —— 19 天逐字节未动 ⇒ 本趟必须仍是这三项逐字相同★** ★""",
    },
    "ISS-410": {
        "agent": "mech-lead",
        "role": "结构总工",
        "src": "ISS-410_mech_premise_tier_decision_table.md",
        "dst": "ISS-410_mech_premise_tier_decision_table_cont1.md",
        "task_name": "queue_iss410_cont1",
        "landed": """★★【已在盘 (★main 本机实测, 直接用, 不要重做★)】★★
| 交付物 | 状态 |
|---|---|
| ★**① 真相页 `MECH/BOARD_ONEPASS_PREMISE_TIER_DECISION_TABLE.md`** ★ | ★**已在盘 · 84,024 B @ 02:57:46** ★ |
| ★**② 新闸 `MECH/check_premise_tier_decision.py`** ★ | ★**已在盘 · 40,949 B @ 02:58:48** ★ · ★**main 本机实测裸跑 rc=1 (★红的是现状: T1 四来源不一致 / T2 板面是 SMD 占位判定不出档位 / T3 档位至今没拍板·★不是闸故障★)** ★ |
| ★**③ `state/fragments/mech.yaml` 收口** ★ | ★**✘ 还没写** ★★**main 实测: `grep -ciE "iss409|iss410|iss411" state/fragments/mech.yaml` = 0 ⇒ 上一趟被掐在写分片之前★** ★ |
★★【本趟【还缺】的 (★这才是你的活★)】★★
| # | 待补 | 说明 |
|---|---|---|
| ★**③' `state/fragments/mech.yaml` 收口 (★最高优先★)** ★ | ★**只走 `state/frag_write.py` (★禁止 `open(p,"w")`★) · 写后四项自检: 条数 / 丢 key / 多的 key / 内容有变的条 (★老条目逐字比对★) ★** | ★**这是 main 签收的凭据之一 ⇒ 【先写它】★★ |
| ★**④ 交卷页** ★ | ★**新建 `HANDOFF/2026-11-25_mech-lead_ISS410_前提量选档决策表与闸.md`** ★ | ★**main 实测: 不在盘★** · ★**B1~B7 全填 (★`state/gate_check.py` Q1 六块齐全★) ★** |
| ★**⑤ `--selftest` 实跑留证 + merge / gate_check 终跑 + 边界自证表** ★ | ★**必跑一次并把输出逐字贴进交卷页★** ★ |
| ★**⑥ 交卷报告 (回复正文)** ★ | ★**读数 / 交付物 / rc 逐条 / 边界自证 / 留给 main 的问句 (★一条都不代拍★) ★** |
★★**三条特别提醒**★★
  · ★**真相页/新闸已经 84 KB / 41 KB 级, 是上一趟的成果 ⇒ 本趟只许追加式补 (★不许推倒重写★) ★**
  · ★**上一趟最后一句是「M1 was already red before my change (roster page predates ISS-407's gate)」⇒ 那是 ISS-405 那道闸 (`check_mech_gate_hook_coverage.py`) 的 M1 红, ★【不是本单造成的, 不许去擦它】★★**
  · ★**「板厂工艺能力」那一格 ⇒ 只能【自己上网查公开官网工艺能力页】+ 标证据等级 + 查不到就写降级方案 ⇒ 【不许挂成「等外部确认」, 更不许外发问询】★★**
  · ★**板 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` —— 19 天逐字节未动 ⇒ 本趟必须仍是这三项逐字相同★** ★""",
    },
    "ISS-411": {
        "agent": "sw-lead",
        "role": "软件总工",
        "src": "ISS-411_sw_mustchange_face_impact.md",
        "dst": "ISS-411_sw_mustchange_face_impact_cont1.md",
        "task_name": "queue_iss411_cont1",
        "landed": """★★【已在盘 (★main 本机实测, 直接用, 不要重做★)】★★
| 交付物 | 状态 |
|---|---|
| ★**② 新闸 `SW/tools/check_sw_mustchange_face_impact.py`** ★ | ★**已在盘 · 38,714 B @ 02:58:49** ★ · ★**main 本机实测裸跑 rc=1 (★2/9 通过 · 命门 = 链上跑的 `SW/tools/check_onepass_sw_sync.py`(20 处) + `SW/tools/check_sw_ref_reachability.py`(55 处) 两道【都在链上且都硬编位号】· ★红的是现状, 不是闸故障★)** ★ |
| ★**① 真相页 `SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md`** ★ | ★**✘ 还没落盘** ★★**main 实测: 该文件【不存在】⇒ 上一趟被掐在写真相页之前 ⇒ 这是本趟最大的一件★** ★ |
| ★**③ `state/fragments/sw.yaml` 收口** ★ | ★**✘ 还没写** ★★**main 实测: `grep -ciE "iss409|iss410|iss411" state/fragments/sw.yaml` = 0 ★** ★ |
★★【本趟【还缺】的 (★这才是你的活★)】★★
| # | 待补 | 说明 |
|---|---|---|
| ★**①' 真相页** ★ | ★**新建 `SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md`** ★ | ★**§0~§7 + 机器块 + 原 brief §2.1 要求的【三张表】(a) 31 道闸 × 输入面 × 硬编位号逐条清单 (★含「判绿变判红 / 判红变判绿 / 静默跳过」三分类的逐条判断依据★) (b) 「改名面」受影响闸清单 + 「布线面」要重锚的 17 道逐道 (★基线钉在哪 / 那一趟后会不会变 / 变了对判据意味着什么★) (c) 「那一趟之前必须先改/先重锚的闸」排序清单 (★按后果: 误判放行 > 误判阻塞 > 静默跳过★)★** ★ |
| ★**③' `state/fragments/sw.yaml` 收口 (★高优先★)** ★ | ★**只走 `state/frag_write.py` (★禁止 `open(p,"w")`★) · 四项自检★★** | ★**main 签收的凭据之一 ⇒ 【先写它】★★ |
| ★**④ 交卷页** ★ | ★**新建 `HANDOFF/2026-11-25_sw-lead_ISS411_SW必改面影响面清账与闸.md`** ★ | ★**main 实测: 不在盘★** · ★**B1~B7 全填 (★`state/gate_check.py` Q1 六块齐全★) ★** |
| ★**⑤ `--selftest` 实跑留证 + merge / gate_check 终跑 + 边界自证表** ★ | ★**必跑一次并把输出逐字贴进交卷页★** ★ |
| ★**⑥ 交卷报告 (回复正文)** ★ | ★**读数 / 交付物 / rc 逐条 / 边界自证 / 留给 main 的问句 (★一条都不代拍★) ★** |
★★**三条特别提醒**★★
  · ★**上一趟被掐时正在写新闸的代码 (transcript 末段是 `judge_c1()` 函数体) ⇒ 【先跑一次 `python3 SW/tools/check_sw_mustchange_face_impact.py --selftest` 确认闸文件没写残】; 若有残缺, ★**追加式补齐, 不许推倒重写★ (★它 38 KB 已经在了★) ★**
  · ★**真相页从零写起 (★它是本趟最大的一件 ⇒ 【先写它】, 写完立刻落盘, 再写分片和交卷页★) ★**
  · ★**板 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` —— 19 天逐字节未动 ⇒ 本趟必须仍是这三项逐字相同★** ★""",
    },
}


def atomic_write(path: str, content: str) -> None:
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    # ---------- 1. 生成 cont1 brief ----------
    written = []
    for iss, spec in SPECS.items():
        src = os.path.join(BRIEFS, spec["src"])
        with open(src, encoding="utf-8") as f:
            orig = f.read()
        head = (
            "# ★★[cont1 续派 · %s] %s · %s\n\n"
            % (iss, spec["agent"], spec["role"])
            + "【项目总工派活 · 队列自动推进 · 闭环 %s (cont1)】你是 %s。\n" % (iss, spec["role"])
            + COMMON_DEATH
            + "\n"
            + spec["landed"]
            + "\n\n"
            + "---以下是原 brief 全文 (★题面 / 交付口径 / 边界 / 自检命令 一律以它为准★)---\n\n"
            + orig
            + "\n\n---\n\n"
            + STD_TAIL
        )
        dst = os.path.join(BRIEFS, spec["dst"])
        atomic_write(dst, head)
        written.append((iss, spec, dst, len(head)))
        print("★ wrote %s (%d chars) -> %s" % (iss, len(head), spec["dst"]))

    # ---------- 2. 原子追加 dispatch_log ----------
    import yaml

    with open(DL, encoding="utf-8") as f:
        log = yaml.safe_load(f) or []
    if not isinstance(log, list):
        raise SystemExit("★dispatch_log.yaml 结构异常 (不是 list) ⇒ 拒绝写")
    before = len(log)
    for iss, spec, dst, n in written:
        log.append({
            "issue": iss,
            "agent": spec["agent"],
            "at": TS,
            "brief": (
                "★★[cont1 续派 · 断点续做] %s · ★**上一趟 (02:51~03:03) 被【共因掐死】: runTimeoutSeconds=5400 (90 分钟) 根本没到, "
                "三条会话在【同一 1.2 秒窗口 03:03:28.846~03:03:29.972】一起死 ⇒ 不是自己超时, 是外部共因中断★** ★"
                "★**上一趟不是空壳: 真相页/新闸/部分分片已在盘 ⇒ 本趟从断点接着做, 不许推倒重写★** ★"
                "★★**纯查证/纯分析/新建真相页 + 新建机器闸类 (零写板·零落表(除自有分片)·零改既有闸判据·零改既有脚本·零改既有页正文·零挂链·零外发·不代拍) "
                "⇒ 合「板只改一次」纪律 ①** ★"
                % iss
            ),
            "brief_file": "state/dispatch_briefs/" + spec["dst"],
            "job": (
                JOB
                + " · ★2026-11-25 03:1x · ★**cont1 续派 (★status 保持 fixing 不动 ⇒ advance.py 的 in_flight 规则继续挡住任何 job 再给该 agent 派活 ⇒ 零撞车窗口★) ★"
                + "· ★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file` 三份全 rc=0 (本轮亲跑) ★"
                + "· ★**派活前 main 本机实测三与判据**: 已落盘 (真相页/新闸/部分分片在盘) + 会话已死 (status=timeout·endedAt 03:03:2x·runTimeoutSeconds=5400 未到 ⇒ 共因) + 交卷页不在盘 ⇒ ★**⇒ 续做, 不是重开, 不是僵尸复活** ★"
                + "· ★**本轮新增一条派活纪律**: brief 里写死【先落盘, 后汇报】+【交卷页 + 自有分片优先】⇒ 因为子会话随时可能被共因掐死 ★"
            ),
            "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★ · ★本趟 = 从上一趟已落的活续做, 不是从零★",
            "task_name": spec["task_name"],
            "dispatched_at": TS,
            "redispatch_zombie": True,
            "death_cause": "★共因中断 (三条同秒死 · runTimeoutSeconds=5400 未到) ⇒ 上一趟非空壳, 已落盘部分产物·只缺收尾★",
        })
    bak = DL + ".bak_20260725_0315_cronfb67af40_cont1_409_410_411"
    shutil.copy2(DL, bak)
    atomic_write(DL, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100000))
    print("★ dispatch_log: %d -> %d 条 (bak: %s)" % (before, len(log), os.path.basename(bak)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
