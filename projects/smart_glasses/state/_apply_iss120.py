#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-120 交卷: status fixing → fixed + 填 fix_ref (sw-lead 自己推进状态)
原子写 issue_log.yaml (tmp + os.replace), 只改 ISS-120 一条, 不动别人的条目。
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f)

issues = doc.get("issues")
items = list(issues.values()) if isinstance(issues, dict) else issues

FIX_REF = (
    "SW/S2_BOARD_TEST_CHECKLIST.md (① 执行清单: CB-01~09 九条机械判据 + BR-01~12 十二条用例 + "
    "S2连挂2次→S3 失败决策树, 每条写死「执行前置/判定口径/记录字段/谁判过」四栏) + "
    "SW/S2_VENDOR_QUESTION_LIST.md (② 原厂问询清单: P1~P4 各一节「问什么/什么格式回/填进 "
    "s2_rescue_config 的哪个字段」, 交项目总工外发) + "
    "SW/tools/s2_board_run.sh (③ 一条命令跑测: 读配置→6步跑测→自动出 CB-01~09+BR-01 判定, "
    "失败自动抓串口日志/下载工具版本/电流表读数) + SW/tools/s2_board_judge.py + "
    "SW/tools/s2_board_selftest.sh/.py + SW/tools/s2_board_e2e.sh + SW/tools/s2_rescue_config.json + "
    "HANDOFF/2026-10-30_sw-lead_ISS120_S2板端实测准备.md (B1-B6)"
)

