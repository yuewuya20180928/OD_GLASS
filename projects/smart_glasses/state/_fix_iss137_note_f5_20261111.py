#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-137 note F5 订正 (rev3) —— 补 sw-lead 2026-11-11 01:5x rev2 复验拍出的 F5。

★★**为什么是 main 自办**: ISS-137 的 owner=main (项目总工自办), verify_by=sw-lead (铁律: 自己修的必须别人验)。
   sw-lead rev2 复验判决: ★**技术内容全过 (R2~R6 + ④TX + ⑥已发布数字 + 边界)**, ★**5 处订正 5/5 逐条命中 rev1 点名的原文**,
   ★**唯一阻塞 = note【交付】② 段一处函数归属 (F5)** ⇒ ★**补这一处 sw-lead 立刻签**。

★**F5 是什么 (rev0 时代遗留, rev1/rev2 两轮都没扫到)**:
   note【交付】② 段写 "② 新增 compose_max_for(S5) ⇒ ... 上限 −2.69ms / 10.09ms / 16.65ms"
   ⇒ ★**但这三个数是 `display_out_max_for()` 的输出, 不是 `compose_max_for()` 的**
   (★rev1 把 TX 显式拆出来后 compose_max_for() 改成了"总额上限 − TX" ⇒ 数字从 10.09 变成 2.32, note 这行没跟着改)
   ⇒ ★**同一份 note 里 compose_max_for 有两个数 (L6 的 10.09 vs L22 的 2.32) ⇒ 自相矛盾** ⇒ 差的就是 TX 那 7.776ms。

★★**我自己的独立复核 (不照抄 sw-lead 的数)**:
   `python3 -c "import HW.e2e_budget_rk3572"` 实跑两个函数 ⇒
   display_out_max_for / compose_max_for:
     yolov5s@640 S5=26.085 ⇒ −2.685 / −10.461
     yolov5n@640 S5=13.305 ⇒  10.095 /   2.319
     yolov5s@320 S5= 6.750 ⇒  16.650 /   8.874
   ⇒ ★**note 里那三个数 (10.09/16.65/−2.69) 确实全是 display_out_max_for 的** ⇒ F5 成立。

★★**纪律 (一条不放松)**:
  ① flock(state/.issue_log.lock) + **锁内重读** + **原子写** (tmp + fsync + os.replace)
  ② **只碰 ISS-137 这一条的 note** —— 其余 180 条逐字段比对, 变了就报错回滚
  ③ 不改 status / verify_result / verify_date (★仍是 fixed + null ⇒ 等 sw-lead 复验签字★)
  ④ 不碰 STATE.yaml / 分片 / PROJECT_TRACKER.md / §0 锁死表 / 任何交付物
  ⑤ 不发邮件 / 不联系供应商

用法:
  python3 state/_fix_iss137_note_f5_20261111.py --dry-run
  python3 state/_fix_iss137_note_f5_20261111.py
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

# ★★**OLD/NEW 直接取 sw-lead 2026-11-11 rev2 复验报告 §8.2 ⑥ 的精确替换串 (它已模拟验证 7 项自检全过)**★
# ★**我不改写语义, 只照抄** —— 改写就等于我自说自话, sw-lead 的复验就失去意义了。
OLD = ("② 新增 compose_max_for(S5) ⇒ **可测判据**: 模式A ≤ 60ms ⇒ t_compose 测出 ≤ 多少才算过。\n"
       "   RK3572+yolov5s@640: 上限 **−2.69ms** (负数 ⇒ 不用测, 必不过) · RK3572+yolov5n@640: 上限 **10.09ms** · "
       "RK3572+yolov5s@320: 上限 **16.65ms**。")

NEW = ("② 新增 **display_out_max_for(S5)** (输出侧总额上限) + **compose_max_for(S5)** (= 输出侧总额上限 − TX 物理下限) ⇒ "
       "**可测判据**: 模式A ≤ 60ms ⇒ 板端第7段+第8段合计测出 ≤ 多少才算过。\n"
       "   【输出侧总额上限】RK3572+yolov5s@640: **−2.69ms** (负数 ⇒ 不用测, 必不过) · RK3572+yolov5n@640: **10.09ms** · "
       "RK3572+yolov5s@320: **16.65ms**; "
       "★**【减 TX 后·合成上限 (仅第7段 t_compose)】: −10.46ms / **2.32ms** / 8.87ms** (★TX 物理下限 @1080p = 7.776ms★)。")

