# `J_UART` 排针 land 改 1.27mm · 结构侧净距真相 (ISS-374)

> ★**一句话答案** ★**方向与姊妹件 `J_DEBUG` 相反**: ★**`J_UART` 换官方 1×2 THT land 后铜箔 X 宽 `2.2700` ⇒ 座体必须清空区 X 宽只剩 `2.5400` ⇒ 每边余量 `0.1350` < `CRIT` `0.60` ⇒ 铜箔不再被座体完全罩住 ⇒ 结构件装不上** ★
> ★**姊妹件 `J_DEBUG` 换官方 1×4 THT land 后余量 `2.6950` (3.99×) ⇒ 仍过 `CRIT`** ★
> ★**⇒ 两件清空区口径【不同源】(`J_DEBUG` = 铜箔支配 / `J_UART` = 座体支配) ⇒ 方向相反的根因就在这里** ★
> ★**⇒ 那一趟若照 `B33` 把 `J_UART` 也换成官方 land ⇒ 结构件要返工, 或者板 md5 变第二次 ⇒ 整趟白跑** ★

★**派活**: 项目总工 (main) · ISS-374 · 2026-11-23 派 / 2026-11-24 01:1x 做 · 交卷人 = 结构总工 (mech-lead) ★
★**关联**: `MECH/check_juart_1p27_clearance.py` (★本单新建的机器闸★) · `HANDOFF/2026-11-23_mech-lead_ISS374_JUART排针1.27净距真相.md` (交卷页) ·
★**姊妹件 (ISS-371 · 已签收 · 本页只读不改)**: `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` · `MECH/check_jdebug_1p27_clearance.py` ★
★**板侧项**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` (★本单不重复发明板侧项编号★) ★
★**沙盒留证**: `tmp/iss374_sbx/` (板副本 `board_S1/S2/S3.kicad_pcb` + `sbx_measure.py`) · `logs/iss374/sbx_S0.json` / `sbx_S1.json` / `sbx_S2.json` / `sbx_S3.json` ★

★**证据等级**: `[实测]` = 本机读盘读到的 · `[推算]` = 由实测值按公式推导 · `[0数据]` = 本机无实物、量不到 ★

---

## §0 口径与读数 · `J_UART` 与 `J_DEBUG` 并排对照表

★**这一节是本单的正题** ★ ⇒ ★**两件必须并排摆着看** ★

| 项 | ★`J_UART` (1×2) ★ | ★`J_DEBUG` (1×4) ★ |
|---|---|---|
| 焊盘数 / 现状 land pitch | 2 / `0.5000` `[实测]` | 4 / `0.5000` `[实测]` |
| 现状 pad 尺寸 / 类型 | `0.2750 × 0.9000` · 全 SMD · 全 `shape=1 (RECT)` `[实测]` | `0.2750 × 0.9000` · 全 SMD · 全 `shape=1 (RECT)` `[实测]` |
| 现状净名 | `UART_TX` / `UART_RX` `[实测]` | `JTAG_TCK` / `TMS` / `TDI` / `TDO` `[实测]` |
| 现状铜箔 X 区间 / 宽 | ★`18.5025..19.2775` (宽 `0.7750`) ★`[实测]` | ★`142.0625..143.8375` (宽 `1.7750`) ★`[实测]` |
| 现状铜箔 Y 区间 / 宽 | `68.1500..69.0500` (`0.9000`) `[实测]` | `56.1500..57.0500` (`0.9000`) `[实测]` |
| 现状 fab 外框 (含笔画) | X `17.6900..23.7900` (`6.1000`) × Y `67.9500..72.0500` (`4.1000`) `[实测]` | X `141.2500..147.3500` (`6.1000`) × Y `55.9500..60.0500` (`4.1000`) `[实测]` |
| 封装原点 / orient | `(20.7400, 70.0000)` / `0.0` `[实测]` | `(144.3000, 58.0000)` / `0.0` `[实测]` |
| ★**官方 land 封装真值** ★ | ★`PinHeader_1x02_P1.27mm_Vertical` (THT) + 两个 SMD 变体 ★`[实测]` | ★`PinHeader_1x04_P1.27mm_Vertical` (THT) ★`[实测]` |
| ★**官方 THT 铜箔 X 宽** ★ | ★**`2.2700`** ★`[实测]` | ★**`4.8100`** ★`[实测]` |
| ★**必须清空区 X 区间 / 宽** ★ | ★**`17.620..20.160` (宽 `2.5400`) ★`[实测]`** ★ | ★**`142.063..143.838` (宽 `1.7750`) ★`[实测]`** ★ |
| ★**必须清空区 X 宽的支配源** ★ | ★★**座体宽支配** (MECH 现行模型「座体 `2.54 × 2.54` 假设」· 固定值) ★★`[实测]`** ★ | ★★**铜箔宽支配** (MECH 现行模型「调试口 座体宽 `1.775` = 板读铜箔宽」· **随铜箔走**) ★★`[实测]`** ★ |
| 必须清空区 Y 区间 | `67.330..69.870` (`2.5400`) `[实测]` | `55.330..57.870` (`2.5400`) `[实测]` |
| 开口 X / Y 区间 | `13.790..23.990` / `66.300..70.900` `[实测]` | `137.850..148.050` / `54.300..58.900` `[实测]` |
| 清空区↔开口 单边间隙 X / Y | `3.830` / `1.030` (最坏 `3.530` / `0.730`) `[推算]` | `4.213` / `1.030` (最坏 `3.913` / `0.730`) `[推算]` |
| ★**换官方 THT 后 每边余量** ★ | ★★**`0.1350`** ★★ (最坏 `-0.1650`) ★`[推算]` ★ | ★★**`2.6950`** ★★ (最坏 `2.3950`) ★`[推算]` ★ |
| ★**换官方 THT 后 ≥ `CRIT` `0.60` ?** ★ | ★★**❌ 不过** ★★ | ★★**✅ 过 (3.99×)** ★★ |
| ★**方向结论** ★ | ★★**红**: 铜箔进座体必须清空区 ⇒ 结构件装不上 ★★ | ★★**绿**: 余量 3.99×, 不构成装不下 ★★ |

★**★「口径不同源」这一行是本单的全部根因** ★
★**① `J_DEBUG` 的必须清空区 X 宽 = 铜箔 X 宽** ⇒ 换 land ⇒ 清空区跟着变宽 (`1.7750` ⇒ `4.8100`) ⇒ 「铜箔 ⊂ 清空区」永远成立 ⇒ 真正卡人的变成【开口 vs 铜箔】⇒ `2.6950` 过阈 ★
★**② `J_UART` 的必须清空区 X 宽 = 座体模型 `2.5400`** (★**固定值**·★**不随铜箔走**★) ⇒ 换 land ⇒ 铜箔变宽而清空区不动 ⇒ 铜箔顶到座体 ⇒ 每边余量塌到 `0.1350` ★
★**⇒ 【不许】把 `J_DEBUG` 的推导链套到 `J_UART` 上** ★ ⇒ ★**本单的机器闸 `J5` 就是专门防这一条的** ★

★**判据常量 (真身只读·不许写死进闸)** ★
★`CRIT = 0.60` = `2 × TOL["fdm_part"]` · `TOL["fdm_part"] = 0.30` ⇒ 真身 `MECH/service_port_check.py` **L126-L127** `[实测]` ★

---

## §1 官方 land 实读 (★读盘上 `.kicad_mod` 本体·不许抄文档★)

★**库目录**: `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/` (★本机 KiCad 10.0.8 官方库★) `[实测]` ★

### §1.1 `.kicad_mod` md5 台账 (★`J7` 要扫这一段★)

| 文件 | md5 |
|---|---|
| `PinHeader_1x02_P1.27mm_Vertical.kicad_mod` | `47bcbf6d0f267d543e50d4b2a8dfabf5` `[实测]` |
| `PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod` | `7f15e4a1a32059c2b8eea027edfdbd84` `[实测]` |
| `PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Right.kicad_mod` | `25ab0efebb8f5df0066508b9686820d7` `[实测]` |
| `PinHeader_1x04_P1.27mm_Vertical.kicad_mod` | `7a5f470c1f70d4b832be258501945385` `[实测]` |

### §1.2 官方 1×2 THT land (`PinHeader_1x02_P1.27mm_Vertical.kicad_mod`) `[实测]`

| 项 | 实读值 |
|---|---|
| 封装名 / version / generator | `PinHeader_1x02_P1.27mm_Vertical` / `20260206` / `kicad-footprint-generator` |
| descr / tags | `Through hole straight pin header, 1x02, 1.27mm pitch, single row` |
| attr | `through_hole` |
| `KiLib_Generator` | `connector/pin_header_socket` |
| ★pad `1` ★ | `thru_hole rect` · `(at 0 0)` · `(size 1 1)` · `(drill 0.65)` · `(layers "*.Cu" "*.Mask")` · `(remove_unused_layers no)` |
| ★pad `2` ★ | `thru_hole circle` · `(at 0 1.27)` · `(size 1 1)` · `(drill 0.65)` · `(layers "*.Cu" "*.Mask")` |
| ★`fp_rect` (F.CrtYd) ★ | `start -1.55 -1.14` · `end 1.55 2.41` ⇒ `3.1000 × 3.5500` · stroke `0.05` |
| `F.Fab` 轮廓线 | X `-1.05..1.05` (`2.1000`) × Y `-0.635..1.905` (`2.5400`) · stroke `0.10` ⇒ 含笔画 `2.2000 × 2.6400` |
| 3D 模型 | `${KICAD10_3DMODEL_DIR}/Connector_PinHeader_1.27mm.3dshapes/PinHeader_1x02_P1.27mm_Vertical.step` |
| ★**环宽 (annular ring)** ★ | ★**`0.1750`** = (`1.0000` pad − `0.6500` drill) ÷ 2 `[推算]` ★★ ⇒ ★**厂家允许的环宽下限 = `[0数据]`** (本机无数据手册实物)★ ★ |

★**⇒ 摆成板上 X 向 1×2 直排 (rot 90°) 后的铜箔 X 宽 = 跨距 `1.2700` + pad 宽 `1.0000` = `2.2700`** `[推算]`
★**⇒ 沙盒 S1 实测铜箔 X 宽 = `2.2700`** `[实测]` (★两者相等 ⇒ 推导链成立★) ★

### §1.3 官方 1×2 SMD 降级变体 (`Pin1Left` / `Pin1Right`) —— ★**几何与 THT 完全不同, 各算各的**★ `[实测]`

| 项 | ★`..._SMD_Pin1Left` ★ | ★`..._SMD_Pin1Right` ★ |
|---|---|---|
| attr / descr | `smd` · `... single row, style 1 (pin 1 left)` | `smd` · `... single row, style 1 (pin 1 right)` |
| ★pad `1` ★ | `smd rect` · `(at -1.5 -0.635)` · `(size 3 0.65)` · `(layers "F.Cu" "F.Mask" "F.Paste")` | `smd rect` · `(at 1.5 -0.635)` · `(size 3 0.65)` |
| ★pad `2` ★ | `smd rect` · `(at 1.5 0.635)` · `(size 3 0.65)` | `smd rect` · `(at -1.5 0.635)` · `(size 3 0.65)` |
| `fp_rect` (F.CrtYd) | `-3.5 -1.77` .. `3.5 1.77` ⇒ `7.0000 × 3.5400` | 同左 (逐字相同) |
| `F.Fab` 体轮廓 | X `-2.5..2.5` · Y `-1.27..1.27` | 同左 |
| ★焊盘排距 (局部 Y) ★ | `1.2700` | `1.2700` |
| ★**铜箔 X 包络 (rot 90° 后)** ★ | ★**`1.9200`** ★ `[实测]` | ★**`1.9200`** ★ `[实测]` |
| ★**铜箔 Y 包络 (rot 90° 后)** ★ | ★**`6.0000`** ★ `[实测]` | ★**`6.0000`** ★ `[实测]` |
| ★pad 序落板位 (rot 90°, 原点 `20.74/70.00`) ★ | pad1 `(20.105, 71.500)` · pad2 `(21.375, 68.500)` | pad1 `(20.105, 68.500)` · pad2 `(21.375, 71.500)` |
| ★**座体本体外框 (F.Fab 轮廓线·不含文字)** ★ | X `19.4200..22.0600` (`2.6400`) × Y `67.4500..72.5500` (`5.1000`) `[实测]` | 同左 `[实测]` |
| (留档) `F.Fab` 层全框 (含 `Reference` 文字) | X `18.0198..23.4602` (`5.4405`) × Y `67.4500..72.5500` (`5.1000`) `[实测]` | 同左 `[实测]` |

★**⇒ 两个 SMD 变体铜箔包络【逐字相同】, 只有 pad 1/2 的落板位置互为镜像** ★
★**⇒ 两个变体都是【卧式贴片排针】(3D 形态 = 体坐在板面上, 6mm 长边躺在 Y 向) ⇒ 与现页「座体高 `2.54` 竖立」的 3D 假设【不同构】 ⇒ 不能只算 X** ★
★**⇒ ★不许拿 THT 的数套到 SMD 变体上 (★闸 `J1` / `J4` 各查一遍★)★ ★

---

## §2 三档量差表 (★现状 / 官方 THT / 官方 SMD 变体★)

★**判据口径 (本单唯一口径, 与 ISS-371 的口径【不同源】)**: ★**铜箔 X 宽必须被座体必须清空区 X 宽完全罩住, 每边余量 ≥ `CRIT`** ★
★`每边余量 = (座体必须清空区 X 宽 − 铜箔 X 宽) ÷ 2` · ★`最坏余量 = 每边余量 − TOL["fdm_part"] (0.30)` (★FDM 座体/罩外形公差往内吃, 与 `MECH/service_port_check.py` L225-L232 的口径同源★) `[推算]` ★

| 档 | 铜箔 X 宽 | 铜箔 Y 宽 | 居中后铜箔 X 区间 | 每边余量 | 最坏余量 | ★**座体本体外框 (X × Y)** ★ | ≥ `CRIT` `0.60` ? |
|---|---|---|---|---|---|---|---|
| ★**现状 (S0)** ★ | `0.7750` `[实测]` | `0.9000` `[实测]` | `18.5025..19.2775` | `0.8825` `[推算]` | `0.5825` `[推算]` | `6.1000 × 4.1000` `[实测]` | ★**名义过 / ★最坏不过 (差 `0.0175`)** ★ |
| ★**官方 THT (S1)** ★ | `2.2700` `[实测]` | `1.0000` `[实测]` | `17.7550..20.0250` | ★**`0.1350`** ★`[推算]` | ★**`-0.1650`** ★`[推算]` | ★**`2.6400 × 2.2000`** ★`[实测]` | ★★**❌ 不过 (差 `0.4650`)** ★★ |
| ★**官方 SMD `Pin1Left` (S2)** ★ | `1.9200` `[实测]` | ★**`6.0000`** ★`[实测]` | `17.9300..19.8500` | `0.3100` `[推算]` | `0.0100` `[推算]` | ★**`2.6400 × 5.1000`** ★`[实测]` | ★★**❌ 不过 (X 差 `0.2900`; ★Y 向 `6.0000` 直接撞开口 Y `66.300..70.900`, 每边越界 `0.7000`)★★** ★ |
| ★**官方 SMD `Pin1Right`** ★ | `1.9200` `[实测]` | `6.0000` `[实测]` | `17.9300..19.8500` | `0.3100` `[推算]` | `0.0100` `[推算]` | ★**`2.6400 × 5.1000`** ★`[实测]` | ★★**❌ 不过 (与 `Pin1Left` 同)★★** ★ |

★**★「座体本体外框」这一列的口径 (★不许混用·2026-11-24 04:xx 复核时专门钉死★)★**: ★**= `F.Fab` 层上【`PCB_SHAPE` 轮廓线】的并集外框 (含笔画半宽), 【不含 `PCB_TEXT` 参考文字】** ★`[实测]` ★
★**⇒ 它才是「结构件要开的那个洞」该看的尺寸** ★ ⇒ ★**S1 官方 THT 座体本体 = `2.6400 × 2.2000`** ★ (★与 `.kicad_mod` 的 `F.Fab` 本体 `2.10 × 2.54` (局部) 旋转 90° 后 `2.54 × 2.10` + 笔画 `0.10` 两路相等 ⇒ 推导链成立★) ★
★**⇒ ★**本表原来那一列写的是「`F.Fab` 层【全框】(含 `Reference` 参考文字)」⇒ S1/S2 报出 `5.4405` ⇒ 那是文字宽 (`J_UART` 六个字符), 不是座体 ⇒ ★**已订正为座体本体口径**★★ ★
★**⇒ 文字全框只作留档, 不进结构判断**: ★**S1/S2 = `5.4405` × (`2.2000` / `5.1000`) ; S3 `J_DEBUG` = `6.7262` × `2.2000` ; S0 现状 = `6.1000 × 4.1000` (板上自绘封装 `F.Fab` 层上无参考文字)** ★`[实测]` ★
★**复跑**: ★**`bash state/pcbnew_py.sh tmp/iss374_sbx/sbx_measure.py S1 measure` ⇒ 看 `fab_body_bbox_mm` / `fab_text_bbox_mm` 两个字段 (★2026-11-24 04:xx 加的·之前只有混口径的 `fab_bbox_mm`★)** ★

★**「居中后铜箔 X 区间」怎么来的** `[推算]`: ★**座体必须清空区 X 中心 = `18.8900`** ⇒ 铜箔中心对齐到 `18.8900` ★
★**⇒ 官方 THT 档的落点必须从 `(20.7400, 70.0000)` 挪到 `(18.2550, 68.6000)`** (★X 挪 `-2.4850` · Y 挪 `-1.4000`·★**不是落点不动**)★ ★
★**⇒ 落点不动 (沿用 `(20.7400, 70.0000)`) rot 90° ⇒ 铜箔 X `20.2400..22.5100` ⇒ 整块铜箔落在座体必须清空区 `17.620..20.160` 的右侧之外 (左沿 `20.2400` 已越过清空区右沿 `20.1600` 达 `0.0800`) ⇒ 立即装配干涉** `[实测]` ★

★**★现状档的 `0.0175` 是一个【追加发现】, 不是本单造成的** ★
★**⇒ 现状每边余量名义 `0.8825` 过阈, 但最坏口径 (`−0.30`) = `0.5825` < `0.60` ⇒ 现状本身已经压在判据线上** `[推算]` ★
★**⇒ 这条要不要写进既有页 (`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md`) ⇒ 归 main 裁决 (§4-④) ⇒ 本单【不】动那一页** ★

★**★Y 向的口径说明 (★不许混算★)** ★
★**① 上表的「铜箔 Y 宽」只是几何事实; 「Y 向撞开口」这一句只在 SMD 变体档成立** ★
★**② 现状 / THT 两档的铜箔 Y 宽 (`0.9000` / `1.0000`) 都小于座体必须清空区 Y 宽 `2.5400` ⇒ Y 向不构成卡点** ★
★**③ SMD 变体档的铜箔 Y 宽 `6.0000` ⇒ 居中后 Y `65.6000..71.6000` ⇒ 上下各越出开口 Y (`66.300..70.900`) `0.7000` ⇒ 红灯** ★
★**④ 座体真实高度 `h` = `[0数据]` (ISS-267 F-8) ⇒ 开口 Y 的一切数等真实型号定版后重算 (★本单不改这一条★)** ★

---

## §3 两个后果 (★**结论必须分成两段写·不许混成一句含混的「过」★**)

### §3.1 ★★后果句 (★那一条会发生什么·事实层★)★★

> ★**事实句**: ★**若那一趟按 `B33` 把 `J_UART` 也换成官方 1×2 THT land (`PinHeader_1x02_P1.27mm_Vertical`), 则铜箔 X 宽 `0.7750` ⇒ `2.2700`; 座体必须清空区 X 宽仍是 `2.5400` (★座体支配★·不随铜箔走★); 每边余量 `0.8825` ⇒ `0.1350`, 最坏 `-0.1650` ⇒ 每边比 `CRIT` `0.60` 少 `0.4650` ⇒ 铜箔不再被座体完全罩住 ⇒ 铜箔进座体必须清空区 ⇒ 结构件装不上** ★

> ★**事实句 (落点位)**: ★**落点若不动 (`20.7400, 70.0000`) rot 90°, 铜箔 X 落 `20.2400..22.5100`, 整块落在清空区 `17.620..20.160` 之外 ⇒ 装配当场干涉; 必须同时把落点挪到 `(18.2550, 68.6000)`** ★

> ★**事实句 (SMD 变体)**: ★**换 SMD 变体也不救: 铜箔 X 宽 `1.9200` ⇒ 每边余量 `0.3100` (< `CRIT`); 且该变体是卧式贴片排针, 铜箔 Y 宽 `6.0000` ⇒ 居中后上下各越出开口 `0.7000` ⇒ 红灯更硬** ★

### §3.2 ★★判据句 (★方向本身能不能救·结论层★)★★

> ★**判据句**: ★**方向仍可救, 但代价落在结构件与板侧项上, 不落在「判据松不松」上** ★
> ★**⇒ 「松判据」这条路不走** (`CRIT` `0.60` 是 `MECH/service_port_check.py` L126-L127 的真身, 本单一个数字没动) ★
> ★**⇒ 下面是四条降级方案, 每条给代价, ★**本单不代拍**★ (★「那一趟 `J_UART` 换不换 land」是 main 的裁决权★)**

| # | 方案 | 结构侧代价 | 板侧代价 | 谁来裁 |
|---|---|---|---|---|
| ★**①** ★ | ★**座体必须清空区 X 宽从 `2.5400` 放宽到 ≥ `2.2700 + 2 × 0.60 = 3.4700`** ★ | ★**结构件必须清空区 X 改 `17.620..20.160` ⇒ `16.960..21.620` (中心 `18.890` 不变·宽 `+0.9300`) ⇒ 结构件返工一次** ★ | ★**落点必须从 `20.7400` 挪到 `18.2550` (X `-2.4850`) ⇒ 板那一趟同批改, 否则干涉** ★ | ★**mech-lead (结构件) + 老板 (结构口径) + main (板那一趟批不批) ★** |
| ★**②** ★ | ★**换 SMD 变体 (`Pin1Left` / `Pin1Right`)** ★ | ★**铜箔 X 宽 `1.9200` ⇒ 余量 `0.3100` 仍 < `CRIT`; 且铜箔 Y 宽 `6.0000` ⇒ 撞开口 Y 每边 `0.7000` ⇒ 结构件口径要整体重做 (卧式 3D 形态)** ★ | ★**pad 序落板位互为镜像 ⇒ ★**pad 序对调是板侧+硬件侧的活, 本单不代拍** ★**; 且 X 向铜箔还要挪 `1.8500`** ★ | ★**main (板侧) + hw-lead (选型/座体) ★** |
| ★**③** ★ | ★**`J_UART` 这颗改选型 / 改座体** (★换一颗 X 宽 ≤ `1.3400` 的 1×2 排针 · ★`1.3400 = 2.5400 − 2 × 0.60`★) | ★**结构件按现有 `2.5400` 清空区不动 ⇒ 结构件零返工** ★ | ★**`B33` 把 `J_UART` 排除在换 land 名单外 ⇒ 板那一趟只动 `J_DEBUG`** ★ | ★**main (板侧名单) + hw-lead (选型) ★** |
| ★**④** ★ | ★**降级: `J_UART` 这一颗那一趟不换 land** ★ | ★**结构件零返工; 但现状最坏余量 `0.5825` < `0.60` 这条要一并登记 (§4-④)** ★ | ★**要动 `B33` 的范围 ⇒ 归 main** ★ | ★**main** ★ |

★**⇒ 四条里只有 ③ 与 ④ 能让结构件零返工; ★① 要结构件 + 板那一趟同批改; ★② 结构件与板侧都要重做** ★
★**⇒ 本单【不代拍】; 本单只给代价** ★

---

## §4 未决项 (★只登记·不代拍★)

| # | 未决 | 要谁回答什么 | 为什么不能由本单回答 | 代价 / 期限 |
|---|---|---|---|---|
| ★**①** ★ | ★**座体必须清空区要不要放宽到 `3.4700`?** ★ | ★**boss (结构口径) + mech-lead (结构件) 回答: 「座体必须清空区 X 宽按 `2.5400` 还是按 `3.4700` 出件?」 ★ | ★**座体真实型号 = `[0数据]` (ISS-267 F-8) ⇒ `2.5400` 本身是 MECH 现行模型假设, 不是实物** ★ | ★**要结构件返工 ⇒ 必须与板那一趟同批定, 否则撞「板只改一次」** ★ |
| ★**②** ★ | ★**那一趟 `J_UART` 换不换 land?** ★ | ★**main 回答: 「`B33_PIN_LAND_1P27` 的范围是只含 `J_DEBUG`, 还是含 `J_DEBUG` + `J_UART`?」 ★ | ★**板那一趟的裁决权在 main; 本单只给结构侧代价与判据, 不代 main 裁** ★ | ★**与 ISS-373 同一件事的两条腿; 本单是结构侧那条腿** ★ |
| ★**③** ★ | ★**座体真实型号仍未定 (`ISS-267 F-8`)** ★ | ★**hw-lead (选型) 回答: 「`J_UART` 用哪颗具体型号?」 ⇒ mech-lead 复核** ★ | ★**本机无实物 ⇒ 座体高 `h` 与体宽全部 `[0数据]` ⇒ 开口 Y 的一切数等定版后重算** ★ | ★**定版后本页 §2 全表要重算 (公式在 §5)** ★ |
| ★**④** ★ | ★**现状最坏余量 `0.5825` < `CRIT` `0.60` (差 `0.0175`) 这条要不要落进 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md`?** ★ | ★**main 回答: 「要不要以追加式订正块的形式落进那一页?」 ★ | ★**本单边界 = 零改既有页面正文 ⇒ 订正块只写在本单这一页 §2, 由 main 决定要不要往既有页落** ★ | ★**差 `0.0175` 落在 FDM 公差口径上 ⇒ 若最终口径改口径, 这条要重算** ★ |
| ★**⑤** ★ | ★**官方 THT land 的落点偏移量 `-2.4850 / -1.4000` 由谁落?** ★ | ★**hw-lead (板那一趟落表) 回答: 「`J_UART` 换 land 时落点挪到 `(18.2550, 68.6000)`, 认不认?」 ★ | ★**本单是结构侧, 不落表 (★零落表边界★)** ★ | ★**不认 ⇒ 落点不动 ⇒ 装配当场干涉 (§3.1)** ★ |

