# [mech-lead→PM] ISS-253 · MECH 侧 H-1 重锚 (网表 md5 过期 ⇒ `check_demo_struct_truth.py` 红)

| 项 | 值 |
|---|---|
| **单号** | ★**ISS-253** · **owner**: mech-lead (结构总工, 带散热) · **verify_by**: main (项目总工) ★ |
| **交卷时刻** | ★**2026-11-16 20:0x (GMT+8)** ★ |
| **地界** | ★**只动 `MECH/HW_CROSS_REVIEW_TRIAGE.md`** (§1 `source_ledger` 网表那一条锚点 4 字段 + §1 `landing_records` 加 1 行台账位置 + §3.1 追加 R-05 留痕行) **+ 本交接单 + `state/fragments/mech.yaml`** (走 `python3 state/frag_write.py` 原子写)** ★ ⇒ ★**`HW/` 受保护件一个字节没写 (★网表 / 脚表 / BOM / 板 / `.kicad_pro` 逐字节不变★) · `SW/` 一个字节没写 · `state/issue_log.yaml` 自改零处 (★不自签 issue_log★) · ★**门禁脚本 `MECH/check_demo_struct_truth.py` 一个字节没碰 (md5 交卷前后同 = `fa9b59e593a13408ad9505d986276f63`) ⇒ 判据逻辑 0 改动** ★ |
| ★**零外发** ★ | ★**本单没发任何邮件 / 询价 / 问询 / 采购 / 外部问询** ★ |
| ★**实物 [实测] = 0 条** ★ | ★**本单零实物** (★MECH 侧纯锚点重锚 + 门禁复跑, 板与样件不在本机 ⇒ 所有 [实测] 都是「本机脚本实跑 / 本机文件实读」★) ★ |

---

## ★0 一句话

★★**这次红 = 【上游合法落表后的锚点过期】, 不是【真源被换】、更不是【红灯被调没】** ★★
⇒ **ISS-249 (hw-lead) 2026-11-16 19:2x~19:4x 合法落表第 5 批 (F1 真落表)** 改了 `state/gen_netlist.py` 两行 `add()` 的 node2 槽 ⇒ **网表被重生成 ⇒ `HW/netlist_v1.csv` md5 `611c3ba3…` → `16ac89f7…`** ⇒ **MECH 侧 §1 锚点还钉在落表前的旧 md5** ⇒ **G5b + C21 双红 (rc=2, 21/23)**
⇒ ★**本单走 H-1 重锚流程 (第 4 跳: ISS-223 第 1 跳 → ISS-233 第 2 跳 → ISS-243 第 3 跳 → 本单第 4 跳)**: ★**只改网表那一条锚点的 4 个字段 (`md5` / `prev_md5` / `by` / `landed_at`) + §1 `landing_records` 加 ISS-249 交接单位置 + §3.1 追加 R-05 留痕行** ★
⇒ ★**G5b / C21 的判据逻辑一个字没动 · 阈值一个没松 · 反向用例一条没删 (14/14) · `HW/` 下 0 字节写入** ★
⇒ ★**`check_demo_struct_truth.py` rc=0 (23/23 · FAIL 0) · `--selftest` rc=0 (14/14)** ★

---

## ★0.1 ★★【重要口径更正 · 给 main 看这一条】★★

★★**派单里写的「文件 = `MECH/check_demo_struct_truth.py`」不成立 —— 网表 md5 锚点不在那个脚本里** ★★

| 项 | 实测事实 |
|---|---|
| ★**锚点在哪** ★ | ★**锚点是 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `# BEGIN MECH_ANCHORS` 块里 `anchors.source_ledger.entries[0]` (`file: HW/netlist_v1.csv`) 的 4 个字段** ★ ⇒ ★**脚本是【读】它, 不是【写死】它** ★ (★`MECH/check_demo_struct_truth.py` L117-126 `load_anchors()`: 正则切块 → `yaml.safe_load()` → `data["anchors"]`★) |
| ★**脚本里唯一的网表 md5 字面量** ★ | ★**L681 `c78f991283cc82d56c8e3dd31657c785` —— 那是 `--selftest` 的【反向用例 ⑪】fixture** (★「网表 md5 锚点改回旧值 ⇒ 必须变红」★) ⇒ ★**按「反向用例一条不许删」的口径, 它【必须不许改】, 本单一个字没动它** ★ |
| ★**本单实际改的** ★ | ★**锚点常量 = 那条 YAML 锚点条目 (4 字段)** ★ ⇒ ★**「锚点只改网表那一条」✅ · 「判据逻辑 0 改动」✅ (脚本 md5 `fa9b59e593a13408ad9505d986276f63` 交卷前后逐字节不变, mtime 仍 = 2026-11-16 03:55:42) · 「脚表 / BOM / 板 / `.kicad_pro` 四件逐字节不变」✅** ★ |
| ★**与前跳一致性** ★ | ★**ISS-246 (第 3 跳) 同样只改 `MECH/HW_CROSS_REVIEW_TRIAGE.md` + HANDOFF + 分片, 明确「未改 `MECH/check_demo_struct_truth.py`」⇒ 本单与既有 H-1 口径一致** ★ |

---

## B1 结论摘要

