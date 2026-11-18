★**ISS-287 · 任务书 —— ★★【「板只改一次」那一趟的 A 类步【沙盒干跑可行性探针】】★★** ★

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 13:4x** ★ · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-287 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 纯分析 + 可行性探针 · ★★零写板 · 零落表 · 零改生成器代码★★ ★

---

## ★① 为什么要做这一单 (★背景三条, 都是实测★)

1. ★**「板只改一次」那一趟 (= S1~S13) 现在只被 2 条老板拍板卡住** (★`DECISION_PENDING_2026-11-16.md` §A-补16 ②★): ★**W-2 (USB `D−` 侧补不补 ESD)** + ★**`D_LED_G` 外露/可见性** ⇒ ★**这两条没拍之前, 那一趟【不许开工】★** ⇒ ★**⇒ 眼下能做的, 恰恰是【不依赖任何人就能走的步】** ★
2. ★**那一趟一旦开工, 板 md5 就变 ⇒ 只能变一次** ⇒ ★**所以最怕的不是"干得慢", 是"干到一半才发现那条链在真盘外根本跑不通" ⇒ 白跑 = 板改第二次** ★
3. ★**事实**: 整条链 (网表 → 原理图 → 板 → 布线 → Gerber → 投产包) ★**从来没有在【真盘之外】完整跑过一遍** ⇒ ★**"能不能干跑"这件事, 现在是猜的, 不是测的** ★

★**⇒ 本单的【唯一目的】**: ★**用实跑回答一个问题 —— 「板那一趟」能不能在【真盘外】先跑一遍? 能/不能 + 缺哪几个开关** ★ ⇒ ★**main 据此写「板那一趟」那一单的任务书 (★那才是真正动板的一趟★)** ★

---

## ★② 要交的 4 个答案 (★逐个用本机实跑回答★)

### ★答案 1 · 复制树能不能自洽 (★原理图侧★)

★**问**: 把 `HW/` + `state/` + `MECH/` + `SW/` + `config/` + `deploy/` ★**复制到 workspace 内的沙盒目录** (★不许放 `/tmp` —— 实测 `/tmp` 已 5.6G/7.5G, 沙盒会写挂★) ⇒ `state/gen_kicad_sch.py` / `gen_netlist.py` / `gen_pcb_netlist_board.py` / `gen_bom.py` 里的 `PROJ` 到底是 ★**由 `__file__` 推导** 还是 ★**写死绝对路径** ★?

★**答法**: ★**逐个读那 4 个脚本里 `PROJ` / `OUT_DIR` / `OUT_SCH` / `OUT_NET` 的定义行 + 实跑一次副本里的脚本, 看产物落在副本里还是落回真盘** ★
★**若答"写死绝对路径"** ⇒ ★**这就是缺的开关** ⇒ ★**如实写出来 (哪个脚本 · 哪一行 · 需要什么 env 或改法) ★★不许自己去改脚本★★**

### ★答案 2 · 板侧能不能单独沙盒 (★已有先例, 要实测确认★)

★**先例 (★盘上已写明★)**: `state/gen_pcb_netlist_board.py:55` ⇒ ★`PCB = os.environ.get("PCB_OUT") or <真盘板>★` ★· ★`:75~82` ⇒ ★**一道守卫: 写正式板必须显式 `PCB_ALLOW_OFFICIAL=1`; 实验臂 (`PCB_OUT=/tmp/…`) 一律不受影响** ★
★**要实测确认两件事**: ① 沙盒板**真的被写出** (★`PCB_OUT=<沙盒>/board.kicad_pcb`★) ② ★**真盘板 md5 + mtime 前后逐字节不变** ★

### ★答案 3 · 只生成不布线能不能跑通

★**先例**: `state/gen_pcb_netlist_board.py:1179` ⇒ ★`PCB_SKIP_ROUTE=1` ★
★**要实测**: 在 ★**副本树里** ★跑一次 (★只生成, 不布线★) ⇒ ★**出板成功? 用时多久? 中间有没有哪一步去找真盘的文件 (⇒ 那就是漏网的写盘路径, 必须点名)★** ★

### ★答案 4 · 沙盒板的读数 (★这 5 个数就是「板那一趟」的现状基线★)

| 读数 | 现状基线 (★盘上实测·任务书里已写死, 你只需在沙盒里复核是否一致★) | 判据口径 |
|---|---|---|
| 封装数 | ★**186** ★ | `pcbnew` 读板 |
| 板框 / 层数 | ★**160×100 mm / 8 铜层 / 帧 `B160x100`** ★ | `HW/PCB/BOARD_FRAME_CALIBER.md` |
| S6 坐标 | ★**已在目标位 19 / 不同 1 (`R_SEL_D3_P`) / 缺失 0** ★ | ★`python3 HW/check_board_frame_caliber.py` 的 S6 段 ★ |
| DNP 标记 | ★**43 个位号零标记 (现状) ⇒ S7 要做到 43 全标** ★ | ★`HW/check_netlist_contradiction_r3.py` R3-A4★ |
| 位号问号 | ★**现状: 186 个位号带 `_1` 后问号行数 0** (★S1 的判据★) | ★`bash state/kicad.sh sch export bom …` + `grep -c '?'` ★ |
| unconnected | ★**45 (现状) ⇒ 这是 S8 的战果, 本单【不许碰】** ★ | ★`state/check_pcb_drc.py` ★ |

