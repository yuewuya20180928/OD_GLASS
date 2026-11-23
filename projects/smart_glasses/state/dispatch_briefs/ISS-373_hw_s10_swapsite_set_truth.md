# ISS-373 · hw-lead · 「板那一趟」S10 换 land 集合的**唯一真源** + 一条「集合口径」机器闸 · 纯分析 + 作业包 + 新建闸 + 沙盒预演 · 零写板

★★**题**: ★**把「S10 那一趟到底换几件」这条【跨三个域、四个页面、四套口径】的悬案, 收成【一个可复跑的集合真源 + 一条机器闸】** ★★

---

## ★★一 背景 (★main 2026-11-23 22:4x~23:0x 本机实读 · **不抄任何 agent 报告** · 每条都可复跑★) ★★

★**主线背景**: ★**「板只改一次」那一趟 = 板 md5 只许变 1 次** (★`HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` INV-1/INV-3★) ⇒ ★**「那一趟换几件」这个问题只要在开工当天还有第二种口径, 就必然有人按错的那份布局 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★

★**★现在有 FOUR 套口径在同一个项目里同时活着 (★本机实读, 四处原文★)★**:

| # | 来源 (★页面/脚本★) | 它写的「件数」 | ★**本机实读原文**★ |
|---|---|---|---|
| **①** | ★`MECH/check_onepass_s10_fp_swap_impact.py` (★ISS-365 机器闸★) | ★**90** ★ | ★实跑输出: 「靶内 = 77 件 + 缺口 = 13 件 ⇒ ★S10 要换官方 land 的集合 = 90 件★」★ |
| **②** | ★`HW/check_fp_libid_truth.py` + `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` §3.3 (★ISS-369★) | ★**90 / 96 / 186 / 158** ★ | ★§3.3 「本单对象 (表 A) = 90 · 其余 (表 B) = 96 · 板面封装总数 = 186 · C4 占位脚号件数 = 158」★ |
| **③** | ★`MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` §1.6 (★ISS-367★) | ★★**91** ★★ | ★§1.6 标题写「★**若那一趟把 90 件全换**★」, 但★**表格行写「★**AFTER (全部 91 件靶子都换)**★ ⇒ 2200」★, §4.2 也写「★**91 件靶子全换 ⇒ 块数 2183→2200**★」★ ⇒ ★**同一页里「90」和「91」并存** ★ |
| **④** | ★`MECH/check_onepass_s10_led_spec_sync.py --compute` (★★本机 22:5x 实跑★★) | ★★**91** ★★ | ★★输出 JSON 末尾: `"swap_n": 25, "swap_all90_n": 91` ★★ ⇒ ★**脚本自己算出来是 91, 可它的变量名却叫 `swap_all90`** ★ |

★**★main 本机实算 (★用 ① 和 ③ 各自的**真函数**复算, 不是抄★) ★★**:

```python
# main 2026-11-23 22:5x 本机跑 (★只读 import, 不改任何文件★)
bom = cov.load_bom("HW/BOM_v1.csv")
c4  = set(cov.netlist_placeholder("HW/netlist_v1.csv"))     # C4 占位脚号集合
iss = set(mech.read_iss356_targets(root))                    # ISS-356 靶子集合
gap = cov.coverage_gap(bom, c4)                              # 缺口集合
inter = iss & c4
print(len(c4), len(iss), len(inter), len(gap))
# ⇒ 实测输出: C4=158  iss356=78  inter=77  gap=13
print(sorted(iss - inter - set(gap)))
# ⇒ 实测输出: ['J_DEBUG']      ★★★只有这一件★
print(len(inter)+len(gap), len(iss)+len(gap))
# ⇒ 实测输出: 90  91
```

★★**⇒ 本机实算的结论 (★数字逐字可复跑★)**:

| 集合 | 算法 | 件数 | 含 `J_DEBUG` ? |
|---|---|---|---|
| ★**90** ★ | `(ISS-356 靶子 ∩ C4) + 缺口` = 77 + 13 | ★**90** ★ | ★**否** ★ |
| ★**91** ★ | `(ISS-356 靶子全体) + 缺口` = 78 + 13 | ★**91** ★ | ★**是** ★ |

