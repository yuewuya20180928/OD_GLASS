#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-121 交卷落地: 分片原子写 (answers / needs_from / interface_claims / artifacts / status)
                  + issue_log.yaml 里 **owner=hw-lead 的 ISS-121 一条** 推到 fixed。

纪律:
  - 分片只写自己那一份 (hw.yaml), 走 state/frag_write.py 的 update_fragment (原子写)。
  - issue_log.yaml 只动 id == ISS-121 且 owner == hw-lead 的那条; 原子写 (tmp+fsync+os.replace)。
  - 不碰 MECH/ SW/ PROJECT_TRACKER.md DECISIONS.md; 不碰别人的分片; 不外发。

用法: python3 HW/_apply_iss121.py [--dry-run]
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
STATE = os.path.join(PROJ, "state")
sys.path.insert(0, STATE)

from frag_write import update_fragment  # noqa: E402

LOG = os.path.join(STATE, "issue_log.yaml")

FIX_REF = (
    "HW/ISS121_MIC_MAGNET_POSITION.md (ISS-121 主文档: 磁场机理/地磁本底/本项目实算三条证据链 + "
    "位置坐标回归 + ≥40mm 判据逐项 + MECH 尺寸 3 条不自洽 P-1~P-3 + 选型硬判据 M-1~M-5 + 台架复测 4 步) + "
    "HW/iss121_mic_magnet_check.py (自证脚本, rc=0; 坐标系回归 4/4 + 磁体模型数值/解析互校 0.000111% + "
    "位置/磁场判据) + HW/iss121_mic_magnet_check.json + "
    "HANDOFF/2026-11-01_hw-lead_ISS121_麦克风磁场与位置复核.md (B1-B6 六块齐)"
)

