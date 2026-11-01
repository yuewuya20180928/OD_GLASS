#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-025 交卷: 把本单产出登记进 mech-lead 分片 (走 state/frag_write.py 的原子写 API)
================================================================================
为什么用脚本而不是命令行 --add-need:
  · frag_write.py 的 CLI `--add-need` 只支持 key/to/item/since,
    **不支持 waiting_on / due** —— 而协议强制 needs_from 必须带这两项
    (否则合并器分不清"等外部"与"等另一个总工")。
  ⇒ 所以用同一工具的 Python API `update_fragment()`, 仍然是原子写 (tmp + os.replace),
    **没有用 open(p,"w")**。

用法:  python3 MECH/_apply_iss025_frag.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

AGENT = "mech-lead"
SINCE = "2026-11-01"

# ---------------------------------------------------------------- 产出
ARTIFACTS = [
    {
        "path": "MECH/DFM_REVIEW.md",
        "kind": "review",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": (
            "结构 DFM 评审 (ISS-025): ① 逐件量产工艺 24 件总表 (镁合金ADC12压铸 2件 / PC-ABS注塑 7件 / "
            "Al6063-T6 CNC 7件 / 硅胶模压+模切胶垫+标准件 8件) "
            "+ 4 个专项 (压铸镁/注塑/CNC/硅胶胶垫) ② DFM 参数 6 类: 脱模斜度(含深腔截面差 Δ=2·h·tanα) / 壁厚 / 圆角 / "
            "公差带(含单向公差原则) / 缩水(收缩敏感性3档 + 收缩敏感尺寸移交规则9项) / 装配顺序(镜脚14步+镜框8步+不可逆工序6项) "
            "③ 打印件验证不了但量产会出问题的清单 27 条 (几何10+收缩表面5+工艺装配7+测试口径5) ④ 阳极工序顺序4方案对比+"
            "基准面选择规则B1-B6+图纸必标6条 ⑤ 量产件DFM检查表16条 "
            "★核心结论: 量产的杀手不是公差而是脱模斜度 (主腔38.00双面1° ⇒ 截面差1.327mm ⇒ 镜脚H链电芯段最坏 -0.577mm "
            "几何上做不出来) ⇒ 电池座/PCB座改CNC嵌件, 延续'打印件造型+CNC金属件承担定位承力'分工。"
            "★0条实测(本机不可打印/量测) ⇒ 全部为[推算]或[推算·通用](未按牌号验证), 牌号级参数一律[0数据]并登记needs"
        ),
    },
    {
        "path": "MECH/dfm_check.py",
        "kind": "script",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": (
            "DFM 自检脚本 (rc=0): A段脱模斜度/倒扣面级统计 (Rev B 三件解析图元表精确求, 1220面; ZERO_DRAFT 25.0/61.9/59.8%, "
            "fit_coupon 2个倒扣面 α=-40/-30°) + B段量产公差栈vs打印件公差栈 (V/H/L三链, 打印件侧沿用fit_check_v3_30mm现值) "
            "+ C段深腔双面脱模截面差 (38mm腔1°⇒1.327mm) 与收缩敏感性 (1.0/1.5/2.0%三档). "
            "输入参数全部显式列在文件头, 一条命令复现 DFM_REVIEW.md 的全部关键数字"
        ),
    },
    {
        "path": "HANDOFF/2026-11-01_mech-lead_ISS025_结构DFM评审.md",
        "kind": "handoff",
        "version": "v2.0",
        "updated_at": SINCE,
        "summary": (
            "质量门 v2: B1-B6 六块 6/6; B2 自评 18 条 (✅通过16 / ❌不通过2: 实物实测不可能 + 量产外壳面级统计0数据点); "
            "B3 证据分级 16 条 (实测条数=0); B4 接口取值 14 条 mech_dfm_*; B5 needs 7 条 (全带waiting_on+due) + 阻塞3条; "
            "B6 自证命令 5 条 (核心 python3 MECH/dfm_check.py)"
        ),
    },
]

