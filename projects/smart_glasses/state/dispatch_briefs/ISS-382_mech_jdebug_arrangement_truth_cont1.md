# ISS-382 · cont1 · mech-lead · 把 `J_DEBUG` 排布标签订正页从【闸已写好·页没写】做到【落盘交卷】· 零写板 · 零改已签收件

★**本单 = ISS-382 cont1 (★不是新单 · 不是从零重做·★)** ★
★**本单 = 纯分析 + 新建机器闸(★已写好·本趟只验收与补齐★) + 沙盒预演 · 零写板 · 零落表 · 零改已签收件 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① ★

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 06:44:18 起 · 06:56:16 止 · runtimeMs 716,511 (≈12.0 分钟) · `status=timeout` + `abortedLastRun=true`** ★
★**子会话** `agent:mech-lead:subagent:0fa8bb52-63c9-44f2-ae07-472831cac2f0` / sessionId `166fef77-ac5b-46f1-8eb2-115f121a9b5b` · transcript 497,757 B @06:56 (★不是空壳·★有 tool_use 记录★) ★
★**死因 = 12 分钟花在【读资料 + 造探针 + 写闸】上 ⇒ 真相页 / 交卷页 / 分片【一件都没写】⇒ 墙一到 ⇒ 零交卷** ★

★★**★但上一趟的重活【已经在盘上了】★★ ⇒ ★**本趟【不许重跑】★** ★

| ★**已在盘的产物** ★ | ★**内容** ★ | ★**本趟怎么用** ★ |
|---|---|---|
| ★`MECH/check_jdebug_arrangement_truth.py` (53,040 B @06:51) ★ | ★**新闸本体已写完** (J0~J5) ★ | ★★**它就是你的页的【规格书】★** ⇒ ★**第一件事: 读它 ⇒ 把它要求的字段 / 段落 / 机器块格式逐条抄成页的骨架 ⇒ 填内容 ⇒ 闸立刻就绿** ★ |
| ★`tmp/iss382_sbx/ledger.json` (1,554 B @06:51) ★ | ★**已签收页里全部「几列 × 几行 / 2x2 / 2×2」表述的逐处清单** (★`file` / `line` / `surface` / `cols` / `rows` / `staggered` / `proposed_surface`★) ★ | ★**§2 订正块草稿的【逐处清单】直接用它, 不许重扫** ★ |
| ★`tmp/iss382_sbx/gen_ledger.py` (1,480 B @06:51) ★ | ★**上面那份清单的生成器** ★ | ★只读 · 要复核就重跑它 (★不重扫整页★) ★ |
| ★`tmp/iss382_sbx/probe_claims.py` / `probe_claims2.py` ★ | ★**两个探针** (★claim 行扫描 + 排布实测★) ★ | ★要复核就重跑 · ★**不许重扫整页** ★ |
| ★`logs/iss382/before_check_connector_caliber.log` (1,085 B @06:46) ★ | ★**`MECH/check_connector_clearance_caliber.py` 的【开工前读数】** ★ | ★★**交卷后必须逐字相同 (★`K7` 本来就红 2 条·★是基线不是要修的★)★★ ★ |
| ★`logs/iss382/before_check_jdebug_1p27.log` (1,425 B @06:46) ★ | ★**`MECH/check_jdebug_1p27_clearance.py` 的【开工前读数】** ★ | ★★**交卷后必须逐字相同 (★零漂移·★不许变红★)★★ ★ |
| ★`tmp/iss382_sbx/baseline_fingerprints.txt` (★0 B·★空文件★) ★ | ★**上一趟开了头但没写进去** ★ | ★**你重写一遍填上 (★板 / 三张表 / 已签收两件 / 四个既有闸的 md5★)★** ★ |

★★**⇒ 本趟的定位: 【闸已写好 · 只差真相页 + 交卷页 + 分片】⇒ ★★这是【收尾趟】, 不是【调研趟】★★ ★★
★★**⇒ ★★头号纪律 (★项目硬规矩 L-13★)★★**: ★**你的第一个动作就是把真相页写出来** ⇒ ★**先把 `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` (★新建★) 的骨架落盘, 再回填内容; 再交卷页; 最后写分片** ⇒ ★**每完成一件立刻落盘, 不许攒到最后一起写** ★★

★**★当前闸的真实状态 (★main 本机实跑·你可以直接复现★)★**:
```
$ python3 MECH/check_jdebug_arrangement_truth.py --selftest
  ✗ 正向对照直接 IO 失败: ['文件不在盘: /home/yuewuya/.openclaw/workspace/projects/smart_glasses/MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md']
⇒ ⇒ 【闸本身没坏】⇒ 【只差页】⇒ ⇒ ★★你把页按闸的要求写出来, 闸就会绿★★
```

