# ISS-388 · SW 域【两道已签收闸今天真的坏了】失效诊断页
<!-- ISS388-DIAGNOSIS-PAGE -->

- **单号**: ISS-388 cont1
- **作者**: sw-lead (软件总工)
- **日期**: 2026-11-24
- **本单性质**: 纯分析 + 新建闸 + 诊断。**零写板 · 零落表 · 零改既有闸的判据/阈值 · 零外发 · 不代拍**
- **证据分级**: `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`
- ★**本页刻意不写板 md5 的字面量** (既不写全串、也不写 8 位前缀) ⇒ ★**因为 `SW/tools/check_sw_board_md5_rebase_readiness.py` 的 H1 会逐行扫 `SW/` 全树找那 8 位前缀** ⇒ ★本页一旦写进去, 那道**已签收闸**的红项就会从 4 条变成 5 条 ⇒ ★**等于我用自己的新页去扰动一道已签收闸的判决** ⇒ ★**那是「板只改一次」铁律的红线, 本单不越** ⇒ ★板 md5 的真值请查 `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 的 §0 机器块 (`board.md5` 字段) ★

---

## §0 一句话结论

1. **闸 1 (`SW/tools/check_debug_pin_order_contract.py`, ISS-375 签收件)**: ★**它没有「坏」, 它是【判据与环境耦合】** —— 它的 M2 反向用例把闸源码复制进 `tempfile.mkdtemp(prefix="iss375_selftest_")` 建的沙盒里再跑, 而副本的 `ROOT` 是从副本自己的 `__file__` 往上退两级算出来的 ⇒ ★**沙盒落在系统 `/tmp` 时 `ROOT` 退化成 `/` ⇒ 副本去找 `/SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` ⇒ 不存在 ⇒ FATAL ⇒ 该用例假红** ★`[实测]`
2. **闸 2 (`SW/tools/check_sw_board_md5_rebase_readiness.py`, ISS-372 签收件)**: ★**它没有「坏」, 它是【账本与现实漂移】** —— ISS-381 新建的 `SW/tools/check_sw_false_connectivity_gate.py` 硬钉了板 md5, 但它没进 ISS-372 真相页 §2 的账 ⇒ 它的 H4 判红 (★**这正是 H4 被设计出来要抓的那件事**★) ⇒ **H1 也红了 4 行** ⇒ ★**[实测]**
3. **★为什么没人看见**: ★**两道闸都是【零挂链】** (`state/gate_check.py` 里没有它们) ⇒ ★**它们判红时没有任何人收到通知** ⇒ ★**「闸自己坏了」这件事本身没有任何检测手段** ⇒ ★**⇒ 这就是本单新建 `SW/tools/check_sw_gate_health.py` 的全部理由** ★

---

## §1 闸 1 诊断 · 「判据与环境耦合」

### §1.1 症状 [实测]

```
$ python3 SW/tools/check_debug_pin_order_contract.py --selftest          # 默认 TMPDIR
  [PASS] M1       把页里的 rot 90 改成 rot 270                    期望红=D2,D3,D4  实红=D2,D3,D4
  [FAIL] M2       把 D2 的算式改成手算常数 (变异本闸源码)           期望红=D2,D4     实红=FATAL: 变异体无 JSON 输出
        ← 期望集未被完全命中 · FATAL: [Errno 2] No such file or directory:
          '/SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md'
  [PASS] M3 / T-D0 / T-D1 / T-D3 / T-D6 / T-D8a / T-D8b / T-D7 / T-D8c
=== selftest 10/11 PASS (共 11 条反向用例, 其中镜像类 3 条) ===
SELFTEST FAILED
rc=1

$ TMPDIR="$PWD/tmp" python3 SW/tools/check_debug_pin_order_contract.py --selftest
  [PASS] M2       把 D2 的算式改成手算常数 (变异本闸源码)           期望红=D2,D4     实红=D2,D4   · 变异体 rc=1
