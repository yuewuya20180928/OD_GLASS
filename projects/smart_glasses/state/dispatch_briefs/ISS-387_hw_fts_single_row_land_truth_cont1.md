# ISS-387 · cont1 · hw-lead · 把「FTS 单排直插原厂 land 几何查证」从【真相页已在盘 · 闸/交卷页/分片全缺】做到【三件交付物齐全 + 交卷】· 零写板 · 零落表 · 零改既有闸

★**本单 = ISS-387 cont1 (★不是新单 · 不是从零重做 · ★)** ★
★**本单 = 纯查证 + 纯分析 + 新建文档/闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【查证层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 09:45:20 起 · 10:10:23 止 · 墙钟 25.05 分钟** ★
★**子会话** `agent:hw-lead:subagent:5170b697-022d-4c45-bce0-c87355c7bd3e` / sessionId `5170b697-022d-4c45-bce0-c87355c7bd3e` · transcript 132 行 ★
★★**★死因 = ★**spawn 时的 `runTimeoutSeconds=1500` (25 分钟) 到点被掐** ★★ (★main 本机实算: 09:45:20 + 1500s = 10:10:20 ≈ 实测 10:10:23 止 ⇒ 逐字对齐 ⇒ ★**不是墙, 是本 job 自己给的上限**★) ★★
★★**⇒ 本趟的 spawn 已改成 `runTimeoutSeconds=2400` (40 分钟) ⇒ 本单【不会再被 25 分钟掐死】★★ ★★
★★**★掐死的位置 = 【真相页写完、闸还没开始写】★** ★★ ⇒ ★**上一趟的最后一条 toolCall 是在编辑真相页机器块 (`Successfully replaced 4 block(s)`) ⇒ 闸 (本单主交付物②) 一次都没开写★** ★★
★★**⇒ 本趟定位: 【续做趟】—— 真相页已在盘 ⇒ 只做【新建闸 + 交卷页 + 分片 + 交卷消息】⇒ ★★真相页正文一个字不许删改★★ ★★**

### ★★★上一趟已经在盘的产物 (★main 本机实读 2026-11-24 10:4x~10:5x · 你要自己再核一遍★) ★★★

| ★产物★ | ★大小 / mtime / md5(前8)★ | ★本趟怎么用★ |
|---|---|---|
| ★`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` ★ | 44,122 B @10:10:03 · `3e019b04` ★ | ★**真相页已在盘** ⇒ ★**只许读 + 只许追加式补注 (★正文一字不许删改★)** ★ |
| ★机器块 (真相页 §7.2 的 `json` 代码块) ★ | ★**main 本机实跑 `json.loads` ⇒ rc=0 解析通过** ★ | ★**闸 K0~K6 全部从这块读 ⇒ 闸不许写死任何数★** ★ |
| ★`tmp/iss387/` 沙盒 ★ | `cand_catalog_english_fts.pdf` 468,445 B + `fts_catalog.pdf` 468,445 B + `fts-1xx-xx-xx-dx-xx-footprint.pdf` 143,472 B + `fts_catalog.txt` 10,512 B + `fts_fp.txt` 12,029 B + `fts_fp_sheet-1.png` 108,297 B + `measure_generic_part.py` 4,124 B @10:06 ★ | ★**两份原厂件已在盘 ⇒ 不要重下 ⇒ 直接 `pdftotext` 抄文字层★** ★ |

★★**★main 本机已复核过的读数 (2026-11-24 10:4x~10:5x 实跑 · ★你要自己再跑一遍, 别只抄本表★)★★ ★★

