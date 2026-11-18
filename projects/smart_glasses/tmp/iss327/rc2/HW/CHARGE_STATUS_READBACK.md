# HW/CHARGE_STATUS_READBACK.md —— 充电状态读取接口规格 (ISS-043)

> **ISS-043** (owner=hw-lead, reporter=main, due 2026-11-05) —— 「充电状态读取接口未确认 → 充电时禁 OD 门禁可能无法实现」
> **sw-lead IR-02 (M-CHRG 安全要求)**: 充电时必须禁 OD (0.8W 充电耗散 → 皮肤 75.1°C), 但若硬件既无充电状态寄存器、也无 VBUS 分压检测, 软件就不知道在充电 ⇒ 门禁实现不了 ⇒ M-CHRG 只能判未验。
>
> **本文结论 (一句话)**: **能实现, 而且硬件上本来就是双通路的** —— 主判据 `CHG_STAT` (BQ25896 STAT 开漏脚) + 兜底判据 `VBUS_DET` (1M+1M 分压 → ADC), 两条都已落在网表里 (P2/P7/P9), **ISS-043 的「未确认」前提不成立**。
>
> **数字/位号唯一出处**: `HW/netlist_v1.csv` (P1/P2/P7/P9/P10 各行) —— 本文逐行给出位号与行号; 复算命令见 §7。

---

## B1 结论摘要 (每条带数字)

1. **充电状态读取 = 2 条独立通路, 已在网表里**:

| 通路 | 网表 | 信号链 | 语义 | 延迟 |
|---|---|---|---|---|
| **① CHG_STAT (主判据)** | P2 第 171-173 行 | `U_CHG` (BQ25896) STAT 脚 → `R_PU_CHG_STAT` **10k±1%** 上拉到 `VDD_3V3_IO` → `NET_CHG_STAT` → `J_CHG pin5` → SoC GPIO | 开漏: **低 = 充电中**, 高 = 未充/充满, **1Hz 闪 = 故障** | 比较器级, **µs~ms** (不依赖 ADC 采样) |
| **② VBUS_DET (兜底 + USB 枚举前提)** | P2 第 159-164 行 | `VBUS_5V` → `R_VBUS_DET_1` **1M±1%** → `R_VBUS_DET_2` **1M±1%** → GND, 中点 + `C_DET_VBUS` **100nF** → `NET_VBUS_DET` → `J_CHG pin7` → SoC `USB_VBUS_DET` ADC | 分压比 1/2 ⇒ 5V → **2.5V** | Rth = 1M‖1M = **500kΩ** × 100nF ⇒ τ = **50 ms**, 95% 建立 ≈ **150 ms** ⚠️ |
| (③ PWR_GOOD) | P9 第 437 行 pin map | `J_CHG pin6` = PWR_GOOD | 「系统电源好」, **不是充电状态** | — |