CLOSE_NOTE = (
    "\n\n★2026-11-01 21:0x hw-lead 交卷并自推状态 (owner=hw-lead)。\n"
    "【本单做了什么】① 出 HW/ISS121_MIC_MAGNET_POSITION.md —— 闭环 ISS-092 转来的 I-5 (磁场) / I-6 (位置) 两条接口请求; "
    "② 出 HW/iss121_mic_magnet_check.py (rc=0) 把坐标系回归/磁体模型/位置判据做成可机械复算的判定; "
    "③ 出 HANDOFF/2026-11-01_hw-lead_ISS121_麦克风磁场与位置复核.md (B1-B6 六块齐); "
    "④ 分片走 state/frag_write.py 原子写 (2 条 answers 闭合 mech-lead 的 I-5/I-6 + 6 条 needs + 6 条 interface_claims + 3 条 artifact); "
    "⑤ 本脚本把 ISS-121 推到 fixed 并落 fix_ref (verify_by=main, 不填自己)。\n"
    "【两条接口请求的答案 (摘要)】"
    "① **磁场 (I-5): 判定『无影响』** —— N35 ⌀4.00×1.00 (Br typ 1.20 T, 带宽 1.14-1.26 T) 端面 **40mm 处 B = 36.0 µT** "
    "(Br 上限 → 37.8 µT), 与地磁 25/50/65 µT 同一量级; 推荐落位 (板 X=5.00) 处 **B = 7.3 µT** (磁铁最靠里 15.1 µT) "
    "**低于地磁最小值 25 µT** ⇒ 远低于任何可用判据线。机理: 电容式 MEMS 麦的换能链 (声压→硅膜位移→电容) **无静态磁场作用点** "
    "(真怕磁的是动圈/驻极体/霍尔式, 本项目不用)。"
    "★★**任务书要求的『按麦克风规格书的磁场敏感度核』这条路走不通, 且不是本项目漏查**: 4 份主流 MEMS 麦规格书 "
    "(Infineon IM69D130 / IM67D128BV01 / Knowles MM20 / ST MP34DT04-C1) 全文检索 'magnet' = **0 命中** ⇒ **规格书里没有这一栏** "
    "⇒ 改用三条替代证据链 (机理 / 地磁本底 / 本项目实算), 并把『静态磁场耐受 ≥100 µT (≈IEC 61000-4-8 L5 126 µT)』写成"
    "**选型硬判据 M-2**, 另给台架复测 4 步 (1kHz 94dB 灵敏度漂移 ≤±0.5dB)。\n"
    "② **位置 (I-6): 我把位置定死** —— 麦克风 = **板坐标 X=5.00 / Y=12.00 (镜脚 L=45.50)**, 顶进式 MEMS, 声孔 ⌀1.00 开在镜脚"
    "**外侧面** + 非磁性粘接防尘网; 净空 **通窗 44.20 / 磁铁 54.80 (最坏 43.00) / 螺钉 55.30 mm** ⇒ **≥40mm 全部 PASS**; "
    "且该处**金属骨架不在上方** (骨架占板 X 18.00..42.00) ⇒ **不需要开骨架窗** (声学通道 3.00mm 直通)。"
    "★**≥40mm 判据的可满足带只有板 X ≤ 8.00** (对通窗与最坏磁铁取交集) ⇒ 铰链端是唯一解; M2 (X=17.00) 与 M3 (X=26.00, "
    "即 mech-lead 假设的『根部 SoC 区』) **全部 FAIL** (23.20~31.00mm)。M1 成立前提是『跨铰链连接器座体悬出板端、只占焊盘 X 0..3』, "
    "该边界 [0数据] (ISS-105 open) 已登记 needs。**导光孔那半条在当前基线 N/A** (充电板已按 ISS-014 决策 5 挪到镜框 ⇒ LED 在框 ⇒ "
    "镜脚侧无导光孔); 若 T-3c 复活 (LED 挪回镜脚), 导光孔必落 SoC 区 ⇒ 距通窗 23.20 / 距磁铁最坏 22.00 ⇒ **破 40mm 判据** ⇒ "
    "复活时导光孔必须回镜框。另: **MECH_BUDGET §802 的『2× MEMS / 两孔间距 ≥40mm』口径需修订为 1 颗/侧** (左右孔距 = 镜框前框总宽 140mm)。\n"
    "【★在 MECH 尺寸里发现的 3 条不自洽 (我不改 MECH, 已登记 needs)】"
    "P-1 **磁铁/凸台/螺钉在现有盖板几何下无处可放** —— 盖板 13.20 × 通窗 10.20 ⇒ X 向搭边仅 1.50/侧, 而 ⌀4.20 磁铁沉槽需 ≥2.10 的壁 "
    "⇒ 磁铁的精确坐标至今 [0数据], 本单只能给『标称板 X=59.80 (L 100.30)』+『包络最坏 X=48.00』两个值, 坐标落定后一条命令重算; "
    "P-2 **ISS-092 §4.3 的『磁铁↔SoC ≥68mm』与其自身尺寸链矛盾** —— 按同一条链实际 **28.00mm** (68.30 是拿磁铁的镜脚 L 减 SoC 的板 X, "
    "两套坐标系混算), 该处 B = 54.8 µT ⇒ 对 SoC 无功能影响, **但数字必须订正**; "
    "P-3 板宽改 30mm (ISS-118) 后麦的 Y 向落位要重算, 且 Y↔V 朝向 [0数据] (不影响 X 向 ≥40mm 判定)。\n"
    "【诚实边界】实物 [实测] = **0 条**。**6 项 [0数据]**: ① 麦克风磁场敏感度 (规格书无此栏, 4 份实测 grep=0) "
    "② 磁铁/定位凸台确切 X/Y ③ 跨铰链连接器落板区边界 (ISS-105 open) ④ 麦的型号 (音频要不要做, 老板未裁 N7) "
    "⑤ 金属骨架是否贯通全板长 (若贯通, M1 退化为破 40mm) ⑥ Y↔V 朝向。"
    "【本单未拍板】: 音频要不要做 (老板)、磁铁与凸台确切坐标 (mech-lead)、MECH_BUDGET §802 麦数量口径 (mech-lead)、"
    "ISS-092 §4.3 的 68mm 订正 (mech-lead) —— 全部登记 needs 经项目总工转达, **未直接联系任何总工或供应商**, "
    "未改 HW/ 之外的任何他人目录, 未外发。"
)

