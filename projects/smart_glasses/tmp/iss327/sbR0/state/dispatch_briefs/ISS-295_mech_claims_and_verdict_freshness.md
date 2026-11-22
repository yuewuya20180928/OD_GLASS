# ISS-295 · mech-lead · 【板只改一次 · 结构侧输入一次性收口 + 过期结论防漂闸】· 内部活

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 17:5x** ★ · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-295 · ★**零外发** ★
> ★**本单性质**: ★★**内部活 · 纯文档 + 机器闸类** ★★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM · 不替老板拍板** ★
> ★**符合老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律** ★ (★本单只动 MECH 侧两份页 + 新建一份认领句页 + 新建一道闸★)

---

## ★⓪ 本单为什么现在派 (★main 17:4x 本机实查盘面, 不抄任何 agent 报告★)

★**ISS-294 (mech-lead · 17:3x 交卷) 已由 main 17:4x 独立复验落 verified ⇒ mech-lead 名额空出来** ★
⇒ ★**而「板只改一次」那一趟的结构侧输入还散着** ⇒ ★**main 复验时又挖出一条新的口径病 (★SW 侧 ISS-293 刚治完同一种病★) ★**

---

## ★① 病灶 (★main 17:4x 本机实读盘面, 逐条带行号★)

### ★①-1 · MECH 两页对同一件事【两种说法】★

★`MECH/BOARD_ONEPASS_MECH_SYNC.md` (★72192 B★) L550 的 `J_USB_C` 行 verdict 已经改成:
> ★**「可装 / ★边开口规格已补 (X 132.995..147.005 @ 板边 Y=0 · h 三档 · 固定孔清空区 X 133.895..146.105)」** ★

