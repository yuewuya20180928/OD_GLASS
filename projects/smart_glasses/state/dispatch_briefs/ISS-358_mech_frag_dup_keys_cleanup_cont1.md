# ISS-358 · mech-lead · ★★分片重名 key 清理 (cont1 · ★★本稿【订正了原 brief 的一处事实错误】★★)·纯分片·零写板★

★**★你是续做 (cont1): 上一趟 (cont0, 会话 `3cb7cedd-c2af-42ec-adbb-8ece67227c96`) 死于 LLM idle timeout (120s 无响应) ⇒ ★**零交付物** (★交卷页无 · `logs/iss358/` 无 · `state/fragments/mech.yaml` 逐字节未动·md5 仍 `a501815ec90137d849c493c8e749c4b5`★) ⇒ ★**成果零, 从头做, 但【不要重走它走过的弯路】**★**

★**★【铁律 · 本单最重要的一条】★★**: ★**cont0 是在「核实 brief 的前提」上把预算烧光的 ⇒ ★★所以本稿开头【已把前提核实完并订正】, 你【不要重新论证】, 直接照订正后的口径干活★★** ★

---

## ★★① 【订正】原 brief 的机制描述【是错的】★★ — ★★你必须按订正后的口径交付, 不许照抄原措辞★★

★**原 brief 说**: ★**「合并器 `state/merge.py` 对同一个 `_by` 的多条同 key answers 只认第一条 ⇒ 后写的 3~4 条对下游完全不可见」** ★
★**★这条【是错的】★★** — ★**main 2026-11-23 09:5x 本机逐行实读 + 实跑 STATE.yaml 核过 (★不是抄 agent 报告★)**:

| 读数 | 实际值 | 怎么读的 |
|---|---|---|
| ★**`state/merge.py:295`** ★ | ★**`ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]` ⇒ 【收集全部匹配的】, 不是取第一条** ★ | ★**逐行读源码★** |
| ★**`STATE.yaml` 实跑** ★ | ★**`hw-lead` 的 need `pcb_outline_confirm` (to=mech-lead) ⇒ `answers n=5` ⇒ 【5 条全在, 一条没丢】** ★ | ★**实跑合并器 + 读 STATE.yaml★** |
| ★**全仓扫「取第一条」的消费者** ★ | ★**零命中** (★`grep -rnE "answers[^\n]*\[0\]|answers_by_key\[[^]]*\]\[0\]|\.get\(k\)\[0\]|\.get\(key\)\[0\]" state/ HW/ SW/ MECH/` ⇒ 只有一条测试断言 + 一条 main 的历史批注, ★**没有任何生产消费者只认第一条**★★) ★ | ★**全仓 grep★** |

★**★⇒ 所以「后写的对下游完全不可见」这个说法【作废】, 你不许把它写进交卷页★★**

---

## ★★② 【订正】但【危害是真的】, 只是走的是【另一条路】★★

★**危害 = 【一个 key 承载 N 个不同主题】⇒ 两条真实的坏后果★★**

### (2-A) ★★need 的「已答」判定是【只看存在性】的 ⇒ 【答错题也算已答】★★
★**三处平行实现口径一致 (★本机实读★)**:
- ★**`state/gate_check.py:440`**: ★**`return bool(to) and to in (_answers_by_key.get(k) or [])` ★
- ★**`state/stage_gate.py:138`**: ★**`return bool(to) and to in (ans_by_key.get(key) or [])` ★
- ★**`state/decision_truth.py:164`**: ★**`return bool(to) and to in (answers_by_key.get(k) or [])` ★
★**★⇒ 只要【被问的那个 agent】名下存在【任意一条】该 key 的答案, 这条 need 就判「已答」⇒ ★★哪怕那条答案答的是完全另一个问题★★ (★例: `hw.yaml` 的 need `pcb_outline_confirm` (to=mech-lead) 只要 mech-lead 名下【存在任意一条】该 key 的答案就闭合 ⇒ 哪怕那条只答了「摄像头安装」★★) ★**
★**★⇒ 这才是【静默错闭合】的机制★**

