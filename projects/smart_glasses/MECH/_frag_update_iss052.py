#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-052 / ISS-047 (owner=mech-lead) —— 分片更新 (接口取值 / 答复 / 需求 / 产出 / 状态)。

★写分片铁律: 必须走 state/frag_write.py 的原子写 (tmp + fsync + os.replace),
   禁止 open(p,"w")。本脚本 **不自己写文件**, 只调 frag_write.update_fragment()。

★规范值纪律: interface_claims.value 必须是**短规范值** (≤40 字符, 中文占比 ≤0.35,
   不含句读/散文词), 否则合并器会把它标成"散文"、不参与冲突比较。
   本脚本落盘前**先跑 state/merge.py 的 is_prose() 自检**, 有散文就中止 (分片保持原样)。

用法: python3 MECH/_frag_update_iss052.py [--dry-run]
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment, load_fragment  # noqa: E402
from merge import is_prose  # noqa: E402  (复用合并器的散文判据)

AGENT = "mech-lead"
REF = "MECH/CAMERA_WINDOW_SPEC.md"
TODAY = "2026-10-29"

# ---------------------------------------------------------------- interface_claims
# (key, value, note) —— value 必须是短规范值
CLAIMS = [
    # --- 更新既有 camera_window (旧值口径过期: 写的是 '俯角20-32度') ---
    ("camera_window", "俯角<=25deg/28deg/凹进<=1.0mm",
     "★ISS-052 (2026-10-29) 重写: 俯角上限由 '20-32度' 收窄为 <=25deg (OV04C10 鱼眼) / <=28deg "
     "(AR0234CS 16:10); 依据 = 垂直半视场 - 4度 工程余量 (29.53-4=25.53 / 31.80-4=27.80); "
     "前顶点凹进由 1.5mm 收紧到 1.0mm (遮挡 2.9度->1.91度); 边框遮挡占垂直半视场 6.5%/6.0%"),
    # --- 更新既有 camera_fov_16x9 (旧表是直行口径且没标投影模型) ---
    ("camera_fov_16x9", "直行100度→H92.1/V60.8/等距120度→H104.5/V59.1",
     "★ISS-047 口径修正: 旧值只给直行口径且没标投影模型。同一'对角120度'直行垂直半视场 40.45度 "
     "vs 等距(鱼眼) 29.53度, 差 10.9度; 俯角必须按垂直半视场判, 不能用对角半角"),
    # --- 新增 ---
    ("camera_tilt_max_deg", "25deg/28deg",
     "俯角上限 (OV04C10 / AR0234CS 16:10), 走鱼眼(等距)路线; 判据 = 垂直半视场 - 4度余量; "
     "旧区间 20-32度的上段作废 (32度时正前方掉出画面)"),
    ("camera_vertical_half_fov", "29.53deg/31.80deg",
     "对角120度等距(鱼眼)口径下的垂直半视场 (OV04C10 / AR0234CS 16:10); "
     "直行口径是 40.45deg/42.55deg —— 投影模型必须连 FOV 一起说"),
    ("camera_brow_h_max_mm", "16.32mm",
     "摄像头光轴中心高于用户视线的上限 h = d*tan(俯角上限); 25deg 档 d=35mm 取 16.32 "
     "(d=30/32 时 13.99/14.92); 28deg 档 18.61/17.01/15.95; MECH 原值 h=12-20mm 的上界收紧到 16.3mm"),
    ("camera_front_vertex_recess", "1.0mm",
     "前镜片顶点相对镜框上沿外表面的凹进基准 (设计值); 允许 0-1.0mm (齐平或凹进<=1.0); "
     "由原 1.5mm 收紧 —— 1.0mm 遮挡 1.91度 (垂直半视场 6.5%), 1.5mm 遮挡 2.86度 (9.7%)"),
    ("camera_lens_barrel_clearance", "⌀7.5mm",
     "镜框上沿加厚区净空孔 (镜筒外径上限 ⌀6.5 + 单边 0.5 壁/公差); 三档 FOV 同值 -> 可不等镜头定档开模"),
    ("camera_module_h", "6.0mm",
     "模组沿光轴总高 (前顶点->PCB顶面) 设计取值; 上游区间写 5.0-5.9 但推荐 6.0 (自相矛盾, "
     "120度鱼眼算术值 4.55+1.30=5.85) -> 结构按保守取 6.0; 镜头总高取 4.6"),
    ("camera_brow_boss_thickness", "10.11-10.41mm",
     "镜框上沿摄像头位的**前后方向厚度**需求 = 倾斜模组包络 (窗口0.3+间距0.5+模组6.0)*cos(φ) "
     "+ ⌀6.5*sin(φ) + 壁1.2, φ=25/28/32度; 落在 MECH '加厚10-12mm' 带内余量 1.6-1.9mm; "
     "★口径: 10-12mm 是前后厚度不是径向直径 (hw-lead 的'径向余量2.5-4.5mm'是把厚度当直径比)"),
    ("camera_brow_vertical_clear", "10.36-10.53mm",
     "镜框上沿摄像头位的**垂直净高**需求 (同一位, 新增口径) = (6.8*sin(φ) + ⌀6.5*cos(φ)) + 上下壁1.6, "
     "φ=25/28度; MECH 原来只算前后厚度, 这条是新增账 -> 需 PM/老板认外观代价"),
    ("lens_projection_model", "equidistant",
     "★镜头投影模型 = 等距(鱼眼); 与 hw-lead 的 lens_fov_basis=full-array-120deg 配套: "
     "该 FOV 数只在等距口径下给出 29.53度垂直半视场; 直行口径 40.45度 不可混用"),
]

