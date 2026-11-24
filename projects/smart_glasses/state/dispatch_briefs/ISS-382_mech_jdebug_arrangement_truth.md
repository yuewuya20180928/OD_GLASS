# ISS-382 · mech-lead · ★★[★新主线·PCB 线·MECH 侧·纯分析+新建闸·零写板] `J_DEBUG` 已签收真相页的 `2x2` 排布标签与实测定值矛盾 (★实测是 2 列 × 4 行★) + 对应闸 `G5` 只查「有没有写交错」不查维数 (★真实盲区★) ★★

★**本单 = 纯分析 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改已签收件 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① ★

---

## ★★一 · 为什么开这个单 (★main 本机实读 + 实算 · 不抄任何 agent 报告★) ★★

★① `python3 state/advance.py --json` 实跑 (2026-11-24 06:2x) ⇒ ★**`internal: []`** ⇒ 三个总工名下零 open 可派
★② 台账实读 (375 条) ⇒ ★**mech-lead: open 0 / fixing 0** (★`ISS-377` 已于 2026-11-24 02:3x 由 main 签收 `verified`★) · sw-lead: open 0 / fixing 0 · hw-lead: fixing 1 (`ISS-380`·真在飞)
★③ ★**上游 = main 于 2026-11-24 06:0x~06:1x 在 webchat 会话里独立复核出来的实测定论** (★`state/fragments/pm.yaml` 尚未登记成 need ⇒ ★**本单把它转成正式单**) ★
★④ ★**本单不碰板, 只解决一个【已签收件里的错标签】+ 一个【闸的真实盲区】** ⇒ ★**错标签若不修, 「板那一趟」照着它选降级方案 ⇒ 板改第二次 ⇒ 违「板只改一次」** ★

---

## ★★二 · 板侧 / 库侧真值 (★main 2026-11-24 06:2x 本机实读 · 你要自己复跑一遍★) ★★

| 项 | 实读值 | 出处 / 复现命令 |
|---|---|---|
| ★官方 SMD 变体排布 ★ | ★`PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left` 与 `_Pin1Right` 两个变体 ⇒ **都是 pads=4 · 列=2 · 行=4** ⇒ **`2x4_staggered`** ★ | ★自己解析 `.kicad_mod` (★两个变体都要测·★不许只测一个★) ★ |
| ★官方 THT 变体排布 ★ | ★`PinHeader_1x04_P1.27mm_Vertical` ⇒ pads=4 · 沿局部 Y 一列 ★ | ★同上 ★ |
| ★闸自己的算法 ★ | ★`MECH/check_jdebug_1p27_clearance.py` L268~L275 自己算出 `"arrangement": "%dx%d%s" % (len(xs), len(ys), ...)` ⇒ ★**它算出来是 `2x4_staggered` (★对的★)** ★ | ★自己复跑那个函数 / 自己写探针★ |
| ★★已签收真相页写的却是 ★★ | ★★`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` L391 机器块 = `"arrangement": "2x2 staggered"`★ · L45 / L203 / L207 / L288 / L471 / L719 正文多处写「2 列 × 2 行交错」★ ⇒ ★★**它自己的 §3 表 (L208) 又写着「4 个焊盘在 Y 向排 4 行 (中心 ±0.635 / ±1.905)」⇒ 同一页自相矛盾**★★ | ★★自己读那 6 处★★ |
| ★★闸的盲区 (★真盲区, 不是假设★)★★ | ★★`MECH/check_jdebug_1p27_clearance.py` 的 `G5` (L576~L618) 只判: ① 降级方案几何被独立实测并单列 ② 页面 `arrangement` 字符串里**含** `staggered` / `交错` (L589~L591) ⇒ ★★**它【从不把页面声明的维数】与【自己实测的维数】对比★ ⇒ 页面写 `2x2` 照样绿、写 `9x9` 也照样绿**★★ | ★★自己读 L576~L618 + 自己造反例验证★★ |
| ★页里钉的 `.kicad_mod` md5 锚 ★ | ★`7a5f470c1f70d4b832be258501945385` (THT) / `9d6b0e63e99e6484d2cd3fa7c` (SMD) ⇒ ★**页里的锚与盘上现值一致 ⇒ 标签是从一开始就写错的, 不是库件变了的陈旧锚** ★ | ★`md5sum` 两个 `.kicad_mod` 自己核★ |
| ★板指纹 ★ | md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ⇒ **19 天逐字节未动** | ★`md5sum` + `stat`★ |

