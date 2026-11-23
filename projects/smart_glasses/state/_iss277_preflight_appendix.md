<!-- ★★ISS-292 · 生成器 sidecar · 【追加式订正块】★★
★★ 本文件 = 清单页的【追加式订正块】的唯一存放处 (★追加式 = 老字一字不删·只往后加★)
★★ 生成器 `state/_iss277_build_preflight.py` 从这里读两块:
★★   ① ISS292:S3_APPENDIX    → 插到 §3 末尾 (★ISS-283 落表带来的板侧同步项 §③-1~§③-3★)
★★   ② ISS292:ISS289_APPENDIX→ 追加到页尾 (★ISS-289 现状值对回盘面·含 state_baseline 登记表★)
★★   ③ ISS304:MD5_ANCHOR     → 追加到页尾 (★ISS-304·md5 基线的现值来源已自动化·含台账现值占位符★)
★★ ★★规矩: ★这三块只许【往后追加】, 不许改老字 ⇒ 重跑生成器不许冲掉它们★ ★★
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
| ⑥ | ★**`B03_ULDO_S28_PAD3`** (脚表缺陷条数) ★ | ★`脚表 15 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 0 条 md5 台账对账` ★ | ★**脚表 15 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 0 条 md5 台账对账** ★ (★现状 = 15 · 本闸钉住★) |

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
        "fresh": "15 条 (★15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 0 条 md5 台账对账 (★基线已于 ISS-299 重锚·那 3 条台账对账缺陷已消失★)★)",
        "expect": "15",
        "probe": [
          "python3",
          "HW/check_pin_function_labels.py"
        ],
        "probe_regex": "(\\d+) 条缺陷",
        "note": "脚表缺陷总条数 18 → 15 (★ISS-299 重锚基线后·md5 台账对账 3 条已消失·脚表功能缺陷 15 条未变★)"
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
        "fresh": "落表台账登记 = 6aee500e60ba0732f83a9cf557ba90ab",
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
        "fresh": "落表台账登记 = 9174309df1ec9411ac8e8d9e80ee386a",
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
        "fresh": "落表台账登记 = 5b9993992405904a60ac96a020b375d8",
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
        "anchor": "脚表 15 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 0 条 md5 台账对账",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "脚表 15 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 0 条 md5 台账对账",
        "expect": "15",
        "probe": [
          "python3",
          "HW/check_pin_function_labels.py"
        ],
        "probe_regex": "(\\d+) 条缺陷",
        "note": "脚表缺陷条数 (★基线已于 ISS-299 重锚·md5 台账对账 3 条已消失 ⇒ 18 → 15·脚表功能缺陷 15 条未变·本闸钉住★)"
      },
      {
        "id": "C07_B26_MD5_LEDGER",
        "category": "md5_baseline",
        "doc": "checklist",
        "anchor": "网表 e06c1dd6…",
        "correction_anchor": "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)",
        "fresh": "落表台账登记 = 6aee500e60ba0732f83a9cf557ba90ab",
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

## ★ISS-354 追加式订正 (★「板那一趟」的下料前一票否决项 · 3 条 · ★零写板★)

★**一句话**: ★★ISS-169 暴露的「板子还不能下单」三件事 (SoM 座 pin1 哪一排 / 5 个 ref 封装与脚号不自洽 / BOM OPN 待选型) ⇒ ★**本节把它们收成 3 条【下料前一票否决项】** ★ ⇒ ★**任一条未闭合 ⇒ 不许下料** ★ ⇒ ★**本节是【板侧项全集】的一部分, 必须在「板那一趟」一次做完** ★

★**交卷人**: hw-lead (硬件总工) · **日期**: 2026-11-23 · **来源单**: ISS-354 (★`state/dispatch_briefs/ISS-354_hw_demo_board_manufacturability_closure.md`★) ★
★**性质**: ★**纯查证 / 作业包类 ⇒ 零写板**★ ⇒ ★**不改网表真源 / 不改脚表 / 不改 BOM / 不改原理图 / 不重出 Gerber** ★
★**配套**: 改项清单全文在 ★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §9-6★ (★追加式·老字一字未删★) · 交卷页 ★`HANDOFF/2026-11-23_hw-lead_ISS354_demo主板可制造性收口.md`★ · 机器闸 ★`HW/check_iss354_mfg_closure.py`★ · 资料留档 ★`logs/iss354/`★

★**★零写板 (双证)** ★: `HW/PCB/demo_mainboard.kicad_pcb` md5 = ★`611b869e13518c3c023fb178f91a0075`★ · mtime = ★`2026-11-06 07:07:17.362193413`★ ★

---

### ★V-1 · ★★SoM 座 pin1「哪一排」= 一票否决项★★

★**★什么状态下不许下料 (★以下任一条成立 ⇒ 不许下料★)** ★

| # | 不许下料的状态 | 为什么 |
|---|---|---|
| ★**V-1-①** ★ | ★**4 个座 (`J_SOM_P1`/`P2`/`P3`/`P4`) 的「奇数脚排 (pin1 排)」归属, 仍是【只靠 KiCad 封装约定推断】而没有实物/官方物证定死** ★ | ★**载板 land 若把两排做反 ⇒ 该座 100 个网络全部对调 ⇒ 板子白打** ★ |
| ★**V-1-②** ★ | ★**板侧 4 个座【没有 pin-1 丝印三角 / 缺口 / 极性标注】** ★ | ★**[实测] 板上 `J_SOM_P1..P4` 的封装只有 F.Fab 外框 (22.6 × 3.2), 一条 F.SilkS 都没有** ★ ⇒ 且 ★**[官网] Hirose 官方白纸黑字「Note 4: This connector is NOT polarized」⇒ 母座无防呆 ⇒ 装反了会【物理插进去】, 不会机械挡下** ★ |
| ★**V-1-③** ★ | ★**4 个座之间任一脚序 / 朝向彼此不一致** ★ | ★**4 个座用同一个型号同一个朝向 ⇒ 测通一个即定死全部; 出现不一致 ⇒ 说明符号/脚表侧也有错 ⇒ 板那一趟还会再改** ★ |
| ★**V-1-④** ★ | ★**SoM 座 land 的焊盘几何与 Hirose 原厂推荐图不符 (pad 尺寸 / 两排中心距 / 跨距 任一项)** ★ | ★**[实测] 板上是 0.2 × 0.7 mm / 两排中心距 3.08 mm / 首末跨距 19.6 mm ⇒ 与 Hirose 原图 (2.38 = 内缘间距, 3.78 = 外缘对内缘总高) 一致 ⇒ 本条【现状已满足】, 但改动后须复测** ★ |

★**★用什么手段核对 (★按优先级, ★前两条本单已做完★)** ★

| 手段 | 能定什么 | 不能定什么 | 本单状态 |
|---|---|---|---|
| ★**① Hirose 原厂推荐 PCB 图 + 官方库封装 (逐参数比对)** ★ | ★**焊盘几何: pad 0.2 × 0.7 / 排距 3.08 / 跨距 19.6 / 外形 22.6 × 3.2** ★ ⇒ ★**顺带把「2.38 的两种解读」定死为【内缘间距】(解读 A)** ★ | ★**定不了「哪一排是奇数排」** ★ | ★**[官网] + [实测] 本单已做** ★ (★本地快照 `state/_os_snapshots/hirose_DF40C-100DS-0.4V(51).pdf` + `state/_os_snapshots/hirose_pages/`★) ★ |
| ★**② 本机 KiCad 10.0.8 官方库 `Connector_Hirose_DF40.pretty/Hirose_DF40C-100DS-0.4V_2x50_P0.4mm`** ★ | ★**逐参数证明: 板上的 4 个座 = 该官方封装整体转 180°** ★ ⇒ ★**「pin1 在哪一端」与「焊盘几何」这两件, 板已经是对的** ★ | ★**该封装的 pin-1 丝印三角落在【奇数排】, 但 Hirose 自己的资料里【无任何一处】能印证这个约定 ⇒ 仍属推断** ★ | ★**[实测] 本单已做** ★ ⇒ ★**★探针 (2026-11-03)「KiCad 官方库没有 DF40」的结论已过期 (该库目录 mtime 2026-10-29, 另有专用库 `Connector_Hirose_DF40.pretty`, 79 个文件)★★ ★ |
| ★**③ Forlinx 官方手册 (底面尺寸图 + 4 张引脚原理图)** ★ | ★**pin1 在哪一「端」= 已定 (P1/P2 → x=60.8; P3/P4 → x=26.8)** ★ | ★**★定不了「哪一排」★★** (★手册无带脚号的接触排布图★) | ★**[官网] 已有 (探针已查, 本单未重查)** ★ |
| ★**④ Hirose 原厂 3D (STEP / IGES) + DF40C-100DP 的 cavity identification 记号** ★ | ★**器件自身的极性/防呆记号在哪一端** ★ | ★**单独仍定不了排 (要配合 ③ 与实物)** ★ | ★**[官网] 入口在 Hirose 产品页 (★需注册下载·★本单不发任何询价/问询★)** ★ |
| ★**⑤ ★★样件通电对称性 (★本单推荐的定案手段·零外发·可自证★★)** ★ | ★**一次定死「奇数排在哪一排」并覆盖全部 4 个座** ★ | —— | ★**手法: 用 `P2` —— 官方表 `P2` pin1 = `I2C2_SDA_M0` (3.3V 信号), pin2 = `GND` ⇒ 在 SoM 底面 (针头侧) 万用表电阻档, 一端接 SoM 地, 逐根试 △ 端的两根针头: 读数 ≈0Ω 那根 = pin2 = 偶数排, 不通那根 = pin1 = 奇数排 ⇒ 再读出它在 y 大的一侧还是 y 小的一侧 ⇒ 4 座同型号同朝向 ⇒ 测通一个即定死全部 4 个** ★ ★**注意读的是底面: 镜像的是 x 不是 y, 顶视/底视的「上/下排」可直接换算** ★ |
| ★**⑥ 1:1 打印校验治具** ★ | ★**68 × 50 轮廓 + 4 个 φ2.1 孔 + 4 个 22.6 × 3.2 座框 + 两排候选位置 A/B, 实物 SoM 压上去一眼看出哪一排是奇数排** ★ | —— | ★**[推算] 成本近乎为零, 建议与 ⑤ 一起做 (顺带复核 17.0/51.0/3.5/46.5 坐标)** ★ |

★**★核对不到怎么办 (★降级 = 改设计路径绕开它, ★不是「等原厂确认」★)** ★

★**★最坏假设 = 两排可能反 ⇒ 三条绕法 (★按代价从低到高★)** ★:

| 绕法 | 内容 | 代价 | 本单判词 |
|---|---|---|---|
| ★**绕法 1 (★代价最低·本单推荐★)** ★ | ★**把 4 个座的物理连接从载板本体上摘出去** —— 用 4 块「排线转接板 / 邮票板」把 SoM 的 4 个座引到别处 ⇒ ★**载板本体先按「任一排」投产, 排向那一趟在转接板上定** ★ | 增 4 块转接板 + 排线 (★结构与成本由 MECH/PM 判, 本单不代拍★) | ★**★推荐★** ★ ⇒ ★**板本体不再被这个不确定项卡住** ★ |
| ★**绕法 2** ★ | ★**把 SoM↔主板的连接改走别的物理路径** (★SoM 板载接口 / 软排线 / 测试点★) | ★**这属于 U-1「画哪块物理产品」的地界 ⇒ 本单只登记事实与影响, 不代拍** ★ | ★**登记** ★ |
| ★**绕法 3 (★明令禁止★)** ★ | ★**先按某一排打板, 错了再改** | ★**4 座 × 100 脚全对调 ⇒ 板子白打 + 板 md5 变第二次** ★ | ★**禁止** ★ |

---

### ★V-2 · ★★「两排镜像兼容 / 装反也能通」= 明确不可行 (★记录在案·不许再议★)★★

| 项 | 内容 |
|---|---|
| ★**判据** ★ | ★**不许把设计做成「装反也能通」** ★ |
| ★**证据 ① (硬短)** ★ | ★**[实测]** `HW/PCB/FET3572C_PIN_TABLE.csv` (Forlinx 官方手册解析产物, 399 行) ⇒ 4 座共 ★**359 对相邻 (奇, 偶) 脚**★, 其中 ★**101 对是「一端 GND、另一端是带电信号」**★ ⇒ ★**例: `P2` pin1=`I2C2_SDA_M0` (3.3V) vs pin2=`GND`; `P1` pin2=`GND` vs pin3=`SDMMC0_D1` (1.8V/3.3V); `P1` pin45=`GPIO0_C1_d` (3.3V) vs pin46=`GND`**★ ⇒ ★**两排一反 = 101 处 GND 直接接到带电信号 = 硬短**★ ★⇒ 镜像兼容【不可行】★ |
| ★**证据 ② (装反不会被挡下)** ★ | ★**[官网]** Hirose DF40 系列 Guideline (ETAD-H1015-00) 与 DF40 目录页: ★**「Note 4: This connector is NOT polarized」**★ ⇒ ★**母座无防呆键 ⇒ 装反了会物理插进去**★ ⇒ ★**防呆必须做在板侧 (V-1-②) ⇒ 不能指望连接器挡住**★ |
| ★**⇒ 对策** ★ | ★**① 接受「装反会硬短」这个前提, 用板侧丝印 + 装配工序 + 上电前检查来挡 (V-1② + V-1⑤) ★ ② 绝不许把 V-2 当成「所以两排随便选」—— 恰恰相反, 正因为装反是静默硬短, 才必须在【布线之前】把排向定死 ★** |

---

### ★V-3b · ★★★`Q1`/`Q2` 的 pad→net 映射对着真实脚号【栅/漏/源错位】= 一票否决项 (★本单查出来的最重一条★★)★★

★**★一句话**: ★**这不是「封装画小了」, 是【电气错】—— 板面按一套 5~7 脚的自创脚序布的网, 装上真实器件后 栅极/漏极/源极、电源/地 全部错位 ⇒ ★**板子造出来也只是一块不能用的板** ★ ★

★**★事实 (★[实测] 板文件逐焊盘 + [官网] TI SLPS202B「Top View」图★)** ★:

| 器件 | 板面 (★实测★) | 真实器件 (★[官网]★) | 后果 |
|---|---|---|---|
| `Q1` | pad2=`BAT_GATE` · pad3=`BAT_CELL_P` · pad4=`BAT_PROT_CELL` · pad5=`BAT_DOUT` · pad6=`GND` | ★**1=S · 2=S · 3=S · 4=G · 5=D · 6=D · 7=D · 8=D** ★ | ★**pad2 栅驱网落到【源】· pad3 电池正极落到【源】· pad4 电芯网落到【栅】· pad5 `BAT_DOUT`(栅驱) 落到【漏】· pad6 不存在** ★ |
| `Q2` | pad2=`BAT_GATE` · pad3=`BAT_PROT_CELL` · pad4=`BAT_PROT_CELL2` · pad5=`BAT_COUT` · pad6=`GND` | ★**同上** ★ | ★**pad5 `BAT_COUT`(栅驱) 落到【漏】· pad4 电芯网落到【栅】· pad2 与 `Q1` 同网 ⇒ 两个 FET 的【源极被短在一起】⇒ 共源, 背靠背拓扑失效** ★ |

★**★什么状态下不许下料** ★: ★**① `Q1`/`Q2` 的符号未改成 8 脚 (1/2/3=S · 4=G · 5/6/7/8=D) ⇒ 不许下料; ② 板面 pad→net 未按真实脚号重排 ⇒ 不许下料; ③ `Q1`/`Q2` 的 `BAT_GATE` 共网未拆 ⇒ 不许下料** ★
★**★手段** ★: 对 TI SLPS202B 的 Top View 脚号逐脚核对 (★本地快照 `logs/iss354/datasheets/csd16406q3.pdf` + 渲染图 `logs/iss354/datasheets/csd_topview2.png` / `csd_tv_left.png`★) + 跑 ★`python3 HW/check_iss354_mfg_closure.py`★
★**★核对不到怎么办 (降级)** ★: ★**把 `Q1`/`Q2` 两个位整个留空 (DNP 不贴) + 丝印标「DNP」+ 网表标「预留」** ⇒ ★**板本体可投产, 保护电路以后再补** ★ ⇒ ★**★注意: 【不能】只换封装不改符号/不改网——那样错位照样在★** ★

★**★全 5 个 ref 的板面 pad→net 逐脚对照表 (★[实测] vs [官网]★)** ★: ★**见 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §9-6-1b** ★ (★`Q1` 5 脚 · `Q2` 5 脚 · `U_BATPROT` 6 脚 · `U_LDO_S28` 缺 `EN`(3) · `U_SUPV` 缺 `GND`(2) 与 `MR`(3)★)

---

### ★V-3c · ★★★两只【必装】负载开关 `U_EN_SW`/`U_PWR_SW` 的 land 也是通用模板 = 一票否决项 (★本轮新增·★不在原 5 个 ref 里·但同样让板子不完整★)★★★

| 项 | 内容 |
|---|---|
| ★**事实** ★ | ★**[实测] 板面**: `U_EN_SW` / `U_PWR_SW` 的焊盘 = 4 个 (`1,2,3,4`) · 0.6×0.9 mm · 双排 1.27 mm · ★**F.Fab 外形 4.00 × 5.00 mm** ★ ★**[实测] BOM 自己写的 footprint**: 「★**UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch**★」· opn = `TPS22991RAA` · dnp = ★**必装**★ ★**[官网]** TI `TPS22991RAA` = UQFN-4 (RAA) ⇒ ★**0.85 × 0.75 mm 单排 4 脚 @ 0.4 mm pitch** ★ |
| ★**判词** ★ | ★**板面 land 与 BOM 自己写的 footprint 完全不符 ⇒ 两只必装件【装不下去】⇒ 板子不完整** ★ ★**⇒ 不许下料** ★ |
| ★**板那一趟怎么清** ★ | ★**换成 UQFN-4 (RAA) 的真实 land (4 脚单排 @ 0.4 mm pitch, 0.85 × 0.75 mm)** ★ · ★**注意: 这两只与原 5 个 ref 无关, 但同属「通用占位封装」波及面 (作业包 §9-6-3) ⇒ 必须同一趟改** ★ |
| ★**与 `J_DEBUG` 的区别** ★ | ★**`J_DEBUG` 的 1.27 mm land 改项已由 ISS-343 的 `B33_PIN_LAND_1P27` 覆盖, 不重复登记** ★ |

---

### ★V-3 · ★★5 个 ref 的封装与脚号不自洽 = 一票否决项 (★板那一趟必须一次做完★)★★

★**★什么状态下不许下料 (★以下任一条成立 ⇒ 不许下料★)** ★

| # | 不许下料的状态 |
|---|---|
| ★**V-3-①** ★ | ★**`Q1` / `Q2` / `U_BATPROT` / `U_LDO_S28` / `U_SUPV` 任一个的板封装, 与最终 OPN 的真实封装 / 脚号不一致** ★ (★现状 5 个全不一致★) |
| ★**V-3-②** ★ | ★**同族 6 只 TPS7A20 LDO (`U_LDO_IO18` / `U_LDO_L18` / `U_LDO_S12` / `U_LDO_IO33` / `U_LDO_S18B` / `U_LDO_L33`) 的封装几何未一并改正** ★ ⇒ ★**只改 5 个 ref 会留下 100+ 个占位封装 ⇒ 板 md5 变第二次** ★ |
| ★**V-3-③** ★ | ★**BOM 里 `opn` 仍为 `[0数据]` 的器件若要贴装, 而其封装未与最终所选 OPN 对齐** ★ |
| ★**V-3-④** ★ | ★**符号侧缺口未补** ★: `Q1`/`Q2` 的栅脚号未定 (符号各只有 `pin2` 一脚) · `U_BATPROT` 缺 `VSS(4)`/`BAT(5)`/`V–(6)` · `U_LDO_S28` 缺 `EN(3)` · `U_SUPV` 缺 `GND(2)`/`MR(3)` |
| ★**V-3-⑤** ★ | ★**`Q1` / `Q2` 仍共栅** (两者 `pin2` 同挂 `BAT_GATE`) ⇒ 与 BQ2970「原厂要求两管不可共栅」冲突 ⇒ 这是【电气错】不是封装错 ⇒ 同样不许下料 (★详见 V-3b★) |

★**★用什么手段核对** ★: ① 逐条对 TI 官方 datasheet 的封装与脚号 (★本地快照在 `logs/iss354/datasheets/`★) ② 逐条对本机 KiCad 10.0.8 官方封装 (★`Package_TO_SOT_SMD:SOT-23-6` / `SOT-23-5` / `Package_SON:Texas_X2SON-4_1x1mm_P0.65mm` / `Package_SON:Texas_DQK`★) ③ 跑本单机器闸 ★`python3 HW/check_iss354_mfg_closure.py`★ ④ 跑既有覆盖度闸 ★`python3 HW/check_onepass_preflight_coverage.py`★ (★它是钉板闸⑥·只读★)

★**★核对不到怎么办 (★降级★)** ★: ★**把这些位全部留空 (DNP 不贴) + 丝印标「DNP」+ 网表把它们标为「预留」** ★ ⇒ ★**板本体可投产, 型号定了再走「板只改一次」的第二趟** ★ ⇒ ★**★这是唯一可接受的绕法★: 不许「先按通用封装打板, 型号定了再换」★ ★

★**★5 个 ref 的「现封装 vs 应为封装」逐条对照 (★全文 + 证据等级 + 连带影响见 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §9-6-1★)** ★:

| ref | 现封装 [实测] | 应为封装 [官网] | 下料前必须核对 |
|---|---|---|---|
| `Q1` | 5 焊盘 `2..6` · 0.6×0.9 mm · 1.27 mm · 4.94×5.00 mm | ★**TI `CSD16406Q3` = Q3 (VSON-CLIP/DQG) 8 脚 SON 3.3×3.3 mm** (8 × 0.500×0.630 @ pitch 0.650 + 2 个中心大焊盘) ★★★**本机 KiCad 官方库无 TI「DQG」原名封装; 同族起点 = `Package_SON:VSON-8_3.3x3.3mm_P0.65mm_NexFET` ⇒ 仍须按 TI §7.2/§7.3 逐脚核脚号** ★★ | ★**是** ★ |
| `Q2` | 同 `Q1` | 同 `Q1` | ★**是** ★ |
| `U_BATPROT` | 6 焊盘 ★**编号 `2..7`** ★ · 4.94×5.00 mm | ★**TI `BQ2970DSER` = DSE (WSON-6, 1.50×1.50×0.75 mm)** ★ 脚号 1=NC / 2=COUT / 3=DOUT / 4=VSS / 5=BAT / 6=V– ★★**BOM 写的「SOT-23-6」是错的** ★★ | ★**是** ★ |
| `U_LDO_S28` | 4 焊盘 ★**`1,2,4,5` (缺 `EN`(3))** ★ · 4.00×5.00 mm | ★**TI `TPS7A2028DQNR` = X2SON (DQN) 4 脚 1.0×1.0 mm** (或 `TPS7A2028PDBVR` = SOT-23-5, ★**脚号会整体换**★) | ★**是** ★ |
| `U_SUPV` | 4 焊盘 ★**`1,4,5,6` (缺 `GND`(2) 与 `MR`(3))** ★ · 4.00×5.00 mm | ★**TI `TPS3808G01DBVR` = SOT-23 (DBV) 6 脚 2.90×1.60 mm** 脚号 1=RESET / 2=GND / 3=MR / 4=CT / 5=SENSE / 6=VDD | ★**是** ★ |

★**★本节的机器落点** ★: ① 改项清单全文 → ★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §9-6★ (★追加式·老字一字未删★) ② 本单机器闸 → ★`HW/check_iss354_mfg_closure.py`★ (★只读·★不碰任何既有闸★) ③ BOM 候选与代价 → ★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §9-6-5★ + `logs/iss354/` ④ 交卷页 → ★`HANDOFF/2026-11-23_hw-lead_ISS354_demo主板可制造性收口.md`★

★**★边界自证 (★本节自证★)** ★: ★**零写板** (★md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** (★网表 / 脚表 / BOM / 原理图 一字未动★) · ★**零改既有闸** (★`state/gate_check.py` / `state/merge.py` / `HW/check_onepass_preflight_coverage.py` / `HW/check_preflight_regen_idempotent.py` 一字未改★) · ★**零外发** (★不发邮件 / 不询价 / 不问询 / 不采购 / 不联系供应商★) · ★**不替老板拍板** ★
<!-- ISS292:ISS289_APPENDIX:END -->

<!-- ISS304:MD5_ANCHOR:BEGIN -->
## ★ISS-304 追加式订正 (★md5 基线的现值来源已自动化 · 永不再漂★)

★**一句话**: ★★那 4 条台账口径登记 (`W10_MD5_NETLIST` / `W10B_MD5_PINS` / `W10C_MD5_BOM` / `C07_B26_MD5_LEDGER`) 的 `fresh` 格, 现在由【生成器】(★清单页★) 与【同步脚本】(★作业包页★) 从落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 的最新链 §16.2 **现读** ⇒ ★落表一次不必人改 · 读不到就拒写页 (fail-closed) ⇒ 永不再漂★★ ★

★**★现行值 (★台账现读 · ★这三个数由生成器/同步脚本从落表台账现读 · 不许手改★)** ★:

| 文件 | ★**现行值 (★落表台账登记★)** ★ |
|---|---|
| `HW/netlist_v1.csv` | ★**落表台账登记 = «LEDGER_MD5:HW/netlist_v1.csv»** ★ |
| `HW/netlist_v1_pins.csv` | ★**落表台账登记 = «LEDGER_MD5:HW/netlist_v1_pins.csv»** ★ |
| `HW/BOM_v1.csv` | ★**落表台账登记 = «LEDGER_MD5:HW/BOM_v1.csv»** ★ |

★**★老字保留 (★一字未删★)**: ★清单页 §附录 ④ 与作业包 §8.2.3 ⑬ 那三个数 = ★**ISS-283 那一跳** (★台账 L1353·§16.2★) 的**快照**★ ⇒ ★那是【历史留痕】, 不是现值★ ⇒ ★**现行值 = 上表三个数 + 登记表那 4 格的 `fresh`**★ ★

★**★机器判据**: ★`python3 HW/check_workpack_state_values.py` ⇒ ★V4 拿台账现值对 `fresh` 格 ⇒ 漂了当场红★ ★
★**★重锚流程 (★落表之后跑这两条 · 顺序不许换★)**: ① `python3 state/_iss277_build_preflight.py` (★刷清单页★) ⇒ ② `python3 state/_iss304_sync_state_baseline_md5.py` (★刷作业包页 + 生成器的输入 sidecar★) ⇒ ★★跑两次 md5 逐字节相同 = 幂等★★ ★
<!-- ISS304:MD5_ANCHOR:END -->
