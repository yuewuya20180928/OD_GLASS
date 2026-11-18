# ISS-313 · mech-lead 任务书 —— ★★【MECH 域 needs 184 条四分类处置 ⇒ 把「108 条没人答 + 16 条外部依赖挂着」这两笔老账一次清掉】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-313
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**性质**: ★**内部活 · 需求闭环 / 卫生类** ★
> ★**边界 (硬)**: ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★1 · 病灶 (★main 05:5x 本机实跑, 不抄任何 agent 报告★) ★

### ★1-1 · 机检缺口清单 (★`python3 state/gate_check.py` 实跑★) ★
```
【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 143 条需求确实还没人答 (等另一个总工)
   · sw-lead:  80 条需求确实还没人答 (等另一个总工)
   · mech-lead: 108 条需求确实还没人答 (等另一个总工)
```
★**★口径 (★`state/gate_check.py` 实读★)**: ★**`real_open = needs_total − needs_answered_incoming − needs_closable_unregistered − needs_waiting_external` ⇒ 「等另一个总工」是真·内部未闭合** ★

### ★1-2 · MECH 域自己的账 (★main 05:5x 读 `state/fragments/mech.yaml` 实跑★) ★
```
mech needs_from = 184
   (waiting_on = 空)      113   ★★真·没人认领★★
   (waiting_on = agent)    34   ★★内部·等另一个总工★★
   (waiting_on = boss)     20   ★★等老板拍板★★
   (waiting_on = vendor)   10   ★★外部依赖挂着★★
   (waiting_on = jbd)       6   ★★外部依赖挂着 (JBD 波导厂)★★
```
★**⇒ 本单就是冲这 184 条来的: 逐条归类 + 处置, 让机检那条红 (108 条) 真的降下来** ★

### ★1-3 · ★★外部依赖那 16 条 (★老板 2026-11-12 02:02 政策·本单必须执行★) ★★
★**老板原话**: 「不再发信，全靠自己查资料」⇒ ★**不许把外部依赖挂着当阻塞项** ★
⇒ ★**16 条 (vendor 10 + jbd 6) 一律不许继续等回信 ⇒ 必须【自己网上查】+ 标证据等级 + 查不到就写降级方案** ★

---

## ★2 · 本单要交的四类处置 (★逐条, 不许抽样★) ★

| 类 | 条数 | 处置口径 (★本单给的动作★) |
|---|---|---|
| ★**① waiting_on = agent (34 条)** ★ | 34 | ★**内部活 ⇒ 必须自己推**: 逐条判【我能答吗】⇒ ★**能答的直接写进自己的 `answers` (带 key + 出处 + 证据等级)★★ ⇒ ★**不能答的 ⇒ 写清【该谁答 + 为什么 + 一句话问法 (★给 main 的一行 need, ★不回裸字母★)】** ★ |
| ★**② waiting_on = boss (20 条)** ★ | 20 | ★**不代拍** ⇒ 整理成 ★**need key + 决策码**★ 的一页 (★每个选项 + 代价 + 建议默认值 (★只作参考·不代拍★)+ 不拍的后果★) ★ |
| ★**③ vendor / jbd (16 条)** ★ | 16 | ★**★按老板政策自查 (零外发)★**: ① ★**自己网上查** ★ ② 标证据等级 ★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ★ ③ ★**查不到 ⇒ 写降级方案 (★实测样件 / 选官网参数直接满足的替代型号 / 改设计路径绕开 / 用 [推算] 值并标明推算依据★)★** ⇒ ★**不许再写「等原厂回信」** ★ |
| ★**④ waiting_on = 空 (113 条)** ★ | 113 | 逐条判定三选一: ★**(a) 已作废** (★被哪个 ISS / 哪份文档改写 ⇒ 必须引证★) ★**(b) 已被本单答复覆盖** (⇒ 指到具体 answers key★) ★**(c) 真·待答** (⇒ 给 owner + 处理方式 + 是否与板那一趟相关★) ★ |

