#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开 ISS-194 (owner=hw-lead) —— 把 PIN-SET-2 孔位表从【套B】改成【套A】(结构侧已仲裁 + main 独立复核证实)

★**为什么现在开这一单**: ISS-192 (mech-lead) 2026-11-11 17:39 交卷, main 18:4x **独立验收签字 (verified/pass)**。
   结构侧把 PIN-SET-2 孔位 Y 的两套互斥口径 (差 7.50mm) 仲裁成一套 = **套A**,
   并用 `state/frag_write.py` 登记 needs_from → hw-lead (`iss192_pcb60x30_holes_set_b_to_set_a`):
   **只有 hw-lead 产物侧还没改** ⇒ 本单就是那"另一半"。

★**本单不是谁的意见冲突, 是 hw-lead 自己产物内部打架 (main 18:4x 逐条实测)**:
  ① `state/fragments/hw.yaml` 的 claim `pcb_mount_holes_xy` = **套A** (值 `P1(8,15)P2(52,15)S1(8,10)S2(52,20)`,
     note 明写"Y 按中心线平移 (旧中心 7.50 → 新中心 15.00, S 孔 ±5.00 不变)")
  ② `HW/hw_week_20261101_check.py`:51-56 = **套A**, 而且是**断言** (`new = {k: (x, y + (W/2.0 - 7.50))}` ⇒ exp 四孔)
  ③ **打印包 (Rev B) = 套A** —— ★**main 自己解析两个二进制 STL + 顶面占据栅格化 (0.5mm) 实测**:
     cage PCB 定位板 (板基线 Y=60) 与 coupon PCB 样板 (基线 X=4/Y=84) **实测四孔 =
     P1(8.00,15.00) ⌀2.4 + P2(52.00,15.00) ⌀2.4 + S1(8.00,10.00) ⌀1.6 + S2(52.00,20.00) ⌀1.6**
     ⇒ ★**套B 的 (8.00,2.50) / (52.00,27.50) 两个位置实测【实心无孔】** ⇒ ★**套B 与打印包不符**
     (另: 生成器常量 `pinset2_p_y=15.00 / s1_y=10.00 / s2_y=20.00`, `gen_print_pack_revb.py:93-95`, 与栅格实测逐值一致)
  ④ 结构侧权威表 `MECH/BOARD_GEOM_30MM.md` §4 = **套A** (main 已验收)
  ⑤ ★**唯一说套B 的**: `HW/pcb60x30_check.py`:113-117 的 `HOLES` + 它生成的 `HW/pcb60x30_check.json`
     (`sec4_holes` 的 RK3588 / RK3576 两段: S1 y=**2.5** / S2 y=**27.5**, edge_wall **1.80mm**)
     ⇒ ★**而那份 .json 是 ISS-118 的验收产物** ⇒ 下游按它做就错 ⇒ ★**必须改**。

★**几何自洽性 (不依赖打印包也成立)**: 套B 相对 30mm 新板中心 (Y=15.00) 的偏移 = S1 −12.50 / S2 +12.50
   ⇒ **不对称 + 两孔分离 25.00mm**; 而 15mm 老口径 (`HW/PCB_FIXING_PINSET2.md` §3.1: P1(8,7.50) P2(52,7.50)
   S1(8,2.50) S2(52,12.50)) 是**关于中心 7.50 的 ±5.00 对角分布** ⇒ 平移到 30mm 板 ⇒ **套A (分离仍 10.00, 仍对称)**。

★**主线口径**: 老板 11-11 10:07 ⇒ 当前主线 = 硬件原理图 demo 绘制; PCB 布线/布局类**不派**。
   ⇒ ★**本单不改板、不改网表、不改原理图、不碰布线/布局** ⇒ 只是**校验器里的孔位表 + 它的机读产物**
   ⇒ 属【机械接口 / 校验器一致性】类 ⇒ **在优先派活范围内**。

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
★**目标**: 把 **PIN-SET-2 孔位表从【套B】改成【套A】** —— 只改 `HW/pcb60x30_check.py` 的 `HOLES` 表
   + 重生成 `HW/pcb60x30_check.json` 的 `sec4_holes` (RK3588 / RK3576 **两段**) + 复核你其余产物里有没有同源的漂移值。
   ★**不改板、不改网表、不改原理图、不碰布线/布局**。

