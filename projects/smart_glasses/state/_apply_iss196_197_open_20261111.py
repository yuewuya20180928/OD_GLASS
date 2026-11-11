#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""开 ISS-196 (sw-lead) + ISS-197 (mech-lead) = 两个空闲总工的下一条 (2026-11-11 21:0x, 项目总工 main)

★**为什么开这两条 (★实测, 不是推测★)**:
  · `state/advance.py --json` 的 A 段 (internal) = **0 条** ⇒ 队列对 sw-lead / mech-lead 是空的
    ⇒ ★**这两个总工本轮【一条 open 待办都没有】** ⇒ 再没有新单, 下轮 cron 依然 A 段空 ⇒ ★**队列要断线了** ★
  · ★**而 hw-lead 不是"空"**: 它有 ISS-193 (`fixing`) + **一条活着的会话** (实测 `agent:hw-lead:subagent:fccbbd04-...`
    的 transcript 末行时间戳 21:03:53, `state/gen_bom.py` mtime 21:03:53) ⇒ ★**铁律「一个 agent 同时只允许一个写会话」⇒ 不动它** ★
    ⇒ ★**ISS-136 / ISS-195 两条 open 继续等它交卷 (advance.py 的 in_flight 规则会自动挡住)** ★
  · ⇒ ★**本脚本只补 sw-lead 与 mech-lead 这两个【真空闲】的槽位** ★

★**★为什么这两条单的内容是"订正已过期的账"而不是"新功能" (★这就是主线口径的活儿★)**:
  · ★**sw-lead**: 两条【逾期 6 天】的 P0 needs_from (`demo_od_p0_1_rk3572_target` / `demo_od_p0_3_build_env`)
    的【前提已被实测推翻】⇒ ★**需求_from 的核法本身跑不通 (`RKNN.RKNN_TARGET_PLATFORM` 属性不存在)** ⇒
    ★**⇒ ISS-145 (demo 模型路线 M1/M2) 至今缺一页事实底座** ⇒ ★**主线下一件就是它** ★
  · ★**mech-lead**: 套A 孔位【昨天 20:0x 已由 hw-lead 落地】⇒ ★**结构侧 5 处记录还停在"套B 仍是活口径"**
    (含 §9 U-3 那条"是否落地") ⇒ ★**⇒ 口径分裂的复发点** ★ (MEMORY: 两套口径打架 ⇒ 白干两遍)

★**落账纪律 (与项目既有范式一致)**:
  ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** (⇒ 除新增两条外, 一个字节都不许动) ⇒ 通过才写
  ③ 原子写: tmp (同目录) → fsync → os.replace → fsync(dir)
  ④ ★**只新增两条 dict** (不改任何既有条目的任何字段) ★

★**边界**: 不改 §0 锁死表 · 不改任何已发布数字 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 / 不下采购单
"""
from __future__ import annotations

import fcntl
import hashlib
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-11"
DUE = "2026-11-13"

BRIEF_196 = """★**目标 (★内部活·不是原厂的事★)**: 把两条【已逾期 6 天】的 P0 needs_from 的【前提用实测钉死】, 并把模型台账 sha 漂移修掉 ⇒ ★**给 ISS-145 (demo 模型路线 M1/M2) 攒一页可决策的事实底座** (★**不替老板拍板, 只给事实与后果★**)。

★**★为什么现在做 (★main 2026-11-11 21:0x 沙盒实测, 不是推测★)**: ★**这两条 need 的前提已被实测推翻** ⇒ ★**再挂着, 下一个读它的人会按错前提做决策** ★

