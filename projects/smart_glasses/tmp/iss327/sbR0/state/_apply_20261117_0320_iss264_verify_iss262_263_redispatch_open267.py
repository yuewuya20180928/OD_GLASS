#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_0320_iss264_verify_iss262_263_redispatch_open267.py
★main (moli) 派活落账 · 2026-11-17 03:20 (cron fb67af40 队列自动派活 · 第 3 趟)★

★★**本轮实跑结论 (★全部自己实跑, 不是抄任何交卷报告★)★★ ★★
· ★**`python3 state/advance.py --json` ⇒ internal = []** (★A 段空★)
  · 原因 = ★**三个总工名下各卡一条 status=fixing, 而它们的会话全已死 (★僵尸 fixing★)** ★
· ★**会话实测 (sessions_list)**: ★**上一趟 (run 6164249d) 起的 3 条子会话全部 ended★**
  · `agent:hw-lead:subagent:7922c2a0` (ISS-262) · runtimeMs **1410578 (≈23.5 min)** · status=done · abortedLastRun=true
    ⇒ transcript 末尾 `openclaw:prompt-error` = **"This operation was aborted"** (★父 cron 收摊把子会话一起 abort★)
    ⇒ ★**盘上产物 = 只有交卷单骨架 1034 B (B1~B6 全是 `_(施工中)_`) + 零脚本 + 零日志 + 分片 grep iss262 = 0★**
  · `agent:sw-lead:subagent:b765bfb4` (ISS-263) · runtimeMs **1332293 (≈22 min)** · status=done · abortedLastRun=true
    ⇒ ★**技术活干完了 (toolkit 已装 / rk3572 config rc=0 / 3 次转换全 rc=0 / 门禁 G1·G2·G3 全 rc=0), 但交卷单仍是骨架 (B1~B6 全 `(填)`) + 分片 grep iss263 = 0★**
  · `agent:mech-lead:subagent:4631cffa` (ISS-264) · runtimeMs 710181 (≈11.8 min) · status=done · abortedLastRun=false
    ⇒ ★**交卷完成 (HANDOFF 77.6 KB + 分片 grep iss264 = 10)★**
· ★**ISS-264 main 本机独立复验 (★自己实跑, 不抄交卷报告★)**:
  · `python3 MECH/service_port_check.py` ⇒ **rc=0 · 57/57 · FAIL 0**
  · `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=0 · 23/23 · FAIL 0**
  · `python3 MECH/cavity_recalc_check.py` ⇒ **rc=0 · 23/23**
  · `python3 state/merge.py` ⇒ **rc=0** (★产出 392 · 阻塞 43 · 未闭合需求 229 · 冲突 0★)
  · `python3 state/gate_check.py` ⇒ **rc=0 · Q1 18/18**
  · ★**3 个受保护脚本 md5 与 mech-lead 自报完全一致**: `4ae5827e986f1aebb108c5aa2a475074` (check_demo_struct_truth.py)
    / `c4bf9151dd59826fb2320c34e8afbd0f` (cavity_recalc_check.py) / `db58ff6a2afc28b8bf517e3c57c56bc1` (service_port_check.py)
  · ★**受保护 5 件 md5 逐字节不变**: 网表 `e06c1dd6…` · 脚表 `287e7861…` · BOM `94642d07…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…`
  ⇒ ★**⇒ 本单 = ISS-264 落 verified (★含 mech-lead 点名要 main 登记的 3 个 md5★)★★

★★**本脚本做的事 (边界写死)★★ ★★
· ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` (★flock + 锁内重读 + tmp/os.replace 原子写★)★**
· ★**ISS-264: fixing → verified** (★fix_ref / verify_by=main / verify_result=pass / verify_date=2026-11-17 / verify_note=本机复验原文★)
  · ★**并把 mech-lead 点名要 main 登记的 3 个 md5 写进 note (★那是 issue_log 地界, 别人不能写★)★**
· ★**ISS-262 / ISS-263: 保持 fixing** (★本来就是 fixing, 本轮是同一单续做, 不重复标★)
  · ★**只追加 note (★僵尸实况 + 本趟派发时刻 + 本趟 brief 路径★) + 更新 dispatched_at★**
