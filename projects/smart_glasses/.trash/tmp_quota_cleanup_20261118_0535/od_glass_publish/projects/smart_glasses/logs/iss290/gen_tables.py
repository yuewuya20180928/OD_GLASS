#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-290 · 从 compute_iss290.json 生成 §3 / §4 的 markdown 表行 (只读)"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "compute_iss290.json"), encoding="utf-8"))

print("### §3 表行")
print()
print("| `ref` | `frame` | `target_x` | `target_y` | `footprint_extent` (F.Fab 外形 · 落位后) | `hit_zones` | `verdict` | `min_clearance_mm` | `evidence` |")
print("|---|---|---|---|---|---|---|---|---|")
for r in D["s6_rows"]:
    fe = r["footprint_extent"]
    hits = ", ".join("`%s`" % h for h in r["hit_zones"]) if r["hit_zones"] else "— (空)"
    print("| `%s` | `%s` | %.3f | %.3f | X %.3f..%.3f × Y %.3f..%.3f (%s) | %s | **%s** | %.4f | `[实测]` 板读 + `[推算]` 复算 |"
          % (r["ref"], r["frame"], r["target_x"], r["target_y"], fe[0], fe[2], fe[1], fe[3],
             "%.2f×%.2f" % (r["footprint_extent_size"][0], r["footprint_extent_size"][1]),
             hits, r["verdict"], r["min_clearance_mm"]))

print()
print("### §3 附: 目标位 vs 现状 / 净距明细")
print()
print("| `ref` | 板上现状原点 | 是否位移 | 落位包络 (F.Fab ∪ 铜箔) | 到 `MC_DEBUG` | 到 `MC_UART` | 占位冲突 | LED 可放行带侵占 |")
print("|---|---|---|---|---|---|---|---|")
for r in D["s6_rows"]:
    e = r["envelope_extent"]
    print("| `%s` | (%.3f, %.3f) | %s | X %.3f..%.3f × Y %.3f..%.3f | %.4f | %.4f | %s | %s |"
          % (r["ref"], r["board_origin"][0], r["board_origin"][1],
             "**是**" if r["moved"] else "否",
             e[0], e[2], e[1], e[3],
             r["mc_clearances"]["MC_DEBUG"], r["mc_clearances"]["MC_UART"],
             (", ".join(r["occupied_by"]) if r["occupied_by"] else "无"),
             (", ".join(r["led_band_hits"]) if r["led_band_hits"] else "无")))

print()
print("### §4 板读 land pattern 明细")
print()
for ref, v in D["lands"].items():
    print("- `%s`: 焊盘 %d (信号 %d / NPTH %d) · 铜箔 X %.4f..%.4f × Y %.4f..%.4f (%.4f × %.4f) · F.Fab X %.3f..%.3f × Y %.3f..%.3f (%.2f × %.2f) · pitch_x %s · %d 行 × %d 列"
          % (ref, v["npads"], v["npads_signal"], v["npads_npth"],
             v["copper_x"][0], v["copper_x"][1], v["copper_y"][0], v["copper_y"][1],
             v["copper_size"][0], v["copper_size"][1],
             v["fab_x"][0], v["fab_x"][1], v["fab_y"][0], v["fab_y"][1],
             v["fab_size"][0], v["fab_size"][1],
             v["pitch_x_unique"], v["n_rows"], v["pad_x_count"]))

print()
print("### §6 corner 口径数")
print()
c = D["corner"]
for k in ("edge_keepout_mm", "R_assumed_mm", "board_size", "corner_usable_area_sharp_mm2",
          "corner_usable_area_roundR3_mm2", "corner_usable_delta_mm2", "board_area_sharp_mm2",
          "board_area_roundR3_mm2", "board_area_delta_mm2", "total_usable_delta_mm2"):
    print("- `%s` = %s" % (k, c[k]))

print()
print("### §5 场景数")
print()
for k, v in D["scenarios"].items():
    print("- `%s`: 铜箔 X %.4f..%.4f (宽 %.4f, 现状宽 %.4f) · 必须清空宽 %.4f (%s 支配) · 开口 X 不变 %.2f..%.2f · 单边间隙 X %.4f (最坏 %.4f, ≥CRIT %s) · 左下角可放行宽 %.4f (Δ %+.4f)"
          % (k, v["new_copper_x"][0], v["new_copper_x"][1], v["new_copper_w"], v["old_copper_w"],
             v["w_clear_used"], v["w_clear_driver"], v["open_x"][0], v["open_x"][1],
             v["clearance_x"], v["worst_clearance_x"], v["pass_crit_x"],
             v["placeable_width"], v["delta_placeable_width"]))

print()
print("### 开口三档")
print()
for pid, p in D["openings"].items():
    for h, t in p["tiers"].items():
        print("- `%s` h=%s: 开口 X %.3f..%.3f × Y %.3f..%.3f · 必须清空 X %.4f..%.4f × Y %.3f..%.3f · 单边间隙 X %.4f / Y %.4f (最坏 %.4f / %.4f) · 过 CRIT %s"
              % (pid, h, t["open_rect"][0], t["open_rect"][2], t["open_rect"][1], t["open_rect"][3],
                 t["must_clear"][0], t["must_clear"][2], t["must_clear"][1], t["must_clear"][3],
                 t["clearance_x"], t["clearance_y"], t["worst_clearance_x"], t["worst_clearance_y"],
                 t["pass_crit"]))
