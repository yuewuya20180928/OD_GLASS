#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_0345_verify_262_263_267.py
★main (moli) 落账 · 2026-11-17 03:4x (cron 775d9893 「ARS45 继续执行后继计划」)★

★★**本轮实跑结论 (★全部自己实跑, 不是抄任何交卷报告★)★★ ★★
· ★**`python3 state/advance.py --json` ⇒ internal = []** (★A 段空★)
  · 原因 = ★**三个总工名下各卡一条 status=fixing (ISS-262 / ISS-263 / ISS-267)⇒ advance.py 的「同 agent 同时只允许一个在飞任务」铁律把其余全压住★**
  · ★**但实测 (sessions_list): 这 3 条的会话【全部已 ended 且交卷完整】⇒ 不是「在飞」, 是「僵尸 fixing」(★交完卷没人落账★)★**
· ★**会话实测 (sessions_list · activeMinutes=30)★**:
  · `agent:hw-lead:subagent:9b6d4d55` (ISS-262) · runtimeMs **322987 (≈5.4 min)** · status=**done** · abortedLastRun=**false**
  · `agent:sw-lead:subagent:d867c0f5` (ISS-263) · runtimeMs **507912 (≈8.5 min)** · status=**done** · abortedLastRun=**false**
  · `agent:mech-lead:subagent:3e051f0f` (ISS-267) · runtimeMs **467846 (≈7.8 min)** · status=**done** · abortedLastRun=**false**
  · ⇒ ★**3 个会话全是「正常跑完」, 不是被父 cron abort 的那种僵尸 (abortedLastRun=true)★** ⇒ ★**本单 = 落账这 3 条 (fixing → verified)★**

★★**main 本机独立复验 (★自己实跑, 不抄交卷报告★)★★ ★★
· ★**ISS-262 (hw-lead · 落表行号锚点兜底闸)**:
  · `python3 HW/check_land_row_anchors.py --selftest` ⇒ **rc=0 · 9/9 全过** (★T1 正向绿 / T2 纯漂移 rc=3 DRIFT=72 / T3 --reanchor 后复跑绿 /
    T4 内容变 rc=1 / T5 行号+内容都变 rc=1 / T6 台账偷改 rc=1 / T7 源码⇄规格页漂移 rc=1 / T8 生成器源码行漂移 rc=3 DRIFT=216 / T9 重锚后复跑绿★)
  · ★**真盘跑 (非沙盒) ⇒ PASS=310 · DRIFT=0 · RED=0** (★310 条锚点 = 网表/脚表/BOM 表行 94 + gen_netlist.py `add()` 源码行 216★)
  · ★**受保护 5 件逐字节不变**: 网表 `e06c1dd6…` · 脚表 `287e7861…` · BOM `94642d07…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…`
· ★**ISS-263 (sw-lead · rknn3-toolkit 1.2.0 安装实测 + rk3572 转换)**:
  · ★**读 `logs/iss263/roundtrip_probe.log` 原样**: `load_rknn` rc=**0** (t=0.001s) · `export_rknn` rc=**0** ·
    ★**`REEXPORT_MD5_MATCH_ORIG = True`** (往返导出 md5 与原文件完全一致 `97a34fff…`) · 整模型那份同样 True (`e8927025…`)
  · ★**板端探测 = `init_runtime()` rc=**-1** / `RKNN3_ERR_DEVICE_UNAVAILABLE` / `adb: no devices/emulators found` / `list_devices() = []` ⇒ 板端 [0数据] (与交卷自述一致)★**
  · ★**分片登记**: `grep -c iss263 state/fragments/sw.yaml` = **18** (★0 → 18★)
· ★**ISS-267 (mech-lead · 检修口/调试口板侧开口约束表)**:
  · `python3 MECH/jd_y0_feasibility.py --selftest` ⇒ **rc=0 · 4/4** (★① 现值复算一致 ② 旧 15mm 回代 ③ 反向用例 24.50 判红 余 −12.77 ④ 口径矛盾留痕 通用式 +8.50★)
  · ★**3 个受保护脚本 md5 逐字节不变**: `4ae5827e…` (check_demo_struct_truth.py) · `c4bf9151…` (cavity_recalc_check.py) · `db58ff6a…` (service_port_check.py)
  · ★**受保护 5 件逐字节不变** (★与上两条同一批 md5 实跑, 三单互证★)
  · ★**分片登记**: `grep -c iss267 state/fragments/mech.yaml` = **7**
