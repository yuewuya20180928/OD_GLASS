#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-319 · 把本单条目写进 state/fragments/mech.yaml (★必须走 state/frag_write.py 的原子写★)

★纪律: 本脚本【不】直接写分片文件 —— 它只用 shlex.quote 把参数拼好,
       再由 `python3 state/frag_write.py --agent mech-lead ...` 执行原子写 (tmp + os.replace)。
★严禁 open(p,"w")。
★只写自己那一份 (mech.yaml) ⇒ hw.yaml / sw.yaml / pm.yaml 一个字节不许碰。
"""
import os
import shlex
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

NEEDS = [
    (
        "iss316_mech_diff_ownership",
        "★26 条差集请裁归属口径 (★本单不代裁·已逐条给出建议 owner + 落表批次 + 验收判据★): "
        "「26 条差集里, D-1-1 的归属表漏记的 18 件归哪个 agent? D-3-1 / D-3-2 (等 hw 的网表/原理图结果) 要不要等? "
        "(★本单已逐条给出建议 owner + 落表批次 + 验收判据, 请裁归属口径★)」 "
        "★逐条归属已交: 26 行一条不少 (D-1 7 / D-2 9 / D-3 6 / D-4 4) ⇒ 落表批次 = 必须同批 17 条 / 单独批 9 条 / 已作废·留证不改 0 条 "
        "(★判据只有一条: 改它会不会动板 md5? 动 ⇒ 必须同批·背靠背不许拆两趟★) ⇒ owner 分布 = mech-lead 10 / main 9 / hw-lead 5 / boss 2 / sw-lead 0; "
        "★其中 6 条带「必须早于板那一趟 S1 开工」的前置条件 (D-1-1 / D-1-2 / D-2-1 / D-3-5 / D-4-1 / D-4-2); "
        "★归 boss 的 2 条 (D-1-7 / D-2-9) 本单只写「它要回答的那一句话 + 不回答的后果」, 没写建议答案★ "
        "★不拍的后果: 下一轮还是同一张 26 条差集 ⇒ 板那一趟照旧会被这 26 条咬 ⇒ 板改第二次 (2-4 周 + ¥4-8K)★ "
        "★交卷页: MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md §1 (26 行表 · 机器生成)★"
    ),
    (
        "iss319_cell_model_rename_scope",
        "★电芯型号订正 (ICP582035PR-01 → ICP422339PR) 的落字范围请裁 (★本单零改既有文档正文·只交逐字改法·不替 boss 拍采购型号★): "
        "「电芯型号订正 (ICP582035PR-01 → ICP422339PR) 按 47 行 / 22 个文件一起改, 还是只改口径行 (★历史留证行不动·留给 main 拍★)? "
        "以及打印包 (gen_print_pack_revb.py / MEASURE_CHECKLIST.md) 要不要跟板那一趟同批重出?」 "
        "★实测影响面 = 47 行 / 22 个活文件 (★ISS-316 §5-1 记的「8 行」只数了 MECH/MECH_BUDGET.md 一个文件, 连那个文件自己都漏了 L1177 ⇒ 实为 9 行★) "
        "⇒ 分类 = 口径行 26 行 (要改) + 脚本行 10 行 (只许改型号名那 5 个字, 逻辑常量 4.60/23.50/40.50 一处都不许动) + 留证·对照行 11 行 (★一行都不改★); "
        "★36 行可改行的数字指纹改前改后逐位相同 ⇒ 「几何与重量结论零变化」是机器判的★ "
        "★★给 main 的「可直接抄的逐字段落」= HW 域那 3 行 (HW/POWER_BUDGET_V3.md L27/L259 + HW/NETLIST_SELF_CONSISTENCY_SPEC.md L1046), MECH 侧 36 行逐字改法见交卷页 §2-2★; "
        "★★实测更正: gen_print_pack_revb.py 只写 4 个 .stl ⇒ 「打印包重出时会带上新型号名」只对 stdout 成立 ⇒ 真正的手工改法在 MECH/print/MEASURE_CHECKLIST.md L221 (★非生成·人手维护的实测清单★) ⇒ 不许拿「等打印包重出」拖这件事★ "
        "★不拍的后果: ① 采购单照现型号买 ⇒ 到货厚 6.40mm (不是 4.60) ⇒ 装不进 7.30mm 镜脚 ⇒ H 链最坏 −1.10mm ⇒ ★这笔比文档订正本身更贵★ "
        "② 只改 MECH_BUDGET 不改打印包/采购面 ⇒ 打印出来的那张清单还是旧型号 ⇒ 采购照样买错 "
        "③ 改了留证行 ⇒ 篡改历史结论链★ "
        "★交卷页: MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md §2 (47 行表 · 机器生成)★"
    ),
]

ARTIFACTS = [
    (
        "MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md",
        "decision_pack",
        "v1.0",
        "★ISS-319 (2026-11-18 · mech-lead · cron fb67af40) 「板只改一次」那一趟的【MECH 侧两件补账】交卷页★: "
        "§0 口径 / 取数命令 / 证据分级 / 边界自证 (★零写板·零落表·零改闸·零改既有文档正文·零改脚本·零改 HW 域文件·零重生成·零外发·不代拍·不自签·零整读大文件★) + "
        "§1 ★26 条差集 × owner × 落表批次 × 验收判据 (26 行一条不少·机器从 ISS-316 §4 逐行解析生成)★ "
        "(落表批次 = 必须同批 17 条 / 单独批 9 条 / 已作废·留证不改 0 条; owner = mech-lead 10 / main 9 / hw-lead 5 / boss 2; "
        "★归 boss 的 2 条只写「要回答的那一句话 + 不回答的后果」, 零建议答案★) + "
        "§2 ★电芯型号订正的真实影响面 (47 行 / 22 个活文件 / 9 个脚本)★ 逐条改法 (★现行逐字 / 改后逐字 / 口径行-脚本行-留证行分类 / 连带影响 / 数字指纹★) "
        "+ 给 main 的「可直接抄的逐字段落」 (HW 域 3 行) + 三条连带 (采购面 / 打印包重出≠写新型号 / 实测清单非生成) + "
        "§3 ★九个命中脚本的常量归属说明★ (★哪个常量是哪个型号的·为什么不能动★: service_port_check.py L51 只改注释里的型号名·4.60/23.50/40.50 一个字不许动 ⇒ 57/57 仍全绿; "
        "fit_check.py L69/L256; fit_check_v3_30mm.py L55; gen_print_pack_revb.py L99 只改第 3 元出处文案·第 1 元 4.60 不许动; "
        "另 5 个: verify_budget.py L126/L141 纯注释 · iss065_check.py L71 name 字段无引用 · L486 留证不改 · carrier_eval.py L55 出处文案 · board_width_15mm_check.py L47 纯注释 · _close_iss065.py L66 留证不改) "
        "+ §3-6 「改名不会让任何一道闸红」(★全仓 .py 里 ICP 只出现 12 次, 无一处拿型号名当匹配串★) + "
        "§4 证据分级 (五档齐) + §5 文件清单 (含 30 件只读/受保护件的 md5 前后对照) · "
        "★零写板 (板 md5 611b869e13518c3c023fb178f91a0075 + mtime 2026-11-06 07:07:17 交卷前后逐字节不变) · 零落表 · 零改闸 · 零改既有文档正文 · 零改脚本 · 零改 HW 域文件 · 零重生成 · 零外发 · 不替老板拍板 · 不自签 issue_log★"
    ),
    (
        "HANDOFF/2026-11-18_mech-lead_ISS319_差集归属与电芯订正影响面.md",
        "handoff",
        "v1.0",
        "★ISS-319 交卷单 (B0~B6 齐全·占位符 0)★: B0 一句话 + 交卷物清单 · "
        "B1 结论摘要 (★B1-1 26 行表 + B1-2 47 行表 + 文件数 22 vs main 的 19 的算术对账 + B1-3 四个脚本的常量归属说明 (补齐到 9 个) + B1-4 给 main 的 need 两行★) · "
        "B2 验收标准自评 31 条 (28 通过 / 3 未验: 老板拍 U-1 / main 裁归属口径 / 47 行实际落字) · B3 证据分级五档 · "
        "B4 接口取值声明 (只读 5 项现行值, 未新增/未修改任何 interface_claims) · "
        "B5 未决项 (给 main 的 need 两行 + 3 条必须 main 裁的 + 本单留给下一轮的 3 个动作) · "
        "B6 自证复现命令 + 交卷前后 md5 逐字节核对 (30 件) + 机检数字 + 交卷物清单"
    ),
    (
        "logs/iss319/",
        "evidence",
        "v1.0",
        "★ISS-319 取数脚本 + 原始输出 (★三支脚本全部只读, 不写受保护文件★): "
        "iss319_scan_audit.py (全量扫描 + 分类 + 9 个脚本的常量归属核对 + 零写板双证) + "
        "iss319_diff_ownership.py (★从 ISS-316 交卷页 MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md §4 逐行解析 26 条差集 + 挂 owner/落表批次/验收判据 + 出 markdown 表★) + "
        "iss319_gen_cell_table.py (47 行逐字改法表 + ★数字指纹证明: 36 行可改行的数字改前改后逐位相同 ⇒ 「几何与重量结论零变化」机器判★) + "
        "cell_model_scan_raw.txt (★47 行全量扫描原始输出★) + cell_model_files_inode.txt (22 个命中文件的 inode 两两不同 ⇒ 排除软/硬链接重复计数) + "
        "scan_audit_raw.txt / diff_ownership_raw.txt / cell_rename_table.md (★机器生成的两张表★) + "
        "mech_gates_baseline.txt (7 道 MECH 闸全 rc=0) + md5_BEFORE/AFTER + mtime_BEFORE/AFTER + placeholder_scan.txt"
    ),
]

STATUS = (
    "★ISS-319 (2026-11-18 · mech-lead · cron fb67af40) 「板只改一次」那一趟的【MECH 侧两件补账】交卷★: "
    "① 接住 ISS-316 §B5-3 第 3 条「§4 的 26 条差集逐条指定 owner」⇒ ★26 行一条不少 (D-1 7 / D-2 9 / D-3 6 / D-4 4·机器从 ISS-316 §4 逐行解析生成)·"
    "逐条给 owner + 落表批次 + 验收判据★ (落表批次 = 必须同批 17 / 单独批 9 / 已作废·留证不改 0; 判据只有一条: 改它会不会动板 md5? 动 ⇒ 必须同批; "
    "owner = mech-lead 10 / main 9 / hw-lead 5 / boss 2 / sw-lead 0; ★6 条带「必须早于 S1 开工」的前置条件★; ★归 boss 的 2 条只写「要回答的那一句话 + 不回答的后果」, 零建议答案★) + "
    "② ★电芯型号订正的真实影响面 = 47 行 / 22 个活文件 / 9 个脚本 (★ISS-316 记的「8 行」只数了 MECH_BUDGET.md 一个文件, 连它自己也漏了 L1177 ⇒ 实为 9 行★)★ "
    "⇒ 逐条给「现行逐字 / 改后逐字 / 口径行-脚本行-留证行分类 / 连带影响」⇒ 口径行 26 要改 · 脚本行 10 (只改型号名那 5 个字, 4.60/23.50/40.50 一处不许动) · 留证·对照行 11 一行都不改; "
    "★36 行可改行的数字指纹逐位相同 ⇒ 几何与重量结论零变化 (机器判)★ + ★九个脚本逐个说清「哪个常量是哪个型号的、为什么不能动」★ + "
    "★★实测更正: gen_print_pack_revb.py 只写 4 个 .stl ⇒ 「打印包重出带上新型号」只对 stdout 成立 ⇒ 真正的手工改法在 MEASURE_CHECKLIST.md L221 (非生成)★ + "
    "③ 给 main 的 need 两行 (iss316_mech_diff_ownership + iss319_cell_model_rename_scope) · "
    "★交付物: MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md + HANDOFF/2026-11-18_mech-lead_ISS319_差集归属与电芯订正影响面.md + logs/iss319/; "
    "★零写板 (板 md5 611b869e13518c3c023fb178f91a0075 + mtime 2026-11-06 07:07:17 交卷前后逐字节不变) · 零落表 · 零改闸 · 零改既有文档正文 · 零改脚本 · "
    "零改 HW 域文件 · 零重生成 · 零外发 · 不替老板拍板 · 不自签 issue_log★"
)


def main() -> int:
    # ★注意: subprocess 传的是 argv 列表 (不走 shell) ⇒ ★【不要】再套一层 shlex.quote★
    #   frag_write.py 自己会 shlex.split(spec) ⇒ spec 里 item=... 的值要用单引号包起来 (shlex.quote 干这件事),
    #   但整个 spec 本身必须【原样】传过去, 否则会被拆成一个大 token。
    argv = ["python3", "state/frag_write.py", "--agent", "mech-lead"]
    for key, item in NEEDS:
        argv += ["--add-need", "key=%s to=main since=2026-11-18 item=%s" % (key, shlex.quote(item))]
    for path, kind, ver, summary in ARTIFACTS:
        argv += ["--add-artifact", "path=%s kind=%s version=%s updated_at=2026-11-18 summary=%s"
                 % (path, kind, ver, shlex.quote(summary))]
    argv += ["--status", "phase=delivered progress_pct=100 health=green summary=%s" % shlex.quote(STATUS)]
    print("[iss319_apply] argv 长度 = %d" % len(" ".join(argv)))
    rc = subprocess.run(argv).returncode
    if rc != 0:
        return rc
    print("[iss319_apply] ✅ 分片已原子写 (state/frag_write.py) → 接着跑 state/merge.py && state/gate_check.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
