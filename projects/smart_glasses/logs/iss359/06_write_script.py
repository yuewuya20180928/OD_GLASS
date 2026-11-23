#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-359 · hw-lead · 分片重名 key 清理 · 【唯一写路径 = state/frag_write.py】

★只写 state/fragments/hw.yaml (★只走 state/frag_write.py 的原子写·不碰 pm/sw/mech★)
★零写板 · 零落表 · 零外发 · 不替老板拍板 ★

【并发哨兵】本脚本开工先记 md5; 若与 main 12:43 实读基线 (dd73d31621ebac6105d19cfc2469d0f0)
  不一致 ⇒ 说明期间有人写过 hw.yaml ⇒ ★直接 abort, 不静默覆盖 (★这正是本单要治的病★)
【前置断言】每一条要动的条目, 先按 (key, to) 定位并断言其原文逐字相符 ⇒ 断言不过 ⇒ 不落盘
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PROJ, "state"))

import frag_write  # ★唯一许可的写路径 ★

FRAG = os.path.join(PROJ, "state", "fragments", "hw.yaml")
BASELINE_MD5 = "dd73d31621ebac6105d19cfc2469d0f0"   # ★main 2026-11-23 12:43 实读 ★

# ---------------------------------------------------------------- 原文断言用常量
A081_MECH = "C-min=41/C-base=57/C-max=91; <=50脚仅C-min可行; BTB按60位/载板16x16预留(勿因pin预算缩到40位)"
A081_MAIN = "C-min=41/C-base=57/C-max=91; 封装球数非风险; 建议BTB 60位+载板16x16"
A287_B3 = ("官方板 186 封装 / 8 铜层 / 板框 160.10×100.10 / S6 已在目标位19 不同1(R_SEL_D3_P) 缺失0 "
           "/ DNP 板上零标记 40 颗 / 位号问号 0 行 / unconnected 45 / DRC violations 0 / Gerber 32")
A287_SUP = ("同批补测: 官方板 186 封装里末字符是字母的只有 156 个 (另 30 个末字符是数字不动) ⇒ 板侧真正要加 _1 的是 156 个不是 186 个; "
            "官方板带 _1 后缀的位号 = 1 个 (R_BAT_DET_1) ⇒ 改完 157 个 (S2 后 156); 封装数官方板 186 / 生成板 185 差 1 = C_VBUS_GND "
            "(CHG_BOARD 归属 + DNP 但官方板上有实物封装@107.70,42.50) ⇒ 动板那趟按官方板数走 开工前 186 收工后 185")


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def pick(lst, key, to):
    """按 (key, to) 精确挑出条目 ★挑不出/挑多条 ⇒ 抛 (调用方断言) ★"""
    return [e for e in lst if isinstance(e, dict) and e.get("key") == key and e.get("to") == to]


