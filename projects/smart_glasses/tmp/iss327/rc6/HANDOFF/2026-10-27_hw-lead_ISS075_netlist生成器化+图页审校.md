# [hw-lead→PM] ISS-075 重派 · 器件级 netlist 搬进生成器 + 8 页图页审校
- 发起方: hw-lead
- 日期: 2026-10-27
- 结论: 器件级 netlist 已从"手改在 CSV 里"搬进生成器 (唯一真源), 重跑幂等; 行数 276→**347** 数据行 (门禁要求 ≥277), `check_netlist.py` **12/12**; 8 页图页审出 **17 处**与硬件现实冲突并全部改掉; 另查出 **1 个会短路的硬伤** + **1 个未解的架构冲突**。
- 依据: `state/gen_netlist.py` · `state/gen_schematic_pages.py` · `state/gen_kicad_net.py` · `HW/netlist_v1.csv` (348 行) · `HW/SCHEMATIC_V1.md` (511 行) · `HW/netlist_v1.net` (1284 行)

## B1 结论摘要

1. **生成器补齐 (第一优先级已完成)**: `state/gen_netlist.py` 从 **108 行 → 347 行数据行** (文件 348 行), 器件级全部用**代码**实现 (充电链 ESD 阵列 / π 滤波 / 2×MOS / 充电 IC 周边 / P7 LED 限流 + 按键 RC 消抖 / 连接器与保护件 / 每条轨去耦)。重跑**幂等** (两次重跑字节一致, 已验)。`python3 state/check_netlist.py` → **12/12 全过**。
2. **8 页图页审校**: 审 `HW/SCHEMATIC_V1.md` 8 页, 查出 **17 处**与硬件现实冲突, 改法全部落在 `state/gen_schematic_pages.py` 的 `NARRATIVE` + `PAGES` (叙述的源), **重跑生成**, 没手改 .md。其中 4 处是**数字错**、2 处是**乱码/错 TBD 号**、11 处是**漏件/矛盾口径**。
3. ★**查出 1 个会短路的硬伤**: 上一轮手改的 277 行 CSV 里, `KEY_VOL+` 与 `KEY_VOL-` 两行的 node2 **都是 `NET_KEY_VOL`** → **两个音量键被短接** (装板后按一个键两个都响应)。生成器里已拆成 `NET_KEY_VP` / `NET_KEY_VM`, 各自独立上拉 + 独立消抖电容。
4. ★**查出 1 个未解的架构冲突 (本轮最大发现)**: Type-C 座在**充电板** (ISS-014 决策 5: 充电板挪镜框), 而 `USB_D+/D-` 的对端是**主 PCB (镜脚)** 里的 SoC → **USB 差分对必然跨铰链**; 而 Type-C 恰恰是我们**唯一的外露烧录/调试口**。USB 2.0 (官网说 3.0 → 还多 4 根 SS 差分) 跨铰链 = 眼图直接废。→ `CONN_USB` 位已由 DNP 改为**必留**, 两条出路 (Type-C 挪主 PCB / 调试改走 J_DEBUG+J_UART) 写在 P6 叙述, **请 PM 拍板** (见 B5 接口请求 1)。
5. ★**USB 差分 90Ω 保持不动** ✅: 规格 B-21/B-22 原文就是 `90Ω ±10% (与 MIPI 不同模板!)`; USB 2.0 D+/D− 的规范差分阻抗就是 90Ω, 与 MIPI/DSI 的 100Ω **不是同一个模板**。已在 P6 叙述加一句"不要为了统一成 100Ω 去改 (那是把规格改坏)"。

## B2 验收标准自评

| 验收标准 | 自评 | 依据 |
|---|---|---|
| `python3 state/gen_netlist.py` 产出 ≥ 277 行 | ✅ 通过 (348 文件行 / 347 数据行) | B6 命令 1 |
| `python3 state/check_netlist.py` 12/12 | ✅ 通过 (12/12, 0 失败) | B6 命令 2 |
| 生成器幂等 (重跑不丢内容) | ✅ 通过 (两次重跑 `cmp` 字节一致) | B6 命令 5 |
| 8 页图页齐全 P1..P8 | ✅ 通过 (grep 出 P1..P8) | B6 命令 3 |
| `state/gen_kicad_net.py` 重跑 + `netlist_v1.net` 更新 | ✅ 通过 (279 器件 / 152 net / 1284 行, 连接器全部进 .net) | B6 命令 4 |
| `merge.py` + `gate_check.py` rc=0 | ✅ 通过 (rc=0) | B6 命令 6 |
| 器件级内容在生成器里 (不在 CSV 里手改) | ✅ 通过 (CSV 已是纯生成物) | `state/gen_netlist.py` 全文 |
| 球位号 0 编造 | ✅ 通过 (62 个 SoC 节点全是 `SoC[TBD-01].<信号>`) | B6 命令 7 |
| net 名合法标识符 (无 `+`) | ✅ 通过 (生成器出口自检 + 复查 0 例外) | `NET_RE` + B6 命令 7 |
| 56 条连接全覆盖 | ✅ 通过 (56/56) | check_netlist 判据 1 |
| **USB 差分跨铰链方案** | ❌ **不通过** (硬件本身冲突, 需 PM/结构拍板) | B5 接口请求 1 |
| **`U_BRIDGE` 是 redriver 还是 DP→DSI 桥接** | ❌ **不通过** (规格自相矛盾, 未定) | B5 接口请求 2 |
| **连接器 pin 编号** (`J_CHG`/`J_TYPE_C`/`CONN_CAM`) | ⚠️ **未验** (本版**自拟**, 非规格/原厂给定) | B5 接口请求 3 |
| 各电源域标称电压 / SoC 球位号 | ⚠️ 未验 (原厂未回, TBD-01/TBD-02) | B5 |