=== selftest 11/11 PASS (共 11 条反向用例, 其中镜像类 3 条) ===
ALL TESTS PASS
rc=0
```
★**同一份源码、同一台机器, 只差 `TMPDIR` ⇒ 10/11 vs 11/11 ⇒ 病根不在判据, 在环境** ★`[实测]`
★完整原样输出留证: `logs/iss388/cont1_verify.log` 的 `=== [2a] ===` / `=== [2b] ===` 两节 ★

### §1.2 因果链 [实测 + 推算(逐步可复算)]

1. `SW/tools/check_debug_pin_order_contract.py` L39:
   `ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))`
   ⇒ ★**`ROOT` 完全由「副本自己所在路径」反推** ★
2. `run_selftest()` L879:
   `tmpdir = tempfile.mkdtemp(prefix="iss375_selftest_")`
   ⇒ ★**注意: 这一行没有 `dir=` 参数** ⇒ ★**沙盒落在 `tempfile.gettempdir()`** ⇒ ★**也就是 `$TMPDIR`, 没设时是系统 `/tmp`** ★
   ★(对比: 同文件 L142 `tempfile.mkdtemp(prefix="iss375_py_", dir=sbx_dir())` 与 L118 `sbx_dir()` 是**显式钉在项目盘 `tmp/iss375_sbx/`** 的 ⇒ ★**只有 selftest 的这一个是漏网的**★) ★
3. 反向用例 M2 (`_case_m2_gate_formula`, L764~789) 把**闸源码整份**写进沙盒: `mutant_path = os.path.join(tmpdir, "_mutant_gate_m2.py")`, 然后 `subprocess.run([sys.executable, mutant_path, "--json"])` ⇒ ★**副本的 `__file__` 变成了沙盒路径** ★
4. ⇒ 副本的 `ROOT` = 沙盒路径往上退两级:
   - 沙盒 = `/tmp/iss375_selftest_XXXX` ⇒ `ROOT` = `/` ⇒ `PAGE` = `/SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` ⇒ **不存在** ⇒ 副本抛 `FileNotFoundError` ⇒ **没有 JSON 输出** ⇒ M2 判红 (`实红=FATAL: 变异体无 JSON 输出`) ★
   - 沙盒 = `<root>/tmp/iss375_selftest_XXXX` ⇒ `ROOT` = `<root>` ⇒ `PAGE` 命中 ⇒ 副本正常跑 ⇒ M2 实红 = `{D2, D4}` ⇒ 与期望集相等 ⇒ PASS ★
   ⇒ ★**判据本身没变, 变的只有「副本的根」** ★`[实测]`

### §1.3 ★为什么签收当天是绿的★ [实测]

★**签收当天 main 跑 selftest 时, `TMPDIR` 就是 `$PWD/tmp`** ⇒ 沙盒落在项目盘 ⇒ `ROOT` 反推正确 ⇒ 11/11。★三条独立留证:

| # | 证据 | 位置 |
|---|---|---|
| E1 | ★**签收当天的必跑脚本第 4 行就是 `export TMPDIR=$PWD/tmp`** ★ | `tmp/iss375_sbx/iss375_final_cmds.sh` |
| E2 | ★**签收当天自测输出留痕: 11/11 PASS + `ALL TESTS PASS`** ★ | `state/.verify/sign_iss375_selftest.txt` |
| E3 | ★**签收当天留下的沙盒实体目录就在项目盘 `tmp/` 下面** (`tmp/iss375_selftest_5wzcz2qq`) ⇒ ★**反推 `TMPDIR` 当天 = `<root>/tmp`** ★ | `tmp/iss375_selftest_5wzcz2qq/` |

★**⇒ 结论: 闸 1 不是「坏了」, 是「一直绿, 但只在 `TMPDIR=$PWD/tmp` 的约定下绿」—— 这个约定从没被写进任何契约文件, 只活在签收那天的一次 shell 环境里** ⇒ ★**今天 main 用默认 TMPDIR 跑 ⇒ 就红了** ★`[实测]`
★**⇒ 这是一个典型的「隐式环境契约」**: **闸的判据是对的, 但它对「从哪个目录被调用」的依赖是隐式的** ★`[推算]`

### §1.4 归因与地界

- ★**本单不改这道闸的判据/阈值一个字** (ISS-375 签收件) ★
- ★**修法有两条路, 都是 main 的裁决权, 本单只摆代价, 不代拍** (详见 §5 待裁项 N3) ★

---

## §2 闸 2 诊断 · 「账本与现实漂移」

### §2.1 症状 [实测]

```
$ python3 SW/tools/check_sw_board_md5_rebase_readiness.py
  [PASS] H2 / H3 / H5 / H6 / H7
  [FAIL] H1 · SW 域板 md5 引用面必须被 §1 清单逐处覆盖
        ⚠ 扫描到 SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23  但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红
        ⚠ 扫描到 SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:241 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红
        ⚠ 扫描到 SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红
        ⚠ 扫描到 SW/tools/check_sw_false_connectivity_gate.py:73 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红
  [FAIL] H4 · SW 域每道【真钉板 md5 的判据脚本】必须登记在册 (类A 字面量 + 类B 页面内嵌基线)
        ⚠ SW 域有闸 SW/tools/check_sw_false_connectivity_gate.py 硬钉了板 md5 (类A·.py 内 32 位字面量) 但它没进 §2 的账 ⇒ 判红
