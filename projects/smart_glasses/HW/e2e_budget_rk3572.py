#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HW/e2e_budget_rk3572.py —— 端到端预算重算器 (主控 RK3572 + 显示 1920×1080)

★为什么要有这个脚本 (2026-11-02 01:30):
  老板在 40 分钟内连下两个决定 —— 主控换 **RK3572** (4 TOPS) + 显示件换 **0.49" 1920×1080 SiOLED**。
  这两条**都把端到端往坏的方向推**, 而且**叠加** ⇒ 必须有一个可复算的脚本把它们代进
  sw-lead 已验证的端到端模型 (SW/RKNN_BENCH.md §4), 而不是靠嘴算。

★模型来源 (全部来自 SW/RKNN_BENCH.md §4/§5, 该文已自证 21/21 + 9/9):
    T_od   = S5 + POST_MS                      # OD 完整耗时 = 纯 NPU + 后处理
    age    = ceil(T_od / FRAME_MS)             # 框龄台阶函数 (16.67ms 一档)
    模式A  = T_FIXED + T_od                    # 显示等 OD (老板 10-25 已授权的兜底)
    模式B  = T_FIXED + age × FRAME_MS          # 异步 60fps 显示
  ★模式A ≤60ms ⇒ S5 ≤ 20.33ms ; 模式B ≤60ms ⇒ age=1 ⇒ S5 ≤ 10.67ms (原文阈值)

★证据分级: [公开实测·第三方] RK3576 三档 NPU 耗时 (model_zoo 性能表)
            [推算] RK3572 的 NPU 耗时 = RK3576 × (6TOPS/4TOPS) —— ★**不保证等比** (4 TOPS 标称 sparse INT8)
            ★★[ISS-137 2026-11-10] 显示合成段已从 T_FIXED 里**单独拆出来打点** ⇒
              [模型占位] 显示合成段 = 4.00ms (S8 画框 1.0 + S9 显示TX 3.0, 出处 RKNN_BENCH §4.1)
              [0数据] ★**该段在 1920×1080 下的实测值 (t_compose)** ⇒ §⑤ 给的是【可测判据】不是【盲扫】

用法:
    python3 HW/e2e_budget_rk3572.py            # 主表
    python3 HW/e2e_budget_rk3572.py --selftest  # 自检 (复现 sw-lead 已发布数字)
    python3 HW/e2e_budget_rk3572.py --t-compose-ms 8.5   # ★代入板端实测的 t_compose 重算 (ISS-137)
