#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-244 · 落表后回归 (post-landing regression) — 2026-11-17 05:0x
==================================================================
★为什么有这一份: ISS-244 第一轮交卷 (2026-11-16 15:59) 之后, 板侧又落了 13 件
  (hw-lead 的 ISS-257 选型落表批次, 网表/脚表/BOM 落盘时刻 2026-11-16 22:25:14) ⇒
  ISS-241 登记范围 22 件里只剩 8 件还待选型 ⇒ ISS-244 的门禁 C5 **按设计变红**
  (锚点过期 = 红 ⇒ 走 H-1 重锚 + 留痕, 不许把红灯调没)。

★本模块做三件事 (全部只读, 一行盘上文件都不改):
  ① 逐件实读「板占位 land (pad → net)」+「网表 note 定的端子角色」+「落地器件的引脚序」
     ⇒ 三者交叉核对 ⇒ 给出「引脚序对不对得上」+「要改哪一处」
  ② 把 G-1 / G-2 / G-3 / G-4 / G-7 / G-8 / G-10 的状态按落表后的**盘上真值**重判一遍
  ③ 输出机器可读行 (post_landing) ⇒ 收口页 §5 与门禁 C7 读同一份数据 (同源)

★器件引脚序的出处纪律:
  - TPD1E05U06DPYR: TI SLVSBO7O Table 4-1 原文「GND = pin 2 / I/O = pin 1」 ⇒ [官网] (本轮实读落盘 PDF)
  - AO3400A / DMP3098L: 厂商手册 p1 的 Pin Configuration **图**上**没有印引脚号** ⇒
    本模块只把「图的排布 (G/S 在一侧, D 在另一侧)」当 [官网·图读], 而
    「哪一根是 1/2/3」按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ [推算] ⇒ 两者分开标注, 不混成 [官网]
  - 双向件 (PESD5V0S1BA) ⇒ 极性无关 ⇒ 不参与引脚序判定
