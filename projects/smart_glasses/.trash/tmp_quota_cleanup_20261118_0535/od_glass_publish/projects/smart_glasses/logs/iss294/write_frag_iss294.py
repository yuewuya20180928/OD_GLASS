#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""write_frag_iss294.py —— ISS-294 分片写入 (★走 state/frag_write.py 的原子写 API★)

纪律: 禁止 open(p, "w") 直写分片; 只写 mech-lead 自己的分片 (state/fragments/mech.yaml);
      不碰 hw.yaml / sw.yaml / pm.yaml。
"""
from __future__ import annotations

import os
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment          # noqa: E402  ★原子写 (tmp + os.replace)★

HANDOFF = "HANDOFF/2026-11-17_mech-lead_ISS294_USBC边开口规格补缺.md"

NEW_NEED = (
    "★ISS-294 · `J_USB_C` 结构边开口规格已补 (E-6 的 MECH 半边) ⇒ 本单只交【几何 + 代价 + 建议】, "
    "★**开口尺寸归 main→boss 拍**★。★**事实 (板读 + 自算, 帧 B160x100)**★: `J_USB_C` 座体 `F.Fab` "
    "X 135.680..144.320 × Y 0.000..6.400 ⇒ Y 下沿 = 0.000 = 板边; `F.CrtYd` X 135.180..144.820 × "
    "Y −0.500..6.900; 两个壳体固定孔 NPTH @ (134.220, 2.625) / (145.780, 2.625), pad Ø0.650 / "
    "drill Ø0.762 ⇒ 孔外缘 X 133.895..146.105 (drill 口径 133.839..146.161)。"
    "★**边开口 (板边缺口, 另一侧是板外 ⇒ 插头从板边进出) = X 132.995..147.005 × Y 0.000..7.300 "
    "(宽 14.010, 深 7.300); 必须清空区 = 座体 `F.Fab` ∪ 两个固定孔外缘 = X 133.895..146.105 × "
    "Y 0.000..6.400; 单边净距 X 0.900 / Y 0.900 ⇒ 最坏 0.600 = CRIT 刚好过; 到 drill 外缘的净距 "
    "0.844 ≥ CRIT; 该开口矩形内除 `J_USB_C` 外无别的封装; S6 的 20 个目标落位压它 0 条, 最小净距 "
    "8.795**★。★**要拍的四条**★: ① 缺口 X 取最小合法值 (132.995..147.005) 还是按立柱/螺钉头外扩 "
    "(D=2.60 ⇒ 132.020..147.980 / D=3.00 ⇒ 131.820..148.180 / D=3.80 ⇒ 131.420..148.580; "
    "代价 = 每侧多让约 1 mm ⇒ 结构件这条边少一条 14 × 2 mm 的承力带) ② 缺口 Y 向深度 7.300 是按"
    "【结构件内壁与板边齐平】的最坏假设算的 (内壁外移 t ⇒ 深度可缩到 t) ③ ★**Z 向窗口 (插头过孔净空高) "
    "= `OPEN_Y_eff(h)` = 4.60 / 4.60 / 5.80 不在板面坐标里, 本页只能登记不能验 ⇒ 必须跟结构件外形"
    "一起定**★ ④ 要不要让 hw-lead 把第三条开口 (X 132.995..147.005 @ 板边 Y=0) 抄进作业包 §3-S6 "
    "(零改板 ⇒ 可以放在「板只改一次」那一趟之后, 但必须在结构件开模前定)。"
    "★**座体真实高 h 仍是 `[0数据]` (BOM 同族件 `J_TYPE_C` 记 3.50 mm [实测 BOM 行 76]; GCT USB4105 "
    "图纸文本含 3.31 / 3.50 两个高度数, 未看图不能判定哪个是座高) ⇒ 三档 0.90/2.54/4.00 覆盖它**★"
)

DIVERGENCE_NEED = (
    "★口径分叉 (ISS-294 发现, 归 main 裁决): `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §4 的 "
    "`J_USB_C` 行 verdict 仍写「可装 / 结构侧缺一条边开口规格」—— ★**那是 ISS-290 的交卷物, 本单"
    "一个字节不许动**★ ⇒ 本单已把 `MECH/BOARD_ONEPASS_MECH_SYNC.md` §10.1 那行改成「可装 / 边开口"
    "规格已补 (X 132.995..147.005 @ 板边 Y=0 · h 三档 · 固定孔清空区 X 133.895..146.105)」"
    "⇒ 两页同一件事两种说法 ⇒ 要不要让 ISS-290 那行补一句「已由 ISS-294 补」, 归 main**★"
)

TRANSFER_MARK = (
    "【已转出 · 2026-11-17 · main 16:0x 已转 hw-lead 的 ISS-292 任务书「⑬ 追加」节 · pm.yaml 已"
    "回写答案 ⇒ 本条不再由 mech-lead 追; 其中 E-1~E-5 归 hw-lead 的 ISS-292, ★**E-6 的 MECH 半边"
    "已由 ISS-294 (mech-lead) 接手并交卷**★】"
)

ARTIFACTS = [
    {
        "path": HANDOFF,
        "kind": "handoff",
        "version": "iss294",
        "updated_at": "2026-11-17",
        "summary": ("ISS-294 交卷单: `J_USB_C` 结构边开口规格补缺 (E-6 的 MECH 半边) —— "
                    "B1 规格页补第三条开口 `PORT_OPEN_USBC` (板边缺口 X 132.995..147.005 × "
                    "Y 0.000..7.300 + 必须清空区 X 133.895..146.105 × Y 0.000..6.400 + h 三档 "
                    "0.90/2.54/4.00) / B2 两道闸改成【期望 id 集合 + 任意两条矩形不许完全相同】"
                    "(合并禁令不但没松, 还多一条「不许把 USB-C 并进检修口/调试口」) / B3 回归 9 条"
                    "命令全 rc=0 + 板 md5+mtime 双重自证 / 反向用例 8 条 (两道闸各 4 条新增, "
                    "沙盒副本上跑) 全抓到"),
    },
    {
        "path": "MECH/BOARD_ONEPASS_MECH_SYNC.md",
        "kind": "spec",
        "version": "iss294-append",
        "updated_at": "2026-11-17",
        "summary": ("ISS-294 追加式: §5 机器块 `openings[]` 加第三条 `PORT_OPEN_USBC` (15 个标准字段"
                    "一条不缺 + `tiers` h 三档) / §2.1 逐条表加 `MECH-PORT-USBC` 8 字段行 / "
                    "§10.1 三方对照摘要 `J_USB_C` 行 verdict 改成「可装 / 边开口规格已补」 / "
                    "§3.1 §3.4 给 hw-lead 的输入加第三条 / 新增 §11.1~§11.7 (边开口与另两条的语义"
                    "差别 · 几何自算 · h 三档 · 立柱/螺钉头外扩三档 · 归 main 拍的 4 条 · 两闸改了什么"
                    "· 边界)。★**另两条开口 / `merged_opening` / `consts` / 老 items[] 一个字没改**★"),
    },
    {
        "path": "MECH/check_onepass_mech_sync.py",
        "kind": "script",
        "version": "iss294",
        "updated_at": "2026-11-17",
        "summary": ("M2 改成【期望 id 集合断言 = {DEBUG, UART, USBC}】(★不是把 `!= 2` 改成 `!= 3`★) "
                    "+ M2b 改成【任意两条矩形不许完全相同】+ M2c 合并缺口复算只取 "
                    "`merged_opening.covers` 点名的两条 (★不然第三条会把「恰好两条」的判据悄悄跳过★) "
                    "+ M3 新增【边开口分支】(下沿必须锚板边 + X = 座体∪固定孔 ± (CRIT+TOL) + "
                    "Y 深度 = max(座体 Y 深度, OPEN_Y_eff(h)) + (CRIT+TOL), 逐档验) + 自检新增 4 条"
                    "反向用例 (删第三条 / 改 id / 并进调试口 / 正向对照) + ★**修掉一条既有回归**★ "
                    "(ISS-286 把 `CFC.PROTECTED` 改成 2 件 ⇒ 沙盒里没有 HW/BOM_v1.csv ⇒ 自检第 ⑦ 条"
                    "直接崩; 改成篡改 M5 真正查的板文件, 语义不变)。主跑 rc=0, --selftest rc=0"),
    },
    {
        "path": "MECH/check_onepass_struct_crosscheck.py",
        "kind": "script",
        "version": "iss294",
        "updated_at": "2026-11-17",
        "summary": ("N3 改成【期望 id 集合断言 = 三条】(读 ISS-290 页的两条 + MECH_SYNC 页的第三条; "
                    "★ISS-290 那页一个字节不许动★) + 【任意两条矩形不许完全相同】+ 三条逐档分别验 "
                    "(第三条逐档进循环, 输出里可见「第三条逐档核 60 次」) + 新增 N3b 两页老开口必须"
                    "逐字一致 / N3b2 机器块内部 rect 与 h_ref 档不许分叉; N4 必清空区 2 ⇒ 3 "
                    "(加 `MC_USBC`)。★**ISS-290 的 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 一个字节"
                    "没动**★。主跑 rc=0, --selftest rc=0 (12 条反向用例)"),
    },
    {
        "path": "logs/iss294/compute_iss294.py",
        "kind": "compute",
        "version": "iss294",
        "updated_at": "2026-11-17",
        "summary": ("★**本单几何自算脚本**★ (只读 import 两个既有闸 + 自写板解析) ⇒ 产出 "
                    "`logs/iss294/compute_iss294.json`: `J_USB_C` 的 `F.Fab` / `F.CrtYd` / 焊盘 / "
                    "NPTH(drill) 实测 + 必须清空区三口径 + 边开口矩形 + 净距 + 立柱外扩三档 + "
                    "邻件冲突扫描 + S6 20 个目标落位净距"),
    },
]

STATUS_SUMMARY = (
    "★ISS-294 `J_USB_C` 结构边开口规格补缺 (E-6 的 MECH 半边) 交付: MECH/BOARD_ONEPASS_MECH_SYNC.md "
    "追加式补第三条开口 `PORT_OPEN_USBC` (板边缺口 X 132.995..147.005 × Y 0.000..7.300 · 必须清空区 "
    "X 133.895..146.105 × Y 0.000..6.400 · h 三档 0.90/2.54/4.00) + 两道闸改成【期望 id 集合 + "
    "任意两条矩形不许完全相同】(合并禁令不但没松还多一条) + 反向用例各 4 条全抓到 + 回归 9 条命令全 "
    "rc=0 + 板 md5/mtime 双重自证 ⇒ 零写板/零落表/零改 HW/·SW//零改既有 MECH 判据脚本/零外发/不自签 "
    "issue_log; ★**结构开口尺寸 / 立柱外径 / Z 向窗口归 main→boss, 本单只交几何 + 代价 + 建议**★"
)


def mutate(d: dict) -> None:
    # 1) ISS-290 留在本分片的那条 need: 标【已转出】(★不关它, 只写清依据★)
    for n in d.get("needs_from") or []:
        if n.get("key") == "iss290_onpass_must_change_list_to_hw":
            if not str(n.get("item", "")).startswith("【已转出"):
                n["item"] = TRANSFER_MARK + " " + str(n.get("item", ""))
            break

    # 2) 新 need ×2 (归 main)
    needs = d.setdefault("needs_from", [])
    keys = {n.get("key") for n in needs}
    if "iss294_usbc_edge_opening_size_and_z_window" not in keys:
        needs.append({"key": "iss294_usbc_edge_opening_size_and_z_window", "to": "main",
                      "item": NEW_NEED, "since": "2026-11-17"})
    if "iss294_iss290_page_verdict_divergence" not in keys:
        needs.append({"key": "iss294_iss290_page_verdict_divergence", "to": "main",
                      "item": DIVERGENCE_NEED, "since": "2026-11-17"})

    # 3) artifacts
    arts = d.setdefault("artifacts", [])
    have = {a.get("path") for a in arts}
    for a in ARTIFACTS:
        if a["path"] not in have:
            arts.append(dict(a))

    # 4) status (追加式, 不覆盖历史口径)
    st = d.setdefault("status", {})
    old_sum = str(st.get("summary") or "")
    if "ISS-294" not in old_sum:
        st["summary"] = (old_sum + " " + STATUS_SUMMARY).strip()
    st["phase"] = "delivered"
    st["progress_pct"] = 100
    st["health"] = "绿"
    d["updated_at"] = "2026-11-17T17:32:00+08:00"
    d["updated_by"] = "mech-lead"


if __name__ == "__main__":
    out = update_fragment("mech-lead", mutate)
    print("✅ mech.yaml 已原子更新")
    print("needs_from 条数 =", len(out.get("needs_from") or []))
    print("artifacts 条数 =", len(out.get("artifacts") or []))
