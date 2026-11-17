# ISS-288 · sw-lead 交卷单 · timing_check 补丁落地 (★情形二: ISS-283 已落 verified★)

- **单号**: ISS-288 · **owner**: sw-lead · **verify_by**: main
- **派活**: 项目总工 (main / moli) · 2026-11-17 14:2x · job cron `fb67af40` (ARS45 队列自动派活)
- **任务书**: `state/dispatch_briefs/ISS-288_sw_timing_check_patch_land.md` (6064 B · check_brief_commands --brief-file rc=0)
- **本单性质**: 内部活 · SW 侧门禁口径收口 · **零写板 · 零落表** ⇒ **续做** (把 ISS-285 的设计落地)
- **交付物**:
  1. 本交卷单 (B1~B6)
  2. `SW/tools/timing_check.py` 的改动 (★落表台账链头口径 + 前缀比对 bugfix + F4' 期望更新 + 自测新增用例★)
  3. 分片 `state/fragments/sw.yaml` (走 `state/frag_write.py --agent sw-lead` 原子写 + grep 校验)

★**本单零外发** ⇒ 全部结论来自**本机实跑**; 证据分级见 §7★

---

## ★★§A · 交卷后叠加说明 (★2026-11-17 17:5x · 续跑补记·★★必读: 下面 §5 的 md5 是【本单交卷时刻】的值, 与【现在盘上】不同★)★★

★**为什么有这一节**: ★**本单交卷 (15:2x) 之后, 同 agent 的后续单 ★`ISS-291` (ADC 满量程与判决对象口径收口, ★已 verified★) 在 `SW/tools/timing_check.py` 上又叠了一层** ⇒ ★**盘上现值与 §5 表格里的值不一样** ⇒ ★**main 验签时按【盘上现值】核, 别按 §5 的旧值核** ★

★**① 本单 (ISS-288) 落在文件里的那 6 个函数 · 与补丁件【逐字节相同】 [实测]** (★拿 `logs/iss288/sbx_base/SW/tools/timing_check.py` (★= ISS-288 补丁件 md5 `68c4becf…`★) 逐函数比对盘上现文件★):

| 函数 | ISS-288 补丁件 vs 盘上现文件 |
|---|---|
| `_dps()` | ★**逐字节相同**★ |
| `_device_dnp_rows()` | ★**逐字节相同**★ |
| `_netlist_baseline_state()` | ★**逐字节相同**★ |
| `netlist_md5_allowed()` | ★**逐字节相同**★ |
| `_bat_det_all_populated()` | ★**逐字节相同**★ |
| `_bat_det_verdict()` | ★**逐字节相同**★ |

⇒ ★**本单的判据逻辑一条都没被后续单动过** (★ISS-291 动的是【ADC 满量程 / 判决对象 VBUS_DET_D→BAT_DET / 落点脚表分类】那一段, 与本单的【网表锚点链头口径】+【BAT_DET 三颗必装期望】不相交★)★

★**② 盘上现值 vs §5 表格里的值 [实测]**:

| 文件 | §5 写的 (本单交卷时刻 15:2x) | ★**盘上现值 (17:5x)**★ | 说明 |
|---|---|---|---|
| `SW/tools/timing_check.py` | `68c4becffe6bcd708e388dba9d18a505` | ★**`cf09c921002937920bfa40701d523b33`**★ | ★**ISS-291 在同一文件上叠了一层** (mtime 15:59:51) ⇒ ★**不是本单被改回去**★ |
| `SW/SW_MD5_BASELINE_LEDGER.md` | `c5484ec677ebd52ad4ff87ab520ec77b` | ★**`83fafcf7d22d8fa999a1db74c781956d`**★ | ★**ISS-279 收口轮追加了 R-13 / R-14 两行【追加式留痕表】行** (mtime 17:52:39) ⇒ ★**§1 锚点块逐字节没动 (见 ③)★** |
| `SW/tools/check_demo_panel_spec.py` | `4e8f9aeaf45f95e120421d29bdaa333c` | ★**`4e8f9aeaf45f95e120421d29bdaa333c`**★ | ★**逐字节不变** (★本单硬约束: R6 判据逻辑不许动★)★ |

★**③ 本单硬约束「不许改 SW 台账 §1 的 `source_ledger.entries` 那两条」· 事后复核 [实测]** (★用本单起跑时的快照 `logs/iss288/SW_MD5_BASELINE_LEDGER.md.BEFORE` 比★):

```
$ diff <(sed -n '/BEGIN SW_MD5_ANCHORS/,/END SW_MD5_ANCHORS/p' logs/iss288/SW_MD5_BASELINE_LEDGER.md.BEFORE) \
       <(sed -n '/BEGIN SW_MD5_ANCHORS/,/END SW_MD5_ANCHORS/p' SW/SW_MD5_BASELINE_LEDGER.md)
★ §1 锚点块逐字节相同 (硬约束守住了) ★
```

★**④ 续跑复核 (★17:53~17:54 · 本趟本机实跑·原样·日志 `logs/iss288/41_final_acceptance.log` + `43_final_merge_gate_rerun.log`★)**:

```
$ python3 SW/tools/timing_check.py                                    → SELFTEST 85/85 通过, rc=0   (0 条 FAIL)
$ python3 SW/patches/ISS-288_timing_check_land/verify_iss288_land.py → ★7 条用例总判定: ✅ 全符合   rc=0
$ python3 SW/tools/check_demo_panel_spec.py                          → rc=0 (R1~R7 全过 · R6 绿)
$ python3 SW/tools/check_demo_panel_spec.py --selftest               → --- SELFTEST 22/22 通过 ---   rc=0
$ python3 HW/check_onepass_preflight_coverage.py                     → ✅ rc=0
$ python3 state/merge.py                                             → ✅ STATE.yaml 已刷新 (2026-11-17T17:54:18+08:00)   merge rc=0
$ python3 state/gate_check.py                                        → 【Q1 交付齐备率】18/18 个必填验收块齐全   gate rc=0
```

★**分母注记**: ★**`85/85` ≠ §5 里写的 `72/72`** ⇒ ★**差的 13 条是 ISS-291 加的 (★ISS-288 只加了 1 条 = REV-11★)** ⇒ ★**本单的判据一条没少 ★**★

★**⑤ 受保护 5 件 · 续跑复核仍逐字节不变 [实测]** (★17:5x · 与 §5 表格里的 BEFORE/AFTER 两列**同值**★):

```
611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb   (mtime 2026-11-06 07:07:17)
3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro   (mtime 2026-11-04 23:47:30)
37f62ac3f0b81d92ca7d48fdea717f07  HW/netlist_v1.csv                 (mtime 2026-11-17 12:30:22)
a4270120454aedf7a23c92cd8985c8a6  HW/netlist_v1_pins.csv            (mtime 2026-11-17 12:30:22)
5d02bece9477ffce5fbe0193c7d5cce4  HW/BOM_v1.csv                    (mtime 2026-11-17 12:30:22)
```

★**⑥ 一条过程留痕 (★不是本单造成的, 但 main 复跑时会撞上·先说在前面★)**:

★**`state/merge.py` 在 17:53:44 那一次返回 rc=2**, 原因 = ★**`state/fragments/hw.yaml` 有 2 条 `interface_claims` 缺 `key` 字段** (★`meta.incomplete_fragments` 点名 ★`file: hw.yaml`★) ⇒ ★**不是 sw.yaml 的问题 (★本单分片 `interface_claims` 缺 key 条数 = 0★)** ⇒ ★**hw-lead 在 17:54:00 又写了一次自己的分片** ⇒ ★**17:54:18 重跑 `merge.py` ⇒ rc=0** ⇒ ★**那是【并发写分片撞车】, 不是本单引入的缺陷** ★

⇒ ★**结论: 本单 (ISS-288) 的全部结论不受后续单叠加影响; main 验签按【盘上现值 + 上面 §A 的对照】核即可** ★

---

## §0 情形判定 (开工前置)

★**结论: 情形二 (ISS-283 已落表并 verified) ⇒ §1 / §2 的补丁必须落地★**

★**依据 (本机实查, 2026-11-17 15:0x~15:2x)**:

- ★**落表实况 [实测]** ★: 落表台账 §16 (★ISS-283 · 2026-11-17 12:30:23★) **L1371** = 网表 `87f2f792513584bee3d147883c8fb93b` ⇒ `37f62ac3f0b81d92ca7d48fdea717f07`; 本机直调判决源 ⇒ 链头 = `37f62ac3f0b8` (单号 ISS-283) ⇒ ★**情形二成立** ★ (详见 §1)
- ★**issue_log 读数 [实测]** ★: `state/issue_log.yaml` 的 ISS-288 = `status: fixing` / `fix_ref: null` / `verify_by: main` ⇒ ★**本单只读, 不自签** ★ (详见 §6.1 ⑥ 与 §8.3)
- ★**补丁已落盘 [实测]** ★: `SW/tools/timing_check.py` md5 = `68c4becffe6bcd708e388dba9d18a505` (= ISS-285 交卷单写死的套用后期望 md5, ★**逐字一致**★) ⇒ ★**本单交卷单里写的全是【已发生的既成事实】, 不是承诺** ★

---

## §1 B1 · 网表锚点 ×2 ⇒ 落表台账链头口径 (★与 R6 同源★)

★**一句话**: 同一个事实 («网表当前合法 md5 是多少») 原来有**两个判决源** ⇒ 授权落表后**一个绿一个红**; 本次修法落在「**让两个判据源同源**」, 不落在「放宽判据」★

★**根因 [源码]**:

| 判据 | 判决源 | ISS-283 落表后 |
|---|---|---|
| ① `SW/tools/check_demo_panel_spec.py` 的 **R6** | 落表台账 **链头** | 绿 ✅ |
| ② `SW/tools/timing_check.py` 的**网表锚点判据 ×2** | SW 台账 §1 锚点块里**冻结的 md5** | 红 ❌ |

★**改前判据文本 [实测]** (改前文件 = `logs/iss288/timing_check.py.BEFORE` · md5 `4cba20b1d0249b671632878c964b4bd7` · 本趟把它的 `_PROJECT_ROOT` 指回真盘后实跑):

```
BEFORE STATE      = BAD
BEFORE ALLOWED   = ['e06c1dd633566aa44732762c2ff99d1c']
BEFORE DETAIL     = 盘上真源 md5 37f62ac3f0b81d92ca7d48fdea717f07 ≠ 锚点登记 e06c1dd633566aa44732762c2ff99d1c (真源被换了或锚点过期)
BEFORE netlist_md5_allowed(disk37f62ac3f0b81d92ca7d48fdea717f07) = False
BEFORE netlist_baseline_ok()     = False
```

★**改后判据文本 [实测]** (改后文件 = `SW/tools/timing_check.py` · md5 `68c4becffe6bcd708e388dba9d18a505` · 本机直调):

```
STATE      = OK
ALLOWED(12)= ['13f59a43dbd3', '16ac89f77c25', '2f17650cfbef', '3215020b6d41', '34132f7e40a2', '37f62ac3f0b8', '611c3ba3db3d', '87f2f7925135', 'c78f991283cc', 'e06c1dd63356']
DETAIL     = 判决源 = HW/SCHEMATIC_LANDING_V1_LANDED.md 链头 37f62ac3f0b8 (单号 ISS-283) · 盘上 md5 = 37f62ac3f0b81d92ca7d48fdea717f07
DISK md5   = 37f62ac3f0b81d92ca7d48fdea717f07 | [:12] = 37f62ac3f0b8
netlist_md5_allowed(disk) = True
netlist_md5_allowed(bogus)= False
netlist_baseline_ok()     = True
```

★**改动位置 (行号 · 改后文件 `SW/tools/timing_check.py`)**:

| 行号 | 符号 | 改了什么 |
|---|---|---|
| **L209-222** | `_dps()` | **新增**: 动态 import `SW/tools/check_demo_panel_spec.py` (= R6 那份判决源实现); ★读不到 ⇒ 返回 `(None, 原因)` ⇒ 判红 (fail-closed, 不许降级)★ |
| **L225** | `_DPS = None` | **新增**: 模块级缓存 |
| **L228-235** | `_device_dnp_rows()` | **新增**: 读该位号【器件本体行】(type ∉ {NET,TP}) 的 dnp (★ISS-190 老教训: dnp 是行级, 拿该位号第一条行 = 假绿★) |
| **L238-296** | `_netlist_baseline_state()` | ★**判决源换掉**: 原来「自己扫落表台账 + 对锚点冻结 md5」⇒ 改成「直接用 R6 的 `sw_ledger_canonical_text()` + `sw_ledger_state()` 取**链头**」★ |
| **L299-301** | `netlist_baseline_ok()` | 逻辑未动, 只是判决源换了 |
| **L1569-1572** | 网表锚点 **×2** 两条用例 | 用例**名字逐字未改**, 底下判决源换了 ⇒ 改前红 / 改后绿 |

★**改前 → 改后 diff hunk 定位 [源码]** (`diff -u logs/iss288/timing_check.py.BEFORE SW/tools/timing_check.py` · ★**9 hunk** · 纯 hunk 体 **+156/-46** (含 `+++`/`---` 头行则 +157/-47)★):

```
@@ -193,8 +193,57 @@     ← ① _dps() / _device_dnp_rows() 新增 + 判据源 docstring
@@ -205,48 +254,46 @@    ← ② _netlist_baseline_state() 判决源换成台账链头
@@ -255,8 +302,17 @@    ← ③ netlist_md5_allowed() 改 12 位前缀 (见 §2)
@@ -1055,6 +1111,7 @@   ← ④ F4 链加 device_dnp 采集
@@ -1062,6 +1119,11 @@  ← ⑤ F4 链加 device_populated
@@ -1088,10 +1150,10 @@ ← ⑥ F4 verdict 文案数据驱动化 (见 §3)
@@ -1455,6 +1517,46 @@  ← ⑦ BAT_DET_REFS / _bat_det_all_populated / _bat_det_verdict (见 §3)
@@ -1545,9 +1647,9 @@  ← ⑧ F4' 用例期望值翻转 (见 §3)
@@ -1629,6 +1731,14 @@ ← ⑨ REV-11 反向用例新增 (见 §4)
```

★**四条不许破 · 逐条自证**:

| # | 不许破 | 自证 |
|---|---|---|
| ① | **判据方向不许变**: 盘上真源 md5 ∉ 台账登记的合法状态集合 ⇒ 仍必须红 | 改后实测 `netlist_md5_allowed(bogus) = False` (伪 md5 `deadbeefdead…` 判红); 沙盒用例①「伪造 md5」★期望红组 (2 条) = 实际红组 (2 条) ✅ (`logs/iss288/32_cont2_verify_iss288_land.log`) ⇒ 判据没被放松 |
| ② | **不许把「取不准」放宽成「取最近一条」** ⇒ fail-closed 三条 (链头不唯一 / 链断 / 链头无单号) 一条都不许动 | 改后代码 L269-283 三条 `return ("BAD", ...)` 逐条保留; 沙盒用例③链头不唯一 / ④链断 / ⑤链头无单号 三条 ★期望红组 = 实际红组 ✅ |
| ③ | **不许把落表台账当「锚点可写集合」** ⇒ 台账 append-only + 链完整性防线不许松 | 改后 L282-284 `orphan = {台账记录} - {链}` ⇒ 非空即红; L285-293 锚点副本**降级为历史留痕** (md5 必须在链上 + 落表单号必须与台账产出该 md5 的单号对得上 + 旧 md5 也必须在链上) ⇒ 台账仍不可写 |
| ④ | **不许弱化 ISS-275 已跑通的链头逻辑** ⇒ 链头实现**直接 import R6 那份** | `SW/tools/check_demo_panel_spec.py` md5 `4e8f9aeaf45f95e120421d29bdaa333c`, 与 `logs/iss288/check_demo_panel_spec.py.BEFORE` ★**逐字节相同** (`diff -q` ⇒ IDENTICAL)★ ⇒ 本单一个字节没碰它 ⇒ 链头 / 链 / 产出单号 三者逐字一致 |

★**实跑 rc [实测]** (本机 2026-11-17 15:1x · 日志 `logs/iss288/31_cont2_timing_check.log`):

```
$ python3 SW/tools/timing_check.py
...
SELFTEST 72/72 通过, rc=0
RC=0
```

---

## §2 B1-bugfix · md5 前缀比对口径 bug

★**一句话**: 落表台账里登记的 md5 是 **12 位前缀** (R6 也是按 12 位比), 但 `netlist_md5_allowed()` 改后拿 **32 位** md5 去做集合成员判断 ⇒ **永远比不中** ⇒ 那条判据**恒红 = 判据自毁** ⇒ 本 bugfix 把**比对口径**对齐到 12 位前缀 (★**只换口径, 不换判据方向**★)★

★**改前代码 [源码]** (`logs/iss288/timing_check.py.BEFORE` L257-259):

```python
def netlist_md5_allowed(md5: str) -> bool:
    """这个网表 md5 是落表台账登记过的状态之一吗 (落表前 / 落表后)?"""
    return md5 in _netlist_baseline_state()[1]
```

★**改后代码 [源码]** (`SW/tools/timing_check.py` L304-315):

```python
def netlist_md5_allowed(md5: str) -> bool:
    """这个网表 md5 是落表台账登记过的状态之一吗 (落表前 / 落表后)?

    ★★【ISS-285】落表台账里登记的 md5 是【12 位前缀】(★R6 也是按 12 位比★
      ⇒ 这里也按 12 位前缀比, 口径与判决源 (R6) 完全一致
      (★不然拿 32 位去比 12 位前缀 ⇒ 这条恒红 = 判据自毁★)。
    ★**判据方向一个字没变**: 盘上 md5 ∉ 台账登记的状态集合 ⇒ 仍必须红。★
    """
    if not md5:
        return False
    allowed = _netlist_baseline_state()[1]
    return str(md5).strip().lower()[:12] in {str(x).strip().lower()[:12] for x in allowed}
```

★**改前为什么会恒红 [实测]** (日志 `logs/iss288/10_prefix_bug_demo.log` · 原样贴):

```
=== 台账登记的『允许集合』全是 12 位前缀 (B1 换判决源后的真值) ===
allowed = ['13f59a43dbd3', '16ac89f77c25', '2f17650cfbef', '3215020b6d41', '34132f7e40a2', '37f62ac3f0b8', '611c3ba3db3d', '87f2f7925135', 'c78f991283cc', 'e06c1dd63356']

=== 旧口径 (ISS-285 §1.4 说的那个 bug): 32 位 md5 直接做集合成员判断 ===
  old: md5 in allowed            -> False   (★32 位 ∉ 12 位前缀集合 ⇒ 永远比不中 ⇒ 那条判据恒红 = 判据自毁★)

=== 新口径 (改后): 按 12 位前缀比 ===
  new: md5[:12] in {x[:12]}      -> True

=== 同一份真盘数据上, 只换比对口径的差 ===
  旧 = False  新 = True  ⇒ 差 = True
```

★**改后怎么比 [源码+实测]**: 取 **12 位前缀** 比, 且**两侧都做** `strip().lower()` 归一 (台账里的大小写 / 空白不许造成假红) ⇒ `str(md5).strip().lower()[:12] in {str(x).strip().lower()[:12] for x in allowed}`; ★**空 md5 直接判 False** (不许空串碰巧前缀匹配上某条)★

★**判据方向一个字没变 [实测]**:

| 输入 | 改后结果 | 含义 |
|---|---|---|
| 盘上真源 `37f62ac3f0b81d92ca7d48fdea717f07` | `True` | 盘上真源 == 台账链头 ⇒ 放行 (正常态) |
| 伪 md5 `deadbeefdead` ×3 | `False` | 盘上真源 ∉ 台账登记状态集合 ⇒ **仍必须红** ⇒ 判据没被放松 |
| 沙盒用例① (伪造盘上网表 md5 = `7fb8a2c9441539f06a60c2c057234011`) | ★期望红组 (2 条) = 实际红组 (2 条) ✅ | 链头对不上 ⇒ 两条锚点判据都红 |

★**实跑 rc [实测]** (本机 2026-11-17 15:1x):

```
$ python3 SW/tools/timing_check.py
SELFTEST 72/72 通过, rc=0
RC=0

$ python3 SW/patches/ISS-288_timing_check_land/verify_iss288_land.py
★7 条用例总判定: ✅ 全符合
RC=0
```

---

## §3 B2 · F4' 期望随落表更新 (★BAT_DET 三颗 DNP → 必装★)

★**一句话**: V-3 = E 落表把 BAT_DET 三颗从 **DNP** 翻成 **必装** ⇒ SW 侧 F4' 的期望值跟着翻 ⇒ ★**旧期望落表后变成过期事实 ⇒ 判红** ⇒ 本节把期望值随落表更新, 且★**判据强度不许比原来弱**★

★**改前值 [源码]** (`logs/iss288/timing_check.py.BEFORE`):

| 位置 | 改前文本 |
|---|---|
| **L1091** (verdict 硬编码) | `"★BAT_DET 链 (R_BAT_DET_1/2 + C_DET_BAT) 三颗**全是 DNP** ⇒ **电量检测分压在现网表上不存在**"` |
| **L1548-1550** (用例期望) | `("F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗全 DNP",`<br>` lambda o: o["F4_adc_det"]["active_chain"] == "VBUS_DET_D"`<br>`           and all(not c["populated"] for c in o["F4_adc_det"]["chains"] if c["tag"] == "BAT_DET")),` |

★**改后值 [源码]** (`SW/tools/timing_check.py`):

| 位置 | 改后文本 |
|---|---|
| **L1156** (verdict 数据驱动) | `... leak_err / DEVICE["V_DET_FS"] * 100, _bat_det_verdict(det_chains)),` ★⇒ 不再硬编码结论, 由网表实读驱动★ |
| **L1528** | `BAT_DET_REFS = ("R_BAT_DET_1", "R_BAT_DET_2", "C_DET_BAT")` |
| **L1531-1543** | `_bat_det_all_populated(o)` ★逐颗判【器件本体行】都是「必装」★ |
| **L1546-1557** | `_bat_det_verdict(det_chains)` ★两个分支: 不装机 ⇒ 回老话; 装机 ⇒ 回新话 (「已改成必装 … R_th=…Ω / τ=…ms」)★ |
| **L1650-1652** (用例期望) | `("F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗必装 (V-3=E 落表后)",`<br>` lambda o: o["F4_adc_det"]["active_chain"] == "VBUS_DET_D"`<br>`           and _bat_det_all_populated(o)),` |

★**依据 (落表台账哪一条) [源码]**:

| 落表条目 | 位置 | 内容 |
|---|---|---|
| **§16 · V 值拍板即落 (ISS-236 · 2026-11-17 09:58:16)** | `HW/SCHEMATIC_LANDING_V1_LANDED.md` 段头 L1252-1258 | 老板拍板凭据 ★**`2026-11-17 A1 = E`**★ |
| **★V-3 = E 那一条** ★ | ★**同文件 L1263** ★ | ★`state/gen_netlist.py` (★**E-3 删 DEMO_DNP 三行 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT)**★) ⇒ 落表后期望 `--expect-resolved` 条数变化 **-13 条**★ |
| **§16 · V 值拍板即落 (ISS-283 · 2026-11-17 12:30:23)** | 同文件 L1353-1359 | 老板拍板凭据 ★**`2026-11-17 A4 = A` / `2026-11-17 A5 = 20mA`**★ |
| **★链头落表行** ★ | ★**同文件 L1371** ★ | ★`\| ★**HW/netlist_v1.csv** ★ \| 87f2f792513584bee3d147883c8fb93b \| 37f62ac3f0b81d92ca7d48fdea717f07 \| ★**是**★ \|`★ ⇒ 这就是 §1 判决源取到的**链头 37f62ac3f0b8 (单号 ISS-283)**★ |