---

## ★★二 · 本趟的时间预算 (★本项目子会话的真实墙 ★★约 12~16 分钟★) ★★

★**墙 = 12~16 分钟 (★实测: 上一趟 12.0 分钟被掐★)** ⇒ ★**本趟必须按【收尾趟】切** ★
★**★顺序不许改 (★每一步都落盘★)**:
1. ★**第 1 步 (前 3 分钟)**: 读 `MECH/check_jdebug_arrangement_truth.py` ⇒ ★**把闸要求的字段 / 段落 / 机器块格式逐条抄成页的骨架并落盘** (★空壳也要先落·★宁可先落骨架再填★) ★
2. ★**第 2 步**: 填 §1 实测表 + §2 订正块草稿 (★逐处清单直接取 `tmp/iss382_sbx/ledger.json`★) + §3 G5 盲区判据设计 + §4 未决项 + §5 复跑命令 ⇒ ★**落盘** ★
3. ★**第 3 步**: 跑 `python3 MECH/check_jdebug_arrangement_truth.py` ⇒ ★**把闸点名的红逐条修到绿** ⇒ ★**再跑 `--selftest` ⇒ 末行 `ALL TESTS PASS`** ★
4. ★**第 4 步**: 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS382_JDEBUG排针排布标签订正与G5盲区.md` (★新建★) · B1~B6 ⇒ ★**落盘** ★
5. ★**第 5 步**: 分片 `state/fragments/mech.yaml` (★只走 `state/frag_write.py`★) ⇒ ★**落盘** ★
★**★如果时间在第 3 步用完 ⇒ 允许只交 1/2/4/5 并把闸的未完项写进 §4 未决项 ⇒ ★★但不许交【半份闸】(★一个写了一半就报绿的文件·★比没有闸更坏★)★★ ★

---

## ★★三 · 板侧 / 库侧真值 (★main 2026-11-24 06:2x 本机实读 · 你要自己复跑一遍★) ★★

| 项 | 实读值 | 出处 / 复现命令 |
|---|---|---|
| ★官方 SMD 变体排布 ★ | ★`PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left` 与 `_Pin1Right` 两个变体 ⇒ **都是 pads=4 · 列=2 · 行=4** ⇒ **`2x4_staggered`** ★ | ★自己解析 `.kicad_mod` (★两个变体都要测·★不许只测一个★) ★ |
| ★官方 THT 变体排布 ★ | ★`PinHeader_1x04_P1.27mm_Vertical` ⇒ pads=4 · 沿局部 Y 一列 ★ | ★同上 ★ |
| ★闸自己的算法 ★ | ★`MECH/check_jdebug_1p27_clearance.py` L268~L275 自己算出 `"arrangement": "%dx%d%s" % (len(xs), len(ys), ...)` ⇒ ★**它算出来是 `2x4_staggered` (★对的★)** ★ | ★自己复跑那个函数 / 自己写探针★ |
| ★★已签收真相页写的却是 ★★ | ★★`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` L391 机器块 = `"arrangement": "2x2 staggered"`★ · L45 / L203 / L207 / L288 / L471 / L719 正文多处写「2 列 × 2 行交错」★ ⇒ ★★**它自己的 §3 表 (L208) 又写着「4 个焊盘在 Y 向排 4 行 (中心 ±0.635 / ±1.905)」⇒ 同一页自相矛盾**★★ | ★★自己读那 6 处 (★逐处清单已在 `tmp/iss382_sbx/ledger.json`★)★★ |
| ★★闸的盲区 (★真盲区, 不是假设★)★★ | ★★`MECH/check_jdebug_1p27_clearance.py` 的 `G5` (L576~L618) 只判: ① 降级方案几何被独立实测并单列 ② 页面 `arrangement` 字符串里**含** `staggered` / `交错` (L589~L591) ⇒ ★★**它【从不把页面声明的维数】与【自己实测的维数】对比★ ⇒ 页面写 `2x2` 照样绿、写 `9x9` 也照样绿**★★ | ★★自己读 L576~L618 + 自己造反例验证★★ |
| ★页里钉的 `.kicad_mod` md5 锚 ★ | ★`7a5f470c1f70d4b832be258501945385` (THT) / `9d6b0e63e99e6484d2cd3fa7c` (SMD) ⇒ ★**页里的锚与盘上现值一致 ⇒ 标签是从一开始就写错的, 不是库件变了的陈旧锚** ★ | ★`md5sum` 两个 `.kicad_mod` 自己核★ |
| ★板指纹 ★ | md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ⇒ **19 天逐字节未动** | ★`md5sum` + `stat`★ |

★**★这一页到底错在哪 (★你自己先复现, 再决定怎么写订正★)★**: ★**错的是【标签 / 维数】, 不是【几何数字】** —— 页里那套降级方案的铜箔包络 `6.0000 × 4.4600` 是按「X 向 2 列 (中心距 3.00) 且每块 pad 长 3.00 ⇒ X 包络 6.00」+「Y 向 4 行 (中心 ±0.635 / ±1.905) 且 pad 高 0.65 ⇒ Y 包络 4.4600」算出来的 ⇒ ★**数字本身与 `2x4` 相容** ⇒ ★★**所以你要分清两件事: ① 标签维数写错 (2x2 ⇒ 应为 2x4) ② 降级方案的数值结论不因此改变** —— ★**这两件你都要在订正块里说清, 不许把「标签错」写成「结论错」** ★★

---

## ★★四 · 交卷物 (4 件 · ★第 ② 件上一趟已写好·本趟只验收与补齐★) ★★

★★**① ★**新建** `MECH/BOARD_ONEPASS_JDEBUG_ARRANGEMENT_TRUTH.md` ⇒ 一页说清五件事 (★每条给复现命令 + 证据等级★)** ★★
★**★写之前先读 `MECH/check_jdebug_arrangement_truth.py` ⇒ ★★闸要的字段名 / 段落标题 / 机器块格式, 一个字都不许自作主张改★ ⇒ 照它写★★ ★★

| 段 | 内容 | 硬要求 |
|---|---|---|
| §0 | ★**一句话结论**: 错的是标签还是结论 / 两个 SMD 变体实测各是什么 / `G5` 的盲区到底在哪 | ★不许写空话★ |
| §1 | ★**实测表**: 两个 SMD 变体 + 一个 THT 变体 ⇒ pads / 列 / 行 / 序列 / 判定 (★`2x4_staggered` 的完整定义: 列=2 且 行=4 且 沿 Y 的列序左右交替★) | ★证据等级 `[实测]`★ |
| §2 | ★**★订正块 (★给 main 落用的追加块草稿·★你【只起草】, 不许自己落进已签收页★)★**: 逐条给出「已签收页哪一行写的什么 ⇒ 实测是什么 ⇒ 建议改成什么」+ 逐条给出「哪些结论数字【不因此改变】」 | ★**这是本单最核心的一段**★ · ★**逐处清单直接取 `tmp/iss382_sbx/ledger.json` (★已列好 file/line/surface/cols/rows/proposed★)·不许重扫整页★** |
| §3 | ★**`G5` 盲区的机器判据设计**: 闸该怎么改成【维数逐字对比】(★页面声明的 `arrangement` 与闸自己实测的维数必须逐字相等, 不等就红并点名★) + 至少 3 条反向用例 (★把页面维数改成 `2x2` / `2x4` / `9x9` 各一条★) | ★不许只写「应该能防」这种没有判据的句子★ |
| §4 | ★**未决项**: 逐条「要谁回答什么」+「本单给了什么事实」+ 证据等级 ⇒ ★**不代拍**★ | ★不许出现「建议主」这种自封裁决的写法★ |
| §5 | ★**复跑命令**: 每个数都能自己跑出来 | ★ |

★★**② `MECH/check_jdebug_arrangement_truth.py` (★上一趟已写好·★本趟 = 验收 + 按 §三 的读数补齐 · 不许重写·不许削弱判据★)** ★★
- ★J0 板三项指纹未动 (md5 / mtime / size)★ · J1 两个 SMD 变体 + 一个 THT 变体自己实测 · J2 页面机器块的 `arrangement` 与本闸实测维数逐字对比 · J3 页正文全部「几列 × 几行」表述逐处扫 · J4 「标签错」与「结论错」分开判 · J5 证据等级 / 零挂起 / 零挂链 / 判据事实分开
- ★★**★你改这个闸的唯一许可 = 【把闸跑绿】⇒ ★·如果发现闸与已签收页的真实状态不符 (★误报★) ⇒ 【修闸】, 不许【改页的结论】去迎合闸★ ⇒ ★★改闸必须在 §3 里写清「改了哪条判据 + 为什么原来的判据是错的」★★ ★
- ★★**★闸不许挂进 `state/gate_check.py`** (★挂链是 main 的地界·★零挂链★) ★★
- ★★**★闸不许改 `MECH/check_jdebug_1p27_clearance.py` 的 `G5` 本身** ★★ —— ★**已签收件一个字节都不许动** ⇒ ★**你交的是【新页 + 新闸 + 订正块草稿】, 由 main 决定怎么落** ★★ (★先例: ISS-374 cont2 在已签收页上追加后 `MECH/check_connector_clearance_caliber.py` 的 `K7` 立刻红 2 条 ⇒ ★**这正是「不许改已签收件」的代价, 你【不要】再制造一处★) ★

★★**③ ★**新建** `HANDOFF/2026-11-24_mech-lead_ISS382_JDEBUG排针排布标签订正与G5盲区.md` ⇒ B1~B6 六段齐全, 且【六个 `##` 标题必须含 gate_check 要的关键词】(★上一批单踩过这个坑·一次写对★)** ★★
- `## B1 结论摘要` (★含「结论」★) · `## B2 验收标准自评` (★含「验收标准自评 / 自评 / 验收标准」★) · `## B3 证据分级` (★含「证据分级 / 证据等级 / 证据」★) · `## B4 接口取值声明` (★含「接口取值 / 接口声明 / interface_claims」★) · `## B5 未决项与卡点` (★含「阻塞 / 卡点 / 未决 / 待办」★) · `## B6 自证复现命令` (★含「复现 / 复现命令 / 自证」★)
- ★★**gate_check 的判据是「全文标题里出现该关键词即可」⇒ 标题里带上关键词即可, 正文不用改**★★