★**★追加式订正块 (★按 cont1 要求: 订正既有页面的部分写成块放本页 §4, 由 main 决定要不要往既有页面落·★本单【不】动既有页面★)** ★
> ★**订正块 (候选 1)**: ★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.5 表格「检修口 · 必须清空区 (座体宽 `2.540`, ★MECH 现行模型; 板读铜箔宽只有 `0.775`★)」★ ⇒ ★**追加一句**: ★「★**该行只对【现状 land】成立; 若 `J_UART` 换官方 1×2 THT land (铜箔 X 宽 `2.2700`), 该行失效 ⇒ 座体必须清空区 X 宽须 ≥ `3.4700` 方能保住 `CRIT`** ★ (★见 `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` §3.2 方案 ①·★见 ISS-374★)」★ ★
> ★**订正块 (候选 2)**: ★`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.5 表格「检修口 · 必须清空区 X `17.620..20.160`」★ ⇒ ★**追加一句**: ★「★**本区为【座体支配】口径, 固定值; 与 `J_DEBUG` 的【铜箔支配】口径不同源 ⇒ 两件的换 land 方向相反** ★ (★ISS-374 §0★)」★ ★

---

## §5 复跑命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ★本单机器闸 (新建) ★
python3 MECH/check_juart_1p27_clearance.py                     # rc=0
python3 MECH/check_juart_1p27_clearance.py --selftest           # rc=0 (末行 ALL TESTS PASS)

# ★沙盒 S0~S3 (只落 tmp/iss374_sbx/ + logs/iss374/) ★
bash state/pcbnew_py.sh tmp/iss374_sbx/sbx_measure.py S0 measure
bash state/pcbnew_py.sh tmp/iss374_sbx/sbx_measure.py S1 swap && bash state/pcbnew_py.sh tmp/iss374_sbx/sbx_measure.py S1 measure
bash state/pcbnew_py.sh tmp/iss374_sbx/sbx_measure.py S2 swap && bash state/pcbnew_py.sh tmp/iss374_sbx/sbx_measure.py S2 measure
bash state/pcbnew_py.sh tmp/iss374_sbx/sbx_measure.py S3 swap && bash state/pcbnew_py.sh tmp/iss374_sbx/sbx_measure.py S3 measure

# ★板面读数 (本机 KiCad 10.0.8) ★
bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');\
print([ (f.GetReference(), len(f.Pads())) for f in b.GetFootprints() if f.GetReference() in ('J_DEBUG','J_UART') ])"

# ★官方 land 实读 (读盘上 .kicad_mod 本体) ★
grep -nE '\(pad |drill|fp_rect|\(at ' /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x02_P1.27mm_Vertical.kicad_mod
md5sum /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x0*.kicad_mod

# ★CRIT 真身 (不许写死) ★
grep -nE 'CRIT|TOL\["fdm_part"\]' MECH/service_port_check.py

# ★座体必须清空区 + 开口 (只读) ★
grep -nE '17\.620|20\.160|67\.330|69\.870|13\.790|23\.990' MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md

# ★零写板自证 + 零挂链自证 ★
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
grep -c check_juart_1p27_clearance state/gate_check.py
```

