#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-145 / ISS-179 落账: fixed → verified (项目总工 main = 验证方) —— 2026-11-11 03:2x

★★**为什么现在做这一对**:
  · 这两条是 **36 条逾期未闭环**里唯一两条「**验证已完成但状态没落账**」的:
    - verify_result 已经是 'pass'
    - verify_by = main, verify_date 已有
    - owner = sw-lead ⇒ ★**verify_by != owner ⇒ 验证分离成立** (C3 判据过)
    - 但 status 还停在 `fixed` ⇒ ★**C4 口径把 fixed 算作逾期未闭环** ⇒ 它们白占两个逾期名额
  · ★**这不是"改判据糊掉逾期"**: 判据一个字没动, 是**把早就做完的验证落账**。

★★**本轮我自己做的独立复验 (不采信 11-02/11-04 的旧回执)**:
  · ISS-145: `SW/DEMO_OD_PIPELINE_SPEC.md` = 675 行 / 59666 B
    ⇒ **7 章齐全** (§1 模型 / §2 推理运行时 / §3 后处理与画框 / §4 显示通路 / §5 帧率与延迟打点 /
      §6 验收判据 / §7 两条路径对比) + **附录 A 待核清单** + **附录 B 下一步** ⇒ 结构与 fix_ref 一致
    ⇒ `python3 SW/tools/demo_timing_check.py` ⇒ **rc=0 (20/20)** (规格结构未被后续改动破坏)
    ⇒ ★**注意**: fix_ref 里写的 "51KB / 624 行" 是 11-02 的快照; ★**11-03 的两处订正后文件长到 675 行**
      ⇒ fix_ref 的行数是**历史值**, 不是错 ⇒ 但要在 note 里说清, 不然下一个人会以为文件被截了
  · ISS-179: `SW/DISPLAY_FRAME_COUNTER.md` (6338 B) + `SW/PHONE_E2E_LATENCY_METHOD.md` (6738 B)
    ⇒ 帧计数器 **§5 自证 5 条判据 S1~S5 齐全** (连续无跳变 / 同帧 / 时间戳单调 / 关开关画面逐字节相同 / 不碰 U-V)
    ⇒ 手机指引 **重复 ≥10 次取中位数报 ±1 帧 / 记录模板 / 4 类误差源 / 建议判据 (中位数 ≤60ms · p95 ≤80ms)** 齐全

★★**两条的残项 (都写进 note, 不藏)**:
  · ISS-145: 板端 acc 复现链 ⇒ **已改挂 ISS-155 / ISS-169 (都还 open)** ⇒ ★**本单不背这条债**
  · ISS-179: **代码实现 (烧帧计数器) 不在本单范围** —— 等 RK3572 板/模组到手才有真画面可烧字
    ⇒ ★**板到位触发 = ISS-181 (自研 demo 主板可下单) / ISS-169** ⇒ ★**本轮不开新单**
    (★**理由**: 现在开一条 owner=sw-lead 的 open 单, 下一轮 advance.py 就会派它 ⇒ ★**而 sw-lead 此刻正在跑
      ISS-137 rev3 复验** ⇒ ★**一个 agent 两个写会话 ⇒ 正是本仓铁律里踩过 3 次的坑** ⇒ ★**故留到板到位再开★)

★★**纪律 (一条不放松)**:
  ① flock(state/.issue_log.lock) + **锁内重读** + **原子写** (tmp + fsync + os.replace)
  ② **只碰 ISS-145 / ISS-179 这两条的 status + verify_date + note** —— 其余 179 条逐字段比对, 变了就回滚
  ③ **不改 verify_result** (本来就是 'pass', 本脚本只确认它是 pass 才允许动)
  ④ 不碰 STATE.yaml / 分片 / PROJECT_TRACKER.md / §0 锁死表 / 任何交付物
  ⑤ 不发邮件 / 不联系供应商 / 不下采购单
  ⑥ ★**不改 ISS-137** (它正在被 sw-lead rev3 复验, 本脚本不得碰它的 note/status)

用法:
  python3 state/_advance_145_179_20261111.py --dry-run
  python3 state/_advance_145_179_20261111.py
