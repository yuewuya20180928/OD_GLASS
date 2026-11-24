# ISS-392 · sw-lead · SW 域【门禁链覆盖率 + 第三道病闸基线漂移】⇒ 把「板那一趟的 SW 侧护栏到底有几道真的在跑」变成机器可判

★**本单性质**: ★**纯分析 + 新建真相页 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【板那一趟·SW 侧护栏自守层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★
★★**★本单为什么必须做 (★main 本机实跑 · 不抄任何 agent 报告★) ★★** ★★

★**① 「板只改一次」那一趟会动板 (位号改名 + 板侧同步 + 布局修正 + 布线 45→0) ⇒ 板面 md5 会变 ⇒ SW 侧所有引用旧 md5 / 旧位号的护栏必须【当场红】才叫护栏** ★
★**② ★★main 本机实跑 `state/gate_check.py` 的门禁链, 逐条数: ★★盘上 `SW/**/check_*.py` 共 ★**30**★ 道, 而链里真正跑的只有 ★**6**★ 道 ⇒ ★★**24 道 SW 闸从来没进过门禁链** ★★** ★
★**③ ★★更要命的一条: 链上 (L222) 跑的是 ★★`SW/tools/check_sw_ref_reachability.py` (★旧版★)★★, 而 ISS-332 (★已签收 verified★) 交出的 ★★收紧版 `SW/tools/check_sw_ref_reachability_v2.py` 根本没挂链** ★★ ⇒ ★★**闸链里跑的是【被查出 4 条洗白面】的那一版, 修好的那一版在盘上没人跑** ★★** ★
★**④ ★★再叠一层: ISS-388 刚交的那道【元闸】`SW/tools/check_sw_gate_health.py` 自己只扫了 ★**13**★ 道 SW 闸 (★ROSTER 硬编码★) ⇒ ★★盘上另外 17 道 (★其中 15 道是带 `__main__` 的独立闸★) 它也看不见** ★★ ⇒ ★★**「元闸查闸坏了」这件事本身有 17 道的盲区** ★★** ★
★**⑤ ⇒ ★★**所以今天 SW 域的真相是: 板那一趟真会动板, 但绝大多数 SW 护栏那天根本不会跑; 跑着的那道里有已知洗白面; 连查闸有没有坏的那道元闸自己也只看了不到一半** ⇒ ★★**「板改完 SW 侧没人拦」这件事今天是【真】的, 不是假设** ★★**

---

## ★★一 · 本单的地界事实 (★main 本机实跑 · 逐条给了出处·★数字都可复现★) ★★

### ★★① SW 域闸: 盘上 30 道 vs 链里 6 道 (★main 本机实跑·不抄任何报告★) ★★

★**main 本机实跑命令**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
find SW -name 'check_*.py' | sort | wc -l          # ⇒ 30
grep -n '"SW"' state/gate_check.py | wc -l          # ⇒ 链里的 SW 闸引用行数
```
★**链里真跑的 6 道 (★逐字★)**: ★
| # | 闸 |
|---|---|
| 1 | `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py` |
| 2 | `SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py` |
| 3 | `SW/tools/check_demo_panel_spec_r6_selftest.py` |
| 4 | `SW/tools/check_landing_trace_obligation.py` |
| 5 | `SW/tools/check_onepass_sw_sync.py` |
| 6 | `SW/tools/check_sw_ref_reachability.py` ★★← **这是旧版 v1** ★★ |

★**⇒ ★★**24 道 SW 闸在盘上、闸链外。板那一趟动板时, 它们【一道都不会响】★★** ★

### ★★② 链上跑 v1, 收紧版 v2 没挂链 (★main 本机实跑★) ★★

★**`state/gate_check.py` L222-223 逐字**:
```python
    (os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability.py"),
     "SW 侧位号引用可达性闸 (ISS-318)", ()),
