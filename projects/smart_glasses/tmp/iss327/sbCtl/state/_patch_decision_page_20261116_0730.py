#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_patch_decision_page_20261116_0730.py
★main 2026-11-16 07:3x · 决策页更新 (ISS-233 落表结果 + ISS-234 交卷 5 条并进 §A)★
★只改事实与数字, 不替老板拍板 (★"推荐默认值" 仍是推荐, 不是已决定★)★
"""
import os
import shutil

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DECISION_PENDING_2026-11-16.md")

OLD_NEW = []

OLD_NEW.append((
    "> **出页人**: 项目总工 (main / moli) · **时间**: 2026-11-16 06:5x",
    "> **出页人**: 项目总工 (main / moli) · **时间**: 2026-11-16 07:3x (★**本版已并入 ISS-233 落表结果 + ISS-234 交卷的 5 条待拍★)**\n"
    "> ★**2026-11-16 07:2x 本版改动 (★全部 main 自己实跑, 不是抄交卷报告★)**: ★**① ISS-233 落表第 3 批 ⇒ `--expect-resolved` 21 → 18 条 (A 类 3 条已落: 网表 L442 / 脚表 L531 / BOM L208 各一行) ⇒ 剩下 18 条 = V-3 13 条 + V-2+板 3 条 + V-4 1 条 + 板侧 R3 1 条** ★ · ★**② A2 的 0.411A 是过期数 ⇒ 订正为 0.608A (门禁实测逐字)** ★ · ★**③ A4 里「负载开关 0 颗」经 main 逐行复核为【2 颗】(U_PWR_SW L50 + U_EN_SW L442) ⇒ 事实订正 + ISS-234 的 5 条 (Q1~Q5) 并进 §A-补** ★ · ★**④ 网表/脚表/BOM md5 已随落表变 (见页尾「本页数字是怎么来的」)** ★",
))

OLD_NEW.append((
    "现值 390Ω ⇒ 单 pin 0.411A (SKIN 侧 42.1°C ★**该数按旧系数 0.822 算 ⇒ 已作废, 无有效数字**)",
    "现值 390Ω ⇒ 单 pin **0.608 A** (★**main 2026-11-16 07:2x 实测门禁输出逐字: 「390Ω 档单 pin 载流上限 = 0.608 A > 0.5 A 触点额定」★ ⇒ ★**旧的 0.411A 是过期数, 已订正; SKIN 侧 42.1°C 按旧系数 0.822 算 ⇒ 已作废, 无有效数字**★)",
))

OLD_NEW.append((
    "★**实测: 网表里负载开关/电源开关 = 0 颗 ⇒ 没有硬件断电通路 ⇒ 「关机」只能是软件深睡 ⇒ 锁死的「待机 <0.05W」在硬件上不成立**",
    "★**★事实订正 (main 2026-11-16 07:2x 逐行读 `HW/netlist_v1.csv` 实测): 网表里负载开关 = 2 颗 (`U_PWR_SW` 本体行 L50 type=IC + `U_EN_SW` 本体行 L442 type=IC), 不是 0 颗 ⇒ 整机有硬件断电通路 (拓扑割边 = U_PWR_SW) ⇒ 但【demo 板做不到真断电】: ①整机电池链 (`BT_432243`/`U_BATPROT`/`Q1`/`Q2`) 全 DNP ⇒ `U_PWR_SW` 的 VIN 无源 ②demo 的 SoM 供电路径 `RAIL_DEMO_5V`→`J_SOM_P3` 7 根 VCC_DCIN 上零开关 ⇒ SoM 永远带电 ⇒ ⇒ 「关机」在 demo 板只能是深睡 ⇒ ★**锁死的「待机 <0.05W」在整机成立 (≈0.21-0.40 mW), 在 demo 板不成立** ★",
))

OLD_NEW.append((
    "⇒ ★**ISS-234 正在出这页的完整 2×2 方案表, 交卷后我再补一版** ★",
    "⇒ ★**★ISS-234 已交卷 (07:02): 完整 2×2 方案表 + 六格矩阵 + 给你的 5 条 (Q1~Q5) 都在 `SW/SHUTDOWN_SEMANTICS_SPEC.md` §1~§3; 机器门禁 `SW/tools/check_shutdown_semantics.py` rc=0 + `--selftest` 17/17 ⇒ 见本页 §A-补** ★",
))

OLD_NEW.append((
    "★**main 不代排优先级** ★",
    "★**main 不代排优先级** ★<br>★**★ISS-234 交卷给了候选**: ★**Q2 推荐 = `TPS22991RAA`** (★与现有封装 UQFN-4 RAA 同封装 ⇒ 可换料不换板★) + ★**并要求登记「无 RCB (反向电流阻断)」这个缺口** ★",
))

# ---- §A-补: ISS-234 的 5 条 (插在 §A 拍板顺序建议之前) ----
OLD_NEW.append((
    "> ★**§A 的拍板顺序建议**",
    """## §A-补 · ★**ISS-234 交卷后的 5 条待拍 (Q1~Q5)** ★ (★**07:02 交卷 · main 已复核 · 只列不代拍★**)

