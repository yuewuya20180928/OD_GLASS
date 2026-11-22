#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-289 · 把「作业包 / 清单页 的现状值对回盘面实测」写进两份文档 (★追加式★)

★**纯追加: 老字一个字都不删** ★
★**只写 HW/PCB/ 下两份文档 + 本脚本; 零写板 · 零落表 · 零改生成器代码** ★

跑法:
    python3 state/_append_iss289_state_values.py
"""
import json
import os
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WP = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_WORKPACKET.md")
CL = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")

# ==============================================================================
# 现状值登记表 (★两份文档同源 ⇒ 逐字一致★)
# ==============================================================================
R3 = ["python3", "HW/check_netlist_contradiction_r3.py"]
FRAME = ["python3", "HW/check_board_frame_caliber.py"]
PCBNET = ["bash", "state/pcbnew_py.sh", "state/check_pcb_nets.py"]

REFS_PROBE = ["bash", "state/pcbnew_py.sh", "-c",
              "import pcbnew;b=pcbnew.LoadBoard('HW/PCB/demo_mainboard.kicad_pcb');"
              "rs=[f.GetReference() for f in b.GetFootprints()];"
              "print('板侧末字符是字母(要加_1) = %d' % len([r for r in rs if not r[-1].isdigit()]));"
              "print('带 _1 后缀 = %d' % len([r for r in rs if r.endswith('_1')]))"]
BOM_LETTER = ["python3", "-c",
              "import csv;rs={r['ref'] for r in csv.DictReader(open('HW/BOM_v1.csv'))};"
              "print('BOM 位号末字符是字母 = %d' % len([r for r in rs if not r[-1].isdigit()]))"]
PCB_DNP_COUNT = ["python3", "-c",
                 "print(open('HW/PCB/demo_mainboard.kicad_pcb',encoding='utf-8',"
                 "errors='replace').read().lower().count('dnp'))"]

CA_S7 = "### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正"
CA_ISS287 = "### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页"
CA_OTHER = "### ★8.2.3 · 同批一起对回的其余现状值型判据"
CA_CL = "## ★§附录 · ISS-289 追加式订正 (★现状值对回盘面★)"

ENTRIES = [
    # ---------------- 作业包: §3-S7 六处 (43 → 40) ----------------
    dict(id="W01_S7_HEADING", category="dnp_zero_mark", doc="workpacket",
         anchor="### ★S7 · DNP 标记 (★43 个位号·★生成器侧改代码★) ★",
         correction_anchor=CA_S7,
         fresh="S7 · DNP 标记 (★40 个位号·★生成器侧改代码★)",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="§3-S7 段标题的老字是 43 ⇒ 现行值 40"),
    dict(id="W02_S7_QUANT_ZERO", category="dnp_zero_mark", doc="workpacket",
         anchor="★现状: **43 个全部零标记**★",
         correction_anchor=CA_S7,
         fresh="现状: **40 个全部零标记**",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="§3-S7 量化判据第一条"),
    dict(id="W03_S7_QUANT_TOKEN", category="dnp_token_count", doc="workpacket",
         anchor='板文件里 "dnp" 出现次数应从 3 涨到 3 + 43 = 46',
         correction_anchor=CA_S7,
         fresh='板文件里 "dnp" 出现次数应从 3 涨到 3 + 40 = 43',
         expect="3", probe=PCB_DNP_COUNT, probe_regex=r"^(\d+)$",
         note="板文件 dnp 出现次数: 现状 3 (三个层设置) ⇒ S7 跑完 = 3 + 40 = 43"),
    dict(id="W04_S3_TABLE_S7", category="dnp_zero_mark", doc="workpacket",
         anchor="★R3-A4: MAIN_PCB且DNP 54 颗 · 在板上 43 颗 · ★**零标记 43 颗** ★",
         correction_anchor=CA_S7,
         fresh="R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · ★**零标记 40 颗** ★",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="§3 表 S7 行的三个数一起订正 (54/43/43 → 51/40/40)"),
    dict(id="W05_S4_ACCEPT_ROW", category="dnp_zero_mark", doc="workpacket",
         anchor="★**R3-A4 零标记 DNP 数 = 0** ★ (★现状 43★)",
         correction_anchor=CA_S7,
         fresh="R3-A4 零标记 DNP 数 = 0** ★ (★现状 40★)",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="§4 验收表 S1~S7 行"),
    dict(id="W06_S2_X2_PIT", category="dnp_zero_mark", doc="workpacket",
         anchor="43 个 DNP 零标记不是「生成器漏刷」",
         correction_anchor=CA_S7,
         fresh="40 个 DNP 零标记不是「生成器漏刷」",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="§2 的 X-2 坑行"),
    dict(id="W14_S6_1_S7_ROW", category="dnp_zero_mark", doc="workpacket",
         anchor="DNP 标记 (43 个)",
         correction_anchor=CA_S7,
         fresh="DNP 标记 (40 个)",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="§6.1 表 S7 行 (同源第三处)"),
    dict(id="W15_S8_1_3_X4", category="dnp_zero_mark", doc="workpacket",
         anchor="★**X-4 修完 ⇒ 板上有 43 个 DNP 标记**",
         correction_anchor=CA_S7,
         fresh="X-4 修完 ⇒ 板上有 40 个 DNP 标记",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="§8.1.3-3 (同源第三处)"),
    dict(id="W16_S1_1_F3", category="dnp_zero_mark", doc="workpacket",
         anchor="MAIN_PCB 且 DNP 的位号数 54 · 其中在板文件里真实存在的 43 · 零标记的 43",
         correction_anchor=CA_S7,
         fresh="MAIN_PCB 且 DNP 的位号数 51 · 其中在板文件里真实存在的 40 · 零标记的 40",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="§1.1 第 1 行 F3 (同源第三处)"),
    # ---------------- 作业包: ISS-287 两条差异 ----------------
    dict(id="W11_FOOTPRINT_COUNT", category="footprint_count", doc="workpacket",
         anchor="160.10×100.10 mm / 8 铜层 / 186 封装",
         correction_anchor=CA_ISS287,
         fresh="186 封装 (★现状·官方板★) / 185 封装 (★S2 把 `C_VBUS_GND` 拿掉之后★)",
         expect="186", probe=FRAME, probe_regex=r"封装 (\d+)",
         note="官方板 186 / 生成板 185 ⇒ 差 1 = C_VBUS_GND (板级归属差, 不是漏数)"),
    dict(id="W12_S1_BOARD_156", category="ref_suffix", doc="workpacket",
         anchor="★**③ 板侧 186 个封装位号 = 走 S6 重出自动带** ★",
         correction_anchor=CA_ISS287,
         fresh="板侧真正要加 `_1` 的是 156 个 (★官方板 186 个封装里末字符是字母的只有 156 个, 另 30 个末字符是数字不动★)",
         expect="156", probe=REFS_PROBE, probe_regex=r"要加_1\) = (\d+)",
         note="§3-S1 的「板侧 186 个封装位号」会被读成「板上有 186 个要改名」⇒ 错"),
    dict(id="W18_S1_SUFFIX_ONE", category="ref_suffix", doc="workpacket",
         anchor="★**186 个 `X` → `X_1` (★`C_AC_CSI_D0_CK_N` → `C_AC_CSI_D0_CK_N_1`★) · ★**`RAIL_*` / `NET_*` 保留** (★单点汇流位, 改了 BOM 多假料号★) · ★**32 个本来就数字结尾的不动** ★",
         correction_anchor=CA_ISS287,
         fresh="官方板带 `_1` 后缀的位号 = 1 个 (`R_BAT_DET_1`) ⇒ 改完 = 157 个",
         expect="1", probe=REFS_PROBE, probe_regex=r"带 _1 后缀 = (\d+)",
         note="ISS-287 ②: 官方板带 _1 后缀的位号 = 1 个"),
    dict(id="W19_S1_SCH_186", category="ref_suffix", doc="workpacket",
         anchor="★**① 器件位号真源 = `HW/SCHEMATIC_V1_SPEC.json`** (★`devices` 段的 186 个 `ref` ★)",
         correction_anchor=CA_ISS287,
         fresh="原理图 / 网表侧要加 `_1` 的位号 = 186 个 (★218 − 32★) ⇒ 板侧是 156 个, 不是 186 个",
         expect="186", probe=BOM_LETTER, probe_regex=r"= (\d+)$",
         note="186 是原理图侧口径 (BOM 218 − 32); 该 JSON 里没有 devices 键 ⇒ 指针失效 (已登记 need)"),
    dict(id="W13_COPPER_COUNT", category="copper_and_frame", doc="workpacket",
         anchor="| ★**铜层数** ★ | ★**8** ★",
         correction_anchor=CA_ISS287,
         fresh="铜层数 = 8",
         expect="8", probe=FRAME, probe_regex=r"铜层 (\d+)",
         note="铜层 / 板框四数之一"),
    dict(id="W13B_FRAME_BOX", category="copper_and_frame", doc="workpacket",
         anchor="| ★**板框 (Edge.Cuts)** ★ | ★**160.10 × 100.10 mm** ★ |",
         correction_anchor=CA_ISS287,
         fresh="板框 = 160.10 × 100.10 mm",
         expect="160.10 × 100.10 mm", probe=FRAME,
         probe_regex=r"板框 \(含线宽\) = ([\d.]+ × [\d.]+ mm)",
         note="铜层 / 板框四数之二 (宽 × 高)"),
    dict(id="W13C_FRAME_ID", category="copper_and_frame", doc="workpacket",
         anchor="帧 id `B160x100` · 板 160.00×100.00 / 8 铜层 / 1.60mm / 186 封装",
         correction_anchor=CA_ISS287,
         fresh="现役帧 = B160x100",
         expect="B160x100", probe=FRAME, probe_regex=r"现役帧 (\S+)",
         note="铜层 / 板框四数之三 (现役帧 id)"),
    # ---------------- 作业包: 其余现状值型判据 ----------------
    dict(id="W07_FINDINGS_2", category="defect_count", doc="workpacket",
         anchor="★**FINDINGS = 0** ★ (★现状 2 = F2+F3★)",
         correction_anchor=CA_OTHER,
         fresh="FINDINGS = 0** ★ (★现状 2 = F2+F3★",
         expect="2", probe=R3, probe_regex=r"FINDINGS: (\d+)",
         note="无漂 (仍 = 2 = F2+F3), 但登记进闸"),
    dict(id="W08_PINS_DEFECT", category="defect_count", doc="workpacket",
         anchor="★**15 条** (★14 串号 + 1 缺脚: `U_LDO_S28` 无 pin3★)",
         correction_anchor=CA_OTHER,
         fresh="18 条 (★15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账★)",
         expect="18", probe=["python3", "HW/check_pin_function_labels.py"],
         probe_regex=r"(\d+) 条缺陷",
         note="脚表语义缺陷 15 → 18 (落表后 md5 台账对账多 3 条)"),
    dict(id="W09_SAME_PAD_NET", category="defect_count", doc="workpacket",
         anchor="缺失 0 · 同号异网 0",
         correction_anchor=CA_OTHER,
         fresh="缺失 0 · 同号异网 3",
         expect="3", probe=PCBNET, probe_regex=r"同号异网 (\d+)",
         note="落表已改、板还没跟 ⇒ 同号异网 0 → 3 (Q_PG pad1/pad3 + D_ESD_USB_D pad1)"),
    dict(id="W10_MD5_NETLIST", category="md5_baseline", doc="workpacket",
         anchor="★**`HW/netlist_v1.csv`** ★ | ★`e06c1dd633566aa44732762c2ff99d1c` ★",
         correction_anchor=CA_OTHER,
         fresh="落表台账登记 = 37f62ac3f0b81d92ca7d48fdea717f07",
         expect_mode="ledger", expect_target="HW/netlist_v1.csv",
         probe=["md5sum", "HW/netlist_v1.csv"], probe_regex=r"^([0-9a-f]{32})",
         note="网表 md5 基线 ★走落表台账为准, 不写死★ (ISS-283 ⑩-b 的口径)"),
    dict(id="W10B_MD5_PINS", category="md5_baseline", doc="workpacket",
         anchor="★**`HW/netlist_v1_pins.csv`** ★ | ★`287e7861a0d1007748d92d9fbecdd490` ★",
         correction_anchor=CA_OTHER,
         fresh="落表台账登记 = a4270120454aedf7a23c92cd8985c8a6",
         expect_mode="ledger", expect_target="HW/netlist_v1_pins.csv",
         probe=["md5sum", "HW/netlist_v1_pins.csv"], probe_regex=r"^([0-9a-f]{32})",
         note="脚表 md5 基线 ★走落表台账为准★"),
    dict(id="W10C_MD5_BOM", category="md5_baseline", doc="workpacket",
         anchor="★**`HW/BOM_v1.csv`** ★ | ★`94642d07a69e8d60dd2af57f69b93607` ★",
         correction_anchor=CA_OTHER,
         fresh="落表台账登记 = 5d02bece9477ffce5fbe0193c7d5cce4",
         expect_mode="ledger", expect_target="HW/BOM_v1.csv",
         probe=["md5sum", "HW/BOM_v1.csv"], probe_regex=r"^([0-9a-f]{32})",
         note="BOM md5 基线 ★走落表台账为准★"),
    # ---------------- 清单页 ----------------
    dict(id="C01_B17_ZERO_MARK", category="dnp_zero_mark", doc="checklist",
         anchor="[实测] R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗",
         correction_anchor=CA_CL,
         fresh="MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="清单页这条的 current_state 已是 40 (老字保留), 本闸把它钉住"),
    dict(id="C02_B17_ID_NAME", category="dnp_zero_mark", doc="checklist",
         anchor="★**`B17_DNP_43`** ★",
         correction_anchor=CA_CL,
         fresh="条目 id `B17_DNP_43` 保留 (★老字留痕 · 闸的探针键也用它 ★) ⇒ 现行值 = 40",
         expect="40", probe=R3, probe_regex=r"零标记 (\d+) 颗",
         note="条目 id 名字含 43 ⇒ 改名会打断闸的探针键 ⇒ 只加注, 不改名"),
    dict(id="C03_B01_REF_SUFFIX", category="ref_suffix", doc="checklist",
         anchor="[实测] 板文件 186 个封装位号零后缀 ⇒ KiCad 判「未标注」⇒ 218 处问号",
         correction_anchor=CA_CL,
         fresh="板文件 186 个封装位号里 30 个末字符是数字 (含 1 个已带 `_1` 的 `R_BAT_DET_1`) ⇒ 真正要加 `_1` 的是 156 个",
         expect="156", probe=REFS_PROBE, probe_regex=r"要加_1\) = (\d+)",
         note="「186 个封装位号零后缀」这句不成立 (ISS-287 ②)"),
    dict(id="C04_B31_FOOTPRINT_COUNT", category="footprint_count", doc="checklist",
         anchor="[实测] 现役板 = 160×100 台架板 (8 铜层 / 186 封装 / 160.10×100.10)",
         correction_anchor=CA_CL,
         fresh="186 封装 (★现状·官方板★) / 185 封装 (★S2 把 `C_VBUS_GND` 拿掉之后★)",
         expect="186", probe=FRAME, probe_regex=r"封装 (\d+)",
         note="官方板 186 / 生成板 185"),
    dict(id="C05_FRAME_B160X100", category="copper_and_frame", doc="checklist",
         anchor="★**160×100 台架板 (现役板)** · 8 铜层 · 160.10×100.10 · 186 封装 ★",
         correction_anchor=CA_CL,
         fresh="8 铜层 · 160.10×100.10",
         expect="8", probe=FRAME, probe_regex=r"铜层 (\d+)",
         note="铜层 / 板框四数"),
    dict(id="C06_B03_DEFECT_COUNT", category="defect_count", doc="checklist",
         anchor="脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账",
         correction_anchor=CA_CL,
         fresh="脚表 18 条缺陷 = 15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账",
         expect="18", probe=["python3", "HW/check_pin_function_labels.py"],
         probe_regex=r"(\d+) 条缺陷",
         note="脚表缺陷条数 (清单页已更新, 本闸钉住)"),
    dict(id="C07_B26_MD5_LEDGER", category="md5_baseline", doc="checklist",
         anchor="网表 e06c1dd6…",
         correction_anchor=CA_CL,
         fresh="落表台账登记 = 37f62ac3f0b81d92ca7d48fdea717f07",
         expect_mode="ledger", expect_target="HW/netlist_v1.csv",
         probe=["md5sum", "HW/netlist_v1.csv"], probe_regex=r"^([0-9a-f]{32})",
         note="B26 的 md5 基线 ★走落表台账为准, 不写死★"),
]

REGISTRY_JSON = json.dumps(
    {"schema": "board-onepass-state-baseline/v1",
     "generated_by": "ISS-289 hw-lead (2026-11-17)",
     "note": "★期望值写在文档里 (不写死在闸里) ⇒ 文档漂了当场红; md5 基线的取值来源 = 落表台账 (HW/landing_md5.py)★",
     "state_baseline": {"entries": ENTRIES}},
    ensure_ascii=False, indent=2)

# ==============================================================================
# 作业包追加段
# ==============================================================================
WP_PROSE = """
---

