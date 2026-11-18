#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-296 cont2 · mech-lead · 分片原子写 (★走 state/frag_write.py 的原子写通道★
   ★**禁止 open(p,"w")** —— 本脚本一次都没直接打开过分片做写入★)

用法: python3 logs/iss296/cont2_write_frag.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "state"))

from frag_write import update_fragment  # noqa: E402  ★state/frag_write.py 的原子写 API★

HANDOFF = "HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md"

CLAIMS = [
    {
        "key": "iss296_mech_two_gates_legal_reboard_channel",
        "value": ("闸1 C4 + 闸2 G5b 已接合法改板通道 (判决源 = 落表台账链头 + reboard 四项原子映射 "
                  "by/file/prev_md5/md5; 判据方向没变; fail-closed 三条没动; 阈值 CRIT 0.60 / "
                  "cavity_req 4.50 / cav_v 38.00 / duct_v 6.00 一个没动)"),
        "note": ("ISS-296 · 2026-11-17 · mech-lead · 照 SW 侧 ISS-284 已 verified 的四条判据一条不许放宽 "
                 "(① 保护基线自证 ② 台账无变更行 ⇒ 纯 md5 硬保护 ③ 有变更行 ⇒ 链头唯一/链不断/链头有单号 "
                 "+ 四项原子记录逐字对上 + 基线留链尾 + 盘上==链头 ④ 同组成对覆盖) · "
                 "MECH 侧不新造第二个可手改的 md5 字段 (基线值保留在 PROTECTED 里只作锚点防篡改) ⇒ "
                 "比 SW 侧少一个可被挖的坑 = 更严 · 板与 .kicad_pro 在变更行读法下链头 = None ⇒ "
                 "今天走判据 ② (纯 md5 硬保护) ⇒ 硬保护一刻没松"),
        "ref": ("MECH/check_board_frame_coords.py L109-125 + L652-789 + L819 · "
                "MECH/check_demo_struct_truth.py L101-109 + L501-640 + L851 · " + HANDOFF + " §B1"),
    },
    {
        "key": "iss296_mech_reboard_reverse_cases_all_caught",
        "value": ("闸1 ⑯a/⑯b/⑰ + 闸2 R10/R11a/R11b/R12 全抓到 (7 条) · 闸2 合计 28/28 · "
                  "闸1 --selftest 末行 自检结论 一致"),
        "note": ("ISS-296 · 2026-11-17 · mech-lead · 沙盒跑真盘零写 (台账与板全是临时目录拷贝) · "
                 "红色用例必须抓到指定判据组才算通过 (C4 / G5b) · 正向用例必须整条绿才算通过 "
                 "(证明通道真有路, 不是把灯调没了) · ⑯a 链头不唯一⇒红 / ⑯b 链断(基线不在链尾)⇒红 / "
                 "⑰ 正向对照⇒绿 (C1-C3 全绿 + C4 错误 0 条) · R10 同组只来一条⇒红 / R11a 链头不唯一⇒红 / "
                 "R11b 链断⇒红 / R12 正向对照⇒绿 (实际红组 无)"),
        "ref": ("logs/iss296/cont2_frame_selftest.log · logs/iss296/cont2_struct_selftest.log · "
                "logs/iss296/frame_selftest.log · logs/iss296/struct_truth_selftest.log · "
                + HANDOFF + " §B3"),
    },
    {
        "key": "iss296_mech_zero_board_write_zero_landing",
        "value": ("受保护 5 件 md5 逐字节不变 (板 611b869e13518c3c023fb178f91a0075 / "
                  ".kicad_pro 3e504d2be83152e337949723e909be1b / 网表 37f62ac3f0b81d92ca7d48fdea717f07 / "
                  "脚表 a4270120454aedf7a23c92cd8985c8a6 / BOM 5d02bece9477ffce5fbe0193c7d5cce4) + "
                  "板 mtime 仍 2026-11-06 07:07:17.362193413 + 同源探针 IDENTICAL: True"),
        "note": ("ISS-296 · 2026-11-17 · mech-lead · 零写板零落表双重自证 (md5 + mtime) · "
                 "落表台账 HW/SCHEMATIC_LANDING_V1_LANDED.md mtime 仍 2026-11-17 12:30:23 "
                 "(= ISS-283 那次落表, 本单零写入) · 闸 1 与闸 2 本趟 cont2 mtime 未变 "
                 "(20:20:17 / 20:25:32) ⇒ 闸本体本趟一个字没动 · 只写自己的分片 "
                 "(hw.yaml / sw.yaml / pm.yaml 零碰) · 不自签 issue_log · 零外发 · "
                 "实物 [实测] = 0 条 (本机无板无量具)"),
        "ref": ("logs/iss296/cont2_probe.log (末行 IDENTICAL: True · 15 组读数逐字相同) · "
                "logs/iss296/cont2_frame_main.log · logs/iss296/cont2_struct_main.log · "
                + HANDOFF + " §B4"),
    },
    {
        "key": "iss296_mech_m1_ledger_row_interface",
        "value": "单号 | 文件 | 前 md5 | 后 md5 (四项同行 · 板与 .kicad_pro 成对两行 · 一行两件两值 = 歧义行 ⇒ 判红)",
        "note": ("ISS-296 · 2026-11-17 · mech-lead · 这是给 main 在 出板那一趟 落表用的接口格式 "
                 "(main 立的口径 ISS-275 §1⑧) · 台账本体不许 MECH 侧写 · "
                 ".kicad_pro 真没变时也要写 否 (逐字节不变) 那一行 · "
                 "单号必须出现在行内或该行所属小节标题里"),
        "ref": "MECH/BOARD_ONEPASS_MECH_SYNC.md 的 ISS-296-收工清单 M1 节 · " + HANDOFF + " §B2",
    },
    {
        "key": "iss296_mech_frame_id_unified_pending_boss",
        "value": "待拍 (main → 老板 U-274-6): B160x100 vs 160x100-bench vs 60x30-setA vs F30A 未统一",
        "note": ("ISS-296 · 2026-11-17 · mech-lead · 本单只登记不代裁 (M2-6) · 一个 id 没改 · 归 main → 老板"),
        "ref": ("MECH/BOARD_ONEPASS_MECH_SYNC.md 的 ISS-296-收工清单 M2-6 + M4 · " + HANDOFF + " §B5"),
    },
]

