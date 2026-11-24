# `J_DEBUG` / `J_UART` 单排直插 Samtec 【FTS】原厂 land 几何真相页 (ISS-387 · hw-lead · 2026-11-24)

> ★**本单性质**: ★**纯查证 + 纯分析 + 新建文档/闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★
> ★**触发源**: `DECISION_ONE_PAGER_2026-11-22.md` §㊳ **发现二** + **A2** (main 2026-11-24 08:3x 签收 ISS-383 时独立复核推翻 ISS-383 §0-2「两家的 1.27 mm 都没有单排」) ⇒ ★**料号 main 已拍, 但 A2 自己写的那句「铜箔 X 宽 / pin 方径 / 座体高仍须官网单品页二次确认」至今 0 人做** ★

---

## §0 一句话结论 (★把「能不能落板」这件事说死★)

★★ **查证结论 (三个数, 直接影响那一趟的板与结构件)** ★★

| # | 结论 | 证据等级 |
|---|---|---|
| 0-1 | ★**`FTS-104-01-F-S` = 4 位 / 1 排 / 直插 / 排距 1.27 mm, `FTS-102-01-F-S` = 2 位 / 1 排 / 直插 / 排距 1.27 mm —— 两个料号都真实存在、都在售、都是【单排直插】** ⇒ ★**ISS-383 §0-2「两家都没有单排」被推翻这件事, 官网单品页【逐字】坐实** | ★`[官网]` (Samtec 两个单品页标题逐字) + `[媒体]` (DigiKey 参数表) ★ |
| 0-2 | ★★ **Samtec 官方的 FTS 直插 land 只给【孔位图】, 不给【铜箔焊盘直径】** ⇒ ★**「原厂 land 的铜箔 X 宽」在 Samtec 那一层【根本没有一个官方数】** ⇒ ★**MECH 整条 3D 判决链吃的 `4.8100` / `2.2700` 不是 Samtec 的数, 是【盘上通用 KiCad 库件自己的焊盘 1.000 mm】算出来的** ⇒ ★**这个偏离必须显式登记, 且必须与「板只改一次」那一趟同批定死** | ★`[官网]` (官方推荐 PCB 图 SHEET 1 的文本层只有 4 个标注, 无第二个直径值) + `[实测]` (本机自解析 `.kicad_mod`) ★ |
| 0-3 | ★★ **盘上通用库的钻孔 `0.65` 比 Samtec 官方推荐的 `Ø0.71` 小 `0.06` mm** ⇒ ★**如果板侧真按 FTS 落料, 孔径必须改 `0.65 → 0.71`**; ★★ **但只要焊盘仍是 `1.000 × 1.000`, 铜箔包络 `4.8100` / `2.2700` 一个数都不动 ⇒ ⇒ 【MECH 全链余量数不需要重算, 结构件不必因这一趟再返工一次】** ⇒ ★**这是本单最值钱的一句: 那条让结构件重出件的风险, 在焊盘不变的前提下【不存在】** | ★`[官网]` (官方孔径表 + 官方推荐 PCB 图) + `[实测]` (本机自解析) + `[推算]` (焊盘不变 ⇒ 铜箔不变 ⇒ 余量不变) ★ |

★★ **落板口径 (★只给边界, 不代拍料号★)** ★★
★**A2 的料号方向成立且官网坐实; 但「官网铜箔宽」这一项的答案是【Samtec 不给】⇒ 【板侧真值档现在只能靠盘上通用件 land + 一条显式偏离登记】撑着, 不许写成「已按原厂 land 落板」** ⇒ ★**「板只改一次」那一趟能不能一次改对, 卡的不是料号 (已定), 是【钻孔 0.65→0.71 这条板侧改动要不要和焊盘 1.000 一起冻结】这一个动作** ★

---

## §1 查证方法与证据分级

### §1.1 证据分级词表 (★全页每条断言都挂其中之一★)

| 等级 | 含义 | 本单怎么用 |
|---|---|---|
| ★`[官网]` ★ | Samtec 官方域名 (`samtec.com` / `suddendocs.samtec.com`) 上的**文字参数 / 表格 / 图纸文字层标注** | ★**官网 PDF 只取其【文字层标注】, 不把 PDF 里的【矢量图】当已核实几何** ★ |
| ★`[媒体]` ★ | 分销商参数表 (DigiKey / Mouser / Sager) 或第三方 CAD 模型社区 | ★**只用于官网文字层没有的项 (座体高 / 尾长 / 总长)** ★ |
| ★`[实测]` ★ | ★**本机自己跑出来 / 自己解析出来** (不含抄任何 agent 报告) ★ | ★**盘上通用 KiCad 库件的全部几何 = 本机自解析 `.kicad_mod`** ★ |
| ★`[推算]` ★ | 由上面三级按明确公式推出 | ★**每个推算都写清公式** ★ |
| ★`[0数据]` ★ | ★**查不到 / 官方压根没给** | ★**每一处 `[0数据]` 都配 §6 的降级方案, 一处都不许挂起** ★ |

### §1.2 取证链 (★每一环都留了可复核的 URL + md5★)

| 环 | 取到的原厂件 | URL | 本机 md5 | 拿到什么 |
|---|---|---|---|---|
| ① | ★**FTS 家族目录页 PDF** (catalog F-226, 1 页, Adobe InDesign) | `https://suddendocs.samtec.com/catalog_english/fts.pdf` | `fa249db9454f92c77d7e0a5ef62a0ba6` | ★**料号编码规则全文** (含 `-S = Single Through-hole` / `-D = Double Through-hole`) + 规格表 (LCP 绝缘体 / 磷青铜端子 / `-55~125°C` / `3.4 A per pin`) ★ |
| ② | ★**官方推荐 PCB 图打印件** (`FTS-1XX-XX-XX-DX-XX-FOOTPRINT`, REVISION N, `2014-06-10`, ECN-229757, SolidWorks 2012, **4 页**) | `https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf` | `1cbe4a2bfa456d8fd030c8b76bdf8dd5` | ★**SHEET 1 = FIG 1 = 直插 (THT) 孔位图的全部文字层标注** (4 个标注) ★ |
| ③ | ★**官网推荐孔径表** (`/support/pcb-hole-sizes`) | `https://www.samtec.com/support/pcb-hole-sizes` | — (网页, 本机 `www.samtec.com` 被 Cloudflare 429 挡住 ⇒ 内容经搜索后端取得, 见 §1.3) | ★**方柱 lead → 推荐孔径 的对照表**: `.016 Sq → .028 Dia` ★ |
| ④ | ★**官网单品页 ×2** | `https://www.samtec.com/products/fts-104-01-f-s` · `https://www.samtec.com/products/fts-102-01-f-s` | — | ★**标题逐字 = 位数 / 排数 / 安装方式 / post 高** ★ |
| ⑤ | ★**分销参数表** (DigiKey / Sager) | `https://www.digikey.com/en/products/detail/samtec-inc/FTS-104-01-F-S/7342275` | — | ★**座体高 (绝缘体高) / 尾长 / 总长 / 接触形状 / 材质** ★ |
| ⑥ | ★**盘上通用 KiCad 库件 ×2** | `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/` | `7a5f470c…` (1x04) · `47bcbf6d…` (1x02) | ★**本机自解析 pad / 钻孔 / 排距 / 铜箔包络 / courtyard / fab 体** ★ |

