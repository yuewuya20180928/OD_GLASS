#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261116_2005_land_249_open_253_254.py —— ★main 20:0x 记账★

★**做三件事** ★
  ① ★**ISS-249 落 verified** (★main 本机独立复核 10 条 rc 全过·详见 note★)
  ② ★**新开 ISS-253** (MECH 侧 H-1 重锚 · owner=mech-lead · status=fixing) ★
  ③ ★**新开 ISS-254** (SW 侧 H-1 重锚 · owner=sw-lead · status=fixing) ★

★**规矩**: ★**先落 fixing 再 spawn** (★关掉兄弟 cron 同分钟重复派活的窗口★) ★
★**零落表**: 网表/脚表/BOM/板/`.kicad_pro` 一个字节没动 ★
"""
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

VERIFY_NOTE = """
★★**main 2026-11-16 19:5x~20:0x 独立复核 (★本机实跑, 不采信自述★)** ★★
★**① F1 真落表**: `HW/check_iss247_f1_landed.py` **rc=0** (S1~S6 全绿) · `--selftest` **rc=0 · 11/11** ★
★**② R3 矛盾判据**: `HW/check_netlist_contradiction_r3.py` **rc=1 · FINDINGS=2 (恰 F2+F3)** ⇒ ★**F1 已消失** ★
  ⇒ ★**main 裁 (need `iss249_r3_rc_semantics_to_main` 的答复)**: ★**rc 语义不许动** ★
  ★★**理由**: 该脚本 rc 语义 = 「有未修缺陷 ⇒ 红」⇒ F2/F3 两条真缺陷还在 ⇒ **动 rc 就等于把两条真缺陷藏起来 = 假绿** ★★
  ⇒ ★**交卷口径按「结论 ✅ 恰 2 条 + rc=1」记** ★
★**③ 落表清零度**: `--expect-resolved` **rc=1 (仍 18 条)** ⇒ ★**V-2/V-3/V-4 一条没代拍 = 正确** ★
★**④ 四道尺子**: `check_netlist` **0** · `check_netlist_pins` **0** · `check_sch_erc` **0** · `check_sch_pinfull` **0 (584=584 · K=0)** ★
★**⑤ 受保护件**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★**逐字节未变** ★
  网表 `16ac89f7…` (F1 落表后) · 脚表 `ef436a37…` · BOM `2a730574…` ★
★**⑥ main 自查到的一条硬事实 (★进 MEMORY 级教训★)**: ★**`.kicad_sch` 的 md5 永久不可当锚点** ★
  ⇒ ★**实测 `check_sch_pinfull.py` / `check_sch_erc.py` 内部会 subprocess 调 `gen_kicad_sch.py`** ⇒ ★**跑一次门禁就重铸 UUID** ★
  ⇒ ★**归一化后 11/11 逐字节相同 ⇒ F1 对原理图图形零影响** ★ ⇒ ★**任何以 .kicad_sch md5 为锚的判据都必须改成【内容归一化】口径** ★
★**⑦ 下游 H-1 重锚 (★本轮 main 已派★)**: 网表 md5 变了 ⇒ SW/MECH 两侧的锚点过期 ⇒
  ★**MECH**: `MECH/check_demo_struct_truth.py` **rc=2 (21/23 · FAIL G5b+C21)** ⇒ ★**ISS-253 → mech-lead** ★
  ★**SW**: `SW/tools/check_demo_panel_spec.py` **rc=1 (R6)** + `SW/tools/timing_check.py` **rc=1 (自测 69/71)** ⇒ ★**ISS-254 → sw-lead** ★
  ⇒ ★**重锚只改【网表那一条】, 脚表/BOM/板/`.kicad_pro` 四件一个字节不许动, 且必须留反向用例** ★