```
★**main 本机实跑 `grep -c check_sw_ref_reachability_v2 state/gate_check.py` ⇒ ★**0**★ ⇒ ★**v2 完全没挂链** ★
★**★ISS-332 (★已签收 verified★) 的 verify_result 逐字写着**: ★★「怎么挂: `state/gate_check.py` 的 `EXTRA_GATES` 第 3 位 (L222-223) · 路径换成 v2 · `args` 传 `()` 裸跑 ⇒ ★**只改 1 行**★」★★ ⇒ ★**main 当时就知道只改 1 行, 但这一行至今没改** ★
★**★v1 vs v2 的差别 (★main 本机实跑 grep★)**: ★
```bash
grep -c "RT-5\|RT-6\|RT-7\|RT-8" SW/tools/check_sw_ref_reachability.py       # ⇒ 0
grep -c "RT-5\|RT-6\|RT-7\|RT-8" SW/tools/check_sw_ref_reachability_v2.py    # ⇒ 2
```
★★**⇒ v1 里那 4 条洗白面反向用例 (★ISS-327 实测出「把真隐患改个形状就骗过闸」★) 至今没有对应用例 ★★**

### ★★③ 第三道病闸: v2 自己的 selftest 现在是红的 (★main 本机实跑·★真退出码★) ★★

★**main 本机实跑 (★不用管道·直接看真 rc★)**:
```bash
python3 SW/tools/check_sw_ref_reachability_v2.py --selftest; echo "rc=$?"
```
★**⇒ 真 rc=1 · 末行逐字: `反向用例: 0/7 通过` + `❌ 有用例没抓到 ⇒ 判据可能没被真读`★**
★**★根因 (★main 本机实读 v2 自己的输出·不是猜★)★**: ★
```
【R3 现状基线】 `DESIGNATOR_MISSING` 实测 = 4 条 · 允许上限 = 3 条
★★超基线★★ SW_MD5  (SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md:453)  出现 4 次
   理由: ★不在建闸日基线里 ⇒ 这是新增的真隐患★
