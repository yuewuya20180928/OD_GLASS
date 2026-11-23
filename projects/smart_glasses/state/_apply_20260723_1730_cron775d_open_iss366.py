#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-23 17:3x · job 775d9893「ARS45 继续执行后继计划」
★开 ISS-366 (hw-lead · S10 换封装那一趟的【网表侧硬缺陷】补行作业包) ★
=========================================================================================
★**为什么这一单现在必须存在 (★main 17:2x 本机实读 · 不抄任何 agent 报告★)**:
  · ISS-364 (hw-lead) 交卷 (17:16) 挖出 3 条新事实, 其中第 3 条是【网表真源级硬缺陷】:
    「4 件的 GND 脚在网表里根本不存在 (C_KEY_PWR / C_KEY_VM / C_KEY_VP / R_BAT_DET_2)
      ⇒ 光改名不够, 必须补 4 行」
  · 同一件事的根因早在 ISS-356 的 D1 就查清并登记成 need `iss356_netlist_4rows_gnd_fix`
    ⇒ ★**但那个 need 的 `to` = 「落表批次」⇒ 它是一张【排进那一趟的待办】, 不是一张【可执行作业包】★**
  · ⇒ ★★后果: 「板只改一次」那一趟开工当天, 这 4 行没有逐字改法、没有沙盒证明、没有回滚说明
    ⇒ ⇒ 要么当天气到补 (落表批次地界 · 现场改真源 = 违纪律), 要么漏掉 ⇒ ★★板子做出来:
       3 颗 100nF 去耦电容接地端悬空 (去耦失效) + R_BAT_DET_2 是 BAT_DET 分压链下臂未接 GND
       (电池检测读数无意义) ⇒ ★**这是一张能出厂的坏板, 不是纸面瑕疵★** ★★
  · ⇒ 本单 = 把那 4 行 (连带 ISS-364 挖出的第 6 条差异 `R_PU_PG` 脚序反转) 做成
    【逐字改法映射 + 沙盒实跑证明 + 机器闸】⇒ ★**零落表 · 零写板 · 零改既有闸** ★
★**为什么它属于「板只改一次」纪律允许的活**: ★**只派【不改网表真源】的活** ——
  本单交的是作业包 + 沙盒 + 闸, ★**真盘网表/脚表/BOM 一个字节都不许动** ⇒ 落表仍由 main 在那一趟排期 ★
