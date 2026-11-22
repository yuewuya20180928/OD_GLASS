# ISS-282 · hw-lead 交卷单 · 「板只改一次」的【`FSIN_OUT` 根因订正 + 布线前置闸】

> ★**派活**: 项目总工 (main / moli) · job cron `775d9893` · 派活时刻 2026-11-17 09:5x
> ★**本单性质**: ★**内部活 · PCB 线 · 纯规格 + 作业包追加式订正 + 机器闸类** ⇒ ★**零写板 · 零落表 · 零跑布线臂 · 零改网表/脚表/BOM · 零改既有判据阈值** ★
> ★**本单边界**: ★**交付的是【根因订正页 + 作业包追加式订正 + 机器闸】, 不是【板】, 不是【布线】** ★
> ★**★本单【零新增待拍项】⇒ 不用问老板 ⇒ hw-lead 自己做完交卷, main 独立复验后落 verified★**
> ★**续做说明**: ★**首趟 2026-11-17 10:0x~10:2x 被网关重载打断 (★盘上已有 3/4 件交付物, 交卷单只有骨架★) ⇒ 本趟 11:0x 续做 ⇒ ★**先读任务书全文, 再逐件复核+补齐, 不从零重做★** ★

---

## ★B0 · 交付物清单 (★4 件 + 分片, 少一件即无效★)

