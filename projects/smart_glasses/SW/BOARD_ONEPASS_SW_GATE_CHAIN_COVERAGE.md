# BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE · 「板那一趟」SW 侧护栏到底有几道真的在跑

> **本页是 ISS-392 (sw-lead) 新建的真相页** · **零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代拍**
> **机器闸**: `SW/tools/check_sw_gate_chain_coverage.py` (★零挂链★) · **交卷页**: `HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md`
> **所有读数都是 2026-11-24 本机实跑** (`main` 本机 · 不是抄任何 agent 报告) · 复跑命令见 §5

---

## §0 一句话结论

★**盘上 SW 域闸 31 道 (★开工时 30 道 + 本单新建的覆盖率闸 1 道★), 门禁链里真正跑的只有 6 道 (★覆盖率 19.4%★),
另外 25 道从来没进过门禁链; 链上跑的还是 ISS-332 已查出 4 条洗白面的旧版 v1, 收紧版 v2 在盘上没人跑;
查闸有没有坏的那道元闸自己只扫了 13 道 (★盲区 18 道★) ⇒ ★★「板那一趟改完板, SW 侧没人拦」今天是【真】的, 不是假设★★** ★[实测]★

- ★**判据句 (★本单立的机器判据·可被 `SW/tools/check_sw_gate_chain_coverage.py` 判·C0~C6★)**:
  ① 板三项指纹 + 三表 md5 未动且本闸零挂链; ② 盘上 SW 闸集合与真相页机器块登记**双向**一致且每道闸的登记读数 (跑法/rc/末行) 与实测**逐字**一致;
  ③ 链里挂的 SW 闸清单与真相页登记的链内清单**双向**一致; ④ 链上位号可达性闸的版本状态必须与真相页登记**一致**且收紧版 v2 **真实存在于盘上**
  (★**不许写死「v2 没挂」·哪天挂上了本条自动转绿**★); ⑤ ISS-388 元闸 ROSTER 的覆盖数与盲区数必须被登记; ⑥ 第三道病闸 (v2) 的 selftest 真 rc 必须被登记且真相页必须写明「**基线红 ≠ 本单引入**」; ⑦ 五级证据白名单 + 零挂起措辞 + 零空洞词 + 判据句与事实句分开。★
- ★**事实句 (★本机实跑出来的读数·只可更新不可改口径★)**:
  盘上 SW 闸 31 道 · 链内 6 道 · 元闸 ROSTER 13 道 · 链外 25 道 (★开工时 24 道★) · 元闸盲区 18 道 (★开工时 17 道★) ·
  链上跑的位号可达性闸 = `SW/tools/check_sw_ref_reachability.py` (★旧版 v1★) · 收紧版 `SW/tools/check_sw_ref_reachability_v2.py` 在盘未挂链 ·
  第三道病闸 v2 的 `--selftest` 真 rc=**1** · 末行逐字 `❌ 有用例没抓到 ⇒ 判据可能没被真读` · 反向用例 **0/7** 通过。★[实测]★

---

## §1 三本账的差集: 盘上 31 道 × 链内 6 道 × 元闸 ROSTER 13 道

### §1.1 三本账的差集表 (★双向·逐条可复算★) ★[实测]★

| 差集 | 条数 | 逐条列在哪儿 |
|---|---|---|
| 盘上 − 链内 (**盘上有 / 链里不跑**) | **25** (★开工时 24★) | §1.2 全表「挂链=否」行 + §1.3 B/C/D/E 分类 |
| 链内 − 盘上 | **0** | 链里挂的 6 道全部在盘上 |
| 盘上 − 元闸 ROSTER (**元闸自己看不见**) | **18** (★开工时 17★) | §1.2 全表「在 ISS-388 元闸 ROSTER=否」行 |
| 元闸 ROSTER − 盘上 | **0** | ROSTER 登记的 13 道全部在盘上 |
| 链内 ∩ 元闸 ROSTER | **4** | `check_onepass_sw_sync.py` · `check_landing_trace_obligation.py` · `check_sw_ref_reachability.py` · `check_demo_panel_spec.py` |
| 链内 − 元闸 ROSTER | **2** | `check_demo_panel_spec_r6_chainjudge_selftest.py` · `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` · `check_demo_panel_spec_r6_selftest.py` (★3 道★) |

