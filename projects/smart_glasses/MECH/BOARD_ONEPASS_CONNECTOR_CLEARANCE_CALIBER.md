# 座体净距判据**同源化**总表 (★`J_DEBUG` 铜箔支配 vs `J_UART` 座体支配 ⇒ 两条口径合成一条★)

> ★**一句话结论** ★**把「座体净距」统一成一条判据链之后, 两颗同族排针的判决【不再相反的原因不是 `J_DEBUG` 变好了, 而是 `J_UART` 的红从「藏在另一套口径里」变成了「同源表上一目了然的红」】** ★
> ★**同源化还额外算出两条此前没被算出来的红**: ★**① `J_UART` 现状 Y 向罩住余量最坏 `0.5200` < `CRIT` `0.60` (ISS-374 只按「铜箔比座体窄 ⇒ Y 不构成卡点」的包含关系判 Y, 没按余量判)** ★ ; ★**② `J_DEBUG` 换官方 1×4 THT 后, 铜箔每边超出真相页清空区 `1.5175` (现页四处理想口径给的是 `0.3625` ⇒ 两个数都红, 方向一致)** ★
> ★**本页的产出物只有三样**: ★**(a) §1 一张同源总表 (板面 9 颗连接器逐颗一行 + 4 个换官方 land 档)** · ★**(b) §2 四条口径冲突清单 (含后果句 / 判据句分开写)** · ★**(c) §3 座体真实型号自查 + 降级方案 (查不到处不挂起)** ★
> ★**本单边界**: ★**零写板 · 零落表 · 零改既有闸 · 零改已签收页正文 · 零挂链 · 零外发 · 不代老板拍板 · 不自签 `state/issue_log.yaml`** ★

★**派活**: 项目总工 (main) · ISS-377 · 2026-11-24 派 / 做 · 交卷人 = 结构总工 (mech-lead) ★
★**续做**: ★**cont1** (★上一趟 02:51 被 16 分钟墙掐死 · 只落了事实文件 `logs/iss377/board_connectors.json` · 三件交付物零★) ★
★**本页闸**: ★**`MECH/check_connector_clearance_caliber.py`** (★本单新建 · 判据 K0~K8 · ★**未挂 `state/gate_check.py`·挂不挂归 main★**★) ★
★**交卷页**: ★**`HANDOFF/2026-11-24_mech-lead_ISS377_座体净距判据同源化与座体型号自查.md`** ★
★**沙盒 / 留证**: ★**`tmp/iss377/` + `logs/iss377/`** (★不写系统 `/tmp`·★系统 `/tmp` 用户配额已满·写那里会出假读数★) ★
★**证据分级**: ★`[官网]` / ★`[实测]` / ★`[媒体]` / ★`[推算]` / ★`[0数据]` (★五级白名单·★本单实际用到的只有 `[实测]` `[推算]` `[0数据]` 三级★) ★

★**只读引用的既有真相页 (★一个字节都没改★)**: ★**`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md`** (★座体必须清空区与开口的真身·§3.4 `J_DEBUG` / §3.5 `J_UART`★) · ★**`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md`** (★ISS-371·已签收 verified★) · ★**`MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md`** (★ISS-374·已签收 verified★) · ★**`MECH/service_port_check.py`** (★`CRIT` / `TOL` 真身 L126-L127★) ★

---

## ★§0 一句话结论 + 同源判据公式 ★

### ★§0.1 同源判据链 (★全表只有这一条链·★两件不许各算各的★)★

```
① 座体必须清空区 H (X/Y 宽)     ← 真身: MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md §3.4 / §3.5 / 机器块
② 铜箔包络 C (X/Y 宽)            ← 真身: 板面实读 (logs/iss377/board_connectors.json) 或官方 land 真值
③ 同源化必须清空区 M = max(H, C) ← ★本单新加的同源步骤: 两件同一公式, 不再各挑一边★
④ 开口余量 (per side) = (O − M) / 2      O = 开口宽 (同 §3.4 / §3.5)
⑤ 罩住余量 (per side) = (H − C) / 2      ★「座体必须清空区有没有把铜箔罩住, 且留够 CRIT」★
⑥ 最坏余量 = 余量 − TOL["fdm_part"]      (★FDM 座体/罩外形公差往内吃·★TOL 与 CRIT 从 MECH/service_port_check.py L126-L127 取·★本页与闸都不写死★)
⑦ 判据: 最坏余量 ≥ CRIT                 (★CRIT = 2 × TOL["fdm_part"]★)
```

★**为什么必须是 ③④⑤ 三条一起走 (★这就是 ISS-374 亲手立的病根★)★**:
★**旧**: ★`J_DEBUG` 只走 ④ (开口余量 `4.2125` → `2.6950` 过阈) ; ★`J_UART` 只走 ⑤ (罩住余量 `0.8825` → `0.1350` 不过阈) ⇒ ★**两件的分母不同 ⇒ 方向相反却都叫「余量」⇒ 每次换件都要重新猜一次口径** ★
★**新**: ★**每一行都同时给出 ④ 与 ⑤, 用同一个 ③ 同源化 ⇒ 两件的数从此可比; 方向相反这件事被【保留】, 但不再被【口径差异】掩盖** ★

### ★§0.2 「清空区口径来源」这一列的定义 (★本单的核心产出★)★

| 取值 | 定义 (★数值同源推导·★不许人挑★) | 含义 |
|---|---|---|
| ★`copper_driven` ★ | ★`H == C` (X 或 Y 某轴) ⇒ 现有模型里的「座体宽」其实是**拿铜箔宽冒充**的 ⇒ 该轴的 ⑤ 是同义反复 (余量恒 0) ⇒ 不可作判据 | 座体真实占位 **未建模** |
| ★`housing_driven` ★ | ★`H > C` (某轴) ⇒ 现有模型里的「座体宽」是**独立的座体占位假设** ⇒ 该轴的 ⑤ 有效可判 | 座体占位 = **模型假设** (真实型号未定) |
| ★`unknown` ★ | ★该连接器在既有真相页里**根本没有**必须清空区模型 ⇒ ④⑤ 全算不出 | ★**未建模** ⇒ 挂 OI-6 ★ |

★**★逐轴给, 不逐件给 (★本单在同源化过程中发现的一个事实·★见 §2-C4★)★**: ★**同一个连接器的 X 与 Y 两轴, 口径来源可以不同** ——
★**`J_DEBUG`**: X 轴 `Hx 1.7750 == Cx 1.7750` ⇒ ★`copper_driven` ; Y 轴 `Hy 2.5400 > Cy 0.9000` ⇒ ★`housing_driven` (★真相页写的是「座体, 高 2.54 假设」★) ⇒ ★**一颗件两个口径 ⇒ 「口径来源」这一列如果是单值, 必然丢信息** ★
★**`J_UART`**: X 轴 `Hx 2.5400 > Cx 0.7750` ⇒ `housing_driven` ; Y 轴 `Hy 2.5400 > Cy 0.9000` ⇒ `housing_driven` ⇒ **两轴同源 (座体模型)** ★
★**⇒ 所以 §1 的「清空区口径来源」列按 X / Y 两轴分别写 (★闸 K1 按两轴分别查★)★**

### ★§0.3 本单的两条结论 (★判据句与事实句分开·★不混成一句★)★

★**判据句 (方向层)**: ★**在同源判据下, `J_UART` 换官方 1×2 THT 后的罩住余量 = `0.1350` (最坏 `-0.1650`) < `CRIT` `0.60` ⇒ 不过阈 ; 姊妹件 `J_DEBUG` 换官方 1×4 THT 后的开口余量 = `2.6950` (最坏 `2.3950`) ≥ `CRIT` ⇒ 过阈** ★
★**事实句 (铜箔层)**: ★**若结构件继续按现有真相页的必须清空区 (`J_UART` X `2.5400` / `J_DEBUG` X `1.7750`) 出件, 则 `J_UART` 换 THT 后铜箔 X 宽 `2.2700` 比座体清空区宽 `2.5400` 每边只差 `0.1350` (最坏 `-0.1650`) ⇒ 铜箔不再被座体完全罩住 ; `J_DEBUG` 换 THT 后铜箔 X 宽 `4.8100` 每边超出真相页清空区 `1.5175` ⇒ 铜箔直接进清空区** ★
★**两句同时成立**: ★**「过阈」≠「结构侧不用改」; 「铜箔进清空区」≠「余量判据不过」** ★

### ★§0.4 本单对「K2 怎么读」的明写 (★让复核的人一眼看到本单没有把红行写成绿★)★

★**§1 表里【有真红行】** (`J_UART` 现状罩住 X/Y 两轴、`J_DEBUG` 换官方 land 后的罩住轴、两个 SMD 档的 Y 轴) ⇒ ★**本单对 K2 的读法是**: ★**每一行、每一轴、每个档的最坏余量都必须与 `CRIT` 逐个比对并把判决写进表里 (不许留空); 判决不许与实算相反 (不许把不过写成过); 任何红行必须挂未决项号 + 降级候选 (不许静默红)** ★
★**⇒ 如果把 K2 读成「所有行都必须绿」, 那这张表就只能靠造假才能绿 ⇒ 本单不这么读 (★此读法已在 §1.3 与交卷页 B2 复述★)★**

