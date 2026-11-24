# ISS-399 · mech-lead · MECH 域【已签收件追加台账】设计与自守闸

> **单号**: ISS-399 · **owner**: mech-lead · **verify_by**: main · **零外发**
> **性质**: 纯分析 + 新建真相页 + 新建机器闸 + 出逐字补丁(不应用) · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 不代拍
> **交付物 (3 件)**: `MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md` (真相页) · `MECH/check_mech_signed_append_ledger.py` (新闸 M1~M7) · 本页 (交卷页)
> **配套**: 分片 `state/fragments/mech.yaml` (`grep -c iss399` = 7) · 留证 `logs/iss399/final_acceptance.log` · 生成器 `tmp/iss399/gen_truth_page.py` + `tmp/iss399/gen_handoff.py`

## B1 结论摘要

★**一句话**: ★**MECH 域 11 道闸把「别的文件」的 md5 写死成 49 处 (P1 硬钉 42 处) ⇒ 3 处已陈旧 ⇒ 本单把三处的归因逐字节查清 (ISS-374 cont2 两处 + ISS-296 一处)、实测证明【三处没有一处是纯字节追加】、给出 MECH 域自己的追加登记台账设计 + 一道自守闸 (M1~M7 · 12 条反向用例 · 裸跑预期 rc=1); 台账落位 / 3 处基线怎么追平 / 挂不挂链 / 「追加式订正」算不算合法 —— ★**四条全部交 main, 一条都没代拍**。** ★

★**三条最值钱的发现 (★本单全部本机实读, 不抄任何 agent 报告★):** ★

★**① 【全量数比任务书多 7 处】—— MECH 域的 pin 不是 35 处, 是 49 处 (P1 硬钉 42 处)。** ★
★**代码级 AST 枚举 (★不手抄任何人的表★): 11 道 MECH 域闸 = 42 处硬钉 + 4 处板族钉 + 3 处台账通道钉。任务书 §一 手数的那张表是 35 处 (只点了 9 道闸) ⇒ ★**漏了 `MECH/cavity_recalc_check.py` (5 处) 与 `MECH/display_biosafety_v2_check.py` (2 处)**。★**那 3 处已陈旧 pin 的认定完全正确 (三处都在那 9 道闸里) ⇒ 结论不受影响; 受影响的只是「MECH 域到底有多少处硬钉」这个数 —— 而这个数正是新闸 M1 用来堵缝的基数。** ★ `[实测]`

★**② 【三处陈旧 pin 没有一处是「纯字节追加」⇒ house 规矩「追加式订正·老字一字未删」在这三处【全部不成立】】** ★
★**盘上恰好留着改动前的逐字节副本 (`tmp/iss377/selftest/M1/…`) ⇒ 本单能直接 diff 而不用推算:** ★
★**① `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` (ISS-374 cont2, 2026-11-24 04:12:52): 新增 51 行 / 删掉 9 行 ⇒ 有 5 行表格老字被【就地替换】 (`fab 外框 (含笔画) 5.4404` ⇒ `座体本体外框 2.6400` 等) + 尾部追加 §7 (旧值在 §7 里留档); ★**结论数 (余量 0.1350 / -0.1650 / 0.3100 / 0.0100 与三条判决) 一个字没动**。** ★ `[实测]`
★**② `MECH/check_juart_1p27_clearance.py` (同单, 04:13:02): 行数一模一样 (1,098 行), 只改 2 行 —— 只动 `--selftest` 的变异夹具字段名 (`fab_x`/5.4404 ⇒ `fab_body_x`/2.6400), ★**九条判据 J0~J9 的逻辑、阈值、顺序一个字没动**。** ★ `[实测]`
★**③ `MECH/check_demo_struct_truth.py` (ISS-296, 2026-11-17 20:25:32): 判决源改造 (G5b 接落表台账通道), 该单自报 rc=0 + 反向用例 28/28。** ★ `[实测]`
★**⇒ ⇒ 三处的红【全部正确】(文件确实被改了), 但按「老字一字未删」去设计台账自证 ⇒ 【三处一条都过不了】⇒ 台账会永远判红 ⇒ 等于没设计。⇒ ★**本单把台账的自证字段改成「改动性质 + 旧值是否留档 + 是否已在交卷页披露 + 结论数有没有变」这四条 (★对得上现实★)。** ★

★**③ 【红是真的, 但原因是对的 ⇒ 不是「某个 agent 的红」, 是「MECH 域缺一本账」】** ★
★**三处红至今没人归因 ⇒ 下一个跑这两道闸的 agent 还得自己考古一遍。★**本单已把归因查清并落进真相页 §2 + 分片 `interface_claims.mech_stale_pin_attribution` ★**(⇒ 下一个 agent 直接读分片就能知道这红是谁的、该不该算自己的)。** ★ `[实测]`

## B2 验收标准自评

★**逐条 (★「未验」= 需要 main 拍完 M-A/M-B/M-D 才能验·★本单不代拍★):** ★