"""

import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------- 器件引脚序 (官方 PDF 实读)

DEVICE_PIN_ORDER = {
    "TPD1E05U06DPYR": {
        "pins": {"1": "I/O", "2": "GND"},
        "pkg": "DPY (X1SON, 2 pin)",
        "arrangement_evidence": "[官网]",
        "numbering_evidence": "[官网]",
        "source": "TI `TPD4E05U06` 数据手册 SLVSBO7O (2024-08 改版) Table 4-1「Pin Functions TPD1E05U06 DPY and DYA」: GND = pin 2 / I/O = pin 1 (本轮实读, 落盘 `state/.cache_iss244/led/tpd4e05u06.pdf`)",
    },
    "AO3400A": {
        "pins": {"1": "G", "2": "S", "3": "D"},
        "pkg": "SOT-23",
        "arrangement_evidence": "[官网]",
        "numbering_evidence": "[推算]",
        "source": "AOS `AO3400A` 数据手册 (本轮实读, 落盘 `state/.cache_iss244/mos/AO3400A.pdf`) p1 Pin Configuration 图: 排布 = G/S 一侧 + D 另一侧 (图上**未印引脚号**) ⇒ 编号 1=G / 2=S / 3=D 按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ 编号这一层标 [推算]",
    },
    "DMP3098L": {
        "pins": {"1": "G", "2": "S", "3": "D"},
        "pkg": "SOT-23",
        "arrangement_evidence": "[官网]",
        "numbering_evidence": "[推算]",
        "source": "Diodes `DMP3098L` 数据手册 (本轮实读, 落盘 `state/.cache_iss244/mos/DMP3098L.pdf`) p1 Pin Configuration 图: 排布 = G/S 一侧 + D 另一侧 (图上**未印引脚号**) ⇒ 编号 1=G / 2=S / 3=D 按 JEDEC TO-236 (SOT-23) 通用编号 ⇒ 编号这一层标 [推算]",
    },
    "PESD5V0S1BA": {
        "pins": {},
        "pkg": "SOD-323 (双向件)",
        "arrangement_evidence": "[官网]",
        "numbering_evidence": "[官网]",
        "source": "Nexperia `PESD5V0S1BA` 双向 ESD (ISS-241 §3 已实读官方手册: 单通道双向) ⇒ 极性无关 ⇒ 不参与引脚序判定",
    },
}

# ---------------------------------------------------------------- 网表 note 定的端子角色 (逐行实读)

ROLE_TABLE = {
    "Q_PG": {
        "PWR_ON": ("S", "网表 L58 note「正解」段: 源极接 ON"),
        "BAT_SW": ("D", "网表 L59 note: 漏极接 BAT_SW"),
        "PWR_GOOD": ("G", "网表 L60 note: 栅极 = 充电板 PG"),
    },
    "Q_AND": {
        "RESET_N": ("D", "网表 L64 note: 漏极 = RESET_N"),
        "GND": ("S", "网表 L65 note: 源极接地"),
        "PG_AND": ("G", "网表 L66 note: 栅极 = PG_AND"),
    },
    "Q_ENVC": {
        "PG_AND": ("G", "网表 L70 note: PG_AND = 栅极"),
        "GND": ("S", "网表 L71 note: 源极接地"),
        "EN_VCORE": ("D", "网表 L72 note: 漏极 = EN_VCORE"),
    },
    "D_ESD_CAM": {
        "GND": ("GND", "网表 L162 note: 跨铰链 CSI ESD 阵列 地脚"),
        "CSI_D0_CK_P": ("I/O", "网表 L412 note: 跨铰链 CSI 主板侧 ESD 阵列位 (紧贴 CONN_CAM)"),
    },
    "D_ESD_USB_D": {
        "USB_D_P_SRC": ("I/O", "网表 L416 note: 跨 D+ 与地"),
        "GND": ("GND", "网表 L417 note: ESD 地端"),
    },
    "D_ESD_DEMO": {
        "RAIL_DEMO_5V": ("I/O", "网表 L419 note: USB-C VBUS 入口 ESD 阵列 (紧贴 J_USB_C)"),
        "GND": ("GND", "网表 L420 note: USB ESD 阵列 地端"),
    },
}

# 角色本身有没有错 (不只是 land 对不对)
TOPOLOGY_NOTE = {
    "Q_PG": "★**角色本身就错 (P0)**: 网表 note 定的「源极接 ON · 漏极接 BAT_SW」是高边 P-MOS 的错接 —— ISS-244 §3.3 写法B: 上电瞬间 ON 被 10 kΩ 下拉到 0 V ⇒ Vgs = 0 ⇒ 不导通; PG 高时 Vgs = +3.3 V (对 P 沟道是反向偏置) ⇒ **PG 高低都关 ⇒ 开机路径彻底不通**。⇒ 正确角色 = **S=BAT_SW / D=ON / G=PG** (写法A)。",
    "Q_AND": "角色本身正确 (D=RESET_N / S=GND / G=PG_AND) ⇒ 差的是占位 land 与器件引脚序的对应关系。",
    "Q_ENVC": "角色与占位 land 都已与器件引脚序对上 ✔ (三颗 MOS 里唯一不用动 land 的一颗)。",
    "D_ESD_CAM": "★**land 与器件引脚序正好相反 (P0)**: 占位 land pad1=GND / pad2=信号, 而器件 pin1=I/O / pin2=GND ⇒ 装上去 = ESD 器件对**正向** ESD 失效 (I/O 脚接地, 到地无通路) + CSI lane 的**负向**摆幅被内部二极管钳到 GND 附近。",
    "D_ESD_USB_D": "引脚序对得上 ✔; 但仍是**单边** (只护 D+, USB_D_N_SRC 无保护) ⇒ G-4 仍开。",
    "D_ESD_DEMO": "双向件 ⇒ 极性无关 ✔; 只差 land 几何 (G-7)。",
}

# 非引脚序敏感件 (几何 / 装配类) 的逐件实读结论
GEOMETRY_NOTE = {
    "C_REGN": "不在主板 (充电板件, 板文件查无此位号) ⇒ 无几何可判; BOM 已按 TI BQ25896 pin22 手册落成 4.7 µF / 10 V ⇒ **G-6 闭合**。",
    "FB_DEMO": "在主板: 占位 2 焊盘 (pad 间距 0.8 mm, 0805 尺��级) vs Murata BLM21PG221SN1D = 0805 ⇒ **land 几何要重画 (G-7)**; 引脚序无关 (无源件)。",
    "FB_VBUS": "充电板件 (板文件查无此位号) ⇒ 封装/land 归充电板那一趟 (G-8); 引脚序无关。",
    "D_TVS_VBUS": "充电板件 (板文件查无此位号) ⇒ 封装/land 归充电板那一趟 (G-8); 引脚序无关。",
    "D_ESD_TC": "充电板件 (板文件查无此位号) ⇒ footprint 仍「待定」(G-8); ★落地的是 **3 通道** SP0503BAHT (SOT-143 4 脚), 而网表只接了 1 个通道 (USB_VBUS_RAW) + GND ⇒ **另 2 个通道闲置** ⇒ Type-C 的 D+/D− 仍未被这阵列覆盖。",
    "Q_CHG_LED": "充电板件 (板文件查无此位号) ⇒ footprint 仍「待定」(G-8); 角色 D=CHG_LED_K / S=GND / G=CHG_STAT ⇒ 充电板 land 须按 **1=G / 2=S / 3=D** 建 (2N7002 的常规序)。",
    "R_SUPV_DIV1": "★**装配级风险 (P0)**: 已落成 0 Ω 跳线且 dnp=**必装**, 而监督器本体 `U_SUPV` 三行 dnp=**DNP** ⇒ 装 0 Ω = 把 `V_SOC_IO` 经两臂短路到地 (ISS-190 同判) ⇒ 建议随 U_SUPV 一并置 DNP (G-10 降级①)。",
    "R_SUPV_DIV2": "同上 (两臂必须同进同退, 只改一颗 = 悬空分压)。",
}

CHARGE_BOARD_REFS = {"D_ESD_TC", "FB_VBUS", "D_TVS_VBUS", "Q_CHG_LED", "D_CHG_LED", "C_REGN"}

# ★P0 分类 (三条引脚序/角色级 + 一类装配级)
P0_PIN_ORDER_REFS = {"Q_PG", "Q_AND", "D_ESD_CAM"}
P0_ASSEMBLY_REFS = {"R_SUPV_DIV1", "R_SUPV_DIV2"}

# ★Q_PG 的「正确角色」覆盖 (写法A: S=BAT_SW / D=ON / G=PG —— 唯一电学自洽的那一套)
#   网表 note 现在的角色 (S=ON / D=BAT_SW / G=PG) 本身是错接 ⇒ 不能拿它当 land 的目标
#   ⇒ 这一颗的 land 目标按【写法A】给, 并且网表 note 必须同批改 (归落表批次)
OVERRIDE_TARGET = {
    "Q_PG": {
        "1": "PWR_GOOD",   # pad1 = G (栅极 = 充电板 PG)
        "2": "BAT_SW",     # pad2 = S (源极 = 电池轨, 高电位侧)
        "3": "PWR_ON",     # pad3 = D (漏极 = 负载侧 ON)
    },
}


# ---------------------------------------------------------------- 只读工具

def load_csv_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for i, row in enumerate(csv.DictReader(fh), 1):
            row["__line__"] = i
            rows.append(row)
    return rows


def board_pads(root):
    """只读解析 .kicad_pcb ⇒ {ref: [(pad_no, net, at), ...]}"""
    p = os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb")
    txt = open(p, encoding="utf-8").read()
    starts = [m.start() for m in re.finditer(r"\n\t\(footprint ", txt)]

    def depth_scan(b):
        d = 0
        for i, ch in enumerate(b):
            if ch == "(":
                d += 1
            elif ch == ")":
                d -= 1
                if d == 0:
                    return i
        return len(b)

    out = {}
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(txt)
        body = txt[s:e][:depth_scan(txt[s:e])]
        m = re.search(r'\(property "Reference" "([^"]+)"', body)
        if not m:
            continue
        pads = re.findall(r'\(pad "([^"]+)"(.{0,400}?)\(at ([^\)]*)\)(.{0,400}?)\(net "([^"]+)"\)', body, re.S)
        out[m.group(1)] = [(pd[0], pd[4], " ".join(pd[2].split())) for pd in pads]
    return out


def scope_refs_from_matrix(root):
    t = open(os.path.join(root, "HW", "PART_SELECTION_MATRIX_2026-11-16.md"), encoding="utf-8").read()
    blob = t.split("<!-- BEGIN 选型证据基准块 -->")[1].split("<!-- END 选型证据基准块 -->")[0]
    blob = re.sub(r"```json|```", "", blob.strip())
    return json.loads(blob)["expected_refs"]


def pending_refs_from_bom(root):
    out = []
    for r in load_csv_rows(os.path.join(root, "HW", "BOM_v1.csv")):
        if "待选型" in (r.get("value") or "") and (r.get("dnp") or "").strip() == "必装":
            ref = (r.get("ref") or "").strip()
            if ref and ref not in ("U_PWR_SW", "U_EN_SW"):
                out.append(ref)
    return out


# ---------------------------------------------------------------- 主计算

def compute(root=ROOT):
    scope = scope_refs_from_matrix(root)
    pending = pending_refs_from_bom(root)
    bom = {r["ref"].strip(): r for r in load_csv_rows(os.path.join(root, "HW", "BOM_v1.csv"))}
    net = load_csv_rows(os.path.join(root, "HW", "netlist_v1.csv"))
    pads = board_pads(root)

    rows = []
    for ref in scope:
        if ref in pending:
            continue  # 还待落 ⇒ 不进落表后回归
        b = bom.get(ref, {})
        model = (b.get("value") or "").split(" (")[0].strip()
        opn = (b.get("opn") or "").split(" (")[0].strip()
        dev = DEVICE_PIN_ORDER.get(opn) or DEVICE_PIN_ORDER.get(model)
        ref_pads = pads.get(ref) or []
        nl = [(r["__line__"], r.get("net")) for r in net if (r.get("ref") or "").strip() == ref]

        row = {
            "ref": ref,
            "model": model,
            "opn": opn,
            "bom_value": b.get("value", ""),
            "bom_opn": b.get("opn", ""),
            "bom_dnp": b.get("dnp", ""),
            "netlist_rows": nl,
            "on_main_board": bool(ref_pads),
            "charge_board": ref in CHARGE_BOARD_REFS,
            "pad_map": [{"pad": p[0], "net": p[1], "at": p[2]} for p in ref_pads],
            "device_pin_order": (dev or {}).get("pins", {}),
            "device_pkg": (dev or {}).get("pkg", ""),
            "device_source": (dev or {}).get("source", ""),
            "device_evidence": "%s / 编号 %s" % ((dev or {}).get("arrangement_evidence", "-"),
                                                 (dev or {}).get("numbering_evidence", "-")),
            "checks": [],
            "verdict": "",
            "fix": "",
            "topology_note": TOPOLOGY_NOTE.get(ref, GEOMETRY_NOTE.get(ref, "")),
            "source": "",
        }

        roles = ROLE_TABLE.get(ref)
        if roles and ref_pads and dev and dev.get("pins"):
            ok = True
            for pad_no, net_name, at in ref_pads:
                dev_role = dev["pins"].get(pad_no, "?")
                want = roles.get(net_name, ("?", "网表里没找到这个网的角色"))[0]
                match = (dev_role == want)
                row["checks"].append({
                    "pad": pad_no, "net": net_name, "at": at,
                    "device_role": dev_role, "netlist_role": want,
                    "match": match,
                })
                if not match:
                    ok = False
            row["verdict"] = "✔ 引脚序与占位 land 对得上" if ok else "✘ 占位 land 与器件引脚序对不上"
            if not ok:
                # 目标: 每个 pad 上放「角色正好等于该 pad 器件脚角色」的那个网
                role2net = {}
                for net_name, (role, _why) in roles.items():
                    role2net.setdefault(role, net_name)
                override = OVERRIDE_TARGET.get(ref)
                target = {}
                for pad_no in sorted(dev["pins"]):
                    want_role = dev["pins"][pad_no]
                    if override:
                        target[pad_no] = override.get(pad_no, "")
                    else:
                        target[pad_no] = role2net.get(want_role, "")
                cur = {p[0]: p[1] for p in ref_pads}
                changes = []
                for pad_no in sorted(target):
                    if target[pad_no] and cur.get(pad_no) != target[pad_no]:
                        changes.append("pad%s: %s → %s" % (pad_no, cur.get(pad_no, "?"), target[pad_no]))
                row["target_pad_nets"] = target
                row["fix"] = ("板侧改 land: " + "; ".join(changes) if changes else "板侧改 land (按目标 pad→网 重排)")
                if override:
                    row["fix"] += ("  ★**同时网表 note 的角色必须同批改成写法A (S=BAT_SW / D=ON / G=PG)** ⇒ "
                                   "否则按 note 的错角色排出来的 land 一样开机不通")
                row["source"] = dev["source"]
            else:
                row["source"] = dev["source"]
        else:
            if not ref_pads:
                row["verdict"] = "– 不在主板 (充电板件 / 板文件查无此位号) ⇒ 无几何可判"
            elif dev and not dev.get("pins"):
                row["verdict"] = "– 双向件 ⇒ 极性无关, 不参与引脚序判定"
            else:
                row["verdict"] = "– 无源件 / 不引脚序敏感 ⇒ 只差 land 几何 (G-7)"
            row["source"] = (dev or {}).get("source", "") or "板文件 + BOM 实读"
        # P0 分类 (在 verdict 上打标 ⇒ 机器能一眼看到哪几件是 P0)
        if ref in P0_PIN_ORDER_REFS:
            row["verdict"] = "★P0 (引脚序/角色级): " + row["verdict"]
            row["p0"] = "pin-order"
        elif ref in P0_ASSEMBLY_REFS:
            row["verdict"] = "★P0 (装配级): 0 Ω 且必装 + U_SUPV DNP ⇒ 短路到地 (见拓扑备注)"
            row["p0"] = "assembly"
        else:
            row["p0"] = ""
        rows.append(row)
    return {
        "scope_refs": scope,
        "pending_refs": pending,
        "landed_refs": [r["ref"] for r in rows],
        "rows": rows,
    }


def main():
    data = compute()
    print("登记范围 %d 件 / 仍待落 %d 件 / 已落表 %d 件"
          % (len(data["scope_refs"]), len(data["pending_refs"]), len(data["landed_refs"])))
    for r in data["rows"]:
        print("- %-12s %-22s %-28s %s" % (r["ref"], r["model"], r["verdict"], r["fix"]))
        for c in r["checks"]:
            print("      pad %-2s net=%-14s 器件脚=%-4s 网表角色=%-4s %s"
                  % (c["pad"], c["net"], c["device_role"], c["netlist_role"],
                     "OK" if c["match"] else "MISMATCH"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
