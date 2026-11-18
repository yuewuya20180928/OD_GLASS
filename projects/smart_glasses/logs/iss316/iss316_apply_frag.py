#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-316 · 把本单条目写进 state/fragments/mech.yaml (★必须走 state/frag_write.py 的原子写★)

★纪律: 本脚本【不】直接写分片文件 —— 它只用 shlex.quote 把参数拼好,
       再由 `python3 state/frag_write.py --agent mech-lead ...` 执行原子写 (tmp + os.replace)。
★严禁 open(p,"w")。
"""
import shlex
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

NEED_KEY = "iss316_mech_board_frame_freeze_gate_criteria"

NEED_ITEM = (
    "★U-1 板框冻结闸的机器判据请裁三件事 (★本单不代拍·决策码 M-B18★): "
    "(a) 「冻结了没有」做成机器闸 (★建议新文件 MECH/check_board_frame_freeze_gate.py · C1~C7 七条判据 · "
    "6 条反向用例 + 1 条正向对照 · 阈值一律只读 MECH/service_port_check.py 与 MECH/board_frame_feasibility.py 的现值 "
    "⇒ 本单只出设计, 零改闸★) 还是只写进作业包一句话 (★路 A·人话挡不住「只拍帧 id 没拍板厚」这个变体★)? "
    "(b) 拍板页上「板只改一次」这句话约束哪块板 —— 现役板 B160x100 还是产品板 F30A "
    "(★ISS-310 §C-2 B3: 换框 ≠ 板改第二次, 换框 = 多画一块板 ⇒ 两边对这句话的作用对象理解不同★)? "
    "(c) MECH/MECH_BUDGET.md 的两处订正 (★① 电芯型号名 ICP582035PR-01 → ICP422339PR, 8 行, 只换名字尺寸不动; "
    "② §3 重量表少算检修口盖板组件 +0.73 g, 6 处必须同批改★) 加上第三条不一致 "
    "(★MECH/service_port_check.py BASE mass_total_lo/hi = 48.90/72.80 vs MECH_BUDGET.md §3 合计 49.58-74.16★) "
    "跟板那一趟同批改还是单独批? "
    "★另: 板框三选一本身请按决策码 M-B18 汇总交老板 (★main 已于 2026-11-18 05:5x 汇总到 DECISION_INDEX_2026-11-18.md §E-1/§E-3; "
    "本单补的是 ① 决策一页 ② 机器可判判据 ③ 与 HW 侧清单的交叉对账差集 26 条★)。"
    "★不拍的后果: 闸 proto_pcb_freeze_gate 永远不满足 ⇒ 板那一趟没有第一前置; "
    "HW 作业包硬顺序首行是「网表」而不是「板框冻结」⇒ S1~S8 可在 U-1 未拍时开工 ⇒ 板 md5 第二次变 ⇒ "
    "Gerber/投产包/留证链全部作废重做 = 2-4 周 + ¥4-8K★。"
    "★交卷页: MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md (★§1 决策一页 · §2 冻结闸判据 + 6 条反向用例 · "
    "§3 结构侧同批件清单 18 必须 + 7 可后置 · §4 交叉对账差集 26 条 · §5 两处订正逐字改法 + 第三条不一致 · §6 证据分级★)★"
)

ARTIFACTS = [
    (
        "MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md",
        "decision_pack",
        "v1.0",
        "★ISS-316 (2026-11-18 · mech-lead · cron 775d9893) 「板只改一次」那一趟的【结构侧输入包】交卷页★: "
        "§1 U-1 板框三选一决策一页 (决策码 M-B18 · need key iss310_main_board_frame_u1_decision · 关联闸 proto_pcb_freeze_gate · "
        "状态待拍 · 三选项 × 8 个代价维度逐项取自 board_frame_feasibility.py --json 的 36 档现读数 · 建议默认值 F30A+板厚≤1.00 (只作参考不代拍) · "
        "不拍的后果 C-1~C-7 · 建议拍板顺序 先框→再板厚→再层数→最后 P7) + "
        "§2 「U-1 已冻结」的机器可判判据 (判什么字段/判成什么值/谁判/判在哪一步 + 落法两条路 + 新闸设计 C1~C7 + 6 条反向用例 + 1 条正向对照; "
        "★阈值一律只读 service_port_check.py 与 board_frame_feasibility.py 的现值 ⇒ 零自造零漂移★) + "
        "§3 结构侧那一趟同批出件清单 (必须同批 18 件 + 可后置 7 件, 逐件 件名/归属/依赖/必须或可后置/顺序位⓪~⑤/验收判据/不出的后果) + "
        "§4 与 HW 侧 ONETRIP_REISSUE_MANIFEST.md 的交叉对账差集 (★26 条: D-1 口径不一样 7 · D-2 只在 MECH 侧 9 · D-3 只在 HW 侧 6 · D-4 依赖顺序打架 4★) + "
        "§5 两处既有文档订正的逐字改法 (电芯型号名 8 行 · §3 重量表 +0.73 g 的 6 处同批改) + 第三条不一致交 need + §6 证据分级 (五档齐) · "
        "★零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零重生成 · 零外发 · 不代拍 · 不自签 issue_log★"
    ),
    (
        "HANDOFF/2026-11-18_mech-lead_ISS316_板那一趟结构侧输入包.md",
        "handoff",
        "v1.0",
        "★ISS-316 交卷单 (B1~B6 齐全)★: B1 结论摘要 + ★给 main 的 1 条建议 (先拍 U-1 板框, 三条理由) + 差集条数 26 + 零写板双证★ · "
        "B2 验收标准自评 30 条 (28 通过 / 2 未验: 老板拍板 + 新闸建挂) · B3 证据分级五档 · "
        "B4 接口取值声明 (只读 8 项现行值, 未新增/未修改任何 interface_claims) · "
        "B5 未决项 (给 main 的 need 一行 + 3 条必须 main 裁的 + 本单留给下一轮的 3 个动作) · "
        "B6 自证复现命令 + 交卷前后 md5 逐字节核对 + 交卷物清单"
    ),
    (
        "logs/iss316/iss316_diff_reconcile.py",
        "script",
        "v1.0",
        "★ISS-316 差集对账脚本 (★只读★): 直接 import MECH/board_frame_feasibility.py 的 all_rows() 与 BASE (★零自造零漂移★) 取 36 档现读数 + "
        "逐行解析 HW/PCB/ONETRIP_REISSUE_MANIFEST.md (主表 25 行 / §4-3 同趟出 12 条 / §4-4 归属表) + MECH 侧 25 件清单 + "
        "26 条差集 (D-1 7 / D-2 9 / D-3 6 / D-4 4) + 14 条依赖排序的依据出处 + 零写板双证 ⇒ "
        "原始输出落 logs/iss316/diff_reconciliation_raw.txt"
    ),
]

STATUS = (
    "★ISS-316 (2026-11-18 · mech-lead · cron 775d9893) 「板只改一次」那一趟的【结构侧输入包】交卷★: "
    "① U-1 板框三选一决策一页 (决策码 M-B18 · need key iss310_main_board_frame_u1_decision · 关联闸 proto_pcb_freeze_gate · 状态待拍 · "
    "三选项逐项代价全部取自 board_frame_feasibility.py --json 的 36 档现读数 · 建议默认值 F30A + 板厚 ≤1.00 (只作参考·不代拍) · "
    "不拍的后果 7 条 · 建议拍板顺序 先框→再板厚(1.22 档只差 0.02 就判红)→再层数→最后 P7) + "
    "② 「U-1 已冻结」的机器可判判据 (五条判据 + 落法两条路 + 新闸设计 C1~C7 + 6 条反向用例 + 1 条正向对照; 阈值零自造零漂移) + "
    "③ 结构侧那一趟同批出件清单 18 件 + 可后置 7 件 (与 HW 侧主表同款口径: 件名/归属/依赖/验收判据/顺序位⓪~⑤) + "
    "④ ★与 HW 侧清单的交叉对账差集 26 条★ (D-1 口径不一样 7 · D-2 只在 MECH 侧 9 · D-3 只在 HW 侧 6 · D-4 依赖顺序打架 4) "
    "⇒ ★这就是「板改第二次」的风险清单★ + "
    "⑤ 两处既有文档订正的逐字改法 (电芯型号名 ICP582035PR-01 → ICP422339PR 8 行 · §3 重量表检修口盖板 +0.73 g 的 6 处同批改) "
    "+ 顺手查出的第三条不一致交 need (service_port_check.py BASE 质量分母 vs MECH_BUDGET.md §3 合计) + "
    "⑥ 给 main 的 need 一行 (iss316_mech_board_frame_freeze_gate_criteria: 路 A/路 B + 「板只改一次」约束哪块板 + 三条订正排期) · "
    "★交付物: MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md + HANDOFF/2026-11-18_mech-lead_ISS316_板那一趟结构侧输入包.md + logs/iss316/; "
    "★零写板 (板 md5 611b869e13518c3c023fb178f91a0075 + mtime 2026-11-06 07:07:17 交卷前后逐字节不变) · 零落表 · 零改闸 · "
    "零改既有文档正文 · 零重生成 · 零外发 · 不替老板拍板 · 不自签 issue_log★"
)


def main() -> int:
    # ★注意: subprocess 传的是 argv 列表 (不走 shell) ⇒ ★【不要】再套一层 shlex.quote★
    #   frag_write.py 自己会 shlex.split(spec) ⇒ spec 里 item=... 的值要用单引号包起来 (shlex.quote 干这件事),
    #   但整个 spec 本身必须【原样】传过去, 否则会被拆成一个大 token (2026-11-18 实测踩到)。
    argv = [
        "python3", "state/frag_write.py", "--agent", "mech-lead",
        "--add-need", "key=%s to=main since=2026-11-18 item=%s" % (NEED_KEY, shlex.quote(NEED_ITEM)),
    ]
    for path, kind, ver, summary in ARTIFACTS:
        argv += ["--add-artifact", "path=%s kind=%s version=%s updated_at=2026-11-18 summary=%s"
                 % (path, kind, ver, shlex.quote(summary))]
    argv += ["--status", "phase=delivered progress_pct=100 health=green summary=%s" % shlex.quote(STATUS)]
    print("[iss316_apply] " + " ".join(argv)[:300] + " ...")
    rc = subprocess.run(argv).returncode
    if rc != 0:
        return rc
    print("[iss316_apply] ✅ 分片已原子写 (state/frag_write.py) → 接着跑 state/merge.py && state/gate_check.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
