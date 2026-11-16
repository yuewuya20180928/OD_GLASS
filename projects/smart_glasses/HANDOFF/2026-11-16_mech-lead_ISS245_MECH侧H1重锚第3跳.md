# [mech-lead→PM] ISS-246 · MECH 侧 §1 锚点重锚到 ISS-243 落表后的盘上真值 (H-1 第 3 跳)

| 项 | 值 |
|---|---|
| **单号** | ★**ISS-246** · **owner**: mech-lead (结构总工, 带散热) · **verify_by**: main (项目总工) ★ |
| **交卷时刻** | ★**2026-11-16 18:2x (GMT+8)** ★ |
| **地界** | ★**只动 `MECH/HW_CROSS_REVIEW_TRIAGE.md` (§1 锚点 2 条 × 4 字段 + §1 `landing_records` + §3.1 追加 R-04 留痕行) + 本交接单 + `state/fragments/mech.yaml` (走 `python3 state/frag_write.py` 原子写)** ★ ⇒ ★**`HW/` 受保护件一个字节没写 (★网表 / 脚表 / BOM / 板 / `.kicad_pro` 五个 md5 交卷前后逐字节不变★) · `SW/` 一个字节没写 (★SW 台账 / SW 分片 = ISS-245 sw-lead 的活, 本单零碰★) · `state/issue_log.yaml` 自改零处 · `PROJECT_TRACKER.md` §0 零改动 · 门禁脚本一个字节没碰** ★ |
| ★**零外发** ★ | ★**本单没发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 口径: 不再发信, 缺口一律自己查资料 + 标证据等级; 本单无外部缺口★) ★ |
| ★**实物 [实测] = 0 条** ★ | ★**本单零实物** (★MECH 侧纯锚点重锚 + 门禁复跑, 板与样件不在本机 ⇒ 所有 [实测] 都是"本机脚本实跑 / 本机文件实读"★) ★ |

---

## ★0 一句话

★★**这次红 = 【上游合法落表后的锚点过期】, 不是【真源被换】、更不是【红灯被调没】** ★★
⇒ **ISS-243 (hw-lead) 2026-11-16 15:45 合法落表第 4 批** (`C_REGN` 1µF → **4.7µF ±10% (10V)**, ★TI BQ25896 SLUSC76C pin22 官方硬要求, 无需拍板★)
⇒ 网表 / 脚表 / BOM 被重生成 ⇒ **md5 全变** ⇒ **MECH 侧 §1 锚点还钉在落表前的旧 md5** ⇒ **G5b + C21 双红 (rc=2, 21/23)**
⇒ ★**本单走 §3.1 建立的 H-1 重锚流程 (第 3 跳: ISS-223 第 1 跳 → ISS-233 并发第 2 跳 → 本单第 3 跳)**: ★**只改 §1 锚点那两条的 4 个字段 (`md5` / `prev_md5` / `by` / `landed_at`) + §1 `landing_records` 加 ISS-243 交接单位置 + §3.1 追加 R-04 留痕行** ★
⇒ ★**G5b / C21 的判据逻辑一个字没动 · 阈值一个没松 · 反向用例一条没删 (14/14) · `HW/` 下 0 字节写入** ★
⇒ ★**`check_demo_struct_truth.py` rc=0 (23/23) · `--selftest` rc=0 · 14/14 · `merge`+`gate_check` rc=0 (Q1 18/18) · 受保护 5 件 md5 逐字节不变** ★

---

## B1 结论摘要

