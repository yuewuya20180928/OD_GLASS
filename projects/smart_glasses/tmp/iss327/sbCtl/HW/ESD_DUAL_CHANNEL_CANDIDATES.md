# HW/ESD_DUAL_CHANNEL_CANDIDATES.md —— USB D+/D− ESD 选型候选集 + 落位可行性 (ISS-307)

> **owner**: hw-lead · **单号**: ISS-307 · **派活**: 项目总工 (main / moli) · cron `fb67af40` · 2026-11-18 03:2x
> **性质**: ★**内部活 · 纯分析/选型研究 · 零写板 · 零落表 · 零改闸 · 零改网表 · 零外发** ★ ⇒ ★**本页不替老板拍板** ★
> **证据纪律**: 每条结论带等级 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` · 官网原文抓取件在 `logs/iss307/evidence/`
> **复现**: 见 `HANDOFF/2026-11-18_hw-lead_ISS307_ESD选型候选集.md` §B6

---

## §0 · 一句话结论

★★**老板手上这两个字母 (need key `boss_esd_model_axis_pending_20261117`) 不是 1 个问题而是 2 个串行问题, 本页把它们拆成【2 个决策码 + 4 个 OPN 选项】, 老板回一行就能一次拍完** ★★

- ★**W-2** (第②问) = D− 侧补不补 ESD ⇒ ★**它先决定架构档 (W-1b)**: 补 ⇒ 必须 3 脚双通道件; 不补 ⇒ 维持 2 脚单通道 + R4 判据口径必须显式改 ★
- ★**W-1c** (第①问) = D+ 那颗的【真 OPN】⇒ ★**4 个官网候选已备齐 (C1/C2/C3/C4)**, 全部是 3 脚小封装, 全部逐字对得上台账 B-3 要求的 `pin1=D+ / pin2=D− / pin3=GND` ★
- ★**落位可行性结论**: ★**3 脚小封装在 R9 的 ≤3.0 mm 判据内【放得下】, 但唯一可落窗口是 `J_USB_C` 正下方 y ≈ 7.65~8.25 mm 一条窄带** ★ (几何证据见 §2)
- ★**★一条必须先说的硬发现**: ★**决策页 §A 与 ISS-306 给的落位候选坐标 (137.18, 6.28) 实测距离 = 3.0022 mm > 3.0 ⇒ 按那个坐标画板, R9 依然判红 ⇒ 板要改第二次** ★ (见 §2-4)

---

## §1 · ★★§1-B1-0 · 台账内部那处硬矛盾的判决★★

### 1-1 · 矛盾原文 (两行, 逐字)

| 行 | 出处 | 逐字内容 |
|---|---|---|
| ★**L166 (B-3)** ★ | `HW/SCHEMATIC_LANDING_V1_LANDED.md` §4「落表后需要【板侧】同步的清单」 | ★**`D_ESD_USB_D` 从 2 脚换 3 脚封装 (pin1=D+ / pin2=D− / pin3=GND)** ★ + 定位列写「板文件 `D_ESD_USB_D` (★现 pads=2, pad1→`USB_D_P_SRC` / pad2→GND, 原点 (94.95, 21.80)★)」 ★ |
| ★**L934 (§18.2 第 4 行)** ★ | `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.2「14 件的落表决定」 | ★**`D_ESD_USB_D` 落表后 value = `TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)`** ★ + opn 列 = `TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)` ★ |

★**⇒ L166 要求「一颗 3 脚件吃 D+ 与 D−」, L934 落的却是「一颗 2 脚单通道件 (X1SON-2 · 1=I/O 2=GND)」 ⇒ 2 脚件物理上没有第三只脚接 D− ⇒ 两行互相打架** ★

### 1-2 · 台账自己有没有承认过这个矛盾? —— ★**没有** ★

- ★**grep 证据 [实测]** ★: 在 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 全文里 grep `矛盾` / `冲突`, 命中 **3 条**, 全部是 **P9 页正文 vs 网表 (d6 ⑤)** 与 **补差A ⑤ 判据 5** 两族, ★**没有一条是 ESD 架构/封装这条** ★
- ★**B-3 / B-4 在台账里出现 2 次 (L166-L167 与 L429-L430), 两次都写「无变化 · 照旧」** ★ ⇒ ★**台账没有在任何一处标注「此处待老板拍架构」** ★

### 1-3 · ★★判决: 走 **B 档 (方向还没落表) + C 档 (真源在别处) 的合并** ★★

★**判决口径 (任务书给的三档对照)**: ★

| 档 | 任务书定义 | 本单判决 |
|---|---|---|
| A | 方向已落表 (3 脚双通道件) ⇒ 老板只差选 OPN | ★**不成立** ★ |
| B | 方向还没落表 (台账只是待选型占位) ⇒ 老板要拍「方向 + 型号」两件 | ★**成立 (方向这一半)** ★ |
| C | 台账两处都有历史版本, 真源在别处 ⇒ 给真源路径 + 行号, 不许自己下结论 | ★**成立 (真源这一半)** ★ ⇒ ★**真源路径已给出 (下表), 但「以哪行为准」是 main/老板的活, 本单不代判** ★ |

### 1-4 · ★★真源路径 + 行号 (★C 档要求的交付物★) ★★

| 真源层 | 路径 : 行号 | 逐字/实测内容 | 等级 |
|---|---|---|---|
| ★**① 机器真源 (网表行数 = 架构形态)** ★ | `state/gen_netlist.py` **L1451** (信号行) + **L1454** (GND 行) | `add("P1", "NET_USB_D_P_TYPEC", "D_ESD_USB_D", ...)` + `add("P1", "GND", "D_ESD_USB_D", "GND", ...)` ⇒ ★**恰好 2 行 = 1 信号 + 1 GND** ★ | `[实测]` |
| ★**② 架构判定器 (机器怎么判「现在几脚」)** ★ | `state/land_v_values.py` **L888 / L890 / L892** (在 `v2_read_source()` 里) | `ro["arch"] = "single2"` (2 行 1 信号 1 GND) / `"dual3"` (3 行 2 信号 1 GND) / `"unknown"` ⇒ ★**按行数判, 不看型号串** ★ | `[实测]` |
| ★**③ 落表真源 (型号)** ★ | `state/gen_netlist.py` **L122** (`PARTS` 字典) | `"D_ESD_USB_D": {"footprint": "", "opn": "TPD1E05U06DPYR (TI X1SON DPY 2-pin · 1=I/O 2=GND · Cd 0.42pF · IEC 61000-4-2 lvl4)"}` | `[实测]` |
| ★**④ 老板已拍的决定 (架构轴)** ★ | `DECISION_PENDING_2026-11-16.md` **L824** | ★**「A3 = V-2 = 1 (ESD 架构轴 ① 2脚单通道) 已于 12:16:08 真落表 (rc=0)」** ★ | `[实测]` |
| ★**⑤ 落表凭据 (谁批的)** ★ | `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 `LANDING_AUTH` 表 (`ISS-283` 行) | `| ISS-283 | HW/netlist_v1.csv | netlist | 417 | ["D_ESD_USB_D", "USB_D_P_SRC"] | ["D_ESD_USB_D", "NET_USB_D_P_TYPEC"] | 2026-11-17 | 2026-11-17 A3 = 1 |` | `[实测]` |
| ★**⑥ 架构档位表 (3 脚档的工具已就位)** ★ | `state/land_v_values.py` **L721-L743** (`V2_ARCHS`) | ★**`"2": dict(shape="dual3", title="② 3 脚双通道", desc="★一颗 3 脚件覆盖 D+ / D− / 地 (pin1=D+ / pin2=D− / pin3=GND)★", cost="★★占位只有 2 焊盘 ⇒ 3 脚件物理落不下 ⇒ 必须先改 footprint (板那一趟 B-3) ⇒ 板 md5 要变★★")** ★ | `[实测]` |
| ★**⑦ 落表器对 arch=2 的行号漂移已写死** ★ | `state/land_v_values.py` `V2_NETLIST_SHIFT_FROM = 418` · `V2_PINS_SHIFT_FROM = 174` | ⇒ ★**arch 2 这条路在工具侧是通的 (不是空想)**, 但 ★**它要求显式 `--v2-arch=2 --v2-model=<型号> --v2-evidence=<等级>`, 落表器绝不替老板选架构** ★ | `[实测]` |

