# HW/PCB · ISS-373 · 「板那一趟」S10 换件集合的**唯一真源** + 口径机器闸

> ★**单号**: ISS-373 · ★**owner**: hw-lead (硬件总工) · ★**性质**: 纯分析 / 新建一页 + 新建一条闸 / 沙盒预演 / **零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代老板拍板 · 不代 main 拍** ★
> ★**本单只做 1 件**: 把「S10 那一趟到底换几件」这条跨三个域、四个页面、四套口径的悬案, 收成**一个可复跑的集合真源 + 一条谁也改不掉的机器判据** ★
> ★**配套机器闸**: `HW/check_onepass_s10_swap_set_truth.py` (L0~L8 + `--selftest` ≥8 条反向用例) ★
> ★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS373_S10换件集合唯一真源与口径闸.md` ★
> ★**沙盒留证**: `tmp/iss373_sbx/` (板副本 + 工具) + `logs/iss373/` (JSON + 文本 + DRC) ★
> ★**本页所有数字均由本机脚本实算生成, 每个数字带复跑命令; 零转述, 零抄 agent 报告** ★

<!-- BEGIN ISS373 S10 换件集合真源机器块 -->
```json
{
 "issue": "ISS-373",
 "owner": "hw-lead",
 "doc": "HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md",
 "gate": "HW/check_onepass_s10_swap_set_truth.py",
 "note": "★本块由 tmp/iss373_sbx/tools/probe_sets.py 从真源实算生成; 闸 L0 校验 counts 与脚本实算逐项相等, L1 校验差集恰为 1 件且与脚本算出的差集逐件相等, L3 逐条校验四处口径的路径+行号+那个数, L4 校验 J_DEBUG 四条腿齐全并交叉引到 B33_PIN_LAND_1P27, L5 校验写库名联动的四个数, L6 校验板面三项指纹, L7 校验证据等级与零挂起措辞, L8 校验本闸零挂链★",
 "counts": {
  "c4_total": 158,
  "iss356_main_board_total": 78,
  "inter_total": 77,
  "gap_total": 13,
  "set90_total": 90,
  "set91_total": 91,
  "diff_total": 1,
  "board_footprints": 186
 },
 "sets": [
  {
   "id": "90",
   "algo": "(ISS-356 靶子 ∩ C4) + 缺口 = 77 + 13",
   "total": 90,
   "contains_jdebug": false,
   "repro": "python3 tmp/iss373_sbx/tools/probe_sets.py"
  },
  {
   "id": "91",
   "algo": "(ISS-356 靶子全体) + 缺口 = 78 + 13",
   "total": 91,
   "contains_jdebug": true,
   "repro": "python3 tmp/iss373_sbx/tools/probe_sets.py"
  }
 ],
 "diff": {
  "algo": "set91 - set90",
  "count": 1,
  "refs": ["J_DEBUG"]
 },
 "four_sources": [
  {
   "id": "①",
   "path": "MECH/check_onepass_s10_fp_swap_impact.py",
   "line": 452,
   "number": 90,
   "kind": "集合定义",
   "quote": "set90 = sorted(set(in_target) | set(gap))",
   "live_check": "python3 MECH/check_onepass_s10_fp_swap_impact.py --json",
   "live_kind": "m1_json",
   "live_key": "results.facts.set90_total"
  },
  {
   "id": "②",
   "path": "HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md",
   "line": 1384,
   "number": 90,
   "kind": "集合定义",
   "quote": "本单的对象 90 件 | 靶内 77 + 缺口 13 = 90",
   "live_check": "python3 tmp/iss373_sbx/tools/probe_sets.py",
   "live_kind": "gate_set90",
   "live_key": "counts.set90_total"
  },
  {
   "id": "③",
   "path": "MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md",
   "line": 125,
   "number": 91,
   "kind": "敏感度算例",
   "quote": "AFTER (全部 91 件靶子都换) | 2200 | 2200/2237/2250/2167",
   "live_check": "python3 tmp/iss373_sbx/tools/led_sensitivity_90_vs_91.py",
   "live_kind": "gate_set91",
   "live_key": "sets[1].n_placeable"
  },
  {
   "id": "④",
   "path": "MECH/check_onepass_s10_led_spec_sync.py",
   "line": 301,
   "number": 91,
   "kind": "敏感度算例",
   "quote": "allrefs = sorted(tmap.keys())",
   "live_check": "python3 MECH/check_onepass_s10_led_spec_sync.py --compute",
   "live_kind": "m4_compute",
   "live_key": "swap_all90_n"
  }
 ],
 "jdebug_legs": [
  {
   "leg": 1,
   "claim": "J_DEBUG 不在 C4 的 158 件里",
   "how": "C4 = state/check_pcb_nets.py 的 netlist_placeholder(netlist_v1.csv) 口径, 实测 158, J_DEBUG 不在其中",
   "evidence": "[实测]"
  },
  {
   "leg": 2,
   "claim": "J_DEBUG 在 ISS-356 靶子 78 件里",
   "how": "HW/FP_TRUTH_BASELINE.md 的 ISS356 基准块 records 共 78 条, 含 J_DEBUG (target_lib = Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical)",
   "evidence": "[实测]"
  },
  {
   "leg": 3,
   "claim": "B33_PIN_LAND_1P27 要求那一趟必须动 J_DEBUG 的 land",
   "how": "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md:63 的 B33 行原文",
   "evidence": "[实测]"
  },
  {
   "leg": 4,
   "claim": "ISS-369 表 B 给 J_DEBUG 的「不写」理由与腿 3 冲突",
   "how": "HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md:1810 的 J_DEBUG 行原文",
   "evidence": "[实测]"
  }
 ],
 "libid_linkage": {
  "formula": "写库名件数 = 换 land 件数 + 只写库名件数(4 件 J_SOM_P1~P4) ; 不写库名件数 = 186 - 写库名件数",
  "if_set90": {"table_a": 90, "table_b": 96, "write": 94, "not_write": 92},
  "if_set91": {"table_a": 91, "table_b": 95, "write": 95, "not_write": 91},
  "c4_impact": "0 (J_DEBUG 不在 C4 的 158 件里 ⇒ 两条路 C4 都恒 158)"
 },
 "paths": [
  {
   "id": "A",
   "name": "换 90 件 (不含 J_DEBUG)",
   "判据": "B33_PIN_LAND_1P27 的期望读数 (J_DEBUG land pitch = 1.27) 在这一趟之后仍然达不到 ⇒ B33 判红",
   "事实": "沙盒 S1 实测: 板副本 md5 33ca83951579b8f9950648278b46e321, C3 不符 7 个, DRC 违规 778 / 未连接 120; MECH 侧 §1.6 那行 2200 作废, 90 件口径实算 = 2206 / 2243 / 2256 / 2174"
  },
  {
   "id": "B",
   "name": "换 91 件 (含 J_DEBUG)",
   "判据": "B33_PIN_LAND_1P27 的期望读数 (J_DEBUG land pitch = 1.27) 在这一趟之后达到 ⇒ 须用官方 1.27mm THT land 且封装须转 90°",
   "事实": "沙盒 S2b 实测: 板副本 md5 38044cb8fcef5ca97302bc74a32afad9, land pitch = 1.27, 铜箔 X 宽 4.810, fab 外框 5.08×2.10, DRC 违规 848 / 未连接 122 (比 S1 多 70 / 多 2), hole_to_hole 由 0 变 4"
  }
 ],
 "board_fingerprint": {
  "path": "HW/PCB/demo_mainboard.kicad_pcb",
  "md5": "611b869e13518c3c023fb178f91a0075",
  "mtime": "2026-11-06 07:07:17.362193413",
  "size": 4940213
 },
 "sandbox": {
  "dir": "tmp/iss373_sbx/",
  "logs": "logs/iss373/",
  "boards": {
   "S0": "s0_board.kicad_pcb",
   "S0b_roundtrip": "s0b_roundtrip.kicad_pcb",
   "S1": "s1_board_90.kicad_pcb",
   "S2a": "s2a_board_91_naive_rot0.kicad_pcb",
   "S2b": "s2b_board_91_rot90.kicad_pcb"
  }
 }
}
```
<!-- END ISS373 S10 换件集合真源机器块 -->

---

## §0 口径表 (★两套算法 · 每个数带复跑命令★)

★**本页只承认两套集合口径, 且两套都写死算法式; 数字一律由脚本实算, 闸 L0 会当场对不上就判红** ★

| 集合 | 算法式 | 件数 | 含 `J_DEBUG` ? | 复跑命令 |
|---|---|---|---|---|
| ★**90** ★ | ★**`(ISS-356 靶子 ∩ C4) + 缺口` = 77 + 13** ★ | ★**90** ★ | ★**否** ★ | `python3 tmp/iss373_sbx/tools/probe_sets.py` |
| ★**91** ★ | ★**`(ISS-356 靶子全体) + 缺口` = 78 + 13** ★ | ★**91** ★ | ★**是** ★ | `python3 tmp/iss373_sbx/tools/probe_sets.py` |

★**两套口径的差 = 恰好 `J_DEBUG` 一件** ★ (★差集算法 = `set91 - set90`; 闸 L1 校验差集恰为 1 件且与脚本算出的差集逐件相等★)

### §0.1 本机实算脚本片段 (★本单原样跑, 输出为原文★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 tmp/iss373_sbx/tools/probe_sets.py
```