# ---------------------------------------------------------------- answers (用对方给过的 key)
ANSWERS = [
    ("pcb_outline_confirm", "hw-lead",
     "★ISS-052 (2026-10-29) 摄像头侧更新: 俯角 <=25deg (OV04C10 鱼眼) / <=28deg (AR0234CS 16:10), "
     "原'20-32度'上段作废; 前顶点凹进 <=1.0mm (原1.5mm 收紧), 设计基准凹进1.0mm -> 感光面凸出 "
     "0.94mm(25度)/1.16mm(28度), 对 MECH 凸出<=2.5mm 余量 1.56/1.34mm; "
     "★新增硬约束: 摄像头光轴中心高于用户视线 h <= 13.99/14.92/16.32mm (25deg, d=30/32/35); "
     "镜框上沿摄像头位前后厚度需求 10.11-10.41mm (落 10-12mm 带余量1.6-1.9mm) + 上沿垂直净高 "
     "10.36-10.53mm; 镜筒净空 ⌀7.5 / 窗口座 ⌀6.8深0.35 / 通光孔打印 ⌀5.4; "
     "**'加厚10-12mm' = 前后方向厚度口径, 不是径向直径** (径向单边余量 1.25-2.25mm)",
     REF),
    ("pcb_outline_confirm", "hw-lead",
     "★ISS-052 答 LENS_SELECTION §B7 卡点4 (加厚10-12mm 的定义): "
     "MECH §1.4.5 的'镜框厚度(前后方向)需求汇总'把上沿区 10-12mm 与正中区 11.8mm 并列 => 同为"
     "**前后方向厚度**; 复算 = 倾斜模组包络 10.11mm(25度)/10.26mm(28度)/10.41mm(32度), "
     "对俯角极不敏感 (20->32度 只变0.60mm) => 俯角收窄不挤压上沿厚度预算。"
     "另: 你给的'径向余量2.5-4.5mm'是把10-12mm当直径跟⌀7.5比的直径差, 单边(半径)余量实为 "
     "1.25-2.25mm/边 —— 口径要改。",
     REF),
]

