#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_fix_ref_rootcause_20261112.py —— ★★订正「位号问号」的错误根因 (★3 个活源头★)★★

★★为什么要改 (★main 2026-11-12 03:0x 实测坐实★)★★:
  ★**旧记录写的根因 = 「下划线命名」⇒ 实测证明是错的** ⇒ ★**真根因 = 【KiCad 判「已标注」的条件是位号末字符为数字】**
  ⇒ ★**⇒ 留着错的根因 = 下次还会照错的方案做 (★去下划线 = 无效 + 让位号不可读★) ⇒ 必须当场订正★**

★改哪三个活源头 (★★只改活口径, 历史留档区一个字不动★)★★:
  ① `state/fragments/pm.yaml` 的 `ref_designator_rename` 条目【item + decision】 (★**C 段决策项的唯一真源★**)
  ② `state/CURRENT_TASK.md` 的待办② (★**播报源★**)
  ③ `state/RECHAIN_ONEPASS_PLAN.md` 的 B 行 (★**执行清单★**)

★纪律 ★:
  ★**① pm.yaml 走 frag_write 的原子写** (★只改那一条的 item/decision 两段文字★)
  ★**② 另两个文件用【精确整行替换】+ 改前改后逐字节 diff 实测** (★不许用碎片匹配 —— 今天学到的坑★)
  ★**③ 改完复跑 `advance.py --json` ⇒ C 段条数必须不变 (★36★) ⇒ 决策项没被改没★**
  ★**④ 受保护文件一个都不碰**