## ★8.2 · ★★ISS-289 追加式订正 (★2026-11-17 15:0x · ★「板只改一次」那一趟的【全部现状值型判据】对回盘面实测 ★)★★

> ★**本节 = 追加式 (★§8.1 及其以上的字一行没删 ★)** ★
> ★**本节只订正【现状值型判据】(= 写死的现状数字), 一个字都不改「该做什么」★** ★
> ★**机器闸**: `python3 HW/check_workpack_state_values.py` (★V1~V7★) + `--selftest` ⇒ ★**「作业包 + 清单页里的现状值 == 盘面实测」当场判红, 不许等到动板那趟才发现** ★

★**★订正的唯一根因 (★三次合法落表 ★)** ★
★**2026-11-17 09:58:16 (V-3=E) + 12:16:08 (V-5) + 12:30:23 (V-6) 三次落表 (★ISS-283 · 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 链头 L1353 ★) 把 BAT_DET 三颗 (`R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT`) 从 DNP 改成【必装】** ★
⇒ ★**R3-A4 的三个数: MAIN_PCB且DNP 54 → **51** 颗 · 在板上 43 → **40** 颗 · 零标记 43 → **40** 颗** ★
⇒ ★**★照 43 走 = 要么 S7 验收假红, 要么为了凑够 43 把刚落表的三颗必装又标回 DNP ⇒ ★★那等于把老板 09:49 拍板并已落表的三颗必装改回去★★ ★** ★