| # | ★产物★ | ★路径★ | ★状态 (★本机实测★)★ |
|---|---|---|---|
| 1 | ★根因订正页 ★ | `HW/PCB/FSIN_OUT_ROOTCAUSE.md` | ★**已落盘 (★首趟 20128 B → 11:12 校订后 20742 B★)** ★ ⇒ ★**§0 订正声明 · §1 病灶逐字 · §2 escape_stub 判据实测 · §3 逐网忽略法实测表 · §4 优先网历史交叉 · §5 沙盒 DRC · §6 4 层 A\* 假阴性 · §7 与 main 三个数字逐条对齐 · §8 结论与直接含义 · §0.1 机器可读锚点块 (9 项)★** ★ |
| 2 | ★作业包追加式订正 ★ | `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §6.2 (★S8 行下面追加★) | ★**已落盘 (★老 S8 行 L387 逐字仍在 + 订正行 L388★)** ★ ⇒ ★**diff 实测: 删除行数 = 0, 新增 23 行 (见 B3.3)★** ★ |
| 3 | ★机器闸 (D1~D5 + selftest) ★ | `HW/check_fsin_rootcause.py` | ★**已落盘 (★首趟 39479 B → 11:13 修 3 处自身 bug → 11:3x 按 main 补充实测回头修 (★见 B1.4★) + 11:5x 修沙盒配额问题后 46812 B★)** ★ ⇒ ★**D1~D5 全绿 (rc=0) · `--selftest` 15/15 (rc=0)★** ★ |
| 4 | ★交卷单 (本文件) ★ | `HANDOFF/2026-11-17_hw-lead_ISS282_FSIN_OUT根因订正.md` | ★**本文件 (★B0~B6 + 附 A/B/C 全填, 不是骨架★)** ★ |
| 5 | ★状态分片 ★ | `state/fragments/hw.yaml` | ★**已落盘 (★走 `state/frag_write.py --agent hw-lead` 原子写 + grep 校验, 见 B4★)** ★ |

★**★本趟 (11:0x) 相对首趟 (10:0x) 补齐的东西 (★不是重做, 是收口★)★**:

| # | 首趟留下的洞 | ★本趟怎么收的★ | ★证据★ |
|---|---|---|---|
| ★**1** ★ | ★**机器闸 D2/D3 报「读不到板面 / 读不到那两个焊盘」** ★ | ★**根因是【闸自己的代码 bug】, 不是板不在 ⇒ 修了 3 处 (详见 B1.2)★** | ★**D2/D3 现在绿 + `--dump` 打出真值 1.300000 / 1.350000 / 0.438361★** ★ |
| ★**2** ★ | ★**D2/D3 的距离口径与页不一致** ★ | ★**统一成【路由器 `_nearest_other_pad()` 自己的口径】(★焊盘中心 → 别的网焊盘外接矩形边缘★) ⇒ 页与闸同一口径★** | ★**页锚点块 d_a=1.300000 / d_b=1.350000 · 闸重算逐字一致 (TOL=1e-6)★** ★ |
| ★**3** ★ | ★**D5 的三个 md5 不在【基线 ∪ 落表后】集合里** ★ | ★**根因 = 闸去【落表台账】里只读了【第一个】「前后对照」小节 (★老批次★) ⇒ 修成扫【全部】小节 + 引台账行号★** | ★**D5 绿 + 出处行号 L1270/L1271/L1272 打出来★** ★ |
| ★**4** ★ | ★**交卷单只有骨架** ★ | ★**本文件全填 (★B1~B6 + 附 A/B/C★)** ★ | ★**本文件★** ★ |
| ★**5** ★ | ★**分片没写** ★ | ★**`state/frag_write.py` 原子写 + grep 校验 (见 B4)** ★ | ★**B4 的 grep 输出★** ★ |
| ★**6** ★ | ★**验收第 3 条 `HW/check_onepass_preflight_coverage.py` 红 (P5 清单过期 + P6 基线过期)** ★ | ★**本单顺手收口 (★main 11:0x 明确授权★): P5 两条 current_state 改成盘面实测值 + P6 三个基线 md5 改成落表后真值并引台账 §16.2★** | ★**rc=0 (P1~P6 全绿) + `--selftest` 8/8★** ★ |

---

## ★B1 · 结论摘要 (★一句话 + 三条 + 三个闸自身 bug★)

### ★B1.0 · 一句话★

★**盘上写的「`FSIN_OUT` 是【逃逸方向 bug】」这个根因【不成立】⇒ 订正为【布线排队顺序】: 第 2 步先布的电源网 `VDD_3V3_IO` 先占了那条走廊, 第 4 步才布的 `FSIN_OUT` 后挑只剩一条被压死的窄缝 ⇒ ⇒ 这条【不是板侧项】⇒ ⇒ 【不需要动板】⇒ ⇒ 它从「会改板」名单里划掉, 但【不划掉「布不通」】⇒ ⇒ 挪到【布线臂 env 配置】(`PCB_PRIORITY_NETS`) ⇒ ⇒ 「板只改一次」的铁律不受影响★** ★

### ★B1.1 · 三条硬证据 (★本机实跑, 闸自己会重算复现★)★

| # | 结论 | ★实测数 (★闸重算, 不抄页★)★ | ★出处★ |
|---|---|---|---|
| ★**①** ★ | ★**这两个焊盘根本不进 `escape_stub()` 分支** ★ ⇒ ★**「逃逸方向」跟这件事无关** ★ | ★**`R_SER_FSIN.1` → 最近异网焊盘 1.300000 mm (`R_SER_FSIN.2`/`FSIN`) · `TP_FSIN.1` → 1.350000 mm (`CONN_CAM.30`/`LIGHT_5V`) · 阈值 (源码读出) 0.45** ★ ⇒ ★**两者 ≫ 0.45 ⇒ 走【正常出脚】** ★ | ★`state/gen_pcb_routing.py` L2089 `if self._nearest_other_pad(net, cx, cy) >= 0.45: return None`★ + L1742 `_nearest_other_pad()` (★口径 = 焊盘中心 → 别的网焊盘外接矩形边缘★)★ |
| ★**②** ★ | ★**唯一挡路者 = `VDD_3V3_IO`** ★ ⇒ ★**只忽略它一个网, 直线就过** ★ | ★**A→B 直线 L = 3.0067 mm · 忽略 `VDD_3V3_IO` 后净距 D = 0.438361 ≥ 判据 0.395 ⇒ PASS · 忽略任何别的网都还是 FAIL (D = −0.1250, 那条铜直接穿过直线)★** ★ | ★判据 0.395 = W_SIG/2 (0.125) + CLEAR (0.20) + 栅格余量 (0.07) ★★源码 `W_SIG`/`CLEAR` + `HW/PCB/ROUTING_REPORT.md` §1 (★闸自己读, 不写死★)★ |
| ★**③** ★ | ★**排队顺序是唯一的机制性解释** ★ | ★**`POWER_NETS` 里就有 `("VDD_3V3_IO", W_SIG, 1)` (电源 = 第 2 步布) · `FSIN_OUT` 在 `POWER_NETS`/`MIPI_PAIRS`/`PCB_PRIORITY_NETS` 三张表里【都没有】⇒ 落到第 4 步 (最后)★** | ★`state/gen_pcb_routing.py` L4675 / L4861 (电源第 2 步) / L4799 (优先网第 1b 步) / L4972 (其余信号第 4 步) / L4808 (用法示例里就有 `FSIN_OUT`)★ |

★**★⇒ 直接含义 (★main 的判断, 本单只登记, 不代拍★)★**: ★**① `FSIN_OUT` 从「会改板 / 要老板拍」那一类里划掉 ⇒ 老板那一趟要拍的东西少一条 (★好消息, 但它没消失, 只是换了归属★) · ② 它挪到【布线臂 env 配置】⇒ 「布线 45→0」那一趟仍然必须把它布通, 而布通它【不需要动板】⇒ 【板只改一次】铁律不受影响 · ③ ★**但走廊是零和的 (★`state/LANE_CONFLICT_WORKLIST.md` §8 已实测★) ⇒ 优先布给了 `FSIN_OUT`, 被挤掉的可能就是差分主干 (★实测 v76p1 臂: `CSI_D0_CK_P_SRC/N_SRC` 成死腿 ⇒ 整板 unc 46→47★) ⇒ ⇒ 【给 `FSIN_OUT` 提前, 不会自动让整板 unc 变小】⇒ ⇒ 那一趟的「unc→0」判据必须【按名单制】看 (★哪些网通了 / 哪些网死了★), 不许只看总数★ ⇒ ★**这是【老板那一趟的判据口径问题】⇒ 交给 main 排期, 本单不代拍★** ★** ★**

### ★B1.2 · ★★机器闸自己身上的三个 bug (★main 11:0x 实跑定位的那一处, 加上本趟查出的另两处★)★★

★**★这三处【全部是闸自己的代码 bug】, 不是板不在 / 不是有人偷改盘 / 不是判据方向错 ⇒ ⇒ ★**本单只修 bug, 一条判据方向都没动, 一个阈值都没改★** ★**

| # | 症状 | ★真因 (★本机实跑定位★)★ | ★修法 (★只修 bug, 不改判据★)★ | ★自证★ |
|---|---|---|---|---|
| ★**1** ★ | ★**D2/D3 报「读不到板面 / 读不到那两个焊盘」** ★ | ★**`_seg_rect_dist()` L337 里的 `NameError: name 'e' is not defined` (★变量 `e` 从未定义, 那个列表叫 `edges`★) ⇒ 异常被上层吞掉 ⇒ 报成「读不到」★** ★ | ★**变量名改对 + 逐条边测相交 (★每条边用自己的两个端点★) ⇒ ★**判据方向一字未改★** ★ | ★**`--dump` 现在能打出完整 D3 实测表 (★修前直接抛 NameError 崩掉★)★** ★ |
| ★**2** ★ | ★**D2/D3 报「读不到那两个焊盘」** ★ | ★**`find_pad()` 只认 `(ref, num)` 分开给, 而锚点块里写的是点分全名 `R_SER_FSIN.1` ⇒ 永远匹配不上** ★ | ★**★按 main 11:0x 指示回头修 (★详见 B1.4★): 拆脚号的活儿归【页面锚点契约】(`pad_a` + `pad_a_num` 分开写), `find_pad()` 回到【严格逐字匹配】⇒ ★**不许它猜脚号**★** ★ | ★**D2 现在能重算 1.300000 / 1.350000 · 契约破了会显式报「契约破了」(★反向用例 ⑬ 守卫★)** ★ |
| ★**3** ★ | ★**D5 报三个 md5「不在【基线 ∪ 落表后】集合里」** ★ | ★**`landing_after_md5()` 只取落表台账里【第一个】「前后对照」小节 (★§6 · 老批次★) 的最后一列 ⇒ 拿到的是老批次的值 (`c78f9912…`), 不是本次落表后的真值 (`2f17650c…`)★** ★ | ★**改成按文件取【最新一条落表记录】(★台账按落表批次往后追加 ⇒ 最后提到该文件的那一行 = 最新一条★) ⇒ 允许集合 = 【MD5 台账基线】∪【最新一条的前/后值】★ ⇒ ★**既不写死三个值, 也不把全部历史值都放行 (★比第一版更紧★)** ★ | ★**D5 现在绿 + 出处行号打出来: 网表 L1270 / 脚表 L1271 / BOM L1272 (★最新一条★) · 反向用例 ⑭⑮ 守卫★** ★ |
| ★**4** ★ | ★**`--selftest` 中途 `OSError: [Errno 122] Disk quota exceeded` ⇒ ★**闸自己跑挂 (A2 一度 rc=1)** ★ | ★**`/tmp` 是带 `usrquota` 的 tmpfs; 老写法把 15 份沙盒留到最后一次性删 ⇒ 峰值 ~86 MB ⇒ 环境一满就炸** ★ | ★**改成【每条用例跑完立刻 `rmtree`】⇒ 峰值只剩 1 份沙盒 (~5.7 MB) ⇒ ★**判据一个字没动, 纯工程鲁棒性** ★ | ★**15/15 全绿 + 跑完沙盒残留 = 0 (★实测★)** ★ |

★★**★⇒ fail-closed 一条没松 (★这是本单改闸的红线★)★★**: ★**任何【没在台账登记过】的 md5 仍然当场红 (★反向用例 ⑦ + ⑫ + ⑭ 自证★) ⇒ ★**允许集合 = 「基线 ∪ 最新一条落表记录」, 不是「随便什么值都放行」★** ★

### ★B1.3 · ★★D2/D3 的口径统一 (★main 11:0x 点名的那一条★)★★

★**★统一到【路由器源码自己的口径】: `_nearest_other_pad()` = 焊盘中心 → 别的网焊盘外接矩形边缘 (mm)★** ⇒ ★**页与闸现在说的是同一个量★**

| 量 | ★main 09:5x 报的数★ | ★本单 (页 + 闸) 的数★ | ★差在哪 (★页 §7 ①② 逐条登记★)★ | ★判定★ |
|---|---|---|---|---|
| ★`R_SER_FSIN.1` → 最近异网焊盘★ | ★**1.1500 mm** ★ | ★**1.300000 mm** ★ (★`R_SER_FSIN.2`/`FSIN`★) ★ | ★**差 0.1500 = 该焊盘【高 0.9】的一半 ⇒ 指向测量脚本把外接矩形宽/高取反 (★只登记现象, 不下断言★)★** ★ | ★**一致 (★1.30 ≫ 0.45★)★** ★ |
| ★`TP_FSIN.1` → 最近异网焊盘★ | ★**1.3528 mm** ★ | ★**1.350000 mm** ★ (★`CONN_CAM.30`/`LIGHT_5V`★) ★ | ★**同一颗物理焊盘 (★板上 Reference 逐字是 `CONN_CAM.30`, 不是 `CONN_LIGHT.30`★); 差 0.0028 落在「取铜多边形角点 vs 取外接矩形边」★** ★ | ★**一致 (★1.35 ≫ 0.45★)★** ★ |
| ★只忽略 `VDD_3V3_IO` 后的净距★ | ★**0.439 (PASS)** ★ | ★**0.438361 (PASS)** ★ | ★**同一口径 (★`D` = 中心线到异网铜边★); 差 0.00064 mm (★浮点/取整级★)★** ★ | ★**一致 (★PASS★)★** ★ |

★**★⇒ 结论一字不变 (★1.30/1.35 ≫ 0.45 ⇒ 不进 `escape_stub`; 忽略 `VDD_3V3_IO` ⇒ PASS; 不忽略 ⇒ FAIL 且挡路者 = `VDD_3V3_IO`★) ⇒ ★**两个口径都 ≫ 0.45, 就算把 main 的 1.1500/1.3528 当真值, 「不进 escape_stub」这个结论照样成立★** ★

---

### ★B1.4 · ★★main 11:0x 补充实测的逐条回应 (★五个点, 全部已收★)★★

★**★main 11:0x 补了「D2/D3 还有第三个坑, 只修 L337 那个 NameError 不够」+ D5 取值建议 ⇒ 本单逐条回:★★**

| # | ★main 11:0x 说的★ | ★本单怎么收的★ | ★验收★ |
|---|---|---|---|
| ★**1** ★ | ★**坑 ①: L337 `_seg_rect_dist` 里 `e` 未定义 (变量名是 `edges`)★** | ★**已修 (★变量名 `e`→`edges`★)★ ⇒ ★**外加把「边-边相交」改成【逐条边用自己的两个端点测】: ★**老代码第二段拿 `edges[0][1]` 跟 `edges[1][0]` 比 ⇒ ★**那两个其实是同一个点** (★`edges[0]` 的尾点 = `edges[1]` 的首点★) ⇒ ★**那段判定本来就在测「相邻两条边」而不是「线段 × 这一条边」⇒ ★**跟变量名是同一处 bug, 一起修★ ⇒ ★**判据方向不变★** ★ | ★**`--dump` 能打出完整实测表 (★修前直接崩★)★** ★ |
| ★**2** ★ | ★**坑 ②: `find_pad` 参数口径 —— 锚点里存的是「位号.脚号」整串 ⇒ 永远 None ⇒ 报「读不到焊盘」; ★**修法二选一: ① 锚点把脚号单列 ② 调用点先 split; ★★不许放宽 `find_pad` 本身去「猜」★★★** ★ | ★**★首趟我修错了方向: 我放宽了 `find_pad` 自己去按最后一个点猜脚号 ⇒ 正是 main 禁止的那一条 ⇒ ★**已回头修成 main 的方案①: 锚点写成 `pad_a=R_SER_FSIN` + `pad_a_num=1` / `pad_b=TP_FSIN` + `pad_b_num=1` (★锚点共 11 项★), `find_pad()` 回到【严格逐字匹配】(★ref 里带点就匹配不上, 不猜★)★ ⇒ ★**并且加了【契约守卫】: 锚点要是还带着脚号后缀, 闸显式报「锚点契约破了」而不是蒙一个焊盘出来★** ★ | ★**反向用例 ⑬ (★把点分写法塞回 `pad_a` ⇒ D2 红且报「契约」★)· D2/D3 现在绿** ★ |
| ★**3** ★ | ★**坑 ③: D2/D3 的距离口径要统一 (★页 1.1500/1.3528 vs 闸 1.300000/1.350000★)★** | ★**已统一 (★11:1x 就收了★) ⇒ ★**页与闸都改成【路由器 `_nearest_other_pad()` 用的那个量】: 焊盘中心 → 异网焊盘外接矩形边缘 = 1.300000 / 1.350000 ★ ⇒ ★**页里新增一段把口径写死: 它【既不是「中心距」也不是「边到边距」】, 是路由器判 escape_stub 用的那个量 ⇒ main 报的 1.1500/1.3528 是另一个口径 (★§7 ①② 已逐条登记★) ⇒ ★**两个口径都 ≫ 0.45 ⇒ 结论逐字不变★** ★ | ★**D2 现在逐字比页上的三个数 (★TOL=1e-6★)★** ★ |
| ★**4** ★ | ★**D5 建议: 取【最新一条】落表记录, 别把三个值写死 ⇒ 下一轮落表 md5 还会变, 写死 = 又一次假红★** | ★**已按建议改 (★且比建议更严一档★) ⇒ ★**闸从台账【读】最新一条 (★一行都不写死★) ⇒ 下一轮落表只要在台账登记了, 闸自动跟上 (★不用改代码★)★ ⇒ ★**同时把「回滚到中间态」(★悄悄撤销一次已拍板的落表★) 拦成红 —— 我第一版是「全部历史登记值都放行」, 那太宽, 已收紧★** ★ | ★**反向用例 ⑭ (★改台账最新一条的后值 ⇒ D5 红 ⇒ 证明不是写死★) + ⑮ (★台账末尾追加更新的落表记录 ⇒ D5 仍绿 ⇒ 证明下一轮落表不会假红★)** ★ |
| ★**5** ★ | ★**其它一切照任务书走 (★交卷单 B1~B6 全填 + 闸 rc=0 + selftest ≥6 + preflight P5/P6 收口 + 分片 frag_write + grep★) ★** ★ | ★**全部照做 (★B1~B6 + 附 A/B/C 全填, 0 待填 · 闸 rc=0 · selftest 15/15 · preflight rc=0 (P5/P6 收口) · 分片走 `frag_write.py` 原子写 + grep 校验 + 别 agent 分片 md5 前后逐字节相同★)★** ★ | ★**见 B3.1 rc 汇总表** ★ |

## ★B2 · 边界自证 + 验收标准自评 (★逐条 通过/不通过/未验★)

### ★B2.1 · 边界逐条自证 (★任务书 §④ 8 条, 全部本机实测★)★

| # | 边界 | ★本机实测证据 (★2026-11-17 11:2x★)★ | 判定 |
|---|---|---|---|
| ★**1** ★ | ★**零写板** ★ | ★**板 md5 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17` (★`stat` 实测, 与起跑基线逐字一致★)★** ★ | ★**通过** ★ |
| ★**2** ★ | ★**零跑布线臂 / 零跑生成器** ★ | ★**本单全程只跑: 只读解析器 (本闸自带的纯 python 板面解析 + 只读 md5/stat/read) + 既有只读检查脚本 ⇒ ★**没跑 `state/gen_pcb_routing.py` / `state/gen_pcb_netlist_board.py` / `state/gen_production_pack.sh` / `state/gen_netlist.py` 一行★** ⇒ ★**板 md5 至今仍是起跑值 (★上条实测★)★** ★ | ★**通过** ★ |
| ★**3** ★ | ★**零落表** ★ | ★**没动网表 / 脚表 / BOM / `.kicad_pro` (★四个 md5 与 09:58:16 落表后的值逐字一致, 本单一个字节没改★)★** | ★**通过** ★ |
| ★**4** ★ | ★**零改既有判据阈值** ★ | ★**本单改的既有文件只有 3 个, 且都不是「判据阈值」: (a) `HW/check_onepass_preflight_coverage.py` = ★**只把 P6 的 3 个 md5 基线常量挪到落表后真值 + 加台账出处注释 (★判据方向不变, 仍是逐字节相等★)★** · (b) `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` = ★**只改 2 条 `current_state` (P5) + 1 处已过期的括号注释 (★判据命令没动★)★** · (c) `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` = ★**追加 1 行 (★老字零删, diff 删除行数 = 0 实测★)★** ⇒ ★**0.45 / 0.395 / 1e-6 / 0.50 这几个判据阈值一个都没动★** ★ | ★**通过** ★ |
| ★**5** ★ | ★**零写别 agent 的分片** ★ | ★**只走 `python3 state/frag_write.py --agent hw-lead` 写 `state/fragments/hw.yaml` (★原子写★) ⇒ ★**`mech.yaml` / `sw.yaml` / `pm.yaml` 一个字节没动 (★md5 前后一致, 见 B3.4★)★** ⇒ ★**`MECH/` / `SW/` 的文件本单一个都没改 (★只读★)** ★ | ★**通过** ★ |
| ★**6** ★ | ★**零外发** ★ | ★**没发信 / 没询价 / 没采购 / 没联系任何供应商 ⇒ ★**实物 [实测] = 0 条★** ★ | ★**通过** ★ |
| ★**7** ★ | ★**实物 [实测] = 0 条** ★ | ★**本单所有数字都是【板面实测】(★脚本实跑只读板文件★) 或 【源码/规格实读】, 没有一条来自实物量测★** ★ | ★**通过** ★ |
| ★**8** ★ | ★**不替老板拍板** ★ | ★**§③ 第 3 条那个「名单制 vs 总数」的判据口径, 本单只登记成 need 给 main (★见 B4 / B5★), 一句没拍★** ⇒ ★**本单零新增待拍项** ★ | ★**通过** ★ |
| ★**附** ★ | ★**`PROJECT_TRACKER.md` §0 锁死表不许动** ★ | ★**本单没碰 `PROJECT_TRACKER.md` (★一个字节没动★)★** ★ | ★**通过** ★ |
| ★**附2** ★ | ★**不自签 issue_log** ★ | ★**没动 `state/issue_log.yaml` (★只跑只读的 `state/issue_check.py`★)★** ★ | ★**通过** ★ |

