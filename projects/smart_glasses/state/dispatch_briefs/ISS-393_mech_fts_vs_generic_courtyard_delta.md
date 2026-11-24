# ISS-393 · mech-lead · MECH 侧【「通用库件 courtyard 被当成厂件」这条前提错误的扩散面清账 + 判决链重算】⇒ 把「换厂件之后哪些数要重算」变成机器可判

★**本单性质**: ★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【板那一趟·MECH 侧对照物真值层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★
★★**★本单为什么必须做 (★main 本机实跑 · 不抄任何 agent 报告★) ★★** ★★

★**① ISS-390 (★mech-lead · 今日 12:5x 已交卷★) 查到了厂件 (★Samtec `FTS` 单排直插★) 的真外形: ★**座体宽 X = N × 1.27 (★4 位 = `5.0800` · 2 位 = `2.5400`★) · 座体深 Y = `2.1600` · 绝缘体高 Z = `0.8600` · 柱高 `3.05`** ★ `[官网]` (★官网机械/营销图 PDF·md5 `69d9415867cd642d6a6e07c6b755516b`★) ★
★**② ★★但 main 本机实读: MECH 整条 3D 判决链吃的 `4.8100` / `2.2700` / `6.0900` / `5.0800` / `2.6400` 全是【盘上通用 KiCad 库件】的数, 与 Samtec 无关** ★
★**★main 本机独立复核 (★不是抄 ISS-390★)★**: ★**本机库件 `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod` ⇒ `(drill 0.65)` + `F.CrtYd` 矩形 `(-1.55,-1.14)..(1.55,4.95)` ⇒ 宽 `3.10` 高 `6.09` ⇒ `6.0900`/`5.0800` 是第三方库件的数** ★★
★**③ ★★⇒ 而这条「前提错误」已经扩散到 §【已签收闸的源码字符串】里★ ⇒ ★★**main 本机实读 `MECH/check_debug_seat_3d_fit.py`: 「官方」命中 ★**15**★ 处, 其中 L848/L879 两处逐字写着「★而官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 判据要求比 courtyard 还大 0.5200★」** ★★**
★**④ ★★⇒ 后果: 「判据偏紧 `0.5200`」这个结论的【对照物是错的】 ⇒ 厂件外形一补上, 结构侧判决链上每一个拿这个对照物算出来的数都要重算** ★★**
★**⑤ ★★**且 ISS-390 自己算出一条本单之前没人算过的数**: ★**若「罩住」判据从罩铜箔扩到罩座体本体: X 需 `6.8800`/`4.3400` (★各缺 `0.2700`★) · ★**Y 需 `3.9600` (★缺 `1.1600`★)** ★ · 而罩开口 Y `4.6000` 最多只容 `2.8000` ⇒ Y 向从「零余量卡死」变成「缺 `1.1600` 卡死」 ⇒ ★**`OI-13` 的「接受零余量」选项已不存在** ★★**

---

## ★★一 · 本单的地界事实 (★main 本机实跑 · 逐条给了出处★) ★★

### ★★① 库件真身 (★main 本机实读 .kicad_mod★) ★★

```bash
cd /home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty
sed -n '113,121p' PinHeader_1x04_P1.27mm_Vertical.kicad_mod   # ⇒ (fp_rect (start -1.55 -1.14) (end 1.55 4.95) ... (layer "F.CrtYd"))
grep -n "drill" PinHeader_1x04_P1.27mm_Vertical.kicad_mod      # ⇒ (drill 0.65)
```
★**⇒ `F.CrtYd` 宽 `3.10` 高 `6.09` · 钻孔 `0.65` ⇒ `6.0900` 是第三方库件的数, 与 Samtec 无关** ★

### ★★② 前提错误在已签收闸的源码字符串里 (★main 本机实读★) ★★

★**`MECH/check_debug_seat_3d_fit.py` 逐字 (★main 实读 L847-848 与 L879 附近★)**:
```
"basis": "官方 THT 真 land 铜箔 X 4.8100 + 2 x (CRIT + TOL) 1.8000 = 6.6100; "
         "而官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900 ⇒ 判据要求比 courtyard 还大 0.5200",
...
"(★事实: 官方 1x4 THT 的 F.CrtYd 只有 6.0900 X, 而判据要求清空区 6.6100 ⇒ 比 courtyard 还大 0.5200★)",
```
★**⇒ ★★**「官方」在这道已签收闸里出现 15 处; 而 `6.0900`/`5.0800` 实测是通用库件的数 ⇒ 【对照物错误】已经写进闸源码★ ★★

