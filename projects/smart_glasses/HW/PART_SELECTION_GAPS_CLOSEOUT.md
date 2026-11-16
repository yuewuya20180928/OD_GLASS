# ISS-241 选型缺口 (G-1~G-10) 逐条自查补全 + 22 件 OPN 回填清单 (ISS-244)

> 作者: sw-lead (软件总工) · 2026-11-16 · 交卷给 main / 项目总工  
> 上游: `HW/PART_SELECTION_MATRIX_2026-11-16.md` (ISS-241 矩阵, 本单**只引用不改**) · 本单零外发 · 实物 [实测] = 0 条  
> ★本文件由 `state/.cache_iss244/build_closout.py` 生成 —— 表与机器可读基准块同源, 不手改★

## §0 一句话

★ISS-241 登记的 10 条缺口 (G-1~G-10) **本轮逐条自查完毕**: 4 条重点缺口 (G-5 / G-3+G-4 / G-10 / G-1) 从「描述性缺口」升级成**带官方出处 + 可复跑算式 + 可量化代价**的条目; 6 条 (G-2/G-6/G-7/G-8/G-9) 写成「已转单 / 已闭合 + 出处」不重复论证。另交 **22 件 OPN 回填清单** (只出清单, 一字未落表)。★**本单不替老板拍任何一条** (V-2 / V-3 / V-4 / G-1 / G-10 / 亮度档 全部只出依据 + 代价)。

★**2026-11-17 05:0x 增补 (H-1 重锚第 1 跳)**: 板侧又落了 13 件 ⇒ ① 每行 `landed_note` 重算 ② **新增 §5 落表后回归**: 把「板占位 land ↔ 落地器件引脚序 ↔ 网表 note 端子角色」三方逐件交叉核对 ⇒ **查出 3 条实物级 P0** (① `Q_PG` 角色本身错 + land 不对 ⇒ 开机路径不通 ② `Q_AND` 栅/漏对调 ⇒ 复位链硬件 AND 门不成立 ③ `D_ESD_CAM` ESD 器件接反 ⇒ 保护失效 + CSI lane 被钳) ⇒ **每条都给了最小修法** (多是「两个外侧 pad 对调」) ⇒ ★**仍然只出依据 + 代价, 一件都没代拍**★。

## §1 口径与边界

