【ISS-333 · mech-lead · ★★MECH 侧位号可达性闸 · 从【设计稿】到【可直接挂的闸】的实现单 (★零改 state/gate_check.py·★挂闸由 main 执行★)★★】

★**★这是 main 拍板后开的单 (2026-11-18 19:2x)·★派活前置: ★**ISS-326 已落 (main 验完签字) ⇒ 你这条是它的执行单; ★**但挂闸本身是 main 的活 (ISS-330, owner=main) ⇒ 你交的是【可直接挂的闸 + 挂闸写法】★★ ★**

---

## ★★★【① 为什么开这一单 (★先读这一段·★别重走 ISS-326 的弯路★)★★★】★★★

★**ISS-326 (verified) 已经把「MECH 侧位号可达性闸」的设计稿交出来了, 但它【只到设计稿】(★它自己 §6 写着: ★**「本单只到设计稿, 不落闸」★) ⇒ ⇒ 那道闸到现在【还没挂进门禁链】⇒ ⇒ MECH 域的位号引用漂移, 今天仍然抓不到 ★ ★**

★**★已有成果 (★全在盘上·★不要重做·★但要自己复核一遍★)**:
| ★件★ | ★路径★ | ★说明★ |
|---|---|---|
| ★设计稿★ | `logs/iss326/gate_design/GATE_DESIGN.md` (13,443 B) | ★§0 一句话主张 / §1 扫描面 / §2 分类口径 / §3 fail-closed 三条 / §4 反向用例 (MECH 版 7 条) / §5 基线数怎么定 / §6 落地形态 / §7 边界 ★ |
| ★基线实测★ | `logs/iss326/gate_design/mech_gate_baseline.json` (22,472 B) + `mech_gate_baseline_raw.txt` | ★键: `scan_surface` / `tokens_unique` / `live_refs` / `classification` / `baseline_designator_missing` / `rule_histogram` / `baseline_tokens` / `rename_exposure` ★ |
| ★设计稿级原型★ | `logs/iss326/gate_design/mech_gate_proto.py` (9,032 B) | ★**只读 import** `SW/tools/check_sw_ref_reachability.py` 复用它的 `TOKEN_PREFIXES` / `read_board_refs` / `read_netlist_refs` / `read_net_names` / `classify` ⇒ ★**口径零漂移的做法** ⇒ 扫描面换成 MECH 递归 ★ |

★**★⇒ 本单 = 把那个原型变成【真能挂的闸脚本 + 自测 + 挂闸写法】⇒ ★**交 main 一键挂上 (ISS-330)★ ★**

---

## ★★★【② main 已定死的硬要求 (★全部来自 ISS-326 的实测·不是设计稿的自嗨·★一条都不许放宽★)★★★】★★★

1. ★**fail-closed 三条** (★设计稿 §3): ★**取不准必须判红, 不许放宽成「取最近一条」★ ★
2. ★**建闸日基线必须 MECH 侧自己 fresh 测** (★实测链: 原始 C14 = 60 → 剔除本单自污染 4 条 = 56 → 再剔除 py 变量名 40 条 = 16 ⇒ ★**MECH 侧是 16, SW 侧是 3, 不许抄 3**★) ⇒ ★**你必须自己跑一遍复现这个 16, 并把逐条明细落盘★ ★
3. ★**反向用例 ≥ 5 条** (★照设计稿 §4 那套 MECH 版 7 条·★**尤其必须含「假绿」那条: ★判据分支匹配不上时必须【红】, 不是【静悄悄不查了】★) ★ ★
4. ★**扫描面**: ★**`MECH/**/*.py` + `MECH/**/*.md` 递归** (★实测 113 份: 48 md + 65 py·唯一 token 230★) ⇒ ★**不许只扫顶层** ★ ★
5. ★**基线只许收紧不许放宽** (★同 SW 那道 `BASELINE_COUNT` 的规矩·★「收紧」要在交卷页里逐条写明**哪一条被解掉了**·★不许只改数字★) ★ ★