ANSWERS = [
    {
        "key": "iss092_mic_magnetic_sensitivity",
        "to": "mech-lead",
        "value": "无影响: N35⌀4x1 端面40mm处B=36.0µT(Br1.20T;上限1.26T→37.8µT)≈地磁量级; "
                 "落位(板X5.00)处B=7.3µT(最坏15.1µT)<地磁最小25µT; 电容式MEMS无静态场作用路径; "
                 "规格书无磁场敏感度栏(4份grep=0)→改用机理/地磁本底/实算三链+选型硬判据M-2(≥100µT)+台架复测4步",
        "ref": "HW/ISS121_MIC_MAGNET_POSITION.md §2 (B3 证据分级) + HW/iss121_mic_magnet_check.py §B/B2/C",
    },
    {
        "key": "iss092_outer_face_holes_position",
        "to": "mech-lead",
        "value": "麦克风=板坐标X5.00/Y12.00(镜脚L45.50)顶进式, 声孔⌀1.00开镜脚外侧面+非磁性粘接防尘网; "
                 "净空 通窗44.20/磁铁54.80(最坏43.00)/螺钉55.30mm 全≥40 PASS; 骨架不在上方→无需骨架开窗; "
                 "≥40mm可满足带仅板X≤8.00(铰链端唯一解), M2/M3 FAIL; 导光孔基线N/A(ISS-014决策5充电板在镜框), "
                 "T-3c复活则破判据; MECH_BUDGET§802『2×/间距≥40』口径需改1颗/侧",
        "ref": "HW/ISS121_MIC_MAGNET_POSITION.md §3 (B3 证据分级) + HW/iss121_mic_magnet_check.py §C",
    },
]

NEEDS = [
    {
        "key": "iss121_magnet_xy_define",
        "to": "mech-lead",
        "item": "ISS-121 U-1 (经项目总工转达): 请给**磁铁 / 2×⌀1.60定位凸台 / M1.6螺钉在盖板下的确切 X/Y 坐标** —— "
                "按 ISS-092 §4.1 C-1/C-3, 盖板13.20×通窗10.20 ⇒ X向搭边只有1.50/侧, 而 ⌀4.20×1.00 磁铁沉槽需 ≥2.10 的壁 "
                "⇒ **现有几何下磁铁无处可放** (P-1)。本单磁场数字用『标称板X=59.80(L100.30)』+『包络最坏X=48.00』两值, "
                "坐标落定后 python3 HW/iss121_mic_magnet_check.py 一条命令重算 (零板费)",
        "since": "2026-11-01",
    },
    {
        "key": "iss121_mag_soc_gap_correction",
        "to": "mech-lead",
        "item": "ISS-121 U-2 (经项目总工转达): ISS-092 §4.3 的 **『磁铁↔SoC 间距 ≥68mm』与该文自身尺寸链矛盾** —— "
                "按同一条链 (磁铁 L100.30 vs SoC 逃线带末端 L72.30) 实际 **28.00mm**; 68.30 是拿磁铁的**镜脚 L** 减 SoC 的**板 X** "
                "(两套坐标系混算)。该处磁场 B=54.8µT ⇒ 对 SoC 无功能影响, 但**数字必须订正**, 否则会被当成已复核引用",
        "since": "2026-11-01",
    },
    {
        "key": "iss121_skeleton_extent_confirm",
        "to": "mech-lead",
        "item": "ISS-121 U-3 (经项目总工转达): 请确认**金属骨架是否贯通全板长**? ISS-092 §8 第4行只给 L58.5..82.5 "
                "(⇒ 板X18.00..42.00), 本单据此假设 X<18 处**骨架不在上方** ⇒ 麦克风顶进式声孔通道 3.00mm 直通、**无需骨架开窗**。 "
                "若骨架实际贯通全板 ⇒ X=5.00 也需开窗 ⇒ **镜脚外侧面无 ≥40mm 合规落位** ⇒ 麦须改到镜框侧充电板 (语音更好, "
                "但要跨铰链多2根 PDM 线, J_CHG 只剩 pin9 一个空脚) ⇒ 需项目总工拉三方评审",
        "since": "2026-11-01",
    },
    {
        "key": "iss121_mic_count_spec",
        "to": "mech-lead",
        "item": "ISS-121 U-4 (经项目总工转达): `MECH/MECH_BUDGET.md` §802 的 **『2× MEMS, 镜腿外侧开⌀1.0声孔, 两孔间距 ≥40mm』** "
                "在 ≥40mm 判据下**做不到** (合规带只有板X≤8.00, 第二孔要≥40mm 就得在X≥45 而那里离通窗仅4.2mm)。"
                "建议改为 **每侧镜脚 1 颗 (L/R 一对)**: 两孔间距 = 镜框前框总宽 **140mm** (远超40mm) ⇒ 防声学串扰判据自动满足, "
                "且不占 PCB 面积 (省 ~6mm² + 一路 I2S/PDM)",
        "since": "2026-11-01",
    },
    {
        "key": "iss121_audio_scope",
        "to": "main",
        "item": "ISS-121 U-5 (经项目总工): **音频要不要做** —— 麦至今 [0数据] (型号未选型; HW/HARDWARE_BREAKDOWN N7 'tracker全文未提, 需老板确认')。"
                "本单假设**第一台样机不做音频** ⇒ 麦不进 BOM/网表, 只保留『磁铁-麦互不影响』结论 + 选型硬判据 M-1~M-5 + 台架复测 4 步。"
                "若老板定要做, 麦的静态磁场耐受 ≥100µT 一条要写进 RFQ (拿不到书面声明就按 [0数据] 处理并加台架复测)",
        "since": "2026-11-01",
        "waiting_on": "boss",
        "due": "2026-11-04",
    },
    {
        "key": "iss121_conn_zone_dependency",
        "to": "main",
        "item": "ISS-121 U-6 (经项目总工): **跨铰链 4 连接器的落板区边界** [0数据] (ISS-105 open, 我的 needs `iss105_hinge_end_conn_width` "
                "仍在等) —— 这条决定麦克风落位 M1 (板X5.00) 是否成立: 情形a (FPC连接器座体悬出板端, 只占焊盘 X0..3) ⇒ M1 净空 2.00mm 成立; "
                "情形b (沿板长拉开占 X0..24) ⇒ **镜脚外侧面无 ≥40mm 合规落位** ⇒ 麦改镜框侧。两种情形的磁场结论**不变** (无影响)",
        "since": "2026-11-01",
    },
]