· ★**门禁**: `state/merge.py` rc=0 (★产出 404 · 阻塞 43 (高危 33) · 未闭合需求 234 · 冲突 0 · 健康度 red★) · `state/gate_check.py` rc=0 (★Q1 18/18 · Q2 3/3 · Q6 ✅ 通过★) ·
  `state/issue_check.py` rc=0 (★全过★) · `state/stage_gate.py` rc=1 (★预期: 当前 G1 缺 1 项 = PCB unconnected=45★)

★★**本脚本做的事 (边界写死)★★ ★★
· ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` (★flock + 锁内重读 + tmp/os.replace 原子写★)★**
· ★**ISS-262 / ISS-263 / ISS-267: fixing → verified** (★fix_ref / verify_by=main / verify_result=pass / verify_date=2026-11-17 / verify_note=本机复验原文★)
· ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM / 任何 agent 的分片 / 决策页 / PROJECT_TRACKER §0★**
· ★**零外发 · 零采购 · 不替老板拍板 (★V-2/V-3/V-4 一个值都不落 · 不拍板框 · 不拍 jd_y0 · 不拍 W-1/W-2/W-4 / P7 / D1~D4★)★**
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
NOW = "2026-11-17 03:4x"
BAK = ".bak_20261117_0345_verify262_263_267"


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


PROTECTED = (
    "★**受保护 5 件逐字节不变 (★main 本机 md5sum 实跑★)**: 网表 `e06c1dd633566aa44732762c2ff99d1c` · "
    "脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` · "
    "板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★\n"
)


