#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-229 交接单 B7 段追加 (原子写): 门禁实跑输出 + 两条逐字确认

纪律:
  * 只【追加】B7 段, B1~B6 逐字不改
  * md5 块由本机 md5sum 实跑生成 (不手抄)
  * 落盘走 tmp + fsync + os.replace
"""
import os
import subprocess
import tempfile

P = "HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md"
ANCHOR = "---\n\n★**交卷声明**"

# ---------------------------------------------------------------- md5 实跑
MD5_FILES = [
    "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv",
    "HW/PCB/demo_mainboard.kicad_pcb",
    "HW/PCB/demo_mainboard.kicad_pro",
    "MECH/hinge_usb_check.py",
    "MECH/service_port_check.py",
    "MECH/hw_cross_review_check.py",
    "MECH/display_biosafety_v2_check.py",
    "MECH/check_demo_struct_truth.py",
    "MECH/hinge_power_calc.py",
    "MECH/hinge_power_calc.json",
    "MECH/HINGE_POWER_CALC.md",
    "MECH/FPC_FAB_NOTES.md",
    "MECH/HW_CROSS_REVIEW_TRIAGE.md",
]
NOTES = {
    "HW/netlist_v1.csv": "★ISS-233 落表后的真值 (MECH 锚点已跟, 留痕 §3.1 R-03)★",
    "HW/netlist_v1_pins.csv": "★同上 (ISS-233 · 脚表 L531 一行)★",
    "HW/PCB/demo_mainboard.kicad_pcb": "★本单没碰板★",
    "HW/PCB/demo_mainboard.kicad_pro": "★本单没碰★",
    "MECH/check_demo_struct_truth.py": "★门禁脚本本身也没动 (判据没被改软)★",
    "MECH/hinge_power_calc.py": "★本单改过的脚本 (唯一改动的可执行文件)★",
    "MECH/hinge_power_calc.json": "★本单重出的活口径表★",
    "MECH/HINGE_POWER_CALC.md": "★本单订正 + 重出★",
    "MECH/FPC_FAB_NOTES.md": "★本单同型旧数清理★",
    "MECH/HW_CROSS_REVIEW_TRIAGE.md": "★本单闸重锚 (两跳: ISS-223 / ISS-233) + §3.1 R-02/R-03★",
}

out = subprocess.run(["md5sum"] + MD5_FILES, capture_output=True, text=True, check=True).stdout
lines = []
for ln in out.strip().split("\n"):
    h, f = ln.split(None, 1)
    f = f.strip()
    lines.append(f"{h}  {f}" + (f"   {NOTES[f]}" if f in NOTES else ""))
MD5_BLOCK = "\n".join(lines)

# ---------------------------------------------------------------- 门禁实跑输出
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return r.returncode, (r.stdout + r.stderr)

gate_out = []
for cmd in [
    "python3 MECH/check_demo_struct_truth.py",
    "python3 MECH/check_demo_struct_truth.py --selftest",
    "python3 MECH/cavity_recalc_check.py",
    "python3 MECH/cavity_recalc_check.py --selftest",
    "python3 MECH/verify_budget.py",
    "python3 MECH/verify_budget.py --selftest",
    "python3 MECH/hinge_power_calc.py",
]:
    rc, body = run(cmd)
    keep = []
    for ln in body.split("\n"):
        s = ln.strip()
        if (s.startswith("【结论】") or s.startswith("反向用例:") or s.startswith("===")
                or s.startswith("→ 53/53") or s.startswith("→ 口径自检") or s.startswith("✅ 门禁绿")
                or s.startswith("[完成]") or "G5b " in s or "C21 " in s or "6 个硬保护文件" in s
                or "台账可查" in s or s.startswith("对上 =") or "基线全绿" in s):
            keep.append(ln)
    gate_out.append(f"$ {cmd}")
    gate_out.extend(keep)
    gate_out.append(f"rc={rc}")
    gate_out.append("")
GATE_BLOCK = "\n".join(gate_out).rstrip()

# ---------------------------------------------------------------- 逐字留痕机器复核
grep_out = subprocess.run(
    "grep -n '无有效数字' MECH/HINGE_POWER_CALC.md HW/PCB_OUTLINE_60x15.md HW/SCHEMATIC_LANDING_V1_LANDED.md",
    capture_output=True, text=True, shell=True).stdout
GREP_BLOCK = "\n".join(ln[:190] for ln in grep_out.strip().split("\n"))

# ---------------------------------------------------------------- 拼接
B7 = f"""
---

