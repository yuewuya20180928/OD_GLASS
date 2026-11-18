#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开 ISS-192 (owner=mech-lead) —— 结构侧(MECH)机械复核器全线迁到现行 60×30 板 + PIN-SET-2 孔位 Y 两套口径仲裁

★**为什么现在开这一单 (main 2026-11-11 13:4x~14:2x 实测, 不是推测★)**:
  · `advance.py --json` 的 A 段 (internal[]) **恒为空** ⇒ 根因: 26 条 `open` 的 owner
    【全部】是 `main`/`boss` ⇒ **三个总工名下没有 open 单** ⇒ 自动派活无单可派。
    ⇒ 本单走项目既有做法 (`_open_iss186_20261111.py` / `_open_iss190_20261111.py`):
    **main 开一单并指派 owner=mech-lead** ⇒ 下一轮 advance.py 就能自动派出去。
  · ★**本单不是凑数**: 结构侧那一整套机械复核器**全部**还钉在**已作废的 12mm/15mm 板宽**上,
    而板宽**已由老板 10-29 19:16 拍板 30mm**、板长 10-28 裁 60mm (§0 台账 11-01 20:5x 已订正)
    ⇒ ★**它们现在的绿灯/红灯都不是关于现行板子说的** (实测见 brief)。
  · ★**主线口径**: 老板 11-11 10:07 ⇒ 当前主线 = 硬件原理图 demo 绘制; PCB 布线/布局类不派;
    本单 = 【结构 / 网表接口 / 机械闸】类 ⇒ 在优先派活范围内, 且**不碰 PCB 布线**。

★**只做这一单**: ① 迁 MECH 机械闸到 60×30 ② 仲裁 PIN-SET-2 孔位 Y 的两套互斥口径
   ③ 把 demo 板"零安装孔/零 keepout"这件事报出去 (只报不改)。

原子写 (flock + 锁内重读 + tmp/os.replace)。
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-11"