| 序 | 结论 | 证据 |
|---|---|---|
| **1.1** | ★**病灶 = 锚点过期 (不是真源被换)**: 开工前本单实跑 `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=2 · 「【结论】21/23 组检查通过 \| FAIL 2 组」** ⇒ 红的是门禁自己标名的 2 组: ★**G5b** (受保护文件 md5 逐字节未变) + ★**C21** (真源变更台账对账) ★ ⇒ ★**不是几何/公差栈的问题** (★G2.1~G2.9 / G4 / G4b / G5 / C22 全绿★) ★ | ★`[实测]` 开工前本机实跑 (★原样输出见 B5 ①-开工前★) ★ |
| **1.2** | ★**根因 = ISS-249 合法落表第 5 批 (2026-11-16 19:2x~19:4x · F1 真落表)**: `state/gen_netlist.py` 两行 `add()` 的 node2 槽从「借来的裸位号 `C_VBUS_OUT`」改成「本行自己的网名」⇒ 网表 L8/L12 两行的 node2 单元变了 ⇒ **网表 md5 变了** ⇒ ★**脚表 / BOM / `.net` / 板 / `.kicad_pro` 全部逐字节不变** ⇒ ★**真源 (网表 / 脚表 / BOM) 一个字都没被我改** ★ | ★`[实测]` 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17.2 / §17.5 + 交接单 `HANDOFF/2026-11-16_hw-lead_ISS249_F1落表.md` §B4.4 / §B5.0 ★ |
| **1.3** | ★**板那一侧逐字节不变 ⇒ 真源没被动过**: `HW/PCB/demo_mainboard.kicad_pcb` = `611b869e13518c3c023fb178f91a0075` · `HW/PCB/demo_mainboard.kicad_pro` = `3e504d2be83152e337949723e909be1b` ⇒ ★**变的只有网表这一件生成物 ⇒ 这不是「真源被换」** ★ | ★`[实测]` 交卷前后 `md5sum` 逐件完全一致 (见 B5 ④) · ★`[实测]` 落表台账 §17.5 受保护 md5 前后对照行 ★ |
| **1.4** | ★**落表凭据齐全 (四项同行 ⇒ C21 判据全过)**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` **§17** (「第 5 批落表条目 (★ISS-249 · 2026-11-16 19:2x~19:4x · 硬件总工 (hw-lead) 执行 · ★**F1 真落表 (ISS-242 第 1 条缺陷)**★)」) + **§17.5 L852** (★`ISS-249` · `HW/netlist_v1.csv` · 旧 `611c3ba3db3dc7de7213063375b96d01` → 新 `16ac89f77c25a3f61834cc7ebcd78a7f` · 「是 (★只有 L8 / L12 两行的 node2 单元★)」★) + **L854** (★脚表 旧 `ef436a37…` → 新 `ef436a37…` · 「否 (★逐字节不变★)」★) ⇒ ★**单号 + 文件名 + 新 md5 + 旧 md5 四项齐全且在同一行** ★ | ★`[实测]` 本机 `grep -n` 落表台账 ⇒ L852 逐字命中 (★原文见 B5 ⑤★) ★ |
| **1.5** | ★**落表时刻 = `2026-11-16 19:2x` (★不是我自己编的★)**: 台账 §17 表头登记的作业窗口 = 「2026-11-16 19:2x~19:4x」, §17.2 逐行实读标注 = 「★`[实测]` (2026-11-16 **19:2x** 本机 `grep -n` + `diff` 实读)」⇒ ★**§17 未登记到秒 ⇒ 锚点 `landed_at` 填 `"2026-11-16 19:2x"`, 与 hw-lead 交接单 `HANDOFF/2026-11-16_hw-lead_ISS249_F1落表.md` §「给 main 的一句话」里指定的值 (`landed_at = 2026-11-16 19:2x`, ★「以落表台账 §17 登记的时刻为准, 别自己编」★) 完全一致** ★ ⇒ ★**旁证**: 盘上网表落盘 mtime = `2026-11-16 19:36:12` (★落在 §17 登记的 19:2x~19:4x 窗口内★) —— 但★**该值未被写进锚点**★ (★前 3 跳 R-02/R-03/R-04 用的是「重生成产物落盘到秒」口径, 本跳 §17 没登记到秒 ⇒ 不自造到秒, 留痕写清两种口径★) ★ | ★`[实测]` 本机 `grep -n` §17 表头 + §17.2 + `stat -c '%y' HW/netlist_v1.csv` ★ |
| **1.6** | ★**判别证据 ① = 门禁脚本一个字没被碰过 ⇒ 是锚点过期不是红灯被调没**: `MECH/check_demo_struct_truth.py` mtime = **2026-11-16 03:55:42** · md5 = `fa9b59e593a13408ad9505d986276f63` ⇒ ★**交卷前后完全相同 ⇒ 脚本没被改过 ⇒ 红灯是「锚点过期」, 不是「有人把红灯调没了」** ★ | ★`[实测]` 本机 `stat` + `md5sum` 交卷前后 ★ |
| **1.7** | ★**判别证据 ② = 反向自证 (★在真盘上做的, ★改锚点 → 跑 → 立刻装回, 全程在一条命令内完成★)**: ★**A 绿 (rc=0 · 23/23) → B 把锚点 `md5` 改回旧值 `611c3ba3…` ⇒ G5b + C21 那 2 组重新变红 (rc=2 · 21/23) → C 装回 ⇒ 又绿 (rc=0 · 23/23)** ⇒ ★**证明 G5b / C21 这 2 组真在读盘上真值, 不是摆设** ★ | ★`[实测]` 三步原样输出见 B5 ③ · ★**装回后文件 md5 = `d75a8794c6ed4ac09aa8cd1100c55a69`, 与反向前逐字节相同 (★`cp` 还原, 非重新编辑★)** ★ |
| **1.8** | ★**本单只改锚点数字, 判据逻辑一个字没动**: G5b 的判据 (6 个硬保护文件 md5 + 2 个台账管理真源 md5) 与 C21 的 6 条判据 (①盘上==锚点 ②锚点md5可查台账 ③prev_md5可查台账 ④by可查台账 ⑤三项同一行 ⑥台账位置存在) ★**逐条原样保留** ★ · ★**阈值一个没松** (`cavity_req` 4.50 / `CRIT` 0.60 / `cav_v` 38.00 / `duct_v` 6.00 / 板框 60.00×30.00×1.00×3.33g) ★ · ★**反向用例一条没删 (14/14)** ★ | ★`[实测]` `check_demo_struct_truth.py --selftest` ⇒ **rc=0 · 14/14** (★输出见 B5 ②★) · ★`[实测]` 门禁脚本 md5 交卷前后逐字节不变 ★ |
| **1.9** | ★**留痕已登记 (§3.1 追加 R-05 行)**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` §3.1 **追加** R-05 (★追加式: **R-01 / R-02 / R-03 / R-04 历史行一个字没改**★) ⇒ ★**G8「留痕在场」门禁仍绿** ★ | ★`[实测]` `--selftest` ⇒ **14/14** (★REV-14「删掉『已修复 (留痕)』那一节」仍能抓到红★) · ★`[实测]` `grep` 逐行确认 R-01~R-05 全在位 ★ |
| **1.10** | ★**脚表锚点一条没动**: `HW/netlist_v1_pins.csv` 锚点仍是 `md5: ef436a37412ac9b6eac3c9f41f1edca4` / `prev_md5: b21b743a7702d30729f0d653c15392df` / `by: ISS-243` / `landed_at: "2026-11-16 15:45:45"` ⇒ ★**因为 ISS-249 本轮脚表 md5 逐字节没变 (台账 §17.5 L854 = 「否」) ⇒ 没有理由动它** ★ | ★`[实测]` YAML 解析逐字段打印 (见 B5 ⑥) · ★`[实测]` 台账 §17.5 L854 ★ |
| **1.11** | ★**本单零外发 / 零实物 / 不替老板拍板 / 不自签 issue_log**: ★**本单不拍任何待拍项** (★板长 / 板厚 / 腔体 / V-2 / V-3 一条没拍★) · ★**不碰 PCB 布线 / 布局 / 板框** ★ | ★`[0数据]` (★MECH 侧纯锚点重锚, 无可测物★) ★ |

---

## B2 验收标准自评 (逐条 通过 / 不通过 / 未验)

| # | 验收标准 | 判定 | 依据 |
|---|---|---|---|
| **A1** | ★**改后实测 rc=0 · 23/23 · FAIL 0** ★ | ★**✅ 通过** ★ | ★`[实测]` `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=0** · 「【结论】23/23 组检查通过 \| FAIL 0 组」 (B5 ①) ★ |
| **A2** | ★**反向用例: 锚点改回旧 md5 ⇒ 必须变红 (rc≠0 且点名 G5b/C21) ⇒ 再改回来 ⇒ rc=0** ★ | ★**✅ 通过** ★ | ★`[实测]` B 步 rc=**2** 且输出点名 ★**G5b**★ + ★**C21**★ (B5 ③) · C 步 rc=**0** (B5 ③) ★ |
| **A3** | ★**判据逻辑 0 改动** ★ | ★**✅ 通过** ★ | ★`[实测]` `MECH/check_demo_struct_truth.py` md5 `fa9b59e593a13408ad9505d986276f63` 交卷前后逐字节不变 · mtime 仍 2026-11-16 03:55:42 ★ |
| **A4** | ★**锚点只改网表那一条 (脚表 / BOM / 板 / `.kicad_pro` 四件逐字节不变)** ★ | ★**✅ 通过** ★ | ★`[实测]` md5 交卷前后对照 12 件, 唯 1 件变 (= 定性表本身), 其余 11 件逐字节不变 (B5 ④) ★ |
| **A5** | ★**`landed_at` 以 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §17 为准 (不自己编)** ★ | ★**✅ 通过** ★ | ★`[实测]` §17 表头 = 「19:2x~19:4x」· §17.2 = 「19:2x 本机实读」· hw-lead 交接单 §549 指定 `19:2x` ⇒ 填 `"2026-11-16 19:2x"` ★ |
| **A6** | ★**`--selftest` rc=0 且一条不许少 (反向用例不许删)** ★ | ★**✅ 通过** ★ | ★`[实测]` **rc=0 · 14/14 反向用例全抓到** (B5 ②) ★ |
| **A7** | ★**交卷单 B1~B6 六块齐全 + 分片走 `python3 state/frag_write.py` 原子写** ★ | ★**✅ 通过** ★ | ★本文件 B1/B2/B3/B4/B5/B6 齐全 · ★`[实测]` `python3 state/frag_write.py --agent mech-lead ...` 写入成功 (B5 ⑦) ★ |
| **A8** | ★**零落表 (网表/脚表/BOM 一个字节不许动) · 零外发 · 零实物 · 不碰 `HW/` 与 `SW/`** ★ | ★**✅ 通过** ★ | ★`[实测]` `HW/` 受保护 7 件 md5 交卷前后零差异 · 本单只写 `MECH/` 1 件 + `HANDOFF/` 1 件 + 自己分片 1 件 (B6.1) ★ |
| **A9** | ★**不碰布线/布局/板框 · 不改判据阈值 · 不替老板拍板 · 不自签 issue_log** ★ | ★**✅ 通过** ★ | ★`[实测]` 板 md5 `611b869e…` / `.kicad_pro` md5 `3e504d2b…` 零差异 · 阈值项 G5 仍绿 · ★**`state/issue_log.yaml` 零改动 (★本单只写自己分片 `state/fragments/mech.yaml`★)** ★ |

---

## B3 证据分级 (实测 / 官方 / 推算 / 0数据)

| 级 | 本单用到的证据 |
|---|---|
| ★**`[实测]`** ★ | ★**① 门禁实跑 (`check_demo_struct_truth.py` rc=0 · 23/23 · FAIL 0) ② `--selftest` rc=0 · 14/14 ③ 反向三步 (改回旧 md5 ⇒ rc=2 点名 G5b/C21 ⇒ 装回 rc=0) ④ 交卷前后 12 件 `md5sum` 对照 ⑤ 落表台账 §17 本机 `grep -n` 逐字命中 (L852 / L854) ⑥ YAML 解析后逐字段打印锚点 ⑦ `stat` mtime · `diff -u` 逐行改前改后 ⑧ `frag_write.py` 写入回执** ★ |
| ★**`[官网]`** ★ | ★**零条** (★本单不引任何外部数据 ⇒ 无需官网来源★) ★ |
| ★**`[推算]`** ★ | ★**零条** (★本单没有推算项, 全部是文件/脚本实读★) ★ |
| ★**`[0数据]`** ★ | ★**实物 [实测] = 0 条** (★板与样件不在本机★) ★ |

---

## B4 接口取值声明 (interface_claims)

