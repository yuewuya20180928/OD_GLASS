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
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # .../SW/tools
PROJ = os.path.dirname(os.path.dirname(HERE))            # .../<项目库根>
SPEC = os.path.join(PROJ, "SW", "DEMO_OD_TIMING_SPEC.md")
UPSTREAM = os.path.join(PROJ, "SW", "DEMO_OD_PIPELINE_SPEC.md")
CHAIN = os.path.join(PROJ, "SW", "ARS45_INT8_CHAIN.md")

# ============================================================================
# ★ISS-215 (2026-11-16): 60ms 判据链「显示侧」重锚门禁 (demo 屏 480×640)
# ============================================================================
VERDICT = os.path.join(PROJ, "SW", "DEMO_BOARD_60MS_VERDICT_PLAN.md")
TRIAGE215 = os.path.join(PROJ, "SW", "DEMO_60MS_DISPLAY_REANCHOR_TRIAGE.md")

# ============================================================================
# ★ISS-221 (2026-11-16): demo 预算【真源脚本】门禁
#   —— demo 判据链引用的数必须 == demo 真源脚本的输出, 且不许再引用整机 DSI 常量
# ============================================================================
DEMO_BUDGET = os.path.join(PROJ, "SW", "tools", "demo_e2e_budget.py")
ANCHOR_BEGIN = "<!-- BEGIN demo 预算真源锚点 (ISS-221)"
ANCHOR_END = "<!-- END demo 预算真源锚点 (ISS-221)"

# ★整机 DSI 带宽口径的“指纹” (demo 活动口径里出现即须显式标成整机语境)
#   ★★★ 只收【能唯一指向整机 4-lane 账本】的写法 ★★★
#   ★★上一轮半成品就栽在这 (2026-11-16 03:5x 实查): 原列表含 "@2.0Gbps" 与 "80% 效率"
#     ⇒ ★**demo 口径 A 本身就是「2 通道 × 2.0 Gbps × 80% 效率」** (ISS-212 §2 定版)
#     ⇒ 把它们当整机指纹 ⇒ 门禁会对**正确的** demo 文档误报红
#     (实测会中招的行: SW/DEMO_OD_TIMING_SPEC.md L230「demo 活动口径: 2-lane D-PHY@2.0Gbps × 80%」)
#   ⇒ 指纹只取: 4-lane / 4 lane / 4 通道 / 整机 4-lane 有效带宽 6400 Mbps
MACHINE_DSI_FINGERPRINTS = ["4-lane", "4 lane", "4 通道", "6400 Mbps"]

# ★整机预算脚本的【调用】写法 (demo 活动口径里不许出现 ⇒ demo 链的判据工具必须是 demo 真源脚本)
MACHINE_SCRIPT_INVOKE = re.compile(r"python3\s+HW/e2e_budget_rk3572\.py|`HW/e2e_budget_rk3572\.py\s+--")

# ★★豁免标记: 只说明"这是整机语境"的措辞 (★比 ISS-215 的整机口径 token 列表宽,
#   因为这里判的是"整机 DSI 指纹"而不是"整机口径数值"★)
MACHINE_EXEMPT_MARKERS = ["整机", "暂缓", "历史", "作废"]

# ★★「demo 预算真源锚点」区块的「项名 → 真源脚本输出键」映射 ★★
#   ★项名 = 文档里的稳定标签; 值必须 == 脚本输出 ⇒ 手抄错一个数就红 (ISS-221 门禁的核心里的一条)★
#   ★门禁认识的项名集合 == 文档锚点区块必须写满的项数 ⇒ 少写一行蒙混过关也不合格★
#   ★("plan" 那一档的第二项是方案名里必须出现的片段, 不写全名 ⇒ 脚本改方案名不必改门禁)★
ANCHOR_KEY_MAP = {
    "demo TX 物理下限 (口径 A)": ("scalar", "tx_floor_a_ms"),
    "demo TX 物理下限 (口径 B)": ("scalar", "tx_floor_b_ms"),
    "demo t_compose 估算 (÷6.75)": ("scalar", "t_compose_est_ms"),
    "demo 显示输出侧合计 [推算]": ("scalar", "display_out_est_ms"),
    "输出侧总额上限 (yolov5s@640)": ("plan", "yolov5s@640", "display_out_cap_ms"),
    "合成段上限 (yolov5s@640)": ("plan", "yolov5s@640", "compose_cap_ms"),
    "输出侧总额上限 (yolov5n@640)": ("plan", "yolov5n@640", "display_out_cap_ms"),
    "合成段上限 (yolov5n@640)": ("plan", "yolov5n@640", "compose_cap_ms"),
    "输出侧总额上限 (yolov5s@320)": ("plan", "yolov5s@320", "display_out_cap_ms"),
    "合成段上限 (yolov5s@320)": ("plan", "yolov5s@320", "compose_cap_ms"),
    "全链路 60ms 预算余量 (yolov5n@640)": ("plan", "yolov5n@640", "margin_ms"),
}

# ★数值比对容差 (脚本侧已 round 到 2~3 位; 0.005 ⇒ 能抓住 0.01 ms 的手抄漂移)★
ANCHOR_TOL_MS = 0.005

# ★「表 A — demo 活动口径」的数据表必须逐行 == 真源脚本输出 (表名的标记, 见 ISS-212)★
DEMO_TABLE_MARK = "表 A — demo 活动口径"

# ★整机路线占位区标记 —— 与 ISS-212 `SW/tools/check_demo_panel_spec.py` 同一套机制
BLOCK_BEGIN = "<!-- BEGIN 整机路线占位区"
BLOCK_END = "<!-- END 整机路线占位区"

