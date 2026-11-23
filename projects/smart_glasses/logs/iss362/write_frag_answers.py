#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-362 · 用 state/frag_write.py 的 CLI 原子写, 登记 9 条 need 的 answer (★退休/改写口径★)

★并发纪律: 写前记 md5 基线 · 写后记 md5 · 并逐条核对【原有条目一条没丢】★
★★不许改任何 need 条目正文 · 不许改锚点 md5 · 不许改别人的分片★★
"""
from __future__ import annotations
import hashlib
import os
import shutil
import subprocess
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FRAG = os.path.join(PROJ, "state", "fragments", "sw.yaml")
SNAP = os.path.join(PROJ, "logs", "iss362", "sw_fragment_snapshot_pre.yaml")


def md5f(p: str) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


CHAIN = ("★依据 = 落表台账链头实测 (★用 check_demo_panel_spec.py 的 sw_ledger_state() 自己算★): "
         "网表链头 6aee500e60ba (by ISS-302 · 盘上 6aee500e60ba0732f83a9cf557ba90ab) · "
         "脚表链头 9174309df1ec (by ISS-302 · 盘上 9174309df1ec9411ac8e8d9e80ee386a) · "
         "BOM 链头 5b9993992405 (by ISS-302 · 盘上 5b9993992405904a60ac96a020b375d8) "
         "⇒ 三件盘上 == 链头 (闸 H2 一条不许红)★")

COMMON = ("★ISS-362 · sw-lead · 2026-11-23 · 「板那一趟」S10 换封装真值对 SW 侧的影响面已登记 "
          "(页 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md · 闸 SW/tools/check_sw_fp_truth_impact.py ⇒ rc=0 · --selftest 6/6)★ "
          "⇒ ★本条 need 要的「H-1 重锚」这件事已被 ISS-275 的判决源换源取代 (判决源 = 落表台账链头 · 合法落表自动前移 · "
          "不用再追锚点) ⇒ 作为待执行指令已过期 ⇒ 本条【退休】(★正文原样留档·一个字没改★)★ "
          + CHAIN + " ⇒ ★处置与影响见页 §2 (逐条 md5 登记 + 逐条 need 处置表)★ "
          "⇒ ★本单零写板 · 零落表 · 零改锚点 md5 · 零改 SW/BOARD_ONEPASS_SW_SYNC.md · 零改既有闸★")

VALUES = {
    "iss232_no_netlist_change_anchor_ok":
        COMMON + " ⇒ ★本条正文里的两个值 (网表 3215020b… = ISS-220 那一跳 · 脚表 a600afae… = ISS-220 那一跳) "
        "都在落表链上 ⇒ 是【已被链头取代的历史值】⇒ 处置 = 退休; ★它正文说的「这一轮网表没改」这个前提早已被后续落表推翻★",
    "iss233_sw_md5_reanchor":
        COMMON + " ⇒ ★本条正文里的四个值 (3215020b… / 34132f7e… / a600afae… / b21b743a…) 全是落表链上的历史值 "
        "⇒ 处置 = 退休 (★它们不许被照抄进锚点★) ⇒ ★本条正文自己写的那句「不重锚就恒红」正是 ISS-275 要消灭的那个红★",
    "iss236_h1_reanchor":
        COMMON + " ⇒ ★本条正文里的三个 32 位 md5 (cb477b37… / b65d2000… / 1119c2a8…) 是【V-3=E 真落之前在 /tmp 副本上排练出来的值】"
        "(★本条自己写明「在 /tmp 副本上实跑」★) ⇒ 它们从来没落到过盘上 ⇒ 不是合法历史值 ⇒ ★处置 = 改写 (不许照抄·照抄会把锚点写到一个不存在的值上)★ "
        "⇒ 本条作为待执行指令【退休】; 另三个 8 位短写 (34132f7e / b21b743a / c195a117) 是历史值 ⇒ 退休",
    "iss239_h1_reanchor_sw":
        COMMON + " ⇒ ★本条正文里的三个 8 位短写 (3b8cf3d9… / 319b21f2… 等) 是【预估 / 副本排练值】"
        "(★本条自己写明「预估 (/tmp 副本 cp -a 整棵树实跑)」★) ⇒ ★处置 = 改写 (不许照抄)★; "
        "另两个 (34132f7e / b21b743a / c195a117) 是已被链头取代的历史值 ⇒ 退休 ⇒ 本条作为待执行指令【退休】",
    "iss249_h1_reanchor_netlist_md5_sw":
        COMMON + " ⇒ ★本条正文里的四个 32 位 md5 (611c3ba3… / 16ac89f7… / ef436a37… / 2a730574…) 全是落表链上的历史值 "
        "⇒ 处置 = 退休 (★不许照抄进锚点★); ★另两个 (板 611b869e… / .kicad_pro 3e504d2b…) 是【受保护 5 件的盘上现值】⇒ 不是过期值 ⇒ 保持不动★ "
        "⇒ ★本条要的 H-1 重锚早已被 ISS-275 取代 ⇒ 本条作为待执行指令【退休】",
    "iss257_h1_reanchor_to_sw_lead":
        COMMON + " ⇒ ★本条正文里的四个值 (e06c1dd6… / 287e7861… / 16ac89f7… / ef436a37…) 全是落表链上的历史值 ⇒ 处置 = 退休 "
        "(★不许照抄进锚点★) ⇒ ★本条正文自己写的那句「本机 21:4x 实跑红点: R6 盘上 md5 e06c1dd6 ≠ 锚点 16ac89f7」"
        "就是 ISS-275 要消灭的那个红 ⇒ 那个红今天已经不存在 (盘上 6aee500e == 链头 6aee500e)★",
    "iss260_h1_reanchor_after_v2_land":
        COMMON + " ⇒ ★本条正文里的两个 32 位 md5 (02c3cec1… / 2c950b67…) 是【沙盒端到端实测的排练值】"
        "(★本条自己写明「本单没落·所以现在不用动」★) ⇒ 从来没落到过盘上 ⇒ ★处置 = 改写 (不许照抄)★; "
        "另三个 (94642d07… / e06c1dd6… / 287e7861…) 是落表链上的历史值 ⇒ 退休 ⇒ 本条作为待执行指令【退休】",
    "iss236_h1_reanchor_v2":
        COMMON + " ⇒ ★本条正文里的三个 32 位 md5 (f617ffc1… / 9effa57c… / cb830fba…) 是【沙盒排练实测值】"
        "(★本条自己写明「排练值·真盘真落后 md5 会再变·以那一遍实测为准·不许拿排练值改台账」★) ⇒ ★处置 = 改写 (不许照抄)★; "
        "另三个 (e06c1dd6… / 287e7861… / 94642d07…) 是落表链上的历史值 ⇒ 退休 ⇒ 本条作为待执行指令【退休】",
    "iss283_sw_anchor_reanchor_after_landing":
        COMMON + " ⇒ ★本条正文里的四个 8 位短写 (e06c1dd6… / 287e7861… / 37f62ac3… / a4270120…) 全是落表链上的历史值 ⇒ 处置 = 退休 "
        "(★不许照抄进锚点★) ⇒ ★本条正文自己给的处置「按台账 §16.2 链头 L1353 追加一条 entries」恰恰就是 ISS-275 已经换成链头判决源的那件事 "
        "⇒ 现在追加 entries 只是历史留痕·不再是判决源 ⇒ 本条作为待执行指令【退休】",
}

REF = ("SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md#§2 · SW/tools/check_sw_fp_truth_impact.py (H3) · "
       "logs/iss362/probe_h3_set.txt · logs/iss362/probe_need_texts.txt · logs/iss362/h3_reg_block.txt")


def main() -> int:
    import yaml
    print("★ 写前基线 md5 = %s" % md5f(FRAG))
    shutil.copy2(FRAG, SNAP)
    before = yaml.safe_load(open(FRAG, encoding="utf-8"))
    n_before_answers = len(before.get("answers") or [])

    for key, val in VALUES.items():
        assert "'" not in val and '"' not in val, "★value 里不许有引号 (shlex 会炸)★"
        spec = "key=%s to=main value='%s' ref='%s'" % (key, val, REF)
        r = subprocess.run([sys.executable, os.path.join(PROJ, "state", "frag_write.py"),
                            "--agent", "sw-lead", "--add-answer", spec],
                           cwd=PROJ, capture_output=True, text=True)
        print("  · %-46s rc=%s %s" % (key, r.returncode, (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else ""))
        if r.returncode != 0:
            print(r.stdout); print(r.stderr)
            return 1

    after_md5 = md5f(FRAG)
    print("★ 写后 md5 = %s" % after_md5)
    after = yaml.safe_load(open(FRAG, encoding="utf-8"))
    n_after_answers = len(after.get("answers") or [])
    print("★ answers 条数: 写前 %d ⇒ 写后 %d (新增 %d)" % (n_before_answers, n_after_answers,
                                                            n_after_answers - n_before_answers))

    # ---- 逐段核对: 原有条目一条没丢 ----
    bad = []
    for field in ("artifacts", "blockers", "needs_from", "interface_claims", "open_questions", "risks"):
        b = before.get(field) or []
        a = after.get(field) or []
        if b != a:
            bad.append("%s 变了 (写前 %d 项 · 写后 %d 项)" % (field, len(b), len(a)))
    ba = before.get("answers") or []
    aa = after.get("answers") or []
    if aa[:len(ba)] != ba:
        bad.append("answers 的原有 %d 条被改动了" % len(ba))
    for k in VALUES:
        if not any(x.get("key") == k for x in aa[len(ba):]):
            bad.append("新 answer %s 没写进去" % k)
    if bad:
        print("❌ 逐段核对失败:")
        for x in bad:
            print("   ·", x)
        return 1
    print("✅ 逐段核对: needs_from / artifacts / blockers / interface_claims / open_questions / risks 全部逐字未变; "
          "answers 原有 %d 条逐字未变; 新增 %d 条" % (len(ba), len(aa) - len(ba)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
