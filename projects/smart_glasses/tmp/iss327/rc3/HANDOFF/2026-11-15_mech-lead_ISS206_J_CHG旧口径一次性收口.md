# ISS-206 交接单 — 结构侧 J_CHG 旧口径一次性收口 (mech-lead · 2026-11-15)

> **交卷人**: 结构总工 (`mech-lead`) · **日期**: 2026-11-15 20:5x · **任务书**: `state/tasks/advance_iss206.md`
> ★ 本单 = ISS-202 / ISS-203 登记的 8 条 need 被 main 逐条裁完之后的一次性执行单; **裁决已在 brief 里裁完 ⇒ 本单不用等下一轮**。
> ★ **本次是第 2 次派活**: 第 1 次 (2026-11-12 03:2x) 会话 status=failed ⇒ **MECH 文档侧已改 (mtime 03:32-03:42) 但分片一个字没落 ⇒ 交卷没人落账**。本单 = **逐项实测复核 + 补齐落账**, 不是重做一遍。

---

## B1 结论摘要 (一句话)

★ **结构侧 J_CHG 已无第 3 套 pin map**: 脚本活口径 `RECOMMENDED_PINS["J_CHG"]` = **10**; 11 处文档旧口径 + §5.2 F-3 + 3 份文档全部按 **1×10p@0.5mm** 逐脚真源改齐; 检修口文档 15mm 口径 → **60×30 现行口径**; 板厚 4 层 0.80 → **6 层 1.00**; **裁 6 (板长 claim) 与裁 8 (逃线带/孔位) 判定为「不属本单数值订正」⇒ 只报不改 + 登记 need**。

| 裁 | 事项 | 结果 | 落点 |
|---|---|---|---|
| 裁 1 | `hinge_usb_check.py` `RECOMMENDED_PINS["J_CHG"]` 8→10 + 注释去 SYS/VBUS_DET/BAT_DET 跨铰链 | ✅ 已改 | `MECH/hinge_usb_check.py` |
| 裁 2 | `USB_HINGE_STRUCTURE.md` 11 处 + §5.2 F-3 + §3.2b/§5.3 C-4/§7/§9 堆叠数 | ✅ 已改 | `MECH/USB_HINGE_STRUCTURE.md` |
| 裁 3 | `FPC_FAB_NOTES.md` N-6/I-5 + `RELIABILITY_TEST_PLAN.md` R10/§T-14/T-14 判据/K-11/K-12 + `STRUCT_REVIEW_ISS065.md` R3 | ✅ 已改 (含 **T-14 判据本身**) | 3 份文档 |
| 裁 4 | `SERVICE_PORT_ISS092.md` 15mm → 60×30 (V PCB 段 21.00→36.00, 余 +17.00→+2.00, §1.6.2 三条余量重算) | ✅ 已改 | `MECH/SERVICE_PORT_ISS092.md` |
| 裁 5 | `service_port_check.py` `pcb_thk` 0.80→1.00 | ✅ 已改 | `MECH/service_port_check.py` |
| 裁 6 | 分片 `mainboard_len_carrier=69mm` / `mainboard_len_direct=76mm` | ★**只报不改** (见 B5 U-1) | `state/fragments/mech.yaml` (need) |
| 裁 7 | `service_port_check.py` 夹具基准 `p2_y/s2_y/jd_y0` | ★**数字不许动 ⇒ 只加注记** (已加) | `MECH/service_port_check.py` |
| 裁 8 | `hw_cross_review_check.py` `soc_escape_x` / `hole_x` | ★**只报不改** (见 B5 U-2) | `state/fragments/mech.yaml` (need) |

### ★ 我自己逐脚复算的 pin map (不照抄题单) —— 与 brief 一致, 但依据是我自己数的

**[实测]** 逐行扫 `HW/netlist_v1.csv` 的 **逐脚 net 行** (不看 note 列文字), 命中 9 个 J_CHG 脚 + 1 个 NC 脚:

| pin | 网表逐脚行 | net | 证据行号 | 跨铰链? |
|---|---|---|---|---|
| 1 | `P1,BAT_CHG,J_CHG pin1,...` / `P10,BAT_CHG,U_CHG pin14,J_CHG pin1` | `BAT_CHG` | 15-16, 76, 416, 497 | ✔ 载流 (双 pin 并联) |
| 2 | `P1,BAT_CHG,J_CHG pin2,J_CHG pin1` | `BAT_CHG` | 16 | ✔ 载流 |
| 3 | `P1,GND,J_CHG pin3,J_CHG pin4` | `GND` | 22 | ✔ 回流 |
| 4 | `P1,GND,J_CHG pin4,GND` | `GND` | 23 | ✔ 回流 |
| 5 | `P2,CHG_STAT,J_CHG pin5,NET_CHG_STAT` / `P10,U_CHG pin4` | `CHG_STAT` | 189, 482 | ✔ 开漏 |
| 6 | `P1,PWR_GOOD,Q_PG,J_CHG pin6` / `P10,U_CHG pin3` | `PWR_GOOD` | 61, 192, 481 | ✔ 开漏 |
| 7 | `P9,NC,J_CHG pin7,NC` (DNP) | `NC` | 433 | ✘ **不接** (VBUS_DET 2026-11-04 起改主板本地分压) |
| 8 | `P1,TS_BAT,J_CHG pin8,R_NTC_BAT` / `P10,U_CHG pin11` | `TS_BAT` | 42, 478 | ✔ 高阻 (源阻抗 3-4 kΩ) |
| 9 | `P1,HINGE_RSV,J_CHG pin9` (DNP) | `HINGE_RSV` | 20 | ✘ 预留 |
| 10 | `P1,HINGE_RSV,J_CHG pin10` (DNP) | `HINGE_RSV` | 21 | ✘ 预留 |