### 1-5 · ★★结论 (★不替老板签字, 只给事实链★) ★★

1. ★**「3 脚双通道件」这个方向 = 【已工具化的待拍选项】(arch 档 2), 不是已落表的既定设计** ★ —— 机器真源 (网表 2 行 = `single2`) 与老板 09:49 的 A3=V-2=1 一致, 与台账 L934 的 `TPD1E05U06DPYR` (2 脚) 一致. ★**与台账 L166 (B-3) 不一致.** ★
2. ★**⇒ 台账 L166 与 L934 的矛盾 = 【台账自身未登记的内部不一致】, 且当前机器真源站在 L934 这一边** ★ —— ★**但 L166 是「板侧动作清单」, 不是「已落表真源」; 它写的 3 脚方向要等 W-2 = 补 才会被激活** ★
3. ★**⇒ 老板要拍的是 2 个字母不是 1 个**: ★**① 方向 (arch 档) = 跟着 W-2 走; ② 型号 (OPN) = W-1c** ★ ⇒ ★**这就是「架构轴 ≠ 型号轴」在 USB 这一格上的具体落法** ★
4. ★**⇒ 若 W-2 拍「补」⇒ 落表器命令已备好 (但那是网表侧, 属另一趟, 本单零写)** ★:
   `python3 state/land_v_values.py --decision V-2=1 --v2-arch 2 --v2-model "<OPN>" --v2-evidence "[官网]" --apply --boss-decision "<老板原话>"`

---

## §2 · ★★落位可行性 (★读板, 零写板★) ★★

### 2-1 · ① 3.0 mm 判据到底按什么量? —— ★★【封装原点距】, 不是焊盘中心距 ★★

★**判据原文 (逐字, `HW/check_netlist_selfconsistency.py`)** ★:

- **L128**: `ESD_MAX_DIST_MM = 3.0`
- **L1218-L1219**: `def _board_ref_xy(path: str) -> dict:` / `"""ref → 封装原点 (x, y)。只读。"""` ★★ ⇒ **它取的是 footprint 的 `(at x y)` 原点** ★★
- **L1446**: `# ---- R9: ESD 必须真的贴到 J_USB_C (★≤3.0mm, 按 ISS-085 规矩; 原 5.0mm 作废★) ----`
- **L1448**: `xy = _board_ref_xy(_path(root, "board"))`
- **L1450**: `a, b = xy["J_USB_C"], xy["D_ESD_USB_D"]`
- **L1452**: `if d > ESD_MAX_DIST_MM:`
- **L1454-L1455**: `f"★R9 未落表: D_ESD_USB_D → J_USB_C 板面距离 = {d:.2f} mm > {ESD_MAX_DIST_MM} mm ⇒ ESD 还是不在接口旁边"`

★**⇒ 判据 = 封装原点 (footprint origin) 到封装原点的欧氏距 ≤ 3.0 mm; ★不是焊盘中心距, 也不是器件外廓边缘距** ★ `[实测]`

### 2-2 · ② 板边与 `J_USB_C` 18 个焊盘的占位 ⇒ 3.0 mm 圆里还剩多少净空

★**实测 (本机 `bash state/pcbnew_py.sh logs/iss307/probe_placement.py`, 零写盘)** ★:

| 项 | 实测值 | 等级 |
|---|---|---|
| 板框 | Edge.Cuts bbox = x **-0.05..160.05** · y **-0.05..100.05** ⇒ 真板边 x 0..160 / y 0..100 (160×100 台架板) | `[实测]` |
| `J_USB_C` | 原点 **(140.00, 5.25)** · 焊盘 **18** 个 (16 SMD + 2 NPTH) | `[实测]` |
| `J_USB_C` courtyard | x **135.16..144.84** · y **-0.53..6.92** (W 9.69 × H 7.45) | `[实测]` |
| `J_USB_C` F.Fab (连接器本体) | x 135.66..144.34 · y **-0.03..6.42** ⇒ ★**本体越过板边 y=0 (板口件, 正常)** ★ | `[实测]` |
| 16 个 SMD 焊盘 | 全部 0.30 × 1.15 mm, y **4.675..5.825**, x 136.10..143.90 (A1/A4/A5/A6/A7/A8/A9/A12/B1/B4/B5/B6/B7/B8/B9/B12) | `[实测]` |
| 2 个 NPTH | (134.22, 2.625) 与 (145.78, 2.625), 0.65 圆 · 钻 0.762 ⇒ ★**距 `J_USB_C` 原点 5.78 mm, 在 3.0 mm 圆外** ★ | `[实测]` |
| 3.0 mm 圆面积 | **28.274 mm²** | `[推算]` (几何) |
| ★**圆内「不在 `J_USB_C` courtyard 里」的净空** ★ | ★**4.662 mm² (只占 16.5%)** ★ = 圆下方 y **6.92..8.25** 的一条缺 (缺高 1.330 mm, @y=6.92 处横向宽 **4.984 mm**, x 137.508..142.492) | `[推算]` (几何) |
| ★**板边 y=0 的影响** ★ | ★**净空区离板边 6.92 mm ⇒ `copper_edge_clearance` 0.5 mm (项目规则) 绰绰有余, 板边不是约束** ★ | `[实测]`+`[推算]` |
| 3.0 mm 圆内的既有铜 | `RAIL_DEMO_5V` 44 项 · `NET_USB_D_N_TYPEC` 34 项 · `NET_USB_D_P_TYPEC` 17 项 · `USB_CC1` 9 项 · `USB_CC2` 1 项 · 2 个未接网焊盘 (A8/B8) · `VIA:RAIL_DEMO_5V` 1 · `VIA:NET_USB_D_N_TYPEC` 1 | `[实测]` |
| ★**周边元件** ★ | ★**`J_USB_C` 原点 12 mm 半径内的其他封装 = 0 个** ★ ⇒ 该片区域只有连接器自己 | `[实测]` |
| 3.0 mm 圆内是否有其他封装 courtyard | ★**全板只有 3 个封装有 F.CrtYd (`CONN_LIGHT` / `J_USB_C` / `U_TEMP`), 前两个离得远** ★ ⇒ ★**新 ESD 的 courtyard 只需与 `J_USB_C` 的 courtyard 不重叠** ★ | `[实测]` |

### 2-3 · ③ + ④ 每条候选封装的落位结论 (★网格扫描, 步长 0.05 mm★)

★**扫描口径 (★DRC 语义★)**: ① R9 圆内 (原点距 ≤ 3.0) ② 新封装 courtyard 与 `J_USB_C` courtyard 不重叠 (`courtyards_overlap = error`, 实测 `.kicad_pro`) ③ courtyard 不与其他封装 courtyard 重叠 ④ 铜到板边 ≥ 0.5 mm. ★**走线可以从器件下方穿过 ⇒ 不拿 courtyard 去卡走线** ★