# ---------------------------------------------------------------- 接口取值 (value 必须是短规范值)
CLAIMS = [
    ("mech_dfm_draft_min", "1.0deg",
     "注塑/压铸件最小脱模斜度; 外观面1.5deg / 皮纹面0.5deg / 深腔2.0deg / 定位孔0deg(阳极后精加工)。通用经验值, 未按牌号验证",
     "MECH/DFM_REVIEW.md §2.1"),
    ("mech_dfm_draft_skin", "0.5deg",
     "镜腿皮肤侧(贴肤面, 面积最大)做皮纹面以放宽脱模斜度 => 深腔截面差1.327=>0.663mm。待boss确认是否接受皮纹面",
     "MECH/DFM_REVIEW.md §2.1/§6-5"),
    ("mech_dfm_tol_inj", "±0.20mm",
     "注塑PC/ABS一般公差带(小件<=30mm)。通用经验值, 需模具厂确认",
     "MECH/DFM_REVIEW.md §2.4"),
    ("mech_dfm_tol_die", "±0.25mm",
     "压铸镁合金ADC12一般公差带(小件)。通用经验值, 需模具厂确认",
     "MECH/DFM_REVIEW.md §2.4/§1.2"),
    ("mech_dfm_tol_cnc", "±0.05mm",
     "CNC Al6063-T6一般公差带; 定位面±0.01/平面度<=5um/孔H7",
     "MECH/DFM_REVIEW.md §2.4/§1.4"),
    ("mech_dfm_cavity_loss_38", "1.327mm@1.0deg",
     "镜脚下壳主腔深38.00mm双面1deg脱模的截面差(=2*h*tanα); 皮纹面0.5deg时0.663mm",
     "MECH/DFM_REVIEW.md §2.1.2"),
    ("mech_dfm_h_chain_worst", "-0.577mm",
     "镜脚H链(电芯段)在'量产公差+1deg脱模'下的最坏余量 => 几何上做不出来, 须靠结构改(电池座/PCB座改CNC嵌件)",
     "MECH/DFM_REVIEW.md §2.1.2/§2.4"),
    ("mech_dfm_v_chain_worst", "1.60mm",
     "镜脚V链(板宽30)量产公差最坏余量(打印件1.40); 叠加脱模不变(V不被拉出方向直接吃)",
     "MECH/DFM_REVIEW.md §2.4"),
    ("mech_dfm_battery_seat", "CNC-6063-insert",
     "量产电池座(及PCB座)改为Al6063-T6 CNC嵌件, 与SoC骨架共基准 => 收缩不作用/深腔脱模不作用/电池不靠胶定位。待main裁",
     "MECH/DFM_REVIEW.md §1.1-8/§6-4"),
    ("mech_dfm_anodize_seq", "Anodize-then-locate-mach",
     "铝件阳极工序顺序=方案A(CNC全部->去毛刺->阳极TypeIII+封孔->定位面/定位孔二次精加工), 保PIN-SET-2 <=0.046mm。承ISS-024 4.3-N1",
     "MECH/DFM_REVIEW.md §4.1/§4.2"),
    ("mech_dfm_datum", "A-B-plus-P1-pin-face",
     "机加工基准面选择: 同一平面内两条精铣带做A-B, 第三约束用P1圆销端面止推; 不用三点基准(膜厚均匀性敏感度 vs 指标<=0.046mm)",
     "MECH/DFM_REVIEW.md §4.2"),
    ("mech_dfm_shrink_sens", "1.0/1.5/2.0%",
     "收缩敏感性假设档(不锁牌号值): 镜框长向1.400/2.100/2.800mm; 镜脚内腔长1.300/1.950/2.600mm => 收缩敏感界面一律移交CNC件/镶件",
     "MECH/DFM_REVIEW.md §2.5.2/§2.5.3"),
    ("mech_dfm_hinge_hole", "post-machined",
     "镜框压铸件的铰链接口孔距必须后加工(CNC精镗)或改镶件, 不得开在压铸/注塑本体上",
     "MECH/DFM_REVIEW.md §2.5.3"),
    ("mech_dfm_shell_geometry", "0-shell-geom",
     "量产外形件(镜框主体/镜腿上壳/镜腿下壳)的脱模/分型/缩痕/顶针面级统计现状=0个数据点(Rev B打印包只含检具与试样)",
     "MECH/DFM_REVIEW.md §3.5/§6-6"),
]