- **范围**: 只交依据 + 清单。网表 / 脚表 / BOM **一个字未改**; ISS-241 矩阵正文与门禁脚本 **一个字未改**; 板 / 布线 / 布局未碰。
- **证据分级**: 只用 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 五级。
- **零外发**: 老板 2026-11-11 19:31 + 2026-11-12 02:02 政策 —— 本轮全部资料来自 web_search / web_fetch / 带 `--max-time` 的 curl + `pdftotext` 实读, **未发任何邮件 / 询价 / 问询 / 采购**。查不到的一律写 `[0数据]` + 降级方案, 不挂任何把结论悬在外部回函上的措辞。
- **件数控 (两个机器派生源, 都不抄硬编码数字)**: ① **登记范围** = ISS-241 矩阵基准块的 `expected_refs` = **22 件** (本单必须全覆盖); ② **当前仍待落** = `HW/BOM_v1.csv` 实跑「待选型∩必装 − 越界件」= **8 件**。两者不等的原因见下 (G-9)。
- ★**并发落表落地的实况 (最新一次实读: 2026-11-17 05:0x)**: 本单生成期间, `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 被落表批次改过 **两次** —— ① 2026-11-16 15:45 (`C_REGN`) ② 2026-11-16 22:25 (选型落表批次, 又落 13 件) ⇒ 登记范围 22 件里 **14 件已落表 / 8 件仍待落** ⇒ 已落表的件**不在 BOM 待选型集合里**, 但仍在 ISS-241 的登记范围内 ⇒ 本单清单**保留这些行**并标注「已落表 + 落表证据 (landed_note)」。★**本单门禁的 C5 就是按这个口径写的**: 登记范围内的一件被并发落掉而又不写落表证据 ⇒ **红** (锚点过期 ⇒ 红 ⇒ 走 H-1 重锚 + 留痕, 不许把红灯调没)。★**本轮已按 H-1 重锚第 1 跳处理** (见 §5)。
- **落表锚点**: 一律写 `ref + net` 这样的稳定锚点 + 当刻的行号; ★**行号会随落表漂移** ⇒ 落表时以 ref+net 为准★。

## §2 ★G-1~G-10 逐条自查结果 (一条不许少)

| # | 缺口 | 归谁 | 本轮自查结果 | 证据等级 | 出处 | 降级方案 | 还差什么 | 状态 |
|---|---|---|---|---|---|---|---|---|
| **G-1** | Q_PG 源漏拓扑: 网表 note 首句与 note 正文自述的「正解」自相矛盾 | main / PM (属原理图 + 落表 + 板那一趟) | ★**本轮已把两种写法各自的电学后果算出来, 不再是「措辞矛盾」这种描述性缺口**: 写法A (note 正文自述的正解) = 源极 S 接 BAT_SW (高电位侧) / 漏极 D 接 ON (负载侧) / 栅极 G 接 PG: PG 低(电源良好)=0 V ⇒ VGS = VG − VS = 0 − 4.2 = **−4.2 V** ⇒ |VGS| 4.2 V > |VGS(th)max| 2.4 V ⇒ 导通 ⇒ ON 被拉到 BAT_SW ⇒ 开机; PG 高(无输入)=3.3 V ⇒ VGS = 3.3 − 4.2 = **−0.9 V** ⇒ |VGS| 0.9 V < |VGS(th)min| 1.4 V ⇒ 关断 ⇒ 关机态仍能充电 ⇒ **逻辑自洽**。写法B (note 首句直译) = 源极 S 接 ON / 漏极 D 接 BAT_SW: 上电瞬间 ON 被 R_PD_ON 10 kΩ 下拉到 0 V ⇒ VGS = 0 − 0 = **0 V** ⇒ |VGS| 0 < |VGS(th)min| ⇒ **不导通**; 且 PG 高时 VGS = 3.3 − 0 = **+3.3 V** (对 P 沟道是反向偏置, 体二极管也不导) ⇒ **PG 高低都关 ⇒ 开机路径彻底不通**。⇒ 结论: note 首句「源极接 ON · 漏极接 BAT_SW」与 note 正文自述的「Vgs≈−4.2V ⇒ 导通 ⇒ 开机」**互斥** ⇒ 首句必须改, 否则板子装出来开不了机。★**连带一条落表前置**: 板占位 pad1=PWR_ON / pad2=BAT_SW / pad3=PWR_GOOD; 若按写法A (BAT_SW→S, ON→D, PG→G) ⇒ 需要器件引脚序 = pad1:D / pad2:S / pad3:G, 而 SOT-23 库标准引脚序是 G/S/D (AO3407A 明写 pin1=G pin2=S pin3=D) ⇒ **要么选 D-S-G 序的 P-MOS, 要么重画 land** ⇒ 这是 G-2 的升级版, 不是 G-2 能盖住的。 | [官网] | ① AOS `AO3407A` 官方数据手册 (落盘 `state/.cache_iss244/mos/AO3407A.pdf`, 5 页): p1 首行标题「30V P-Channel MOSFET」; 特性表 VGS(th) min −1.4 / typ −1.9 / max −2.4 V (VDS=VGS, ID=−250 mA); VGS 绝对最大 ±20 V; RDS(ON) 78 mΩ max @VGS=−4.5 V; IDSS ≤1 µA@25 °C / ≤5 µA@55 °C; 引脚定义 pin1=G pin2=S pin3=D。② Diodes Inc `DMP3098L` 官方数据手册 (落盘 `state/.cache_iss244/mos/DMP3098L.pdf`, 5 页): p1 引脚配置图 Drain / Gate / Source; VGS(th) −1.0 / −1.8 / −2.1 V; IDSS ≤800 nA @VDS=−30 V; RDS(on) 98/120 mΩ @−4.5 V; VGS 绝对最大栏手册未给 ⇒ 该项 [0数据]。③ 网表原文 `HW/netlist_v1.csv` L59/L60/L61 三行 (Q_PG 的 PWR_ON / BAT_SW / PWR_GOOD) —— L59 的 note 同时写了首句与「正解」两种写法。④ 板文件 pad↔net 实读 (ISS-241 §5 S21, 本单只读不改)。 | 降级 ① (不改板, 换引脚序): 选**引脚序 = D-S-G** 的 P 沟道 SOT-23 ⇒ 板占位不动; 代价 = 本轮只核到 AO3407A (G-S-D) 与 DMP3098L (D-S-G 之外的常见序) ⇒ **D-S-G 序的在售件本轮 [0数据]**, 落表批次按此口径复核。降级 ② (改 land, 换标准器件): 选 G-S-D 序器件 (AO3407A) ⇒ 落板批次把 pad 重新对应到 BAT_SW→S / ON→D / PG→G ⇒ 代价 = 重画 land (归板那一趟) + 必须逐焊盘核 pad↔pin。降级 ③ (换拓扑, 不换器件): 把 Q_PG 改回 N 沟道低边 ⇒ 与 V1.9 的改动方向相反 ⇒ 代价 = V1.9 已判 N-MOS 低边「开机路径彻底不通」, 这条实际不成立, 只作记录。★三个降级都要 main/PM 拍, 本单不代拍。 | ① 拍板: 写法A 还是写法B (本单建议 A, 但**不代拍**); ② 拍板: D-S-G 器件存在与否 (落表批次复核); ③ 拍板: 是否重画 land (板那一趟)。 | 需老板拍 + 需落表 |
| **G-2** | 占位焊盘的 pad 序号 = 网表行顺序, 不是库封装的 G/S/D 顺序 | hw-lead (板那一趟) + 落表批次 | 三件 MOS 的 pad↔pin 映射三样都不同 (`Q_AND`=D/S/G, `Q_ENVC`=G/S/D, `Q_PG`=S/D/G), 换任何 SOT-23 器件都必须逐件重画 land 并核 pin 映射。★本轮补充一条: 这条在 G-1 裁决为「写法A」之后会**升级** —— 需要的器件引脚序变成 D-S-G, 与库标准 G-S-D 不符 ⇒ G-2 与 G-1 必须同批处理, 不能分两趟。 | [实测] | ISS-241 §4 缺口 G-2 + §5 S21 (板文件逐焊盘 at/size/net 实读); 本单只读板文件, 未写入任何板文件。 | 降级 = 选**引脚序与占位 pad 顺序一致**的器件 ⇒ 本轮在售 SOT-23 绝大多数是 G-S-D ⇒ 此路实际不通 ⇒ 实际等价于「必须重画 land」。⇒ 落板批次把 G-2 与 G-1 合并成一次 land 重画, 避免重画两遍。 | land 重画时 pad↔pin 映射表 (G-1 裁决后才能定稿)。 | 已转单 (hw-lead 板那一趟) · 与 G-1 同批 |
| **G-3** | CSI-2 ESD 只覆盖 1 条 lane (10 条高速差分线里 9 条无 ESD 占位) | PM (ESD 方案口径 = V-2 二选一) · sw-lead 只出依据 + 代价 | 实测: `D_ESD_CAM` 在网表上只有两个焊盘 (GND + CSI_D0_CK_P) ⇒ 只护 clock lane 的**正相**一根。而本板 CSI-2 在网表上是 **5 对差分 = 10 条线** (CSI_D0_CK_P/N + CSI_D0_D0_P/N + CSI_D0_D1_P/N + CSI_D0_D2_P/N + CSI_D0_D3_P/N, 各经 100 nF AC 耦合电容到 CONN_CAM pin2/3/5/6/11/12/14/15/17/18) ⇒ **CK_N 与 D0~D3 的正负两根共 9 条线没有任何 ESD 占位**。★业界依据 (本轮新查): TI 官方应用文档 `SLVAF82B`《ESD and Surge Protection for USB Interfaces》(Rev. B, 2024-01, 19 页, 落盘 `state/.cache_iss244/ref/ti_slvaf82_usb_esd.pdf`) §3.2/§4 写明两条硬原则: ①「the diodes are connected to **each data line**」且例图用 ESD321 **同时护 D+ 与 D−**; ②「place the diodes **as close to the source of ESD**, in this case the connector, as design rules allow」。同一原则套到 CSI-2 ⇒ **每条 lane 的正负两根都要护**; 本项目网表 L417 note 已引 Forlinx 载板指引的同一条「ESD 紧贴接口」要求。★代价 (可量化): ① 焊盘数: 2 焊盘单通道件 → 6 通道件 6 焊盘 (+4); ② 面积: 单通道 `TPD1E05U06DPYR` (X1SON 0.5×0.5 mm, 落盘 `state/.cache_iss244/led/tpd6e05u06.pdf` 同族) → 6 通道 `TPD6E05U06` (SOT-23-6, 2.9×1.3 mm) ⇒ 本体面积约 ×15; ③ 结电容: **不是瓶颈** —— `TPD6E05U06` 官方 IO 电容 0.42 pF typ, 与单通道 `TPD1E05U06` 同档 ⇒ 双边保护可以不付结电容的代价, 只付焊盘与面积。 | [官网] | ① TI `SLVAF82B` (落盘 `state/.cache_iss244/ref/ti_slvaf82_usb_esd.pdf`) §3.2 段 + §4「Capacitance (D+, D-)」; ② TI `TPDxE05U06` 数据手册 (落盘 `state/.cache_iss244/led/tpd6e05u06.pdf`) p1「IO capacitance 0.42pF to 0.5pF (typical)」; ③ 网表 `HW/netlist_v1.csv` L413/L414 (D_ESD_CAM 两行) + L250~L269 (10 条 CSI 线与 AC 耦合电容); ④ 板文件 pad 实读 (ISS-241 §5 S21)。 | 降级 ① (不改板, 只把现有 2 焊盘位用足): 维持单边 ⇒ 代价 = 9 条高速差分线裸奔, 一次 ESD 就可能打死相机链路 (CSI-2 无重传兜底)。降级 ② (改板, 加 6 通道件): 一颗 `TPD6E05U06` (6 通道 / 0.42 pF) 覆盖 CK_P/N + D0_P/N + D1_P/N (6 条) ⇒ 代价 = +4 焊盘 + 约 3.8 mm² 面积; 剩余 D2/D3 四条线仍无 ⇒ 需第二颗 4 通道件。降级 ③ (改板, 分层保护): 把 ESD 放在**靠近 SoM 侧**而不是连接器侧 ⇒ 代价 = 违反 TI「紧贴 ESD 源」的布局原则, 不推荐。★本单只列代价, **不代拍 V-2**。 | V-2 (ESD 方案二选一) 由 PM/老板拍: 保持单边 / 改板加多通道。 | 需老板拍 (V-2) · 依据与代价已备齐 |
| **G-4** | USB 2.0 只保护 D+, D− (USB_D_N_SRC) 无 ESD 占位 | PM (同上, V-2) · sw-lead 只出依据 + 代价 | 实测: `D_ESD_USB_D` 只有两个焊盘 (USB_D_P_SRC + GND); `USB_D_N_SRC` 在网表上只出现在串阻行 (R_SER_USB_D_N), 无任何 ESD 器件挂载 ⇒ **D− 完全裸奔**。★这条是 ISS-190 §7-7 已登记过的旧发现, 本轮把它补上了**可引用的官方依据 + 可量化的代价**: ① TI `SLVAF82B` §3.2/§4 原文用 `ESD321` (双通道) **同时护 D+ 与 D−**, 并写明「the diodes are connected to each data line」; ② Würth Elektronik 应用文档 `ANP002`《The protection of USB 2.0 applications》§7 Figure 9 (双差分线都走 TVS) 与 Figure 11 (单通道器件的用法是 **D+ / D− 各一颗**, 连接方式 D+ / D− → GND) ⇒ **单通道器件的业界通行做法也是两条线各一颗, 不是「一条线就够了」**; ③ Semtech 官方技术文章《ESD Protection of USB 2.0 Interfaces》同口径 (`RClamp0582B` 双通道护 D+/D−)。★TI 还给了 USB 2.0 的**结电容判据**: 「An ESD diode with a capacitance **less than 4 pF** is recommended」 (USB 2.0 ≤480 Mbps) ⇒ 双通道 `TPD2E2U06` 官方 CL = 1.5 pF typ / 1.9 pF max (落盘 `state/.cache_iss244/led/tpd2e2u06.pdf`, Rev. C) ⇒ **1.9 pF max 仍在 4 pF 判据内** ⇒ **双边保护的代价不在结电容, 在焊盘数 (+1) 与面积**。 | [官网] | ① TI `SLVAF82B` (落盘 `state/.cache_iss244/ref/ti_slvaf82_usb_esd.pdf`): §3.2 (each data line / ESD321 护 D+ 与 D− / 紧贴连接器) + §4「Capacitance (D+, D-): ... less than 4 pF is recommended」; ② Würth `ANP002` §7 Figure 9 / Figure 11 (D+ / D− 各一颗, 单通道器件同样两条线都护); ③ TI `TPD2E2U06` 数据手册 Rev. C (落盘 `state/.cache_iss244/led/tpd2e2u06.pdf`): CL 1.5 pF typ / 1.9 pF max, CCROSS 0.02 pF, ΔCIO-TO-GND 0.03/0.1 pF; ④ 网表 `HW/netlist_v1.csv` L417/L418 (D_ESD_USB_D 两行); ⑤ ISS-190 §7-7 已登记同一事实 (本单只引用, 未改 SW/ 任何文件)。 | 降级 ① (不改板): 维持单边 ⇒ 代价 = D− 裸奔, 而 J_USB_C 是板内**唯一的刷写口** ⇒ 一次 ESD 打到 D− 就只能拆机 JTAG (与 ISS-190 §7-7 同口径)。降级 ② (改板, 双通道件): 换 `TPD2E2U06` (SOT-23-3, 3 焊盘) ⇒ 代价 = 焊盘 +1 + 面积增加, 结电容 1.9 pF max 仍 < TI 的 4 pF 判据 ⇒ **对 USB 2.0 上升沿无实质影响**。降级 ③ (改板, 换更小封装双通道): 找 X1SON/X2SON 双通道低容值件 ⇒ 代价 = 本轮只核到 TI 一家的双通道官方手册, 其它厂双通道在售件的 Cd 本轮 [0数据], 落表批次补。★不代拍 V-2。 | V-2 拍板 + 若选双边, 落表批次定双通道具体型号 (Cd < 4 pF 判据已定死)。 | 需老板拍 (V-2) · 依据与代价已备齐 |
| **G-5** | LED 亮度账不匹配: 1 kΩ 串阻 + 3.3 V ⇒ 实际 ~1.1~1.35 mA, 而候选全是 20 mA 标称 | PM / 结构 (亮度档) + 落表批次 (改 R) · sw-lead 只出依据 + 代价 | ★**本轮把 [0数据] 升成了 [官网] + [推算], 并且把上一轮只活在会话内存里的数变成了盘上可复核的证据**。① 电流账 (网表 L301/L304 实读): `R_LED_G` / `R_LED_R` = **1 kΩ ±1%**, 驱动 3.3 V ⇒ I = (3.3 − Vf)/1 kΩ。按 ISS-241 已核的厂商 Vf: 红 `AA1608SURSK` VF typ 1.95 V ⇒ I ≈ **1.35 mA**; 绿 `KP-2012SGC` VF typ 2.2 V ⇒ I ≈ **1.10 mA**; Vf 取 max 2.5 V 时 I 只剩 **0.80 mA** ⇒ 实际工作点区间 **0.80 ~ 1.35 mA** (比 ISS-241 写的 1.1~1.3 mA 更宽)。② 亮度档 (本轮新查 + 数字化): **Kingbright 厂商 PDF 里每一份数据手册都画了「Luminous Intensity vs. Forward Current」归一化曲线** (纵轴 = 以 20 mA 归一化, 横轴 = If)。本轮落盘 4 份原厂 PDF 并写了数字化脚本 `state/.cache_iss244/led/extract_ivif.py`, 从 PDF **文本层**取坐标轴刻度做标定 (不是人眼量), 再用 RANSAC 拟合迹线提取曲线, 脚本自带 3 条自证 (过原点 / 20 mA 点 ≈ 1.00 / 单调)。★**四颗料各跑一遍, 数字互相印证** (1 mA 工作点占 20 mA 标称亮度的比例): `AA1608SURSK` (D_LED_R) = **5.10%** · `APT1608SURCK` (D_CHG_LED) = **5.10%** · `APH1608SURCK` = **4.77%** · `APH1608SGC` (0603 绿) = **5.24%** · `AP2012CGCK` (0805 绿) = **7.19%**。★**结论 (可复核)**: 1 mA 工作点的 LED 亮度只有 20 mA 标称值的 **约 4.8% ~ 7.2%**, 也就是 **暗 14 ~ 21 倍**。③ 折成绝对值: `D_LED_R` (AA1608SURSK, Iv 40 min / 160 typ mcd @20 mA) ⇒ 1.35 mA 时 ≈ **11 mcd typ** (最坏档 40 mcd ⇒ ≈2.8 mcd); `D_LED_G` (KP-2012SGC, GaP 绿, Iv 5 min / 12 typ mcd @20 mA) ⇒ 1.10 mA 时 ≈ **0.7~0.9 mcd typ**; `D_CHG_LED` (APT1608SURCK, Iv 40/80 mcd @20 mA) ⇒ 1.35 mA 时 ≈ **5.5 mcd typ**。④ 归一化曲线在厂商图上只画到 If≈30 mA ⇒ 超出部分本单**不外推**。★**这颗 LED 不是显示白场** (显示件是 0.49" SiOLED / demo 是 Waveshare 2.8" LCD) ⇒ 光生物安全的「白场辐亮度」判定不直接落在它身上; 但它是**眼旁指示光源**, 仍需按 IEC 62471 单列评估 ⇒ 登记为需老板拍的一项。 | [官网] | ① Kingbright 官方 `AA1608SURSK` 数据手册 (落盘 `state/.cache_iss244/led/AA1608SURSK_kingbright.pdf`, Ver.3A, 4 页) 第 3 页 4 格图第 2 格 「Luminous Intensity vs. Forward Current」(Y 轴刻度 0.0~2.5, X 轴刻度 0~50 mA), 第 1 页 SELECTION GUIDE Iv 40 min / 160 typ mcd @20 mA; ② Kingbright 官方 `APT1608SURCK` 数据手册 (落盘 `state/.cache_iss244/led/APT1608SURCK_kingbright.pdf`, Ver.22A, 4 页) 同款图 + Iv 40/80 mcd @20 mA; ③ Kingbright 官方 `APH1608SURCK` (落盘 `state/.cache_iss244/led/led_aph1608surck.pdf`, Ver.13A) + `APH1608SGC` (`led_aph1608sgc.pdf`) + `AP2012CGCK` (`led_ap2012cgck.pdf`) 三份交叉印证; ④ `KP-2012SGC` 数据手册 (落盘 `state/.cache_iss244/led/KP-2012SGC_farnell.pdf`, DSAB1341 V.18B) 第 2 页 SELECTION GUIDE Iv 5 min / 12 typ mcd @20 mA + VF 2.2/2.5 V @20 mA ⇒ ★**该版本的曲线是位图 (非文本层) ⇒ 本脚本按文本层标定抓不到 ⇒ 绿灯的 1 mA 档用同厂同尺寸绿 `AP2012CGCK` 的曲线做代理 ⇒ 该档标 [推算] 并写明代理件**; ⑤ 数字化脚本 `state/.cache_iss244/led/extract_ivif.py` + 逐件 JSON 结果 `state/.cache_iss244/led/ivif_*.json` (含坐标轴刻度/自证/采样点); ⑥ 网表 `HW/netlist_v1.csv` L300/L301/L303/L304 (R_LED_R / R_LED_G = 1 kΩ ±1%, 3.3 V 驱动)。 | 降级 ① (**不改网表, 只改亮度预期**): 接受 LED 就是这么暗 (≈ 5% 标称) ⇒ 代价 = 指示灯在白天/强光下基本看不见 ⇒ 需要 PM 给「指示灯可接受亮度」口径 (结构侧给眼旁辐亮度上限) ⇒ ★这是**本单建议的默认路线**, 因为改 R = 改网表 (归落表批次)。降级 ② (改串阻, 保 20 mA 档): 红 Vf 1.95 V ⇒ R = (3.3 − 1.95)/20 mA ≈ **68 Ω** (取 E96 68 Ω); 绿 Vf 2.2 V ⇒ R ≈ **55 Ω** ⇒ 代价 = ① 改网表 (落表批次) + ② 功耗从 ~2.2 mW 升到 ~66 mW (两颗合计约 0.13 W ⇒ 进关机/待机电池账, 参照 ISS-172 的 108 µA 关机账) + ③ **亮度直接进光生物安全评估** (从 ~11 mcd 升到 ~160 mcd, 眼旁光源强度提升 14 倍) ⇒ 需结构侧重算 IEC 62471 分级。降级 ③ (改驱动方式, 不改 R): 用 SoC GPIO 恒流/PWM 驱动 ⇒ 代价 = 硬件要加恒流或改成 PWM + 电阻, 且 1 kΩ 上拉的亮度可调 ⇒ 但 **PWM 占空比与 60 fps 帧预算耦合**, 属 SW 侧改动 ⇒ 本单不碰。★**改 R 阻值 = 改网表 ⇒ 归落表批次, 本单只出建议值 + 代价, 一字未改网表**; ★**亮度档本身需老板/PM 拍 (不代拍)**。 | ① 拍板: 亮度档走降级 ① (接受暗) 还是 ② (改 R 到 20 mA 档) 还是 ③ (PWM); ② 若走 ②, 落表批次改 R 阻值 + 结构侧重算 IEC 62471; ③ KP-2012SGC 自身曲线若要精确值, 落表批次用厂商图纸 (非本机 PDF) 复核。 | 需老板拍 (亮度档) + 需落表 (若选改 R) |
| **G-6** | C_REGN 的 BOM value (1 µF) 与 TI BQ25896 手册 (4.7 µF / 10 V) 冲突 | main (落表批次) | TI BQ25896 数据手册 (SLUSC76C) pin22 REGN 原文: 「Internally, REGN is connected to the cathode of the boost-strap diode. **Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND.** The capacitor should be placed close to the IC. REGN also serves as bias rail of TS pin.」⇒ BOM value 必须从 1 µF 改成 4.7 µF / 10 V / X7R。★本轮已按 ISS-241 的交接条件 L1 并进 **ISS-243 (落表)**, 本单不重复论证, 只登记出处与当前状态。★★**2026-11-16 15:45:45 实测: 已被并发落表批次落掉** —— `HW/BOM_v1.csv` 的 `C_REGN` 行 value 已变成「4.7µF ±10% (10V)」、opn 已填「GRM21BR71C475KA73L (Murata 0805 / 4.7µF / 16V / X7R / ±10%)」⇒ ★**本条当场闭合** ⇒ 该件不再进落表批次 (清单里保留该行 + 落表证据)。 | [官网] | TI `BQ25896` 数据手册 SLUSC76C pin22 (ISS-241 §5 已下载本地实读, 本单只引用) + `HW/BOM_v1.csv` `C_REGN` 行 value='[待选型] 1µF' + ISS-241 交卷单 L1。 | ① 落表批次同批改 BOM value = 4.7 µF / 10 V / X7R (1 行改动, 与 OPN 回填同批走) ⇒ **这是唯一安全路线**;② 若充电板面积不允许 0805 ⇒ 0402 4.7 µF ⇒ 代价 = DC bias 降容比 0805 狠, 吃掉手册余量 (该型号官方页本轮 [0数据], 落表批次补);③ 若坚持 1 µF ⇒ 必须登记「偏离 TI 手册」并由 main/PM 签字 ⇒ 本单不代签。 | 落表批次改 BOM value 一行 (ISS-243)。 | 已闭合 (2026-11-16 15:45 实测已被并发落表批次落掉) · 已转单 (ISS-243 L1) |
| **G-7** | 占位 land 与在售器件的厂商 land 普遍不重合 (22 件里绝大多数都要重画 land) | hw-lead (板那一趟) | 4 件 ESD (占位 2.30 mm 间距) vs SOD-323 1.3 mm / X1SON 0.65 mm; 3 件 MOS (占位 1.27~1.53 mm) vs SOT-23 0.95 mm; 5 件按键 (占位 2.20 mm) vs gullwing 外扩 4.6 mm ⇒ **这不是选型的错, 是占位脚手架的性质** ⇒ 本单 22 件里绝大多数都要在板那一趟重画 land。★本轮新增一条跨缺口结论: G-7 与 G-1/G-2 **必须合并成同一次 land 重画**, 否则要重画两遍 (G-1 裁决会改 pad↔pin 映射)。 | [实测] | ISS-241 §4 缺口 G-7 + §5 S21 (板文件逐焊盘实读) + `HW/PART_SELECTION_MATRIX_2026-11-16.md` §3 每件的「封装兼容性结论」栏。 | 选 land 间距与占位接近的器件 ⇒ 本轮在售件普遍偏小 ⇒ 此路对 ESD/按键基本不通 ⇒ 实际必须重画 land (板那一趟)。 | 板那一趟的 land 重画清单 (含 G-1/G-2 的 pad↔pin 映射)。 | 已转单 (hw-lead 板那一趟) · 与 G-1/G-2 同批 |
| **G-8** | 6 件充电板器件的封装占位是「待定」⇒ 无法给几何兼容结论 | main (充电板那一趟) | `D_ESD_TC` / `FB_VBUS` / `D_TVS_VBUS` / `Q_CHG_LED` / `D_CHG_LED` / `C_REGN` 六件的 BOM footprint 栏是「待定」, 且板文件里查无此位号 ⇒ 本单对这些件只能给「落 N 焊盘 + 充电板侧封装另行定」。★已并进 **ISS-243 的落表前置条件 L4**, 本单不重复论证。 | [实测] | `HW/BOM_v1.csv` 六行的 footprint 栏 + 板文件逐位号实查 (ISS-241 §5 S21) + ISS-241 交卷单 L4。 | 落 N 焊盘 + 充电板侧封装另行定 ⇒ 代价 = 这六件的 OPN 回填与 land 要在充电板那一趟一起做, 不能在主板那一趟提前定死。 | 充电板那一趟定六件的封装与 land。 | 已转单 (ISS-243 L4) · 已闭合 |
| **G-9** | 任务书 / BOM / main 三处「件数」口径互不一致 | main (确认口径) | ★本轮**自己跑 csv 复核** (不抄任何硬编码数字): 两个机器派生源 —— ① **登记范围** = ISS-241 矩阵基准块的 `expected_refs` = **22 件** (本单必须全覆盖); ② **当前仍待落** = `HW/BOM_v1.csv` 实跑「待选型∩必装 − 越界件」= **21 件**。两者差的那一件是 `C_REGN` —— ★**2026-11-16 15:45:45 实测: 它被另一个落表批次落掉了** (BOM value 从「[待选型] 1µF」改成「4.7µF ±10% (10V)」+ opn 已填) ⇒ **登记范围仍是 22 (登记事实不变), 当前待落是 21 (盘上事实变了)** ⇒ 两个数都要写在清单里并注明来源。任务书按类别枚举 = 20 个位号、抬头说 21 件 ⇒ 口径差不改, 本单按**超集 22 行**全覆盖。★ISS-241 的门禁 `HW/check_part_selection_matrix.py` 用的是矩阵基准块里的 `expected_refs` 快照 (22) ⇒ 它仍然 22/22 全绿, 本单没有把它改红。★**本单门禁的 C5 写成双源判定** (登记范围 + 当前待落), 并要求「已被并发落掉的一件必须写 landed_note 落表证据」⇒ **锚点过期 = 红 ⇒ 走 H-1 重锚 + 留痕**, 而不是把红灯调没 (ISS-225 纪律)。 | [实测] | `HW/BOM_v1.csv` 实跑 (本单 §6 复现命令 ①, 输出原样贴在交卷单 B5) + `HW/check_part_selection_matrix.py` 的 `expected_refs` 逻辑 + main 2026-11-16 14:3x 亲核记录。 | 若落表批次再改 BOM 的「待选型/必装」口径 ⇒ 本单门禁 `HW/check_part_selection_gaps.py` 的 C5 会**按设计变红** (要么有登记范围内的一件不见了, 要么多出越界件, 要么已被并发落掉的一件没写落表证据) ⇒ 走 H-1 重锚流程 (改本单生成器 + 留痕) 而不是把红灯调没。 | 无 (口径已定死 = 登记范围 22 件 / 当前待落 21 件, 两个数都注明了来源与时点)。 | 已闭合 |
| **G-10** | R_SUPV_DIV1/2 的最终阻值 (原厂电压窗口未到 ⇒ 只给得出 0 Ω 跳线件的 OPN) | main / PM (落表批次 + 老板拍是否恢复监督器) | ★**本轮把公式和候选表做出来了, 结论是「真正阻塞的不是阻值算不出, 而是监控器本体不装」**。① 官方公式 (TI `TPS3808G01`, 数据手册 SBVS050N Rev. N, 2026-08, 36 页, 落盘 `state/.cache_iss244/ref/tps3808.pdf`): §7.3.1 + Figure 7-1 明写 **V_IT = (1 + R1/R2) × 0.405 V** (R1 = 上臂 被监控轨→SENSE, R2 = 下臂 SENSE→GND), 功能框图注 **R1 + R2 = 4 MΩ**, TPS3808G01 = Adjustable 版 / V_IT 标称 0.405 V / 阈值精度 VIT ≤3.3 V 时 typ ±1.5% / −1.5% ±0.5% / 迟滞 1.5% / SENSE 脚建议 1 nF~10 nF 滤波电容。② 被监控轨 `RAIL_V_SOC_IO` 的电压在网表 L84 原文是「**[待原厂] (3.3V / 1.8V / 1.2V)**」(TBD-02 未闭合) ⇒ 三档候选。③ 候选表 (触发点取轨标称 ×0.90 = 轨电压跌 10 % 报欠压; 电阻 1 %; 算式见 `state/.cache_iss244/supv_divider_solve.py`, 可复跑): 轨 3.3 V ⇒ V_IT 2.970 V ⇒ R1/R2 = 3.480 M / 549 k (E96) ⇒ 实际触发 2.9722 V, 误差带 2.8108~3.1378 V; 轨 1.8 V ⇒ V_IT 1.620 V ⇒ R1/R2 = 3.010 M / 1.000 M ⇒ 实际触发 1.6240 V, 误差带 1.5359~1.7145 V; 轨 1.2 V ⇒ V_IT 1.080 V ⇒ R1/R2 = 2.490 M / 1.500 M ⇒ 实际触发 1.0773 V, 误差带 1.0188~1.1373 V。④ ★**真正的阻塞**: `U_SUPV` 三行 dnp=**DNP** (网表 L407~L409, note 写明「SoM 内部 PMIC 已做上电复位 ⇒ 主板不装监督器」), 而产生 `RAIL_V_SOC_IO` 的 `U_DCDC_VIO` 也 dnp=**DNP** (网表 L84/L86) ⇒ **监督器本体不装 ⇒ 分压两臂装上只会把 RAIL_V_SOC_IO 短路到地** (ISS-190 已判过同一件事) ⇒ 分压阻值这件事本身没有可落的对象。 | [官网] | ① TI `TPS3808` 数据手册 SBVS050N Rev. N (落盘 `state/.cache_iss244/ref/tps3808.pdf`) §7.3.1 + Figure 7-1 + Ordering Information 表 (TPS3808G01 Adjustable 0.405 V) + 特性表 (阈值精度/迟滞); ② 网表 `HW/netlist_v1.csv` L84/L86 (U_DCDC_VIO dnp=DNP, 轨电压 [待原厂]) + L404/L405/L406 (R_SUPV_DIV1/2 = 0 Ω 跳线位, tbd=TBD-02) + L407~L409 (U_SUPV dnp=DNP); ③ 计算脚本 `state/.cache_iss244/supv_divider_solve.py` (可复跑, 输出原样贴在交卷单 B5)。 | 降级 ① (**推荐**): `R_SUPV_DIV1` / `R_SUPV_DIV2` 随 `U_SUPV` 一并置 **DNP** ⇒ 零新增器件、零板改动、顺带解掉 ISS-190 判的「装 0 Ω 就短路」装配级灾难 ⇒ 代价 = 主板侧放弃独立欠压监督 (依赖 SoM 内部 PMIC 的上电复位)。降级 ②: 决定恢复监督器 ⇒ 按上表取 E96 值 + 触发点随轨标称重算 + 补 1 nF SENSE 滤波电容 ⇒ 代价 = ① 要新增 U_SUPV 的器件行 (现在 DNP) + ② 轨标称必须先定 (TBD-02) + ③ 误差带 (上表) 要并进欠压策略。降级 ③: 监督器换成**可编程/带窗口**的器件 (不加分压) ⇒ 代价 = 封装与板位要重新核, 本轮未查 ⇒ [0数据], 落表批次补。★**本单只出依据 + 代价, 不代拍「要不要恢复监督器」。** | ① 拍板: 主板侧要不要独立欠压监督 (降级 ① / ② / ③); ② 若走 ②, TBD-02 轨标称要定 (3.3 / 1.8 / 1.2 V 三选一)。 | 需老板拍 + 需落表 |

## §3 四条重点缺口的结论摘要

### §3.1 G-5 (LED 亮度账不匹配) —— 本轮从 [0数据] 升到 [官网]+[推算]

- **电流**: `R_LED_G`/`R_LED_R` = 1 kΩ ±1% @ 3.3 V ⇒ 红 ≈ **1.35 mA** (Vf 1.95 typ) / 绿 ≈ **1.10 mA** (Vf 2.2 typ) / Vf 取 2.5 max 时只剩 **0.80 mA**。
- **亮度档 (厂商曲线数字化)**: Kingbright 每份数据手册第 3 页第 2 格都是「Luminous Intensity vs. Forward Current」(以 20 mA 归一化)。本轮落盘 4 份原厂 PDF + 写了 `state/.cache_iss244/led/extract_ivif.py` (从 PDF **文本层**取刻度做标定 + RANSAC 提迹线 + 3 条自证)。
- **四颗料互相印证的 1 mA 档 (占 20 mA 标称的比例)**: `AA1608SURSK` **5.10%** · `APT1608SURCK` **5.10%** · `APH1608SURCK` 4.77% · `APH1608SGC` 5.24% · `AP2012CGCK` 7.19% ⇒ **1 mA 工作点只有标称亮度的 4.8%~7.2% (暗 14~21 倍)**。
- **绝对值**: 红 ≈ **11 mcd typ** (1.35 mA) / 绿 ≈ **0.7~0.9 mcd typ** (1.10 mA, 代理曲线) / 充电灯 ≈ **5.5 mcd typ**。
- **代价**: 改 R 到 20 mA 档 ⇒ 红 **68 Ω** / 绿 **55 Ω**, 功耗 ~2.2 mW → ~66 mW (两颗 ≈ 0.13 W 进电池账) 且亮度 ×14 ⇒ 眼旁光源的 IEC 62471 分级要重算。★**这颗不是显示白场** ⇒ 光生物安全的「白场辐亮度」判定不直接落在它身上, 但仍需单列评估 ⇒ 登记为需老板拍。

### §3.2 G-3 + G-4 (高速差分对单边 ESD) —— 业界依据 + 代价

- **依据**: TI `SLVAF82B` §3.2/§4 —— 「the diodes are connected to **each data line**」(例图用双通道件同时护 D+ 与 D−) + 「place the diodes **as close to the source of ESD**, in this case the connector」; Würth `ANP002` §7 Figure 9 / Figure 11 —— **单通道器件的业界通行做法也是 D+ / D− 各一颗**; TI USB 2.0 结电容判据 **Cd < 4 pF**。
- **本板实测**: `D_ESD_CAM` 只护 `CSI_D0_CK_P` (2 焊盘) ⇒ CSI-2 的 5 对差分共 10 条线里 **9 条裸奔**; `D_ESD_USB_D` 只护 `USB_D_P_SRC` ⇒ **D− 裸奔**。
- **代价 (可量化)**: USB 双边 ⇒ 焊盘 +1 (2→3), `TPD2E2U06` Cd **1.5 pF typ / 1.9 pF max** < 4 pF 判据 ⇒ **结电容不是瓶颈, 瓶颈是焊盘与面积**; CSI 全护 10 条 ⇒ 需 6 通道件 ×2 (SOT-23-6, 本体 2.9×1.3 mm) ⇒ 焊盘 +4, 面积约 ×15, 但 `TPD6E05U06` 的 **0.42 pF** 与单通道同档 ⇒ **双通道不必付结电容代价**。

### §3.3 G-1 (Q_PG 源漏拓扑) —— 两种写法的电学后果都算出来了

- **写法A** (S=BAT_SW / D=ON / G=PG): PG 低 ⇒ VGS = 0 − 4.2 = **−4.2 V** ⇒ 导通 (|VGS(th)max| 2.4 V) ⇒ 开机; PG 高 ⇒ VGS = 3.3 − 4.2 = **−0.9 V** ⇒ 关断 (|VGS(th)min| 1.4 V) ⇒ **逻辑自洽**。
- **写法B** (note 首句直译 S=ON / D=BAT_SW): 上电瞬间 ON 被 10 kΩ 下拉到 0 V ⇒ VGS = **0 V** ⇒ 不导通; PG 高时 VGS = **+3.3 V** (反向偏置) ⇒ **PG 高低都关 ⇒ 开机路径彻底不通**。
- ⇒ **note 首句与 note 正文自述的「正解」互斥, 首句必须改** (改网表 note 归落表/原理图那一趟, 本单一字未改)。
- ★**连带**: 按写法A 需要器件引脚序 = **D-S-G**, 而 SOT-23 库标准序是 **G/S/D** ⇒ 要么选 D-S-G 序器件 (在售件本轮 [0数据]), 要么重画 land ⇒ **G-1 与 G-2 / G-7 必须同批处理**。

### §3.4 G-10 (分压最终阻值) —— 公式与候选表都做出来了, 但真正阻塞在别处

- **官方公式**: TI `TPS3808G01` (SBVS050N Rev. N) §7.3.1 + Figure 7-1 ⇒ **V_IT = (1 + R1/R2) × 0.405 V**, **R1 + R2 = 4 MΩ** (R1 上臂 / R2 下臂), 阈值精度 typ ±1.5%, 迟滞 1.5%, SENSE 脚建议 1 nF 滤波电容。
- **候选表** (触发点 = 轨标称 ×0.90; 算式见 `state/.cache_iss244/supv_divider_solve.py`): 轨 3.3 V ⇒ 3.480 M / 549 k ⇒ 触发 2.9722 V (带 2.8108~3.1378 V); 轨 1.8 V ⇒ 3.010 M / 1.000 M ⇒ 1.6240 V (1.5359~1.7145); 轨 1.2 V ⇒ 2.490 M / 1.500 M ⇒ 1.0773 V (1.0188~1.1373)。
- ★**真正的阻塞**: `U_SUPV` 三行 **DNP**、产生被监控轨的 `U_DCDC_VIO` 也 **DNP** ⇒ 监督器本体不装 ⇒ **分压两臂装上只会把 RAIL_V_SOC_IO 短路到地** (ISS-190 同判) ⇒ **建议两臂随 U_SUPV 一并置 DNP**; 若决定恢复监督器, 才按上表取值。

## §4 ★OPN 回填清单 (只出清单, 不落表)

★**登记范围 = 22 件** (ISS-241 矩阵基准块的 `expected_refs`, 机器派生) · 其中 **8 件当前仍待落** · **14 件已被并发落表批次落掉** (`C_REGN`, `D_ESD_CAM`, `D_ESD_DEMO`, `D_ESD_TC`, `D_ESD_USB_D`, `D_TVS_VBUS`, `FB_DEMO`, `FB_VBUS`, `Q_AND`, `Q_CHG_LED`, `Q_ENVC`, `Q_PG`, `R_SUPV_DIV1`, `R_SUPV_DIV2`) ⇒ 该行保留并标注落表证据, 不进落表批次。

| # | 位号 | 板 | 矩阵推荐项 (型号) | 证据等级 | 封装兼容性结论 | 落表锚点 (ref+net, ★行号会随落表漂移★) | 要改 footprint / land? | 谁拍 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `C_REGN` | CHG_BOARD | `GRM21BR71C475KA73L` | [官网] | 落2焊盘+充电板侧封装另行定 | 网表 L44,L45 (ref=C_REGN, nets=REGN+GND) · 脚表 C_REGN.1,C_REGN.2 · BOM L43 (ref=C_REGN) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 2 | `D_CHG_LED` | CHG_BOARD | `APT1608SURCK` | [官网] | 落2焊盘+充电板侧封装另行定 | 网表 L510,L511 (ref=D_CHG_LED, nets=LED_CHG_A+CHG_LED_K) · 脚表 D_CHG_LED.1,D_CHG_LED.2 · BOM L57 (ref=D_CHG_LED) | 充电板侧封装占位待定 ⇒ 板那一趟定 (ISS-243 L4) | main (充电板那一趟) | 已转单 (ISS-243 L4) · 需落表 |
| 3 | `D_ESD_CAM` | MAIN_PCB | `TPD1E05U06DPYR` | [官网] | 条件兼容 | 网表 L163,L413,L414 (ref=D_ESD_CAM, nets=GND+CSI_D0_CK_P+GND) · 脚表 D_ESD_CAM.1,D_ESD_CAM.2 · BOM L58 (ref=D_ESD_CAM) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 4 | `D_ESD_DEMO` | MAIN_PCB | `PESD5V0S1BA` | [官网] | 条件兼容 | 网表 L420,L421 (ref=D_ESD_DEMO, nets=RAIL_DEMO_5V+GND) · 脚表 D_ESD_DEMO.1,D_ESD_DEMO.2 · BOM L59 (ref=D_ESD_DEMO) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 5 | `D_ESD_TC` | CHG_BOARD | `PESD5V0S1BA` | [官网] | 落2焊盘+充电板侧封装另行定 | 网表 L4,L162 (ref=D_ESD_TC, nets=USB_VBUS_RAW+GND) · 脚表 D_ESD_TC.1,D_ESD_TC.2,D_ESD_TC.3,D_ESD_TC.4 · BOM L61 (ref=D_ESD_TC) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 6 | `D_ESD_USB_D` | MAIN_PCB | `TPD1E05U06DPYR` | [官网] | 条件兼容 | 网表 L417,L418 (ref=D_ESD_USB_D, nets=USB_D_P_SRC+GND) · 脚表 D_ESD_USB_D.1,D_ESD_USB_D.2 · BOM L62 (ref=D_ESD_USB_D) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 7 | `D_LED_G` | MAIN_PCB | `KP-2012SGC` | [官网] | 兼容 | 网表 L305 (ref=D_LED_G, nets=GND) · 脚表 D_LED_G.1,D_LED_G.2 · BOM L64 (ref=D_LED_G) | 否 — 0805 本体 2.0×1.25 mm 与占位 fab bbox 2.70×1.60 mm 对齐 ⇒ land 不用动 | PM / 结构 (亮度档) + 落表批次 | 需老板拍 (亮度档 G-5) · 需落表 |
| 8 | `D_LED_R` | MAIN_PCB | `AA1608SURSK` | [官网] | 兼容 | 网表 L302 (ref=D_LED_R, nets=GND) · 脚表 D_LED_R.1,D_LED_R.2 · BOM L65 (ref=D_LED_R) | 否 — 0603 本体 1.6×0.8 mm 在同 bbox 内偏小, 落板后位置略靠内 | PM / 结构 (亮度档) + 落表批次 | 需老板拍 (亮度档 G-5) · 需落表 |
| 9 | `D_TVS_VBUS` | CHG_BOARD | `SMBJ5.0A` | [官网] | 落2焊盘+充电板侧封装另行定 | 网表 L505,L506 (ref=D_TVS_VBUS, nets=VBUS_5V+GND) · 脚表 D_TVS_VBUS.1,D_TVS_VBUS.2 · BOM L66 (ref=D_TVS_VBUS) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 10 | `FB_DEMO` | MAIN_PCB | `BLM21PG221SN1D` | [官网] | 兼容 | 网表 L422,L423 (ref=FB_DEMO, nets=RAIL_DEMO_5V+GND) · 脚表 FB_DEMO.1,FB_DEMO.2 · BOM L67 (ref=FB_DEMO) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 11 | `FB_VBUS` | CHG_BOARD | `BLM31PG121SN1` | [官网] | 落2焊盘+充电板侧封装另行定 | 网表 L5,L8 (ref=FB_VBUS, nets=VBUS_5V_ESD+VBUS_5V_F1) · 脚表 FB_VBUS.1,FB_VBUS.2 · BOM L68 (ref=FB_VBUS) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 12 | `Q_AND` | MAIN_PCB | `AO3400A` | [官网] | 条件兼容 | 网表 L65,L66,L67 (ref=Q_AND, nets=RESET_N+GND+PG_AND) · 脚表 Q_AND.1,Q_AND.2,Q_AND.3 · BOM L82 (ref=Q_AND) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 13 | `Q_CHG_LED` | CHG_BOARD | `2N7002` | [官网] | 落3焊盘+充电板侧封装另行定 | 网表 L512,L513,L514 (ref=Q_CHG_LED, nets=CHG_LED_K+GND+CHG_STAT) · 脚表 Q_CHG_LED.1,Q_CHG_LED.2,Q_CHG_LED.3 · BOM L83 (ref=Q_CHG_LED) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 14 | `Q_ENVC` | MAIN_PCB | `AO3400A` | [官网] | 条件兼容 | 网表 L71,L72,L73 (ref=Q_ENVC, nets=PG_AND+GND+EN_VCORE) · 脚表 Q_ENVC.1,Q_ENVC.2,Q_ENVC.3 · BOM L84 (ref=Q_ENVC) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 15 | `Q_PG` | MAIN_PCB | `DMP3098L` | [官网] | 条件兼容 | 网表 L59,L60,L61 (ref=Q_PG, nets=PWR_ON+BAT_SW+PWR_GOOD) · 脚表 Q_PG.1,Q_PG.2,Q_PG.3 · BOM L85 (ref=Q_PG) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 16 | `R_SUPV_DIV1` | MAIN_PCB | `RC0603JR-070RL` | [官网] | 兼容 | 网表 L404 (ref=R_SUPV_DIV1, nets=V_SOC_IO) · 脚表 R_SUPV_DIV1.1,R_SUPV_DIV1.2 · BOM L147 (ref=R_SUPV_DIV1) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 17 | `R_SUPV_DIV2` | MAIN_PCB | `RC0603JR-070RL` | [官网] | 兼容 | 网表 L405,L406 (ref=R_SUPV_DIV2, nets=SUPV_SENSE+GND) · 脚表 R_SUPV_DIV2.1,R_SUPV_DIV2.2 · BOM L148 (ref=R_SUPV_DIV2) | 不适用 (已落表) | 无需再拍 (已落表) | ★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落 |
| 18 | `SW_BOOT` | MAIN_PCB | `KMR231ULCLFS` | [官网] | 条件兼容 | 网表 L386,L387 (ref=SW_BOOT, nets=BOOT_N+GND) · 脚表 SW_BOOT.1,SW_BOOT.2 · BOM L153 (ref=SW_BOOT) | 是 — 占位 2.20 mm vs gullwing 外扩 4.6 mm ⇒ 必重画 | 落表批次 (main 排期) | 需落表 |
| 19 | `SW_KEY_PWR` | MAIN_PCB | `KMR231ULCLFS` | [官网] | 条件兼容 | 网表 L310,L312 (ref=SW_KEY_PWR, nets=KEY_PWR+GND) · 脚表 SW_KEY_PWR.1,SW_KEY_PWR.2 · BOM L155 (ref=SW_KEY_PWR) | 是 — 同上 | 落表批次 (main 排期) | 需落表 |
| 20 | `SW_KEY_VM` | MAIN_PCB | `B3U-1000P` | [官网] | 条件兼容 | 网表 L320,L322 (ref=SW_KEY_VM, nets=KEY_VOL_M+GND) · 脚表 SW_KEY_VM.1,SW_KEY_VM.2 · BOM L156 (ref=SW_KEY_VM) | 是 — 同上 | 落表批次 (main 排期) | 需落表 |
| 21 | `SW_KEY_VP` | MAIN_PCB | `B3U-1000P` | [官网] | 条件兼容 | 网表 L315,L317 (ref=SW_KEY_VP, nets=KEY_VOL_P+GND) · 脚表 SW_KEY_VP.1,SW_KEY_VP.2 · BOM L157 (ref=SW_KEY_VP) | 是 — 同上 | 落表批次 (main 排期) | 需落表 |
| 22 | `SW_RST` | MAIN_PCB | `KMR231ULCLFS` | [官网] | 条件兼容 | 网表 L382,L383 (ref=SW_RST, nets=RESET_N+GND) · 脚表 SW_RST.1,SW_RST.2 · BOM L158 (ref=SW_RST) | 是 — 同上 | 落表批次 (main 排期) | 需落表 |

- ★`C_REGN` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L43 行的 value='4.7µF ±10% (10V)' / opn='GRM21BR71C475KA73L (Murata 0805 / 4.7µF / 16V / X7R / ±10%)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`D_ESD_CAM` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L58 行的 value='TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)' / opn='TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`D_ESD_DEMO` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L59 行的 value='PESD5V0S1BA (Nexperia 单通道双向 ESD · SOD-323 · VRWM 5V · IRM 5nA)' / opn='PESD5V0S1BA (Nexperia SOD-323 2-lead · VRWM 5V · VBR 6V min · IEC 61000-4-2 >30kV)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`D_ESD_TC` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L61 行的 value='SP0503BAHT (Littelfuse 3 通道 TVS/ESD 阵列 · 5.5V standoff · SOT-143 4 脚)' / opn='SP0503BAHT (Littelfuse · 订购码 SP0503BAHTG · 3 通道 TVS 阵列 · SOT-143-4 · 5.5VWM/8.5VC)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`D_ESD_USB_D` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L62 行的 value='TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)' / opn='TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`D_TVS_VBUS` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L66 行的 value='SMBJ5.0A (Littelfuse 单向 TVS · SMB · VRWM 5.0V · Vc 9.2V@65.3A · 600W)' / opn='SMBJ5.0A (Littelfuse DO-214AA SMB · VRWM 5.0V · VBR 6.4V min · Vc 9.2V @ Ipp 65.3A)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`FB_DEMO` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L67 行的 value='BLM21PG221SN1D (Murata 0805 · 220Ω@100MHz · 2A · DCR 45mΩ max)' / opn='BLM21PG221SN1D (Murata BLM21PG 0805 2012 metric · 220Ω ±25%@100MHz · 2000mA · DCR 45mΩ max)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`FB_VBUS` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L68 行的 value='BLM31PG121SN1 (Murata 1206 · 120Ω@100MHz · 3A · DCR 25mΩ)' / opn='BLM31PG121SN1 (Murata BLM31PG 1206 3216 metric · 120Ω@100MHz · 3000mA · DCR 0.025Ω)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`Q_AND` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L82 行的 value='AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)' / opn='AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`Q_CHG_LED` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L83 行的 value='2N7002 (onsemi N-MOS SOT-23 · VGS(th) max 2.0V · IGSS ≤10nA)' / opn='2N7002 (onsemi SOT-23 3-pin · 60V · RDS(on) 1.2Ω typ@10V · ID 115mA · IGSS ≤10nA)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`Q_ENVC` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L84 行的 value='AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)' / opn='AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`Q_PG` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L85 行的 value='DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)' / opn='DMP3098L (Diodes Inc SOT23 3-pin · −30V · RDS(on) 98mΩ typ@-4.5V · IDSS ≤800nA)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`R_SUPV_DIV1` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L147 行的 value='0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板' / opn='RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次
- ★`R_SUPV_DIV2` 的落表证据 (landed_note): 登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L148 行的 value='0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板' / opn='RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次

★**落表时的通用注意事项**:

1. **行号会随落表漂移** ⇒ 落表器请用 `ref + net` 定位, 不要写死行号。
2. **每件的 value 栏** = 把 `[待选型] ...` 换成型号 + 判据串 (判据串照抄矩阵 §3 的「判据」栏, 一个字不改)。
3. **每件的 opn 栏** = 填矩阵推荐项的**完整型号含变体字母** (例 `TPS22991RAA` 这种带后缀的不能只写 `TPS22991`)。
4. **footprint 栏**: 主板件多数要重画 land (G-7) ⇒ footprint 名可能变 ⇒ 落表时 footprint 与 land 必须同批改, 不能只改网表。
5. **充电板 6 件** (`D_ESD_TC`/`FB_VBUS`/`D_TVS_VBUS`/`Q_CHG_LED`/`D_CHG_LED`) 的封装占位是「待定」 ⇒ 归充电板那一趟 (ISS-243 L4), 主板那一趟不要提前定死。
6. **`C_REGN` 已被并发落表批次落掉** (BOM value 4.7 µF / 10 V + opn 已填, 2026-11-16 15:45 实测) ⇒ **不进落表批次**, 清单里保留该行只作登记。
7. **`R_SUPV_DIV1/2`** 在 G-10 拍板前, **建议先不填最终阻值** ⇒ 若采纳「随 U_SUPV 一并 DNP」, 直接把两行的 dnp 改成 DNP。

## §5 ★落表后回归 (2026-11-17 05:0x 实测) — H-1 重锚第 1 跳

★**背景**: ISS-244 第一轮交卷 (2026-11-16 15:59) 之后, 板侧又落了一批选型件 (网表 / 脚表 / BOM 落盘时刻 = **2026-11-16 22:25:14**) ⇒ 登记范围 22 件里 **14 件已落表 / 8 件仍待落** ⇒ 本单门禁 C5 **按设计变红** (锚点过期 = 红 ⇒ 走 H-1 重锚 + 留痕, **不许把红灯调没**)。

⇒ 本轮按 **H-1 重锚第 1 跳** 处理: ① 重算每一行的 `landed_note` (落表证据) ② 按盘上真值**重判**十条缺口的状态 ③ 新增本节的**落表后回归表** (三方交叉核对) ④ 收口页正文与机器可读基准块**同源** (都由 `state/.cache_iss244/build_closout.py` 生成)。

### §5.1 「板占位 land ↔ 器件引脚序 ↔ 网表 note 角色」三方交叉核对 (逐件实读)

★**为什么加这一节**: ISS-244 第一轮只给了「占位 land 与在售器件的 land 普遍不重合」这个**几何层**的结论 (G-7); 板侧把料真正落下来之后, 才第一次有可能回答更致命的那一层: **★落地的器件, 装到现在的占位焊盘上, 引脚还对不对得上★** ⇒ 本节把三份盘上真源摆到一张表里逐件对: ① `HW/PCB/demo_mainboard.kicad_pcb` 的 pad→net (占位 land) ② `HW/netlist_v1.csv` 每行的 note 写的端子角色 ③ 厂商手册的引脚序。

| 位号 | 落地型号 | 器件引脚序 (官方 PDF 实读) | 板占位 land (pad→net) | 网表 note 定的角色 | 判定 | 要改哪几处 |
|---|---|---|---|---|---|---|
| `C_REGN` | `4.7µF ±10%` | – | 板文件查无此位号 | – | **– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判** | – |
| `D_ESD_CAM` | `TPD1E05U06DPYR` | pin1=I/O<br>pin2=GND | pad1=GND<br>pad2=CSI_D0_CK_P | GND=GND<br>CSI_D0_CK_P=I/O | **★P0 (引脚序/角色级): ✘ 占位 land 与器件引脚序对不上** | 板侧改 land: pad1: GND → CSI_D0_CK_P; pad2: CSI_D0_CK_P → GND |
| `D_ESD_DEMO` | `PESD5V0S1BA` | – | pad1=RAIL_DEMO_5V<br>pad2=GND | – | **– 双向件 ⇒ 极性无关, 不参与引脚序判定** | – |
| `D_ESD_TC` | `SP0503BAHT` | – | 板文件查无此位号 | – | **– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判** | – |
| `D_ESD_USB_D` | `TPD1E05U06DPYR` | pin1=I/O<br>pin2=GND | pad1=USB_D_P_SRC<br>pad2=GND | USB_D_P_SRC=I/O<br>GND=GND | **✔ 引脚序与占位 land 对得上** | – |
| `D_TVS_VBUS` | `SMBJ5.0A` | – | 板文件查无此位号 | – | **– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判** | – |
| `FB_DEMO` | `BLM21PG221SN1D` | – | pad1=RAIL_DEMO_5V<br>pad2=GND | – | **– 无源件 / 不引脚序敏感 ⇒ 只差 land 几何 (G-7)** | – |
| `FB_VBUS` | `BLM31PG121SN1` | – | 板文件查无此位号 | – | **– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判** | – |
| `Q_AND` | `AO3400A` | pin1=G<br>pin2=S<br>pin3=D | pad1=RESET_N<br>pad2=GND<br>pad3=PG_AND | RESET_N=D<br>GND=S<br>PG_AND=G | **★P0 (引脚序/角色级): ✘ 占位 land 与器件引脚序对不上** | 板侧改 land: pad1: RESET_N → PG_AND; pad3: PG_AND → RESET_N |
| `Q_CHG_LED` | `2N7002` | – | 板文件查无此位号 | – | **– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判** | – |
| `Q_ENVC` | `AO3400A` | pin1=G<br>pin2=S<br>pin3=D | pad1=PG_AND<br>pad2=GND<br>pad3=EN_VCORE | PG_AND=G<br>GND=S<br>EN_VCORE=D | **✔ 引脚序与占位 land 对得上** | – |
| `Q_PG` | `DMP3098L` | pin1=G<br>pin2=S<br>pin3=D | pad1=PWR_ON<br>pad2=BAT_SW<br>pad3=PWR_GOOD | PWR_ON=S<br>BAT_SW=D<br>PWR_GOOD=G | **★P0 (引脚序/角色级): ✘ 占位 land 与器件引脚序对不上** | 板侧改 land: pad1: PWR_ON → PWR_GOOD; pad3: PWR_GOOD → PWR_ON  ★**同时网表 note 的角色必须同批改成写法A (S=BAT_SW / D=ON / G=PG)** ⇒ 否则按 note 的错角色排出来的 land 一样开机不通 |
| `R_SUPV_DIV1` | `0Ω ±1% 跳线` | – | pad1=V_SOC_IO<br>pad2=SUPV_SENSE | – | **★P0 (装配级): 0 Ω 且必装 + U_SUPV DNP ⇒ 短路到地 (见拓扑备注)** | 见 §5.2 拓扑备注 |
| `R_SUPV_DIV2` | `0Ω ±1% 跳线` | – | pad1=SUPV_SENSE<br>pad2=GND | – | **★P0 (装配级): 0 Ω 且必装 + U_SUPV DNP ⇒ 短路到地 (见拓扑备注)** | 见 §5.2 拓扑备注 |

★**引脚序的出处与分级 (不许混成一条)**:

- `TPD1E05U06DPYR`: TI `SLVSBO7O` Table 4-1 原文「**GND = pin 2 / I/O = pin 1**」⇒ **[官网]** (本轮实读, 落盘 `state/.cache_iss244/led/tpd4e05u06.pdf`, 10 页)。
- `AO3400A` / `DMP3098L`: 厂商手册 p1 的 Pin Configuration **图上没印引脚号** ⇒ 本节只把「**排布** (G/S 在一侧, D 在另一侧)」当 **[官网·图读]**, 而「哪一根是 1/2/3」按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ **[推算]** ⇒ ★**两层分开标注, 不合并成 [官网]★**。
- `PESD5V0S1BA`: 双向件 ⇒ 极性无关 ⇒ 不参与引脚序判定。

### §5.2 ★三条 P0 (板那一趟必须同批改, 否则板子出来就是坏的)

**P0-a · `Q_PG` — 开机路径不通 (角色本身就错 + land 也不对)**:

- **网表 note 的角色 = 错接**: `HW/netlist_v1.csv` L58 note 的「正解」段写「源极接 ON · 漏极接 BAT_SW · 栅极接 PG」 ⇒ 这就是 ISS-244 §3.3 的**写法B**: 上电瞬间 ON 被 10 kΩ 下拉到 0 V ⇒ Vgs = 0 − 0 = **0 V** ⇒ 不导通; PG 高时 Vgs = **+3.3 V** (对 P 沟道是反向偏置) ⇒ **PG 高低都关 ⇒ 开机路径彻底不通**。⇒ ★**唯一电学自洽的是写法A: S=BAT_SW / D=ON / G=PG**★ (PG 低 ⇒ Vgs = 0 − 4.2 = **−4.2 V** ⇒ 导通 ⇒ ON 被拉到 BAT_SW ⇒ 开机)。
- **落地的器件引脚序 = G-S-D**: `DMP3098L` (Diodes) pin1=G / pin2=S / pin3=D ⇒ ★**按写法A 排, land 目标 = pad1=PWR_GOOD(G) / pad2=BAT_SW(S) / pad3=PWR_ON(D)**★ ⇒ 现在占位是 pad1=PWR_ON / pad2=BAT_SW / pad3=PWR_GOOD ⇒ ★**只需把两个外侧 pad 的网名对调 (pad1 ↔ pad3), pad2 不动**★。
- ⇒ **落表批次 + 板那一趟要一起做的两件事**: ① 网表 note 的角色措辞改成写法A (本单不改网表) ② land 把 pad1/pad3 的网名对调。
- ★**顺带订正 ISS-244 第一轮的降级①**: 当时写「写法A 需要 D-S-G 引脚序器件, 在售件 [0数据]」⇒ ★**本轮实读证明: 用已落地的 G-S-D 器件 (DMP3098L) + 板侧对调两个外侧 pad 就够, 不需要买 D-S-G 器件**★。

**P0-b · `Q_AND` — 栅/漏对调 (复位链的硬件 AND 门不成立)**:

- 网表 note 的角色是对的 (L64 漏极=RESET_N / L65 源极=GND / L66 栅极=PG_AND) ⇒ ★**但落地的 `AO3400A` 引脚序是 pin1=G / pin2=S / pin3=D**★ ⇒ 现在的占位 (pad1=RESET_N / pad2=GND / pad3=PG_AND) 装上去 = **栅极接 RESET_N、漏极接 PG_AND** ⇒ 复位链的硬件 AND 门不成立。
- ⇒ **land 目标 = pad1=PG_AND(G) / pad2=GND(S) / pad3=RESET_N(D)** ⇒ 同样是**两个外侧 pad 对调**。
- ★**对照**: `Q_ENVC` 的占位 (pad1=PG_AND / pad2=GND / pad3=EN_VCORE) 与 `AO3400A` 的 G-S-D **正好对上** ⇒ ★**三颗 MOS 里只有这一颗不用动 land**★。

**P0-c · `D_ESD_CAM` — ESD 器件接反 (跨铰链 CSI 时钟线既没保护又被钳)**:

- 落地件 `TPD1E05U06DPYR`: pin1 = **I/O**, pin2 = **GND** (TI Table 4-1, 原文) ⇒ 而占位 land 是 **pad1=GND / pad2=CSI_D0_CK_P** ⇒ ★**正好相反**★。
- ⇒ 装上去: 器件的 I/O 脚接地、器件的 GND 脚接信号 ⇒ **正向 ESD 到地无通路 (保护失效)** + **CSI lane 的负向摆幅被内部二极管钳到 GND 附近**。
- ⇒ **land 目标 = pad1=CSI_D0_CK_P(I/O) / pad2=GND** ⇒ 两个 pad 对调 (ISS-241 §3 的候选1 栏已预告过这条, 本轮落到实物)。

★**另外两条「不是 P0 但必须同批」**: ① `R_SUPV_DIV1/2` 已落成 **0 Ω 跳线且 dnp=必装**, 而 `U_SUPV` 三行 dnp=**DNP** ⇒ **装 0 Ω = 把 `V_SOC_IO` 经两臂短路到地** (ISS-190 同判) ⇒ 建议随 `U_SUPV` 一并置 DNP (G-10 降级①); ② `D_ESD_TC` 落的是 **3 通道** `SP0503BAHT`, 而网表只接了 1 个通道 (USB_VBUS_RAW) + GND ⇒ **另 2 个通道闲置** ⇒ Type-C 的 D+/D− 仍未被这阵列覆盖。

### §5.3 十条缺口按落表后的盘上真值重判

| 缺口 | 落表后的盘上真值 (2026-11-17 05:0x 实读) | 本轮变化 | 状态 |
|---|---|---|---|
| **G-1** | `Q_PG` 已落 `DMP3098L` (G-S-D) + 网表 note 仍是**写法B 的错角色** + 占位 land 也不对 ⇒ **三方互不一致** | ★由「note 措辞矛盾」升级成**实物级 P0** (§5.2 P0-a), 并给出**只对调两个外侧 pad** 的最小修法 | 需老板拍 (写法) + 需落表 + 需板那一趟 |
| **G-2** | 3 颗 MOS 的占位 pad 序 = 网表行序 (`Q_AND`=D/S/G · `Q_PG`=S/D/G · `Q_ENVC`=G/S/D) ⇒ **与落地的 G-S-D 器件逐件核对后: 2 颗不符, 1 颗相符** | ★由「三件都不同」精确到**逐件结论 + 目标 pad→网** (§5.1 / §5.2) | 已转单 (hw-lead 板那一趟) · 追加 P0-b |
| **G-3** | `D_ESD_CAM` 已落 `TPD1E05U06DPYR` (**单通道**) ⇒ CSI-2 五对差分共 10 条线仍只有 `CSI_D0_CK_P` 一条有保护 ⇒ **9 条裸奔**; 且这颗的 pad↔pin **接反** | ★保护范围结论不变, 但**新增「接反」这条实物级缺陷** (§5.2 P0-c) | 需老板拍 (V-2) · 依据与代价已备齐 |
| **G-4** | `D_ESD_USB_D` 已落 `TPD1E05U06DPYR` (**单通道**, 引脚序对得上) ⇒ `USB_D_N_SRC` 仍无保护 ⇒ **D− 裸奔**; 另一颗 `D_ESD_TC` 是 3 通道件但只接了 1 通道 | ★**从「设计缺口」变成「已落地的缺口」** ⇒ 现在是**已装机状态**下的实际风险, 不是「还没选」 | 需老板拍 (V-2) · 依据与代价已备齐 |
| **G-5** | LED 四颗 (`D_LED_R` / `D_LED_G` / `D_CHG_LED` / 2 颗按键 LED) 仍**待选型** ⇒ 1 kΩ 串阻 + 3.3 V ⇒ 0.8~1.35 mA 的工作点**仍未改**; 厂商曲线数字化结论 (1 mA 档 = 标称亮度的 4.8%~7.2%) 不受落表影响 | 无变化 (这三条仍待落 ⇒ 亮度档仍需老板拍) | 需老板拍 (亮度档) + 需落表 (若选改 R) |
| **G-6** | `C_REGN` 已落 4.7 µF / 10 V (Murata 0805, X7R) ⇒ 与 TI BQ25896 pin22 手册一致 | ★**已闭合** (落表证据见 §4 landed_note) | 已闭合 |
| **G-7** | 主板在册件的占位 land 仍与厂商 land 不重合 (ESD 占位 2.30 mm 间距 vs X1SON 0.65 mm; MOS 占位 1.27~1.53 mm vs SOT-23 0.95 mm; FB_DEMO 占位 0.8 mm vs 0805) ⇒ **本轮又多了 13 件已落地的实物可核** | ★范围扩大 (14 件已落表 ⇒ 几何结论可逐件核) | 已转单 (hw-lead 板那一趟) · 与 G-1/G-2 同批 |
| **G-8** | 6 件充电板器件 (`D_ESD_TC`/`FB_VBUS`/`D_TVS_VBUS`/`Q_CHG_LED`/`D_CHG_LED`/`C_REGN`) 里 **5 件已落型号**, 但**板文件里查无此位号** ⇒ 封装占位仍「待定」 | ★型号已落 ≠ 封装已定 ⇒ 落表批次仍需另补 footprint | 已转单 (ISS-243 L4) · 已闭合 |
| **G-9** | 登记范围 = 22 (不变) / 当前仍待落 = **8** (`D_CHG_LED`, `D_LED_G`, `D_LED_R`, `SW_BOOT`, `SW_KEY_PWR`, `SW_KEY_VM`, `SW_KEY_VP`, `SW_RST`) ⇒ 两个数都要写, 来源都注明 | ★口径差从 1 件扩大到 13 件 (全部是被并发落表批次合法落掉的) ⇒ 本单门禁 C5 按双源判定 | 已闭合 |
| **G-10** | `R_SUPV_DIV1/2` 已落成 **0 Ω 跳线 (RC0603JR-070RL) 且 dnp=必装**, 而 `U_SUPV` 三行 dnp=**DNP** ⇒ **短路到地的风险已从「设计缺陷」变成「装机缺陷」** | ★由「阻塞在阻值算不出」变成**「阻塞在要不要装」** ⇒ 降级① (两臂随 U_SUPV 一并 DNP) 变成零成本动作 | 需老板拍 + 需落表 |

## §6 出处表

| # | 出处 | 类型 | 支持的结论 | 落盘位置 |
|---|---|---|---|---|
| S1 | Kingbright `AA1608SURSK` 数据手册 Ver.3A (4 页) 第 3 页 4 格图第 2 格 + 第 1 页 SELECTION GUIDE | [官网] | D_LED_R 的 Iv-vs-If 归一化曲线 (数字化 ⇒ 1 mA 档 5.10 %) + Iv 40/160 mcd @20 mA | `state/.cache_iss244/led/AA1608SURSK_kingbright.pdf` |
| S2 | Kingbright `APT1608SURCK` 数据手册 Ver.22A (4 页) 第 3 页 + 第 1 页 | [官网] | D_CHG_LED 的 Iv-vs-If 曲线 (1 mA 档 5.10 %) + Iv 40/80 mcd @20 mA | `state/.cache_iss244/led/APT1608SURCK_kingbright.pdf` |
| S3 | Kingbright `APH1608SURCK` / `APH1608SGC` / `AP2012CGCK` 三份数据手册 | [官网] | ★跨型号交叉印证 1 mA 档 (4.77% / 5.24% / 7.19%) ⇒ 证明数字化方法本身准 | `state/.cache_iss244/led/led_aph1608surck.pdf` 等 |
| S4 | Kingbright `KP-2012SGC` 数据手册 DSAB1341 V.18B 第 2 页 SELECTION GUIDE + 特性表 | [官网] | D_LED_G 的 Iv 5/12 mcd @20 mA + VF 2.2/2.5 V @20 mA (★曲线是位图 ⇒ 1 mA 档用同厂同尺寸绿代理 ⇒ 该档标 [推算]) | `state/.cache_iss244/led/KP-2012SGC_farnell.pdf` |
| S5 | ★数字化脚本 (坐标轴标定取自 PDF 文本层 + RANSAC 提迹线 + 3 条自证) | [实测] | G-5 的全部 1 mA 档数字 ⇒ 可一条命令复跑 | `state/.cache_iss244/led/extract_ivif.py` (+ `ivif_*.json`) |
| S6 | TI `SLVAF82B`《ESD and Surge Protection for USB Interfaces》Rev. B (19 页) | [官网] | G-3/G-4 的业界依据: each data line / 紧贴连接器 / USB 2.0 Cd < 4 pF | `state/.cache_iss244/ref/ti_slvaf82_usb_esd.pdf` |
| S7 | Würth Elektronik `ANP002`《The protection of USB 2.0 applications》§7 Fig.9 / Fig.11 | [官网] | G-4: 单通道器件的业界通行做法也是 D+ / D− 各一颗 | (线上原件, 站点对本机 curl 返回 HTML ⇒ 只引用章节号与图号) |
| S8 | TI `TPD2E2U06` Rev. C + `TPDxE05U06` Rev. O 数据手册 | [官网] | G-3/G-4 的代价量化: 双通道 Cd 1.5/1.9 pF; 多通道 0.42 pF | `state/.cache_iss244/led/tpd2e2u06.pdf` / `tpd6e05u06.pdf` |
| S9 | AOS `AO3407A` 官方数据手册 (5 页) + Diodes `DMP3098L` (5 页) | [官网] | G-1: P 沟道 VGS 极性与阈值定义 + SOT-23 引脚序 G/S/D | `state/.cache_iss244/mos/AO3407A.pdf` / `DMP3098L.pdf` |
| S10 | TI `TPS3808` 数据手册 SBVS050N Rev. N (36 页) §7.3.1 + Figure 7-1 + Ordering Information | [官网] | G-10: V_IT = (1 + R1/R2) × 0.405 V, R1+R2 = 4 MΩ, 阈值精度/迟滞 | `state/.cache_iss244/ref/tps3808.pdf` |
| S11 | ★分压候选表计算脚本 | [推算] | G-10 的三档候选阻值 + E96 取值 + 误差带 | `state/.cache_iss244/supv_divider_solve.py` |
| S12 | 网表 / 脚表 / BOM / 板文件 实读 | [实测] | G-3/G-4 的「只护一边」事实 + G-5 的 1 kΩ 事实 + G-10 的 dnp 事实 + 22 件的落表锚点 | `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/PCB/demo_mainboard.kicad_pcb` |
| S13 | ★TI `TPD4E05U06` 数据手册 SLVSBO7O (2024-08 改版, 10 页) Table 4-1 + Figure 4-1 (DPY 2-Pin X1SON Top View) | [官网] | §5.1 的 `TPD1E05U06DPYR` 引脚序: **GND = pin 2 / I/O = pin 1** ⇒ `D_ESD_CAM` 占位 land (pad1=GND) 接反 ⇒ P0-c | `state/.cache_iss244/led/tpd4e05u06.pdf` |
| S14 | AOS `AO3400A` (5 页) p1 Pin Configuration 图 + Diodes `DMP3098L` (5 页) p1 Pin Configuration 图 | [官网·图读] + 编号 [推算] | §5.1 的 `AO3400A` / `DMP3098L` 引脚序: 排布 G/S 一侧 + D 另一侧 (**图上未印引脚号**) ⇒ 编号按 JEDEC TO-236 ⇒ P0-a / P0-b | `state/.cache_iss244/mos/AO3400A.pdf` / `DMP3098L.pdf` |
| S15 | ★落表后回归计算模块 (板文件 pad→net + 网表 note 角色 + 器件引脚序 三方交叉核对) | [实测] | §5.1 逐件结论 + §5.2 三条 P0 的最小修法 ⇒ 一条命令可复跑 | `state/.cache_iss244/post_landing.py` |

## §7 自证复现命令

```bash
# ① 件数 (两个机器派生源, 都不抄硬编码数字)
python3 - <<'EOF'
import csv, json, re
rows=list(csv.DictReader(open("HW/BOM_v1.csv",encoding="utf-8")))
pend=[r["ref"] for r in rows if "待选型" in r["value"] and r["dnp"]=="必装" and r["ref"] not in ("U_PWR_SW","U_EN_SW")]
t=open("HW/PART_SELECTION_MATRIX_2026-11-16.md",encoding="utf-8").read()
b=t.split("<!-- BEGIN 选型证据基准块 -->")[1].split("<!-- END 选型证据基准块 -->")[0]
scope=json.loads(re.sub(r"```json|```","",b.strip()))["expected_refs"]
print("ISS-241 登记范围 =",len(scope))
print("当前仍待落 =",len(pend))
print("已被并发落表落掉 =",[r for r in scope if r not in pend])
EOF

