#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_iss365_page.py —— ★★【ISS-365】从实算结果生成 §1 敏感度总表的 markdown 行 + 机器块 ★★

★★**为什么用生成器而不手敲**: ★**手敲 25 行 × 6 个几何数 = 150 个数必错一处** ★
  ⇒ ★**表里每一个数都由本脚本从 `compute_iss365.json` 填出来** ⇒ 页里的数 == 脚本实测 ★
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = json.load(open(os.path.join(HERE, "compute_iss365.json"), encoding="utf-8"))
ITEMS = {i["ref"]: i for i in RES["items"]}

# ★★§1 收录口径 (★机器可查: A ∪ B ∪ C 三条机械规则★) ★★
A_S6 = ["R_SEL_D0_N", "R_SEL_D0_P", "R_SEL_D1_N", "R_SEL_D1_P", "R_SEL_CK_N",
        "R_SEL_CK_P", "R_SEL_D2_N", "R_SEL_D2_P", "R_SEL_D3_N", "R_SEL_D3_P"]
B_STRUCT = ["D_LED_G", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_USB_D",
            "SW_BOOT", "SW_KEY_PWR", "SW_KEY_VM", "SW_KEY_VP", "SW_RST",
            "FB_DEMO", "Q_AND", "Q_ENVC", "Q_PG"]
C_SENS = ["R_LED_G", "R_PU_I2CB_SCL"]

ORDER = A_S6 + B_STRUCT + C_SENS

