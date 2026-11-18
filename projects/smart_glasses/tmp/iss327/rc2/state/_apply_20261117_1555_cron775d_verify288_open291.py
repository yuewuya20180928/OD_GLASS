#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 15:5x · job 775d9893「ARS45 继续执行后继计划」
★ISS-288 落 verified (main 独立复验) + 新开 ISS-291 (owner=sw-lead)★
=========================================================================================
★**ISS-288 复验依据 (★main 15:4x~15:5x 本机实跑, 不抄交卷报告★)**:
  · `python3 SW/tools/timing_check.py` ⇒ **rc=0 · 末行 `SELFTEST 72/72 通过, rc=0`** (开工前 rc=1 · 68/71 三条红)
  · 补丁 md5 `SW/tools/timing_check.py` = `68c4becffe6bcd708e388dba9d18a505` (★= ISS-285 交卷单写死的期望值, 逐字一致★)
  · 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md` = 555 行 / 43335 B / md5
    `e6662435a1671dada9793b5c03470168` ⇒ §0~§8 九节齐全 (★占位符扫描 0 处真实空白★)
  · 受保护 5 件逐字节未变: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro`
    `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6`
    · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ **零写板 · 零落表 成立**
  · `state/fragments/sw.yaml` ⇒ artifacts 3 条 (含 `SW/patches/ISS-288_timing_check_land/verify_iss288_land.py`)
    + interface_claims 3 条 (含 `iss288_handoff_b1_b8_filled_cont2`) + needs_from 2 条 ⇒ **交付物齐**
  · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18) · `state/issue_check.py` rc=0 ⇒ 三道总闸全绿
★**ISS-291 (本 job 新开, owner=sw-lead)**: SW 侧 ADC 判据的【判决对象 + 满量程口径】双错
  ⇒ `DEVICE["V_DET_FS"] = 3.3` (脚本写死) vs 官方 SARADC_VIN5 = 1.8V 域 (`FET3572C_PIN_TABLE.csv:39`
  + `rk3572_datasheet_V1.1.txt:2454/2863/2864`) ⇒ 漏电偏移 %FS: 网表 note 2.1% vs SW 闸 15.2% (差 7 倍)
  ⇒ 且 F4 取链规则 = 「元组顺序第一条 populated」⇒ 判的是 VBUS_DET_D (→ pin100 = USB_DRD1_VBUSDET 数字脚),
  真 ADC 链 BAT_DET (→ pin38 = SARADC_VIN5) 一条判据都没有 ⇒ **本单 = 纯判据口径 + 机器闸 · 零写板 · 零落表**
★**纪律**: verify_by=main (干活的人不许自签) · ★不碰: 任何真源文件 / 任何分片 (★sw.yaml 是 sw-lead 的, main 不写★) /
  板 / 网表 / 脚表 / BOM / 决策页 / outbox / 兄弟 job 的 ISS-289 / ISS-290
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_1555_cron775d_verify288_open291"
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-291_sw_adc_fullscale_domain_reconcile.md")
TODAY = "2026-11-17"

VERIFY_288 = (
    "★main 2026-11-17 15:4x~15:5x 本机独立复验 (不抄交卷报告)★ ⇒ `python3 SW/tools/timing_check.py` "
    "**rc=0 · 末行 `SELFTEST 72/72 通过, rc=0`** (★开工前 rc=1 · 68/71 三条红★) ⇒ 补丁 md5 "
    "`SW/tools/timing_check.py` = `68c4becffe6bcd708e388dba9d18a505` (★= ISS-285 交卷单写死的期望值, 逐字一致★) ⇒ "
    "交卷单 `HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md` = **555 行 / 43335 B / md5 "
    "`e6662435a1671dada9793b5c03470168`** ⇒ §0~§8 九节齐全 (★占位符扫描 0 处真实空白, 4 处命中全是正文里"
    "「0 处空白占位」这句自述★) ⇒ 受保护 5 件逐字节未变 (板 `611b869e…` · `.kicad_pro` `3e504d2b…` · 网表 "
    "`37f62ac3…` · 脚表 `a4270120…` · BOM `5d02bece…`) ⇒ **零写板 · 零落表 成立** ⇒ `state/fragments/sw.yaml` "
    "artifacts 3 条 + interface_claims 3 条 + needs_from 2 条 ⇒ **交付物齐** ⇒ `state/merge.py` rc=0 · "
    "`state/gate_check.py` rc=0 (Q1 18/18) · `state/issue_check.py` rc=0 ⇒ 三道总闸全绿 ⇒ **本条闭环** ★\n"
    "★**留给 sw-lead 的一件 (★main 不越界写他的分片★)**: need `iss285_sw_apply_after_iss283_verified` 的前提"
    "已满足 (ISS-283 已 verified + 补丁已落盘) ⇒ **由 sw-lead 自己标 `resolved_by: ISS-288`** ⇒ 已写进 ISS-291 任务书 ★"
)

