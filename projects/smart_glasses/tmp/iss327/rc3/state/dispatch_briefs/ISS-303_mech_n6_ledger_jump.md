# ISS-303 · mech-lead 任务书 —— ★★【MECH 侧那 2 道闸的 N6: 只认硬基线, 不认【合法落表跳】⇒ 落表一次就假红】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-303
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 01:0x** ★
> ★**性质**: ★**内部活 · 闸机制类 · 零写板 · 零落表** ★ ⇒ ★**外发**: ★**零外发** ★

---

## ★① 病灶 (★main 2026-11-18 00:5x 本机实跑, 原样 rc, 不抄任何 agent 报告★)

★**背景**: ★**老板 09:49 拍板「按照你的建议执行」⇒ ISS-283 落表 (11-17 10:58) ⇒ 网表/脚表/BOM 三件 md5 变过一轮** ★
⇒ ★**ISS-299 (hw-lead) 已把 HW 侧的 `HW/check_pin_function_labels.py` / `HW/check_onepass_preflight_coverage.py` 改成【落表台账链头口径】** ★
⇒ ★**但 MECH 侧这 2 道闸还是【硬基线口径】** ★

★**然后 2026-11-18 00:21, ISS-302 又合法落表一次 (C_SYS / SYS_CHG 必装 + BOM 加 20 µF)** ⇒ ★**MECH 侧那 2 道闸当场转红** ★

★**main 00:5x 实跑 (原样 rc)**:
```bash
$ python3 MECH/check_onepass_struct_crosscheck.py; echo "rc=$?"     # ★rc=1★
$ python3 MECH/check_onepass_mech_release.py; echo "rc=$?"          # ★rc=1 (汇总: 绿 5 / 红 1)★
$ python3 state/gate_check.py; echo "rc=$?"                          # ★rc=1 (Q7 钉板 md5 闸链 8/9)★
```
★**红的原文 (main 原样贴)**:
```
  ✗ N6 受保护件被改: HW/netlist_v1.csv 基线 37f62ac3f0b81d92ca7d48fdea717f07 ⇒ 现值 6aee500e60ba0732f83a9cf557ba90ab
  ✗ N6 受保护件被改: HW/netlist_v1_pins.csv 基线 a4270120454aedf7a23c92cd8985c8a6 ⇒ 现值 9174309df1ec9411ac8e8d9e80ee386a
  ✗ N6 受保护件被改: HW/BOM_v1.csv 基线 5d02bece9477ffce5fbe0193c7d5cce4 ⇒ 现值 5b9993992405904a60ac96a020b375d8
```
★**⇒ 真源在 `MECH/check_onepass_struct_crosscheck.py`**: N6 用 `PROTECTED_LEDGER_MD5` (★**网表/脚表/BOM 三件的硬基线, 来自 ISS-290 任务书基线★**) 逐个比 md5 ⇒ ★**盘上一变就判「受保护件被改」★** ⇒ ★**它分不出「合法落表」和「有人手改」** ★

★**★这为什么致命**: ★**MECH 侧准出汇总闸 (ISS-300) 的口径是「汇总 rc=0 ⇒ 结构侧可以出 Gerber」⇒ 现在它恒红 ⇒ 「板只改一次」那一趟的结构侧准出被一个【假红】挡住 ⇒ 现场极可能误读成「板改坏了」⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★

★**★这就是 ISS-296 (MECH 侧接合法改板通道) 的【落表跳版】**: ★**合法改板跳 (板 md5 变) 当时接了, 合法落表跳 (网表/脚表/BOM md5 变) 当时没接** ★

---

## ★② 病灶定位 (★main 已查到行号级★)

`MECH/check_onepass_struct_crosscheck.py`:
- ★L66~L67 `PROTECTED_LEDGER_MD5` = ★**网表/脚表/BOM 三件的硬基线常量** ★
- ★L25 `N6 ★**受保护 5 件 md5 逐字节不变** (板 / .kicad_pro / 网表 / 脚表 / BOM)` ★
- ★L747~L761 `check_n6()` = ★**逐个比 md5 ⇒ 不等就记 `N6 受保护件被改`** ★
- ★L1105~L1118 反向用例⑦ = ★「改受保护件 ⇒ N6 红」★ ⇒ ★**这条必须继续成立** ★

