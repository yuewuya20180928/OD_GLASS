# ISS-363 · sw-lead · 「板那一趟」S10 那一跳的【清单第 9 条】落法 + 「读封装栏」机器闸 · 纯分析 + 新建闸 + 沙盒预演 · 零写板 · 零改既有闸

★★**派单人**: 项目总工 (main / moli) · ★**派活时间**: 2026-11-23 15:45 GMT+8 · ★**cron fb67af40 (ARS45 队列自动派活)** ★

★★**主线口径**: ★**当前主线 = 绘制 PCB 图** (老板 2026-11-17 00:43) ⇒ PCB 线可派 ⇒ ★**但「板只改一次」⇒ 本单是【纯分析 + 新建闸 + 沙盒预演】类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发** ★

★★**外发口径 (★老板 2026-11-11 19:31 + ★★2026-11-12 02:02★)★★**: ★**不许外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询** ⇒ ★**缺口一律【自己网上查】+ 标证据等级 (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`) + 查不到就写降级方案** ⇒ ★**没有「批一句可以发」这个选项** ⇒ `state/outbox/` 里的草稿【一律不发】, 只作资料留档 ★

---

## ★★一 · main 的本机实读 (★不抄任何 agent 报告 · 全部数字可复跑 · 2026-11-23 15:4x★) ★★

### ★★1.1 上一趟 (ISS-362) 交了什么 · 本单接着干什么 ★★

★**ISS-362 (sw-lead · 已 verified)** 交的是「S10 换封装真值」这一跳对 SW 侧的**影响面**: 一页 `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` + 一道沙盒预演闸 `SW/tools/check_sw_fp_truth_impact.py` (H0~H7) + 交卷页 + 分片 ★

★**它自己的 H1 / H3 / H4 三条是【「登记式绿」】** ⇒ 它把三个缺口**登记**上了, 但**没有任何闸**去判这三件事:
- ★**H1** 「SW 侧读封装栏 (fp 栏)」这件事被登记了 ⇒ ★**SW 全域 0 道闸读 `footprint` 栏** (★ISS-362 页 §H1-REG 实测 H1-READERS = 0★)
- ★**H4** 「8 条板侧输入清单里没有「S10 换封装真值」这一条」⇒ ★**清单覆盖条数 = 0** ★

★**⇒ 本单 = 把 H1 从「登记」变成「有闸」, 并把 H4 从「登记」变成【可落地的补丁 + 沙盒证明】★** ★★**为什么这一跳值得单独一单**: 「板只改一次」那一趟 S10 会**合法地**把三份真源 (网表 / 脚表 / BOM) 的 md5 一起换掉 ⇒ 若清单里没有这一条 ⇒ 那一趟当天 SW 侧没人认领这一跳 ⇒ 红了没人解释 ⇒ 最坏的结果是有人为让闸绿去改锚点 / 改判据 ⇒ 那正是 ISS-273 / 275 / 284 三单花大力气堵掉的「悄悄换真源」漏洞 ★

### ★★1.2 本机实读数 (★可复跑★) ★★

| # | 事实 | 实测 | 复现 |
|---|---|---|---|
| 1 | ★**三份真源的封装栏在哪** ★ | 网表 `HW/netlist_v1.csv` 第 **14** 栏 `footprint` (513 行 · 非空 90) · 脚表 `HW/netlist_v1_pins.csv` 第 **11** 栏 `footprint` (584 行 · 非空 162) · BOM `HW/BOM_v1.csv` 第 **10** 栏 `footprint` (218 行 · 非空 218) | ★**按表头名定位 `footprint` 栏, 不许写死列号** ★ (★ISS-362 派活书写的「脚表第 12 栏」实为 `opn`, 已在页里更正★) · `head -1` 三份 csv |
| 2 | 清单里★**讲 fp 栏**★的条目数 | **0** (8 条里 0 条) | 本单新闸 F4 的实测口径 |
| 3 | 清单里★**泛提「封装」**★的条目数 | **4** (SW02 / SW04 / SW07 / SW08) | 同上 |
| 4 | 清单 JSON 块 `items` 条数 | **8** (`SW01_PCB_MD5` … `SW08_ESD_USB_D`) | `python3 SW/tools/check_onepass_sw_sync.py` |
| 5 | 清单每条固定字段 | **9 个**: `id` / `source_iss` / `title` / `current_state` / `action` / `criterion` / `step` / `blocked_by` / `evidence` | `SW/tools/check_onepass_sw_sync.py` 的 `FIELDS` |
| 6 | 清单闸 W4 的 `source_iss` 白名单 | **14 个**: ISS-225 / 234 / 241 / 244 / 266 / 269 / 271 / 273 / 274 / 275 / 276 / 277 / 278 / 279 ⇒ ★**ISS-362 / ISS-363 不在里面** ★ | `grep -n "SOURCES = " SW/tools/check_onepass_sw_sync.py` |
| 7 | 清单闸对★**多出来的条目**★ | ★**不判红** ⇒ 只要 9 字段齐全 + `step` ∈ S1~S13 + `source_iss` ∈ 白名单 + `criterion` 脚本在盘 ⇒ ★**第 9 条可以加, 且【不必改既有闸】** ★ | `REQUIRED_IDS` 只判「8 条一条不许漏」 |
| 8 | ISS-362 闸 H4 的判据是动态还是硬编码 | ★**动态**: 判「页里登记的 `H4-ITEMS` / `H4-COVER` / `H4-GENERIC` == 本机实测」⇒ ⇒ ★**加第 9 条后 H4 会红, 但【不需要改闸脚本】, 只要同步页里 §H4-REG 三个数字** ★ | `grep -n "H4-ITEMS" -A 6 SW/tools/check_sw_fp_truth_impact.py` |
| 9 | 页里 §H4-REG 现值 | `H4-ITEMS` = **8** · `H4-COVER` = **0** · `H4-GENERIC` = **4** | `grep -n "H4-ITEMS" SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` |
| 10 | 落表台账链头 | `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★判决源台账★) | `python3 SW/tools/check_demo_panel_spec.py` (内部 `sw_ledger_state()`) |
| 11 | 板双证 | md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` | `md5sum` + `stat -c %y` |
| 12 | 受保护件现值 md5 (★本单不许动★) | `SW/BOARD_ONEPASS_SW_SYNC.md` = `b8f935db333c16fa1051f0b06ae3e6ec` · `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` = `17b3c38c397e9aab06c8d2cbdd7d7461` · `SW/SW_MD5_BASELINE_LEDGER.md` = `83fafcf7d22d8fa999a1db74c781956d` | `md5sum` 三件 |

★**⇒ 本单要交的那块「可落地的补丁」= 三处同批落地 ★**:
1. `SW/BOARD_ONEPASS_SW_SYNC.md` ⇒ §2 逐条表加 1 行 + §2.1 归属步分布表 (★S10 的条数 3→4★) + §6 JSON 块 `items` 加 1 项 (9 字段齐全)
2. `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` ⇒ §H4-REG 三个数字 (★8→9 / 0→1 / 4→新值★) + H4 标题语义从「没有 S10 条」改成「已有 S10 条」
3. `SW/tools/check_fp_truth_read.py` (★本单新建★) ⇒ 把 H1 从「登记」变成「有闸」

★**★为什么本单【不许】直接落真件 (★边界的最硬一条★)★**:
① 那个 `.md` 是 ★**ISS-362 签收闸的 PROTECTED 件** (md5 `b8f935db333c16fa1051f0b06ae3e6ec`) ⇒ 改了它, ISS-362 的签收脚本重跑会红 ⇒
② 真件落地必须★**三处同批**★ ⇒ 中间任何一刻不同步 ⇒ 链就红 (★§三 的反证会实跑出来★) ⇒
③ ⇒ ★**本单只出补丁 + 沙盒证明, 真件落地是 main 的一键动作** ★ (★★本单不许碰 §2 三处里的任何一处真件★★)

---

## ★★二 · 本单交付物 (3 件 · 不许扩项) ★★

### ★★① 交卷物 (3 件) · 第 1 件 · 一页 (★新建★): `SW/BOARD_ONEPASS_FP_TRUTH_READ_ENTRY.md` ★★

★**必须包含 (★逐条 · 不许少★)**:
- ★**§0 口径与本机实读数** ★: 上面那张 12 行表逐行抄进去 ⇒ ★**每个数字都要能被某条命令复现 · 不许抄 main 的转述** ★
- ★**§1 ★SW09 的 9 个字段逐字段草案★** ★: `id` / `source_iss` / `title` / `current_state` / `action` / `criterion` / `step` / `blocked_by` / `evidence` ⇒ **每一栏给值 + 给依据** (★哪个本机读数支持它★)
  - ★**`source_iss` 必须用既有闸白名单里的 token** ⇒ 建议 `ISS-241+ISS-244` (★落表残项 8 行的 footprint 选型归 ISS-241 / ISS-244 · 见清单 SW03 那行的 `current_state`★) ⇒ ★**不许写 ISS-362 / ISS-363 (★不在白名单 ⇒ W4 当场红★)★** ⇒ 但★**「本条的发现依据 = ISS-362」必须在页里正文写清** ⇒ 来源不隐瞒, 只是 `source_iss` 字段按「输入来源」口径填 ★
  - ★**`criterion` 必须是一条真命令** ⇒ 指向本单新建的那道闸 (★`python3 SW/tools/check_fp_truth_read.py` ⇒ rc=0★) ⇒ ★**不许写不存在的脚本 (★W3 会当场红★)★**
  - ★**`step` = `S10`** ★ · ★**`evidence` 栏必须落在五级白名单** ★ · ★**`current_state` 里的每个实测值都要能被复现** ★
- ★**§2 ★三处同批落地的补丁清单★** ★: 逐处给 ★**改哪个文件 / 哪几行 / 改前逐字 / 改后逐字 / 为什么必须同批 / 谁来落** ★ ⇒ ★**真件零改, 补丁只在本页里** ★
- ★**§3 ★双态判据的设计说明★** ★: ★**为什么新闸不许断言「清单里必须没有第 9 条」或「必须有第 9 条」, 而只断言「登记数 == 实测数」★** ⇒ ⇒ ★**这样第 9 条落地那天新闸不红, 而 ISS-362 的 H4 会红 ⇒ 于是本单交付的 §2 补丁正好是那天的落地方案 (而不是一颗哑弹)★** ★
- ★**§4 降级方案 (★逐项必填 · 不许空着★)** ★: ★**查不到 ⇒ 写官网参数可满足的等效件 / 沙盒验证法 / 改设计路径绕开 ⇒ 三选一写清代价** ★
- ★**§5 未决项与卡点** ★: ★**哪些真需要老板拍 (★例: SW09 的 `blocked_by` 到底写「落表批次」还是「U-1 板宽档位」· ★你只登记不代拍★)★** ★

### ★★② 交卷物 (3 件) · 第 2 件 · 一道新闸 (★新建★): `SW/tools/check_fp_truth_read.py` ★★

★**判据 (★内容级 · 不挂 md5 锚点 · 照 `SW/tools/check_sw_fp_truth_impact.py` 的做法 · 文档改一个字就重判★)**:
- ★**F1** ★**三份真源的封装栏可读** ★: ★**按表头名定位 `footprint` 栏 (★不许写死列号★)** ⇒ 报出每份真源的「行数 / 封装栏非空条数 / 封装栏为空条数」实测值 ⇒ ★**判据自己跑统计, 不抄页里任何数字** ★
- ★**F2** ★**盘上现值 == 落表台账链头 (三件)** ★: ★**复用 `check_demo_panel_spec.sw_ledger_state()` 口径, 不许自己另写一套链头算法** ★ ⇒ 三件全对才绿
- ★**F3** ★**仍 open 的 to=sw-lead need 引着的 md5 == 链头** ★: 扫 `state/fragments/sw.yaml` 的 `needs_from` 里**仍 open** 的条目 ⇒ 抽出 32 位 md5 ⇒ 与链头逐条比对 ⇒ 不等 ⇒ **点名 need key** ⇒ ★**这是 B5-3 的机器化 (★代替人工去改 need 正文★)★** ⇒ ★**今天的实测量由你脚本自己算, 不许抄 main 的转述** ★
- ★**F4** ★**清单「讲 fp 栏的条目数」登记 == 实测** ★: 页里登记的条数必须 == 脚本实测 ⇒ ★**双态: N=8 / M=0 与 N=9 / M=1 都绿, 只要登记与实测一致** ★ ⇒ ★**改了清单没同步登记 ⇒ 红** ★ ★★**这是本闸最关键的判据★** ★
- ★**F5** ★**零写板 + 零落表自证** ★: 板 md5 / mtime + 三份真源 md5 == 基线 ⇒ 任一漂移即红
- ★**F6** ★**禁语** ★: 页里不许出现「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」(★老板 2026-11-12 02:02★)
- ★**F7** ★**证据等级五级白名单** ★: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` ⇒ 写 `[官方]` = 红
- ★**F8** ★**`--selftest` 反向用例 ≥6 条, 每条自证「红的是目标那一条, 其余仍绿」** ★ (★每条都要点名哪一条判据红了★)

