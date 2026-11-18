# ISS-131 · RK3572 口径版 R-GEO 问询 · ★自查版（不发信）★

> ★**本单 = ISS-131**「ISS-124/125 问询口径改 RK3572 (ISP 16M→12M, CSI 3×→2×) + 球位号问询对象改瑞芯微/RK3576→RK3572 模组厂」
> ★**产出方式 = 自查公开资料**（老板 2026-11-12 02:02 口径：「不再发信，全靠自己查资料」）
> ★**产出人 = 项目总工 (main) · 01:3x 自办** ⇒ ★**verify_by = hw-lead（别人验 · 铁律）**
> ★**边界 = 零写板 · 零落表 · 零外发 · 不替老板拍板**

---

## 0 · 一句话结论

★**「口径改 RK3572」这三件事，对我方板侧的影响 = 零。**

- ★**ISP 16M→12M**：官方 datasheet Rev 1.1 明写 **「One channel ISP, 12M pixels」+「Maximum input: 4096x3072」** ⇒ ★**这是【单帧分辨率上限】，不是 MP/s 吞吐** ⇒ 我方 1080p60 需求在**分辨率维度不卡** [官方] ★
- ★**CSI 3×→2×**：官方 datasheet §1.2.7 明写 **「Support 2 MIPI CSI-2 interfaces」+「Two 4 data lanes of D-PHY v1.2」+「Each interface may be configured as 2x2 data lanes port」** ⇒ 物理 = **2 个 4-lane D-PHY，可拆成 4 个 2-lane 口** ⇒ ★**我方网表只用 `CSI_D0` 一路 4 lane** ⇒ ★**无论 2 接口还是 4 口，都不构成约束** [官方] ★
- ★**球位号**：★**项目内已有 `HW/PCB/FET3572C_PIN_TABLE.csv`（399 条 conn/num）** ⇒ ★**11 处 CSI/MCLK 落位与官方 datasheet 逐条对拍 11/11 一致** ⇒ ★**只剩「模组厂底面图 pin1 标号」一条真需要问 ⇒ 草稿已在盘（`state/outbox/som_balltable_inquiry.md`）⇒ ★**不发，等老板放行** ★

★**⇒ 结论：ISS-131 不构成「板那一趟」的新增阻塞项；本单可以按「口径已自查完成 · 只剩 1 条待老板放行的问询」收口。**

---