| 项 | 取值 | 出处 | 谁改的 | 依据 |
|---|---|---|---|---|
| ★**网表 md5 锚点 (HW/netlist_v1.csv)** ★ | ★**`16ac89f77c25a3f61834cc7ebcd78a7f`** ★ | ★`MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `source_ledger.entries[0].md5` ★ | ★**hw-lead (落表) / mech-lead (只重锚)** ★ | ★`HW/SCHEMATIC_LANDING_V1_LANDED.md` §17.5 L852 ★ |
| ★**网表 md5 锚点 prev_md5 (旧值留痕)** ★ | ★**`611c3ba3db3dc7de7213063375b96d01`** ★ | ★同上 `entries[0].prev_md5` ★ | ★**mech-lead (只重锚)** ★ | ★同上 L852 的「旧 md5」列 ★ |
| ★**网表 md5 锚点 by (落表单号)** ★ | ★**`ISS-249`** ★ | ★同上 `entries[0].by` ★ | ★**hw-lead (落表)** ★ | ★同上 L852 的「单号」列 ★ |
| ★**网表 md5 锚点 landed_at** ★ | ★**`"2026-11-16 19:2x"`** ★ | ★同上 `entries[0].landed_at` ★ | ★**mech-lead (只重锚)** ★ | ★台账 §17 表头 + §17.2 + hw-lead 交接单 §549 ★ |
| ★**脚表 md5 锚点 (HW/netlist_v1_pins.csv)** ★ | ★**`ef436a37412ac9b6eac3c9f41f1edca4` (★本单一条没动★)** ★ | ★同上 `entries[1]` ★ | ★**hw-lead (ISS-243 落表) / 本单零碰** ★ | ★台账 §17.5 L854 = 「否 (逐字节不变)」 ★ |
| ★**受保护件 md5 (板 / `.kicad_pro` / 4 个 check 脚本)** ★ | ★**8 件逐字节不变** ★ | ★`MD5_EXPECTED` (脚本内写死) ★ | ★**本单零碰** ★ | ★B5 ④ 对照表 ★ |

---

## B5 验收命令原样输出 (未决项与卡点)

### ① `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=0 · 23/23 · FAIL 0** (改后实测)

```text
$ python3 MECH/check_demo_struct_truth.py
====================================================================================================
ISS-213/224 结构侧真值门禁 (demo 板当前成立的条目 + 板框/阈值/红灯保护 + 真源台账对账)
====================================================================================================
定性表: MECH/HW_CROSS_REVIEW_TRIAGE.md  |  源: MECH/service_port_check.py + MECH/hw_cross_review_check.py + MECH/BOARD_GEOM_30MM.md + HW/netlist_v1.csv + HW/SCHEMATIC_V1.md
----------------------------------------------------------------------------------------------------
  [OK ] G5    判据阈值未松: cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00
         service_port: cavity_req=4.5 cav_v=38.0 duct_v=6.0 CRIT=0.60; hw_cross_review: judge=0.6 cav_v_now=38.0
  [OK ] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)
         6 个硬保护文件 + 2 个台账管理真源 全部一致
  [OK ] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)
         台账可查 = ['HW/SCHEMATIC_LANDING_V1_LANDED.md', 'HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md', 'HANDOFF/2026-11-16_hw-lead_ISS233_21条未落表归因与拍板即落清单.md', 'HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md', 'HANDOFF/2026-11-16_hw-lead_ISS249_F1落表.md']; 对上 = ['HW/netlist_v1.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-249)', 'HW/netlist_v1_pins.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-243)']
  [OK ] C22   PIN-MISMATCH 独立复核 (P9 页声明 vs 网表实际 + d6 新旧口径)
         网表实读 CONN_LIGHT 22p / CONN_CAM 31p / J_CHG 10p; P9 声明 CONN_LIGHT [22] / CONN_CAM [31] / J_CHG [10]; 旧口径 0 处 / 新口径 3 处
  [OK ] G6    定性表 54 项全覆盖 (项号一个不缺) 且处置栏不留空/不写'待定'
         表内 54 行 / 应 54; 缺项号 = 无; 多余项号 = 无; 处置留空或待定 = 无
  [OK ] G6b   16 条 FAIL 每条都有明确去处 (修掉/出规格/登记 need 给 main/排队等原理图定稿)
         FAIL 行 16 条; 去处不在受控词表里的 = 无
  [OK ] G7    分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)
         实测 value = 25.00
  [OK ] G8    已修复的留痕必须在场 (PIN-MISMATCH 行 + §3.1「已修复 (留痕)」节)
         §2 行在位 (判定 = ✅ PASS, 备注带 ISS-220/落表) + §3.1 已修复节在位 (列着 ['PIN-MISMATCH', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)'])
----------------------------------------------------------------------------------------------------
【结论】23/23 组检查通过 | FAIL 0 组
口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**。
          本闸守的是 **demo 板当前成立的条目**, 不是'54 项全绿'。
          ★ 6 个 PCB 类 id 仍是 FAIL 是**正确状态** (排队等原理图定稿), 不是缺陷。
          ★ ISS-224: `PIN-MISMATCH` 是**被 ISS-220 真修好了**, 不是被调没 ⇒ 留痕在 §2 第 05 行 + §3.1。
====================================================================================================
$ echo $?
0
```

★**开工前同一命令的输出 (⇒ 这是红的那个起点, 供 main 对照)** ★

```text
  [FAIL] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)
         HW/netlist_v1.csv: 16ac89f77c25a3f61834cc7ebcd78a7f != 611c3ba3db3dc7de7213063375b96d01
  [FAIL] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)
         HW/netlist_v1.csv: 盘上 md5 16ac89f77c25a3f61834cc7ebcd78a7f != 锚点登记 611c3ba3db3dc7de7213063375b96d01 (真源被换了或锚点过期)
【结论】21/23 组检查通过 | FAIL 2 组
$ echo $?
2
```

### ② `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ **rc=0 · 14/14 (一条没删)**

```text
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
$ echo $?
0
```

### ③ ★反向用例: 锚点改回旧 md5 ⇒ 必须变红 ⇒ 装回 ⇒ 又绿 (★真盘实跑, 三步在同一条命令内走完★)★

```text
$ python3 - <<'PY'   # 只改 §1 锚点那一个 md5 字段, 跑完立刻 cp 装回
>>> 反向: 锚点 md5 已改回旧值 611c3ba3db3dc7de7213063375b96d01
>>> reverse rc = 2
    [FAIL] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)
         HW/netlist_v1.csv: 16ac89f77c25a3f61834cc7ebcd78a7f != 611c3ba3db3dc7de7213063375b96d01
    [FAIL] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)
         HW/netlist_v1.csv: 盘上 md5 16ac89f77c25a3f61834cc7ebcd78a7f != 锚点登记 611c3ba3db3dc7de7213063375b96d01 (真源被换了或锚点过期)
    【结论】21/23 组检查通过 | FAIL 2 组
>>> 装回后 md5 = d75a8794c6ed4ac09aa8cd1100c55a69
>>> restored rc = 0
    【结论】23/23 组检查通过 | FAIL 0 组
PY
```

★**这就是「它真在被读」的证据**: 同一份盘上文件, 只动锚点那一个 md5 字段 ⇒ G5b + C21 立刻点名变红 ⇒ 装回 ⇒ 立刻又绿 ⇒ ★**这两组判据跟着盘上真值走, 不是摆设** ★
★**装回用的是 `cp` 还原 (不是重新编辑)** ⇒ ★**还原后文件 md5 `d75a8794c6ed4ac09aa8cd1100c55a69` = 反向前逐字节相同** ★

### ④ ★受保护 md5 交卷前后对照 (★本机自己跑出来的, 不是抄别人的★)★

```text
$ md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/BOM_pseudo_refs_v1.csv \
         HW/netlist_v1.net HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
         MECH/check_demo_struct_truth.py MECH/service_port_check.py MECH/hw_cross_review_check.py \
         MECH/hinge_usb_check.py MECH/display_biosafety_v2_check.py MECH/HW_CROSS_REVIEW_TRIAGE.md
```

| 文件 | 交卷前 md5 | 交卷后 md5 | 变了? |
|---|---|---|---|
| `HW/netlist_v1.csv` (网表) | `16ac89f77c25a3f61834cc7ebcd78a7f` | `16ac89f77c25a3f61834cc7ebcd78a7f` | ★**否** ★ |
| `HW/netlist_v1_pins.csv` (脚表) | `ef436a37412ac9b6eac3c9f41f1edca4` | `ef436a37412ac9b6eac3c9f41f1edca4` | ★**否** ★ |
| `HW/BOM_v1.csv` | `2a7305741134788dfee9f13f34c656b4` | `2a7305741134788dfee9f13f34c656b4` | ★**否** ★ |
| `HW/BOM_pseudo_refs_v1.csv` | `47e1659a42d8d3f6728ea653df1eb530` | `47e1659a42d8d3f6728ea653df1eb530` | ★**否** ★ |
| `HW/netlist_v1.net` | `564fed05c1f5f9dab09efce51eebae74` | `564fed05c1f5f9dab09efce51eebae74` | ★**否** ★ |
| `HW/PCB/demo_mainboard.kicad_pcb` (板) | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | ★**否** ★ |
| `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | `3e504d2be83152e337949723e909be1b` | ★**否** ★ |
| `MECH/check_demo_struct_truth.py` (门禁脚本) | `fa9b59e593a13408ad9505d986276f63` | `fa9b59e593a13408ad9505d986276f63` | ★**否** ★ |
| `MECH/service_port_check.py` | `9b24bf985764880f0105aee677fba6a8` | `9b24bf985764880f0105aee677fba6a8` | ★**否** ★ |
| `MECH/hw_cross_review_check.py` | `e521387b87b0fcdf9f22d56f14199967` | `e521387b87b0fcdf9f22d56f14199967` | ★**否** ★ |
| `MECH/hinge_usb_check.py` | `3425bc141508de8a35f34c7cf7b803e8` | `3425bc141508de8a35f34c7cf7b803e8` | ★**否** ★ |
| `MECH/display_biosafety_v2_check.py` | `29c77fc3fc823048b1d96c9500d28dd7` | `29c77fc3fc823048b1d96c9500d28dd7` | ★**否** ★ |
| `MECH/HW_CROSS_REVIEW_TRIAGE.md` (★本单唯一被改的源文件★) | `a4900225e102f2ee1ff52ef55b56458d` | `d75a8794c6ed4ac09aa8cd1100c55a69` | ★**是 (★锚点 4 字段 + landing_records 1 行 + §3.1 R-05 1 行 = 3 个 hunk★)** ★ |

★**`diff` 逐行对照的原始输出 (唯一 1 行差异 = 本单要改的那个文件)** ★

```text
$ diff md5_before.txt md5_after.txt
13c13
< a4900225e102f2ee1ff52ef55b56458d  MECH/HW_CROSS_REVIEW_TRIAGE.md
---
> d75a8794c6ed4ac09aa8cd1100c55a69  MECH/HW_CROSS_REVIEW_TRIAGE.md
```

### ⑤ ★逐行改前改后 (`diff -u`, 全量, 本单唯一被改的文件)★

```diff
--- MECH/HW_CROSS_REVIEW_TRIAGE.md (改前 / 备份)
+++ MECH/HW_CROSS_REVIEW_TRIAGE.md (改后)
@@ -107,12 +107,13 @@
       - HANDOFF/2026-11-16_hw-lead_ISS223_*.md
       - HANDOFF/2026-11-16_hw-lead_ISS233_*.md
       - HANDOFF/2026-11-16_hw-lead_ISS243_*.md