★**边界**: 零落表 (本单) · 零外发 · 零实物 · 不碰布线/布局/板框 · 不替老板拍板 (V-2/V-3/V-4 一条没拍) ★
""".strip()

ISS253 = {
    "id": "ISS-253",
    "title": ("★★[主线内·MECH 侧·H-1 重锚·内部活] ★★`MECH/check_demo_struct_truth.py` 因 ISS-249 合法落表而 "
              "锚点过期 ⇒ **rc=2 (21/23 · FAIL G5b+C21)** ⇒ ★**只重锚网表那一条 md5 (611c3ba3… → 16ac89f7…), "
              "判据逻辑一个字节不许动** ★"),
    "severity": "medium",
    "owner": "mech-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-19",
    "status": "fixing",
    "note": ("★**main 2026-11-16 20:0x 实测派单** ⇒ `MECH/check_demo_struct_truth.py` rc=2 (21/23 · FAIL G5b+C21)\n"
             "★**根因 = 上游合法落表 (ISS-249 F1) ⇒ 网表 md5 变, 不是真源被换** ⇒ ★**只重锚** ★\n"
             "★**新锚点**: `16ac89f77c25a3f61834cc7ebcd78a7f` · ★**旧锚点留痕**: `611c3ba3db3dc7de7213063375b96d01` ★\n"
             "★**brief 全文**: `state/dispatch_briefs/ISS-253_mech_h1_reanchor.md`\n"
             "★**验收**: rc=0 · 23/23 · FAIL 0 + ★**反向用例 (改回旧 md5 ⇒ 必须变红)★** + `--selftest` 不许少 ★\n"
             "★**边界**: 零落表 · 零外发 · 不碰 HW/SW · 不改判据阈值 · 不替老板拍板 ★"),
}

ISS254 = {
    "id": "ISS-254",
    "title": ("★★[主线内·SW 侧·H-1 重锚·内部活] ★★`SW/tools/check_demo_panel_spec.py` rc=1 (R6 锚点) + "
              "`SW/tools/timing_check.py` rc=1 (自测 69/71, 掉的 2 条 = 同源 md5 锚点断言) ⇒ ★**只重锚网表那一条 md5** ★"),
    "severity": "medium",
    "owner": "sw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-19",
    "status": "fixing",
    "note": ("★**main 2026-11-16 20:0x 实测派单** ⇒ 两个 SW 门禁因 ISS-249 合法落表而锚点过期\n"
             "★**新锚点**: `16ac89f77c25a3f61834cc7ebcd78a7f` · ★**旧锚点留痕**: `611c3ba3db3dc7de7213063375b96d01` ★\n"
             "★**本单与 ISS-250 同一个 sw-lead 会话一起做 (★铁律: 一个 agent 同时只开一个写会话★) ⇒ brief 全文 `state/dispatch_briefs/ISS-250_part1_reanchor_and_close.md` 的 ① 号件** ★\n"
             "★**验收**: `check_demo_panel_spec.py` rc=0 · `timing_check.py` rc=0 (自测 71/71) + ★**反向用例** ★\n"
             "★**边界**: 零落表 · 零外发 · 不碰 HW/MECH · 不改判据逻辑 · 不替老板拍板 ★"),
}


def main() -> int:
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues")
    by_id = {it.get("id"): it for it in issues}

    it = by_id.get("ISS-249")
    if it and it.get("status") not in ("verified", "closed"):
        it["status"] = "verified"
        it["verify_result"] = "pass"
        it["verify_by"] = "main"
        it["verify_date"] = TODAY
        it["note"] = (str(it.get("note") or "") + "\n" + VERIFY_NOTE).strip()
        print("✔ ISS-249 ⇒ verified (main 独立复核)")
    else:
        print(f"⚠ ISS-249 已是 {it.get('status') if it else '缺失'} ⇒ 幂等跳过")

    for new in (ISS253, ISS254):
        if new["id"] in by_id:
            print(f"⚠ {new['id']} 已存在 ⇒ 幂等跳过")
            continue
        issues.append(dict(new))
        print(f"＋ 新开 {new['id']} → {new['owner']} (fixing)")

    bak = LOG + ".bak_20261116_2005_land249_open253_254"
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_20261116_2005"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=100000)
    os.replace(tmp, LOG)
    print(f"✔ 已写盘 (备份: {os.path.basename(bak)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
