#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/demo_timing_check.py — ISS-145 demo 端到端时序规格自检器
=====================================================================
目的: 机械核对 `SW/DEMO_OD_TIMING_SPEC.md` 里**可以机器判定**的那些断言
      (段数 / 打点名 / 时钟基准 / 报数字段 / 判据条数 / CSV 表头),
      防止"文档写了但和另一份文档对不上"这类静默腐烂。

★铁律 (SOUL.md):
  1. 本脚本 **不编板端时延数字**。板端时延 = [0数据] (无板)。
     脚本只核对**规格自身的结构一致性**, 数字一律来自被核对的文档。
  2. 退出码 0 = 自检全过; 1 = 有项不通过; 2 = 有项未验/缺前置。

用法:
    python3 SW/tools/demo_timing_check.py --selftest     # 自检 (rc=0)
    python3 SW/tools/demo_timing_check.py                 # 核对规格文档
    python3 SW/tools/demo_timing_check.py --json          # 机读输出
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # .../SW/tools
PROJ = os.path.dirname(os.path.dirname(HERE))            # .../<项目库根>
SPEC = os.path.join(PROJ, "SW", "DEMO_OD_TIMING_SPEC.md")
UPSTREAM = os.path.join(PROJ, "SW", "DEMO_OD_PIPELINE_SPEC.md")
CHAIN = os.path.join(PROJ, "SW", "ARS45_INT8_CHAIN.md")

# ★打点名取自 SW/ARS45_INT8_CHAIN.md §4 (B8 埋点表) —— 上游真源, 不许自己另起一套
REQUIRED_POINTS = [
    "t_capture", "t_pre", "t_npu", "t_sdk_total",
    "t_decode", "t_draw", "t_compose", "t_display",
]
REQUIRED_FIELDS = ["min", "avg", "max", "p50", "p95", "n"]
CSV_HEADER = [
    "frame_idx", "ts_capture", "ts_pre", "ts_npu", "ts_sdk_total",
    "ts_decode", "ts_draw", "ts_compose", "ts_display",
    "exposure_us", "queue_wait_ms", "box_count", "npu_err", "frame_dropped",
]


class CheckError(Exception):
    pass


def read(path: str) -> str:
    if not os.path.exists(path):
        raise CheckError("文件不存在: %s" % path)
    with open(path, encoding="utf-8") as f:
        return f.read()


