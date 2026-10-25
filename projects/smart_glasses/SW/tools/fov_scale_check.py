#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISP 缩放路径 FOV 自检 (ISS-056) — sw-lead / 2026-10-25
====================================================================
算清楚一件事: **ISP 用 "ROI (crop+scale)" 还是 "整幅 scale", 对角 FOV 差多少。**

投影模型: 等距 (equidistant) r = f·θ   [决策文本] 老板 10-25 19:42 工作基线
设计基线: 对角 FOV 120°                [决策文本]

用法:
  python3 fov_scale_check.py              # 全表 + 自检 (rc=0 = 自检全过)
  python3 fov_scale_check.py --tables     # 只打印表

自检项 (硬断言, 任何一条不过 rc=1):
  A1  OV04C10 全幅对角 FOV == 120.00° (±0.05)
  A2  OV04C10 1080p ROI 对角 FOV == 85.61° (±0.05)   ← ISS-053 的关键数字, 必须复现
  A3  AR0234CS 1080p 裁高对角 FOV == 116.75° (±0.05)
  A4  俯角 25° 时: 全幅正前方余量 > 0, ROI 余量 < 0 (正前方掉出画面)
  A5  等比 letterbox 的角分辨率各向异性 <= 1.01 ; 非等比拉伸 >= 1.30
  A6  立体角: 全幅=100%, ROI 路线 < 80%