# ② G-5 曲线数字化 (四条自证 + 逐件 JSON)
python3 state/.cache_iss244/led/extract_ivif.py \
        state/.cache_iss244/led/AA1608SURSK_kingbright.pdf 3 \
        --json state/.cache_iss244/led/ivif_aa1608sursk.json
python3 state/.cache_iss244/led/extract_ivif.py --selftest

# ③ G-10 分压候选表
python3 state/.cache_iss244/supv_divider_solve.py

# ④ 本单机器门禁 + 反向用例
python3 HW/check_part_selection_gaps.py             # rc=0
python3 HW/check_part_selection_gaps.py --selftest   # rc=0

# ④b 落表后回归 (三方交叉核对)
python3 state/.cache_iss244/post_landing.py

# ⑤ 上游门禁 (ISS-241) 不许被本单改红
python3 HW/check_part_selection_matrix.py && python3 HW/check_part_selection_matrix.py --selftest
```

## §8 ★机器可读基准块 (门禁脚本读这一块)

<!-- BEGIN ISS244 缺口收口基准块 -->
```json
{
  "issue": "ISS-244",
  "author": "sw-lead",
  "generated": "2026-11-16",
  "reanchor_note": "★H-1 重锚第 1 跳 (2026-11-17 05:0x): 板侧又落了一批 (网表/脚表/BOM 落盘时刻 2026-11-16 22:25:14) ⇒ 登记范围 22 件里 14 件已落表 / 8 件仍待落 ⇒ 本单的 landed_note 与 §5 落表后回归表按盘上真值重算",
  "scope_note": "本块由 state/.cache_iss244/build_closout.py 生成 ⇒ 表与块同源, 改数据只改脚本。落表锚点里的网表/脚表/BOM 行号会在落表批次后漂移 ⇒ ★锚点以 ref+net 为准★。",
  "gap_count": 10,
  "opn_row_count": 22,
  "scope_refs": [
    "C_REGN",
    "D_CHG_LED",
    "D_ESD_CAM",
    "D_ESD_DEMO",
    "D_ESD_TC",
    "D_ESD_USB_D",
    "D_LED_G",
    "D_LED_R",
    "D_TVS_VBUS",
    "FB_DEMO",
    "FB_VBUS",
    "Q_AND",
    "Q_CHG_LED",
    "Q_ENVC",
    "Q_PG",
    "R_SUPV_DIV1",
    "R_SUPV_DIV2",
    "SW_BOOT",
    "SW_KEY_PWR",
    "SW_KEY_VM",
    "SW_KEY_VP",
    "SW_RST"
  ],
  "pending_refs": [
    "D_CHG_LED",
    "D_LED_G",
    "D_LED_R",
    "SW_BOOT",
    "SW_KEY_PWR",
    "SW_KEY_VM",
    "SW_KEY_VP",
    "SW_RST"
  ],
  "landed_elsewhere": [
    "C_REGN",
    "D_ESD_CAM",
    "D_ESD_DEMO",
    "D_ESD_TC",
    "D_ESD_USB_D",
    "D_TVS_VBUS",
    "FB_DEMO",
    "FB_VBUS",
    "Q_AND",
    "Q_CHG_LED",
    "Q_ENVC",
    "Q_PG",
    "R_SUPV_DIV1",
    "R_SUPV_DIV2"
  ],
  "gaps": [
    {
      "id": "G-1",
      "evidence_level": "[官网]",
      "source": "① AOS `AO3407A` 官方数据手册 (落盘 `state/.cache_iss244/mos/AO3407A.pdf`, 5 页): p1 首行标题「30V P-Channel MOSFET」; 特性表 VGS(th) min −1.4 / typ −1.9 / max −2.4 V (VDS=VGS, ID=−250 mA); VGS 绝对最大 ±20 V; RDS(ON) 78 mΩ max @VGS=−4.5 V; IDSS ≤1 µA@25 °C / ≤5 µA@55 °C; 引脚定义 pin1=G pin2=S pin3=D。② Diodes Inc `DMP3098L` 官方数据手册 (落盘 `state/.cache_iss244/mos/DMP3098L.pdf`, 5 页): p1 引脚配置图 Drain / Gate / Source; VGS(th) −1.0 / −1.8 / −2.1 V; IDSS ≤800 nA @VDS=−30 V; RDS(on) 98/120 mΩ @−4.5 V; VGS 绝对最大栏手册未给 ⇒ 该项 [0数据]。③ 网表原文 `HW/netlist_v1.csv` L59/L60/L61 三行 (Q_PG 的 PWR_ON / BAT_SW / PWR_GOOD) —— L59 的 note 同时写了首句与「正解」两种写法。④ 板文件 pad↔net 实读 (ISS-241 §5 S21, 本单只读不改)。",
      "fallback": "降级 ① (不改板, 换引脚序): 选**引脚序 = D-S-G** 的 P 沟道 SOT-23 ⇒ 板占位不动; 代价 = 本轮只核到 AO3407A (G-S-D) 与 DMP3098L (D-S-G 之外的常见序) ⇒ **D-S-G 序的在售件本轮 [0数据]**, 落表批次按此口径复核。降级 ② (改 land, 换标准器件): 选 G-S-D 序器件 (AO3407A) ⇒ 落板批次把 pad 重新对应到 BAT_SW→S / ON→D / PG→G ⇒ 代价 = 重画 land (归板那一趟) + 必须逐焊盘核 pad↔pin。降级 ③ (换拓扑, 不换器件): 把 Q_PG 改回 N 沟道低边 ⇒ 与 V1.9 的改动方向相反 ⇒ 代价 = V1.9 已判 N-MOS 低边「开机路径彻底不通」, 这条实际不成立, 只作记录。★三个降级都要 main/PM 拍, 本单不代拍。",
      "remaining": "① 拍板: 写法A 还是写法B (本单建议 A, 但**不代拍**); ② 拍板: D-S-G 器件存在与否 (落表批次复核); ③ 拍板: 是否重画 land (板那一趟)。",
      "status": "需老板拍 + 需落表",
      "gap": "Q_PG 源漏拓扑: 网表 note 首句与 note 正文自述的「正解」自相矛盾",
      "scope": "main / PM (属原理图 + 落表 + 板那一趟)",
      "self_check_result": "★**本轮已把两种写法各自的电学后果算出来, 不再是「措辞矛盾」这种描述性缺口**: 写法A (note 正文自述的正解) = 源极 S 接 BAT_SW (高电位侧) / 漏极 D 接 ON (负载侧) / 栅极 G 接 PG: PG 低(电源良好)=0 V ⇒ VGS = VG − VS = 0 − 4.2 = **−4.2 V** ⇒ |VGS| 4.2 V > |VGS(th)max| 2.4 V ⇒ 导通 ⇒ ON 被拉到 BAT_SW ⇒ 开机; PG 高(无输入)=3.3 V ⇒ VGS = 3.3 − 4.2 = **−0.9 V** ⇒ |VGS| 0.9 V < |VGS(th)min| 1.4 V ⇒ 关断 ⇒ 关机态仍能充电 ⇒ **逻辑自洽**。写法B (note 首句直译) = 源极 S 接 ON / 漏极 D 接 BAT_SW: 上电瞬间 ON 被 R_PD_ON 10 kΩ 下拉到 0 V ⇒ VGS = 0 − 0 = **0 V** ⇒ |VGS| 0 < |VGS(th)min| ⇒ **不导通**; 且 PG 高时 VGS = 3.3 − 0 = **+3.3 V** (对 P 沟道是反向偏置, 体二极管也不导) ⇒ **PG 高低都关 ⇒ 开机路径彻底不通**。⇒ 结论: note 首句「源极接 ON · 漏极接 BAT_SW」与 note 正文自述的「Vgs≈−4.2V ⇒ 导通 ⇒ 开机」**互斥** ⇒ 首句必须改, 否则板子装出来开不了机。★**连带一条落表前置**: 板占位 pad1=PWR_ON / pad2=BAT_SW / pad3=PWR_GOOD; 若按写法A (BAT_SW→S, ON→D, PG→G) ⇒ 需要器件引脚序 = pad1:D / pad2:S / pad3:G, 而 SOT-23 库标准引脚序是 G/S/D (AO3407A 明写 pin1=G pin2=S pin3=D) ⇒ **要么选 D-S-G 序的 P-MOS, 要么重画 land** ⇒ 这是 G-2 的升级版, 不是 G-2 能盖住的。"
    },
    {
      "id": "G-2",
      "evidence_level": "[实测]",
      "source": "ISS-241 §4 缺口 G-2 + §5 S21 (板文件逐焊盘 at/size/net 实读); 本单只读板文件, 未写入任何板文件。",
      "fallback": "降级 = 选**引脚序与占位 pad 顺序一致**的器件 ⇒ 本轮在售 SOT-23 绝大多数是 G-S-D ⇒ 此路实际不通 ⇒ 实际等价于「必须重画 land」。⇒ 落板批次把 G-2 与 G-1 合并成一次 land 重画, 避免重画两遍。",
      "remaining": "land 重画时 pad↔pin 映射表 (G-1 裁决后才能定稿)。",
      "status": "已转单 (hw-lead 板那一趟) · 与 G-1 同批",
      "gap": "占位焊盘的 pad 序号 = 网表行顺序, 不是库封装的 G/S/D 顺序",
      "scope": "hw-lead (板那一趟) + 落表批次",
      "self_check_result": "三件 MOS 的 pad↔pin 映射三样都不同 (`Q_AND`=D/S/G, `Q_ENVC`=G/S/D, `Q_PG`=S/D/G), 换任何 SOT-23 器件都必须逐件重画 land 并核 pin 映射。★本轮补充一条: 这条在 G-1 裁决为「写法A」之后会**升级** —— 需要的器件引脚序变成 D-S-G, 与库标准 G-S-D 不符 ⇒ G-2 与 G-1 必须同批处理, 不能分两趟。"
    },
    {
      "id": "G-3",
      "evidence_level": "[官网]",
      "source": "① TI `SLVAF82B` (落盘 `state/.cache_iss244/ref/ti_slvaf82_usb_esd.pdf`) §3.2 段 + §4「Capacitance (D+, D-)」; ② TI `TPDxE05U06` 数据手册 (落盘 `state/.cache_iss244/led/tpd6e05u06.pdf`) p1「IO capacitance 0.42pF to 0.5pF (typical)」; ③ 网表 `HW/netlist_v1.csv` L413/L414 (D_ESD_CAM 两行) + L250~L269 (10 条 CSI 线与 AC 耦合电容); ④ 板文件 pad 实读 (ISS-241 §5 S21)。",
      "fallback": "降级 ① (不改板, 只把现有 2 焊盘位用足): 维持单边 ⇒ 代价 = 9 条高速差分线裸奔, 一次 ESD 就可能打死相机链路 (CSI-2 无重传兜底)。降级 ② (改板, 加 6 通道件): 一颗 `TPD6E05U06` (6 通道 / 0.42 pF) 覆盖 CK_P/N + D0_P/N + D1_P/N (6 条) ⇒ 代价 = +4 焊盘 + 约 3.8 mm² 面积; 剩余 D2/D3 四条线仍无 ⇒ 需第二颗 4 通道件。降级 ③ (改板, 分层保护): 把 ESD 放在**靠近 SoM 侧**而不是连接器侧 ⇒ 代价 = 违反 TI「紧贴 ESD 源」的布局原则, 不推荐。★本单只列代价, **不代拍 V-2**。",
      "remaining": "V-2 (ESD 方案二选一) 由 PM/老板拍: 保持单边 / 改板加多通道。",
      "status": "需老板拍 (V-2) · 依据与代价已备齐",
      "gap": "CSI-2 ESD 只覆盖 1 条 lane (10 条高速差分线里 9 条无 ESD 占位)",
      "scope": "PM (ESD 方案口径 = V-2 二选一) · sw-lead 只出依据 + 代价",
      "self_check_result": "实测: `D_ESD_CAM` 在网表上只有两个焊盘 (GND + CSI_D0_CK_P) ⇒ 只护 clock lane 的**正相**一根。而本板 CSI-2 在网表上是 **5 对差分 = 10 条线** (CSI_D0_CK_P/N + CSI_D0_D0_P/N + CSI_D0_D1_P/N + CSI_D0_D2_P/N + CSI_D0_D3_P/N, 各经 100 nF AC 耦合电容到 CONN_CAM pin2/3/5/6/11/12/14/15/17/18) ⇒ **CK_N 与 D0~D3 的正负两根共 9 条线没有任何 ESD 占位**。★业界依据 (本轮新查): TI 官方应用文档 `SLVAF82B`《ESD and Surge Protection for USB Interfaces》(Rev. B, 2024-01, 19 页, 落盘 `state/.cache_iss244/ref/ti_slvaf82_usb_esd.pdf`) §3.2/§4 写明两条硬原则: ①「the diodes are connected to **each data line**」且例图用 ESD321 **同时护 D+ 与 D−**; ②「place the diodes **as close to the source of ESD**, in this case the connector, as design rules allow」。同一原则套到 CSI-2 ⇒ **每条 lane 的正负两根都要护**; 本项目网表 L417 note 已引 Forlinx 载板指引的同一条「ESD 紧贴接口」要求。★代价 (可量化): ① 焊盘数: 2 焊盘单通道件 → 6 通道件 6 焊盘 (+4); ② 面积: 单通道 `TPD1E05U06DPYR` (X1SON 0.5×0.5 mm, 落盘 `state/.cache_iss244/led/tpd6e05u06.pdf` 同族) → 6 通道 `TPD6E05U06` (SOT-23-6, 2.9×1.3 mm) ⇒ 本体面积约 ×15; ③ 结电容: **不是瓶颈** —— `TPD6E05U06` 官方 IO 电容 0.42 pF typ, 与单通道 `TPD1E05U06` 同档 ⇒ 双边保护可以不付结电容的代价, 只付焊盘与面积。"
    },
    {
      "id": "G-4",
      "evidence_level": "[官网]",
      "source": "① TI `SLVAF82B` (落盘 `state/.cache_iss244/ref/ti_slvaf82_usb_esd.pdf`): §3.2 (each data line / ESD321 护 D+ 与 D− / 紧贴连接器) + §4「Capacitance (D+, D-): ... less than 4 pF is recommended」; ② Würth `ANP002` §7 Figure 9 / Figure 11 (D+ / D− 各一颗, 单通道器件同样两条线都护); ③ TI `TPD2E2U06` 数据手册 Rev. C (落盘 `state/.cache_iss244/led/tpd2e2u06.pdf`): CL 1.5 pF typ / 1.9 pF max, CCROSS 0.02 pF, ΔCIO-TO-GND 0.03/0.1 pF; ④ 网表 `HW/netlist_v1.csv` L417/L418 (D_ESD_USB_D 两行); ⑤ ISS-190 §7-7 已登记同一事实 (本单只引用, 未改 SW/ 任何文件)。",
      "fallback": "降级 ① (不改板): 维持单边 ⇒ 代价 = D− 裸奔, 而 J_USB_C 是板内**唯一的刷写口** ⇒ 一次 ESD 打到 D− 就只能拆机 JTAG (与 ISS-190 §7-7 同口径)。降级 ② (改板, 双通道件): 换 `TPD2E2U06` (SOT-23-3, 3 焊盘) ⇒ 代价 = 焊盘 +1 + 面积增加, 结电容 1.9 pF max 仍 < TI 的 4 pF 判据 ⇒ **对 USB 2.0 上升沿无实质影响**。降级 ③ (改板, 换更小封装双通道): 找 X1SON/X2SON 双通道低容值件 ⇒ 代价 = 本轮只核到 TI 一家的双通道官方手册, 其它厂双通道在售件的 Cd 本轮 [0数据], 落表批次补。★不代拍 V-2。",
      "remaining": "V-2 拍板 + 若选双边, 落表批次定双通道具体型号 (Cd < 4 pF 判据已定死)。",
      "status": "需老板拍 (V-2) · 依据与代价已备齐",
      "gap": "USB 2.0 只保护 D+, D− (USB_D_N_SRC) 无 ESD 占位",
      "scope": "PM (同上, V-2) · sw-lead 只出依据 + 代价",
      "self_check_result": "实测: `D_ESD_USB_D` 只有两个焊盘 (USB_D_P_SRC + GND); `USB_D_N_SRC` 在网表上只出现在串阻行 (R_SER_USB_D_N), 无任何 ESD 器件挂载 ⇒ **D− 完全裸奔**。★这条是 ISS-190 §7-7 已登记过的旧发现, 本轮把它补上了**可引用的官方依据 + 可量化的代价**: ① TI `SLVAF82B` §3.2/§4 原文用 `ESD321` (双通道) **同时护 D+ 与 D−**, 并写明「the diodes are connected to each data line」; ② Würth Elektronik 应用文档 `ANP002`《The protection of USB 2.0 applications》§7 Figure 9 (双差分线都走 TVS) 与 Figure 11 (单通道器件的用法是 **D+ / D− 各一颗**, 连接方式 D+ / D− → GND) ⇒ **单通道器件的业界通行做法也是两条线各一颗, 不是「一条线就够了」**; ③ Semtech 官方技术文章《ESD Protection of USB 2.0 Interfaces》同口径 (`RClamp0582B` 双通道护 D+/D−)。★TI 还给了 USB 2.0 的**结电容判据**: 「An ESD diode with a capacitance **less than 4 pF** is recommended」 (USB 2.0 ≤480 Mbps) ⇒ 双通道 `TPD2E2U06` 官方 CL = 1.5 pF typ / 1.9 pF max (落盘 `state/.cache_iss244/led/tpd2e2u06.pdf`, Rev. C) ⇒ **1.9 pF max 仍在 4 pF 判据内** ⇒ **双边保护的代价不在结电容, 在焊盘数 (+1) 与面积**。"
    },
    {
      "id": "G-5",
      "evidence_level": "[官网]",
      "source": "① Kingbright 官方 `AA1608SURSK` 数据手册 (落盘 `state/.cache_iss244/led/AA1608SURSK_kingbright.pdf`, Ver.3A, 4 页) 第 3 页 4 格图第 2 格 「Luminous Intensity vs. Forward Current」(Y 轴刻度 0.0~2.5, X 轴刻度 0~50 mA), 第 1 页 SELECTION GUIDE Iv 40 min / 160 typ mcd @20 mA; ② Kingbright 官方 `APT1608SURCK` 数据手册 (落盘 `state/.cache_iss244/led/APT1608SURCK_kingbright.pdf`, Ver.22A, 4 页) 同款图 + Iv 40/80 mcd @20 mA; ③ Kingbright 官方 `APH1608SURCK` (落盘 `state/.cache_iss244/led/led_aph1608surck.pdf`, Ver.13A) + `APH1608SGC` (`led_aph1608sgc.pdf`) + `AP2012CGCK` (`led_ap2012cgck.pdf`) 三份交叉印证; ④ `KP-2012SGC` 数据手册 (落盘 `state/.cache_iss244/led/KP-2012SGC_farnell.pdf`, DSAB1341 V.18B) 第 2 页 SELECTION GUIDE Iv 5 min / 12 typ mcd @20 mA + VF 2.2/2.5 V @20 mA ⇒ ★**该版本的曲线是位图 (非文本层) ⇒ 本脚本按文本层标定抓不到 ⇒ 绿灯的 1 mA 档用同厂同尺寸绿 `AP2012CGCK` 的曲线做代理 ⇒ 该档标 [推算] 并写明代理件**; ⑤ 数字化脚本 `state/.cache_iss244/led/extract_ivif.py` + 逐件 JSON 结果 `state/.cache_iss244/led/ivif_*.json` (含坐标轴刻度/自证/采样点); ⑥ 网表 `HW/netlist_v1.csv` L300/L301/L303/L304 (R_LED_R / R_LED_G = 1 kΩ ±1%, 3.3 V 驱动)。",
      "fallback": "降级 ① (**不改网表, 只改亮度预期**): 接受 LED 就是这么暗 (≈ 5% 标称) ⇒ 代价 = 指示灯在白天/强光下基本看不见 ⇒ 需要 PM 给「指示灯可接受亮度」口径 (结构侧给眼旁辐亮度上限) ⇒ ★这是**本单建议的默认路线**, 因为改 R = 改网表 (归落表批次)。降级 ② (改串阻, 保 20 mA 档): 红 Vf 1.95 V ⇒ R = (3.3 − 1.95)/20 mA ≈ **68 Ω** (取 E96 68 Ω); 绿 Vf 2.2 V ⇒ R ≈ **55 Ω** ⇒ 代价 = ① 改网表 (落表批次) + ② 功耗从 ~2.2 mW 升到 ~66 mW (两颗合计约 0.13 W ⇒ 进关机/待机电池账, 参照 ISS-172 的 108 µA 关机账) + ③ **亮度直接进光生物安全评估** (从 ~11 mcd 升到 ~160 mcd, 眼旁光源强度提升 14 倍) ⇒ 需结构侧重算 IEC 62471 分级。降级 ③ (改驱动方式, 不改 R): 用 SoC GPIO 恒流/PWM 驱动 ⇒ 代价 = 硬件要加恒流或改成 PWM + 电阻, 且 1 kΩ 上拉的亮度可调 ⇒ 但 **PWM 占空比与 60 fps 帧预算耦合**, 属 SW 侧改动 ⇒ 本单不碰。★**改 R 阻值 = 改网表 ⇒ 归落表批次, 本单只出建议值 + 代价, 一字未改网表**; ★**亮度档本身需老板/PM 拍 (不代拍)**。",
      "remaining": "① 拍板: 亮度档走降级 ① (接受暗) 还是 ② (改 R 到 20 mA 档) 还是 ③ (PWM); ② 若走 ②, 落表批次改 R 阻值 + 结构侧重算 IEC 62471; ③ KP-2012SGC 自身曲线若要精确值, 落表批次用厂商图纸 (非本机 PDF) 复核。",
      "status": "需老板拍 (亮度档) + 需落表 (若选改 R)",
      "gap": "LED 亮度账不匹配: 1 kΩ 串阻 + 3.3 V ⇒ 实际 ~1.1~1.35 mA, 而候选全是 20 mA 标称",
      "scope": "PM / 结构 (亮度档) + 落表批次 (改 R) · sw-lead 只出依据 + 代价",
      "self_check_result": "★**本轮把 [0数据] 升成了 [官网] + [推算], 并且把上一轮只活在会话内存里的数变成了盘上可复核的证据**。① 电流账 (网表 L301/L304 实读): `R_LED_G` / `R_LED_R` = **1 kΩ ±1%**, 驱动 3.3 V ⇒ I = (3.3 − Vf)/1 kΩ。按 ISS-241 已核的厂商 Vf: 红 `AA1608SURSK` VF typ 1.95 V ⇒ I ≈ **1.35 mA**; 绿 `KP-2012SGC` VF typ 2.2 V ⇒ I ≈ **1.10 mA**; Vf 取 max 2.5 V 时 I 只剩 **0.80 mA** ⇒ 实际工作点区间 **0.80 ~ 1.35 mA** (比 ISS-241 写的 1.1~1.3 mA 更宽)。② 亮度档 (本轮新查 + 数字化): **Kingbright 厂商 PDF 里每一份数据手册都画了「Luminous Intensity vs. Forward Current」归一化曲线** (纵轴 = 以 20 mA 归一化, 横轴 = If)。本轮落盘 4 份原厂 PDF 并写了数字化脚本 `state/.cache_iss244/led/extract_ivif.py`, 从 PDF **文本层**取坐标轴刻度做标定 (不是人眼量), 再用 RANSAC 拟合迹线提取曲线, 脚本自带 3 条自证 (过原点 / 20 mA 点 ≈ 1.00 / 单调)。★**四颗料各跑一遍, 数字互相印证** (1 mA 工作点占 20 mA 标称亮度的比例): `AA1608SURSK` (D_LED_R) = **5.10%** · `APT1608SURCK` (D_CHG_LED) = **5.10%** · `APH1608SURCK` = **4.77%** · `APH1608SGC` (0603 绿) = **5.24%** · `AP2012CGCK` (0805 绿) = **7.19%**。★**结论 (可复核)**: 1 mA 工作点的 LED 亮度只有 20 mA 标称值的 **约 4.8% ~ 7.2%**, 也就是 **暗 14 ~ 21 倍**。③ 折成绝对值: `D_LED_R` (AA1608SURSK, Iv 40 min / 160 typ mcd @20 mA) ⇒ 1.35 mA 时 ≈ **11 mcd typ** (最坏档 40 mcd ⇒ ≈2.8 mcd); `D_LED_G` (KP-2012SGC, GaP 绿, Iv 5 min / 12 typ mcd @20 mA) ⇒ 1.10 mA 时 ≈ **0.7~0.9 mcd typ**; `D_CHG_LED` (APT1608SURCK, Iv 40/80 mcd @20 mA) ⇒ 1.35 mA 时 ≈ **5.5 mcd typ**。④ 归一化曲线在厂商图上只画到 If≈30 mA ⇒ 超出部分本单**不外推**。★**这颗 LED 不是显示白场** (显示件是 0.49\" SiOLED / demo 是 Waveshare 2.8\" LCD) ⇒ 光生物安全的「白场辐亮度」判定不直接落在它身上; 但它是**眼旁指示光源**, 仍需按 IEC 62471 单列评估 ⇒ 登记为需老板拍的一项。"
    },
    {
      "id": "G-6",
      "evidence_level": "[官网]",
      "source": "TI `BQ25896` 数据手册 SLUSC76C pin22 (ISS-241 §5 已下载本地实读, 本单只引用) + `HW/BOM_v1.csv` `C_REGN` 行 value='[待选型] 1µF' + ISS-241 交卷单 L1。",
      "fallback": "① 落表批次同批改 BOM value = 4.7 µF / 10 V / X7R (1 行改动, 与 OPN 回填同批走) ⇒ **这是唯一安全路线**;② 若充电板面积不允许 0805 ⇒ 0402 4.7 µF ⇒ 代价 = DC bias 降容比 0805 狠, 吃掉手册余量 (该型号官方页本轮 [0数据], 落表批次补);③ 若坚持 1 µF ⇒ 必须登记「偏离 TI 手册」并由 main/PM 签字 ⇒ 本单不代签。",
      "remaining": "落表批次改 BOM value 一行 (ISS-243)。",
      "status": "已闭合 (2026-11-16 15:45 实测已被并发落表批次落掉) · 已转单 (ISS-243 L1)",
      "gap": "C_REGN 的 BOM value (1 µF) 与 TI BQ25896 手册 (4.7 µF / 10 V) 冲突",
      "scope": "main (落表批次)",
      "self_check_result": "TI BQ25896 数据手册 (SLUSC76C) pin22 REGN 原文: 「Internally, REGN is connected to the cathode of the boost-strap diode. **Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND.** The capacitor should be placed close to the IC. REGN also serves as bias rail of TS pin.」⇒ BOM value 必须从 1 µF 改成 4.7 µF / 10 V / X7R。★本轮已按 ISS-241 的交接条件 L1 并进 **ISS-243 (落表)**, 本单不重复论证, 只登记出处与当前状态。★★**2026-11-16 15:45:45 实测: 已被并发落表批次落掉** —— `HW/BOM_v1.csv` 的 `C_REGN` 行 value 已变成「4.7µF ±10% (10V)」、opn 已填「GRM21BR71C475KA73L (Murata 0805 / 4.7µF / 16V / X7R / ±10%)」⇒ ★**本条当场闭合** ⇒ 该件不再进落表批次 (清单里保留该行 + 落表证据)。"
    },
    {
      "id": "G-7",
      "evidence_level": "[实测]",
      "source": "ISS-241 §4 缺口 G-7 + §5 S21 (板文件逐焊盘实读) + `HW/PART_SELECTION_MATRIX_2026-11-16.md` §3 每件的「封装兼容性结论」栏。",
      "fallback": "选 land 间距与占位接近的器件 ⇒ 本轮在售件普遍偏小 ⇒ 此路对 ESD/按键基本不通 ⇒ 实际必须重画 land (板那一趟)。",
      "remaining": "板那一趟的 land 重画清单 (含 G-1/G-2 的 pad↔pin 映射)。",
      "status": "已转单 (hw-lead 板那一趟) · 与 G-1/G-2 同批",
      "gap": "占位 land 与在售器件的厂商 land 普遍不重合 (22 件里绝大多数都要重画 land)",
      "scope": "hw-lead (板那一趟)",
      "self_check_result": "4 件 ESD (占位 2.30 mm 间距) vs SOD-323 1.3 mm / X1SON 0.65 mm; 3 件 MOS (占位 1.27~1.53 mm) vs SOT-23 0.95 mm; 5 件按键 (占位 2.20 mm) vs gullwing 外扩 4.6 mm ⇒ **这不是选型的错, 是占位脚手架的性质** ⇒ 本单 22 件里绝大多数都要在板那一趟重画 land。★本轮新增一条跨缺口结论: G-7 与 G-1/G-2 **必须合并成同一次 land 重画**, 否则要重画两遍 (G-1 裁决会改 pad↔pin 映射)。"
    },
    {
      "id": "G-8",
      "evidence_level": "[实测]",
      "source": "`HW/BOM_v1.csv` 六行的 footprint 栏 + 板文件逐位号实查 (ISS-241 §5 S21) + ISS-241 交卷单 L4。",
      "fallback": "落 N 焊盘 + 充电板侧封装另行定 ⇒ 代价 = 这六件的 OPN 回填与 land 要在充电板那一趟一起做, 不能在主板那一趟提前定死。",
      "remaining": "充电板那一趟定六件的封装与 land。",
      "status": "已转单 (ISS-243 L4) · 已闭合",
      "gap": "6 件充电板器件的封装占位是「待定」⇒ 无法给几何兼容结论",
      "scope": "main (充电板那一趟)",
      "self_check_result": "`D_ESD_TC` / `FB_VBUS` / `D_TVS_VBUS` / `Q_CHG_LED` / `D_CHG_LED` / `C_REGN` 六件的 BOM footprint 栏是「待定」, 且板文件里查无此位号 ⇒ 本单对这些件只能给「落 N 焊盘 + 充电板侧封装另行定」。★已并进 **ISS-243 的落表前置条件 L4**, 本单不重复论证。"
    },
    {
      "id": "G-9",
      "evidence_level": "[实测]",
      "source": "`HW/BOM_v1.csv` 实跑 (本单 §6 复现命令 ①, 输出原样贴在交卷单 B5) + `HW/check_part_selection_matrix.py` 的 `expected_refs` 逻辑 + main 2026-11-16 14:3x 亲核记录。",
      "fallback": "若落表批次再改 BOM 的「待选型/必装」口径 ⇒ 本单门禁 `HW/check_part_selection_gaps.py` 的 C5 会**按设计变红** (要么有登记范围内的一件不见了, 要么多出越界件, 要么已被并发落掉的一件没写落表证据) ⇒ 走 H-1 重锚流程 (改本单生成器 + 留痕) 而不是把红灯调没。",
      "remaining": "无 (口径已定死 = 登记范围 22 件 / 当前待落 21 件, 两个数都注明了来源与时点)。",
      "status": "已闭合",
      "gap": "任务书 / BOM / main 三处「件数」口径互不一致",
      "scope": "main (确认口径)",
      "self_check_result": "★本轮**自己跑 csv 复核** (不抄任何硬编码数字): 两个机器派生源 —— ① **登记范围** = ISS-241 矩阵基准块的 `expected_refs` = **22 件** (本单必须全覆盖); ② **当前仍待落** = `HW/BOM_v1.csv` 实跑「待选型∩必装 − 越界件」= **21 件**。两者差的那一件是 `C_REGN` —— ★**2026-11-16 15:45:45 实测: 它被另一个落表批次落掉了** (BOM value 从「[待选型] 1µF」改成「4.7µF ±10% (10V)」+ opn 已填) ⇒ **登记范围仍是 22 (登记事实不变), 当前待落是 21 (盘上事实变了)** ⇒ 两个数都要写在清单里并注明来源。任务书按类别枚举 = 20 个位号、抬头说 21 件 ⇒ 口径差不改, 本单按**超集 22 行**全覆盖。★ISS-241 的门禁 `HW/check_part_selection_matrix.py` 用的是矩阵基准块里的 `expected_refs` 快照 (22) ⇒ 它仍然 22/22 全绿, 本单没有把它改红。★**本单门禁的 C5 写成双源判定** (登记范围 + 当前待落), 并要求「已被并发落掉的一件必须写 landed_note 落表证据」⇒ **锚点过期 = 红 ⇒ 走 H-1 重锚 + 留痕**, 而不是把红灯调没 (ISS-225 纪律)。"
    },
    {
      "id": "G-10",
      "evidence_level": "[官网]",
      "source": "① TI `TPS3808` 数据手册 SBVS050N Rev. N (落盘 `state/.cache_iss244/ref/tps3808.pdf`) §7.3.1 + Figure 7-1 + Ordering Information 表 (TPS3808G01 Adjustable 0.405 V) + 特性表 (阈值精度/迟滞); ② 网表 `HW/netlist_v1.csv` L84/L86 (U_DCDC_VIO dnp=DNP, 轨电压 [待原厂]) + L404/L405/L406 (R_SUPV_DIV1/2 = 0 Ω 跳线位, tbd=TBD-02) + L407~L409 (U_SUPV dnp=DNP); ③ 计算脚本 `state/.cache_iss244/supv_divider_solve.py` (可复跑, 输出原样贴在交卷单 B5)。",
      "fallback": "降级 ① (**推荐**): `R_SUPV_DIV1` / `R_SUPV_DIV2` 随 `U_SUPV` 一并置 **DNP** ⇒ 零新增器件、零板改动、顺带解掉 ISS-190 判的「装 0 Ω 就短路」装配级灾难 ⇒ 代价 = 主板侧放弃独立欠压监督 (依赖 SoM 内部 PMIC 的上电复位)。降级 ②: 决定恢复监督器 ⇒ 按上表取 E96 值 + 触发点随轨标称重算 + 补 1 nF SENSE 滤波电容 ⇒ 代价 = ① 要新增 U_SUPV 的器件行 (现在 DNP) + ② 轨标称必须先定 (TBD-02) + ③ 误差带 (上表) 要并进欠压策略。降级 ③: 监督器换成**可编程/带窗口**的器件 (不加分压) ⇒ 代价 = 封装与板位要重新核, 本轮未查 ⇒ [0数据], 落表批次补。★**本单只出依据 + 代价, 不代拍「要不要恢复监督器」。**",
      "remaining": "① 拍板: 主板侧要不要独立欠压监督 (降级 ① / ② / ③); ② 若走 ②, TBD-02 轨标称要定 (3.3 / 1.8 / 1.2 V 三选一)。",
      "status": "需老板拍 + 需落表",
      "gap": "R_SUPV_DIV1/2 的最终阻值 (原厂电压窗口未到 ⇒ 只给得出 0 Ω 跳线件的 OPN)",
      "scope": "main / PM (落表批次 + 老板拍是否恢复监督器)",
      "self_check_result": "★**本轮把公式和候选表做出来了, 结论是「真正阻塞的不是阻值算不出, 而是监控器本体不装」**。① 官方公式 (TI `TPS3808G01`, 数据手册 SBVS050N Rev. N, 2026-08, 36 页, 落盘 `state/.cache_iss244/ref/tps3808.pdf`): §7.3.1 + Figure 7-1 明写 **V_IT = (1 + R1/R2) × 0.405 V** (R1 = 上臂 被监控轨→SENSE, R2 = 下臂 SENSE→GND), 功能框图注 **R1 + R2 = 4 MΩ**, TPS3808G01 = Adjustable 版 / V_IT 标称 0.405 V / 阈值精度 VIT ≤3.3 V 时 typ ±1.5% / −1.5% ±0.5% / 迟滞 1.5% / SENSE 脚建议 1 nF~10 nF 滤波电容。② 被监控轨 `RAIL_V_SOC_IO` 的电压在网表 L84 原文是「**[待原厂] (3.3V / 1.8V / 1.2V)**」(TBD-02 未闭合) ⇒ 三档候选。③ 候选表 (触发点取轨标称 ×0.90 = 轨电压跌 10 % 报欠压; 电阻 1 %; 算式见 `state/.cache_iss244/supv_divider_solve.py`, 可复跑): 轨 3.3 V ⇒ V_IT 2.970 V ⇒ R1/R2 = 3.480 M / 549 k (E96) ⇒ 实际触发 2.9722 V, 误差带 2.8108~3.1378 V; 轨 1.8 V ⇒ V_IT 1.620 V ⇒ R1/R2 = 3.010 M / 1.000 M ⇒ 实际触发 1.6240 V, 误差带 1.5359~1.7145 V; 轨 1.2 V ⇒ V_IT 1.080 V ⇒ R1/R2 = 2.490 M / 1.500 M ⇒ 实际触发 1.0773 V, 误差带 1.0188~1.1373 V。④ ★**真正的阻塞**: `U_SUPV` 三行 dnp=**DNP** (网表 L407~L409, note 写明「SoM 内部 PMIC 已做上电复位 ⇒ 主板不装监督器」), 而产生 `RAIL_V_SOC_IO` 的 `U_DCDC_VIO` 也 dnp=**DNP** (网表 L84/L86) ⇒ **监督器本体不装 ⇒ 分压两臂装上只会把 RAIL_V_SOC_IO 短路到地** (ISS-190 已判过同一件事) ⇒ 分压阻值这件事本身没有可落的对象。"
    }
  ],
  "opn_rows": [
    {
      "ref": "C_REGN",
      "model": "GRM21BR71C475KA73L",
      "evidence_level": "[官网]",
      "board": "CHG_BOARD",
      "package_verdict": "落2焊盘+充电板侧封装另行定",
      "land_anchor": "网表 L44,L45 (ref=C_REGN, nets=REGN+GND) · 脚表 C_REGN.1,C_REGN.2 · BOM L43 (ref=C_REGN)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L43 行的 value='4.7µF ±10% (10V)' / opn='GRM21BR71C475KA73L (Murata 0805 / 4.7µF / 16V / X7R / ±10%)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "D_CHG_LED",
      "model": "APT1608SURCK",
      "evidence_level": "[官网]",
      "board": "CHG_BOARD",
      "package_verdict": "落2焊盘+充电板侧封装另行定",
      "land_anchor": "网表 L510,L511 (ref=D_CHG_LED, nets=LED_CHG_A+CHG_LED_K) · 脚表 D_CHG_LED.1,D_CHG_LED.2 · BOM L57 (ref=D_CHG_LED)",
      "need_land": "充电板侧封装占位待定 ⇒ 板那一趟定 (ISS-243 L4)",
      "decision_owner": "main (充电板那一趟)",
      "status": "已转单 (ISS-243 L4) · 需落表",
      "landed_note": ""
    },
    {
      "ref": "D_ESD_CAM",
      "model": "TPD1E05U06DPYR",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L163,L413,L414 (ref=D_ESD_CAM, nets=GND+CSI_D0_CK_P+GND) · 脚表 D_ESD_CAM.1,D_ESD_CAM.2 · BOM L58 (ref=D_ESD_CAM)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L58 行的 value='TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)' / opn='TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "D_ESD_DEMO",
      "model": "PESD5V0S1BA",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L420,L421 (ref=D_ESD_DEMO, nets=RAIL_DEMO_5V+GND) · 脚表 D_ESD_DEMO.1,D_ESD_DEMO.2 · BOM L59 (ref=D_ESD_DEMO)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L59 行的 value='PESD5V0S1BA (Nexperia 单通道双向 ESD · SOD-323 · VRWM 5V · IRM 5nA)' / opn='PESD5V0S1BA (Nexperia SOD-323 2-lead · VRWM 5V · VBR 6V min · IEC 61000-4-2 >30kV)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "D_ESD_TC",
      "model": "PESD5V0S1BA",
      "evidence_level": "[官网]",
      "board": "CHG_BOARD",
      "package_verdict": "落2焊盘+充电板侧封装另行定",
      "land_anchor": "网表 L4,L162 (ref=D_ESD_TC, nets=USB_VBUS_RAW+GND) · 脚表 D_ESD_TC.1,D_ESD_TC.2,D_ESD_TC.3,D_ESD_TC.4 · BOM L61 (ref=D_ESD_TC)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L61 行的 value='SP0503BAHT (Littelfuse 3 通道 TVS/ESD 阵列 · 5.5V standoff · SOT-143 4 脚)' / opn='SP0503BAHT (Littelfuse · 订购码 SP0503BAHTG · 3 通道 TVS 阵列 · SOT-143-4 · 5.5VWM/8.5VC)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "D_ESD_USB_D",
      "model": "TPD1E05U06DPYR",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L417,L418 (ref=D_ESD_USB_D, nets=USB_D_P_SRC+GND) · 脚表 D_ESD_USB_D.1,D_ESD_USB_D.2 · BOM L62 (ref=D_ESD_USB_D)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L62 行的 value='TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)' / opn='TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "D_LED_G",
      "model": "KP-2012SGC",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "兼容",
      "land_anchor": "网表 L305 (ref=D_LED_G, nets=GND) · 脚表 D_LED_G.1,D_LED_G.2 · BOM L64 (ref=D_LED_G)",
      "need_land": "否 — 0805 本体 2.0×1.25 mm 与占位 fab bbox 2.70×1.60 mm 对齐 ⇒ land 不用动",
      "decision_owner": "PM / 结构 (亮度档) + 落表批次",
      "status": "需老板拍 (亮度档 G-5) · 需落表",
      "landed_note": ""
    },
    {
      "ref": "D_LED_R",
      "model": "AA1608SURSK",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "兼容",
      "land_anchor": "网表 L302 (ref=D_LED_R, nets=GND) · 脚表 D_LED_R.1,D_LED_R.2 · BOM L65 (ref=D_LED_R)",
      "need_land": "否 — 0603 本体 1.6×0.8 mm 在同 bbox 内偏小, 落板后位置略靠内",
      "decision_owner": "PM / 结构 (亮度档) + 落表批次",
      "status": "需老板拍 (亮度档 G-5) · 需落表",
      "landed_note": ""
    },
    {
      "ref": "D_TVS_VBUS",
      "model": "SMBJ5.0A",
      "evidence_level": "[官网]",
      "board": "CHG_BOARD",
      "package_verdict": "落2焊盘+充电板侧封装另行定",
      "land_anchor": "网表 L505,L506 (ref=D_TVS_VBUS, nets=VBUS_5V+GND) · 脚表 D_TVS_VBUS.1,D_TVS_VBUS.2 · BOM L66 (ref=D_TVS_VBUS)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L66 行的 value='SMBJ5.0A (Littelfuse 单向 TVS · SMB · VRWM 5.0V · Vc 9.2V@65.3A · 600W)' / opn='SMBJ5.0A (Littelfuse DO-214AA SMB · VRWM 5.0V · VBR 6.4V min · Vc 9.2V @ Ipp 65.3A)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "FB_DEMO",
      "model": "BLM21PG221SN1D",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "兼容",
      "land_anchor": "网表 L422,L423 (ref=FB_DEMO, nets=RAIL_DEMO_5V+GND) · 脚表 FB_DEMO.1,FB_DEMO.2 · BOM L67 (ref=FB_DEMO)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L67 行的 value='BLM21PG221SN1D (Murata 0805 · 220Ω@100MHz · 2A · DCR 45mΩ max)' / opn='BLM21PG221SN1D (Murata BLM21PG 0805 2012 metric · 220Ω ±25%@100MHz · 2000mA · DCR 45mΩ max)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "FB_VBUS",
      "model": "BLM31PG121SN1",
      "evidence_level": "[官网]",
      "board": "CHG_BOARD",
      "package_verdict": "落2焊盘+充电板侧封装另行定",
      "land_anchor": "网表 L5,L8 (ref=FB_VBUS, nets=VBUS_5V_ESD+VBUS_5V_F1) · 脚表 FB_VBUS.1,FB_VBUS.2 · BOM L68 (ref=FB_VBUS)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L68 行的 value='BLM31PG121SN1 (Murata 1206 · 120Ω@100MHz · 3A · DCR 25mΩ)' / opn='BLM31PG121SN1 (Murata BLM31PG 1206 3216 metric · 120Ω@100MHz · 3000mA · DCR 0.025Ω)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "Q_AND",
      "model": "AO3400A",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L65,L66,L67 (ref=Q_AND, nets=RESET_N+GND+PG_AND) · 脚表 Q_AND.1,Q_AND.2,Q_AND.3 · BOM L82 (ref=Q_AND)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L82 行的 value='AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)' / opn='AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "Q_CHG_LED",
      "model": "2N7002",
      "evidence_level": "[官网]",
      "board": "CHG_BOARD",
      "package_verdict": "落3焊盘+充电板侧封装另行定",
      "land_anchor": "网表 L512,L513,L514 (ref=Q_CHG_LED, nets=CHG_LED_K+GND+CHG_STAT) · 脚表 Q_CHG_LED.1,Q_CHG_LED.2,Q_CHG_LED.3 · BOM L83 (ref=Q_CHG_LED)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L83 行的 value='2N7002 (onsemi N-MOS SOT-23 · VGS(th) max 2.0V · IGSS ≤10nA)' / opn='2N7002 (onsemi SOT-23 3-pin · 60V · RDS(on) 1.2Ω typ@10V · ID 115mA · IGSS ≤10nA)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "Q_ENVC",
      "model": "AO3400A",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L71,L72,L73 (ref=Q_ENVC, nets=PG_AND+GND+EN_VCORE) · 脚表 Q_ENVC.1,Q_ENVC.2,Q_ENVC.3 · BOM L84 (ref=Q_ENVC)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L84 行的 value='AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)' / opn='AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "Q_PG",
      "model": "DMP3098L",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L59,L60,L61 (ref=Q_PG, nets=PWR_ON+BAT_SW+PWR_GOOD) · 脚表 Q_PG.1,Q_PG.2,Q_PG.3 · BOM L85 (ref=Q_PG)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L85 行的 value='DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)' / opn='DMP3098L (Diodes Inc SOT23 3-pin · −30V · RDS(on) 98mΩ typ@-4.5V · IDSS ≤800nA)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "R_SUPV_DIV1",
      "model": "RC0603JR-070RL",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "兼容",
      "land_anchor": "网表 L404 (ref=R_SUPV_DIV1, nets=V_SOC_IO) · 脚表 R_SUPV_DIV1.1,R_SUPV_DIV1.2 · BOM L147 (ref=R_SUPV_DIV1)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L147 行的 value='0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板' / opn='RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "R_SUPV_DIV2",
      "model": "RC0603JR-070RL",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "兼容",
      "land_anchor": "网表 L405,L406 (ref=R_SUPV_DIV2, nets=SUPV_SENSE+GND) · 脚表 R_SUPV_DIV2.1,R_SUPV_DIV2.2 · BOM L148 (ref=R_SUPV_DIV2)",
      "need_land": "不适用 (已落表)",
      "decision_owner": "无需再拍 (已落表)",
      "status": "★已落表 (并发落表批次; 本轮 2026-11-17 05:0x 实读 BOM 已改) · 本单无需再落",
      "landed_note": "登记范围内但当前已不在 BOM 待选型集合 ⇒ 已被别的落表批次落掉: BOM L148 行的 value='0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板' / opn='RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C)' (本单实读, 2026-11-17 05:0x 的盘上状态) ⇒ 该件的 OPN 回填已完成, 不进落表批次"
    },
    {
      "ref": "SW_BOOT",
      "model": "KMR231ULCLFS",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L386,L387 (ref=SW_BOOT, nets=BOOT_N+GND) · 脚表 SW_BOOT.1,SW_BOOT.2 · BOM L153 (ref=SW_BOOT)",
      "need_land": "是 — 占位 2.20 mm vs gullwing 外扩 4.6 mm ⇒ 必重画",
      "decision_owner": "落表批次 (main 排期)",
      "status": "需落表",
      "landed_note": ""
    },
    {
      "ref": "SW_KEY_PWR",
      "model": "KMR231ULCLFS",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L310,L312 (ref=SW_KEY_PWR, nets=KEY_PWR+GND) · 脚表 SW_KEY_PWR.1,SW_KEY_PWR.2 · BOM L155 (ref=SW_KEY_PWR)",
      "need_land": "是 — 同上",
      "decision_owner": "落表批次 (main 排期)",
      "status": "需落表",
      "landed_note": ""
    },
    {
      "ref": "SW_KEY_VM",
      "model": "B3U-1000P",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L320,L322 (ref=SW_KEY_VM, nets=KEY_VOL_M+GND) · 脚表 SW_KEY_VM.1,SW_KEY_VM.2 · BOM L156 (ref=SW_KEY_VM)",
      "need_land": "是 — 同上",
      "decision_owner": "落表批次 (main 排期)",
      "status": "需落表",
      "landed_note": ""
    },
    {
      "ref": "SW_KEY_VP",
      "model": "B3U-1000P",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L315,L317 (ref=SW_KEY_VP, nets=KEY_VOL_P+GND) · 脚表 SW_KEY_VP.1,SW_KEY_VP.2 · BOM L157 (ref=SW_KEY_VP)",
      "need_land": "是 — 同上",
      "decision_owner": "落表批次 (main 排期)",
      "status": "需落表",
      "landed_note": ""
    },
    {
      "ref": "SW_RST",
      "model": "KMR231ULCLFS",
      "evidence_level": "[官网]",
      "board": "MAIN_PCB",
      "package_verdict": "条件兼容",
      "land_anchor": "网表 L382,L383 (ref=SW_RST, nets=RESET_N+GND) · 脚表 SW_RST.1,SW_RST.2 · BOM L158 (ref=SW_RST)",
      "need_land": "是 — 同上",
      "decision_owner": "落表批次 (main 排期)",
      "status": "需落表",
      "landed_note": ""
    }
  ],
  "post_landing": {
    "pending_refs": [
      "D_CHG_LED",
      "D_LED_G",
      "D_LED_R",
      "SW_BOOT",
      "SW_KEY_PWR",
      "SW_KEY_VM",
      "SW_KEY_VP",
      "SW_RST"
    ],
    "landed_refs": [
      "C_REGN",
      "D_ESD_CAM",
      "D_ESD_DEMO",
      "D_ESD_TC",
      "D_ESD_USB_D",
      "D_TVS_VBUS",
      "FB_DEMO",
      "FB_VBUS",
      "Q_AND",
      "Q_CHG_LED",
      "Q_ENVC",
      "Q_PG",
      "R_SUPV_DIV1",
      "R_SUPV_DIV2"
    ],
    "rows": [
      {
        "ref": "C_REGN",
        "model": "4.7µF ±10%",
        "opn": "GRM21BR71C475KA73L",
        "bom_value": "4.7µF ±10% (10V)",
        "bom_opn": "GRM21BR71C475KA73L (Murata 0805 / 4.7µF / 16V / X7R / ±10%)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            43,
            "REGN"
          ],
          [
            44,
            "GND"
          ]
        ],
        "on_main_board": false,
        "charge_board": true,
        "pad_map": [],
        "device_pin_order": {},
        "device_pkg": "",
        "device_source": "",
        "device_evidence": "- / 编号 -",
        "checks": [],
        "verdict": "– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判",
        "fix": "",
        "topology_note": "不在主板 (充电板件, 板文件查无此位号) ⇒ 无几何可判; BOM 已按 TI BQ25896 pin22 手册落成 4.7 µF / 10 V ⇒ **G-6 闭合**。",
        "source": "板文件 + BOM 实读",
        "p0": ""
      },
      {
        "ref": "D_ESD_CAM",
        "model": "TPD1E05U06DPYR",
        "opn": "TPD1E05U06DPYR",
        "bom_value": "TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)",
        "bom_opn": "TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            162,
            "GND"
          ],
          [
            412,
            "CSI_D0_CK_P"
          ],
          [
            413,
            "GND"
          ]
        ],
        "on_main_board": true,
        "charge_board": false,
        "pad_map": [
          {
            "pad": "1",
            "net": "GND",
            "at": "-0.45 -0.2"
          },
          {
            "pad": "2",
            "net": "CSI_D0_CK_P",
            "at": "1.85 -0.2"
          }
        ],
        "device_pin_order": {
          "1": "I/O",
          "2": "GND"
        },
        "device_pkg": "DPY (X1SON, 2 pin)",
        "device_source": "TI `TPD4E05U06` 数据手册 SLVSBO7O (2024-08 改版) Table 4-1「Pin Functions TPD1E05U06 DPY and DYA」: GND = pin 2 / I/O = pin 1 (本轮实读, 落盘 `state/.cache_iss244/led/tpd4e05u06.pdf`)",
        "device_evidence": "[官网] / 编号 [官网]",
        "checks": [
          {
            "pad": "1",
            "net": "GND",
            "at": "-0.45 -0.2",
            "device_role": "I/O",
            "netlist_role": "GND",
            "match": false
          },
          {
            "pad": "2",
            "net": "CSI_D0_CK_P",
            "at": "1.85 -0.2",
            "device_role": "GND",
            "netlist_role": "I/O",
            "match": false
          }
        ],
        "verdict": "★P0 (引脚序/角色级): ✘ 占位 land 与器件引脚序对不上",
        "fix": "板侧改 land: pad1: GND → CSI_D0_CK_P; pad2: CSI_D0_CK_P → GND",
        "topology_note": "★**land 与器件引脚序正好相反 (P0)**: 占位 land pad1=GND / pad2=信号, 而器件 pin1=I/O / pin2=GND ⇒ 装上去 = ESD 器件对**正向** ESD 失效 (I/O 脚接地, 到地无通路) + CSI lane 的**负向**摆幅被内部二极管钳到 GND 附近。",
        "source": "TI `TPD4E05U06` 数据手册 SLVSBO7O (2024-08 改版) Table 4-1「Pin Functions TPD1E05U06 DPY and DYA」: GND = pin 2 / I/O = pin 1 (本轮实读, 落盘 `state/.cache_iss244/led/tpd4e05u06.pdf`)",
        "target_pad_nets": {
          "1": "CSI_D0_CK_P",
          "2": "GND"
        },
        "p0": "pin-order"
      },
      {
        "ref": "D_ESD_DEMO",
        "model": "PESD5V0S1BA",
        "opn": "PESD5V0S1BA",
        "bom_value": "PESD5V0S1BA (Nexperia 单通道双向 ESD · SOD-323 · VRWM 5V · IRM 5nA)",
        "bom_opn": "PESD5V0S1BA (Nexperia SOD-323 2-lead · VRWM 5V · VBR 6V min · IEC 61000-4-2 >30kV)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            419,
            "RAIL_DEMO_5V"
          ],
          [
            420,
            "GND"
          ]
        ],
        "on_main_board": true,
        "charge_board": false,
        "pad_map": [
          {
            "pad": "1",
            "net": "RAIL_DEMO_5V",
            "at": "-0.45 -0.2"
          },
          {
            "pad": "2",
            "net": "GND",
            "at": "1.85 -0.2"
          }
        ],
        "device_pin_order": {},
        "device_pkg": "SOD-323 (双向件)",
        "device_source": "Nexperia `PESD5V0S1BA` 双向 ESD (ISS-241 §3 已实读官方手册: 单通道双向) ⇒ 极性无关 ⇒ 不参与引脚序判定",
        "device_evidence": "[官网] / 编号 [官网]",
        "checks": [],
        "verdict": "– 双向件 ⇒ 极性无关, 不参与引脚序判定",
        "fix": "",
        "topology_note": "双向件 ⇒ 极性无关 ✔; 只差 land 几何 (G-7)。",
        "source": "Nexperia `PESD5V0S1BA` 双向 ESD (ISS-241 §3 已实读官方手册: 单通道双向) ⇒ 极性无关 ⇒ 不参与引脚序判定",
        "p0": ""
      },
      {
        "ref": "D_ESD_TC",
        "model": "SP0503BAHT",
        "opn": "SP0503BAHT",
        "bom_value": "SP0503BAHT (Littelfuse 3 通道 TVS/ESD 阵列 · 5.5V standoff · SOT-143 4 脚)",
        "bom_opn": "SP0503BAHT (Littelfuse · 订购码 SP0503BAHTG · 3 通道 TVS 阵列 · SOT-143-4 · 5.5VWM/8.5VC)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            3,
            "USB_VBUS_RAW"
          ],
          [
            161,
            "GND"
          ]
        ],
        "on_main_board": false,
        "charge_board": true,
        "pad_map": [],
        "device_pin_order": {},
        "device_pkg": "",
        "device_source": "",
        "device_evidence": "- / 编号 -",
        "checks": [],
        "verdict": "– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判",
        "fix": "",
        "topology_note": "充电板件 (板文件查无此位号) ⇒ footprint 仍「待定」(G-8); ★落地的是 **3 通道** SP0503BAHT (SOT-143 4 脚), 而网表只接了 1 个通道 (USB_VBUS_RAW) + GND ⇒ **另 2 个通道闲置** ⇒ Type-C 的 D+/D− 仍未被这阵列覆盖。",
        "source": "板文件 + BOM 实读",
        "p0": ""
      },
      {
        "ref": "D_ESD_USB_D",
        "model": "TPD1E05U06DPYR",
        "opn": "TPD1E05U06DPYR",
        "bom_value": "TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)",
        "bom_opn": "TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            416,
            "USB_D_P_SRC"
          ],
          [
            417,
            "GND"
          ]
        ],
        "on_main_board": true,
        "charge_board": false,
        "pad_map": [
          {
            "pad": "1",
            "net": "USB_D_P_SRC",
            "at": "-0.45 -0.2"
          },
          {
            "pad": "2",
            "net": "GND",
            "at": "1.85 -0.2"
          }
        ],
        "device_pin_order": {
          "1": "I/O",
          "2": "GND"
        },
        "device_pkg": "DPY (X1SON, 2 pin)",
        "device_source": "TI `TPD4E05U06` 数据手册 SLVSBO7O (2024-08 改版) Table 4-1「Pin Functions TPD1E05U06 DPY and DYA」: GND = pin 2 / I/O = pin 1 (本轮实读, 落盘 `state/.cache_iss244/led/tpd4e05u06.pdf`)",
        "device_evidence": "[官网] / 编号 [官网]",
        "checks": [
          {
            "pad": "1",
            "net": "USB_D_P_SRC",
            "at": "-0.45 -0.2",
            "device_role": "I/O",
            "netlist_role": "I/O",
            "match": true
          },
          {
            "pad": "2",
            "net": "GND",
            "at": "1.85 -0.2",
            "device_role": "GND",
            "netlist_role": "GND",
            "match": true
          }
        ],
        "verdict": "✔ 引脚序与占位 land 对得上",
        "fix": "",
        "topology_note": "引脚序对得上 ✔; 但仍是**单边** (只护 D+, USB_D_N_SRC 无保护) ⇒ G-4 仍开。",
        "source": "TI `TPD4E05U06` 数据手册 SLVSBO7O (2024-08 改版) Table 4-1「Pin Functions TPD1E05U06 DPY and DYA」: GND = pin 2 / I/O = pin 1 (本轮实读, 落盘 `state/.cache_iss244/led/tpd4e05u06.pdf`)",
        "p0": ""
      },
      {
        "ref": "D_TVS_VBUS",
        "model": "SMBJ5.0A",
        "opn": "SMBJ5.0A",
        "bom_value": "SMBJ5.0A (Littelfuse 单向 TVS · SMB · VRWM 5.0V · Vc 9.2V@65.3A · 600W)",
        "bom_opn": "SMBJ5.0A (Littelfuse DO-214AA SMB · VRWM 5.0V · VBR 6.4V min · Vc 9.2V @ Ipp 65.3A)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            504,
            "VBUS_5V"
          ],
          [
            505,
            "GND"
          ]
        ],
        "on_main_board": false,
        "charge_board": true,
        "pad_map": [],
        "device_pin_order": {},
        "device_pkg": "",
        "device_source": "",
        "device_evidence": "- / 编号 -",
        "checks": [],
        "verdict": "– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判",
        "fix": "",
        "topology_note": "充电板件 (板文件查无此位号) ⇒ 封装/land 归充电板那一趟 (G-8); 引脚序无关。",
        "source": "板文件 + BOM 实读",
        "p0": ""
      },
      {
        "ref": "FB_DEMO",
        "model": "BLM21PG221SN1D",
        "opn": "BLM21PG221SN1D",
        "bom_value": "BLM21PG221SN1D (Murata 0805 · 220Ω@100MHz · 2A · DCR 45mΩ max)",
        "bom_opn": "BLM21PG221SN1D (Murata BLM21PG 0805 2012 metric · 220Ω ±25%@100MHz · 2000mA · DCR 45mΩ max)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            421,
            "RAIL_DEMO_5V"
          ],
          [
            422,
            "GND"
          ]
        ],
        "on_main_board": true,
        "charge_board": false,
        "pad_map": [
          {
            "pad": "1",
            "net": "RAIL_DEMO_5V",
            "at": "-0.4 -0.3"
          },
          {
            "pad": "2",
            "net": "GND",
            "at": "0.4 0.3"
          }
        ],
        "device_pin_order": {},
        "device_pkg": "",
        "device_source": "",
        "device_evidence": "- / 编号 -",
        "checks": [],
        "verdict": "– 无源件 / 不引脚序敏感 ⇒ 只差 land 几何 (G-7)",
        "fix": "",
        "topology_note": "在主板: 占位 2 焊盘 (pad 间距 0.8 mm, 0805 尺��级) vs Murata BLM21PG221SN1D = 0805 ⇒ **land 几何要重画 (G-7)**; 引脚序无关 (无源件)。",
        "source": "板文件 + BOM 实读",
        "p0": ""
      },
      {
        "ref": "FB_VBUS",
        "model": "BLM31PG121SN1",
        "opn": "BLM31PG121SN1",
        "bom_value": "BLM31PG121SN1 (Murata 1206 · 120Ω@100MHz · 3A · DCR 25mΩ)",
        "bom_opn": "BLM31PG121SN1 (Murata BLM31PG 1206 3216 metric · 120Ω@100MHz · 3000mA · DCR 0.025Ω)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            4,
            "VBUS_5V_ESD"
          ],
          [
            7,
            "VBUS_5V_F1"
          ]
        ],
        "on_main_board": false,
        "charge_board": true,
        "pad_map": [],
        "device_pin_order": {},
        "device_pkg": "",
        "device_source": "",
        "device_evidence": "- / 编号 -",
        "checks": [],
        "verdict": "– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判",
        "fix": "",
        "topology_note": "充电板件 (板文件查无此位号) ⇒ 封装/land 归充电板那一趟 (G-8); 引脚序无关。",
        "source": "板文件 + BOM 实读",
        "p0": ""
      },
      {
        "ref": "Q_AND",
        "model": "AO3400A",
        "opn": "AO3400A",
        "bom_value": "AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)",
        "bom_opn": "AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            64,
            "RESET_N"
          ],
          [
            65,
            "GND"
          ],
          [
            66,
            "PG_AND"
          ]
        ],
        "on_main_board": true,
        "charge_board": false,
        "pad_map": [
          {
            "pad": "1",
            "net": "RESET_N",
            "at": "-1.4 -2"
          },
          {
            "pad": "2",
            "net": "GND",
            "at": "-0.13 -2"
          },
          {
            "pad": "3",
            "net": "PG_AND",
            "at": "1.4 2"
          }
        ],
        "device_pin_order": {
          "1": "G",
          "2": "S",
          "3": "D"
        },
        "device_pkg": "SOT-23",
        "device_source": "AOS `AO3400A` 数据手册 (本轮实读, 落盘 `state/.cache_iss244/mos/AO3400A.pdf`) p1 Pin Configuration 图: 排布 = G/S 一侧 + D 另一侧 (图上**未印引脚号**) ⇒ 编号 1=G / 2=S / 3=D 按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ 编号这一层标 [推算]",
        "device_evidence": "[官网] / 编号 [推算]",
        "checks": [
          {
            "pad": "1",
            "net": "RESET_N",
            "at": "-1.4 -2",
            "device_role": "G",
            "netlist_role": "D",
            "match": false
          },
          {
            "pad": "2",
            "net": "GND",
            "at": "-0.13 -2",
            "device_role": "S",
            "netlist_role": "S",
            "match": true
          },
          {
            "pad": "3",
            "net": "PG_AND",
            "at": "1.4 2",
            "device_role": "D",
            "netlist_role": "G",
            "match": false
          }
        ],
        "verdict": "★P0 (引脚序/角色级): ✘ 占位 land 与器件引脚序对不上",
        "fix": "板侧改 land: pad1: RESET_N → PG_AND; pad3: PG_AND → RESET_N",
        "topology_note": "角色本身正确 (D=RESET_N / S=GND / G=PG_AND) ⇒ 差的是占位 land 与器件引脚序的对应关系。",
        "source": "AOS `AO3400A` 数据手册 (本轮实读, 落盘 `state/.cache_iss244/mos/AO3400A.pdf`) p1 Pin Configuration 图: 排布 = G/S 一侧 + D 另一侧 (图上**未印引脚号**) ⇒ 编号 1=G / 2=S / 3=D 按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ 编号这一层标 [推算]",
        "target_pad_nets": {
          "1": "PG_AND",
          "2": "GND",
          "3": "RESET_N"
        },
        "p0": "pin-order"
      },
      {
        "ref": "Q_CHG_LED",
        "model": "2N7002",
        "opn": "2N7002",
        "bom_value": "2N7002 (onsemi N-MOS SOT-23 · VGS(th) max 2.0V · IGSS ≤10nA)",
        "bom_opn": "2N7002 (onsemi SOT-23 3-pin · 60V · RDS(on) 1.2Ω typ@10V · ID 115mA · IGSS ≤10nA)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            511,
            "CHG_LED_K"
          ],
          [
            512,
            "GND"
          ],
          [
            513,
            "CHG_STAT"
          ]
        ],
        "on_main_board": false,
        "charge_board": true,
        "pad_map": [],
        "device_pin_order": {},
        "device_pkg": "",
        "device_source": "",
        "device_evidence": "- / 编号 -",
        "checks": [],
        "verdict": "– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判",
        "fix": "",
        "topology_note": "充电板件 (板文件查无此位号) ⇒ footprint 仍「待定」(G-8); 角色 D=CHG_LED_K / S=GND / G=CHG_STAT ⇒ 充电板 land 须按 **1=G / 2=S / 3=D** 建 (2N7002 的常规序)。",
        "source": "板文件 + BOM 实读",
        "p0": ""
      },
      {
        "ref": "Q_ENVC",
        "model": "AO3400A",
        "opn": "AO3400A",
        "bom_value": "AO3400A (AOS N-MOS SOT-23 · VGS(th) max 1.45V · RDS(on) 32mΩ@4.5V)",
        "bom_opn": "AO3400A (Alpha & Omega SOT-23 3-pin G-S-D · 30V · RDS(on) 26.5mΩ@10V · VGS(th) max 1.45V)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            70,
            "PG_AND"
          ],
          [
            71,
            "GND"
          ],
          [
            72,
            "EN_VCORE"
          ]
        ],
        "on_main_board": true,
        "charge_board": false,
        "pad_map": [
          {
            "pad": "1",
            "net": "PG_AND",
            "at": "-1.4 -2"
          },
          {
            "pad": "2",
            "net": "GND",
            "at": "-0.13 -2"
          },
          {
            "pad": "3",
            "net": "EN_VCORE",
            "at": "1.4 2"
          }
        ],
        "device_pin_order": {
          "1": "G",
          "2": "S",
          "3": "D"
        },
        "device_pkg": "SOT-23",
        "device_source": "AOS `AO3400A` 数据手册 (本轮实读, 落盘 `state/.cache_iss244/mos/AO3400A.pdf`) p1 Pin Configuration 图: 排布 = G/S 一侧 + D 另一侧 (图上**未印引脚号**) ⇒ 编号 1=G / 2=S / 3=D 按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ 编号这一层标 [推算]",
        "device_evidence": "[官网] / 编号 [推算]",
        "checks": [
          {
            "pad": "1",
            "net": "PG_AND",
            "at": "-1.4 -2",
            "device_role": "G",
            "netlist_role": "G",
            "match": true
          },
          {
            "pad": "2",
            "net": "GND",
            "at": "-0.13 -2",
            "device_role": "S",
            "netlist_role": "S",
            "match": true
          },
          {
            "pad": "3",
            "net": "EN_VCORE",
            "at": "1.4 2",
            "device_role": "D",
            "netlist_role": "D",
            "match": true
          }
        ],
        "verdict": "✔ 引脚序与占位 land 对得上",
        "fix": "",
        "topology_note": "角色与占位 land 都已与器件引脚序对上 ✔ (三颗 MOS 里唯一不用动 land 的一颗)。",
        "source": "AOS `AO3400A` 数据手册 (本轮实读, 落盘 `state/.cache_iss244/mos/AO3400A.pdf`) p1 Pin Configuration 图: 排布 = G/S 一侧 + D 另一侧 (图上**未印引脚号**) ⇒ 编号 1=G / 2=S / 3=D 按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ 编号这一层标 [推算]",
        "p0": ""
      },
      {
        "ref": "Q_PG",
        "model": "DMP3098L",
        "opn": "DMP3098L",
        "bom_value": "DMP3098L (Diodes Inc P-MOS SOT-23 · −30V · VGS(th) typ −1.8V · IDSS ≤800nA)",
        "bom_opn": "DMP3098L (Diodes Inc SOT23 3-pin · −30V · RDS(on) 98mΩ typ@-4.5V · IDSS ≤800nA)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            58,
            "PWR_ON"
          ],
          [
            59,
            "BAT_SW"
          ],
          [
            60,
            "PWR_GOOD"
          ]
        ],
        "on_main_board": true,
        "charge_board": false,
        "pad_map": [
          {
            "pad": "1",
            "net": "PWR_ON",
            "at": "-1.4 -2"
          },
          {
            "pad": "2",
            "net": "BAT_SW",
            "at": "-0.13 -2"
          },
          {
            "pad": "3",
            "net": "PWR_GOOD",
            "at": "1.4 2"
          }
        ],
        "device_pin_order": {
          "1": "G",
          "2": "S",
          "3": "D"
        },
        "device_pkg": "SOT-23",
        "device_source": "Diodes `DMP3098L` 数据手册 (本轮实读, 落盘 `state/.cache_iss244/mos/DMP3098L.pdf`) p1 Pin Configuration 图: 排布 = G/S 一侧 + D 另一侧 (图上**未印引脚号**) ⇒ 编号 1=G / 2=S / 3=D 按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ 编号这一层标 [推算]",
        "device_evidence": "[官网] / 编号 [推算]",
        "checks": [
          {
            "pad": "1",
            "net": "PWR_ON",
            "at": "-1.4 -2",
            "device_role": "G",
            "netlist_role": "S",
            "match": false
          },
          {
            "pad": "2",
            "net": "BAT_SW",
            "at": "-0.13 -2",
            "device_role": "S",
            "netlist_role": "D",
            "match": false
          },
          {
            "pad": "3",
            "net": "PWR_GOOD",
            "at": "1.4 2",
            "device_role": "D",
            "netlist_role": "G",
            "match": false
          }
        ],
        "verdict": "★P0 (引脚序/角色级): ✘ 占位 land 与器件引脚序对不上",
        "fix": "板侧改 land: pad1: PWR_ON → PWR_GOOD; pad3: PWR_GOOD → PWR_ON  ★**同时网表 note 的角色必须同批改成写法A (S=BAT_SW / D=ON / G=PG)** ⇒ 否则按 note 的错角色排出来的 land 一样开机不通",
        "topology_note": "★**角色本身就错 (P0)**: 网表 note 定的「源极接 ON · 漏极接 BAT_SW」是高边 P-MOS 的错接 —— ISS-244 §3.3 写法B: 上电瞬间 ON 被 10 kΩ 下拉到 0 V ⇒ Vgs = 0 ⇒ 不导通; PG 高时 Vgs = +3.3 V (对 P 沟道是反向偏置) ⇒ **PG 高低都关 ⇒ 开机路径彻底不通**。⇒ 正确角色 = **S=BAT_SW / D=ON / G=PG** (写法A)。",
        "source": "Diodes `DMP3098L` 数据手册 (本轮实读, 落盘 `state/.cache_iss244/mos/DMP3098L.pdf`) p1 Pin Configuration 图: 排布 = G/S 一侧 + D 另一侧 (图上**未印引脚号**) ⇒ 编号 1=G / 2=S / 3=D 按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ 编号这一层标 [推算]",
        "target_pad_nets": {
          "1": "PWR_GOOD",
          "2": "BAT_SW",
          "3": "PWR_ON"
        },
        "p0": "pin-order"
      },
      {
        "ref": "R_SUPV_DIV1",
        "model": "0Ω ±1% 跳线",
        "opn": "RC0603JR-070RL",
        "bom_value": "0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板",
        "bom_opn": "RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            403,
            "V_SOC_IO"
          ]
        ],
        "on_main_board": true,
        "charge_board": false,
        "pad_map": [
          {
            "pad": "1",
            "net": "V_SOC_IO",
            "at": "0 0.1"
          },
          {
            "pad": "2",
            "net": "SUPV_SENSE",
            "at": "1.6 0.1"
          }
        ],
        "device_pin_order": {},
        "device_pkg": "",
        "device_source": "",
        "device_evidence": "- / 编号 -",
        "checks": [],
        "verdict": "★P0 (装配级): 0 Ω 且必装 + U_SUPV DNP ⇒ 短路到地 (见拓扑备注)",
        "fix": "",
        "topology_note": "★**装配级风险 (P0)**: 已落成 0 Ω 跳线且 dnp=**必装**, 而监督器本体 `U_SUPV` 三行 dnp=**DNP** ⇒ 装 0 Ω = 把 `V_SOC_IO` 经两臂短路到地 (ISS-190 同判) ⇒ 建议随 U_SUPV 一并置 DNP (G-10 降级①)。",
        "source": "板文件 + BOM 实读",
        "p0": "assembly"
      },
      {
        "ref": "R_SUPV_DIV2",
        "model": "0Ω ±1% 跳线",
        "opn": "RC0603JR-070RL",
        "bom_value": "0Ω ±1% 跳线 (首版装 0Ω) · V-3 分压最终阻值待 A1 拍板",
        "bom_opn": "RC0603JR-070RL (Yageo 0Ω 跳线 / Jumper 档 · 0.1W · 50V · −55~+155°C)",
        "bom_dnp": "必装",
        "netlist_rows": [
          [
            404,
            "SUPV_SENSE"
          ],
          [
            405,
            "GND"
          ]
        ],
        "on_main_board": true,
        "charge_board": false,
        "pad_map": [
          {
            "pad": "1",
            "net": "SUPV_SENSE",
            "at": "0 0.1"
          },
          {
            "pad": "2",
            "net": "GND",
            "at": "1.6 0.1"
          }
        ],
        "device_pin_order": {},
        "device_pkg": "",
        "device_source": "",
        "device_evidence": "- / 编号 -",
        "checks": [],
        "verdict": "★P0 (装配级): 0 Ω 且必装 + U_SUPV DNP ⇒ 短路到地 (见拓扑备注)",
        "fix": "",
        "topology_note": "同上 (两臂必须同进同退, 只改一颗 = 悬空分压)。",
        "source": "板文件 + BOM 实读",
        "p0": "assembly"
      }
    ]
  }
}
```
<!-- END ISS244 缺口收口基准块 -->

## §9 边界自证

| 边界 | 自证 |
|---|---|
| 不改网表 / 脚表 / BOM | 三个文件本轮只读; 落表清单只给 `ref+net` 锚点, 一行未改 |
| 不改 ISS-241 矩阵正文与门禁脚本 | `HW/PART_SELECTION_MATRIX_2026-11-16.md` 与 `HW/check_part_selection_matrix.py` 只读引用 |
| 不碰 PCB 布线 / 布局 / 板框 | 本单零板文件写入; land 重画结论全部交 hw-lead 那一趟 |
| 不写别人的分片 | 只写 `state/fragments/sw.yaml` (sw-lead 自己的), 走 `state/frag_write.py` 原子写 |
| 零外发 | 未发任何邮件 / 询价 / 问询 / 采购; 全部资料来自 web_search / web_fetch / 带 `--max-time` 的 curl + `pdftotext` |
| 不替老板拍板 | V-2 / V-3 / V-4 / G-1 / G-10 / LED 亮度档 全部只出依据 + 代价, 状态列写「需老板拍」 |
| 实物 [实测] = 0 条 | 本机无板; 所有 `[实测]` 都是**文件/网表/板文件实读**与**脚本实跑**, 不是实物测量 |
| `state/issue_log.yaml` 不自改 | 本单零写入 ⇒ verify 留给 main |