# ---------------------------------------------------------------- needs_from (要别人配合/回答)
NEEDS = [
    ("iss052_tilt_margin_criterion", "main",
     "ISS-052 口径裁决: 俯角余量取 **4度** (工程判据 -> 俯角<=25deg/28deg, 与 PM 10-25 19:42 基线一致) "
     "还是 **10度** (MECH §1.5 原表口径 -> 俯角<=19.53deg/21.80deg)? "
     "两者差 6.0度, 换算到结构是 h_max 差 3.4mm (14.92 vs 11.35mm @d=32), "
     "即'摄像头能不能藏在眉毛里'的差别。**我的假设 (不回我就按这个走): 取 4度**, 因为它等于 PM/hw-lead "
     "已定的 <=25deg/28deg, 且能覆盖 FDM 打印件角度公差 ±0.5deg + 镜框上沿造型公差 ±1deg。",
     "agent", "2026-10-30"),
    ("iss052_brow_vertical_clearance", "main",
     "ISS-052 新增账需老板认: 镜框上沿摄像头位**垂直净高需求 10.36mm(俯角25度)/10.53mm(28度)** "
     "(倾斜模组包络 + 上下壁1.6) —— MECH 原来只算了前后厚度(10-12mm), 这条是新增的。"
     "主流 AI 眼镜上沿带高只有 6-12mm, 直穿式安装要 10.4mm。请裁三个选项: "
     "(a) 摄像头位**局部加高/凸包** (b) **下沉/斜切式安装** —— 但会把前顶点凹进顶到 >1.0mm, 与 ISS-052 "
     "刚收紧的凹进上限冲突 (c) 换更短的模组 —— 但会破坏'不等镜头定档开模'的解耦。"
     "**我的假设 (不回我就按这个走): 选 (a) 局部加高**, 且把上沿垂直净高按 10.6mm 预留。",
     "boss", "2026-10-30"),
    ("iss052_window_material_vendor", "main",
     "ISS-052 卡点: 摄像头窗口材质与厚度 —— 化学强化玻璃 0.3mm (平面度<=0.05) vs 蓝宝石 0.5mm "
     "(平面度<=0.02, 防碎, 贵)。影响窗口座沉孔深度 (0.35 vs 0.55) + 座面机加工精度要求。"
     "**外发一律经你, 我不联系供应商**。**我的假设 (不回我就按这个走): 按玻璃 0.3mm 设计 + 蓝宝石 0.5mm "
     "预留 (沉孔按 0.55 深做, 两种都能装)**。",
     "vendor", "2026-10-31"),
    ("iss052_sensor_pkg_height_vendor", "main",
     "ISS-052 卡点: sensor 封装高 1.3mm 是 hw-lead LENS_SELECTION §B7 卡点7 的**占位值** [0数据], "
     "直接进'模组沿光轴总高 6.0mm' 与上沿厚度 10.11mm。±0.3mm 的封装高误差对上沿厚度是 ±0.3mm "
     "(余量 1.6mm, 吃得住) —— 但请把原厂封装高回填, 否则模组总高与加厚区终值不能封版。"
     "**外发经你, 我不联系原厂**。",
     "vendor", "2026-10-31"),
    ("iss052_relay_lens_spec_questions", "main",
     "ISS-052 请转 hw-lead 两条上游自相矛盾 (我不直接联系): "
     "(1) HW/LENS_SELECTION.md §B4.1 S3: 模组沿光轴总高'区间 5.0-5.9mm'但'推荐 6.0mm' —— "
     "区间上界 < 推荐值; 120度鱼眼算术值是 4.55+1.30=5.85。结构侧按保守取 6.0, 请 hw-lead 统一口径。 "
     "(2) HW/LENS_SELECTION.md §4.2: '窗口内壁哑黑消光'与同表'窗口必须 AR 镀膜 R<2%@60度入射'互斥 —— "
     "内表面做消光就没有 AR 膜, 边缘亮度损失 20-30%。结构侧按'消光做在遮光罩内壁, 窗口内表面保持 AR' "
     "执行, 请 hw-lead 改文档措辞。"
     "另: 镜框上沿加厚 10-12mm 我已答 (前后方向厚度口径), 径向单边余量 1.25-2.25mm。",
     "agent", "2026-10-30"),
]

# ---------------------------------------------------------------- artifacts
ARTIFACTS = [
    ("MECH/CAMERA_WINDOW_SPEC.md", "spec", "v1.0",
     "ISS-052+ISS-047 结构侧摄像头窗口规格: B1 摘要6条 + B2 要跟的数 (镜筒⌀6.5/净空⌀7.5/镜头总高4.6/"
     "沿光轴6.0/窗口⌀6.5x0.3/AR R<2%@60度/间距>=0.5/顶点凹进<=1.0) + B3 倾斜模组三向包络 (前后10.11-10.41/"
     "垂直10.36-10.72/水平6.50, 前后余量1.6-1.9mm) + B4 凸出凹进账 (新最坏2.16mm/设计0.94-1.16mm) + "
     "B5 俯角三判据 (4度/10度) + 六行FOV五列表 (ISS-047 口径修正) + h_max 新硬约束 + B6 打印装配预留 + "
     "B8 未决项8条"),
    ("MECH/camera_window_check.py", "script", "v1.0",
     "自证脚本 (rc=0, FAIL 0 / WARN 0): §1 FOV五列表(两靶面x两投影x三档) + §2 俯角上限三判据 + "
     "§3 h_max 表 + §4 倾斜包络 + §5 凸出账 + §6 窗口预留 + §7 水平余量; 12 条判据机器判定"),
    ("MECH/_apply_iss052_docs.py", "script", "v1.0",
     "MECH_BUDGET.md §1.5/§1.5.1/§1.5.2/§4(c) 改写器 (幂等, 连跑两次第二遍改0条)"),
]

