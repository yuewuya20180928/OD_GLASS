# ISS-357 · sw-lead 任务书 —— ★★【SW 域 needs 144 条四分类处置 ⇒ 把「98 条没人答 + 8 条外发依赖挂着」这两笔老账一次清掉】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-357
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**性质**: ★**内部活 · 需求闭环 / 卫生类** ★
> ★**边界 (硬)**: ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★
> ★**同型先例 (★已验证可抄★)**: ★**ISS-313 (mech-lead · MECH 域 needs 184 条四分类处置) = verified** ⇒ ★**MECH 分片从 184 条降到 139 条, `waiting_on=空` 113→100, `waiting_on=vendor` 10→0, `waiting_on=jbd` 6→0** ⇒ ★**本单照抄它的口径 / 交卷物结构 / 对账要求** ★

---

## ★1 · 病灶 (★main 2026-11-23 08:1x~08:2x 本机实跑, 不抄任何 agent 报告★) ★

### ★1-1 · 机检缺口清单 (★`python3 state/gate_check.py` 实跑 · rc=0★)
```
【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 179 条需求确实还没人答 (等另一个总工)
   · sw-lead:  98 条需求确实还没人答 (等另一个总工)      ★★本单要对准的数★★
   · mech-lead: 76 条需求确实还没人答 (等另一个总工)
```
★**★口径 (★`state/gate_check.py` 实读★)**: ★**`real_open = needs_total − needs_answered_incoming − needs_closable_unregistered − needs_waiting_external` ⇒ 「等另一个总工」是真·内部未闭合** ★
⇒ ★**本单的验收判据之一 = 这条 98 必须真的降下来 (不是把 needs 删空, 是把每一条落到「已答 / 已作废 / 别人在等」的确定状态)** ★

### ★1-2 · SW 域自己的账 (★main 08:2x 读 `state/fragments/sw.yaml` 实跑★)
```
sw needs_from = 144
   to=main       waiting_on=空        99
   to=hw-lead    waiting_on=空        17   ★★内部·等另一个总工★★
   to=main       waiting_on=boss       12   ★★等老板拍板★★
   to=vendor     waiting_on=vendor      8   ★★外部依赖挂着 (★外发口径违规★★)
   to=main       waiting_on=agent       4   ★★内部·等另一个总工★★
   to=mech-lead  waiting_on=空          2   ★★内部·等另一个总工★★
   to=main       waiting_on=sw-lead     2
```
★**⇒ 本单就是冲这 144 条来的: 逐条归类 + 处置, 让机检那条红 (98 条) 真的降下来** ★

### ★1-3 · ★★外部依赖那 8 条 (★老板 2026-11-12 02:02 政策 · 本单必须执行★) ★★
★**老板原话**: 「不再发信，全靠自己查资料」⇒ ★**不许把外部依赖挂着当阻塞项** ★
⇒ ★**8 条 (waiting_on=vendor) 一律不许继续等回信 ⇒ 必须【自己网上查】+ 标证据等级 + 查不到就写降级方案** ★

★**★而且这 8 条的原文本身就在喊「外发」★** (★main 08:2x 逐条实读·只摘原句关键部分★):
- `vendor_q8_q9_scope` = 「…**走 main 发第二轮邮件**, 我不单独对外」
- `fw_vendor_toolchain` = 「原厂烧录工具链 (**经 main 转达**, 我不单独对外)」
- `fw_usb_boot_phy` = 「USB 下载能力 (**经 main 转达**…)」
- `fw_boot_entry_cond` = 「BOOT 模式与校验机制 (**经 main 转达**…)」
- `sw_reset_timing_spec` = 「TBD-12 追加问 (**请项目总工并进第二轮邮件**, 我不外发)」
- `sw_usb_phy_spec` = 「USB 设备控制器是 FS 还是 HS (**请项目总工并进第二轮邮件**)」
- `sw_aon_deepsleep_spec` = 「原厂追加问 (**经项目总工并进第二轮邮件**…)」
- `model_license_yolov5sim` = 「★ISS-087 本地已判定: yolov5s-sim 系 = ultralytics/yolov5 v6.0 release 导出物 → 许可 = AGPL-3.0 (证据链 7 环, 见 SW/MODEL_LICENSE.md §1.2…)」★**★这一条本地已经查完了 ⇒ 它根本不该还挂在 vendor 上 ⇒ 本单必须把它落到确定状态★★**

