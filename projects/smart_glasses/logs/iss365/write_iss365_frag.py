#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""write_iss365_frag.py —— ★★【ISS-365】写分片 (★只走 `state/frag_write.py`·禁止 open(p,"w")★) ★★

★★**纪律 (★任务书原文★)**: ★**写前后各记一次 md5 基线·期间被别人改过 ⇒ 停下并在交卷页 B5 写清「已停止」·不许静默覆盖** ★
  ⇒ ★**本脚本: ① 记写前 md5 ② 再读一次 md5 确认没被别人改 (并发保护) ③ 调 `state/frag_write.py` ④ 记写后 md5 ⑤ 写后必须 [实测] 校验自己的 key 在不在** ★
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FRAG = os.path.join(PROJ, "state", "fragments", "mech.yaml")
LOG = os.path.join(PROJ, "logs", "iss365")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


CLAIMS = [
    ("iss365_s10_set90_computed",
     "靶内 77 + 缺口 13 = 90 件 (脚本实算)",
     "ISS-365: 90 件集合 = 只读 import HW/check_fp_truth_coverage_gap.py 的 netlist_placeholder/iss356_targets/coverage_gap 三函数实算 ⇒ 靶内(C4 ∩ ISS-356 靶子) 77 + 缺口(必装∩非NET/TP∩footprint≠待定∩C4) 13 = 90 ⇒ 本单新建的机器闸 M1 把这一条做成判据 (页里写 ≠ 实算 ⇒ 红)",
     "MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md §0.2 + logs/iss365/compute_iss365.json"),
    ("iss365_s10_rsel_10_in_set90",
     "10 / 10 (R_SEL_D0_N/P D1_N/P CK_N/P D2_N/P D3_N/P 全在 90 件里)",
     "ISS-365: 脚本实算交集 ⇒ 这 10 件正是换官方 land 要动的那批 ⇒ MECH 侧 §3「20 个目标落位 × MECH 保留区」的净距结论用的就是它们【当前占位 fab 1.80×1.00 · 中心距 1.60】⇒ 换封装后必须重算 (之前没人算过) ⇒ 机器闸 M2 守这条",
     "MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md §0.3 + §2"),
    ("iss365_s10_rsel_clearance_after_swap",
     "闸口径最小净距 7.6500 → 7.3250 (Δ −0.3250); 冲突 0 → 0; 相邻落位间距 2.0000 → 2.3500; 必清空净距 +0.6750 ⇒ 结构侧零重排",
     "ISS-365 实算 (与 MECH/check_onepass_struct_crosscheck.py 自己打印的 min_clr(全)/min_clr(必清空) 逐字同口径, 换封装前后各 20/20 逐条对账一致, 见 logs/iss365/xcheck_result.json) ⇒ 结论 = 那一趟的 S6 落位不需要为换封装重排; 代价在布线端点重接 (占位 pad1 在原点/pad2 在 +1.600 不对称 ⇒ 官方 0603 对称 ±0.825), 归 hw-lead",
     "MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md §2.1 + §2.3"),
    ("iss365_s10_led_space_drift_real",
     "D_LED_G 换官方 0805 ⇒ led_space 可落位块数 1992 → 2183; 两条整高自由带 X 1.550..3.450 / 72.540..73.660 → 2.225..3.250 / 73.215..74.385; 净距敏感度 sweep 1992/2016/2031/2075 → 2183/2241/2253/2197 (不再单调)",
     "ISS-365 沙盒实测 (tmp/iss365_sbx/ 板副本上换官方 land, 只读 import MECH/check_board_frame_coords.py 的 compute() ⇒ led_space) ⇒ 根因 = led_space() 用的是 D_LED_G 铜箔外框相对封装原点的偏移 rel, 换 land ⇒ rel 变 ⇒ 带/窗口/块数全变 ⇒ 既有页 MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md §3.2 那句「led_space 块数 (1992/2016/2031/2075) 不变」在换封装后【不成立】⇒ 必须同一次重算 (本单建议 E-9)",
     "MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md §8.3 + logs/iss365/led_space_drift.json"),
    ("iss365_s10_negative_conclusions",
     "座体类 6 组 ref (J_DEBUG/J_UART/J_USB_C/J_CHG/J_SOM_P1..P4) + 10 个 TP_DSI_* 与 90 件的交集 = ∅",
     "ISS-365 脚本实算 (机器闸 M3 守这条, 不为空即红) ⇒ MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md §4 的座体三方对照 + 开口尺寸 + E-1 的排针 pitch 1.27 vs 0.50 三条结论【不受 S10 影响】⇒ 省下一轮重复劳动 (注: J_SOM_P1/J_SOM_P3 的 BOM type=NET ⇒ 进不了「必装 ∩ 非 NET/TP」)",
     "MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md §3"),
    ("iss365_zero_external_pending",
     "0 件外部等待项 (25 件逐件都有本机可执行或本机已实测在盘的退路)",
     "ISS-365: 本单 0 次外发 (不发邮件/不询价/不采购/不问询) ⇒ 封装高度等外部数据全部自己网上查并标 [官网] (X1SON-2 0.45 / SOD-323 0.80 / SOT-23 1.03 / KMR2 1.9 / B3U-1000 1.6 mm) ⇒ 查不到的一律 [0数据] + 降级方案 ⇒ 机器闸 M7 守「正文零挂起措辞」",
     "MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md §3 + §6 + §7"),
]

