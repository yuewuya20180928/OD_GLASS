# ISS-304 · hw-lead 任务书 —— ★★【钉板闸⑥ 作业包现状值闸: 落表一次 ⇒ 页面里的现值就漂 ⇒ 「板只改一次」那一趟不许开工】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-304
> ★**job**: cron `775d9893` (ARS45 继续执行后继计划) · ★**派活时刻**: ★**2026-11-18 01:1x** ★
> ★**性质**: ★**内部活 · 现状值重锚类 · 零写板 · 零落表** ★ ⇒ ★**外发**: ★**零外发** ★
> ★**★排队说明**: ★**本单由兄弟 job fb67af40 于 01:0x 新开进队列 (status=open) ⇒ 本 job 于 01:1x 派它 (★先落 fixing 再 spawn ⇒ 兄弟 job 的 advance.py 看不见 open 窗口 ⇒ 不会重复派同一个 agent★)** ★
> ★**★派活依据**: ★**ISS-302 (hw-lead) cont1 已于 01:03 交卷并于 01:1x 落 `verified` (★main 独立复验通过★) ⇒ ★**hw-lead 名额释放**★ ⇒ 本单可派 ★

---

## ★① 病灶 (★main 2026-11-18 00:5x 本机实跑, 原样 rc, 不抄任何 agent 报告★)

★**main 00:5x 实跑**:
```bash
$ python3 HW/check_workpack_state_values.py; echo "rc=$?"    # ★rc=1★
$ python3 state/gate_check.py; echo "rc=$?"                   # ★rc=1 (Q7 钉板 md5 闸链 8/9 绿)★
```
★**红的原文 (main 原样贴)**:
```
  FAIL  V4  现状值 == 盘面实测 (★实跑探针★): ❌
     ❌ id=W10_MD5_NETLIST:     实测值 '6aee500e60ba0732f83a9cf557ba90ab' 不在 fresh 原句里 ⇒ 订正句里的现值没跟上盘面
     ❌ id=W10B_MD5_PINS:       实测值 '9174309df1ec9411ac8e8d9e80ee386a' 不在 fresh 原句里 ⇒ 订正句里的现值没跟上盘面
     ❌ id=W10C_MD5_BOM:        实测值 '5b9993992405904a60ac96a020b375d8' 不在 fresh 原句里 ⇒ 订正句里的现值没跟上盘面
     ❌ id=C07_B26_MD5_LEDGER:  实测值 '6aee500e60ba0732f83a9cf557ba90ab' 不在 fresh 原句里 ⇒ 订正句里的现值没跟上盘面
```
★**★这就是「钉板闸⑥」** ⇒ ★**`state/gate_check.py` 的 Q7 钉板 md5 闸链 = 8/9 绿 ⇒ ★★板那一趟不许开工★★** ★

★**★为什么红**: ★**2026-11-18 00:21, ISS-302 又合法落表一次 (C_SYS / SYS_CHG 必装 + BOM 加 20 µF)** ⇒
★**网表/脚表/BOM 三件的 md5 变了**: `37f62ac3…`→`6aee500e…` · `a4270120…`→`9174309d…` · `5d02bece…`→`5b999399…` ⇒
★**而两份页面里那 4 条登记的 `fresh` 原句还停在 ISS-283 那一跳** ⇒ ★**闸判「订正句里的现值没跟上盘面」⇒ 红** ★