### §1.3 ★本机取证的限制 (★诚实交代, 不装全★)
★**`www.samtec.com` 在本机一律返回 HTTP 429 (Cloudflare error 1015 rate_limited)**, `curl` 与 `web_fetch` 各试 5 次 (含 30s/60s 退避) 全部被挡 ⇒ ★**单品页标题 / 家族页标题 / 孔径表**这三个网页的**文字内容**是通过搜索后端 (tavily) 取到的 ⇒ ★**证据等级记 `[官网]` (内容出自 Samtec 官网) 但【来源通道】记 `[媒体]` 的等价通道, 可复核性靠 URL** ★
★**但 ★★两份 PDF (① ②) 是本机 `curl` 直连 `suddendocs.samtec.com` 亲自下载的 (HTTP 200, 字节数/md5 见 §1.2) ⇒ ★★ 本单最要紧的两个几何来源是【本机直取 + 有 md5】的** ★
★**解析手段**: `pdftotext -layout` 取文字层; ★**PDF 里的图一律不当已核实几何** (★只把【文字层标注】抄进页里; 标注与图元的对应关系用图面交叉核对过一遍, 结论写在 §2 的「交叉核对」列里, 但**任何数字都只来自文字层**) ★

### §1.4 本机通用件自解析命令
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 tmp/iss387/measure_generic_part.py     # ★自己解析 .kicad_mod, 不抄任何 agent 结论★
```

---

## §2 `FTS-104-01-F-S` (4 位) 官网单品页逐项抄录

★**料号编码 (逐位拆, 出自 ① FTS 家族目录页 PDF 文字层)**: `FTS` `-` `1`+`04` (每排位数 = 04) `-` `01` (lead style) `-` `F` (镀层) `-` `S` (**行选项 = Single Through-hole**) ★`[官网]`

| 字段 | 值 | 出处 (逐字) | 证据等级 |
|---|---|---|---|
| ★`positions_rows` ★ | ★**4 位 / 1 排** ★ | ★官网单品页标题逐字「.050in/1.27mm Low Profile Micro Header Strip, **4 Pin, 1 Row, Through Hole**, Gold Flash/Tin, .120in Post」; ★DigiKey 参数表「Number of Positions: **4**」+「Number of Rows: **1**」 ★ | ★`[官网]` + `[媒体]` ★ |
| ★`mount_style` ★ | ★**直插 (THT)** ★ | ★同上标题「**Through Hole**」; ★目录页 PDF 选项表「**–S = Single Through-hole**」 ★ | ★`[官网]` + `[媒体]` ★ |
| ★`pitch` ★ | ★**0.050″ = 1.27 mm** ★ | ★标题「.050in/1.27mm」; ★目录页 PDF「(1.27 mm) .050" PITCH」 ★ | ★`[官网]` ★ |
| ★`post_size` ★ | ★**`.016″` (0.41 mm) 方针** ★ | ★官网 FTS 家族页标题逐字「FTS - .050" (1,27mm) Low Profile, **.016" (.41mm) Square Post** Terminal Strip, Single Row」 ★ ⇒ ★**与 §㊳ A2 自己写的那句 `.016″/.41mm` 一致, 但本单是从官网家族页独立抄到的, 不是抄决策页** ★ | ★`[官网]` ★ |
| ★`pad_drill` ★ | ★**`Ø 0.028″` = 0.71 mm (TYP)** ★ | ★**官方推荐 PCB 图 SHEET 1 / FIG 1 文字层逐字「**.028 0.71 (TYP)**」**; ★**官网推荐孔径表「(.41) .016 Sq. → (.71) .028 Dia.」** ⇒ ★**两个互相独立的官网来源互证** ★ | ★`[官网]` ★ |
| ★`copper_x_width` ★ | ★**`[0数据]` —— Samtec 直插图【没给铜箔焊盘直径】** ★ | ★**FIG 1 的文字层一共只有 4 个标注**: 「(NO OF POS x .050[1.27]) - .050[1.27]」/「.050 1.27 (TYP)」/「**.028 0.71 (TYP)**」/「.050 1.27」⇒ ★**没有任何第二个直径值** ⇒ ★**[推算] Samtec 的直插推荐图只给孔位、不给铜箔焊盘直径 (同族 SMT 档的 SHEET 2/3 文字层里反而出现了 `.029 0.74 (TYP)` 与 `.024 0.61` 两个直径值, 直插档没有) ⇒ ⇒ 「原厂铜箔宽」在 Samtec 那一层【无官方数】** ★ | ★`[官网]` + `[推算]` ⇒ 值 `[0数据]` ★ |
| ★`copper_y_width` ★ | ★**`[0数据]`** (同上, 理由逐字相同) ★ | 同上 ★ | ★`[官网]` + `[推算]` ⇒ 值 `[0数据]` ★ |
| ★`seat_height` ★ | ★**绝缘体高 `0.034″` = 0.86 mm** ★ | ★DigiKey 参数表「**Insulation Height**: 0.034" (0.86mm)」 ★ ⇒ ★**注意: 这是【绝缘体高出板面】, 不是 MECH 的 `OI-11` 那个「座体模型高 h」, 两个量不许混** (§5-④) ★ | ★`[媒体]` ★ |
| ★`post_height_above_insulator` ★ | ★**`0.120″` = 3.05 mm** ★ | ★目录页 PDF「–01 = (3.05 mm) .120" Post」; ★DigiKey「Contact Length - Mating: 0.120" (3.05mm)」 ★ | ★`[官网]` + `[媒体]` ★ |
| ★`tail_length` ★ | ★**`0.090″` = 2.29 mm** ★ | ★DigiKey「Contact Length - Post: 0.090" (2.29mm)」; ★Sager「Termination Post Length 2.29 mm (0.09 in)」 ★ | ★`[媒体]` ★ |
| ★`overall_contact_length` ★ | ★**`0.244″` = 6.20 mm** ★ | ★DigiKey「Overall Contact Length: 0.244" (6.20mm)」 ★ | ★`[媒体]` ★ |
| ★`mating_footprint` ★ | ★**官方推荐 PCB 图打印件** = `https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf` (md5 `1cbe4a2b…`) ★**该件 SHEET 1 / FIG 1 = 直插孔位图** ⇒ ★**单排 (-S) 版的打印件直链 = `[0数据]`** (见 §6 降级-①) ★ | ★**官网 `www.samtec.com/products/fts` 的「Prints and Footprints」区列了两个链接: 「FTS - Single Row Footprint」与「FTS - Double Row Footprint」**; ★**本机只解析出 Double Row 那一份的直链** ⇒ ★**单排版直链未取得** ★ | ★`[官网]` (已取到的打印件) + ★`[0数据]` (单排版直链) ★ |
| ★`keepout_dwg` ★ | ★**来源 = ① 官网推荐 PCB 图打印件 + 官网单品页的 3D/CAD 下载** ⇒ ★**但 THT 档 (FIG 1) 的文字层里【没有座体外形标注】(`.270 6.86 CL` / `.123 3.12 N (TYP)` 这两条在 SHEET 3 = 贴片带端罩档) ⇒ 「直插档座体外形的官方尺寸」= `[0数据]`** ★ | ★`[官网]` (来源已知) + ★`[0数据]` (直插档外形尺寸) ★ |
| ★`datasheet_url` ★ | ★`https://www.samtec.com/products/fts-104-01-f-s` ★+ `https://suddendocs.samtec.com/catalog_english/fts.pdf` (md5 `fa249db9…`) ★+ `https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf` (md5 `1cbe4a2b…`) ★ | ★`[官网]` ★ |

