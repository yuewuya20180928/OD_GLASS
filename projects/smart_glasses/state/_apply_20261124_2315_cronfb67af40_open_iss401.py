#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20261124_2315_cronfb67af40_open_iss401.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-24 23:1x 一趟
  ⇒ ★**新开 1 条内部单 (ISS-401) 并【直接落 `fixing`】** (★铁律⑩-i: 先落 fixing 再 spawn ⇒
    兄弟 job `775d9893` 的 `advance.py --json` 看不见 ⇒ 零撞车窗口★)

★**为什么这轮开单 (★本机实读, 不抄任何 agent 报告★)**:
  · `python3 state/advance.py --json` ⇒ `internal: []` / `approvals: []` / `waiting: []` / `decisions: 55`
  · 台账 16 条 `open` 的 owner 全部 = `boss`(5) / `main`(11) ⇒ 不在三个总工可派域 (advance.py L33
    `AGENT_ROLE = {"hw-lead","sw-lead","mech-lead"}`)
  · 三个槽位实检 (两采样法): sw-lead `d35b8dd2` (running) + mech-lead `665ad4dd` (ISS-400, running)
    ⇒ **两条真在飞 ⇒ 不许续派**; hw-lead `ca14678f` (advance_iss391_cont2) **已 done + transcript
    停在 22:59:04 静止 ⇒ 槽位实际已空** ⇒ ★**只有 hw-lead 一个空槽位**★
  · ⇒ 本 job 逐条实检 `state/fragments/hw.yaml` (★312 条 needs_from + 7 条 blockers★) ⇒
    **waiting_on = vendor 6 / jbd 2 · to = vendor 1 / jbd 1 ⇒ 共 10 条外部路由**
    + **blockers 里 6 条 (HW-B1~B6) 写着「等原厂」**
    + 网表 `HW/netlist_v1.csv` **109 行带 tbd 标签 + 36 行 evidence=[待原厂] (全 MAIN_PCB)**
  · ⇒ ★**HW 域是三个总工里唯一没做外部依赖自查收口的域** (SW 侧 ISS-270 + ISS-357 均 verified;
    MECH 侧 ISS-313 verified) ⇒ ★**违反老板 2026-11-11 19:31 + 2026-11-12 02:02 口径第 ② 半 (义务侧)**★
  · ⇒ 而「板只改一次」要求板对着一个【不再变的网表】画 ⇒ 145 行仍可能动网表 ⇒ **板 md5 第二次变的种子**

★**本脚本三道自保**: ① md5 守卫 (写前重算源文件 md5, 不一致 ⇒ rc=3 中止)
  ② 原子写 (`os.replace`) ③ 写后复跑 `state/check_brief_commands.py`
★**零外发 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 不写任何 agent 的分片**
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
DLOG = os.path.join(HERE, "dispatch_log.yaml")
BRIEFS = os.path.join(HERE, "dispatch_briefs")
BACKUP = os.path.join(HERE, "issue_log.yaml.bak_20261124_2315_cronfb67af40_open_iss401")
DLOG_BACKUP = os.path.join(HERE, "dispatch_log.yaml.bak_20261124_2315_cronfb67af40_open_iss401")
BRIEF_REL = "ISS-401_hw_external_dep_selfcheck_closure.md"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def brief_text(name):
    with io.open(os.path.join(BRIEFS, name), encoding="utf-8") as f:
        return f.read()


