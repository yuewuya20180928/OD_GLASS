#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-137 note 订正 (rev2) —— 补 sw-lead 2026-11-11 00:2x rev1 复验拍出的 R1 半修。

★★**为什么是 main 自办**: ISS-137 的 owner=main (项目总工自办, 按铁律『自己修的必须别人验』⇒ verify_by=sw-lead)。
   sw-lead 已在 HANDOFF/2026-11-10_sw-lead_ISS137_验证.md §7 签字: ★**技术内容全过 (R2~R6 + ④ + ⑥)**,
   ★**唯一阻塞他签字的是 issue_log.yaml 里 note 的 5 处旧口径没订正** ⇒ 那 5 处在 main 自己的分片 ⇒ 本单闭环。
   ⇒ ★**本单只改 note 文本, 不碰任何交付物 (脚本/规格/RKNN_BENCH 一个字节都不动)**。

★**5 处 (sw-lead §7.2 表格逐条点名)**:
  ① note idx4  : 槽位名 `T_COMPOSE` → `T_DISPLAY_OUT` (★旧名已不存在于脚本★)
  ② note idx6  : yolov5s@320 上限 **17.65ms** → **16.65ms** (★脚本实算 16.65★)
  ③ note idx7  : "板端打一个点" → "打两个点 (第7段合成 + 第8段上屏)" (★TX 在第8段★)
  ④ note idx10 : 【口径纪律】段是 rev0 的自我评价 ("t_compose ↔ S9 直接代入 ⇒ 不制造分叉") ⇒ ★R2 已判它不成立★ ⇒ 改成 rev1 口径
  ⑤ note idx11 : "新增 6 条拆分护栏" → **7 条** (★另: 护栏③ 的描述 "代入T_COMPOSE" 也是旧名★)

★★**纪律 (一条不放松)**:
  ① flock(state/.issue_log.lock) + **锁内重读** + **原子写** (tmp + fsync + os.replace)
  ② **只碰 ISS-137 这一条的 note** —— 其余 180 条逐字节比对, 变了就报错回滚
  ③ 不改 status / verify_result / verify_date (★仍是 fixed + null ⇒ 等 sw-lead 复验签字★)
  ④ 不碰 STATE.yaml / 分片 / PROJECT_TRACKER.md / §0 锁死表 / 任何交付物
  ⑤ 不发邮件 / 不联系供应商

用法:
  python3 state/_fix_iss137_note_rev2_20261111.py --dry-run
  python3 state/_fix_iss137_note_rev2_20261111.py
