★★★★【main 2026-11-23 01:4x · ★★PCB 线 · 「板侧项全集」页被手改 ⇒ 生成器重跑会蒸发 E-1 · 修生成器 + 建「重跑不蒸发」机器闸 · 零写板 ★★】★★★★
★**ISS-343 把 `B33_PIN_LAND_1P27` (E-1 排针 land 0.50→1.27) 直接手写进了 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 §7 JSON 块 ⇒ 而这份页是生成器 `state/_iss277_build_preflight.py` 的产物 ⇒ 下一次重跑生成器, 这一条【静默蒸发】 ⇒ 「板只改一次」那一趟的板侧项全集少一条 ⇒ 实物排针照样装不进 ⇒ 补做 = 板 md5 变第二次 ★**

★**派活方 = 项目总工 (main / moli) · 2026-11-23 01:4x · cron fb67af40 (队列自动派活) ★★
★**来源 = main 2026-11-23 01:4x 本机实读 + 实跑 (★不抄任何 agent 报告★) ★**
★**工作目录 (★所有命令都在这里跑★)**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses`

---

## §0 事实 (★main 本机实读 + 实跑, 逐条可复现★)

★**① 页现在【表与 JSON 不同源】了 (main 实跑脚本解析, 不是目测) ★**:
★**`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (★它自己的定位: 「板只改一次」那一趟 S1~S13 的**板侧项全集**★) ★**
- ★**§2 表格: 32 行 · 32 个唯一 id = `B01_REF_SUFFIX` … `B32_V2_NET_RENAME` (★表里**没有** `B33`★) ★**
- ★**§7 JSON 块: 33 条 (★最后一条 = `B33_PIN_LAND_1P27`★) ★**
- ★**全页 `grep -c "B33"` = 1 ⇒ 只在 §7 JSON 块内 (行 543), §2 表里一处都没有 ★**
- ★**⇒ 页脚那句「★**本页由 `state/_iss277_build_preflight.py` 生成 (★页与 JSON 同源 ⇒ 不会写岔★)** ★」现在是**假的** ⇒ 32 ≠ 33 = 已经写岔了 ★**

★**② 生成器里根本没有这一条 (main 实跑 grep) ★**:
★**`state/_iss277_build_preflight.py` 的 `ITEMS_RAW` (★行 260★) 只有 `B01_REF_SUFFIX` … `B32_V2_NET_RENAME` (★32 条★) ⇒ ★**grep `B33|PIN_LAND|1\.27|排针` 在整个生成器里 0 命中** ★**
★**⇒ 生成器重跑 ⇒ §2 表 32 行 + §7 JSON 32 条 ⇒ `B33_PIN_LAND_1P27` **当场蒸发** ★**

★**③ sidecar 里也没有 (★sidecar = 生成器的第二个输入 = 追加式订正块的存放处★) ★**:
★**`state/_iss277_preflight_appendix.md` (29,471 B @ 2026-11-18 01:16) ⇒ grep `B33` / `1.27` / `排针` / `PIN_LAND` 全 0 命中 ★**

★**④ ⇒ 「页回退这条路已经堵死」这个结论, 现在是假的 (main 本机比对 md5) ★**:
- ★**ISS-292 (2026-11-17) 的交卷页原文**: 「★**重跑幂等: 页 md5 跑前跑后逐字节相同 (★`159bf20fe71c36e48292f39dafc46a35`★)** ⇒ ★**页回退这条路已经堵死** ★」 ★**
- ★**现在真页 md5 = `8ae70471604dcf447f43477dbada3f13` (★mtime 2026-11-23 01:09:04★) ⇒ ★**≠ `159bf20f…` ⇒ 页在 ISS-292 之后被手改过 (★就是 01:09 那次改 B33★) ★**
- ★**⇒ 现在只要有人跑一次生成器 ⇒ 页回到 `159bf20f…` 那一族形态 ⇒ B33 没了 ⇒ 「已堵死」当场失效 ★**