★**⇒ ★★`J_DEBUG` 就是这 1 件的差 ★★** ★⇒ **两套口径的差别 = 恰好 `J_DEBUG` 一件** ★

★★**★为什么这一件值得单独查 (★这才是本单的真题·不是数字洁癖★)★★**:

★**★`J_DEBUG` 在那一趟【确实要动 land】★** ⇒ ★本机实读 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` (★ISS-290 · step S6★) 原文: 「★**`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm** (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)」★ + 期望读数: 「★J_DEBUG land pitch = 1.27 / J_UART land pitch = 1.27★」★ ⇒ ★**`J_DEBUG` 不在「90 件换 land 名单」里, 但它【另一条腿】要换 land ⇒ 两份清单会漏掉它** ★

★**★而 `J_DEBUG` 的现页写「不写库名」的理由, 恰好把这条腿否掉了★** ⇒ ★本机实读 `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` 表 B 行: 「★**`J_DEBUG`** | 靶内-非C4 | **不写** | ★**不需要写**★ | — | BOM footprint 栏 = 「待定」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; **且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land** ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测]★」★ ⇒ ★★**它的推理链是「因为它不在 90 件名单里 ⇒ 本趟不动它的 land」⇒ 而 B33 说本趟【要】动它的 land ⇒ 这条推理的前提与 B33 冲突** ★★

★★**⇒ 所以「90 还是 91」这个问题在那一趟有【两种后果完全不同】的答案 ★★**:

| 若那一趟实际换 | ⇒ 后果 |
|---|---|
| ★**90 件 (不含 J_DEBUG)** ★ | ★`J_DEBUG` 的 land 不动 ⇒ ★**B33 的期望读数「J_DEBUG land pitch = 1.27」永远达不到 ⇒ B33 这一项判红** ★ ⇒ ★**而且实物 1.27mm 排针仍然落不进** ⇒ ★**板要么改第二次, 要么实物报废** ★ |
| ★**91 件 (含 J_DEBUG)** ★ | ★`J_DEBUG` 的 land 要换 ⇒ ★**按 ISS-369 自己的 §2.3 机制, 换 land 必须同时写库名** (★同一封装块 ①②③④ 必须同一次做完⇒ 板 md5 只变一次★) ⇒ ★★**那 `J_DEBUG` 就必须进「写库名」名单** ⇒ 「写 94 / 不写 92」这个口径也要跟着改** ★★ |

★**★⇒ 结论 (★main 的话, 不是你的话★): ★**这一件在「那一趟」要不要换 land, 只有两条路, 都要落成机器可查的判据; ★**但【选哪条】是 main 的裁决权, 不是你的** ⇒ ★**你这一单只做【把两条路各自的完整后果算清 + 把判据做成闸 + 把 90/91 两套口径的来源钉成唯一真源】, 不代拍** ★★

---

## ★★二 你这一单要交的东西 (★三件 + 交卷页 + 分片★) ★★

### ★★① ★**新建★ 一页集合真源 `HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` (★本单产出物·交卷时它才存在★) ★★

★**必须含 (★每个数字带复跑命令★)**:

1. ★**§0 口径表**: 90 / 91 两套算法各一行 (★算法式 + 件数 + 含不含 `J_DEBUG`★) + ★**本机实算脚本片段** (★照 §一 那段, 你自己重跑一遍贴输出★)
2. ★**§1 四处口径逐条对表**: 上表 ①②③④ 四处, 每处给「★文件路径 + 行号 + 它写的数 + 它是【集合定义】还是【敏感度算例】★」 ⇒ ★**你要判清 `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` 里那个「91」到底是【集合定义】还是【§1.6 敏感度算例的一行】★** (★这是本单的核心判断之一 ★)
3. ★**§2 `J_DEBUG` 一件的完整账**: ★**四条腿逐条列** ——
   - ① `J_DEBUG` 在不在 C4 158 里? ★**不在**★ (★本机实算★)
   - ② 在不在 ISS-356 靶子 78 里? ★**在**★ ⇒ ★**这正是 90 vs 91 的那 1 件差**★
   - ③ `B33_PIN_LAND_1P27` 要不要动它的 land? ★**要**★ (★引原文★)
   - ④ ISS-369 说「不写库名」的理由是什么? ★**引原文 + 指出它与 ③ 的冲突**★
   - ⇒ ★**⑤ 两条路各自的后果表** (★上表那张, 但你要自己把「若换」那行的完整后果算出来: 包括写库名名单要不要从 94/92 改成 95/91 这类联动手 ★)