## B3 证据分级

| 关键结论 | 等级 | 说明 |
|---|---|---|
| netlist 347 行 / 门禁 12/12 / 生成器幂等 | [实测] | 本轮脚本自跑, B6 可复现 |
| LDO 是 7 路 (S28/S18/S12/L33/L18/IO33/IO18) | [实测] | 从生成的 CSV 逐个数 (`TPS7A20-*` 出现次数) |
| 物理测点 40 个 / 逻辑 TP 13 个 | [实测] | netlist 里 `,TP,` 行数 = 40; 规格 `testpoints` = 13 |
| R_SEL 实物 16 颗 (逻辑 8 位) | [实测] | netlist 里 `R_SEL_*`=10 + `BR_*`=6 |
| USB 差分 90Ω | [官方] | 规格 B-21/B-22 原文 + USB 2.0 规范模板 |
| MIPI/DSI 差分 100Ω ±10% | [官方] | 规格 A-01..A-20 `imp` 字段 |
| 充电链在充电板 / SoC 在主 PCB / 两者跨铰链 | [官方] | `PROJECT_TRACKER.md` 决策 5 (ISS-014 关闭) + `INTERFACES.md` 充电板行 |
| USB 差分跨铰链的 SI 风险 | [推算] | USB 2.0 D+/D− 90Ω 差分 + 铰链行程抖动 → 阻抗不连续; **量化待实测** |
| 散热 0.90W → 80.1°C / 96.1°C | [推算] | `MECH/MECH_BUDGET.md` §2.6 (只读引用, 已核对一致, **未改**) |
| `U_BRIDGE` 到底是 redriver 还是桥接芯片 | [0数据] | 规格 A-21 写 "redriver 位", P4 `BR_*` 写 "桥接芯片", 两者互斥未决 |
| NTC 是裸分压还是数字温度计 | [0数据] | 规格 B-01 只写 "NTC", 未说形态 |

## B4 接口取值声明

| 接口 | 本版取值 (短规范值) | 说明 |
|---|---|---|
| netlist 行数 | `347` | 生成器数据行; 文件 348 行 (含表头) |
| 物理测试点 | `40` | 逻辑 13 条按合并名展开 |
| 0Ω 位 | `R_SEL 10颗 + BR 6颗` | 逻辑 8 位 → P/N 拆位后 16 颗 |
| LDO 路数 | `7` | + 2 路 DC-DC |
| USB 差分阻抗 | `90Ω ±10%` | **不改** |
| MIPI/DSI 差分阻抗 | `100Ω ±10%` | 不改 |
| CONN_USB | `必装` | USB 差分跨铰链 → 位必留 |
| U_BRIDGE | `DNP` | 方案B 才装; redriver/桥接未定 |
| MCLK 串阻位 | `必装` (值待 TBD-03) | 位必留, 不是 DNP |
| LED_B + R_LED_B | `DNP` | 第一版不上无线 |
| 电源去耦 | `10µF + 100nF / 每条轨` | 标准 PDN, 值随负载核 |

## B5 未决项与卡点

**接口请求 (给 PM, 不直接联系其他总工):**

1. **★USB 差分跨铰链 (最高优先)** — 对方: PM + mech-lead (走 PM 转达)
   - 我的需求: Type-C 位置定板 → (a) Type-C 挪主 PCB (镜脚) 侧, 充电 IC 留充电板, **电池大电流线**跨铰链; 或 (b) Type-C 留充电板, **调试改走板上 `J_DEBUG` (1×4) / `J_UART` (1×2)**, Type-C 只做充电。
   - 我的假设 (若不回应): **按 (b) 画** —— `CONN_USB` 位必留但走线按"USB 只充电、不做调试"预留; 烧录流程等 SW 总工用 UART/JTAG 走线。
   - 卡点: 铰链行程 / 跨铰链走线长度预算 (ISS-065 结构建议) + 用户可及性 (Type-C 开孔 9.5×3.6mm 在镜框还是镜脚)。
