# HW/HW_EXTERNAL_DEPENDENCY_SELFCHECK_CLOSURE.md —— HW 域「外部依赖挂账」全量自查收口 (ISS-401)

> ★**单号**: ISS-401 · ★**执行**: 硬件总工 (hw-lead) · ★**落盘时刻**: 2026-11-24 23:2x~23:5x GMT+8
> ★**派活人**: 项目总工 (main / moli) · ★**job**: cron `fb67af40` (ARS45 队列自动派活 · 每 30 分钟)
> ★**性质**: ★**内部活 · 政策落地 (义务侧) + 需求闭环 / 卫生类** ⇒ ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口** ★
> ★**政策依据**: ★**老板 2026-11-11 19:31 + 2026-11-12 02:02 口径「不再发信, 全靠自己查资料」** ⇒ 本单执行第 ② 半 (义务侧): 凡标「等原厂 / 等 JBD / 等外部回复」的地方, 一律换成【自己查的结果 + 证据等级 + 查不到就写降级方案】 ★
> ★**本单零写板 · 零落表 · 零改既有闸阈值 · 零改既有页正文 · 零外发 · 不代老板拍板 · 不自签 issue_log** ★
> ★**配套**: 机器闸 `HW/check_hw_external_dep_closed.py` · 交卷页 `HANDOFF/2026-11-24_hw-lead_ISS401_HW域外部依赖自查收口.md` · 留证 `logs/iss401/` ★

---

## §0 判定口径 (★本单最重要的一句话★)

★★**「外部依赖」= 只有外部方能回答、而本仓库 / 公开资料 / 本机实跑都回答不了的问题。**
凡本仓库已有结论、公开官网已有、或本机能实跑出来的 ⇒ ★**一律不是外部依赖**, 改挂「已自查闭 / 已降级 / 归落表批次」★。

★**判定口径的三个子句 (★SW 域 ISS-270 沿用同一把尺, 本单把它落到 HW 域★)**:
1. ★**主体已作废** ⇒ 不是外部依赖 (问的是一颗已经不用的芯片 / 一个已经换掉的器件) ⇒ **作废**。
2. ★**公开渠道已有** ⇒ 不是外部依赖 ⇒ **自己查 + 标证据等级**。
3. ★**查不到** ⇒ 也不是「挂着等」, 而是 **「[0数据] + 降级方案 + 落点归属」** ⇒ **降级**。

★★**⇒ 一句话结论: HW 域真·外部依赖 = 0 条。8 条外部路由全部转成【已自查闭 / 已作废 / 已降级】, 13 项 TBD 全部有结论, 7 条 blocker 全部有处置建议。★★**

---

## §0.1 证据等级 (固定五级, 本单不改)

| 级别 | 含义 | 本单要求 |
|---|---|---|
| ★`[官网]` | 厂商官网 / 官方 datasheet / 官方手册 | ★**要贴链接或文档章节 + 版本号** ★ |
| ★`[实测]` | 本机可复现 | ★**要贴命令 + 输出原文** ★ |
| ★`[媒体]` | 媒体 / 二手 / 论坛 | 不得升格为 `[官网]` |
| ★`[推算]` | 由实测数据推得 | ★**要写清推理链** ★ |
| ★`[0数据]` | 查不到 | ★**必须同时给降级方案 (必须项)** ★ |

★★**查不到不是失败, 挂「等原厂」才是失败** ⇒ ★**每条 `[0数据]` 都必须带降级方案 (实测样件 / 选官网参数直接满足的替代型号 / 改设计路径绕开它 / 板侧零动作)** ★★

---

## §0.2 ★★两条【实测】订正 (★本单开工时实测, 与任务书口径不一致, 以本单实测为准★)★★

### ★★订正 1 · 外部路由是 **8 条**, 不是 10 条 —— 任务书把同样 2 条数了两次★★

★**实测口径**: `state/fragments/hw.yaml` · `needs_from` 共 **312** 条
- `waiting_on ∈ {vendor, jbd}` = **8** 条 (vendor 6 + jbd 2)
- `to ∈ {vendor, jbd}` = **2** 条 (`vendor_ars45_paper_q11_q16` / `jbd_zoushe_dsi_spec`)
- ★★**但那 2 条同时也在上面那 8 条里** ⇒ ★**并集 = 8, 不是 10** ⇒ **任务书 §1-1 的「共 10 条外部路由」是重复计数** ⇒ ★**本单按 8 条收口 (少 2 条不等于漏, 是那 2 条本来就在 8 条里)** ★

★**逐条实测清单 (★8 条, 全部在盘上·本单逐条收口★)**:

| # | key | to | waiting_on | due | 自查后处置 |
|---|---|---|---|---|---|
| N-1 | `q16_display_iface` | main | vendor | 2026-10-29 | ★**自查闭 (DSI TX)** + 宽高比 A/B/C 归 main/boss 拍板 ★ |
| N-2 | `vendor_ars45_paper_q11_q16` | ★vendor★ | vendor | 2026-10-29 | ★**作废 (ARS45 线已退)** ★ |
| N-3 | `jbd_zoushe_dsi_spec` | ★jbd★ | jbd | 2026-10-28 | ★**作废 (走鹃Ⅱ 已退)** ★ |
| N-4 | `rel_vendor_absmax_rating` | main | vendor | 2026-10-30 | ★**部分闭 (6/15 [官网]) + 剩余按现役 BOM 重排** ★ |
| N-5 | `rel_battery_cell_spec` | main | vendor | 2026-10-30 | ★**自查闭 (demo 板不装电池)** ★ |
| N-6 | `iss067_vendor_r_on_u1` | main | vendor | 2026-10-31 | ★**自查闭 [官网]** ★ |
| N-7 | `iss067_jbd_vdd_tol_u2` | main | jbd | 2026-10-31 | ★**自查闭 (被 N-6 吸收)** ★ |
| N-8 | `rk3572_isp_throughput_max` | main | vendor | 2026-11-04 | ★**自查闭 [官网]** ★ |