★**★你这 6 个数的作用**: ★**「板那一趟」开工前, 先有一张【实测现状表】⇒ 那一趟跑完, 逐项对比就知道有没有变坏 ⇒ ★★不许用"应该没问题"交卷★★ ★

---

## ★③ 边界 (★违反就是不合格★)

★**零写板** ⇒ ★真盘 `HW/PCB/demo_mainboard.kicad_pcb` 的 **md5 与 mtime 前后都必须 == `611b869e13518c3c023fb178f91a0075` / 2026-11-06 07:07:17** ★
★**零落表** ⇒ ★真盘 网表/脚表/BOM 的 md5 前后必须 == `37f62ac3f0b81d92ca7d48fdea717f07` / `a4270120454aedf7a23c92cd8985c8a6` / `5d02bece9477ffce5fbe0193c7d5cce4` ★
★**零改生成器代码** ⇒ ★**不许改 `state/gen_*.py` 一个字节** (★S1 的 `HW/SCHEMATIC_V1_SPEC.json` 真源改动 + S7 的 `make_footprint()` DNP 支持 = 属「板那一趟」那一单, 不许提前落★) ⇒ ★**沙盒副本里也不许改** (★沙盒里改了也不能回灌★) ★
★**不许把沙盒产物拷回真盘** (★沙盒板只用于读数; 真盘板仍是唯一官方板★)
★**不许跑布线臂** (★`PCB_SKIP_ROUTE=1` 就是"不布线"; 若某条路径仍触发布线 ⇒ ★**立刻停手并记录**★)
★**不许碰别人的分片** (★只写 `state/fragments/hw.yaml`, 走 `python3 state/frag_write.py --agent hw-lead` 原子写 + `grep` 校验★)
★**零外发** · ★**不替老板拍板** · ★**不自签 issue_log** (★签字是 main 的活★)

---

## ★④ 时间盒与纪律 (★这项目的老教训★)

★**整单 ≤ 90 分钟** ⇒ ★**答不完就交「答到哪 + 缺哪个开关」的降级方案, ★★不许为了跑通去改脚本★★ ★
★**长任务一律 `nohup … > logs/iss287/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★)
★**单条 `exec` ≤ ~120 秒** · ★**每 10 分钟至少一次写盘** · ★**每落一件交付物就把 rc 追加进交卷单** ★
★**交卷单第一件事就是 `write` 建骨架** (★哪怕只写 3 行标题 + 交付物清单★) ★
★**不许把整份大文件读进来** (★只 grep 你要看的行★)

---

## ★⑤ 交付物 (★3 件★)

1. ★**交卷单** `HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md` (★B1~B5 齐全: ① 4 个答案逐条 + 实测 rc ② 那 6 个读数 ③ 边界自证 (受保护 md5 前后对照) ④ 结论: 【能/不能干跑 + 缺哪几个开关】⑤ 自证复现命令★)
2. ★**沙盒目录** ★**留在 workspace 内** ★`tmp/iss287_sandbox/` (★不许放 `/tmp`★) + 一份 `tmp/iss287_sandbox/README.md` 说明【怎么复跑】+ 【沙盒与真盘的差异清单】
3. ★**分片** `state/fragments/hw.yaml` (★走 `state/frag_write.py --agent hw-lead` 原子写 ⇒ 写完 `grep` 校验 `iss287` 在不在★)

---

## ★⑥ 验收 (★main 复跑, 逐条对照★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★期望: 板 611b869e… / .kicad_pro 3e504d2b… / 网表 37f62ac3… / 脚表 a4270120… / BOM 5d02bece… ★
# ★★与本单开工前逐字节相同 ⇒ 零写板 · 零落表 自证★★
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb      # ★期望仍是 2026-11-06 07:07:17★
python3 HW/check_board_frame_caliber.py;  echo "rc=$?"   # 期望 rc=0
python3 HW/check_onepass_commit_order.py; echo "rc=$?"   # 期望 rc=0 (变更区 0 行 ⇒ 板没变过)
python3 HW/check_land_row_anchors.py;     echo "rc=$?"   # 期望 rc=0 (PASS=310)
python3 state/merge.py && python3 state/gate_check.py; echo "rc=$?"   # 期望 0 / 0 (Q1 18/18)
python3 state/issue_check.py; echo "rc=$?"             # 期望 rc=0
```

★**★一句话交卷口径**: ★**「能不能干跑 = 能 / 不能 + 缺哪几个开关」+ 那 6 个读数 + 真盘 5 件 md5 前后不变** ★ ⇒ ★**别写过程流水账, 写结论 + 证据行★** ★