# ★「板只改一次」那一趟 · SW 侧准出汇总闸 · 清单页★

> ★**单号**: ISS-335 · ★**owner**: sw-lead · ★**闸本体**: `SW/tools/check_onepass_sw_release.py` ★
> ★**对标物 (MECH 侧)**: `MECH/check_onepass_mech_release.py` (ISS-300 已交卷) ★
> ★**本单性质**: 纯新建闸类 · ★**零写板 · 零落表 · 零改既有 16 道 SW 闸 · 零改 `state/gate_check.py`** ★
> ★**零外发** ★ (老板 2026-11-11 19:31 + 2026-11-12 02:02 不再发信) ★

---

## 0 一句话

★**「板只改一次」那一趟当天, SW 侧必跑 10 道闸 ⇒ 一条命令 `python3 SW/tools/check_onepass_sw_release.py` 给出
「SW 侧能不能出 Gerber」的结论; 任一道红 ⇒ 汇总红并点名是哪一道; 闸脚本不存在 / 跑不起来 / 超时 ⇒ 一律算闸红
(★绝不「没跑就当过」★) ★**

---

## 1 闸清单 (★10 道 · 顺序 = 收工验收的执行顺序 · 一条不许少★)

| # | 闸 (相对项目根) | 怎么调 (★裸跑 / 带参★) | 期望 rc | 在日常链上? | 备注 |
|---:|---|---|---:|---|---|
| 1 | `SW/tools/check_onepass_sw_sync.py` | ★**裸跑** ★ `args=()` | 0 | ✅ 是 (EXTRA_GATES + 钉板闸⑨) | SW 侧板侧输入 / 合法改板闸 (ISS-279/298/321) |
| 2 | `SW/tools/check_sw_ref_reachability.py` | ★**裸跑** ★ `args=()` | 0 | ✅ 是 (EXTRA_GATES) | 位号引用可达性闸 **v1** (ISS-318) |
| 3 | `SW/tools/check_landing_trace_obligation.py` | ★**裸跑** ★ `args=()` | 0 | ✅ 是 (EXTRA_GATES) | 落表留痕义务闸 (ISS-315) |
| 4 | `SW/tools/check_demo_panel_spec.py` | ★**裸跑** ★ `args=()` | 0 | ❌ ★**链外** ★ | 面板规格 / 三方对账闸 (ISS-275/315) |
| 5 | `SW/tools/check_demo_panel_spec_r6_selftest.py` | ★**裸跑 + `--tmpdir`** ★ `args=("--tmpdir", <项目内目录>)` | 0 | ✅ 是 (EXTRA_GATES) | ★**不许传 `--selftest`** ★ (ISS-309) |
| 6 | `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` | ★**裸跑 + `--tmpdir`** ★ | 0 | ✅ 是 (EXTRA_GATES) | ★**不许传 `--selftest`** ★ (ISS-312) |
| 7 | `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | ★**裸跑 + `--tmpdir`** ★ | 0 | ✅ 是 (EXTRA_GATES) | ★**不许传 `--selftest`** ★ (ISS-315) |
| 8 | `SW/tools/check_shutdown_semantics.py` | ★**裸跑** ★ `args=()` | 0 | ❌ ★**链外** ★ | 关机语义闸 (ISS-234 系) |
| 9 | `SW/tools/check_timing_review_adc_sync.py` | ★**裸跑** ★ `args=()` | 0 | ❌ ★**链外** ★ | 时序评审 ADC 同步闸 |
| 10 | `SW/tools/timing_check.py` | ★**裸跑** ★ `args=()` | 0 | ❌ ★**链外** ★ | 上电 / 复位时序预算闸 |

★**清单完备性基准 (`MANIFEST_BASE`) = 上表这 10 条路径** ⇒ ★**清单里少一道 ⇒ 汇总闸直接红★ ★
★**(★对标 MECH 侧 `MANIFEST_REQUIRED` 的做法: 清单与基准分开定义 ⇒ 「漏一道」这件事本身才能被检出★)** ★

★**影子道 (★默认只跑、只打印读数、【不参与判决】★)★**: `SW/tools/check_sw_ref_reachability_v2.py` (ISS-332)
⇒ ★**理由 + 默认值建议 + 不选的后果 = 交卷页 §B5-①** ★

---

## 2 ★为什么是这 10 道 (★来源 = ISS-321 实测表·不是设计稿的自嗨★)★

★**来源**: `HANDOFF/2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md` §B1-3 的 ★**逐闸读数表**★
(★S0 基线 / S1 改名+SW 文档没改 / S2 改名+SW 文档同步改了 / S4 全做对 / S8 零改名对照组★)
⇒ ★**那 10 道就是 ISS-321 实测过的「板那一趟当天必跑」的闸** ★

| # | 闸 | ★**为什么它属于「板那一趟当天必跑」** ★ | ★**当天它红意味着什么** ★ |
|---:|---|---|---|
| 1 | `check_onepass_sw_sync.py` | 板面动作一旦落地, 它是 SW 侧第一个看到盘面变化的闸 (ISS-279/298) | 板改了但 SW 侧输入没同步 |
| 2 | `check_sw_ref_reachability.py` | S1 改名 + SW 文档没同步 ⇒ 它当场红 (★rename-safe★) | ★**位号漂移** ★ |
| 3 | `check_landing_trace_obligation.py` | 板改了但单号 / md5 没留痕 ⇒ 它当场红 | 落表留痕缺失 |
| 4 | `check_demo_panel_spec.py` | 只判 md5 链 ⇒ 合法落表全就绿 / 悄悄换真源就红 | 真源与台账对不上 |
| 5 | `check_demo_panel_spec_r6_selftest.py` | 判决源本身的反向用例 (S4 与 S8 都红 ⇒ 不是改名特有) | 判决源本身有问题 |
| 6 | `check_demo_panel_spec_r6_chainjudge_selftest.py` | 链头落表单号交叉核对 (★S4 红 / S8 绿 ⇒ 改名特有★) | ★**台账自相矛盾** ★ |
| 7 | `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` | 硬保护路径反向用例 (S4 与 S8 都红) | 硬保护件发生过一次真实合法改板 |
| 8 | `check_shutdown_semantics.py` | S1 红 / S2 绿 ⇒ 改名会把关机语义判据打空 (★rename-safe★) | 关机语义与改名后的盘面脱节 |
| 9 | `check_timing_review_adc_sync.py` | S1/S2 红 ⇒ 上游崩 ⇒ fail-closed (★改名特有★) | 时序评审与盘面脱节 |
| 10 | `timing_check.py` | ★**崩在算术那一行** ⇒ 改名后网表查不到 ⇒ 上电时序算不出来 (★改名特有★) | 上电 / 复位预算算不出来 |

### ★2-1 链外那 4 道 (#4 / #8 / #9 / #10) 为什么【必须】收进来 ★

★**实测事实**: ISS-321 的表已证明 ★**板那一趟当天这 4 道会红**★ (S1/S2 列 rc≠0) ★
★**而它们今天【不在】`state/gate_check.py` 的链上** ⇒ ★**没人会注意到它们红了**★ ⇒
★**⇒ 必须收进汇总闸, 否则「漏跑没人知道」这条路在 SW 域仍然敞着** ★

★**本机实读的挂链现状** (★`grep -c` 于 `state/gate_check.py`★):
`check_onepass_sw_sync` = 2 · `check_sw_ref_reachability` = 1 · `check_landing_trace_obligation` = 1 ·
`check_demo_panel_spec_r6_selftest` = 1 · `..._r6_chainjudge_selftest` = 1 · `..._r6_hardprot_iss315_selftest` = 1
★⇒ **链上的 6 道** ★
★`check_demo_panel_spec.py` / `check_shutdown_semantics.py` / `check_timing_review_adc_sync.py` / `timing_check.py`
= ★**0** ★ ⇒ ★**链外 4 道** ★

---

## 3 ★fail-closed 四条语义 (★对标 `state/gate_check.py` 的 `run_external_gate` + MECH 侧同款★)★

| # | 情形 | 汇总闸怎么判 | rc 记法 |
|---:|---|---|---|
| ① | ★**脚本不存在** ★ | ★**算闸红** (★不许静默跳过★) | `rc=None` + 详情「闸脚本不存在 … 视为闸红」 |
| ② | ★**脚本跑不起来 (异常)** ★ | ★**算闸红** | `rc=None` + 详情「闸脚本跑不起来: …」 |
| ③ | ★**超时** ★ (口径 ★**300s** ★) | ★**算闸红** | `rc=None` + 详情「闸脚本超时 (300s) …」 |
| ④ | ★**跑完 rc≠0** ★ | ★**算闸红** + 解析 stdout 的 `[FAIL]` / `❌` 行当详情 | `rc=该值` |
| ⑤ | 跑完 rc=0 | 闸绿 | `rc=0` |

★**清单本身也参与判决**: ★**少一道 ⇒ 汇总直接红** ★

---

## 4 ★TMPDIR 约定 (★本机系统临时目录配额已到顶·不指会 6 道一起假红★)★

★**汇总闸给每个子进程设**:
```
TMPDIR = TMP = TEMP = <项目根>/tmp/iss335_tmp
```
★**并对 3 道 R6 闸额外传** `--tmpdir <项目根>/tmp/iss335_gates` ★

★**为什么**: ★**本机系统临时目录带配额且本用户配额已到顶** ⇒ 沙盒写不进去 ⇒ `OSError [Errno 122] Disk quota
exceeded` ⇒ ★**6 道闸一起假红** ★ ⇒ ★**ISS-297 / ISS-299 两单都踩过** ★
★**(★自检 §⑦ 会断言 TMPDIR 落在项目根内★)** ★

---

## 5 ★三道 R6 selftest 闸【必须裸跑】(★本单最容易踩的坑★)★

★**实测事实** (★ISS-318 交卷页 §B4-2★): 这 3 个文件的 argparse ★**没有** `--selftest` 参数 ★
(只有 `--root` / `--tmpdir`) ⇒ ★**带 `--selftest` 会 rc=2 usage 错误 ⇒ 汇总闸自己红 ⇒ 假红** ★

★**本闸的处置**: ★**判决清单里这 3 道 `args` 只有 `("--tmpdir", …)`** ★
★**自检 §⑥b 会现场证明「手动加 `--selftest` ⇒ rc≠0」⇒ 这条坑是真的** ★

---

## 6 ★「板那一趟当天 SW 侧怎么跑」的逐字 SOP★

### ★步 0 · 前提★

★**板 md5 当天会【合法地】变一次** ⇒ ★**不许为了「让闸变绿」去改板** ★
★**SOP 的第一原则: ★红了 = 停下来 = 回 main; 不是「红了 = 去改板」★** ★

### ★步 1 · 先钉住盘面 (★跑之前先留底·免得事后说不清★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c "%y %n" HW/PCB/demo_mainboard.kicad_pcb
```
★**期望**: 板 md5 = 跑之前的值 (★当天可以是新值, 只要是【合法改板通道】改的★) ★

