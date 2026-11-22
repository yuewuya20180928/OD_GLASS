#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/_apply_20261117_1555_cronfb67_answer288_needs.py

★main 2026-11-17 15:5x (cron fb67af40 队列自动派活)★

★**为什么有这一趟**: ★ISS-288 已由 main 验签落 verified (★15:5x·另一路 main 会话签的★) ⇒ ★**但三条 to=main 的 need 还挂在
  `state/fragments/sw.yaml` 里处于 pending** ⇒ ★**队列表面收口了, 内部待办却还挂着 ⇒ 这就是「内部待办断线」的另一种形态** ★

★**merge.py 的配对口径 (★本机实读 state/merge.py L290~L330★)**: ★**need 只被【它问的那个 agent】的答案闭合**
  (★`ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]★) ⇒ ★**这三条 need 的 to = main ⇒ 答案必须写在 main 自己的分片
  (`state/fragments/pm.yaml`) ⇒ sw-lead 在自己分片里写只能算 foreign_answer, 闭合不了** ★

★**本脚本做一件事**: ★**用 `state/frag_write.py` 的原子写 API, 在 main 自己的分片 pm.yaml 里补 3 条答案** ★
  ① `iss285_sw_apply_after_iss283_verified`  ★② `iss288_sw_timing_check_patch_landed`  ★③ `iss288_main_verify_sign_issue_log`

★**边界**: ★**只写 main 自己的分片 pm.yaml** (★不碰 sw.yaml / hw.yaml / mech.yaml / issue_log / 板 / 网表★)
  ⇒ ★**零写板 · 零落表 · 零外发 · 不替老板拍板★** ★**答案内容全部是 main 本机实跑复验过的结论 (不抄交卷报告)★**
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from frag_write import update_fragment  # noqa: E402

ANSWERS = [
    {
        "key": "iss285_sw_apply_after_iss283_verified",
        "to": "main",
        "value": (
            "★已由 ISS-288 履行完毕 (★本答案 = main 2026-11-17 15:3x~15:5x 本机独立实跑复验, 不抄交卷报告★)★ "
            "⇒ 真盘 SW/tools/timing_check.py md5 = 68c4becffe6bcd708e388dba9d18a505 "
            "(★与 ISS-285 交卷单写死的【改后期望 md5】逐字一致★) ⇒ `python3 SW/tools/timing_check.py` rc=0 "
            "(★实跑末行逐字: SELFTEST 72/72 通过, rc=0★) ⇒ `python3 state/merge.py` rc=0 ⇒ "
            "`python3 state/gate_check.py` rc=0 (★Q1 交付齐备率 18/18★) ⇒ 板 611b869e… / .kicad_pro 3e504d2b… / "
            "网表 37f62ac3… / 脚表 a4270120… / BOM 5d02bece… 五个 md5 逐字节未变 ⇒ ★本 need 关闭★ "
            "⇒ ★ISS-288 已落 verified (fix_ref = HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md)★"
        ),
        "ref": "ISS-288 交卷单 + main 2026-11-17 15:3x~15:5x 本机实跑复验",
    },
    {
        "key": "iss288_sw_timing_check_patch_landed",
        "to": "main",
        "value": (
            "★补丁已落盘, 且已由 main 验签★ ⇒ ISS-288 status = verified (verify_by = main · verify_date = 2026-11-17) · "
            "fix_ref = HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md ⇒ 真盘 timing_check.py md5 = "
            "68c4becffe6bcd708e388dba9d18a505 + rc=0 (SELFTEST 72/72) ⇒ ★本 need 关闭★"
        ),
        "ref": "ISS-288 交卷单 + main 15:5x 验签",
    },
    {
        "key": "iss288_main_verify_sign_issue_log",
        "to": "main",
        "value": (
            "★已验签★ ⇒ ISS-288 已由 main 签 verified (★status fixing→verified · fix_ref 填交卷单路径 · verify_by = main · "
            "verify_date = 2026-11-17★) ⇒ ★本 need 关闭★ ⇒ ★附: 同时把 `iss285_sw_apply_after_iss283_verified` 与 "
            "`iss288_sw_timing_check_patch_landed` 一并代录 (★这两条 need 的 to 也是 main ⇒ 答案只能由 main 写进自己的分片· "
            "sw-lead 在自己分片里写只会变成 foreign_answer, 闭合不了★)★"
        ),
        "ref": "main 2026-11-17 15:5x 验签",
    },
]


def main() -> int:
    def mut(d):
        ans = d.setdefault("answers", [])
        existing = {a.get("key") for a in ans if isinstance(a, dict)}
        added = []
        for a in ANSWERS:
            if a["key"] in existing:
                print("★已存在答案 %s ⇒ 不重复写" % a["key"])
                continue
            ans.append(a)
            added.append(a["key"])
        d["updated_at"] = "2026-11-17 15:55"
        d["updated_by"] = "main (cron fb67af40 队列自动派活)"
        return added

    added = update_fragment("main", mut)
    print("✅ pm.yaml 补答案 %d 条: %s" % (len(added), ", ".join(added) if added else "(无)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