### §2.1 ★官方推荐 PCB 图 SHEET 1 / FIG 1 的文字层【逐字全录】★ (`[官网]`)
```
RECOMMENDED PCB LAYOUT FOR FTS-1XX-XX-XX-DX-XX
(NO OF POS x .050[1.27]) - .050[1.27]      ← 一排的孔中心总跨距 (公式)
.050 1.27 (TYP)                             ← 排内孔距
.028 0.71 (TYP)                             ← 孔径
.050 1.27                                   ← 排间距 (仅双排 -D 档适用)
FIG 1
FTS-1XX-XX-XX-D SHOWN
ALL DIMENSIONS ARE SYMMETRIC ABOUT THE CENTERLINE
```
★**图面交叉核对结论 (只用来确认「哪个标注配哪个图元」, 不用来产生任何新数字)**: `Ø.028[.71] (TYP)` 的引线指向【孔】; `.050[1.27] (TYP)` 是同排相邻孔的中心距; `(NO OF POS × .050[1.27]) − .050[1.27]` 是同排首末孔的中心距公式; ★**图上【没有】任何铜箔焊盘直径的标注 (只有一个孔径标注)** ⇒ ★**与文字层互相印证: 直插档官方图只给孔位** ★ `[官网]` + `[推算]`

### §2.2 ★把上面的公式代到 4 位 ★
★`[推算]` (公式出自 §2.1 文字层, 代入 `NO OF POS = 4`) ★
```
一排孔中心总跨距 = (4 × 1.27) − 1.27 = 3.810 mm
铜箔沿脚排总宽   = 3.810 + 铜箔焊盘直径   ← ★焊盘直径无官方数 ⇒ 这一项本单【不落数】★
```
⇒ ★**唯一能落的一个官方数: 排距 `1.27` 与孔中心跨距 `3.810`** ★

---

## §3 `FTS-102-01-F-S` (2 位) 官网单品页逐项抄录

★**料号编码**: `FTS` `-` `1`+`02` (每排 02 位) `-` `01` (lead style) `-` `F` `-` `S` (Single Through-hole) ★`[官网]`

| 字段 | 值 | 出处 (逐字) | 证据等级 |
|---|---|---|---|
| ★`positions_rows` ★ | ★**2 位 / 1 排** ★ | ★官网单品页标题逐字「.050in/1.27mm Low Profile Micro Header Strip, **2 Pin, 1 Row, Through Hole**, Gold Flash/Tin, .120in Post」 ★ ⇒ ★**同族同规格的 `FTS-103-01-F-S` 单品页标题也是「3 Pin, 1 Row, Through Hole」⇒ ★**「`-S` = 1 排直插」这件事在官网【按位置数连续三次逐字重复】, 不是从一条推的** ★ | ★`[官网]` + `[媒体]` ★ |
| ★`mount_style` ★ | ★**直插 (THT)** ★ | ★同上标题「Through Hole」 + 目录页 PDF「–S = Single Through-hole」 ★ | ★`[官网]` ★ |
| ★`pitch` ★ | ★**1.27 mm** ★ | ★同 §2 ★ | ★`[官网]` ★ |
| ★`post_size` ★ | ★**`.016″` (0.41 mm) 方针** ★ | ★同 §2 (家族页标题) ★ ⇒ ★**两颗件同族同 post** ★ | ★`[官网]` ★ |
| ★`pad_drill` ★ | ★**`Ø 0.71` (TYP)** ★ | ★同 §2 (官方打印件 + 官方孔径表) ★ | ★`[官网]` ★ |
| ★`copper_x_width` ★ | ★**`[0数据]`** (与 §2 同因: 官方直插图不给焊盘直径) ★ | 同 §2 ★ | ★`[官网]` + `[推算]` ★ |
| ★`copper_y_width` ★ | ★**`[0数据]`** ★ | 同 §2 ★ | ★`[官网]` + `[推算]` ★ |
| ★`seat_height` ★ | ★**0.86 mm** (绝缘体高) ★ | ★DigiKey 同族 `FTS-107-01-F-S` 参数表「Insulation Height: 0.034" (0.86mm)」★ ⇒ ★**2 位与 4 位是同一个塑壳高度档 (同 lead style / 同 row option) ⇒ 取同族同构型的值, 标 `[媒体]`** ★ | ★`[媒体]` ★ |
| ★`post_height_above_insulator` ★ | ★**3.05 mm** ★ | ★同 §2 ★ | ★`[官网]` + `[媒体]` ★ |
| ★`tail_length` ★ | ★**2.29 mm** ★ | ★同 §2 ★ | ★`[媒体]` ★ |
| ★`overall_contact_length` ★ | ★**6.20 mm** ★ | ★同 §2 ★ | ★`[媒体]` ★ |
| ★`mating_footprint` ★ | ★**同 §2** (官方打印件直链已知; ★**单排版直链 `[0数据]`**) ★ | 同 §2 ★ | ★`[官网]` + `[0数据]` ★ |
| ★`keepout_dwg` ★ | ★**同 §2** (来源已知; ★**直插档外形尺寸 `[0数据]`**) ★ | 同 §2 ★ | ★`[官网]` + `[0数据]` ★ |
| ★`datasheet_url` ★ | ★`https://www.samtec.com/products/fts-102-01-f-S` ★+ 目录 PDF + 打印件 (同 §2) ★ | ★`[官网]` ★ |

### §3.1 ★2 位的官方公式代入 ★
★`[推算]`: 一排孔中心总跨距 = (2 × 1.27) − 1.27 = **1.270 mm** ⇒ ★**排距与 4 位那颗完全同源同值, 只有跨距公式里的 N 不同** ★