★**★HW 侧已经跑通的同款口径 (★照抄判据方向, 不照抄代码★)**:
`HW/check_workpack_state_values.py` 的 V6 段 (★main 00:5x 实跑原样★):
```
  ✔ HW/netlist_v1.csv md5 == 落表台账登记 6aee500e60ba0732f83a9cf557ba90ab (★落表单号 ISS-302·台账 L1437·§16.2★) ⇒ 未被绕过改动
  ✔ HW/netlist_v1_pins.csv md5 == 落表台账登记 9174309df1ec9411ac8e8d9e80ee386a (★落表单号 ISS-302·台账 L1437·§16.2★) ⇒ 未被绕过改动
  ✔ HW/BOM_v1.csv md5 == 落表台账登记 5b9993992405904a60ac96a020b375d8 (★落表单号 ISS-302·台账 L1437·§16.2★) ⇒ 未被绕过改动
```
★**★台账真源 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★ISS-302 那一跳在 §19 + `<!--ISS302_ROWS-->` L1451~L1455★)** ★
★**⇒ 本单要做的是: ★**让 N6 的判决源从【硬基线常量】换成【硬基线 ∪ 落表台账登记值】**★ ★

---

## ★③ 要交的四件 (★每件都能独立验收★)

### ★B1 · N6 判决源改造 (★`MECH/check_onepass_struct_crosscheck.py`★)
★**硬要求 (★破一条就不合格★)**:
1. ★**判据方向不许变**: ★**盘上 md5 ∉ 合法集合 ⇒ 仍然必须红** ★ (★"被改坏"要红, 这条不许松★)
2. ★**合法集合 = 硬基线 ∪ ★落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里该文件登记过的 md5★** ⇒ ★**读台账, 不许把新 md5 写死成常量** ★
3. ★**fail-closed 三条一条都不许动/不许弱化** ★:
   - ★台账里**找不到**该文件 ⇒ **红** (不许"找不到就当没改") ★
   - ★台账**链头不唯一** / 链断 ⇒ **红** ★
   - ★台账**解析不出来** ⇒ **红** (★不许 try/except 吞掉★) ★
4. ★**板 2 件 (`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro`) 的【合法改板通道】(ISS-296 已接) 一个字不许动** ⇒ ★**N6 对这 2 件的行为必须逐字不变** ★
5. ★**不许放宽别的判据** (N1~N5 / 反向用例⑦ / 阈值) ★

★**★做法提示 (★ISS-298 已验证过的同款形状, 你可参考★)**: ★**别自己写第二套台账解析** ⇒ ★**只读调用权威闸的现成 API** (★`SW/tools/check_demo_panel_spec.py` 里有 `check_r6_hard_protected()` / `load_sw_anchor()` 这类现成入口★ ⇒ ★**先 grep 看它现在还叫不叫这个名★) ⇒ ★**两个闸对同一盘面永远给同一个答案 ⇒ 口径零漂移** ★
★**若你决定走代码级耦合**: ★**必须登记一条 need 给 main** (★说明你依赖了哪个模块的哪些名字 + 那些名字不许改, 否则你的闸会 fail-closed 恒红★) ★
★**若你决定自己读台账**: ★**必须写【反向用例】证明「台账里伪造一个 md5 ⇒ 盘上不符 ⇒ 仍红」** ★

### ★B2 · 反向用例 (★≥ 5 条, 每条贴原样 rc + 期望红组 vs 实际红组★)

| # | 构造 | 期望 |
|---|---|---|
| ① | ★**把网表 md5 改成一个台账里查不到的假值** ⇒ N6 | ★**红** ★ |
| ② | ★**把脚表 md5 改成一个台账里查不到的假值** ⇒ N6 | ★**红** ★ |
| ③ | ★**台账里把 ISS-302 那一行删掉 (链断) ⇒ 现值变回「不在合法集合」** ⇒ N6 | ★**红** ★ |
| ④ | ★**台账里出现两条指向同一文件的链头 (链头不唯一)** ⇒ N6 | ★**红** ★ |
| ⑤ | ★**反向用例⑦ 回归**: ★**沙盒里改板文件 ⇒ N6 仍红** (★ISS-296 那条不许被放松★) ⇒ ★`--selftest` | ★**红** ★ |
| ⑥ | ★**正向对照: 一切如常 (现值 == 台账链头) ⇒ N6** | ★**绿** (★证明闸不是恒红★) ★

