#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""append 2026-11-24 10:33 播报记录到 memory/2026-11-05.md (append-only)"""
import io, os

WS = "/home/yuewuya/.openclaw/workspace"
MEM = os.path.join(WS, "memory", "2026-11-05.md")
FACTS = os.path.join(WS, "projects/smart_glasses/state/.verify/_bcast_facts_20260724_1033.txt")

facts = open(FACTS, encoding="utf-8").read().rstrip("\n")

card = """进展 2026-11-24 10:33 | 走线 18092 段 | 过孔 433 | unconnected 45 | DRC 0 (板 md5 611b869e… 自 11-06 07:07 逐字节未动 · facts 内「已放行」0 处 ⇒ 无放行章 ⇒ G1 仍开, 不许投板)
当前在做: 主线 = PCB 图「板只改一次」那一趟; 板面仍零变化 (18 天逐字节未动), 变化全在交卷/签收侧 —— 10:14 ISS-379 cont1 交卷 (闸侧根因 = pad 角度被取整到 6 位 ⇒ K2 修绿, selftest 19/19); 10:26~10:28 ISS-381 cont1 交卷 (新闸 check_sw_false_connectivity_gate K0~K6 / selftest 17/17 · 真结论: unc 45→0 是计数判据, 证不出「是哪 23 条必需网接上了」); 10:27 ISS-384 cont1 交卷页 (34 处充电电流活值订正追平已落表真值 680Ω); 10:10/10:11 ISS-387(hw)/ISS-389(mech) 会话已结束, 内容页在盘但交卷页+分片未落 ⇒ 卡在「内容已出、交付未闭」; ISS-388(sw) 仍在跑 (最后活动 10:13); 10:29 日巡检: G1 · 齐备率 18/18 · 问题单 384 (逾期 19 · 违规 19) · 内部未闭合需求 350
待办 ①: ISS-379/381/384 三条 cont1 已交卷 ⇒ 等 main 独立验收签字 (闸 rc=0 + selftest 末行 ALL TESTS PASS + 板三项指纹未动); ISS-384 交卷页 10:27:54 被重写 (25,055 B / 213 行 / 只剩 B1~B6), cont1 声称的 B7/B7-8 追加段当前不在盘 ⇒ 要核一次; ISS-384 内容 = 34 处充电电流活值订正追平 680Ω 真值 (ICHG 0.697A / 单 pin 0.349A), 新发现网表/脚表 3 处 390Ω 残留未标作废 (已登记 needs_from); ISS-387/389 要么派 cont1 补齐交卷页+分片、要么 main 直接签收补写
待办 ②: 板那一趟仍是 G1 唯一缺口 —— 布线 unc 45→0 + 布局修正 + 位号改名 + 板侧同步 B-1~B-8 + Gerber/投产包重出 同一趟做完; 巡检两条老账 check_pcb_nets rc=1 (网表 480 / 板上 482 · 多余 2 · 同号异网 3) 与 chain_gate rc=1 都是这一趟本体, 板重出时一起清; G1a 还差 G1a-4 (翻面口径) + G1a-8 (关机语义 SD-1 + 负载开关 TPS22991RAA 追认 LS-1) —— 两条在老板域, 已按自己查到的资料给出建议默认值与证据等级, 未代拍
待办 ③: 板框第一问 (甲 demo 台架板 / 乙 F30A 产品板) 仍待定 —— 结构件出件窗口挂它; 自己查的实跑数据 (main 36 档 = 3 框 × 板厚 4 × 层数 3): B160×100 36 档全红 (V 链 −68.00 / L 链 −85.50 · 板重 47.36 g = 整机质量预算 65~97%) · F30A 板厚 0.80/1.00 两档全绿 (内腔 4.90/4.70) · P60×15 整档作废 (套 A 四孔在 15 mm 板上不成立) ⇒ 权威口径 = 一页 §⑥/§§⑦/§⑬-3 + 索引 §E-1(已就地标注)/§R/§T, 未代拍; 同批还有电芯型号 D-2-9 (ICP422339PR 4.6 mm vs ICP582035PR-01 6.4 mm): 按现型号到货厚 6.40 mm 装不进 7.30 mm 镜脚 ⇒ 电芯段 H 链最坏 −1.10 mm; 结构侧新结论 (自己查 · ISS-386 新闸 201 条判据 / selftest 18/18): J_DEBUG 结构件那一趟无论如何都要动, 要过罩住判据清空区 X ≥ 6.6100 / 开口 Y ≥ 5.6000, ISS-377 的 DP-1 3.4700 缺 0.6000
下一步: main 独立验收 ISS-379/381/384 三条 cont1 + 闭掉 ISS-387/389 的交卷页与分片 + 核 ISS-384 交卷页重写 ⇒ 三条腿结论并进「板只改一次」同一趟一次做完 ⇒ 过 G1; 本 job 只落本地快照, 零外发, 不推 GitHub"""