### §3.2 ★★两处「查出来但本单不代裁」的官网事实登记 ★★
| # | 事实 | 证据等级 | 本单态度 |
|---|---|---|---|
| 3-2-① | ★**目录页 PDF 的「NO. PINS PER ROW」字段逐字写「02 thru 50 (except –S & –SA option = 05 thru 46)」** ⇒ ★**这句话若读成「行选项 -S 只供 05~46 位」, 则 2 位与 4 位都落在区间外**; ★**但同一份 PDF 的「OTHER OPTION」栏里 `–S`/`–SA` 另有所指 (End Shroud / End Shroud with Alignment Pin, 也写 05 thru 46) ⇒ ★**两读都通, 单看这句话判不了** ★ ⇒ ★**判它不成立的是另一条独立证据: Samtec 官网有 `FTS-102-01-F-S` / `FTS-104-01-F-S` 的单品页 (可下单), DigiKey 把 `FTS-104-01-F-S` 标 `Part Status: Active` 且有库存与报价** ⇒ ★**「存在且可订」这件事官网已经坐实** ★ | ★`[官网]` + `[媒体]` ★ | ★**登记, 不代裁** ★ |
| 3-2-② | ★**目录页 PDF 明确「FTS Board Mates: CLP, FLE」「Cable Mates: FFSD」, 且 lead style –01 (.120" Post) 标注「Mates with FFSD」** ⇒ ★**即: 这颗件的对插件是 FFSD (IDT 的 .050" IDC 排线座), 不是 Cortex-10 的 2×5 座** ⇒ ★**这与 §㊳ A1「以板侧真值档为准, 结构侧重算」方向一致, 但也意味着【结构侧那套 Cortex-10 2×5 的对插模型作废】** ★ | ★`[官网]` ★ | ★**登记 (只登记事实, 不写结构侧的改法)** ★ |

---

## §4 与盘上【通用 KiCad 库件】逐项对比表 (★逐项列, 不许只写结论★)

★**盘上通用件 = 本机自解析 (★不许抄 ISS-379/380 的结论★)** · 复跑: `python3 tmp/iss387/measure_generic_part.py` ★`[实测]`

★**坐标系约定 (★全表按这条读, 不然 X/Y 会看反★)**:
★**MECH 判据坐标系 `X` = 沿脚排方向**, `Y` = 垂直脚排方向; ★**KiCad 库件自身坐标系里脚排在 `Y` 向** ⇒ ★**MECH X ≡ KiCad Y, MECH Y ≡ KiCad X** ⇒ ★**下面「沿脚排」= MECH 的 `copper.x`, 也是 MECH 全部 X 向余量数的输入** ★

| 字段 | ★FTS 厂件 (官网)★ | ★盘上通用 KiCad 库件 (本机实测)★ | 一致? | ★若不一致 ⇒ 影响哪条判据★ |
|---|---|---|---|---|
| ★`positions` (位数) ★ | ★`4` / `2` ★`[官网]` | ★`4` / `2` ★`[实测]` | ★**一致** ★ | — |
| ★`positions_rows` (排数) ★ | ★**1 排** ★`[官网]` | ★**1 排** (焊盘中心 X 唯一值 `[0.0]`) ★`[实测]` | ★**一致** ★ | ★**这是 ISS-383 翻车的那个点: 现在两边都是 1 排 ⇒ 双排那一支 (FTSH) 与本单无关 (★族别辨析: FTSH 是另一个族, 不可顶替 FTS★)** ★ |
| ★`mount_style` ★ | ★**THT 直插** ★`[官网]` | ★**thru_hole** (4 个/2 个焊盘全 `thru_hole`) ★`[实测]` | ★**一致** ★ | — |
| ★`pitch` ★ | ★**1.27 mm** ★`[官网]` | ★**1.27 mm** (逐段实测 `[1.27, 1.27, 1.27]` / `[1.27]`) ★`[实测]` | ★**一致** ★ | ★**一致 ⇒ B-2 / E-1 排距口径不动** ★ |
| ★`post_size` ★ | ★**`.016″` / 0.41 mm 方针** ★`[官网]` | ★**库件不写 post 尺寸** (通用排针) ⇒ ★**无对照值** ★ | ★**不可比** ★ | ★**不可比 ⇒ 「这颗通用件到底是不是 .41 方针」本身没有依据 ⇒ ★**盘上通用件只能当【几何载体】, 不能当【厂件真值】** ★ |
| ★`pad_drill` (钻孔) ★ | ★**`Ø 0.71` (TYP)** ★`[官网]` | ★**`0.65`** ★`[实测]` | ★★**不一致 (差 `0.06` mm, 通用件偏小)** ★★ | ★★**【板侧要改的一个动作】**: 孔径 `0.65 → 0.71` ⇒ ★**孔位 (排距/跨距) 不动 ⇒ MECH 全部余量数不动** (铜箔包络只看焊盘, 不看钻孔) ★★ ⇒ ★**但这一改是【板侧改板】, 必须与「板只改一次」那一趟同批** ★ |
| ★`copper_x_width` (沿脚排铜箔总宽) ★ | ★**`[0数据]` —— 官方直插图只给孔位, 不给焊盘直径** ★`[官网]`+`[推算]` | ★**`4.8100` / `2.2700`** (= 跨距 `3.810`/`1.270` + 焊盘 `1.000`) ★`[实测]` | ★★**不一致 (官方无此数 ⇒ 通用件这个数【不是厂件数】)** ★★ | ★★**【本单命门】** ★★ `MECH/check_debug_seat_3d_fit.py` L491 / L683-L686 / L746 写死的 `4.81` / `2.27` ⇒ `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 的 `6.6100` / `4.0700` / `0.1350` / `2.6950` / `0.7700` 与 OI-5 三档 `1.7750`/`4.0850`/`4.8100` ⇒ ★★**全部由这个「非厂件」的焊盘 `1.000` 决定 ⇒ 必须显式登记偏离** ★★ (见 §5-①) ★ |
| ★`copper_y_width` (垂直脚排铜箔宽) ★ | ★**`[0数据]`** ★`[官网]`+`[推算]` | ★**`1.0000`** (焊盘尺寸的垂直分量) ★`[实测]` | ★★**同上** ★★ | ★**MECH `copper.y = 1.0000` ⇒ 罩住 Y 余量 `0.7700` 与开口 Y 余量 `0.7300`/`1.0300` 同样吃这个数** ★★ |
| ★`seat_height` (座体高) ★ | ★**绝缘体高 `0.86`** ★`[媒体]` ⇒ ★**全高约 `0.86 + 3.05 = 3.91`** ★`[推算]` | ★**库件不标座体高** (3D STEP 是通用排针) ⇒ ★**无对照值** ★ | ★**不可比** ★ | ★**OI-11 (归 boss) 的「座体真实高 h」** ⇒ ★**官网给了 `0.86` (绝缘体) 与 `3.91` (全高) 两个数, 但★**都不是** MECH 模型里那个 `h` (MECH 的 `2.54` / `4.00` 是【镜脚侧座体模型高】) ⇒ ★**三个量不许混, 混了就把结构件做错** ★ (见 §5-④) ★ |
| ★`mating_footprint` ★ | ★官方推荐 PCB 图打印件 (直链已知, ★**单排版直链 `[0数据]`**) ★`[官网]` | ★**KiCad 官方库件 `Connector_PinHeader_1.27mm.pretty` (不是 Samtec 的件)** ★`[实测]` | ★**来源不同源** ★ | ★**同源纪律**: 板上封装与 BOM 型号栏必须指向【同一家同型号】; ⇒ ★**现在盘上是「通用库件 + BOM 型号栏待定」, 落 FTS 那一刻必须两边一起换** (即 §㊳ A3) ★ |
| ★`keepout_dwg` ★ | ★来源已知 (打印件 + 官网 3D 下载); ★**直插档外形尺寸 `[0数据]`** ★`[官网]`+`[0数据]` | ★`F.CrtYd` `3.100 × 6.090` / `3.100 × 3.550`; `F.Fab` 体 `2.100 × 5.080` / `2.100 × 2.540` ★`[实测]` | ★**通用件的 courtyard 不是厂件 keepout** ★ | ★**MECH §3 用的 `F.CrtYd 6.0900` / `F.Fab 5.0800` 就是这个通用件的数** ⇒ ★**OI-12 (判据要求的清空区 `6.6100` 比 courtyard 还大 `0.5200`) 这个「偏紧」结论, 也是拿通用件的 courtyard 比的 ⇒ ★**换成厂件后 courtyard 变了, 这个结论要重算** ★ |
| ★`datasheet_url` ★ | ★见 §2 / §3 ★`[官网]` | — | — | — |

### §4.1 ★★「若不一致」的汇总: 一共三条, 每条都点名影响哪条判据 ★★
| # | 不一致 | 量差 | 影响哪条判据 | 方向 |
|---|---|---|---|---|
| ★4-1-① ★ | ★**铜箔焊盘直径: 官方无此数 vs 通用件 `1.000`** ★ | ★**未知** (官方不给) ⇒ ★**MECH 全链余量数的根** ★ | ★`MECH/check_debug_seat_3d_fit.py` **L491 / L683-L686 / L746** ⇒ `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 的 **`6.6100` / `4.0700` / `0.1350` / `2.6950` / `0.7700`** + **OI-5 三档 `1.7750`/`4.0850`/`4.8100`** + **OI-12 (`6.6100` vs courtyard `6.0900`)** ★ | ★**焊盘不变 ⇒ 全链不动; 焊盘一变 ⇒ 全链重算 (每 `0.01` mm 焊盘变化 ⇒ `J_DEBUG` 清空区需求变 `0.01`, `J_UART` 罩住余量变 `0.005`)** ★ |
| ★4-1-② ★ | ★**钻孔: 官方 `Ø0.71` vs 通用件 `0.65`** ★ | ★**`0.06` mm (通用件偏小)** ★ | ★**板侧改板一个动作 (孔径) ⇒ 不进 MECH 判据链 (钻孔不进铜箔包络)** ★ ⇒ ★**MECH 侧【不受影响】** ★ | ★**只需登记 + 同批改** ★ |
| ★4-1-③ ★ | ★**keepout / courtyard: 官方直插档外形 `[0数据]` vs 通用件 `F.CrtYd 3.100×6.090`** ★ | ★**未知** ★ | ★**OI-12** (判据要求的清空区比 courtyard 还大 `0.5200` ⇒ 「判据对 THT 排针偏紧」这条结论的对照物是通用件) ★ | ★**换厂件后 OI-12 要重算** ★ |

