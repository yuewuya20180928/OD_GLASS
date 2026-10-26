#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
flash_writer.py —— 分区写入 + 版本块原子写 (S2 救砖链路的 PC 侧仿真载体)

================================================================================
这是 SW/FLASH_AND_VERSION.md §4.5 的机器可读附件之一。

它干什么
--------------------------------------------------------------------------------
把 §2.5.2 的"先内容、后标志"烧录顺序做成**可执行、可断电注入、可回读校验**的一段
代码, 并且**不依赖任何硬件**: 目标可以是一个普通文件 (当作"假 flash"), 也可以是
一个 loop 设备。所以没有板子的时候, S2 链路里最容易出事的软件部分 (写入顺序 /
原子性 / CRC / 版本块字段完整性) 现在就能先验一遍。

它干什么 (以及明确不干什么)
--------------------------------------------------------------------------------
✅ 做的: 分区写入 (按分区表) / 各分区 CRC32 计算 / 版本块 payload 写 / magic +
        bootable 标志最后写 / 回读校验 (magic、bootable、mode、SN、calib、版本串
        6 分项非空、分区 CRC 一致) / 断电注入 (--fail-after)
❌ 不做的: 不调用任何原厂下载工具 (P2 = [0数据]); 不碰真实块设备 (除非显式
        --allow-real-device, 本项目永不传); 不假装知道 ARS45 的真实分区表
        (partition_layout 是 [推算] 占位, 待 P4)

子命令
--------------------------------------------------------------------------------
    write   写镜像 + 版本块 (payload → magic/bootable 两步)
    verify  回读校验 (刷回来的判据 CB-02 / CB-03 / CB-06 的机器实现)
    inject  只做断电注入 (等价于 write --fail-after <分区>)

用法
--------------------------------------------------------------------------------
    # 1) 用合成镜像写一个 128MB 的"假 flash"文件
    python3 SW/tools/flash_writer.py write \
        --config SW/tools/s2_rescue_config.example.json \
        --target /tmp/ars45_flash.img --synth

    # 2) 回读校验
    python3 SW/tools/flash_writer.py verify \
        --config SW/tools/s2_rescue_config.example.json \
        --target /tmp/ars45_flash.img

    # 3) 断电注入: 写到 model_a 就断电 (模拟写到一半掉电)
    python3 SW/tools/flash_writer.py write \
        --config SW/tools/s2_rescue_config.example.json \
        --target /tmp/ars45_flash_cut.img --synth --fail-after model_a
    python3 SW/tools/flash_writer.py verify \
        --config SW/tools/s2_rescue_config.example.json \
        --target /tmp/ars45_flash_cut.img     # 期望: 判"未生效" (magic 缺失 / bootable=0)

退出码
--------------------------------------------------------------------------------
    0 = 成功 (write 写完 / verify 全部通过)
    1 = 校验不通过 (verify 发现不一致)
    2 = 参数或环境错误
    5 = 断电注入触发 (故意中止, 用于验证原子性)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import zlib

MAGIC = b"AR45"
BOOTABLE_BIT = 0x01
MODE_NAMES = {"dev": 0, "prod": 1, "service": 2}
MODE_VALUES = {v: k for k, v in MODE_NAMES.items()}

# 版本块二进制布局 (与 flash_layout_check.py 同源, 与 §3.2 字段表一一对应)
VB = {
    "magic": 0x000,
    "payload_len": 0x004,
    "flags": 0x006,
    "mode": 0x007,
    "boot_count_a": 0x008,
    "boot_count_b": 0x00C,
    "active_slot": 0x010,
    "build_time": 0x012,
    "sn": 0x01A,
    "calib_id": 0x02A,
    "tool_ver": 0x04A,
    "partition_crc": 0x060,
    "version_str": 0x078,
    "payload_crc32": 0x278,
}
VERSION_STR_MAX = 512
CRC_SLOT_COUNT = 6


# ----------------------------------------------------------------------------- 工具函数
def synth_image(path: str, size: int) -> bytes:
    """合成确定性镜像 (无真实固件时用): 内容只取决于文件名与大小, 可复现。"""
    buf = bytearray()
    seed = hashlib.sha256(os.path.basename(path).encode()).digest()
    block = bytes(seed)
    while len(buf) < size:
        buf.extend(block)
        block = hashlib.sha256(block).digest()
    return bytes(buf[:size])


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def partition_plan(layout: dict) -> list[dict]:
    parts = list(layout.get("partitions", []))
    off = 0
    plan = []
    for p in parts:
        off = int(p.get("offset") if p.get("offset") is not None else off)
        plan.append({
            "name": p["name"],
            "offset": off,
            "size": int(p["size"]),
            "file": p.get("file"),
            "crc_slot": p.get("crc_slot"),
            "slot": p.get("slot"),
        })
        off += int(p["size"])
    return plan


