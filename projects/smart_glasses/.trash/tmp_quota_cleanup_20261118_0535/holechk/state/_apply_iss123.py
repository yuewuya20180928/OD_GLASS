#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性脚本: 给 s2_rescue_config{,.example}.json 加 identity 段 + 显式 sector_size 参数 (ISS-123)"""
import json
import os
from collections import OrderedDict

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
TOOLS = os.path.join(_ROOT, "projects", "smart_glasses", "SW", "tools")

IDENTITY = OrderedDict([
    ("_readme", [
        "★★ ISS-123: 版本块 magic 与版本串前缀的**唯一真源** —— 代码里不再写死。",
        "★ 原来写死的是: 版本块 magic = b'AR45' (flash_writer.py) · 版本串行首 = 'ARS45-SW ' (s2_board_judge.py / s2_board_selftest.py)。",
        "★ 基线已翻案 (RK3588 → RK3576, 见 PROJECT_TRACKER §(1.46)/(1.47) + HW/CHIP_SELECTION_DECISION.md §0) ⇒ 这两个值必须能改, 且**改一处就够**。",
        "★ 改这一段 = 改全链路: flash_writer 写入 / judge 判定 / 板端自检提取 / preflight 检查 / 问询清单回填。",
        "★ 板端 /etc/version 的生成模板与本文件是**两个落点** (FLASH_AND_VERSION §3.1.3), 改前缀时两边都要改 —— 但**代码**只认这里。"
    ]),
    ("version_block_magic", "RK35"),
    ("version_block_magic_len", 4),
    ("version_block_magic_basis", [
        "[推算] 版本块 magic 是**项目自有**的 4 字节标签 (SW/FLASH_AND_VERSION.md §3.2: 'magic (4B)'),",
        "  原值 'AR45' 取自**已作废**的酷芯微 ARS45 (老板 10-29 19:20 拍板 ARS45/AR9481/酷芯微全部作废)",
        "  ⇒ 基线翻到瑞芯微 RK3576 后, 家族短标签取 'RK35' (瑞芯微 RK35xx 系列短标签写法: RK3528/RK3566/RK3568/RK3576/RK3588 同族前缀 'RK35')。",
        "★ 宽度仍 4 字节 ⇒ §3.2 版本块二进制布局 (magic@0x000 / payload_len@0x004 / flags@0x006 / ... / payload_crc32@0x278) **零改动**。",
        "★ 选 'RK35' 而不是 'RK76' 的理由: RK35 是**系列**标签 ⇒ 万一基线再翻回 RK3588, 这一项**不用再改**。",
        "★★ 待裁决: 本项目**尚无板、无已刷镜像** ⇒ 改 magic 的兼容成本 = 0。真正取值待模组厂给出「版本/元数据分区」格式后由项目总工裁决 (P4)。",
        "★ 要回退到旧值: 改这一个字段即可, 代码/文档零改动。"
    ]),
    ("version_str_prefix", "ARS45-SW "),
    ("version_str_prefix_basis", [
        "[推算·文档] 这段是**产品代号** (PROJECT_TRACKER 标题 'ARS45 Smart Glasses'), **不是** SoC 型号",
        "  ⇒ 换芯 (ARS45 芯片 → RK3576) **不构成**改它的理由; 软件版本前缀不该跟着芯片型号走。",
        "★ 老板 10-29 19:20 'ARS45/AR9481/酷芯微 作废' 指的是**芯片与方案商**, 眼镜**产品代号**是否同步改名**未见拍板**",
        "  ⇒ 本单**不擅自改名**, 保持原值作默认值 (不脑补)。若 boss 决定改产品代号 ⇒ 改这一个字段 + 板端 /etc/version 生成模板, 代码零改动。",
        "★ 已登记 needs: s2_product_codename (to=main, waiting_on=boss)。",
        "★ 前缀末尾的空格是**格式的一部分** (行首 'ARS45-SW ' + 合法 semver), 别删。"
    ]),
])