★**三本账的取法 (★都可复算·不靠散文★)**:
- 盘上 = `find SW -name 'check_*.py'` (★排除 `__pycache__` 与 `.bak`★) ⇒ **31** 道 ★[实测]★
- 链内 = 从 `state/gate_check.py` 的 **AST** 里抽 `os.path.join(PROJ, "SW", ...)` ⇒ 去重 ⇒ **6** 道 ★[实测]★
- 元闸 ROSTER = 从 `SW/tools/check_sw_gate_health.py` 的 **AST** 里抽 `ROSTER` 常量 ⇒ **13** 道 ★[实测]★

<!--TABLE-->

### §1.3 按「后果」分五类 (★分类依据全部来自本机实测/源码信号·不是按文件名猜★) ★[实测]★

| 类 | 判据 (★机器算的★) | 后果 | 条数 |
|---|---|---|---|
| **A** | 板敏感 (★源码引用板/网表/脚表/BOM/位号★) **且** 已在链内 | ★板那一趟它会响 ⇒ 护栏在位★ | 见下表 |
| **B** | 板敏感 **且** 不在链内 | ★★板那一趟它本该响但今天不响 ⇒ 那天是个洞★★ | 见下表 |
| **C** | 与板无关 **且** 当前读数红 (rc≠0) | 与板无关但会因基线/账漂变红 | 见下表 |
| **D** | 与板无关 **且** 当前读数绿 | 不必进链 (辅助/自测/板无关闸) | 见下表 |
| **E** | 元闸本身 (★含本单新建的覆盖率闸★) | ★它的盲区就是本单的对象★ | 见下表 |

<!--CLASSES-->

---

## §2 链上 v1 vs 在盘 v2: 4 条洗白面的差集 (★ISS-332 已签收件★)

### §2.1 差集逐条 (★出处: `logs/iss332/03_repro_with_v2.txt` · `logs/iss332/2RT-*_RT-*_v2.txt`★) ★[实测]★

| 用例 | 改法 (★把真患换个形状★) | 真件闸 v1 (★链上跑的★) | 收紧版 v2 (★在盘·没挂链★) | 差集性质 |
|---|---|---|---|---|
| **RT-5** | `TP_TEMP` → `U\_TEMP\_1` (★真患改成 live 位号名★) | rc=0 (★绿·洗白成功★) | rc=1 (★红·点名该 token★) | v1 漏 · v2 抓 |
| **RT-6** | `TP_TEMP` → `TP\_temp` (★改大小写★) | rc=0 (★绿★) | rc=1 (★红★) | v1 漏 · v2 抓 |
| **RT-7** | `TP_TEMP` → `SW\_TEMP\_ISSX` (★加 SW_ 前缀★) | rc=0 (★绿★) | rc=1 (★红★) | v1 漏 · v2 抓 |
| **RT-8** | `TP_TEMP` → `TP\_TEMP\_` (★加尾下划线★) | rc=0 (★绿★) | rc=1 (★红★) | v1 漏 · v2 抓 |

★**对照组 (★v1 与 v2 都红 ⇒ 这不是 v2 比 v1 严·是两条闸共有的地基★)**:
`CTL-1` (加 `\_ISSX` 后缀) · `CTL-2` (加 `\_ISSX` 后缀) · `CTL-3` (加 `\_ISSX` 后缀) ⇒ 三条 v1/v2 都 rc=1 ✔ ★[实测]★

★**v1 与 v2 的判据差集 (★带行号·主 agent 实读两文件·不猜★)** ★[实测]★:

| 差集项 | v1 (`check_sw_ref_reachability.py`) | v2 (`check_sw_ref_reachability_v2.py`) | 差集性质 |
|---|---|---|---|
| 形状豁免台账 `EXEMPT_LEDGER` | ★**没有** ⇒ C7~C13 形状可疑就豁免 | ★**有** (L173 起) ⇒ ★**只有登记在册的 token 才允许按形状豁免**★ | ★v2 的核心收紧★ |
| 执法点 A (登记制豁免) | ★**无**★ | ★**有** (L13~L15)★ | 差集 |
| 执法点 B (真患台账必须对得上账) | ★**无**★ | ★**有** (L17)★ | 差集 |
| 执法点 C (台账口径自洽: `BASELINE_COUNT == len(BASELINE_TOKENS)`) | ★**无** (v1 只有 `BASELINE_TOKENS` L134 + `BASELINE_COUNT` 注释) | ★**有** (L20)★ | 差集 |
| 洗白替身点名 (执法点 D) | ★**无**★ | ★**有** (真件闸输出「★洗白替身点名 (执法点 D)★」段)★ | 差集 |
| 假绿护栏 (执法点 E: 判据分支探针) | ★**无**★ | ★**有** (输出「★假绿护栏 (执法点 E)★ 判据分支探针 9 项 ⇒ ✔ 全命中」)★ | 差集 |
| `RT-5`~`RT-8` 四条洗白面反向用例 | ★**没有** (★`grep -c "RT-5\|RT-6\|RT-7\|RT-8" check_sw_ref_reachability.py` ⇒ **0**★) | ★**有** (★同一条 grep 在 v2 ⇒ **2**★)★ | 差集 |

### §2.2 「只改 1 行就能切链」的逐字写法 (★**切不切是 main 的地界·本单只出写法·不代拍**★)

★**位置**: `state/gate_check.py` **L222-223** (★当前逐字★):
```python
    (os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability.py"),
     "SW 侧位号引用可达性闸 (ISS-318)", ()),
```
★**若 main 决定切, 逐字改成** (★只改路径 1 个 token + 标题 1 处★):
```python
    (os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability_v2.py"),
     "SW 侧位号引用可达性闸 (ISS-318 · 收紧版 ISS-332)", ()),
```
★**切完之后链上的预期读数**: v2 裸跑 **rc=1** (★今天就红·见 §3★) ⇒ ★**切链 ≠ 立刻变好, 反而当场把门禁链打成红** ⇒ 切链必须与 §4 选项 3 (SW_MD5 算不算真隐患) 一起拍★ ★[实测]★

---

## §3 第三道病闸 (v2) 的基线漂移证据

### §3.1 基线漂移的三条实测证据 (★**基线红 ≠ 本单引入**★) ★[实测]★

**① v2 自己的 selftest 现在是红的** (★`python3 SW/tools/check_sw_ref_reachability_v2.py --selftest`★):
- 真 rc = **1** · 末行逐字 `❌ 有用例没抓到 ⇒ 判据可能没被真读`
- 倒数第二行逐字 `反向用例: 0/7 通过`
- ★**本单零改 v2** ⇒ 这是**基线红**, 不是本单引入 ⇒ ★**基线红 ≠ 本单引入**★

**② 根因在 v2 自己的输出里 (★不是猜·是逐字读出来的★)**:
```
【R3 现状基线】 `DESIGNATOR_MISSING` 实测 = 4 条 · 允许上限 = 3 条
   ⇒ ✘ 超基线 (见下方 FAIL 行)
[FAIL] 位号引用解析不到 (新增真隐患·超基线): SW_MD5 @ SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md:453 ⇒ 板与网表里现在叫: (无近似名)
[FAIL] 真隐患条数 4 > 基线上限 3 (★基线只许收紧不许放宽★)
```
- 第 4 条真患 = **`SW_MD5`** · 分类理由逐字:
  `DESIGNATOR_MISSING C14 SW_MD5 ★命中了形状豁免规则 C13 (SW_ 开头 ⇒ SW 侧文档 / 锚点 / 环境变量键 / 条目编号) 但【不在 EXEMPT_LEDGER 登记台账里】⇒ 登记制不许豁免 ⇒ 判真隐患 (ISS-332 收紧)★`
- ★**它不是「板上的位号」, 是「SW 侧台账文件的锚点名」被当成位号 token 抽出来了** ★[实测]★