★**为什么 (★main 2026-11-11 18:4x 逐条实测, 不是推测★)**: 现在**你自己的产物内部打架** ——
| # | 产物 | 孔位口径 |
|---|---|---|
| ① | `state/fragments/hw.yaml` claim `pcb_mount_holes_xy` | ★**套A** (`P1(8,15)P2(52,15)S1(8,10)S2(52,20)`), note 明写"Y 按中心线平移 (旧中心 7.50 → 新中心 15.00, **S 孔 ±5.00 不变**)" |
| ② | `HW/hw_week_20261101_check.py`:51-56 | ★**套A** (而且是**断言**: `new = {k: (x, y + (W/2.0 - 7.50))}` ⇒ exp 四孔) |
| ③ | ★**打印包 Rev B (STL 实测)** | ★**套A** (见下) |
| ④ | `MECH/BOARD_GEOM_30MM.md` §4 (结构侧权威表, main 已验收签字) | ★**套A** |
| ⑤ | ★**`HW/pcb60x30_check.py`:113-117 + 它生成的 `HW/pcb60x30_check.json`** | ★★**套B** (S1 y=**2.5** / S2 y=**27.5**, `edge_wall` **1.80mm**) ⇒ ★**唯一说套B 的** |
⇒ ★**★那份 .json 是 ISS-118 的验收产物** ⇒ 下游按它做就错 ⇒ ★**必须改**。

★**③ 打印包 = 套A 是 main 自己测的 (★我没抄任何人的自述★)**: ★**main 纯 Python 解析了两个二进制 STL
   (`MECH/print/temple_cage_revb.stl` / `MECH/print/fit_coupon_revb.stl`) + 顶面占据栅格化 (0.5mm) 实测**:
   · cage 的 PCB 定位板 (板基线 Y=60) ⇒ **四个通孔 = P1(8.00,15.00) ⌀2.4 + P2(52.00,15.00) ⌀2.4 +
     S1(8.00,10.00) ⌀1.6 + S2(52.00,20.00) ⌀1.6**
   · coupon 的 PCB 样板 (基线 X=4 / Y=84) ⇒ **同一组值**
   · ★**套B 的 (8.00,2.50) / (52.00,27.50) 两个位置实测【实心无孔】** ⇒ ★**套B 与打印包不符**
   ★(注: 打印包是**包络多边形**切孔, 所以圆心靠栅格/弦宽反算, 不是找圆柱面 —— 你自己复核时别找圆面)
   ★另: 生成器常量 `pinset2_p_y=15.00 / pinset2_s1_y=10.00 / pinset2_s2_y=20.00`
   (`MECH/print/gen_print_pack_revb.py`:93-95) 与栅格实测**逐值一致**。

★**几何自洽性 (★不依赖打印包也成立★)**: 套B 相对 30mm 新板中心 (Y=15.00) 的偏移 = S1 **−12.50** / S2 **+12.50**
   ⇒ **不对称 + 两孔分离 25.00mm**; 而 15mm 老口径 (`HW/PCB_FIXING_PINSET2.md` §3.1: P1(8,7.50) P2(52,7.50)
   S1(8,2.50) S2(52,12.50)) 是**关于中心 7.50 的 ±5.00 对角分布** ⇒ 平移到 30mm 板 (中心 15.00)
   ⇒ **套A (分离仍 10.00, 仍对称)** ⇒ ★**套B 是「只改 Y」时的漂移产物, 不是平移**。

★**具体要改什么 (main 已定位到行, 你自己复核后再改)**
1. `HW/pcb60x30_check.py`:113-117 `HOLES` 四行 ⇒ ★**只改两个 Y**:
   `("S1", "压紧螺钉孔", (8.00, 2.50), 1.40, ...)` ⇒ **(8.00, 10.00)**
   `("S2", "压紧螺钉孔", (52.00, 27.50), 1.40, ...)` ⇒ **(52.00, 20.00)**
   ⇒ ★**P1(8.00,15.00) / P2(52.00,15.00) ⌀2.00 一律不动** (它们两套口径本来就一致)
2. ★**重生成 `HW/pcb60x30_check.json`** ⇒ `sec4_holes` 的 **RK3588 段 + RK3576 段**都要是套A
   ⇒ ★**验收看这三个数**: S1/S2 的 `y` = **10.0 / 20.0** · `edge_wall` 由 **1.80 → 7.30**
   (`edge_to_center` 8.00) ⇒ ★**且 `ov_escape_band` / `ov_pkg` / `ov_jchg_keepout` 仍全为 0.0**
   (结构侧已复算: 套A 四孔 × SoC 逃线带 2D 重叠 = **0.0000 mm²**)