### ★B2.2 · 验收标准自评 (★任务书 §⑤ 逐条对照★)★

| # | 验收命令 | ★期望 (★任务书 09:5x 写的★)★ | ★实跑 (★11:2x★)★ | 判定 | ★根因 (★不是本单能收的, 就说清楚★)★ |
|---|---|---|---|---|---|
| A1 | `python3 HW/check_fsin_rootcause.py` | rc=0 (D1~D5 全绿) | ★**rc=0 · D1~D5 全绿** ★ | ★**通过** ★ | — |
| A2 | `python3 HW/check_fsin_rootcause.py --selftest` | rc=0 (反向用例 ≥6 全抓到) | ★**rc=0 · 15/15 全抓到 (★≥6 达标★)** ★ | ★**通过** ★ | — |
| A3 | `python3 HW/check_onepass_preflight_coverage.py` | rc=0 (既有闸不许被本单带红) | ★**rc=0 · P1~P6 全绿** ★ | ★**通过 (★本单收口★)** ★ | ★**首趟时红 (P5 清单过期 + P6 基线过期) ⇒ 本单按 main 11:0x 授权收口★** ★ |
| A4 | `python3 HW/check_onepass_commit_order.py` | rc=0 (既有闸) | ★**rc=1 · D0 红** ★ | ★**不通过 (★本单未修, 见下★)** ★ | ★**D0 = 「网表/脚表/BOM md5 逐字节不变 (零落表)」的硬基线 ⇒ ★**09:58:16 那次【已授权落表】把三个 CSV 的 md5 依法改了 ⇒ 这道闸的「零落表」前提当场过期** ⇒ ★**根因 = 落表后遗症, 与本单无关 (★本单没碰那三个 CSV★)⇒ 修法 = 把 `HW/check_onepass_commit_order.py` 的 `HARD_BASELINE` / `PROTECTED_5` 三个 md5 挪到落表后真值并引 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 L1270-L1272 (★与本单 A3 的 P6 同一处修法★)⇒ ★**本单【没动它】: 它不在本单授权范围 (★main 11:0x 只点名 A3★), 且 main 10:4x 已把落表后遗症追加进 ISS-283 ⇒ ★**登记成 need 给 main (B4/B5)★** ★ |
| A5 | `python3 HW/check_onepass_s10_manifest.py` | rc=0 (既有闸) | ★**rc=1 · M1 红 (清单不在盘上)** ★ | ★**不通过 (★结构性, 改判据也改不绿★)** ★ | ★**闸自己写着: 「这正是 ISS-281 的病灶本身」+ 「S10 那一趟 (`state/gen_production_pack.sh`) 生成了 `MANIFEST.md5` 之后, 本闸才会转绿」⇒ ★**绿的条件是【跑 S10 那一趟】, 那是「板只改一次」那一趟 (★本单零跑生成器★)⇒ ★**任何手改判据的做法都是造假, 本单不做★** ★ |
| A6 | `python3 MECH/check_onepass_mech_sync.py` | rc=0 (既有闸) | ★**rc=1 · M5 红 3 条** ★ | ★**不通过 (★文件在 `MECH/` = 别人的域, 本单只读★)** ★ | ★**M5 同样是「三个 CSV md5 ≠ 旧基线」的落表后遗症 ⇒ ★**修法 = `MECH/check_onepass_mech_sync.py` 里那三个基线挪到落表后真值并引台账 §16.2 ⇒ ★**但那是 `MECH/` 的文件, 本单纪律 = `MECH/` 只读 ⇒ 登记成 need 给 mech-lead (B4/B5)★** ★ |
| A7 | `python3 state/merge.py` | rc=0 | ★**rc=0 (★11:32:48★) · 产出 494 · 阻塞 43 (高危 33) · 未闭合需求 274 · 冲突 0** ★ | ★**通过** ★ | — |
| A8 | `python3 state/gate_check.py` | rc=0 (★Q1 18/18★) | ★**rc=0 · Q1 = 18/18 (★hw-lead 6/6, sw-lead 6/6, mech-lead 6/6★) · Q2 3/3 有证据分级 · Q6 硬件真源闸 ✔** ★ | ★**通过** ★ | — |
| A9 | `python3 state/issue_check.py` | rc=0 | ★**rc=0** ★ | ★**通过** ★ | — |
| A10 | `md5sum` 受保护 5 件 | ★`611b869e…` / `3e504d2b…` / `e06c1dd6…` / `287e7861…` / `94642d07…` 5/5 逐字节不变★ | ★**板 `611b869e…` ✔ · `.kicad_pro` `3e504d2b…` ✔ · 网表 `2f17650c…` · 脚表 `6ea65fec…` · BOM `ea5f4f58…`** ★ | ★**板与 `.kicad_pro` 2/2 逐字节不变 ✔ · 三个 CSV 是【09:58:16 授权落表后】的值 (★台账 §16.2 L1270-L1272 登记★), 本单未改 (★不是「变了」, 是【基线过期】★)** ★ | ★**板侧 2/2 不变 ✔ (★「板只改一次」铁律本体✔★); CSV 3 件在【台账登记的落表后值】上, 非本单所改★** ★ |

