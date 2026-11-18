#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-092 状态推进: fixing -> fixed (并落 fix_ref) —— mech-lead 交卷后自推。

★为什么要自己推 (不能只交卷): `state/advance.py` 的 in_flight 规则 = "同一 agent 名下只要有
  status==fixing 的 issue, 该 agent 本轮就不再派新活" ⇒ ISS-092 一直卡在 fixing, mech-lead 名下
  10 条 open 待办全被挡住。**交卷 ≠ 状态推进**, 必须一起做。

★写文件铁律: 原子写 (tmp + fsync + os.replace), 禁止 open(p,"w") 覆盖 issue_log.yaml。

用法: python3 state/_close_iss092.py [--dry-run]
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

FIX_REF = (
    "MECH/SERVICE_PORT_ISS092.md (镜脚末端检修口规格书: 开孔位置与尺寸 + 盖板方案 + 对镜腿厚度/重量的影响 + "
    "对 IP 防护等级的影响 + 产线可达性 + 与电池/铰链的结构冲突复核; 尺寸表 C-1~C-15 + H/V/L 三方向尺寸链/公差表 "
    "+ 12 项冲突复核 + 3 条结构硬约束 S-1~S-3 + 6 项 [0数据] 诚实边界) + "
    "MECH/service_port_check.py (自证脚本, rc=0, 54/54 项一致) + "
    "HANDOFF/2026-10-30_mech-lead_ISS092_镜脚末端检修口.md (B1-B6 六块齐) + "
    "MECH/USB_HINGE_STRUCTURE.md §6.1/§7/§8 U-6 (补交叉引用 + 修正腔体占用 0.3cc -> 0.013cc / 重量 +0.73g) + "
    "MECH/_frag_update_iss092.py (分片原子写, 走 state/frag_write.py 的 update_fragment) + "
    "state/_close_iss092.py (本脚本, issue_log 原子写 tmp+fsync+os.replace) + "
    "state/fragments/mech.yaml (interface_claims 新增 10 条: mech_service_port_face / _opening_mm / _cover_mm / "
    "_cavity_mm / _clearance_mm / _weight_g / _ip / _fixture_depth_mm / _fixture_datum + mech_j_debug_conn; "
    "needs_from 新增 7 条 (iss092_* 经项目总工); risks 新增 4 条)"
)