★**⑤ ★★重跑不是假想, 是流程里写着的动作 ★★ (main 实读 `state/_iss304_sync_state_baseline_md5.py:145`) ★**:
★**「★落表后重锚流程: ① `python3 state/_iss277_build_preflight.py` ② …」 ★**
★**⇒ ★**每次落表重锚都会触发这次蒸发** ⇒ 不是「以后有人跑」, 是「流程每次跑都跑」 ★**

★**⑥ ⇒ 覆盖度闸给的是【假绿】 (main 实读 `HW/check_onepass_preflight_coverage.py`, ★40,636 B @ 2026-11-23 01:12★) ★**:
- 该闸判的是「清单页里有没有这条」⇒ ★**页里现在【有】`B33` ⇒ 判绿 ⇒ ★**但下一次重跑之后页里【没有】了 ⇒ 该闸不会红 (★它从不读生成器★) ⇒ 绿是骗的 ★**
- ★**这正是 ISS-343 自己点名的那条「一条不带新位号的板改 (同一 `J_DEBUG`/`J_UART` 改 land pitch) 天生查不出」的放大版: 现在连【页自己】都会被重跑吞掉 ★**

★**⑦ 本仓铁律早就写过, 是这一单没照做 (main 实读两份任务书原文) ★**:
- ★**ISS-304 任务书 (`state/dispatch_briefs/ISS-304_hw_workpack_state_values_reanchor.md:52`) 逐字**: 「★**不许手改生成器产物**: ★**清单页 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`) 是 `state/_iss277_build_preflight.py` 的产物 ⇒ 改它 ⇒ 等于下一次重跑就回退 ⇒ ★**必须改 sidecar / 生成器, 再重跑生成器** ★」 ★**
- ★**ISS-292 任务书 (`state/dispatch_briefs/ISS-292_hw_preflight_generator_realign_cont1.md:107`) 逐字**: 「★**不许改 `state/_iss277_build_preflight.py` 的取数逻辑 (★那部分已经对了★)** ★**只许改它允许的地方 = 加 E-1~E-6 那一条的读入 (★不许写死六条·从真源读★)** ★」 ★**
- ★**⇒ ★**E-1 本来就该长在生成器里** (★IS﻿S-292 当年就是这么规划的★) ⇒ ★**本单就是把这条路补上 ★**

★**⑧ ★★病根在派单口径, 不在 agent (★main 自认★) ★★**:
★**ISS-343 的任务书 §1-① 写的是「★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` **追加一条 item**★」⇒ ★**agent 照做, 直接把 JSON 条目手写进产物页 ⇒ 违反了本仓铁律 ⇒ ★**这一条是 main 的派单口径漏了「要落到生成器 + 重跑」这一步 ⇒ 本单把它补上 (★★不许把这条算成 agent 的错★★) ★**

★**⑨ 本条【不】依赖老板拍板 (★老板那 9 件还在队列里, 本单不许拿它当阻塞项★) ★**:
★**E-1 = main 2026-11-17 18:45 已拍死** (★`state/fragments/pm.yaml` → `needs_from` → key `main_e1_e2_board_side_rulings_20261117` → `decision` = 「E-1 = 按 1.27mm 排针定 + 板 land 并进那一趟重画」★) ★
★**⇒ 本单做的是「让这条【重跑不蒸发】」⇒ 纯技术活 ⇒ 现在就能做 (★零写板★) ★**

---

## §1 本单要交付什么 (★四件, 不许跑题★)