+      - HANDOFF/2026-11-16_hw-lead_ISS249_*.md
     entries:                        # ★ 受"台账对账"机制管的真源: 旧锚点 → 新锚点 + 落表单号
       - file: HW/netlist_v1.csv
-        by: ISS-243                 # ★ 落表单号 (★**ISS-246 重锚 · 2026-11-16 · 第三跳**★: ... 第 3 跳 = ISS-243 ...)
-        prev_md5: 34132f7e40a241e1fae1476be0eafbd5
-        md5: 611c3ba3db3dc7de7213063375b96d01
-        landed_at: "2026-11-16 15:45:45"
+        by: ISS-249                 # ★ 落表单号 (★**ISS-253 重锚 · 2026-11-16 · 第四跳 (H-1 跳链第 5 跳)**★: hw-lead 的 ISS-249 第 5 批落表 (F1 真落表) 改了网表 L8/L12 两行的 node2 单元 ⇒ 按 H-1 再重锚一次; ★**第 1 跳 = ISS-223 (`13f59a43…`→`3215020b…`), 留痕见 §3.1 R-02** ★ · ★**第 2 跳 = ISS-233 (`3215020b…`→`34132f7e…`), 留痕见 §3.1 R-03** ★ · ★**第 3 跳 = ISS-243 (`34132f7e…`→`611c3ba3…`), 留痕见 §3.1 R-04** ★ · ★**第 4 跳 = ISS-249 (`611c3ba3…`→`16ac89f7…`), 留痕见 §3.1 R-05**★)
+        prev_md5: 611c3ba3db3dc7de7213063375b96d01
+        md5: 16ac89f77c25a3f61834cc7ebcd78a7f
+        landed_at: "2026-11-16 19:2x"
       - file: HW/netlist_v1_pins.csv
         by: ISS-243                 # ★ 落表单号 (★**ISS-246 重锚 · 2026-11-16 · 第三跳**★: ... 留痕见 §3.1 R-04)   ← ★**这一条 (脚表锚点) 一个字节没动** ★
         prev_md5: b21b743a7702d30729f0d653c15392df
@@ -234,6 +235,7 @@
 | **R-02** | ... (历史行, 未动) |
 | **R-03** | ... (历史行, 未动) |
 | **R-04** | ... (历史行, 未动) |
+| **R-05** | `HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**) | ★**第 4 跳重锚**: 锚点还停在 ISS-243 版 (网表 `611c3ba3…`), 但真源已被 hw-lead 的 ★**ISS-249 第 5 批**★ 落表换掉 (盘上网表 = `16ac89f7…`) ⇒ 门禁 **G5b + C21 双红** (rc=2, 21/23) | ★**hw-lead** ... | ★**ISS-249** ★ | ★**已由 ISS-249 落表修复 (2026-11-16 19:2x)** ★ ... | ★**`md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv`** ★ ⇒ ... | ★**✅ 已修复 (留痕)** ★ |
```

★**hunk 数 = 3 (① landing_records +1 行 · ② 网表锚点条目 4 字段+注释 · ③ §3.1 R-05 +1 行) ⇒ §2 定性表 54 行一个没动 · 脚表锚点条目一个字节没动 · §3.1 历史行 R-01~R-04 一个字节没动** ★

### ⑥ 锚点字段落地后逐字段回读 (YAML 解析, 非肉眼)

```text
$ python3 -c "import re,yaml; t=open('MECH/HW_CROSS_REVIEW_TRIAGE.md',encoding='utf-8').read(); \
  a=yaml.safe_load(re.search(r'# BEGIN MECH_ANCHORS(.*?)# END MECH_ANCHORS',t,re.S).group(1))['anchors']; \
  [print(e['file'], e['md5'], e.get('prev_md5'), e.get('by'), repr(e.get('landed_at'))) for e in a['source_ledger']['entries']]"
HW/netlist_v1.csv 16ac89f77c25a3f61834cc7ebcd78a7f 611c3ba3db3dc7de7213063375b96d01 ISS-249 '2026-11-16 19:2x'
HW/netlist_v1_pins.csv ef436a37412ac9b6eac3c9f41f1edca4 b21b743a7702d30729f0d653c15392df ISS-243 '2026-11-16 15:45:45'

netlist anchor == disk md5 ? True
```

### ⑦ 落表台账 §17 逐字命中 (C21 的凭据)

```text
$ grep -n "16ac89f7\|^### ★★17.5\|^## ★★17" HW/SCHEMATIC_LANDING_V1_LANDED.md
704:## ★★17 · 第 5 批落表条目 (ISS-249 · 2026-11-16 19:2x~19:4x · 硬件总工 (hw-lead) 执行 · ★**F1 真落表 (ISS-242 第 1 条缺陷)**★) ★★
847:### ★★17.5 · ★★md5 台账 (★单号 + 文件名 + 旧 md5 + 新 md5 四项同行齐全 · ★SW 侧 R6 判据要读★)★★ ★★
852:| ★**ISS-249** ★ | ★**`HW/netlist_v1.csv`** (表A) ★ | `611c3ba3db3dc7de7213063375b96d01` | `16ac89f77c25a3f61834cc7ebcd78a7f` | ★**是 (★只有 L8 / L12 两行的 node2 单元★)** ★ |
854:| ★**ISS-249** ★ | ★**`HW/netlist_v1_pins.csv`** (脚表) ★ | `ef436a37412ac9b6eac3c9f41f1edca4` | `ef436a37412ac9b6eac3c9f41f1edca4` | ★**否 (★逐字节不变★)** ★ |
```

### ⑧ 分片原子写回执

```text
$ python3 state/frag_write.py --agent mech-lead --add-claim key=iss253_mech_md5_anchor_netlist \
    value=16ac89f77c25a3f61834cc7ebcd78a7f note="..." --add-claim key=iss253_mech_md5_anchor_pins \
    value=ef436a37412ac9b6eac3c9f41f1edca4 note="..." --add-claim key=iss253_mech_md5_hop_count \
    value="第 4 跳" note="..." --add-artifact path=HANDOFF/2026-11-16_mech-lead_ISS253_H1重锚网表md5.md \
    summary="..." kind=handoff version=v1.0
[frag_write] mech.yaml 写入完成 (原子写 tmp + os.replace)
```

### ⑨ 未决项与卡点

| 项 | 状态 | 谁 |
|---|---|---|
| ★**本单有没有未决项** ★ | ★**没有** (★锚点已重锚, 门禁 rc=0 · 23/23, selftest 14/14, 受保护件零差异, 留痕已登记, 分片已写★) ★ | — |
| ★**待 main 裁的** ★ | ★**无本单遗留** (★本单不拍任何待拍项★) ★ | — |
| ★**下一跳预告 (★不是本单任务, 只报不接★)** ★ | ★**只要 hw-lead 再落一次表改到网表/脚表, 锚点就会再过期一次 ⇒ 下一跳照 H-1 流程走 (改 4 字段 + `landing_records` +1 + §3.1 R-06 +1)** ★ | ★**hw-lead 落表时同步 notify main** ★ |

---

## B6 边界审计 (自证复现命令)

### B6.1 本单动过的文件 (★3 件★)

| # | 文件 | 动了什么 | md5 前 → 后 |
|---|---|---|---|
| **1** | ★**`MECH/HW_CROSS_REVIEW_TRIAGE.md`** ★ | ★**① §1 `source_ledger.landing_records` +1 行 (ISS-249 台账位置) ② §1 `source_ledger.entries[0]` (网表) 4 字段 + 跳链注释 ③ §3.1 追加 R-05 留痕行** ★ | ★`a4900225e102f2ee1ff52ef55b56458d` → ★`d75a8794c6ed4ac09aa8cd1100c55a69` ★ |
| **2** | ★**`HANDOFF/2026-11-16_mech-lead_ISS253_H1重锚网表md5.md`** ★ | ★**本交卷单 (新建)** ★ | ★**新建** ★ |
| **3** | ★**`state/fragments/mech.yaml`** ★ | ★**自己分片: +3 claim +2 artifact (走 `state/frag_write.py` 原子写)** ★ | ★**原子写 (tmp + `os.replace`)★** ★ |