★**★这一页到底错在哪 (★你自己先复现, 再决定怎么写订正★)★**: ★**错的是【标签 / 维数】, 不是【几何数字】** —— 页里那套降级方案的铜箔包络 `6.0000 × 4.4600` 是按「X 向 2 列 (中心距 3.00) 且每块 pad 长 3.00 ⇒ X 包络 6.00」+「Y 向 4 行 (中心 ±0.635 / ±1.905) 且 pad 高 0.65 ⇒ Y 包络 4.4600」算出来的 ⇒ ★**数字本身与 `2x4` 相容** ⇒ ★★**所以你要分清两件事: ① 标签维数写错 (2x2 ⇒ 应为 2x4) ② 降级方案的数值结论不因此改变** —— ★**这两件你都要在订正块里说清, 不许把「标签错」写成「结论错」** ★★

---

## ★★三 · 交卷物 (4 件) ★★

★★**① ★**新建** `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` ⇒ 一页说清五件事 (★每条给复现命令 + 证据等级★)** ★★

| 段 | 内容 | 硬要求 |
|---|---|---|
| §0 | ★**一句话结论**: 错的是标签还是结论 / 两个 SMD 变体实测各是什么 / `G5` 的盲区到底在哪 | ★不许写空话★ |
| §1 | ★**实测表**: 两个 SMD 变体 + 一个 THT 变体 ⇒ pads / 列 / 行 / 序列 / 判定 (★`2x4_staggered` 的完整定义: 列=2 且 行=4 且 沿 Y 的列序左右交替★) | ★证据等级 `[实测]`★ |
| §2 | ★**★订正块 (★给 main 落用的追加块草稿·★你【只起草】, 不许自己落进已签收页★)★**: 逐条给出「已签收页哪一行写的什么 ⇒ 实测是什么 ⇒ 建议改成什么」+ 逐条给出「哪些结论数字【不因此改变】」 | ★**这是本单最核心的一段**★ |
| §3 | ★**`G5` 盲区的机器判据设计**: 闸该怎么改成【维数逐字对比】(★页面声明的 `arrangement` 与闸自己实测的维数必须逐字相等, 不等就红并点名★) + 至少 3 条反向用例 (★把页面维数改成 `2x2` / `2x4` / `9x9` 各一条★) | ★不许只写「应该能防」这种没有判据的句子★ |
| §4 | ★**未决项**: 逐条「要谁回答什么」+「本单给了什么事实」+ 证据等级 ⇒ ★**不代拍**★ | ★不许出现「建议主」这种自封裁决的写法★ |
| §5 | ★**复跑命令**: 每个数都能自己跑出来 | ★ |

★★**② ★**新建** `MECH/check_jdebug_arrangement_truth.py` ⇒ 闸 J0~J5 (★每条 fail-closed · 每条一条反向用例 · `--selftest` 末行 `ALL TESTS PASS`★)** ★★
- ★J0 板三项指纹未动 (md5 / mtime / size)★
- ★J1 ★**两个 SMD 变体 + 一个 THT 变体的排布自己实测一遍** (★不许把 md5 锚当答案·★要真解析 pad 坐标★)★
- ★J2 ★**页面机器块的 `arrangement` 字符串与本闸实测维数逐字对比** ⇒ 不等 ⇒ 红并点名 (★**这正是旧 `G5` 缺的那一条**★)★
- ★J3 ★**页面正文里所有「几列 × 几行 / 2x2 / 2×2」的表述逐处扫出来** ⇒ 与实测不符的一处都不许漏 (★页里那 6 处 L45/L203/L207/L288/L471/L719★)★
- ★J4 ★**「标签错」与「结论错」必须分开判**: ★**降级方案的铜箔包络 / 开口余量 / 判决结论各值必须独立重算一遍** ⇒ 与页里写的比 ⇒ ★**只准结论值一致, 不准维数标签一致** (★这两条判据不同, 不许合并成一条★)★
- ★J5 ★**证据等级 + 零挂起 + 零挂链 + 判据/事实分开** (★出现无等级的断言 ⇒ 红★)★
- ★★**闸不许挂进 `state/gate_check.py`** (★挂链是 main 的地界 · 你只交脚本 + 路径 + 建议★)★★
- ★★**★闸不许改 `MECH/check_jdebug_1p27_clearance.py` 的 `G5` 本身** ★★ —— ★**已签收件一个字节都不许动** ⇒ ★**你交的是【新闸 + 订正块草稿】, 由 main 决定怎么落** ★★ (★先例: ISS-374 cont2 在已签收页上追加后 `MECH/check_connector_clearance_caliber.py` 的 `K7` 立刻红 2 条 ⇒ ★**这正是「不许改已签收件」的代价, 你【不要】再制造一处★) ★