# ★"整机口径" token (正则) —— demo 活动口径里出现即判不合格 (除非带豁免标记或落在整机占位区)
LEGACY_RES = [
    re.compile(r"(?<![\d.])7\.776(?![\d])"),   # 整机 TX 物理下限 @1080p
    re.compile(r"(?<![\d.])2\.32(?![\d])"),    # 整机口径的合成段上限 (10.09 - 7.776)
    re.compile(r"(?<![\d.])4\.32(?![\d])"),    # 整机口径的缩放律 (×4.32)
    re.compile(r"(?<![\d.])12\.96(?![\d])"),   # 整机口径的线性上界 (3.00 × 4.32)
    re.compile(r"1920\s*[×xX]\s*1080"),       # 整机屏分辨率
    re.compile(r"1080p"),                     # 整机口径标记
]

# ★豁免标记: 该行只要带其一, 说明它是整机路线占位 / 历史 / 降级说明 ⇒ 允许
EXEMPT_MARKERS = ["整机路线", "整机屏", "整机口径", "历史", "作废", "暂缓"]

# ★demo 活动口径必含项 (全部出自 ISS-212 已发布的数: 480×640 / ÷6.75 / 0.44 / 2.75 / 7.79 / 2.304 / 2.048)
DEMO_REQUIRED = ["480×640", "÷6.75", "0.44", "2.75", "7.79", "2.304", "2.048"]

# ★demo 活动口径表的表头签名 (用来定位「表 A」并检查它的数据行)
DEMO_TABLE_SIG = "输出侧总额上限"