★**① 把 E-1 补进【生成器】 (★不是补进页★) ★**
- ★**改 `state/_iss277_build_preflight.py` 的 `ITEMS_RAW` (★行 260★) ⇒ 加一条 9 元组 (★格式照抄 `B01_REF_SUFFIX`/`B32_V2_NET_RENAME` 两条★) ★**
- ★**id = `B33_PIN_LAND_1P27` (★与 ISS-343 已写进 JSON 的 id 保持一致 ⇒ 不许改 id, 不许重名★) ★**
- ★**`source_iss` = `ISS-290` (★★**必须**保持 `ISS-290` ⇒ ISS-343 已把 `ISS-290` 加进 `HW/check_onepass_preflight_coverage.py` 的 `SOURCES` ⇒ 你改成别的 id 会让那个闸判「来源不明」★★) ★**
- ★**★**九个字段的值不许写死现状** ★**: 按生成器铁律①「★现状值一律从真源读, 一律不许写死★」⇒ ★**板读 pitch 必须现读板 (★生成器里已有 `run()` 辅助函数 + 多条 `bash state/pcbnew_py.sh -c "import pcbnew;…"` 范例★) ⇒ ★**BOM/网表里的 1.27 从 `HW/BOM_v1.csv` / `HW/netlist_v1.csv` 读 ⇒ 读不到 ⇒ fail-closed 拒写页 (★与生成器现有两条真源读法同款纪律★) ★**
- ★**★**反向要求 (★本项目铁律★)★**: ★**不许把 `0.50` / `1.27` / 铜箔坐标写死成常量** ⇒ ★**板那一趟改完 land 后, 重跑生成器 ⇒ 这一条的现状值必须自己变成 1.27 ⇒ 这才算真源读 (★你的反向用例里必须证明这一条: 沙盒里把板读结果改成 1.27 ⇒ 页里的现状值跟着变 ⇒ 不是死值★) ★**

★**② 重跑生成器 ⇒ 页回到【同源】 (★表 33 行 + JSON 33 条 + id 集合逐一相等★) ★**
- ★**跑 `python3 state/_iss277_build_preflight.py` (★cwd = 项目根★) ★**
- ★**验收口径 (★三条都要机器证, 不许目测★) ★**:
  1. ★**§2 表行数 == §7 JSON 条数 == 33 且两边的 id 集合【逐一相等】 (★不许只比个数★) ★**
  2. ★**除新增 `B33` 外, 其余 32 条的【老字一字未删】 ⇒ 逐行 diff 贴出来 (★追加式纪律★) ★**
  3. ★**★**若重跑导致别的行的现状值也变了 (★生成器是「从真源读」的 ⇒ 落表一变它就变★) ⇒ 不许默默接受 ⇒ 必须逐条列出「哪一行变了 / 为什么变 / 是不是落表带来的合法变化」★★ ★**
- ★**★**沙盒跑法 (★不许拿真页练手★)★**: ★**`PREFLIGHT_PROJ` 环境变量可指向沙盒副本 (★生成器第 47 行 PROJ 的定义★) ⇒ 沙盒副本必须落在【项目盘】(★`tmp/iss349/…`★) ⇒ ★**`/tmp` 是带 userquota 的 tmpfs 且配额已打满 ⇒ 写 /tmp 必 EDQUOT ⇒ 门禁输出落 /tmp 会拿到假读数 (rc=120 / 0 字节) ⇒ 会把「闸红」和「闸崩」混成一团★) ★**

★**③ 新建机器闸 `HW/check_preflight_regen_idempotent.py` (★只读 + 沙盒 · 独立脚本 + 自测★) ★**
- ★**判据三条 (★每条都要能当场判红, 不许是装饰★) ★**:
  1. ★**§2 表 id 集合 == §7 JSON id 集合 (★逐个相等, 不是只比个数★) ⇒ 不等 ⇒ 判红并点名差集 ★**
  2. ★**真页 == 生成器沙盒重跑输出 (★`PREFLIGHT_PROJ` 指沙盒 ⇒ 输出 md5 == 真页 md5 ⇒ 零行差异★) ⇒ 不等 ⇒ 判红并贴 diff ★**
  3. ★**★**每一条 item 的 `source_iss` 必须仍在 `HW/check_onepass_preflight_coverage.py` 的 `SOURCES` 里 (★只读那个文件, 不许改它★) ⇒ 不在 ⇒ 判红并点名 ★**