TITLE_291 = (
    "★★[主线内·SW 侧·ADC 判据口径收口+机器闸类·内部活] ★★【SW 侧 ADC 判据的【判决对象 + 满量程口径】双错】★★ "
    "⇒ ★**满量程**: 脚本写死 `DEVICE[\"V_DET_FS\"] = 3.3` (3.3V 域) vs 官方 `SARADC_VIN5` = **1.8V 域** "
    "(`FET3572C_PIN_TABLE.csv:39` 实测 + `rk3572_datasheet_V1.1.txt:2454/2863/2864` 官网) ⇒ ★**漏电偏移 %FS: "
    "网表 note 写 2.1% vs SW 闸算 15.2% (差 7 倍, 同一分压链两个数)★** ⇒ ★**判决对象**: F4 取链规则 = 「元组顺序第一条 "
    "populated」⇒ 判的是 `VBUS_DET_D` (→ `J_SOM_P1 pin100` = `USB_DRD1_VBUSDET` **数字脚**) ⇒ ★**真 ADC 链 "
    "`BAT_DET` (→ `J_SOM_P1 pin38` = `SARADC_VIN5`) 一条判据都没有**★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM 真源**★ "
    "⇒ ★**产出 = 口径改对 (FS 1.8V + 取链按「落点是不是 ADC 脚」) + 反向用例 + 与网表 note 逐字对齐 (2.1% FS) + "
    "硬件后果只登记 need 不自己改**★"
)

DESC_291 = (
    "★main 2026-11-17 15:4x~15:5x 本机实读 + 实跑 (不抄交卷报告)★\n"
    "★**① 满量程口径错 (★两源不同, 错的是脚本★)**: `SW/tools/timing_check.py:81` 写死 "
    "`\"V_DET_FS\": 3.3,  # V   SoC ADC 满量程 (3.3V 域) [网表 P2 RAIL_VDD_3V3_IO]` ⇒ 而本板唯一用的 ADC 脚 = "
    "`J_SOM_P1 pin38` = `SARADC_VIN5` = **1.8V 域** (★`HW/PCB/FET3572C_PIN_TABLE.csv:39` 逐字 "
    "`P1,38,1AE17,SARADC_VIN5,——,1.8V,General ADC5,SARADC_VIN5`★) ⇒ 官方 datasheet §3.10 Table 3-16 "
    "(★`HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt:2454` `SARADC Analog Power(1.8V) SARADC_AVDD1V8 "
    "1.62 1.8 1.98 V` · `:2863` `Resolution … 12 Bit` · `:2864` `Anglog Input Range AIN AVSS18 NA AVDD18 V`★) ⇒ "
    "★**⇒ 满量程 = 1.8V, 不是 3.3V** ★\n"
    "★**② 后果数字 (★main 本机按现有公式手算, 与盘面输出逐字对得上★)**: LSB 0.806 mV (3.3) vs **0.440 mV (1.8)** · "
    "漏电偏移 %FS **15.2%** (3.3) vs **2.1%** (1.8) ⇒ ★**★而网表 `HW/netlist_v1.csv:182` 的 note 自己写的是 "
    "「R_th=37.5kΩ ⇒ ADC 输入漏电 ~1µA 只造成 37.5mV 偏移 (2.1% FS, 可软件标定)」★ ⇒ ★★网表按 1.8V FS 写的, "
    "SW 闸按 3.3V FS 写的 ⇒ 同一个 BAT_DET 分压链, 项目里有两个数, 差 7 倍★★ ★\n"
    "★**③ 判决对象错 (★比满量程错更隐蔽★)**: F4 (★`SW/tools/timing_check.py` 约 L1110~L1157★) 的取链逻辑 = "
    "`act = [c for c in det_chains if c[\"populated\"]] or det_chains` + `act[0]` ⇒ ★**永远取元组顺序第一条 "
    "populated = `VBUS_DET_D`, 判据【从不看这条链落到哪个脚】★** ⇒ 而两条链落点完全不同: `VBUS_DET_D` "
    "(★网表 L434~L438 必装 1M/1M + 100nF★) 落到 ★`HW/netlist_v1.csv:439` `J_SOM_P1 pin100`★ = "
    "`USB_DRD1_VBUSDET` (★`FET3572C_PIN_TABLE.csv:101` 逐字: `P1,100,B28,USB_DRD1_VBUSDET,——,——,USB2_OTG1_"
    "VBUSDET insert detection` ⇒ **USB OTG 插入检测 = 数字输入脚**)★ ⇒ ★**把 USB 数字脚当 12bit SAR-ADC 在算建立"
    "时间/漏电偏移/满量程**★; 真正的 ADC 链 `BAT_DET` (★网表 L182~L186 必装 100k/60k/100nF★) 落到 ★L186 "
    "`J_SOM_P1 pin38` = `SARADC_VIN5`★ ⇒ ★**一条判据都没有** ★\n"
    "★**④ 盘面实测的错位后果 (main 15:4x 实跑原样)**: `active_chain : VBUS_DET_D` · `源阻抗 500000.0Ω / τ=50.0ms` · "
    "`12bit 精度需 451ms 建立` · `1µA 漏电流 ⇒ 0.50V 偏移 (15% 满量程)` · verdict 「★★该分压值对 ADC 不可用★★」 ⇒ "
    "★**★这是【对象错 + 满量程错】双重错之后得到的一条红; 而真 ADC 链自己站得住: R_th=37.5kΩ · τ=3.75ms · 12bit "
    "建立 33.8ms · 漏电 37.5mV=2.1% FS (与网表 note 逐字一致) · @4.2V 节点 1.575V ≤ 1.98V abs-max ⇒ 不是问题★** ★\n"
    "★**⑤ 为什么必须在「板只改一次」那一趟之前做完**: ★**板是照着网表画的 ⇒ 网表 note 说 2.1% FS 而 SW 闸说 15% ⇒ "
    "带着这条红去改板, 改完还是红的 ⇒ 板要白改第二遍 ⇒ 判据口径必须先钉死, 板才能一次改对** ★\n"
    "★**⑥ 名额理由**: ISS-288 已由 main 复验落 verified ⇒ sw-lead 名额空出; hw-lead 被 ISS-289 占 (在飞) · "
    "mech-lead 被 ISS-290 占 (在飞) ⇒ ★**本单是此刻唯一能合法派出去的内部活** ★"
)