★⇒ ★**这 8 条既有「挂外部依赖」的病, 又有「措辞里留外发口」的病 ⇒ 本单一并清** ★

### ★1-4 · 陈旧条目的证据 (★说明「逐条判」不是形式主义★)
★**12 条 boss 类里已经有一条自己标了「已结 (ISS-212, 2026-11-15 sw-lead)」** (key = `demo_od_p0_4_panel_init_code`) ⇒ ★**SW 域确实存在「条目本身已结、但 need 还挂着」的漂移 ⇒ 逐条判是必要的** ★

---

## ★2 · 本单要交的四类处置 (★逐条, 不许抽样★) ★

| 类 | 条数 | 处置口径 (★本单给的动作★) |
|---|---|---|
| ★**① 内部等另一个总工 (17 + 2 + 4 = 23 条)** ★ | 23 | ★**内部活 ⇒ 必须自己推**: 逐条判【我能答吗】⇒ ★**能答的直接写进自己的 `answers` (带 key + 出处 + 证据等级)★★ ⇒ ★**不能答的 ⇒ 写清【该谁答 + 为什么 + 一句话问法 (★给 main 的一行 need, ★不回裸字母★)】** ★ ⇒ ★**跨域对答时, 同 key 的答案必须写回【自己那一份分片】, 答案里带对方分片的出处 key (★项目铁律: 同 key 的决策是全局事实, 条目住在谁的片段里不该成为退休不掉的理由★)** ★ |
| ★**② waiting_on = boss (12 条)** ★ | 12 | ★**不代拍** ⇒ 整理成 ★**need key + 决策码**★ 的一页 (★每个选项 + 代价 + 建议默认值 (★只作参考·不代拍★)+ 不拍的后果★) ⇒ ★**不回裸字母** ★ ⇒ ★**已经自己判完的 (如 `demo_od_p0_4_panel_init_code` 已标已结) ⇒ 直接落到确定状态, 不要重复上报老板★** ★ |
| ★**③ vendor (8 条)** ★ | 8 | ★**★按老板政策自查 (零外发)★**: ① ★**自己网上查** ★ ② 标证据等级 ★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ★ ③ ★**查不到 ⇒ 写降级方案 (★实测样件 / 选官网参数直接满足的替代型号 / 改设计路径绕开 / 用 [推算] 值并标明推算依据★)★** ⇒ ★**不许再写「等原厂回信」** ⇒ ★**不许再留「走 main 发第二轮邮件 / 经 main 转达 / 请并进邮件」这类外发字样 (★措辞一并改掉★)** ⇒ ★**查不到也必须交 (降级方案是必须项, 不是可选项)** ★ |
| ★**④ waiting_on = 空 (99 + 17 + 2 = 118 条)** ★ | 118 | 逐条判定三选一: ★**(a) 已作废** (★被哪个 ISS / 哪份文档改写 ⇒ 必须引证★) ★**(b) 已被本单答复覆盖** (⇒ 指到具体 answers key★) ★**(c) 真·待答** (⇒ 给 owner + 处理方式 + 是否与板那一趟相关★) ★ |

★**★对账要求**: ★**交卷页必须给「关 X 条 / 保留 Y 条 / 新答 Z 条」的对账表, 且每条关闭都要有依据行 (★不许批量清空·不许无据关闭·不许把 118 条批量标同一个结论★)** ★