★**落表后网表实读 [实测]** (`HW/netlist_v1.csv` · ★**逐行贴, 含行号★**):

```
L182: P2,BAT,RAIL_BAT,R_BAT_DET_1,R_BAT_DET_1,100k ±1%,R,必装,[推算],,"[BAT_DET_RAW] 分压上臂 (100k); ★方案E (ISS-223 §11.4): R_th=37.5kΩ ⇒ ADC 输入漏电 ~1µA 只造成 37.5mV 偏移 (2.1% FS, 可软件标定)★; ★常开静态功耗 26.25µA / 110µW (V-3 裁决的代价)★ [V1.6: 临时线名 BAT 已归一到源节点]",B-08,MAIN_PCB,,
L183: P2,BAT_DET,R_BAT_DET_2,GND,R_BAT_DET_2,60k ±1%,R,必装,[推算],,"[BAT_DET] 分压下臂 地端 (60k ±1%)",B-08,MAIN_PCB,,
L184: P2,BAT_DET,C_DET_BAT,R_BAT_DET_2,C_DET_BAT,100nF ±10%,C,必装,[推算],,"[BAT_DET] ADC 滤波电容 (★V1.2: 电池在镜脚, 本地检测, 不跨铰链)",B-08,MAIN_PCB,,
```

★**逐颗读【器件本体行】, 不读该位号第一条行 (★ISS-190 的老教训: dnp 是行级, 拿错行 = 假绿★) [源码]**:

- ★`R_BAT_DET_1` 的**第一条行是 L181 (type=NET)**, 器件本体行才是 **L182** ⇒ 所以判据走 `_device_dnp_rows()` (L228-235, 过滤 `type ∉ {NET, TP}`), 不走 `Netlist.dnp_of()`★

```
L181: P2,BAT_DET,R_BAT_DET_1,R_BAT_DET_2,NET_BAT_DET,100k+60k 分压 + 100nF,NET,必装,[推算],,"方向 充电板→SoC; ...",B-08,MAIN_PCB,,   ← ★这一行是 NET 行, 不是器件本体行★
```

★**判据强度不许比原来弱 [源码+实测]**:

| 维度 | 改前 | 改后 | 结论 |
|---|---|---|---|
| 事实类型 | **一个负面事实** (三颗**没有**装机) | **全集正面事实 + 三颗都必须在场** (逐颗按器件本体行都是「必装」) | ★**更强** ★ |
| 在场性 | 不要求三颗都在网表里 | `_bat_det_all_populated()` L1537 `if set(dev) != set(BAT_DET_REFS): return False` ⇒ ★缺一颗就红★ | ★**更强** ★ |
| 空集保护 | — | L1540-1541 `if not rows or not all(d == "必装" for d in rows): return False` ⇒ ★空列表不许当「装上了」★ | ★fail-closed★ |