| # | 验收标准 | 自评 | 实测依据 |
|---|---|---|---|
| 1 | ★**新建真相页 `MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md`** ★ | ★**通过** ★ | ★**在盘 (70,138 B) · §0~§6 齐全 · §1.5 机器块可解析** ★ |
| 2 | ★**§1 全量清账表 (逐处一行)** ★ | ★**通过** ★ | ★**P1 42 行 + P2/P3 7 行 = 49 处, 全部由 AST 枚举器生成 (★不手抄★)** ★ |
| 3 | ★**§2 三处陈旧 pin 逐条裁定 (合法? / 为什么没人更新基线? / 缺陷?)** ★ | ★**通过** ★ | ★**§2.1 / §2.2 / §2.3 各一节 + §2.4 汇总表; 每条带 9 条证据链 (E1~E9)** ★ |
| 4 | ★**§3 台账设计 (原子记录字段 / 放哪 / fail-closed 口径)** ★ | ★**通过** ★ | ★**§3.1 7 字段逐字段给理由 + §3.2 三个候选的优缺点 (★不代拍★) + §3.3 fail-closed 4 条 + §3.4 判决源换法** ★ |
| 5 | ★**§4 三条逐字补丁 (★不应用★)** ★ | ★**通过 (★补丁只写在页里·一条都没落★)** ★ | ★**补丁 ① 新建只读 helper 全文 + 补丁 ② `check_connector_clearance_caliber.py` 的 K7 (改前 L81-L88 / L642-L653 逐字 + 改后逐字) + 补丁 ③ `check_zoujuan_marker_consistency.py` 的 K5 (改前 L59-L64 / L259-L273 逐字 + 改后逐字)** ★ |
| 6 | ★**§5 挂链建议 (★不应用★)** ★ | ★**通过 (★零挂链★)** ★ | ★**§5 给了挂链理由 3 条 + 逐字建议 + 建议顺序 (M-A→M-B→M-D→落台账→再挂) + 「先挂会挂一道永久红的闸 ⇒ 比不挂更糟」这条代价提示** ★ |
| 7 | ★**§6 边界自证 + 机器块** ★ | ★**通过** ★ | ★**§6.1 板三证 + 11 道闸 md5 + 零挂链 + 零外发 + 不自签 + 只写自己分片; §6.3 闸与页同源逐项对照** ★ |
| 8 | ★**新建机器闸 `MECH/check_mech_signed_append_ledger.py` (M1~M8 + `--selftest` ≥8 条反向用例 + 一条专打 M4)** ★ | ★**通过** ★ | ★**M1~M7 七条判据 + M8 = `--selftest`; ★**反向用例 12 条 (≥8) 全抓到, 末行 `ALL TESTS PASS`, rc=0** ★; c06 = 专打 M4「悄悄改常量 ⇒ 必红」 ★ |
| 9 | ★**新闸零挂链** ★ | ★**通过** ★ | ★**`grep -c check_mech_signed_append_ledger state/gate_check.py` = 0** ★ |
| 10 | ★**新闸裸跑 rc≠0 (★红的是现状·不是闸故障★)** ★ | ★**通过** ★ | ★**裸跑 rc=1, 失败 2 条 = M2 (3 处陈旧 pin) + M3 (台账还没建·M-A 待 main 拍) ⇒ ★**红的是现状** ★**; M1/M4/M5/M6/M7 全绿** ★ |
| 11 | ★**闸自带说明「预期读数 = rc=1 (红)·不许为了让它绿而放宽判据」** ★ | ★**通过** ★ | ★**闸末行逐字保留; ★**本单对它做的 4 处修正全是【修假红】(见 B7 第 3 条) ⇒ 闸整体仍红 ⇒ 没有一条是放宽判据** ★ |
| 12 | ★**交卷页 B1~B7 七块齐全** ★ | ★**通过** ★ | ★**本页 B1/B2/B3/B4/B5/B6/B7 全填; 标题含 `gate_check.py` Q1 要的关键词 (结论/自评/证据分级/接口取值/卡点/复现)** ★ |
| 13 | ★**分片登记 (产出物 + interface_claims + 4 条 needs_from, 全部 to=main)** ★ | ★**通过** ★ | ★**`grep -c iss399 state/fragments/mech.yaml` = 7; 3 件产出物 + 4 条 interface_claims + 4 条 needs_from (★全部 to=main★)** ★ |
| 14 | ★**那 9 道 (★实为 11 道★) 既有闸的 md5 开工前后逐字相同** ★ | ★**通过** ★ | ★**11 道全部与 `logs/iss399/baseline_9gates_md5.txt` 基线逐字相同 (★含任务书点名的 9 道 + 漏数的 2 道★)** ★ |
| 15 | ★**零写板 / 零落表** ★ | ★**通过** ★ | ★**板 md5/mtime(ns)/size 三项 == 基线; 网表/脚表/BOM 三张表 md5 == 基线** ★ |
| 16 | ★**零外发** ★ | ★**通过** ★ | ★**全程只读本机文件 + 跑本机脚本, 零次外发请求** ★ |
| 17 | ★**不代拍 (★任务书 §三 那四条一条都不代拍★)** ★ | ★**通过** ★ | ★**M-A / M-B / M-C / M-D 四条全在 B5 + 分片 `needs_from` (to=main) + 真相页 §3.2/§5 各处只给「建议默认值 + 代价」, 一条都没自己定** ★ |
| 18 | ★**不自签 issue_log** ★ | ★**通过** ★ | ★**`state/issue_log.yaml` 一个字节没动** ★ |
| 19 | ★**沙盒只落项目盘** ★ | ★**通过** ★ | ★**临时产物只写 `tmp/iss399/` · 留证只写 `logs/iss399/` ⇒ 未写系统 `/tmp`** ★ |
| 20 | ★**闸与页同源 (★闸是判据、页是数据·两者必须同源★)** ★ | ★**通过** ★ | ★**真相页 §1.5 机器块由 `tmp/iss399/gen_truth_page.py` import 新闸自己的枚举器生成 ⇒ 结构上不可能各写各的; §6.3 逐项对照表** ★ |
| 21 | ★**台账落位 / 3 处基线追平 / 挂链 / 「追加式订正」口径** ★ | ★**未验 (★要 main 先拍 M-A/M-B/M-D·★本单不代拍★)** ★ | ★**台账文件本单【没有】创建 (⇒ M3 红); 那 11 道闸本单【一个字都没改】(⇒ §4 只出逐字补丁)** ★ |

★**总体自评**: ★**21 条里 20 条通过、1 条未验 (★未验的那条要 main 拍板·★不是本单能自己做的★)。三件交付物全部在盘 · 新闸裸跑 rc=1 (★预期读数·★红的是现状★) · `--selftest` rc=0 末行 `ALL TESTS PASS` (12/12) · 板零写 · 零落表 · 那 11 道既有闸零改 · 零挂链 · 零外发 · 不代拍 · 分片 `grep -c iss399` = 7。** ★

## B3 证据分级

