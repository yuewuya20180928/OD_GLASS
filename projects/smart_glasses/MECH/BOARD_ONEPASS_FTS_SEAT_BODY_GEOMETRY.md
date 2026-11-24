# `FTS` 直插档【座体外形 (宽 X / 深 Y / 绝缘体高 Z)】官网查证 + 「通用库件 courtyard 被当成厂件」前提订正 (ISS-390 · mech-lead · 2026-11-24)

> ★**本单性质**: ★**纯查证 + 纯分析 + 新建闸 + 作业包 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★
> ★**本单把 ISS-387 的 `OI-387-4` (`FTS` 直插档座体外形 = `[0数据]`) 结掉**: ★**路径 (甲) 走通了 ⇒ 厂件外形不再是 `[0数据]`** ★

---

## ★§0 一句话结论 ★

★**`FTS-104-01-F-S` (4 位) 与 `FTS-102-01-F-S` (2 位) 的厂件座体外形 = 【宽 X = N × 1.27 mm ⇒ `5.0800` / `2.5400`】·【深 Y = `2.1600`】·【绝缘体高 Z = `0.8600`】, 全部 `[官网]` (★Samtec 官方机械图 `FTS-1XX-XX-X-SX-MKT` REVISION AE 的 FIG 1 平面图 + 端视图, DigiKey `Insulation Height 0.86 mm` 交叉印证★); 而 MECH 全链吃的 `6.0900` / `5.0800` / `3.5500` / `2.5400` 是【盘上通用 KiCad 库件 `PinHeader_1x0{4,2}_P1.27mm_Vertical` 的 `F.CrtYd` / `F.Fab`】, 与 Samtec 无关 ⇒ ★★**`OI-12` 的「判据偏紧 `0.5200`」这个结论的对照物是错的 ⇒ 【需重算】** ★★ (★`0.5200` 这个数**作废**, 不是改成别的数; 用厂件座体本体重算后: `J_DEBUG` 每边多让 `0.7650` (★与 ISS-389 路 A 逐字一致, **数值是对的**★), `J_UART` 每边多让应是 `0.7650` 而不是 `0.7150` ⇒ **差 `0.0500`/边 需订正**★) ★★

---

## ★§1 官网查证过程 (★每个 URL + 字节数 + md5 + 取得方式 + HTTP 状态码★)★

### ★§1.1 本机通道实测 (★2026-11-24 12:0x~12:4x★)★

| 通道 | 目标 | 结果 | ★证据等级★ |
|---|---|---|---|
| ★`curl` 直连★ | `https://www.samtec.com/products/fts` | ★**HTTP 429** (★Cloudflare 1015 rate_limited, 17 bytes★) | — |
| ★`curl` 直连★ | `https://www.samtec.com/products/fts-104-01-f-s` | ★**HTTP 429** (17 bytes) | — |
| ★`curl` 直连★ | `https://suddendocs.samtec.com/` (★**可直连的域★**) | ★**HTTP 200** | — |
| ★搜索后端 (tavily)★ | `www.samtec.com` 网页类文字 (家族页标题 / 单品页标题 / 「2D view may not be representative… 请以 3D preview 或 CAD download 为准」免责段) | ★**取到, URL 留档** | ★`[官网]` (来源通道 = 搜索后端, 可复核性靠 URL) ★ |

### ★§1.2 取到的厂件文件 (★`suddendocs.samtec.com` 直连, ★★HTTP 200 + md5 齐全★★)★

| # | ★URL (来源通道 = `curl` 直连)★ | HTTP | bytes | md5 | ★内容★ | ★证据等级★ |
|---|---|---|---|---|---|---|
| ★**①** ★ | ★**`https://suddendocs.samtec.com/prints/fts-1xx-xx-x-sx-mkt.pdf`** ★ | ★**200** ★ | ★**190339** ★ | ★**`69d9415867cd642d6a6e07c6b755516b`** ★ | ★**`FTS-1XX-XX-X-SX` 官方机械/营销图, REVISION AE, SolidWorks 2019 SP5, 2022-07-27, 2 页 (SHEET 1 OF 2 + SHEET 2 OF 2) ⇒ ★★本单厂件外形的唯一来源★★** ★ | ★`[官网]` ★ |
| ② | `https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf` | 200 | 143472 | `1cbe4a2bfa456d8fd030c8b76bdf8dd5` | ★官方推荐 PCB 图 (4 页, **只有 land 尺寸 / 孔位, 无座体外形标注**) ⇒ ★★它给不了座体外形★★ ★ | ★`[官网]` ★ |
| ③ | `https://suddendocs.samtec.com/catalog_english/fts.pdf` | 200 | 468445 | `fa249db9454f92c77d7e0a5ef62a0ba6` | ★FTS 家族目录页 (1 页, **只有料号编码规则 + 规格表, 无外形图**) ⇒ ★**给不了座体外形** ★ | ★`[官网]` ★ |
| ④ | DigiKey `FTS-104-01-F-S` 单品页 (`https://www.digikey.com/en/products/detail/samtec-inc/FTS-104-01-F-S/7342275`) | ★(搜索后端)★ | — | — | ★属性表逐字: `Insulation Height 0.034" (0.86mm)` · `Contact Length - Post 0.090" (2.29mm)` · `Overall Contact Length 0.244" (6.20mm)` · `Contact Length - Mating 0.120" (3.05mm)` ⇒ ★**`0.86` 与官网图 `.034 0.86 REF` 逐字互证** ★ | ★`[媒体]` ★ |

★**① 是本单的转折点**: ★ISS-387 只找到 ② (footprint) 与 ③ (catalog) ⇒ 「座体外形 = `[0数据]`」; ★**本单在 `suddendocs.samtec.com/prints/` 下找到了 `-mkt` (mechanical / marketing drawing) 这一族文件名 ⇒ 直接拿到带座体外形标注的官方图** ★

### ★§1.3 探测记录 (★「查不到」的部分也要留证, ★不许写「官网打不开」就交差★)★

★**同域探测 40+ 个候选路径, 全部 HTTP 403** (★`suddendocs.samtec.com` 对**不存在的路径**返 403 + `application/xml` 111 bytes ⇒ **403 = 不存在**, 不是被挡★):

| 候选 (全部 403) | 说明 |
|---|---|
| `/3d/{fts-104-01-f-s, fts-1xx-xx-xx-sx-xx}.{step,stp,wrl,igs}` · `/cad/*.step` | ★**官网 3D/CAD 下载件不在 `suddendocs` 的 `/3d/` 或 `/cad/` 路径下** ⇒ ★**该通道拿不到 3D 件** ★ |
| `/prints/fts-1xx-xx-xx-{s,sx,s-xx,sx-xx,sxx}-footprint.pdf` · `/prints/fts-single-row-footprint.pdf` | ★单排版 PCB 图直链仍不存在 (ISS-387 同结论, 本单复核) ★ |
| `/prints/fts-1xx-xx-xx-{s,sx}-drawing.pdf` · `/{s,sx}-3d.pdf` · `/{s,sx}-step.pdf` · `/{s,sx}-stencil*.pdf` · `/prints/fts-104-01-f-s.pdf` · `/specsheets/*` · `/product_specs/*` · `/specs/*` · `/product/*` | ★**本域唯一存在的那一族是 `-mkt`** (①) ★ |

★**⇒ 路径 (甲) 的实际落点 = 「官网机械/营销图 (MKT drawing)」, 不是「3D/CAD 下载件」** ★

### ★§1.4 图纸读数自证 (★不是靠肉眼, 是靠像素量, ★可复现★)★