---

## ★§1 同源总表 (★本单的主表★)★

★**覆盖范围**: ★**板面上每一颗连接器/排针/座体件逐颗一行** ⇒ ★**实读板面共 9 颗** (`J_BOOT1` · `J_CHG` · `J_DEBUG` · `J_SOM_P1` · `J_SOM_P2` · `J_SOM_P3` · `J_SOM_P4` · `J_UART` · `J_USB_C`) ⇒ ★**板上没有 键盘类 / 复位类这类位号 (★`grep -oE '\(property "Reference" "J[^"]*"' HW/PCB/demo_mainboard.kicad_pcb | sort -u` 只出上面 9 个★)** ★
★**列义**: ★`位号` / `颗数` / `现状 land` / `现状铜箔包络 X/Y 宽` / `座体必须清空区 X/Y 宽` / `开口 X/Y 宽` / `清空区口径来源` / `每边余量 (现状)` / `最坏余量 (FDM ±0.30)` / `CRIT` / `过/不过` / `证据等级` / `来源页 + 行号` ★
★**★「每边余量」与「最坏余量」两格都是【向量】(★每格两个数: 前一个 = 开口口径 ④ · 后一个 = 罩住口径 ⑤★)★** ★
★**★每一格都能指回某个既有页的某个数 · 本页不另算一套★ ★**

### ★§1.1 现状档 (★板面实读 · 不换 land★)★

| 位号 | 颗数 | 现状 land | 现状铜箔包络 X/Y 宽 | 座体必须清空区 X/Y 宽 | 开口 X/Y 宽 | 清空区口径来源 | 每边余量 (现状) | 最坏余量 (FDM ±0.30) | CRIT | 过/不过 | 证据等级 | 来源页 + 行号 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `J_BOOT1` | 1 | SMD 6 pad, pitch 0.50, 0.275x0.9 | 2.7750 × 0.9000 | [0数据] | [0数据] | `unknown` | [0数据] | [0数据] | 0.60 | 未建模 (挂 OI-6) | [实测]+[推算] | logs/iss377/board_connectors.json J_BOOT1 |
| `J_CHG` | 1 | SMD 2 pad, pitch 0.50, 0.275x0.9 | 0.7750 × 0.9000 | [0数据] | [0数据] | `unknown` | [0数据] | [0数据] | 0.60 | 未建模 (挂 OI-6) | [实测]+[推算] | logs/iss377/board_connectors.json J_CHG |
| `J_DEBUG` | 1 | SMD 4 pad, pitch 0.50, 0.275x0.900 自绘占位 (lib_id 空) | 1.7750 × 0.9000 | 1.7750 × 2.5400 | 10.2000 × 4.6000 | `copper_driven` (X) / `housing_driven` (Y) | 开口 4.2125/1.0300 ; 罩住 0.0000/0.8200 | 开口 3.9125/0.7300 ; 罩住 -0.3000/0.5200 | 0.60 | 红: 罩住Y | [实测]+[推算] | logs/iss377/board_connectors.json J_DEBUG; MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351 (X) + L183 (Y); MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352/L353 |
| `J_SOM_P1` | 1 | SMD 100 pad, pitch 0.40, 0.2x0.7 | 19.8000 × 3.7800 | [0数据] | [0数据] | `unknown` | [0数据] | [0数据] | 0.60 | 未建模 (挂 OI-6) | [实测]+[推算] | logs/iss377/board_connectors.json J_SOM_P1 |
| `J_SOM_P2` | 1 | SMD 100 pad, pitch 0.40, 0.2x0.7 | 19.8000 × 3.7800 | [0数据] | [0数据] | `unknown` | [0数据] | [0数据] | 0.60 | 未建模 (挂 OI-6) | [实测]+[推算] | logs/iss377/board_connectors.json J_SOM_P2 |
| `J_SOM_P3` | 1 | SMD 100 pad, pitch 0.40, 0.2x0.7 | 19.8000 × 3.7800 | [0数据] | [0数据] | `unknown` | [0数据] | [0数据] | 0.60 | 未建模 (挂 OI-6) | [实测]+[推算] | logs/iss377/board_connectors.json J_SOM_P3 |
| `J_SOM_P4` | 1 | SMD 100 pad, pitch 0.40, 0.2x0.7 | 19.8000 × 3.7800 | [0数据] | [0数据] | `unknown` | [0数据] | [0数据] | 0.60 | 未建模 (挂 OI-6) | [实测]+[推算] | logs/iss377/board_connectors.json J_SOM_P4 |
| `J_UART` | 1 | SMD 2 pad, pitch 0.50, 0.275x0.900 自绘占位 (lib_id 空) | 0.7750 × 0.9000 | 2.5400 × 2.5400 | 10.2000 × 4.6000 | `housing_driven` (X) / `housing_driven` (Y) | 开口 3.8300/1.0300 ; 罩住 0.8825/0.8200 | 开口 3.5300/0.7300 ; 罩住 0.5825/0.5200 | 0.60 | 红: 罩住X / 罩住Y | [实测]+[推算] | logs/iss377/board_connectors.json J_UART; MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346 (X) + L196 (Y); MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347/L348 |
| `J_USB_C` | 1 | SMD 16 pad, pitch 0.50, 0.3x1.15 | 7.8000 × 1.1500 | [0数据] | [0数据] | `unknown` | [0数据] | [0数据] | 0.60 | 未建模 (挂 OI-6) | [实测]+[推算] | logs/iss377/board_connectors.json J_USB_C |

### ★§1.2 换官方 land 档 (★只有两颗排针有官方 land 真值 · 其余 7 颗未建模不列★)★

| 位号 | 档 | 铜箔包络 X/Y 宽 (官方 land) | 座体必须清空区 X/Y 宽 | 开口 X/Y 宽 | 清空区口径来源 | 每边余量 | 最坏余量 (FDM ±0.30) | CRIT | 过/不过 | 来源页 + 行号 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `J_DEBUG` | official_tht_1x04 | 4.8100 × 1.0000 | 1.7750 × 2.5400 | 10.2000 × 4.6000 | `copper_driven` (X) / `housing_driven` (Y) | 开口 2.6950/1.0300 ; 罩住 -1.5175/0.7700 | 开口 2.3950/0.7300 ; 罩住 -1.8175/0.4700 | 0.60 | 红: 罩住X / 罩住Y | MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md §7 land_tht + §1.1 |
| `J_DEBUG` | official_smd_1x04 | 6.0000 × 4.4600 | 1.7750 × 2.5400 | 10.2000 × 4.6000 | `copper_driven` (X) / `copper_driven` (Y) | 开口 2.1000/0.0700 ; 罩住 -2.1125/-0.9600 | 开口 1.8000/-0.2300 ; 罩住 -2.4125/-1.2600 | 0.60 | 红: 开口Y / 罩住X / 罩住Y | MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md §7 land_smd + §3 |
| `J_UART` | official_tht_1x02 | 2.2700 × 1.0000 | 2.5400 × 2.5400 | 10.2000 × 4.6000 | `housing_driven` (X) / `housing_driven` (Y) | 开口 3.8300/1.0300 ; 罩住 0.1350/0.7700 | 开口 3.5300/0.7300 ; 罩住 -0.1650/0.4700 | 0.60 | 红: 罩住X / 罩住Y | MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md §1.2 + §2 (S1) |
| `J_UART` | official_smd_1x02 | 1.9200 × 6.0000 | 2.5400 × 2.5400 | 10.2000 × 4.6000 | `housing_driven` (X) / `copper_driven` (Y) | 开口 3.8300/-0.7000 ; 罩住 0.3100/-1.7300 | 开口 3.5300/-1.0000 ; 罩住 0.0100/-2.0300 | 0.60 | 红: 开口Y / 罩住X / 罩住Y | MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md §1.3 + §2 (S2) |

### ★§1.3 读法 (★三句★)★

★**① 「未建模 (挂 OI-6)」不是「过」**: ★**那 7 颗 (`J_BOOT1` / `J_CHG` / `J_SOM_P1..P4` / `J_USB_C`) 在既有真相页里根本没有必须清空区与开口 ⇒ ④⑤ 算不出 ⇒ 本单【不许】把「算不出」写成「过」** ★
★**② `copper_driven` 行的罩住轴是同义反复**: ★**`J_DEBUG` 现状的 `Hx == Cx` ⇒ 罩住 X 余量 `0.0000` (最坏 `-0.3000`) 是模型定义出来的, 不是物理事实 ⇒ 不作判据 (登记 OI-5); 但只要 `C` 一换 (换官方 land), 罩住轴立刻变成真判据 (见 §1.2)** ★
★**③ 每行都同时给 ④ 与 ⑤**: ★**只给一个口径就是同源化失败 ⇒ 表里没有「只给一个」的行★** ★

---

## ★§2 冲突清单 (★本单最有价值的第二件产物★)★

★**每条都写**: ★**冲突是什么 / 为什么会撞 / 后果句 (事实层) / 判据句 (方向层) / 候选解法 + 代价 (不代拍) / 要谁回答什么** ★
★**★后果句与判据句必须分开写·不许混成一句含混的「过」★ (★ISS-371 立下的口径纪律·本单继承·闸 K4 专查这条★)★**

