#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main 2026-11-24 15:4x (cron 775d9893 r87) ——
  ① ISS-394 note_addendum: 记录本轮【续跑再派活】的实况 (上一趟被墙掐死 + 自动续跑 failed + 本轮 cont1 再派)
  ② 新开 ISS-395: 钉板闸⑩ 的【并发假红】(★本机实测复现 + 隔离复跑 rc=0 ⇒ 板面没漂移★)
只写 state/issue_log.yaml (main 自己的台账) ⇒ 不碰别人分片。
"""
import os
import shutil
import sys
import time

import yaml

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(PROJ, "state", "issue_log.yaml")
BAK = os.path.join(PROJ, "state", ".bak_issue_log_20261124_1545_cron775d_r87.yaml")

d = yaml.safe_load(open(LOG, encoding="utf-8"))
iss = d["issues"]
by_id = {x.get("id"): x for x in iss}

# ---------- ① ISS-394 note_addendum ----------
t394 = by_id["ISS-394"]
t394["note_addendum"] = (
    "★**2026-11-24 15:4x main (cron 775d9893) 复核 + 续跑再派活**★\n"
    "★**上一趟怎么死的 (★main 本机实读 transcript·不抄任何 agent 报告★)★**: 14:45 起 → 15:15 被 `runTimeoutSeconds` 掐死 ⇒ 15:37:54 被自动续跑 → "
    "**15:41:21 `failed` (墙钟 3.5 分钟)** ⇒ transcript 最后一条 assistant 消息逐字 = 「Existing gates all green. Now let me write the fragment via `frag_write.py`.」"
    "⇒ ★**死因 = 写分片那一步** ⇒ ★**真相页 + 新闸是好的, 缺的是【交卷页 · 分片 · 交卷消息】**★\n"
    "★**main 本机实读的盘面读数 (★15:4x★)★**: `HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md` 在盘 (52,848 B @ 15:12 · §0~§6 + 机器块齐全) · "
    "`HW/check_seat_part_verdict_propagation.py` 在盘 · ★**main 亲手跑 ⇒ rc=1 · 4/7 绿 (K1/K2/K3 红) ⇒ 【红的是现状, 不是闸故障】**★ · "
    "★**`HANDOFF/2026-11-24_hw-lead_ISS394_*.md` 不在盘**★ · ★**`state/fragments/hw.yaml` 里 `iss394` 命中 = 0**★\n"
    "★**本轮动作 (★cron 775d9893 r87·项目总工·续跑再派活★)★**: ★**派 cont1 给 hw-lead**★ (★子会话 `agent:hw-lead:subagent:ec9ee961-e83e-421e-bddc-e2d245645886` · "
    "taskName `advance_iss394_cont1` · ★**runTimeoutSeconds=3600 (★上一趟 30 分钟就掐死了★)·★** brief `state/dispatch_briefs/ISS-394_hw_seat_part_verdict_propagation_cont1.md` · "
    "命令存在性守卫 `state/check_brief_commands.py --brief-file` **rc=0**★) ★★⇒ ★**cont1 = 收尾趟: 交卷页 (新建 B1~B6 + B7) + 分片登记 + 交卷消息**★ ⇒ "
    "★**零写板 · 零落表 · 零改既有闸/既有页正文 · 零挂链 · 零外发 · 不代拍**★ ⇒ 合「板只改一次」纪律 ①★\n"
    "★**特别写死的一条 (★给 cont1·也给 main 以后签收时看★)★**: ★**K1/K2/K3 这三条红要修的是【5 处活副本】(★`HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` "
    "L18/L62/L67/L73/L112 · `state/fragments/hw.yaml` L5271-5272 / L4346-4347 / L8097 · `HW/check_debug_uart_seat_alignment.py` L397★) ⇒ 那是 main 的地界 ⇒ "
    "★**owner 交的是【红的读数 + 每处该改什么 + 代价】, 不是【把红改成绿】**★"
)

# ---------- ② 新开 ISS-395 ----------
if "ISS-395" not in by_id:
    iss.append({
        "id": "ISS-395",
        "title": (
            "★★[★新主线·PCB 线·HW 侧·纯分析+新建闸·零写板] 钉板闸⑩【板侧项全集重跑幂等闸】在【并发跑】时必假红 ⇒ "
            "「板 md5/落表链/结构真值 漂移 ⇒ 板那一趟不许开工」这条红是【假的】 ⇒ 把并发安全变成机器可判 ★★"
        ),
        "severity": "high",
        "source_blocker": "ISS-349",
        "source_agent": "main",
        "desc": (
            "★★[★新主线·PCB 线·HW 侧·纯分析+新建闸·零写板·零落表·零改既有闸的判据·零改既有页面正文·零外发·不代拍]★★\n\n"
            "★**题 (★来源 = ★**cron 775d9893 本 job 2026-11-24 15:2x 例行跑 `state/gate_check.py` 时本机实跑撞出·不抄任何 agent 报告★)★**:\n\n"
            "★**① 现象**: ★**`state/gate_check.py` 的【Q7 钉板 md5 闸链】第 ⑩ 道 (`HW/check_preflight_regen_idempotent.py`, ★**\"板侧项全集重跑幂等闸\"★) 本轮 rc=1** ⇒ "
            "★**闸脚本自己的失败行没解析出来, 只看到一段 traceback 的尾巴**: `OSError: [Errno 39] Directory not empty: "
            "'/home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss349/regen_gate/regen/state'`★ ⇒ "
            "★**闸链据此判定「板 md5 / 落表链 / 结构真值 出现漂移 ⇒ 板那一趟不许开工」** ★★\n\n"
            "★**② 根因 (★main 本机实读源码 + 实跑定位·不是猜★)★**: ★**`HW/check_preflight_regen_idempotent.py` 的沙盒落点是【固定路径】**★ —— "
            "L60 逐字 `SANDBOX = os.environ.get(\"PREFLIGHT_SANDBOX\") or os.path.join(PROJ, \"tmp\", \"iss349\", \"regen_gate\")` ⇒ "
            "★**它不做每次运行唯一化**★ ⇒ ★**L136 `shutil.rmtree(dst)` 在【另一个进程正在往同一个 dst 里写】时就会抛 `Errno 39` (目录非空)★** ⇒ "
            "★**⇒ 这道闸【不是并发安全】的 ⇒ 只要两个 gate_check 同时跑, 必有一个假红**★\n\n"
            "★**③ 是谁在并发 (★main 本机实读源码·★)★**: ★**`state/daily_check.py` L317 逐字 `rc_g, gate = jrun(\"gate_check.py\")` ⇒ 每日巡检链【自己内部就会跑一遍 gate_check】**★ ⇒ "
            "★**cron「ARS45 项目每日巡检」与 cron「ARS45 继续执行后继计划」两个 job 在同一分钟各跑一次 gate_check ⇒ 必撞**★ ⇒ ★**⇒ 【假红是必然事件, 不是偶发】★**\n\n"
            "★**④ main 本机的隔离复跑 (★决定性证据★)★**: ★**用脚本自己支持的 `PREFLIGHT_SANDBOX` 环境变量指向一个【独占】沙盒路径单独跑 ⇒ rc=0**★ ⇒ "
            "★**末行逐字: 「✅ rc=0: ★★页与生成器同源 · 重跑零差异 · 来源全在册 · 必需项在场 ★★」⇒ ⇒ ★★板面【没有】漂移·预检页【没有】漂移·链【没有】漂移★★ ★** ⇒ "
            "★**⇒ ★★这条红是【并发假红】⇒ 【板那一趟不许开工】这条结论本身是假的**★★ ★★\n\n"
            "★**⑤ 为什么这条必须修 (★main 判·不代拍·)★**: ★**① 「板只改一次」那一趟开工前的门禁读数会被这条假红污染 ⇒ 老板/总工看到「板漂移了」会误判**★ · "
            "★**② 更坏的一层: 将来真的漂移时, 这道闸【也会红】⇒ 【红红不可分】⇒ 真漂移会被这条假红淹没**★ ⇒ ★**③ 这正是本项目已记的「判据本身有 bug ⇒ 门禁形同虚设」的同类**★\n\n"
            "★**⑥ 本单要什么 (★只摆选项与代价, 不代拍★)★**: ★**候选甲 = 让沙盒落点每次运行唯一 (★`PREFLIGHT_SANDBOX` 默认值带上 PID/时间戳★) ⇒ 零改判据, 只改落点**★ · "
            "★**候选乙 = `shutil.rmtree` 改成容错 (`ignore_errors=True` / 先 rename 再删) ⇒ 但那样【真冲突】会被静默吞掉**★ · "
            "★**候选丙 = 给 gate_check 加一把跨进程锁 (★`state/` 下建锁文件★) ⇒ 一次只许一个 gate_check 跑 ⇒ 【代价: 巡检链会排队】**★ · "
            "★**候选丁 = 三件一起做 (★唯一化 + 容错 + 锁★) ⇒ 最稳但改动面最大**★ ⇒ ★**【挂不挂新闸进 `state/gate_check.py` 是 main 的地界】**★\n\n"
            "★**⑦ 本单边界 (★照抄★)★**: ★**零写板 · 零落表 · 零改既有闸的【判据/阈值】· 零改既有页面正文 · 零外发 · 不代拍 · 未自签 `state/issue_log.yaml` · "
            "只写 `state/fragments/hw.yaml` · 沙盒只落 `tmp/iss395_sbx/` + `logs/iss395/`**★ ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★"
        ),
        "owner": "hw-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "open",
        "external": False,
        "need_keys": ["iss395_gate10_concurrency_safe_sandbox"],
        "task_brief": (
            "ISS-395 · hw-lead · 把【钉板闸⑩ 的并发假红】变成机器可判。\n\n"
            "★**题**: `HW/check_preflight_regen_idempotent.py` (★\"板侧项全集重跑幂等闸\"★) 的沙盒落点是【固定路径】"
            " (`tmp/iss349/regen_gate`, ★L60 逐字★) ⇒ `shutil.rmtree` (★L136★) 在【两个 gate_check 并发跑】时抛 `OSError: [Errno 39] Directory not empty` "
            "⇒ 闸链判红 ⇒ ★**「板 md5 / 落表链 / 结构真值 漂移 ⇒ 板那一趟不许开工」这条结论是假的**★。\n\n"
            "★**决定性证据 (★main 本机实跑·不抄任何 agent 报告★)★**: ★**① `state/daily_check.py` L317 逐字 `jrun(\"gate_check.py\")` ⇒ 巡检链内部自己会再跑一遍 gate_check "
            "⇒ 「每日巡检」与「继续执行后继计划」两个 cron job 同分钟各跑一次 ⇒ 必撞**★ · "
            "★**② 用 `PREFLIGHT_SANDBOX` 指向独占路径隔离复跑 ⇒ rc=0 (★末行: 「✅ rc=0: 页与生成器同源 · 重跑零差异 · 来源全在册 · 必需项在场」★) ⇒ 板面零漂移**★ · "
            "★**③ 留证: `logs/main_r87_gate10_isolated.log` (★项目盘★)**★\n\n"
            "★**本单要交**: ★**① 真相页 (★新建·★`HW/PCB/BOARD_ONEPASS_GATE10_CONCURRENCY_SAFETY.md`★): 把「并发 ⇒ 假红 ⇒ 板那一趟不许开工」这条因果链写成可复现的机器可判**★ · "
            "★**② 新闸 (★新建·★`HW/check_gate10_concurrency_safety.py`★): 判据至少覆盖 —— (a) ★**并发两跑时两个进程都必须拿到 rc=0·不许有一个假红**★ · "
            "(b) ★**沙盒落点必须每次运行唯一**★ · (c) ★**同一沙盒路径被第二个进程 rmtree 时不许抛未捕获异常**★ · (d) ★**板三项零扰动**★ · "
            "(e) ★**真漂移仍然判红** (★沙盒里改坏一个真源 ⇒ 必须红★ ⇒ ★**不许把「红」改成「绿」来掩盖问题**)★ + `--selftest` 反向用例**★ · "
            "★**③ 交卷页 (★B1~B6 齐全★) + `state/fragments/hw.yaml` 分片登记**★\n\n"
            "★**边界 (★照抄, 不许放宽★)★**: ★**零写板 · 零落表 · 零改既有闸的判据/阈值 (★`HW/check_preflight_regen_idempotent.py` 的判据不许放松·★只许改【落点唯一化】或【加锁】这类不改变判据的改动·"
            "★若你认为必须改判据, 先登记 need 给 main·不许自己改★) · 零改既有页面正文 · 零挂链 (★挂不挂 `state/gate_check.py` 是 main 的地界★) · 零外发 · 不代拍 · "
            "未自签 `state/issue_log.yaml` · 只写 `state/fragments/hw.yaml` · 沙盒只落 `tmp/iss395_sbx/` + `logs/iss395/` (★不落系统 `/tmp`★)**★\n\n"
            "★**板三项基线 (★全程逐字不变★)★**: 板 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`\n\n"
            "★**必跑命令 (★派活前 main 已实跑命令存在性守卫 rc=0★)★**: ★**① `PREFLIGHT_SANDBOX=<独占路径> python3 HW/check_preflight_regen_idempotent.py` (★对照相★) · "
            "② `python3 HW/check_preflight_regen_idempotent.py` (★现状相★) · ③ `python3 HW/check_gate10_concurrency_safety.py` · ④ `python3 HW/check_gate10_concurrency_safety.py --selftest` · "
            "⑤ `python3 state/merge.py` · ⑥ `python3 state/gate_check.py` · ⑦ `md5sum HW/PCB/demo_mainboard.kicad_pcb` (★必须仍是 611b869e…★)**★"
        ),
        "note": (
            "★**2026-11-24 15:4x main (cron 775d9893 r87) 新开并【落 open (不是 fixing)】★** ⇒ "
            "★**派活由队列 job 执行** (★同族先例: ISS-358 / ISS-359 / ISS-384 cont1 …★) ⇒ "
            "★**本轮 r87 里 hw-lead 的槽位被【ISS-394 cont1】占着 (★我亲自派的·★上一趟被墙掐死+自动续跑 failed·★本单缺【交卷页+分片】★) ⇒ "
            "⇒ 本单不与 ISS-394 cont1 并行派给同一个 agent (★铁律: 一个 agent 同时只许一个写会话★)**★\n"
            "★**开单依据 (★main 本机实跑·不抄任何 agent 报告★)★**: ① ★**`state/gate_check.py` 本轮 Q7 钉板闸⑩ rc=1 且闸脚本失败行没解析出来, 只余一段 `OSError: [Errno 39] Directory not empty` 的 traceback 尾巴**★ · "
            "② ★**隔离复跑 (★`PREFLIGHT_SANDBOX` 指向独占路径★) ⇒ rc=0 ⇒ 板面零漂移 ⇒ 这条红是假的**★ · "
            "③ ★**`state/daily_check.py` L317 会再跑一遍 gate_check ⇒ 两个 cron job 同分钟必撞 ⇒ 假红是必然事件**★ · "
            "④ ★**「板只改一次」那一趟开工前的门禁读数会被假红污染; 且【真漂移也会红】⇒ 红红不可分**★"
        ),
    })

shutil.copy2(LOG, BAK)
with open(LOG, "w", encoding="utf-8") as f:
    yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False, width=100000)
print("✅ issue_log.yaml 已写入 (备份: %s)" % os.path.basename(BAK))
print("   ISS-394 note_addendum: %d 字符" % len(t394["note_addendum"]))
print("   ISS-395: 新开 (owner=hw-lead, status=open, severity=high)")
print("   总条数: %d" % len(iss))