def main():
    cur_md5 = md5_file(FRAG)
    print("★开工 md5 = %s" % cur_md5)
    if cur_md5 != BASELINE_MD5:
        print("★★**ABORT: hw.yaml 与 main 12:43 实读基线 (%s) 不一致 ⇒ 期间有人写过** ★" % BASELINE_MD5)
        print("★★**按 brief 的并发规则: 停下 + 写进交卷页 (不静默覆盖)** ★")
        return 2

    d = frag_write.load_fragment("hw-lead")
    A, N = d.get("answers") or [], d.get("needs_from") or []

    # ============================== 前置断言 ==============================
    assert len(pick(A, "iss081_pin_budget_carrier", "mech-lead")) == 1, "iss081/mech 条目数不对"
    assert len(pick(A, "iss081_pin_budget_carrier", "main")) == 1, "iss081/main 条目数不对"
    assert pick(A, "iss081_pin_budget_carrier", "mech-lead")[0]["value"] == A081_MECH
    assert pick(A, "iss081_pin_budget_carrier", "main")[0]["value"] == A081_MAIN
    assert len(pick(A, "iss287_baseline_readings", "main")) == 2, "iss287 条目数不对"
    assert pick(A, "iss287_baseline_readings", "main")[0]["value"] == A287_B3
    assert pick(A, "iss287_baseline_readings", "main")[1]["value"] == A287_SUP
    assert len(pick(N, "iss249_h1_reanchor_netlist_md5", "sw-lead")) == 1
    assert len(pick(N, "iss249_h1_reanchor_netlist_md5", "mech-lead")) == 1
    assert len(pick(N, "iss249_kicad_sch_md5_not_anchor", "sw-lead")) == 1
    assert len(pick(N, "iss249_kicad_sch_md5_not_anchor", "mech-lead")) == 1
    s1 = pick(N, "s1_ref_rename_caliber_20261118", "main")
    assert len(s1) == 3, "s1 条目数不对 (%d)" % len(s1)
    assert s1[0]["item"] == s1[1]["item"], "s1 #0/#1 不再逐字相同 ⇒ 前提变了, 停"
    assert s1[2]["item"] != s1[0]["item"], "s1 #2 与 #0 已相同 ⇒ 前提变了, 停"
    print("★前置断言 12/12 通过 (原文逐字相符) ★")

    n_ans_before, n_needs_before = len(A), len(N)

    # ============================== (1) answers: 2 组高危重名 ==============================
    # (1a) iss081_pin_budget_carrier ×2 → 1 条 (★key 不许改★: mech.yaml 的 need 问的就是这个 key)
    a_mech = pick(A, "iss081_pin_budget_carrier", "mech-lead")[0]
    a_main = pick(A, "iss081_pin_budget_carrier", "main")[0]
    a_mech["value"] = (
        "C-min=41/C-base=57/C-max=91; <=50脚仅C-min可行; 封装球数非风险; "
        "BTB按60位/载板16x16预留(勿因pin预算缩到40位); 建议BTB 60位+载板16x16"
        " ★【ISS-359 清重名】原同 key 两条答复并成 1 条 (一条 to=mech-lead + 一条 to=main): "
        "四段语义全部保留, 本条同口径亦同步 main ★"
    )
    a_mech["ref"] = "HW/SOC_PIN_BUDGET.md#1.1 + HW/SOC_PIN_BUDGET.md"
    a_mech["to"] = "mech-lead"     # ★保持 to=mech-lead: gate_check 的「真对上别人的需求 key」要靠它★
    A.remove(a_main)              # ★第二条并入第一条 ⇒ 逐字删除, 不留重名 ★

    # (1b) iss287_baseline_readings ×2 → 1 条 (两条都是 to=main; ★合并, 不拆 key★)
    a287 = pick(A, "iss287_baseline_readings", "main")
    keep, drop = a287[0], a287[1]
    keep["value"] = (
        A287_B3 + " || " + A287_SUP +
        " ★【ISS-359 清重名】原同 key 两条答复并成 1 条 (原「同上 B3」段 + 原「同批补测」段): 两段全文保留 ★"
    )
    keep["ref"] = ("HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md B3 "
                   "(★原 ref 逐字写作「同上 B3」⇒ 经文件实读确认指向本文档 B3 读数表★) + "
                   "HANDOFF/2026-11-17_hw-lead_ISS289_作业包现状值对回盘面.md §B2")
    keep["to"] = "main"
    A.remove(drop)

    # ============================== (2) needs_from: 3 组重名 ==============================
    # (2a) iss249_h1_reanchor_netlist_md5 ×2 → 拆成 _sw / _mech (★收件人不同 = 两件事★)
    pick(N, "iss249_h1_reanchor_netlist_md5", "sw-lead")[0]["key"] = "iss249_h1_reanchor_netlist_md5_sw"
    pick(N, "iss249_h1_reanchor_netlist_md5", "mech-lead")[0]["key"] = "iss249_h1_reanchor_netlist_md5_mech"
    # (2b) iss249_kicad_sch_md5_not_anchor ×2 → 拆成 _sw / _mech
    pick(N, "iss249_kicad_sch_md5_not_anchor", "sw-lead")[0]["key"] = "iss249_kicad_sch_md5_not_anchor_sw"
    pick(N, "iss249_kicad_sch_md5_not_anchor", "mech-lead")[0]["key"] = "iss249_kicad_sch_md5_not_anchor_mech"
    # (2c) s1_ref_rename_caliber_20261118 ×3 → #0/#1 逐字重复合并成 1 条 + #2 拆独立 key
    s1 = pick(N, "s1_ref_rename_caliber_20261118", "main")
    N.remove(s1[1])                                   # ★#1 与 #0 逐字相同 ⇒ 删 #1 零丢失 ★
    s1[2]["key"] = "s1_ref_rename_caliber_nc_whitelist_20261118"   # ★#2 语义独立 ⇒ 保留全文, 换 key ★

    d["answers"] = A
    d["needs_from"] = N

    # ============================== 写盘 (★走 frag_write 原子写★) ==============================
    frag_write.update_fragment("hw-lead", lambda _d: _d.update({"answers": A, "needs_from": N}))
    print("★已原子写 state/fragments/hw.yaml")
    print("★answers   %d → %d" % (n_ans_before, len(A)))
    print("★needs_from %d → %d" % (n_needs_before, len(N)))
    print("★写后 md5 = %s" % md5_file(FRAG))
    return 0


if __name__ == "__main__":
    sys.exit(main())
