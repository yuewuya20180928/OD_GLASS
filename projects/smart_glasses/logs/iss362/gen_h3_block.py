#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-362 · 生成 SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md 的 H3-REG 机器可读登记块
★事实全部由 SW/tools/check_sw_fp_truth_impact.py 的同一套采集函数算出来 ⇒ 页与闸不会打架★
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "SW", "tools"))

import check_sw_fp_truth_impact as G   # noqa: E402

NEED_WHY = {
    "iss232_no_netlist_change_anchor_ok":
        "它正文说的是【网表这一轮没改 ⇒ 锚点不用动】; 那个前提早就被后续落表推翻 ⇒ 它作为【待执行指令】已过期 ⇒ 退休; "
        "但它正文里的脚表 8 位短写 `a600afae` 是历史值 ⇒ 不许照抄 ⇒ 改写",
    "iss233_sw_md5_reanchor":
        "它要的是「按 H-1 重锚 §1 entries[] 的 md5」; ISS-275 已把判决源换成【落表台账链头】(链头自动前移·不用再追锚点) ⇒ "
        "这条 need 作为【待执行指令】已过期 ⇒ 退休; 它正文里的 4 个值全是历史值 ⇒ 不许照抄",
    "iss236_h1_reanchor":
        "它正文里那 3 个 32 位 md5 是【V-3=E 真落之前在 /tmp 副本上排练出来的值】(它自己写明「在 /tmp 副本上实跑」) ⇒ "
        "它们从来没落到过盘上 ⇒ 不是合法历史值 ⇒ 改写 (照抄会把锚点写到一个不存在的值上)",
    "iss239_h1_reanchor_sw":
        "它正文里 3 个 8 位短写是【预估 / 副本排练值】(它自己写明「预估 (/tmp 副本 cp -a 整棵树实跑)」) ⇒ 改写; "
        "另外 2 个 (34132f7e / b21b743a) 是已被取代的历史值 ⇒ 退休; 整条 need 作为【待执行指令】已过期 ⇒ 退休",
    "iss249_h1_reanchor_netlist_md5_sw":
        "它要的 H-1 重锚早已被 ISS-275 取代 ⇒ 退休; 它正文里的 4 个 32 位 md5 都是已被链头取代的历史值 ⇒ 不许照抄 ⇒ 退休; "
        "★它正文里另外那 2 个 (板 611b869e / .kicad_pro 3e504d2b) 是【受保护 5 件的盘上现值】⇒ 不是过期值 ⇒ 保持",
    "iss249_kicad_sch_md5_not_anchor_sw":
        "★这条 need 一个 md5 字面量都没有 (它说的是「.kicad_sch 的 md5 不能当锚点」) ⇒ 不在 H3 的逐条判据内 ⇒ "
        "但它【同样已经过期】(ISS-275 之后 .kicad_sch 也不在受保护 5 件里) ⇒ 退休 (登记在本表里留档)",
    "iss257_h1_reanchor_to_sw_lead":
        "它正文里明写「本机 21:4x 实跑红点: R6 盘上 md5 e06c1dd6 ≠ 锚点 16ac89f7」—— ★那个红就是 ISS-275 要消灭的红★ ⇒ "
        "ISS-275 已把判决源换成链头 ⇒ 这条 need 作为【待执行指令】已过期 ⇒ 退休; 它正文里的 4 个值全是历史值 ⇒ 不许照抄",
    "iss260_h1_reanchor_after_v2_land":
        "它正文里明写「本单没落, 所以现在不用动」+「沙盒端到端实测的新 md5」⇒ 那 2 个 32 位 md5 是【排练值】⇒ 改写; "
        "另外 3 个是历史值 ⇒ 退休; 整条 need 作为【待执行指令】已过期 ⇒ 退休",
    "iss236_h1_reanchor_v2":
        "它是 iss236_h1_reanchor 的订正版, 正文里 3 个 32 位 md5 是【沙盒排练实测值】(它自己写明「排练值·真盘真落后 md5 会再变·以那一遍实测为准·不许拿排练值改台账」) ⇒ "
        "★这条 need 自己就写着「不许拿排练值改台账」★ ⇒ 改写; 另外 3 个是历史值 ⇒ 退休",
    "iss283_sw_anchor_reanchor_after_landing":
        "它正文里明写「盘上已是 ISS-283 落表后的 37f62ac3 / a4270120」+「降级 = 按台账 §16.2 链头 L1353 追加一条 entries」⇒ "
        "★它给的处置恰恰就是 ISS-275 已经换成链头判决源的那件事 ⇒ 这条 need 作为【待执行指令】已过期 ⇒ 退休; "
        "它正文里的 4 个 8 位短写都是历史值 ⇒ 不许照抄",
}