★**★对账要求**: ★**交卷页必须给「关 X 条 / 保留 Y 条 / 新答 Z 条」的对账表, 且每条关闭都要有依据行 (★不许批量清空·不许无据关闭★)** ★

★**★与主线的关系 (★写进交卷页§)★**: ★**老板 11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 板只改一次 ⇒ ★**凡与「板框 / 板厚 / 层数 / 镜腿宽度 / 检修口净空 / 重量预算」有关的待答条目, 都要标出来 (★给板那一趟的输入清单★)** ⇒ ★**MECH 域自己的 `MECH/BOARD_FRAME_DECISION_INPUT.md` 已经把框口径摊开了 (ISS-310 交), 本单不要重做那部分, 只做【还没答的条目】** ★

---

## ★3 · 交卷物 (4 件) ★

1. ★**新建 `MECH/MECH_NEEDS_TRIAGE.md`** (★四类逐条表 · 依据行 · 对账 · 「与板那一趟相关的待答输入清单」· 证据分级 §★)
2. ★**新建 `HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md`** (★B1~B6 齐全 · 占位符 0 · 与上面那份同源不重写★)
3. ★**`logs/iss313/`** (★逐条取数命令 + 原始输出 + 改分片前后的 md5★)
4. ★**`state/fragments/mech.yaml`** (★★**必须用 `python3 state/frag_write.py --agent mech-lead` 原子写 (★禁止 open(p,"w")★)★** · ★**新答的进 `answers` · 关闭的 `needs_from` 条目必须带依据★** · ★**只写自己那一份, 不碰 hw.yaml / sw.yaml / pm.yaml★ ★)

---

## ★4 · 硬边界 (★违反即不算交卷★) ★

- ★**零写板**: 板 `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 (`611b869e13518c3c023fb178f91a0075`) + mtime (`2026-11-06 07:07:17`) 交卷前后逐字节相同 ⇒ **交卷页要贴这两个值** ★
- ★**零落表** (★网表 / 脚表 / BOM / 落表台账 一律不动★) ★
- ★**零改闸**: `state/gate_check.py` / `state/merge.py` / `MECH/service_port_check.py` 一个字不许改 ★
- ★**零改既有文档正文**: `MECH/BOARD_FRAME_DECISION_INPUT.md` / `MECH/BOARD_GEOM_30MM.md` / `MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md` 只读不写 ⇒ **本单只交「还没答的条目」, 不重做 ISS-310 已交的对照表** ★
- ★**★零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★)★**: ★**不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询 / 任何对外沟通 ⇒ `state/outbox/` 里的草稿【一律不发】, 只作资料留档 ⇒ 没有「批一句可以发」这个选项** ★ ⇒ **16 条外部依赖必须自查+降级** ★
- ★**不替老板拍板**: 20 条 boss 类一律交 need key + 决策码, ★**不回裸字母** ★
- ★**不自签 issue_log** (★`state/issue_log.yaml` 只由 main 改★) ★
- ★**只写**: `MECH/` 下本单新建文件 · `HANDOFF/` 本单交卷单 · `logs/iss313/` · `state/fragments/mech.yaml` (★经 frag_write.py★) ★

---

## ★5 · 交卷前必跑 (★把输出原样贴进回复★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py    # rc 必须 0 · Q1 必须 18/18 · ★缺口清单里 mech-lead 那条要真的降下来★
md5sum HW/PCB/demo_mainboard.kicad_pcb MECH/service_port_check.py state/fragments/mech.yaml
```

★**★额外纪律 (★与所有派活单同款★)★**: ① ★**写分片必须用 `state/frag_write.py` (禁止 open(p,"w"))** ★ ② ★**只写本任务允许的文件, 不碰别人的** ★ ③ ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★ ④ ★**不许外发任何邮件/询价/问询/采购** ★ ⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