★**沙盒一律落项目盘 `tmp/iss363_sbx/` (★不许写 /tmp ★ · ★禁止 `os.symlink` ★ · ★2026-11-23 04:4x 实测系统 /tmp 配额已满 ⇒ 写 /tmp 会让闸拿到假读数★)** ★
★**★不许把新闸挂进 `state/gate_check.py` 的 EXTRA_GATES 或 `SW/tools/check_onepass_sw_release.py` 的 MANIFEST (★挂不挂链 = main 的机制地界 · ISS-330 / ISS-333 同款★) ⇒ ★**只交脚本 + 路径 + 建议挂法** ★**

### ★★③ 交卷物 (3 件) · 第 3 件 · 交卷页 + 分片 + 留证 ★★

- ★**交卷页** `HANDOFF/2026-11-23_sw-lead_ISS363_S10清单第9条落法.md` (★B1~B6 六段齐全 + 20 条验收逐条判定 + 落盘文件清单 + 沙盒留证路径★)
- ★**分片** `state/fragments/sw.yaml` ★**只走 `state/frag_write.py`** ★ ⇒ ★**写前后各记一次 md5 基线 · 期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」· 不许静默覆盖** ★ (★这正是 ISS-359 / ISS-360 两单治的病★)
- ★**留证** `logs/iss363/` (★基线 md5 / 实算输出 / 三处补丁 diff / 沙盒 10 道闸全量输出 / selftest 全量输出★)