### ★8.2.1 · 六处 S7 现状值 (43 → 40) 逐条订正 (★老字一字未删 ★)

★**★六处 (主判据) —— 逐处对应任务书 §① 的表 ★** ★

| # | 作业包位置 | 老字 (★原样保留, 一字未删 ★) | ★**现行值 (★盘面实测★)** ★ | 实测命令 (★本机实跑★) |
|---|---|---|---|---|
| ① | ★**§3-S7 段标题** ★ | `### ★S7 · DNP 标记 (★43 个位号·★生成器侧改代码★) ★` | ★**S7 · DNP 标记 (★40 个位号·★生成器侧改代码★)** ★ | `python3 HW/check_netlist_contradiction_r3.py` ⇒ `R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · 零标记 40 颗` |
| ② | ★**§3-S7 量化判据 (第一条)** ★ | `★现状: **43 个全部零标记**★` | ★**现状: **40 个全部零标记**★** ★ | 同 ① |
| ③ | ★**§3-S7 量化判据 (第二条)** ★ | `板文件里 "dnp" 出现次数应从 3 涨到 3 + 43 = 46` | ★**板文件里 "dnp" 出现次数应从 3 涨到 3 + 40 = 43** ★ | 板文件 "dnp" 出现次数 = **3** (三个层设置) ⇒ S7 跑完 = **43** (= 3 + 40) |
| ④ | ★**§3 表 S7 行** ★ | `★R3-A4: MAIN_PCB且DNP 54 颗 · 在板上 43 颗 · ★**零标记 43 颗** ★` | ★**★R3-A4: MAIN_PCB且DNP 51 颗 · 在板上 40 颗 · ★**零标记 40 颗** ★** ★ | 同 ① |
| ⑤ | ★**§4 验收表 S1~S7 行** ★ | `★**R3-A4 零标记 DNP 数 = 0** ★ (★现状 43★)` | ★**★**R3-A4 零标记 DNP 数 = 0** ★ (★现状 40★)** ★ | 同 ① |
| ⑥ | ★**§2 的 X-2 坑行** ★ | `43 个 DNP 零标记不是「生成器漏刷」` | ★**40 个 DNP 零标记不是「生成器漏刷」** ★ | 同 ① |

