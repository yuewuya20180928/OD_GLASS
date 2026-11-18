<!-- ★★ISS-292 · 生成器 sidecar · 【追加式订正块】★★
★★ 本文件 = 清单页的【追加式订正块】的唯一存放处 (★追加式 = 老字一字不删·只往后加★)
★★ 生成器 `state/_iss277_build_preflight.py` 从这里读两块:
★★   ① ISS292:S3_APPENDIX    → 插到 §3 末尾 (★ISS-283 落表带来的板侧同步项 §③-1~§③-3★)
★★   ② ISS292:ISS289_APPENDIX→ 追加到页尾 (★ISS-289 现状值对回盘面·含 state_baseline 登记表★)
★★ ★★规矩: ★这两块只许【往后追加】, 不许改老字 ⇒ 重跑生成器不许冲掉它们★ ★★
★★ ★★另一条规矩: ② 里的 `state_baseline.entries[].expect` 是【漂移闸的期望值】(★`HW/check_workpack_state_values.py`★)
★★    ⇒ ★它【故意】不随盘面自动更新 ⇒ 盘面一变闸当场红 ⇒ 那时【同一次重锚】它 (★不许生成器偷偷改·那等于把闸调没★)★
-->

<!-- ISS292:S3_APPENDIX:BEGIN -->
### ★★§3-追加 · ★★ISS-283 落表带来的板侧同步项 (★3 条 · 追加式 · 上面每一行老字一字未删★) ★★

★**背景 (★main 13:1x 本机实读盘面 + 实跑闸·★不是推测★)**: ★**ISS-283 在 2026-11-17 12:16:08 (A3 / V-2=1) 与 12:30:23 (A4 / W-4 写法A + A5 / G-5 20mA 档) 两次真落表** ★
⇒ ★**网表 / 脚表 / BOM 三件已变 (板一个字节没变)** ⇒ ★**板那一趟 (「板只改一次」那一趟) 必须同趟吃掉下面 3 条, 否则网表与板对不上** ★
★**三条的编号 = 网表 note 里引用的「ISS-283 板侧清单 §③-N」** ★