★**五级白名单: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`** ★

| # | 结论 | 等级 | 出处 (★全部本机可复跑★) |
|---|---|---|---|
| 1 | ★**MECH 域 pin 共 49 处 (P1 42 + P2 4 + P3 3), 分布在 11 道闸** ★ | ★`[实测]` ★ | `python3 MECH/check_mech_signed_append_ledger.py` 末行「枚举: 硬钉(无通道) 42 处 / 板族钉 4 处 / 台账通道钉 3 处 ⇒ 合计 49 处」 · 枚举器 = 闸里的 `enumerate_pins()` (AST 解析) |
| 2 | ★**任务书 §一 的 35 处少算了 7 处 (漏 `cavity_recalc_check.py` 5 处 + `display_biosafety_v2_check.py` 2 处)** ★ | ★`[实测]` ★ | 同上枚举结果 vs 任务书 §一 表 (★差集逐闸列在真相页 §1.4★) |
| 3 | ★**3 处陈旧 pin 的基线 ≠ 盘上现值** ★ | ★`[实测]` ★ | `md5sum` + 闸 M2 的原样输出 (基线 `ffc09939`/`ea89e0dd`/`fa9b59e5` vs 现值 `f1ce54c9`/`daf8fa36`/`483d018a`) |
| 4 | ★**改动前副本还在盘上 ⇒ 可逐字节 diff** ★ | ★`[实测]` ★ | `tmp/iss377/selftest/M1/MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` md5 `ffc09939…` (mtime 01:23:23) · `…/check_juart_1p27_clearance.py` md5 `ea89e0dd…` (mtime 01:24:52) |
| 5 | ★**#1 = 5 行表格老字被就地替换 + 尾部追加 §7 (新增 51 行 / 删掉 9 行)** ★ | ★`[实测]` ★ | `diff` 原样输出 (真相页 §2.1.1 逐字列了被删的 9 行) |
| 6 | ★**#2 = 只改 2 行 selftest 夹具, 判据逻辑零改动, 行数不变 (1,098 行)** ★ | ★`[实测]` ★ | `diff` 原样输出 (真相页 §2.2.1) |
| 7 | ★**#3 的作者 = ISS-296, 改动 = G5b 合法改板通道** ★ | ★`[实测]` ★ | `HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md` 第 16 行 + 第 34 行 |
| 8 | ★**三处都已披露 (交卷页里有逐字 md5 台账行)** ★ | ★`[实测]` ★ | ISS-374 页 ⑬ (交卷时 md5 `f1ce54c9`/`daf8fa36`) · ISS-296 页第 16 行 |
| 9 | ★**上游 agent 已经归因过一次, 但没落进任何判决源** ★ | ★`[实测]` ★ | ISS-382 交卷页验收第 11 条: 「`K7` 基线红 2 条是开工前就有的 (ISS-374 cont2 追加已签收页所致)」 |
| 10 | ★**11 道闸里只有 1 道在官方链上 ⇒ 其余的红零通知** ★ | ★`[实测]` ★ | `grep -c` 于 `state/gate_check.py` (★任务书 §一⑤ 同款口径·本单逐道复核★) |
| 11 | ★**新闸的 4 处修正全是修假红, 判据与阈值常量一字没动** ★ | ★`[实测]` ★ | 真相页 §6.2 的逐条对照表 + 修前/修后裸跑读数 (6 条红 ⇒ 2 条红) |
| 12 | ★**台账放在 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 会污染板侧落表链** ★ | ★`[推算]` ★ | ★**依据 = 该文件的语义 (板侧落表台账) + 闸里的 `LEDGER_MANAGED` 口径把 `HW/netlist_v1.csv` 等三个文件归它管; ★**「会污染」是本单的口径判断, 不是实测★** ★ |
| 13 | ★**挂链时机: 先落台账再挂, 否则等于挂一道永久红的闸** ★ | ★`[推算]` ★ | ★**依据 = 新闸裸跑 rc=1 的实测读数 + 官方链红会被习惯性忽略的风险判断; ★**这是判断, 不是实测★** ★ |
| 14 | ★**实物 (座体型号 / 出厂图纸 / 厂回单) 一律无本机证据** ★ | ★`[0数据]` ★ | ★**本单全部结论都在「盘面 + 文本」层; 一条都不依赖外部实物** ★ |

★**★零挂起措辞: 本单【没有】把任何缺口推给外部; 四条待拍事项全部是【main 内部机制地界】, 不是外部依赖 ⇒ 不存在「等外部回话」的缺口。** ★

## B4 接口取值声明 (interface_claims)

★**四条 (★已写进 `state/fragments/mech.yaml` 的 `interface_claims`·★键名见下★):** ★

| 键 | 取值 | 说明 |
|---|---|---|
| ★**`mech_md5_pin_inventory_count`** ★ | ★**49** ★ | ★**MECH 域钉别人 md5 的 pin 总数 (P1 硬钉 42 + P2 4 + P3 3) ⇒ 下一趟别再按 35 数** ★ |
| ★**`mech_stale_pin_attribution`** ★ | ★**3 处: ISS-374 cont2 ×2 + ISS-296 ×1** ★ | ★**三处陈旧 pin 的归因 + 各自的改动性质 + 「都不是偷改」的依据 ⇒ 跑这些闸的 agent 不用再自己考古** ★ |
| ★**`mech_signed_append_ledger_schema`** ★ | ★**表头 = `单号｜文件｜prev_md5｜md5｜追加类型｜追加位置｜自证`** ★ | ★**台账记录格式 (★本单设计·★措辞待 M-A/M-B/M-D 拍板★): 第 5 栏枚举 = 纯字节追加｜局部订正; 第 7 栏自证必须含「旧值是否留档 / 是否已在交卷页披露 / 结论数有没有变」三条 (★不用「老字一字未删」——三处陈旧 pin 一条都过不了★)** ★ |
| ★**`mech_ledger_path_proposed`** ★ | ★**`MECH/SIGNED_APPEND_LEDGER.md`** ★ | ★**M-A 的建议默认值 (★本单【没有】创建这个文件★); 新闸已按此路径实现 ⇒ main 拍别的路径改一个常量即可** ★ |

★**★本单不向任何人【请求接口取值】: 四条全是【本单自己声明的取值】, 归属方是 main 与 MECH 域后续单。** ★

## B5 未决项与卡点 (★要 main 回话的·每条带代价·★一条都不代拍★)

| # | 要 main 回答什么 | 不答的后果 | 本单的建议默认值 (★仅供参考·决定权在 main★) | 归属 |
|---|---|---|---|---|
| ★**M-A** ★ | ★**MECH 域【已签收件追加登记台账】放哪 / 叫什么 / 谁写?** ★ (A = 新建 `MECH/SIGNED_APPEND_LEDGER.md` / B = 复用 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的 MECH 段 / C = 放 `state/` 下) | ★**台账没落位 ⇒ 3 处陈旧 pin 永远归不了因 ⇒ 板那一趟每一处合法追加都变成「来源不明」⇒ 收工验收的红没法判读** ★ (★本单已把三处归因查清写进真相页 §2, 但归因不在判决源里 ⇒ 下一个 agent 还得再查一遍★) | ★**A (新建 MECH 域自己的台账)** ★ —— 理由: B 那本是【板侧落表台账】, MECH 页的追加式订正不是落表, 塞进去会污染板那条链; C 会让闸跨域读账 | main |
| ★**M-B** ★ | ★**3 处已陈旧的基线怎么追平 —— 追平到「台账登记值」还是「显式改常量 + 台账留一行」?** ★ | ★**3 处永久红 ⇒ 每个跑这两道闸的 agent 都要自己写一句「这红不是我造成的」⇒ 噪音永续 (★ISS-382 已经这么写过一次★)** ★ | ★**走台账登记值 (与 ISS-303 N6 同形)**, 且必须同时落真相页 §4 的三条逐字补丁 (硬基线 ∪ 台账链头)。★**代价提示: 走台账登记值 = 台账链头成了新的合法基线 ⇒ 台账一旦被改坏就全域判红 ⇒ 台账的写权限必须比闸还紧 ⇒ 这就是 M-A「谁写」那一问的真正代价** ★ | main |
| ★**M-C** ★ | ★**本单新闸挂不挂 `state/gate_check.py`?** ★ | ★**不挂 ⇒ 下一个 agent 新造一道钉 md5 的闸, 照样从缝里溜过去 (★SW 侧 H4 抓的就是这个, MECH 域至今没有对偶★)** ★ | ★**挂** ★ (与 `SW/tools/check_sw_board_md5_rebase_readiness.py` 同等待遇)。★**挂链时机建议: M-A → M-B (→ M-D) → 落台账 + 落补丁 → 再挂 ⇒ 否则等于往官方链上挂一道永久红的闸 ⇒ 比不挂更糟** ★ | main |
| ★**M-D** ★ | ★**「追加式订正」在 MECH 域到底算不算「合法变更」?** (★本单默认按 house 规矩【算】, 但 K7/K5 两条判据说【已签收件不许改】·且实测三处【没有一处是纯追加】★) | ★**口径不定 ⇒ 台账与判据打架 ⇒ 闸永远红** ★ | ★**算合法, 但台账必须记【改动性质 + 旧值是否留档 + 是否已在交卷页披露 + 结论数有没有变】⇒ 判据从「不许改」变成「不许【悄悄】改」** ★ (★表头已在真相页 §3.1 给出★) | main |

★**★本单【一条都不代拍】: 上面 4 条全部走 `needs_from` 交 main (键名 `iss399_ledger_location` / `iss399_stale_baseline_rebase` / `iss399_gate_hook` / `iss399_append_is_legal`), 每条带「问法 + 不答后果 + 建议默认值 + 归属」。** ★

★**★卡点 (★不是要 main 回答, 是本单自己走不完的★):** ★
★**① 台账本体本单【没有】创建 (★所以 M3 红·★这是现状红·★等 M-A·M-B★)** —— 本单【刻意】不建: 建了就等于替 M-A 拍了落位、替 M-B 拍了追平方式。** ★
★**② 真相页 §4 的三条逐字补丁本单【没有】应用 (★所以那 11 道既有闸一个字没动★)** —— 应用前必须先有台账 (否则补丁里的 `ledger_reader` 读不到链头 ⇒ 两道闸会从「红 2 条」变成「红 4 条 + 2 条报错」)。** ★
★**③ 新闸 M4 有【一个残留缺口】(★双边同步偷换基线抓不到★) —— 真相页 §6.4 写了建议收紧方向 (M4 的锚点从「§1 登记基线」换成「台账链头」), 但★**那是判据口径的改动 ⇒ 归 M-B / M-D 拍板 ⇒ 本单不落** ★。** ★

## B6 自证复现命令 (★必跑命令原样输出 + rc★)

★**复现方式**: `cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses` 后逐条跑; 留证原文在 `logs/iss399/final_acceptance.log` (★本块逐字贴该日志★)。** ★

```text
##### $ python3 MECH/check_mech_signed_append_ledger.py
ISS-399 · MECH 域【已签收件追加登记台账】自守闸
==============================================================================
[ok]   M1   MECH 域每一处【硬钉别人 md5】的 pin 必须在 §1 在册清单里 (★新闸溜过去 ⇒ 判红★)
[FAIL] M2   每处硬钉 pin 的写死基线必须 == 盘上现值 (★现状红·★不是闸故障★)
       · ★陈旧 pin: MECH/check_connector_clearance_caliber.py L84 钉 MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md 基线 ffc09939 ≠ 盘上现值 f1ce54c9 ⇒ 判红 (★红的是现状不是闸故障★)
       · ★陈旧 pin: MECH/check_connector_clearance_caliber.py L86 钉 MECH/check_juart_1p27_clearance.py 基线 ea89e0dd ≠ 盘上现值 daf8fa36 ⇒ 判红 (★红的是现状不是闸故障★)
       · ★陈旧 pin: MECH/check_zoujuan_marker_consistency.py L63 钉 MECH/check_demo_struct_truth.py 基线 fa9b59e5 ≠ 盘上现值 483d018a ⇒ 判红 (★红的是现状不是闸故障★)
