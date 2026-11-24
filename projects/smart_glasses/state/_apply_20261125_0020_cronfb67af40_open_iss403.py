#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20261125_0020_cronfb67af40_open_iss403.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-25 00:2x 一趟
  ⇒ ★**新开 1 条内部单 (ISS-403) 并【直接落 `fixing`】** (★铁律⑩-i: 先落 fixing 再 spawn ⇒
    兄弟 job `775d9893` 的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★)

★**为什么这轮开单 (★本机实读 + 本机沙盒 A/B 实测, 零抄任何 agent 报告★)**:
  · `python3 state/advance.py --json` ⇒ `internal: []` / `approvals: []` / `waiting: []` / `decisions: 55`
    ⇒ ★**16 条 `open` 的 owner 全是 `boss`(5) / `main`(11) ⇒ 不在三个总工可派域**
    (★advance.py L33 `AGENT_ROLE = {"hw-lead","sw-lead","mech-lead"}`★)
  · 三个槽位实检 (`sessions_list` / `subagents list`):
    hw-lead `7ed253f7` (ISS-402) **done @23:57:43** · sw-lead `d35b8dd2` (ISS-398 cont2) **done @22:59:39** ·
    mech-lead `665ad4dd` (ISS-400) **done @22:48:43** ⇒ ★**三条会话全部收工 ⇒ 三个槽位实际都空** ★
    ⇒ ★**本轮只派 1 条 (mech-lead)**: ★hw-lead 的 ISS-402 刚交卷 (待 main 签收, 不是再派一遍),
      sw 域本轮没有可复述的已核实缺口 ⇒ ★**宁可不派, 也不派一条我自己没核实的题** ★
  · ★**本单的题 (main 本机实跑 + 沙盒 A/B 对照, 零抄报告)★**:
      - ★**前提已死**: 官方 `Ø0.71` 配通用件 `1.000×1.000` 焊盘 ⇒ 环宽 `(1.000−0.71)/2 = 0.1450` mm;
        板厂 (JLCPCB) 官网逐字 `Multilayer: 1 oz: … absolute minimum 0.15 mm` ⇒ **0.1450 < 0.15**
        ⇒ 「焊盘维持 1.000」的前提【已被坐实为不成立】⇒ 那趟必然要放大焊盘
      - ★**★本单的核心缺口 (main 本机沙盒 A/B 实测, 已复现)★**: 把 KiCad 官方库件
        `PinHeader_1x0{2,4}_P1.27mm_Vertical.kicad_mod` 复制到沙盒, `(size 1 1)` → `(size 1.11 1.11)`,
        ★**只换库不换真件 + `--root` 指向真实项目 (零拷贝假象)**, 同一条命令跑两遍比红项集合:
        ★**7 道 MECH 闸里 5 道对焊盘尺寸【完全盲】**★ (含 201 条判据的判决链主闸
        `check_debug_seat_3d_fit.py`) ⇒ 只有 `check_jdebug_1p27_clearance` (G1~G4 转红) +
        `check_juart_1p27_clearance` (J0/J5/J7 转红) 抓得到 ⇒
        ★**「焊盘放大 ⇒ 7 个数全作废 ⇒ 结构件按旧数出件 ⇒ 装配干涉 ⇒ 板改第二次」这条路,
          今天没有任何机器闸会响** ★
      - ★**根因 (main 实读源码)**: `MECH/check_debug_seat_3d_fit.py` 的 `official` 表把铜箔宽写死成
        `copper.x = 4.81` / `2.27` (L683/L686) ⇒ 这两个数就是 `pad=1.000` 的产物 ⇒ pad 一改它们就是错的;
        ★**且该文件里已经写好了「从 `.kicad_mod` 现读 pad 算铜箔包络」的 `parse_footprint_copper()`
        (L187) —— 但它一次都没被调用 (死代码)**★
      - ★**且 7 道 MECH 闸一道都没挂 `state/gate_check.py`** (★L211 `EXTRA_GATES` / L262
        `PINNED_MD5_GATES` 两张表逐条核过★) ⇒ 连「盲」的那道主闸都不会在门禁链上跑
      - ★**7 个数会怎么变 (main 本机实算)★**: pad `1.000→1.110` ⇒ `4.8100→4.9200` / `2.2700→2.3800` /
        `6.6100→6.7200` / `4.0700→4.1800` / `0.1350→0.0800` / `2.6950→2.6400` / `0.7700→0.7150`
        ⇒ ★**七个无一例外全部要重算** ⇒ 结构件 + 镜脚侧整体返工一次 (2-4 周 + ¥4-8K 级)