★**本机实测输出 (2026-11-23 23:2x, 原样贴) ★**:

```
C4 158 / iss356 78 / inter 77 / gap 13
差集 (91 - 90) = ['J_DEBUG']
90 集 = 90   91 集 = 91
目标库名覆盖: 91 件 / 缺库文件 0 件
```

★**等价的手写复算片段 (★只读 import 既有闸, 不改任何文件★; 复跑命令与上面同一行) ★**:

```python
import importlib.util, os
root = os.getcwd()
def load(n, p):
    s = importlib.util.spec_from_file_location(n, os.path.join(root, p))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cov  = load("cov",  "HW/check_fp_truth_coverage_gap.py")
mech = load("mech", "MECH/check_onepass_s10_fp_swap_impact.py")
bom  = cov.load_bom(os.path.join(root, "HW", "BOM_v1.csv"))
c4   = set(cov.netlist_placeholder(os.path.join(root, "HW", "netlist_v1.csv")))
iss  = set(mech.read_iss356_targets(root))
gap  = cov.coverage_gap(bom, c4)
inter = iss & c4
print("C4", len(c4), "iss356", len(iss), "inter", len(inter), "gap", len(gap))
print("差集", sorted(iss - inter - set(gap)))
print("90集", len(inter) + len(gap), "91集", len(iss) + len(gap))
```

★**本机实测输出 (原样贴) ★**:

```
C4 158 iss356 78 inter 77 gap 13
差集 ['J_DEBUG']
90集 90 91集 91
```

★**⇒ 本机复算结果与派活书 §一 给的四个数 (158 / 78 / 13 / 77) 与两个结论 (90 / 91) 【逐字相等】★ ⇒ ★**本单与派活书在数上零分歧; 分歧只可能出现在「哪个数才是那一趟该用的数」这条裁决上, 而那条是 main 的裁决权** ★

### §0.2 三个集合的口径定义 (★谁是权威★)

| 集合 | 定义 | 权威来源 | 件数 | 复跑命令 |
|---|---|---|---|---|
| ★**C4** ★ | 板面占位脚号器件清单 (网表节点串是 bare ⇒ 焊盘号按行序占位) | `state/check_pcb_nets.py` 的 C4 口径 | ★**158** ★ | `bash state/pcbnew_py.sh state/check_pcb_nets.py` |
| ★**ISS-356 靶子 (本板)** ★ | 必装 ∩ 非 NET/TP ∩ BOM `footprint` 栏 = 待定 | `HW/FP_TRUTH_BASELINE.md` 的 ISS356 基准块 `records` | ★**78** ★ (全项目 100 = 本板 78 + 充电板 22) | `python3 HW/check_fp_truth_baseline.py` |
| ★**缺口** ★ | C4 158 − (TP 42 + DNP 26 + 靶内 77) | `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` 的 `gap_refs` | ★**13** ★ | `python3 tmp/iss373_sbx/tools/probe_sets.py` |

★**板面封装总数 186** (★186 = 90 + 96 = 91 + 95, 两条路都对得上★) —— 复跑 `python3 tmp/iss369/tools/parse_board.py` ★

---

## §1 四处口径逐条对表 (★同一件事, 四个地方写的不是一个数★)

★**本节要判清的核心问题: `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` 里那个「91」到底是【集合定义】还是【§1.6 敏感度算例的一行】★**

