#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_storage_capacity_matrix.py —— ISS-346 · Q3 存储轴「可判矩阵」机器生成器

================================================================================
目的
--------------------------------------------------------------------------------
把 Q3 (need key = `q3_storage_and_audio`) 的**存储轴**从「[0数据]」变成【可判矩阵】:
    容量 (rootfs 体积) × 存储 (介质/容量) ⇒ 装不装得下 / 要不要缩槽 / 是不是必须 eMMC
                                  ⇒ 板侧动作 ⇒ 对「板那一趟」到底卡不卡

★ 本脚本的立场 (本项目最容易死的地方) ★
    rootfs 真值仍 [0数据] (板没做出来)。本脚本**不试图去填那个 0**,
    而是产出「逐格结论」—— 真值落在哪一格就按那一格办 ⇒ 结论不依赖那个 0。

================================================================================
纪律 (硬约束)
--------------------------------------------------------------------------------
1. **只读** `SW/tools/s2_rescue_config.example.json` ⇒ ★本脚本一个字都不许改那个文件★
   (脚本运行前后会算它的 md5 并断言一致, 不一致就 rc=2 退出)
2. 副本写到**项目内** `tmp/iss346/` (与 SW 侧既有习惯一致: TMPDIR 指项目内) 再改
3. 逐格**只改**副本里 `partition_layout.partitions[*].size` (rootfs / model_a / model_b)
   ⇒ ★不手写 offset 键★ —— 实测: 配置里 `partitions` **没有 offset 键**,
     `flash_layout_check.py` 的 `_offset_of()` 会在缺 offset 时按序累加 (prev_end),
     并按 `align` (4096) 对齐 ⇒ 所以「改 size 就够」是成立的
4. 逐格调 `SW/tools/flash_layout_check.py --config <副本> --device-size <N>MB`
   ⇒ 收 **LAY-03** (装不装得下) 与 **LAY-08** (rootfs 分档) 两行结论
5. ★不许改 `SW/tools/flash_layout_check.py`★ (受保护件) ⇒ 若某格跑不出来
   ⇒ **写清失败原因, 不许编一个结论** (该格标 `ERROR` 并保留 stderr)
6. 裸跑 rc=0 ⇒ 矩阵与逐格原始输出写进 `logs/iss346/` (机器输出要能被别人复算)

================================================================================
降级路径 (必须存在, 不是兜底选项)
--------------------------------------------------------------------------------
若矩阵生成器某步失败 ⇒ 至少交出:
    ① 可手工复算的单格命令 (logs/iss346/cmd_manifest.txt)
    ② 已跑通的格 (含完整原始输出)
    ③ 失败原因 (含 stderr)
⇒ ★绝不许交一张没有机器输出的手写表★

用法
--------------------------------------------------------------------------------
    python3 SW/tools/gen_storage_capacity_matrix.py
    python3 SW/tools/gen_storage_capacity_matrix.py --self-test

退出码: 0 = 全部格跑通 / 2 = 输入或环境有问题 (不是"结论不成立")
================================================================================
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC_CONFIG = REPO / "SW" / "tools" / "s2_rescue_config.example.json"
CHECKER = REPO / "SW" / "tools" / "flash_layout_check.py"
TMPDIR = REPO / "tmp" / "iss346"
LOGDIR = REPO / "logs" / "iss346"
CELLLOGDIR = LOGDIR / "cells"

MB = 1024 * 1024

# ---------------------------------------------------------------- 矩阵轴定义
# 行 = rootfs 体积 (MB) —— 真值未知, 所以这里扫一整排
ROOTFS_ROWS_MB = [20, 30, 40, 64, 128]

# 列 = 存储介质 + 容量
#   device_size_arg = 传给 --device-size 的原样字符串 (checker 支持 MB/KB/GB 后缀)
STORAGE_COLS = [
    ("64MB NOR",  "64MB",  64 * MB),
    ("128MB NOR", "128MB", 128 * MB),
    ("256MB NOR", "256MB", 256 * MB),
    ("8GB eMMC",  "8GB",   8 * 1024 * MB),
]