★**★⇒ 结论: 9 条验收命令里 6 条 rc=0 (★含本单自己的两条闸 + main 点名要收口的 A3★), 3 条 rc=1 (★A4/A5/A6★) ⇒ ★**这 3 条红的根因全部【与本单无关】, 且【都不是本单能收的】(★A4 未获授权 + 归 ISS-283★ / A5 结构性等 S10 那一趟★ / A6 在 `MECH/` 别人的域★)⇒ ★**逐条给了可执行修法并登记成 need (★B4/B5★), 不代改也不装绿★** ★**

---

## ★B3 · 验收 rc (★本机实跑, 原样贴★) + 证据分级

### ★B3.1 · 验收命令 rc 汇总 (★2026-11-17 11:4x★)

| # | 命令 | rc | ★一句话★ |
|---|---|---|---|
| A1 | `python3 HW/check_fsin_rootcause.py` | ★**0** ★ | ★D1~D5 全绿★ |
| A2 | `python3 HW/check_fsin_rootcause.py --selftest` | ★**0** ★ | ★15/15 反向用例全抓到 (★中途有一次 rc=1 = `/tmp` 配额炸了 ★**闸自己跑挂**★ ⇒ 已修成【每条用例跑完立刻清沙盒】, 见 B1.2 第 4 行★)★ |
| A3 | `python3 HW/check_onepass_preflight_coverage.py` | ★**0** ★ | ★P1~P6 全绿 (★本单收口★)★ |
| A4 | `python3 HW/check_onepass_commit_order.py` | ★**1** ★ | ★D0 红 = 落表后遗症 (★未获授权, 归 ISS-283★)★ |
| A5 | `python3 HW/check_onepass_s10_manifest.py` | ★**1** ★ | ★M1 红 = S10 那一趟还没跑 (★结构性★)★ |
| A6 | `python3 MECH/check_onepass_mech_sync.py` | ★**1** ★ | ★M5 红 3 条 = 落表后遗症 (★`MECH/` 只读, 归 mech-lead★)★ |
| A7 | `python3 state/merge.py` | ★**0** ★ | ★快照刷新成功★ |
| A8 | `python3 state/gate_check.py` | ★**0** ★ | ★Q1 = 18/18 ✔★ |
| A9 | `python3 state/issue_check.py` | ★**0** ★ | ★问题闭环门全过★ |
| A10 | `md5sum` 受保护 5 件 | ★**—** ★ | ★板/`.kicad_pro` 2/2 逐字节不变; CSV 3 件 = 台账 §16.2 登记的落表后值★ |

### ★B3.2 · 原样输出 (★节选关键行, 完整输出见附 C★)★

```
$ python3 HW/check_fsin_rootcause.py
==============================================================================
  ISS-282 · `FSIN_OUT` 根因订正 + 布线前置闸 (★主模式 · root=/home/yuewuya/.openclaw/workspace/projects/smart_glasses★)
==============================================================================
  ✅ D1   ★订正页在盘 · 「逃逸方向」+「不成立」+「布线排队顺序」三个口径齐全 · 锚点块可解析 (9 项)★
  ✅ D2   ★重算: R_SER_FSIN→最近异网焊盘 1.300000 (R_SER_FSIN.2/FSIN) · TP_FSIN→最近异网焊盘 1.350000 (CONN_CAM.30/LIGHT_5V) · 两者 ≥ 源码阈值 0.45 ⇒ escape_stub 不适用 · 页上三个数与重算逐字一致★
  ✅ D3   ★重算: A→B 直线 L=3.0067 · 唯一挡路者=VDD_3V3_IO (seg (93.450,47.950)->(93.200,47.700) w=0.250) · 忽略它之后净距 0.4384 ≥ 判据 0.3950 · 忽略任何别的网都还是 FAIL ⇒ 页上结论可复现★
  ✅ D4   ★老 S8 行逐字仍在 (L387) · 订正行在其下 (L388) · 「不是板侧项 / 不需要动板 / 布线臂 env 配置 / 布线排队顺序 / VDD_3V3_IO / 划掉」六个口径齐全★
  ✅ D5   ★受保护 5 件逐字节未变 (板/`.kicad_pro` 硬钉 + 网表/脚表/BOM 有出处) ★ · 板 md5/mtime 未变 · .kicad_pro md5 未变 · netlist_v1.csv = 2f17650c (出处: 落表台账「前后对照」L1270) · netlist_v1_pins.csv = 6ea65fec (出处: 落表台账「前后对照」L1271) · BOM_v1.csv = ea5f4f58 (出处: 落表台账「前后对照」L1272)
------------------------------------------------------------------------------
  ⇒ 0 项不通过
==============================================================================
RC=0
```

