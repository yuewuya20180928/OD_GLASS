# ISS-294 · mech-lead 任务书 —— ★★【`J_USB_C` 缺一条结构边开口规格 (★座体贴板边 ⇒ 插头从板边进出, 但 MECH 规格里【没有】这条开口★)】★★

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 16:5x** ★ · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-294 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · MECH 侧规格补缺 + 机器闸类** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM** ★
> ★**符合老板 2026-11-17 00:43「PCB 类先派【纯分析 / 作业包】类」纪律** ★ (★本单只动 MECH 侧规格页 + MECH 闸, 不动板★)

---

## ★⓪ 本单为什么现在派 (★main 16:3x 本机实查盘面, 不抄任何交卷报告★)

★**ISS-290 (mech-lead · 结构侧交叉核对) 已由 main 16:0x 独立复验落 verified ⇒ mech-lead 名额空出来** ★

★**★但 ISS-290 自己在 §5 留了一条【它做不了、也没做的】缺口 ★★** ⇒ ★**它 §5.6 的 E-1~E-6 六条已由 main 转给 hw-lead 的 ISS-292 (任务书「⑬ 追加」节) ⇒ ★**唯独 E-6 的【MECH 侧规格本体】没人接** ★ ⇒ ★**本单就是接 E-6 的 MECH 那一半** ★

★**★E-6 在 ISS-290 交卷单 §5 的逐字原文 (★main 16:0x 已复验·你接着往下做★)★**:
> ★**E-6 · `J_USB_C` 缺一条结构边开口规格 (★缺口, 不改板★)** ★
> ★| 现状 `[实测]` | ★**`J_USB_C` 座体 `F.Fab` = X 135.680..144.320 × Y 0.000..6.400, ★Y 下沿 = 0.000 = 板边 ⇒ 插头从板边进出; 现有 MECH 规格 (检修口 / 调试口两条开口) 里【没有】这条边开口** ★ |
> ★| 改法 | ★**补一条结构边开口规格 (开口 X 135.680..144.320 @ 板边 Y = 0; 必须清空区 = 座体外形 + 固定孔位置) ⇒ 并进 §2 保留区与闸 (N3 加第三条开口) —— ★本单只登记, 结构开口尺寸的拍板归 main→boss** ★ |

★**⇒ 也就是说: `J_USB_C` 已在 ISS-290 的结构侧交叉核对表里被登记为 `USB-C-BODY` 禁入区 (X 135.680..144.320 × Y 0.000..6.400), ★**但 MECH 的【规格页 + 机器闸】里还只有两条开口 (检修口 / 调试口), 第三条边开口【完全不存在】** ★**

---

## ★① 病灶 (★main 16:3x 本机实读盘面, 逐条带行号 / 行名★)

### ★①-1 · MECH 规格页的机器块里只有【两条】开口

★**`MECH/BOARD_ONEPASS_MECH_SYNC.md` §5 机器块 (★main 16:3x 本机 json 解析实读★)**:
```
顶层键: issue / agent / updated / frame_default / frames_allowed / consts / openings / merged_opening / led / connectors / items
openings: list len=2 → ['PORT_OPEN_DEBUG', 'PORT_OPEN_UART']
items  : list len=9 → ['MECH-PORT-DEBUG','MECH-PORT-UART','MECH-PORT-NOMERGE','MECH-BODY-H','MECH-LED-G','MECH-LED-GD-NET']
```
★**⇒ 两条开口 + 一条合并禁令 (`merged_opening`) + 9 个 item ⇒ ★**没有任何一条是 `J_USB_C` 的板边开口** ★

### ★①-2 · 两道 MECH 闸都把「恰好两条」写死了 ⇒ 第三条开口加不进去

| 位置 | 现状逐字 |
|---|---|
| ★`MECH/check_onepass_mech_sync.py` L191~L193 ★ | ★`if len(openings) != 2: errs.append(f"M2 开口必须【两条】(检修口 / 调试口), 机器块里只有 {len(openings)} 条 ⇒ 不许合并")` ★ |
| ★`MECH/check_onepass_struct_crosscheck.py` L544~L548 ★ | ★`if len(openings) != 2: errs.append(f"N3 机器块开口条数 = {len(openings)} (期望恰好 2 条: 检修口 + 调试口; 合并成一条 ⇒ 红)")` ★ + ★`if sorted(ids) != ["PORT_OPEN_DEBUG", "PORT_OPEN_UART"]: errs.append(...)` ★ |