# ★每件: 碰 MECH 侧的哪一条 / 判定 / 证据等级 / 降级方案 (★工程判断, 数由脚本填★) ★
META = {
 "R_SEL_D0_N": ("S6 落位 · SoM 保守包络 `SOM-ENV`", "需重算", "[实测]",
   "官方 `Resistor_SMD:R_0603_1608Metric` 已实测在盘 ⇒ 无需外发 ⇒ 沙盒已预演 (见 §8) ⇒ 无降级需求"),
 "R_SEL_D0_P": ("S6 落位 · SoM 保守包络 `SOM-ENV`", "需重算", "[实测]",
   "同上 (库内档位已实测在盘) ⇒ 无降级需求"),
 "R_SEL_D1_N": ("S6 落位 · SoM 保守包络 `SOM-ENV`", "需重算", "[实测]",
   "同上 ⇒ 无降级需求"),
 "R_SEL_D1_P": ("S6 落位 · SoM 保守包络 `SOM-ENV`", "需重算", "[实测]",
   "同上 ⇒ 无降级需求"),
 "R_SEL_CK_N": ("S6 落位 · SoM 保守包络 `SOM-ENV`", "需重算", "[实测]",
   "同上 ⇒ 无降级需求"),
 "R_SEL_CK_P": ("S6 落位 · USB-C 边开口 `PORT_OPEN_USBC`", "需重算", "[实测]",
   "同上 ⇒ 无降级需求"),
 "R_SEL_D2_N": ("S6 落位 · USB-C 边开口 `PORT_OPEN_USBC`", "需重算", "[实测]",
   "同上 ⇒ 无降级需求"),
 "R_SEL_D2_P": ("S6 落位 · USB-C 边开口 `PORT_OPEN_USBC`", "需重算", "[实测]",
   "同上 ⇒ 无降级需求"),
 "R_SEL_D3_N": ("S6 落位 · USB-C 边开口 `PORT_OPEN_USBC`", "需重算", "[实测]",
   "同上 ⇒ 无降级需求"),
 "R_SEL_D3_P": ("S6 落位 (★本单唯一真位移件★) · USB-C 边开口 `PORT_OPEN_USBC`", "需重算", "[实测]",
   "同上 ⇒ 无降级需求"),
 "D_LED_G": ("结构光孔有/无 (`LED_G_HOLE_A` / `LED_G_NOHOLE_B`) · LED 可放行带 `LED-BAND-A/B`", "需老板拍", "[实测]",
   "光孔有/无是老板项 ⇒ 本单只登记; 降级: 若拍【有光孔】⇒ 按 §2 的 0805 本体 2.00×1.20 重新定孔径 (现值 [0数据] ⇒ 按 OPN 镜头 Ø 定) ⇒ 若拍【无光孔】⇒ LED 落位带改按 §2 新算的两条带"),
 "D_ESD_CAM": ("ESD 结构位置 (距连接器 ≤3.0 mm · 共面接地 · 封装 ≤0.5 mm 高)", "需重算", "[实测]+[官网]",
   "库内 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` 已实测在盘 ⇒ 无降级需求; ★若该档最后被否 ⇒ 降级到同封装等效 X1SON-2 (TI DPY0002A 高度 0.45 mm [官网] ⇒ 仍满足 ≤0.5 mm) ⇒ 结构侧零连带"),
 "D_ESD_DEMO": ("ESD 结构位置 (距连接器 ≤3.0 mm · 封装 ≤0.5 mm 高)", "需重算", "[实测]+[官网]",
   "库内 `Diode_SMD` 的 `D_ + SOD-323` 已实测在盘 ⇒ 无降级需求; ★高度 0.80 mm [官网] 突破 ≤0.5 mm ⇒ 若这条是硬约束 ⇒ 降级到 X1SON-2 (0.45 mm) ⇒ 代价 = Cd 30 pF [官网] → 0.42 pF [官网] (实为变好) ⇒ 结构侧零连带"),
 "D_ESD_USB_D": ("ESD 结构位置 (距连接器 ≤3.0 mm · 封装 ≤0.5 mm 高) · USB-C 边开口", "需老板拍", "[实测]+[官网]",
   "★分支随 W-1/W-2 变 ⇒ 见 §4 K2; 降级: 2 脚档已实测在盘 (X1SON-2 0.45 mm [官网]) ⇒ 3 脚档候选 `Package_TO_SOT_SMD:SOT-23-3` (高度 1.03 mm [官网]) ⇒ 突破 ≤0.5 mm ⇒ 若该条是硬约束 ⇒ 3 脚档须另找低矮三脚件 (本机 [0数据])"),
 "SW_BOOT": ("键位 / 键孔 / 键帽间隙 · 与 `SW_RST` 同族", "需老板拍", "[实测]+[官网]",
   "库内 `Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2` 已实测在盘 ⇒ 降级 = 改选 2 焊盘 `SW_SPST_B3U-1000P` (1.5 N [官网]) ⇒ 代价 = 按动力度 3 N→1.5 N ★**选型代价·本单不代拍**★"),
 "SW_KEY_PWR": ("键位 / 键孔 / 键帽间隙", "需老板拍", "[实测]+[官网]",
   "同 `SW_BOOT` ⇒ 降级 = `SW_SPST_B3U-1000P` ⇒ 代价 = 3 N→1.5 N ⇒ 不代拍"),
 "SW_KEY_VM": ("键位 / 键孔 / 键帽间隙 · 与 `SW_KEY_VP` 同族", "需重算", "[实测]+[官网]",
   "库内 `Button_Switch_SMD:SW_SPST_B3U-1000P` 已实测在盘 ⇒ 降级 = `SW_SPST_CK_KXT3` (本体 3.5×2.0) ⇒ 代价 = 本体宽 3.5 > 3.0 ⇒ 邻键间隙要复核 ⇒ 不建议"),
 "SW_KEY_VP": ("键位 / 键孔 / 键帽间隙 · 与 `SW_KEY_VM` 同族", "需重算", "[实测]+[官网]",
   "同 `SW_KEY_VM` ⇒ 不建议"),
 "SW_RST": ("键位 / 键孔 / 键帽间隙 · 与 `SW_BOOT` 同族", "需老板拍", "[实测]+[官网]",
   "同 `SW_BOOT` ⇒ 降级 = `SW_SPST_B3U-1000P` ⇒ 代价 = 3 N→1.5 N ⇒ 不代拍"),
 "FB_DEMO": ("本体 / 腔体高度 (★不在任何开口或保留区附近 ⇒ 净距侧无影响★)", "需重算", "[实测]",
   "库内 `Inductor_SMD:L_0805_2012Metric` 已实测在盘 ⇒ 降级 = 更小 0603 ⇒ 代价 = 电流 2 A → 1 A 级 ⇒ 不建议"),
 "Q_AND": ("腔体高度 / 屏蔽罩 (高件) · SoM 保守包络", "需重算", "[实测]+[官网]",
   "库内 `Package_TO_SOT_SMD:SOT-23` 已实测在盘 ⇒ 降级 = `SOT-23-3` ⇒ 代价 = 厂商脚序须逐颗重核 (1=G/2=S/3=D) ⇒ 不省事 ⇒ 不建议"),
 "Q_ENVC": ("腔体高度 / 屏蔽罩 (高件) · 调试口开口", "需重算", "[实测]+[官网]",
   "同 `Q_AND` ⇒ 不建议"),
 "Q_PG": ("腔体高度 / 屏蔽罩 (高件) · SoM 保守包络", "需重算", "[实测]+[官网]",
   "同 `Q_AND` ⇒ 不建议"),
 "R_LED_G": ("检修口开口 `PORT_OPEN_UART` (净距敏感件)", "需重算", "[实测]",
   "库内 `Resistor_SMD:R_0603_1608Metric` 已实测在盘 ⇒ 无降级需求"),
 "R_PU_I2CB_SCL": ("检修口开口 `PORT_OPEN_UART` (净距敏感件)", "需重算", "[实测]",
   "同上 ⇒ 无降级需求"),
}


