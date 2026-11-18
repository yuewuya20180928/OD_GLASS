# ISS-323 · sw-lead · ★★「板只改一次」那一趟的 SW 侧: 7 件必须同批改的活, 做成【逐字可执行清单】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-323
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 11:4x** ★
> ★**性质**: 内部活 · ★**纯分析 / 作业包 / 判据设计类 (SW 侧)** ★ · 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零改网表/脚表/BOM/原理图真源 · 沙盒只写 `tmp/` · 零外发 · 不替老板拍板 · 不自签 issue_log
> ★**上游**: `ISS-318` (SW 侧位号引用可达性闸 · verified) · `ISS-315` (判据链收口 · verified) · `ISS-321` (S1 改名对 SW 判据安全性体检 · **verified 11:3x**) · `ISS-317` (S1 五侧改名可执行清单 · HW 侧同款范本 · verified)

---

## ★0 · 主线口径 (★老板 2026-11-17 00:43: 「接下来的目标是绘制 PCB 图」★)

★**当前主线 = 绘制 PCB 图** ⇒ ★**布线 / 布局类 ISS 现在【可派】** ★
★**但「板只改一次」⇒ 派 PCB 单的纪律 (★老板口径★)**:
1. ★**先派【纯分析 / 作业包】类 (★不动板★)** ★ ⇒ ★**本单就是这一类** ★
2. ★**真动板那一趟必须一次做完** (位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出 · 同一趟 · 背靠背) ⇒ ★**本单不碰板, 只把 SW 侧那一半做成「照着就能干」的清单** ★
3. ★**原理图/网表侧只派【不改网表真源】的活** ⇒ ★**本单零碰网表真源** ★

---

## ★1 · main 11:4x 本机实读的事实 (★你的活从这些数开始, 不许自己重测当基线★)