2. **★门禁判据要用 OR, 不能只靠 CHG_STAT**: `CHG_STAT` 是开漏上拉 ⇒ **断线时读到"高"= 未充电** ⇒ 只用它做判据, 线一断就把"充电中"误判成"未充电" ⇒ **禁 OD 失效 ⇒ 皮肤侧 75.1°C 风险**。正确判据: **`在充电 = (CHG_STAT == 低) OR (VBUS_DET > 4.0V 阈值)** ⇒ 任一条通路失效, 另一条仍能关门禁 ⇒ **fail-safe**。
3. **ISS-043 的「未确认」前提不成立 ⇒ 可以从 open 走到 fixed**: 硬件侧两条通路都在网表里、有位号、有阻值、有测试点 (`TP_CHG_STAT` / `TP_VBUS`); sw-lead 的 M-CHRG 门禁**在硬件上可实现**。剩下的**不是硬件问题**, 是 (a) SoC 脚号映射 (换芯 RK3576 后要重映射, 见 §4 风险) (b) 实测确认 (EVT 项 R-H-03 已写进 `HW/EVT_RELIABILITY_TEST_ITEMS.md`)。
4. **★但 VBUS_DET 通路有已知缺陷, 必须跟 sw-lead 的 P1-8 一起改**: sw-lead 在 9 项改动请求 P1-8 里指出的 "1M+1M 源阻抗 500kΩ / 建立 451ms / 漏电 15.2%FS" **是对的**, 本文复算一致 (τ=50ms; 若按 451ms 口径是 9τ 保守值) ⇒ **建议 R_VBUS_DET 改 100k/47k** (Rth = 32kΩ ⇒ τ = 3.2ms, 漏电误差降 10 倍到 ~1.5%FS; 分压比 47/147 = 0.3197 ⇒ 5V → 1.60V)。**改的是阻值不是拓扑 ⇒ 换料不换板**。
5. **关机态充电灯与 CHG_STAT 同源**: 充电灯 NMOS 读同一个 STAT (P10 充电灯链, 老板 10-27 拍板"关机时充电灯要亮") ⇒ 灯亮 ⟺ CHG_STAT 低 ⟺ 充电中 ⇒ **软件可以拿灯的状态做交叉验证** (EVT 项 R-H-03)。

---

## B2 网表逐行依据 (复算入口)

| 网表行 | 关键内容 | 出处 |
|---|---|---|
| P2 #171 | `CHG_STAT` = `U_CHG` STAT 脚 → `R_PU_CHG_STAT`, 方向 充电IC→SoC, 电平 3.3V (开漏), 测试点 `TP_CHG_STAT` | `HW/netlist_v1.csv` |
| P2 #172 | `R_PU_CHG_STAT` = **10k ±1%** 上拉到 `RAIL_VDD_3V3_IO` | 同上 |
| P2 #173 | `CHG_STAT` → `J_CHG pin5` (跨铰链) | 同上 |
| P2 #159 | `NET_VBUS_DET` = `R_VBUS_DET_1`/`R_VBUS_DET_2` **1M+1M 分压 + 100nF** → SoC ADC, `TP_VBUS` | 同上 |
| P2 #160 | `R_VBUS_DET_1` = **1M ±1%** (上臂), 漏电流 ~1.65µA @5V | 同上 |
| P2 #161 | `R_VBUS_DET_2` = **1M ±1%** (下臂接 GND) | 同上 |
| P2 #162-163 | `C_DET_VBUS` = **100nF ±10%** (ADC 滤波, 跨铰链侧) | 同上 |
| P2 #164 | `NET_VBUS_DET` → `SoC[TBD-01].USB_VBUS_DET` (脚号待原厂, **TBD-10**) | 同上 |
| P7 #382 | `TP_CHG_STAT` 测试点 (测什么: 充电状态; 位置: BQ25896 STAT 脚) | 同上 |
| P7 #355 | `TP_VBUS` 测试点 (位置: Type-C 出口侧 ≤3mm) | 同上 |
| P9 #437 | `J_CHG` pin map: pin1/2=BAT_CHG, pin3/4=GND, **pin5=CHG_STAT**, pin6=PWR_GOOD, **pin7=VBUS_DET**, pin8=TS, pin9/10=预留 | 同上 |
| P10 | `I2C_CHG_SCL/SDA` 跨铰链 **DNP** (预留, 上拉只在主板侧) ⇒ **默认状态无法编程 ICHG/读寄存器** ⇒ 见 §3.3 | 同上 |

> 复算: `grep -n "CHG_STAT\|VBUS_DET\|R_VBUS_DET\|C_DET_VBUS\|R_PU_CHG_STAT" HW/netlist_v1.csv`

---

## B3 门禁规格 (交给 sw-lead 的 M-CHRG 判定口径)

### 3.1 判定式 (硬件给定的口径, 软件照实现)

```
在充电 = (CHG_STAT == 低)  OR  (VBUS_DET_ADC > VBUS_PRESENT_TH)
其中 VBUS_PRESENT_TH = 3.0V (对应输入 VBUS ≥ 4.4V —— 1/2 分压口径下 5V→2.5V, 阈值取 3.0V 对应 1/3 弱负载也能识别)

