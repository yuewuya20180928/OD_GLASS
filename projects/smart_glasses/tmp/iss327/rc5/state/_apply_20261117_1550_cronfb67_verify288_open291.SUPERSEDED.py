#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/_apply_20261117_1550_cronfb67_verify288_open291.py

★main 2026-11-17 15:5x (cron fb67af40 队列自动派活)★

★**为什么有这一趟**: ★`advance.py --json` 实测 `internal: []` (三个名额全被 `fixing` 占着) ★
  ⇒ **盘面 ≠ 名单**: 实查发现 ★**sw-lead 名额被一条已经交卷的单占着** ★
  → 会话 `agent:sw-lead:subagent:b54d24be` (★15:1x~15:2x·cont2★) 实测 **status=done**,
    交卷单 43335 B 在盘 (★grep「待写」= 0★) · `SW/tools/timing_check.py` md5 = 68c4becf… (★与 ISS-285 写死的期望值逐字一致★)
    · 分片 `state/fragments/sw.yaml` 里 `iss288` 6 处 ⇒ ★**但 status 还挂在 `fixing` ⇒ sw-lead 名额被一条已经干完的单占着 ⇒ 队列静默断线** ★

★**本脚本做两件事**:
  ① **ISS-288 落 verified** (★main 本机独立实跑复验, 不抄交卷报告★)
  ② **新开 ISS-291** (sw-lead · ★ADC 域口径订正 + 逐链判决★ · ★纯分析 + 机器闸类 · 零写板 · 零落表★)
     ⇒ ★**来源 = main 15:3x~15:4x 本机实读 + 实跑** (`SW/tools/timing_check.py --json` 实跑输出 / `HW/netlist_v1.csv` L181~L186 实读 / md5 实测)

★**边界**: ★只写 `state/issue_log.yaml` + (由调用方另跑) `state/fragments/pm.yaml` 的答案条 ★
  ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM · 不写任何 agent 的分片(除 main 自己的 pm.yaml 答案)★
  ⇒ ★**不替老板拍板 · 零外发**★ ★**派活日志由 `advance.py --apply --only ISS-291` 写(本脚本不写)★**