SECTOR_BLOCK = OrderedDict([
    ("sector_size", 512),
    ("sector_size_basis", [
        "[官方·瑞芯微分区文档] 瑞芯微 parameter.txt 的 mtdparts **十六进制写法** (0x<size>@0x<offset>(name)) 的单位是**扇区**, 1 扇区 = 512 字节。",
        "  三处独立一致: 九鼎 Rockchip 官方文档英译 'The unit of all values is sector, and one sector is 512 bytes' / armsom 'All values use sectors of 512Bytes' / Vicharak RK3399 parameter.txt 实例。",
        "★★ 但同族还有**后缀方言** (8M@9M(boot)) ⇒ 数值单位是**字节** (M=MiB), sector_size 在那种文件里**不参与换算**。",
        "  ⇒ 单位由**文件方言**决定, 所以本字段是**显式参数**而不是代码里的常量; 默认 512 只在十六进制扇区方言下成立。",
        "  ★ 拿到模组厂的表**先确认方言** (问询清单 §4 Q4.2c 强制问单位 + 方言), 换算一律走 SW/tools/s2_partition_convert.py。"
    ]),
    ("size_unit", "bytes"),
    ("size_unit_basis", "我方内部单位**恒为字节** (partitions[].size / device_total_size 都是字节) ⇒ 扇区只允许出现在**换算的输入端**。"),
    ("expected_total_bytes", 90210304),
    ("expected_total_bytes_basis", [
        "[推算] §4.1 条件式推荐 C 的容量算术: bootloader 1 + kernel 8 + rootfs 30 + app 8×2 + model 15×2 + isp 1 = 86 MiB, + version_block 32 KiB ⇒ 90210304 B。",
        "★ 守卫用它抓 **÷512 方向**的错 (合计对不上声明值 ⇒ 必是单位错或漏抄); ★换到模组厂的真实表后**必须同步更新**这个值。"
    ]),
    ("vendor_size_unit", None),
    ("vendor_size_unit_basis", "模组厂的表**原样单位**: null = 还没拿到表; 拿到后填 'sector' (十六进制扇区方言) 或 'bytes' (后缀方言), 并同时回填 provenance。"),
    ("provenance", OrderedDict([
        ("converted", False),
        ("converted_with_sector_size", None),
        ("converted_total_bytes", None),
        ("note", "★ 换算留痕: 换算完必须回填这三个字段 (s2_partition_convert.py --parse 直接产出可粘贴的 JSON)。"
                 "★ 守卫会核对「换算时用的 sector_size」与「配置里写的 sector_size」是否一致 —— 不一致 ⇒ 报错 (表就是错的)。")
    ])),
    ("vendor_min_align", 32768),
    ("vendor_min_align_basis", "[官方·瑞芯微分区文档] 'every partition start must be aligned to 32KB (64 sectors), and its size must be a multiple of 32KB' ⇒ 模组厂的表按 32 KiB 对齐复核。"),
])


def patch(path: str, is_example: bool) -> None:
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f, object_pairs_hook=OrderedDict)

    # --- identity 段插到 params 之前 (顶层顺序: _readme, identity, params, ...) ---
    if "identity" not in d:
        new = OrderedDict()
        for k, v in d.items():
            if k == "params":
                new["identity"] = IDENTITY
            new[k] = v
        if "identity" not in new:
            new["identity"] = IDENTITY
        d = new

    # --- partition_layout 加扇区/字节参数 ---
    pl = d["partition_layout"]
    new_pl = OrderedDict()
    for k, v in pl.items():
        new_pl[k] = v
        if k == "device_total_size":
            for sk, sv in SECTOR_BLOCK.items():
                new_pl[sk] = sv
    if "sector_size" not in new_pl:
        for sk, sv in SECTOR_BLOCK.items():
            new_pl[sk] = sv
    d["partition_layout"] = new_pl

    # --- _readme 加一条 ISS-123 说明 ---
    rm = d.get("_readme")
    if isinstance(rm, list):
        rm.insert(1, "★★ ISS-123 (2026-11-01): magic / 版本串前缀 / 扇区单位 三处硬编码已抽成**可配置** —— 见 identity 段 + partition_layout.sector_size。")
        if not is_example:
            rm.insert(2, "   ★ 基线 = 瑞芯微 RK3576 (RK3588 → RK3576, ISS-118 T4 翻案) ⇒ 问询对象 = **RK3576 模组厂**, 见 SW/S2_VENDOR_QUESTION_LIST.md v2.0。")
    elif isinstance(rm, str):
        d["_readme"] = rm + "\n★★ ISS-123: magic / 前缀 / 扇区单位已抽成可配置 (identity 段 + partition_layout.sector_size)。"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"✅ 已更新: {path}")


if __name__ == "__main__":
    patch(os.path.join(TOOLS, "s2_rescue_config.json"), False)
    patch(os.path.join(TOOLS, "s2_rescue_config.example.json"), True)