★**★① `demo_od_p0_1_rk3572_target` 的核法本身跑不通 (实测)** ★:
· ★**`RKNN.RKNN_TARGET_PLATFORM` 这个属性【不存在】** (实测 `AttributeError: type object 'RKNN' has no attribute 'RKNN_TARGET_PLATFORM'`) ⇒ ★**need 里写的核法必定报错** ⇒ ★**核法要改成【读支持清单 + 全库 grep】** ★
· ★**真核法 (两条, 都实测过)**: ① `grep -n "currently support" ~/miniconda3/envs/rknn/lib/python3.10/site-packages/rknn/api/rknn.py` ⇒ 支持清单在★**第 88-89 行**; ② `grep -rl "rk3572" ~/miniconda3/envs/rknn/lib/python3.10/site-packages/rknn/` ⇒ ★**0 命中** ★
· ★**该清单实测内容 = rv1103 / rv1103b / rv1106 / rv1106b / rv1126b / rk2118 / rk3562 / rk3566 / rk3568 / rk3576 / rk3588** ⇒ ★**rk3572 不在其中** ⇒ ★**⇒【本机 2.3.2 工具链【不能直接以 rk3572 为 target_platform 出产物】★** ★

★**★② `demo_od_p0_3_build_env` 说【本机缺工具链/ONNX/校准集】⇒ 已被推翻 (实测全部在位)** ★:
· `~/miniconda3/envs/rknn/lib/python3.10/site-packages/rknn_toolkit2-2.3.2.dist-info` ⇒ ★**工具链在 (2.3.2)** ★
· `~/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx` (★29,365,856 B★) + `yolov5n-sim.onnx` (★7,931,774 B★) ⇒ ★**源 ONNX 在** ★
· `~/Public/radxa_yolo/calib_yolov5_100/` ⇒ ★**恰好 100 张 jpg 在** ★
· `/work/object_detection/data/coco/raw/val2017/` ⇒ ★**5000 张在**; `.../annotations/instances_val2017.json` ⇒ ★**19,987,840 B 在** ★
· ⇒ ★**构建环境【已恢复】⇒ 这条 need 的内容已过期 ⇒ 应当【回答 + 退休】, 而不是继续挂着当活账** ★

★**★③ 模型台账漂移 (实测)**: `python3 SW/tools/rknn_bench.py probe` ⇒ ★**rc=0** ⇒ 但输出 ★**「模型 sha16 = 1e2c716bd16ed9d3 (台账一致: False)」**★ ⇒ 而 `SW/RKNN_BENCH.md` ★**第 473 行★** 记的台账 sha16 是 ★**`20368be665f6f59a`**★ ⇒ ★**⇒ 两处对不上 ⇒ 要钉死【哪个是权威 + 为什么】⇒ 目标: probe 打出【台账一致: True】** ★

★**你要做的三件 (★按顺序做, 每做完一件立刻落盘 ⇒ 宁可交一半也不要交零★)**:
★**A. 出事实页** (★新建 `HANDOFF/2026-11-11_sw-lead_ISS196_rknn台账与rk3572结论.md★`): ① rk3572 在 2.3.2 的支持结论 + 核法 + 原始输出 (贴命令与输出, 别只写结论) ② 构建环境现状清单 (路径 + 文件数 + 字节数, 逐项贴实测) ③ 模型 sha 台账: 哪个是权威 + 依据 + 为什么两边曾对不上
★**B. 修台账 + 答两条 need**: ① 改 `SW/RKNN_BENCH.md` ★**第 473 行那一处** (★**只许改这一处, 其它段落一字不动★**) 使 `probe` 打出【台账一致: True】⇒ ★**若你发现台账权威应是另一个 sha ⇒ 先在事实页写清理由, 再改★** ② 用 `state/frag_write.py --agent sw` 回答两条 need (`key=demo_od_p0_1_rk3572_target` / `key=demo_od_p0_3_build_env`, `to=main`, `value=你的结论`) ③ 更新 `state/fragments/sw.yaml` 的 `interface_claims` 里 `rknn_target_platform` 这条 (★只许新增/订正这一条, 不许删改别人的 key★)
★**C. 给 main 一页 ISS-145 的决策底座** (★写在同一份事实页里, ★**只列事实与后果, 不替老板拍板, 不许改 ISS-145 的状态★**): 在【2.3.2 无 rk3572 target_platform】这个实测前提下, M1 (直接复用 A7S 的 .rknn 产物, 零转换) 与 M2 (yolov5n 需重转 + 重评精度) ★**各自还差什么 / 差多少 / 谁挡着** ⇒ ★**结论按老板 11-11 19:31 口径【信不批 ⇒ 缺口自己网上查 + 标证据等级】处理, 不许说【等回信】** ★