★而 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` (★91535 B·ISS-290 交卷物★) 里仍是老结论 (★main 17:4x 实测命中 **5 处**★):

| 行 | 过期文字 (逐字) |
|---|---|
| ★L68 ★ | ★「★**现有 MECH 规格里【没有】这一条 ⇒ 本单登记为缺口 (见 §5 清单 E-6)**★」★ |
| ★L175 ★ | ★「★**结构件必须有边开口 (现有 MECH 规格里【没有】这一条)**★ · 开孔 = ★**缺口, 待登记**★」· verdict「★**可装 (三方一致) / ★结构侧缺一条边开口规格 (缺口)**★」★ |
| ★L188 ★ | ★「1 个: `J_USB_C` (16p @0.50 + 2×Ø0.65 对上, ★**但结构侧缺一条边开口规格**★)」★ |
| ★L1816 ★ | ★机器块 JSON 的 `"verdict": "可装 (三方一致) / 结构侧缺一条边开口规格"` ★ |

★★**注 (★别误读★)**: main 17:4x 已在该页**末尾追加**一节 `§E-6-订正` (★L2162 起★) 声明那几句是过期文字、★**老字一字未删 (留痕)**★ ⇒ ★**所以现状 = 【老行还在 + 末尾有订正节】⇒ 读页的人若只 grep 老行, 拿到的还是错结论** ★★

### ★①-2 · 机器闸只挡了一半 ⇒ 叙事文字漂移 = 绿灯 ★

★`MECH/check_onepass_struct_crosscheck.py` 的 **N3b** (★L630~L641★) 比的是★**两页机器块里 `openings[]` 的矩形**★ (★ISS-294 加的「两页逐字一致」★) ⇒ ★**老行里那句过期结论, 机器一个字都不查** ★
★⇒ ★**SW 侧刚栽过同一个坑**: `SW/SW_TIMING_REVIEW.md` 停在旧口径 ⇒ 照它判「ADC 链不合格 ⇒ 改板」⇒ ★**板白改第二遍** ⇒ ★**ISS-293 给 SW 侧建了 `SW/tools/check_timing_review_adc_sync.py` ⇒ MECH 侧还没有对应的那道闸** ★★

### ★①-3 · 结构侧输入还散着 ⇒ 「板只改一次」那一趟的结构件会缺料 ★

★`state/fragments/mech.yaml` 的 `needs_from` 里 ★**9 条 pending 且 to=main**★ (★main 17:4x 实读★), 其中至少 4 条是★**「板那一趟」的结构侧输入认领**★:

| need key | 内容要点 |
|---|---|
| ★`iss271_mech_s6_port_opening_claim` ★ | ★**检修口 / 调试口开口认领句** ⇒ 请挂进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S6 ★ |
| ★`iss278_mech_to_hw_board_inputs` ★ | ★**MECH→HW 输入清单** (★§3「MECH→HW 输入清单」★) ★ |
| ★`iss290_onpass_must_change_list_to_hw` ★ | ★**E-1~E-6 必须随那一趟一起改的清单** (★已转 hw-lead 的 ISS-292「⑬ 追加」节★) ★ |
| ★`iss294_usbc_edge_opening_size_and_z_window` ★ | ★**第三条开口的 4 条几何取舍 + Z 向窗口** (★`OPEN_Y_eff(h)` = 4.60/4.60/5.80 不在板面坐标里 ★**本页只能登记不能验**★) ★ |

★⇒ ★**这 4 条散在分片里 ⇒ 谁也没一份「可直接抄进作业包 §3-S6 的完整结构侧输入」⇒ 那一趟开工时结构件必然缺料** ★★

---

## ★② 本单要交的三件 (★每件能独立验收★)

### ★B1 · 结构侧输入认领句全表 (★新建一份页★)

★**新建 `MECH/BOARD_ONEPASS_MECH_CLAIMS.md`** (★交卷时才有 ⇒ 现在不存在是正常的★)
⇒ ★**每条 = 5 要素**: ① **认领句原文** (★一段可直接抄进作业包 §3-S6 的话, 不许写「见别处」★) ② **数值 / 坐标** (★带坐标系标签: 160×100 台架板★) ③ **判据出处** (★哪个脚本 / 哪一页 / 哪一行★) ④ **待拍板标记** (★归 main→老板的, 你只标不代拍★) ⑤ **状态** (★已定 / 待拍 / `[0数据]`★)
⇒ ★**至少收齐 4 类**: ① **三条开口的认领句** (检修口 / 调试口 / ★**USB-C 边开口 `PORT_OPEN_USBC`**★) ② **座体类器件的落位认领句** (★`J_DEBUG` / `J_UART` / `J_USB_C` / `J_CHG` / `J_SOM_P1..P4`★) ③ **S6 那 20 个目标落位 × MECH 保留区的认领句** (★ISS-290 已验: 冲突 0 条·最小净距 4.6500mm★) ④ **E-1~E-6 里属于 MECH 侧的那几条** (★只列事实与代价★)
⇒ ★**页里必须有一节「还没主的输入」** (★列全 = 老板/PM 待拍的那几条, 不许自己拍★)

### ★B2 · 过期结论防漂闸 (★新建一道闸, 判据只许变严★)

★**新建 `MECH/check_mech_verdict_freshness.py`** (★交卷时才有 ⇒ 现在不存在是正常的★)
⇒ ★**判据**: 扫 `MECH/BOARD_ONEPASS_MECH_SYNC.md` + `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 里★**已被推翻的结论字样**★ (★至少含: 「结构侧缺一条边开口规格」/「缺一条边开口规格」/「登记为缺口」/「缺口, 待登记」★) ⇒ ★**每一处都必须有一条【显式订正节】覆盖它** (★老字保留留痕是【允许】的 ⇒ 但没有订正节 ⇒ **红**★) ⇒ ★**同一份结论不许在两页出现两种说法** ★
⇒ ★**反向用例 ≥ 4 条** (★在沙盒副本上做, ★真件一个字节不许碰★): ① **删掉那条订正节 ⇒ 必须红** ② **把老行改成「已订正」但删掉订正节 ⇒ 必须红** ③ **把老结论改写成另一种过期说法 ⇒ 必须红** ④ **正向对照: 现状 ⇒ 必须绿** (★证明闸不是恒红★)
⇒ ★`--selftest` **rc=0** ⇒ ★**反向用例一条都不许改松** ★

### ★B3 · 分叉扫描表 + 交卷单 + 分片

