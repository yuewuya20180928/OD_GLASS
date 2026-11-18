#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cron 775d9893 (ARS45 继续执行后继计划) 2026-11-17 08:2x
★**开 ISS-280 → hw-lead (先落 fixing, 再 spawn)** ★
★ISS-278 / ISS-279 保持 fixing (08:14 派出, 被 08:22:12 网关重载截断 ⇒ 盘上只有骨架 ⇒ 本轮【续做重派】, 不改 status, 只补 dispatch_log)★

★**纪律**: flock(state/.issue_log.lock) + ★**锁内重读** + ★**原子写** (tmp + fsync + os.replace)
★**只碰**: 新增 ISS-280 一条 (status=fixing) + dispatch_log 追加 3 条 ⇒ 其余 issue 逐字段比对, 变了就回滚
★**不碰**: 真源 / 分片 / 板 / 网表 / 脚表 / BOM / 任何门禁脚本 / 任何交卷单 / PROJECT_TRACKER §0
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_0830_cron_775d_open280"
TODAY = "2026-11-17"
BRIEF_PATH = os.path.join(HERE, "dispatch_briefs", "ISS-280_hw_commit_order_guard.md")


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


ISS280 = {
    "id": "ISS-280",
    "title": ("★★[★新主线·PCB 线·纯分析+作业包订正+机器闸类] ★★「板只改一次」的【提交时序守卫】★★ "
              "⇒ ★**作业包 v3 §0/§6.1 把【会产出留证产物的步 S9/S10/S12/S13】和【只改板的步 S1/S2/S3/S6/S7】"
              "混进了同一个「不投板也能做完」的集合, 且 §6.1 断言「拍完只重跑 S8 之后的链, 板本体不用再改」★★ "
              "⇒ ★**但 §6.2 自己写着 S4 (ESD 封装/位置/网表) 也要改板 ⇒ 照字面执行 = 板 md5 变两次 + "
              "Gerber/留证链/盖章/发布全白跑 ⇒ 破「板只改一次」铁律** ★ ⇒ ★**⇒ 本单 = 把它一般化 + 给它一道机器闸 "
              "(板 md5 变更次数 ≤ 1)** ★"),
    "severity": "high",
    "source_blocker": None,
    "source_agent": "main",
    "desc": ("★main 2026-11-17 08:2x 本机实读作业包 §0/§6.1/§6.2 (逐行, 不抄交卷报告)★\n"
              "★**① §6.1 末行**: 「⇒ 【不投板也能做完的集合 = S1 + S2 + S3 + S6 + S7 + S9 + S10 + S11 + S12 + S13】」★\n"
              "★**② §6.1 结句**: 「这一趟做完, 板子的【位号/内容/布局/可装配性/DNP/投产包/留证链】全部锁死, "
              "剩下 S4 + S8 只等老板拍板 → ★拍完只重跑 S8 之后的链, 板本体不用再改★」★\n"
              "★**③ §6.2 自己写着**: 「S4 | 卡在【老板】 | 等 W-1/W-2 | ★不拍 ⇒ D_ESD_USB_D 的封装/位置/网表都不能定 "
              "⇒ ★板必须再改一次★」★\n"
              "★**④ ⇒ 三类步**: A 类改板步 (S1/S2/S3/S6/S7 + 卡老板的 S4/S8) · B 类留证产物终段步 (S9/S10/S12/S13) · "
              "C 类只读闸 (S11) ⇒ ★**B 类必须最后跑** ⇒ 现在的「能先做的」只有 A 类里不卡老板的 S1/S2/S3/S6/S7** ★\n"
              "★**⑤ 现在没有任何一道闸能判「板 md5 变了几次」**: chain_gate 只判「产物比板新」(mtime 口径, 且 ③ PCB 那环现在本来就红) "
              "· ISS-277 的 preflight 闸判「板侧项有没有漏进作业包」· 都不判时序 ⇒ 「板只改一次」这条最贵的铁律现在靠人记着★"),
    "owner": "hw-lead",
    "reporter": "main",
    "raised": "2026-11-17",
    "due": "2026-11-20",
    "status": "fixing",
    "external": False,
    "need_keys": [],
    "fix_ref": "state/dispatch_briefs/ISS-280_hw_commit_order_guard.md",
    "verify_by": None,
    "verify_result": None,
    "verify_date": None,
    "note": ("2026-11-17 08:2x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮 08:2x 本机实读作业包 §0/§6.1/§6.2** ★\n"
             "⇒ ★**任务书 `state/dispatch_briefs/ISS-280_hw_commit_order_guard.md`** ★\n"
             "★**hw-lead 名下本轮无 open 队列 (ISS-277 已于 08:1x 落 verified ⇒ 真空; 会话实测无 running) ⇒ 本单是本轮给 hw-lead 的活** ★\n"
             "★**类别**: 内部活 · PCB 线 · 纯分析 + 作业包追加式订正 + 机器闸类 ⇒ ★**零写板 · 零落表 · 零改既有判据脚本** ⇒ 不是老板级拍板★\n"
             "★**不代拍**: P7 / W-1 / W-2 / W-4 / A1 / 座体高度 h / LED 亮度档 —— 一条都不代拍★"),
    "dispatched_at": "2026-11-17",
}


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            with open(LOG, encoding="utf-8") as f:
                log = yaml.safe_load(f) or {}
            issues = log.get("issues") or []
            before = {i.get("id"): dict(i) for i in issues}

            if "ISS-280" in before:
                print("⚠ ISS-280 已存在 ⇒ 幂等, 只补 dispatch_log")
                new_issue = None
            else:
                brief = open(BRIEF_PATH, encoding="utf-8").read()
                new_issue = dict(ISS280)
                new_issue["task_brief"] = brief
                issues.append(new_issue)
                log["issues"] = issues
                print("✅ 新开 ISS-280 (owner=hw-lead · status=fixing · brief %d 字)" % len(brief))

            dl = {}
            if os.path.exists(DL):
                with open(DL, encoding="utf-8") as f:
                    dl = yaml.safe_load(f) or {}
            disp = dl.setdefault("dispatches", [])
            entries = [
                {"issue": "ISS-280", "agent": "hw-lead", "at": TODAY,
                 "brief": "★**续做重派 (★08:22:12 网关重载把 08:14 那一派整段截断 ⇒ 盘上只有交卷单骨架 877 B / 1965 B ⇒ 零交付物★) ⇒ "
                          "★**从盘上骨架继续, 不要从零重做**★ · "
                          "★**续做纪律**: 第一件事先 write 交卷单骨架 · 长任务 nohup 后台 · 单条 exec ≤120 秒 · 每 10 分钟写盘 · "
                          "分片写完 grep 校验★",
                 "job": "cron 775d9893 (ARS45 继续执行后继计划) · 续做重派"},
            ]
            for e in entries:
                disp.append(e)
                print("  dispatch_log += %s → %s" % (e["issue"], e["agent"]))

            shutil.copy2(LOG, BAK)
            atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))
            atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))

            # ---------- 自检: 其它 issue 逐字段比对 ----------
            with open(LOG, encoding="utf-8") as f:
                after = yaml.safe_load(f) or {}
            aiss = {i.get("id"): i for i in (after.get("issues") or [])}
            drift = []
            for iid, it0 in before.items():
                it1 = aiss.get(iid)
                if it1 is None:
                    drift.append("%s 消失" % iid)
                    continue
                if it0 != it1:
                    diffk = [k for k in set(list(it0) + list(it1)) if it0.get(k) != it1.get(k)]
                    drift.append("%s %s" % (iid, diffk))
            print("  漂移条数 =", len(drift), drift[:5])
            if drift:
                print("❌ 有漂移 ⇒ 回滚")
                shutil.copy2(BAK, LOG)
                return 3
            print("✅ 落盘 OK (锁内重读 + 原子写 + 逐字段比对)")
            return 0
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


if __name__ == "__main__":
    raise SystemExit(main())
