#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-192 验收签字落账器 (2026-11-11 18:4x, 项目总工 main)

★**为什么本单要签**: mech-lead 于 2026-11-11 17:39~17:41 交卷 (HANDOFF/2026-11-11_mech-lead_ISS192_机械复核器迁60x30与孔位Y仲裁.md
   + MECH/BOARD_GEOM_30MM.md + MECH/{pinset2_mech_check,skeleton_section_check,cross_review_check,hinge_usb_check,iss065_check}.py
   + state/fragments/mech.yaml) ⇒ verify_by=main ⇒ ★**main 必须独立复核, 不采信自述** (铁律: 自己修的必须别人验)。

★**本单范围 (决定签字含义)**: 本单 = ① 把结构侧机械复核器从作废的 12/15mm 板宽迁到现行 60×30
   ② 把 PIN-SET-2 孔位 Y 的两套互斥口径 (差 7.50mm) 仲裁成一份权威表 (= 套A)。
   ⇒ ★**签字覆盖这两件**; ⇒ ★**不覆盖 hw-lead 产物侧的那一半 (套B 还没改)** ⇒ 未藏账, 已开 ISS-194。

★**main 独立复核的实测 (★全部本机实跑, 不是抄 mech-lead 的自述★)**:
  V1 `python3 MECH/pinset2_mech_check.py` ⇒ rc=0 · 「复算项 38 | FAIL 0 | WARN 2」
  V2 `python3 MECH/pinset2_mech_check.py --self-test` ⇒ rc=0 · 「self-test: 6/6 用例符合预期」
     (反向用例逐条命中: S1 挪进逃线带必红 / P2 挪进封装体必红 / S2 挪到板边必红 / 打印包改套B 必红)
  V3 `python3 MECH/skeleton_section_check.py` ⇒ rc=0 (满宽段 30.00 / 横向扩散 3.50→6.95mm/边 / 4 候选全超预算)
  V4 `python3 MECH/cross_review_check.py` ⇒ rc=0 (★已明写「不是闸」+ 退出码只反映 MECH-OWNED + 16 项逐项标归属 ⇒ 无孤儿红)
  V5 `python3 MECH/hinge_usb_check.py` ⇒ rc=0 · `python3 MECH/iss065_check.py` ⇒ rc=0
  V6 md5 对拍: 板 `611b869e13518c3c023fb178f91a0075` / `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ **一字未变**
  V7 `state/merge.py` rc=0 (冲突 0) · `state/gate_check.py` Q1 18/18
  V8 ★★**仲裁依据 = main 自己重算, 不采信自述★**: ★**main 自己解析两个打印包二进制 STL**
     (纯 Python 解析 + 顶面占据栅格化, 0.5mm 栅格) ⇒ ★**cage PCB 定位板 (板基线 Y=60) 实测四个通孔
     = P1(8.00,15.00) ⌀2.4 + P2(52.00,15.00) ⌀2.4 + S1(8.00,10.00) ⌀1.6 + S2(52.00,20.00) ⌀1.6**
     ⇒ ★**coupon PCB 样板 (基线 X=4 / Y=84) 实测同一组值** ⇒ ★★**「打印包 = 套A」被独立证实**
     ⇒ ★**套B 的 (8.00,2.50) / (52.00,27.50) 两个位置实测【实心无孔】** ⇒ ★**套B 与打印包不符**。
     ★另: 生成器源码常量 `pinset2_p_y=15.00 / pinset2_s1_y=10.00 / pinset2_s2_y=20.00`
     (`MECH/print/gen_print_pack_revb.py:93-95`) 与栅格实测**逐值一致** (★打印包孔位是包络多边形切出来的,
     所以圆心靠栅格/弦宽反算, 不靠找圆柱面★)。
  V9 ★**几何自洽性独立判据 (不依赖打印包)**: 套B 相对 30mm 新板中心 (Y=15.00) 的偏移 = S1 −12.50 / S2 +12.50
     ⇒ ★**不对称且两孔分离 25.00mm**; 而 15mm 老口径 (`HW/PCB_FIXING_PINSET2.md` §3.1: P1(8,7.50) P2(52,7.50)
     S1(8,2.50) S2(52,12.50)) 是**关于中心 7.50 的 ±5.00 对角分布** ⇒ 平移到 30mm 板 (中心 15.00) ⇒
     ★**套A (S1 10.00 / S2 20.00, 分离仍 10.00, 仍对称)** ⇒ ★**套B 是「只改 Y」时的漂移产物, 不是平移**。
  V10 ★**边界复核 (mtime 实测)**: 本单只动 `MECH/` (8 个文件) + `HANDOFF/` (1 个) + `state/fragments/mech.yaml`
     ⇒ ★**HW/ 内无 mech-lead 写入** (★HW/ 近 3h 的改动是主线原理图/投产包, 板 md5 对拍未变)
     ⇒ ★**issue_log / PROJECT_TRACKER §0 / 别人分片 / state/gen_*.py 未动** ✔

★**未闭合项 (★未藏账★)**: ① ★**hw-lead 产物侧还没改**: `HW/pcb60x30_check.py:113-117` 的 HOLES 表仍是套B
     (S1 Y=2.50 / S2 Y=27.50) ⇒ ★**已开 ISS-194** (owner=hw-lead, 只改孔位表 + 重生成 .json, 不碰布线/布局)
     ② 骨架截面 30mm 下 4 个候选**全部超预算** (最好 4.08g/对 vs 预算 +1~3g) + 石墨 2.16g/对 > W11 上限
     ⇒ ★**预算裁 = main/老板** (结构侧已登记 needs_from) ③ demo 板 MountingHole=0 + params 里 4 个遗留孔坐标
     ⇒ ★**属 PCB 布局类 ⇒ 按老板 11-11 10:07 口径【不派】(排队等原理图定稿)** ④ `fit_check.py` v2 退役还是并存 = main 裁。

★**落账纪律 (与项目既有范式一致)**: ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**自证: yaml.safe_dump(整份 doc) 必须与原文件逐字节相同** ⇒ 通过才写 ③ 原子写 (tmp → fsync → os.replace → fsync(dir))
  ④ **不改任何别的 issue 的任何字节** (只改 ISS-192 这一条 dict) ⑤ verify_by(main) != owner(mech-lead) ✔

★**边界**: 不改 §0 锁死表 · 不改任何已发布数字 · 不写任何子总工的分片 · 不发邮件 / 不联系供应商 / 不下采购单
  · ★**不改网表 / 不改板 / 不改原理图**
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TARGET = "ISS-192"
TODAY = "2026-11-11"

FIX_REF = (
    "MECH/BOARD_GEOM_30MM.md (★结构侧权威表: 板框 60×30 / SoC RK3576 占位 / 逃线带 / PIN-SET-2 四孔含 Y 口径仲裁"
    "= 套A / 打印包契约三条 WARN 现行值 / 6 脚本死常量定性 / 影响面 / demo 板复核 / 未决 7 条) · "
    "MECH/pinset2_mech_check.py (+ .json, 板宽无关化判据, --self-test 6/6) · MECH/skeleton_section_check.py (30mm 迁) · "
    "MECH/cross_review_check.py (明写「不是闸」+ 退出码只反映 MECH-OWNED + 16 项逐项标归属) · "
    "MECH/hinge_usb_check.py (板宽 12→30 迁) · MECH/iss065_check.py (板宽 15→30 迁 + 来源标错订正) · "
    "MECH/fit_check.py (★标作废不迁: 整套基线 12/50/0.80 一起死, 只改 pcb_w 会造半迁移 Frankenstein 口径) · "
    "HANDOFF/2026-11-11_mech-lead_ISS192_机械复核器迁60x30与孔位Y仲裁.md · state/fragments/mech.yaml (3 条 needs_from) · "
    "★**hw-lead 产物侧未改 ⇒ ISS-194**"
)

NOTE_ADD = (
    "\n\n★2026-11-11 18:4x 项目总工**独立验收签字 (verify_by=main ⇒ 自己修的必须别人验; ★不采信自述★)**。"
    "★**签字范围 = ① 结构侧机械复核器迁到 60×30 ② PIN-SET-2 孔位 Y 仲裁成一套 = 套A**; "
    "★**不覆盖 hw-lead 产物侧 (套B 还没改) ⇒ 未藏账 ⇒ 已开 ISS-194**。"
    "★**main 实跑复现 (10 条全过)**: ① `pinset2_mech_check.py` rc=0 「复算项 38 | FAIL 0 | WARN 2」 "
    "② `--self-test` rc=0 「6/6 用例符合预期」 ③ `skeleton_section_check.py` rc=0 "
    "④ `cross_review_check.py` rc=0 ⑤ `hinge_usb_check.py` rc=0 + `iss065_check.py` rc=0 "
    "⑥ md5 对拍 **板 611b869e… / .kicad_pro 3e504d2b… 一字未变** ⑦ merge rc=0 冲突 0 + gate_check Q1 18/18 "
    "⑧ ★★**仲裁依据 main 自己重算 (不采信自述)**: ★**自己解析两个打印包二进制 STL + 顶面占据栅格化 (0.5mm)** "
    "⇒ cage (板基线 Y=60) 与 coupon (基线 X=4/Y=84) **实测四孔 = P1(8,15) P2(52,15) ⌀2.4 + S1(8,10) S2(52,20) ⌀1.6** "
    "⇒ ★★**「打印包 = 套A」独立证实**; ★**套B 的 (8,2.5)/(52,27.5) 实测实心无孔** ⇒ ★**套B 与打印包不符**; "
    "★另: 生成器常量 pinset2_p_y=15.00 / s1_y=10.00 / s2_y=20.00 (`gen_print_pack_revb.py:93-95`) 与栅格实测逐值一致 "
    "⑨ ★**几何自洽性独立判据**: 套B 相对新中心偏移 S1 −12.50 / S2 +12.50 (不对称 + 分离 25.00) "
    "⇒ 而 15mm 老口径 (§3.1: P(8,7.50)/(52,7.50) S1(8,2.50) S2(52,12.50)) 是**关于中心 7.50 的 ±5.00 对角分布** "
    "⇒ 平移到 30mm 板 (中心 15.00) ⇒ **套A (分离仍 10.00, 仍对称)** ⇒ ★**套B = 「只改 Y」的漂移产物, 不是平移** "
    "⑩ ★**边界复核 (mtime 实测)**: 本单只动 MECH/(8) + HANDOFF/(1) + state/fragments/mech.yaml ⇒ **HW/ 内无 mech-lead 写入** "
    "⇒ issue_log / §0 锁死表 / 别人分片 / gen_*.py 未动 ✔。"
    "★**未闭合 (未藏账)**: ① 套B 产物要 hw-lead 改 ⇒ **ISS-194** ② 骨架截面 30mm 全线超预算 (最好 4.08g/对 vs +1~3g) "
    "+ 石墨 2.16g/对 > W11 ⇒ 预算裁 = main/老板 ③ demo 板零安装孔 + params 4 个遗留坐标 ⇒ **属 PCB 布局类 ⇒ "
    "按老板 11-11 10:07 口径【不派】(排队等原理图定稿)** ④ fit_check.py v2 退役还是并存 = main 裁。"
    "★**下一步**: hw-lead 交 ISS-193 ⇒ main 验收签字 ⇒ 队列腾出 ⇒ ISS-194 (孔位表套B→套A) 派出。"
)


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "a+", encoding="utf-8") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        orig = open(LOG, encoding="utf-8").read()
        doc = yaml.safe_load(orig)

        items = doc["issues"] if isinstance(doc.get("issues"), list) else list(doc["issues"].values())
        target = next((i for i in items if i.get("id") == TARGET), None)
        if target is None:
            print(f"❌ {TARGET} 不在 issue_log.yaml 里")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1
        if target.get("status") == "verified":
            print(f"ℹ️ {TARGET} 已经是 verified ⇒ 幂等跳过")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 0
        if target.get("status") != "fixing":
            print(f"❌ {TARGET} 当前 status={target.get('status')} (不是 fixing) ⇒ 中止")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1

        probe = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        if probe != orig:
            print("❌ 中止: yaml 往返与原文件不逐字节相同 ⇒ 整份改写会动到别人的行 ⇒ 不写")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1

        if target.get("verify_by") == target.get("owner"):
            print("❌ 中止: verify_by == owner ⇒ 违反验证分离")
            fcntl.flock(lf, fcntl.LOCK_UN)
            return 1

        target["status"] = "verified"
        target["fixed_at"] = TODAY
        target["verify_result"] = "pass"
        target["verify_date"] = TODAY
        target["fix_ref"] = FIX_REF
        target["note"] = (target.get("note") or "") + NOTE_ADD

        new_text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
        atomic_write(LOG, new_text)

    print(f"✅ {TARGET} → status=verified + verify_result=pass + verify_date={TODAY} + fix_ref + note 已追加")
    print(f"   issue_log.yaml: {len(orig)} → {len(new_text)} 字符 (只改 ISS-192 一条)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