### (2-B) ★★同一个 key 下的 5 条讲 5 件不同的事 ⇒ 【下游无法分辨哪条答了哪个问题】★★
★**`pcb_outline_confirm` 的 5 条分别是**: ★**①PCB 50×12mm 厚 0.8/1.0 ②镜脚内腔需求 ③摄像头安装 ④散热接触路径 ⑤M-FIT 结果** ★
★**★⇒ 一个 key 装 5 个主题 ⇒ 任何「按 key 取答案」的读者拿到的都是【一锅粥】⇒ 这就是「板框口径到处飘」的技术根因之一★★**

★**★⇒ 所以本单【仍然该做】, 但【理由要写对】★★**: ★**交卷页 B1/B3 必须写【订正后的机制】(★① 存在性判定导致静默错闭合 + ② 一 key 多主题导致下游无法分辨★), ★**不许写「后写覆盖前写/后写不可见」★★** ★

---

## ★★③ 【安全规则 · 本单最容易踩的坑】★★ —— ★★★拆 key 绝不许把别的分片的 need 打成未答★★★

★**★本机实读: 【谁在问这 4 个 key】★** ★**(★`needs_from` 逐条扫四片★)**

| 被问的 need | 在哪个分片 | to | ★**拆光该 key 的后果** ★ |
|---|---|---|---|
| ★**`pcb_outline_confirm`** ★ | ★**`hw.yaml`** ★ | ★**mech-lead** ★ | ★★**hw.yaml 这条 need 会从「已答」变成「未答」⇒ 台账未闭合数【变多】⇒ 这是回退, 不是收口★★** ★ |
| ★**`ntc_placement`** ★ | ★**`sw.yaml`** ★ | ★**mech-lead** ★ | ★★**同上★** ★ |
| ★**`pcb_outline_confirm`** ★ | ★`mech.yaml` (★自己家的·to=hw-lead★) | hw-lead | ★**不受影响** (★它由 hw.yaml 的答案闭合·★你改 mech.yaml 的 answers 不动它★) ★ |
| ★**`ntc_placement`** ★ | ★`mech.yaml` (★自己家的·to=sw-lead★) | sw-lead | ★**不受影响** ★ |
| ★**`iss219_mech_c7_sink_area_confirm`** ★ | ★`mech.yaml` (★自己家的·to=main★) | main | ★**自家 ⇒ 你可以连 need 的 key 一起改 (★只改 mech.yaml★) ★** |
| ★**`iss251_mech_service_port_pad_y_migrate`** ★ | ★`mech.yaml` (★自己家的·to=main★) | main | ★**自家 ⇒ 同上★** |

★**★★ 硬规则 ★★**:
1. ★**★`pcb_outline_confirm` 与 `ntc_placement` 这两组: 【必须至少保留一条答案留在原 key 上】★★** ⇒ ★**否则 `hw.yaml` / `sw.yaml` 的 need 变未答 ⇒ 台账回退★★**
2. ★**★保留哪一条留原 key? ⇒ 留【hw.yaml / sw.yaml 那条 need 真正问到的那条】★★** ⇒ ★**`hw.yaml` 的 need item = 「PCB 外形 50x12mm 确认 + 器件发热分布 + NTC 位置 (定桥接芯片上主板还是小板 / 散热路径)」⇒ ★★`pcb_outline_confirm` 留【①PCB 50×12mm 厚 0.8/1.0】(★答「PCB 外形」的那条★); `sw.yaml` 的 need `ntc_placement` (★item = TMP117 测点由 SW 定★) ⇒ ★★`ntc_placement` 留【①NTC 贴 SoC 背面散热焊盘边缘…】(★答「贴哪」的那条★)★★**
3. ★**★其余每条各自换成语义独立的 key (★value 一字不改, 只换 key 名★)★★** ⇒ 例: ★`pcb_outline_confirm` → 保留原 key 1 条 + `pcb_outline_confirm_2_cavity` / `_3_camera_mount` / `_4_thermal_path` / `_5_mfit_result`★★; ★`ntc_placement` → 保留原 key 1 条 + `ntc_placement_2_power_budget` / `_3_struct_constraint`★★
4. ★**★若某条答案【拆分后会让别家的 need 看不到它原本能看到的内容】(★例: ④散热接触路径 也是 `hw.yaml` 那条 need item 里要的「散热路径」★) ⇒ ★★不许静默让它消失: 要么【保留它在原 key 上】(★即原 key 留 2 条★), 要么【在交卷页 B5 写成一条【跨分片待办】交给 main 去改 `hw.yaml` 的 need★】⇒ ★★二选一, 在 B5 写清你选了哪个 + 为什么★★** ★
5. ★**★自家那两组 (`iss219_mech_c7_sink_area_confirm` / `iss251_mech_service_port_pad_y_migrate`): 答案换 key 的同时, ★★`mech.yaml` 里对应的 need (to=main) 也一起换成同一个新 key★★ (★只改 mech.yaml, 不许碰别人分片★) ⇒ ★★否则那条 need 会变未答★★**

