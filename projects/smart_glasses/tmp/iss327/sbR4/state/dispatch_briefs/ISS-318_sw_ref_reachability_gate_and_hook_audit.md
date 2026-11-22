# ISS-318 · sw-lead 任务书 —— ★★【「板只改一次」那一趟的 SW 侧: ①把那 95 处位号引用做成【机器可判的重命名影响面闸】 ②把 ISS-315 的三道新闸挂链前的【门禁链体检】做完 (含 ISS-309 那道一直没挂的)★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-318
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**性质**: ★**内部活 · 判据新建 + 判据修复类 (SW 侧)** ★
> ★**边界 (硬)**: ★**零写板 · 零落表 · 零改既有文档正文 · 零改既有判据方向 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★0 · 本单为什么存在 (★main 08:1x 本机实读, 不抄任何 agent 报告★) ★

★**两件事在 SW 侧都还开着, 而且两件都【不卡在老板身上】⇒ 现在就能做完**: ★

### ★★① 位号改名 (S1) 会踩到 SW 侧的 95 处位号引用 — 但没有任何闸管这件事 ★★

★**main 08:1x 本机实跑 `grep -hoE` (★细口径: `R_`/`C_`/`U_`/`J_`/`D_`/`L_`/`Q_`/`TP_`/`LED_`/`SW_`/`VBUS_`/`PWR_` 开头的标识符★) 实测**:

| 文件 | 唯一位号数 |
|---|---|
| `SW/SW_TIMING_REVIEW.md` | **63** |
| `SW/SHUTDOWN_SEMANTICS_SPEC.md` | **30** |
| `SW/BOARD_ONEPASS_SW_SYNC.md` | **23** |
| `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` | **8** |
| `SW/LOAD_SWITCH_SELECTION_FACTS.md` | 4 |
| `SW/POWER_STATE_SEMANTICS.md` | 4 |
| `SW/ADC_CALIBER_TABLE.md` | 4 |
| ★**SW 侧合计 (唯一) ★** | ★**95** ★ |

★**★ISS-314 (verified) 实测: 板那一趟的 S1 会给 156 个板位号加 `_1` 后缀 ⇒ ★**改名之后, 上面这些文档里引用的位号就【对不上板了】★ ⇒ ★**但 SW 侧现在【没有任何一道闸】检查「SW 文档里引用的位号是否还存在于板上」★★ ⇒ ★**改完板, SW 侧没人知道自己的文档烂了 ⇒ 这正是「板改第二次」的典型入口** ★

★**★更要紧的是: 这个问题在【闸链里是隐形的】⇒ SW 侧的 9 道闸全部 rc=0 (★main 08:1x 实跑全绿★) ⇒ ★**「全绿」不等于「改完板之后还对」★** ★**

### ★★② ISS-315 立的三道新闸 + ISS-309 立的那一道, 一道都没挂进 `state/gate_check.py` ★★

★**ISS-315 (verified) 交卷单 §3.3 逐字写的是「建议 main 挂进 `EXTRA_GATES` 的【具体位置与写法】(★本单没改 `state/gate_check.py`★)」⇒ ★**挂闸是 main 的机制地界 ⇒ 但【挂之前该体检什么】是 sw-lead 的活★** ★
★**★而且 ISS-315 自己的交卷页 §5 第 6 条写得很清楚: 「`check_demo_panel_spec_r6_selftest.py` (ISS-309 的 7/7) ★**建议也一起挂 —— ISS-309 当初就建议过, 至今没挂★」⇒ ★**这一道从 ISS-309 拖到现在已经两轮了★** ★

★**★本单 = 把这两件都做完 (★挂在链上是 main 的活, ★**但「挂上去会不会当场红」「挂上去之后判据方向有没有变」「挂上去要花多久」这三件事必须先有实测答案★)★**

---

## ★1 · 交两件 (★每件都必须有机器可判的验收★) ★

### ★★★ 第一件 · 【SW 侧位号引用闸 (★新建一道·★判据方向是「引用的位号必须存在于板/网表」★)】★★★

★**要交一道新闸** (★建议路径 `SW/tools/check_sw_ref_reachability.py` · ★**新建, 不许改既有闸★**), 判据方向固定:
★| 判据 | 内容 |
|---|---|
| ★**R1 引用可解析** ★ | ★**SW 侧每份文档里引用的每个位号, 必须能在【板文件】或【网表】里找到** ⇒ 找不到 ⇒ ★**列出「哪个文件 / 哪一行 / 引用的是谁 / 板与网表里现在叫什么」** ★ |
| ★**R2 区分「设计意图」与「引用」** ★ | ★**★不许把所有 `R_`/`C_` 开头的东西都当位号 ⇒ 必须先分类 (★真位号 / 电源轨名 / 逻辑信号名 / 文档自己的编号★) ⇒ ★**分类规则写进闸里, 且必须能用一条命令复现★** ★ |
| ★**R3 现状基线** ★ | ★**★跑当前盘面 ⇒ 给出「现在有多少条引用对不上」的基线数 (★这个数就是闸的允许上限★) ⇒ ★**不许为了让闸绿而放宽上限★** ★ |
| ★**R4 反向用例** ★ | ★**≥3 条反向用例 (★沙盒副本上改坏 ⇒ 判红★) + ★**每条都要有「不是巧合」自证** (★同一棵被改坏的树, 修前的闸必须判绿★) ★ |
| ★**R5 fail-closed** ★ | ★**板文件读不到 / 网表读不到 / 文档列表拿不到 ⇒ 判红 (★不许静默跳过⇒绿灯★)** ★ |