def active_partitions(plan: list[dict], active_slot: str) -> list[dict]:
    """A/B 槽: 只取活动槽那一路参与 CRC 计算 (对应 §4.1 方案 C)。"""
    out = []
    for p in plan:
        if p["slot"] is None:
            out.append(p)
        elif p["slot"] == active_slot:
            out.append(p)
    return out


def build_version_block(meta: dict, crc_values: list[int], active_slot: str) -> tuple[bytes, bytes]:
    """
    返回 (payload, final_block):
      payload    —— 不含 magic、不含 bootable 标志的那一版 (此时 magic 区填 0xFF)
      final_block —— payload + magic + flags(bootable) + payload CRC, 最后写
    写入顺序铁律 (§2.5.2): 先写 payload, 最后写 magic + bootable。
    """
    version = str(meta.get("version", "")).encode("utf-8")
    if len(version) > VERSION_STR_MAX:
        raise SystemExit(f"版本串超长 {len(version)}B > {VERSION_STR_MAX}B")
    sn = str(meta.get("sn", "")).encode("utf-8")[:16]
    calib = str(meta.get("calib_id", "")).encode("utf-8")[:32]
    tool = str(meta.get("tool_ver", "")).encode("utf-8")[:16]
    mode = MODE_NAMES.get(str(meta.get("mode", "dev")), 0)
    build_time = int(meta.get("build_time", 0))

    payload = bytearray(b"\xFF" * 32768)
    struct.pack_into("<H", payload, VB["payload_len"], len(version))
    payload[VB["mode"]] = mode
    struct.pack_into("<Q", payload, VB["build_time"], build_time)
    payload[VB["sn"]:VB["sn"] + len(sn)] = sn
    payload[VB["calib_id"]:VB["calib_id"] + len(calib)] = calib
    payload[VB["tool_ver"]:VB["tool_ver"] + len(tool)] = tool
    payload[VB["active_slot"]] = 0 if active_slot == "a" else 1
    for i in range(CRC_SLOT_COUNT):
        struct.pack_into("<I", payload, VB["partition_crc"] + 4 * i, int(crc_values[i]))
    payload[VB["version_str"]:VB["version_str"] + len(version)] = version

    # payload CRC 覆盖 [payload_len .. payload_crc32) 这段有效载荷
    crc_start = VB["payload_len"]
    crc_end = VB["payload_crc32"]
    pcrc = zlib.crc32(bytes(payload[crc_start:crc_end])) & 0xFFFFFFFF
    struct.pack_into("<I", payload, VB["payload_crc32"], pcrc)

    final = bytearray(payload)
    final[VB["magic"]:VB["magic"] + 4] = MAGIC
    final[VB["flags"]] = BOOTABLE_BIT
    return bytes(payload), bytes(final)


def crc_of_region(fh, offset: int, size: int) -> int:
    fh.seek(offset)
    remaining = size
    crc = 0
    while remaining > 0:
        chunk = fh.read(min(1 << 20, remaining))
        if not chunk:
            break
        crc = zlib.crc32(chunk, crc)
        remaining -= len(chunk)
    return crc & 0xFFFFFFFF