[FAIL] M3   每一处陈旧 pin 必须在台账里查到一行 (★查不到 = 来源不明 = 判红★)
       · ★台账判决失败: 台账 MECH/SIGNED_APPEND_LEDGER.md 读不到 (★还没建·★或路径不对·★M-A 待 main 拍★) ⇒ 全部陈旧 pin 归因不到 ⇒ 判红 (★fail-closed★)
[ok]   M4   ★不许靠改常量消红★ (★改常量必须同时在台账留一行·★否则判红★)
[ok]   M5   板三证 (md5 / mtime / size) == 基线 (★零写板自证★)
[ok]   M6   证据分级五级白名单 + 零挂起措辞
[ok]   M7   零挂链 (★本闸不在官方门禁链里·★挂不挂是 main 的地界★)
------------------------------------------------------------------------------
枚举: 硬钉(无通道) 42 处 / 板族钉 4 处 / 台账通道钉 3 处 ⇒ 合计 49 处
判据 M1~M7 · 失败 2 条
FAIL
★**本闸的【预期读数】= rc=1 (红)**: 红的是【现状】(★3 处陈旧 pin 归因不到台账·★不是闸故障★) ⇒ ★**不许为了让它绿而放宽判据** ★
★绿的唯一条件 = ① 3 处陈旧 pin 在台账里有登记行 (单号+prev_md5+md5 四项齐全)② 台账落位 (M-A 待 main 拍) ③ §1 在册清单与盘面零差 ★
rc=1