"""
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_P = os.path.join(HERE, "issue_log.yaml")
BRIEF_P = os.path.join(HERE, "dispatch_briefs", "ISS-291_sw_adc_fs_domain_caliber.md")
TODAY = "2026-11-17"


def main() -> int:
    bak_dir = os.path.join(HERE, ".bak_288_291_1550")
    os.makedirs(bak_dir, exist_ok=True)
    shutil.copy2(LOG_P, os.path.join(bak_dir, "issue_log.yaml.bak_1550"))

    with open(LOG_P, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log["issues"]
    by_id = {it["id"]: it for it in issues}

    # ---------- ① ISS-288 落 verified (main 本机独立实跑复验) ----------
    i288 = by_id["ISS-288"]
    assert i288["status"] == "fixing", i288["status"]
    i288["status"] = "verified"
    i288["verify_by"] = "main"
    i288["verify_date"] = TODAY
    i288["fix_ref"] = "HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md"
    i288["verify_result"] = (
        "★main 2026-11-17 15:3x~15:5x 本机独立实跑复验 (不抄交卷报告)★ "
        "⇒ `python3 SW/tools/timing_check.py` **rc=0 · SELFTEST 72/72 通过 · 0 条红** (★实跑输出末行逐字: "
        "「SELFTEST 72/72 通过, rc=0」★ · 关键判定行: 「★反向: ISP avg = 15.11 ms ⇒ 必须 FAIL」「★反向: 无实测输入 ⇒ INDET + [0数据]」"
        "「T2 交叉核对: 纯 NPU 21.00 ms ⇒ 命中老板翻案条款 (20.33 ms)」★) "
        "⇒ `SW/tools/timing_check.py` md5 = **68c4becffe6bcd708e388dba9d18a505** (★与 ISS-285 交卷单写死的「改后期望 md5」逐字一致★) "
        "⇒ 交付物在盘: 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md` **43335 B** (★grep「待写」= **0 处**★) "
        "· 分片 `state/fragments/sw.yaml` 里 `iss288` **6 处** (含 1 条 need to=main + 1 条 answer 素材) "
        "⇒ `python3 state/merge.py` **rc=0** (★STATE.yaml 已刷新 2026-11-17T15:48:22+08:00★) "
        "⇒ `python3 state/gate_check.py` **rc=0** (★Q1 交付齐备率 **18/18** · 全部检查项通过★) "
        "⇒ 板 `611b869e13518c3c023fb178f91a0075` + `.kicad_pro` `3e504d2be83152e337949723e909be1b` + "
        "网表 `37f62ac3f0b81d92ca7d48fdea717f07` + 脚表 `a4270120454aedf7a23c92cd8985c8a6` + BOM `5d02bece9477ffce5fbe0193c7d5cce4` "
        "**逐字节未变** ⇒ ★**零写板 · 零落表**★ "
        "⇒ ★**待 main 另行落笔的两条 need (本脚本在 pm.yaml 代录答案): `iss285_sw_apply_after_iss283_verified` 与 "
        "`iss288_main_verify_sign_issue_log` + `iss288_sw_timing_check_patch_landed` 三条 to=main 的 need 已由本单履行完毕 ⇒ 标 answered★**"
    )
    i288["note"] = (i288.get("note") or "") + (
        " | 2026-11-17 15:5x (cron fb67af40 队列自动派活) ★main 独立复验通过 ⇒ 落 verified★ "
        "⇒ 依据 = 本机实跑 timing_check.py rc=0 (SELFTEST 72/72) + md5 68c4becf… 与 ISS-285 期望值逐字一致 + 交卷单 43335 B / 待写 0 处 "
        "+ merge rc=0 + gate_check rc=0 (Q1 18/18) + 板/网表/脚表/BOM 五个 md5 逐字节未变 "
        "⇒ ★**sw-lead 名额已释放 ⇒ 本轮新派 ISS-291 (ADC 域口径订正 + 逐链判决)★** ★"
    )
    print("✅ ISS-288 fixing → verified (main 独立复验)")

    # ---------- ② 新开 ISS-291 ----------
    assert "ISS-291" not in by_id, "ISS-291 已存在 ⇒ 不重复开单"
    with open(BRIEF_P, encoding="utf-8") as f:
        brief = f.read()
    assert "iss223_sw_vdet_fs_domain_fix" in brief
    i291 = {
        "id": "ISS-291",
        "title": (
            "★★[主线内·SW 侧·判据口径收口 + 机器闸类·内部活] ★★【ADC 域口径订正: `SW/tools/timing_check.py` 的 "
            "`DEVICE[\"V_DET_FS\"] = 3.3` 对 BAT_DET 链是错的 (它 1.8V 域) ⇒ 漏电偏移 %FS 偏小 1.83 倍 + 静态功耗分子口径错 "
            "(落表台账写死 26.25µA @4.2V/160k) + 【装机链判决只看第一条链】⇒ BAT_DET 那条链从来没被判过】★★ "
            "⇒ ★**纯分析 + 机器闸 · 零写板 · 零落表 · 零改网表真源★** ⇒ ★**机器闸必须带反向用例 (FS 错 ⇒ 红 / 分压对值错 ⇒ 红 / "
            "真源被换 ⇒ 红) + 逐链输出 (FS / R_th / τ / t_settle / 偏移 mV 与 %FS / 静态功耗 µA / 可用性结论)★**"
        ),
        "severity": "high",
        "source_blocker": None,
        "source_agent": "main",
        "desc": (
            "★main 2026-11-17 15:3x~15:4x 本机实读 + 实跑 (不抄任何 agent 报告)★\n"
            "★**① 病灶**: `SW/tools/timing_check.py` L81 `\"V_DET_FS\": 3.3` 是一个**全局常量**, 而 F4 段同时判**两条** ADC 分压链 "
            "(VBUS_DET_D 与 BAT_DET) ⇒ 两条链的 ADC 域根本不是同一个\n"
            "★**② 实跑现状** (`python3 SW/tools/timing_check.py --json`): active_chain=VBUS_DET_D · rth=500000Ω · τ=50.0ms · "
            "t_settle=450.546ms · leak_offset_v=0.5 · leak_offset_pct_fs=15.2 · standby_ua=1.65 ⇒ ★**BAT_DET 链 (100k+60k+100nF ⇒ "
            "R_th=37500Ω) 自己的偏移/建立时间/静态功耗一个数都没算** ⇒ 「装机链判决只看第一条链」\n"
            "★**③ 判决锚 (落表台账写死)**: `HW/netlist_v1.csv` L182 note「R_th=37.5kΩ ⇒ 1µA 漏电 ⇒ 37.5mV 偏移 (2.1% FS) · 常开静态功耗 "
            "26.25µA / 110µW」⇒ ★**反推 FS = 37.5mV ÷ 2.1% ≈ 1.786V ≈ 1.8V** ⇒ ★**用 3.3V 算同一条链只有 1.14% FS ⇒ 偏差 1.83 倍**; "
            "静态功耗那条反推 = **4.2V ÷ 160kΩ** (电池电压上限, 不是 ADC 满量程) ⇒ ★**分子口径错**\n"
            "★**④ 域电压**: `HW/netlist_v1.csv` L181 note「电平 0-1.8V (分压, SARADC_VIN5 1.8V 域)」[实测·落表网表] ⇒ ★**但那条 note 的原始出处 "
            "`FET3572C_PIN_TABLE.csv` 在本仓不存在** ⇒ ★**域电压权威来源缺失 ⇒ 必须标 [0数据] + 写降级方案 (降级 = 取落表网表已登记的 1.8V + "
            "登记 need 给 main) ⇒ 不许外发问原厂**\n"
            "★**⑤ 另一条链 (只查不改)**: VBUS_DET_D = RAIL_DEMO_5V 5V ⇒ 1M+1M ⇒ 中点 2.5V ⇒ ★**若 `J_SOM_P1 pin100` (USB_DRD1_VBUSDET, "
            "球位 B28) 是 1.8V 域 ⇒ 2.5V 超绝对最大值 ⇒ 那是板级缺陷 (要改板那一趟一起改) ⇒ SW 侧只查清 + 给结论 + 登记 need**\n"
            "★**⑥ 这条 need 已经挂了**: `state/fragments/hw.yaml` 里 need `iss223_sw_vdet_fs_domain_fix` (since 2026-11-16 · to=sw-lead) "
            "至今 pending ⇒ ★**本单就是来做掉它的** ★"
        ),
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": ["iss223_sw_vdet_fs_domain_fix"],
        "fix_ref": "",
        "verify_by": "main",
        "verify_result": "",
        "verify_date": "",
        "note": (
            "2026-11-17 15:5x (cron fb67af40 队列自动派活) 新开 ★**依据 = main 15:3x~15:4x 本机实读 (`SW/tools/timing_check.py` L81/L1138~L1156 · "
            "`HW/netlist_v1.csv` L181~L186 · `HW/RK3572_PIN_TABLE/` 实目录) + 本机实跑 (`timing_check.py --json`)★ "
            "⇒ ★**性质 = 纯分析 + 机器闸类 · 零写板 · 零落表 · 零改网表真源** ⇒ ★**主板要对着一个不再变的网表画, 这一单只许判据不许动真源** ★ "
            "⇒ ★**机器闸必须带反向用例, 只测「改对之后是绿的」不算★** ★"
        ),
        "dispatched_at": "",
        "task_brief": brief,
    }
    issues.append(i291)
    print("✅ ISS-291 已开 (owner=sw-lead · status=open · brief %d B)" % len(brief))

    with open(LOG_P, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)

    # 回读校验
    with open(LOG_P, encoding="utf-8") as f:
        chk = yaml.safe_load(f)
    st = {i["id"]: i.get("status") for i in chk["issues"]}
    print("   回读: ISS-288 = %s · ISS-291 = %s · 总条数 = %d" % (st.get("ISS-288"), st.get("ISS-291"), len(chk["issues"])))
    print("   备份 = %s" % bak_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