---

## ★★三 · 沙盒预演 (★本单的核心证明 · 不许省★) ★★

★**在 `tmp/iss363_sbx/` 里做 (★副本, 不许碰真件★)**:
1. ★**复制三份** ★: `SW/BOARD_ONEPASS_SW_SYNC.md` + `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` + 本单新闸 ⇒ 副本
2. ★**在副本上做「三处同批落地」** ★: 副本清单 JSON 块加 SW09 (9 字段齐全) + §2 表加行 + §2.1 分布表改数 + 副本页 §H4-REG 三个数字同步
3. ★**实跑 10 道 SW 闸基线 ⇒ 全绿** ★ ⇒ ⇒ ★**证明「三处同批落地 ⇒ 全链仍绿」** ★
4. ★**反证** ★: ★**只改清单不同步登记 ⇒ ISS-362 闸 H4 红 + 本单新闸 F4 红** ★ ⇒ ⇒ ★**证明「必须同批」** ★
5. ★**沙盒里的每一道都要贴原样输出 (★不许写「应该绿」★)** ★

---

## ★★四 · 边界 (★逐条 · 不许越★) ★★

★**零写板** ★ (★板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B ⇒ **开工前 + 交卷后各打一次双证**★) ★
★**零落表** ★ (★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/SCHEMATIC_LANDING_V1_LANDED.md` / 原理图 / `state/issue_log.yaml` 一字不改★) ★
★**零改既有闸** ★ (★`SW/tools/check_onepass_sw_sync.py` / `SW/tools/check_sw_fp_truth_impact.py` / `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改★) ★
★**零改既有页面** ★ (★`SW/BOARD_ONEPASS_SW_SYNC.md` / `SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md` / `SW/SW_MD5_BASELINE_LEDGER.md` ★**老字一字不许删 · 不许改 · 只在本单交卷页里写补丁方案**★) ★
★**零挂链** ★ (★不许把新闸写进 `state/gate_check.py` 的 EXTRA_GATES 或 `check_onepass_sw_release.py` 的 MANIFEST★) ★
★**零外发 / 零采购 / 零联系供应商** ★ (★不发邮件 · 不询价 · 不问询 · 不下采购单★) ★
★**不替老板拍板** ★ (★你只登记缺口 + 给依据 + 给代价 · **不许代选**★) ★
★**不写别人的分片** ★ (★只写 `state/fragments/sw.yaml`★) ★
★**证据分级必标** ★ (★`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`★) ★
★**单条 `exec` ≤ ~120 秒 · 不许 `yaml.safe_load` 3 MB 的 `STATE.yaml`** ★ (★ISS-360 cont0 就是死在这上面★) ★