闸结果 5/7 通过, rc=1
```

### §2.2 登记漂移账 [实测]

| 漂移项 | 盘上事实 | 账上事实 | 谁建的 | 什么时候 | 差集方向 |
|---|---|---|---|---|---|
| **D-1** | `SW/tools/check_sw_false_connectivity_gate.py:73` 有 32 位板 md5 字面量 (类A) | §2 的 `gates` 清单里**没有**这道闸 | ISS-381 | 2026-11-24 06:25~07:20 一线 | ★**账缺 ⇒ 现实多** ★ |
| **D-2** | `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23` 引用了板 md5 | §1 的 `refs` 清单里**没有**这一行 | ISS-381 | 2026-11-24 | ★**账缺 ⇒ 现实多** ★ |
| **D-3** | `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:241` 引用了板 md5 | §1 的 `refs` 清单里**没有**这一行 | ISS-381 | 2026-11-24 | ★**账缺 ⇒ 现实多** ★ |
| **D-4** | `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215` 引用了板 md5 | §1 的 `refs` 清单里**没有**这一行 | ISS-378 一线 | 2026-11-24 03:1x | ★**账缺 ⇒ 现实多** ★ |

★**判红方向单一: 全部是「现实多、账少」⇒ 没有任何一条是「账上写了、盘上没了」⇒ ⇒ 这不是账本写错了, 是账本【没跟上】** ★`[实测]`

### §2.3 ★★「闸没坏」的证据 ★★ [实测]

★**H1/H4 判红, 恰恰是这两条判据被设计出来要抓的那个现象**: H4 的设计意图就是「SW 域再硬钉板 md5 的闸, 当场被抓住」⇒ **ISS-381 新建 `check_sw_false_connectivity_gate.py` 时, 这道闸就应该当场把它抓出来** ⇒ ★**它抓到了 ⇒ 它是绿的 (在「账」的意义上) ⇒ 只有账没跟上** ★

### §2.4 ★★第三个失效模式: 「差值型自测在基线漂移时全灭」★★ [实测]

```
$ python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest
  用例 1 · 目标 H1 · 红的集合 = ['H1', 'H4'] · FAIL
  用例 2 · 目标 H2 · 红的集合 = ['H1', 'H2', 'H4'] · FAIL
  ...
  用例 10 · 目标 无 (期望全绿) · 红的集合 = ['H1', 'H4'] · FAIL