★**★自证 (★交卷页必须贴★)★**: ★**改完之后, ★★把「四片里所有 `needs_from` 的 key」与「四片里所有 `answers` 的 key」重新对一遍, 证明: 每条 need (含 to=hw-lead / to=sw-lead / to=main / to=mech-lead) 仍然【有】对应 agent 名下的同 key 答案 ⇒ 未闭合需求数【不得比改前多】★★** ★

---

## ★★④ 本单只做 3 件 (★不许扩项·零写板·零落表·零外发★)★★

### (4-1) ★**4 组高危 answers 拆成语义独立的 key (★一条内容都不许删·value 逐字照抄★)★★**
- ★**做法**: ★**每条保留原 value 全文, 只换 key 名** ⇒ key 名要能自解释 (★上表已给出建议命名★) ★
- ★**★必须遵守 §③ 的安全规则 (★尤其第 1/2/5 条★)** ★
- ★**★`pcb_outline_confirm` 特别提醒**: ★**这 5 条里没有一条是「板框 U-1 的答案」** ⇒ ★**不许把它当板框答案用** (★板框 U-1 的真答案在 `DECISION_ONE_PAGER_2026-11-22.md` §⑥/§⑦ + `DECISION_INDEX_2026-11-18.md` §R·★与本单无关★) ★

### (4-2) ★**低危 artifacts 重名去重 (★只保留信息最全的一条·★其余写进交卷页的「已删重复登记」清单★)★★**
- ★**★本机实读 (★09:5x·★以体检器输出为准★)★**: ★**`check_frag_dup_keys.py --agent mech-lead` ⇒ 低危 32 组 (★体检器统计 `artifacts` + `interface_claims` + `risks` + `blockers` 四个低危段★); ★★其中 `mech.yaml` 的 `artifacts` 段【同 `path` 重复】= ★★31 组★★ (★artifacts 共 230 条 · ★逐条核对: 这 31 组的 `key` 也全相同 ⇒ 是同一条登记了两次, 不是两条不同登记撞一个 path★) ★**
- ★**做法**: ★**同一 `path` 多条 ⇒ 留 value/summary 最全的那条, 其余登记到交卷页 (★不许静默丢·★要能追回★)** ★

### (4-3) ★**自证 + 交卷 (★零写板★)★★**
- ★**自检命令 (★交卷前跑, 原样输出贴进交卷页★)**: ★`python3 state/check_frag_dup_keys.py --agent mech-lead` ⇒ ★**rc=0 (高危 0 组)**, ★`python3 state/check_frag_dup_keys.py` ⇒ ★**全仓高危总数 = hw-lead 那几组 (★不在你地界·不许越界改★)** ★
- ★**必跑**: ★`python3 state/merge.py` (rc=0) · `python3 state/gate_check.py` (rc=0 · Q1 18/18) · `python3 state/frag_write.py --agent mech-lead --show` · `md5sum HW/PCB/demo_mainboard.kicad_pcb` (必须 `611b869e13518c3c023fb178f91a0075`) ★
- ★**★另外必跑 (★本单特有的回退闸★)★**: ★**合并后逐条核对「四片所有 need 都仍有对应 agent 的同 key 答案」⇒ 【未闭合需求数不得比改前多】★** ⇒ ★**把改前/改后两个数都贴进交卷页 B2★** ★
- ★**交卷页**: `HANDOFF/2026-11-23_mech-lead_ISS358_分片重名key清理.md` (★B1~B6 六个 `##` 标题里必须分别出现: B1 `结论` · B2 `验收标准自评` · B3 `证据分级` · B4 `接口取值声明` · B5 `未决项与卡点` · B6 `自证复现命令`) + `state/fragments/mech.yaml` 分片 (★只走 `state/frag_write.py`★) + `logs/iss358/`