head = """
### 本轮播报 (2026-11-24 10:33 · cron 5bd48f25 · 脚本输出全文 + 卡片正文)

★板面判据 ([板]+[布线]) 与上一条 (09:46 · facts 取自 09:46:xx) 逐字相同 ⇒ 板面无变化; ★但交卷/签收侧 09:46~10:33 有实质变化 ⇒ 本轮播报 ★
★① **ISS-379 cont1 交卷 (10:14)** —— `HANDOFF/2026-11-24_hw-lead_ISS379_JUART排针换land落位可行性.md` 43,177 B @10:14 · 真相页 `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` 51,433 B (追加 §10) · ★**根因 = 闸自己把 pad 角度取整到 6 位** (`ang=round(math.radians(...),6)` ⇒ 90° 变 1.570796 rad ⇒ 余量 3.1266499666→3.1266500913 ⇒ round4 翻格) ⇒ 修在产生点 (闸侧第 308 行) · selftest 19/19 ALL TESTS PASS · 零写板 (板三项指纹逐字相同)
★② **ISS-381 cont1 交卷 (10:26~10:28)** —— 真相页 `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` 28,761 B @10:26 · 闸 `SW/tools/check_sw_false_connectivity_gate.py` 54,358 B (K0~K6 · selftest 17/17) · 交卷页 24,640 B @10:28 · sw.yaml 分片登记 8 条 `iss381_cont1_*` @10:26 ⇒ ★**真结论: `unc 45→0` 是计数判据, 证不出「是哪 23 条必需网接上了」** (沙盒实测: 24 条网全标 NC、一条铜不加 ⇒ unc 计数 45→20) ⇒ 删焊盘 / 标 NC / 改名 三种刷法都能把 45 刷到 0 而一条铜都不加
★③ **ISS-384 cont1 交卷页 10:27:54 被重写** —— 现盘 25,055 B / 213 行 / 只剩 B1~B6; cont1 会话曾报 44,710 B / 426 行 且含 B7+B7-8 ⇒ ★**追加段当前不在盘上 ⇒ 要 main 核一次 (可能仍在写)** · 内容要点: 三份 HW 活文档 34 处活值订正追平已落表真值 680Ω (ICHG 0.697A / 单 pin 0.349A / 余量 1.43× · 系数 1.216@3.70V / 1.071@4.20V) + 新闸 `HW/check_charge_current_live_value.py` selftest 14/14 + 新发现: 既有闸 `check_netlist_selfconsistency.py` 的 R10 只扫一个文件 ⇒ 判定面有洞 + 网表/脚表 3 处 390Ω 残留未标作废 (已登记 `iss384_netlist_note_390ohm_residual` to=main)
★④ **ISS-387 / ISS-389 卡在「内容已出、交付未闭」** —— 10:10 / 10:11 会话已结束 (`status=done`): ISS-387 真相页 `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` 44,122 B @10:10 · ISS-389 要求单 `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` 65,851 B + 闸 `MECH/check_debug_seat_rework_spec.py` 47,102 B @10:08 ⇒ ★**两单交卷页 + 分片都没落盘 (HANDOFF/ 里 grep ISS-387/388/389 = 空 · hw.yaml/mech.yaml 里 grep = 空)** ⇒ ★**内容页在盘 ≠ 交付完** ⇒ 下一趟要么派 cont1 补齐, 要么 main 直接签收补写
★⑤ **ISS-388 (sw-lead) 仍在跑** —— session `d67efde7` 最后活动 02:13:47Z (10:13:47) · 台账 status=fixing · owner=sw-lead
★⑥ **10:29 日巡检 (`state/daily_check.py` → `state/STATUS_DIGEST.md`)**: 阶段门 **G1** (已过 G0) · 齐备率 18/18 · 问题单 384 (逾期 19 | 违规 19) · 内部未闭合需求 350 · 接口声明 1198 条 · 实测 0/4 · 三条异常全是老账 (问题闭环门 19 条 / `check_pcb_nets` rc=1 / `chain_gate`) ⇒ **G1 仍开, 不许投板**
★⑦ **板面零变化 (双证)**: 板 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 逐字节未动 (18 天) · 走线 18092 段 / 过孔 433 / unconnected 45 / DRC 违规 0 ⇒ facts 内 grep「已放行」= **0 处** ⇒ 无放行章 ⇒ **G1 仍开, 不许投板**
★已落盘: `state/.verify/_bcast_facts_20260724_1033.txt` · MEMORY.md 实时块 (update_progress_block.py --facts ⇒ 旧块 7273 B → 新块 7273 B, rc=0) · `PROGRESS_SNAPSHOT.md` (gen_progress_snapshot.py rc=0 · 3,073 B @10:37) · 本条 (append) · 零外发 (微信通道已删 ⇒ 零外部投递) · 零写板 · 不推 GitHub (归 5 小时同步 job)
★纪律自检: 本轮只做 4 步 (取事实 → 判变化 → 落盘三处 → 发主会话) · 未派活 · 未改任何项目真文件 (只写了 state/.verify/ 下的事实副本与本条 append 脚本) · 未调 message 工具 · 卡片已落进主会话 (sessions_send → agent:main:main)

```
%s
```

### 本轮卡片正文 (2026-11-24 10:33 · 落进主会话 sessions_send → agent:main:main)
```
%s
```
""" % (facts, card)

with io.open(MEM, "a", encoding="utf-8") as f:
    f.write(head)

print("appended bytes:", len(head.encode("utf-8")))
print("memory file size:", os.path.getsize(MEM))