★**★★注意这两条断言的【本意】: 「不许把检修口/调试口【合并】成一条」⇒ ★**所以你加第三条时, 必须【保留】合并禁令这条防线 (★不许把 `!= 2` 改成 `!= 3` 就完事★ ⇒ ★**那是把「恰好两条」从「两条不许合并」偷换成「三条不许合并」★ ⇒ ★**合并成【一条】照样能过 ⇒ 防线反而松了**)★ ★**

★**★正确改法 (★本单最关键的一条纪律★)★**: ★**把断言从【条数】改成【集合 + 两两不相同】** ⇒ ★**即: 期望 id 集合 = {PORT_OPEN_DEBUG, PORT_OPEN_UART, ★★PORT_OPEN_USBC★★} (★恰好三条, 一条不少一条不多★) + ★**任意两条的矩形不许完全相同 (★合并成一条 ⇒ 红★) + ★**三条必须【分别】验, 不许合并验** ★ ⇒ ★**这样「合并」这条防线不但没松, 还多了一条「不许把 USB-C 开口并进检修口/调试口」★**

### ★①-3 · 板面实测 (★main 16:3x 本机用 `state/pcbnew_py.sh` 读板★)

★**★`J_USB_C` 座体 `F.Fab` = X 135.680..144.320 × Y 0.000..6.400 (★8.64 × 6.40· 座体高 3.50★) ⇒ ★**Y 下沿 = 0.000 = 板边 ⇒ 插头从板边进出** ★**

★**板读焊盘 (★main 16:3x 实读★)**:
```
J_USB_C pads=18  pos=(140.0, 5.25)
  两个 Ø0.65 固定孔 (NPTH): (134.22, 2.625) 与 (145.78, 2.625)   ★★⇒ X 间距 = 11.56, 中心 140.00 ★★
  16 个信号焊盘: A1(136.25,5.25) A4(137.25,5.25) A5(138.75,5.25) A6(139.75,5.25) A7(140.25,5.25) A8(141.25,5.25)
                 A9(142.75,5.25) A12(143.75,5.25) B1(143.25,5.25) B4(142.25,5.25) B5(141.75,5.25) B6(140.75,5.25)
                 B7(139.25,5.25) B8(138.25,5.25) B9(137.75,5.25) B12(136.75,5.25)
  ★★全部信号焊盘 Y 中心 = 5.25, 焊盘尺寸 0.30 × 1.15 ⇒ 铜箔 Y 向 2.3000..5.8250 (来自 ISS-290 §4 实测)★★
```
★**★⇒ 固定孔 (Ø0.65 @ X 134.22 / 145.78) 比座体 `F.Fab` (135.680..144.320) 【还往外 1.46】⇒ ★**结构件的边开口必须【比座体外形更宽】, 才容得下这两个固定孔的螺丝头/结构柱** ★ ⇒ ★**这正是 E-6 说的「必须清空区 = 座体外形 + 固定孔位置」★ ★**

### ★①-4 · 现有两条开口的规格写法 (★你要照它的格式写第三条★)

★**`MECH/BOARD_ONEPASS_MECH_SYNC.md` §5 机器块 `openings[0]` (PORT_OPEN_DEBUG) 的字段 (★main 16:3x 实读★)**:
```
id / role / covers / frame / body_w / body_w_source / rect{x0,x1,y0,y1} / x0_range / y0_range_at_h_ref
cl_x / cl_y / worst_cl_x / worst_cl_y / som_hits / evidence
```
★**★关键: `rect` 是【h 三档】算出来的 (★`consts.open_y_formula` = `OPEN_Y_eff(h) = max(4.60, h + 2*(0.60+0.30)) = max(4.60, h+1.80)`★ · `consts.h_tiers` = `[0.90, 2.54, 4.00]` · `consts.body_h_ref` = `2.54` 但 `body_h_ref_is_fact: false` ⇒ ★**座体真实高度 = `[0数据]` ⇒ 开口 Y 一律按公式取三档, 不许把 2.54 当事实**)★**

