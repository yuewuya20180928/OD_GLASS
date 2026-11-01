#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hw_week_20261101_check.py —— 本周 (2026-11-01) 硬件周更新关键数字一次复算

--------------------------------------------------------------------------------
本脚本是 2026-11-01 周更新窗口的"自证入口": 交接单 B6 里写的每个数字, 都能用
    python3 HW/hw_week_20261101_check.py
一条命令复算。只读, 不写任何文件 (除 --json 时的 stdout), 不碰 state/。

复算项 (7 组):
  §1 板宽 30mm 后 PCB 固定孔位重算 (ISS-118 台账订正 60x15 → 60x30)
  §2 充电电流换算 (ISS-089 交叉评审 #3 / ISS-105)  —— 调 HW/calc_chg_ichg.py
  §3 充电状态读取通路存在性 (ISS-043)            —— 扫 HW/netlist_v1.csv
  §4 EVT 实测项清单齐套性 (ISS-111)               —— 扫 HW/EVT_RELIABILITY_TEST_ITEMS.md
  §5 BOM 备料口径 (ISS-105 子项③)                 —— 扫 HW/BOM_v1.csv
  §6 分片 interface_claims 过期值/重复键          —— 读 state/fragments/hw.yaml (只读)
  §7 分片登记计数 (answers / claims / needs)      —— 同上
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
FRAG = os.path.join(PROJ, "state", "fragments", "hw.yaml")
NETLIST = os.path.join(HERE, "netlist_v1.csv")
BOM = os.path.join(HERE, "BOM_v1.csv")
EVT = os.path.join(HERE, "EVT_RELIABILITY_TEST_ITEMS.md")

RESULTS: list[tuple[str, str, str, str]] = []   # (组, 检查项, 结果, 数值/说明)


def chk(group: str, name: str, ok: bool, detail: str = "") -> bool:
    RESULTS.append((group, name, "PASS" if ok else "FAIL", detail))
    return ok


def close(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


# ---------------------------------------------------------------- §1 孔位重算
def sec1_holes() -> None:
    g = "§1 孔位(60x30)"
    L, W = 60.0, 30.0
    # 板宽 15 → 30 后: X 不变 (板长 60 不变), Y 向按中心线平移 (旧中心 7.50 → 新中心 15.00)
    old = {"P1": (8.00, 7.50), "P2": (52.00, 7.50), "S1": (8.00, 2.50), "S2": (52.00, 12.50)}
    new = {k: (x, y + (W / 2.0 - 7.50)) for k, (x, y) in old.items()}
    exp = {"P1": (8.00, 15.00), "P2": (52.00, 15.00), "S1": (8.00, 10.00), "S2": (52.00, 20.00)}
    chk(g, "孔位重算 = 期望值", all(close(new[k][0], exp[k][0]) and close(new[k][1], exp[k][1])
                                  for k in exp), json.dumps({k: new[k] for k in exp}, ensure_ascii=False))
    # 孔在板内 + 边距 >= 2.0mm
    edge_ok = all(2.0 <= x <= L - 2.0 and 2.0 <= y <= W - 2.0 for x, y in new.values())
    chk(g, "4 孔在板内且边距>=2.0mm", edge_ok, f"板 {L}x{W}")
    # 与 SoC 逃线带 X[20.20,31.80] 的 2D 重叠 = 0
    esc = (20.20, 31.80)
    overlap = sum(1 for x, _ in new.values() if esc[0] <= x <= esc[1])
    chk(g, "与 SoC 逃线带 X[20.20,31.80] 重叠孔数 = 0", overlap == 0, f"重叠 {overlap}")
    # 孔位窗口规则 X[4,12] + X[46,56]
    win = all((4 <= x <= 12) or (46 <= x <= 56) for x, _ in new.values())
    chk(g, "全部落在 X[4,12]+X[46,56] 窗口", win)
    # P1-P2 基准跨距不变 (X 12 → 52 = 40mm)
    d = (new["P2"][0] - new["P1"][0], new["P2"][1] - new["P1"][1])
    chk(g, "P1-P2 基准跨距 44.00mm 不变 (板长不变)", close(d[0], 44.0) and close(d[1], 0.0), f"{d}")
    # 板重 (60x30x1.0, 6层 1.6mm 铜等效) —— 与 HW/pcb60x30_check.json 对齐
    vol_mm3 = L * W * 1.0
    w_g = vol_mm3 * 1.85e-3   # FR4 1.85 g/cc
    chk(g, "板重 (60x30x1.0) = 3.33g ±0.01", close(w_g, 3.33, 0.01), f"{w_g:.3f} g")


# ---------------------------------------------------------------- §2 充电电流
def sec2_chg() -> None:
    g = "§2 充电电流"
    sys.path.insert(0, HERE)
    import calc_chg_ichg as C  # noqa: E402
    ratio_ok = C.ETA * (C.VBUS / C.VBAT)
    ratio_bad = (C.VBAT / C.VBUS) / C.ETA
    chk(g, "正确系数 = 1.216216 (η·Vbus/Vbat)", close(ratio_ok, 1.216216, 1e-6), f"{ratio_ok:.6f}")
    chk(g, "旧式系数 = 0.822222 (方向反了)", close(ratio_bad, 0.822222, 1e-6), f"{ratio_bad:.6f}")
    chk(g, "两者互为倒数 (乘积 = 1.0)", close(ratio_ok * ratio_bad, 1.0, 1e-9),
        f"{ratio_ok*ratio_bad:.9f}")
    hi = max(k / 390.0 for k in C.KILIM)
    ichg = C.ichg_correct(hi)
    pin = ichg / C.PIN_COUNT
    chk(g, "390Ω 档 IINMAX max = 1.000A", close(hi, 1.000, 1e-3), f"{hi:.3f} A")
    chk(g, "390Ω 档 ICHG max = 1.216A", close(ichg, 1.216, 1e-3), f"{ichg:.3f} A")
    chk(g, "390Ω 档单 pin = 0.608A", close(pin, 0.608, 1e-3), f"{pin:.3f} A")
    chk(g, "390Ω 档单 pin > 0.5A 触点天花板 ⇒ FAIL", pin > C.TOUCH_RATING, f"{pin:.3f} > 0.5")
    hi68 = max(k / 680.0 for k in C.KILIM)
    pin68 = C.ichg_correct(hi68) / C.PIN_COUNT
    chk(g, "680Ω 档单 pin = 0.349A (余量 1.43x)", close(pin68, 0.349, 1e-3),
        f"{pin68:.3f} A, 余量 {0.5/pin68:.2f}x")
    # R_ILIM 不装 => REG04 默认 2048mA => 铰链过 1.365x
    chk(g, "R_ILIM 不装 ⇒ 铰链过 1.365x 设计点",
        close((C.REG04_DEFAULT_ICHG / 1000.0) / C.HINGE_DESIGN, 1.365, 1e-3),
        f"{(C.REG04_DEFAULT_ICHG/1000.0)/C.HINGE_DESIGN:.3f}x")


# ---------------------------------------------------------------- §3 充电状态通路
def sec3_chg_stat() -> None:
    g = "§3 充电状态通路"
    rows = list(csv.DictReader(open(NETLIST, encoding="utf-8")))
    def find(pred):
        return [r for r in rows if pred(r)]
    stat_pu = find(lambda r: r.get("ref") == "R_PU_CHG_STAT")
    stat_net = find(lambda r: r.get("net") == "CHG_STAT")
    vbus_r = find(lambda r: r.get("ref", "").startswith("R_VBUS_DET"))
    vbus_c = find(lambda r: r.get("ref") == "C_DET_VBUS")
    jchg = find(lambda r: r.get("ref") == "J_CHG")
    chk(g, "CHG_STAT 网存在 (>=3 行)", len(stat_net) >= 3, f"{len(stat_net)} 行")
    chk(g, "R_PU_CHG_STAT = 10k 上拉存在", any("10k" in (r.get("value") or "") for r in stat_pu),
        (stat_pu[0].get("value") if stat_pu else "缺"))
    chk(g, "R_VBUS_DET_1/2 = 1M+1M 存在", len(vbus_r) == 2 and all("1M" in (r.get("value") or "")
                                                                  for r in vbus_r), f"{len(vbus_r)} 行")
    chk(g, "C_DET_VBUS = 100nF 存在", any("100nF" in (r.get("value") or "") for r in vbus_c),
        (vbus_c[0].get("value") if vbus_c else "缺"))
    pinmap = " ".join((r.get("note") or "") for r in jchg)
    chk(g, "J_CHG pin map 含 pin5=CHG_STAT / pin7=VBUS_DET",
        "pin5=CHG_STAT" in pinmap and "pin7=VBUS_DET" in pinmap, "")
    tp = find(lambda r: r.get("ref") in ("TP_CHG_STAT", "TP_VBUS"))
    chk(g, "测试点 TP_CHG_STAT / TP_VBUS 各存在", len(tp) == 2, f"{len(tp)} 个")
    # RC 复算
    rth = 1e6 / 2.0   # 1M || 1M
    tau = rth * 100e-9
    chk(g, "VBUS_DET 1M档 Rth=500k τ = 50ms / 95% ≈ 150ms", close(tau, 0.050, 1e-9),
        f"τ={tau*1e3:.1f}ms, 95%≈{3*tau*1e3:.0f}ms")
    rth2 = 100e3 * 47e3 / (100e3 + 47e3)
    chk(g, "若改 100k/47k: τ = 3.2ms", close(rth2 * 100e-9, 0.0032, 1e-5),
        f"τ={rth2*100e-9*1e3:.1f}ms")


# ---------------------------------------------------------------- §4 EVT 清单
def sec4_evt() -> None:
    g = "§4 EVT 清单"
    txt = open(EVT, encoding="utf-8").read()
    ids = re.findall(r"\*\*(R-[DVBHSC]-\d{2})\*\*", txt)
    uniq = sorted(set(ids))
    chk(g, "实测项编号唯一且 >= 36 条", len(uniq) >= 36, f"{len(uniq)} 条 (出现 {len(ids)} 次)")
    cats = {c: len([i for i in uniq if i.startswith(f"R-{c}-")]) for c in "DVBHSC"}
    chk(g, "6 类齐全 (跌落/振动/弯折/热/焊点/连接器)", all(v > 0 for v in cats.values()),
        json.dumps(cats, ensure_ascii=False))
    # 每行 5 字段非空 (测什么/怎么测/判据/回退/状态)
    lines = [ln for ln in txt.splitlines() if re.search(r"\|\s*\*\*R-[DVBHSC]-\d{2}\*\*\s*\|", ln)]
    bad = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 6:
            bad.append((ln[:40], "列数不足"))
            continue
        for idx in (1, 2, 3, 4, 5):
            if not cells[idx]:
                bad.append((cells[0][:28], f"第{idx+1}列为空"))
    chk(g, "每行 5 个字段 (测什么/怎么测/判据/回退/状态) 全非空", not bad, f"{len(bad)} 处空缺")
    chk(g, "三态判定含 ⚠️ 未验", "未验" in txt, "")
    chk(g, "X-ray 抽样按位置计 (1 块板 3 位置 + 1 切片)",
        "3 个位置" in txt and "1 处切片" in txt, "")


# ---------------------------------------------------------------- §5 BOM 备料
def sec5_bom() -> None:
    g = "§5 BOM 备料"
    rows = list(csv.DictReader(open(BOM, encoding="utf-8")))
    j = [r for r in rows if r.get("ref") == "J_CHG"]
    chk(g, "BOM 里有 J_CHG 行", len(j) == 1, f"{len(j)} 行")
    if j:
        memo = (j[0].get("memo") or "") + (j[0].get("procurement") or "")
        chk(g, "J_CHG 备料栏写明实物一对 / 2 只", ("实物一对" in memo) or ("2 只" in memo), "")
        chk(g, "J_CHG memo 含 R_ILIM 订正提示", "CHARGE_CURRENT_RECHECK" in memo, "")
    chk(g, "BOM qty 自检口径仍是 1 (逻辑器件)", all(r.get("qty") == "1" for r in rows),
        "生成器 state/gen_bom.py 强制 qty=1 ⇒ 备料口径只能写在 memo")


# ---------------------------------------------------------------- §6/§7 分片
def sec67_frag() -> None:
    g = "§6 分片 claims"
    d = yaml.safe_load(open(FRAG, encoding="utf-8"))
    claims = d.get("interface_claims") or []
    keys = [c.get("key") for c in claims]
    dups = sorted({k for k in keys if keys.count(k) > 1})
    chk(g, "interface_claims 无重复 key (旧值已清)", not dups, f"重复: {dups}")
    last = {}
    for c in claims:
        last[c.get("key")] = c.get("value")
    chk(g, "pcb_outline = 60x30mm (旧 60x15mm)",
        last.get("pcb_outline") == "60x30mm", str(last.get("pcb_outline")))
    chk(g, "battery_capacity_tier = 315mAh无桥/387mAh有桥",
        last.get("battery_capacity_tier") == "315mAh无桥/387mAh有桥",
        str(last.get("battery_capacity_tier")))
    chk(g, "chg_input_limit 已改成 390Ω 档 IINMAX 0.82-1.00A",
        last.get("chg_input_limit") == "0.82-1.00A", str(last.get("chg_input_limit")))
    chk(g, "chg_single_pin_a 已订正为 0.50-0.61A",
        last.get("chg_single_pin_a") == "0.50-0.61A", str(last.get("chg_single_pin_a")))
    chk(g, "chg_ichg_at_rilim = 1.00-1.22A",
        last.get("chg_ichg_at_rilim") == "1.00-1.22A", str(last.get("chg_ichg_at_rilim")))
    chk(g, "chg_rilim_recommended = 680Ω",
        last.get("chg_rilim_recommended") == "680Ω", str(last.get("chg_rilim_recommended")))
    chk(g, "pcb_width_recommend = 30mm (旧 15mm)",
        last.get("pcb_width_recommend") == "30mm", str(last.get("pcb_width_recommend")))
    chk(g, "pcb_mount_holes_xy 已按 30mm 板宽重算 Y",
        last.get("pcb_mount_holes_xy") == "P1(8,15)P2(52,15)S1(8,10)S2(52,20)",
        str(last.get("pcb_mount_holes_xy")))
    g = "§7 分片计数"
    ans = d.get("answers") or []
    chk(g, "answers >= 24 条 (窗口开始时 13)", len(ans) >= 24, f"{len(ans)} 条")
    ans_keys = [(a.get("key"), a.get("to")) for a in ans]
    chk(g, "answers 无重复 (key,to) 组合", len(ans_keys) == len(set(ans_keys)),
        f"重复: {sorted({k for k in ans_keys if ans_keys.count(k) > 1})}")
    chk(g, "interface_claims >= 100 条", len(claims) >= 100, f"{len(claims)} 条")
    needs = d.get("needs_from") or []
    nodue = [n.get("key") for n in needs if not n.get("due")]
    chk(g, "needs_from 全部带 due (无僵尸)", not nodue, f"缺 due: {nodue}")


def main() -> int:
    for fn in (sec1_holes, sec2_chg, sec3_chg_stat, sec4_evt, sec5_bom, sec67_frag):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            RESULTS.append((fn.__name__, "脚本异常", "FAIL", repr(e)))
    npass = sum(1 for r in RESULTS if r[2] == "PASS")
    nfail = len(RESULTS) - npass
    width = max(len(r[1]) for r in RESULTS) + 2
    print("=" * 100)
    print("hw-lead 周更新 (2026-11-01) 关键数字自证")
    print("=" * 100)
    cur = None
    for grp, name, res, detail in RESULTS:
        if grp != cur:
            cur = grp
            print(f"\n【{grp}】")
        print(f"  {res:4}  {name:<{width}} {detail}")
    print("\n" + "-" * 100)
    print(f"合计: {len(RESULTS)} 项 | PASS {npass} | FAIL {nfail}")
    if "--json" in sys.argv:
        print(json.dumps([{"group": g, "check": n, "result": r, "detail": d}
                          for g, n, r, d in RESULTS], ensure_ascii=False, indent=2))
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