| # | 文件 | 行 | 它写的数 | 它是**集合定义**还是**敏感度算例** | 本机实读原文 | 判读 |
|---|---|---|---|---|---|---|
| ★**①** ★ | `MECH/check_onepass_s10_fp_swap_impact.py` | ★**452** ★ (另见 :6) | ★**90** ★ | ★**集合定义** ★ | `set90 = sorted(set(in_target) \| set(gap))` (★`in_target` = 靶子 ∩ C4 = 77★) | ★**这一套的 90 是真 90** ★; 实跑 `--json` ⇒ `facts.set90_total = 90` / `in_target_total = 77` / `gap_total = 13` [实测] |
| ★**②** ★ | `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` | ★**1384** ★ (另见 :1375=186 · :1382=158 · :1385=96 · :1386=94 · :1387=92) | ★**90 / 96 / 186 / 158** ★ | ★**集合定义** ★ | 「本单的对象 90 件 \| 靶内 77 + 缺口 13 = 90」 | ★**与 ① 同算法 (交集 + 缺口) ⇒ 同为 90** ★ [实测] |
| ★**③** ★ | `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` | ★**125** ★ (★小节标题在 :119★) | ★**91** ★ | ★**敏感度算例 (★不是集合定义★)** ★ | 「AFTER (全部 91 件靶子都换) \| 2200 \| 2200/2237/2250/2167」 | ★**★本单的核心判断: ③ 的「91」是 §1.6 那张表里的【一行敏感度算例】, 不是集合定义; 但 ③ 自己的小节标题 (:119) 写的是「若那一趟把 90 件全换」⇒ ⇒ 【同一页里 90 与 91 并存, 且标题按 90 / 表行按 91】⇒ 这是真矛盾, 不是排版★** ★ [实测] |
| ★**④** ★ | `MECH/check_onepass_s10_led_spec_sync.py` | ★**301** ★ (算式) · ★**311** ★ (输出键名) | ★**91** ★ | ★**敏感度算例 (★且变量名错了★)** ★ | :301 `allrefs = sorted(tmap.keys())` · :311 `"swap_all90_n": len(used90),` | ★**★`tmap` = `read_iss356_targets()` 78 条 ∪ `read_gap_targets()` 13 条 = 91 条 ⇒ `allrefs` 是 91 件 ⇒ `swap_all90_n` 实算 = 91 ⇒ 【变量名写着 90, 实算的是 91】★** [实测] |

### §1.1 ★★两套口径的根因 (★本单最硬的一条结论★) ★★

★**④ 的 `target_map()` (★`MECH/check_onepass_s10_led_spec_sync.py:223-226`★) 是这样写的** ★:

```python
def target_map(root, fp_gate):
    tgt = dict(fp_gate.read_iss356_targets(root))   # ★ISS-356 靶子 78 件 (含 J_DEBUG)★
    tgt.update(fp_gate.read_gap_targets(root))        # ★缺口 13 件★
    return tgt
```

★**⇒ `tmap` = 78 + 13 = 91 条, `allrefs` = 91 ⇒ ④ 实算的敏感度集合就是「91 件口径」; 而 ①② 的 90 = (靶子 ∩ C4) + 缺口 = 77 + 13 ⇒ 两套口径的差 = 靶子里不在 C4 的那 1 件 = `J_DEBUG` ★** [实测]

★**⇒ ⇒ ★★「90 vs 91」不是一个排版问题, 是【④ 的变量名 (`swap_all90`) 与它实算的集合 (91) 差 1 件】★; ③ 那一行 2200 其实是【91 件口径】算出来的, 却挂在【90 件】的标题下 ⇒ ★★** 那一趟若按 91 件换, ③ 的 2200 成立; 若按 90 件换, ③ 的 2200 作废 ⇒ ⇒ **③ 那一行其实在给「91 件」那条路背书, 却在「90 件」的标题下** ★★**

### §1.2 ★★本机实算: 两套口径在 MECH 侧落位块数上的实测差 (★§2.⑤ 两条路代价表的 MECH 那一列的来源★) ★★

★**做法: 只读 import `MECH/check_onepass_s10_led_spec_sync.py` 的 `swap_set()` / `led_space()` / `summarize()` (★判据函数零漂移★), 只把 refs 集合换掉, 跑同一套 `led_space()` ★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 tmp/iss373_sbx/tools/led_sensitivity_90_vs_91.py
```

★**本机实测输出 (原样贴, 2026-11-23 23:3x) ★**:

```
BEFORE  n_placeable=1992 sweep=[1992, 2016, 2031, 2075] bands=[{'x0': 1.55, 'x1': 3.45, ...}, {'x0': 72.54, 'x1': 73.66, ...}]
25件_S10_MECH_REFS            refs=25 swapped=25 n_placeable=2183 sweep=[2183, 2241, 2253, 2197]
91件_ISS356靶子全体+缺口       refs=91 swapped=91 n_placeable=2200 sweep=[2200, 2237, 2250, 2167]
90件_靶子∩C4+缺口             refs=90 swapped=90 n_placeable=2206 sweep=[2206, 2243, 2256, 2174]
tmap=91  tmap-set90=['J_DEBUG']  tmap-set91=[]
```

★**⇒ 三行逐位对上了 ③ 那张表**: 25 件口径 = 2183/2241/2253/2197 ✔ · 91 件口径 = 2200/2237/2250/2167 ✔ ⇒ ★**③ 的 §1.6 那一行确实是 91 件口径的算例** ★ [实测]

★**⇒ ★★而「90 件口径」的落位块数 = 2206 / 2243 / 2256 / 2174 —— ★★全项目没有任何一页写过这个数★★ ⇒ ⇒ **那一趟若走 90 件这条路, MECH 侧两处机器块 + `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 LED 窗口规格, 要按 2206 / 2243 / 2256 / 2174 重写 (而不是按 2200)★** [实测]

★**⇒ ★★方向值得记一笔: ★不换 `J_DEBUG` ⇒ 它的旧占位 land (0.275×0.900 SMD) 留在板上 ⇒ 占地方更小 ⇒ 可落位块【反而多 6 个】(2206 > 2200) ⇒ 【漏换的代价不是「少一块」, 是「MECH 侧全部数按错的那个数走」】★★** [实测]

---

## §2 `J_DEBUG` 一件的完整账 (★四条腿 + 两条路各自的后果★)

### §2.1 四条腿 (★逐条给判据与证据★)

| 腿 | 问题 | 本机实读结论 | 依据 | 证据等级 |
|---|---|---|---|---|
| ★**①** ★ | `J_DEBUG` 在不在 C4 的 158 件里 ? | ★**不在** ★ | `C4 = netlist_placeholder(HW/netlist_v1.csv)` 实测 158 件, `J_DEBUG` 不在其中 (★它的网表节点串是具名的 `pin1..pin4` ⇒ 不算占位脚号★) | ★[实测] ★ |
| ★**②** ★ | 在不在 ISS-356 靶子 78 件里 ? | ★**在** ★ | `HW/FP_TRUTH_BASELINE.md` 的 ISS356 基准块 `records` 共 78 条, 含 `J_DEBUG` (★`target_lib` = `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical`★); §2 逐 ref 表第 166 行也有它 | ★[实测] ★ |
| ★**③** ★ | `B33_PIN_LAND_1P27` 要不要动它的 land ? | ★**要** ★ | `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md:63` 原文: 「★**`J_DEBUG`/`J_UART` 排针 land pitch 0.50→1.27mm (E-1 · 实测排针落不进 · main 11-17 18:45 拍死)**★」+ 同页 JSON 块 (:544~:549) 的 `action` 写「★那一趟把 `J_DEBUG`(1×4) 与 `J_UART`(1×2) 的 land pitch 从 0.50 改成 1.27 ★…★ 与 S4 的 ESD 挪位、S6 的 `Q_PG`/`Q_AND` land 重画同一次布局里做完 ⇒ 板 md5 只许变一次★」 | ★[实测] ★ |
| ★**④** ★ | ISS-369 说「不写库名」的理由是什么 ? | ★**引原文见下, 且它与 ③ 冲突** ★ | `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md:1810` 原文: 「★`J_DEBUG` \| 靶内-非C4 \| **不写** \| ★**不需要写**★ \| — \| BOM footprint 栏 = 「待定」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; **且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land** ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写 | [实测] ★」 | ★[实测] ★ |

