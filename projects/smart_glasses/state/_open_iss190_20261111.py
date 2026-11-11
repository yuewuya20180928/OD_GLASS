#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开 ISS-190 (owner=sw-lead) —— SW 侧时序/电源评审口径漂移复评 + timing_check.py 改实读网表
================================================================================
★**为什么现在开这一单 (main 实测, 不是推测)**:
  · `advance.py --json` 的 A 段 (internal[]) **恒为空** ⇒ 根因: 26 条 `open` 的 owner
    【全部】是 `main` / `boss` ⇒ **三个总工名下没有 open 单** ⇒ 自动派活无单可派。
    ★本单走项目既有做法 (见 `state/_open_iss186_20261111.py` / `_apply_iss188_...`):
    **main 开一单并指派 owner=sw-lead** ⇒ 下一轮 advance.py 就能自动派出去。
  · ★**而且这一单不是凑数**: 实测发现 **SW 侧的时序/电源评审 (SW/SW_TIMING_REVIEW.md)
    与其机械复核器 (SW/tools/timing_check.py) 已经和现网表脱节** —— 三处硬证据:
      ① 口径漂移: 该文声明被评审对象 = netlist **476 行 / V1.6**; 现行 = **513 行**。
      ② F4 的自带复现命令记录 = 0, **main 实跑 = 11** ⇒ "控制脚在网表里根本不存在" 对 EN 已不成立。
      ③ F8 的自带复现命令是**假阴性** (pattern 看不见 `U_PWR_SW`) ⇒ F8 结论对现网表**是错的**。
      ④ timing_check.py **从不打开网表**, F8 写死 `False` 还当自测 **PASS 条件** ⇒ **假绿**;
         且 `R_I2C_PULL` 写死 4700, 而现网表 I2C_A 实际 **2.2k / 1.8V 域** ⇒ 一条结论会翻转。
  · ★**主线口径 (老板 2026-11-11 10:07)**: 当前主线 = 硬件原理图 demo 绘制 ⇒ PCB 布线/布局类不派;
    本单 = 【网表 / ERC / 软件】类 ⇒ 在优先派活范围内。

★**只做这一单**: ① 复评 (SW 侧) ② 把复核器从"手抄常量"改成"实读网表" ③ 把假绿变真绿 (加反向用例)。
   ★**不许改网表** (网表侧矛盾只报不改 —— 那是 hw-lead 的分片)。

原子写 (tmp + os.replace)。
"""
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-11"

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f)

items = list(doc.get("issues") or [])
existing = {it.get("id") for it in items}
if "ISS-190" in existing:
    print("ℹ️ ISS-190 已存在, 跳过 (幂等)")
    sys.exit(0)

BRIEF = """\
★**目标**: 把 SW 侧对 demo 主板上电/复位/时序的评审 (`SW/SW_TIMING_REVIEW.md`) 与其机械复核器 \
(`SW/tools/timing_check.py`) **重新锚定到现行网表**, 并把"假绿"改成"真绿" —— 让 timing_check.py 的\
每个网表相关数字都【从网表实读】算出来, 而不是手抄常量; 凡结论与现网表矛盾的, 按现网表订正并标 [实测]。