# ---------------------------------------------------------------- needs (必须带 waiting_on + due)
NEEDS = [
    {
        "key": "mech_dfm_shrink_rate", "to": "vendor", "since": SINCE,
        "waiting_on": "vendor", "due": "2026-11-10",
        "item": (
            "ISS-025 量产收缩率 (经项目总工走供应商/模具厂, 我不联系): ① 镁合金ADC12压铸件线性收缩率"
            "(线/面内 + 工艺窗口 + 模温条件); ② PC/ABS镜腿壳注塑件收缩率(须注明原生料比例, 回料比例一变收缩率就变); "
            "③ 对应的模具补偿基准。我的假设: 按1.0/1.5/2.0%三档假设做敏感性, 不锁单值; "
            "所有'两件互相配'的界面按DFM_REVIEW 2.5.3移交CNC件/镶件 => 结论不因具体S改变"
        ),
    },
    {
        "key": "mech_dfm_anodize_uniformity", "to": "vendor", "since": SINCE,
        "waiting_on": "vendor", "due": "2026-11-10",
        "item": (
            "ISS-025 阳极工序与均匀性 (经项目总工走表面处理方): ① 硬质阳极Type III膜厚均匀性(标称±?%)与实测报告格式; "
            "② 能否做到'定位面/定位孔阳极后精加工<=5um', 精加工后膜层如何处理(遮蔽/裸铝/重做); "
            "③ 镁合金化学转化+涂层+边缘封孔体系与膜厚。我的假设: 按方案A(CNC->阳极->定位面/定位孔二次精加工)出图; "
            "若只能做方案C(阳极前留量)则要求书面承诺膜厚均匀性<=±10%, 否则方案B/C不可用"
        ),
    },
    {
        "key": "mech_dfm_mold_tolerance", "to": "vendor", "since": SINCE,
        "waiting_on": "vendor", "due": "2026-11-12",
        "item": (
            "ISS-025 量产公差与最小特征 (经项目总工走模具厂): ① 注塑PC/ABS与压铸ADC12的一般公差带"
            "(本单用的±0.20/±0.25是通用经验值, 需按实际模具工艺确认); ② 最小特征可达性"
            "(⌀1.6让过孔 / ⌀2.4销孔 / 0.6mm壁厚台阶); ③ 顶针/浇口/分型面的可行布置。我的假设: "
            "按DFM_REVIEW 2.4公差带出图并全部设单向公差; 若最小特征不可达则该处改CNC镶件"
        ),
    },
    {
        "key": "mech_dfm_battery_seat", "to": "main", "since": SINCE,
        "waiting_on": "agent", "due": "2026-11-08",
        "item": (
            "ISS-025 量产架构改动请裁: 电池座与PCB座由'注塑件本体特征'改为CNC金属嵌件(Al6063-T6, 与SoC骨架共基准), "
            "与MECH_BUDGET 5.5既有分工一致。理由: 镜脚下壳主腔深38.00mm, 内外双面1deg脱模 => 内腔横截面窄端少1.327mm "
            "=> 镜脚H链(电芯段)最坏余量-0.577mm, 几何上做不出来; 皮纹面0.5deg也只救到0.087mm<判据0.40 "
            "=> 靠公差或斜度都救不回来。代价: 零件数+2(左右各1电池座)+成本。请裁是否接受"
        ),
    },
    {
        "key": "mech_dfm_draft_texture", "to": "main", "since": SINCE,
        "waiting_on": "boss", "due": "2026-11-10",
        "item": (
            "ISS-025 镜腿皮肤侧(贴肤, 面积最大)是否接受皮纹面/喷砂面(而非光面), 经项目总工走老板。接受 => 脱模斜度可放宽到0.5deg "
            "(深腔截面差1.327=>0.663mm); 不接受 => 皮肤侧须1.5deg => 截面差1.990mm。我的假设: 按皮纹面推进"
            "(镜腿皮肤侧做细皮纹; 鼻梁区仍可光面, 皮肤接触面清单见ISS-024 2.7)"
        ),
    },
    {
        "key": "mech_dfm_shell_geometry", "to": "main", "since": SINCE,
        "waiting_on": "agent", "due": "2026-11-12",
        "item": (
            "ISS-025 量产外形件建模排期请定: Rev B打印包交付的是检具+试样(fit_coupon_revb 150x132x22 / "
            "temple_cage_revb 60x122.4x27.8 / frame_typec_coupon_revb 33x3x7.2), 不含镜框主体/镜腿上壳/镜腿下壳等任何"
            "量产外形件 => 脱模斜度/分型面/缩痕/飞边/顶针目前0个数据点。我的假设: 在ISS-027 B3(镜框与光学批)之前完成"
            "外形件建模并跑MECH/dfm_check.py面级检查; 未完成则不开模"
        ),
    },
    {
        "key": "mech_dfm_waveguide_seat", "to": "jbd", "since": SINCE,
        "waiting_on": "jbd", "due": "2026-11-10",
        "item": (
            "ISS-025 波导卡槽工艺选型 (经项目总工走JBD): 需要波导2D外形 + 外形公差 + 是否可承受压铸件的收缩与热变形 "
            "+ 安装面平面度要求, 才能定波导卡槽是'压铸本体'还是'CNC卡座'。我的假设: 按CNC卡座+3点金属压条做"
            "(DFM_REVIEW 1.1-12), 波导按玻璃基假设; 平行度±0.3deg与0.2mm硅胶垫不变"
        ),
    },
]