★**★同源三处 (★同一根因, 一并订正 ★)** ★

| # | 作业包位置 | 老字 (★原样保留, 一字未删 ★) | ★**现行值** ★ |
|---|---|---|---|
| ⑦ | ★**§6.1 表 S7 行** ★ | `DNP 标记 (43 个)` | ★**DNP 标记 (40 个)** ★ |
| ⑧ | ★**§8.1.3-3 (X-4 修完)** ★ | `★**X-4 修完 ⇒ 板上有 43 个 DNP 标记**` | ★**X-4 修完 ⇒ 板上有 40 个 DNP 标记** ★ |
| ⑨ | ★**§1.1 第 1 行 (F3)** ★ | `MAIN_PCB 且 DNP 的位号数 54 · 其中在板文件里真实存在的 43 · 零标记的 43` | ★**MAIN_PCB 且 DNP 的位号数 51 · 其中在板文件里真实存在的 40 · 零标记的 40** ★ |

★**★⇒ S7 的验收目标写死成 40 (★不是 43★) —— ★★照 43 走 = 验收假红, 或者为了凑 43 把刚落表的三颗必装改回 DNP (= 把老板拍板 undo)★★ ★** ★

### ★8.2.2 · ISS-287 那两条差异对回作业包 / 清单页 (★沙盒干跑探针 13:49~14:2x 实测 ★)

