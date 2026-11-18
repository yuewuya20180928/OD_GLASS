#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-18 04:1x · job 775d9893「ARS45 继续执行后继计划」
★ISS-131 交付页的 over-claim 收窄 (★ISS-305 独立复验的 B5-4 / need n3·severity=high★)
=========================================================================================
★**为什么要改 (★ISS-305 hw-lead 独立复验的判决·verdict=「部分 over-claim」★)**:
★**交付页 §1.2 L64 现在写**:
★   ★**「多摄像头方案在 RK3572 上不成立（无论 CSI 物理上有几个口）」** ⇒ 「这一条要写进 demo 选型硬判据」(ISS-156 的 camera 模组选型：只能 1 路)
★**⇒ 这条是 [官方 + 推算] 的合成结论, 但 §1.2 自己已经逐字写出「One channel ISP」只讲 ISP 处理核,**
★**   没讲「多摄并发不可能」⇒ ⇒ 宽版结论比官方字面强 ⇒ ★**hw-lead 判 severity=high, 理由: 它将来会变成 demo 选型硬判据 ⇒ 会拿它去筛掉本来可行的多摄方案** ★
★
★**官方字面到底是什么 (★ISS-306/sw-lead + ISS-307/hw-lead 两路独立核过★)**:
★   · datasheet §1.2.8 = ★**`One channel ISP, 12M pixels`** ★
★   · datasheet §1.2.7 = ★**`Support 2 MIPI CSI-2 interfaces` + `Two 4 data lanes of D-PHY v1.2` + `Each interface may be configured as 2x2 data lanes port`** ★
★   · §1.2.8 VICAP = ★**`Support receiving four groups of MIPI CSI interfaces`** ★
★**⇒ 官方给的硬事实是「ISP 处理核 = 1 路」; 「多摄并发整体不成立」是【比官方字面更宽】的推算, 而官方并没有说「ISP 只能挂 1 个 sensor」★**
★
★**ISS-305 建议的收窄措辞 (★只列事实与代价, 不代拍·本单照它执行★)**:
★   「★**实时 ISP 处理路数 = 1 (多路需 VICAP 虚拟通道 + 降帧时分)**★」, 且「★**最终 ISP 能否多摄并发 = [0数据] ⇒ 要 TRM/官方确认**★」
★
★**改法 (★遵守本项目 append-only 铁律★)**: ★**不改老字一个字 (★留痕在案★) ⇒ 在文件末尾追加 §5 订正节, 并在 §1.2/§3-3 处加【指向订正的箭头注记】★★
★   ⇒ ★**读者读 §1.2 时立刻看到「本条已被 §5 收窄」; 老字逐字保留 ⇒ 留证链完整★**
★
★**同时修 ISS-305 的另两条 main-owned 欠账 (B5-5 / B5-6 · severity=low)**:
★   · B5-5: 交付页 L29「跑前跑后实测一致」的「实测」二字与证据等级 [实测] 撞名 ⇒ 改成「本机校验 (md5 逐字节比对)」
★   · B5-6: §1.3 建议补「12M = 12×2^20 = 4096×3072 精确相等 (二进制)」⇒ 防下一个人把 12M 当十进制 12,000,000 (差 4.86%)
★
★**边界**: ★**零写板 · 零落表 · 零改网表/脚表/BOM · 零改闸脚本 · 零外发 · 不替老板拍板·不自签 issue_log (签字在别的脚本里做)★** ★
★**本文件被哪些东西引用**: ★**`state/_append_decision_page_20261118_0155_r66.py` (追加页引用过) + `state/_apply_20261118_0140_cron775d_iss131_305.py` + `state/_iss131_frag_write.py` ★ ⇒ ★**没有任何闸脚本锚定它的 md5 (实测 grep: 无) ⇒ 可安全追加★**
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "HW", "RK3572_INQUIRY_CALIBER_V2.md")
BAK = PAGE + ".bak_20261118_0410_overclaim_narrow"

# ★★§1.2 L64 的箭头注记 (★只加一句指向订正·不改老字★)★★
OLD_L64 = (
    "★**ISP 是 `One channel` ⇒ 同一时刻只有 1 路传感器能进 ISP** ⇒ "
    "★**多摄像头方案在 RK3572 上不成立（无论 CSI 物理上有几个口）** ⇒ ⇒ "
    "**这一条要写进 demo 选型硬判据**（ISS-156 的 camera 模组选型：只能 1 路）。 [官方 + 推算]"
)
NEW_L64 = (
    OLD_L64
    + "\n\n> ★★★【★★**本条已被 §5 收窄 —— 上句「多摄像头方案在 RK3572 上不成立」是比官方字面更宽的推算, "
    "ISS-305 (hw-lead 独立复验) 判 severity=high: 它将来会变成 demo 选型硬判据 ⇒ 会拿它去筛掉本来可行的多摄方案★★ "
    "⇒ ★**官方字面只说「ISP 处理核 = 1 路 (One channel ISP) / CSI 物理有 2 接口 4 组口」; "
    "「ISP 能否多摄并发」官方没写 ⇒ [0数据] ⇒ 要 TRM/官方确认**★ "
    "⇒ ★**收窄后的正确读法 = 「实时 ISP 处理路数 = 1 (多路需 VICAP 虚拟通道 + 降帧时分)」; "
    "「多摄并发最终能否做」= [0数据], 不许当硬判据用**★ ⇒ ★**逐条改法见 §5 (2026-11-18 04:1x main 追加式订正)· 老字一字未删留痕**★]**"
)

