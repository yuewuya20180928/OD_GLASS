#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_0450_iss261_delivery_truth_fix.py
★main (moli) 2026-11-17 04:5x (cron 775d9893 继续执行后继计划)★
★① ISS-261 (main · 投递口径① 的 mode=none 归类) open → fixing → fixed (★自做自验, 但按验证分离不落 verified★) ★
★② 新开 ISS-272 (sw-lead · 独立复核 ISS-261 的口径①改判) ⇒ 验证分离 (★C3: verify_by ≠ owner★) ★

★★**为什么是 main 自己干 (★不是偷懒, 是没人可派★)** ★★
· ★**本轮 advance.py 的 `internal` 是空的** ⇒ 根因 = ★**三个总工名额全被 ISS-269/270/271 占着 (★一 agent 同时只允许一个写会话·★sessions_list 实测三条会话 status=running★)** ★
· ★**ISS-261 的 owner 本来就是 main** (★登记时就是 main 2026-11-16 22:4x 心跳自检撞到时开的★) ⇒ ★**它一直排在 main 自己的活池里, 没有任何总工能接** ★
· ⇒ ★**本轮 main 的 cron 槽位除派活外本来就是空的 ⇒ 顺手把这条「唯一的假故障源」修掉** ★

★★**为什么值得修 (★不是洁癖, 是「狼来了」★)** ★★
· ★**修前实测输出**: 「ARS45 状态速报 (每小时推微信, 老板手机上看状态)」⇒ ★**送到 0 · 没送到 12 / 12** ★
· ★**而真实情况**: ★**这 4 个 job 的 `delivery.mode` 全是 `none`** (★老板 2026-11-04 09:5x 关掉微信推送★) ⇒ ★**delivered=false 是预期行为, 零投递故障** ★
· ★**⇒ 每次投递自检都在打「像是推送挂了」的假象 ⇒ 老板看到的就是噪声** ★

★★**修法的边界 (★本单自己定的★)** ★★
· ★**只动分类** (★`state/delivery_truth.py` 的 `classify_run`) ⇒ ★**不改任何告警阈值 · 不动 A/B/D 三类判据 · `state/delivery_health.py` 一个字节没改** ★
· ★**反向用例**: ★**`--selftest` 31 条断言 (7 纯函数 + 4 job × 6 端到端) rc=0** ★
· ★**隔离性自证**: ★**同一份真实 run 记录修前/修后各跑一次 `delivery_health.py` ⇒ diff 只有 4 行口径① 变了** ★
· ★**⇒ 但「验证分离」规定 verify_by ≠ owner ⇒ ★**main 不能自签 verified ⇒ 新开 ISS-272 交给 sw-lead 复核** ★