ARTIFACTS = [
    ("MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md", "spec", "iss365",
     "ISS-365 交卷页: 「板只改一次」那一趟 S10 把 90 件占位 land 换成官方封装 ⇒ 对 MECH 侧几何判据的影响面 (机器可读) —— §0 口径与读数 (90 件集合/10 件交集/负结论/保留区口径全脚本实算) + §1 敏感度总表 25 件 × 9 字段 (现占位几何读板 / 目标几何读 .kicad_mod / Δ / 碰哪条 / 判定 / 重算后的数 / 证据等级 / 降级方案) + §2 那 10 个 R_SEL_* 的专项 (换封装前后净距两列 + Δ + 要不要重排的依据与代价) + §3 负结论 + §4 K2/K3 两条分支的结构后果 + §5 E-7~E-13 追加建议 (既有页老字零改动) + §6 降级方案 + §7 未决项 + §8 沙盒重判实测 (四道闸前后并排 + LED 带真漂移) + §9 边界 + §10 机器块"),
    ("MECH/check_onepass_s10_fp_swap_impact.py", "gate", "iss365",
     "ISS-365 新建机器闸: M0 基准块合法 JSON / M1 90 件集合脚本实算 (页里写 ≠ 实算 ⇒ 红) / M2 10 个 R_SEL_* 落在 90 件里 (实算交集) / M3 负结论可证 (座体类 + TP_DSI_* 与 90 件交集 = ∅) / M4 §1 逐件 9 字段齐全 (漏件点名 ref) / M5 几何一致性 (页里写的目标 fab 外框/courtyard/焊盘数 == 脚本从 .kicad_mod 实测) / M6 证据等级五级白名单 (写 [官方] = 红) + 降级方案逐件非空 / M7 正文零挂起措辞 ⇒ rc=0 全绿; --selftest 8 条反向用例 (删行→M4 / 改错几何→M5 / 空壳降级→M6 / [官方]→M6 / 塞挂起措辞→M7 / 改 90→M1 / 塞假 R_SEL→M2 / 塞 J_USB_C→M3) 每条自证「红的是目标那一条, 其余仍绿」⇒ 内容级判据, 不挂 md5 ⇒ 板合法改一次之后仍绿"),
    ("HANDOFF/2026-11-23_mech-lead_ISS365_S10换封装对MECH侧影响面.md", "handoff", "iss365",
     "ISS-365 交卷页: B1 结论 (三个最硬的数 + D_LED_G 真漂移 + §2 专项 + 一条没替老板拍) + B2 验收标准自评 20 条逐条 + B3 证据分级 + B4 接口取值声明 + B5 未决项与卡点 U-365-1~6 + B6 自证复现命令 + 落盘文件清单 + logs/iss365/ 留证清单 + 沙盒重判实测结论表 + B7 边界自证"),
    ("logs/iss365/", "evidence", "iss365",
     "ISS-365 留证: 基线/终检 md5 + 实算脚本链 (pcbparse/compute/build/compose/xcheck/led_space_drift) + 实算产物 (compute_iss365.json / machine_block.json / section1_rows.md) + 沙盒建造与换 land 脚本 + ★四道 MECH 闸换封装前后的并排输出 (本单最硬的一件)★ + 与既有闸 20/20 逐条对账 + selftest 全量输出 + 真板复核"),
    ("tmp/iss365_sbx/", "sandbox", "iss365",
     "ISS-365 沙盒 (项目盘内, 不写 /tmp): MECH/ 213 件 + HW/ + HW/PCB/ 副本 + state 符号链接 ⇒ 板副本上把 §1 的 25 件换成官方 .kicad_mod (位置/旋转沿用旧封装, pad↔net 按焊盘号继承, 不替老板做 pad 序对调) ⇒ 四道 MECH 闸 BEFORE/SWAP/AFTER 三段并排 ⇒ 真板一个字节没碰"),
]