- ★**★**方向纪律 (★本项目铁律★)★★: ★**只许【加严】不许【放宽】** ★ ⇒ ★**不许改 `HW/check_onepass_preflight_coverage.py` 的任何判定逻辑 (★它是钉板闸⑥★) ⇒ ★**不许改 `HW/check_workpack_state_values.py` (★ISS-289 的闸★) ⇒ ★**不许改 `state/gate_check.py` (★那是 main 的地界★ ⇒ 你把「要 main 挂进 gate_check 的那一行」写进交卷页 §B4, main 自己挂) ★**
- ★**★**反向用例 (★≥3 条, 带 `--selftest`, 末行 `ALL TESTS PASS`, rc=0★)★★:
  - ★**R1**: 沙盒副本里把生成器 `ITEMS_RAW` 的 `B33` 那条删掉 ⇒ 重跑 ⇒ 页回到 32 条 ⇒ ★**闸必须判红并点名「B33 缺失 / 表与 JSON 不等」** ★
  - ★**R2**: 沙盒副本里把真页 JSON 块的 `B33` 的 pitch 改成假值 (★如 `9.99`★) ⇒ ★**闸必须判红 (★因为真页 != 重跑输出★) ★**
  - ★**R3**: 沙盒副本里把某条 item 的 `source_iss` 改成一个不在 `SOURCES` 里的号 ⇒ ★**闸必须判红并点名该 id** ★
  - ★**⇒ 三条例外验证完必须恢复原件 ⇒ 判绿 ⇒ ★**闸不是只会在坏情况下红, 也要能在好情况下绿 (★别写出一个永远红的闸★) ★**

★**④ 交卷三件 (★与本仓既有交卷格式一致★) ★**
- ★**交卷页 `HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md` (★B0~B7 齐全: B1 结论 / B2 逐条验收 / B3 证据分级 / B4 闸的 rc·入参·白名单·**要给 main 的 gate_check 挂载行** / B5 卡点 / B6 命令原样输出 / B7 边界自证★) ★**
- ★**`logs/iss349/` (★本单新建 `logs/iss349/run_iss349.sh` ⇒ 一条命令可复现全部读数★) ★**
- ★**分片 `state/fragments/hw.yaml` (★**只许**用 `python3 state/frag_write.py --agent hw-lead` 写 ⇒ **禁止** `open(p,"w")` 手写 YAML★) ★**

---

## §2 边界 (★违反了就不是交卷★)

| ★不许做 ★ | ★为什么 ★ |
|---|---|
| ★**写板 / 改板 / 重跑布线** ★ | ★「板只改一次」铁律 + 本单是零写板单 ★ |
| ★**改网表 / 脚表 / BOM / 原理图 / `.kicad_pro`** ★ | ★板那一趟要对着一份【不再变】的网表画 ★ |
| ★**手改 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`** ★ | ★★它是生成器产物 ⇒ 手改 = 下次重跑就回退 (★本单存在的全部理由★)★★ ★ |
| ★**改 `HW/check_onepass_preflight_coverage.py` 的判定逻辑** ★ | ★它是钉板闸⑥ ⇒ 只许读 ★ |
| ★**改 `state/gate_check.py` / `state/issue_log.yaml` / `state/fragments/pm.yaml` / `mech.yaml` / `sw.yaml`** ★ | ★都是别人的地界 (★签字是 main 的活★) ★ |
| ★**把沙盒 / 日志落 `/tmp`** ★ | ★`/tmp` userquota 已打满 ⇒ EDQUOT ⇒ 假读数 ⇒ 沙盒用 `tmp/iss349/` (项目盘) ★ |
| ★**外发任何邮件 / 询价 / 问询 / 采购** ★ | ★★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★★ ★ |
| ★**替老板拍板** ★ | ★E-1 早已由 main 拍死; 本单不新增任何老板拍板面 ★ |

★**★**证据分级固定用 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ★★

---

## §3 交卷前必跑 (★把命令与原样输出贴进 §B6★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ★1 板指纹 (前后双证)
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
# ★期望: md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 (★逐字节未动★)
# ★2 新闸 + 自测
python3 -B HW/check_preflight_regen_idempotent.py --selftest     # ★末行 ALL TESTS PASS · rc=0★
python3 -B HW/check_preflight_regen_idempotent.py                 # ★rc=0★
# ★3 既有闸不许被本单弄红
python3 -B HW/check_onepass_preflight_coverage.py                # ★rc=0★
python3 -B HW/check_workpack_state_values.py                      # ★rc=0 (★ISS-289 的闸, 读同一份页★)★
# ★4 必跑两项
python3 state/merge.py && python3 state/gate_check.py             # ★rc=0 且 Q1 = 18/18★
```