★**★沙盒要求**: ★**反向用例必须在沙盒临时目录跑** ⇒ ★**真盘 5 件 md5 一个字节不许动** ★

### ★B3 · 回归 (★别的闸一条不许红★)
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_onepass_struct_crosscheck.py; echo "rc=$?"   # ★期望 rc=0★
python3 MECH/check_onepass_struct_crosscheck.py --selftest; echo "rc=$?"   # ★条数只许增不许减★
python3 MECH/check_onepass_mech_release.py; echo "rc=$?"        # ★期望 rc=0 (汇总 6 道闸全绿)★
python3 MECH/check_onepass_mech_release.py --json; echo "rc=$?"
python3 MECH/check_onepass_mech_sync.py; echo "rc=$?"
python3 MECH/check_mech_verdict_freshness.py; echo "rc=$?"
python3 MECH/check_demo_struct_truth.py; echo "rc=$?"
python3 MECH/check_board_frame_coords.py; echo "rc=$?"
python3 state/merge.py; echo "rc=$?"
python3 state/gate_check.py; echo "rc=$"
python3 state/issue_check.py; echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```
★**★注意**: ★`state/gate_check.py` 现在是 rc=1 (★钉板闸⑥ = `HW/check_workpack_state_values.py` 3 条文档现值漂★) ⇒ ★**那是 ISS-304 (hw-lead) 的活, 不是你的** ⇒ ★**你交卷时它可能还是红的 ⇒ 原样写 + 注明归属, 不许自己去改它** ★
★**★受保护 5 件的 md5 判据**: ★板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · ★**这三件 (网表/脚表/BOM) = `6aee500e…` / `9174309d…` / `5b999399…` (ISS-302 落表后的现值, 本单只读不许动)** ★

### ★B4 · 交卷物 (★4 件★)
1. ★**交卷单** `HANDOFF/2026-11-18_mech-lead_ISS303_N6合法落表跳.md` (★B0 + B1~B6 六块齐全 + 反向用例原样 rc + 边界自证★) ★
2. ★**闸本体改动** `MECH/check_onepass_struct_crosscheck.py` (★只改 N6 判决源 + 补反向用例; ★阈值/其它判据不许动★) ★
3. ★**日志** `logs/iss303/` (★沙盒反向用例 + 全量回归的原样输出★) ★
4. ★**分片** `state/fragments/mech.yaml` (★走 `python3 state/frag_write.py --agent mech-lead` 原子写★ ⇒ ★**写完 `grep -c iss303` 校验 (★目标 ≥ 5★)★ ⇒ ★**不许用 `open(p,"w")`★) ★

★**★真判据 (★main 实测的坑★)**: ★`python3 state/check_report_placeholders.py < <交卷单>` **抓不到 `🔄 待填`** ⇒ ★**真判据是 `grep -cE "🔄|待填"` 必须 = 0** ★

---

## ★④ 边界 (★违反就是不合格★)

★**零写板** · ★**零落表** (★网表/脚表/BOM/台账/`state/p10_rows.json` 一个字节不许动★) · ★**不许改 `HW/` 任何文件与分片** (★`HW/check_workpack_state_values.py` 的红归 ISS-304★) ★
· ★**不许改 `SW/` 任何文件与分片** (★只读调用它的现成 API 不算改, 但名字不许动★) · ★**不许动 ISS-296 已经接好的合法改板通道** ★
· ★**不许放宽 fail-closed / 不许改基线常量去凑绿** · ★**零外发** · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** (★签字是 main 的活★) · ★**只写自己那一份分片** ★
· ★**实物 `[实测]` = 0 条** (★本机无板无量具⇒ 不许编★) · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

---

## ★⑤ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★
· ★**长任务一律 `nohup ... > logs/iss303/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★
· ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★
· ★**★闸本体改之前先备份一份 (★`cp` 到同目录 `.bak_20261118`★) ⇒ 改完能用它做【改前红/改后绿】对照** ★
