#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把被 kill 的那两个会话的 brief 精华, 补进 issue_log 的 task_brief (供下一轮队列派活用)。

★为什么: 2026-10-29 09:1x 我手动派活与队列 cron 撞车 → 我 kill 了自己那两个会话 →
  cron 那三条 (ISS-112/113/027) 用的是 issue_log 里原有的短 brief;
  ⇒ 我手动 brief 里的两处增量必须**写回 issue_log**, 否则下一轮队列派活会丢掉:
    ① ISS-113: ★"必须先删掉 /tmp/rknn_bench 再跑 §7 命令"的干净机器自证要求
    ② ISS-111: 我那份 brief 里的完整上下文 (工况出处 / 判据要求 / 交付物清单)

用法: python3 state/_patch_briefs_20261029.py [--dry-run]
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

PATCH = {
    "ISS-113": (
        "\n\n★2026-10-29 09:1x 项目总工追加 (自证纪律): 你必须**先把 /tmp/rknn_bench 整个删掉**, "
        "再逐条跑 SW/RKNN_BENCH.md §7 里列出的命令, 并把**每条命令的实测输出**贴进回复 —— "
        "★我本人就是被『文档写得像能跑、实际跑不了』坑的 (§7 把 `acc` 列为可单独执行, "
        "实际干净机器上直接 AssertionError 崩在 rknn_bench.py:626, 因为 dataset.txt 由 calib 步生成)。"
        "★另外给个参考数: 我补跑 calib 后用 `--images 293` 得到 286 张有标注图 / F1 INT8 0.3129 / "
        "FP32 0.3172 / Δ−0.0044; 你报告里 `--images 300` 对应 293 张 / 0.3139 / 0.3182 / Δ−0.0043 ⇒ "
        "★**取图张数不同会小幅改变 F1, 报告里的数不用改, 但 §7 里要把 --images 写清楚**。"
    ),
    "ISS-111": (
        "\n\n★2026-10-29 09:1x 项目总工补充 brief (我手动派的那版被队列 cron 撞车后 kill 了, 增量在此):\n"
        "【B.1 逐项要写满的字段】测什么 / 怎么测 (设备 + 工装 + 样品数 + 次数) / **判据 (量化阈值, 不要"
        "『外观无异常』这种)** / 测不过怎么办 (回退哪一版) / 状态标 [未验]。\n"
        "【覆盖这 6 类 (RELIABILITY_DESIGN §2.2 已列为『必须等样机』)】跌落 / 振动 / 弯折 / 热 / 焊点 / 连接器寿命。\n"
        "【★工况不许重写 —— 直接引用已写死的那套】跌落 1.0m 自由跌落, 6 面各 1 次 + 4 角各 1 次 = 10 次每台 × 3 台 = 30 次; "
        "随机振动 5-200Hz PSD 0.005g²/Hz + 2g rms 扫频; 弯折 100 次/天 → 5 年 182,500 次, 弯折半径 R≥3.0mm。\n"
        "【交付物】HW/EVT_RELIABILITY_TEST_ITEMS.md (新建) + HANDOFF/2026-10-29_hw-lead_ISS111_EVT可靠性实测项清单.md (B1-B6)。\n"
        "【边界】只写 HW/EVT_RELIABILITY_TEST_ITEMS.md 一个新文件 + 交接单; 不许改既有 HW 文档; "
        "不许碰 state/ 下任何文件 (分片由项目总工代写)。"
    ),
    "ISS-112": (
        "\n\n★2026-10-29 09:1x 项目总工追加 (官方证据已由我独立查证, 直接引用不用再查): TI 官网产品页 "
        "→ 'WQFN (RTW) | 24 | 16 mm² (4 mm × 4 mm)'; 订购页 → 'WQFN (RTW) 24, -40 to 85'; "
        "datasheet 封装附录 (SLUSC76C) → 订单型号只有 BQ25896RTWR / RTWT / RTWR.A / RTWR.B。\n"
        "★**库内网表/原理图本来就是 24 脚** (HW/SCHEMATIC_V1.md 有『全 24 脚对照』表 + 'U_CHG pin24 NC'), "
        "库内引用到的脚位 = pin1/4/5/6/10/11/13/14/16/17/18/19/22/23/24 ⇒ **是文档与网表互相矛盾, 不是网表错**。\n"
        "★A.2 你**可以**改 state/gen_netlist.py 里的器件封装字符串 (那是生成器数据, 不是状态源), "
        "但**不许碰** state/fragments/ 下任何文件、不许碰 STATE.yaml、不许碰 state/issue_log.yaml。\n"
        "★A.3 是本任务的重点: 给我一个**明确的数** (充电板多少 mm² / 扣掉这 7mm² 还剩多少 / 够不够摆), "
        "不够就给 3 条腾挪方案 (每条写: 挪什么 / 省几 mm² / 代价 / 对应改哪份文档), 不要写『大概』。\n"
        "★A.4 复核 24 脚 pinout 与网表引用有无错位; 你改不动的写进『未决项』, **不要自己改网表连接关系**。"
    ),
}


def main() -> int:
    dry = "--dry-run" in sys.argv
    with open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc.get("issues")
    items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])

    hit = 0
    for it in items:
        iid = it.get("id") if isinstance(it, dict) else None
        if iid not in PATCH:
            continue
        hit += 1
        brief = str(it.get("task_brief") or "")
        add = PATCH[iid]
        if add.strip() in brief:
            print(f"[skip] {iid} 已打过补丁")
            continue
        it["task_brief"] = brief + add
        print(f"[patch] {iid} task_brief +{len(add)} B → {len(it['task_brief'])} B")

    if hit != len(PATCH):
        print(f"❌ 命中 {hit} 条, 期望 {len(PATCH)} 条 —— 中止, 不落盘")
        return 2
    if dry:
        print("[dry-run] 未落盘")
        return 0

    doc["issues"] = items
    text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)
    fd, tmp = tempfile.mkstemp(prefix="issue_log.yaml.", suffix=".tmp", dir=HERE)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, LOG)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    print("✅ issue_log.yaml task_brief 补丁已原子落盘")
    return 0


if __name__ == "__main__":
    sys.exit(main())
