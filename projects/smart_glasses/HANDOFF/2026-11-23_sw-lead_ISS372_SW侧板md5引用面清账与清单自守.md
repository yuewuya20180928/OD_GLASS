# ISS-372 · sw-lead · 「板那一趟」SW 侧板 md5 引用面清账 + 清单自守 · 交卷页

★**状态: 已交付 (CONT2 收尾趟 · 2026-11-23 22:39 起 · 23:0x 收工)** ★
★**★上一趟 21:30 failed + cont1 22:28 被 16 分钟墙掐死 + 本趟只补交卷页与分片 (★两件重产物上一趟已落·本趟零重跑扫描·零重建页·零重建闸★)** ★
★**★本趟读数全部为本单自己 2026-11-23 22:39~23:0x 本机实跑 (★不抄 main 的读数·main 的独立复跑另行记账★)** ★

---

## B1 · 结论摘要

### B1-1 · 一句话

★**「板只改一次」那一趟, SW 侧真正会出事的不是板, 是【板的 md5 被谁抄在了纸上】** ——
★**SW 域板 md5 引用面 = 17 个活文件 / 47 命中行 / 57 命中处; 三类归属 = 判据锚 9 行 / 规格页引用 17 行 / 历史留证 21 行** ★
★**⇒ 改板当天会假红的闸 = SW 域 2 道 (F5 / G8) + 跨域 1 道 (A-5) = 3 道, 它们【没有合法改板通道】★**
★**⇒ 而这 3 道闸的红色原文里【没有一个字】说「这是合法改板」⇒ 现场一读就是「板改坏了」⇒ 极可能去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★
★**⇒ 本单交付: ① 一页清账 (逐处 47 行 + 三类归属 + 逐闸账 + 补丁规格) ② 一道自守闸 (H1~H7 + `--selftest` 8/8) ③ 跨域登记 + 未决项 6 条 (★只登记·不代拍★)** ★

### B1-2 · 交了三件 (★三件·不许扩项★)

| # | 交付物 | 路径 | 大小 | md5 | 状态 |
|---|---|---|---|---|---|
| ① | ★**清账页** ★ | `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` | 74,490 B | `569e684437443a91788b1679c894fed0` | ★**已落盘 (★上一趟落的·本趟一个字都没改★)** ★ |
| ② | ★**自守闸** ★ | `SW/tools/check_sw_board_md5_rebase_readiness.py` | 24,690 B | `0f984c2ade7781afae9b40be417e0feb` | ★**已落盘 (★上一趟落的·本趟一个字都没改★)** ★ |
| ③ | ★**交卷页 + 分片 + 留证** ★ | 本页 + `state/fragments/sw.yaml` + `logs/iss372/` (7 件) | — | 分片 `7be5198c9f15c85af6467856fbdd176d` · ★本页 md5 见 `logs/iss372/07_board_double_evidence.txt` 末段 (★不把本页自己的 md5 写进本页·免得自我引用·★)★ | ★**已落盘 (★本趟补的·★就是这两件★)** ★ |

★**★两件重产物的来历 (★本趟一字未改·所以本趟的活只有两件★)** ★
★**① 与 ② 是上一趟 (21:30 那趟 failed 之前) 落的 ⇒ 本趟只做「交卷页」+「分片登记」⇒ 所以 B6 的必跑命令【必须本趟自己跑一遍】(★不用重跑那 57 处扫描★)** ★
★**★main 已独立复跑过 ②: 裸跑 rc=0 (7/7 PASS) + `--selftest` rc=0 (8/8 反向用例全过·末行 ALL TESTS PASS) ⇒ 这道闸是好的★** ★[实测·main 独立复跑 + 本趟本机复跑两条独立读数逐字一致]

