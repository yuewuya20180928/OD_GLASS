★**ISS-289 · hw-lead 任务书 —— ★★【续做 cont1: 只补交卷单 B0~B6 + 跑回归验收贴 rc · 不许重做闸 / 不许重改订正块】★★** ★ (main · 2026-11-17 15:2x)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 15:2x** ★ · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-289 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · PCB 线 · 纯规格订正 + 一道闸 · ★★零写板 · 零落表 · 零改生成器代码★★** ★
> ★**优先级 (★时间不够就按这个顺序砍★)**: ★**① > ② > ③** ★ ★**① 和 ② 都不许砍** ★

---

## ① ★★你上一趟已经做完的部分 (★main 15:2x 本机实读 + 实跑, 零重做★) ★★

★**★你这趟的会话在 15:12 被网关掐断 (`abortedLastRun=true`) ⇒ 盘上的技术产出全在, 缺的只是交卷单正文★**

| # | 产出 | 盘上实测 (main 15:2x 实读) |
|---|---|---|
| 1 | ★**新闸** `HW/check_workpack_state_values.py` ★ | ★**26466 B** · `python3 HW/check_workpack_state_values.py` ⇒ ★**rc=0** (V1~V7 全过: 29 条登记两份文档逐字一致 · 29 条老字全在位 · 订正块在位 · **34 个现状值探针实测 == 期望** · 七类覆盖齐全 · 受保护 5 件 md5 逐字节不变) ★ · `--selftest` ⇒ ★**rc=0 · 反向用例 10/10 全抓到** ★ |
| 2 | ★**作业包追加式订正块** `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` ★ | ★**九处订正在位** (① S7 段标题 ② S7 量化判据第一条 ③ S7 量化判据第二条 ④ §3 表 S7 行 ⑤ §4 验收表 S1~S7 行 ⑥ §2 的 X-2 坑行 ⑦ §6.1 表 S7 行 ⑧ §8.1.3-3 ⑨ §1.1 第 1 行) · 末尾追加式订正块 + **29 条 `state_baseline` 登记**在位 ★ |
| 3 | ★**清单页追加式订正** `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ★ | ★已改 (14:5x 后 mtime 更新) ★ |
| 4 | ★**分片** `state/fragments/hw.yaml` ★ | ★`grep -c iss289` = **9** ⇒ 含 artifact + ★**5 条 need**: `iss289_footprint_186_vs_185` · `iss289_ref_suffix_156` · `iss289_s1_specjson_devices_missing` · `iss289_preflight_generator_stale` · `iss289_gate_registration` ★ |

★**★main 15:2x 本机独立实跑回归 (不抄任何交卷报告) ⇒ 全绿★**:
```
python3 HW/check_onepass_preflight_coverage.py            ⇒ rc=0
python3 HW/check_onepass_preflight_coverage.py --selftest ⇒ rc=0
python3 HW/check_board_frame_caliber.py                  ⇒ rc=0
python3 HW/check_board_frame_caliber.py --selftest       ⇒ rc=0
python3 state/merge.py                                   ⇒ rc=0
python3 state/gate_check.py                              ⇒ rc=0
板 md5 611b869e13518c3c023fb178f91a0075 (mtime 仍 2026-11-06 07:07:17) · .kicad_pro 3e504d2be83152e337949723e909be1b ⇒ 逐字节未变
```

★**⇒ 本单只剩一件事: 把交卷单写完 + 把两条差异的结论写清 + 贴你自己实跑的 rc★**

---

## ② ★★你唯一缺的东西: 交卷单 B0~B6 全是「施工中」骨架 ★★

★**当前文件**: `HANDOFF/2026-11-17_hw-lead_ISS289_作业包现状值对回盘面.md` (★**1175 B**★) ⇒ ★**B0 / B1 / B2 / B3 / B4 / B5 / B6 七段全是「★(施工中 —— 收工补全)★」「★(施工中)★」★** ⇒ ★**本 job 的验收标准就是: 这七段全部填满, 且 0 处「施工中 / 待填」残留★**

| 段 | 本段必须写什么 (★内容主体现成, 你自己实读补齐, 不许照抄本任务书★) |
|---|---|
| ★**B0** ★ | ★开工前基线: 受保护 5 件 md5 + 板 mtime (★板 `611b869e…` / `.kicad_pro` `3e504d2b…` / 网表 `37f62ac3…` / 脚表 `a4270120…` / BOM `5d02bece…`★) ★+ 开工时刻 |
| ★**B1** ★ | ★**六处订正 (★现在是九处, 把你实际改的九处逐条列出来★)**: 每处 = 位置 / 原字面 / 现字面 / 依据 (★哪次合法落表造成·单号 + 台账行号★) ⇒ ★**并写清「老字零删除」的逐字节证明 (★追加点字节偏移★)** ★ |
| ★**B2** ★ | ★**ISS-287 那两条差异对回的结论** ★★⇒ 见 §③ 两个问题 ★★ |
| ★**B3** ★ | ★**新闸** `HW/check_workpack_state_values.py`: V1~V7 每条一条一句话 + **34 个探针的分类计数** (★dnp_zero_mark / dnp_token_count / footprint_count / ref_suffix / defect_count / md5_baseline / copper_and_frame / 同一个数可跨类别但登记必须归一类★) + **追加式自证怎么做的** (★V2 那 29 条老字 anchor 的机制★) + **七类覆盖的判定式** ★ |
| ★**B4** ★ | ★**边界自证** (★逐条自证 + 贴数字★): 零写板 (★md5 + mtime 双重★) · 零落表 (★网表/脚表/BOM 三个 md5 前后不变★) · 零改生成器代码 (★`state/gen_pcb_netlist_board.py` / `state/gen_netlist.py` md5 未变★) · 老字零删除 · 不碰 `MECH/` / `SW/` · 零外发 · 不替老板拍板 · 不自签 issue_log ★ |
| ★**B5** ★ | ★**验收命令 + rc 原样** (★你自己实跑, 不要贴 main 的★) ⇒ 见 §④ 命令表 ★+ ★**必贴 `check_workpack_state_values.py --selftest` 的 10/10 输出原文** ★ |
| ★**B6** ★ | ★**结论 + 给 main 的 need** ★ ⇒ ★**把你分片里那 5 条 need 逐条复述 (★一句话一条: 是什么 / 归谁 / 卡不卡「板只改一次」那趟★)** + ★**未决项** + ★**给老板/PM 的拍板项 (只列事实与代价, 不代拍)** ★ |

---

## ③ ★★B2 要回答 main 的两个问题 (★必须给结论, 不许只列现象★) ★★

### ③-1 封装数: 186 (真盘) vs 185 (ISS-287 沙盒) —— **动板那趟按哪个数走?**

★**事实**: ★**真盘闸实测 = 186** (★`HW/check_workpack_state_values.py` V4 的 `W11_FOOTPRINT_COUNT` 实测 **186** == 期望 186★) ★· ★**ISS-287 沙盒实测 = 185** (★13:49~13:54 沙盒干跑探针测出★) ⇒ ★**差 1 件★**
★**你要交**: ★**① 那 1 件差在哪 (★是沙盒生成器少生成一个? 是位号改名后必有差异? 是沙盒树拷贝漏了某个器件?★) ⇒ 用盘面证据说清★** ★· ★**② 动板那趟按哪个数走 (★186 还是 185★) ⇒ **并写清这个结论对「板只改一次」那趟有没有影响** ★· ★**③ 若两数都可能对 (★比如「官方板 185 + 新增一个件 = 186」★) ⇒ 把判据写死成一句可执行口径, 让闸能长期自动判★**

### ③-2 `_1` 后缀位号: 官方板 1 个 vs 登记 156

★**事实**: ★**闸实测 `W18_S1_SUFFIX_ONE` = 1** (★官方板带 `_1` 后缀的位号 = 1 个★) · `C03_B01_REF_SUFFIX` 实测 = **156** (★作业包 §S1 要改的 `X`→`X_1` 条数 = 156★) ⇒ ★**这两个数不是一回事, 别混★**
★**你要交**: ★**① 156 是什么口径 (★是「要改名的位号数」还是「已带后缀的位号数」?★) ★· ★**② 改完 156 个之后, 官方板上还会有几个 `_1` 后缀位号 (★是 1 还是别的数★) ⇒ ★**③ 这两个数进了闸没有 (★进了就写明是哪个登记项; 没进就补一条登记 + 说明为什么补★)** ★**
★**★分片里已有一条 need `iss289_ref_suffix_156` ⇒ 你要把它写成结论 (★是收口还是保留为未决, 说清★)★**

---

## ④ ★★验收命令 (★本机实跑, rc 原样贴进交卷单 B5★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_workpack_state_values.py            # rc=0 (★你新建的闸★)
python3 HW/check_workpack_state_values.py --selftest # rc=0 (★反向用例 ≥10 条·全抓到★)
python3 HW/check_onepass_preflight_coverage.py       # rc=0
python3 HW/check_onepass_preflight_coverage.py --selftest  # rc=0 (★反向一条不许少★)
python3 HW/check_board_frame_caliber.py              # rc=0
python3 HW/check_board_frame_caliber.py --selftest   # rc=0
python3 HW/check_netlist_contradiction_r3.py         # rc=1 (★现状读数: FINDINGS=2 / R3-A4 零标记 43? 实测 40★ ⇒ 原样贴★)
python3 state/merge.py                               # rc=0
python3 state/gate_check.py                          # rc=0 (★Q1 18/18★)
python3 state/issue_check.py                         # rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e13518c3c023fb178f91a0075 (mtime 仍 2026-11-06 07:07:17) · .kicad_pro 3e504d2be83152e337949723e909be1b
# ★★网表 37f62ac3f0b81d92ca7d48fdea717f07 · 脚表 a4270120454aedf7a23c92cd8985c8a6 · BOM 5d02bece9477ffce5fbe0193c7d5cce4
# ★★五件跑前跑后逐字节相同 ⇒ 贴前后两次 md5 对照★★
```