★**为什么现在做 (★main 2026-11-11 13:0x 实测, 不是推测★)**
1. ★**口径漂移**: `SW/SW_TIMING_REVIEW.md` 头部声明被评审对象 = `HW/netlist_v1.csv` (**476 行**, V1.6, \
2026-10-27); ★**现行网表 = 513 行** (md5 `c78f991283cc82d56c8e3dd31657c785`, 2026-11-05 10:57) ⇒ 中间 37 行 \
是 V1.7/V1.8 变更, ★**本文从未复评**。
2. ★**F4 已被现网表推翻 (部分)**: 该文 §6 自带复现命令 \
`grep -cE ",(EN|SS|CT|MR)[, ]" HW/netlist_v1.csv` 记录 = **0**; ★**main 实跑 = 11** (EN 10 行: \
`EN_VCORE`→`U_DCDC_VCORE` pin13 · `EN_VIO`→`U_DCDC_VIO` pin13 · 7 颗 `U_LDO_*` pin3 · `U_EN_SW` pin2 · \
`CARRIER_BOARD_EN`; CT 1 行: `SUPV_CT`→`U_SUPV` pin4, ★但 `U_SUPV` 本身 DNP); ★**SS/MR 仍 = 0** ⇒ \
"供电器件的控制脚在网表里根本不存在" **对 EN 已不成立**, 对 SS/MR 仍成立。
3. ★**F8 的复现命令本身是假阴性 ⇒ 结论已错**: `grep -cE "LOAD|LOADSW|U_LS" HW/netlist_v1.csv` 记录 = 0, \
★**main 实跑也 = 0** —— 但★**现网表里负载开关叫 `U_PWR_SW`** (TPS22991RAA, 9 行: VIN=`BAT_SW` → \
VOUT=`RAIL_SYS`; ON pin2 配 `R_PD_ON` 10k 下拉 = 默认关; `Q_PG` P-MOS 高边) ⇒ **该 pattern 永远看不见它** \
(`U_PWR_SW` 不含 LOAD/LOADSW/U_LS 任一子串)。★而 `HW/POWER_SHUTDOWN_V3.md` §3 已写明该真关机拓扑 ⇒ \
F8 的结论"网表里没有负载开关/电源开关/EN 断开路径 ⇒ 关机只能靠软件深睡, 轨全部带电" \
★**对现网表是错的**。
4. ★**timing_check.py 是"假绿"**: 它★**从不打开网表** (全文只有第 25 行注释提到 `netlist_v1.csv`), \
F8 段直接写死 `"load_switch_in_netlist": False` / `"rail_switching_devices": 0` (L193-198), \
★**自测第 227 行却把 `is False` 当 PASS 条件** ⇒ ★**网表变了它照样绿**。同类: `R_I2C_PULL` 写死 **4700** \
(L38, 注释"网表 P2/P4: 4.7k 上拉到 3.3V"), ★**但现网表 L169 的 `R_PU_I2CA_SCL` = 2.2k → \
`RAIL_VDD_1V8_IO` (1.8V 域, ISS-153 11-04 订正)**。⇒ F3 的 t_r 按 4.7k 算是 **398ns@100pF**; \
按 2.2k 算是 **186ns**; 且 300pF 标准模式上限判据 (现文档: 1194ns > 1000ns ⇒ ❌) 按 2.2k 算是 **559ns ⇒ ✅** \
⇒ ★**一条结论会翻转**。
   ⚠ 另: ★**现网表自身就有两行打架** —— L167 (`I2C_A_SCL` 的 NET 行) 仍写"上拉 4.7k 到 3.3V … \
t_r=2.38µs@100pF", L169 (R 行) 写 2.2k/1.8V ⇒ ★**这属 hw-lead 的网表分片, 你只报不改** (见边界)。

★**交付物 (3 件, 缺一不可)**
**A. `SW/SW_TIMING_REVIEW.md` —— 按现网表复评**
   · 头部"被评审对象"改为 **513 行 / md5 `c78f991283cc82d56c8e3dd31657c785` / 2026-11-05 10:57**, \
并注明相对 476 行版本哪些结论变了 (推翻 / 部分推翻 / 仍成立)。
   · ★**F1~F8 逐条**给: 结论 (仍成立 / 已推翻 / 部分成立) + 复现命令 + ★**实跑输出** + 证据等级。
   · ★**新增一节**写"本次复评发现的网表侧待修项" (如 L167 与 L169 矛盾) ⇒ ★**登记 needs_from 给 \