# ----------------------------------------------------------------------------- write
def cmd_write(args, cfg: dict) -> int:
    layout = cfg.get("partition_layout", {})
    total = int(layout.get("device_total_size", 0))
    align = int(layout.get("align", 4096))
    active_slot = layout.get("active_slot", "a")
    plan = partition_plan(layout)
    meta = cfg.get("version_meta", {})

    target = args.target
    if not target.endswith(".img") and not args.allow_real_device:
        # 真实块设备 (无扩展名) 一律拒绝, 除非显式放行
        if os.path.exists(target) and not target.startswith("/dev/loop"):
            print(f"❌ 拒绝写非镜像文件目标 {target} (加 --allow-real-device 才放行)", file=sys.stderr)
            return 2
    if os.path.exists(target) and os.path.isfile(target) and not args.truncate:
        os.unlink(target)

    with open(target, "wb") as fh:
        fh.truncate(total)
        # 擦除态: 全 0xFF
        fh.seek(0)
        block = b"\xFF" * (1 << 20)
        for _ in range(total // (1 << 20)):
            fh.write(block)

        crc_values = [0] * CRC_SLOT_COUNT
        written = []
        for p in plan:
            if p["name"] == "version_block":
                continue
            img_path = p["file"] or ""
            if args.images:
                img_path = os.path.join(args.images, img_path)
            data = None
            if img_path and os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    data = f.read()
            elif args.synth:
                data = synth_image(p["name"], p["size"])
            else:
                print(f"❌ 缺镜像 {img_path} (用 --synth 生成合成镜像)", file=sys.stderr)
                return 2
            if len(data) > p["size"]:
                print(f"❌ 镜像 {p['name']} 大小 {len(data)} > 分区 {p['size']}", file=sys.stderr)
                return 2
            data = data + b"\xFF" * (p["size"] - len(data))
            fh.seek(p["offset"])
            fh.write(data)
            crc = zlib.crc32(data) & 0xFFFFFFFF
            if p["crc_slot"] is not None:
                crc_values[int(p["crc_slot"])] = crc
            written.append({"name": p["name"], "offset": p["offset"], "size": p["size"],
                            "crc32": f"0x{crc:08X}", "slot": p["slot"]})
            if args.fail_after and args.fail_after == p["name"]:
                fh.flush()
                os.fsync(fh.fileno())
                print(f"⚡ 断电注入: 写完 {p['name'] 后中止 (模拟写到一半掉电)", file=sys.stderr)
                print(f"   → 版本块 magic/bootable **未写** → 按 §2.5.2 板端应当拒绝启动", file=sys.stderr)
                return 5

        # ---- 版本块: 两步写 (payload → magic/bootable) ----
        payload, final = build_version_block(meta, crc_values, active_slot)
        vb = next(p for p in plan if p["name"] == "version_block")
        fh.seek(vb["offset"])
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())
        if args.fail_after == "version_block_payload":
            print("⚡ 断电注入: 版本块 payload 写完、magic 未写 → 应判未生效", file=sys.stderr)
            return 5
        fh.seek(vb["offset"])
        fh.write(final)
        fh.flush()
        os.fsync(fh.fileno())

    report = {
        "tool": "flash_writer.py",
        "action": "write",
        "target": target,
        "device_total_size": total,
        "active_slot": active_slot,
        "partitions_written": written,
        "version_block": {
            "offset": vb["offset"],
            "size": vb["size"],
            "magic": "AR45",
            "bootable": 1,
            "mode": meta.get("mode"),
            "sn": meta.get("sn"),
            "calib_id": meta.get("calib_id"),
            "tool_ver": meta.get("tool_ver"),
        },
        "evidence": "[实测] PC 侧仿真 (目标为普通文件, 非真实 flash); 分区表为 [推算] 占位",
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"✅ 写入完成: {target} ({total} B)")
        for w in written:
            print(f"   - {w['name']:<14} off={w['offset']:>10} size={w['size']:>10} crc32={w['crc32']} slot={w['slot']}")
        print(f"   - version_block  off={vb['offset']} size={vb['size']} magic=AR45 bootable=1 "
              f"(最后一步写, §2.5.2)")
    return 0


