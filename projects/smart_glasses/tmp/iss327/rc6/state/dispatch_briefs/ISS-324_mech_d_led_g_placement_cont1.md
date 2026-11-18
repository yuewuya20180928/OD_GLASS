# ISS-324 · mech-lead · ★★cont1 续做: 把已算完的候选终表落成交卷页 + 交卷页 + 分片 (★交付物①②③ 一个都不在盘上★)★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-324 (★**cont1**★)
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 12:1x** ★
> ★**性质**: 内部活 · ★**纯分析 / 作业包 / 判据设计类 (MECH 侧)** ★ · 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 沙盒只写 `tmp/` + `logs/iss324/` · 零外发 · 不替老板拍板 · 不自签 issue_log
> ★**上游**: `ISS-271` (板侧认领 · `D_LED_G` 位置口径查证 · verified) · `ISS-316` (结构侧输入包 · verified) · `ISS-319` (差集归属 · verified) · `ISS-320` (电芯型号订正实做 · verified) · `ISS-283` (G-5 亮度档 · **老板 2026-11-17 09:49 已拍**)

---

## ★0 · ★★为什么有这一趟 cont (★main 12:1x 本机实读·不猜★)★★

★**上一趟 (11:4x 派出) 的子会话 `agent:mech-lead:subagent:ed19e10c-…` 在 12:0x 被父 cron run 连带 abort (★`status=timeout` · `abortedLastRun=true` · runtimeMs=1156074★)** ★
★**⇒ 它做完的是【算】, 没做完的是【写】** ★
★**⇒ ★★本单只剩 3 件事: 交付物① · 交付物② · 分片 —— 全是「把算好的读数落成文档」的活★★ ★

---

## ★1 · main 12:1x 本机实读: ★**已经算完的读数 (★全在 `logs/iss324/` 里·不用重算·不许重跑★)★**