BLOCKERS = [
    {
        "id": "MECH-B-DFM-1",
        "desc": (
            "量产外形件几何不存在 => 脱模/分型/收缩/缩痕/飞边/顶针的面级统计 = 0个数据点。Rev B打印包只含检具与试样。"
            "不补就开模 = 模具报废风险(本单已算出镜脚H链在1deg脱模下最坏 -0.577mm, 几何上做不出来)"
        ),
        "severity": "high",
        "needs_from": ["main"],
        "waiting_since": SINCE,
    },
    {
        "id": "MECH-B-DFM-2",
        "desc": (
            "量产级工艺参数(脱模斜度/公差带/收缩率)全部是[推算·通用]或[0数据], 未按牌号/模具厂验证。"
            "已登记3条 waiting_on=vendor 的needs(收缩率/阳极均匀性/模具公差), 未回应前不进入开模"
        ),
        "severity": "medium",
        "needs_from": ["vendor"],
        "waiting_since": SINCE,
    },
]

STATUS = {
    "phase": "P3",
    "progress_pct": 95,
    "health": "yellow",
    "summary": (
        "ISS-025 结构DFM评审已交 (MECH/DFM_REVIEW.md 9章 + MECH/dfm_check.py rc=0 + HANDOFF B1-B6六块): "
        "① 逐件量产工艺24件 (镁合金ADC12压铸2件/PC-ABS注塑7件/Al6063-T6 CNC 7件/硅胶模压+模切胶垫+标准件8件) "
        "② DFM参数6类 (脱模斜度含深腔截面差/壁厚/圆角/公差带含单向公差/缩水含收缩敏感尺寸移交规则/装配顺序镜脚14步+镜框8步+不可逆工序6项) "
        "③ 打印件验证不了但量产会出问题的清单27条 (几何10+收缩表面5+工艺装配7+测试口径5) "
        "④ 阳极工序顺序选方案A (CNC→阳极→定位面/定位孔二次精加工) + 基准面A-B两点+P1销端面止推 => PIN-SET-2 <=0.046mm仍成立 "
        "★核心结论: 量产的杀手不是公差而是脱模斜度 (主腔38.00双面1°=>内腔横截面窄端少1.327mm => 镜脚H链电芯段最坏-0.577mm "
        "几何上做不出来; 皮纹面0.5°也只救到0.087<判据0.40) => 电池座/PCB座改CNC嵌件, 延续'打印件造型+CNC金属件承担定位承力'分工 "
        "★另一条: Rev B打印包=检具+试样, 不含任何量产外形件 => 脱模/分型/缩痕/顶针目前0个数据点 (high阻塞, 建模前不开模) "
        "★0条实测(本机不可打印/量测) => 全部[推算]或[推算·通用](未按牌号验证); 牌号级参数一律[0数据]并登记needs "
        "14条 mech_dfm_* claim + 7条 mech_dfm_* need(全带waiting_on+due) + 2条 blocker. "
        "未联系任何供应商/原厂/模具厂, 未改 issue_log/HW/SW/PROJECT_TRACKER/DECISIONS, 未改ISS-024与MECH_BUDGET既有数字(只引用)"
    ),
}


def main() -> int:
    def mutate(d):
        arts = d.setdefault("artifacts", [])
        by_path = {a.get("path"): a for a in arts}
        for a in ARTIFACTS:
            if a["path"] in by_path:
                by_path[a["path"]].update(a)      # 幂等: 已存在则就地更新
            else:
                arts.append(a)
        claims = d.setdefault("interface_claims", [])
        have_c = {c.get("key") for c in claims}
        for k, v, note, ref in CLAIMS:
            if k not in have_c:
                claims.append({"key": k, "value": v, "note": note, "ref": ref})
        needs = d.setdefault("needs_from", [])
        have_n = {n.get("key") for n in needs}
        for n in NEEDS:
            if n["key"] not in have_n:
                needs.append(n)
        bl = d.setdefault("blockers", [])
        have_b = {b.get("id") for b in bl}
        for b in BLOCKERS:
            if b["id"] not in have_b:
                bl.append(b)
        d.setdefault("status", {}).update(STATUS)

    update_fragment(AGENT, mutate)
    print("[apply_iss025] ✅ mech.yaml 已原子更新 (artifacts +3 / claims +14 / needs +7 / blockers +2 / status)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