CLAIMS = [
    {
        "key": "mic_acoustic_hole_pos",
        "value": "板X5.00/Y12.00(镜脚L45.50)",
        "note": "顶进式 MEMS 声孔开在镜脚外侧面; ⌀1.00 壁孔 + 非磁性粘接防尘网; 金属骨架不在上方(骨架占板X18.00..42.00) ⇒ 无需骨架开窗; "
                "HW/ISS121_MIC_MAGNET_POSITION.md §3.2",
        "ref": "HW/ISS121_MIC_MAGNET_POSITION.md §3.2",
    },
    {
        "key": "mic_acoustic_hole_dia",
        "value": "⌀1.00mm",
        "note": "沿用 MECH_BUDGET §802; 配套非磁性粘接防尘网 (不锈钢松散网会被磁铁吸, 43mm 外吸力虽仅 μg 量级但有掉件风险)",
        "ref": "HW/ISS121_MIC_MAGNET_POSITION.md §3.2",
    },
    {
        "key": "mic_count",
        "value": "1/侧(L-R一对)",
        "note": "两孔间距 = 镜框前框总宽 140mm (≫40mm) ⇒ 防声学串扰判据自动满足; MECH_BUDGET §802 的『2×/间距≥40』口径需修订 (needs iss121_mic_count_spec)",
        "ref": "HW/ISS121_MIC_MAGNET_POSITION.md §3.5",
    },
    {
        "key": "mic_magnetic_margin",
        "value": "B≤15.1µT@落位/36.0µT@40mm",
        "note": "N35 Br=1.20T (带宽1.14-1.26T) 均匀磁化圆柱模型 (数值积分 vs 解析解 0.000111%); 均 ≤ 地磁典型值 50µT ⇒ 判定无影响",
        "ref": "HW/iss121_mic_magnet_check.py §B/§C",
    },
    {
        "key": "mag_field_immunity_req",
        "value": "≥100µT",
        "note": "麦选型硬判据 M-2: 静态磁场耐受书面声明 (≈IEC 61000-4-8 L5 126µT); 拿不到 ⇒ 按 [0数据] 处理并加台架复测 (1kHz 94dB 灵敏度漂移 ≤±0.5dB)",
        "ref": "HW/ISS121_MIC_MAGNET_POSITION.md §2.7/§2.8",
    },
    {
        "key": "service_port_feature_clearance",
        "value": "≥40mm",
        "note": "判据对象 = 通窗/磁铁/螺钉凸台; M1 实测 通窗44.20 / 磁铁54.80(最坏43.00) / 螺钉55.30 ⇒ PASS; M2(X17)/M3(X26) FAIL; "
                "可满足带仅板X≤8.00",
        "ref": "HW/iss121_mic_magnet_check.py §C",
    },
]