NOTE = """
★2026-10-30 00:3x sw-lead 交卷 (状态 fixing → fixed, **板端实测仍未做**):
【交付三件套 (全在 SW/ 下)】① **SW/S2_BOARD_TEST_CHECKLIST.md** (18.9KB) — EVT-8/BR-01 可勾选执行清单: CB-01~09 九条机械判据 + BR-01~12 十二条用例, **每条写死「执行前置 / 判定口径 / 记录字段 / 谁判过」四栏**并带 ☐; S2 连挂 2 次→S3 失败决策树 (6 行 + 硬规则, 升级/判 S4 由项目总工裁决); 工位准备表 (器材/软件/人员) + 三态判定栏 + 追溯字段。判据与 EVT §11.2/§11.5 一一对应, 未增未减。
② **SW/S2_VENDOR_QUESTION_LIST.md** (19KB) — P1_BOOT_ENTER_SPEC / P2_DL_TOOL / P3_USB_PHY / P4_BOOT_STORE 四节, 每节三栏: **问什么 / 什么格式回 (给对方的可直接填的表格) / 拿到后填进 s2_rescue_config 的哪个字段 (精确到 JSON 路径)**; 附 ISS-119 换芯口径分叉 (§0.2 线路A模组厂 / 线路B ARS45供应商) + RK3588 公开工具链事实作**提问靶子** (§5.1, 标了出处且明写"不能直接抄进配置") + 与既有 7 条 needs_from 的对应关系 (§6, 避免重复问) + 回填自检 5 条命令 (§7)。**★ sw-lead 未联系任何原厂/供应商/模组厂 —— 本件是交项目总工的外发草稿。**
③ **SW/tools/s2_board_run.sh 一条命令跑测** (+ s2_board_judge.py 判定器 + s2_board_selftest.sh/.py 板端自检 + s2_board_e2e.sh 端到端自检 + s2_rescue_config.json 板端实跑配置) — 读配置 (P1~P4 不齐 → rc=3 并逐条列缺哪几个 + 指向问询清单对应节, **不降级**) → 6 步跑测 (正常态基线 → 进 BOOT → 刷写 → 回读校验 → 板端自检 → 重启3次 → 刷后重新枚举) → 证据按 EVT §11.7 的文件名落盘 → 自动出 CB-01~09 + BR-01 三态判定; **任一步失败自动抓现场: 串口日志 / 下载工具版本 / 电流表读数** (取不到就记 [0数据], 脚本绝不编数)。
【★本单最有价值的产出 = 把 ISS-080 的口径从"文档承诺"变成"代码强制"】判定器 4 条硬规则: ①**缺失即判未验, 绝不判 PASS** ②**generic-example 签名不算证据**; 且**签名表里没有真值签名时 CB-01 也判未验** —— "不再匹配任何 BOOT 签名"在空签名表下是**空判** (本轮 e2e 实测抓出并已修, 固化成自测 T7) ③**P4 未填 ⇒ CB-06 判未验** (不许拿 [推算] 占位分区表判回读 CRC 通过) ④**仅日志特征命中不算进 BOOT**。4 条反例全部固化成自测。
【★顺手查出一个必须先裁决的口径冲突】ISS-119 (10-29) 已把 SoC 基线从 ARS45 换成 RK3588 (RK3576 为可机械触发的翻转后手; HW/CHIP_SELECTION_DECISION.md, **verify_by=boss 待老板点头**), 但 S2 全套文档/工具链仍按 ARS45 写 ⇒ ①flash_writer.py 版本块 magic 写死 `AR45` + 版本串行首写死 `ARS45-SW ` ②RK3588 分区表用 parameter.txt (**按 512B 扇区计, 我方按字节 ⇒ 差 512 倍**) ③**问谁变了** (从 ARS45 供应商变成模组厂/板级设计方)。**我未拍板**, 已写进清单 §0.2 + 问询清单 §0.2/§5, 并登记 needs `s2_chip_swap_scope` (to=main, waiting_on=boss, due 2026-11-10) 请项目总工裁决 —— **分叉没定就发信会问错对象, 白等一轮**。
【★状态诚实声明】**板端 S2 实测仍 0 次**, P1~P4 四个 [0数据] 项在 SW/tools/s2_rescue_config.json 里**仍是 value=null / status=TODO, 一个都没填** ⇒ 按 EVT §11.4 R2, BR-01 现在**最高只能判 ⚠️未验**, 该板不得进产线。**本单交付的是"怎么测 + 怎么问 + 怎么判", 不是"测过了"。**
【自证复现】bash SW/tools/s2_board_run.sh --selftest → **rc=0 (6/6)**; python3 SW/tools/s2_board_judge.py --selftest → **rc=0 (7/7, 含 4 条反例)**; bash SW/tools/s2_board_e2e.sh → **rc=0 (10/10)**; bash SW/tools/s2_board_selftest.sh --selftest → **rc=0 (5/5)**; bash SW/tools/s2_selftest.sh (ISS-080 既有) → **rc=0 (10/10, 未被破坏)**; preflight 真配置 → **rc=3** + 逐条列缺 P1~P4; forensics 真跑 → 5 个下载工具版本**全记 [0数据] 命令不在 PATH** + 电流表 value_ma=null + 串口 0 字节 (**没编一个数**); python3 state/merge.py → **rc=0 (冲突 0)**; python3 state/gate_check.py → **Q1 18/18**。
【未决 (已登记 needs)】`s2_chip_swap_scope` (换芯口径裁决, to=main/boss, due 11-10) / `s2_vendor_inquiry_draft` (请项目总工外发问询清单 + 并行催 hw-lead 的 fw_boot_mode_hw / fw_boot_storage_bom, due 11-05) / `s2_param_fill_backfill` (板端回读通道 + 工厂标定台账, due 11-10)。板端自检 6 项的实际命令 (board_test.selftest.*) 仍全 null, 需板端可执行环境信息。
【验证】**verify_by=main** —— BR-01 是否判过、EVT §11.4 的"量产一票否决"是否解除, 由项目总工签; 修复人不能自验。
"""

changed = []
for it in items:
    if it.get("id") != "ISS-120":
        continue
    it["status"] = "fixed"
    it["fix_ref"] = FIX_REF
    it["note"] = (it.get("note") or "") + "\n" + NOTE
    changed.append(it.get("id"))

if not changed:
    print("❌ 没找到 ISS-120")
    sys.exit(1)

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

print(f"✅ 已推进: {changed} (status=fixed, fix_ref 已填)")