```
$ python3 HW/check_fsin_rootcause.py --selftest
==============================================================================
  ISS-282 · `FSIN_OUT` 根因订正闸 · ★--selftest 反向用例 (15 条)★
==============================================================================
  ✅ ① 订正页把「布线排队顺序」口径删掉 ⇒ D1 红
  ✅ ② 把 D2 的 0.45 阈值改成 1.50 ⇒ D2 红
  ✅ ③ 把 D3 忽略的网名从 VDD_3V3_IO 改成 V_SOC_IO ⇒ D3 红
  ✅ ④ 把作业包老 S8 行删掉 ⇒ D4 红
  ✅ ⑤ 把订正行里的「不是板侧项」删掉 ⇒ D4 红
  ✅ ⑥ 改受保护件 (板) ⇒ D5 红
  ✅ ⑦ 改受保护件 (网表 CSV · 无落表出处) ⇒ D5 红
  ✅ ⑧ 订正页把页上的 d_a 改成 1.150000 ⇒ D2 红 (页 ≠ 盘面)
  ✅ ⑨ 订正页把「逃逸方向」口径写坏 ⇒ D1 红
  ✅ ⑩ 正向对照: 沙盒原样不动 ⇒ rc=0 (★证明闸不是恒红★)
  ✅ ⑪ 订正页把 blocker_d 改成 0.500000 ⇒ D3 红 (页 ≠ 盘面)
  ✅ ⑫ 拿掉落表台账 ⇒ D5 红 (★无出处的落表值不许默认放行★)
  ✅ ⑬ 锚点把「位号.脚号」整串塞回 pad_a ⇒ D2 红 (★锚点契约破了★)
  ✅ ⑭ 落表台账最新一条的后值被改 ⇒ D5 红 (★闸是读台账的, 不是写死三个值★)
  ✅ ⑮ 台账末尾追加更新的落表记录 ⇒ D5 仍绿 (★取最新一条 ⇒ 下一轮落表自动跟上★)
------------------------------------------------------------------------------
  ⇒ 15/15 条反向用例全部符合预期
==============================================================================
RC=0
```

★**★反向用例 ⑨ 是本趟修的 (★首趟那条是【空转的】: 它把「逃逸方向」替换成「逃逸方向XX」⇒ 子串还在 ⇒ D1 照样绿 ⇒ 那条用例【根本抓不到任何东西】★) ⇒ ★**本趟改成真正把口径写坏 (「逃逸方向」→「出脚方向」) ⇒ 抓到了★** ★

```
$ python3 HW/check_onepass_preflight_coverage.py
  OK   P1  条目 31 条 · 9 字段齐全且非空: ✔
  OK   P2  步覆盖: S1=1 S2=3 S3=2 S4=3 S5=1 S6=9 S7=2 S8=1 S9=1 S10=5 S11=1 S12=1 S13=1
  OK   P3  每条 criterion 的脚本文件都在盘上: ✔
  OK   P4  覆盖度: 26 个标记全部在清单里: ✔
  OK   P5  5 个现状探针: 清单里的现状值 == 盘面实测: ✔
  OK   P6  受保护 5 件 md5 逐字节不变: ✔
  ✅ rc=0: ★★板侧项全集与作业包对齐, 现状值与盘面一致 ★★
RC=0
```

```
$ python3 HW/check_onepass_commit_order.py
  ❌ D0   权威页存在且 INV-1~INV-4 齐全 · 网表 md5 = 2f17650cfbef48d5efd71821505c3343 ≠ 基线 e06c1dd633566aa44732762c2ff99d1c ⇒ 落表了 (零落表被破) · 脚表 md5 = 6ea65fecdf95902e47330083d140d455 ≠ 基线 287e7861a0d1007748d92d9fbecdd490 ⇒ 落表了 (零落表被破) · BOM md5 = ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd ≠ 基线 94642d07a69e8d60dd2af57f69b93607 ⇒ 落表了 (零落表被破)
  ✅ D1 ~ ✅ D6 (全绿)
  ❌ 1 项不通过
RC=1        ★★根因 = 09:58:16 授权落表的后遗症; 「零落表」前提过期; 修法见 B2.2 A4★

$ python3 HW/check_onepass_s10_manifest.py
  ❌ M1   ★清单文件不在盘上: .../HW/PCB/production/MANIFEST.md5 ⇒ ★**S10 那一趟还没生成清单 (★这正是 ISS-281 的病灶本身★)**
  ⏭  M2 / M3 / M4 不可判定 (依赖 M1)
  ❌ 1 项不通过
RC=1        ★★结构性: 绿的条件是跑 S10 那一趟; 本单零跑生成器 ⇒ 不造假★

$ python3 MECH/check_onepass_mech_sync.py
  ✗ M5 受保护件被改: HW/netlist_v1.csv 基线 e06c1dd633566aa44732762c2ff99d1c ⇒ 现值 2f17650cfbef48d5efd71821505c3343
  ✗ M5 受保护件被改: HW/netlist_v1_pins.csv 基线 287e7861a0d1007748d92d9fbecdd490 ⇒ 现值 6ea65fecdf95902e47330083d140d455
  ✗ M5 受保护件被改: HW/BOM_v1.csv 基线 94642d07a69e8d60dd2af57f69b93607 ⇒ 现值 ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd
  【红】3 条
RC=1        ★★根因 = 同一处落表后遗症; 文件在 MECH/ (别人的域) ⇒ 本单只读, 归 mech-lead★

$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-17T11:32:48+08:00)
   产出 494 | 阻塞 43 (高危 33) | 未闭合需求 274 | 冲突 0 | 健康度 red
RC=0

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-17_hw-lead_ISS282_FSIN_OUT根因订正.md
   sw-lead    6/6  缺: 无   mech-lead  6/6  缺: 无
【Q2 证据分级率】 3/3 个总工的交付做了证据分级
【Q3 接口声明率】 全员 interface_claims 共 807 条
【Q4 需求闭环率】 ...
【Q5 硬指标覆盖】 0/3 个总工报出了 ≥3 类硬指标数字
【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
RC=0

$ python3 state/issue_check.py
✅ 问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖)
RC=0
```

### ★B3.3 · ★★作业包追加式订正的 diff 实测 (★删除行数必须 = 0★)★★

★**★基线取【ISS-282 之前盘上就有的快照】`/tmp/iss279_sandbox2/HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (★2026-11-17 08:33:11 ★★435 行 / md5 `61566cfc7ee8ba5621e8cb28048337cd`★) ⇒ 跟现盘 (★458 行 / md5 `fa76c17fcff2af069844e0d5abeb3c17`★) 实测 diff★**

```
$ diff -u /tmp/iss279_sandbox2/HW/PCB/BOARD_ONEPASS_WORKPACKET.md \
         HW/PCB/BOARD_ONEPASS_WORKPACKET.md > /tmp/iss282_wp_diff.txt