| # | 已在盘上的东西 (★main 逐件实读★) | 内容 |
|---|---|---|
| ① | ★**`logs/iss324/05_candidates.log`** (★6,971 B★) ★ | ★★★**★本单最值钱的一件: 候选落位点终表 (帧 B160x100 · 现役台架板) = C1~C6 六个候选, 每个候选 7 项读数 (封装原点 / 焊盘绝对坐标 / 到 `R_LED_G.2` 直线距离 / 最近邻器件净距 / 对 §3 坐标空间落位 / 改板 md5 影响 / 余量) 全填实★★** ★ |
| ② | ★**`logs/iss324/03b_board_frame_coords_json.log`** + `03c_s6_check_json.log` + `03d_recompute_f30a_space.log` ★ | ★**双板框坐标空间的机器读数 (★含 F30A 60×30 那条·rc=0★)** ★ |
| ③ | ★**`logs/iss324/02_recompute_led_space.log`** + `03_board_frame_coords_compute.log` ★ | ★**LED 侧可放行空间复算 + 板框坐标推导 ★** |
| ④ | ★**`logs/iss324/04_zero_data_scan.log`** (★76,567 B★) + `04a_grep_mech_led.log` (★30,394 B★) ★ | ★★**§2「结构侧有没有 LED 位置规定」的【0数据】查证证据 ★** —— ★**注意: `04a_grep_mech_led.log` 里 ★**149 处 `D_LED_G` 命中**, 其中 ★**`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 确实登记了 `D_LED_G` 首选窗口 ⇒ ★**★这一条【不是 0数据】, 是【有登记但要分清哪条适用哪块板】—— 你必须把这层说清, 不许简单写「0数据」★★** ★ |
| ⑤ | ★**`logs/iss324/04b_web_search.log`** (★2,666 B★) ★ | ★**官网检索记录 (Kingbright KP-2012SGC 官方规格 + 导光柱尺寸) + 抓取时刻 ⇒ ★**这条已经是【自己查到的官网证据】·你不用重查·直接引用并标 `[官网]`★** ★ |
| ⑥ | ★**`logs/iss324/01_probe_led_pads.log` / `01b_probe_ledg_channel.log` / `01c_probe_som_pad_pitch.log`** ★ | ★**焊盘坐标 / `LED_G` 通道 / `J_SOM_P4` 焊盘间距 (0.4mm pitch) 的只读探针读数 ★** |
| ⑦ | ★**`logs/iss324/` 共 20 件** (★含 6 个只读探针/复算脚本★) ★ | ★★**★你写的那些探针脚本都还在 (`probe_led_pads.py` / `probe_ledg_channel.py` / `probe_som_pad_pitch.py` / `recompute_led_space.py` / `recompute_f30a_space.py` / `compute_candidates.py` / `check_zero_data_led.py`) ⇒ ★**★不需要重写探针, 直接引用它们的输出★**★ ★ |

★**★⇒ 结论: 本单是【写卷】不是【算卷】★ ⇒ ★**你唯一要做的新计算 = §1-④ 那一层的口径澄清 (MECH 域的 149 处命中里哪些适用现役台架板) + 把 `05_candidates.log` 的六个候选按判据排序** ★

---

## ★2 · 本单要交的 3 件事 (★做完就算交卷★)

### ★★交付物 (2 件) · ★★这两份是本单新建的文件 (★交卷时才有 ⇒ 交卷前必然不存在★)★★

1. ★**新建 `MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md`** ★ (★主交付物·§0~§9★)
2. ★**新建 `HANDOFF/2026-11-18_mech-lead_ISS324_D_LED_G落位口径.md`** ★ (★交卷页·B0~B6★)

### ★① 【主交付物】`D_LED_G` 落位口径一页 (★新建文档★)

- ★**落点**: ★**`MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md`** (★**新建**; ★**`MECH/**` 下的既有文件一个字节都不许改**★) ★
- ★**章节 (每一节都要填实, 不许写「同上」/「见前」)**:
  | § | 内容 | ★**硬要求** ★ |
  |---|---|---|
  | §0 | ★**口径与边界自证** ★ | ★**写清本单是什么 / 不是什么 (零写板 · 零落表 · 零改闸 · 零改既有文档正文)★** ★ |
  | §1 | ★**现状复算 + 根因分解** ★ | ★**自己复算 `LED_G_D` 的 93.492727 mm (★`R_LED_G.2` (7.50,62.60) ↔ `D_LED_G.1` (100.80,56.60) ⇒ `math.hypot(93.30,6.00)`★) + X/Y 分解 (★X 向 93.30 mm = 99.794%★) + 说明「★**为什么是布局问题不是板子不够大**★」 ★ |
  | §2 | ★**结构侧到底有没有 `D_LED_G` 位置规定 (★★必须比「[0数据]」更精确★★) ★** | ★**★把 `logs/iss324/04a_grep_mech_led.log` 的 149 处命中分类: 哪些是【真位置规定】/ 哪些是【引述作业包】/ 哪些是【只覆盖 F30A 60×30 那块板】★★ ⇒ ★**★特别是 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 `D_LED_G` 首选窗口 (★X 33.00..47.71 × Y 1.60..28.40, 标 F30A 帧★) ⇒ ★**★它【不适用现役台架板 B160x100】★ ⇒ 你必须把【现役台架板】与【产品板 F30A】两套坐标空间分开写, 不许混★★** ★ |
  | §3 | ★**双板框假设的坐标空间** ★ | ★**台架板 B160x100 一份 + 产品板 F30A 60×30 一份, 各给可放行带 (X/Y 区间) + 依据 + 净距敏感度 (★照 `logs/iss324/03b` + `03d` 的机器读数逐字搬★)★** ★ |
  | §4 | ★**G-5 亮度档的事实订正 + 影响链** ★ | ★**写清「★**已拍 (ISS-283, 2026-11-17 09:49, 选项②) = 绿 `R_LED_G` 55Ω±1% / 红 `R_LED_R` 68Ω±1%**★」+「★**但盘上三个 LED 串阻封装的 Value 还是 `1k ±1%` (★main 12:1x 实读: `R_LED_G` = `R_LED_B` = `R_LED_R` = `1k ±1%`·而网表 `HW/netlist_v1.csv` L301/L304 已写 68Ω/55Ω★) ⇒ 【板那一趟要同步器件值】★」+ 影响链 (网表 → BOM → 板面) 每一步归谁** ★ |
  | §5 | ★**出光孔两假设 (有孔 / 无孔)** ★ | ★**各一份可放行空间 + 差异 + 哪个假设对板面更友好 (★照 `05_candidates.log` 里 C6 那条「整高自由带内 (假设 B 无光孔口径)」的口径★)★** ★ |
  | §6 | ★**候选落位点 (★≥3 个·照 `logs/iss324/05_candidates.log` 的 C1~C6 逐字搬★)** ★ | ★**每个候选给: 封装原点坐标 · 焊盘绝对坐标 · 到 `R_LED_G.2` 的直线距离 · 最近邻器件净距 · 对 §3 坐标空间的落位 · 改板 md5 的影响 (动 / 不动)· 余量** ★ ★**★并且必须【按判据排序 + 说明谁被淘汰】★★ ★ |
  | §7 | ★**给 hw-lead 的 `PCB_PART_POS` 候选行 (★沙盒不落表★)** ★ | ★**逐字可抄的候选行 (★格式对齐 `state/plan_part_moves.py` 的 `PCB_PART_POS="REF:x,y"` 写法★) + 一句「★**这是候选不是决定**★」 ★ |
  | §8 | ★**机器可判判据建议 (★新闸设计 · 零改闸★)** ★ | ★**给出判据条目 (例: `LED_G_D` 直线距离上限 / 与邻件净距 / 落位必须在坐标空间内) + 每条的反向用例设计 (★证明闸不是装饰★) + 挂闸建议 (★交 main★) ★ |
  | §9 | ★**证据分级 + 零写板双证 + 文件清单 ★** | ★**`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 逐条标 + 板 md5/mtime 交卷前后 + 占位符扫描 0** ★ |
- ★★**★§6 的候选排序必须处理掉 main 12:1x 实测到的一个真问题★**: ★**`05_candidates.log` 里 C1 与 C4 的「最近邻器件净距」都记着 `C_KEY_CAM 0.000 mm` 与 `R_LED_G 0.000 mm` —— 而 main 12:1x 用 pcbnew 直读现役板复算: `C_KEY_CAM` 原点 (10.7, 62.5) 只有 1 个焊盘 (10.7,62.6); `R_LED_G` 原点 (5.9,62.5) 有 2 个焊盘 (5.9,62.6)/(7.5,62.6) ⇒ ★**C1 候选的 `D_LED_G` pad1 (7.80,63.50) 距 `R_LED_G.2` (7.5,62.6) = 0.949 mm, 距 `C_KEY_CAM.1` (10.7,62.6) = 1.273 mm, 距 `TP_LED_G.1` (6.1,65.6) = 2.702 mm** ★ ⇒ ★★**⇒ 「0.000 mm」那两行必须逐条复算并说明口径 (★是 pad 边缘距还是原点距? 净距算的是哪个对象?★) ⇒ ★**★不许把 0.000 照抄进交付页当结论, 必须给出你自己的复算读数 + 口径说明**★** ★**
- ★**占位符扫描必须 0** (★扫 `🔄` / `待填` / `PLACEHOLDER` / `施工中★)

### ★② 交卷页 (★标准验收块 B0~B6 齐全★)

- ★**落点**: ★**`HANDOFF/2026-11-18_mech-lead_ISS324_D_LED_G落位口径.md`** ★
- ★**B0** 一句话 + 交付物清单 · ★**B1** 结论摘要 (★**★第一条必须是「`D_LED_G` 落位到底定在哪 + 直线距离变成多少」★**) · ★**B2** 验收标准自评 (★逐条 通过/不通过/未验★) · ★**B3** 证据分级 · ★**B4** 接口取值声明 (★**别人要照抄的东西逐字给: 候选坐标行 + 判据条目 + 降级方案★**) · ★**B5** 未决项与卡点 (★need key + 一句话问法 + 不拍的后果★) · ★**B6** 自证复现命令 (★逐条可跑·输出已落盘★)
- ★**占位符扫描 0**

### ★③ mech 分片

- ★**落点**: ★**`state/fragments/mech.yaml`** · ★**必须走 `python3 state/frag_write.py --agent mech-lead` 原子写** ★ (★禁止 `open(p,"w")`★)
- ★**内容**: artifacts (≥2 · 指向 ①②) · needs_from (★**一条新的 need: `iss324_d_led_g_placement_decision` (★key 自拟但必须唯一 + 写在交付页里★) · 问法 = 「★**`D_LED_G` 落在板上哪个点 + 亮度档已拍后是否还要动器件位置**★」· 不拍的后果 = 「★**`LED_G_D` 93.49 mm 这条 + `LED_G` 净距那条布不了 ⇒ S8 归不了零 ⇒ G1 开不了**★」· 谁答 = ★**mech-lead + 老板 (★依赖 MECH 侧落位★)★**) · interface_claims (≥1 · 给 hw-lead 的候选坐标行 + 判据条目) · status
★**★写之前先 `python3 state/frag_write.py --agent mech-lead --show` 看现状 ⇒ 不要重复 add 同 key (⇒ merge 会报重复/冲突)★** ★

---

## ★3 · 交卷前必跑 (★逐字可粘贴·输出原样贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 板框可行域 (★双假设的机器读数)
python3 MECH/board_frame_feasibility.py --json
python3 MECH/board_frame_feasibility.py --selftest

# ② MECH 侧既有闸 (★交卷前必须全绿·不许带红交卷★)
python3 MECH/check_onepass_mech_sync.py --selftest
python3 MECH/check_board_frame_coords.py
python3 MECH/check_demo_struct_truth.py

# ③ 门禁链 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py

# ④ 零写板双证
md5sum HW/PCB/demo_mainboard.kicad_pcb        # 期望 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb  # 期望 2026-11-06 07:07:17.362193413

# ⑤ 占位符 (★两份交付文档都必须 0★)
grep -cE "🔄|待填|PLACEHOLDER|施工中" MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md
grep -cE "🔄|待填|PLACEHOLDER|施工中" "HANDOFF/2026-11-18_mech-lead_ISS324_D_LED_G落位口径.md"

# ⑥ 分片已写 (★必须 ≥1★)
grep -c "iss324" state/fragments/mech.yaml
```

---

## ★4 · 边界 (★一条都不许越★)

| # | 边界 | 自证方式 |
|---|---|---|
| 1 | ★**零写板** ★ | ★板 md5 + mtime 交卷前后逐字节相同 ★ |
| 2 | ★**零落表** ★ | ★网表 / 脚表 / BOM / 原理图源 md5 全部未变 (★★G-5 的板面器件值同步 = 板那一趟的活, 本单只写进影响链★★) ★ |
| 3 | ★**零改闸** ★ | ★**`MECH/*.py` 全部 md5 未变** (★新闸只给设计, 不建闸; 建闸是 main 的活★) ★ |
| 4 | ★**零改既有文档正文** ★ | ★**`MECH/*.md` 真件 md5 全部未变** (★本单只新建 ①·不改老文档★) ★ |
| 5 | ★**不写别人的分片** ★ | ★**只写 `state/fragments/mech.yaml`** ★ (★`hw.yaml` / `sw.yaml` / `pm.yaml` 一个字节都不许碰★) ★ |
| 6 | ★**零外发** ★ | ★**不许发任何邮件 / 询价 / 问询 / 采购 ⇒ 结构件 / LED 的官网资料一律自己网上查 + 标证据等级 + 查不到写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ (★`logs/iss324/04b_web_search.log` 已经是自己查到的官网证据·直接引用★) ★ |
| 7 | ★**不替老板拍板** ★ | ★**落位与亮度档 ⇒ 只交 need + 建议默认值 + 代价 + 不拍的后果; 你给候选坐标, 不给「决定」** ★ |
| 8 | ★**不自签 issue_log** ★ | ★`state/issue_log.yaml` 一个字节不许动 (★签字是 main 的活★) ★ |

---

## ★5 · 时间盒 (★本项目的老教训★)

★**整单 ≤ 45 分钟** ⇒ ★**本单是写卷活, 读数全在盘上** ★ ⇒ ★**★不许重跑探针 (★`logs/iss324/` 的 20 件已够·重跑只会烧时间并可能撞 `/tmp` 配额★)★** ★
★**★若 45 分钟还没写完, 停下来交已完成的部分 (★§1~§5 写完即交·§6~§9 可以标「未验」★), 不许硬撑★** ★

---