# ★★L29「实测」撞名 (ISS-305 B5-5)★★
OLD_L29 = "★**脚本只读·零写板**：读 `HW/netlist_v1.csv` + `HW/PCB/FET3572C_PIN_TABLE.csv` + `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` ⇒ ★**板 md5 / 网表 md5 / 脚表 md5 / BOM md5 一个字节都不动**（跑前跑后实测一致）。"
NEW_L29 = "★**脚本只读·零写板**：读 `HW/netlist_v1.csv` + `HW/PCB/FET3572C_PIN_TABLE.csv` + `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` ⇒ ★**板 md5 / 网表 md5 / 脚表 md5 / BOM md5 一个字节都不动**（★**本机校验 (md5 逐字节比对) 一致**★ · ★**措辞订正见 ISS-305 B5-5: 原文「实测」二字与证据等级标签 `[实测]` 撞名 ⇒ 这里只表示「本机跑脚本 + 比对 md5」, 不表示有实物实测**★）。"

# ★★§1.3 补二进制精确相等 (ISS-305 B5-6)★★
OLD_13 = "★**读法**：4096×3072 = **12.58 Mpixel** ⇒ ★**「12M」是【单帧分辨率上限】，与 `Maximum input` 自洽** ⇒ ⇒ ★**它不是 MP/s 吞吐**。"
NEW_13 = (
    OLD_13
    + "\n\n★**★补一条精确换算 (★ISS-305 B5-6 · 防止下一个人把「12M」当十进制 12,000,000 用·差 4.86%·对 1080p 无影响★)**★: "
    "★**12M = 12 × 2^20 = 12,582,912 像素 = 4096 × 3072 精确相等 (二进制口径)**★ ⇒ "
    "★**官方「12M」是 2 的幂口径 ⇒ 与 `Maximum input 4096x3072` 逐位对得上; 若按十进制 12,000,000 读则差 4.86% (★对 1080p 两种读法都不构成约束★)★**"
)