| # | 事实 (★main 本机实跑★) | 怎么复现 |
|---|---|---|
| ① | ★**ISS-321 已 verified (11:3x)** ⇒ 它交的是【发现 + 改法】, ★**缺的是【像 ISS-317 那样的逐字可执行清单】** ★ | 读 `SW/ONETRIP_SW_RENAME_SAFETY.md` §4 + `HANDOFF/2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md` |
| ② | ★**ISS-321 §4-6 的执行顺序表给的是「7 件必须同批」 (#1~#7) + 1 件可板后补 (#9)** ⇒ ★**这 7 件就是你本单的主体** ★ | 同上 §4-6 |
| ③ | ★**改名宇宙**: 表侧 218 个 ref · **要改 186** (末字符是字母 ⇒ 加 `_1`) · 不动 32 (末字符是数字) ★ | `python3 logs/iss321/iss321_parse_rename_sets.py` |
| ④ | ★**改名后必炸的 3 道闸 (改名特有·S4 红 + S8 绿 对照组已隔离)**: `SW/tools/timing_check.py` (★崩在 L1113·`TypeError`★) · `SW/tools/check_timing_review_adc_sync.py` (★上游 fail-closed ⇒ rc=2★) · `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` ★ | 读 `SW/ONETRIP_SW_RENAME_SAFETY.md` §2/§3 |
| ⑤ | ★**F-1 改法已在沙盒验证**: `timing_check.py` 的 `Netlist` 位号解析层 **25 处定点替换** ⇒ rc 1→0 · SELFTEST 65/85 → **85/85** ★ | `python3 logs/iss321/iss321_verify_fix.py` |
| ⑥ | ★**F-2 改法已在沙盒验证 (最终采用版)**: `check_onepass_sw_sync.py` 的 **SW03/SW04/SW05 三条现状探针** 改成「从网表实读」⇒ 三条转绿 ★★**注意: 只加 `_1` 变体不够 —— 探针【打印出来的标签】也要跟着改**★ ★ | `python3 logs/iss321/iss321_verify_f2.py` |
| ⑦ | ★**F-3 是改数据不是改脚本**: `SW/tools/check_sw_ref_reachability.py` 的 `DESIGNATOR_REGISTRY` 要按改名后盘面重建 ★ | `python3 SW/tools/check_sw_ref_reachability.py --freeze-registry` (★**这是【冻结表重建命令】, 不是本单让你去跑它★——本单只给逐字改法, 不许真跑在真件上★) |
| ⑧ | ★**第 4 件跨域 (不是 SW 的域!)**: `HW/check_netlist_selfconsistency.py` 的 **16 个位号字面量 (116 处)** 属 ★**hw-lead 的域** ★ ⇒ ★**你只准给逐字改法 + 交 need, 不许碰那个文件** ★ | 读 `SW/ONETRIP_SW_RENAME_SAFETY.md` §4-4 |
| ⑨ | ★**SW 侧文档同步量**: **24 份 md / 834 处位号字面量** (类别 ②·不改不红, 但改了才准) ⇒ 不改 ⇒ 漂移闸判 **58 条改名漂移** ★ | `python3 logs/iss321/iss321_scan_sw_refs.py` + `python3 logs/iss321/iss321_make_tsv.py` |
| ⑩ | ★**闸链现状 (main 11:4x 实跑)**: `python3 state/gate_check.py` ⇒ ★**rc=0** · ★**Q1 18/18** · ★**Q7 钉板 md5 闸链 9/9 全绿** ★ ⇒ ★**ISS-321 交卷后 SW 侧那道红已回绿 (本 job 11:2x 实测)** ★ ⇒ ★**你交卷时 rc 必须是 0, 若红 ⇒ 必须逐字归因到某一件, 不许「环境问题」四个字糊过去** ★ | `python3 state/gate_check.py` |
| ⑪ | ★**零写板双证基线**: 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` ⇒ **你的交卷前后必须逐字节相同** ★ | `md5sum HW/PCB/demo_mainboard.kicad_pcb` · `stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb` |
| ⑫ | ★★**踩过的坑 (本单别再踩)★**: ★**「改名方案类文档」写进 `SW/` 会把 ISS-318 的漂移闸带红** (★它判「形状像位号但不是位号」是真隐患★) ⇒ ★**写法约束 = 清单进 `logs/` 不进 `SW/` + 不写死「改名后名」** ⇒ ★**这是 need `iss321_decide_rename_doc_notation` 的内容, 你把它写进清单即可, 不代拍** ★ | `python3 logs/iss321/iss321_doc_gate_check.py` |

---

## ★2 · 本单要交的东西 (★4 件 · 缺一不算交卷★)

### ★① 【主交付物】SW 侧 7 件同批改动的【逐字可执行清单】(★新建文档★)

- ★**本单新建 (★交付物①·落点★)**: ★**`SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md`** ★
- ★**体量**: 参考 HW 侧同款范本 `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` (★959 行 · §0~§6★) ⇒ ★**本单按【7 件】组织, 不是按 834 处组织** ★
- ★**每一件必须给到这 9 列 (★缺一列 = 不合格★)**:
  | 列 | 内容要求 |
  |---|---|
  | `#` | 件号 (★与 ISS-321 §4-6 的 #1~#7 对齐, 一个字不许错位★) |
  | ★**改哪个文件** ★ | 路径 (★**第 4 件是 `HW/check_netlist_selfconsistency.py` ⇒ 必须标「★跨域·不是 SW 的域·只给改法★」★) |
  | ★**改前逐字** ★ | 该处的原文 (★从盘上真件抄, 不许凭印象★) |
  | ★**改后逐字** ★ | 要换成的原文 (★**能直接粘贴★) |
  | ★**行号 / 定位锚点** ★ | 行号 + 稳定的定位串 (★函数名 / 常量名 / 唯一子串★) |
  | ★**验收命令** ★ | 逐字可粘贴 + ★**期望读数** (★例如「rc=0 · SELFTEST 85/85」★) |
  | ★**归属** ★ | ★**SW 域 (你) / 跨域 (交 need 给 hw-lead) / main 域 (交 need)★** ★ |
  | ★**不改的后果** ★ | 引用 ISS-321 的实测读数 (★不许自己编★) |
  | ★**时序** ★ | ★**必须与板那一趟同批 / 可板后补** ★ (★只有 #9 可板后补, 而 #9 不在 7 件里★) |

- ★**第 7 件 (24 份 md / 834 处) 的特殊要求**: ★**不许把 834 处逐条抄进清单** (★那份是机器产物★) ⇒ ★**你要交的是【怎么机器化改】+【改完怎么验】+【哪些是留证不能改】+【改完 58 条漂移会不会归零】** ★ ⇒ ★**清单里给逐字命令 (★`python3 logs/iss321/iss321_make_tsv.py` 产出的 TSV 怎么用★) + 验收命令 (`python3 SW/tools/check_sw_ref_reachability.py` 期望 `DESIGNATOR_DRIFT = 0`)★ ★
- ★**第 5 件 (三道 R6 selftest 夹具) 的特殊要求**: ★**这条不是改名特有的 (S8 对照组同样红)** ⇒ ★**清单里必须写清「它是【合法改板后夹具失配】, 不是【改名炸的】」** ⇒ ★**你只给夹具改法建议 + 代价 + 「不改的后果」, 不代拍 (need `iss321_decide_r6_selftest_fixture_after_reboard`)★ ★
- ★**第 6 件 (`SW/BOARD_ONEPASS_SW_SYNC.md` 的 `SW01_PCB_MD5` 的 `current_state` 重锚)**: ★**归属步 S9** ⇒ ★**清单里标明「板 md5 重锚是 S9 的活, 清单里给重锚的读法与落点」** ★
- ★**占位符扫描必须 0** (★扫 `🔄` / `待填` / `PLACEHOLDER` / `施工中★)

### ★② 交卷页 (★标准验收块 B0~B6 齐全★)

- ★**本单新建 (★交付物②·落点★)**: ★**`HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md`** ★
- ★**B0** 一句话 + 交付物清单 · ★**B1** 结论摘要 (★7 件逐件一句 + 最值钱的那条★) · ★**B2** 验收标准自评 (★逐条 通过/不通过/未验★) · ★**B3** 证据分级 (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) · ★**B4** 接口取值声明 (★别人要照抄的东西逐字给★) · ★**B5** 未决项与卡点 (★need key + 一句话问法 + 不拍的后果★) · ★**B6** 自证复现命令 (★逐条可跑·输出已落盘★)
- ★**占位符扫描 0**

### ★③ 原始输出目录

- ★**落点**: ★**`logs/iss323/`** (★新建★)
- ★**内容**: ① 机器解析出来的 7 件清单 (★TSV/JSON 机读 + 人读两版★) ② 沙盒复现 (★重跑 ISS-321 的沙盒脚本, 证明你的清单里的改法**在沙盒里真的成立**★) ③ 交卷前门禁链输出 ④ 零写板双证
- ★**★沙盒纪律★**: ★**沙盒只写 `tmp/` + `logs/iss323/`★** ⇒ ★**`SW/tools/*.py` 的 md5 一个都不许变 (★它们是受保护资产·闸链会读·改了就是改闸★)★ ★

### ★④ sw 分片

- ★**落点**: ★**`state/fragments/sw.yaml`** · ★**必须走 `python3 state/frag_write.py --agent sw-lead` 原子写** ★(★禁止 `open(p,"w")`★)
- ★**内容**: artifacts (≥1 · 指向 ①②) · needs_from (★**把 ISS-321 交回的 4 条 need 抄进你自己的分片, 按你本单的口径写清「批不批 + 不批的后果」★) · interface_claims (≥1 · 别人要照抄的逐字改法) · status

---

## ★3 · 边界 (★一条都不许越★)

| # | 边界 | 自证方式 |
|---|---|---|
| 1 | ★**零写板** ★ | 板 md5 + mtime 交卷前后逐字节相同 |
| 2 | ★**零落表** ★ | 网表 / 脚表 / BOM / 原理图源 md5 全部未变 |
| 3 | ★**零改闸** ★ | ★**`SW/tools/*.py` 全部 md5 未变** (★**改法只落在沙盒副本与清单里★)★ |
| 4 | ★**零改既有文档正文** ★ | ★**`SW/*.md` 真件 md5 未变** (★第 7 件的 834 处改法只给清单, 不动真件★) |
| 5 | ★**不写别人的分片** ★ | ★**只写 `state/fragments/sw.yaml`★** (★`hw.yaml` / `mech.yaml` / `pm.yaml` 一个字节都不许碰★) |
| 6 | ★**零外发** ★ | ★**不许发任何邮件 / 询价 / 问询 / 采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ |
| 7 | ★**不替老板拍板** ★ | 涉及「能不能改受保护判据脚本 / 夹具怎么改 / 文档写法约束」⇒ ★**只交 need + 建议默认值 + 不拍的后果** ★ |
| 8 | ★**不自签 issue_log** ★ | `state/issue_log.yaml` 一个字节不许动 (★签字是 main 的活★) |

---

## ★4 · 交卷前必跑 (★逐字可粘贴·★输出原样贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 机器解析 (★7 件清单的数据源·不许手抄★)
python3 logs/iss321/iss321_parse_rename_sets.py
python3 logs/iss321/iss321_scan_sw_refs.py
python3 logs/iss321/iss321_make_tsv.py

# ② 沙盒复现 (★证明你清单里的改法真的成立·真闸零改★)
python3 logs/iss321/iss321_sb_make.py
python3 logs/iss321/iss321_sb_make_s4.py
python3 logs/iss321/iss321_sb_make_s8.py
bash    logs/iss321/iss321_sb_run.sh
python3 logs/iss321/iss321_verify_fix.py
python3 logs/iss321/iss321_verify_f2.py

# ③ 门禁链 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/merge.py && python3 state/gate_check.py

# ④ 零写板双证
md5sum HW/PCB/demo_mainboard.kicad_pcb        # 期望 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb  # 期望 2026-11-06 07:07:17.362193413

# ⑤ 占位符 (★两份交付文档都必须 0★)
grep -cE "🔄|待填|PLACEHOLDER|施工中" SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md
grep -cE "🔄|待填|PLACEHOLDER|施工中" HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md

# ⑥ 你自己的交卷文档不许把 ISS-318 漂移闸带红 (★ISS-321 踩过的坑★)
python3 SW/tools/check_sw_ref_reachability.py    # 期望 rc=0 · DRIFT=0
```

---

## ★5 · 交卷判据 (★main 验收签字只看这 6 条★)

1. ★**`SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` 存在 · §0~§6 全填实 · 7 件逐件 9 列齐全 · 占位符 0** ★
2. ★**交卷页 B0~B6 齐全 · 占位符 0** ★
3. ★**`logs/iss323/` 有机器原始输出 (★解析 + 沙盒 + 门禁 + 零写板四类都有★)** ★
4. ★**`state/fragments/sw.yaml` 已写 (走 `frag_write.py`) · `hw.yaml` / `mech.yaml` / `pm.yaml` md5 未变** ★
5. ★**`state/gate_check.py` rc=0 且 Q1 18/18** ★
6. ★**板 md5 + mtime 逐字节不变 · `SW/tools/*.py` 全部 md5 未变** ★

---

## ★6 · 额外纪律 (★派活抬头固定条款·逐条遵守★)

① ★**写分片必须用 `state/frag_write.py` (禁止 `open(p,"w")`)★** ② ★**只写本任务允许的文件, 不碰别人的** ★ ③ ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★ ④ ★**不许外发任何邮件/询价/问询/采购 ⇒ 缺口【自己网上查】+ 标证据等级 + 查不到就写降级方案★** ⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
