# ISS-296 · mech-lead 任务书 —— ★★【MECH 两道闸把【板 md5】写死成「硬保护基线」⇒ 板那一趟合法改板一次后 ⇒ 这两道闸必假红 ⇒ 而收工验收时的假红会被误读成「板改坏了」⇒ 板白改第二遍】★★ ⇒ ★**本单 = 把 SW 侧 ISS-284 已验证的「合法改板」机制 (reboard 四项原子记录 + 落表台账链头 + fail-closed 四条) 接到 MECH 侧两道闸 + 把 MECH 侧「收工后同一次重锚」写成收工清单强制项 + ≥4 条反向用例** ★ (★纯 MECH 侧 · 零写板 · 零落表 · 零改网表★)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 17:5x** ★ · ★**job**: cron `775d9893` (ARS45 继续执行后继计划)
> ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-296 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · MECH 侧 · 闸机制类 (★纯分析/闸类·不动板★)** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM 真源** ★
> ★**符合老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律** ★ (★本单只动 MECH 侧两道闸 + 一页 MECH 收工清单, 不动板、不动网表、不动落表台账★)

---

## ★⓪ 本单为什么现在派 (★main 17:4x~17:5x 本机实读盘面, 不抄任何交卷报告★)

★**mech-lead 名额刚空出来 (★ISS-294 已由 main 17:4x 独立复验落 `verified`★) ⇒ 而板那一趟是当前唯一主线 ⇒ ★**本单是【板那一趟】开工前 MECH 侧还差的那一件** ★

★**★一句话病灶: 「板只改一次」那一趟里, 板 md5 会【合法地变一次】⇒ ★**而 MECH 侧有两道闸把板 md5 写死成「硬保护基线」⇒ 那一趟改完板, 这两道闸【必假红】★ ⇒ ⇒ ★**而收工验收时的假红, 历史上【每一次】都被误读成「板改坏了」⇒ ⇒ 有人去「改板凑绿」⇒ ⇒ 板白改第二遍** ★

---

## ★① 病灶 (★main 17:4x~17:5x 本机实读, 逐条带行号★)

### ★①-1 · MECH 两道闸把板 md5 写死成基线 (★这本身没错, 错在【它没有合法的例外路径】★)

★| 位置 | 现状逐字 (★main 17:4x 实读★) | ★
|---|---|---|
| ★`MECH/check_board_frame_coords.py` **L79** ★ | ★`os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"): "611b869e13518c3c023fb178f91a0075",` ★ (★`PROTECTED` 字典, 共 2 件: 板 + `.kicad_pro`★) ★ | ★**基线写死 ⇒ 板一改 ⇒ C4 必红** ★ |
| ★`MECH/check_demo_struct_truth.py` **L81** ★ | ★`"HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",` ★ (★`MD5_EXPECTED` 共 6 件: 板 + `.kicad_pro` + 4 个 MECH 脚本★) ★ | ★**基线写死 ⇒ 板一改 ⇒ 必红** ★ |

★**★`MECH/check_board_frame_coords.py` L74~L78 自己写着为什么写死**: ★「★**受保护 2 件 (★真·不许变 ⇒ 基线写死★ · ISS-276 派单 §③ 基线) ⇒ 跑前跑后必须逐字节不变**★」 ★ ⇒ ★**这句话在【板不许变】的年代是对的 ⇒ 但板那一趟授权了【板合法改一次】⇒ ⇒ 这句话的前提没了, 缺口就出在这儿** ★

★**★同文件 L76~L80 还留着本项目【已解决过一次的同类病】的解法**: ★「★**ISS-286 · 2026-11-17** ★★ 原先这里是 5 件 (板 / `.kicad_pro` + 网表 / 脚表 / BOM 三件写死 md5) ★★⇒ 网表 / 脚表 / BOM 三件【移出】写死基线, 改走【落表台账链头】★★」 ★ ⇒ ★**★★★同一个病, 在同一个文件里, 只治了网表/脚表/BOM 三件, 板那两件【没治】⇒ 现在板要合法变了, 缺口暴露★★★ ★**