★**改前红 / 改后绿 [实测]** (原样贴):

```
# 改前 (logs/iss288/20_REPRO_BEFORE_timing_check.log L228) — rc=1
  [FAIL] F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗全 DNP

# 改后 (logs/iss288/31_cont2_timing_check.log L229) — rc=0
  [PASS] F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗必装 (V-3=E 落表后)
```

★**★一条历史留痕 (★不改判据, 但必须留痕★) [源码]**: 落表台账 L418 记着 hw-lead (ISS-233) 查到的一条 SW 侧口径错 —— `DEVICE["V_DET_FS"] = 3.3`, 而 BAT_DET 走 `J_SOM_P1 pin38 = SARADC_VIN5` = **1.8V 域** ⇒ SW 算出的「漏电偏移 %满量程」对 BAT_DET 链**偏小 1.83 倍** ★⇒ ★**该条不是 ISS-288 的范围 (本单只收口径, 不动算式) ⇒ 不在本单私自改** ★; ★它已由 ISS-233 登记成 need 给 sw-lead, 本单不改它的状态, 只在这里留痕★★

---

## §4 B3 · 自测新增用例 (REV-11)

★**一句话**: F4' 期望值随落表翻了 ⇒ ★**必须有反向用例锁死「改回 DNP ⇒ 变红」** ★ ⇒ 新增 **REV-11** ⇒ ★自测条数 **71 → 72**★

★**用例原文 [源码]** (`SW/tools/timing_check.py` **L1734-1741**, `REV_TESTS` 列表尾):

```python
    # ★★【ISS-285】F4' 期望值随落表翻了 ⇒ 必须有反向用例锁死「改回 DNP ⇒ 变红」 ★★
    _mk_reverse_dnp(
        "REV-11 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ "
        "F4'『BAT_DET 三颗必装』必须变红",
        targets=[("BAT", "R_BAT_DET_1"), ("BAT_DET", "R_BAT_DET_2"),
                 ("BAT_DET", "C_DET_BAT"), ("GND", "C_DET_BAT")],
        fn=lambda o, mo: (_bat_det_all_populated(o) is True
                          and _bat_det_all_populated(mo) is False)),
```

★**跑法 [源码]** (`_mk_reverse_dnp` L1438-1459): 按 `(net 列, ref 列)` 匹配出**要改的行号** ⇒ 拷一份网表 ⇒ 只把那些行的 `dnp` 列改成 **DNP** ⇒ 重算一遍 ⇒ 断言「**原图绿 + 变异图红**」 ⇒ ★**这是行级变异, 不许拿错行**★

★**targets 覆盖 [源码+实测]**: `("BAT", "R_BAT_DET_1")` → **L182** (R_BAT_DET_1 器件本体行) · `("BAT_DET", "R_BAT_DET_2")` → **L183** · `("BAT_DET", "C_DET_BAT")` → **L184** · `("GND", "C_DET_BAT")` → **L185** (C_DET_BAT 的 GND 端行) ⇒ ★**三颗器件本体行 + C_DET_BAT 的第二行都盖到了**★

★**它抓的是哪个回归 (★两个方向都抓★) [推算 + 实测]**:

| # | 回归 | REV-11 怎么抓 |
|---|---|---|
| **①** | ★**期望值被改回去 / 落表口径漂移** ★ —— 若有人把 F4' 期望改回「三颗全 DNP」 (即没随 V-3=E 落表更新), 或网表再翻回 DNP 而期望没跟 | `fn` 的 `o` 分支 `_bat_det_all_populated(o) is True` ⇒ **原图不绿 ⇒ REV-11 直接红** ⇒ ★**期望与现状对不上时不可能全绿**★ |
| **②** | ★**判据被写松** ★ —— 若有人把 F4' 判据改成只看该位号**第一条行** / 用 `any` 而非 `all` / 不要求三颗都在场 | `fn` 的 `mo` 分支 `_bat_det_all_populated(mo) is False` ⇒ ★把 BAT_DET 改回 DNP 后判据**仍绿** ⇒ REV-11 红★ ⇒ ★**ISS-190 的「拿错行 = 假绿」被锁死**★ |

★**实跑证据 [实测]** (沙盒用例⑥ · `logs/iss288/32_cont2_verify_iss288_land.log` · 原样贴):