★**§2 全表的重算公式 (★座体真实型号定版后照这张表重算·★不用重读文档★)** ★
```
座体必须清空区 X 宽      = 2.5400            (★MECH 现行模型·[0数据] 待定版★)
每边余量 (名义)          = (座体清空区 X 宽 − 铜箔 X 宽) ÷ 2
最坏余量 (FDM ±0.30)     = 每边余量 − 0.30
判据                      = 0.60              (CRIT = 2 × TOL["fdm_part"])
铜箔 X 宽 (THT 1×2)      = 1.2700 + 1.0000   = 2.2700
铜箔 X 宽 (SMD 1×2)      = 2 × 0.6500 + 0.6350×2 ... ⇒ 1.9200   (★以实算 1.9200 为准★)
过阈门槛 (铜箔 X 宽上限) = 座体清空区 X 宽 − 2 × 0.60 = 2.5400 − 1.2000 = 1.3400
```

---

## §6 边界自证 (★本单做到了什么 / 没做什么★)

| 边界 | 本单做法 | 自证 |
|---|---|---|
| ★**零写板** ★ | 只 `LoadBoard` 只读; 换封装只对 `tmp/iss374_sbx/board_S*.kicad_pcb` 副本做并另存 | ★板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` · ★开工前 / 交卷后各打一次, 三项逐字相等★ ★ |
| ★**零落表** ★ | `HW/netlist_v1.csv` / `netlist_v1_pins.csv` / `BOM_v1.csv` 一个字没碰 | md5 未变 (交卷页 B6 贴输出) |
| ★**零改既有闸** ★ | `MECH/check_jdebug_1p27_clearance.py` (★ISS-371 已签收★) / `check_onepass_s10_fp_swap_impact.py` / `check_onepass_s10_led_spec_sync.py` / `check_onepass_struct_crosscheck.py` / `check_onepass_mech_sync.py` / `check_board_frame_coords.py` / `service_port_check.py` / `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改 | ★交卷页 B6 贴 `python3 MECH/check_jdebug_1p27_clearance.py` 的 rc=0 (零漂移自证)★ ★ |
| ★**零改既有页面正文** ★ | 只新写本页 + 新闸 + 交卷页 + 自己的分片; ★**订正既有页面的部分写成 §4 的追加式订正块, 由 main 决定要不要落** ★ | 本页之外 `MECH/` 下无本单写入 |
| ★**零挂链** ★ | 本单新闸**不**挂进 `state/gate_check.py` | ★`grep -c check_juart_1p27_clearance state/gate_check.py` ⇒ `0` (交卷页 B6 贴输出)★ ★ |
| ★**只写自己的分片** ★ | 只走 `python3 state/frag_write.py --agent mech-lead` | 写前写后各记一次 md5 |
| ★**沙盒只落两处** ★ | `tmp/iss374_sbx/` + `logs/iss374/` | 本单只在这两处落文件 |
| ★**不代老板拍板 / 不代 main 拍** ★ | §3.2 四条方案只给代价; §4 五条未决只登记 | 本页无「应」「建议改」「已决定」式裁决语 |
| ★**零外发** ★ | ★**不把活推给原厂或外部; 缺口一律自己查 + 标证据等级 + 查不到写降级方案** ★ | 官方库读的是本机盘上 `.kicad_mod` 本体, 不是邮件 |
| ★**不自签 `state/issue_log.yaml`** ★ | 台账由 main 签收 | 本单未碰 `issue_log.yaml` |
| ★**零推 GitHub** ★ | 由独立同步 job 负责 | 本单未推 |
| ★**不套 `J_DEBUG` 的推导链** ★ | `J_UART` 走座体支配口径, `J_DEBUG` 走铜箔支配口径, 两条链在 §0 并排摆明 | ★闸 `J5` 专防这条★ ★ |