##### $ python3 MECH/check_mech_signed_append_ledger.py --selftest
沙盒自测 · 真实陈旧 pin 3 处 · BOARD_ONEPASS_JUART_1P27_CLEARANCE.md→f1ce54c9, check_juart_1p27_clearance.py→daf8fa36, check_demo_struct_truth.py→483d018a
[ok]   c01    正向对照: 3 处陈旧 pin 都在台账留行 ⇒ M3/M4 应绿 (★M2 红 = 现状★)
[ok]   c02    把台账清空 ⇒ 陈旧 pin 归因不到 ⇒ M3 应红
[ok]   c03    台账行的单号字段抹掉 ⇒ M3 应红 (★链头无单号★)
[ok]   c04    台账链断 (第二行 prev_md5 ≠ 第一行 md5) ⇒ M3 应红
[ok]   c05    台账链头改成不是盘上现值 ⇒ M3 应红
[ok]   c06    ★专打 M4★ 把闸里的基线常量悄悄改成盘上现值 (台账不动) ⇒ M4 应红
[ok]   c07    ★M4 反向自证★ 改常量 + 台账留对应行 ⇒ M4 应绿 (★证明 M4 不是宽放乱抓★)
[ok]   c08    在沙盒里新造一道闸硬钉一个 md5 (不在 §1 在册) ⇒ M1 应红
[ok]   c09    把 §1 在册清单里删掉一条 ⇒ M1 应红 (★清单过期★)
[ok]   c10    台账行的追加类型写成枚举外的词 ⇒ M3 应红
[ok]   c11    在真相页里写入【零挂起措辞清单里的一个词】 ⇒ M6 应红 (★零挂起措辞★)
[ok]   c12    把 §1 机器块整块删掉 ⇒ M1/M4 应 fail-closed 判红
反向 12 条 (共 12)
ALL TESTS PASS
rc=0

##### $ python3 MECH/check_connector_clearance_caliber.py
=== ISS-377 · MECH/check_connector_clearance_caliber.py ===
页: MECH/BOARD_ONEPASS_CONNECTOR_CLEARANCE_CALIBER.md
CRIT=0.6000 (真身 MECH/service_port_check.py L126-L127) TOL[fdm_part]=0.3000
------------------------------------------------------------------------------
K0   PASS   §1 表逐格与既有真相页一致
K1   PASS   口径来源逐行逐轴已标且非空
K2   PASS   余量与判决逐行逐轴自洽
K3   PASS   余量按 X/Y 两向向量判且有 X绿Y红 实例
K4   PASS   §2 每条冲突都有分开的判据句/后果句
K5   PASS   证据等级白名单 + 零挂起措辞 + 降级方案齐全
K6   PASS   板 md5/mtime/size 三项 == 基线
K7   FAIL   MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md md5 f1ce54c981dd1f64071a177a374df85d != 已签收基线 ffc099397dc573df207f265bff57dffb; MECH/check_juart_1p27_clearance.py md5 daf8fa367d89e22f6d3af3d5049bdfb6 != 已签收基线 ea89e0dd3b2f77828b69f06bbe76969d
K8   PASS   零挂链 (grep -c == 0)
------------------------------------------------------------------------------
RESULT: FAIL (1 条不通过)
rc=1

##### $ python3 MECH/check_zoujuan_marker_consistency.py
=== MECH/check_zoujuan_marker_consistency.py (ISS-238) ===
  [K1] 走鹃行必须全部带 canonical 标注 (活动口径 = 0)   PASS
        走鹃命中 36 行 ; 带 canonical 36 行 ; 活动口径 = 0 (必须 0) ; 逐文件(活动/带标注): MECH_BUDGET.md 0/28 · PROTOTYPE_PLAN.md 0/3 · SOC_CARRIER_EVAL.md 0/1 · STRUCT_REVIEW_ISS065.md 0/3 · CLEARANCE_FIX.md 0/1
  [K2] canonical 标注串自身在位 (门禁不许自我失效)       PASS
        canonical 标注串在位: 走鹃行 36 处 + 提案文件 + 受保护脚本 MARKER 常量一致
  [K3] 结构侧真源不许有裸走鹃命中 (真漏标)                PASS
        MECH/MECH_BUDGET.md 走鹃命中 28 行 ; 无标注裸命中 = 0 (必须 0)
  [K4] 作废标注形态清单 ↔ 盘面双向一致                  PASS
        作废标注形态 4 种, 盘上出现次数 已作废=10/已作废 (2026-11-15, ISS-134 V2)=36/已作废 (ISS-222 · 2026-11-16, C-6 落地)=1/已作废 (ISS-222 · C-6 落地)=1 ; 与提案 §5 登记清单双向一致 (白名单 4 种)
  [K5] 受保护文件 md5 未变                       FAIL
        受保护文件被改: MECH/check_demo_struct_truth.py md5 483d018a66d17d2ead25d1558a1f8ffe≠fa9b59e593a13408ad9505d986276f63
结论: 4/5 项通过
✗ 门禁不通过: K5
rc=1

##### $ python3 MECH/check_onepass_mech_release.py
================================================================================================
【MECH 侧「板只改一次」准出汇总闸】 (ISS-300)
================================================================================================
  汇总根 (root) = /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  闸数 = 6  ·  ★清单缺一道 ⇒ 汇总直接红 (不许「没跑就当过」)★

  [1/6] MECH/check_board_frame_coords.py
        名称: 坐标系闸 (C1~C4 · ISS-276)
        rc  : 0     ⇒ ✅ 绿
        详情: 全部检查项通过

  [2/6] MECH/check_demo_struct_truth.py
        名称: 结构侧真值闸 (G1~G8 / C21~C22 · ISS-213/224/273)
        rc  : 0     ⇒ ✅ 绿
        详情: 全部检查项通过

  [3/6] MECH/check_onepass_mech_sync.py
        名称: MECH 侧板侧输入闸 (M1~M5 · ISS-278/286)
        rc  : 0     ⇒ ✅ 绿
        详情: 全部检查项通过

  [4/6] MECH/check_onepass_struct_crosscheck.py
        名称: 结构侧交叉核对闸 (N1~N6 · ISS-290)
        rc  : 0     ⇒ ✅ 绿
        详情: 全部检查项通过

  [5/6] MECH/board_port_opening_s6_check.py
        名称: S6 板侧开口复算闸 (ISS-271)
        rc  : 0     ⇒ ✅ 绿
        详情: 全部检查项通过

  [6/6] MECH/check_mech_verdict_freshness.py
        名称: 结构结论防漂闸 (F1~F6 · ISS-295)
        rc  : 0     ⇒ ✅ 绿
        详情: 全部检查项通过

================================================================================================
【汇总】
================================================================================================
  6 道闸: 绿 6 / 红 0
  ★汇总 rc = 0 ⇒ ★MECH 侧结构可以出 Gerber★
    (★只代表结构侧 6 道闸全绿; ★不等于整条板链全绿·HW/SW 侧的闸另算★)
rc=0

