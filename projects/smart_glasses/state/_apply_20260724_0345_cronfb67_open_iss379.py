#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0345_cronfb67_open_iss379.py
==============================================
main (项目总工) 的【开单 + 落 fixing】· ISS-379 (hw-lead) · 「板那一趟」`J_UART` 换官方 P1.27 THT land 的落位可行性

★**为什么开这个单 (★本机实读 + 实算 · 不抄任何 agent 报告★)**:
  ★① `python3 state/advance.py --json` 实跑 (2026-11-24 03:4x) ⇒ ★**`internal: []`** (★三个总工名下零 open 可派★)
  ★② 名额实读: `ISS-377` (mech-lead) = `fixing` 且其会话 `c3d27d29…` 03:41:45 仍在写 ⇒ ★**mech-lead 真在飞**
     · `ISS-378` (sw-lead) = `fixing` 且其交卷页 `HANDOFF/2026-11-24_sw-lead_ISS378_…md` (66,316 B @03:26) 已在盘
       ⇒ ★**sw-lead 是【已交卷待签收】的假在飞** ⇒ 本单不碰它
     · `ISS-376` (hw-lead) = ★**verified** (★main 03:29 签收闸 `state/_apply_20260724_0320_main_sign_iss376.py`★)
       ⇒ ★**hw-lead 槽位真空出来, 且名下零 open 项 ⇒ 不补新单则槽位空转 (队列对 HW 这条线真断线)★**
  ★③ 本单正题 = ★**ISS-376 的对称件**★: E-1 判定 `J_DEBUG`(1×4) 与 `J_UART`(1×2) 的 land pitch `0.50→1.27`
     要在【同一趟】做完 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 判据栏 + `HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` §2.1 第 ③ 行)
     ⇒ ★**ISS-376 只算了 `J_DEBUG` 那一半 ⇒ `J_UART` 这一半至今没人算过** ⇒ ★**「板只改一次」⇒ 必须现在算清楚** ★

★**纪律 (★铁律⑩-i★)**: ★**先落 `fixing` 再 spawn** ⇒ ★**兄弟 job 775d9893 的 `advance.py --json` 看不见本条
  ⇒ 撞车窗口 = 0** ★
★**边界**: ★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代拍 · 不自签台账**
  ⇒ ★**纯分析 / 作业包类 (不动板)** ⇒ 合「板只改一次」纪律 ① (先派纯分析/作业包类)★

★**本机实测事实 (main 2026-11-24 03:4x · 只读真板 + 只读官方 KiCad 10 库·可复跑)★**:
  ★`J_UART` 现位 = 2 个 SMD 焊盘 (pad attr=1 · 无孔) · 尺寸 `0.275 × 0.900` · pitch `0.50`
  ★· pad1 `(18.6400, 68.6000)` = `UART_TX` (netcode 129) · pad2 `(19.1400, 68.6000)` = `UART_RX` (netcode 130)
  ★· 封装原点 `(20.7400, 70.0000)` · crtyd bbox `(17.6900, 67.9500)-(23.7900, 72.0500)`
  ★· 目标 land 官方库件**已在盘**: `/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x02_P1.27mm_Vertical.kicad_mod` (3,074 B)
  ★· 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ⇒ 19 天逐字节未动