| 序 | 结论 | 证据 |
|---|---|---|
| **1.1** | ★**病灶 = 锚点过期 (不是真源被换)**: 开工前本单实跑 `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=2 · 「【结论】21/23 组检查通过 \| FAIL 2 组」** ⇒ 红的是门禁自己标名的 2 组: ★**G5b** (受保护文件 md5 逐字节未变) + ★**C21** (真源变更台账对账) ★ ⇒ ★**不是几何/公差栈的问题** (★G2.1~G2.9 / G4 / G4b / G5 / C22 全绿★) ★ | ★`[实测]` 开工前本机实跑 (★原样输出见 B5 ①★) ★ |
| **1.2** | ★**根因 = ISS-243 合法落表第 4 批 (2026-11-16 15:45)**: `C_REGN` 的 value 从「[待选型] 1µF」改成「4.7µF ±10% (10V)」+ 首次带 footprint (0805, **2.0×1.25 mm**) + OPN (`GRM21BR71C475KA73L`) ⇒ ★**三处落表 = 网表 L44/L45 + 脚表 L132/L133 + BOM L43 ⇒ 网表 / 脚表 / BOM 被重生成 ⇒ md5 全变** ★ ⇒ ★**真源 (网表 / 脚表 / BOM) 一个字都没被我改** ★ | ★`[官网]`+`[实测]` TI BQ25896 (SLUSC76C) §Pin Functions pin22 REGN 行原文: "Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND." (★hw-lead 本机 PDF 实读, 缓存 `state/.cache_iss243/bq25896.pdf` + `bq25896.txt`★) · ★`[实测]` 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 / §16.4 ★ |
| **1.3** | ★**板那一侧逐字节不变 ⇒ 真源没被动过**: `HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` · `HW/PCB/demo_mainboard.kicad_pro` = `3e504d2be83152e337949723e909be1b` ⇒ ★**ISS-243 明确「板逐字节未动」⇒ 变的只有网表/脚表/BOM 这三件生成物 ⇒ 这不是"真源被换"** ★ | ★`[实测]` 交卷前后 `md5sum` 5 件完全一致 (见 B5 ⑦) · ★`[实测]` 落表台账 §16.4「受保护 md5 前后对照」★ |
| **1.4** | ★**落表凭据齐全 (四项在同一行 ⇒ C21 判据 ②③④⑤ 都过)**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` **§16** (「第 4 批落表条目 (★ISS-243 · 2026-11-16 · 硬件总工 (hw-lead) 执行 · ★**C_REGN 官方值落表**★)」) + **§16.4 L656** (★`HW/netlist_v1.csv` · 旧 `34132f7e40a241e1fae1476be0eafbd5` → 新 `611c3ba3db3dc7de7213063375b96d01` · 「是 (★只有 L44/L45 两行★)」★) + **L657** (★脚表 旧 `b21b743a7702d30729f0d653c15392df` → 新 `ef436a37412ac9b6eac3c9f41f1edca4` · 「是 (★只有 L132/L133 两行★)」★) ⇒ ★**单号 + 文件名 + 新 md5 + 旧 md5 四项齐全且在同一行** ★ | ★`[实测]` 本机 `grep -n` 落表台账 ⇒ L656/L657 逐字命中 (★原文见 B5 ⑤★) ★ |
| **1.5** | ★**落表时刻 = 2026-11-16 15:45:45** (★不是我自己编的★): 三件生成物的落盘 mtime = **15:45:45** (★网表 `15:45:45.577` / 脚表 `15:45:45.673` / BOM `15:45:45.787`★) ⇒ ★**`landed_at` 字段填 `"2026-11-16 15:45:45"`, 与 R-02 (ISS-223 → `"2026-11-16 05:18:41"`) / R-03 (ISS-233 → `"2026-11-16 06:48:38"`) 同一口径 (取重生成产物落盘到秒)★ ★ | ★`[实测]` 本机 `stat -c '%y' HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` ★ |
| **1.6** | ★**判别证据 ① = 门禁脚本一个字没被碰过 ⇒ 是锚点过期不是红灯被调没**: `MECH/check_demo_struct_truth.py` mtime = **2026-11-16 03:55:42** · md5 = `fa9b59e593a13408ad9505d986276f63` ⇒ ★**都早于落表时刻 15:45:45 ⇒ 脚本没被改过 ⇒ 红灯是"锚点过期", 不是"有人把红灯调没了"** ★ | ★`[实测]` 本机 `stat` + `md5sum` ★ |
| **1.7** | ★**判别证据 ② = 反向自证 (★在 `/tmp/iss246_mech/sandbox/` 里做的, 真盘一个字节没动★)**: ★**A 绿 (rc=0 · 23/23) → B 把锚点回滚到 ISS-233 那版 (`34132f7e…` / `b21b743a…`) ⇒ G5b + C21 那 2 组重新变红 (rc=2 · 21/23) → C 装回去 ⇒ 又绿 (rc=0 · 23/23)** ⇒ ★**证明 G5b / C21 这 2 组跟着盘上真值走, 不是摆设** ★ | ★`[实测]` 沙盒三步原样输出见 B5 ④ ★ |
| **1.8** | ★**本单只改锚点数字, 判据逻辑一个字没动**: G5b 的判据 (6 个硬保护文件 md5 + 2 个台账管理真源 md5) 与 C21 的 6 条判据 (①盘上==锚点 ②锚点md5可查台账 ③prev_md5可查台账 ④by可查台账 ⑤三项同一行 ⑥台账位置存在) ★**逐条原样保留** ★ · ★**阈值一个没松** (`cavity_req` 4.50 / `CRIT` 0.60 / `cav_v` 38.00 / `duct_v` 6.00 / 板框 60.00×30.00×1.00×3.33g) ★ · ★**反向用例一条没删 (14/14, 且 REV-11 现在动态读出的就是 ISS-243 那版)** ★ | ★`[实测]` `check_demo_struct_truth.py --selftest` ⇒ **rc=0 · 14/14** (★输出见 B5 ③★) · ★`[实测]` 门禁脚本 md5 `fa9b59e5…` 交卷前后逐字节不变 ★ |
| **1.9** | ★**留痕已登记 (§3.1 追加 R-04 行)**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` §3.1 **追加** R-04 (★追加式: **R-01 / R-02 / R-03 历史行一个字没改**★) ⇒ ★**G8「留痕在场」门禁仍绿** ★ | ★`[实测]` `--selftest` ⇒ **14/14** (★REV-14「删掉『已修复 (留痕)』那一节」仍能抓到红★) · ★`[实测]` `grep` 逐行确认 R-01~R-04 全在位 ★ |
| **1.10** | ★**`HW/` 下 0 字节写入 (★就本单自己动的口径★)**: 网表 / 脚表 / BOM / 板 / `.kicad_pro` 五个 md5 交卷前后**逐字节不变** ⇒ ★**ISS-243 的落表成果一个字节没被本单回退掉** ★ | ★`[实测]` 交卷前后 `md5sum` 五行完全一致 (见 B5 ⑤) · ★`[实测]` `find MECH -type f -newermt "2026-11-16 18:40:00"` ⇒ 输出为空 (本轮开工后 `MECH/` 下 0 个文件被动过) · ★**★口径更正: 本行原先写的「`HW/` 全目录 326 文件 md5 清单前后 diff 为空」在 18:4x 复跑时不成立 ⇒ 实际 diff 非空 (326→329 行, 7 项) ⇒ 但那 7 项全部是别的 agent (hw-lead ISS-247 作业包 + 板侧重新生成, mtime 18:33~18:47) 写的, 不是本单写的 ⇒ 逐项归属见 B5 ⑦★** ★ |
| **1.11** | ★**本单零外发 / 零实物 / 不替老板拍板**: ★**本单不拍任何待拍项** (★V-2 / V-3 一条没拍★) ⇒ 本单不碰任何老板级决策 · ★**不碰 PCB 布线 / 布局 / 板框** (★板那一趟按老板 2026-11-11 10:07 口径继续排队★) ★ | ★`[0数据]` (★MECH 侧纯锚点重锚, 无可测物★) ★ |

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

★**逐条对 `state/issue_log.yaml` 里 ISS-246 的 `task_brief` ⑤①~⑥ (★不是抄任何交卷报告★)★

| 序 | 验收标准 (★brief 原文口径★) | 判定 | 依据 (★原样输出见 B5 对应编号★) |
|---|---|---|---|
| **⑤①** | ★**`python3 MECH/check_demo_struct_truth.py` ⇒ rc=0 · 23/23** ★ | ★**通过** ★ | ★**本机实跑 ⇒ `RC=0` · 「【结论】23/23 组检查通过 \| FAIL 0 组」** ★ (★B5 ①★) · ★**其中 G5b = [OK]** (★「6 个硬保护文件 + 2 个台账管理真源 全部一致」★) · ★**C21 = [OK]** (★「对上 = [网表 ← 台账 (ISS-243), 脚表 ← 台账 (ISS-243)]」★) ★ |
| **⑤②** | ★**`python3 MECH/check_demo_struct_truth.py --selftest` ⇒ rc=0 · 14/14** (★反向用例一条不许删★) ★ | ★**通过** ★ | ★**本机实跑 ⇒ `RC=0` · 「反向用例: 14/14 抓到了」** ★ (★B5 ②★) · ★**14 条一条没少, 且 ★反向11 现在动态读出的就是 ISS-243 那版 (`611c3ba3…`)★ —— 不是写死的旧值★** ★ |
| **⑤③** | ★**反向自证 (必做): 在 `/tmp` 沙盒里把 §3.1 锚点改回旧 md5 (`34132f7e…`) ⇒ G5b/C21 那 2 组必须重新红 ⇒ 装回去 ⇒ 又绿 ⇒ 证明这两组不是摆设** ★ | ★**通过** ★ | ★**沙盒三步已在盘上 (`/tmp/iss246_mech/stepA.log` / `stepB.log` / `stepC.log` ⇒ ★本轮已各拷一份留档到 `HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_step{A,B,C}.log`★) ★**A 绿 (23/23 · FAIL 0) → B 回滚锚点 ⇒ G5b + C21 真红 (21/23 · FAIL 2) → C 装回 ⇒ 又绿 (23/23 · FAIL 0)** ★ (★B5 ③ 引用原样输出★) ★**真盘一个字节没动** (★沙盒在 `/tmp/iss246_mech/sandbox/` 里, 已按纪律清理★) ★ |
| **⑤④** | ★**`python3 state/merge.py && python3 state/gate_check.py` ⇒ rc=0** ★ | ★**通过** ★ | ★**本机实跑 ⇒ `merge` ⇒ 「✅ STATE.yaml 已刷新 (2026-11-16T18:47:50+08:00)」· `MERGE_RC=0` ; `gate_check` ⇒ 「【Q1 交付齐备率】 **18/18** 个必填验收块齐全」· 「mech-lead 6/6 缺: 无」· 「【Q6 硬件真源闸】 ✅ 通过 (rc=0)」· `GATE_RC=0`** ★ (★B5 ④ 原样输出★) ★ |
| **⑤⑤** | ★**`HW/` 下 5 个受保护 md5 逐字节不变: 网表 `611c3ba3…` · 脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…`** ★ | ★**通过** ★ | ★**本机 `md5sum` 5 行输出与 5 个期望值逐字节相同** ★ (★B5 ⑤★) · ★**且与落表台账 §16.4 L656/L657 的「后 (交卷)」列完全一致** ★ (★B5 ⑥★) ★ |
| **⑤⑥** | ★**分片走 `python3 state/frag_write.py --agent mech-lead ...` 原子写 (★不许手改 yaml★)** ★ | ★**通过** ★ | ★**本单只用 `python3 state/frag_write.py --agent mech-lead --add-artifact ×2 --add-claim ×5 --add-need ×1` ⇒ 回显「[frag_write] ✅ mech.yaml 已原子更新 → 再跑 python3 state/merge.py」· `RC=0`** ★ · ★**`state/fragments/mech.yaml` 由 334838 B → 338263 B (mtime 13:06:48 → 18:47:17), 走 tmp+fsync+os.replace 原子替换, 全程没碰 `open(p,"w")` / 没手改 yaml** ★ |
| **④-1** | ★**改 §3.1 锚点那两条的 `md5` / `prev_md5` / `by` / `landed_at`** ★ | ★**通过** ★ | ★**已在盘上 (★上一轮 17:43 落的, mtime `2026-11-16 17:43:28`★): 网表 `md5`=`611c3ba3db3dc7de7213063375b96d01` / `prev_md5`=`34132f7e40a241e1fae1476be0eafbd5` / `by`=`ISS-243` / `landed_at`=`2026-11-16 15:45:45`; 脚表 `md5`=`ef436a37412ac9b6eac3c9f41f1edca4` / `prev_md5`=`b21b743a7702d30729f0d653c15392df` / `by`=`ISS-243` / `landed_at`=`2026-11-16 15:45:45` ★ ⇒ ★**与盘上真值 + 落表台账逐字相同** ★ (★B5 ⑤⑥ + B6 复现命令★) ★ |
| **④-2** | ★**追加一条 §3.1 留痕行 (★追加式 ⇒ 历史行一个字不改★)**: 记清 跳数 / 谁改的 / 哪个单号 / 新旧 md5 / 复现命令 ★ | ★**通过** ★ | ★**§3.1 **R-04** 行在位 (★R-01 / R-02 / R-03 历史行逐字未动★) ⇒ 内容含 跳数「第 3 跳重锚」/ 谁改的「hw-lead」/ 单号「ISS-243」/ 新旧 md5 两组 / 复现命令 3 条 (`md5sum` + 门禁 + `--selftest`)★ ⇒ ★**门禁 G8「留痕在场」判 [OK] ⇒ 删留痕就会红 (反向14 已自证)★** ★ |
| **④-3** | ★**三条不许动的**: ① G5b / C21 的判据逻辑 ② §2 第 05 行 PIN-MISMATCH 行 ③ §3.1「已修复 (留痕)」节 ★ | ★**通过** ★ | ★**① `MECH/check_demo_struct_truth.py` md5 `fa9b59e593a13408ad9505d986276f63` 交卷前后逐字节不变 (★本轮实测 + 与 brief 给的基准值同★) ⇒ 判据逻辑一个字节没动★ · ② §2 54 行全覆盖 (门禁 G6: 「表内 54 行 / 应 54; 缺项号 = 无」) + 第 05 行判定 = ✅ PASS 且备注带 ISS-220/落表 (门禁 G8) ⇒ ★**行没删★** · ③ §3.1 已修复节在位且列着 4 条 (门禁 G8 回读确认) ⇒ ★**节没删★** ★ |
| **⑥-边** | ★**边界 (逐条自证)**: 零落表 / 零外发 / 不许碰 PCB 布线布局板框 / 不许碰 `HW/` 下任何文件 / 不许碰 SW 分片 SW 台账 / 不许改判据逻辑 / 不许把红灯调没 / 不改 `PROJECT_TRACKER.md` §0 / 不替老板拍板 / `state/issue_log.yaml` 不自改 ★ | ★**通过** ★ | ★**10 条逐条见 B6 (★含 `HW/` 全目录 326→329 文件 md5 清单逐行 diff 的归属说明: 3 个新增 + 4 个变更是 ★**别的 agent (hw-lead / main)★** 在 18:33~18:39 写的, ★**不是本单写的**★; 本单 `MECH/` 下 mtime > 18:40 的文件数 = **0**★) ★ |

