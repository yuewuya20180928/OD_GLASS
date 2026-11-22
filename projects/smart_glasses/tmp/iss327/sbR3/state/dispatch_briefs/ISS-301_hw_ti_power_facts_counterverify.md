【项目总工派活 · 队列自动派活 · 闭环 ISS-301】你是 硬件总工 (hw-lead)。

★★【★★主线口径 (★老板 2026-11-17 00:43 指令★)★★】★★ 当前主线 = **绘制 PCB 图** ⇒ ★**PCB 布线 / 布局类可派** ⇒ ★**但「板只改一次」铁律: 会改板的动作必须一次做完** ⇒ ★**★本单是【纯分析 + 复核类】⇒ 零写板 · 零落表 · 零改网表真源 ★★

★**本单性质**: ★**复核类 + 残余事实类 (★不动板 · 不动网表 · 不动脚表 · 不动 BOM★)** ★ ⇒ ★**唯一目的 = 给两条卡在 `fixed` 的单 (ISS-095 / ISS-102) 签字依据, 并把唯一的 [0数据] 残余答掉** ★

★**派活人**: 项目总工 (main / moli) · ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**时刻**: 2026-11-17 22:5x · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-301 · ★**due**: 2026-11-19 · ★**零外发** ★

---

## ★① 病灶 (★main 2026-11-17 22:4x~22:5x 本机实跑, 原样 rc/原文, 不抄任何交卷报告★)

★**背景**: ★**`HW/TI_POWER_FACTS.md` (7,765 B · mtime 2026-11-16 06:46) = main 自产的 [官网] 事实卡** (★标题自述: 「TI 电源器件 + RK3572 电源域 【官网自查】事实卡 (ISS-095 / ISS-102)」★) ⇒ ★**铁律「自己产的必须别人验」⇒ 这张卡至今【没有人验过】⇒ ISS-095 / ISS-102 两条自 11-16 起卡在 `fixed` (owner=main · verify_by=hw-lead · due 11-19)** ★

★**main 实测 (★22:4x 本机实跑★)**:
```
$ ls -la --time-style=full-iso HW/TI_POWER_FACTS.md
-rw-rw-r-- 1 yuewuya yuewuya 7765 2026-11-16 06:46:36.763210225 +0800 HW/TI_POWER_FACTS.md
```
★**卡里四条断言 (★逐字★)**: ★**① BQ25896 的 SYS/VSYS 脚 —— 必须接 20 µF, 不能悬空 [官网]** · ★**② TPS62130A 的 PG 极性 —— 高 = 好, 开漏需上拉 [官网]** · ★**③ RK3572 有 dedicated USB VBUS detect 脚 —— 有, 2 个 [官网]** (★`1C18 = USB_DRD0_VBUSDET` · `B28 = USB_DRD1_VBUSDET`★) · ★**④ ISS-102 ① (ARS45 的 AON/唤醒脚) —— 该问法已作废** ★

★**★卡里自己承认的【唯一残余缺口】(★L61 逐字★)**: ★**「但仍差一步 (★别当成已闭环★): ★**SoM (Forlinx RK3572 模组) 有没有把这两个球引出来, 本卡无法判定** ⇒ ★**〔0数据·待核〕: 查 Forlinx RK3572 模组手册的引脚表** ⇒ ★**若 SoM 已引出 ⇒ 直接用; 若没引出 ⇒ 仍要分压」★ ★