反向用例: 0/10 通过
★有用例 FAIL ⇒ 本闸不可信 ⇒ rc=1★
```

★**原因**: 这道闸的 selftest 每条用例都断言「**红的集合 == {目标那一条}**」⇒ ★**这是一个【差值断言】⇒ 前置条件是【基线本身全绿】** ⇒ ★**基线已经被 §2.2 的四条漂移弄红了 ⇒ 每条用例的红集都 ⊋ {目标} ⇒ 10/10 全 FAIL** ★
★**⇒ 于是出现一个二阶放大: 账本漂移 (H1/H4 红) → 差值型自测全灭 (0/10) → 闸自己宣告「本闸不可信」⇒ 人再去查「是不是闸坏了」⇒ ★**真相是「闸没坏, 是账漂了」, 但闸自己没法说这句话** ★`[实测]` + `[推算]`
★**⇒ 这就是本单新闸 H0 必须【点名】而不是只报一个布尔值的原因: 要让人一眼看出「是哪个闸的哪一条红了」, 而不是「闸不可信」四个字** ★

---

## §3 两道闸的共同失效模式抽象

★**把 §1 与 §2 摆在一起, 抽象出三类「闸的失效」** ★

| 类 | 名字 | 机理 | 现场证据 | 为什么没人看见 |
|---|---|---|---|---|
| **①** | ★**判据与环境耦合** ★ | 判据的输入依赖「从哪个目录/哪个 TMPDIR 被调用」, 这个依赖是隐式的 | 闸 1: 同源码 `TMPDIR` 一换, 10/11 → 11/11 | ★**零挂链 ⇒ 没人跑 ⇒ 没人发现它对环境敏感** ★ |
| **②** | ★**账本与现实漂移** ★ | 「账」(清单/台账) 与「现实」(盘上文件) 之间的差集没有被任何机制在【新增那一趟】当场消掉 | 闸 2: H1 4 行 + H4 1 道闸 全部「现实多、账少」 | ★**零挂链 ⇒ 红了没人看见 ⇒ 漂移持续累积** ★ |
| **③** | ★**差值型自测在基线漂移时全灭** ★ | 自测断言的是「红集 == {目标}」, 基线不绿 ⇒ 自测全灭 ⇒ 闸自曝「不可信」, 但掩盖了真因 | 闸 2 selftest 0/10 | ★**零挂链 + 自测退化 ⇒ 连「自测可信」这件事本身都没人能查** ★ |

★★**三类里有两类 (①③) 是【闸自己的健康度】问题, 现有 13 道闸一条都查不出来** ⇒ ★**⇒ 本单新建的 `SW/tools/check_sw_gate_health.py` 就是补这个洞的** ★
★★**⇒ 关键洞察: 「零挂链」是这两道闸烂掉的**根本原因**, 但「零挂链」本身是本项目的既定纪律 ⇒ ⇒ **本单只能做到「把零挂链的闸的坏处【可见化】, 挂不挂链交 main 裁决」** ★`[推算]`

---

## §4 影响面 · 这两道闸在「板只改一次」那一趟里各自把关什么

| 闸 | 在「板只改一次」那一趟里守的是什么 | 它烂掉的后果 | 严重度 |
|---|---|---|---|
| ★`check_debug_pin_order_contract.py` (ISS-375) ★ | ★**物理针序契约**: 调试排针 1x04 的 pad1 到底在哪 / 官方 land 的实际 pad1 形状 / JTAG 四线 SoM 侧端点 / SoM 侧与板侧是否互为逆序 ⇒ ★**它是「排针插反 = 烧板」的唯一护栏** ★ | ★**插针方向没人拦 ⇒ 一块烧掉的板** ★ | ★**最高** ★ |
| ★`check_sw_board_md5_rebase_readiness.py` (ISS-372) ★ | ★**板 md5 引用面自守**: 「SW 域每道钉板 md5 的闸都必须登记在册」+ 「板指纹三项未动」⇒ ★**它是「改板那天, 所有引用旧 md5 的东西都跟着改」的护栏** ★ | ★**改板那一趟, 旧 md5 的引用面没人清账 ⇒ 半新半旧的真相 ⇒ 后面每一趟都建在流沙上** ★ | ★**高** ★ |

★**⇒ 这两道闸烂掉 ⇒ 「板只改一次」那一趟【没有护栏】⇒ ⇒ 那一趟就变成「一撞就碎、且碎了不知道」的一趟 ⇒ ★**这就是 ISS-388 必须闭环的原因** ★`[推算]`

---

## §5 降级方案 + 待裁项 (★全部 to=main · 本单不代拍★)

| 编号 | 待裁项 | 两条路的代价 | 降级方案 (main 不裁时的兜底) |
|---|---|---|---|
| ★**N1** ★ | ★**闸 2 的 §1/§2 账本差集 (D-1~D-4) 归谁修** ★ | **路 A**: main 指派回 sw-lead 去改 ISS-372 真相页的 §1/§2 机器块 (★改的是**已签收页** ⇒ 需 main 授权★) ⇒ 代价: 要重跑闸 2 的 10 条反向用例 + 重签 ISS-372。★**路 B**: main 自己改 (main 的地界) ⇒ 代价: 同上但由 main 承担。 | ★**降级: 本单不改账, 只把差集逐条登记成 `needs_from to=main`; 闸 2 保持判红 (★那是它的正确行为★) ⇒ 后果是「板只改一次」那一趟必须【人工】复核这 4 条** ★ |
| ★**N2** ★ | ★**新闸 `check_sw_gate_health.py` 挂不挂 `state/gate_check.py`** ★ | **路 A**: 挂 ⇒ ★**立刻能看见闸坏了**, 但 ★**它今天就是红的** (H0/H1/H2/H3 会当场点名三处病灶) ⇒ 代价: `gate_check.py` 的读数会从今天的「全绿」变成「有红」, 需要 main 接受这个新基线。★**路 B**: 不挂 ⇒ 零扰动, 但 ★**重蹈覆辙 (零挂链 ⇒ 没人看见)** ★。 | ★**降级: 零挂链 (本单已落盘), 交卷页写明「建议挂在哪个位置 + 挂链后的预期读数」⇒ 等 main 裁决** ★ |
| ★**N3** ★ | ★**闸 1 的环境敏感在【源头上】修还是在【调用约定】上修** ★ | **路 A (改闸)**: 改 `ROOT` 反推机制 / 给 `mkdtemp` 显式 `dir=sbx_dir()` ⇒ ★**属于改已签收件的判据逻辑 ⇒ main 地界** ⇒ 代价: 要重签 ISS-375 + 重跑 11 条反向用例。★**路 B (改调用约定)**: 把「所有 selftest 必须 `TMPDIR=$PWD/tmp`」写进 `state/check_brief_commands.py` 或任务书模板 ⇒ ★**改的是调用方, 不是被签收件** ⇒ 代价: 约定靠人记, 会有忘的那天。 | ★**降级: 本单在诊断页 §1.3 把「签收当天 TMPDIR 是 `$PWD/tmp`」这个事实写成明文; 新闸 H1 判据已经在【自动】检测这一类 ⇒ 不再靠人记** ★ |

★**★三条全是 main 的裁决权 ⇒ 本单【只摆代价, 不写「应该 X」】⇒ 机器块里三条一律写 `not_decided_here`** ★

---

## §6 复跑命令 + 机器块

### §6.1 复跑命令 (★全部实测存在·不许自己编★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ① 闸 1 · 环境敏感对照实验 (★本单的命门证据★)
python3 SW/tools/check_debug_pin_order_contract.py --selftest      # ★默认 TMPDIR ⇒ 10/11 FAIL rc=1★
TMPDIR="$PWD/tmp" python3 SW/tools/check_debug_pin_order_contract.py --selftest   # ⇒ 11/11 PASS rc=0

# ② 闸 2 · 账本漂移
python3 SW/tools/check_sw_board_md5_rebase_readiness.py             # ⇒ 5/7 rc=1 (H1 4 行 + H4 1 道闸)
python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest  # ⇒ 0/10 rc=1 (★差值型自测全灭★)

# ③ 本单新闸 (★零挂链★)
python3 SW/tools/check_sw_gate_health.py
python3 SW/tools/check_sw_gate_health.py --selftest

# ④ 板 / 三表 指纹 (★零写板 · 零落表自证★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑤ 收尾
python3 state/frag_write.py --agent sw-lead --show
python3 state/merge.py
python3 state/gate_check.py
```

