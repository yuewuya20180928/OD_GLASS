#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-200 分片更新 (mech-lead 交卷) —— 走 state/frag_write.py 的原子写, 禁 open(p,"w")。

★**为什么不用 CLI**:
  `state/frag_write.py --add-claim` 是【**追加**】语义 (它只往列表尾部 append),
  本单要的是把 `interface_claims` 里**已经存在的那一条** `j_chg_pin_map` **按 key 定位后替换**
  —— 若用 CLI, 该 key 会变成**两条** ⇒ 合并器按 key 归并时要么判成口径冲突, 要么进
  【待规范化】清单 ⇒ 正是 ISS-107 踩过的坑。
  ⇒ 所以走 `update_fragment()` 直改结构, 但**原子写仍由 `frag_write.atomic_write_yaml` 负责**
  (tmp + fsync + os.replace), 与 CLI 同一条路径。★范式照 `MECH/_frag_update_iss092.py`。

★**边界 (本脚本只做三件事, 一件都不多做)**:
  ① `interface_claims` 里 `j_chg_pin_map` **这一条** → 按 key 定位后**替换** (不追加)
  ② `artifacts` → **新增** 2 条 (本脚本 + 本单交接单)
  ③ `needs_from` → **新增** 3 条 (只报不改的越界残留)
  ★**不改**: status / risks / answers / 其它任何 claim · `HW/` · `state/issue_log.yaml`
    · `state/p10_rows.json` · `state/gen_*.py` · 别人的分片。

用法: python3 MECH/_frag_update_iss200.py [--dry-run]
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

CLAIM_KEY = "j_chg_pin_map"

# ★**现行逐脚口径 (2026-11-12 独立复算, 不是照抄题单)**:
#   [实测] HW/netlist_v1.csv 逐脚 net 名复算 → pin1/2=BAT_CHG · pin3/4=GND ·
#   pin5=CHG_STAT · pin6=PWR_GOOD · pin7=NC · pin8=TS_BAT · pin9/10=HINGE_RSV
#   ⇒ 与 HW/CHARGE_BOARD_SPEC.md §5.2 (ISS-136 定版) 逐脚一致
NEW_CLAIM = {
    "key": "j_chg_pin_map",
    "value": "1x10p:1/2=BAT_CHG,3/4=GND,5=CHG_STAT,6=PWR_GOOD,7=NC,8=TS_BAT,9/10=HINGE_RSV",
    "note": (
        "★ISS-200 (2026-11-12) 按**网表真源**逐脚订正 (★[实测] `HW/netlist_v1.csv` 逐脚 net 名独立复算, "
        "与 `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 定版) 逐脚一致★)。"
        "pin1/2 = BAT_CHG (充电电流跨铰链, **双 pin 并联**, 390Ω 档 ICHG 0.82A ⇒ **单 pin 0.411A ≤ 0.5A 触点额定**, 余量 1.22×); "
        "pin3/4 = GND (回流双 pin, 与电源 pin 相邻 ⇒ 环路面积最小); "
        "pin5 = CHG_STAT (开漏, 主板侧 10k 上拉); pin6 = PWR_GOOD (开漏, 主板侧 10k 上拉); "
        "★**pin7 = NC** (2026-11-04 起 VBUS_DET 改**主板本地**分压 `R_VBUS_DET_D1`/`_D2` → `J_SOM_P1` pin100 "
        "⇒ 本脚不接; ★**过期的是『VBUS_DET 跨铰链走 J_CHG pin7/pin8』这句话, 不是 VBUS_DET 这个网** —— "
        "该网在网表里仍有 9 处, 仍是主板本地检测网); "
        "★**pin8 = TS_BAT** (电池 NTC 在镜脚 / BQ25896 TS 在镜框 ⇒ TS 必须跨铰链, 高阻无电流, 源阻抗 3-4 kΩ); "
        "★**pin9/10 = HINGE_RSV** (预留 DNP —— BQ25896 的 I2C 本板自闭环, 不跨铰链)。"
        "★**历史沿革 (旧口径已作废, 勿再当活口径用)**: 原值 "
        "『7=VBUS_DET / 8=TS / 9=RSV / 10=TS_RTN』是 V1.5-V1.8 期口径 —— ★**`TS_RTN` 这个网在网表里已 0 次出现** "
        "(2026-11-03 起跨铰链 TS 专用回流残留撤除, NTC 与 30.31k 分压下臂改回 PGND) "
        "⇒ **现行 10p map 里不存在跨铰链的 TS 专用回流**, 原 note 那句 "
        "『pin10 = TS 专用回流 (偏差 0.44-0.99°C → <0.01°C)』**随该口径一并作废** (那条偏差数字是按已不存在的跨铰链回流算的)。"
    ),
    "ref": "HW/netlist_v1.csv + HW/CHARGE_BOARD_SPEC.md#5.2",
}

