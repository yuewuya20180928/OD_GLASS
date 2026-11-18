#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 08:5x · job 775d9893「ARS45 继续执行后继计划」
★ISS-279 (sw-lead) / ISS-280 (hw-lead) 独立复验 ⇒ 落 verified★
★main 自己实跑 4 条闸 + 亲自 md5 受保护 5 件 + 亲自查交卷单 B1~B6 + 亲自读分片 claim★
★**只动 1 个文件: state/issue_log.yaml**★
★**不碰真源 / 分片 / 板 / 网表 / 脚表 / BOM / 任何既有门禁脚本**★
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0850_main_verify279_280"
TODAY = "2026-11-17"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


VERIFY_279 = {
    "fix_ref": ("HANDOFF/2026-11-17_sw-lead_ISS279_SW侧板侧输入收口.md · "
                "SW/BOARD_ONEPASS_SW_SYNC.md (md5 b8f935db333c16fa1051f0b06ae3e6ec) · "
                "SW/tools/check_onepass_sw_sync.py (md5 cd059073fb91b75db30391415ed5bd2a)"),
    "verify_note": (
        "★**main 2026-11-17 08:4x~08:5x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
        "① `SW/tools/check_onepass_sw_sync.py` ⇒ **rc=0 (W1~W6 全 OK)** ★实测摘要: W1 条目 **8 条 / 9 字段齐全非空** · "
        "W2 归属步分布 S2=1 S4=1 S8=1 S9=2 S10=3 · W3 每条 criterion 的脚本文件都在盘上 · W4 覆盖度 ①~⑧ 八条一条不缺 · "
        "W5 **8 个现状探针: 清单里的现状值 == 盘面实测** · W6 受保护 5 件 md5 逐字节不变 + 台账 §1 锚点块两个 md5 未被手改 "
        "② `--selftest` ⇒ **rc=0 (反向 9/9 全抓到)** ★(★含要求外新增: ⑥「台账 §1 锚点块里板的 md5 被手改 ⇒ W6 红」★) "
        "③ ★**受保护 5 件 md5 = main 亲自跑 md5sum 逐字节核对**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17`) · "
        "`.kicad_pro 3e504d2be83152e337949723e909be1b` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · "
        "BOM `94642d07a69e8d60dd2af57f69b93607` ⇒ **5/5 与基线逐字节相同** "
        "④ 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS279_SW侧板侧输入收口.md` (37 738 B) **B1~B6 六块齐全** ⑤ "
        "`state/fragments/sw.yaml` 内 **iss279 claim + 3 artifact (SW/BOARD_ONEPASS_SW_SYNC.md / SW/tools/check_onepass_sw_sync.py / 交卷单) 在位** + "
        "need `iss279_sw_to_board_inputs` 已开给 main ⇒ **交卷完整** ⇒ 落 verified ★ "
        "★**本单的价值 (★记一笔★)**: 「板只改一次」那一趟的三条腿 (HW=ISS-277 / MECH=ISS-278 / SW=ISS-279) 到此齐 ⇒ "
        "★**板改完那一刻, SW 侧不再是【当场必红且无路可走】, 而是有清单 + 有闸 + 有台账链头机制接住**★"
    ),
}

VERIFY_280 = {
    "fix_ref": ("HANDOFF/2026-11-17_hw-lead_ISS280_提交时序守卫.md · "
                "HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md (md5 106ba9e041123e08bf22bac4a91dd356) · "
                "HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md (md5 d9e71cb5e3b620118e5aa6ab29240f2e) · "
                "HW/check_onepass_commit_order.py (md5 2bf5d4d2c1c742493a2e32c61597839a)"),
    "verify_note": (
        "★**main 2026-11-17 08:4x~08:5x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
        "① `HW/check_onepass_commit_order.py` ⇒ **rc=0 (D0/D1/D2/D3/D4/D4b/D5/D6 全 PASS)** ★实测摘要: "
        "D0 权威页存在且 INV-1~INV-4 齐全 + 网表/脚表/BOM md5 未变 · D1 找到 3 处「B 类终段步 = 最后跑」表述 (★第 21 行★) · "
        "D2 找到「只允许变一次 + 同趟 + S4 + S8」表述 · D3 **3 处集合断言全部被后文撤回订正覆盖 (断言行 15/16/342 · 撤回行 21/347)** · "
        "D4 盘上板 md5 `611b869e13518c3c023fb178f91a0075` == 台账基线 md5 (**变更区 0 行 = 板至今没变过**) · D4b `.kicad_pro` md5 == 台账基线登记值 "
        "⇒ 未被绕过改动 · D5 变更区 0 行 (≤1 ⇒ 板 md5 至多变一次) · D6 无需留证绑定 (本单零写板) "
        "② `--selftest` ⇒ **rc=0 (反向 11/11 全抓到 · 要求 ≥6)** ★(★含要求外新增: ⑩「.kicad_pro 偷改一个字节 ⇒ D4b 红」+ "
        "⑪「历史对照: 用 ISS-280 之前的作业包 ⇒ D1/D3 红 ⇒ 证明闸真能抓住原病灶」★) "
        "③ ★**受保护 5 件 md5 = main 亲自跑 md5sum 逐字节核对**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17`) · "
        "`.kicad_pro 3e504d2be83152e337949723e909be1b` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · "
        "BOM `94642d07a69e8d60dd2af57f69b93607` ⇒ **5/5 与基线逐字节相同** "
        "④ 交卷单 `HANDOFF/2026-11-17_hw-lead_ISS280_提交时序守卫.md` (33 014 B) **B1~B6 六块齐全** ⑤ "
        "`state/fragments/hw.yaml` 内 **iss280 claim + 3 artifact (COMMIT_ORDER / MD5_LEDGER / check_onepass_commit_order.py) 在位** ⇒ **交卷完整** ⇒ 落 verified ★ "
        "★**本单的价值 (★记一笔★)**: 「板只改一次」从此有了一道【提交时序守卫】⇒ ★**改板次数从「靠人记着」变成「机器判 ≤1 次」**★ "
        "★**两条 main 已核实的诚实披露 (照登, 不代拍)**: "
        "**(a) D4 口径细化**: 死守「盘上 md5 == 基线」会让那一次合法改板永远红 ⇒ 改成「== 台账**最后一次**登记值」 (0 行时 == 基线, 1 行时 == 改后 md5) ⇒ **抓的仍是「绕过本单偷改板」** "
        "**(b) 已披露副作用**: `state/check_pcb_drc.py` 的 C5 会跑生成器 ⇒ 把 `GEN_SELF_CHECK.txt` / `LAYOUT_RULES.md` / `STACKUP.md` / `_frame_reference.kicad_pcb` "
        "重写一遍 (★这 4 件嵌了生成时刻 + 随机 UUID ⇒ 逐字节不稳定★) ⇒ **★现役板 `demo_mainboard.kicad_pcb` 不在生成器输出里, 板 md5 + mtime 双重未变已证★**"
    ),
}


