#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-027: 把「原型制作计划」的产出登记进 mech-lead 分片 (原子写, 走 frag_write 模块 API)

★ 纪律: **禁止 open(p,"w") 写分片** —— 走 state/frag_write.py 的 update_fragment
  (tmp + fsync + os.replace, 读者永远看到完整文件)。
  与 MECH/_frag_update_iss091.py 同一套路。

用法:  python3 MECH/_frag_update_iss027.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

ARTIFACTS = [
    dict(path="MECH/skeleton_section_check.py", kind="script", version="v1.0", updated_at="2026-10-29",
         summary="金属骨架截面形状+重量口径+石墨H链 的独立复算 (rc=0, ISS-049 两问的可复现答复, "
                "hw-lead 明确把截面决定权交给结构侧): 独立复算**不共用 hw-lead 的代码路径**; "
                "① V覆盖需求 15mm板 = SoC沿板宽8.00+两侧各3.50 = 15.00 = 板宽 (SoC段骨架必须满宽; "
                "12mm板无扩散余量) ② 4候选截面重量: 满宽1.0=4.86g/对(判死) / 台阶1.0=3.62g/对(**与hw-lead报的3.62一致**) "
                "/ 台阶0.8=2.89g/对(落进§2.4 B的+1-3g) / 铜0.8=9.61g/对(重) ③ 石墨0.30铺PCB内侧 -> H链4.70(骨架1.0)"
                "/4.50mm(骨架0.8), 余2.60/2.80mm; 石墨0.54g/片=1.08g/对 归 W11 不占骨架预算 "
                "④ 骨架/石墨止于PCB段后缘X=60.00 (延伸进电池段=并联热路730->4.50 K/W) "
                "★ 不出新的皮肤侧温度数 (要完整热模型重算 U-3), 不拍板"),
    dict(path="MECH/PROTOTYPE_PLAN.md", kind="plan", version="v1.0", updated_at="2026-10-29",
         summary="ISS-027 原型制作计划 (分批打样/验证矩阵/回滚阶梯/依赖链): ① 四批解耦 B1 工艺标定 (打1件 coupon, "
                "34项 A5+B6+C7+D5+E5+F3+G3, 5条硬判据: 孔收缩+0.05~+0.15 / 0.80壁成型 / 45°免支撑 / 拉脱>=15N / "
                "0.10塞尺进不去) -> B2 镜脚装配验证 (打3件 = temple_cage×1 + 新增 R11 J_CHG防呆试样×2, 15项 H段, "
                "3条硬判据 H13<=0.25 / H4晃动<=0.10 / 类A类B孔不许混用) -> B3 镜框与光学 (打2件, 卡 JBD u1+u4) -> "
                "B4 整机装配 (1台, 卡 PCB+波导+固件三者取最晚); §1.6 第2批改版触发规则表 (现象->改哪层->产出->哪些数据可复用); "
                "② 验证矩阵三分类 A打印件可测10项 / B必须等电路板7项 / C必须等整机+固件+仪器6项; "
                "③ 回滚五层 L1打印参数0.5-1天 / L2打印件几何1-2天 / L3结构方案1-2周 / L4 PCB 2-4周+打样费(打印件全报废) / "
                "L5固件1-3天 + 六条判定顺序 (机械先排L1->L2->L3, L3前不许碰L4, L5永远最后); "
                "④ 衔接: RELIABILITY_TEST_PLAN (R11防呆试样现有包里没有->放B2; R4拉脱试样可由B1 coupon切出; "
                "T-14无损段排B4装配后/S0后/S1前; T-13不占独立步位) + measurements.yaml M-PRINT回填口径 (B2完成才升[实测]; "
                "B1的34项只回填MECH_BUDGET §5.4四行; M-FIT镜脚侧=B2/整机=B3后; M-WEIGHT=B4) + print_pack.3mf 现状与下一版; "
                "⑤ 时间与依赖链 (JBD回图与发货分两个里程碑) + G1->G2里程碑表; §6 20项 [0数据] 清单; "
                "★ [实测]实物条数=0 (本机无打印机无量具, ENV_PROBE.log 为证), 所有[实测]只指模型/脚本级真值"),
    dict(path="MECH/prototype_plan_check.py", kind="script", version="v1.0", updated_at="2026-10-29",
         summary="原型制作计划机械自检 (rc=0): 机械判定 ISS-027 五项验收 (①分批打样计划含改版触发规则 ②验证矩阵三分类+"
                "尺寸/干涉/佩戴/功能/热/续航六维度 ③回滚五层L1-L5含成本与耗时 ④与RELIABILITY_TEST_PLAN/measurements.yaml/"
                "print_pack.3mf的衔接 ⑤时间与依赖链含JBD/PCB/固件) + 三条铁律 (A 未测即通过措辞=0 / B 证据分级四标签齐全且"
                "声明'[实测]实物条数=0' / C 不替别人拍板) + §6 [0数据]清单>=10行 + 关键数字锚点 (46/46 / 0.95 / 0.65 / 24.50 / "
                "48.9-74.0) 与 fit_check.py / verify_budget.py 交叉核对"),
    dict(path="HANDOFF/2026-10-29_mech-lead_原型制作计划_ISS027.md", kind="handoff", version="v1.0",
         updated_at="2026-10-29",
         summary="ISS-027 交接单 (B1-B6 六块齐全): B1 五条带数字结论 (四批件数与验证项 / 矩阵三分类10+7+6项 / "
                "回滚五层成本差3个量级 / 给G1->G2的三条排期结论含'PCB必须在B1开工前冻结' / [实测]实物=0且20项[0数据]) ; "
                "B2 自评 13 条 (✅10 / ⚠️3, 其中3条诚实写出不达标与未验); B3 证据分级四档 + 口径纪律; "
                "B4 接口取值 4 条 (proto_batch_plan / proto_b1_coupon_measure_items / proto_b2_h_measure_items / "
                "proto_pcb_freeze_gate); B5 未决 5 条 (P-1 ISS-040 打印+量测执行方 / P-2 PCB冻结 / P-3 ISS-060三条几何 / "
                "P-4 B4佩戴可测项定义 / P-5 verify_print_pack文案漂移) + 6 条接口请求各带'我的假设'; B6 七条复现命令"),
]