# ★打点名取自 SW/ARS45_INT8_CHAIN.md §4 (B8 埋点表) —— 上游真源, 不许自己另起一套
REQUIRED_POINTS = [
    "t_capture", "t_pre", "t_npu", "t_sdk_total",
    "t_decode", "t_draw", "t_compose", "t_display",
]
REQUIRED_FIELDS = ["min", "avg", "max", "p50", "p95", "n"]
CSV_HEADER = [
    "frame_idx", "ts_capture", "ts_isp_in", "ts_isp_hw_start", "ts_isp_out",
    "ts_pre", "ts_npu", "ts_sdk_total",
    "ts_decode", "ts_draw", "ts_compose", "ts_display",
    "exposure_us", "queue_wait_ms", "box_count", "npu_err", "frame_dropped",
]
# ★ISS-210 (2026-11-15): §2 段表 11 段 => **12 段** (新增段 12 = ISP) ⇒ CSV 表头 14 列 => **17 列**
#   (多出 ts_isp_in / ts_isp_hw_start / ts_isp_out 三列 ⇒ 派生 t_isp_total (判据用) + t_isp_hw (归因用))


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
    out.append(("CSV 表头 17 列齐全且顺序一致", csv_ok, detail))

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

    # ⑭ t_compose 是关键未知数 (★ISS-215: demo 屏 480×640 · 缩放律 ÷6.75, 不再是整机的 ×4.32)
    _c14 = ("t_compose" in spec and "÷6.75" in spec and "0.44" in spec)
    out.append((
        "t_compose 标注为关键未知数 (÷6.75 缩放 · demo 480×640)",
        _c14,
        "有" if _c14 else "缺",
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

    # ⑲ ★ISS-210 (2026-11-15): 12 段接力表 + ISP 段打点名 + ISP 判据线 (新增段 12 = ISP)
    out.append((
        "ISP 段打点名齐全 (t_isp_hw + t_isp_total, 两个数不许合并)",
        "t_isp_hw" in spec and "t_isp_total" in spec,
        "有" if ("t_isp_hw" in spec and "t_isp_total" in spec) else "缺",
    ))
    out.append((
        "ISP 段判据线齐全 (模式A 15.10 / 模式B 17.33 ms)",
        "15.10" in spec and "17.33" in spec,
        "有" if ("15.10" in spec and "17.33" in spec) else "缺",
    ))
    out.append((
        "时序接力表 = 12 段 (段号 1..12, 含段 12 = ISP)",
        spec.count("| 12 | ") >= 1,
        "找到段 12 行" if spec.count("| 12 | ") >= 1 else "缺",
    ))

    # ⑱ 本单不许写板端时延数字 —— 全文不得出现"板端实测 xx ms"式的假数
    fake = re.findall(r"板端实测[^。\n]{0,30}?(\d+\.\d+)\s*ms", spec)
    out.append((
        "本单未编造板端时延数字",
        not fake,
        "发现疑似编造: %s" % fake if fake else "无",
    ))

    return out


# ---------------------------------------------------------------------------
# ★ISS-215: 60ms 判据链显示侧的 demo 活动口径门禁
# ---------------------------------------------------------------------------
def block_mask(text: str) -> list:
    """返回每行是否落在「整机路线占位区」块内 (与 ISS-212 同一套机制)。"""
    mask = []
    inside = False
    for line in text.split("\n"):
        if BLOCK_BEGIN in line:
            inside = True
            mask.append(True)
            continue
        if BLOCK_END in line:
            inside = False
            mask.append(True)
            continue
        mask.append(inside)
    return mask


def _legacy_hits(line: str) -> list:
    return [r.pattern for r in LEGACY_RES if r.search(line)]


def check_display_reanchor(docs: dict) -> list:
    """ISS-215: 60ms 判据链显示侧的 demo 活动口径门禁。

    docs = {"SW/DEMO_OD_TIMING_SPEC.md": ..., "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md": ..., "triage": ...}
    ★本函数【不编任何板端时延数字】, 只核对口径分流是否正确。
    """
    out = []
    names = ["SW/DEMO_OD_TIMING_SPEC.md", "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md"]

    for name in names:
        text = docs.get(name, "")
        lines = text.split("\n")
        mask = block_mask(text)

        # ⑳ 整机口径 token 必须显式标注 (落在整机占位区 或 同行带豁免标记)
        bad = []
        for idx, line in enumerate(lines):
            hits = _legacy_hits(line)
            if not hits:
                continue
            if mask[idx]:
                continue                                    # 在占位区块内 ⇒ 允许
            if any(mark in line for mark in EXEMPT_MARKERS):
                continue                                    # 带「整机路线/暂缓/历史」标注 ⇒ 允许
            bad.append("L%d%s" % (idx + 1, hits))
        out.append((
            "[ISS-215] %s 整机口径 token 必须显式标注" % name,
            not bad,
            "未标注: %s" % bad if bad else "全部已标注/已分区",
        ))

        # ㉑ demo 活动口径必含项齐全 (ISS-212 已发布的 7 个数)
        missing = [t for t in DEMO_REQUIRED if t not in text]
        out.append((
            "[ISS-215] %s demo 活动口径必含项齐全 (7 项)" % name,
            not missing,
            "缺: %s" % missing if missing else "7/7 齐全",
        ))

        # ㉒ demo 活动口径表的数据行零整机 token (整机那套不许占着 demo 栏的格子)
        bad_rows = []
        in_demo_tbl = False
        for idx, line in enumerate(lines):
            if not line.startswith("|"):
                in_demo_tbl = False
                continue
            if mask[idx]:
                in_demo_tbl = False
                continue
            if "---" in line:
                continue
            if DEMO_TABLE_SIG in line:
                in_demo_tbl = True
                continue
            if in_demo_tbl:
                hits = _legacy_hits(line)
                if hits and not any(mark in line for mark in EXEMPT_MARKERS):
                    bad_rows.append("L%d%s" % (idx + 1, hits))
        out.append((
            "[ISS-215] %s demo 活动口径表数据行零整机 token" % name,
            not bad_rows,
            "混入: %s" % bad_rows if bad_rows else "干净",
        ))

        # ㉓ 10.09 只许以「输出侧总额上限」身份出现 (该行或最近的表头行须含 "输出侧")
        bad10 = []
        for idx, line in enumerate(lines):
            if "10.09" not in line:
                continue
            if mask[idx]:
                continue
            if "输出侧" in line:
                continue
            hdr = ""
            for back in range(idx - 1, max(-1, idx - 12), -1):
                cand = lines[back]
                if cand.startswith("|") and "---" in cand:
                    # ★分隔行 ⇒ 它上面那一行就是表头
                    hdr = lines[back - 1] if back - 1 >= 0 else ""
                    break
                if not cand.startswith("|"):
                    break
            if "输出侧" not in hdr:
                bad10.append("L%d" % (idx + 1))
        out.append((
            "[ISS-215] %s 的 10.09 必带「输出侧上限」身份" % name,
            not bad10,
            "身份不明: %s" % bad10 if bad10 else "全部有身份",
        ))

        # ㉔ 整机占位区必须显式分区 (BEGIN/END 成对)
        nb, ne = text.count(BLOCK_BEGIN), text.count(BLOCK_END)
        out.append((
            "[ISS-215] %s 有成对的「整机路线占位区」分区标记" % name,
            nb >= 1 and nb == ne,
            "BEGIN=%d END=%d" % (nb, ne),
        ))

    # ㉕ 逐处定性表存在 + 四档判定齐全
    tri = docs.get("triage", "")
    tri_ok = all(k in tri for k in ("demo 活动口径", "整机路线占位", "历史留档", "说明文字"))
    out.append((
        "[ISS-215] 逐处定性表存在且四档判定齐全",
        bool(tri) and tri_ok,
        "存在, 四档齐全" if tri_ok else "缺定性表或判定档不全",
    ))
    return out


# ---------------------------------------------------------------------------
# ★ISS-221 (2026-11-16): demo 预算【真源脚本】门禁
#   —— demo 判据链引用的数必须 == demo 真源脚本的输出, 且不许再引用整机 4-lane DSI 常量
# ---------------------------------------------------------------------------
def _demo_budget_truth():
    """导入 demo 真源脚本并算一份账 (★脚本不在 / 导不进 ⇒ 门禁红, 不许静默跳过★)。"""
    if not os.path.exists(DEMO_BUDGET):
        return None, "真源脚本不存在: %s" % DEMO_BUDGET
    try:
        spec = importlib.util.spec_from_file_location("demo_e2e_budget_gate", DEMO_BUDGET)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.compute_report(), None
    except Exception as e:                                    # 脚本自身炸了也算门禁红
        return None, "真源脚本导入/执行失败: %s: %s" % (type(e).__name__, e)


def _truth_lookup(truth: dict, keys: tuple):
    """按 ANCHOR_KEY_MAP 的说明, 从真源脚本的输出里取值 (取不到 ⇒ None)。"""
    if keys[0] == "scalar":
        return truth.get(keys[1])
    _, plan_key, field = keys
    for p in truth.get("plans", []):
        if plan_key in p.get("name", ""):
            return p.get(field)
    return None


def _cell_to_float(cell: str):
    """把文档单元格里那个数取出来 (★兼容 −(U+2212) / **加粗** / 后缀 ms★)。"""
    c = cell.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")
    c = c.replace("**", "").replace("*", "").replace("`", "")
    c = c.replace("ms", "").replace("MS", "").replace("Ms", "")
    m = re.search(r"-?\d+(?:\.\d+)?", c)
    return float(m.group(0)) if m else None


def _fmt_num(v) -> str:
    """把一个数格式成文档里好读的样子 (3 位小数 ⇒ 2.304 / 2.048 / 0.440 都对得上)。"""
    if v is None:
        return "?"
    return "%.3f" % float(v)


def _anchor_rows(text: str):
    """取「demo 预算真源锚点」区块里的 (项名, 值单元格) 对。取不到 ⇒ None。"""
    m = re.search(re.escape(ANCHOR_BEGIN) + r"(.*?)" + re.escape(ANCHOR_END), text, re.S)
    if not m:
        return None
    rows = []
    for line in m.group(1).split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if cells[0] == "项":                       # 表头行
            continue
        rows.append((cells[0], cells[1]))
    return rows


def _demo_plan_table_rows(text: str):
    """取「表 A — demo 活动口径」的数据行 (方案 / S5 / 输出侧总额上限 / 合成段上限 / 显示输出侧)。"""
    lines = text.split("\n")
    mask = block_mask(text)
    rows, in_tbl = [], False
    for idx, line in enumerate(lines):
        if not line.startswith("|"):
            in_tbl = False
            continue
        if mask[idx]:                             # 整机路线占位区 ⇒ 不算 demo 活动口径
            in_tbl = False
            continue
        if "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0].startswith("方案") and any("输出侧总额上限" in c for c in cells):
            in_tbl = True
            continue
        if not in_tbl or len(cells) < 5:
            continue
        rows.append((idx + 1, cells))
    return rows


def check_demo_budget_source(docs: dict) -> list:
    """ISS-221: demo 判据链的预算数必须 == demo 真源脚本的输出, 且不许引用整机 4-lane DSI 常量。

    docs = {"SW/DEMO_OD_TIMING_SPEC.md": ..., "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md": ...}
    ★本函数【不编任何板端时延数字】—— 所有期望值都来自真源脚本自己的 compute_report()。
    """
    out = []
    names = ["SW/DEMO_OD_TIMING_SPEC.md", "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md"]

    truth, err = _demo_budget_truth()
    out.append((
        "[ISS-221] demo 真源脚本可执行且算得出账 (SW/tools/demo_e2e_budget.py)",
        truth is not None,
        err or ("TX下限(口径A)=%s ms · %d 个方案 · 60ms 预算=%s ms"
               % (truth["tx_floor_a_ms"], len(truth["plans"]), truth["budget_ms"])),
    ))
    if truth is None:
        for name in names:
            out.append(("[ISS-221] %s 锚点区块逐项 == demo 真源脚本输出" % name, False,
                        "真源脚本不可用 ⇒ 无从比对"))
        return out

    # ★真源脚本自身不许含整机 DSI 常量 (复用它自己的源码泄漏扫描器)★
    leaks = []
    try:
        with open(DEMO_BUDGET, encoding="utf-8") as f:
            src = f.read()
        spec = importlib.util.spec_from_file_location("demo_e2e_budget_leak", DEMO_BUDGET)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        leaks = list(mod.source_leak_anomalies(src))
    except Exception as e:
        leaks = ["扫描失败: %s: %s" % (type(e).__name__, e)]
    out.append((
        "[ISS-221] demo 真源脚本源码零整机 DSI 常量",
        not leaks,
        "泄漏: %s" % leaks if leaks else "0 项",
    ))

    anchor_map = {}
    for name in names:
        text = docs.get(name, "")
        lines = text.split("\n")
        mask = block_mask(text)

        # ⑴ 锚点区块必须存在且成对
        nb, ne = text.count(ANCHOR_BEGIN), text.count(ANCHOR_END)
        out.append((
            "[ISS-221] %s 有成对的「demo 预算真源锚点」分区标记" % name,
            nb >= 1 and nb == ne,
            "BEGIN=%d END=%d" % (nb, ne),
        ))

        # ⑵ 锚点区块逐项 == 真源脚本输出
        rows = _anchor_rows(text)
        if not rows:
            anchor_map[name] = {}
            out.append(("[ISS-221] %s 锚点区块逐项 == demo 真源脚本输出" % name, False,
                        "锚点区块缺失或解析不出数据行"))
        else:
            anchor_map[name] = dict(rows)
            bad = []
            for label, cell in rows:
                keys = ANCHOR_KEY_MAP.get(label)
                if keys is None:
                    bad.append("门禁不认识的项名 %r (改脚本输出 ⇒ 同步门禁映射)" % label)
                    continue
                want = _truth_lookup(truth, keys)
                got = _cell_to_float(cell)
                if got is None:
                    bad.append("%s: 值取不出 (%r)" % (label, cell))
                elif want is None:
                    bad.append("%s: 真源脚本算不出该值 (%s)" % (label, keys))
                elif abs(got - want) > ANCHOR_TOL_MS:
                    bad.append("%s: 文档 %s ≠ 真源 %s" % (label, got, want))
            out.append((
                "[ISS-221] %s 锚点区块逐项 == demo 真源脚本输出" % name,
                not bad,
                "; ".join(bad) if bad else "%d 项全对上" % len(rows),
            ))

            # ⑶ 锚点区块必须写满门禁认识的全部项 (不许少写一行蒙混过关)
            missing = [k for k in ANCHOR_KEY_MAP if k not in anchor_map[name]]
            out.append((
                "[ISS-221] %s 锚点区块项齐全 (%d 项)" % (name, len(ANCHOR_KEY_MAP)),
                not missing,
                "缺: %s" % missing if missing else
                "%d/%d 齐全" % (len(anchor_map[name]), len(ANCHOR_KEY_MAP)),
            ))

        # ⑷ demo 活动口径零「整机 4-lane DSI」指纹
        bad_fp = []
        for idx, line in enumerate(lines):
            if mask[idx]:
                continue
            hits = [t for t in MACHINE_DSI_FINGERPRINTS if t in line]
            if not hits:
                continue
            if any(mk in line for mk in MACHINE_EXEMPT_MARKERS):
                continue
            bad_fp.append("L%d%s" % (idx + 1, hits))
        out.append((
            "[ISS-221] %s demo 活动口径零「整机 4-lane DSI」指纹" % name,
            not bad_fp,
            "混入: %s" % bad_fp if bad_fp else "干净",
        ))

        # ⑸ 判据工具必须是 demo 真源脚本 (不许拿整机脚本当 demo 判据工具)
        bad_inv = []
        for idx, line in enumerate(lines):
            if mask[idx]:
                continue
            if not MACHINE_SCRIPT_INVOKE.search(line):
                continue
            if any(mk in line for mk in MACHINE_EXEMPT_MARKERS):
                continue
            if "--selftest" in line:
                continue          # ★整机脚本自己的账本自检, 不产 demo 判据数★
            bad_inv.append("L%d" % (idx + 1))
        out.append((
            "[ISS-221] %s 判据工具是 demo 真源脚本 (不许拿整机脚本当判据工具)" % name,
            not bad_inv,
            "违规: %s" % bad_inv if bad_inv else "无",
        ))

        # ⑹ 必须真的引用 demo 真源脚本
        out.append((
            "[ISS-221] %s 引用了 demo 真源脚本" % name,
            "demo_e2e_budget.py" in text,
            "有" if "demo_e2e_budget.py" in text else "缺",
        ))

        # ⑺「表 A — demo 活动口径」必须存在, 且每一行都 == 真源脚本输出
        trows = _demo_plan_table_rows(text)
        need_tbl = DEMO_TABLE_MARK in text
        if not trows:
            out.append((
                "[ISS-221] %s demo 活动口径表逐行 == demo 真源脚本输出" % name,
                not need_tbl,
                "本文件带「%s」标记却找不到数据行" % DEMO_TABLE_MARK if need_tbl
                else "本文件无「%s」⇒ 免检 (只有锚点区块)" % DEMO_TABLE_MARK,
            ))
        else:
            bad_t = []
            for lineno, cells in trows:
                plan_name = cells[0]
                match = None
                for p in truth["plans"]:
                    if p["name"] in plan_name or plan_name in p["name"]:
                        match = p
                        break
                if match is None:
                    bad_t.append("L%d: 方案 %r 不在真源方案表里" % (lineno, plan_name))
                    continue
                for col, field in ((1, "s5_ms"), (2, "display_out_cap_ms"),
                                   (3, "compose_cap_ms")):
                    got = _cell_to_float(cells[col])
                    want = match.get(field)
                    if got is None or want is None:
                        bad_t.append("L%d col%d: 取不出 (%r)" % (lineno, col, cells[col]))
                    elif abs(got - want) > ANCHOR_TOL_MS:
                        bad_t.append("L%d col%d: 文档 %s ≠ 真源 %s" % (lineno, col, got, want))
                # 第 5 列 = 显示输出侧合计 (★它是【顶层】标量, 不在方案字典里★)
                got4 = _cell_to_float(cells[4])
                want4 = truth.get("display_out_est_ms")
                if got4 is None or want4 is None:
                    bad_t.append("L%d col4: 取不出 (%r)" % (lineno, cells[4]))
                elif abs(got4 - want4) > ANCHOR_TOL_MS:
                    bad_t.append("L%d col4: 文档 %s ≠ 真源 %s" % (lineno, got4, want4))
            out.append((
                "[ISS-221] %s demo 活动口径表逐行 == demo 真源脚本输出" % name,
                not bad_t,
                "; ".join(bad_t) if bad_t else "%d 行全对上" % len(trows),
            ))

    # ⑻ 两份文档的锚点区块必须逐项一致 (不许一份改了另一份没改)
    if len(anchor_map) == len(names):
        (n1, a), (n2, b) = list(anchor_map.items())
        diff = ["%s: %s ≠ %s" % (k, a.get(k), b.get(k))
                for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
        out.append((
            "[ISS-221] 两份文档的锚点区块逐项一致",
            not diff,
            "; ".join(diff) if diff else "一致 (%s / %s)" % (n1, n2),
        ))
    return out


def _good221_doc(truth: dict) -> str:
    """按真源脚本的输出生成一份「正确的」ISS-221 样本文档 (★自检的好样本★)。"""
    anchor_rows = []
    for label, keys in ANCHOR_KEY_MAP.items():
        anchor_rows.append("| %s | %s ms | `SW/tools/demo_e2e_budget.py` |"
                           % (label, _fmt_num(_truth_lookup(truth, keys))))
    plan_rows = []
    for p in truth["plans"]:
        plan_rows.append("| %s | %s | %s ms | %s ms | ~%s ms | %s |"
                         % (p["name"], _fmt_num(p["s5_ms"]), _fmt_num(p["display_out_cap_ms"]),
                            _fmt_num(p["compose_cap_ms"]), _fmt_num(truth["display_out_est_ms"]),
                            "✅ 过" if p["verdict"] == "PASS" else "❌ 不过"))
    return (
        "> ★ISS-221 demo 预算真源: 本文件所有 demo 侧预算数由 "
        "`python3 SW/tools/demo_e2e_budget.py` 输出\n"
        "★★**表 A — demo 活动口径 (480×640 · 2-lane)★★**\n"
        "| 方案 | S5(ms) | **输出侧总额上限** | **减 demo TX 下限后·合成段上限** | "
        "**显示输出侧 [推算]** | 判定 |\n"
        "|---|---|---|---|---|---|\n"
        + "\n".join(plan_rows) + "\n"
        + "<!-- BEGIN demo 预算真源锚点 (ISS-221) -->\n"
        + "| 项 | 值 | 源 |\n|---|---|---|\n"
        + "\n".join(anchor_rows) + "\n"
        + "<!-- END demo 预算真源锚点 (ISS-221) -->\n"
        + "| 判据 | 显示输出侧合计 ≤ %s ms | "
          "`python3 SW/tools/demo_e2e_budget.py --t-compose-ms … --t-display-ms …` |\n"
          % _fmt_num(truth["plans"][1]["display_out_cap_ms"])
    )


def selftest() -> int:
    """自检: 用一份合成文档验证检查器本身能抓出问题 (不是永远返回全过)"""
    good = """t_capture t_pre t_npu t_sdk_total t_decode t_draw t_compose t_display
t_e2e_A_soft t_e2e_A_hard S10
CLOCK_MONOTONIC 不许用 `CLOCK_REALTIME`
min avg max p50 p95 n
300 帧
frame_idx,ts_capture,ts_isp_in,ts_isp_hw_start,ts_isp_out,ts_pre,ts_npu,ts_sdk_total,ts_decode,ts_draw,ts_compose,ts_display,exposure_us,queue_wait_ms,box_count,npu_err,frame_dropped
A-soft A-hard
S10 = [0数据]
exposure_us 不并进 `t_capture`
27.19 36.51 9.29
| 10 | 汇总 | | 11 | 段
| 12 | ISP |
t_isp_hw t_isp_total
15.10 17.33
t0 t1 t2 t3 t4 t5 t6 t7 t8 t9
不设门限
t_compose 0.44 ÷6.75
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

    # ── ★ISS-215 (2026-11-16): 显示侧重锚门禁 ──
    GOOD215_SPEC = """> ★ISS-215 显示侧重锚: demo 活动口径 = 480×640 · 缩放律 ÷6.75 · t_compose [推算] ~0.44 ms · 显示输出侧合计 [推算] ~2.75 ms · 合成段余量 7.79 ms · TX 物理下限 2.304 ms (口径 A) / 2.048 ms (口径 B)
显示帧 (480×640) 就绪
| 方案 | S5(ms) | **输出侧总额上限** | **减 demo TX 下限 2.304ms 后·合成段上限** | **显示输出侧 [推算]** | 判定 |
|---|---|---|---|---|---|
| RK3572 + yolov5n@640 | 13.31 | **10.09 ms** | **7.79 ms** | ~2.75 ms | ✅ |
<!-- BEGIN 整机路线占位区 (整机 1920×1080 路线 · 暂缓 · 非 demo 活动口径) -->
| 方案 | S5(ms) | **输出侧上限** | **减 TX 后·合成上限** | 线性上界@×4.32 | 判定 |
|---|---|---|---|---|---|
| RK3572 + yolov5n@640 | 13.31 | **10.09 ms** | **2.32 ms** | 12.96 | ❌ |
<!-- END 整机路线占位区 -->
"""
    GOOD215_VERDICT = """> ★ISS-215 显示侧重锚: demo 活动口径 = 480×640 · 缩放律 ÷6.75 · t_compose [推算] ~0.44 ms · 显示输出侧合计 [推算] ~2.75 ms · 合成段余量 7.79 ms · TX 物理下限 2.304 ms (口径 A) / 2.048 ms (口径 B)
| 7 合成 | `t_compose` | post 线程 | ★**输出侧总额上限 10.09 ms (ISS-137 · 与显示分辨率无关)** ★ + ★**demo 合成段上限 7.79 ms** ★ |
| 8 上屏 | `t_display` | DRM/KMS | ★**demo TX 物理下限 2.304 ms @480×640 (2-lane; 口径 A) / 2.048 ms (口径 B)** ★ ⇒ ★**整机路线·暂缓: TX 物理下限 7.776 ms @1080p** ★ |
# ② 合成/上屏侧判据 (ISS-137: 输出侧总额 ≤ 10.09 ms ⇒ demo 合成段 ≤ 7.79 ms ⇒ 已扣 demo TX 物理下限 2.304 ms)
| **3** | ★**显示输出侧** (段 7+段 8) | 合计 ≤ **10.09 ms** (★**输出侧总额上限, 与显示分辨率无关**★ ⇒ 合成段 ≤ **7.79 ms**, 已扣 **demo TX 物理下限 2.304 ms** @480×640 (口径 A) / 2.048 ms (口径 B) ⇒ ★**整机路线·暂缓: 整机 1080p 口径下是 合成段 ≤ 2.32 ms @ TX 7.776 ms**★) | `HW/e2e_budget_rk3572.py --t-compose-ms` |
<!-- BEGIN 整机路线占位区 (整机 1920×1080 路线 · 暂缓 · 非 demo 活动口径) -->
| 条件 | 通过线 | 谁判 |
|---|---|---|
| **3 (整机口径)** | 合计 ≤ **10.09 ms** (⇒ 合成段 ≤ **2.32 ms**, 已扣 TX 物理下限 7.776 ms @1080p) | `HW/e2e_budget_rk3572.py --t-compose-ms` (4-lane 口径) |
<!-- END 整机路线占位区 -->
"""
    GOOD215_TRIAGE = """# 逐处定性表
| L-01 | 83 | demo 活动口径 | 改写 |
| L-02 | 201 | 整机路线占位 | 标注 |
| L-03 | 000 | 历史留档 | 原样保留 |
| L-04 | 000 | 说明文字 | 原样保留 |
"""
    g215 = {
        "SW/DEMO_OD_TIMING_SPEC.md": GOOD215_SPEC,
        "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md": GOOD215_VERDICT,
        "triage": GOOD215_TRIAGE,
    }
    r215 = check_display_reanchor(g215)
    fails215 = [n for n, ok, _ in r215 if not ok]

    # 反例 4: 把缩放律从 demo 的 ÷6.75 塞回整机的 ×4.32 ⇒ 必须被抓到
    bad4 = good.replace("÷6.75", "×4.32")
    fails4 = [n for n, ok, _ in check_spec(bad4, include_file_checks=False) if not ok]

    # 反例 5: demo 活动口径表里把 7.79 塞回整机口径的 2.32 (不带标注) ⇒ 必须被抓到
    bad5 = dict(g215)
    bad5["SW/DEMO_OD_TIMING_SPEC.md"] = GOOD215_SPEC.replace(
        "| RK3572 + yolov5n@640 | 13.31 | **10.09 ms** | **7.79 ms** | ~2.75 ms | ✅ |",
        "| RK3572 + yolov5n@640 | 13.31 | **10.09 ms** | **2.32 ms** | ~2.75 ms | ✅ |")
    fails5 = [n for n, ok, _ in check_display_reanchor(bad5) if not ok]

    # 反例 6: 删掉 demo 必含项 7.79 ⇒ 必须被抓到
    bad6 = dict(g215)
    bad6["SW/DEMO_OD_TIMING_SPEC.md"] = GOOD215_SPEC.replace("7.79 ms", "0.00 ms")
    fails6 = [n for n, ok, _ in check_display_reanchor(bad6) if not ok]

    # 反例 7: 拆掉「整机路线占位区」分区标记 ⇒ 整机数失去分区 ⇒ 必须被抓到
    bad7 = dict(g215)
    bad7["SW/DEMO_OD_TIMING_SPEC.md"] = (GOOD215_SPEC
                                         .replace(BLOCK_BEGIN, "<!-- BEGIN 其他区")
                                         .replace(BLOCK_END, "<!-- END 其他区"))
    fails7 = [n for n, ok, _ in check_display_reanchor(bad7) if not ok]

    # 反例 8: 10.09 失去「输出侧上限」身份 ⇒ 必须被抓到
    bad8 = dict(g215)
    bad8["SW/DEMO_OD_TIMING_SPEC.md"] = GOOD215_SPEC.replace("输出侧", "上限")
    fails8 = [n for n, ok, _ in check_display_reanchor(bad8) if not ok]

    # ── ★ISS-221 (2026-11-16): demo 预算真源门禁 ──
    truth221, err221 = _demo_budget_truth()
    if truth221 is None:
        checks221 = [("ISS-221 真源脚本可执行", False, err221)]
        fails221 = ["真源脚本不可用"]
    else:
        good221 = _good221_doc(truth221)
        g221 = {
            "SW/DEMO_OD_TIMING_SPEC.md": good221,
            "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md": good221,
        }
        r221 = check_demo_budget_source(g221)
        fails221 = [n for n, ok, _ in r221 if not ok]

        # 反例 9: 锚点里 TX 物理下限手抄错 (2.304 → 2.400) ⇒ 必须被抓到
        bad9 = dict(g221)
        bad9["SW/DEMO_OD_TIMING_SPEC.md"] = good221.replace(
            "| demo TX 物理下限 (口径 A) | 2.304 ms |",
            "| demo TX 物理下限 (口径 A) | 2.400 ms |")
        fails9 = [n for n, ok, _ in check_demo_budget_source(bad9) if not ok]

        # 反例 10: 锚点里合成段上限写回整机口径 (7.79 → 2.32) ⇒ 必须被抓到
        bad10 = dict(g221)
        bad10["SW/DEMO_OD_TIMING_SPEC.md"] = good221.replace(
            "| 合成段上限 (yolov5n@640) | 7.790 ms |",
            "| 合成段上限 (yolov5n@640) | 2.320 ms |")
        fails10 = [n for n, ok, _ in check_demo_budget_source(bad10) if not ok]

        # 反例 11: 锚点区块少写一行 (删掉全链路余量行) ⇒ 「项齐全」必须抓到
        bad11 = dict(g221)
        bad11["SW/DEMO_OD_TIMING_SPEC.md"] = "\n".join(
            [l for l in good221.split("\n") if "全链路 60ms 预算余量" not in l])
        fails11 = [n for n, ok, _ in check_demo_budget_source(bad11) if not ok]

        # 反例 12: demo 活动口径混入整机 4-lane DSI 指纹 (不带豁免标记) ⇒ 必须被抓到
        bad12 = dict(g221)
        bad12["SW/DEMO_OD_TIMING_SPEC.md"] = good221.replace(
            "<!-- BEGIN demo 预算真源锚点 (ISS-221) -->",
            "| demo TX 物理下限 | 4-lane D-PHY@2.0Gbps × 80% | 7.776 ms |\n"
            "<!-- BEGIN demo 预算真源锚点 (ISS-221) -->")
        fails12 = [n for n, ok, _ in check_demo_budget_source(bad12) if not ok]

        # 反例 13: 判据工具换成整机脚本 (不带豁免标记) ⇒ 必须被抓到
        bad13 = dict(g221)
        bad13["SW/DEMO_BOARD_60MS_VERDICT_PLAN.md"] = good221.replace(
            "`python3 SW/tools/demo_e2e_budget.py --t-compose-ms … --t-display-ms …`",
            "`python3 HW/e2e_budget_rk3572.py --t-compose-ms`")
        fails13 = [n for n, ok, _ in check_demo_budget_source(bad13) if not ok]

        # 反例 14: 锚点区块整个删掉 ⇒ 必须被抓到
        bad14 = dict(g221)
        bad14["SW/DEMO_OD_TIMING_SPEC.md"] = re.sub(
            re.escape(ANCHOR_BEGIN) + r".*?" + re.escape(ANCHOR_END), "", good221, flags=re.S)
        fails14 = [n for n, ok, _ in check_demo_budget_source(bad14) if not ok]

        # 反例 15: 「表 A」里手抄错一个数 (合成段上限 7.79 → 8.79) ⇒ 必须被抓到
        bad15 = dict(g221)
        bad15["SW/DEMO_OD_TIMING_SPEC.md"] = good221.replace(
            "| RK3572 + yolov5n@640 | 13.310 | 10.090 ms | 7.790 ms |",
            "| RK3572 + yolov5n@640 | 13.310 | 10.090 ms | 8.790 ms |")
        fails15 = [n for n, ok, _ in check_demo_budget_source(bad15) if not ok]

        checks221 = [
            ("ISS-221 好样本应当全过", not fails221, "未过: %s" % fails221),
            ("ISS-221 反例9 锚点 TX 下限手抄错必被抓到",
             any("锚点区块逐项" in f for f in fails9), "抓到: %s" % fails9),
            ("ISS-221 反例10 锚点写回整机 2.32 必被抓到",
             any("锚点区块逐项" in f for f in fails10), "抓到: %s" % fails10),
            ("ISS-221 反例11 锚点少写一行必被抓到",
             any("锚点区块项齐全" in f for f in fails11), "抓到: %s" % fails11),
            ("ISS-221 反例12 混入整机 4-lane 指纹必被抓到",
             any("4-lane DSI" in f for f in fails12), "抓到: %s" % fails12),
            ("ISS-221 反例13 判据工具换成整机脚本必被抓到",
             any("判据工具是 demo 真源脚本" in f for f in fails13), "抓到: %s" % fails13),
            ("ISS-221 反例14 锚点区块删掉必被抓到",
             any("锚点区块逐项" in f for f in fails14), "抓到: %s" % fails14),
            ("ISS-221 反例15 表 A 手抄错必被抓到",
             any("活动口径表逐行" in f for f in fails15), "抓到: %s" % fails15),
        ]

    checks = [
        ("好样本应当全过", not fails_good, "未过: %s" % fails_good),
        ("反例1 缺打点名必被抓到", any("打点名齐全" in f for f in fails1), "抓到: %s" % fails1),
        ("反例2 错时钟基准必被抓到", any("时钟基准" in f for f in fails2), "抓到: %s" % fails2),
        ("反例3 编 S10 必被抓到", any("S10" in f for f in fails3), "抓到: %s" % fails3),
        ("反例4 缩放律塞回 ×4.32 必被抓到", any("t_compose" in f for f in fails4), "抓到: %s" % fails4),
        ("ISS-215 好样本应当全过", not fails215, "未过: %s" % fails215),
        ("ISS-215 反例5 整机 2.32 混进 demo 表必被抓到",
         any("整机口径 token 必须显式标注" in f or "demo 活动口径表数据行" in f for f in fails5),
         "抓到: %s" % fails5),
        ("ISS-215 反例6 删掉 7.79 必被抓到",
         any("demo 活动口径必含项" in f for f in fails6), "抓到: %s" % fails6),
        ("ISS-215 反例7 拆掉占位区标记必被抓到",
         any("整机口径 token 必须显式标注" in f or "分区标记" in f for f in fails7), "抓到: %s" % fails7),
        ("ISS-215 反例8 10.09 失去身份必被抓到",
         any("10.09" in f for f in fails8), "抓到: %s" % fails8),
    ] + checks221
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
        verdict = read(VERDICT)
        triage = read(TRIAGE215)
    except CheckError as e:
        print("❌ %s" % e)
        return 2

    res = check_spec(spec)
    res += check_display_reanchor({
        "SW/DEMO_OD_TIMING_SPEC.md": spec,
        "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md": verdict,
        "triage": triage,
    })
    res += check_demo_budget_source({
        "SW/DEMO_OD_TIMING_SPEC.md": spec,
        "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md": verdict,
    })
    passed = sum(1 for _, ok, _ in res if ok)
    if a.json:
        print(json.dumps({
            "spec": "SW/DEMO_OD_TIMING_SPEC.md",
            "specs": ["SW/DEMO_OD_TIMING_SPEC.md", "SW/DEMO_BOARD_60MS_VERDICT_PLAN.md",
                      "SW/DEMO_60MS_DISPLAY_REANCHOR_TRIAGE.md"],
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