★**★腿 ④ 与腿 ③ 的冲突点 (★本单要点名的那个矛盾★) ★★**:

- ★腿 ④ 的推理链 = 「★因为它**不在** 90 件换 land 名单里 ⇒ 本趟**不动**它的 land ⇒ 所以**不写**库名★」⇒ ★**它的前提正是腿 ③ 所否的那件事 (B33 说本趟**要**动它的 land)** ⇒ ⇒ **前提与 B33 冲突 ⇒ 这一行的「不写」结论在「本趟换 91 件」这条路上不成立** ★ [推算]
- ★腿 ④ 还有一个**已过期**的前半句: 「★BOM footprint 栏 = 「待定」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板★」⇒ ★**这一条已被 B33 (★main 2026-11-17 18:45 拍死★) + ISS-356 §1 的 `J_DEBUG` 族 (★目标 `lib:name` 已定 + 库文件 md5 `7a5f470c1f70d4b832be258501945385` 已锁★) 推翻 ⇒ ⇒ **「选型未定」这个理由已不成立** ⇒ **腿 ④ 的两半理由, 前半已过期, 后半与 B33 冲突** ★ [推算]

### §2.2 ★★两条路各自的后果表 (★代价算全, 不代拍★) ★★

| 维度 | ★**路 A: 换 90 件 (不含 `J_DEBUG`)** ★ | ★**路 B: 换 91 件 (含 `J_DEBUG`)** ★ |
|---|---|---|
| 集合定义 | `(靶子 ∩ C4) + 缺口` = 77 + 13 = **90** | `(靶子全体) + 缺口` = 78 + 13 = **91** |
| `J_DEBUG` 的 land | ★**不动** ⇒ 仍是 4×SMD 0.275×0.900 @0.50 (★实测 pitch 0.50★) ★ | ★**动** ⇒ 4×THT 1.00×1.00 钻 0.65 @1.27 (★实测 pitch 1.27, 须封装转 90°★) ★ |
| ★**B33_PIN_LAND_1P27** ★ | ★**判红** ⇒ 期望读数「J_DEBUG land pitch = 1.27」永远达不到; 实物 1.27mm 排针落不进 ⇒ **板要么改第二次, 要么实物报废** ★ | ★**判绿** ⇒ B33 期望读数达到 (★实测 `J_DEBUG land pitch = 1.27`★) ★ |
| ★**MECH 侧落位块数** ★ | ★**2206 / 2243 / 2256 / 2174** ⇒ ★**③ §1.6 那行 2200 作废, MECH 两处机器块 + LED 窗口规格要按 2206 重写** ★ | ★**2200 / 2237 / 2250 / 2167** ⇒ ★**③ §1.6 那行成立, MECH 两处机器块按 2200 改** ★ |
| 库名名单 (§3) | 写 **94** / 不写 **92** (表 A 90 / 表 B 96) | 写 **95** / 不写 **91** (表 A 91 / 表 B 95) |
| ★**`J_DEBUG` 落位** ★ | 不涉及 | ★**官方 land 放不进现位**: 4 个 0.65 钻孔与板面既有过孔冲突 (★PTH pad1 vs via `JTAG_TDO`@143.70,57.95 净距 0.1271; PTH pad3 vs via `XTAL_OUT`@146.95,57.95 净距 **0.0000**★) ⇒ DRC `hole_to_hole` 由 **0 → 4** ★ |
| ★**JTAG 走线** ★ | 不涉及 | ★**4 条 JTAG 网的走线端点全部脱网** (★TMS / TDI / TDO 三条在 S2b 的 DRC 未连接项里明写「Missing connection between … PTH pad N of J_DEBUG」★) ⇒ **走线要重接** ★ |
| ★**铜箔短路** ★ | 不涉及 | ★**+12 条 `JTAG_TDI` vs `XTAL_OUT` + 1 条 `JTAG_TMS` vs `SENSOR_VDD_IO`** ⇒ 新 land 与既有走线撞铜 ★ |
| ★**零铜网** ★ | ★24 (★与 S0 相同★) ★ | ★**25** ⇒ 新增 1 条零铜网 (★`JTAG_TDO`★) ★ |
| ★**结构净宽** ★ | 不涉及 | ★**铜箔净宽实测 4.810 mm** vs MECH 侧现算的 **4.0850 mm** ⇒ ★**差 0.725 mm, 结构清空区要重算** ★ |
| ★**调试口开口** ★ | 不涉及 | ★**courtyard 落到 X 143.16..149.25 × Y 56.45..59.55** ⇒ 比原占位 fab 外框 (X 141.30..147.30) 右沿多 **1.95 mm** ⇒ MECH 调试口罩要重算 ★ |
| ★**库名那一腿** ★ | `J_DEBUG` 留在表 B「不写」⇒ **但它的 land 也不动 ⇒ 板面铜箔与库件对不上这条「假身份」风险不存在** ⇒ 逻辑自洽 | `J_DEBUG` 进表 A ⇒ **ISS-369 §3 判定口径第 1 条「换 land 的件必须同时写库名」⇒ 必须写库名** ⇒ ⇒ **但表 B 给它的「选型未定」理由已被 B33 + ISS-356 推翻 ⇒ 这一行必须改写 (追加式订正块见 §4)★** |
| ★**那一趟的额外工作量** ★ | 0 件额外 | ★**J_DEBUG 落位要挪 + 2 个过孔要挪 + 4 条 JTAG 走线要重接 + 调试口开口与结构清空区要重算 ⇒ 这一件不是「换个 land」, 是「换位置 + 重画一小块」★** |

★**★ ⇒ 两句话结论 (★只给事实, 不代拍★) ★★**:

1. ★**路 A 的代价集中在「实物与判据」**: `J_DEBUG` 排针装不上、B33 判红、实物报废风险; ★**但那一趟的板面工作量最小 (90 件, 不含 `J_DEBUG`)★**
2. ★**路 B 的代价集中在「那一趟的板面工作量」**: `J_DEBUG` 这一件连带 2 个过孔 + 4 条走线 + 1 处结构开口 + 1 处净宽口径; ★**但那一趟做完, B33 与 MECH 的 2200 都成立, 实物排针装得上★**
3. ★**★决定权在 main (★因为它同时牵动 B33 / ISS-369 两页 + MECH 侧两处机器块★)⇒ 本单只登记, 不代裁 ⇒ 见 §4★**

### §2.3 ★★沙盒三轮 (★S0 / S1 / S2) 的实测读数 (★每轮都是板副本, 真板零改动★) ★★