★**验收自证 (交卷前跑, 把输出贴进回复) ★:
```
python3 SW/tools/rknn_bench.py probe          # ★rc=0 且【台账一致: True】
python3 state/merge.py                         # ★rc 必须 0 (冲突 0)
python3 state/gate_check.py                    # ★Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv   # ★必须一字未变 (611b869e… / c78f9912…)
```

★**交卷 ≤ 15 行** (结论先行 + 三件逐条一句话 + 上面命令的实测输出)

★**边界 (不许越) ★:
· ★**只写**: ★新建 `HANDOFF/2026-11-11_sw-lead_ISS196_rknn台账与rk3572结论.md` + `SW/RKNN_BENCH.md` (★**只许改第 473 行那一处★**) + `state/fragments/sw.yaml` (★走 `state/frag_write.py`, ★只许动 `rknn_target_platform` 那一条 claim + 新增那两条 answer★)
· ★**不许碰**: `HW/**` (板/网表/原理图/BOM 一律只读) · `SW/tools/**` (★**只许【跑】rknn_bench.py, 不许改它★**) · `SW/MODEL_ASSETS.md` · `state/gen_*.py` · `state/issue_log.yaml` (★改 issue 状态是 main 的活★) · **别人的分片** (hw.yaml / mech.yaml / pm.yaml)
· ★**不许联系供应商/原厂/服务商** (★外发一律经项目总工★) · ★**不许发任何邮件** ★
· ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标; ★**任何统计数必须同时给口径** (哪块板/哪个口径/何时) ★
· ★**不许用推算冒充实测**: 台账一致 False 这条是【实测】(probe 输出), 「rk3572 不受支持」是【实测】(docstring + grep), 「所以 M1 不成立」是【推算】⇒ ★**三者必须分开标** ★
"""

BRIEF_197 = """★**目标 (★内部活·不是原厂的事★)**: 套A 孔位【昨天 20:0x 已由 hw-lead 落地】⇒ ★**结构侧 5 处记录还停在「套B 仍是活口径」** ⇒ ★**把结构侧口径收敛成一套, 并把 3 条给 main 的未决项整理成一页带数字的选项表** ⇒ ★**不许改任何几何数字, 不许碰板与网表**。

★**★为什么现在做 (★main 2026-11-11 21:0x 沙盒实测, 不是推测★)** ★:
· ★**实测: `HW/pcb60x30_check.py` 的 `HOLES` 表现在已经是套A** (★S1 = (8.00, 10.00) / S2 = (52.00, 20.00), ★表上方注释明写「套 B ... 已否决」★) ⇒ ★**⇒ 而 `MECH/BOARD_GEOM_30MM.md` 还在说它是套B** ⇒ ★**⇒ 口径分裂的复发点** ★ (MEMORY: 两套口径打架 ⇒ 白干两遍)
· ★**实测: `HW/pcb60x30_check.json` 的 `sec4_holes` 现在也是套A** (★「孔心 (8.00,10.00) ⌀1.40」★) ⇒ ★**⇒ §6/§7 的影响面表也跟着过期了** ★

★**★你必须先自己核对这 5 处 (★main 给的是行号线索, 你要自己 grep 定位, 行号可能已漂★)** ★:
1. `MECH/BOARD_GEOM_30MM.md` §5.2 的 **W-2** 行: 现在写「硬件侧口径分歧: `HW/pcb60x30_check.py` 的 HOLES 仍是套 B」⇒ ★**已不成立** ★
2. 同文件 §4.1 两套对照表的 **套B 那一行的「出处」列**: 现在指向 `HW/pcb60x30_check.py` 的 `HOLES` + `HW/pcb60x30_check.json` 的 `sec4_holes` ⇒ ★**而那两处现在都是套A ⇒ 出处自相矛盾** ★
3. 同文件 §6「唯一不一致的产物」那段: 现在写「唯一不一致的产物 = `HW/pcb60x30_check.py` + `HW/pcb60x30_check.json`」⇒ ★**已不成立** ★
4. 同文件 §7 影响面表里那两行「`HW/pcb60x30_check.py` / `.json` 套 B → 改 → 套 A, owner hw-lead」⇒ ★**已完成** ★
5. 同文件 §9 **U-3**: 「套 B → 套 A 订正是否落地 (owner hw-lead)」⇒ ★**答案是【已落地】⇒ 这条未决项可以关** ★