★**★**沙盒自测必须端到端跑真生成器 (★不许只测纯函数★) ⇒ ★**`--selftest` 里要有真跑一次 `python3 state/_iss277_build_preflight.py` 的沙盒用例 (★沙盒在项目盘 `tmp/iss349/`★) ★**

---

## §4 main 要你答的三问 (★答不出来 = 没干完★)

★**① 「重跑会蒸发 B33」你是怎么复现的? (★贴证据, 不许只讲道理★) ★**
★**⇒ 在沙盒副本上跑一次生成器 ⇒ 贴: 跑前页的 §2 表 id 集合 + §7 JSON id 集合 + md5 ⇒ 跑后同样三项 ⇒ 两组差集 (★`B33_PIN_LAND_1P27` 必须在跑后的差集里★) ⇒ 再贴【跑前的页 vs 跑后的页】的 diff 行数 (★应当是【B33 那几行消失】+ 其余零差异★) ★**

★**② 新闸的三条判据分别从盘面哪一段读? (★贴代码行号★) ★**
★**⇒ 贴出 `HW/check_preflight_regen_idempotent.py` 里三条判据各自的实现位置 (★文件:行号★) + 各自读的文件路径 + 各自的失败判定条件 ★**

★**③ 你的反向用例把 B33 弄没之后, 闸红了没有? 点的是哪一行? (★三条例外逐条答★) ★**
★**⇒ R1/R2/R3 各自的: 沙盒改了哪个文件的哪一行 ⇒ 闸的 rc ⇒ 闸输出里点名的内容 (★逐字贴★) ⇒ 恢复原件后再跑一次 ⇒ rc=0 ★**

---

## §5 纪律 (★本仓既有规矩, 不许新造★)

★**① 写分片必须用 `python3 state/frag_write.py --agent hw-lead` (★禁止 `open(p,"w")` 手写 YAML★) ★**
★**② 只写本单允许的文件, 不碰别人的 (★`pm.yaml` / `mech.yaml` / `sw.yaml` / `issue_log.yaml` / `gate_check.py` 全部不许写★) ★**
★**③ 交卷页 B0~B7 必须齐 (★少一节 = 门禁打回★) ⇒ 先把骨架落盘再填内容 (★半页比没页更糟★) ★**
★**④ 日志放 `logs/iss349/` (★**不许落 `/tmp`**★) ★**
★**⑤ 你交卷页里引用的每一个文件路径, 都要自己 `[ -e ]` 查一遍 ⇒ ★**页内 MISS 行数必须 = 0** (★最近三轮 (ISS-337 / ISS-340 / ISS-342) 全栽在这条上★) ★**
★**⑥ 不许替 main 签字 (★`status` 改 `verified` 是 main 的活★) ★**

★**★**本单性质: ★**纯脚本改造 + 文档(生成器)订正 + 新建机器闸 + 反向用例 · 零写板 · 零落表 · 零改既有闸判定逻辑 · 零外发 · 不代拍** ★
★**★**本单属于「板只改一次那一趟开工前必须做完」的**判据冻结类** ⇒ ★**做完之后, 板那一趟期间不许再改这一套 (★生成器 + 新闸 + 那一页★) ⇒ 板那一趟的读数才有效 ★**