CLAIMS = [
    ("proto_batch_plan", "B0-B4",
     "原型制作计划分批编号: B0 打印包就绪 / B1 工艺标定(打1件) / B2 镜脚装配验证(打3件) / B3 镜框与光学(打2件, 卡JBD) / "
     "B4 整机装配(1台). 每批硬判据与回滚层见 MECH/PROTOTYPE_PLAN.md §1 [推算-计划]",
     "MECH/PROTOTYPE_PLAN.md#1.1"),
    ("proto_b1_coupon_measure_items", "34",
     "B1 测量项数 (A5+B6+C7+D5+E5+F3+G3) —— coupon 一件覆盖全部工艺试样, 不多打; 这34项只回填 MECH_BUDGET §5.4 的4行, "
     "**不能**用来把 M-PRINT 升 [实测] [口径]",
     "MECH/PROTOTYPE_PLAN.md#1.2"),
    ("proto_b2_h_measure_items", "15",
     "B2 测量项数 (H段) —— M-PRINT 升 [实测] 的充要条件是这15项填完; M-FIT 镜脚侧=H4实物电芯插入, 整机侧须B3完成后才整体升",
     "MECH/PROTOTYPE_PLAN.md#1.3"),
    ("proto_pcb_freeze_gate", "B1开工前",
     "PCB 板框/厚度/层数/孔位的冻结点要求 —— 晚于 B1 则 L4 回滚 2-4 周 + B2 打印件全部报废; 板厚 4层0.8 vs 6层1.0 差0.34g "
     "且吃掉 PCB 段 H 余量 0.20mm (整机已推算48.9-74.0g vs 目标30-40g) [推算]",
     "MECH/PROTOTYPE_PLAN.md#5.3"),
    # --- ISS-049 两问的接口取值 (答复 hw-lead) ---
    ("mech_skeleton_section_shape", "台阶形 X19..33满宽15/其余10",
     "金属骨架截面形状 (hw-lead ISS-049 把决定权交给结构侧): 15mm 板下 SoC 沿板宽占8.00 + 两侧横向扩散带各3.50 = 15.00 "
     "= 板宽 -> SoC 段骨架必须满宽; 非 SoC 段只需承PCB, 取10.00. 满宽60x15已判死 [推算]",
     "MECH/skeleton_section_check.py#2"),
    ("mech_skeleton_thickness_mm", "0.80",
     "建议厚度 (非拍板): 0.80mm 铝台阶形 = 2.89g/对 落进 MECH_BUDGET §2.4 B 的 '+1-3g'; 1.00mm = 3.62g/对 超0.62g "
     "(与 hw-lead 独立复算一致). ⚠️ 热学代价: 导热截面变小 -> Tj 会升, 必须并进 U-3 热模型重算一起算, "
     "不能只看重量选截面 [推算]",
     "MECH/skeleton_section_check.py#2"),
    ("mech_graphite_placement", "PCB内侧(骨架与PCB之间)",
     "石墨片 0.30mm 铺装位置 (ISS-049 问): 与板同长同宽 X[0,60]xY[0,15], 铺在骨架与PCB之间 -> PCB段 H 链 "
     "4.70mm(骨架1.0)/4.50mm(骨架0.8), 余 2.60/2.80mm (>=0.60 规矩). 重量0.54g/片=1.08g/对 归 MECH_BUDGET §3 W11, "
     "不占 §2.4 B 骨架预算 [推算]",
     "MECH/skeleton_section_check.py#4"),
    ("mech_graphite_weight_g_per_pair", "1.08",
     "石墨 0.30x60x15 = 0.270cc x 2.00 g/cc = 0.54g/片 = 1.08g/对 (与 hw-lead ISS-049 报的 0.54g/片 一致). "
     "归 MECH_BUDGET §3 W11 (石墨散热膜+导热垫+隔热垫 1-2g) [推算]",
     "MECH/skeleton_section_check.py#3"),
]