def main():
    if not os.path.exists(LOG):
        print("★issue_log.yaml 不存在 ⇒ 中止")
        return 2
    src_md5 = md5(LOG)
    with io.open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}
    issues = doc.get("issues") or []
    have = {i.get("id") for i in issues}
    if "ISS-401" in have:
        print("★ISS-401 已在台账 ⇒ 中止 (不重复开单)")
        return 2

    common = dict(
        source_agent="main",
        verify_by="main",
        reporter="main",
        raised="2026-11-24",
        due="2026-11-27",
        status="fixing",
        external=False,
        dispatched_at="2026-11-24",
    )

    note_common = (
        "★**2026-11-24 23:1x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】**"
        "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★) ★\n"
        "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `python3 state/advance.py --json` 实跑 ⇒ "
        "`internal: []` / `approvals: []` / `waiting: []` / `decisions: 55`; ★**台账 16 条 `open` 的 owner "
        "全部 = `boss`(5) / `main`(11) ⇒ 不在三个总工可派域** (★`state/advance.py` L33 "
        "`AGENT_ROLE = {\"hw-lead\",\"sw-lead\",\"mech-lead\"}`★) ★\n"
        "★**② 三个槽位实检 (★两采样法·★体积在长 ⇒ 真在飞★)★**: ★sw-lead `d35b8dd2` "
        "(`advance_iss398_cont2`) **running · 23:03 仍在长 ⇒ 真在飞 ⇒ 不许续派**★; ★mech-lead `665ad4dd` "
        "(ISS-400 · 22:50 本 job 派的那条) **running · 23:10 仍在长 ⇒ 真在飞 ⇒ 不许续派**★; "
        "★hw-lead `ca14678f` (`advance_iss391_cont2`) **已 done (endedAt 23:05:44) + transcript 停在 "
        "22:59:04 静止 ⇒ 槽位实际已空** ⇒ ★**只有 hw-lead 一个空槽位**★ ★\n"
        "★**③ 真缺口 (main 23:1x 逐条实检 `state/fragments/hw.yaml`)★**: ★`needs_from` = **312 条** ⇒ "
        "`to` 分布 main 251 / mech-lead 28 / sw-lead 16 / boss 12 / 落表批次 3 / ★**vendor 1 / jbd 1**★ ⇒ "
        "`waiting_on` 分布 agent 19 / boss 11 / ★**vendor 6 / jbd 2**★ / main 1 ⇒ ★**共 10 条外部路由**★ ⇒ "
        "★`blockers` 7 条里 ★**6 条 (HW-B1/B2/B3/B4/B5/B6) 的 `needs_from` 含 `vendor` (=「等原厂」)**★ ⇒ "
        "★网表 `HW/netlist_v1.csv` ★**109 行带 `tbd` 标签 (TBD-01/02/03/04/06/10/11/12/13) + 36 行 "
        "`evidence=[待原厂]` (全 MAIN_PCB)**★ ⇒ ★**TBD-01..TBD-13 = 「13 项画不了清单」, 网表 CSV 里只出现 "
        "9 个标签 (TBD-05/07/08/09 只在文档里) ⇒ 收口必须以 13 项为准**★ ★\n"
        "★**④ 为什么至今没人做**: ★**SW 域已做 (ISS-270 5 条外部依赖自查 + ISS-357 needs 144 条四分类, 均 "
        "verified) · MECH 域已做 (ISS-313 needs 184 条四分类, verified) ⇒ ★**HW 域 (needs 312 条 + 6 条 "
        "blocker + 13 项 TBD) 是三域里唯一没做过的**★ ⇒ ★**违反老板 2026-11-11 19:31 + 2026-11-12 02:02 "
        "「不再发信, 全靠自己查资料」的第 ② 半 (义务侧)**★ ★\n"
        "★**⑤ 为什么在「板只改一次」的关键路径上**: ★**网表 = 板要对着画的那份真源** ⇒ ★`HW/PCB/BOARD_ONEPASS_"
        "COMMIT_ORDER.md` INV-1 明写「板 md5 全生命周期变更次数 ≤ 1」⇒ ★**今天挂着 `[待原厂]` 的 36 行 + "
        "109 行 TBD = 板那一趟开工当天仍有 145 行可能动网表 ⇒ 动网表 ⇒ 板 md5 第二次变 ⇒ Gerber / 投产包 / "
        "留证链 / 盖章 / 发布全部白跑** ⇒ ★**坏结局二选一: ① 开工当天才发现要落值 ⇒ 那一趟作废; ② 带着 145 行 "
        "`[待原厂]` 直接投板 ⇒ 这是一张能出厂但不该出厂的板**★ ★\n"
        "★**⑥ 派活纪律**: ★**本单是「纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口」类 ⇒ 合"
        "「板只改一次」纪律 ① (先派纯分析类, 不动板) ⇒ 零写板·零落表·零改既有闸阈值·零改既有页正文·零外发·"
        "不代拍·不自签** ★\n"
        "★**命令存在性守卫**: ★`python3 state/check_brief_commands.py --brief-file "
        "state/dispatch_briefs/%s` ⇒ **rc=0** ★" % BRIEF_REL
    )

    new_issues = [
        dict(
            id="ISS-401",
            title=(
                "★★[★新主线·PCB 线·HW 侧·政策落地+纯查证+纯分析+新建真相页+新建机器闸+自有分片收口·零写板·"
                "零落表] 「老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料」的第 ② 半 "
                "【义务侧】在 HW 侧落地 ⇒ HW 域 needs 312 条里 10 条仍路由到 vendor/jbd + 6 条 blocker "
                "写着「等原厂」+ 网表 109 行 tbd / 36 行 [待原厂] ⇒ 逐条换成【自己查的结果 + 证据等级 + "
                "查不到就写降级方案】⇒ 板那一趟的网表才真能冻结 ★★"
            ),
            severity="high",
            source_blocker=None,
            desc=(
                "★★[★新主线·PCB 线·HW 侧·政策落地 + 需求闭环 + 纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + "
                "自有分片收口·零写板·零落表·零改既有闸阈值·零改既有页正文·零挂链·零外发·不代拍·不自签]★★\n\n"
                "★**题 (来源 = ★main 2026-11-24 23:1x 本机实读 `state/fragments/hw.yaml` + `HW/netlist_v1.csv`"
                " · 不抄任何 agent 报告★)★:\n"
                "★**① 现象**: ★**HW 域是三个总工里唯一没做外部依赖自查收口的域** ⇒ ★SW 侧已做 (ISS-270「SW 侧"
                "还挂着 5 条干等原厂/等外部回复/待确认」+ ISS-357「SW 域 needs 144 条四分类」· 均 verified) ⇒ "
                "★MECH 侧已做 (ISS-313「MECH 域 needs 184 条四分类 + 16 条外部依赖」· verified) ⇒ "
                "★**HW 域 (needs 312 条 · blockers 7 条 · TBD 13 项) 一次都没做**★ ⇒ ★**违反老板 "
                "2026-11-11 19:31「以后不再做任何邮件咨询…都自己去网上查找」+ 2026-11-12 02:02「不再发信, "
                "全靠自己查资料」的第 ② 半 (义务侧) ⇒ 而任务书里写着的「没有『老板批一句可以发』这个选项了」"
                "这条, 在 HW 域根本没有对应动作**★ ★\n"
                "★**② 精确账 (本机实读)★**: ★`state/fragments/hw.yaml` 的 `needs_from` = **312 条** ⇒ "
                "`to` = main 251 / mech-lead 28 / sw-lead 16 / boss 12 / 落表批次 3 / ★**vendor 1 / jbd 1**★ ⇒ "
                "`waiting_on` = agent 19 / boss 11 / ★**vendor 6 / jbd 2**★ / main 1 ⇒ ★**8 条 waiting_on 外部 "
                "+ 2 条 to 外部 = 10 条外部路由** ★★ 10 条逐条清单: ★`q16_display_iface` · "
                "`vendor_ars45_paper_q11_q16` (to=vendor) · `jbd_zoushe_dsi_spec` (to=jbd) · "
                "`rel_vendor_absmax_rating` · `rel_battery_cell_spec` · `iss067_vendor_r_on_u1` · "
                "`iss067_jbd_vdd_tol_u2` · `rk3572_isp_throughput_max` ⇒ ★**这 8 个 key 在 hw.yaml 里各只出现 "
                "1 次 (grep 实测) ⇒ 只作为 needs 挂着, 没有一条有自查结论**★ ★\n"
                "★**③ blockers 侧**: ★`blockers` 7 条里 ★**HW-B1 (显示 TX) / HW-B2 (FCCSP pitch) / HW-B3 "
                "(电源域上限) / HW-B4 (启动存储) / HW-B5 (R-F1 残留·含 3 条外部依赖) / HW-B6 (15/15 器件 "
                "Absolute Maximum Ratings 未核) 六条的 `needs_from` 里写着 `vendor`** ⇒ ★**HW-B7 (R-GEO 六问) "
                "不是外部依赖 ⇒ 本单不碰, 但要写明「别混进清单」**★ ★\n"
                "★**④ 网表侧 (板要对着它画的那份真源)★**: ★`HW/netlist_v1.csv` (★零落表 ⇒ 本单只读★) ⇒ "
                "★**109 行带 `tbd` 标签** (TBD-01 6 / TBD-02 12 / TBD-03 25 / TBD-04 24 / TBD-06 6 / "
                "TBD-10 3 / TBD-11 4 / TBD-12 27 / TBD-13 2) + ★**36 行 `evidence=[待原厂]` (★全部 board=MAIN_PCB★)**★ ⇒ "
                "★**TBD-01..TBD-13 = 「13 项画不了清单」** (★口径出处 `HW/ERC_DRC_CHECKLIST.md` §A5★) ⇒ "
                "★**网表 CSV 里只出现 9 个标签 (TBD-05/07/08/09 只在文档里) ⇒ 收口必须以 13 项为准, 不能只扫 CSV**★ ★\n"
                "★**⑤ 为什么在「板只改一次」的关键路径上**: ★**板 md5 全生命周期只许变一次** ⇒ ★**凡会改网表"
                "真源的动作必须与板那一趟同批** ⇒ ★**今天挂着 `[待原厂]` 的 36 行 + 109 行 TBD ⇒ 板那一趟开工"
                "当天仍有 145 行可能动网表 ⇒ 动网表 ⇒ 板 md5 第二次变 ⇒ Gerber / 投产包 / 留证链 / 盖章 / "
                "发布全部白跑** ⇒ ★**坏结局二选一: ① 开工当天才发现要落值 ⇒ 那一趟作废; ② 带着 145 行 "
                "`[待原厂]` 直接投板 ⇒ 这是一张能出厂但不该出厂的板**★ ★\n"
                "★**⑥ 盘上已有的现成结论 (别重查)★**: ★TBD-01 对 demo 板已不阻塞 (★主板走 RK3572 SoM 路线 ⇒ "
                "不碰 SoC 球位号★ · `HW/DEMO_BOARD_HW_DECISION.md`) ⇒ ★TBD-01 可用官网数据直接关 (★TX=O/RX=I/"
                "3.3V/单端★ · `HW/PCB/RK3572_UART0_TX_PINMUX_VERDICT.md` §5 F2 · ISS-204 已 verified) ⇒ "
                "★TBD-05 = 无公开数据 `[0数据]` (★`HW/ONLINE_FINDINGS_2026-10-26.md` §7★) ⇒ ★存储档 "
                "TBD-06/11 已由 ISS-346/ISS-350 三档化 (★台架板档板侧零动作·不卡★) ⇒ ★★**这些是现成弹药, "
                "本单的任务是【把它们收成一条可执行的收口结论 + 一条机器闸】, 不是重查一遍**★★ ★\n"
                "★**⑦ 本单交付 (★5 件·全部零写板★)★**: ★① 真相页 (★新建) 逐条给【自己查的结果 + 证据等级五级 + "
                "查不到就写降级方案 + 还卡不卡板那一趟 + 路由改成什么】★ ② 新闸 (★新建) 裸跑 rc=1 红的是现状 · "
                "`--selftest` rc=0 末行 `ALL TESTS PASS` (★正向 ≥1 + 反向 ≥6★) ★ ③ 交卷页 B1~B7 全填 "
                "(★B2/B3/B4 标题须用标准口径★) ★ ④ 自有分片 `state/fragments/hw.yaml` 收口 (★走 "
                "`state/frag_write.py`·★**不许 `open(p,\"w\")`·★其余 302 条 needs 一个字都不许动·★改后必须跑"
                "条数/丢 key/多的 key/内容有变的条 四项自检★) ★ ⑤ 留证 `logs/iss401/` ★\n"
                "★**⑧ 归 main 的五条问句 (★本单一律不代拍★)★**: ★HW-B1~B7 里哪几条能正式解除/降级 · 10 条 "
                "needs 的 `to`/`waiting_on` 各自改成什么 · TBD-01..TBD-13 里哪几条还卡板那一趟 · 新闸挂不挂链 "
                "· 网表 36 行 `[待原厂]` 归谁落 (同批 vs 拆批 ⇒ 直接决定板 md5 变更次数) ★"
            ),
            owner="hw-lead",
            need_keys=[
                "iss401_hw_external_dep_closure",
                "iss401_blocker_verdicts",
                "iss401_tbd_13_boardtrip_verdict",
            ],
            task_brief=brief_text(BRIEF_REL),
            note=note_common,
        ),
    ]

    for i in new_issues:
        for k, v in common.items():
            i.setdefault(k, v)

    # ---- ① md5 守卫: 写前重算 ----
    if md5(LOG) != src_md5:
        print("★md5 守卫: 源文件在读与写之间被改过 ⇒ 中止 (rc=3)")
        return 3

    doc["issues"] = list(issues) + new_issues
    shutil.copy2(LOG, BACKUP)
    tmp = LOG + ".tmp.%d" % int(time.time())
    with io.open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100000)
    # ---- ② 原子替换 ----
    os.replace(tmp, LOG)

    # ---- dispatch_log 追加 (同款原子写) ----
    try:
        with io.open(DLOG, encoding="utf-8") as f:
            dlog = yaml.safe_load(f) or []
    except Exception:  # noqa: BLE001
        dlog = []
    if not isinstance(dlog, list):
        dlog = []
    dlog.append(
        dict(
            task_name="queue_iss401",
            dispatched_at="2026-11-24 23:1x",
            redispatch_zombie=False,
            child_session_key="(spawn 后回填)",
            on_disk_session="(spawn 后回填)",
            liveness_check="(spawn 后回填)",
            carried_over_from=note_common,
        )
    )
    shutil.copy2(DLOG, DLOG_BACKUP)
    tmp2 = DLOG + ".tmp.%d" % int(time.time())
    with io.open(tmp2, "w", encoding="utf-8") as f:
        yaml.safe_dump(dlog, f, allow_unicode=True, sort_keys=False, width=100000)
    os.replace(tmp2, DLOG)

    print("★已写 %s (+1 条: ISS-401 · owner=hw-lead · status=fixing)" % LOG)
    print("★备份 %s (md5 %s)" % (BACKUP, md5(BACKUP)))
    print("★台账条数 %d → %d" % (len(issues), len(doc["issues"])))
    print("★已追加 dispatch_log (现 %d 条)" % len(dlog))
    return 0


if __name__ == "__main__":
    sys.exit(main())