### B6.2 边界逐条自证 (10 条)

| # | 边界 | 自证 |
|---|---|---|
| **1** | ★**零落表 (网表 / 脚表 / BOM 一个字节不许动)** ★ | ★`[实测]` `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/BOM_pseudo_refs_v1.csv` / `HW/netlist_v1.net` 交卷前后 md5 逐字节相同 (B5 ④) ★ |
| **2** | ★**零外发** ★ | ★`[实测]` 本单无任何网络请求 / 邮件 / 询价 / 问询 / 采购动作 ★ |
| **3** | ★**零实物** ★ | ★`[实测]` 实物 [实测] = 0 条 (板与样件不在本机) ★ |
| **4** | ★**不碰 `HW/`** ★ | ★`[实测]` `HW/` 下 7 件受保护件 md5 零差异; ★**`HW/SCHEMATIC_LANDING_V1_LANDED.md` 只读不写** ★ |
| **5** | ★**不碰 `SW/`** ★ | ★`[实测]` 本单零写 `SW/` 任何文件 (★SW 台账 / SW 分片 = sw-lead 的活★) ★ |
| **6** | ★**不碰布线 / 布局 / 板框** ★ | ★`[实测]` 板 md5 `611b869e…` / `.kicad_pro` md5 `3e504d2b…` 零差异 ★ |
| **7** | ★**不改判据阈值 / 判据逻辑** ★ | ★`[实测]` 门禁脚本 md5 `fa9b59e593a13408ad9505d986276f63` 交卷前后逐字节不变 · G5 阈值项仍绿 · selftest 14/14 ★ |
| **8** | ★**不替老板拍板 (板长 / 板厚 / 腔体不归我)** ★ | ★`[实测]` 本单 0 个待拍项被拍 ★ |
| **9** | ★**不自签 issue_log** ★ | ★`[实测]` `state/issue_log.yaml` 零改动; ★**verify 留给 main** ★ |
| **10** | ★**不把整份脚本重写 (只改锚点常量)** ★ | ★`[实测]` `MECH/check_demo_struct_truth.py` 一个字节没改 (md5 + mtime 双证); ★**§2 定性表 54 行 / §3 去处表 16 行 / G6 全绿** ★ |

### B6.3 自证复现命令 (★main 可原样跑★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ① 改后门禁
python3 MECH/check_demo_struct_truth.py; echo "rc=$?"
# ② 反向用例 (14 条一条不许少)
python3 MECH/check_demo_struct_truth.py --selftest; echo "rc=$?"
# ③ 锚点逐字段回读
python3 -c "import re,yaml; t=open('MECH/HW_CROSS_REVIEW_TRIAGE.md',encoding='utf-8').read(); a=yaml.safe_load(re.search(r'# BEGIN MECH_ANCHORS(.*?)# END MECH_ANCHORS',t,re.S).group(1))['anchors']; [print(e['file'], e['md5'], e.get('prev_md5'), e.get('by'), repr(e.get('landed_at'))) for e in a['source_ledger']['entries']]"
# ④ 受保护件 md5
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro MECH/check_demo_struct_truth.py
# ⑤ 落表凭据
grep -n "16ac89f77c25a3f61834cc7ebcd78a7f" HW/SCHEMATIC_LANDING_V1_LANDED.md
# ⑥ 留痕行
grep -n "^| \*\*R-0" MECH/HW_CROSS_REVIEW_TRIAGE.md
```

### B6.4 本单自用临时物

| 路径 | 说明 |
|---|---|
| `/tmp/iss253/TRIAGE.before.md` | 改前的定性表备份 (★`diff -u` 的左侧★) |
| `/tmp/iss253/TRIAGE.after.md` | 重锚后的定表备份 (★反向用例「装回」用的就是它, `cp` 还原★) |
| `/tmp/iss253/md5_before.txt` / `md5_after.txt` | 交卷前后 13 件 md5 清单 |
| `/tmp/iss253/triage.diff` | 逐行改前改后全量 diff |
| `/tmp/iss253/reverse_red.txt` / `reverse_green.txt` / `selftest.txt` / `after_run.txt` | 三次门禁原样输出留档 |

★**本单没有在真盘上留任何临时文件** (★反向用例全程用 `cp` 还原 + 立刻复跑, 真盘只在「旧锚点」与「新锚点」两个确定态之间切换, 且两个态都有原样输出留档★) ★

---

## ★附 · 交卷物清单 (3 件)

| # | 物件 | 路径 |
|---|---|---|
| **1** | ★**本交卷单 (B1~B6 齐全)** ★ | `HANDOFF/2026-11-16_mech-lead_ISS253_H1重锚网表md5.md` ★ |
| **2** | ★**被重锚的定性表 (锚点 4 字段 + landing_records + §3.1 R-05)** ★ | `MECH/HW_CROSS_REVIEW_TRIAGE.md` ★ |
| **3** | ★**自己分片 (走 `state/frag_write.py` 原子写)** ★ | `state/fragments/mech.yaml` ★ |

---

## ★附2 · 2026-11-17 05:0x 续做复核 (★重派复核 · 本单早已落表并 verified ⇒ 本轮零字节改动锚点★)

| 项 | 值 |
|---|---|
| **单号** | ★**ISS-253 (重派复核)** · **owner**: mech-lead · **verify_by**: main ★ |
| **本轮性质** | ★**复核单 —— 不是新落表单**: 本单 (=ISS-253) 已于 **2026-11-16 20:07** 落表交付, main 20:1x 独立复核并把 `state/issue_log.yaml` 的 ISS-253 标成 **`verified`**; 随后被 hw-lead 的 **ISS-257 第 6 批落表**覆盖, main 21:4x 另派 **ISS-259 (第 6 跳)**, ISS-259 亦已 `verified` ⇒ ★**本轮 = 一张【过期旧派单】的复核, 不是一次新的重锚** ★ |
| **本轮改了几个字节** | ★**0 个** ★ (★`MECH/HW_CROSS_REVIEW_TRIAGE.md` md5 前后逐字节同 = `920b497b3664e40aebc23f2ea63463c2`★) |

### ★附2.0 一句话 (★给 main 先看这一条★)

★★**ISS-253 这张派单的前提已经过期: 锚点早就不在 `611c3ba3…` 了, 现在在 `e06c1dd6…`** ★★
⇒ ★**盘上网表 (`HW/netlist_v1.csv`) = `e06c1dd633566aa44732762c2ff99d1c` (hw-lead ISS-257 第 6 批落表, 2026-11-16 21:22; 盘上 mtime 22:25, 内容未再变) = §1 锚点 `source_ledger.entries[0].md5` 现值 ⇒ 门禁 **rc=0 · 23/23 · FAIL 0** ★
⇒ ★**★若照本派单字面把锚点改成 `16ac89f77c25a3f61834cc7ebcd78a7f` (prev `611c3ba3…` · by `ISS-249`), 门禁会【立刻变红】rc=2 · 21/23 · FAIL G5b + C21** ★ ⇒ ★**⇒ 已用真盘实测证明 (见 ★附2.4★): 那等于把网表谎报成「ISS-249 落表后的旧版本」, 而盘上真源已经是 ISS-257 版 ⇒ 这不是重锚, 是把绿灯打红** ★
⇒ ★**所以本轮: 锚点一个字没动, MECH/ 与 HW/ 零字节写入, 做的是【复核 + 反向自证 + 留痕】** ★

---

### ★附2.1 B1′ 结论摘要

| 序 | 结论 | 证据 |
|---|---|---|
| **1.1′** | ★**ISS-253 早已完结**: 交卷单在盘 (mtime 2026-11-16 20:07:47) · §3.1 **R-05** 留痕行在位 (网表 `611c3ba3…` → `16ac89f7…`, by ISS-249) · `state/issue_log.yaml` 的 **ISS-253 status = `verified`** ⇒ ★**本轮没有可做的重锚动作** ★ | ★`[实测]` `stat` + `grep` §3.1 + `grep -A4 "id: ISS-253" state/issue_log.yaml` (★只读, 本单零字节写 issue_log★) ★ |
| **1.2′** | ★**锚点已被第 6 跳 (ISS-259) 推到最新**: 现值 = 网表 `md5=e06c1dd633566aa44732762c2ff99d1c` / `prev_md5=16ac89f77c25a3f61834cc7ebcd78a7f` / `by=ISS-257` / `landed_at="2026-11-16 21:22"` · 脚表 `md5=287e7861a0d1007748d92d9fbecdd490` / `prev_md5=ef436a37412ac9b6eac3c9f41f1edca4` / `by=ISS-257` ⇒ ★**跳链完整**: ISS-220 (`13f59a43…`) → ISS-223 (`3215020b…` · R-02) → ISS-233 (`34132f7e…` · R-03) → ISS-243 (`611c3ba3…` · R-04) → ★**ISS-249 (`16ac89f7…` · R-05 = 本单)** → ★**ISS-257 (`e06c1dd6…` · R-06 = ISS-259)** ★ | ★`[实测]` YAML 逐字段回读 (★附2.3 ③★) + `grep` §3.1 R-01~R-07 ★ |
| **1.3′** | ★**闸门现在是绿的, 不是红的**: `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=0 · 23/23 · FAIL 0** ★ · `--selftest` ⇒ ★**rc=0 · 14/14 (一条没少)** ★ ⇒ ★**派单里写的「rc=2 (21/23, FAIL G5b + C21)」已【不复现】** ★ | ★`[实测]` 原样输出见 ★附2.3 ①②★ ★ |
| **1.4′** | ★**反向自证 (真盘跑, 带 trap 还原)**: 步骤 A 把锚点改成【本派单字面要求的目标态】(`16ac89f7…` / prev `611c3ba3…` / by `ISS-249` / landed_at `2026-11-16 19:2x` ⇒ 依 §17) ⇒ ★**rc=2 · 21/23 · FAIL 2 组 = G5b + C21** ★; 步骤 B 只把 `md5` 回滚到 `611c3ba3…` ⇒ ★**同样 rc=2 · FAIL G5b + C21** ★; 步骤 C 按备份逐字节装回 ⇒ ★**rc=0 · 23/23 · FAIL 0** ★ ⇒ ★**⇒ 证明 G5b/C21 真在读盘上真值 (不是摆设), 同时证明【本派单字面落地 = 把绿灯打红】** ★ | ★`[实测]` 原样输出见 ★附2.4★ ★ |
| **1.5′** | ★**受保护件本轮逐字节未变 (11 件自跑)**: 板 `611b869e…` · `.kicad_pro` `3e504d2b…` · 网表 `e06c1dd6…` · 脚表 `287e7861…` · 门禁脚本 `4ae5827e…` · `service_port_check.py` `db58ff6a…` · `hinge_usb_check.py` `3425bc14…` · `hw_cross_review_check.py` `e521387b…` · `display_biosafety_v2_check.py` `29c77fc3…` · 定性表 `920b497b…` ⇒ ★**本轮改动的文件 = 0 个 (只写了这张交卷单 + 自己分片)** ★ | ★`[实测]` 本机 `md5sum` (★附2.5 前后对照表★) ★ |
| **1.6′** | ★**留痕**: 本附2 段 + 分片 claim `mech_netlist_md5_anchor_current` (走 `state/frag_write.py --agent mech-lead` 原子写) ⇒ ★**§3.1「已修复 (留痕)」节本轮【不新增行】** ★ (★理由: 本轮零锚点改动 ⇒ 没有新的「已修复」事件可留痕; 留痕写在本交卷单 + 分片层, 且 R-05/R-06 两行原样在位, G8 仍绿★) | ★`[实测]` `--selftest` 14/14 (★反向14「删掉『已修复』留痕」仍能抓红 ⇒ 留痕机制没被削弱★) ★ |