NEEDS = [
    ("iss365_e9_led_band_and_sweep_recompute", "main",
     "ISS-365 E-9: D_LED_G 换官方 0805 后, MECH/BOARD_ONEPASS_MECH_SYNC.md 机器块的 led.full_height_bands (X 1.550..3.450 / 72.540..73.660) + led.clearance_sweep (1992/2016/2031/2075) 与 MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md 的 LED 窗口规格【全部过期】⇒ 本单沙盒实测的新值 = 可落位块数 1992→2183 · 两条带 X 2.225..3.250 / 73.215..74.385 (宽 1.900→1.025 / 1.120→1.170) · sweep 2183/2241/2253/2197 (clr=0.5 反而 < clr=0.2 ⇒ 不再单调, 必须重扫不能插值) · LED_G_D 走线最短 0.450→0.621 mm ⇒ 建议 main 派活把这三处同一次重算 (本单零改既有页正文, E-9 写在 MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md §5)",
     "2026-11-23"),
    ("iss365_e8_e10_key_hole_and_esd_height_gates", "main",
     "ISS-365 E-8 + E-10: 两条 MECH 侧判据【现在没有任何闸在管】⇒ ① 【键孔尺寸】: 3 只按键换 KMR2 后 fab 3.00×3.00→4.20×2.80 (宽 +1.200) ⇒ 键孔要沿 X 加宽 1.200 mm, 键高 1.9 mm [官网] ⇒ 建议新建 MECH/check_onepass_key_clearance.py; ② 【ESD 封装高度 ≤0.5 mm】: 官方 X1SON-2 = 0.45 mm [官网] 满足 / SOD-323 = 0.80 mm [官网] 突破 / SOT-23 = 1.03 mm [官网] 突破 ⇒ 建议新建 MECH/check_onepass_esd_height.py ⇒ 本单只建了守住 §1 目标几何与 §2 净距两列的那道闸, 这两条判据本单【不越界】建",
     "2026-11-23"),
    ("iss365_u365_4_esd_height_provenance", "main",
     "ISS-365 U-365-4: 任务书给的 ESD 结构要求里「封装 ≤0.5 mm 高」这一条, 本单在 MECH/ 全目录 grep 只找到 ISS-085 的「ESD 距连接器 ≤3.0 mm」(登记在 state/.bak_iss249/HW/SCHEMATIC_V1.md 的「结构总工已回」段) ⇒ 「≤0.5 mm 高」的登记原文【本单找不到】⇒ 本单按任务书的数算并把它标 [0数据] + 给降级方案, 同时把「找不到原文」登记成缺口 ⇒ 请 main 补登记或确认口径 (若该条最终不是硬约束, 则 D_ESD_DEMO 的 SOD-323 与 D_ESD_USB_D 的 3 脚档的 0.80/1.03 mm 都不构成问题)",
     "2026-11-23"),
]

