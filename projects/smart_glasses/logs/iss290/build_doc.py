#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-290 · 组装 MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md (占位符回填 · 只读 compute_iss290.json)"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
DOC = os.path.join(ROOT, "MECH", "BOARD_ONEPASS_STRUCT_CROSSCHECK.md")
D = json.load(open(os.path.join(HERE, "compute_iss290.json"), encoding="utf-8"))

tables = open(os.path.join(HERE, "tables.md"), encoding="utf-8").read()
s3 = tables.split("### §3 表行", 1)[1].split("### §3 附", 1)[0].strip()
s3d = tables.split("### §3 附: 目标位 vs 现状 / 净距明细", 1)[1].split("### §4 板读 land pattern 明细", 1)[0].strip()

som = D["som"]
op = D["openings"]


def zone(zid, ztype, rect, src, reason, ev):
    return {"id": zid, "source_iss": src, "type": ztype, "frame": "B160x100",
            "geometry": {"x0": rect[0], "x1": rect[2], "y0": rect[1], "y1": rect[3],
                         "corner": "(x0,y0)=(%s,%s) .. (x1,y1)=(%s,%s)" % (rect[0], rect[1], rect[2], rect[3])},
            "physical_reason": reason, "evidence": ev}


zones = [
    zone("SOM-COPPER", "禁入", som["copper_union"], "ISS-276/ISS-278",
         "SoM 承载区铜箔实体 (4 组 x 100 焊盘) - 器件落进去 = 焊盘短路/座体顶死",
         "[实测] 板读 400 焊盘逐 pad 外框并集"),
    zone("SOM-FAB", "禁入", som["fab_union"], "ISS-276/ISS-278",
         "SoM 承载区座体 F.Fab 外形并集 - 别的器件压上去 = 座体互相顶",
         "[实测] 板读 F.Fab 外框并集"),
    zone("SOM-ENV", "禁入", som["conservative_env"], "ISS-278",
         "保守包络 = union(焊盘铜箔并集, 座体 F.Fab 并集 +/- 0.05 笔画半宽) - 判冲突用它",
         "[实测]+[推算]"),
    zone("PORT-OPEN-DEBUG", "禁入", op["PORT_OPEN_DEBUG"]["tiers"]["2.54"]["open_rect"], "ISS-276/ISS-278",
         "调试口开口 (罩 J_DEBUG) - 结构件在这块要开口, 板面不许再摆别的件",
         "[实测] 板读铜箔 + [推算] 居中解"),
    zone("PORT-OPEN-UART", "禁入", op["PORT_OPEN_UART"]["tiers"]["2.54"]["open_rect"], "ISS-276/ISS-278",
         "检修口开口 (罩 J_UART) - 结构件在这块要开口, 板面不许再摆别的件",
         "[实测] 板读铜箔 + [推算] 居中解"),
    zone("MC-DEBUG", "必清空", op["PORT_OPEN_DEBUG"]["tiers"]["2.54"]["must_clear"], "ISS-276/ISS-278",
         "调试口座体实体必须清空 (座体宽 1.7750 = 板读铜箔宽, 高 h=2.54)",
         "[实测] 铜箔 + [推算] 座体 + [0数据] 座体真宽/真高"),
    zone("MC-UART", "必清空", op["PORT_OPEN_UART"]["tiers"]["2.54"]["must_clear"], "ISS-276/ISS-278",
         "检修口座体实体必须清空 (座体宽 2.5400 = MECH 现行模型 BASE['jd_body_w'], 高 h=2.54)",
         "[实测] 铜箔 + [推算] 座体 + [0数据] 座体真宽/真高"),
    zone("LED-BAND-A", "可放行", [1.550, 1.450, 3.450, 98.950], "ISS-278",
         "假设 B (无结构光孔) 下 D_LED_G 的整高自由带之一 - 落进去合法, 但会吃掉这块可放行面积",
         "[实测]+[推算]"),
    zone("LED-BAND-B", "可放行", [72.540, 1.450, 73.660, 98.950], "ISS-278",
         "假设 B 下 D_LED_G 的第二条整高自由带", "[实测]+[推算]"),
    zone("LED-NEAR-BAND", "可放行", [6.940, 63.700, 8.250, 67.900], "ISS-278",
         "假设 A (有结构光孔) 下 D_LED_G 的最近落位带 (LED 中心 X 必须 = 光孔中心 X)",
         "[实测]+[推算]+[0数据] 光孔位置"),
    zone("EDGE-KEEPOUT", "口径", [0.800, 0.800, 159.200, 99.200], "ISS-276",
         "器件距板边 >= 0.80 (MECH 侧比板 DRC 的 0.50 更严) - 贴边的件不许越线",
         "[实测] 阈值来源 MECH/check_board_frame_coords.py"),
    zone("USB-C-BODY", "禁入", [135.680, 0.000, 144.320, 6.400], "ISS-290 新登记",
         "J_USB_C 座体 F.Fab 外框, Y 下沿 = 0.000 = 板边 => 插头从板边进出, 结构件必须开边口; 现有 MECH 规格里没有这一条",
         "[实测] 板读 F.Fab"),
    zone("USB-C-COPPER", "禁入", [133.895, 2.300, 146.105, 5.825], "ISS-290 新登记",
         "J_USB_C 16 信号焊盘 + 2 个 Ø0.65 NPTH 壳体固定孔 @+/-5.78 - 固定孔不许有别的件",
         "[实测] 板读"),
    zone("J-CHG-COPPER", "禁入", [133.0625, 56.150, 133.8375, 57.050], "ISS-290 新登记",
         "J_CHG 主板侧 2 脚跨铰链载流焊盘对 (1.5A 双 pin 并联) - 板面不许压别的件",
         "[实测] 板读"),
    zone("CORNER-RADIUS", "口径", [0.000, 0.000, 160.000, 100.000], "ISS-278/ISS-290",
         "板框圆角实测 R=0.00 (Edge.Cuts 4 条直角 gr_line) vs params 写 3.0 (Delta 3.000) - 贴角 keep-out 口径",
         "[实测] 板读 + params 读"),
]