## 1 · 机器可复核的交叉核对（★不是手抄·是脚本跑出来的★）

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/_iss131_crosscheck_rk3572_caliber.py     # rc=0
```

★**脚本只读·零写板**：读 `HW/netlist_v1.csv` + `HW/PCB/FET3572C_PIN_TABLE.csv` + `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` ⇒ ★**板 md5 / 网表 md5 / 脚表 md5 / BOM md5 一个字节都不动**（★**本机校验 (md5 逐字节比对) 一致**★ · ★**措辞订正见 ISS-305 B5-5: 原文「实测」二字与证据等级标签 `[实测]` 撞名 ⇒ 这里只表示「本机跑脚本 + 比对 md5」, 不表示有实物实测**★）。

### 1.1 球位号自洽（11/11 ✔）

| 网表落位 | SoM pin | 球位 | 信号 | 与官方 datasheet |
|---|---|---|---|---|
| `CSI_D0_CK_P_SRC` | J_SOM_P4 pin79 | A20 | MIPI_DPHY_CSI0_RX_CLKP | ✔ |
| `CSI_D0_CK_N_SRC` | J_SOM_P4 pin77 | B20 | MIPI_DPHY_CSI0_RX_CLKN | ✔ |
| `CSI_D0_D0_P_SRC` | J_SOM_P4 pin67 | A19 | MIPI_DPHY_CSI0_RX_D0P | ✔ |
| `CSI_D0_D0_N_SRC` | J_SOM_P4 pin65 | B19 | MIPI_DPHY_CSI0_RX_D0N | ✔ |
| `CSI_D0_D1_P_SRC` | J_SOM_P4 pin73 | 1B14 | MIPI_DPHY_CSI0_RX_D1P | ✔ |
| `CSI_D0_D1_N_SRC` | J_SOM_P4 pin71 | 1C14 | MIPI_DPHY_CSI0_RX_D1N | ✔ |
| `CSI_D0_D2_P_SRC` | J_SOM_P4 pin85 | A22 | MIPI_DPHY_CSI1_RX_D0P | ★同球双名 ✔ |
| `CSI_D0_D2_N_SRC` | J_SOM_P4 pin83 | B22 | MIPI_DPHY_CSI1_RX_D0N | ★同球双名 ✔ |
| `CSI_D0_D3_P_SRC` | J_SOM_P4 pin91 | A23 | MIPI_DPHY_CSI1_RX_D1P | ★同球双名 ✔ |
| `CSI_D0_D3_N_SRC` | J_SOM_P4 pin89 | B23 | MIPI_DPHY_CSI1_RX_D1N | ★同球双名 ✔ |
| `CSI_MCLK_SRC` | J_SOM_P2 pin45 | AM32 | CAM_CLK0_OUT_M0 | ✔ |

★**「同球双名」是 RK3572 的正常设计**：`CSI0_RX_D2P` 与 `CSI1_RX_D0P` 是**同一个球 A22 的两个功能名**（官方 datasheet L1789 逐字：`MIPI_DPHY_CSI0_RX_D2P/MIPI_DPHY_CSI1_RX_D0P  A22`）⇒ ★**这正是「一个 4-lane 口可配成 2×2」的物理证据** ⇒ 我方把它当 CSI_D0 的 D2/D3 用，与官方口径完全一致。

### 1.2 CSI 通道数（官方逐字）

| 出处 | 逐字 |
|---|---|
| datasheet §1.2.7 | `Support 2 MIPI CSI-2 interfaces` |
| datasheet §1.2.7 | `Two 4 data lanes of D-PHY v1.2` |
| datasheet §1.2.7 | `Each interface may be configured as 2x2 data lanes port` |
| datasheet §1.2.7 | `Each port supports 4 virtual channels` |
| datasheet §1.2.8 (VICAP) | `Support receiving four groups of MIPI CSI interfaces,up to four IDs for each group` |

★**读法**：§1.2.7 说「2 个 CSI-2 接口 · 每个 4 lane D-PHY v1.2」；§1.2.8 VICAP 说「可收 4 组 MIPI CSI」 ⇒ ★**这两句不矛盾**：4 组 = 2 个 4-lane 口各拆成 2×2 后的 4 个 2-lane 口。 [官方]

★**我方用量**：网表里 CSI 数据对前缀只有 `CSI_D0` 一组（`CSI_D0_D0/D1/D2/D3` 四对 + `CSI_D0_CK` 时钟）⇒ ★**1 路传感器 · 4 lane** ⇒ ★**2 接口 / 4 口 对我方无差别**。

★**★但有一条硬架构约束必须记下来（★原文没说·我从「One channel ISP」推出来的★）★**：
★**ISP 是 `One channel` ⇒ 同一时刻只有 1 路传感器能进 ISP** ⇒ ★**多摄像头方案在 RK3572 上不成立（无论 CSI 物理上有几个口）** ⇒ ⇒ **这一条要写进 demo 选型硬判据**（ISS-156 的 camera 模组选型：只能 1 路）。 [官方 + 推算]

> ★★★【★★**本条已被 §5 收窄 —— 上句「多摄像头方案在 RK3572 上不成立」是比官方字面更宽的推算, ISS-305 (hw-lead 独立复验) 判 severity=high: 它将来会变成 demo 选型硬判据 ⇒ 会拿它去筛掉本来可行的多摄方案★★ ⇒ ★**官方字面只说「ISP 处理核 = 1 路 (One channel ISP) / CSI 物理有 2 接口 4 组口」; 「ISP 能否多摄并发」官方没写 ⇒ [0数据] ⇒ 要 TRM/官方确认**★ ⇒ ★**收窄后的正确读法 = 「实时 ISP 处理路数 = 1 (多路需 VICAP 虚拟通道 + 降帧时分)」; 「多摄并发最终能否做」= [0数据], 不许当硬判据用**★ ⇒ ★**逐条改法见 §5 (2026-11-18 04:1x main 追加式订正)· 老字一字未删留痕**★]**

### 1.3 ISP 12M（官方逐字）

| 出处 | 逐字 |
|---|---|
| datasheet §概述 | `RK3572 introduces a new generation 12-Megapixel ISP` |
| datasheet §1.2.8 | `Image Signal Processor V3.5` / `One channel ISP,12M pixels` / `Maximum input:4096x3072` / `Minimum input:264x264` |

★**读法**：4096×3072 = **12.58 Mpixel** ⇒ ★**「12M」是【单帧分辨率上限】，与 `Maximum input` 自洽** ⇒ ⇒ ★**它不是 MP/s 吞吐**。

★**★补一条精确换算 (★ISS-305 B5-6 · 防止下一个人把「12M」当十进制 12,000,000 用·差 4.86%·对 1080p 无影响★)**★: ★**12M = 12 × 2^20 = 12,582,912 像素 = 4096 × 3072 精确相等 (二进制口径)**★ ⇒ ★**官方「12M」是 2 的幂口径 ⇒ 与 `Maximum input 4096x3072` 逐位对得上; 若按十进制 12,000,000 读则差 4.86% (★对 1080p 两种读法都不构成约束★)★**

★**我方需求比对**：

| 维度 | 我方 | RK3572 上限 | 判定 |
|---|---|---|---|
| 分辨率 | 1920×1080 (OV04C10 @1080p60·老板 10-29 定) | 4096×3072 | ★**不卡** [官方] |
| 吞吐 | 1920×1080×60 = **124.4 MP/s** | ★**datasheet 全文检索不到 ISP 的 MP/s 上限** | ★**[0数据]** |

★**⇒ 这条缺口【没有因为换芯而变好，也没有变坏】**：
- ★RK3576 侧同样没给 MP/s（★ISS-124 已 verified，但那一条 MP/s 仍挂着★）
- ★RK3572 侧 datasheet Rev 1.1 也没给 ⇒ ★**[0数据] 依旧**
- ★⇒ **降级方案（不许拿经验值冒充实测）**：
  1. ★**官方 TRM / 产品页**（★本机只留了 datasheet V1.1·无 TRM ⇒ 需联网查·标 [官网]★）
  2. ★**板端实测**（★ISS-210 已把 60ms 判据链 + ISP 段打点备好 ⇒ 板那一趟一到就能判★）
  3. ★**在拿到 (1) 或 (2) 之前，任何 MP/s 数字都只能标 [推算] 并写清推算链** ★

---

## 2 · 三个问询对象的处置（★口径改完·谁还欠什么★）

| 原问询 | 原对象 | ★新对象/新口径 | ★现在还欠什么★ |
|---|---|---|---|
| ISP MP/s 吞吐上限 + 动态功耗曲线 | 瑞芯微/RK3576 模组厂 | ★**RK3572 口径**（12M 单通道 ISP · 4096×3072 上限） | ★**MP/s = [0数据]** ⇒ TRM 或板端实测（ISS-210）★ |
| ISP 动态功耗 vs 吞吐曲线 | 同上 | ★同左 | ★**[0数据]** ⇒ 同上；★与 ISS-130（670mW vs 43°C 红线）同源 ⇒ **必须在同一次实测里同时判** ★ |
| 球位号 / pin1 标号 | 瑞芯微/RK3576 | ★**RK3572 模组厂（FET3572C）** | ★**只剩「模组底面图 pin1 标号」** ⇒ ★草稿已在盘 `state/outbox/som_balltable_inquiry.md` ⇒ ★**不发·等老板放行**★ |

★**★纪律：以上任何一条都不许本 job 自己发出去★**（老板 2026-11-11 19:31 + 2026-11-12 02:02）★

---

## 3 · 诚实边界

1. ★**实物 [实测] = 0 条**（★本机无板·无量具★）—— 本单全部结论来自 **官方 datasheet Rev 1.1（项目内留存 PDF + txt）** + **项目内 `FET3572C_PIN_TABLE.csv`** + **本机网表**。
2. ★**MP/s 吞吐 = [0数据]** —— 本单**没有**解决它，只把它准确地标成「官方没给 · 只能 TRM 或实测」，并指到 ISS-210。
3. ★**「One channel ISP ⇒ 同时只能 1 路传感器」** 是 [官方 + 推算] 的合成结论，★**建议进决策页给老板确认**（★因为它约束 demo 选型，但老板 10-29 已定的 1 路方案与它一致 ⇒ 不构成冲突★）。
4. ★**本单零写板 · 零落表 · 零外发 · 未自签 `state/issue_log.yaml`**（★签字 = main 的活·复验 = hw-lead 的活★）。
5. ★**引用的官方文档版本 = `RK3572 Datasheet Rev 1.1`**（★`HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` · 2,414,580 B · 解析产物 `rk3572_datasheet_V1.1.txt` 143,755 B★）。

---

## 4 · 复现命令（★复验人照这条跑★）

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/_iss131_crosscheck_rk3572_caliber.py    # ★rc=0★ · 11/11 球位号 + CSI 口径 6 条 + ISP 口径

# 零写板双证 (★跑前跑后都比★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat  -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb       # ★应停在 2026-11-06 07:07:17★
```