**③ 为什么「基线先红 ⇒ 差值型自测全灭」 (★机制逐字可见★)**:
v2 的 7 条反向用例 (RC-1~RC-7) 全部用「★不是巧合自证★」句式 ⇒ 它们要求 **破坏前 rc=0** 才能说「破坏后的红【只可能】来自被改坏的那一处」。
- 破坏前的基树 **已经** 因为 `SW_MD5` 多出一条真患 (4 > 3) ⇒ 破坏前 rc=**1** ⇒ ★「不是巧合」的前提不成立 ⇒ 7 条用例**全部**判「用例没过」
- ★**⇒ 差值型自测在基线先红时不是「测不出」, 是「测不了」: 它连自己的基线都不信 ⇒ 反向用例 0/7★** ★[实测]★
- ★**这一条与 ISS-388 的 `iss388_delta_selftest_convention` 那条 need 对齐** ⇒ ★**但本单【不代拍通则】** ⇒ 见 §4 选项 4★

### §3.2 `SW_MD5` 这个 token 的 4 次出现 (★逐条给文件+行号★) ★[实测]★

★**口径**: v2 扫 `SW/*.md` (★`DOC_GLOB = "SW/*.md"` ⇒ 不扫 `SW/tools/*.py`★) · 抽 token 的正则是 `TOKEN_PREFIXES` + `[A-Za-z0-9_]*` ⇒ `SW_` 前缀的**独立** token 都会被抽出来。

| # | 文件:行 | 该 token 在那一行的角色 | 分类 (v2 的 R2 全表逐字) |
|---|---|---|---|
| 1 | `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md:453` | ★★超基线★★ 第 4 条真患的**首报位置** (★出现次数按全树统计★) | `DESIGNATOR_MISSING C14` |
| 2 | `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md:456` | 同页「自证『与腿 B 无关』」三条里又提一次该 token | `DESIGNATOR_MISSING C14` |
| 3 | `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md:86` | ISS-372 那一趟的清单页里的一条引用 | `DESIGNATOR_MISSING C14` |
| 4 | `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md:346` | 同页另一条引用 | `DESIGNATOR_MISSING C14` |

