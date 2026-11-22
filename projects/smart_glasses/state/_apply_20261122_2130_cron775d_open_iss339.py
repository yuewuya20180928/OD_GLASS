#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-22 21:3x · 项目总工 moli

★**本轮一件事**: 新开并直接派出 ISS-339 (hw-lead) —— 【可比性前置闸】+【S8 布线归零目标名单重读器】

★**为什么本轮要开新单 (★依据全是本机实读·不抄任何 agent 报告★)**:
  · ★**队列排空**: `python3 state/advance.py --json` ⇒ `internal: []` · `approvals: []` · `waiting: 0`
    (★40 条待老板拍板项全部归老板, 不归三个总工 ⇒ advance.py 的 A 段本轮无货★)
  · ★**hw-lead 名额已释放**: ISS-337 已于 2026-11-22 21:16 被 main 签收 `verified` ⇒ 三总工名下 open=0 / fixing=0
  · ★**子会话全空**: `sessions_list` ⇒ hw-lead / sw-lead / mech-lead 都没有在跑的写会话
    (★hw-lead 最后一条 = ISS-337 cont2 · 21:08:44 status=timeout · abortedLastRun=true★)
  · ★**main 21:2x 已把两条机制级 need 裁完 (pm.yaml answers 76→79)**, 缺的只是【实现】:
      ① `iss337_band_truth_overrides_doc`  ⇒「`compare_arm_official.py` 不用改代码 ⇒ 只需在它前面加一道【可比性前置闸】」
      ② `iss337_rereread_zerocopper_denominator` ⇒「重读办法 = ① 用那一趟的真实基线板跑 unconnected 清单 ⇒ 得分母 N' ② 逐条标 [必需/可悬空/待定] + 有没有铜」
    ⇒ ★**这两条 need 是板那一趟 (S8 布线归零 unc 45→0) 开工前的两把尺子 ⇒ 现在做 = 纯分析 · 零写板★**

★**纪律**: 零写板 · 零落表 · 零改闸 · 零改生成器 · 零外发 · 不替老板拍板 · 不写别人的分片
★**幂等**: ISS-339 已存在 ⇒ 直接退出 (不重复开单)
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-22"

BRIEF_REL = "state/dispatch_briefs/ISS-339_hw_comparable_gate_and_s8_target_list.md"
BRIEF_PATH = os.path.join(os.path.dirname(HERE), BRIEF_REL)