##### $ python3 MECH/check_demo_struct_truth.py
====================================================================================================
ISS-213/224 结构侧真值门禁 (demo 板当前成立的条目 + 板框/阈值/红灯保护 + 真源台账对账)
====================================================================================================
定性表: MECH/HW_CROSS_REVIEW_TRIAGE.md  |  源: MECH/service_port_check.py + MECH/hw_cross_review_check.py + MECH/BOARD_GEOM_30MM.md + HW/netlist_v1.csv + HW/SCHEMATIC_V1.md
----------------------------------------------------------------------------------------------------
  [OK ] G1    不许把红灯调没 (FAIL 名单仍是 16 条)
         实测汇总 PASS 15 / FAIL 16 / 条件通过 8 / 说明 15 (共 54)
  [OK ] G1b   FAIL 名单逐条对齐 (一条不许少/一条不许多)
         实测 16 条 vs 锚点 16 条; 差集 实测多=[] 锚点多=[]
  [OK ] G2.1  检修口盖板内腔 ≥ cavity_req (ISS-126 现口径)
         内腔 = 7.3 − 2.6 = 4.70mm vs 硬要求 4.50 (余 +0.20); 锚点写 4.7
  [OK ] G2.2  Type-C 新开孔口径最坏单边间隙 ≥ 判据 (FDM 直成型档)
         10.5×4.8 ⇒ 最坏 X 0.63 / Y 0.62 vs 判据 0.60
  [OK ] G2.3  Type-C 金属/CNC 档最坏单边间隙 ≥ 判据 (±0.05)
         10.25×4.55 ⇒ 最坏 X 0.63 / Y 0.62 vs 判据 0.60
  [OK ] G2.4  两档现候选 (打印包现试样) 判不合格 —— 证明'二选一'是假选择
         现口径: 最坏 X 0.13 / Y 0.02; ISS-089 建议: 最坏 X 0.38 / Y 0.32
  [OK ] G2.5  端件温升按 buck 口径 (Pin−Pout+DCR), 不用 MECH_BUDGET 的 0.8W 线性口径
         P=0.50W × R=166.67 K/W ⇒ ΔT 83.3K ⇒ 表面 108.3°C (线性口径 0.80W ⇒ ΔT 133K ⇒ 158°C)
  [OK ] G2.6  60°C 判据 ⇒ 端件表面能吃下的最大耗散 P_max (现值必须超它 ⇒ 强制金属热路)
         P_max = (60−25)/166.67 = 0.210W; 现耗散 0.50W ⇒ 超 2.38× ⇒ 必须金属热路
  [OK ] G2.7  散热路径必须是金属 (打印件 R 远大于铝)
         打印件 1944 K/W vs 铝 1.641 K/W (差 1185×) ⇒ 0.5W 打进去 +972K (打印件) vs +0.82K (铝)
  [OK ] G2.8  buck 功率守恒 ICHG/IIN = η·Vbus/Vbat (规格书的 0.822/0.933 是倒数)
         3.70V ⇒ 1.216 (锚点 1.216) · 4.20V ⇒ 1.071 (锚点 1.071); 规格书倒数 = 0.822 / 0.933
  [OK ] G2.9  demo 当前成立的 PASS 项 (公差链 C1~C5 / 径向 / 堆叠余量 / 合并 14P / 拓扑 B) 全过
         共 12 项, 不再 PASS 的 = 无
  [OK ] G3    6 个 PCB 类 id 已登记排队且恢复条件非空 (不许静默丢弃)
         排队表缺恢复条件的 = 无; 锚点 pcb_class_queued 缺的 = 无
  [OK ] G3b   排队的 PCB 类 id 在 hw_cross_review_check.py 里仍然是 FAIL (不许修绿)
         不再是 FAIL 的 = 无
  [OK ] G4    MECH/BOARD_GEOM_30MM.md §1 四数 (60.00/30.00/1.00/3.33g) 一个没被改
         §1 缺失项 = 无; 锚点与文档不一致 = 无
  [OK ] G4b   板框四数与两个 check 脚本的现行口径一致 (pcb_len/pcb_w/pcb_thk)
         脚本 pcb_len=60.0 / pcb_w=30.0 / pcb_thk=1.0 vs 锚点 60.0/30.0/1.0
  [OK ] G5    判据阈值未松: cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00
         service_port: cavity_req=4.5 cav_v=38.0 duct_v=6.0 CRIT=0.60; hw_cross_review: judge=0.6 cav_v_now=38.0
  [OK ] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro 走【合法改板】通道 (ISS-296) + 4 个 check 脚本 + 网表/脚表)
         4 个硬保护 check 脚本 全部一致 + 2 个受保护硬件件走合法改板通道 (板/.kicad_pro: HW/PCB/demo_mainboard.kicad_pcb=纯 md5 硬保护 (台账无变更行), HW/PCB/demo_mainboard.kicad_pro=纯 md5 硬保护 (台账无变更行)) + 2 个台账管理真源 = 台账最新记录 (链头: HW/netlist_v1.csv=6aee500e60ba, HW/netlist_v1_pins.csv=9174309df1ec) + 域侧锚点副本 = 历史留痕 (允许停在历史值)
  [OK ] C21   真源变更台账对账 (盘上真源 ↔ 落表台账最新记录 (链头) ↔ 域侧锚点历史副本)
         台账最新记录 (链头) = HW/netlist_v1.csv 6aee500e60ba (by ['ISS-302']), HW/netlist_v1_pins.csv 9174309df1ec (by ['ISS-302']); 锚点副本 = 历史留痕 (允许停在历史值, 但不许与台账对不上)
  [OK ] C22   PIN-MISMATCH 独立复核 (P9 页声明 vs 网表实际 + d6 新旧口径)
         网表实读 CONN_LIGHT 22p / CONN_CAM 31p / J_CHG 10p; P9 声明 CONN_LIGHT [22] / CONN_CAM [31] / J_CHG [10]; 旧口径 0 处 / 新口径 3 处
  [OK ] G6    定性表 54 项全覆盖 (项号一个不缺) 且处置栏不留空/不写'待定'
         表内 54 行 / 应 54; 缺项号 = 无; 多余项号 = 无; 处置留空或待定 = 无
  [OK ] G6b   16 条 FAIL 每条都有明确去处 (修掉/出规格/登记 need 给 main/排队等原理图定稿)
         FAIL 行 16 条; 去处不在受控词表里的 = 无
  [OK ] G7    分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)
         实测 value = 25.00
  [OK ] G8    已修复的留痕必须在场 (PIN-MISMATCH 行 + §3.1「已修复 (留痕)」节)
         §2 行在位 (判定 = ✅ PASS, 备注带 ISS-220/落表) + §3.1 已修复节在位 (列着 ['PIN-MISMATCH', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'MECH/service_port_check.py` 的 md5 锚点 (门禁 **G5b**)', 'MECH/check_demo_struct_truth.py` 的 md5 (门禁脚本【本体】) + ★**判决源机制本身**★'])