---

## ★★五 · 必跑命令 (★全部真实存在 · main 本机实测过★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss363_tmp TMP=$PWD/tmp/iss363_tmp TEMP=$PWD/tmp/iss363_tmp
mkdir -p "$TMPDIR"
python3 SW/tools/check_fp_truth_read.py            # ★本单新建★
python3 SW/tools/check_fp_truth_read.py --selftest
python3 SW/tools/check_onepass_sw_sync.py          # 清单闸 · rc=0
python3 SW/tools/check_sw_fp_truth_impact.py       # ISS-362 闸 (真件) · rc=0
python3 SW/tools/check_onepass_sw_release.py       # SW 侧准出汇总闸 · rc=0
python3 state/merge.py
python3 state/gate_check.py
python3 state/check_brief_commands.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv SW/BOARD_ONEPASS_SW_SYNC.md SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md SW/SW_MD5_BASELINE_LEDGER.md
```

★**验收线 (★20 条 · main 会自己复跑 · 不采信你的自述★)**:
① 页存在且非空 ② §0 的 12 行读数与脚本实算一致 ③ SW09 的 9 个字段逐字段在页里 ④ SW09 的 `source_iss` token 全部在既有闸白名单里 ⑤ SW09 的 `step` = S10 ⑥ SW09 的 `criterion` 指向的脚本在盘 ⑦ §2 三处补丁逐处给改前改后逐字 ⑧ 新闸 rc=0 ⑨ `--selftest` ≥6/6 全 PASS 且每条自证「只红目标那一条」 ⑩ 新闸 F4 双态成立 (★登记 8/0 时绿 · 登记 9/1 时也绿 · 登记与实测不一致时红★) ⑪ 新闸 F3 自己算出「仍 open 的 need 引着的 md5 ≠ 链头」的条数 (★不许抄 main★) ⑫ 沙盒三处同批落地后 10 道 SW 闸全绿 (★原样输出★) ⑬ 沙盒反证「只改清单不同步登记 ⇒ H4 红 + F4 红」 (★原样输出★) ⑭ 沙盒在项目盘 `tmp/` 且无 `os.symlink` ⑮ 板 md5 / mtime 逐字节未变 ⑯ 网表 / 脚表 / BOM / 落表台账 md5 逐字节未变 ⑰ 既有闸脚本一个字节未改 ⑱ 既有页面老字零改动 (★md5 同值★) ⑲ `merge.py` rc=0 且 `gate_check.py` rc=0 且 `check_onepass_sw_sync.py` rc=0 且 `check_sw_fp_truth_impact.py` rc=0 ⑳ 分片写入只走 `frag_write.py` + 交卷页 B1~B6 齐全 + `logs/iss363/` 留证在盘 ★