---

## ★★★【③ 本单要交的四件 (★就这四件★)★★★】★★★

### ★★★★【第 ① 件: 真闸脚本 (★新建·★可直接挂·★自测入口自带★)】★★★★★★
- ★**落 `MECH/tools/check_mech_ref_reachability.py`** (★新建·★`MECH/tools/` 目录已存在★) ⇒ ★**逻辑照抄设计稿 §2 的分类口径 (C1/C2/C14 三类 + 冻结注册表机制 + MECH 侧必须新增的两条) + §3 的 fail-closed 三条 ★ ★**
- ★**只读 import `SW/tools/check_sw_ref_reachability.py`** 复用它的口径函数 ⇒ ★**口径零漂移** ⇒ ★**但不许改那一个 SW 文件★ ★**
- ★**必须自带 `--selftest` 入口** (★照 SW 那道 `check_sw_ref_reachability.py` 的 `--selftest` 写法·★见 `SW/tools/check_sw_ref_reachability.py`★) ⇒ ★**自测用例 ≥ 5 条反向 + 正向 + 假绿那条 ★ ★**
- ★**必须支持「建闸日基线冻结」**(★照设计稿 §2 抄来的 freeze 机制⇒ ★**重建的触发条件 = 【盘面改过位号】, 不是【闸红了就重建】** ★**★这一条是 main 对 ISS-327 need #1 的拍板, 写进你这道闸的护栏里 (★零新增流程★)★ ★**

### ★★★★【第 ② 件: 基线复现 + 反向用例证据 (★全部落 `logs/iss333/`·★悬空引用 = 0★)】★★★★★★
- ★**基线**: ★**自己 fresh 跑一遍 ⇒ 逐条列出那 16 条 `DESIGNATOR_MISSING` 明细 (★token + 出现位置 + 为什么它是基线内★) ⇒ ★**若你实测的数 ≠ 16 ⇒ ★**如实写出来 + 说明差在哪 (★不许把 16 改成你算的数·★16 是 ISS-326 的建闸日基线·你的是「今天复现值」·两者都要写★) ★ ★**
- ★**反向用例**: ★**照设计稿 §4 那 7 条 (case1B/1C/1D/2/3A/3B/4) 逐条跑 ⇒ 每条给【期望 / 实际 / 判决】三列 ★ ★**
- ★**假绿用例**: ★**判据分支匹配不上时必须 rc≠0 且点名** ⇒ ★**这条是本单最要紧的自检 (★ISS-326 自己写的: ★「判据分支匹配不上时必须【红】而不是【静悄悄不查了】」★) ★ ★**

### ★★★★【第 ③ 件: 交 main 的挂闸写法 (★main 的机制地界·你只出写法不执行★)】★★★★★★
- ★**① 挂哪**: ★**实读 `state/gate_check.py` 的 `EXTRA_GATES` 结构 (★自己读, 不许猜★) ⇒ ★**给出「挂在第几位 / 用什么调用形态 / 参数怎么传」的逐字写法 + 行号 ★ ★**
- ★**② 挂完自检**: ★**挂完必须重跑 `merge.py` + `gate_check.py` + `issue_check.py` 三道 ⇒ ★**给出 main 挂完之后应当看到的期望输出 (★Q1/Q2/Q6/Q7 读数 + 新闸那一行 rc★) ⇒ ★**main 会照着贴 rc ★ ★**
- ★**③ 挂不挂的风险**: ★**给出「挂了会不会把现在的门禁链带红」的分析 (★基线 16 是建闸日值·若今天实测 ≠ 16 ⇒ 要不要先收紧到今天值·给建议 + 理由★) ⇒ ★**不许含糊★ ★**

### ★★★★【第 ④ 件: 交卷页 + 分片 (★B0~B6 齐全★)】★★★★★★
| ★#★ | ★交付物★ | ★路径★ | ★要求★ |
|---|---|---|---|
| 1 | ★**真闸脚本** ★ | ★`MECH/tools/check_mech_ref_reachability.py` (★新建★) | ★带 `--selftest` ★ |
| 2 | ★**交卷页** ★ | ★`HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` (★新建·★中文名照 ISS-326 交卷页命名法★) | ★**B0~B6 齐全** (★B1 结论摘要 / B2 验收标准自评·逐条「通过/不通过/未验」/ B3 证据分级·带 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 标签 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令·原样贴输出★) ⇒ ★**不许留「(施工中)」占位符** ★ |
| 3 | ★**证据目录** ★ | ★`logs/iss333/` | ★每条被引用的读数都有对应 raw 文件 ★ |
| 4 | ★**分片** ★ | ★`state/fragments/mech.yaml` | ★**必须走 `python3 state/frag_write.py --agent mech-lead`** (★禁止 `open(p,"w")`★) ★ |

---

## ★★★【④ 边界 (★违反就是不合格★)★★★】★★★
- ★**零写板**: ★**`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` · mtime 必须还是 `2026-11-06 07:07:17.362193413`** ★
- ★**零落表** (★网表/脚表/BOM/原理图真源一个字节不许动★)
- ★★★**零改 `state/gate_check.py`** (★挂闸是 main 的机制地界·★**本单只出闸脚本 + 挂闸写法**★) ★★★ · ★**零改 `state/check_*.py`** · ★**零改 `SW/tools/check_sw_ref_reachability.py`** (★只读 import★) · ★**零改既有 `MECH/**/*.md` 正文** · ★**零改既有 `MECH/**/*.py`** (★你只许新建 `MECH/tools/check_mech_ref_reachability.py`★) · ★**零改 `logs/iss326/`** (★那是已落的交卷证据·只读★)
- ★**沙盒只写 `tmp/iss333/` + `logs/iss333/`** · ★**只写 `state/fragments/mech.yaml`** · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ ★**没有「批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`**
- ★★★**沙盒里凡要【写】的文件 ⇒ 一律真拷贝; 写前 `assert not os.path.islink(path)`** (★sw-lead 11-18 14:39 因为软链写穿过一次真件★) ★★
- ★★★**一次 write 别超过 ~6000 字 ⇒ 先 write 骨架, 再 edit 逐块补** (★你自己连挂两趟都死在超长 write 上·★先落骨架, 再干活★) ★★
- ★★**文档纪律**: ★**MECH 侧任何要写「改名后名」或「形状像位号但不是位号」的文档 ⇒ ★**写进 `logs/iss333/`, 不许写进 `MECH/`** ⇒ ★**否则把你这道新闸自己带红 (★实测过: ★方案文档里写死位号 ⇒ 闸判新增真隐患 ⇒ rc=1★) ★★

## ★★★【⑤ 交卷前必跑 (原样输出贴进交卷页 B6)★★★】★★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py   # rc 必须 0
python3 state/gate_check.py   # rc 必须 0 (★本单不挂闸 ⇒ 门禁链与今天一样·不许自己去改它★)
python3 state/issue_check.py   # rc 必须 0
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb   # 必须 2026-11-06 07:07:17.362193413
python3 MECH/tools/check_mech_ref_reachability.py --selftest   # 必须全过
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md"   # 必须 0
grep -c "iss333" state/fragments/mech.yaml   # 必须 >= 1
find tmp/iss333 -type l | wc -l   # 必须 0
```

★额外纪律: ★**证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标** ★ · ★**不许外发任何邮件/询价/问询/采购 ⇒ 缺口一律自己网上查 + 标证据等级 + 写降级方案** ★ · ★**交卷前跑 merge.py (rc=0) && gate_check.py 并把输出贴进回复** ★

## ★★★【⑥ 一句话 (★本单到底在回答什么★)★★★】★★★
★**MECH 域的位号引用漂移到底能不能被机器抓住 ⇒ 那道闸从设计稿变成能挂的东西要改哪几行 ⇒ ★**挂不挂、怎么挂 ⇒ 交 main 一键执行 (ISS-330)★ ★**