★**⇒ 第三条边开口【也必须给 h 三档】, 同样不许把 2.54 当事实** ★

### ★①-5 · 一个新问题 (★E-6 只说了「补规格」, 但没说【板边开口往哪边开】★)

★**★`J_USB_C` 的边开口 = 板【下边】(Y=0) ⇒ ★**它跟检修口/调试口【不是同一种开口】★** ⇒ ★**检修口/调试口是【罩住一个器件的洞】(在板内部), 而 USB-C 边开口是【插头从板边插进来的缺口】(在板边界上) ⇒ ★**⇒ 你在写第三条时必须把这两种【语义不同】说清楚, 并且【不许把边开口写成一条普通矩形就完事】—— ★**因为边开口的【另一侧是板外】⇒ 它【不可能】像另两条那样做「h 三档 Y 净距」判定 ⇒ ★**这一点你要在规格里写清, 并【登记 need 给 main 拍板】(★结构开口尺寸归 main→boss★) ★ ★**

---

## ★② 根因一句话: 【ISS-290 把 `J_USB_C` 当【禁入区】登记了 (那是「不许放东西」), 但 MECH 的【开口规格 + 闸】是另一套东西 (那是「要在这里开洞」) ⇒ ★**两套东西之间没有第三种: 「这条边该怎么开口」⇒ 缺口一直在★ ★**

---

## ★③ 要交的几件 (★每件都能独立验收★)

### ★B1 · 规格页补第三条开口 (★`MECH/BOARD_ONEPASS_MECH_SYNC.md` §5 机器块 + §2 逐条表 + §10.1 三方对照摘要)