★**★差在哪 (★本单实算 vs cont1 brief 给的数·以本机复算为准★)** ★
| 项 | cont1 brief | ★本机复算★ | 差 | 为什么差 |
|---|---|---|---|---|
| `J_UART` 现状铜箔 X 宽 | `0.7750` | ★**`0.7750`** ★ | 0 | 一致 |
| 官方 1×2 THT 铜箔 X 宽 | `2.2700` | ★**`2.2700`** ★ | 0 | 一致 (S1 实测 + `.kicad_mod` 推导两路相等) |
| 座体必须清空区 X 宽 | `2.5400` | ★**`2.5400`** ★ | 0 | 一致 |
| THT 档每边余量 | `0.1350` | ★**`0.1350`** ★ | 0 | 一致 (前提 = 铜箔居中于座体清空区中心 `18.8900`) |
| `J_DEBUG` THT 档每边余量 | `2.6950` | ★**`2.6950`** ★ | 0 | 一致 (S3 实测; 与 ISS-371 §1.2 逐字相等) |
| ★**官方 SMD 变体 pad 坐标** ★ | ★`pad (at 0 -2.38)` 与 `(at 0 2.38)`★ | ★**`pad1 (at -1.5 -0.635)` · `pad2 (at 1.5 0.635)` (size `3 × 0.65`)★** | ★**有差** ★ | ★**cont1 读到的 `(0 -2.38)` / `(0 2.38)` 是 `property "Reference"` / `property "Value"` 的文字位置, 不是焊盘位置** ★ |
| ★**官方 SMD 变体铜箔 X 宽** ★ | ★**未给**★ | ★**`1.9200`** ★ | ★**新增** ★ | ★**S2 沙盒实测** ★ |
| ★**官方 SMD 变体铜箔 Y 宽** ★ | ★**未给**★ | ★**`6.0000`** ★ | ★**新增 (★这是 SMD 变体真正的杀手: 撞开口 Y★)** ★ | ★**S2 沙盒实测** ★ |
| ★**落点不动会干涉** ★ | ★未给★ | ★**铜箔 X `20.2400..22.5100` ⇒ 整块在清空区外** ★ | ★**新增** ★ | ★**S1 实测 (rot 90° 的旋转方向 = 局部 +Y → 板 +X)★ ★ |
| ★**座体本体外框** ★ | ★未给★ | ★**S1 `2.6400 × 2.2000` · S2 `2.6400 × 5.1000` · S3 `J_DEBUG` `5.1800 × 2.2000`** ★ | ★**新增 (★本单 01:1x 那趟把「含 `Reference` 文字的全框」当成了座体 ⇒ 已订正, 见 §7★)** ★ | ★**S1/S2/S3 沙盒实测 (`fab_body_bbox_mm`·不含 `PCB_TEXT`)★** ★ |