### ★★C1 · 同族两颗排针, 分母不同 ⇒ 方向相反 (★ISS-374 亲手立的病根·本单继承★)★★

★**冲突是什么**: ★**`J_DEBUG` 的余量是 ④ (开口口径: `(开口宽 − 铜箔宽)/2`) ; `J_UART` 的余量是 ⑤ (罩住口径: `(座体清空区宽 − 铜箔宽)/2`) ⇒ 同名不同义** ★
★**为什么会撞**: ★**`J_DEBUG` 换官方 THT 后铜箔 X `4.8100` ⇒ ④ = `2.6950` 过阈 ; `J_UART` 换官方 THT 后铜箔 X `2.2700` ⇒ ⑤ = `0.1350` 不过阈 ⇒ ★**两颗件一个绿一个红, 但两者的「余量」根本不是同一个量** ★
★**★后果句 (事实层)**: ★**若那一趟按 `B33` 把 `J_UART` 也换成官方 land, 则铜箔每边只剩 `0.1350` (最坏 `-0.1650`) 余量 ⇒ 铜箔不再被座体必须清空区完全罩住 ⇒ 结构件装不上** ★
★**★判据句 (方向层)**: ★**在同源判据下, `J_UART` 罩住余量 `0.1350` < `CRIT` `0.60` ⇒ 不过阈 ; `J_DEBUG` 开口余量 `2.6950` ≥ `CRIT` ⇒ 过阈 ⇒ ★**方向相反这件事是真的, 但它此前被口径差异掩盖了** ★
★**候选解法 + 代价 (★不代拍★)**: ★**① 座体清空区放宽到 `3.4700`** ⇒ 结构件返工一次 + 板那一趟要同批改落点 ; ★**② `J_UART` 这一颗不换 land** ⇒ 结构件零返工, 但 `B33` 范围要改 (归 main) ; ★**③ `J_UART` 换 X 宽 ≤ `1.3400` 的 1×2 排针** ⇒ 结构件零返工 + 板那一趟只动 `J_DEBUG`, 但选型与 pad 序要另开一单** ★
★**要谁回答什么**: ★**main 回答「`B33_PIN_LAND_1P27` 的范围是只含 `J_DEBUG`, 还是含 `J_DEBUG` + `J_UART`?」 (OI-2)** ★

### ★★C2 · 余量不是一个标量, 是一对向量: 支配方会从 X 换到 Y (★只看一个轴就会漏★)★★

★**冲突是什么**: ★**同一件在三档之间, 支配方会换人: `J_UART` 换 SMD 变体后, 铜箔 Y 宽 `6.0000` 直接撞开口 Y (每边越界 `0.7000`) ⇒ 支配方从 X 转到 Y** ★
★**为什么会撞**: ★**`J_UART` 现状与 THT 档的铜箔 Y 宽 (`0.9000` / `1.0000`) 都远小于座体清空区 Y `2.5400` ⇒ Y 轴在现状看不出问题 ; 一换 SMD 变体, Y 轴的铜箔包络 `6.0000` 比开口 Y `4.6000` 还大 ⇒ 只看 X 的话 (X 罩住余量 `0.3100` 名义过阈) 会误判为「小问题」** ★
★**★后果句 (事实层)**: ★**`J_UART` 换官方 SMD 变体 (`Pin1Left`/`Pin1Right`) 后, 铜箔 Y 包络 `6.0000` ⇒ 居中后上下各越出开口 Y `0.7000` ⇒ 装配当场干涉 ; 同档 X 罩住余量最坏只有 `0.0100` ⇒ 两轴同时红** ★
★**★判据句 (方向层)**: ★**`J_UART` SMD 档: 开口 Y 余量 `-0.7000` (最坏 `-1.0000`) < `CRIT` `0.60` ⇒ 不过阈 ; 罩住 X 余量 `0.3100` (最坏 `0.0100`) < `CRIT` ⇒ 不过阈 ⇒ ★**两轴都判才拦得住** ★
★**★姊妹件同样中招 (★本单新增的一条·★ISS-371 §3 只报了 Y 不够, 没报 X 是绿的★)★**: ★**`J_DEBUG` 换官方 SMD 变体后, 开口 X 余量 `2.1000` (最坏 `1.8000`) **过阈**, 但开口 Y 余量 `0.0700` (最坏 `-0.2300`) **不过阈** ⇒ ★**这是全表里唯一一行「X 绿 Y 红」⇒ 闸 K3 就用它证明闸不是只判一个轴** ★
★**候选解法 + 代价 (★不代拍★)**: ★**① 两个 SMD 档整体弃用, 走 THT** ⇒ 代价 = `J_DEBUG` 的清空区要按 `4.8100` 重做 (`OI-5`) ; ★**② SMD 档要开口 Y ≥ 铜箔 Y `4.4600` + 2 × (`CRIT` + `TOL`) = `6.2600`** ⇒ 结构件开口规格重做 ; ★**③ `J_UART` SMD 档要开口 Y ≥ `6.0000` + 1.8000 = `7.8000`** ⇒ 结构件开口 Y 几乎翻倍** ★
★**要谁回答什么**: ★**main 回答「同源表 §1.2 的两个 SMD 档要不要在 `B33` 里写成『禁用变体』?」 (OI-2)** ★

### ★★C3 · 同一位号的「必须清空区 X 宽」在仓里有三个数 (★追加发现·本单实测)★★