★**要做的**:
1. ★**`openings[]` 加第三条** (★id 建议 `PORT_OPEN_USBC`★) ⇒ ★**字段照 `PORT_OPEN_DEBUG` 的 15 个字段一条不缺** (★不许自创字段名★) ⇒ ★**`covers` = `J_USB_C` · `role` = `USB-C 边开口` · `frame` = `B160x100` (★跟另两条同帧★)**
2. ★**`rect` 必须给 h 三档** ⇒ ★**Y 向按 `OPEN_Y_eff(h) = max(4.60, h+1.80)` 取值 (★`h_tiers` = `[0.90, 2.54, 4.00]`★) ⇒ ★**X 向 = 板边开口的那条边 = Y=0 板边线, X 范围按 §①-3 的座体 + 固定孔实算 (★固定孔 Ø0.65 @ X 134.22 / 145.78 ⇒ 开口必须容得下 ⇒ 你自己算, 别照抄★)**
3. ★**`body_w` / `body_w_source` / `cl_x` / `cl_y` / `worst_cl_x` / `worst_cl_y` / `som_hits` / `evidence` 一条不许留空** ⇒ ★**`evidence` 标 `[实测]` (★板读 `F.Fab` + 焊盘实读★) ★**`body_h_ref_is_fact` 保持 `false` (★座体真实高度仍是 `[0数据]`★)**
4. ★**§2 逐条表** 加一条 `J_USB_C` 的 **8 字段行** (★字段名照 `MECH-PORT-DEBUG` / `MECH-PORT-UART` 那两行, 一条不许少★) ⇒ ★**`spec` 字段写边开口规格 (X 范围 / h 三档 Y) + 必须清空区 = ★**座体外形 + 两个固定孔位置 + 固定孔外扩** ⇒ ★**几何你自己从板读算 (★照 `USB-C-BODY` 禁入区那条的算法, 但【必须清空区】比【禁入区】更宽, 因为要容螺丝头/结构柱★) ⇒ ★**`criterion` 字段写一条可机器验的判据 (★怎么算绿 / 什么情况算红★) ★ ★**★另: `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §2 的 `USB-C-BODY` 禁入区【不许动】(★那是 ISS-290 的交卷物, 不是本单的活★) ⇒ ★**你只写 MECH_SYNC 这一页 + 两道 MECH 闸★ ★
5. ★**§10.1 三方对照摘要** 的 `J_USB_C` 行 `verdict` 字段: ★**现在是「可装 / 结构侧缺一条边开口规格」⇒ 改后要写成【可装 / ★边开口规格已补 (X 范围 / h 三档 / 固定孔清空区)★】★ ⇒ ★**★那行 `verdict` 不许留「待定」(★N5 闸会判红★) ★** ★**★另注 (★main 16:5x 实读确认, 别写错段号★)★: ★**完整 9 行三方对照表在 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §4 (★那是 ISS-290 的交卷物, 【不许动】★) ⇒ ★**你只改 `MECH_SYNC` §10.1 这个【9 行摘要】里的 `J_USB_C` 一行★ ★

★**★★一条不许破的纪律★★**: ★**这是【追加式】补规格 ⇒ 另两条开口 (`PORT_OPEN_DEBUG` / `PORT_OPEN_UART`) 的【一个字不许改】** ★ ⇒ ★**不许借机改 h 公式 / 不许改 `merged_opening` 块 / 不许改 `consts` 里任何一个数** ★

### ★B2 · 两道闸改成【集合 + 两两不相同】(★★合并禁令不许松★)

★**★`MECH/check_onepass_mech_sync.py` (M2) 与 `MECH/check_onepass_struct_crosscheck.py` (N3)★**:
- ★**把 `len(openings) != 2` 这种【条数断言】改成【期望 id 集合断言】**: ★**期望 = `{PORT_OPEN_DEBUG, PORT_OPEN_UART, PORT_OPEN_USBC}` (★恰好三条, 一条不少一条不多★) ⇒ ★**并【保留】(★或加强★)「任意两条矩形不许完全相同」这条 (★`M2b` 现在已有这条, 别删★) ⇒ ★**⇒ ★**合并成一条 / 把 USB-C 并进检修口 ⇒ 照样红** ★
- ★**N3 的「三条分别验」循环已经天然逐条跑 (★`for o in openings: for h, t in ...`★) ⇒ ★**第三条【自动进】逐档验 ⇒ ★**但你要【确认】它进来了 (★不许只看「三条都在 ids 里」就交卷★) ⇒ ★**在交卷单里贴出「第三条被验到」的实跑输出 (★哪一行报的是 `PORT_OPEN_USBC`★) ★
- ★**★闸的新增反向用例 (★≥4 条, 每条贴原样 rc★)★**:
| # | 构造 | 期望 |
|---|---|---|
| ★① ★ | ★**把 `openings[]` 里的 `PORT_OPEN_USBC` 删掉 ⇒ 闸必须红** ★ | ★**红** ★ |
| ★② ★ | ★**把 `PORT_OPEN_USBC` 的 id 改成别的 (★如 `PORT_OPEN_USB_C`★) ⇒ 闸必须红 (★集合不匹配★) ★ | ★**红** ★ |
| ★③ ★ | ★**把 `PORT_OPEN_USBC` 的矩形改成跟 `PORT_OPEN_DEBUG` 完全一样 ⇒ 闸必须红 (★合并禁令★) ★ | ★**红** ★ |
| ★④ ★ | ★**正向对照: 三条齐全且互不相同 ⇒ 闸 rc=0** ★ | ★**绿** ★ |
- ★**★反向用例必须在【沙盒副本】上做 (★真件一个字节不许碰★)★ ⇒ ★**照抄 `MECH/check_onepass_struct_crosscheck.py --selftest` 现成的沙盒做法 (★`_edit_spec_json` 那套改副本的办法, 它已经在用★)**

### ★B3 · 回归 (★别的闸一条不许红★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_onepass_mech_sync.py;          echo "rc=$?"   # 期望 rc=0 (M1~M5 全过)
python3 MECH/check_onepass_mech_sync.py --selftest; echo "rc=$?"   # 期望 rc=0 (★条数只许增不许减★)
python3 MECH/check_onepass_struct_crosscheck.py;    echo "rc=$?"   # 期望 rc=0 (N1~N6 全过)
python3 MECH/check_onepass_struct_crosscheck.py --selftest; echo "rc=$?"  # 期望 rc=0 (★条数只许增不许减★)
python3 MECH/check_demo_struct_truth.py;            echo "rc=$?"   # 期望 rc=0 (★G5b + C21 + C22★)
python3 MECH/check_board_frame_coords.py;           echo "rc=$?"   # 期望 rc=0
python3 state/merge.py;                             echo "rc=$?"   # 期望 rc=0
python3 state/gate_check.py;                        echo "rc=$?"   # 期望 rc=0 (Q1 18/18)
python3 state/issue_check.py;                       echo "rc=$?"   # 期望 rc=0
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

1. ★**交卷单** `HANDOFF/2026-11-17_mech-lead_ISS294_USBC边开口规格补缺.md` (★B1~B3 三块齐全 + 反向用例原样 rc★) ★
2. ★**改动的规格页** `MECH/BOARD_ONEPASS_MECH_SYNC.md` (★§5 机器块 `openings[]` 加第三条 + §2 逐条表加一行 + §10.1 三方对照摘要 `J_USB_C` 行的 verdict★) ★
3. ★**改动的两道闸** `MECH/check_onepass_mech_sync.py` + `MECH/check_onepass_struct_crosscheck.py` (★集合断言 + 合并禁令 + 反向用例★) ★
   ★**★并且: `MECH/BOARD_ONEPASS_MECH_SYNC.md` §5 机器块是 §2 逐条表的【投影】⇒ ★**改一处必须同步改另一处 (★页面自己写着「改数必须同步改 §2 表」★) ⇒ ★**交卷单里要贴出【两处逐字对得上】的自证 (★怎么对·贴什么★) ★★ ★
4. ★**分片** `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写 ⇒ ★**写完 `grep` 校验 `iss294` 在不在★**) ★
   ★**★另外顺手做一件小事 (★只有你能做, main 不越界写你的分片★)★**: ★**把 ISS-290 留在你分片里的那条 need `iss290_onpass_must_change_list_to_hw` 的状态标成【已转出】(★main 16:0x 已转 hw-lead 的 ISS-292 任务书「⑬ 追加」节·pm.yaml 已回写答案★) ⇒ ★**别自作主张把 need 关了, 在分片里写清依据就行★ ★**