★★**本轮共同边界** ★★
零外发 · 零采购 · 零写板 · 零落表 · 零改网表/脚表/BOM · 不写别人的分片 · 不改 PROJECT_TRACKER.md §0 · 不替老板拍板 ★
"""
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-17"

BRIEF_272 = open(os.path.join(HERE, "dispatch_briefs",
                               "ISS-272_sw_delivery_truth_review.md"), encoding="utf-8").read()

FIX_261 = (
    "★main 2026-11-17 04:5x 落账 (★依据 = main 本机实跑, 不抄任何交卷报告★) ★\n"
    "★**① 病灶 (修前实测原文)**: `python3 state/delivery_health.py` ⇒ ★**「ARS45 状态速报 (每小时推微信, 老板手机上看状态)」= 送到 0 · 没送到 12 / 12** ★"
    "⇒ ★**4 个 job 的「本来就不投」这一列结构上恒为 0** ★ ⇒ ★**根因在 `state/delivery_truth.py` 的分类顺序**: ★**`elif delivered is False` 先于 `else: no_delivery` 命中** ★ "
    "⇒ ★**而 OpenClaw 在 `delivery.mode == 'none'` 时照样把 `delivery.delivered` 写成 `false`** (★老板 2026-11-04 09:5x 关掉微信推送·★这 4 个 job 的 mode 全是 none★) "
    "⇒ ★**那个写着「mode=none ⇒ 本来就不投」的分支是死代码, 永远走不到** ★\n"
    "★**② 修法 (★只动分类, 别的一个字没动★)**: ★**新增纯函数 `classify_run(status, delivered, mode)`** ★ "
    "⇒ 分类顺序 = `status=error`⇒run_error → `delivered is True`⇒delivered → ★**`mode=='none'`⇒no_delivery (★修点★)**★ → `delivered is False`⇒not_delivered → 其余⇒no_delivery ★ "
    "⇒ ★**`runs_view(job_id, n, mode=None)` 加 mode 形参 + `collect()` 把 `d.get(\"mode\")` 传进去** ★\n"
    "★**③ 反向用例 (★ISS-261 登记时点名要的那条·已落进脚本★)**: ★**`python3 state/delivery_truth.py --selftest` ⇒ rc=0 · 31 条断言 (7 纯函数 + 4 job × 6 端到端)** ★ "
    "⇒ ★**C1 = mode=none + delivered=false ⇒ 必须落 `no_delivery` (★「没送到」挪到「本来就不投」★)** ★ · ★**C2 = mode=announce + false ⇒ 仍落 `not_delivered` (★行为逐字不变★)** ★ "
    "⇒ ★**E2E 端到端: 拿盘上真 run 记录跑 `collect()` ⇒ mode=none 的 job「没送到」必为 0 且「本来就不投」= 非 error 轮数; 四个计数与逐轮 verdict 逐项自洽** ★\n"
    "★**④ 修后实测 (★同一份 run 记录★)**: ★**「状态速报」那一行 = 没送到 0 · 本来就不投 12 (★修前是 没送到 12 · 本来就不投 0★)** ★ · "
    "另三行 = 没送到 0 · 本来就不投 4 / 8 / 7 ⇒ ★**「送到 0 · 没送到 12」那个假象消失** ★\n"
    "★**⑤ 隔离性自证 (★本单最要紧的一条★)**: ★**同一份真实 run 记录, 修前/修后各跑一次 `state/delivery_health.py`, 逐行 diff** ★ "
    "⇒ ★**只有 4 行口径① 变了; A 类 / B 类 / D 类 / 口径② / 结论行 逐字节不变** ★ ⇒ ★**判据改动零外溢** ★\n"
    "★**⑥ H-1 台账**: ★**改前 md5 `00ff09721fad2b1fa8621d5af5573f7f` ⇒ 改后 md5 `8dad8b39d873b3d930acb1c076e240cb`** ★ "
    "· ★**备份 `state/.bak_delivery_truth_20261117_0435_iss261.py` (★逐字节相同★)** ★ · ★**台账三处互指: 脚本 docstring「H-1 台账 · ISS-261」段 + 交卷单 + 本 note** ★ "
    "⇒ ★**`delivery_truth.py` 不在任何受保护 md5 台账里 ⇒ 无外部台账需连带重基线** ★\n"
    "★**⑦ 交卷单**: ★**`HANDOFF/2026-11-17_main_ISS261_投递口径mode_none归类修复.md`** (★B1~B6 六块齐全 + 原始 diff + 31 条断言清单 + 自证复现命令★) ★\n"
    "★**⑧ 零副作用 (★本机实跑 md5★)**: ★**受保护 5 件逐字节未变** ★ —— 板 `611b869e13518c3c023fb178f91a0075` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · "
    "脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**零写板 · 零落表成立** ★ "
    "· ★**`state/delivery_health.py` md5 逐字节未变 (★A/B/D 三类判据一个字没动★)** ★\n"
    "★**⑨ 为什么只落 `fixed` 不落 `verified`**: ★**`state/issue_check.py` C3「验证分离」规定 `verify_by` 不得等于 `owner` ⇒ 本单 owner = main ⇒ main 不能自签 verified** ★ "
    "⇒ ★**已新开 ISS-272 (sw-lead) 做独立复核 ⇒ 复核通过后由 main 落 verified** ★ (★先例: ISS-095 / ISS-252 两条 main-owned 单同样停在 `fixed` 等复核★)\n"
    "★**边界**: ★**零外发 · 零采购 · 零写板 · 零落表 · 零改任何告警阈值 · A/B/D 三类判据零改动 · 不写别人的分片 · 不改 PROJECT_TRACKER.md §0 · 不替老板拍板 · 不自签 verified** ★"
)


def atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main():
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    by_id = {it.get("id"): it for it in issues}

    # ---------- ① ISS-261: open → fixing → fixed ----------
    it = by_id["ISS-261"]
    assert it["status"] == "open", "ISS-261 预期 open, 实际 %s" % it["status"]
    # 状态机: open → fixing (合法) → fixed (合法) ⇒ 两步都走, 不跳级
    it["status"] = "fixing"
    it["note"] = (str(it.get("note") or "") + "\n\n" + FIX_261)
    it["fix_ref"] = "HANDOFF/2026-11-17_main_ISS261_投递口径mode_none归类修复.md"
    it["status"] = "fixed"
    it["verify_by"] = "sw-lead"      # ★验证分离: ≠ owner(main)★
    it["verify_result"] = None
    it["verify_date"] = None
    it["dispatched_at"] = None

    # ---------- ② 新开 ISS-272 (sw-lead · 独立复核) ----------
    assert "ISS-272" not in by_id, "ISS-272 已存在"
    issues.append({
        "id": "ISS-272",
        "title": ("★★[门禁/运维侧·独立复核·内部活] ★★**独立复核 main 亲手改的 `state/delivery_truth.py` 口径① 归类** "
                  "★(★修前「送到 0 · 没送到 12」是假故障: 4 个 job 的 `delivery.mode` 全是 `none`·★老板 11-04 09:5x 关掉微信推送★) "
                  "★⇒ 验证分离 (★C3: verify_by ≠ owner★) ⇒ main 不能自签 verified ⇒ 交 sw-lead 复核★** ★★"),
        "severity": "medium",
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-20",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": ("2026-11-17 04:5x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮 04:2x~04:5x 本机实跑 + ISS-261 登记时点名的反向用例要求** ★ "
                 "⇒ ★**任务书 `state/dispatch_briefs/ISS-272_sw_delivery_truth_review.md`** ★\n"
                 "★**本单要验的东西 (★四件★)**: ★**① 独立复现 main 的验收 (自己跑 selftest + 自己 swap 修前修后做 diff·★不许只信 main 的结论★)** ★ "
                 "· ★**② 反向用例加压 (★最值钱的一件★)**: ★**自造假 run 记录喂给 `classify_run` ⇒ 逐条问「这个输入下真故障会不会被藏起来」⇒ ★**至少覆盖: mode=none+status=error (job 自己挂了必须仍算 run_error) · mode=none+delivered=true (真送到必须仍算 delivered) · mode 字段缺 (按 announce 判) · mode=announce 连着 3 轮 false (「没送到」必须 = 3·★不许被洗成 0★)** ★** ★ "
                 "· ★**③ 假故障会不会被藏起来 (★不许含糊: 「mode=none 的 job 真坏了, 老板能不能看见?」⇒ 答 能/不能 + 为什么 + 缺口★)** ★ "
                 "· ★**④ 交卷单 + 分片 (frag_write.py) + 一句复核结论 (★main 拿这句话才能把 ISS-261 从 fixed 落 verified★)** ★\n"
                 "★**为什么必须有人独立验 (★验证分离·★C3★)**: ★**改的是「投递健康」这个判据本身 ⇒ 万一改错 ⇒ 真故障会被吞掉 ⇒ ★**这是会骗到老板的那一类 bug** ⇒ 必须有人站在 main 之外再看一遍** ★\n"
                 "★**sw-lead 名额被 ISS-270 占着 (★本单 04:5x 实测其会话 status=running★) ⇒ 本单在队列里排队, 等名额空出来再派 ⇒ ★**不抢跑·不许与 ISS-270 并行写同一分片**★** ★\n"
                 "★**边界**: ★**零外发 · 零采购 · 零写板 · 零落表 · 零改 `state/delivery_health.py` (★A/B/D 三类判据不是本单地界★) · 不许自签 issue_log · 不写别人的分片 · 不替老板拍板** ★"),
        "dispatched_at": None,
        "task_brief": BRIEF_272,
    })

    bak = os.path.join(HERE, "issue_log.yaml.bak_20261117_0450_iss261_fix")
    shutil.copy2(LOG, bak)
    atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
    atomic_write(os.path.join(HERE, "tasks", "advance_iss272.md"), BRIEF_272)

    print("✅ ISS-261: open → fixing → fixed (★两步都走·不跳级★) · fix_ref 已挂 · verify_by=sw-lead (★验证分离·不落 verified★)")
    print("   ISS-261 note 追加: 病灶 + 修法 + 31 条断言 + 修前修后 diff + H-1 台账 + md5 前后值")
    print("✅ 新开 ISS-272 (sw-lead · 独立复核口径①改判) — status=open (★等 sw-lead 名额★)")
    print("   备份: %s" % bak)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