★**★与主线的关系 (★写进交卷页§★)★**: ★**老板 11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 板只改一次 ⇒ ★**凡与「板框 / 板厚 / 层数 / 镜腿宽度 / 检修口净空 / 重量预算 / 位号改名 / 布线 45→0 / Gerber 投产包重出 / Q3 存储分档」有关的待答条目, 都要标出来 (★给板那一趟的【SW 侧输入清单】★)** ⇒ ★**SW 域已交的现成件不要重做**: `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (7 件同批清单) · `SW/ONETRIP_SW_RENAME_SAFETY.md` (闸脚本安全性) · `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (改名后闸链复活 SOP) · `SW/MODEL_LICENSE.md` (许可证据链) ⇒ ★**本单只做【还没答的条目】** ★

---

## ★3 · 交卷物 (4 件) ★

1. ★**新建 `SW/SW_NEEDS_TRIAGE.md`** (★四类逐条表 · 依据行 · 对账 · 「与板那一趟相关的 SW 侧待答输入清单」· 证据分级 §★)
2. ★**新建 `HANDOFF/2026-11-23_sw-lead_ISS357_SW未答需求分类.md`** (★B1~B6 齐全 · 占位符 0 · 与上面那份同源不重写★)
3. ★**新建 `logs/iss357/`** (★逐条取数命令 + 原始输出 + 改分片前后的 md5★)
4. ★**`state/fragments/sw.yaml`** (★★**必须用 `python3 state/frag_write.py --agent sw-lead` 原子写 (★禁止 open(p,"w")★)★** · ★**新答的进 `answers` · 关闭/改判的 `needs_from` 条目必须带依据 (★`resolved_by` / `closed_ref` / `resolved_note` 这类字段照 ISS-313 的写法填★)· ★**只写自己那一份, 不碰 hw.yaml / mech.yaml / pm.yaml★ ★**

---

## ★4 · 硬边界 (★违反即不算交卷★) ★

- ★**零写板**: 板 `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 (`611b869e13518c3c023fb178f91a0075`) + mtime (`2026-11-06 07:07:17.362193413`) 交卷前后逐字节相同 ⇒ **交卷页要贴这两个值** ★
- ★**零落表** (★网表 / 脚表 / BOM / 落表台账 一律不动★) ★
- ★**零改闸**: `state/gate_check.py` / `state/merge.py` / `SW/tools/` 下任何脚本 一个字不许改 ★
- ★**零改既有文档正文**: `SW/MODEL_LICENSE.md` / `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` / `SW/ONETRIP_SW_RENAME_SAFETY.md` / `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` 只读不写 ⇒ **本单只交「还没答的条目」, 不重做上面那四份已交的件** ★
- ★**★零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★)★**: ★**不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询 / 任何对外沟通 ⇒ `state/outbox/` 里的草稿【一律不发】, 只作资料留档 ⇒ 没有「批一句可以发」这个选项** ★ ⇒ **8 条外部依赖必须自查 + 降级** ★
- ★**不替老板拍板**: 12 条 boss 类一律交 need key + 决策码, ★**不回裸字母** ★
- ★**不自签 issue_log** (★`state/issue_log.yaml` 只由 main 改★) ★
- ★**只写**: `SW/` 下本单新建文件 · `HANDOFF/` 本单交卷单 · `logs/iss357/` · `state/fragments/sw.yaml` (★经 frag_write.py★) ★

---

## ★5 · 交卷前必跑 (★把输出原样贴进回复★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py    # rc 必须 0 · Q1 必须 18/18 · ★缺口清单里 sw-lead 那条 (98) 必须真的降下来★
md5sum HW/PCB/demo_mainboard.kicad_pcb SW/MODEL_LICENSE.md state/fragments/sw.yaml
```

★**★额外纪律 (★与所有派活单同款★)★**: ① ★**写分片必须用 `state/frag_write.py` (禁止 open(p,"w"))** ★ ② ★**只写本任务允许的文件, 不碰别人的** ★ ③ ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★ ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ ⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