def main() -> int:
    facts = G.collect_facts(PROJ)
    md5_rows = G.need_md5_rows(facts)
    pref_rows = G.need_prefix_rows(facts)
    stale32 = [r for r in md5_rows if r["stale"]]
    keep32 = [r for r in md5_rows if not r["stale"]]

    # 去重 (key, md5)
    def dedup(rows):
        seen, out = set(), []
        for r in rows:
            k = (r["key"], r["md5"])
            if k in seen:
                continue
            seen.add(k)
            out.append(r)
        return out

    stale32 = dedup(stale32)
    pref_rows = dedup(pref_rows)

    all_stale = stale32 + pref_rows
    all_rows = all_stale + keep32
    need_keys = []
    for r in all_rows:
        if r["key"] not in need_keys:
            need_keys.append(r["key"])
    # iss249_kicad_sch_md5_not_anchor_sw 没有 md5 字面量 ⇒ 手工登记 (机器判据覆盖不到)
    # ★只登记【确实属于 md5 重锚这件事】的无字面量 need; 其余 (iss223 / iss334 / iss229) 与 md5 无关 ⇒ 不许混进来★
    MANUAL_NO_MD5 = ("iss249_kicad_sch_md5_not_anchor_sw",)
    manual_no_md5 = [k for k in MANUAL_NO_MD5
                     if k in {n.get("key") for n in facts["sw_needs"]}]

    L = []
    A = L.append
    A("<!-- H3-REG:BEGIN -->")
    A("★**H3-REG · SW 侧待办 need 里引着的过期 md5 · 逐条清理口径** ★")
    A("")
    A("★**机器判据 (★闸 `SW/tools/check_sw_fp_truth_impact.py` H3 逐条复核·不是靠人眼★)** ★")
    A("")
    A("| 判据 | 含义 |")
    A("|---|---|")
    A("| 落在链上 | 该 md5 是 SW 受管真源 (网表 / 脚表 / BOM) 某一跳落表产出过的值 ⇒ 已被链头取代 ⇒ 处置词必须是 **退休** |")
    A("| 不在链上 | 该 md5 从来没落到过这三件上 (多是沙盒排练值 / 预估值) ⇒ 不是合法历史值 ⇒ 处置词必须是 **改写** |")
    A("| 保持 | 该 md5 是受保护 5 件的**盘上现值** (板 / `.kicad_pro`) ⇒ 不是过期值 ⇒ 不许当陈旧值处理 |")
    A("")
    A("★**处置词的含义** ★")
    A("")
    A("- **退休** = 这条 need 的正文【原样留档】, 但它【不再是一条待执行的重锚指令】 ⇒ 它不再虚增未闭合需求数")
    A("- **改写** = 这条 need 正文里那个 md5 【不许被照抄进任何锚点】 ⇒ 真要重锚只能用【落表台账链头】")
    A("- **保持** = 这个值是当前的合法值 (板 / `.kicad_pro` 的保护基线) ⇒ 不动")
    A("")
    A("★**§2-1 · 逐条 need 处置表 (need 级 · 覆盖全部 %d 条引着 md5 字面量 + 1 条无 md5 但同类的 to=sw-lead 待办 need)** ★"
      % len(need_keys))
    A("")
    A("| need key | since | 引了几个 md5 | 其中陈旧几个 | 处置 | 一句话理由 |")
    A("|---|---|---|---|---|---|")
    for k in need_keys:
        allr = [r for r in all_rows if r["key"] == k]
        st = [r for r in allr if r["stale"]]
        if st and all(r["disposition"] == "退休" for r in st):
            disp = "**退休**"
        elif st and all(r["disposition"] == "改写" for r in st):
            disp = "**改写**"
        else:
            disp = "**退休 + 改写**"
        since = allr[0].get("since")
        A("| `%s` | %s | %d | %d | %s | %s |" % (k, since, len(allr), len(st), disp, NEED_WHY.get(k, "")))
    for k in manual_no_md5:
        A("| `%s` | %s | 0 | 0 | **退休** | %s |"
          % (k, [n.get("since") for n in facts["sw_needs"] if n.get("key") == k][0],
             NEED_WHY.get(k, "★它一个 md5 字面量都没有 ⇒ 机器逐条判据覆盖不到 ⇒ 手工登记留档★")))
    A("")
    A("★**§2-2 · 逐条 md5 登记 (★机器逐条复核用 ★ 本单【不许】改 need 条目·只出建议表★)** ★")
    A("")
    A("★下列每一行都是机器可复核的: 【need key】+【它引的那个 md5】+【处置】三件套缺一 ⇒ H3 判红 ★")
    A("")
    for r in all_stale:
        if r["on_chain"]:
            rel = r["on_chain"].split("/")[-1]
            c = next(x for x in facts["chain12"][r["on_chain"]] if x.startswith(r["md5"][:12]))
            hop = facts["chain12"][r["on_chain"]].index(c)
            head = facts["ledger"][r["on_chain"]]["head"]
            where = "%s 落表链第 %d 跳 · 链头 %s" % (rel, hop, head)
        else:
            where = "不在任何一跳落表链上 (排练值 / 预估值)"
        A("- NEED-KEY: %s | NEED-MD5: %s | PRODUCED-BY: %s | DISPOSITION: %s | WHERE: %s | SINCE: %s"
          % (r["key"], r["md5"], (r["producer"] or "—"), r["disposition"], where, r["since"]))
    for r in keep32:
        owner = [k for k, v in facts["on_disk"].items() if v == r["md5"]][0]
        A("- NEED-KEY: %s | NEED-MD5: %s | PRODUCED-BY: — | DISPOSITION: 保持 | WHERE: %s 的盘上现值 (受保护 5 件之一) | SINCE: %s"
          % (r["key"], r["md5"], owner, r["since"]))
    for k in manual_no_md5:
        since = [n.get("since") for n in facts["sw_needs"] if n.get("key") == k][0]
        A("- NEED-KEY: %s | NEED-MD5: — | PRODUCED-BY: — | DISPOSITION: 退休 | WHERE: 该 need 无 md5 字面量 (同类过期 need·手工登记) | SINCE: %s"
          % (k, since))
    A("")
    A("★**§2-3 · 本单【只出建议表】的边界 (★不许直接改 `state/fragments/sw.yaml` 的 need 条目★)** ★")
    A("")
    A("- 本单**没有**改任何一条 need 的正文 (`state/fragments/sw.yaml` 的 need 条目一个字没动)")
    A("- 本单**没有**改任何锚点 md5 (`SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点块一个字没动)")
    A("- 上表的处置词**只是建议** ⇒ 要不要真把某些 need 标成 closed / 改写, **归 main 裁**")
    A("- ★**判据**: 一条 need 能不能退休, 只有一条机器判据 ⇒ ★**它要的「H-1 重锚」这件事有没有被 ISS-275 的【判决源换源】取代** ⇒ 被取代了 ⇒ 退休; 没被取代 ⇒ 不许退休 ★")
    A("")
    A("<!-- H3-REG:END -->")
    txt = "\n".join(L)
    outp = os.path.join(HERE, "h3_reg_block.txt")
    with open(outp, "w", encoding="utf-8") as f:
        f.write(txt)
    print("stale32=%d pref=%d keep=%d needs=%d manual=%d" % (len(stale32), len(pref_rows), len(keep32), len(need_keys), len(manual_no_md5)))
    print("wrote", outp, len(txt), "chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