| 编号 | 板侧项 | 来源 | 落表事实 (★台账出处★) | 板那一趟要做的事 | 判据 (★真命令★) |
|---|---|---|---|---|---|
| ★**§③-1** ★ | ★**V-2 网改名: `D_ESD_USB_D` pad1 网名 `USB_D_P_SRC` → `NET_USB_D_P_TYPEC`** ★ | ★**ISS-283 · A3 (V-2=1)** ★ | ★**网表 L417 的 net 已落 `NET_USB_D_P_TYPEC`** (★台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 · 链头 L1353 · ISS-283 · 12:16:08★) ⇒ ★**板面 3 处焊盘网名还挂旧的 `USB_D_P_SRC`** (★`D_ESD_USB_D.pad1` / `R_SER_USB_D_P` 一端 / `J_SOM_P1` 的 USB_D_P 脚★) ★ | ★**这 3 处焊盘网名同趟改成 `NET_USB_D_P_TYPEC`** (★不改 ⇒ 网表与板对不上★) ⇒ ★**对应条目 = `B32_V2_NET_RENAME`** ★ | ★`python3 HW/check_board_frame_caliber.py` ⇒ ★**C6 绿** (★盘上 md5 == 落表台账登记★) ★ |
| ★**§③-2** ★ | ★**`Q_PG` land 重画 (pad1 ↔ pad3 的网互换)** ★ | ★**ISS-283 · A4 (W-4 写法A)** ★ | ★**网表已落: pad1 = `PWR_GOOD` (G) / pad2 = `BAT_SW` (S) / pad3 = `PWR_ON` (D)** (★台账 §16.2 · 链头 L1353 · ISS-283 · 12:30:23★) ⇒ ★**DMP3098L 引脚序 = 1=G / 2=S / 3=D ⇒ 板上 land 仍是旧接法 (pad1=`PWR_ON` / pad3=`PWR_GOOD`) ⇒ 这 3 根线必须重画** ★ | ★**重画 `Q_PG` 的 3 根线** (★pad1→`PWR_GOOD` / pad2→`BAT_SW` / pad3→`PWR_ON`★) ⇒ ★**对应条目 = `B11_Q_PG_LAND`** ★ | ★`bash state/pcbnew_py.sh -c "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');print([(p.GetNumber(),p.GetNetname()) for p in [f for f in b.GetFootprints() if f.GetReference()=='Q_PG'][0].Pads()])"` ⇒ ★**pad1 挂 `PWR_GOOD` / pad3 挂 `PWR_ON`** ★ |
| ★**§③-3** ★ | ★**D− 侧 ESD 三件仍挂着 (R4×2 + R9)** ★ | ★**ISS-266 (板侧) · ISS-283 (登记)** ★ | ★**落表侧已落, 板侧未清**: ① `D_ESD_USB_D` 板上仍是 **2 焊盘** ② D− 网 (`USB_D_N_SRC` / `NET_USB_D_N_TYPEC`) 上 **ESD 位号数 = 0** ③ `D_ESD_USB_D` → `J_USB_C` 板面距离 **47.99 mm** > 3.0 mm 判据 ⇒ ★**这 4 条是 G1a-4 的最后 4 条未落表项 (板侧)** ★ | ★**板那一趟清掉这 4 条** ⇒ ★**对应条目 = `B07_ESD_USB_D_3PIN` / `B08_ESD_USB_D_NEAR` / `B09_ESD_USB_D_MINUS`** ★ | ★`python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ ★**R4 / R9 转绿** ★ |

★**★铁律 (★本单口径·★零写板★)**: ★**这 3 条本单【一条都不许在盘上做】** ★ ⇒ ★**板 `611b869e…` 与 `.kicad_pro 3e504d2b…` 逐字节不变** ★ ⇒ ★**Gerber / 投产包一律不许用 (★板现在仍是「旧网表的板」★)** ★ ⇒ ★**板改 = 「板只改一次」那一趟, 由 main 统一开** ★
★**★登记 (★只登记 · 不代拍★)**: ★**G-5 亮度档 ⇒ 亮度 ×14 ⇒ 眼旁光源的 IEC 62471 分级要重算 ⇒ 登记成 need 给 main (★hw-lead 不代拍★)** ★
<!-- ISS292:S3_APPENDIX:END -->

<!-- ISS292:ISS289_APPENDIX:BEGIN -->
## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)

> ★**本附录 = 追加式 (★本页上面每一行老字一字未删 ★)** ★
> ★**本页的 items JSON 里那两句已过期的现状值 (★`B01_REF_SUFFIX` 的「零后缀」/ `B26_BASELINE` 的 `e06c1dd6…`★) 按追加式纪律原样留着, 订正写在这里** ★
> ★**机器闸**: `python3 HW/check_workpack_state_values.py` (★V1~V7★) ⇒ ★**「本页 + 作业包里的现状值 == 盘面实测」当场判红 ★** ★

| # | 本页条目 / 位置 | 老字 (★原样保留, 一字未删 ★) | ★**现行值 (★盘面实测★)** ★ |
|---|---|---|---|
| ① | ★**`B17_DNP_43`** ★ | ★**`B17_DNP_43`** ★ | ★**条目 id `B17_DNP_43` 保留 (★老字留痕 · 闸的探针键也用它 ★) ⇒ 现行值 = 40** ★ ⇒ ★**该条的 `current_state` 已是 `MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗` (★落表后已更新★); 本次只补「id 名字里的 43 是历史留痕, 不是现值」这句注解** ★ |
| ② | ★**`B01_REF_SUFFIX`** ★ | `[实测] 板文件 186 个封装位号零后缀 ⇒ KiCad 判「未标注」⇒ 218 处问号` | ★**板文件 186 个封装位号里 30 个末字符是数字 (含 1 个已带 `_1` 的 `R_BAT_DET_1`) ⇒ 真正要加 `_1` 的是 156 个** ★ ⇒ ★**「零后缀」那句不成立 (★ISS-287 ②★); 186 是【原理图侧】口径 (★218 − 32★), 板侧是 156** ★ |
| ③ | ★**`B31_P7_TARGET`** · ★**§1 帧声明** ★ | `186 封装` | ★**186 封装 (★现状·官方板★) / 185 封装 (★S2 把 `C_VBUS_GND` 拿掉之后★)** ★ ⇒ ★**官方板 186 / 沙盒生成板 185 ⇒ 差 1 = `C_VBUS_GND` (★网表 board 列 = CHG_BOARD·DNP, 但官方板上有实物封装@107.70,42.50★) ⇒ ★★动板那一趟按【官方板的数】走: 开工前 186 / 收工后 185★★ ★** |
| ④ | ★**`B26_BASELINE`** ★ | `网表 e06c1dd6…` | ★**落表台账登记 = 37f62ac3f0b81d92ca7d48fdea717f07** ★ (★脚表 `a4270120454aedf7a23c92cd8985c8a6` / BOM `5d02bece9477ffce5fbe0193c7d5cce4`·★ISS-283 · 台账 L1353·§16.2★) ⇒ ★**基线走落表台账为准, 不写死** ★ |
| ⑤ | ★**铜层 / 板框四数** ★ | `8 铜层 · 160.10×100.10` | ★**8 铜层 · 160.10×100.10** ★ (★现状=现役帧 B160x100★) |
| ⑥ | ★**`B03_ULDO_S28_PAD3`** (脚表缺陷条数) ★ | ★`脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账` ★ | ★**脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账** ★ (★现状 = 18 · 本闸钉住★) |

★**★本附录的现状值登记表 (★与作业包 §8.2.5 逐字相同★)** ★

```json
{
  "schema": "board-onepass-state-baseline/v1",
  "generated_by": "ISS-289 hw-lead (2026-11-17)",
  "note": "★期望值写在文档里 (不写死在闸里) ⇒ 文档漂了当场红; md5 基线的取值来源 = 落表台账 (HW/landing_md5.py)★",
  "state_baseline": {
    "entries": [
      {
        "id": "W01_S7_HEADING",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "### ★S7 · DNP 标记 (★43 个位号·★生成器侧改代码★) ★",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "S7 · DNP 标记 (★40 个位号·★生成器侧改代码★)",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§3-S7 段标题的老字是 43 ⇒ 现行值 40"
      },
      {
        "id": "W02_S7_QUANT_ZERO",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "★现状: **43 个全部零标记**★",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "现状: **40 个全部零标记**",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§3-S7 量化判据第一条"
      },
      {
        "id": "W03_S7_QUANT_TOKEN",
        "category": "dnp_token_count",
        "doc": "workpacket",
        "anchor": "板文件里 \"dnp\" 出现次数应从 3 涨到 3 + 43 = 46",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "板文件里 \"dnp\" 出现次数应从 3 涨到 3 + 40 = 43",
        "expect": "3",
        "probe": [
          "python3",
          "-c",
          "print(open('HW/PCB/demo_mainboard.kicad_pcb',encoding='utf-8',errors='replace').read().lower().count('dnp'))"
        ],
        "probe_regex": "^(\\d+)$",
        "note": "板文件 dnp 出现次数: 现状 3 (三个层设置) ⇒ S7 跑完 = 3 + 40 = 43"
      },
      {
        "id": "W04_S3_TABLE_S7",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "★R3-A4: MAIN_PCB且DNP 54 颗 · 在板上 43 颗 · ★**零标记 43 颗** ★",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · ★**零标记 40 颗** ★",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§3 表 S7 行的三个数一起订正 (54/43/43 → 51/40/40)"
      },
      {
        "id": "W05_S4_ACCEPT_ROW",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "★**R3-A4 零标记 DNP 数 = 0** ★ (★现状 43★)",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "R3-A4 零标记 DNP 数 = 0** ★ (★现状 40★)",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§4 验收表 S1~S7 行"
      },
      {
        "id": "W06_S2_X2_PIT",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "43 个 DNP 零标记不是「生成器漏刷」",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "40 个 DNP 零标记不是「生成器漏刷」",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§2 的 X-2 坑行"
      },
      {
        "id": "W14_S6_1_S7_ROW",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "DNP 标记 (43 个)",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "DNP 标记 (40 个)",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§6.1 表 S7 行 (同源第三处)"
      },
      {
        "id": "W15_S8_1_3_X4",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "★**X-4 修完 ⇒ 板上有 43 个 DNP 标记**",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "X-4 修完 ⇒ 板上有 40 个 DNP 标记",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§8.1.3-3 (同源第三处)"
      },
      {
        "id": "W16_S1_1_F3",
        "category": "dnp_zero_mark",
        "doc": "workpacket",
        "anchor": "MAIN_PCB 且 DNP 的位号数 54 · 其中在板文件里真实存在的 43 · 零标记的 43",
        "correction_anchor": "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正",
        "fresh": "MAIN_PCB 且 DNP 的位号数 51 · 其中在板文件里真实存在的 40 · 零标记的 40",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "§1.1 第 1 行 F3 (同源第三处)"
      },
      {
        "id": "W11_FOOTPRINT_COUNT",
        "category": "footprint_count",
        "doc": "workpacket",
        "anchor": "160.10×100.10 mm / 8 铜层 / 186 封装",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "186 封装 (★现状·官方板★) / 185 封装 (★S2 把 `C_VBUS_GND` 拿掉之后★)",
        "expect": "186",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "封装 (\\d+)",
        "note": "官方板 186 / 生成板 185 ⇒ 差 1 = C_VBUS_GND (板级归属差, 不是漏数)"
      },
      {
        "id": "W12_S1_BOARD_156",
        "category": "ref_suffix",
        "doc": "workpacket",
        "anchor": "★**③ 板侧 186 个封装位号 = 走 S6 重出自动带** ★",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "板侧真正要加 `_1` 的是 156 个 (★官方板 186 个封装里末字符是字母的只有 156 个, 另 30 个末字符是数字不动★)",
        "expect": "156",
        "probe": [
          "bash",
          "state/pcbnew_py.sh",
          "-c",
          "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');rs=[f.GetReference() for f in b.GetFootprints()];print('板侧末字符是字母(要加_1) = %d' % len([r for r in rs if not r[-1].isdigit()]));print('带 _1 后缀 = %d' % len([r for r in rs if r.endswith('_1')]))"
        ],
        "probe_regex": "要加_1\\) = (\\d+)",
        "note": "§3-S1 的「板侧 186 个封装位号」会被读成「板上有 186 个要改名」⇒ 错"
      },
      {
        "id": "W18_S1_SUFFIX_ONE",
        "category": "ref_suffix",
        "doc": "workpacket",
        "anchor": "★**186 个 `X` → `X_1` (★`C_AC_CSI_D0_CK_N` → `C_AC_CSI_D0_CK_N_1`★) · ★**`RAIL_*` / `NET_*` 保留** (★单点汇流位, 改了 BOM 多假料号★) · ★**32 个本来就数字结尾的不动** ★",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "官方板带 `_1` 后缀的位号 = 1 个 (`R_BAT_DET_1`) ⇒ 改完 = 157 个",
        "expect": "1",
        "probe": [
          "bash",
          "state/pcbnew_py.sh",
          "-c",
          "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');rs=[f.GetReference() for f in b.GetFootprints()];print('板侧末字符是字母(要加_1) = %d' % len([r for r in rs if not r[-1].isdigit()]));print('带 _1 后缀 = %d' % len([r for r in rs if r.endswith('_1')]))"
        ],
        "probe_regex": "带 _1 后缀 = (\\d+)",
        "note": "ISS-287 ②: 官方板带 _1 后缀的位号 = 1 个"
      },
      {
        "id": "W19_S1_SCH_186",
        "category": "ref_suffix",
        "doc": "workpacket",
        "anchor": "★**① 器件位号真源 = `HW/SCHEMATIC_V1_SPEC.json`** (★`devices` 段的 186 个 `ref` ★)",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "原理图 / 网表侧要加 `_1` 的位号 = 186 个 (★218 − 32★) ⇒ 板侧是 156 个, 不是 186 个",
        "expect": "186",
        "probe": [
          "python3",
          "-c",
          "import csv;rs={r['ref'] for r in csv.DictReader(open('HW/BOM_v1.csv'))};print('BOM 位号末字符是字母 = %d' % len([r for r in rs if not r[-1].isdigit()]))"
        ],
        "probe_regex": "= (\\d+)$",
        "note": "186 是原理图侧口径 (BOM 218 − 32); 该 JSON 里没有 devices 键 ⇒ 指针失效 (已登记 need)"
      },
      {
        "id": "W13_COPPER_COUNT",
        "category": "copper_and_frame",
        "doc": "workpacket",
        "anchor": "| ★**铜层数** ★ | ★**8** ★",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "铜层数 = 8",
        "expect": "8",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "铜层 (\\d+)",
        "note": "铜层 / 板框四数之一"
      },
      {
        "id": "W13B_FRAME_BOX",
        "category": "copper_and_frame",
        "doc": "workpacket",
        "anchor": "| ★**板框 (Edge.Cuts)** ★ | ★**160.10 × 100.10 mm** ★ |",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "板框 = 160.10 × 100.10 mm",
        "expect": "160.10 × 100.10 mm",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "板框 \\(含线宽\\) = ([\\d.]+ × [\\d.]+ mm)",
        "note": "铜层 / 板框四数之二 (宽 × 高)"
      },
      {
        "id": "W13C_FRAME_ID",
        "category": "copper_and_frame",
        "doc": "workpacket",
        "anchor": "帧 id `B160x100` · 板 160.00×100.00 / 8 铜层 / 1.60mm / 186 封装",
        "correction_anchor": "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页",
        "fresh": "现役帧 = B160x100",
        "expect": "B160x100",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "现役帧 (\\S+)",
        "note": "铜层 / 板框四数之三 (现役帧 id)"
      },
      {
        "id": "W07_FINDINGS_2",
        "category": "defect_count",
        "doc": "workpacket",
        "anchor": "★**FINDINGS = 0** ★ (★现状 2 = F2+F3★)",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "FINDINGS = 0** ★ (★现状 2 = F2+F3★",
        "expect": "2",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "FINDINGS: (\\d+)",
        "note": "无漂 (仍 = 2 = F2+F3), 但登记进闸"
      },
      {
        "id": "W08_PINS_DEFECT",
        "category": "defect_count",
        "doc": "workpacket",
        "anchor": "★**15 条** (★14 串号 + 1 缺脚: `U_LDO_S28` 无 pin3★)",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "18 条 (★15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账★)",
        "expect": "18",
        "probe": [
          "python3",
          "HW/check_pin_function_labels.py"
        ],
        "probe_regex": "(\\d+) 条缺陷",
        "note": "脚表语义缺陷 15 → 18 (落表后 md5 台账对账多 3 条)"
      },
      {
        "id": "W09_SAME_PAD_NET",
        "category": "defect_count",
        "doc": "workpacket",
        "anchor": "缺失 0 · 同号异网 0",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "缺失 0 · 同号异网 3",
        "expect": "3",
        "probe": [
          "bash",
          "state/pcbnew_py.sh",
          "state/check_pcb_nets.py"
        ],
        "probe_regex": "同号异网 (\\d+)",
        "note": "落表已改、板还没跟 ⇒ 同号异网 0 → 3 (Q_PG pad1/pad3 + D_ESD_USB_D pad1)"
      },
      {
        "id": "W10_MD5_NETLIST",
        "category": "md5_baseline",
        "doc": "workpacket",
        "anchor": "★**`HW/netlist_v1.csv`** ★ | ★`e06c1dd633566aa44732762c2ff99d1c` ★",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "落表台账登记 = 37f62ac3f0b81d92ca7d48fdea717f07",
        "expect_mode": "ledger",
        "expect_target": "HW/netlist_v1.csv",
        "probe": [
          "md5sum",
          "HW/netlist_v1.csv"
        ],
        "probe_regex": "^([0-9a-f]{32})",
        "note": "网表 md5 基线 ★走落表台账为准, 不写死★ (ISS-283 ⑩-b 的口径)"
      },
      {
        "id": "W10B_MD5_PINS",
        "category": "md5_baseline",
        "doc": "workpacket",
        "anchor": "★**`HW/netlist_v1_pins.csv`** ★ | ★`287e7861a0d1007748d92d9fbecdd490` ★",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "落表台账登记 = a4270120454aedf7a23c92cd8985c8a6",
        "expect_mode": "ledger",
        "expect_target": "HW/netlist_v1_pins.csv",
        "probe": [
          "md5sum",
          "HW/netlist_v1_pins.csv"
        ],
        "probe_regex": "^([0-9a-f]{32})",
        "note": "脚表 md5 基线 ★走落表台账为准★"
      },
      {
        "id": "W10C_MD5_BOM",
        "category": "md5_baseline",
        "doc": "workpacket",
        "anchor": "★**`HW/BOM_v1.csv`** ★ | ★`94642d07a69e8d60dd2af57f69b93607` ★",
        "correction_anchor": "### ★8.2.3 · 同批一起对回的其余现状值型判据",
        "fresh": "落表台账登记 = 5d02bece9477ffce5fbe0193c7d5cce4",
        "expect_mode": "ledger",
        "expect_target": "HW/BOM_v1.csv",
        "probe": [
          "md5sum",
          "HW/BOM_v1.csv"
        ],
        "probe_regex": "^([0-9a-f]{32})",
        "note": "BOM md5 基线 ★走落表台账为准★"
      },
      {
        "id": "C01_B17_ZERO_MARK",
        "category": "dnp_zero_mark",
        "doc": "checklist",
        "anchor": "[实测] R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "清单页这条的 current_state 已是 40 (老字保留), 本闸把它钉住"
      },
      {
        "id": "C02_B17_ID_NAME",
        "category": "dnp_zero_mark",
        "doc": "checklist",
        "anchor": "★**`B17_DNP_43`** ★",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "条目 id `B17_DNP_43` 保留 (★老字留痕 · 闸的探针键也用它 ★) ⇒ 现行值 = 40",
        "expect": "40",
        "probe": [
          "python3",
          "HW/check_netlist_contradiction_r3.py"
        ],
        "probe_regex": "零标记 (\\d+) 颗",
        "note": "条目 id 名字含 43 ⇒ 改名会打断闸的探针键 ⇒ 只加注, 不改名"
      },
      {
        "id": "C03_B01_REF_SUFFIX",
        "category": "ref_suffix",
        "doc": "checklist",
        "anchor": "[实测] 板文件 186 个封装位号零后缀 ⇒ KiCad 判「未标注」⇒ 218 处问号",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "板文件 186 个封装位号里 30 个末字符是数字 (含 1 个已带 `_1` 的 `R_BAT_DET_1`) ⇒ 真正要加 `_1` 的是 156 个",
        "expect": "156",
        "probe": [
          "bash",
          "state/pcbnew_py.sh",
          "-c",
          "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');rs=[f.GetReference() for f in b.GetFootprints()];print('板侧末字符是字母(要加_1) = %d' % len([r for r in rs if not r[-1].isdigit()]));print('带 _1 后缀 = %d' % len([r for r in rs if r.endswith('_1')]))"
        ],
        "probe_regex": "要加_1\\) = (\\d+)",
        "note": "「186 个封装位号零后缀」这句不成立 (ISS-287 ②)"
      },
      {
        "id": "C04_B31_FOOTPRINT_COUNT",
        "category": "footprint_count",
        "doc": "checklist",
        "anchor": "[实测] 现役板 = 160×100 台架板 (8 铜层 / 186 封装 / 160.10×100.10)",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "186 封装 (★现状·官方板★) / 185 封装 (★S2 把 `C_VBUS_GND` 拿掉之后★)",
        "expect": "186",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "封装 (\\d+)",
        "note": "官方板 186 / 生成板 185"
      },
      {
        "id": "C05_FRAME_B160X100",
        "category": "copper_and_frame",
        "doc": "checklist",
        "anchor": "★**160×100 台架板 (现役板)** · 8 铜层 · 160.10×100.10 · 186 封装 ★",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "8 铜层 · 160.10×100.10",
        "expect": "8",
        "probe": [
          "python3",
          "HW/check_board_frame_caliber.py"
        ],
        "probe_regex": "铜层 (\\d+)",
        "note": "铜层 / 板框四数"
      },
      {
        "id": "C06_B03_DEFECT_COUNT",
        "category": "defect_count",
        "doc": "checklist",
        "anchor": "脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账",
        "expect": "18",
        "probe": [
          "python3",
          "HW/check_pin_function_labels.py"
        ],
        "probe_regex": "(\\d+) 条缺陷",
        "note": "脚表缺陷条数 (清单页已更新, 本闸钉住)"
      },
      {
        "id": "C07_B26_MD5_LEDGER",
        "category": "md5_baseline",
        "doc": "checklist",
        "anchor": "网表 e06c1dd6…",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "落表台账登记 = 37f62ac3f0b81d92ca7d48fdea717f07",
        "expect_mode": "ledger",
        "expect_target": "HW/netlist_v1.csv",
        "probe": [
          "md5sum",
          "HW/netlist_v1.csv"
        ],
        "probe_regex": "^([0-9a-f]{32})",
        "note": "B26 的 md5 基线 ★走落表台账为准, 不写死★"
      }
    ]
  }
}
```

★**★本页的每个数字都是本机实读, 没有一条是估的★★** ★
<!-- ISS292:ISS289_APPENDIX:END -->
