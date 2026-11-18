#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/_frag_update_iss047.py —— ISS-047 (owner=mech-lead) 分片更新
=====================================================================
按 `state/frag_write.py` 协议原子写 `state/fragments/mech.yaml`:
  - 更新两个**已过期**的 interface_claims (camera_window / camera_fov_16x9)
  - 新增 ISS-047 的口径类 claims (垂直半视场 / 俯角上限 / 投影模型 / 有效余量)
  - 登记 artifact (ISS047_FOV_TABLE.md + 两个脚本)
  - 登记 need (PM 拍板俯角余量口径 B' vs B vs C) —— **带 key + to + since**
  - 更新 status

★写文件铁律: 分片只经 `state/frag_write.py` 的原子写路径 (tmp + fsync + os.replace),
  禁 open(p,"w")。本脚本只 import frag_write, 不自己写文件。
★规范值纪律: interface_claims.value 必须是**短规范值** (≤40 字符, 中文占比 ≤0.35,
  不含句读/散文词), 否则合并器会标 "散文"、不参与冲突比较。
  落盘前先跑 merge.is_prose() 自检, 有散文就中止 (分片保持原样)。

用法: python3 MECH/_frag_update_iss047.py [--dry-run]
退出码: 0 = 已落盘 / 1 = 有散文值 (中止, 未落盘) / 2 = 出错
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment, load_fragment  # noqa: E402
from merge import is_prose  # noqa: E402

AGENT = "mech-lead"
TODAY = "2026-11-02"

# ---------------------------------------------------------------- interface_claims
# (key, value, note) —— value 必须是短规范值
CLAIMS = [
    # --- 更新既有 camera_window (旧值 '俯角20-32度/凹进<=1.5mm' 口径已作废) ---
    ("camera_window", "俯角<=25deg/凹进<=1.0mm",
     "★ISS-047 复核 (2026-11-02) 重写: 俯角上限由旧 '20-32度' 收窄为 <=25deg; "
     "依据 = 现行定案 AR0234CS 整幅 等距120度 垂直半视场 31.80deg - 4deg 工程余量; "
     "前顶点凹进 <=1.0mm (1.0mm 遮挡 1.91deg, 吃的是正前方那一侧)"),
    # --- 更新既有 camera_fov_16x9 (旧表是直行口径且没标投影模型/读出窗口) ---
    ("camera_fov_16x9", "AR0234CS整幅等距120度→H101.8/V63.6/半31.80",
     "★ISS-047 复核 (2026-11-02) 重写: 旧值 '对角100度→H92.2/V60.6' 是直行口径且无投影模型/读出窗口标注 "
     "⇒ 无效引用。现行定案 = AR0234CS 1920x1200 整幅不裁剪 + 等距(鱼眼) + 对角120度 "
     "(f=3.2432mm) ⇒ H101.76/V63.60/垂直半视场31.80/水平半视场50.88。★引用 FOV 必须带三元组"),
    # --- 新增 ---
    ("camera_vertical_half_fov", "31.80deg",
     "★判俯角的量 (ISS-047): 现行定案 AR0234CS 整幅 等距120度 的垂直半视场; "
     "直行口径同靶面同对角是 42.55deg (差 10.75deg); OV04C10 旧基线 29.53deg; "
     "AR0234CS 裁1080p 只有 29.42deg (裁切代价 2.38deg)"),
    ("camera_horizontal_half_fov", "50.88deg",
     "★判水平偏置的量 (与垂直半视场是两个独立量, 不可互换): 现行定案 AR0234CS 整幅 等距120度; "
     "水平偏置 10deg 的余量 +40.88deg ⇒ '装镜框上沿正中' 成立"),
    ("camera_tilt_max_deg", "25deg",
     "★俯角上限 (ISS-047 重基线): 工程基线 <=25deg; 现行定案垂直半视场31.80 ⇒ 名义4deg判据允许<=27.80deg, "
     "★有效余量4deg判据(推荐)允许<=25.89deg; 硬上限(零余量)29.89deg ⇒ h_max(d=35)=20.12mm "
     "**超过旧MECH上界20mm ⇒ 零余量位置做不到**"),
    ("camera_tilt_margin_effective", "4deg",
     "★判据B'(本单建议): 俯角余量须按**有效余量**(名义余量 - 边框遮挡角1.91deg) >= 4deg; "
     "遮挡吃的是正前方那一侧(装上沿+光轴朝下俯⇒正前方在画面上半部) ⇒ 30deg名义+1.80但有效-0.11 "
     "⇒ 25-30deg 都不行。待 PM 拍板口径"),
    ("camera_brow_h_max_mm", "16.32mm",
     "摄像头光轴中心高于用户视线的上限 h = d*tan(俯角上限); 25deg 档 d=30/32/35 取 "
     "13.99/14.92/16.32mm; MECH 原值 h=12-20mm 的上界收紧到 16.3mm; "
     "零余量位置 (29.89deg) ⇒ 20.12mm 做不到"),
    ("camera_border_occlusion_deg", "1.91deg",
     "前顶点凹进1.0mm@d=30 的边框遮挡角 atan(1.0/30); 吃上半视场=正前方侧; "
     "占现行定案垂直半视场 6.0%; 凹进1.5mm→2.86deg(9.0%) 故上限收紧到1.0mm"),
    ("camera_fov_citation_rule", "projection+window+diagFOV",
     "★ISS-047 口径铁律: 引用任何 FOV 数必须带三元组 (投影模型+读出窗口+对角FOV); 缺投影模型差10.75deg, "
     "缺读出窗口(整幅vs裁切)差2.38deg ⇒ 少任何一项该数无效。详见 MECH/ISS047_FOV_TABLE.md §B2.2"),
]

# ---------------------------------------------------------------- artifacts
ARTIFACTS = [
    ("MECH/ISS047_FOV_TABLE.md", "spec", "v1.0", TODAY,
     "ISS-047 复核交卷: ① hw-lead 指摘逐条核对 (旧表三个错: 对角半角判俯角/垂直俯角与水平偏置混列/"
     "FOV 无投影模型; 旧结论40deg高估9.70deg) ② 完整五数对应表 (对角FOV/水平FOV/垂直FOV/垂直半视场/"
     "俯角余量) × 现行定案+备选+旧基线 × 直行/等距 × 三档 ③ 每个俯角的「正前方是否在画面内」判定 "
     "(名义余量/有效余量双列, 有效余量扣边框遮挡1.91deg) ④ 俯角上限→h_max 三判据+建议判据B' "
     "⑤ 4个路线映射 ⑥ 与上游口径不一致2处 (DISPLAY_SENSOR_CHAIN 路线C/D 两行) "
     "⑦ 未决6项。全部 [推算], 0 实测"),
    ("MECH/iss047_fov_table.py", "script", "v1.0", TODAY,
     "ISS-047 自证脚本: §1 口径核验(复现16:9对角100度→垂直半视场30.30deg) §2 五数对应表(4窗口×2投影×3档) "
     "§3 正前方在画面内判定表(名义/有效双列) §4 俯角上限→h_max(判据A/B/B'/C) §5 四路线映射+上游口径不一致2处 "
     "§6 自检10条。rc=0, FAIL 0 / WARN 0"),
    ("MECH/iss047_doc_check.py", "script", "v1.0", TODAY,
     "ISS-047 文档一致性检查: 把 ISS047_FOV_TABLE.md 的 220 个数抽成清单现场重算逐条比对 "
     "⇒ 220/220 一致, rc=0。文档里的数不许靠人眼核对"),
]

# ---------------------------------------------------------------- needs
# (key, to, item)
NEEDS = [
    ("iss047_margin_criterion_decision", "main",
     "ISS-047 卡点1 (需 PM/老板一句话): 俯角余量口径取 **B' 有效余量>=4deg** (推荐, "
     "含边框遮挡1.91deg ⇒ 俯角<=25.89deg, h_max d=35 = 16.99mm) 还是 **B 名义余量>=4deg** "
     "(<=27.80deg, 18.45mm) 还是 **C 名义>=10deg** (<=21.80deg, 14.00mm)? "
     "差 1.91deg/6.00deg ⇒ 差 h_max 1.47mm/3.45mm ⇒ 镜框上沿高度与摄像头能否藏在眉毛里。"
     "★我的建议 B': 遮挡是实物必然 (窗口座沉孔0.35mm 就要占深度), 名义余量留不住。"
     "★附带: 无论选哪个, 现行定案 AR0234CS 整幅 的 25deg 基线都站得住 (有效余量 +4.89deg)"),
]

STATUS = {
    "phase": "P3",
    "progress_pct": 96,
    "health": "yellow",
    "summary": (
        "ISS-047 复核交卷 (2026-11-02): ① hw-lead 指摘成立, 旧 §1.5「对角半角50deg→<=40deg」整表作废 "
        "(16:9 对角100deg 垂直半视场只有 30.30deg, 旧结论高估 9.70deg), 并补出旧表另两个错 "
        "(垂直俯角与水平偏置混列 / FOV 无投影模型, 直行vs等距差10.75deg) "
        "② 交付完整五数对应表 MECH/ISS047_FOV_TABLE.md (对角FOV/水平FOV/垂直FOV/垂直半视场/俯角余量) "
        "× 现行定案+备选+旧基线 × 直行/等距 × 三档, 每个俯角标注「正前方是否在画面内」 "
        "(名义余量/有效余量双列) ③ ★★基线已变: 老板 11-02 09:41 拍板「使用D」⇒ "
        "AR0234CS 1920x1200 整幅不裁剪 + 等距120deg ⇒ 垂直半视场 31.80deg (比旧 OV04C10 基线 29.53 多 2.27deg) "
        "⇒ 俯角25deg 名义余量 +6.80 / 有效 +4.89 ⇒ <=25deg 基线站得住且从临界点变有余量设计点, "
        "h_max 仍 13.99/14.92/16.32mm (d=30/32/35) "
        "④ ★新发现: 边框遮挡吃的是「正前方那一侧」(装上沿+光轴朝下俯⇒正前方在画面上半部) ⇒ 必须用有效余量; "
        "俯角30deg 名义+1.80 但有效-0.11 ⇒ 被镜框上沿遮掉 ⇒ 25-30deg 都不行 "
        "⑤ 零余量位置 (29.89deg) ⇒ h_max(d=35)=20.12mm > 旧上界20mm ⇒ 零余量做不到 "
        "⑥ 与上游口径不一致2处 (HW/DISPLAY_SENSOR_CHAIN 路线C 的 f=1.2704 是直行口径、路线D 的 "
        "116.75/28.62 是裁切口径) 已列待 hw-lead 回写 "
        "⑦ 自证: iss047_fov_table.py rc=0/FAIL0 + iss047_doc_check.py 220/220 一致; "
        "已改 MECH_BUDGET §1.5/§1.5.1/§1.5.2/§4(c) 与 CAMERA_WINDOW_SPEC §B5 重基线 "
        "⑧ 全部[推算] 0 实测 (0件打印件/0片镜头样片/镜头未下单); 未改 HW/SW/PROJECT_TRACKER/DECISIONS; "
        "未联系任何供应商"),
}


def main() -> int:
    dry = "--dry-run" in sys.argv

    # ---------------------------------------------------------------- 散文自检
    bad = [(k, v) for k, v, _ in CLAIMS if is_prose(v)]
    if bad:
        print("❌ 以下 claim 的 value 被判为散文 (不能机器比较), 中止, 分片保持原样:")
        for k, v in bad:
            print(f"   - {k} = {v!r}")
        return 1
    print(f"✅ 散文自检通过 ({len(CLAIMS)} 条 claim 的 value 都是短规范值)")

    if dry:
        print("[dry-run] 未落盘")
        for k, v, _ in CLAIMS:
            print(f"   claim {k} = {v}")
        return 0

    def mutate(d: dict):
        claims = d.setdefault("interface_claims", [])
        by_key = {c.get("key"): c for c in claims}
        for key, value, note in CLAIMS:
            if key in by_key:
                by_key[key]["value"] = value
                by_key[key]["note"] = note
                by_key[key].setdefault("ref", "MECH/ISS047_FOV_TABLE.md")
            else:
                claims.append({"key": key, "value": value, "note": note,
                               "ref": "MECH/ISS047_FOV_TABLE.md"})
        arts = d.setdefault("artifacts", [])
        have = {a.get("path") for a in arts}
        for path, kind, ver, upd, summary in ARTIFACTS:
            if path in have:
                for a in arts:
                    if a.get("path") == path:
                        a.update({"kind": kind, "version": ver, "updated_at": upd, "summary": summary})
            else:
                arts.append({"path": path, "kind": kind, "version": ver,
                             "updated_at": upd, "summary": summary})
        needs = d.setdefault("needs_from", [])
        if not any(n.get("key") == NEEDS[0][0] for n in needs):
            needs.append({"key": NEEDS[0][0], "to": NEEDS[0][1], "item": NEEDS[0][2],
                          "since": TODAY, "waiting_on": "boss", "due": "2026-11-05"})
        st = d.setdefault("status", {})
        st.update(STATUS)
        d["updated_at"] = TODAY
        d["updated_by"] = AGENT

    update_fragment(AGENT, mutate)
    print(f"✅ mech.yaml 已原子更新 (claims {len(CLAIMS)} / artifacts {len(ARTIFACTS)} / need 1 / status)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