3. ★**扫一遍你自己其余产物里有没有同源的漂移值** (★别只改这一处就收工★):
   `HW/PCB_FIXING_PINSET2.md` (§3.1 仍是 15mm 老板宽口径 —— ★**只报不改**, 改它要另开单) ·
   `HW/STEP1_LANDING_LIST.md` · `HW/PART_ALTERNATIVES_REGISTRY.md` · `state/fragments/hw.yaml` 的 note ·
   ★**凡"孔位 Y"相关的表格/清单/JSON, 一律核一遍值** ⇒ ★**有漂移就列清单报给 main** (不要顺手改无关文件)。

★**验收自证 (交卷前跑, 把输出贴进回复)**
```
python3 HW/pcb60x30_check.py                 # rc=0, 且 sec4_holes 两段 S1/S2 的 y = 10.0 / 20.0
python3 -c "import json;d=json.load(open('HW/pcb60x30_check.json'));print({s:{k:(v['x'],v['y'],v.get('edge_wall')) for k,v in d['sec4_holes'][s]['holes'].items()} for s in ('RK3588','RK3576')})"
python3 HW/hw_week_20261101_check.py         # rc=0 (它本来就断言套A ⇒ 改完两边必须一致)
python3 MECH/pinset2_mech_check.py           # rc=0 (结构侧闸; 改完必须仍绿)
python3 state/merge.py                       # rc 必须 0 (冲突 0)
python3 state/gate_check.py                  # Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv   # 必须一字未变 (611b869e… / 网表 md5 见项目基线)
```
★**交卷 ≤ 20 行** (结论先行; 逐条给复现命令与实测输出; ★**列清你扫过哪些文件、哪些有漂移**)。

★**边界 (不许越)**
· ★**只写**: `HW/pcb60x30_check.py` + `HW/pcb60x30_check.json` + ★**必要时** `state/fragments/hw.yaml`
  (走 `state/frag_write.py`; ★**只许订正 note/值, 不许动别的 key**)。
· ★**不许碰**: `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/PCB/demo_mainboard.kicad_pcb` ·
  `HW/PCB/demo_mainboard*.kicad_sch` · 任何 `state/gen_*.py` · `PROJECT_TRACKER.md` §0 ·
  **别人的分片** · `state/issue_log.yaml` (★**改 issue 状态是 main 的活**)。
· ★**不许联系供应商/原厂** (外发一律经项目总工)。
· ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标; ★**任何统计数必须同时给口径** (哪块板 / 哪套孔位 / 哪个 SoC)。
· ★**不要自己改板**: demo 板 (160×100) 实测 **MountingHole = 0** + `params.json` 里有 4 个 60×45 时代的遗留孔坐标
  ⇒ ★**那是布局类, 按老板 11-11 10:07 口径【不派】(排队等原理图定稿)** ⇒ ★**本单不许碰它**, 由 main 裁。