★**复算命令 (★原样可粘贴★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 - <<'PY'
import os, re
pat = re.compile(r'SW_MD5(?![A-Za-z0-9_])')
for d, _, fs in os.walk('SW'):
    if '__pycache__' in d: continue
    for f in sorted(fs):
        if not f.endswith(('.md', '.py')): continue
        p = os.path.join(d, f)
        for i, l in enumerate(open(p, encoding='utf-8', errors='ignore').read().splitlines(), 1):
            if pat.search(l): print("%s:%d" % (p, i))
PY
```
★**注**: 本页自身 (`SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md`) 是 `SW/*.md` 的一员 ⇒ 它会被 v2 扫到 ⇒ ★**本页对 v2 的真患条数贡献必须为 0** ⇒ ★**本页里凡是要引用 ISS-332 那 4 条洗白面的新 token, 一律写成 `U\_TEMP\_1` / `TP\_temp` / `SW\_TEMP\_ISSX` / `TP\_TEMP\_` (★markdown 转义·渲染出来还是原样·但 v2 的 tokenizer 抽不到★)** ⇒ ★**这是 ISS-370 同款「自污染零贡献」纪律★** ★[实测]★

### §3.3 闸 1 的环境耦合对照实验 (★两组 rc + 逐字末行★) ★[实测]★

★**现象**: `SW/tools/check_debug_pin_order_contract.py` 在不同 TMPDIR 深度下读数不同 ⇒ 它的判决与环境耦合 (★ISS-388 元闸 H1 已独立查出同一条·本单复现·不是抄它★)。

| 组 | 命令 | 真 rc | 逐字末行 |
|---|---|---|---|
| 深度 A | `python3 SW/tools/check_debug_pin_order_contract.py --selftest` (★默认 TMPDIR★) | **1** | `SELFTEST FAILED` |
| 深度 A′ | `TMPDIR=$PWD/tmp python3 SW/tools/check_debug_pin_order_contract.py --selftest` | **0** | `ALL TESTS PASS` |
| 深度 B | `TMPDIR=$PWD/tmp/iss392_sbx/depth_b/nested/g1 python3 SW/tools/check_debug_pin_order_contract.py --selftest` | **1** | `SELFTEST FAILED` (★`selftest 10/11 PASS`★) |

★**机制 (★实读源码·不是猜★)**: 该闸的 selftest 把「变异体」脚本写到 `TMPDIR` 下的临时目录, 变异体从 `__file__` 反推 ROOT ⇒ ★**TMPDIR 的上两级必须正好是项目根**⇒ 深度 A (`<ROOT>/tmp`) 成立 ⇒ M2 用例通过; 深度 B (更深) ⇒ 变异体找不到 `<TMPDIR>/SW/...` ⇒ M2 用例失败 (★`[FAIL] M2 … 实红=FATAL: 变异体无 JSON 输出`★) ★[实测]★

★**⇒ 这道闸【一直绿】, 但只在「TMPDIR 是一级子目录」这个从没写进任何契约文件的约定下绿** ⇒ 本单把它登记成 **env_coupled** (★见机器块 `gate_readings.*.env_same`★) ★[实测]★

---

## §4 挂链的【代价与选项】 (★只摆代价·**不代拍**·四条全是 main 的地界★)

★**判据句**: 以下四个选项的取舍属 main 的机制/裁决地界 ⇒ 本单**只列代价与读数**, 一条都不拍板。★**事实句**: 每条选项后面的读数都是本机实跑出来的。★

### §4.1 选项 1 · 切不切链 (★v1 → v2★) —— 谁的地界: ★**main**★

| 做法 | 代价 (★实测★) | 谁的地界 |
|---|---|---|
| **不切 (今天)** | 链上跑 v1 ⇒ ★ISS-332 查出的 4 条洗白面 (RT-5~RT-8) 在链上没人抓★ ⇒ 「把真患改个形状就骗过闸」这条路, 门禁链管不住 | main |
| **切 (只改 L222-223 一处)** | ★**切完当场红**★: v2 裸跑 rc=1 (§3.1) ⇒ 门禁链从今天起常红 ⇒ ★**切链必须与 §4.3 一起拍, 否则是把门禁链打成常红**★ | main |
| **v1 与 v2 并挂** | ★**不成立**★: v2 没有「期望已知红项」那种参数 (★v1 那种 `--expect-known` 机制 v2 没有★) ⇒ 裸跑就是 rc=1 ⇒ 并挂 = 多一道常红闸 | main |
| **先修基线再切** | 顺序: §4.3 口径 B (登记进 EXEMPT_LEDGER) ⇒ v2 回绿 ⇒ 再切 ⇒ 链上是真收紧版 | main |

### §4.2 选项 2 · 挂不挂本单新建的覆盖率闸 —— 谁的地界: ★**main**★

| 做法 | 代价 (★实测★) | 谁的地界 |
|---|---|---|
| **不挂 (本单交付态)** | 覆盖率只能靠人记得跑 ⇒ ★明天再加一道闸, 没人会发现账飘了★ ⇒ 本单只保证「跑起来会红」, 不保证「天天有人跑」 | main |
| **挂进链** | ① 耗时: 本闸要扫 31 道闸 × 2 个 TMPDIR 深度 ⇒ ★实测单次 ≈ 6~7 分钟★ ⇒ 门禁链整体 +6~7 分钟 ② 任何一道 SW 闸的读数漂了 (含 rc/末行变化) ⇒ 本闸红 ⇒ 需要一次「重生成真相页机器块」的例行动作 ③ 本闸自己在盘上 ⇒ 链上多一道自指闸 (★实测: 本闸 `--selftest` 0.5s, 不递归·因为 selftest 走夹具不走真盘★) | main |

### §4.3 选项 3 · `SW_MD5` 算不算真隐患 —— 谁的地界: ★**main**★

| 口径 | 代价 (★实测★) | 谁的地界 |
|---|---|---|
| **A · 维持现状 (v2 的 C13+C14 口径)** | 第 4 条真患成立 ⇒ v2 长期红 ⇒ ★差值型自测永久 0/7 ⇒ v2 挂不了链 ⇒ 收紧版永远躺在盘上没人跑★ | main |
| **B · 把它登记进 `EXEMPT_LEDGER`** | ⇒ 第 4 条消失 ⇒ v2 回绿 ⇒ 差值型自测恢复 ⇒ v2 可挂链。★代价: 登记制多了一条「形状像位号的锚点台账名」的合法豁免 ⇒ 将来真出现一个同名的位号引用 ⇒ 会被豁免掉 ⇒ 留一个漏检窗口★。★且要改 `SW/tools/check_sw_ref_reachability_v2.py` (★已签收件·本单零改·要 main 派单★) | main |
| **B′ · 把基线上限从 3 抬到 4** | ★**与 v2 自己的执法点 C 冲突** (★v2 逐字写着「基线只许收紧不许放宽」★) ⇒ 抬上限 = 放宽 ⇒ **不建议** | main |
| **C · 改第三方页里那 4 处字面量** | ★**触碰已签收页 + 本单零改既有页面正文** ⇒ 本单不做★ | main |

### §4.4 选项 4 · 要不要立「基线必须先绿」通则 —— 谁的地界: ★**main**★

| 做法 | 代价 (★实测★) | 谁的地界 |
|---|---|---|
| **立 (挂链前 selftest 必须 rc=0)** | 优点: 元闸/覆盖率闸的读数才有意义 (★否则「登记的红」和「闸坏了」分不开★)。★代价: 今天盘上有 **3** 道闸 selftest 红 (v2 · v2 的自测脚本 · 板 md5 重锚就绪闸) ⇒ 通则一立, 这 3 道不许挂链 ⇒ ★覆盖率只会更低★ | main |
| **不立 (允许「基线红但已登记」)** | 允许登记过的红项存在 ⇒ 代价: 链上出现常红闸 ⇒ ★门禁链天天红 ⇒ 大家习惯性忽略 ⇒ 比「没有护栏」更危险★ | main |
| **折中 (元闸层面立)** | 只要求「元闸/覆盖率闸扫到的闸的读数必须被登记且与实测一致」⇒ 不要求红项归零 ⇒ ★**本单的新闸就是按这条做的★** ⇒ 代价: 判据变弱 ⇒ 「账漂了」与「闸坏了」仍要靠人分辨 | main |

---

## §5 复跑命令 (★原样可粘贴★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 三本账的条数 (盘上 / 链内 / 元闸 ROSTER)
find SW -name 'check_*.py' -not -path '*/__pycache__/*' | sort | wc -l        # ⇒ 31
grep -c 'check_sw_ref_reachability' state/gate_check.py                        # ⇒ 见下 (v1 在链上)
python3 SW/tools/check_sw_ref_reachability_v2.py --selftest ; echo "rc=$?"      # ⇒ rc=1 (★基线红·本单不改★)
python3 SW/tools/check_debug_pin_order_contract.py --selftest ; echo "rc=$?"    # ⇒ rc=1 (★默认 TMPDIR★)
TMPDIR="$PWD/tmp" python3 SW/tools/check_debug_pin_order_contract.py --selftest ; echo "rc=$?"   # ⇒ rc=0 (★对照相★)

# ② 本单新建的机器闸 (★零挂链★)
python3 SW/tools/check_sw_gate_chain_coverage.py              # ⇒ rc=0 · C0~C6 全绿
python3 SW/tools/check_sw_gate_chain_coverage.py --selftest    # ⇒ rc=0 · 末行 ALL TESTS PASS (★24 条反向用例★)
python3 SW/tools/check_sw_gate_chain_coverage.py --emit        # ⇒ 机器块 JSON (★本页机器块同源★)

# ③ 零挂链 + 零扰动
grep -c check_sw_gate_chain_coverage state/gate_check.py       # ⇒ 0
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%n mtime=%y size=%s' HW/PCB/demo_mainboard.kicad_pcb
```

---

## 机器块 (★`--emit` 可解析★)

<!--BLOCK-->