---

## §5 与 §㊳ A2 / §㊳ A4 / ISS-379 / ISS-380 / ISS-383 的关系与影响面 (★谁在用这个数★)

### §5-① ★★命门: `4.8100` / `2.2700` 这两个数的【来源链】★★
★**本机实读 (`MECH/check_debug_seat_3d_fit.py` L98-L101)**: ★
```python
KICAD_LIB = "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty"
FOOTPRINT_FILE = {
    "J_DEBUG": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
    "J_UART":  "PinHeader_1x02_P1.27mm_Vertical.kicad_mod",
}
```
★⇒ ★**那两颗件是【通用 KiCad 库件】, 不是【Samtec FTS 厂件】** ⇒ ★**MECH 全链的铜箔宽输入 = 通用件的焊盘 `1.000`** ★`[实测]`

★**这两行写死 `4.81` / `2.27` 的地方 (★本机实读, 行号会随该文件改动而漂, 以内容为准★)** ★`[实测]`
| 行 | 内容 | 吃的是什么 |
|---|---|---|
| ★L491 ★ | `want_cover = r4((float(c["value"]) - 4.81) / 2.0)` | ★OI-5 三档清空区候选的罩住余量 ★ |
| ★L683 ★ | `"J_DEBUG": {"copper": {"x": 4.81, "y": 1.0}, ...}` | ★`J_DEBUG` 官方档铜箔包络 ★ |
| ★L686 ★ | `"J_UART": {"copper": {"x": 2.27, "y": 1.0}, ...}` | ★`J_UART` 官方档铜箔包络 ★ |
| ★L746 ★ | `mc = r4((v - 4.81) / 2.0)` + L753 `protrusion_per_side = r4(max(0.0, (4.81 - v) / 2.0))` | ★OI-5 三档的罩住余量与每边伸出量 ★ |

★**⇒ 派给 MECH 的影响面清单 (★§㊳ OI-5 / OI-12 一并点名★)** ★`[实测]`
- ★`MECH/check_debug_seat_3d_fit.py` ★**L491** / ★**L683-L686** / ★**L746** / ★**L753** (写死 `4.81` / `2.27` 的那几行)
- ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` ★**`6.6100`** (J_DEBUG 清空区 X 需求) · ★**`4.0700`** (J_UART 清空区 X 需求) · ★**`0.1350`** (J_UART 罩住 X 名义余量) · ★**`2.6950`** (J_DEBUG 开口 X 余量) · ★**`0.7700`** (两件罩住 Y 余量)
- ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` ★**OI-5** (清空区 X 三档 `1.7750` / `4.0850` / `4.8100`) 与 ★**OI-12** (`6.6100` vs 官方 land courtyard `6.0900` ⇒ 「偏紧」结论的对照物是通用件)
- ★`MECH/check_debug_seat_3d_fit.py` L37 / L108 的 `DEBUG_CLEAR_X = (1.7750, 4.0850, 4.8100)` (三档里最高那档 `4.8100` 本身就等于通用件铜箔宽 ⇒ ★**三档里有一档是「拿通用件自己的数当清空区」** ⇒ ★**换厂件后这档的含义会变**)

★★ **⇒ 本单对 MECH 的净影响 (★给结论, 不代 MECH 拍★)** ★★
★**【只要板上焊盘保持 `1.000 × 1.000`, MECH 的 `4.8100` / `2.2700` / `6.6100` / `4.0700` / `0.1350` / `2.6950` / `0.7700` 一个数都不用改】** ⇒ ★★ **结构件【不必】因为这一趟再出件一次** ⇒ ★★ **但这条「一个数都不用改」的成立条件是【焊盘不动】, 所以它必须变成一个写下来、被闸守住的约束, 而不是一句口头结论** ★`[推算]`