| 候选封装 | 本体 (mm) | courtyard (推算: 本体 + 0.25/边) | ★**可行原点窗口** ★ | ★**推荐落位** ★ | 距 `J_USB_C` 原点 | ★**窗口内外来网铜 (障碍)** ★ |
|---|---|---|---|---|---|---|
| ★**C1 `TPD2EUSB30DRTR`** (DRT / SOT-3) | 1.00 × 0.80 | 1.50 × 1.30 | x **138.25..141.75** · y **7.65..8.25** (Δx 3.50 / Δy 0.60) · 619 点 | ★**(140.00, 7.65)** ★ | **2.400 mm** | ★**无** (窗口内只有 `NET_USB_D_P_TYPEC` 6 段 = 本来就要改的线) ★ |
| ★**C2 `TPD2E2U06DCKR`** (SC70-3 / DCK) | 2.00 × 1.25 | 2.50 × 1.75 | x **138.55..141.45** · y **7.85..8.25** (Δx 2.90 / Δy 0.40) · 349 点 | ★**(140.00, 7.85)** ★ | **2.600 mm** | ★**无** (窗口内 `NET_USB_D_N_TYPEC` 2 段 + `NET_USB_D_P_TYPEC` 8 段 = 要改的线) ★ |
| ★**C3 `ESD752DCKR`** (SC70-3 / DCK) | 2.00 × 1.25 | 2.50 × 1.75 | 同 C2 | ★**(140.00, 7.85)** ★ | **2.600 mm** | 同 C2 |
| ★**C3' `ESD752DBZR`** (SOT-23-3 / DBZ) | 2.92 × 1.30 | 3.42 × 1.80 | x 138.60..141.40 · y **7.90..8.25** (Δy 0.35) · 290 点 | (140.00, 7.90) | 2.650 mm | ★**`USB_CC1` 2 段侵入** (138.20,6.95)→(137.95,7.20) ⇒ 要么挪 x, 要么改 CC1 走线 ★ |
| ★**C3'' `ESD752DXAR`** (DFN1110-3 / DXA) | 1.10 × 1.00 | 1.60 × 1.50 | x 138.35..141.65 · y **7.75..8.25** (Δy 0.50) · 479 点 | (140.00, 7.75) | 2.500 mm | 无 |
| ★**C4 `CM1218-02S7`** (SC70-3) | 2.00 × 1.25 | 2.50 × 1.75 | 同 C2 | (140.00, 7.85) | 2.600 mm | 同 C2 |
| ★**★反向用例 A★ `USBLC6-2SC6`** (SOT-23-6) | 2.90 × 1.60 | 3.40 × 2.10 | x 138.95..141.05 · y **8.05..8.25** (Δy 仅 **0.20**) · 133 点 | (140.00, 8.05) | 2.800 mm | ★**`USB_CC1` 2 段侵入** ★ ⇒ ★**否掉的理由不是几何, 是 6 脚 (违反台账 B-3 的「3 脚封装」) + BOM 封装体量 (任务书明令「不能是 SOT-23-6 以上的大件」) ★ |
| ★**★反向用例 B★ `D_SMB`** (DO-214AA) | 5.59 × 3.42 | 6.09 × 3.92 | ★**0 个可行原点** ★ | — | — | ★**【放不下】★** (courtyard 高 3.92 ⇒ 最近可行 y0 = 8.880 ⇒ 距接口 3.630 mm > 3.0) ★ |

★**临界高度公式 (★为什么窗口这么窄★)** ★:
`J_USB_C` courtyard 下沿 = 6.92 ⇒ 新封装 courtyard 顶边 ≥ 6.92 ⇒ **y0 ≥ 6.92 + hc/2**; 同时 R9 ⇒ **y0 ≤ 5.25 + 3.00 = 8.25**
⇒ ★**courtyard 高 hc ≤ 2.66 mm 时可行 (hc = 2.66 ⇒ 恰好 y0 = 8.25, 距接口正好 3.000 mm)** ★ `[推算]`

### 2-4 · ★★③ ISS-306 给的落位候选 (137.18, 6.28) —— 复核结论: ★★不通过★ ★★

| 项 | 实测/计算 | 等级 |
|---|---|---|
| 距离 | `hypot(140.00-137.18, 5.25-6.28)` = **3.002216 mm** ⇒ ★**> 3.0 ⇒ R9 依然判红** ★ (★超 **0.0022 mm**★) | `[实测]` (本机 python) |
| courtyard | 该点按 SC70-3 (2.50×1.75) ⇒ courtyard = (135.93, 5.405, 138.43, 7.155) ⇒ ★**与 `J_USB_C` courtyard (135.16,-0.53,144.84,6.92) 重叠 ⇒ DRC `courtyards_overlap` = error** ★ | `[推算]` |
| 出处 | `HANDOFF/2026-11-18_sw-lead_ISS306_G1a两条红溯源.md` L356 自述: 「沿 `J_USB_C`→`D_ESD_USB_D` 直线方向平移至恰好 3.0 mm 处的算术结果」 ★ ⇒ ★**那个"恰好 3.0"的算术没算准** ★ | `[实测]` |
| ★**⇒ 后果** ★ | ★**若板那一趟照 (137.18, 6.28) 钉位 ⇒ R9 不转绿 + courtyard DRC 报错 ⇒ 板改第二次 ⇒ Gerber/投产包/留证链/盖章/发布全作废重做** ★ | `[推算]` |
| ★**本单给的替代值** ★ | ★**(140.00, 7.65) [C1] / (140.00, 7.85) [C2·C3·C4]** ★ —— 两者都同时满足 R9 与 courtyard | `[推算]` |

★**正向对照 (反向用例 ③)**: (140.00, 7.80) → 2.5500 mm ★**PASS** ★; (140.00, 8.30) → 3.0500 mm ★**FAIL** ★; (137.18, 6.60) → 3.1265 mm ★**FAIL** ★

### 2-5 · ★落位的三条硬约束 (★板那一趟必须照做★) ★

1. ★**落位必须走 `state/gen_pcb_netlist_board.py` 的 `PCB_PART_POS` 钉位, 不许手改板坐标** ★ (台账 B-4 定位列已写明) ★
2. ★**D+/D− 的铜要在 ESD 焊盘上「流过」 (flow-through), 不能从旁边绕过** ★ ⇒ ★**窗口内既有的 `NET_USB_D_P_TYPEC` / `NET_USB_D_N_TYPEC` 走线 (实测 6~10 段) 必须重跑** ★ ⇒ ★**这与台账 B-4「挪位置 ⇒ 布线必须重跑 ⇒ 必须与 B-3 同趟」完全一致, 不增加额外趟数** ★
3. ★**换封装 ⇒ land 必须按厂商 land 重画** ★ (ISS-241 已登记: 占位 land = 焊盘 0.6×0.9 @ 2.30 mm 间距, fab bbox 2.70×1.60, 与任何在售 ESD 器件的 land 都不重合) ★

---

## §3 · ★★候选集 (路径甲: 走 3 脚双通道件 / 补 D−) ★★

### 3-0 · 台账 B-3 对候选件的硬要求 (逐字)

★**`HW/SCHEMATIC_LANDING_V1_LANDED.md` L166**: ★**`D_ESD_USB_D` 从 2 脚换 3 脚封装 (pin1=D+ / pin2=D− / pin3=GND)** ★ + R4 判据口径 = ★**「板上挂 D− 两张网的 ESD 位号数 ≥1 且 `D_ESD_USB_D` 焊盘数 = 3」** ★
★**现用件档位 (L934)**: ★**VRWM 5.5V · Cd 0.42pF (单通道) · IEC 61000-4-2 lvl4** ★ ⇒ ★**候选件 VRWM 必须 ≥ 5.5V 档, IEC 口径同档 (lvl4)** ★