```
【⑥】把 BAT_DET 三颗改回 DNP (+ 合法补记把链头前移) ⇒ ★只该红 F4' + REV-11★
  构造: BAT_DET 三颗的器件本体行 L[182, 183, 184, 185] 改回 DNP ⇒ 盘上 md5 = 993877bcf49a9afaaf57d795f78a47e5 ; 台账补一行【合法落表记录】(改前 = 真链头 37f62ac3f0b8) ⇒ 链头前移 ⇒ 锚点两条判据保持绿
  ---- timing_check.py (沙盒) ---- rc=1
    [FAIL] F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗必装 (V-3=E 落表后)
    [FAIL] REV-11 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ F4'『BAT_DET 三颗必装』必须变红
  SELFTEST 70/72 通过, rc=1
  ---- check_demo_panel_spec.py (沙盒) ---- rc=0
  ★期望红组 (2 条): ["F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗必装 (V-3=E 落表后)", "REV-11 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ F4'『BAT_DET 三颗必装』必须变红"]
  ★实际红组 (2 条): ["F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗必装 (V-3=E 落表后)", "REV-11 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ F4'『BAT_DET 三颗必装』必须变红"]
  ★判定: ✅ 一致
```

★**★同时验证了「不是恒红闸」★ [实测]** (同日志用例⑦ 正向对照):

```
【⑦】正向对照: 一切如常 (证明闸不是恒红)
  ---- timing_check.py (沙盒) ---- rc=0
  SELFTEST 72/72 通过, rc=0
  ---- check_demo_panel_spec.py (沙盒) ---- rc=0
  ★期望红组 (0 条): (空 ⇒ 期望全绿)
  ★实际红组 (0 条): (空 ⇒ 实际全绿)
  ★判定: ✅ 一致
```

★**自测条数口径 [实测]**: 改前 **71** 条 (68 过 / 3 红) ⇒ 改后 **72** 条 (72 过 / 0 红) ⇒ **+1 条 = REV-11** ⇒ ★**且改前那 3 条红里就包含 F4' 与两条锚点判据 ⇒ 改后 3 → 0 + 新增 1 条绿 ⇒ 71+1=72 全对得上**★

---

## §5 B4 · 回归 (★前后 rc 对照 + 受保护件 md5★)

★**① 前后 rc 对照表 [实测]** (★改前那行是本趟**自己重跑**出来的, 不是抄上趟日志★ · 沙盒 = copies ⇒ 真盘一个字节不动★):

| | 改前 (BEFORE 快照) | 改后 (真盘) |
|---|---|---|
| 文件 | `logs/iss288/timing_check.py.BEFORE` | `SW/tools/timing_check.py` |
| **md5** | `4cba20b1d0249b671632878c964b4bd7` | ★**`68c4becffe6bcd708e388dba9d18a505`** ★ (= ISS-285 交卷单写死的「套用后期望 md5」, ★**逐字一致**★) |
| **自测** | ★**`SELFTEST 68/71 通过, rc=1`** ★ | ★**`SELFTEST 72/72 通过, rc=0`** ★ |
| 红条数 | ★**3 条** ★ | ★**0 条** ★ |
| 跑的方式 | 沙盒 (改前快照代进去) | 真盘 |

★**改前 3 条红的原样输出 [实测]** (本趟重跑日志 `logs/iss288/37_cont2_REPRO_BEFORE_rerun.log`):

```
[沙盒] 改前 timing_check.py md5 = 4cba20b1d0249b671632878c964b4bd7
[沙盒] 改前 check_demo_panel_spec.py md5 = 4e8f9aeaf45f95e120421d29bdaa333c
---- 沙盒改前 SELFTEST 末行 ----
SELFTEST 68/71 通过, rc=1
---- 沙盒改前 FAIL 组 ----
[FAIL] 网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)
[FAIL] 网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)
[FAIL] F4' 实读: ADC 装机链是 VBUS_DET_D; BAT_DET 三颗全 DNP
[沙盒] rc=1 ⇒ 日志 .../logs/iss288/20_REPRO_BEFORE_timing_check.log
```

★**改后末行的原样输出 [实测]** (本机真盘 · `logs/iss288/31_cont2_timing_check.log`):

```
SELFTEST 72/72 通过, rc=0
RC=0
```

★**② 受保护 5 件 md5 前后对照 [实测]** (跑前跑后逐字节相同; 前后快照 = `logs/iss288/30_cont2_protected_BEFORE.txt` / `logs/iss288/36_cont2_protected_AFTER.txt` · ★两份 `diff` 只差标题行一处★):

| 件 | 文件 | md5 (BEFORE) | md5 (AFTER) | ★逐字节相同?★ | mtime (前后均未变) |
|---|---|---|---|---|---|
| 板 | `HW/PCB/demo_mainboard.kicad_pcb` | `611b869e13518c3c023fb178f91a0075` | `611b869e13518c3c023fb178f91a0075` | ★**✔**★ | ★**2026-11-06 07:07:17.362193413 +0800**★ (★双重自证: md5 + mtime 都指向 11-06★) |
| `.kicad_pro` | `HW/PCB/demo_mainboard.kicad_pro` | `3e504d2be83152e337949723e909be1b` | `3e504d2be83152e337949723e909be1b` | ★**✔**★ | `2026-11-04 23:47:30.279742515 +0800` |
| 网表 | `HW/netlist_v1.csv` | `37f62ac3f0b81d92ca7d48fdea717f07` | `37f62ac3f0b81d92ca7d48fdea717f07` | ★**✔**★ | `2026-11-17 12:30:22.352463497 +0800` |
| 脚表 | `HW/netlist_v1_pins.csv` | `a4270120454aedf7a23c92cd8985c8a6` | `a4270120454aedf7a23c92cd8985c8a6` | ★**✔**★ | `2026-11-17 12:30:22.488465119 +0800` |
| BOM | `HW/BOM_v1.csv` | `5d02bece9477ffce5fbe0193c7d5cce4` | `5d02bece9477ffce5fbe0193c7d5cce4` | ★**✔**★ | `2026-11-17 12:30:22.647467015 +0800` |

★**同一批快照里另外 3 件 (★本单也不许动, 同样前后不变★)**:

| 文件 | md5 (BEFORE = AFTER) |
|---|---|
| `SW/tools/timing_check.py` | ★**`68c4becffe6bcd708e388dba9d18a505`** ★ (★mtime `2026-11-17 14:36:16` = cont1 落补丁时刻 ⇒ ★**cont2 (本单) 一个字节都没碰**★) |
| `SW/tools/check_demo_panel_spec.py` | `4e8f9aeaf45f95e120421d29bdaa333c` (★与 `logs/iss288/check_demo_panel_spec.py.BEFORE` 逐字节相同 ⇒ ISS-284/275 的成果未被本单碰过★) |
| `SW/SW_MD5_BASELINE_LEDGER.md` | `c5484ec677ebd52ad4ff87ab520ec77b` (★SW 台账 §1 锚点块一字未动 ★) |

★**③ 8 条验收命令 · 本机实跑 rc [实测]** (全部本趟重跑, 原样贴):

```
$ python3 SW/tools/timing_check.py                                  → SELFTEST 72/72 通过, rc=0   RC=0
$ python3 SW/patches/ISS-288_timing_check_land/verify_iss288_land.py → ★7 条用例总判定: ✅ 全符合   RC=0
$ python3 SW/tools/check_demo_panel_spec.py                          → RC=0
$ python3 SW/tools/check_demo_panel_spec.py --selftest               → --- SELFTEST 22/22 通过 ---   RC=0
$ python3 HW/check_step1_parts_spec.py                              → ---- 8/8 通过 ⇒ rc=0 ----   RC=0
$ python3 state/merge.py                                            → ✅ STATE.yaml 已刷新 (2026-11-17T15:12:31+08:00)   RC=0
$ python3 state/gate_check.py                                       → 【Q1 交付齐备率】18/18 个必填验收块齐全   RC=0
$ python3 state/issue_check.py                                      → ✅ 问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖)   RC=0
```