⇒ **我的实算 = brief 的真源 = `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 定版) = 三方一致**。
★ **一条容易踩的坑已按 brief 处理**: 废的是「`VBUS_DET` 跨铰链走 J_CHG pin7/pin8」这句话, **不是 `VBUS_DET` 这个网** ⇒ **[实测]** `grep -c VBUS_DET HW/netlist_v1.csv` = **9 处仍在** (网表 38/412/433/434-439) ⇒ 主板本地分压描述**一处没删**。

---

## B2 验收标准自评 (逐条 通过/不通过/未验)

| # | 验收标准 | 自评 | 依据 |
|---|---|---|---|
| 1 | `RECOMMENDED_PINS["J_CHG"]` = 10, 注释里不再有 SYS / VBUS_DET / BAT_DET 跨铰链 | ✅ **通过** | `MECH/hinge_usb_check.py:77-88`; 脚本跑 rc=0 |
| 2 | `USB_HINGE_STRUCTURE.md` 11 处 + §5.2 F-3 全部 10p 口径, 五处堆叠数一致 | ✅ **通过** | 逐条 grep 见 B6 命令 4 |
| 3 | `FPC_FAB_NOTES` N-6/I-5 + `RELIABILITY_TEST_PLAN` R10/T-14/K-11/K-12 + `STRUCT_REVIEW_ISS065` R3 改齐 | ✅ **通过** | 逐行读回 |
| 4 | **T-14 判据本身**改成 10p 真实反插后果 | ✅ **通过** | `RELIABILITY_TEST_PLAN.md:583` |
| 5 | `SERVICE_PORT_ISS092.md` 正文 15mm → 60×30 口径 | ✅ **通过** | `SERVICE_PORT_ISS092.md:18,191-201` |
| 6 | `service_port_check.py` `pcb_thk` = 1.00, H 链 4.40 / 余 +2.90 | ✅ **通过** | 脚本输出 §1/§5.2 |
| 7 | 裁 6 两条板长 claim | ✅ **通过 (按闸只报不改)** | 依据见 B5 U-1 |
| 8 | 裁 7 夹具基准数字不许动 | ✅ **通过** | `p2_y=7.50 / s2_y=12.50 / jd_y0=9.50` 一字未动, 只加了作废注记 |
| 9 | 裁 8 `soc_escape_x` / `hole_x` 不许动 | ✅ **通过** | `hw_cross_review_check.py:63-64` = (20.20, 31.80) / (5.00, 15.00, 55.00), 一字未动 |
| 10 | **判据阈值一个没松** (`judge/CRIT 0.60` / `cav_v 38.00` / `duct_v 6.00`) | ✅ **通过** | 本单没碰任何阈值; PASS/FAIL 变化只因真源变 |
| 11 | `HW/**` 一个字没动 (网表 md5 一字未变) | ✅ **通过** | md5 实测见 B6 命令 5 |
| 12 | 不外发任何邮件/询价/采购 | ✅ **通过** | 本单零外发; 全部靠自查网表 + 本地脚本 |
| 13 | 实物验证 | ⛔ **未验 (设计态几何, [实测]=0 条)** | 0 件打印 / 0 台样机 ⇒ 全部数是 [推算] |

---

## B3 证据分级

| 项 | 级别 | 说明 |
|---|---|---|
| J_CHG 逐脚 pin map (10 脚) | **[实测]** | 逐行扫 `HW/netlist_v1.csv` 逐脚 net 行 (9 脚命中 + pin7 NC) + `grep -c VBUS_DET` = 9 |
| 收敛版堆叠 **25.0 mm** / 声明版 **31.50 mm** / 触点区 **21.0 mm** | **[实测]** | `python3 MECH/hinge_usb_check.py` §2 实跑 (脚数 10p ⇒ 50 脚 @0.5) |
| 检修口 V PCB 段 **需求 36.00 / 余 +2.00 / 最坏 +1.40** · H PCB 段 **需求 4.40 / 余 +2.90** | **[实测]** | `python3 MECH/service_port_check.py` 实跑 (54/54, FAIL 0) |
| 板厚 **1.00 mm (6 层)** / 板长 **60.00** / 板宽 **30.00** | **[官方]** | `MECH/BOARD_GEOM_30MM.md` §1 (10-28 项目总工裁 + 老板 10-29 19:16) |
| 反插位型后果 (断路 + 两条短) | **[推算]** | 按 10p 逐脚 map 算 pin i ↔ pin 11-i; 未实物反插验证 |
| 夹具基准迁移后的 J_DEBUG 阵列 Y | **[0数据]** | 现行套 A 的 J_DEBUG 阵列 Y **尚未定** ⇒ `SERVICE_PORT_ISS092.md:88` 已标"须重定"; 迁移随整链重出 |
| 整机外形干涉 / 波导耦入容差 | **[0数据]** | 波导未选型 ⇒ 不在本单范围 |

★ **证据分级纪律**: 查不到的一律写 `[0数据]` + 降级方案, **零编造**。

---

## B4 接口取值声明 (interface_claims)

★ **本单写进分片 `state/fragments/mech.yaml` 的取值** (走 `state/frag_write.py` 原子写, 没碰别人的 key):

| key | value | note 摘要 | 依据 |
|---|---|---|---|
| `mainboard_len_carrier` | **`69mm` (未改)** | ★**只报不改**: 这是 ISS-084/SOC_CARRIER_EVAL 的 **B 档 (BTB 载板化) 方案**板长 | 见 B5 U-1 |
| `mainboard_len_direct` | **`76mm` (未改)** | ★**只报不改**: 这是 **A 档 (直接焊) 方案**板长 | 见 B5 U-1 |
| `mech_j_chg_pins` | `10p@0.5mm` (既有, 未改) | 逐脚 map 已与网表真源逐脚一致 | `HW/netlist_v1.csv` |
| `mech_hinge_stack_fixed_mm` | **`24.00` (未改 ★)** | ★**文档 §9 已改 25.00, 分片仍 24.00** ⇒ **本单边界不许改 (只有裁 6 那两条 claim 可写)** ⇒ 报 main | 见 B5 U-3 |

★ **本单没有新增任何 claim 值** (除裁 6 两条的 note 澄清), **没有改任何别人的 key**, **没有删任何条目**。

---

## B5 未决项与卡点 (需要谁回答什么)

| # | 未决项 | 需要谁 | 状态 |
|---|---|---|---|
| **U-1** | ★**裁 6 闸命中 ⇒ 两条板长 claim 不改**: `mainboard_len_carrier=69mm` / `mainboard_len_direct=76mm` 描述的是 **`MECH/SOC_CARRIER_EVAL.md` 的 A 档 (直接焊, 76×12=912 mm²) 与 B 档 (BTB 载板, 69×12) 两个互斥方案**, 不是同一块板的两个口径 ⇒ **数值订正 = 方案取舍 = 老板级**。⇒ 本单**只报不改**, 已登记 need 给 main | **main / boss** | 卡住 |
| **U-2** | ★**裁 8 只报不改**: `MECH/hw_cross_review_check.py` 的 `soc_escape_x=(20.20, 31.80)` / `hole_x=(5.00, 15.00, 55.00)` 是**旧 SoC (RK3576) 的逃线带与孔位**; 主控已换 RK3572 ⇒ 逃线带本身要重算 ⇒ 属整链重出的一步, 且老板 10-29 口径「PCB 布线/布局类一律排队等原理图定稿」⇒ **本单不碰**, 已登记 need | **main** | 卡住 |
| **U-3** | ★**分片 vs 文档的堆叠数差**: `MECH/USB_HINGE_STRUCTURE.md` §9 已按裁 2 改成 `mech_hinge_stack_fixed_mm = 25.00 (16p/20p/4p/10p)`, 但**分片 claim 仍是 `24.00` + note 里仍写 `(16p/20p/4p/8p @0.5)`** ⇒ ★**本单边界只许写「裁 6 那两条 claim」+ need/artifact ⇒ 我不许改它** ⇒ 报 main (建议: 改成 `25.00` + note 换 10p 口径; 该 claim 已标"仅供追溯 · 现行板无跨铰链", 影响面 = 追溯口径) | **main** | 卡住 |
| **U-4** | **ISS-202 / ISS-203 的 8 条 need 仍挂在 `to: main` 未闭**: 裁决已在 brief 里裁完且本单已执行, 但 **`state/fragments/pm.yaml` 里没有对应 key 的 answer** ⇒ merge.py 的闭单口径 (作者 = `to` = main) 认不到 ⇒ **Q4 需求闭环率**上这 8 条仍算未回音 ⇒ 要 main 落 answer | **main** | 卡住 |
| **U-5** | **现行套 A 的 J_DEBUG 焊盘阵列 Y 未定** (30 mm 板上) ⇒ `service_port_check.py` 检查 7.4/7.5 仍在用**已作废的**旧夹具基准 `p2_y=7.50 / s2_y=12.50 / jd_y0=9.50` (只加了注记, 数字未动 ⇒ 不会假红) ⇒ 真正迁移留整链重出 | **hw-lead / main** | 排队 |
| **U-6** | `HW/**` 侧仍带旧口径 4 处 (网表 38/412 行 note 列 · `POWER_SHUTDOWN_V3.md:129` · `J_CHG_SELECTION.md` C-8/§0-5 · `CHARGE_BOARD_SPEC.md` §5.1 表 + §7 P10 镜像块) ⇒ **已由既有 need `iss200_hw_residual_old_pinmap` 覆盖** (转 ISS-199), **本单不重复登记** | **hw-lead (经 main)** | 已登记 |

---

## B6 自证复现命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/hinge_usb_check.py          # rc=0, [FAIL] 0, 收敛版 25.0mm (16p/20p/4p/10p)
python3 MECH/service_port_check.py       # rc=0, 54/54 一致, FAIL 0 (H PCB 4.40/余+2.90; V PCB 36.00/余+2.00/最坏+1.40)
python3 MECH/hw_cross_review_check.py    # rc=0, PASS 14 / FAIL 17 / 条件 8 / 说明 15 (裁 8 不许动 ⇒ 分布未因本单变红)
grep -rn '8p@0.5\|8p @0.5\|1×6@1.27\|1×6 1.27' MECH/ | head -40   # 期望: 只剩历史脚本里的旧值探针/归档 apply 脚本
md5sum HW/netlist_v1.csv HW/PCB/demo_mainboard.kicad_pcb
# 期望 c78f991283cc82d56c8e3dd31657c785 / 611b869e13518c3c023fb178f91a0075 (一字未变)
python3 state/merge.py ; echo "rc=$?"        # rc=0
python3 state/gate_check.py ; echo "rc=$?"   # rc=0, 【Q1】18/18
```

### ★ 裁 1 判据要求的「改前 / 改后两套跑法」

★ **改前** = 只把 `RECOMMENDED_PINS["J_CHG"]` 这**一个变量**回退成 8 (其余一律不动), 用 `state/_huc_before_iss206.py` 载入同一脚本再跑 ⇒ **隔离出"脚数本身"这一个因子**:

```
[2] 铰链区几何账
    垂直(高度)占位 声明版     = 31.5 mm  (网表声明 31p/22p/0p/10p 全 0.5mm) vs 镜脚净高 38.0 mm
    垂直(高度)占位 收敛版     = 24.0 mm  (16p/20p/4p/8p 全 0.5mm) vs 镜脚净高 38.0 mm
[FAIL]
  · 正文里找不到脚本算出的关键数 24.0 (文档与脚本不一致)
结论: ❌ 不自洽 (修完再交)          rc=1
```

★ **改后** (现行文件):

```
[2] 铰链区几何账
    垂直(高度)占位 声明版     = 31.5 mm  (网表声明 31p/22p/0p/10p 全 0.5mm) vs 镜脚净高 38.0 mm
    垂直(高度)占位 收敛版     = 25.0 mm  (16p/20p/4p/10p 全 0.5mm) vs 镜脚净高 38.0 mm
[FAIL] 0 项
结论: ✅ 算术与文档自洽            rc=0
```

★ **根因说明 (不许含糊)**: **改前那 1 条 FAIL 的根因 = 脚数本身** (8p ⇒ 收敛版 24.0 mm; 10p ⇒ 25.0 mm, 8p→10p 多 2 脚 × 0.5 mm = **+1.0 mm**, 几何事实) **＋ 正文已按裁 2 改成 25.0** ⇒ 两者不一致 ⇒ 脚本判红。⇒ **这是 FAIL→PASS, 根因 = pin 数本身变 + 文档跟着镜像变**, **不是判据被放宽** (判据 `CRIT 0.60` / `cav_v 38.00` / `duct_v 6.00` 本单一字未动)。
★ **同时声明**: 收敛版 24.0 → 25.0 mm 仍 **< 镜脚净高 38.00 mm**, 余量 12.00 mm ⇒ **几何上仍放得下**, 不存在"10p 装不下"。

### ★ 每个数字变化属于哪一类 (最后一条纪律)

| 变化 | 类别 | 原因 |
|---|---|---|
| 收敛版堆叠 24.0 → 25.0 mm | **真源变** (8p→10p) | 网表逐脚复算 |
| §5.3 C-4 触点区 20.0 → **21.0 mm** (堆叠仍 25.0) | **真源变** | 同上 (行内算式 8+20+4+10) |
| V PCB 段 需求 21.00 → **36.00**, 余 +17.00 → **+2.00** (最坏 +1.40) | **真源变** (板宽 15→30) | `BOARD_GEOM_30MM.md` §1 |
| H PCB 段 需求 4.20 → **4.40**, 余 +3.10 → **+2.90** | **真源变** (板厚 0.80→1.00, 6 层) | 同上 |
| `hw_cross_review_check.py` PASS/FAIL 分布 | **未变** | 裁 8 不许动 ⇒ 不许因本单变红 |
| **判据阈值** | **一个都没动** | `judge/CRIT 0.60` / `cav_v 38.00` / `duct_v 6.00` |

### ★ `grep` 残留逐行归类 (说得清才叫做完)

`grep -rn '8p@0.5\|8p @0.5\|1×6@1.27\|1×6 1.27' MECH/` 的全部命中 **[实测] 只在 4 个历史脚本里, 没有一处是活文档的当前口径断言**:

| 文件:行 | 归类 | 说明 |
|---|---|---|
| `MECH/rebase_20261106.py:200` | **历史沿革 (旧值探针)** | `probe = {"probe_j_chg": "8p@0.5mm", ...}` = **喂给扫描器的已知旧值** (脚本自检用), 不是取值 |
| `MECH/rebase_20261106.py:437` | **历史沿革 (旧值探针)** | `_probe_stale["mech_j_chg_pins"] = "8p@0.5mm"`, 紧邻的 `_probe_truth` 已是 `10p@0.5mm` ⇒ **回归自检对**, 不会把 claim 写回 8p |
| `MECH/_frag_rebase_20261106.py:73` | **历史沿革 (归档 apply 脚本)** | 11-06 那轮的一次性 apply 脚本, 记录"原值 8p@0.5mm 已订正" |
| `MECH/_frag_update_iss200.py:92` · `_frag_update_iss202.py:88,103-108,120,153` | **历史沿革 (归档 apply 脚本)** | 11-12 那轮的一次性 apply 脚本, 记录"旧口径已被本单改掉" |
| `MECH/USB_HINGE_STRUCTURE.md` · 其余 6 份文档 | **零命中** | 活文档里已无 8p / 1×6@1.27 的当前口径断言 |

---

## 附: 本单边界自检 (一条没破)

- ✅ 没碰 `HW/**` (md5 一字未变) · 没碰 `SW/**` · 没碰 `state/gen_*.py` · 没碰 `state/issue_log.yaml` (status 是 main 的活) · 没碰 `PROJECT_TRACKER.md` §0
- ✅ 没碰别人的分片 (`state/fragments/{hw,sw,pm}.yaml` 一字没写) · 没碰 `MECH/print/**` · 没碰 `MECH/BOARD_GEOM_30MM.md` (只读)
- ✅ 写分片走 `state/frag_write.py` (原子写), 零 `open(p,"w")`
- ✅ 零外发 (无邮件/无询价/无采购/无问询)
- ✅ 没碰 PCB 布线 / 布局 / 逃线 / 层数 (主线 = 原理图 demo)
- ✅ 没改任何判据阈值