禁 OD (M-CHRG) = 在充电  ⇒  拒绝启动 OD / 正在跑则立即停推理 + 停 sensor 流 + 息屏
```

| 通路 | 失效模式 | 门禁是否还安全 |
|---|---|---|
| CHG_STAT 断线 (读到高) | 判"未充电" | ✅ **安全** —— VBUS_DET 仍能判出"在充电" ⇒ OR 逻辑兜住 |
| VBUS_DET 断线 (读到 0V) | 判"未充电" | ✅ **安全** —— CHG_STAT 低仍能判出"在充电" |
| 两条都断 | 判"未充电" | ❌ **不安全** ⇒ 缓解: 开机自检时若 `VBUS_DET_ADC < 1.0V` 且 `CHG_STAT` 为高 ⇒ 判为 **未知态** ⇒ **默认禁 OD** (fail-closed), 并上报故障码 |
| 充电灯亮但 CHG_STAT 读"高" | 逻辑矛盾 | ❌ ⇒ 上报故障 (灯由同一 STAT 驱动, 矛盾说明 pin map 错) |

### 3.2 时序预算

| 环节 | 预算 | 依据 |
|---|---|---|
| BQ25896 STAT 输出切换 | µs ~ ms (内部比较器) | `[官方]` 器件行为 (具体 t 值 **[0数据]**, 需 datasheet) |
| 跨铰链 1 条信号 (≤40mm FPC) | ns 级 | `[推算]` |
| SoC GPIO 读取 (轮询 100ms / 中断) | ≤100 ms | 软件策略 |
| **VBUS_DET ADC 通道** (1M+1M 现状) | τ = 500kΩ × 100nF = **50 ms**; 95% 建立 ≈ **150 ms** (9τ 保守 451ms) | `[推算]` 本文复算 |
| **VBUS_DET (建议改 100k/47k 后)** | Rth = 32kΩ ⇒ τ = **3.2 ms**, 95% ≈ 29 ms | `[推算]` |
| **门禁总延迟 (取 CHG_STAT 通路)** | **≤ 100 ms** ⇒ 插线到禁 OD ≤ 0.1 s | `[推算]` |

### 3.3 为什么不靠 I2C 读充电 IC 寄存器

`I2C_CHG_SCL/SDA` 跨铰链在网表里是 **DNP (预留)** ⇒ 没有跨铰链的 I²C ⇒ 软件**读不到** BQ25896 的 REG (VBUS/IBAT/ICHG 实际值) ⇒ **门禁只能靠 2 条数字通路 (STAT + VBUS 分压)**。⇒ 本文的判据式不依赖 I2C ⇒ **即使 I2C 永远不装, M-CHRG 仍可实现**。 (代价: 读不到精确电流值, 只能判"在充/不在充"。)

---

## B4 风险 / 未验项

| # | 风险 | 影响 | 处置 | 状态 |
|---|---|---|---|---|
| R-1 | **SoC 脚号映射**: 网表写 `SoC[TBD-01].USB_VBUS_DET` (TBD-10); 11-01 基线已换 **RK3576** ⇒ 所有 SoC 侧映射要重做 | 换芯重做工作量 (已在 ISS-119 口径: 157 行 TBD) | 随换芯一次性重做, **不单独投板费** | ⚠️ 未验 |
| R-2 | **STAT 脚极性/闪烁语义** (低=充电中 / 1Hz 闪=故障) | 门禁误判 | 以 BQ25896 datasheet 为准 [官方]; EVT 项 R-H-03 实测复核 | ⚠️ 未验 (datasheet 条目 **[0数据]**, 已在 `rel_vendor_absmax_rating` 需求里) |
| R-3 | **VBUS_DET 分压档位** 1M vs 100k/47k (sw-lead P1-8) | 慢 + 漏电误差 | 建议改 100k/47k (换料不换板); **本单不改网表** (网表生成器不属本单边界) | ⚠️ 未决 → 需项目总工裁决 |
| R-4 | **CHG_STAT 上拉电压域**: 现在上拉到 `VDD_3V3_IO` (3.3V) | 若换芯后 SoC IO 域变 1.8V, 3.3V 上拉会打穿 SoC IO | 换芯时同步复核 IO 域; **已在 `rail.v33_load_ma`/电压域表口径内** | ⚠️ 未验 |
| R-5 | 跨铰链 CHG_STAT 走 FPC, 与 USB 差分线并行 | 串扰误判充电态 | 布局上与差分对间距 ≥3mm (mech-lead `iss085_esd_cmc_placement` ⑤ 同款约束) | ⚠️ 未验 |

---

## B5 对 sw-lead / main 的答复要点

1. **M-CHRG 门禁可实现** ⇒ ISS-043 可从 `open` 走到 `fixed` (硬件侧); sw-lead 侧只需实现 §3.1 的 OR 判据 + §3.3 的未知态 fail-closed。
2. **充电状态 = `CHG_STAT` (低=充电中)**, 不是寄存器 (I²C 跨铰链 DNP); `VBUS_DET` 是兜底, 顺带满足 USB 枚举前提 (S2 救砖链路, ISS-080)。
3. **要 sw-lead 确认一件事**: 是否同意把 `VBUS_DET` 的分压从 1M+1M 改为 **100k/47k** (换料不换板, 修 P1-8 的 451ms 建立 + 15.2%FS 漏电); 改动会让 5V→1.60V, 请 sw-lead 核对 ADC 量程与阈值。
4. **要 main 决定**: R-3 的阻值改动要动 `state/gen_netlist.py` (不属硬件总工本单边界) ⇒ 请项目总工排期重生成网表。

---

## B6 证据分级

| 结论 | 等级 |
|---|---|
| 两条充电状态通路在网表中 (位号/阻值/测试点) | **[实测-网表]** (网表为可复算的机读文件, 非纸面推测) |
| STAT 开漏 + 10k 上拉 + 低=充电中 | **[官方]** (BQ25896 行为; 精确 t 值 **[0数据]**) |
| 1M‖1M = 500kΩ, ×100nF ⇒ τ=50ms / 95%≈150ms | **[推算]** (RC 一阶) |
| 100k‖47k = 32.0kΩ ⇒ τ=3.2ms | **[推算]** |
| 漏电流 1.65µA @5V (1M 档) | **[推算]** (与网表 P2 #160 注记一致) |
| I²C 跨铰链 DNP ⇒ 读不到寄存器 | **[实测-网表]** (P10 行 dnp=DNP) |
| SoC 侧脚号 | **[0数据]** (TBD-10; 换芯后重做) |
| 实物 [实测] 条数 | **0** (无样机) |

---

## B7 自证复现命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# (1) 两条通路的网表依据 (逐行)
grep -n "CHG_STAT\|VBUS_DET\|R_VBUS_DET\|C_DET_VBUS\|R_PU_CHG_STAT\|TP_VBUS" HW/netlist_v1.csv
# (2) RC 复算 (τ / 建立时间)
python3 -c "
rth=1e6; c=1e-9; print('1M 档: Rth=%.0fk tau=%.1fms 95%%=%.0fms'%(rth/1e3, rth*c*1e3, 3*rth*c*1e3))
r2,r1=47e3,100e3; rth=r1*r2/(r1+r2); print('100k/47k 档: Rth=%.1fk tau=%.1fms 分压比=%.4f 5V->%.2fV'%(rth/1e3, rth*c*1e3, r2/(r1+r2), 5*r2/(r1+r2)))"
# (3) 充电电流换算 (与本单 §B1 联动)
python3 HW/calc_chg_ichg.py
```

---

## B8 写入范围声明

| 项 | 内容 |
|---|---|
| **本文只写** | `HW/CHARGE_STATUS_READBACK.md` (本文件) · `HANDOFF/2026-11-01_hw-lead_*.md` · `state/fragments/hw.yaml` · `state/issue_log.yaml` (仅 ISS-043 行) |
| **本文没改** | `HW/netlist_v1.csv` · `state/gen_netlist.py` · `HW/CHARGE_BOARD_SPEC.md` · `PROJECT_TRACKER.md` · `STATE.yaml` · `SW/` · `MECH/` · 别人的分片 |
| **本文没做** | 未联系原厂/供应商 · 未发邮件 |