★**★硬约束★**:
- ★**★零写板 · 零落表 · 零改既有闸 (★`state/gate_check.py` 一个字节不许碰★ ⇒ **挂闸是 main 的活**★) · 零改 SW 侧既有文档正文★ ★**只新建 1 个脚本 + 1 份交卷单 + 1 个 logs 目录 + 自己那一份分片** ★
- ★**★不许把「位号改名」这个具体方案写进判据★ ⇒ 判据只问「你引用的位号现在存在吗」⇒ ★**这样 S1 走①还是③, 闸都不用改★** ★
- ★**★R3 的基线数必须【实测】, 不许估★ ⇒ 并交「哪些引用现在就对不上 (★归类为『本来就该对不上』vs『真隐患』)」的清单** ★

### ★★★ 第二件 · 【三道新闸 + 一道旧闸的挂链前体检 (★只出结论与写法, 不挂★)】★★★

★**要交一份【挂链前体检报告】**, 逐闸给:
★| 闸 | 必答的问题 |
|---|---|
| ★**`SW/tools/check_landing_trace_obligation.py`** (★ISS-315 新立★) ★ | ★**① 现在挂上去 rc=? (★本机实跑, 不是抄★) ② 跑一次要多久 ③ fail-closed 三条还在不在 ④ ★**它会不会对「板那一趟的合法落表」假红 (★ISS-315 自己的 N-2 口径问题就是这条★) ⇒ 给出你实测的答案, 不给「应该不会」★** ★ |
| ★**`SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py`** (★ISS-315 新立★) ★ | ★**同上 ①~③ + 它是 selftest ⇒ 挂进链里会不会每次跑都改沙盒 (★★TMPDIR 指向不对就会假红★) ★** ★ |
| ★**`SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py`** (★ISS-312 新立★) ★ | ★**同上 + 它和 ISS-315 那道【是不是同一棵树的两条用例】(★若是 ⇒ 挂两道是不是重复投入★) ⇒ 给出你的判断★** ★ |
| ★**`SW/tools/check_demo_panel_spec_r6_selftest.py`** (★ISS-309 新立 · ★**从 ISS-309 拖到现在★**) ★ | ★**同上 + ★**它为什么至今没挂 (★★ISS-309 的交卷单里有没有说原因? 没说的话, 查清并写进报告★) ★** ★ |

★**★报告末尾必须给【挂链的逐字写法】(★照 `state/gate_check.py` 的 `EXTRA_GATES` 现有格式★) + 【挂上后 expected 的 Q1/Q7 读数变化】+ 【挂上后总耗时增量】⇒ ★★但 ★**挂闸这个动作本身不许做** (★`state/gate_check.py` 一个字节不许碰★ ⇒ ★★main 拿你的写法自己挂★)★ ★**

★**★额外必做 (★main 08:1x 实测出来的机器坑, 必须写进报告★)★**:
> ★**本机 `/tmp` 是带 `usrquota` 的 tmpfs 且配额已满 ⇒ 走沙盒的 `--selftest` 会因 `OSError 122 Disk quota exceeded` 假红 (★失效方向是安全的: 红, 不是假绿★) ⇒ ★**每一条 selftest 都必须带 `export TMPDIR=$PWD/tmp/iss318_tmp` 跑一遍, 并在报告里写明「不设 TMPDIR 会假红 + 怎么设」★★**

---

## ★2 · 交卷物 (★3 件, 一个都不能少★) ★

1. ★**新建 `SW/tools/check_sw_ref_reachability.py`** (★R1~R5 齐全 · ★**主模式 + `--selftest` 两个入口** · ★**不依赖任何需要 root 的工具 (★不许 import pcbnew★ ⇒ ★**用板文件文本解析★) ★**)
2. ★**新建 `HANDOFF/2026-11-18_sw-lead_ISS318_SW位号引用闸与挂链体检.md`** (★B0~B6 齐全 · ★**占位符 0** · ★**必含: 新闸的 R1~R5 逐条自评 + 四道闸的挂链前体检表 + 挂链逐字写法 + 给 main 的 need 一行 + 零写板双证★) ★
3. ★**新建 `logs/iss318/`** (★新闸的逐条原始输出 · ★R3 基线清单 (★「哪条引用对不上」的完整表★) · ★四道闸的体检原始输出 (★带 TMPDIR 的★) · ★md5 前后对照 · ★占位符扫描结果★) ★ + ★**改 `state/fragments/sw.yaml`** (★必须用 `python3 state/frag_write.py --agent sw-lead` 原子写★ ⇒ ★**禁止 `open(p,"w")`**★ ⇒ ★**只写自己那一份, `hw.yaml`/`mech.yaml`/`pm.yaml` 一个字节不许碰**★) ★