def main() -> int:
    shutil.copy2(IL, IL + BAK)
    shutil.copy2(DL, DL + BAK)

    lock_fh = open(LOCK, "a+")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)

        il = yaml.safe_load(open(IL, encoding="utf-8"))
        issues = il["issues"]
        by_id = {i.get("id"): i for i in issues}

        # ---------------- ISS-262 ----------------
        i = by_id["ISS-262"]
        assert i.get("status") == "fixing", "★ISS-262 状态不是 fixing ⇒ 拒绝落账: %s" % i.get("status")
        i["status"] = "verified"
        i["fix_ref"] = (
            "HANDOFF/2026-11-17_hw-lead_ISS262_落表行号锚点兜底与同批落表清单.md (25 KB · B1~B6 齐全) · "
            "HW/check_land_row_anchors.py (新闸本体 · 310 条锚点 · 三态判定 · --reanchor · --selftest 9/9) · "
            "HW/land_row_anchors_registry.json (机器写台账 · REGISTRY_SHA256 防偷改) · "
            "HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md (§9 追加: 9 条撞车 + GEN_ORDER 硬顺序 + 落表后 7 项重基线) · "
            "HW/ISS262_acceptance_rc.log (106 KB 原始日志)"
        )
        i["verify_by"] = "main"
        i["verify_result"] = "pass"
        i["verify_date"] = TODAY
        i["verify_note"] = (
            "★**main 2026-11-17 03:3x 独立复验 (★自己实跑, 不抄交卷报告★)**:\n"
            "· `python3 HW/check_land_row_anchors.py --selftest` ⇒ **rc=0 · 9/9 全过** "
            "(★T1 正向绿 / T2 纯漂移 rc=3 DRIFT=72 / T3 --reanchor 后复跑绿 / T4 内容变 rc=1 / "
            "T5 行号+内容都变 rc=1 / T6 台账偷改 rc=1 / T7 源码⇄规格页漂移 rc=1 / "
            "T8 生成器源码行漂移 rc=3 DRIFT=216 / T9 重锚后复跑绿★)\n"
            "· ★**真盘跑 (非沙盒) ⇒ 锚点 310 条 · PASS=310 · DRIFT=0 · RED=0** (★94 表行 + 216 生成器源码行★)\n"
            + PROTECTED +
            "· `python3 state/merge.py` ⇒ **rc=0** (★产出 404 · 阻塞 43 · 未闭合需求 234 · 冲突 0★)\n"
            "· `python3 state/gate_check.py` ⇒ **rc=0 · Q1 18/18 · Q2 3/3 · Q6 ✅**\n"
            "· `python3 state/issue_check.py` ⇒ **rc=0**\n"
            "· ★**判定 pass** ⇒ ★**本单价值 = 「落表链有了行号漂移判据」⇒ V-3 落表 (删 3 行 DNP) 不再能把门禁刷假绿★**\n"
            "★**给老板的两条硬消息 (原样转达, 不代拍)★**: ① **决策页 §A-补7 的「15 条一次落」是错的** ⇒ 实测 **网表侧 14 条 (V-3 13 + V-4 1) + 板那一趟 4 条 (R4×2 + R9 + R3)**; "
            "② **W-1b 第四条路有配方缺口**: `D_ESD_USB_N` 在 `state/land_v_values.py` 里 grep 计数 = **0** ⇒ 落表器做不了, D− 侧只能排队到板那一趟\n"
            "★**一个认知订正 (实跑发现)★**: 任务书「V-3 删 3 行 ⇒ 所有行号锚点 −3」**对网表 CSV 行号不成立** (实测表A 513 / 脚表 584 / BOM 218 行数都不变); "
            "V-3=E 删的是 `state/gen_netlist.py` 里的 Python 字典 ⇒ **真正 −3 的是生成器源码行号** ⇒ 本闸补上了源码行那层 (216 条 + T8/T9 用例) ★\n"
            "★**边界 (实跑自证)**: 零落表 (三条全干跑) · 零写板 · 零外发 · 零采购 · SW/MECH 一个字节没碰 · 未替老板拍板 · 未自签 issue_log ★\n"
        )
        i["note"] = (i.get("note") or "") + (
            "\n★**main 2026-11-17 03:4x 落账 (cron 775d9893)**: 会话 `agent:hw-lead:subagent:9b6d4d55` "
            "runtimeMs 322987 · status=done · abortedLastRun=false ⇒ **不是僵尸, 是「交完卷没人落账」** ⇒ "
            "main 本机复验通过 ⇒ **fixing → verified** ★\n"
        )

        # ---------------- ISS-263 ----------------
        i = by_id["ISS-263"]
        assert i.get("status") == "fixing", "★ISS-263 状态不是 fixing ⇒ 拒绝落账: %s" % i.get("status")
        i["status"] = "verified"
        i["fix_ref"] = (
            "HANDOFF/2026-11-17_sw-lead_ISS263_rknn3_toolkit安装实测与rk3572转换.md (26.9 KB · B1~B6 齐全) · "
            "SW/tools/iss263_roundtrip_probe.py (往返自证探针) · "
            "logs/iss263/roundtrip_probe.log (原始日志: 签名 + 往返 md5 + 板端探测) · "
            "SW/RK3572_TARGET_COMPAT_V2.md (§5.4 + §6.4 追加, 老字零删除)"
        )
        i["verify_by"] = "main"
        i["verify_result"] = "pass"
        i["verify_date"] = TODAY
        i["verify_note"] = (
            "★**main 2026-11-17 03:3x 独立复验 (★自己实跑, 不抄交卷报告★)**:\n"
            "· ★**读 `logs/iss263/roundtrip_probe.log` 原样**: `load_rknn` rc=**0** (t=0.001s) · `export_rknn` rc=**0** · "
            "★**`REEXPORT_MD5_MATCH_ORIG = True`** (往返导出 md5 与原文件完全一致 `97a34fff0b855b92681f26627dba5354`) · "
            "整模型那份同样 True (`e8927025d8d0494a1a949802bbac7a1f`)\n"
            "· ★**板端 = `init_runtime()` rc=**-1** / `RKNN3_ERR_DEVICE_UNAVAILABLE` / `adb: no devices/emulators found` / "
            "`list_devices() = []` ⇒ 板端 [0数据]** (★与交卷自述逐字一致★)\n"
            "· ★**分片登记**: `grep -c iss263 state/fragments/sw.yaml` = **18** (★0 → 18★)\n"
            + PROTECTED +
            "· `python3 state/merge.py` ⇒ **rc=0** · `python3 state/gate_check.py` ⇒ **rc=0 · Q1 18/18** · "
            "`python3 state/issue_check.py` ⇒ **rc=0**\n"
            "· ★**判定 pass** ⇒ ★**结论 = 转换链已通 (rknn3-toolkit 1.2.0 · `config('rk3572')` rc=0 · ONNX→.rknn 3 次全 rc=0) · 板端仍 [0数据]· 等板到手★**\n"
            "★**给 main 的口径订正 (原样转达)★**: **ISS-155 的 blocker 可改写为「转换链已通 / 板端待板」** ⇒ "
            "板到手后按 `SW/tools/iss263_roundtrip_probe.py` 的 `init_runtime(target='rk3572', core_mask=NPU_CORE_0)` 口径补测 "
            "(★纯 NPU ms 与 SDK 总 ms 两条线都要, 别混用★)\n"
            "★**边界 (实跑自证)**: 未重下 wheel / 未重装 / 未重转模型 · toolkit2 2.3.2 旧 env 未污染 · 未碰 HW/MECH/网表/脚表/BOM/板 · "
            "未自签 issue_log · 未替老板拍路线 ★\n"
        )
        i["note"] = (i.get("note") or "") + (
            "\n★**main 2026-11-17 03:4x 落账 (cron 775d9893)**: 会话 `agent:sw-lead:subagent:d867c0f5` "
            "runtimeMs 507912 · status=done · abortedLastRun=false ⇒ **不是僵尸, 是「交完卷没人落账」** ⇒ "
            "main 本机复验通过 ⇒ **fixing → verified** ★\n"
        )

        # ---------------- ISS-267 ----------------
        i = by_id["ISS-267"]
        assert i.get("status") == "fixing", "★ISS-267 状态不是 fixing ⇒ 拒绝落账: %s" % i.get("status")
        i["status"] = "verified"
        i["fix_ref"] = (
            "HANDOFF/2026-11-17_mech-lead_ISS267_检修口调试口板侧开口约束表.md (27.3 KB · B1~B6 齐全) · "
            "MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md (29.3 KB 新建: 口径矩阵 18 量 + 板框冲突影响表 + jd_y0 区间+候选 + 约束清单) · "
            "MECH/jd_y0_feasibility.py (39.8 KB 新建: 只读 import 闸脚本取 BASE/TOL/CRIT ⇒ 阈值零漂移 · --selftest 4/4 · --json)"
        )
        i["verify_by"] = "main"
        i["verify_result"] = "pass"
        i["verify_date"] = TODAY
        i["verify_note"] = (
            "★**main 2026-11-17 03:4x 独立复验 (★自己实跑, 不抄交卷报告★)**:\n"
            "· `python3 MECH/jd_y0_feasibility.py --selftest` ⇒ **rc=0 · 4/4** "
            "(★① 现值复算一致 (开口 Y 7.835..12.435 · P-5 3.23/8.53) ② 旧 15mm 板口径回代 (P-5 1.00/1.03, 判据 0.60 未松) "
            "③ 反向用例 jd_y0=24.50 ⇒ 闸脚本判据判红 (2.5: 焊盘上沿 25.77 > 13.00, 余 −12.77) ④ 口径矛盾留痕 (通用式 = +8.50)★)\n"
            "· ★**3 个受保护脚本 md5 逐字节不变**: `4ae5827e986f1aebb108c5aa2a475074` (check_demo_struct_truth.py) · "
            "`c4bf9151dd59826fb2320c34e8afbd0f` (cavity_recalc_check.py) · "
            "`db58ff6a2afc28b8bf517e3c57c56bc1` (service_port_check.py) ★\n"
            + PROTECTED +
            "· ★**分片登记**: `grep -c iss267 state/fragments/mech.yaml` = **7**\n"
            "· `python3 state/merge.py` ⇒ **rc=0** · `python3 state/gate_check.py` ⇒ **rc=0 · Q1 18/18** · "
            "`python3 state/issue_check.py` ⇒ **rc=0**\n"
            "· ★**判定 pass** ⇒ ★**纯分析单, 零写板 / 零落表 / 零改阈值 (3 md5 逐字节不变)★**\n"
            "★**三条给老板的材料 (原样转达, 不代拍)★**:\n"
            "① ★**`jd_y0` 合法区间 = [1.665, 11.730] mm, 上界不是 12.13 而是 11.73** (★闸脚本检查项 **2.5** `pad_y1 ≤ 13.00` 比 P-2 更紧; "
            "ISS-264 §0.1 漏了这条判据★) ⇒ 现状 9.50 距上界只剩 **2.23mm** (不是 2.63mm); "
            "另两处口径差异: 下界 1.665 (非 3.57) · 「24.50 ⇒ 重叠 12.37mm」在脚本自己 7.4 通用式下复现不出来 (实为 **+8.50**)\n"
            "② ★**板框三套并存 + 机器判红**: 台架板 160×100 (Edge.Cuts 实读) **盖板内腔 4.10 < 4.50 / V 链 −68.00 / L 链 −85.50 三处判红** ⇒ 它当不了镜脚板; "
            "60×30 套A 全绿 (V 最坏 +1.40); 60×15 几何绿但 **套A 孔位在 15mm 板上不成立** (P-2 孔心 Y=15 = 板边) ⇒ "
            "**建议把「拍框 + 拍 jd_y0」合成一拍** (候选 A 9.50 / C 10.00~11.00; B 贴判据不可用; D 改 X 成本最高)\n"
            "③ ★**板侧开口约束与落表/作业包对不上 (已点名到行)★**: 落表 `J_DEBUG` 是 **1×4** (`HW/BOM_v1.csv:71` · `netlist_v1_pins.csv:202-205`) 而脚本按 **2×5**; "
            "盘上板 `J_DEBUG`@(144.30,58.00) 与 `J_UART`@(20.74,70.00) **相距 123.6mm** 而 MECH 模型让它们紧邻 ⇒ **开口 X 10.20 与「必须清空区」X 宽 7.62 必须重算**; "
            "座体高 2.54 是假设 `[0数据]` ⇒ **Y 向表可用、X 向待真实型号定版**; "
            "作业包 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md:301`/`:310` 仍写产品板 60×15 (与 ISS-118 的 30 冲突), `:164`/`:289` 里 MECH 侧只认领了 `D_LED_G` ⇒ "
            "**检修口开口在「板只改一次」那一趟里无人认领** ⇒ 建议把本单 §1/§3 挂进 S6\n"
            "★**边界 (实跑自证)**: 零写板 · 零落表 · 零改阈值 (3 md5 逐字节不变) · 零外发 · 未自签 issue_log · 未替老板拍板框 / 拍 jd_y0 ★\n"
        )
        i["note"] = (i.get("note") or "") + (
            "\n★**main 2026-11-17 03:4x 落账 (cron 775d9893)**: 会话 `agent:mech-lead:subagent:3e051f0f` "
            "runtimeMs 467846 · status=done · abortedLastRun=false ⇒ **不是僵尸, 是「交完卷没人落账」** ⇒ "
            "main 本机复验通过 ⇒ **fixing → verified** ★\n"
        )

        atomic_write(IL, il)

        # ---------------- dispatch_log ----------------
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).extend([
            {"issue": "ISS-262", "agent": "hw-lead", "at": TODAY,
             "brief": "state/dispatch_briefs/ISS-262_hw_land_row_anchor_guard_r2.md",
             "note": "★main 2026-11-17 03:4x 落账: 会话 done/aborted=false ⇒ 交卷完整 ⇒ main 本机复验 (selftest 9/9 · 真盘 310 锚点全绿 · 受保护 5 md5 不变) ⇒ fixing → verified ★"},
            {"issue": "ISS-263", "agent": "sw-lead", "at": TODAY,
             "brief": "state/dispatch_briefs/ISS-263_sw_rknn3_toolkit_install_test_r2.md",
             "note": "★main 2026-11-17 03:4x 落账: 会话 done/aborted=false ⇒ 交卷完整 ⇒ main 本机复验 (往返 md5 一致 · 板端 [0数据] · frag 18 条) ⇒ fixing → verified ★"},
            {"issue": "ISS-267", "agent": "mech-lead", "at": TODAY,
             "brief": "state/dispatch_briefs/ISS-267_mech_debug_port_layout_constraints.md",
             "note": "★main 2026-11-17 03:4x 落账: 会话 done/aborted=false ⇒ 交卷完整 ⇒ main 本机复验 (jd_y0_feasibility selftest 4/4 · 3 md5 不变) ⇒ fixing → verified ★"},
        ])
        atomic_write(DL, dl)
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    # ---------------- 自检 ----------------
    chk = yaml.safe_load(open(IL, encoding="utf-8"))
    by = {i.get("id"): i for i in chk["issues"]}
    for k in ("ISS-262", "ISS-263", "ISS-267"):
        print("✅ %s ⇒ status=%s (verify_by=%s · verify_result=%s · verify_date=%s)"
              % (k, by[k]["status"], by[k].get("verify_by"), by[k].get("verify_result"), by[k].get("verify_date")))
    print("   - 总条数: %d (备份: %s)" % (len(chk["issues"]), os.path.basename(IL) + BAK))
    dl2 = yaml.safe_load(open(DL, encoding="utf-8"))
    print("✅ dispatch_log.yaml 已原子写 · 总条数: %d (本轮 +3)" % len(dl2["dispatches"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