★**★main 22:5x 本机已先查了一步 (★给你省时间, 但【结论仍要你自己独立复核 + 补证据链】★)**: ★**`HW/PCB/FET3572C_PIN_TABLE.csv` (400 行 = 表头 1 + SoM 球位 399) 里两条命中** ★:
```
$ grep -nE "VBUSDET" HW/PCB/FET3572C_PIN_TABLE.csv
101:P1,100,B28,USB_DRD1_VBUSDET,——,——,USB2_OTG1_VBUSDET insert detection,USB2_OTG1_VBUSDET
216:P3,16,1C18,USB_DRD0_VBUSDET,——,——,USB2_OTG0_VBUSDET insert detection,USB2_OTG0_VBUSDET
```
★⇒ ★**初步读数 = 【两颗球 SoM 都引出来了】(P1.100 = B28 = USB_DRD1_VBUSDET · P3.16 = 1C18 = USB_DRD0_VBUSDET) ⇒ ★**⇒ 网表那条 [官方] 断言 (`HW/netlist_v1.csv` L439: 「[VBUS_DET] ★SoM 的 USB_DRD1_VBUSDET (P1_100) ← 板载 Type-C VBUS 分压」) 看起来是对的** ⇒ ★**⇒ 而 ⇒ 【板只改一次】那一趟的 S6 布局清单里 `R_VBUS_DET_D1` / `R_VBUS_DET_D2` / `C_DET_VBUS_D` 三件【不用动】** ★ ⇒ ★**★但这是 main 的初步读数 ⇒ ★**你的活 = 把它变成【可引用的证据链】(含官方手册出处) 并复核其余三条断言** ★

★**★同时 main 22:5x 实测到一条【规格 vs 网表】的张力, 也要你判 (★不许你改网表, 只出结论+代价★)**: ★**`HW/netlist_v1.csv` L499 (逐字)**: ★**`P10,SYS_CHG,U_CHG pin16,C_SYS,C_SYS,20µF 6.3V,C,DNP,[官方],,"★C_SYS 留位不装 = 保留 '电池挪镜框' 可回退分支 (将来接 2 根线 + 贴这颗电容即可, 不用改板); 本板 SYS 无负载, 装 20µF 只占 25×10mm 板面 ★裁决 (PM): 电池与负载**都在镜脚** ⇒ 充电板没有系统侧负载 · **VSYS...` ★ ⇒ ★**⇒ 即: TI 规格说 SYS 脚必须挂 20 µF, 我们把它标了 DNP, 依据是「本板 SYS 无负载」这条 PM 裁决 ⇒ ★**你要判的是: 这两条自洽吗? 若不自洽, 代价是什么?** ★ (★C_SYS 在 **CHG_BOARD** (C-03) 上, 不在 demo 主 PCB 上 ⇒ ★**影响的是充电板, 不是「板只改一次」那一趟的主板 ⇒ 但仍要写清归属★★) ★

---

## ★② 要交的三件 (★每件都能独立验收★)

### ★B1 · 四条断言的复核表 (★逐条给结论, 不许只写「已复核」★)

★**做一张表, 每条一行, 列齐: `断言编号 | 卡里的原文(逐字) | 证据出处(文件+行号 或 URL+访问日期) | 本次复核手段(实际跑了什么) | 结论(成立 / 不成立 / 部分成立) | 证据等级` ★**