### ★★③ ISS-390 已查到的厂件真值 (★★`[官网]` 级·★你本单要独立复核, 不许只抄★) ★★

★**官网机械/营销图** `FTS-1xx-xx-x-sx-mkt.pdf` (★Samtec `suddendocs.samtec.com` 直连·HTTP 200·190339 B·md5 `69d9415867cd642d6a6e07c6b755516b`★) ⇒ ★**文字层逐字**: ★`(NO OF POS x .0500 [1.27])` · `.085 2.16 REF` · `.034 0.86 REF` · `.120 [3.05] POST` ★
★**⇒ 座体宽 X = N × 1.27 (★4 位 = `5.0800` · 2 位 = `2.5400`★) · 深 Y = `2.1600` · 绝缘体高 Z = `0.8600` · 柱高 `3.05`** ★ `[官网]`
★**★⇒ 关键差 (★main 本机算★)★**: ★**通用库件 `F.Fab` X `5.0800` (4 位) 与厂件 X `5.0800` 恰好同值 ⇒ ★**这掩盖了 X 方向的错**★; ★**但 2 位档通用库件 `2.6400` vs 厂件 `2.5400` ⇒ 差 `0.1000`; 且跨排距通用 `2.1000` vs 厂件 `2.1600` ⇒ 差 `0.0600`** ★★**

### ★★④ Y 向缺 `1.1600` 这条 (★ISS-390 实测·★你本单要独立复算★) ★★

★**现状口径 (只罩铜箔)**: 清空区 Y 需 `2.8000` (★开口 Y `4.6000` 恰好只容 `2.8000`★) ⇒ 现状是「零余量卡死」
★**座体口径 (连座体本体一起罩)**: 座体深 Y = `2.1600` ⇒ 清空区 Y 需 `2.1600 + 2 × 0.9000 = 3.9600` ⇒ ★**缺 `1.1600`** ★
★**⇒ `OI-13` 的「接受零余量」选项在新口径下【已不存在】** ★

---

## ★★二 · 本单要交 4 件 (★就这 4 件·不要顺手多跑别的★) ★★

### ★★① 新建真相页: `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` (★新建★) ★★

★**必须包含 (★每条都要有出处 + 本机实跑命令★)**: ★
★**(a)** ★★**「两本对照账」表**★★: ★★把 MECH 判决链上【每一个】被消费的几何量列成三列 —— ★**数值 · 现在的出处 (★通用库件 / 厂件 / 推算 / 0数据★) · 换厂件之后的新值** ★★ ⇒ ★**逐个点名: 座体宽 X (4 位 / 2 位) · 座体深 Y · 绝缘体高 Z · 柱高 · 铜箔包络 X/Y (★这两个【不变】·孔位不动★) · 钻孔 Ø (★`0.65 → 0.71`·★铜箔包络不动★) · 判据要求的清空区 X/Y** ★★ ★
★**(b)** ★★**「换厂件之后哪些数要重算」的重算清单**★★: ★★逐条给出 ★**【现在的数】/【厂件真值下的新数】/【差】/【这个数被哪道闸/哪一页消费着 (★给文件+行号★)】** ★★ ⇒ ★**明确分成三类: 【A 类·换厂件后不变 (★并给出为什么不变·★例如铜箔包络只看焊盘不看钻孔★)】/【B 类·换厂件后变了 (★给出新数与差★)】/【C 类·依赖 main/boss 还没拍的口径 (★只摆两三个选项与各自代价·不代拍★)】** ★★ ★
★**(c)** ★★**「前提错误」的扩散面清单**★★: ★★★**全仓逐处扫出「把通用库件的数写成『官方』」的地方** ★★ ⇒ ★★**main 已实测两处起点 (★`MECH/check_debug_seat_3d_fit.py` L848 / L879 的源码字符串★) + `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` L634 的 OI-12 答复 + `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` L26/L114/L168/L193/L854 + 两块 clearance 页的「座体本体」口径** ★★ ⇒ ★**你要【自己实跑 grep 全仓】把扩散面【扫全】, 不许只抄 main 列的这几处** ★★ ★
★**(d)** ★★**Y 向缺 `1.1600` 的完整复算 (★独立复算·★不许只抄 ISS-390 的数★)**: ★**含「座体口径 vs 铜箔口径」两条路的**代价**各自多少 (★比如放大罩开口 Y 要到多少·★两种口径下 X/Y 各自缺多少·★以及哪个数一动就顶死另一个数★)** ★★ ★
★**(e)** ★★**降级方案 (★必须项·不是可选项★)**: ★★**官网图已到手 ⇒ 主力路径是「用官网图」; 但 REF 公差未知 ⇒ 必须同时给出「落 FTS 时先打一块单板样 + 卡尺量三个量」的可执行动作 (★谁在什么时候量哪三个量·量完填回哪一格★)** ★★ ⇒ ★★**不许出现「等原厂回信」/「待外部确认」/「等放行」这类措辞** ★★ ★
★**(f)** ★★**每段带证据等级 (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★)** ★
★**(g)** ★**机器块** (★`--emit` 可解析★): ★`dimensions` / `delta_by_class` / `spread_sites` / `y_direction_gap` / `degradation` 五个键 ★