★**日志落盘位置**: `logs/iss288/31_cont2_timing_check.log` · `32_cont2_verify_iss288_land.log` · `33_cont2_dps.log` · `34_cont2_gates.log` · `30_cont2_protected_BEFORE.txt` · `36_cont2_protected_AFTER.txt` · `37_cont2_REPRO_BEFORE_rerun.log` · `39_cont2_merge_gate_final.log`★

---

## §6 B5 · 边界自检 + B6 留痕 / 分片 / need

### §6.1 B5 · 边界自检 (★逐条自证★)

| # | 边界 | 自证 (本机实跑) | 判定 |
|---|---|---|---|
| ① | ★**零写板** ★ | 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` (BEFORE=AFTER) ★**且** mtime 仍 `2026-11-06 07:07:17.362193413 +0800` (★md5 + mtime **双重自证**★) | ✔ |
| ② | ★**零落表** ★ | 网表 `37f62ac3f0b81d92ca7d48fdea717f07` / 脚表 `a4270120454aedf7a23c92cd8985c8a6` / BOM `5d02bece9477ffce5fbe0193c7d5cce4` 三个 md5 BEFORE=AFTER; mtime 全仍 `2026-11-17 12:30:22` (★= ISS-283 落表时刻 ⇒ 本单没碰过这三个文件★) | ✔ |
| ③ | ★**零改 `SW/tools/timing_check.py`** ★ | md5 `68c4becffe6bcd708e388dba9d18a505` + mtime `2026-11-17 14:36:16.101396715 +0800` ⇒ ★**cont2 (本单) 一个字节没碰** (补丁本体是 cont1 落的) ★ | ✔ |
| ④ | ★**零改既有 SW 判据脚本** ★ | `SW/tools/check_demo_panel_spec.py` md5 `4e8f9aeaf45f95e120421d29bdaa333c` 与 `logs/iss288/check_demo_panel_spec.py.BEFORE` ★**逐字节相同** (`diff -q` ⇒ IDENTICAL) ★; `SW/SW_MD5_BASELINE_LEDGER.md` md5 `c5484ec677ebd52ad4ff87ab520ec77b` 未动 | ✔ |
| ⑤ | ★**零外发** ★ | 本单★**没有**发邮件 / 询价 / 问询 / 采购; ★**没有**联系供应商; ★**没有**下采购单★ ⇒ 详见 §8 | ✔ |
| ⑥ | ★**不自签 issue_log** ★ | `state/issue_log.yaml` 的 ISS-288 仍是 `status: fixing` / `fix_ref: null` / `verify_by: main` ⇒ ★**本单只读, 没签** ★ | ✔ |
| ⑦ | ★**只写自己的分片** ★ | 只写 `state/fragments/sw.yaml` (sw-lead); `hw.yaml` `ec04a542590c8d874ebf11c87954fa71` / `mech.yaml` `b6fd10b74c4b6298092cad87a064d6a4` / `pm.yaml` `502521af931876abf5f5e1b8dbe4c739` 三个 md5 ★**写前 = 写后** ★ ⇒ 没碰别人的地界 | ✔ |
| ⑧ | ★**实物 [实测] = 0 条** ★ | 本机★**无板端实测** (无量具 / 无样机 / 无板子) ★⇒ 本单所有 [实测] 全是**本机脚本实跑**, 板端一条没有 ⇒ ★**本单全文不做任何板端性能主张** ★ | ✔ |
| ⑨ | ★**并发提示** ★ | hw-lead 的 ISS-289 与 mech-lead 的 ISS-290 此刻在飞 ⇒ `HW/` 与 `MECH/` ★**只读** ★; 本单只写 `HANDOFF/` + sw-lead 自己的分片 | ✔ |
| ⑩ | ★**零改 hw.yaml / mech.yaml / pm.yaml / issue_log** ★ | 见 ⑥⑦ | ✔ |

### §6.2 B6 · 留痕 (★交付物清单★)

| # | 交付物 | 落盘路径 | 状态 |
|---|---|---|---|
| 1 | ★**交卷单 (本文件)** ★ | `HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md` | ★**本单 (cont2) 把 §1~§8 全部填满, 0 处空白占位** ★ (★交卷前空白占位符扫描结果 = 0, 见 §6.4★) |
| 2 | 补丁本体 | `SW/tools/timing_check.py` | ★**cont1 落的 (mtime 14:36:16) · cont2 只读** ★ |
| 3 | 验证脚本 | `SW/patches/ISS-288_timing_check_land/verify_iss288_land.py` | cont1 落的 (★19 868 B · 14:55 mtime★) · cont2 实跑 rc=0 |
| 4 | 分片 | `state/fragments/sw.yaml` | ★**cont1 6 处 + cont2 补 2 处** ★ (详见 §6.3) |
| 5 | 改前快照 | `logs/iss288/timing_check.py.BEFORE` (101 521 B) | cont1 留的 · ★**改前证据直接引用, 不编** ★ |
| 6 | 本单日志 8 份 | `logs/iss288/30_cont2_protected_BEFORE.txt` · `31_cont2_timing_check.log` · `32_cont2_verify_iss288_land.log` · `33_cont2_dps.log` · `34_cont2_gates.log` · `36_cont2_protected_AFTER.txt` · `37_cont2_REPRO_BEFORE_rerun.log` · `39_cont2_merge_gate_final.log` | cont2 实跑产物 |

### §6.3 分片 (★只做「核对 + 补漏」★)
★**写前核对 [实测]** — `grep -n "iss288" state/fragments/sw.yaml` ⇒ ★**6 行**命中 (★**6 个条目, 全是 cont1 留的**★):

```
1292:- path: SW/patches/ISS-288_timing_check_land/verify_iss288_land.py
2518:- key: iss288_sw_timing_check_patch_landed
4265:- key: iss288_timing_check_patch_landed_chainhead_source
4271:    (logs/iss288/21_sbx_verify_iss288_cont1.log) ; 零写板 (板 611b869e… mtime 2026-11-06 07:07:17 不变) 零落表
4274:- key: iss288_selftest_72_72_green_and_prefix_bugfix
4279:  note: '[实测] 改前基线本趟自跑复现 (沙盒 logs/iss288/20_REPRO_BEFORE_timing_check.log, rc=1 / 68/71 / 3 条红) ; 改后真盘
```

★**逐条核对结论**: 已有 = **interface_claim ×2** (链头判决源 / 自测 72-72 + 前缀 bugfix) + **need ×1** (交付告知) + **artifact ×1** (验证脚本) ⇒ ★**cont1 的活一件不缺, 本单不重写★**

★**缺的 2 条 (cont2 补) [实测]** — ★**走 `python3 state/frag_write.py --agent sw-lead` 原子写 (★禁止 `open(p,"w")`★), 输出 `✅ sw.yaml 已原子更新 → 再跑 python3 state/merge.py`★:

| 类型 | key | 补什么 |
|---|---|---|
| **interface_claim** | `iss288_handoff_b1_b8_filled_cont2` | ★**交卷单 §1~§8 已填满 (0 处空白占位)** + 补丁 md5 + 前后 rc 对照 + 8 条验收命令 rc + 受保护 5 件前后对照 + 边界自检 ★ |
| **need** (to main) | `iss288_main_verify_sign_issue_log` | ★**请 main 验签 issue_log ISS-288 (status fixing → verified, fix_ref 填本交卷单路径) + 把 `iss285_sw_apply_after_iss283_verified` 标 closed** ★ (★verify_by = main, sw-lead 不自签★) |

★**写后校验 [实测]** — `grep -n "iss288" state/fragments/sw.yaml` ⇒ ★**10 行**文本命中 (★= cont1 留的 **6 行** + 本单新增 **2 个条目**各自的 key 行与正文行, 合计新增 4 行★; ⇒ ★**条目口径: 6 → 8 条**★) (原样贴):

```
1292:- path: SW/patches/ISS-288_timing_check_land/verify_iss288_land.py
2518:- key: iss288_sw_timing_check_patch_landed
2528:- key: iss288_main_verify_sign_issue_log
4277:- key: iss288_timing_check_patch_landed_chainhead_source
4283:    (logs/iss288/21_sbx_verify_iss288_cont1.log) ; 零写板 (板 611b869e… mtime 2026-11-06 07:07:17 不变) 零落表
4286:- key: iss288_selftest_72_72_green_and_prefix_bugfix
4291:  note: '[实测] 改前基线本趟自跑复现 (沙盒 logs/iss288/20_REPRO_BEFORE_timing_check.log, rc=1 / 68/71 / 3 条红) ; 改后真盘
4294:- key: iss288_handoff_b1_b8_filled_cont2
4296:    逐字一致) · 回归由 rc=1 · 68/71 (3 条红) 转 rc=0 · 72/72 (0 条红) · 8 条验收命令全 rc=0 (timing_check / verify_iss288_land
4302:  note: '[实测] 本机实跑 2026-11-17 15:0x~15:2x, 每条命令原样 rc 贴进交卷单 §5; 改前基线本趟自己重跑 (沙盒 logs/iss288/repro_before_sbx.py
```

★**YAML 完整性校验 [实测]** (写完必须能解析, 不许写坏分片):

```
$ python3 -c "import yaml; d=yaml.safe_load(open('state/fragments/sw.yaml',encoding='utf-8')); print('OK keys=',list(d.keys()))"
OK keys= ['agent', 'role', 'updated_at', 'updated_by', 'status', 'artifacts', 'blockers', 'needs_from', 'answers', 'interface_claims', 'open_questions', 'risks']
interface_claims= 246 needs_from= 104 artifacts= 182
```

★**need 汇总 (给 main)**:

| key | 状态 | 内容 |
|---|---|---|
| `iss288_main_verify_sign_issue_log` | ★**本单新增** ★ | 请 main 验签 issue_log ISS-288 (fixing→verified) + 把 `iss285_sw_apply_after_iss283_verified` 标 closed |
| `iss285_sw_apply_after_iss283_verified` | ★**cont1 留的 · 仍 open** ★ | ★**已由本单履行完毕** (真盘 md5 68c4becf… + rc=0 · 72/72) ⇒ 请 main 标 closed ★ |
| `iss288_sw_timing_check_patch_landed` | cont1 留的 | 交付告知 (含全部 md5 / rc / 受保护件读数) |

### §6.4 交卷前最后一遍自检 (★本机实跑·原样贴★)

★**① 空白占位符扫描 (★必须是 0★)** —— ★★把两个字符分开写, 免得这份交卷单自己命中自己的扫描★★:

```
$ grep -c "待""写" "HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md"
0
```

★**② 交卷前最后一轮闸 (★分片写完后重跑★ · 日志 `logs/iss288/39_cont2_merge_gate_final.log`)**:

```
$ python3 state/merge.py
✅ STATE.yaml 已刷新 (2026-11-17T15:24:41+08:00)
   产出 506 | 阻塞 43 (高危 33) | 未闭合需求 294 | 冲突 0 | 健康度 red
RC=0

$ python3 state/gate_check.py
【Q1 交付齐备率】 18/18 个必填验收块齐全
RC=0

$ python3 state/issue_check.py
✅ 问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖)
RC=0
```

★**③ 受保护 5 件最后一遍 md5 (与 §5 的 BEFORE 快照逐字对比)**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413 +0800`) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ ★**5 件全同 = 零写板 + 零落表** ★