### 3-1 · ★★候选总表 (★4 条, 全部官网 datasheet 逐字核过★) ★★

| # | OPN (完整型号串) | 厂商 | 封装 | 脚数/焊盘数 | pin 映射 | VRWM (standoff) | Cd | 钳位 / IEC | 官网直链 | 落位可行性 |
|---|---|---|---|---|---|---|---|---|---|---|
| ★**C1** ★ | **`TPD2EUSB30DRTR`** | TI | **DRT / SOT-9X3 (3 脚 SOT)**, 本体 1.00 × 0.80 mm | **3 / 3** | ★**pin1 = D1+ (D+) · pin2 = D1− (D−) · pin3 = GND** ★ ★**逐字命中 B-3** ★ | **5.5 V** | **0.7 pF** (CIO-GND, DRT, typ) | Vclamp **8 V** @1A; VBR **7 V** min @1mA; ★**IEC 61000-4-2 contact 8000 V (lvl4)** ★; 另带 61000-4-5 surge 5 A | `https://www.ti.com/lit/ds/symlink/tpd2eusb30.pdf` (http=200) | ★**放得下** ★ 窗口 x 138.25..141.75 / y 7.65..8.25 · ★**推荐 (140.00, 7.65) = 2.400 mm** ★ · 窗口内无外来网铜 |
| ★**C2** ★ | **`TPD2E2U06DCKR`** | TI | **DCK / SOT-SC70-3 (3 脚)**, 本体 2.00 × 1.25 mm | **3 / 3** | ★**pin1 = IO1 · pin2 = IO2 · pin3 = GND** ★ ★**逐字命中 B-3** ★ | **5.5 V** | **1.5 pF** typ / **1.9 pF** max | Vclamp **9.7 V** @1A (IO→GND); VBR **6.5 V** min / 8.5 V max; ★**IEC 61000-4-2 level 4: ±25 kV contact / ±30 kV air** ★ | `https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf` (http=200) | ★**放得下** ★ 窗口 x 138.55..141.45 / y 7.85..8.25 · ★**推荐 (140.00, 7.85) = 2.600 mm** ★ |
| ★**C3** ★ | **`ESD752DCKR`** (同族另有 `ESD752DBZR` / `ESD752DXAR`) | TI | **DCK / SOT-SC70-3** (2.00×1.25) · 另 **DBZ / SOT-23-3** (2.92×1.30) · 另 **DXA / DFN1110-3** (1.10×1.00) | **3 / 3** | ★**pin1 = IO · pin2 = IO · pin3 = GND** ★ ★**逐字命中 B-3** ★ | **24 V** (datasheet 逐字: `VRWM Reverse stand-off voltage All Packages –24 … 24 V` ⇒ ±24 V; 汽车 CAN 定位件, 对 3.6V USB 信号无副作用) | **3 pF** typ / **5 pF** max | Vclamp **37 V** (@IPP MAX 8/20 µs; TLP 16 A 时 SOT-23/SC-70 = 35 V, DFN1110-3 = 38 V); VBRF **25.5 V** min (VBRR -25.5 V max); ILEAK 50 nA max @ ±24 V; ★**IEC 61000-4-2 level 4: ±30 kV contact / ±30 kV air** ★; ★**双向** ★ | `https://www.ti.com/lit/ds/symlink/esd752.pdf` (http=200) | ★**放得下** ★ SC70-3 同 C2; DBZ 窗口 y 7.90..8.25 且 **`USB_CC1` 走线侵入**; DXA (DFN1110-3, 1.10×1.00) 窗口 y 7.75..8.25 最干净 |
| ★**C4** ★ | **`CM1218-02S7`** (同族另有 `CM1218-02SO` = SOT23-3) | onsemi | **SC70-3**, 本体 2.00 × 1.25 mm 级 | **3 / 3** | ★**pin1 = CH1 (阴极 = I/O) · pin2 = CH2 (阴极 = I/O) · pin3 = VN (共阳 → 接 GND)** ★ ⇒ ★**I/O 在 1/2、GND 在 3 ⇒ 命中 B-3** ★ | **5.5 V** (VRSO) | **7 pF** typ | 小信号钳位 正 **6.8 V** / 负 **-0.8 V** (⇒ 单向, 共阳到 GND); ★**IEC 61000-4-2 contact ±15 kV** ★ | `https://www.onsemi.com/download/data-sheet/pdf/cm1218-d.pdf` (http=200) | ★**放得下** ★ 同 C2 窗口; ★**代价: Cd 7 pF (是 C1 的 10 倍) + 单向钳位 (负向 -0.8 V, USB 2.0 规格下限 -0.3 V ⇒ 合法工作不误触, 但比双向件余量小)** ★ |

### 3-2 · ★每条候选的官网逐字摘录 (★抓取件全文在 `logs/iss307/evidence/`★) ★★

**C1 · `TPD2EUSB30DRTR`** — `logs/iss307/evidence/A1_TI_TPD2EUSB30.txt` (直链 `https://www.ti.com/lit/ds/symlink/tpd2eusb30.pdf`, http=200, 抓取 2026-11-18 03:18, `pdftotext -layout` 抽取, 文档号 **SLVSAC2G – AUGUST 2010 – REVISED JUNE 2021**)

- ★**§1 Features** ★: `•   IEC 61000-4-2 ESD protection (level 4 contact)` · `•   Low capacitance – DRT: 0.7 pF (typical)` · `•   Dynamic resistance: 0.6 Ω (typical)` · `•   Space-saving DRT, DQA packages` · `•   Flow-through pin mapping`
- ★**§3 Description + Device Information** ★: `The TPD2EUSB30 and TPD2EUSB30A are offered in space saving DRT (1 mm × 1 mm) package.` · `TPD2EUSB30 | SOT (3) | 1.00 mm × 0.80 mm`
- ★**§5 Table 5-1 Pin Functions** ★: `D1+ | 1 | ... High-speed ESD clamp, provides ESD protection to the high-speed differential data lines.` · `D1– | 2 | ...` · `GND | 3 | GND | Ground`
- ★**§6.2 ESD Ratings** ★: `IEC 61000-4-2 Contact Discharge | D+, D– pins | 8000 | V`
- ★**§6.5 Electrical Characteristics** ★: `VRWM | Reverse stand-off voltage (D+ and D- pins) | TPD2EUSB30, TPD4EUSB30 | 5.5 | V` · `Vclamp | Clamp voltage | D+,D– pins to ground, IIO = 1 A | 8 | V` · `Break-down voltage, TPD2EUSB30, TPD4EUSB30 | IIO = 1 mA | 7 | V` · `CIO-IO | Capacitance IO to IO | VIO = 2.5 V; ƒ = 100 kHz | 0.05 | pF` · `CIO-GND | Capacitance IO to GND | D1+, D1-, (DRT) | VIO = 2.5 V; ƒ = 100 kHz | 0.7 | pF`
- ★**§6.3 Recommended Operating Conditions** ★: `Operating Voltage | TPD2EUSB30, TPD4EUSB30 | 0 | 5.5 | V`
- ★**§12 Orderable Addendum** ★: `TPD2EUSB30DRTR | Active | Production | SOT-9X3 (DRT) | 3 | 3000 | LARGE T&R`

**C2 · `TPD2E2U06DCKR`** — `logs/iss307/evidence/A2_TI_TPD2E2U06.txt` (直链 `https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf`, http=200, 文档号 **SLLSEG9C – JUNE 2013 – REVISED DECEMBER 2019**)