★**你要做的三件 (★按顺序做, 每做完一件立刻落盘 ⇒ 宁可交一半也不要交零★)** ★:
★**A. 订正这 5 处 + 扫老口径**: ① 把上面 5 处按【套A 已落地】订正 (★**只许改这 5 处 + §9 U-3 那一行的状态, 其它章节一字不动★**) ⇒ ★**套B 那一行【不许删】** ⇒ ★**保留它 + 标注「已否决 (套B) · 仅留档」** (★它是你自己仲裁的依据, 删了就没人知道为什么否它★) ② ★**全仓扫 `MECH/**` 里还在引 15mm / 12mm / 板长 50 / 板长 76 老口径的地方, 逐条定性两类**: 【★历史留档★ (原文保留 + 加一句「已作废 · 仅留档」+ 指向现行口径) vs 【★活口径 (必须改)★】⇒ ★**清单写进交卷报告, 活口径的那几条【只报给 main, 不许自己改】(★别越界改别人的地界★)】 ★
★**B. 关掉那条 numpy 阻塞 (★实测已不成立★)**: 你分片里的 `mech_numpy_dep_for_print_check` 说「本机 python3.14 无 numpy 且装不上」⇒ ★**实测: `numpy 2.5.4` 现在装上了, `python3 MECH/dfm_check.py` rc=0, `python3 MECH/print/verify_pack_revb.py` rc=0 (合计 38/38 点一致) ★** ⇒ ★**⇒ 真正的剩余阻塞不是 numpy, 是【量产外形件模型还没做】(★Rev B 打印包是检具+试样, 不含量产外壳 ⇒ 脱模面级统计【仍 0 个数据点】★) ⇒ ★**请用 `state/frag_write.py --agent mech` 把这条 need 的内容改成现况 + 真阻塞, 并注明 numpy 已恢复** ★
★**C. 给 main 一页未决项选项表** (★新建 `HANDOFF/2026-11-11_mech-lead_ISS197_口径收敛与未决项选项表.md★`): 把【U-1 金属骨架超重 (最好 4.08 g/对 vs 预算 3 g)】/【U-2 石墨满板 2.16 g/对 > W11 上限 2 g】/【U-5 demo 板安装孔 (删 / 改 M3)】+ ★**ISS-127 交卷留给你那三条 (mech_iss127_temple_split / mech_iss127_graphite_cut / mech_iss127_graphite_in_hchain)★** ★**合并成一页** ⇒ ★**每条给: 现状数字 (带口径) + 至少 2 个可选项 + 每个选项的【代价 (重量/件/钱)】+ 你推荐哪个 + ★**不改任何已冻结口径, 不替 main 拍板** ★

★**验收自证 (交卷前跑, 把输出贴进回复) ★:
```
python3 MECH/pinset2_mech_check.py             # ★rc=0 (复算项 38 | FAIL 0 | WARN 2)
python3 MECH/dfm_check.py                      # ★rc=0 (★面级统计能跑 ⇒ numpy 已恢复的证据★)
python3 MECH/print/verify_pack_revb.py         # ★rc=0 (合计 38/38 点一致)
python3 state/merge.py                         # ★rc 必须 0 (冲突 0)
python3 state/gate_check.py                    # ★Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv   # ★必须一字未变 (611b869e… / c78f9912…)
```

★**交卷 ≤ 15 行** (结论先行 + 三件逐条一句话 + 上面命令的实测输出)