----------------------------------------------------------------------------------------------------
【结论】23/23 组检查通过 | FAIL 0 组
口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**。
          本闸守的是 **demo 板当前成立的条目**, 不是'54 项全绿'。
          ★ 6 个 PCB 类 id 仍是 FAIL 是**正确状态** (排队等原理图定稿), 不是缺陷。
          ★ ISS-224: `PIN-MISMATCH` 是**被 ISS-220 真修好了**, 不是被调没 ⇒ 留痕在 §2 第 05 行 + §3.1。
====================================================================================================
rc=0

##### $ md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
rc=0

c4bf9151dd59826fb2320c34e8afbd0f  MECH/cavity_recalc_check.py
fc8d97d48cacafb43a1be4e1fe3a6524  MECH/check_connector_clearance_caliber.py
667e6006280cc8c0533d8ce8fa39f8be  MECH/check_debug_seat_3d_fit.py
babadd6b073d691374051ea7409a6a1f  MECH/check_debug_seat_rework_spec.py
483d018a66d17d2ead25d1558a1f8ffe  MECH/check_demo_struct_truth.py
1cdc6e9838419647e018c9a4c41319a2  MECH/check_fts_seat_body_geometry.py
7b6ae98c04d32dea87e90f9a683bcac7  MECH/check_fts_seat_sample_plan.py
8f8424a5e632fa3d223271850109c6d0  MECH/check_fts_vs_generic_courtyard_delta.py
c898273018eabba466a04b88402d286c  MECH/check_mech_dual_caliber_gate.py
bcc165d7461ba8906c03b101a72f962d  MECH/check_zoujuan_marker_consistency.py
29c77fc3fc823048b1d96c9500d28dd7  MECH/display_biosafety_v2_check.py

HW/PCB/demo_mainboard.kicad_pcb md5-见上 size=4940213 mtime=2026-11-06 07:07:17.362193413 +0800

grep -c iss399 state/fragments/mech.yaml = 7
grep -c check_mech_signed_append_ledger state/gate_check.py = 0
grep -c check_mech_signed_append_ledger state/gate_check.py ⇒ 零挂链自证完成
##### $ python3 state/merge.py && python3 state/gate_check.py
✅ STATE.yaml 已刷新 (2026-11-24T22:11:45+08:00)
   产出 886 | 阻塞 43 (高危 33) | 未闭合需求 400 | 冲突 0 | 健康度 red
merge rc=0

==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-24_hw-lead_ISS396_FTS改孔登记落盘.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-24_sw-lead_ISS398_第三道病闸自测基线无关化.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-24_mech-lead_ISS399_MECH域已签收件追加台账设计与自守闸.md

【Q2 证据分级率】 2/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算']
   sw-lead    标签: 无
   mech-lead  标签: ['实测', '官方', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 1281 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    500 条
   sw-lead    362 条
   mech-lead  419 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 171/621  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 244 条, 其中 58 条真对上了别人的需求 key
   hw-lead    被答 63/307 | 我答 87 条(有效 31) | 产出 346 | 阻塞 7
   sw-lead    被答 46/110 | 我答 72 条(有效 6) | 产出 299 | 阻塞 15
   mech-lead  被答 62/204 | 我答 85 条(有效 21) | 产出 226 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也有可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 51 条 | **全局 46 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 400 条**
   ✅ 与 merge.py 自对账一致 (等外部 46 / 等总工 400)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): 10 个
      q4_battery_scope: 发起方 ['main', 'hw-lead', 'mech-lead']
      q16_aspect_ratio: 发起方 ['main', 'hw-lead', 'mech-lead']
      iss105_jchg_rfq_release: 发起方 ['main', 'hw-lead']
      iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice: 发起方 ['main', 'mech-lead']
      iss236_boss_v_decision: 发起方 ['main', 'hw-lead']

【Q5 硬指标覆盖】 1/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    2/5 类: ['镜腿/镜脚厚度(mm)', 'FCCSP 球间距(pitch)']
   sw-lead    0/5 类: []
   mech-lead  3/5 类: ['功耗(W)', '皮肤温度(°C)', '镜腿/镜脚厚度(mm)']

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

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

【缺口清单】(可直接转成下一轮派活项) —— 4 条
   · hw-lead: 224 条需求确实还没人答 (等另一个总工)
   · sw-lead: 关键结论未做证据分级 (实测/官方/推算/0数据)
   · sw-lead: 50 条需求确实还没人答 (等另一个总工)
   · mech-lead: 125 条需求确实还没人答 (等另一个总工)