```
$ python3 tmp/iss387/measure_generic_part.py          ⇒ rc=0
  J_UART: pad 1.0x1.0 / 钻孔 0.65 / 1 排 / 排距 [1.27] / 铜箔包络 2.27 x 1.0
           F.CrtYd X -1.55..1.55 (3.1)  Y -1.14..2.41 (3.55)
           F.Fab  X -1.05..1.05 (2.1)   Y -0.635..2.54 (2.54)
$ pdftotext -layout tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf - | head -6
  REVISION N   RECOMMENDED PCB LAYOUT FOR FTS-1XX-XX-XX-DX-XX
  (NO OF POS x .050[1.27]) - .050[1.27]
$ python3 HW/check_debug_uart_seat_alignment.py --selftest  ⇒ rc=0 · ALL TESTS PASS
$ python3 MECH/check_debug_seat_3d_fit.py                 ⇒ rc=0
$ python3 state/merge.py                                  ⇒ rc=0 (产出 839 | 冲突 0)
$ python3 state/gate_check.py                             ⇒ rc=0 (【Q1】18/18)
```

★★**★一条必须如实报进交卷的事实 (★main 本机实读★)** ★★: ★**`python3 state/check_footprint_geom.py` 【裸跑会炸】(★`ModuleNotFoundError: No module named 'pcbnew'`·rc=1★) ⇒ ★真命令是 `bash state/pcbnew_py.sh state/check_footprint_geom.py` (★main 实跑 rc=0·末行「✅ 几何全对」★)** ★★
★★**⇒ 原 brief §五③ 写的那条命令是错的 ⇒ 本趟【已改写成真命令】⇒ 你按本 brief 走, 不要照抄老 brief★** ★★

---

## ★★二 · 本趟的时间预算 (★本项目子会话的真实墙 ★★runTimeout 2400s = 40 分钟★★) ★★

★**顺序不许改 (★每一步都落盘★)**:
1. ★**第 1 步 (≤5 分钟) · 独立复核**: 跑下面 §四 的必跑命令 ①②③ ⇒ ★**把原样输出落 `logs/iss387/cont1_verify.log`** ⇒ ★**逐条对照 §一 的「已在盘」清单 ⇒ 有任何对不上, 如实写出来 (★不许糊过去★)★ ★
2. ★**第 2 步 (≤18 分钟) · 新建闸 `HW/check_fts_single_row_land_truth.py`** (★本单主交付物★) ⇒ ★**先写文件落盘, 再跑裸跑 + `--selftest` ⇒ 修【误报/漏检/崩溃】, 不许放松任何判据★** ★
3. ★**第 3 步 (≤8 分钟) · 交卷页** ★**新建** `HANDOFF/2026-11-24_hw-lead_ISS387_FTS单排直插原厂land几何查证.md` (★B1~B6 六段齐全 + B6 贴必跑命令原样输出 + rc★) ★
4. ★**第 4 步 (≤4 分钟) · 分片** ⇒ ★**只走 `state/frag_write.py`** (★**禁止 `open(p,"w")` 直接写分片**★) ⇒ ★**产出物 ≥3 条 + `interface_claims` ≥5 条 + `needs_from` (`to=main`)★** ★
5. ★**第 5 步 (★最关键★)**: ★**交卷消息 (★上一趟就是死在这★)** ★

★★**★如果时间在第 3 步用完 ⇒ 允许交卷页先写 B1~B5 (B6 可后补) ⇒ ★★但交卷消息【绝对不许省】★★ ★★**

---

## ★★三 · 本单的地界事实 (★不许越★) ★★

