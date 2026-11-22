#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-202 分片更新 (mech-lead 交卷) —— 走 state/frag_write.py 的原子写, 禁 open(p,"w")。

★**为什么不用 CLI**:
  `state/frag_write.py --add-claim` 是【**追加**】语义 (它只往列表尾部 append),
  本单要的是把 `interface_claims` 里**已经存在的那一条** `mech_j_chg_pins` **按 key 定位后替换**
  —— 若用 CLI, 该 key 会变成**两条** ⇒ 合并器按 key 归并时静默覆盖 / 判成口径冲突
  ⇒ 正是 ISS-107 / ISS-200 踩过的坑。
  ⇒ 所以走 `update_fragment()` 直改结构, 但**原子写仍由 `frag_write.atomic_write_yaml` 负责**
  (tmp + fsync + os.replace), 与 CLI 同一条路径。★范式照 `MECH/_frag_update_iss200.py`。

★**边界 (本脚本只做三件事, 一件都不多做)**:
  ① `interface_claims` 里 `mech_j_chg_pins` **这一条** → 按 key 定位后**替换** (不追加)
     ★**value 不动** (`10p@0.5mm` —— 已与网表 CONN 行 "1×10p@0.5mm 排线座" 一致), 只订正 **note**
  ② `artifacts` → **新增** 2 条 (本脚本 + 本单交接单)
  ③ `needs_from` → **新增** 5 条 (只报不改的越界残留)
  ★**不改**: status / risks / answers / 其它任何 claim · **既有 needs_from 条目**
    (含 ISS-200 登记的 `iss200_mech_doc_residual_old_pinmap` / `iss200_mech_frag_mech_j_chg_pins_note`
     —— 那两条本单已做掉, 但**关闭需求是 main 的活**, 本单只报不改, 由 main 回写 answers)
    · `HW/` · `state/issue_log.yaml` · `state/p10_rows.json` · `state/gen_*.py` · 别人的分片。

用法: python3 MECH/_frag_update_iss202.py [--dry-run]
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

CLAIM_KEY = "mech_j_chg_pins"

# ★**现行逐脚口径 (2026-11-12 独立复算, 不是照抄题单)**:
#   [实测] HW/netlist_v1.csv 逐脚 net 名复算 → pin1/2=BAT_CHG · pin3/4=GND ·
#   pin5=CHG_STAT · pin6=PWR_GOOD · pin7=NC · pin8=TS_BAT · pin9/10=HINGE_RSV
#   ⇒ 与 HW/CHARGE_BOARD_SPEC.md §5.2 (ISS-136 定版) 逐脚一致
#   ⇒ 与同域另一条 claim `j_chg_pin_map` (ISS-200 已订正) **逐脚完全一致**
NEW_CLAIM = {
    "key": "mech_j_chg_pins",
    "value": "10p@0.5mm",          # ★不动: 已与网表 CONN 行 "1×10p@0.5mm 排线座" 一致
    "note": (
        "★**已按网表真源订正 (ISS-202 · 2026-11-12)** —— 本 note 现与同域另一条 claim `j_chg_pin_map` "
        "(ISS-200 已订正) **逐脚完全一致**, ★**分片内不一致已消除**。"
        "★**value 不动** (`10p@0.5mm` —— [实测] `HW/netlist_v1.csv` J_CHG CONN 行 = “1×10p@0.5mm 排线座”, "
        "选型件 Hirose FH12-10S-0.5SH(55) 亦为 1×10p@0.5) ⇒ 本条已从『建议 pin 数』升级为**定版**。"
        "★**现行 10p 逐脚 map** ([实测] 网表逐脚 net 名独立复算, 与 `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 定版) 逐脚一致): "
        "pin1/2=BAT_CHG (充电电流跨铰链, **双 pin 并联**) · pin3/4=GND (回流双 pin, 与电源 pin 相邻) · "
        "pin5=CHG_STAT (开漏, 主板侧 10k 上拉) · pin6=PWR_GOOD (开漏, 主板侧 10k 上拉) · "
        "★**pin7=NC** (2026-11-04 起 VBUS_DET 改**主板本地**分压 `R_VBUS_DET_D1`/`_D2` → `J_SOM_P1` pin100 ⇒ 本脚不接; "
        "★**过期的是『VBUS_DET 跨铰链走 J_CHG pin7/pin8』这句话, 不是 VBUS_DET 这个网** —— 该网在网表里仍有 9 处, 仍是主板本地检测网) · "
        "★**pin8=TS_BAT** (电池 NTC 在镜脚 / BQ25896 TS 在镜框 ⇒ TS 必须跨铰链, 高阻无电流, 源阻抗 3-4 kΩ) · "
        "★**pin9/10=HINGE_RSV** (预留 DNP —— BQ25896 的 I2C 本板自闭环, 不跨铰链)。"
        "★**原 note 的三处逐脚断言已作废**: ①『pin8=TS』⇒ 现为 **TS_BAT**; ②『pin9=RSV』⇒ 现为 **HINGE_RSV**; "
        "③★**『pin10=TS 专用回流』⇒ 现为 HINGE_RSV** —— ★**`TS_RTN` 这个网在网表里已 0 次出现** "
        "([实测] `grep -c TS_RTN HW/netlist_v1.csv` = 0; 2026-11-03 起跨铰链 TS 专用回流残留撤除, NTC 与 30.31k 分压下臂改回 PGND) "
        "⇒ **现行 10p map 里不存在跨铰链的 TS 专用回流**, 原 note 那句『pin10 = TS 专用回流』**随该口径一并作废**。"
        "★**原 note 开头『SYS×2 载流 + 检测×2 + 状态×2 + GND×2』是老 6 脚 map 的拆脚说法, 已作废** —— "
        "★**跨铰链载流是 BAT_CHG** (pin1/pin2 双 pin 并联; 现行 `R_ILIM=390Ω` ⇒ ICHG 0.82 A ⇒ 单 pin 0.411 A ≤ 0.5 A 触点额定, 余量 1.22×), "
        "★**SYS 根本不跨铰链** (网表 J_CHG 无 SYS 脚)。"
        "★**原 note 末尾『原值与本域另一条 claim j_chg_pin_map 自相矛盾』一句现已失效** (两条已对齐)。"
    ),
    "ref": "HW/netlist_v1.csv + MECH/USB_HINGE_STRUCTURE.md#5.2",
}