NEEDS = [
    dict(key="proto_pcb_freeze_gate", to="main", since="2026-10-29", due="2026-10-31",
         item="★ISS-027 排期硬前置: **PCB 板框/厚度/层数/孔位必须在 B1 (工艺标定批) 开工前冻结**. "
              "理由: 老板 10-29 00:49 已令跳过酷芯微改选国内 TOP5, PCB 还开着变更口子; 若 B2 打完再改板 -> L4 回滚 2-4 周 + "
              "打样费 + **B2 打印件全部报废**. 附带账: 板厚 4层0.80mm(1.33g) vs 6层1.00mm(1.67g) 差 0.34g, 而整机已推算 "
              "48.9-74.0g vs 目标30-40g, 这0.34g不是可忽略量级; PCB段 H 向余量 2.80mm 也会被板厚差 0.20mm 吃掉一部分. "
              "**我的建议(不拍板): 按 4 层 0.80mm 冻结**. 依据 MECH/PROTOTYPE_PLAN.md §5.3"),
    dict(key="proto_pcb_thickness_tier", to="hw-lead", since="2026-10-29", due="2026-10-31",
         item="ISS-027 接口请求 (经项目总工转达): PCB 最终层数/厚度档位 (4层0.80 vs 6层1.00) + 板重口径 (1.33g vs 1.67g) + "
              "是否带屏蔽罩及高度上限, 因为 B2 要按它做 mock 板 (60×15×厚度) 才能验 ⌀2.4 间隙孔 + 2×⌀1.6 让过孔 + 装入姿态. "
              "**我的假设 (若不回应我按这个做): 按 4 层 0.80mm** 做 mock 板与 H 链校核 (省0.34g, H余量宽0.20mm); 若实际投6层, "
              "H链余量按 -0.20 重算并上报. 另: **假定 PCB 面上不需要结构开孔** (散热孔/接地过孔/固定孔避让), 打印件按"
              "'板平放+2×⌀2.4间隙孔+2×⌀1.6让过孔'预留, 若需开孔请在 B4 前告知"),
    dict(key="proto_wear_criteria", to="main", since="2026-10-29", due="2026-11-05", waiting_on="boss",
         item="ISS-027 P-4: **B4 佩戴体验的可测项定义** (夹持力 / 配重分布 / 鼻梁压感, 各测什么、判据多少、用什么器具). "
              "现状: 这三项全标 [0数据] **且没有判据**, 而 1 台样机只有一次采集机会 (RELIABILITY_TEST_PLAN §B2.3/B3.3 的"
              "样本量硬边界), 漏测后续补不回来. 需老板给可测项定义 (经项目总工转达)"),
    dict(key="proto_b4_reliability_kit", to="boss", since="2026-10-29", due="2026-11-05", waiting_on="boss",
         item="ISS-027 附带: B4 整机装配当天要做 **T-14 无损段** (弯折区结构审查 + **J_CHG 反插 20 次**) 与 **T-13 挂测位就位**, "
              "两者都需要零星器具: 反插只需 J_CHG 实物一对(打印的 R11 防呆件 B2 出) + 计数; T-13 需要协议分析器/示波器差分探头 + "
              "自动传输脚本. 与已提的 mech_reltest_kit_site (场地工装总预算) **同源同账**, 本条只追加'本批次需要的器具清单', "
              "不重复申请金额. 另需提醒: **ISS-040 的打印+量测执行方 (打印机192.168.1.68跨网段 + 无卡尺/千分尺/塞尺) 是 B1 的唯一硬前置**, "
              "它解锁 B1 -> B2 -> G2 直接少2项 (M-PRINT + M-FIT镜脚侧), 是当前投入产出比最高的动作. 经项目总工转达"),
]

