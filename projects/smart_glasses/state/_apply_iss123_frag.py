#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-123 交卷: 用 state/frag_write.py 的原子写登记 sw-lead 分片 (不手改 STATE.yaml)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from frag_write import update_fragment  # noqa: E402


def mutate(d):
    # ---------- 1) 关闭 s2_chip_swap_scope (项目总工 11-01 20:5x 裁决: 基线翻案为 RK3576) ----------
    for n in d.setdefault("needs_from", []):
        if n.get("key") == "s2_chip_swap_scope":
            n["decision"] = (
                "基线已翻案: RK3588 → RK3576 (ISS-118 机械判定 54/58 通过/FAIL 4, 硬否决项 = "
                "RK3588 在 60×30mm 板框内摆不下 ⇒ T4 翻案条件命中); 依据 PROJECT_TRACKER.md "
                "§(1.46)/(1.47) + HW/CHIP_SELECTION_DECISION.md §0。★ARS45/AR9481/酷芯微 全部作废 "
                "(老板 10-29 19:20)。⇒ 三个子问题的答案: ①magic/前缀 **抽成可配置** (ISS-123 已改, "
                "默认 RK35 / ARS45-SW , 取值待 P4 裁决) ②分区表按 **RK3576 模组厂 parameter.txt** 重排, "
                "单位差 512 倍已做成**显式参数 + 机械守卫** (ISS-123 已改) ③问询对象 = **RK3576 模组厂** "
                "(ISS-123 已把问询清单整版重写为 v2.0)。"
            )
            n["decided_at"] = "2026-11-01"
            n["closed_ref"] = "SW/S2_VENDOR_QUESTION_LIST.md v2.0 + SW/tools/s2_rescue_config.json#identity"
        if n.get("key") == "s2_vendor_inquiry_draft":
            n["item"] = (
                "★ISS-123 (2026-11-01) 问询清单已按 **RK3576 模组厂** 口径整版重写为 v2.0, 请项目总工外发 "
                "(sw-lead 不直接联系模组厂): SW/S2_VENDOR_QUESTION_LIST.md (P1 进 Maskrom/Loader 条件 / "
                "P2 下载工具与固件包 / P3 USB 下载通路与枚举特征 / P4 启动存储与分区表, 每节仍是"
                "「问什么 / 什么格式回(可填表格) / 拿到后填进 s2_rescue_config 的哪个字段」)。"
                "★v2.0 相对 v1.0 的三处实质变化: ①对象/术语改成瑞芯微口径 (Maskrom/Loader/Rockusb, "
                "SARADC_VIN0_BOOT 电压档位) ②★新增必答项: **parameter.txt 的单位与方言** (扇区 512B? 后缀 K/M/G?) "
                "+ **专用 MaskROM USB 口** + **三个态各自的 VID:PID** ③§4.3 给了「扇区→字节」四步换算法 "
                "(禁止手抄, 一条命令 s2_partition_convert.py --parse)。"
                "★既有 fw_vendor_toolchain / fw_usb_boot_phy / fw_boot_entry_cond / sw_usb_phy_spec 四条 vendor 需求 "
                "due 2026-10-29 已逾期, 本清单是它们的具体化, 不重复问。回填后跑该文 §7 的 7 条自检命令 + preflight。"
            )

    # ---------- 2) 新增 needs ----------
    d.setdefault("needs_from", []).append({
        "key": "s2_product_codename",
        "to": "main",
        "waiting_on": "boss",
        "due": "2026-11-08",
        "since": "2026-11-01",
        "item": (
            "★ISS-123: 眼镜**产品代号**是否随『ARS45/AR9481/酷芯微 作废』(老板 10-29 19:20) 一起改名? "
            "—— 现状: 版本串前缀 `ARS45-SW ` 已从代码硬编码抽成**可配置** (`identity.version_str_prefix`), "
            "但**默认值仍保持 `ARS45-SW ` 未擅自改**, 依据是: 该前缀取自**产品代号** (PROJECT_TRACKER 标题 "
            "'ARS45 Smart Glasses'), **不是** SoC 型号 ⇒ 换芯 (ARS45 芯片 → RK3576) **不构成**改它的理由; "
            "而『ARS45 作废』指的是**芯片与方案商**, 产品代号是否同步改名**未见拍板** ⇒ sw-lead **不脑补**。"
            "★请项目总工请老板明确: ①产品代号保持 ARS45 ②改名 (请给新代号)。裁决后**只改配置一个字段** + "
            "板端 /etc/version 生成模板, 代码零改动。"
        ),
    })
    d.setdefault("needs_from", []).append({
        "key": "s2_version_block_magic_decision",
        "to": "main",
        "waiting_on": "boss",
        "due": "2026-11-08",
        "since": "2026-11-01",
        "item": (
            "★ISS-123: 版本块 magic 的**最终取值**待裁决 —— 现状已从代码写死 b'AR45' 抽成可配置 "
            "(`identity.version_block_magic`), 现默认 **\"RK35\"**, 依据: ①版本块 magic 是**项目自有**的 4 字节标签 "
            "(SW/FLASH_AND_VERSION.md §3.2), 原值 'AR45' 取自**已作废**的酷芯微 ARS45 ②基线翻到 RK3576 ⇒ 家族短标签取 "
            "'RK35' (瑞芯微 RK35xx 系列短标签写法; RK3528/RK3566/RK3568/RK3576/RK3588 同族前缀) ③**宽度仍 4 字节** ⇒ "
            "§3.2 版本块二进制布局零改动 ④★本项目**尚无板、无已刷镜像** ⇒ 改 magic 的兼容成本 = 0。"
            "★待裁决点: 最终取值应等模组厂给出版本/元数据分区格式后定 (P4); 若老板另有指定, 改配置一个字段即可。"
        ),
    })
    d.setdefault("needs_from", []).append({
        "key": "s2_boot_entry_hw_rk3576",
        "to": "main",
        "waiting_on": "agent",
        "due": "2026-11-08",
        "since": "2026-11-01",
        "item": (
            "★ISS-123 连带: 载板上的下载态入口需按 **RK3576** 重核 —— RK3576 的 boot 选择脚是 "
            "**SARADC_VIN0_BOOT** (一个 **ADC 引脚, 用电压档位选启动优先级**), 不是普通 BOOT GPIO; "
            "且官方 MaskROM 模式**只走专用 MaskROM USB 口**。⇒ 我方现有接口声明 "
            "`boot_entry_hw = BOOT-static-strap+上电` (SW/SW_TIMING_REVIEW.md, 按旧 SoC 写的) **需按 RK3576 重核**: "
            "①SARADC_VIN0_BOOT 的电压门限要谁来定 (模组厂给, 还是 hw-lead 按我们选定的档位设计跳线/治具) "
            "②专用 MaskROM USB 口在载板上引不引、走哪个 SoC 引脚 (跨铰链救援通道那侧能否进 Maskrom)。"
            "★已并入问询清单 §1 Q1.1c / §3 Q3.1a, 请项目总工在外发模组厂的同时**并行**转 hw-lead, 两条**不互相等**。"
        ),
    })

    # ---------- 3) interface_claims (跨模块取值, value 必须是短规范值) ----------
    new_claims = [
        {"key": "s2_version_block_magic", "value": "RK35",
         "note": "★ISS-123: 版本块 magic 的唯一真源 = s2_rescue_config.identity.version_block_magic (默认 RK35); "
                 "代码不再写死。宽度 4B ⇒ §3.2 布局零改动。最终取值待 P4/裁决。",
         "ref": "SW/tools/s2_rescue_config.json#identity + SW/tools/flash_writer.py#magic_from_config"},
        {"key": "s2_version_str_prefix", "value": "ARS45-SW",
         "note": "★ISS-123: 版本串前缀的唯一真源 = s2_rescue_config.identity.version_str_prefix (默认 ARS45-SW); "
                 "产品代号性质, 非 SoC 型号 ⇒ 换芯不构成改它的理由; 是否改名待老板拍板 (s2_product_codename)。",
         "ref": "SW/tools/s2_rescue_config.json#identity + SW/tools/s2_board_judge.py#version_regex"},
        {"key": "s2_partition_sector_size", "value": "512",
         "note": "★ISS-123: 扇区↔字节换算的**显式参数** = s2_rescue_config.partition_layout.sector_size; "
                 "依据 瑞芯微 parameter.txt mtdparts 十六进制写法的单位 = 扇区, 1 扇区 = 512 字节 (三处官方文档独立一致); "
                 "★同族另有后缀方言 (8M@9M, 单位=字节) ⇒ 单位由方言决定 ⇒ 必须显式, 拿到模组厂的表先确认方言。",
         "ref": "SW/tools/s2_rescue_config.json#partition_layout + SW/S2_VENDOR_QUESTION_LIST.md §4.3"},
        {"key": "s2_partition_size_unit", "value": "bytes",
         "note": "★ISS-123: 我方内部单位恒为 bytes; 扇区只允许出现在换算的输入端 (守卫 UNIT_NOT_BYTES 拦)。",
         "ref": "SW/tools/s2_partition_convert.py#check_layout"},
        {"key": "s2_partition_guard_rule", "value": "512x-err-blocked-by-check_layout",
         "note": "★ISS-123: ★512 倍差 (parameter.txt 扇区 vs 我方字节) 由 SW/tools/s2_partition_convert.py "
                 "check_layout() **机械拦住** (合计超容量 / 合计≠声明值 / 对齐 / 未换算 / 换算参数不一致 五条判据), "
                 "并固化 2 条反例自测; 不再依赖人肉小心。",
         "ref": "SW/tools/s2_partition_convert.py + SW/tools/s2_iss123_verify.sh"},
        {"key": "s2_vendor_inquiry_target", "value": "RK3576-模组厂",
         "note": "★ISS-123: S2 问询对象 = 瑞芯微 RK3576 模组厂 (ARS45/AR9481/酷芯微 全部作废); "
                 "问询清单已整版重写为 v2.0 (术语/格式/新增必答项)。",
         "ref": "SW/S2_VENDOR_QUESTION_LIST.md v2.0"},
        {"key": "s2_magic_config_key", "value": "identity.version_block_magic",
         "note": "★ISS-123: 版本块 magic 的配置路径 (改这一处即全链路生效)。",
         "ref": "SW/tools/s2_rescue_config.json#identity"},
        {"key": "s2_prefix_config_key", "value": "identity.version_str_prefix",
         "note": "★ISS-123: 版本串前缀的配置路径 (改这一处即全链路生效)。",
         "ref": "SW/tools/s2_rescue_config.json#identity"},
        {"key": "s2_evidence_stale_magic_rule", "value": "magic-mismatch=UNVERIFIED",
         "note": "★ISS-123: 回读报告里记的 magic 与配置不一致 ⇒ 证据已过期 ⇒ CB-02 判未验 (不许判过)。",
         "ref": "SW/tools/s2_board_judge.py#magic_mismatch"},
    ]
    existing = {c.get("key") for c in d.get("interface_claims", [])}
    for c in new_claims:
        if c["key"] not in existing:
            d.setdefault("interface_claims", []).append(c)

    # 更新两条既有 claim 的 note (取值本身不变, 只补来源)
    for c in d.setdefault("interface_claims", []):
        if c.get("key") == "fw_version_format":
            c["note"] = (c.get("note", "") + "。★ISS-123: 前缀已抽成可配置 (identity.version_str_prefix), "
                         "本 claim 的取值仍为默认口径; 改前缀 = 改配置一个字段, 不改代码。")
        if c.get("key") == "s2_partition_source_marker":
            c["note"] = (c.get("note", "") + "。★ISS-123: 单位陷阱已从『文档提醒』升级为**机械守卫** "
                         "(s2_partition_convert.check_layout + 显式 sector_size), 512 倍差不再可能静默发生。")
        if c.get("key") == "boot_entry_hw":
            c["note"] = (c.get("note", "") + "。★ISS-123: ★**该取值按旧 SoC 写的, 需按 RK3576 重核** —— "
                         "RK3576 的 boot 选择脚是 SARADC_VIN0_BOOT (ADC 引脚, 电压档位选启动优先级), "
                         "且官方 MaskROM 只走专用 USB 口 ⇒ 已开 needs s2_boot_entry_hw_rk3576 转项目总工。")

    # ---------- 4) artifacts ----------
    arts = [
        {"path": "SW/tools/s2_partition_convert.py", "kind": "tool", "version": "1.0", "updated_at": "2026-11-01",
         "summary": "★ISS-123 新增: 扇区↔字节换算器 (解析瑞芯微 parameter.txt 的两种方言) + 分区表一致性守卫 "
                    "(6 条判据, ★含 2 条 512 倍反例) + --selftest (14/14)"},
        {"path": "SW/tools/s2_iss123_verify.sh", "kind": "tool", "version": "1.0", "updated_at": "2026-11-01",
         "summary": "★ISS-123 新增: 一条命令自证 (V1~V9: 静态口径/配置口径/换算守卫/往返/既有四件套/ISS-080 既有/状态源), rc=0"},
        {"path": "SW/S2_VENDOR_QUESTION_LIST.md", "kind": "doc", "version": "2.0", "updated_at": "2026-11-01",
         "summary": "★ISS-123 重写: v1.0 (ARS45 原厂口径) 整版作废 ⇒ v2.0 按 **RK3576 模组厂** 口径 "
                    "(对象/术语/格式; 新增 parameter.txt 单位方言 + 专用 MaskROM USB 口 + 三态 VID:PID 必答项)"},
        {"path": "SW/tools/s2_rescue_config.json", "kind": "config", "version": "1.1", "updated_at": "2026-11-01",
         "summary": "★ISS-123: 新增 identity 段 (version_block_magic / version_str_prefix + 各自依据) + "
                    "partition_layout 显式 sector_size / size_unit / expected_total_bytes / provenance"},
        {"path": "SW/tools/flash_writer.py", "kind": "tool", "version": "1.1", "updated_at": "2026-11-01",
         "summary": "★ISS-123: magic 改从配置读 (magic_from_config) + 写入前跑分区表守卫 + verify 报告带 magic (供判过期)"},
        {"path": "SW/tools/s2_board_judge.py", "kind": "tool", "version": "1.1", "updated_at": "2026-11-01",
         "summary": "★ISS-123: 版本串前缀动态化 (version_regex) + 分区表守卫接入 CB-02/CB-06 + 证据过期检测 + "
                    "自测 7/7 → 13/13 (含 2 条 512 倍反例 + magic/前缀可配置用例)"},
        {"path": "SW/tools/s2_board_run.sh", "kind": "tool", "version": "1.1", "updated_at": "2026-11-01",
         "summary": "★ISS-123: preflight 加 identity/sector_size 检查项 + 自测 6/6 → 9/9 (S7 换算守卫 / S8 配置齐全 / S9 真配置守卫)"},
        {"path": "SW/tools/s2_board_e2e.sh", "kind": "tool", "version": "1.1", "updated_at": "2026-11-01",
         "summary": "★ISS-123: 新增 E10~E13 (÷512 反例 / ×512 反例 / 换算守卫 / magic 改后证据过期) + 合成数据改为从真配置取前缀; 10/10 → 14/14"},
        {"path": "SW/tools/s2_board_selftest.py", "kind": "tool", "version": "1.1", "updated_at": "2026-11-01",
         "summary": "★ISS-123: 版本串前缀改从配置读 (version_prefix), 不再写死 'ARS45-SW'"},
        {"path": "SW/S2_BOARD_TEST_CHECKLIST.md", "kind": "doc", "version": "1.1", "updated_at": "2026-11-01",
         "summary": "★ISS-123: §0.2 口径变更提示改写为『已闭环』+ CB-02/CB-03 判定口径改引配置字段 + 风险项 C-5 已闭环 / 新增 C-5b/C-5c"},
    ]
    have = {a.get("path") for a in d.get("artifacts", [])}
    for a in arts:
        if a["path"] in have:
            for old in d["artifacts"]:
                if old.get("path") == a["path"]:
                    old.update(a)
                    break
        else:
            d.setdefault("artifacts", []).append(a)

    # ---------- 5) status ----------
    st = d.setdefault("status", {})
    st["phase"] = "P2(方案设计)"
    st["progress_pct"] = 60
    st["health"] = "yellow"
    st["summary"] = (
        "11-01 ISS-123 闭环 (S2 救砖链路按 RK3576 模组厂口径重写): ①★三处硬编码抽成可配置 —— 版本块 magic "
        "(b'AR45' → 配置 identity.version_block_magic, 默认 'RK35', 4B 宽度 ⇒ §3.2 布局零改动) · 版本串前缀 "
        "('ARS45-SW ' → 配置 identity.version_str_prefix, 保持原值: 它是**产品代号**不是 SoC 型号, 换芯不构成改它的理由) "
        "· 分区表扇区单位 (→ 配置 partition_layout.sector_size 显式参数, 默认 512, 依据瑞芯微分区文档三处独立一致) "
        "②★512 倍差升级为**机械守卫**: 新增 SW/tools/s2_partition_convert.py (parameter.txt 两种方言解析 + 6 条一致性判据 + "
        "2 条 512 倍反例自测 14/14) + flash_writer 写入前拦截 + judge 的 CB-02/CB-06 接入守卫 + 证据过期检测 "
        "③问询清单整版重写 v2.0 = **RK3576 模组厂**口径 (术语 Maskrom/Loader/Rockusb/SARADC_VIN0_BOOT; 新增必答项: "
        "分区表单位与方言 / 专用 MaskROM USB 口 / 三态 VID:PID; §4.3 给出禁止手抄的四步换算法) ④★自证 15/15 全绿: "
        "run.sh 9/9 · judge 13/13 · e2e 14/14 · partition_convert 14/14 · selftest.py 全过 · ISS-080 既有 10/10 未破 "
        "· merge rc=0 冲突 0 · gate Q1 18/18 ⑤★板端实测仍 0 次: P1~P4 四个 [0数据] 项仍 null/TODO ⇒ BR-01 最高只能判 "
        "⚠️未验, 该板不得进产线 ⑥health 仍 yellow: magic 最终取值 / 产品代号改名 / RK3576 下载态入口(SARADC_VIN0_BOOT) "
        "三项待裁决 (已登记 3 条 needs)"
    )


if __name__ == "__main__":
    update_fragment("sw-lead", mutate)
    print("[frag_write] ✅ sw.yaml 已原子更新 → 再跑 python3 state/merge.py")
