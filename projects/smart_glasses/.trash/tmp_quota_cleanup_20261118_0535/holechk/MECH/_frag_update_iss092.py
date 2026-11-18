#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-092 分片更新 (mech-lead 交卷) —— 走 state/frag_write.py 的原子写, 禁 open(p,"w")。

为什么用 Python API 而不是 CLI:
  CLI 的 --add-need 只支持 key/to/item/since, **不支持 waiting_on / due**;
  本单的 needs 需要 due (有明确时限) ⇒ 用 update_fragment() 直改结构, 但**原子写仍由
  frag_write.atomic_write_yaml 负责** (tmp + fsync + os.replace), 与 CLI 走同一条路径。

边界: 只改**自己的**分片 (state/fragments/mech.yaml)。不改 HW/ 与 issue_log.yaml
      (issue_log 走 state/_close_iss092.py 单独原子写)。

用法: python3 MECH/_frag_update_iss092.py [--dry-run]
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

ARTIFACTS = [
    {
        "path": "MECH/SERVICE_PORT_ISS092.md",
        "kind": "spec",
        "version": "1.0",
        "updated_at": "2026-10-30",
        "summary": ("ISS-092 镜脚末端检修口规格书: 开孔位置与尺寸 (外侧面, 开口 10.20x4.60, 必须清空区 7.62x2.54, "
                    "单边间隙 1.29/1.03 最坏 0.99/0.73) + 盖板方案 (磁吸 + 1xM1.6x6 自攻, 盖板 13.20x7.60x1.20, "
                    "内腔 4.90 >= 4.50) + 对镜腿厚度/重量的影响 (H/V/L 三链 Delta=0.00, +0.364 g/侧) + "
                    "IP 影响 (无密封条则 IPx4 不成立, 量产加密封条+迷宫则可达) + 产线可达性 (Cortex-10 标准 pogo, "
                    "夹具基准复用 PIN-SET-2, 装前压针零新增工位) + 与电池/铰链 12 项冲突复核 + 3 条结构硬约束"),
    },
    {
        "path": "MECH/service_port_check.py",
        "kind": "script",
        "version": "1.0",
        "updated_at": "2026-10-30",
        "summary": "ISS-092 自证脚本: rc=0, 54/54 项一致 (H 坐标自洽 / 焊盘阵列与必须清空区 / 开口间隙 / 盖板与螺钉凸台 / "
                   "三条锁死尺寸链 / 重量 / 产线探针与夹具基准 / 冲突间距 / IP 口径 / 末端 V 净高要求)",
    },
    {
        "path": "HANDOFF/2026-10-30_mech-lead_ISS092_镜脚末端检修口.md",
        "kind": "handoff",
        "version": "1.0",
        "updated_at": "2026-10-30",
        "summary": "ISS-092 交接单 B1-B6 六块齐; 12 条结论 (含 4 条不拍板的裁决点) + 16 条验收自评 + 6 项 [0数据] + "
                   "10 条 interface_claims + 7 条 needs + 4 条自登记风险",
    },
    {
        "path": "MECH/_frag_update_iss092.py",
        "kind": "script",
        "version": "1.0",
        "updated_at": "2026-10-30",
        "summary": "ISS-092 分片原子写脚本 (走 state/frag_write.py 的 update_fragment, 支持 needs 的 waiting_on/due)",
    },
]