==========================================================================
gate_check rc=0
```

★**读数摘要 (★与上面的原样输出逐字对应★):** ★

| 命令 | rc | 判读 |
|---|---|---|
| `python3 MECH/check_mech_signed_append_ledger.py` | ★**1** ★ | ★**预期读数 (★红的是现状·★不是闸故障★): M2 红 (3 处陈旧 pin) + M3 红 (台账还没建·等 M-A/M-B); M1/M4/M5/M6/M7 绿** ★ |
| `python3 MECH/check_mech_signed_append_ledger.py --selftest` | ★**0** ★ | ★**反向 12 条全抓到 · 末行 `ALL TESTS PASS`** ★ |
| `python3 MECH/check_connector_clearance_caliber.py` | ★**1** ★ | ★**基线红 2 条 (★开工前就有·★本单没让它多红一条★)** ★ |
| `python3 MECH/check_zoujuan_marker_consistency.py` | ★**1** ★ | ★**基线红 1 条 (★同上★)** ★ |
| `python3 MECH/check_onepass_mech_release.py` | ★**0** ★ | ★**MECH 侧准出汇总闸没被扰动** ★ |
| `python3 MECH/check_demo_struct_truth.py` | ★**0** ★ | ★**钉板闸⑧ (★在链★) 没被扰动** ★ |
| `md5sum` 板 + 三张表 | ★**0** ★ | ★**板 `611b869e…` / 网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 全 == 基线** ★ |
| `grep -c "iss399" state/fragments/mech.yaml` | — | ★**7 (≥1)** ★ |
| `grep -c check_mech_signed_append_ledger state/gate_check.py` | — | ★**0 (零挂链)** ★ |
| `python3 state/merge.py && python3 state/gate_check.py` | ★**0** ★ | ★**见下方收工复跑块** ★ |

## B7 边界自证

| 边界 | 要求 | 自证 (★全部本机实跑★) | 结论 |
|---|---|---|---|
| ★**零写板** ★ | 板 / 网表 / 脚表 / BOM / 原理图真源 一个字节不许动 | ★**板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` (ns `1793920037362193413`) · size `4940213`; 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8`** ★ | ★**成立** ★ |
| ★**零改既有闸** ★ | ★**那 9 道 (★实为 11 道★) 闸的判据 / 阈值 / 常量 / 正文一个字不许动** ★ | ★**逐字 md5 与 `logs/iss399/baseline_9gates_md5.txt` 基线相同:** `fc8d97d4…` (caliber) · `667e6006…` (3d_fit) · `babadd6b…` (rework_spec) · `483d018a…` (demo_struct_truth) · `1cdc6e98…` (fts_body_geom) · `7b6ae98c…` (fts_sample_plan) · `8f8424a5…` (fts_vs_generic) · `c8982730…` (dual_caliber) · `bcc165d7…` (zoujuan) · ★**另 2 道漏数的: `c4bf9151…` (cavity_recalc_check) · `29c77fc3…` (display_biosafety_v2_check)** ★ | ★**成立** ★ |
| ★**零改既有页面正文** ★ | 只许新建真相页 + 交卷页 | ★**只新建了 `MECH/BOARD_ONEPASS_SIGNED_APPEND_LEDGER_DESIGN.md` + 本页; 已有的 MECH 页面一个字没改** ★ | ★**成立** ★ |
| ★**零挂链** ★ | `grep -c check_mech_signed_append_ledger state/gate_check.py` = 0 | ★**0** ★ | ★**成立** ★ |
| ★**零外发** ★ | 不发邮件 / 询价 / 问询 / 采购 | ★**全程只读本机文件 + 跑本机脚本, 零次外发请求** ★ | ★**成立** ★ |
| ★**不代拍** ★ | M-A/M-B/M-C/M-D 一条都不自己定 | ★**四条全在 B5 + 分片 `needs_from` (to=main); 真相页 §3.2/§5 只给「建议默认值 + 代价」** ★ | ★**成立** ★ |
| ★**不自签 issue_log** ★ | `state/issue_log.yaml` 一个字节不许动 | ★**没动** ★ | ★**成立** ★ |
| ★**只写自己分片** ★ | 只走 `state/frag_write.py --agent mech-lead` | ★**只写了 `state/fragments/mech.yaml`; `hw.yaml` / `sw.yaml` / `pm.yaml` 没碰** ★ | ★**成立** ★ |
| ★**沙盒只落项目盘** ★ | 临时产物只写 `tmp/iss399/` · 留证只写 `logs/iss399/` | ★**未写系统 `/tmp`** ★ | ★**成立** ★ |

★**★一条必须主动交代的事 (★不交代就是不诚实★): ★**本单对自己新建的新闸 `MECH/check_mech_signed_append_ledger.py` (★上一趟 21:48:41 落盘的那一份★) 做了 4 处实现缺陷修正。** ★
★**★这 4 处【全部是修假红】(★闸说自己坏·其实自己没坏★), ★**判据与阈值常量一条没动, 闸整体仍然红 (rc=1, M2/M3 红 = 现状)** ⇒ ★**不是「为了让它绿而放宽判据」。** ★

| # | 位置 | 问题 | 修法 | 判据/阈值动没动 |
|---|---|---|---|---|
| 1 | M5 (板三证) | ★**拿 6 位微秒去比 9 位纳秒基线 ⇒ M5 永远红 ⇒ 且打印「板被写过」⇒ 对真没被写过的板做假指控** ★ | 改用 `st_mtime_ns` 的纳秒位按 9 位拼 | ★**没有** (★`BOARD_MD5`/`BOARD_MTIME`/`BOARD_SIZE` 三个阈值常量一字未改·★精度反而更严★) ★ |
| 2 | M6 (证据分级) | ★**闸源码里就有 `FORBIDDEN_PENDING` 词表常量 ⇒ 扫自己源码必然自命中 ⇒ M6 永远红** ★ | 扫本闸源码时先剔掉词表定义块 (★词表一个词没删·★真相页/台账两处的扫描一个字没动★) | ★**没有** ★ |
| 3 | `--selftest` c01 + 沙盒构建 | ★**① c01 期望「M2 也绿」, 但 M2 是现状判据 ⇒ 用例永远不可能通过; ② 沙盒没复制被钉的 .md 页 ⇒ 4 条用例改的那一行在沙盒里不存在 ⇒ 「应红却绿」假通过** ★ | ① 期望值改成逐判据给; ② 沙盒额外复制每处 pin 的被钉文件本身 (只读副本) | ★**没有** (★只改自测用例的期望写法与沙盒文件清单·★M1~M7 一条没动★) ★ |
| 4 | `--selftest` c11 夹具 | ★**c11 的标题与夹具里把零挂起词表里的词又写了一遍 ⇒ 闸源码又含那个词 ⇒ M6 又自命中** ★ | 夹具改成从词表里取那个词 (`FORBIDDEN_PENDING[0]`), 用例标题改成不含该词的描述 | ★**没有** (★c01 除外, c11 反而从【假通过】变成【真通过】★) ★ |

★**★修前/修后: 裸跑 6 条红 (M1 红=本页未落 · M2 红=现状 · M3 红=台账未建 · M4 红=fail-closed · M5 红=假红 · M6 红=假红) ⇒ 修后 2 条红 (M2/M3 = 现状) ⇒ `--selftest` 由 `SELFTEST FAILED (3/12)` ⇒ `ALL TESTS PASS` (12/12)。** ★

★**★★ 回卷摘要 ★★** ★**三件交付物已落 (真相页 70,138 B + 新闸 + 本交卷页) + 分片已落 (3 产出物 / 4 interface_claims / 4 needs_from 全 to=main) + 留证 `logs/iss399/final_acceptance.log`; ★**新闸裸跑 rc=1 (★预期读数·红的是现状★) · `--selftest` rc=0 末行 ALL TESTS PASS (12/12) · 板零写 · 零落表 · 那 11 道既有闸零改 · 零挂链 · 零外发 · 不代拍** ★** ⇒ ★**本单闭环, 剩下的只有 M-A / M-B / M-C / M-D 四条等 main 回话 (★每条都带代价·一条都没代拍★) ★** ★
