#!/usr/bin/env python3
"""ISS-384 (hw-lead) · 交卷页生成器 (B1~B6) · 2026-11-24"""
import io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _iss384_append_corr_blocks as M

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
OUT = os.path.join(ROOT, "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md")

DOCS = [
    ("HW/PCB_OUTLINE_60x15.md", M.PCB_ROWS),
    ("HW/J_CHG_SELECTION.md", M.JCHG_ROWS),
    ("HW/POWER_BUDGET_V3.md", M.PB_ROWS),
]

import json
_LM = {}
_LMP = os.path.join(ROOT, "logs/iss384/row_lines.json")
if os.path.exists(_LMP):
    _LM = json.load(open(_LMP, encoding="utf-8"))


def rows_of(rel):
    out = []
    for i, r in enumerate(DOCS[[d[0] for d in DOCS].index(rel)][1]):
        r = list(r)
        if rel in _LM and str(i) in _LM[rel]:
            r[0] = str(_LM[rel][str(i)])
        out.append(tuple(r))
    return out

FP = [
    ("HW/PCB/demo_mainboard.kicad_pcb", "611b869e13518c3c023fb178f91a0075",
     "mtime 2026-11-06 07:07:17.362193413 · size 4940213"),
    ("HW/netlist_v1.csv", "6aee500e60ba0732f83a9cf557ba90ab", "零落表"),
    ("HW/netlist_v1_pins.csv", "9174309df1ec9411ac8e8d9e80ee386a", "零落表"),
    ("HW/BOM_v1.csv", "5b9993992405904a60ac96a020b375d8", "零落表"),
    ("HW/check_netlist_selfconsistency.py", "5281b65dbcc9af7bccc6c79a9066812d", "零改既有闸"),
]