★**受保护 5 件 (★你跑前跑后各贴一次 md5, 两次必须逐字相同★)**: ★**板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4`** ★

---

## ⑤ ★★边界 (★逐条自证, 写进交卷单 B4★) ★★

- ★**零写板** (★板 md5 + mtime 双重自证★) ⇒ ★**不许跑 `state/gen_pcb_netlist_board.py`, 不许跑任何布线臂, 不许碰 `HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro`★**
- ★**零落表** (★网表 / 脚表 / BOM 三个 md5 前后不变★) ⇒ ★**不许碰 `HW/SCHEMATIC_LANDING_V1_LANDED.md`★**
- ★**零改生成器代码** (★`state/gen_pcb_netlist_board.py` / `state/gen_netlist.py` / `state/gen_kicad_sch.py` 一律只读★)
- ★**★不许重做闸** (★`HW/check_workpack_state_values.py` ★**一个字都不许改**★ ⇒ ★**它已 rc=0 · selftest 10/10★ ⇒ ★**若你认为它有 bug ⇒ ★**不许直接改★ ⇒ 写进交卷单 B5 的「未决项」并告诉 main, 由 main 裁决★** ★**
- ★**★不许重改订正块** (★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 与 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的追加式订正块 ★**已由闸 V2/V3 自证在位★ ⇒ ★**不许再动一个字★ ⇒ ★**若你认为订正块有漏 ⇒ 写进 B5 未决项, 不许自己补★** ★**
- ★**零改既有闸的判据方向** (★`HW/check_onepass_preflight_coverage.py` / `HW/check_board_frame_caliber.py` 只读★)
- ★**不碰 `MECH/` / `SW/` 的文件与分片** (★`state/fragments/mech.yaml` / `sw.yaml` 一律不许写★)
- ★**零外发** (★不许发邮件 / 不许联系供应商 / 不许下采购单★)
- ★**不替老板拍板** (★只列事实与代价★)
- ★**不自签 `issue_log`** (★verify_by = main ⇒ 签字是 main 的活★)
- ★**只写自己的分片** (★`state/fragments/hw.yaml`★) ⇒ ★**走 `python3 state/frag_write.py --agent hw-lead` 原子写 ★(★禁止 `open(p,"w")`★) ⇒ 写完 `grep -c iss289` 校验★**
- ★**实物 [实测] = 0 条** (★本机无量具/无打印机 ⇒ 任何需要实物才能定的量, 一律标 `[0数据]` 并给降级路径, 不许编★)
- ★**并发提示 (★必读★)**: ★**sw-lead 的 ISS-288 此刻正在飞 (★它在写 `SW/`, 15:18 刚写 `HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md`★) · mech-lead 的 ISS-290 此刻正在飞 (★它在写 `MECH/`★) ⇒ ★**你只读 `SW/` / `MECH/`, 只写 `HW/` + `HANDOFF/` + 你自己的分片 ⇒ 跑验收前若某个闸红了, 先看是不是别人刚改的, 不要替别人改** ★
- ★**纪律 (★你上一趟就是被这两条掐的★)**: ★**交卷单第一件事 = `write` 建骨架 (★哪怕 3 行★) ★· ★**每填完一段立刻把该段的 rc 追加进交卷单 (★不许攒到最后一次写★) ★· ★**单条 `exec` ≤ ~120 秒 ★· ★**长任务 `nohup ... > logs/iss289/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★) ★· ★**每 10 分钟至少一次写盘★**

---

## ⑥ ★★你要回答 main 的三个问题 (★写进交卷单 B6★) ★★

1. ★**封装数 186 vs 185 的差 1 件到底在哪? 动板那趟按哪个数走?** (★§③-1★)
2. ★**`_1` 后缀位号: 官方板 1 个 vs 登记 156 这两个数分别是什么口径? 改完名之后官方板还剩几个 `_1`?** (★§③-2★)
3. ★**这 29 条 `state_baseline` 登记里, 有没有哪一条是「下一次落表又会打漂」的 (★= 写死的现状值而不是台账为准★)? 有的话是哪一条, 要不要改成台账口径?** ⇒ ★**这直接决定「板只改一次」那趟会不会又被落表打回重画★**

★**★答完这三个, 本单就闭环了 ⇒ 交卷单填满 + 验收 rc 贴齐 + 分片 grep 校验 ⇒ main 复验落 verified★**