★**★真源在哪 (★main 已查清, 不用你再摸一遍★)**:
| 文件 | 角色 | 实测 |
|---|---|---|
| ★`state/_iss277_preflight_appendix.md` ★ | ★**sidecar: 两份页面 state_baseline 登记表的搬运源** (★29 条·含 `id` / `doc` / `anchor` / `fresh` / `expect_mode` / `expect_target` / `probe`★) ★ | 27,525 B · mtime 11-17 21:55 ★ |
| ★`state/_iss277_build_preflight.py` ★ | ★**清单页生成器 (★只做搬运, 不改一个字★) ⇒ sidecar 缺失 ⇒ fail-closed 拒写页★) ★ | ★`PREFLIGHT_PROJ` 环境变量可改项目根 (★沙盒跑法★)· `OUT` = `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ★ |
| ★`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ★ | ★**清单页** (★生成器产物★) ★ | 29 条登记 · L875/L891/L907/L1015 附近是那 4 条 `fresh` ★ |
| ★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` ★ | ★**作业包页** (★L811~L813 现状值表 + L1140/L1156/L1172/L1280 附近的 4 条 `fresh`★) ★ | 同 29 条登记 (★V1 要求两份逐字一致★) ★ |

★**★注意那 4 条登记的 `note` 自己就写着**: ★**「网表 md5 基线 ★走落表台账为准, 不写死★ (ISS-283 ⑩-b 的口径)」** ⇒ ★**口径早就定了是「走台账」, 只是这条链上次没跟上** ★

---

## ★② 要交的四件 (★每件都能独立验收★)

### ★B1 · 让那 4 条 `fresh` 原句跟上盘面 (★且【永不再漂】★)
★**两条路, 你定细节, 但下面 5 条不许破★**:
1. ★**判据不许放宽**: ★**`HW/check_workpack_state_values.py` 的判定逻辑一个字不许改** (★它是钉板闸⑥, 判据是板那趟的验收依据★) ★
2. ★**两份页面必须逐字一致** (★V1 判据: 两份文档的 29 条登记逐字一致★) ⇒ ★**改一边不改另一边 ⇒ V1 直接红** ★
3. ★**新 `fresh` 原句里必须逐字含当前实测值**: 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` ★
4. ★**★老字不许删 (★追加式自证★)**: ★**29 条 `anchor` 老字必须逐字还在 (★V2 判据★) ⇒ 只许改 `fresh` 那一格的值, 不许动 `anchor` / `correction_anchor` / `probe` / `expect_*`★** ★
5. ★**★不许手改生成器产物★**: ★**清单页 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md`) 是 `state/_iss277_build_preflight.py` 的产物 ⇒ 改它 ⇒ 等于下一次重跑就回退 ⇒ ★**必须改 sidecar / 生成器, 再重跑生成器** ★ (★ISS-292 的结论: 追加式订正块必须独立于生成器存放★) ★

★**★两条路的具体含义 (★选哪条都行, 但要写清选了哪条+为什么★)**:
- ★**路 A (最小改)**: ★**只把 sidecar 里那 4 条的 `fresh` 改成当前台账值 ⇒ 重跑生成器 ⇒ 清单页跟着变; 作业包页按同样的追加式改法同步** ⇒ ★**代价: 下次再落表还会漂 (⇒ 要写进交卷单并登记 need)★** ★
- ★**路 B (彻底)**: ★**让生成器在构建时从落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 现读该文件的链头 md5 ⇒ 拼进 `fresh` ⇒ ★**读不到 ⇒ fail-closed 拒写页 (★不许静默回退到硬基线★)★** ⇒ ★**代价: 作业包页不是这个生成器写的 ⇒ 那 4 条要靠另一个途径同步 ⇒ 你要查清并写下来** ★

### ★B2 · 幂等 (★★这是本单最容易被踩的坑★★)
★**ISS-292 留下的硬判据**: ★**生成器重跑 ⇒ 页 md5 逐字节相同 ⇒ 页回退这条路被堵死** ★
★**★但这次页的内容【本来就该变】(fresh 要跟上新 md5) ⇒ 所以判据是: 【改完之后】再跑一次 ⇒ md5 与改完那一刻相同 (★不是"与改前相同"★)★** ★
★**沙盒跑法 (★ISS-292 用过, 可照抄★)**: ★**用 `PREFLIGHT_PROJ` 环境变量把项目根指向临时目录 ⇒ 生成器写到沙盒的 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` ⇒ 跑两次比 md5 ⇒ 真盘一个字节不许动** ★
★**★同时验真页: ★**重跑真生成器一次 ⇒ 真页 md5 与你改完那一刻相同 (★证明没引入"重跑就回退"★)** ★

### ★B3 · 回归 (★别的闸一条不许红★)
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_workpack_state_values.py; echo "rc=$?"    # ★期望 rc=0 (★V4 那 4 条全绿★)★
python3 HW/check_workpack_state_values.py --selftest; echo "rc=$?"   # ★条数只许增不许减★
python3 HW/check_onepass_preflight_coverage.py; echo "rc=$?"
python3 HW/check_pin_function_labels.py; echo "rc=$?"       # ★★现在是 rc=1 = 15 条既有缺陷基线 (★不是本单的锅·原样写★)★
python3 HW/check_step1_parts_spec.py; echo "rc=$?"
python3 MECH/check_onepass_mech_release.py; echo "rc=$?"     # ★★现在 rc=1 = MECH 侧 N6 (★归 ISS-303·不是本单·原样写★)★
python3 state/merge.py; echo "rc=$?"
python3 state/gate_check.py; echo "rc=$?"                   # ★★期望 Q7 = 9/9 绿 (★现在 8/9★)★
python3 state/issue_check.py; echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```
★**★受保护 5 件**: ★板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · ★**网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` (★本单只读, 不许动★)★**

### ★B4 · 交卷物 (★4 件★)
1. ★**交卷单** `HANDOFF/2026-11-18_hw-lead_ISS304_作业包现状值重锚.md` (★B0 + B1~B6 六块齐全 + 幂等对照 md5 + 边界自证★) ★
2. ★**改动** = ★sidecar (`state/_iss277_preflight_appendix.md`) ★或★ 生成器 (`state/_iss277_build_preflight.py`) ★或★ 两份页面 (★按你选的路 B 说清★) ★
3. ★**日志** `logs/iss304/` (★沙盒两次跑的 md5 + 全量回归原样输出★) ★
4. ★**分片** `state/fragments/hw.yaml` (★走 `python3 state/frag_write.py --agent hw-lead` 原子写★ ⇒ ★**写完 `grep -c iss304` 校验 (★目标 ≥ 5★)★) ★

★**★真判据 (★main 实测的坑★)**: ★`python3 state/check_report_placeholders.py < <交卷单>` **抓不到 `🔄 待填`** ⇒ ★**真判据是 `grep -cE "🔄|待填"` 必须 = 0** ★

---

## ★③ 边界 (★违反就是不合格★)

★**零写板** (★板 + `.kicad_pro` md5/mtime 逐字节不变★) · ★**零落表** (★网表/脚表/BOM/落表台账/`state/p10_rows.json` 一个字节不许动★) ★
· ★**不许改 `HW/check_workpack_state_values.py` 的判据** (★它是钉板闸⑥★) · ★**不许动 `HW/check_pin_function_labels.py`** (★ISS-299 的重锚成果★) ★
· ★**不许动 `MECH/` 任何文件与分片** (★MECH 侧 N6 归 ISS-303★) · ★**不许改 `SW/`** · ★**零外发** · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★
· ★**只写自己那一份分片** (★`hw.yaml`★) · ★**实物 `[实测]` = 0 条** · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★) ★

---

## ★④ 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★
· ★**长任务一律 `nohup ... > logs/iss304/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★
· ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★
· ★**★改 sidecar / 生成器之前先备份一份 (★`cp` 到同目录 `.bak_20261118`★) ⇒ 好做【改前/改后】对照★** ★
