# ISS-391 cont1 · hw-lead · 工作笔记 (中途落盘 · L-13)

> 本文件是**过程留痕**, 不是交卷页。交卷页 = `HANDOFF/2026-11-24_hw-lead_ISS391_cont1_闸判据加固与夹具真件现读.md`

## 0 · 承接上一趟 (2026-11-24 21:44~21:51 被外部掐死)

- 上一趟 sessionId `4a27de2e-e519-4e85-b1f4-f2991a71baac` / runId `ac9f0d7f-6f58-4e30-babb-f4ccf1b23cf1`
- 21:44:38 起 → 21:51:51 止 (432.5s) · status=timeout · abortedLastRun=true
- `runTimeoutSeconds=5400` ⇒ **不是本单超时** ⇒ 同期 sw-lead / mech-lead 两条同一秒内 abort ⇒ 外部共因
- ⇒ 本趟是**续做趟**; 上一趟**只做了备份**, 真件一个字未改

## 1 · 本趟开工时盘上实读 (22:0x)

```
$ md5sum HW/check_fts_land_drill_same_batch.py
dabc12000b6cecb1769bb16df09f1abb   ★与 ISS-396 签收基线逐字相同 ⇒ 上一趟没动过真件
```

```
$ cat logs/iss391/md5_before.txt
00b0ea5bae70b7f663b55b9b80014d03  HW/PCB/BOARD_ONEPASS_WORKPACKET.md
192873f6c977b376c28785824a82f9f1  HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
fc37ea0eee9cea6a1f2b91e3d2f581dc  HW/check_onepass_preflight_coverage.py
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb
6aee500e60ba0732f83a9cf557ba90ab  HW/netlist_v1.csv
9174309df1ec9411ac8e8d9e80ee386a  HW/netlist_v1_pins.csv
5b9993992405904a60ac96a020b375d8  HW/BOM_v1.csv
HW/PCB/demo_mainboard.kicad_pcb 4940213 2026-11-06 07:07:17.362193413 +0800
```

- `logs/iss391/selftest_before.log` (21:44, 2185 B) = 改前 `--selftest` 逐字输出 = **14/17 · 末行 `SELFTEST FAILED`**
- `logs/iss391/bare_before.log` (21:44, 1205 B) = 改前裸跑 = **7/7 全绿 rc=0**
- ⇒ ★**改前基线已在盘上** (上一趟落的) ⇒ 本趟不重复落, 直接引用

## 2 · 真件 §0.2 ③ 那一项的逐字原文 (本机实读 · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L47)

```
③ `J_DEBUG`/`J_UART` 排针 land 0.50→1.27mm + 钻孔 0.65→0.71mm
   (★ISS-391·落 FTS 必须用 Samtec 官方 Ø0.71 TYP (官网推荐 PCB 图 `.028 0.71 (TYP)`)·
    通用库件默认 (drill 0.65) 偏小 0.06·★同属这一项的两条腿, 不可只做其一★)
   (★E-1·实物排针落不进·main 18:4x 裁决: 按 1.27 定, 板 land 改★)
```

⇒ **动作腿 = 「钻孔 0.65→0.71mm」** (把动作词「钻孔」与改动作「0.65→0.71」绑在一起)
⇒ **解释括注 = 「(★ISS-391·落 FTS 必须用 Samtec 官方 Ø0.71 TYP (官网推荐 PCB 图 `.028 0.71 (TYP)`)·通用库件默认 (drill 0.65) 偏小 0.06·★同属这一项的两条腿, 不可只做其一★)」**
⇒ **动作腿与解释括注里都含「钻孔/drill」「0.71」「1.27」** ⇒ 旧判据 (纯子串命中) 两者都满足 ⇒ ★这就是 main 决定性实验假绿的机制

## 3 · 两级根因 (本趟自己复核, 不抄报告)

### (甲) 夹具层 — 真件已被 ISS-396 登记过 ⇒ 夹具二次注入 + 只删第一处 ⇒ 变异空操作