BLOCKERS = [
    dict(id="MECH-B9", severity="high", waiting_since="2026-10-29",
         desc="ISS-027: 原型制作计划已交 (MECH/PROTOTYPE_PLAN.md + prototype_plan_check.py rc=0), 但**B1 批次的唯一硬前置 "
              "ISS-040 (打印+量测执行方) 至今未闭**: 本机物理上无法打印/量测 (打印机 192.168.1.68 与本机 192.168.2.4/24 跨网段 "
              "不可达: ping 无响应 + TCP 990/8883/6000/4000 全 closed; 无切片器; 无卡尺/千分尺/塞尺; 无 USB 串口 —— "
              "证据 MECH/print/ENV_PROBE.log). 因此 B1 之前所有尺寸仍是图纸值, M-PRINT/M-FIT/M-WEIGHT 三项 [实测] 全空, "
              "G2 缺 7 项一项没减. **B1+B2 共 49 项实测不需要 PCB 也不需要 JBD**, 是当前唯一不被外部依赖卡死的路径 —— "
              "但要靠 ISS-040 落地才走得动. 未闭之前: 打印件0件 -> ISS-017 无法闭 -> G2 不可判.",
         needs_from=["boss", "main"]),
    dict(id="MECH-B10", severity="medium", waiting_since="2026-10-29",
         desc="ISS-049 遗留: 金属骨架的**热学代价**未重算 —— 我给 hw-lead 的截面建议是 0.80mm 厚 (比 1.00 轻 0.73g/对, "
              "落进 MECH_BUDGET §2.4 B 的 '+1-3g' 预算), 但**铝的导热截面变小 -> Tj 会升**, 而 §2.3.1 的皮肤侧 46.5°C "
              "(0.23W 按需触发口径) **已经超 ISO 13732-1 的 43°C 红线 3.5°C**. 也就是说: 重量上省下来的 0.73g, "
              "热学上可能还回去. 这两个数必须**一起**算, 不能只看重量选截面. 重算需完整热模型 (含石墨铺装范围 + "
              "骨架截面形状 + 隔热层), 即 PCB_MOUNT_PIN_SET2.md §5 U-3 那张单. 未重算前: "
              "**我不出新的皮肤侧温度数**, 也不把 0.80mm 当已定版 —— 只作为待裁候选.",
         needs_from=["main", "hw-lead"]),
]