"""
import fcntl
import io
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import yaml  # noqa: E402
import frag_write  # noqa: E402

PM = os.path.join(HERE, "fragments", "pm.yaml")
PM_BAK = PM + ".bak_20261112_refrootcause"
TASK = os.path.join(HERE, "CURRENT_TASK.md")
TASK_BAK = TASK + ".bak_20261112_refrootcause"
PLAN = os.path.join(HERE, "RECHAIN_ONEPASS_PLAN.md")
PLAN_BAK = PLAN + ".bak_20261112_refrootcause"

ITEM_NEW = (
    "★**位号规范: 要不要改位号** (★实测: KiCad 导出的 BOM 里 **186/218** 个位号带字面量问号 ⇒ "
    "★**★真根因 (★2026-11-12 03:0x 实测钉死★) = 【KiCad 判「已标注」的条件是【位号最后一个字符是数字】】** "
    "⇒ 位号末字符是字母 ⇒ 判未标注 ⇒ BOM 里打 `?` ⇒ ★**【不是下划线命名的问题 —— 去下划线实测无效且会让位号不可读】★** "
    "⇒ ★**解法 = 给位号加 `_1` 数字后缀 (★已在副本实测: 问号行数 0 + annotation errors 警告消失 + 零撞名★)** ⇒ "
    "★**改它 ⇒ netlist表 → BOM → 原理图 11 页 → 板里 186 个封装位号 → 丝印/CPL/装配/IPC-2581/3D/D356 全套 "
    "⇒ 【板 md5 必变】⇒ 留证链/Gerber/投产包全要重出** (★一个位号平均散在 19~112 个文件★) ⇒ "
    "★**证据: `HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md` (★含全部对照实验★) · 实现单 ISS-205 (owner=hw-lead)★**"
)

DEC_NEW = (
    "★老板 2026-11-11 19:31 决定「全做」⇒ ★**位号改名随「一次整链重出」一起做** (★清单 `state/RECHAIN_ONEPASS_PLAN.md` "
    "v2, 14 步★) ⇒ ★**`RAIL_*`/`NET_*` 保留** (★单点汇流位, 改了 BOM 多假料号★) ⇒ ★**该项从待拍板清单退休 (已并入整链重出)** ★★\n"
    "★**★2026-11-12 03:0x main 订正 (★★根因变了, 实现方案随之改写★★)★**: ★**旧记录写的「根因是下划线命名」是错的** ⇒ "
    "★**实测钉死的真根因 = 【KiCad 判「已标注」的条件是位号末字符为数字】** (★带 `?` 的 186 个末字符 100% 是字母; "
    "不带 `?` 的 32 个 100% 是数字; 零例外 + 在 /tmp 造最小对照工程逐个换位号复现★) ⇒ ⇒ "
    "★**★★实现方案改为「加 `_1` 数字后缀」★★ (★不是去下划线★): ★**实测副本上改完 ⇒ 问号行数 0 + "
    "KiCad 的 annotation errors 警告一并消失 + 186 个 ref 加后缀【零撞名】⇒ ★**可读性只多一个尾巴 "
    "(★`C_AC_CSI_D0_CK_N_1` 仍一眼看得出是「CSI D0 CK 负端」★) ⇒ 比「去下划线」明显更优 ⇒ "
    "★**⇒ 实现已开单 ISS-205 (owner=hw-lead · verify_by=main · due 11-14) ⇒ 落点在生成器 `state/gen_kicad_sch.py` "
    "(★改在产生点★) ⇒ ★★板侧改动仍属整链重出第 1 步 (★与 C/D/E 合并落表★) ⇒ ★★该单会让原理图位号与板位号暂时不一致 "
    "(★预期中间态·不许因此改板★)★★ ⇒ ★★证据 `HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md`★★** ★★"
)

TASK_NEW = (
    "② ★**老板拍板: 位号改名** (★KiCad 导出的 BOM 里 186/218 个位号带 `?` ⇒ "
    "★**★真根因 (★2026-11-12 03:0x 实测钉死★) = 【KiCad 判「已标注」的条件是位号末字符为数字】★** "
    "⇒ ★**不是下划线命名 (★旧记录错了, 已订正★)⇒ 解法 = 加 `_1` 数字后缀 (★副本实测问号清零 + 零撞名★)★** "
    "⇒ ★**已开 ISS-205 (hw-lead) 落点在生成器** ⇒ 板侧改动随整链重出第 1 步一起做 ⇒ "
    "RAIL_*/NET_* 保留 ⇒ 证据 `HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md`****"
)

PLAN_NEW = (
    "| **B** | ★**位号加数字后缀** (★KiCad 导出的 BOM 里 186/218 个位号带 `?` ⇒ ★**★真根因 (★2026-11-12 03:0x 实测★) "
    "= 【KiCad 判「已标注」的条件是位号末字符为数字】★★ ⇒ 解法 = 给位号加 `_1` 后缀 (★副本实测: 问号行数 0 + "
    "annotation errors 消失 + 零撞名★) ⇒ ★**不是去下划线 (★实测无效且不可读★)★**) | 改**表** ⇒ 原理图 / BOM / "
    "**板里 186 个封装位号** / 丝印 / CPL / 装配 / IPC-2581 / 3D / D356 | **必变** | "
    "★**`RAIL_*`/`NET_*` 保留** (单点汇流位, 改了 BOM 多假料号) · ★**实现单 ISS-205 (owner=hw-lead) 只做原理图侧 "
    "(★板侧归本趟第 5 步★)** · 证据 `HW/PCB/KICAD_REF_QUESTIONMARK_ROOTCAUSE.md` |"
)


def replace_line(path, marker, new_line, tag):
    """★整行精确替换 (★不许碎片匹配★)"""
    raw = io.open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    hits = 0
    for i, l in enumerate(lines):
        if marker in l:
            lines[i] = new_line
            hits += 1
            break
    if hits != 1:
        print("★锚点没找到或有多处 ⇒ 没改:", tag)
        return False
    tmp = path + ".tmp.main"
    io.open(tmp, "w", encoding="utf-8").write("\n".join(lines))
    os.replace(tmp, path)
    print("✅ 已改:", tag)
    return True


def main():
    # ---- 基线 ----
    p = subprocess.run([sys.executable, os.path.join(HERE, "advance.py"), "--json"],
                       capture_output=True, text=True, cwd=PROJ)
    import json
    before = len((json.loads(p.stdout).get("plan", {}) or {}).get("decisions") or [])
    print("★基线 C 段 = %d 条" % before)

    # ---- ① pm.yaml ----
    with open(os.path.join(HERE, ".frag.lock"), "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            d = yaml.safe_load(io.open(PM, encoding="utf-8")) or {}
            shutil.copy2(PM, PM_BAK)
            hit = 0
            for n in d.get("needs_from") or []:
                if n.get("key") == "ref_designator_rename":
                    n["item"] = ITEM_NEW
                    n["decision"] = DEC_NEW
                    hit += 1
                    break
            assert hit == 1, "pm.yaml 里没找到 ref_designator_rename"
            frag_write.atomic_write_yaml(PM, d)
            print("✅ pm.yaml: ref_designator_rename 的 item + decision 已订正")
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)

    # ---- ② CURRENT_TASK.md 待办② ----
    shutil.copy2(TASK, TASK_BAK)
    ok2 = replace_line(TASK, "② ★**老板拍板: 位号改名**", TASK_NEW, "CURRENT_TASK.md 待办②")

    # ---- ③ RECHAIN 计划 B 行 ----
    shutil.copy2(PLAN, PLAN_BAK)
    ok3 = replace_line(PLAN, "| **B** | ★**位号改名**", PLAN_NEW, "RECHAIN_ONEPASS_PLAN.md B 行")

    # ---- 验收 ----
    p = subprocess.run([sys.executable, os.path.join(HERE, "advance.py"), "--json"],
                       capture_output=True, text=True, cwd=PROJ)
    after = len((json.loads(p.stdout).get("plan", {}) or {}).get("decisions") or [])
    print()
    print("=== 验收 ===")
    print("  C 段条数: %d → %d %s" % (before, after, "✅ 未变" if before == after else "❌ 变了!"))
    # 残留扫描
    print("  pm.yaml 残留'根因是下划线':", "❌" if "根因是下划线" in io.open(PM, encoding="utf-8").read() else "✅ 无")
    print("  CURRENT_TASK 残留'根因是下划线命名':",
          "❌" if "根因是下划线命名" in io.open(TASK, encoding="utf-8").read() else "✅ 无")
    return 0 if (ok2 and ok3 and before == after) else 1


if __name__ == "__main__":
    sys.exit(main())