hw-lead** (走 `state/frag_write.py`), ★**不要自己改网表**。
   · ★**不许删改 §7 证据分级里任何 [实测]/[官方]/[推算]/[0数据] 标签**。
**B. `SW/tools/timing_check.py` —— 从"手抄常量"改成"实读网表"**
   · ★**用 csv 读 `HW/netlist_v1.csv`**, 凡网表可得的量一律**现读现算**: ① F1/F2 的 R/C 与 τ 注记 \
② F3 ★**按网名分别**取上拉电阻值与域 (★**I2C_A = 2.2k / 1.8V**, I2C_B = 4.7k / 3.3V) ③ F4 \
EN/SS/CT/MR 脚是否在网表 ④ F5 上拉轨域 ⑤ F8 负载开关是否存在 (★**按 ref 名 `U_PWR_SW` / `U_EN_SW` 认**, \
★**不要再用 `LOAD|LOADSW|U_LS` 这个看不见东西的 pattern**)。
   · 器件级常数 (TPS3808 VIT / CT 延时 等) 可留常量, 但每条**必须注明来源** (datasheet / [官方])。
   · 输出里★**必须打印网表锚点** (md5 + 行数) ⇒ 下次漂移一眼可见。
   · ★**既有 21 条自测一条不许删 / 不许弱化**; 另★**必须加反向用例**: 改坏输入 (如改掉网表里 \
I2C_A 上拉那一行) ⇒ 对应判据**必须变红** ⇒ 自测要能证明"它真在读网表", 不是在演常量。
**C. 交接单 `HANDOFF/2026-11-11_sw-lead_ISS190_*.md`** —— ★**必须含 B1~B6 六块** \
(结论摘要 / 验收标准自评 / 证据分级 / 接口取值声明 / 未决项与卡点 / 自证复现命令) ⇒ \
★**`state/gate_check.py` 的 Q1 是按"每个 agent 最新一份交接单"打分的, 缺 B 块 ⇒ Q1 掉出 18/18**。

★**写入范围 (只许动这些)**
· 可改: `SW/SW_TIMING_REVIEW.md` · `SW/tools/timing_check.py` · `HANDOFF/2026-11-11_sw-lead_ISS190_*.md` (新建) · \
`state/fragments/sw.yaml` (★**只经 `state/frag_write.py` 原子写**)。
· ★**只读不许改**: `HW/netlist_v1.csv` 与 `HW/**` 任何文件 (网表矛盾**只报不改**) · `state/issue_log.yaml` \
(落账由 main 做) · 别人的分片 (`hw.yaml`/`mech.yaml`/`pm.yaml`) · `PROJECT_TRACKER.md` §0 锁死表。

★**验收标准 (★可机械判★)**
1. `python3 SW/tools/timing_check.py` ⇒ rc=0, 且输出里的★**网表锚点行** (md5 + 行数) 与 \
`md5sum HW/netlist_v1.csv` 一致。
2. ★**反向用例 (★必做★)**: 把网表副本里 I2C_A 上拉那一行改掉后重跑 ⇒ 对应 t_r / 判据**必须变** \
(旧 398ns → 新值) ⇒ ★**证明它真在读网表**。
3. 既有自测 **21 条全保留**且通过; 新增反向用例 ≥1 条且**会红**。
4. `SW/SW_TIMING_REVIEW.md` 里 F1~F8 每条都有"结论 + 复现命令 + 实跑输出 + 证据等级"; 头部已锚定 513 行; \
§6 复现命令★**当场可跑** (main 会重跑你贴的命令)。
5. `python3 state/merge.py` ⇒ rc=0; `python3 state/gate_check.py` ⇒ ★**Q1 = 18/18** ⇒ 两个输出都贴进回复。
6. ★**不许**把 §7 证据分级里任何标签删掉或改成别的。