★**本脚本三道自保**: ① **幂等** (ISS-403 已存在 ⇒ 不写盘, 直接退出)
  ② **CAS 守卫** (写前重算 `issue_log.yaml` md5, 与读时不一致 ⇒ rc=3 中止)
  ③ **原子写 + 写后回读自检** (条数 +1 / ISS-403 在位 / status=fixing / 旧条目条数不变)
★**零外发 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 不写任何 agent 的分片**
"""
import hashlib
import io
import os
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
BRIEFS = os.path.join(HERE, "dispatch_briefs")
BACKUP = os.path.join(HERE, "issue_log.yaml.bak_20261125_0020_cronfb67af40_open_iss403")
DLOG_BACKUP = os.path.join(HERE, "dispatch_log.yaml.bak_20261125_0020_cronfb67af40_open_iss403")
BRIEF_REL = "ISS-403_mech_pad_size_coupling_blindspot.md"
ISS_ID = "ISS-403"
AGENT = "mech-lead"


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_yaml(p):
    with io.open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_iss403_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


TITLE = ("★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建真相页+新建机器闸+自有分片收口·零写板·零落表] "
         "「板那一趟」焊盘从 `1.000` 放大 ⇒ MECH 判决链 7 个数全作废 ⇒ 【7 道 MECH 闸里 5 道对它完全盲】"
         "的清账与 fail-closed 闸 (★main 本机沙盒 A/B 实测·已复现★) ★★")

DESC = """★★[★新主线·PCB 线·MECH 侧·纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口·零写板·零落表·零改既有闸判据·零改既有页正文·零挂链·零外发·不代拍·不自签]★★

★**题 (来源 = ★main 2026-11-25 00:2x 本机实读 + 本机沙盒 A/B 实测 · 不抄任何 agent 报告★)★:

★**① 前提已死 (★这一格是本单的根★)★:
★**官方 `Ø0.71` 配通用件 `1.000×1.000` 焊盘 ⇒ 环宽 (annular ring) = (`1.000` − `0.71`) / 2 = `0.1450` mm** ★
(★出处: `state/issue_log.yaml` ISS-387 `verify_result` · main 2026-11-24 13:1x 独立复核·自己算过★)
★**板厂口径逐字**: `PTH annular ring ≧0.20mm` · `Multilayer: 1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm` ★
(★出处: `state/ROUND_LOG_cron775d_2026-11-24_2050.md` L46 · ★**原件落盘** `tmp/cron775d_r90/jlcpcb_pcb_capabilities_20261124_2043.html` md5 `24dd86f0…` · ★另 `HANDOFF/2026-11-24_hw-lead_ISS396_FTS改孔登记落盘.md` L83 逐字同款★)
★**⇒ `0.1450` < `0.15` ⇒ 低于绝对下限 ⇒ 「焊盘维持 `1.000×1.000`」的前提【已被坐实为不成立】⇒ 那趟必然要放大焊盘 (`≥1.010` 够绝对下限 / `1.110` 够推荐值 `0.20` / `1.218` 够 2oz 的 `0.254`)★**