> ★**出处**: `SW/SHUTDOWN_SEMANTICS_SPEC.md` §3 (交卷单 `HANDOFF/2026-11-16_sw-lead_ISS234_关机语义三口径方案与门禁.md` B5 U-A) · ★**机器门禁**: `SW/tools/check_shutdown_semantics.py` rc=0 (R1~R7) + `--selftest` **17/17** (main 07:2x 实跑) ★
> ★**口径**: 每条 = 问句 + 我的推荐默认值 + 不拍的后果; ★**「推荐默认值」≠「已决定」—— 等你回一个字母** ★

| # | 问句 | 推荐默认值 (★**不是已决定**★) | 不拍的后果 |
|---|---|---|---|
| **Q1** | demo 板要不要「关机」这个状态? | ★**A: 不设独立关机态** (用户词保留, 实现 = 深睡 + 底板断电) | 售后与固件的侧键长按映射各写各的 ⇒ demo 台架「按 10 秒没反应 = 砖机」的返修单持续产生; 且原理图侧不敢动 |
| **Q2** | 整机负载开关选型 (ISS-172) 怎么裁? | ★**A: `TPS22991RAA`** (同封装 ⇒ 可换料不换板) + ★**记录「无 RCB」缺口** | 整机主板 BOM 出不来 (OPN 空着); 「关机态电池会不会被 USB 反灌」无人负责 |
| **Q3** | 关机态静态电流账 (108µA) 怎么标? | ★**A: 维持 108µA / 0.40mW + 标注算式存疑 + 对外写区间 5-11 个月** | 对外功耗口径没有单一数 (三份文档给 5.4 / 8.4 / 5-11 个月) ⇒ §0 与 §6 自相矛盾 1.5 倍 |
| **Q4** | demo 板的「关机时充电灯」怎么办? | ★**A: 不适用** (删掉售后 demo 流程里的充电步骤) | 售后三步排查第 3 步「充电 10 分钟后再试」在 demo 台架上永远是死路 |
| **Q5** | 「长按 10s = 关机」在三处口径冲突时听谁的? | ★**A: 整机=真断电 / demo=深睡+底板断电, 售后文档按载体分两套话** | 「关机」这个词在 demo 台架上变成一句假话 ⇒ 会被写进售后文档 ⇒ 变成验收依据 ⇒ 返修与纠纷的根 |

> ★**★Q1 / Q4 / Q5 与 §A4 同族 (关机语义) ⇒ 一起拍最省事; Q2 与 §A5 同族 (负载开关选型) ⇒ 一起拍★** ★