2. **★`U_BRIDGE` 定位** — 对方: PM → 原厂 (TBD-04) + JBD 接口定义
   - 我的需求: 这颗是 redriver (只做缓冲) 还是 DP→DSI 桥接芯片 (要协议/电平转换)?
   - 我的假设: 按"DP→DSI 桥接"留位 (P4 `BR_*` 走它的 DSI 输出), 型号/封装全 DNP。
3. **★连接器 pin 编号与型号** — 对方: PM → mech-lead + 装配
   - 我的需求: `J_CHG` (1×6 跨铰链排线) / `J_TYPE_C` / `CONN_CAM` (40p) 的 **pin 编号 + 型号 + pitch + 翻盖方式**。
   - 我的假设: 本版 pin 编号是**我自拟**的 (已在 netlist 里逐条标注 "★本版自拟, 非规格给定"), 装配前必须复核。
4. **★NTC 形态** — 对方: PM → 原厂 + sw-lead
   - 我的需求: "NTC 挂 I2C_A" 到底是裸 NTC 分压 (→ 改成 ADC 位) 还是数字温度计 (→ 留 `U_TEMP` DNP 位)?
   - 我的假设: 按数字温度计留 DNP 位。

**等外部 (不是我的锅):**
- SoC 引脚表 / 球位图 / FCCSP pitch → 原厂 (TBD-01/TBD-05), 邮件 10-21 已发, 未回。
- 各电源域标称电压 / 上电时序 → 原厂 (TBD-02)。
- CSI lane 数 / MCLK 电压 / AC 耦合是否内置 → 原厂 (TBD-03)。
- 显示 TX 接口类型 → 原厂 (TBD-04) + JBD 开发套件接口定义。
- 光机 1.8V/5V 轨电压 → JBD。

**我自己的下一步 (不需外部):**
- 把本轮 netlist 的 347 行滚成 BOM 初稿 (含 42 行"待选型/待原厂"标红)。
- PCB 逃线评估: 16 颗 0Ω + 7 路 LDO + 2 路 DC-DC 的布局密度 (等 pitch 结论)。

## B6 自证复现命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# 1) 生成器行数 (必须 >= 277)
python3 state/gen_netlist.py && wc -l HW/netlist_v1.csv

# 2) 门禁 (必须 12/12)
python3 state/check_netlist.py

# 3) 8 页齐全
python3 state/gen_schematic_pages.py && grep -o "^## P[0-9]" HW/SCHEMATIC_V1.md | sort -u | tr '\n' ' '

# 4) KiCad .net
python3 state/gen_kicad_net.py && wc -l HW/netlist_v1.net

# 5) 幂等 (两次重跑字节一致)
cp HW/netlist_v1.csv HW/.iss075_bak/_t.csv && python3 state/gen_netlist.py >/dev/null && cmp HW/.iss075_bak/_t.csv HW/netlist_v1.csv && echo IDEMPOTENT

# 6) 状态门禁 (必须 rc=0)
python3 state/merge.py && python3 state/gate_check.py; echo "rc=$?"

# 7) 球位号 0 编造 + net 名合法 + 阻抗抽查
python3 - <<'PY'
import csv,re
rows=list(csv.DictReader(open('HW/netlist_v1.csv',encoding='utf-8')))
soc=[r for r in rows if 'SoC[' in r['node1']+r['node2']]
print("SoC 节点", len(soc), "| 缺 TBD-01 占位",
      sum(1 for r in soc if not re.search(r'SoC\[TBD-01\]\.', r['node1']+r['node2'])))
print("非法 net 名", {r['net'] for r in rows if not re.match(r'^[A-Za-z0-9_]+$', r['net'])} or "无")
print("USB 阻抗", {r['value'] for r in rows if r['net'].startswith('USB_D') and r['type']=='NET'})
PY
```

## 待办: 需要项目总工做什么
1. **拍板 USB 跨铰链方案** (接口请求 1) —— 这一条不定, P6/P1 画不下去。
2. 把接口请求 2/3/4 转给对应的人 (原厂 / mech-lead / sw-lead)。
3. **分片登记**: 本轮**没有**写 `state/fragments/` (按 ISS-075 任务边界, 分片归并行中的 ISS-078 会话) → 本单的 `answers` / `interface_claims` **尚未登记**, 请 PM 在收尾时补或指派登记人。
4. 本单新增缺口 (USB 跨铰链 / `U_BRIDGE` 定位 / 连接器 pin 编号 / NTC 形态) 已写进 `HW/SCHEMATIC_V1.md` 文末缺口清单 (10 条)。

## 阻塞: 缺什么信息
- 原厂 SoC 引脚表 / 球位图 (TBD-01) —— 未回, 第 6 天。
- 原厂电源域表 (TBD-02) —— 未回。
- 原厂 CSI 规格 (TBD-03) —— 未回。
- 原厂显示 TX 结论 (TBD-04) —— 未回。
- JBD 光机接口定义 + 供电电压 —— 未回。