4. ★**§3 「写库名」名单的联动手**: ★**若 `J_DEBUG` 进换 land 名单 ⇒ ISS-369 §2.3 说换 land 必须同时写库名 ⇒ 「写 94 / 不写 92」这两个数怎么变? ★把算式写出来 (★不许拍, 只给算式 + 结论口径★)** ★
5. ★**§4 未决项**: ★只登记不代拍★ —— ★**「那一趟 `J_DEBUG` 换不换 land」这条要 main 裁 (★因为它同时牵动 B33 与 ISS-369 两页 + MECH 侧两处机器块★) ⇒ 你把两条路的代价列清, 交 main** ★
6. ★**§5 复跑命令** + ★**§6 边界自证** (★板指纹三项未动 + 既有闸/既有页面 md5 未动 + 零写板 + 零落表★)

### ★★② ★**新建★ 一条新闸 `HW/check_onepass_s10_swap_set_truth.py` (★本单产出物·交卷时它才存在★) ★★

★**判据 (★至少 L0~L8 · 每条 fail-closed · 每条带反向用例★)**:

| # | 判据 | ★**不许写死的**★ |
|---|---|---|
| L0 | ★**集合算法自算**: 脚本自己从 `HW/BOM_v1.csv` + `HW/netlist_v1.csv` + `HW/FP_TRUTH_BASELINE.md` 基准块算出 (★inter + gap★) 和 (★iss + gap★) 两个数 ⇒ ★**页里写的数 ≠ 脚本实算 ⇒ 红** ★ | ★不许把 90 / 91 写死成常量 ★ |
| L1 | ★**差集恰为 1 件且是 `J_DEBUG`** ⇒ ★**不是 1 件 ⇒ 红** (★差集变了 ⇒ 两套口径的差变了 ⇒ 全部下游数都要重算★) ★ | ★不许写死 `J_DEBUG` 一个名字就算过 (★要脚本自己算出来再比★) ★ |
| L2 | ★**页 §0 口径表两行都在, 且都带复跑命令** ★ | |
| L3 | ★**四处口径逐条可查** (★文件路径 + 行号 + 那个数 + 它是定义还是算例★) ⇒ ★**少一条 ⇒ 红** ★ | |
| L4 | ★**`J_DEBUG` 四条腿逐条齐全** + ★**与 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 交叉引到** (★★该件换不换 land 的两边说法必须同时在页里出现, 不许只留一边★★) ★ | |
| L5 | ★**写库名名单的联动手算式在页里** (★若换 ⇒ 94/92 怎么变★) ★ | |
| L6 | ★**板面零写板自证** (★md5 / mtime / size 三项 == `611b869e13518c3c023fb178f91a0075` / `2026-11-06 07:07:17.362193413` / `4940213`★) ★ | |
| L7 | ★**证据等级五级白名单** `[官网]/[实测]/[媒体]/[推算]/[0数据]` + ★**零挂起措辞** (★不许出现「待补」「等原厂」「应该没问题」★) + ★**判据句/事实句分开写** ★ | |
| L8 | ★**零挂链** (★本闸【不许】挂进 `state/gate_check.py` 的 `EXTRA_GATES` ⇒ 挂不挂归 main★) ⇒ ★**自证: `grep -c check_onepass_s10_swap_set_truth state/gate_check.py` == 0** ★ | |

★**★必须带 `--selftest` (★≥8 条反向用例·每条自证「红的是目标那一条, 其余仍绿」★)★★**

### ★★③ 沙盒预演 (★只落 `tmp/iss373_sbx/` + `logs/iss373/`★) ★★

★**目的: 把「90 / 91 两种集合各自在沙盒里跑一遍」变成可复现的数, 而不是纸上推演★**:

★**用 `bash state/pcbnew_py.sh` (★本机 KiCad 10.0.8★) 在【板副本】上做, 真板零改动★**:

