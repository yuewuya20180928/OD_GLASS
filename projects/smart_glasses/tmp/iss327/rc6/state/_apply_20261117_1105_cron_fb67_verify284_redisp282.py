#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cron fb67af40「ARS45 队列自动派活」 2026-11-17 11:0x (main / moli)

★(1) ISS-284 (sw-lead · P10 方案② 落地) ⇒ 独立复验 ⇒ 落 `verified` (verify_by=main)★
★(2) ISS-282 (hw-lead · FSIN_OUT 根因订正) ⇒ 登记【续做重派】到 dispatch_log (★status 仍是 fixing, 不动★)★

★**纪律**: 只动 state/issue_log.yaml + state/dispatch_log.yaml 两个文件
★**多行标量一律走「yaml 取旧值 → 拼新值 → 单行 json 写回 → 全量复核」**★
"""
import json
import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
BAK_LOG = LOG + ".bak_20261117_1105_cron_fb67_verify284"
BAK_DLOG = DLOG + ".bak_20261117_1105_cron_fb67_redisp282"
TODAY = "2026-11-17"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


VERIFY_284 = (
    "★**main 2026-11-17 10:5x~11:0x 独立复验 (★cron fb67af40「队列自动派活」· 自己实跑, 不抄交卷报告★)**: "
    "① `SW/tools/check_demo_panel_spec.py` ⇒ **rc=0** (R1~R7 全绿 · ★R6 受保护真源三方对账 = 锚点 ↔ 落表台账 ↔ 盘上真源 一致★) "
    "② `--selftest` ⇒ **rc=0 · 22/22** (★原 16 条一条没删 + 新增 REV-16~REV-21 六条反向用例全抓到★) "
    "③ `state/merge.py` ⇒ rc=0 · `state/gate_check.py` ⇒ rc=0 (★Q1 18/18★) "
    "④ 受保护件: 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ★**逐字节不变**★; 网表/脚表/BOM = 09:58:16 A1+A2 落表后的合法新值 "
    "`2f17650c…` / `6ea65fec…` / `ea5f4f58…` (★落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 L1270-L1272 有正式登记 ⇒ **不是未登记改动**★) "
    "⑤ 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS284_hard_protected合法改板机制.md` 22592 B (B1~B6 齐全) · `state/fragments/sw.yaml` 8 处 ISS-284 记录 "
    "(artifact/claim/answer/need 齐全 · 走 frag_write.py 原子写) "
    "⑥ ★**两处现红归因已查清**: `SW/tools/timing_check.py` rc=1 (68/71) 与 `HW/check_onepass_preflight_coverage.py` rc=1 "
    "(P5 清单现状过期 + P6 基线 md5 过期) = ★**09:58:16 落表的直接后果, 早于本单开工 (10:18)★** ⇒ 已由 main 10:4x 追加进 ISS-283 收口 "
    "⇒ ★**不是本单造成**★ · ★**判据方向确认一个字没变**: 盘上 ≠ 链头 ⇒ 红; fail-closed 三条 (链头不唯一/链断/链头无单号) 一条没动; "
    "网表/脚表链头读数前后逐字相同 ⇒ ISS-275 成果没被碰 ★ "
    "⑦ ★**机制 essence**: 「一个字段两个值」= 单号 + 文件名 + 改前 md5 + 改后 md5 四件捆一个原子映射 + 落表台账同一行可查 ⇒ 「只改 md5 凑绿」被堵死 "
    "⇒ ★**留痕 need `sw_legal_reboard_landing_row_on_board_trip` = 出板那一趟往台账写两行 (板一行 + `.kicad_pro` 一行「逐字节不变」· 同一单号)★**"
)

NOTE_284_ADD = (
    " ★**2026-11-17 11:0x (cron fb67af40 队列自动派活) 独立复验落 verified** ⇒ ★**P10 方案② 已落地**: "
    "「一个字段两个值」原子记录 (单号/文件名/改前 md5/改后 md5) + 落表台账可查 ⇒ 「只改 md5 凑绿」这条路被堵死 ⇒ "
    "★**出板那一趟必做**: 往落表台账写两行 (板 + `.kicad_pro` · 同一单号) ⇒ SW 侧 R6 即绿★"
)

CONT_282 = (
    "★**续做重派 (★10:22 那一趟会话被网关重载/超时打断 ⇒ 盘上已有 3/4 件交付物, 但交卷单只有骨架 ⇒ 未交卷★)** ⇒ "
    "★**从盘上现状继续, 不要从零重做**★\n\n"
    "★**main 10:5x~11:0x 本机实测的盘上现状 (逐条可复核)★**:\n"
    "- ✅ `HW/PCB/FSIN_OUT_ROOTCAUSE.md` 20128 B (10:16) 已在盘\n"
    "- ✅ `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 67726 B (10:11) 已在盘 (★老 S8 行 L387 逐字仍在, 订正行 L388 在其下★)\n"
    "- ✅ `HW/check_fsin_rootcause.py` 39479 B (10:19) 已在盘 (★D1/D4 绿★)\n"
    "- ⚠️ `HANDOFF/2026-11-17_hw-lead_ISS282_FSIN_OUT根因订正.md` ★**只有 2617 B 骨架 (B1~B6 全是「待填」)★**\n"
    "- ⚠️ `state/fragments/hw.yaml` ★**无 ISS-282 记录 (grep = 0) ⇒ 分片没写**★\n\n"
    "★**main 实跑闸 ⇒ 3 项不通过 (这就是你要收的最后三件)★**:\n"
    "- ❌ ★**D2 / D3 = 「读不到板面 / 读不到那两个焊盘」⇒ main 已定位根因: 是闸自己代码的 bug, 不是板不在**★: "
    "`HW/check_fsin_rootcause.py` L337 `_seg_rect_dist` 里 ★**`NameError: name 'e' is not defined`★** (异常被吞掉 ⇒ 报成「读不到板面」) "
    "⇒ ★**修那一处 (不许改判据方向, 只修变量名)★**\n"
    "- ⚠️ ★**D2/D3 的距离口径要统一**: 订正页写 1.1500 / 1.3528 mm (★边缘距★) 而闸重算得 1.300000 / 1.350000 mm (★中心距★) "
    "⇒ ★**两者都 ≫ 0.45 ⇒ 结论一字不变, 但判据与页必须同一口径, 否则 D2 永远红**★\n"
    "- ❌ ★**D5 = 网表/脚表/BOM 三个 md5 不在【基线 ∪ 落表后】集合里 ⇒ 根因 = 集合过期, 不是有人偷改**★: "
    "当前真值 `2f17650c…` / `6ea65fec…` / `ea5f4f58…` ★**在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 L1270-L1272 有正式登记** "
    "(★老板 09:49 拍板 → main 09:58:16 A1+A2 落表★) ⇒ ★**修法 = 把这三个登记值加进闸的允许集合并引台账行号 (是【登记】不是【放宽】, "
    "其余 fail-closed 一条不许动)★**\n"
    "- ⇒ ★**`--selftest` 现在 8/10** (★差的两条 ⑨⑩ 就是 D2/D3/D5 这三处 ⇒ 修完应到 10/10★)\n\n"
    "★**★另外: 任务书 ⑤ 验收第 3 条 `HW/check_onepass_preflight_coverage.py` 现红 (P5 清单现状过期 + P6 基线 md5 过期) "
    "= 同一处落表的后遗症 (★main 10:4x 已追加进 ISS-283, 但本单验收要它 rc=0 ⇒ 本单顺手收口★): "
    "P5 两条 current_state 改成盘面实测值 + P6 三个基线 md5 改成刚落表真值并引台账 §16.2**★\n\n"
    "★**交卷要交齐**: ① 订正页 ② 作业包追加式订正 (★老字零删除★) ③ 机器闸 (D1~D5 + selftest ≥6) ④ 交卷单 B1~B6 全填 (★不是骨架★) "
    "⑤ `state/fragments/hw.yaml` 分片 (走 `state/frag_write.py` 原子写 · grep 校验) ⑥ ★**任务书 ⑤ 那 9 条验收命令逐条贴原样 rc**★\n\n"
    "★**纪律 (不变)**: ★**零写板 · 零落表 · 零跑布线臂 · 零改网表/脚表/BOM · 零改既有判据阈值 · 不替老板拍板 · 不自签 issue_log · 零外发**★"
)


def dump_block(d) -> str:
    lines = ["- id: %s" % d["id"]]
    for k, v in d.items():
        if k == "id":
            continue
        if v is None:
            lines.append("  %s: null" % k)
        elif isinstance(v, bool):
            lines.append("  %s: %s" % (k, "true" if v else "false"))
        elif isinstance(v, (int, float)):
            lines.append("  %s: %s" % (k, v))
        else:
            lines.append("  %s: %s" % (k, q(v)))
    return "\n".join(lines)


def main() -> int:
    raw = open(LOG, encoding="utf-8").read()
    lines = raw.split("\n")
    # ── 找 ISS-284 块 ──
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("- id: ISS-284"):
            start = i
            break
    if start is None:
        print("❌ 找不到 ISS-284 块")
        return 2
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("- id: "):
            end = j
            break
    block_txt = "\n".join(lines[start:end])
    blk = yaml.safe_load(block_txt)
    if isinstance(blk, list) and len(blk) == 1:      # ★块本身是列表项 ⇒ safe_load 给 list★
        blk = blk[0]
    if not isinstance(blk, dict) or blk.get("id") != "ISS-284":
        print("❌ ISS-284 块解析失败")
        return 2
    print("→ ISS-284 旧 status =", blk.get("status"), "· verify_by =", blk.get("verify_by"))

    blk["status"] = "verified"
    blk["verify_by"] = "main"
    blk["verify_result"] = "pass"
    blk["verify_date"] = TODAY
    blk["verify_note"] = VERIFY_284
    blk["note"] = (blk.get("note") or "") + NOTE_284_ADD

    new_block = dump_block(blk).split("\n")
    new_lines = lines[:start] + new_block + lines[end:]
    new_raw = "\n".join(new_lines)

    # ── 全量复核 (写盘前) ──
    chk = yaml.safe_load(new_raw) or {}
    cblk = {it["id"]: it for it in (chk.get("issues") or [])}
    assert cblk["ISS-284"]["status"] == "verified", "ISS-284 status 没落上"
    assert cblk["ISS-284"]["verify_by"] == "main", "verify_by 没落上"
    assert cblk["ISS-284"]["verify_result"] == "pass", "verify_result 没落上"
    assert cblk["ISS-284"]["verify_date"] == TODAY, "verify_date 没落上"
    assert len(chk["issues"]) == len((yaml.safe_load(raw) or {}).get("issues") or []), "issue 条数变了"

    shutil.copy2(LOG, BAK_LOG)
    open(LOG, "w", encoding="utf-8").write(new_raw)
    print("✅ issue_log.yaml 已更新 (ISS-284 → verified) · 备份:", os.path.basename(BAK_LOG))

    # ── dispatch_log: 追加两条 ──
    d_raw = open(DLOG, encoding="utf-8").read()
    add = ""
    add += "- issue: ISS-284\n  agent: sw-lead\n  at: '%s'\n  brief: %s\n  note: %s\n" % (
        TODAY,
        q("★**独立复验落 verified** (★main 2026-11-17 11:0x · cron fb67af40 队列自动派活★) · "
          "rc: check_demo_panel_spec rc=0 · --selftest rc=0 22/22 · merge rc=0 · gate_check rc=0 (Q1 18/18) · "
          "受保护板 611b869e… / .kicad_pro 3e504d2b… 逐字节不变"),
        q(VERIFY_284),
    )
    add += "- issue: ISS-282\n  agent: hw-lead\n  at: '%s'\n  brief: %s\n  note: %s\n" % (
        TODAY,
        q(CONT_282),
        q("★**续做重派** · ★**完整任务书全文 = `state/dispatch_briefs/ISS-282_hw_fsin_rootcause_correction.md` (16885 B · 与 09:5x 首次派活同一份) "
          "⇒ 第一件事先 cat 全文★** · ★**前一趟会话 = `agent:hw-lead:subagent:169ee40f` (10:22 结束 · abortedLastRun=true · "
          "最后一条 = 「Diagnosed: my landing-ledger window matched an older section ... Let me fix both.」⇒ 中途被打断, 未交卷★**"),
    )
    d_new = d_raw.rstrip("\n") + "\n" + add
    d_chk = yaml.safe_load(d_new) or {}
    assert len(d_chk["dispatches"]) == len((yaml.safe_load(d_raw) or {}).get("dispatches") or []) + 2, "dispatch 条数不对"
    shutil.copy2(DLOG, BAK_DLOG)
    open(DLOG, "w", encoding="utf-8").write(d_new)
    print("✅ dispatch_log.yaml 已追加 2 条 (ISS-284 verified + ISS-282 续做重派) · 备份:", os.path.basename(BAK_DLOG))
    return 0


if __name__ == "__main__":
    sys.exit(main())