★**② ★★★【本单的核心缺口 · main 本机沙盒 A/B 实测 · 已复现】★★★★:
★**做法**: 把 KiCad 官方库件 `PinHeader_1x0{2,4}_P1.27mm_Vertical.kicad_mod` 复制一份到沙盒, 把 `(size 1 1)` 改成 `(size 1.11 1.11)`, ★**只换库不换真件 + `--root` 指向真实项目 ⇒ 零沙盒拷贝假象**, 同一条命令跑两遍 (★A=`1.110` / B=`1.000`★), 比对两遍的判据红项集合★

| MECH 闸 | pad `1.000` | pad `1.110` | 反应 |
|---|---|---|---|
| `MECH/check_debug_seat_3d_fit.py` (★**201 条判据**★) | rc=0 (201/201 绿) | ★**rc=0 (201/201 绿)** ★ | ★**✗ 完全盲** ★ |
| `MECH/check_debug_seat_rework_spec.py` | rc=0 | ★**rc=0** ★ | ★**✗ 完全盲** ★ |
| `MECH/check_fts_seat_body_geometry.py` | rc=0 | ★**rc=0** ★ | ★**✗ 完全盲** ★ |
| `MECH/check_connector_clearance_caliber.py` | rc=1 (3 条红) | ★**rc=1 (红项集合逐条相同)** ★ | ★**✗ 盲** ★ |
| `MECH/check_fts_vs_generic_courtyard_delta.py` | rc=1 (红) | ★**rc=1 (红项集合逐条相同)** ★ | ★**✗ 盲** ★ |
| `MECH/check_jdebug_1p27_clearance.py` | G1~G7 全 PASS | ★**G1/G2/G3/G4 转红** ★ | ★✓ 抓得到 ★ |
| `MECH/check_juart_1p27_clearance.py` | 全 PASS | ★**J0/J5/J7 转红** ★ | ★✓ 抓得到 ★ |

★**⇒ 「焊盘放大 ⇒ 7 个数作废 ⇒ 结构件按旧数出件 ⇒ 装配干涉 ⇒ 板改第二次」这条坏结局, 今天没有任何机器闸会响** ★

★**③ 根因 (★main 实读源码★)★: `MECH/check_debug_seat_3d_fit.py` 的 `official` 表把铜箔宽【写死】成 `copper.x = 4.81` / `2.27` (L683/L686) ⇒ 这两个数就是 `pad=1.000` 的产物 (`3.81 + 1.00` / `1.27 + 1.00`) ⇒ pad 一改它们就是错的, 而闸拿错的数去算判决 ⇒ 判决【自洽但失真】⇒ ★**全绿**★ ★
★**★⇒ 而且该文件里其实已经写好了「从 `.kicad_mod` 现读 pad 算铜箔包络」的 `parse_footprint_copper()` (L187) —— ★**但它一次都没被调用** (★全仓 grep: 只有定义那一行★) ⇒ 【现读的能力有、但没接上】★★ ★
★**★⇒ 且 7 道 MECH 闸【一道都没挂 `state/gate_check.py`】(★L211 `EXTRA_GATES` / L262 `PINNED_MD5_GATES` 两张表逐条核过★) ⇒ 连「盲」的那道主闸都不会在门禁链上跑 ⇒ 红了没人知道, 更别说它压根不红** ★

★**④ 7 个数怎么变 (★main 本机实算★)★: pad `1.000→1.110` ⇒ `4.8100→4.9200` / `2.2700→2.3800` / `6.6100→6.7200` / `4.0700→4.1800` / `0.1350→0.0800` / `2.6950→2.6400` / `0.7700→0.7150` ⇒ ★**七个无一例外全部要重算** ⇒ 结构件 + 镜脚侧整体返工一次 (2-4 周 + ¥4-8K 级·金额不代估)★ ★
★**★⇒ 且 `J_UART` 罩住余量 `0.1350→0.0800` 本来就红 (最坏 `-0.1650` < CRIT `0.60`) ⇒ 红得更狠; CRIT/TOL 真身 = `MECH/service_port_check.py` L126/L127 (`TOL["fdm_part"]=0.30` ⇒ `CRIT=0.60` ⇒ 每边要求 `0.9000`)★ ★
★**★⇒ ⇒ 「MECH 七个数一个都不用改」这个结论 (★ISS-387 / ISS-391 当时的口径★) 在 pad=1.000 之下成立, 在 pad≥1.010 之下【不成立】⇒ 那两页的现状值型判据【已经陈旧】★ ★