ARTIFACTS = [
    {
        "path": "MECH/_frag_update_iss200.py",
        "kind": "script",
        "version": "1.0",
        "updated_at": "2026-11-12",
        "summary": ("ISS-200 分片原子写脚本 (走 state/frag_write.py 的 update_fragment): "
                    "★**按 key 定位后替换** interface_claims.j_chg_pin_map 这一条 (★不用 CLI --add-claim, "
                    "它是追加语义 ⇒ 会造成同 key 两条★), 另新增 2 条 artifact + 3 条 need; 禁 open(p,\"w\")。"),
    },
    {
        "path": "HANDOFF/2026-11-12_mech-lead_ISS200_J_CHG接口契约收敛.md",
        "kind": "handoff",
        "version": "1.0",
        "updated_at": "2026-11-12",
        "summary": ("ISS-200 交卷单: 结构侧 J_CHG 接口契约收敛到网表真源 —— "
                    "①state/fragments/mech.yaml 的 interface_claims.j_chg_pin_map 逐脚订正 (pin7 VBUS_DET→NC / "
                    "pin8 TS→TS_BAT / pin9-10 旧值(RSV / TS_RTN)→HINGE_RSV) ②MECH/USB_HINGE_STRUCTURE.md §5.2 "
                    "J_CHG 块整块改写 (5 条结论全部按现行 10p map 重推: 防呆 / 载流 / 电池脚 / 检测线 / pitch) "
                    "③逐脚复算依据 + 5 条越界残留只报不改 (MECH §5.1+§5.3 / HW 4 处) + 验收自证命令。"),
    },
]