ARTIFACTS = [
    {
        "path": HANDOFF,
        "kind": "handoff",
        "version": "iss296-cont2",
        "updated_at": "2026-11-17",
        "summary": ("★ISS-296 cont2 交卷单 (26,949 B) · B1 结论摘要 (两道闸怎么接的合法改板通道 + 四条判据表 + "
                    "口径纪律自证) · B1-⑤ 同源机器证明 (IDENTICAL True · 15 组读数逐字相同) · "
                    "B2 验收标准自评 + 收工后同一次重锚清单 (M0/M1/M2-1~M2-6/M3 九道闸表/M4) · "
                    "B3 证据分级 + 反向用例 7 条 (⑯a/⑯b/⑰ + R10/R11a/R11b/R12) · "
                    "B4 接口取值声明 + 回归 10 条 rc=0 + 受保护 5 件 md5/mtime 双重自证 · "
                    "B5 未决项与卡点 4 条 (归 main/老板) · 复现清单一条一条贴 · "
                    "零写板零落表零改网表真源 · 不自签 issue_log · 零外发 · 实物 [实测] = 0 条★"),
    },
    {
        "path": "MECH/check_board_frame_coords.py",
        "kind": "gate",
        "version": "iss296",
        "updated_at": "2026-11-17",
        "summary": ("★ISS-296 合法改板通道 (C4)★ · 86,674 B · mtime 2026-11-17 20:20:17 · "
                    "PROTECTED (L109-112) 基线值一字未改 + LEDGER_CANON (L119) + PROTECTED_LEDGER (L121-125) + "
                    "check_hard_protected_legal_reboard (L652-789) 四条判据 + 调用点 L819 · "
                    "主跑 rc=0 (末行 结论 四项全过) · --selftest rc=0 (末行 自检结论 一致) · "
                    "阈值零漂移 (CRIT 照抄 board_port_opening_s6_check) · 本单 cont2 未动此文件★"),
    },
    {
        "path": "MECH/check_demo_struct_truth.py",
        "kind": "gate",
        "version": "iss296",
        "updated_at": "2026-11-17",
        "summary": ("★ISS-296 合法改板通道 (G5b)★ · 72,428 B · mtime 2026-11-17 20:25:32 · "
                    "HARD_PROTECTED_PAIR (L101) + LEDGER_REQUIRED (L109) + LEDGER_CANON (L334) + "
                    "check_hard_protected_legal_reboard (L501-640) + 调用点 L851 + G5b 标签 L879 · "
                    "主跑 rc=0 (G5b = OK) · --selftest rc=0 (末行 反向用例 28/28 抓到了) · "
                    "本单 cont2 未动此文件★"),
    },
    {
        "path": "MECH/BOARD_ONEPASS_MECH_SYNC.md",
        "kind": "note",
        "version": "iss296",
        "updated_at": "2026-11-17",
        "summary": ("★ISS-296-收工清单 (追加式 · 老字一字没删)★ · 96,970 B · mtime 2026-11-17 20:57 · "
                    "一节含 M0 为什么先做 / M1 落表台账那一行的接口格式 (给 main) / "
                    "M2 收工后同一次重锚强制项 M2-1~M2-6 / "
                    "M3 收工那天全仓 9 道钉板 md5 的闸都要绿 (含 9/9 机器清单 "
                    "state/board_md5_pinned_gates.json 复核) / M4 不代拍三条 / M5 边界自证 · "
                    "本趟 cont2 只订正 M3 表里 HW 6 道的 6 个单元格 (待建 ⇒ 已建 (ISS-297) · 已留痕 · "
                    "改前副本 logs/iss296/msync_before_iss296_cont2.md 96,970 B)★"),
    },
    {
        "path": "logs/iss296/probe_ledger_reading_same_source.py",
        "kind": "script",
        "version": "iss296",
        "updated_at": "2026-11-17",
        "summary": ("★ISS-296 同源机器证明探针★ · 7,407 B · mtime 2026-11-17 20:27:02 · "
                    "MECH 侧台账解析器 vs SW 侧 (ISS-284 定版闸) 解析器 · "
                    "比对 6 项 (链头/链/链头单号/取不准原因/链上出现过的 md5/记录集) · "
                    "5 文件 × 3 读法 = 15 组读数全部逐字相同 · 实跑 rc=0 末行 IDENTICAL: True · "
                    "台账本体只读★"),
    },
]