$ echo "删除行数 = $(grep '^-' /tmp/iss282_wp_diff.txt | grep -vc '^---')"
删除行数 = 0
$ echo "新增行数 = $(grep '^+' /tmp/iss282_wp_diff.txt | grep -vc '^+++')"
新增行数 = 23
$ grep '^@@' /tmp/iss282_wp_diff.txt
@@ -246,6 +246,28 @@      ★= ISS-281 的 §S10.1 追加块 (22 行)★
@@ -363,6 +385,7 @@      ★= ISS-282 的 §6.2 订正行 (1 行)★
```

★**★⇒ 删除行数 = 0 ⇒ 「追加式」成立 (★ISS-281 那块也是追加, 一样 0 删除★)★** ★

★**★老 S8 行逐字未删的硬证 (★两版同一行 cmp 逐字节相同★)★**:

```
$ sed -n '365p' /tmp/iss279_sandbox2/HW/PCB/BOARD_ONEPASS_WORKPACKET.md > /tmp/a.txt   ★老 S8 行★
$ sed -n '387p' HW/PCB/BOARD_ONEPASS_WORKPACKET.md                        > /tmp/b.txt   ★现盘老 S8 行★
$ cmp /tmp/a.txt /tmp/b.txt && echo "逐字节相同 ✔"
逐字节相同 ✔
$ md5sum /tmp/a.txt /tmp/b.txt
f1e201820ad8448606ec61d8dd4add3e  /tmp/a.txt
f1e201820ad8448606ec61d8dd4add3e  /tmp/b.txt
$ grep -c '^| ★\*\*S8\*\* ★ | ... 疑似逃逸方向 bug ... |$' HW/PCB/BOARD_ONEPASS_WORKPACKET.md
1        ★= 老 S8 行在现盘里逐字存在, 且只有 1 条 (没被复制成两条)★
```

### ★B3.4 · 受保护件 md5 (★跑前跑后逐字节不变★) + 别 agent 分片 md5 (★证明没碰★)★

```
$ md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
         HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb      ★= 起跑基线 ✔ 未变★
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro      ★= 起跑基线 ✔ 未变★
2f17650cfbef48d5efd71821505c3343  HW/netlist_v1.csv                    ★= 09:58:16 授权落表后值 (台账 L1270)★
6ea65fecdf95902e47330083d140d455  HW/netlist_v1_pins.csv               ★= 09:58:16 授权落表后值 (台账 L1271)★
ea5f4f58e3fb8bb7b6c3a2e0de8b1dfd  HW/BOM_v1.csv                       ★= 09:58:16 授权落表后值 (台账 L1272)★
$ stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
2026-11-06 07:07:17.362193413 +0800                                    ★= 起跑 mtime ✔ 未变★
```

```
$ md5sum state/fragments/mech.yaml state/fragments/sw.yaml state/fragments/pm.yaml
★三个都是【本单跑前跑后逐字节相同】(★本单只写了 hw.yaml★)
```

### ★B3.5 · 证据分级 (★[实测] / [推算] / [0数据] / [官方]★)★

| 证据 | 内容 | 分级 | 出处 |
|---|---|---|---|
| ★**E1** ★ | ★`R_SER_FSIN.1` = 1.300000 mm · `TP_FSIN.1` = 1.350000 mm (★到最近异网焊盘外接矩形边缘★) ★ | ★**[实测]** ★ | ★**本单本机实跑 (闸自带的只读解析器 + `--dump` 输出)★** ★ |
| ★**E2** ★ | ★`escape_stub` 阈值 0.45 / 净距判据 0.395 (★= 0.125 + 0.20 + 0.07★) ★ | ★**[实测]** ★ | ★**源码实读 + 规格实读 (★闸自己正则读出来, 不写死★)★** ★ |
| ★**E3** ★ | ★逐网忽略法: 唯一挡路者 `VDD_3V3_IO`, 忽略后 D = 0.438361 ≥ 0.395 ⇒ PASS; 忽略任何别的网都 FAIL (D = −0.1250) ★ | ★**[实测]** ★ | ★**本单本机实跑 (看板面铜 + 算几何)★** ★ |
| ★**E4** ★ | ★队列顺序: `VDD_3V3_IO` 在 `POWER_NETS` (第 2 步) · `FSIN_OUT` 三张表都没有 ⇒ 第 4 步 ★ | ★**[实测]** ★ | ★**源码实读 (`state/gen_pcb_routing.py` 行号逐个可复核)★** ★ |
| ★**E5** ★ | ★`FSIN_OUT` 在现役板上铜件数 = 0 (★整网无铜★) ★ | ★**[实测]** ★ | ★**本单本机实跑 (板面铜统计)★** ★ |
| ★**E6** ★ | ★沙盒 DRC (pristine 0/45 → 手工布线 18 违规 / unc 44) ★ | ★**[引用·main 实测]** ★ | ★**main 本机实跑 (★本单零复跑, 零跑 DRC, 零写板★)★** ★ |
| ★**E7** ★ | ★4 层 A\* `NO ROUTE FOUND` = 假阴性 (★现状铜已占★) ★ | ★**[引用·main 实测] + [实测·本单的解释]** ★ | ★**main 实跑 A\* + 本单实测「那条铜真的穿过直线」★** ★ |
| ★**E8** ★ | ★`PCB_PRIORITY_NETS` 让 `FSIN_OUT` 一次就通 (L=3.0mm) ★ | ★**[引用·历史实测]** ★ | ★**`state/LANE_CONFLICT_WORKLIST.md` L260 逐字★** ★ |
| ★**E9** ★ | ★板 md5 / `.kicad_pro` md5 / mtime 逐字节未变 ★ | ★**[实测]** ★ | ★**md5sum + stat★** ★ |
| ★**E10** ★ | ★三个 CSV 的落表后 md5 与出处行号 (L1270/L1271/L1272) ★ | ★**[实测]** ★ | ★**md5sum + 落表台账实读★** ★ |
| ★**E11** ★ | ★P5 两条现状实测值 (「零标记 40 颗」/「18 条缺陷」) ★ | ★**[实测]** ★ | ★**本单本机实跑两个既有检查脚本★** ★ |
| ★**E12** ★ | ★「18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账」★ | ★**[实测]** ★ | ★**本单实跑 `HW/check_pin_function_labels.py` + 数缺陷类型条数★** ★ |
| ★**E13** ★ | ★一切实物尺寸 / 高度 / 光学 ★ | ★**[0数据]** ★ | ★**本单零实物量测, 零外发 ⇒ 一条实物 [实测] 都没有★** ★ |
| ★**E15** ★ | ★锚点契约 (★`pad_a` + `pad_a_num` 分开写, 闸不许猜脚号★) 与「契约破了要显式红」★ | ★**[实测]** ★ | ★**反向用例 ⑬ 实跑: 把点分写法塞回 `pad_a` ⇒ D2 红且报「契约破了」★** ★ |
| ★**E17** ★ | ★`--selftest` 跑完沙盒残留 = 0 + 峰值占用 ~5.7 MB (★`/tmp` 带 usrquota★) ★ | ★**[实测]** ★ | ★**本单本机实跑 (★`ls -d /tmp/iss282_selftest_* | wc -l` = 0★)★** ★ |
| ★**E16** ★ | ★D5 允许集合 = 【MD5 台账基线】∪【落表台账最新一条落表记录】(★一行都不写死★) ★ | ★**[实测]** ★ | ★**反向用例 ⑭ (★改台账最新一条 ⇒ D5 红⇒ 证明不是写死★) + ⑮ (★台账末尾追加更新的记录 ⇒ D5 仍绿⇒ 证明下一轮落表不假红★)★** ★ |
| ★**E14** ★ | ★器件官方 pinout / 封装 ★ | ★**[官方]** ★ | ★**本单未引用任何新器件官方资料 (★不落表, 不查料★) ⇒ 这条是范围外的既有引用, 本单没动★** ★ |

---

## ★B4 · 接口取值声明 (interface_claims) + claim / artifact / need / status (★分片★)

★**★分片写入方式 (★协议强制★): `python3 state/frag_write.py --agent hw-lead` (★原子写★) ⇒ ★**写完必须 grep 校验 (★并发写会 lost-update★)★** ★

```
$ python3 state/frag_write.py --agent hw-lead \
    --add-artifact 'path=HW/PCB/FSIN_OUT_ROOTCAUSE.md kind=spec summary=FSIN_OUT 根因订正页: 逃逸方向 bug 不成立 ⇒ 订正为布线排队顺序 (第2步电源网 VDD_3V3_IO 先占走廊); 八个必含项齐全 + 机器可读锚点块' \
    --add-artifact 'path=HW/check_fsin_rootcause.py kind=gate summary=ISS-282 机器闸 D1~D5 + --selftest 15/15 (D1 页双口径/D2 escape_stub判据实算+锚点契约 pad_a+pad_a_num/D3 逐网忽略法实算/D4 作业包追加式订正/D5 受保护5件 md5=基线∪落表台账最新一条落表记录)' \
    --add-artifact 'path=HW/PCB/BOARD_ONEPASS_WORKPACKET.md kind=workpacket-summary summary=§6.2 S8 行下面追加 ISS-282 订正行 (老字零删, diff 删除行数=0): FSIN_OUT 不是板侧项/不需要动板/挪到布线臂 env 配置' \
    --add-artifact 'path=HANDOFF/2026-11-17_hw-lead_ISS282_FSIN_OUT根因订正.md kind=handoff summary=ISS-282 交卷单 B0~B6 + 附 A/B/C 全填 + 9 条验收命令逐条 rc' \
    --add-claim 'key=iss282_fsin_out_rootcause value=布线排队顺序 note=VDD_3V3_IO 第2步电源网先占走廊; escape_stub 不适用 (1.30/1.35 ≫ 0.45); 唯一挡路者实测 D=0.438361 ≥ 0.395' \
    --add-claim 'key=iss282_fsin_out_not_board_side value=不需要动板 note=划掉的是「要改板」不是「布不通」; 挪到布线臂 env PCB_PRIORITY_NETS; 板只改一次铁律不受影响' \
    --add-need 'key=iss282_commit_order_d0_baseline_after_landing to=main item=HW/check_onepass_commit_order.py 的 HARD_BASELINE/PROTECTED_5 三个 CSV md5 挪到落表后真值 (2f17650c/6ea65fec/ea5f4f58) 并引 HW/SCHEMATIC_LANDING_V1_LANDED.md §16.2 L1270-L1272 ⇒ 现在 D0 红 (零落表前提过期) ⇒ 本单未获授权故未动 since=2026-11-17' \
    --add-need 'key=iss282_mech_sync_m5_baseline_after_landing to=mech-lead item=MECH/check_onepass_mech_sync.py 的 M5 三个 CSV 基线挪到落表后真值并引台账 §16.2 L1270-L1272 ⇒ 现在 M5 红 3 条 ⇒ 文件在 MECH/ 域, 本单只读未动 since=2026-11-17' \
    --add-need 'key=iss282_unc_judgement_by_name_list to=main item=那一趟的 unc→0 判据按名单制 (哪些网通了/哪些网死了), 不许只看总数 (走廊零和: 优先布给 FSIN_OUT 会挤掉差分主干, 实测 v76p1 臂 unc 46→47) ⇒ 本单只登记, 不代拍 since=2026-11-17' \
    --status 'phase=P1 progress_pct=100 health=yellow summary=ISS-282 交卷: 根因订正页+作业包追加式订正+机器闸(D1~D5 全绿, selftest 15/15)+交卷单+分片; 零写板零落表零跑布线臂; 顺手收口 A3 preflight 闸 ⇒ rc=0; 验收 9 条 6 绿 3 红 (A4/A5/A6 根因与本单无关, 已登记 need)'