★**★本节订正后的现值 (★逐条 = 闸的登记表里的 `fresh` 原句 ★)** ★

| 条目 | ★**订正后的现值** ★ |
|---|---|
| 封装数 | ★**186 封装 (★现状·官方板★) / 185 封装 (★S2 把 `C_VBUS_GND` 拿掉之后★)** ★ |
| S1 改名数 (板侧) | ★**板侧真正要加 `_1` 的是 156 个 (★官方板 186 个封装里末字符是字母的只有 156 个, 另 30 个末字符是数字不动★)** ★ |
| 带 `_1` 后缀的位号 | ★**官方板带 `_1` 后缀的位号 = 1 个 (`R_BAT_DET_1`) ⇒ 改完 = 157 个** ★ |
| S1 改名数 (原理图侧) | ★**原理图 / 网表侧要加 `_1` 的位号 = 186 个 (★218 − 32★) ⇒ 板侧是 156 个, 不是 186 个** ★ |
| 铜层数 | ★**铜层数 = 8** ★ |
| 板框 | ★**板框 = 160.10 × 100.10 mm** ★ |
| 现役帧 | ★**现役帧 = B160x100** ★ |

★**★① 封装数: 官方板 186 vs 沙盒生成板 185 ⇒ 差的那 1 个是 `C_VBUS_GND` ★** ★