★**做法**: `bash state/pcbnew_py.sh tmp/iss373_sbx/tools/sbx_s10_swap.py` 在**板副本**上换 official land ⇒ 再 `bash state/pcbnew_py.sh tmp/iss373_sbx/tools/sbx_measure.py` 读数 ⇒ 真板 `HW/PCB/demo_mainboard.kicad_pcb` md5 开工前/交卷后各打一次, 逐字相同 ★

★**★pad↔net 映射口径 (★必须写清, 否则读数会被误读★) ★★**: 沙盒按★**焊盘号 1:1 继承板面旧 land 的 net** ★(★不引入 pad↔net 换序★) ⇒ 板面与网表在电气上保持等价 ⇒ **C1/C2/C3 的 Δ 只反映【几何 / 焊盘个数】, 不掺杂换序项**; ★**pad↔net 换序 (B10_Q_AND_LAND / B11_Q_PG_LAND / B13_ESD_CAM_PAD / B07_ESD_USB_D_3PIN) 是另一批改项, 不在本沙盒范围内** ★ [推算]

| 读数 | ★**S0 基线 (不换)** ★ | ★**S1 换 90 件** ★ | ★**S2a 换 91 件 (`J_DEBUG` @0°)** ★ | ★**S2b 换 91 件 (`J_DEBUG` @90°)** ★ |
|---|---|---|---|---|
| 板副本 md5 | ★`611b869e13518c3c023fb178f91a0075` ★ | ★`33ca83951579b8f9950648278b46e321` ★ | ★`be50d1a9f68dcedd4c0bb24d1ef5cb07` ★ | ★`38044cb8fcef5ca97302bc74a32afad9` ★ |
| ★**C1** ★ | ❌ 缺 0 / 多 2 / 错 3 / 非法 NC 0 | ❌ 缺 0 / 多 2 / 错 3 / 非法 NC **4** | ❌ 同 S1 | ❌ 同 S1 |
| ★**C2** ★ | ✅ **26 / 26** 全绿 | ✅ **26 / 26** 全绿 | ✅ **26 / 26** 全绿 | ✅ **26 / 26** 全绿 |
| ★**C3** ★ | ✅ 器件 185 · 不符 **0** | ❌ 器件 185 · 不符 **7** | ❌ 不符 **7** | ❌ 不符 **7** |
| ★**C4** ★ | ★**158** ★ | ★**158** ★ | ★**158** ★ | ★**158** ★ |
| 走线段数 seg | 18092 | 18092 | 18092 | 18092 |
| 过孔数 via | 433 | 433 | 433 | 433 |
| ★**zero_copper (零铜网数)** ★ | ★**24** ★ | ★**24** ★ | ★**25** ★ | ★**25** ★ |
| ★**diff_half (单边零铜对数)** ★ | ★**11** ★ | ★**11** ★ | ★**11** ★ | ★**11** ★ |
| ★**diff_over (Δ超差对数)** ★ | ★**3** ★ | ★**3** ★ | ★**3** ★ | ★**3** ★ |
| DRC 违规总数 | ★**0** ★ | ★**778** ★ | (未跑) | ★**848** ★ (★比 S1 多 70★) |
| DRC 未连接项 | ★**45** ★ | ★**120** ★ | (未跑) | ★**122** ★ (★比 S1 多 2★) |
| ★**`J_DEBUG` land pitch (B33 口径)** ★ | ★**0.50** ★ | ★**0.50** ★ | ★**读不出来** ★ (★4 个焊盘 X 全同 ⇒ B33 那条 `c[1]-c[0]` **IndexError** ⇒ 命令 rc=1★) | ★**1.27** ★ |
| ★**`J_DEBUG` 铜箔 X 宽** ★ | ★**1.775** ★ | ★**1.775** ★ | ★**1.000** ★ | ★**4.810** ★ |
| ★**`J_DEBUG` fab 外框 (绝对)** ★ | X 141.30..147.30 × Y 56.00..60.00 (**6.00 × 4.00**) | 同 S0 | X 143.25..145.35 × Y 57.365..62.445 (**2.10 × 5.08**) | X 143.665..148.745 × Y 56.95..59.05 (**5.08 × 2.10**) |
| `J_DEBUG` 焊盘 | 4×SMD 0.275×0.900 @0.50, 无钻孔 | 同 S0 | 4×THT 1.00×1.00 钻 0.65 @1.27, **沿 Y** | 4×THT 1.00×1.00 钻 0.65 @1.27, **沿 X** |

★**★三个必须写进交卷页的读数解读★**:

1. ★**S1 (换 90 件) 的 C3 不符 7 个** ⇒ ★**纯「换 land」不重画布线 ⇒ C3 当场红** (★已知项: `SW_BOOT`/`SW_KEY_PWR`/`SW_RST` 换成官方 KMR2 后 2 land 变 4 land ⇒ 板 4 脚 / 网表 2 脚, 与 `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §0 表第 12 行记载一致★) ⇒ **那一趟必须同批把网表脚号一起改, 否则这一道闸红** ★ [实测]
2. ★**S2a ⇒ S2b 的唯一差别是 `J_DEBUG` 封装的朝向, 而 B33 的读数从「IndexError / rc=1」变成「1.27」** ⇒ ★**★官方 1.27mm 排针的 4 个焊盘在库里是沿 Y 排的; 照抄 0° 装上去, 整排焊盘沿 Y 排, B33 那条判据按 X 读 pitch 会读不出数 (rc=1), 而不是读出 1.27★ ⇒ ⇒ 【那一趟必须把该封装转 90° 才能让 B33 判绿】★★** ★ [实测]
3. ★**C4 在 S0/S1/S2a/S2b 四轮恒等于 158** ⇒ ★**与 `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §0 表第 12 行的口径一致: C4 由网表节点命名决定, 与板面 land 无关 ⇒ 「换 90 件」与「换 91 件」对 C4 的贡献都 = 0★** ★ [实测]

★**★沙盒发现的、派活书里没有的三条 (★本单新增★) ★★**:

| # | 发现 | 数值 | 证据 | 复跑命令 |
|---|---|---|---|---|
| ★**新-1** ★ | ★**官方 1.27mm THT land 放不进 `J_DEBUG` 现位** ★ | PTH pad1 (144.30, 58.00) vs via `JTAG_TDO` (143.70, 57.95) 孔净距 **0.1271** (要求 ≥0.25); PTH pad3 (146.84, 58.00) vs via `XTAL_OUT` (146.95, 57.95) 孔净距 **0.0000** ⇒ DRC `hole_to_hole` 由 **0 → 4** | ★[实测] ★ | `bash state/kicad.sh pcb drc --output logs/iss373/drc_s2b_board_91_rot90.json --severity-error --severity-warning --format json tmp/iss373_sbx/sbx/s2b_board_91_rot90.kicad_pcb` |
| ★**新-2** ★ | ★**新 land 的铜箔净宽 4.810 mm 与 MECH 侧现算的 4.0850 mm 差 0.725 mm** ★ | 3×1.27 + 1.00 = 4.810 (实测) vs 3×1.27 + 0.275 = 4.0850 (MECH 侧口径) | ★[实测] + [推算] ★ | 同上 + `bash state/pcbnew_py.sh tmp/iss373_sbx/tools/sbx_measure.py` |
| ★**新-3** ★ | ★**落盘后 KiCad 连通性重建把那 63 段 `JTAG_TDO` 走线改归 `JTAG_TCK`** ★ | S1: `JTAG_TCK` 34 段 / `JTAG_TDO` 63 段 ⇒ S2b: `JTAG_TCK` **97** 段 / `JTAG_TDO` **0** 段 (★坐标逐段相同, 只换 net 名★) ⇒ **那 4 条 JTAG 走线的端点脱网 ⇒ 必须重接** | ★[实测] ★ | `python3 tmp/iss373_sbx/tools/sbx_measure.py` (读 `logs/iss373/04_sbx_measurements.json` 的 `jtag_segs`) |

★**★一条必须写清的沙盒边界 (★不许被当成板面结论★) ★★**: S1/S2a/S2b 是★**「只换 land, 不重画布线」**★ 的中间态 ⇒ ★**DRC 违规 778 / 848 里有相当一部分是「走线没跟着改」的必然结果, 不代表最终板** ★; ★**但 `hole_to_hole` / `hole_clearance` / 钻孔与过孔重合这一类【落位冲突】不是重画布线能消掉的 ⇒ 它们是「那一趟必须挪 J_DEBUG 或挪过孔」的直接证据** ★ [推算]

★**★DRC 分型 Δ (S2b − S1) ★★ (★复跑: `python3 -c "import json;d=json.load(open('logs/iss373/06_drc_summary.json'));print(d)"`★):

| 违规类型 | S0 | S1 | S2b | ★Δ(S2b−S1)★ |
|---|---|---|---|---|
| clearance | 0 | 168 | 188 | ★**+20** ★ |
| shorting_items | 0 | 180 | 192 | ★**+12** ★ |
| hole_clearance | 0 | 39 | 63 | ★**+24** ★ |
| hole_to_hole | 0 | 0 | 4 | ★**+4** ★ (★S1 里这一类为 0 ⇒ 完全是 `J_DEBUG` 带来的★) ★ |
| solder_mask_bridge | 0 | 192 | 199 | ★**+7** ★ |
| track_dangling | 0 | 70 | 73 | ★**+3** ★ |
| courtyards_overlap | 0 | 5 | 5 | +0 |
| copper_sliver | 0 | 2 | 2 | +0 |
| silk_edge_clearance | 0 | 2 | 2 | +0 |
| silk_over_copper | 0 | 29 | 29 | +0 |
| silk_overlap | 0 | 91 | 91 | +0 |
| ★**违规总数** ★ | ★**0** ★ | ★**778** ★ | ★**848** ★ | ★**+70** ★ |
| ★**未连接项** ★ | ★**45** ★ | ★**120** ★ | ★**122** ★ | ★**+2** ★ |

---

## §3 「写库名」名单的联动手 (★只给算式 + 结论口径, 不代拍★)

★**ISS-369 的判定口径原文 (`HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` §3, ★写在 §3 表前面★)**: 「★**1. 换 land 的 90 件 ⇒ 必须同时写库名** (★换 land 而不写库名 = 装配厂拿不到封装 + BOM 与板面对不上★)★」「★**2. 不动 land 的件 ⇒ 只有在【逐焊盘几何与官方件等价】时才写库名**★」「★**3. 其余 ⇒ 不写**★」 ★

★**⇒ 算式 (★只有一条, 两套口径都套它★) ★**:

```
写库名件数   = 换 land 件数 + 只写库名件数(4 件 J_SOM_P1~P4)
不写库名件数 = 186 - 写库名件数
表 A 件数    = 换 land 件数
表 B 件数    = 186 - 表 A 件数
```

| 口径 | 表 A (换 land + 写库名) | 表 B (其余) | ★**写库名** ★ | ★**不写库名** ★ | 依据 |
|---|---|---|---|---|---|
| ★**现状 (换 90 件)** ★ | 90 | 96 | ★**94** ★ | ★**92** ★ | `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` §0 表第 12 / 13 行 (★实算·与本单复算逐字相等★) |
| ★**若 `J_DEBUG` 进换 land 名单 (换 91 件)** ★ | 91 | 95 | ★**95** ★ | ★**91** ★ | ★**本单算式实算**: 91 + 4 = 95 ; 186 − 95 = 91 ; 91 + 95 = 186 ✔ ★ |

★**★对 C4 的影响 = 0 (★两条路都成立★) ★★**: `J_DEBUG` 不在 C4 的 158 件里 (★腿 ①★) ⇒ 它进不进换 land 名单都动不了 C4 ⇒ ★**C4 恒 158 (★沙盒 S0/S1/S2a/S2b 四轮实测逐字相等✔★)** ★

★**★一条必须一起改的连带项 (★不代拍, 只登记★) ★★**: `J_DEBUG` 若进换 land 名单 ⇒ 按 ISS-369 §3 判定口径第 1 条必须同时写库名 ⇒ ★**表 B 里 `J_DEBUG` 那一行 (★:1810★) 的「不写」结论必须改写**, 而它给的两半理由分别要这样处理: ★**前半「选型/封装未落定 ⇒ 写库名 = 拍板」⇒ 已被 B33 (2026-11-17 18:45) + ISS-356 §1 锁死目标封装所推翻 ⇒ 该理由过期** ★; ★**后半「不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land」⇒ 与 B33 正面冲突 ⇒ 若走 91 件这条路, 该前提不再成立** ★。★**⇒ 追加式订正块写在 §4, 由 main 决定要不要往既有页面落 (★本单不改既有页面一个字★)** ★

---

## §4 未决项 (★只登记 · 给代价 · 不代老板拍 · 不代 main 拍★) + 追加式订正块

### §4.1 要 main 裁的事 (★第 1 条是本单的正题★)

| # | 未决项 | 两条路的代价 | 要谁回答什么 | 关联闸 |
|---|---|---|---|---|
| ★**1** ★ | ★**★「那一趟 `J_DEBUG` 换不换 land」★** ★ | 路 A (90): 排针装不上 + B33 判红 + 实物报废风险 + MECH 侧数要按 **2206** 重写 · 路 B (91): `J_DEBUG` 落位要挪 + 2 个过孔要挪 + 4 条 JTAG 走线要重接 + 调试口开口与结构清空区要重算 | ★**main** ★ (★它同时牵动 B33 / ISS-369 两页 + MECH 侧两处机器块★) | `HW/check_onepass_s10_swap_set_truth.py` L1 / L4 |
| ★**2** ★ | ★**若走 91 件 ⇒ ISS-369 表 B 的 `J_DEBUG` 行 (:1810) 怎么改写** ★ | 改写 = 追加式订正块 (★本单已写好, 见 §4.2★) ⇒ 既有页面一个字不动, 由 main 决定是否落 | ★**main** ★ | L4 |
| ★**3** ★ | ★**若走 91 件 ⇒ `J_DEBUG` 的落位挪到哪** ★ | ★**官方 land 放不进现位** (孔净距 0.0000 / 0.1271) ⇒ 要么挪 `J_DEBUG`, 要么挪 `XTAL_OUT` / `JTAG_TDO` 两个过孔 ⇒ 都要 MECH 侧确认调试口开口位置 | ★**main** + ★**mech-lead** ★ | 沙盒 S2b |
| ★**4** ★ | ★**MECH 侧 §1.6 那行 2200 的标题与表行口径不一致 (★标题按 90 / 表行按 91★)** ★ | 改法二选一: ① 标题改成「91 件口径」并把 91 件写进标题; ② 另算并补一行 90 件口径 (★2206 / 2243 / 2256 / 2174★) ⇒ **本单已把 90 件口径的数算出来放着** | ★**main** + ★**mech-lead** ★ | L3 (③) |
| ★**5** ★ | ★**MECH/check_onepass_s10_led_spec_sync.py 的变量名 `swap_all90` / `swap_all90_n` 与它实算的 91 件不符** ★ | 改名 = 改既有闸的一个字节 ⇒ **本单零改既有闸, 只登记** ⇒ 但不改名, 下一趟还会有人把 91 当 90 | ★**main** ★ (★该文件归 MECH 域★) | L3 (④) |
| ★**6** ★ | ★**那一趟的网表脚号同步 (★C3 红 7 件★)** ★ | 官方 KMR2 是 4 个物理焊盘 (1,1,2,2) ⇒ 板 4 脚 / 网表 2 脚 ⇒ **网表必须同批给 4 个具名脚** (★零落表 ⇒ 本单只登记★) | ★**main** (★落表是 main 的地界★) | `state/check_pcb_nets.py` C3 |

### §4.2 追加式订正块 (★供 main 决定要不要往既有页面落; ★本单不改既有页面一个字★)

> ★**订正块 A · 目标页: `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` §1.6** ★
> ★**订正内容**: §1.6 的小节标题写「★若那一趟把 90 件全换★」, 而同节的表行写「★AFTER (全部 91 件靶子都换) ⇒ 2200 / 2200-2237-2250-2167★」⇒ ★**该行的数是 91 件口径算出来的 (本单本机复算逐位相等), 标题却按 90 件 ⇒ 标题与表行口径不一致** ★ ⇒ ★**建议改法: 把标题里的「90 件」改成「91 件」, 并把 §4.2 的「91 件靶子全换 ⇒ 块数 2183→2200」保留; 若那一趟最终走 90 件, 则另补一行 90 件口径 (★2206 / 2243 / 2256 / 2174, 本单已实算★)** ★ [实测]

> ★**订正块 B · 目标页: `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` §3.2 表 B 的 `J_DEBUG` 行 (:1810)** ★
> ★**订正内容 (只在「那一趟走 91 件」时才需要落)**: 该行现写「靶内-非C4 \| **不写** \| 不需要写 \| BOM footprint 栏 = 「待定」⇒ 选型/封装未落定 ⇒ 写库名 = 拍板; 且本件不在 ISS-364 的 90 件换 land 名单里 ⇒ 本趟不动它的 land ⇒ 写库名会让板面铜箔与库件对不上 (假身份) ⇒ 不写」⇒ ★**前半「选型/封装未落定」已被 B33 (2026-11-17 18:45 拍死目标 land) + ISS-356 §1 (目标 `lib:name` = `Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical`, 库文件 md5 `7a5f470c1f70d4b832be258501945385`) 推翻; 后半「不在 90 件换 land 名单里 ⇒ 本趟不动它的 land」与 B33 正面冲突** ★ ⇒ ★**若那一趟换 91 件, 该行应移入表 A (换 land + 写库名), 写库名件数随之 94 → 95 / 92 → 91** ★ [实测]

> ★**订正块 C · 目标页: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 判据栏** ★
> ★**订正内容**: 该判据用「板面焊盘 X 坐标的前两个唯一值之差」当 pitch ⇒ ★**官方 1.27mm 排针的焊盘在库里沿 Y 排 ⇒ 若照抄 0° 装上去, 4 个焊盘的 X 全同 ⇒ 该判据不是读出 0.50 或 1.27, 而是 **IndexError / rc=1** (★沙盒 S2a 实测★)** ⇒ ★**建议在判据栏补一句「★该封装必须转 90° (1×4 直排沿 X) 才读得出 pitch★」** ★ [实测]

---

## §5 复跑命令 (★每个数字都能被下面某一条复现★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ---- ① 集合口径自算 (★§0 的 90 / 91 / 差集 / 三个集合件数★) ----
python3 tmp/iss373_sbx/tools/probe_sets.py

# ---- ② MECH 侧两套口径的落位块数实测 (★§1.2 的 1992 / 2183 / 2200 / 2206★) ----
python3 tmp/iss373_sbx/tools/led_sensitivity_90_vs_91.py

# ---- ③ 沙盒三轮 (★只落 tmp/iss373_sbx/ + logs/iss373/ · 真板零改动★) ----
bash state/pcbnew_py.sh tmp/iss373_sbx/tools/sbx_s10_swap.py
bash state/pcbnew_py.sh tmp/iss373_sbx/tools/sbx_measure.py

# ---- ④ B33 判据原样跑在板副本上 (★S0 / S2a / S2b 三块★) ----
bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('tmp/iss373_sbx/sbx/s2b_board_91_rot90.kicad_pcb');print('; '.join('%s land pitch = %.2f'%(r,(lambda c:c[1]-c[0])(sorted(set(round(pcbnew.ToMM(p.GetPosition().x),4) for p in [f for f in b.GetFootprints() if f.GetReference()==r][0].Pads())))) for r in ('J_DEBUG','J_UART')))"

# ---- ⑤ DRC 分型 (★§2.3 的 DRC 表★) ----
bash state/kicad.sh pcb drc --output logs/iss373/drc_s2b_board_91_rot90.json --severity-error --severity-warning --format json tmp/iss373_sbx/sbx/s2b_board_91_rot90.kicad_pcb
python3 -c "import json;print(json.load(open('logs/iss373/06_drc_summary.json',encoding='utf-8')))"

# ---- ⑥ 四处口径的活体检 (★§1 的四个数★) ----
python3 MECH/check_onepass_s10_fp_swap_impact.py --json
python3 MECH/check_onepass_s10_led_spec_sync.py --compute

# ---- ⑦ 本单新闸 (★L0~L8 + 反向用例★) ----
python3 HW/check_onepass_s10_swap_set_truth.py
python3 HW/check_onepass_s10_swap_set_truth.py --selftest

# ---- ⑧ 零写板自证 (★板三项指纹★) ----
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
```

★**留证路径**: 集合自算 `tmp/iss373_sbx/sets.json` · 沙盒换件报告 `logs/iss373/02_sbx_swap_report.json` · 沙盒读数 `logs/iss373/04_sbx_measurements.json` · 沙盒日志 `logs/iss373/05_sbx_measure.log` · DRC 分型 `logs/iss373/06_drc_summary.json` + `logs/iss373/drc_*.json` · LED 敏感度 `logs/iss373/07_led_sensitivity_90_vs_91.json` ★

---

## §6 边界自证 (★本单开了什么、没开什么★)

| 边界 | 自证 | 证据等级 |
|---|---|---|
| ★**零写板** ★ | 板 `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 三项, **开工前 / 交卷后各打一次, 逐字相同**; 沙盒只在 `tmp/iss373_sbx/sbx/` 上做 | ★[实测] ★ |
| ★**零落表** ★ | 网表 `6aee500e60ba0732f83a9cf557ba90ab` · BOM `5b9993992405904a60ac96a020b375d8` · 脚表只读, md5 未变 | ★[实测] ★ |
| ★**零改既有闸** ★ | `HW/check_fp_libid_truth.py` · `HW/check_fp_truth_land_swap.py` · `HW/check_fp_truth_coverage_gap.py` · `HW/check_onepass_preflight_coverage.py` · `MECH/check_onepass_s10_fp_swap_impact.py` · `MECH/check_onepass_s10_led_spec_sync.py` · `MECH/check_jdebug_1p27_clearance.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` —— 十个文件 md5 开工前后逐字相同 (★逐个数见交卷页 B6★) | ★[实测] ★ |
| ★**零改既有页面正文** ★ | `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md` · `MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md` · `MECH/BOARD_ONEPASS_MECH_SYNC.md` · `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` · `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` —— 八个文件 md5 开工前后逐字相同; ★**要订正的部分一律写成 §4.2 的追加式订正块, 由 main 决定要不要落** | ★[实测] ★ |
| ★**零挂链** ★ | 本闸**没有**挂进 `state/gate_check.py` ⇒ `grep -c check_onepass_s10_swap_set_truth state/gate_check.py` = **0** (★挂不挂归 main★) | ★[实测] ★ |
| ★**沙盒只落两处** ★ | `tmp/iss373_sbx/` (板副本 + 工具 + sets.json) + `logs/iss373/` (JSON / 日志 / DRC) | ★[实测] ★ |
| ★**只写自己的分片** ★ | 只写 `state/fragments/hw.yaml`, 且**只走 `state/frag_write.py`**; 写前写后各记一次 md5; 期间若被别人改过 ⇒ 停下并在交卷页 B5 写明 | ★[实测] ★ |
| ★**零外发** ★ | 本单**没有发任何邮件 / 询价 / 问询 / 采购**; 官方封装参数全部来自**本机 KiCad 10.0.8 官方库文件** (★`/home/yuewuya/kicad/AppDir/share/kicad/footprints/`, md5 `7a5f470c1f70d4b832be258501945385`★) | ★[实测] + [官网] ★ |
| ★**不代拍** ★ | ★**「那一趟 `J_DEBUG` 换不换 land」是 main 的裁决权** ⇒ 本单只给两条路的代价与判据 (§2.2) 与未决项 (§4.1) ★ | — |
| ★**不自签台账** ★ | `state/issue_log.yaml` 本单未动 (★台账由 main 签收★) | ★[实测] ★ |
| ★**零推 GitHub** ★ | 本单没有做任何 git push | ★[实测] ★ |

★**★判据句 / 事实句分开 (★本单纪律, L7 机器校验★) ★★**:

- ★**判据句** = 可判真假、可被闸复跑的陈述 (★写成「★… ⇒ …★」并给出复跑命令★) ★
- ★**事实句** = 本机跑出来的读数 (★一律带 [实测] / [推算] / [官网] 等级 + 数字★) ★
- ★**§2.2 那张表里, 每一行的左半列是判据, 右半列是事实; 机器块 `paths[]` 里的 `判据` 与 `事实` 两个键是这条纪律的机器化形态 (★闸 L7 校验两栏都非空★)** ★

---

## §7 本单新闸 (★`HW/check_onepass_s10_swap_set_truth.py`★)

★**九条判据 (★每条 fail-closed · 每条带反向用例★) ★**

| # | 判据 | 不许写死的部分 |
|---|---|---|
| ★**L0** ★ | ★**集合算法自算**: 脚本自己从 `HW/BOM_v1.csv` + `HW/netlist_v1.csv` + `HW/FP_TRUTH_BASELINE.md` 基准块 + `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` 缺口表算出 (★`inter + gap`★) 与 (★`iss + gap`★) 两个数 ⇒ ★**页里写的数 ≠ 脚本实算 ⇒ 红** ★ | ★**不许把 90 / 91 写死成常量** ★ |
| ★**L1** ★ | ★**差集恰为 1 件, 且脚本自己算出的那件与页里写的那件逐件相等** ⇒ 不是 1 件 ⇒ 红 | ★**不许写死一个名字就算过** ★ |
| ★**L2** ★ | 页 §0 口径表两行都在, 且都带复跑命令 | — |
| ★**L3** ★ | 四处口径逐条可查 (★路径 + 行号 + 那个数 + 定义还是算例★) ⇒ 少一条 ⇒ 红; ★**行号处那一行必须真的含那个数; 两处「实算出来的数」还要活体复跑对得上** ★ | — |
| ★**L4** ★ | `J_DEBUG` 四条腿逐条齐全 + 与 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 交叉引到 ⇒ ★**B33 那边的说法与 ISS-369 那边的说法必须同时在页里出现, 不许只留一边** ★ | — |
| ★**L5** ★ | 写库名名单的联动手算式在页里 (★94 / 92 与 95 / 91 四个数 + 算式★) | — |
| ★**L6** ★ | 板面零写板自证 (★md5 / mtime / size 三项★) | — |
| ★**L7** ★ | 证据等级五级白名单 + 零挂起措辞 + 判据句 / 事实句分开 | — |
| ★**L8** ★ | 零挂链 (★`grep -c check_onepass_s10_swap_set_truth state/gate_check.py` == 0★) | — |

★**★反向用例 (`--selftest` ≥ 8 条·每条自证「红的是目标那一条, 其余仍绿」) ★★**: L0 改页里的 90 · L1 改差集件数 · L1 把差集那件换成别的名字 · L2 删掉一行口径 · L3 改一个行号 · L3 把 ③ 的那个数改成 90 · L4 删掉一条腿 · L4 删掉 ISS-369 那边的说法 (只留 B33 一边) · L4 删掉 B33 的交叉引用 · L5 改 95 / 91 · L6 改板 md5 · L7 塞一个不在五级白名单里的证据标签 · L7 塞一句挂起措辞 · L7 把判据栏清空 · L8 往 `gate_check.py` 里塞一行本闸名 —— ★**每条都只让目标判据变红, 其余八条仍绿★** ★

---

*本页由 hw-lead 于 2026-11-23 实机生成; 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发; 「`J_DEBUG` 那一趟换不换 land」的裁决权在 main。*