# ★追加的 rev3 段 (记录本次订正, 让 sw-lead 复验时知道改了什么)★
REV3_TAIL = (
    "\n★★**★rev3 (2026-11-11 03:1x, ★★sw-lead rev2 复验: 技术内容全过·只卡本 note 1 处 (F5)·项目总工已订正·待复验签字★★)★**:\n"
    "  ★**sw-lead rev2 判决 (原文)**: 『★**技术内容全过 (R2~R6 + ④TX + ⑥已发布数字 + 边界); ★唯一阻塞 = note 的"
    "【交付】② 段一处函数归属 (F5)** ⇒ ★**补它我立刻签**』\n"
    "  ★**F5 是什么**: 本 note【交付】② 段写『② 新增 compose_max_for(S5) ⇒ 上限 −2.69 / 10.09 / 16.65ms』"
    "⇒ ★**但这三个数是 `display_out_max_for()` 的输出, 不是 `compose_max_for()` 的** ⇒ ★**同一份 note 里 compose_max_for "
    "出现两个数 (L6 的 10.09 vs L22 的 2.32) ⇒ 自相矛盾** ⇒ 差的就是 TX 那 7.776ms\n"
    "  ★**★为什么 rev0 时代是对的, 现在错了**: rev0 的脚本里 `compose_max_for()` 本来就返回这三个数 ⇒ rev1 把 TX 显式拆出来, "
    "`compose_max_for()` 改成了『总额上限 − TX』, 数字随之从 10.09 变成 2.32 ⇒ ★**但 note 这一行 (rev0 遗留) 没跟着改**\n"
    "  ★**★本次订正 (1 处, 交付物一个字节都没动)**: ② 段换成『display_out_max_for(S5) (输出侧总额上限) + compose_max_for(S5) "
    "(= 输出侧总额上限 − TX 物理下限)』+ 三个输出侧数**一个不动** + **补上合成上限 −10.46 / 2.32 / 8.87ms** ⇒ "
    "★**note 里两个函数的归属现在全对了**\n"
    "  ★**我自己的独立复核 (不照抄 sw-lead 的数)**: 直接 import 脚本实跑两个函数 ⇒ display_out_max_for / compose_max_for = "
    "yolov5s@640 (S5=26.085) **−2.685 / −10.461** · yolov5n@640 (S5=13.305) **10.095 / 2.319** · yolov5s@320 (S5=6.750) "
    "**16.650 / 8.874** ⇒ ★**证实 note 里那三个数确实全是 display_out_max_for 的 ⇒ F5 成立**\n"
    "  ★**自证 (rev3)**: `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 · "
    "`python3 SW/tools/demo_timing_check.py` ⇒ rc=0 (20/20) · ★**交付物 md5 与 rev1/rev2 复验时逐字节相同 (本单只改 note)** ★★\n"
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
            # ---- F5 替换 (要求 OLD 恰好命中 1 次) ----
            if OLD in note:
                if note.count(OLD) != 1:
                    print(f"❌ F5 旧原文出现 {note.count(OLD)} 次 (要求恰好 1 次) ⇒ 拒绝替换")
                    return 2
                note = note.replace(OLD, NEW)
                print("✅ F5 已替换 (① ② 段函数归属)")
            elif NEW in note:
                print("⏭  F5 已应用过 (幂等, 跳过)")
            else:
                print("❌ F5 定位失败 (旧原文没命中, 且新原文也不在)")
                print("   " + OLD[:160])
                return 2

            # ★**自检: 替换后 note 里 compose_max_for 的每个出现都带正确语义?** ★
            bad = []
            for ln in note.split("\n"):
                if "compose_max_for" in ln:
                    if "display_out_max_for" not in ln and "总额上限 − TX" not in ln and "− TX 下限" not in ln:
                        bad.append(ln[:120])
            if bad:
                print("❌ 替换后仍有关于 compose_max_for 的歧义行:")
                for b in bad:
                    print("   " + b)
                return 2
            print("✅ 替换后 note 里 compose_max_for 的每一处都带正确语义")

            # ★追加 rev3 段 (只加一次)★
            if "rev3 (2026-11-11" in note:
                print("⚠️ rev3 段已存在 ⇒ 不重复追加")
            else:
                note = note.rstrip("\n") + REV3_TAIL
                print("✅ 已追加 rev3 段")

            target["note"] = note

            # ★★**只允许 ISS-137 的 note 变, 其余 180 条必须逐字段相同**★★
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
    ok = 0
    # ① F5 新原文在
    if NEW in n2:
        print("  ✅ F5 新原文在位")
        ok += 1
    else:
        print("  ❌ F5 新原文不在")
    # ② F5 旧原文不在 (整句)
    if OLD not in n2:
        print("  ✅ F5 旧原文整句已消失")
        ok += 1
    else:
        print("  ❌ F5 旧原文还在")
    # ③ 两个数都在 (10.09 = 输出侧 / 2.32 = 合成)
    if "10.09ms" in n2 and "2.32ms" in n2 and "−10.46ms" in n2 and "8.87ms" in n2:
        print("  ✅ 四个数 (10.09 / 2.32 / −10.46 / 8.87) 都在位")
        ok += 1
    else:
        print("  ❌ 四个数有缺")
    # ④ status/verify 未被本脚本改动
    if t2.get("status") == "fixed" and t2.get("verify_result") is None and t2.get("verify_date") is None:
        print("  ✅ status 仍 fixed / verify_result 仍 null / verify_date 仍 null (没自签)")
        ok += 1
    else:
        print(f"  ❌ status/verify 被改了: {t2.get('status')}/{t2.get('verify_result')}/{t2.get('verify_date')}")
    print(f"写盘后回读自检: {ok}/4 通过")
    return 0 if ok == 4 else 2


if __name__ == "__main__":
    sys.exit(main())
