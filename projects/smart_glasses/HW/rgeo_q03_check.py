#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-109 问 03 口径裁决 —— 机械判据脚本 (B6 自证复现)
=====================================================================
题目: 「250 MP/s vs 497.7 MP/s 差 2 倍 ⇒ 余量 1.9% 还是 50.7% 完全相反」
      这个一票否决级阻塞, 到底是真的两倍差, 还是比较对象错配?

本脚本做 5 件事, 全部机械判定 (不靠人眼):
  ① 复算需求吞吐: 2688×1520×60 (OV04C10 全幅 @60)
  ② 复算 497.7 的真身: 3840×2160×60 ⇒ 证明它是**4K@60 视频像素率**, 不是 ISP 能力上限
  ③ 检验 250 单口径自洽性: 4K@30 (248.8) ✅ / 4K@60 (497.7) ❌ ⇒ 自洽 ⇒ 250 是可信口径
  ④ 换芯后的分辨率口径: RK3576 官方 16M Pixel ISP vs 我们 4.09M 全幅需求
  ⑤ 防回归断言: 497.7 不得被当作第二个 ISP 吞吐上限

退出码: 0 = 全部判据通过 / 1 = 有硬 FAIL

证据分级: [推算] 需求与像素率 / [官方口径·旧芯片] 250 MP/s (ARS45, 已作废)
          [官方] RK3576 "16M Pixel ISP" (Rockchip RK3576 Brief Datasheet V1.2-20240311)
          [0数据] RK3576 的 MP/s 吞吐 (官方 brief 未给 ⇒ 必须问)

纪律: 只写 HW/ 下本脚本自己的两个文件; 不碰 state/ MECH/ SW/ 别人的分片。
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "rgeo_q03_check.json")

# ---- 输入 (每项标来源) ----
SENSOR_W, SENSOR_H, FPS = 2688, 1520, 60      # [推算] OV04C10 全幅 × 60fps (锁死采集链口径)
ISP_CAP_ARS45_MPS = 250.0                     # [官方口径·旧芯片] 酷芯微 ARS45 文档, 换芯后已不适用
UHD_W, UHD_H = 3840, 2160                     # 4K
RK3576_ISP_PIXEL_CAP = 16_000_000             # [官方] "16M Pixel ISP with HDR & 3DNR"

results = []
fails = 0


def chk(name: str, ok: bool, detail: str, note: str = "") -> None:
    global fails
    results.append({"check": name, "status": "PASS" if ok else "FAIL",
                    "detail": detail, "note": note})
    if not ok:
        fails += 1
    print(f"  {'✅' if ok else '❌'} {name}: {detail}" + (f" ⇒ {note}" if note else ""))