| 轮次 | 板副本上换哪几件 | ★**要报的数** ★ |
|---|---|---|
| ★**S0** ★ | 不换 (★基线★) | ★`state/check_pcb_nets.py` 的 C1/C2/C3/C4 读数 ★ |
| ★**S1** ★ | ★**90 件** (★按 ① 的算法实算出来的那一套★) | ★同上 + ★**换完的板副本 md5 / 段数 / 过孔数 / 零铜网数 / 单边零铜对数** ★ |
| ★**S2** ★ | ★**91 件** (★= S1 + `J_DEBUG` 一件, 用官方 `Connector_PinHeader_1.27mm.pretty/PinHeader_1x04_P1.27mm_Vertical.kicad_mod`★) | ★同上 + ★**★`J_DEBUG` 换完后的实测 land pitch / 铜箔 X 宽 / fab 外框★★** ★ |

★**★S2 那三个数是本单最有价值的产出 ★★** ⇒ ★**你要把 `J_DEBUG` 换成官方 1×4 THT land 之后: 实测它的 land pitch (★期望 1.27★) · 实测它的铜箔 X 宽 · 实测它的 fab 外框 · 实测换完之后 C1/C2/C3/C4 相对 S0/S1 的差异 (★★尤其 C3 「板脚数 vs 网表脚数」会不会因此变★★)** ★

★**★沙盒纪律 (★一条不许破★)★★**: ★**副本只落 `tmp/iss373_sbx/`** · ★**不许写真板** (★板 md5 开工前/交卷后各打一次★) · ★**不许跑会重铸随机 UUID 的门禁去"验"板** (★`state/check_sch_pinfull.py` / `state/check_sch_erc.py` 内部会 subprocess 调 `state/gen_kicad_sch.py` ⇒ 重铸 UUID ⇒ 任何 md5 比对都失效⇒ **板 md5 只能在你自己的脚本前后打, 不能跑完门禁再打**★) ★

---

## ★★三 边界 (★一条不许越★) ★★

