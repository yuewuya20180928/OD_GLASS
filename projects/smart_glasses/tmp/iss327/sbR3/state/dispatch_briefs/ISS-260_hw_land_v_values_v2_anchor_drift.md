# ISS-260 · hw-lead 任务书 —— V-2 落表路径在 ISS-257 落表后已失效 (★落表器自测缺失★)

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-16 21:5x · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**本单 = 内部活 · 原理图/网表/选型侧 · 不是 PCB 布线/布局类 · 不是老板级拍板**
> ★**老板 2026-11-11 10:07 主线口径**: 「先解决原理图绘制的问题, 再解决 PCB 绘制的问题」 ⇒ 本单在主线正中央 (原理图侧落表工具)。
> ★**老板 2026-11-12 02:02 政策**: 不再发信, 全靠自己查资料 ⇒ 证据自己查, 标证据等级, 查不到写降级方案, **不许去凑「等一句可以发」**。
> ★**零外发 · 零采购 · 不联系任何供应商 · 不下单**。

---

## ① 目标 (一句话)

★**把 `state/land_v_values.py` 的 V-2 落表路径修回可用, 并给它补一套 `--selftest` (★含本轮实测的坏案例当回归用例★)** ⇒ ★**老板拍完 A1/A2/A3 后, 决策页承诺的「一条命令 ⇒ 15 条一次落」这句话必须重新成立** ★★

★**本单一个字都不许落** (★V-2 / V-3 / V-4 老板都还没拍★) ⇒ ★**只修工具 + 补自测 + 出决策材料** ★

---

## ② 病灶 (★main 2026-11-16 21:5x 本机实跑, 原样输出, 不是抄交卷报告★)

```
$ python3 state/land_v_values.py --decision V-2=1
★★ rc=3: ★**落表前校验不过 ⇒ 拒绝落 (★零写盘★)** ★★
   ★★补丁对不上 (★状态漂移 or 已落过?★): state/gen_netlist.py · V2-1 USB ESD 段:
       2 行 → 3 行 (pin1=D+ / pin2=D− / pin3=GND) + 挪到 Type-C 侧 ⇒ 旧值出现 0 次 (期望 1 次)
```