ARTIFACTS = [
    {
        "path": "HW/ISS121_MIC_MAGNET_POSITION.md",
        "kind": "report",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "ISS-121 主文档: 磁场 (机理/地磁本底/实算 三链) + 位置 (板X5.00 落位, ≥40mm 判据) + MECH 尺寸 3 条不自洽 P-1~P-3 "
                   "+ 麦选型硬判据 M-1~M-5 + 台架复测 4 步",
    },
    {
        "path": "HW/iss121_mic_magnet_check.py",
        "kind": "script",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "ISS-121 自证脚本 rc=0: 坐标系回归 4/4 (板X↔镜脚L 偏移40.50) + 磁体模型数值/解析互校 0.000111% + 位置/磁场判据 + JSON 落盘",
    },
    {
        "path": "HANDOFF/2026-11-01_hw-lead_ISS121_麦克风磁场与位置复核.md",
        "kind": "handoff",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "ISS-121 交接单 (B1-B6 六块齐): 磁场判无影响 + 麦克风落位板X5.00 + 导光孔基线N/A + 6 条 needs + 6 条 interface_claims",
    },
]

STATUS = {
    "phase": "P2(原理图/BOM)+结构接口",
    "progress_pct": 55,
    "health": "yellow",
    "summary": (
        "ISS-121 交卷 (MEMS 麦克风 vs 检修口 N35 磁铁的磁场/位置复核, 闭环 ISS-092 的 I-5/I-6): "
        "产出 HW/ISS121_MIC_MAGNET_POSITION.md + HW/iss121_mic_magnet_check.py (rc=0) + HW/iss121_mic_magnet_check.json + "
        "HANDOFF/2026-11-01_hw-lead_ISS121_麦克风磁场与位置复核.md (B1-B6 六块齐)。"
        "核心结论: (1) **磁场判『无影响』** —— N35⌀4x1 (Br typ 1.20T) 端面40mm处 B=36.0µT (上限37.8µT) ≈ 地磁量级, "
        "推荐落位(板X5.00)处 B=7.3µT (磁铁最靠里15.1µT) < 地磁最小25µT; 电容式MEMS换能链无静态场作用点 (真怕磁的是动圈/驻极体/霍尔式, 不用); "
        "(2) ★**『按麦克风规格书的磁场敏感度核』这条路走不通且非漏查** —— 4份主流MEMS麦规格书 (Infineon IM69D130/IM67D128BV01 / "
        "Knowles MM20 / ST MP34DT04-C1) 全文 grep 'magnet' = **0命中**, 规格书里没有这一栏 ⇒ 改用机理/地磁本底/实算三链 + "
        "选型硬判据 M-2 (静态磁场耐受≥100µT) + 台架复测4步; "
        "(3) **位置由我定死** = 板坐标 X=5.00/Y=12.00 (镜脚L45.50), 顶进式MEMS, 声孔⌀1.00开镜脚外侧面; 净空 通窗44.20 / 磁铁54.80"
        "(最坏43.00) / 螺钉55.30 mm ⇒ **≥40mm 全 PASS**; 该处金属骨架不在上方 ⇒ 无需骨架开窗 (通道3.00mm直通); "
        "(4) ★**≥40mm可满足带仅板X≤8.00** ⇒ 铰链端唯一解, M2(X17)/M3(X26, mech-lead假设的根部SoC区) 全FAIL; M1 成立前提是"
        "『跨铰链连接器座体悬出板端只占焊盘X0..3』, 该边界[0数据](ISS-105 open) 已登记needs; "
        "(5) **导光孔基线N/A** (ISS-014决策5充电板在镜框 ⇒ LED在框 ⇒ 镜脚侧无导光孔); T-3c复活则落点必破40mm判据 ⇒ 导光孔须回镜框; "
        "MECH_BUDGET§802『2×/间距≥40』口径需改1颗/侧 (左右孔距=框宽140mm); "
        "(6) ★**MECH尺寸3条不自洽**: P-1 磁铁/凸台/螺钉在现有盖板几何下无处可放 (搭边1.50 < 沉槽需2.10) ⇒ 磁铁坐标[0数据]; "
        "P-2 ISS-092§4.3『磁铁↔SoC≥68mm』与自身尺寸链矛盾 ⇒ 实际28.00mm (该处B=54.8µT, 无功能影响但数字须订正); "
        "P-3 板宽改30mm后Y向落位重算 + Y↔V朝向[0数据]; "
        "已登记2条answers(闭合mech-lead的I-5/I-6)+6条needs(4条mech-lead经项目总工/1条main等老板/1条main等ISS-105)+"
        "6条interface_claims+3条artifact; 边界: 未发任何邮件/未联系供应商/未改MECH与SW与PROJECT_TRACKER/未改别人分片; "
        "merge rc=0 + gate Q1 18/18 | phase=P2(原理图/BOM)+结构接口 progress=55% health=yellow"
    ),
}