| 项 | 实测值 | 读法 |
|---|---|---|
| ★**官方板 (真盘, 唯一官方)** ★ | ★**186 个封装 / 186 个唯一位号 / 零重复** ★ | `bash state/pcbnew_py.sh` 读板 (★ISS-287 `logs/iss287/refdiff3.log`★) |
| ★**沙盒生成板 (MAIN_PCB 纯口径)** ★ | ★**185 个封装** ★ | 生成器 `[板级过滤] MAIN_PCB` 把 CHG_BOARD 的件剔掉 |
| ★**差的那 1 个** ★ | ★**`C_VBUS_GND`** ★ (★网表 `HW/netlist_v1.csv:10` 与 `:12` 的 board 列 = `CHG_BOARD` + dnp=DNP, 但官方板上有实物封装 @ (107.70, 42.50) 且未打 DNP 标记★) | ★**不是漏数, 不是位号改名, 是【板级归属差】★** |

★**★结论 (★必须写明「动板那趟按哪个数走」★)** ★
- ★**① 现状值 = 186 (官方板) ⇒ 作业包正文里写死的「186 封装」那一格, 现状是对的, 不用改数字 ★**
- ★**② 但「那一趟收工后」= 185 ⇒ 因为 §3-S2 的判据是「C1 多余 0」, 而多余的那 2 个焊盘就是 `C_VBUS_GND` ⇒ 它必须下板 ⇒ 板从 186 变 185** ★
- ★**★⇒ 动板那一趟按【官方板 (真盘) 的数】走, 并且两个数都要写进那一趟的任务书: 开工前 186 / 收工后 185 ★** ★
- ★**★⇒ 不许拿 186 去卡那一趟的板 (★那是假红★), 也不许拿 185 去描述现在的板 (★那是错话★)** ★
- ★**★⇒ 185 不是「少了一件」, 是「MAIN_PCB 纯口径」—— 与 ISS-287 B4-B 逐字一致; ★★而「重跑生成器 ⇒ `C_VBUS_GND` 从板上掉下来」这件事, 归 ISS-287 B4-D 的路线甲/乙裁决 (★我不拍★)★★ ★**

★**★② 带 `_1` 后缀的位号: 现在 1 个 (`R_BAT_DET_1`) ⇒ 改完 157 个, 不是 186 个 ★** ★

| 口径 | 实测 | 读法 |
|---|---|---|
| ★**官方板 186 个封装里末字符是字母 (⇒ 要加 `_1`)** ★ | ★**156** ★ | `bash state/pcbnew_py.sh` 读板 |
| ★**官方板 186 个封装里末字符是数字 (⇒ 不动)** ★ | ★**30** ★ | 同上 (含 `R_BAT_DET_1` / `R_BAT_DET_2` / `J_SOM_P1..P4` 等) |
| ★**官方板带 `_1` 后缀的位号 (现状)** ★ | ★**1 个 (`R_BAT_DET_1`)** ★ | 同上 ⇒ ★**★所以「板文件 186 个封装位号零后缀」这句是错的 (★清单页 `B01_REF_SUFFIX` 那条也是★)★** ★ |
| ★**原理图 / 网表侧要加 `_1` 的位号** ★ | ★**186** ★ (★218 − 32★) | `HW/BOM_v1.csv` 218 个位号里末字符是字母的 186 个 |
| ★**★改完之后板上带 `_1` 后缀的位号** ★ | ★**157** ★ (★156 + `R_BAT_DET_1` 那 1 个★) | 若那一趟连 S2 一起跑 (板变 185) ⇒ 变 **156** (★`C_VBUS_GND` 也是字母结尾, 要下板★) |