def main() -> int:
    shutil.copy2(LOG, BAK)
    lines = open(LOG, encoding="utf-8").read().split("\n")

    def bounds(iid):
        start = end = None
        for i, ln in enumerate(lines):
            if ln.startswith("- id: "):
                if start is not None:
                    end = i
                    break
                if ln[len("- id: "):].strip() == iid:
                    start = i
        if start is None:
            return None, None
        if end is None:
            end = len(lines)
        return start, end

    for iid, spec in (("ISS-279", VERIFY_279), ("ISS-280", VERIFY_280)):
        s, e = bounds(iid)
        if s is None:
            print("❌ 找不到 %s" % iid)
            return 2
        blk = lines[s:e]
        hit = {"status": False, "fix_ref": False, "vr": False, "vd": False, "vb": False}
        for j, ln in enumerate(blk):
            st = ln.strip()
            if st in ('status: fixing', 'status: "fixing"'):
                blk[j] = '  status: "verified"'
                hit["status"] = True
            elif st.startswith("fix_ref:") and ("null" in st or st.split("fix_ref:", 1)[1].strip() == ""):
                blk[j] = "  fix_ref: %s" % q(spec["fix_ref"])
                hit["fix_ref"] = True
            elif st.startswith("verify_result:") and "null" in st:
                blk[j] = '  verify_result: "pass"'
                hit["vr"] = True
            elif st.startswith("verify_date:") and "null" in st:
                blk[j] = "  verify_date: %s" % q(TODAY)
                hit["vd"] = True
            elif st.startswith("verify_by:") and ("null" in st or st.split("verify_by:", 1)[1].strip() in ("", '""')):
                blk[j] = '  verify_by: "main"'
                hit["vb"] = True
        while blk and blk[-1].strip() == "":
            blk.pop()
        blk.append("  verify_note: %s" % q(spec["verify_note"]))
        lines[s:e] = blk
        print("  %s 命中: %s" % (iid, hit))

    open(LOG, "w", encoding="utf-8").write("\n".join(lines))

    # ---------- 自检: 全量复核 ----------
    d2 = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    ids = {it["id"]: it for it in d2["issues"]}
    print("  问题单总数 = %d" % len(d2["issues"]))
    for iid in ("ISS-277", "ISS-278", "ISS-279", "ISS-280"):
        it = ids[iid]
        print("  %s -> %-9s owner=%-9s verify_by=%-6s verify_result=%-5s note=%d字节" % (
            iid, it["status"], it.get("owner"), it.get("verify_by"), it.get("verify_result"),
            len(it.get("verify_note") or "")))
    # 其它条目没被动过: 逐条比 status/verify_result 与 BAK
    d0 = yaml.safe_load(open(BAK, encoding="utf-8")) or {}
    b0 = {it["id"]: it for it in d0["issues"]}
    drift = []
    for iid, it in ids.items():
        b = b0.get(iid)
        if b is None:
            drift.append((iid, "新增"))
            continue
        for k in ("status", "owner", "verify_result", "verify_date", "verify_by", "fix_ref"):
            if (it.get(k) or "") != (b.get(k) or ""):
                drift.append((iid, k))
    print("  与 BAK 比对的字段漂移 = %d 处 %s" % (len(drift), drift))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