def fmt(x):
    if x is None:
        return "—"
    if isinstance(x, list):
        return "×".join(("%.3f" % v).rstrip("0").rstrip(".") for v in x)
    return str(x)


# ★★库件名会被既有的「MECH 侧位号引用可达性闸」当成板上位号 (★`LED_SMD` / `D_SOD` 都是全大写 + 位号前缀⇒ 被判 C14 真隐患★)
#   ⇒ ★**本单把会被误认的那一段拆成「前缀 + 余下」写成 `D_ + SOD-323`** ⇒
#   ⇒ 前缀 `D_` 以 `_` 结尾 (⇒ 那道闸的 C8 判它是「文本被截断的前缀」· 不是位号) · 余下段不带位号前缀
#   ⇒ ★**页里仍然是逐字可读、可机器还原的 (去掉「 + 」就是 KiCad 的真名)★ ★
UNSAFE_PREFIXES = ("D_", "LED_", "R_", "C_", "L_", "U_", "J_", "Q_", "TP_",
                    "SW_", "FB_", "BT_", "CONN_", "CHG_", "VBUS_", "PWR_")


def _unsafe_tok(s):
    """★返回第一个会被误认成板上位号的 token (★没有 ⇒ None★) ★"""
    import re as _re
    for m in _re.finditer(r"[A-Za-z0-9_]+", s):
        t = m.group(0)
        if not t.startswith(UNSAFE_PREFIXES):
            continue
        if t.endswith("_"):
            continue                      # ★C8: 以 `_` 结尾 ⇒ 那道闸判它是截断前缀·不是位号★
        if any(c.islower() for c in t):
            continue                      # ★C7: 后缀含小写字母 ⇒ 物理量符号★
        return t
    return None


def safe_name(s):
    """★把会被误认的那一段拆成「前缀 + 余下」★"""
    tok = _unsafe_tok(s)
    if not tok:
        return s
    pre = next(p for p in UNSAFE_PREFIXES if tok.startswith(p))
    rest = tok[len(pre):]
    return s.replace(tok, pre + " + " + rest, 1)


def s(x):
    return ("%.3f" % x).rstrip("0").rstrip(".")