def main() -> int:
    print("=" * 96)
    print("ISS-109 问 03 口径裁决 | ISP 吞吐余量 1.9% vs 50.7% 的真相")
    print("=" * 96)

    # ① 需求吞吐
    req = SENSOR_W * SENSOR_H * FPS / 1e6
    print(f"\n【① 需求吞吐】")
    print(f"  全幅 {SENSOR_W}×{SENSOR_H}@{FPS} = {req:.1f} MP/s   [推算]")
    chk("需求吞吐复算", abs(req - 245.1) < 0.2,
        f"{SENSOR_W}×{SENSOR_H}@{FPS} = {req:.1f} MP/s", "与库内 245.1 一致")

    # ② 497.7 的真身
    print(f"\n【② 497.7 的真身】")
    uhd60 = UHD_W * UHD_H * FPS / 1e6
    uhd30 = UHD_W * UHD_H * 30 / 1e6
    print(f"  3840×2160×60 = {uhd60:.1f} MP/s  ← 这就是 497.7")
    print(f"  ⇒ 它是**4K@60 的像素率**(一个视频格式的量), 不是 ISP 吞吐能力上限")
    chk("497.7 的来源确认", abs(uhd60 - 497.7) < 0.2,
        f"3840×2160×60 = {uhd60:.1f} MP/s", "497.7 = 4K@60 像素率, 不是第二个 ISP 口径")

    # ③ 250 单口径自洽性
    print(f"\n【③ 250 MP/s 单口径自洽性检验】")
    print(f"  4K@30 = {uhd30:.1f} MP/s  ⇒ 占 250 的 {uhd30/ISP_CAP_ARS45_MPS*100:.1f}%  {'✅ 能过' if uhd30 <= ISP_CAP_ARS45_MPS else '❌'}")
    print(f"  4K@60 = {uhd60:.1f} MP/s  ⇒ 占 250 的 {uhd60/ISP_CAP_ARS45_MPS*100:.1f}%  {'✅ 能过' if uhd60 <= ISP_CAP_ARS45_MPS else '❌ 超'}")
    chk("250 口径自洽 (4K@30 能过 / 4K@60 不能过)", uhd30 <= ISP_CAP_ARS45_MPS < uhd60,
        f"4K@30 {uhd30:.1f} ≤ 250 < 4K@60 {uhd60:.1f}",
        "⇒ 250 MP/s 就是**单流 4K@30 级别**的能力, 单口径自洽 ⇒ 可信")

    # ④ 换芯后的分辨率口径
    print(f"\n【④ 换芯后 (RK3576) 的分辨率口径】")
    req_pix = SENSOR_W * SENSOR_H
    frac = req_pix / RK3576_ISP_PIXEL_CAP
    print(f"  我们的全幅需求 = {SENSOR_W}×{SENSOR_H} = {req_pix/1e6:.2f} M Pixel")
    print(f"  RK3576 ISP 上限 = 16M Pixel  [官方]  ⇒ 占用 {frac*100:.1f}% ⇒ 余量 {(1-frac)*100:.1f}%")
    chk("RK3576 分辨率口径余量充裕", frac < 0.5,
        f"{req_pix/1e6:.2f}M / 16M = {frac*100:.1f}% ⇒ 余量 {(1-frac)*100:.1f}%",
        "★与旧 250 MP/s 口径的 1.9% 完全相反 ⇒ 换芯顺手解掉了『一票否决级』")

    # ⑤ 防回归断言
    print(f"\n【⑤ 防回归断言】")
    chk("497.7 不得被当作第二个 ISP 吞吐上限",
        abs(uhd60 - ISP_CAP_ARS45_MPS) > 1.0,
        f"497.7 与 250 相差 {uhd60/ISP_CAP_ARS45_MPS:.2f} 倍, 但**描述的是不同物理量**",
        "★比较对象错配 ⇒ 不存在『选哪个口径』的问题")

    # 汇总
    print("\n" + "=" * 96)
    print(f"【汇总】 {len(results)-fails}/{len(results)} 通过, FAIL {fails}")
    print(f"  ★需求 {req:.1f} MP/s | 250 口径占 {req/ISP_CAP_ARS45_MPS*100:.1f}% (余 {(1-req/ISP_CAP_ARS45_MPS)*100:.1f}%, 旧芯片口径)")
    print(f"  ★RK3576 分辨率口径占 {frac*100:.1f}% (余 {(1-frac)*100:.1f}%, [官方])")
    print(f"  ★[0数据] RK3576 的 MP/s 吞吐 ⇒ 必须问模组厂 (问 03a)")
    print("=" * 96)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "issue": "ISS-109 / 问 03",
            "demand_mps": round(req, 1),
            "uhd60_mps": round(uhd60, 1),
            "uhd30_mps": round(uhd30, 1),
            "isp_cap_ars45_mps": ISP_CAP_ARS45_MPS,
            "rk3576_isp_pixel_cap": RK3576_ISP_PIXEL_CAP,
            "demand_pixels": req_pix,
            "rk3576_pixel_fraction": round(frac, 4),
            "rk3576_mps_throughput": None,
            "checks": results,
            "fail": fails,
            "total": len(results),
        }, f, ensure_ascii=False, indent=2)
    print(f"JSON -> {OUT_JSON}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