CLOSE_NOTE = (
    "★2026-10-30 00:2x mech-lead 交卷并自推状态 (owner=mech-lead)。\n"
    "【本单做了什么】① 出 MECH/SERVICE_PORT_ISS092.md —— ISS-085 §6.1 那条 "
    "'J_DEBUG/J_UART 位置不冲突但**够不着** ⇒ 镜脚封闭 = 排针装上也用不了' 的结构收口; "
    "② 出 MECH/service_port_check.py (rc=0, 54/54 项一致) 把本件全部数字做成可机械复算的判定; "
    "③ 出 HANDOFF/2026-10-30_mech-lead_ISS092_镜脚末端检修口.md (B1-B6 六块齐); "
    "④ MECH/USB_HINGE_STRUCTURE.md §6.1/§7/§8-U-6 补交叉引用并修正两处旧数 (腔体占用 0.3cc -> 0.013cc, 重量 +0.73g); "
    "⑤ 分片走 state/frag_write.py 原子写 (10 条新 interface_claims + 7 条 needs + 4 条 risks); "
    "⑥ 本脚本把 ISS-092 推到 fixed 并落 fix_ref。\n"
    "★【六问的答案 (摘要)】① **开孔位置 = 镜脚末端外侧面** (不是下方) —— 决定性理由是**探针与焊盘同轴**: "
    "主 PCB 平面 = L×V、元件面朝外 ⇒ 焊盘法向 = H ⇒ 开在外侧面时 pogo 探针垂直下压即可; 开在下方则探针要**侧向**压针, "
    "市售 pogo 块做不到 (下方另留 2 条硬伤: H 向只剩 7.30 总厚 ⇒ 两侧各剩 1.35mm 筋; 下壳贴皮肤, 承力面被切断)。"
    "**开口 10.20 (X) × 4.60 (Y)**, 位置板坐标 X 49.21..59.41 (= 镜脚 L 89.71..99.91); 必须清空区 **7.62 × 2.54** "
    "(按 Cortex-10 **座体**算不按焊盘算, 否则将来装座体装不进); 单边间隙 **1.29 / 1.03**, 最坏 (FDM ±0.30) "
    "**0.99 / 0.73** ≥ 判据 0.60 ⇒ 任务书要的 ≥7.1×2.7 满足且有余量。② **盖板 = 磁吸 + 自攻螺钉防丢**: "
    "盖板 **13.20 × 7.60 × 1.20** (搭边 1.50/1.50) + 2×N35 钕铁硼 ⌀4.0×1.0 磁吸 + **1×M1.6×6 自攻螺钉** "
    "(旋入 2.40mm = 1.5×d, 螺钉柱 ⌀3.20 向内加厚 1.60) + 2×⌀1.60 定位凸台 (磁吸不承定位); "
    "**盖板内腔 = 4.90mm** (镜脚外表面 H7.30 − PCB 元件面 H2.40) **≥ ISS-085 的 4.50 硬要求 (余 0.40)**; "
    "排针总高 ≤3.00 时针尖只到 H5.40 ⇒ **针不顶盖板, 不需要剪脚**; 若选'装盖板压针'则盖板中央需让位窗 6.40×3.90。"
    "③ **对镜腿厚度/重量的影响**: ★**H 7.30 / V 38.00 / L 130.00 三条锁死尺寸链 Delta = 0.00** —— 开窗只挖外壁 0.8 厚"
    "的一层 (不改外包络), 螺钉凸台向内加厚落进 **PCB 段本来就空着的 3.10mm 空腔** (H 3.40..6.50, 不吃 H 链 —— H 链"
    "控制段是电池段 6.35 不是 PCB 段 4.20), 盖板坐在外表面向外凸 1.20 (完全不进腔体) ⇒ '镜腿厚度 7.3mm 一毫米不用改'"
    " (ISS-065 B1-2) **继续成立**; 重量 **+0.364 g/侧 (整机 +0.73 g = 原型 48.9-72.8 g 的 +1.00~+1.49%)**; "
    "**净腔体占用 0.013 cc** (ISS-085 §7 估的 ≈0.3 cc **偏保守 23×**, 因为盖板在壁外不占腔), "
    "ISS-085 的重量估 '+0.5~+0.8 g' 与本单 +0.73 g 一致。④ **对 IP 的影响**: ★**开孔本身不必然降级 IPx4, "
    "降级与否取决于盖板密封形式** —— 磁吸+自攻螺钉**无密封条 ⇒ 搭边缝 + 螺钉孔 + 磁铁缝全是通路 ⇒ IPx4 不成立** "
    "(只能宣称防汗); 量产加 PORON 密封条 0.50×1.50 (截面 0.75mm², 压缩 30-50% ⇒ 挡 0.2-0.5 bar 溅水) + 0.50mm "
    "迷宫搭边 ⇒ **IPx4 可达, IPx5/x7 浸水不可达**; **原型是 FDM 打印, 层纹本身就是渗漏路径 ⇒ 原型一律不宣称 IP** "
    "(本项目 IP 口径本就 0 处, FRAMEWORK_SCOPE H5-04 已把 IP 推迟到量产) ⇒ 建议规格书写 "
    "'**防汗; 量产件按 IPx4 设计 (待认证)**', 现阶段**不要**把 IPx4 三个字写进规格书。⑤ **产线可达性**: "
    "J_DEBUG 改 **2×5@1.27 Cortex-10 焊盘阵列** (D-1 默认不装座体) ⇒ 市售 **ARM CoreSight 10-pin 1.27mm pogo "
    "探针块现成可用** (不用定制夹具); **夹具基准直接复用 PCB 的 PIN-SET-2** (P2 ⌀2.0 H7 @板坐标 X52.00/Y7.50 + "
    "S2 ⌀1.4) ⇒ **不新增夹具基准孔**, P2 孔壁到焊盘阵列最近 1.00mm; 焊盘共面 ≤0.05mm 由 ISS-049 定位链保证 "
    "(骨架铣削面 ≤5µm + H7 销 ≤0.010 ⇒ 重复性 **0.046mm**) ⇒ 可达; 探针可伸入深度需求 **≥5.90mm** "
    "(净空 4.90 + 工作行程 1.00, 市售 pogo 伸出 typ. 6-11mm 够); ★**「装前压针」是本单给产线的关键建议** —— "
    "盖板最后装 ⇒ 最终盖板可以是**实心的** (防汗/防尘最好) 且 **零新增工位** (不需要治具盖板来回换)。"
    "⑥ **与电池/铰链的结构冲突复核 = 12 项全部无冲突**: 电芯 L 0..40.5 / 铰链区 L 0..15 / 开口 L 89.71..99.91 ⇒ "
    "与电芯末端间距 **49.21mm** (≥ ISS-085 D-3 的 2mm 缓冲要求)、与铰链 **74.71mm**、与金属骨架末端 7.21mm; "
    "**唯一的真冲突是'骨架若延伸到 PCB 末端'** ⇒ 由此产生 3 条结构硬约束: **S-1** 骨架在 X ≥ 45 必须停止或绕开"
    "螺钉凸台 (定位链不能被凸台改变)、**S-2** 镜脚末端外侧面 V 净高必须 ≥ 7.10mm、**S-3** PCB 末端 X 50.0..60.0 段"
    "不得布 2.54mm 以上器件/凸起。\n"
    "★【顺手清两条陈旧口径 (给 PM 的施工单, 本单未改)】`MECH/MECH_BUDGET.md` §5.2 的 "
    "'充电孔 | 镜腿末端开 Type-C 孔' 与 §5.6.3 的 '镜脚·尾端 尾端截面宽 (开口9.5+两侧1.5) = 12.50' **两行已随 "
    "ISS-014 决策 5 (充电板挪镜框) 作废但还在表里** ⇒ 结构侧会误以为镜脚末端已有开孔要避让; 交接单 §9 另列了 8 条改动清单。\n"
    "【验收依据 (交卷自评 + 可复现)】实跑 python3 MECH/service_port_check.py → **rc=0, 54/54 项一致, FAIL 0**; "
    "实跑 python3 state/merge.py → **rc=0, 冲突 0** (本单新增 10 条 interface_claims 未与任何方冲突); "
    "实跑 python3 state/gate_check.py → **Q1 18/18** (mech-lead 6/6, 交接单 2026-10-30_mech-lead_ISS092_镜脚末端检修口.md), "
    "Q2 3/3 证据分级, Q5 mech-lead 5/5 硬指标; 实跑 python3 MECH/_frag_update_iss092.py → 分片原子写成功。\n"
    "【诚实边界】实物 [实测] = **0 条** (0 件打印 / 0 台样机 / 0 个实测温度/IP/磁力)。**6 项 [0数据]**: "
    "① 镜脚末端 V 净高 (未定义 ⇒ 本文给的是要求 S-2 不是断言, 很可能被这条打回) ② J_DEBUG 座体型号与焊盘尺寸 "
    "③ 磁铁拉脱力/牌号 ④ MEMS 麦克风磁场敏感度 (本单**新发现**的风险) ⑤ 自攻螺钉扭矩与塑料螺纹寿命 "
    "⑥ IP 实测 (原型 FDM 本就不可测)。**本单未拍板**: 形态 (外侧面 vs 下方) / 是否接受 +0.73 g / 采不采纳'装前压针' / "
    "规格书写不写 IPx4 —— 这 4 条裁决点与 3 条硬件请求 (I-1~I-7) 全部登记 needs 经项目总工转达, "
    "**未直接联系任何总工或供应商**, 未改 HW/ 与 PROJECT_TRACKER.md 与 DECISIONS.md, 未碰 MECH/print/ 与任何 STL。"
)


def main() -> int:
    dry = "--dry-run" in sys.argv
    with open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc.get("issues")
    items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])

    hit = 0
    for it in items:
        if not isinstance(it, dict) or it.get("id") != "ISS-092":
            continue
        hit += 1
        print(f"[before] ISS-092 status={it.get('status')!r} fix_ref={it.get('fix_ref')!r}")
        it["status"] = "fixed"
        it["fix_ref"] = FIX_REF
        note = str(it.get("note") or "")
        if "ISS-092 交卷" not in note:
            it["note"] = note + "\n\n" + CLOSE_NOTE
        print(f"[after ] ISS-092 status='fixed' fix_ref 已落 ({len(FIX_REF)} B)")

    if hit != 1:
        print(f"❌ 找到 {hit} 条 ISS-092 (应为 1) —— 中止, 不落盘")
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
    print("✅ issue_log.yaml 已原子更新 (ISS-092 fixing → fixed, fix_ref 已落)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