★**B2 小结**: ★**①~⑥ 六条验收标准全部通过 (6/6 通过 · 0 不通过 · 0 未验)**, ★**没有一条是「未验」** ★ ⇒ ★**本单可以交 main verify** ★

---

## B3 证据分级 (实测 / 官方 / 推算 / 0数据)

★**证据标签定义**: ★**`[实测]`** = ★本机实跑 / 本机文件实读 (可复现)★ · ★**`[官网]`** = ★厂商官方文档原文 (本机缓存的 PDF/TXT 实读)★ · ★**`[媒体]`** = ★第三方媒体/公开报道★ · ★**`[推算]`** = ★设计态几何/公差/功耗按公式推导 (无实物)★ · ★**`[0数据]`** = ★本机零数据 / 零实物 / 无外部来源★

| 序 | 命题 | 证据等级 | 证据来源 (★可复现路径★) |
|---|---|---|---|
| **E-01** | ★**`MECH/check_demo_struct_truth.py` 交卷时 rc=0 · 23/23 组检查通过 · FAIL 0 组** ★ | ★**`[实测]`** ★ | ★**本机实跑 `python3 MECH/check_demo_struct_truth.py` ⇒ 末行「【结论】23/23 组检查通过 \| FAIL 0 组」· `RC=0`** ★ (★B5 ① 原样输出★) ★ |
| **E-02** | ★**`--selftest` rc=0 · 14/14 反向用例全抓到 (一条没删)** ★ | ★**`[实测]`** ★ | ★**本机实跑 `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ 末行「反向用例: 14/14 抓到了」· `RC=0`** ★ (★B5 ② 原样输出★) ★ |
| **E-03** | ★**反向自证成立: G5b + C21 两组跟着盘上真值走, 不是摆设** ★ | ★**`[实测]`** ★ | ★**沙盒三步 (`/tmp/iss246_mech/sandbox/`, 真盘零写入): stepA 23/23 FAIL 0 → stepB (锚点回滚到 ISS-233 版) 21/23 **FAIL 2 且红组恰是 G5b + C21** → stepC 23/23 FAIL 0** ★ ⇒ ★**原样输出已留档 `HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_step{A,B,C}.log`** ★ (★B5 ③★) ★ |
| **E-04** | ★**§3.1 锚点现值 (网表 `611c3ba3db3dc7de7213063375b96d01` / 脚表 `ef436a37412ac9b6eac3c9f41f1edca4`, by=`ISS-243`, landed_at=`2026-11-16 15:45:45`) 与盘上真值逐字节一致** ★ | ★**`[实测]`** ★ | ★**本机 `md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv` ⇒ 与锚点值相同 (★B5 ⑤★) + ★**本机 `grep` 逐行读 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `source_ledger.entries` L110~L119** ★ ★ |
| **E-05** | ★**落表凭据四项 (落表单号 / 文件名 / 新 md5 / 旧 md5) 在同一行齐全 (★C21 判据 ②③④⑤ 全过★)** ★ | ★**`[实测]`** ★ | ★**本机 `sed -n '656p;657p' HW/SCHEMATIC_LANDING_V1_LANDED.md` ⇒ L656 网表 `34132f7e…`→`611c3ba3…` (★只 L44/L45 两行★) · L657 脚表 `b21b743a…`→`ef436a37…` (★只 L132/L133 两行★)** ★ (★B5 ⑥ 原样输出★) ★ |
| **E-06** | ★**`C_REGN` = 4.7µF ±10% (10V) 是 TI 官方硬要求** (★落表合法、不是拍脑袋★) ★ | ★**`[官网]`** ★ | ★**TI BQ25896 (SLUSC76C) §Pin Functions · pin22 REGN 行原文: 「Internally, REGN is connected to the cathode of the boost-strap diode. ★**Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND**★. The capacitor should be placed close to the IC. REGN also serves as bias rail of TS pin.」** ★ ⇒ ★**本机缓存实读 `state/.cache_iss243/bq25896.txt` L340~L342** ★ (★本单只转述该原文, 未重新下载★) ★ |
| **E-07** | ★**落表时刻 = 2026-11-16 15:45:45 (不是编的)** ★ | ★**`[实测]`** ★ | ★**本机 `stat -c '%y' HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv` ⇒ `15:45:45.577` / `15:45:45.673` / `15:45:45.787` (取到秒 = `15:45:45`, 与 R-02 `05:18:41` / R-03 `06:48:38` 同口径)★** ★ |
| **E-08** | ★**门禁脚本没被改过 ⇒ 是锚点过期不是「红灯被调没」** ★ | ★**`[实测]`** ★ | ★**本机 `md5sum MECH/check_demo_struct_truth.py` ⇒ `fa9b59e593a13408ad9505d986276f63` (★与 brief 给的基准值同★) · mtime `2026-11-16 03:55:42` (★早于落表 15:45:45 ⇒ 脚本在落表前就定型了★)** ★ |
| **E-09** | ★**`HW/` 5 个受保护件 md5 交卷前后逐字节不变** ★ | ★**`[实测]`** ★ | ★**本机 `md5sum` 5 行 (★B5 ⑤★) ⇒ 网表 `611c3ba3…` / 脚表 `ef436a37…` / BOM `2a730574…` / 板 `611b869e…` / `.kicad_pro` `3e504d2b…`, 5 个全与期望值相同** ★ |
| **E-10** | ★**本轮 (18:40 起) `MECH/` 下 0 个文件被改** ★ | ★**`[实测]`** ★ | ★**本机 `find MECH -type f -newermt "2026-11-16 18:40:00"` ⇒ 输出为空 (count = 0)** ★ · ★**`MECH/HW_CROSS_REVIEW_TRIAGE.md` md5 本轮开工前后都是 `a4900225e102f2ee1ff52ef55b56458d` (★第 3 跳落表是上一轮 17:43 做的, 本轮只如实记「已落」★)** ★ |
| **E-11** | ★**`merge.py` rc=0 · `gate_check.py` rc=0 · Q1 18/18 · Q6 硬件真源闸 rc=0** ★ | ★**`[实测]`** ★ | ★**本机实跑两条命令 (★B5 ④ 原样输出★) ⇒ 「✅ STATE.yaml 已刷新」·「【Q1 交付齐备率】 18/18」·「mech-lead 6/6 缺: 无」·「【Q6 硬件真源闸】 ✅ 通过 (rc=0)」· `MERGE_RC=0` / `GATE_RC=0`** ★ |
| **E-12** | ★**分片走原子写, 没手改 yaml** ★ | ★**`[实测]`** ★ | ★**本机实跑 `python3 state/frag_write.py --agent mech-lead --add-artifact ×2 --add-claim ×5 --add-need ×1` ⇒ 回显「✅ mech.yaml 已原子更新」· `RC=0`; ★**落盘后本机回读 YAML 确认 2 artifact + 5 claim (`iss246_mech_*`) + 1 need (`iss246_mech_handoff_review` → main) 全部在位** ★ ★ |
| **E-13** | ★**本单零外发 (不发邮件/询价/问询/采购)** ★ | ★**`[0数据]`** ★ | ★**本单零外部通信动作** (★未调用任何邮件/消息/外发工具; 老板 2026-11-11 19:31 + 2026-11-12 02:02 口径: 不再发信, 缺口自己查资料★) ⇒ ★**本单无外部缺口 ⇒ 无需降级方案** ★ ★ |
| **E-14** | ★**本单零实物 (板与样件不在本机 ⇒ 所有 [实测] 都是「本机脚本实跑 / 本机文件实读」)** ★ | ★**`[0数据]`** ★ | ★**本单零实物测量、零样件、零仪器读数** ★ |
| **E-15** | ★**门禁 23 组里的几何/公差/功耗结论本身是设计态推导, 不是实物测量** (★继承门禁自带的口径提醒★) ★ | ★**`[推算]`** ★ | ★**门禁输出自带口径提醒: 「全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**」** ★ ★ |
| **E-16** | ★**`HW/` 全目录 md5 清单本轮非空 diff 的归属: 3 新增 + 4 变更全是别的 agent 写的, 不是本单** ★ | ★**`[实测]`** ★ | ★**本机 `find HW -type f -print0 \| sort -z \| xargs -0 md5sum` (★★避开文件名含空格的坑, 不用裸 `xargs md5sum`★) ⇒ 清单 326 → 329 行; diff 出的 7 项 mtime 分别为 `18:33:20` (`HW/check_iss247_f1_landed.py` ⇒ ISS-247 hw-lead 的门禁) · `18:37:54`/`18:39:21` (`HW/SCHEMATIC_LANDING_F1_WORKPACKET_V1.md` / `_NEXT_BATCH_V1.md` ⇒ ISS-247 hw-lead 的作业包) · `18:38:37` ×4 (`HW/PCB/_frame_reference.kicad_pcb` / `GEN_SELF_CHECK.txt` / `LAYOUT_RULES.md` / `STACKUP.md` ⇒ 板侧重新生成) ⇒ ★**全部早于或晚于本单开工且都不是我写的; 本单对 `HW/` 只读 (md5sum + grep + stat), 0 字节写入** ★ ★ |
| **E-17** | ★**本单不替老板拍任何待拍项** ★ | ★**`[0数据]`** ★ | ★**本单零拍板 (★V-2 / V-3 / V-4 / M-04 一条没碰★) · 不碰 PCB 布线/布局/板框 (★按老板 2026-11-11 10:07 口径继续排队★) · `state/issue_log.yaml` 自改 0 处 (★verify 留给 main★)** ★ |

★**证据标签统计**: ★**`[实测]` 12 条 · `[官网]` 1 条 (E-06 TI BQ25896 SLUSC76C pin22) · `[推算]` 1 条 · `[0数据]` 3 条 · `[媒体]` 0 条** ★ ⇒ ★**本单没有一条结论靠 `[媒体]` 二手报道撑着** ★

---

## B4 接口取值声明 (interface_claims)

★**格式照 `HANDOFF/2026-11-16_sw-lead_ISS245_SW侧H1重锚第4跳.md` 的 B4 表 (序 / key / 取值声明 / 证据等级)★**
★**★本单这 5 条已用 `python3 state/frag_write.py --agent mech-lead --add-claim` 原子写进 `state/fragments/mech.yaml` 的 `interface_claims` (★已回读确认在位: claims 225 → 230 条, 5 条 key 全是 `iss246_mech_*` 前缀★)★ ★

| 序 | key | 取值声明 | 证据等级 |
|---|---|---|---|
| **I-1** | `iss246_mech_md5_anchor_netlist` | ★**MECH 侧 §3.1 锚点 (网表 `HW/netlist_v1.csv`) = `611c3ba3db3dc7de7213063375b96d01`** (★`by`=ISS-243 · `prev_md5`=`34132f7e40a241e1fae1476be0eafbd5` · `landed_at`=`2026-11-16 15:45:45`★) ⇒ ★**盘上真值, 不是抄来的** ★ | ★`[实测]` ★ |
| **I-2** | `iss246_mech_md5_anchor_pins` | ★**MECH 侧 §3.1 锚点 (脚表 `HW/netlist_v1_pins.csv`) = `ef436a37412ac9b6eac3c9f41f1edca4`** (★`by`=ISS-243 · `prev_md5`=`b21b743a7702d30729f0d653c15392df` · `landed_at`=`2026-11-16 15:45:45`★) ⇒ ★**盘上真值** ★ | ★`[实测]` ★ |
| **I-3** | `iss246_mech_md5_hop_count` | ★**MECH 侧 md5 锚点重锚跳数 = 第 3 跳** (★先例: ISS-223 第 1 跳 R-02 → ISS-233 并发第 2 跳 R-03 → 本单 ISS-246 第 3 跳 R-04★) ⇒ ★**锚点 `by` 单号链 = ISS-233 → ISS-243** ★ | ★`[实测]` (★台账 §3.1 R-01~R-04 行 + 本单 R-04★) ★ |
| **I-4** | `iss246_mech_md5_landing_ticket` | ★**本次锚点挂的落表单号 = `ISS-243`** (★hw-lead 落表第 4 批, 2026-11-16 15:45:45, `C_REGN` 官方值落表★) ⇒ ★**落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 + §16.4 L656/L657 + 交接单 `HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md` 三处都在 §1 `landing_records` 里登记** ★ | ★`[实测]` (★`[官网]` 支撑落表合法性: TI BQ25896 SLUSC76C pin22「Connect a 4.7 µF (10 V rating) ceramic capacitor from REGN to analog GND」★) ★ |
| **I-5** | `iss246_mech_gate_contract` | ★**MECH 侧门禁的契约 (交卷后不变)**: `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=0 且 23/23 组检查通过且 FAIL 0 组**★; `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ ★**rc=0 且 14/14 反向用例全抓到 (一条没删)**★; ★**受保护脚本 md5 `fa9b59e593a13408ad9505d986276f63` 逐字节不变; 判据逻辑 / 阈值 / 反向用例一条没动** ★ | ★`[实测]` ★ |

★**★配套登记**: ★**本单另用 `--add-artifact` 登记 2 条交卷物 (`MECH/HW_CROSS_REVIEW_TRIAGE.md` + 本交接单) + `--add-need` 登记 1 条复核项 (`iss246_mech_handoff_review` → main) ⇒ ★**main 可直接照这 5 条 key 核对锚点, 不必读全文** ★ ★

---

## B5 验收命令原样输出 (未决项与卡点)

★**全部为本机实跑 (★不是抄任何报告★)★; ★**每段末尾的 `RC=` / `MERGE_RC=` / `GATE_RC=` 是 shell 回显的真实退出码★ ★

### ① `python3 MECH/check_demo_struct_truth.py` ⇒ rc=0 · 23/23

```
$ python3 MECH/check_demo_struct_truth.py
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
  [OK ] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)
         6 个硬保护文件 + 2 个台账管理真源 全部一致
  [OK ] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)
         台账可查 = ['HW/SCHEMATIC_LANDING_V1_LANDED.md', 'HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md', 'HANDOFF/2026-11-16_hw-lead_ISS233_21条未落表归因与拍板即落清单.md', 'HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md']; 对上 = ['HW/netlist_v1.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-243)', 'HW/netlist_v1_pins.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-243)']
  [OK ] C22   PIN-MISMATCH 独立复核 (P9 页声明 vs 网表实际 + d6 新旧口径)
         网表实读 CONN_LIGHT 22p / CONN_CAM 31p / J_CHG 10p; P9 声明 CONN_LIGHT [22] / CONN_CAM [31] / J_CHG [10]; 旧口径 0 处 / 新口径 3 处
  [OK ] G6    定性表 54 项全覆盖 (项号一个不缺) 且处置栏不留空/不写'待定'
         表内 54 行 / 应 54; 缺项号 = 无; 多余项号 = 无; 处置留空或待定 = 无
  [OK ] G6b   16 条 FAIL 每条都有明确去处 (修掉/出规格/登记 need 给 main/排队等原理图定稿)
         FAIL 行 16 条; 去处不在受控词表里的 = 无
  [OK ] G7    分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)
         实测 value = 25.00
  [OK ] G8    已修复的留痕必须在场 (PIN-MISMATCH 行 + §3.1「已修复 (留痕)」节)
         §2 行在位 (判定 = ✅ PASS, 备注带 ISS-220/落表) + §3.1 已修复节在位 (列着 ['PIN-MISMATCH', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)'])
----------------------------------------------------------------------------------------------------
【结论】23/23 组检查通过 | FAIL 0 组
口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**。
          本闸守的是 **demo 板当前成立的条目**, 不是'54 项全绿'。
          ★ 6 个 PCB 类 id 仍是 FAIL 是**正确状态** (排队等原理图定稿), 不是缺陷。
          ★ ISS-224: `PIN-MISMATCH` 是**被 ISS-220 真修好了**, 不是被调没 ⇒ 留痕在 §2 第 05 行 + §3.1。
====================================================================================================
RC=0
```

### ② `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ rc=0 · 14/14

```
$ python3 MECH/check_demo_struct_truth.py --selftest
====================================================================================================
ISS-213/224 机器门禁 —— 反向用例 (改坏任一锚点必须变红)
====================================================================================================
  ✅ 基线全绿 (23/23 组检查)
  ✅ 反向1: 板宽锚点 30.00 → 15.00 (旧板宽)                    期望红组 G4     实际红组 ['G4', 'G4b']
  ✅ 反向2: 判据 CRIT 0.60 → 0.30 (松判据)                   期望红组 G5     实际红组 ['G2.4', 'G5']
  ✅ 反向3: 新开孔 10.50 → 9.50 (退回到不合格的现口径)               期望红组 G2.2   实际红组 ['G2.2']
  ✅ 反向4: buck 耗散 0.50 → 0.15 (假装不需要金属热路)             期望红组 G2.6   实际红组 ['G2.5', 'G2.6']
  ✅ 反向5: FAIL 名单里删掉 NET-LED (把红灯调没)                  期望红组 G1b    实际红组 ['G1b']
  ✅ 反向6: 排队表里删掉 FRM-SUM (静默丢弃排队条目)                   期望红组 G3     实际红组 ['G3']
  ✅ 反向7: 板重 3.33 → 3.30 (板框真源被偷改)                    期望红组 G4     实际红组 ['G4']
  ✅ 反向8: cavity_req 4.50 → 5.00 (松硬要求)               期望红组 G5     实际红组 ['G5']
  ✅ 反向9: P9 页正文回退成 21p (PIN-MISMATCH 改回 FAIL)        期望红组 C22    实际红组 ['C22']
  ✅ 反向10: 网表 CONN_LIGHT 改回 21p (网表被回退)               期望红组 C22    实际红组 ['C22']
  ✅ 反向11: 网表 md5 锚点改回旧值 c78f9912… (锚点回滚)             期望红组 G5b    实际红组 ['G5b', 'C21']
  ✅ 反向12: 网表 md5 锚点改成台账里查不到的哈希                       期望红组 C21    实际红组 ['G5b', 'C21']
  ✅ 反向13: 落表单号改坏 (ISS-220 → ISS-999)                 期望红组 C21    实际红组 ['C21']
  ✅ 反向14: 删掉「已修复」留痕 (行 05 备注 + §3.1 整节)              期望红组 G8     实际红组 ['G8']
----------------------------------------------------------------------------------------------------
反向用例: 14/14 抓到了
RC=0
```

★**注**: ★**反向11 的「旧值 c78f9912…」是反向用例自身的测试夹具值 (比 ISS-233 版还旧一档), 不是本单锚点现值** ★ ⇒ ★**但它的效果一样: 锚点一改就红 ⇒ 证明 G5b/C21 跟着盘上真值走 (★与 B5 ③ 沙盒三步互为印证★)★ ★

### ③ 沙盒反向自证三步 (★直接引用原样输出, 本轮未重跑★)

★**三份原始日志本轮已各拷一份留档到 `HANDOFF/` (★md5 与 `/tmp/iss246_mech/step*.log` 逐字节一致★)**:
★**`HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_stepA.log` (`a1b0915e744dbf130b74acb158b8cf00`) · `_stepB.log` (`73995f6125c8b69dc889f7374dfe5167`) · `_stepC.log` (`a1b0915e744dbf130b74acb158b8cf00`)** ★
★**★沙盒位置: `/tmp/iss246_mech/sandbox/` (★真盘一个字节没动★) ⇒ ★**A 绿 → B 把 §3.1 锚点回滚到 ISS-233 那版 ⇒ G5b + C21 真红 → C 装回去 ⇒ 又绿★** ★

**★stepA (基线, 沙盒内 §3.1 锚点 = ISS-243 新值) ⇒ 绿 ★**
```
【结论】23/23 组检查通过 | FAIL 0 组
  [OK ] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)
         6 个硬保护文件 + 2 个台账管理真源 全部一致
  [OK ] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)
         台账可查 = [..., 'HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md']; 对上 = ['HW/netlist_v1.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-243)', 'HW/netlist_v1_pins.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-243)']
```

**★stepB (★把 §3.1 锚点回滚到 ISS-233 那版 `34132f7e…` / `b21b743a…`★) ⇒ ★红, 且红的恰是 G5b + C21 这 2 组★**
```
  [FAIL] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)
         HW/netlist_v1.csv: 611c3ba3db3dc7de7213063375b96d01 != 34132f7e40a241e1fae1476be0eafbd5; HW/netlist_v1_pins.csv: ef436a37412ac9b6eac3c9f41f1edca4 != b21b743a7702d30729f0d653c15392df
  [FAIL] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)
         HW/netlist_v1.csv: 盘上 md5 611c3ba3db3dc7de7213063375b96d01 != 锚点登记 34132f7e40a241e1fae1476be0eafbd5 (真源被换了或锚点过期); HW/netlist_v1_pins.csv: 盘上 md5 ef436a37412ac9b6eac3c9f41f1edca4 != 锚点登记 b21b743a7702d30729f0d653c15392df (真源被换了或锚点过期)
----------------------------------------------------------------------------------------------------
【结论】21/23 组检查通过 | FAIL 2 组
```

**★stepC (★把 §3.1 锚点装回 ISS-243 那版★) ⇒ ★又绿★**
```
  [OK ] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)
         6 个硬保护文件 + 2 个台账管理真源 全部一致
  [OK ] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)
         对上 = ['HW/netlist_v1.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-243)', 'HW/netlist_v1_pins.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-243)']
----------------------------------------------------------------------------------------------------
【结论】23/23 组检查通过 | FAIL 0 组
```

★**⇒ 绿 → 红 → 绿 三步齐 ⇒ G5b / C21 这 2 组不是摆设 (★真盘始终 23/23 绿, 沙盒里才红★)★ ★

### ④ `python3 state/merge.py && python3 state/gate_check.py` ⇒ rc=0 · Q1 18/18

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-16T18:47:50+08:00)
   产出 357 | 阻塞 43 (高危 33) | 未闭合需求 202 | 冲突 0 | 健康度 red