# ★**3 条 need = 只报不改的越界残留** (★越界就是错★ ⇒ 一律登记给项目总工裁决)
NEEDS = [
    {
        "key": "iss200_mech_doc_residual_old_pinmap",
        "to": "main",
        "item": ("★ISS-200 只报不改 (①**MECH/USB_HINGE_STRUCTURE.md §5.1 表** J_CHG 行仍写 "
                 "『6 (1×6 @1.27) / 触点区宽 6.35 mm / 座体宽 8.35 mm』= 老 6 脚口径; "
                 "②**同文件 §5.3 C-4** 仍写『J_CHG → 8p @0.5』 (现行是 1×10p@0.5mm); "
                 "③**同文件 §5.3 C-1** 尾巴仍写『SYS 单触点载流下降 → 用 2 脚并联解决』(现行跨铰链载流是 BAT_CHG, SYS 不跨铰链); "
                 "④**同文件 F-5 / F-6** 的『SYS ↔ GND 反插短接』措辞仍是老 6 脚口径。"
                 "★**这 4 处都在本单地界外** (本单只许动 §5.2 的 J_CHG 块) ⇒ **只报不改**。"
                 "★**请裁**: 是否授权我在下一轮一并订正这 4 处 (文字口径, **不动任何几何数字**)。"),
        "waiting_on": "agent",
        "due": "2026-11-14",
        "since": "2026-11-12",
    },
    {
        "key": "iss200_hw_residual_old_pinmap",
        "to": "main",
        "item": ("★ISS-200 只报不改 (★**HW/ 是 ISS-199 的地界, 我不许代改**★), 结构侧扫出 4 处仍带旧 J_CHG 口径: "
                 "①`HW/netlist_v1.csv` **第 38 行 (J_CHG CONN 行) 与第 412 行 (P9 HINGE_CHG 行) 的 note 列** 仍写 "
                 "『pin7=VBUS_DET / pin8=TS / pin9-10=预留』『SYS 经 J_CHG 回主 PCB』 = V1.5 期旧文字 "
                 "(★**但同表逐脚 net 行是对的**, 机器判定以逐脚 net 名为准 ⇒ 建议 note 列订正, 别改逐脚行★); "
                 "②`HW/POWER_SHUTDOWN_V3.md` 第 129 行 『TS 专用回流 (J_CHG pin10 + R_TS_PULL/R_NTC_BAT 下端改接 TS_RTN)』 "
                 "—— **TS_RTN 网在网表里 0 次出现**; "
                 "③`HW/J_CHG_SELECTION.md` C-8 / §0-5 的防呆论证仍写『反插 = SYS/BAT_CHG 短接 GND → MOS 直通』 "
                 "—— ★**在现行 10p map 下该论证不成立**: 180° 翻转是 pin i ↔ pin 11-i ⇒ "
                 "BAT_CHG(pin1/pin2) 落到 HINGE_RSV(pin10/pin9) = 预留脚 ⇒ **断路, 不短接**; "
                 "真实反插后果是 **GND(pin3) ↔ TS_BAT(pin8) 短** + **CHG_STAT(pin5) ↔ PWR_GOOD(pin6) 短** "
                 "⇒ **机械防呆仍必需, 但理由要换**; "
                 "④`HW/CHARGE_BOARD_SPEC.md` §5.1 表 + §7 的 P10 镜像块 (ISS-136 已登记 needs_from, 不重复登记)。"
                 "★**转 ISS-199 / 项目总工裁决**。"),
        "waiting_on": "agent",
        "due": "2026-11-14",
        "since": "2026-11-12",
    },
    {
        "key": "iss200_mech_frag_mech_j_chg_pins_note",
        "to": "main",
        "item": ("★ISS-200 只报不改 (★**本单只许动 `interface_claims.j_chg_pin_map` 这一条**★): "
                 "**同域另一条 claim `mech_j_chg_pins`** 的 note 里仍断言现行口径为 "
                 "『pin1/2=BAT_CHG, pin3/4=GND, pin5=CHG_STAT, pin6=PWR_GOOD, pin7=NC, pin8=TS, pin9=RSV, "
                 "**pin10=TS 专用回流**』 ⇒ ★**pin10 这一句现在是错的** (现行 pin10 = HINGE_RSV), "
                 "且该 note 自己在末尾写着『原值与本域另一条 claim j_chg_pin_map 自相矛盾』。"
                 "★**订正 j_chg_pin_map 后, 分片内自相矛盾的那一条变成了 mech_j_chg_pins** ⇒ "
                 "合并器检不出这种**同域**不一致 (只有跨域同 key 才判冲突) ⇒ **必须人工收口**。"
                 "★**请裁**: 是否授权我一并订正 `mech_j_chg_pins` 的 note (只改那一句 pin map 文字, "
                 "**不动它的 value 10p@0.5mm**)。"),
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
                f"[ISS-200] {CLAIM_KEY} 命中 {len(hit)} 条 (期望恰好 1 条) —— "
                f"★不许新增, 只许替换既有那一条★; 请人工查 state/fragments/mech.yaml")
        i = hit[0]
        old = dict(claims[i])
        claims[i] = dict(NEW_CLAIM)
        print(f"  [claim] {CLAIM_KEY} 已按 key 替换 (位置 {i}, 共 {len(claims)} 条, ★key 不重复★)")
        print(f"          旧 value: {old.get('value')}")
        print(f"          新 value: {NEW_CLAIM['value']}")

        # ---------- ② artifacts: 按 path 去重; ★已存在的则刷新 summary (本单自己新增的那两条, 可反复重跑保持幂等★) ----------
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
        print(f"  [need] 新增 {addedn} 条 (共 {len(needs)})")

    if dry:
        from frag_write import load_fragment
        d = load_fragment("mech-lead")
        print("[dry-run] 将写入:")
        print(f"  claim {CLAIM_KEY} 替换 1 条 / artifacts +{len(ARTIFACTS)} / needs +{len(NEEDS)}")
        return 0

    d = update_fragment("mech-lead", mutate)
    print("✅ mech.yaml 已原子更新 "
          f"(artifacts={len(d.get('artifacts') or [])} claims={len(d.get('interface_claims') or [])} "
          f"needs={len(d.get('needs_from') or [])} risks={len(d.get('risks') or [])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
