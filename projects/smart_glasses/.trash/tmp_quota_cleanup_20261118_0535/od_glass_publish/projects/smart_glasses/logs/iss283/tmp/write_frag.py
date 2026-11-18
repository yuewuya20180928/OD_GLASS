#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-283 · cont2 · 写自己的分片 (★走 `state/frag_write.py` 的原子写·禁止 open(p,"w")★) ★"""
import os
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment      # ★★原子写 (tmp + fsync + os.replace)★★

TODAY = "2026-11-17"

ARTIFACTS = [
    {"path": "HANDOFF/2026-11-17_hw-lead_ISS283_V2解锁与W4G5落表.md", "kind": "handoff",
     "version": "1.0", "updated_at": TODAY,
     "summary": "ISS-283 交卷单 B0~B6 + 附 A/B/C/D 全填 (0 处未完成标记残留); 三件落表 (A3 12:16:08 / "
                "A4+A5 12:30:23 · 两次 rc=0) + C6 机制化 + 两道红闸修复 + 板侧清单 §③ 三条; 零写板·零外发"},
    {"path": "HW/landing_md5.py", "kind": "gate-lib", "version": "1.0", "updated_at": TODAY,
     "summary": "★新增★ 落表台账的 md5 注册表 ⇒ C6 / P6 / D0 三道闸的【取值来源】从「写死基线」改成"
                "「落表台账为准」⇒ 落表后不必再改基线数字 (fail-closed 七条: 查不到/链头不唯一/链断/"
                "链头无单号/四项不齐 ⇒ 红)"},
    {"path": "HW/check_board_frame_caliber.py", "kind": "gate", "version": "1.1", "updated_at": TODAY,
     "summary": "★cont2 修★ C6 走落表台账为准; ★★反向用例 ⑤b / ⑤c 的突变函数改为锚到【最新一条链】的 §16.2 表"
                " (旧写法打到旧链上 ⇒ 台账没改到 ⇒ C6 仍绿 ⇒ 假失败) ⇒ 并增 ⑤f (旧 md5 缺) + ⑤g (链头不唯一)"
                " ⇒ --selftest 12 条 → 14 条 · 失败 0 条 · rc=0"},
    {"path": "HW/check_onepass_preflight_coverage.py", "kind": "gate", "version": "1.1", "updated_at": TODAY,
     "summary": "★cont2 修★ P6 的网表/脚表/BOM 三件改走落表台账为准; ★★反向用例 ⑥c 的突变过滤条件逻辑取反"
                " ⇒ 台账一行都没删 ⇒ P6 必然绿 ⇒ 假失败 ⇒ 已改成真的删掉网表登记行 + 增 ⑥d (四项不齐)"
                " ⇒ --selftest 10 条 → 11 条 · 11/11 · rc=0; SOURCES 增 ISS-283 (只增来源·来源不明照样红)"},
    {"path": "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md", "kind": "board-side-checklist", "version": "1.1",
     "updated_at": TODAY,
     "summary": "★板侧清单追加 §3-追加 三条 (★§③-1 V-2 网改名 / §③-2 Q_PG land 重画 / §③-3 D− 侧 ESD 三件★)"
                " ⇒ 补实网表 note 里引用的「板侧清单 §③-2」; 新增条目 B32_V2_NET_RENAME (S4); "
                "B11_Q_PG_LAND / B30_LED_BRIGHTNESS 现状值跟盘面走 ⇒ 32 条 · P1~P6 全绿 · rc=0"},
    {"path": "HW/PCB/BOARD_ONEPASS_WORKPACKET.md", "kind": "workpacket-summary", "version": "1.1",
     "updated_at": TODAY,
     "summary": "★板那一趟的 S 步清单追加 2 行 (S4 = §③-1 V-2 网改名改 3 处焊盘网名 / S6 = §③-2 重画 Q_PG 的 3 根线)"
                " + S6 的 G-5 行由「未拍」订正为「已拍 20mA 档·已落表」; 老字一字未删 ⇒ D0~D6 全绿 · rc=0"},
    {"path": "HW/SCHEMATIC_LANDING_V1_LANDED.md", "kind": "landing-ledger", "version": "1.0",
     "updated_at": TODAY,
     "summary": "★三件落表的台账痕迹★ 链头 L1297 (A3 = V-2=1 · 12:16:08 · LANDING_AUTH L1328~L1332) + "
                "链头 L1353 (A4 = W-4 写法A + A5 = G-5 20mA · 12:30:23) ⇒ 两者都是 C6/P6/D0 的判定链头"},
]