★**⑤ 交付物 5 件**: ★① 真相页 `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` (新建 · 含 pad 档位矩阵 + 盲闸名单 + 机器块) ② 新闸 `MECH/check_pad_size_coupling_closed.py` (新建 · 裸跑 rc=0 (现状自洽) · `--selftest` rc=0 末行逐字 `ALL TESTS PASS` · 正向 ≥1 + 反向 ≥8 · 零挂链) ③ 交卷页 B1~B7 (标题用仓里规范口径) ④ 自有分片收口 (走 `state/frag_write.py` · 写后四项自检: 条数/丢 key/多的 key/内容有变的条 · `needs_from` 全 `to: main`) ⑤ 留证 `logs/iss403/` + 沙盒 `tmp/iss403/` (不硬链接真件 · 不写系统 `/tmp`) ★

★**⑥ brief**: ★`state/dispatch_briefs/ISS-403_mech_pad_size_coupling_blindspot.md` (★9,954 B★) ⇒ ★**派活前已跑 `python3 state/check_brief_commands.py --brief-file …` ⇒ rc=0** ★

★**⑦ 五条一条都不代拍 (★全交 main★)★: 焊盘档位最终取哪档 (★连带「本板厂到底是谁」这一格至今 `[0数据]`·`FAB_ORDER_NOTES.md` 只写「板厂」从未指名★) / 7 个数新值何时落 / 5 道盲闸要不要修 (★改已签收件 ⇒ 要重签+留痕★) / 7 道 MECH 闸挂不挂链 / `parse_footprint_copper()` 死代码怎么处理★ ★
"""


def main():
    if not os.path.exists(LOG):
        sys.exit("★issue_log.yaml 不存在 ⇒ 拒绝跑")

    brief_path = os.path.join(BRIEFS, BRIEF_REL)
    if not os.path.exists(brief_path):
        sys.exit("★brief 不存在 ⇒ 拒绝跑: %s" % brief_path)
    with io.open(brief_path, encoding="utf-8") as f:
        brief_text = f.read()

    before_md5 = md5(LOG)
    log = read_yaml(LOG)
    issues = log.get("issues") or []

    # ── 幂等守卫 (L-28: 撞名必须报错, 不是静默跳过) ──
    existing = [it for it in issues if it.get("id") == ISS_ID]
    if existing:
        sys.stderr.write("★%s 已存在 (status=%s) ⇒ 幂等跳过, 不写盘\n"
                         % (ISS_ID, existing[0].get("status")))
        print("IDEMPOTENT_NO_WRITE")
        return 0

    n_before = len(issues)
    new_issue = {
        "id": ISS_ID,
        "title": TITLE,
        "severity": "high",
        "source_blocker": None,
        "desc": DESC,
        "owner": AGENT,
        "need_keys": [
            "iss403_pad_size_coupling_ledger",
            "iss403_blind_gate_audit",
            "iss403_seven_numbers_matrix",
        ],
        "task_brief": brief_text,
        "note": ("★**2026-11-25 00:2x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】**"
                 " (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★)\n"
                 "★**开单依据 (本机实读 + 本机沙盒 A/B 实测, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0 "
                 "(16 条 open 的 owner 全是 boss/main ⇒ 不在三个总工可派域); ② 三个槽位会话 (hw-lead ISS-402 @23:57 done / "
                 "sw-lead ISS-398 cont2 @22:59 done / mech-lead ISS-400 @22:48 done) 全部收工 ⇒ 槽位实际都空 ⇒ "
                 "本轮只派 mech-lead 一条 (★hw-lead 的 ISS-402 刚交卷待 main 签收 ⇒ 不是再派一遍; sw 域本轮没有"
                 "可复述的已核实缺口 ⇒ 宁可不派也不派没核实的题★); ③ ★**本单的题 = 焊盘放大 ⇒ MECH 7 个数全作废, "
                 "而 7 道 MECH 闸里 5 道对它完全盲 (★main 沙盒 A/B 实测: `check_debug_seat_3d_fit` 201 条判据 "
                 "pad 1.000 与 1.110 都 rc=0★) ⇒ 「板只改一次」那趟开工前的沉默地雷 ⇒ 本单做成逐条台账 + "
                 "fail-closed 闸。\n"
                 "★**本单是纯查证/纯分析类** ⇒ 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 ⇒ "
                 "合「板只改一次」纪律 ① ⇒ 真动板那一趟不受本单影响。"),
        "source_agent": "main",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-25",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "dispatched_at": "2026-11-25",
    }
    issues.append(new_issue)
    log["issues"] = issues

    # ── CAS 守卫: 写前重算 md5, 与读时不一致 ⇒ 中止 ──
    now_md5 = md5(LOG)
    if now_md5 != before_md5:
        sys.stderr.write("★CAS 守卫命中: issue_log.yaml 在读后被改 (%s → %s) ⇒ 中止, 不写盘\n"
                         % (before_md5, now_md5))
        return 3

    shutil.copy2(LOG, BACKUP)
    text = yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100)
    atomic_write(LOG, text)

    # ── 写后回读自检 (打印 ≠ 落地) ──
    chk = read_yaml(LOG)
    chk_issues = chk.get("issues") or []
    ids = [it.get("id") for it in chk_issues]
    problems = []
    if len(chk_issues) != n_before + 1:
        problems.append("条数 %d ≠ 期望 %d" % (len(chk_issues), n_before + 1))
    if ids.count(ISS_ID) != 1:
        problems.append("%s 出现 %d 次" % (ISS_ID, ids.count(ISS_ID)))
    got = [it for it in chk_issues if it.get("id") == ISS_ID]
    if not got or got[0].get("status") != "fixing" or got[0].get("owner") != AGENT:
        problems.append("status/owner 不对: %r" % (got[0].get("status") if got else None))
    if not got or "parse_footprint_copper" not in str(got[0].get("task_brief")):
        problems.append("task_brief 没落进去")
    if problems:
        sys.stderr.write("★写后自检失败: %s ⇒ 回滚\n" % " | ".join(problems))
        shutil.copy2(BACKUP, LOG)
        return 2
    print("ISSUE_LOG_OK: %d → %d 条, %s 在位 status=fixing owner=%s, md5 %s → %s"
          % (n_before, len(chk_issues), ISS_ID, AGENT, before_md5, md5(LOG)))

    # ── dispatch_log (list 形状 ⇒ 追加式写回) ──
    entry = {
        "issue": ISS_ID,
        "agent": AGENT,
        "at": "2026-11-25",
        "brief": BRIEF_REL,
        "run_id": "cron_fb67af40_20261125_0020",
    }
    if os.path.exists(DLOG):
        raw = read_yaml(DLOG)
        dl_list = raw if isinstance(raw, list) else (raw or {}).get("dispatches", [])
        n_dl = len(dl_list)
        shutil.copy2(DLOG, DLOG_BACKUP)
        with io.open(DLOG, "a", encoding="utf-8") as f:
            f.write(yaml.safe_dump([entry], allow_unicode=True, sort_keys=False, width=200))
        chk_dl = read_yaml(DLOG)
        chk_list = chk_dl if isinstance(chk_dl, list) else (chk_dl or {}).get("dispatches", [])
        if len(chk_list) != n_dl + 1 or chk_list[-1] != entry:
            sys.stderr.write("★dispatch_log 自检失败 ⇒ 回滚\n")
            shutil.copy2(DLOG_BACKUP, DLOG)
            return 2
        print("DISPATCH_LOG_OK: %d → %d 条" % (n_dl, len(chk_list)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