ARTIFACTS = [
    {
        "path": "MECH/_frag_update_iss202.py",
        "kind": "script",
        "version": "1.0",
        "updated_at": "2026-11-12",
        "summary": ("ISS-202 分片原子写脚本 (走 state/frag_write.py 的 update_fragment): "
                    "★**按 key 定位后替换** interface_claims.mech_j_chg_pins 这一条 (★不用 CLI --add-claim, "
                    "它是追加语义 ⇒ 会造成同 key 两条★; ★**value 不动**, 只订正 note), "
                    "另新增 2 条 artifact + 5 条 need; 禁 open(p,\"w\")。"),
    },
    {
        "path": "HANDOFF/2026-11-12_mech-lead_ISS202_J_CHG旧口径收尾.md",
        "kind": "handoff",
        "version": "1.0",
        "updated_at": "2026-11-12",
        "summary": ("ISS-202 交卷单: 结构侧 J_CHG 旧口径收尾 —— "
                    "①MECH/USB_HINGE_STRUCTURE.md §5.1 表 J_CHG 行 (6 (1×6 @1.27) / 6.35 / 8.35 → 10 (1×10 @0.5) / 3.5 / 5.5, 按 hinge_usb_check.py 复算) "
                    "②§5.3 C-4 (J_CHG → 8p @0.5 → 1×10p @0.5; 堆叠算式属几何数字 ⇒ 只报不改) "
                    "③§5.3 C-1 尾巴 (SYS 单触点载流 → BAT_CHG 双 pin 并联) "
                    "④§5.2 F-5 / F-6 (反插后果按 pin i ↔ pin 11-i 重算: 断路 + GND↔TS_BAT 短 + CHG_STAT↔PWR_GOOD 短) "
                    "⑤frag claim mech_j_chg_pins 的 note (pin10=TS 专用回流 → HINGE_RSV) "
                    "⑥逐脚复算依据 + 越界残留只报不改 (本文件 11 处 + 其它 MECH 文档 3 份 + 脚本 RECOMMENDED_PINS) + 验收自证命令。"),
    },
]