★**★结论** ★
- ★**★§3-S1 的「186 个 `X` → `X_1`」是【原理图侧】口径 (★218 − 32 = 186★) —— 数字本身没错; 但同一行的「③ 板侧 186 个封装位号 = 走 S6 重出自动带」会被读成「板上有 186 个要改名」⇒ 那是错的 ⇒ 板侧真正要改的是 156 个 (收工后 155 个) ★** ★
- ★**★⇒ 板那一趟的 S1 验收数字: 改名数 = 156 (★收工后 155★) / 带 `_1` 后缀数 = 157 (★收工后 156★) —— ★★拿 186 去数板上的 `_1` = 假红 ★** ★
- ★**★⇒ 另: §3-S1 写的位号真源 `HW/SCHEMATIC_V1_SPEC.json` 的 `devices` 段, ★★盘上这个 JSON 里没有 `devices` 键★★ (★实测: 顶层只有 meta / counts / connections / power_rails / display_select / testpoints / undrawable 七个键★) ⇒ ★**这是 ISS-281 同型的「判据引用了盘上不存在的字段」⇒ 已登记 need 给 main, 本单只登记不拍** ★

### ★8.2.3 · 同批一起对回的其余现状值型判据 (★漂 3 处 + 无漂 1 处 ★)

| # | 作业包位置 | 老字 (★原样保留, 一字未删 ★) | ★**现行值 (★盘面实测★)** ★ | 实测命令 |
|---|---|---|---|---|
| ⑩ | ★**§1.5 脚表语义缺陷** ★ | `★**15 条** (★14 串号 + 1 缺脚: `U_LDO_S28` 无 pin3★)` | ★**18 条 (★15 条脚表功能缺陷 (14 串号 + 1 缺脚) + 3 条 md5 台账对账★)** ★ | `python3 HW/check_pin_function_labels.py` ⇒ `❌ 不过 (18 条缺陷)` |
| ⑪ | ★**§1.5 板↔网表焊盘级** ★ | `缺失 0 · 同号异网 0` | ★**缺失 0 · 同号异网 3** ★ | `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ `★错: Q_PG pad1 / Q_PG pad3 / D_ESD_USB_D pad1` (★落表已改, 板还没跟 ⇒ 已在清单页 `B11` / `B32` 登记★) |
| ⑫ | ★**§4 验收表 findings** ★ | `★**FINDINGS = 0** ★ (★现状 2 = F2+F3★)` | ★**★**FINDINGS = 0** ★ (★现状 2 = F2+F3★)** ★ (★无漂, 但登记进闸★) | `python3 HW/check_netlist_contradiction_r3.py` ⇒ `FINDINGS: 2` |

★**★⑬ md5 基线 (§5 表的三行) —— ★走落表台账为准, 不写死★** ★

| 文件 | 老字 (★01:3x 实测值, 原样保留 ★) | ★**现行值 (★落表台账登记★)** ★ |
|---|---|---|
| `HW/netlist_v1.csv` | `e06c1dd633566aa44732762c2ff99d1c` | ★**落表台账登记 = 37f62ac3f0b81d92ca7d48fdea717f07** ★ (★ISS-283 · 台账 L1353·§16.2★) |
| `HW/netlist_v1_pins.csv` | `287e7861a0d1007748d92d9fbecdd490` | ★**落表台账登记 = a4270120454aedf7a23c92cd8985c8a6** ★ (★同上★) |
| `HW/BOM_v1.csv` | `94642d07a69e8d60dd2af57f69b93607` | ★**落表台账登记 = 5d02bece9477ffce5fbe0193c7d5cce4** ★ (★同上★) |

★**★⇒ 基线【取值来源】已经换了 (★台账★), 不再是写死的数字 ⇒ 下次落表, 闸自己去台账取新值, 不必改闸 ★** ★

### ★8.2.4 · 新闸 (★「现状值漂移当场红」★)

| 项 | 内容 |
|---|---|
| ★**闸** ★ | `python3 HW/check_workpack_state_values.py` (★V1~V7★) |
| ★**反向用例** ★ | `python3 HW/check_workpack_state_values.py --selftest` (★10 条, 每条自证改到了目标★) |
| ★**七条判据** ★ | ★**V1** 登记表结构 (★两份文档逐字一致★) · ★**V2** 追加式自证 (★老字原句还在★) · ★**V3** 订正块在位且自带现值 · ★**V4** 现状值 == 盘面实测 (★实跑探针★) · ★**V5** 七类覆盖 (★少一类即红★) · ★**V6** 受保护 5 件 md5 (★网表/脚表/BOM 走落表台账★) · ★**V7** 探针真实性 + 测量源多样性 ★ |
| ★**七个必备类别** ★ | `dnp_zero_mark` / `footprint_count` / `dnp_token_count` / `defect_count` / `md5_baseline` / `copper_and_frame` / `ref_suffix` |
| ★**★为什么是七类而不是一条 DNP 探针** ★ | ★**每次落表都会改盘面真值 (★DNP 颗数 / 缺陷条数 / md5 基线 / 脚表行数★) ⇒ 只盯 DNP 一条, 下次落表照样漂别的 ⇒ ★★闸必须把七类现状值全盯住, 少一类即红★★ ★ |
| ★**期望值写在哪儿** ★ | ★**写在两份文档的 `state_baseline` JSON 块里 (★不写死在闸里★) ⇒ 文档漂了当场红; md5 基线的【取值来源】是落表台账 (`HW/landing_md5.py`) ⇒ ★**落表一次, 闸自己知道新基线, 不必改闸** ★ |
| ★**与既有闸的关系** ★ | `HW/check_onepass_preflight_coverage.py` (★P5 管【清单页 5 个现状探针】★) ⇒ ★**本闸 = 它的升级版: 把【作业包正文里的现状值型判据】也纳进来, 并从 5 个探针扩到七类 ★** ★ |

### ★8.2.5 · 现状值登记表 (★机器可读 · 两份文档同源 · 逐字一致★)

★**★这块 JSON 是【闸的唯一数据源】—— 期望值写在文档里, 不写死在闸里 ⇒ 文档的现状值漂了, 闸当场红 ★** ★
★**格式**: `state_baseline.entries[]` 每条 = `id` / `category` / `doc` / `anchor` (★老字原句★) / `correction_anchor` (★订正块★) / `fresh` (★订正后的现值句★) / `expect` (★或 `expect_mode`=ledger + `expect_target`★) / `probe` / `probe_regex` / `note` ★
★**★清单页 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 §附录 里有【逐字相同的一块】⇒ 闸会查两份是否分叉 ★** ★

```json
%s
```

★**★本节全部数字都是本机实跑 (★`bash state/pcbnew_py.sh` 读板 / 各闸原始输出 / ISS-287 `logs/iss287/*` ★), 没有一条是估的★★** ★
"""

# ==============================================================================
# 清单页追加段
# ==============================================================================
CL_PROSE = """
---

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
%s
```

★**★本页的每个数字都是本机实读, 没有一条是估的★★** ★
"""

WP_APPEND = WP_PROSE % REGISTRY_JSON
CL_APPEND = CL_PROSE % REGISTRY_JSON

def append_once(path, marker, block, doc_key):
    """★追加 (★若之前追加过 ⇒ 先把旧的那段截掉再重写, ★老字 (前面部分) 一个字节不动 ★)★"""
    txt = open(path, encoding="utf-8").read()
    if marker in txt:
        i = txt.index(marker)
        cut = txt.rfind("\n---\n", 0, i)
        if cut < 0:
            cut = i
        prefix = txt[:cut]
        print("★已存在旧追加段 ⇒ 截掉重写 (★前 %d 字符不动 ★): %s" % (len(prefix), path))
        miss = [e["id"] for e in ENTRIES
                if (e["doc"] == doc_key) and (e["anchor"] not in prefix)]
        if miss:
            print("❌ 截断后老字没了 ⇒ 停 (id=%s)" % miss[:5])
            sys.exit(1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(prefix)
        with open(path, "a", encoding="utf-8") as f:
            f.write(block)
        new = open(path, encoding="utf-8").read()
        assert new.startswith(prefix), "★前缀被改了 ⇒ 停★"
        print("★已重写 %s (+%d 字节) (★前缀逐字节不变 ✔★)" % (path, len(block.encode("utf-8"))))
        return True
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)
    print("★已追加 %s (+%d 字节)" % (path, len(block.encode("utf-8"))))
    return True


def selfcheck():
    """★追加前自检: 每条的 anchor / correction_anchor / fresh 必须在目标文档里找得到 ★"""
    bad = []
    for e in ENTRIES:
        p = WP if e["doc"] == "workpacket" else CL
        txt = open(p, encoding="utf-8").read()
        prose = WP_PROSE if e["doc"] == "workpacket" else CL_PROSE
        if e["anchor"] not in txt:
            bad.append("id=%s 的 anchor 不在 %s" % (e["id"], os.path.basename(p)))
        if e["correction_anchor"] not in prose:
            bad.append("id=%s 的 correction_anchor 不在追加段的正文里" % e["id"])
        if e["fresh"] not in prose:
            bad.append("id=%s 的 fresh 不在追加段的正文里 (★只写在登记表里 = 闸查不到★)" % e["id"])
    if bad:
        print("❌ 自检不过:")
        for b in bad:
            print("   -", b)
        sys.exit(1)
    print("★自检过: %d 条登记的 anchor / correction_anchor / fresh 全部就位" % len(ENTRIES))


if __name__ == "__main__":
    selfcheck()
    append_once(WP, "## ★8.2 · ★★ISS-289 追加式订正", WP_APPEND, "workpacket")
    append_once(CL, "## ★§附录 · ISS-289 追加式订正", CL_APPEND, "checklist")