★**图纸比例 `SHEET SCALE: 4:1` ⇒ `1.27 mm` (`.050`) = `14.40 pt`** ★

| 量 | 图上位置 | ★像素实测 (300 dpi 渲染, `pdftoppm`)★ | ★折算★ | ★图纸标注★ | ★自证★ |
|---|---|---|---|---|---|
| 端子中心距 | 平面图相邻端子矩形中心 | `14.40 pt` (实测 `224.64` → `239.04`) | `1.2700 mm` | `.050 1.27 REF` | ★**逐字命中** ⇒ 比例自证成立 ★ |
| ★**绝缘体高 Z** ★ | ★**FIG 1 端视图 (右), `.034 0.86 REF` 的两条洋红延长线 y=`181.56` / `191.40` ⇒ 黑块上下缘 `9.84 pt`** ★ | ★`9.84 pt` ★ | ★`0.868 mm` ★ | ★**`.034 0.86 REF`** ★ | ★**+0.9%** (线宽误差) ⇒ ★**Z = `0.8600`** ★ |
| ★**座体深 Y** ★ | ★**FIG 1 平面图 (上), `.085 2.16 REF` 的两条洋红延长线 y=`62.04` / `86.28` ⇒ 黑块上下缘 `24.24 pt`** ★ | ★`24.24 pt` ★ | ★`2.138 mm` ★ | ★**`.085 2.16 REF`** ★ | ★**−1.0%** ⇒ ★**Y = `2.1600`** ★ |
| ★**座体长 X** ★ | ★**平面图总长标注 `(NO OF POS x .0500 [1.27]) ±.010 [.25]`, 其两条延长线正好落在座体左右端 (`x=188.40` / `x=340.80`) ⇒ ★★**座体长 = N × 1.27**★★ ★ | ★端子中心到座体端 overhang = `7.44 pt` / `7.08 pt` ⇒ `0.656` / `0.624 mm` ★ | ★≈ `0.635` = `1.27/2` ★ | ★`(NO OF POS x .0500 [1.27])` ★ | ★**⇒ 座体长 = (N−1)×1.27 + 2×0.635 = N×1.27** ★ |

★**★该图是【带断视图 (broken view, 锯齿折断线)】的 50 位通用图** ⇒ ★**画出来的长度不是 `50 × 1.27`**, ★但**总长标注是通式 `(NO OF POS x .0500 [1.27])`** ⇒ ★★**座体长 = N × 1.27 mm (REF, 公差 ±0.25)** ★★ ⇒ **N=4 ⇒ `5.0800` ; N=2 ⇒ `2.5400`** ★

★**⇒ 三量与厂件图逐字对上了, 且与 DigiKey `Insulation Height 0.86 mm` 交叉互证 ⇒ ★★`[0数据]` 结掉★★** ★

---

## ★§2 座体外形三量表 (★逐项标证据等级★)★

★**板系坐标约定 (★与 MECH 全链一致★)**: ★**X = 沿排距方向 (板上的 row 方向, ★铜箔包络 X `4.8100` / `2.2700` 就是这个方向★) ; Y = 跨排距方向 (铜箔 Y `1.0000`) ; Z = 板面以上** ★
★**本机实测佐证**: ★盘上 `J_DEBUG` 现状 4 个 pad 的局部 x = `-2.1 / -1.6 / -1.1 / -0.6` (间距 `0.5`), 尺寸 `0.275 × 0.9` ⇒ ★**现状 row 沿板 X** ✔ ⇒ ★**`X` = row 方向成立** ★`[实测]`

| ★量 (★板系轴★)★ | ★`FTS-104-01-F-S` (4 位 · `J_DEBUG`)★ | ★`FTS-102-01-F-S` (2 位 · `J_UART`)★ | ★证据等级★ | ★图纸原文 (★逐字★)★ | ★双证★ |
|---|---|---|---|---|---|
| ★**座体宽 X** (★沿排距★) | ★**`5.0800`** (★= 4 × 1.27★) | ★**`2.5400`** (★= 2 × 1.27★) | ★**`[官网]`** ★ | ★FIG 1 平面图总长 `(NO OF POS x .0500 [1.27]) ±.010 [.25]` ⇒ **N × 1.27** ★ | ★overhang `0.635`/端 自证 (§1.4) ★ |
| ★**座体深 Y** (★跨排距★) | ★**`2.1600`** | ★**`2.1600`** | ★**`[官网]`** ★ | ★FIG 1 平面图 `.085 2.16 REF` ★ | ★端视图黑块宽 `25.2 pt` 独立复核 `≈2.16` ✔ ★ |
| ★**绝缘体高 Z** (★板面以上★) | ★**`0.8600`** | ★**`0.8600`** | ★**`[官网]`** ★ | ★FIG 1 端视图 `.034 0.86 REF` ★ | ★★**DigiKey `Insulation Height 0.034" (0.86mm)`** ★`[媒体]`★★ ★ |

### ★§2.1 ★★厂件 vs 通用库件 ★★ 对照表 (★本单的核心★)★

★**通用库件 (本机 `Connector_PinHeader_1.27mm.pretty` 实测, ★`[实测]`★)**:

| 库件 | `F.Fab` 本体 (★不含笔画, 逐点算★) | `F.CrtYd` (逐点算) | 焊盘 / 钻孔 |
|---|---|---|---|
| `PinHeader_1x04_P1.27mm_Vertical` | ★**`2.1000` (跨) × `5.0800` (沿)** ★ | ★**`3.1000` × `6.0900`** ★ | `(size 1 1)` + `(drill 0.65)` |
| `PinHeader_1x02_P1.27mm_Vertical` | ★**`2.1000` (跨) × `2.5400` (沿)** ★ | ★**`3.1000` × `3.5500`** ★ | `(size 1 1)` + `(drill 0.65)` |

★**⇒ 逐格对照 (★厂件 = 官网图, 通用件 = 本机库件★)**:

| 对照格 | ★厂件 (FTS)★ | ★通用库件★ | ★差★ | ★定性★ |
|---|---|---|---|---|
| ★座体宽 X (N=4)★ | ★**`5.0800`** ★ | ★`5.0800` (`F.Fab`) ★ | ★**`0.0000`** ★ | ★★**通用件的 `F.Fab` 沿排距长与厂件逐字相同** (两边都是 `N × 1.27`) ⇒ ★**MECH 沿用 `5.0800` 作「座体本体」这个数【数值是对的】, 但它的出处被写成了「官方 land」—— ★★错的是出处, 不是这个数★★** ★ |
| ★座体宽 X (N=2)★ | ★**`2.5400`** ★ | ★`2.5400` (`F.Fab`, 不含笔画) ★ | ★**`0.0000`** ★ | ★同上; ★但 ISS-374/ISS-389 用的是**含笔画 `0.05`/边**的 `2.6400` ⇒ **那边多了 `0.1000`** ★ |
| ★座体深 Y (N=2 / N=4)★ | ★**`2.1600`** ★ | ★`2.1000` (`F.Fab`) ★ | ★**`+0.0600`** ★ | ★★**通用件比厂件【窄 `0.0600`】⇒ 通用件当座体用 ⇒ Y 向【少让 `0.0300`/边】** ★★ |
| ★绝缘体高 Z★ | ★**`0.8600`** ★ | ★**无** (库件没有 Z) ★ | — | ★★**库件根本给不了 Z ⇒ `OI-11` 那条 `[0数据]` 的性质变了 (见 §6.1)★★** ★ |
| ★`F.CrtYd`★ | ★**无** (★Samtec 厂件**没有** courtyard 这个数★) ★ | ★`6.0900` / `3.5500` / `3.1000` ★ | — | ★★★**`6.0900` / `5.0800` / `3.5500` / `2.5400` 这组数【全部来自通用库件】, 与 Samtec 无关** ⇒ ★★**ISS-389 `OI-12` 把 `6.0900` 这个【通用库件 `F.CrtYd`】的数, 在答复里当成了【Samtec 厂件的 courtyard】⇒ 是定性错误** ★★ ★ |