### ★步 2 · 跑汇总闸 (★就这一条命令★)★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_onepass_sw_release.py ; echo "RELEASE_RC=$?"
```
★**期望**: `RELEASE_RC=0` + ★**逐条列出 10 道闸各自的 rc** ★

### ★步 3 · 红了怎么办 (★逐条·不许跳★)★

1. ★**看它【点名】的是哪一道** ★ (汇总输出里「红了的那道闸」段会逐条点名 + 详情)
2. ★**读那道闸的详情** ★ (★不是看总 rc·是看详情★)
3. ★**分类** ★:
   - ★**A 类 · 板改了但 SW 侧没跟上** (位号漂移 / 输入没同步 / 落表留痕缺失) ⇒
     ★**按【合法改板通道】补 SW 侧的同步 + 落表留痕 (ISS-296 通道) ⇒ 让判决源跟着板走** ★
   - ★**B 类 · 闸本身/台账自相矛盾** (链头不唯一 / 单号抢同一个 md5) ⇒
     ★**停下来交 main 裁决** ★ ⇒ ★**不许自己放宽判据 / 不许改基线** ★
   - ★**C 类 · 假红** (见 §7) ⇒ ★**按 §7 处理·不许去改板** ★
4. ★**处理完重跑步 2** ⇒ ★**板 md5 只许变一次** ★
5. ★**★绝不许**: ★改板凑绿 / 改闸里的基线常量 / 放宽判据 / 删台账行 ★ ⇒
   ★⇒ **板 md5 变第二次 ⇒ 整趟白跑** ★

### ★步 4 · 回滚三档 (★从轻到重·★先试轻的★)★

| 档 | 动作 | ★什么时候用★ |
|---:|---|---|
| ★一档** | ★**只补 SW 侧文档 / 台账** (★零改板·零改闸·零改基线★) | ★A 类: 板已合法改完, 只是 SW 侧没跟上 ⇒ ★**这一档是首选** ★ |
| ★二档** | ★**回退 SW 侧那一批改动** (★把本趟 SW 侧文档/台账改动撤掉·板不动★) | ★一档搞不定·或本趟 SW 侧改动被误改坏 ⇒ ★**板仍只变一次** ★ |
| ★三档** | ★**整趟中止** (★板的那一次合法改板也回退·下一趟重来★) | ★二档之后仍红·或发现板面本身有硬伤 ⇒ ★**代价最大·最后才用** ★ |

★**任何一档都【不许】碰**: ★板 (除非第三档整趟中止) · ★既有闸的判据数字 · ★台账既有行 ★

### ★步 5 · 留证★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_onepass_sw_release.py --json > logs/iss335/day_run_<日期>.json
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

---

## 7 ★本闸会不会自己假红? (★逐条列 + 各自怎么处理★)★

| # | 假红路径 | 症状 | 处理 |
|---:|---|---|---|
| 1 | ★**R6 三道被误传 `--selftest`** ★ | rc=2 usage 错误 | ★判决清单里这 3 道**只**传 `--tmpdir` ★ (自检 §⑥b 现场证明) |
| 2 | ★**TMPDIR 落到系统临时目录** ★ | 6 道一起 `Errno 122` | 汇总闸强制把 TMPDIR 指项目内 (自检 §⑦ 断言) |
| 3 | ★**链外 4 道当天本来就红** ★ | #4/#8/#9/#10 红 | ★**这是【真信号】不是假红** ★ ⇒ 走 §6 步 3 的 A/B 类分流 ⇒ ★**但绝不许因为它红就去改板凑绿** ★ |
| 4 | ★**闸脚本被挪走 / 改名** ★ | rc=None + 「不存在」 | ★**fail-closed: 算闸红** ★ ⇒ 确认是不是本趟有人挪了 ⇒ ★**不许把清单改小来绕过** ★ |
| 5 | ★**单闸跑到 300s 超时** ★ | rc=None + 「超时」 | 看那道闸是不是本机慢 (★`timing_check.py` 最重★) ⇒ ★**不许把 timeout 调大来掩盖** ★ |
| 6 | ★**影子道 (v2) 红** ★ | 影子段红、汇总仍绿 | ★**默认【不参与判决】★** ⇒ 说明 v2 抓到了 v1 放过的东西 ⇒ ★**别去改板** ★ ⇒ 交 main 拍 (§B5-①) |
| 7 | ★**清单被改小 (少一道)** ★ | 汇总直接红 + 列出缺哪道 | ★**这是设计意图** ★ ⇒ 补回基准里的 10 道 |

---

## 8 机器读 / 参数

```bash
python3 SW/tools/check_onepass_sw_release.py                    # 人读 (逐条 rc)
python3 SW/tools/check_onepass_sw_release.py --json             # 机器读
python3 SW/tools/check_onepass_sw_release.py --selftest         # 反向用例自检 (沙盒副本上跑)
python3 SW/tools/check_onepass_sw_release.py --ref-gate v2      # ★把位号可达性闸换成 v2★
python3 SW/tools/check_onepass_sw_release.py --ref-gate both    # ★v1 + v2 都进判决★
python3 SW/tools/check_onepass_sw_release.py --shadow-strict    # ★让影子道也参与判决★
python3 SW/tools/check_onepass_sw_release.py --shadow-off       # ★不跑影子道★
python3 SW/tools/check_onepass_sw_release.py --timeout 600      # ★单闸超时★
```

★**★边界 (★本闸自己守着的那几条线★)★**
★**零写板 · 零落表 · 零改既有 16 道 `SW/tools/check_*.py` · 零改 `state/gate_check.py` ·
零改 `state/issue_log.yaml` · 零改别人的分片 · 零外发** ★
★**(★挂链是 main 的机制地界 ⇒ 本闸【不】自己进 `EXTRA_GATES`★)** ★