★**① 真相页正文一个字不许删改** —— `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` 的 §0~§7 全部在盘且已定稿 ⇒ ★**只许追加式补注 (★追加块要在页尾, 不许插在正文中间, 免得行号位移★)** ★
★★**② 真相页已查到的三个硬结论, 本趟【不许推翻, 只许补证据】★★ ★★
· ★**`FTS-104-01-F-S` / `FTS-102-01-F-S` 真实存在、4 位/2 位、1 排、直插、排距 1.27 mm** ⇒ ★**ISS-383 §0-2「两家都没有单排」被官网单品页逐字推翻** ★`[官网]`
· ★**Samtec 官方直插 land 只给孔位图, 不给铜箔焊盘直径 ⇒ 「原厂 land 的铜箔 X 宽」在 Samtec 那一层【根本不存在官方数】** ⇒ ★**MECH 全链吃的 `4.8100` / `2.2700` 是盘上通用 KiCad 库件的焊盘 `1.000` 算的, 不是厂件数** ★`[官网]`+`[实测]`
· ★**盘上通用库钻孔 `0.65` 比 Samtec 官方 `Ø0.71` 小 `0.06` ⇒ 落 FTS 必须改孔** ⇒ ★**但只要焊盘仍是 `1.000×1.000`, 铜箔包络不变 ⇒ MECH 全链余量数不用重算 ⇒ 结构件不必为这一趟再返工一次** ★`[官网]`+`[实测]`+`[推算]`
★★**③ 「族别辨析」是本单的命门** —— ★**`FTSH-104-01-F-DV` 是双排贴片, 与 `FTS-104-01-F-S` 是不同族、不同件 ⇒ 它的任何数都不许顶替 FTS 的数** ★ ⇒ ★**闸 K4 专门打这一条** ★
★★**④ 板只改一次 ⇒ 本单零写板零落表** —— ★**本单不许碰 `HW/PCB/demo_mainboard.kicad_pcb` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv`** ⇒ ★**BOM 型号栏只给草案 (真相页 §6-③ 已给), 落表时机 = 与 land 改动同一次工序** ★
★★**⑤ 「板只改一次」那一趟的净影响已经算清** —— ★**「只要板上焊盘保持 `1.000×1.000`, MECH 的 `4.8100`/`2.2700`/`6.6100`/`4.0700`/`0.1350`/`2.6950`/`0.7700` 一个数都不用改」⇒ 这条成立条件必须【写下来被闸守住】, 不能只是一句口头结论** ★ ⇒ ★**这正是闸 K3 的活** ★

---

## ★★四 · 本单要交 3 件 (★三件都要在盘 + 交卷页 B1~B6 齐全★) ★★

### ★★交卷物 (3 件) ★★

1. ★**`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md`** (★真相页 · ★**已在盘 · 本趟只许追加式补注, 正文一字不许删改**★) ★
2. ★**`HW/check_fts_single_row_land_truth.py`** (★★新建★★ 新闸 · 零挂链) ★
3. ★**`HANDOFF/2026-11-24_hw-lead_ISS387_FTS单排直插原厂land几何查证.md`** (★★新建★★ 交卷页 · B1~B6) ★

### ★★① 真相页 (★已在盘 · 只许追加式补注★) ★★
★**§0 一句话结论** · ★**§1 查证方法与证据分级** · ★**§2 `FTS-104-01-F-S` 官网单品页逐项抄录** · ★**§3 `FTS-102-01-F-S` 官网单品页逐项抄录** · ★**§4 与盘上通用 KiCad 库件逐项对比表 + §4.1 三条不一致汇总** · ★**§5 与 §㊳ A2/A4 / ISS-379/380/383 的关系与影响面** · ★**§6 降级方案 (6-①~6-⑤)** · ★**§7 复跑命令 + 机器块** ★
★**★本趟只做两件小事**: ★**(甲)** 复核页里每个数还能不能复现出 (★§7.1 的命令逐条能跑 ⇒ 跑一遍, 对不上的在页尾写追加块订正★) · ★**(乙)** 闸写完后, 若闸要求页里有某个新字段 (★如 `gate_checked_by` / `gate_ref`★) ⇒ ★**在页尾追加一小块登记, 不许改 §7.2 机器块既有字段的值★ ★

### ★★② 新闸 `HW/check_fts_single_row_land_truth.py` (★★本单主交付物★★) ★★
★**零挂链** (★`grep -c check_fts_single_row_land_truth state/gate_check.py` 必须 = 0 · 挂链是 main 的地界★) ★
★**fail-closed · 每条判据都要有反向用例 · 判据与事实分开 (★K5 专门打「把判据句和事实句混成一句」★)** ★
★**闸自己从真相页机器块读数 (★不许写死任何数 ⇒ 改页即红★)** ★

| 判据 | ★判什么 (★口径照抄真相页 §4 / §5-①★)★ |
|---|---|
| ★**K0** ★ | ★真相页在盘 + 机器块在盘 + `json.loads` 能解析 + 页里**没有**空字段 (★`[0数据]` 允许, ★**空字符串不允许**★) ★ |
| ★**K1** ★ | ★`positions_rows` 必须是 **1 排** (★**这一条是本单最容易翻车的地方**: ★FTSH 是 2 排, ★**FTS 是 1 排, 族不同**★ ⇒ 页里若写成 2 排必须判红★) ★ |
| ★**K2** ★ | ★`copper_x_width` / `copper_y_width` 必须是【与盘上通用件实测值一致】或【`[0数据]` 且 `degrade_refs` 里有对应条目】⇒ ★**两种情形都合法, 但第三种 (写了个既不等于通用件、又不是 `[0数据]`、也没有降级条目的数) 必须判红** ⇒ ★**闸不许自己写死 `4.8100` / `2.2700`, 要从机器块 `generic_part_measured` 读出来再比★** ★ |
| ★**K3** ★ | ★★**本单的命门**★★: ★真相页里 `copper_x_width` 的值若**不等于**盘上通用 KiCad 库件实测的铜箔宽 ⇒ ★**必须显式登记「与通用件不一致」这个事实 + 影响面清单里点名 MECH 那几行** ⇒ ★**机器块 `deviation_vs_generic_part.status` 必须是 `registered`, 且 `differing_values` 必须逐条列出 `copper_x_width` 的差异 (★`samtec_value` vs `generic_value`★) ⇒ ★**没登记就判红** (★**不许默默写一个不同的数**★) ★ |
| ★**K4** ★ | ★**不许拿 FTSH 的数顶替 FTS** ⇒ ★**页里若出现 `FTSH-` 料号与 FTS 料号混用 (★`FTSH-` 出现在 FTS 料号字段里, 或同一字段里两族并列★) ⇒ 判红** ★ |
| ★**K5** ★ | ★证据分级白名单 (★`[官网]`/`[媒体]`/`[实测]`/`[推算]`/`[0数据]`★) + ★**零挂起措辞** (★「等原厂回信」/「待外部确认」/「等回复」/「pending reply」/「待确认」等语境判红★) + ★**判据句与事实句分开** ★ |
| ★**K6** ★ | ★板三项指纹未动 (★md5 + mtime + size★) + ★**零落表** (★网表/脚表/BOM 三件 md5 与基线同★) + ★**零挂链** (★`state/gate_check.py` 命中数 = 0★) + ★**真相页机器块里 `board_write` / `table_write` / `mech_files_touched` 三个字段的值必须是 `none`★** ★ |

★★**★`--selftest` 至少 8 条反向用例**, ★**其中至少 2 条专打本单的命门**: ★① 页面把 `positions_rows` 从 1 改成 2 ⇒ 必须 K1 红 ★② 页面把 `copper_x_width` 改成一个**与通用件不同的数** 却**没登记影响面** ⇒ 必须 K3 红 ★
★★**★另外建议再加 2 条**: ★③ 把 `deviation_vs_generic_part.status` 从 `registered` 改成别的 ⇒ K3 红 ★④ 把 `FTSH-104-01-F-DV` 塞进 FTS 料号字段 ⇒ K4 红 ★
★★**★你的新闸自己必须【与环境无关】★** (★★**沙盒临时目录放在【项目盘】`tmp/iss387_sbx/`, 路径从本闸自己的 `ROOT` 推, 不许依赖系统 `/tmp` 的深度 —— 现役 `SW/tools/check_debug_pin_order_contract.py` 今天实测就栽在这里: 默认 `/tmp` ⇒ 10/11 FAIL, `TMPDIR=$PWD/tmp` ⇒ 11/11 PASS★★) ★★

### ★★③ 交卷页 `HANDOFF/2026-11-24_hw-lead_ISS387_FTS单排直插原厂land几何查证.md` (★★新建★★) ★★
★**B1~B6 六段齐全** (★**闸认这六段, 缺一段就红**★) + ★**B6 必须贴必跑命令的原样输出 + rc** ★
★★**★B1~B6 的标题必须含 gate_check.py 认的关键词 (★本机实读 `state/gate_check.py` 的 `REQUIRED_BLOCKS`★)★★ ★★
| 块 | ★标题里必须出现★ |
|---|---|
| B1 | ★`结论` (或 `结论摘要` / `一句话`) ★ |
| B2 | ★`验收标准自评` (或 `自评` / `验收标准`) ★ |
| B3 | ★`证据分级` (或 `证据等级` / `证据`) ★ |
| B4 | ★`接口取值` (或 `接口声明` / `interface_claims` / `接口请求`) ★ |
| B5 | ★`未决` (或 `卡点` / `阻塞` / `待办`) ★ |
| B6 | ★`复现` (或 `复现命令` / `自证`) ★ |
★★**★命门: `state/gate_check.py` 的 `pick_handoff` 规则 = 「取最新一份交接单评分; 若最新一份自称 B 块结构但缺块 ⇒ 【不许回退】⇒ 真倒退 ⇒ Q1 立刻掉」⇒ ★★你这份一旦自称 B1~B6, 六段就必须真齐全, 不许缺一块★ ★★** ★★

---

## ★★五 · 分片 ★★
★**只走 `state/frag_write.py`** (★**禁止 `open(p,"w")` 直接写分片**★) ★
★**产出物 ≥3 条 + `interface_claims` ≥5 条 + `needs_from` (★`to=main`★) ★**
★**★`needs_from` 必须逐条写清「要谁回答什么 + 代价」, 不许只写「请裁决」★** ★
★**★真相页机器块里已登记的 4 条 `open_items` (OI-387-1~4) 就是本单 needs 的底稿 ⇒ 照抄进 `needs_from` 即可 (★OI-387-4 是 `to=mech-lead` 的那条 ⇒ 你照样登记进本单 needs, 但 `to` 写 main 并注明「mech-lead 侧执行」★)** ★
★★**坑 (★main 本机实测过的★) ★★**: ★**`state/frag_write.py --add-*` 的分隔符是【空格】不是【分号】** (★`shlex.split()` 切参数 ⇒ 写成 `path=…;summary=…` 会把整串吞进 `path` ⇒ **写出畸形条目却照样打印「✅ 已原子更新」**★) ⇒ ★**写完必须 `grep` 复验条目唯一, 不许只信它打印的那行** ★

---

## ★★六 · ★★本单必跑的坑 (★main 本机实测踩过, 你不要重踩★) ★★

★★**坑 1 ★★ `--selftest` 必须与环境无关** (★沙盒落项目盘 `tmp/iss387_sbx/`, 不许写系统 `/tmp`·不许用硬链接·不许 `cp -al`★) ★
★★**坑 2 ★★ 官网/分销页可能拿不到** ⇒ ★**但本单两份关键几何来源 (`tmp/iss387/fts_catalog.pdf` + `tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf`) 已在盘 ⇒ 不许重下 ⇒ 直接 `pdftotext` 抄文字层** ★
★★**坑 3 ★★ 「官方 PDF 机械图」本机没有图形解析器** ⇒ ★**只准把官网上的【文字参数】抄进页里 + 标证据等级; ★不许把 PDF 里的图当已核实几何★ ⇒ 几何要么来自官网文字/表格, 要么标 `[0数据]`** ★
★★**坑 4 ★★ `state/check_footprint_geom.py` 裸跑会炸** ⇒ ★**必须用 `bash state/pcbnew_py.sh state/check_footprint_geom.py`** ★
★★**坑 5 ★★ 真值页的机器块是闸的输入** ⇒ ★**改页即红 (这是设计, 不是 bug) ⇒ 闸写好后你要【故意改一次页】验证 K2/K3 会红 (在沙盒副本上改, 不许改真页)** ★

---

## ★★七 · 必跑命令 (★全部实测存在的真命令 ★· 不许自己编★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ① 命令存在性守卫 (★派活前 main 已跑过 rc=0, 你开工再跑一遍★)
python3 state/check_brief_commands.py

# ② 盘上通用 KiCad 库件自己实测 (★上一趟已写好脚本, 不许重写★)
python3 tmp/iss387/measure_generic_part.py

# ③ 原厂件文字层 (★两份 PDF 已在盘, 不要重下★)
pdftotext -layout tmp/iss387/fts-1xx-xx-xx-dx-xx-footprint.pdf - | head -40
pdftotext -layout tmp/iss387/fts_catalog.pdf - | head -40

# ④ 通用封装几何闸 (★★真命令 = 带 pcbnew 包装器★, 裸 python3 会炸★)
bash state/pcbnew_py.sh state/check_footprint_geom.py

# ⑤ 已签收的相关闸 (★只读, 用来对照口径·不许改★)
python3 HW/check_debug_uart_seat_alignment.py
python3 HW/check_debug_uart_seat_alignment.py --selftest
python3 HW/check_debug_uart_seat_truth.py
python3 MECH/check_debug_seat_3d_fit.py
python3 MECH/check_debug_seat_3d_fit.py --selftest

# ⑥ 本单新闸 (★你自己写的, 裸跑 + selftest★)
python3 HW/check_fts_single_row_land_truth.py
python3 HW/check_fts_single_row_land_truth.py --selftest

# ⑦ 板 / 三表 指纹 (★开工前后各打一次, 逐项对比★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑧ 收尾 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/frag_write.py --agent hw-lead --show
python3 state/merge.py
python3 state/gate_check.py
```