CLAIMS = [
    {"key": "iss283_landing_chain_head", "value": "HW/SCHEMATIC_LANDING_V1_LANDED.md L1353 (ISS-283 · A4/A5 · 12:30:23)",
     "note": "★最新一条落表链★ ⇒ 任何闸要取 网表/脚表/BOM 的 md5 基线, 取这里 (HW/landing_md5.py 的 latest_chain)",
     "ref": ""},
    {"key": "iss283_protected_md5_current",
     "value": "板 611b869e13518c3c023fb178f91a0075 · .kicad_pro 3e504d2be83152e337949723e909be1b",
     "note": "★本单零写板★ ⇒ 这两个基线本单没动也没重锚 (它们不归落表链管); 网表 37f62ac3… / 脚表 a4270120… / BOM 5d02bece… 才是落表链管的",
     "ref": ""},
    {"key": "iss283_led_brightness_20ma", "value": "R_LED_R = 68Ω ±1% · R_LED_G = 55Ω ±1%",
     "note": "[官方]/[官网] 级折算的 20 mA 档真值 (ISS-244 实跑: 150Ω 只有 ~5 mA ⇒ 达不到 20 mA 档); 单颗 ~20 mA · 功耗 2.2mW→66mW · 两颗 ≈ 0.13 W 进电池账",
     "ref": ""},
    {"key": "iss283_qpg_write_a", "value": "Q_PG pad1 = PWR_GOOD (G) / pad2 = BAT_SW (S) / pad3 = PWR_ON (D)",
     "note": "★写法 A (老板 2026-11-17 09:49 拍板)★ DMP3098L 引脚序 1=G/2=S/3=D ⇒ 板上 land 必须重画 (板侧清单 §③-2)",
     "ref": ""},
    {"key": "iss283_c6_source_now_ledger", "value": "C6 / P6 / D0 三道闸的 md5 取值来源 = 落表台账 (HW/landing_md5.py)",
     "note": "★取值来源变了, 不是取值变了★ ⇒ 下次落表这三道不会再因基线过期而红 ⇒ 代价 = 台账成了新的单点 ⇒ 已配 fail-closed 七条兜底",
     "ref": ""},
    {"key": "iss283_board_side_sync_three", "value": "§③-1 V-2 网改名 / §③-2 Q_PG land 重画 / §③-3 D− 侧 ESD 三件",
     "note": "★板那一趟必须同趟清掉的三条★ ⇒ 已写进 HW/PCB/BOARD_ONEPASS_PREFLIGHT.md §3-追加 + 作业包 S4/S6 追加行 ⇒ 本单零写板",
     "ref": ""},
]