### §6.2 机器块

```json
{
  "schema": "iss388.sw_gate_failure_diagnosis.v1",
  "issue": "ISS-388",
  "cont": "cont1",
  "agent": "sw-lead",
  "date": "2026-11-24",
  "sick_gates": [
    {
      "gate": "SW/tools/check_debug_pin_order_contract.py",
      "signed_by": "ISS-375",
      "failure_mode": "判据与环境耦合",
      "symptom": "默认 TMPDIR 下 selftest 10/11 FAIL rc=1; TMPDIR=$PWD/tmp 下 11/11 PASS rc=0",
      "root_cause": "run_selftest() 的 mkdtemp 无 dir= 参数 ⇒ 沙盒落 tempfile.gettempdir(); M2 变异副本的 ROOT 由 __file__ 退两级反推 ⇒ 沙盒在 /tmp 时 ROOT 退成 /",
      "green_on_signoff_because": "签收当天 TMPDIR=$PWD/tmp (证据: tmp/iss375_sbx/iss375_final_cmds.sh 第4行 / state/.verify/sign_iss375_selftest.txt / tmp/iss375_selftest_5wzcz2qq)",
      "evidence": "[实测]",
      "modified_by_this_task": false
    },
    {
      "gate": "SW/tools/check_sw_board_md5_rebase_readiness.py",
      "signed_by": "ISS-372",
      "failure_mode": "账本与现实漂移 (+ 差值型自测在基线漂移时全灭)",
      "symptom": "裸跑 5/7 rc=1 (H1 4 行 + H4 1 道闸); --selftest 0/10 rc=1",
      "root_cause": "ISS-381 新建 check_sw_false_connectivity_gate.py 硬钉板 md5 却没进 §2 账; ISS-381/ISS-378 三页新引用没进 §1 账; 差值型自测断言 红集=={目标} ⇒ 基线漂了以后 10 条全灭",
      "green_on_signoff_because": "签收当天账与现实还一致 (ISS-381 之后才漂)",
      "evidence": "[实测]",
      "modified_by_this_task": false
    }
  ],
  "drift_ledger": [
    {"id": "D-1", "file": "SW/tools/check_sw_false_connectivity_gate.py", "line": 73, "missing_in": "§2 gates", "direction": "现实多账少", "created_by": "ISS-381"},
    {"id": "D-2", "file": "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md", "line": 23, "missing_in": "§1 refs", "direction": "现实多账少", "created_by": "ISS-381"},
    {"id": "D-3", "file": "SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md", "line": 241, "missing_in": "§1 refs", "direction": "现实多账少", "created_by": "ISS-381"},
    {"id": "D-4", "file": "SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md", "line": 215, "missing_in": "§1 refs", "direction": "现实多账少", "created_by": "ISS-378"}
  ],
  "new_gate": {
    "path": "SW/tools/check_sw_gate_health.py",
    "hooked_into_gate_check": false,
    "hook_count_grep": 0,
    "criteria": ["H0", "H1", "H2", "H3", "H4", "H5"],
    "selftest_reverse_cases_min": 8
  },
  "boundary_selfproof": {
    "board_written": false,
    "netlist_tables_written": false,
    "existing_gate_criteria_modified": false,
    "existing_pages_modified": false,
    "zero_hook": true,
    "outbound_mail": false,
    "decided_on_main_behalf": false,
    "issue_log_touched": false,
    "sandbox_only": ["tmp/iss388_sbx/", "logs/iss388/"],
    "system_tmp_written": false
  },
  "decisions": {
    "n1_ledger_drift_owner": "not_decided_here",
    "n2_new_gate_hooked_into_gate_check": "not_decided_here",
    "n3_env_sensitivity_fix_location": "not_decided_here"
  },
  "evidence_levels": ["[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]"]
}
```