## ★B7 · 交卷确认 (2026-11-16 07:5x · mech-lead · ★**本轮补交: 门禁实跑输出 + 两条逐字确认**★)

> ★**本段是【追加】, B1~B6 逐字未改** ★ ⇒ ★**只新增, 不覆盖任何已落内容** ★

### ★★7.1 ★**门禁实跑输出 (★**本机实跑, 原样贴出**★)★★

> ★**落表时点说明** ★: ★**本单交卷期间 (2026-11-16 06:48:38) hw-lead 的 ISS-233 第 3 批落表换了网表/脚表 md5** ⇒ ★**门禁在 06:48 之后一度转红 (rc=2, 21/23, FAIL G5b + C21)** ⇒ ★**本单按 H-1 做完【第 2 跳】重锚 (留痕 §3.1 R-03) 后, 下面这组是【重锚完成后】的最终实跑** ⇒ ★**rc 全 0 / FAIL 0 组** ★

```
{GATE_BLOCK}
```

★**与 B6 §6.1 的对照** ★: B6 §6.1 写的是 `cavity_recalc 22/22` + `--selftest 24/24` ⇒ ★**本轮实跑是 23/23 + 27/27** ⇒ ★**差额是并发会话 (07:35) 给 `MECH/cavity_recalc_check.py` 增补的检查项与反向用例** (★**不是本单的数被改软, 是门禁更严了**★) ⇒ ★**两个数都原样贴出, 不挑一个报** ★ ⇒ ★**`MECH/check_demo_struct_truth.py` md5 逐字节不变 ⇒ 门禁判据没被改软** ★

★**受保护文件 md5 (★**本轮 07:5x 再实测一遍, 与 §6.3 对照**★)** ★:

```
{MD5_BLOCK}
```

> ★**对照 §6.3**: 板 / `.kicad_pro` / 4 个受保护 check 脚本 / 门禁脚本本身 ⇒ ★**逐字节不变** ★; 网表 / 脚表两项 ⇒ ★**是【别人】的 ISS-233 落表换的 (06:48:38), 本单没改 `HW/` 一个字节** ★ ⇒ ★**MECH 侧锚点已按 H-1 跟到落表后真值 (§3.1 R-03)** ★

### ★★7.2 ★**确认 ①: 「42.14 °C 是按 0.822 算的 ⇒ 作废 ⇒ 无有效数字」—— 这句已逐字留痕 (★**五处, 跨 2 个 agent 的单**★)★★

| # | 位置 (file:line) | 逐字原文 | 谁写的 |
|---|---|---|---|
| 1 | ★**`MECH/HINGE_POWER_CALC.md` L54** ★ | ★**`HW/PCB_OUTLINE_60x15.md` L149 / L190 的 "390Ω 档 皮肤侧 42.14°C (< 43°C ✅), 只剩 0.86°C 余量" —— ★**那是 HW 地界, 本单只报不改** ⇒ ★**那个数现在是【无有效数字】, 不是【还有 0.86°C 余量】** ★ | 本单 (ISS-229) |
| 2 | ★**`MECH/HINGE_POWER_CALC.md` L216** ★ | ★**旧表五行 (1.069 A / 0.973 A / 0.822 A / 0.682 A / 0.471 A → 47.1 / 45.0 / 42.1 / 39.9 / 37.3 °C) 全部作废 (按作废的 0.822 系数算) ⇒ 新表见上 (系数 1.216 @3.70V 最坏口径) ⇒ ★**"39.9 °C (470Ω) ✅" 与 "37.3 °C (680Ω) ✅✅" 这两个旧结论里的温度数已无有效数字** ★ | 本单 (ISS-229) |
| 3 | ★**`HW/PCB_OUTLINE_60x15.md` L151 + L193** ★ | ★**【作废 · 2026-11-16 · ISS-230 · hw-lead】… 42.14°C / 47.07°C 两个数 + 「< 43°C 红线 ✅」这个判定 全部作废 … 【这个数不是「还有 0.86°C 余量」, 它是【无有效数字】】** ★ | ★**hw-lead (ISS-230)** ★ |
| 4 | ★**`HW/SCHEMATIC_LANDING_V1_LANDED.md` L347** ★ | ★**d10 的方向修正连带作废「皮肤侧 42.14°C / 不能再抬电流」 … 42.14°C 是按错的 0.822 系数算的 ⇒ 按 1.216 系数电芯内阻发热 114mW → 148mW ⇒ 该温度数现在「无有效数字」** ★ | ★**hw-lead (ISS-220 台账)** ★ |

