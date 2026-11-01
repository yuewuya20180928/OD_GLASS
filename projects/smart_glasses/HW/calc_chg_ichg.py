#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calc_chg_ichg.py —— 充电电流换算自证脚本 (ISS-089 交叉评审 #3 / ISS-105 硬判据)

--------------------------------------------------------------------------------
为什么有这个脚本 (2026-11-01):
  `HW/CHARGE_BOARD_SPEC.md` §3.4 写的是
      ICHG ≈ IIN × (VBAT / VBUS) / η  = 0.822 × IIN      ← ★方向反了
  mech-lead 在 ISS-089 交叉评审里指出 (needs `iss089_ichg_ratio_datasheet`):
  buck 降压的功率守恒是 Pout = η·Pin, 所以
      ICHG = η · VBUS / VBAT · IIN = 0.9 × 5 / 3.7 = 1.216 × IIN   ← 正确
  0.822 与 1.216 互为倒数 (1/1.2162 = 0.8222)。

  影响: 铰链里流的是**电池充电电流 ICHG**, 不是输入电流 IIN。
  按旧式算, 单 pin (双 pin 并联) 峰值 = 0.411A < 0.5A 触点天花板 → 判过;
  按新式算, 单 pin 峰值 = 0.61A > 0.5A → **判不过** ⇒ 390Ω 档不成立。

--------------------------------------------------------------------------------
用法:
    python3 HW/calc_chg_ichg.py            # 打印全部档位 + 写 JSON
    python3 HW/calc_chg_ichg.py --json     # 只打印 JSON

数字唯一出处: 本文 + `HW/CHARGE_BOARD_SPEC.md` §2.4/§3.4。
边界: 只读不写任何文件 (除同目录 JSON); 不碰网表/网表生成器 (那是 state/gen_netlist.py 的事)。
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- 参数 (全部可追源)
VBUS = 5.0            # [V] Type-C 5V (PD 协商 5V only); CHARGE_BOARD_SPEC §2.4
VBAT = 3.7            # [V] 标称电芯电压; CHARGE_BOARD_SPEC §2.4
ETA = 0.90            # [比例] buck 转换效率; CHARGE_BOARD_SPEC §3.4 [推算]
KILIM = (320.0, 355.0, 390.0)   # [AΩ] BQ25896 IINLIM = KILIM / R_ILIM 的三档; §2.4
RILIM_CAND = (390.0, 510.0, 680.0, 1000.0, 1200.0)  # [Ω] 0402 ±1% 候选
PIN_COUNT = 2         # J_CHG pin1/pin2 双 pin 并联载流
TOUCH_RATING = 0.5    # [A] 0.5mm pitch ZIF 单触点额定 (硬判据 j_chg_contact_rating_min)
HINGE_DESIGN = 1.5    # [A] 铰链段 BAT_CHG 设计点 (双 pin 并联)
CELL_MAH = 420.0      # [mAh] 丰江432243 ≥420mAh; battery.cell claim
CELL_C_MAX = 1.0      # [C] 电芯允许充电倍率上限 (典型 1C) —— ★[0数据] 规格书未到
REG04_DEFAULT_ICHG = 2048.0  # [mA] BQ25896 REG04 复位默认 (官方)

# ---------------------------------------------------------------- 换算式
def ichg_correct(iin: float) -> float:
    """正确: buck 功率守恒 Pout = η·Pin ⇒ ICHG = η·(VBUS/VBAT)·IIN。"""
    return ETA * (VBUS / VBAT) * iin


def ichg_wrong(iin: float) -> float:
    """旧式 (方向反了): ICHG = (VBAT/VBUS)/η · IIN。"""
    return (VBAT / VBUS) / ETA * iin


def iin_max(r_ilim: float) -> tuple[float, float, float]:
    """IINMAX = KILIM / R_ILIM, 返回 (min, typ, max)。"""
    vals = [k / r_ilim for k in KILIM]
    return (min(vals), sum(vals) / len(vals), max(vals))