"""
from __future__ import annotations

import math
import sys

# ── 模型常数 (来自 SW/RKNN_BENCH.md §4) ────────────────────────────────────
FRAME_MS = 16.67          # 60fps 帧周期
POST_MS = 5.6             # 后处理 (从 T_od=21~23 与 S5=15.38~17.39 反解, 一致)
T_FIXED = 34.00           # 曝光→OD 输入就绪 + 显示输出段 (从 模式A 54.98~56.99 反解)

# ★★ISS-137 (2026-11-10 23:5x) 把 T_FIXED 这个黑箱**拆成五段** ★★
# ★**为什么要拆**: 原来 T_FIXED 是 34.00 一个数 ⇒ 显示合成段占多少永远是 [0数据]
#   ⇒ §⑤ 只能做 0~60% 的盲扫 ⇒ ★**老板看不到"到底测哪个数才能定案"**。
# ★**拆完后**: 显示合成段有了 ①确定的占位值 ②**一个可测判据** ⇒ 板端打一个点就能定案。
# ★**出处**: RKNN_BENCH.md §4.1 的 S1~S10 明细 (曝光块 E+R+S3=24.67 · S8 画框 1.0 · S9 3.0 · S10 光机 5.0)
#   + DEMO_OD_TIMING_SPEC.md §3.3 (t_compose ↔ S9) + §3.2 阶段表 (第7段 = 合成/缩放)
T_PRE_EXPOSURE = 24.67    # ★曝光→OD 输入就绪 (E 8.3 + R 8.3 + S3 ISP含缩放 8.0) —— ★**不随显示分辨率变**
T_DRAW = 1.00             # ★画框 (S8) —— 在 NV12 的 Y 平面画 ⇒ 画的是**采集帧**(640×640) ⇒ ★**不随显示分辨率变**
T_COMPOSE = 3.00          # ★★显示合成/缩放 (S9) —— ★★**唯一随显示像素数变的段**★★
T_PANEL = 5.00            # ★光机逐帧延迟 (S10) —— ★**不随像素数变** (面板自身时序)
# ★T_FIXED 是从"模式A 54.98~56.99"反解出来的, 与 §4.1 明细 (24.67+1+3+5=33.67) 差 0.33 ⇒ 记为残差, 恒等成立
T_RESIDUAL = T_FIXED - (T_PRE_EXPOSURE + T_DRAW + T_COMPOSE + T_PANEL)   # = 0.33 反解余量

# ── [公开实测·第三方] RK3576 (6 TOPS) model_zoo 整链路 FPS ─────────────────
RK3576_S5 = {
    "yolov5s@640 (SiLU)": (17.39, 15.38),
    "yolov5s@640 (relu)": (15.38, 15.38),
    "yolov5n@640":        (8.87, 8.87),
    "yolov5s@320 (估)":   (5.00, 4.00),
}
RK3576_TOPS = 6
RK3572_TOPS = 4

# ── 显示输出规格 (11-02 01:12 老板换件) ───────────────────────────────────
DISPLAY_OLD = ("走鹃Ⅱ 800×600", 800 * 600)
DISPLAY_NEW = ("视涯 0.49\" 1920×1080", 1920 * 1080)

# ★ISS-137: 板端实测的 t_compose (ms); None = 还没实测 ⇒ 只给判据
_tc_override: float | None = None


def age(t_od: float) -> int:
    return math.ceil(t_od / FRAME_MS)


# ── ISS-137: 显示合成段 (t_compose) 的独立模型 ──────────────────────────────
# ★**为什么要把它抽成独立量**: 拆开之前 T_FIXED 是个 34.00 的黑箱
#   ⇒ "显示合成段占 T_FIXED 多少" 永远是 [0数据] ⇒ §⑤ 只能盲扫 0~60%
#   ⇒ ★**盲扫的毛病**: 它回答不了"板端到底要测出多少才算过" (⇒ 测完了还是不知道算不算过)
# ★**拆开之后**: t_compose 是一个**有名有姓的数** ⇒ 能反过来算【判据】(测出 ≤ 多少就过)
T_FIXED_OTHER = T_PRE_EXPOSURE + T_DRAW + T_PANEL + T_RESIDUAL   # 31.00 (与显示分辨率无关的部分)


def compose_upper_bound(px_ratio: float) -> float:
    """显示合成段随像素数线性放大的**上界** (硬件缩放器跑满也不降本)。"""
    return T_COMPOSE * px_ratio


def modeA_with_compose(s5: float, t_compose_ms: float) -> float:
    """给定 S5 与**实测/代入的 t_compose**, 算模式A 端到端。"""
    t_od = s5 + POST_MS
    return T_FIXED_OTHER + t_compose_ms + t_od


def compose_max_for(s5: float, budget_ms: float = 60.0) -> float:
    """★**可测判据**: 模式A 要 ≤ budget_ms, t_compose 最多能是多少 (ms)。"""
    return budget_ms - T_FIXED_OTHER - (s5 + POST_MS)


def e2e(s5: float) -> dict:
    """给一个纯 NPU 耗时, 算完整端到端账"""
    t_od = s5 + POST_MS
    a = age(t_od)
    return {
        "s5": s5,
        "t_od": t_od,
        "age": a,
        "modeA": T_FIXED + t_od,
        "modeB": T_FIXED + a * FRAME_MS,
    }


def scale(s5_3576: float, tops_from: int, tops_to: int) -> float:
    return s5_3576 * tops_from / tops_to


def show(title: str, rows: list[tuple], note: str = "") -> None:
    print(f"\n{'=' * 100}\n{title}\n{'=' * 100}")
    if note:
        print(note)
    hdr = (f"{'方案':<26}{'S5(ms)':>9}{'T_od':>8}{'age':>5}"
           f"{'模式A(ms)':>12}{'判定':>8}{'模式B(ms)':>12}{'判定':>8}")
    print(hdr)
    print("-" * 100)
    for row in rows:
        name, r = row[0], row[1]
        okA = "✅" if r["modeA"] <= 60 else "❌"
        okB = "✅" if r["modeB"] <= 60 else "❌"
        print(f"{name:<26}{r['s5']:>9.2f}{r['t_od']:>8.2f}{r['age']:>5}"
              f"{r['modeA']:>12.2f}{okA:>8}{r['modeB']:>12.2f}{okB:>8}")
        if len(row) > 2 and row[2]:
            print(f"{'':<26}└─ {row[2]}")


def selftest() -> int:
    """复现 sw-lead 已发布的数字 (SW/RKNN_BENCH.md §5.1/§5.2) —— 差 >0.6ms 判失败"""
    print("【自检】复现 sw-lead 已发布数字 (容差 0.6ms)")
    cases = [
        # (名, S5_hi, S5_lo, 发布模式A区间, 发布模式B)
        ("RK3576 yolov5s@640", 17.39, 15.38, (54.98, 56.99), 67.01),
        ("RK3576 yolov5n@640", 8.87, 8.87, None, 50.34),
    ]
    bad = 0
    for name, hi, lo, exp_a, exp_b in cases:
        r_hi, r_lo = e2e(hi), e2e(lo)
        if exp_a is not None:
            if abs(r_lo["modeA"] - exp_a[0]) > 0.6 or abs(r_hi["modeA"] - exp_a[1]) > 0.6:
                print(f"  ❌ {name}: 模式A 本脚本 {r_lo['modeA']:.2f}~{r_hi['modeA']:.2f} vs 已发布 {exp_a}")
                bad += 1
            else:
                print(f"  ✅ {name}: 模式A {r_lo['modeA']:.2f}~{r_hi['modeA']:.2f} (发布 {exp_a[0]}~{exp_a[1]})")
        if abs(r_hi["modeB"] - exp_b) > 0.6:
            print(f"  ❌ {name}: 模式B 本脚本 {r_hi['modeB']:.2f} vs 已发布 {exp_b}"); bad += 1
        else:
            print(f"  ✅ {name}: 模式B {r_hi['modeB']:.2f} (发布 {exp_b})")
    # T2 阈值反解: 模式A ≤60 ⇒ S5 ≤ 20.33 (原文)
    s5_thr = 60 - T_FIXED - POST_MS
    print(f"  {'✅' if abs(s5_thr - 20.33) < 0.6 else '❌'} 模式A 阈值 S5 ≤ {s5_thr:.2f} (原文 20.33)")

    # ★★ISS-137 新增回归护栏 (★下面每一条都是"判据退化"会被抓住的反向用例★)
    print("【自检】ISS-137 拆分护栏")
    # ① 拆分必须恒等还原 T_FIXED (★拆错 ⇒ 全部已发布数字都偏了★)
    tot = T_PRE_EXPOSURE + T_DRAW + T_COMPOSE + T_PANEL + T_RESIDUAL
    ok = abs(tot - T_FIXED) < 1e-9
    print(f"  {'✅' if ok else '❌'} 拆分恒等: {T_PRE_EXPOSURE}+{T_DRAW}+{T_COMPOSE}+{T_PANEL}+{T_RESIDUAL} = {tot:.2f} == T_FIXED {T_FIXED:.2f}")
    bad += 0 if ok else 1
    # ② compose_max_for 与 modeA_with_compose 必须互为逆运算 (★判据与算账对不上 ⇒ 板端测出来也判不了★)
    for s5v in (10.0, 17.39, 26.085, 13.305):
        mx = compose_max_for(s5v)
        ok = abs(modeA_with_compose(s5v, mx) - 60.0) < 1e-9
        print(f"  {'✅' if ok else '❌'} 判据↔算账互逆 @S5={s5v}: t_compose 上限 {mx:.3f} ⇒ 模式A {modeA_with_compose(s5v, mx):.6f}")
        bad += 0 if ok else 1
    # ③ t_compose=0 时必须退化成旧模型 (T_FIXED 全量) ⇒ 证明"其他部分 = T_FIXED - T_COMPOSE" 没错
    #    (★这【不是】旧模型: 旧模型把整段显示合成都算进 T_FIXED ⇒ 新模型是【扣掉合成段再加实测值】★)
    s5v = 13.305
    ok = abs(modeA_with_compose(s5v, T_COMPOSE) - e2e(s5v)["modeA"]) < 1e-9
    print(f"  {'✅' if ok else '❌'} 代入 T_COMPOSE 本身 ⇒ 与旧模型逐位一致 "
          f"({modeA_with_compose(s5v, T_COMPOSE):.4f} vs {e2e(s5v)['modeA']:.4f}) ⇒ ★拆分无副作用★")
    bad += 0 if ok else 1
    # ④ 线性上界必须严格大于 t_compose 上限 才需要"实测" (★若二者顺序反了 ⇒ 判据无意义★)
    ub = compose_upper_bound(DISPLAY_NEW[1] / DISPLAY_OLD[1])
    ok = ub > compose_max_for(s5v)
    print(f"  {'✅' if ok else '❌'} 线性上界 {ub:.2f} > yolov5n 判据 {compose_max_for(s5v):.2f} ⇒ ★真需要实测才判得了★")
    bad += 0 if ok else 1

    print(f"\n{'✅ 自检通过' if bad == 0 else f'❌ 自检失败 {bad} 项'}")
    return 0 if bad == 0 else 1


def main() -> int:
    global _tc_override
    if "--selftest" in sys.argv:
        return selftest()
    # ★ISS-137: 代入板端实测的 t_compose (ms) ⇒ 一行命令出结论
    if "--t-compose-ms" in sys.argv:
        try:
            _tc_override = float(sys.argv[sys.argv.index("--t-compose-ms") + 1])
        except (IndexError, ValueError):
            print("❌ --t-compose-ms 需要一个数值 (ms)")
            return 2

    print(__doc__.split("用法:")[0])

    # ── 1. 基线复现 (RK3576) ────────────────────────────────────────────────
    show("① 基线: RK3576 (6 TOPS) —— sw-lead 已发布, 供对照",
         [(f"{k}", e2e(v[0])) for k, v in RK3576_S5.items()],
         "★这四行是**已经验证过的锚点** (RKNN_BENCH §5.1/§5.2) ⇒ 下面所有 RK3572 结论都相对它们成立")

    # ── 2. RK3572 (4 TOPS) ─────────────────────────────────────────────────
    rows = []
    for k, (hi, lo) in RK3576_S5.items():
        s5_hi = scale(hi, RK3576_TOPS, RK3572_TOPS)
        s5_lo = scale(lo, RK3576_TOPS, RK3572_TOPS)
        r_hi = e2e(s5_hi)
        r_lo = e2e(s5_lo)
        rows.append((k, {"s5": (s5_hi + s5_lo) / 2,
                         "t_od": (r_hi["t_od"] + r_lo["t_od"]) / 2,
                         "age": r_hi["age"],
                         "modeA": (r_hi["modeA"] + r_lo["modeA"]) / 2,
                         "modeB": r_hi["modeB"]}))
    show("② RK3572 (4 TOPS) —— ★老板 11-02 01:00 拍板的新基线",
         rows,
         "★S5 = RK3576 × (6/4) [推算] —— ★**不保证等比** (4 TOPS 标称是 sparse INT8)\n"
         "★而且 RK3576 的 17.39ms 本身是**整链路 FPS = 纯 NPU 上界** ⇒ 本节数字是**保守上界**, 真实值可能更好 ⇒ **必须板端实测 (ISS-129)**")

    # ── 3. T2 判定 ────────────────────────────────────────────────────────
    s5_3572_yolov5s = scale(17.39, RK3576_TOPS, RK3572_TOPS)
    print(f"\n{'=' * 100}\n③ T2 翻案条件判定 (老板 10-29 自己定的: 纯 NPU S5 > 20.33ms ⇒ 60ms 不保)\n{'=' * 100}")
    print(f"  RK3572 + yolov5s@640 推算 S5 = {s5_3572_yolov5s:.2f} ms  vs 阈值 20.33 ms"
          f"  ⇒  {'★命中 T2 (推算)' if s5_3572_yolov5s > 20.33 else '未命中'}")
    print(f"  ⇒ 但 T2 的**实测**必须用 RK3572 板端跑 (ISS-129) —— 因为上面是 TOPS 等比换算, 不是实测")

    # ── 4. 出路表 ──────────────────────────────────────────────────────────
    print(f"\n{'=' * 100}\n④ 出路: 要在 RK3572 上保住 60ms, 只有三条\n{'=' * 100}")
    out = []
    s5n = scale(8.87, RK3576_TOPS, RK3572_TOPS)
    r = e2e(s5n)
    out.append(("换 yolov5n@640", r,
                 f"模式A ✅ 但 模式B ❌ (age 仍=2, 差 {r['t_od'] - FRAME_MS:.2f}ms 就掉到 age=1)"))
    s5_320 = scale(5.00, RK3576_TOPS, RK3572_TOPS)
    s5_320_lo = scale(4.00, RK3576_TOPS, RK3572_TOPS)
    r2 = e2e((s5_320 + s5_320_lo) / 2)
    out.append(("换 yolov5s@320 (改锁死变量)", r2,
                 "★**两个模式都 ✅** ⇒ 但改锁死表 §0 #8「OD 640×480」⇒ 需老板拍板"))
    s5_3576_yolov5s = e2e(17.39)
    out.append(("★回到 RK3576 (6 TOPS)", s5_3576_yolov5s,
                 "★但 RK3576 在 30mm 板宽内只剩 122.3mm² 余量 (面积账) ⇒ 除非放宽板宽或 PCB 厂确认 6 层可塞"))
    show("④ 出路对比 (RK3572 平台)", out)

    # ── 5. 1920×1080 显示的叠加影响 (★ISS-137: 已把显示合成段拆出来 ⇒ 给【可测判据】) ──
    print(f"\n{'=' * 100}\n⑤ ★显示件换 1920×1080 的叠加影响 (★ISS-137: 显示合成段已拆成独立量 ⇒ 不再盲扫)\n{'=' * 100}")
    px_old = DISPLAY_OLD[1]
    px_new = DISPLAY_NEW[1]
    ratio = px_new / px_old
    print(f"  显示输出像素: {DISPLAY_OLD[0]} = {px_old/1e6:.2f} Mpx → {DISPLAY_NEW[0]} = {px_new/1e6:.2f} Mpx  (×{ratio:.2f})")
    print(f"\n  ★**T_FIXED = {T_FIXED:.2f} 的拆分 (★出处 RKNN_BENCH §4.1 的 S1~S10 明细★)**")
    print(f"    {'T_PRE_EXPOSURE (曝光→OD输入就绪)':<38} = {T_PRE_EXPOSURE:>6.2f} ms   ★**不随显示分辨率变**")
    print(f"    {'T_DRAW (画框 S8)':<38} = {T_DRAW:>6.2f} ms   ★**不随显示分辨率变** (画的是采集帧 640×640)")
    print(f"    {'T_COMPOSE (显示合成/缩放 S9)':<38} = {T_COMPOSE:>6.2f} ms   ★★**随显示像素数变 ★★")
    print(f"    {'T_PANEL (光机逐帧延迟 S10)':<38} = {T_PANEL:>6.2f} ms   ★**不随像素数变** (面板自身时序)")
    print(f"    {'T_RESIDUAL (反解余量)':<38} = {T_RESIDUAL:>6.2f} ms")
    print(f"    {'合计 (= T_FIXED, 恒等)':<38} = {T_PRE_EXPOSURE+T_DRAW+T_COMPOSE+T_PANEL+T_RESIDUAL:>6.2f} ms")
    print(f"\n  ★★**可测判据 (★这才是本节要的东西★)**: 模式A ≤ 60ms ⇒ **t_compose 最多能是多少**")
    print(f"    {'方案':<26}{'S5(ms)':>9}{'t_compose 上限':>16}{'线性上界@4.32x':>17}{'判定':>10}")
    print("    " + "-" * 80)
    cand5 = [
        ("RK3572 + yolov5s@640", scale(17.39, RK3576_TOPS, RK3572_TOPS)),
        ("RK3572 + yolov5n@640", s5n),
        ("RK3572 + yolov5s@320", (scale(5.00, RK3576_TOPS, RK3572_TOPS) + scale(4.00, RK3576_TOPS, RK3572_TOPS)) / 2),
    ]
    upper = compose_upper_bound(ratio)
    for name, s5v in cand5:
        mx = compose_max_for(s5v)
        print(f"    {name:<26}{s5v:>9.2f}{mx:>16.2f}{upper:>17.2f}{'✅ 过' if mx >= upper else '❌ 不过':>10}")
    print(f"\n  ★**读法 (★这是 ISS-137 的交付物★)**:")
    print(f"    · 【线性上界】= {T_COMPOSE:.2f}ms × {ratio:.2f} = {upper:.2f}ms ⇒ ★**假设显示段完全随像素数等比放大**")
    print(f"      (硬件缩放器跑满也不降本) ⇒ 这是**悲观上界**, 不是预测")
    print(f"    · 【t_compose 上限】= ★**板端该测出 ≤ 多少才算过** ⇒ ★这才是打点的意义")
    print(f"    · ★**两者一比, 立刻知道[这个方案还剩多少空间]**: 若 上限 < 线性上界 ⇒ 该方案在[最坏情况]也不过线")
    if _tc_override is not None:
        print(f"\n  ★★**代入实测 t_compose = {_tc_override:.2f} ms 的重算 (★板端打点后直接用这个★)**")
        for name, s5v in cand5:
            ma = modeA_with_compose(s5v, _tc_override)
            print(f"    {name:<26} 模式A = {ma:>7.2f} ms  {'✅ 过' if ma <= 60 else '❌ 不过'}")
    else:
        print(f"\n  ★**还没实测 ⇒ 上面的[上限]就是判据本身** ⇒ ★板端打一个点 (t_compose@1920×1080)")
        print(f"    ⇒ 代入: `python3 HW/e2e_budget_rk3572.py --t-compose-ms <实测值>` ⇒ ★**一行命令出结论**")
    print(f"  ★**两条决定是叠加的**: 主控 RK3572 (NPU ×1.5) 与 显示 1920×1080 (合成 ×{ratio:.2f}) **都往同一个方向推**")
    print(f"  ★**结论不变**: 换 yolov5n 只救得回模式A, 且**余量极薄** (显示段只要占 T_FIXED 的 15% 以上, 模式A 就重新破线)")
    print(f"  ★★**但现在这个结论【可判了】**: 不再是\"显示段占多少是 [0数据]\" ⇒ ★**变成\"t_compose 测出 ≤ {compose_max_for(s5n):.2f}ms\"**")

    # ── 6. DSI 带宽 ────────────────────────────────────────────────────────
    print(f"\n{'=' * 100}\n⑥ DSI 带宽核对 (1920×1080 显示输出)\n{'=' * 100}")
    for fps in (25, 60, 90):
        payload = 1920 * 1080 * 24 * fps / 1e6      # RGB888 8bpc
        print(f"  {fps:>3} fps: RGB888 payload = {payload:>7.1f} Mbps  | 4-lane D-PHY@2.0Gbps 够? "
              f"{'✅' if payload < 4*2000*0.8 else '❌'}  (假设 2.0Gbps/lane, 按 80% 效率留余量)")
    print(f"  ★ 对照: 走鹃Ⅱ 800×600@25fps 只要 288 Mbps ⇒ 新屏是 ×4.32")
    print(f"  ★ 60fps 有余量, 但 **90fps 只剩不到 2× 余量** ⇒ ★**若要 90fps ⇒ 面板 DSC 必须开, 且 RK3572 的 DSI 支不支持 DSC 尚未核实** (新问题)")

    print(f"\n{'=' * 100}\n⑦ 结论 (一句话)\n{'=' * 100}")
    print(f"  ★ RK3572 + yolov5s@640 ⇒ 模式A {e2e(scale(15.38,6,4))['modeA']:.1f}~{e2e(scale(17.39,6,4))['modeA']:.1f}ms ❌ / 模式B 67.3ms ❌")
    print(f"    ⇒ ★**RK3572 把唯一达标的模式 (模式A) 也打掉了** ⇒ 60ms 在 RK3572 + yolov5s 上不成立")
    print(f"  ★ 两条决定叠加 (NPU ×1.5 + 显示合成 ×4.3) ⇒ 60ms 余量归零")
    print(f"  ★ 出路按代价排: ①yolov5s@320 (双模式达标, 但改锁死变量 #8) ②yolov5n@640 (只救模式A, 精度要重评)")
    print(f"    ③回到 RK3576 (但面积装不下) ④实测出真数再看 (ISS-129) —— ★**推算不能签字**")
    print(f"  ★ ★**但是**: 上面所有 RK3572 数字都是 **TOPS 等比换算** ⇒ 而 RK3576 那 17.39ms 本身是**整链路上界**")
    print(f"    ⇒ 真值可能比这好 ⇒ ★**第一件事是买板实测 (ISS-129), 不是继续推算**")
    return 0


if __name__ == "__main__":
    sys.exit(main())