```
★**⇒ 第 4 条真患 = `SW_MD5`, 出现在 `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md:81` 与 `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md:453`** ★
★**★main 本机实读 `SW/tools/check_sw_ref_reachability_v2_selftest.py --selftest` ⇒ 真 rc=1 · `10/15 通过` · 差异逐字★**:
> `❌ G1-4 逐 token 分类/规则/理由 与真件闸【逐字相同】 · ★差异 2 条: [('SW_MD5', 'DESIGNATOR_MISSING', 'C14', '★命中了形状豁免规则 C13 (`SW_` 开头 …) 但【不在 EXEMPT_LEDGER 登记台账里】⇒ 登记制不许豁免 ⇒ 判真隐患 (ISS-332 收紧)★'), ('SW_MD5', 'DOC_INTERNAL', 'C13', '`SW_` 开头 ⇒ SW 侧文档 / 锚点 / 环境变量键 / 条目编号')]`
> `❌ G0 ★沙盒基树在 v2 下仍绿 (★证明下面 ② ③ 组的红不是基树带来的★) · 基树 rc=1 (★期望 0★)`

★**⇒ ★★**基线漂移 = 一个第三方页 (★ISS-372 那一趟的页★) 引入了一个新的形状像位号的 token `SW_MD5`, 把 `DESIGNATOR_MISSING` 从 3 顶到 4 ⇒ 超过建闸日冻结的上限 3 ⇒ 差值型自测全灭 (★ISS-388 诊断页 §2 写的那种「账漂了」而不是「闸坏了」★)** ★★**

### ★★④ 闸 1 的环境耦合 (★main 本机实跑·★两组对照逐字★) ★★

```bash
python3 SW/tools/check_debug_pin_order_contract.py --selftest; echo "rc=$?"
TMPDIR="$PWD/tmp" python3 SW/tools/check_debug_pin_order_contract.py --selftest; echo "rc=$?"
```
★**⇒ 默认 TMPDIR: 真 rc=1 · 末行 `SELFTEST FAILED` · `selftest 10/11 PASS`**
★**⇒ `TMPDIR=$PWD/tmp`: 真 rc=0 · 末行 `ALL TESTS PASS` · `selftest 11/11 PASS`**
★★**⇒ 这道闸【一直绿】, 但只在 `TMPDIR=$PWD/tmp` 这个从没写进任何契约文件的约定下绿** ★★**

### ★★⑤ ISS-388 那道元闸自己的 ROSTER 只有 13 道 (★main 本机实跑逐个 diff★) ★★

★**`SW/tools/check_sw_gate_health.py` 的 `ROSTER` 硬编码 13 条 (★main 实读★)**; ★**盘上 `SW/**/check_*.py` = 30 道 ⇒ 17 道不在册** ★
★**其中 ★**15 道★是带 `__main__`/`argparse` 的独立闸 (★main 逐个 grep 确认·不是靠文件名猜★)★, 例如: ★
`check_brightness_biosafety.py` · `check_iss250_rknn_target_gate.py` · `check_iss355_convert_route.py` · `check_load_switch_selection.py` · `check_onepass_sw_release.py` · `check_rk3572_target_caliber.py` · `check_rk3572_vccio_domain.py` · `check_rknn_target_compat.py` · `check_shutdown_semantics.py` · `check_sw09_patch_dryrun.py` · `check_sw_zero_copper_grade_consistency.py` · `check_timing_review_adc_sync.py` · `check_sw_ref_reachability_v2_selftest.py` · `check_demo_panel_spec_r6_chainjudge_selftest.py` · `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` ★
★**★⇒ 元闸自己的盲区 17 道, 比它查出来的病还多** ★★

---

## ★★二 · 本单要交 4 件 (★就这 4 件·不要顺手多跑别的★) ★★

### ★★① 新建真相页: `SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md` (★新建★) ★★

★**必须包含 (★每条都要有出处行号 + main 本机实跑命令★)**: ★
★**(a)** ★★**三本账的差集表**★★: ★★盘上 30 道 SW 闸 × ①链里跑的 6 道 × ②ISS-388 元闸 ROSTER 的 13 道 × ③**三者的差集逐条列出**★★ ⇒ ★★**「盘上有 / 链里不跑」24 条 + 「元闸看不见」17 条**★★ ★
★**(b)** ★★**每一条差集要分类 + 给后果**, 至少这四类: ★★【A 类·板那一趟会因它变红而必须跑】/【B 类·板那一趟会因它变红而今天不跑 ⇒ 那天是个洞】/【C 类·与板无关但会因基线漂移变红】/【D 类·辅助/自测脚本, 本来就不该进链】★★ ⇒ ★**B 类才是真病灶, 要逐条点名** ★
★**(c)** ★★**第三道病闸 (v2) 的基线差集逐条算清**: ★**`SW_MD5` 的 4 次出现分别在哪个文件哪一行** (★main 已实测 2 个: `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md:81` 与 `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md:453`★) + ★**它到底是【真隐患】还是【形状像位号的锚点台账名】** + ★**两种口径各自的代价 (★不许你自己拍, 两条路都摆出来★)** ★
★**(d)** ★★**闸 1 环境耦合的对照实验 (★两组 rc + 逐字末行★)** ★
★**(e)** ★★**v1 vs v2 的逐条差异清单 (★带行号★)** + ★**「只改 1 行就能切链」那个位置 (L222-223) 的逐字写法** ⇒ ★**但 §三 的边界写着: 切链是 main 的动作, 你只出写法** ★
★**(f)** ★★**每段都带证据等级 (★`[实测]`=本机跑出来的 / `[推算]` / `[0数据]`★)** ★
★**(g)** ★**机器块** (★`--emit` 可解析★): ★`sw_gates_on_disk` / `sw_gates_in_chain` / `sw_gates_in_health_roster` / `coverage` / `blind_spot_classes` / `baseline_drift` 六个键 ★

### ★★② 新建机器闸: `SW/tools/check_sw_gate_chain_coverage.py` (★新建★) ★★

★**判据 (★fail-closed · 每条都有反向用例★)**: ★
| 键 | 判据 |
|---|---|
| ★**C1** ★ | ★★**盘上 SW 域闸集合 vs 三本账的差集必须可复算** ⇒ ★**每条差集都要能指名到文件路径** ★★ |
| ★**C2** ★ | ★★**「链里跑的那道 SW 位号可达性闸」必须与 ISS-332 签收的收紧版一致** ⇒ ★**不一致 ⇒ 红并点名「链上跑的是 v1 / 收紧版 v2 未挂链」** ★★ |
| ★**C3** ★ | ★★**SW 域每道闸的 `--selftest` 真 rc 必须 = 0** ⇒ ★**任一道非 0 ⇒ 红并点名是哪一道 + 它的原文末行 (★照抄 ISS-388 元闸 H0 的形状★)** ★★ |
| ★**C4** ★ | ★★**环境无关**: 每道被扫的闸在两个不同深度的 TMPDIR 下各跑一次 selftest ⇒ 两次 rc + 逐字输出必须相同 ⇒ 不同 ⇒ 红并点名 ★★ |
| ★**C5** ★ | ★★**元闸自身的 ROSTER 覆盖率**: ROSTER 里每道都要在盘上; ★**盘上独立闸数 - ROSTER 数 ⇒ 差集必须被登记 (登记了才算已知盲区, 没登记 ⇒ 红)** ★★ |
| ★**C6** ★ | ★**零扰动 + 证据分级 + 零挂链 + 零挂起措辞 + 判据/事实分开** ★ |
★**★反向用例 ≥10 条**, 其中 ★**≥3 条专打 C3 (把某道闸改成红 ⇒ 必须红 + 点名)★**、★**≥2 条专打 C2 (把链上那行换成 v2 ⇒ 差集必须变)★**、★**≥2 条专打 C5 (把 ROSTER 删一条 ⇒ 必须红)★** ★
★**★必须支持 `--selftest` 入口 + 末行逐字 `ALL TESTS PASS` + 真 rc=0** ★
★**★★零挂链 ★★: `grep -c check_sw_gate_chain_coverage state/gate_check.py` ⇒ **0** ★★**

### ★★③ 交卷页: `HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md` (★新建★) ★★

★**B1~B6 六段齐全, 六个 `##` 标题必须命中 `state/gate_check.py` 的 `REQUIRED_BLOCKS` 关键词 (★main 本机实读 L47~L54★)**: ★
| 段 | 标题必须含 |
|---|---|
| B1 | `结论` / `结论摘要` / `一句话` |
| B2 | `验收标准自评` / `自评` / `验收标准` |
| B3 | `证据分级` / `证据等级` / `证据` |
| B4 | `接口取值` / `接口声明` / `interface_claims` / `接口请求` |
| B5 | `阻塞` / `卡点` / `未决` / `待办` |
| B6 | `复现` / `复现命令` / `自证` |
★**★不许留「(施工中)」占位符 ★★**