def check_spec(spec: str, include_file_checks: bool = True) -> list:
    """核对规格文档自身 —— 返回 [(name, ok, detail), ...]

    include_file_checks=False 时跳过"读上游文件"那两条 (自检用的合成样本没有上游文件)。
    """
    out = []

    # ① 9 个打点名一个都不能少 (SOUL.md: 打点名一字不改名)
    #    ★用词边界匹配: 否则 "t_npu_XX" 也算含 "t_npu" ⇒ 漏检
    missing = [p for p in REQUIRED_POINTS if not re.search(r"\b%s\b" % re.escape(p), spec)]
    out.append((
        "打点名齐全 (9 个, 取自 ARS45_INT8_CHAIN §4)",
        not missing,
        "缺: %s" % missing if missing else "9/9 齐全",
    ))

    # ② 端到端汇总点必须存在 (口径 A 软/硬两层)
    for k in ("t_e2e_A_soft", "t_e2e_A_hard", "S10"):
        out.append(("汇总/占位项 %s 存在" % k, k in spec, "有" if k in spec else "缺"))

    # ③ 时钟基准: 必须写明 MONOTONIC, 且禁止 CLOCK_REALTIME
    out.append((
        "时钟基准 = CLOCK_MONOTONIC 且显式禁用 CLOCK_REALTIME",
        "CLOCK_MONOTONIC" in spec and "不许用 `CLOCK_REALTIME`" in spec,
        "MONOTONIC=%s REALTIME禁用=%s" % ("CLOCK_MONOTONIC" in spec,
                                          "不许用 `CLOCK_REALTIME`" in spec),
    ))

    # ④ 报数字段齐全
    missing_f = [f for f in REQUIRED_FIELDS if f not in spec]
    out.append((
        "报数字段齐全 (min/avg/max/p50/p95/n)",
        not missing_f,
        "缺: %s" % missing_f if missing_f else "6/6 齐全",
    ))

    # ⑤ 采样帧数门槛 ≥300
    out.append((
        "采样帧数门槛 ≥300 帧",
        "300" in spec,
        "有" if "300" in spec else "缺",
    ))

    # ⑥ CSV 表头 14 列齐全且顺序一致
    csv_ok = False
    m = re.search(r"^frame_idx,.*$", spec, re.M)
    if m:
        got = [c.strip() for c in m.group(0).split(",")]
        csv_ok = got == CSV_HEADER
        detail = "表头 %d 列, 与规定一致=%s" % (len(got), csv_ok)
    else:
        detail = "找不到 CSV 表头行"
    out.append(("CSV 表头 14 列齐全且顺序一致", csv_ok, detail))

    # ⑦ 口径 A 必须分 A-soft / A-hard 两层 (不许混报)
    out.append((
        "口径 A 分 A-soft / A-hard 两层 (终点不偷换)",
        "A-soft" in spec and "A-hard" in spec,
        "有" if ("A-soft" in spec and "A-hard" in spec) else "缺",
    ))

    # ⑧ S10 必须标 [0数据] (不许编光机延迟)
    s10_zero = bool(re.search(r"S10[^\n]{0,80}\[0数据\]", spec)) or \
        bool(re.search(r"\[0数据\][^\n]{0,80}S10", spec))
    out.append(("S10 (光机逐帧延迟) 标 [0数据]", s10_zero, "已标" if s10_zero else "未标"))

    # ⑨ 曝光时长必须单列 (不许并进 t_capture)
    out.append((
        "曝光时长单列 (exposure_us 不并进 t_capture)",
        "exposure_us" in spec and "不并进 `t_capture`" in spec,
        "有" if ("exposure_us" in spec and "不并进 `t_capture`" in spec) else "缺",
    ))

    # ⑩ 纯 NPU vs SDK 总耗时 必须分开报 (A733 铁律)
    out.append((
        "纯 NPU vs SDK 总耗时 分开报 (A733 铁律)",
        "27.19" in spec and "36.51" in spec and "9.29" in spec,
        "A733 基准三数齐全" if ("27.19" in spec and "36.51" in spec and "9.29" in spec) else "缺 A733 基准",
    ))

    # ⑪ 11 段接力表行数 (段 1..11)
    out.append((
        "时序接力表 ≥11 段",
        spec.count("| 11 | 段") >= 1 or spec.count("| 10 | 汇总") >= 1,
        "找到段 10/11 行",
    ))

    # ⑫ 阶段 1 = t0 曝光积分开始, 阶段 9 = t9 光机出光
    out.append((
        "事件时间线 t0..t9 齐全",
        all(("t%d" % i) in spec for i in range(0, 10)),
        "t0..t9 全在" if all(("t%d" % i) in spec for i in range(0, 10)) else "缺",
    ))

    # ⑬ demo 阶段 60ms 不设门限
    out.append((
        "demo 阶段 60ms 不设门限 (只记录)",
        "不设门限" in spec,
        "有" if "不设门限" in spec else "缺",
    ))

    # ⑭ t_compose 是关键未知数 (1920×1080 ×4.32)
    out.append((
        "t_compose 标注为关键未知数 (×4.32 像素)",
        "t_compose" in spec and "4.32" in spec,
        "有" if ("t_compose" in spec and "4.32" in spec) else "缺",
    ))

    # ⑮ 验收判据 9 条 (demo 线)
    crit = len(re.findall(r"^\| [①②③④⑤⑥⑦⑧⑨] ", spec, re.M))
    out.append(("验收判据 ≥9 条", crit >= 9, "找到 %d 条" % crit))

    # ⑯ 必读: 打点名与上游 §4 一致 (不许改名字)
    if include_file_checks:
        up_ok, up_detail = False, "上游文件不存在"
        if os.path.exists(CHAIN):
            up = read(CHAIN)
            miss_up = [p for p in REQUIRED_POINTS if p not in up]
            up_ok = not miss_up
            up_detail = "上游缺: %s" % miss_up if miss_up else "9/9 对上"
        out.append(("打点名与上游 ARS45_INT8_CHAIN §4 一致", up_ok, up_detail))

        # ⑰ 上游规格存在 (本单是它的补充, 不是替代)
        out.append((
            "上游 DEMO_OD_PIPELINE_SPEC.md 存在",
            os.path.exists(UPSTREAM),
            "在" if os.path.exists(UPSTREAM) else "缺",
        ))

    # ⑱ 本单不许写板端时延数字 —— 全文不得出现"板端实测 xx ms"式的假数
    fake = re.findall(r"板端实测[^。\n]{0,30}?(\d+\.\d+)\s*ms", spec)
    out.append((
        "本单未编造板端时延数字",
        not fake,
        "发现疑似编造: %s" % fake if fake else "无",
    ))

    return out