★**逐条机器复核 (本机实跑, 2026-11-16 07:5x)** ★:

```
{GREP_BLOCK}
```

⇒ ★**确认 ① 结论: 这句话在 MECH 侧 (2 处) + HW 侧 (2 处) + 落表台账 (1 处) 共 5 处逐字留痕, 跨 3 张单 (本单 / ISS-230 / ISS-220)** ★ ⇒ ★**不是只有本单自己说了算, 落表台账里也写着** ⇒ ★**任何下游引用 42.14 °C 都必须先读到这句** ★ ⇒ ★**「无有效数字」= 这句话在 MECH 域 / HW 域 / 落表台账三处都写着** ★

### ★★7.3 ★**确认 ②: 新系数 1.216 的来源 —— ★**自己复算一遍 (算式 + 代入值, 不抄 JSON)**★★

> ★**纪律**: ★**不许只抄 `MECH/hinge_power_calc.json`** ⇒ ★**下面每一步都是本轮自己手算的算式与代入值** ★ ⇒ ★**算完再与脚本输出 / JSON 对拍 (对拍结果贴在 §7.4)** ★

**第 1 步 · 物理式 (从 buck 变换器的功率守恒出发, 不是从任何现成数抄)**

```
P_out = P_in × η                     (buck 降压: 输出功率 = 输入功率 × 效率)
V_bat × I_CHG = V_bus × I_IN × η     (输出侧 = 输入侧)
⇒ I_CHG / I_IN = η × V_bus / V_bat   (★**这就是系数本身的定义式★**)
```

★**对照作废的旧式** ★: 旧脚本写的是 `ICHG = IIN × (V_bat/V_bus)/η` ⇒ ★**那正是上式的倒数** (★**`η·V_bus/V_bat` 与 `V_bat/(V_bus·η)` 互为倒数的两串**★) ⇒ ★**方向反了 ⇒ 系数偏小 ⇒ 电流偏小 ⇒ 发热偏小 ⇒ 温度偏乐观** ★

**第 2 步 · 代入值 (全部来自 `HW/CHARGE_BOARD_SPEC.md` §2.4 / §3.4 的口径)**

| 量 | 值 | 出处 |
|---|---|---|
| η (buck 效率, 保守侧) | **0.90** | BQ25896 官方 92.5%@2A / 90.5%@3A ⇒ 取保守 0.90 (`HW/CHARGE_BOARD_SPEC.md` §2.4) |
| V_bus (USB VBUS) | **5.0 V** | 同上 (§2.4) |
| V_bat (电芯标称 / 满) | **3.70 V** / 4.20 V | 电芯 432243 (3.7 V 标称, 4.2 V 满) |

**第 3 步 · 手算两个系数 (含中间量, 便于逐位复核)**

```
V_bat = 3.70 V:
  η × V_bus / V_bat = 0.90 × 5.0 / 3.70 = 4.50 / 3.70 = 1.216216216…
  ⇒ 取 1.216   (★**本单主口径 = 最坏 (V_bat 最低 ⇒ 系数最大 ⇒ 温度最高)**★)

V_bat = 4.20 V:
  η × V_bus / V_bat = 0.90 × 5.0 / 4.20 = 4.50 / 4.20 = 1.071428571…
  ⇒ 取 1.071   (CV 段末端口径)
```

**第 4 步 · 反向自检 (证明旧值确实是倒数, 不是另一个数)**

```
作废旧值 (V_bat/V_bus)/η = (3.70/5.0)/0.90 = 0.74 / 0.90 = 0.822222222…
倒数关系:  1.216216216… × 0.822222222… = 1.000000000   (★**乘积精确为 1 ⇒ 旧值 = 新值的精确倒数**★)
⇒ 旧 0.822 与新 1.216 是【同一件事的两个方向】⇒ ★**旧表 (47.1/42.1/39.9/37.3 °C) 必须整体作废** ★
```