ISS339 = {
    "id": "ISS-339",
    "title": (
        "★★[★新主线·PCB 线·纯分析+新建闸类·零写板] ★★【板那一趟 S8 布线归零的两把尺子: "
        "① 【可比性前置闸】(main 21:2x 已裁 need `iss337_band_truth_overrides_doc`: "
        "`compare_arm_official.py` 不用改代码 ⇒ 只需在它前面加一道可比性前置闸, 判据 = 归一化段数 [2300,3200] · "
        "铜长 [4600,5900]mm · 过孔 [380,520] ⇒ 越界即拦) + ② 【S8 目标名单重读器】"
        "(main 21:2x 已裁 need `iss337_rereread_zerocopper_denominator`: 在那一趟的真实基线板上跑 unconnected 清单 "
        "⇒ 得分母 N' ⇒ 逐条标 [必需/可悬空/待定] + 该网有没有铜)】★★ "
        "★**板只改一次 ⇒ 这一趟没开工 ⇒ 本单只出【两把尺子】, 一个字节都不许碰板**★ "
        "★**纯分析 / 新建闸类 · 零写板 · 零落表 · 零改闸 · 零重生成 · 零外发 · 不替老板拍板** ★"
    ),
    "severity": "high",
    "source_blocker": "ISS-337",
    "source_agent": "hw-lead",
    "desc": (
        "★**main 2026-11-22 21:2x 把 ISS-337 交回的三条机制级 need 裁完 (pm.yaml answers 76→79), 缺的只是【实现】★** ⇒ "
        "★**① 可比性前置闸**: 官方板与现役臂同带 (归一化段数 2649/2582 · 铜长 5726.9/5582.8 · 过孔 433/471) ⇒ "
        "老区间 [2400,2900]/[5400,5900]/[380,450] 会把官方板自己拦掉 ⇒ 区间真值 = `tmp/iss337/seg_parity_selfcheck.py` L59-61 ⇒ "
        "★**不许拿不可比的板刷闸的结论**★ ⇒ "
        "★**② S8 目标名单重读器**: 官方板那 24 条零铜网【不能直接当布线靶】(21 条在 v76mg1 上已有铜 ⇒ 两边都零铜只剩 3 条: "
        "CSI_D0_D0_N_SRC / CSI_D0_D2_N / CSI_D0_D3_N) ⇒ 必需性分级沿用 20:5x 已裁口径 (23 必需 = 15 差分腿 + 8 单端脚 / "
        "1 可悬空 FSIN_OUT / 0 待定) ⇒ 但【靶更小 ≠ 板子更好】⇒ "
        "★**判据顺序必须是: 先可比性 → 再名单 → 最后才看计数有没有变好**★ ⇒ "
        "★**v44/v46/v47/v48 四个臂打死同样三条差分对 = 布局级线索 ⇒ 没有两把尺子的那一趟会重演「计数变好、板子更烂」** ★"
    ),
    "owner": "hw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-23",
    "status": "fixing",
    "external": False,
    "need_keys": [],
    "task_brief": "★**ISS-339 任务书全文: `%s`** ★\n(★派活方已用 `python3 state/check_brief_commands.py --brief-file %s` 实跑 rc=0 ⇒ brief 里引用的路径/命令全部存在★)\n\n%s"
    % (BRIEF_REL, BRIEF_REL, open(BRIEF_PATH, encoding="utf-8").read()),
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": (
        "★**2026-11-22 21:3x · cron 775d9893 (ARS45 继续执行后继计划) 新开并直接派出 (★status 直接落 fixing ⇒ "
        "兄弟 job fb67af40 (队列自动派活) 的 advance.py 看不见 open 窗口 ⇒ 不会重复派 hw-lead★)** ★ "
        "★**开单依据 (★main 本机实读·不抄任何 agent 报告★)** ★ "
        "★**① 队列排空**: `state/advance.py --json` ⇒ internal=[] / approvals=[] / waiting=0 ⇒ A 段本轮无货 ⇒ "
        "★**按「开新单」处理 (让内部待办不断线 = 本 job 的存在意义)★** ★ "
        "★**② hw-lead 名额已释放**: ISS-337 于 2026-11-22 21:16 被 main 签收 verified ⇒ hw-lead 名下 open=0 / fixing=0 ★ "
        "★**③ 子会话全空**: `sessions_list` ⇒ hw-lead 最后一条 = ISS-337 cont2 · 21:08:44 status=timeout ⇒ 无在跑写会话 ⇒ 不违「一个 agent 同时只允许一个写会话」★ "
        "★**④ 活源**: main 21:2x 裁的两条机制级 need (pm.yaml answers 76→79) 已经把【判据】定死 ⇒ 缺的只是【实现】⇒ 两把尺子 ★ "
        "★**⑤ 派活纪律 (★main 21:16 教训·cont1 死于 token 限额 2056 · cont2 死于 run timeout 17.8 分钟★)**: "
        "brief 里已写死「每个交付物 = 一次 write 调用 · 不许写第一件之前跑任何探查 · 必跑项只许跑一次 · 先落 D1+D2 脚本再写页」★"
    ),
    "dispatched_at": TODAY,
}


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        if any(i.get("id") == ISS339["id"] for i in issues):
            print("· ISS-339 已存在 ⇒ 幂等退出 (不重复开单)")
            return 0

        shutil.copy2(LOG, LOG + ".bak_20261122_2130_cron775d_open_iss339")
        issues.append(ISS339)
        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {"dispatches": []}
        shutil.copy2(DL, DL + ".bak_20261122_2130_cron775d_open_iss339")
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-339",
            "agent": "hw-lead",
            "at": TODAY,
            "brief": "★PCB 线·纯分析+新建闸类·零写板: ①【可比性前置闸】(归一化段数 [2300,3200] · 铜长 [4600,5900]mm · 过孔 [380,520] ⇒ 越界即拦) "
                     "②【S8 布线归零目标名单重读器】(N' + 逐条 [必需/可悬空/待定] + 有无铜 + 两个分母口径 + 两边都零铜清单) ★",
            "job": "cron 775d9893 (ARS45 继续执行后继计划) · ★派活时刻 2026-11-22 21:3x · ★**status 直接落 fixing ⇒ 兄弟 job fb67af40 不会重复派** ★",
        })
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))

    print("✅ ISS-339 已开 (status=fixing, owner=hw-lead, due=2026-11-23)")
    print("   brief: %s (%d B)" % (BRIEF_REL, os.path.getsize(BRIEF_PATH)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