MERGE_RC=0

$ python3 state/gate_check.py
==========================================================================
项目总工质量门 · 3 个子模块总工交付看板
==========================================================================

【Q1 交付齐备率】 18/18 个必填验收块齐全
   hw-lead    6/6  缺: 无   交接单: 2026-11-16_hw-lead_ISS247_F1落表作业包v1.md
   sw-lead    6/6  缺: 无   交接单: 2026-11-16_sw-lead_ISS248_reverse-demo演示段口径对齐.md
   mech-lead  6/6  缺: 无   交接单: 2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md

【Q2 证据分级率】 3/3 个总工的交付做了证据分级
   hw-lead    标签: ['实测', '官方', '推算', '0数据']
   sw-lead    标签: ['实测', '官方', '推算', '0数据']
   mech-lead  标签: ['实测', '官方', '推算', '0数据']

【Q3 接口声明率】 全员 interface_claims 共 664 条 (目标 ≥3 条/总工 → 冲突才能自动检出)
   hw-lead    242 条
   sw-lead    192 条
   mech-lead  230 条

【Q4 需求闭环率】
   问方视角 (我的需求被别人答了): 76/355  ← 与 merge.py 口径一致
   答方视角 (我登记的答复): 101 条, 其中 62 条真对上了别人的需求 key
   hw-lead    被答 27/122 | 我答 41 条(有效 31) | 产出 112 | 阻塞 7
   sw-lead    被答 12/83 | 我答 20 条(有效 5) | 产出 116 | 阻塞 15
   mech-lead  被答 37/150 | 我答 40 条(有效 26) | 产出 119 | 阻塞 12
   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: 0 条  ← 需人工判定, 也有可能是 waiting_on 标错
   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 81 条 | **全局 72 条** (含 main)
   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 202 条**
   ✅ 与 merge.py 自对账一致 (等外部 72 / 等总工 202)
   ⚠️ 自闭合 (自己答自己 = to 写错): 0 条
   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): 11 个
      q1_latency_scope: 发起方 ['main', 'sw-lead']
      q4_battery_scope: 发起方 ['main', 'hw-lead', 'mech-lead']
      q17_display_fps: 发起方 ['main', 'sw-lead']
      q18_highspeed_cam: 发起方 ['main', 'sw-lead']
      q16_aspect_ratio: 发起方 ['main', 'hw-lead', 'mech-lead']