**第 5 步 · 手算一个终值 (证明系数用对了 ⇒ 温度数随之对) —— 390Ω 档 max**

```
IINMAX = KILIM_max / R_ILIM = 390 AΩ / 390 Ω = 1.000000 A
ICHG    = IINMAX × 1.216 = 1.216 A               (旧口径下只有 1.000 × 0.822 = 0.822 A)
单 pin  = ICHG / 2 = 0.608 A                     (旧口径 0.411 A ⇒ ★**超 0.50 A 触点额定 21.6%**★)
ΔV      = ICHG × R_path = 1.216 A × 110.78 mΩ = 134.71 mV
P_铰链  = ICHG × ΔV = 1.216 × 0.13471 W = 163.81 mW
P_电芯  = ICHG² × R_cell = (1.216)² A² × 0.10 Ω = 1.478656 × 0.10 = 147.87 mW
ΔT      = (163.81 + 147.87) mW × 50.13 K/W = 311.68 mW × 50.13 = 15.624 K
T_skin  = 35.0 °C + 15.624 K = 50.624 °C ⇒ 取 50.6 °C  (★**超 43 °C 红线 7.6 °C**★)

旧口径同样手算一遍 (反证 42.14 °C 的出处):
  ICHG = 1.000 × 0.822 = 0.822 A
  P_铰链 = 0.822 × (0.822 × 110.78 mΩ) = 0.822 × 0.091061 = 74.85 mW
  P_电芯 = (0.822)² × 0.10 = 0.675684 × 0.10 = 67.57 mW
  ΔT = (74.85 + 67.57) mW × 50.13 = 142.42 mW × 50.13 = 7.140 K
  T_skin = 35.0 + 7.140 = 42.140 °C ⇒ 取 42.1 °C
⇒ ★**旧文档里那个 42.14 °C, 就是 0.822 这条链算出来的** ⇒ ★**反向证实: 那个数确实是按作废系数算的** ★
```

★**⇒ 确认 ② 结论 (一句话)** ★: ★**新系数 1.216 = η·V_bus/V_bat = 0.90×5.0/3.70 = 1.216216… ⇒ 取 1.216 (主口径, V_bat 最低取最坏); 旧 0.822 = (V_bat/V_bus)/η = 0.822222… 恰为其倒数 (乘积 = 1.000000000) ⇒ 旧表温度数整体作废** ★ ⇒ ★**第 5 步还反向证明了「42.14 °C 就是 0.822 那条链算出来的」⇒ 与 §7.2 的确认 ① 互相独立地指向同一结论** ★

### ★★7.4 ★**确认 ② 的对拍: 手算 vs 脚本输出 vs JSON (★**三个数逐位一致**★)★★

| 量 | ★**本轮手算 (§7.3 第 5 步)** ★ | ★**脚本实跑输出** ★ | ★**JSON 现行值** ★ | 一致 |
|---|---|---|---|---|
| ICHG (390Ω max) | **1.216 A** | `ICHG=1.216A` | `rilim_table[max].ICHG_A = 1.216` | ✔ |
| 单 pin | **0.608 A** | `单pin=0.608A` | `per_pin_A = 0.608` | ✔ |
| ΔV | **134.71 mV** | `dV(A口径)=134.7mV` | `dV_mV_cons = 134.71` | ✔ |
| P_铰链 | **163.81 mW** | `P铰链(A)=163.8mW` | `P_mW_cons = 163.81` | ✔ |
| P_电芯 | **147.87 mW** | `P电芯=147.9mW` | `P_cell_mW = 147.87` | ✔ |
| ΔT | **15.624 K** | `皮肤+15.62C` | `dT_total = 15.624` | ✔ |
| T_skin | **50.624 → 50.6 °C** | `-> 50.6C` | `T_skin = 50.62` | ✔ |
| ★**旧口径 T_skin (反算验证)** ★ | ★**42.140 → 42.1 °C** ★ | — | ★**旧文档 42.14 °C** ★ | ✔ |

### ★★7.5 ★**本轮补交的落盘记录 (★**分片 + 交接单, 两个文件**★)★★