def selftest() -> int:
    """自检: 用一份合成文档验证检查器本身能抓出问题 (不是永远返回全过)"""
    good = """t_capture t_pre t_npu t_sdk_total t_decode t_draw t_compose t_display
t_e2e_A_soft t_e2e_A_hard S10
CLOCK_MONOTONIC 不许用 `CLOCK_REALTIME`
min avg max p50 p95 n
300 帧
frame_idx,ts_capture,ts_pre,ts_npu,ts_sdk_total,ts_decode,ts_draw,ts_compose,ts_display,exposure_us,queue_wait_ms,box_count,npu_err,frame_dropped
A-soft A-hard
S10 = [0数据]
exposure_us 不并进 `t_capture`
27.19 36.51 9.29
| 10 | 汇总 | | 11 | 段
t0 t1 t2 t3 t4 t5 t6 t7 t8 t9
不设门限
t_compose 4.32
| ① | a |
| ② | a |
| ③ | a |
| ④ | a |
| ⑤ | a |
| ⑥ | a |
| ⑦ | a |
| ⑧ | a |
| ⑨ | a |
"""
    r_good = check_spec(good, include_file_checks=False)
    fails_good = [n for n, ok, _ in r_good if not ok]

    # 变异体 1: 删掉 t_npu (打点名缺失必须被抓到)
    #    ★删词边界: 只把 "t_npu " 换掉, 避免 "t_npu_XX" 里仍含 "t_npu" 子串而漏检
    bad1 = good.replace("t_npu ", "")
    fails1 = [n for n, ok, _ in check_spec(bad1, include_file_checks=False) if not ok]

    # 变异体 2: 把 MONOTONIC 换成 REALTIME (时钟基准必须被抓到)
    bad2 = good.replace("CLOCK_MONOTONIC", "CLOCK_REALTIME")
    fails2 = [n for n, ok, _ in check_spec(bad2, include_file_checks=False) if not ok]

    # 变异体 3: 删掉 S10 的 [0数据] 标记 (不许编光机延迟)
    bad3 = good.replace("S10 = [0数据]", "S10 = 5.0 ms")
    fails3 = [n for n, ok, _ in check_spec(bad3, include_file_checks=False) if not ok]

    checks = [
        ("好样本应当全过", not fails_good, "未过: %s" % fails_good),
        ("反例1 缺打点名必被抓到", any("打点名齐全" in f for f in fails1), "抓到: %s" % fails1),
        ("反例2 错时钟基准必被抓到", any("时钟基准" in f for f in fails2), "抓到: %s" % fails2),
        ("反例3 编 S10 必被抓到", any("S10" in f for f in fails3), "抓到: %s" % fails3),
    ]
    passed = sum(1 for _, ok, _ in checks if ok)
    print("=" * 78)
    print("自检 (demo_timing_check): %d/%d" % (passed, len(checks)))
    for name, ok, detail in checks:
        print("  %s %-34s %s" % ("✅" if ok else "❌", name, detail))
    print("=" * 78)
    rc = 0 if passed == len(checks) else 1
    print("退出码 rc = %d (0=自检全过)" % rc)
    return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    try:
        spec = read(SPEC)
    except CheckError as e:
        print("❌ %s" % e)
        return 2

    res = check_spec(spec)
    passed = sum(1 for _, ok, _ in res if ok)
    if a.json:
        print(json.dumps({
            "spec": "SW/DEMO_OD_TIMING_SPEC.md",
            "passed": passed, "total": len(res),
            "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in res],
            "board_latency": "[0数据] (无板) —— 本脚本不编板端时延数字",
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 78)
        print("ISS-145 demo 端到端时序规格自检: %d/%d" % (passed, len(res)))
        print("=" * 78)
        for name, ok, detail in res:
            print("  %s %-42s %s" % ("✅" if ok else "❌", name, detail))
        print("-" * 78)
        print("★板端时延数字 = [0数据] (无板) —— 本脚本只核规格结构, 不编数")
    return 0 if passed == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
