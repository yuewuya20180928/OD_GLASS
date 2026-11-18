#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/_apply_20261117_0730_land274_276_redisp275_open277_278.py

★main 2026-11-17 07:3x (cron fb67af40 队列自动派活)★

★**为什么有这一趟**: ★三个总工名下 ISS-274/275/276 全停在 `fixing`, 而三个会话早已 `done` ⇒
  ★advance.py 的 in_flight 规则会把三个 agent 全部锁死 ⇒ 队列断线 ★
  ⇒ 本脚本 = ①**独立复验后落 verified** (274/276 全绿) ②**ISS-275 半交付 ⇒ 续做重派** ③**新开 2 条 PCB 线纯分析单** (277/278) ★

★**边界**: 只写 state/issue_log.yaml + state/dispatch_log.yaml; 不碰板/网表/脚表/BOM; 不写任何分片;
  不替老板拍板; 零外发。★
"""
import os, shutil, sys, yaml, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOG_P = os.path.join(HERE, "issue_log.yaml")
DL_P = os.path.join(HERE, "dispatch_log.yaml")
TODAY = "2026-11-17"

def main() -> int:
    # ---------- 备份 ----------
    bak = os.path.join(HERE, ".bak_iss277_278")
    os.makedirs(bak, exist_ok=True)
    for p in (LOG_P, DL_P):
        shutil.copy2(p, os.path.join(bak, os.path.basename(p) + ".bak_iss277_278"))

    log = yaml.safe_load(open(LOG_P, encoding="utf-8"))
    issues = log["issues"]
    by_id = {it["id"]: it for it in issues}

    def brief(name):
        p = os.path.join(HERE, "dispatch_briefs", name)
        return open(p, encoding="utf-8").read()

    changed = []

    # ---------- ① ISS-274 落 verified (main 本机独立复验) ----------
    i274 = by_id["ISS-274"]
    assert i274["status"] == "fixing", i274["status"]
    i274["status"] = "verified"
    i274["verify_by"] = "main"
    i274["verify_date"] = TODAY
    i274["fix_ref"] = "HANDOFF/2026-11-17_hw-lead_ISS274_板框坐标系口径收口.md"
    i274["verify_result"] = (
        "★main 2026-11-17 07:0x~07:2x 本机独立实跑复验 (不抄交卷报告)★ "
        "⇒ `python3 HW/check_board_frame_caliber.py` rc=0 (C1~C6 全过: 帧标签 20/20 = B160x100 · "
        "S6 已在目标位 19 / 不同 1 [R_SEL_D3_P] / 缺失 0 · 出界 0 · 重叠 0 · 异帧矩形压 SoM 焊盘 "
        "J_SOM_P3×10 + J_SOM_P1×56 已机器化留存 · 受保护 5 件 md5 全同) "
        "⇒ `--selftest` rc=0 (反向 8 条, 失败 0 条) "
        "⇒ 受保护 5 件 md5 实测 = 基线 (板 611b869e… / .kicad_pro 3e504d2b… / 网表 e06c1dd6… / "
        "脚表 287e7861… / BOM 94642d07…) ⇒ 板零变化, 仍不许投板 "
        "⇒ 交付物 6 件全在盘 (HW/PCB/BOARD_FRAME_CALIBER.md 19.2KB · HW/check_board_frame_caliber.py 39.1KB · "
        "交卷单 33.7KB · 作业包 §3-S6 追加式订正 · LAYOUT_FIX_SPEC §3 追加式订正 · 分片 3 claim) "
        "⇒ 注: 交卷单自报的 U-274-5 (C2 字面 == 改为 ⊆ + 位置白名单) 已由 hw-lead 显式报备, main 认可; "
        "U-274-2 (P7 画哪一块) 与 U-274-6 (帧 id 跨域统一) 仍归老板/main, 不在本单判定范围"
    )
    i274["note"] = (i274.get("note") or "") + (
        " | 2026-11-17 07:2x (cron fb67af40) ★main 独立复验通过 ⇒ 落 verified★ "
        "⇒ 依据 = 本机实跑 check_board_frame_caliber.py rc=0 + --selftest 8/8 + 受保护 5 件 md5 与基线逐字节一致 "
        "⇒ hw-lead 名额已释放 (下一轮可接新单)"
    )
    changed.append("ISS-274 fixing → verified")

    # ---------- ② ISS-276 落 verified ----------
    i276 = by_id["ISS-276"]
    assert i276["status"] == "fixing", i276["status"]
    i276["status"] = "verified"
    i276["verify_by"] = "main"
    i276["verify_date"] = TODAY
    i276["fix_ref"] = "HANDOFF/2026-11-17_mech-lead_ISS276_MECH侧坐标系归一与三条need收口.md"
    i276["verify_result"] = (
        "★main 2026-11-17 07:1x 本机独立实跑复验 (不抄交卷报告)★ "
        "⇒ `python3 MECH/check_board_frame_coords.py` rc=0 (四项全过) "
        "⇒ `--selftest` rc=0 (反向 6 条, 含『真件 5 件 md5 跑完自检后仍逐字节不变』) "
        "⇒ `MECH/board_port_opening_s6_check.py --json` rc=0 · `MECH/jd_y0_feasibility.py --selftest` rc=0 "
        "⇒ `MECH/check_demo_struct_truth.py` rc=0 (23/23) + `--selftest` rc=0 (21/21) "
        "⇒ 受保护 5 件 md5 实测 = 基线 ⇒ 板零变化 "
        "⇒ 交付物全在盘 (MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md 25.8KB · MECH/check_board_frame_coords.py 46.3KB · "
        "交卷单 38.4KB · 分片 3 claim) "
        "⇒ 注: 交卷单报的『另两条 mech→main need 仍 pending+foreign=1 ⇒ 需 main 代录』★**main 已于 07:14 代录闭合**★ "
        "(pm.yaml 三条 answer: iss273_mech_ledger_format_contract / iss273_mech_ledger_itself_anchor / "
        "iss275_sw_ledger_format_contract ⇒ merge 后三条 need 全部 answered) ⇒ mech-lead 名额已释放"
    )
    i276["note"] = (i276.get("note") or "") + (
        " | 2026-11-17 07:2x (cron fb67af40) ★main 独立复验通过 ⇒ 落 verified★ "
        "⇒ 依据 = 本机实跑 check_board_frame_coords.py rc=0 + --selftest 6/6 + check_demo_struct_truth 23/23 & 21/21 "
        "⇒ 另两条 mech→main need 已由 main 07:14 在 pm.yaml 代录闭合 (契约落点 = HW 侧落表作业包模板; 台账本体不加锚) "
        "⇒ mech-lead 名额已释放"
    )
    changed.append("ISS-276 fixing → verified")

    # ---------- ③ ISS-275 半交付 ⇒ 续做重派 (状态仍 fixing) ----------
    i275 = by_id["ISS-275"]
    assert i275["status"] == "fixing", i275["status"]
    i275["dispatched_at"] = TODAY
    i275["note"] = (i275.get("note") or "") + (
        " | 2026-11-17 07:3x (cron fb67af40) ★★续做重派 (第 2 次)★★ "
        "⇒ 派单后 sw-lead 会话在 compaction 处断掉 (status=done 但最后一屏停在『现在把 R6 实现细化』), "
        "★**半交付实测**★: ✅ 已落盘且可用的部分 = `SW/tools/check_demo_panel_spec.py` 的 R6 判决源改造 "
        "(main 与基线 e14014aac 逐行 diff ⇒ **只动了 R6 那一段 + 新增 3 个 helper (sw_ledger_records / sw_ledger_state / "
        "sw_ledger_canonical_text), R1~R5/R7 一字未动**; 主闸 rc=0 · `--selftest` rc=0 且 **16/16 未掉** (基线也是 16/16, "
        "★反向用例一条没删★) · `SW/tools/timing_check.py` rc=0 (71/71) · `HW/check_step1_parts_spec.py` rc=0 (8/8)) "
        "⇒ ❌ **仍缺 5 件**: ① `SW/tools/check_demo_panel_spec_r6_selftest.py` (R1~R6 专项反向用例, 独立文件) **不存在** "
        "② `SW/SW_MD5_BASELINE_LEDGER.md` **一字未改** (mtime 仍 11-16 22:02 ⇒ §1 角色声明 + §3 留痕 未追加) "
        "③ 交卷单 B1~B6 全是『(施工中 · 待填)』占位 ④ 分片缺 2 claim + 3 artifact + status (只有给 main 的 1 条 need) "
        "⑤ R1/R3/R4/R5a/R5b 这 5 条专项反向用例未落地 (现只有 REV-13/14/15 混在主脚本里, ★brief 明确要求独立成文件★) "
        "⇒ ★**判定: 不是僵尸空转, 是真活做了一半 ⇒ 续做, 不重做**★ "
        "⇒ ★**已代 main 把三条落表台账契约 need 闭合** (pm.yaml answer: iss275_sw_ledger_format_contract ⇒ "
        "硬格式 = 单号|文件名|改前 md5|改后 md5 四项同行, 落点 = HW 侧落表作业包模板)★"
    )
    changed.append("ISS-275 续做重派 (状态仍 fixing, 剩余 5 件已列明)")

    # ---------- ④ 新开 ISS-277 (hw-lead) ----------
    assert "ISS-277" not in by_id
    issues.append({
        "id": "ISS-277",
        "title": "★★[主线内·PCB 线·纯分析+作业包订正+机器闸类] ★★「板只改一次」那一趟的【板侧漏项覆盖度收口】★★ ⇒ ★**作业包 v3 是 11-17 01:2x 的, 那之后 ISS-239/241/244/247/276 又各自发现了板侧项, 作业包一条没跟 ⇒ 且没有任何一道闸能发现「某项只在交卷单里、没进作业包」** ★ ⇒ ★**⇒ 那一趟漏做一项 = 板 md5 变第二次 = 留证链/Gerber/投产包/盖章全白跑** ★",
        "severity": "high",
        "source_blocker": None,
        "source_agent": "main",
        "desc": (
            "★main 2026-11-17 07:0x~07:3x 本机实读 + 实跑 (不抄交卷报告)★\n"
            "★**① 作业包 v3 (ISS-266, 11-17 01:2x, 381 行) 之后又出了 6 个单, 板侧新发现未并回** ★:\n"
            "  · ISS-241: F-1 `D_ESD_CAM` 器件脚接反 (板 pad 序 GND/信号 vs 器件 I/O/GND ⇒ CSI lane 无 ESD) · "
            "F-2 `Q_AND` pad 序 D/S/G vs 库 G/S/D ⇒ 硬件 AND 变 OR · `D_ESD_TC` = SP0503BAHT ⇒ 充电板 footprint 须 4 焊盘\n"
            "  · ISS-244: 三条实物级 P0 (`Q_PG` 角色错 ⇒ 开不了机 / `Q_AND` 栅漏对调 / `D_ESD_CAM` 接反) · "
            "落表残项 8 行 (`D_CHG_LED`/`D_LED_G`/`D_LED_R`/`SW_BOOT`/`SW_KEY_PWR`/`SW_KEY_VM`/`SW_KEY_VP`/`SW_RST`) "
            "⇒ 其中 4 键 + 2 LED 的 land 必须同批重画\n"
            "  · ISS-247: F2 `J_CHG` 位号消歧 (只登记不做) · F3 板侧 43 颗 DNP 零标记 (≈作业包 §3-S7, 待核对)\n"
            "  · ISS-239: `U_LDO_S28.pin3` A/B 两案 ⇒ 若走 A 案, 板必须补 pad3\n"
            "  · ISS-274/276: S6 真实位移口径 + 检修口/调试口必须拆两条 + 座体高度 [0数据] ⇒ 作业包未收\n"
            "★**② 现状基线 (main 07:0x~07:2x 实跑)** ★: 板 Edge.Cuts 160.10×100.10 · 8 层 · 186 封装 · md5 611b869e… "
            "· unconnected=45 · DRC 违规 0 · 网表 480 / 板上带网 482 · 缺失 0 · 同号异网 0 · "
            "★多余 2 焊盘 `C_VBUS_GND` pad1=GND / pad2=VBUS_5V_CHG★ · `--expect-resolved` 仍 18 条 · Gerber 32 个齐\n"
            "★**③ 作业包 §3-S2 只写「拿掉 `C_VBUS_GND`」, 没写这 2 个焊盘当下各挂什么网 ⇒ 「只写了动作、没写现状」的行要补** ★\n"
            "★**④ 核心判据必须是【覆盖度】**: 从 6 份来源交卷单反向 grep 出板侧项标记 ⇒ 每条都必须在清单里 ⇒ "
            "漏一条即红; 另加【现状一致】(清单里的 [实测] 值必须与盘面实测一致 ⇒ 盘面变了清单不跟 = 当场红) ⇒ "
            "★否则清单就是第二份过期文档★\n"
            "★**交付**: ① 新建 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` (板侧项全集 · 9 字段逐条表 + 机器可读 JSON) "
            "② 追加式订正 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (§3-S0 漏项并入表 + §4 闸 + §1 现状基线追加, 老字不删) "
            "③ 新建 `HW/check_onepass_preflight_coverage.py` (P1 字段齐 / P2 归属步 S1~S13 / P3 判据命令真存在 / "
            "P4 覆盖度 / P5 现状一致 / P6 保护件 md5 + ≥6 条反向 selftest) ④ 交卷单 B1~B6 ⑤ 分片\n"
            "★**类别**: 内部活 · PCB 线 · 纯分析 + 作业包订正 + 机器闸类 · **零写板 · 零落表 · 零改判据阈值** ⇒ "
            "**不是老板级拍板** ★"
        ),
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "2026-11-17 07:3x (cron fb67af40 队列自动派活) 新开 ★**依据 = main 本轮 07:0x~07:3x 本机实跑 + "
            "实读作业包/交卷单** ★\n"
            "⇒ ★**任务书 `state/dispatch_briefs/ISS-277_hw_onepass_preflight_coverage.md`** ★\n"
            "★**hw-lead 名下本轮无 open 队列 (ISS-274 已于 07:2x 落 verified ⇒ 真空; 会话实测无 running) ⇒ "
            "本单是本轮给 hw-lead 的活** ★\n"
            "★**为什么排第一**: ★**它是「板只改一次」那一趟开工前的【覆盖度保险】⇒ 漏做一项 = 板 md5 变第二次** ★\n"
            "★**边界**: 零写板 · 零落表 · 零改网表/脚表/BOM · 零改既有判据阈值 · 零开新布线臂 · 只许新增 HW/ 文件 + "
            "追加式订正作业包 · 不写 MECH/SW 分片 · 不替老板拍板 · 零外发 ★"
        ),
        "dispatched_at": None,
        "task_brief": brief("ISS-277_hw_onepass_preflight_coverage.md"),
    })
    changed.append("ISS-277 新开 (owner=hw-lead, status=open)")

    # ---------- ⑤ 新开 ISS-278 (mech-lead) ----------
    assert "ISS-278" not in by_id
    issues.append({
        "id": "ISS-278",
        "title": "★★[主线内·MECH 侧·纯分析+规格页订正+机器闸类] ★★「板只改一次」那一趟的【MECH 侧板侧输入收口】★★ ⇒ ★**ISS-276 已把坐标归一到 B160x100 帧, 但 4 条板侧输入还悬着: 检修口/调试口必须拆两条 (盘上相距 123.6mm, 合并差 116.017mm) / 座体真实高度 [0数据] ⇒ 开口 Y 一切数建在 2.54 假设上 / LED 光孔 [0数据] / 连接器参数与落表板对不上** ★ ⇒ ★**⇒ 照现状开那一趟 = 开口位置按合并的错值写 = 板改第二次** ★",
        "severity": "high",
        "source_blocker": None,
        "source_agent": "main",
        "desc": (
            "★main 2026-11-17 07:0x~07:3x 本机实读板 + 实读 ISS-276 交卷单 (不抄交卷报告)★\n"
            "★**① 检修口/调试口必须拆两条** ★: ISS-276 交卷单原文「合并开口不可行 — 必须清空宽 126.218 vs 开口 10.20 ⇒ "
            "差 116.017mm」; 盘上实测 `J_DEBUG`@(144.30,58.00) 与 `J_UART`@(20.74,70.00) 相距 **123.6mm** ⇒ "
            "★合并是几何上不可能, 不是「还没想好」★ ⇒ 现在 (以及 §3-S6 引用链) 仍是合并写法 ⇒ 照抄 = 开口位置错\n"
            "★**② 座体真实高度 = [0数据]** ★: 现值 2.54 是假设 ⇒ 开口 Y 一切数都建在假设上 ⇒ 本机量不到 (打印/量测全 0 数据) ⇒ "
            "★**不许把 2.54 当事实继续传, 也不许挂成等外部回复** ⇒ 降级方案 = 【参数式 f(h) + h 三档 + 板那一趟按公式取值】★\n"
            "★**③ `D_LED_G` 出光侧结构光孔 = [0数据]** ★: 须给有孔/无孔两假设下的可放行空间 + 对 `LED_G_D` 走线 93.49mm 的影响\n"
            "★**④ `demo_mainboard_params.json` 连接器参数与落表板对不上** ★: ISS-276 登记为 HW 域外 ⇒ 本单交对照表 ⇒ "
            "**交 main 转 hw-lead (ISS-277 同批在做板侧清单) ⇒ 一个字不许改 HW/**\n"
            "★**⑤ ISS-276 已完成的部分不许重做** ★: 归一页 25.8KB · 新闸 46.3KB (rc=0 四项全过 + selftest 6/6) · 交卷单 38.4KB · "
            "帧 id 已与 hw-lead 对齐 (B160x100 / F30A / P60x15)\n"
            "★**⑥ 没有一道闸检查「MECH 侧板侧输入是否都成规格」** ★ ⇒ 本单补: M1 帧标签 (帧 id ∈ {B160x100,F30A,P60x15}) / "
            "M2 两条开口【分别】不压 SoM 座 / M3 座高参数式三档自洽 / M4 判据命令真存在 / M5 保护件 md5 + ≥5 条反向 selftest\n"
            "★**交付**: ① 新建 `MECH/BOARD_ONEPASS_MECH_SYNC.md` (8 字段逐条表 + 机器可读 JSON + MECH→HW 输入清单) "
            "② 追加式订正 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` (§3b 两条开口 / §4b 座高参数化 / §6b 光孔两假设 / "
            "§7b 连接器对照表 / §8 S6 认领句加一条, 老字不删) ③ 新建 `MECH/check_onepass_mech_sync.py` ④ 交卷单 B1~B6 ⑤ 分片\n"
            "★**类别**: 内部活 · MECH 侧 · 纯分析 + 规格页订正 + 机器闸类 · **零写板 · 零落表 · 零改既有 MECH 判据脚本** ⇒ "
            "**不是老板级拍板** ★"
        ),
        "owner": "mech-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": (
            "2026-11-17 07:3x (cron fb67af40 队列自动派活) 新开 ★**依据 = main 本轮 07:0x~07:3x 本机实读板 + "
            "实读 ISS-276 交卷单** ★\n"
            "⇒ ★**任务书 `state/dispatch_briefs/ISS-278_mech_onepass_sync.md`** ★\n"
            "★**mech-lead 名下本轮无 open 队列 (ISS-276 已于 07:2x 落 verified ⇒ 真空; 会话实测无 running) ⇒ "
            "本单是本轮给 mech-lead 的活** ★\n"
            "★**与 ISS-277 (hw-lead) 的分界**: ★**277 = HW 侧板侧项全集 + 覆盖度闸 · 278 = MECH 侧板侧输入规格 + 闸** ★ "
            "⇒ ★**两边各写各的域, 只交叉引用, 不许改对方的文件** ★\n"
            "★**边界**: 零写板 · 零落表 · 零改既有 MECH 判据脚本 · 零改 HW/ · 只写自己分片 · 零外发 · "
            "★**不许把「座体高度 / 光孔 / 亮度档」挂成等外部回复** ★"
        ),
        "dispatched_at": None,
        "task_brief": brief("ISS-278_mech_onepass_sync.md"),
    })
    changed.append("ISS-278 新开 (owner=mech-lead, status=open)")

    # ---------- 落盘 ----------
    with open(LOG_P, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)

    dl = yaml.safe_load(open(DL_P, encoding="utf-8")) if os.path.exists(DL_P) else {"dispatches": []}
    dl.setdefault("dispatches", []).extend([
        {"issue": "ISS-274", "agent": "hw-lead", "at": TODAY,
         "brief": "★main 07:2x 独立复验 rc=0 + selftest 8/8 ⇒ 落 verified (释放 hw-lead 名额)"},
        {"issue": "ISS-275", "agent": "sw-lead", "at": TODAY,
         "brief": "★main 07:3x 半交付实测 ⇒ 续做重派第 2 次 (R6 改造已在盘且门禁绿, 剩 5 件: 独立 selftest 文件 / "
                  "台账副本追加 / 交卷单 B1~B6 / 分片 claims+artifacts+status / R1~R6 专项 5 条反向用例)"},
        {"issue": "ISS-276", "agent": "mech-lead", "at": TODAY,
         "brief": "★main 07:2x 独立复验 rc=0 + selftest 6/6 ⇒ 落 verified (释放 mech-lead 名额)"},
    ])
    with open(DL_P, "w", encoding="utf-8") as f:
        yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)

    print("=== 已落 ===")
    for c in changed:
        print(" ·", c)
    print("备份 →", bak)
    return 0

if __name__ == "__main__":
    sys.exit(main())