"""
from __future__ import annotations

import fcntl
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
ISSUE_ID = "ISS-137"

# ★**每条 = (旧原文必须逐字命中, 新原文) —— 用"必须命中"当断言, 命中不了就报错退出 (不许模糊替换)**★
REPLACEMENTS = [
    # ① 槽位名 (★脚本里已无 T_COMPOSE 这个常量, 现在是 T_DISPLAY_OUT★)
    (
        "+ T_COMPOSE 3.00 (S9 显示合成/缩放, ★**唯一随显示像素数变的一段**)",
        "+ T_DISPLAY_OUT 3.00 (S9 显示输出侧 = 板端第7段合成 + 第8段上屏, ★**唯一随显示像素数变的一段**)",
    ),
    # ② 数字 (★脚本 §⑤ 实打印 16.65★)
    (
        "RK3572+yolov5s@320: 上限 **17.65ms**。",
        "RK3572+yolov5s@320: 上限 **16.65ms**。",
    ),
    # ③ 打点数 (★TX 在第8段 ⇒ 两个点★)
    (
        "★**板端打一个点 ⇒ 一行命令出结论** (不用再自己算)。",
        "★**板端打两个点 (第7段合成 + 第8段上屏) ⇒ 一行命令出结论** (不用再自己算)。",
    ),
    # ④ 口径纪律段 (★rev0 的自我评价被 R2 判为不成立 ⇒ 整段换成 rev1 口径★)
    (
        '【★口径纪律】板端阶段表第7段 `t_compose` 的定义 (画完框的帧 → 显示帧就绪) 与 RKNN_BENCH §4.1 的 S9 标签 (原文写"显示 TX") **不完全一致** (合成 vs TX) ⇒ ★**本单按 DEMO_OD_TIMING_SPEC §3.3 的映射 (t_compose ↔ S9) 对齐**, ⇒ 板端实测值**直接代入、无需换算** ⇒ ★**不制造新的口径分叉** (MEMORY 铁律: 口径混用比数字错更贵)。',
        '【★口径纪律 (rev1 订正·★R2 判 rev0 此段不成立★)】板端阶段表第7段 `t_compose` (合成) 与第8段 `t_display` (上屏) **两段之和** 才等于 RKNN_BENCH §4.1 的 S9 (显示输出侧) ⇒ ★**rev0 写的"t_compose ↔ S9 直接代入、无需换算"已被 R2 判为不成立 (★那恰恰造了 S9 一名两义★)** ⇒ ★**rev1 口径: `t_compose` 只是 S9 的一部分 ⇒ 板端必须另测 `t_display` (★或先取 TX 物理下限 @1080p = 7.776ms★) ⇒ 判据 = `display_out_max_for()` (输出侧总额上限) 与 `compose_max_for()` (= 总额上限 − TX 下限) 两条, 不可混用** ⇒ ★**口径单一 (MEMORY 铁律: 口径混用比数字错更贵)**。',
    ),
    # ⑤ 护栏条数 (★脚本 selftest 实打印 7 条: ①拆分恒等 ②互逆@4个S5 ③代入800×600基线 ④TX在账里 ⑤合成上限=输出侧−TX ⑥输出侧线性上界>判据 ⑦TX随像素数比==像素比★)
    (
        "★**新增 6 条拆分护栏**: 拆分恒等 / 判据↔算账互逆@4个S5 / 代入T_COMPOSE与旧模型逐位一致 / 线性上界>判据 ⇒ 真需要实测)。",
        "★**新增 7 条拆分护栏**: ①拆分恒等 ②判据↔算账互逆@4个S5 ③代入 800×600 基线 (合成 1.20 + TX 1.80) 与旧模型逐位一致 ④TX 在账里 (加/不加 TX 差 == TX 物理下限) ⑤合成上限 == 输出侧上限 − TX 下限 ⑥输出侧线性上界 > 判据 ⇒ 真需要实测 ⑦TX 随像素数比 == 像素比)。",
    ),
]

# ★**追加到 note 末尾的 rev2 段 (记录本次订正, 让 sw-lead 复验时知道改了什么)**★
REV2_TAIL = (
    "\n★★**★rev2 (2026-11-11 01:4x, ★★sw-lead rev1 复验: 技术内容全过·只卡本 note 5 处·项目总工已订正·待复验签字★★)★**:\n"
    "  ★**sw-lead 判决 (原文)**: 『★**技术内容全过 (R2~R6 + ④ + ⑥), 但 R1 只修了一半 ⇒ 判 fail(轻量) ⇒ ★差 1 处字符串同步, 补上我立刻签**』"
    " ⇒ ★**唯一阻塞 = 本 note 的 5 处旧口径** ⇒ ★**本段逐条订正如下 (交付物一个字节都没动)**:\n"
    "  ★**① 槽位名**: `T_COMPOSE` → ★**`T_DISPLAY_OUT`** (★脚本里已无 T_COMPOSE 这个常量★) ⇒ 描述同步改成"
    "『S9 显示输出侧 = 板端第7段合成 + 第8段上屏』\n"
    "  ★**② 数字**: yolov5s@320 上限 **17.65ms → 16.65ms** (★脚本 §⑤ 实打印 16.65·本 note 此前与脚本不一致★)\n"
    "  ★**③ 打点数**: 『板端打**一个**点』 → ★**『板端打两个点 (第7段合成 + 第8段上屏)』** (★TX 在第8段·一个点扣不掉 TX★)\n"
    "  ★**④ 口径纪律段**: ★**整段重写** ⇒ ★**rev0 的『t_compose ↔ S9 直接代入 ⇒ 不制造分叉』已被 R2 判为不成立"
    " (★它恰恰造了 S9 一名两义★) ⇒ rev1 口径 = 『t_compose 只是 S9 的一部分 ⇒ 必须另测 t_display 或取 TX 物理下限 7.776ms』**\n"
    "  ★**⑤ 护栏条数**: 『新增 **6** 条拆分护栏』 → ★**『新增 7 条』** ⇒ ★**并把护栏③ 的描述从旧名『代入T_COMPOSE』改成"
    "『代入 800×600 基线 (合成 1.20 + TX 1.80) 与旧模型逐位一致』** (★脚本 selftest ⑦ 条逐条实打印 ①~⑦★)\n"
    "  ★**自证 (rev2)**: `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 (★拆分护栏 7 条全过★) · "
    "`python3 SW/tools/demo_timing_check.py` ⇒ rc=0 (20/20) · ★**交付物 md5 与 rev1 复验时逐字节相同 (本单只改 note)** ★★\n"
    "  ★**待 sw-lead 复验签字** ⇒ ★**本单 owner=main / verify_by=sw-lead ⇒ 签字前状态仍是 fixed, 不许自己标 verified** ★★"
)


def atomic_write(path: str, text: str) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    dry = "--dry-run" in sys.argv

    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            with open(LOG, encoding="utf-8") as f:
                raw = f.read()
            data = yaml.safe_load(raw)
            issues = data.get("issues") or []
            target = next((i for i in issues if i.get("id") == ISSUE_ID), None)
            if target is None:
                print(f"❌ 找不到 {ISSUE_ID}")
                return 2

            before_note = target.get("note") or ""
            before_snapshot = {i.get("id"): dict(i) for i in issues if i.get("id") != ISSUE_ID}

            note = before_note
            for old, new in REPLACEMENTS:
                if old in note:
                    if note.count(old) != 1:
                        print(f"❌ 旧原文出现 {note.count(old)} 次 (要求恰好 1 次) ⇒ 拒绝替换")
                        return 2
                    note = note.replace(old, new)
                    print(f"✅ 已替换: {old[:70]}...")
                elif new in note:
                    # ★**幂等**: 上一轮已应用 ⇒ 不重复替换 (★允许脚本重跑★)
                    print(f"⏭  已应用过 (跳过): {new[:70]}...")
                else:
                    print("❌ 定位失败 (旧原文没命中, 且新原文也不在):")
                    print("   " + old[:160])
                    return 2

            # ★追加 rev2 段 (只加一次)★
            if "rev2 (2026-11-11" in note:
                print("⚠️ rev2 段已存在 ⇒ 不重复追加")
            else:
                note = note.rstrip("\n") + REV2_TAIL
                print("✅ 已追加 rev2 段")

            target["note"] = note

            # ★★**只允许 ISS-137 的 note 变, 其余 180 条必须逐字节相同**★★
            changed = []
            for i in issues:
                iid = i.get("id")
                if iid == ISSUE_ID:
                    continue
                if before_snapshot.get(iid) != i:
                    changed.append(iid)
            if changed:
                print(f"❌ 意外改动了别的 issue: {changed} ⇒ 回滚 (不写盘)")
                return 2
            print(f"✅ 其余 {len(before_snapshot)} 条 issue 逐字段比对无变化")

            out = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=200)
            if dry:
                print("--- dry-run: 不写盘 ---")
                print(f"note 长度 {len(before_note)} → {len(note)}")
                return 0
            atomic_write(LOG, out)
            print(f"✅ 已写入 {LOG}")
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)

    # ★写盘后再回读验证★
    with open(LOG, encoding="utf-8") as f:
        again = yaml.safe_load(f.read())
    t2 = next(i for i in again["issues"] if i.get("id") == ISSUE_ID)
    n2 = t2.get("note") or ""
    # ★★**判据口径 (★sw-lead 验收标准 ① 的原话: 『两处的 yolov5s@320 上限都是 16.65』★)**:
    #   ⇒ **查的是"断言行", 不是"全文有没有这个词"** ⇒ ★**rev2 段里必须保留 "17.65ms → 16.65ms" 的改动说明
    #   (★那是 changelog, 不是断言★) ⇒ ★**故此处查"旧断言整句"是否已消失, 而不是查 token 全局缺席**★
    stale_claims = [
        "+ T_COMPOSE 3.00 (S9 显示合成/缩放, ★**唯一随显示像素数变的一段**)",
        "RK3572+yolov5s@320: 上限 **17.65ms**。",
        "★**板端打一个点 ⇒ 一行命令出结论** (不用再自己算)。",
        "★**新增 6 条拆分护栏**",
        "⇒ ★**不制造新的口径分叉** (MEMORY 铁律: 口径混用比数字错更贵)。",
    ]
    checks = [
        ("旧断言① 槽位名已消失", all(s not in n2 for s in stale_claims[:1])),
        ("旧断言② 17.65 已消失", stale_claims[1] not in n2),
        ("旧断言③ 一个点已消失", stale_claims[2] not in n2),
        ("旧断言④ 6 条护栏已消失", stale_claims[3] not in n2),
        ("旧断言⑤ rev0 口径纪律已消失", stale_claims[4] not in n2),
        ("16.65 在位", "16.65ms" in n2),
        ("T_DISPLAY_OUT 在位", "T_DISPLAY_OUT 3.00" in n2),
        ("两个点在位", "打两个点" in n2),
        ("7 条护栏在位", "新增 7 条拆分护栏" in n2),
        ("rev1 口径在位", "已被 R2 判为不成立" in n2),
        ("rev2 段在位", "rev2 (2026-11-11" in n2),
        ("status 仍是 fixed", t2.get("status") == "fixed"),
        ("verify_result 仍是 null", t2.get("verify_result") is None),
    ]
    bad = 0
    for name, ok in checks:
        print(("  ✅ " if ok else "  ❌ ") + name)
        if not ok:
            bad += 1
    print("✅ 回读全过" if bad == 0 else f"❌ 回读有 {bad} 项不过")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