· ★**新开 ISS-267 (owner=mech-lead, status=open)**: ★**纯分析类内部活 (检修口/调试口板侧开口约束表 + jd_y0 候选枚举 + 框口径冲突清单)★
  · ★**为什么新开**: ★**三个总工里只有 mech-lead 这趟交完了 (ISS-264 verified) ⇒ 它的名额空出来, 而「板只改一次」正卡在 mech 侧输入 (ISS-266 作业包 §S8)★**
  · ★**零写板 / 零改阈值 / 不代拍板框 / 不代拍 jd_y0★**
· ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM / 任何 agent 的分片 / 决策页 / PROJECT_TRACKER §0★**
· ★**零外发 · 零采购 · 不替老板拍板 (★V-2/V-3/V-4 一个值都不落★)· 不替老板拍板框 / jd_y0 / W-1★**
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"
NOW = "2026-11-17 03:2x"

BR262 = os.path.join(HERE, "dispatch_briefs", "ISS-262_hw_land_row_anchor_guard_r2.md")
BR263 = os.path.join(HERE, "dispatch_briefs", "ISS-263_sw_rknn3_toolkit_install_test_r2.md")
BR267 = os.path.join(HERE, "dispatch_briefs", "ISS-267_mech_debug_port_layout_constraints.md")


def atomic_write(path: str, data) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix="." + os.path.basename(path) + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def read_text(p: str) -> str:
    with open(p, encoding="utf-8") as f:
        return f.read()


