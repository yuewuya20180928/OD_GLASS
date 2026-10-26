# 硬件原理图投板前检查清单 (ERC / DRC) —— V1

> **归属**: 项目总工 (main)。**作用**: 把"图看起来对"变成"每一项都能机械判或明确签字"。
> **对应交付物**: `HW/SCHEMATIC_V1.md` (8 页图页) · `HW/netlist_v1.csv` (netlist) · `HW/netlist_v1.net` (KiCad 可 import) · `HW/SCHEMATIC_V1_SPEC.json` (图纸规格) · `HW/SCHEMATIC_REFDIE.md` (SoC 侧 79 功能位号 + 证据等级) · `HW/INTERFACE_TABLE.md` (56 条连接) · `HW/POWER_BUDGET_V2.md` (功耗与皮肤温度)
> **原则**: 每条判据要么**有脚本能跑** (§A), 要么**有明确责任人签字** (§D) —— 不许有"看着没问题"这种判据。

---

## §0 放行判据 (DoD): 全部满足才叫"可投板"

| # | 条件 | 怎么判 | 现在 |
|---|---|---|---|
| 1 | **机械门禁全绿** | `python3 state/check_netlist.py` → rc=0 且 12/12 | ✅ 已过 |
| 2 | **8 页齐全且与 netlist 同步** | `grep -o '^## P[0-9]' HW/SCHEMATIC_V1.md \| sort -u` = P1..P8 | ✅ 已过 |
| 3 | **生成器幂等** | 重跑 `gen_netlist.py` / `gen_schematic_pages.py` / `gen_kicad_net.py` → 两个 STL 无关, 但 **CSV 与 .md 的 md5 不变** | ⚠️ 待 hw-lead 交卷后重跑核对 |
| 4 | **原厂 4 项闭合** | 引脚表+球位图+pitch · 电源域表 · 显示 TX 结论 · 启动存储方案 | 🔴 **未闭 (TBD-01/02/04/06/11)** |
| 5 | **板宽/叠层复核通过** | ISS-078 (官网"宽度≤8mm" + pitch 0.3/0.4/0.5mm 三档) | 🔴 未闭 |
| 6 | **交叉评审两方通过** | mech-lead (机械/热/装配) + sw-lead (时序/信号/电源时序) 各出结论 | ⚠️ 未做 |
| 7 | **器件级 netlist 补齐** | 充电链 ESD/π滤波/MOSFET + LED 限流 + 按键消抖 + 去耦 | ⚠️ ISS-075 在做 |
| 8 | **BOM 齐** | 每行有: 位号 / 值 / 封装 / 容差 / DNP / 替代料 | ⚠️ 随 ISS-075 |
| 9 | **投板前 3 个"人眼项"签字** | 见 §D | 🔴 未签 |

---

## §A 机械可判 (脚本能跑, 不靠人眼)

| # | 判据 | 脚本 | 现状 |
|---|---|---|---|
| A1 | 56 条连接全覆盖 (每条 conn_id 至少 1 行) | `check_netlist.py` ① | ✅ |
| A2 | 每条 net 两端齐全 (node1/node2 非空) | ② | ✅ |
| A3 | DNP 标注只用 3 档 (必装/DNP/可选) | ③ | ✅ |
| A4 | 证据等级只用 7 档 (官方/推算/实测/待原厂/待JBD/同Die参考-待官方确认/0数据) | ④ | ✅ |
| A5 | TBD 编号落在 TBD-01..TBD-13 (对应 13 项画不了清单, 编号一致) | ⑤ | ✅ |
| A6 | A 组高速差分阻抗**逐条对照规格** (不许用"全是 100Ω"这种粗判) | ⑥ | ✅ |
| A7 | 差分对成对 (每个 _P 有 _N) | ⑦ | ✅ |
| A8 | 13 个测试点全部在图 | ⑧ | ✅ |
| A9 | 13 条电源轨全部在图 | ⑨ | ✅ |
| A10 | 显示双出口互斥: `R_SEL_*` 与 `BR_*` 不得同时装 | ⑩ | ✅ |
| A11 | 8 页齐全 (P1..P8) | ⑪ | ✅ |
| A12 | 同一 net 不得有多个输出驱动 | ⑫ | ✅ |
| A13 | **SoC 侧零编造球号** (grep `SoC[` 必须是 `SoC[TBD-01].` 形式, 不许出现具体球号) | `grep -n 'SoC\[' HW/netlist_v1.csv \| grep -v 'TBD-01'` → 应为空 | ⚠️ 随 ISS-075 复跑 |
| A14 | **禁改文件未被 sub agent 动过** (mtime 比对) | `ls -l --time-style=+%m-%d\ %H:%M MECH/fit_check.py MECH/print/verify_pack.py state/measurements.yaml` | ⚠️ 随 ISS-075 复跑 |
| A15 | 重量表与温度表口径一致 (MECH_BUDGET ↔ POWER_BUDGET_V2) | 人工 + grep 关键数 | ✅ 41.6-42.6°C / 80.1°C 口径已对齐 |

---

## §B 电气判据 (ERC 类 —— 可用脚本或逐条核对, 不许含糊)