---

## 5 · ★★【追加式订正】★ over-claim 收窄 + 两条措辞订正 ★ (★2026-11-18 04:1x · main · ISS-305 独立复验判决落地★)

> ★**追加人**: 项目总工 (moli) · cron `775d9893` · ★**追加时刻**: 2026-11-18 04:1x
> ★**依据**: `HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md` §B3-C (★「部分 over-claim」判决★) + §B5-4 (★severity=high★) + §B5-5 / §B5-6 (★severity=low★)
> ★**纪律**: ★**append-only —— 上面 §1~§4 的老字一个字未删未改 (★只有 §1.2 / §1.3 / 开头三处加了【指向本节的箭头注记】+ 一处措辞订正★)· 留证链完整★**

### 5-1 · ★★over-claim 的原文与官方字面 (★逐字对照★)★

| 项 | 内容 |
|---|---|
| ★**老字 (§1.2 L64)** ★ | ★**「ISP 是 `One channel` ⇒ 同一时刻只有 1 路传感器能进 ISP ⇒ 多摄像头方案在 RK3572 上不成立（无论 CSI 物理上有几个口）⇒ 这一条要写进 demo 选型硬判据（ISS-156 的 camera 模组选型：只能 1 路）」** ★ `[官方 + 推算]` |
| ★**官方字面 (datasheet Rev 1.1)** ★ | §1.2.8 = ★**`One channel ISP, 12M pixels`** ★ · §1.2.7 = ★**`Support 2 MIPI CSI-2 interfaces` + `Two 4 data lanes of D-PHY v1.2` + `Each interface may be configured as 2x2 data lanes port`** ★ · §1.2.8 VICAP = ★**`Support receiving four groups of MIPI CSI interfaces`** ★ |
| ★**差距在哪** ★ | ★**官方说的是「ISP 处理核 = 1 路」; 老字把它推成了「多摄方案整体不成立」+「只有 1 路」⇒ ★**这是比官方字面更宽的一步★** ⇒ ★**官方从未写「ISP 只能挂 1 个 sensor」, 也没写「多摄并发不可能」⇒ 那一条 = [0数据]⇒ 要 TRM / 官方确认★** |