★**冲突是什么**: ★**`J_DEBUG` 的必须清空区 X 宽, 仓里同时存在三个值**: ★**`1.7750`** (★真相页 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` L351「座体宽 1.775 = 板读铜箔宽」★) · ★**`4.0850`** (★现页四处: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L326 / `MECH/BOARD_ONEPASS_MECH_SYNC.md` L561 / `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` L50 / `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` L175★) · ★**`4.8100`** (★官方 THT 真值, ISS-371 §1.1★) ★
★**为什么会撞**: ★**三个数都自称「必须清空区 X 宽」, 但来源分别是「现状铜箔宽」/「把现状铜箔宽搬到 1.27 pitch 上」/「官方 THT 真 land」⇒ 没有单一真源 ⇒ 结构件按哪个出件, 决定它会不会当场干涉** ★
★**★后果句 (事实层)**: ★**若结构件按真相页 `1.7750` 留, 则 `J_DEBUG` 换官方 THT 后铜箔每边超出清空区 `1.5175` ; 若按现页 `4.0850` 留, 则每边超出 `0.3625` (ISS-371 §2.2 的数) ⇒ ★**两个数都红, 但差 4.18 倍 ⇒ 结构件返工范围完全取决于按哪个数出件** ★
★**★判据句 (方向层)**: ★**罩住余量 = `(H − C)/2` ⇒ `H < C` 即负余量 ⇒ 三个数里, 只有取到 ≥ `4.8100` 的那个才能让 `J_DEBUG` 的罩住轴过阈 ⇒ ★**「必须清空区」这三个数必须先定死一个, 否则同源表第一行就是空的** ★
★**候选解法 + 代价 (★不代拍★)**: ★**① 以官方 THT 真 land 为准 (`4.8100`) ⇒ 结构件按 `4.8100` 出件, 与板那一趟同批定死** ; ★**② 以座体物理占位为准 (`F.Fab` 旋转后 `5.0800` / courtyard `6.0900`, ISS-371 §1.3) ⇒ 结构件要多让 `0.2700`/边 (选 `6.0900` 则 Y 向两档要红, 开口 Y 必须同时放大)** ; ★**③ 维持现页 `4.0850` ⇒ 板那一趟换 land 后每边越界 `0.3625` ⇒ 不成立** ★
★**要谁回答什么**: ★**main 回答「`J_DEBUG` 的『必须清空区 X 宽』以哪一个数为准 (`1.7750` / `4.0850` / `4.8100`)?」 (OI-5)** ★

### ★★C4 · 口径来源在【一颗件内部】就会分叉 (X 铜箔支配 / Y 座体支配) + 全板 9 颗只有 2 颗建了模 (★追加发现·本单实测)★★

★**冲突是什么**: ★**`J_DEBUG` 的 X 轴 `Hx == Cx` (口径来源 `copper_driven`) 而 Y 轴 `Hy 2.5400 > Cy 0.9000` (口径来源 `housing_driven`) ⇒ ★**「一颗件一个口径来源」这个假设在板面上就站不住** ★ ; 且 ★**9 颗连接器里只有 2 颗 (`J_DEBUG` / `J_UART`) 在真相页里有必须清空区, 其余 7 颗口径来源 = `unknown`** ★
★**为什么会撞**: ★**若「清空区口径来源」这一列按单值写, `J_DEBUG` 的 Y 轴真实口径 (`housing_driven`) 会被 X 轴的 `copper_driven` 掩盖 ⇒ §1.1 的罩住 Y 余量 `0.8200` (最坏 `0.5200`) 这条红会被吃掉** ★
★**★后果句 (事实层)**: ★**`J_UART` 现状罩住 Y 余量最坏 `0.5200` < `CRIT` `0.60` ⇒ 现状这一颗在同源表上就是红的 (ISS-374 §2 只按「铜箔比座体窄 ⇒ Y 不构成卡点」的包含关系判 Y, 没按余量判) ; 其余 7 颗连「红还是绿」都判不了** ★
★**★判据句 (方向层)**: ★**罩住余量 `0.5200` < `CRIT` `0.60` ⇒ 不过阈 ; `unknown` 行的判决是「未建模」, 不是「过」⇒ ★**表不许把这 7 颗写成绿** ★
★**候选解法 + 代价 (★不代拍★)**: ★**① 把「口径来源」列改成逐轴 (本单已改) ⇒ 零成本** ; ★**② 把罩住口径是否对全部连接器一律适用交上去裁 (OI-8) ⇒ 老板 + main ; ★**③ 给其余 7 颗补建必须清空区模型 (先补板面 fab 外框, 再补厂商 keepout) ⇒ 一轮建模 + 逐颗找厂商图纸 (OI-6 / OI-10)** ★
★**要谁回答什么**: ★**boss 回答「罩住口径 (座体必须清空区 vs 铜箔 ≥ `CRIT`) 是否对全部连接器一律适用?」 (OI-8) ; main 回答「其余 7 颗的必须清空区模型由谁补、什么时候补?」 (OI-6)** ★

---

## ★§3 座体真实型号自查 (★全靠自己查·★查不到给降级方案·★不挂起★)★

★**自查口径**: ★**① 板面实读 ⇒ `logs/iss377/board_connectors.json` 的 `value` 字段 (★这是板子自己写的型号字符串·★最硬的板面证据★) ; ② 既有已签收页里已实读过的官方 land 真值 (★ISS-371 §0.1/§0.2 / ISS-374 §1.2/§1.3·★只读引用·★不重查★) ; ③ 本机无厂商图纸者一律 `[0数据]` + 降级方案 (★本单零外发·★不把活推给外部·★不等待外部答复★) ★

### ★§3.1 逐颗自查结果 (★证据等级逐颗标★)★

| 位号 | 板面 `value` 字符串 (★实读★) | 厂商料号 | 官方必须清空区 / keepout 尺寸 | 证据等级 | 复跑 |
|---|---|---|---|---|---|
| ★`J_DEBUG` ★ | ★`1×4 1.27mm 排针 (JTAG)` ★ | ★**无厂商料号** (★板面只写了规格族, 没写厂商/型号★) | ★**`[0数据]`** (★本机无该座体的厂商图纸★) | ★`[实测]`(字符串) + ★`[0数据]`(料号/keepout) ★ | ★`jq -r '.J_DEBUG.value' logs/iss377/board_connectors.json` ★ |
| ★`J_UART` ★ | ★`1×2 1.27mm 排针 (UART)` ★ | ★**无厂商料号** ★ | ★**`[0数据]`** ★ | ★`[实测]`(字符串) + ★`[0数据]`(料号/keepout) ★ | ★`jq -r '.J_UART.value' logs/iss377/board_connectors.json` ★ |
| ★`J_SOM_P1..P4` ★ | ★`Hirose DF40C-100DS-0.4V(51) 100pin 0.4mm (SOM P*)` ★ | ★**`Hirose DF40C-100DS-0.4V(51)`** (★板面写死★) | ★**`[0数据]`** (★本机无 Hirose 该料号的 keepout / 座体占位图纸★) | ★`[实测]`(料号) + ★`[0数据]`(keepout) ★ | ★`jq -r '.J_SOM_P1.value' logs/iss377/board_connectors.json` ★ |
| ★`J_USB_C` ★ | ★`GCT USB4105-16P USB-C 电源口 (自绘, 原厂图纸 Rev B3)` ★ | ★**`GCT USB4105-16P`** (★板面写死★) ★ | ★**`[0数据]`** (★板面注明「原厂图纸 Rev B3」, 但该图纸不在本仓·★本单零外发·★只登记★) ★ | ★`[实测]`(料号) + ★`[0数据]`(keepout) ★ | ★`jq -r '.J_USB_C.value' logs/iss377/board_connectors.json` ★ |
| ★`J_CHG` ★ | ★`SoM BTB CHG (100pin, 部分已分配)` ★ | ★**`[0数据]`** (★与 SoM 同族, 但板面未写厂商/型号★) | ★**`[0数据]`** ★ | ★`[实测]`(字符串) + ★`[0数据]`(料号/keepout) ★ | ★`jq -r '.J_CHG.value' logs/iss377/board_connectors.json` ★ |
| ★`J_BOOT1` ★ | ★`启动存储焊盘位 (4p 信号 + 2p 电源/GND 预留)` ★ | ★**不适用** (★板面位置是焊盘位, 不是座体★) | ★**不适用** ★ | ★`[实测]`(字符串) ★ | ★`jq -r '.J_BOOT1.value' logs/iss377/board_connectors.json` ★ |

★**★结论 (★一句话)★**: ★**9 颗连接器里, 只有 2 颗 (`J_SOM_P1..P4` 的 Hirose 料号 + `J_USB_C` 的 GCT 料号) 在板面上写死了厂商料号; ★`J_DEBUG` 与 `J_UART` 这两颗正是本单的病根, 它们恰好【没有厂商料号】⇒ 座体真实型号 = `[0数据]` (★与 ISS-267 F-8 一致·★不是本单查不出来, 是本机上就没有★)** ★

### ★§3.2 降级方案 (★查不到处的必须项·★不是可选项★)★

| # | 方案 | 依据 | 代价 | 影响哪颗件 |
|---|---|---|---|---|
| ★**DP-1** ★ | ★**按最坏值设计: 座体必须清空区取两档里的较大值** ⇒ `J_UART` 的 X 清空区从 `2.5400` 放到 `3.4700` (= `2.2700` + 2 × `CRIT` `0.60`) ⇒ 结构件按 `3.4700` 出件 ★ | ★ISS-374 §3.2 方案 ① + 本单 §1.2 同源表 (罩住余量公式) ★ | ★**结构件必须返工一次** (清空区 X 宽 `+0.9300`, 中心 `18.8900` 不变) ; 板那一趟要同批把落点挪到 `(18.2550, 68.6000)` ⇒ 撞「板只改一次」风险 ★ | ★`J_UART` (★`J_DEBUG` 不受此条影响, 它的真值已经是 `4.8100`★) ★ |
| ★**DP-2** ★ | ★**选官网参数直接满足的替代型号: `J_UART` 换 X 宽 ≤ `1.3400` 的 1×2 排针** (= `2.5400` − 2 × `CRIT` `0.60`) ⇒ 结构件清空区一个数都不改 ★ | ★ISS-374 §3.2 方案 ③ + 本单 §0.1 公式 ⑦ ★ | ★**选型与 pad 序要另开一单** (★pad 序对调是板侧 + 硬件侧的活, 本单不代拍★) ; `B33` 要把 `J_UART` 排除在换 land 名单外 ★ | ★`J_UART` ★ |
| ★**DP-3** ★ | ★**改设计路径绕开: 这两颗调试排针改走板边贴片 / 换出线方式** (★例如改成贴片排针或直接引出测试点, 不再走通孔排针★) ★ | ★本单 §1.2 (两个 SMD 档的 Y 向红灯) + ISS-371 §3 / ISS-374 §2 (SMD 变体 Y 撞开口) ★ | ★**SMD 变体 Y 向撞开口 ⇒ 开口规格要重做** (`J_UART` SMD 档要开口 Y ≥ `7.8000`, 现口径 `4.6000`) ⇒ 结构件开口几乎翻倍 ; 且 `J_DEBUG` SMD 档的 X 方向是绿的 (最坏 `1.8000`) ⇒ **不是全无解, 但要按 Y 向重算开口** ★ | ★`J_DEBUG` + `J_UART` ★ |
| ★**DP-4** ★ | ★**给其余 7 颗连接器补建「座体必须清空区」模型 (★本单新增的第 4 条降级候选·因为它们的 `[0数据]` 不是两颗排针的问题★)** ★ | ★本单 §1.1 (7 行口径来源 = `unknown`) + §3.1 (厂商料号可从板面拿到) ★ | ★**一轮建模 + 逐颗找厂商图纸** (★`J_SOM_P1..P4` 的 Hirose keepout 与 `J_USB_C` 的 GCT Rev B3 图纸都不在本仓⇒ 靠下一单能拿到资料的入口补, 本单只登记型号与缺口★) ; 补齐前这 7 颗的净距判决一律是「未建模」 ★ | ★`J_BOOT1` · `J_CHG` · `J_SOM_P1..P4` · `J_USB_C` ★ |

---

## ★§4 未决项 (★只登记 · 不代拍 · 每条给「要谁回答什么」★)★

| # | 未决项 | 要谁回答什么 | 为什么本单不能回答 | 代价 / 期限 |
|---|---|---|---|---|
| ★**OI-1** ★ | ★**座体必须清空区按 `2.5400` 还是 `3.4700` 出件** (★`J_UART`★) | ★**boss (结构口径) + mech-lead (结构件) 回答: 「`J_UART` 座体必须清空区 X 宽按 `2.5400` 还是按 `3.4700` 出件?」** ★ | ★**座体真实型号 = `[0数据]` (ISS-267 F-8) ⇒ `2.5400` 本身是 MECH 现行模型假设, 不是实物** ★ | ★**结构件返工 ⇒ 必须与板那一趟同批定, 否则撞「板只改一次」** ★ |
| ★**OI-2** ★ | ★**那一趟 `B33` 换 land 的范围** | ★**main 回答: 「`B33_PIN_LAND_1P27` 的范围是只含 `J_DEBUG`, 还是含 `J_DEBUG` + `J_UART`?」** ★ | ★**板那一趟的裁决权在 main; 本单只给结构侧代价与判据, 不代 main 裁** ★ | ★**与 ISS-373/374 同一件事的两条腿; 本单是结构侧那条腿** ★ |
| ★**OI-3** ★ | ★**`J_UART` 换 land 的落点挪 `(18.2550, 68.6000)` 认不认** | ★**hw-lead 回答: 「`J_UART` 换 land 时落点挪到 `(18.2550, 68.6000)`, 认不认?」** ★ | ★**本单是结构侧, 不落表 (★零落表边界★)** ★ | ★**不认 ⇒ 铜箔整块落在座体清空区之外 ⇒ 装配当场干涉 (ISS-374 §3.1)** ★ |
| ★**OI-4** ★ | ★**同源化后的这张表要不要进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md`** | ★**main 回答: 「§1 这张同源总表要不要以追加块的形式落进板侧作业包?」** ★ | ★**挂不挂归 main; 本单边界 = 零改既有页面正文** ★ | ★**挂进去 ⇒ 板那一趟有一张唯一口径表可用 ; 不挂 ⇒ 结构侧与板侧各持一份, 下一次还要再同源化一遍** ★ |
| ★**OI-5** ★ | ★**`J_DEBUG` 的「必须清空区 X 宽」以哪个数为准: `1.7750` / `4.0850` / `4.8100`** | ★**main 回答: 「`J_DEBUG` 的『必须清空区 X 宽』取哪一个?」** ★ | ★**三个数在仓里并存 (C3); 本单只登记, 不代拍** ★ | ★**取 `1.7750` ⇒ 每边越界 `1.5175` ; 取 `4.0850` ⇒ 每边越界 `0.3625` ⇒ 结构件返工范围差 4.18 倍** ★ |
| ★**OI-6** ★ | ★**其余 7 颗连接器的「座体必须清空区」未建模 (口径来源 `unknown`)** | ★**main 回答: 「这 7 颗的必须清空区模型由谁补、什么时候补?」 ; mech-lead 回答: 「补模型时要不要把 §0.1 的 ③④⑤ 三条一起补?」** ★ | ★**本单只做了全板扫描与登记 (DP-4)** ★ | ★**补齐前这 7 颗的净距判决 = 「未建模」, 不许当绿用** ★ |
| ★**OI-7** ★ | ★**座体真实高 `h` (三档 `0.90` / `2.54` / `4.00`)** | ★**boss 回答: 「`h` 走三档参数化, 还是定版一个值锁死?」** ★ | ★**`h` 本身 = `[0数据]` (ISS-267 F-8); 本单 §1 统一用真相页的固定开口 Y `4.6000` (同源), ISS-371 的 `h` 三档口径另列 (OI 登记)** ★ | ★**定版 ⇒ 结构件一次出件 ; 继续三档 ⇒ 结构件按最坏档出件** ★ |
| ★**OI-8** ★ | ★**罩住口径 (座体必须清空区 vs 铜箔 ≥ `CRIT`) 是否对全部连接器一律适用** | ★**boss + main 回答: 「⑤ 这一条是对全部连接器一律判, 还是只对座体模型可信的连接器判?」** ★ | ★**本单把 ④⑤ 两条同时列出来, 但不代裁哪条是准绳** ★ | ★**一刀切 ⇒ 现状 `J_UART`/`J_DEBUG` 的罩住轴都红 ; 只对座体可信者判 ⇒ 其余 7 颗继续「未建模」** ★ |
| ★**OI-9** ★ | ★**`J_UART` 现状 Y 向罩住余量最坏 `0.5200` < `CRIT` (ISS-374 未算这一条)** | ★**boss + mech-lead 回答: 「这条要不要写进 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.5 的追加订正块?」** ★ | ★**本单边界 = 零改既有页面正文 ⇒ 订正块只写在本页 §1.1, 由 main 决定要不要往既有页落** ★ | ★**差 `0.0800` (最坏口径) ⇒ 若最终口径改 `TOL` 或 `CRIT`, 这条要重算** ★ |
| ★**OI-10** ★ | ★**座体真实厂商料号 (★两颗排针没有, 两族有★)** | ★**hw-lead 回答: 「`J_DEBUG` / `J_UART` 用哪颗具体厂商型号? `J_SOM_P1..P4` 与 `J_USB_C` 的厂商 keepout 图纸从哪里补?」** ★ | ★**本单零外发 ⇒ 只登记板面已写死的料号与缺口, 不去要资料** ★ | ★**`J_DEBUG`/`J_UART` 型号定版 ⇒ OI-1 的 `2.5400` vs `3.4700` 才有实物依据 ; SoM/USB-C 的 keepout 补齐 ⇒ OI-6 才能推进** ★ |

---

## ★§5 复跑命令 (★本单全部·★必跑·★rc 见交卷页 B6★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★本单新建闸 (★只读·★判据 K0~K8★)★
python3 MECH/check_connector_clearance_caliber.py              # rc=0
python3 MECH/check_connector_clearance_caliber.py --selftest   # rc=0 · 末行 ALL TESTS PASS

# ★同源表生成器 (★沙盒·★只落 tmp/iss377/★)★
python3 tmp/iss377/gen_table.py                                # rc=0 · 重出 §1 表 + 机器块

# ★既有闸回归 (★只跑不改·★证明零漂移★)★
python3 MECH/check_jdebug_1p27_clearance.py                     # rc=0
python3 MECH/check_juart_1p27_clearance.py                      # rc=0

# ★板面实读 (★座体/连接器逐颗读数·★§1 表的铜箔列真身★)★
jq -r 'to_entries[] | "\(.key)\t\(.value.npads)\t\(.value.pitch)\t\(.value.copper_x_width)\t\(.value.copper_y_width)\t\(.value.value)"' logs/iss377/board_connectors.json

# ★真相页真身 (★H / O / 口径来源的出处·★逐行行号★)★
grep -nE '调试口 · 必须清空区|检修口 · 必须清空区|调试口 · 开口|检修口 · 开口' MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md

# ★CRIT / TOL 真身 (★只读引用·★不写死·★闸从这取★)★
grep -nE 'CRIT|TOL\["fdm_part"\]' MECH/service_port_check.py

# ★零写板 + 零挂链 自证★
md5sum HW/PCB/demo_mainboard.kicad_pcb                           # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                 # 必须 2026-11-06 07:07:17.362193413 / 4940213
grep -c check_connector_clearance_caliber state/gate_check.py   # 必须输出 0
```

---

## ★§6 边界自证 (★逐条★)★

| 边界 | 怎么自证 | 结果 |
|---|---|---|
| ★**零写板** ★ | ★板 md5 / mtime / size 开工前 + 交卷后各打一次 (★三项 == 基线★) ★ | ★`[实测]` = `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213` ★ |
| ★**零落表** ★ | ★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 一字不碰 ★ | ★`[实测]` ★ |
| ★**零改既有闸** ★ | ★`MECH/check_jdebug_1p27_clearance.py` / `MECH/check_juart_1p27_clearance.py` / `MECH/service_port_check.py` / `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改 ★ | ★`[实测]` (闸 K7 逐字节 md5 比对) ★ |
| ★**零改已签收页正文** ★ | ★`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` / `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` / `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 只读引用, 一字不改 ★ | ★`[实测]` (闸 K7 逐字节 md5 比对) ★ |
| ★**零改其它 `MECH/BOARD_ONEPASS_*` 页** ★ | ★本单只新建本页一个 `MECH/BOARD_ONEPASS_*` 文件 ★ | ★`[实测]` ★ |
| ★**零挂链** ★ | ★本单新建的闸**不**进 `state/gate_check.py` ★ | ★`[实测]` = `grep -c check_connector_clearance_caliber state/gate_check.py` ⇒ `0` (闸 K8) ★ |
| ★**零外发** ★ | ★不发邮件 / 不询价 / 不问询 / 不采购 ; 缺口一律自己查 + 标证据等级 + 查不到写降级方案 (§3.2 DP-1~DP-4) ★ | ★`[实测]` ★ |
| ★**不代老板拍板** ★ | ★OI-1~OI-10 只登记 + 给候选解法与代价 ; 本页正文无「已决定 / 应改」式裁决语 ★ | ★`[实测]` ★ |
| ★**不自签 `state/issue_log.yaml`** ★ | ★台账由 main 签收 ★ | ★`[实测]` ★ |
| ★**沙盒只落两处** ★ | ★`tmp/iss377/` + `logs/iss377/` ★ | ★`[实测]` ★ |
| ★**零改判据阈值** ★ | ★`CRIT` / `TOL` 只从 `MECH/service_port_check.py` 读取, 本页与闸都不写死 ★ | ★`[实测]` (闸 K2 现场解析 `CRIT == 2 × TOL["fdm_part"]`) ★ |

---

## ★§7 机器可读 JSON 块 (★`MECH/check_connector_clearance_caliber.py` 只认这块★)★

<!-- MECH-CONNECTOR-CLEARANCE-CALIBER-JSON-BEGIN -->

```json
{
 "schema": "mech.connector.clearance.caliber.v1",
 "issue": "ISS-377",
 "agent": "mech-lead",
 "updated": "2026-11-24",
 "caliber": {
  "formula": "M = max(H_housing, C_copper) per axis; margin_open = (O_opening - M)/2; margin_cover = (H_housing - C_copper)/2; worst = margin - TOL['fdm_part']; pass iff worst >= CRIT",
  "crit_source": "MECH/service_port_check.py L126-L127 (CRIT = 2 * TOL['fdm_part'])",
  "axes": [
   "x",
   "y"
  ]
 },
 "rows": [
  {
   "ref": "J_BOOT1",
   "tier": "status_quo",
   "copper": {
    "x": 2.775,
    "y": 0.9
   },
   "land": "SMD 6 pad, pitch 0.50, 0.275x0.9",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-6"
   ],
   "note": "",
   "source_refs": [
    "logs/iss377/board_connectors.json J_BOOT1"
   ],
   "housing": null,
   "opening": null,
   "merged": null,
   "caliber_source": "unknown",
   "caliber_source_axes": {
    "x": "unknown",
    "y": "unknown"
   },
   "margin_open": null,
   "worst_open": null,
   "pass_open": null,
   "pass_worst_open": null,
   "margin_cover": null,
   "worst_cover": null,
   "pass_cover": null,
   "pass_worst_cover": null,
   "cover_tautology": null,
   "verdict": "未建模 (口径来源 unknown)"
  },
  {
   "ref": "J_CHG",
   "tier": "status_quo",
   "copper": {
    "x": 0.775,
    "y": 0.9
   },
   "land": "SMD 2 pad, pitch 0.50, 0.275x0.9",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-6"
   ],
   "note": "",
   "source_refs": [
    "logs/iss377/board_connectors.json J_CHG"
   ],
   "housing": null,
   "opening": null,
   "merged": null,
   "caliber_source": "unknown",
   "caliber_source_axes": {
    "x": "unknown",
    "y": "unknown"
   },
   "margin_open": null,
   "worst_open": null,
   "pass_open": null,
   "pass_worst_open": null,
   "margin_cover": null,
   "worst_cover": null,
   "pass_cover": null,
   "pass_worst_cover": null,
   "cover_tautology": null,
   "verdict": "未建模 (口径来源 unknown)"
  },
  {
   "ref": "J_DEBUG",
   "tier": "status_quo",
   "copper": {
    "x": 1.775,
    "y": 0.9
   },
   "land": "SMD 4 pad, pitch 0.50, 0.275x0.900 自绘占位 (lib_id 空)",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-5",
    "OI-7",
    "OI-8"
   ],
   "note": "",
   "source_refs": [
    "logs/iss377/board_connectors.json J_DEBUG",
    "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351 (X) + L183 (Y)",
    "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352/L353"
   ],
   "housing": {
    "x": 1.775,
    "y": 2.54,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351 (X) + L183 (Y)"
   },
   "opening": {
    "x": 10.2,
    "y": 4.6,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352/L353"
   },
   "merged": {
    "x": 1.775,
    "y": 2.54
   },
   "caliber_source": "copper_driven",
   "caliber_source_axes": {
    "x": "copper_driven",
    "y": "housing_driven"
   },
   "margin_open": {
    "x": 4.2125,
    "y": 1.03
   },
   "worst_open": {
    "x": 3.9125,
    "y": 0.73
   },
   "pass_open": {
    "x": true,
    "y": true
   },
   "pass_worst_open": {
    "x": true,
    "y": true
   },
   "margin_cover": {
    "x": 0.0,
    "y": 0.82
   },
   "worst_cover": {
    "x": -0.3,
    "y": 0.52
   },
   "pass_cover": {
    "x": false,
    "y": true
   },
   "pass_worst_cover": {
    "x": false,
    "y": false
   },
   "cover_tautology": {
    "x": true,
    "y": false
   },
   "verdict": "红: 罩住Y"
  },
  {
   "ref": "J_SOM_P1",
   "tier": "status_quo",
   "copper": {
    "x": 19.8,
    "y": 3.78
   },
   "land": "SMD 100 pad, pitch 0.40, 0.2x0.7",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-6"
   ],
   "note": "",
   "source_refs": [
    "logs/iss377/board_connectors.json J_SOM_P1"
   ],
   "housing": null,
   "opening": null,
   "merged": null,
   "caliber_source": "unknown",
   "caliber_source_axes": {
    "x": "unknown",
    "y": "unknown"
   },
   "margin_open": null,
   "worst_open": null,
   "pass_open": null,
   "pass_worst_open": null,
   "margin_cover": null,
   "worst_cover": null,
   "pass_cover": null,
   "pass_worst_cover": null,
   "cover_tautology": null,
   "verdict": "未建模 (口径来源 unknown)"
  },
  {
   "ref": "J_SOM_P2",
   "tier": "status_quo",
   "copper": {
    "x": 19.8,
    "y": 3.78
   },
   "land": "SMD 100 pad, pitch 0.40, 0.2x0.7",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-6"
   ],
   "note": "",
   "source_refs": [
    "logs/iss377/board_connectors.json J_SOM_P2"
   ],
   "housing": null,
   "opening": null,
   "merged": null,
   "caliber_source": "unknown",
   "caliber_source_axes": {
    "x": "unknown",
    "y": "unknown"
   },
   "margin_open": null,
   "worst_open": null,
   "pass_open": null,
   "pass_worst_open": null,
   "margin_cover": null,
   "worst_cover": null,
   "pass_cover": null,
   "pass_worst_cover": null,
   "cover_tautology": null,
   "verdict": "未建模 (口径来源 unknown)"
  },
  {
   "ref": "J_SOM_P3",
   "tier": "status_quo",
   "copper": {
    "x": 19.8,
    "y": 3.78
   },
   "land": "SMD 100 pad, pitch 0.40, 0.2x0.7",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-6"
   ],
   "note": "",
   "source_refs": [
    "logs/iss377/board_connectors.json J_SOM_P3"
   ],
   "housing": null,
   "opening": null,
   "merged": null,
   "caliber_source": "unknown",
   "caliber_source_axes": {
    "x": "unknown",
    "y": "unknown"
   },
   "margin_open": null,
   "worst_open": null,
   "pass_open": null,
   "pass_worst_open": null,
   "margin_cover": null,
   "worst_cover": null,
   "pass_cover": null,
   "pass_worst_cover": null,
   "cover_tautology": null,
   "verdict": "未建模 (口径来源 unknown)"
  },
  {
   "ref": "J_SOM_P4",
   "tier": "status_quo",
   "copper": {
    "x": 19.8,
    "y": 3.78
   },
   "land": "SMD 100 pad, pitch 0.40, 0.2x0.7",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-6"
   ],
   "note": "",
   "source_refs": [
    "logs/iss377/board_connectors.json J_SOM_P4"
   ],
   "housing": null,
   "opening": null,
   "merged": null,
   "caliber_source": "unknown",
   "caliber_source_axes": {
    "x": "unknown",
    "y": "unknown"
   },
   "margin_open": null,
   "worst_open": null,
   "pass_open": null,
   "pass_worst_open": null,
   "margin_cover": null,
   "worst_cover": null,
   "pass_cover": null,
   "pass_worst_cover": null,
   "cover_tautology": null,
   "verdict": "未建模 (口径来源 unknown)"
  },
  {
   "ref": "J_UART",
   "tier": "status_quo",
   "copper": {
    "x": 0.775,
    "y": 0.9
   },
   "land": "SMD 2 pad, pitch 0.50, 0.275x0.900 自绘占位 (lib_id 空)",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-1",
    "OI-7",
    "OI-8",
    "OI-9"
   ],
   "note": "",
   "source_refs": [
    "logs/iss377/board_connectors.json J_UART",
    "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346 (X) + L196 (Y)",
    "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347/L348"
   ],
   "housing": {
    "x": 2.54,
    "y": 2.54,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346 (X) + L196 (Y)"
   },
   "opening": {
    "x": 10.2,
    "y": 4.6,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347/L348"
   },
   "merged": {
    "x": 2.54,
    "y": 2.54
   },
   "caliber_source": "housing_driven",
   "caliber_source_axes": {
    "x": "housing_driven",
    "y": "housing_driven"
   },
   "margin_open": {
    "x": 3.83,
    "y": 1.03
   },
   "worst_open": {
    "x": 3.53,
    "y": 0.73
   },
   "pass_open": {
    "x": true,
    "y": true
   },
   "pass_worst_open": {
    "x": true,
    "y": true
   },
   "margin_cover": {
    "x": 0.8825,
    "y": 0.82
   },
   "worst_cover": {
    "x": 0.5825,
    "y": 0.52
   },
   "pass_cover": {
    "x": true,
    "y": true
   },
   "pass_worst_cover": {
    "x": false,
    "y": false
   },
   "cover_tautology": {
    "x": false,
    "y": false
   },
   "verdict": "红: 罩住X / 罩住Y"
  },
  {
   "ref": "J_USB_C",
   "tier": "status_quo",
   "copper": {
    "x": 7.8,
    "y": 1.15
   },
   "land": "SMD 16 pad, pitch 0.50, 0.3x1.15",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-6"
   ],
   "note": "",
   "source_refs": [
    "logs/iss377/board_connectors.json J_USB_C"
   ],
   "housing": null,
   "opening": null,
   "merged": null,
   "caliber_source": "unknown",
   "caliber_source_axes": {
    "x": "unknown",
    "y": "unknown"
   },
   "margin_open": null,
   "worst_open": null,
   "pass_open": null,
   "pass_worst_open": null,
   "margin_cover": null,
   "worst_cover": null,
   "pass_cover": null,
   "pass_worst_cover": null,
   "cover_tautology": null,
   "verdict": "未建模 (口径来源 unknown)"
  }
 ],
 "tier_rows": [
  {
   "ref": "J_DEBUG",
   "tier": "official_tht_1x04",
   "copper": {
    "x": 4.81,
    "y": 1.0
   },
   "land": "Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical (THT)",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-2",
    "OI-5",
    "OI-7",
    "OI-8"
   ],
   "note": "",
   "source_refs": [
    "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md §7 land_tht + §1.1"
   ],
   "housing": {
    "x": 1.775,
    "y": 2.54,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351 (X) + L183 (Y)"
   },
   "opening": {
    "x": 10.2,
    "y": 4.6,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352/L353"
   },
   "merged": {
    "x": 4.81,
    "y": 2.54
   },
   "caliber_source": "copper_driven",
   "caliber_source_axes": {
    "x": "copper_driven",
    "y": "housing_driven"
   },
   "margin_open": {
    "x": 2.695,
    "y": 1.03
   },
   "worst_open": {
    "x": 2.395,
    "y": 0.73
   },
   "pass_open": {
    "x": true,
    "y": true
   },
   "pass_worst_open": {
    "x": true,
    "y": true
   },
   "margin_cover": {
    "x": -1.5175,
    "y": 0.77
   },
   "worst_cover": {
    "x": -1.8175,
    "y": 0.47
   },
   "pass_cover": {
    "x": false,
    "y": true
   },
   "pass_worst_cover": {
    "x": false,
    "y": false
   },
   "cover_tautology": {
    "x": false,
    "y": false
   },
   "verdict": "红: 罩住X / 罩住Y"
  },
  {
   "ref": "J_DEBUG",
   "tier": "official_smd_1x04",
   "copper": {
    "x": 6.0,
    "y": 4.46
   },
   "land": "Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-2",
    "OI-5",
    "OI-7",
    "OI-8"
   ],
   "note": "",
   "source_refs": [
    "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md §7 land_smd + §3"
   ],
   "housing": {
    "x": 1.775,
    "y": 2.54,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L351 (X) + L183 (Y)"
   },
   "opening": {
    "x": 10.2,
    "y": 4.6,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L352/L353"
   },
   "merged": {
    "x": 6.0,
    "y": 4.46
   },
   "caliber_source": "copper_driven",
   "caliber_source_axes": {
    "x": "copper_driven",
    "y": "copper_driven"
   },
   "margin_open": {
    "x": 2.1,
    "y": 0.07
   },
   "worst_open": {
    "x": 1.8,
    "y": -0.23
   },
   "pass_open": {
    "x": true,
    "y": false
   },
   "pass_worst_open": {
    "x": true,
    "y": false
   },
   "margin_cover": {
    "x": -2.1125,
    "y": -0.96
   },
   "worst_cover": {
    "x": -2.4125,
    "y": -1.26
   },
   "pass_cover": {
    "x": false,
    "y": false
   },
   "pass_worst_cover": {
    "x": false,
    "y": false
   },
   "cover_tautology": {
    "x": false,
    "y": false
   },
   "verdict": "红: 开口Y / 罩住X / 罩住Y"
  },
  {
   "ref": "J_UART",
   "tier": "official_tht_1x02",
   "copper": {
    "x": 2.27,
    "y": 1.0
   },
   "land": "Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical (THT)",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-1",
    "OI-2",
    "OI-3",
    "OI-7",
    "OI-8"
   ],
   "note": "",
   "source_refs": [
    "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md §1.2 + §2 (S1)"
   ],
   "housing": {
    "x": 2.54,
    "y": 2.54,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346 (X) + L196 (Y)"
   },
   "opening": {
    "x": 10.2,
    "y": 4.6,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347/L348"
   },
   "merged": {
    "x": 2.54,
    "y": 2.54
   },
   "caliber_source": "housing_driven",
   "caliber_source_axes": {
    "x": "housing_driven",
    "y": "housing_driven"
   },
   "margin_open": {
    "x": 3.83,
    "y": 1.03
   },
   "worst_open": {
    "x": 3.53,
    "y": 0.73
   },
   "pass_open": {
    "x": true,
    "y": true
   },
   "pass_worst_open": {
    "x": true,
    "y": true
   },
   "margin_cover": {
    "x": 0.135,
    "y": 0.77
   },
   "worst_cover": {
    "x": -0.165,
    "y": 0.47
   },
   "pass_cover": {
    "x": false,
    "y": true
   },
   "pass_worst_cover": {
    "x": false,
    "y": false
   },
   "cover_tautology": {
    "x": false,
    "y": false
   },
   "verdict": "红: 罩住X / 罩住Y"
  },
  {
   "ref": "J_UART",
   "tier": "official_smd_1x02",
   "copper": {
    "x": 1.92,
    "y": 6.0
   },
   "land": "Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left",
   "evidence": "[实测]+[推算]",
   "open_items": [
    "OI-1",
    "OI-2",
    "OI-3",
    "OI-7",
    "OI-8"
   ],
   "note": "",
   "source_refs": [
    "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md §1.3 + §2 (S2)"
   ],
   "housing": {
    "x": 2.54,
    "y": 2.54,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L346 (X) + L196 (Y)"
   },
   "opening": {
    "x": 10.2,
    "y": 4.6,
    "source": "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md L347/L348"
   },
   "merged": {
    "x": 2.54,
    "y": 6.0
   },
   "caliber_source": "housing_driven",
   "caliber_source_axes": {
    "x": "housing_driven",
    "y": "copper_driven"
   },
   "margin_open": {
    "x": 3.83,
    "y": -0.7
   },
   "worst_open": {
    "x": 3.53,
    "y": -1.0
   },
   "pass_open": {
    "x": true,
    "y": false
   },
   "pass_worst_open": {
    "x": true,
    "y": false
   },
   "margin_cover": {
    "x": 0.31,
    "y": -1.73
   },
   "worst_cover": {
    "x": 0.01,
    "y": -2.03
   },
   "pass_cover": {
    "x": false,
    "y": false
   },
   "pass_worst_cover": {
    "x": false,
    "y": false
   },
   "cover_tautology": {
    "x": false,
    "y": false
   },
   "verdict": "红: 开口Y / 罩住X / 罩住Y"
  }
 ],
 "open_items": {
  "OI-1": "J_UART 座体必须清空区 X 宽按 2.5400 还是 3.4700 出件 (真实型号 [0数据], ISS-267 F-8) 归 boss + mech-lead",
  "OI-2": "B33_PIN_LAND_1P27 的范围: 只含 J_DEBUG 还是含 J_DEBUG + J_UART 归 main",
  "OI-3": "J_UART 换 land 落点挪到 (18.2550, 68.6000) 认不认 归 hw-lead",
  "OI-4": "同源总表要不要落进 HW/PCB/BOARD_ONEPASS_WORKPACKET.md 归 main",
  "OI-5": "J_DEBUG 的必须清空区 X 宽取 1.7750 / 4.0850 / 4.8100 哪一个 归 main",
  "OI-6": "其余 7 颗连接器必须清空区未建模 (口径来源 unknown) 由谁补 归 main + mech-lead",
  "OI-7": "座体真实高 h 三档 0.90 / 2.54 / 4.00 走参数化还是定版 归 boss",
  "OI-8": "罩住口径 (座体必须清空区 vs 铜箔 >= CRIT) 是否对全部连接器一律适用 归 boss + main",
  "OI-9": "J_UART 现状 Y 向罩住余量最坏 0.5200 < CRIT (ISS-374 未算) 要不要落进 PORT_OPENING 归 boss + mech-lead (main 决定落不落)",
  "OI-10": "座体真实厂商料号 (J_DEBUG/J_UART 无; J_SOM_P1..P4 = Hirose DF40C-100DS-0.4V(51); J_USB_C = GCT USB4105-16P) 归 hw-lead"
 },
 "degrade_plans": [
  {
   "id": "DP-1",
   "title": "按最坏值设计 (座体必须清空区取两档较大值)",
   "basis": "J_UART X 清空区 2.5400 -> 3.4700 (= 2.2700 + 2 x CRIT 0.60)",
   "cost": "结构件返工一次 (清空区 X 宽 +0.9300, 中心 18.8900 不变); 板那一趟要同批挪落点到 (18.2550, 68.6000)",
   "affects": [
    "J_UART"
   ],
   "evidence": "[推算]"
  },
  {
   "id": "DP-2",
   "title": "选官网参数直接满足的替代型号",
   "basis": "J_UART 换 X 宽 <= 1.3400 的 1x2 排针 (= 2.5400 - 2 x CRIT 0.60) => 结构件清空区一个数都不改",
   "cost": "选型与 pad 序要另开一单; B33 要把 J_UART 排除在换 land 名单外",
   "affects": [
    "J_UART"
   ],
   "evidence": "[推算]"
  },
  {
   "id": "DP-3",
   "title": "改设计路径绕开 (改走板边贴片 / 换出线方式)",
   "basis": "两个 SMD 档 Y 向红灯 (J_UART SMD 开口 Y 需 >= 7.8000; J_DEBUG SMD 开口 Y 净距 0.0700)",
   "cost": "结构件开口规格重做 (J_UART SMD 档开口 Y 几乎翻倍); J_DEBUG SMD 档 X 向是绿的 (最坏 1.8000) 但要按 Y 向重算开口",
   "affects": [
    "J_DEBUG",
    "J_UART"
   ],
   "evidence": "[推算]"
  },
  {
   "id": "DP-4",
   "title": "给其余 7 颗连接器补建座体必须清空区模型",
   "basis": "本单 §1.1 的 7 行口径来源 = unknown; 厂商料号可从板面 value 字段拿到",
   "cost": "一轮建模 + 逐颗补厂商 keepout; 补齐前这 7 颗的净距判决一律是未建模",
   "affects": [
    "J_BOOT1",
    "J_CHG",
    "J_SOM_P1",
    "J_SOM_P2",
    "J_SOM_P3",
    "J_SOM_P4",
    "J_USB_C"
   ],
   "evidence": "[推算]"
  }
 ],
 "conflicts": [
  {
   "id": "C1",
   "title": "同族两颗排针分母不同 -> 方向相反",
   "judgement": "同源判据下 J_UART 罩住余量 0.1350 (最坏 -0.1650) < CRIT 0.60 => 不过阈; J_DEBUG 开口余量 2.6950 (最坏 2.3950) >= CRIT => 过阈",
   "fact": "若那一趟按 B33 把 J_UART 也换成官方 land, 则铜箔每边只剩 0.1350 (最坏 -0.1650) 余量 => 铜箔不再被座体必须清空区完全罩住 => 结构件装不上",
   "owner": "main 回答 B33 范围 (OI-2)"
  },
  {
   "id": "C2",
   "title": "余量是向量不是标量: 支配方从 X 换到 Y",
   "judgement": "J_UART SMD 档: 开口 Y 余量 -0.7000 (最坏 -1.0000) < CRIT => 不过阈; 罩住 X 余量 0.3100 (最坏 0.0100) < CRIT => 不过阈; 姊妹件 J_DEBUG SMD 档开口 X 绿 (最坏 1.8000) 而 Y 红 (最坏 -0.2300)",
   "fact": "J_UART 换官方 SMD 变体后铜箔 Y 包络 6.0000 => 居中后上下各越出开口 Y 0.7000 => 装配当场干涉",
   "owner": "main 回答是否把两个 SMD 档写成禁用变体 (OI-2)"
  },
  {
   "id": "C3",
   "title": "同一位号的必须清空区 X 宽在仓里有三个数",
   "judgement": "罩住余量 = (H - C) / 2 => H < C 即负余量 => 三个数里只有 >= 4.8100 的那个能让 J_DEBUG 的罩住轴过阈",
   "fact": "若结构件按真相页 1.7750 留, 则 J_DEBUG 换官方 THT 后铜箔每边超出清空区 1.5175; 若按现页 4.0850 留, 则每边超出 0.3625",
   "owner": "main 回答 J_DEBUG 必须清空区 X 宽取哪一个 (OI-5)"
  },
  {
   "id": "C4",
   "title": "口径来源在一颗件内部就会分叉 + 全板 9 颗只有 2 颗建了模",
   "judgement": "J_UART 现状罩住 Y 余量最坏 0.5200 < CRIT 0.60 => 不过阈; unknown 行的判决是未建模不是过",
   "fact": "J_DEBUG 的 X 轴 Hx == Cx (copper_driven) 而 Y 轴 Hy 2.5400 > Cy 0.9000 (housing_driven); 其余 7 颗连红绿都判不了",
   "owner": "boss 回答罩住口径是否一律适用 (OI-8); main 回答 7 颗模型谁补 (OI-6)"
  }
 ],
 "part_models": {
  "J_DEBUG": {
   "value": "1x4 1.27mm 排针 (JTAG)",
   "vendor_part": null,
   "keepout": null,
   "evidence": "[实测](字符串) + [0数据](料号/keepout)",
   "ref": "logs/iss377/board_connectors.json"
  },
  "J_UART": {
   "value": "1x2 1.27mm 排针 (UART)",
   "vendor_part": null,
   "keepout": null,
   "evidence": "[实测](字符串) + [0数据](料号/keepout)",
   "ref": "logs/iss377/board_connectors.json"
  },
  "J_SOM_P1..P4": {
   "value": "Hirose DF40C-100DS-0.4V(51) 100pin 0.4mm (SOM P*)",
   "vendor_part": "Hirose DF40C-100DS-0.4V(51)",
   "keepout": null,
   "evidence": "[实测](料号) + [0数据](keepout)",
   "ref": "logs/iss377/board_connectors.json"
  },
  "J_USB_C": {
   "value": "GCT USB4105-16P USB-C 电源口 (自绘, 原厂图纸 Rev B3)",
   "vendor_part": "GCT USB4105-16P",
   "keepout": null,
   "evidence": "[实测](料号) + [0数据](keepout)",
   "ref": "logs/iss377/board_connectors.json"
  },
  "J_CHG": {
   "value": "SoM BTB CHG (100pin, 部分已分配)",
   "vendor_part": null,
   "keepout": null,
   "evidence": "[实测](字符串) + [0数据](料号/keepout)",
   "ref": "logs/iss377/board_connectors.json"
  },
  "J_BOOT1": {
   "value": "启动存储焊盘位 (4p 信号 + 2p 电源/GND 预留)",
   "vendor_part": null,
   "keepout": null,
   "evidence": "[实测](字符串)",
   "ref": "logs/iss377/board_connectors.json",
   "note": "板面位置是焊盘位, 不是座体 => 型号不适用"
  }
 },
 "board_baseline": {
  "path": "HW/PCB/demo_mainboard.kicad_pcb",
  "md5": "611b869e13518c3c023fb178f91a0075",
  "mtime": "2026-11-06 07:07:17.362193413",
  "size": 4940213,
  "evidence": "[实测]"
 },
 "sandbox": "tmp/iss377/",
 "logs": "logs/iss377/",
 "gate": "MECH/check_connector_clearance_caliber.py",
 "gate_chained": false,
 "verdict_summary": "同源判据 (M = max(H, C) per axis; 开口余量 = (O - M)/2; 罩住余量 = (H - C)/2; worst = margin - TOL['fdm_part']; 最坏余量 >= CRIT) 统一了 J_DEBUG 与 J_UART 两条口径: J_DEBUG 换官方 1x4 THT 开口余量 2.6950 (最坏 2.3950) 过阈; J_UART 换官方 1x2 THT 罩住余量 0.1350 (最坏 -0.1650) 不过阈; 同源化另算出 J_UART 现状罩住 Y 最坏 0.5200 与 J_DEBUG 换 THT 后每边越界 1.5175 两条此前没被算出来的红; 全板 9 颗连接器逐颗列行, 其中 7 颗口径来源 unknown 挂 OI-6",
 "verdict_two_sentences": {
  "judgement_sentence": "判据句 (方向): 同源判据下 J_UART 换官方 1x2 THT 后罩住余量 0.1350 (最坏 -0.1650) < CRIT 0.60 => 不过阈; 姊妹件 J_DEBUG 换官方 1x4 THT 后开口余量 2.6950 (最坏 2.3950) >= CRIT => 过阈",
  "fact_sentence": "事实句 (铜箔): 若结构件继续按现有真相页的必须清空区出件, 则 J_UART 换 THT 后铜箔每边只差 0.1350 (最坏 -0.1650) 余量 => 铜箔不再被座体完全罩住; J_DEBUG 换 THT 后铜箔每边超出真相页清空区 1.5175 => 铜箔直接进清空区",
  "must_not_merge": "两句同时成立, 不许合成一句模糊的通过结论"
 },
 "evidence_levels_used": [
  "[实测]",
  "[推算]",
  "[0数据]"
 ]
}
```

<!-- MECH-CONNECTOR-CLEARANCE-CALIBER-JSON-END -->

★**★机器块的读法 (★闸的 K0~K8 逐条对着这块与 §1/§2/§3 的正文查·★正文与机器块必须一致·★K0 会两两对拍★)★**:
★**`rows`** = §1.1 现状档 9 行 (★顺序 = 板面位号顺序★) ; ★**`tier_rows`** = §1.2 换官方 land 档 4 行 ; ★**`caliber_source` / `caliber_source_axes`** = §0.2 的口径来源 (★逐轴★) ; ★**`margin_open` / `margin_cover`** = 公式 ④ / ⑤ ; ★**`worst_*`** = 公式 ⑥ ; ★**`pass_*`** = 公式 ⑦ ; ★**`open_items`** = §4 的 OI 号 (★红行与 `unknown` 行必挂★) ★