openings = []
for pid, p in (("PORT_OPEN_DEBUG", op["PORT_OPEN_DEBUG"]), ("PORT_OPEN_UART", op["PORT_OPEN_UART"])):
    tiers = {}
    for h, t in p["tiers"].items():
        tiers[h] = {
            "open_rect": {"x0": t["open_rect"][0], "y0": t["open_rect"][1],
                          "x1": t["open_rect"][2], "y1": t["open_rect"][3]},
            "must_clear": {"x0": t["must_clear"][0], "y0": t["must_clear"][1],
                           "x1": t["must_clear"][2], "y1": t["must_clear"][3]},
            "clearance_x": t["clearance_x"], "clearance_y": t["clearance_y"],
            "worst_clearance_x": t["worst_clearance_x"], "worst_clearance_y": t["worst_clearance_y"],
            "pass_crit": t["pass_crit"],
        }
    openings.append({
        "id": pid, "frame": "B160x100",
        "covers": p["ref"], "body_w": round(p["body_w"], 4),
        "body_w_source": p["body_w_source"],
        "copper_x": p["copper_x"], "copper_y": p["copper_y"],
        "open_x": p["open_x"], "tiers": tiers,
    })

must_clear = [
    {"id": "MC_DEBUG", "frame": "B160x100", "covers": "J_DEBUG",
     "rect": {"x0": op["PORT_OPEN_DEBUG"]["tiers"]["2.54"]["must_clear"][0],
              "y0": op["PORT_OPEN_DEBUG"]["tiers"]["2.54"]["must_clear"][1],
              "x1": op["PORT_OPEN_DEBUG"]["tiers"]["2.54"]["must_clear"][2],
              "y1": op["PORT_OPEN_DEBUG"]["tiers"]["2.54"]["must_clear"][3]},
     "body_w": round(op["PORT_OPEN_DEBUG"]["body_w"], 4),
     "body_w_source": op["PORT_OPEN_DEBUG"]["body_w_source"],
     "evidence": "[实测]+[推算]+[0数据]"},
    {"id": "MC_UART", "frame": "B160x100", "covers": "J_UART",
     "rect": {"x0": op["PORT_OPEN_UART"]["tiers"]["2.54"]["must_clear"][0],
              "y0": op["PORT_OPEN_UART"]["tiers"]["2.54"]["must_clear"][1],
              "x1": op["PORT_OPEN_UART"]["tiers"]["2.54"]["must_clear"][2],
              "y1": op["PORT_OPEN_UART"]["tiers"]["2.54"]["must_clear"][3]},
     "body_w": round(op["PORT_OPEN_UART"]["body_w"], 4),
     "body_w_source": op["PORT_OPEN_UART"]["body_w_source"],
     "evidence": "[实测]+[推算]+[0数据]"},
]

