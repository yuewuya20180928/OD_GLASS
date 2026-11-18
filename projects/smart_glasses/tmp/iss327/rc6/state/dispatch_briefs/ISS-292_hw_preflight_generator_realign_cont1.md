# ISS-292 · hw-lead 任务书 (cont1 续做) —— ★★【清单页生成器与盘面页对齐 · ★从上一趟的半成品继续·不要从零重做★】★★

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 16:3x** ★ · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-292 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · PCB 线 · 纯生成器对齐 + 作业包指针订正类** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM 真源** ★
> ★**符合老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律** ★ (★本单只动生成器 + 两份文档, 不动板★)

---

## ★⓪ 上一趟到底发生了什么 (★main 16:2x 本机实查会话 + 盘面, 不抄任何交卷报告★)

★**子会话 `agent:hw-lead:subagent:71c9e8bb` (sessionId 54b83bdf-4400-42e8-85b2-9a28026b5a72) 15:52:21 → 16:08:07 (runtime 944s · status=timeout · abortedLastRun=true)** ⇒ ★**死在超时, 不是活干完** ⇒ ★**transcript 末条 = 工具结果缺失的合成报错 + 空 assistant 消息** ★

★**⇒ 交卷单只剩骨架**: `HANDOFF/2026-11-17_hw-lead_ISS292_清单页生成器对齐.md` = **1341 B** · B0~B6 七块**全是 `★(施工中★)`** · ★**六块一个都没填** ★

★**★但是! 生成器那一大块活【已经真落在盘上了】★★ ⇒ ⇒ ★★**本趟是【续做】, 不是【重做】★★** ⇒ ★**下面「已落盘 / 别重做」那几条, 一条都不许推倒重来** ★

---

## ★① 已落盘 (★★别重做★ · main 16:2x 本机实测逐条核过★)

| # | 已完成的东西 | ★main 实测证据 (★本机跑, 不是抄报告★) ★ |
|---|---|---|
| ★1 ★ | ★**生成器 `state/_iss277_build_preflight.py` 已改写** ★ | ★md5 `0767fcc5471249d1f533e2e45394d96d` → **`f80a094fc1d8e497295bb543a06ee109`** (★mtime 16:04:45★) · ★**25077 B → 41748 B** ★ |
| ★2 ★ | ★**R3-A4 三个数改成【从真源读】** ★ | ★生成器 L56~L63 = `subprocess` 跑 `HW/check_netlist_contradiction_r3.py` + 正则取 `MAIN_PCB且DNP (\d+) 颗 · 在板上 (\d+) 颗 · 零标记 (\d+) 颗` ★ ★**读不到 ⇒ `raise SystemExit` 拒写页 (fail-closed)** ★ |
| ★3 ★ | ★**脚表缺陷条数改成【从真源读】** ★ | ★生成器 L69~L93 = 跑 `HW/check_pin_function_labels.py` + 正则取 `总数 / 功能缺陷 / 串号 / 缺脚` + ★**读不到 ⇒ 同样 fail-closed** ★ |
| ★4 ★ | ★**补了 `B32_V2_NET_RENAME` 条目** ★ | ★生成器 L273 = `("B32_V2_NET_RENAME", "ISS-283", ...)` ★ (★原任务书 B1-3 那条【缺项】已补上★) ★ |
| ★5 ★ | ★**条目 id `B17_DNP_43` 没改名** (★只订正值★) ★ | ★生成器 L321 仍是 `("B17_DNP_43", "ISS-269", ...)` ★ ★**符合要求** ★ |
| ★6 ★ | ★**新增追加式 sidecar `state/_iss277_preflight_appendix.md`** (★27293 B · 16:02★) ★ | ★承载 `ISS292:S3_APPENDIX` (★ISS-283 落表的 §③-1~§③-3 三条板侧同步项★) + `ISS292:ISS289_APPENDIX` (★ISS-289 现状值对回盘面 · 含 state_baseline 登记表★) ★ ★**sidecar 缺 ⇒ 拒写页 (fail-closed) · 块读不到 ⇒ 拒写页** ★ |
| ★7 ★ | ★**★重跑幂等 (原任务书 B2 的核心硬判据) —— 已达成, main 独立复验过★★** ★ | ★见下面 §② 的沙盒复现法 ★ |