### ★★④ 分片: `state/fragments/sw.yaml` ★★

★**必须走** `python3 state/frag_write.py --agent sw-lead` ★★(★禁止 `open(p,"w")`★) ★
★**≥4 产出物 + ≥6 interface_claims + ≥6 needs_from (★全部 to=main·★不许自签★)** ★

---

## ★★三 · 边界 (★违反就是不合格★) ★★

| # | 边界 |
|---|---|
| ★**1** ★ | ★**零写板**: `HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` · mtime 必须还是 `2026-11-06 07:07:17.362193413` · size 必须还是 `4940213` |
| ★**2** ★ | ★**零落表**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / 原理图真源 一个字节不许动 |
| ★**3** ★ | ★★**零改既有闸的判据/阈值** ★★: ★**`SW/tools/check_sw_ref_reachability.py` / `..._v2.py` / `..._v2_selftest.py` / `check_debug_pin_order_contract.py` / `check_sw_gate_health.py` / `check_sw_board_md5_rebase_readiness.py` 一个字节都不许动** ★★(★它们是已签收件★)★ |
| ★**4** ★ | ★**零改 `state/gate_check.py`** (★挂链/切闸是 main 的机制地界★) ⇒ ★**你只交「怎么切」的逐字写法 + 位置 (L222-223) + 切完之后的预期读数** ★ |
| ★**5** ★ | ★**零改既有页面正文** (★`SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md` / `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` / `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` / `SW/SW_MD5_BASELINE_LEDGER.md` 全都不许动★) ⇒ ★**只登记差集, 不代落** ★ |
| ★**6** ★ | ★**零改 `state/issue_log.yaml`** (★不自签台账★) |
| ★**7** ★ | ★**零挂链**: `grep -c check_sw_gate_chain_coverage state/gate_check.py` ⇒ **0** |
| ★**8** ★ | ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购** ⇒ ★**老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ |
| ★**9** ★ | ★**不代拍**: ★**切不切链 / 挂不挂新闸 / `SW_MD5` 算不算真隐患 / 要不要立「基线必须先绿」通则 —— 四条全是 main 的地界, 你只摆代价** ★ |
| ★**10** ★ | ★**不写别人的分片** (★只写 `state/fragments/sw.yaml`★) |
| ★**11** ★ | ★**沙盒只落** `tmp/iss392_sbx/` + `logs/iss392/` ★ |
| ★**12** ★ | ★**一次 write ≤ 3000 字 ⇒ 先 write 骨架 (章节标题 + 每节 1~2 行), 再 edit 逐块补** (★★连挂两趟都是死在超长 write 上★★) ★ |