### ★附2.2 B2′ 验收标准自评 (逐条)

| # | 派单验收项 | 自评 | 说明 |
|---|---|---|---|
| 1 | ★**改后 rc=0 · 23/23 · FAIL 0** ★ | ✅ **通过** | ★**现状已是 rc=0 · 23/23 · FAIL 0** (★锚点现值 = 盘上真值★) ★ |
| 2 | ★**锚点新值 = `16ac89f77c25a3f61834cc7ebcd78a7f` · 旧值留痕 `611c3ba3…`** ★ | ⚠️ **不适用 (已被覆盖)** | ★**这两个值正是【第 4 跳 / R-05】的内容, 2026-11-16 20:07 已落表并 verified**; ★**现值 = 第 6 跳 / R-06 = `e06c1dd6…`** ★ ⇒ ★**且照字面改回去会变红 (已实测) ⇒ 拒绝执行, 不做假绿** ★ |
| 3 | ★**反向用例: 改回旧 md5 ⇒ 必红且点名 G5b/C21 ⇒ 改回来 ⇒ rc=0** ★ | ✅ **通过** | ★**真盘跑完 A/B/C 三步 (★附2.4★), 两次红 + 一次绿, 全程 `cp` 还原, 还原后 md5 与基线逐字节同** ★ |
| 4 | ★**`--selftest` rc=0 且一条不许少** ★ | ✅ **通过** | ★**rc=0 · 14/14** (★附2.3 ② 原样贴出★) ★ |
| 5 | ★**脚表 / BOM / 板 / `.kicad_pro` 四件逐字节不变** ★ | ✅ **通过** | ★**见 ★附2.5 表 (本轮 11 件自跑, 前后同)★ ★ |
| 6 | ★**判据逻辑 0 改动** ★ | ✅ **通过** | ★**`MECH/check_demo_struct_truth.py` md5 `4ae5827e986f1aebb108c5aa2a475074` 本轮前后同, mtime 仍 = 2026-11-17 02:33:22 (★ISS-264 那次改的, 不是本轮★)** ★ |
| 7 | ★**交卷单 B1~B6 齐全** ★ | ✅ **通过** | ★**B1~B6 齐全 = 2026-11-16 20:07 原交卷 (本轮以「附2 B1′~B6′」续证, 原六块一字没删)** ★ |
| 8 | ★**分片走 `frag_write.py` 原子写** ★ | ✅ **通过** | ★**本轮新增 claim 1 条 (★附2.7★) ★ |

### ★附2.3 B3′ 证据分级 + B5′ 原样输出 (★现状实测★)

**① `python3 MECH/check_demo_struct_truth.py` ⇒ rc=0 · 23/23 · FAIL 0 (原样)**

```text
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
         台账可查 = ['HW/SCHEMATIC_LANDING_V1_LANDED.md', 'HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md', 'HANDOFF/2026-11-16_hw-lead_ISS233_21条未落表归因与拍板即落清单.md', 'HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md', 'HANDOFF/2026-11-16_hw-lead_ISS249_F1落表.md', 'HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md']; 对上 = ['HW/netlist_v1.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-257)', 'HW/netlist_v1_pins.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-257)']
  [OK ] C22   PIN-MISMATCH 独立复核 (P9 页声明 vs 网表实际 + d6 新旧口径)
         网表实读 CONN_LIGHT 22p / CONN_CAM 31p / J_CHG 10p; P9 声明 CONN_LIGHT [22] / CONN_CAM [31] / J_CHG [10]; 旧口径 0 处 / 新口径 3 处
  [OK ] G6    定性表 54 项全覆盖 (项号一个不缺) 且处置栏不留空/不写'待定'
         表内 54 行 / 应 54; 缺项号 = 无; 多余项号 = 无; 处置留空或待定 = 无
  [OK ] G6b   16 条 FAIL 每条都有明确去处 (修掉/出规格/登记 need 给 main/排队等原理图定稿)
         FAIL 行 16 条; 去处不在受控词表里的 = 无
  [OK ] G7    分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)
         实测 value = 25.00
  [OK ] G8    已修复的留痕必须在场 (PIN-MISMATCH 行 + §3.1「已修复 (留痕)」节)
         §2 行在位 (判定 = ✅ PASS, 备注带 ISS-220/落表) + §3.1 已修复节在位 (列着 ['PIN-MISMATCH', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'MECH/service_port_check.py` 的 md5 锚点 (门禁 **G5b**)'])
----------------------------------------------------------------------------------------------------
【结论】23/23 组检查通过 | FAIL 0 组
口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**。
          本闸守的是 **demo 板当前成立的条目**, 不是'54 项全绿'。
          ★ 6 个 PCB 类 id 仍是 FAIL 是**正确状态** (排队等原理图定稿), 不是缺陷。
          ★ ISS-224: `PIN-MISMATCH` 是**被 ISS-220 真修好了**, 不是被调没 ⇒ 留痕在 §2 第 05 行 + §3.1。
====================================================================================================
```

**② `python3 MECH/check_demo_struct_truth.py --selftest` ⇒ rc=0 · 14/14 (原样)**

```text
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
```

**③ 锚点逐字段回读 (YAML 解析, 非肉眼)**

```text
source_ledger.entries:
  file=HW/netlist_v1.csv
    md5       = e06c1dd633566aa44732762c2ff99d1c
    prev_md5  = 16ac89f77c25a3f61834cc7ebcd78a7f
    by        = ISS-257
    landed_at = 2026-11-16 21:22
  file=HW/netlist_v1_pins.csv
    md5       = 287e7861a0d1007748d92d9fbecdd490
    prev_md5  = ef436a37412ac9b6eac3c9f41f1edca4
    by        = ISS-257
    landed_at = 2026-11-16 21:22
landing_records:
  - HW/SCHEMATIC_LANDING_V1_LANDED.md
  - HANDOFF/2026-11-16_hw-lead_ISS223_*.md
  - HANDOFF/2026-11-16_hw-lead_ISS233_*.md
  - HANDOFF/2026-11-16_hw-lead_ISS243_*.md
  - HANDOFF/2026-11-16_hw-lead_ISS249_*.md
  - HANDOFF/2026-11-16_hw-lead_ISS257_*.md