★**同一条命令, 另两个取值仍然过 (★所以不是工具整体坏了, 是 V-2 这一条漂了★)**:
```
$ python3 state/land_v_values.py --decision V-3=E    ⇒ rc=0  ✅ DRY-RUN 完成 · 零写盘
$ python3 state/land_v_values.py --decision V-4=680  ⇒ rc=0  ✅ DRY-RUN 完成 · 零写盘
$ python3 state/land_v_values.py --decision V-2=2    ⇒ rc=2  ✅ V-2=2 必须打回 (白名单守得住)
$ python3 state/land_v_values.py --decision V-3=E --apply   ⇒ rc=2  ✅ 缺 --boss-decision 拒绝执行
```
★**干跑全程 5 个受保护 md5 逐字节不变 (★fail-closed 生效★)**:
板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ·
网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607`

### ★★根因 (★main 逐字实读, 不是推测★) ★★

★**落表器把 V-2 的【改前原串】硬编码在工具里 (`state/land_v_values.py` 的 `V2_ESD_OLD`)**, 它写的是 **ISS-257 之前**的网表源码串:
```
'    add("P1", "USB_D_P_SRC", "D_ESD_USB_D", "USB_D_P_SRC", "D_ESD_USB_D",\n'
'        "ESD 阵列 [待选型] (USB 2.0 双通道)", "D", "必装", "[推算]", "",\n'
```
★**而 ISS-257 (★21:22 落表, 已 verified★) 把 `state/gen_netlist.py` L1454-L1459 那一段改成了真型号**:
```
    add("P1", "USB_D_P_SRC", "D_ESD_USB_D", "USB_D_P_SRC", "D_ESD_USB_D",
        "TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)", "D", "必装", "[官方]", "", ...
```
⇒ ★**main 实测: 旧串在 `state/gen_netlist.py` 里现在出现 0 次** ⇒ ★**V-2 的补丁对不上当前真源 ⇒ 工具 fail-closed 拒绝落** ★

★**后果 (★这条是本单存在的理由★)**: 决策页 `DECISION_PENDING_2026-11-16.md` §A 明确承诺
「★**A1 + A2 + A3 一并拍 ⇒ 一条命令 `python3 state/land_v_values.py --apply --boss-decision "…"` ⇒ 15 条一次落** ★」
⇒ ★**现在老板就算拍完 A3, 那条命令也会当场 rc=3 失败** ⇒ ★**A3 = V-2 这一格【当前不可兑现】** ★

### ★★更深一层: 光把锚点改回去【还是错的】 (★这是本单真正的难点★) ★★

★**V-2 配方把 ESD 的【架构】写死成了「3 脚双通道」** (★`V2_ESD_NEW` 写 3 行: pin1=D+ / pin2=D− / pin3=GND, value 写 `ESD 阵列 (USB 2.0 双通道, D+/D− 共用一颗, …)` 或 `TPD2EUSB30 (3脚双通道, …)`★)。
★**但这与两件已落的事实冲突**: ★
① ★**ISS-241 的选型矩阵硬发现①**: ★**ESD 4 件全是 2 焊盘占位 ⇒ 双通道 3 脚件 (`TPD2E2U06` 的 DCK/SC70-3 = 3 脚 · DRL/SOT-5 = 5 脚) 物理落不下 ⇒ 只能选 2 脚单通道器件** ★
② ★**ISS-257 已经按这条把 `D_ESD_USB_D` 落成 2 脚单通道真型号 `TPD1E05U06DPYR` (★evidence `[官方]`★)**, 并且它就是 ISS-241 矩阵 ③ 里 `D_ESD_USB_D` 的**推荐项** (★「0.42 pF · 4 件 ESD 用 1 个 OPN · 减少来料种类」★)

⇒ ★**⇒ 如果只是把 `V2_ESD_OLD` 的锚点改回当前真源就完事, 老板拍 A3=① 后这一跑, 会把 ISS-257 刚落下的【真采购型号】覆盖成一句【判据串】+ evidence `[推算]`** ⇒ ★**G1a-7「选型已落表」刚转绿的东西被自己 undo 掉, BOM 又拿不到真实 OPN** ⇒ ★**这与 ISS-257 的交付目标直接相反** ★

⇒ ★**⇒ 所以本单不是「改个字符串」, 是【把 V-2 这条路径重新对齐到当前真源, 并且让「架构待裁」这件事在工具里显式可见、而不是靠一段硬编码悄悄替老板做主】** ★

---

## ③ 你要做的 (★四件交付物, 少一件即无效★) ★

### ★① 修 `state/land_v_values.py` 的 V-2 路径 (★只改这一个文件★) ★

★**三条硬要求 (★每条都要能被机器判★)**:

★**(a) 锚点必须对【当前真源】成立** ⇒ ★**`python3 state/land_v_values.py --decision V-2=1` ⇒ rc=0 (dry-run) 且 5 个受保护 md5 逐字节不变** ★
★**(b) 绝不许把 ISS-257 已落的真 OPN 悄悄换成判据串** ⇒ ★**跑出来的逐字 diff 里, `D_ESD_USB_D` 的 value / evidence 两列不许出现「`TPD1E05U06DPYR (TI 单通道 ESD …)` → `ESD 阵列 (USB 2.0 双通道, …)`」这种把真型号降级成描述串的替换** ⇒ ★**如果你的修法必然要动 `D_ESD_USB_D` 的 value, 那就说明【架构本身待裁】(★A3 / W-1★) ⇒ 你的输出必须是【工具明确拒绝 + 说清为什么】, 而不是【自己挑一个架构落下去】** ★
★**(c) fail-closed 语义不许放宽** ⇒ ★**任何一处对不上仍然必须 rc≠0 且零写盘** ⇒ ★**不许把 `verify()` 的计数断言改松** ★

★**允许你做的改法 (★不限于, 但至少做到★)**:
★**· 让 V-2 配方【读当前真源】而不是硬编码一串旧文本** (★例: 从 `state/gen_netlist.py` 现读 `D_ESD_USB_D` 那两行, 用位号/网名定位, 而不是靠 value 串匹配★)
★**· 把「型号」与「架构」两件事在工具里分开**: ★**型号未拍 ⇒ 只可能写判据串; 架构 (2 脚单通道 vs 3 脚双通道) ⇒ 归 A3/W-1 裁** ⇒ ★**工具该做的是【把两个未决显式列出来并要求 `--boss-decision` 同时覆盖】, 而不是先替老板选一个架构写死** ★
★**· 报错文案要能区分【状态漂移】与【已落过】** (★现在两者的提示混在一起★) ⇒ ★**漂移时要说清「哪一行 / 期望什么 / 实际什么」** ★

★**边界**: ★**不许落任何 V 值** (★`--apply` 全程不许带★) · ★**不许改 `state/gen_netlist.py` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / 板 / `.kicad_pro`** ★

### ★② 给落表器补 `--selftest` (★≥6 条反向用例★) ★

★**为什么必须有**: ★**这个项目所有的闸都有 `--selftest`, 只有落表器没有** ⇒ ★**所以 ISS-257 落表把 V-2 锚点打漂这件事, 没有任何机器会主动报出来 —— 是 main 今晚手点 `--decision V-2=1` 才撞到的** ⇒ ★**下次再有人落一次选型, 同样的漂移还会再发生一次, 而且还是会等到老板拍板那天才炸** ★

★**必须覆盖的用例 (★至少这 6 条, 每条都要自证「真的改到了目标」★)**:
1. ★**【本轮实测的坏案例·必须当回归用例】** ★把 `state/gen_netlist.py` 里 `D_ESD_USB_D` 那段改回 ISS-257 之前的旧串 ⇒ ★**V-2 路径必须立刻红** (★证明它真在读当前真源★)
2. ★**V-2=2 必须 rc≠0** (★假绿那一条路必须永远堵死★)
3. ★**非法取值 (★例 `--decision V-2=E2`★) 必须 rc≠0 且零写盘**
4. ★**`--apply` 不带 `--boss-decision` 必须 rc≠0 且零写盘** (★「不许替老板拍板」的机器化保证不许松★)
5. ★**V-3 / V-4 的锚点必须仍然是【当前真源】** ⇒ ★**这条现在是「碰巧成立」(★ISS-257 恰好没动 `DEMO_DNP` 那三行、也没动 `R_ILIM`★), 必须变成【被断言住】** ★
6. ★**每个用例跑完, 5 个受保护 md5 必须逐字节不变** (★自测自己也不许写盘★)

★**自测跑法**: ★**`python3 state/land_v_values.py --selftest` ⇒ rc=0** ★ (★`--help` 里现在没有这一项, 你要加★)
★**边界**: ★**自测一律在临时副本里做 (★像 `HW/check_netlist_selfconsistency.py` 那样★), 真盘零写入** ★

### ★③ 出【A3 / W-1 语义冲突】的决策材料 (★交 main, 不代拍★) ★

★**这是本单第三件交付物, 也是最容易被做成「又一份没人看的文档」的一件 —— 请写成【main 能直接转给老板的选项表】** ★

★**必须摆清楚的冲突 (★以下都是 main 今晚实读的原文事实, 你要在材料里逐条复核一遍再写★)**:
| 事实 | 出处 | 证据等级 |
|---|---|---|
| ESD 4 件全是 2 焊盘占位 ⇒ 双通道 3 脚件物理落不下 | `HW/PART_SELECTION_MATRIX_2026-11-16.md` §1 共同硬约束 | `[官网]` (矩阵自测) |
| `D_ESD_USB_D` 已落 2 脚单通道真型号 `TPD1E05U06DPYR` | `state/gen_netlist.py` L1454-L1459 · `HW/netlist_v1.csv` L417/L418 | `[实测]` (main 今晚实读) |
| 该型号 = 矩阵 ③ `D_ESD_USB_D` 的推荐项 | 矩阵 §③ 推荐栏 | `[官网]` (矩阵自测) |
| 落表器 V-2 配方写死「3 脚双通道」 | `state/land_v_values.py` `V2_ESD_NEW` | `[实测]` (main 今晚实读) |
| V-2 网表侧落表 = **0 条转绿** (★7→7 = 假绿★) | ISS-230 实测 (★ISS-236 已照抄进工具★) | `[实测]` (沿用已核数据) |
| V-2 的 3 条真要转绿得靠板那一趟 (B-3 / B-4 / B-5) | `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` §2 | `[实测]` |

★**选项表至少给这三条 (★每条: 改哪个文件的哪一行 + 改成什么 + 代价 + 会让 `--expect-resolved` 少几条 + 会不会碰板★)**:
- ★**① 维持 2 脚单通道** (★与 ISS-257 已落的真源一致★) ⇒ ★**V-2 网表侧还需要落什么? 还是【什么都不用落】?** ⇒ ★**D− 侧的保护怎么办 (★R4 / R9 那 3 条★)** ⇒ ★**板那一趟要不要改 footprint** ★
- ★**② 换 3 脚双通道 (★= 现有 V-2 配方★)** ⇒ ★**必须同时改 footprint (★占位 2 焊盘 → 3 焊盘★) ⇒ ★**这是【板那一趟】(★按 10:07 口径排队★) ⇒ 板 md5 会变一次** ⇒ ★**且要回答「改 footprint 会不会让 SW / MECH 两侧再走一轮 H-1 重锚」** ★
- ★**③ 换 2 脚双向件 (★矩阵 W-1 的 ③ 号选项: `PESD5V0S1BA` SOD-323, pin1=K1 / pin2=K2 对称 ⇒ 天然免疫 pad 序接反★)** ⇒ ★**代价: 面积 + 焊盘间距要改 (★落板批次按 SOD-323 官方 land 重画★) ⇒ 仍是板那一趟** ★

★**纪律**: ★**本单不代拍 A3 / W-1** ⇒ ★**每个选项后面只准写「建议默认值 + 依据 + 代价」, 不准写「已决定」** ★
★**落点**: ★**写进交卷单 (§C) ⇒ 由 main 转进决策页** ⇒ ★**`DECISION_PENDING_2026-11-16.md` 是 main 的地界, 本单一个字不许改** ★

### ★④ 交卷单 + 分片 + 机器自证 ★

★**交卷单** `HANDOFF/2026-11-16_hw-lead_ISS260_V2落表路径修复与A3冲突.md` (★B1~B6 六块齐全★)
★**分片** `state/fragments/hw.yaml` (★必须走 `python3 state/frag_write.py` 原子写★)
★**机器自证 (★全部贴进回复★)**: ★**交卷前把 6 条自测用例 + 6 条门禁逐条实跑, 输出原样贴出来** ★

---

## ④ 交卷前必须实跑并把输出原样贴进回复 (★命令都已实测存在★) ★★

```
python3 state/land_v_values.py --decision V-2=1            # rc=0 (★dry-run · 零写盘★)
python3 state/land_v_values.py --decision V-2=2            # rc≠0 (★必须打回★)
python3 state/land_v_values.py --decision V-3=E            # rc=0 (★不许回归★)
python3 state/land_v_values.py --decision V-4=680          # rc=0 (★不许回归★)
python3 state/land_v_values.py --decision V-3=E --apply    # rc≠0 (★缺 --boss-decision 拒绝★)
python3 state/land_v_values.py --selftest                 # rc=0 (★≥6 条反向用例★)
python3 HW/check_netlist_selfconsistency.py                # rc=0 (★现状守卫不许回归★)
python3 HW/check_netlist_selfconsistency.py --selftest      # rc=0 (★反向用例一条不许少★)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★预期: 仍 18 条未落表★)
python3 state/check_stage_g1a.py                           # rc=1 (★预期: 只差 G1a-4 + G1a-8 两条★)
python3 state/check_netlist.py                             # rc=0
python3 state/check_netlist_pins.py                        # rc=0
python3 state/check_sch_erc.py                             # rc=0 (★ERC 违规数 = 0★)
python3 state/check_sch_pinfull.py                         # rc=0 (★K=0★)
python3 HW/check_g1a7_selection_landed.py                  # rc=0 (★G1a-7 不许被本单 undo 掉★)
python3 state/merge.py && python3 state/gate_check.py      # rc=0 且 【Q1 交付齐备率】 18/18
```

★**受保护 md5 (交卷前后必须逐字节不变)**: ★**板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607`** ★
★**再自证一次**: ★**`HW/netlist_v1.csv` 里 `D_ESD_USB_D` 仍是 `TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)` (★ISS-257 的成果一个字没被本单 undo★)** ★

★**★已知会红、且不归你管的那两盏 (★提前说清, 免得你误修★)** ★★
· ★**`HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ rc=1, 18 条未落表** ⇒ ★**这是【等老板拍 A1/A2/A3】的正常态** (★13 条卡 V-3 · 3 条卡 V-2+板 · 1 条卡 V-4 · 1 条卡板那一趟★) ⇒ ★**本单的目标是【让 A3 变得可兑现】, 不是【把 18 条变 0 条】⇒ 一条都不许上升, 也不许为了好看去动 `--expect-resolved` 的断言** ★
· ★**`state/check_stage_g1a.py` ⇒ rc=1, 还差 G1a-4 + G1a-8 两条** ⇒ ★**G1a-8 卡在 ISS-097 (★等老板审阅关机语义★) ⇒ 不归你管** ★

---

## ⑤ 边界 (★违反一条即本单无效★) ★★

· ★**不许落任何 V-2 / V-3 / V-4 的值** (★`--apply` 全程不许带★) ⇒ ★**网表 / 脚表 / BOM / 板 / 原理图 一个字节不许动** ★
· ★**不许改** `state/gen_netlist.py` · `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` · `HW/PCB/demo_mainboard.kicad_pcb` · `HW/PCB/demo_mainboard.kicad_pro` · 任何 `.kicad_sch` ★
· ★**不许改** `HW/check_netlist_selfconsistency.py` 的 EXPECT 现状断言 (★那是【判据】, 改它 = 改判据刷绿 = 铁律违规★) ★
· ★**不许改** `SW/` 下任何文件 (★sw-lead 的 ISS-258 正在跑 H-1 重锚★) · 不许改 `MECH/` 下任何文件 (★mech-lead 的 ISS-259 正在跑 H-1 重锚★) ★
· ★**不许改** `state/issue_log.yaml` (★status 留给 main 落 verified★) / `DECISION_PENDING_2026-11-16.md` (★决策页是 main 的地界★) / `PROJECT_TRACKER.md` §0 / `state/outbox/` / 别人的分片 ★
· ★**不许碰** PCB 布线 / 布局 / 板框 ⇒ ★**板侧 8 项 (B-1~B-8) 继续【排队等原理图定稿】, 不归本单** ★
· ★**不许把 [推算] 写成 [官网]/[实测]** ⇒ ★**板端 [实测] = 0 条** ★
· ★**零外发** (★不发邮件 / 询价 / 问询 / 采购★) ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到必须写降级方案** ⇒ ★**不许写「等原厂回信」** ★
· ★**不许自签 issue_log** ★
· ★**不许替老板拍板** (★A1 / A2 / A3 / W-1 / V-2 / V-3 / V-4 全部只给选项 + 量化代价 + 建议默认值★) ★
· ★**不许把「修工具」做成「重写工具」** ⇒ ★**本单允许你改的只有 `state/land_v_values.py` 这一个文件 (★加上 §③② 要新建的自测件, 若你另建文件请在交卷单里声明★)** ⇒ ★**这个文件是 ISS-236 的交付物, 里面还有 V-3 / V-4 两套已经自证过的配方 ⇒ 不许推倒重来** ★

---

## ⑥ 交卷前最后一件事

★**把你改完的落表器, 按「老板明天就拍 A3=①」这个假设, 在【临时副本】里端到端跑一遍 V-2 的两段走 (★网表侧 + 板那一趟的清单对齐★)** ⇒ ★**交卷时贴出: 「如果老板明天拍 A3=①, 会不会再撞一次 rc=3?」的实测答案 (★干跑即可, 不许 --apply★)** ★
★**不许为了对上而改口径** ⇒ ★**对不上就写「不一致, 原因是 X」** ★