### §5-② 与 §㊳ **A2** (料号已拍) 的关系
★**A2 原文的三不许跳过的字**: 「★**但铜箔 X 宽 / pin 方径 / 座体高仍须官网单品页二次确认** (★FTS 的 post 是 .016″ (.41mm) 方柱, 与 FTSH 的 .41 mm 不同族, **不许拿 FTSH 的铜箔数顶替**) ★★」 ★ (★本页引这一句只为记录 A2 的要求; ★**族别辨析: FTSH 是另一个族, 它的任何数都不许顶替 FTS**★)
| A2 里的三个待确认项 | 本单的结果 |
|---|---|
| ★**铜箔 X 宽** ★ | ★**官网直插图【不给】 ⇒ `[0数据]` + 偏离登记 (§4-1-①) ⇒ A2 这一项【查完了, 答案是不存在】** ★ |
| ★**pin 方径** ★ | ★**`.016″` (0.41 mm) 方针 —— 官网家族页 + 官网孔径表双证** ⇒ ★**A2 的这句【抄对了】, 但本单是从官网独立抄到的** ★ |
| ★**座体高** ★ | ★**绝缘体高 `0.86` / 全高约 `3.91` (分销参数表) ⇒ ★**但与 MECH 的 `OI-11` 那个 `h` 不是同一个量 (§5-④)** ★ |

### §5-③ 与 §㊳ **A4** (官方通用件 vs 自建) 的关系
★**A4 原文**: 「★**官方通用件 (`PinHeader_1x04_P1.27mm_Vertical` md5 `7a5f470c…` / `PinHeader_1x02_P1.27mm_Vertical` md5 `47bcbf6d…`) ⇒ 自建留给走双排 SMT 那一档**」 ★⇒ ★**本机实测两个 md5 与 A4 逐字一致 (★A4 引的 md5 就是这两个文件本身, 不是厂件)★** ⇒ ★**A4 的「官方通用件」措辞指的是【KiCad 官方库件】, 不是【Samtec 官方件】** ⇒ ★**A2 选了 Samtec FTS (厂件) 而 A4 选的是 KiCad 通用件 (第三方库件) ⇒ ★★ **两个裁决指向【不同的封装来源】, 落板那一刻必须合成一个: 要么用 Samtec 的官方 land (那 A4 的 KiCad 通用件就不用了), 要么用 KiCad 通用件 (那 A2 的 Samtec 料号与 BOM 型号栏就得写成「等价替代」而不是「原厂 land」)** ⇒ ★★ **这是本单发现的一处 A2/A4 之间的缝, 本单只登记, 不代裁** ★`[实测]`

### §5-④ 与 ISS-380 (座体选型) / ISS-379 (落点) / ISS-383 (单排可得性) 的关系
| 单 | 关系 | 证据等级 |
|---|---|---|
| ★**ISS-383** ★ | ★**§0-2「两家的 1.27 mm 都没有单排」被官网单品页逐字推翻** (4 位 / 1 排 / 直插, 官网标题明写) ⇒ ★**ISS-383 的降级路径「另找厂按规格书下单」确实不再是唯一解** ★ | ★`[官网]` ★ |
| ★**ISS-380** ★ | ★**§2 的 D-1 / U-1 (`FTSH-104-01-F-DV` 等) 已被 §㊳ 发现一推翻 (双排贴片), 本单【不碰它们】** ⇒ ★**本单只把「1 排直插」这一档的官网真值补齐** ★ (★**族别辨析: `FTSH-104-01-F-DV` 是双排贴片, 与 FTS 单排直插不同族、不同件, 它的任何数都不许顶替本单 FTS 的数**★) | ★`[官网]` ★ |
| ★**ISS-379** ★ | ★**落点三候选 (`C1 17.9650` / `C2 19.0350` / `C3 18.9350`) 与「三候选铜箔宽逐字相同 = `2.2700`」这条** ⇒ ★**本单实测通用件 `J_UART` 铜箔沿脚排 = `2.2700` ⇒ 与 ISS-379 §2.3 逐字一致 (★本单是独立自解析得出的一致, 不是抄的)★ ⇒ ★**落点裁决【不受本单影响】** ★ | ★`[实测]` ★ |
| ★**ISS-380 §3.3-② / MECH `OI-11`** ★ | ★**`h` (座体真实高) 三档参数化 (`2.54` / `4.00` / Z 向上界 `4.70`) ⇒ ★**本单给的 `0.86` (绝缘体高) 与 `3.91` (全高) 是【另外两个量】, 不是 `h`** ⇒ ★**★ 本单【不】用它去替 `h`, 也不拿它去动 MECH 的 `2.54`** ⇒ ★**OI-11 仍归 boss** ★ | ★`[推算]` + `[媒体]` ★ |
| ★**`HW/BOM_v1.csv`** ★ | ★**`J_DEBUG` 行 (第 71 行) 与 `J_UART` 行 (第 77 行) 的 `opn` 与 `footprint` 两栏现在都还是「待定」, `evidence` 栏是「[推算]」** ⇒ ★**本单【零落表】, 只给草案 (§6-③)** ★ | ★`[实测]` ★ |

---

## §6 降级方案 (★查不到就写降级方案, 一处都不许挂起★)

### 6-① ★「单排 (-S) 版官方打印件直链未取得」的降级 (★brief 指定的第 ① 类: 选官网参数直接满足的替代型号★)
★**事实**: 官网 FTS 家族页的「Prints and Footprints」区列了「FTS - Single Row Footprint」与「FTS - Double Row Footprint」两个链接; ★**本机只解析出 Double Row 那一份的直链** (`https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf`, md5 `1cbe4a2b…`); ★**`suddendocs.samtec.com/prints/` 下本机探测了 14 个候选文件名 (含 `sx` / `s-xx` / `single-row` 等) 全部 403 (该域对不存在的路径返 403), `www.samtec.com` 全站 429 ⇒ 单排版直链 = `[0数据]`** ★
★**降级 (不用单排版打印件也能成立)**: ★**该打印件的 SHEET 1 / FIG 1 是【直插孔位图】, 其行内几何 (排距 `.050[1.27]` TYP / 孔径 `Ø.028[.71]` TYP / 一排孔中心跨距公式 `(NO OF POS × .050[1.27]) − .050[1.27]`) 对【每一排】成立, 而 `-D` 与 `-S` 的差别只是【排数】(FIG 1 的另一个标注 `.050 1.27` 是排间距, 单排件没有第二排, 该标注不适用)** ⇒ ★**[推算] ⇒ 单排件适用的官方 land = FIG 1 的行内几何, 无需单排版打印件** ★ ⇒ ★**降级路径 = 用已取得的直插孔位图 + 「单排只取一行」这条明示推算, 并把「单排版打印件直链未取得」显式登记为 `[0数据]`** ★