CLAIMS = [
    {
        "key": "mech_service_port_face",
        "value": "outer",
        "note": ("检修口开在镜脚末端**外侧面** (法向=H, 朝外); 皮肤侧零开孔; **探针与焊盘同轴** 是决定性理由 "
                 "(PCB 平面=LxV, 元件面朝外); 下方为备选 SP-C (探针要侧向压, 市售 pogo 块做不到). "
                 "5 条判据对照见 MECH/SERVICE_PORT_ISS092.md 3.3"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#3.3",
    },
    {
        "key": "mech_service_port_opening_mm",
        "value": "10.20x4.60",
        "note": ("开口(通窗) X x Y (板坐标 X=0 为 PCB 铰链端); **必须清空区 7.62 x 2.54** (按 Cortex-10 座体算, "
                 "不按焊盘算); 位置 X 49.21..59.41 = 镜脚 L 89.71..99.91; 任务书要的 >=7.1x2.7 已满足且有余量"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#3.2",
    },
    {
        "key": "mech_service_port_cover_mm",
        "value": "13.20x7.60x1.20",
        "note": ("盖板 (PA-CF 打印 / 量产 PA-CF+GF 1.0mm 注塑); 搭边 1.50/1.50; 防丢 = 2xN35 磁铁 phi4.0x1.0 + "
                 "1xM1.6x6 自攻螺钉 (旋入 2.40mm = 1.5xd) + 2x phi1.60 定位凸台"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#4.1",
    },
    {
        "key": "mech_service_port_cavity_mm",
        "value": "4.90",
        "note": ("盖板内腔 (镜脚外表面 H7.30 - PCB 元件面 H2.40); ISS-085 硬要求 >=4.50, 余 0.40. "
                 "排针总高 <=3.00mm 时针尖只到 H5.40 => 针不顶盖板, **不需要剪脚**"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#4.1",
    },
    {
        "key": "mech_service_port_clearance_mm",
        "value": "1.29/1.03",
        "note": ("开口单边间隙 X/Y (名义); 最坏 (FDM +/-0.30) 0.99/0.73 >= 判据 0.60 (2x 单边公差)"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#4.1",
    },
    {
        "key": "mech_service_port_weight_g",
        "value": "0.364/侧",
        "note": ("盖板 0.144 + 磁铁 0.094 + M1.6x6 螺钉 0.111 + 凸台 0.015; 整机 +0.73 g = 原型 48.9-72.8 g 的 "
                 "+1.00~+1.49%; 净腔体占用仅 0.013 cc (ISS-085 估的 0.3 cc 偏保守 23x, 因盖板在壁外)"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#5.2",
    },
    {
        "key": "mech_service_port_ip",
        "value": "防汗+IPx4(量产加密封条)",
        "note": ("磁吸+螺钉无密封条 => 搭边缝/螺钉孔/磁铁缝全是通路 => **IPx4 不成立**, 只能宣称防汗; "
                 "量产 PORON 0.50x1.50 (截面 0.75mm2, 压缩 30-50% => 挡 0.2-0.5bar 溅水) + 0.50mm 迷宫搭边 "
                 "=> IPx4 可达, IPx5/x7 浸水不可达; 原型 (FDM 层纹渗漏) 一律不宣称 IP. "
                 "现阶段建议写 '防汗; 量产件按 IPx4 设计 (待认证)'"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#6",
    },
    {
        "key": "mech_j_debug_conn",
        "value": "2x5@1.27 Cortex-10",
        "note": ("J_DEBUG 改标准 2x5@1.27 Cortex-10 **焊盘阵列** (D-1: 默认不装座体, 产线 pogo 压接); "
                 "J_UART 保持 1x2@1.27 但 **座体 DNP 只留焊盘** (座体下沿会掉到开口下沿之外); "
                 "阵列坐标 J_DEBUG X 50.50..55.58 / Y 9.50..10.77, J_UART X 56.85..58.12 / Y 9.50"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#7.1",
    },
    {
        "key": "mech_service_port_fixture_depth_mm",
        "value": ">=5.90",
        "note": ("产线 pogo 探针可伸入深度要求 = 净空 4.90 (H7.30->H2.40) + 工作行程 1.00; "
                 "市售 pogo 伸出 typ. 6-11mm 够; 净开口 10.20x4.60 容得下 2x5 探针阵列 (需 7.08x3.27)"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#7.2",
    },
    {
        "key": "mech_service_port_fixture_datum",
        "value": "PIN-SET-2 P2+S2",
        "note": ("夹具基准**复用 PCB 的** PIN-SET-2 (P2 phi2.0 H7 @板坐标 X52.00/Y7.50 + S2 phi1.4 @X52.00/Y12.50), "
                 "**不新增夹具基准孔**; P2 孔壁到焊盘阵列最近 1.00mm, S2 孔壁 1.03mm; "
                 "焊盘共面 <=0.05mm 由 ISS-049 定位链 (骨架 <=5um + H7 销 <=0.010 => 重复性 0.046mm) 保证 => 可达"),
        "ref": "MECH/SERVICE_PORT_ISS092.md#7.2",
    },
]

NEEDS = [
    {
        "key": "iss092_jdebug_cortex10_netlist",
        "to": "hw-lead",
        "item": "ISS-092: J_DEBUG 改 2x5@1.27 Cortex-10 焊盘阵列 (座体 DNP) 的网表与 footprint (焊盘尺寸/间距/引脚序) + J_UART 1x2 是否并入同一阵列",
        "waiting_on": "agent",
        "due": "2026-11-01",
        "since": "2026-10-30",
    },
    {
        "key": "iss092_service_port_face_decision",
        "to": "main",
        "item": "ISS-092: 检修口形态裁决 (外侧面 推荐 / 下方 备选 SP-C) + 是否接受 +0.73 g 整机",
        "waiting_on": "agent",
        "due": "2026-10-31",
        "since": "2026-10-30",
    },
    {
        "key": "iss092_probe_before_cover_decision",
        "to": "main",
        "item": "ISS-092: 产线采不采纳 '装前压针' (零新增工位 + 盖板可实心); 若装盖板压针则须开让位窗 6.40x3.90 且接受防汗降级",
        "waiting_on": "agent",
        "due": "2026-10-31",
        "since": "2026-10-30",
    },
    {
        "key": "iss092_ip_wording_decision",
        "to": "main",
        "item": "ISS-092: 规格书写不写 'IPx4' (建议 '防汗; 量产件按 IPx4 设计 待认证') —— 开孔后 IPx4 成立的唯一前提是量产加密封条+迷宫搭边",
        "waiting_on": "agent",
        "due": "2026-10-31",
        "since": "2026-10-30",
    },
    {
        "key": "iss092_mic_magnetic_sensitivity",
        "to": "hw-lead",
        "item": "ISS-092: MEMS 麦克风型号与磁场敏感度 (确认镜脚末端 N35 磁铁 phi4.0 在 40mm 外无影响)",
        "waiting_on": "agent",
        "due": "2026-11-02",
        "since": "2026-10-30",
    },
    {
        "key": "iss092_outer_face_holes_position",
        "to": "hw-lead",
        "item": "ISS-092: 麦克风声孔 phi1.0 与导光孔 (ISS-065 R2 改开镜脚外侧) 在镜脚外侧的实际位置 (确认与检修口通窗间距 >=40mm)",
        "waiting_on": "agent",
        "due": "2026-11-02",
        "since": "2026-10-30",
    },
    {
        "key": "iss092_print_pack_rev",
        "to": "main",
        "item": "ISS-092: 打印包改版 (新增通窗/螺钉凸台/磁铁沉槽/定位凸台/盖板件) 排进 ISS-027 哪一批 (建议 B2 镜脚装配验证批)",
        "waiting_on": "agent",
        "due": "2026-10-31",
        "since": "2026-10-30",
    },
]

RISKS = [
    {
        "id": "R-mech-service-port-tip-v",
        "text": ("镜脚末端外侧面 V 净高未定义 [0数据] (镜腿是上宽下窄锥形) => 开口 4.60 + 两侧 1.25 = 需要 7.10mm; "
                 "若不满足只能开口往根部挪或启备选 SP-C (下方开孔)"),
        "severity": "medium",
    },
    {
        "id": "R-mech-service-port-magnet",
        "text": ("检修口磁吸用 N35 钕铁硼, 对 MEMS 麦克风的磁场影响未验 [0数据] (麦克风磁场敏感度项目里没有); "
                 "间距 >=40mm 大概率无碍, 但磁铁牌号应选低矫顽力或改弹性卡扣"),
        "severity": "medium",
    },
    {
        "id": "R-mech-service-port-coplanarity",
        "text": ("产线 pogo 压 10 针焊盘的共面度 <=0.05mm 依赖 PIN-SET-2 定位链 (重复性 0.046mm); "
                 "若骨架/PCB 装配超差会出现 1-2 针压不到 => 选自浮动 pogo + 夹具加 0.05mm 通止规自检"),
        "severity": "medium",
    },
    {
        "id": "R-mech-service-port-seam",
        "text": ("磁吸+自攻螺钉若**无密封条**, 搭边缝/螺钉孔/磁铁缝全是水路 => **IPx4 不成立** (只能宣称防汗); "
                 "量产必须加 PORON 0.50x1.50 密封条 + 0.50mm 迷宫搭边, 且 IPx5/x7 浸水仍不可达"),
        "severity": "low",
    },
]

STATUS = {
    "phase": ("P2(ISS-092 镜脚末端检修口规格书已交: 开孔/盖板/厚度重量/IP/产线/冲突复核 六问全答 + "
              "尺寸链表 + 3 条结构硬约束; 待 PM 裁形态与是否接受重量代价)"),
    "progress_pct": 88,
    "health": "yellow",
    "summary": (
        "第9轮 ISS-092: 新增 MECH/SERVICE_PORT_ISS092.md (镜脚末端检修口规格书, 尺寸表 C-1~C-15) + "
        "MECH/service_port_check.py (rc=0, 54/54 项一致) + "
        "HANDOFF/2026-10-30_mech-lead_ISS092_镜脚末端检修口.md (B1-B6 六块齐) + "
        "MECH/USB_HINGE_STRUCTURE.md 6.1/7/8-U-6 补交叉引用与修正 (腔体占用 0.3cc -> 0.013cc, 重量 +0.73g)。"
        "核心结论: (1) **位置=镜脚末端外侧面** (不是下方) —— 决定性理由是**探针与焊盘同轴** (PCB 平面=LxV, 元件面朝外), "
        "下方开孔则探针要侧向压, 市售 pogo 块做不到; (2) **开口 10.20x4.60** (任务书 >=7.1x2.7 已满足), "
        "必须清空区 7.62x2.54 (按 Cortex-10 座体算不按焊盘算), 单边间隙 1.29/1.03 最坏 0.99/0.73 >= 判据 0.60; "
        "(3) **盖板 13.20x7.60x1.20** = 磁吸(2x N35 phi4.0x1.0) + 1xM1.6x6 自攻 (旋入 2.40mm=1.5xd) + 2x phi1.60 定位凸台, "
        "**盖板内腔 4.90 >= 4.50 硬要求 (余 0.40)**, 排针总高 <=3.00 时针不顶盖板 **不需剪脚**; "
        "(4) ★**镜腿厚度 7.3mm / 净高 38 / 内长 130 三条锁死尺寸链 Delta=0.00** (开窗只挖外壁 0.8 一层, "
        "螺钉凸台落进 PCB 段本空着的 3.10mm 空腔, 盖板坐在壁外) => ISS-065 '7.3mm 一毫米不用改' 继续成立; "
        "重量 **+0.364 g/侧 (整机 +0.73 g, +1.0~1.5%)**, 净腔体占用 **0.013 cc** (ISS-085 估的 0.3cc 偏保守 23x); "
        "(5) ★**IP: 开孔不必然降级 IPx4, 但磁吸+螺钉无密封条 => IPx4 不成立** (只能宣称防汗), 量产加 PORON 0.5x1.5 "
        "+ 0.5mm 迷宫 => IPx4 可达/浸水不可达, 原型 FDM 一律不宣称 IP, 建议规格书写 '防汗; 量产件按 IPx4 设计 (待认证)'; "
        "(6) ★**产线: J_DEBUG 改 2x5@1.27 Cortex-10 焊盘阵列 (D-1 不装座体) + 装前压针** => 市售 ARM CoreSight 10-pin "
        "pogo 现成可用, **夹具基准复用 PIN-SET-2 的 P2+S2 (不新增基准孔)**, 重复性 0.046 <= 焊盘共面 0.05, "
        "探针需可伸入 >=5.90mm (净空 4.90+行程 1.00), **零新增工位**; (7) **与电池/铰链 12 项零冲突** "
        "(电芯间距 49.21mm / 铰链 74.71mm / 骨架 7.21mm) + 3 条结构硬约束 (骨架 X>=45 停 / 末端 V 净高 >=7.10mm / "
        "PCB 末端 10mm 内不布 >2.54mm 器件); (8) ★**顺手清两条陈旧口径**: MECH_BUDGET 5.2 '充电孔 镜腿末端开 Type-C 孔' 与 "
        "5.6.3 '镜脚·尾端 尾端截面宽 12.50' 已随 ISS-014 决策 5 作废但还在表里, 已在 9 节列 8 条施工单; "
        "(9) ★**诚实边界**: 实物 [实测]=0 条, **6 项 [0数据]** (末端 V 净高 / 座体型号与焊盘 / 磁铁拉脱力 / "
        "麦克风磁场敏感度 / 螺钉扭矩与塑料螺纹寿命 / IP 实测), **不拍板** —— 形态/重量/装前压针/IP 措辞 4 条裁决点 "
        "已登记 needs (I-1~I-7 经项目总工)。未联系任何供应商/原厂, 未改 HW/ 与 PROJECT_TRACKER.md 与 DECISIONS.md。"
    ),
}


def main() -> int:
    dry = "--dry-run" in sys.argv

    def mutate(d: dict):
        arts = d.setdefault("artifacts", [])
        have = {a.get("path") for a in arts if isinstance(a, dict)}
        for a in ARTIFACTS:
            if a["path"] not in have:
                arts.append(dict(a))
        claims = d.setdefault("interface_claims", [])
        ckeys = {c.get("key") for c in claims if isinstance(c, dict)}
        for c in CLAIMS:
            if c["key"] not in ckeys:
                claims.append(dict(c))
        needs = d.setdefault("needs_from", [])
        nkeys = {n.get("key") for n in needs if isinstance(n, dict)}
        for n in NEEDS:
            if n["key"] not in nkeys:
                needs.append(dict(n))
        risks = d.setdefault("risks", [])
        rids = {r.get("id") for r in risks if isinstance(r, dict)}
        for r in RISKS:
            if r["id"] not in rids:
                risks.append(dict(r))
        d["updated_at"] = "2026-10-30T00:20:00+08:00"
        d["updated_by"] = "mech-lead"
        d["status"] = dict(STATUS)

    if dry:
        from frag_write import load_fragment
        d = load_fragment("mech-lead")
        print("[dry-run] 将写入:")
        print(f"  artifacts +{len(ARTIFACTS)} / claims +{len(CLAIMS)} / needs +{len(NEEDS)} / risks +{len(RISKS)}")
        return 0

    d = update_fragment("mech-lead", mutate)
    print("✅ mech.yaml 已原子更新 "
          f"(artifacts={len(d.get('artifacts') or [])} claims={len(d.get('interface_claims') or [])} "
          f"needs={len(d.get('needs_from') or [])} risks={len(d.get('risks') or [])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
