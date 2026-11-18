#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/_close_iss047.py —— ISS-047 状态推进: fixing → fixed (并落 fix_ref)
=====================================================================
作者: mech-lead (结构总工) · 2026-11-02 · 交卷后自推状态

★为什么要自己推 (不能只交卷): 交卷 ≠ 状态推进。ISS-047 owner=mech-lead,
  status 一直 fixing ⇒ 项目总工的队列会当成"没人做"再派一次。
  交卷时必须把状态一起推到 fixed + verify_by=main。

★写文件铁律:
  - `state/issue_log.yaml` ⇒ **yaml.safe_dump + 原子写** (tmp + fsync + os.replace),
    **禁止 open(p,"w") 覆盖** (并发下会把整个 issue log 写成半截)。
  - `state/fragments/mech.yaml` ⇒ **必须走 `state/frag_write.py`** (本脚本只 import 它的
    `update_fragment`, 不自己 open)。分片已由 `MECH/_frag_update_iss047.py` 落好, 本脚本不再重复写。

边界:
  本脚本只改 `state/issue_log.yaml` 里 **ISS-047 这一条**。
  不碰 PROJECT_TRACKER.md / DECISIONS.md / HW/ / SW/ / 打印包 / 其他 issue。

用法:
    cd projects/smart_glasses && python3 MECH/_close_iss047.py [--dry-run]
退出码: 0 = 已落盘 / 2 = 找不到 ISS-047 (中止, 不落盘)
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
STATE = os.path.join(PROJ, "state")
LOG = os.path.join(STATE, "issue_log.yaml")

FIX_REF = (
    "MECH/ISS047_FOV_TABLE.md (ISS-047 复核交卷: hw-lead 指摘逐条核对 + 完整五数对应表 "
    "[对角FOV/水平FOV/垂直FOV/垂直半视场/俯角余量] × 现行定案+备选+旧基线 × 直行/等距 × 三档 "
    "+ 每个俯角下「正前方是否在画面内」判定表[名义余量/有效余量双列] + 俯角上限→h_max 三判据 "
    "+ 4 路线映射 + 上游口径不一致 2 处 + 未决 6 项) "
    "+ MECH/iss047_fov_table.py (自证脚本, rc=0, FAIL 0 / WARN 0, 自检 10 条) "
    "+ MECH/iss047_doc_check.py (文档一致性检查, 220/220 一致, rc=0) "
    "+ MECH/_frag_update_iss047.py (分片口径更新: claims 9 条 + artifacts 3 条 + need 1 条) "
    "+ MECH/MECH_BUDGET.md §1.5/§1.5.1/§1.5.2/§4(c) 重基线改写 "
    "+ MECH/CAMERA_WINDOW_SPEC.md §B5 基线标注 "
    "+ MECH/camera_window_check.py 头部基线提示 "
    "+ HANDOFF/2026-11-02_mech-lead_ISS047_FOV俯角表复核.md "
    "+ state/fragments/mech.yaml (interface_claims 9 条)"
)