- ★**§1 Features** ★: `•   IEC 61000-4-2 Level 4 – ±25 kV (Contact discharge) – ±30 kV (Air-gap discharge)` · `•   IO Capacitance 1.5 pF (Typ)` · `•   DC Breakdown voltage 6.5 V (Min)` · `•   Ultra-Low leakage current 10 nA (Max)`
- ★**§3 Device Information** ★: `TPD2E2U06DRL | SOT (5) | 1.60 mm × 1.20 mm` · `TPD2E2U06DCK | SC70 (3) | 2.0 mm × 1.25 mm`
- ★**§5 Pin Functions** ★: `IO1 | 3 (DRL) | 1 (DCK) | I/O | The IO1 and IO2 pins are an ESD protected channel. Connect these pins to the data line as close to the connector as possible.` · `IO2 | 5 | 2 | I/O` · `GND | 4 | 3 | G | The GND (ground) pin is connected to ground.`
- ★**§6.5 Electrical Characteristics** ★: `VRWM | Reverse stand-off voltage | IIO < 10 µA | 5.5 | V` · `VCLAMP | IO to GND | IPP = 1 A | 9.7 V` · `CL | Line capacitance | f = 1 MHz, VBIAS = 2.5 V | 1.5 | 1.9 | pF` · `ILEAK | Leakage current | VIO = 2.5 V | 1 | 10 | nA`
- ★**§12 Orderable Addendum** ★: `TPD2E2U06DCKR | Active | Production | SC70 (DCK) | 3 | 3000 | LARGE T&R`

**C3 · `ESD752`** — `logs/iss307/evidence/A3_TI_ESD752.txt` (直链 `https://www.ti.com/lit/ds/symlink/esd752.pdf`, http=200, 文档号 **SLVSJ54A – DECEMBER 2025 – REVISED DECEMBER 2025**)

- ★**§1 Features** ★: `•   IEC 61000-4-2 level 4 ESD protection: – ±30kV contact discharge – ±30kV air-gap discharge` · `•   24V working voltage` · `•   Bidirectional ESD protection` · `•   I/O capacitance = 3pF (typical)` · `•   SOT-23 (DBZ), SOT-SC70 (DCK), and DFN1110 (DXA) common packages available`
- ★**§4 Pin Functions** ★: `IO | 1, 2 | I/O | ESD protected IO` · `GND | 3 | G | Connect to ground.`
- ★**§5.5 Electrical Characteristics** ★: `VRWM | Reverse stand-off voltage | All Packages | –24 | 24 | V` · `VBRF | Forward breakdown voltage | IIO = 10mA, IO to GND | All Packages | 25.5 | 35.5 | V` · `VBRR | Reverse breakdown voltage | IIO = –10mA, IO to GND | All Packages | –35.5 | –25.5 | V` · `Clamping voltage | IPP = MAX, tp = 8/20µs, IO to GND | All Packages | 37 | V` · `CL | Line capacitance | VIO = 0V, f = 1MHz, Vpp = 30mV | All Packages | 3 | 5 | pF`
- ★**Package Information** ★: `DBZ (SOT-23, 3) | 2.92mm × 1.30mm` · `DCK (SOT SC-70, 3) | 2.00mm × 1.25mm` · `DXA (DFN1110, 3) | 1.1mm × 1.0mm`
- ★**§12 Orderable Addendum** ★: `ESD752DCKR | Active | Production | SC70 (DCK) | 3 | 3000 | JUMBO T&R` · `ESD752DBZR | ... SOT-23 (DBZ) | 3 | ...` · `ESD752DXAR | ... USON (DXA) | 3 | ...`

**C4 · `CM1218-02S7`** — `logs/iss307/evidence/A4_onsemi_CM1218.txt` (直链 `https://www.onsemi.com/download/data-sheet/pdf/cm1218-d.pdf`, http=200, 文档号 **CM1218/D, February 2011 – Rev. 4**)

- ★**§Description** ★: `All pins of the CM1218 are rated to withstand ±15 kV ESD pulses using the IEC 61000−4−2 contact discharge method.`
- ★**§Features** ★: `• Low I/O Capacitance at 7 pF Typical` · `• Two, Three, Four or Five Channels of ESD Protection` · `• In−system ESD Protection to ±15 kV Contact Discharge, per the IEC 61000−4−2 International Standard`
- ★**PACKAGE / PINOUT DIAGRAMS & PIN DESCRIPTIONS** ★: `CH1 1 / CH2 2 / VN 3` (3-lead SC70 = `CM1218−03` 版图) · `Rxx = Specific Device Code` · `CHx = The Cathode of the Respective TVS Diode, which should be connected to the node requiring transient voltage protection` · `VN = The Anode of the TVS Diodes`
- ★**Table 3 ELECTRICAL OPERATING CHARACTERISTICS** ★: `CIN | Channel Input Capacitance | TA = 25°C, 2.5 VDC, 1 MHz | 7 | pF` · `VRSO | Reverse Stand−off Voltage | IR = 10 mA | 5.5 | V` · `VSIG | Small Signal Clamp Voltage | Positive Clamp | I = 10 mA | 6.8 | V` · `Negative Clamp | I = −10 mA | −0.8 | V` · `VESD | ESD Withstand Voltage | Contact Discharge per IEC 61000−4−2 standard | ±15 | kV`
- ★**ORDERING INFORMATION** ★: `CM1218−02SO | SOT23−3 | 3000/Tape & Reel` · `CM1218−02S7 | SC70−3 | 3000/Tape & Reel`

### 3-3 · ★★[0数据] + 降级方案 (★官网 datasheet 抓不到 ⇒ 不进候选表★) ★★

| 型号 | 状态 | 证据 | 降级方案 |
|---|---|---|---|
| ★**Nexperia `PESD5V0S2BT`** (SOT23 / TO-236AB, 双通道双向) | ★**[0数据]** ★ (★datasheet PDF 抓不到★) | ★**官网产品页 `https://www.nexperia.com/product/PESD5V0S2BT` 本机 web_fetch 成功 (http=200), 逐字: 「Bidirectional ESD protection of two lines」/「Ultra low leakage current: IRM = 5 nA at VRWM = 5 V」/「ESD protection up to 30 kV」/「IEC 61000-4-2; level 4 (ESD)」/「VCL = 14 V at IPPM = 12 A」★ ⇒ ★**厂商 + 通路 + VRWM + IEC 档位 = [官网]; 但 ★pin 映射与 Cd / land 图 = [0数据]** ⇒ ★**按任务书纪律不许留在候选表里当候选** ★ | ★**datasheet 直链 `https://assets.nexperia.com/documents/data-sheet/PESD5V0S2BT.pdf` 本机 curl 返回 **http=403** (三个候选 URL 变体全 403) ⇒ 抓不到原文 ⇒ 不进表** ★ | ★**降级 = 直接用 C1 (`TPD2EUSB30DRTR`): 同一档 VRWM 5.5V, Cd 0.7pF < 0.1pF 之外的所有候选都更低, IEC 同 lvl4, 且 ★**是本表唯一 pin 映射逐字命中的最小件** ★ ⇒ ★**老板若想要 Nexperia 料号, 需要在本机把该 PDF 落到本地缓存后再补证据 (属网表/选型侧另派单, 不是本单能拍的)** ★ |

### 3-4 · ★★候选集的自评对比 (★给老板看的一眼版★) ★★