STATUS = ("phase=delivered progress_pct=100 health=绿 "
          "summary=\"ISS-365 交卷: 「板只改一次」S10 把 90 件占位 land 换成官方封装 ⇒ 对 MECH 侧的影响面提前算完并钉成机器闸 "
          "(MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md + MECH/check_onepass_s10_fp_swap_impact.py M0~M7 + --selftest 8/8) ⇒ "
          "90 件集合 = 靶内 77 + 缺口 13 (脚本实算) · 10 个 R_SEL_* 全在 90 件里 · 换官方 0603 后闸口径最小净距 7.6500→7.3250 (Δ −0.3250) 冲突 0→0 "
          "⇒ 结构侧零重排 (代价在布线端点重接, 归 hw-lead) · ★真漂移 = D_LED_G 换 0805 后 led_space 块数 1992→2183 ⇒ 既有页 §3.2 那句旧结论作废, 须同一次重算 (E-9)★ · "
          "座体类 6 组 + 10 个 TP_DSI_* 与 90 件交集 = ∅ ⇒ §10 三方对照/开口尺寸/排针 pitch 不受 S10 影响 · "
          "零写板 (611b869e… / mtime 2026-11-06 07:07:17) 零落表 零改既有闸 零改既有页正文 零挂链 零外发 未替老板拍板 (光孔有无 / W-1W-2 / 按键 3N vs 1.5N 只登记) ⇒ "
          "写 5 处 = 规格页 + 新闸 + 交卷页 + logs/iss365/ + 本分片 (只走 state/frag_write.py)\"")


def verify_only():
    """★只校验 (★不写★) —— 用来在【写完之后】独立复核一遍分片里自己的 key 在不在★"""
    text = open(FRAG, encoding="utf-8").read()
    claim_keys = [k for k, _v, _n, _r in CLAIMS]
    need_keys = [k for k, _t, _i, _s in NEEDS]
    art_paths = [p for p, _k, _v, _s in ARTIFACTS]
    miss_claim = [k for k in claim_keys if ("key: %s" % k) not in text]
    miss_need = [k for k in need_keys if ("key: %s" % k) not in text]
    miss_art = [p for p in art_paths if ("path: %s" % p) not in text]
    ok_status = "ISS-365 交卷" in text
    out = {"claim_keys": len(claim_keys), "claim_missing": miss_claim,
           "need_keys": len(need_keys), "need_missing": miss_need,
           "artifact_paths": len(art_paths), "artifact_missing": miss_art,
           "status_updated": ok_status,
           "frag_md5_now": md5(FRAG)}
    out["all_present"] = not (miss_claim or miss_need or miss_art) and ok_status
    with open(os.path.join(LOG, "23_frag_write_status.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("[frag-verify] %s" % out)
    return 0 if out["all_present"] else 4


def main():
    os.makedirs(LOG, exist_ok=True)
    if "--verify-only" in sys.argv:
        return verify_only()
    before = md5(FRAG)
    with open(os.path.join(LOG, "22_frag_md5_before.txt"), "w", encoding="utf-8") as fh:
        fh.write("%s  state/fragments/mech.yaml\n" % before)
    print("[frag] 写前 md5 = %s" % before)

    # ---- 并发保护: 再读一次, 确认没被别人改过 ----
    again = md5(FRAG)
    if again != before:
        print("[frag] ★★写前二次读数不一致 (%s ≠ %s) ⇒ 有人正在改 ⇒ 【已停止·不静默覆盖】★★" % (again, before))
        return 3

    cmd = [sys.executable, os.path.join(PROJ, "state", "frag_write.py"), "--agent", "mech-lead"]
    for k, v, n, r in CLAIMS:
        cmd += ["--add-claim", 'key=%s value="%s" note="%s" ref="%s"' % (k, v, n, r)]
    for p, kind, ver, summary in ARTIFACTS:
        cmd += ["--add-artifact", 'path=%s kind=%s version=%s updated_at="2026-11-23" summary="%s"'
                % (p, kind, ver, summary)]
    for k, to, item, since in NEEDS:
        cmd += ["--add-need", 'key=%s to=%s item="%s" since=%s' % (k, to, item, since)]
    cmd += ["--status", STATUS]
    r = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print("[frag] ★★frag_write 失败 rc=%d★★\n%s" % (r.returncode, r.stderr[-2000:]))
        return r.returncode

    after = md5(FRAG)
    with open(os.path.join(LOG, "24_frag_md5_after.txt"), "w", encoding="utf-8") as fh:
        fh.write("%s  state/fragments/mech.yaml\n" % after)
    print("[frag] 写后 md5 = %s (写前 %s ⇒ 变了: %s)" % (after, before, after != before))

    # ---- 写后自证: 自己的 key 在不在 ----
    rc = verify_only()
    if rc != 0:
        print("[frag] ★★写后自证没过 ⇒ 停★★")
        return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
