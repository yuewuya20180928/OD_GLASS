ISS-395 · hw-lead · 把【钉板闸⑩ 的并发假红】变成机器可判。

★**题**: `HW/check_preflight_regen_idempotent.py` (★"板侧项全集重跑幂等闸"★) 的沙盒落点是【固定路径】 (`tmp/iss349/regen_gate`, ★L60 逐字★) ⇒ `shutil.rmtree` (★L136★) 在【两个 gate_check 并发跑】时抛 `OSError: [Errno 39] Directory not empty` ⇒ 闸链判红 ⇒ ★**「板 md5 / 落表链 / 结构真值 漂移 ⇒ 板那一趟不许开工」这条结论是假的**★。

★**决定性证据 (★main 本机实跑·不抄任何 agent 报告★)★**: ★**① `state/daily_check.py` L317 逐字 `jrun("gate_check.py")` ⇒ 巡检链内部自己会再跑一遍 gate_check ⇒ 「每日巡检」与「继续执行后继计划」两个 cron job 同分钟各跑一次 ⇒ 必撞**★ · ★**② 用 `PREFLIGHT_SANDBOX` 指向独占路径隔离复跑 ⇒ rc=0 (★末行: 「✅ rc=0: 页与生成器同源 · 重跑零差异 · 来源全在册 · 必需项在场」★) ⇒ 板面零漂移**★ · ★**③ 留证: `logs/main_r87_gate10_isolated.log` (★项目盘★)**★

★**本单要交**: ★**① 真相页 (★新建·★`HW/PCB/BOARD_ONEPASS_GATE10_CONCURRENCY_SAFETY.md`★): 把「并发 ⇒ 假红 ⇒ 板那一趟不许开工」这条因果链写成可复现的机器可判**★ · ★**② 新闸 (★新建·★`HW/check_gate10_concurrency_safety.py`★): 判据至少覆盖 —— (a) ★**并发两跑时两个进程都必须拿到 rc=0·不许有一个假红**★ · (b) ★**沙盒落点必须每次运行唯一**★ · (c) ★**同一沙盒路径被第二个进程 rmtree 时不许抛未捕获异常**★ · (d) ★**板三项零扰动**★ · (e) ★**真漂移仍然判红** (★沙盒里改坏一个真源 ⇒ 必须红★ ⇒ ★**不许把「红」改成「绿」来掩盖问题**)★ + `--selftest` 反向用例**★ · ★**③ 交卷页 (★B1~B6 齐全★) + `state/fragments/hw.yaml` 分片登记**★

★**边界 (★照抄, 不许放宽★)★**: ★**零写板 · 零落表 · 零改既有闸的判据/阈值 (★`HW/check_preflight_regen_idempotent.py` 的判据不许放松·★只许改【落点唯一化】或【加锁】这类不改变判据的改动·★若你认为必须改判据, 先登记 need 给 main·不许自己改★) · 零改既有页面正文 · 零挂链 (★挂不挂 `state/gate_check.py` 是 main 的地界★) · 零外发 · 不代拍 · 未自签 `state/issue_log.yaml` · 只写 `state/fragments/hw.yaml` · 沙盒只落 `tmp/iss395_sbx/` + `logs/iss395/` (★不落系统 `/tmp`★)**★

★**板三项基线 (★全程逐字不变★)★**: 板 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213`

★**必跑命令 (★派活前 main 已实跑命令存在性守卫 rc=0★)★**: ★**① `PREFLIGHT_SANDBOX=<独占路径> python3 HW/check_preflight_regen_idempotent.py` (★对照相★) · ② `python3 HW/check_preflight_regen_idempotent.py` (★现状相★) · ③ `python3 HW/check_gate10_concurrency_safety.py` · ④ `python3 HW/check_gate10_concurrency_safety.py --selftest` · ⑤ `python3 state/merge.py` · ⑥ `python3 state/gate_check.py` · ⑦ `md5sum HW/PCB/demo_mainboard.kicad_pcb` (★必须仍是 611b869e…★)**★