---

## §7 证据分级 (★每条结论标 [实测] / [源码] / [推算] / [0数据]★)

★**分级口径**: ★**实测** = 本机跑出来的 (原样输出贴在正文里)★ · ★**源码** = 盘上文件的字面内容 (行号可查)★ · ★**推算** = 由前两者推演出来的 (★推算就是推算, 不许冒充实测★)★ · ★**0数据** = 本机没有这个数据 (★不许编, 不许拿推算冒充★)★

| # | 结论 | ★证据等级★ | 出处 |
|---|---|---|---|
| 1 | 补丁本体 md5 = `68c4becffe6bcd708e388dba9d18a505` (= ISS-285 交卷单写死的期望值, **逐字一致**) | ★**[实测]**★ | 本机 `md5sum SW/tools/timing_check.py` |
| 2 | 改后 `python3 SW/tools/timing_check.py` ⇒ `SELFTEST 72/72 通过, rc=0` | ★**[实测]**★ | `logs/iss288/31_cont2_timing_check.log` |
| 3 | 改前基线 ⇒ `SELFTEST 68/71 通过, rc=1` + **3 条红** (两条网表锚点 + 一条 F4') | ★**[实测]**★ | 本趟自跑 `logs/iss288/37_cont2_REPRO_BEFORE_rerun.log` ⇒ `20_REPRO_BEFORE_timing_check.log` |
| 4 | 8 条验收命令全 `rc=0` (含 `gate_check` **Q1 18/18** / `issue_check` 全过) | ★**[实测]**★ | `logs/iss288/31~34_cont2_*.log` |
| 5 | 判决源 = 落表台账链头 `37f62ac3f0b8` (单号 ISS-283), 盘上 md5 = `37f62ac3f0b81d92ca7d48fdea717f07` | ★**[实测]**★ | 本机直调 `_netlist_baseline_state()` 的 DETAIL |
| 6 | 改前判决文本 = 「盘上真源 md5 … ≠ 锚点登记 e06c1dd633566aa44732762c2ff99d1c」 | ★**[实测]**★ | 本机直调 BEFORE 快照 |
| 7 | 允许集合 = **10 个 12 位前缀** (非 32 位) | ★**[实测]**★ | 本机直调 + `logs/iss288/10_prefix_bug_demo.log` |
| 8 | 旧口径 `md5 in allowed` ⇒ **False** (32 位 ∉ 12 位前缀集合 ⇒ 恒红 = 判据自毁) | ★**[实测]**★ | `logs/iss288/10_prefix_bug_demo.log` |
| 9 | 伪 md5 `deadbeefdead…` ⇒ `netlist_md5_allowed` = False (★判据方向没被放松★) | ★**[实测]**★ | 本机直调 |
| 10 | fail-closed 三条 (链头不唯一 / 链断 / 链头无单号) 一条没放宽 (★期望红组 = 实际红组★) | ★**[实测]**★ | 沙盒用例③④⑤ (`logs/iss288/32_cont2_verify_iss288_land.log`) |
| 11 | 链头实现 = ★**直接 import**★ `check_demo_panel_spec.py` 的 R6 (同域 SW/tools, 不 import MECH) | ★**[源码]**★ | `SW/tools/timing_check.py` L209-222 |
| 12 | `check_demo_panel_spec.py` 一个字节没被本单碰过 (★md5 与改前快照逐字节相同★) | ★**[实测]**★ | `diff -q` ⇒ IDENTICAL + md5 |
| 13 | 改动 = **9 hunk**, 纯 hunk 体 **+156/-46** (含 `+++`/`---` 头行则 +157/-47) | ★**[实测]**★ | `diff -u` 的 hunk 头 + 逐行计数 |
| 14 | F4' 期望随落表翻 = 「BAT_DET 三颗全 DNP」⇒「BAT_DET 三颗必装 (V-3=E 落表后)」 | ★**[源码]**★ | BEFORE L1548-1550 ⇒ AFTER L1650-1652 |
| 15 | 落表依据 = ★**落表台账 §16 · ISS-236 · V-3 = E**★ ⇒ `state/gen_netlist.py` **E-3 删 DEMO_DNP 三行 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT)** | ★**[源码]**★ | `HW/SCHEMATIC_LANDING_V1_LANDED.md` L1252-1258 (段头) + **L1263 (V-3=E 那行)** |
| 16 | 老板拍板凭据 = **`2026-11-17 A1 = E`** (台账原文登记) | ★**[源码]**★ | 同上 L1256 |
| 17 | 现在台账链头 = ISS-283 落的 `87f2f7925135…` ⇒ `37f62ac3f0b81d92ca7d48fdea717f07` | ★**[源码]**★ | 同上 **L1371** |
| 18 | 落表后网表实读 L182 / L183 / L184 三颗器件本体行 dnp = `必装` | ★**[实测]**★ | `HW/netlist_v1.csv` |
| 19 | `R_BAT_DET_1` 的**第一条行是 L181 (type=NET)**, 器件本体行才是 L182 ⇒ 必须走 `_device_dnp_rows()` | ★**[实测]**★ | `HW/netlist_v1.csv` + 源码 L228-235 |
| 20 | F4' 改前 **FAIL** ⇒ 改后 **PASS** (★同一台账同一条判据★) | ★**[实测]**★ | `20_REPRO_BEFORE…log` L228 ⇒ `31_cont2_timing_check.log` L229 |
| 21 | REV-11 抓两类回归 (★期望被改回去 / 判据被写松★) | ★**[推算]**★ | 读 `fn` 两个分支的语义推演; ★**并由沙盒用例⑥ 实跑佐证** (改回 DNP ⇒ 只红 F4' + REV-11, ★不误伤两条锚点判据★) ★ |
| 22 | 判据强度「**更强**」 (负面事实 ⇒ 全集正面事实 + 三颗都必须在场 + 缺一颗就红) | ★**[推算]**★ | 改前/改后断言语义对比 (源码 L1537 / L1540-1541) |
| 23 | REV-11 的 `targets` 盖到 L182 / L183 / L184 / L185 四行 | ★**[实测]**★ | `HW/netlist_v1.csv` + 源码 L1738-1739 |
| 24 | 自测 71 → 72 (+1 = REV-11), 3 红 → 0 红 | ★**[实测]**★ | 改前 68/71 · 改后 72/72 |
| 25 | 受保护 5 件 md5 跑前跑后**逐字节相同** (板 mtime 仍 `2026-11-06 07:07:17`) | ★**[实测]**★ | `logs/iss288/30_cont2_protected_BEFORE.txt` vs `36_cont2_protected_AFTER.txt` (★`diff` 只差标题行★) |
| 26 | ★**板端实测 / 实物验证** ★ | ★**[0数据]**★ | ★**本机无样机 / 无量具 / 无板子 ⇒ 一条都没有, 不许编** ★ |
| 27 | ★**NPU 纯硬件耗时 / 端到端 <60ms 是否达标** ★ | ★**[0数据]**★ | ★**本单不涉性能, 也不许抢这个结论**; 真实读数 = `SW-B1` 阻塞 (ARS45 从没公开跑过 YOLO) ⇒ **硬件纯耗时仍未知** ★ |
| 28 | ★**板是否已能出货 / 能否点亮 / BAT_DET 分压是否达到精度目标** ★ | ★**[0数据]**★ | ★**本单只改判据口径, 不出任何实物结论** ★ |
| 29 | 分片写入走原子写 (tmp + fsync + `os.replace`), 没把分片写坏 | ★**[实测]**★ | `frag_write.py` 输出 `✅ sw.yaml 已原子更新` + 写后 YAML `safe_load` 成功 |
| 30 | 别人的分片没被碰 | ★**[实测]**★ | `hw.yaml` / `mech.yaml` / `pm.yaml` md5 写前=写后 |

★**★一句话总结**: 本单 ★**没有一条结论是拿推算冒充实测的** ★; 凡本机跑不出来的 (板端 / 性能 / 出货), ★**一律标 [0数据] 并明写「不许编」** ★。

---

## §8 零外发声明 + 不替老板拍板 + 不自签 issue_log

### §8.1 零外发声明

★**本单零外发**: ★**没有**发邮件 / 询价 / 问询 / 采购 / 催货; ★**没有**联系任何供应商; ★**没有**下任何采购单; ★**没有**把本项目任何内容发到机器外★

⇒ 本单全部结论**只来自本机实跑** (日志路径见 §5) ⇒ ★**没有「批一句可以发」这个选项, 也没向任何人请示过能不能发** ★(老板 2026-11-11 19:31 + 2026-11-12 02:00 定的纪律: 不再发信, 全靠自己查资料)★

★**本单的外部事实只有一个, 而且是盘上既成事实, 不是本单去查的**: V-3 = E 的落表记录 (台账 §16, 含老板拍板凭据 `2026-11-17 A1 = E`) ★⇒ **没上网查, 也没问任何人** ★

### §8.2 不替老板拍板

★**本单零拍板**: 本单★**没有**新增 / 修改 / 解释任何 V 值、阈值、目标值 ★(★V-3 = E 早已由老板拍完并落表, 本单只是把 SW 侧判据口径**对齐到已落表的既成事实**★)★

⇒ ★**没碰**: 任何 ISP 生死线 / 任何采样帧数门限 / 任何分压比 / 任何功耗预算 / 任何帧率目标 ⇒ ★**本单一件硬件决策都不做** ★

⇒ ★**留给老板 / main 的**: ★**issue_log ISS-288 的验签** (★verify_by = main★) 与 ★**V-7 充电板整机阶段的 BAT_DET 兜底口径** (若 SoM 手册 / SoC TRM 拿不到 I_leak / C_in / t_acq, 台账 §11 的降级方案③ 仍待拍) ★—— ★**这两件本单都【不代拍】, 只在 §6.3 登记成 need 给 main** ★

⇒ ★**一条已知的历史留痕 (本单也不动它)**: 落表台账 L418 记着 `DEVICE["V_DET_FS"] = 3.3` 与 BAT_DET 实走 1.8V 域的不一致 (由 ISS-233 登记成 need 给 sw-lead) ⇒ ★**那是另一个口径单的事, 本单只留痕不擅改** ★(★若擅自改 `V_DET_FS`, 就会连带改变本单之外的算式与门禁, 超出本单授权★)

### §8.3 不自签 issue_log

★**本单没有签任何 issue_log**: `state/issue_log.yaml` 的 ISS-288 仍是 ★`status: fixing` / `fix_ref: null` / `verify_by: main`★ ⇒ ★**本单只读, 没写一个字节** ★

⇒ ★**验签与改状态是 main 的活** (已在 §6.3 登记成 need `iss288_main_verify_sign_issue_log`) ⇒ ★**sw-lead 不自签、不代签、不预签** ★

### §8.4 本单到底干了什么 (★一句话 + 边界★)

★**本单 (cont2) 只干一件事: 把已经跑出来的东西写成交卷单** —— ★**补丁本体是 cont1 落的** (md5 `68c4becffe6bcd708e388dba9d18a505` · mtime `2026-11-17 14:36:16` ⇒ 本单一个字节没碰)★; 本单把 §1~§8 里的 **8 处空白占位**全部填成**本机实跑输出**, 并补了 2 条分片 (interface_claim + need)★

★**边界守住**: ★**零写板 · 零落表 · 零改 `SW/tools/timing_check.py` · 零改既有 SW 判据脚本 · 零外发 · 不自签 issue_log · 只写自己的分片** ★⇒ 受保护 5 件 md5 跑前跑后逐字节相同 (板 mtime 仍 2026-11-06 07:07:17) ⇒ ★**实物 [实测] = 0 条** ★

---

★**交卷人**: 软件总工 (sw-lead) · ★**交卷时刻**: ★**2026-11-17 15:2x (Asia/Shanghai)** ★ · ★**verify_by**: ★**main (未签)** ★ · ★**本单零外发** ★