| 项 | ★**C1 `TPD2EUSB30DRTR`** ★ | C2 `TPD2E2U06DCKR` | C3 `ESD752DCKR` | C4 `CM1218-02S7` |
|---|---|---|---|---|
| pin 映射逐字命中 B-3 | ★**✔ 完全命中** ★ | ✔ 完全命中 | ✔ 完全命中 | ✔ 命中 (I/O=1/2, GND=3) |
| VRWM | 5.5 V ★同现用件档★ | 5.5 V ★同档★ | 24 V (远高于) | 5.5 V ★同档★ |
| Cd | ★**0.7 pF (最低)** ★ | 1.5 pF | 3 pF | 7 pF (最高) |
| IEC 61000-4-2 | ★**lvl4 · contact 8 kV** ★ | ★**lvl4 · ±25 kV contact / ±30 kV air** ★ | ★**lvl4 · ±30 kV contact / ±30 kV air** ★ | ±15 kV contact (onsemi 口径) |
| 极性 | ★**双向 (无正向导通地板)** ★ | 双向 | 双向 | 单向 (负向钳位 -0.8 V) |
| 本体 | ★**1.00 × 0.80 mm (最小)** ★ | 2.00 × 1.25 | 2.00 × 1.25 / 2.92×1.30 / 1.10×1.00 | 2.00 × 1.25 |
| 落位窗口 | ★**最宽 (Δy 0.60) + 无外来网铜** ★ | Δy 0.40 | Δy 0.40 (DBZ 版 Δy 0.35 + CC1 侵入) | Δy 0.40 |
| 厂商/第二来源 | TI | TI | TI | ★**onsemi (第二厂商)** ★ |

---

## §4 · ★★路径乙 (老板拍「不补 D−」) 的代价 + 判据口径改法草案 ★★

### 4-1 · ★★R4 判据原文与「两条红一起红」的机制 (★逐字★) ★★

★**`HW/check_netlist_selfconsistency.py` L1359-L1378** ★:

```python
1359    # ---- R4: USB D− 必须有 ESD ----
1360    dminus = {"USB_D_N_SRC", "NET_USB_D_N_TYPEC"}
1361    hit = []
1362    for ref, info in board.items():
1363        if "ESD" not in ref.upper():
1364            continue
1365        for _num, pnet in info.get("pads_list", []):
1366            if pnet in dminus:
1367                hit.append((ref, pnet))
1368                break
1369    if not hit:
1370        errors.append(
1371            "★R4 未落表: 板上仍然没有任何 ESD 位号挂在 D− 那条网上 "
1372            "(USB_D_N_SRC / NET_USB_D_N_TYPEC) ⇒ D− 仍然裸奔")
1373    if "D_ESD_USB_D" in board:
1374        info = board["D_ESD_USB_D"]
1375        if info["pads"] < 3 and not hit:
1376            errors.append("★R4 未落表: D_ESD_USB_D 仍然只有 2 个焊盘 (D+ + GND) ⇒ 仍不是双通道")
```

★**★机制 (★ISS-306 §1/§5 已 verified 的结论, 本单只引不重做★)**: ★**R4 行2 的判红条件是 `pads < 3 AND not hit` ⇒ ① 落 (D− 上有 ESD ⇒ `hit` 非空) ⇒ 行1 与行2 同时自动转绿; ① 不落 ⇒ `hit` 空 + `D_ESD_USB_D` 仍 2 焊盘 ⇒ 行1 与行2 两条红都亮** ★

### 4-2 · ★★改法草案 (★只写草案, 零改闸; 签字归 main/老板★) ★★

★**改哪个文件哪一行**: ★**`HW/check_netlist_selfconsistency.py` L1373-L1376 (R4 行2 块)** ★ —— ★**只动这一个块, 不动 L1359-L1372 (行1)** ★

★**改完长什么样 (草案 A · ★推荐★ = 把「3 焊盘」这条判据【架构轴条件化】, 而不是删掉它)** ★:

```python
# ★★草案 A (★仅供 main/老板审; 本单零改闸★)★★
#   判据口径: 「D_ESD_USB_D 必须 3 焊盘」只在【架构轴 = 3 脚双通道 (dual3)】时成立;
#   架构轴 = 2 脚单通道 (single2) 时, D− 侧保护由【别的 ESD 位号】承担, 改由行1 单独判。
#   真源 = state/gen_netlist.py 的 D_ESD_USB_D 行数 (2 行 = single2 / 3 行 = dual3),
#          判定逻辑与 state/land_v_values.py v2_read_source() (L888/L890/L892) 同源。
1373    if "D_ESD_USB_D" in board:
1374        info = board["D_ESD_USB_D"]
1375        if info["pads"] < 3 and not hit and _v2_arch_is_dual3(root):   # ★★新增条件★★
1376            errors.append("★R4 未落表: D_ESD_USB_D 仍然只有 2 个焊盘 (D+ + GND) ⇒ 仍不是双通道")
```

★**配套 (草案 A 的必要补充, 否则会出现「行1 不红但行2 也不红 ⇒ D− 无人管」的新盲区)**: ★**行1 的错误串必须挂上「架构轴 = single2 ⇒ D− 侧零保护已被登记」这个事实**, 例如在 L1370-L1372 的串尾追加 `⇒ 【架构轴 single2 ⇒ D− 侧无任何 ESD 位号】`, ★**并把这条缺口登记成 need (归老板/PM), 而不是让它悄悄消失** ★。

★**★谁签字**: ★**main (归 main 的活) + 老板 (因为这是判据口径的放宽, 涉及「D− 零保护」这个产品级取舍) ★ ⇒ ★**本单只交草案, 不自签, 不改判据代码** ★**

★**★不许的做法 (★明确写死, 免得被当成「偷偷放宽」★)**: ★
1. ★**不许把 `if info["pads"] < 3 and not hit:` 直接删掉** ★ (⇒ 行2 永远不判红 = 判据静默失效)
2. ★**不许把 `dminus` 集合缩小 / 改网名** ★ (⇒ D− 换张网名就绕过判据)
3. ★**不许把 `ESD_MAX_DIST_MM` 或 R4 的阈值改成更宽松的值** ★
4. ★**不许在董事会层把「D− 零保护」登记成「已解决」** ★ ⇒ ★**它只能被登记成【老板显式承担的缺口】** ★

### 4-3 · ★★路径乙的量化代价 (★台账理由逐字 + 本单的量化★) ★★

★**台账 L168 (B-5) 的理由逐字**: ★**「R4 判据: D− 侧必须有 ESD ⇒ **Type-C 是日常插拔口, 这是 4 条里唯一的"用了就可能坏"**」** ★