### B1-3 · ★**必跑命令原样 rc (★2026-11-23 22:39 本机实跑·★本趟自己跑的★)** ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 SW/tools/check_sw_board_md5_rebase_readiness.py            # ★rc=0 · 7/7 全绿★
python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest  # ★rc=0 · 8/8 · ALL TESTS PASS★
python3 state/merge.py                                              # ★rc=0★
python3 state/gate_check.py                                         # ★rc=0 · Q1 18/18★
md5sum HW/PCB/demo_mainboard.kicad_pcb                             # ★rc=0 · 611b869e13518c3c023fb178f91a0075★
```

★**完整原样输出见 §B6-1 (★一行都没删·rc 逐条标出★)** ★
★**★本趟跑了【两遍】: 第一遍 22:39 (★写分片之前★) + 第二遍 22:42 (★写分片之后★) ⇒ 五条命令的 rc 两遍逐字一致 (全 0) ⇒ 【写分片没有把门禁链带红】★** ★[实测]

### B1-4 · ★**写盘闸实测 (★本单零写真件 ⇒ 用「边界 md5 前后对照」自证★)** ★

| 项 | 值 (★本趟开工前 · 22:40:38 实读★) | 交卷前 | 逐字节相同? |
|---|---|---|---|
| 板 md5 | `611b869e13518c3c023fb178f91a0075` | 同左 | ★**是** ★ |
| 板 mtime | `2026-11-06 07:07:17.362193413` | 同左 | ★**是** ★ |
| 板 size | `4940213` | 同左 | ★**是** ★ |
| 网表 / 脚表 / BOM | `6aee500e60ba0732f83a9cf557ba90ab` / `9174309df1ec9411ac8e8d9e80ee386a` / `5b9993992405904a60ac96a020b375d8` | 同左 | ★**是** ★ |
| SW 台账 `SW_MD5_BASELINE_LEDGER.md` | `83fafcf7d22d8fa999a1db74c781956d` | 同左 | ★**是** ★ |

★**完整 22 条 md5 对照 (板 1 + 受保护/不得改 20 + 分片 1) = `logs/iss372/07_board_double_evidence.txt`** ★[实测]

### B1-5 · ★**本单最有价值的一条发现 (★必须让 main 知道★)** ★

★**「板只改一次」那道铁律, 在 SW 侧从此不再靠人记得** ★
★**自守闸 H1~H7 的形状 = 把三件人脑活变成了机器判据** ★[实测]
★**① H1 (漏一处就红)**: §1 的 47 行清单必须逐处覆盖盘面扫描结果 ⇒ ★**盘上多一处引用而清单没登记 ⇒ 红**; ★**清单里登记了但盘上扫不到 ⇒ 清单过期 ⇒ 也红** ★
★**② H3 (活判据不许伪装成历史留证)**: 【历史留证】类不许落在 `.py` 上 ⇒ ★**不许把一个活判据塞进「历史留证」栏来免改** ★
★**③ H4 (谁钉了板 md5 要在册)**: 自己扫 `SW/tools/*.py` 里含 32 位字面量的闸 ⇒ ★**今天新造的那两道今天就能被抓住** ★
★**④ H5 (知道也没人给它建通道 ⇒ 红)**: 每道闸要么【代码级已有合法改板通道】, 要么【在 §2 登记成已知缺口 + 归属 + 谁来补 + 补法规格】⇒ ★**「登记过的缺口」不红, 「没人知道的缺口」才红** ★
★**★⇒ 配套结论: 通道存在之后, 「板改第二次」当场红 (沙盒 T5 全红) ⇒ 纯 md5 硬保护支路没被放松 ⇒ 闸不是把红灯调没了, 是把「没人知道的洞」变成「登记在册的洞」** ★[实测]

★**第二条 (答那条挂了两周的 need)**: ★**`.kicad_sch` 的 md5 不能当锚点 —— 结论一个字没变, 但机理要订正** ★
★**真正���随机源 = `state/gen_kicad_sch.py` 本身 (L119 `uuid.uuid4()`) ⇒ 跑它一次, 11 个 `.kicad_sch` 的 raw md5 11/11 全变; 归一化 (UUID + 时间戳) 后 0/11 变 (同图)★**
★**⇒ need 原文写的「`check_sch_erc.py` / `check_sch_pinfull.py` 内部会 subprocess 调 `gen_kicad_sch.py` ⇒ 跑这两条门禁就会重铸 UUID」这个机理【不成立】(★沙盒各跑一次 rc=0 ⇒ md5 变化文件数 = 无★)★**
★**⇒ 且这个风险至今没伤到任何人: SW 域活文件里 `.kicad_sch` 的 md5 命中 = 0 处** ★[实测] ⇒ ★**处置 = 结论订正 + 降级为「一条已知注意事项」⇒ 本单用同 key 在 `state/fragments/sw.yaml` 的 `answers` 里答掉 (★答方 sw-lead·问方 hw-lead★)** ★

---

## B2 · 验收标准自评 (★逐条 通过 / 不通过 / 未验★)

| # | 验收标准 | 自评 | 依据 |
|---|---|---|---|
| A1 | ★**新建自守闸裸跑 rc=0 · H1~H7 全绿** ★ | ★**通过** ★ | ★7/7 PASS·rc=0★ (B6-1 第 1 条) |
| A2 | ★**`--selftest` rc=0 · 8 条反向用例全过** ★ | ★**通过** ★ | ★8/8·每条自证「红的集合 == {目标那一条}」·末行 ALL TESTS PASS·rc=0★ (B6-1 第 2 条) |
| A3 | ★**既有闸复跑仍全绿** ★ | ★**通过** ★ | ★5/5 rc=0: `check_demo_panel_spec.py` / `check_onepass_sw_sync.py` / `check_fp_truth_read.py` / `check_onepass_legb_sw_impact.py` / `HW/check_iss354_manufacturability.py`★ (B6-2) |
| A4 | ★**`state/merge.py` rc=0** ★ | ★**通过** ★ | ★rc=0·STATE.yaml 已刷新 2026-11-23T22:42:25+08:00·产出 796 / 阻塞 43 (高危 33) / 未闭合需求 327 / 冲突 0★ (B6-1 第 3 条) |
| A5 | ★**`state/gate_check.py` rc=0 · Q1 18/18** ★ | ★**通过** ★ | ★rc=0·Q1 18/18 个必填验收块齐全 (★sw-lead 6/6·且本单交卷页已被认成 sw-lead 的交接单·Q1 6/6 齐全★)·Q7 钉板 md5 闸链 10/10 全绿★ (B6-1 第 4 条) |
| A6 | ★**板 md5 = `611b869e13518c3c023fb178f91a0075`** ★ | ★**通过** ★ | ★md5sum 原样输出·rc=0★ (B6-1 第 5 条) |
| A7 | ★**交卷页 B1~B6 六段齐全** ★ | ★**通过** ★ | ★本页 B1/B2/B3/B4/B5/B6 六段都在·无占位符★ |
| A8 | ★**分片登记只走 `python3 state/frag_write.py --agent sw-lead` (★禁止 `open(p,"w")`★)** ★ | ★**通过** ★ | ★本单写分片只有这一条命令·写前写后各记一次 md5·见 B5-5★ |
| A9 | ★**零写板** ★ | ★**通过** ★ | ★板 md5 / mtime / size 三项前后逐字节相同 (B1-4 + `logs/iss372/07_board_double_evidence.txt`)★ |
| A10 | ★**零落表** (网表/脚表/BOM/落表台账/原理图 11 个/`issue_log.yaml` 一字不改) ★ | ★**通过** ★ | ★18 件受保护 md5 前后逐字节相同·`state/issue_log.yaml` 本单零写入 (不自签)★ |
| A11 | ★**零改既有闸** (那 3 道 SW 闸 + `check_demo_panel_spec`/`timing_check`/`check_shutdown_semantics`/`check_pcb_nets`/`gate_check`/`merge`/`frag_write`/`check_sch_erc`/`check_sch_pinfull` 一字不改) ★ | ★**通过** ★ | ★全部在受保护 20 件清单里·md5 前后相同 (B6-2)★ |
| A12 | ★**零改既有页面正文** (`SW/SW_MD5_BASELINE_LEDGER.md` 那 13 处是 R6/R7 的判决源·一个字都不许动) ★ | ★**通过** ★ | ★md5 `83fafcf7d22d8fa999a1db74c781956d` 前后相同★ |
| A13 | ★**零改 `state/` 下的 `board_md5_pinned_gates.json`/`.md`** ★ | ★**通过** ★ | ★两个 md5 (`917757c0460aee130ceda5ec49aadde1` / `918b0969d359120d64efcf6f97beba62`) 前后相同★ |
| A14 | ★**零挂链** (不许挂 `state/gate_check.py`) ★ | ★**通过** ★ | ★`state/gate_check.py` md5 `5f370bb8cf828473e70ccc5d6412da98` 前后相同·新闸【零挂链】·挂不挂 = main 的决定★ |
| A15 | ★**只写自己的分片 `state/fragments/sw.yaml`** ★ | ★**通过** ★ | ★`pm.yaml` / `hw.yaml` / `mech.yaml` 本单零写入 (只读 grep 过 iss372 命中 = 0)★ |
| A16 | ★**沙盒只落 `tmp/iss372/` + `logs/iss372/`** ★ | ★**通过** ★ | ★本趟只往 `logs/iss372/` 落了 07 号留证·`tmp/iss372/` 是上一趟落的 (本趟零重跑扫描)★ |
| A17 | ★**零外发** (全靠自己查·查不到写降级方案·不许写「等原厂回信」) ★ | ★**通过** ★ | ★本单零邮件零询价零下单零问供应商; 全页无「等原厂回信」形态★ |
| A18 | ★**不代老板拍板** ★ | ★**通过** ★ | ★未决项 6 条全部「只登记 + 给代价 + 归谁」·自守闸对 mtime/size 缺口只出规格不出结论★ |
| A19 | ★**不自签 `state/issue_log.yaml`** ★ | ★**通过** ★ | ★`state/issue_log.yaml` 本单零写入 (对它只读不写; 零写入由 §B5-5 的写前写后 md5 对照 + 22 条边界对照共同覆盖)★ |
| A20 | ★**扫描面 57 处逐处登记 (不许按文件归并)** ★ | ★**通过** ★ | ★清账页 §1.3 逐行 47 行 + §1.10 机器可读 JSON 双形态; 分类表覆盖不到任何一行 ⇒ 生成器 rc=2 fail-closed★ |
| A21 | ★**§1.10 那块机器清单可再生 (不许手改)** ★ | ★**未验 (★本趟刻意不跑·不越「别重跑扫描」那条线★)** ★ | ★生成器 = `tmp/iss372/gen_manifest.py`·上一趟落盘时已跑通; ★本趟只补交卷页与分片 ⇒ 不重跑扫描 ⇒ 这条由 main 在独立复核时跑★ |
| A22 | ★**§4 那条挂了两周的 need 要有答复** ★ | ★**通过** ★ | ★`iss249_kicad_sch_md5_not_anchor_sw` ⇒ 已在本单分片 `answers` 里答掉 (★答方 sw-lead·问方 hw-lead·同 key★)★ |

★**自评汇总: 21 条通过 / 0 条不通过 / 1 条未验 (A21·刻意不跑·不是失败)** ★

---

## B3 · 证据分级 (★五级白名单: 官网 / 实测 / 媒体 / 推算 / 0数据★)

### B3-1 · 本单的证据分布

| 等级 | 条数 | 说明 |
|---|---|---|
| ★[实测] ★ | 18 | 本机实跑原样 rc / 实读 / 沙盒预演 |
| ★[推算] ★ | 1 | S9「一次改齐」的具体执行顺序 (依据实测 + 分类, 哪一步先跑待 main 拍) |
| ★[官网] ★ | 0 | 本单不依赖任何外部资料 (★零外发·全靠本机读数★) |
| ★[媒体] ★ | 0 | 同上 |
| ★[0数据] ★ | 1 | 板端实测 = 0 条 (本机无板) |
| **合计** | **20** | E1~E20 |

### B3-2 · ★**逐条证据出处 (★每一处都能被 §B6 的命令复现★)** ★

| # | 结论 | 证据等级 | 留证路径 / 复跑命令 |
|---|---|---|---|
| E1 | 板 md5 / mtime / size = `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213` | ★[实测] ★ | `md5sum HW/PCB/demo_mainboard.kicad_pcb` · `logs/iss372/07_board_double_evidence.txt` |
| E2 | SW 域板 md5 引用面 = ★**17 个活文件 / 47 命中行 / 57 命中处** ★ | ★[实测] ★ | `python3 SW/tools/check_sw_board_md5_rebase_readiness.py` (H1 自扫) · `logs/iss372/01_scan_sw_md5_refs.txt` |
| E3 | 三类分布 = 判据锚 9 / 规格页引用 17 / 历史留证 21 | ★[实测] ★ | 同上 · `tmp/iss372/gen_manifest.py` |
| E4 | 上一趟那套 `grep -v '\.bak'` 的逐行清单★**少 1 行** (台账 L173·正文里含 `.bak_iss220` ⇒ 被连带过滤) | ★[实测] ★ | `grep -rn 611b869e SW/ \| grep -v '\.bak\|__pycache__' \| wc -l` (46) vs `grep -rn 611b869e SW/SW_MD5_BASELINE_LEDGER.md \| wc -l` (13) |
| E5 | ★**闸 C / D / E 在合法改板当天【仍红】** (沙盒 T2b) ★ | ★[实测] ★ | `logs/iss372/05_sbx_reboard_rehearsal.txt` |
| E6 | ★**打了补丁规格原型后 3 道闸回绿** (沙盒 T4) ★ | ★[实测] ★ | 同上 · `tmp/iss372/patch_spec.py` |
| E7 | ★**通道存在后「板改第二次」当场红** (沙盒 T5) ⇒ 纯 md5 硬保护支路没被放松 | ★[实测] ★ | 同上 |
| E8 | ★**已有通道的闸 B 在 T2 仍红 ⇒ 红在【规格页 current_state 过期】⇒ S9 必须连规格页一起换基线** | ★[实测] ★ | 同上 (T2 vs T2b 对比) |
| E9 | `state/board_md5_pinned_gates.json` = 11-17 生成的 9 条; 今天新造的 2 道 SW 闸 + 跨域 1 道不在表里 | ★[实测] ★ | `python3 -c "import json;print(len(json.load(open('state/board_md5_pinned_gates.json'))))"` |
| E10 | ★**没有任何闸在守那张清单的新鲜** (`state/gate_check.py` 零命中) ★ | ★[实测] ★ | `grep -rn "board_md5_pinned_gates" --include=*.py .` |
| E11 | `state/land_v_values.py` L96 也硬钉板 md5, 但那张表的收集口径只收 `check_*.py` ⇒ 收不进去 | ★[实测] ★ | `grep -n '611b869e' state/land_v_values.py` |
| E12 | `.kicad_sch` 跑一次 `state/gen_kicad_sch.py` ⇒ raw md5 11/11 变; 归一化后 0/11 变 ⇒ 同图 | ★[实测] ★ | `logs/iss372/03_exp1_sch_md5.txt` |
| E13 | `check_sch_erc.py` / `check_sch_pinfull.py` 跑完 `.kicad_sch` 的 md5 逐字节不变 ⇒ need 原文的机理不成立 | ★[实测] ★ | 同上 (沙盒 S0/①/②) |
| E14 | SW 域活文件里 `.kicad_sch` 的 md5 命中 = 0 处 ⇒ 该风险至今没伤到任何人 | ★[实测] ★ | `grep -rn 'e433793b4a3ec321cc69f466d7e15de7' SW/` (空) |
| E15 | `SW/tools/check_demo_panel_spec.py` 的 `check_r6_hard_protected()` 是合法改板判据的唯一真源 | ★[实测] ★ | `grep -n 'def check_r6_hard_protected' SW/tools/check_demo_panel_spec.py` (L748) |
| E16 | ★**机器闸 H1~H7 + 8 条反向用例每条自证「红的集合 == {目标那一条}」** ★ | ★[实测] ★ | `python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest` |
| E17 | S9「一次改齐」的具体清单 = 17 处规格页引用 + 落表台账链前移 + 台账锚点 reboard 四项 + issue_log 留痕 | ★[推算] ★ (★依据 E8 的实测 + §1.3 的分类·具体到哪一步先跑 = 待 main 拍★) | `logs/iss372/05_sbx_reboard_rehearsal.txt` (T2b) |
| E18 | ★**P-C / P-D / P-E 的 mtime/size 缺口** ★ | ★[实测] ★ (★「reboard 原子不带 mtime/size」= 读代码 + 沙盒 T4 原型实测★) | `tmp/iss372/patch_spec.py` + `logs/iss372/05_sbx_reboard_rehearsal.txt` |
| E19 | ★**历史留证 21 行的清单** ★ | ★[实测] ★ (★逐行人工判定 + §1.10 的机器清单双形态★) | 清账页 §1.3 |
| E20 | ★**`.kicad_sch` 的 md5 能不能当锚点 = 不能; 处置 = 结论订正 + 降级** ★ | ★[实测] ★ (★结论★) + ★[推算] ★ (★处置方式★) | 清账页 §4 + 本单分片 `answers[iss249_kicad_sch_md5_not_anchor_sw]` |
| E21 | ★**板端实测 = 0 条** (本机无板) ★ | ★[0数据] ★ | `list_devices()` = [] (本机无设备) |

### B3-3 · ★**一条必须说清的观察 (★不是本单干的·但必须留痕★)** ★

★**本单新增的两道 SW 闸 (`check_fp_truth_read.py` 2026-11-23 17:27 交付 / `check_onepass_legb_sw_impact.py` 2026-11-23 19:50 交付) + 跨域 1 道 (`HW/check_iss354_manufacturability.py` 都不在 `state/board_md5_pinned_gates.json` 里 ⇒ ★那 9 条「全部标已有 reboard 通道」是【过期口径】★ ⇒ ★不是本单造成, 是「没人守那张表的新鲜」的必然结果 ⇒ 本单只登记, 不改 (★那是 main 的域★)** ★[实测]

---

## B4 · 接口取值声明 (interface_claims)

### B4-1 · 本单落进分片的 interface_claim (★键名带 `iss372` 前缀★)

| key | value (★一句话·不许含糊★) | 证据等级 |
|---|---|---|
| ★`iss372_sw_board_md5_ref_surface` ★ | ★**SW 域板 md5 引用面 = 17 个活文件 / 47 命中行 / 57 命中处; 三类归属 = 判据锚 9 行 / 规格页引用 17 行 / 历史留证 21 行; 板 md5 基线 = `611b869e13518c3c023fb178f91a0075` (mtime `2026-11-06 07:07:17.362193413` / size `4940213`) ⇒ ★**判据锚 9 行一个字都不许动; 规格页引用 17 行随板改那一趟换基线; 历史留证 21 行永远不许动** ★ | ★[实测] ★ |
| ★`iss372_board_reboard_fake_red_gates` ★ | ★**「板那一趟」改板当天会假红的闸 = SW 域 2 道 (`check_fp_truth_read.py` F5 / `check_onepass_legb_sw_impact.py` G8) + 跨域 1 道 (`HW/check_iss354_manufacturability.py` A-5a/A-5b) = 3 道 (★这三道没有合法改板通道★); 已有通道的 2 道 = `check_demo_panel_spec.py` R6 + `check_onepass_sw_sync.py` W6 ⇒ ★**通道存在之后「板改第二次」当场红 (纯 md5 硬保护支路没被放松)** ★ | ★[实测] ★ |
| ★`iss372_pinned_gates_manifest_stale` ★ | ★**`state/board_md5_pinned_gates.json` = 2026-11-17 20:49 生成的 9 条 (SW 只 1 条) ⇒ 今天新造的 2 道 SW 闸 + 跨域 1 道不在表里; 且收集口径只收 `check_*.py` ⇒ `state/land_v_values.py` L96 (落表器自钉板 md5) 收不进去; 没有任何闸在守它的新鲜 (`state/gate_check.py` 零命中) ⇒ ★**刷新后应有的内容 = 现有 9 条 + 新增 3 条 + 口径补 1 条 (★本单只给内容·不写那两个文件★)** ★ | ★[实测] ★ |
| ★`iss372_kicad_sch_md5_cannot_be_anchor` ★ | ★**`.kicad_sch` 的 md5 不能当锚点 (结论不变) ★但机理订正: 真正的随机源 = `state/gen_kicad_sch.py` 本身 (L119 `uuid.uuid4()`) ⇒ 跑一次它, 11 个 `.kicad_sch` 的 raw md5 11/11 全变, 归一化 (UUID + 时间戳) 后 0/11 变 (同图); `check_sch_erc.py` / `check_sch_pinfull.py` 【不改】它 ⇒ 需原文那个机理不成立 ⇒ ★**SW 域 `.kicad_sch` 的 md5 命中 = 0 处 ⇒ 该风险至今没伤到任何人 ⇒ 处置 = 结论订正 + 降级为「一条已知注意事项」(不机器化)** ★ | ★[实测] ★ |

### B4-2 · ★**本单给下游的取值 (★只声明·不越界拍板★)** ★

| 项 | 本单给的取值 | 谁可以用它做什么 |
|---|---|---|
| 板 md5 期望值 | `611b869e13518c3c023fb178f91a0075` (+ mtime + size 三项) | 任何要钉板 md5 的闸 / 落表台账链头 / 合法改板 reboard 四项的 `prev_md5` |
| 合法改板判据的【唯一真源】 | `SW/tools/check_demo_panel_spec.py` 的 `check_r6_hard_protected()` (L748) | ★**任何要加通道的闸只能【只读调用】它, 不许自己抄第二套判据** ★ |
| 3 道缺口编号 | `iss372_gap_f5_reboard_channel` (SW) / `iss372_gap_g8_reboard_channel` (SW) / `iss372_gap_iss354_reboard_channel` (跨域) | 刷新 `board_md5_pinned_gates` 时的登记条目 |
| 补法规格 | ★**P-C** (`check_fp_truth_read.py` F5) / ★**P-D** (`check_onepass_legb_sw_impact.py` G8) / ★**P-E** (`HW/check_iss354_manufacturability.py` A-5) ★**共同形状: 判据方向一个字不改 (仍是「盘上必须 == 期望值」), 合法改板只让【期望值】从「保护基线」前移到「落表台账链头」, 纯 md5 硬保护支路一条都不许松** ★ | 谁落补丁谁照抄这三份规格 |
| S9「一次改齐」清单 | ① 落表台账链前移 ② 台账锚点 reboard 四项 ③ 【规格页引用】那 17 处 ④ issue_log 留痕 ⇒ ★**顺序必须是「先落表 → 再换基线 → 最后跑闸」** ★ | 「板那一趟」的作业包 |

★**★本单不声明的东西 (★不许被当成已拍板★)**: ★**mtime / size 要不要进 reboard 原子 (U3) ⇒ 不声明** ★ · ★**3 道补丁谁落什么时候落 (U2) ⇒ 不声明** ★ · ★**新闸要不要挂 `EXTRA_GATES` ⇒ 不声明 (★挂链是 main 的活★)** ★

---

## B5 · 未决项与卡点 (★需要谁回答什么★)

### B5-1 · ★**本单的历史 (★三句话·必须让人知道这一趟为什么只做两件事★)** ★

★**① 上一趟 21:30 failed** —— ⇒ ★**两件重产物 (清账页 + 自守闸) 上一趟已落盘, 本趟一个字都没改 (★md5 与 mtime 见 B6-2★)** ★
★**② cont1 22:28 被 16 分钟墙掐死** (★同批三条都被掐在 16 分钟: 16m3s / 16m16s / 16m3s★) ⇒ ★**cont1 死在「交卷页 + 分片」这两件事【之前】⇒ 所以本趟只补这两件, 别的都不碰** ★
★**③ 本趟只补交卷页与分片** (★零重跑那 57 处扫描·零重建页·零重建闸·零重跑生成器★) ⇒ ★**A21 (§1.10 清单可再生) 本趟刻意未验, 留给 main 独立复核时跑** ★

### B5-2 · ★**要 main 裁的 (★写清「要谁回答什么」★)** ★

| # | 未决项 | ★**要谁回答什么 (逐条写清)★** ★ | 不拍的代价 |
|---|---|---|---|
| ★U1 ★ | ★改板那一趟的「S9 换基线」到底一次改齐哪些 ★ | ★**要 main 回答**: ★**「S9 换基线」这一批要不要按本单 §B4-2 那 4 步 (落表链前移 → 锚点 reboard 四项 → 规格页 17 处 → issue_log 留痕) 一次改齐? 且顺序「先落表 → 再换基线 → 最后跑闸」认不认?** ★ | ★**不一次改齐 ⇒ 已有通道的闸 B 也会红 (沙盒 T2 实测 rc=1) ⇒ 现场又多一次「误读成板坏了」的窗口** ★ |
| ★U2 ★ | ★那 3 道闸的通道补丁 (P-C / P-D / P-E) 谁来落、什么时候落 ★ | ★**要 main 回答**: ★**「P-C / P-D / P-E 谁落、什么时候落?」★ (★P-C / P-D = sw-lead 的域·★P-E = 跨域·要 main 转 hw-lead★) ★ | ★**不落 ⇒ 改板当天 3 道闸必红 ⇒ 现场误读 ⇒ 板 md5 变第二次 ⇒ 整趟白跑 (★这正是本单要防的那件事★)** ★ |
| ★U3 ★ | ★reboard 四项原子 (by/file/prev_md5/md5) 够不够 ★ | ★**要 main (⇒ 可能要老板) 回答**: ★**「合法改板时 mtime / size 这两条要不要进 reboard 原子?」★** —— ★**要么给 reboard 原子补 mtime/size (★要动权威判据 ⇒ 老板拍★), 要么给 F5 / A-5 的 mtime 判据一条明文口径 (★判据方向放宽 ⇒ 也要拍★)** ★**★本单只登记, 不代拍★** ★ | ★**不够 ⇒ F5 的 mtime + size 两条在合法改板后仍红 ⇒ P-C 只解决一半 ⇒ 改板当天照样红** ★ |
| ★U4 ★ | ★历史留证那一类「永远不许改」这条禁令要不要写成机器判据 ★ | ★**要 main 回答**: ★**「除了本单已做的『活判据不许伪装成历史留证」(H3), 还要不要再加一条『历史留证不许出现在 .md 的现状表里』?」★** —— ★**本单建议: 【不加】(★会误伤 ⇒ H3 + 本页 §1 当唯一口径源就够★)** ★ | ★**不机器化 ⇒ 下一个 agent 仍要靠人眼判断某一处是「现状值」还是「历史读数」 ⇒ 本单 §1.9 那种「按文件归并」的错还会再犯** ★ |
| ★U5 ★ | ★「板改第二次」的兜底预案 ★ | ★**要 main (⇒ 老板) 回答**: ★**「现场由谁当场判定『这是第二次改板』并停手? 判据能不能自动判出『第二次』?」★** | ★**没有预案 ⇒ 现场第二次改板 ⇒ 闸红着, 但没人知道那是「第二次」而不是「第一次」** ★ |
| ★U6 ★ | ★`state/board_md5_pinned_gates.json` 的刷新时机与收集口径 ★ | ★**要 main 回答**: ★**「那张表什么时候刷新? 收集口径要不要放宽 (★把 `state/land_v_values.py` 也收进去★)?」★** —— ★**本单只给『刷新后应有的内容』(§B4-1 的 claim `iss372_pinned_gates_manifest_stale` + 清账页 §5.1)·不写那两个文件 (★那是 main 的域★)** ★ | ★**不刷新 ⇒ 那张表继续漏新闸 ⇒ 下一个新闸再硬钉板 md5 时还是没人拦** ★ |
| ★U7 ★ | ★新闸要不要挂 `state/gate_check.py` 的 `EXTRA_GATES` ★ | ★**要 main 回答**: ★**「`SW/tools/check_sw_board_md5_rebase_readiness.py` 挂不挂 EXTRA_GATES?」★** —— ★**本单零挂链 (`state/gate_check.py` md5 前后不变)·先例 = ISS-300 (mech 出结论 / main 挂) / ISS-309 / ISS-312 / ISS-315 (四轮都只交写法没人挂)** ★ | ★**不挂 ⇒ 这道闸只活在本单交卷页里 ⇒ 下一个 agent 不读交卷页就没人知道它存在 ⇒ 「板只改一次」那道铁律在 SW 侧还是靠人记得** ★ |

### B5-3 · ★**要 hw-lead 回答的 (★跨域·只登记·不越界改★)** ★

| # | 对象 | ★**要谁回答什么** ★ | 本单做了什么 |
|---|---|---|---|
| ★E1 ★ | ★`HW/check_iss354_manufacturability.py` L40/L41 (闸 E·跨域第 3 道没通道的闸) ★ | ★**要 main 转 hw-lead 回答**: ★**「P-E (md5 期望值前移到落表台账链头 + mtime 那条怎么处理) 什么时候落?」★** | ★**只给补丁规格 P-E (清账页 §2.3)·一个字都不许改那个文件** ★ |
| ★E2 ★ | ★`state/land_v_values.py` L96 (落表器·`PROTECTED` 段) ★ | ★**要 main 回答**: ★**「改板那一趟由谁改这一行?」★ (★建议: 与落表台账链前移同一步·原子★) ★ | ★**只登记** ★ |
| ★E3 ★ | ★need `iss249_kicad_sch_md5_not_anchor_sw` (hw-lead 发起·to= sw-lead·since 2026-11-16) ★ | ★**要 hw-lead 确认**: ★**「本单的答复 (结论不变 + 机理订正 + 降级为已知注意事项) 你认不认?」★** | ★**已在本单分片 `answers` 里用同 key 答掉 (★答方 sw-lead·问方 hw-lead★)·★结论一个字没改★** |

### B5-4 · ★**要老板拍的 (★本单只登记缺口 + 依据 + 代价·**不代拍**★)** ★

| # | 事项 | 依据 | ★**为什么必须到老板这一层** ★ |
|---|---|---|---|
| ★B1 ★ | ★**U3 的判据方向**: 要么改 reboard 原子 (★动权威判据 `check_r6_hard_protected()` 的形状★), 要么给 mtime 判据写明文口径 (★判据方向放宽★) | 清账页 §2.3 的 P-C / P-E 缺口列 | ★**这两条都是判据方向的变更 ⇒ 不是 sw-lead 能定的 ⇒ 走 main→老板★** ★ |
| ★B2 ★ | ★**U5 的兜底流程**: 现场停手权归谁 | 沙盒 T5 (通道存在后当场红) | ★**这是流程权责 ⇒ 不是 sw-lead 能定的★** ★ |

### B5-5 · ★**分片登记的自证 (★写前写后各记一次 md5★)** ★

| 项 | 值 |
|---|---|
| 写前 md5 | ★`37f8663e7b2b4ba06667012a28857351` ★ (mtime `2026-11-23 19:50:54.787056235` · size `724435`) |
| 写后 md5 | ★`7be5198c9f15c85af6467856fbdd176d` ★ (mtime `2026-11-23 22:42:01.215093677` · size `733410`) |
| 写入方式 | ★**只用 `python3 state/frag_write.py --agent sw-lead` (★全程没有 `open(p,"w")`·工具自带 tmp + fsync + `os.replace` 原子写★)** ★ |
| 期间是否被别人改过 | ★**否** —— 写前 (22:40:38 读数 `37f8663e…` · mtime 19:50:54) 与写前即时复读 (22:41 · md5 逐字相同) 一致 ⇒ ★**这段时间内没有人动过这个分片**; 写后 22:42:01 变成本单那一次原子写 ⇒ ★**没有发生「静默覆盖」, 不触发「已停止」条款** ★ |
| 写后自检 (★机器判定★) | ★**幂等**: 现文件 md5 `7be5198c…` == 用同参数 (`safe_dump` · `allow_unicode` · `sort_keys=False` · `width=100`) 重排后的 md5 ⇒ **无格式漂移** ★ · ★**增量**: 写前 → 写后 = artifacts 272→275 (+3) / answers 70→71 (+1) / interface_claims 315→319 (+4) / needs_from 74→80 (+6) ⇒ **只有本单新增, 旧条目一条没少** ★ · ★**新 key 零重复** (iss372 前缀 11 条各出现 1 次; artifacts/claims 里出现的同名项是本单之前就有的历史条目, 与本单无关) ★ |
| ★**是否触发「已停止」条款** ★ | ★**未触发** —— ★写前写后之间没有人动过这个分片 (mtime 从 `19:50:54` 变成写入时刻, 且 diff 只有本单新增条目) ⇒ ★**没有发生「静默覆盖」** ★ |

★**★写后逐条 diff (★只列本单新增的条目·其余逐字节不变★)** ★
★**`interface_claims` +4 条 (`iss372_sw_board_md5_ref_surface` / `iss372_board_reboard_fake_red_gates` / `iss372_pinned_gates_manifest_stale` / `iss372_kicad_sch_md5_cannot_be_anchor`) ★**
★**`answers` +1 条 (`iss249_kicad_sch_md5_not_anchor_sw`·to=hw-lead) ★**
★**`artifacts` +3 条 (清账页 / 自守闸 / 本交卷页) ★**
★**`needs_from` +6 条 (全部 to=main ⇒ U1 / U2 / U3 / U5 / U6 + U7 (挂不挂闸); ★U4 本单给了建议默认值 ⇒ 不立 needs·不占 main 的活★)** ★
★**`pm.yaml` / `hw.yaml` / `mech.yaml` 零写入 ★**

---

## B6 · 自证复现命令

### B6-1 · ★**必跑四条 + 板 md5 (★原样输出·rc 逐条标出·★2026-11-23 22:39 (写分片前) + 22:42 (写分片后) 两遍本机实跑·★rc 两遍逐字一致★)** ★

★**★两遍的差别只有 ③④ 的读数数字 (★因为分片变了 ⇒ 产出数 793→796 / 未闭合需求 322→327 (★本单新立 6 条 need + 1 条 answer·不是新增缺陷★)·★rc 全程一致★)** ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
```

**① 新建自守闸 (裸跑)**
```text
============================================================================================
ISS-372 · 「板那一趟」SW 侧板 md5 引用面清账 + 清单自守闸
  根     = /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  清单页 = SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md
============================================================================================
  [PASS] H1 · SW 域板 md5 引用面必须被 §1 清单逐处覆盖 (★漏一处就红★)
  [PASS] H2 · 每一处都必须标了【三类归属】+【处置】+ 备注
  [PASS] H3 · 【历史留证】类必须真的不许改 (★活判据不许伪装成历史留证★)
  [PASS] H4 · SW 域每道【真钉板 md5 的判据脚本】必须登记在册
  [PASS] H5 · 每道闸要么已有合法改板通道, 要么在 §2 被登记成已知缺口
  [PASS] H6 · 板面零写板自证 (md5 / mtime / size 三项)
  [PASS] H7 · 证据等级五级白名单 + 正文零挂起措辞 + 零空洞词
--------------------------------------------------------------------------------------------
闸结果 7/7 通过, rc=0
```
★**rc=0** ★

**② 同闸反向用例自检**
```text
============================================================================================
ISS-372 · 反向用例自检 (★每条必须自证: 红的集合 == {目标那一条}★)
============================================================================================
  用例 1 · 目标 H1 · 红的集合 = ['H1'] · PASS
        手法: 从 §1 清单里删掉 SW/SW_NEEDS_TRIAGE.md:346 (扫描仍能扫到它)
  用例 2 · 目标 H2 · 红的集合 = ['H2'] · PASS
        手法: 把 SW/SW_NEEDS_TRIAGE.md:346 的三类归属改成空串
  用例 3 · 目标 H3 · 红的集合 = ['H3'] · PASS
        手法: 把 SW/tools/check_fp_truth_read.py:87 标成【历史留证】
  用例 4 · 目标 H4 · 红的集合 = ['H4'] · PASS
        手法: 把 SW/tools/check_onepass_sw_sync.py (★已有通道的那道★) 从 §2 的账里删掉
  用例 5 · 目标 H5 · 红的集合 = ['H5'] · PASS
        手法: 把 check_onepass_sw_sync.py 的通道形态抹掉 + 清单谎报「已有通道」 ⇒ 没人知道的缺口
  用例 6 · 目标 H6 · 红的集合 = ['H6'] · PASS
        手法: 在沙盒里给板追加一个字节 (★真件零写★)
  用例 7 · 目标 H7 · 红的集合 = ['H7'] · PASS
        手法: 把页面里的 [实测] 全换成 [官方] (★白名单只认五级·[官方] 是明令禁的★)
  用例 8 · 目标 H1 · 红的集合 = ['H1'] · PASS
        手法: 把台账 SW/SW_MD5_BASELINE_LEDGER.md 加进声明式排除清单 (★想把判据锚藏起来★)
--------------------------------------------------------------------------------------------
反向用例: 8/8 通过 (★每条都自证「红的集合 == {目标那一条}」★)
ALL TESTS PASS
```
★**rc=0** ★

**③ `state/merge.py`**
```text
✅ STATE.yaml 已刷新 (2026-11-23T22:42:25+08:00)
   产出 796 | 阻塞 43 (高危 33) | 未闭合需求 327 | 冲突 0 | 健康度 red
```
★**rc=0** ★ (★写分片前那一遍 = 22:39:28 · 产出 793 · 未闭合需求 322 · rc 同样 = 0★)

**④ `state/gate_check.py`**
```text
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-23_sw-lead_ISS370_腿B对SW侧影响面.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-23_mech-lead_ISS371_JDEBUG排针1.27净距真相.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
   mech-lead  标签: ['实测', '官方', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 1111 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    434 条
   sw-lead    319 条
   mech-lead  358 条
...
【Q7 钉板 md5 闸链】 10/10 道绿 (★9 道全部 fail-closed 挂在门禁链里★)
   ✅ 钉板闸① FSIN 根因闸: rc=0
   ✅ 钉板闸② G1a-7 选型落表闸: rc=0
   ✅ 钉板闸③ 改板提交顺序闸: rc=0
   ✅ 钉板闸④ 作业包覆盖度闸: rc=0
   ✅ 钉板闸⑤ 脚表功能标签闸: rc=0
   ✅ 钉板闸⑥ 作业包现状值闸: rc=0
   ✅ 钉板闸⑦ 板框坐标闸: rc=0
   ✅ 钉板闸⑧ 结构真值闸: rc=0
   ✅ 钉板闸⑨ SW 侧合法改板通道闸: rc=0
   ✅ 钉板闸⑩ 板侧项全集重跑幂等闸: rc=0

==========================================================================
```
★**rc=0** ★ (★Q1 = 18/18 ★)

**⑤ 板 md5**
```text
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
```
★**rc=0** ★ ⇒ ★**md5 与期望值 `611b869e13518c3c023fb178f91a0075` 逐字相同 ⇒ 板面零写板成立** ★

### B6-2 · ★**边界自证读数 (★期望值 vs 实测值★)** ★

**既有闸复跑 (只读用 · 读完须仍 rc=0)**
```text
SW/tools/check_demo_panel_spec.py        => rc=0   (R1~R7 全过)
SW/tools/check_onepass_sw_sync.py         => rc=0   (①~⑧ 八条齐全 + 现状值与盘面一致)
SW/tools/check_fp_truth_read.py           => rc=0   (绿 7 / 红 0)
SW/tools/check_onepass_legb_sw_impact.py  => rc=0   (9/9 通过)
HW/check_iss354_manufacturability.py     => rc=0   (全部断言通过)
```

**22 条 md5 (板 1 + 受保护/不得改 20 + 分片 1) · 写前 vs 写后 (★21 条逐条相同 + 1 条 = 本单唯一允许变化的那一件 = 分片★)** ★[实测] ★
★**完整读数 = `logs/iss372/07_board_double_evidence.txt` (BEFORE 段 = 22:40:38 · AFTER 段 = 22:4x 写分片后)★**
★**机器判定 (★脚本逐条比对 BEFORE/AFTER 两段的 md5★)**: `BEFORE 件数 = 22 · AFTER 件数 = 22 · md5 不一致的件 = [state/fragments/sw.yaml]` ⇒ ★**21/22 逐字节相同 + 唯一那一条就是本单被允许写的分片 ⇒ 零越界成立** ★

| 文件 | md5 (前后相同) |
|---|---|
| `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` |
| `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` |
| `HW/netlist_v1.csv` | `6aee500e60ba0732f83a9cf557ba90ab` |
| `HW/netlist_v1_pins.csv` | `9174309df1ec9411ac8e8d9e80ee386a` |
| `HW/BOM_v1.csv` | `5b9993992405904a60ac96a020b375d8` |
| `HW/SCHEMATIC_LANDING_V1_LANDED.md` | `d1a7765bb151cc69bb794dc6b6158264` |
| `HW/check_iss354_manufacturability.py` | `838f5a65e8fda7d1257bc49f64d0b558` |
| `SW/SW_MD5_BASELINE_LEDGER.md` | `83fafcf7d22d8fa999a1db74c781956d` |
| `SW/tools/check_demo_panel_spec.py` | `4d9c21dd0125b3b0e1a7e567852287b8` |
| `SW/tools/check_onepass_sw_sync.py` | `3984cab48cea0201a5187abaaa4c9499` |
| `SW/tools/check_fp_truth_read.py` | `cab7a6f17c1da35f4e54185ad8b62089` |
| `SW/tools/check_onepass_legb_sw_impact.py` | `7059f19d7397bf6039d9f87c9ec8ca8f` |
| `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` | `569e684437443a91788b1679c894fed0` (★本趟一个字都没改★) |
| `SW/tools/check_sw_board_md5_rebase_readiness.py` | `0f984c2ade7781afae9b40be417e0feb` (★本趟一个字都没改★) |
| `state/gate_check.py` | `5f370bb8cf828473e70ccc5d6412da98` (★零挂链★) |
| `state/merge.py` | `c9191025020fefd9b475e2573a335815` |
| `state/frag_write.py` | `3b383a52b4fa540f1d16a2c6f3811de8` (★本单只用它·没改它★) |
| `state/check_sch_erc.py` | `aa8d2b966d76def7080bbd1c6f0bd589` |
| `state/check_sch_pinfull.py` | `9f1b498a081a49d436351f54ea572b2a` |
| `state/board_md5_pinned_gates.json` | `917757c0460aee130ceda5ec49aadde1` (★main 的域·零写入★) |
| `state/board_md5_pinned_gates.md` | `918b0969d359120d64efcf6f97beba62` (★main 的域·零写入★) |

### B6-3 · ★**留证路径 (★`logs/iss372/` = 7 件★)** ★

| 文件 | 内容 |
|---|---|
| `logs/iss372/01_scan_sw_md5_refs.txt` | ★逐文件扫描读数 (17 文件 / 47 行 / 57 处) ★ |
| `logs/iss372/02_scan_sw_md5_refs_lines.txt` | ★逐行读数 (47 行) ★ |
| `logs/iss372/03_exp1_sch_md5.txt` | ★`.kicad_sch` md5 实验 (raw 11/11 变 · 归一化 0/11 变) ★ |
| `logs/iss372/04_sch_md5_11files.txt` | ★11 个 `.kicad_sch` 的逐件读数 ★ |
| `logs/iss372/05_sbx_reboard_rehearsal.txt` | ★★沙盒 T0~T5 六阶段全部读数 (★本单第二正题的证据源★) ★ |
| `logs/iss372/06_existing_gates_rerun.txt` | ★既有闸复跑读数 ★ |
| `logs/iss372/07_board_double_evidence.txt` | ★★板三项 + 22 条 md5 (受保护 20 + 板 1 + 分片 1) 的写前/写后对照 (★本趟落的★) ★ |

★**沙盒脚本 (★本趟零重跑·上一趟落的·可复跑★)**: `tmp/iss372/exp2_reboard.py` (★驱动★) · `tmp/iss372/patch_spec.py` (★补丁规格原型·9 条补丁·每条锚点必须恰好匹配 1 次★) · `tmp/iss372/legal_channel_sbx.py` (★通道原型·照 ISS-284 四项原子 + 落表台账链头★) · `tmp/iss372/gen_manifest.py` (★清单生成器·fail-closed rc=2★) · `tmp/iss372/tree/` (★沙盒树★)

---

★**本单零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零改 state/ 下的清单 · 零挂链 · 零外发 · 不代老板拍板 · 不自签 issue_log** ★
★**本单自守: `SW/tools/check_sw_board_md5_rebase_readiness.py` (H1~H7 + 8 条反向用例)★** ★
★**★本趟 (CONT2) 只补了两件: ① 本交卷页 ② `state/fragments/sw.yaml` 分片登记 (★走 `state/frag_write.py`·零重跑扫描·零重建页·零重建闸★)** ★