---

## ★⑤ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 + mtime 双重自证★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**不许改 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `state/gen_netlist.py` / `state/land_v_values.py`** ★ · ★**不许改 `HW/` 与 `SW/` 的任何文件与分片** (★`HW/PCB/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 是 ISS-290 的交卷物, ★**不许动它**★) ★ · ★**不许改 `MECH/check_board_frame_coords.py`** (★它是两道闸的阈值来源, ★零漂移★) ★ · ★**不许改 `MECH/check_demo_struct_truth.py`** (★G5b/C21/C22 不许动★) ★ · ★**不许改 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 里 ISS-290 已登记的 `USB-C-BODY` 禁入区条目** (★你写的是【必须清空区】, 那是【另一回事】★★) ★ · ★**零外发** ★ · ★**不替老板拍板** (★★结构开口的最终尺寸归 main→boss★ ⇒ ★**你只交【几何 + 代价 + 建议】, 不许自己定尺寸★) · ★**不自签 issue_log** (★签字是 main 的活★)

★**★本单零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**不许发任何邮件/询价/问询/采购 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★ ★**

---

## ★⑥ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss294/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★

★**★这项目的老坑, 一条都不许再踩★**:
1. ★**写分片必须用 `state/frag_write.py` 原子写 (★禁止 `open(p,"w")`★)** ★
2. ★**只写本任务允许的文件, 不碰别人的** (★`state/fragments/hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节都不许碰★) ★
3. ★**★★不许把「恰好两条」改成「恰好三条」就当合并禁令还在 ★★★** ⇒ ★**那条禁制的本意是【不许把检修口/调试口合并】⇒ ★**你要改成【集合 + 两两不相同】, 合并成一条照样红★ ★**
4. ★**追加式**: 另两条开口 / `merged_opening` / `consts` 一个字不许改 ★
5. ★**不许为了让闸绿而改闸 / 放宽判据** ★
6. ★**不许自签 issue_log** ★

★**★为什么这一单必须赶在「板只改一次」那一趟之前做完★**: ★**USB-C 是 demo 板【唯一的供电 + 数据入口】⇒ 结构件没有这条边开口 ⇒ ★**实物插头根本插不进去 ⇒ 板装上了也用不了** ★ ⇒ ⇒ ★**这条规格必须在板定稿前补齐, 否则板改完才发现装不上 ⇒ ★**板白改第二遍** ★
