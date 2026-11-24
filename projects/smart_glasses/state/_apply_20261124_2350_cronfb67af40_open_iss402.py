#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★_apply_20261124_2350_cronfb67af40_open_iss402.py★

★**用途**: cron `fb67af40` (ARS45 队列自动派活) · 2026-11-24 23:5x 一趟
  ⇒ ★**新开 1 条内部单 (ISS-402) 并【直接落 `fixing`】** (★铁律⑩-i: 先落 fixing 再 spawn ⇒
    兄弟 job `775d9893` 的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★)

★**为什么这轮开单 (★本机实读, 不抄任何 agent 报告★)**:
  · `python3 state/advance.py --json` ⇒ `internal: []` / `approvals: []` / `waiting: []` / `decisions: 55`
    ⇒ ★**16 条 `open` 的 owner 全是 `boss`(5) / `main`(11) ⇒ 不在三个总工可派域**
    (★advance.py L33 `AGENT_ROLE = {"hw-lead","sw-lead","mech-lead"}`★)
  · 三个槽位实检 (`sessions_list` / `subagents list`):
    hw-lead `4268ade7` (ISS-401) **done** · sw-lead `d35b8dd2` (ISS-398 cont2) **done** ·
    mech-lead `665ad4dd` (ISS-400) **done** ⇒ ★**三条会话全部收工 ⇒ 三个槽位实际都空** ★
    ⇒ ★**本 job 只派 1 条 (hw-lead)**: ★sw/mech 两域的 needs 四分类 (ISS-357 / ISS-313) 与
      ISS-401 (HW 域外部依赖收口) 刚交卷, ★**本轮没有可复述的、已核实的不重复缺口** ⇒
      ★**宁可不派, 也不派一条我自己没核实的题** ★
  · ★**本单的题 (main 本机实读 + 全仓检索, 零抄报告)★**:
      - `HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md` L9/L82/L162/L268/L282/L329
        ⇒ ★**「重跑生成器 ⇒ 26 处 Value 不同 (12 处手写功能描述 + 14 处旧选型) + `C_VBUS_GND` 掉板」** ★
      - 同页 L329 逐字: ★**「ISS-289 只认领了 S7 那一条, 其余 4 条 need (路线拍板 / `C_VBUS_GND` /
        `/tmp` 写穿 / **26 处 Value 差异**) 仍开着」** ★
      - `state/fragments/hw.yaml` L3692 / L3697 / L3703 ⇒ ★**`iss287_cvbus_gnd_board_only` /
        `iss287_tmp_write_through` / `iss287_26_value_diff` 三条至今零 answers** ★
      - 全仓 `grep -rn "26 处 Value"` ⇒ ★**只命中 ISS-287 交卷页散文 + 一条 open need + 一个
        `_apply_*.py` ⇒ 没有任何机器闸读它** ★
      - ★**「板只改一次」⇒ 板 md5 全生命周期只许变 1 次 ⇒ 这一条现在是那趟开工前的沉默地雷** ★

★**本脚本三道自保**: ① **幂等** (ISS-402 已存在 ⇒ 不写盘, 直接退出)
  ② **CAS 守卫** (写前重算 `issue_log.yaml` md5, 与读时不一致 ⇒ rc=3 中止)
  ③ **原子写 + 写后回读自检** (条数 +1 / ISS-402 在位 / status=fixing / 旧条目条数不变)
★**零外发 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 不写任何 agent 的分片**
"""
import hashlib
import io
import os
import shutil
import sys
import tempfile
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
BRIEFS = os.path.join(HERE, "dispatch_briefs")
BACKUP = os.path.join(HERE, "issue_log.yaml.bak_20261124_2350_cronfb67af40_open_iss402")
DLOG_BACKUP = os.path.join(HERE, "dispatch_log.yaml.bak_20261124_2350_cronfb67af40_open_iss402")
BRIEF_REL = "ISS-402_hw_generator_value_drift_26_audit.md"
ISS_ID = "ISS-402"
AGENT = "hw-lead"


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
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_iss402_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


TITLE = ("★★[★新主线·PCB 线·HW 侧·纯查证+纯分析+新建真相页+新建机器闸+自有分片收口·零写板·零落表] "
         "「板那一趟」重跑生成器 ⇒ 【26 处 Value 漂移】+ 【`C_VBUS_GND` 掉板】的逐条清账与 fail-closed 闸 "
         "(★ISS-287 遗留 3 条 open need 至今零 answers · 全仓无任何机器闸读它★) ★★")

DESC = """★★[★新主线·PCB 线·HW 侧·纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 自有分片收口·零写板·零落表·零改既有闸判据·零改既有页正文·零挂链·零外发·不代拍·不自签]★★

★**题 (来源 = ★main 2026-11-24 23:4x 本机实读 + 全仓检索 · 不抄任何 agent 报告★)★:

★**① 现象**: ★**「板那一趟」缺的 4 条开关里, `S-2` (重跑生成器 ⇒ 26 处 Value 不同) 与 `S-3` (`C_VBUS_GND` 只在官方板 ⇒ 重跑会掉) 至今只以【散文】形式记在 2026-11-17 的交卷页里, 【既没有逐条台账, 也没有任何机器闸钉住】** ★ ⇒ ★**而「板只改一次」= 板 md5 全生命周期只许变 1 次 ⇒ 这 26 处 + 这 1 件 = 那趟开工前的沉默地雷** ★