★**零写板** (★真板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` 三项开工前/交卷后各打一次★) ★
★**零落表** (★网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 一律只读★) ★
★**零改既有闸** (★`HW/check_fp_libid_truth.py` / `HW/check_fp_truth_land_swap.py` / `HW/check_fp_truth_coverage_gap.py` / `HW/check_onepass_preflight_coverage.py` / `MECH/check_onepass_s10_fp_swap_impact.py` / `MECH/check_onepass_s10_led_spec_sync.py` / `MECH/check_jdebug_1p27_clearance.py` / `state/gate_check.py` / `state/merge.py` / `state/frag_write.py` 一字不改★) ★
★**零改既有页面正文** (★`HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` · `MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md` · `MECH/BOARD_ONEPASS_MECH_SYNC.md` · `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` —— ★**本单只新写一页 + 一条闸, 既有页面一个字都不许动** ★ ⇒ ★**要订正既有页面的部分 ⇒ 写成「追加式订正块」放进【你自己那一页】的 §4, 由 main 决定要不要往既有页面落★**) ★
★**零挂链** (★本单新闸【不许】挂进 `state/gate_check.py`★) ★
★**只写自己的分片 `state/fragments/hw.yaml`** (★**只走 `state/frag_write.py`** ★· 写前写后各记一次 md5 · 期间被别人改过 ⇒ 停下并在交卷页 B5 写明「已停止」· 不许静默覆盖★) ★
★**沙盒只落 `tmp/iss373_sbx/` + `logs/iss373/`** ★
★**不代老板拍板** · **不代 main 拍** (★「`J_DEBUG` 那一趟换不换 land」是 main 的裁决权 ⇒ 你只给两条路的代价与判据★) ★
★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 ⇒ **全靠自己查资料** · **不许发任何邮件/询价/问询** · **不许写「等原厂回信」** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案★) ★
★**不自签 `state/issue_log.yaml`** (★台账由 main 签收★) ★
★**零推 GitHub** (★由独立的 5 小时同步 job 负责★) ★

---

## ★★四 交卷前必跑 (★把原样输出贴进交卷页 B6★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

python3 HW/check_onepass_s10_swap_set_truth.py                 # 新闸 ⇒ rc=0
python3 HW/check_onepass_s10_swap_set_truth.py --selftest       # 新闸自测 ⇒ rc=0 (末行 ALL TESTS PASS)
python3 state/merge.py                                          # rc=0
python3 state/gate_check.py                                     # rc=0 (★Q1 必须 18/18★)
python3 state/check_brief_commands.py                           # rc=0
grep -c check_onepass_s10_swap_set_truth state/gate_check.py    # ⇒ 0 (零挂链自证)
md5sum HW/PCB/demo_mainboard.kicad_pcb                          # ⇒ 611b869e13518c3c023fb178f91a0075
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb                 # ⇒ 2026-11-06 07:07:17.362193413 4940213
```

★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS373_S10换件集合唯一真源与口径闸.md` (★**B1~B6 六段齐全** + 验收线逐条判定 + 落盘清单 + 沙盒留证路径★) ⇒ ★**§B5 要写明「要 main 裁的事」逐条 (★要谁回答什么★), 其中第 1 条必须是「`J_DEBUG` 那一趟换不换 land」★**

★**★收工后回卷 (★按老规矩★)★★**: ★**交卷摘要 + 必跑命令的 rc + 三件交付物路径 + 边界自证 + 要 main 裁的事 (逐条写清「要谁回答什么」)★**

---

## ★★五 你必须自己复算、**不许抄**的五个数 (★main 已算过一遍, 但你要自己重跑并贴你的输出★) ★★

1. ★**C4 集合件数** (★`158`★) + ★**ISS-356 靶子件数** (★`78`★) + ★**缺口件数** (★`13`★) ★
2. ★**`inter` 件数** (★`77`★) ⇒ ★**90 = inter + gap** ★
3. ★**`iss - inter - gap` 的完整名单** (★main 实算 = `['J_DEBUG']` · 一件★) ⇒ ★**91 = iss + gap** ★
4. ★**`J_DEBUG` 换官方 land 后的实测**: ★**land pitch / 铜箔 X 宽 / fab 外框** (★沙盒 S2 实测, ★不是抄 `.kicad_mod` 的字面★) ★
5. ★**S0 / S1 / S2 三轮的 C1/C2/C3/C4 读数 + 段数/过孔数/零铜网/单边零铜对** (★★`zero_copper` 与 `diff_over` 两个数必须都报, 不许只报一个★ ★)

★**★主命令 (★本机实测存在, 你自己再验一遍★)★★**:

```bash
# 集合口径自算 (★照抄下面这段, 只读 import, 不改任何文件★)
python3 - <<'PY'
import importlib.util, os
root=os.getcwd()
def load(n,p):
    s=importlib.util.spec_from_file_location(n, os.path.join(root,p))
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cov=load("cov","HW/check_fp_truth_coverage_gap.py"); mech=load("mech","MECH/check_onepass_s10_fp_swap_impact.py")
bom=cov.load_bom(os.path.join(root,"HW","BOM_v1.csv"))
c4=set(cov.netlist_placeholder(os.path.join(root,"HW","netlist_v1.csv")))
iss=set(mech.read_iss356_targets(root)); gap=cov.coverage_gap(bom,c4); inter=iss&c4
print("C4",len(c4),"iss356",len(iss),"inter",len(inter),"gap",len(gap))
print("差集",sorted(iss-inter-set(gap)))
print("90集",len(inter)+len(gap),"91集",len(iss)+len(gap))
PY

# 板面读数 (★本机 KiCad 10.0.8★)
bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print('; '.join('%s pitch=%.4f'%(r,(lambda c:c[1]-c[0])(sorted(set(round(pcbnew.ToMM(p.GetPosition().x),4) for p in [f for f in b.GetFootprints() if f.GetReference()==r][0].Pads())))) for r in ('J_DEBUG','J_UART')))"

# 四道真闸 (★只读, 复跑确认零漂移★)
python3 HW/check_fp_libid_truth.py
python3 HW/check_fp_truth_land_swap.py
python3 MECH/check_onepass_s10_fp_swap_impact.py
python3 MECH/check_onepass_s10_led_spec_sync.py
```

★**★最后一句纪律 (★main 2026-11-23 23:0x 追加★)★★**: ★**「90 vs 91」不是一个排版问题, 是「那一趟会不会漏换一件、漏换 ⇒ 板 md5 变第二次」的开关 ⇒ ★**你这一单的价值不在于把两个数说清楚, 而在于【把「到底换几件」变成一条谁也改不掉的机器判据】★ ★