★**★顺带查到的一条口径不一致 (★只登记, 不代裁★)**: ★ISS-371/ISS-389 对 `J_DEBUG` 的「座体本体」用 **`5.0800 × 2.1000` (不含笔画)**, ISS-374/ISS-389 对 `J_UART` 的用 **`2.6400 × 2.2000` (含笔画 `0.05`/边)** ⇒ ★**同一页两个零件用了两个口径** ⇒ ★**`0.7150` 与 `0.7650` 的差 `0.0500`/边 就是这么来的** ⇒ ★见 §4-① / §5-⑦ ★`[实测]`

---

## ★§3 降级方案 (★路径 (甲) 已通, 路径 (乙) 仍然在册备用★)★

### ★§3.0 路径 (甲) 的结果 (★不用降级了★)★

★**路径 (甲) = 官网 3D/CAD 下载件** ⇒ ★**部分成功**: ★**3D/CAD 件在本机拿不到** (`/3d/` `/cad/` 路径全 403), ★**但同一份官方机械图 (`-mkt.pdf`) 给了完整的座体三量** ⇒ ★**厂件外形不再是 `[0数据]`** ⇒ ★**降级路径 (乙) 从「必须走」降为「装配前复核」** ★

### ★§3.1 路径 (乙) 全文 (★谁在什么时候量哪三个量, 量完填回 `keepout_dwg` 的哪一格★)★

★**触发条件**: ★**装配前对不上、或有人质疑图纸读数** (★不是「官网查不到」—— ★**官网查到了**★) ⇒ ★**动作 (★全部在项目内, ★零外发★)**:

| 步 | ★谁★ | ★什么时候★ | ★量哪三个量 (★逐字写清量法★)★ | ★量完填回哪一格★ |
|---|---|---|---|---|
| 乙-1 | ★**装配工序第一站的人 (★不是结构设计, ★是装机台★)** ★ | ★**落 FTS 时先打一块单板样 (★只 1 块, boss: 成本不是问题但别乱花★) 焊接完成后、装进镜脚内腔之前** ★ | ★**① 座体宽 X**: ★卡尺量 LCP 塑壳【沿排距方向】两端外表面间距 (★不是量端子, 不是量铜箔★) ⇒ 期望 `5.0800` (4 位) / `2.5400` (2 位) ★**② 座体深 Y**: ★卡尺量 LCP 塑壳【跨排距方向】前后外表面间距 ⇒ 期望 `2.1600` ★**③ 绝缘体高 Z**: ★卡尺量塑壳底面到塑壳顶面的高度 ⇒ 期望 `0.8600` (★注意: 端子柱另高 `3.05`, 别把柱高当成塑壳高★) ★ | ★**`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` 机器块 `keepout_dwg` 那一行** ⇒ ★**逐项写 `X = <实测> / Y = <实测> / Z = <实测>` + 标注 `[实测]` + 记测量日期 + 记「样件 = 第几块」** ★ |
| 乙-2 | ★**结构设计 (mech-lead)★** ★ | ★**实测回填的当天** ★ | ★**不复测, 只核对**: ★三个数与 §2 逐字对照, 差 > `0.05` ⇒ **登记一条偏离并更新本页 §2 的证据等级** (★`[官网]` → `[实测]` 双证★) ★ | ★**本页 §2 三量表 + 机器块 `body_geometry.*`** ★ |
| 乙-3 | ★**结构设计 (mech-lead)★** ★ | ★**乙-2 完成后** ★ | ★**把实测回填到 ISS-387 的 `keepout_dwg` 行** ⇒ ★**`OI-387-4` 正式关闭** ★ | ★**ISS-387 机器块 `keepout_dwg` + 本页机器块 `degradation.fallback_b` 的 `status` 由 `armed` 改 `closed`** ★ |

★**⇒ 缺口不许挂成「等厂商回复」/「外部待确认」/「阻塞项挂着」: ★**本单既没查不到, 也没在等谁回信; 路径 (乙) 只是一道【装配前的实测复核工序】, 有明确的执行人 / 时点 / 量法 / 回填格** ★

---

## ★§4 前提订正表 (★逐条: 哪一行 / 原措辞 / 改成什么 / 状态★)★

★**状态一律 `待 main 落` (★本单零改既有页正文, ★零改既有闸源码★)** ★

| # | ★位置★ | ★现在的说法 (★逐字★)★ | ★订正成什么 (★逐字★)★ | ★状态★ |
|---|---|---|---|---|
| ★**①** ★ | ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` **L634** (机器块 `OI-12` 的 `structural_answer`) ★ | ★「硬差额: 判据要求每边 `0.9000`, ★**官方 land courtyard 只给每边 `0.6400`** (J_DEBUG `F.CrtYd 6.0900` vs 铜箔 `4.8100`; J_UART 退包络 `3.5500` vs 铜箔 `2.2700`) => 每边差 `0.2600`, 清空区 X 总宽差 `0.5200` (6.6100-6.0900 / 4.0700-3.5500). 路 A 判据不动 => 清空区 X `6.6100`/`4.0700`, 每边比座体本体多让 `0.7650`/`0.7150`, …」 ★ | ★「硬差额: 判据要求每边 `0.9000`; ★**本单 (ISS-390) 实测: `6.0900` / `5.0800` / `3.5500` / `2.5400` 全部来自盘上【通用 KiCad 库件 `PinHeader_1x0{4,2}_P1.27mm_Vertical` 的 `F.CrtYd` / `F.Fab`】, ★**不是 Samtec 厂件的数**★ ⇒ ★**厂件 `FTS` 座体本体 = `5.0800` (N=4) / `2.5400` (N=2) × `2.1600` × `0.8600` `[官网]` ⇒ 【对照物换掉】⇒ 『比 courtyard 还大 `0.5200` ⇒ 偏紧』这个结论【作废】(★不是改成别的数, 是对照物无效★) ⇒ ★**清空区 X `6.6100`/`4.0700` 本身不变 (它是 `铜箔 + 2 × 0.9000` 的自洽式)★; 用厂件座体本体比: `J_DEBUG` 每边多让 `(6.6100−5.0800)/2 = 0.7650` (不变) ; `J_UART` 每边多让 `(4.0700−2.5400)/2 = 0.7650` (★原写 `0.7150` ⇒ 订正 `+0.0500`/边★)」** ★ | ★`待 main 落` ★ |
| ★**②** ★ | ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` **L149 / L154** (正文「路径 A / 路径 B」段 + `D-6` / `U-7` 行) ★ | ★L149: 「★**`J_DEBUG` 的 `6.0100` 比 courtyard `6.0900` 还小 `0.0800` ⇒ 「比 courtyard 还大」的反常消失**」 ; L154: 「★`J_DEBUG` 的 `6.0100` 比 courtyard `6.0900` 还小 `0.0800` ⇒ 「比 courtyard 还大」的反常消失★」 ; L69/L90: 「官方 1×4 THT 座体本体 (`F.Fab`) X `5.0800` × `2.1000`」 / 「官方 1×2 THT 座体本体 (`F.Fab`) `2.6400` × `2.2000`」 ★ | ★① 「courtyard」三处一律加限定语 ★**「通用 KiCad 库件的 `F.CrtYd`」**★, 并补「厂件 `FTS` 无 courtyard 概念 ⇒ 该对照不成立」; ② 座体本体一律改成 ★**厂件实测值 `5.0800 × 2.1600` (N=4) / `2.5400 × 2.1600` (N=2) `[官网]`**, 并注明通用库件 `F.Fab` 的 `5.0800` / `2.5400` (沿排距) 恰好逐字相同、跨排距 `2.1000` 比厂件窄 `0.0600`; ③ `J_UART` 的 `2.6400` 注明是【含笔画 `0.05`/边】口径, 去掉笔画后是 `2.5400` ⇒ ★**那 `0.1000` 就是口径差, 不是件差** ★ | ★`待 main 落` ★ |
| ★**③** ★ | ★`MECH/check_debug_seat_3d_fit.py` **L848** (★**闸源码里的字符串★**) ★ | ★「★**而★**官方 land 的 `F.Fab 5.0800` / `F.CrtYd 6.0900` ⇒ 判据要求比 courtyard 还大 `0.5200`★」 ★ | ★**源码字符串里的定性也要订正** ⇒ ★**但本单【不许改这个闸】(★它已签收★) ⇒ 只登记「该字符串需订正」+ 落 `needs_from` to=main ⇒ ★★不许自己动它★★ ★ ⇒ ★**建议措辞**: 「而【通用 KiCad 库件】的 `F.Fab 5.0800` / `F.CrtYd 6.0900` ⇒ 【该对照不成立: 厂件 `FTS` 座体本体 = `5.0800` × `2.1600` × `0.8600`】(★ISS-390★)」 ★ | ★`待 main 落` ★ |
| ★**④** ★ | ★`MECH/check_debug_seat_3d_fit.py` **L879** (★**闸源码里的字符串★**) ★ | ★「(★事实: ★**官方 1x4 THT 的 `F.CrtYd` 只有 `6.0900` X, 而判据要求清空区 `6.6100` ⇒ 比 courtyard 还大 `0.5200`★)」 ★ | ★同上 ⇒ ★**建议措辞**: 「(★事实: ★**通用 1x4 库件的 `F.CrtYd` 是 `6.0900` X; ★厂件 `FTS-104-01-F-S` 座体本体 = `5.0800` X ⇒ 判据要求清空区 `6.6100` 比【厂件座体本体】每边多让 `0.7650`; 那个 `0.5200` 的对照物无效★)」 ★ | ★`待 main 落` ★ |

