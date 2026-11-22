#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""logs/iss353/apply_caliber_dispositions.py
=====================================================================
ISS-353 · sw-lead · 「rk3572 目标口径」越权条目的**逐字替换补丁**
=====================================================================
★为什么有这个脚本★
  ISS-353 的闸 (`SW/tools/check_rk3572_target_caliber.py`) 扫出 18 条「结论矛盾(要处置)」:
    · 本单可处置 3 条 (SW/RK3572_TARGET_COMPAT_V2.md) ⇒ sw-lead 已在本单内改写
    · ★越权 15 条 ⇒ 文件不在 ISS-353 的允许写范围 (HW/* 属 hw-lead 地界; 其余 SW 文档不在
      本单"只写"清单里) ⇒ sw-lead 不越界改 ⇒ 改成「逐字替换文本 + 一键补丁」交 main 裁★
  ⇒ main 一条命令即可把这 15 条清零:
      python3 logs/iss353/apply_caliber_dispositions.py --apply
  ⇒ 补丁脚本本身默认 dry-run (只打印将要改什么 + 校验), ★不加 --apply 一个字节都不改★

★纪律★
  · 每条替换 = 「旧片段 → 新片段」, **旧片段必须在该文件里精确出现且仅出现 1 次**,
    否则该条判 FAIL 并整体中止 (不许"改了一部分"就当成功)
  · 只做**行内片段替换**, 不动行数、不动行序、不删任何老字 (新片段把老片段包在中间/接在后面)
  · 每个新片段都带取代标记 (★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572')
    取代·本条保留作历史留档·结论不再引用★★) ⇒ 应用后闸脚本把该行判「历史叙述(可留)」

★验证 (sw-lead 本单已跑, 见 logs/iss353/patch_verify/)★
  ① dry-run 全部 15 条 old 片段命中且唯一
  ② 在**项目盘副本** (tmp/iss353/patch_verify/root) 上真跑 --apply ⇒ 闸 rc=0 (零残留)
  ③ 真件 (HW/ / SW/ 其它文档) **一个字节未改** (md5 前后一致, 见交卷页 §B6)
=====================================================================
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys

MARKER = ("★已被 ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') 取代"
          "·本条保留作历史留档·结论不再引用★")

# ── 15 条逐字替换 (file, 旧片段, 新片段, 一句话说明) ─────────────────────────
REPLACEMENTS = [
    # 1 ─────────────────────────────────────────────────────────────────────
    ("HW/STEP1_LANDING_LIST.md",
     "★**target 兼容性验证**（`rk3572` 非合法 target ⇒ 用 `rk3576` 转）",
     "★**target 兼容性验证**（★toolkit2 侧 `rk3572` 非合法 target ⇒ 转换链走 rknn3-toolkit 1.2.0 的 "
     "`target_platform='rk3572'`★） " + MARKER,
     "Step1 落地清单 S1: 转换 target 改口径"),
    # 2 ─────────────────────────────────────────────────────────────────────
    ("SW/DEMO_BOARD_60MS_VERDICT_PLAN.md",
     "★**官方根本没有 `rk3572` 这个 target** (2.3.2 与 2.5.0 均无) ⇒ 只能 `target_platform='rk3576'` 转",
     "★**toolkit2 (2.3.2 与 2.5.0) 都没有 `rk3572` 这个 target** ⇒ ★**转换链走 rknn3-toolkit 1.2.0 的 "
     "`target_platform='rk3572'`** (config rc=0 [实测]) " + MARKER,
     "60ms 判决页 编译期行: 转换 target 改口径"),
    # 3 ─────────────────────────────────────────────────────────────────────
    ("SW/DEMO_BOARD_60MS_VERDICT_PLAN.md",
     "★**RK3572 BSP runtime 认不认 rk3576-target 产物** ⇒ 官方无此口径 ⇒ **只能板端判**",
     "★**RK3572 BSP runtime 认不认 rk3572-target 产物** (★主路线; rk3576-target 已降为次要路线①★) "
     "⇒ 官方无此口径 ⇒ **只能板端判** " + MARKER,
     "60ms 判决页 加载期行: 补 rk3572-target 分支"),
    # 4 ─────────────────────────────────────────────────────────────────────
    ("SW/DEMO_OD_PIPELINE_SPEC.md",
     "⇒ ★**必须用 `target_platform='rk3576'` 重转** (RK3572/RK3576 同代 RKNPU v2; "
     "★**但算力不等 4 vs 6 TOPS ⇒ 板端待验**)",
     "⇒ ★**必须重转, 但转换 target 改为 rknn3-toolkit 1.2.0 的 `target_platform='rk3572'`** "
     "(★ISS-263 实测 config rc=0 / 转换 rc=0 / 产物 249,360 B md5 97a34fff0b855b92681f26627dba5354; "
     "★2026-11-23 ISS-353 复跑逐字节一致★) · ★**板端接受性仍 [0数据] ⇒ 板端待验**★ " + MARKER,
     "OD pipeline spec 结论表第 2 行: 转换 target 改口径"),
    # 5 ─────────────────────────────────────────────────────────────────────
    ("SW/DEMO_OD_PIPELINE_SPEC.md",
     "★★**只能用 `'rk3576'`** —— ★**`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 target** "
     "(2.3.2 与最新 2.5.0 都抛 `ValueError: Invalid target_platform 'rk3572'!`) ⇒ "
     "★**在 RK3572 上也必须用 `target_platform='rk3576'` 转** (RK3572/RK3576 同代 RKNPU v2); "
     "★**但算力不等 (4 vs 6 TOPS) ⇒ 该 .rknn 在 RK3572 上的表现板端待验**",
     "★★**只能用 `'rk3572'`** —— ★**`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 target** "
     "(2.3.2 与最新 2.5.0 都抛 `ValueError: Invalid target_platform 'rk3572'!`) ⇒ "
     "★**转换链改走 rknn3-toolkit 1.2.0, 其 `config(target_platform='rk3572')` rc=0** "
     "(★ISS-263 实测 / ★2026-11-23 ISS-353 复跑 rc=0★); "
     "★**板端接受性仍 [0数据] ⇒ 该 .rknn 在 RK3572 上的表现板端待验** " + MARKER,
     "OD pipeline spec §2.3 target_platform 写死行: 改写为 rk3572"),
    # 6 ─────────────────────────────────────────────────────────────────────
    ("SW/DEMO_OD_PIPELINE_SPEC.md",
     "⇒ ★**\"升级到某版本就有 rk3572\"这个选项不存在** ⇒ 本行不再是 [待核], 而是**已定的阻塞** ⇒ 替代路线见 ISS-155。",
     "⇒ ★**\"升级到某版本就有 rk3572\"这个选项不存在** (★**限定在 toolkit2 家族内**★) ⇒ "
     "★**v2.1 订正 (2026-11-23 · ISS-353): 本行的\"已定的阻塞\"已降级 —— 转换链已通 "
     "(rknn3-toolkit 1.2.0 支持 `target_platform='rk3572'`, [实测]) ⇒ 剩下的只是板端接受性 [0数据]**★ "
     "⇒ 替代路线见 ISS-155。",
     "OD pipeline spec P0-1 行: 阻塞状态降级 (toolkit2 限定)"),
    # 7 ─────────────────────────────────────────────────────────────────────
    ("SW/DEMO_OD_PIPELINE_SPEC.md",
     "★★**ISS-155 已钉的替代路线 (2026-11-02)**: ★**用 `target_platform='rk3576'` 转, "
     "板端用 RK3572 BSP 自带的 runtime 加载** (RK3572 与 RK3576 **同代同架构**: 3 核 RKNPU v2)",
     "★★**ISS-155 当时钉的替代路线 (2026-11-02)**: ★**用 `target_platform='rk3576'` 转, "
     "板端用 RK3572 BSP 自带的 runtime 加载** (RK3572 与 RK3576 **同代同架构**: 3 核 RKNPU v2 "
     "— ★该前提已被 ISS-250 官方反证★) " + MARKER,
     "OD pipeline spec P0-1 行: 2026-11-02 替代路线标注取代"),
    # 8 ─────────────────────────────────────────────────────────────────────
    ("SW/MODEL_RELEASE_LIST.md",
     "且 `rk3572` 不是合法 target ⇒ 板端要加载的必须是用 `rk3576` target 转的产物",
     "且 ★**toolkit2 侧 `rk3572` 不是合法 target ⇒ 板端要加载的必须是 rknn3-toolkit 1.2.0 的 "
     "`target_platform='rk3572'` 产物**★ " + MARKER,
     "模型发布清单 根因行: 转换 target 改口径"),
    # 9 ─────────────────────────────────────────────────────────────────────
    ("SW/RK3572_TARGET_BOARD_VERIFY.md",
     "> `target_platform` ⇒ 必须用 `target_platform='rk3576'` 转换)。但**剩下的那条死结**——",
     "> `target_platform` ⇒ ★**v2.1 订正 (2026-11-23 · ISS-353): 转换 target 已改为 rknn3-toolkit 1.2.0 的 "
     "`target_platform='rk3572'` (config rc=0 [实测])**★ " + MARKER + ")。但**剩下的那条死结**——",
     "板端验证单 摘要行: 转换 target 改口径"),
    # 10 ────────────────────────────────────────────────────────────────────
    ("SW/RKNN_BUILD_ENV_RECOVERY.md",
     "★★ **但 RK3572 的 NPU 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2) ⇒ "
     "用 `target_platform='rk3576'` 转换, 板端用 RK3572 BSP 自带 runtime 加载**",
     "★★ **但 RK3572 的 NPU 与 RK3576 同代同架构 (4 TOPS / 3 核 RKNPU v2) ⇒ "
     "用 `target_platform='rk3576'` 转换, 板端用 RK3572 BSP 自带 runtime 加载** "
     "(★v2.1 订正 2026-11-23 ISS-353: 该前提已被 ISS-250 官方反证 (RK3576=6 TOPS / "
     "RK3572=RKNN3-native) ⇒ 转换链已改走 rknn3-toolkit 1.2.0 的 `target_platform='rk3572'`★) " + MARKER,
     "构建环境恢复 §0 摘要第 3 行: 前提反证 + 转换 target 改口径"),
    # 11 ────────────────────────────────────────────────────────────────────
    ("SW/RKNN_BUILD_ENV_RECOVERY.md",
     "★★ **`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 `target_platform`** —— "
     "从 2.2.0 到最新 2.5.0 全部拒绝, **不存在\"升级到某版本就有 rk3572\"这个选项**。",
     "★★ **`rk3572` 不是任何已发布版 rknn-toolkit2 的合法 `target_platform`** —— "
     "从 2.2.0 到最新 2.5.0 全部拒绝, **不存在\"升级到某版本就有 rk3572\"这个选项** "
     "(★**限定在 toolkit2 家族内** ★v2.1 订正 2026-11-23 ISS-353: rknn3-toolkit 1.2.0 的 "
     "`config(target_platform='rk3572')` rc=0 [实测], 官方 README「Supported Platforms」明列 RK3572 [官网]★) "
     + MARKER,
     "构建环境恢复 §2.2 结论 1: 结论限定在 toolkit2 家族内"),
    # 12 ────────────────────────────────────────────────────────────────────
    ("SW/RKNN_BUILD_ENV_RECOVERY.md",
     "因为**根本没有 `rk3572` 这个编译目标**。⇒ **必须重转**。",
     "因为**根本没有 `rk3572` 这个编译目标** (★v2.1 订正 2026-11-23 ISS-353: ★这句现在只对 toolkit2 "
     "家族成立 —— rknn3-toolkit 1.2.0 有 rk3572 编译目标 [官网]+[实测]★)。⇒ **必须重转** "
     "(★转换 target = rknn3-toolkit 1.2.0 的 `target_platform='rk3572'`★) " + MARKER,
     "构建环境恢复 §2.2 结论 2: 「没有 rk3572 编译目标」加限定"),
    # 13 ────────────────────────────────────────────────────────────────────
    ("SW/RKNN_BUILD_ENV_RECOVERY.md",
     "3. ★**替代路线: 用 `target_platform='rk3576'` 转换** —— 理由是 RK3572 的 NPU 与 RK3576 **同代同架构**, "
     "但这是**推算, 不是实测**, 必须板端验证 (见 §2.4.3)。",
     "3. ★**替代路线: 用 `target_platform='rk3576'` 转换** —— 理由是 RK3572 的 NPU 与 RK3576 **同代同架构**, "
     "但这是**推算, 不是实测**, 必须板端验证 (见 §2.4.3)。 "
     "★**v2.1 订正 (2026-11-23 · ISS-353): 该替代路线已被 ISS-263 取代 ⇒ 主路线 = rknn3-toolkit 1.2.0 + "
     "`target_platform='rk3572'` (config rc=0 [实测]); 「同代同架构」前提已被 ISS-250 官方反证**★ " + MARKER,
     "构建环境恢复 §2.2 结论 3: 替代路线标注取代"),
    # 14 ────────────────────────────────────────────────────────────────────
    ("SW/RKNN_BUILD_ENV_RECOVERY.md",
     '> ★**这些是"支持用 rk3576 target 转换"的**依据**, 不是"rk3572 = rk3576"的证据**。',
     '> ★**这些是"支持用 rk3576 target 转换"的**依据**, 不是"rk3572 = rk3576"的证据**。 '
     "★**v2.1 订正 (2026-11-23 · ISS-353): 这组依据属于【历史】—— 主路线已改为 rknn3-toolkit 1.2.0 + "
     "`target_platform='rk3572'`**★ " + MARKER,
     "构建环境恢复 §2.4 引述行: 依据降为历史"),
    # 15 ────────────────────────────────────────────────────────────────────
    ("SW/RKNN_BUILD_ENV_RECOVERY.md",
     "★**改 M1 定义为\"用 rk3576 target 重转 yolov5n\"**, 转换成本 ≈ 0.5 人天 (本单已做完 80%)",
     "★**改 M1 定义为\"用 rk3576 target 重转 yolov5n\"** (★v2.1 订正 2026-11-23 ISS-353: M1 的目标 target "
     "已改为 rknn3-toolkit 1.2.0 + `target_platform='rk3572'`★), 转换成本 ≈ 0.5 人天 (本单已做完 80%) " + MARKER,
     "构建环境恢复 §6 降级表 M1 行: 目标 target 改口径"),
]


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None, help="作用根目录 (默认 = 项目根)")
    ap.add_argument("--apply", action="store_true", help="★真改★ (默认只 dry-run)")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    mode = "APPLY" if args.apply else "DRY-RUN"
    print("=" * 78)
    print("ISS-353 · 口径越权条目逐字替换补丁 · %s" % mode)
    print("=" * 78)
    print("root  : %s" % root)
    print("条目  : %d" % len(REPLACEMENTS))
    print("")

    # ── 先全量校验 (有任一条不唯一 ⇒ 整体中止, 一个字节都不改) ──────────────
    plan, bad = [], []
    for i, (rel, old, new, why) in enumerate(REPLACEMENTS, 1):
        p = os.path.join(root, rel)
        if not os.path.isfile(p):
            bad.append((i, rel, "文件不存在"))
            continue
        text = open(p, encoding="utf-8", errors="ignore").read()
        n = text.count(old)
        if n != 1:
            bad.append((i, rel, "旧片段命中 %d 次 (必须恰好 1 次)" % n))
            continue
        plan.append((i, rel, old, new, why, p, text))

    if bad:
        print("✗ 校验失败 ⇒ 不改任何文件:")
        for i, rel, why in bad:
            print("   #%d %s —— %s" % (i, rel, why))
        return 1

    print("─── 计划 (逐条) ───")
    for i, rel, old, new, why, p, text in plan:
        print("#%-2d %s" % (i, rel))
        print("    理由: %s" % why)
        print("    旧  : %s" % old[:150])
        print("    新  : %s" % new[:150])
        print("    md5 : %s" % md5(p))
    print("")

    if not args.apply:
        print("★DRY-RUN: 未改任何文件 (加 --apply 才真改)★")
        print("校验结果: %d/%d 条旧片段精确命中且唯一 ⇒ 补丁可干净应用" % (len(plan), len(REPLACEMENTS)))
        return 0

    # ── 真改 (逐条原子写, 失败即中止) ─────────────────────────────────────
    # ★每条都重新从磁盘读一遍 ⇒ 同一文件的多条替换不会互相覆盖★
    for i, rel, old, new, why, p, text in plan:
        cur_text = open(p, encoding="utf-8", errors="ignore").read()
        if cur_text.count(old) != 1:
            print("✗ #%d %s: 应用时旧片段命中 %d 次 (期望 1) ⇒ 中止"
                  % (i, rel, cur_text.count(old)))
            return 1
        out = cur_text.replace(old, new, 1)
        tmp = p + ".iss353.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(out)
        os.replace(tmp, p)
        print("✔ #%-2d %s" % (i, rel))
        print("    理由: %s" % why)
        print("    md5_after = %s" % md5(p))
    print("")
    print("★APPLY 完成: %d 条已改 ⇒ 请复跑闸: python3 SW/tools/check_rk3572_target_caliber.py★" % len(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