NEEDS = [
    {
        "key": "iss296_mech_m3_nine_gates_green_need",
        "to": "main",
        "item": ("★ISS-296 · M3 那张 9 道钉板 md5 的闸表里 HW 6 道的通道状态: "
                 "机器清单 state/board_md5_pinned_gates.json (mtime 2026-11-17 20:49) 实测 9/9 全是 "
                 "已有 reboard 通道 ⇒ HW 6 道已由 ISS-297 建好 (本单已把 M3 表那 6 个单元格由 待建 订正为 "
                 "已建 (ISS-297) · 已留痕) ⇒ "
                 "★**但 收工那天 9 道要 同一次 全绿 这件事要 main 写进 板只改一次 那一趟的作业包**★ ⇒ "
                 "且第 5 道 HW/check_pin_function_labels.py 现在主模式仍 rc=1 (18 条 ISS-257 起的既有缺陷 · "
                 "改前也是 rc=1 · 属别单范畴) ⇒ 那一道的前置债在 hw-lead 那边, 不在 MECH 侧 · "
                 "本单只登记事实与代价, 不代 main 拍板"),
        "since": "2026-11-17",
    },
    {
        "key": "iss296_mech_m2_6_frame_id_need",
        "to": "main",
        "item": ("★ISS-296 · M2-6 帧标 id 统一: 现盘上并存 B160x100 (MECH 闸里的现役帧) / "
                 "160x100-bench (HW 侧) / 60x30-setA / F30A (60×30 套A 旧帧) 四套写法 ⇒ "
                 "id 不统一 = 后期坐标漂移 (M2-6 登记的后果) ⇒ "
                 "★**本单只登记 不代裁 一个 id 没改**★ ⇒ ★**归 main → 老板 (U-274-6)**★ · "
                 "依据 MECH/BOARD_ONEPASS_MECH_SYNC.md 的 ISS-296-收工清单 M2-6 + M4 第 1 条"),
        "since": "2026-11-17",
    },
    {
        "key": "iss296_mech_m1_ledger_row_need",
        "to": "main",
        "item": ("★ISS-296 · M1 落表台账那一行的接口格式 (★这是给 main 在 出板那一趟 落表用的格式, "
                 "★**台账本体不许 MECH 侧写**★): 每受管文件一行 = 单号 | 文件名 | 改前 md5 | 改后 md5 四项同行 ⇒ "
                 "板与 .kicad_pro 必须成对两行同一个单号 (只写一行 ⇒ 判红) ⇒ "
                 ".kicad_pro 真没变时也要写 否 (逐字节不变) 那一行 ⇒ "
                 "一行不许同时写两件两值 (歧义行 ⇒ MECH 侧当它不算变更行 ⇒ 判红) ⇒ "
                 "单号必须出现在行内或该行所属小节标题里 (两处都没有 ⇒ 四项不齐 ⇒ 判红) · "
                 "板的前值 = 611b869e13518c3c023fb178f91a0075 · "
                 ".kicad_pro 的前值 = 3e504d2be83152e337949723e909be1b (逐字节不变)"),
        "since": "2026-11-17",
    },
    {
        "key": "iss296_mech_iss294_opening_status_need",
        "to": "main",
        "item": ("★ISS-296 · 把 iss294_usbc_edge_opening_size_and_z_window 这条 need 的现状写清 "
                 "(它仍在盘上, state/fragments/mech.yaml L2729, to=main): J_USB_C 边开口几何与代价已算完 "
                 "(帧 B160x100 · 边开口 X 132.995..147.005 × Y 0.000..7.300 · "
                 "必须清空区 X 133.895..146.105 × Y 0.000..6.400 · 单边净距 0.900 · "
                 "最坏 0.600 = CRIT 刚好过 · 座体真实高 h 仍 [0数据]) ⇒ "
                 "★**开口最终尺寸 + Z 向窗口 (OPEN_Y_eff = 4.60 / 4.60 / 5.80 不在板面坐标里, "
                 "必须跟结构件外形一起定) = main → 老板 拍板项 ⇒ 本单不许自己定尺寸 一个尺寸没定**★ · "
                 "另: 任务书 §④ 尾巴提的 iss282_mech_sync_m5_baseline_after_landing 这条 need "
                 "实查已不在盘上 (grep -c = 0 · 被后来的单子合并清掉) ⇒ 本单不找它也不凭空造它"),
        "since": "2026-11-17",
    },
]