---

## ★★⑤ ★★执行纪律 (★cont0 死于超时 ⇒ 本单必须【先落盘】★★)★★

1. ★**★★第 0 步: 先把交卷页骨架 + `logs/iss358/` 建起来 (★哪怕每份只写 3 行标题 + 交付物清单★) ⇒ ★★再死一次至少留得下骨架★★** ★
2. ★**★不许 `yaml.safe_load` 3 MB 的 `STATE.yaml` (★★cont0 就是在这里耗掉的预算·★`STATE.yaml` = 3,017,411 B·★`yaml.safe_load` 一次要几十秒⇒ 极易撞上 120s idle timeout★) ⇒ ★★只读 `state/fragments/*.yaml` (★82 条 answers / 139 条 needs·秒级★) + 要看板面就 `grep`★** ★
3. ★**★单条 `exec` ≤ ~120 秒·★不要一条命令里塞 3 MB 的解析★** ★
4. ★**★每落一件交付物就把 rc 追加进交卷页 (★别攒到最后一起写★)★** ★
5. ★**★写分片只用 `state/frag_write.py` (★`--set` 是【整段替换】★ ⇒ ★改 answers 必须【整段导出→改 key→整段写回】, 不许用 `--add-answer` 追加★)** ★

---

## ★★⑥ 边界 (★一条不许越★)★★

★**零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413`) · ★**零落表** (不改网表/脚表/BOM/原理图/任何闸) · ★**只写 `state/fragments/mech.yaml`** (★只走 `state/frag_write.py`·★**不许写 pm.yaml / hw.yaml / sw.yaml — 那是别人的地界★**) · ★**零外发/零采购** · ★**不替老板拍板 · 不新增拍板项** (★`pcb_outline_confirm` 那 5 条不是板框答案★) · ★**证据分级必标** · ★**不许改 `state/merge.py` / `state/gate_check.py` / `state/frag_write.py`** (★★**并发写的根治是「给 frag_write.py 加乐观并发断言」, 但那是 main 的地界·本单只清已攒下的重名, 不许自己改工具★**) · ★**不许改 `state/check_frag_dup_keys.py`** (★main 的工具·只读用★) ★
★**做不完不许假装做完**: 交卷页写清「已做 / 未做」分界 (逐组名单) ★

★额外纪律: ① 写分片必须用 state/frag_write.py (禁止 open(p,"w")) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ⑤ 交卷前跑 python3 state/merge.py (rc 必须 0) && python3 state/gate_check.py (Q1 必须 18/18) 并把输出贴进回复

★**并发哨兵 (★main 09:3x 实读★)**: ★**你本工位上可能还有一条同 agent 的老会话残留在飞 (★它卡在一次模型调用上 40+ 分钟没动·★它的 issue ISS-333 已由兄弟会话交付并被 main 签 verified ⇒ 它对本单是干扰不是依赖★) ⇒ ★**你写 `state/fragments/mech.yaml` 前后各跑一次 `md5sum state/fragments/mech.yaml` (★写前基线 = `a501815ec90137d849c493c8e749c4b5`★) ⇒ ★**若你写之前基线已经变了 ⇒ 说明有人并发写了 ⇒ 停下, 在交卷页 B5 写清「分片被并发改动, 已停止」, 不许静默覆盖** ★**★这就是本单要治的病本身·不许自己再犯一遍★** ★