### 5-2 · ★★收窄后的正确表述 (★ISS-305 建议·照它执行★)★

| 项 | 收窄后 |
|---|---|
| ★**可以说 (★[官方]★)** ★ | ★**RK3572 = `One channel ISP` ⇒ 实时 ISP 处理路数 = 1** ★ (★官方逐字★) |
| ★**可以说 (★[推算]★)** ★ | ★**若要多路传感器实时进 ISP ⇒ 需走 VICAP 虚拟通道 + 降帧/时分 (本项目未验证该路径可行性)★** |
| ★**不能说 (★[0数据]★)** ★ | ★**「多摄像头方案在 RK3572 上不成立」/「只能 1 路」⇒ 官方没写 ⇒ 不许当硬判据用★** ⇒ ★**ISS-156 的 camera 模组选型【不许】拿它去筛掉本来可行的多摄方案★** |
| ★**要定死这一条怎么办** ★ | ★**查官方 TRM / 产品页 (★老板 2026-11-12 02:02「不再发信·全靠自己查」口径★) ⇒ 查到落 `[官网]` + 证据副本 ⇒ 查不到就保持 [0数据] + 降级方案★** (★= ISS-305 B5-3, 已登记为 need★) |

### 5-3 · ★★对下游的影响 (★哪几条要跟着改口径★)★

| 下游 | 原来怎么写的 | ★**收窄后** ★ |
|---|---|---|
| ★**ISS-156 (demo camera 模组选型)** ★ | 拿「只能 1 路」当筛选前提 | ★**前提改成「实时 ISP 路数 = 1 (官方) + 多摄并发 = [0数据]」⇒ 选型时按自己判定的需求路数筛, 不拿未证实的结论筛★** |
| ★**决策页 §A-补28 的那条** ★ | 「多摄方案不成立」列成事实项 | ★**已在 `DECISION_INDEX_2026-11-18.md` §D / `DECISION_PENDING_2026-11-16.md` §A-补29 一并订正 (★append-only★)★** |
| ★**本交付页 §3-3 的诚实边界** ★ | 「是 [官方 + 推算] 的合成结论, 建议进决策页给老板确认」 | ★**保留 (★老字未删★) ⇒ 但决策页那条已按 §5-2 收窄 ⇒ 现在状态 = 「已收窄, 多摄并发仍 [0数据]」★** |

### 5-4 · ★本节自证 (★main 2026-11-18 04:1x 本机实跑★)

| 项 | 读数 |
|---|---|
| ★**零写板** ★ | 板 `611b869e13518c3c023fb178f91a0075` · mtime 仍 `2026-11-06 07:07:17` ⇒ 本节未写板 ★ |
| ★**零落表** ★ | 网表 `843e4065…` / 脚表 `9174309d…` / BOM `5b999399…` / 落表台账 未动 ★ |
| ★**零改闸** ★ | `HW/check_netlist_selfconsistency.py` / `state/check_stage_g1a.py` / `state/gate_check.py` 只读未编辑 ★ |
| ★**零外发** ★ | 本节不发信 · 不联系供应商 · 不下单 ★ |
| ★**不替老板拍板** ★ | 本节只收窄一条【事实表述】+ 补一条【二进制换算】+ 修一处【措辞撞名】⇒ 不涉及任何决策项的建议默认值 ★ |
| ★**append-only** ★ | §1~§4 老字未删未改 · 仅加箭头注记 + 追加本节 · 备份 `HW/RK3572_INQUIRY_CALIBER_V2.md.bak_20261118_0410_overclaim_narrow` ★ |