★★**④ 分片登记**: `state/fragments/mech.yaml` ⇒ ★**只走 `python3 state/frag_write.py --agent mech-lead ...` (★禁止 `open(p,"w")`★)** ⇒ 登记产出物 2 件 + `interface_claims` (★排布判定口径 + 「标签 ≠ 结论」这条口径★) + `needs_from` (★把 §4 的未决项逐条登记成 need·★**to=main**·★不许代 main 拍★)★

---

## ★★五 · 边界自证 (★交卷前每一条都要实跑并把输出贴进回复★) ★★

★**零写板**: 板三项指纹 (md5 / mtime / size) 开工前 / 交卷后逐字相同
★**零落表**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 三个 md5 开工前 / 交卷后逐字相同
★**零改已签收件**: ★**`MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` 与 `MECH/check_jdebug_1p27_clearance.py` 两个 md5 开工前 / 交卷后逐字相同** (★**你只交新页 + 新闸 + 订正块草稿**★) ★
★**零改既有闸**: `MECH/check_connector_clearance_caliber.py` / `MECH/check_juart_1p27_clearance.py` / `MECH/check_onepass_mech_release.py` / `MECH/check_onepass_struct_crosscheck.py` 四个 md5 开工前 / 交卷后逐字相同
★**零改既有页面正文**: `MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md` / `MECH/BOARD_ONEPASS_MECH_SYNC.md` / `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` / `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 四页正文一字不改 (★订正一律进【新页】★)
★**零挂链**: `grep -c check_jdebug_arrangement_truth state/gate_check.py` ⇒ 0
★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**厂商资料一律【自己上网查】+ 标证据等级 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) + 查不到就写降级方案 (★降级方案是必须项★)** ★
★**不代拍**: 订正块【怎么落 / 落在哪一页 / 落在哪一批】⇒ 全部只起草 + 给代价, 由 main 裁
★**不自签 `state/issue_log.yaml`** ★**不写别人的分片** (★`hw.yaml` / `sw.yaml` / `pm.yaml` 一个字都不许写★) ★**沙盒只落 `tmp/iss382_sbx/` + `logs/iss382/`** (★**不许写系统 `/tmp`** ★—— ★它带 userquota·本仓已因它 EDQ 过一轮★)
★**★不许用 `cp -al` 造沙盒副本★** (★项目硬规矩 L-24: 硬链接 + 写操作 = 写穿真件·★静默无报错★) ⇒ ★**要复制就 `cp -a`★**
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

## ★★六 · 要 main 回答什么 (★只登记·不代拍★) ★★

★① ★**订正块落在哪一页 / 哪一批** ⇒ 本单只起草, 不代裁 (★**先例 ISS-374 cont2 追加后 `K7` 立刻红 2 条 ⇒ 落点与时机是有代价的**★) ★
★② ★**`G5` 的维数对比判据怎么落进既有闸** (★本单零改已签收闸·★由 main 裁是「改旧闸」还是「新闸独立挂」★) ★
★③ ★**「标签错」要不要连带改页里引用该标签的结论句** ⇒ ★**本单逐处列出来了, 由 main 裁** ★
★④ ★**新闸挂不挂 `state/gate_check.py`** ⇒ ★**本单零挂链** (★挂链是 main 的地界★) ★