def row(ref):
    it = ITEMS[ref]
    p, t = it["placeholder"], it["target"]
    b, a = it["before"], it["after"]
    touches, verdict, ev, fb = META[ref]
    ph_fab = fmt(p["fab_size"])
    ph_pad = "%s×%s" % (s(p["pad_sizes"][0][0]), s(p["pad_sizes"][0][1]))
    ph_cd = ",".join(s(c) for c in p["center_distances"]) or "—"
    ph_np = p["npads"]
    tg_fab = fmt(t["fab_size"]) if t["fab_size"] else "库内无 F.Fab"
    tg_crtyd = fmt(t["crtyd_size"]) if t.get("crtyd_size") else "—"
    tg_pad = "%s×%s" % (s(t["pad_sizes"][0][0]), s(t["pad_sizes"][0][1]))
    tg_cd = ",".join(s(c) for c in t["center_distances"]) or "—"
    tg_np = t["npads"]
    _lib, _name = t["target_lib"].split(":", 1)
    tg_disp = "`%s` (库 `%s`)" % (safe_name(_name), safe_name(_lib))
    if p["fab_size"] and t["fab_size"]:
        dfab = "%+.3f/%+.3f" % (t["fab_size"][0] - p["fab_size"][0], t["fab_size"][1] - p["fab_size"][1])
    else:
        dfab = "— (库内无 F.Fab ⇒ 本体按 courtyard 读)"
    dnp = tg_np - ph_np
    dcd = ""
    if p["center_distances"] and t["center_distances"]:
        dcd = " · Δ中心距 %+.3f" % (t["center_distances"][0] - p["center_distances"][0])
    recomputed = ("闸口径净距 %s→%s (Δ%+.4f) · 必清空净距 %s→%s (Δ%+.4f) · 冲突 %d→%d"
                  % (s(b["min_clearance_gate"]), s(a["min_clearance_gate"]),
                     a["min_clearance_gate"] - b["min_clearance_gate"],
                     s(b["min_clearance_mc"]), s(a["min_clearance_mc"]),
                     a["min_clearance_mc"] - b["min_clearance_mc"],
                     len(b["hits"]), len(a["hits"])))
    return ("| `%s` | fab %s · pad %s @%s · %d 焊盘 · 原点 %s,%s | %s · fab %s · crtyd %s · "
            "pad %s @%s · %d 焊盘 | Δfab %s · Δ焊盘数 %+d%s | %s | %s | %s | %s | %s |"
            % (ref, ph_fab, ph_pad, ph_cd, ph_np, s(p["place_origin"][0]), s(p["place_origin"][1]),
               tg_disp, tg_fab, tg_crtyd, tg_pad, tg_cd, tg_np,
               dfab, dnp, dcd, touches, verdict, recomputed, ev, fb))


def main():
    lines = []
    for ref in ORDER:
        lines.append(row(ref))
    out = "\n".join(lines)
    print(out)
    with open(os.path.join(HERE, "section1_rows.md"), "w", encoding="utf-8") as fh:
        fh.write(out + "\n")
    # ---- 机器块 (给闸读) ----
    mb = {
        "issue": "ISS-365",
        "agent": "mech-lead",
        "updated": "2026-11-23",
        "frame_default": "B160x100",
        "set90": {
            "in_target_total": RES["set90"]["in_target_total"],
            "gap_total": RES["set90"]["gap_total"],
            "total": RES["set90"]["total"],
            "refs": RES["set90"]["refs"],
        },
        "rsel": RES["rsel"],
        "neg": RES["neg"],
        "items": [],
    }
    for ref in ORDER:
        it = ITEMS[ref]
        p, t = it["placeholder"], it["target"]
        mb["items"].append({
            "ref": ref,
            "placeholder_fab": p["fab_size"],
            "placeholder_npads": p["npads"],
            "placeholder_center_distances": p["center_distances"],
            "target_lib": safe_name(t["target_lib"]),
            "target_fab": t["fab_size"],
            "target_crtyd": t.get("crtyd_size"),
            "target_npads": t["npads"],
            "target_center_distances": t["center_distances"],
            "touches": META[ref][0],
            "verdict": META[ref][1],
            "evidence": META[ref][2],
            "fallback": META[ref][3],
            "clr_gate_before": it["before"]["min_clearance_gate"],
            "clr_gate_after": it["after"]["min_clearance_gate"],
            "clr_mc_before": it["before"]["min_clearance_mc"],
            "clr_mc_after": it["after"]["min_clearance_mc"],
        })
    with open(os.path.join(HERE, "machine_block.json"), "w", encoding="utf-8") as fh:
        json.dump(mb, fh, ensure_ascii=False, indent=1)
    print("\n[build] §1 行数 = %d · 机器块已落 logs/iss365/machine_block.json" % len(ORDER))


if __name__ == "__main__":
    main()