- 夹具常量 `WORKPACKET_DRILL_LEG` 与真件那一段**逐字不同** (真件多了「(官网推荐 PCB 图 `.028 0.71 (TYP)`)」「通用库件」「★」三处)
- `make_fixed_workpacket()` 是**无条件**把常量塞进去 (`text.replace("排针 land 0.50→1.27mm", WORKPACKET_DRILL_LEG, 1)`)
  ⇒ 真件已经有登记了 ⇒ 沙盒里那条腿**出现两次**
- 反向用例 ① 只做 `wp03.replace(WORKPACKET_DRILL_LEG, "排针 land 0.50→1.27mm")` (替换**第一处**)
  ⇒ ★真件那一处**原封不动** ⇒ D1 照样查到「钻孔」+「0.71」⇒ 仍判绿 ⇒ **用例假绿**
- ② ③ 同型: `make_fixed_preflight(..., add_desc=False/add_crit=False)` 是在**真件基础上再改**
  ⇒ 真件那一列 (ISS-396 18:32 已落) **删不掉** ⇒ D2/D3 照样绿

### (乙) 判据层 — D1/D2/D3 只做子串命中 ⇒ 解释性文字冒充动作腿

- D1 (L318~L345): ① `has_drill(text)` ② `"0.71" in text` ③ `"1.27" in text`
- D2 (L347~L380): `has_drill(desc)` + `"0.71" in desc`
- D3 (L382~L410): `has_drill(crit)` + `"0.71" in crit`
- ⇒ 三条都可能被**解释性文字**满足 ⇒ ★判据被削弱

## 4 · 本趟要做的事 (§三 逐条)

- 3-1 判据层: D1/D2/D3 → 「★动作腿命中★」; 解释性括注不得满足判据
- 3-2 夹具层: `--selftest` → 【真件现读】; 变异从真件当前原文派生; 不依赖与真件逐字相等的写死常量; 变异干掉该腿**全部出现处**; 夹具识别「真件已登记过」并跳过重复注入
- 3-3 重签留痕: 追加一节 (改前/改后 md5 + 行号 + 改前/改后原文 + 为什么 + 派单人 + 审签人 + 证据留档路径 + 「板/网表/脚表/BOM/既有页正文一个字未改」)
- ★★决定性实验必须写进夹具并留证: 删动作腿留解释 ⇒ D1 红; ③ 只剩 pitch ⇒ D1 红

## 5 · 硬边界 (本趟自守)

零写板 · 零落表 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 未自签 issue_log ·
只写自己分片 `state/fragments/hw.yaml` (走 `state/frag_write.py`) ·
板三证 `611b869e…` / `6aee500e…` / `9174309d…` / `5b999399…` 逐字节未动 ·
D4/D5/D6/D7 一条不许碰

---

## 6 · 本趟完成记录 (2026-11-24 22:0x~22:5x · hw-lead)

★**交卷页**: `HANDOFF/2026-11-24_hw-lead_ISS391_cont1_闸判据加固与夹具真件现读.md`
★★**在上一趟 21:44 建的骨架页上填实 B1~B6·未新建第二页**★ (★gate_check Q1 按【最新一份】评分·不能落到骨架上★)

### 6-1 · 交付物清单 (★全部本机实跑★)

| # | 交付物 | 状态 |
|---|---|---|
| 1 | ★`HW/check_fts_land_drill_same_batch.py`★ (★唯一改动的已签收件★) | 判据层 + 夹具层改完 · ★**追加了 ISS-391 cont1 重签留痕节**★ · md5 `dabc12000b6cecb1769bb16df09f1abb` → `131f7edd39ecedec55a61917896a3c98` |
| 2 | ★交卷页 (★B1~B6 六段填实★)★ | 机器核: `check_blocks` 6/6 True · 证据标签 4 个 · 未填空段 0 |
| 3 | ★`logs/iss391/` 留证 11 件★★ | `selftest_before.log` · `bare_before.log` · `selftest_after.log` · `bare_after.log` · `decisive_experiment.log` · `gate.diff` · `md5_before.txt` · `md5_after.txt` · `merge.log` · `gate_check.log` · `cont1_worknotes.md` |