# ---------------------------------------------------------------------
# ISS-049 两问的答复 (hw-lead 明确把决定权交给结构侧)
# 关键: answers 的 key 必须用**对方给的 key**, 且 to 必须是对方, 才算真闭环
# ---------------------------------------------------------------------
ANSWERS = [
    dict(key="iss049_skeleton_profile", to="hw-lead",
         value="台阶形 X19..33满宽15 / 其余10, 厚0.80铝(建议) = 2.89g/对",
         ref="MECH/skeleton_section_check.py rc=0 §2 候选C; 重量口径 3.62g/对(t=1.0) 与你报的一致, 独立复算; "
             "0.80mm 才落进 MECH_BUDGET §2.4 B 的 +1-3g; 满宽 4.86g/对 维持判死"),
    dict(key="iss049_graphite_hchain", to="hw-lead",
         value="石墨0.30铺PCB内侧(骨架与PCB之间), PCB段H链4.70mm(骨架1.0)/4.50mm(骨架0.8), 余2.60/2.80mm",
         ref="MECH/skeleton_section_check.py rc=0 §4; 骨架与PCB之间, 与板同长同宽 X[0,60]xY[0,15]; "
             "重量 0.54g/片=1.08g/对 归 MECH_BUDGET §3 W11, 不占 §2.4 B 骨架预算; "
             "石墨/骨架一律止于 PCB 段后缘 X=60.00 (延伸进电池段=并联热路 730->4.50 K/W)"),
    dict(key="iss049_mount_screw", to="hw-lead",
         value="确认: 螺钉头只落PCB皮肤侧沉孔, 严禁接触皮肤侧下壳; 打印件上壳需2xD2.4+2xD1.6让过孔",
         ref="MECH/PCB_MOUNT_PIN_SET2.md §4 (热学硬约束) + §3 (打印件连带: 让过孔1->2个/螺钉孔距40->44mm/"
             "定位板长50->60mm, 随打印包改版授权一并吸收)"),
    dict(key="iss049_segment_order", to="hw-lead",
         value="确认: PCB段在铰链端/电池段在尾端, PCB段后缘=板坐标X=60.00",
         ref="MECH/BOARD_WIDTH_15MM.md §2.6 (骨架长度上限=止于PCB段后缘, 不因板宽改变) + "
             "MECH/CLEARANCE_FIX.md (电池段前端壁引电极)"),
]

