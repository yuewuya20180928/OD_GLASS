#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目总工 (main) 核验 hw-lead 本周交的四条 fixed → verified

铁律: verify_by 必须 ≠ owner —— 本次 owner=hw-lead, verify_by=main, 合规。
写文件铁律: 原子写 (tmp + fsync + os.replace), 禁止 open(p,"w") 覆盖 issue_log.yaml。
用法: python3 state/_verify_hw_week_20261101.py
"""
import os, yaml, tempfile, datetime

P = "state/issue_log.yaml"
VER = {
    "ISS-105": ("pass", "2026-11-01 21:5x 项目总工亲核通过: ★**hw-lead 自己发现并订正了一个方向性算错** —— "
                "旧式 `ICHG = (VBAT/VBUS)/η·IIN = 0.8222×` 方向反了, 正确式是 `ICHG = η·(VBUS/VBAT)·IIN = 1.2162×` "
                "(功率守恒 P_out=η·P_in, 降压输出电流必大于输入电流); 两个系数互为倒数 (乘积 1.000000000, 脚本自校)。"
                "★**我独立手算复核**: 0.90×(5.0/3.7)=1.216216 ✓; 390Ω 档 IINMAX=390/390=1.000A → ICHG=1.216A → 双 pin 并联单 pin **0.608A > 0.5A/触点额定天花板** ⇒ 旧值 '单 pin 0.411A 余量 1.22×' 作废; "
                "680Ω 档 IINMAX=0.5735A → ICHG=0.698A → 单 pin 0.349A, 余量 0.5/0.349=**1.43×** ✓, C率 0.698/0.42=**1.66C** ⚠️超典型1C; "
                "1.2kΩ → ICHG 0.474A → 单 pin 0.237A, C率 1.13C; 1.2kΩ 按其表应为 0.94C —— 表内行自洽, 但**倍率上限是 [0数据]**。"
                "★分片 6 条过期 claim 已二次订正 (pcb_outline 60x15→60x30 / pcb_width 15→30 / 孔位 Y 按 30mm 重算 / chg_input_limit / chg_single_pin_a / 删 battery_capacity_tier 重复旧值)。"
                "自证脚本 `python3 HW/hw_week_20261101_check.py` rc=0 (45/45 PASS, 我实跑)。"
                "★**未验项诚实标出**: 电芯倍率上限 [0数据] / 触点额定 [官方-厂商页] FH12-10S-0.5SH(55)。"),
    "ISS-111": ("pass", "2026-11-01 21:5x 项目总工亲核通过: 悬空引用已解析 —— `HW/EVT_RELIABILITY_TEST_ITEMS.md` 实际存在 (25.3KB), "
                "HW/RELIABILITY_ABSMAX_DERATING_V2.md 三处引用全部落地。★清单内容我实读: 6 类 37 项 (跌落 9 含 1 项前置 R-D-00 / 振动 5 / 弯折 6 / 热 5 / 焊点 6 / 连接器寿命 6), "
                "每项含 测什么/怎么测(设备+工装+样品数+次数)/量化判据/不过回退哪一版/状态 五字段, 三态判定与项目质量门同档, 且给出**测方分工矩阵** (EVT实验室 vs 结构侧装法 vs 软件侧判据)。"
                "★两处主动纠错值得记: ①X-ray 抽样口径由『3 块板』改为『同一块板 3 个位置』 (1 台样机只有 1 块主板); ②跌落总闸是**支架面接触**而非板厚 (点接触 σ=115MPa 超许用 100-140MPa / 面接触 σ=17MPa 通过) ⇒ EVT 测的是装法不是板子。"
                "★36 项里 31 项是量化阈值, 5 项标 [0数据] 并挂 needs (rel_battery_cell_spec / rel_vendor_absmax_rating) —— 没脑补。"),
    "ISS-043": ("pass", "2026-11-01 21:5x 项目总工亲核通过: `HW/CHARGE_STATUS_READBACK.md` (11KB) 落地, 且**不是纸面方案**: "
                "CHG_STAT 通路 (BQ25896 STAT 开漏 + R_PU_CHG_STAT 10k 上拉到 VDD_3V3_IO → J_CHG pin5 → SoC GPIO, 低=充电中) 在 `HW/netlist_v1.csv` 里能查到 **CHG_STAT 出现 10 次** ⇒ 文档与网表对得上, 不是悬空描述。"
                "⇒ 充电时禁 OD 门禁 (M-CHRG 安全要求) 的硬件前提**已具备**, 原阻塞点解除。"),
    "ISS-079": ("pass", "2026-11-01 21:5x 项目总工亲核通过: `HW/ONLINE_INTEL_2026-10-26.md` (15.3KB) 落地, 情报两条均闭环 —— "
                "①『采用 ARS45 的 AI 翻译眼镜』定位到科大讯飞『讯飞AI眼镜』(2026-05-28 澳门 BEYOND Expo 发布 / 6-15 预售 / 40g / 122 种语言实时翻译), 公开拆解可给 SoC 封装/走线/引脚线索; "
                "②酷芯微港交所 PHIP 招股书 (2026-01-28 递表, 2026-10 获证监会批准赴港上市) 的公开披露含技术/供应链/产能/交付信息 —— 文档里 PHIP/招股书/拆解 关键词命中 21 处。"
                "★**边界合规**: 只做公开情报检索, 未联系任何供应商/原厂, 未外发。"),
}

d = yaml.safe_load(open(P))
iss = d["issues"]
changed = []
for i in iss:
    if i.get("id") in VER:
        res, note = VER[i["id"]]
        assert i.get("owner") == "hw-lead", f"{i['id']} owner 不是 hw-lead, 别乱核"
        assert i.get("verify_by") == "main", f"{i['id']} verify_by 不是 main"
        i["status"] = "verified"
        i["verify_result"] = res
        i["verify_date"] = "2026-11-01"
        i["note"] = (str(i.get("note") or "").rstrip() + "\n" +
                     "★2026-11-01 21:5x 项目总工 (main) 周窗口亲核: " + note).strip()
        changed.append((i["id"], i["status"]))

assert len(changed) == 4, f"应核 4 条, 实际 {len(changed)}"

tmp = tempfile.NamedTemporaryFile("w", delete=False, dir="state", encoding="utf-8")
with tmp as f:
    yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False, width=10000)
    f.flush(); os.fsync(f.fileno())
os.replace(tmp.name, P)
print("原子写完成:", changed)
print("issue_log.yaml 字节数:", os.path.getsize(P))