def main() -> int:
    ratio_ok = ETA * (VBUS / VBAT)
    ratio_wrong = (VBAT / VBUS) / ETA
    rows = []
    for r in RILIM_CAND:
        lo, ty, hi = iin_max(r)
        ichg_lo, ichg_hi = ichg_correct(lo), ichg_correct(hi)
        pin_hi = ichg_hi / PIN_COUNT
        c_rate = (ichg_hi / (CELL_MAH / 1000.0))
        rows.append({
            "r_ilim_ohm": r,
            "iinmax_a": {"min": round(lo, 4), "typ": round(ty, 4), "max": round(hi, 4)},
            "ichg_a_correct": {"min": round(ichg_lo, 4), "max": round(ichg_hi, 4)},
            "ichg_a_old_wrong_formula": {"min": round(ichg_wrong(lo), 4), "max": round(ichg_wrong(hi), 4)},
            "single_pin_a_correct": round(pin_hi, 4),
            "single_pin_a_old": round(ichg_wrong(hi) / PIN_COUNT, 4),
            "touch_rating_margin_x": round(TOUCH_RATING / pin_hi, 3),
            "hinge_margin_x": round(HINGE_DESIGN / ichg_hi, 3),
            "cell_charge_rate_c": round(c_rate, 3),
            "verdict_touch": "PASS" if pin_hi <= TOUCH_RATING else "FAIL",
            "verdict_cell_rate": "PASS" if c_rate <= CELL_C_MAX else "FAIL",
            "verdict_hinge": "PASS" if ichg_hi <= HINGE_DESIGN else "FAIL",
        })

    # 必装件逻辑: R_ILIM 不装 ⇒ REG04 复位默认 2048mA ⇒ 铰链过流
    no_rilim = {
        "ichg_a": REG04_DEFAULT_ICHG / 1000.0,
        "single_pin_a": REG04_DEFAULT_ICHG / 1000.0 / PIN_COUNT,
        "hinge_overrun_x": round((REG04_DEFAULT_ICHG / 1000.0) / HINGE_DESIGN, 3),
    }

    out = {
        "issue": "ISS-089(交叉评审#3)/ISS-105",
        "params": {
            "vbus_v": VBUS, "vbat_v": VBAT, "eta": ETA,
            "kilim_a_ohm": list(KILIM), "pin_count": PIN_COUNT,
            "touch_rating_a_per_contact": TOUCH_RATING,
            "hinge_design_a": HINGE_DESIGN,
            "cell_mah": CELL_MAH, "cell_charge_rate_max_c": CELL_C_MAX,
            "reg04_reset_default_ichg_ma": REG04_DEFAULT_ICHG,
        },
        "ratio": {
            "correct_buck_ratio": round(ratio_ok, 6),
            "old_wrong_ratio": round(ratio_wrong, 6),
            "reciprocal_check": round(ratio_ok * ratio_wrong, 9),
        },
        "r_ilim_sweep": rows,
        "rilim_not_fitted": no_rilim,
        "conclusion": {
            "old_value_in_hw_yaml": "chg_input_limit=1.00A/0.82A/0.411A (300Ω→390Ω 换算时用了反式)",
            "correct_value_at_390ohm": "IINMAX 0.82-1.00A / ICHG 1.00-1.22A / 单pin 0.50-0.61A",
            "verdict_390ohm": "FAIL (单pin 0.61A > 0.5A 触点天花板)",
            "recommended_r_ilim": "680Ω (触点余量 1.43×) 或 1.0kΩ (若电芯按 1C 限, 需电芯规格书确认)",
        },
    }

    print("=" * 78)
    print("充电电流换算自证 (ISS-089 交叉评审 #3 / ISS-105)")
    print("=" * 78)
    print(f"参数: VBUS={VBUS}V  VBAT={VBAT}V  eta={ETA}  KILIM={KILIM} AΩ")
    print(f"正确(buck): ICHG = eta*Vbus/Vbat*IIN = {ratio_ok:.6f} * IIN")
    print(f"旧式(反了): ICHG = (Vbat/Vbus)/eta*IIN = {ratio_wrong:.6f} * IIN"
          f"   [两者乘积={ratio_ok*ratio_wrong:.9f} ⇒ 互为倒数]")
    print()
    hdr = (f"{'R_ILIM':>8} {'IINMAX(min/typ/max)':>26} {'ICHG 正确':>16} "
           f"{'单pin 正确':>12} {'单pin 旧':>10} {'触点余量':>9} {'铰链余量':>9} {'倍率C':>7}  判定")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['r_ilim_ohm']:>7.0f}Ω "
              f"{r['iinmax_a']['min']:>7.3f}/{r['iinmax_a']['typ']:>6.3f}/{r['iinmax_a']['max']:>6.3f}A "
              f"{r['ichg_a_correct']['min']:>7.3f}-{r['ichg_a_correct']['max']:<7.3f}A "
              f"{r['single_pin_a_correct']:>10.3f}A "
              f"{r['single_pin_a_old']:>8.3f}A "
              f"{r['touch_rating_margin_x']:>8.2f}x "
              f"{r['hinge_margin_x']:>8.2f}x "
              f"{r['cell_charge_rate_c']:>6.2f}C  "
              f"触点:{r['verdict_touch']} 电芯倍率:{r['verdict_cell_rate']} 铰链:{r['verdict_hinge']}")
    print()
    print(f"★ R_ILIM 不装 (误装大阻值) ⇒ REG04 复位默认 ICHG={REG04_DEFAULT_ICHG}mA ⇒ "
          f"铰链过 {no_rilim['hinge_overrun_x']}x 设计点, 单pin {no_rilim['single_pin_a']}A "
          f"⇒ R_ILIM 是必装件 (换料不换板)")
    print()
    print("结论:")
    for k, v in out["conclusion"].items():
        print(f"  · {k}: {v}")

    js = os.path.join(HERE, "calc_chg_ichg.json")
    with open(js, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nJSON 已写: {js}")
    if "--json" in sys.argv:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