| # | 判据 | 现状 |
|---|---|---|
| B1 | **每个电源域都有来源与去向**: 13 条轨各有上游 IC 与负载标注 | ✅ P1 页逐条列了 |
| B2 | **每条轨都有电流上限与依据** (V_CORE ≥2.0A / V_SOC_IO ≥1.0A / SYS 0.55A ...) | ✅ 引自 INTERFACE_TABLE + POWER_BUDGET_V2 |
| B3 | **R-F1 电源拓扑**: UVP 抬到 3.5V + 3.3V 改由 TPS62130A 供 (末段 12-15% 电量不黑屏) | ⚠️ 画的是基线, 第三条路评估中 (ISS-067) |
| B4 | **V_CORE 电压上界按 1.0V** (查证: 0.65-1V DVFS) 而非 0.9V | ⚠️ 待 hw-lead 按 ISS-077 更新 |
| B5 | **SoC 域上电时序**: 哪轨先起 / RESET 何时释放 / 内部 DCDC 同步 | 🔴 待原厂 (TBD-12) + ISS-067 |
| B6 | **去耦**: 每个电源引脚就近 0.1µF + 每条轨 1×10µF (具体值待器件定) | ⚠️ 随 ISS-075 补器件级 |
| B7 | **极性/方向**: 所有电源/信号方向与 INTERFACE_TABLE 一致; 电容极性、LED 方向、TVS 方向 | ✅ 方向在 netlist note 里 |
| B8 | **无悬空**: 每个 net 至少有 2 个连接 (除单点测试点/预留) | ✅ (A2 + 逐条) |
| B9 | **I2C 地址不冲突**: 4 个从设备地址唯一 (总线 A 2 个 + 总线 B 2 个) | ✅ 规划在 INTERFACE_TABLE §4.2 |
| B10 | **双出口互斥在 BOM 层也成立** (两组 0Ω 分开列, 装配决定) | ✅ A10 + BOM 要求 |
| B11 | **未用 4-lane CSI 的 D2/D3 与 BR_* 全 DNP** | ✅ A10 + netlist dnp 列 |
| B12 | **XTAL 双方案**: 内部 RC 不装 / 外部晶振焊盘位不装 (原厂一句话定生死) | ✅ P8 页 |

## §C 物理 / 布线判据 (DRC 类 —— 交给 PCB 阶段逐条签)

| # | 判据 | 依据 | 现状 |
|---|---|---|---|
| C1 | **差分 100Ω ±10%** + 差分对内间距/外部间距规则 | 规格 A 组 | ⛔ 需 SoC 侧 pin (TBD-01) |
| C2 | **差分对长度匹配** (组内 ≤5mil) + 跨铰链段单独控 | 经验规则 | ⛔ 同上 |
| C3 | **AC 耦合电容位置**: 靠近从设备 (sensor) 侧, 不靠近 SoC | 规格原文 "AC 耦合电容位" | ✅ 位置已标 |
| C4 | **对地端接 100Ω 位置**: 靠近 SoC 侧 (发射端) | 规格原文 | ✅ 位置已标 |
| C5 | **跨铰链段**: 走线随结构件过铰链, 与电源并行间距 ≥3mm, MCLK 单独包地 | 规格 A-11 | ⚠️ 需与结构/EMC 联合确认 |
| C6 | **去耦回路面积最小** (电容—球 距离 <3mm) | 经验规则 | ⛔ 需球位图 |
| C7 | **散热铜箔与热点**: SoC 下方/上方导热路径, 不与敏感信号冲突 | MECH 热模型 | ⚠️ 待 ISS-077 功耗 V3 后复核 |
| C8 | **板宽 12mm + 4-6 层** 假设 | 老板锁死 | 🔴 **ISS-078 复核中 (官网宽度≤8mm)** |
| C9 | **地平面完整性与回流路径** (跨铰链段的回流) | EMC_PRECHECK R-01~R-12 | ⚠️ 随 PCB |
| C10 | **保护器件靠近接口** (ESD 在 Type-C/连接器侧) | EMC | ⚠️ 随 ISS-075 补器件级 |

## §D 必须人工签字的 3 项 (脚本判不了, 也不许含糊)

| # | 项 | 责任人 | 判据 |
|---|---|---|---|
| D1 | **原厂 4 项闭合**: 引脚表+球位图+pitch (TBD-01/05) · 电源域表 (TBD-02) · 显示 TX 结论 (TBD-04) · 启动存储 (TBD-06/11) | 酷芯微书面答复 | 回信后按 `SCHEMATIC_REFDIE.md` §9 的差异修订清单逐条打勾, **不重画** |
| D2 | **交叉评审**: mech-lead 挑机械/热/装配刺 + sw-lead 挑时序/信号/电源时序刺 | 两个总工 | 各自出书面结论 (进 `HANDOFF/`), 我裁决 |
| D3 | **投板决定**: 老板拍板 G1 (原理图/PCB 定稿) | boss | 阶段门 `state/stage_gate.py` 从 G0 → G1 |

## §E 本清单与已有门禁的对应 (别重复造轮子)

| 门禁 | 管什么 | 跑法 |
|---|---|---|
| `state/check_netlist.py` | §A 的 12 条 netlist 判据 | `python3 state/check_netlist.py` |
| `state/issue_check.py` | 问题闭环 (字段/状态机/验证分离/逾期/双向覆盖) | `python3 state/issue_check.py` |
| `state/gate_check.py` | 交付质量门 (Q1-Q5 证据分级/交接单) | `python3 state/gate_check.py` |
| `state/stage_gate.py` | 阶段门 (G0→G1) | `python3 state/stage_gate.py` |
| `state/merge.py` | 共享状态源合并 (冲突检测) | `python3 state/merge.py` |
| `state/daily_check.py` | 巡检 + 漂移 | `python3 state/daily_check.py` |
| `state/publish_github.sh` | GitHub 同步 (脱敏 + API 验 SHA) | `bash state/publish_github.sh "说明"` |

---

## §F 一句话

> **机械的 15 条现在全绿, 但 §D 的 3 项 (原厂 4 条 + 交叉评审 + 投板决定) 一项都没闭 → 所以现在的状态是"可评审", 不是"可投板"。**
> **原厂回信后, 按 REFDIE §9 差异清单逐条打勾, 不重画。**