### ★①-2 · MECH 侧【完全没有】「合法改板」机制 (★main 17:4x 实跑 grep★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
grep -rn "reboard" MECH/*.py | wc -l      # ★★ 实测 = 0 ★★
```

★**★而 SW 侧【早就有了】(★ISS-284 · 已 verified·main 已独立复验过★): ★**

★| 位置 | 逐字 (★main 17:4x 实读★) | ★
|---|---|---|
| ★`SW/tools/check_demo_panel_spec.py` ★ | ★`def check_r6_hard_protected(root, anchors, led_text, led_spec)` ★ (★L522 起★) + ★判据四条 (★fail-closed 三条一条不许动★)★ | ★**判红/判绿的完整机器形状★** ★ |
| ★`SW/SW_MD5_BASELINE_LEDGER.md` §1 ★ | ★`hard_protected[].reboard` ★ 原子映射: ★**单号 `by` + 文件名 `file` + 改前 md5 `prev_md5` + 改后 md5 `md5` 四项捆一起** ★ | ★**合法改板 = 一次由单号背书的显式动作★** ★ |
| ★落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 ★ | ★`| 文件 | 前 | 后 | 变了? |` 表 ★ (★现链头 §16.2 的板那两行 = `变了? = 否` ⇒ 板还没合法改过★) ★ | ★**判决源 = 落表台账链头★** ★ |

★**★SW 侧四条判据 (★你必须照抄这四条, 一条都不许放宽★)★**:
1. ★**保护基线自证**: 锚点里的基线 md5 必须能在落表台账里与该文件【同行】查到 ⇒ ★**只改闸里的 md5 而台账没记 ⇒ 红** ★
2. ★**台账里该文件没有变更行** ⇒ 不许有 `reboard` 记录; 且 ★**盘上 md5 必须 == 基线** (★纯 md5 硬保护★) ★
3. ★**台账里有变更行** ⇒ ★**链头唯一 / 链不断 / 链头有单号** (★fail-closed 三条一条不许动★) + 锚点四项必须与台账链头逐字对上 + ★**保护基线必须留在链尾** + ★**盘上 md5 必须 == 台账链头** ★
4. ★**同组受保护件成对覆盖**: 一次合法改板必须覆盖同组全部件 (★板 + `.kicad_pro` 只来一条 ⇒ 红★) ★

### ★①-3 · 这一趟板会变哪些东西 (★⇒ MECH 侧要重锚的不止 md5★)

★**板那一趟 (★作业包 §3-S1~S13 的 A 类步★) 的板上改动清单 (★main 17:4x 本机实读作业包★)**: 位号 `_1` 后缀 **156 → 157** (★ISS-289 §B3.2 算过★) · `C_VBUS_GND` 下板 (★封装 **186 → 185**★) · `Q_PG` 3 根线重画 (★pad1→`PWR_GOOD` / pad2→`BAT_SW` / pad3→`PWR_ON`★) · D− 侧 ESD 三件 (★`R4`/`R9` 落表★) · S6 布局修正 (★20 个落位坐标·真实位移只有 `R_SEL_D3_P` 一处★) · S8 布线归零 (★unconnected **45 → 0**★) ⇒ ★**⇒ 板 md5 变一次 + 封装数变一次 + 位号后缀变一次 + 至少一处落位变一次 + 布线段数变 ⇒ MECH 侧凡【读板】的判据都要重锚** ★

★**★而 ISS-290 (结构侧交叉核对·已 verified) 与 ISS-294 (USB-C 边开口·已 verified) 刚把 MECH 侧的规格基线【刚抬高】(★三条开口 + 固定孔清空区 + 座体 `F.Fab` + 承区三口径★) ⇒ ★**这两页的几何, 也是那一趟【必须一起复验】的对象** ★

---

## ★② 根因一句话: 【MECH 侧的「板不许变」判决源 = 【写死的 md5】⇒ 它【没有合法的例外路径】⇒ 板一合法改, 它只能判红 ⇒ 而假红 = 假缺陷 ⇒ 于是有人去动板★】

★**⇒ 所以本单不能只是【把基线改个数】⇒ 那是「悄悄换真源」(★本项目 ISS-273/275 花大力气堵掉的洞★) ⇒ ★**必须照 SW 侧 ISS-284 的形状做成【一个由单号背书的显式动作】★**

---

## ★③ 要交的几件 (★每件都能独立验收★)

### ★B1 · MECH 侧两道闸接入「合法改板」机制 (★判据只许变严, 不许放松★)

★**要动的文件只有两个**: ★`MECH/check_board_frame_coords.py` ★ + ★`MECH/check_demo_struct_truth.py` ★ (★其余 MECH 脚本一个都不许动★)

★**★判据 (★照 §①-2 的 SW 四条, 一条都不许放宽★)★**:
- ★**① 保护基线自证**: MECH 侧那个写死的板 md5 基线, 必须能在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里与该文件【同行】查到 ⇒ ★**只改 MECH 闸里的 md5 而台账没记 ⇒ 判红** ★
- ★**② 台账里该文件没有变更行** ⇒ 不许有 `reboard` 记录; 且 ★**盘上 md5 必须 == 基线** (★纯 md5 硬保护, 与现在一样★) ★
- ★**③ 台账里有变更行** ⇒ ★**链头唯一 / 链不断 / 链头有单号** (★fail-closed 三条一条不许动★) + 四项与链头逐字对上 + ★**保护基线必须留在链尾** + ★**盘上 md5 必须 == 台账链头** ★
- ★**④ 同组成对覆盖**: 板 + `.kicad_pro` 一次合法改板必须成对 (★只来一条 ⇒ 判红★) ★

★**★★两条设计口径 (★main 已经替你想过了, 照办, 别自己另发明★)★**:
1. ★**MECH 侧【不要新造第二个可手改的 md5 字段】** ⇒ ★**判决源 = 落表台账链头** (★SW 侧之所以有 `SW_MD5_BASELINE_LEDGER.md` 那张锚点页, 是因为 SW 侧要锚【网表/脚表/链头判定源】那一整套; MECH 侧只要判【板/`.kicad_pro`】这一对 ⇒ ★**少一个可被挖的坑 = 更严★) ★ ⇒ ★**如果你认为必须留一张 MECH 锚点页, 你自己决定, 但【基线 md5 字段必须永远不许改】+ 【reboard 四项必须捆成一个原子映射】+ 【锚点与台账必须逐字对账】这三条一条都不许松, 且要在交卷单里写清为什么需要它★ ★
2. ★**MECH 侧的台账解析器, 必须与 SW 侧读出【逐字相同】的结果** ⇒ ★**这是「同源」的机器证明** ⇒ ★**做法照抄 ISS-288 的先例** (`logs/iss288/probe_netlist_reading.py` · ★比对老/新两版脚本算出的链头/链/产出单号 ⇒ `IDENTICAL: True`★) ⇒ ★**你交一个同类的探针脚本: 对同一份台账文本, MECH 侧解析器与 SW 侧解析器读出的【链头 / 链 / 产出单号】逐字相同 ⇒ 不相同 ⇒ 判红** ★ ★

### ★B2 · MECH 侧「收工后同一次重锚」清单 (★写成强制项★)

★**收工清单 = 板那一趟【改完板以后】必须同一次做完的那一组事** ⇒ ★**HW 侧那条已经在 ISS-292 的 B4 里写了 (★作业包 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 收工清单·「重锚」现在 grep = 0 处 ⇒ hw-lead 在补★) ⇒ ★**MECH 侧这条【还没人写】⇒ ★**你写在你自己的 MECH 页上 (★`MECH/BOARD_ONEPASS_MECH_SYNC.md` 追加式★), 并【登记 need 给 main】★ ⇒ ★**要不要把 MECH 那条抄进 HW 作业包 = main 的活 (★那是 HW 域★)** ★

★**MECH 侧要重锚的清单 (★你按实读盘面自己核全, 下面是 main 已核到的, 至少这些★)**:
1. ★**两道闸里【板 + `.kicad_pro`】那两个写死基线** ⇒ ★**走合法改板路径 (★B1★) ⇒ 而不是手改基线★** ★
2. ★**ISS-286 已经台账化的那三件 (网表/脚表/BOM) 的链头** ⇒ 板那一趟若再落表 ⇒ 链头要同一次前移 (★C4 读链头 ⇒ 自动跟上, 但你要【证明】它跟上了★) ★
3. ★**开口/座体/净距几何**: 三条开口 (★`PORT_OPEN_DEBUG` / `PORT_OPEN_UART` / `PORT_OPEN_USBC`★) 的 rect + 固定孔清空区 + `J_USB_C` 座体 `F.Fab` ⇒ ★**板那一趟板边/落位若变 ⇒ 这三条的几何要同一次复算★** ★
4. ★**S6 那 20 个落位坐标 (★`PCB_PART_POS` 串·真实位移只有 `R_SEL_D3_P` 一处★) ⇒ ★**板那一趟 S6 重出后 ⇒ MECH 侧的落位/禁入区/承区判定要同一次复算** ★ ★
5. ★**帧标 id 统一** (★`B160x100` vs `160x100-bench` vs `60x30-setA` / `F30A` ⇒ 指同一批帧, id 不统一 = 后期漂 ⇒ ★**这条 main 还没裁 (U-274-6) ⇒ 你只登记 need, 不许自己裁★) ★ ★

### ★B3 · 反向用例 (★≥4 条, 每条贴原样 rc + 期望红组 vs 实际红组★)

★| # | 构造 (★全部在【沙盒副本】上做, 真件一个字节不许碰★) | 期望 | ★
|---|---|---|---|
| ★① ★ | ★**把 MECH 闸里的板基线 md5 改掉 (★模拟「悄悄换真源」★) 而落表台账不动** ★ | ★**红** ★ | ★
| ★② ★ | ★**把沙盒里的盘上板 md5 改掉 (★模拟「手改板」★) 而落表台账没有变更行** ★ | ★**红** ★ (★纯 md5 硬保护不许被放松★) | ★
| ★③ ★ | ★**给台账补一条【变更行】(★改前→改后★) 但 MECH 侧没有对应的合法改板记录 / 四项不齐** ★ | ★**红** ★ | ★
| ★④ ★ | ★**只让板有变更行, `.kicad_pro` 没有** (★同组覆盖★)** ⇒ ★**红** ★ | ★**红** ★ | ★
| ★⑤ ★ | ★**链头不唯一 / 链断 / 链头缺单号** (★三条 fail-closed 各一条★)** ⇒ ★**红** ★ | ★**红** ★ | ★
| ★⑥ ★ | ★**正向对照: 一切如常 ⇒ rc=0** ★ | ★**绿** ★ (★证明闸不是恒红★) | ★

### ★B4 · 回归 (★别的闸一条不许红★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_board_frame_coords.py;            echo "rc=$?"   # 期望 rc=0
python3 MECH/check_board_frame_coords.py --selftest;  echo "rc=$?"   # 期望 rc=0 (★条数只许增不许减★)
python3 MECH/check_demo_struct_truth.py;              echo "rc=$?"   # 期望 rc=0
python3 MECH/check_demo_struct_truth.py --selftest;   echo "rc=$?"   # 期望 rc=0 (★条数只许增不许减★)
python3 MECH/check_onepass_mech_sync.py;              echo "rc=$?"   # 期望 rc=0 (ISS-294 那道·不许碰)
python3 MECH/check_onepass_mech_sync.py --selftest;   echo "rc=$?"   # 期望 rc=0
python3 MECH/check_onepass_struct_crosscheck.py;      echo "rc=$?"   # 期望 rc=0 (ISS-294 那道·不许碰)
python3 MECH/check_onepass_struct_crosscheck.py --selftest; echo "rc=$?"
python3 state/merge.py;                               echo "rc=$?"   # 期望 rc=0
python3 state/gate_check.py;                          echo "rc=$?"   # 期望 rc=0 (Q1 18/18)
python3 state/issue_check.py;                         echo "rc=$?"   # 期望 rc=0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★板 611b869e13518c3c023fb178f91a0075 / .kicad_pro 3e504d2be83152e337949723e909be1b
# ★★网表 37f62ac3f0b81d92ca7d48fdea717f07 / 脚表 a4270120454aedf7a23c92cd8985c8a6
# ★★BOM 5d02bece9477ffce5fbe0193c7d5cce4 必须逐字节不变 ★★
# ★★板 mtime 仍须是 2026-11-06 07:07:17 (★md5 + mtime 双重证明★) ★★
```

★**★一条不许踩的坑 (★ISS-289 交卷单自己发现的副作用★)★**: ★**`HW/check_onepass_preflight_coverage.py` 每次跑都会重生成 `HW/PCB/` 下 4 个辅助文件 ⇒ 判「有没有偷改板」必须看【官方板那两个文件的 md5 + mtime】, 不能看目录★★ ★**

---

## ★④ 交卷物 (★4 件★)

1. ★**交卷单** `HANDOFF/2026-11-17_mech-lead_ISS295_合法改板机制与收工重锚.md` (★B1~B4 四块齐全 + 反向用例原样 rc + 同源探针的 `IDENTICAL: True` 读数★) ★
2. ★**改动的两道闸** `MECH/check_board_frame_coords.py` + `MECH/check_demo_struct_truth.py` (★合法改板路径 + fail-closed 四条 + 反向用例★) ★
3. ★**MECH 侧收工清单** (★写进 `MECH/BOARD_ONEPASS_MECH_SYNC.md` 追加式 ⇒ ★**老字一字不许删**★) + ★**同源探针脚本** (★MECH 解析器 vs SW 解析器读数逐字相同★) ★
4. ★**分片** `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写 ⇒ ★**写完 `grep` 校验 `iss295` 在不在★**) ★
   ★**★另外顺手做一件小事 (★只有你能做, main 不越界写你的分片★)★**: ★**把你在 `needs_from` 里登记的 need `iss282_mech_sync_m5_baseline_after_landing` 的状态标成【已被本单覆盖 / 已转出】(★它的内容 = MECH 侧收工后基线重锚 ⇒ ★**本单 B1+B2 就是干这个的★)⇒ ★**并把 ISS-294 留给 main 的那条 `iss294_usbc_edge_opening_size_and_z_window` 的状态写清 (★它是【结构开口最终尺寸】= main→boss 拍板项 ⇒ ★**不许你自己定尺寸★)★ ⇒ ★**别自作主张把 need 关了, 在分片里写清依据就行★ ★**

---

## ★⑤ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) ★ · ★**★不许写落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★那一行留给「出板那一趟」的 main 落★)★** · ★**不许改 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/SCHEMATIC_LANDING_V1_LANDED.md` / `state/gen_netlist.py` / `state/land_v_values.py`** ★ · ★**不许改 `SW/tools/check_demo_panel_spec.py` 的 R6 逻辑** (★那是 ISS-284 的定版闸·MECH 侧只【读它的形状】+ 【在自己的探针里读它的解析器】·不许改它★) ★ · ★**不许改 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md`** (★那是 ISS-290 的交卷物★) · ★**不许改 `MECH/check_onepass_mech_sync.py` / `MECH/check_onepass_struct_crosscheck.py`** (★那是 ISS-294 的交卷物·本单只跑它们做回归·不许改★) ★ · ★**不许改 `MECH/check_board_frame_coords.py` 的 C1/C2/C3 语义与 `MECH/check_demo_struct_truth.py` 的 G5b/C21/C22 语义** (★本单只碰【板/`.kicad_pro` 基线】这一段★) ★ · ★**不许改任何阈值** (★CRIT 0.60 / cavity_req 4.50 / cav_v 38.00 / duct_v 6.00 一个都不许动★) ★ · ★**不许碰 `HW/` 与 `SW/` 的文件与分片** ★ · ★**零外发** ★ · ★**不替老板拍板** (★结构开口尺寸 / 帧标 id 统一 / 落表批次 = 建议交 main★) · ★**不自签 issue_log** (★签字是 main 的活★) · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

★**★本单零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**不许发任何邮件/询价/问询/采购 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★ ★**

★**★★一条最容易踩的错 (★main 提前说破★)★**: ★**「让闸变绿」有两种做法, 只有一种是对的**: ★**(A) 改判据 / 改基线数字 ⇒ 错** (★那是「悄悄换真源」★) ★**(B) 把【合法的那次改板】做成【有单号背书、有台账可查、fail-closed】的一个显式动作 ⇒ 对** ★ ⇒ ★**本单只许做 B ⇒ 任何时候你发现自己在改「期望值」而不是在改「取值来源」, 就是走错了★ ★**

---

## ★⑥ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss295/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~60 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★

★**★这项目的老坑, 一条都不许再踩★**:
1. ★**写分片必须用 `state/frag_write.py` 原子写 (★禁止 `open(p,"w")`★)** ★
2. ★**只写本任务允许的文件, 不碰别人的** (★`state/fragments/hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节都不许碰★) ★
3. ★**文档订正必须追加式 (★老字不许删★)** ⇒ ★**改数必须留痕 (★谁改的 / 哪个单号 / 新旧值 / 依据★)★ ★
4. ★**不许为了让闸绿而改闸 / 放宽判据** ★
5. ★**不许自签 issue_log** ★
6. ★**沙盒副本上做反向用例, 真件一个字节不许碰** ★

★**★为什么这一单必须在「板只改一次」那一趟【之前】做完★**: ★**那一趟一开工, 板 md5 就变了 ⇒ MECH 两道闸当场红 ⇒ ⇒ 而假红在收工验收时会被读成「板改坏了」⇒ ⇒ 有人会去「改板凑绿」⇒ ⇒ ★**最坏 = 把 `C_VBUS_GND` 装回板上 (ISS-289 交卷单自己点名的 2-4 周 + ¥4-8K)** ★ ⇒ ⇒ ★**所以这条机制必须赶在开工前落地, 而且它【本身不碰板】** ★


---

## ★★⑮ 追加 (★2026-11-17 17:6x · 本单【已开·本轮未派】★)

★**★兄弟 job fb67af40 在 17:5x 并发开了 ISS-295 (★scope = 「结构侧输入一次性收口 + 过期结论防漂闸」· brief = `state/dispatch_briefs/ISS-295_mech_claims_and_verdict_freshness.md`★) ⇒ ★**它已先落 `fixing` 再 spawn ⇒ ★**ISS-295 归它所有 ⇒ 本单改号 = ISS-296** ★

★**★本轮 (17:6x) 【不派】**: ★**mech-lead 名额被 ISS-295 占着 ⇒ 一个 agent 同时只能有一个写会话 ⇒ ★**⇒ **状态留 `open`** (★**不许先落 fixing 再不派** ⇒ 那会造出【僵尸 fixing】⇒ 永久占住 mech-lead 名额★) ⇒ ★**等 mech-lead 名额空出来, 由 `state/advance.py` / 队列 job 正常派出** ★

★**★你被派出时的第一条命令**: ★**先 `cat state/dispatch_briefs/ISS-296_mech_legal_reboard_mechanism.md` 全文** ★ (★本文件就是你的任务书全文★) ⇒ ★**再 `cat state/dispatch_briefs/ISS-295_mech_claims_and_verdict_freshness.md` 看 ISS-295 已经往 `MECH/BOARD_ONEPASS_MECH_SYNC.md` 追加了什么 (★你本单也要往那一页追加 ⇒ ★**追加式·老字一字不许删·ISS-295 的内容必须原样保留★)** ★



---

## ★★⑭ 追加 (★2026-11-17 18:4x main 实扫全仓·★你的活是【全仓 9 道闸】里的一格★)★★

★**★全仓清单 (★机器生成, 可复核★)★**: ★**`state/board_md5_pinned_gates.md`** ★ (★生成脚本 `state/_gen_board_md5_pinned_gates.py` · 机器可读 JSON `state/board_md5_pinned_gates.json`★)
⇒ ★**全仓共 9 道闸硬钉板 md5 `611b869e…`**: ★**HW 6 道** (`check_fsin_rootcause` · `check_g1a7_selection_landed` · `check_onepass_commit_order` · `check_onepass_preflight_coverage` · `check_pin_function_labels` · `check_workpack_state_values`) + ★**MECH 2 道** (★你这一单★) + ★**SW 1 道** (`SW/tools/check_onepass_sw_sync.py`) ⇒ ★**HW 侧 = ISS-297 (hw-lead) · SW 侧 = ISS-298 (sw-lead)·★**
⇒ ★**★口径已被证明可行 (★不是猜的★)**: `SW/tools/check_demo_panel_spec.py` 在 ISS-284 转成台账口径后**已不再硬钉板 md5** ⇒ ★**全仓清单里根本找不到它** ⇒ ★**⇒ 「不硬钉」不是靠删断言, 是靠判决源换成【落表台账 + 合法改板记录】** ★
⇒ ★**★建议 (★main 18:4x 实跑得出的★)**: 你的【收工清单强制项】那一段, ★**把「收工后同一次重锚」的对象从【MECH 两道闸】扩成【全仓 9 道闸】** ★ ⇒ ★**否则 HW/SW 侧的闸在收工那天照样红, 一半收工清单等于没写** ★
### ★★main 对 E-1 / E-2 的裁决 (★2026-11-17 18:4x·★这两条归 main, 不归老板★)★★

| # | 事实 | ★**裁决** ★ |
|---|---|---|
| ★**E-1** ★ | ★**BOM/网表写「1.27mm 排针」, 板上 land 实测 0.50mm pitch (Δ0.77) ⇒ 实物排针落不进** ★ · ★**BOM 那两行的备注自己写着「型号/间距/引脚编号【待结构与装配复核】」(★证据等级 [推算]★)** ★ | ★**★按 1.27mm 排针定 ⇒ 板 land 要改成 1.27mm ⇒ 并进「板只改一次」那一趟同一次做★** ★ ⇒ ★**理由**: ① `J_DEBUG` 是 JTAG 调试口 / `J_UART` 是 UART 口 ⇒ ★**0.5mm 单排不是常规可手插排针, 探针与杜邦线都插不上 ⇒ 「改料号到 0.5mm」这条路等于把调试口做成摆设 ⇒ 否决** ★ ② BOM 备注已写「待结构与装配复核」⇒ ★**本次复核的结论就是「1.27mm 成立, 所以 land 画错了」** ★ ③ ★**改 land 会动那 6 个焊盘 ⇒ 它们的走线本来就要在那一趟重布 ⇒ 与「unconnected 45→0」同一次做完, 不额外增加板改次数** ★ ⇒ ★**另: 改完必须用 `MECH/check_onepass_struct_crosscheck.py` (N2/N3/N4 净距核对) 复验一遍, 不许压 SoM 座** ★ |
| ★**E-2** ★ | ★**`HW/PCB/demo_mainboard_params.json` 的 `corner_radius_mm: 3.0` 是【死参数】: 板框实测 R=0.00, 且 `state/gen_pcb_netlist_board.py` 的 `add_outline()` 根本不读它** ★ | ★**★按【口径改板读 · 零板改】落: 把 params 里那个值改成与板框实测一致 (R=0.00) 或直接删掉这个死参数 + 在页里注明「板框无圆角」★** ⇒ ★**3.0 圆角【不】并进那一趟** ★ ⇒ ★**理由: 圆角对功能零影响, 而那一趟已经装了 5+ 项板改 (Q_PG 三根线 / D_ESD_USB_D 2→3 脚 + 挪位 / 位号 _1 后缀 / C_VBUS_GND 下板 / R4·R9 落表 / E-1 排针 land) ⇒ 再加一项只增风险; 哪天要圆角, 单独一次小改** ★ ⇒ ★**★但死参数必须清掉 (留着 = 下一个人会以为板框有 3.0 圆角)★★** ★ |

⇒ ★**两条合计: 板那一趟的板改清单再 +1 项 (E-1 的排针 land 重画), 但仍只改一次板; E-2 零板改 ⇒ 只清参数** ★