```

### ★附2.4 B5′ 反向自证 (★真盘跑 · 三步在同一条命令内走完 · 全程 trap 还原★)

**步骤 A ★= 复刻本派单字面要求的目标态 ★⇒ 必须变红**

```text
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
  [FAIL] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)
         HW/netlist_v1.csv: e06c1dd633566aa44732762c2ff99d1c != 16ac89f77c25a3f61834cc7ebcd78a7f
  [FAIL] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)
         HW/netlist_v1.csv: 盘上 md5 e06c1dd633566aa44732762c2ff99d1c != 锚点登记 16ac89f77c25a3f61834cc7ebcd78a7f (真源被换了或锚点过期)
  [OK ] C22   PIN-MISMATCH 独立复核 (P9 页声明 vs 网表实际 + d6 新旧口径)
         网表实读 CONN_LIGHT 22p / CONN_CAM 31p / J_CHG 10p; P9 声明 CONN_LIGHT [22] / CONN_CAM [31] / J_CHG [10]; 旧口径 0 处 / 新口径 3 处
  [OK ] G6    定性表 54 项全覆盖 (项号一个不缺) 且处置栏不留空/不写'待定'
         表内 54 行 / 应 54; 缺项号 = 无; 多余项号 = 无; 处置留空或待定 = 无
  [OK ] G6b   16 条 FAIL 每条都有明确去处 (修掉/出规格/登记 need 给 main/排队等原理图定稿)
         FAIL 行 16 条; 去处不在受控词表里的 = 无
  [OK ] G7    分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)
         实测 value = 25.00
  [OK ] G8    已修复的留痕必须在场 (PIN-MISMATCH 行 + §3.1「已修复 (留痕)」节)
         §2 行在位 (判定 = ✅ PASS, 备注带 ISS-220/落表) + §3.1 已修复节在位 (列着 ['PIN-MISMATCH', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'MECH/service_port_check.py` 的 md5 锚点 (门禁 **G5b**)'])
----------------------------------------------------------------------------------------------------
【结论】21/23 组检查通过 | FAIL 2 组
口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**。
          本闸守的是 **demo 板当前成立的条目**, 不是'54 项全绿'。
          ★ 6 个 PCB 类 id 仍是 FAIL 是**正确状态** (排队等原理图定稿), 不是缺陷。
          ★ ISS-224: `PIN-MISMATCH` 是**被 ISS-220 真修好了**, 不是被调没 ⇒ 留痕在 §2 第 05 行 + §3.1。
====================================================================================================
```

**步骤 B ★= 只把锚点 `md5` 回滚到更旧的 `611c3ba3…` (派单里的 prev_md5) ★⇒ 同样必须变红**

```text
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
  [FAIL] G5b   受保护文件 md5 逐字节未变 (板/.kicad_pro + 4 个 check 脚本 + 网表/脚表)
         HW/netlist_v1.csv: e06c1dd633566aa44732762c2ff99d1c != 611c3ba3db3dc7de7213063375b96d01
  [FAIL] C21   真源变更台账对账 (网表/脚表: 锚点 ↔ 落表台账 ↔ 盘上真源, 三方一致)
         HW/netlist_v1.csv: 盘上 md5 e06c1dd633566aa44732762c2ff99d1c != 锚点登记 611c3ba3db3dc7de7213063375b96d01 (真源被换了或锚点过期)
  [OK ] C22   PIN-MISMATCH 独立复核 (P9 页声明 vs 网表实际 + d6 新旧口径)
         网表实读 CONN_LIGHT 22p / CONN_CAM 31p / J_CHG 10p; P9 声明 CONN_LIGHT [22] / CONN_CAM [31] / J_CHG [10]; 旧口径 0 处 / 新口径 3 处
  [OK ] G6    定性表 54 项全覆盖 (项号一个不缺) 且处置栏不留空/不写'待定'
         表内 54 行 / 应 54; 缺项号 = 无; 多余项号 = 无; 处置留空或待定 = 无
  [OK ] G6b   16 条 FAIL 每条都有明确去处 (修掉/出规格/登记 need 给 main/排队等原理图定稿)
         FAIL 行 16 条; 去处不在受控词表里的 = 无
  [OK ] G7    分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)
         实测 value = 25.00
  [OK ] G8    已修复的留痕必须在场 (PIN-MISMATCH 行 + §3.1「已修复 (留痕)」节)
         §2 行在位 (判定 = ✅ PASS, 备注带 ISS-220/落表) + §3.1 已修复节在位 (列着 ['PIN-MISMATCH', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'MECH/service_port_check.py` 的 md5 锚点 (门禁 **G5b**)'])
----------------------------------------------------------------------------------------------------
【结论】21/23 组检查通过 | FAIL 2 组
口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**。
          本闸守的是 **demo 板当前成立的条目**, 不是'54 项全绿'。
          ★ 6 个 PCB 类 id 仍是 FAIL 是**正确状态** (排队等原理图定稿), 不是缺陷。
          ★ ISS-224: `PIN-MISMATCH` 是**被 ISS-220 真修好了**, 不是被调没 ⇒ 留痕在 §2 第 05 行 + §3.1。
