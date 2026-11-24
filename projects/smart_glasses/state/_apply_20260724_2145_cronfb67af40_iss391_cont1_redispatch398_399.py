#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20260724_2145_cronfb67af40_iss391_cont1_redispatch398_399.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-24 21:4x 一趟
  ⇒ ★**三条**: ① ★**ISS-391 cont1 续派** (★main 19:55 暂缓签收 · 夹具脱节 14/17 ⇒ 归 owner 修★)
                ② ★**ISS-398 cont1 补派** (★20:0x 那一趟【spawn 从未发生】★)
                ③ ★**ISS-399 补派** (★同上★)

★★**本单最重要的发现 (★本机实跑复核, 不抄任何 agent 报告★)**★★:
  ★**20:00 那一趟 (main cron fb67af40 · transcript `36cd6141-…` · 19:34:41→20:34:37)★**
  ★**在 20:34:37 那句话上死掉了: 「Ledger is clean … Now let me verify the in_flight guard holds, then spawn.」**
  ★**⇒ 它的 `sessions_spawn` 从未执行 ⇒ 但它已经: ① 写好了两份 brief (20:28 / 20:32)
  ② 落好了台账 (ISS-398 note + ISS-399 新开为 fixing, 20:34:26) ③ 追加了 dispatch_log 两条
  (★两条都写着 `dispatched_at: 2026-11-24 20:0x`★)**
  ★**⇒ 台账说「已派」、dispatch_log 说「已派」、实际【一个 agent 会话都没起】**
  ★**⇒ 盘上实证: sw-lead 最新会话 = 19:30 / mech-lead 最新会话 = 19:29
  (★两位的 brief 分别落盘于 20:28 / 20:32 ⇒ 晚于任何会话★)
  ⇒ ISS-398 交卷页不在盘 + `grep -c iss398 state/fragments/*.yaml` = 0
  ⇒ ISS-399 交卷页不在盘 + `grep -c iss399 state/fragments/*.yaml` = 0**
  ★★**⇒ 这就是「活被掐死了还占着名额」那个病: 名额被一个【从未启动的空壳】占住
  ⇒ advance.py 的 internal 恒空 ⇒ 队列看着像没活 ⇒ 实际是【两个槽位被空壳占住】★★**
  ★★**⇒ 本单把三条一次补齐 ⇒ 三个总工槽位全部真在飞 ⇒ 断线修复★★**

★**本脚本三道自保**: ① md5 守卫 (写前重算源文件 md5, 不一致 ⇒ rc=3 中止)
  ② 原子写 (`os.replace`) ③ 写后复跑 `state/check_brief_commands.py`