【Q5 硬指标覆盖】 1/3 个总工报出了 ≥3 类硬指标数字
   hw-lead    0/5 类: []
   sw-lead    5/5 类: ['功耗(W)', '皮肤温度(°C)', '镜腿/镜脚厚度(mm)', '端到端延迟(ms)', 'FCCSP 球间距(pitch)']
   mech-lead  1/5 类: ['镜腿/镜脚厚度(mm)']

【Q6 硬件真源闸】 HW pinout 真源闸: ✅ 通过 (rc=0)
   全部检查项通过

【缺口清单】(可直接转成下一轮派活项) —— 3 条
   · hw-lead: 76 条需求确实还没人答 (等另一个总工)
   · sw-lead: 46 条需求确实还没人答 (等另一个总工)
   · mech-lead: 76 条需求确实还没人答 (等另一个总工)

==========================================================================
GATE_RC=0
```

★**注 1**: ★**Q4 的 3 条缺口 (76/46/76) 是全项目层面的存量需求未闭合, ★**不是本单造成的**★ (★本单只新增 1 条 need 给 main = 复核项★) ★ · ★**Q1 18/18 是硬指标, 交卷后复跑仍是 18/18 (★上面这份就是分片写完后跑的★)★ ★
★**注 2 (★防误读, main 请看★)**: ★**Q5 里 mech-lead 从「1/5 类」变成「5/5 类」是 ★**假阳性★** —— 原因是 ★**本单把上面这段 gate_check 原样输出贴进了交接单, 而 sw-lead 那行恰好把 5 类硬指标名全列了出来 ('功耗(W)' / '皮肤温度(°C)' / '镜腿/镜脚厚度(mm)' / '端到端延迟(ms)' / 'FCCSP 球间距(pitch)') ⇒ gate_check 的正则扫全文就命中了 ⇒ ★**本单 (纯锚点重锚) 实质新增的硬指标 = 0 条** ★ ⇒ ★**请 main 别把这条当成「mech-lead 补齐了硬指标」★** ★

### ⑤ `md5sum` 5 个受保护件 (交卷前后逐字节不变)

```
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
611c3ba3db3dc7de7213063375b96d01  HW/netlist_v1.csv
ef436a37412ac9b6eac3c9f41f1edca4  HW/netlist_v1_pins.csv
2a7305741134788dfee9f13f34c656b4  HW/BOM_v1.csv
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro
RC=0
```

★**对账**: ★**5 行全与 brief 给的期望值逐字节相同** (网表 `611c3ba3…` / 脚表 `ef436a37…` / BOM `2a730574…` / 板 `611b869e…` / `.kicad_pro` `3e504d2b…`) ★
★**★另附受保护脚本 md5 (★也必须不变★)★**: ★**`MECH/check_demo_struct_truth.py` = `fa9b59e593a13408ad9505d986276f63`** ★ ⇒ ★**与 brief 给的基准值同 ⇒ 判据逻辑一个字没动★** ★

### ⑥ 落表台账 §16 L656/L657 逐行命中

```
$ sed -n '656p;657p' HW/SCHEMATIC_LANDING_V1_LANDED.md
| ★**`HW/netlist_v1.csv`** ★ | `34132f7e40a241e1fae1476be0eafbd5` | `611c3ba3db3dc7de7213063375b96d01` | ★**是 (★只有 L44/L45 两行★)** ★ |
| ★**`HW/netlist_v1_pins.csv`** ★ | `b21b743a7702d30729f0d653c15392df` | `ef436a37412ac9b6eac3c9f41f1edca4` | ★**是 (★只有 L132/L133 两行★)** ★ |
RC=0
```

★**⇒ C21 要的四项 (★落表单号 `ISS-243` / 文件名 / 新 md5 / 旧 md5★) 在同一行齐全 ⇒ 门禁 C21 判 ②③④⑤ 全过** ★
★**⇒ 与 B5 ⑤ 的盘上现值逐字一致 (★`611c3ba3…` / `ef436a37…`★) ⇒ 锚点 = 台账 = 盘上 三方一致** ★

### ⑦ `HW/` 全目录 md5 清单逐行 diff (★归属说明: 非空, 但不是本单写的★)

```
$ find HW -type f -print0 | sort -z | xargs -0 md5sum > /tmp/iss246_mech/hw_manifest_now2.txt
$ diff /tmp/iss246_mech/hw_manifest_before.txt /tmp/iss246_mech/hw_manifest_now2.txt
18a19
> 5a62b02ef69a7168fac815e60c84bee0  HW/check_iss247_f1_landed.py
112,113c112,113
< be964003598ac3bd630d44f13f707579  HW/PCB/_frame_reference.kicad_pcb
< 16d7bf42cab31e7d58c41b35831cc6bc  HW/PCB/GEN_SELF_CHECK.txt
---
> 9c9ec38fb12af2c71e85060c8caa9709  HW/PCB/_frame_reference.kicad_pcb
> 481280707fe14cf903837fd5f83df04a  HW/PCB/GEN_SELF_CHECK.txt
150c151
< a8176d8ec0e26eb9b81bf7381825f4c1  HW/PCB/LAYOUT_RULES.md
---
> def24ea161a59b8476e18493ed43bab2  HW/PCB/LAYOUT_RULES.md
254c255
< 813e777ad0a35fb62807c4f1a36db2be  HW/PCB/STACKUP.md
---
> 936ab65a2b25f00a8fee031f300c7daa  HW/PCB/STACKUP.md
308a310,311
> 6e611473c303081bece8571156c5441e  HW/SCHEMATIC_LANDING_F1_WORKPACKET_V1.md
> 585718fbf39a9ad191469363c4e02216  HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md
```

★**★口径更正 (★上一轮 B1 §1.10 写的是「HW/ 全目录 diff 为空」—— 本轮实跑发现不成立, 据实更正★)★**
★**清单 326 → 329 行, diff 出 7 项 (★3 新增 + 4 变更★), 逐项归属 (★按 mtime★)**:

| 项 | mtime | 归属 | 是谁写的 |
|---|---|---|---|
| `HW/check_iss247_f1_landed.py` | 18:33:20 | ★**ISS-247** ★ | ★**hw-lead** (★该单的「机器门禁」交卷物★) ★ |
| `HW/SCHEMATIC_LANDING_F1_WORKPACKET_V1.md` | 18:37:54 (★18:47:47 被重写过一次★) | ★**ISS-247** ★ | ★**hw-lead** (★F1 落表作业包★) ★ |
| `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` | 18:39:21 | ★**ISS-247** ★ | ★**hw-lead** (★下一批落表清单★) ★ |
| `HW/PCB/_frame_reference.kicad_pcb` | 18:38:37 | ★**板侧重新生成** ★ | ★**hw-lead / main 的板侧作业 (★不是本单★)** ★ |
| `HW/PCB/GEN_SELF_CHECK.txt` | 18:38:37 | ★**板侧重新生成** ★ | ★**同上★** ★ |
| `HW/PCB/LAYOUT_RULES.md` | 18:38:37 | ★**板侧重新生成** ★ | ★**同上★** ★ |
| `HW/PCB/STACKUP.md` | 18:38:37 | ★**板侧重新生成** ★ | ★**同上★** ★ |

★**⇒ 这 7 项全部是 ★**别的 agent (hw-lead / main) 在 18:33~18:47 写的★**, ★**不是本单写的**★ ⇒ ★**本单对 `HW/` 的写入 = 0 字节 (只读: md5sum / grep / sed / stat)★** ★
★**★本单的硬证据 (比目录 diff 更强)★**: ★**① 5 个受保护件 md5 交卷前后逐字节不变 (B5 ⑤) ★② `find MECH -type f -newermt "2026-11-16 18:40:00"` ⇒ 输出为空 (★本单开工后 `MECH/` 下 0 个文件被动过★) ★③ `MECH/HW_CROSS_REVIEW_TRIAGE.md` md5 本轮开工前后都是 `a4900225e102f2ee1ff52ef55b56458d` (★第 3 跳落表是上一轮 17:43 做的★)★** ★

### ⑧ 未决项与卡点

★**本单零卡点 (★不需要谁回答什么就能交卷★)** ⇒ ★**只留 1 条给 main 的复核项 (已登记进分片 `needs_from`, key = `iss246_mech_handoff_review`)** ★

| 序 | 卡点 | 要谁回答 | 状态 |
|---|---|---|---|
| **N-1** | ★**ISS-246 交卷待 main 复核: 交卷单 6 段 + 分片 + merge/gate_check 输出** ★ | ★**main** ★ | ★**已登记 (★`state/fragments/mech.yaml` `needs_from` ★)★ · ★**verify 由 main 做 (★本单不自签 `state/issue_log.yaml`★)** ★ |

★**★本单没有等外部 (老板/原厂/JBD) 的缺口 ⇒ 不需要降级方案★** ★

---

## B6 边界审计 (自证复现命令)

### B6.1 本单动过的文件 (★3 件 + 3 份沙盒日志留档★)

| 序 | 文件 | 动了什么 | 什么没动 |
|---|---|---|---|
| **1** | ★**`HANDOFF/2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md`** (★本交接单本身★) | ★**B2~B6 + 附交卷物清单逐段填完; B1 §1.10 的口径更正 (★见 B5 ⑦★)** ★ | ★**B0 一句话 / B1 结论摘要 11 行没动 (★上一轮填的★)** ★ |
| **2** | ★**`state/fragments/mech.yaml`** | ★**走 `python3 state/frag_write.py --agent mech-lead` 原子写: +2 artifact (交卷单 + `MECH/HW_CROSS_REVIEW_TRIAGE.md`) +5 claim (`iss246_mech_*`) +1 need (`iss246_mech_handoff_review` → main) ⇒ 334838 B → 338263 B** ★ | ★**已有 119 artifact / 225 claim / 149 need / 40 answer 一条没改没删★ (只追加)★ · ★**没手改 yaml, 没用 `open(p,"w")`★** ★ |
| **3** | ★**`state/STATE.yaml`** (★`merge.py` 自动刷新, ★非我手改★) | ★**由 `python3 state/merge.py` 从 4 个分片合并生成 (★唯一合法写入路径★)** ★ | ★**`state/issue_log.yaml` 自改 0 处 (★verify 留给 main★)★** ★ |
| **4** | ★**`HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_stepA.log`** | ★**沙盒 stepA 原样输出留档 (★`a1b0915e744dbf130b74acb158b8cf00`★)** ★ | ★**`/tmp` 原件未动 (★留作可追溯★)** ★ |
| **5** | ★**`HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_stepB.log`** | ★**沙盒 stepB 原样输出留档 (★`73995f6125c8b69dc889f7374dfe5167`★)** ★ | ★**同上★** ★ |
| **6** | ★**`HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_stepC.log`** | ★**沙盒 stepC 原样输出留档 (★`a1b0915e744dbf130b74acb158b8cf00`★)** ★ | ★**同上★** ★ |

★**★★本轮 (18:40 起) `MECH/` 下 0 个文件被改动 ⇒ 也就是 ★**「§3.1 第 3 跳重锚」是上一轮 (mtime 17:43) 做的, 本轮只如实记「已落」, 一个字没动**★ ⇒ ★**交卷物 3 件清单里的 `MECH/HW_CROSS_REVIEW_TRIAGE.md` 属于【上一轮已落的成果】, 本轮 0 改动**★ ★
★**★硬证据: ★**`find MECH -type f -newermt "2026-11-16 18:40:00"` ⇒ 输出为空 (count = 0)★** · ★**`MECH/HW_CROSS_REVIEW_TRIAGE.md` md5 本轮开工前后都是 `a4900225e102f2ee1ff52ef55b56458d`★** ★

### B6.2 边界逐条自证 (10 条)

| 序 | 边界条款 | 自证 | 判定 |
|---|---|---|---|
| **BL-1** | ★**零落表**: 网表/脚表/BOM/板 一个字都不许改 ★ | ★**5 个受保护件 md5 交卷前后逐字节不变 (B5 ⑤)★ + ★**`MECH/` 下 18:40 后 0 个文件被动过★ + ★**本单对 `HW/` 只读 (md5sum/grep/sed/stat), 0 字节写入★** ★ | ★**通过** ★ |
| **BL-2** | ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 缺口自己查★) ★ | ★**本单零外部通信动作** (★未发任何邮件/询价/问询/采购; 无外部缺口 ⇒ 无需降级方案★) ★ | ★**通过** ★ |
| **BL-3** | ★**不许碰 PCB 布线 / 布局 / 板框** (★按老板 2026-11-11 10:07 口径继续排队★) ★ | ★**本单零 PCB 文件写入; 板 `611b869e…` / `.kicad_pro` `3e504d2b…` 逐字节不变; 6 个 PCB 类 id 仍处于「排队等原理图定稿」的正确 FAIL 状态 (门禁 G3/G3b [OK])★** ★ | ★**通过** ★ |
| **BL-4** | ★**不许碰 `HW/` 下任何文件** (★只读用来核 md5★) ★ | ★**本单对 `HW/` 只有只读命令 (md5sum / grep / sed -n / stat / find); 5 个受保护件 md5 不变; 全目录 diff 的 7 项逐项归属到别的 agent (B5 ⑦)★** ★ | ★**通过** ★ |
| **BL-5** | ★**不许碰 SW 分片 / SW 台账** (★那是 ISS-245 sw-lead 的活★) ★ | ★**本单 0 次写 `state/fragments/sw.yaml`; `SW/` 下 0 文件写入; ★**没有把 SW 侧的 md5 锚点写进 MECH 分片 (两个域各写各的 key: `iss245_sw_*` vs `iss246_mech_*`)★** ★ | ★**通过** ★ |
| **BL-6** | ★**不许改判据逻辑 / 不许把红灯调没** ★ | ★**`MECH/check_demo_struct_truth.py` md5 `fa9b59e593a13408ad9505d986276f63` 交卷前后不变★ + ★**阈值未松 (cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00 — 门禁 G5 [OK])★ + ★**FAIL 名单仍是 16 条 (G1/G1b [OK])★ + ★**反向用例 14/14 一条没删 (B5 ②)★** ★ | ★**通过** ★ |
| **BL-7** | ★**不改 `PROJECT_TRACKER.md` §0 锁死表** ★ | ★**本单 0 次写 `PROJECT_TRACKER.md` (mtime 未变)★** ★ | ★**通过** ★ |
| **BL-8** | ★**不替老板拍板** ★ | ★**本单零拍板 (★V-2 / V-3 / V-4 / M-04 一条没碰★) · 提给 main 的只有 1 条复核项 (不是决策项)★** ★ | ★**通过** ★ |
| **BL-9** | ★**`state/issue_log.yaml` 不自改** (★verify 留给 main★) ★ | ★**本单 0 次写 `state/issue_log.yaml` (★ISS-246 的 status 仍是 `fixing` / `verify_result: null` / `verify_date: null` ⇒ 等 main 落 verified★)** ★ | ★**通过** ★ |
| **BL-10** | ★**不许碰别人的分片** ★ | ★**只写 `state/fragments/mech.yaml` (自己的); `hw.yaml` (mtime 18:46:05) / `sw.yaml` (18:38:10) / `pm.yaml` (04:15:57) 都不是本单写的** ★ | ★**通过** ★ |

### B6.3 自证复现命令 (★main 可原样跑★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 门禁 (23/23)
python3 MECH/check_demo_struct_truth.py ; echo "RC=$?"

# ② 反向用例 (14/14)
python3 MECH/check_demo_struct_truth.py --selftest ; echo "RC=$?"

# ③ 沙盒反向自证三步 (★已留档, 可直接对账★)
md5sum HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_step*.log
grep -n "FAIL" HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_stepB.log   # ⇒ 恰 2 个 FAIL (G5b / C21)
grep -n "【结论】" HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_step*.log  # ⇒ 23/23 → 21/23 → 23/23

# ④ 分片 + 状态源
python3 state/merge.py ; echo "MERGE_RC=$?"
python3 state/gate_check.py ; echo "GATE_RC=$?"      # ⇒ Q1 18/18

# ⑤ 5 个受保护件 + 受保护脚本 md5
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       MECH/check_demo_struct_truth.py

# ⑥ 落表台账 L656/L657 逐行
sed -n '656p;657p' HW/SCHEMATIC_LANDING_V1_LANDED.md

# ⑦ §3.1 锚点 + R-04 留痕 (只读)
grep -n "611c3ba3db3dc7de7213063375b96d01\|ef436a37412ac9b6eac3c9f41f1edca4\|R-04" \
     MECH/HW_CROSS_REVIEW_TRIAGE.md

# ⑧ 分片里本单的 5 条 claim + 1 条 need
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('state/fragments/mech.yaml'))
for c in d['interface_claims']:
    if str(c.get('key','')).startswith('iss246'): print(c['key'], '=', c['value'])
for n in d['needs_from']:
    if str(n.get('key','')).startswith('iss246'): print(n['key'], '->', n['to'])
PY

# ⑨ 本轮 MECH/ 零改动
find MECH -type f -newermt "2026-11-16 18:40:00" ; echo "(空 ⇒ 0 改动)"
```