STATUS = {
    "phase": "ISS-052/ISS-047 交卷 (摄像头窗口 + 俯角收窄 + 口径修正)",
    "progress_pct": 100,
    "health": ("yellow (几何全部算完且判据 rc=0/FAIL0; 但 3 项要 PM/老板拍板: 俯角余量口径 4度 vs 10度 / "
               "上沿垂直净高 10.4mm 外观代价 / 窗口材质; 4 项 [0数据] 等原厂与供应商: sensor封装高1.3mm / "
               "窗口材质 / CRA>=55度匹配 / 模组总高区间口径)"),
    "summary": ("镜框上沿摄像头位复核通过: 倾斜模组包络 = 前后 10.11mm(25度)/10.26mm(28度)/10.41mm(32度), "
                "落 MECH 加厚 10-12mm 带内余量 1.6-1.9mm, 且对俯角不敏感 (20->32度只变0.60mm) => 俯角收窄不挤压"
                "厚度预算; 俯角上限收窄到 <=25deg(OV04C10)/<=28deg(AR0234CS 16:10) (垂直半视场29.53/31.80 - 4度余量), "
                "MECH '20-32度不可回避' 作废; ISS-047 原表(用对角半角50度推<=40度) 整表作废, 换成两靶面x两投影x三档的"
                "五列表; 前顶点凹进 1.5->1.0mm 收紧, 凸出最坏 2.44->2.16mm (余量0.06->0.34mm); "
                "新增硬约束 h<=13.99/14.92/16.32mm (摄像头中心高于视线) 与上沿垂直净高>=10.4mm; "
                "并更正常见口径错误: hw-lead 的'径向余量2.5-4.5mm'是把厚度当直径比(单边实为1.25-2.25mm)"),
}


def main() -> int:
    dry = "--dry-run" in sys.argv

    # ---- 落盘前自检: 新增/更新的 claim 不得是散文 ----
    bad = [(k, v) for k, v, _ in CLAIMS if is_prose(v)]
    if bad:
        for k, v in bad:
            print(f"❌ claim {k!r} 的 value 会被合并器判成散文: {v!r}")
        raise SystemExit("[frag] 中止, 分片保持原样")
    for k, v, _ in CLAIMS:
        print(f"[check] claim {k!r} = {v!r} (len={len(v)}) ✅")

    def mutate(d: dict):
        # 1) interface_claims: 同 key 覆盖 (merge.py 取最后一条), 新 key 追加
        claims = d.setdefault("interface_claims", [])
        by_key = {c.get("key"): c for c in claims}
        for k, v, note in CLAIMS:
            if k in by_key:
                by_key[k]["value"] = v
                by_key[k]["note"] = note
                by_key[k]["ref"] = REF
                by_key[k].pop("canon", None)
            else:
                claims.append({"key": k, "value": v, "note": note, "ref": REF})
        # 2) answers (用对方给过的 key)
        for k, to, val, ref in ANSWERS:
            d.setdefault("answers", []).append({"key": k, "to": to, "value": val, "ref": ref})
        # 3) needs_from (带 key + to + item + waiting_on + due)
        existing = {n.get("key") for n in d.get("needs_from", []) or []}
        for k, to, item, won, due in NEEDS:
            if k in existing:
                continue
            d.setdefault("needs_from", []).append({
                "key": k, "to": to, "item": item, "since": TODAY,
                "waiting_on": won, "due": due,
            })
        # 4) artifacts
        have = {a.get("path") for a in d.get("artifacts", []) or []}
        for path, kind, ver, summary in ARTIFACTS:
            if path in have:
                continue
            d.setdefault("artifacts", []).append({
                "path": path, "kind": kind, "version": ver,
                "updated_at": TODAY, "summary": summary,
            })
        # 5) status
        d["status"] = dict(STATUS)
        d["updated_at"] = "2026-10-29T01:40:00+08:00"
        d["updated_by"] = "mech-lead"

    if dry:
        d = load_fragment(AGENT)
        mutate(d)
        print("[dry-run] 未落盘")
        return 0

    after = update_fragment(AGENT, mutate)
    print(f"[frag_write] ✅ {AGENT}.yaml 已原子更新")
    print(f"[after] interface_claims {len(after.get('interface_claims') or [])} 条 | "
          f"answers {len(after.get('answers') or [])} 条 | "
          f"needs_from {len(after.get('needs_from') or [])} 条 | "
          f"artifacts {len(after.get('artifacts') or [])} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