### ★★② 新建机器闸: `MECH/check_fts_vs_generic_courtyard_delta.py` (★新建★) ★★

★**判据 (★fail-closed · 每条都有反向用例★)**: ★
| 键 | 判据 |
|---|---|
| ★**G1** ★ | ★★**真相页机器块里的每个几何量必须带 `source` 字段 (★`generic_library` / `factory` / `derived` / `missing` 四选一★) ⇒ 缺 `source` ⇒ 红** ★★ |
| ★**G2** ★ | ★★**凡标 `generic_library` 的数, 页面正文里不许出现「官方」这个定性词** ⇒ ★★**出现 ⇒ 红并点名哪一行 + 哪个数** ★★ |
| ★**G3** ★ | ★★**「两本对照账」必须【覆盖判决链实际消费的每一个量】** ⇒ ★★**闸自己实读 `MECH/check_debug_seat_3d_fit.py` 与 `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` 抽出被消费的数 (★逐个给行号★) ⇒ 账里缺任何一个 ⇒ 红** ★★ |
| ★**G4** ★ | ★★**A/B/C 三类分类必须【每个量都有】** ⇒ 缺分类 ⇒ 红; ★**且 A 类 (不变) 必须给出不变的理由 (★不许空着·★例如「铜箔包络只看焊盘不看钻孔」★)** ★★ |
| ★**G5** ★ | ★★**Y 向缺口必须可复算**: 闸自己按机器块里的座体深 Y + 判据余量重算 Y 缺口 ⇒ 与页面写的数不一致 ⇒ 红; ★**且「Y 缺口 = 0」这种「零余量」结论必须被点名 (★因为新口径下它不成立★)** ★★ |
| ★**G6** ★ | ★★**扩散面扫描**: 闸自己实跑全仓 grep, 凡在「已签收闸源码 / 已签收页正文」里出现「通用库件数 + 官方定性」组合 ⇒ 红并逐处点名 (★文件+行号★)** ★★ |
| ★**G7** ★ | ★**零扰动 (板三指纹 + 三表 md5) + 零落表 + 零挂链 + 零挂起措辞 + 证据分级五级白名单 + 判据/事实分开** ★ |
★**★反向用例 ≥10 条**, 其中 ★**≥3 条专打 G2 (把某个数改成「官方」定性 ⇒ 必须红)★**、★**≥2 条专打 G1 (删掉 source 字段 ⇒ 必须红)★**、★**≥2 条专打 G5 (改 Y 缺口那个数 ⇒ 必须红)★** ★
★**★必须支持 `--selftest` 入口 + 末行逐字 `ALL TESTS PASS` + 真 rc=0** ★
★**★★零挂链 ★★: `grep -c check_fts_vs_generic_courtyard_delta state/gate_check.py` ⇒ **0** ★★**

### ★★③ 交卷页: `HANDOFF/2026-11-24_mech-lead_ISS393_通用库件与厂件对照物差集与判决链重算.md` (★新建★) ★★

★**B1~B6 六段齐全, 六个 `##` 标题必须命中 `state/gate_check.py` 的 `REQUIRED_BLOCKS` 关键词 (★main 本机实读 L47~L54★)**: ★
| 段 | 标题必须含 |
|---|---|
| B1 | `结论` / `结论摘要` / `一句话` |
| B2 | `验收标准自评` / `自评` / `验收标准` |
| B3 | `证据分级` / `证据等级` / `证据` |
| B4 | `接口取值` / `接口声明` / `interface_claims` / `接口请求` |
| B5 | `阻塞` / `卡点` / `未决` / `待办` |
| B6 | `复现` / `复现命令` / `自证` |
★**★不许留「(施工中)」占位符 ★★**

### ★★④ 分片: `state/fragments/mech.yaml` ★★

★**必须走** `python3 state/frag_write.py --agent mech-lead` ★★(★禁止 `open(p,"w")`★) ★
★**≥4 产出物 + ≥6 interface_claims + ≥6 needs_from (★全部 to=main·★不许自签★)** ★