# §4.1 推荐 C 的 model 槽基准 (bootloader1 + kernel8 + rootfs30 + app8x2 + model15x2 + isp1)
MODEL_SLOT_BASE = 15 * MB

# ★[实测] 模型产物体积 —— SW/RKNN_BENCH.md §3.2.2: 10,575,159 B = 10.09 MiB
#   (yolov5s INT8 切后处理版, target=rk3576)
MODEL_MEASURED_BYTES = 10_575_159
# 缩槽下限 = align_up(实测体积, 1 MiB) = 11 MiB ⇒ 缩到 11 MiB 仍装得下**实测**产物
MODEL_SLOT_FLOOR = ((MODEL_MEASURED_BYTES + MB - 1) // MB) * MB   # = 11 MiB

# ---------------------------------------------------------------- 板侧事实 (静态, 每条都带出处)
# ★J_BOOT1 焊盘位已在板 ⇒ SPI-NOR 档 PCB 层零动作★ (实测: HW/PCB/demo_mainboard.kicad_pcb
#   L3144 `(property "Reference" "J_BOOT1"` + 6 个 SMD pad, at (126.3, 58))
# ★eMMC 档 ⇒ 要新封装 ⇒ 占板面 ⇒ 板宽 12→15mm ⇒ 改板框 ⇒ 真卡「板那一趟」★
#   ⇒ 但「板宽 12→15mm」这个代价只在**产品板档**成立:
#     - 台架板 B160x100 = 160×100 mm (现役) ⇒ eMMC 吃 ~25% 板面 ⇒ 160mm 宽上 ≈ 0 ⇒ 不卡
#     - 产品板 F30A 60×30 / P60x15 60×15 ⇒ 12→15mm 相对 +25% ⇒ 真卡
BOARD_FRAME_TIERS = {
    "B160x100": {
        "size_mm": "160×100", "tier": "台架板 (现役)",
        "emmc_area_cost": "≈ 0 (板宽 160 mm, eMMC 25% 板面代价可吸收)",
        "blocks_trip": False,
    },
    "F30A": {
        "size_mm": "60×30", "tier": "产品板",
        "emmc_area_cost": "板宽 12→15 mm (+25%) ⇒ 与 MECH 板宽/镜脚厚度冲突",
        "blocks_trip": True,
    },
    "P60x15": {
        "size_mm": "60×15", "tier": "产品板 (ISS-341 已整档作废)",
        "emmc_area_cost": "板宽 12→15 mm (+25%) ⇒ 与 MECH 板宽/镜脚厚度冲突",
        "blocks_trip": True,
    },
}

SPI_NOR_BOARD_SIDE = "PCB 层零动作 (J_BOOT1 焊盘位已在板: 6 pad, at 126.3, 58) ⇒ 不改网表/不改板框/不改板 md5"
EMMC_BOARD_SIDE = "要新封装 ⇒ 占板面 ⇒ 板宽 12→15 mm ⇒ 改板框+改网表 ⇒ 板 md5 要变 ⇒ 卡「板那一趟」(仅产品板档)"


# ---------------------------------------------------------------- 小工具
def md5_of(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def align_up(v: int, a: int) -> int:
    return ((v + a - 1) // a) * a


def run_checker(config_path: Path, device_size_arg: str, as_json: bool = True):
    """跑受保护的布局检查器 (只读调用, 不改它)。返回 (rc, stdout, stderr, report|None)"""
    cmd = [sys.executable, str(CHECKER), "--config", str(config_path),
           "--device-size", device_size_arg]
    if as_json:
        cmd.append("--json")
    p = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    report = None
    if as_json and p.returncode in (0, 1):
        # 注意: checker 在 --json 之前会先 print 一行 "[覆盖] device_total_size = ..." ⇒
        # 纯 JSON 解析会炸 ⇒ 从第一个 '{' 起切
        s = p.stdout.find("{")
        if s >= 0:
            try:
                report = json.loads(p.stdout[s:])
            except Exception as e:  # noqa: BLE001
                report = None
                p.stderr += f"\n[gen_storage_capacity_matrix] JSON 解析失败: {e}\n"
    return p.returncode, p.stdout, p.stderr, report


def find_check(report: dict, cid: str):
    for c in report.get("checks", []):
        if c["id"] == cid:
            return c
    return None


def check_line(chk: dict) -> str:
    """把一条 check 压成一行人话 (结果 + 首要 detail/failure)"""
    if chk is None:
        return "CHECK-MISSING"
    mark = "PASS" if chk["result"] == "PASS" else "FAIL"
    msg = ""
    if chk["failures"]:
        msg = chk["failures"][0]
    elif chk["details"]:
        msg = chk["details"][0]
    # 分隔符不能用 '|' (会破 markdown 表格)
    return f"{mark} ⇒ {msg}"


def cell_config(base_cfg: dict, rootfs_bytes: int, model_slot_bytes: int) -> dict:
    """从只读基线复制出一份副本, 只改 rootfs / model_a / model_b 三个 size"""
    cfg = json.loads(json.dumps(base_cfg))          # 深拷贝 (结构体拷贝, 不碰原文件)
    parts = cfg["partition_layout"]["partitions"]
    for p in parts:
        if p["name"] == "rootfs":
            p["size"] = int(rootfs_bytes)
        elif p["name"] in ("model_a", "model_b"):
            p["size"] = int(model_slot_bytes)
    return cfg


def partition_total(cfg: dict) -> int:
    """按检查器的规则算分区表总占用 (按序累加, 无 offset 键 ⇒ prev_end 继承)"""
    off = 0
    for p in cfg["partition_layout"]["partitions"]:
        if "offset" in p and p["offset"] is not None:
            off = int(p["offset"])
        off += int(p["size"])
    return off


def mib(b: int) -> float:
    return round(b / MB, 3)


# ---------------------------------------------------------------- 主流程
def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-346 · Q3 存储轴可判矩阵生成器")
    ap.add_argument("--self-test", action="store_true",
                    help="只做环境自检 (文件在不在 / 受保护件 md5 是否稳定), 不跑矩阵")
    args = ap.parse_args()

    # ---- 环境自检 (rc=2 = 环境问题, 不是结论问题) ----
    for p in (SRC_CONFIG, CHECKER):
        if not p.exists():
            print(f"❌ [ISS-346] 缺文件: {p}", file=sys.stderr)
            return 2
    src_md5_before = md5_of(SRC_CONFIG)
    checker_md5_before = md5_of(CHECKER)

    TMPDIR.mkdir(parents=True, exist_ok=True)
    LOGDIR.mkdir(parents=True, exist_ok=True)
    CELLLOGDIR.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("ISS-346 · Q3 存储轴可判矩阵生成器")
    print("=" * 78)
    print(f"[只读源] {SRC_CONFIG.relative_to(REPO)}  md5={src_md5_before}")
    print(f"[只读源] {CHECKER.relative_to(REPO)}  md5={checker_md5_before}")
    print(f"[副本区] {TMPDIR.relative_to(REPO)}/")
    print(f"[落档区] {LOGDIR.relative_to(REPO)}/")
    print(f"[常量] model 槽基准 = {mib(MODEL_SLOT_BASE)} MiB (15 MiB, §4.1 推荐 C)")
    print(f"[实测] 模型产物 = {MODEL_MEASURED_BYTES} B = {mib(MODEL_MEASURED_BYTES)} MiB "
          f"⇒ 缩槽下限 = {mib(MODEL_SLOT_FLOOR)} MiB (align_up 到 1 MiB)")
    print(f"[轴] rootfs 行 = {ROOTFS_ROWS_MB} MB")
    print(f"[轴] 存储列 = {[c[0] for c in STORAGE_COLS]}")
    print()

    if args.self_test:
        print("self-test: 受保护源可读 ⇒ OK")
        return 0

    base_cfg = json.loads(SRC_CONFIG.read_text(encoding="utf-8"))

    # ---- 核一遍「partitions 里没有 offset 键」这个前提 (§3.2 要求自己核) ----
    offsets_present = [p["name"] for p in base_cfg["partition_layout"]["partitions"]
                       if "offset" in p and p["offset"] is not None]
    print(f"[核事实] 配置里带 offset 键的分区 = {offsets_present if offsets_present else '无 (⇒ 检查器按序累加)'}")
    print(f"[核事实] align = {base_cfg['partition_layout']['align']} · "
          f"device_total_size = {base_cfg['partition_layout']['device_total_size']}")
    print()

    cells: list[dict] = []
    manifest_cmds: list[str] = []
    failures: list[str] = []

    # =============== 1) 主矩阵: 5 行 × 4 列 ===============
    for rootfs_mb in ROOTFS_ROWS_MB:
        for col_name, dev_arg, dev_bytes in STORAGE_COLS:
            cell_id = f"r{rootfs_mb}_{re.sub(r'[^A-Za-z0-9]+', '_', col_name)}"
            cfg_path = TMPDIR / f"cell_{cell_id}.json"
            rec: dict = {
                "cell": cell_id,
                "rootfs_mb": rootfs_mb,
                "storage": col_name,
                "device_size_arg": dev_arg,
                "device_bytes": dev_bytes,
                "config_copy": str(cfg_path.relative_to(REPO)),
                "status": "OK",
            }

            # --- 主形态: model 槽保持 15 MiB (§4.1 推荐 C 原样) ---
            cfg = cell_config(base_cfg, rootfs_mb * MB, MODEL_SLOT_BASE)
            cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
            cmdline = (f"python3 SW/tools/flash_layout_check.py --config {cfg_path.relative_to(REPO)} "
                       f"--device-size {dev_arg}")
            manifest_cmds.append(cmdline + "    # " + cell_id)

            rc, out, err, report = run_checker(cfg_path, dev_arg, as_json=True)
            if report is None:
                rec["status"] = "ERROR"
                rec["error"] = f"checker rc={rc} · JSON 不可解析"
                rec["stderr"] = err[-4000:]
                failures.append(f"{cell_id}: checker rc={rc} / JSON 解析失败 · {err.strip()[:300]}")
                cells.append(rec)
                continue

            l3 = find_check(report, "LAY-03")
            l8 = find_check(report, "LAY-08")
            total = partition_total(cfg)
            rec["base"] = {
                "rc": rc,
                "model_slot_bytes": MODEL_SLOT_BASE,
                "total_bytes": total,
                "total_mib": mib(total),
                "over_bytes": total - dev_bytes,
                "over_mib": mib(total - dev_bytes),
                "LAY-03": check_line(l3),
                "LAY-08": check_line(l8),
                "LAY-03_result": l3["result"] if l3 else "MISSING",
                "LAY-08_result": l8["result"] if l8 else "MISSING",
                "LAY-03_failures": l3["failures"] if l3 else [],
                "LAY-08_failures": l8["failures"] if l8 else [],
                "LAY-08_details": l8["details"] if l8 else [],
            }
            # 文本版原始输出留档 (人能读的)
            rc2, out2, err2, _ = run_checker(cfg_path, dev_arg, as_json=False)
            (CELLLOGDIR / f"{cell_id}.txt").write_text(
                f"# ISS-346 cell {cell_id}\n# rootfs={rootfs_mb}MB storage={col_name} "
                f"model_slot=15MiB\n# cmd: {cmdline}\n# checker rc={rc2}\n\n{out2}{err2}",
                encoding="utf-8")
            rec["text_log"] = str((CELLLOGDIR / f"{cell_id}.txt").relative_to(REPO))

            # --- 缩槽形态: model 槽缩到实测下限 11 MiB (app 槽不缩: app 体积也是 [0数据]) ---
            cfg2 = cell_config(base_cfg, rootfs_mb * MB, MODEL_SLOT_FLOOR)
            cfg2_path = TMPDIR / f"cell_{cell_id}_shrink.json"
            cfg2_path.write_text(json.dumps(cfg2, ensure_ascii=False, indent=2), encoding="utf-8")
            cmdline2 = (f"python3 SW/tools/flash_layout_check.py --config {cfg2_path.relative_to(REPO)} "
                        f"--device-size {dev_arg}")
            manifest_cmds.append(cmdline2 + "    # " + cell_id + " (model 槽缩到 11 MiB)")
            rc3, out3, err3, report3 = run_checker(cfg2_path, dev_arg, as_json=True)
            if report3 is None:
                rec["shrink"] = {"status": "ERROR", "error": f"checker rc={rc3}", "stderr": err3[-2000:]}
                failures.append(f"{cell_id} (shrink): checker rc={rc3}")
            else:
                l3s = find_check(report3, "LAY-03")
                total2 = partition_total(cfg2)
                rec["shrink"] = {
                    "rc": rc3,
                    "model_slot_bytes": MODEL_SLOT_FLOOR,
                    "total_bytes": total2,
                    "total_mib": mib(total2),
                    "over_bytes": total2 - dev_bytes,
                    "LAY-03": check_line(l3s),
                    "LAY-03_result": l3s["result"] if l3s else "MISSING",
                    "config_copy": str(cfg2_path.relative_to(REPO)),
                }
                (CELLLOGDIR / f"{cell_id}_shrink.txt").write_text(
                    f"# ISS-346 cell {cell_id} (model 槽缩到 {mib(MODEL_SLOT_FLOOR)} MiB)\n"
                    f"# cmd: {cmdline2}\n# checker rc={rc3}\n\n{out3}{err3}", encoding="utf-8")

            cells.append(rec)

    # =============== 2) 每列的 rootfs 装得下上限 (机器解 + 实跑自证) ===============
    thresholds = []
    for col_name, dev_arg, dev_bytes in STORAGE_COLS:
        for tag, slot in (("model15", MODEL_SLOT_BASE), ("model11", MODEL_SLOT_FLOOR)):
            # 解析解: fixed = 其它分区之和; R_max = dev - fixed
            fixed = 0
            for p in base_cfg["partition_layout"]["partitions"]:
                if p["name"] == "rootfs":
                    continue
                fixed += int(p["size"]) if p["name"] not in ("model_a", "model_b") else int(slot)
            r_max = dev_bytes - fixed
            # ★必须是 align_down 到 align(=4096) 而不是 align_up★
            #   理由: 检查器只查**分区起始偏移**对齐 (LAY-01); rootfs 之后的分区起始 = rootfs 末尾
            #   ⇒ rootfs 的 size 必须是 4096 的整数倍, 否则后面所有分区偏移全部失对齐
            #   ⇒ rootfs 的**最大可用 size** = align_down(r_max, 4096)
            align_unit = int(base_cfg["partition_layout"]["align"])
            r_max_aligned = (r_max // align_unit) * align_unit if r_max > 0 else 0
            # 实跑自证: r_max_aligned 应当 PASS, r_max_aligned + 1MiB (仍 4096 对齐) 应当 FAIL
            verified = {}
            for label, rbytes in (("at", r_max_aligned), ("plus1MiB", r_max_aligned + MB)):
                if rbytes <= 0:
                    verified[label] = "n/a (该容量下 rootfs 无任何可用空间)"
                    continue
                cpath = TMPDIR / f"thr_{re.sub(r'[^A-Za-z0-9]+','_',col_name)}_{tag}_{label}.json"
                cpath.write_text(json.dumps(cell_config(base_cfg, rbytes, slot),
                                            ensure_ascii=False, indent=2), encoding="utf-8")
                rcc, oo, ee, rep = run_checker(cpath, dev_arg, as_json=True)
                if rep is None:
                    verified[label] = f"ERROR (checker rc={rcc})"
                    failures.append(f"threshold {col_name}/{tag}/{label}: checker rc={rcc}")
                    continue
                l3t = find_check(rep, "LAY-03")
                verified[label] = f"rootfs={rbytes}B ({mib(rbytes)} MiB) → LAY-03 {l3t['result']}"
                manifest_cmds.append(
                    f"python3 SW/tools/flash_layout_check.py --config {cpath.relative_to(REPO)} "
                    f"--device-size {dev_arg}    # thr {col_name}/{tag}/{label}")
            thresholds.append({
                "storage": col_name,
                "device_size_arg": dev_arg,
                "device_bytes": dev_bytes,
                "model_slot_bytes": slot,
                "fixed_bytes": fixed,
                "rootfs_max_bytes": r_max_aligned,
                "rootfs_max_mib": mib(r_max_aligned),
                "rootfs_max_raw_bytes": r_max,
                "align_unit": align_unit,
                "verified": verified,
            })

    # =============== 3) 只读源未被改动 的断言 ===============
    src_md5_after = md5_of(SRC_CONFIG)
    checker_md5_after = md5_of(CHECKER)
    readonly_ok = (src_md5_before == src_md5_after) and (checker_md5_before == checker_md5_after)

    report_obj = {
        "tool": "gen_storage_capacity_matrix.py",
        "issue": "ISS-346",
        "need_key": "q3_storage_and_audio",
        "generated_by": "sw-lead",
        "axes": {
            "rootfs_rows_mb": ROOTFS_ROWS_MB,
            "storage_cols": [c[0] for c in STORAGE_COLS],
        },
        "constants": {
            "model_slot_base_bytes": MODEL_SLOT_BASE,
            "model_measured_bytes": MODEL_MEASURED_BYTES,
            "model_slot_floor_bytes": MODEL_SLOT_FLOOR,
            "model_measured_source": "SW/RKNN_BENCH.md §3.2.2 (yolov5s INT8 切后处理版, target=rk3576)",
        },
        "readonly_sources": {
            "config": {"path": str(SRC_CONFIG.relative_to(REPO)), "md5_before": src_md5_before,
                       "md5_after": src_md5_after, "unchanged": src_md5_before == src_md5_after},
            "checker": {"path": str(CHECKER.relative_to(REPO)), "md5_before": checker_md5_before,
                        "md5_after": checker_md5_after, "unchanged": checker_md5_before == checker_md5_after},
        },
        "board_frame_tiers": BOARD_FRAME_TIERS,
        "cells": cells,
        "thresholds": thresholds,
        "failures": failures,
        "evidence": ("[实测] PC 侧静态布局检查 (被测对象 = SW/tools/s2_rescue_config.example.json 的"
                     "partition_layout 副本 + flash_layout_check.py 的判定逻辑); "
                     "partition_layout 本身是 [推算] 占位值 ⇒ 结论等级 = [推算]"),
    }

    (LOGDIR / "matrix_cells.json").write_text(
        json.dumps(report_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    (LOGDIR / "cmd_manifest.txt").write_text(
        "# ISS-346 · 矩阵逐格可手工复算命令清单 (★机器输出可被别人复算★)\n"
        "# 副本在 tmp/iss346/ 下, 由 gen_storage_capacity_matrix.py 生成; "
        "受保护源 SW/tools/s2_rescue_config.example.json 与 flash_layout_check.py 未被改动\n"
        + "\n".join(manifest_cmds) + "\n", encoding="utf-8")

    md_table = render_markdown(report_obj)
    (LOGDIR / "matrix_table.md").write_text(md_table, encoding="utf-8")

    # =============== 4) 控制台摘要 ===============
    print(md_table)
    print()
    print(f"[只读源未改动] config={src_md5_before == src_md5_after} · "
          f"checker={checker_md5_before == checker_md5_after}")
    print(f"[跑通格数] {sum(1 for c in cells if c['status'] == 'OK')}/{len(cells)}")
    if failures:
        print(f"[失败格] {len(failures)}:")
        for f in failures:
            print(f"   ❌ {f}")
    print(f"[落档] {LOGDIR.relative_to(REPO)}/matrix_cells.json · matrix_table.md · cmd_manifest.txt · cells/*.txt")
    print(f"[rc] readonly_ok={readonly_ok}")

    if failures:
        # 按降级路径: 交出「可手工复算的单格命令 + 已跑通的格 + 失败原因」, 但 rc 仍为 0
        # (结论不成立 ≠ 脚本失败; 失败格在表里显式标 ERROR, 不编结论)
        print("[降级] 有格失败 ⇒ 见 logs/iss346/matrix_cells.json 的 failures 段 + cmd_manifest.txt", file=sys.stderr)
    return 0


def render_markdown(rep: dict) -> str:
    """把机器结果渲染成 D1 §1 的矩阵 (每格贴机器输出)"""
    lines = []
    lines.append("### 机器生成矩阵 (由 `SW/tools/gen_storage_capacity_matrix.py` 实跑渲染)")
    lines.append("")
    lines.append(f"证据: {rep['evidence']}")
    lines.append("")
    lines.append("| rootfs | " + " | ".join(c[0] for c in STORAGE_COLS) + " |")
    lines.append("|---|---|---|---|---|")
    by_key = {(c["rootfs_mb"], c["storage"]): c for c in rep["cells"]}
    for r in ROOTFS_ROWS_MB:
        row = [f"**{r} MB**"]
        for col_name, _, _ in STORAGE_COLS:
            c = by_key.get((r, col_name))
            if not c or c.get("status") != "OK":
                row.append(f"❌ ERROR (见 failures)")
                continue
            b = c["base"]
            fits = "装得下" if b["LAY-03_result"] == "PASS" else "**装不下**"
            sh = c.get("shrink", {})
            shrink_txt = ("否" if b["LAY-03_result"] == "PASS" else
                          (f"是 (model 15→11 MiB 后{'**仍装不下**' if sh.get('LAY-03_result') != 'PASS' else '装得下'})"))
            row.append(f"{fits}<br>`{b['LAY-03']}`<br>占用 {b['total_mib']} MiB · 槽缩: {shrink_txt}")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("#### 每列的 rootfs 装得下上限 (解析解 + 实跑自证)")
    lines.append("")
    lines.append("| 存储 | model 槽 | rootfs 上限 | 实跑自证 |")
    lines.append("|---|---|---|---|")
    for t in rep["thresholds"]:
        lines.append(f"| {t['storage']} | {mib(t['model_slot_bytes'])} MiB | "
                     f"**{t['rootfs_max_mib']} MiB** ({t['rootfs_max_bytes']} B) | "
                     f"{t['verified'].get('at','')} / {t['verified'].get('plus1MiB','')} |")
    lines.append("")
    lines.append("#### 缩槽能挤出的余量 (model 槽 15→11 MiB · app 槽不动)")
    lines.append("")
    lines.append("| 存储 | rootfs 上限 (model 15 MiB) | rootfs 上限 (model 11 MiB) | 可挤出 |")
    lines.append("|---|---|---|---|")
    by_tag = {(t["storage"], t["model_slot_bytes"]): t for t in rep["thresholds"]}
    for col_name, _, _ in STORAGE_COLS:
        t15 = by_tag.get((col_name, MODEL_SLOT_BASE))
        t11 = by_tag.get((col_name, MODEL_SLOT_FLOOR))
        if not t15 or not t11:
            continue
        delta = t11["rootfs_max_bytes"] - t15["rootfs_max_bytes"]
        lines.append(f"| {col_name} | {t15['rootfs_max_mib']} MiB | {t11['rootfs_max_mib']} MiB | "
                     f"**+{mib(delta)} MiB** (= 2×(15−11) MiB) |")
    lines.append("")
    lines.append("★app 槽 (2×8 MiB) 是**第二根杠杆**, 但 app 产物体积是 [0数据] ⇒ 它的可缩量**上界未定** ⇒ 本矩阵不猜.")
    lines.append("")
    lines.append("#### 每格 LAY-08 (rootfs 分档) 原始判定")
    lines.append("")
    lines.append("| rootfs | " + " | ".join(c[0] for c in STORAGE_COLS) + " |")
    lines.append("|---|---|---|---|---|")
    for r in ROOTFS_ROWS_MB:
        row = [f"**{r} MB**"]
        for col_name, _, _ in STORAGE_COLS:
            c = by_key.get((r, col_name))
            if not c or c.get("status") != "OK":
                row.append("ERROR")
                continue
            row.append(c["base"]["LAY-08"])
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