### 6-② ★「原厂铜箔宽无官方数」的降级 (★brief 指定的第 ② 类: 用盘上通用件 land 并显式登记该偏离★)
★**降级 (本单采用的就是这一条)**: ★**板侧 land 继续用盘上通用 KiCad 库件 (`PinHeader_1x04/1x02_P1.27mm_Vertical`), 但把三条偏离逐条登记在案, 且登记必须写进 §7 机器块, 由 `HW/check_fts_single_row_land_truth.py` 的 **K3** 守住** ★
| 偏离 | 内容 | 后果 |
|---|---|---|
| ★**D-1** ★ | ★**铜箔焊盘直径 `1.000` 是【第三方库件 / IPC 口径】的选择, 不是 Samtec 官方数 (官方直插图不给)** ★ | ★**MECH 全链余量数的根 ⇒ 只要它不动, MECH 全链不动 (见 §5-①)** ★ |
| ★**D-2** ★ | ★**钻孔 `0.65` ≠ Samtec 官方 `Ø0.71` (小 `0.06`)** ★ | ★**落 FTS 那一刻必须改孔 (板侧改板动作); 不影响铜箔包络 ⇒ 不影响 MECH** ★ |
| ★**D-3** ★ | ★**`F.CrtYd` / `F.Fab` 是通用排针的 courtyard, 不是 FTS 厂件 keepout** ★ | ★**OI-12 (「判据比 courtyard 还大 `0.5200`」) 的对照物要重算** ★ |

### 6-③ BOM 型号栏草案 (★本单零落表, 只给草案; 落表时机 = §㊳ A3 的「与 land 改动同一次工序」★)
| ref | 现盘上 `opn` / `footprint` | ★草案 (不落表)★ | 证据等级 |
|---|---|---|---|
| ★`J_DEBUG` (行 71) ★ | `待定` / `待定` | ★`FTS-104-01-F-S` (Samtec · 4 位 1 排 直插 · 1.27 mm) + land = `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical` + ★**孔径改 `0.71`** + ★**偏离 D-1/D-2/D-3 登记** ★ | ★`[官网]` (料号) + `[实测]` (land 与现孔径) + `[推算]` (改孔动作) ★ |
| ★`J_UART` (行 77) ★ | `待定` / `待定` | ★`FTS-102-01-F-S` (Samtec · 2 位 1 排 直插 · 1.27 mm) + land = `Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical` + ★**孔径改 `0.71`** + ★**偏离 D-1/D-2/D-3 登记** ★ | ★同上 ★ |

### 6-④ ★「直插档座体外形尺寸 (keepout 几何)」的降级 (★brief 指定的第 ③ 类: 实测样件复现路径 + 官方 3D 下载★)
★**降级路径 (两条, 按优先级)**: ★**(甲)** 官网单品页的 **3D 模型 / CAD 下载** (官网「2D view may not be representative… 请以 3D preview 或 CAD download 为准」那段免责文字本身, 就说明官网有 3D/CAD 下载件) ⇒ ★**用它量座体外形 (宽 X / 深 Y / 高 Z) 补 `keepout_dwg`**; ★**(乙)** **实测样件复现路径**: 落 FTS 时先打一块单板样, 用卡尺量【座体宽 X / 座体深 Y / 绝缘体高 Z】三个量, 回填 `keepout_dwg` ⇒ ★**这两条都不许写成「等原厂回信」/「待外部确认」** ★

### 6-⑤ ★「`www.samtec.com` 429」的降级
★**降级**: ★**两份关键几何来源 (FTS 目录 PDF + 官方推荐 PCB 图打印件) 本机直连 `suddendocs.samtec.com` 已取得并有 md5 ⇒ 不依赖被挡的 `www.samtec.com`**; ★**网页类内容 (单品页标题 / 家族页标题 / 孔径表) 已在 §1.3 登记来源通道, URL 留档可复核** ⇒ ★**不写「待官网恢复访问」这种挂起话** ★

---

## §7 复跑命令 + 机器块