★**边界 (不许越) ★:
· ★**只写**: ★新建 `HANDOFF/2026-11-11_mech-lead_ISS197_口径收敛与未决项选项表.md` + `MECH/BOARD_GEOM_30MM.md` (★**只许动上面点名的 5 处 + §9 U-3 那一行, 其它章节一字不动★**) + `state/fragments/mech.yaml` (★走 `state/frag_write.py`, ★只许动 `mech_numpy_dep_for_print_check` 那一条 need + 新增一条 answer, 不许删改别人的 key★)
· ★**不许碰**: `HW/**` (板/网表/原理图/BOM/脚本一律只读) · `HW/iss121_mic_magnet_check.py` / `HW/iss121_mic_magnet_check.json` / `HW/ISS121_MIC_MAGNET_POSITION.md` (★**那是 ISS-195 的地界, 不许碰★**) · `HW/pcb60x30_check.py` / `HW/pcb60x30_check.json` (★只许读, 不许改★) · `MECH/print/**` (打印包与 STL) · `MECH/pinset2_mech_check.py` (★只许跑, 不许改★) · 任何 `state/gen_*.py` · `state/issue_log.yaml` (★改 issue 状态是 main 的活★) · **别人的分片** (hw.yaml / sw.yaml / pm.yaml)
· ★**不许联系供应商/原厂/模具厂** (★外发一律经项目总工★) · ★**不许发任何邮件** ★
· ★**证据分级** [实测]/[官方]/[推算]/[0数据] 必标; ★**任何数字必须同时给口径** (哪块板/哪个板宽/哪套孔位/何时) ★
· ★**不许改判据阈值来让自己变绿** (★降级等于伪造验收★) · ★**不许把套B 那行删掉** ★
"""

NEW_ISSUES = [
    {
        "id": "ISS-196",
        "title": "★【内部活·不是原厂的事】两条逾期 6 天的 P0 needs_from 前提已被实测推翻 ⇒ rknn 工具链/构建环境/模型 sha 台账三处口径订正 (ISS-145 demo 模型路线 M1/M2 的事实底座)",
        "severity": "medium",
        "owner": "sw-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": TODAY,
        "due": DUE,
        "status": "open",
        "task_brief": BRIEF_196,
    },
    {
        "id": "ISS-197",
        "title": "★【内部活·不是原厂的事】套A 孔位已落地 ⇒ 结构侧 5 处记录还停在「套B 仍是活口径」⇒ 口径收敛 + 3 条未决项(骨架超重/石墨超预算/demo 安装孔)整理成一页选项表",
        "severity": "medium",
        "owner": "mech-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": TODAY,
        "due": DUE,
        "status": "open",
        "task_brief": BRIEF_197,
    },
]


def main() -> int:
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        orig = open(LOG, "rb").read()
        doc = yaml.safe_load(orig.decode("utf-8"))
        issues = doc.get("issues") or []
        have = {i.get("id") for i in issues}
        for n in NEW_ISSUES:
            if n["id"] in have:
                print("★ 已存在, 跳过:", n["id"])
                continue
            issues.append(n)
        doc["issues"] = issues
        # ★自证: 除新增两条外, 逐字节不变 (⇒ 排序/缩进/宽度都对齐原文件的 safe_dump 参数)
        redump = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200).encode("utf-8")
        # ★只允许【末尾多出两条】⇒ 校验: 原文件内容必须是新文件的【前缀】(safe_dump 保序)
        if not redump.startswith(orig):
            print("★ 自证失败: 重排后的内容与原文件不是前缀关系 (说明有字段顺序/格式漂移)")
            return 1
        added = redump[len(orig):]
        tmp = LOG + ".tmp"
        with open(tmp, "wb") as f:
            f.write(redump)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, LOG)
        dfd = os.open(os.path.dirname(LOG), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
        print("✅ 已新增 %d 条:" % len(NEW_ISSUES))
        for n in NEW_ISSUES:
            print("   · %s → %s (open, due %s)" % (n["id"], n["owner"], n["due"]))
        print("   原 %d B → 新 %d B (只增不改: %s)"
              % (len(orig), len(redump), hashlib.md5(orig).hexdigest()[:8]))
        return 0


if __name__ == "__main__":
    sys.exit(main())