### ★② ★★main 16:2x 沙盒实测: 重跑输出与真页【逐字节相同】★★ (★这是 B2 的硬判据, 已过★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
mkdir -p tmp/iss292_sbx
sed 's#^OUT = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")#OUT = os.path.join(PROJ, "tmp", "iss292_sbx", "gen_out.md")#' \
    state/_iss277_build_preflight.py > tmp/iss292_sbx/gen.py
python3 tmp/iss292_sbx/gen.py          # ★rc=0 · 沙盒跑, 不碰真页★
md5sum tmp/iss292_sbx/gen_out.md HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
diff tmp/iss292_sbx/gen_out.md HW/PCB/BOARD_ONEPASS_PREFLIGHT.md   # ★rc=0 ⇒ 零行差异★
```
★**main 实跑结果 (★原样★)**:
- ★生成器 rc=0 · 读数 `R3_T/R3_O/R3_Z = 51 / 40 / 40` · `P_T/P_F/P_W/P_M/P_MD5 = 18 / 15 / 14 / 1 / 3` · **32 条** · 步分布 S1~S13 全覆盖 ★
- ★**沙盒输出 md5 = `159bf20fe71c36e48292f39dafc46a35`** ★
- ★**真页 md5 = `159bf20fe71c36e48292f39dafc46a35`** ★
- ★**diff rc=0 (零行差异) ⇒ ★★重跑后页【零回退】★★ ⇒ ★★B2 已达成** ★

★**⇒ 所以本趟【不要】再去改生成器的取数逻辑 (★那部分已经对了★) ⇒ ★★你这一趟的活 = 把【还没做的 7 件】一次做完 + 把交卷单 B0~B6 填满★ ★★**

---

## ★③ ★★还没做的 7 件 (★这才是本趟的全部活★) ★

| # | 待做 | ★main 16:2x 实测的缺口 (★不是推测, 是盘面读数★) ★ |
|---|---|---|
| ★**B3** ★ | ★**作业包 §3-S1 位号真源指针改对** ★ | ★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` **L146 + L774** 仍写「器件位号真源 = `HW/SCHEMATIC_V1_SPEC.json` (★`devices` 段的 186 个 `ref`★)」⇒ ★**main 实测: 该 JSON 顶层只有 meta / counts / connections / power_rails / display_select / testpoints / undrawable 七个键, 【没有 `devices`】** ⇒ ★**照字面实现找不到真源** ⇒ ★**真源 = `HW/netlist_v1_pins.csv` (★218 器件★)** ⇒ ★**按追加式订正 (★老字一字不许删★) + 把「为什么原指针失效」写进订正句** ★ |
| ★**B4** ★ | ★**「收工后同一次重锚」写成收工清单强制项** ★ | ★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 里 grep「重锚」= **0 处** ⇒ ★**这条强制项完全没写进去** ⇒ ★**要写全**: ① 强制项原句 (★「收工后同一次重锚两份文档的 `state_baseline` 写死期望值 + 新闸 `HW/check_workpack_state_values.py` 跑绿」★) ② ★**最危险三条的重锚值写全**: `W11`/`C04` (封装 186 ⇒ 185) · `W09_SAME_PAD_NET` (同号异网 3 ⇒ 0) · `W12`/`C03` + `W18` (156 / 1 ⇒ 156 或 157) ③ ★**一句警告: 「★不许为了让闸绿而把 `C_VBUS_GND` 装回板上 ⇒ 那会直接毁掉 §3-S2 的『C1 多余 0』★」** ★ |
| ★**B5** ★ | ★**反向用例 ≥3 条 (★每条贴原样 rc★)** ★ | ★`logs/iss292/` 里**只有** `baseline_before.txt` (★1312 B·15:53★) ⇒ ★**反向用例一条都没跑** ★ ⇒ ★按原任务书 §B5 的 ①②③ 三条构造 (★① 沙盒里模拟又一次合法落表 ⇒ 数值必须跟着变 ② 把 R3-A4 改回 54/43/43 ⇒ 必须变红 ③ 正向对照: 一切如常 ⇒ 零变化 + 闸绿★) ★ |
| ★**B6** ★ | ★**回归 (★别的闸一条不许红★)** ★ | ★本趟一条都没跑过 (★上一趟死在半路★) ⇒ ★按原任务书 §B6 那 8 条命令跑 (★`check_workpack_state_values.py` + `--selftest` · `check_onepass_preflight_coverage.py` + `--selftest` · `check_board_frame_caliber.py` · `state/merge.py` · `state/gate_check.py` (★Q1 18/18★) · `state/issue_check.py` + md5 五件★) ★ |
| ★**⑬** ★ | ★**ISS-290 的 E-1~E-6 六条并进清单页** ★ | ★`grep -c "E-1" HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` = **0** ⇒ ★**六条一条都没并进去** ★ ⇒ ★**任务书「⑬ 追加」节已把 E-1~E-6 全文转给你了** (★`state/issue_log.yaml` 里 ISS-292 的 `task_brief` 尾部★) ⇒ ★**E-1/E-2/E-6 是老板级 ⇒ 本单只【登记条目 + 给选项与代价】, 不代拍** ★ ★**生成器不许写死这六条 ⇒ 要从真源读 (★`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §5 那张 E-1~E-6 表是它们的出处★) ⇒ 读不到 ⇒ fail-closed 报错, 不许猜** ★ |
| ★**R** ★ | ★**沙盒 README** ★ | ★`tmp/iss292/README.md` **不存在** ⇒ ★**要写**: 「生成器输入 / 输出 / 真源」三件套 (★输入 = `state/_iss277_preflight_appendix.md` sidecar + 两个真源脚本; 输出 = `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`; 真源 = `HW/check_netlist_contradiction_r3.py` + `HW/check_pin_function_labels.py` + `HW/SCHEMATIC_LANDING_V1_LANDED.md`★) ★ ⇒ ★**下一个人才知道怎么维护** ★ |
| ★**F** ★ | ★**交卷单 B0~B6 填满 + 分片** ★ | ★交卷单 = **1341 B 骨架** (★B0~B6 全「施工中」★) ⇒ ★**六块全部要填, B0 贴受保护 5 件 md5/mtime, B3 贴重跑幂等的前后 md5 逐字, B5 贴反向用例原样 rc, B6 贴 8 条回归 rc★** ★ ⇒ ★**分片**: `state/fragments/hw.yaml` 里 ★**`grep -c iss292` = 0** ★ ⇒ ★**一条都没写** ⇒ ★**走 `python3 state/frag_write.py --agent hw-lead` 原子写 (★禁止 `open(p,"w")`★) ⇒ 写完 `grep` 校验** ★ |

★**★一句话: 生成器那半已经做完了 (别动它) ⇒ 你这趟 = 补上面 7 件 + 填交卷单 + 写分片。★★ ★**

---

## ★④ 硬判据 (★main 会照这几条复验★)

★**B2-续 · 重跑幂等仍然必须成立 (★你加了 E-1~E-6 之后【页会变】⇒ 但【再跑一次必须零变化】★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum HW/PCB/BOARD_ONEPASS_PREFLIGHT.md HW/PCB/BOARD_ONEPASS_WORKPACKET.md   # 跑前
python3 state/_iss277_build_preflight.py                                        # ★重跑生成器★
md5sum HW/PCB/BOARD_ONEPASS_PREFLIGHT.md HW/PCB/BOARD_ONEPASS_WORKPACKET.md   # 跑后
# ★★跑后两个 md5 必须与跑前逐字节相同 (★零回退·页零变化★) ★★
```
★**★绝不许**: 页里的 51/40/40 变回 54/43/43 · 18 条变回 15 条 · **ISS-283 / ISS-289 的九处追加式订正 anchor 少任何一处** ★

★**B6 · 回归 (★原样贴 rc 进交卷单★)**:
```bash
python3 HW/check_workpack_state_values.py;          echo "rc=$?"   # 期望 rc=0
python3 HW/check_workpack_state_values.py --selftest; echo "rc=$?"  # 期望 rc=0 (★条数只许增不许减★)
python3 HW/check_onepass_preflight_coverage.py;      echo "rc=$?"   # 期望 rc=0
python3 HW/check_onepass_preflight_coverage.py --selftest; echo "rc=$?"
python3 HW/check_board_frame_caliber.py;             echo "rc=$?"   # 期望 rc=0
python3 state/merge.py;                              echo "rc=$?"   # 期望 rc=0
python3 state/gate_check.py;                         echo "rc=$?"   # 期望 rc=0 (Q1 18/18)
python3 state/issue_check.py;                        echo "rc=$?"   # 期望 rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e13518c3c023fb178f91a0075 / .kicad_pro 3e504d2be83152e337949723e909be1b
# ★★网表 37f62ac3f0b81d92ca7d48fdea717f07 / 脚表 a4270120454aedf7a23c92cd8985c8a6
# ★★BOM 5d02bece9477ffce5fbe0193c7d5cce4 必须逐字节不变 ★★
# ★★板 mtime 仍须是 2026-11-06 07:07:17 (★md5 + mtime 双重证明★) ★★
```

★**★一条不许踩的坑 (★ISS-289 交卷单自己发现的副作用★)★**: ★**`HW/check_onepass_preflight_coverage.py` 每次跑都会重生成 `HW/PCB/` 下 4 个辅助文件 (`_frame_reference.kicad_pcb` / `STACKUP.md` / `GEN_SELF_CHECK.txt` / `LAYOUT_RULES.md`) ⇒ 它们的 mtime 会变 (内容逐字相同) ⇒ ★★判「有没有偷改板」必须看【官方板那两个文件的 md5 + mtime】, 不能看目录★★ ★**

★**★第二条不许踩的坑 (★本单新加的·E-1~E-6 会改页★)★**: ★**你把 E-1~E-6 并进清单页之后, 新闸 `HW/check_workpack_state_values.py` 的探针/条目数可能对不上 (★它按 ISS-289 那批 29 条登记 + 七类判据钉的★) ⇒ ⇒ ★**★不许为了让闸绿而改闸 (`HW/check_workpack_state_values.py` 是 ISS-289 的闸, 本单【不许碰】) ⇒ 也不许放宽判据 ⇒ 而是把「哪条探针被 E-1~E-6 顶到了」原样写进交卷单 B5 + 登记 need 给 main 裁决**★ ★**

---

## ★⑤ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `state/gen_netlist.py` / `state/land_v_values.py`** ★ · ★**不许改 `HW/check_workpack_state_values.py` (★那是 ISS-289 的闸★)** ★ · ★**不许改 `state/_iss277_build_preflight.py` 的取数逻辑 (★那部分已经对了·见 §①-2/§①-3★)** ★ ★**只许改它允许的地方 = 加 E-1~E-6 那一条的读入 (★不许写死六条·从真源读★)** ★ · ★**不许碰 `SW/` 与 `MECH/` 的文件与分片** (★`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 只许读, 不许改★) ★ · ★**零外发** ★ · ★**不替老板拍板** (★E-1 排针 pitch / E-2 corner_radius / E-6 开口尺寸 = 老板/PM 域★ ⇒ 本单只交选项与代价★) · ★**不自签 issue_log** (★签字是 main 的活★)

★**★本单零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**不许发任何邮件/询价/问询/采购 ⇒ 缺口一律【自己网上查】+ 标证据等级 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★ ★**

---

## ★⑥ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss292/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★

★**★这项目的老坑, 一条都不许再踩★**:
1. ★**同一条 issue 的续做单, 必须从盘上继续, 不许从零重做** (★上一趟的生成器成果已在盘·§① 就是给你的交接单★) ★
2. ★**不许在交卷单里写「施工中」就当交卷** (★上一趟就是这么死的·B0~B6 七块全空★) ★
3. ★**不许用 `open(p,"w")` 写分片** (★走 `state/frag_write.py` 原子写★) ★
4. ★**不许自己签 issue_log** ★
5. ★**不许为了让闸绿而改闸 / 放宽判据** ★

★**★为什么这一单必须赶在「板只改一次」那一趟之前★**: ★**那一趟一开工, 生成器就可能被再跑一次 ⇒ 页回退 ⇒ 新闸红 ⇒ ⇒ 而那时红会被误读成「板改坏了」⇒ ⇒ 有人会去改板凑绿 ⇒ ★**最坏 = 把 `C_VBUS_GND` 装回板上 = 2-4 周 + ¥4-8K 返工**★ ⇒ ⇒ ★**生成器对齐 + E-1~E-6 并页 + 收工重锚清单, 必须在开工前落地** ★

★**★E-1~E-6 为什么必须现在并进去 (★ISS-290 mech-lead 16:0x 交卷, main 已复验落 verified★)★**: ★**E-1 排针 pitch 1.27 vs 板读 0.50 (Δ0.77) ⇒ 实物排针落不进** ★ · ★**E-2 `corner_radius` 板读 0.00 / params 写 3.0 且生成器根本不读它 ⇒ 贴角 keep-out 是摆设** ★ · ★**这两条是【真·会改板】的, 必须排在「板只改一次」那一趟之前定, 不许拖到投板后** ★