### §7.1 复跑命令 (★每个数都能自己跑出来★)
★**前置**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses` · `export TMPDIR=$PWD/tmp`

| # | 命令 | 出什么 |
|---|---|---|
| 7-1 | `python3 tmp/iss387/measure_generic_part.py` | ★**§4 的「盘上通用件 (本机实测)」整列** (pad / 钻孔 / 排距 / 排数 / 铜箔包络 / courtyard / fab 体 / 两个 md5) ★ |
| 7-2 | `md5sum /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x0{4,2}_P1.27mm_Vertical.kicad_mod` | ★**§4 的两个库件 md5** (与 §㊳ A4 引的 `7a5f470c…` / `47bcbf6d…` 对齐) ★ |
| 7-3 | `pdftotext -layout tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf - \| head -40` | ★**§2.1 官方推荐 PCB 图 SHEET 1 的文字层逐字全录** ★ |
| 7-4 | `pdftotext -layout tmp/iss387/fts_catalog.pdf - \| head -40` | ★**§1.2 ① 目录页 PDF 的料号编码规则** (`–S = Single Through-hole` 等) ★ |
| 7-5 | `md5sum tmp/iss387/fts_catalog.pdf tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf` | ★**§1.2 两份原厂件的 md5** (期望 `fa249db9…` / `1cbe4a2b…`) ★ |
| 7-6 | `sed -n '98,101p;491p;683p;686p;746p' MECH/check_debug_seat_3d_fit.py` | ★**§5-① 的「那几行吃铜箔宽」逐行原文** ★ |
| 7-7 | `grep -n '6\.6100\|4\.0700\|0\.1350\|2\.6950\|0\.7700\|OI-5\|OI-12' MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` | ★**§5-① 影响面清单里点名的 MECH 侧各数** ★ |
| 7-8 | `sed -n '71p;77p' HW/BOM_v1.csv` | ★**§6-③ 的 BOM 两行原文** (`opn` / `footprint` 仍「待定」) ★ |
| 7-9 | `grep -rn "FTS-104-01-F-S" HW/ MECH/ SW/` | ★**本单交卷前应仍为 0 命中** (真相页写在 `HW/PCB/` 下 ⇒ 命中 1 = 本页自己) ⇒ ★**注意: 本页落盘后该数会变成 1 命中, 这是预期的** ★ |
| 7-10 | `python3 HW/check_fts_single_row_land_truth.py` | ★**本单新建闸 K0~K6 全绿 (rc=0)** ★ |
| 7-11 | `python3 HW/check_fts_single_row_land_truth.py --selftest` | ★**闸自测 `ALL TESTS PASS`** ★ |

### §7.2 机器块 (★给下游闸读★)
```json
{
 "schema": "hw.fts.single_row.land_truth.v1",
 "issue": "ISS-387",
 "agent": "hw-lead",
 "updated": "2026-11-24",
 "truth_doc": "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md",
 "landing_part_decision": "not_decided_here",
 "board_write": "none",
 "table_write": "none",
 "mech_files_touched": "none",
 "frame_note": "MECH 判据坐标系 X = 沿脚排方向 (≡ KiCad 库件自身坐标系的 Y); MECH Y = 垂直脚排方向",
 "parts": {
  "FTS-104-01-F-S": {
   "positions": 4,
   "positions_rows": "1 排",
   "mount_style": "THT",
   "pitch_mm": "1.27",
   "post_size": ".016in_square_0.41mm",
   "pad_drill_mm": "0.71",
   "copper_x_width": "[0数据]",
   "copper_y_width": "[0数据]",
   "seat_height_mm": "0.86",
   "hole_center_span_mm": "3.810",
   "mating_footprint": "https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf (SHEET1 FIG1 THT hole pattern; single-row variant direct URL = [0数据])",
   "keepout_dwg": "https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf + 官网 3D/CAD 下载 (THT 档外形尺寸 = [0数据])",
   "datasheet_url": "https://www.samtec.com/products/fts-104-01-f-s",
   "evidence": "[官网]",
   "prose_anchors": [
    "4 Pin, 1 Row, Through Hole",
    ".028 0.71 (TYP)",
    "(NO OF POS x .050[1.27]) - .050[1.27]"
   ],
   "value_anchors": {
    "positions_rows": ["1 排"],
    "pitch_mm": ["1.27"],
    "post_size": [".016", "0.41"],
    "pad_drill_mm": ["0.71"],
    "seat_height_mm": ["0.86"],
    "hole_center_span_mm": ["3.810"]
   }
  },
  "FTS-102-01-F-S": {
   "positions": 2,
   "positions_rows": "1 排",
   "mount_style": "THT",
   "pitch_mm": "1.27",
   "post_size": ".016in_square_0.41mm",
   "pad_drill_mm": "0.71",
   "copper_x_width": "[0数据]",
   "copper_y_width": "[0数据]",
   "seat_height_mm": "0.86",
   "hole_center_span_mm": "1.270",
   "mating_footprint": "https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf (SHEET1 FIG1 THT hole pattern; single-row variant direct URL = [0数据])",
   "keepout_dwg": "https://suddendocs.samtec.com/prints/fts-1xx-xx-xx-dx-xx-footprint.pdf + 官网 3D/CAD 下载 (THT 档外形尺寸 = [0数据])",
   "datasheet_url": "https://www.samtec.com/products/fts-102-01-f-s",
   "evidence": "[官网]",
   "prose_anchors": [
    "2 Pin, 1 Row, Through Hole",
    ".028 0.71 (TYP)",
    "Single Through-hole"
   ],
   "value_anchors": {
    "positions_rows": ["1 排"],
    "pitch_mm": ["1.27"],
    "post_size": [".016", "0.41"],
    "pad_drill_mm": ["0.71"],
    "seat_height_mm": ["0.86"],
    "hole_center_span_mm": ["1.270"]
   }
  }
 },
 "generic_part_measured": {
  "lib": "/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty",
  "J_DEBUG": {
   "file": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
   "md5": "7a5f470c1f70d4b832be258501945385",
   "pad_count": 4,
   "pad_size_mm": "1.000x1.000",
   "pad_drill_mm": "0.65",
   "pitch_mm": "1.27",
   "copper_x_width": "4.8100",
   "copper_y_width": "1.0000"
  },
  "J_UART": {
   "file": "PinHeader_1x02_P1.27mm_Vertical.kicad_mod",
   "md5": "47bcbf6d0f267d543e50d4b2a8dfabf5",
   "pad_count": 2,
   "pad_size_mm": "1.000x1.000",
   "pad_drill_mm": "0.65",
   "pitch_mm": "1.27",
   "copper_x_width": "2.2700",
   "copper_y_width": "1.0000"
  }
 },
 "deviation_vs_generic_part": {
  "status": "registered",
  "differing_values": [
   {"part": "FTS-104-01-F-S", "field": "copper_x_width", "samtec_value": "[0数据]", "generic_value": "4.8100"},
   {"part": "FTS-102-01-F-S", "field": "copper_x_width", "samtec_value": "[0数据]", "generic_value": "2.2700"}
  ],
  "d1_pad_diameter_not_samtec_specified": "Samtec 官方直插推荐 PCB 图只给孔位 (Ø0.71 TYP) 不给铜箔焊盘直径 ⇒ 盘上 1.000 mm 焊盘是第三方库件/IPC 口径的选择, 不是厂件数",
  "d2_drill_mismatch": "盘上通用件钻孔 0.65 mm ≠ Samtec 官方 Ø0.71 mm (小 0.06) ⇒ 落 FTS 必须改孔 0.65→0.71; 钻孔不进铜箔包络 ⇒ MECH 余量数不变",
  "d3_courtyard_not_vendor_keepout": "F.CrtYd/F.Fab 来自通用排针库件, 不是 FTS 厂件 keepout ⇒ MECH OI-12 的对照物要重算",
  "impact_targets": [
    "MECH/check_debug_seat_3d_fit.py:L491",
    "MECH/check_debug_seat_3d_fit.py:L683-L686",
    "MECH/check_debug_seat_3d_fit.py:L746",
    "MECH/check_debug_seat_3d_fit.py:L753",
    "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:6.6100",
    "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:4.0700",
    "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:0.1350",
    "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:2.6950",
    "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:0.7700",
    "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:OI-5",
    "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md:OI-12",
    "HW/BOM_v1.csv:J_DEBUG",
    "HW/BOM_v1.csv:J_UART"
   ]
 },
 "degrade_refs": {
  "copper_x_width": "§6-②",
  "copper_y_width": "§6-②",
  "mating_footprint_single_row_url": "§6-①",
  "keepout_dwg_tht_outline": "§6-④",
  "pad_drill_vs_generic": "§6-②"
 },
 "open_items": [
  "OI-387-1: 落 FTS 时板上焊盘是否仍取 1.000x1.000 (决定 MECH 全链余量数是否需要重算) ⇒ to=main",
  "OI-387-2: 板上钻孔 0.65→0.71 的改板动作是否与「板只改一次」那一趟同批 ⇒ to=main",
  "OI-387-3: §㊳ A2 (Samtec 厂件 land) 与 A4 (KiCad 通用件 land) 指向不同封装来源, 落板时须合成一个 ⇒ to=main",
  "OI-387-4: FTS 直插档座体外形 (宽/深) 官方尺寸 = [0数据] ⇒ 走 §6-④ 降级 (官网 3D/CAD 下载 或 实测样件) ⇒ to=mech-lead"
 ]
}
```

---

> **本单边界自证**: ★**零写板** (板 md5 仍 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413`) · ★**零落表** (`HW/BOM_v1.csv` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` 一个字节未动) · ★**零改既有闸** (`MECH/check_debug_seat_3d_fit.py` / `HW/check_debug_uart_seat_alignment.py` / `HW/check_debug_uart_seat_truth.py` 一个字节未动) · ★**零改既有页面正文** (`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 等一个字节未动) · ★**零挂链** (`state/gate_check.py` 未被碰, 命中数 = 0) · ★**零外发** (只读本机 + 自己上网查资料, `state/outbox/` 一个字节未动) · ★**不代拍** (`landing_part_decision = not_decided_here`) · ★**不自签台账** (`state/issue_log.yaml` 一个字节未动) · ★**没写别人的分片** (只写 `state/fragments/hw.yaml`) · ★**沙盒只落 `tmp/iss387/`** · ★**证据分级全页逐条标注** · `[实测]`