★**四条的复核手段各是什么 (★main 22:5x 已替你查过一步, 但每条都要你自己跑一遍并留下可复现命令★)**:
- ★**① BQ25896 SYS 必接 20 µF**: ★**卡里引的是 TI bq25896 datasheet (SLUSC76C) §7 Pin Configuration and Functions 逐字: "The internal BATFET is connected between BAT and SYS. … **Connect a 20uF closely to the SYS pin.**"** ⇒ ★**你要核: ① 本仓有没有 TI 官方 datasheet 原文可离线对拍? ② 没有就按 11-12 02:02 政策【自己网上查 TI 官网】(★不许发信 / 不许询价★) ⇒ 记 [官网] + URL + 访问日期 ⇒ ★**③ 若仍查不到 ⇒ 写 [0数据] + 降级方案 (★不许把外部依赖挂着当阻塞项★)** ★
- ★**② TPS62130A PG 极性 = 高有效 + 开漏需上拉**: ★**卡里引 "Output power good (High = VOUT ready, Low = VOUT below nominal regulation); open drain (requires pull-up)" + §9 "pulls the PG pin Low when the device is shut down by EN, UVLO, or thermal shutdown"** ⇒ ★**同上核; ★**并核一句: 这跟本项目复位链 (`RESET_N` / `U_SUPV` / `DMP3098L`) 的实际接法自洽吗? (★只读不改★)** ★
- ★**③ RK3572 两颗 USB VBUS detect 球**: ★**卡里引 `HW/RK3572_PIN_TABLE/rk3572_pins.csv` + datasheet 抽取文本 (引脚表 L1641 / L1651)** ⇒ ★**你要核: ① 那两颗球在 SoC 侧确实存在 (★grep `HW/RK3572_PIN_TABLE/rk3572_pins.csv`★) ② ★**【本单的核心】SoM 侧有没有引出来** ⇒ ★**用 `HW/PCB/FET3572C_PIN_TABLE.csv` (P1.100 / P3.16 两行) + `HW/PCB/RK3572_SOM_BALLTABLE_CROSSCHECK.md` (★它 §1 实测: 我们 399 行 vs 官方手册 399 行, Signal Name / BALL / GPIO / VOL 四列零差异 ⇒ ★**本地表可信度 = 官方手册级**★) ⇒ ★**③ 【板侧影响】**: 既然 SoM 引出了 ⇒ 网表那条 [官方] 断言 (L439) 成立 ⇒ ★**⇒ 【板只改一次】那一趟的 S6 布局清单里 `R_VBUS_DET_D1` / `R_VBUS_DET_D2` / `C_DET_VBUS_D` 三件【留, 不动】⇒ 板侧清单零变化 ⇒ 「板只改一次」不受影响** ⇒ ★**★这一条必须写成给 main 的明确结论 (★main 要拿它去确认作业包 §3-S6 不用改★)** ★
- ★**④ ISS-102 ① (ARS45 的 AON/唤醒脚) 作废**: ★**卡的依据 = 「ARS45 / AR9481 / 酷芯微 已于 2026-10-29 19:20 拍板作废」+ 「RK3572 datasheet V1.1 全文检索无 AON 字样」** ⇒ ★**你要核: ① 全文检索确实无 AON (★自己 grep `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt`★) ② ★**并核一句降级方案是否还站得住**: 「关机续航沿用 ISS-097 §0 第 6 条 ~108 µA / 0.40 mW [推算], AON 项按 0 计」★ ⇒ ★**注意: ISS-097 现在 owner=boss · status=fixed (★等老板过目★) ⇒ 你不许去动它, 只出结论★** ★

### ★B2 · 交叉一致性 (★只读, 不许改网表★)

★**两处要判**:
1. ★**ISS-095 ① (SYS 必接 20 µF) vs 网表 L499 `C_SYS` = DNP 的 note** ⇒ ★**自洽吗? 代价是什么? (★板面积 25×10mm · 归属 CHG_BOARD 不是 demo 主 PCB★)** ★ ⇒ ★**结论只能写给 main + 老板 (★不许你代拍★)** ★
2. ★**ISS-102 ④ 已被 ISS-095 结掉** ⇒ ★**两条的交叉引用有没有写错 (★查 `state/issue_log.yaml` 里 ISS-095 / ISS-102 的 note 与 `HW/TI_POWER_FACTS.md` §⑤「BQ25896 的 /PG (与 ② 的 TPS62130A PG 是两个脚, 别混)」★)** ★