- ★**B3-1** · 出「**分叉全表**」: 扫了多少条结论 (N) · 发现多少条分叉 (M) · 逐条写清【在哪一行 / 两页分别怎么说 / 怎么处理 / 处理完剩什么】 ⇒ ★**贴原样 grep 输出** ★
- ★**B3-2** · ★**交卷单** `HANDOFF/2026-11-17_mech-lead_ISS295_结构输入认领与防漂闸.md` (★B0~B6 七块齐全 + 占位符残留 **0**★)
- ★**B3-3** · ★**分片** `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写 ⇒ ★**禁止 `open(p,"w")`★ ⇒ 写完 `grep -c iss295 state/fragments/mech.yaml` 必须 ≥ **4**★) ⇒ ★并把上面 4 条 need 的★**「main 该做什么」写成一条汇总 need (to=main)**★ (★answer 要用★**被问方开单时用的那个 key 逐字一致**★ ⇒ 差一个字 = 永远 pending★)

---

## ★③ 验收命令 (★自己跑, 把原样 rc 贴进交卷单★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_onepass_mech_sync.py; echo "rc=$?"
python3 MECH/check_onepass_mech_sync.py --selftest; echo "rc=$?"
python3 MECH/check_onepass_struct_crosscheck.py; echo "rc=$?"
python3 MECH/check_onepass_struct_crosscheck.py --selftest; echo "rc=$?"
python3 MECH/check_mech_verdict_freshness.py; echo "rc=$?"
python3 MECH/check_mech_verdict_freshness.py --selftest; echo "rc=$?"
python3 state/merge.py; echo "rc=$?"
python3 state/gate_check.py; echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★**期望**: 四道既有 MECH 闸全 rc=0 (★**不许被你这趟弄红**★) · 你那道新闸 rc=0 + `--selftest` rc=0 (★≥4 条反向用例全抓到★) · merge rc=0 · gate_check rc=0 (★**Q1 18/18**★) · 受保护 5 件 md5 逐字 = 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ★
★**板 mtime 必须仍是 `2026-11-06 07:07:17` (★零写板双重自证★)★**

---

## ★④ 边界 (★违反就是不合格★)

- ★**零写板** (★md5 + mtime 双重自证★) · ★**零落表** (★网表 / 脚表 / BOM 一个字节不许动★)
- ★**不许改 `HW/` 任何文件与分片** (★作业包 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 是 hw-lead 的地界 ⇒ 你只交认领句, 由 main 转抄★)
- ★**不许改既有 MECH 判据脚本** (★`MECH/check_onepass_mech_sync.py` / `MECH/check_onepass_struct_crosscheck.py` / `MECH/check_board_frame_coords.py` / `MECH/check_demo_struct_truth.py` / `MECH/board_port_opening_s6_check.py` 只读★) ⇒ ★**你的新闸是【新建】文件** ★
- ★**不许改 `state/gate_check.py`** (★挂闸是 main 的活, 你交闸 + 交命令★)
- ★**不许改 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 的机器块 `openings[]` / `rect` / `tiers`** (★N3b 比的就是它 ⇒ 动了必红★) ⇒ ★**只许改叙事文字与过期字样 (追加式, 老字保留作留痕)★**
- ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ **没有「批一句可以发」这个选项**★)
- ★**不替老板拍板** (★**4 条几何取舍 / Z 向窗口 / 立柱外径 / 座体真实高 h** = 只列事实与代价 + 建议默认值, 归 main→老板★)
- ★**不自签 issue_log** (★签字是 main 的活★)
- ★**只写自己的分片** `state/fragments/mech.yaml`
- ★**实物 `[实测]` = 0 条** (★本机无板、无量具、无打印机 ⇒ 板面数值只能引本项目已有的板读记录, 并标 `[实测]` 出处★)

---

## ★⑤ 交卷物 (★4 件★)

1. ★**新建** `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` (★B1 · 结构侧输入认领句全表 + 「还没主的输入」一节★)
2. ★**新建** `MECH/check_mech_verdict_freshness.py` (★B2 · 过期结论防漂闸 + `--selftest` ≥4 条反向用例★)
3. ★**交卷单** `HANDOFF/2026-11-17_mech-lead_ISS295_结构输入认领与防漂闸.md` (★B0~B6 七块齐全 + 占位符残留 0 + 原样 rc★)
4. ★**分片** `state/fragments/mech.yaml` (★原子写 + `grep -c iss295` ≥ 4 + 汇总 need to=main★)

---

## ★⑥ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架** (★哪怕只写 3 行标题 + 交付物清单★) ★
★**长任务一律 `nohup ... > logs/iss295/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) ★
★**单条 exec ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★
★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)