### 6-2 · 验收读数 (★全部本机实跑·★rc 全 0★)

| 命令 | rc | 结果 |
|---|---|---|
| `python3 HW/check_fts_land_drill_same_batch.py --selftest` | ★0★ | ★**19/19 PASS · ALL TESTS PASS**★ (★改前 14/17 · rc=1 · SELFTEST FAILED★) |
| `python3 HW/check_fts_land_drill_same_batch.py` | ★0★ | ★**7/7 全绿**★ |
| `python3 tmp/iss391/decisive_experiment.py` | ★0★ | ★**三个实验全部成立**★ |
| `python3 HW/check_onepass_preflight_coverage.py` | ★0★ | 回归通过 |
| `python3 HW/check_preflight_regen_idempotent.py` | ★0★ | 回归通过 |
| `python3 state/merge.py` | ★0★ | STATE.yaml 已刷新 |
| `python3 state/gate_check.py` | ★0★ | ★**Q1 18/18**★ |
| 板三证 md5 | — | ★**611b869e… / 6aee500e… / 9174309d… / 5b999399… 逐字节未动**★ |

### 6-3 · ★★决定性实验 (★main 那个实验·★现在红★) ★★

- ★**实验③ (删动作腿留解释) ⇒ D1 红**★ (★改前假绿★)
- ★**实验③b (③ 只剩 pitch) ⇒ D1 红**★
- ★**对照 (真件原样) ⇒ D1 绿**★ (★判据没被改松★)
- ★★**两条实验已固化进夹具**★ (★用例 ① 与 ⑯★) ⇒ 以后谁把判据改松这两条立刻红

### 6-4 · 分片登记 (★全部走 `state/frag_write.py`·★禁止 `open(p,"w")`★)

- 产出物 3 条 (★闸 / 交卷页 / 留证目录★)
- interface_claims **12 条**
- needs_from **5 条 · 全部 `to=main` · 一条不代拍**
- ★**去重也走 `--set-json` 通道**★ (★本单自己写重复的 15 条已清·别人的历史重复一条没碰★)
- 台账 status 未动 (★只更新了 hw.yaml 自己的 `status.phase`★)

### 6-5 · ★★边界自证 (★8 条全过★) ★★

零写板 · 零落表 · 零改既有页正文 · 只改一道闸 · 零挂链 (`state/gate_check.py` md5 未动) · 零外发 (未调用任何发信工具) · 不代拍 (5 条 needs 全 to=main) · 不自签 issue_log

★**★本单【不自签】· ISS-391 cont1 必须由 main 重签·verify_by = main★** ★

### 6-6 · 追加: 夹具【未登记路径】双向复核 (22:5x)

★**目的**: 证明判据既没改松 (未登记就红) 也没改得过严 (注册了就绿) ⇒ 夹具两条路径都实测通 ★

- ★**未登记副本** (★把真件里的改钻孔动作腿 + 验收手段里的读钻孔命令都去掉·别的字不动★) ⇒ **D1+D2+D3 红** ✔
- ★**同一副本 + 夹具的派生注入** (★按真相页机器块派生·不是写死常量★) ⇒ **全绿** ✔
- 留证: `logs/iss391/unregistered_path.log` · 脚本 `tmp/iss391/unregistered_path.py`

### 6-7 · 追加: D4~D7 逐字未改的机器核

```
$ python3 - <<'PY'   # 用 difflib 抓函数体逐字比
d4: ★逐字未改★   d5: ★逐字未改★   d6: ★逐字未改★   d7: ★逐字未改★
d1: 已改 (★符合本单要求★)   d2: 已改   d3: 已改
阈值 "0.71": old 9 次 / new 9 次   (★口径未动★)
PY
```

★**issue_log 未签**: `state/issue_log.yaml` 里 ISS-391 仍是 `status=fixing · verify_by=main` ⇒ ★**本单没有自签**★ ★