---

## ★★四 · 交卷前必跑 (★原样输出贴进交卷页 B6 · 期望值写在后面★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-392_sw_gate_chain_coverage.md   # rc 必须 0
python3 SW/tools/check_sw_gate_chain_coverage.py                    # rc 必须 0 · ★本闸裸跑全绿★
python3 SW/tools/check_sw_gate_chain_coverage.py --selftest          # rc 必须 0 · 末行 ALL TESTS PASS
python3 SW/tools/check_sw_ref_reachability_v2.py --selftest          # rc=1 ★★基线漂移·本单不改它★ ⇒ 交卷页要写明这是【已知基线红】不是本单引入
python3 SW/tools/check_debug_pin_order_contract.py --selftest        # rc=1 ★★默认 TMPDIR·本单不改它★★ ⇒ 同上
TMPDIR="$PWD/tmp" python3 SW/tools/check_debug_pin_order_contract.py --selftest   # rc 必须 0 ★对照相★
python3 state/merge.py                                              # rc 必须 0
python3 state/gate_check.py                                         # rc 必须 0 · Q1 18/18
python3 state/issue_check.py                                        # rc=1 ★★既有逾期老账·本单零新增★★
md5sum HW/PCB/demo_mainboard.kicad_pcb                              # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                     # 必须 2026-11-06 07:07:17.362193413 4940213
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv        # 必须 6aee500e… / 9174309d… / 5b999399…
grep -c "check_sw_gate_chain_coverage" state/gate_check.py           # 必须 0
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md"   # 必须 0
grep -c "iss392" state/fragments/sw.yaml                            # 必须 >= 1
find tmp/iss392_sbx -type l | wc -l                                 # 必须 0
```

★额外纪律: ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★ · ★**不许外发任何邮件/询价/问询/采购 ⇒ 缺口一律自己网上查 + 标证据等级 + 写降级方案** ★ · ★**交卷前跑 `python3 state/merge.py` (rc=0) && `python3 state/gate_check.py` 并把输出贴进回复** ★

---

## ★★五 · 一句话 (★本单到底在回答什么★) ★★

★**「板只改一次」那一趟真会动板 (md5 会变 · 位号会改) ⇒ 到那天 SW 侧到底有几道护栏会真的响 ⇒ 现在能不能回答 ⇒ 以及第三道病闸 (v2) 的红到底是不是「闸坏了」还是「账漂了」** ★