CLOSE_NOTE = (
    "★2026-11-02 09:5x mech-lead 交卷并自推状态 (owner=mech-lead)。\n"
    "【hw-lead 的指摘成立, 旧表整表作废】旧 §1.5 用「半对角 50° − 俯角 − 余量 10° → 可接受最大偏置 ≤40°」"
    "判**垂直俯角** —— 错。**垂直俯角由垂直半视场决定, 与对角半角无关**: 16:9 理想靶面对角 100° 直行口径下"
    "垂直半视场只有 **30.30°** (本单复现, 与 hw-lead 的 30.3° 一致), 旧结论 40° **高估 9.70°**。\n"
    "★【旧表还有另外两个错, 本单一并补出】① 把**垂直俯角**与**水平偏置**放同一列比 —— 两者由不同的量决定 "
    "(垂直俯角→垂直半视场; 水平偏置→水平半视场), 物理上不可互换; ② 「对角 FOV」**没带投影模型** —— "
    "同一「对角 120°」直行口径垂直半视场 42.55°, 等距(鱼眼)口径只有 31.80°, **差 10.75°** ⇒ "
    "引用 FOV 必须带三元组 (投影模型 + 读出窗口 + 对角 FOV)。\n"
    "★★【基线已变, 整表重算】老板 **2026-11-02 09:41 拍板「使用D」** ⇒ sensor = **onsemi AR0234CS "
    "1920×1200@60 整幅不裁剪** (`PROJECT_TRACKER.md` §(1.56)); 老板 10-25「禁止 ROI/crop」⇒ 不做 1080p 裁切。\n"
    "  ⇒ 现行定案 = AR0234CS 整幅 + 等距(鱼眼) + 对角 120° (f=**3.2432mm**) ⇒ "
    "**垂直半视场 31.80° / 水平半视场 50.88°** (与 SW `SW/tools/fov_scale_check.py` 及 hw-lead 分片 "
    "`sensor_lens_focal_equidistant` 三方一致)。\n"
    "★【结构侧结论 (本单真正的价值)】① **俯角 ≤25° 基线站得住, 且从「临界点」变成「有余量的设计点」**: "
    "垂直半视场比旧 OV04C10 基线 (29.53°) **多 2.27°** ⇒ 俯角 25° 名义余量 **+6.80°** (旧 +4.53°), "
    "扣边框遮挡后**有效余量 +4.89°** ⇒ `h_max` 仍 **13.99/14.92/16.32mm** (d=30/32/35) —— "
    "**换 sensor 不改结构基线, 但给了镜框上沿 2.27° 的造型自由度**。\n"
    "★【新发现: 边框遮挡吃的是「正前方那一侧」】摄像头装镜框上沿、光轴朝下俯 ⇒ 正前方对应画面**上半部** ⇒ "
    "镜框上沿正好挡住它 ⇒ 判「正前方是否在画面内」必须用**有效余量** (名义余量 − 遮挡角 1.91°), "
    "不能只看名义余量。**现行定案下俯角 30° 名义 +1.80° 但有效 −0.11° ⇒ 正前方被镜框上沿遮掉** ⇒ "
    "**25°~30° 之间都不行**; 俯角 32° 名义 −0.20° ⇒ 根本掉出画面。\n"
    "★【零余量位置做不到】硬上限 (有效余量=0) 29.89° ⇒ `h_max(d=35)` = **20.12mm**, **比 MECH 原上界 20mm "
    "还高 0.12mm** ⇒ 任何设计点都必须留余量 (判据 B' 有效余量 4° ⇒ 16.99mm)。\n"
    "★【交付物】`MECH/ISS047_FOV_TABLE.md`: ① hw-lead 指摘逐条核对 (B2) ② **完整五数对应表** (B3) —— "
    "现行定案 + 备选 + 旧基线 + 作废裁切口径 四组, 每组 × 直行/等距 × 三档对角 FOV, 五数齐全; "
    "③ **每个俯角下的「正前方是否在画面内」判定表** (B3.1/B3.2, 名义余量/有效余量双列, 四档标记: "
    "在画面内 / 临界 / 遮挡后掉出 / 掉出) ④ 俯角上限 → h_max 三判据 + 建议判据 B' (B4) ⑤ 结构侧照抄清单 (B5) "
    "⑥ 与上游口径不一致 2 处 (B6) ⑦ 未决 6 项 (B7)。\n"
    "★【自证】`python3 MECH/iss047_fov_table.py` → **rc=0, FAIL 0 / WARN 0** (自检 10 条); "
    "`python3 MECH/iss047_doc_check.py` → **220/220 数字一致, rc=0** (文档里的数不许靠人眼核对)。\n"
    "★【与上游口径不一致 2 处, 需上游回写, 我不追进度只标出来】① `HW/DISPLAY_SENSOR_CHAIN.md` §2.2/§2.3 "
    "路线 C 的 `f=1.2704mm` 是**直行**口径的焦距 (等距 120° 需 f=2.1015mm), 且同行的「垂直半视场 29.53°」"
    "取自 OV04C10 **全幅** (1080p 裁切窗口应是 29.42°) ⇒ 三个数混了两个口径 (路线 C 已被 D 取代, 不追); "
    "② 同文件路线 D 旧写「对角 116.75° / 垂直半 28.62°」= **裁到 1080p** 的口径, 现行定案是**整幅不裁剪** ⇒ "
    "应为 对角 120.00° / 垂直半 31.80° / 水平半 50.88°。\n"
    "★【待 PM 拍板 1 项 (已登记 need, key=iss047_margin_criterion_decision)】俯角余量口径取 "
    "**B' 有效余量≥4°** (推荐, 含边框遮挡 ⇒ ≤25.89°, h_max d=35 = 16.99mm) / **B 名义余量≥4°** "
    "(≤27.80°, 18.45mm) / **C 名义≥10°** (≤21.80°, 14.00mm)? 差 1.91°/6.00° ⇒ 差 h_max 1.47mm/3.45mm ⇒ "
    "镜框上沿高度与摄像头能否藏在眉毛里。**我的建议 B'**: 遮挡是实物必然 (窗口座沉孔 0.35mm 就要占深度), "
    "名义余量留不住。★**无论选哪个, 现行定案下 25° 基线都站得住 (有效余量 +4.89°)。**\n"
    "★【诚实边界】本单**全部 [推算], [实测] 条数 = 0** —— 0 件打印件 / 0 片镜头样片 / 镜头未下单 / "
    "原厂 datasheet 未到。遮挡角 1.91° 是几何推算, 打印件出来后必须实测复核 (正前方标靶在画面中的垂直位置)。"
    "未改 HW/ SW/ PROJECT_TRACKER.md DECISIONS.md / 打印包; 未联系任何供应商/原厂/模组厂。"
)


def atomic_write_yaml(path: str, data: dict) -> None:
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp",
                               dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    dry = "--dry-run" in sys.argv

    with open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc.get("issues")
    items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])

    hit = 0
    for it in items:
        if not isinstance(it, dict) or it.get("id") != "ISS-047":
            continue
        hit += 1
        print(f"[before] ISS-047 status={it.get('status')!r} fix_ref={it.get('fix_ref')!r}")
        it["status"] = "fixed"
        it["fix_ref"] = FIX_REF
        it["verify_by"] = "main"
        note = str(it.get("note") or "")
        # ★幂等护栏: 串必须与 CLOSE_NOTE 实际写入的一致, 否则重跑会重复追加
        if "mech-lead 交卷并自推状态" not in note:
            it["note"] = note + "\n\n" + CLOSE_NOTE
        print(f"[after ] ISS-047 status='fixed' verify_by='main' fix_ref 已落 ({len(FIX_REF)} B)")

    if hit != 1:
        print(f"❌ 找到 {hit} 条 ISS-047 (应为 1) —— 中止, 不落盘")
        return 2
    if dry:
        print("[dry-run] 未落盘")
        return 0

    doc["issues"] = items
    atomic_write_yaml(LOG, doc)
    print("✅ issue_log.yaml 已原子更新 (ISS-047 fixing → fixed, fix_ref + verify_by 已落)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