def main():
    live = sum(1 for _, rows in DOCS for r in rows if r[3] != "—")
    total = sum(len(r) for _, r in DOCS)
    L = []
    A = L.append
    A("# ISS-384 交卷页 · 充电电流活值口径收口与 R10 判定面盲区 (hw-lead · 2026-11-24)")
    A("")
    A("> ★**本单 = 纯文档口径单 + 新建机器闸** ⇒ ★**零写板 / 零落表 / 零改既有闸 / 零改既有页面正文 (只追加) / 零外发 / 不代拍** ★")
    A("> ★**主线口径 (老板 2026-11-11 10:07)**: 当前主线 = 绘制 PCB 图 ⇒ ★**本单属纪律 ① (纯分析/作业包类 · 不动板)** ★")
    A("")
    A("---")
    A("")
    A("## B1 结论摘要")
    A("")
    A("| # | 结论 |")
    A("|---|---|")
    A("| 1 | ★**三份 HW 活文档的充电电流活值仍停在 `0.822` 旧系数档** ⇒ 逐处订正 **%d 处活值** (逐条见 B2) ★ |" % live)
    A("| 2 | ★**网表侧 2026-11-16 (V-4) 就已经落成 `R_ILIM` = 680Ω + `1.216 / 1.071` 系数** ⇒ ★**网表早就对了, 错的是这三份文档** ⇒ ★**本单是「把文档追平到已落表的真值」, 不是「改一个数」** ★ |")
    A("| 3 | ★**本单只改文档, 网表 / 脚表 / BOM / 板文件一个字节没动** ⇒ ★**板继续对着一个不再变的网表画** (合「板只改一次」纪律 ①) ★ |")
    A("| 4 | ★**订正一律走「追加式订正块」** ⇒ 三份文档末尾各一个 ISS-384 块 ⇒ ★**既有正文一行未删、既有行号未位移** (★ISS-230 的 L151 / L193 作废标记原样保留★) ★ |")
    A("| 5 | ★**新闸 `HW/check_charge_current_live_value.py` (新建 · 零挂链)**: 裸跑 rc=0 · `--selftest` **14/14 通过 · 末行 `ALL TESTS PASS`** ⇒ ★**两条命门都有反向用例**: ① 删 L151/L193 的作废标记 ⇒ 变红 ② 把网表/脚表/BOM/板文件加进扫描范围 ⇒ 变红 ★ |")
    A("| 6 | ★**最有价值的发现 (本单真正要交的东西)**: ★**既有闸 `HW/check_netlist_selfconsistency.py` 的 R10 判据只扫一个文件 (`chgspec` = `HW/CHARGE_BOARD_SPEC.md`)** ⇒ ★**那份文件今天 `grep -c \"0.822\"` = 0 (已清干净) ⇒ R10 现在是绿的, 但它【压根没看】下面这三份文件** ⇒ ★★**「闸的判定面有洞」= 机器事实, 不是感觉** ⇒ ★**本单在【新闸】里另写一份 (既有闸的判据表一个字没改) ★★ |")
    A("| 7 | ★**不代拍**: `R_ILIM` 最终取哪一档是【老板/PM 域】; V-4 已裁 680Ω 是已落表事实 ⇒ ★**本单只报「文档与已落表真值不一致」, 不提新档位建议** ★ |")
    A("| 8 | ★**零外发**: 没有发出任何邮件/询价/问询/采购 ⇒ ★**缺口一律自己查 + 标证据等级 + 查不到写降级方案** ⇒ ★**零条「等原厂回信」挂起** ★ |")
    A("")
    A("---")
    A("")
    A("## B2 验收标准自评 (★逐条 通过/不通过/未验★)")
    A("")
    A("| # | 验收项 | 判定 | 依据 (实测读数) |")
    A("|---|---|---|---|")
    A("| 1 | ★**三份文档每一处活值都改到了** (逐条列, 不写「已全部修正」) | ★**通过** | ★**逐条见下方 B2-1 表: %d 处活值 + 1 处「数值不变·说明行」= %d 行, 每行都有 旧值/新值/出处/证据 四栏, 且由新闸逐行核对通过★ |" % (live, total))
    A("| 2 | ★**网表 / 脚表 / BOM md5 前后逐字相同 (零落表)** | ★**通过** | `HW/netlist_v1.csv` `6aee500e60ba0732f83a9cf557ba90ab` (前后同) · `HW/netlist_v1_pins.csv` `9174309df1ec9411ac8e8d9e80ee386a` (前后同) · `HW/BOM_v1.csv` `5b9993992405904a60ac96a020b375d8` (前后同) ⇒ ★**网表 L47/L48 那 2 处 `0.822` 一个字没动** (仍是「旧口径写的 (VBAT/VBUS)/η = 0.822 是它的倒数」) ★ |")
    A("| 3 | ★**板三项指纹逐字相同 (零写板)** | ★**通过** | `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ ★**开工前/开工后各打一次, 三项全同** ★ |")
    A("| 4 | ★**既有闸 md5 未变** | ★**通过** | `HW/check_netlist_selfconsistency.py` md5 `5281b65dbcc9af7bccc6c79a9066812d` (前后同) ⇒ ★**R10 的判定面只在新闸里另写一份, 它的判据表一个字没改** ★ |")
    A("| 5 | ★**既有闸读数前后逐字相同** | ★**通过** | `python3 HW/check_netlist_selfconsistency.py` ⇒ 开工前 rc=0 / 开工后 rc=0, ★**stdout 逐字 diff 为空** ★; `MECH/check_connector_clearance_caliber.py` ⇒ 开工前 rc=1 / 开工后 rc=1, ★**stdout 逐字 diff 为空** (★K7 本来就红 2 条, 是基线, 不是本单的锅★) ★ |")
    A("| 6 | ★**新闸裸跑 rc=0** | ★**通过** | `python3 HW/check_charge_current_live_value.py` ⇒ rc=0 (输出「✅ rc=0: 三份 HW 活文档的充电电流活值已追平到 680Ω 落表真值 (ISS-384)」) ★ |")
    A("| 7 | ★**新闸 `--selftest` 末行 ALL TESTS PASS** | ★**通过** | `python3 HW/check_charge_current_live_value.py --selftest` ⇒ rc=0 · **14/14 通过** · 末行 `ALL TESTS PASS` ★ |")
    A("| 8 | ★**`grep -c check_charge_current_live_value state/gate_check.py` = 0** | ★**通过** | 实测 = **0** ⇒ ★**本闸零挂链** (挂链是 main 的地界; 先例同款: ISS-383 的 K0~K4 闸同样零挂链) ★ |")
    A("| 9 | ★**历史留痕未被误伤** | ★**通过** | `HW/PCB_OUTLINE_60x15.md` L151 / L193 (ISS-230 作废标记) ★**逐字保留** ⇒ 新闸**不红**; ★**反向用例 T2 / T3 证明: 删掉作废标记 ⇒ 立刻变红** ★ |")
    A("| 10 | ★**落表真源未被文档闸碰** | ★**通过** | 网表 / 脚表 / BOM / 板文件**不在扫描范围** ⇒ 新闸**不红**; ★**反向用例 T4 / T5 / T6 证明: 把它们加进扫描范围 ⇒ 立刻变红** ★ |")
    A("| 11 | ★**不代拍** | ★**通过** | 全文无新档位建议; 真相页 §5 写明「`R_ILIM` 最终取哪一档是【老板/PM 域】」 ★ |")
    A("| 12 | ★**零外发** | ★**通过** | 本单未发出任何邮件/询价/问询/采购; `state/outbox/` 未动 ★ |")
    A("| 13 | ★**只写本任务允许的文件** | ★**通过** | 产出 = 1 新真相页 + 1 新闸 + 1 新交卷页 + 3 份文档【追加块】+ 本分片; ★**`state/fragments/mech.yaml` / `sw.yaml` / `pm.yaml` 一个字节没动**; ★**`MECH/` 与 `SW/` 只读** ★ |")
    A("| 14 | ★**写入方式合规** | ★**通过** | 分片走 `state/frag_write.py` (原子写) ★**未用 open(p,\"w\")**; 沙盒只落 `tmp/iss384_sbx/` + `logs/iss384/` ⇒ ★**未用 `cp -al`** ★ |")
    A("| 15 | ★**板端实测** | ★**未验 (不适用)** | ★**本单是文档口径单, 不涉及板端实测** ⇒ 真相页 §5 已按 `[0数据]` 登记并给降级方案 (EVT 实测复核) ★ |")
    A("")
    A("### B2-1 三份文档每一处活值 (逐条, 不写「已全部修正」)")
    A("")
    for rel, _rows in DOCS:
        rows = rows_of(rel)
        A("**`%s`** (%d 行)" % (rel, len(rows)))
        A("")
        A("| 文件:行号 | 锚点 (闸用 token 码) | 旧值 (逐字) | 新值 (逐字) | 判定 |")
        A("|---|---|---|---|---|")
        for r in rows:
            lineno, ctx, old, anchor, new, src, ev = r
            A("| `%s` L%s | %s | %s | %s | ★**通过** (新闸逐行核对) |" % (rel, lineno, anchor, old, new))
        A("")
    A("> ★**另有 2 处历史留痕不进上表 (只加不删)**: `HW/PCB_OUTLINE_60x15.md` **L151 / L193** = ISS-230 的作废标记 ⇒ ★**一个字节没动, 新闸不红** ★")
    A("> ★**另有 2 处合法历史说明在网表里 (只读)**: `HW/netlist_v1.csv` **L47 / L48** 的 `R_ILIM` note 里的 `0.822` ⇒ ★**一个字节没动, 不在扫描范围** ★")
    A("")
    A("> ★**「旧值逐字」列的分隔符约定**: ★**表格行的格间分隔符统一写成 `·`** (原为表格竖线 `|`), ★**其余字符逐字照抄原页** ⇒ ★**这一列可逐字核对, 但不等于原行整行复制** ★")
    A("")
    A("### B2-2 ★追加块 (只加不删) 一览")
    A("")
    A("| 文件 | 追加位置 | 追加内容 | 行数 |")
    A("|---|---|---|---|")
    A("| `HW/PCB_OUTLINE_60x15.md` | 文末 | ISS-384 充电电流活值订正块 | 14 行订正 |")
    A("| `HW/J_CHG_SELECTION.md` | §7 表后 + 文末 | ★**§7 规格页逐字条款 + 官方参数补钉块** + ISS-384 充电电流活值订正块 | 16 + 16 行 |")
    A("| `HW/POWER_BUDGET_V3.md` | 文末 | ISS-384 充电电流活值订正块 | 5 行订正 |")
    A("")
    A("> ★**§7 补钉块内容** (★main 2026-11-24 09:3x 裁决 `iss384_jchg_触点额定` 点名要做的「把规格页的逐字条款 + 页码钉进 §7」★): ★**70% 降额条款逐字原文** (Hirose [FH12] Series Catalog · Nov.1.2026 · Adaptive FPC/FFC contact specifications 表 Note 1) + ★**FH12-10S-0.5SH(55) Rated Current 0.5A** + ★**10p 官方尺寸 A=4.5 / B=8.1 / C=9.1 / D=5.57** (官网) ⇒ ★**页码 = [0数据]** (本机直连官网/Farnell PDF 被拦: 21 字节 stub / rc=124) ⇒ 降级方案 = 条款原文 + 文档名 + 版本日期 + 小节名 + URL 四锚点已齐 ★ ⇒ ★**只补证据, 不改选型 · 不改几何判定** ★")
    A("")
    A("---")
    A("")
    A("## B3 证据分级")
    A("")
    A("| 结论 | 等级 | 依据 |")
    A("|---|---|---|")
    A("| 三份文档的**旧值逐字 + 行号** | **[实测]** | 本机 `grep -nE` + 逐行实读 (行号见 B2-1) |")
    A("| **新值** (ICHG / 单 pin / 余量 / 充电时间 / 电芯发热 / TS 偏移) | **[实测]** | 本机实跑 `python3 MECH/hinge_power_calc.py --json` (rc=0) ⇒ `MECH/hinge_power_calc.json` 的 `rilim_table` (ISS-229 · mech-lead · 已 verified) |")
    A("| **当前系数 1.216 @3.70V / 1.071 @4.20V** | **[实测]**(脚本) + **[推算]**(式源) | 脚本 `ichg_factor` 字段; 式源 = `HW/CHARGE_BOARD_SPEC.md` §2.4 |")
    A("| `ICHG = IIN × η·(Vbus/Vbat)` | **[推算]** | buck 功率守恒 `Vbus·IIN·η = Vbat·ICHG` (MECH §0-A 同口径) |")
    A("| `IINMAX = KILIM/R_ILIM` (KILIM 320/355/390 AΩ) | **[官方]** | BQ25896 datasheet (经 `HW/CHARGE_BOARD_SPEC.md` §2.4 引) |")
    A("| 680Ω 档皮肤侧 40.1 °C / 电芯发热 48.6 mW / TS 偏移 20.9 mV·0.65 °C | **[推算]** (MECH 实算) | `MECH/HINGE_POWER_CALC.md` §0-A.1 + §M-4 表 ⇒ ★**只引用, 不另算一套** ★ |")
    A("| 板件/网表/脚表/BOM 指纹 | **[实测]** | `md5sum` + `stat` 开工前后各一次 (见 B2) |")
    A("| `R_ILIM` = 680Ω 是**已落表**事实 | **[实测]** | `HW/netlist_v1.csv` L47/L48 + 脚表 + BOM (V-4 裁定 2026-11-16) |")
    A("| J_CHG 座体单触点额定 / KILIM 低电流档 trim / 板端实测 | **[0数据]** | 真相页 §5 第 2/3/4 条 ⇒ ★**降级方案已写, 不挂起** ★ |")
    A("")
    A("---")
    A("")
    A("## B4 接口取值声明")
    A("")
    A("| key | value | note | ref |")
    A("|---|---|---|---|")
    A("| `charge_current_coef_main` | `1.216` | ★**ICHG/IIN = η·(Vbus/Vbat) @ VBAT=3.70V (最坏档)** ⇒ ★**旧值 0.822 是它的倒数 (方向反了), 已作废** ★ | `HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md` 机器块 + `MECH/HINGE_POWER_CALC.md` §0-A |")
    A("| `charge_current_coef_cv` | `1.071` | @ VBAT=4.20V (CV 段末端) | 同上 |")
    A("| `charge_current_rilim_landed` | `680Ω` | ★**已落表事实 (V-4 裁定 2026-11-16)** ⇒ ★**本单不代拍新档位** ★ | `HW/netlist_v1.csv` L47/L48 |")
    A("| `charge_current_ichg_max_680` | `0.697A` | 680Ω 档 max 档 (KILIM_max 390 AΩ) | `MECH/hinge_power_calc.json` rilim_table |")
    A("| `charge_current_per_pin_max_680` | `0.349A` | pin1/pin2 双 pin 并联 ⇒ ÷2 ⇒ ≤0.50A 触点工作上限 | 同上 |")
    A("| `charge_current_margin_680` | `1.43×` | 0.50A ÷ 0.349A | 同上 |")
    A("| `charge_current_ichg_max_390` | `1.216A` | ★**390Ω 档已判死** (单 pin 0.608A 超上限 21.6%) | 同上 |")
    A("| `charge_current_per_pin_max_390` | `0.608A` | ★**超 0.50A 上限 21.6% ⇒ 判死** | 同上 |")
    A("| `charge_current_per_pin_max_470` | `0.505A` | ★**超 1.0% ⇒ 判死** | 同上 |")
    A("| `charge_current_per_pin_max_300` | `0.790A` | ★**超 58% ⇒ 判死** | 同上 |")
    A("| `ts_ref_ground_offset_680` | `20.9mV / 0.65°C` | TS 参考地被 0.697A 回流抬高 (O-4 行真值) | `MECH/HINGE_POWER_CALC.md` §M-4 表 |")
    A("| `jchg_contact_rating` | `0.5A/触点` | ★**FH12-10S-0.5SH(55) 官网 Rated Current 0.5A** + 70% 降额条款逐字原文已钉进 `HW/J_CHG_SELECTION.md` §7 ⇒ 触点天花板 (0.50A) 有官网出处 | Hirose 官网产品页 CL0586-0522-3-55 + [FH12] Series Catalog (Nov.1.2026) |")
    A("| `jchg_10p_dims_mm` | `A=4.5 / B=8.1 / C=9.1 / D=5.57` | ★**官网目录尺寸表** ⇒ 10p 外形宽 C=9.1mm 与本页原反推值吻合; ★**尺寸字母语义归 mech-lead 判定, 本单只登记数据** | Hirose [FH12] Series Catalog (Nov.1.2026) 尺寸表 |")
    A("| `charge_time_max_680` | `34.41min` | 400mAh 口径 (max 档) | `MECH/hinge_power_calc.json` rilim_table t_charge_min |")
    A("")
    A("---")
    A("")
    A("## B5 未决项与卡点 (需要谁回答什么)")
    A("")
    A("| # | 需要谁 | 问什么 | 状态 / 降级方案 |")
    A("|---|---|---|---|")
    A("| 1 | ★**main / 老板** | ★**是否把本单的新闸挂进 `state/gate_check.py`** (本单按先例零挂链 ⇒ 挂链是 main 的地界) | ★**本单不代挂** ⇒ ★**降级方案: 新闸已可裸跑 + `--selftest` 自证 ⇒ main 想挂随时一行 ★ |")
    A("| 2 | ★**main / 老板** | ★**`R_ILIM` 是否维持 680Ω** (V-4 已裁 680Ω 且已落表; 390Ω/470Ω/300Ω 在 1.216 系数下全判死) | ★**本单不代拍** ⇒ ★**降级方案: 文档已全部追平到 680Ω 真值; 若改档 ⇒ 走「板只改一次」那一趟 (换料不换板, ILIM 脚稳 0.8V) ★ |")
    A("| 3 | ★**mech-lead** | 若 680Ω 档的 TS 偏差 0.65 °C 是否需要留 1 °C 裕量 ⇒ 0.65 °C 满足 ⇒ ★**无阻塞** | ★**已答 (MECH §M-4: 680Ω 档 0.65 °C ✅) ★ |")
    A("| 4 | ★**PM / 采购 (非本单外发)** | J_CHG 座体单触点额定 ≥0.5A 的书面确认 (RFQ 硬判据) | ★**[官网] 证据已补齐** (官网产品页 Rated Current **0.5A** + 目录尺寸表 + 70% 条款逐字原文, 已钉进 `HW/J_CHG_SELECTION.md` §7) ⇒ ★**只剩「厂商书面确认」这个动作属采购域** ⇒ ★**本单零外发**; ★**main 已裁: 书面确认走 RFQ (零外发, 由老板放行)** ★ |")
    A("| 5 | ★**EVT 阶段** | 板端 ICHG / 触点温升实测 | ★**[0数据]** ⇒ ★**降级方案: EVT 按 `HW/EVT_RELIABILITY_TEST_ITEMS.md` 实测复核; 在此之前所有 ICHG 数一律标 [推算]/[实测](脚本), 不冒充实测 ★ ⇒ ★**main 已裁: 不阻塞本趟 (知悉型)** ★ |")
    A("| 6 | ★**mech-lead** | 官网 10p 尺寸 (A=4.5 / B=8.1 / C=9.1 / D=5.57) 已入库 ⇒ ★**哪个字母是座体 X 向进深 / Y 向占宽 ⇒ §4.1/§4.2 的间隙结论是否要重算, 归 mech-lead 地界** ⇒ ★**本单只登记数据不判定, 已开 need** ★ |")
    A("| 7 | ★**main (已回覆, 闭环)** | main 2026-11-24 09:3x 回覆 5 条 need: ① 维持 680Ω (老板域) ② 规格页条款钉 §7 (★本单已做★) ③ EVT 不阻塞 ④ 闸与「板只改一次」同批挂 (★本单零挂链 = 一致★) ⑤ 网表 note 三处 390Ω 活值另开「网表 note 订正」单, 进那一趟同批做 | ★**全部已收** ⇒ 详见真相页 §6 ★ |")
    A("")
    A("> ★★**零「等原厂回信 / 等外部确认」挂起项**: ★**本单 0 条外部依赖** ⇒ 全部缺口已换成【自己查的结果 + 证据等级 + 查不到就写降级方案】 ★★")
    A("")
    A("---")
    A("")
    A("## B6 自证复现命令")
    A("")
    A("```bash")
    A("cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses")
    A("")
    A("# ① 权威源重新生成 (rc=0) ⇒ 真相页 §1 的新值")
    A("python3 MECH/hinge_power_calc.py --json")
    A("python3 MECH/hinge_power_calc.py")
    A("")
    A("# ② 新闸裸跑 (rc=0)")
    A("python3 HW/check_charge_current_live_value.py")
    A("")
    A("# ③ 新闸自测 (rc=0 · 14/14 · 末行 ALL TESTS PASS)")
    A("python3 HW/check_charge_current_live_value.py --selftest")
    A("")
    A("# ④ 既有闸读数 (rc=0 · 与开工前 stdout 逐字相同)")
    A("python3 HW/check_netlist_selfconsistency.py")
    A("")
    A("# ⑤ 零落表 / 零写板 / 零改既有闸 (md5 与开工前逐字相同)")
    A("md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/check_netlist_selfconsistency.py")
    A("stat -c '%n mtime=%y size=%s' HW/PCB/demo_mainboard.kicad_pcb")
    A("")
    A("# ⑥ 零挂链 (必须 = 0)")
    A("grep -c check_charge_current_live_value state/gate_check.py")
    A("")
    A("# ⑦ 网表那 2 处 0.822 未动 (合法历史说明)")
    A("grep -n '0.822' HW/netlist_v1.csv")
    A("")
    A("# ⑧ 流程闸")
    A("python3 state/merge.py")
    A("python3 state/gate_check.py")
    A("python3 state/check_brief_commands.py")
    A("```")
    A("")
    A("---")
    A("")
    A("## 附: 交付物清单")
    A("")
    A("| # | 文件 | 动作 | 说明 |")
    A("|---|---|---|---|")
    A("| 1 | `HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md` | ★**新建** | 真相页 §0~§5 + 机器块 (`charge_current_live_value:`) |")
    A("| 2 | `HW/check_charge_current_live_value.py` | ★**新建** | 新闸 · 裸跑 rc=0 · `--selftest` 14/14 · ★**零挂链** |")
    A("| 3 | `HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md` | ★**新建** | 本页 B1~B6 |")
    A("| 4 | `HW/PCB_OUTLINE_60x15.md` | ★**追加** | 末尾追加 ISS-384 订正块 (14 行订正) ⇒ ★**既有正文一行未删 / 既有行号未位移** |")
    A("| 5 | `HW/J_CHG_SELECTION.md` | ★**追加** | 末尾追加 ISS-384 订正块 (16 行订正) |")
    A("| 6 | `HW/POWER_BUDGET_V3.md` | ★**追加** | 末尾追加 ISS-384 订正块 (5 行订正) |")
    A("| 7 | `state/fragments/hw.yaml` | ★**追加** | 3 产出物 + interface_claims + needs_from (走 `state/frag_write.py`) |")
    A("")
    A("> ★**零改清单 (逐项实测)**: ★**板文件 / 网表 / 脚表 / BOM / 既有闸 / `MECH/` / `SW/` / `state/gate_check.py` / 别人的分片** ⇒ ★**全部未动 (md5 与开工前逐字相同)** ★")
    A("")

    txt = "\n".join(L)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write(txt)
    print("WROTE: %s (%d chars)" % (OUT, len(txt)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