---

## ★★三 · 边界 (★违反就是不合格★) ★★

| # | 边界 |
|---|---|
| ★**1** ★ | ★**零写板**: 板 md5 必须还是 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` |
| ★**2** ★ | ★**零落表**: 网表 / 脚表 / BOM / 原理图真源 一个字节不许动 |
| ★**3** ★ | ★★**零改既有闸** ★★: ★**`MECH/check_debug_seat_3d_fit.py` / `MECH/check_debug_seat_3d_fit.py` 的阈值 / `MECH/check_debug_seat_rework_spec.py` / `MECH/check_fts_seat_body_geometry.py` (★ISS-390 刚交的那道★) 一个字节都不许动** ★★(★它们是已签收件·★本单只登记差集与重算清单, 不代落★)★ |
| ★**4** ★ | ★**零改既有页面正文**: ★**`MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` / `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` / `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` / `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` / `MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` 全都不许改正文** ⇒ ★**只登记 + 只出逐字订正建议, 落不落归 main** ★ |
| ★**5** ★ | ★**零改 `state/gate_check.py`** (★挂链 = main 的机制地界★) |
| ★**6** ★ | ★**零改 `state/issue_log.yaml`** (★不自签台账★) |
| ★**7** ★ | ★**零挂链**: `grep -c check_fts_vs_generic_courtyard_delta state/gate_check.py` ⇒ **0** |
| ★**8** ★ | ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购** ⇒ ★**老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ |
| ★**9** ★ | ★**不代拍**: ★**罩住判据管到铜箔还是管到座体本体 / `OI-12` 过不过严 / `OI-13` 怎么处置 / `OI-14` 的目标值取多少 / 座体真实高 `h` 走三档还是定版 —— 全是 main/boss 的地界, 你只摆代价** ★ |
| ★**10** ★ | ★**不写别人的分片** (★只写 `state/fragments/mech.yaml`★) |
| ★**11** ★ | ★**沙盒只落** `tmp/iss393_sbx/` + `logs/iss393/` ★ |
| ★**12** ★ | ★**一次 write ≤ 3000 字 ⇒ 先 write 骨架, 再 edit 逐块补** (★★连挂两趟都是死在超长 write 上★★) ★ |

---

## ★★四 · 交卷前必跑 (★原样输出贴进交卷页 B6 · 期望值写在后面★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-393_mech_fts_vs_generic_courtyard_delta.md   # rc 必须 0
python3 MECH/check_fts_vs_generic_courtyard_delta.py                    # rc 必须 0 · ★本闸裸跑全绿★
python3 MECH/check_fts_vs_generic_courtyard_delta.py --selftest          # rc 必须 0 · 末行 ALL TESTS PASS
python3 MECH/check_debug_seat_3d_fit.py                                 # rc 必须 0 (★既有闸·本单不许让它变红★)
python3 MECH/check_fts_seat_body_geometry.py                            # rc 必须 0 (★ISS-390 刚交的那道·本单不许让它变红★)
python3 state/merge.py                                                  # rc 必须 0
python3 state/gate_check.py                                             # rc 必须 0 · Q1 18/18
python3 state/issue_check.py                                            # rc=1 ★★既有逾期老账·本单零新增★★
md5sum HW/PCB/demo_mainboard.kicad_pcb                                  # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                         # 必须 2026-11-06 07:07:17.362193413 4940213
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv            # 必须 6aee500e… / 9174309d… / 5b999399…
grep -c "check_fts_vs_generic_courtyard_delta" state/gate_check.py       # 必须 0
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HANDOFF/2026-11-24_mech-lead_ISS393_通用库件与厂件对照物差集与判决链重算.md"   # 必须 0
grep -c "iss393" state/fragments/mech.yaml                              # 必须 >= 1
find tmp/iss393_sbx -type l | wc -l                                     # 必须 0
```

★额外纪律: ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★ · ★**不许外发任何邮件/询价/问询/采购 ⇒ 缺口一律自己网上查 + 标证据等级 + 写降级方案** ★ · ★**交卷前跑 `python3 state/merge.py` (rc=0) && `python3 state/gate_check.py` 并把输出贴进回复** ★

---

## ★★五 · 一句话 (★本单到底在回答什么★) ★★

★**「换厂件之后, MECH 判决链上到底有几个数要重算 / 有几个数一个都不用动 / 有几个数卡在 main 还没拍的路口上」⇒ 以及「把通用库件的数当成厂件的数」这条错误到底扩散到了哪几处 (★尤其已签收闸的源码字符串★)** ★