★**边界**: ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` 两个文件** (★老条目一字未删·追加式★
  ⇒ 不碰板 / 网表 / 脚表 / BOM / 任何分片 / PROJECT_TRACKER.md §0 / DECISIONS / outbox ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20260723_1730_cron775d_open_iss366"

TITLE366 = (
    "★★[★新主线·PCB 线·网表侧·「板那一趟」S10 同批的【网表硬缺陷】补行作业包·纯作业包+沙盒+新建闸·零写板·零落表] ★★"
    "【ISS-364 (hw-lead, 17:16 交卷) 挖出第 3 条新事实: 「4 件的 GND 脚在网表里根本不存在 "
    "(C_KEY_PWR / C_KEY_VM / C_KEY_VP / R_BAT_DET_2) ⇒ 光改名不够, 必须补 4 行」⇒ "
    "同一根因早在 ISS-356 的 D1 查清并登记成 need `iss356_netlist_4rows_gnd_fix` (★`to` = 「落表批次」★) "
    "⇒ ★★但那只是一张【排进那一趟的待办】, 不是一张【可执行作业包】★★ "
    "⇒ ★★「板只改一次」那一趟开工当天, 这 4 行没有逐字改法 / 没有沙盒证明 / 没有回滚说明 "
    "⇒ ⇒ 要么当天气到补 (★落表批次地界 · 现场改真源 = 违纪律★), 要么漏掉 "
    "⇒ ★★板子做出来是: 3 颗 100nF 去耦电容接地端悬空 (去耦失效) + R_BAT_DET_2 是 BAT_DET 分压链下臂未接 GND "
    "(电池检测读数无意义) ⇒ 这是一张能出厂的坏板, 不是纸面瑕疵★★】★★ "
    "⇒ ★★本单 = ① 4 行的逐字改法映射 (★网表哪一行 / 改成什么 / 脚表要不要同步 / 生成器要不要改★) "
    "② 连带 ISS-364 挖出的第 6 条差异 `R_PU_PG` (板面 pad1/pad2 与脚表真值相反) 的逐字改法 "
    "③ 沙盒实跑: 补 4 行 ⇒ C1/C3/C4 的 Δ + 板面 land 数从 1 变 2 ⇒ 证明【补行】这条路走得通 "
    "④ 一条机器闸 (★判「这 4 件在网表里有没有 GND 脚」+「脚表与网表的脚数是否一致」·★不许判 md5★) "
    "⑤ 一页 + 交卷页 + 分片 + 留证★ "
    "★★【纯作业包 + 沙盒 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★"
)

DESC366 = (
    "★2026-11-23 17:2x main 本机实读 · 全部数字可复跑 · 不抄任何 agent 报告★\n"
    "★**① 病灶 (本单为什么必须存在)**:\n"
    "  · `HW/netlist_v1.csv` 里 `C_KEY_PWR` / `C_KEY_VM` / `C_KEY_VP` / `R_BAT_DET_2` 这 4 件的**接地行把 "
    "`net` 栏写成了信号网名** (形如 `net=KEY_PWR node1=C_KEY_PWR node2=GND`) ⇒ 而正常写法是独立的 `net=GND` 行 "
    "(对照 `C_BULK_SENSOR_CORE`)\n"
    "  · 板生成器 `state/gen_pcb_netlist_board.py` 的 `derive_pads()` **按 (器件, 网名) 去重** ⇒ 这 4 件只长出 **1 个**焊盘\n"
    "  · ⇒ 板面缺接地 land: ★**3 个 100nF 去耦电容接地端悬空 (去耦失效) + `R_BAT_DET_2` 是 BAT_DET 分压链下臂未接 GND "
    "(电池检测读数无意义)★ ⇒ ★**这是能出厂的坏板**★\n"
    "★**② 已有登记 (但不是作业包)**: need key `iss356_netlist_4rows_gnd_fix` (在 `state/fragments/hw.yaml` 的 "
    "`needs_from` 里, ★`to` = 「落表批次」★) ⇒ ★**它排进了那一趟的待办清单, 但没有逐字改法 / 沙盒证明 / 回滚说明★**\n"
    "★**③ 连带项 (ISS-364 挖出, 同一批)**: `R_PU_PG` 板面 pad1/pad2 与脚表真值**相反** ⇒ C1 看不见 (电阻对称) "
    "⇒ 但按脚表真值编号的那一趟脚位就是反的 ⇒ ★**本单要把它一并做成逐字改法**\n"
    "★**④ 纪律归属**: ★**本单只出【作业包 + 沙盒 + 闸】, 真盘网表/脚表/BOM 一个字节都不许动** ⇒ "
    "★**落表由 main 在「板只改一次」那一趟排期** ⇒ ★**板要对着一个不再变的网表画 ⇒ 网表真源的改动必须和板那一趟同批★**"
)

BRIEF_FILE = "ISS-366_hw_netlist_4rows_fix.md"
_BP = os.path.join(HERE, "dispatch_briefs", BRIEF_FILE)
BRIEF366 = (
    "★**任务书全文**: `state/dispatch_briefs/%s` (%d B)★\n"
    "★**题**: ★**把「板只改一次」那一趟必须同批落表的 4 行网表硬缺陷 (C_KEY_PWR / C_KEY_VM / C_KEY_VP / R_BAT_DET_2 "
    "的 GND 脚在网表里根本不存在 ⇒ 板生成器按 (器件, 网名) 去重 ⇒ 这 4 件只长出 1 个 land), 加上连带项 `R_PU_PG` 脚序反转, "
    "做成【逐字改法映射 + 沙盒实跑证明 + 一条机器闸】** ★★\n"
    "★**类别**: ★**纯作业包 + 沙盒 + 新建闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板** ★★\n"
    "★**★分量的所在 (★main 本机实读★)**: ★**3 颗 100nF 去耦电容接地端悬空 (去耦失效) + `R_BAT_DET_2` 是 BAT_DET 分压链下臂未接 GND "
    "(电池检测读数无意义) ⇒ 这是一张能出厂的坏板, 不是纸面瑕疵** ★★ ⇒ "
    "而 need `iss356_netlist_4rows_gnd_fix` 早已登记 (★`to` = 「落表批次」★) ⇒ ★**只是一张待办, 没有逐字改法 / 沙盒证明 / 回滚说明** ★\n"
    "★**★纪律要点 (★与 §一~§四 全表同源, 详见任务书全文★)**: ★**零落表 ⇒ 不许碰网表/脚表/BOM 三个真源文件与两个生成器** ⇒ "
    "本单交的是【改法】不是【改动】⇒ 真盘改动由 main 在「板只改一次」那一趟排期 ★★\n"
    "★**沙盒落 `tmp/iss366_sbx/` (★不许写 /tmp: 2026-11-23 04:4x 实测系统 /tmp 配额已满·写 /tmp 会让闸拿到假读数★)** ★\n"
    "★**交卷页 B2/B3/B4 的标题必须用标准口径** (`验收标准自评` / `证据分级` / `接口取值声明`) ⇒ ★**闸只扫标题行** "
    "(★`state/gate_check.py` 的 `check_blocks()` + 关键词表 L49-51★) ⇒ ★**标题不合规 ⇒ Q1 掉到 15/18 ⇒ 三张签收闸全卡** ★\n"
    "★**零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02)** ★ · ★**不自签 issue_log** ★"
) % (BRIEF_FILE, os.path.getsize(_BP))

NOTE366 = (
    "★派活人: 项目总工 (main / moli) · 2026-11-23 17:3x · cron 775d9893 (ARS45 继续执行后继计划)★\n"
    "★主线口径: 当前主线 = 绘制 PCB 图 (老板 2026-11-17 00:43) ⇒ PCB 线可派; 但「板只改一次」⇒ "
    "本单属【纯作业包 + 沙盒 + 新建闸】类, 零写板 / 零落表 / 零改既有闸 / 零改既有页面 / 零外发 / 不代老板拍板★\n"
    "★外发口径: 老板 2026-11-11 19:31 + 2026-11-12 02:02 ⇒ 不许外发任何邮件 / 询价 / 采购; "
    "缺口一律自己网上查 + 标证据等级 ([官网]/[实测]/[媒体]/[推算]/[0数据]); state/outbox/ 的草稿一律不发★\n"
    "★与在飞单的关系: ISS-364 (hw-lead) 已交卷待签 (★本单不签它, 签收归 main★); "
    "本单与 ISS-364 的沙盒/判据互不覆盖 (★ISS-364 沙盒在 tmp/iss364_sbx/, 本单沙盒在 tmp/iss366_sbx/★)★\n"
    "★★签收前置: ISS-364 / ISS-365 的签收闸都卡在「gate_check Q1 = 18/18」这一条 ⇒ "
    "Q1 掉档的病灶在 sw-lead 的 ISS-363 交卷页 (★骨架 + B2/B3/B4 标题不合规★) ⇒ main 已派 sw-lead cont1 收口 ⇒ "
    "★hw-lead 本单交卷前请自己先跑 `python3 state/gate_check.py` 看 Q1 是不是 18/18 (★不是 18/18 ⇒ 先在交卷页写明, 别自己背这个锅★)★"
)

NEW = [
    {
        "id": "ISS-366",
        "title": TITLE366,
        "severity": "high",
        "source_blocker": "ISS-364",
        "source_agent": "main",
        "desc": DESC366,
        "owner": "hw-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-25",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss356_netlist_4rows_gnd_fix"],
        "task_brief": BRIEF366,
        "note": NOTE366,
        "dispatched_at": "2026-11-23",
    },
]


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
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        for spec in NEW:
            iid = spec["id"]
            if iid in idx:
                it = idx[iid]
                it["status"] = "fixing"
                it["task_brief"] = spec["task_brief"]
                it["note"] = spec["note"]
                applied.append("%s 已存在 ⇒ status→fixing + brief/note 刷新 (幂等)" % iid)
            else:
                issues.append(dict(spec))
                applied.append("新开 %s (%s) · status 直接落 fixing" % (iid, spec["owner"]))

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        if isinstance(dlog, dict):
            entries = dlog.get("dispatches") or []
            dlog_is_dict = True
        else:
            entries = dlog
            dlog_is_dict = False
        _have = any((x.get("issue") == "ISS-366") for x in entries)
        if not _have:
            entries.append({
                "issue": "ISS-366",
                "agent": "hw-lead",
                "at": "2026-11-23",
                "brief": "「板那一趟」S10 同批的网表硬缺陷补行作业包 (4 件 GND 脚 + R_PU_PG 脚序) · 纯作业包 + 沙盒 + 新建闸 · 零写板 · 零落表",
            })
            applied.append("dispatch_log +1 条 (ISS-366 → hw-lead)")
        else:
            applied.append("dispatch_log 已有 ISS-366 条目 ⇒ 幂等不重复追加")
        out = {"dispatches": entries} if dlog_is_dict else entries
        atomic_write(DLOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=10**6))
        applied.append("dispatch_log +1 条 (ISS-366 → hw-lead)")

        # 自检: 写回后条数与末条必须对得上
        chk = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        chk_issues = chk.get("issues") or []
        chk_idx = {i.get("id"): i for i in chk_issues}
        assert "ISS-366" in chk_idx, "★ISS-366 没落进 issue_log★"
        assert chk_idx["ISS-366"].get("status") == "fixing", "★ISS-366 状态没落成 fixing★"
        assert chk_idx["ISS-366"].get("owner") == "hw-lead", "★ISS-366 owner 不对★"
        assert len(chk_issues) == len(issues), "★issue_log 条数对不上 (自检失败)★"
        dchk = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        dlist = dchk.get("dispatches") if isinstance(dchk, dict) else dchk
        assert dlist[-1].get("issue") == "ISS-366", "★dispatch_log 末条不是 ISS-366★"
        applied.append("自检通过: issue_log %d 条 / dispatch_log 末条 = ISS-366" % len(chk_issues))

    for a in applied:
        print("✅ " + a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