BRIEF = """\
★**目标**: 把**结构侧 (MECH) 整套机械复核器**从"已作废的 12mm/15mm 板宽"迁到**现行 60×30mm 板**,
   并把 **PIN-SET-2 孔位 Y 的两套互斥口径 (差 7.50mm)** 仲裁成**一份权威表** (机械侧出结论 + 报给 hw-lead 改他的产物,
   **你不许动 HW/ 任何文件**)。

★**背景 (main 2026-11-11 13:4x~14:2x 实测, 不是推测★)**:
1. **板宽已不是 15mm**: 老板 10-29 19:16 拍板"板宽可以放到 30mm 以内"; 板长 60mm (10-28 项目总工裁);
   §0 台账 11-01 20:5x 已订正 ⇒ **12mm / 15mm / 板长 76mm 都是死值**。
2. ★**六个 MECH 脚本仍带死常量 (行号照抄, 你自己复核)**:
   · `MECH/pinset2_mech_check.py` :44 `PCB_W = 15.00` · :50 `SOC_Y0, SOC_Y1 = 3.50, 11.50`
     (RK3588 时代 FCCSP 8×10 口径) · :56 `JCHG_Y0, JCHG_Y1 = 4.25, 10.75` (居中 Y=7.50)
     · :59-63 `HOLES` = 15mm 板孔位 P1(8,7.50) P2(52,7.50) S1(8,2.50) S2(52,12.50)
   · `MECH/skeleton_section_check.py` :45 `PCB_W = 15.00` · :53 `SOC_Y_LEN = 8.00` ·
     :55 `HOT_BAND = 3.50` (= (15-8)/2)
   · `MECH/cross_review_check.py` :36 `"board_w": 12.0` · :37 `"board_w_alt": 15.0` · :38 `"board_l": 76.0`
   · `MECH/fit_check.py` :55 `"pcb_w": 12.00` (v2 基线; 30mm 版是 `MECH/fit_check_v3_30mm.py`)
   · `MECH/hinge_usb_check.py` :45 `"board_w_mm": (12.0, "暂锁 12mm")`
   · `MECH/iss065_check.py` :76 `PCB_W = 15.00` 但注释标 **[官方]** ⇒ 15mm 决策本身已作废 ⇒ **来源标错**
3. ★★**假绿 (本单最要紧的一条)**: `MECH/pinset2_mech_check.py` 现在跑出来是
   **"复算项 31 | FAIL 0 | WARN 3" rc=0** ⇒ ★**它是在一块已经不存在的板子上亮绿灯**。
   main 实测把它迁到 30mm + RK3576 (SoC 占位 Y 6.95..23.05 ⇒ 逃线带 Y[6.15,23.85]) ⇒
   **FAIL 变 1** —— 且★**变红的那条判据本身就是 15mm 语义**:
   "老口径 (2×M1.2 + 1×⌀2.0H7 @孔心到板边2.50) 在 15mm 板下不可用 → 必须改"
   (15mm 板: 3/3 孔压逃线带 ⇒ 判据成立; 30mm 板: 只剩 **2/3** ⇒ 判据语义变了)。
   ⇒ ★**只改常量不够, 判据文案与判据本身要一起重推** (你重新定判据并说明依据)。
   ⇒ 另 3 条 WARN 不变 (打印包契约: pcb_len 50 vs 板长 60 / ⌀2.4 让过孔 1 个 vs 应 2 个 /
     M1.2 让过孔中心距 40.00 vs 应 44.00) ⇒ ★**打印包契约也是老口径, 是本单要出权威表的一部分**。
4. ★**`MECH/cross_review_check.py` 是孤儿脚本**: 全项目**只**被 `state/gen_netlist.py` 的一句注释提到,
   **不被任何闸调用** ⇒ 它现在 rc=1 (16 项 10 FAIL) 但**没人看得见**; 其中 C-16 标题是
   "板宽 12 → 15mm 的机械后果 (供老板拍板)" ⇒ ★**它在问一个老板 10-29 已经答完的问题**。

★★**核心仲裁 (本单最重要的一条): PIN-SET-2 孔位 Y 有两套互斥口径, 差 7.50mm, 且分属 hw-lead 自己的两个产物★★**
· **套 A (中心线平移, ±5.00 不变)**: S1(8,10) S2(52,20) —— 出处:
  `state/fragments/hw.yaml` 的 `pcb_mount_holes_xy` · `HW/hw_week_20261101_check.py`:55 的 `exp` ·
  `MECH/print/gen_print_pack_revb.py` (`pinset2_s1_y = 10.00`) · `MECH/print/MEASURE_CHECKLIST.md`:298 ·
  `MECH/_apply_iss017_answers.py` · 以及 `hw.yaml` 的 needs_from `iss118_pcb_holes_30mm_y` **明写**
  "Y 按中心线平移 (旧中心 7.50 → 新中心 15.00, **S 孔 ±5.00 不变**)"
· **套 B (保持绝对 Y)**: S1(8,2.50) S2(52,27.50) —— 出处:
  `HW/pcb60x30_check.py`:113-117 的 `HOLES` 与 `HW/pcb60x30_check.json` 的 `sec4_holes` (RK3576 段)
★**main 实测的物理后果 (30mm 板)**:
| 套 | S1/S2 孔心距板边 | 孔壁距板边 | S1→S2 距离 |
|---|---|---|---|
| A (10.00/20.00) | 8.00 | **7.30** | 45.12 |
| B (2.50/27.50) | 2.50 | **1.80** | 50.61 |
⇒ ★**打印包 (Rev B 笼 + 量测清单) 已按套 A 做出** (实测 `gen_print_pack_revb.py` 与 `MEASURE_CHECKLIST.md`:298 都是套 A);
  若 PCB 按套 B 钻 ⇒ **螺钉与笼差 7.50mm ⇒ 板装不进骨架**; 反之若 PCB 按套 A 而
  `pcb60x30_check.py`/`.json` 仍发套 B ⇒ ★**那份 JSON 是 ISS-118 的验收产物** ⇒ 下游按它做就错。
★**你只出机械侧结论 + 一份权威表**: 机械后果 (压装/笼孔/让过孔/打印包) 到底支持哪一套、依据是什么、
   被否掉的方案为什么否、**改了谁会受影响** —— 然后**用 frag_write.py 登记 needs_from → hw-lead**,
   把**要改的文件/行号/取值**写清楚。★**不许你改 HW/ 任何文件** (网表/板/原理图/生成器/HW 分片一律不许碰)。

★**顺带一条 (只报不改, 归 hw-lead / main)**:
main 实测: demo 板 (`HW/PCB/demo_mainboard.kicad_pcb`, 160×100mm) 里 **MountingHole footprint = 0 个**,
全板只有 2 个 np_thru_hole (USB-C 座自己的壳体柱); `HW/PCB/demo_mainboard_params.json` 声明 4 个
`[[3,3],[57,3],[3,42],[57,42]]` ⌀2.2, 但在 160×100 板上 X 只跨 54/160mm、Y 只跨 39/100mm
⇒ ★**像 60×45 时代的遗留坐标** (params 自己的 `_pending` 注释就写了"原 60×45 是骨架生成器时代的草案");
网表侧 0 行含固定孔/安装孔/keepout (cross_review C-11 实测 hits=0) ⇒ **原理图与网表都没有固定孔/keepout 行**
⇒ 板出来无从锁紧。★**只登记 needs_from (含你复核的坐标/直径/数量建议 + 依据), 不许改网表/板/params**。

★**交付物 (缺一不可)**
A. `MECH/BOARD_GEOM_30MM.md` (新建) —— **结构侧权威表**: 板框 60×30 / SoC RK3576 实际占位 / 逃线带 /
   PIN-SET-2 四孔 (含 **Y 口径仲裁结论 + 依据 + 被否方案 + 影响面**) / 打印包契约三条 WARN 的现行值
   ⇒ 每条标明**哪个产物用哪套、谁是下游真源**。
B. `MECH/pinset2_mech_check.py` 迁到 60×30 (常量 + **判据文案/判据本身一起改**) + 加 `--self-test`
   (**含反向用例**: 把某个孔挪进 SoC 逃线带 ⇒ 必须变红) ⇒ rc=0 且迁后判据与 A 的权威表一致。
C. `MECH/skeleton_section_check.py` 迁 30mm (`PCB_W` / `SOC_Y_LEN` / `HOT_BAND`) ⇒ 重出骨架宽与横向热扩散结论。
D. `MECH/cross_review_check.py`: C-16 改成 30mm 现状 (不再问已答完的 12→15) + `board_l` 76→60
   ⇒ 并**明确它是闸还是不是闸**: 要么接进闸, 要么写清为何不接 ⇒ ★**不许留一个没人看的孤儿红**。
E. `MECH/fit_check.py` / `MECH/hinge_usb_check.py` / `MECH/iss065_check.py` 三处 12/15mm 死常量:
   **逐个定性** (该迁 / 该标作废 / 只是文档引用) 并落成文字 + 必要的 needs_from ⇒ ★**不许闷头改数字了事**。
F. `HANDOFF/2026-11-11_mech-lead_ISS192_*.md` —— ★**B1~B6 六块齐全**
   (结论摘要 / 验收标准自评逐条 / 证据分级 / 接口取值声明 / 未决项与卡点 / 自证复现命令) ⇒ Q1 要 18/18。
G. `state/frag_write.py` 登记: needs_from → **hw-lead** (套 B 产物要改哪几行/取值/影响面) +
   needs_from → **main** (demo 板零安装孔/零 keepout 那条, 含你的坐标/直径/数量建议 + 依据)。

★**边界 (不许越)**
· 只写 `MECH/**` + `HANDOFF/**` + `state/fragments/mech.yaml` (★**必须走 `state/frag_write.py`**) + 你的交卷单。
· ★**不许碰** `HW/**` (网表 / 板 / 原理图 / 生成器 / HW 分片) · `state/issue_log.yaml` ·
  `PROJECT_TRACKER.md` §0 · **别人的分片** · `state/gen_*.py`。
· 板 md5 `611b869e13518c3c023fb178f91a0075` 与 `.kicad_pro` `3e504d2b` **一字不许动** (只读都不必去碰)。
· ★**不许联系供应商/原厂** (外发一律经项目总工)。
· ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标; ★**凡给出任何统计数必须同时给出口径**
  (哪个板宽 / 哪套孔位 / 含不含 DNP / 哪个 SoC) —— ★**只给数不给口径 = 会被当事实传下去**。
· 写分片**必须**用 `state/frag_write.py` (禁止 `open(p,"w")`)。

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 MECH/pinset2_mech_check.py            # rc=0, 且 FAIL/WARN 与 A 的权威表对得上
python3 MECH/pinset2_mech_check.py --self-test # rc=0, 且【反向用例】把孔挪进逃线带必须变红
python3 MECH/skeleton_section_check.py        # rc=0
python3 state/merge.py                        # rc 必须 0
python3 state/gate_check.py                   # Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb        # 必须仍 = 611b869e13518c3c023fb178f91a0075
```
★**交卷 ≤ 25 行** (结论先行; 逐条给复现命令与实测输出)。
"""

