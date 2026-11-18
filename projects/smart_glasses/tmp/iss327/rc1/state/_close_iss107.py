#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-107 状态推进: fixing -> fixed (并落 fix_ref) —— mech-lead 交卷后自推。

★为什么要自己推 (不能只交卷): `state/advance.py` 的 in_flight 规则 = "同一 agent 名下只要有
  status==fixing 的 issue, 该 agent 本轮就不再派新活" ⇒ ISS-107 一直卡在 fixing, mech-lead 名下
  11 条 open 待办 (ISS-017/024/025/027/047/052/065/066/076/092/103) 全被挡住 —— 上一轮就是这么
  锁死整个 agent 队列的。**交卷 ≠ 状态推进**, 必须一起做。

★写文件铁律: 原子写 (tmp + fsync + os.replace), 禁止 open(p,"w") 覆盖 issue_log.yaml。

用法: python3 state/_close_iss107.py [--dry-run]
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

FIX_REF = (
    "MECH/PCB_MOUNT_PIN_SET2.md (结构侧采纳 PIN-SET-2 的独立复算文档, 31 项 FAIL 0 / WARN 3) + "
    "MECH/pinset2_mech_check.py + MECH/pinset2_mech_check.json (自证脚本, rc=0) + "
    "MECH/BOARD_WIDTH_15MM.md §5.1/§5.2/§5.3/§6 M-4/§7 R-3/§8 N2/N4/§9/§10 + "
    "MECH/CLEARANCE_FIX.md (骨架接口表/§B5 卡点2/§5.5 骨架 1销→2销一圆一菱/代价) + "
    "MECH/fit_check.py + MECH/board_width_15mm_check.py + MECH/cross_review_check.py (文案跟改) + "
    "MECH/_frag_update_iss107.py (分片原子写, 走 state/frag_write.py) + "
    "MECH/_apply_pinset2_docs.py (20 条文档替换, 幂等) + "
    "HANDOFF/2026-10-29_mech-lead_ISS107_pcb_mounting改PIN-SET2.md (B1-B6) + "
    "state/fragments/mech.yaml (interface_claims.pcb_mounting 已改 PIN-SET-2: 2x⌀2.0H7+2x⌀1.4, "
    "并补 canon=pin-set-2:2x⌀2.0h7+2x⌀1.4 对齐 hw-lead; answers[iss105_pcb_outline_sync_60x15] 追加作废更正)"
)

CLOSE_NOTE = (
    "★2026-10-29 00:1x mech-lead 交卷并自推状态 (owner=mech-lead)。\n"
    "【本单做了什么】① 分片 interface_claims.pcb_mounting 从旧口径 '2xM1.2+1x⌀2.0H7' 改成 hw-lead ISS-049 "
    "已定版的 PIN-SET-2 = '2x⌀2.0H7+2x⌀1.4' (走 state/frag_write.py 原子写, 禁 open(p,\"w\")); "
    "② 同步清 MECH/ 下 5 个文件 20 处老口径引用 (BOARD_WIDTH_15MM.md 9 / CLEARANCE_FIX.md 4 / "
    "fit_check.py 3 / board_width_15mm_check.py 3 / cross_review_check.py 1), 幂等脚本连跑 3 次 = 改 0 条; "
    "③ 出 B1-B6 交接单。\n"
    "★【一个任务书没写、但不做就消不掉冲突的坑】state/merge.py 的冲突判定比的是 canon 完整串, 而 canon_of() "
    "**不去 'PIN-SET-2:' 方案名前缀** —— 实测 canon_of('PIN-SET-2:2x⌀2.0H7+2x⌀1.4')='pin-set-2:2x⌀2.0h7+2x⌀1.4' "
    "≠ canon_of('2x⌀2.0H7+2x⌀1.4') ⇒ 只把 value 写成裸串, 冲突照样判。已按本项目既有先例 "
    "(hw-lead 对 skeleton_extent 用 canon: 字段对齐, state/fragments/hw.yaml:682) 给 mech 侧补显式 "
    "canon: pin-set-2:2x⌀2.0h7+2x⌀1.4 ⇒ 两边 comparable canon 逐字节相等。\n"
    "【验收依据 (交卷自评 + 可复现)】实跑 python3 state/merge.py → 冲突数 **1 → 0**, rc=0 (改前输出: "
    "'产出 73 | 阻塞 32 (高危 26) | 未闭合需求 47 | 冲突 1 | 健康度 red' + "
    "'⚠️ 冲突 pcb_mounting: {hw-lead: PIN-SET-2:2x⌀2.0H7+2x⌀1.4, mech-lead: 2xM1.2+1x⌀2.0H7}'; "
    "改后: '冲突 0', 且 --for mech-lead 切片显示【全局冲突】0 项); 实跑 python3 state/gate_check.py → "
    "**Q1 18/18** (mech-lead 6/6); 实跑 python3 MECH/pinset2_mech_check.py → rc=0, **复算项 31 | FAIL 0 | WARN 3**; "
    "实跑 python3 MECH/_apply_pinset2_docs.py → 改 0 条 / 跳过 20 条 (幂等)。\n"
    "【诚实边界】3 个 WARN **全部**是'打印包契约 (MECH/print/GEOM_SPEC_REVA.md) 还是老口径', 不在本单授权范围: "
    "① PCB 定位让过孔 1→2 个; ② M1.2 让过孔中心距 40.00→44.00mm; ③ 打印件 PCB 定位板长 50.00→60.00mm "
    "⇒ **打印包改版授权在 PM 手上**, 本单没动 MECH/print/** 与任何 STL。结构侧独立复算结论: "
    "4/4 孔与 SoC 逃线带 X[20.20,31.80]×Y[2.70,12.30] 的 2D 重叠 = **0.0000 mm²** (真圆∩矩形解析积分); "
    "老口径按最有利假设复算 3/3 孔压带 (M1.2 压 Y 0.50mm / ⌀2.0 压 2.00×2.00mm) ⇒ 加宽不解, 必须沿板长移出。"
    "打印件实测尺寸 **0 件已打** [0数据]; JBD 座体 A/B/C 尺寸页 [0数据]; 未联系任何供应商/原厂。"
)


def main() -> int:
    dry = "--dry-run" in sys.argv
    with open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc.get("issues")
    items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])

    hit = 0
    for it in items:
        if not isinstance(it, dict) or it.get("id") != "ISS-107":
            continue
        hit += 1
        print(f"[before] ISS-107 status={it.get('status')!r} fix_ref={it.get('fix_ref')!r}")
        it["status"] = "fixed"
        it["fix_ref"] = FIX_REF
        note = str(it.get("note") or "")
        if "ISS-107 交卷" not in note:
            it["note"] = note + "\n\n" + CLOSE_NOTE
        print(f"[after ] ISS-107 status='fixed' fix_ref 已落 ({len(FIX_REF)} B)")

    if hit != 1:
        print(f"❌ 找到 {hit} 条 ISS-107 (应为 1) —— 中止, 不落盘")
        return 2
    if dry:
        print("[dry-run] 未落盘")
        return 0

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
    print("✅ issue_log.yaml 已原子更新 (ISS-107 fixing → fixed, fix_ref 已落)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