NEEDS = [
    {"key": "iss283_iec62471_regrade", "to": "main",
     "item": "G-5 落 20 mA 档 ⇒ 亮度 ×14 ⇒ 眼旁光源的 IEC 62471 分级必须重算 (hw-lead 只登记·不代拍)。"
             "降级方案: 按 ISS-244 同款实测口径补一组实测即可定档; 来不及 ⇒ 按最保守分组限制眼旁光源使用 (不擅自放宽)",
     "since": TODAY},
    {"key": "iss283_board_qpg_land_redraw", "to": "main",
     "item": "板那一趟必须重画 Q_PG 的 3 根线 (pad1→PWR_GOOD / pad2→BAT_SW / pad3→PWR_ON) ⇒ 漏了 ⇒ 开机路径彻底不通。"
             "已写进板侧清单 §③-2 + 作业包 S6 追加行 ⇒ 降级 = 改选 D-S-G 序器件 (同样是换封装·同样是板那一趟)",
     "since": TODAY},
    {"key": "iss283_board_v2_net_rename", "to": "main",
     "item": "板面 3 处焊盘网名 USB_D_P_SRC → NET_USB_D_P_TYPEC 必须同趟改 (D_ESD_USB_D.pad1 / R_SER_USB_D_P 一端 / "
             "J_SOM_P1 的 USB_D_P 脚) ⇒ 漏了 ⇒ 网表与板对不上。已写进板侧清单 §③-1 + 新增条目 B32_V2_NET_RENAME + 作业包 S4 追加行",
     "since": TODAY},
    {"key": "iss283_esd_dminus_still_open", "to": "main",
     "item": "D− 侧 ESD 三件仍挂着 (R4×2 + R9): ① D_ESD_USB_D 只有 2 焊盘 ② D− 网上 ESD 位号数 = 0 ③ 距 J_USB_C 47.99mm > 3.0mm "
             "⇒ 这 4 条是 G1a-4 的最后 4 条未落表项 (板侧) ⇒ 板那一趟清掉它们 G1a-4 才转绿。hw-lead 不代拍 ESD 型号轴 (W-1/W-2); "
             "降级 = 按「一颗双通道 (3 脚封装)」先落位 (B07 已写清 pad1=D+/pad2=D−/pad3=GND), 改选也只是同趟改位号",
     "since": TODAY},
    {"key": "iss283_sw_anchor_reanchor_after_landing", "to": "sw-lead",
     "item": "SW/SW_MD5_BASELINE_LEDGER.md 的网表/脚表锚点仍停在 ISS-257 那一版 (网表 e06c1dd6… / 脚表 287e7861…), "
             "而盘上已是 ISS-283 落表后的 37f62ac3… / a4270120… ⇒ SW/tools/timing_check.py 的两条网表锚点判红 "
             "(★该红在 12:30 那次落表扫描里就存在 ⇒ 不是本单造成⇒ 本单不碰 SW/ 文件·只登记★); "
             "降级 = 按台账 §16.2 链头 L1353 追加一条 entries (by=ISS-283, prev=e06c1dd6…, md5=37f62ac3…)",
     "since": TODAY},
    {"key": "iss283_preflight_c6_source_now_ledger", "to": "main",
     "item": "C6 / P6 / D0 三道闸的 md5 取值来源已改成「落表台账为准」⇒ 以后每次落表这三道不会再因基线过期而红, "
             "但台账本身成了新的单点 (台账被改坏 = 三道闸同时红 ⇒ 这是设计意图·不是巧合)。"
             "降级 = 若台账结构再变, 改 HW/landing_md5.py 一处即可 (三道闸共用它)",
     "since": TODAY},
]


def mutate(d):
    arts = d.setdefault("artifacts", [])
    for a in ARTIFACTS:
        arts[:] = [x for x in arts if x.get("path") != a["path"]]
        arts.append(dict(a))
    claims = d.setdefault("interface_claims", [])
    for c in CLAIMS:
        claims[:] = [x for x in claims if x.get("key") != c["key"]]
        claims.append(dict(c))
    needs = d.setdefault("needs_from", [])
    for n in NEEDS:
        needs[:] = [x for x in needs if x.get("key") != n["key"]]
        needs.append(dict(n))
    st = d.setdefault("status", {})
    st["phase"] = "P1"
    st["progress_pct"] = 100
    st["health"] = "yellow"
    st["summary"] = ("ISS-283 交卷: 三件落表已在盘上真落地 (A3 12:16:08 / A4+A5 12:30:23 · 两次 rc=0) + "
                      "C6/P6/D0 三道闸的 md5 取值来源改成「落表台账为准」 (HW/landing_md5.py) + "
                      "修好 main 13:1x 点名的 C6 selftest 红 (12→14 条 · 失败 0) 与扫描撞出来的 preflight selftest 红 "
                      "(10→11 条 · 11/11) + 板侧清单追加 §③ 三条 (新增 B32) + 作业包 S4/S6 追加行; "
                      "零写板·零落表(已落过不重复落)·零外发; 板 611b869e… 与 .kicad_pro 3e504d2b… 逐字节不变")
    st["updated_at"] = TODAY
    d["updated_at"] = TODAY
    d["updated_by"] = "hw-lead"


update_fragment("hw-lead", mutate)
print("✔ hw.yaml 已原子更新 (frag_write.update_fragment)")