def main() -> int:
    for p in (BR262, BR263, BR267):
        if not os.path.exists(p):
            raise SystemExit("★brief 缺失 ⇒ 拒绝落账: %s" % p)
    brief267 = read_text(BR267)

    shutil.copy2(IL, IL + ".bak_20261117_0320_iss264verify_open267")
    shutil.copy2(DL, DL + ".bak_20261117_0320_iss264verify_open267")

    lock_fh = open(LOCK, "a+")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)

        # ---------------- issue_log ----------------
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        issues = il["issues"]
        by_id = {i.get("id"): i for i in issues}

        # ① ISS-264 → verified
        i264 = by_id["ISS-264"]
        assert i264.get("status") == "fixing", "★ISS-264 状态不是 fixing ⇒ 拒绝落账: %s" % i264.get("status")
        i264["status"] = "verified"
        i264["fix_ref"] = (
            "HANDOFF/2026-11-17_mech-lead_ISS264_检修口常量迁30mm套A.md (77.6 KB · B1~B6 齐全) · "
            "MECH/service_port_check.py (p2_y 7.50→15.00 · s2_y 12.50→20.00 · 阈值未松) · "
            "MECH/check_demo_struct_truth.py (H-1 重基线) · MECH/cavity_recalc_check.py (H-1 重基线) · "
            "MECH/HW_CROSS_REVIEW_TRIAGE.md (§1 锚点 + §3.1 R-07 追加) · MECH/SERVICE_PORT_ISS092.md (L5/L6/L89/L281/L322 追加)"
        )
        i264["verify_by"] = "main"
        i264["verify_result"] = "pass"
        i264["verify_date"] = TODAY
        i264["verify_note"] = (
            "★**main 2026-11-17 03:1x 独立复验 (★自己实跑, 不抄交卷报告★)**:\n"
            "· `python3 MECH/service_port_check.py` ⇒ **rc=0 · 57/57 · FAIL 0** (★P-5 最近距离 P2 3.23mm / S2 8.53mm · §5.1 开口 Y 7.835..12.435★)\n"
            "· `python3 MECH/check_demo_struct_truth.py` ⇒ **rc=0 · 23/23 · FAIL 0**\n"
            "· `python3 MECH/cavity_recalc_check.py` ⇒ **rc=0 · 23/23**\n"
            "· `python3 state/merge.py` ⇒ **rc=0** (★产出 392 · 阻塞 43 · 未闭合需求 229 · 冲突 0★)\n"
            "· `python3 state/gate_check.py` ⇒ **rc=0 · Q1 18/18**\n"
            "· ★**3 个受保护脚本 md5 与 mech-lead 自报逐字节一致**: `4ae5827e986f1aebb108c5aa2a475074` (check_demo_struct_truth.py) · "
            "`c4bf9151dd59826fb2320c34e8afbd0f` (cavity_recalc_check.py) · `db58ff6a2afc28b8bf517e3c57c56bc1` (service_port_check.py)\n"
            "· ★**受保护 5 件逐字节不变**: 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · "
            "BOM `94642d07a69e8d60dd2af57f69b93607` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b`\n"
            "★**⇒ 判定 pass; 6 个 PCB 类 FAIL 仍是「正确状态」(排队等原理图定稿), 不是本单缺陷★**\n"
            "★**★登记 main 地界该登的 3 个 md5 (★mech-lead 交卷单 §④ 点名要 main 落进 issue_log, 别人不能写★)★**:\n"
            "· `MECH/check_demo_struct_truth.py` ⇒ `MD5_EXPECTED` 已更新为 **`4ae5827e986f1aebb108c5aa2a475074`**\n"
            "· `MECH/cavity_recalc_check.py` ⇒ `MD5_EXPECTED` 已更新为 **`c4bf9151dd59826fb2320c34e8afbd0f`**\n"
            "· `MECH/service_port_check.py` ⇒ `MD5_EXPECTED` 已更新为 **`db58ff6a2afc28b8bf517e3c57c56bc1`**\n"
            "★**⇒ 三个 md5 已在本条落账, 后续任何 agent 改这三个脚本都必须同步更新本条 + 三个脚本的 MD5_EXPECTED★**\n"
            "★**遗留给 main 的两件 (★不许本单代拍★)**: ① `jd_y0` 终值 (合法区间 [3.57, 12.13]) 需 main + hw-lead 拍 "
            "(★已开 ISS-267 给 mech-lead 做候选枚举, 拍板仍在 main/老板★) · ② `MECH/SERVICE_PORT_ISS092.md` L89 旧值 8.67..13.27 的最终处置 "
            "(★已标「已作废·以脚本为准」, 老字没删★)"
        )
        i264["note"] = (i264.get("note") or "") + (
            "\n\n★" + NOW + " cron fb67af40 (队列自动派活 · 第 3 趟) **main 独立复验 ⇒ 落 verified** ★\n"
            "· ★**会话实况**: `agent:mech-lead:subagent:4631cffa` runtimeMs 710181 (≈11.8 min) · status=done · abortedLastRun=**false** "
            "(★本条是三条里唯一没被 abort 的★) ⇒ 交卷物 4 件全在盘 ★\n"
            "· ★**main 自己实跑了 5 条验收 (★rc 原文见 verify_note★) ⇒ pass ⇒ 落 verified + 登记 3 个 md5★**\n"
            "· ★**本条 verified 后 mech-lead 名额空出 ⇒ 同轮新开 ISS-267 (纯分析类, 零写板)★**\n"
        )

        # ② ISS-262 续做 (status 保持 fixing)
        i262 = by_id["ISS-262"]
        assert i262.get("status") == "fixing", "★ISS-262 状态不是 fixing ⇒ 拒绝落账: %s" % i262.get("status")
        i262["dispatched_at"] = TODAY
        i262["note"] = (i262.get("note") or "") + (
            "\n\n★" + NOW + " cron fb67af40 (队列自动派活 · 第 3 趟) **僵尸 fixing 续做重派 (第 2 趟)** ★\n"
            "· ★**第 1 趟会话 `agent:hw-lead:subagent:7922c2a0` (taskName queue_iss262) runtimeMs 1410578 (≈23.5 min) · "
            "status=done · abortedLastRun=true ⇒ transcript 末尾 `openclaw:prompt-error` = \"This operation was aborted\" "
            "(★父 cron 收摊把子会话一起 abort, 不是它自己写崩★)★**\n"
            "· ★**盘上产物 = 交卷单骨架 1034 B (B1~B6 全 `_(施工中)_`) + 零脚本 + 零日志 + `grep -c iss262 state/fragments/hw.yaml` = 0 ★**\n"
            "· ★**第 2 趟 brief = `state/dispatch_briefs/ISS-262_hw_land_row_anchor_guard_r2.md` (★权威任务书仍是 ISS-262_hw_land_row_anchor_guard.md, "
            "r2 只加纪律 + 已完成盘点 + 交付范围收窄★)★**\n"
            "· ★**r2 的三处收窄**: ① 25 分钟 5 段预算 (P1 ≤12min 先把「闸 + --selftest ≥4 条反向用例」落盘) · "
            "② 交付物② (NEXT_BATCH_V1 追加) 可延到第 3 趟 (★如实写「未交」, 不许空交卷★) · "
            "③ 追加了第 1 趟已想清、可直接用的结论 (★锚点是混合的: gen_netlist.py L381/L393/L40/L184 + netlist_v1.csv L8/L12 + "
            "check_pin_function_labels.py L127/L143; 判定指向哪个文件 = 用 snippet 反查, 不许手抄★)★**\n"
            "· ★**本单 status 保持 fixing (本来就是 fixing; 同一单续做, 不重复标)★**\n"
        )

        # ③ ISS-263 续做 (status 保持 fixing)
        i263 = by_id["ISS-263"]
        assert i263.get("status") == "fixing", "★ISS-263 状态不是 fixing ⇒ 拒绝落账: %s" % i263.get("status")
        i263["dispatched_at"] = TODAY
        i263["note"] = (i263.get("note") or "") + (
            "\n\n★" + NOW + " cron fb67af40 (队列自动派活 · 第 3 趟) **僵尸 fixing 续做重派 (第 2 趟)** ★\n"
            "· ★**第 1 趟会话 `agent:sw-lead:subagent:b765bfb4` (taskName queue_iss263) runtimeMs 1332293 (≈22 min) · "
            "status=done · abortedLastRun=true ⇒ 同样被 \"This operation was aborted\" 掐掉 (★父 cron 收摊★)★**\n"
            "· ★**★但技术活其实干完了 (★main 03:1x 本机实跑核对盘上证据, 一条都不用重做★)★**:\n"
            "  · 独立 env `/home/yuewuya/miniconda3/envs/rknn3` (python 3.10.22) · ★**rknn3-toolkit 1.2.0 已装** ★ · numpy 2.2.6 / torch 2.4.0+cpu / onnx 1.23.2\n"
            "  · `config(target_platform='rk3572')` ⇒ **rc=0 (0.019s)** ; ★**反向自证**: `rk3576` ⇒ `ValueError: Unsupported target_platform 'rk3576'. "
            "Supported target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` (★证明 target 真被读★)\n"
            "  · ★**转换 3 次读数 (全 rc=0)**: 产出 `yolov5n_heads_int8_rk3572_run{1,2,3}.rknn` = **249360 B · md5 `97a34fff0b855b92681f26627dba5354` (三次逐字节一致)** · "
            "t_total **33.389 / 34.108 / 41.672 s** (min/avg/max = 33.389/36.390/41.672)\n"
            "  · ★**全模型 yolov5s@640 额外证据**: `yolov5s_full_int8_rk3572.rknn` = 339992 B · md5 `e8927025d8d0494a1a949802bbac7a1f` · t_total 74.314 s\n"
            "  · 门禁 (装完照跑): `check_demo_panel_spec.py` **G1_RC=0** (R1~R7 全过) · `timing_check.py` **G2_RC=0 (71/71)** · `merge.py` **G3_MERGE_RC=0**\n"
            "  · ★**唯一的真尾巴**: `logs/iss263/extra_probe.log` 里往返自证炸了 ⇒ `TypeError: RKNN.load_rknn() missing 1 required positional argument: 'weight_path'`\n"
            "· ★**盘上缺的**: 交卷单 B1~B6 全是 `(填)` + `grep -c iss263 state/fragments/sw.yaml` = 0 + `SW/RK3572_TARGET_COMPAT_V2.md` §5/§6.3 未追加\n"
            "· ★**第 2 趟 brief = `state/dispatch_briefs/ISS-263_sw_rknn3_toolkit_install_test_r2.md` (★只干三件事: 补往返自证 + 交卷单写满 + 两个交卷物; "
            "不许重下 wheel / 重装 / 重转模型★)★**\n"
            "· ★**★结论口径 (main 定, 不许含糊)★**: **转换链已通 (rknn3-toolkit 1.2.0 + target_platform='rk3572' 实跑 3 次全 rc=0) / 板端接受性仍是 [0数据]** "
            "⇒ ★**ISS-155 (blocker) 的状态可改写成「转换链已通 / 板端待板」 (★路线取舍仍由老板拍★)★**\n"
            "· ★**本单 status 保持 fixing (本来就是 fixing; 同一单续做, 不重复标)★**\n"
        )

        # ④ 新开 ISS-267
        assert "ISS-267" not in by_id, "★ISS-267 已存在 ⇒ 拒绝重复开单★"
        issues.append({
            "id": "ISS-267",
            "title": (
                "★★[主线内·结构侧·板侧开口约束·纯分析·内部活] ★★"
                "检修口/调试口 `jd_y0` 的合法区间只剩 [3.57, 12.13]mm (★按比例迁 ⇒ P-2 净空 −11.77mm ⇒ 孔与焊盘阵列直接重叠★) "
                "⇒ 出「板侧开口约束表 + 候选枚举」 ★★ ★**同时: 板框口径三套并存 (★台架板 160×100·8层 / 产品目标板 60×15⇒60×30套A / "
                "MECH 检修口脚本按 60×30 算★) ⇒ 「板只改一次」对着哪个框画现在没有唯一真源 ⇒ 列成决策材料交 main★**"
            ),
            "severity": "medium",
            "source_blocker": "ISS-085",
            "source_agent": "main",
            "desc": (
                "★main 2026-11-17 03:1x 本机实跑 (★不抄交卷报告★):\n"
                "· `MECH/service_port_check.py` 现值 (★ISS-264 刚迁完★): `pcb_thk` 1.00 (只核不动) · `p2_y` **15.00** · `s2_y` **20.00** "
                "(★旧 7.50/12.50 已作废·追加式留痕★) ⇒ rc=0 · 57/57\n"
                "· 重算: P-5 最近距离 **P2 3.23mm / S2 8.53mm** (≥0.60 判据, 余 +2.63/+7.93) · §5.1 开口 Y **7.835..12.435** "
                "(★ISS-251 手算 8.67..13.27 与脚本差 0.835mm ⇒ 以脚本为准★)\n"
                "· ★**`jd_y0` 合法区间只剩 [3.57, 12.13]mm** (最紧是 P-2: `12.73 − jd_y0 ≥ 0.60`) ⇒ 现状 9.50 距上界只剩 2.63mm "
                "⇒ ★**按 15mm 板相对位置平迁 (jd_y0=24.50) ⇒ P-2 净空 −11.77mm ⇒ 缺口 12.37mm ⇒ 绝不许按比例迁★**\n"
                "· 候选 A (维持 9.50) / B (贴判据, 剩 0.13mm < FDM ±0.30 ⇒ 不可用) / C (迁 10.00~11.00) / D (改 X 排布, HW 地界) "
                "★**ISS-264 已列但没代拍★**\n"
                "· ★**板框口径三套并存 (★main 实读★)**: ① `HW/PCB/demo_mainboard_params.json` board = **160.0×100.0mm / 8层 / 1.6mm** "
                "(★`_pending` 自述「先能装下所有件的尺寸」, 与盘上板 pcbnew 实读 160.10×100.10·8铜层一致★) · ② 产品目标板 **60×15** (老板 10-27) "
                "⇒ ISS-118 后板宽 30 ⇒ **60×30 套A** · ③ **MECH 检修口脚本现在按 60×30 套A 算** ⇒ "
                "★**「板只改一次」对着哪个框画没有唯一真源 ⇒ 这正是会让那一趟白做的头号坑 (★hw-lead ISS-266 作业包 §S8 就卡在 P7/A1/W-4/mech★)★**\n"
                "· 坐标约定沿用既有口径: 原点 = 板框左下角 · X = 板长 0→60 (X=0 = 铰链端) · Y = 板宽 0→15 (现 30) ⇒ Y↔V 朝向仍 [0数据]"
            ),
            "owner": "mech-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-21",
            "status": "open",
            "external": False,
            "need_keys": ["iss264_mech_jd_y0_and_open_y_caliber"],
            "fix_ref": None,
            "note": (
                "★main 2026-11-17 03:2x 开单 (job fb67af40 队列自动派活 · 第 3 趟)★\n"
                "★**为什么现在开**: ISS-264 verified ⇒ mech-lead 名额空出; 而「板只改一次」正卡在 mech 侧输入 (★ISS-266 作业包 §S8★)\n"
                "★**类别**: ★**纯分析/作业包类** (★老板 2026-11-17 00:43: 目标是绘制 PCB 图 ⇒ PCB 布线/布局类可派, 但板只改一次 ⇒ 先派不动板的★)\n"
                "★**边界**: 零写板 · 零改布局 · 零改判据阈值 (★3 个 md5 必须逐字节不变★) · 零外发 · 不代拍板框 / 不代拍 jd_y0\n"
                "★**不许改既有闸脚本, 要算新东西只能新建独立脚本 (★可带 --selftest★)★**"
            ),
            "task_brief": brief267,
            "dispatched_at": None,
        })

        atomic_write(IL, il)

        # ---------------- dispatch_log ----------------
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).extend([
            {"issue": "ISS-262", "agent": "hw-lead", "at": TODAY,
             "brief": "state/dispatch_briefs/ISS-262_hw_land_row_anchor_guard_r2.md",
             "note": "★僵尸 fixing 续做第 2 趟 (第 1 趟会话被 \"This operation was aborted\" 掐死, 盘上只有交卷单骨架)★"},
            {"issue": "ISS-263", "agent": "sw-lead", "at": TODAY,
             "brief": "state/dispatch_briefs/ISS-263_sw_rknn3_toolkit_install_test_r2.md",
             "note": "★僵尸 fixing 续做第 2 趟 (技术活已做完, 只差往返自证 + 写卷 + 分片)★"},
            {"issue": "ISS-267", "agent": "mech-lead", "at": TODAY,
             "brief": "state/dispatch_briefs/ISS-267_mech_debug_port_layout_constraints.md",
             "note": "★新开内部活 (纯分析类): 检修口/调试口板侧开口约束表 + jd_y0 候选枚举 + 板框口径三套并存的冲突清单★"},
        ])
        atomic_write(DL, dl)
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    # ---------------- 自检 ----------------
    chk = yaml.safe_load(open(IL, encoding="utf-8"))
    by = {i.get("id"): i for i in chk["issues"]}
    print("✅ issue_log.yaml 已原子写 (flock + 锁内重读 + tmp/os.replace):")
    print("   - ISS-264 ⇒ status=%s (verify_by=%s · verify_result=%s · verify_date=%s)"
          % (by["ISS-264"]["status"], by["ISS-264"]["verify_by"], by["ISS-264"]["verify_result"], by["ISS-264"]["verify_date"]))
    print("   - ISS-262 ⇒ status=%s (★保持 fixing, 同一单续做★)" % by["ISS-262"]["status"])
    print("   - ISS-263 ⇒ status=%s (★保持 fixing, 同一单续做★)" % by["ISS-263"]["status"])
    print("   - ISS-267 ⇒ 新开 · status=%s · owner=%s · severity=%s · due=%s"
          % (by["ISS-267"]["status"], by["ISS-267"]["owner"], by["ISS-267"]["severity"], by["ISS-267"]["due"]))
    print("   - 总条数: %d (备份: %s)" % (len(chk["issues"]), os.path.basename(IL) + ".bak_20261117_0320_iss264verify_open267"))
    dl2 = yaml.safe_load(open(DL, encoding="utf-8"))
    print("✅ dispatch_log.yaml 已原子写 · 总条数: %d (本轮 +3)" % len(dl2["dispatches"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