STATUS = dict(
    phase="P2(ISS-027 原型制作计划已交: B0-B4 四批 + 验证矩阵 + 回滚五层 + 依赖链 + 20项[0数据]清单; 待 ISS-040 打印+量测执行方)",
    progress_pct=86,
    health="yellow",
    summary="第8轮 ISS-027: 新增 MECH/PROTOTYPE_PLAN.md (分批打样/验证矩阵/回滚阶梯/依赖链) + MECH/prototype_plan_check.py "
            "(rc=0 机械判定 ISS-027 五项验收 + 三条铁律) + HANDOFF/2026-10-29_mech-lead_原型制作计划_ISS027.md (B1-B6六块齐)。"
            "核心结论: (1) **四批解耦** B1工艺标定(打1件coupon, 34项, 5条硬判据: 孔收缩+0.05~+0.15/0.80壁成型/45°免支撑/"
            "拉脱>=15N/0.10塞尺进不去) -> B2镜脚装配验证(打3件 = temple_cage×1 + **新增R11 J_CHG防呆试样×2**, 15项H段, "
            "3条硬判据 H13<=0.25/H4晃动<=0.10/类A类B孔不许混用) -> B3镜框与光学(打2件, 卡JBD u1+u4) -> B4整机装配(1台, "
            "卡PCB+波导+固件取最晚); §1.6 给第2批改版触发规则表 (现象->改哪层->哪些数据可复用); "
            "(2) **验证矩阵三分类**: A打印件阶段可测10项 / B必须等电路板7项 / C必须等整机+固件+仪器6项; "
            "(3) **回滚五层成本差3个量级**: L1打印参数0.5-1天 / L2打印件几何1-2天 / L3结构方案1-2周(动锁死表需裁) / "
            "L4 PCB **2-4周+打样费(打印件全报废)** / L5固件1-3天; 判定顺序: 机械先排L1->L2->L3, L3前不许碰L4, L5永远最后; "
            "(4) **给G1->G2的三条排期结论**: ①PCB板框/厚度/层数必须在B1开工前冻结(否则改板->打印件报废+重投板2-4周) "
            "②JBD'回图'与'发货'分两个里程碑催(B3只等u1/u4图不等实物, 实物4-8周) ③**ISS-040是本周唯一催办项**(解锁B1->B2->"
            "G2直接少2项, 投入产出比最高); (5) 衔接: R11防呆试样现有打印包里没有->放B2, R4拉脱试样可由B1 coupon切出, "
            "T-14无损段排B4装配后/S0后/S1前, T-13不占独立步位; M-PRINT升[实测]=B2完成(B1的34项只回填MECH_BUDGET §5.4四行), "
            "M-FIT镜脚侧=B2/整机=B3后, M-WEIGHT=B4; (6) ★诚实边界: [实测]实物条数=0, **20项关键量在实物到手前只能标[0数据]**, "
            "打印件与量测环境不具备的证据见 ENV_PROBE.log; (7) 新增4条interface_claims + 4条needs_from + 1条blocker(MECH-B9) + "
            "3条artifacts。★ 本单只交计划与判据, 不拍板 (裁断点全写P-1~P-5并注明走谁); 未联系任何供应商(外发经PM)。",
)


def main():
    def mutate(d):
        d.setdefault("artifacts", [])
        existing_paths = {a.get("path") for a in d["artifacts"]}
        for a in ARTIFACTS:
            if a["path"] not in existing_paths:
                d["artifacts"].append(a)

        d.setdefault("interface_claims", [])
        existing_keys = {c.get("key") for c in d["interface_claims"]}
        for key, value, note, ref in CLAIMS:
            if key not in existing_keys:
                d["interface_claims"].append(
                    {"key": key, "value": value, "note": note, "ref": ref})

        d.setdefault("needs_from", [])
        existing_need_keys = {n.get("key") for n in d["needs_from"]}
        for n in NEEDS:
            if n["key"] not in existing_need_keys:
                d["needs_from"].append(n)

        d.setdefault("answers", [])
        existing_ans = {(a.get("key"), a.get("to")) for a in d["answers"]}
        for a in ANSWERS:
            if (a["key"], a["to"]) not in existing_ans:
                d["answers"].append(a)

        d.setdefault("blockers", [])
        existing_bid = {b.get("id") for b in d["blockers"]}
        for b in BLOCKERS:
            if b["id"] not in existing_bid:
                d["blockers"].append(b)

        d["status"] = STATUS
        d["updated_at"] = "2026-10-29T09:12:00+08:00"
        d["updated_by"] = "mech-lead"

    d = update_fragment("mech-lead", mutate)
    print(f"[frag_write] ✅ mech.yaml 已原子更新: "
          f"artifacts={len(d.get('artifacts') or [])} "
          f"claims={len(d.get('interface_claims') or [])} "
          f"needs={len(d.get('needs_from') or [])} "
          f"answers={len(d.get('answers') or [])} "
          f"blockers={len(d.get('blockers') or [])}")
    print("[frag_write] → 再跑 python3 state/merge.py")


if __name__ == "__main__":
    main()