STATUS = {
    "phase": "delivered",
    "progress_pct": 100,
    "health": "绿",
    "summary": (
        "★ISS-296 cont2 交卷 (2026-11-17 20:5x) ⇒ 本趟只剩 paperwork 三件, 闸本体一件没再动: "
        "① 交卷单 HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md 补满 B1 结论摘要"
        "(两道闸怎么接的合法改板通道 + 四条判据表 + 口径纪律自证) / B1-⑤ 同源机器证明"
        "(IDENTICAL True · 15 组读数逐字相同) / B2 验收标准自评 + 收工清单"
        "(M0/M1/M2-1~M2-6/M3 九道闸表/M4) / B3 证据分级 + 反向用例 7 条(⑯a/⑯b/⑰ + R10/R11a/R11b/R12) / "
        "B4 接口取值声明 + 回归 10 条 rc=0 + 受保护 5 件 md5/mtime 双重自证 / B5 未决项与卡点 4 条 "
        "② 分片原子写(5 条 interface_claims + 5 条 artifacts + 4 条 needs_from · "
        "走 state/frag_write.py, 禁止 open(p,w) 一个字没用) "
        "③ 交卷前必跑 10 条全 rc=0 (gate_check Q1 = 18/18) ⇒ "
        "边界: 零写板(板 md5 611b869e… + mtime 2026-11-06 07:07:17 双重自证) / "
        "零落表(台账 mtime 仍 12:30:23) / 未改 HW/ / 未改 SW/ / 未改既有 MECH 判据脚本 / 未改阈值 / "
        "未改 state/gate_check.py / 未改 state/issue_log.yaml / hw.yaml+sw.yaml+pm.yaml 零碰 / "
        "只订正 M3 表 HW 6 道 6 个单元格并留痕 / 零外发 / 不代拍 / 不自签 issue_log / 实物 [实测] = 0 条★"
    ),
}


def main() -> int:
    def mutate(d: dict) -> None:
        d.setdefault("interface_claims", []).extend(CLAIMS)
        d.setdefault("artifacts", []).extend(ARTIFACTS)
        d.setdefault("needs_from", []).extend(NEEDS)
        st = d.setdefault("status", {})
        st.update(STATUS)
        d["updated_at"] = "2026-11-17T20:59:00+08:00"
        d["updated_by"] = "mech-lead"

    update_fragment("mech-lead", mutate)
    print("✅ mech.yaml 已原子写 (state/frag_write.update_fragment → atomic_write_yaml)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