# ----------------------------------------------------------------------------- verify
def cmd_verify(args, cfg: dict) -> int:
    layout = cfg.get("partition_layout", {})
    active_slot = layout.get("active_slot", "a")
    plan = partition_plan(layout)
    vb = next((p for p in plan if p["name"] == "version_block"), None)
    if vb is None:
        print("❌ 分区表里没有 version_block", file=sys.stderr)
        return 2

    checks: list[tuple[str, bool, str]] = []

    with open(args.target, "rb") as fh:
        fh.seek(vb["offset"])
        block = fh.read(vb["size"])

        magic = block[VB["magic"]:VB["magic"] + 4]
        bootable = block[VB["flags"]] & BOOTABLE_BIT
        checks.append(("CB-02a 版本块 magic == 'AR45'", magic == MAGIC,
                       f"magic={magic!r} (期望 b'AR45')"))
        checks.append(("CB-02b bootable 标志置位", bool(bootable),
                       f"flags=0x{block[VB['flags']]:02X} bootable={bool(bootable)}"))

        mode = MODE_VALUES.get(block[VB["mode"]], "unknown")
        checks.append(("CB-03a mode 字段合法", mode in ("dev", "prod", "service"), f"mode={mode}"))

        vlen = struct.unpack_from("<H", block, VB["payload_len"])[0]
        version = block[VB["version_str"]:VB["version_str"] + vlen].decode("utf-8", "replace")
        checks.append(("CB-03b 版本串非空", vlen > 0, f"version_str_len={vlen}"))

        required = ["boot=", "kern=", "rootfs=", "app=", "model=", "isp="]
        missing = [k for k in required if k not in version]
        checks.append(("CB-03c 版本串 6 分项齐全 (boot/kern/rootfs/app/model/isp)",
                       not missing, f"缺={missing or '无'}"))

        sn = block[VB["sn"]:VB["sn"] + 16].split(b"\x00")[0].decode("utf-8", "replace")
        checks.append(("CB-03d SN 非空", bool(sn), f"sn={sn!r}"))

        calib = block[VB["calib_id"]:VB["calib_id"] + 32].split(b"\x00")[0].decode("utf-8", "replace")
        checks.append(("CB-07  标定 ID 非空 (F6 防线)", bool(calib), f"calib={calib!r}"))

        tool = block[VB["tool_ver"]:VB["tool_ver"] + 16].split(b"\x00")[0].decode("utf-8", "replace")
        checks.append(("CB-03e 烧录工具版本非空", bool(tool), f"tool_ver={tool!r}"))

        stored_crcs = [struct.unpack_from("<I", block, VB["partition_crc"] + 4 * i)[0]
                       for i in range(CRC_SLOT_COUNT)]
        crc_slots = list(layout.get("crc_slots", []))
        for i, p in enumerate(active_partitions(plan, active_slot)):
            if p["crc_slot"] is None:
                continue
            idx = int(p["crc_slot"])
            actual = crc_of_region(fh, p["offset"], p["size"])
            slot_name = crc_slots[idx] if idx < len(crc_slots) else f"#{idx}"
            checks.append((f"CB-06 分区 CRC 一致 [{slot_name}] ({p['name']})",
                           actual == stored_crcs[idx],
                           f"回读=0x{actual:08X} 版本块=0x{stored_crcs[idx]:08X}"))

        pcrc = struct.unpack_from("<I", block, VB["payload_crc32"])[0]
        calc = zlib.crc32(block[VB["payload_len"]:VB["payload_crc32"]]) & 0xFFFFFFFF
        checks.append(("CB-02c 版本块 payload CRC 一致", pcrc == calc,
                       f"存=0x{pcrc:08X} 算=0x{calc:08X}"))

    n_fail = sum(0 if ok else 1 for _, ok, _ in checks)
    report = {
        "tool": "flash_writer.py",
        "action": "verify",
        "target": args.target,
        "checks": [{"name": n, "result": "PASS" if ok else "FAIL", "detail": d} for n, ok, d in checks],
        "result": "PASS" if n_fail == 0 else "FAIL",
        "evidence": "[实测] PC 侧回读校验; 分区表为 [推算] 占位",
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("=" * 78)
        print(f"flash_writer verify: {args.target}")
        print("=" * 78)
        for n, ok, d in checks:
            print(f"{'✅' if ok else '❌'} {n}\n        {d}")
        print("-" * 78)
        print(f"结论: {report['result']} ({len(checks) - n_fail}/{len(checks)} 通过)")
    return 0 if n_fail == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="ARS45 分区写入 + 版本块原子写 (S2 PC 侧仿真)")
    ap.add_argument("action", choices=["write", "verify"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--images", default=None, help="镜像目录 (默认取配置里的相对路径)")
    ap.add_argument("--synth", action="store_true", help="镜像缺失时生成确定性合成镜像")
    ap.add_argument("--truncate", action="store_true", help="目标已存在时先删")
    ap.add_argument("--fail-after", default=None,
                    help="断电注入: 写完该分区后立刻中止 (分区名, 或 'version_block_payload')")
    ap.add_argument("--allow-real-device", action="store_true",
                    help="放行写真实块设备 (本项目禁止使用)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ 配置不存在: {args.config}", file=sys.stderr)
        return 2
    if not os.path.exists(args.target) and args.action == "verify":
        print(f"❌ 目标不存在: {args.target}", file=sys.stderr)
        return 2
    cfg = load_config(args.config)
    if args.action == "write":
        return cmd_write(args, cfg)
    return cmd_verify(args, cfg)


if __name__ == "__main__":
    sys.exit(main())