$ echo "rc=$?"
```

★★**★11:3x 补充一步 (★main 11:0x 补充实测之后回头修闸, artifact/status 的摘要要跟着改★)★★**: ★**`--add-artifact` 是【追加】不是【改】⇒ 再跑一次会多出一条同 path 的重复条目 ⇒ ★**所以这轮改用 `state/frag_write.py` 的 Python API (`update_fragment`) 原地改摘要 (★协议文档明确允许, 同样是原子写★)★**:

```python
import sys; sys.path.insert(0, "state")
from frag_write import update_fragment
update_fragment("hw-lead", lambda d: (
    [a.__setitem__("summary", ...) for a in d.get("artifacts", []) if a.get("path") == "HW/check_fsin_rootcause.py"],
    d.get("status", {}).__setitem__("summary", ...)))
```

★**★校验: `grep -c "path: HW/check_fsin_rootcause.py" state/fragments/hw.yaml` = 1 (★无重复条目★)★** ★

★**★分片 grep 校验 (★原子写完必须校验★)★**:

```
$ grep -n "iss282_fsin_out_rootcause\|iss282_fsin_out_not_board_side\|iss282_commit_order_d0_baseline_after_landing\|iss282_mech_sync_m5_baseline_after_landing\|iss282_unc_judgement_by_name_list" state/fragments/hw.yaml
★5 条 key 全部在盘 (★逐条行号见附 C★)★
$ grep -n "FSIN_OUT_ROOTCAUSE.md\|check_fsin_rootcause.py\|ISS282_FSIN_OUT根因订正.md" state/fragments/hw.yaml
★artifact 全部在盘★
$ python3 state/merge.py     ⇒ rc=0
```

★**★B4.1 · 本单没有自签 issue_log (★`state/issue_log.yaml` 一个字节没动★) ⇒ 本单的状态只落在 `state/fragments/hw.yaml` 里, 等 main 复验后由 main 落 verified★** ★

---

## ★B5 · 未决项与卡点 (★需要谁回答什么★)

| # | 未决项 | ★要谁回答什么★ | ★状态★ |
|---|---|---|---|
| ★**1** ★ | ★**A4 `HW/check_onepass_commit_order.py` D0 红 (★零落表硬基线 vs 09:58:16 授权落表后的值★)** ★ | ★**main: 要不要把它的三个 md5 基线挪到落表后真值 (★与本单给 P6 的修法完全一致★)? 或按 ISS-283 一起处理?** ★ | ★**need 已登记 (`iss282_commit_order_d0_baseline_after_landing` → main) · 本单未动它 (未获授权)★** ★ |
| ★**2** ★ | ★**A6 `MECH/check_onepass_mech_sync.py` M5 红 3 条 (★同一处落表后遗症★)** ★ | ★**mech-lead: 把 M5 的三个基线挪到落表后真值 + 引台账 §16.2 L1270-L1272** ★ | ★**need 已登记 (`iss282_mech_sync_m5_baseline_after_landing` → mech-lead) · 文件在 `MECH/` 域, 本单只读未动★** ★ |
| ★**3** ★ | ★**A5 `HW/check_onepass_s10_manifest.py` M1 红 (★`MANIFEST.md5` 不在盘★)** ★ | ★**main: 这是 S10 那一趟的产物, 跑那一趟就绿 ⇒ 本单零跑生成器 ⇒ 不造假★** | ★**结构性, 无需本单动作 (★闸自己写着「这正是 ISS-281 的病灶本身」★)★** ★ |
| ★**4** ★ | ★**★「那一趟的 unc→0 判据按名单制」的口径★** ★ | ★**main 排期 (★或另开一单★): 给 `FSIN_OUT` 提前不会自动让整板 unc 变小 ⇒ 判据必须按名单制看 (★哪些网通了 / 哪些网死了★)** ★ | ★**need 已登记 (`iss282_unc_judgement_by_name_list` → main) · ★**本单不代拍** ★** ★ |
| ★**5** ★ | ★**`HW/check_pin_function_labels.py` 的 `KNOWN_DEFECTS` 快照过期 (★实算 18 vs 快照 15 ⇒ `--expect-known` rc=1★)** ★ | ★**main (★归 ISS-283★): 落表后要把冻结快照同步到 18 条 (★或按「md5 台账对账不计入缺陷」的语义改口径★)** ★ | ★**已登记给 main (★同属落表后遗症★) · ★**本单没改那个脚本 (★不在本单授权范围, 且它自己有 9 条反向用例在保 fail-closed★)★** ★ |
| ★**6** ★ | ★**ISS-265 历史交卷单 §6 桶B-26 那句「逃逸方向 bug (两者竖直对齐, 逃逸口互挡)」还留在盘上** ★ | ★**main: 要不要回写? (★本单只订正了作业包 §6.2, 历史交卷单按任务书不动★)** ★ | ★**已登记 (★页 §1 ② 逐字留痕, 指向那一句★)★** ★ |
| ★**7** ★ | ★**本单零新增待拍项 ⇒ 不用问老板★** ★ | ★**—** ★ | ★**✔** ★ |

---

## ★B6 · 自证复现命令 (★一条一条复制粘贴, ★全部本机实跑过★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ── 本单自己的闸 (★D1~D5 + 反向用例★) ──
python3 HW/check_fsin_rootcause.py                # ⇒ rc=0 · D1~D5 全绿
python3 HW/check_fsin_rootcause.py --selftest     # ⇒ rc=0 · 15/15 反向用例全抓到
python3 HW/check_fsin_rootcause.py --dump         # ⇒ rc=0 · 打印 D2/D3 的实测表 (1.300000 / 1.350000 / 0.438361)

# ── 既有闸 (★A3 本单收口; A4/A5/A6 根因与本单无关, 见 B2.2★) ──
python3 HW/check_onepass_preflight_coverage.py          # ⇒ rc=0  ★本单收口★
python3 HW/check_onepass_preflight_coverage.py --selftest # ⇒ rc=0 · 8/8
python3 HW/check_onepass_commit_order.py                # ⇒ rc=1 · D0 (落表后遗症)
python3 HW/check_onepass_s10_manifest.py                # ⇒ rc=1 · M1 (S10 未跑)
python3 MECH/check_onepass_mech_sync.py                 # ⇒ rc=1 · M5×3 (落表后遗症)

# ── 状态链 ──
python3 state/merge.py                                  # ⇒ rc=0
python3 state/gate_check.py                             # ⇒ rc=0 · Q1 18/18
python3 state/issue_check.py                            # ⇒ rc=0

# ── 受保护 5 件 (★板只改一次铁律本体★) ──
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb             # ⇒ 2026-11-06 07:07:17 (起跑 mtime)

# ── 作业包追加式订正 (★删除行数必须 = 0★) ──
diff -u /tmp/iss279_sandbox2/HW/PCB/BOARD_ONEPASS_WORKPACKET.md \
         HW/PCB/BOARD_ONEPASS_WORKPACKET.md | grep -c '^-[^-]'   # ⇒ 0
sed -n '387p' HW/PCB/BOARD_ONEPASS_WORKPACKET.md | md5sum         # ⇒ f1e201820ad8448606ec61d8dd4add3e (老 S8 行)

# ── 分片 (★原子写 + grep 校验★) ──
grep -n "iss282_" state/fragments/hw.yaml
```

---

## ★附 A · 回答 main 的三句话

> ★**① 「这一趟你要交什么?」**
>
> ★**四件: (a) 根因订正页 `HW/PCB/FSIN_OUT_ROOTCAUSE.md` (★八个必含项齐全 + 机器可读锚点块 11 项★) · (b) 作业包 §6.2 的追加式订正行 (★老 S8 行逐字零删, diff 删除行数 = 0 实测★) · (c) 机器闸 `HW/check_fsin_rootcause.py` (★D1~D5 全绿 + `--selftest` 15/15★) · (d) 本交卷单 + `state/fragments/hw.yaml` 分片 (★原子写 + grep 校验★) ⇒ ★**外加顺手收口了 main 点名的 A3 (preflight 闸) ⇒ rc=0★** ★