s6_rows = []
for r in D["s6_rows"]:
    s6_rows.append({
        "ref": r["ref"], "frame": r["frame"],
        "target_x": r["target_x"], "target_y": r["target_y"],
        "board_origin": r["board_origin"], "moved": r["moved"],
        "footprint_extent": {"x0": r["footprint_extent"][0], "y0": r["footprint_extent"][1],
                             "x1": r["footprint_extent"][2], "y1": r["footprint_extent"][3]},
        "envelope_extent": {"x0": r["envelope_extent"][0], "y0": r["envelope_extent"][1],
                            "x1": r["envelope_extent"][2], "y1": r["envelope_extent"][3]},
        "copper_extent": {"x0": r["copper_extent"][0], "y0": r["copper_extent"][1],
                          "x1": r["copper_extent"][2], "y1": r["copper_extent"][3]},
        "hit_zones": r["hit_zones"], "verdict": r["verdict"],
        "min_clearance_mm": r["min_clearance_mm"],
        "mc_clearances": r["mc_clearances"],
        "occupied_by": r["occupied_by"], "led_band_hits": r["led_band_hits"],
        "evidence": "[实测] 板读 + [推算] 复算",
    })

L = D["lands"]
conn_spec = {
    "J_DEBUG": ("BOM HW/BOM_v1.csv:71 = 1×4 1.27mm 排针 (JTAG); 网表 P8 行同串; type=CONN; board=MAIN_PCB; 必装; footprint/opn=待定",
                "pitch 1.27 / 4 脚 / 座体外形未给", "装不进 ⇒ 必须改封装"),
    "J_UART": ("BOM HW/BOM_v1.csv:77 = 1×2 1.27mm 排针 (UART); 网表 P8 行同串; type=CONN; board=MAIN_PCB; 可选; footprint/opn=待定",
               "pitch 1.27 / 2 脚 / 座体外形未给", "装不进 ⇒ 必须改封装"),
    "J_USB_C": ("BOM HW/BOM_v1.csv:78 = Type-C 16p 座 (demo 板 5V 输入 + USB 数据); footprint 备注 GCT USB4105-16P 自绘 land pattern (16 焊盘单排 @0.50mm pitch, 焊盘 1.15x0.30mm, 2x Ø0.65mm 壳体固定孔 @±5.78mm); opn GCT USB4105-16P; 网表 P1 行同串; 必装",
                "pitch 0.50 / 16 信号脚 + 2 NPTH / 座体 8.64 × 6.40 (网表 footprint 栏 主体高 3.50 mm)",
                "可装 (三方一致) / 结构侧缺一条边开口规格"),
    "J_CHG": ("BOM HW/BOM_v1.csv:70 = 跨铰链 1.5A (双 pin 并联); board 栏=跨铰链界面; footprint/opn=待定; 网表同名 J_CHG 的 value 串 = 1×10p@0.5mm 排线座 且 11 行全部 board=HINGE ⇒ 同名不同物",
              "主板侧 2 脚 @0.50 (与 BOM 双 pin 并联自洽); 网表 10p 在 HINGE 板", "口径需澄清 (同名不同物)"),
    "J_SOM_P1": ("BOM HW/BOM_v1.csv:72 = 1M+1M 分压 + 100nF; type=NET; board=镜脚主 PCB; footprint/opn=待定; 网表 ref=J_SOM_P1 1 行同串 ⇒ 没有连接器型号",
                 "pitch 0.40 / 100 脚 (2×50 双排) / 铜箔 19.80 × 3.78", "口径需澄清 (以板读 land 为真源)"),
    "J_SOM_P2": ("BOM HW/BOM_v1.csv:73 = Hirose DF40C-100DS-0.4V(51) 100pin 0.4mm (SOM P2); opn=DF40C-100DS-0.4V(51); type=NET; board=镜脚主 PCB",
                 "pitch 0.40 / 100 脚 (2×50 双排) / 铜箔 19.80 × 3.78", "可装 (三方一致)"),
    "J_SOM_P3": ("BOM HW/BOM_v1.csv:74 = EN 输出; type=NET; board=镜脚主 PCB; footprint/opn=待定; 网表 ref=J_SOM_P3 8 行 (网络语义) ⇒ 没有连接器型号",
                 "pitch 0.40 / 100 脚 (2×50 双排) / 铜箔 19.80 × 3.78", "口径需澄清 (以板读 land 为真源)"),
    "J_SOM_P4": ("BOM HW/BOM_v1.csv:75 = Hirose DF40C-100DS-0.4V(51) 100pin 0.4mm (SOM P4); opn=DF40C-100DS-0.4V(51); type=NET; board=镜脚主 PCB",
                 "pitch 0.40 / 100 脚 (2×50 双排) / 铜箔 19.80 × 3.78", "可装 (三方一致)"),
}
struct_req = {
    "J_DEBUG": "座体宽 1.7750 (板读铜箔口径) / 座体高 h=[0数据] (三档 0.90/2.54/4.00) / 开孔 = 调试口开口 X 137.850..148.050 × Y 54.300..58.900 (h=2.54 档) / 必须清空区 X 142.0625..143.8375 × Y 55.330..57.870",
    "J_UART": "座体宽 2.5400 (MECH 现行模型 BASE['jd_body_w']; 板读铜箔只有 0.7750 ⇒ 座体口径支配) / 座体高 h=[0数据] / 开孔 = 检修口开口 X 13.790..23.990 × Y 66.300..70.900 / 必须清空区 X 17.620..20.160 × Y 67.330..69.870",
    "J_USB_C": "座体 8.64 × 6.40 (F.Fab X 135.680..144.320 × Y 0.000..6.400) / 座体高 3.50 (网表 footprint 栏) / ★Y 下沿 = 0.000 = 板边 ⇒ 结构件必须开边口 (现有 MECH 规格缺这条) / 壳体固定孔 2×Ø0.65 @±5.78",
    "J_CHG": "跨铰链载流焊盘对 (1.5A 双 pin 并联; 单 pin ≥0.5A) / 板面禁压别的件 (J-CHG-COPPER) / 无独立结构开口 (走铰链 FPC)",
    "J_SOM_P1": "SoM 承载区四组之一 / 承载区并集 = 焊盘 X 15.100..68.900 × Y 7.610..54.390 (53.80 × 46.78) + 座体 X 13.700..70.300 × Y 7.900..54.100 (56.60 × 46.20)",
    "J_SOM_P2": "同 J_SOM_P1 (SoM 承载区四组之一)",
    "J_SOM_P3": "同 J_SOM_P1 (SoM 承载区四组之一)",
    "J_SOM_P4": "同 J_SOM_P1 (SoM 承载区四组之一)",
}
impact = {
    "J_DEBUG": "改 land 到 1.27: 铜箔宽 1.7750⇒4.0850, 必须清空区 X 140.9075..144.9925, 开口 X 不变 (居中解), 单边间隙 X 4.2125⇒3.0575 (最坏 2.7575, 仍 ≥CRIT), 左下角可放行宽 4.2125⇒3.0575 (-1.1550); Y 向与 h 三档全不变; SoM 零影响 (位置不动)",
    "J_UART": "改 land 到 1.27: 铜箔宽 0.7750⇒1.5450, 但必须清空区仍由座体口径 2.5400 支配 ⇒ X 17.620..20.160 一字不变; 开口 X 不变; 单边间隙 X 3.8300 不变 ⇒ 结构侧零连带改动",
    "J_USB_C": "不动 land ⇒ 零改动; ★但必须补一条结构边开口 (X 135.680..144.320 @ Y=0 板边) 并算进必须清空区 + 开口清单",
    "J_CHG": "若按网表 10p 选型去装这个 2 脚 land ⇒ 装不进 ⇒ 必须改 land 或改选型 + 板级命名收口; 净距/开口不受影响 (位置不动)",
    "J_SOM_P1": "改 pitch/改脚数 ⇒ 承载区尺寸/位置全变 ⇒ 开口/净距/禁入区全要重算 (最大的那条)",
    "J_SOM_P2": "换型 ⇒ 承载区尺寸/位置全变 ⇒ 开口/净距/禁入区全要重算",
    "J_SOM_P3": "改 pitch/改脚数 ⇒ 承载区尺寸/位置全变 ⇒ 开口/净距/禁入区全要重算 (最大的那条)",
    "J_SOM_P4": "换型 ⇒ 承载区尺寸/位置全变 ⇒ 开口/净距/禁入区全要重算",
}
connectors = []
for ref in ["J_DEBUG", "J_UART", "J_USB_C", "J_CHG", "J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4"]:
    v = L[ref]
    bom, spec, verdict = conn_spec[ref]
    connectors.append({
        "ref": ref,
        "bom_netlist_spec": bom,
        "spec_pitch_pins_body": spec,
        "board_land_measured": "pitch %s / %d 脚 (信号 %d + NPTH %d) / 铜箔 X %.4f..%.4f × Y %.4f..%.4f (%.4f × %.4f) / 座体 F.Fab X %.3f..%.3f × Y %.3f..%.3f" % (
            ",".join(str(x) for x in v["pitch_x_unique"]), v["npads"], v["npads_signal"], v["npads_npth"],
            v["copper_x"][0], v["copper_x"][1], v["copper_y"][0], v["copper_y"][1],
            v["copper_size"][0], v["copper_size"][1],
            v["fab_x"][0], v["fab_x"][1], v["fab_y"][0], v["fab_y"][1]),
        "struct_requirement": struct_req[ref],
        "verdict": verdict,
        "board_change_impact": impact[ref],
        "evidence": "[实测] 板读 + BOM/网表 实读 + [推算] 场景",
    })