★★**基线 (★main 2026-11-24 10:4x 本机实跑, 你自己再核一遍★)** ★★
```
板 md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 · size = 4940213
网表 6aee500e60ba0732f83a9cf557ba90ab · 脚表 9174309df1ec9411ac8e8d9e80ee386a · BOM 5b9993992405904a60ac96a020b375d8
真相页 md5 = 3e019b04f469bce196529300bf374979 · 44,122 B
gate_check.py md5 = 5f370bb8cf828473e70ccc5d6412da98 (★不许碰★)
MECH/check_debug_seat_3d_fit.py = 667e6006280cc8c0533d8ce8fa39f8be (★不许碰★)
MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md = 3d0c8e7de86e0f853450dcb7404d9f44 (★不许碰★)
HW/check_debug_uart_seat_alignment.py = 52e067ed99edaaced50fd565bed90042 (★不许碰★)
HW/check_debug_uart_seat_truth.py = 274f759101ca4bc131f25633dc209b0c (★不许碰★)
⇒ ★**板 18 天逐字节未动 ⇒ G1 仍开, 不许投板** ★
merge.py ⇒ rc=0 · gate_check.py ⇒ rc=0 · 【Q1】18/18 · 【Q7】钉板 md5 闸链 10/10 道绿
```

---

## ★★八 · 边界自证 (★交卷页里必须有这一段★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5/mtime/size 前后逐字相同★ |
| ★零落表★ | ★网表/脚表/BOM 三件 md5 前后逐字相同★ |
| ★零改既有闸/既有页面正文★ | ★`MECH/check_debug_seat_3d_fit.py` / `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` / `HW/check_debug_uart_seat_alignment.py` / `HW/check_debug_uart_seat_truth.py` / `state/gate_check.py` 等 md5 与基线同★ |
| ★零改真相页正文★ | ★真相页只许追加式补注; ★追加前后 §0~§7 正文 md5 与基线同★ |
| ★零挂链★ | ★`grep -c check_fts_single_row_land_truth state/gate_check.py` = 0★ |
| ★零外发★ | ★全程只读本机 + 自己上网查; ★`state/outbox/` 一个字节未动★ |
| ★不代拍★ | ★页里没有「已决定 / 应采用」式裁决语; ★`landing_part_decision = not_decided_here` 这个机器块字段必须有★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 你一个字节未动★ |
| ★没写别人的分片★ | ★只写 `state/fragments/hw.yaml`★ |
| ★沙盒纪律★ | ★只落 `tmp/iss387/` 与 `tmp/iss387_sbx/`; ★不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★ |
| ★证据分级★ | ★每条结论标五级之一★ |