NOTE_291 = (
    "2026-11-17 15:5x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 15:4x~15:5x 本机实读 "
    "`SW/tools/timing_check.py:81` / F4 取链代码 / `HW/netlist_v1.csv:181~186 + :434~439` / "
    "`HW/PCB/FET3572C_PIN_TABLE.csv:39 + :101` / `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt:2454/2863/2864` "
    "+ 实跑 `python3 SW/tools/timing_check.py` (rc=0 · 72/72)★** ★\n"
    "⇒ ★**任务书全文 = `state/dispatch_briefs/ISS-291_sw_adc_fullscale_domain_reconcile.md` (★已过 "
    "`python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ★\n"
    "⇒ ★**口径**: **纯判据口径 + 机器闸 · 零写板 · 零落表 · 零改 `HW/` · 零碰 `MECH/`** ⇒ ★**符合老板 2026-11-17 "
    "00:43「PCB 类先派纯分析/作业包类」纪律** ★\n"
    "⇒ ★**跨域纪律**: 若结论指向硬件要改 ⇒ **只登记 need 给 main**, 由 main 进「板只改一次」那一趟 ⇒ **本单不许改 "
    "网表/脚表/BOM/板** ★\n"
    "⇒ ★**受保护 5 件本 job 15:4x 实测**: 板 611b869e… (mtime 2026-11-06 07:07:17) · .kicad_pro 3e504d2b… · "
    "网表 37f62ac3… · 脚表 a4270120… · BOM 5d02bece… ⇒ 零写板 · 零落表 成立 ★"
)


def main():
    with open(BRIEF, encoding="utf-8") as f:
        brief_text = f.read()
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {i.get("id"): i for i in issues}

        # ── ISS-288: fixing → verified (main 独立复验) ──
        i288 = by_id.get("ISS-288")
        if i288 is None:
            print("⚠ ISS-288 不存在")
        elif i288.get("status") == "verified":
            print("· ISS-288 已是 verified ⇒ 幂等跳过")
        else:
            i288["status"] = "verified"
            i288["verify_by"] = "main"
            i288["verify_result"] = "pass"
            i288["verify_date"] = TODAY
            i288["fix_ref"] = "HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md"
            i288["note"] = (i288.get("note") or "") + "\n\n★★ **main 2026-11-17 15:5x 复验落 verified** ★\n" + VERIFY_288
            print("· ISS-288 fixing → verified (main 独立复验)")

        # ── ISS-291: 新开 (owner=sw-lead) ──
        if "ISS-291" in by_id:
            print("⚠ ISS-291 已存在 ⇒ 幂等跳过")
        else:
            issues.append({
                "id": "ISS-291",
                "title": TITLE_291,
                "severity": "high",
                "source_blocker": None,
                "source_agent": "main",
                "desc": DESC_291,
                "owner": "sw-lead",
                "reporter": "main",
                "raised": TODAY,
                "due": "2026-11-20",
                "status": "open",
                "external": False,
                "need_keys": [],
                "fix_ref": "",
                "verify_by": "main",
                "verify_result": "",
                "verify_date": "",
                "note": NOTE_291,
                "dispatched_at": "",
                "task_brief": brief_text,
            })
            print("· ISS-291 已开 (owner=sw-lead, status=open, due=2026-11-20)")

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