> ★**② 「`FSIN_OUT` 到底是不是逃逸方向 bug?」**
>
> ★**不是。★** ★**两个焊盘到最近异网焊盘外接矩形边缘的距离 = 1.300000 / 1.350000 mm (★这个量【就是路由器 `_nearest_other_pad()` 判 escape_stub 用的那个量】, 它既不是「中心距」也不是「边到边距」★), 阈值 0.45 (★路由器源码 L2089 实读★) ⇒ ⇒ 压根不进 `escape_stub()` 分支 ⇒ ⇒ 「逃逸方向」四个字跟这件事无关。★** ★**真根因 = 【布线排队顺序】: `VDD_3V3_IO` 是电源网 (★第 2 步布★), `FSIN_OUT` 落到第 4 步 ⇒ 后挑走廊只剩那条被压死的窄缝 (★逐网忽略法实跑: 只忽略 `VDD_3V3_IO` ⇒ D = 0.438361 ≥ 0.395 ⇒ 过; 忽略任何别的网都还是 FAIL★)★** ★**

> ★**③ 「那老板那一趟要拍的东西变没变?」**
>
> ★**变少了一条, 但那条没消失, 只是换了归属。★** ★**① `FSIN_OUT` 从「会改板」名单里划掉 ⇒ 【不需要动板】⇒ 「板只改一次」铁律不受影响 · ② 「布线 45→0」那一趟仍然必须把它布通, 而布通它靠的是布线臂 env `PCB_PRIORITY_NETS` (★不是改板★) ⇒ 归 hw-lead + 路由器作者 · ③ ★**但走廊是零和的 ⇒ 给 `FSIN_OUT` 提前不会自动让整板 unc 变小 ⇒ 那一趟的「unc→0」判据必须按名单制看 (★哪些网通了 / 哪些网死了★), 不许只看总数★ ⇒ ★**这是老板那一趟的判据口径问题 ⇒ 交 main 排期, 本单一句没拍★** ★** ★**

---

## ★附 B · 沙盒路径清单 (★全部在 /tmp, 真盘零写★)

| 路径 | 用途 | 生命周期 |
|---|---|---|
| ★`/tmp/iss282_selftest_<随机>` ★ | ★**机器闸 `--selftest` 的 15 条反向用例沙盒 (★每个用例一份最小镜像: 板 + `.kicad_pro` + 3 个 CSV + 订正页 + 作业包 + 两个台账 + 路由器源码 + 净距规格★)** ★ | ★**函数退出时 `shutil.rmtree` 自动删除 (★实跑后盘上无残留★)★** |
| ★`/tmp/iss279_sandbox2/HW/PCB/BOARD_ONEPASS_WORKPACKET.md` ★ | ★**diff 基线 (★ISS-282 之前盘上就有的快照, 08:33:11 ★★不是本单造的★★)★** ⇒ 用它证明「追加式 ⇒ 删除行数 = 0」★ | ★**只读引用, 本单没动它★** |
| ★`/tmp/iss282_wp_diff.txt` ★ | ★**diff 输出留痕 (★B3.3 贴的就是它★)** ★ | ★**本单生成★** |
| ★`/tmp/a.txt` `/tmp/b.txt` ★ | ★**老 S8 行两版的单行副本 (★`cmp` 逐字节同证★)** ★ | ★**本单生成★** |

★**★⇒ 本单全程没在真盘上跑过任何生成器/布线臂 ⇒ ★**沙盒只用来跑反向用例, 真盘一个字节没写 (★除了本单自己的 5 个交付物 + 被授权的 A3 收口那 2 个文件★)★** ★

---

## ★附 C · 本单实测原始输出样例

### ★C.1 · `--dump` 的 D2/D3 实测表 (★前 12 行 + 尾部 4 行, 中间 300+ 个网全 FAIL 那段略★)★

```
=== D2 · escape_stub 判据实测 (阈值取自路由器源码) ===
  阈值 (源码) = 0.45 mm
  R_SER_FSIN.1   center=(93.300000,46.600000)  最近异网焊盘 = 1.300000 mm  by R_SER_FSIN.2/FSIN   不进 escape_stub
  TP_FSIN.1      center=(93.500000,49.600000)  最近异网焊盘 = 1.350000 mm  by CONN_CAM.30/LIGHT_5V   不进 escape_stub

=== D3 · 逐网忽略法实测 (A→B 直线 L=3.0067, 判据 0.3950) ===
  忽略的网             净距 D       判定       挡路者
  VDD_3V3_IO       0.4384     PASS     seg (93.450,47.950)->(93.200,47.700) w=0.250
  LIGHT_3V3        -0.1250    FAIL     via @(92.700,48.700) dia=0.600
  FSIN             -0.1250    FAIL     pad R_SER_FSIN.2
  LIGHT_5V         -0.1250    FAIL     pad CONN_CAM.30
  ... (其余 300+ 个网全部 FAIL, ★因为 `VDD_3V3_IO` 那条铜原地不动地穿过直线★)

  ⇒ 唯一挡路者 = VDD_3V3_IO (seg (93.450,47.950)->(93.200,47.700) w=0.250)
  ⇒ 忽略它之后净距 = 0.4384 ≥ 0.3950 ⇒ PASS
  ⇒ 忽略任何别的网都还是 FAIL

=== 现状 ===
  FSIN_OUT 铜件数 (走线+过孔) = 0 ⇒ 整网无铜
RC=0
```

### ★C.2 · 精确值 (★6 位小数, 与锚点块逐字一致★)★

```
blocker = VDD_3V3_IO   who = seg (93.450,47.950)->(93.200,47.700) w=0.250
blocker_d exact = 0.438361016814      ⇒ 锚点块写 0.438361 (★页正文 4 位小数显示 0.4384, 是同一个数不是两个口径★)
d_all      = -0.125000000000         ⇒ 不忽略任何网时穿铜 0.125 (= 半个线宽)
d_a = 1.300000   d_b = 1.350000   esc_threshold = 0.45   need = 0.395
```

### ★C.3 · P5 两条现状值的实测 (★本单改清单的依据★)★

```
$ python3 HW/check_netlist_contradiction_r3.py | grep 零标记
  R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗  ⇒ ❌ 红
        · 零标记的: 40
  ⇒ 清单旧值 (54 颗 / 43 颗 / 43 颗) 是落表前的 ⇒ 落表 V-3=E 删了 3 行 DNP ⇒ 三个数各减 3

$ python3 HW/check_pin_function_labels.py | grep 条缺陷
  判定: ❌ 不过 (18 条缺陷) ⇒ ★当前是已知缺陷基线, 落表批次里修★
  ⇒ 实算分解: WRONG_FUNCTION 14 条 + MISSING_PIN 1 条 + MD5_CHANGED 3 条 = 18
  ⇒ 脚表【功能】缺陷本批一条没变 (还是 14 串号 + 1 缺脚), 多出的 3 条全是【落表后 md5 基线过期】
```

### ★C.4 · 分片 grep 校验 (★B4 的实测输出★)★

```
$ grep -n "iss282_fsin_out_rootcause\|iss282_fsin_out_not_board_side\|iss282_commit_order_d0_baseline_after_landing\|iss282_mech_sync_m5_baseline_after_landing\|iss282_unc_judgement_by_name_list" state/fragments/hw.yaml
★5 条 key 全部在盘★
$ grep -n "FSIN_OUT_ROOTCAUSE.md\|check_fsin_rootcause.py\|ISS282_FSIN_OUT根因订正.md" state/fragments/hw.yaml
★artifact 全部在盘★
$ md5sum state/fragments/mech.yaml state/fragments/sw.yaml state/fragments/pm.yaml
★三个都与本单跑前逐字节相同 (★本单只写了 hw.yaml★)★
```

---

> ★**★交卷人**: 硬件总工 (hw-lead) · ★**交卷时刻**: 2026-11-17 11:32 (Asia/Shanghai) ★
> ★**★末次全量自检 (★2026-11-17 11:53, ★本文件最后一轮改完之后跑的最后一遍★)★**: ★**A1 rc=0 · A2 rc=0 (15/15) · A3 rc=0 · A4 rc=1 (落表后遗症) · A5 rc=1 (S10 未跑) · A6 rc=1 (落表后遗症) · A7 rc=0 · A8 rc=0 (Q1 18/18) · A9 rc=0 · A10 板/`.kicad_pro` 逐字节不变 + 3 个 CSV = 台账 §16.2 登记的落表后值** ★
> ★**★本单零新增待拍项 ⇒ 不用问老板 ⇒ 等 main 独立复验后落 verified★** ★