### B6.4 沙盒清理

★**已清**: ★**`/tmp/iss246_mech/sandbox/` 整个目录已删 (★沙盒副本不留★) · 三份原样输出已留档到 `HANDOFF/` (★md5 与原件逐字节一致★) · ★**真盘一个字节没动** ★ ★

---

## ★附 · 交卷物清单 (3 件)

| 序 | 交卷物 | 路径 | 本轮状态 | 证据 |
|---|---|---|---|---|
| **1** | ★**§3.1 锚点重锚 (第 3 跳)** ★ | ★**`MECH/HW_CROSS_REVIEW_TRIAGE.md`** ★ | ★**★上一轮已落 (mtime `2026-11-16 17:43:28`) · 本轮 0 改动★** ★ | ★**md5 `a4900225e102f2ee1ff52ef55b56458d` 本轮前后不变 · `find MECH -newermt 18:40` ⇒ 空** ★ |
| **2** | ★**本交接单 (B1~B6 + 附)** ★ | ★**`HANDOFF/2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md`** ★ | ★**★本轮填完 (B2/B3/B4/B5/B6 + 附)★** ★ | ★**门禁 gate_check 认到 mech-lead 6/6 块齐全 (Q1 18/18)★** ★ |
| **3** | ★**分片 (原子写)** ★ | ★**`state/fragments/mech.yaml`** ★ | ★**★本轮写: +2 artifact +5 claim +1 need★** ★ | ★**`frag_write.py` 回显「✅ mech.yaml 已原子更新」· `RC=0` · 回读确认 5 条 `iss246_mech_*` claim + 1 条 need 在位** ★ |