# ★**5 条 need = 只报不改的越界残留** (★越界就是错★ ⇒ 一律登记给项目总工裁决)
NEEDS = [
    {
        "key": "iss202_mech_doc_residual_jchg_old_6pin",
        "to": "main",
        "item": ("★ISS-202 只报不改 (★**本单地界只含 §5.1 表 J_CHG 行 / §5.3 C-4 / §5.3 C-1 / §5.2 F-5·F-6 四处**★): "
                 "`MECH/USB_HINGE_STRUCTURE.md` 里 J_CHG **仍带老 6 脚 / 8p 口径** 共 11 处 —— "
                 "①§0 C-3 『J_CHG 1×6@1.27→8p@0.5 后, 堆叠降到 24.0 mm』 ②§0 C-5 『J_CHG 的 pin 定义里没有电池脚』+『0.55 A (SYS 口径) vs 1.5 A』 "
                 "(⇒ 与 ISS-200 §5.2 第 4 条『有电池脚』直接矛盾) ③§0 C-6 『1×6 1.27mm 排线座无防呆, 反插 = SYS 短接到 GND』 "
                 "④§3.1 链路表 L-1 『J_CHG (1×6 1.27 mm 排线座) | 6 | 5 | 0』 ⑤§3.2b 声明版行 『40p + 40p + 4p + 1×6@1.27 | 49.62 mm』 "
                 "(★[实测] 现网表声明 = 31.5 mm, `python3 MECH/hinge_usb_check.py` §2) ⑥§3.2b 收敛版行 『16p + 20p + 4p + 8p@0.5 | 24.00 mm』 "
                 "⑦§3.2c 『声明版 49.62 mm / 收敛版 24.00 mm』 ⑧§7 『铰链区高度占位 49.62 → 24.00 mm (省 25.62 mm)』 ⑨§8 U-2 『(16p / 20p / 4p / 8p)』 "
                 "⑩§9 `mech_hinge_stack_fixed_mm` 注 『收敛版 (16p/20p/4p/8p @0.5)』 ⑪★**§9 `mech_j_chg_pins` 行仍写 value = `8p@0.5mm`** "
                 "(★**与本分片 claim `mech_j_chg_pins` 的 value `10p@0.5mm` 直接矛盾 ⇒ 结构侧文档里还藏着第 3 套 pin map**★)。"
                 "★**另**: §5.2 F-3 行『缩 pin (16p/20p/8p → 24.0 mm)』的 8p 同属旧口径, 但 §5.2 是 ISS-200 已定版区 ⇒ **我没碰**。"
                 "⇒ ★**请裁**: 是否授权下一轮一并订正这 12 处 (★**文字口径为主**; §3.2b/§7/§9 的 49.62 / 24.00 / 25.62 是几何数字, 是否连带重算请一并给口径)。"),
        "waiting_on": "agent",
        "due": "2026-11-14",
        "since": "2026-11-12",
    },
    {
        "key": "iss202_mech_c4_stack_arith_pending",
        "to": "main",
        "item": ("★ISS-202 边界内发现, 但**本单只报不改** (★属几何数字变更★): "
                 "`MECH/USB_HINGE_STRUCTURE.md` §5.3 **C-4** 行, 本单已把 `J_CHG` 的 pin 规格从 **8p @0.5** 订正为 **1×10p @0.5** (ISS-202 · 2026-11-12), "
                 "但**同一行的触点区/堆叠算式仍是 8p 口径** (『8+20+4+8 = 40 脚 @0.5 = 20 mm 触点区』+『铰链区堆叠 24.0 mm (含间隙), 余 13.0 mm』) ⇒ "
                 "★**该行现在自相矛盾** (已就地打 ★ 标注『本格算式仍按原 8p 口径 ⇒ 与上格 1×10p 不一致; 属几何数字变更 ⇒ 本单只报不改』)。"
                 "★**两种算式的候选重算值 (供裁, 本单未写入文档)**: "
                 "按本文行内算式 8+20+4+10 = 42 脚 @0.5 = **21.0 mm 触点区** + 4×1.0 mm 间隙 = **25.0 mm 堆叠 / 余 12.0 mm**; "
                 "按脚本算式 16+20+4+10 = 50 脚 @0.5 = **25.0 mm 堆叠** ⇒ **两种算式都落在 25.0 mm 堆叠** (但『触点区』那一格两法不同: 21.0 vs 25.0)。"
                 "★**另**: 该表 `MECH/hinge_usb_check.py` 的 `RECOMMENDED_PINS['J_CHG']=8` (及其注释『SYS×2(载流) + VBUS_DET + BAT_DET + …』= 老 6 脚期 map) 同源 ⇒ 见下一条 need。"
                 "⇒ ★**请裁**: C-4 行按哪套算式重算, 以及是否授权改脚本 `RECOMMENDED_PINS` (脚本属既有件, 改它要单独授权)。"),
        "waiting_on": "agent",
        "due": "2026-11-14",
        "since": "2026-11-12",
    },
    {
        "key": "iss202_mech_script_recommended_pins_jchg_8",
        "to": "main",
        "item": ("★ISS-202 只报不改 (★**`MECH/hinge_usb_check.py` 是既有脚本, 本单地界不含改它**★): "
                 "该脚本第 77 行 `RECOMMENDED_PINS = {… \"J_CHG\": 8,   # SYS×2(载流) + VBUS_DET + BAT_DET + CHG_STAT + PWR_GOOD + GND×2 …}` "
                 "⇒ ★**\"J_CHG 收敛成 8p\" 仍是脚本里的活口径**, 且**注释还在用老 6 脚期的拆脚说法 (SYS 载流 / VBUS_DET / BAT_DET 跨铰链)** —— "
                 "★**后果**: 脚本算出的『收敛版垂直占位 24.0 mm (16p/20p/4p/8p 全 0.5mm)』建立在 8p 上, "
                 "而 `MECH/USB_HINGE_STRUCTURE.md` §5.3 C-4 / §3.2b / §9 三处都引用这个 24.0 ⇒ ★**口径链的根在脚本**。"
                 "★[实测] 脚本里 `j_chg_pitch_mm` 已是 0.5 (对), `decl` 解析出的 J_CHG 声明也是 10 (对) ⇒ **只有 `RECOMMENDED_PINS` 与它的注释是旧口径**。"
                 "⇒ ★**请裁**: 是否授权把 `RECOMMENDED_PINS['J_CHG']` 改成 10 并重算 24.0 mm 那条链 (连带 §3.2b / §7 / §9 的 24.00 / 25.62 引用)。"),
        "waiting_on": "agent",
        "due": "2026-11-14",
        "since": "2026-11-12",
    },
    {
        "key": "iss202_mech_other_docs_jchg_old_pinmap",
        "to": "main",
        "item": ("★ISS-202 只报不改 (★**本单地界只有 `MECH/USB_HINGE_STRUCTURE.md` 那 4 处 + 本分片 claim 一条**★), "
                 "结构侧**其它文档**仍带 J_CHG 旧口径 (登记给项目总工裁, 建议下一轮一并收): "
                 "①`MECH/FPC_FAB_NOTES.md` **N-6** 『J_CHG 的 pin10 必须走成 TS 专用回流, 与 pin8 (TS 信号) 成对相邻』+ I-5 『反插 = BAT_CHG 短接 GND』 "
                 "(⇒ 现 pin10 = HINGE_RSV, 且现行反插是**断路**不是短接) ②`MECH/RELIABILITY_TEST_PLAN.md` **R10**『J_CHG 用 0.5mm pitch, SYS 双脚并联』+ "
                 "**§T-14 失效模式**『J_CHG 反插导致 SYS 短接 GND』+ **T-14 判据**『SYS 与 GND 在反插位型下不得导通』+ **K-11**『J_CHG 8p @0.5mm』+ **K-12**『J_CHG 脚数 8p 还是 10p』 "
                 "(★**T-14 的判据本身要改**: 现行 10p 下反插是 pin3(GND)↔pin8(TS_BAT) 短 + pin5(CHG_STAT)↔pin6(PWR_GOOD) 短, BAT_CHG 落预留脚 = 断路) "
                 "③`MECH/STRUCT_REVIEW_ISS065.md` **R3**『V 方向只有 VBUS_DET 分压信号过铰链』+『占用 J_CHG pin9/pin10 中的一个 ⇒ 与 ISS-091 的 pin9/10 用途申请撞车』 "
                 "(★**两条都过期**: VBUS_DET 2026-11-04 起主板本地分压不跨铰链; pin9/10 现为 HINGE_RSV, TS 专用回流提案已被网表撤除)。"
                 "⇒ ★**请裁**: 是否授权下一轮一并订正这三份 (★**不改任何几何数字, 只改 pin map / 跨铰链归属 / 防呆措辞**★)。"),
        "waiting_on": "agent",
        "due": "2026-11-14",
        "since": "2026-11-12",
    },
    {
        "key": "iss202_mech_frag_old_needs_stale",
        "to": "main",
        "item": ("★ISS-202 只报不改 (★**本单只许新增 need, 不许改既有 need 条目**★; ★**关闭需求是 main 的活**★): "
                 "**本分片里 2 条老 need 的口径已过期**, 请 main 裁 (回写 answers 关掉, 或改口径): "
                 "①`iss091_pin9_10_ntc_return` (2026-10-28) 还在问『**裁决: J_CHG 的 pin9/pin10 (预留) 是否改一个作 NTC 专用回流**』, "
                 "并把『改成 NTC 专用回流后偏差 <0.01C』当活结论 ⇒ ★**该提案已被网表撤除** ([实测] `TS_RTN` 在网表里 0 次出现, 2026-11-03 起残留撤除, "
                 "NTC 与 30.31k 分压下臂改回 PGND) ⇒ **现行 pin9/10 = HINGE_RSV, 没有 TS 专用回流** ⇒ 这条 need 的前提已不存在。"
                 "②`iss100_jchg_pitch_fix` (2026-10-28) 还在说『`MECH/hinge_usb_check.py` 的 j_chg_pitch_mm 仍是 1.27 (旧口径)』+『座体 6.50mm, 12mm 板就装得下』 "
                 "⇒ ★[实测] 该脚本 `j_chg_pitch_mm` **早已是 0.5** ⇒ 这条 need 也已过期 (且它引的『12mm 板宽』基线已被 ISS-192 迁到 30mm)。"
                 "★**另**: ISS-200 登记的 `iss200_mech_doc_residual_old_pinmap` 与 `iss200_mech_frag_mech_j_chg_pins_note` 两条 **本单已做掉** "
                 "(⇒ 本单只报不改, 请 main 回写 answers 闭合)。"
                 "⇒ ★**请裁**: 是否由 main 直接给这 4 条 need 回写 answers 闭合。"),
        "waiting_on": "agent",
        "due": "2026-11-14",
        "since": "2026-11-12",
    },
]