★**★本单另外发现、但【不在上面 4 处之内】的两处 (★一并登记, 同样 `待 main 落`★)★:

| # | ★位置★ | ★现在的说法★ | ★订正成什么★ | ★状态★ |
|---|---|---|---|---|
| ★⑤ ★ | ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` L114 (正文) 与机器块 `DP-5` 的 `basis` ★ | ★「★**官方 land 自己的 `F.Fab` 旋转后是 `5.0800` X、`F.CrtYd` 是 `6.0900` X ⇒ 判据要求的 `6.6100` 比 courtyard 还大 `0.5200` ⇒ ⑤ 这条判据对 THT 排针偏紧 ⇒ 登记 `OI-12`★」 ★ | ★「★**通用库件的 `F.Fab` 旋转后是 `5.0800` X、`F.CrtYd` 是 `6.0900` X ⇒ 【对照物无效】⇒ 厂件 `FTS` 座体本体 `5.0800` X ⇒ 判据要求的 `6.6100` 比【厂件座体本体】每边多让 `0.7650` ⇒ ★★【`0.5200` 作废; 「偏紧」这个说法要重新表述为 §5-⑧ 的【座体口径】那条**★」 ★ | ★`待 main 落` ★ |
| ★⑥ ★ | ★`MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` L118 (`S1` 行「座体本体外框」列) + `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` L139 (「座体口径」行) ★ | ★`J_UART`: `2.6400 × 2.2000` (★含笔画★) ; `J_DEBUG`: `5.08 × 2.10` (★不含笔画★) ⇒ ★**同页两零件两个口径** ★ | ★**两处统一成厂件实测 `5.0800 × 2.1600` / `2.5400 × 2.1600` `[官网]`** ; 通用库件值作为「对照列」保留并注明口径 (★`F.Fab` 不含笔画 = `5.0800 × 2.1000` / `2.5400 × 2.1000`★) ★ | ★`待 main 落` ★ |

---

## ★§5 影响面 (★哪些数会变 / 哪些不会 · ★逐个说清★)★

★**判据链 (★MECH 现状, 一字不改地重述★)**: ★**罩住余量 = (清空区 H − 铜箔包络 C) / 2 ≥ `CRIT 0.60` + `TOL 0.30` = `0.9000`/边** ; ★**开口余量 = (罩开口 O − max(H, C)) / 2 ≥ `0.9000`** ★
★**`C` (铜箔包络) = `4.8100 × 1.0000` (J_DEBUG) / `2.2700 × 1.0000` (J_UART)** ★**【由 land 焊盘尺寸决定, 与座体外形无关 ⇒ 不动】** ★`[实测]` (ISS-371 / ISS-374 已签收)

| # | ★数★ | ★会不会变★ | ★为什么 (★逐条给算式★)★ |
|---|---|---|---|
| ★**①** ★ | ★**`6.6100`** (`J_DEBUG` 罩住 X 需求) ★ | ★**不变** ★ | ★`= 4.8100 + 2 × 0.9000` ★**只由铜箔 + 判据定义, 座体外形不进这条式子** ★ ⇒ ★**厂件外形补上后它一个数都没动** ★`[推算]` |
| ★**②** ★ | ★**`4.0700`** (`J_UART` 罩住 X 需求) ★ | ★**不变** ★ | ★`= 2.2700 + 2 × 0.9000` ⇒ 同上 ★`[推算]` |
| ★**③** ★ | ★**`0.1350`** (`J_UART` 罩住 X 余量) ★ | ★**数值不变, 但它的【物理含义要加一条限定】★** ★ | ★`= (2.5400 − 2.2700)/2` ⇒ **只由现有结构件出件值 `2.5400` + 铜箔决定** ⇒ **数不动** ; ★★**但本单发现: `J_UART` 的厂件座体宽 X 恰好也是 `2.5400` ⇒ 【座体本体与现有清空区 X 齐平, 每边 `0.0000`】★★ ⇒ ★**若「罩住」也要罩住座体本体, 这一项立刻变红** ⇒ 见 ⑧ ★`[推算]` ★ |
| ★**④** ★ | ★**`2.6950`** (`J_UART`/`J_DEBUG` 开口 X 余量) ★ | ★**不变** ★ | ★`= (10.2000 − M)/2`, `M = max(H, C) = 4.8100` ⇒ **三个候选 H (`1.7750`/`4.0850`/`4.8100`) 都 ≤ `4.8100`, 且座体外形不进 `M`** ⇒ 不动 ★`[推算]` |
| ★**⑤** ★ | ★**`0.7700`** (罩住 Y 余量, `h=2.54` 档) ★ | ★**数值不变, 但【够不够】的答案变了** ★ | ★`= (2.5400 − 1.0000)/2` ⇒ **只由 `h` 档 + 铜箔 Y 决定** ⇒ 数不动 ; ★★**但厂件座体深 Y = `2.1600` ⇒ 若同样按 `0.9000`/边要求罩住座体 ⇒ 需 `3.9600` ⇒ 现有清空区 Y `2.8000` 【差 `1.1600`】★★ ⇒ 见 ⑧ ★`[推算]` ★ |
| ★**⑥** ★ | ★**`OI-5` 三档 `1.7750` / `4.0850` / `4.8100`** ★ | ★**三个数全部不变; 但多了一个【第四参照】★** ★ | ★`1.7750` = 现状板读铜箔宽 ; `4.0850` = `3.81 + 0.275` ; `4.8100` = `3.81 + 1.00` ⇒ ★**三条推导链里没有一条用到座体外形 ⇒ 三个数都不动** ★`[推算]` ; ★★**但本单给了一个新的对照物: 厂件座体本体 X = `5.0800` (J_DEBUG) / `2.5400` (J_UART) ⇒ 它落在 `4.8100` 与 `6.6100` 之间 ⇒ 【座体比铜箔宽 `0.2700`】⇒ ★**若 `OI-5` 选 `4.8100` (铜箔齐平档), 座体本体每边仍伸出清空区 `0.1350` ⇒ 「铜箔齐平」这句话现在必须加限定词** ★★ ★ |
| ★**⑦** ★ | ★**`0.7650` / `0.7150`** (ISS-389 路 A 的「每边比座体本体多让」) ★ | ★**`0.7650` 不变; `0.7150` ⇒ `0.7650` (+`0.0500`/边)** ★ | ★`J_DEBUG`: `(6.6100 − 5.0800)/2 = 0.7650` ★**厂件座体 X 恰与通用 `F.Fab` 逐字相同 ⇒ 数值不变** ★ ; ★`J_UART`: ISS-389 用的是含笔画的通用件 `2.6400` ⇒ `(4.0700 − 2.6400)/2 = 0.7150` ; ★**换成厂件 `2.5400` ⇒ `(4.0700 − 2.5400)/2 = 0.7650`** ⇒ ★**差 `0.0500`/边** ★`[推算]` ★ |
| ★**⑧** ★ | ★**★新增的一条: 「罩住」要不要连【座体本体】一起罩住 ★** ★ | ★**★这是本单新算出来、前面没人算过的一条 (★归 main + boss 裁决, ★本单不代拍★)★** ★ | ★★**若判据从「罩住铜箔」扩到「罩住座体本体」, 需求变成**: ★**X: `J_DEBUG` 座体 `5.0800 + 1.8000 = 6.8800` (比 `6.6100` 差 `0.2700`) ; `J_UART` 座体 `2.5400 + 1.8000 = 4.3400` (比 `4.0700` 差 `0.2700`) ; Y: 座体 `2.1600 + 1.8000 = 3.9600` (比 `2.8000` 差 `1.1600`, 且开口 Y `4.6000` 最多只容 `2.8000` ⇒ 【Y 向从「零余量卡死」变成「差 `1.1600` 卡死」】)★★** ★ ⇒ ★**⇒ `Y` 向这条是本单最值钱的一句: 现在 Y 向「零制造余量」不只是零, 是【负 `1.1600`】★★** ★`[推算]` ★ |
| ★**⑨** ★ | ★**`0.5200`** (★`OI-12` 争议的那个数★) ★ | ★**作废 (★前提无效, ★不是改成别的数★)** ★ | ★它的对照物是通用库件 `F.CrtYd` ⇒ ★**厂件 `FTS` 没有 courtyard 这个量 ⇒ 对照不成立** ★ ⇒ ★**正确表述见 ⑦ 与 ⑧** ★ |
| ★**⑩** ★ | ★**`OI-11` 的 `h`** ★ | ★**不变 (★本单解决不了★)** ★ | ★见 §6.1 ★ |

★**⇒ 一句话收口**: ★**厂件外形补上后, MECH 全链【没有一个数因为「外形」本身而变】; ★变的是【对照物的定性】与【两个口径下的每边余量】: `0.7150` → `0.7650` (J_UART) ; `0.5200` 作废 ; ★新增一条 Y 向「座体口径」缺口 `1.1600` 待裁决** ★★

---

## ★§6 与 `OI-11` / `OI-12` / `OI-13` / `OI-14` 的关系 ★

### ★§6.1 `OI-11` (★`J_DEBUG` 座体真实高 `h` = `[0数据]`) ★

★**★结论: ★解决不了★, 而且【不能】用本单的 `Z = 0.8600` 去顶它 ⇒ 必须说清 ★**

| | ★`OI-11` 的 `h` ★ | ★本单查到的 Z ★ |
|---|---|---|
| ★主体★ | ★**罩 / 座体【结构件】** (★MECH 的 debug seat / 罩★) ★ | ★**连接器【元器件】的 LCP 绝缘体** ★ |
| ★在 MECH 链里的作用★ | ★三档 `0.90` / `2.54` / `4.00` ⇒ 决定「★清空区 Y 有效高★」⇒ ★**只影响 Y 向判决, X 向判决与 `h` 无关** ★ | ★**不进 MECH 判决链的任何一个式子** ★ |
| ★证据等级★ | ★`[0数据]` ★ | ★`[官网]` + `[媒体]` ★ |

★**⇒ `h` 与 `Z` 同向 (都是 Z) 但【主体不同】⇒ 本单【不能】解决 `OI-11`; ★★把 `0.8600` 当成 `h` 用, 会把罩高从 `2.54` 档压到 `0.86` 档 ⇒ 直接把 Y 向判决从「罩住红 / 开口绿」推到更红 ⇒ ★★**这是危险的方向, 明确禁掉** ★★**

★**★但本单确实给 `h` 送来了一条【以前没有的】官网下界输入 (★不是 `h` 的值, ★是 `h` 的一条约束★)★**:
★**官网图 `.120 [3.05] POST` (lead style `-01`) ⇒ 连接器在板面以上实际占高 = `3.05` mm** (★绝缘体只有 `0.86`, 柱露出 `3.05 − 0.86 = 2.19`; ★尾脚 `.090 [2.29]` 在板面以下, ★`SHEAR TAILS TO DIMENSION SHOWN`★) ⇒ ★★**罩的内腔【板面以上】那一维不能按 `0.86` 出件, 至少要 `3.05` + 装配余量 ⇒ 而 MECH 链里 `h` 的三档 (`0.90` / `2.54` / `4.00`) ★★`0.90` 档【物理上】装不下这个连接器★★ ⇒ ★**`h = 0.90` 档应当被排除 (依据 = 官网柱高 `3.05`)** ⇒ ★**这是给 boss 的一条可核对的输入, 不是本单代拍 `h`** ★`[官网]`+`[推算]`

### ★§6.2 `OI-12` (★判据对 THT 排针是否过严★) ★

★**★状态: 【需重算】★** ★**(★三值取一: `不需重算` / `需重算` / `待定`★)**

| ★读法★ | ★结论★ |
|---|---|
| ★**原读法 (ISS-389 / ISS-379 写下的)★** ★ | ★「判据要求清空区 `6.6100` 比【厂件 courtyard】`6.0900` 还大 `0.5200` ⇒ ⑤ 这条判据对 THT 排针偏紧」 (★`6.0900` 那个数本身的逐字出处见 §4-①★) ★ |
| ★**本单复核 (★对照物换掉★)★** ★ | ★★**`6.0900` 是【通用 KiCad 库件】的 `F.CrtYd`, 厂件 `FTS` 没有 courtyard ⇒ 这条对照【无效】⇒ 「偏紧 `0.5200`」这个结论【作废】★★ ★ |
| ★**换厂件后真正成立的两条 (★本单新算★)★** ★ | ★**① 判据要求 `6.6100` 比厂件座体本体 `5.0800` 每边多让 `0.7650` ⇒ 判据【对厂件并不偏紧】(★ISS-389 路 A 的数, ★数值本来就对★) ; ② 若判据口径扩到【罩住座体本体】⇒ 需 `6.8800` / `4.3400` / `3.9600` ⇒ ★★**X 向缺 `0.2700`, Y 向缺 `1.1600`** ★★ ⇒ ★**⇒ 「偏紧」这个问题【没有消失, 是换了个问法】: 现在要问的是「判据管到铜箔还是管到座体本体」** ★ |
| ★**归谁★** ★ | ★**main + boss** (★口径裁决权不在结构侧★) ★ |

### ★§6.3 `OI-13` (★Y 向零余量 / 接受零余量★) ★

★**★代价变大 (★具体数见 §5-⑧★)★**: ★现状口径 (只罩铜箔) 下 Y 向是「零制造余量卡死」; ★★**加上座体本体 `2.1600` 之后, Y 向从「零余量」变成「缺 `1.1600`」⇒ `OI-13` 的两个选项 (放大开口 Y / 接受零余量) 【第二个选项已经不存在了】⇒ `OI-13` 必须跟 `OI-12` 的口径一起拍** ★ ⇒ ★**归 main + boss** ★

### ★§6.4 `OI-14` (★ISS-377 `DP-1` 的 `3.4700` 订正为 `4.0700`★) ★

| | ★结论★ |
|---|---|
| ★**现状口径下★** ★ | ★**`4.0700` 不变** (★纯铜箔口径 `2.2700 + 2 × 0.9000`, 与座体外形无关★) ⇒ ★**`OI-14` 本身不受本单影响** ★`[推算]` |
| ★**若 main 采纳「判据也管座体本体」★** ★ | ★**`J_UART` 的 X 需求变 `4.3400`** ⇒ ★**`OI-14` 的目标值要跟着 `OI-12` 的口径一起改** ⇒ ★★**这才是 ISS-389 说的「两条必须一起拍」的精确理由** (★不是「都在 `OI-12` 后面」, ★而是「`OI-14` 的目标值由 `OI-12` 的口径决定」★) ★ |
| ★**归谁★** ★ | ★**main** (★与 `OI-12` 同批拍★) ★ |

---

## ★§7 复跑命令 + 机器块 ★

### ★§7.1 复跑命令 (★逐条实跑, ★原样贴输出★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ① 厂件机械图 (★本单的唯一一手来源·★走可直连通道★)
curl -sS -o tmp/iss390_sbx/fts-1xx-xx-x-sx-mkt.pdf -w '%{http_code} %{size_download}\n' \
  https://suddendocs.samtec.com/prints/fts-1xx-xx-x-sx-mkt.pdf
md5sum tmp/iss390_sbx/fts-1xx-xx-x-sx-mkt.pdf     # ★期望 69d9415867cd642d6a6e07c6b755516b★
pdftotext -layout tmp/iss390_sbx/fts-1xx-xx-x-sx-mkt.pdf - | grep -n "\.085\|\.034\|NO OF POS"

# ② 通用库件对照 (★本机实测·★证明 6.0900/5.0800 的出处★)
grep -o "(drill [0-9.]*)" /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod
python3 - <<'PY'
import re
for f in ("PinHeader_1x04_P1.27mm_Vertical","PinHeader_1x02_P1.27mm_Vertical"):
    p=f"/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/{f}.kicad_mod"
    txt=open(p).read(); print("=====",f)
    for lay in ("F.CrtYd","F.Fab"):
        xs=[];ys=[]
        for m in re.finditer(r"\(fp_line\b", txt):
            s=m.start(); d=0; i=s
            while i<len(txt):
                if txt[i]=='(': d+=1
                elif txt[i]==')':
                    d-=1
                    if d==0: break
                i+=1
            blk=txt[s:i+1]
            if f'(layer "{lay}")' not in blk: continue
            for a,b in re.findall(r"\((?:start|end)\s+(-?[\d.]+)\s+(-?[\d.]+)\)", blk):
                xs.append(float(a)); ys.append(float(b))
        print(f"  {lay}: X {min(xs):.4f}..{max(xs):.4f} (w={max(xs)-min(xs):.4f})  Y {min(ys):.4f}..{max(ys):.4f} (h={max(ys)-min(ys):.4f})")
PY

# ③ 本单机器闸 (★新建·★零挂链★)
python3 MECH/check_fts_seat_body_geometry.py
python3 MECH/check_fts_seat_body_geometry.py --selftest

# ④ 既有 MECH 闸 (★只读对照·★不许改★)
python3 MECH/check_debug_seat_3d_fit.py
python3 MECH/check_debug_seat_rework_spec.py --selftest

# ⑤ 零写板 / 零落表 指纹
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑥ 零挂链
grep -c check_fts_seat_body_geometry state/gate_check.py     # ★必须 = 0★

# ⑦ 收尾
python3 state/merge.py          # ★rc 必须 0★
python3 state/gate_check.py     # ★Q1 必须 18/18★
```

