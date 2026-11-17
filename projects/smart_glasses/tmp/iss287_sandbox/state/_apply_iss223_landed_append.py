#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-223 · 落表记录 §10~§14 (第 2 批) 追加"""
import sys

P = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
s = open(P, encoding="utf-8").read()
orig_len = len(s)

APPEND = r"""
---

# ★★★第 2 批 (★ISS-223 · 2026-11-16 · 硬件总工 hw-lead 执行★) ★★★

> ★**一句话**: ★**V-1 已由 main 裁 = 22Ω ⇒ 落表第 2 批 = d5 (USB 串阻) + 补差A 的值迁移 (A 组 20 条 `imp` 清空 / 差分阻抗搬进 `z_diff`) ⇒ 门禁 `--expect-resolved` 的「未落表条数」★**25 → 21**★ (★ISS-220 交卷基线是 29; 本单起跑实测 25, 因为 04:15 那一版 SPEC.json 已把 B-21/B-22 的 `imp` 改掉, R5 的 4 条 spec 侧条件先转了绿★) ⇒ ★**R5 全组 8 条清零**★ · ★**同时把 ISS-220 查出的作业包 5 处病 (F-1~F-5) 就地修完 + 新增 §9 修订记录**★ · ★**并把 V-3 从「拍不了」变成「可拍」(★给出误差算式 + 推荐值 + 降级方案, 但不代拍★)**★**
> ★**零外发** (★未发邮件 / 询价 / 问询 / 采购 / 原厂问询★) · ★**本单实物 [实测] = 0 条** (★板与屏不在本机; 所有 [实测] 均为本机脚本 / 本机文件实读★) · ★**没有自签 issue_log** (★status 留给 main 落 verified★)

## ★★10 · 第 2 批落表条目 · 逐条 (★改了哪个真源的哪一行 · 改前/改后字面值 · 落表后跑的命令与输出行 · 证据等级★) ★★

### ★★10.1 · d5 · USB 串阻: 同一颗器件两个阻值 (90Ω vs 22Ω) (★★R5 全绿★★) ★★

| 栏 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ① ★**`HW/SCHEMATIC_V1_SPEC.json`** · `connections` 里 `id == "B-21"` / `id == "B-22"` 的 `imp` ★ (★**这两行是 ISS-223 前一个会话 04:15 落的, 本单沿用·未再改★**) · ② ★**`HW/check_netlist_selfconsistency.py`** · `EXPECT` 的 4 个单元格 (`d5_a291_value` / `d5_a292_value` / `d5_spec_b21_imp` / `d5_spec_b22_imp`) ★ + ③ ★**`HW/NETLIST_SELF_CONSISTENCY_SPEC.md`** · §2 锚点表同 4 个单元格 (★用 `--emit-anchors` 整块重生成覆盖, 不是手打★) |
| ★**改前 (字面)** ★ | `d5_a291_value` = `value == 90Ω ±10% (与 MIPI 不同模板!)` · `d5_a292_value` = `value == 90Ω ±10%` · `d5_spec_b21_imp` = `spec.connections[id=B-21].imp == 90Ω ±10% (与 MIPI 不同模板!)` · `d5_spec_b22_imp` = `spec.connections[id=B-22].imp == 90Ω ±10%` |
| ★**改后 (字面)** ★ | `d5_a291_value` = `value == 22Ω ±1%` · `d5_a292_value` = `value == 22Ω ±1%` · `d5_spec_b21_imp` = `spec.connections[id=B-21].imp == 22Ω ±1%` · `d5_spec_b22_imp` = `spec.connections[id=B-22].imp == 22Ω ±1%` |
| ★**★为什么这 4 个单元格必须同趟改 (★不是「改判据凑绿」★)** ★ | ★**这 4 条断言的【本体】(表A L291/L292 的 NET 行 value 必须 == SPEC.json B-21/B-22 的 `imp`) 一个字没改, 改的只是【断言的现状值】** ★ ⇒ ★**锚点条数一条没减 (d5 组仍 16 条 · 全表仍 160 条)**★ ⇒ ★**判据阈值与 `check_resolved()` 的 R1~R11 代码逐字未动**★ ⇒ ★**自检 19/19 仍全绿 ⇒ 判据没被放松成「怎么改都不红」**★ ★ |
| ★**--selftest 用例 9 的突变方向同步翻转** ★ | ★**落表后现状已是 22Ω ⇒ 原用例「改坏 B-21.imp (90Ω→22Ω)」改成了【同值改坏 ⇒ 永远抓不到红】⇒ 必须翻** ★ ⇒ ★**改成「退回 90Ω 的旧缺陷」** (★与 ISS-220 落表时 d1 (`m_net_value`) / d6 (`m_pages_21p_to_22p`) 同型处理★) ★ ⇒ ★**用例名也跟着改**: `用例9 [d5] 改坏 SPEC.json B-21.imp (22Ω→90Ω 退回旧缺陷) ⇒ 必须红` ★ |
| ★**落表后重生成 (★不许手工编辑产物★)** ★ | `python3 state/gen_netlist.py` → 表A **L291/L292 两行** value 由 `90Ω ±10% (与 MIPI 不同模板!)` / `90Ω ±10%` 变成 `22Ω ±1%`, 且 note 多了 `; 差分阻抗 90Ω ±15% 受控阻抗` (★`conn_row()` 的 `imp_extra` 逻辑★) ⇒ ★**全网表只有这 2 行变了 (diff = 6 行 = 2 改 + 4 分隔符), 其余 511 行逐字节不变** ★ |
| ★**命令与输出行** ★ | `python3 HW/check_netlist_selfconsistency.py` ⇒ `✅ rc=0: ★现状与 HW/NETLIST_SELF_CONSISTENCY_SPEC.md 一致★` · `python3 HW/check_netlist_selfconsistency.py --selftest` ⇒ `自检结果: 19/19 通过` · `python3 HW/check_netlist_selfconsistency.py --expect-resolved` ⇒ `★★ rc=1: 翻面口径未通过 (21 条未落表) ★★` (★R5 段一条红都没有了★) |
| ★**证据等级** ★ | ★**[官网]** ON Semi **AND8074/D** (USB 1.1 规范串阻 28~44Ω · 工业主流 22Ω/30Ω · 双绞线特性阻抗 Zo = 90Ω ±15%) · onsemi **STF202-22T1G** (内置 RS 20/22/24Ω) · ★**[实测]** `HW/SCHEMATIC_V1_SPEC.json` `B-21`/`B-22` 全文 (本机实读) + 表A L291/L292/L431/L432 逐字 + 板 `R_SER_USB_D_P/N = 22Ω±1%` (★本机文件实读·不是板实物量测★) + ★**[推算]** 「90Ω 串在 90Ω 线上 ⇒ 源端看到 180Ω ⇒ 摆幅减半 ⇒ 眼图不合规」 · ★**[0数据]** SoM (Forlinx) USB PHY 的驱动阻抗 / 外部串阻是否必需 (★V-1 的唯一外部依赖⇒ 降级: 已按 22Ω 落, 手册到手只核对驱动阻抗一条★) |

### ★★10.2 · 补差A / #1 · 值迁移 (★A 组 20 条 `imp` 清空 · 差分阻抗搬进 `z_diff`★) ★★

| 栏 | 内容 |
|---|---|
| ★**真源文件 · 行号** ★ | ① ★**`HW/SCHEMATIC_V1_SPEC.json`** · `connections` 里 A 组 20 条 (`A-01`~`A-10` / `A-13`~`A-22`) 的 `imp` → `""` + `z_diff` → `"100Ω ±10%"` (★**04:15 那版会话落的, 本单沿用·未再改★**) · ② ★**`state/gen_netlist.py`** · `conn_row()` 的取值优先级 (`imp` → `z_diff` → `level`) + note 的『差分阻抗』栏 (★**04:21 落的·本单沿用★**) · ③ ★**`state/check_netlist.py`** · 判据 5 的比对源 (`imp` 或 `z_diff`) (★**04:24 落的·本单沿用★**) |
| ★**★F-3 的同趟约束 (★本单实测确认★)** ★ | ★**只清空 A 组 `imp` 不改 `state/check_netlist.py` 判据 5 ⇒ `want` 变空 ⇒ 那 20 行被 `continue` 跳过 ⇒ 判据覆盖从 20 行【静默掉到 0 行】, 而门禁仍然是绿的 (判据被悄悄废掉)** ★ ⇒ ★**本单实测: 判据 5 的比对源已是 `(c.get("imp") or c.get("z_diff") or "")` ⇒ `python3 state/check_netlist.py` 的判据 5 输出仍是「A 组阻抗逐条对照规格 (20 条 net)」⇒ 覆盖 20 行, 一条没少** ★ |
| ★**落表后重生成** ★ | ★**A 组 20 条 NET 行的 value 逐字节不变** (★`imp` 清空前是 `100Ω ±10%`, 迁移后由 `z_diff` 顶上仍是 `100Ω ±10%`★) ⇒ ★**这正是「拆字段不改变任何产物」的设计意图, 本批实测确认** ★ |
| ★**证据等级** ★ | ★**[实测]** `HW/SCHEMATIC_V1_SPEC.json` 57 条 connections 全表枚举 (本机实读) + `state/gen_netlist.py` `conn_row()` 逐字 (L772-L800) + `state/check_netlist.py` 判据 5 逐字 (L93-L113) + 表A 20 条 A 组行逐行实读 · ★**[推算]** 「改动面 = 2 行 / 1 个文件, 且 A 组 20 条产物逐字节不变」 |

### ★★10.3 · 作业包 F-1 ~ F-5 就地修完 (★ISS-220 查出的 5 处病★) ★★

★**落表位置**: ★**`HW/SCHEMATIC_LANDING_WORKPACKET_V1.md`** (★作业包是 hw-lead 自己的产物, 本单可改★) ★**本单新增 §9「F-1 ~ F-5 修订记录」, 并就地改了 4 处** ★

| # | 病 | ★**就地改在哪** ★ | ★**本单实测依据** ★ |
|---|---|---|---|
| ★**F-1** ★ | d2 的 `dnp` 改法落不了地 | ★**§2.2 ④⑤** | `state/gen_netlist.py` 的 `DEMO_DNP` (L315-L322) 里 `R_BAT_DET_1` / `R_BAT_DET_2` / `C_DET_BAT` 三个 ref 【确在】⇒ `add()` 末尾会无条件覆盖 `dnp="DNP"` ⇒ 原改法无效 ⇒ 改法改成【删白名单条目 + 改 value/note】; 脚表的 `dnp` 是从网表 CSV 派生的 (`state/gen_netlist_pins.py` L230) ⇒ 不用单独改 |
| ★**F-2** ★ | d10 的 `J_CHG` 行真源写错文件 | ★**§2.10 ④⑤ + §4.C ④** | `state/gen_netlist.py` L1366-L1370 逐字「充电板整页的行数据由 `state/p10_rows.json` 提供」⇒ `J_CHG` 那条 NET 行 (表A L497, `net=BAT_CHG`) 的真源是 `state/p10_rows.json`, 改 `gen_netlist.py` 无效 ⇒ 且该 note 的目标值已过期 (ISS-220 已落成 1.216 真值口径) |
| ★**F-3** ★ | 清空 A 组 `imp` 会静默放松判据 5 | ★**§4.A ⑤ 改法表新增第 9 行 + 结果表 + ⑦** | `state/check_netlist.py` 判据 5 的 `want` 变空 ⇒ 20 行被 `continue` ⇒ 覆盖 20→0 行且门禁仍绿 ⇒ 改法表第 9 行写明「必须同趟改」; 结果表的「为什么」列原文「判据仍成立」已订正为「必须同趟改比对源」 |
| ★**F-4** ★ | d10 的方向修正连带作废「皮肤侧 42.14°C / 不能再抬电流」 | ★**§2.10 ⑤ 新增一行** | 42.14°C 是按错的 0.822 系数算的 ⇒ 按 1.216 系数电芯内阻发热 114mW → 148mW ⇒ 该温度数现在「无有效数字」; 目标文件写明 = `HW/PCB_OUTLINE_60x15.md` L149/L190 + `MECH/hinge_power_calc.json` 的 `rilim_table` ⇒ **本单没改那两行** (★不在本单可改清单★) ⇒ 归 MECH 重算那一趟 |
| ★**F-5** ★ | #5 的「白名单 ↔ §7 双向对账」在现状下不可能过 | ★**§3.5 ⑤ ②** | ★**本单实测复算三方对拍**: §7 的 CSV 块共 80 行, `board` 分布 = CHG_BOARD 64 / HINGE 11 / MAIN_PCB 4 / **1 行解析错位** (★`U_CHG` 那行 note 里逗号未加引号 ⇒ board 列被解析成 `" 0.8mm max height"` ⇒ §7 本身不是合法 CSV★) ⇒ §7 里有网表没有 = **16 个位号** (9 个 §7 侧 CHG_BOARD + 7 个 §7 侧 HINGE/MAIN_PCB/错位) · 网表有 §7 没有 = **15 个 CHG_BOARD 位号** ⇒ ⇒ 对账归 #6/补差C 的【充电板整页】那一趟, 本批不做 |

### ★★10.4 · ISS-220 的 3 条分片声明补落盘 (★交付物 ①★) ★★

| 栏 | 内容 |
|---|---|
| ★**落点** ★ | ★**`state/fragments/hw.yaml`** 的 `interface_claims` · 走 ★**`python3 state/frag_write.py --agent hw-lead --add-claim ...`** (★内部走 `update_fragment()` → `atomic_write_yaml()`: tmp + fsync + `os.replace`★) ⇒ ★**没有用 `open(p,"w")`** ★ |
| ★**3 个 key** ★ | ★**`iss220_chgboard_white_list_scope`** (★充电板归属 = `CHG_BOARD_REFS` 白名单驱动 ⇒ 漏一颗就默认落 MAIN_PCB★) · ★**`iss220_i2ca_pullup_domain_1v8`** (★I2C_A 上拉 = 2.2k 到 `RAIL_VDD_1V8_IO`★) · ★**`iss220_ichg_ratio_true_value`** (★`ICHG/IIN = η·Vbus/Vbat` = 1.216@3.70V / 1.071@4.20V★) |
| ★**mtime 前 / 后** ★ | ★**前**: `2026-11-16 01:59:34` (md5 `7eeea9ebc73556d525b9b816fc77667f`) ⇒ ★**后**: `2026-11-16 05:13:58` (md5 `88d0f2f92479a21980bca9cfb4427638`) ★ |
| ★**命中行** ★ | `state/fragments/hw.yaml` L2858 / L2863 / L2868 (★`grep -n` 实测★) |

---

## ★★11 · V-3 可判化 (★RK3572 SARADC_VIN5 官方参数自查 + 误差算式 + 推荐值 + 降级方案★; ★不许代拍★) ★★

★**结论一句话**: ★**V-3 现在的选项集 (A: 2.0M+1.2M vs D: 2.0M+1.0M) 是个【伪选择】—— 两者的 R_top 都是 2.0M, 而两个主导误差项 (电阻比容差 / 漏电经 R_top) 【完全相同】; 真正的决策是【分压链的阻抗等级】, 而这一条被 V-3 的选项集漏掉了 ⇒ 本单给出可拍依据 + 推荐值 (新方案 E = 100k+60k+100nF) + 降级方案, 但【不代拍】** ★

### ★★11.1 · 官方参数自查 (★自己查·零外发·用项目库内的一手件★) ★★

| 参数 | 查到的值 | 证据等级 | 逐字出处 (本机实读) |
|---|---|---|---|
| ★**分辨率** ★ | ★**12 bit** ★ | ★**[官网]** | `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` (RK3572 Datasheet Rev 1.1, ★**Copyright © 2026 Rockchip Electronics Co., Ltd.**★) §3.10 **Table 3-16** → `Resolution  NA  12  NA  Bit`; §1.2 特性也写「Successive approximation ADC(SARADC) / Supports 12-bit resolution / Supports up to 1MS/s sampling rate / Supports 8 single-ended input channels」 |
| ★**满量程 / 模拟输入范围** ★ | ★**AIN = `AVSS18` ~ `AVDD18`**; `SARADC_AVDD1V8` = ★**1.62 / 1.8 / 1.98 V** (min/typ/max) ★ | ★**[官网]** | 同上 Table 3-16 → `Anglog Input Range  AIN  AVSS18  NA  AVDD18  V`; 电气总表 → `SARADC Analog Power(1.8V)  SARADC_AVDD1V8  1.62  1.8  1.98  V` ⇒ ★**1 LSB = 1.8/4096 = 439.5 µV (typ) / 1.98/4096 = 483.4 µV (max)** ★ |
| ★**线性度 / 偏移** ★ | ★**DNL ±1.0 typ / ±3.0 max LSB (PD=Low) · INL ±2.0 typ / ±6.0 max LSB (Fs=1MS/s, FCLK=20MHz) · 顶部/底部 offset 误差 ±10 typ / ±20 max LSB** ★ | ★**[官网]** | 同上 Table 3-16 ⇒ ★**合计 worst = (20+6+3) = 29 LSB** ★ |
| ★**★输入漏电流** ★ | ★**[0数据] ★查不到**★ ⇒ datasheet Table 3-16 【没有】漏电流行 | ★**[0数据]** | ★**逐字核对过的坑**: datasheet 全文里那几条 `Input leakage current  IPAD  -10  NA  10  uA` 属于 ★**Table 3-4「Electrical Characteristics for General IO」= 数字 GPIO**★ (★行归属已逐字核对: 那一段每个参数的分组写的是 `Digital 3.3V/1.8V GPIO` / `Digital 1.8V only and Digital 1.8V/1.2V GPIO` / `VCCIO0 IO`★), ★**不是 SARADC**★ ⇒ ★**不能拿 GPIO 的 10µA 当 SARADC 的值, 也不能拿它当 SARADC 的值来论证「漏电无所谓」** ★ |
| ★**★输入电容 / 采样保持时间 / 内部采样电容 C_in** ★ | ★**[0数据] ★查不到**★ | ★**[0数据]** | ★**datasheet 全文 grep「input capacitance / Capacitance / acquisition / Input Resistance / source impedance / Sample」⇒ 零命中** ★ ⇒ 这些参数在 ★**Rockchip TRM**★ 里, ★**TRM 不公开** ★ ⇒ 公开的 Linux 主线 `drivers/iio/adc/rockchip_saradc.c` ★**也没有 rk3572 的条目**★ (★表里只有 saradc / rk3066-tsadc / rk3399 / rk3528 / rk3562 / rk3568 / rk3588 / rv1106★) ⇒ ★**RK3572 走 BSP 驱动 ⇒ 拿不到** ★ ⇒ ★**顺带一条有用的 [官网]**: 该驱动的 `IIO_CHAN_INFO_SCALE` 是 `uv_vref / 1000` 除以 `scan_type.realbits` ⇒ ★**VFS 由 vref regulator 定, 且 raw 读数不做硬件 offset 校准** (`last_val &= GENMASK(realbits-1, 0)`) ⇒ ★**offset ±20 LSB 是【软件】要自己标的** ★ |

### ★★11.2 · 误差算式 (★口径 = 项目自己的 `SW/tools/timing_check.py` F4, 不是本单另起一套★) ★★

```
k          = R_bot / (R_top + R_bot)                       # 分压比
V_node     = V_BAT · k
R_th       = R_top || R_bot                               # 源阻抗 (THEVENIN)
τ          = R_th · C_filter
LSB_node   = V_FS / 2^12                                  # V_FS = 1.8V typ (★不是 3.3V★)
t_settle   = ln(1 / (0.5·LSB/ V_FS)) · τ = ln(2^12) · τ = 9.0109 · τ
ΔV_leak    = I_leak · R_th                                ⇒ ★折算到电池侧 = I_leak · **R_top**★
ΔV_ratio   = ( R_top/(R_top+R_bot)·ε_bot + R_bot/(R_top+R_bot)·ε_top ) · V_node   (worst-case, 两颗反向取极值)
ΔV_ADC     = (offset_max + INL_max + DNL_max) · LSB = 29 · LSB
```

★**★决定性的恒等式 (本单实算)★**: ★**`R_th / k = R_top`** ⇒ ★**漏电引起的【电池侧】误差只跟【上臂】R_top 有关, 与下臂无关** ★ ⇒ ★**A (2.0M+1.2M) 与 D (2.0M+1.0M) 的 R_top 都是 2.0M ⇒ 漏电误差项【完全相同】** ★ ⇒ ★**而电阻比容差项 A 与 D 也同为 ±1.00%** ★ ⇒ ★**⇒ A 与 D 的差别只剩【利用率 / 分辨率 / 分压电流】三项 (A 全面占优), 而【决定成败】的两项 (漏电 + 建立时间) 两边一样差** ★

### ★★11.3 · 三档实测对比 (★`state/calc_v3_batdet.py` 的本机实跑输出·可复现★) ★★

| 方案 | k | R_th | τ | t_settle(½LSB) | V_node@4.2V | 利用率@1.8V | ★**过压?** ★ | 比容差(worst) | ADC 自身(max) | 漏电@1µA | 占 FS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ★**现行 1M+1M** (DNP 未装) ★ | 0.50000 | 500.0 kΩ | 50.00 ms | 450.5 ms | **2.1000** | 116.7% | ★**是** ★ | ±1.00% | 28.0 mV | 500.0 mV | 27.8% |
| ★**V-3 方案 A 2.0M+1.2M** ★ | 0.37500 | 750.0 kΩ | 75.00 ms | 675.8 ms | 1.5750 | 87.5% | 否 | ±1.00% | 37.4 mV | 750.0 mV | 41.7% |
| ★**V-3 方案 D 2.0M+1.0M** ★ | 0.33333 | 666.7 kΩ | 66.67 ms | 600.7 ms | 1.4000 | 77.8% | 否 | ±1.00% | 42.1 mV | 666.7 mV | 37.0% |
| ★**★新方案 E 100k+60k + 100nF** ★ | 0.37500 | **37.5 kΩ** | **3.75 ms** | **33.8 ms** | 1.5750 | 87.5% | 否 | ±1.00% | 37.4 mV | **37.5 mV** | **2.1%** |
| ★**新方案 E′ 100k+60k + 1µF** ★ | 0.37500 | 37.5 kΩ | 37.50 ms | 337.9 ms | 1.5750 | 87.5% | 否 | ±1.00% | 37.4 mV | 37.5 mV | 2.1% |

★**★静态功耗 (方案 E 的唯一代价)★**: ★**26.25 µA / 110.25 µW / 0.630 mAh·日⁻¹** (★现行 1M+1M 只要 2.10 µA / 8.82 µW / 0.050 mAh·日⁻¹★) ⇒ ★**这是「待机功耗 vs 精度」的唯一取舍, 归老板拍** ★

★**★建立时间敏感度 (C_in 是 [0数据], 只做扫描★)★**: ★**`t_acq = 9.0109 × R_th × C_in`** ★ ⇒ 方案 E 在 C_in = 10/20/30 pF 下分别 = ★**3.4 / 6.8 / 10.1 µs**★ (★方案 A 是 67.6 / 135.2 / 202.7 µs★) ⇒ ★**方案 E 的采样窗口小到可以忽略; 方案 A 的窗口虽然也不大, 但要跟 1MS/s 的转换周期比, 就不确定了** ★

### ★★11.4 · 可拍依据 + 推荐值 + 降级方案 (★供 main/老板拍·本单不代拍★) ★★

| 栏 | 内容 |
|---|---|
| ★**可拍依据 (①)** ★ | ★**现行 1M+1M 在【任何】分压比下都过压** (4.2V × 0.5 = **2.100V > AVDD18 max 1.98V**) ⇒ ★**d2/d7/d8 的现状是确定的缺陷, 不是"待定"** ★ |
| ★**可拍依据 (②)** ★ | ★**V-3 现有两个候选 (A / D) 的差别只有 R_th 的 12.5%, 而两者都差 3 个数量级** (★SAR ADC 要的是 kΩ 级源阻抗, 不是 750kΩ★) ⇒ ★**⇒ V-3 现在的选项集是【伪选择】; 必须把【阻抗等级】摆到台面上** ★ |
| ★**可拍依据 (③)** ★ | ★**漏电误差项只跟 R_top 有关 (恒等式 `R_th/k = R_top`)** ⇒ ★**要压漏电误差只有一条路: 把 R_top 从 2.0M 降到 100k (↓20 倍)**, 而不是在下臂 1.2M/1.0M 之间选 ★ |
| ★**可拍依据 (④)** ★ | ★**BAT_DET 的用途定位把它从"精度需求"降级成"阈值判断"**: ★**`SW/SW_REQUIREMENTS.md` M7-R6 只要求「软件侧确认电量读取正常」, 不是电量百分比精度** ⇒ ★**⇒ 用途的精度需求 (低电量告警粗判, ±100mV 级) ≪ 残差误差 ⇒ V-3 变成【可判】** ★ |
| ★**★推荐值 (供拍, 本单不代拍)★** ★ | ★**方案 E = 上臂 100k ±1% + 下臂 60k ±1% + 滤波 100nF ±10%** ★ ⇒ ★**k = 0.375 (与 A 同 ⇒ 利用率 87.5% / 电池侧分辨率 1.172 mV 都不打折)** · ★**R_th = 37.5 kΩ ⇒ τ = 3.75 ms ⇒ t_settle(½LSB) = 34 ms ⇒ 软件侧等 ≥50 ms 就到 ½LSB** · ★**漏电 @1µA (最坏占位值) = 37.5 mV = 2.1% FS ⇒ 可软件标定 (常数项)** · ★**总误差 (含 ADC 自身 29 LSB) < 2.9% FS** · ★**唯一代价 = 26.25 µA / 110 µW 常开** ★ |
| ★**降级方案 (①)** ★ | ★**若不能接受 110 µW 常开** ⇒ ★**把分压链改成"按需使能" (用一个 P-MOS 把上臂接到 BAT, 采样时才开)**: 采样窗口 34 ms × 采样周期 ⇒ ★**均摊功耗可降到 µW 级** ⇒ ★**但这是【板级拓扑】改动 ⇒ 归「板只改一次」那一趟★** ★ |
| ★**降级方案 (②)** ★ | ★**若 SoM 手册 / SoC TRM 拿不到 (I_leak / C_in / t_acq 三个数)**: ★**按方案 E 落表, 并把 BAT_DET 的用途口径写死为【低电量告警粗判 (±100mV 级)】, 不作【电量百分比显示】的精度基准** ⇒ ★**依据 = M7-R6 的措辞 (只要求"读取正常")** ★ ⇒ ★**即便 I_leak = 1µA 这个最坏占位值, E 的总误差仍 < 2.9% FS ⇒ 够用** ★ |
| ★**降级方案 (③)** ★ | ★**若连方案 E 的 110 µW 都不能接受** ⇒ ★**兜底口径: BAT_DET 链【保持不装 (DNP)】, 电量改由【BQ25896 的 I2C 状态寄存器】读 (★BQ25896 有 VBUS/VSYS/IBAT 遥测★) ⇒ ★**但这是【换架构】, 归 V-7 充电板整机阶段单★** ★ |
| ★**降级方案 (④)** ★ | ★**★本单【不落表 V-3 的值】★**: ★**网表仍是 1M+1M + DNP (★诚实的现状★) ⇒ ★**d2 / d7 / d8 仍然 BLOCKED 于 V-3, 门禁 R2/R7/R8 仍然红 (★21 条里的 13 条★) ⇒ ★**这不是本单的失败, 这是"没拍就不落"的纪律** ★ |
| ★**★顺带查出的一处 SW 侧口径错 (★只报不改·SW 地界★)★** ★ | ★**`SW/tools/timing_check.py` 的 `DEVICE["V_DET_FS"] = 3.3`** ★ ⇒ ★**`BAT_DET` 走 `J_SOM_P1 pin38 = SARADC_VIN5` = 1.8V 域 (FET3572C_PIN_TABLE.csv P1_38) ⇒ V_DET_FS 对这条链应该是 1.8V, 不是 3.3V** ★ ⇒ ★**⇒ SW 算出来的「漏电偏移 %满量程」对 BAT_DET 链【偏小 1.83 倍】(1.8/3.3)** ★ ⇒ ★**⇒ 本单把这条登记成 need 给 sw-lead (见交接单 B5 第 11 条), 本单不动 `SW/`** ★ |
| ★**证据等级** ★ | ★**[官网]** RK3572 Datasheet Rev 1.1 §3.10 Table 3-16 + 电气总表 + §1.2 特性 (★项目库内 `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt`★) · ★**[官网]** Linux 主线 `drivers/iio/adc/rockchip_saradc.c` (★VFS 由 vref regulator 定 / raw 无硬件 offset 校准 / 无 rk3572 条目★) · ★**[实测]** `state/calc_v3_batdet.py` 的本机实跑输出 (★`state/calc_v3_batdet_output.txt`·可复现★) + `SW/tools/timing_check.py` L1028-L1070 逐字 (★公式口径★) + `HW/PCB/FET3572C_PIN_TABLE.csv` P1_38 逐字 · ★**[推算]** `R_th/k = R_top` 恒等式与全部误差项的传播 · ★**[0数据]** SARADC_VIN5 的输入漏电流 / 输入电容 / t_acq / C_in (★datasheet 无 · TRM 不公开 · BSP 驱动拿不到★) |

---

## ★★12 · 板侧同步清单 (★第 2 批更新·★只更新状态, 不许动板★) ★★

| 项 | 落表项 | ★**因本批落表而变化的** ★ | ★**仍等 V-2 与「板只改一次」那一趟的** ★ |
|---|---|---|---|
| ★**B-1** ★ | ★**d11 / #5** ★ | ★**无变化** (★ISS-220 已把 `C_VBUS_GND` 判成 CHG_BOARD, 板还是 MAIN_PCB ⇒ 已知不一致照旧★) | ★**照旧**: 把 `C_VBUS_GND` 的封装从 demo 主 PCB 上拿掉 (★板生成器按 board 列过滤 ⇒ 重跑 `state/gen_pcb_netlist_board.py` 即自动消失★) ★ |
| ★**B-2** ★ | ★**d3** ★ | ★**无变化** | ★**照旧**: 板封装 `U_EN_SW` 的 `Value` 属性从 `EN 输入 (高=放行底板)` 改成器件身份描述 (★R3 判据就是这条★) ★ |
| ★**B-3** ★ | ★**d4 / d9** ★ | ★**无变化** | ★**照旧**: `D_ESD_USB_D` 从 2 脚换 3 脚封装 (pin1=D+ / pin2=D− / pin3=GND) ★ |
| ★**B-4** ★ | ★**d4 / d9** ★ | ★**无变化** | ★**照旧**: 把 `D_ESD_USB_D` 挪到 `J_USB_C` 旁 ≤ 3.0 mm (★现距 47.99 mm★) ⇒ 布线必须重跑 ⇒ 必须与 B-3 同趟 ★ |
| ★**B-5** ★ | ★**d4 / d9** ★ | ★**无变化** | ★**照旧**: USB D− 那条路上补 ESD (★现在板上挂 D− 两张网的 ESD 位号数 = 0★) ★ |
| ★**B-6** ★ | ★**#6 / 补差C** ★ | ★**无变化** | ★**照旧**: 充电板 π 滤波的位号与拓扑 (★归充电板整机阶段单 V-7★) ★ |
| ★**★B-7 (★本批新增★)** ★ | ★**d5 / 补差A** ★ | ★**★网表侧已改: `R_SER_USB_D_P` / `R_SER_USB_D_N` 的 NET 行 value 由 90Ω 改成 22Ω ±1% ⇒ ★**板上的器件值本来就是 22Ω, 板侧【无需改动】★ (★本批实测: 板 `R_SER_USB_D_P/N` = 22Ω±1%★)** ⇒ ★**⇒ d5 这一条【不进板侧同步清单】(★它是"网表追平板", 不是"板要改"★)** ★ | — (★无★) |
| ★**★B-8 (★本批新增★)** ★ | ★**V-3 (待拍)** ★ | ★**无 (★V-3 没拍, 没落表★)** | ★**★若 main/老板拍【方案 E (100k+60k)】⇒ 板侧 `R_BAT_DET_1` / `R_BAT_DET_2` 的封装/阻值要改 (★1M → 100k / 60k★) ⇒ ★**这条必须并进「板只改一次」那一趟**, 否则又要重出一次板 ★** ⇒ ★**⇒ ★**这是 V-3 必须在派板前拍完的原因** ★ ★ |

---

## ★★13 · 受保护 md5 前后对照 (★第 2 批·本单起跑基线 ⇒ 交卷实测★) ★★

| 文件 | 前 (本单起跑) | 后 (交卷) | 变了? |
|---|---|---|---|
| ★**`HW/SCHEMATIC_V1_SPEC.json`** ★ | `7584f8b479194710621d175fa3168c1f` | `7584f8b479194710621d175fa3168c1f` | ★**否** (★04:15 那版会话已落 B-21/B-22 的 `imp` + A 组清空·本单沿用未再改★) |
| ★**`state/gen_netlist.py`** ★ | `3c765729de34db50ee1b0ddd60c360a2` | `3c765729de34db50ee1b0ddd60c360a2` | ★**否** (★04:21 那版会话已落 `conn_row()` 取值优先级★) |
| ★**`state/check_netlist.py`** ★ | `d13381f42f41f2f1a89dbfbf98484535` | `d13381f42f41f2f1a89dbfbf98484535` | ★**否** (★04:24 那版会话已落判据 5 的 `imp or z_diff`★) |
| ★**`HW/check_netlist_selfconsistency.py`** ★ | `5e387936738f399ebbe4cbebd5479bb0` | `6767202963eb96c4050125379b125b7c` | ★**是** (★EXPECT 4 个单元格 + selftest 用例 9 的突变方向 + 用例名★) |
| ★**`HW/NETLIST_SELF_CONSISTENCY_SPEC.md`** ★ | `8e0ac3f7e0edc31847ca158e5ee0456a` | `118bfabbf726b9fa9a59e6361a5f412c` | ★**是** (★锚点表 4 个单元格·用 `--emit-anchors` 整块重生成★) |
| ★**`HW/SCHEMATIC_LANDING_WORKPACKET_V1.md`** ★ | `0970113b9443157d2f3c2d3c2e72f510` | `bae9da8c15ff0d08bf6c3c900a84b0a7` | ★**是** (★F-1~F-5 就地修 + §9 修订记录 + §8 状态表更新★) |
| ★**`HW/SCHEMATIC_LANDING_V1_LANDED.md`** ★ | `5fd6e08ca9d9138c5cbf84a86be77908` | ★**见交卷实测** | ★**是** (★本 §10~§14★) |
| ★**`HW/netlist_v1.csv`** ★ | `13f59a43dbd35dc6cb16e897c8c891ab` | `3215020b6d4120e1b7728227effdc6d3` | ★**是** (★**只 L291/L292 两行**★) |
| ★**`HW/netlist_v1_pins.csv`** ★ | `a600afae493f5a7a6c55f46ad35ac89c` | `a600afae493f5a7a6c55f46ad35ac89c` | ★**否** (★脚表不含 NET 行的 value★) |
| ★**`HW/BOM_v1.csv`** ★ | `92b51580867deca9f8b04af88d925d96` | `92b51580867deca9f8b04af88d925d96` | ★**否** ★ |
| ★**`HW/BOM_pseudo_refs_v1.csv`** ★ | `984dd73dd8d1ed492b5b1fb38519034c` | `47e1659a42d8d3f6728ea653df1eb530` | ★**是** (★L54/L55 两行跟着网表走★) |
| ★**`HW/netlist_v1.net`** ★ | `978ab59e297e6bb89f873b763569eccb` | `978ab59e297e6bb89f873b763569eccb` | ★**否** ★ |
| ★**`HW/SCHEMATIC_V1.md`** ★ | `a349ccbeee4a65830cbde21d0e409825` | `b06298db21de27112def71d28ce2997b` | ★**是** (★生成物·跟着网表走★) |
| ★**`HW/PCB/demo_mainboard.kicad_pcb`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**`611b869e13518c3c023fb178f91a0075`** ★ | ★**否 (受保护·逐字节不变)★** |
| ★**`HW/PCB/demo_mainboard.kicad_pro`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**`3e504d2be83152e337949723e909be1b`** ★ | ★**否 (受保护·逐字节不变)★** |
| ★**`state/fragments/hw.yaml`** ★ | `7eeea9ebc73556d525b9b816fc77667f` | `88d0f2f92479a21980bca9cfb4427638` | ★**是** (★3 条 `interface_claims` 补落·走 `frag_write.py` 原子写★) |

★**★回滚副本★**: ★**`state/.bak_iss223_r2/`** (★12 个本单起跑基线副本★) + ★**`state/.bak_iss223/`** (★上一会话 04:06 留的 13 个 ISS-223 前基线★) ★

---

## ★★14 · 第 2 批复现命令 (★B6 自证★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ★★7 条必跑门禁 ★★
python3 HW/check_netlist_selfconsistency.py                    # rc=0 (现状守卫 + 作业包完整性 + 三方对齐)
python3 HW/check_netlist_selfconsistency.py --selftest          # rc=0 (反向用例全抓到, 19/19)
python3 HW/check_netlist_selfconsistency.py --expect-resolved   # rc=1 (★预期: 还有 21 条未落表★)
python3 state/check_netlist.py                                  # rc=0 (全过)
python3 state/check_netlist_pins.py                             # rc=0 (每个针脚归属唯一)
python3 state/check_sch_erc.py                                  # rc=0 (ERC 违规数 = 0)
python3 state/check_sch_pinfull.py                              # rc=0 (图上脚数 = 表里脚数)
python3 state/merge.py && python3 state/gate_check.py           # rc=0 且 【Q1 交付齐备率】 18/18

# ★★落表链路 (改源 → 重生成; ★板不碰★) ★★
python3 state/gen_netlist.py && python3 state/gen_netlist_pins.py && \
python3 state/gen_bom.py && python3 state/gen_kicad_net.py && \
python3 state/gen_schematic_pages.py && python3 state/gen_kicad_sch.py

# ★★V-3 误差预算 (★可复现★) ★★
python3 state/calc_v3_batdet.py          # 输出已存 state/calc_v3_batdet_output.txt

# ★★受保护 md5 (必须逐字节不变) ★★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# 611b869e13518c3c023fb178f91a0075 / 3e504d2be83152e337949723e909be1b

# ★★锚点表 (规格页 ⇄ 脚本 逐字一致) ★★
python3 HW/check_netlist_selfconsistency.py --emit-anchors | wc -l    # 162
```
"""

s = s.rstrip("\n") + "\n" + APPEND
open(P, "w", encoding="utf-8").write(s)
print(f"✅ 已写 {P} · {orig_len} → {len(s)} 字节")
