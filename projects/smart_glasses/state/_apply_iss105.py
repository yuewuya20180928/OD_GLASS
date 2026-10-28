#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-105 一次性分片更新器 (原子写, 走 state/frag_write.py 的 update_fragment)

纪律: 只写 hw-lead 自己的分片; 禁止 open(p,"w")。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from frag_write import update_fragment  # noqa: E402


def claim(d, key):
    for c in d.get("interface_claims") or []:
        if c.get("key") == key:
            return c
    return None


def mutate(d):
    # ---------- ① pcb_outline: 50x12mm -> 60x15mm ----------
    c = claim(d, "pcb_outline")
    assert c is not None, "pcb_outline 缺失"
    assert c["value"] == "50x12mm", f"pcb_outline 预期旧值 50x12mm, 实为 {c['value']}"
    c["value"] = "60x15mm"
    c["note"] = ("★板宽 15 = 老板 10-27 拍板; 板长 60 = 项目总工 10-28 裁 (60x15=900mm² 使双面贴面积缺口闭合, "
                 "长度余量 14.50mm, 不动镜脚长度方案, 不砍 BOM); 镜脚截面 H7.30/V38.00/L130.00 不因板宽改变 "
                 "(板宽是 V 向尺寸, 不进 H 链); ★结构侧已证伪『净高 37->40 / 打印件要改版』 (净高 38mm 一毫米不用动)")
    c["ref"] = "HW/PCB_OUTLINE_60x15.md#1"

    # ---------- ② pcb_width_recommend: 删掉已作废的『代价镜腿根部净高+3mm』 ----------
    c = claim(d, "pcb_width_recommend")
    assert c is not None, "pcb_width_recommend 缺失"
    assert "代价镜腿根部净高+3mm" in c["note"], "note 里没有预期作废串, 手工核对"
    c["note"] = ("第一台样机锁 15mm (逃线带误差容忍 +1.25mm vs 12mm 的 +0.20mm); "
                 "★已拍板 10-27; ★结构侧代价 = 几乎为零 (三方向余量一字不变, 净高 38mm 不动, 打印件不改版); "
                 "板长 60 见 pcb_outline")
    c["ref"] = "HW/PCB_OUTLINE_60x15.md#1"

    # ---------- ③ chg_input_limit: 300Ω 档 -> 390Ω 档 ----------
    c = claim(d, "chg_input_limit")
    assert c is not None, "chg_input_limit 缺失"
    assert c["value"] == "1.07-1.30A", f"chg_input_limit 预期旧值 1.07-1.30A, 实为 {c['value']}"
    c["value"] = "1.00A/0.82A/0.411A"
    c["note"] = ("R_ILIM=390Ω 档 (老板 10-28 拍板『边戴边充不允许』=> 皮肤温度不再是充电时硬约束 => 可提速; "
                 "换料不换板): IINMAX max 1.00A / ICHG max 0.82A / 单 pin 0.411A (pin1+pin2 双 pin 均分); "
                 "★300Ω 档已判死 (单 pin 0.534A > 任何 0.5mm pitch FPC ZIF 的 0.5A 额定天花板, 想上 1A 只能 1.0mm pitch 而铰链区装不下); "
                 "260Ω/680Ω 亦不可用/过剩, 详见档位表; R_ILIM 是必装件 (不装 => REG04 复位默认 ICHG 2048mA 会让铰链过 2.05A)")
    c["ref"] = "HW/PCB_OUTLINE_60x15.md#3.4"

    # ---------- ④ 新增: 板长 / 螺钉孔位 / 充电档位 / J_CHG 采购 ----------
    def upsert(key, value, note, ref):
        c = claim(d, key)
        if c is None:
            d.setdefault("interface_claims", []).append(
                {"key": key, "value": value, "note": note, "ref": ref})
        else:
            c["value"] = value
            c["note"] = note
            c["ref"] = ref

    upsert("pcb_length", "60mm",
           "板长 60 = 项目总工 10-28 裁 (60x15=900mm² 闭合双面贴面积缺口; 长度余量 14.50mm); 骨架长度上限仍 = PCB 段后缘",
           "HW/PCB_OUTLINE_60x15.md#1.1")

    upsert("pcb_mount_holes_xy", "M1.2(5.0,2.5)(55.0,12.5) H7(15.0,7.5)",
           "★ISS-049 定版 (板长 60 坐标, 原点在左下角, X=板长 0..60 / Y=板宽 0..15): "
           "2xM1.2 ⌀1.4 对角分布 (5.0,2.5) 与 (55.0,12.5) + 1x⌀2.0 H7 定位销 (15.0,7.50 中心线); "
           "★15mm 下器件带仅 2.70mm/边, 孔心到板边 2.50mm 仍压 SoC 逃线带 0.50mm => 必须沿板长移出逃线区; "
           "本方案与逃线带 X[20.20,31.80] 零重叠 (机械复算 0.000mm²); 骨架多一个方向加工面待项目总工与骨架件核",
           "HW/PCB_OUTLINE_60x15.md#2.3")

    upsert("chg_rilim", "390Ω",
           "R_ILIM 电阻取值 (0402 ±1%, 必装件, 换料不换板); IINMAX=KILIM/RILIM, KILIM=320/355/390 AΩ; "
           "充电 ~29min (390Ω max 档); 皮肤温度保守口径 42.14°C (<43°C 红线)",
           "HW/PCB_OUTLINE_60x15.md#3.4")

    upsert("chg_single_pin_a", "0.411A",
           "J_CHG pin1/pin2 双 pin 均分后的单 pin 电流 (390Ω 档 max); 对 0.5mm pitch ZIF 触点天花板 0.5A 余量 1.22x; "
           "★工况前提: 只有 pin1/pin2 载流, 其余脚 <=1mA (FH12 的 70% 降额条款只针对全部触点同时导通)",
           "HW/PCB_OUTLINE_60x15.md#3.3")

    upsert("j_chg_qty", "2",
           "★实物一对 (框侧充电板座 1 + 脚侧主 PCB 座 1): 网表只声明 1 只逻辑器件, 采购/备料必须按 2 只算; "
           "网表侧建议拆 J_CHG_A(框侧)/J_CHG_B(脚侧) 两个 ref",
           "HW/PCB_OUTLINE_60x15.md#3.2")

    upsert("j_chg_contact_rating_min", "0.5A",
           "★选型硬判据 (从 0.35A 收紧): 0.35A 是 FH12『全触点导通用 70%』的降额值, 按 0.35A 判 390Ω 档单 pin 0.411A 在保守读法下不合格; "
           "收紧到 0.5A 后两种读法都过; 首选 Hirose FH12-10S-0.5SH(55) (0.5A/触点, 0.5mm pitch, 座高 2.0mm)",
           "HW/PCB_OUTLINE_60x15.md#3.3")

    upsert("j_chg_preferred_part", "FH12-10S-0.5SH(55)",
           "J_CHG 首选型号 (Hirose FH12 系列, 1x10p @0.5mm, 0.5A/触点, 座高 2.0mm); "
           "★未询价 (RFQ 草稿 state/outbox/j_chg_rfq.md, 待老板放行); 10p 外形尺寸 [0数据] 未核",
           "HW/PCB_OUTLINE_60x15.md#3.1")

    # ---------- ⑤ needs_from: mech-lead 同步 pcb_outline (冲突) ----------
    d.setdefault("needs_from", []).append({
        "key": "iss105_pcb_outline_sync_60x15",
        "to": "mech-lead",
        "item": ("你的分片 interface_claims.pcb_outline 仍写 '50x15mm' (板长暂维持 50), 但板长已被项目总工 10-28 裁为 60mm "
                 "(60x15=900mm² 使双面贴面积缺口闭合, 长度余量 14.50mm)。我已把 hw-lead 侧的 pcb_outline 改成 '60x15mm' "
                 "=> 合并器现在报 pcb_outline 冲突 (60x15mm vs 50x15mm)。请把 mech.yaml 的 pcb_outline 同步成 60x15mm "
                 "(板宽 15 不变), 或删掉该 key 改用已有的 pcb_board_width=15mm + pcb_length=60mm 两个细分 key。"
                 "另: 你的 pcb_mounting note 已写明 M1.2 压逃线带 0.50mm 要沿板长移出, 我已按你给的坐标定版 (见 pcb_mount_holes_xy)。"
                 "同时更正一条: 你 BOARD_WIDTH_15MM.md §7 R-1 的『板重 +0.24g』是单位错误 (0.48cc 体积当重量), "
                 "真值 60x15x1.0mm 6层 = 1.67g, 增量 +0.56g, 请一并更正。"),
        "since": "2026-10-28",
    })

    # ---------- ⑥ needs_from: main (J_CHG / 充电口径一致性) ----------
    d.setdefault("needs_from", []).append({
        "key": "iss105_chg_spec_consistency_390",
        "to": "main",
        "waiting_on": "main",
        "due": "2026-10-30",
        "item": ("充电档位已定 390Ω (网表 P1 行 44/45 + BOM_v1 行 25 都是 390Ω), 但同库还有 3 处写 300Ω 需你统一: "
                 "① HW/CHARGE_BOARD_SPEC.md §2.4 档位表把 300Ω 标成『★本规格推荐值』, §2.8/§3.4/§4 多处按 300Ω 推算; "
                 "② HW/netlist_v1.csv P10 行 484 与行 494 的 note 仍写 R_ILIM=300Ω (行 44/45 已写 390Ω) => 同一份网表内部自相矛盾; "
                 "③ state/p10_rows.json (P10 页数据源) 也带 300Ω 措辞。这三个文件都不在本单边界内 (我只改了 hw.yaml), 请你或项目总工统一为 390Ω。"
                 "另: 网表 J_CHG 仍只声明 1 只 ref, 实物是 2 只 (框侧+脚侧) —— 建议拆成 J_CHG_A/J_CHG_B 两个 ref 并在 BOM 备料栏写『实物 2 只』。"),
        "since": "2026-10-28",
    })

    d.setdefault("needs_from", []).append({
        "key": "iss105_jchg_rfq_release",
        "to": "main",
        "waiting_on": "boss",
        "due": "2026-10-31",
        "item": ("J_CHG 询价草稿 state/outbox/j_chg_rfq.md 已就绪 (硬判据 C-1~C-8 + F-1~F-5, 含单触点 >=0.5A 的书面确认、"
                 "可插厚度 >=0.25mm、机械防呆), 但**未发**。请求放行外发 (收件方 Hirose + 国产对标), 外发一律经你。"
                 "★采购口径已按『实物一对』写进 RFQ 与 BOM 备料栏, 别只按网表的 1 只 ref 备料。"),
        "since": "2026-10-28",
    })

    d.setdefault("needs_from", []).append({
        "key": "iss105_hinge_end_conn_width",
        "to": "main",
        "due": "2026-10-31",
        "item": ("★铰链端板宽核算没人做过: 4 条跨铰链连接器 J_CHG 10p + CONN_USB 4p + CONN_CAM 18p + CONN_LIGHT 22p "
                 "= 54 触点 @0.5mm = 27mm 焊盘排, 而镜脚主 PCB 铰链端板宽只有 15mm (ISS-085 的『堆叠 26.5mm』算的是 FPC 排线竖向堆叠, 不是 PCB 焊盘排宽度)。"
                 "3 条出路: ① 沿板长 X 依次拉开 (吃掉铰链端 20.20mm 长度, 4 条约需 20-24mm, 刚好不够) "
                 "② 其中 2 条 (尤其 CONN_LIGHT 22p) 移到充电板/镜框侧 (光机本来在框内) "
                 "③ 改板宽/拆子板。请项目总工组织三方评审裁决。"),
        "since": "2026-10-28",
    })

    # ---------- ⑦ answers: 回答 mech-lead 的 4 条需求 (证据都在我的既有产出里) ----------
    def answer(key, to, value, ref):
        d.setdefault("answers", []).append({"key": key, "to": to, "value": value, "ref": ref})

    answer("iss091_jchg_contact_rating", "mech-lead",
           "Hirose FH12-10S-0.5SH(55) (0.5mm pitch / 1x10p / 0.5A 每触点 / 座高 2.00mm / UL94V-0); "
           "★判据从 0.35A 收紧到 0.5A (0.35A 是 FH12『全触点导通用 70%』的降额值, 按 0.35A 判 390Ω 档单 pin 0.411A 在保守读法下不合格); "
           "★工况前提: 只有 pin1/pin2 载流 (0.411A), 其余脚 <=1mA => 70% 降额条款不适用, 余量 1.22x; "
           "★300Ω 档正式判死 (单 pin 0.534A > 0.5A 触点天花板); 型号未询价 (RFQ 草稿 state/outbox/j_chg_rfq.md, 待放行)",
           "HW/J_CHG_SELECTION.md#2.1+#3.2")

    answer("iss091_fpc_vendor_caps", "mech-lead",
           "三项能力已写成 RFQ 硬判据 F-1~F-5: ① 分段铜厚 固定段 2oz / 弯折段 1oz + 过渡斜坡 >=1.0mm "
           "(2oz 在 R3.0 弯折段应变 1.167% => 寿命掉到 1/16~1/32) ② L2/L3 在 pin1-4 区域 keep-out 且 CAM 不自动修复 "
           "③ 0.5mm pitch 下载流铜箔加宽到 0.40mm (需厂商确认最小间隙 0.1mm) + 焊盘改加长型 (>=0.80mm, 带宽 <=0.30mm); "
           "另 F-4 每 pin 0.411A 持续 (1.07A 不接受, 触点天花板)",
           "HW/J_CHG_SELECTION.md#2.2 + MECH/FPC_FAB_NOTES.md#2")

    answer("iss091_contact_res_def", "mech-lead",
           "口径澄清: 按**单个连接器界面**计 (每个界面 5-30mΩ/pin), 路径内 2 个界面 (框侧 + 脚侧) = 10-60mΩ/pin; "
           "FPC 铜箔段 (31mm) 电阻单独建模不混进界面电阻 (你的 trace_table 已是这个分法, 口径一致)。"
           "口径B (整条 pin 路径) 下压降 111->40-87mV, 两种口径**结论方向一致** (充电必须摘下眼镜), 所以这个澄清不改变任何裁决; "
           "接触电阻本身仍是 [0数据] (厂商规格书未到), 选型时按 5-30mΩ/pin 保守代入",
           "HW/PCB_OUTLINE_60x15.md#3.1 + MECH/HINGE_POWER_CALC.md")

    answer("iss085_conn_pin_convergence", "mech-lead",
           "跨铰链 4 条链路 pin 数已收敛并落网表 (0.5mm pitch 统一): J_CHG 1x10p (pin1/2 载流双 pin) / "
           "CONN_USB 4p (pin3=GND, pin4=GND 双回流) / CONN_CAM 18p (含 pin18 回流地) / CONN_LIGHT 1x22p (末脚接 GND, 差分有回流)。"
           "★声明 pin 数 == 网表实际引用已是门禁判据 (你提的 F-1 断链已修)。"
           "★但新增一条待裁决: 这 4 条若全落镜脚主 PCB 铰链端, 焊盘排合计 54 触点 = 27mm > 15mm 板宽 (见 needs_from iss105_hinge_end_conn_width)",
           "HW/netlist_v1.csv (P9 跨铰链页) + HW/INTERFACE_TABLE.md")

    # ---------- ⑧ artifacts ----------
    d.setdefault("artifacts", []).append({
        "path": "HW/PCB_OUTLINE_60x15.md",
        "kind": "pcb-outline",
        "version": "v1.0",
        "updated_at": "2026-10-28",
        "summary": ("ISS-105 交付: PCB 板框 60x15mm 定版 (板宽15=老板10-27 / 板长60=项目总工10-28, 面积900mm² 对双面贴需求909.72差-9.72) "
                    "+ ISS-049 定位孔位定版 (2xM1.2 ⌀1.4 对角分布 (5.0,2.5)/(55.0,12.5) + 1x⌀2.0H7 (15.0,7.50), 与 SoC 逃线带 X[20.20,31.80] 零重叠 0.000mm²) "
                    "+ J_CHG 采购口径『实物一对』 (1x10p@0.5mm ZIF, 框侧座+脚侧座, 单触点>=0.5A, 首选 FH12-10S-0.5SH(55), 未询价 RFQ 草稿待放行) "
                    "+ 充电档位 390Ω (IINMAX 1.00A/ICHG 0.82A/单pin 0.411A, 300Ω档判死) "
                    "+ 板重口径更正 (旧『0.48g』是 50x12x0.8 体积当重量, 60x15x1.0 6层真值 1.67g, 增量 +0.56g 不是 +0.24g) "
                    "+ 3 条自发现 (板重单位错 / 铰链端 54 触点 vs 15mm 板宽没人算过 / 390Ω 档余量在电芯侧) + 6 条未决"),
    })
    d.setdefault("artifacts", []).append({
        "path": "HANDOFF/2026-10-28_hw-lead_ISS105_板框60x15与J_CHG采购口径.md",
        "kind": "handoff",
        "version": "v1.0",
        "updated_at": "2026-10-28",
        "summary": ("ISS-105 交接单 (B1-B6 六块齐全): 分片两个过期值已更正 (pcb_outline 50x12->60x15mm / chg_input_limit 300Ω->390Ω) "
                    "+ J_CHG 采购口径写死『实物一对』 + ISS-049 螺钉孔定版 + §5/§7 作废标注已扫干净 (grep 净高/改版/37→40 逐条标) "
                    "+ 3 条自发现 + 5 条未决 + 3 条 needs_from + 4 条回答 mech-lead"),
    })

    # ---------- ⑨ status ----------
    st = d.setdefault("status", {})
    st["phase"] = "P2(原理图/BOM)+板框定版"
    st["progress_pct"] = 52
    st["health"] = "red"
    st["summary"] = (
        "ISS-105闭: 分片两个过期值已原子更正 (state/frag_write.py) —— pcb_outline 50x12mm->60x15mm (板宽15=老板10-27/板长60=项目总工10-28, "
        "面积900mm²闭合双面贴缺口309.72->9.72mm²) 且删掉已作废的『代价镜腿根部净高+3mm』(结构总工已证伪: 净高38mm一毫米不用动, 打印件不改版); "
        "chg_input_limit 1.07-1.30A(300Ω)->390Ω档 1.00A/0.82A/0.411A (单pin) 并注明300Ω档判死(单pin0.534A>任何0.5mm pitch FPC ZIF的0.5A触点天花板); "
        "★口径纠错: 触点天花板必须取 max 列不能取 typ (取typ会把300Ω误判为过) "
        "J_CHG采购口径写死『实物一对』(网表1只逻辑器件 vs 采购2只实物, 以前只有我说才不会被备料漏买一半; 首选FH12-10S-0.5SH(55) 未询价 RFQ草稿待放行) "
        "ISS-049定位孔位定版: 2xM1.2⌀1.4对角分布(5.0,2.5)/(55.0,12.5)+1x⌀2.0H7(15.0,7.50), 与SoC逃线带X[20.20,31.80]零重叠(复算0.000mm²) "
        "PCB_FORM_FACTOR_RECHECK.md §5/§7 作废数字已逐条标注 (grep 净高/改版/37→40 命中7处) "
        "★3条自发现: (a)板重口径单位错(0.48cc体积当重量, 60x15x1.0 6层真值1.67g, 增量+0.56g不是+0.24g) (b)铰链端4条跨铰链连接器54触点=27mm焊盘排>15mm板宽没人算过 "
        "(c)390Ω档余量在电芯侧不在皮肤侧(42.14°C vs 红线43°C 只剩0.86°C, 不能再抬电流) "
        "另发现库内3处仍写300Ω (CHARGE_BOARD_SPEC/netlist P10行484+494/p10_rows.json) 已登记 needs_from 转项目总工统一 "
        "新增3条needs_from + 回答mech-lead 4条 (J_CHG触点额定/FPC厂商三项能力/接触电阻口径/pin数收敛) "
        "未改 netlist_v1.csv gen_netlist.py SCHEMATIC_V1.md BOM_v1.csv MECH/ PROJECT_TRACKER.md DECISIONS.md issue_log.yaml; 未联系任何厂商")
    d["updated_at"] = "2026-10-28T01:10:00+08:00"
    d["updated_by"] = "hw-lead"


update_fragment("hw-lead", mutate)
print("[iss105] ✅ hw.yaml 已原子更新")