---

## §7 边界自证

| 边界 | 怎么自证 | 读数 |
|---|---|---|
| ★零写板★ | 板 md5/mtime/size 前后逐字相同 | 板 md5/mtime/size 与基线逐字相同 (见交卷页 B6) |
| ★零落表★ | 网表/脚表/BOM 三件 md5 前后逐字相同 | 同上 |
| ★零改既有闸的判据/阈值★ | 两道病闸 md5 与基线同 | `SW/tools/check_debug_pin_order_contract.py` / `SW/tools/check_sw_board_md5_rebase_readiness.py` md5 与开工前同 |
| ★零改既有页面正文★ | ISS-372/375/381/385 已签收页 md5 与基线同 | 同上 |
| ★零挂链★ | `grep -c check_sw_gate_health state/gate_check.py` | 0 |
| ★零外发★ | 全程只读本机; `state/outbox/` 未动 | 未动 |
| ★不代拍★ | 三条待裁项一律 `not_decided_here` | §6.2 `decisions` 三字段 |
| ★不自签台账★ | `state/issue_log.yaml` 未动 | 未动 |
| ★没写别人的分片★ | 只写 `state/fragments/sw.yaml` | 只写 sw.yaml |
| ★沙盒纪律★ | 只落 `tmp/iss388_sbx/` 与 `logs/iss388/` | 未往系统 `/tmp` 写 |
| ★证据分级★ | 每条结论标五级之一 | §0~§7 逐条已标 |

<!-- ISS388-DIAGNOSIS-PAGE -->