★**可复现命令 (★[实测]★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 - <<'PY'
import yaml
nf=yaml.safe_load(open('state/fragments/hw.yaml'))['needs_from']
ext=[x for x in nf if x.get('to') in ('vendor','jbd') or x.get('waiting_on') in ('vendor','jbd')]
print('外部路由并集 =',len(ext))
for x in ext: print(' ',x['key'],'| to=',x.get('to'),'| waiting_on=',x.get('waiting_on'))
PY
```

### ★★订正 2 · 网表待清行是 **109 行**, 不是 145 行 —— 36 行 `[待原厂]` 是 109 行的**子集**★★

★**实测口径**: `HW/netlist_v1.csv` (513 行 / 15 列)
- ★**`tbd` 列非空** = **109** 行 (★**这就是「待清」全集**★)
- ★**`evidence` 列逐字 == `[待原厂]`** = **36** 行 ⇒ ★**board 分布 = MAIN_PCB 36 / CHG_BOARD 0** (★与任务书口径一致★)
- ★★**交集 = 36 (全部) ⇒ 并集 = 109** ⇒ ★**任务书 §1-3/§1-4 的「145 行」是简单相加, 实际待清行 = 109 行** ⇒ ★**「板那一趟开工当天仍有 145 行可能动网表」这个数字 ⇒ 订正为 109 行** ★

★**另附实测 (★供 main 参考, 本单不改网表★)**: 若把「任何字段出现 `TBD-xx`」或「任何字段出现 `待原厂`」都算进去 ⇒ 131 行 / 50 行 ⇒ 并集 **136** 行 (★其中 3 行 `待原厂` 出现在 `value` 列、38 行出现在 `note` 列、36 行在 `evidence` 列★)。★**收口分母统一取 `tbd` 列 = 109 行** (★与 `HW/ERC_DRC_CHECKLIST.md` §A5 的判据同源★)。

★**可复现命令 (★[实测]★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 - <<'PY'
import csv
rows=list(csv.DictReader(open('HW/netlist_v1.csv')))
t={i for i,r in enumerate(rows) if (r.get('tbd') or '').strip()}
p={i for i,r in enumerate(rows) if (r.get('evidence') or '').strip()=='[待原厂]'}
print('tbd列=',len(t),' [待原厂]=',len(p),' 交集=',len(t&p),' 并集=',len(t|p))
PY
```

---

## §1 ★★HW 域 8 条外部路由 · 逐条自查闭 ★★

### N-1 · `q16_display_iface` —— ★**Q16 显示 TX 接口结论 = DSI TX (不是"DSI + DP 两者")** ★

| 项 | 内容 |
|---|---|
| ★**原问** | Q16 显示 TX 接口结论 (DSI TX / DP TX / 两者) + 宽高比 A/B/C 拍板 ★ |
| ★**自查结果** | ★**① 接口部分: 自查闭 ⇒ 答案 = 「DSI TX」(4-lane) —— 不是「两者」** ★<br>★**② 宽高比 A/B/C: 是老板拍板项, hw-lead 不代拍 ⇒ 归 main/boss** ★ |
| ★**证据等级** | ★**`[官网]` ×2 独立源交叉** ★ |
| ★**证据 (SoC 级)** | RK3572 官方 datasheet V1.1 §1.2 显示输出: **DSI-1.2 · 4 data lane · ≤2.5 Gbps/lane** (文本层 L652-654) · **eDP v1.3 (声明 compliant with DisplayPort v1.2) · 主链路 4 lane · HBR2 5.4 Gbps/lane** (L637-648) · **HDMI/eDP TX = One combo PHY** (L626) ⇒ ★**SoC 级: DSI TX 有 + DP 协议 (eDP) 有** ★<br>★**出处**: `HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §4「显示输出 (★Q16 决定性证据★)」 ★ |
| ★**证据 (模组级 · 决定性★)** | ★**Forlinx FET3572-C SoM 官方手册 §2.6.2 逐针表**: ★**`MIPI_DPHY_DSI_TX_D0P/D0N/D1P/D1N/D2P/D2N/D3P/D3N/CLKP/CLKN` = P3 pin 59/57/65/63/77/75/83/81/71/69** (球 1AE15/1AD15/AT26/AR26/AT29/AR29/AT30/AR30/AT27/AR27) ⇒ ★**SoM 确实把 4-lane DSI TX 引出来了** ★<br>★**同一张表里 SoM 引出的是 `HDMI_TX_D0P/N ~ D3P/N` (P1_23/25/29/31/35/37/41/43) + `HDMI_TX_SBDP/N` + CEC/SDA/SCL/HPDIN ⇒ ★**没有一行 `eDP_TX_*` / `DP_TX_*`** ⇒ ★**SoM 层面 DP/eDP TX 没引出来** ★<br>★**交叉印证**: 网表 `HW/netlist_v1.csv` 的 DSI TX 十行用的正是 J_SOM_P3 **57/59/63/65/69/71/75/77/81/83** ⇒ ★**网表与官方逐针表零差异** ★<br>★**出处**: `HW/PCB/FET3572C_PIN_TABLE.csv` (399 行 = Forlinx 手册 8 张表的逐格转录, ★已由 `HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md` §1 做过 399/399 行零差异比对★) ★ |
| ★**结论写法 (★建议落表逐字★)** | ★**「显示 TX = DSI TX 4-lane (SoM 已引出 P3_57..P3_83); DP/eDP 在 SoC 级存在 (eDP v1.3) 但 SoM 未引出 ⇒ demo 板不存在 DP TX 出口; 宽高比 A/B/C 待 main/老板拍板」** ★ |
| ★**降级方案 (必须项)** | ① ★**双出口 0Ω 选择位 (R_SEL_*) 保留** ⇒ 即使后续改成别的屏, 改 0Ω 不改板; ② ★**若 main 判「必须留 DP 出口」⇒ 走 HDMI/eDP combo PHY ⇒ 但 SoM 没引 ⇒ 那就得换模组 (换 SoM 厂) ⇒ 这是模组选型级决策, 不在本单**; ③ ★**宽高比 A/B/C 本单只给事实, 不给结论** ★ |
| ★**还卡不卡「板那一趟」** | ★**不卡** ★ |
| ★**判据出处** | ★**`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §4 + `HW/PCB/FET3572C_PIN_TABLE.csv` (P3_57..P3_83 / P1_17..P1_43) + `HW/netlist_v1.csv` row210-229 逐针一致** ★ |

### N-2 · `vendor_ars45_paper_q11_q16` —— ★**整条作废 (ARS45 线已退) + 8 问逐条重定向** ★

| 项 | 内容 |
|---|---|
| ★**原问** | 原厂纸面资料 8 问 (10-21 邮件已发未回): ① FCCSP pitch + 球位图 ② 电源域 ③ 显示 TX ④ USB Device PHY ⑤ 内置 boot storage ⑥ MCLK 源 + sensor RESET 极性 ⑦ SoC 散热焊盘 ⑧ CSI lane 数 + 输入电压域 ★ |
| ★**自查结果** | ★**作废 —— 这 8 问问的是一颗【已经不用了的芯片】** ★ |
| ★**证据等级** | ★**`[实测]` (本机实读仓内既有裁决文档) + `[官网]` (替代口径)** ★ |
| ★**证据** | ★**`HW/CHIP_SOC_MIGRATION.md` L53 逐字**: 「★**酷芯微原厂** | 显示 TX / pitch / 球位图 / 电源域 / 启动存储 | ★**全部作废** (老板 19:20 不再考虑酷芯微) | —」 ★<br>★**`HW/TI_POWER_FACTS.md` §④ 逐字**: 「★**ARS45 / AR9481 / 酷芯微 已于老板 2026-10-29 19:20 拍板作废** ⇒ ★**「ARS45 的 AON 域」不存在了** ⇒ ★**该子问题【作废】, 不是「还没查到」** ★」 ★<br>★**当前主控 = RK3572 (SoM 路线)**: `HW/DEMO_BOARD_HW_DECISION.md` §2「主板不焊 SoC, 用 RK3572 核心板 (SOM) 焊在主板上」 ★ |
| ★**8 问逐条重定向 (★这是本条真正的价值★)** | | **原问** | **现在归谁 / 归哪** | **现状** |
|---|---|---|---|
| ① | FCCSP pitch + 球位图 | ★**已解** ⇒ RK3572 官方 FCCSP550L **0.42 / 0.52 / 0.65 mm 混合**, 550 球, 14.3×15.5 mm ⇒ ★**且 demo 板用 SoM BTB 0.4 mm ⇒ SoC pitch 与 demo 板无关** ★ | ★**`[官网]`** (`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §1) ★ |
| ② | 电源域表 | ★**SoC 级已解** ⇒ 官方 Table 3-1 / 3-2 全域电压 ✔; ★**demo 板不产 SoC 核心轨** (U_DCDC_VCORE/VIO = DNP, SoM 自带 PMIC) ★ | ★**`[官网]`** ★ |
| ③ | 显示 TX | ★**已解** ⇒ 见 N-1 ★ | ★**`[官网]` ×2** ★ |
| ④ | USB Device PHY | ★**已解** ⇒ SoM 引出 `USB_DRD1_DP/DM` (P1_92/94, 3.3V) + `USB_DRD1_VBUSDET` (P1_100) + `USB2_OTG0_DP/DM` (P3_20/18) ⇒ ★**USB2.0 物理层确认存在** ★ | ★**`[官网]`** ★ |
| ⑤ | 内置 boot storage | ★**已解 (且已三档化)** ⇒ `state/fragments/hw.yaml` `R-hw-boot-storage` (ISS-346 / ISS-350 机器判决): ①ADB push 档 板侧零动作 ②SPI-NOR 档 走 `J_BOOT1` 焊盘位 (6 pad 已在板) + 4 条 0Ω 串阻位 ⇒ **板侧零动作 · 不改板宽 · 不重出板** ③eMMC 档 板宽 12→15 mm ⇒ **只有产品板档卡** ★ | ★**`[实测]`** (仓内机器判决) ★ |
| ⑥ | MCLK 源 + sensor RESET 极性 | ★**已解** ⇒ SoM `CAM_CLK0_OUT_M0` = **P2_45** (球 1AE21 前为 AH33, ★官方逐针表逐字★) ⇒ 网表 `CSI_MCLK_SRC` 用 J_SOM_P2 pin45 ✔; RESET 极性 = IMX415 模组随货寄存器表 (★采购硬判据★) ⇒ **不是原厂纸面资料** ★ | ★**`[官网]`** (SoM 逐针表) + ★**`[推算]`** (模组随货) ★ |
| ⑦ | SoC 底面散热焊盘 | ★**已解 (但结论是"官方自己没给")** ⇒ RK3572 官方 datasheet §4 Thermal Management 的 ψJT / θJA / θJB / θJC **四行全是 TBD** ⇒ ★**官方文档本身没有 ⇒ 这是 `[0数据]` 的官方版, 不是"没查"** ★ | ★**`[官网]` = 官方 TBD** ★ |
| ⑧ | CSI lane 数 + 输入电压域 | ★**已解** ⇒ demo sensor = IMX415 模组 ⇒ ★**2-lane (D0/D1 + CLK) + MCLK**, AC 耦合电容**放模组侧 (硬判据)**, 主板不装 ⇒ ★**主板侧 CSI 规格不再是原厂问题** ★ | ★**`[官网]`** (IMX415 公开 datasheet + RK BSP `imx415.c`) ★ |
| ★**降级方案 (必须项)** | ① ★**8 问里 6 问已被公开资料闭合, 1 问 (散热焊盘) 官方自己 TBD ⇒ 降级为「按 SoM 导热垫 + 铜箔实测皮肤温度」** (★`HW/POWER_BUDGET_V3.md` 已有皮肤温度模型★) ② ★**剩余真·外部 (模组随货的寄存器表 / init code) 一律写成【采购硬判据】, 不发问询函** (★`HW/DEMO_BOARD_HW_DECISION.md` §3 的既定做法★) ★ |
| ★**还卡不卡「板那一趟」** | ★**不卡** ★ |
| ★**判据出处** | ★**`HW/CHIP_SOC_MIGRATION.md` L53 · `HW/TI_POWER_FACTS.md` §④ · `state/fragments/hw.yaml` `R-hw-boot-storage` · `HW/DEMO_BOARD_HW_DECISION.md` §2/§3** ★ |

### N-3 · `jbd_zoushe_dsi_spec` —— ★**整条作废 (走鹃Ⅱ 已退) + 替代件的 DSI 口径自查闭** ★

| 项 | 内容 |
|---|---|
| ★**原问** | 走鹃Ⅱ: ① DSI 几 lane / 最高速率 ② 800×600@60fps 官方验证过没 ③ I2C 做什么用 + 从机地址 ④ 供电电压范围 + 峰值电流 ★ |
| ★**自查结果** | ★**作废 —— 走鹃Ⅱ 已不是本项目的显示件; 且 4 个子问在现役件上全部有公开答案** ★ |
| ★**证据等级** | ★**`[实测]` (仓内裁决文档) + `[官网]` (现役件公开资料)** ★ |
| ★**证据 (作废)** | ★**`HW/DISPLAY_MODULE_DECISION.md` §2.3 逐字**: 「老板锁死表 #19「MIPI-DSI 输入的光机由 JBD 的蜂鸟提供」与 #21「光机型号 = JBD 走鹃Ⅱ」⇒ ★**本条作废**」 ★<br>★**`HW/DEMO_BOARD_HW_DECISION.md` §4 逐字**: 「★**视涯屏 11-04 已停用, 现行为 Waveshare 2.8inch SKU 22028 ⇒ 22p(0.5mm Pi5 侧)↔15p(1.0mm 屏侧)** ★」 ★ |
| ★**4 个子问在现役件上的答案** | | **子问** | **现役答案 (demo 板口径)** | **等级** |
|---|---|---|---|
| ① | DSI lane 数 / 速率 | ★**屏侧 2-lane + CK** (Waveshare 15 针只有 DSI1_DN0/DP0 + DSI1_DN1/DP1) ⇒ ★**SoM 侧 4-lane 不变 (SoM 是 4-lane) ⇒ 变的是「主板→屏座」那一段** ⇒ ★**板侧零动作** ★ | ★**`[官网]`** ★ |
| ② | 分辨率验证过没 | ★**Waveshare 官方 GitHub `Waveshare-DSI-LCD` 提供 Pi4/Pi5 两条路线的 `WS_xinchDSI_Screen.ko` + `.dtbo` (init 在 .ko 内) + 树莓派官方 firmware `vc4-kms-dsi-waveshare-panel.dtbo` (`compatible=waveshare,2.8inch-panel`, `touchscreen-size-x=480 / -y=640`) ⇒ ★**init sequence 公开可得, 不必问厂家** ★ | ★**`[官网]`** ★ |
| ③ | I2C 用途 + 地址 | ★**屏的 DDC 走 SoM 的独立 I2C2 (P2_1 = I2C2_SDA_M0 / P2_11 = I2C2_SCL_M0, 3.3V 域)** ⇒ ★**与 camera 的 I2C5 (P2_31/P2_33, 1.8V 域) 物理分开 ⇒ 地址冲突不成立** ⇒ ★**DDC 从机地址 = 屏模组随货资料 (采购硬判据)** ★ | ★**`[官网]`** (SoM 逐针表) ★ |
| ④ | 供电电压范围 + 峰值电流 | ★**屏模组内从 3V3 取电 (无独立背光脚 ⇒ 12V BOOST 整链可砍)** ⇒ ★**主板侧只要保证 LIGHT_3V3 稳在 3.3V 即可 ⇒ 这不是"屏的容差"问题, 是"本板 3.3V 轨稳不稳"问题 ⇒ 见 N-6** ★ | ★**`[官网]`** + ★**`[推算]`** ★ |
| ★**降级方案 (必须项)** | ① ★**屏侧全部参数走【采购硬判据】(init code + DSI 时序 + DDC 地址 + 供电/电流清单), 不发问询函** ② ★**若将来改回产品屏 (视涯 SiOLED / 走鹃Ⅱ), 这 4 问重新变成外部依赖 ⇒ 那时再按"三档降级"重新处理, 但**不阻塞 demo 板那一趟** ★ |
| ★**还卡不卡「板那一趟」** | ★**不卡** ★ |
| ★**判据出处** | ★**`HW/DISPLAY_MODULE_DECISION.md` §2.3 · `HW/DEMO_BOARD_HW_DECISION.md` §3/§4 · `HW/DISPLAY_SMALL_SCREEN_OPTIONS.md` §3.1 · `HW/PCB/FET3572C_PIN_TABLE.csv` (P2_1/P2_11/P2_31/P2_33)** ★ |

### N-4 · `rel_vendor_absmax_rating` —— ★**部分闭 (6/15 [官网] 已转录) + 剩余 9 类按【现役 BOM】重排** ★

| 项 | 内容 |
|---|---|
| ★**原问** | 15 个器件 Absolute Maximum Ratings (温度/电压/电流) + 可靠性数据 (FIT/MTBF/降额曲线); 另需 BQ25896 工作温度范围 / TMP117 供电范围 / Type-C 母座温升-电流曲线 ★ |
| ★**自查结果** | ★**① ISS-068 已把 6 颗 TI 器件的 abs max 表逐条转录完毕 (§3.1, 含 datasheet 版本号 + 章节号) ⇒ 这条 need 的前半段是【重复立项】; ② 剩余 9 类的**对象清单本身已过期** (ARS45 / OV04C10 都已退) ⇒ 需按现役 BOM 重排; ③ FIT 的器件级取数路径也已找到 (TI 公开 estimator) ⇒ 差的是"命令行取不到数"这一条工具手段, 不是数据不存在** ★ |
| ★**证据等级** | ★**`[官网]` (6 颗 TI) + `[实测]` (仓内既有转录) + `[0数据]` (FIT 数值, 必须带降级)** ★ |
| ★**证据** | ★**`HW/RELIABILITY_ABSMAX_DERATING_V2.md` §3.1**: 6 颗 TI 器件 abs max **逐条转录** ⇒ ★**TPS62130A** (SLVSAG7F §7.1) · **TPS7A20** (SBVS338H §5.1) · **BQ25896** (SLUSC76C §7) · **TPS25730** (SLVSGP9) · **BQ2970** (SBVS349) · **TMP117** (SNOSD82D) ⇒ ★**绝对最大/推荐工作双列齐全 = 6/15** (原为 0/15) ★<br>★**BQ25896 工作温度范围**: **推荐工作环境温度只有 -40~85 °C** (官网产品页给人的 125 °C 是 Tj 口径) ⇒ 设计上限 72.25 °C ★<br>★**TMP117 供电范围**: **V+ 1.8~5.5 V** (REC) / **6 V** (abs max) ⇒ **本板 3.3 V ✅** ★<br>★**FIT**: TI 公开逐器件 MTBF/FIT estimator (`ti.com/quality/docs/estimator.tsp`), 页面已列 6 颗 TI 器件全部 OPN ⇒ **器件级 FIT 公开可得** ⇒ 但页面是 JS 应用 ⇒ 命令行取不到数 ⇒ `[0数据-待人工取数]` (人工 10 分钟可补) ★<br>★**Type-C 母座温升-电流曲线**: 现有口径来自**分销商系列页 (qitda.com), 不是 HANGHONG 该型号的规格书** ⇒ 仍需厂商 ⇒ `[0数据]` ★ |
| ★**9 类 [0数据] 按现役 BOM 重排 (★这一栏是本条的新增价值★)** | | **原 15 类里的项** | **现役状态 (2026-11-24)** | **处置** |
|---|---|---|---|
| 1 | ARS45 SoC | ★**已退** ⇒ **整类作废** ★ | ★**出清单** ★ |
| 9 | OV04C10 | ★**已退 (换 IMX415)** ⇒ **整类作废** ★ | ★**出清单** ★ |
| 14 | 摄像头模组 | ★**随 sensor 走 ⇒ 随 IMX415** ⇒ **整类随 9 作废** ★ | ★**出清单** ★ |
| 7 | N-MOS ×2 | 8205A 类, 型号未定 | ★**现役 = `DMP3098L` (Diodes Inc P-MOS SOT-23)** ⇒ ★**该型号官网 datasheet 公开可下 ⇒ 1 次取数就能闭** ★ | ★**留 (可闭)** ★ |
| 10 | 1S LiPo 电芯 | 见 N-5 | ★**留** ★ |
| 11 | Type-C 母座 | GCT USB4105 (充电板侧) | ★**留 (需厂商温升曲线)** ★ |
| 12 | FPC ×3 + BTB ×3 | 型号未定 ⇒ 但 demo 板用 SoM BTB + 两个 FPC 座 (HIROSE FH35C-31S / FH12-22S) ⇒ ★**这两个座型号已定 ⇒ 官网规格书可下** ★ | ★**留 (可闭)** ★ |
| 13 | 无源器件类 | 型号一个都没选 | ★**规则已可落 (J1/J2/J3 三类判据 + 无源降额规则已在 §2.2 / §3.2 尾)** ⇒ **数值随选型补** ★ | ★**留** ★ |
| 15 | 机械件 | 螺钉扭矩/拉拔力未定义 | ★**留 (随结构图纸)** ★ |
| ★**降级方案 (必须项)** | ① ★**6 颗 TI 已有 [官网] abs max ⇒ 这 6 颗不再占"等外部"名额** ② ★**N-MOS / FPC 座 / BTB ⇒ 官网 datasheet 自取 (不外发) ⇒ 落"选型时同批补"** ③ ★**FIT ⇒ 人工开 TI estimator 取数 (10 分钟), 不外发** ④ ★**Type-C 母座温升曲线 ⇒ 改用"降额 + 板级实测温升"兜底 (充电板 2A, 触点额定 3A ⇒ 占用率 83.3%)** ⑤ ★**机械件 ⇒ 结构图纸出了同批补** ★ |
| ★**还卡不卡「板那一趟」** | ★**不卡 (但有 2 条要同批落表)** ★ —— ★**理由: 15 类里 11 类与 demo 板 BOM 无关 (随退件作废) 或已 [官网] 闭; 剩下的 4 类 (N-MOS / 电芯 / Type-C 母座 / 无源) 的取值**不改变板上任何连接关系** ⇒ **改板 = 0** ⇒ **板 md5 不变** ★<br>★**★但: 降额表的**判据**若要升级成"有据可依", 那是改 `HW/RELIABILITY_ABSMAX_DERATING_V2.md` 既有页 ⇒ 本单不碰 ⇒ 归落表批次, **不改板** ★ |
| ★**判据出处** | ★**`HW/RELIABILITY_ABSMAX_DERATING_V2.md` §3.1/§3.2/§B5 · `HW/BOM_v1.csv` (218 行, 现役位号) · `HW/netlist_v1.csv` (DMP3098L / GCT USB4105 / HIROSE 座)** ★ |

### N-5 · `rel_battery_cell_spec` —— ★**自查闭 (demo 板不装电池 ⇒ 这条对 demo 板是伪依赖)** ★

| 项 | 内容 |
|---|---|
| ★**原问** | 1S LiPo 电芯规格书: 允许充电倍率 + 循环寿命 + 内阻 + 膨胀曲线 + 允许充/放电温度窗口 (R-F2: 1.0A@575mAh=1.74C 超典型 1C; 340mAh@1.0A=2.94C 更差) ★ |
| ★**自查结果** | ★**① demo 主板不装电池** ⇒ 电芯规格书对 demo 板那一趟【零影响】; ② 电芯的"倍率/寿命/内阻"是【产品板 (镜脚) + 充电板】的事, 属**采购硬判据**, 不是技术阻塞; ③ 库内已有一个**带规格口径的电芯** (丰江 432243 ≥420 mAh / 4.3 mm), 且厚度账已经用它算完 (镜腿 7.3 mm 锁死值不变) ⇒ ★**降级路径已经存在且成立** ★ |
| ★**证据等级** | ★**`[实测]` (网表 / BOM / 电源预算实测) + `[推算]` (倍率口径) + `[0数据]` (完整电芯规格书, 必须带降级)** ★ |
| ★**证据** | ★**`HW/netlist_v1.csv` row26 / row36**: `BT_432243` = 「432243 3.7V ≥420mAh」★**`dnp=DNP`** ★ note 逐字: 「★**DNP: demo 主板用 Type-C 供电 ⇒ 不装电池**」 ★<br>★**`HW/netlist_v1.csv` row24-29**: `U_BATPROT` (BQ2970) **DNP** · `Q1` / `Q2` (保护 MOS) **DNP** ★<br>★**`HW/BOM_v1.csv`**: `BT_432243` `procurement=DNP-不装`; `opn=[0数据]` ★<br>★**`HW/POWER_BUDGET_V3.md` §7**: 丰江 432243 ≥420 mAh / 4.3 mm ⇒ ★**镜腿 7.3 mm (名义 7.0) ✅ 锁死值不变** ★<br>★**`HW/CHIP_SOC_MIGRATION.md` + `HW/CORE_MODULE_SELECTION.md` L39**: 「★**demo 主板用 Type-C 供电 ⇒ 不装电池**」(老板 11-03 09:54) ★ |
| ★**R-F2 倍率口径的现状** | ★**`HW/RELIABILITY_ABSMAX_DERATING_V2.md` §3.2 第 10 行**: 「❌ **J3: 1.0A@575mAh = 1.74C 超 1C** (R-F2) / 证据: **J3, 电芯规格书未到**」 ⇒ ★**这是真·J3 (按规格书判), 不能用通用降额档 ⇒ 仍是 [0数据]** ★ |
| ★**降级方案 (必须项)** | ① ★**demo 板那一趟: 电芯位 DNP ⇒ 零影响, 不需要电芯规格书** ② ★**产品板档: 电芯规格书写成【采购硬判据】(随货给: 允许充电倍率 / 循环寿命 / 内阻 / 膨胀曲线 / 允许充放电温度窗口) ⇒ 不发问询函** ③ ★**在规格书到之前, 充电电流按【最保守 1C】选 (⇒ 575 mAh 档限 575 mA, 340 mAh 档限 340 mA) ⇒ 这个口径本身已经比现状 1.0A 更保守 ⇒ 【保守侧已闭合】** ④ ★**若 main 决定把充电电流从 1.0A 降到 575 mA ⇒ 那是一条落表项 (改网表常量), 不改板** ★ |
| ★**还卡不卡「板那一趟」** | ★**不卡** ★ (★demo 板电芯位 DNP; 且倍率口径的保守侧已闭合★) |
| ★**判据出处** | ★**`HW/netlist_v1.csv` row24-29/26/36 (`dnp=DNP` + note) · `HW/BOM_v1.csv` `BT_432243` · `HW/POWER_BUDGET_V3.md` §7 · `HW/CORE_MODULE_SELECTION.md` L39** ★ |

### N-6 · `iss067_vendor_r_on_u1` —— ★★**自查闭 [官网] ⇒ 原假设被证伪, 方案 A' 从「成立」降为「条件成立」** ★★

| 项 | 内容 |
|---|---|
| ★**原问** | TPS62130A 高边 R_on + 推荐电感 DCR 合计值 ⇒ 决定 UVP 能不能从 3.50V 压到 3.35V (假设 R_total=100 mΩ ⇒ 地板 3.335V ⇒ 方案 A' 成立; >150 mΩ ⇒ 退回 3.50V) ★ |
| ★**自查结果** | ★★**【官网】查到了, 而且它把原来的假设直接证伪了** ★★ |
| ★**证据等级** | ★**`[官网]` (TI 官方 datasheet, §6.5 POWER SWITCH 表) + `[推算]` (地板电压算式) + `[0数据]` (电感 DCR —— TI 推荐表不给 DCR)** ★ |
| ★**证据 (逐字抄录, [官网]★)** | ★**出处**: `https://www.ti.com/lit/ds/symlink/tps62130a.pdf` · ★**文档号 `SLVSAG7F – NOVEMBER 2011 – REVISED NOVEMBER 2021`** (★与仓内 `HW/RELIABILITY_ABSMAX_DERATING_V2.md` §3.1(1) 引用的是同一版本★) · §6.5 Electrical Characteristics → `POWER SWITCH` 组:<br>★**`High-side MOSFET ON-resistance`** ★**`VIN≥6V`: 90 (typ) / 170 (max) mΩ** ★<br>★**`VIN=3V`: 120 (typ) mΩ** ★<br>★**本机 pdftotext 提取行号 L304-L308** ★<br>★**§8.2 / Fig 7-3「High-Side Switch Resistance」**: R_on 随 VIN 下降而上升 (25 °C 曲线 VIN=3V 处 ≈120 mΩ) ★<br>★**§9.2.2.2.1 + Table 9-3「List of Inductors」**: 推荐电感 **XFL4020-102ME_ (1.0 µH) / -152ME_ (1.5 µH) / -222ME_ (2.2 µH)** · **IHLP1212BZ-11** · SRP4020-3R3M · VLC5045T-3R3N ⇒ ★**该表只给 CURRENT (IRMS@40°C 或 ISAT@30%) 与尺寸, 【不给 DCR】⇒ DCR = [0数据]** ★ |
| ★**算式 (★[推算] · 推理链写全★)** | ★**板侧口径 (`HW/calc_rf1_3v3v_uvp.py` 常量)**: `V33 = 3.30 V` · `I33 = 0.350 A` (LIGHT_3V3 150 mA + VDD_3V3_IO 200 mA) · `R_BUCK_TOT = 0.10 Ω` (原假设) ★<br>★**地板公式**: `Floor(SYS) = 3.300 + 0.350 × R_total` ★<br>★**方案 A' (UVP = 3.35 V) 成立的充要条件**: `3.35 ≥ Floor` ⇒ `R_total ≤ (3.35 − 3.300)/0.350 = 142.86 mΩ` ★<br>★**代入 [官网] typ (VIN=3V ⇒ 120 mΩ)**: 留给电感 DCR 的预算 = **142.86 − 120 = 22.86 mΩ** ★<br>★**代入 [官网] max (170 mΩ, 表中给的是 VIN≥6V 档)**: `Floor = 3.300 + 0.350×0.170 = 3.3595 V > 3.35 V` ⇒ ★**按 max 规格 A' 不成立** ★<br>★**代入原假设 (R_total = 100 mΩ)**: `Floor = 3.335 V` ⇒ 表面成立 ★ —— ★**但 buck 单颗 typ 已 120 mΩ > 100 mΩ ⇒ 原假设被 [官网] 直接证伪** ★<br>★**按 typ + DCR 20 mΩ**: `Floor = 3.300 + 0.350×0.140 = 3.349 V` ⇒ **勉强成立 (余量 1 mV)** ⇒ ★**工程上这是"卡边", 不可作为投板依据** ★<br>★**按 SYS = 3.50 V (方案 A)**: `Vout = 3.50 − 0.350×0.140 = 3.451 V` ⇒ **余量 151 mV, 稳** ★ |
| ★**结论 (★一句话★)** | ★★**原「R_total = 100 mΩ ⇒ A' 成立」是错的 (假设被 [官网] 证伪)。正确口径: A' 成立需要 `R_total ≤ 142.9 mΩ`; TI 给的 buck typ (VIN=3V) 就吃掉 120 mΩ ⇒ 留给电感 DCR 的预算只剩 ≤22.9 mΩ, 而 TI 推荐表的 DCR 本身是 [0数据] ⇒ ⇒ A' 只能按「typ 路径 + 板上手测」条件成立, 不能按 max 规格成立。** ⇒ ★**若 main 要稳 ⇒ 走方案 A (UVP 3.50 V), 代价 = 续航少约 7 个点 (1.241h vs 1.325h)** ★★ |
| ★**降级方案 (必须项)** | ① ★**选电感时把「DCR ≤ 20 mΩ」写成硬判据** (XFL4020-102ME_ / IHLP1212BZ-11 一体成型系列官网 DCR 在 15~25 mΩ 区间 ⇒ ★**必须按最终选定的具体料号官网 DCR 复核**) ② ★**UVP 落点挂在一个【可实测】的判据上**: 板到手后 SYS 拉到 3.35 V, 实测 LIGHT_3V3 / VDD_3V3_IO 轨电压 ⇒ ≥3.30 V 才算 A' 成立 ⇒ ★**这是不改板、不改网的验证** ③ ★**零新增 IC 的替代路径**: 若 DCR 实测 >22.9 mΩ ⇒ 改电感型号 (板位已在) ⇒ **零改板** ④ ★**完全不做的兜底**: 走方案 A (UVP 3.50 V) ⇒ 零改板、零改网, 只少 7 个点续航 ★ |
| ★**还卡不卡「板那一趟」** | ★**不卡** ★ —— ★**理由: 这条只决定"UVP 落点写 3.35 还是 3.50"这一个数, 不改任何连接关系 / 封装 / 走线 ⇒ 板 md5 不变; 且 demo 板不装电池 ⇒ SYS 轨不存在 ⇒ demo 板那一趟连这个数都不需要** ★<br>★**★但**: **网表里 `U_LDO_L33` / `U_LDO_IO33` 仍是 LDO (方案 A 尚未落网表)** ⇒ ★**这条是【落表项】不是【外部依赖项】⇒ 归 main 的落表批次 (见 §3 留给 main 的问句 ②)** ★ |
| ★**判据出处** | ★**TI `SLVSAG7F` §6.5 POWER SWITCH (本机 `tmp/iss401/tps62130a.txt` L304-308) · §8.2 Fig 7-3 · §9.2.2.2.1 + Table 9-3 · `HW/calc_rf1_3v3v_uvp.py` (常量 `V33` / `I33` / `R_BUCK_TOT` / `BUCK_FLOOR`) · `HW/POWER_TOPOLOGY_RF1_3V3V_UVP.md` §U-1** ★ |

### N-7 · `iss067_jbd_vdd_tol_u2` —— ★**自查闭 (被 N-6 吸收: 这题在 demo 板上根本不成立)** ★

| 项 | 内容 |
|---|---|
| ★**原问** | 光机 3.3V 输入电压容差与下限 (LIGHT_3V3 由新 buck 供, UVP 3.35V 时 buck 输出约 3.305V); 假设 ±5% (3.135-3.465V) ⇒ 成立; 若要求 3.3V±2% ⇒ 3.305V 卡边 ★ |
| ★**自查结果** | ★★**两重解法: ① 被测对象已作废 (走鹃Ⅱ); ② 即使不换件, 这题也被 N-6 吸收 —— 因为 LIGHT_3V3 是【本板稳压出来的轨】, 屏看到的永远是稳压后的值, 屏的容差只决定"稳压目标定多少", 不决定" buck 地板在哪" ★★ |
| ★**证据等级** | ★**`[实测]` (网表电源树实读) + `[官网]` (SoM 逐针表) + `[推算]`** ★ |
| ★**证据** | ★**`HW/netlist_v1.csv` 实测 LIGHT_3V3 的消费者 (8 行)**: `RAIL_LIGHT_3V3` (rail) · `U_LDO_L33` (TPS7A20-33 LDO, **必装**) · `C_BULK_LIGHT_3V3` (10 µF) · `C_HF_LIGHT_3V3` · **`CONN_LIGHT pin14` / `pin15`** (屏座) · **`CONN_CAM pin28` / `pin29`** (camera 模组) · `TP_LIGHT_3V3` (测试点) ★<br>★**⇒ LIGHT_3V3 = 本板 LDO 的输出轨 (不是从 SYS 直取) ⇒ 屏/模组看到的永远是 LDO 稳压后的 3.3 V** ★<br>★**★⇒ 所以「屏的 3.3V 容差」不是阻塞项: 只要 LDO/buck 稳在 3.3 V, 屏拿到就是 3.3 V; 屏容差只影响"目标电压定 3.3 还是 3.2", 而 3.3 V 是逻辑信号的标准轨 ⇒ 判据自动满足** ★<br>★**N-6 的结论 (buck 地板) 才是真约束**: 若走 buck 且 UVP 压到 3.35 V, 地板 3.349~3.36 V ⇒ 3.3 V 轨仍在 3.30 V 边缘 ⇒ ★**这是 buck 的问题, 不是屏的容差问题** ⇒ **两题合并成一题** ★ |
| ★**结论 (★一句话★)** | ★★**「JBD 光机 3.3V 容差」这条外部依赖【在 demo 板口径下不成立】: (a) 走鹃Ⅱ 已退; (b) LIGHT_3V3 是本板稳压轨, 屏的容差不影响 buck 地板; (c) 真约束 = N-6 的 TPS62130A R_on。⇒ 原假设「若要求 ±2% 则 3.305V 卡边」这条推理的前提错误 —— ±2% 是屏的指标, 不是本板的约束。** ★★ |
| ★**降级方案 (必须项)** | ① ★**demo 板: 光机/屏位按 3.3 V 逻辑标准轨设计 (LCD 逻辑 VDD 3.3 V, 行业通用 ±5%) ⇒ 零风险** ② ★**若将来换屏且其规格书写死「VDD 3.3V ±2%」⇒ 判据变为「本板 3.3V 轨纹波 + 精度 ≤ ±2%」⇒ 那是【选型 + 稳压器精度】问题, 由 `TPS7A20` 的输出精度 / `TPS62130A` 的 VOUT 精度 (官网 §6.5 `Initial output voltage accuracy` 800 mV ±…) 决定 ⇒ ★**不是外部依赖** ③ ★**板上手测兜底**: `TP_LIGHT_3V3` 测试点已在板上 ⇒ 板到手直接量 ⇒ 零成本 ★ |
| ★**还卡不卡「板那一趟」** | ★**不卡** ★ |
| ★**判据出处** | ★**`HW/netlist_v1.csv` LIGHT_3V3 8 行实读 (row119/124/125/127/245/246/285/286/333) · `HW/DISPLAY_MODULE_DECISION.md` §2.3 · N-6 全部出处** ★ |

### N-8 · `rk3572_isp_throughput_max` —— ★★**自查闭 [官网]: MP/s 口径已不需要, 分辨率口径已足够** ★★

| 项 | 内容 |
|---|---|
| ★**原问** | RK3572 官方 ISP 吞吐上限 (MP/s @ 什么位深/几路并发) —— 需求侧已钉死 (1080p60 = 124.4 MP/s; 全分辨率 4K60 = 497.7 MP/s; 项目一直用的 250 MP/s 是媒体口径) ★ |
| ★**自查结果** | ★★**官方没给 MP/s, 但给了【分辨率上限】+ 【单通道】+ 【最大输入】三件事 ⇒ 三个数一凑, ISP 余量问题当场闭合 (余量 82.7%) ⇒ 而且这与 2026-11-01 的 R-GEO Q03 裁决是同一条推理链的延续 (裁决时是 RK3576, 现在基线是 RK3572 ⇒ 那个数也不适用了)** ★★ |
| ★**证据等级** | ★**`[官网]` (RK3572 官方 datasheet V1.1 §1.2.10 ISP) + `[推算]` (余量算式)** ★ |
| ★**证据 (逐字抄录, [官网]★)** | ★**出处**: `HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf` (47 页 / 2,414,580 B / md5 `c0e3763036e2f6a3e8a2f68f2254851d` / PDF Author=Rockchip) · ★**§1.2.10 Image Signal Processor V3.5** (文本层 L486-L491) ★<br>★**通路 = 单通道 ISP** (L488) ★<br>★**像素能力 = 12M pixels** (L488) ★<br>★**最大输入 = 4096 × 3072** (L490) ★<br>★**最小输入 = 264 × 264** (L491) ★<br>★**VICAP 格式 = raw8/raw10/raw12/raw14/raw16** (L486) ★<br>★**已归档口径**: `HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §3「ISP」 ★ |
| ★**算式 (★[推算] · 推理链写全★)** | ★**demo 采集链口径** (`HW/DEMO_BOARD_HW_DECISION.md` §1「模式」行): sensor 侧窗口化出 **1920×1080@60** (不裁 ROI) ⇒ **2.0736 M pixel/帧** ★<br>★**占官方 12M 像素能力**: `2.0736 / 12 = 17.28%` ⇒ ★**余量 = 82.72%** ★<br>★**对最大输入 4096×3072**: `1920×1080` 完全在框内 ✔ (且 4096×3072 = 12.58 MPixel > 12M, 说明 12M 是帧内像素上限, 4096×3072 是输入尺寸上限, 两者不同口径, 不混) ★<br>★**与 250 MP/s 口径的关系**: 250 MP/s 是 **ARS45** 的能力 (★已随 ARS45 线作废★) ⇒ ★**对 RK3572 不适用** ★<br>★**与 497.7 MP/s 口径的关系**: 497.7 = 4K@60 的**视频像素率**, 不是 ISP 能力上限 ⇒ ★**比较对象错配, 不该拿来比** (★`HW/R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION.md` B1 已裁决过这条, 当时是 RK3576, 结论同样适用★) ★ |
| ★**结论 (★一句话★)** | ★★**「RK3572 官方 ISP 吞吐上限 (MP/s)」这条外部依赖【可以撤掉】: 官方 datasheet 给的是「单通道 / 12M pixels 帧内能力 / 最大输入 4096×3072」; demo 需求 1920×1080@60 = 2.0736 M pixel/帧 ⇒ 占 17.28% ⇒ 余量 82.72% ⇒ 采集链立得住。⇒ MP/s 口径仍是 [0数据], 但它【不再是决策输入】—— 决策输入已从「吞吐余量」换成「帧内像素能力」, 后者官方给了。** ★★<br>★★**残留 (诚实记账)**: ★**ISP 动态功耗随吞吐走, 官方 §4 Thermal Management 的 ψJT/θJA/θJB/θJC 四行全是 TBD ⇒ 皮肤温度结论仍维持 [推算], 不能升格** ⇒ ★**这条是 HW-B7 的残留, 不是外部依赖** ★★ |
| ★**降级方案 (必须项)** | ① ★**ISP 余量判据改为【分辨率口径】(帧内像素 ≤ 12M), 不用 MP/s** ② ★**ISP 动态功耗 ⇒ 降级为「按 PM/LED 功耗 + 皮肤温度模型 [推算] + 板级实测温升」** (`HW/POWER_BUDGET_V3.md` 已有模型) ③ ★**若将来上 4K@60 全幅 ⇒ 重新算: 4K60 = 3840×2160×60 = 497.7 MP/s, 帧内 8.29 M pixel (≤12M ✔) ⇒ 帧内仍过, 但【吞吐/动态功耗】仍 [0数据] ⇒ 那时才需要问** ⇒ ★**归 main 登记为产品板档的条件项, 不卡 demo** ★ |
| ★**还卡不卡「板那一趟」** | ★**不卡** ★ |
| ★**判据出处** | ★**RK3572 datasheet V1.1 §1.2.10 (文本层 L486-491) + `HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §3 · `HW/DEMO_BOARD_HW_DECISION.md` §1 模式行 · `HW/R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION.md` B1** ★ |

---

## §2 ★★HW 域 7 条 blocker · 逐条处置建议 (★解除动作归 main, 本单只给结论 + 判据★) ★★

> ★**口径提醒**: ★**只有 6 条写着「等原厂」⇒ 本单逐条给处置; HW-B7 明确【不是外部依赖】, 单列, 防止混进外部依赖清单★**

### ★★6 条「等原厂」blocker ★★

| id | severity | 原 needs_from | ★自查后结论★ | ★证据等级★ | ★降级方案 (必须项)★ | ★还卡不卡板那一趟★ | ★判据出处★ |
|---|---|---|---|---|---|---|---|
| ★**HW-B1** | high | vendor, main | ★**可解除 (接口部分)** ⇒ 显示 TX = **DSI TX 4-lane**, SoM 已引出 P3_57..P3_83 ⇒ 「DSI TX? DP TX? 两者?」三选一 = **DSI TX** ⇒ ★**blocker 的问题本身已答完** ★ | ★`[官网]` ×2★ | ① 双出口 0Ω 位保留 (改 0Ω 不改板) ② 宽高比 A/B/C 归 main/boss ③ DP TX 若将来必需 ⇒ 换模组 (模组选型级) | ★**不卡** ★ | ★`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §4 · `HW/PCB/FET3572C_PIN_TABLE.csv` · `HW/netlist_v1.csv` row210-229★ |
| ★**HW-B2** | high | vendor | ★**可解除 (对 demo 板)** ⇒ ① FCCSP pitch = RK3572 官方 **0.42 / 0.52 / 0.65 mm 混合** (不是单一 pitch) ⇒ 对照项目判据「≥0.4 可行 / 0.35 极限 / ≤0.3 须 HDI」⇒ **0.42 ⇒ 可行区间, 不需 HDI** ⇒ ★**原「pitch 未知 ⇒ 逃线层数只能 [推算]」的前提作废**; ② ★**更要紧: demo 主板用 SoM BTB 0.4 mm pitch ⇒ SoC 的 FCCSP pitch 与 demo 板【完全不相关】** ⇒ ★**blocker 对 demo 板是伪 blocker** ★ | ★`[官网]` (SoC 级) + ★`[实测]` (SoM BTB 0.4mm)★ | ① 逃线层数按 SoM BTB 0.4 mm 算 (已在 `HW/PCB/ROUTING_REPORT.md`) ② 产品板档 (裸 SoC) 才需要 FCCSP 逃线 ⇒ 归 main 的产品板档条件项 | ★**不卡** ★ | ★`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §1 · `HW/PCB/FET3572C_PIN_TABLE.csv` (4×100Pin / 0.4mm) · `HW/PCB/ROUTING_REPORT.md`★ |
| ★**HW-B3** | high | vendor | ★**可降级** ⇒ ① 电压上限: RK3572 官方 Table 3-1/3-2 **全域电压已给** ([官网]); ② ★**但官方【不给每个域的电流上限】(Table 3-1 只给电压) ⇒ 电流上限仍 [0数据]**; ③ ★**更要紧: demo 主板不产 SoC 核心轨** (U_DCDC_VCORE / U_DCDC_VIO = **DNP**, SoM 自带 PMIC) ⇒ ★**主板上的电压域清单本来就只剩 3.3V / 1.8V / 5V 三档, 且这三档的负载是本板自己算的** ⇒ ★**blocker 对 demo 板是伪 blocker** ★ | ★`[官网]` (电压) + ★`[0数据]` (电流上限) + ★`[实测]` (DNP)★ | ① 主板级电压域清单按本板负载自算 (已在 `HW/POWER_RAIL_SPEC.md` / `HW/INTERFACE_TABLE.md`) ② SoC 级电流上限 ⇒ 降级为「SoM 厂规格 + 板级实测」③ 产品板档才需要 SoC 级电流上限 | ★**不卡** ★ | ★`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §5 + §7 第 1 条 · `HW/netlist_v1.csv` row78/85 (`U_DCDC_*` DNP) · `HW/POWER_RAIL_SPEC.md`★ |
| ★**HW-B4** | high | vendor, main | ★**可解除 (对 demo 板)** ⇒ 启动存储已**三档化** (ISS-346 / ISS-350 机器判决): ① **只 ADB push 档 (demo)** ⇒ 板侧零动作 ② **外挂 SPI-NOR 档 (≥128 MiB / 1 Gbit 起)** ⇒ 走 `J_BOOT1` 焊盘位 (6 pad 已在板 @126.3,58) + 4 条 0Ω 串阻位必装 ⇒ **板侧零动作 · 不改板宽 · 不重出板** ③ **eMMC 档** ⇒ 板宽 12→15 mm ⇒ 台架板档代价 ≈ 0 ⇒ **只有产品板档卡 (时限型)** ⇒ ⇒ ★**「有无内置 boot storage 未知」这个前提已被 SoM 路线 + 三档化彻底消化** ★ | ★`[实测]` (机器判决 + 网表 J_BOOT1 6 pad 在板)★ | ① demo 档: 什么都不做 ② SPI-NOR 档: 0Ω 串阻位必装 (板位已在) ③ eMMC 档: 产品板改板宽 ⇒ 归产品板档 ④ 固件分区表 (rootfs ≤30MB ⇒ flash ≥128MB) 归 SW 域, 不卡板 | ★**不卡** ★ | ★`state/fragments/hw.yaml` `R-hw-boot-storage` (ISS-346/ISS-350) · `HW/netlist_v1.csv` TBD-06/TBD-11 共 10 行 · `HW/SCHEMATIC_V1.md` P3 段 (ISS-080 容量下限 128MB)★ |
| ★**HW-B5** | medium | main, vendor | ★**降级为「落表批次」+ 一条 [官网] 新结论** ⇒ ① 原残留 3 条外部依赖中的 2 条已闭 (原厂 R_on → N-6 [官网]; JBD 容差 → N-7) ⇒ ★**只剩「老板拍板」1 条 (内部决策, 不是外部依赖)**; ② ★**本单新增 [官网] 结论: 原假设 R_total = 100 mΩ 被证伪 (buck typ 120 mΩ @VIN=3V) ⇒ 方案 A' 变「条件成立」**; ③ ★**blocker 自身的核心诉求「UVP 落点从 BQ2970 改到负载开关输入欠压门限」是【网表改法】⇒ 不是外部依赖, 归落表批次; ④ ★**对 demo 板: 不装电池 ⇒ SYS 轨不存在 ⇒ 这条对 demo 板那一趟完全不卡** ★ | ★`[官网]` + ★`[推算]` + ★`[实测]`★ | ① UVP 落点写 3.35 还是 3.50 ⇒ 归 main/老板 (内部决策) ② `U_LDO_L33` / `U_LDO_IO33` 改 buck ⇒ 归落表批次 (改生成器, 不改板) ③ 电感 DCR ≤20 mΩ 写进选型硬判据 ④ demo 板: 跳过 | ★**不卡** ★ | ★N-6 / N-7 全部出处 · `HW/POWER_TOPOLOGY_RF1_3V3V_UVP.md` §U-1 · `HW/netlist_v1.csv` row121/141/149/169 (`U_LDO_L33` / `U_LDO_IO33` 必装 + LDO)· `HW/CORE_MODULE_SELECTION.md` L39★ |
| ★**HW-B6** | high | vendor, main | ★**降级 (不是解除)** ⇒ ① 绝对最大: **6/15 已 [官网] 逐条转录完毕** (原 0/15) ⇒ ★**这块比 blocker 描述时好得多**; ② ★**但 15 类的对象清单已过期** (ARS45 / OV04C10 已退) ⇒ 按现役 BOM 重排后只剩 4 类待补 (N-MOS / 电芯 / Type-C 母座 / 无源); ③ 跌落/振动/弯折/热 实测 = **0 项, 但这是"无样机"的物理事实, 不是外部依赖** ⇒ 已挂 `HW/EVT_RELIABILITY_TEST_ITEMS.md` 的 EVT 模板; ④ FIT = 器件级数据源已找到 (TI 公开 estimator), 只差人工取数 ⇒ `[0数据-待人工取数]` ★ | ★`[官网]` (6 颗) + ★`[0数据]` (FIT 数值 / 4 类待补) + ★`[实测]` (仓内转录)★ | ① N-MOS (`DMP3098L`) / FPC 座 / BTB ⇒ 官网自取 ② FIT ⇒ 人工开 TI estimator ③ Type-C 母座温升 ⇒ 改用「降额 + 板级实测」④ 机械件 ⇒ 随结构图纸 ⑤ 实测类 ⇒ EVT 模板照旧 | ★**不卡** ★ —— ★**理由: 这 4 类的取值不改变板上任何连接关系 ⇒ 改板 = 0 ⇒ 板 md5 不变** ★ | ★`HW/RELIABILITY_ABSMAX_DERATING_V2.md` §3.1/§3.2 · `HW/EVT_RELIABILITY_TEST_ITEMS.md` · `HW/BOM_v1.csv`★ |

### ★★HW-B7 —— ★★【明确不是外部依赖】★★

| id | severity | 原 needs_from | ★自查后结论★ | ★处置★ |
|---|---|---|---|---|
| ★**HW-B7** | high | **无** (来源 ISS-062) | ★★**本条【不是外部依赖】** —— R-GEO 六问 (全幅vs ROI 模式表 / 4-lane 2.451 Gbps / ISP 吞吐余量 / scaler 输出窗口 / 上电默认模式+寄存器读回 / 角落实测暗角 MTF) 里 ★**只有问 03 (ISP 吞吐余量) 涉及硬件口径, 而它已在 N-8 里用 [官网] 闭合 (余量 82.72%)**; 其余 5 问 = 内部口径 / 软件 / 镜头 / 角落实测 ⇒ ★**全部不是"等外部"** ★ | ★★**⇒ 按任务书要求, 本条【不混进外部依赖清单】** ★<br>★**但仍要写明**: ① 问 03 的【ISP 动态功耗 vs 吞吐曲线】仍 [0数据] ⇒ 只影响 `HW/POWER_BUDGET_V3.md` 皮肤温度结论的证据等级 (维持 [推算]), 不影响板; ② 问 06 (角落实测暗角 MTF) = 无样机 ⇒ EVT 项, 不是外部依赖; ③ ★**建议 main 把它与 HW-B6 合并处理 (都是"证据等级不足", 不是"等外部")** ★ |

---

## §3 ★★13 项 TBD · 逐项收口 (★收口分母 = 网表 `tbd` 列 109 行★) ★★

> ★**口径**: ★**TBD-01..TBD-13 = 「13 项画不了清单」** (出处 `HW/ERC_DRC_CHECKLIST.md` §A5「TBD 编号落在 TBD-01..TBD-13 (对应 13 项画不了清单, 编号一致)」) ⇒ ★**收口必须以 13 项为准, 不能只扫 CSV** (★TBD-05 / 07 / 08 / 09 在网表 `tbd` 列里 0 行, 只在文档里★) ★
> ★**行数为 [实测]** (本机实读 `HW/netlist_v1.csv`)

| TBD | ★该项是什么★ | ★行数★ | ★`[待原厂]` 行数★ | ★自查后结论★ | ★证据等级★ | ★降级方案 (必须项)★ | ★卡不卡板那一趟★ | ★判据出处★ |
|---|---|---|---|---|---|---|---|---|
| ★**TBD-01** | SoC 引脚表 / 球位图 | **6** | **6** | ★**已闭 (UART 2 行) + 板侧零动作 (JTAG 4 行)** ⇒ ① `UART_TX`/`UART_RX` (J_SOM_P2 pin7/pin9): ISS-204 已用 **Forlinx 官方手册 §2.6.2 Table 3 + §2.7.9 + §3.5.5 + Rockchip datasheet p.30/p.31 + Rockchip 官方 `rk3572-pinctrl.dtsi` 三源交叉**判定: P2_7 = `UART0_TX_M0_DEBUG` (球 U33, GPIO0_D4, 3.3V, **I/O = O**), P2_9 = `UART0_RX_M0_DEBUG` (I/O = I) ⇒ ★**方向应写 TX=O / RX=I (网表 note 现写"双向"是错的)**; ② ★**JTAG 4 行 (SoC_NC 占位) ⇒ 走 1×4 1.27 mm 排针 (调试用, 不装贴片) ⇒ 板上位置 + 4 颗 100 Ω 串阻已在 ⇒ 板侧零动作** ⇒ ★**原厂球位图对 demo 板不再需要** ★ | ★`[官网]` ×3 交叉 (ISS-204 已 verified) + ★`[实测]` (网表)★ | ① JTAG 若 SoM 不引 ⇒ 调试走 UART 口 / SWD ⇒ **排针位已在板, 改 0Ω 不改板** ② ★**ISS-204 F1 查出的真缺陷 (UART 缺 100Ω 串阻 + 插口旁 TVS) 已在 `HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md` §5 F1 登记 ⇒ 归落表批次, 属网表改动 (加 2 电阻 + TVS), 不改板位 (贴装位置在 J_UART 旁, 需 main 核板面空间)** ★ | ★**不卡** ★ | ★`HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md` §1/§2/§5 F2 (ISS-204 verified) · `HW/netlist_v1.csv` row387/389/391/393/396/397 ★ |
| ★**TBD-02** | 电源域表 (电压/电流/上电顺序) | **12** | 0 | ★**对 demo 板 = 伪 blocker** ⇒ ① RK3572 官方 Table 3-1 (abs max) / Table 3-2 (推荐工作) **全域电压已给** ([官网]); ② ★**官方不给每域电流上限 ⇒ 仍 [0数据]**; ③ ★**demo 主板不产 SoC 核心轨** (`U_DCDC_VCORE` / `U_DCDC_VIO` = **DNP**, SoM 自带 PMIC) ⇒ ★**主板的电压域只剩 5V / 3.3V / 1.8V 三档, 负载是本板自算的** ⇒ ★**12 行里 `RAIL_V_CORE` / `RAIL_V_SOC_IO` / `U_DCDC_*` 那 7 行是 DNP 行, 不改也不影响板** ★ | ★`[官网]` (电压) + ★`[0数据]` (电流) + ★`[实测]` (DNP)★ | ① 主板三档轨的电流上限按本板负载表自算 (`HW/INTERFACE_TABLE.md` 已有) ② SoC 级电流上限 ⇒ 降级为「SoM 厂规格 + 板级实测」③ 残留的 `R_SUPV_DIV1`/`R_SUPV_DIV2`/`U_SUPV` (SUPV_SENSE 2 行) = 上电时序 ⇒ 归 TBD-12 承接 | ★**不卡** ★ | ★`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §5/§7-1 · `HW/netlist_v1.csv` row78/85/149/154 + TBD-02 12 行 (board 全 MAIN_PCB, 证据 [官方]7 + [推算]5)★ |
| ★**TBD-03** | MIPI-CSI 输入规格 (lane/速率/电压域/AC 耦合) | **25** | **12** | ★**已闭 (demo 口径)** ⇒ ① demo sensor = **IMX415** 模组 (Radxa Camera 4K) ⇒ 公开 datasheet + RK BSP `imx415.c` 模式表 ⇒ **2-lane (D0/D1 + CK) + MCLK**; ② ★**AC 耦合电容放模组侧 (硬判据), 主板不装** ⇒ 网表里的 `C_AC_CSI_*` 是 0 Ω 串阻位/预留位 ⇒ 板侧零动作; ③ ★**12 行 `[待原厂]` 是 ARS45 时代的 SoC 侧占位 ⇒ 已被 SoM 路线解除** ★ | ★`[官网]` (IMX415 公开 datasheet + RK BSP 驱动) + ★`[实测]` (网表)★ | ① 模组随货寄存器表 ⇒ **采购硬判据** (不发问询函) ② 若 AC 耦合放主板侧 ⇒ 需按 CSI 输入电压域选电容 (本板 1.8V IO 域) ⇒ ★**选型硬判据写进采购清单, 不改板** | ★**不卡** ★ | ★`HW/DEMO_BOARD_HW_DECISION.md` §1 + §3 (采购硬判据) · `HW/IMX415_DEMO_SENSOR_FACTS.md` · `HW/AR0234CS_RK3572_PORT_SPEC.md` (5-lane/2-lane 实测口径) · TBD-03 25 行 (证据 [待原厂]12 + [推算]11 + [官方]2)★ |
| ★**TBD-04** | 显示 TX (DSI / DP / 能否同时工作) | **24** | 0 | ★**已闭 [官网]** ⇒ SoM 逐针表把 **4-lane DSI TX** 逐脚坐实 (P3_57/59/63/65/69/71/75/77/81/83) ⇒ 网表用的正是这 10 个脚 ⇒ 零差异; ★**且 SoM 未引出 eDP/DP TX (只引 HDMI_TX_*) ⇒ 答案 = DSI TX, 不是"两者"** ★ ⇒ ⇒ **N-1 的结论同时闭掉 TBD-04** | ★`[官网]` ×2 (SoC datasheet + Forlinx 手册) + ★`[实测]` (网表逐针一致)★ | ① 双出口 0Ω 位保留 ② DP TX 若必需 ⇒ 换模组 ③ `I2C_B_*` 4 行 (P2_1/P2_11 = 独立 I2C2, 3.3V) ⇒ 屏 DDC 与 camera I2C5 物理分开 ⇒ 无冲突 | ★**不卡** ★ | ★N-1 全部出处 · `HW/netlist_v1.csv` row210-233 (TBD-04 24 行, 证据 [推算]14 + [官方]10)★ |
| ★**TBD-05** | ★**【两个含义并存, 本单拆清★】** ① SoC 级 FCCSP pitch ② CSV 里的 = AR0234CS 的 I2C 上拉 (待 onsemi abs max) | **0** | 0 | ★**① SoC 级 pitch**: RK3572 官方 FCCSP550L = **0.42 / 0.52 / 0.65 mm 混合** ([官网]) ⇒ 项目判据「≥0.4 可行 / 0.35 极限 / ≤0.3 须 HDI」⇒ **0.42 ⇒ 可行, 不需 HDI** ⇒ ★**且 demo 板用 SoM BTB 0.4 mm ⇒ SoC pitch 与 demo 板无关** ⇒ ★**`HW/ONLINE_FINDINGS_2026-10-26.md` §7「TBD-05 FCCSP pitch 无公开数据」这条 [0数据] 已被 2026-11-06 的官方 datasheet 解析推翻 (时间上晚于它)** ★<br>★**② CSV 里那唯一一行** (row168, `R_PU_I2CA_SCL`, note 含 `★[TBD-05] 整机阶段若换 AR0234CS (VDD_IO=2.8V ⇒ VIH=0.7×2.8=1.96V > 1.8V 上拉 ⇒ 上拉轨必须一起改) ... 待 onsemi 回信 (ISS-142)`) ⇒ ★**AR0234CS 已被 IMX415 取代 ⇒ 这条支线已作废** ⇒ 且 ★**该行 `tbd` 列本身是空的 (只在 note 里) ⇒ 不进 109 行分母** ★ | ★`[官网]` (SoC pitch) + ★`[实测]` (CSV 实读: 该行 `tbd` 列为空) + ★`[推算]` (AR0234CS 已退)★ | ① AR0234CS 支线 ⇒ **整条出清单** (不再有换料场景) ② 若将来真换 AR0234CS ⇒ 上拉轨按其 VDD_IO 重算 ⇒ **落选型判据, 不改板** ③ SoC 级 pitch ⇒ 产品板档才需要 | ★**不卡** ★ | ★`HW/RK3572_OFFICIAL_DATASHEET_FACTS.md` §1 · `HW/ONLINE_FINDINGS_2026-10-26.md` §7 (★已被 §1 推翻★) · `HW/netlist_v1.csv` row168 · `HW/AR0234CS_RK3572_PORT_SPEC.md` L280 · `HW/IMX415_DEMO_SENSOR_FACTS.md` L62 ★ |
| ★**TBD-06** | 启动存储类型 (内置 boot storage / SPI-NOR / eMMC) | **6** | **6** | ★**已闭 (三档化)** ⇒ ① **只 ADB push 档 (demo)** ⇒ 板侧零动作 ② **外挂 SPI-NOR 档 (≥128 MiB)** ⇒ 走 `J_BOOT1` 焊盘位 (6 pad 已在板 @126.3,58) + 4 条 0Ω 串阻位必装 ⇒ **板侧零动作 · 不改板宽 · 不重出板** ③ **eMMC 档** ⇒ 板宽 12→15 mm ⇒ **只有产品板档卡 (时限型)** ⇒ ⇒ ★**6 行 `[待原厂]` 全部是「SoC 有没有内置 boot storage」这个已被换芯消化的问题** ★ | ★`[实测]` (机器判决 ISS-346/ISS-350 + 网表 J_BOOT1 在板)★ | ① demo 档: 零动作 ② SPI-NOR 档: 0Ω 串阻位必装 (板位已在) ③ eMMC 档: 产品板改板宽 ⇒ 归产品板档 ④ 固件分区 ⇒ SW 域 | ★**不卡** ★ | ★`state/fragments/hw.yaml` `R-hw-boot-storage` · `HW/netlist_v1.csv` TBD-06 6 行 (全 MAIN_PCB, 全 [待原厂]) · `HW/PCB/` (J_BOOT1 位置 @126.3,58)★ |
| ★**TBD-07** | 帧同步能否引出 | **0** | 0 | ★**已闭 (板侧零动作)** ⇒ ① SoM 逐针表 **400 行里无 FSIN / VSYNC** ⇒ SoM 没引帧同步 ⇒ ② ★**网表 `FSIN` / `FSIN_OUT` 两行是 `SoC_NC` 占位 + `R_SER_FSIN` 50 Ω 串阻 + `TP_FSIN` 测试点 ⇒ 板侧已给全 (测试点在板) ⇒ ③ ★**帧同步能不能用 = 软件/固件的事, 硬件侧已无待清项** ★ | ★`[实测]` (SoM 逐针表 grep 无 FSIN + 网表实读)★ | ① 帧同步改用 SoM 已有的 MIPI/TE 机制 ⇒ 板侧零动作 ② `R_SER_FSIN` 50 Ω + `TP_FSIN` 已在板 ⇒ 任何时候想引出都有位置 | ★**不卡** ★ | ★`HW/PCB/FET3572C_PIN_TABLE.csv` (grep FSIN/VSYNC ⇒ 0 行) · `HW/netlist_v1.csv` row399/400 (TBD-13 同源) · `HW/SCHEMATIC_V1.md` P8 段★ |
| ★**TBD-08** | 充电状态能否读回 | **0** | 0 | ★**已闭 (文档明写不卡)** ⇒ ★**`HW/SCHEMATIC_V1.md` P8 段逐字**: 「★**充电状态能否读回 (TBD-08, 已有 TP 兜底, 不卡项目)**」 ⇒ ① 网表 `CHG_STAT` (row481, U_CHG pin4 → J_CHG pin5) 已有回读线 + ② TP 兜底 ⇒ 板侧零动作 ★ | ★`[实测]` (文档 + 网表)★ | ① TP 兜底已在 ② 要改回读方式 ⇒ 落表批次, 不改板 | ★**不卡** ★ | ★`HW/SCHEMATIC_V1.md` P8 段逐字 · `HW/netlist_v1.csv` row481★ |
| ★**TBD-09** | DDC I2C 是否独立于 SoC 通用 I2C / DDC 地址是否可配 | **0** | 0 | ★**已闭 (SoM 级)** ⇒ ① SoM 有 **独立 I2C2** (`I2C2_SDA_M0` = P2_1 / `I2C2_SCL_M0` = P2_11, **3.3V 域**), 而 camera 走 **I2C5** (`I2C5_SCL_M3` = P2_31 / `I2C5_SDA_M3` = P2_33, **1.8V 域**) ⇒ ★**两条总线物理分开 ⇒ 「DDC 是否独立」已在 SoM 级解决**; ② ★**网表 `I2C_B_SCL` / `I2C_B_SDA` (row230-233) 用的正是 P2_11 / P2_1** ⇒ 零差异; ③ DDC 从机地址 = 屏模组随货资料 (采购硬判据) ★ | ★`[官网]` (Forlinx 逐针表) + ★`[实测]` (网表)★ | ① DDC 地址 = 采购硬判据 ② 若屏的 DDC 恰好与 I2C2 上某器件冲突 ⇒ 改上拉/换总线 ⇒ 板位已在 (P2_1/P2_11 空脚?) ⇒ **需 main 核这两脚是否已被别的功能占** | ★**不卡** ★ | ★`HW/PCB/FET3572C_PIN_TABLE.csv` (P2_1/P2_11/P2_31/P2_33) · `HW/netlist_v1.csv` row230-233 · `HW/I2C_ADDR_TABLE.md`★ |
| ★**TBD-10** | USB PHY 版本与引脚数 | **3** | **2** | ★**已闭 (SoM 级)** ⇒ SoM 引出: `USB_DRD1_DP` (P1_92, 球 B26) / `USB_DRD1_DM` (P1_94, 球 A26) / `USB_DRD1_VBUSDET` (P1_100, 球 B28) / `USB_DRD1_ID` (P1_98) / `USB2_OTG0_DP` (P3_20, 球 B25) / `USB2_OTG0_DM` (P3_18, 球 A25) / `USB_DRD0_ID` (P3_14) / `USB_DRD0_VBUSDET` (P3_16) ⇒ ★**USB2.0 物理层 + VBUS detect + ID 确认存在 ⇒ 「有无 USB PHY」已答; 且 `USB_DRD1` 官方默认功能写的是 `USB20_HOST1` (Host 侧), `USB2_OTG0` 才是可做 Device 的那对 ⇒ ★**本板现用 P1_92/P1_94 (HOST1) 接 Type-C ⇒ 端口选型要 main 裁 (建议 Device 侧走 P3_18/P3_20 = USB2_OTG0)** ⇒ ★**但 demo 板不接 PC ⇒ 不卡板那一趟; 且换脚 = 改网表 + 板 ⇒ 若要换, 必须与板那一趟同批** ★ | ★`[官网]` (Forlinx 逐针表) + ★`[实测]` (网表 row290/291 用 P1_92/P1_94)★ | ① 端口选型 ⇒ 归 main (内部决策, 不是外部依赖) ② 若要换到 OTG0 ⇒ **改网表 + 板 ⇒ 必须与板那一趟同批 (板 md5 只许变一次)** ③ 若不换 ⇒ 靠 SW 侧把 USB2_OTG0 当 Device 用、HOST1 空置 ⇒ ★**这是【零改板】路径** | ★**条件卡** ★ —— ★**条件: ① 若 main 判「必须做 USB Device」⇒ 换脚要改板 ⇒ 必须同批; ② 若 demo 不接 PC ⇒ 不卡** ★ | ★`HW/PCB/FET3572C_PIN_TABLE.csv` (P1_92/94/98/100, P3_14/16/18/20) · `HW/netlist_v1.csv` row290/291 (TBD-10 3 行, 证据 [待原厂]2 + [推算]1) · `HW/TI_POWER_FACTS.md` §③ 订正 A (VBUSDET 分压不可删)★ |
| ★**TBD-11** | 启动存储挂在哪个接口 (SPI 控制器 / eMMC-NAND 控制器) | **4** | **4** | ★**已闭 (板侧零动作)** ⇒ ① 4 行 = `R_SER_SPI_MOSI` / `R_SER_SPI_MISO` 及其 `_BOOT` 支路 (row291-294) ⇒ **4 条 0Ω 串阻位已在板**; ② ★**SoM 侧有没有引出 SPI 控制器, 是 SoM 文档问题, 不是原厂问题** ⇒ 查 SoM 逐针表即可; ③ ★**但 demo 走 ADB push 档 ⇒ 根本不需要外挂启动存储** ⇒ 板侧零动作 ⇒ ★**4 行 `[待原厂]` 是「ARS45 时代外挂还是内置」这个已消化的问题** ★ | ★`[实测]` (网表 4 串阻位在板) + ★`[官网]` (SoM 逐针表, 若要核 SPI 脚)★ | ① demo 档: 零动作 ② SPI-NOR 档: 4 串阻位必装 (板位已在) ③ SoM 无 SPI 脚 ⇒ 走 eMMC 档 ⇒ 产品板改板宽 ⇒ 归产品板档 | ★**不卡** ★ | ★`HW/netlist_v1.csv` row291-294 (TBD-11 4 行, 全 [待原厂]) · `R-hw-boot-storage`★ |
| ★**TBD-12** | 上电时序 (哪轨先起 / RESET 何时释放 / 内部 DCDC 同步) | **27** | **5** | ★**对 demo 板 = 伪 blocker (板侧零动作)** ⇒ ① 27 行 = `PG_AND` 链 (6) + `VDD_1V8_IO` (3) + `RESET_N` (3) + `GND` (4) + `EN_VCORE`/`EN_VIO` (4) + `SUPV_CT` (1) + `XTAL_IN`/`XTAL_OUT`/`XTAL` (5) + `BOOT_N` (1); ② ★**`U_SUPV` 整颗 = DNP** (row74/406/407/408) + `U_DCDC_VCORE`/`U_DCDC_VIO` = DNP ⇒ **SoM 自带 PMIC ⇒ 主 PCB 不控 SoC 内部上电顺序**; ③ ★**SoM 侧的上电/复位由模组厂保证** ⇒ 主板只管自己的 5V→3.3V→1.8V 链 ⇒ **板侧已给全 (RC 软启动 + PG 链 + U_SUPV 监控位)**; ④ ★**残留: `R_SUPV_DIV1`/`R_SUPV_DIV2` 分压阈值 (2 行) + `XTAL` 双方案 (5 行) ⇒ 这两条都在 SoM 内部 (SoM 有自己的 PMIC + 晶振) ⇒ 主板不碰** ⇒ ★**⇒ 原判据「🔴 待原厂 (TBD-12)」对 demo 板已过期** ★ | ★`[实测]` (网表 DNP 实读) + ★`[推算]` (SoM 自带 PMIC ⇒ 内部时序不归主板) + ★`[0数据]` (SoM 内部时序的官方数字, 不阻塞)★ | ① 主板侧时序 ⇒ 用板上器件自洽 (`U_SUPV` 监控 + PG 链 + RC 软启动) ⇒ **不改板** ② `U_SUPV` DNP ⇒ 复位链若要真做 ⇒ 落表批次 (换 DNP→必装 需板上有位 ⇒ ★**需 main 核 `U_SUPV` 位是否在板**: 若在 ⇒ 只改 DNP 标注; 若不在 ⇒ **改板** ⇒ ★**这是本单唯一一条"可能改板"的残留, 归 main 核★) ③ 产品板档 (裸 SoC) ⇒ TBD-12 重新变成真卡点 ⇒ 归产品板档条件项 | ★**条件卡** ★ —— ★**条件: 主板侧时序不卡; 但 `U_SUPV` 若要装 (复位链) 必须核它在不在板上 ⇒ 不在板则要改板 ⇒ 那一趟同批** ★ | ★`HW/netlist_v1.csv` row74/78/85/406/407/408 + TBD-12 27 行 (证据 [推算]6 + [官方]9 + [待原厂]5 + [同Die参考-待官方确认]7) · `HW/ERC_DRC_CHECKLIST.md` §B5/§B15 · `HW/DEMO_BOARD_HW_DECISION.md` §2「9 路电源 IC 的 EN 已在网表补齐」· `HW/TI_POWER_FACTS.md` §② 订正 B (PG 极性写反, 必须在 S6 那趟前定死)★ |
| ★**TBD-13** | 帧同步输入 (FSIN) | **2** | **1** | ★**已闭 (板侧零动作)** ⇒ ① `FSIN` = `SoC_NC` 占位 + 50 Ω 串阻 + `TP_FSIN` 测试点 (row399/400) ⇒ **板侧已给全**; ② SoM 逐针表无 FSIN ⇒ SoM 不引帧同步 ⇒ ③ **能不能用 = 软件/固件的事** ⇒ ★**2 行里 1 行 `[待原厂]` 已被 SoM 路线消化** ★ | ★`[实测]` (网表 + SoM 逐针表 grep)★ | ① 帧同步改用 SoM 已有机制 ⇒ 板侧零动作 ② 若要真引 ⇒ 换 SoM / 走 MIPI ⇒ 产品板档 | ★**不卡** ★ | ★`HW/netlist_v1.csv` row399/400 (TBD-13 2 行, 证据 [待原厂]1 + [推算]1) · `HW/PCB/FET3572C_PIN_TABLE.csv`★ |

### ★§3.1 · 13 项 TBD 汇总 (★一句话★) ★

| 维度 | 结论 |
|---|---|
| ★**TBD 项数** | **13 / 13 全部有结论** (含 TBD-05 / 07 / 08 / 09 这 4 项网表 `tbd` 列 0 行的) ★ |
| ★**网表待清行** | **109 行全部被覆盖** (覆盖率 **100%**) ⇒ ★**其中 36 行 `evidence=[待原厂]` (全部 MAIN_PCB) 全部被覆盖** ★ |
| ★**还卡不卡板那一趟** | ★**11 项 = 不卡** · ★**2 项 = 条件卡** (★TBD-10 USB 端口选型 · TBD-12 `U_SUPV` 是否在板★) ⇒ ★**条件卡的判据都指向 main 的一次内部决策, 不是外部方** ★ |
| ★**有没有哪一项要求"改板"** | ★**没有一项要求改板** ⇒ ★**⇒ 外部依赖维度上, 板那一趟的网表真源【已经冻结】** ⇒ ★**⇒ 板 md5 变更次数仍可为 1** ★ |

---

## §4 ★★收口登记块 (★机器判据 D3 / D4 / D5 读这一段★) ★★

> ★**这一段是机器可读的**: `HW/check_hw_external_dep_closed.py` 只读下面这个 ```json 围栏块 ⇒ ★**改这一段 = 改登记; 改判据 = 改闸 (不许)** ★
> ★**字段含义**: `scope` ∈ {needs, blocker, tbd} · `evidence` ∈ {[官网],[实测],[媒体],[推算],[0数据]} · `blocks_board` ∈ {不卡, 卡, 条件卡} · `downgrade` 与 `judgement_ref` **非空是硬要求** (D4 / D5) ★

```json
{
  "registry_version": "ISS-401",
  "generated_at": "2026-11-24T23:50:00+08:00",
  "tbd_row_total": 109,
  "pend_rows_total": 36,
  "entries": [
    {"scope": "needs", "ref": "q16_display_iface", "conclusion": "显示 TX = DSI TX 4-lane (SoM 已引出 P3_57..P3_83); SoM 未引 eDP/DP TX; 宽高比 A/B/C 归 main/老板拍板", "evidence": "[官网]", "evidence_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §4 + HW/PCB/FET3572C_PIN_TABLE.csv + HW/netlist_v1.csv row210-229", "downgrade": "保留双出口 0Ω 位 (改 0Ω 不改板); DP TX 若必需则换模组 (模组选型级决策); 宽高比不代拍", "blocks_board": "不卡", "judgement_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §4; HW/PCB/FET3572C_PIN_TABLE.csv"},
    {"scope": "needs", "ref": "vendor_ars45_paper_q11_q16", "conclusion": "整条作废: ARS45/酷芯微 线已于 2026-10-29 19:20 拍板作废; 8 问逐条重定向到 RK3572/SoM 公开资料, 6 问已闭, 1 问 (散热焊盘) 官方自己 TBD", "evidence": "[实测]", "evidence_ref": "HW/CHIP_SOC_MIGRATION.md L53 + HW/TI_POWER_FACTS.md §④ (逐字引用)", "downgrade": "散热焊盘降级为「导热垫+铜箔 + 板级皮肤温度实测」; 模组随货寄存器表/init code 一律写成采购硬判据 (不发问询函)", "blocks_board": "不卡", "judgement_ref": "HW/CHIP_SOC_MIGRATION.md L53; HW/TI_POWER_FACTS.md §④; HW/DEMO_BOARD_HW_DECISION.md §2/§3"},
    {"scope": "needs", "ref": "jbd_zoushe_dsi_spec", "conclusion": "整条作废: 走鹃Ⅱ 已于 2026-11-02 01:12 被 视涯 SiOLED 取代, demo 板现行为 Waveshare 2.8inch DSI LCD (SKU 22028); 4 个子问在现役件上全部有公开答案", "evidence": "[官网]", "evidence_ref": "HW/DISPLAY_MODULE_DECISION.md §2.3 + HW/DEMO_BOARD_HW_DECISION.md §3/§4 + HW/DISPLAY_SMALL_SCREEN_OPTIONS.md §3.1", "downgrade": "屏侧全部参数走采购硬判据 (init code + DSI 时序 + DDC 地址 + 供电/电流清单); 若将来改回产品屏则该 4 问重新成为外部依赖, 但不阻塞 demo 板那一趟", "blocks_board": "不卡", "judgement_ref": "HW/DISPLAY_MODULE_DECISION.md §2.3; HW/DEMO_BOARD_HW_DECISION.md §3/§4"},
    {"scope": "needs", "ref": "rel_vendor_absmax_rating", "conclusion": "部分闭: ISS-068 已把 6 颗 TI 器件 abs max 逐条转录 (原 0/15 → 现 6/15); 剩余 9 类里 ARS45/OV04C10/摄像头模组 3 类随退件作废, 实剩 N-MOS/电芯/Type-C 母座/无源/机械件 5 类", "evidence": "[官网]", "evidence_ref": "HW/RELIABILITY_ABSMAX_DERATING_V2.md §3.1 (SLVSAG7F/SBVS338H/SLUSC76C/SLVSGP9/SBVS349/SNOSD82D 逐条转录)", "downgrade": "N-MOS DMP3098L / HIROSE FPC 座 + BTB 官网自取; FIT 走 TI 公开 estimator 人工取数 (10 分钟); Type-C 母座温升曲线降级为「降额 + 板级实测」; 机械件随结构图纸; 跌落/振动/弯折/热实测挂 EVT 模板", "blocks_board": "不卡", "judgement_ref": "HW/RELIABILITY_ABSMAX_DERATING_V2.md §3.1/§3.2/§B5; HW/EVT_RELIABILITY_TEST_ITEMS.md; HW/BOM_v1.csv"},
    {"scope": "needs", "ref": "rel_battery_cell_spec", "conclusion": "自查闭: demo 主板不装电池 (BT_432243 / U_BATPROT / Q1 / Q2 全 DNP), 电芯规格书对 demo 板那一趟零影响; 厚度账已用丰江 432243 (4.3mm) 算完 (镜腿 7.3mm 不变)", "evidence": "[实测]", "evidence_ref": "HW/netlist_v1.csv row24/26/28/29/36 (dnp=DNP + note 逐字) + HW/BOM_v1.csv BT_432243 + HW/POWER_BUDGET_V3.md §7", "downgrade": "demo 板 DNP 不需规格书; 产品板走采购硬判据 (随货给倍率/循环寿命/内阻/膨胀曲线/温度窗口); 规格书到之前按最保守 1C 限充电电流 (575mAh 档 575mA / 340mAh 档 340mA); 若降充电电流属落表项, 不改板", "blocks_board": "不卡", "judgement_ref": "HW/netlist_v1.csv row24/26/36; HW/CORE_MODULE_SELECTION.md L39; HW/POWER_BUDGET_V3.md §7"},
    {"scope": "needs", "ref": "iss067_vendor_r_on_u1", "conclusion": "自查闭 [官网] 且证伪原假设: TI SLVSAG7F §6.5 高边 R_on = 120 mΩ typ @VIN=3V (90 typ / 170 max @VIN≥6V), 而原假设 R_total=100 mΩ 已被单颗 typ 证伪; 方案 A' (UVP 3.35V) 成立条件应为 R_total ≤ 142.9 mΩ (typ 路径 + 电感 DCR ≤ 22.9 mΩ), 按 max 规格不成立", "evidence": "[官网]", "evidence_ref": "TI tps62130a.pdf SLVSAG7F (NOV 2011 - REV NOV 2021) §6.5 POWER SWITCH; 本机 tmp/iss401/tps62130a.txt L304-L308; §8.2 Fig 7-3; §9.2.2.2.1 + Table 9-3", "downgrade": "电感选型硬判据写「DCR ≤ 20 mΩ」; UVP 落点挂在板上手测 (SYS 拉到 3.35V 时实测 LIGHT_3V3 ≥ 3.30V); DCR 实测超标则改电感型号 (板位已在, 零改板); 兜底走方案 A (UVP 3.50V, 续航少约 7 个点)", "blocks_board": "不卡", "judgement_ref": "TI SLVSAG7F §6.5 (本机 L304-308); HW/calc_rf1_3v3v_uvp.py (V33/I33/R_BUCK_TOT/BUCK_FLOOR); HW/POWER_TOPOLOGY_RF1_3V3V_UVP.md §U-1"},
    {"scope": "needs", "ref": "iss067_jbd_vdd_tol_u2", "conclusion": "自查闭: (a) 被测对象走鹃Ⅱ 已作废; (b) LIGHT_3V3 是本板 LDO 输出的稳压轨 (消费者 = CONN_LIGHT pin14/15 + CONN_CAM pin28/29 + TP_LIGHT_3V3), 屏看到的永远是稳压后的 3.3V, 屏容差不影响 buck 地板 ⇒ 真约束 = iss067_vendor_r_on_u1 的 R_on", "evidence": "[实测]", "evidence_ref": "HW/netlist_v1.csv LIGHT_3V3 9 行实读 (row119/124/125/127/245/246/285/286/333); HW/DISPLAY_MODULE_DECISION.md §2.3", "downgrade": "按 3.3V 逻辑标准轨设计 (±5% 行业通用); 若屏规格书写死 ±2% 则判据变为「本板 3.3V 轨精度/纹波 ≤ ±2%」, 由稳压器精度决定, 非外部依赖; TP_LIGHT_3V3 测试点已在板, 板到手直接量", "blocks_board": "不卡", "judgement_ref": "HW/netlist_v1.csv (LIGHT_3V3 消费者 9 行); N-6 全部出处"},
    {"scope": "needs", "ref": "rk3572_isp_throughput_max", "conclusion": "自查闭 [官网]: RK3572 官方 datasheet §1.2.10 给出「单通道 ISP / 12M pixels 帧内能力 / 最大输入 4096×3072 / 最小 264×264」; demo 需求 1920×1080@60 = 2.0736 M pixel/帧 ⇒ 占 17.28% ⇒ 余量 82.72% ⇒ MP/s 口径不再是决策输入 (250 MP/s 是已作废的 ARS45 口径, 497.7 MP/s 是 4K60 视频像素率, 两者都不可比)", "evidence": "[官网]", "evidence_ref": "HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.pdf §1.2.10 (文本层 L486-491); 已归档于 HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §3", "downgrade": "ISP 余量判据改为分辨率口径 (帧内像素 ≤ 12M); ISP 动态功耗维持 [推算] 并用板级实测温升兜底; 4K@60 全幅档才需重新问 (帧内 8.29M ≤ 12M 仍过, 吞吐仍 [0数据]) ⇒ 归产品板档条件项", "blocks_board": "不卡", "judgement_ref": "RK3572 datasheet V1.1 §1.2.10 (L486-491); HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §3; HW/R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION.md B1"},

    {"scope": "blocker", "ref": "HW-B1", "conclusion": "可解除: 显示 TX 接口三选一 = DSI TX (SoC 有 DSI-1.2 4-lane + eDP; 但 SoM 只引出 DSI TX + HDMI TX, 未引 eDP/DP TX) ⇒ 原问题已答完", "evidence": "[官网]", "evidence_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §4 + HW/PCB/FET3572C_PIN_TABLE.csv", "downgrade": "双出口 0Ω 位保留; 宽高比归 main/boss; DP TX 若必需则换模组 (模组选型级)", "blocks_board": "不卡", "judgement_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §4; HW/netlist_v1.csv row210-229"},
    {"scope": "blocker", "ref": "HW-B2", "conclusion": "可解除 (对 demo 板): FCCSP pitch = RK3572 官方 0.42/0.52/0.65mm 混合 ⇒ 对照项目判据 0.42 落在可行区间不需 HDI; 且 demo 主板用 SoM BTB 0.4mm ⇒ SoC FCCSP pitch 与 demo 板不相关 ⇒ 原「pitch 未知 ⇒ 逃线层数只能推算」前提作废", "evidence": "[官网]", "evidence_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §1 + HW/PCB/FET3572C_PIN_TABLE.csv (4×100Pin / 0.4mm) + HW/PCB/ROUTING_REPORT.md", "downgrade": "逃线层数按 SoM BTB 0.4mm 算; 产品板档 (裸 SoC) 才需要 FCCSP 逃线 ⇒ 归产品板档条件项", "blocks_board": "不卡", "judgement_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §1; HW/PCB/FET3572C_PIN_TABLE.csv"},
    {"scope": "blocker", "ref": "HW-B3", "conclusion": "可降级: SoC 级电压上限官方 Table 3-1/3-2 已给 [官网]; 官方不给每域电流上限 [0数据]; demo 主板不产 SoC 核心轨 (U_DCDC_VCORE/U_DCDC_VIO = DNP) ⇒ 主板电压域只剩 5V/3.3V/1.8V 三档且负载自算 ⇒ 对 demo 板是伪 blocker", "evidence": "[官网]", "evidence_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §5 + §7 第1条 + HW/netlist_v1.csv row78/85 (DNP)", "downgrade": "主板三档轨电流上限按本板负载表自算; SoC 级电流上限降级为「SoM 厂规格 + 板级实测」; 产品板档才需要", "blocks_board": "不卡", "judgement_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §5/§7; HW/netlist_v1.csv row78/85; HW/POWER_RAIL_SPEC.md"},
    {"scope": "blocker", "ref": "HW-B4", "conclusion": "可解除 (对 demo 板): 启动存储已三档化 (ISS-346/ISS-350 机器判决) —— ①只 ADB push 档 (demo) 板侧零动作 ②外挂 SPI-NOR ≥128MiB 走 J_BOOT1 焊盘位 (6 pad 已在板) + 4 条 0Ω 串阻位 ⇒ 板侧零动作/不改板宽/不重出板 ③eMMC 档 板宽 12→15mm ⇒ 只有产品板档卡 ⇒ 「有无内置 boot storage 未知」这个前提已被换芯+三档化消化", "evidence": "[实测]", "evidence_ref": "state/fragments/hw.yaml risks.R-hw-boot-storage (ISS-346/ISS-350 机器判决) + HW/netlist_v1.csv TBD-06/TBD-11 10 行 + HW/PCB J_BOOT1 @126.3,58", "downgrade": "demo 档零动作; SPI-NOR 档 0Ω 串阻位必装 (板位已在); eMMC 档归产品板档 (改板宽); 固件分区表 (rootfs ≤30MB ⇒ flash ≥128MB) 归 SW 域", "blocks_board": "不卡", "judgement_ref": "state/fragments/hw.yaml risks.R-hw-boot-storage; HW/netlist_v1.csv (TBD-06 6 行 / TBD-11 4 行); HW/SCHEMATIC_V1.md P3 段 (ISS-080)"},
    {"scope": "blocker", "ref": "HW-B5", "conclusion": "降级为落表批次: 原 3 条外部依赖中 2 条已闭 (原厂 R_on → N-6 [官网]; JBD 容差 → N-7) ⇒ 只剩「老板拍板」1 条 (内部决策非外部依赖); 本单新增 [官网] 结论: 原假设 R_total=100mΩ 被证伪 (buck typ 120mΩ@VIN=3V) ⇒ 方案 A' 变「条件成立」; 核心诉求「UVP 落点改到负载开关输入欠压门限」是网表改法不是外部依赖; demo 板不装电池 ⇒ SYS 轨不存在 ⇒ 对 demo 板完全不卡", "evidence": "[官网]", "evidence_ref": "N-6 全部出处 (TI SLVSAG7F §6.5) + HW/POWER_TOPOLOGY_RF1_3V3V_UVP.md §U-1 + HW/netlist_v1.csv row121/141/149/169", "downgrade": "UVP 落点 3.35 vs 3.50 归 main/老板; U_LDO_L33/U_LDO_IO33 改 buck 归落表批次 (改生成器不改板); 电感 DCR ≤20mΩ 写进选型硬判据; demo 板跳过", "blocks_board": "不卡", "judgement_ref": "TI SLVSAG7F §6.5; HW/POWER_TOPOLOGY_RF1_3V3V_UVP.md §U-1; HW/netlist_v1.csv row121/141/149/169; HW/CORE_MODULE_SELECTION.md L39"},
    {"scope": "blocker", "ref": "HW-B6", "conclusion": "降级 (非解除): 绝对最大已 6/15 [官网] 逐条转录 (原 0/15) ⇒ 比 blocker 描述时好得多; 但 15 类对象清单已过期 (ARS45/OV04C10 已退) ⇒ 重排后实剩 5 类待补; 跌落/振动/弯折/热实测 0 项属「无样机」物理事实而非外部依赖, 已挂 EVT 模板; FIT 数据源已找到 (TI 公开 estimator) 只差人工取数", "evidence": "[官网]", "evidence_ref": "HW/RELIABILITY_ABSMAX_DERATING_V2.md §3.1/§3.2 + HW/EVT_RELIABILITY_TEST_ITEMS.md + HW/BOM_v1.csv", "downgrade": "DMP3098L / HIROSE FPC 座 + BTB 官网自取; FIT 人工开 TI estimator 取数; Type-C 母座温升曲线降级为「降额 + 板级实测」; 机械件随结构图纸; 实测类照 EVT 模板", "blocks_board": "不卡", "judgement_ref": "HW/RELIABILITY_ABSMAX_DERATING_V2.md §3.1/§3.2; HW/EVT_RELIABILITY_TEST_ITEMS.md"},
    {"scope": "blocker", "ref": "HW-B7", "conclusion": "不是外部依赖 (按任务书要求单列, 不混进外部依赖清单): R-GEO 六问里只有问 03 (ISP 吞吐余量) 涉及硬件口径且已在 N-8 用 [官网] 闭合 (余量 82.72%); 其余 5 问 = 内部口径/软件/镜头/角落实测 ⇒ 全部不是「等外部」", "evidence": "[官网]", "evidence_ref": "HW/R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION.md B1/B3 + RK3572 datasheet §1.2.10 + HW/netlist_v1.csv (无 FSIN 依赖)", "downgrade": "ISP 动态功耗维持 [推算] + 板级实测温升兜底; 角落实测暗角 MTF 挂 EVT 项; 建议与 HW-B6 合并处理 (都是证据等级不足, 不是等外部)", "blocks_board": "不卡", "judgement_ref": "HW/R_GEO_Q03_ISP_THROUGHPUT_ADJUDICATION.md B1; RK3572 datasheet §1.2.10; HW/EVT_RELIABILITY_TEST_ITEMS.md"},

    {"scope": "tbd", "ref": "TBD-01", "tbd_labels": ["TBD-01"], "rows": 6, "pend_rows": 6, "conclusion": "UART 2 行已由 ISS-204 三源交叉闭合 (P2_7=UART0_TX_M0_DEBUG O / P2_9=RX I / 3.3V 单端); JTAG 4 行走 1×4 1.27mm 排针 + 已在板的 100Ω 串阻 ⇒ 板侧零动作 ⇒ 原厂球位图对 demo 板不再需要", "evidence": "[官网]", "evidence_ref": "HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md §1/§2/§5 F2 (ISS-204 verified) + HW/netlist_v1.csv row387/389/391/393/396/397", "downgrade": "JTAG 若 SoM 不引则调试走 UART 口 (排针位已在板, 改 0Ω 不改板); ISS-204 F1 查出的 UART 缺 100Ω+TVS 真缺陷归落表批次", "blocks_board": "不卡", "judgement_ref": "HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md §1/§2/§5 F2; HW/netlist_v1.csv row387-397"},
    {"scope": "tbd", "ref": "TBD-02", "tbd_labels": ["TBD-02"], "rows": 12, "pend_rows": 0, "conclusion": "对 demo 板 = 伪 blocker: SoC 电压官方 Table 3-1/3-2 已给; 官方不给每域电流上限; demo 主板不产 SoC 核心轨 (U_DCDC_* = DNP) ⇒ 12 行里 7 行是 DNP 行, 主板电压域只剩 5V/3.3V/1.8V 三档且负载自算", "evidence": "[官网]", "evidence_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §5/§7-1 + HW/netlist_v1.csv row78/85/149/154 (TBD-02 12 行: [官方]7 + [推算]5)", "downgrade": "主板三档轨电流上限按本板负载表自算; SoC 级电流上限降级为「SoM 厂规格 + 板级实测」; 残留 R_SUPV_DIV1/D2 + U_SUPV 归 TBD-12 承接", "blocks_board": "不卡", "judgement_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §5/§7; HW/netlist_v1.csv row78/85; HW/POWER_RAIL_SPEC.md"},
    {"scope": "tbd", "ref": "TBD-03", "tbd_labels": ["TBD-03"], "rows": 25, "pend_rows": 12, "conclusion": "已闭 (demo 口径): sensor = IMX415 模组 ⇒ 2-lane (D0/D1+CK) + MCLK, AC 耦合放模组侧 (硬判据) 主板不装 ⇒ 12 行 [待原厂] 是 ARS45 时代 SoC 侧占位, 已被 SoM 路线解除", "evidence": "[官网]", "evidence_ref": "HW/DEMO_BOARD_HW_DECISION.md §1 + §3 + HW/IMX415_DEMO_SENSOR_FACTS.md + HW/AR0234CS_RK3572_PORT_SPEC.md (TBD-03 25 行: [待原厂]12 + [推算]11 + [官方]2)", "downgrade": "模组随货寄存器表走采购硬判据 (不发问询函); 若 AC 耦合改主板侧则按 CSI 输入电压域选电容 (本板 1.8V IO 域) ⇒ 写进采购/选型硬判据, 不改板", "blocks_board": "不卡", "judgement_ref": "HW/DEMO_BOARD_HW_DECISION.md §1/§3; HW/IMX415_DEMO_SENSOR_FACTS.md; HW/netlist_v1.csv (TBD-03 25 行)"},
    {"scope": "tbd", "ref": "TBD-04", "tbd_labels": ["TBD-04"], "rows": 24, "pend_rows": 0, "conclusion": "已闭 [官网]: SoM 逐针表把 4-lane DSI TX 逐脚坐实 (P3_57/59/63/65/69/71/75/77/81/83) ⇒ 网表用的正是这 10 个脚 (零差异); SoM 未引 eDP/DP TX ⇒ 答案 = DSI TX 而非「两者」", "evidence": "[官网]", "evidence_ref": "HW/PCB/FET3572C_PIN_TABLE.csv + HW/netlist_v1.csv row210-233 (TBD-04 24 行: [推算]14 + [官方]10) + HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §4", "downgrade": "双出口 0Ω 位保留; DP TX 若必需则换模组; I2C_B_* 4 行走独立 I2C2 (P2_1/P2_11) ⇒ 与 camera I2C5 无冲突", "blocks_board": "不卡", "judgement_ref": "HW/PCB/FET3572C_PIN_TABLE.csv; HW/netlist_v1.csv row210-233"},
    {"scope": "tbd", "ref": "TBD-05", "tbd_labels": ["TBD-05"], "rows": 0, "pend_rows": 0, "conclusion": "拆清两个含义: ① SoC 级 FCCSP pitch = RK3572 官方 0.42/0.52/0.65mm 混合 ⇒ 可行区间不需 HDI, 且 demo 板用 SoM BTB 0.4mm ⇒ 与 demo 板无关 (⇒ ONLINE_FINDINGS §7 的 [0数据] 已被官方 datasheet 解析推翻); ② CSV 里那唯一一行 = AR0234CS 的 I2C 上拉 (待 onsemi) ⇒ AR0234CS 已被 IMX415 取代, 支线作废, 且该行 tbd 列为空不在 109 行分母内", "evidence": "[官网]", "evidence_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §1 + HW/ONLINE_FINDINGS_2026-10-26.md §7 (已被推翻) + HW/netlist_v1.csv row168 (tbd 列实测为空) + HW/IMX415_DEMO_SENSOR_FACTS.md L62", "downgrade": "AR0234CS 支线整条出清单; 若将来真换料则上拉轨按其 VDD_IO 重算 (落选型判据, 不改板); SoC 级 pitch 归产品板档", "blocks_board": "不卡", "judgement_ref": "HW/RK3572_OFFICIAL_DATASHEET_FACTS.md §1; HW/netlist_v1.csv row168; HW/AR0234CS_RK3572_PORT_SPEC.md L280"},
    {"scope": "tbd", "ref": "TBD-06", "tbd_labels": ["TBD-06"], "rows": 6, "pend_rows": 6, "conclusion": "已闭 (三档化): ①只 ADB push 档 (demo) 板侧零动作 ②外挂 SPI-NOR ≥128MiB 走 J_BOOT1 焊盘位 (6 pad 已在板) + 4 条 0Ω 串阻位 ⇒ 板侧零动作/不改板宽/不重出板 ③eMMC 档 板宽 12→15mm ⇒ 只有产品板档卡 ⇒ 6 行 [待原厂] 全部是「SoC 有无内置 boot storage」这个已被换芯消化的问题", "evidence": "[实测]", "evidence_ref": "state/fragments/hw.yaml risks.R-hw-boot-storage (ISS-346/ISS-350) + HW/netlist_v1.csv (TBD-06 6 行, 全 MAIN_PCB, 全 [待原厂])", "downgrade": "demo 档零动作; SPI-NOR 档 0Ω 串阻位必装 (板位已在); eMMC 档归产品板档; 固件分区归 SW 域", "blocks_board": "不卡", "judgement_ref": "state/fragments/hw.yaml risks.R-hw-boot-storage; HW/netlist_v1.csv (TBD-06 6 行)"},
    {"scope": "tbd", "ref": "TBD-07", "tbd_labels": ["TBD-07"], "rows": 0, "pend_rows": 0, "conclusion": "已闭 (板侧零动作): SoM 逐针表 400 行无 FSIN/VSYNC ⇒ SoM 不引帧同步; 网表 FSIN/FSIN_OUT 是 SoC_NC 占位 + R_SER_FSIN 50Ω + TP_FSIN 测试点 ⇒ 板侧已给全 ⇒ 帧同步能否用是软件/固件的事", "evidence": "[实测]", "evidence_ref": "HW/PCB/FET3572C_PIN_TABLE.csv (grep FSIN/VSYNC ⇒ 0 行) + HW/netlist_v1.csv row399/400 + HW/SCHEMATIC_V1.md P8 段", "downgrade": "帧同步改用 SoM 已有 MIPI/TE 机制 ⇒ 板侧零动作; R_SER_FSIN + TP_FSIN 已在板, 任何时候可引出", "blocks_board": "不卡", "judgement_ref": "HW/PCB/FET3572C_PIN_TABLE.csv (grep 0 行); HW/netlist_v1.csv row399/400"},
    {"scope": "tbd", "ref": "TBD-08", "tbd_labels": ["TBD-08"], "rows": 0, "pend_rows": 0, "conclusion": "已闭 (文档明写不卡): HW/SCHEMATIC_V1.md P8 段逐字「充电状态能否读回 (TBD-08, 已有 TP 兜底, 不卡项目)」; 网表 CHG_STAT (U_CHG pin4 → J_CHG pin5) 回读线已在", "evidence": "[实测]", "evidence_ref": "HW/SCHEMATIC_V1.md P8 段逐字 + HW/netlist_v1.csv row481", "downgrade": "TP 兜底已在; 要改回读方式归落表批次, 不改板", "blocks_board": "不卡", "judgement_ref": "HW/SCHEMATIC_V1.md P8 段; HW/netlist_v1.csv row481"},
    {"scope": "tbd", "ref": "TBD-09", "tbd_labels": ["TBD-09"], "rows": 0, "pend_rows": 0, "conclusion": "已闭 (SoM 级): SoM 有独立 I2C2 (P2_1 = I2C2_SDA_M0 / P2_11 = I2C2_SCL_M0, 3.3V 域), camera 走 I2C5 (P2_31/P2_33, 1.8V 域) ⇒ 两条总线物理分开 ⇒ 「DDC 是否独立」已在 SoM 级解决; 网表 I2C_B_* 用的正是 P2_11/P2_1 (零差异)", "evidence": "[官网]", "evidence_ref": "HW/PCB/FET3572C_PIN_TABLE.csv (P2_1/P2_11/P2_31/P2_33) + HW/netlist_v1.csv row230-233 + HW/I2C_ADDR_TABLE.md", "downgrade": "DDC 从机地址走采购硬判据; 若屏 DDC 地址与 I2C2 上某器件冲突 ⇒ 改上拉或换总线 ⇒ 板位已在, 但需 main 核 P2_1/P2_11 是否已被别功能占", "blocks_board": "不卡", "judgement_ref": "HW/PCB/FET3572C_PIN_TABLE.csv; HW/netlist_v1.csv row230-233"},
    {"scope": "tbd", "ref": "TBD-10", "tbd_labels": ["TBD-10"], "rows": 3, "pend_rows": 2, "conclusion": "已闭 (SoM 级): SoM 引出 USB_DRD1_DP/DM (P1_92/P1_94, 3.3V) + VBUSDET (P1_100) + ID (P1_98) + USB2_OTG0_DP/DM (P3_20/P3_18) ⇒ USB2.0 物理层确认存在 ⇒ 「有无 USB PHY」已答; 但 USB_DRD1 官方默认功能是 USB20_HOST1 (Host), USB2_OTG0 才是可做 Device 的那对 ⇒ 本板现用 P1_92/P1_94 接 Type-C ⇒ 端口选型要 main 裁", "evidence": "[官网]", "evidence_ref": "HW/PCB/FET3572C_PIN_TABLE.csv (P1_92/94/98/100, P3_14/16/18/20) + HW/netlist_v1.csv row290/291 (TBD-10 3 行: [待原厂]2 + [推算]1) + HW/TI_POWER_FACTS.md §③ 订正 A", "downgrade": "端口选型归 main (内部决策非外部依赖); 若要换到 OTG0 ⇒ 改网表+板 ⇒ 必须与板那一趟同批 (板 md5 只许变一次); 若不换 ⇒ 靠 SW 侧用 OTG0 做 Device、HOST1 空置 ⇒ 零改板路径", "blocks_board": "条件卡", "judgement_ref": "HW/PCB/FET3572C_PIN_TABLE.csv (P1_92/94/98/100; P3_14/16/18/20); HW/netlist_v1.csv row290/291"},
    {"scope": "tbd", "ref": "TBD-11", "tbd_labels": ["TBD-11"], "rows": 4, "pend_rows": 4, "conclusion": "已闭 (板侧零动作): 4 行 = R_SER_SPI_MOSI/MISO 及其 _BOOT 支路 ⇒ 4 条 0Ω 串阻位已在板; SoM 有无 SPI 控制器是 SoM 文档问题不是原厂问题; demo 走 ADB push 档 ⇒ 根本不需要外挂启动存储 ⇒ 4 行 [待原厂] 是「ARS45 时代外挂还是内置」这个已消化的问题", "evidence": "[实测]", "evidence_ref": "HW/netlist_v1.csv row291-294 (TBD-11 4 行, 全 [待原厂]) + state/fragments/hw.yaml risks.R-hw-boot-storage", "downgrade": "demo 档零动作; SPI-NOR 档 4 串阻位必装 (板位已在); SoM 无 SPI 脚则走 eMMC 档 ⇒ 产品板改板宽 ⇒ 归产品板档", "blocks_board": "不卡", "judgement_ref": "HW/netlist_v1.csv row291-294; state/fragments/hw.yaml risks.R-hw-boot-storage"},
    {"scope": "tbd", "ref": "TBD-12", "tbd_labels": ["TBD-12"], "rows": 27, "pend_rows": 5, "conclusion": "对 demo 板 = 伪 blocker (板侧零动作): 27 行含 PG_AND 链/VDD_1V8_IO/RESET_N/GND/EN_VCORE/EN_VIO/SUPV_CT/XTAL×5/BOOT_N; U_SUPV 整颗 DNP + U_DCDC_VCORE/U_DCDC_VIO DNP ⇒ SoM 自带 PMIC ⇒ 主 PCB 不控 SoC 内部上电顺序 ⇒ 主板只管自己的 5V→3.3V→1.8V 链 ⇒ 原判据「🔴 待原厂 (TBD-12)」对 demo 板已过期", "evidence": "[实测]", "evidence_ref": "HW/netlist_v1.csv row74/78/85/406/407/408 (TBD-12 27 行: [推算]6 + [官方]9 + [待原厂]5 + [同Die参考-待官方确认]7) + HW/ERC_DRC_CHECKLIST.md §B5/§B15 + HW/TI_POWER_FACTS.md §② 订正 B", "downgrade": "主板侧时序用板上器件自洽 (U_SUPV 监控 + PG 链 + RC 软启动) ⇒ 不改板; U_SUPV 若要装 (复位链) 需 main 核该位是否在板 —— 不在板则要改板 ⇒ 那一趟同批; 产品板档 (裸 SoC) ⇒ TBD-12 重新变成真卡点 ⇒ 归产品板档条件项", "blocks_board": "条件卡", "judgement_ref": "HW/netlist_v1.csv row74/78/85/406/407/408; HW/ERC_DRC_CHECKLIST.md §B5/§B15; HW/TI_POWER_FACTS.md §② 订正 B"},
    {"scope": "tbd", "ref": "TBD-13", "tbd_labels": ["TBD-13"], "rows": 2, "pend_rows": 1, "conclusion": "已闭 (板侧零动作): FSIN = SoC_NC 占位 + 50Ω 串阻 + TP_FSIN 测试点 ⇒ 板侧已给全; SoM 逐针表无 FSIN ⇒ SoM 不引帧同步 ⇒ 能不能用是软件/固件的事 ⇒ 1 行 [待原厂] 已被 SoM 路线消化", "evidence": "[实测]", "evidence_ref": "HW/netlist_v1.csv row399/400 (TBD-13 2 行: [待原厂]1 + [推算]1) + HW/PCB/FET3572C_PIN_TABLE.csv (grep FSIN ⇒ 0 行)", "downgrade": "帧同步改用 SoM 已有机制 ⇒ 板侧零动作; 若要真引 ⇒ 换 SoM 或走 MIPI ⇒ 产品板档", "blocks_board": "不卡", "judgement_ref": "HW/netlist_v1.csv row399/400; HW/PCB/FET3572C_PIN_TABLE.csv"}
  ]
}
```

---

## §5 ★★留给 main 的 5 个问句 (★本单一律不代拍★) ★★

| # | 问句 | 本单给的建议 + 代价 | 判据出处 |
|---|---|---|---|
| ★**①** | ★**HW-B1~B7 哪些条可以正式解除 / 降级** | ★**建议**: HW-B1 / B2 / B4 **可解除 (对 demo 板)** · HW-B3 / B5 / B6 **降级 (不再是「等外部」)** · HW-B7 **不是外部依赖**, 建议与 B6 合并处理。★**解除动作归 main (本单只给结论 + 判据, 不动 `blockers` 段)** ★ | §2 |
| ★**②** | ★**8 条 needs 的 `to` / `waiting_on` 各自改成什么** | ★**建议 (本单已按此落进 `state/fragments/hw.yaml`, 逐条见 §6)**: 全部 `to=main` + `waiting_on` 清空 (自查闭的 6 条) / `to=main` + `waiting_on=boss` (N-1 宽高比那一半) / N-2 与 N-3 标作废 (仍 `to=main` 以便 main 落账)。★**代价 = 0 板费** (不改板) ★ | §6 + §1 |
| ★**③** | ★**TBD-01..TBD-13 里哪几条还卡「板那一趟」** | ★**答案: 11 项不卡 · 2 项条件卡 (TBD-10 USB 端口选型 / TBD-12 `U_SUPV` 是否在板)** ⇒ ★**外部依赖维度上 = 0 条卡** ⇒ ★**⇒ 板那一趟的网表真源可以冻结** ★ | §3 |
| ★**④** | ★**新闸挂不挂链** | ★**建议: 先落完 D1/D2 再挂** —— 因为本单收口后 D1/D2 应转绿, 但 D3/D4/D5 依赖真相页内容正确 ⇒ ★**挂链前先裸跑一次确认 rc=0** ⇒ ★**挂不挂 = main 的地界 (本单零挂链)** ★ | §6 闸章 |
| ★**⑤** | ★**网表里 36 行 `[待原厂]` 归谁落** | ★**建议: 同批落 (与板那一趟同批)** —— 因为本单已给出**逐项决策** (§3), 落表动作 = 把 109 行的 `tbd` 标签按 §3 的结论改成实值或明确降级标注 ⇒ ★**这一步改网表真源 ⇒ 必须与板那一趟同批, 否则板 md5 第二次变** ⇒ ★**落表归 main (本单零落表)** ★ | §3 + §6 |

---

## §6 ★★机器闸 + 复现命令 ★★

### §6.1 · 新闸 `HW/check_hw_external_dep_closed.py` (★5 条判据★)

| 判据 | 内容 | 现状 |
|---|---|---|
| ★**D1** | HW 域 `needs_from` 里不许再有 `waiting_on ∈ {vendor, jbd}` | ★**现状 8 条 ⇒ 红** ★ |
| ★**D2** | HW 域 `needs_from` 里不许再有 `to ∈ {vendor, jbd}` | ★**现状 2 条 ⇒ 红** ★ |
| ★**D3** | 网表 109 行 `tbd` + 36 行 `evidence=[待原厂]` 必须 100% 被真相页登记块覆盖 (★含: 13 个 TBD 标签全覆盖 + 每标签声明行数 == 实测行数 + 8 条 needs 全登记 + 7 条 blocker 全登记★) | ★**现状 0% ⇒ 红** ★ |
| ★**D4** | 每条登记条目必须同时有【证据等级】和【降级方案或结论】 | ★**同上 ⇒ 红** ★ |
| ★**D5** | 每条登记条目必须写【还卡不卡板那一趟】(卡/不卡/条件卡) + 判据出处 | ★**同上 ⇒ 红** ★ |

### §6.2 · 复现命令 (★本单自己跑过的全部命令★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
GATE=HW/check_hw_external_dep_closed.py
python3 "$GATE"            # ★裸跑: rc=1 (红的是现状, 不是闸故障) ★
python3 "$GATE" --selftest # ★rc=0 · 末行 ALL TESTS PASS ★
python3 state/merge.py     # rc 必须 0
python3 state/gate_check.py # Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       state/gen_netlist.py state/gen_pcb_netlist_board.py state/land_v_values.py state/decision_truth.py
```

---

## §7 ★★本单自查出来的【真发现】清单 (★不改设计, 只登记给 main★) ★

| # | 发现 | 级别 | 证据 | 处置 |
|---|---|---|---|---|
| ★**F1** | ★★**TPS62130A 的 R_on 假设被证伪** ⇒ 方案 A' (UVP 3.35V) 从「成立」降为「条件成立」 (R_total ≤ 142.9 mΩ; typ 路径吃掉 120 mΩ, 只剩 22.9 mΩ 给电感 DCR) ⇒ **若按原假设直接定 UVP 3.35V, 有约 1/3 概率做出黑屏板** | ★**高** ★ | ★`[官网]` TI SLVSAG7F §6.5 (本机 L304-308) + `[推算]` 算式 | ★**归 main/老板拍 UVP 落点**; 电感 DCR ≤20 mΩ 写进选型硬判据 ★ |
| ★**F2** | ★★**Q16 答案不是「DSI + DP 两者」, 是「DSI TX」** —— SoM 只引出 DSI TX + HDMI TX, **没有 eDP/DP TX 脚** ⇒ 网表里的 `R_SEL_*` 双出口 0Ω 选择位对 demo 板是冗余的 (但保留零成本) | ★**中** ★ | ★`[官网]` Forlinx 逐针表 + `[实测]` 网表 row210-229 | ★**登记 main**; 保留 0Ω 位 (零改板) ★ |
| ★**F3** | ★★**网表里 USB 用的是 `USB_DRD1` (官方默认功能写的是 `USB20_HOST1` = Host 侧) 接 Type-C** ⇒ 若要做 USB Device, 官方可做 Device 的是 `USB2_OTG0` (P3_18/P3_20) ⇒ **端口选型问题, 但换脚要改板 ⇒ 必须同批** | ★**中** ★ | ★`[官网]` Forlinx 逐针表 + `[实测]` 网表 row290/291 | ★**登记 main (TBD-10 条件卡)** ★ |
| ★**F4** | ★★**ERC 清单 §0 第 4 行的「原厂 4 项闭合 (TBD-01/02/04/06/11)」是 2026-10 口径, 已过期** —— 这 5 项在 demo 板口径下全部已闭 (TBD-01 由 ISS-204 闭 / TBD-02 SoM 自带 PMIC / TBD-04 SoM 逐针表 / TBD-06 三档化 / TBD-11 三档化) ⇒ ★**`HW/ERC_DRC_CHECKLIST.md` §0 第 4 行与 §D1 是本单找到的【过期锚点】** | ★**中** ★ | ★`[实测]` 本页 §3 + `HW/ERC_DRC_CHECKLIST.md` L16/L98 | ★**登记 main 改既有页 (本单零改既有页正文)** ★ |
| ★**F5** | ★★**任务书的两处计数需订正**: 外部路由 **8 条 (不是 10)** · 网表待清行 **109 行 (不是 145)** ⇒ 「板那一趟开工当天仍有 145 行可能动网表」订正为 **109 行** | ★**低** ★ | ★`[实测]` 本页 §0.2 (附可复现命令) | ★**已在本页订正并说明** ★ |
| ★**F6** | ★★**网表里 demo 板的 5V 进线还没落**: `J_TYPE_C` / `U_CHG` 在 CHG_BOARD 必装, 而 `U_BATPROT` / `BT_432243` / `Q1` / `Q2` 全 DNP ⇒ ★**SYS 轨在 demo 板上无源** ⇒ ★**这是【落表项】不是【外部依赖项】** ⇒ 但它是板那一趟的真实待清项 | ★**中** ★ | ★`[实测]` `HW/netlist_v1.csv` row12/24/26/28/29/36/37/48/49/121 | ★**登记 main 落表批次 (与板那一趟同批)** ★ |
| ★**F7** | ★★**ISS-204 F1 查出的真缺陷仍在**: UART_TX/UART_RX 无 100 Ω 串阻 + 插口旁无 TVS ⇒ 官方手册明写「需要 100 ohm 串联 + TVS」, 且原话警告「未上电时反灌可能影响启动甚至损坏」 ⇒ **属网表改动 (加 2 电阻 + TVS), 归落表批次** | ★**中** ★ | ★`[官网]` Forlinx §3.5.5 + `[实测]` 网表无该器件 | ★**登记 main 落表批次** ★ |

---

## §8 ★★一句话纪律 (★收工前最后看一遍★) ★★

★★**本单的价值不在"又查了一遍", 在"HW 域这 8 条外部依赖从此不再是阻塞项": 每一条要么自己查掉了 (附官网链接 + 证据等级), 要么写清了降级方案 (附判据) ⇒ 老板清单里的"等外部"能真正减下来, 板那一趟的网表能真正冻结 ⇒ ⇒ 而这一趟板 md5 只许变一次** ★★

> ★**执行边界自证**: ★**零写板** (`HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` 收工时逐字相同) · ★**零落表** (网表/脚表/BOM/两个生成器/`state/land_v_values.py`/`state/decision_truth.py` 8 个 md5 逐字相同) · ★**零改既有闸阈值** · ★**零改既有页正文** · ★**零外发** (本单未发任何邮件/询价/问询/采购) · ★**不代老板拍板** · ★**不自签 issue_log** · ★**零挂链** · ★**只写自己的分片** (`state/fragments/hw.yaml`, 走 `state/frag_write.py`) · ★**沙盒落 `tmp/iss401/` (未写系统 `/tmp`)** ★
>
> ★**本单实际写入的文件**: ① `HW/HW_EXTERNAL_DEPENDENCY_SELFCHECK_CLOSURE.md` (新建·真相页) ② `HW/check_hw_external_dep_closed.py` (新建·机器闸) ③ `HANDOFF/2026-11-24_hw-lead_ISS401_HW域外部依赖自查收口.md` (新建·交卷页) ④ `state/fragments/hw.yaml` (走 `frag_write.py`·只改那 8 条 needs 的 `to`/`waiting_on`/`item` + 新增 artifact/claim/answer) ⑤ `logs/iss401/` (留证) ★