| 代价项 | ★**路径甲 (补 D−, 3 脚双通道)** ★ | ★**路径乙 (不补 D−)** ★ |
|---|---|---|
| 板面改动量 | ★**1 个封装 (D_ESD_USB_D): 2 脚 → 3 脚, land 重画 + 位置 (94.95, 21.80) → (140.00, 7.65~7.85) (直线挪 47.99 mm, R9 现值实测)** ★ | ★**1 个封装: land 重画 + 同样挪位 (B-4 仍要做) ⇒ 改板量与路径甲几乎相同** ★ |
| 布线重跑量 | ★**D+ 与 D− 两条网: 窗口内既有走线实测 `NET_USB_D_P_TYPEC` 6~10 段 + `NET_USB_D_N_TYPEC` 2~4 段 要重跑 (flow-through 过 ESD 焊盘)** ★ | ★**只有 D+ 一条网要重跑 (D− 不经 ESD) ⇒ 比路径甲少约 1/3** ★ |
| BOM 变化 | ★**1 行 (`D_ESD_USB_D` 的 value/opn) + 脚表 +1 行 (2 脚 → 3 脚) ⇒ BOM 行数不变** ★ | ★**0 行 (`D_ESD_USB_D` 已是 `TPD1E05U06DPYR`, 台账 L934)** ★ |
| 网表变化 | ★**+1 行 (D− 行), 走 `land_v_values.py --v2-arch 2` (工具已就位, 行号漂移 L418/L174 已写死) ⇒ 属网表侧另一趟** ★ | ★**0 行** ★ |
| ★**闸** ★ | ★**R4 行1 + 行2 自动转绿 (零修闸成本) + R9 按 §2-3 落位即转绿** ★ | ★**★R4 行1 + 行2 两条红都亮 ⇒ 必须显式改判据 (草案 A) ⇒ 判据口径被放宽, 且新增一个「D− 无人管」的盲区风险** ★ |
| ★**功能代价 (照抄台账口径 + 量化)** ★ | ★**D+ 与 D− 同时受保护 ⇒ Type-C 插拔浪涌不直达 SoM 的 USB PHY** ★ | ★**D− 侧零保护 ⇒ Type-C 是日常插拔口 ⇒ 一次插拔的接触浪涌即可直接打到 SoM USB PHY ⇒ 现场故障模式 = 整机 USB 链路失效 (语音/显示/固件升级全断) ⇒ 故障率随插拔次数线性累积, 且是【用了就可能坏】的那一类 (台账 L168 原话) ⇒ ★**代价落在售后/返修, 不是落在 BOM 行数上** ★ |
| ★**评审口径** ★ | ★**与 R4 判据本身 (双通道口径) 一致 ⇒ 判据与实物同口径** ★ | ★**判据与实物长期打架 ⇒ 必须靠改判据维持 ⇒ 「绿灯 = 符合一个我们自己改过的口径」** ★ |

---

## §5 · ★★老板一页纸 (★need key + 决策码 · 不回裸字母★) ★★

> ★**need key**: `boss_esd_model_axis_pending_20261117` (★同一个 key 下 2 个问题, 分别登记在 pm.yaml / STATE.yaml, `since: 2026-11-17`, 无 `decided_at` ⇒ 仍未拍★)
> ★**回法**: ★**回一行即可 (三段用空格隔开)** ★ ★**「建议默认值」≠「已决定」★ ★**本单不代拍★ ★

### 5-1 · ★决策项 1 (need key 第②问 = `W-2`) ★

| 项 | 内容 |
|---|---|
| ★**need key + 决策码** ★ | **`boss_esd_model_axis_pending_20261117` (第②问) → `W-2`** ★ |
| ★**要老板拍什么** ★ | ★**USB D− 侧补不补 ESD** (现状实测: `USB_D_N_SRC` / `NET_USB_D_N_TYPEC` 上的 ESD 位号数 = **0** ⇒ D− 裸奔) ★ |
| ★**选项** ★ | ★**① 补** (= 走 3 脚双通道件, 架构档 arch=2) ★ / ★**② 不补** (= 维持 2 脚单通道, 架构档 arch=1, R4 判据口径必须显式改, 见 §4-2 草案 A) ★ |
| ★**每项量化代价** ★ | ★**① 补**: 板面改 1 个封装 + land 重画 + 挪 47.99 mm; 布线重跑 D+/D− 两条 (窗口内 8~14 段实测); BOM 改 1 行 + 脚表 +1 行; 网表 +1 行 (另一趟); ★**闸零修闸成本, R4 两红自动转绿** ★ · ★**② 不补**: 板面改 1 个封装 + land 重画 + 同样挪 47.99 mm; 布线只重跑 D+ (少约 1/3); BOM 0 行; 网表 0 行; ★**闸: R4 两条红都亮 ⇒ 必须改判据口径 + 新增「D− 无人管」盲区; 功能代价 = D− 零保护 (台账 L168: Type-C 是 4 条里唯一的『用了就可能坏』) ⇒ 现场故障 = 整机 USB 链路失效** ★ |
| ★**建议默认值 (★建议, 不是决定★)** ★ | ★**① 补** ★ —— 理由: ① R4 判据本身就是双通道口径, 不补 = 判据与实物长期打架; ② 台账 L168 的理由 (Type-C = 唯一「用了就可能坏」的接口); ③ 补的板面改动量与不补几乎相同 (B-4 挪位在两条路里都要做) ⇒ 补的增量代价只有「多一条网的重跑 + 多一行 BOM」, 而不补的代价是判据口径被放宽 + 功能缺口; ★**代价最小档 = 只给两条高速对补负线的 D+/D− 这两条 (ISS-241 G-3/G-4 缺口就是这个口径)** ★ |
| ★**不拍的后果** ★ | ★**板那一趟的 S4/B-5 无法开工; G1a-4 (R4) 永远红; 板 md5 要变两次 ⇒ Gerber / 投产包 / 留证链 / 盖章 / 发布全作废重做 (台账 §4 的 2-4 周 + ¥4-8K 量级)** ★ |

### 5-2 · ★决策项 2 (need key 第①问 = `W-1b` 架构档 + `W-1c` 真 OPN) ★

| 项 | 内容 |
|---|---|
| ★**need key + 决策码** ★ | **`boss_esd_model_axis_pending_20261117` (第①问) → `W-1b` (架构档) + `W-1c` (真 OPN)** ★ |
| ★**依赖关系 (★本单给的最省事结论★)** ★ | ★**`W-1b` 由 `W-2` 唯一确定** ★ ⇒ ★**W-2 = 补 ⇒ `W-1b = 2` (3 脚双通道, arch=dual3) ; W-2 = 不补 ⇒ `W-1b = 1` (2 脚单通道, arch=single2, OPN 已经是 `TPD1E05U06DPYR`, 不用再拍)** ★ ⇒ ★**⇒ 老板实际只需拍 2 个字母: `W-2` + `W-1c`** ★ |
| ★**要老板拍什么** ★ | ★**`D_ESD_USB_D` 的真 OPN 型号 (3 脚双通道件选哪一颗)** ★ |
| ★**选项 (≤3, ★这里给 4 个是因为 4 个都能落位, 由老板按供应链偏好选★)** ★ | ★**`W-1c = C1`** (`TPD2EUSB30DRTR` · TI · DRT SOT-3 3 脚 · 1.00×0.80 mm · Cd 0.7 pF · VRWM 5.5 V · IEC lvl4) / ★**`C2`** (`TPD2E2U06DCKR` · TI · SC70-3 · Cd 1.5 pF · VRWM 5.5 V · IEC lvl4 ±25 kV) / ★**`C3`** (`ESD752DCKR`/`DBZR`/`DXAR` · TI · SC70-3/SOT-23-3/DFN1110-3 · Cd 3 pF · VRWM 24 V · IEC lvl4 ±30 kV) / ★**`C4`** (`CM1218-02S7` · onsemi · SC70-3 · Cd 7 pF · VRWM 5.5 V · ±15 kV contact · 单向) ★ |
| ★**每项量化代价** ★ | ★**C1**: 板面改 1 封装 + land 重画 (占位 2.30 mm 间距 → DRT 0.5 mm 级 pitch) + 挪位 (140.00, 7.65) · 布线重跑 D+/D− (窗口内 6 段 D+ 实测) · BOM 1 行 · 网表 +1 行 (另一趟) · ★**落位窗口最宽 + 窗口内无外来网铜** ★ · Cd 最低 (0.7 pF) · pin 映射逐字命中 · ★**但只有 TI 一家 ⇒ 无第二来源** ★ <br> ★**C2**: 同 C1 的量 · 落位 (140.00, 7.85) · Cd 1.5 pF (USB 2.0 12 Mbps 够用) · IEC ±25 kV contact 比 C1 的 8 kV 更强 · 窗口内无外来网铜 · ★**同样只有 TI** ★ <br> ★**C3**: 同上 + Cd 3 pF (C1 的 4.3 倍, 边沿变慢) · VRWM 24 V (对 3.6 V USB 信号无副作用, 但属汽车 CAN 定位件, 需确认不是「拿错定位」) · DBZ 版窗口窄且 `USB_CC1` 走线侵入, DXA 版 (DFN1110-3, 1.10×1.00 mm) 最干净 · ★**同样只有 TI** ★ <br> ★**C4**: 同上 · Cd **7 pF** (C1 的 10 倍) · 单向钳位 (负向 -0.8 V) · ★**★唯一第二厂商 (onsemi) ⇒ 供应链上唯一能拿双来源的选项** ★ |
| ★**建议默认值 (★建议, 不是决定★)** ★ | ★**`W-1c = C1`** ★ —— 理由: ① ★**唯一「pin 映射逐字等于台账 B-3 (pin1=D+ / pin2=D− / pin3=GND)」+ 「VRWM 与现用件同档 5.5 V」+ 「Cd 最低 0.7 pF」+ 「本体最小 1.00×0.80 mm」四项全中** ★; ② 落位窗口最宽 (Δy 0.60) 且窗口内无外来网铜 ⇒ 板那一趟改动量最小; ③ TI 官网直链与 orderable 表都在本机抓得到 (http=200), 落表证据链完整. ★**若老板更看重供应链双来源 ⇒ `C4` 是表里唯一的第二厂商, 但 Cd 7 pF 与单向钳位要一并接受** ★ |
| ★**不拍的后果** ★ | ★**板那一趟的 S4/B-3 换不了封装 ⇒ 板又改一次; BOM 的 OPN 列写不出主板 BOM; 即使 W-2 拍了「补」, 落表器 `--v2-model=` 拿不到型号 ⇒ `land_v_values.py` 会按 ISS-260 的设计【拒绝落】(型号轴是占位串就拒绝, 不许把占位串当「落了」)⇒ 网表侧也走不下去** ★ |