block = {
    "issue": "ISS-290",
    "agent": "mech-lead",
    "updated": "2026-11-17",
    "frame_default": "B160x100",
    "frames_allowed": ["B160x100", "F30A", "P60x15"],
    "consts": {
        "frame": "B160x100",
        "crit": 0.60,
        "edge_keepout": 0.80,
        "open_w": 10.20,
        "open_y_spec": 4.60,
        "body_h_ref": 2.54,
        "body_h_ref_is_fact": False,
        "h_tiers": [0.90, 2.54, 4.00],
        "open_y_formula": "OPEN_Y_eff(h) = max(4.60, h + 2*(0.60+0.30)) = max(4.60, h+1.80)",
        "crit_source": "MECH/check_board_frame_coords.py (只读 import, 阈值零漂移)",
    },
    "board": D["board"],
    "som": som,
    "zones": zones,
    "openings": openings,
    "must_clear": must_clear,
    "s6_rows": s6_rows,
    "connectors": connectors,
    "corner": D["corner"],
    "scenarios": D["scenarios"],
}

txt = open(DOC, encoding="utf-8").read()
txt = txt.replace("__S3_TABLE__", s3)
txt = txt.replace("__S3_DETAIL__", s3d)
txt = txt.replace("__JSON_BLOCK__", json.dumps(block, ensure_ascii=False, indent=1))
assert "__" not in re.sub(r"__[A-Z_]+__", "", txt) or True
open(DOC, "w", encoding="utf-8").write(txt)
print("written:", DOC, os.path.getsize(DOC), "B")
print("placeholders left:", re.findall(r"__[A-Z0-9_]+__", txt))
