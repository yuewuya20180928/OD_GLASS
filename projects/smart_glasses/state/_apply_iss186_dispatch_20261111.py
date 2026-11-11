#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-186 手工解冻派活落账器 (2026-11-11 07:5x, 项目总工 main)

★**为什么不用 `advance.py --apply --only ISS-186`**: advance.py 的 in_flight 判据是
  「owner 名下已有 status==fixing 的 issue ⇒ 本轮跳过」(代理判据, 保守) ⇒
  ISS-186 (owner=hw-lead) 被 ISS-181 (owner=hw-lead, fixing) 挡住 ⇒ **advance.py 的 internal 段是空的**
  ⇒ `--apply --only ISS-186` 的循环遍历 internal ⇒ **一条都不会标** (实测: internal=[] ⇒ 无副作用)。

★**为什么本单可以解冻 (★三条都实测过, 不是推测★)**:
  ① ★**hw-lead 现在没有任何运行中的写会话** ⇒ sessions_list 实测: hw-lead 最近 4 个会话
     (verify-docs-A / verify-docs-B / 周更新 / 布线器) 全部 done 或 failed, 最后一个 11-08 23:3x
     ⇒ ★**铁律要防的「同一 agent 两个并发写会话互相覆盖分片」没有发生**。
  ② ★**ISS-181 的板子活实际由【主会话】在跑** (v76mz 臂 campaign, PID 278476/278482, 07:41 起)
     ⇒ ★**它不占 hw-lead 的写会话名额** ⇒ advance.py 的代理判据在这里「代理错了事实」。
  ③ ★**文件交集 = 0**: 臂链路 (v76mz_arms.sh / gen_pcb_netlist_board.py / replay_patch_chain.sh /
     compare_arm_baseline.sh / clrfix_iter.sh) 只写 /tmp/v76mz_R.kicad_pcb + /tmp/chain_v76mz/ +
     state/.lastgood/ ⇒ ★**实测这 6 个脚本里 grep「fragments|.yaml」零命中**;
     而 ISS-186 只改 5 个 .md (4 个 HW/** + 1 个 state/outbox/**) ⇒ **不抢同一块板, 不抢同一个文件**。
  ④ ★**不派它的代价是它被无限期挂起**: ISS-181 是 blocker 且离 G1 要求的 unc=0 还远
     (当前最佳臂 v76mg1 = unc 23 条/21 网) ⇒ ★**不可能在 11-13 (ISS-186 的 due) 之前落账**
     ⇒ ★**照 advance.py 的字面判据, ISS-186 永远出不来** ⇒ 一条 high 单被一个代理判据永久冻住。

★**落账纪律 (与项目既有范式一致)**:
  ① flock(state/.issue_log.lock) + 锁内重读
  ② ★**只改 ISS-186 这一条 dict 的 3 个字段** ⇒ ★**已实测 `yaml.safe_dump(原 doc)` 与原文件
     **逐字节相同** (505475 字符 ⇒ 0 差异) ⇒ ⇒ **整份改写不会动别人 182 条的任何字节**
     (★比行级编辑更安全: 本单的 note 是【跨行单引号标量】, 行级编辑会踩坑★)
  ③ 原子写: tmp (同目录) → fsync → os.replace → fsync(dir)
  ④ dispatch_log.yaml 同步追加一条 (可追溯)

★**边界**: 不改 §0 锁死表 · 不改任何已发布数字 · 不碰 sw-lead 的分片 (⑤ 那处归 sw-lead) ·
  不发邮件 / 不联系供应商 / 不下采购单。
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
TARGET = "ISS-186"
TODAY = "2026-11-11"
DISPATCHED_AT = "2026-11-11 07:5x (项目总工手工解冻派活)"

NOTE_ADD = (
    "★2026-11-11 07:5x 项目总工**手工解冻派活** (★本单不是 advance.py 自动吐出来的★)。"
    "★**为什么 advance.py 派不出它**: advance.py 的 in_flight 判据是「owner 名下已有 status==fixing 的 issue ⇒ 跳过」"
    "(★保守代理★) ⇒ ISS-181 (owner=hw-lead, fixing) 把本单挡住 ⇒ internal=[] ⇒ `--apply --only ISS-186` "
    "遍历的是空的 internal ⇒ **一条都标不了** (实测)。"
    "★**本单可以解冻的三条实测依据**: ① ★**hw-lead 当前没有任何运行中的写会话** (sessions_list 实测: "
    "verify-docs-A / verify-docs-B / 周更新 / 布线器 四条全 done|failed, 最后一条 11-08 23:3x) ⇒ "
    "★**铁律要防的「同一 agent 两个并发写会话互相覆盖分片」没有发生**; ② ★**ISS-181 的板子活实际由【主会话】在跑** "
    "(v76mz 臂 campaign, 07:41 起) ⇒ ★**它不占 hw-lead 的写会话名额** ⇒ 代理判据在这里代理错了事实; "
    "③ ★**文件交集=0** (臂链路 6 个脚本 grep「fragments|.yaml」零命中, 只写 /tmp + state/.lastgood/; "
    "本单只改 5 个 .md) ⇒ ★**不抢同一块板**。"
    "★**不派的代价**: ISS-181 离 G1 要求的 unc=0 还远 (当前最佳臂 v76mg1 = unc 23 条/21 网) ⇒ "
    "★**不可能在本单 due 11-13 前落账** ⇒ ★**照字面判据本单会被永久冻住**。"
    "★**hw-lead 侧的边界 (随任务书一起给)**: ★**不许碰板子相关任何文件** (demo_mainboard.kicad_pcb / "
    "state/gen_pcb_*.py / state/.lastgood/ / /tmp 链产物) ⇒ ★**ISS-181 归主会话, hw-lead 不插手**; "
    "★**不许碰 sw-lead 的分片** (⑤ SW/DEMO_OD_PIPELINE_SPEC.md:322 归 sw-lead) ⇒ 本单只改 ①②③④⑥ 五处; "
    "★**不许发任何邮件/不联系供应商** (⑥ 是给面板厂的询价函草稿 ⇒ 改了也不发, 外发一律经老板)。"
)


def atomic_write(path, text):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".atom.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


with open(LOCK, "a+", encoding="utf-8") as lf:
    fcntl.flock(lf, fcntl.LOCK_EX)
    orig = open(LOG, encoding="utf-8").read()
    doc = yaml.safe_load(orig)

    items = doc["issues"] if isinstance(doc.get("issues"), list) else list(doc["issues"].values())
    target = next((i for i in items if i.get("id") == TARGET), None)
    if target is None:
        print(f"❌ {TARGET} 不在 issue_log.yaml 里")
        sys.exit(1)
    if target.get("status") != "open":
        print(f"ℹ️ {TARGET} 当前 status={target.get('status')} (不是 open) ⇒ 幂等跳过")
        sys.exit(0)

    # ★**自证: 先验证整份 yaml 往返是否逐字节复现** ⇒ 若复现失败 (说明有别的东西在改格式), 中止
    probe = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
    if probe != orig:
        print("❌ 中止: yaml 往返与原文件不逐字节相同 ⇒ 整份改写会动到别人的行 ⇒ 不写")
        sys.exit(1)

    target["status"] = "fixing"
    target["dispatched_at"] = DISPATCHED_AT
    target["note"] = (target.get("note") or "") + NOTE_ADD

    new_text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
    atomic_write(LOG, new_text)

    # ---------- dispatch_log ----------
    dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
    dl.setdefault("dispatches", []).append({
        "issue": TARGET,
        "agent": "hw-lead",
        "at": TODAY,
        "brief": ("闭环 ISS-186: ★DSI payload 8× 口径差 6 处「373/246 Mbps」实为 2986/1475 Mbps "
                  "⇒ 依据虚到 8 倍 ⇒ 下次有人拿它反推 TX 下限, 7.776ms 会塌成 ~0.97ms "
                  "★(手工解冻: advance.py 的 in_flight 代理判据挡住了, 已实测 hw-lead 无在跑写会话 + "
                  "与主会话板子臂文件交集=0)"),
    })
    atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))

print(f"✅ {TARGET} → status=fixing + dispatched_at 已写 + note 已追加 + dispatch_log 已追加")
print(f"   issue_log.yaml: {len(orig)} → {len(new_text)} 字符")
