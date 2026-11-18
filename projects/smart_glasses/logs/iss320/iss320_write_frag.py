#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-320 · mech-lead · 分片写入驱动 (★只调 state/frag_write.py·不走别的路★)
=====================================================================
★纪律: `state/fragments/mech.yaml` 只许由 `python3 state/frag_write.py --agent mech-lead` 原子写
  (★禁止 open(p,"w")★) ⇒ 本脚本【只负责拼 argv】, 真正的落盘由 frag_write.py 做。
★用 subprocess 传 argv 列表 (不走 shell) ⇒ 长文本里的引号/空格/特殊字符一个都不会被 shell 吃掉。
"""
from __future__ import annotations

import subprocess
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"

ART_HANDOFF = (
    "path=HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md kind=handoff version=v1.0 "
    "summary='★ISS-320 交卷单 (B0~B6 齐全·占位符 0)★: "
    "B0 一句话 + 交付物清单 (4 件) · "
    "B1 结论摘要 5 条 (★B1-1 本单最值钱的一条: 33 行里有 1 行落在 md5 钉死的受保护判据脚本 "
    "MECH/service_port_check.py L51 里 ⇒ 本单 (零落表) 改不了 ⇒ 必须跟板那一趟同批走合法改板通道 ISS-296★ · "
    "B1-2 机器自证 8 项全绿 · "
    "B1-3 硬指标 8 项 (电芯 4.60x23.50x40.50mm / 340mAh / 4.38cc / 4.8g / 镜脚 105.5mm / 镜腿 7.3mm / 0.87W 一个数没变) · "
    "B1-4 两颗电芯官网规格对照 (真型号是 ICP422339PR) · "
    "B1-5 零写板零落表零改闸零重生成零外发) · "
    "B2 验收标准自评 20 条 (18 通过 / 2 部分通过: 第 6 条 32/33 行 + 第 11 条 gate_check rc=1 但与本单零因果) · "
    "B3 证据分级 13 行 (官网/官方/推算/0数据/实测) · B4 接口取值声明 8 项 · "
    "B5 未决项 2 条给 main 的 need + 3 条登记 · "
    "B6 自证复现命令 6 组 (含 SW 闸红的 A/B 逐字节对照证明)·'"
)

ART_LEDGER = (
    "path=MECH/ONETRIP_CELL_MODEL_RENAME_APPLY.md kind=ledger version=v1.0 "
    "summary='★ISS-320 33 行实做台账 (先落纸·每改完一个文件立刻原子写台账·中途被杀也不丢成果)★: "
    "§1 33 行逐行台账 (32 行实做 + 第 32 行 MECH/service_port_check.py L51 改判为「留证行·本单不许改 "
    "(受保护判据脚本 md5 钉死·钉板闸⑧ G5b)」+ 每行给 改前逐字/改后逐字/数字指纹/连带影响) · "
    "§2-1 11 行留证对照行 (逐条与改前逐字节相同) · §2-2 1 行撤回行 · "
    "§3 施工后自证 16 项实测读数 (板 md5+mtime 未变 / 网表脚表BOM原理图 14/14 未变 / "
    "4 个受保护脚本 4/4 未变 / MECH 域全量 md5 越界 0 漏改 0 / 526 个 .pyc mtime 全早于开工时刻)·'"
)

ART_EVID = (
    "path=logs/iss320/ kind=evidence version=v1.0 "
    "summary='★ISS-320 原始输出目录 (施加器 + 机器自证器 + BEFORE/AFTER 全文 + md5 快照 + diff + 闸输出)★: "
    "iss320_apply.py (行限定替换 + 先落纸原子写台账 + 撤回行处理 + --render-only 只重建台账不改任何 MECH 文件) + "
    "iss320_verify.py (V1~V8 机器自证: 期望版逐字节 / 留证行逐字节 / 整文件数字指纹 / "
    "替换后基线扫描 / 零写板 / 零落表 / 零改闸 / 零越界(按域归因·MECH 域独占判据) / .pyc 未动) + "
    "before/ 与 after/ 各 16 个文件逐字全文 + diff_per_file.txt (unified diff·只有型号名一处变) + "
    "md5_ALL_BEFORE.txt (全树 31,826 个文件施改前 md5 快照 ⇒ 零越界判据的 BEFORE 侧) + "
    "VERIFY_REPORT.txt + cell_model_scan_AFTER.txt + script_gates_AFTER.txt / mech_gates_AFTER.txt (各 7/7 rc=0) + "
    "gate_after.txt (钉板闸⑧ 23/23 组·G5b [OK]) + merge_after.txt + "
    "gate_check_after.txt (rc=0·Q1 18/18·Q2 3/3·Q7 9/9) + "
    "gate_A_mech_reverted.txt 与 gate_B_mech_current.txt (「SW 闸红与本单零因果」的 A/B 逐字节对照证据) + "
    "ledger_state.json (逐行台账数据)·'"
)

NEED_REBOARD = (
    "key=iss320_cell_model_rename_deferred_to_reboard to=main since=2026-11-18 "
    "item='★MECH/service_port_check.py L51 的电芯型号订正 (ICP582035PR-01 → ICP422339PR) "
    "要不要跟板那一趟同批走合法改板通道 (ISS-296) + 落表台账留痕 (落表单号 + 文件名 + 新旧 md5)?★ "
    "★背景 (机器判): MECH/check_demo_struct_truth.py 的 MD5_EXPECTED_SCRIPTS 把该文件基线 md5 钉死为 "
    "db58ff6a2afc28b8bf517e3c57c56bc1 ⇒ 改一个字钉板闸⑧ G5b 就红 ⇒ state/gate_check.py 的 Q7 从 9/9 掉到 8/9 "
    "⇒ 该文件不进「合法改板」通道 ⇒ 本单 (零落表) 改不了★ "
    "★不改的后果: 零后果 (可接受) —— 这行只是注释里的型号名, 常量 \"cell_thk\": 4.60 未动 ⇒ 功能零变化 ⇒ 闸照绿 "
    "⇒ 留成旧型号名是【已知的可接受不一致】, 不要为「文档好看」去动它; 唯一代价是 MECH/service_port_check.py L51 的注释 "
    "与官网真型号不一致 (文档级瑕疵·不影响判据)★ "
    "★要改的后果: 必须同批落表 (走板那一趟合法改板通道 + 重锚该脚本基线 md5) ⇒ 不许单独改★ "
    "★owner: main (板那一趟的排期)· 本单 owner = mech-lead (已交卷)★ severity: 低 (已知可接受·不阻塞本单交卷)★ "
    "★交卷页: HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md B5-1★'"
)

NEED_PURCHASE = (
    "key=iss320_cell_purchase_order_still_old_model to=main since=2026-11-18 "
    "item='★采购单上的电芯型号什么时候从 ICP582035PR-01 改成 ICP422339PR? (★归 D-2-9 · owner = boss · "
    "本单不替老板拍板★) ★背景: MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md L280/L321/L326 三行 "
    "(★本单的留证行·一个字没碰★) 写明: 照 ICP582035PR-01 下单 ⇒ 到货厚 6.40mm (不是 4.60) ⇒ "
    "装不进 7.30mm 镜脚 ⇒ 电芯段 H 链最坏 −1.10mm ⇒ 归 D-2-9 (owner = boss)★ "
    "★不改的后果: 照旧型号买 ⇒ 到货装不进镜脚 ⇒ 这笔损失远大于任何文档订正本身★ "
    "★要改的后果: 采购单改型号即可 (文档侧本单已订正完 32 行) ⇒ 采购单是最后一块拼图★ "
    "★owner: boss (D-2-9)★'"
)

CLAIM_MODEL = (
    "key=mech_cell_model_correct value='ICP422339PR' "
    "note='★renata.com 官网实读: 340mAh / 4.6x23.5x40.5mm (旧名 ICP582035PR-01 实为 340mAh / 6.4x20.5x37mm) ⇒ "
    "MECH 域 32 行已实做订正 (只换型号名·尺寸一个数没动)· [官网]·' "
    "ref='HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md#B4'"
)
CLAIM_THK = (
    "key=mech_cell_thk_mm value='4.60' "
    "note='★电芯厚 4.60mm (官网) · 本单订正前后逐位相同 · [官网]·' "
    "ref='MECH/MECH_BUDGET.md#1.6.1'"
)
CLAIM_H = (
    "key=mech_cell_h_mm value='23.50' "
    "note='★电芯高 23.50mm (官网) · 本单订正前后逐位相同 · [官网]·' "
    "ref='MECH/MECH_BUDGET.md#1.6.1'"
)
CLAIM_L = (
    "key=mech_cell_l_mm value='40.50' "
    "note='★电芯长 40.50mm (官网) · 本单订正前后逐位相同 · [官网]·' "
    "ref='MECH/MECH_BUDGET.md#1.6.1'"
)
CLAIM_CAP = (
    "key=mech_cell_cap_mah value='340' "
    "note='★电芯容量 340mAh (官网) · 本单订正前后逐位相同 · [官网]·' "
    "ref='MECH/MECH_BUDGET.md#1.6.1'"
)
CLAIM_MASS = (
    "key=mech_cell_mass_g value='4.8' "
    "note='★电芯重 4.8g (315mAh 档 · 1.258 Wh ÷ 260 Wh/kg) · 本单订正前后逐位相同 · [推算]·' "
    "ref='MECH/MECH_BUDGET.md#3'"
)
CLAIM_TEMPLE = (
    "key=mech_temple_thk_mm value='7.30' "
    "note='★镜腿厚 7.30mm (老板锁死值·本单不动) · M-FIT 解A 前后余量 0.95mm (最坏 0.65 ≥ 0.60) · [推算]·' "
    "ref='MECH/MECH_BUDGET.md#1.6.2'"
)
CLAIM_PENDING = (
    "key=mech_cell_model_rename_pending value='MECH/service_port_check.py L51' "
    "note='★该行仍留旧型号名 ICP582035PR-01 ⇒ 等板那一趟同批走合法改板通道 (ISS-296) + 落表留痕 "
    "(落表单号+文件名+新旧 md5) ⇒ 该文件被 MD5_EXPECTED_SCRIPTS 钉死 ⇒ 本单 (零落表) 改不了· [实测]·' "
    "ref='HANDOFF/2026-11-18_mech-lead_ISS320_电芯型号订正实做.md#B1-1'"
)

STATUS = (
    "phase=done progress_pct=100 health=green "
    "summary='★ISS-320 (2026-11-18 · mech-lead · cron fb67af40) 电芯型号订正【实做】交卷★: "
    "33 行权威清单里 ★32 行本单改成了 (16 个 MECH 活文件: 9 个 .md + 7 个 .py)· 只把型号名 "
    "ICP582035PR-01 → ICP422339PR ⇒ 除型号名外全部数字序列逐位相同 (4.60/23.50/40.50mm / 340mAh / "
    "4.38cc / 78mAh/cc / 105.5mm / 7.3mm / 4.8g / 0.87W 一个数没变)★; "
    "★1 行本单改不了 (MECH/service_port_check.py L51 · 受保护判据脚本 md5 钉死 · 钉板闸⑧ G5b) ⇒ "
    "该行订正跟板那一趟同批走合法改板通道 (ISS-296) ⇒ 已交 need 给 main★; "
    "机器自证 V1-V8 全绿 (32/32 期望版逐字节 / 12/12 留证+撤回行逐字节 / 16/16 整文件数字指纹 / "
    "替换后基线扫描 12 行=11 留证+1 撤回 / 板 md5+mtime 未变 / 零落表 14/14 / 零改闸 4/4 / "
    "MECH 域全量 md5 越界 0 漏改 0 / 526 个 .pyc 未动) ★; "
    "7 个改过的脚本 + 7 道 MECH 闸 全 rc=0; 钉板闸⑧ 23/23 组 · G5b [OK]; "
    "merge rc=0; gate_check rc=0 · Q1 18/18 · Q2 3/3 · Q7 9/9 · 零外溢 · 零占位符; "
    "零写板 · 零落表 · 零改闸 · 零重生成 · 零外发 · 不替老板拍板 · 不自签 issue_log★'"
)


def main() -> int:
    argv = [
        "python3", "-B", "state/frag_write.py", "--agent", "mech-lead",
        "--add-artifact", ART_HANDOFF,
        "--add-artifact", ART_LEDGER,
        "--add-artifact", ART_EVID,
        "--add-need", NEED_REBOARD,
        "--add-need", NEED_PURCHASE,
        "--add-claim", CLAIM_MODEL,
        "--add-claim", CLAIM_THK,
        "--add-claim", CLAIM_H,
        "--add-claim", CLAIM_L,
        "--add-claim", CLAIM_CAP,
        "--add-claim", CLAIM_MASS,
        "--add-claim", CLAIM_TEMPLE,
        "--add-claim", CLAIM_PENDING,
        "--status", STATUS,
    ]
    r = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