★**★附 · 留档 (★不是交卷物, 是证据副本★)★**

| 序 | 留档 | 路径 | md5 |
|---|---|---|---|
| **L-1** | ★**沙盒 stepA (绿, 23/23)** ★ | ★**`HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_stepA.log`** ★ | ★**`a1b0915e744dbf130b74acb158b8cf00`** ★ |
| **L-2** | ★**沙盒 stepB (★红, 21/23 · FAIL 2 = G5b + C21★)** ★ | ★**`HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_stepB.log`** ★ | ★**`73995f6125c8b69dc889f7374dfe5167`** ★ |
| **L-3** | ★**沙盒 stepC (绿, 23/23)** ★ | ★**`HANDOFF/2026-11-16_mech-lead_ISS246_沙盒反向自证_stepC.log`** ★ | ★**`a1b0915e744dbf130b74acb158b8cf00`** ★ |

★**★交卷口径一句话★**: ★**这次红 = 上游合法落表后的锚点过期, 不是真源被换、不是红灯被调没; 本单只重锚 + 留痕, 判据逻辑/阈值/反向用例一个字节没动, `HW/` 零写入, 零外发, 零实物, 不替老板拍板; 交卷后 `check_demo_struct_truth.py` rc=0 (23/23) · `--selftest` rc=0 (14/14) · `merge`+`gate_check` rc=0 (Q1 18/18) · 受保护 5 件 md5 逐字节不变 ⇒ 请 main 落 verify。** ★ ★

---

★**★交卷人**: ★**mech-lead (结构总工, 带散热)** ★ · ★**交卷时刻**: ★**2026-11-16 18:5x (GMT+8)** ★ · ★**verify_by**: ★**main (项目总工)** ★ · ★**本单 §3.1 锚点数字本轮未动 (★第 3 跳是上一轮 17:43 落的★)· 本轮只补交卷单 6 段 + 分片 + 验收输出** ★