### ★B3 · 复现命令 + 现场 rc (★贴现场 rc, 不许只说「已复核」★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
grep -nE "VBUSDET" HW/PCB/FET3572C_PIN_TABLE.csv ;              echo "rc=$?"
grep -nE "USB_DRD0_VBUSDET|USB_DRD1_VBUSDET" HW/RK3572_PIN_TABLE/rk3572_pins.csv ; echo "rc=$?"
grep -c "AON" HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt ;     echo "rc=$?"   # ★期望 0★
grep -n "VBUS_DET" HW/netlist_v1.csv ;                             echo "rc=$?"
grep -n "C_SYS" HW/netlist_v1.csv ;                                echo "rc=$?"
python3 HW/check_netlist_selfconsistency.py --expect-resolved ;    echo "rc=$?"
python3 state/merge.py ;                                           echo "rc=$?"
python3 state/gate_check.py ;                                      echo "rc=$?"
python3 state/issue_check.py ;                                     echo "rc=$?"
grep -c iss301 state/fragments/hw.yaml ;                           echo "count=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb
```

### ★B4 · 交卷单 + 分片 (★各一件★)

1. ★**交卷单** `HANDOFF/2026-11-17_hw-lead_ISS301_TI电源事实卡复核.md` (★B0 一句话结论 + B1 复核表 + B2 交叉一致性 + B3 现场 rc + B4 边界自证 + B5 待 main 动作★) ★ ⇒ ★**必须含一块【给 main 的明确结论】**: ★**① ISS-095 能不能落 verified? ② ISS-102 能不能落 verified? ③ 板侧影响一句话 (S6 清单变不变) ④ 若有错, 错在哪一行 + 修法 + 代价 (★不许你改网表真源, 那是 main 的活★)** ★
2. ★**分片** `state/fragments/hw.yaml` (★**必须走 `python3 state/frag_write.py` 原子写, 禁止 `open(p,"w")`★**) ⇒ ★**至少 1 条 `needs_from` (to=main, key 逐字 = `iss301_ti_power_facts_counterverify_result`) + 1 条 `interface_claims` (key 逐字 = `iss301_ti_power_facts_4_claims_verified`) + 1 条 `artifacts` (交卷单路径)★** ⇒ ★**写完 `grep -c iss301 state/fragments/hw.yaml` 校验 ≥ 3** ★ ⇒ ★**不许写 `mech.yaml` / `sw.yaml` / `pm.yaml`** ★

---

## ★③ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 + mtime 双重自证★) ★ · ★**零落表** (★不许动 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 本体·只读★) ★ · ★**★零改网表真源** (★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/TI_POWER_FACTS.md` **一个字都不许改** ⇒ ★**发现了错也只写成结论交给我 (main) 去改**) ★ · ★**零改脚表 / 零改 BOM** ★ · ★**不许改 `state/gate_check.py`** (★挂闸是 main 的活★) ★ · ★**不许改 `HW/check_netlist_selfconsistency.py` 与任何闸本体** ★ · ★**不许写 `state/issue_log.yaml`** (★铁律: 干活的人不许自签 · ★**ISS-095 / ISS-102 的签字是 main 的活, 你只交依据★**) ★ · ★**不许外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **不许发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ⇒ 缺口一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项★) ★ · ★**不替老板拍板** (★B2 的取舍只列事实与代价★) ★ · ★**实物 `[实测]` = 0 条** (★本单全是文档/表格级复核★) ★ · ★**只写交卷单 + 你自己的日志 (★`logs/iss301/`★) + 你的分片** ★

## ★④ 死因纪律 (★这项目的老教训★)

★**① 先落盘**: ★**先把交卷单骨架 (B0 + B1 表头) 写下来落盘, 再去查** ⇒ ★**每 10 分钟至少一次写盘** ★ · ★**② 长任务一律 `nohup ... > logs/iss301/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) ★ · ★**③ 单条 `exec` ≤ 60 秒** ★ · ★**④ 不许把整份大文件读进来** (★只 grep 你要的那几行★) ★ · ★**⑤ 文档订正必须追加式** (★老字不许删★) ★ · ★**⑥ 不许为了让闸变绿而改闸 / 放宽判据** ★

## ★⑤ 交卷回复格式 (★贴现场 rc, 不许只说「已完成」★)

★**① B1 复核表全文 + B2 两条一致性结论** · ★**② 上面 §B3 那组命令的现场 rc 原样** · ★**③ 受保护 5 件 md5 + 板 mtime** · ★**④ 「ISS-095 / ISS-102 能不能落 verified」这一句的直接回答 + 依据** · ★**⑤ 诚实边界 (★零写板零落表零改网表·零外发·实物 [实测]=0 条·没自签 issue_log★)** ★