### 5-3 · ★★给老板的一行回法 (★可直接复制★) ★★

```
need key: boss_esd_model_axis_pending_20261117
W-2  = 补 | 不补
W-1b = 2            (★由 W-2 唯一确定: 补⇒2 / 不补⇒1; 可不写★)
W-1c = C1 | C2 | C3 | C4
```

★**建议默认值 (★只作参考, 不代拍★)**: `W-2 = 补` · `W-1b = 2` · `W-1c = C1` ★

---

## §6 · ★反向用例 (★≥3 条 · 每条贴 rc / 读数★) ★

| # | 用例 | 做法 | 结果 (实测) | 判定 |
|---|---|---|---|---|
| ★**①** ★ | ★**故意写一个错 OPN ⇒ 官网直链打不开 ⇒ 该条必须落 `[0数据]` 而不是留在表里当候选** ★ | curl 一个不存在的 OPN 的 TI 直链 | `http=404  https://www.ti.com/lit/ds/symlink/tpd2eusb31.pdf` · `http=404  https://www.ti.com/lit/ds/symlink/tpd2e2u07.pdf` (对照组: `tpd2eusb30.pdf` → **http=200**, `esd752.pdf` → **http=200**) | ★**通过** ★ ⇒ 错 OPN 的直链打不开 ⇒ 不许进候选表; ★**Nexperia `PESD5V0S2BT` 因为 datasheet PDF 本机 403 ⇒ 已在 §3-3 落 `[0数据]` + 降级方案, 未留在候选表** ★ |
| ★**②** ★ | ★**拿一条封装明显过大的候选走一遍落位计算 ⇒ 必须被自己否掉** ★ | `D_SMB` (DO-214AA, 本体 5.59×3.42, courtyard 6.09×3.92) 走同一套扫描 | ★**可行原点数 = 0 ⇒ 【放不下】** ★ (临界高 hc ≤ 2.66 mm, 该件 hc = 3.92 ⇒ 最近可行 y0 = 8.880 ⇒ 距接口 3.630 mm > 3.0) | ★**通过** ★ |
| ★**③** ★ | ★**把某条候选的落位距离算成 >3.0 mm ⇒ 必须被标「放不下」⇒ 再给一条 ≤3.0 mm 的做正向对照** ★ | 同距离函数逐点算 | ★**(137.18, 6.28) → 3.0022 mm ⇒ FAIL** ★ · (137.18, 6.60) → 3.1265 mm ⇒ FAIL · (140.00, 8.30) → 3.0500 mm ⇒ FAIL · ★**(140.00, 7.80) → 2.5500 mm ⇒ PASS** ★ | ★**通过** ★ ★(★并且这条把 ISS-306 给的 (137.18, 6.28) 判成了 FAIL★)★ |
| ★**④ (附加)** ★ | ★**判据口径是否真的按「原点距」而不是「焊盘中心距」** ★ | 读 `HW/check_netlist_selfconsistency.py` L1218-L1219 + L1448-L1452 | `_board_ref_xy` docstring 逐字 = `"""ref → 封装原点 (x, y)。只读。"""`; R9 用 `math.hypot` 算两个 **原点** | ★**通过** ★ ⇒ 落位候选坐标必须按 **原点** 设计, 不是按焊盘 ★ |

---

## §7 · 边界自证 (逐条)

| 项 | 做了 / 没做 | 证据 |
|---|---|---|
| ★**零写板** ★ | ✔ 没写 | 板 md5 跑前跑后各一次 = `611b869e13518c3c023fb178f91a0075` · mtime = `2026-11-06 07:07:17` (见交卷单 §B6) |
| ★**零落表 (网表/脚表/BOM)** ★ | ✔ 没改 | 三份 md5 跑前跑后逐字节不变 |
| ★**零改闸** ★ | ✔ 只读 | `HW/check_netlist_selfconsistency.py` / `state/check_stage_g1a.py` / `state/gate_check.py` 只 grep / `sed -n` 读, 未编辑 |
| ★**零改网表** ★ | ✔ 没改 | `HW/netlist_v1.net` md5 不变 |
| ★**零改落表台账** ★ | ✔ 没改 | `HW/SCHEMATIC_LANDING_V1_LANDED.md` 未动 |
| ★**零改决策页** ★ | ✔ 没改 | `DECISION_PENDING_2026-11-16.md` / `DECISION_INDEX_2026-11-18.md` 未动 |
| ★**零外发** ★ | ✔ 没发 | 只做本机 `curl` / `web_fetch` / `web_search` 读官网; **未发邮件、未询价、未联系厂商** (老板 2026-11-11 19:31 + 2026-11-12 02:02) |
| ★**不替老板拍板** ★ | ✔ | 本页只给「建议默认值」, 全文无「已决定 / 已拍 / 就选 X」 |
| ★**不自签 issue_log** ★ | ✔ 没签 | 只写 `state/fragments/hw.yaml` (走 `state/frag_write.py --agent hw-lead`) |
| ★**没碰别人的分片** ★ | ✔ | `mech.yaml` / `sw.yaml` / `pm.yaml` 一个字节没碰 |
| ★**只写 §5 允许的 4 处路径** ★ | ✔ | `HW/ESD_DUAL_CHANNEL_CANDIDATES.md` · `HANDOFF/2026-11-18_hw-lead_ISS307_ESD选型候选集.md` · `logs/iss307/**` · `state/fragments/hw.yaml` |