====================================================================================================
```

**步骤 C ★= 按备份逐字节装回 ⇒ 必须又绿**

```text
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
         台账可查 = ['HW/SCHEMATIC_LANDING_V1_LANDED.md', 'HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md', 'HANDOFF/2026-11-16_hw-lead_ISS233_21条未落表归因与拍板即落清单.md', 'HANDOFF/2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md', 'HANDOFF/2026-11-16_hw-lead_ISS249_F1落表.md', 'HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md']; 对上 = ['HW/netlist_v1.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-257)', 'HW/netlist_v1_pins.csv ← HW/SCHEMATIC_LANDING_V1_LANDED.md (ISS-257)']
  [OK ] C22   PIN-MISMATCH 独立复核 (P9 页声明 vs 网表实际 + d6 新旧口径)
         网表实读 CONN_LIGHT 22p / CONN_CAM 31p / J_CHG 10p; P9 声明 CONN_LIGHT [22] / CONN_CAM [31] / J_CHG [10]; 旧口径 0 处 / 新口径 3 处
  [OK ] G6    定性表 54 项全覆盖 (项号一个不缺) 且处置栏不留空/不写'待定'
         表内 54 行 / 应 54; 缺项号 = 无; 多余项号 = 无; 处置留空或待定 = 无
  [OK ] G6b   16 条 FAIL 每条都有明确去处 (修掉/出规格/登记 need 给 main/排队等原理图定稿)
         FAIL 行 16 条; 去处不在受控词表里的 = 无
  [OK ] G7    分片 claim `mech_hinge_stack_fixed_mm` = 25.00 (ISS-206 裁 2 的 16p/20p/4p/10p)
         实测 value = 25.00
  [OK ] G8    已修复的留痕必须在场 (PIN-MISMATCH 行 + §3.1「已修复 (留痕)」节)
         §2 行在位 (判定 = ✅ PASS, 备注带 ISS-220/落表) + §3.1 已修复节在位 (列着 ['PIN-MISMATCH', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv` 的 md5 锚点 (门禁 **G5b / C21**)', 'MECH/service_port_check.py` 的 md5 锚点 (门禁 **G5b**)'])
----------------------------------------------------------------------------------------------------
【结论】23/23 组检查通过 | FAIL 0 组
口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); **实物 [实测] = 0 条**。
          本闸守的是 **demo 板当前成立的条目**, 不是'54 项全绿'。
          ★ 6 个 PCB 类 id 仍是 FAIL 是**正确状态** (排队等原理图定稿), 不是缺陷。
          ★ ISS-224: `PIN-MISMATCH` 是**被 ISS-220 真修好了**, 不是被调没 ⇒ 留痕在 §2 第 05 行 + §3.1。
====================================================================================================
```

★**还原校验**: A / B / C 三步走完后, `MECH/HW_CROSS_REVIEW_TRIAGE.md` md5 = `920b497b3664e40aebc23f2ea63463c2` = 本轮开工前基线 (★逐字节相同★) ★

### ★附2.5 B5′ 受保护 md5 前后对照 (★本机自己跑出来的, ★没抄别人的★)

| # | 文件 | 本轮开工前 md5 (★2026-11-17 05:0x 实跑★) | 本轮交卷时 md5 (★实跑★) | 变了? |
|---|---|---|---|---|
| 1 | `HW/PCB/demo_mainboard.kicad_pcb` (板) | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | 否 |
| 2 | `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | `3e504d2be83152e337949723e909be1b` | 否 |
| 3 | `HW/netlist_v1.csv` (网表 · 台账管理真源) | `e06c1dd633566aa44732762c2ff99d1c` | `e06c1dd633566aa44732762c2ff99d1c` | 否 |
| 4 | `HW/netlist_v1_pins.csv` (脚表 · 台账管理真源) | `287e7861a0d1007748d92d9fbecdd490` | `287e7861a0d1007748d92d9fbecdd490` | 否 |
| 5 | `HW/BOM_v1.csv` (BOM · 供对照, 不在 MECH 锚点管辖内) | `94642d07a69e8d60dd2af57f69b93607` | `94642d07a69e8d60dd2af57f69b93607` | 否 |
| 6 | `MECH/check_demo_struct_truth.py` (门禁脚本) | `4ae5827e986f1aebb108c5aa2a475074` | `4ae5827e986f1aebb108c5aa2a475074` | 否 |
| 7 | `MECH/service_port_check.py` | `db58ff6a2afc28b8bf517e3c57c56bc1` | `db58ff6a2afc28b8bf517e3c57c56bc1` | 否 |
| 8 | `MECH/hinge_usb_check.py` | `3425bc141508de8a35f34c7cf7b803e8` | `3425bc141508de8a35f34c7cf7b803e8` | 否 |
| 9 | `MECH/hw_cross_review_check.py` | `e521387b87b0fcdf9f22d56f14199967` | `e521387b87b0fcdf9f22d56f14199967` | 否 |
| 10 | `MECH/display_biosafety_v2_check.py` | `29c77fc3fc823048b1d96c9500d28dd7` | `29c77fc3fc823048b1d96c9500d28dd7` | 否 |
| 11 | `MECH/HW_CROSS_REVIEW_TRIAGE.md` (★锚点所在文件★) | `920b497b3664e40aebc23f2ea63463c2` | `920b497b3664e40aebc23f2ea63463c2` | ★**否 (★本轮零改动★)** ★ |

★**逐行改前改后**: ★**本轮 MECH/ 与 HW/ 零文件改动 ⇒ 无 diff 可贴** ★ (★`MECH/HW_CROSS_REVIEW_TRIAGE.md` 改前 = 改后, 逐字节同 `920b497b…`★) ⇒ ★**唯一被写的是本交卷单 (追加附2) + 自己分片 (`state/fragments/mech.yaml`)** ★

### ★附2.6 B6′ 边界自证 (逐条)

| # | 边界 | 自证 |
|---|---|---|
| 1 | ★**零落表** (网表 / 脚表 / BOM 一个字节不许动) ★ | ✅ `HW/netlist_v1.csv` mtime 仍 `2026-11-16 22:25:14` · `HW/netlist_v1_pins.csv` mtime 仍 `2026-11-16 22:25:14` · `HW/BOM_v1.csv` md5 同 ★ |
| 2 | ★**零外发** ★ | ✅ 本单没发任何邮件 / 询价 / 问询 / 采购 / 外部请求 ★ |
| 3 | ★**零实物** ★ | ✅ 实物 [实测] = 0 条 (★MECH 侧纯锚点复核 + 门禁复跑★) ★ |
| 4 | ★**不碰 `HW/` 与 `SW/`** ★ | ✅ `HW/` 只读 (md5/mtime 全同) · `SW/` 一个字节没读没写 ★ |
| 5 | ★**不碰布线 / 布局 / 板框** ★ | ✅ 板 md5 同 · 板框四数 (60.00/30.00/1.00/3.33g) 一个没碰 ★ |
| 6 | ★**不改判据阈值** ★ | ✅ 门禁脚本 md5 同 (阈值 `cavity_req` 4.50 / `CRIT` 0.60 / `cav_v` 38.00 / `duct_v` 6.00 一个没动, G5 反向用例 2/8 仍能抓红) ★ |
| 7 | ★**不替老板拍板** ★ | ✅ 本轮没拍任何待拍项 (板长 / 板厚 / 腔体 / U-1~U-4 一条没拍) ★ |
| 8 | ★**不自签 issue_log** ★ | ✅ `state/issue_log.yaml` 只读 (★ISS-253 / ISS-259 的 `verified` 是 main 自己落的, 不是本单★) ★ |
| 9 | ★**别把整份脚本重写 (只改锚点常量)** ★ | ✅ 本轮连锚点常量都没改; 反向自证期间的临时改动用 `cp` 按备份还原, 还原后 md5 = 基线 ★ |
| 10 | ★**只写自己分片** ★ | ✅ `state/frag_write.py --agent mech-lead` ⇒ 只动 `state/fragments/mech.yaml`; `hw.yaml` / `sw.yaml` / `pm.yaml` 零字节 ★ |

### ★附2.7 B4′ 接口取值声明 (interface_claims)

| key | value | note |
|---|---|---|
| `mech_netlist_md5_anchor_current` | ★**网表 `e06c1dd633566aa44732762c2ff99d1c` / 脚表 `287e7861a0d1007748d92d9fbecdd490`** ★ | ★**锚点现值 (第 6 跳 / R-06 · by `ISS-257` · landed_at `2026-11-16 21:22`)** ★ ⇒ ★**上一跳 (本单 ISS-253 / R-05) 的 `16ac89f77c25a3f61834cc7ebcd78a7f` 已被它取代** ★ · ★**依据**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 L1069/L1070 (四项同行) + 本机 `md5sum` + 门禁 G5b/C21 现场判绿 ★ |
| `mech_netlist_md5_anchor_jump_chain` | ★**ISS-220 → ISS-223 → ISS-233 → ISS-243 → ISS-249 → ISS-257** ★ | ★**留痕 R-02 ~ R-06 在 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §3.1, 每一跳都有旧 md5 / 新 md5 / 落表单号 / 复现命令** ★ |

### ★附2.8 待 main 处置 (★本单不代拍, 不自签 issue_log★)

| # | 事项 | 我的建议 (★建议 ≠ 拍板★) |
|---|---|---|
| 1 | ★**ISS-253 派单在队列里重复触发** (★单子 2026-11-16 20:0x 就已 verified, 现在又来一次★) | ★**建议按「已被 ISS-259 (第 6 跳) 覆盖」关单 / 撤单, 不必再派 mech-lead 重锚** ★ ⇒ ★**派单本身写着「文件 = `MECH/check_demo_struct_truth.py`」也不成立 (★锚点不在那个脚本里, 在 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `MECH_ANCHORS` 块★) —— 这点 2026-11-16 20:07 原交卷单 §0.1 已写明, 建议以后派单直接写锚点文件★** ★ |
| 2 | ★**机制建议 (★我这边能自己做的已经做了, 不需要 main 拍板★)** | ★**H-1 重锚每来一次上游落表就要手工跳一次, 跳了 6 次; 本域新门禁 `MECH/check_hinge_fpc_truth.py` (ISS-240) 已改成【网表/脚表 md5 一律现场解析, 一律不写死】⇒ 建议其余锚点也照此收口, 否则【一落表就红】会一直重复** ★ |
| 3 | ★**本轮无未决项 / 无卡点** ★ | ✅ |

### ★附2.9 复现命令 (★main 可原样跑★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ① 现状 (应 rc=0 · 23/23 · FAIL 0)
python3 MECH/check_demo_struct_truth.py; echo "rc=$?"
# ② selftest (应 rc=0 · 14/14)
python3 MECH/check_demo_struct_truth.py --selftest; echo "rc=$?"
# ③ 盘上真源 md5 (应 = 锚点现值)
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv
# ④ 锚点现值 (YAML 逐字段回读)
python3 - <<'PY'
import re, yaml
t = open("MECH/HW_CROSS_REVIEW_TRIAGE.md", encoding="utf-8").read()
blk = re.search(r"# BEGIN MECH_ANCHORS(.*?)# END MECH_ANCHORS", t, re.S).group(1)
a = yaml.safe_load(blk)["anchors"]
for e in a["source_ledger"]["entries"]:
    print(e["file"], e["md5"], e["prev_md5"], e["by"], e["landed_at"])
PY
# ⑤ 本轮受保护 md5 前后对照 (11 件)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv \
        HW/netlist_v1_pins.csv HW/BOM_v1.csv MECH/check_demo_struct_truth.py \
        MECH/service_port_check.py MECH/hinge_usb_check.py MECH/hw_cross_review_check.py \
        MECH/display_biosafety_v2_check.py MECH/HW_CROSS_REVIEW_TRIAGE.md
```

### ★附2.10 本轮自用临时物 (★真盘零临时文件★)

| 路径 | 说明 |
|---|---|
| `/tmp/iss253_triage.bak` | ★**锚点文件的逐字节备份 (反向自证的还原源)** ★ |
| `/tmp/iss253_mutate.py` | ★**定点改锚点 4 字段的临时脚本 (★只改 `source_ledger.entries[0]`, 判据逻辑一个字节不动★)** ★ |
| `/tmp/iss253_probe.sh` | ★**反向自证驱动脚本 (★步骤 0/A/B/C + trap 还原 + 每步 md5 校验★)** ★ |
| `/tmp/iss253_logs/{0_baseline,A_iss253_target,B_rollback_old,C_restored,selftest}.log` | ★**五次门禁原样输出留档** ★ |

★**真盘上没留任何临时文件** (★反向自证全程 `cp` 按备份还原, 三步之后文件 md5 与基线逐字节同 = `920b497b3664e40aebc23f2ea63463c2`★) ★

---

### ★附2.11 ★分片被并发写覆盖的一次事故 + 补写留痕 (2026-11-17 05:1x)★

★**现象**: 交卷单附2 与门禁都在盘上, 但 `state/fragments/mech.yaml` 里本轮写的 3 条 claim (`mech_netlist_md5_anchor_current` / `mech_netlist_md5_anchor_jump_chain` / `iss253_redispatch_review_20261117`) ★**不见了** ★ (`grep -c` = 0), 而文件 mtime = `2026-11-17 05:13:13` (★= 本轮 `frag_write.py` 写入的那一秒★) ⇒ ★**判定: 同一秒内另一个 mech-lead 会话用【自己的陈旧快照】跑了 `frag_write.py` ⇒ 原子写把我的 3 条 claim 整段盖掉 (lost-update)** ★

★**处置 (不是「再写一遍就算」, 是【写完必校验 + 失败重试】)**: ★**补写脚本 `/tmp/iss253_reclaim.sh` = 写 → 逐条 `grep` 校验 → 不过就重试 (上限 5 次)** ★ ⇒ ★**第 1 次尝试即 3/3 在位 (行 4391 / 4398 / 4405)** ★ ⇒ ★**再跑 `state/merge.py` ⇒ rc=0 (`STATE.yaml` 已含这 3 条) · `state/gate_check.py` ⇒ rc=0** ★

★**教训 (★写进 MEMORY 了★)**: ★**同一 workspace 里多个 mech-lead 会话并发跑 `frag_write.py` ⇒ 原子写只保证「不写坏文件」, 不保证「不丢别人的条目」** ★ ⇒ ★**凡是用 `frag_write.py` 落交付, 必须【写完立刻 grep 校验自己的 key 在不在】, 最好带重试** ★ ⇒ ★**本次交卷物 (交卷单 / 记忆 / 日志) 都没被盖 (只有分片是共享可写文件) ⇒ 只有分片这一件需要重试补写** ★