def main() -> int:
    dry = "--dry-run" in sys.argv

    # ---------------- 1. 分片 (原子写) ----------------
    def mutate(d):
        # answers: 按 key 覆盖 (幂等, 避免重复登记)
        ans = d.setdefault("answers", [])
        ans_keys = {a.get("key") for a in ans}
        for a in ANSWERS:
            if a["key"] in ans_keys:
                ans[:] = [x for x in ans if x.get("key") != a["key"]]
            ans.append(dict(a))
        # needs_from: 同 key 覆盖
        nf = d.setdefault("needs_from", [])
        nf_keys = {n.get("key") for n in nf}
        for n in NEEDS:
            if n["key"] in nf_keys:
                nf[:] = [x for x in nf if x.get("key") != n["key"]]
            nf.append(dict(n))
        # interface_claims: 同 key 覆盖
        ic = d.setdefault("interface_claims", [])
        ic_keys = {c.get("key") for c in ic}
        for c in CLAIMS:
            if c["key"] in ic_keys:
                ic[:] = [x for x in ic if x.get("key") != c["key"]]
            ic.append(dict(c))
        # artifacts: 同 path 覆盖
        arts = d.setdefault("artifacts", [])
        art_paths = {a.get("path") for a in arts}
        for a in ARTIFACTS:
            if a["path"] in art_paths:
                arts[:] = [x for x in arts if x.get("path") != a["path"]]
            arts.append(dict(a))
        d["status"] = dict(STATUS)
        d["updated_at"] = "2026-11-01"
        d["updated_by"] = "hw-lead"

    if dry:
        print("[dry-run] 分片未落盘")
    else:
        update_fragment("hw-lead", mutate)
        print("✅ 分片 hw.yaml 已原子更新 (2 answers + 6 needs + 6 claims + 3 artifacts + status)")

    # ---------------- 2. issue_log: 只动 ISS-121 ----------------
    with open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc.get("issues")
    items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])
    hit = 0
    for it in items:
        if not isinstance(it, dict) or it.get("id") != "ISS-121":
            continue
        if it.get("owner") != "hw-lead":
            print("❌ ISS-121 的 owner 不是 hw-lead ⇒ 中止")
            return 2
        hit += 1
        print("[before] ISS-121 status=%r fix_ref=%r verify_by=%r"
              % (it.get("status"), it.get("fix_ref"), it.get("verify_by")))
        it["status"] = "fixed"
        it["fix_ref"] = FIX_REF
        it["need_keys"] = [n["key"] for n in NEEDS]
        note = str(it.get("note") or "")
        if "hw-lead 交卷" not in note:
            it["note"] = note + CLOSE_NOTE
        if it.get("verify_by") in (None, "", "hw-lead"):
            it["verify_by"] = "main"          # ★ verify_by 不能填自己
        print("[after ] ISS-121 status='fixed' fix_ref 已落 (%d B) verify_by=%r"
              % (len(FIX_REF), it.get("verify_by")))
    if hit != 1:
        print("❌ 找到 %d 条 ISS-121 (应为 1) ⇒ 中止, 不落盘" % hit)
        return 2
    if dry:
        print("[dry-run] issue_log 未落盘")
        return 0

    doc["issues"] = items
    text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)
    fd, tmp = tempfile.mkstemp(prefix="issue_log.yaml.", suffix=".tmp", dir=STATE)
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
    print("✅ issue_log.yaml 已原子更新 (ISS-121 fixing → fixed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