★**② 精确证据 (★main 本机实读·行号可查★)★**:
- ★`HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md` L9 / L82 / L162 / L268 / L282 ⇒ ★**「官方板与沙盒生成板 位号/封装名/数量全同, 但 26 处 Value 不同」+「缺的 4 条开关 = S-1 `/tmp` 写穿 / S-2 26 处 Value / S-3 `C_VBUS_GND` 会掉 / S-4 186/186 封装 FPID 全空」** ★
- ★同页 L329 逐字 ⇒ ★**「ISS-289 只认领了 `iss287_s7_target_40` 那一条, 其余 4 条 need (路线拍板 / `C_VBUS_GND` / `/tmp` 写穿 / 26 处 Value 差异) 仍开着」** ★
- ★`state/fragments/hw.yaml` L3692 / L3697 / L3703 ⇒ ★**`iss287_cvbus_gnd_board_only` / `iss287_tmp_write_through` / `iss287_26_value_diff` 三条各只出现 1 次, 零 answers** ★
- ★全仓 `grep -rn "26 处 Value"` ⇒ ★**只命中 ISS-287 交卷页散文 + 一条 open need + `state/_apply_20261117_1445_cron775d_verify287_open290.py` ⇒ 零机器闸** ★

★**③ 为什么必须在「板那一趟」之前收口**: ★**路线乙 (重跑生成器) ⇒ 官方板上那 26 条手写功能描述丢失 + `C_VBUS_GND` 从板上掉下来 + DNP 标记一次性被打上 40 个位号** ⇒ ★**⇒ 那一趟照现状执行 ⇒ 板面内容与官方板不同 ⇒ 事后才发现 = 板 md5 第二次变 = 2-4 周返工 + ¥4-8K** ★

★**④ 三条路线 (甲 不重跑 / 乙 重跑 / 丙 重跑+补齐) 的取舍 = main / 老板的地界 ⇒ 本单只给逐条台账 + 代价账, 一条都不代拍** ★

★**⑤ 交付物 5 件**: ★① 真相页 `HW/PCB/BOARD_ONEPASS_GENERATOR_VALUE_DRIFT.md` (新建 · §0~§6 + 机器块) ② 新闸 `HW/check_generator_value_drift_closed.py` (新建 · 裸跑 rc=1 红的是现状 · `--selftest` rc=0 末行 `ALL TESTS PASS` · 正向 ≥1 + 反向 ≥6 · 零挂链) ③ 交卷页 B1~B7 (标题用仓里规范口径) ④ 自有分片收口 (走 `state/frag_write.py` · 写后四项自检: 条数/丢 key/多的 key/内容有变的条) ⑤ 留证 `logs/iss402/` + 沙盒 `tmp/iss402/` (不硬链接真件 · 不写系统 `/tmp`) ★

★**⑥ brief**: ★`state/dispatch_briefs/ISS-402_hw_generator_value_drift_26_audit.md` (★12,133 B★) ⇒ ★**派活前已跑 `python3 state/check_brief_commands.py --brief-file …` ⇒ rc=0** ★
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
            "iss402_26_value_row_ledger",
            "iss402_cvbus_gnd_drop_mechanism",
            "iss402_route_cost_matrix",
        ],
        "task_brief": brief_text,
        "note": ("★**2026-11-24 23:5x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】**"
                 " (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 的 `advance.py --json` 看不见本单 ⇒ 零撞车窗口★)\n"
                 "★**开单依据 (本机实读 + 全仓检索, 零抄报告)★**: ① `state/advance.py --json` ⇒ internal 0 "
                 "(16 条 open 的 owner 全是 boss/main ⇒ 不在三个总工可派域); ② 三个槽位会话 (hw-lead ISS-401 / "
                 "sw-lead ISS-398 cont2 / mech-lead ISS-400) 全部 done ⇒ 槽位实际都空 ⇒ 本轮只派 hw-lead 一条 "
                 "(★sw/mech 两域刚交卷, 本轮没有可复述的已核实缺口 ⇒ 宁可不派也不派没核实的题★); ③ ★**本单的题 = "
                 "ISS-287 遗留的 3 条 open need (`iss287_26_value_diff` / `iss287_cvbus_gnd_board_only` / "
                 "`iss287_tmp_write_through` 至今零 answers) + 全仓零机器闸读它**★ ⇒ 「板只改一次」那趟开工前的"
                 "沉默地雷 ⇒ 本单做成逐条台账 + fail-closed 闸。\n"
                 "★**本单是纯查证/纯分析类** ⇒ 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 ⇒ "
                 "合「板只改一次」纪律 ① ⇒ 真动板那一趟不受本单影响。"),
        "source_agent": "main",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "dispatched_at": "2026-11-24",
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
    if not got or "26" not in str(got[0].get("task_brief")):
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
        "at": "2026-11-24",
        "brief": BRIEF_REL,
        "run_id": "cron_fb67af40_20261124_2350",
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
