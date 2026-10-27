#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性脚本: 把 2026-10-27 V1.1 原理图增量的 issue 状态落盘 (项目总工自用)
铁律: 改 issue_log.yaml 后必须 safe_load 回读验证 (MEMORY 2026-10-26)"""
import json
import shutil
import yaml

P = "state/issue_log.yaml"
shutil.copy(P, P + ".bak_v11")

d = yaml.safe_load(open(P, encoding="utf-8"))
issues = d["issues"]
items = list(issues.values()) if isinstance(issues, dict) else issues
by_id = {str(i.get("id")): i for i in items}

def app(iid, field, text):
    i = by_id[iid]
    old = (i.get(field) or "").rstrip()
    i[field] = (old + "\n" + text).strip() if old else text

# ---- ISS-074 原理图 V1 → verified (验证人 = hw-lead, 复审在 ISS-088) ----
i = by_id["ISS-074"]
i["status"] = "verified"
i["fix_ref"] = "HW/SCHEMATIC_V1.md"
app("ISS-074", "note",
    "V1.1 增量 (2026-10-27 08:40-09:10, 项目总工): 9 页 (新增 P9 跨铰链页) / netlist 392 行 13 列 / "
    "BOM 295 位号 / 门禁 15→24 条全过 / 生成器幂等 (重跑 3 次 md5 一致)。变更清单见 "
    "HW/SCHEMATIC_V1_1_CHANGELOG.md。★自己撞出并修掉 3 个真缺陷 (USB 差分跨铰链被短接 / 电池 NTC 漏画 / "
    "9 颗供电器件输入侧漏画) + 1 个定位矛盾 (U_BRIDGE P4/P6 说法冲突)。verify_by=hw-lead 的 V1.1 复审在 ISS-088")

# ---- ISS-082 电源域不确定性 → fixed (前提被 TI 官网证据推翻, 改换料不换板) ----
i = by_id["ISS-082"]
i["status"] = "fixed"
i["owner"] = "main"
i["verify_by"] = "hw-lead"
i["fix_ref"] = "HW/SCHEMATIC_V1.md"
app("ISS-082", "note",
    "★前提修正 (2026-10-27): 原单写的『**可编程** TPS7A20 一颗覆盖 1.2-5.5V』**不成立** —— "
    "[官方 ti.com/product/TPS7A20] TPS7A20 只有**固定输出** (30 档 0.8-5.5V) 且 Iout 上限 **300mA** → "
    "覆盖不了 7 条不同电压的轨, 也不该替换 V_CORE/V_SOC_IO (那两条走 3A buck)。改为三步『**换料不换板**』: "
    "① 7 路 LDO 全系列同封装 X2SON → 电压回信后换档位料 ② 2 路 DC-DC 用 TPS62130A 的**引脚可选**输出 "
    "(标称 ±5%) → 落在档内换料, 落在档外换同封装可调型号 (改 2 颗反馈电阻) ③ 新增 U_SUPV 电压监督器, "
    "监督窗口用**分压位**实现 → 任何电压轨都能映射到监控窗口。已画进 P1/P8; BOM 里 7 路 LDO 全是固定档。"
    "★效果比原方案更好: 不需要可编程器件, 也不需要改板")

# ---- ISS-083 显示 TX 公开渠道穷举 → fixed ----
i = by_id["ISS-083"]
i["status"] = "fixed"
i["owner"] = "main"
i["verify_by"] = "hw-lead"
i["fix_ref"] = "HW/SCHEMATIC_V1.md"
app("ISS-083", "note",
    "★穷举完成 (2026-10-27): ① 官网 ARS45 产品页**只字未提显示接口** [官网] ② 官网『智能可穿戴』应用页: "
    "集成 **Display Port 1.4** 与 **USB 3.0** [官网·方案级, 未说 TX/RX 方向] ③ 百度百科: DP1.4 **RX** [媒体] "
    "④ **没有任何官方渠道出现 DSI 字样** → ⇒ 『ARS45 原生带 DSI TX』**至今未证实** ⇒ **双出口互斥 "
    "(R_SEL_* vs BR_*) 必须保留, 桥接芯片 fallback 不能删** (采购周期 4-8 周, 不能等回信) ⑤ 官网确认集成 "
    "USB 3.0 → 但 SS 差分**绝不能跨铰链** ⇒ Type-C 按 16p (USB2+充电) 定, 烧录走 USB 2.0 D+/D−。 "
    "结论已写进 P4 叙述 + U_BRIDGE 定位统一 (P4/P6 同为 DP1.4 TX → MIPI DSI TX 桥接)")

# ---- ISS-086 netlist 收尾 → fixed (项目总工自己动手, verify_by=hw-lead) ----
i = by_id["ISS-086"]
i["status"] = "fixed"
i["owner"] = "main"
i["verify_by"] = "hw-lead"
i["fix_ref"] = "HW/netlist_v1.csv"
app("ISS-086", "note",
    "★2026-10-27 08:40-09:10 项目总工自己动手做完 (owner 改 main / verify_by=hw-lead): "
    "① U_TEMP 定型 **TMP117** (I2C 0x48, ±0.1°C, [官方]) ② USB 跨铰链段加两端 ESD (D_ESD_USB / D_ESD_CAM), "
    "**不装共模扼流圈** (USB2 眼图对共模转差分极敏感, 原单这条要改) ③ U_BRIDGE 定位统一为 "
    "**DP1.4 TX → MIPI DSI TX 桥接** (方案B 专用, redriver 候选兼列)。★额外撞出并修 3 个 V1 真缺陷: "
    "USB 差分**跨铰链被短接** (直连 J_TYPE_C) / **电池 NTC 漏画** (BQ25896 TS 脚, 硬件停充安全项) / "
    "**9 颗供电器件输入侧漏画**; 另新增 P9 跨铰链页 + netlist `board` 板级归属列 + BOM。门禁 15→24 条全过")

# ---- 新单: ISS-088 hw-lead 审 V1.1 + BOM 复核 ----
new = [
    dict(id="ISS-088",
         title="★审原理图 V1.1 (9 页 + 24 条门禁 + BOM 295 位号) —— V1.1 增量由项目总工自产, 验证人必须是 hw-lead",
         severity="high", source_blocker=None, source_agent="main",
         desc="项目总工 2026-10-27 08:40-09:10 自产 V1.1 增量 (新增 P9 跨铰链页 + board 板级归属列 + 补画 4 类漏项 + "
              "修 3 个真缺陷 + BOM 首次生成 + 门禁 15→24 条)。铁律: 自己产的必须别人验 ⇒ 本单请 hw-lead 独立复审, "
              "重点是机械/电气现实 (不是排版): P9 的 4 组跨铰链通道 pin 账与保护件位置、P1 补画的电池 NTC/π 滤波/"
              "输入侧、P8 监督器链、U_BRIDGE 定位、BOM 采购状态分档。",
         owner="hw-lead", reporter="main", raised="2026-10-27", due="2026-10-28", status="open",
         external=False, need_keys=[], task_brief="", fix_ref=None, verify_by="main",
         verify_result=None, verify_date=None, note="2026-10-27 08:50 项目总工派 (V1.1 复审)",
         dispatched_at=None),
    dict(id="ISS-089",
         title="★硬件交叉评审 (机械/热/装配) —— 以 V1.1 的 9 页为输入, 挑出会打回来重画的点",
         severity="high", source_blocker=None, source_agent="main",
         desc="ERC §D2 要求两方交叉评审 (mech-lead 机械/热/装配 + sw-lead 时序/信号/电源时序), V1.1 之前一直没做。"
              "V1.1 新增的 P9 跨铰链页给了结构总工明确的输入 (4 组通道 + pin 账), 正好是交叉评审的抓手。",
         owner="mech-lead", reporter="main", raised="2026-10-27", due="2026-10-29", status="open",
         external=False, need_keys=[], task_brief="", fix_ref=None, verify_by="main",
         verify_result=None, verify_date=None, note="2026-10-27 08:50 项目总工登记 (等 mech-lead 空出写会话)",
         dispatched_at=None),
    dict(id="ISS-090",
         title="★软件侧交叉评审 (时序/信号/电源时序) + TMP117 测点物理位置 + 跨铰链 USB 烧录可行性",
         severity="high", source_blocker=None, source_agent="main",
         desc="ERC §D2 的另一半。V1.1 新增了上电监督链 (2×DC-DC PG + U_SUPV 开漏释放 RESET_N + 分压窗口) 与 "
              "TMP117 数字温度计 → 软件侧必须确认够不够; 且『温度计装在哪个物理点』只有 SW 总工能定。",
         owner="sw-lead", reporter="main", raised="2026-10-27", due="2026-10-29", status="open",
         external=False, need_keys=[], task_brief="", fix_ref=None, verify_by="main",
         verify_result=None, verify_date=None, note="2026-10-27 08:50 项目总工登记 (等 sw-lead 空出写会话)",
         dispatched_at=None),
]
have = {str(x.get("id")) for x in items}
for n in new:
    if n["id"] not in have:
        items.append(n)

d["issues"] = items
with open(P, "w", encoding="utf-8") as f:
    f.write(json.dumps(d, ensure_ascii=False))
# 回读验证
chk = yaml.safe_load(open(P, encoding="utf-8"))
ids = [str(x.get("id")) for x in chk["issues"]]
print("OK 回读成功, issue 总数:", len(ids))
for i in ("ISS-074", "ISS-082", "ISS-083", "ISS-086", "ISS-088", "ISS-089", "ISS-090"):
    e = [x for x in chk["issues"] if str(x.get("id")) == i][0]
    print(f"  {i}: status={e['status']} owner={e['owner']} verify_by={e['verify_by']}")