★★**③ ★**新建** `HANDOFF/2026-11-24_mech-lead_ISS382_JDEBUG排针排布标签订正与G5盲区.md` ⇒ B1~B6 六段齐全, 且【六个 `##` 标题必须含 gate_check 要的关键词】(★上一批单踩过这个坑·一次写对★)** ★★
- `## B1 结论摘要` (★含「结论」★) · `## B2 验收标准自评` (★含「验收标准自评 / 自评 / 验收标准」★) · `## B3 证据分级` (★含「证据分级 / 证据等级 / 证据」★) · `## B4 接口取值声明` (★含「接口取值 / 接口声明 / interface_claims」★) · `## B5 未决项与卡点` (★含「阻塞 / 卡点 / 未决 / 待办」★) · `## B6 自证复现命令` (★含「复现 / 复现命令 / 自证」★)

★★**④ 分片登记**: `state/fragments/mech.yaml` ⇒ ★**只走 `python3 state/frag_write.py --agent mech-lead ...` (★禁止 `open(p,"w")`★)** ⇒ 登记产出物 2 件 + `interface_claims` (★排布判定口径 + 「标签 ≠ 结论」这条口径★) + `needs_from` (★把 §4 的未决项逐条登记成 need·★**to=main**·★不许代 main 拍★)★

---

## ★★四 · 边界自证 (★交卷前每一条都要实跑并把输出贴进回复★) ★★

★**零写板**: 板三项指纹 (md5 / mtime / size) 开工前 / 交卷后逐字相同
★**零落表**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三个 md5 开工前 / 交卷后逐字相同
★**零改已签收件**: ★**`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 与 `MECH/check_jdebug_1p27_clearance.py` 两个 md5 开工前 / 交卷后逐字相同** (★**你只交新页 + 新闸 + 订正块草稿**★) ★
★**零改既有闸**: `MECH/check_connector_clearance_caliber.py` / `MECH/check_juart_1p27_clearance.py` / `MECH/check_onepass_mech_release.py` / `MECH/check_onepass_struct_crosscheck.py` 四个 md5 开工前 / 交卷后逐字相同
★**零改既有页面正文**: `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` / `MECH/BOARD_ONEPASS_MECH_SYNC.md` / `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` / `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 四页正文一字不改 (★订正一律进【新页】★)
★**零挂链**: `grep -c check_jdebug_arrangement_truth state/gate_check.py` ⇒ 0
★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**厂商资料一律【自己上网查】+ 标证据等级 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) + 查不到就写降级方案 (★降级方案是必须项★)** ★
★**不代拍**: 订正块【怎么落 / 落在哪一页 / 落在哪一批】⇒ 全部只起草 + 给代价, 由 main 裁
★**不自签 `state/issue_log.yaml`** ★**不写别人的分片** (★`hw.yaml` / `sw.yaml` / `pm.yaml` 一个字都不许写★) ★**沙盒只落 `tmp/iss382_sbx/` + `logs/iss382/`** (★**不许写系统 `/tmp`** ★—— ★它带 userquota·本仓已因它 EDQ 过一轮★)
★**必跑命令 (★rc 必须全对, 并把输出贴进回复★)**:
```
python3 MECH/check_jdebug_arrangement_truth.py            # rc=0
python3 MECH/check_jdebug_arrangement_truth.py --selftest  # rc=0 末行 ALL TESTS PASS
python3 MECH/check_jdebug_1p27_clearance.py                # rc=0 (★既有闸零漂移·★不许变红★)
python3 MECH/check_connector_clearance_caliber.py         # rc=0 (★★注意: K7 本来就红 2 条(ISS-374 cont2 追加所致)·★你的前后读数必须【逐字相同】·★不许让它多红一条★)
python3 state/merge.py                                    # rc=0
python3 state/gate_check.py                               # rc=0 且 Q1 18/18
python3 state/check_brief_commands.py                      # rc=0
```

---

## ★★五 · 要 main 回答什么 (★只登记·不代拍★) ★★

★① ★**订正块落在哪一页 / 哪一批** ⇒ 本单只起草, 不代裁 (★**先例 ISS-374 cont2 追加后 `K7` 立刻红 2 条 ⇒ 落点与时机是有代价的**★) ★
★② ★**`G5` 的维数对比判据怎么落进既有闸** (★本单零改已签收闸·★由 main 裁是「改旧闸」还是「新闸独立挂」★) ★
★③ ★**「标签错」要不要连带改页里引用该标签的结论句** ⇒ 本单逐处列出来了, 由 main 裁 ★
★④ ★**新闸挂不挂 `state/gate_check.py`** ⇒ ★**本单零挂链** (★挂链是 main 的地界★) ★