ISS192 = {
    "id": "ISS-192",
    "title": ("★★结构侧(MECH)机械复核器全线仍钉在已作废的 12/15mm 板宽 ⇒ 现在的绿灯不是关于现行板子说的"
              "(pinset2_mech_check rc=0 但那是块不存在的板) + PIN-SET-2 孔位 Y 在 hw-lead 自己两个产物里差 7.50mm"
              "(打印包已按套A做出, 若 PCB 按套B钻则装不进骨架) ⇒ 迁到 60×30 + 仲裁成一份权威表"),
    "severity": "high",
    "source_blocker": "MECH-B4",
    "source_agent": "main",
    "desc": (
        "★2026-11-11 13:4x~14:2x 项目总工实测开单 (★不是推测★)。\n"
        "★**根因 (为什么本单现在才存在)**: `advance.py --json` 的 A 段 (internal[]) **恒为空** ⇒ "
        "26 条 `open` 的 owner【全部】是 `main`/`boss` ⇒ 三个总工名下没有 open 单 ⇒ 自动派活无单可派 ⇒ "
        "本单按项目既有做法 (`_open_iss186_20261111.py` / `_open_iss190_20261111.py`) 由 main 开单并指派。\n"
        "★**发现的真问题 (四条硬证据, 全部 main 实跑)**:\n"
        "① **板宽已不是 15mm**: 老板 10-29 19:16 拍板 30mm, 板长 10-28 裁 60mm, §0 台账 11-01 20:5x 已订正 ⇒ "
        "12/15/76mm 全是死值。\n"
        "② ★**六个 MECH 脚本仍带死常量** (行号见任务书): pinset2_mech_check.py:44/50/56/59-63 · "
        "skeleton_section_check.py:45/53/55 · cross_review_check.py:36/37/38 · fit_check.py:55 · "
        "hinge_usb_check.py:45 · iss065_check.py:76。\n"
        "③ ★★**假绿**: pinset2_mech_check.py 现在输出 \"复算项 31 | FAIL 0 | WARN 3\" rc=0 ⇒ **它是在一块"
        "已经不存在的板子上亮绿灯**; main 实测迁到 30mm+RK3576 ⇒ FAIL 变 1, 且变红的那条判据本身就是 15mm 语义 "
        "(老口径 3/3 孔压逃线带 → 30mm 下只剩 2/3) ⇒ **只改常量不够, 判据要一起重推**。\n"
        "④ ★**cross_review_check.py 是孤儿脚本** (全项目只被 gen_netlist.py 一句注释提到, 不被任何闸调用) ⇒ "
        "它 rc=1 (16 项 10 FAIL) 没人看得见, 且 C-16 还在问老板 10-29 已答完的 12→15。\n"
        "★**核心仲裁**: PIN-SET-2 孔位 Y 两套互斥口径差 7.50mm —— 套A S1(8,10)/S2(52,20) (hw 分片声明 + "
        "hw_week_20261101_check.py + **打印包 RevB + MEASURE_CHECKLIST** + needs_from 明写的\"±5.00 不变\"规则) "
        "vs 套B S1(8,2.5)/S2(52,27.5) (HW/pcb60x30_check.py + 它的 .json, 而那份 .json 是 ISS-118 的验收产物) ⇒ "
        "main 实测 30mm 板上套B 孔壁距边仅 1.80mm (套A 7.30mm) ⇒ **两者不可能同时对**。\n"
        "★**主线口径**: 老板 11-11 10:07 ⇒ 当前主线 = 硬件原理图 demo 绘制; PCB 布线/布局类不派 ⇒ "
        "★**本单是【结构 / 网表接口 / 机械闸】类, 在优先派活范围内**, 且**全程不碰 PCB 布线/布局**。\n"
        "★**边界**: mech-lead 只出机械侧结论 + 权威表; **HW/ 一律不许改** ⇒ needs_from 报给 hw-lead / main。"
    ),
    "owner": "mech-lead",
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
        "★2026-11-11 13:4x 项目总工开单 (owner=mech-lead, verify_by=main ⇒ ★**自己修的必须别人验**, 铁律满足)。\n"
        "★**为什么这一单现在才派得出来**: 26 条 open 的 owner 全部是 main/boss ⇒ 三个总工名下没有 open ⇒ "
        "advance.py A 段恒空 ⇒ 自动派活无单可派 ⇒ 本单是 main 按项目既有做法开的**指派单**。\n"
        "★**为什么不派 PCB 类**: 老板 11-11 10:07 指令 —— PCB 布线/布局类一律【不派】(排队等原理图定稿); "
        "ISS-181 (hw-lead, 自研 demo 主板布线到可下单) ★**本轮按主线口径继续排队不派**。\n"
        "★**与在飞任务的并发安全 (实测)**:\n"
        "· hw-lead 正在跑**主线 6b (照尺子改生成器)** ⇒ 只碰 `state/gen_kicad_sch.py` + `demo_mainboard*.kicad_sch` "
        "+ `state/check_sch_pinfull.py` + `PIN_REALITY_GAP.md` ⇒ ★**与本单要动的 `MECH/**` 零文件交集** (实测 grep)。\n"
        "· 本单**不写** `HW/netlist_v1.csv` / `demo_mainboard.kicad_pcb` / 任何 `state/gen_*.py` ⇒ 无写冲突。\n"
        "★**验收**: main 会独立重跑本单贴的复现命令 + 跑反向用例 + 查 `merge.py` rc=0 与 `gate_check.py` Q1=18/18 "
        "⇒ ★**不采信自述**。"
    ),
    "task_brief": BRIEF,
}


def main() -> int:
    lock_fh = open(LOCK, "w")
    fcntl.flock(lock_fh, fcntl.LOCK_EX)
    try:
        with open(LOG, encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        items = list(doc.get("issues") or [])
        existing = {it.get("id") for it in items}
        if "ISS-192" in existing:
            print("ℹ️ ISS-192 已存在, 跳过 (幂等)")
            return 0
        items.append(ISS192)
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

        # dispatch_log 同步追加 (可追溯)
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-192", "agent": "mech-lead", "at": TODAY,
            "brief": BRIEF[:300],
        })
        fd, tmp2 = tempfile.mkstemp(dir=HERE, prefix=".dispatch_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp2, DL)
        except Exception:
            if os.path.exists(tmp2):
                os.unlink(tmp2)
            raise
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    print("✅ 已原子写 issue_log.yaml (flock + 锁内重读 + tmp/os.replace):")
    print("   - ISS-192 (owner=mech-lead, verify_by=main, due=2026-11-13, status=open)")
    print("     MECH 机械闸迁 60×30 + PIN-SET-2 孔位 Y 两套口径仲裁")
    print(f"   issue 总数: {len(items)}")
    print("   dispatch_log.yaml 已同步追加一条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