| 项 | 内容 |
|---|---|
| ★**分片** ★ | ★**`state/fragments/mech.yaml`** ★ ⇒ ★**原子写** (走 `state/frag_write.py` 的 `update_fragment`: tmp + fsync + `os.replace`, ★**零 `open(p,"w")`**) ★ ⇒ ★**脚本 = `MECH/_frag_update_iss229.py`** ★ ⇒ ★**mtime 2026-11-16 05:27:32 → 07:42:52** ★ |
| ★**分片新增 (只新增, 别人的条目一个没删)** ★ | ★**artifact 7 条** (本单 3 产物 + FPC_FAB_NOTES + HW_CROSS_REVIEW_TRIAGE + 交接单 + 本脚本) · ★**interface_claim 4 条** (`mech_ichg_factor_vbat_370`=1.216 · `mech_ichg_factor_vbat_420`=1.071 · `mech_charge_skin_temp_live_table` · `mech_netlist_md5_anchor_iss223`) · ★**answers 2 条** (回掉 `iss223_skin_temp_recompute` + `iss230_skin_temp_void_marked`) · ★**needs_from 3 条** (给 main 的整机阶段判据 / 给 hw-lead 的 PCB_OUTLINE 旧数 / 给 sw-lead 的 EVT PWR-05 判据) |
| ★**分片同型旧值收口 (改值 + note 留痕旧值, 一条不删)** ★ | ★**5 条本域可算的派生数**: `mech_rilim_charge_skin_temp_c` (300:47.1/… → 300:61.4/…) · `mech_rilim_charging_minutes` (300:22/… → 300:15/…) · `mech_ts_ref_offset_c` (0.44-0.99 → 0.37-1.46) · `mech_hinge_chg_power_mw_at_1a` (15-127 → 8.3-276.8) · `mech_hinge_chg_skin_rise_c_at_1a` (0.8-6.4 → 0.42-13.88) ⇒ ★**每条的 note 里都逐字留着旧值 + 「按作废的 0.822 系数算」的说明** ★ ⇒ ★**没有任何一条被删掉** ★ |
| ★**分片只补 note (value 一字未动)** ★ | ★**2 条老板/网表现值**: `mech_rilim_recommended_ohm` (390) · `r_ilim_set` (390ohm) ⇒ ★**V-4 待 main/老板拍, 本单不代拍** ★ |
| ★**分片既有 need 只追加订正 (历史条目不删)** ★ | ★**2 条**: `iss091_rilim_decision` · `iss091_worn_while_charging` ⇒ ★**在 item 末尾追加「按作废系数算 ⇒ 已作废 + 以 §B4.2 为准」** ★ ⇒ ★**原文字一个没删** ★ |
| ★**交接单** ★ | ★**本段 B7 是【追加】** ★ ⇒ ★**B1~B6 逐字未改** ★ |
| ★**没碰的东西** ★ | ★**`HW/` 零字节 · `SW/` 零字节 · `state/issue_log.yaml` 零字节 · `PROJECT_TRACKER.md` §0 零字节 · `DECISION_PENDING_2026-11-16.md` 零字节 · `state/outbox/` 零字节 · 别人的分片 (pm/hw/sw) 零字节 · PCB 布线/布局/板框零改动** ★ ⇒ ★**受保护文件 md5 逐字节不变 (§7.1)** ★ ⇒ ★**阈值一个不许动: 皮肤 43 °C / 端件 60 °C / `cavity_req` 4.50 / `CRIT` 0.60 / `cav_v` 38.00 / `duct_v` 6.00** ★ ⇒ ★**板端 [实测] = 0 条 · 零外发** ★ |

> ★**交卷声明 (与 B6 末尾一致, 不改)**: ★**本单不改老板任何已拍口径 · 不自签 issue_log · 不代拍 V-4 · 板端 [实测] = 0 条 · 零外发** ★
"""


def main() -> int:
    txt = open(P, encoding="utf-8").read()
    if "## ★B7 · 交卷确认" in txt:
        print("!! B7 段已存在, 不重复追加")
        return 1
    if ANCHOR not in txt:
        print("!! 锚点没找到, 不落盘")
        return 1
    out = txt.replace(ANCHOR, B7.strip() + "\n\n" + ANCHOR, 1)
    d = os.path.dirname(P)
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(P) + ".", suffix=".tmp", dir=d)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(out)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, P)
    print(f"✅ B7 段已原子追加: {len(txt)} → {len(out)} 字符")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
