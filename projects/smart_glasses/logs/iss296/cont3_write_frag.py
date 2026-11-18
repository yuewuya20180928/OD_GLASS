#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-296 cont3 · 分片增量写 (★走 state/frag_write.py 的原子写通道 ★禁止 open(p,"w")★)

用法: python3 logs/iss296/cont3_write_frag.py
幂等: 同 key / 同 path 的旧条目先删后加 (★可重复跑, 不会写出重复条目★)
"""
from __future__ import annotations

import os
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

HO = "HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md"

CLAIMS = [
    {
        "key": "iss296_mech_cont3_reverify_and_10c_count_fix",
        "value": (
            "2026-11-18 05:4x cont3 复核: 闸1/闸2 主跑 rc=0 + --selftest 全 rc=0 "
            "(闸1 --selftest 曾因 ISS-302 落表变成 rc=2 ⇒ 已修回 rc=0 · 改的只是自检里那条【计数型 sanity 断言】"
            "hit==1 ⇒ hit>=1 · 判据方向 / fail-closed 三条 / 阈值 CRIT 0.60 与 cavity_req 4.50 与 cav_v 38.00 与 duct_v 6.00 "
            "一个都没动 · C4 判决函数 check_hard_protected_legal_reboard 一个字没动)"
        ),
        "note": (
            "根因 = ISS-302 (hw-lead · 2026-11-18 00:3x 落表) 往 HW/SCHEMATIC_LANDING_V1_LANDED.md §19 加了【两张表】"
            "⇒ 同一个链头 md5 6aee500e60ba0732f83a9cf557ba90ab 现在落在 2 行 "
            "(L1451 前后对照 + L1466 登记表) ⇒ 自检里【台账形状假设】hit==1 过期 ⇒ 误报红 · "
            "★该用例的【真正断言】c4_red10c (链头那一行被改坏 ⇒ C4 必须红) 一直是红的 ⇒ "
            "本次只把计数断言从 恰好 1 行 放宽成 至少 1 行 ⇒ 判据只可能变严 (多改一行 ⇒ 链断得更彻底) 不可能变松 · "
            "改前副本 logs/iss296/check_board_frame_coords_before_iss296_cont3.py (md5 051967adde31be65888de056c6fbf478) ⇒ "
            "★**最终态 md5 d4bd30c241718a8c0baf3084f78e2eb7**★ · 追加式留痕 (谁改的 / 哪个单号 / 新旧值 / 依据) · "
            "★**中间态 md5 5b38bf4e552b8699e8bc811b34529922 = 我 05:47:46 改完那一刻的中间态·不是最终态**★ · "
            "★**为什么变了: 2026-11-18 05:48:53 另一个并发 mech-lead 会话在【同一个闸】上追加了反向用例 ⑱/⑲**★ "
            "(★⑱ 真实落表形状 (两张表) 下合法改板 ⇒ C4 绿★ · ★⑲ 同样两张表但改前 md5 互相不一致 ⇒ C4 红 (fail-closed 在真实形状上没松)★) ⇒ "
            "★**我的 ⑩c 计数断言订正在最终态里逐字保留 (L1436 / L1439)·没被覆盖★** ⇒ 两者互补 (⑩c 证明【改坏 ⇒ 红】· ⑱ 证明【合法 ⇒ 绿】· ⑲ 证明【两张表不一致 ⇒ 仍红】) · "
            "最终态自检 21 条用例全 OK · 末行 自检结论 一致 · rc=0"
        ),
        "ref": f"{HO} §8-3 · logs/iss296/cont3_final_verification.log",
    },
    {
        "key": "iss296_mech_reboard_channel_live_validated_by_iss302",
        "value": (
            "本单 合法改板 通道在【真实台账】上第一次实战通过: ISS-302 真落表 "
            "(网表/脚表/BOM 重新生成 + 台账 §19 两张表) ⇒ 闸1 主跑仍 rc=0 且判决源自动跟到新链头 "
            "(by ISS-302 · 台账记录 12 条 · 链长 9 / 8) ⇒ 台账落一行 ⇒ 链头前移 ⇒ 闸跟着链头走 ⇒ 仍绿 "
            "这条路在真件上走通了 (不是沙盒)"
        ),
        "note": (
            "这正是 ISS-296 立项担心的那个坑 (合法改板后必假红 ⇒ 假红被误读成板改坏了 ⇒ 板白改第二遍) —— "
            "现在它在真落表面前是通的 · ★板与 .kicad_pro 仍逐字节不变 "
            "(md5 611b869e13518c3c023fb178f91a0075 / 3e504d2be83152e337949723e909be1b · "
            "板 mtime 仍 2026-11-06 07:07:17.362193413) · 网表/脚表/BOM 三件的变化全部出自 ISS-302 的落表 "
            "(台账 §19 有 ISS302_ROWS 登记 · 可查) ⇒ 本单对这 5 件零写入"
        ),
        "ref": f"{HO} §8-4 · logs/iss296/cont3_final_verification.log",
    },
    {
        "key": "iss296_mech_zero_board_write_zero_landing_cont3",
        "value": (
            "零写板 零落表 零改网表真源 (cont3 复核): 板 611b869e13518c3c023fb178f91a0075 + "
            ".kicad_pro 3e504d2be83152e337949723e909be1b (md5 与 mtime 双重不变) · "
            "落表台账本体零写入 (mtime 2026-11-18 00:22:44 = ISS-302 那次落表 · 非本单) · 同源探针 IDENTICAL: True"
        ),
        "note": (
            "本单 cont3 只写 3 处 = 交卷单 (追加 §8 · 老字一字没删) + state/fragments/mech.yaml "
            "(走 state/frag_write.py 原子写 · 一次没用过 open(p,w)) + MECH/check_board_frame_coords.py 的 "
            "1 条计数断言 (改前副本已留证) · hw.yaml / sw.yaml / pm.yaml 零碰 · 不自签 issue_log (verify_by = main) · "
            "零外发 · 实物 [实测] = 0 条 (本机无板无量具)"
        ),
        "ref": f"{HO} §8-4 · logs/iss296/cont3_final_verification.log · logs/iss296/cont3_probe.log",
    },
]

ARTIFACTS = [
    {
        "path": "logs/iss296/cont3_final_verification.log",
        "kind": "log",
        "version": "iss296-cont3",
        "updated_at": "2026-11-18",
        "summary": (
            "★ISS-296 cont3 交卷前必跑 全量日志 (10 条命令 rc 全 0 + 受保护 5 件 md5 + "
            "板 mtime 双重自证 + grep -c iss296 计数)★"
        ),
    },
    {
        "path": "logs/iss296/check_board_frame_coords_before_iss296_cont3.py",
        "kind": "backup",
        "version": "iss296-cont3",
        "updated_at": "2026-11-18",
        "summary": (
            "★ISS-296 cont3 改前副本 (★闸1 自检 ⑩c 计数断言订正前★ · md5 051967adde31be65888de056c6fbf478 · "
            "mtime 2026-11-17 20:20:17 原样保留★)★"
        ),
    },
    {
        "path": HO,
        "kind": "handoff",
        "version": "iss296-cont3",
        "updated_at": "2026-11-18",
        "summary": (
            "★ISS-296 交卷单 (cont3 + cont3-b 追加式 · 老字一字没删)★ · §8 cont3 复核轮 = ⑩c 计数断言订正留痕 "
            "+ ISS-302 真落表把 合法改板 通道在真实台账上首次跑通 · §9 cont3 最终复核轮 = 12 条命令 rc 表 + 闸 1 并发编辑留痕 "
            "· §10 cont3 + cont3-b 合并收口 = 时间线 + M3 need 事实订正 (9 道钉板闸 ①~⑨ 同一次全绿) + 最终态零写板自证 + 留给 main 的 4 条 · "
            "前身 §B1~§B5 + §6 复现清单 + §7 最终复核轮 (2026-11-17 21:0x) 全部保留 · 大小以盘上实际为准 (★每次追加都涨★)★"
        ),
    },
]

STATUS = {
    "phase": "delivered",
    "progress_pct": 100,
    "health": "green",
    "summary": (
        "★ISS-296 cont3 + cont3-b 交卷 (2026-11-18 05:5x · mech-lead · 两趟并发成果合并)★: "
        "① cont3 = 修回一条被 ISS-302 合法落表打破的自检计数断言 (⑩c hit==1 ⇒ hit>=1 · 判据方向 / fail-closed 三条 / 阈值 一个都没动 · 改前副本已留证) "
        "+ 拿到机制在【真实台账】上的第一次实战验证 (ISS-302 落表 ⇒ 判决源自动跟到 by ISS-302 的新链头 ⇒ 仍绿) "
        "② cont3-b = 补上【main 真实落表形状 (两张表)】的正向对照 ⑱ (⇒ C4 绿) + fail-closed ⑲ (两张表改前 md5 不一致 ⇒ C4 红) "
        "+ 独立探针 logs/iss296/probe_real_landing_shape_dup_rows.py (rc=0 · A 绿 / B 红 / C 定位 ⑩c 根因) · 自检条数 20→22 只增不减 "
        "③ 交卷前必跑 12 条命令全 rc=0 · Q1 18/18 · 门禁链上【9 道钉板闸 ①~⑨ 同一次全绿】(★含第 5 道脚表功能标签闸已修到 rc=0★) "
        "④ 零写板零落表零改网表真源 (板 md5 611b869e… + mtime 2026-11-06 07:07:17 双证不变) "
        "⑤ 4 条待 main/老板拍板仍挂账 (★本块 status 为 ISS-296 本轮合并留痕 · 两趟的 artifacts / claims / needs 全在盘上未丢★)·"
    ),
}

# ★★M3 那条 need 的【事实订正】(★留痕: 谁改的 / 哪个单号 / 旧值 → 新值 / 依据★★)
M3_NEED_OLD_FACT = (
    "★**旧值 (2026-11-17 21:3x main 实测)**: 门禁链 EXTRA_GATES 只有 2 条 ⇒ 9 道钉板闸里只有 SW 那 1 道在链上 "
    "· 且第 5 道 HW/check_pin_function_labels.py 主模式仍 rc=1 (18 条 ISS-257 起的既有缺陷)★"
)
M3_NEED_NEW_FACT = (
    "★**新值 (2026-11-18 05:56 本机实跑 · mech-lead cont3 实测)**: ★**9 道钉板闸 ①~⑨ 已全部挂进门禁链且【同一次全绿】**★ "
    "(①FSIN 根因闸 / ②G1a-7 选型落表闸 / ③改板提交顺序闸 / ④作业包覆盖度闸 / ⑤脚表功能标签闸 / ⑥作业包现状值闸 / "
    "⑦板框坐标闸 / ⑧结构真值闸 / ⑨SW 侧合法改板通道闸 —— ★**全 rc=0**★) "
    "⇒ ★**第 5 道的前置债已由 hw-lead 修掉 (rc=1 ⇒ rc=0)·不在 MECH 侧**★ "
    "⇒ ★**⇒ 「收工那天 9 道要同一次全绿」现在只剩一件事: main 把它写进 板只改一次 那一趟的作业包** ★ "
    "(★**落表当天 MECH 两道闸的主跑 + --selftest 必须同一次都跑** ⇒ 见本分片 needs_from 的 iss296_mech_cont3b_reboard_day_selftest_must_run★) ★ "
    "⇒ ★**本单只登记事实与代价, 不代 main 拍板 · 一个阈值没动 · 一个闸没改判据**★"
)
M3_NEED_KEY = "iss296_mech_m3_nine_gates_green_need"


def mutate(d: dict) -> None:
    claims = d.setdefault("interface_claims", [])
    for c in CLAIMS:
        claims[:] = [x for x in claims if x.get("key") != c["key"]]
        claims.append(dict(c))
    arts = d.setdefault("artifacts", [])
    for a in ARTIFACTS:
        arts[:] = [x for x in arts if not (x.get("path") == a["path"]
                                           and x.get("version") == a["version"])]
        arts.append(dict(a))
    st = d.setdefault("status", {})
    st.update(STATUS)
    # ★★M3 那条 need 的事实订正 (★append 式留痕写在 item 里 · 旧字保留在 [旧值…] 段★) ★★
    for n in d.setdefault("needs_from", []):
        if n.get("key") == M3_NEED_KEY:
            it = n.get("item", "")
            if "【2026-11-18 05:56 事实订正】" not in it:
                n["item"] = (
                    it.rstrip() + "\n\n    ★★【2026-11-18 05:56 事实订正 · mech-lead · ISS-296 cont3 · 留痕】★★ "
                    + M3_NEED_OLD_FACT + " ⇒ " + M3_NEED_NEW_FACT
                )


if __name__ == "__main__":
    update_fragment("mech-lead", mutate)
    print("[cont3_write_frag] ✅ mech.yaml 已原子更新 (claims+3 artifacts+3 status) → 再跑 python3 state/merge.py")