### ★§7.2 机器块 ★

<!-- MECH-FTS-SEAT-BODY-GEOMETRY-JSON-BEGIN -->
```json
{
  "doc": "MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md",
  "issue": "ISS-390",
  "agent": "mech-lead",
  "date": "2026-11-24",
  "subject": "FTS 直插档座体外形 (宽 X / 深 Y / 绝缘体高 Z) 官网查证 + courtyard 前提订正",
  "parts": ["FTS-104-01-F-S", "FTS-102-01-F-S"],

  "source_files": [
    {"path": "https://suddendocs.samtec.com/prints/fts-1xx-xx-x-sx-mkt.pdf",
     "channel": "curl_direct", "http": 200, "bytes": 190339,
     "md5": "69d9415867cd642d6a6e07c6b755516b",
     "title": "FTS-1XX-XX-X-SX-MKT (REVISION AE, 2022-07-27, 2 pages)",
     "evidence": "[官网]", "local_copy": "tmp/iss390_sbx/fts-1xx-xx-x-sx-mkt.pdf"},
    {"path": "https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf",
     "channel": "curl_direct", "http": 200, "bytes": 143472,
     "md5": "1cbe4a2bfa456d8fd030c8b76bdf8dd5",
     "note": "官方推荐 PCB 图: 只有 land/孔位, 无座体外形", "evidence": "[官网]"},
    {"path": "https://suddendocs.samtec.com/catalog_english/fts.pdf",
     "channel": "curl_direct", "http": 200, "bytes": 468445,
     "md5": "fa249db9454f92c77d7e0a5ef62a0ba6",
     "note": "FTS 家族目录页: 无外形图", "evidence": "[官网]"},
    {"path": "https://www.digikey.com/en/products/detail/samtec-inc/FTS-104-01-F-S/7342275",
     "channel": "search_backend", "note": "Insulation Height 0.034\" (0.86mm)",
     "evidence": "[媒体]"},
    {"path": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
     "channel": "local_measured", "note": "通用第三方库件: F.Fab 2.1000 x 5.0800 / F.CrtYd 3.1000 x 6.0900 / size 1 1 / drill 0.65",
     "evidence": "[实测]"},
    {"path": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x02_P1.27mm_Vertical.kicad_mod",
     "channel": "local_measured", "note": "通用第三方库件: F.Fab 2.1000 x 2.5400 / F.CrtYd 3.1000 x 3.5500",
     "evidence": "[实测]"}
  ],

  "body_geometry": {
    "FTS-104-01-F-S": {
      "positions": 4,
      "seat_body_width_x_mm":  {"value": "5.0800", "evidence": "[官网]", "degradation_id": "",
                                 "drawing_callout": "(NO OF POS x .0500 [1.27]) ±.010 [.25]  => N x 1.27"},
      "seat_body_depth_y_mm":  {"value": "2.1600", "evidence": "[官网]", "degradation_id": "",
                                 "drawing_callout": ".085 2.16 REF"},
      "insulator_height_z_mm": {"value": "0.8600", "evidence": "[官网]", "degradation_id": "",
                                 "drawing_callout": ".034 0.86 REF",
                                 "cross_check": "[媒体] DigiKey Insulation Height 0.034\" (0.86mm)"}
    },
    "FTS-102-01-F-S": {
      "positions": 2,
      "seat_body_width_x_mm":  {"value": "2.5400", "evidence": "[官网]", "degradation_id": "",
                                 "drawing_callout": "(NO OF POS x .0500 [1.27]) ±.010 [.25]  => N x 1.27"},
      "seat_body_depth_y_mm":  {"value": "2.1600", "evidence": "[官网]", "degradation_id": "",
                                 "drawing_callout": ".085 2.16 REF"},
      "insulator_height_z_mm": {"value": "0.8600", "evidence": "[官网]", "degradation_id": "",
                                 "drawing_callout": ".034 0.86 REF",
                                 "cross_check": "[媒体] DigiKey Insulation Height 0.034\" (0.86mm)"}
    }
  },

  "attribution": {
    "source_of_6_0900_5_0800_3_5500_2_5400": "generic_kicad_lib",
    "generic_parts": ["Connector_PinHeader_1.27mm.pretty:PinHeader_1x04_P1.27mm_Vertical",
                      "Connector_PinHeader_1.27mm.pretty:PinHeader_1x02_P1.27mm_Vertical"],
    "is_samtec_vendor_data": false,
    "samtec_vendor_body_values": {"x": ["5.0800", "2.5400"], "y": ["2.1600"], "z": ["0.8600"]},
    "samtec_has_courtyard_concept": false,
    "forbidden_phrasings": [
      "官方 land courtyard",
      "官方 land 的 F.Fab",
      "官方 land 的 `F.Fab`",
      "官方 land 的 `F.CrtYd`",
      "官方 land 自己的",
      "官方 1x4 THT 的 F.CrtYd",
      "官方 1x2 THT 的 F.CrtYd",
      "官方 1x4 THT 座体本体",
      "官方 1x2 THT 座体本体",
      "官方 1×4 THT 座体本体",
      "官方 1×2 THT 座体本体",
      "IPC 的 courtyard",
      "比 courtyard `6.0900` 还小"
    ],
    "forbidden_phrasings_note": "★本列表必须与 MECH/check_fts_seat_body_geometry.py 的 FORBIDDEN_MARKERS 逐条相等 (★闸的 G3.5 会校验·不许弱化闸★); ★收窄到【只有当『官方/厂件』这个定语直接挂在本机通用库件的 F.CrtYd / F.Fab 图元上】时才算误认 —— 「换官方 1×4 THT」这类说法指的是【把那颗连接器换成 FTS 厂件】, ★是合法的, 不在词表里★"
  },

  "oi12_recompute": {
    "status": "需重算",
    "status_enum": ["不需重算", "需重算", "待定"],
    "old_figure_0_5200": "作废 (前提无效: 对照物是通用库件 F.CrtYd, 厂件无 courtyard)",
    "new_figures": {
      "J_DEBUG_clear_x_vs_vendor_body": "6.6100 - 5.0800 = 1.5300 total => 0.7650/side",
      "J_UART_clear_x_vs_vendor_body": "4.0700 - 2.5400 = 1.5300 total => 0.7650/side (原写 0.7150, 订正 +0.0500/side)",
      "body_based_requirement": {"J_DEBUG_x": "6.8800 (缺 0.2700)", "J_UART_x": "4.3400 (缺 0.2700)", "y": "3.9600 (缺 1.1600)"}
    }
  },

  "impact": {
    "unchanged": ["6.6100", "4.0700", "0.1350", "2.6950", "0.7700",
                  "OI-5:1.7750", "OI-5:4.0850", "OI-5:4.8100"],
    "changed": ["OI-12:0.5200 作废", "ISS-389 路 A J_UART:0.7150 -> 0.7650"],
    "new_open_issue": {"id": "OI-390-1", "name": "罩住判据是否扩到座体本体",
                        "gap_x": "0.2700", "gap_y": "1.1600", "owner": "main+boss"},
    "affected_numbers_detail": [
      {"name": "6.6100", "change": false, "why": "铜箔 4.8100 + 2*0.9000, 与座体外形无关"},
      {"name": "4.0700", "change": false, "why": "铜箔 2.2700 + 2*0.9000, 与座体外形无关"},
      {"name": "0.1350", "change": false, "why": "(2.5400-2.2700)/2, 只用现有出件值+铜箔"},
      {"name": "2.6950", "change": false, "why": "(10.2000-max(H,C))/2, 座体外形不进 M"},
      {"name": "0.7700", "change": false, "why": "(2.5400-1.0000)/2, 只用 h 档 + 铜箔 Y"},
      {"name": "1.7750", "change": false, "why": "现状板读铜箔宽"},
      {"name": "4.0850", "change": false, "why": "3.81+0.275"},
      {"name": "4.8100", "change": false, "why": "3.81+1.00"},
      {"name": "0.7650", "change": false, "why": "(6.6100-5.0800)/2, 厂件 X 与通用 F.Fab 逐字相同"},
      {"name": "0.7150", "change": true, "why": "通用件含笔画 2.6400 -> 厂件 2.5400"},
      {"name": "0.5200", "change": true, "why": "对照物无效 => 作废"}
    ]
  },

  "oi_relations": {
    "OI-11": {"resolved_by_this": false,
              "reason": "OI-11 的 h 是罩/座体结构件的量 (三档 0.90/2.54/4.00, 决定清空区 Y 有效高); 本单 Z=0.8600 是连接器 LCP 绝缘体高, 主体不同, 不能顶替",
              "new_input_for_boss": "官网图 .120 [3.05] POST => 连接器板面以上实际占高 3.05 mm => h=0.90 档物理上装不下"},
    "OI-12": {"status": "需重算", "owner": "main+boss"},
    "OI-13": {"status": "代价变大", "detail": "Y 向从零余量卡死变为缺 1.1600; 第二个选项(接受零余量)已不存在", "owner": "main+boss"},
    "OI-14": {"status": "现状口径下不变 (4.0700)", "detail": "若 OI-12 采纳座体口径则 J_UART X 需求变 4.3400, OI-14 须同批改", "owner": "main"}
  },

  "corrections_registered": [
    {"id": "COR-1", "loc": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L634",
     "old": "官方 land courtyard 只给每边 0.6400", "new": "通用 KiCad 库件 PinHeader_1x0{4,2}_P1.27mm_Vertical 的 F.CrtYd; 厂件 FTS 座体本体 5.0800/2.5400 x 2.1600 x 0.8600 [官网]",
     "scan_substrings": ["官方 land courtyard 只给每边 0.6400"],
     "status": "待 main 落"},
    {"id": "COR-2", "loc": "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md L149/L154 (+L69/L90)",
     "old": "比 courtyard `6.0900` 还小 `0.0800`; 官方 1×4 THT 座体本体 (`F.Fab`) X `5.0800` × `2.1000`; 官方 1×2 THT 座体本体 (`F.Fab`) `2.6400` × `2.2000`",
     "new": "加限定语『通用 KiCad 库件的 F.CrtYd』; 座体本体统一成厂件实测 5.0800 x 2.1600 / 2.5400 x 2.1600 [官网]",
     "scan_substrings": ["比 courtyard `6.0900` 还小 `0.0800`", "IPC 的 courtyard", "官方 1×4 THT 座体本体", "官方 1×2 THT 座体本体", "官方 1x4 THT 座体本体", "官方 1x2 THT 座体本体", "官方 land 自己的", "官方 land 的 `F.CrtYd`"],
     "status": "待 main 落"},
    {"id": "COR-3", "loc": "MECH/check_debug_seat_3d_fit.py L848",
     "old": "而官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 判据要求比 courtyard 还大 0.5200",
     "new": "而【通用 KiCad 库件】的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 【该对照不成立: 厂件 FTS 座体本体 = 5.0800 x 2.1600 x 0.8600】(ISS-390)",
     "scan_substrings": ["官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 判据要求比 courtyard 还大 0.5200"],
     "status": "待 main 落"},
    {"id": "COR-4", "loc": "MECH/check_debug_seat_3d_fit.py L879",
     "old": "(★事实: 官方 1x4 THT 的 F.CrtYd 只有 6.0900 X, 而判据要求清空区 6.6100 ⇒ 比 courtyard 还大 0.5200★)",
     "new": "(★事实: 通用 1x4 库件的 F.CrtYd 是 6.0900 X; 厂件 FTS-104-01-F-S 座体本体 = 5.0800 X ⇒ 判据要求清空区 6.6100 比【厂件座体本体】每边多让 0.7650; 那个 0.5200 的对照物无效★)",
     "scan_substrings": ["官方 1x4 THT 的 F.CrtYd 只有 6.0900 X, 而判据要求清空区 6.6100 ⇒ 比 courtyard 还大 0.5200"],
     "status": "待 main 落"},
    {"id": "COR-5", "loc": "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md L26/L114/L168/L193 + 机器块 L854",
     "old": "官方 land 自己的 F.Fab 5.0800 X、F.CrtYd 是 6.0900 X ⇒ 判据要求的 6.6100 比 courtyard 还大 0.5200 ⇒ 这条判据对 THT 排针偏紧",
     "new": "通用库件值 => 对照无效 => 0.5200 作废; 改用厂件座体本体 5.0800 => 每边多让 0.7650; 新增座体口径缺口 X 0.2700 / Y 1.1600",
     "scan_substrings": ["官方 land 自己的", "官方 land 的 `F.CrtYd`", "官方 land 的 F.Fab 5.0800", "官方 1x4 THT 的 F.CrtYd"],
     "status": "待 main 落"},
    {"id": "COR-6", "loc": "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md L118 + MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md L139",
     "old": "官方 1×2 THT 座体本体 (`F.Fab`) `2.6400` × `2.2000` / 官方 1×4 THT 座体本体 (`F.Fab`) X `5.0800` × `2.1000`",
     "new": "统一成厂件实测 5.0800 x 2.1600 / 2.5400 x 2.1600 [官网]; 通用库件值保留为对照列并注明口径",
     "scan_substrings": ["官方 1×2 THT 座体本体", "官方 1×4 THT 座体本体"],
     "status": "待 main 落"}
  ],

  "degradation": {
    "path_a": {"status": "succeeded",
               "note": "官网 3D/CAD 件本机拿不到 (/3d/ /cad/ 全 403), 但同域 prints/ 下的 -mkt 官方机械图给了完整三量",
               "evidence": "[官网]"},
    "path_b": {"id": "fallback_b_caliper",
               "status": "armed_for_preassembly_crosscheck",
               "trigger": "装配前对不上或图纸读数被质疑 (不是『官网查不到』)",
               "who": "装机组第一站的人 (量) -> mech-lead (核对 + 回填)",
               "when": "落 FTS 时先打一块单板样, 焊接完成后、装进镜脚内腔之前",
               "measure": ["座体宽 X = 塑壳沿排距两端外表面间距 (期望 5.0800 / 2.5400)",
                           "座体深 Y = 塑壳跨排距前后外表面间距 (期望 2.1600)",
                           "绝缘体高 Z = 塑壳底面到顶面高度 (期望 0.8600; 别把 3.05 的柱高当塑壳高)"],
               "fill_back_to": "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md 机器块 keepout_dwg 行 + 本页 body_geometry.*",
               "closed_when": "OI-387-4 关闭"},
    "blocked_on_external_reply": false
  },

  "decisions": {
    "oi12_over_strict_decision": "not_decided_here",
    "body_based_criterion_decision": "not_decided_here",
    "oi11_h_lock_decision": "not_decided_here"
  },

  "boundaries": {
    "board_untouched": true,
    "netlist_bom_untouched": true,
    "signed_off_pages_unmodified": true,
    "signed_off_gates_unmodified": true,
    "zero_chain": true,
    "zero_outbound": true,
    "no_iss_log_edit": true,
    "sandbox_dirs_only": ["tmp/iss390_sbx/", "logs/iss390/"]
  }
}
```
<!-- MECH-FTS-SEAT-BODY-GEOMETRY-JSON-END -->