"""
from __future__ import annotations

import fcntl
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-11"
TARGETS = ("ISS-145", "ISS-179")
FORBIDDEN = ("ISS-137",)   # ★正在被 sw-lead 复验, 绝对不碰★

NOTES = {
    "ISS-145": (
        "★2026-11-11 03:2x 项目总工 (main = 本单 verify_by) **补做独立复验 + 落账** (fixed → verified):\n"
        "  ★**为什么现在做**: verify_result 早在 2026-11-02 就是 'pass'、verify_by 已有、owner=sw-lead ⇒ "
        "**验证分离成立 (C3 过)**; ★**但 status 还停在 fixed ⇒ C4 口径把它算作逾期未闭环** ⇒ "
        "★**本轮是补落账, 不是改判据** (判据一个字没动)\n"
        "  ★**我本轮自己复的 (不采信 11-02 的旧回执)**: `SW/DEMO_OD_PIPELINE_SPEC.md` = **675 行 / 59666 B** ⇒ "
        "**7 章齐全** (§1 模型 / §2 推理运行时 / §3 后处理与画框 / §4 显示通路 / §5 帧率与延迟打点 / "
        "§6 验收判据 / §7 两条路径对比) + **附录 A 待核清单** + **附录 B 下一步** ⇒ 结构与 fix_ref 一致; "
        "`python3 SW/tools/demo_timing_check.py` ⇒ **rc=0 (20/20)** ⇒ 规格结构未被后续任何改动破坏\n"
        "  ★**一处要说清的 (不是缺陷)**: fix_ref 写的 '51KB / 624 行' 是 **2026-11-02 的快照值** ⇒ "
        "★**11-03 项目总工/sw-lead 订正了两处口径 (rk3572 不是合法 target / F1 差 0.0090) 后文件长到 675 行** ⇒ "
        "★**fix_ref 的行数是历史值, 不是文件被截**\n"
        "  ★**残项 (不藏)**: 本单的下一步 (第 0 步 = 恢复构建环境) **已改挂 ISS-147 (已 verified)**; "
        "**板端 acc 复现链已改挂 ISS-155 / ISS-169 (都还 open)** ⇒ ★**本单不背这条债**\n"
        "  ★**状态机**: fixed → **verified** (★**不进 closed**: 板端链路未跑通前, 规格只是'已交付且已验收', "
        "不等于'demo 板 OD 管线已打通' ⇒ ★**别把这条读成'管线跑通了'**)\n"
        "  ★**边界**: 未改任何交付物 (规格/脚本/RKNN_BENCH 一个字节没动) · 未改别人分片 · 未改 §0 锁死表 · 未发邮件"
    ),
    "ISS-179": (
        "★2026-11-11 03:2x 项目总工 (main = 本单 verify_by) **补做独立复验 + 落账** (fixed → verified):\n"
        "  ★**为什么现在做**: verify_result 早在 2026-11-04 就是 'pass'、verify_by 已有、owner=sw-lead ⇒ "
        "**验证分离成立 (C3 过)**; ★**但 status 还停在 fixed ⇒ C4 口径把它算作逾期未闭环** ⇒ "
        "★**本轮是补落账, 不是改判据**\n"
        "  ★**我本轮自己复的 (不采信 11-04 的旧回执)**: "
        "`SW/DISPLAY_FRAME_COUNTER.md` (6338 B) + `SW/PHONE_E2E_LATENCY_METHOD.md` (6738 B) ⇒ "
        "帧计数器 **§5 自证 5 条判据 S1~S5 齐全** (帧号连续无跳变 / 与 t_display 同帧 / 时间戳单调不减 / "
        "关开关后画面逐字节相同 / 不碰 U-V 只改 Y 平面) ⇒ 手机指引 **重复 ≥10 次取中位数报 ±1 帧 / 记录模板 / "
        "4 类误差源 / 建议判据 (中位数 ≤60ms · p95 ≤80ms)** 齐全 ⇒ 两份文档都达到 desc 的交付要求\n"
        "  ★**残项 (不藏)**: ★**代码实现 (真正把帧号烧进 Y 平面) 不在本单范围** —— 等 RK3572 板/模组到手才有真画面可烧字\n"
        "  ⇒ ★**板到位触发 = ISS-181 (自研 demo 主板可下单) / ISS-169** ⇒ ★**本轮不开新单**\n"
        "  ⇒ ★**★为什么现在不开**: 现在开一条 owner=sw-lead 的 open 单, 下一轮 advance.py 就会派它 ⇒ "
        "★**而 sw-lead 此刻正在跑 ISS-137 rev3 复验** ⇒ ★**一个 agent 两个写会话 = 本仓铁律里已踩过 3 次的坑** "
        "⇒ ★**故留到板到位再开**\n"
        "  ★**状态机**: fixed → **verified** (★**不进 closed**: 本单交的是**规格 + 作业指引**两份文档, "
        "**代码实现与端到端实测都还没做** ⇒ ★**别把这条读成'手机测延时已经能用了'**)\n"
        "  ★**边界**: 未改任何交付物 · 未改别人分片 · 未改 §0 锁死表 · 未发邮件"
    ),
}


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
            before = {i.get("id"): dict(i) for i in issues}

            for tid in TARGETS:
                t = next((i for i in issues if i.get("id") == tid), None)
                if t is None:
                    print(f"❌ 找不到 {tid}")
                    return 2
                # ★**落账前置条件 (三条, 缺一条就不动)**★
                if t.get("verify_result") != "pass":
                    print(f"❌ {tid}: verify_result={t.get('verify_result')} (必须 'pass') ⇒ 不动")
                    return 2
                if not t.get("verify_by"):
                    print(f"❌ {tid}: verify_by 缺 ⇒ 不动")
                    return 2
                if t.get("verify_by") == t.get("owner"):
                    print(f"❌ {tid}: verify_by == owner ⇒ 违反验证分离 ⇒ 不动")
                    return 2
                if not t.get("fix_ref"):
                    print(f"❌ {tid}: fix_ref 缺 ⇒ 不动")
                    return 2
                if t.get("status") != "fixed":
                    print(f"⏭  {tid}: status={t.get('status')} (不是 fixed) ⇒ 跳过")
                    continue
                print(f"✅ {tid}: 前置条件全过 (verify_result=pass · verify_by={t.get('verify_by')}"
                      f" != owner={t.get('owner')} · fix_ref 在位) ⇒ fixed → verified")
                t["status"] = "verified"
                t["verify_date"] = TODAY
                t["note"] = (t.get("note") or "") + "\n" + NOTES[tid]

            # ★★**只允许这 2 条变, 其余 179 条必须逐字段相同 (含 ISS-137!)**★★
            changed = []
            for i in issues:
                iid = i.get("id")
                if iid in TARGETS:
                    continue
                if before.get(iid) != i:
                    changed.append(iid)
            if changed:
                print(f"❌ 意外改动了别的 issue: {changed} ⇒ 回滚 (不写盘)")
                return 2
            print(f"✅ 其余 {len(before) - len(TARGETS)} 条 issue 逐字段比对无变化"
                  f" (★含 ISS-137 —— 它正在被 sw-lead 复验, 本脚本没碰★)")

            out = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=200)
            if dry:
                print("--- dry-run: 不写盘 ---")
                return 0
            atomic_write(LOG, out)
            print(f"✅ 已写入 {LOG}")
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)

    # ★写盘后再回读验证★
    with open(LOG, encoding="utf-8") as f:
        again = yaml.safe_load(f.read())
    ok = 0
    for tid in TARGETS:
        t = next(i for i in again["issues"] if i.get("id") == tid)
        if t.get("status") == "verified" and t.get("verify_date") == TODAY and t.get("verify_result") == "pass":
            print(f"  ✅ {tid}: status=verified · verify_date={TODAY} · verify_result=pass")
            ok += 1
        else:
            print(f"  ❌ {tid}: {t.get('status')}/{t.get('verify_date')}/{t.get('verify_result')}")
    t137 = next(i for i in again["issues"] if i.get("id") == "ISS-137")
    if t137.get("status") == "fixed" and t137.get("verify_result") is None:
        print("  ✅ ISS-137: status 仍 fixed / verify_result 仍 null (没被本脚本碰)")
        ok += 1
    else:
        print(f"  ❌ ISS-137 被本脚本碰了: {t137.get('status')}/{t137.get('verify_result')}")
    print(f"写盘后回读自检: {ok}/3 通过")
    return 0 if ok == 3 else 2


if __name__ == "__main__":
    sys.exit(main())