---

## ★3 · 交卷前必跑 (★输出原样贴进回复★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss318_tmp          # ★本机 /tmp 是带 usrquota 的 tmpfs, 配额已满 ⇒ 别写 /tmp★
mkdir -p "$TMPDIR"

# ---- ① 新闸主模式 + 自测 (★rc 必须 0★) ----
python3 SW/tools/check_sw_ref_reachability.py            | tee logs/iss318/ref_reachability_main.txt
python3 SW/tools/check_sw_ref_reachability.py --selftest | tee logs/iss318/ref_reachability_selftest.txt

# ---- ② 四道闸的挂链前体检 (★每道都带 TMPDIR 跑, 并记录耗时★) ----
for g in SW/tools/check_landing_trace_obligation.py \
         SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py \
         SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py \
         SW/tools/check_demo_panel_spec_r6_selftest.py ; do
  printf "%-60s " "$g"
  /usr/bin/time -f "rc=%x  %es" python3 "$g" --selftest >/dev/null
done

# ---- ③ 门禁链 (★rc 必须 0 · Q1 必须 18/18★) ----
python3 state/merge.py && python3 state/gate_check.py

# ---- ④ 零写板 / 零落表 双证 ----
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb

# ---- ⑤ 占位符扫描 (★必须 0★) ----
grep -cE "🔄|待填|PLACEHOLDER" "HANDOFF/2026-11-18_sw-lead_ISS318_SW位号引用闸与挂链体检.md"
```

★**★交卷页必须贴: ① 新闸的 R1~R5 逐条自评 + R3 基线数 ② 四道闸的体检表 (含耗时) ③ 挂链逐字写法 ④ 零写板双证 ⑤ 给 main 的 need 一行★**

---

## ★4 · 硬边界 (★违反就是不合格★) ★

★**零写板** · ★**零落表** · ★**零改 `state/gate_check.py`** (★**挂闸是 main 的机制地界 ⇒ 你只交写法与体检, 不挂**★) · ★**零改既有判据方向** (★`SW/tools/check_demo_panel_spec.py` / `check_onepass_sw_sync.py` 一个字节不许碰★) · ★**零改既有 SW 文档正文** (★`SW/SW_TIMING_REVIEW.md` / `SW/SHUTDOWN_SEMANTICS_SPEC.md` / `SW/BOARD_ONEPASS_SW_SYNC.md` 只读★) · ★**零改 `SW/SW_MD5_BASELINE_LEDGER.md`** (★★它就是判据的锚点账, 改了 = 改判据★) · ★**零外发** (★不发邮件 / 不询价 / 不问询 / 不采购 ⇒ ★**外部依赖一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + ★**查不到就写降级方案 (必须项)**★ ⇒ ★**没有「等老板批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 issue_log** · ★**只写自己那一份分片** ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

---

## ★5 · 给 main 的 need (★交卷页必含一行: need key + 一句话问法 + 不拍的后果★) ★

★**建议 need key (★两个, 一个都不能少★)**:
- ★**`iss318_sw_gates_hook_decision`** ★ | ★**问法**: ★**「ISS-315 新立的两道闸 + ISS-312/ISS-309 的两道 selftest, 挂不挂 `EXTRA_GATES`? (★本单已给出逐字写法 + 实测耗时 + 会不会假红·请裁·挂不挂是 main 的机制地界★)」** ★ | ★**不拍的后果**: ★**判据哪天被改软了没人拦 ⇒ ★**这正是 ISS-309 的起因**★ (★[实测] 依据)★ ★
- ★**`iss318_sw_ref_impact_gate`** ★ | ★**问法**: ★**「SW 侧位号引用闸 `SW/tools/check_sw_ref_reachability.py` (★本单新建★) 建好后挂不挂? 挂的话挂哪个位点 (★`EXTRA_GATES` 还是 `PINNED_MD5_GATES`★)?」** ★ | ★**不拍的后果**: ★**板那一趟 S1 改名之后, SW 侧 95 处位号引用对不上板 ⇒ 没人拦 ⇒ SW 文档带着过期位号进投产 ⇒ 投产端才发现★** ★

---

## ★6 · 纪律 (★这项目的老教训★) ★

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss318/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★