> ★**§A 的拍板顺序建议**""",
))

# ---- 页尾数字来源更新 ----
OLD_NEW.append((
    "- `--expect-resolved` 21 条构成 (R2×11 / R3×4 / R4×2 / R7×1 / R8×1 / R9×1 / R10×1) ⇒ `python3 HW/check_netlist_selfconsistency.py --expect-resolved` (★**2026-11-16 06:2x 由 main 实跑, rc=1** ★)",
    "- ★**`--expect-resolved` 18 条构成 (★ISS-233 落表后★)**: ★**V-3 13 条 (R2×11 + R7 + R8) · V-2+板 3 条 (R4×2 + R9) · V-4 1 条 (R10) · 板侧 R3 1 条 (板封装 Value)** ★ ⇒ `python3 HW/check_netlist_selfconsistency.py --expect-resolved` (★**2026-11-16 07:2x 由 main 实跑, rc=1, 18 条** ★; ★**落表前同一条命令是 21 条 ⇒ ISS-233 的 A 类落表 21→18** ★)",
))

OLD_NEW.append((
    "- 网表/脚表/BOM/板 md5 ⇒ ★**main 06:4x 实测**: 网表 `3215020b…` · 脚表 `a600afae…` · BOM `92b51580…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ★",
    "- ★**网表/脚表/BOM/板 md5 (★main 2026-11-16 07:2x 实测, ISS-233 落表后的新值★)**: 网表 **`34132f7e…`** (旧 `3215020b…`) · 脚表 **`b21b743a…`** (旧 `a600afae…`) · BOM **`c195a117…`** (旧 `92b51580…`) · 板 `611b869e…` ★**逐字节不变** · `.kicad_pro` `3e504d2b…` ★**逐字节不变** ★ ⇒ ★**这 3 个 md5 的变更 = ISS-233 落表第 3 批 (网表 L442 / 脚表 L531 / BOM L208 各一行) ⇒ SW 侧已走 H-1 重锚 (§1 锚点 by=ISS-233 + R-05 留痕) ⇒ `check_demo_panel_spec.py` rc=0** ★",
))

OLD_NEW.append((
    "- 负载开关 0 颗 ⇒ ★**main 06:5x 逐行读 `HW/netlist_v1.csv` 实测** ★",
    "- ★**负载开关 = 2 颗 (★事实订正: 原写「0 颗」是派单前提错★)**: `U_PWR_SW` 本体行 L50 (type=IC) + `U_EN_SW` 本体行 L442 (type=IC) ⇒ ★**main 2026-11-16 07:2x 逐行读 `HW/netlist_v1.csv` 实测; ISS-234 的机器门禁实测「整机拓扑割边 = ['U_PWR_SW'] / demo 拓扑割边 = 空」⇒ demo 板做不到真断电** ★",
))

OLD_NEW.append((
    "- 关机语义七条结论 ⇒ `HW/POWER_SHUTDOWN_V3.md` §0 (★**main 自产 ⇒ 待你审阅, main 不自签** ★)",
    "- 关机语义七条结论 ⇒ `HW/POWER_SHUTDOWN_V3.md` §0 (★**main 自产 ⇒ 待你审阅, main 不自签** ★) · ★**关机语义 2×2 方案表 + 六格矩阵 + Q1~Q5 ⇒ ISS-234 交卷件 `SW/SHUTDOWN_SEMANTICS_SPEC.md` (07:02) + `SW/tools/check_shutdown_semantics.py` (rc=0 / 17/17)** ★\n"
    "- ★**本轮 main 新开并已派的 2 条 (★cron 775d9893 07:2x★)**: ★**ISS-235 (sw-lead) = ISS-233 落表把 SW 侧 3 条断言打成过期红 ⇒ 订正 F8 / REV-3 / REV-12 (★订正不是放宽★)** ★ · ★**ISS-236 (hw-lead) = 把【V-2/V-3/V-4 拍板即可一键落】做成参数化落表器 (★默认 dry-run, `--apply` 必须带 `--boss-decision` ⇒ 机器化保证「不许替老板拍板」★) + 出【原理图定稿收口清单】** ★",
))


def main():
    with open(P, "r", encoding="utf-8") as f:
        txt = f.read()
    for old, new in OLD_NEW:
        n = txt.count(old)
        assert n == 1, (n, old[:80])
        txt = txt.replace(old, new)
    shutil.copy2(P, P + ".bak_20261116_0730_main_update")
    with open(P, "w", encoding="utf-8") as f:
        f.write(txt)
    print("OK: 决策页更新 %d 处 (★只改事实/数字, 不代拍★)" % len(OLD_NEW))


if __name__ == "__main__":
    main()