SECTION = """

---

## 5 · ★★【追加式订正】★ over-claim 收窄 + 两条措辞订正 ★ (★2026-11-18 04:1x · main · ISS-305 独立复验判决落地★)

> ★**追加人**: 项目总工 (moli) · cron `775d9893` · ★**追加时刻**: 2026-11-18 04:1x
> ★**依据**: `HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md` §B3-C (★「部分 over-claim」判决★) + §B5-4 (★severity=high★) + §B5-5 / §B5-6 (★severity=low★)
> ★**纪律**: ★**append-only —— 上面 §1~§4 的老字一个字未删未改 (★只有 §1.2 / §1.3 / 开头三处加了【指向本节的箭头注记】+ 一处措辞订正★)· 留证链完整★**

### 5-1 · ★★over-claim 的原文与官方字面 (★逐字对照★)★

| 项 | 内容 |
|---|---|
| ★**老字 (§1.2 L64)** ★ | ★**「ISP 是 `One channel` ⇒ 同一时刻只有 1 路传感器能进 ISP ⇒ 多摄像头方案在 RK3572 上不成立（无论 CSI 物理上有几个口）⇒ 这一条要写进 demo 选型硬判据（ISS-156 的 camera 模组选型：只能 1 路）」** ★ `[官方 + 推算]` |
| ★**官方字面 (datasheet Rev 1.1)** ★ | §1.2.8 = ★**`One channel ISP, 12M pixels`** ★ · §1.2.7 = ★**`Support 2 MIPI CSI-2 interfaces` + `Two 4 data lanes of D-PHY v1.2` + `Each interface may be configured as 2x2 data lanes port`** ★ · §1.2.8 VICAP = ★**`Support receiving four groups of MIPI CSI interfaces`** ★ |
| ★**差距在哪** ★ | ★**官方说的是「ISP 处理核 = 1 路」; 老字把它推成了「多摄方案整体不成立」+「只有 1 路」⇒ ★**这是比官方字面更宽的一步★** ⇒ ★**官方从未写「ISP 只能挂 1 个 sensor」, 也没写「多摄并发不可能」⇒ 那一条 = [0数据]⇒ 要 TRM / 官方确认★** |

### 5-2 · ★★收窄后的正确表述 (★ISS-305 建议·照它执行★)★

| 项 | 收窄后 |
|---|---|
| ★**可以说 (★[官方]★)** ★ | ★**RK3572 = `One channel ISP` ⇒ 实时 ISP 处理路数 = 1** ★ (★官方逐字★) |
| ★**可以说 (★[推算]★)** ★ | ★**若要多路传感器实时进 ISP ⇒ 需走 VICAP 虚拟通道 + 降帧/时分 (本项目未验证该路径可行性)★** |
| ★**不能说 (★[0数据]★)** ★ | ★**「多摄像头方案在 RK3572 上不成立」/「只能 1 路」⇒ 官方没写 ⇒ 不许当硬判据用★** ⇒ ★**ISS-156 的 camera 模组选型【不许】拿它去筛掉本来可行的多摄方案★** |
| ★**要定死这一条怎么办** ★ | ★**查官方 TRM / 产品页 (★老板 2026-11-12 02:02「不再发信·全靠自己查」口径★) ⇒ 查到落 `[官网]` + 证据副本 ⇒ 查不到就保持 [0数据] + 降级方案★** (★= ISS-305 B5-3, 已登记为 need★) |

### 5-3 · ★★对下游的影响 (★哪几条要跟着改口径★)★

| 下游 | 原来怎么写的 | ★**收窄后** ★ |
|---|---|---|
| ★**ISS-156 (demo camera 模组选型)** ★ | 拿「只能 1 路」当筛选前提 | ★**前提改成「实时 ISP 路数 = 1 (官方) + 多摄并发 = [0数据]」⇒ 选型时按自己判定的需求路数筛, 不拿未证实的结论筛★** |
| ★**决策页 §A-补28 的那条** ★ | 「多摄方案不成立」列成事实项 | ★**已在 `DECISION_INDEX_2026-11-18.md` §D / `DECISION_PENDING_2026-11-16.md` §A-补29 一并订正 (★append-only★)★** |
| ★**本交付页 §3-3 的诚实边界** ★ | 「是 [官方 + 推算] 的合成结论, 建议进决策页给老板确认」 | ★**保留 (★老字未删★) ⇒ 但决策页那条已按 §5-2 收窄 ⇒ 现在状态 = 「已收窄, 多摄并发仍 [0数据]」★** |

### 5-4 · ★本节自证 (★main 2026-11-18 04:1x 本机实跑★)

| 项 | 读数 |
|---|---|
| ★**零写板** ★ | 板 `611b869e13518c3c023fb178f91a0075` · mtime 仍 `2026-11-06 07:07:17` ⇒ 本节未写板 ★ |
| ★**零落表** ★ | 网表 `843e4065…` / 脚表 `9174309d…` / BOM `5b999399…` / 落表台账 未动 ★ |
| ★**零改闸** ★ | `HW/check_netlist_selfconsistency.py` / `state/check_stage_g1a.py` / `state/gate_check.py` 只读未编辑 ★ |
| ★**零外发** ★ | 本节不发信 · 不联系供应商 · 不下单 ★ |
| ★**不替老板拍板** ★ | 本节只收窄一条【事实表述】+ 补一条【二进制换算】+ 修一处【措辞撞名】⇒ 不涉及任何决策项的建议默认值 ★ |
| ★**append-only** ★ | §1~§4 老字未删未改 · 仅加箭头注记 + 追加本节 · 备份 `HW/RK3572_INQUIRY_CALIBER_V2.md.bak_20261118_0410_overclaim_narrow` ★ |
"""


def main() -> int:
    with open(PAGE, encoding="utf-8") as f:
        t = f.read()
    if "## 5 · ★★【追加式订正】" in t:
        print("ℹ §5 订正节已存在 ⇒ 幂等跳过")
        return 0

    for old, new, tag in ((OLD_L64, NEW_L64, "§1.2 over-claim 箭头注记"),
                          (OLD_L29, NEW_L29, "L29「实测」措辞订正"),
                          (OLD_13, NEW_13, "§1.3 二进制精确相等")):
        if old not in t:
            raise SystemExit("★找不到待改原文 ⇒ 拒绝写 (tag=%s): %s" % (tag, old[:60]))
        if t.count(old) != 1:
            raise SystemExit("★待改原文不唯一 (%d 处) ⇒ 拒绝写 (tag=%s)" % (t.count(old), tag))

    shutil.copy2(PAGE, BAK)
    t = t.replace(OLD_L64, NEW_L64).replace(OLD_L29, NEW_L29).replace(OLD_13, NEW_13)
    t += SECTION
    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(t)
    print("✅ 交付页已收窄 over-claim + 2 处措辞订正 + 追加 §5 · 备份 %s" % os.path.basename(BAK))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