★**机器块要点**: ★**三量逐项有值 + 证据等级 ∈ 五级白名单** ; ★**对照物写死 `source_of_6_0900_5_0800_3_5500_2_5400 = generic_kicad_lib`** ; ★**`oi12_recompute.status = "需重算"` (三值之一) + 受影响数名清单从 §5 机器块读** ; ★**三个 `*_decision` 字段全是 `not_decided_here`** ★

---

## ★§8 边界自证 ★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 前后逐字相同 ★ |
| ★零落表★ | ★网表 `6aee500e…` · 脚表 `9174309d…` · BOM `5b999399…` 前后逐字相同 ★ |
| ★零改既有闸★ | ★`MECH/check_debug_seat_3d_fit.py` md5 `667e6006280cc8c0533d8ce8fa39f8be` · `MECH/check_debug_seat_rework_spec.py` md5 `babadd6b073d691374051ea7409a6a1f` 与基线同 (★**含 L848 / L879 两个字符串一个字未动**★) ★ |
| ★零改既有页面正文★ | ★ISS-389 / ISS-387 / ISS-386 已签收页 md5 与基线同 (★**订正只登记在 §4 / 机器块 `corrections_registered`, 一律 `待 main 落`**★) ★ |
| ★零挂链★ | ★`grep -c check_fts_seat_body_geometry state/gate_check.py` = `0` ★ |
| ★零外发★ | ★全程只读本机 + 自己上官网查; ★`state/outbox/` 一个字节未动; ★**零邮件 / 零询价 / 零问询 / 零采购** ★ |
| ★不代拍★ | ★★**厂件外形的最终采用值 / `OI-11` 的 `h` / `OI-12` 过不过严 / 判据要不要扩到座体本体 —— 全是 main / boss 的裁决权 ⇒ 本单只摆证据与代价; 机器块 `decisions.*` 三项全是 `not_decided_here`** ★★ ★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 一个字节未动 ★ |
| ★没写别人的分片★ | ★只写 `state/fragments/mech.yaml` ★ |
| ★沙盒纪律★ | ★只落 `tmp/iss390_sbx/` 与 `logs/iss390/`; ★**未写系统 `/tmp` · 未 `cp -al` · 未硬链接** ★ |
| ★证据分级★ | ★每条结论标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 之一 ★ |