"""

ISS194 = {
    "id": "ISS-194",
    "title": ("★★PIN-SET-2 孔位表【套B ⇒ 套A】: hw-lead 自己 5 个产物里 4 个写套A, 只有 pcb60x30_check.py + "
              "它的 .json 写套B (S1 y=2.5 / S2 y=27.5, 孔壁距边只剩 1.80mm) ⇒ 而那份 .json 是 ISS-118 的验收产物 "
              "⇒ 若 PCB 按套B 钻, 螺钉与打印包笼孔差 7.50mm ⇒ 板装不进骨架"),
    "severity": "high",
    "source_blocker": "MECH-B4",
    "source_agent": "main",
    "desc": (
        "★2026-11-11 18:4x 项目总工开单 (★依据 = ISS-192 交卷 + main 独立验收签字 + main 自己实测★)。\n"
        "★**ISS-192 已于 18:4x 经 main 独立验收签字 (verified/pass)**: 结构侧把 PIN-SET-2 孔位 Y 的两套互斥口径\n"
        "  (差 7.50mm) 仲裁成一套 = **套A**, 并登记 needs_from → hw-lead (`iss192_pcb60x30_holes_set_b_to_set_a`)。\n"
        "★**main 自己实测的『套B 是孤例』 (不是抄任何人的自述)**: ① hw.yaml claim `pcb_mount_holes_xy` = 套A\n"
        "  ② `HW/hw_week_20261101_check.py`:51-56 = 套A 且是断言 ③ **打印包两个 STL 的顶面占据栅格化 (0.5mm)\n"
        "  实测四孔 = 套A, 套B 位置实心无孔** ④ 结构侧权威表 = 套A\n"
        "  ⇒ ★**唯一说套B 的 = `HW/pcb60x30_check.py`:113-117 + 它的 `.json` (sec4_holes 两段)**。\n"
        "★**几何自洽性 (不依赖打印包)**: 套B 相对新中心 (Y=15.00) 偏移 S1 −12.50 / S2 +12.50 ⇒ 不对称 + 分离 25.00mm;\n"
        "  而 15mm 老口径是关于中心 7.50 的 ±5.00 对角分布 ⇒ 平移到 30mm 板 ⇒ 套A (分离仍 10.00, 仍对称)\n"
        "  ⇒ ★**套B = 「只改 Y」时的漂移产物, 不是平移**。\n"
        "★**后果**: 套B 的 S1/S2 孔壁距板边只剩 **1.80mm** (套A 7.30mm) + 叠加 ISS-049 §5 的 ⌀3.0 让位孔\n"
        "  ⇒ 孔缘距板边只剩 **1.00mm ⇒ 破边**; 且 ★**打印包笼孔已是套A** ⇒ 按套B 钻 ⇒ 螺钉穿实心板 ⇒ 装不进骨架。\n"
        "★**主线口径**: 老板 11-11 10:07 ⇒ 当前主线 = 硬件原理图 demo 绘制; PCB 布线/布局类不派\n"
        "  ⇒ ★**本单只改校验器里的孔位表 + 它的机读产物, 不改板/网表/原理图, 不碰布线布局** ⇒ 在优先派活范围内。\n"
        "★**边界**: 只写 `HW/pcb60x30_check.py` + `.json` (+ 必要时 hw.yaml 的 note, 走 frag_write.py);\n"
        "  ★**不许碰网表/板/原理图/gen_*.py/§0 锁死表/别人的分片/issue_log**; ★**不许联系供应商**。"
    ),
    "owner": "hw-lead",
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
        "★2026-11-11 18:4x 项目总工开单 (owner=hw-lead, verify_by=main ⇒ ★**自己修的必须别人验**, 铁律满足)。\n"
        "★**来源**: ISS-192 (mech-lead) 交卷 ⇒ main 18:4x 独立验收签字 (verified/pass) ⇒ 结构侧登记的\n"
        "  needs_from `iss192_pcb60x30_holes_set_b_to_set_a` 的另一半 ⇒ ★**本单就是那『另一半』**。\n"
        "★**为什么不派 PCB 类**: 老板 11-11 10:07 指令 —— PCB 布线/布局类一律【不派】(排队等原理图定稿);\n"
        "  ★**本单只改校验器里的孔位表 + 机读产物, 不碰布线/布局** ⇒ 不违反主线口径。\n"
        "★**与在飞任务的并发安全 (实测)**: hw-lead 正在跑 **ISS-193** (29 个器件真实脚数) ⇒ ★**那个单只碰\n"
        "  BOM/封装/脚数来源, 不碰 `HW/pcb60x30_check.py`** ⇒ ★**零文件交集**; 且 ★**一个 agent 同时只允许一个\n"
        "  写会话** ⇒ ⇒ 本单 status=open, ★**等 ISS-193 交卷后由 advance.py 自动派出**, 不手动并发派。\n"
        "★**验收**: main 会独立重跑本单贴的复现命令 + 复核 json 两段的 S1/S2 y/edge_wall + 查 merge rc=0 与\n"
        "  gate_check Q1=18/18 ⇒ ★**不采信自述**。"
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
        if "ISS-194" in existing:
            print("ℹ️ ISS-194 已存在, 跳过 (幂等)")
            return 0
        items.append(ISS194)
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

        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-194", "agent": "hw-lead", "at": TODAY,
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
    print("   - ISS-194 (owner=hw-lead, verify_by=main, due=2026-11-13, status=open)")
    print("     PIN-SET-2 孔位表 套B ⇒ 套A (只改 pcb60x30_check.py + .json)")
    print(f"   issue 总数: {len(items)}")
    print("   dispatch_log.yaml 已同步追加一条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