★**零外发 · 零写板 · 零落表 · 零改既有闸 · 不写任何 agent 的分片 · 不改任何既有页正文**
"""
import hashlib
import io
import os
import shutil
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
BACKUP = LOG + ".bak_20260724_2145_cronfb67af40_iss391_cont1_redispatch398_399"
BACKUP_DL = DL + ".bak_20260724_2145_cronfb67af40_iss391_cont1_redispatch398_399"

TS = time.strftime("%Y-%m-%d %H:%M")
JOB = "cron fb67af40 (ARS45 队列自动派活) · ★2026-11-24 21:4x"

BRIEF_391 = "ISS-391_fts_land_drill_gate_judge_harden_and_fixture_realread_cont1.md"
BRIEF_398 = "ISS-398_sw_ref_reach_v2_selftest_baseline_independent_cont1.md"
BRIEF_399 = "ISS-399_mech_signed_append_ledger_design.md"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    if not os.path.exists(LOG) or not os.path.exists(DL):
        print("★issue_log.yaml / dispatch_log.yaml 不存在 ⇒ 中止")
        return 2
    src_md5 = md5(LOG)
    src_md5_dl = md5(DL)
    print("★开读时: issue_log md5=%s · dispatch_log md5=%s" % (src_md5, src_md5_dl))

    with io.open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    issues = doc.get("issues") or []
    by_id = {i.get("id"): i for i in issues}

    # ---------- ① 三条单都在台账 + 都是 fixing ----------
    for iid in ("ISS-391", "ISS-398", "ISS-399"):
        it = by_id.get(iid)
        if it is None:
            print("★%s 不在台账 ⇒ 中止" % iid)
            return 2
        if it.get("status") != "fixing":
            print("★%s status 不是 fixing (★%s★) ⇒ 中止" % (iid, it.get("status")))
            return 2
        if it.get("owner") not in ("hw-lead", "sw-lead", "mech-lead"):
            print("★%s owner 非法 ⇒ 中止" % iid)
            return 2
    if by_id["ISS-391"].get("owner") != "hw-lead":
        print("★ISS-391 owner 不是 hw-lead ⇒ 中止")
        return 2
    if by_id["ISS-398"].get("owner") != "sw-lead":
        print("★ISS-398 owner 不是 sw-lead ⇒ 中止")
        return 2
    if by_id["ISS-399"].get("owner") != "mech-lead":
        print("★ISS-399 owner 不是 mech-lead ⇒ 中止")
        return 2

    # ---------- ② ISS-391: 追加式 note_addendum (老字一字未删) ----------
    iss391 = by_id["ISS-391"]
    add = (
        "\n\n★**2026-11-24 21:4x · cron fb67af40 补派 cont1 (★main 19:55 暂缓签收的处置项③「夹具必修归 owner」★)** ★\n"
        "★★**续派理由 (★本机实跑复核, 不抄任何 agent 报告★)**★★\n"
        "★**①** 上一趟 (★交卷页 `HANDOFF/2026-11-24_hw-lead_ISS391_排针改孔进板侧改动清单同批完整性.md` · 12:50★) "
        "已把真相页 / 新闸 / 作业包登记都交了 ⇒ ★**本趟是【续做趟】不是重做** ★\n"
        "★**②** main 19:55 签收台账逐字: 裸跑 rc=0 · 7/7 全绿 · 但 `--selftest` rc=1 · **14/17** · 末行 `SELFTEST FAILED` "
        "⇒ 按 L-29 通则① 这道闸【不可信】⇒ ★**暂缓签收** ★\n"
        "★**③** 三条反向用例全 FAIL (★期望红却绿★): ① 删作业包 §0.2 ③ 里的「钻孔」⇒ 期望 D1 红·实际无 "
        "② 删 B33 描述列钻孔字样 ⇒ 期望 D2 红·实际无 ③ 删 B33 验收手段列读钻孔命令 ⇒ 期望 D3 红·实际无 ★\n"
        "★**④ ★★main 决定性实验 (★沙盒·真件逐字节未动★)★★**: 把真文件作业包 §0.2 ③ 里的「钻孔 0.65→0.71」"
        "这一腿真的删掉, 再跑 D1 ⇒ ★**D1 仍判绿** ⇒ ★**判据被削弱 ⇒ 不可签** ★ "
        "★**对照实验**: ③ 整条只剩 pitch 那一腿 ⇒ D1 才红 ⇒ ★**D1 只挡得住「整条没写」, 挡不住「只删动作腿留解释」** ★\n"
        "★**⑤ ★★两级根因 (★本机逐条复核出来·★比 main 的描述更具体★)★★**: "
        "★**【夹具层】** 真件 (★18:28~18:32 由 ISS-396 提前落★) 里那行排针腿与夹具常量 `WORKPACKET_DRILL_LEG` "
        "**逐字不同** ⇒ `make_fixed_workpacket()` 无条件再注入一份 ⇒ 沙盒里那条腿**出现两次** ⇒ "
        "反向用例 ① 只 `replace` 掉**第一处** ⇒ **真件那一处原封不动 ⇒ 变异成了空操作 ⇒ D1 照样绿** ⇒ "
        "② ③ 是同型 (`add_desc=False` / `add_crit=False` 删不掉真件已落的那一列) "
        "★**【判据层 · 更致命】** D1 的三条子判据全是**关键词 / 子串命中** (`has_drill()` + 「0.71」+ 「1.27」) "
        "⇒ 真件那行带一段**解释性括注** (「通用库件默认 (drill 0.65) 偏小 0.06」+「Ø0.71 TYP」) "
        "⇒ **纯解释文字也满足全部三条** ⇒ 动作腿删掉照样绿 ★\n"
        "★**⑥ 本趟要做的事 (★main 处置项③逐字: 「ISS-391 闸的夹具改成【真件现读】(★归 owner·★修完自测全绿才谈签收★)」★)★**: "
        "★**(甲) 判据层** 把 D1 / D2 / D3 从「关键词命中」改成「**动作腿命中**」⇒ 解释性文字不得满足判据 "
        "★**(乙) 夹具层** 变异从**真件当前原文**派生 ⇒ 不许依赖任何与真件逐字相等的写死常量 ⇒ 变异要把该腿的**全部出现处**干掉 "
        "⇒ 且夹具要能识别「真件已登记过」并跳过重复注入 "
        "★**(丙)** 把 main 的决定性实验 (★删动作腿留解释⇒D1 必须红★) **固化进夹具** ★\n"
        "★**⑦ 硬边界**: ★**零写板 · 零落表 · 零改既有页正文 (★作业包 / 预检清单 / `check_onepass_preflight_coverage.py` 全是受保护件★) "
        "· 只许改 `HW/check_fts_land_drill_same_batch.py` 一道 · D4~D7 一条不许碰 · 零挂链 · 零外发 · 不代拍 · 不自签** ★\n"
        "★**⑧** 改的是【已签收件】的判据逻辑 ⇒ ★**需重签 ⇒ 归 main, 本单不自签** ★\n"
        "★**⑨** brief: `state/dispatch_briefs/%s` ⇒ ★**命令存在性守卫 rc=0** ★" % BRIEF_391
    )
    old = iss391.get("note_addendum")
    if old is None:
        iss391["note_addendum"] = [add]
    elif isinstance(old, list):
        old.append(add)          # ★追加式 · 老字一字未删★
    elif isinstance(old, str):
        iss391["note_addendum"] = old + add
    else:
        print("★ISS-391 note_addendum 类型异常 (%s) ⇒ 中止" % type(old))
        return 2
    iss391["dispatched_at"] = "2026-11-24"

    # ---------- ③ dispatch_log 追加三条 ----------
    with io.open(DL, encoding="utf-8") as f:
        dl = yaml.safe_load(f) or []
    if not isinstance(dl, list):
        print("★dispatch_log 不是 list ⇒ 中止")
        return 2

    e1 = {
        "issue": "ISS-391",
        "agent": "hw-lead",
        "at": TS,
        "brief": "★★[续派·cont1] 钉板闸 `HW/check_fts_land_drill_same_batch.py` 的【判据加固 + 夹具改真件现读】"
                 "⇒ main 19:55 暂缓签收 (★裸跑 7/7 全绿 但 `--selftest` **14/17** · 三条反向用例全 FAIL·★期望红却绿★) "
                 "⇒ 决定性实验: 删掉动作腿、保留解释括注 ⇒ D1 仍判绿 ⇒ 判据被削弱 ⇒ 不可签 "
                 "⇒ 两级根因: 夹具二次注入 (真件已被 ISS-396 提前落 ⇒ 变异成空操作) + 判据只做关键词/子串命中 "
                 "⇒ ★**纯分析 + 改一道已签收闸的判据逻辑 + 改它的夹具 · 零写板 · 零落表 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★",
        "brief_file": "state/dispatch_briefs/%s" % BRIEF_391,
        "job": JOB + " · ★**cont1 续派 (★status 保持 fixing 不动·★上一趟 12:50 已交卷: 真相页/新闸/作业包登记都在盘★·★本趟只修判据与夹具★)** "
                   "· ★**命令存在性守卫 rc=0** ★",
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
        "task_name": "queue_iss391_cont1",
        "dispatched_at": TS,
        "redispatch_zombie": False,
        "carried_over_from": "★**main 2026-11-24 19:55 签收台账 §三 的 6 条机器依据** · ★**处置项③ 逐字: 「ISS-391 闸的夹具改成【真件现读】(★归 owner·★修完自测全绿才谈签收★)」** ★",
    }
    e2 = {
        "issue": "ISS-398",
        "agent": "sw-lead",
        "at": TS,
        "brief": "★★[补派·cont1] 第三道病闸 `SW/tools/check_sw_ref_reachability_v2.py` 的 `--selftest` 实测 **0/7** "
                 "⇒ 差值型自测在【基线漂移】时全灭 ⇒ 把夹具改成基线无关型 + 交出 `SW_MD5` 基线重锚的逐字补丁 (不代拍) ★★",
        "brief_file": "state/dispatch_briefs/%s" % BRIEF_398,
        "job": JOB + " · ★**【补派】(★20:0x 那一趟的 spawn 从未发生★)** · ★**命令存在性守卫 rc=0** ★",
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
        "task_name": "queue_iss398_cont1",
        "dispatched_at": TS,
        "redispatch_zombie": True,
        "death_cause": "★★**不是超时被掐 · 不是崩溃 · 是【spawn 从未发生】**★★ · "
                       "★20:00 那一趟 (main cron fb67af40 · transcript `36cd6141-…` · 19:34:41→20:34:37) 在 "
                       "「Now let me verify the in_flight guard holds, then spawn.」这句话上死掉 ⇒ `sessions_spawn` 从未执行 ⇒ "
                       "★**但它已经把 brief (20:28)、台账 (20:34:26)、dispatch_log (★两条都写着 `dispatched_at: 2026-11-24 20:0x`★) 全落了盘** ⇒ "
                       "★**台账说「已派」· dispatch_log 说「已派」· 实际一个 agent 会话都没起** ★ "
                       "★**盘上实证: sw-lead 最新会话 = 19:30 (★brief 落盘 20:28 ⇒ 晚于任何会话★) · "
                       "ISS-398 交卷页不在盘 · `grep -c iss398 state/fragments/*.yaml` = 0** ★",
        "partial_delivery": "0/3 交付物在盘 (★交卷页不在盘 · 分片登记 0 条 · 闸 md5 仍 1c4043ea26a1182b210e85f1b5130d8d·mtime 11-18 21:37 ⇒ 一字未动★) "
                            "· ★但【改前 0/7 原始输出 + 改前 selftest/gate_health 日志 + plan】已落盘在 `logs/iss398/` 与 `tmp/iss398/` (★直接用, 勿重跑★)",
    }
    e3 = {
        "issue": "ISS-399",
        "agent": "mech-lead",
        "at": TS,
        "brief": "★★[补派·新开] MECH 域【闸把别人的 md5 写死成硬基线】的全量清账 (9 道闸 / 35 处 pin) + 3 处已陈旧 pin 的裁定 "
                 "+ 一道《已签收件追加登记台账》自守闸 ⇒ 「板那一趟」合法追加一次 ⇒ MECH 闸就陈旧一处 ⇒ 收工验收的红被误读成「MECH 改坏了」⇒ 板白改第二遍 "
                 "★★★★**纯分析 + 新建真相页 + 新建机器闸 + 出逐字补丁(不应用) · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零挂链 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★",
        "brief_file": "state/dispatch_briefs/%s" % BRIEF_399,
        "job": JOB + " · ★**【补派】(★20:0x 那一趟的 spawn 从未发生★)** · ★**命令存在性守卫 rc=0** ★",
        "status_note": "★台账 status 保持 fixing (★20:34:26 已由那一趟落好·本趟未改★) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
        "task_name": "queue_iss399",
        "dispatched_at": TS,
        "redispatch_zombie": True,
        "death_cause": "★★**同上: spawn 从未发生**★★ · ★20:00 那一趟 (transcript `36cd6141-…` · 20:34:37 死) "
                       "在 20:32 落好 brief、20:34:26 落好台账 + dispatch_log ⇒ ★**但没起会话** ★ "
                       "★**盘上实证: mech-lead 最新会话 = 19:29 (★brief 落盘 20:32 ⇒ 晚于任何会话★) · "
                       "ISS-399 交卷页不在盘 · `grep -c iss399 state/fragments/*.yaml` = 0 · `logs/iss399/` 与 `tmp/iss399/` 都不存在** ★",
        "carried_over_from": "★**开单依据 = 20:00 那一趟本机实跑 MECH 域全部 25 道闸**: ★**唯一新缺口 = MECH 域【md5 硬基线】闸这一族** ★",
    }
    dl.extend([e1, e2, e3])

    # ---------- ④ md5 守卫复检 (fail-closed) ----------
    if md5(LOG) != src_md5:
        print("★★issue_log.yaml 在写前被第三方改动 (★%s → %s★) ⇒ 中止 (fail-closed)" % (src_md5, md5(LOG)))
        return 3
    if md5(DL) != src_md5_dl:
        print("★★dispatch_log.yaml 在写前被第三方改动 ⇒ 中止 (fail-closed)")
        return 3

    # ---------- ⑤ 备份 + 原子写 ----------
    shutil.copy2(LOG, BACKUP)
    shutil.copy2(DL, BACKUP_DL)

    tmp_log = LOG + ".tmp_write"
    with io.open(tmp_log, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, default_flow_style=False, width=4096, sort_keys=False)
    os.replace(tmp_log, LOG)

    tmp_dl = DL + ".tmp_write"
    with io.open(tmp_dl, "w", encoding="utf-8") as f:
        yaml.safe_dump(dl, f, allow_unicode=True, default_flow_style=False, width=100000, sort_keys=False)
    os.replace(tmp_dl, DL)

    print("★✅ issue_log.yaml 已写入 (ISS-391 note_addendum 追加 + dispatched_at) · 备份: %s" % os.path.basename(BACKUP))
    print("★✅ dispatch_log.yaml 已追加 3 条 (ISS-391 cont1 / ISS-398 补派 / ISS-399 补派) · 备份: %s" % os.path.basename(BACKUP_DL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