★**自证命令 (交卷前跑, 输出贴回复)**
```
python3 SW/tools/timing_check.py
md5sum HW/netlist_v1.csv; wc -l < HW/netlist_v1.csv
grep -cE ",(EN|SS|CT|MR)[, ]" HW/netlist_v1.csv
grep -c "U_PWR_SW" HW/netlist_v1.csv
grep -n "R_PU_I2CA_SCL" HW/netlist_v1.csv
python3 state/merge.py
python3 state/gate_check.py
```

★**边界**
· ★**不许联系供应商 / 原厂 / 外部** (外发一律经项目总工) —— ★**本单不需要任何外部信息**。
· ★**不许**把"改网表"混进来 (那是 hw-lead 的分片); 发现网表侧矛盾 ⇒ 只报 + 登记 needs_from。
· ★**不许**动 §0 锁死表 / 别人的分片 / `state/issue_log.yaml`。
· ★**写分片必须用 `state/frag_write.py`**, ★**禁止 `open(p,"w")`** (并发写分片会让合并器读到半截 YAML ⇒ \
整份数据静默消失 ⇒ 项目压测实测过的坑)。
· ★**交卷前必须** `python3 state/merge.py` (rc=0) && `python3 state/gate_check.py` (Q1=18/18) ⇒ 贴输出。
"""

ISS190 = {
    "id": "ISS-190",
    "title": ("★SW 侧时序/电源评审与机械复核器口径漂移 ⇒ SW_TIMING_REVIEW 锚在 476 行旧网表 "
              "(现行 513 行) ⇒ F4/F8 结论已被现网表推翻 ⇒ timing_check.py 实读网表 (现为手抄常量 + 假绿自测)"),
    "severity": "high",
    "source_blocker": "SW-TIM-B1",
    "source_agent": "main",
    "desc": (
        "★2026-11-11 13:0x 项目总工实测开单 (★不是推测★)。\n"
        "★**根因 (为什么本单现在才存在)**: `advance.py --json` 的 A 段恒空 ⇒ 26 条 open 的 owner "
        "【全部】是 main/boss ⇒ 三个总工名下没有 open 单 ⇒ 自动派活无单可派 ⇒ 本单按项目既有做法 "
        "(`_open_iss186_20261111.py` / `_apply_iss188_verify_iss189_open_20261111.py`) 由 main 开单并指派。\n"
        "★**发现的真问题 (三处硬证据)**: ① 口径漂移 —— `SW/SW_TIMING_REVIEW.md` 声明被评审对象 = "
        "`HW/netlist_v1.csv` **476 行 / V1.6 / 2026-10-27**; ★**现行 = 513 行** (md5 "
        "`c78f991283cc82d56c8e3dd31657c785`, 2026-11-05 10:57) ⇒ 37 行变更从未复评。\n"
        "② ★**F4 已被现网表推翻 (部分)**: 该文 §6 自带命令 `grep -cE \",(EN|SS|CT|MR)[, ]\" "
        "HW/netlist_v1.csv` 记录 = 0, ★**实跑 = 11** (EN 10 行 + CT 1 行; SS/MR 仍 = 0) ⇒ "
        "\"供电器件的控制脚在网表里根本不存在\" 对 EN 已不成立。\n"
        "③ ★**F8 的复现命令是假阴性 ⇒ 结论已错**: `grep -cE \"LOAD|LOADSW|U_LS\" HW/netlist_v1.csv` "
        "记录 = 0, ★**实跑也 = 0** —— 但★**现网表里负载开关叫 `U_PWR_SW`** (TPS22991RAA, 9 行: "
        "VIN=`BAT_SW`→VOUT=`RAIL_SYS`; ON pin2 配 `R_PD_ON` 10k 下拉=默认关; `Q_PG` P-MOS 高边) ⇒ "
        "★**该 pattern 永远看不见它**; 而 `HW/POWER_SHUTDOWN_V3.md` §3 已写明该真关机拓扑 ⇒ F8 结论"
        "\"关机只能靠软件深睡, 轨全部带电\" ★**对现网表是错的**。\n"
        "★**假绿 (★本单最要紧的一条★)**: `SW/tools/timing_check.py` ★**从不打开网表** (全文只有第 25 行"
        "注释提到 `netlist_v1.csv`), F8 段写死 `\"load_switch_in_netlist\": False` (L193-198) 而★**自测 "
        "L227 把 `is False` 当 PASS 条件** ⇒ ★**网表变了它照样绿**; 同类 `R_I2C_PULL` 写死 4700 (L38), "
        "★**现网表 L169 的 `R_PU_I2CA_SCL` = 2.2k → `RAIL_VDD_1V8_IO` (1.8V 域, ISS-153 11-04 订正)** ⇒ "
        "F3 的 t_r 按 4.7k 算 398ns@100pF, 按 2.2k 算 186ns, 且 300pF 上限判据 1194ns(❌)→559ns(✅) ⇒ "
        "★**一条结论会翻转**。\n"
        "★**主线口径**: 老板 2026-11-11 10:07 ⇒ 当前主线 = 硬件原理图 demo 绘制; PCB 布线/布局类不派 ⇒ "
        "★**本单是【网表 / ERC / 软件】类, 在优先派活范围内**。\n"
        "★**边界**: 只改 `SW/SW_TIMING_REVIEW.md` + `SW/tools/timing_check.py` + 自己的 HANDOFF + 自己的分片; "
        "★**网表只读不许改** (网表自身矛盾 L167 vs L169 只报不改 ⇒ 登记 needs_from 给 hw-lead); "
        "★**不许联系供应商/原厂**; ★**写分片必须走 `state/frag_write.py`**。"
    ),
    "owner": "sw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-13",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": "",
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "★2026-11-11 13:0x 项目总工开单 (owner=sw-lead, verify_by=main ⇒ ★**自己修的必须别人验**, "
        "铁律满足 —— 修复人 sw-lead, 验收人 main)。\n"
        "★**为什么这一单现在才派得出来**: 26 条 open 的 owner 全部是 main/boss ⇒ 三个总工名下没有 open "
        "⇒ advance.py A 段恒空 ⇒ 自动派活无单可派 ⇒ 本单是 main 按项目既有做法 (_open_iss186_20261111.py "
        "那一套) 开的**指派单**。\n"
        "★**为什么不派 PCB 类**: 老板 11-11 10:07 指令 —— PCB 布线/布局类一律【不派】(排队等原理图定稿); "
        "ISS-181 (hw-lead, 自研 demo 主板布线到可下单) ★**本轮按主线口径继续排队不派**。\n"
        "★**与 hw-lead 在飞任务的关系**: 主线第六件 (hw-lead 补图, 11:38 起) 动的是 "
        "`demo_mainboard*.kicad_sch` + 生成器 + `state/check_sch_pinfull.py`; ★**本单动的文件与之零交集** "
        "(`SW/**` + `HANDOFF/` + `state/fragments/sw.yaml`), ★**网表 `HW/netlist_v1.csv` 两个任务都不许改** "
        "(主线第六件任务书明写\"不许改 netlist_v1.csv\") ⇒ ★**无并发写冲突**。\n"
        "★**验收**: main 会独立重跑本单贴的复现命令 + 跑反向用例 + 查 `merge.py` rc=0 与 `gate_check.py` "
        "Q1=18/18 ⇒ ★**不采信自述**。"
    ),
    "task_brief": BRIEF,
}

items.append(ISS190)
doc["issues"] = items

fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)
    os.replace(tmp, LOG)
except Exception:
    if os.path.exists(tmp):
        os.unlink(tmp)
    raise

print("✅ 已原子写 issue_log.yaml:")
print("   - ISS-190 (owner=sw-lead, verify_by=main, due=2026-11-13) SW_TIMING_REVIEW 复评 + timing_check.py 实读网表")
print(f"   issue 总数: {len(items)}")