"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
DLOG = os.path.join(PROJ, "state/dispatch_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

BRIEF = "state/dispatch_briefs/ISS-379_hw_juart_land_fit.md"

TITLE = ("★★[★新主线·PCB 线·HW 侧·「板那一趟」] `J_UART` (1×2) 换官方 P1.27 THT land 的**落位可行性**穷举"
         "(现位放不下 ⇒ 挪哪 / 挪多大 / 挪完还剩什么)·纯分析+沙盒预演+新建闸·零写板] ★★"
         "【ISS-376 (`J_DEBUG` 1×4) 的对称件 · E-1 判定两件的 land pitch `0.50→1.27` 同一趟做完 ⇒ `J_UART` 这一半至今没人算过】★★")

DESC = (
    "★**题 (来源 = ISS-376 的对称面, 不是本 job 造的口径)★**: E-1 判定 `J_DEBUG`(1×4) 与 `J_UART`(1×2) 的 land pitch "
    "`0.50 → 1.27` 要在【同一趟】做完 (`HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` 判据栏 + "
    "`HW/PCB/BOARD_ONEPASS_S10_SWAP_SET_TRUTH.md` §2.1 第 ③ 行) ⇒ ★**ISS-376 只算了 `J_DEBUG` 那一半** ⇒ "
    "★**`J_UART` 这一半至今没人算过** ⇒ ★**「板只改一次」⇒ 这一半必须现在算清楚, 不能等画板时才发现放不下** ★ "
    "★**main 本机实读 (2026-11-24 03:4x · 只读真板 + 只读官方 KiCad 10 库 · 可复跑)★**: `J_UART` 现位 = 2 个 SMD 焊盘 "
    "(pad attr=1 · 无孔) · 尺寸 `0.275 × 0.900` · pitch `0.50` · pad1 `(18.6400, 68.6000)` = `UART_TX` (netcode 129) · "
    "pad2 `(19.1400, 68.6000)` = `UART_RX` (netcode 130) · 封装原点 `(20.7400, 70.0000)` · crtyd bbox "
    "`(17.6900, 67.9500)-(23.7900, 72.0500)` · 周边 5 邻居 crtyd: `U_TEMP` / `TP_UART` / `R_PU_I2CB_SDA` / `C_RST` / "
    "`SW_KEY_CAM` (坐标写在任务书里) · ★**目标 land 官方库件已在盘**: "
    "`/home/yuewuya/kicad/AppDir/share/kicad/footprints/Connector_PinHeader_1.27mm.pretty/PinHeader_1x02_P1.27mm_Vertical.kicad_mod` "
    "(3,074 B · 不用上网找这个件) ⇒ ★**板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / "
    "size `4940213` ⇒ 19 天逐字节未动** ★ "
    "★**本单要交四件**: ① 真相页 `HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md` (官方 land 实读 + 三朝向 pad 绝对坐标 + "
    "现位冲突表 + 落位可行域 + 代价账 + `UART_TX`/`UART_RX` pin 顺序契约 + 未决项) ② 交卷页 (B1~B6 六段, 六个 `##` 标题必须命中 gate_check 关键词) "
    "③ 新闸 `HW/check_juart_land_fit.py` (K0~K8 · 每条反向用例 · `--selftest` 末行 `ALL TESTS PASS` · ★**零挂链★**) ④ `hw.yaml` 分片登记 (只走 `state/frag_write.py`) ★"
)

NOTE = (
    "★2026-11-24 03:4x~03:5x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
    "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★ "
    "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
    "(★三个总工名下零 open 可派 ⇒ 队列对 HW 这条线真断线★) ② ★**ISS-376 (hw-lead) 已于 2026-11-24 03:29 由 main "
    "独立复核签收 verified** (★签收闸 `state/_apply_20260724_0320_main_sign_iss376.py` · fail-closed·全绿才签★) "
    "⇒ ★**hw-lead 槽位真空出来, 且名下零 open 项** ③ ★**ISS-377 (mech-lead) 会话 `c3d27d29…` 03:41:45 仍在写 ⇒ 真在飞, 不碰★ "
    "④ ★**ISS-378 (sw-lead) 交卷页已在盘 (66,316 B @03:26) ⇒ 已交卷待 main 签收, 不碰** ★ "
    "★**本单正题 = ISS-376 的对称件**: E-1 判定 `J_DEBUG`(1×4) 与 `J_UART`(1×2) 的 land pitch `0.50→1.27` 同一趟做完 "
    "⇒ ISS-376 只算了 `J_DEBUG` 那半 ⇒ `J_UART` 这半至今没人算过 ⇒ 「板只改一次」必须现在算清楚 ★ "
    "★**类别**: ★**纯分析 / 作业包类** (★老板 2026-11-17 00:43: 目标是绘制 PCB 图 ⇒ PCB 线可派, 但板只改一次 ⇒ 先派不动板的★) ★ "
    "★**边界**: 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml` · "
    "沙盒只落 `tmp/iss379/` + `logs/iss379/` ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-379_hw_juart_land_fit.md` "
    "(★命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0★) ★"
)

ISSUE = {
    "id": "ISS-379",
    "title": TITLE,
    "severity": "high",
    "source_blocker": "ISS-376",
    "source_agent": "main",
    "desc": DESC,
    "owner": "hw-lead",
    "reporter": "main",
    "raised": "2026-11-24",
    "due": "2026-11-26",
    "status": "fixing",
    "external": False,
    "need_keys": ["iss376_juart_swap_or_not", "iss376_juart_land_fit_domain"],
    "task_brief": open(os.path.join(PROJ, BRIEF), encoding="utf-8").read(),
    "note": NOTE,
    "dispatched_at": "2026-11-24",
}


def dump_entry(e):
    """★把一条 issue 序列化成 YAML 列表项 (0 缩进 '- id:' + 2 缩进字段)★"""
    txt = yaml.safe_dump({"issues": [e]}, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=100000)
    lines = txt.split("\n")
    assert lines[0].startswith("issues:"), lines[0]
    return "\n".join(lines[1:]).rstrip("\n") + "\n"


def main():
    raw = open(LOG, encoding="utf-8").read()
    doc = yaml.safe_load(raw)
    issues = doc.get("issues") or []
    ids = {i.get("id") for i in issues}
    if ISSUE["id"] in ids:
        print("★★%s 已存在 ⇒ 停下, 不重复开单" % ISSUE["id"])
        return 2

    # ---- 1 先落 issue_log (status=fixing, 铁律⑩-i) ----
    bak = LOG + ".bak_%s_cronfb67_open" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw.rstrip("\n") + "\n" + dump_entry(ISSUE))
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)

    doc2 = yaml.safe_load(open(LOG, encoding="utf-8"))
    got = {i.get("id"): i.get("status") for i in (doc2.get("issues") or [])}
    assert got.get("ISS-379") == "fixing", got.get("ISS-379")
    print("★ issue_log 已落: ISS-379=fixing (条数 %d → %d · 备份 %s)"
          % (len(issues), len(doc2.get("issues") or []), os.path.basename(bak)))

    # ---- 2 再落 dispatch_log (追加式) ----
    ddoc = yaml.safe_load(open(DLOG, encoding="utf-8"))
    assert isinstance(ddoc, list)
    bak2 = DLOG + ".bak_%s_cronfb67_open" % STAMP
    shutil.copy2(DLOG, bak2)
    ddoc.append({
        "issue": "ISS-379",
        "agent": "hw-lead",
        "at": "2026-11-24",
        "brief": TITLE,
        "brief_file": BRIEF,
        "job": ("cron fb67af40 (ARS45 队列自动派活) · ★本 job 步骤 2 的动作: ★**开单 + 直接落 fixing + spawn** "
                "(★铁律⑩-i 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) · "
                "★**开单依据 = ISS-376 于 03:29 被 main 独立复核签收 verified ⇒ hw-lead 槽位真空 + `advance.py --json` "
                "实跑 `internal: []` (三个总工名下零 open) ⇒ 队列对 HW 这条线真断线★** · "
                "★**本单 = ISS-376 的对称件 (`J_UART` 1×2 那一半) · 纯分析/作业包类 (零写板·零落表·零外发·不代拍) ⇒ "
                "合「板只改一次」纪律 ①★**"),
        "status_note": "★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则会挡住任何 job 给 hw-lead "
                        "再派活 ⇒ 零撞车窗口★",
    })
    tmp2 = DLOG + ".tmp_%d" % os.getpid()
    with open(tmp2, "w", encoding="utf-8") as f:
        yaml.safe_dump(ddoc, f, allow_unicode=True, sort_keys=False, default_flow_style=False, width=100000)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp2, DLOG)
    d2 = yaml.safe_load(open(DLOG, encoding="utf-8"))
    assert isinstance(d2, list) and d2[-1]["issue"] == "ISS-379"
    print("★ dispatch_log 已追加: ISS-379 (条数 %d → %d · 备份 %s)"
          % (len(ddoc) - 1, len(d2), os.path.basename(bak2)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
