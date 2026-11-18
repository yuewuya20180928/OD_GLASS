
---

## ★★2026-11-17 22:2x · job fb67af40「ARS45 队列自动派活」· 本轮处置 ★★
★**派活 2 条 (★都是【僵尸 fixing 重派 = cont1 续做】· 不是新开单★)**:
- ★**ISS-299 → hw-lead** (session `agent:hw-lead:subagent:018e190a` · taskName `queue_iss299_cont1` · runTimeout 5400s)
- ★**ISS-300 → mech-lead** (session `agent:mech-lead:subagent:9fc3d633` · taskName `queue_iss300_cont1` · runTimeout 5400s)
★**根因 = 【父死子死】型连带**: 两个上一趟子会话 `endedAt` 相差 **81 毫秒** (hw-lead `5b01e341` 21:59:41 / mech-lead `1765a992` 21:59:40)
⇒ 父 run `aea23265` 整个被掐 ⇒ 两个子被连带杀掉 ⇒ **status 卡在 fixing 变僵尸** ⇒ advance.py 的 in_flight 规则又把两条全挡住 ⇒ `internal: []` (★盘面 ≠ 名单·第 8 次了★)
★**处置**: fixing → open → fixing ★**同一个锁内原子完成** (`state/_apply_20261117_2225_cronfb67_zombie_299_300_cont1.py`) ⇒ ★**中间不留 open 窗口 ⇒ 兄弟 job 775d9893 不会撞车** ★
★**★本轮实测确认: 两条的主体其实【都做完了】, 只是 paperwork 没填完 ★**:
- ISS-299: 闸已重锚 (`--expect-known` rc=0 · `--selftest` rc=0 (13+10) · 默认 rc=1 恰好 15 条缺陷=既有基线) · 交卷单 20,689 B · B0~B6 齐全 · ⑰-1/⑰-3/⑰-4/⑰-5 已填 ⇒ ★**只差 §⑰-2 一行占位符** ★
- ISS-300: 新闸 21,227 B (主跑 rc=0 绿6/红0 · `--selftest` rc=0 反向用例⑥真沙盒真篡改⇒红1道并点名 · `--json` ok=True) · 交卷单仍 1,828 B 骨架 10 处 `🔄 待填` ⇒ ★**只差 B0~B6 paperwork** ★
★**★★一条本轮实测出来的判据坑 (★已写进两条续做任务书★)★★**:
★**`state/check_report_placeholders.py` 对 ISS-300 那份交卷单的 10 处 `🔄 待填` 判【无占位符】** ⇒
★**因为它只抓 `%(name)s` / `PLACEHOLDER` / 裸 `TODO`·抓不到 `🔄 待填` 与 `★(…填入…)★` 这两种形态** ⇒
★**⇒ 真判据必须是 `grep -cE "🔄|待填"` = 0 ⇒ ★别拿 check_report_placeholders 当「已填」的证据★ ★
★**板面零变化**: 板 `611b869e…` (mtime 仍 2026-11-06 07:07:17.362193413) · `.kicad_pro` `3e504d2b…` · 网表 `37f62ac3…` · 脚表 `a4270120…` · BOM `5d02bece…` · 落表台账 `1ae6242a…` ⇒ 六件逐字节不变
★**核验**: merge rc=0 · gate_check rc=0 (Q1 18/18) · issue_check rc=0 · 两份 cont brief 过命令存在性闸 rc=0 · `subagents list` 实测 2 条 running (每 agent 各 1 条·无重复)