def main() -> int:
    dry = "--dry-run" in sys.argv

    def mutate(d: dict):
        # ---------- ① 按 key 定位后**替换** interface_claims 里的那一条 (★不是追加★) ----------
        claims = d.setdefault("interface_claims", [])
        hit = [i for i, c in enumerate(claims)
               if isinstance(c, dict) and c.get("key") == CLAIM_KEY]
        if len(hit) != 1:
            raise SystemExit(
                f"[ISS-202] {CLAIM_KEY} 命中 {len(hit)} 条 (期望恰好 1 条) —— "
                f"★不许新增, 只许替换既有那一条★; 请人工查 state/fragments/mech.yaml")
        i = hit[0]
        old = dict(claims[i])
        claims[i] = dict(NEW_CLAIM)
        print(f"  [claim] {CLAIM_KEY} 已按 key 替换 (位置 {i}, 共 {len(claims)} 条, ★key 不重复★)")
        print(f"          旧 value: {old.get('value')}  (★本单不改 value★)")
        print(f"          新 value: {NEW_CLAIM['value']}")
        print(f"          旧 note 尾: …{str(old.get('note'))[-60:]}")
        print(f"          新 note 尾: …{str(NEW_CLAIM['note'])[-60:]}")

        # ---------- ② artifacts: 按 path 去重; ★已存在的则刷新 summary (幂等★) ----------
        arts = d.setdefault("artifacts", [])
        bypath = {a.get("path"): a for a in arts if isinstance(a, dict)}
        added = 0
        for a in ARTIFACTS:
            cur = bypath.get(a["path"])
            if cur is None:
                arts.append(dict(a))
                bypath[a["path"]] = arts[-1]
                added += 1
            else:
                for k in ("kind", "version", "updated_at", "summary"):
                    if k in a and cur.get(k) != a[k]:
                        cur[k] = a[k]
        print(f"  [artifact] 新增 {added} 条 / 刷新已存在条目 (共 {len(arts)})")

        # ---------- ③ 新增 needs (按 key 去重) ----------
        needs = d.setdefault("needs_from", [])
        nkeys = {n.get("key") for n in needs if isinstance(n, dict)}
        addedn = 0
        for n in NEEDS:
            if n["key"] not in nkeys:
                needs.append(dict(n))
                addedn += 1
        print(f"  [need] 新增 {addedn} 条 (共 {len(needs)}; ★既有 need 一条未动★)")

    if dry:
        from frag_write import load_fragment
        d = load_fragment("mech-lead")
        print("[dry-run] 将写入:")
        print(f"  claim {CLAIM_KEY} 替换 1 条 (value 不动) / artifacts +{len(ARTIFACTS)} / needs +{len(NEEDS)}")
        return 0

    d = update_fragment("mech-lead", mutate)
    print("✅ mech.yaml 已原子更新 "
          f"(artifacts={len(d.get('artifacts') or [])} claims={len(d.get('interface_claims') or [])} "
          f"needs={len(d.get('needs_from') or [])} risks={len(d.get('risks') or [])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
