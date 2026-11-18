#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0705_ti_research_and_due.py
★main 2026-11-16 07:0x · 按老板 2026-11-12 02:02「不再发信, 全靠自己查资料」结掉 ISS-095 / ISS-102 + 逾期未闭环项 due 顺延 (★逐条写清卡点★)★
"""
import os
import shutil
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

BOSS_NOTE = ("★2026-11-16 07:0x due 顺延到 2026-11-18: ★**本条已列进 `DECISION_PENDING_2026-11-16.md` (★§A/§B/§C★) ⇒ 等老板在决策窗口拍** ★ "
             "⇒ ★**顺延的是【催办时间】, 不是【已定时间】; 本条 status 保持 open (★真的还没拍★)** ★")

MAIN_NOTES = {
 "ISS-109": "★卡点 = R-GEO 六问 (问03 ISP 吞吐余量 1.9% vs 50.7% 完全相反 ⇒ 一票否决级) ⇒ ★**按 11-12 02:02 政策不再等原厂回信 ⇒ 改为 main 自查公开资料 (RK3572 ISP/TRM) + 查不到写降级方案** ★ ⇒ due 顺延到 11-19 ★",
 "ISS-125": "★卡点 = R-GEO 其余五问 (问 01/02/04/05/06 仍是 0 答复) ⇒ ★**同 ISS-109: 政策已改为自查公开资料, 不再等回信** ★ ⇒ due 顺延到 11-19 ★",
 "ISS-131": "★卡点 = 问询口径改 RK3572 (ISP 16M→12M / CSI 3×→2×) + 球位号对象 ⇒ ★**政策已改为【自己查官方手册/引脚表】⇒ 项目内已有 RK3572 官方引脚表 (`HW/RK3572_PIN_TABLE/`) 可直接查** ★ ⇒ due 顺延到 11-19 ★",
 "ISS-126": "★卡点 = 板厚档位未定 ⇒ 检修口净空 ⇒ ★**属 PCB/板类 ⇒ 按老板 11-11 10:07「PCB 布线/布局类不派, 排队等原理图定稿」⇒ 继续排队** ★ ⇒ due 顺延到 11-20 (随板那一趟) ★",
 "ISS-128": "★卡点 = RK3572 (FCCSP550L 14.3×15.5mm / 550 球) 板面积账 + 逃线层数重算 ⇒ ★**属 PCB/板类 ⇒ 继续排队** ★ ⇒ due 顺延到 11-20 (随板那一趟) ★",
 "ISS-129": "★卡点 = 板端纯 NPU 实测 ⇒ ★**本机无板 ⇒ 等板那一趟** ★ ⇒ due 顺延到 11-20 (随板那一趟) ★",
 "ISS-130": "★卡点 = RK3572 功耗 670mW (原厂口径) vs 贴皮肤 43°C 红线 ⇒ ★**原厂口径不能判 ⇒ 上板实测才可判** ★ ⇒ due 顺延到 11-20 (随板那一趟) ★",
 "ISS-133": "★卡点 = 显示架构变更 (「屏」≠「光机」⇒ 须新增一级耦合光学 ⇒ 镜框光学腔体/分光器/整机空间全算) ⇒ ★**属整机/光学腔体 ⇒ 按老板 11-02「结构不考虑」口径延后到整机阶段** ★ ⇒ due 顺延到 11-20 ★",
 "ISS-155": "★卡点 = rk3572 不是 rknn-toolkit2 合法 target ⇒ ★**内部可做, 不等外部 (★本条是 demo 头号卡点★) ⇒ 等 sw-lead 名额 (★本轮 sw-lead 在跑 ISS-234, 下一轮派★)** ⇒ due 顺延到 11-19 ★",
 "ISS-156": "★卡点 = 三件前置选型 (camera 模组 / 屏模组 / RK3572 核心板) ⇒ ★**待 main 选型; 屏版本已列决策页 §A6 (等老板拍全彩版/单色绿版)** ★ ⇒ due 顺延到 11-19 ★",
 "ISS-160": "★卡点 = 图纸链剩余 (密集布线 / 打样) ⇒ ★**属 PCB/板类 ⇒ 继续排队** ★ ⇒ due 顺延到 11-20 (随板那一趟) ★",
 "ISS-169": "★卡点 = SoM 座 pin1 排向待查证 + 15 个器件封装脚号待落定 ⇒ ★**属 PCB/板类 ⇒ 继续排队** ★ ⇒ due 顺延到 11-20 (随板那一趟) ★",
 "ISS-172": "★卡点 = 负载开关 U_PWR_SW / U_EN_SW 原厂在售型号判据互斥 (RON vs IQ vs 反向阻断) ⇒ ★**已由新开 ISS-234 (sw-lead) 出【优先级序 + 2×2 方案表 + 硬件最小需求清单】⇒ 本条等 ISS-234 交卷 + 老板拍 §A5** ★ ⇒ due 顺延到 11-19 ★",
}


def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    by_id = {i.get("id"): i for i in log["issues"]}

    # ---------- ISS-095: 自查 TI 官网 ⇒ 结掉 ----------
    i95 = by_id["ISS-095"]
    assert i95.get("status") == "open"
    i95["status"] = "fixed"
    i95["due"] = "2026-11-19"
    i95["verify_result"] = (
        "★main 2026-11-16 06:4x~07:0x 自查 TI 官网 ⇒ 已结 (★按老板 11-12 02:02 政策, 不再等原厂回信★)★\n"
        "· ★**结论 [官网]**: ★**BQ25896 的 SYS/VSYS 脚【必须接】** ⇒ TI bq25896 datasheet (SLUSC76C) §7 Pin Configuration and Functions 逐字: "
        "\"The internal BATFET is connected between BAT and SYS. When the battery falls below the minimum system voltage, switch-mode converter keeps SYS above the minimum system voltage. "
        "**Connect a 20uF closely to the SYS pin.**\" ⇒ ★**⇒ 原裁「VSYS(pin15/16) 不接」不成立** ★\n"
        "· ★**但【不需要】把系统轨跨铰链引到镜脚** ⇒ §10.2.2.3 System Output Capacitor 逐字: \"For good loop stability, 1-µH and minimum of 20-µF output capacitor is recommended\" ⇒ "
        "★**20 µF 可留在充电板本地 (紧靠 SYS 脚), 不必连到负载** ⇒ ⇒ ⇒ ★**「多两根 J_CHG 电源 pin」的回退分支【不需要】** ★\n"
        "· ★**电压窗口 [官网]**: VSYS(MIN) = 3.50 V (SYS_MIN 默认 3.5V) · VSYS(MAX) = 4.40 V (§6) ; 典型应用 SYS 10 µF + BAT 10 µF (§10.2) ★\n"
        "· ★**落表口径建议**: 「充电板 SYS 脚不接跨铰链系统轨, 但必须按 TI 规格挂 20 µF 到地 (紧靠 SYS 脚); 充电板无系统侧负载时由 buck 把 SYS 维持 ≥3.5 V」 ★\n"
        "· ★**证据全文与复现命令**: `HW/TI_POWER_FACTS.md` §① (★main 自产 ⇒ 待 hw-lead 复核; verify_by 仍为 hw-lead, 本条状态落 fixed 等复核★) ★"
    )
    i95["note"] = (i95.get("note") or "") + (
        "\n2026-11-16 07:0x ★**按 11-12 02:02 政策改成【自己查官网】⇒ TI datasheet 已给出明确答案 ⇒ 本条不再等回信 ⇒ 落 `fixed` (待 hw-lead 复核后落 verified)** ★"
    )

    # ---------- ISS-102: 4 问 → 3 问已答 + 1 问作废 ----------
    i102 = by_id["ISS-102"]
    assert i102.get("status") == "open"
    i102["status"] = "fixed"
    i102["due"] = "2026-11-19"
    i102["verify_result"] = (
        "★main 2026-11-16 06:4x~07:0x 自查官方材料 ⇒ 4 问里 3 问已答, 1 问作废 (★按 11-12 02:02 政策, 不再等回信★)★\n"
        "· ★**① ARS45 的 AON/唤醒脚与静态电流 ⇒ 【问法作废】**: ★**ARS45 / AR9481 / 酷芯微 已于 2026-10-29 19:20 拍板作废 ⇒ 「ARS45 的 AON 域」不存在了** ★ ; "
        "替代口径: ★**RK3572 datasheet V1.1 全文检索无 \"AON\" 字样 ⇒ 〔0数据〕SoC 无 datasheet 级 AON 域** ★ ⇒ 降级方案 = 关机续航沿用 ISS-097 §0 第 6 条 ~108 µA / 0.40 mW [推算], AON 项按 0 计 ★\n"
        "· ★**② 有无 dedicated USB VBUS detect 脚 ⇒ 【有, 2 个】[官网]**: RK3572 官方 datasheet V1.1 引脚表 (项目内 `HW/RK3572_PIN_TABLE/rk3572_pins.csv`, 550 球) ⇒ ★**球 1C18 = USB_DRD0_VBUSDET / 球 B28 = USB_DRD1_VBUSDET** ★ ⇒ "
        "★**⇒ VBUS_DET 分压整条可删 (省 50 µA + 2 颗电阻 = ISS-097 §0 第 6 条「关机静态电流最大单项」的直接解法)** ★ ⇒ ★**残余一步: SoM (Forlinx 模组) 是否引出这两球 = 〔0数据·待核〕★** ★\n"
        "· ★**③ TPS62130A 的 PG 极性 ⇒ 【ok=高】[官网]**: tps62130a datasheet 逐字 \"Output power good (High = VOUT ready, Low = VOUT below nominal regulation); open drain (requires pull-up)\" + §9 \"pulls the PG pin Low when the device is shut down by EN, UVLO, or thermal shutdown\" ⇒ "
        "★**⇒ 复位链可按「PG 高 = 就绪」写** ★ ⇒ ★**注意: 与 BQ25896 的 /PG (低有效) 是两个器件两个脚, 文档里必须写清是哪家的 PG** ★\n"
        "· ★**④ BQ25896 的 VSYS 是否必接 ⇒ 【必接 20 µF】[官网]**: ★**已由 ISS-095 结掉** (⇒ §7 原文 \"Connect a 20uF closely to the SYS pin\") ★\n"
        "· ★**证据全文与复现命令**: `HW/TI_POWER_FACTS.md` §①~§④ (★main 自产 ⇒ 待 hw-lead 复核; verify_by 仍为 hw-lead★) ★"
    )
    i102["note"] = (i102.get("note") or "") + (
        "\n2026-11-16 07:0x ★**按 11-12 02:02 政策改成【自己查官方材料】⇒ 3 问已答 + 1 问随 ARS45 作废 ⇒ 本条不再等回信 ⇒ 落 `fixed` (待 hw-lead 复核后落 verified)** ★"
    )

    # ---------- 逾期未闭环项 due 顺延 (逐条写清卡点) ----------
    for iid in ("ISS-038", "ISS-041", "ISS-060", "ISS-063", "ISS-106"):
        it = by_id[iid]
        assert it.get("status") == "open" and it.get("owner") == "boss", (iid, it.get("status"), it.get("owner"))
        it["due"] = "2026-11-18"
        it["note"] = (it.get("note") or "") + "\n" + BOSS_NOTE

    for iid, note in MAIN_NOTES.items():
        it = by_id[iid]
        assert it.get("status") == "open", (iid, it.get("status"))
        it["due"] = "2026-11-19" if "11-19" in note else "2026-11-20"
        it["note"] = (it.get("note") or "") + ("\n2026-11-16 07:0x " + note + " ⇒ ★**顺延的是【催办时间】, 不是【已定时间】** ★")

    shutil.copy2(LOG, LOG + ".bak_20261116_0705_ti_research_and_due")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("OK: ISS-095/ISS-102 → fixed (自查官网已结) · 18 条逾期未闭环项 due 顺延 + 逐条写清卡点")

if __name__ == "__main__":
    main()