---

## §7 本单复核记录 (★2026-11-24 04:0x 重派·独立复核 + 一处订正★)

★**背景**: ★**本单 (ISS-374) 在 2026-11-24 01:1x 那趟已把三件交付物 + 沙盒四轮全部落盘; 2026-11-24 04:09 因 gateway reload 重派 ⇒ 本趟不重开, 改为【逐条独立复核 + 补正】** ★

| 复核项 | 本趟怎么做的 | 结果 |
|---|---|---|
| ★**板面现状读数** ★ | ★**用 `pcbnew` API 重读 (★不读上一趟的 json·不走上一趟的解析代码★)** ★ | ★**`J_UART`: npads `2` · `libid` 空 · pitch `0.5000` · pad `0.2750 × 0.9000` · 净名 `UART_TX` / `UART_RX` · 铜箔 X `18.5025..19.2775` (宽 `0.7750`) ⇒ 与 §0 表逐字相符** ★ `[实测]` |
| ★**官方 1×2 THT land** ★ | ★**直接 `sed`/`grep` 盘上 `.kicad_mod` 原文** ★ | ★**pad1 `thru_hole rect (at 0 0) (size 1 1) (drill 0.65)` · pad2 `thru_hole circle (at 0 1.27) (size 1 1) (drill 0.65)` · `fp_rect (start -1.55 -1.14) (end 1.55 2.41)` ⇒ 与 §1.2 逐字相符** ★ `[实测]` |
| ★**`CRIT` 真身** ★ | ★**读 `MECH/service_port_check.py` L126-L127** ★ | ★**`TOL = {"fdm_part": 0.30}` · `CRIT = 2 * TOL["fdm_part"]` = `0.60` ⇒ 与 §0 末行相符** ★ `[实测]` |
| ★**座体必须清空区** ★ | ★**读 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` §3.5** ★ | ★**`X 17.620..20.160` (宽 `2.5400`) · 开口 `X 13.790..23.990` ⇒ 与 §0 表相符** ★ `[实测]` |
| ★**三档量差重算** ★ | ★**本趟重跑沙盒 S0/S1/S2/S3 (★板副本·真换官方封装·新进程重载实测★)** ★ | ★**现状 `0.7750` / THT `2.2700` / SMD `1.9200 × 6.0000` · THT 每边余量 `0.1350` < `CRIT` `0.60` (差 `0.4650`) ⇒ 与 §2 表逐格相符** ★ `[实测]` |
| ★**S3 反向对照轮** ★ | ★**同一轮里 `J_DEBUG` 也换官方 1×4 THT** ★ | ★**`J_DEBUG` 铜箔 X 宽 `4.8100` · 开口单边余量 `2.6950` (最坏 `2.3950`) ⇒ 过 `CRIT`; `J_UART` 每边 `0.1350` ⇒ 不过 ⇒ ★**两件方向确实相反 (一绿一红)·与 ISS-371 §1.1 的 `J_DEBUG` 数逐字相符** ★ `[实测]` |
| ★**与 cont1 brief 给的数对账** ★ | ★**逐条对** ★ | ★**`0.7750` / `2.2700` / `2.5400` / `0.1350` / `0.8825` / Δ `−0.7475` / `J_DEBUG` `2.6950` ⇒ ★**七条全对, 零差** ★ ⇒ ★**brief 给的方向 (不过阈) 与本机实算一致 ⇒ 不触发「停下报告」条款** ★ |

★**★本趟找到并订正的一处缺陷 (★不是数错, 是口径混用★)★**
★**① 缺陷**: ★**§2 那一列「fab 外框 (X × Y)」在 S1/S2 两档报的是 `5.4404` ⇒ 那是 `F.Fab` 层上【`Reference` 参考文字】撑出来的全框, 不是座体本体 ⇒ 会被结构侧读成「座体宽 5.44」⇒ ★**错得离谱 (官方 THT 座体本体实测只有 `2.64`)** ★
★**② 根因**: ★**官方封装加载后 `F.Fab` 层上会多出参考文字, 而沙盒脚本原先只输出一个混口径的 `fab_bbox_mm`** ★
★**③ 订正**: ★**① `tmp/iss374_sbx/sbx_measure.py` 加了 `fab_body_bbox_mm` / `fab_text_bbox_mm` 两个字段 (★只加字段, 不改原有字段·★它是沙盒脚本, 不是签收件★) ; ② 本页 §2 表改成两列并写死口径 (座体本体 = `F.Fab` 层 `PCB_SHAPE` 并集·不含 `PCB_TEXT`) ; ③ 机器块 `tiers[].fab_x/fab_y` ⇒ 改成 `fab_body_x/fab_body_y` + `fab_layer_x/fab_layer_y` (★文字全框只留档·不进结构判断★)** ★
★**④ 影响面**: ★**★§0/§2/§3 的【结论数】一个字没动 (铜箔宽 / 每边余量 / 过不过阈) ⇒ 方向结论不受影响★** ★ (★唯一变的是「座体外框」这一项的【读法】★)
★**⑤ 闸**: ★**`MECH/check_juart_1p27_clearance.py` 的 J0~J8 判据不读 `fab_body_*` / `fab_layer_*` 字段 ⇒ 订正后闸仍 9/9 绿 (已复跑, 见 B6)** ★

★**★本趟零写板 / 零改签收件自证★**: ★**板 md5 开工前 `611b869e13518c3c023fb178f91a0075` · 沙盒前后 `611b869e13518c3c023fb178f91a0075` · 交卷后同 ⇒ 三项逐字相等** ★ `[实测]` ★
★**★ISS-371 那两件 (`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` + `MECH/check_jdebug_1p27_clearance.py`) 本趟【一个字都没动】** ★ ⇒ ★**本趟只动本页 + 本单新闸 + 本单交卷页 + 沙盒脚本 + 自己的分片** ★

---

```MECH-JUART-CLEARANCE-JSON
{
  "schema": "mech.juart.1p27.clearance.v1",
  "crit_mm": 0.60,
  "tol_fdm_part_mm": 0.30,
  "must_clear_regime": {
    "J_UART": "body_driven",
    "J_DEBUG": "copper_driven"
  },
  "must_clear": {
    "J_UART": {"x": [17.620, 20.160], "width": 2.540, "center": 18.890,
               "y": [67.330, 69.870], "opening_x": [13.790, 23.990], "opening_y": [66.300, 70.900]},
    "J_DEBUG": {"x": [142.063, 143.838], "width": 1.775,
                "y": [55.330, 57.870], "opening_x": [137.850, 148.050], "opening_y": [54.300, 58.900]}
  },
  "official_land": {
    "tht_1x02": {
      "name": "PinHeader_1x02_P1.27mm_Vertical",
      "md5": "47bcbf6d0f267d543e50d4b2a8dfabf5",
      "pitch": 1.27,
      "pad1": {"shape": "rect", "at": [0.0, 0.0], "size": [1.0, 1.0], "drill": 0.65},
      "pad2": {"shape": "circle", "at": [0.0, 1.27], "size": [1.0, 1.0], "drill": 0.65},
      "crtyd": [[-1.55, -1.14], [1.55, 2.41]],
      "fab": [[-1.05, -0.635], [1.05, 1.905]],
      "annular_ring": 0.175
    },
    "smd_pin1left": {
      "name": "PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left",
      "md5": "7f15e4a1a32059c2b8eea027edfdbd84",
      "pad1": {"shape": "rect", "at": [-1.5, -0.635], "size": [3.0, 0.65]},
      "pad2": {"shape": "rect", "at": [1.5, 0.635], "size": [3.0, 0.65]},
      "crtyd": [[-3.5, -1.77], [3.5, 1.77]]
    },
    "smd_pin1right": {
      "name": "PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Right",
      "md5": "25ab0efebb8f5df0066508b9686820d7",
      "pad1": {"shape": "rect", "at": [1.5, -0.635], "size": [3.0, 0.65]},
      "pad2": {"shape": "rect", "at": [-1.5, 0.635], "size": [3.0, 0.65]},
      "crtyd": [[-3.5, -1.77], [3.5, 1.77]]
    },
    "tht_1x04": {
      "name": "PinHeader_1x04_P1.27mm_Vertical",
      "md5": "7a5f470c1f70d4b832be258501945385",
      "pitch": 1.27,
      "pad1": {"shape": "rect", "at": [0.0, 0.0], "size": [1.0, 1.0], "drill": 0.65},
      "pad2": {"shape": "circle", "at": [0.0, 1.27], "size": [1.0, 1.0], "drill": 0.65},
      "pad3": {"shape": "circle", "at": [0.0, 2.54], "size": [1.0, 1.0], "drill": 0.65},
      "pad4": {"shape": "circle", "at": [0.0, 3.81], "size": [1.0, 1.0], "drill": 0.65},
      "crtyd": [[-1.55, -1.14], [1.55, 3.15]]
    }
  },
  "tiers": [
    {"tier": "status_quo", "round": "S0", "variant": "board_as_is",
     "copper_x_width": 0.775, "copper_y_width": 0.900,
     "copper_x": [18.5025, 19.2775], "copper_x_centered": [18.5025, 19.2775],
     "margin_nominal": 0.8825, "margin_worst": 0.5825,
     "pass_nominal": true, "pass_worst": false,
     "fab_body_x": 6.1000, "fab_body_y": 4.1000,
     "fab_layer_x": 6.1000, "fab_layer_y": 4.1000,
     "fab_note": "座体本体外框 = F.Fab 层 PCB_SHAPE 并集 (含笔画, 不含 Reference 文字); fab_layer_* = F.Fab 层全框 (含文字, 只留档不是座体)",
     "verdict": "nominal_pass_worst_shortfall_0.0175"},
    {"tier": "official_tht", "round": "S1", "variant": "PinHeader_1x02_P1.27mm_Vertical",
     "copper_x_width": 2.2700, "copper_y_width": 1.0000,
     "copper_x_centered": [17.7550, 20.0250],
     "margin_nominal": 0.1350, "margin_worst": -0.1650,
     "pass_nominal": false, "pass_worst": false,
     "fab_body_x": 2.6400, "fab_body_y": 2.2000,
     "fab_layer_x": 5.440477, "fab_layer_y": 2.2000,
     "fab_note": "座体本体外框 = F.Fab 层 PCB_SHAPE 并集 (含笔画, 不含 Reference 文字); fab_layer_* = F.Fab 层全框 (含文字, 只留档不是座体)",
     "origin_moved_to": [18.2550, 68.6000],
     "verdict": "FAIL_copper_enters_body_must_clear_region"},
    {"tier": "official_smd_pin1left", "round": "S2", "variant": "PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left",
     "copper_x_width": 1.9200, "copper_y_width": 6.0000,
     "copper_x_centered": [17.9300, 19.8500],
     "margin_nominal": 0.3100, "margin_worst": 0.0100,
     "pass_nominal": false, "pass_worst": false,
     "fab_body_x": 2.6400, "fab_body_y": 5.1000,
     "fab_layer_x": 5.440477, "fab_layer_y": 5.1000,
     "fab_note": "座体本体外框 = F.Fab 层 PCB_SHAPE 并集 (含笔画, 不含 Reference 文字); fab_layer_* = F.Fab 层全框 (含文字, 只留档不是座体)",
     "origin_moved_to": [18.8900, 68.6000],
     "opening_y_overflow_per_side": 0.7000,
     "verdict": "FAIL_x_margin_short_and_y_hits_opening"},
    {"tier": "official_smd_pin1right", "round": "S2", "variant": "PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Right",
     "copper_x_width": 1.9200, "copper_y_width": 6.0000,
     "copper_x_centered": [17.9300, 19.8500],
     "margin_nominal": 0.3100, "margin_worst": 0.0100,
     "pass_nominal": false, "pass_worst": false,
     "fab_body_x": 2.6400, "fab_body_y": 5.1000,
     "fab_layer_x": 5.440477, "fab_layer_y": 5.1000,
     "fab_note": "座体本体外框 = F.Fab 层 PCB_SHAPE 并集 (含笔画, 不含 Reference 文字); fab_layer_* = F.Fab 层全框 (含文字, 只留档不是座体)",
     "origin_moved_to": [18.8900, 68.6000],
     "opening_y_overflow_per_side": 0.7000,
     "verdict": "FAIL_x_margin_short_and_y_hits_opening"}
  ],
  "sibling": {
    "ref": "J_DEBUG",
    "tier": "official_tht_1x4",
    "round": "S3",
    "variant": "PinHeader_1x04_P1.27mm_Vertical",
    "copper_x_width": 4.8100, "copper_y_width": 1.0000,
    "copper_x_centered": [140.5450, 145.3550],
    "opening_margin_left": 2.6950, "opening_margin_right": 2.6950,
    "margin_worst": 2.3950,
    "pass_nominal": true, "pass_worst": true,
    "origin_moved_to": [141.0450, 56.6000],
    "verdict": "PASS_margin_3.99x"
  },
  "direction": {
    "J_UART": "RED_structure_part_does_not_fit",
    "J_DEBUG": "GREEN_margin_3.99x"
  }
}
```