"""
import math
import sys

DEG = math.pi / 180.0
DIAG_FOV_DESIGN = 120.0          # [决策文本] 对角 FOV 设计值
HALF_DIAG = DIAG_FOV_DESIGN / 2.0

# --------------------------------------------------------------------------
# sensor 参数
#   OV04C10  : 1/3" 2688x1520, 像元 1.998um  [官方] (HW/SENSOR_SELECTION.md §B3-D)
#   AR0234CS: 1/2.6" 1920x1200, 像元 3.0um  [官方] (HW/SENSOR_SELECTION.md §B3-A)
# --------------------------------------------------------------------------
SENSORS = {
    "OV04C10":  dict(w=2688, h=1520, pitch_um=1.998, fps=60),
    "AR0234CS": dict(w=1920, h=1200, pitch_um=3.000, fps=60),
}

# ISP 输出链路 (PROJECT_TRACKER §0 变量 8 / §5.6)
CHAINS = [
    ("640x480@60",  640, 480,  60),
    ("1280x960@15", 1280, 960, 15),
]

# 结构侧光轴俯角上限 (ISS-051 / ISS-052): OV04C10 <=25deg, AR0234CS <=28deg
TILT_LIMIT = {"OV04C10": 25.0, "AR0234CS": 28.0}
TILT_PROBE = [25.0, 28.0, 32.0]   # 32deg = 原始结构区间上段 (已被否决, 仍列出做对照)

# ISP 吞吐口径 (两个互相矛盾的口径, 都要算)
ISP_MPS_SINGLE = 250.0    # PROJECT_TRACKER §3.1 "4K@30 单路 ~250 MP/s"  [官方口径·自相矛盾]
ISP_MPS_4K60 = 3840 * 2160 * 60 / 1e6   # 官网 "4K 60fps 实时处理" = 497.7 MP/s [官方]
SPHERE = 4.0 * math.pi                      # 全球立体角 12.566 sr


def sensor_geom(name: str) -> dict:
    s = SENSORS[name]
    w, h = s["w"], s["h"]
    pitch_mm = s["pitch_um"] / 1000.0
    diag_mm = math.hypot(w * pitch_mm, h * pitch_mm)
    # 等距: 半径与角度成正比 -> f = (半对角尺寸) / (对角半视场 rad)
    f_mm = (diag_mm / 2.0) / (HALF_DIAG * DEG)
    f_px = f_mm / pitch_mm
    return dict(name=name, w=w, h=h, pitch_mm=pitch_mm, diag_mm=diag_mm,
                f_mm=f_mm, f_px=f_px, fps=s["fps"])


def theta_of(g: dict, half_w_px: float, half_h_px: float) -> dict:
    """给定取图窗口 (半宽/半高 px), 返回角度量。"""
    th_w = half_w_px / g["f_px"]
    th_h = half_h_px / g["f_px"]
    th_d = math.hypot(half_w_px, half_h_px) / g["f_px"]
    return dict(th_w=th_w, th_h=th_h, th_d=th_d,
                h_half_deg=th_w / DEG, v_half_deg=th_h / DEG,
                diag_deg=2 * th_d / DEG)


def solid_angle_sr(g: dict, half_w_px: float, half_h_px: float, n=20000) -> float:
    """取图窗口覆盖的立体角 (sr), 等距投影下精确积分。

    像素矩形 (|x|<=hw, |y|<=hh) 在等距投影里映射到球面上的区域:
        theta_max(psi) = min(hw/|cos psi|, hh/|sin psi|) / f_px
    立体角 dOmega = sin(theta) dtheta dpsi  ->  Omega = Int (1 - cos theta_max(psi)) dpsi
    四象限对称 -> 4 * Int_0^{pi/2}
    """
    def omega(hw, hh):
        tot = 0.0
        dpsi = (math.pi / 2.0) / n
        for i in range(n):
            psi = (i + 0.5) * dpsi
            c, s = math.cos(psi), math.sin(psi)
            # 射线出框处: min(hw/c, hh/s)
            lim = hw / c if c > 1e-12 else float("inf")
            if s > 1e-12:
                lim = min(lim, hh / s)
            th = lim / g["f_px"]
            tot += (1.0 - math.cos(th)) * dpsi
        return 4.0 * tot

    return omega(half_w_px, half_h_px)


def solid_angle_fraction(g: dict, half_w_px: float, half_h_px: float) -> float:
    """占全视场立体角的比例 (全视场 = 1.0); 同时给出占整个球面的比例。"""
    return solid_angle_sr(g, half_w_px, half_h_px) / solid_angle_sr(g, g["w"] / 2.0, g["h"] / 2.0)


def fit_letterbox(src_w: int, src_h: int, dst_w: int, dst_h: int):
    """等比 letterbox: 缩放后居中, 不足处补黑边。返回 (scale, scene_w, scene_h, bar_x, bar_y)。"""
    s = min(dst_w / src_w, dst_h / src_h)
    sw = int(round(src_w * s))
    sh = int(round(src_h * s))
    if sw % 2:
        sw -= 1
    if sh % 2:
        sh -= 1
    return s, sw, sh, (dst_w - sw) // 2, (dst_h - sh) // 2


def chain_report(g: dict, name: str, dst_w: int, dst_h: int, fps: int) -> dict:
    """对一条 ISP 输出链路, 分别算 '整幅 scale(等比/非等比)' 与 'ROI(crop+scale)'。"""
    full = theta_of(g, g["w"] / 2.0, g["h"] / 2.0)

    # --- A. 整幅 scale · 等比 letterbox (推荐) ---
    s, sw, sh, bx, by = fit_letterbox(g["w"], g["h"], dst_w, dst_h)
    # 场景区在输出图里的角范围 = sensor 全幅 (等比, 未丢内容)
    aniso_lb = (full["h_half_deg"] / (sw / 2.0)) / (full["v_half_deg"] / (sh / 2.0))
    lb = dict(mode="letterbox", scale=s, scene_w=sw, scene_h=sh, bar_x=bx, bar_y=by,
              deg_h_per_px=full["h_half_deg"] / (sw / 2.0),
              deg_v_per_px=full["v_half_deg"] / (sh / 2.0),
              aniso=aniso_lb, fov=full)

    # --- B. 整幅 scale · 非等比拉伸 (不裁剪但变形) ---
    sx, sy = dst_w / g["w"], dst_h / g["h"]
    aniso_st = (full["h_half_deg"] / (dst_w / 2.0)) / (full["v_half_deg"] / (dst_h / 2.0))
    st = dict(mode="stretch", scale=sx, sy=sy, scene_w=dst_w, scene_h=dst_h, bar_x=0, bar_y=0,
              deg_h_per_px=full["h_half_deg"] / (dst_w / 2.0),
              deg_v_per_px=full["v_half_deg"] / (dst_h / 2.0),
              aniso=aniso_st, fov=full)

    # --- C. ROI (crop + scale) —— 禁止路线 ---
    roi_cw = min(g["w"], 1920)
    roi_ch = min(g["h"], 1080)
    # 居中裁剪窗口 (裁剪原点偏移属 [0数据], 不影响 FOV 损失量, 只影响主点)
    roi = theta_of(g, roi_cw / 2.0, roi_ch / 2.0)
    aniso_roi = (roi["h_half_deg"] / (dst_w / 2.0)) / (roi["v_half_deg"] / (dst_h / 2.0))
    rc = dict(mode="roi_crop", crop_w=roi_cw, crop_h=roi_ch, scene_w=dst_w, scene_h=dst_h,
              deg_h_per_px=roi["h_half_deg"] / (dst_w / 2.0),
              deg_v_per_px=roi["v_half_deg"] / (dst_h / 2.0),
              aniso=aniso_roi, fov=roi)

    return dict(chain=name, dst_w=dst_w, dst_h=dst_h, fps=fps,
                lb=lb, st=st, roi=rc,
                so_full=solid_angle_fraction(g, g["w"] / 2.0, g["h"] / 2.0),
                so_roi=solid_angle_fraction(g, roi_cw / 2.0, roi_ch / 2.0),
                so_full_sr=solid_angle_sr(g, g["w"] / 2.0, g["h"] / 2.0),
                so_roi_sr=solid_angle_sr(g, roi_cw / 2.0, roi_ch / 2.0))


def bandwidth(g: dict) -> dict:
    mp = g["w"] * g["h"] / 1e6
    mps = mp * g["fps"]
    gbps = g["w"] * g["h"] * g["fps"] * 10 / 1e9     # RAW10
    return dict(mp=mp, mps=mps, gbps=gbps,
                pct_250=100 * mps / ISP_MPS_SINGLE,
                pct_4k60=100 * mps / ISP_MPS_4K60)


def tilt_margin(v_half_deg: float, beta: float) -> float:
    """光轴俯角 beta 时, 正前方 (水平) 相对画面上边缘的余量。负数 = 掉出画面。"""
    return v_half_deg - beta


def main() -> int:
    tables = "--tables" in sys.argv
    print("=" * 100)
    print("[ISS-056] ISP 缩放路径 FOV 自检 — ROI(crop+scale) vs 整幅 scale")
    print(f"[ISS-056] 投影模型 = 等距 (r=f·theta) [决策文本]; 设计对角 FOV = {DIAG_FOV_DESIGN}° [决策文本]")
    print("=" * 100)

    failures = []

    for name in SENSORS:
        g = sensor_geom(name)
        print()
        print("#" * 100)
        print(f"### sensor = {name}  ({g['w']}x{g['h']}, 像元 {g['pitch_mm']*1000:.3f}um, 对角 {g['diag_mm']:.4f}mm)")
        print(f"    等距焦距 f = {g['f_mm']:.4f} mm   f_px = {g['f_px']:.2f} px   [推算: 由 对角120° 反算]")
        full = theta_of(g, g["w"] / 2.0, g["h"] / 2.0)
        print(f"    全幅对角 FOV = {full['diag_deg']:.2f}°   垂直半视场 = {full['v_half_deg']:.2f}°   水平半视场 = {full['h_half_deg']:.2f}°")
        bw = bandwidth(g)
        print(f"    带宽 RAW10@{g['fps']} = {bw['gbps']:.3f} Gbps   吞吐 = {bw['mps']:.1f} MP/s "
              f"({bw['pct_250']:.1f}% of 250MP/s 口径 | {bw['pct_4k60']:.1f}% of 4K60 官方口径)")
        print("-" * 100)
        print(f"    {'链路':<14} {'路线':<22} {'对角FOV':>9} {'垂直半':>8} {'水平半':>8} "
              f"{'水平°/px':>9} {'垂直°/px':>9} {'各向异性':>8} {'有效像素':>12}")
        for cname, dw, dh, fps in CHAINS:
            c = chain_report(g, cname, dw, dh, fps)
            for key, tag in (("lb", "整幅scale·等比letterbox"), ("st", "整幅scale·非等比拉伸"), ("roi", "ROI(crop+scale) 禁止")):
                m = c[key]
                print(f"    {cname:<14} {tag:<22} {m['fov']['diag_deg']:>8.2f}° {m['fov']['v_half_deg']:>7.2f}° "
                      f"{m['fov']['h_half_deg']:>7.2f}° {m['deg_h_per_px']:>9.4f} {m['deg_v_per_px']:>9.4f} "
                      f"{m['aniso']:>8.3f} {m['scene_w']}x{m['scene_h']:<6}")
            print(f"    {'':14} {'→ 立体角 (视场面积)':<22} 整幅scale: {c['so_full_sr']:.3f} sr "
                  f"({100*c['so_full']/SPHERE:.2f}% 球面)   "
                  f"ROI路线: {c['so_roi_sr']:.3f} sr ({100*c['so_roi']/SPHERE:.2f}% 球面)   "
                  f"→ 视场面积只剩 {100*c['so_roi']:.2f}%  (损失 {100*(1-c['so_roi']):.2f}%)")
            # 俯角余量
            for beta in TILT_PROBE:
                m_lb = tilt_margin(c['lb']['fov']['v_half_deg'], beta)
                m_roi = tilt_margin(c['roi']['fov']['v_half_deg'], beta)
                flag_lb = "OK" if m_lb >= 0 else "掉出画面"
                flag_roi = "OK" if m_roi >= 0 else "掉出画面"
                print(f"    {'':14}   俯角 {beta:>4.1f}°  余量: 整幅scale {m_lb:+6.2f}° [{flag_lb}]   "
                      f"ROI {m_roi:+6.2f}° [{flag_roi}]")
            print()

        # ---------------- 自检 ----------------
        if name == "OV04C10":
            if abs(full["diag_deg"] - 120.00) > 0.05:
                failures.append(f"A1 全幅对角 FOV {full['diag_deg']:.2f} != 120.00")
            roi_full = theta_of(g, 960, 540)
            if abs(roi_full["diag_deg"] - 85.61) > 0.05:
                failures.append(f"A2 ROI 对角 FOV {roi_full['diag_deg']:.2f} != 85.61")
            m25_lb = tilt_margin(full["v_half_deg"], 25.0)
            m25_roi = tilt_margin(roi_full["v_half_deg"], 25.0)
            if not (m25_lb > 0 and m25_roi < 0):
                failures.append(f"A4 俯角25° 余量 整幅 {m25_lb:+.2f} / ROI {m25_roi:+.2f} 不符合预期")
        if name == "AR0234CS":
            roi_full = theta_of(g, 960, 540)
            if abs(roi_full["diag_deg"] - 116.75) > 0.05:
                failures.append(f"A3 AR0234CS 裁高对角 FOV {roi_full['diag_deg']:.2f} != 116.75")
        # ---- per-sensor 自检 (A5/A6) ----
        c0 = chain_report(g, "640x480@60", 640, 480, 60)
        exp_stretch_aniso = {"OV04C10": 1.326, "AR0234CS": 1.200}[name]
        exp_roi_so = {"OV04C10": 0.523, "AR0234CS": 0.903}[name]
        if c0["lb"]["aniso"] > 1.01:
            failures.append(f"A5 {name} letterbox 各向异性 {c0['lb']['aniso']:.4f} > 1.01")
        if abs(c0["st"]["aniso"] - exp_stretch_aniso) > 0.005:
            failures.append(f"A5 {name} 拉伸各向异性 {c0['st']['aniso']:.4f} != {exp_stretch_aniso}")
        if abs(c0["so_roi"] - exp_roi_so) > 0.02:
            failures.append(f"A6 {name} ROI 立体角占比 {c0['so_roi']*100:.2f}% != ~{exp_roi_so*100:.0f}%")

    print("=" * 100)
    if failures:
        print("[自检] ❌ 失败:")
        for f in failures:
            print("   -", f)
        return 1
    print("[自检] ✅ A1~A6 全部通过 (rc=0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
