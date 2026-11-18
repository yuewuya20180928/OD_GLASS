#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-325 cont5 / ISS-326 cont2 brief 追加 (★status 保持 fixing★) · cron fb67af40 · 2026-11-18 16:25

★**为什么又续做 (两条, 都死在最后一口气上)**:
  · ISS-325 cont4 (15:29→16:12, 42m42s): `status=failed: subagent run lost active execution context`
    ⇒ ★**但它落盘的东西几乎全在** (交卷页 29,720 B · 交付页 80,471 B · 分片 32 条 · 占位符 0)
    ⇒ ★**只是它起飞的那个验证脚本到 16:18~16:19 才吐完 (91~99 号) ⇒ 比文档晚 ⇒ 文档里没引用**
    ⇒ ★**⇒ cont5 = 纯收尾: ① 把 91~99 号读数写进两份文档 ② B6 贴实际输出 ③ 最终回复** ★
  · ISS-326 cont1 (14:51→16:12, 1h21m): 最后一句 = "Let me build the sandbox — first the builder script."
    ⇒ ★**三件交付物 (沙盒实证 / 处置表 / 闸设计稿) 一件都没做** ⇒ ★**⇒ cont2 = 补三件 + 交卷页按闸链 6 块语义重排** ★

★**main 16:1x 实跑门禁链**: merge rc=0 · gate rc=0 · **Q1 = 14/18** (hw-lead 6/6 · sw-lead 6/6 · ★mech-lead 2/6 缺 B2/B3/B4/B5★) · Q2 2/3 (mech-lead 无证据分级标签) · Q3 972 条 · Q7 9/9
"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1625"
MARK = "★派活标记=CONT-20261118-1625★"

CONT = {
    "ISS-325": (
        "hw-lead", "ISS-325_hw_s8_leftupper_layout_rehearsal_cont5.md",
        "★**15:30 那趟 (cont4) 其实基本交完了** — 交卷页 29,720 B (B0~B6 七块正文都在) + 交付页 80,471 B (§7 已按证伪改写: 「显式钉 TP_DSI_* 是 no-op」/「两臂几何等价」/「归零不可达」) + 分片 32 条 + 占位符 0 ⇒ ★**只差三件**: ① 91~99 号证据 (16:18~16:19 落盘·★比两份文档晚·所以文档里没引用★) 要写进交付页 §3-4/§7-1/§7-2 与交卷页 B1-2/B4-3/B4-6/B2 ② 交卷页 B6 只有命令清单没有实际输出 ③ 最终回复。★**一道臂都不许重跑** (★读数全在 logs/iss325/·★重跑 = 白烧一小时 + 有把臂跑歪的风险★) ★ ★**★99 号同链基线表必须带口径警告**: 候选臂 3666 段 vs 基线 14023 段 ⇒ 段数差一个量级 ⇒ 两边不在同一条工艺线上 ⇒ **不许把「unc 46→29」直接算成「左上布局的功劳」** ★ ★**★Q1 交卷时是 14/18 不是 18/18** (★缺的是 mech-lead 的 B2/B3/B4/B5·它还在飞·不许写成已达标★)"
    ),
    "ISS-326": (
        "mech-lead", "ISS-326_mech_s1_rename_safety_audit_cont2.md",
        "★**14:51→16:12 跑了 1h21m 那趟 (cont1) 死在建沙盒之前** (★最后一句 = 「Let me build the sandbox — first the builder script.」★) ⇒ ★**三件交付物一件都没做**: logs/iss326/sandbox/ 不存在 · mech_ref_disposition.tsv 不存在 · gate_design/ 不存在 ⇒ ★**⇒ 这一趟还是那三件 + 交卷页重排** ★ ★**已落盘可复用 (不许重扫)**: mech_ref_hits.tsv (1,935 行) · mech_ref_universe.json (218 条 = 改名 186 / 不动 32) · reconcile_counts_raw.txt (口径A=1,934 / B=1,282 / C=7,553) · reconcile6_raw.txt (py-only occ=578 + 逐文件计数) ★**★「571 / 1,934 / 578」是三个不同口径, 交卷页三个都要给并写清差在哪★★ ★**★iss326_reconcile6.py L79 崩在 KeyError: MECH/BOARD_ONEPASS_MECH_CLAIMS.md ⇒ 这个 bug 必须写进交卷页 (它就是「脚本会崩」的实例), 不许假装没崩★★ ★**★交卷页必须按闸链的 6 块语义重排**: B1 结论摘要 / B2 验收标准自评(逐条 通过/不通过/未验) / B3 证据分级(实测/官方/推算/0数据 ⇒ Q2 现在 2/3, mech-lead 无标签) / B4 接口取值声明(interface_claims ⇒ Q3) / B5 未决项与卡点 / B6 自证复现命令 ⇒ ★**现在这版 B2~B6 名字跟闸链要的不是一回事 ⇒ 所以 Q1 = 14/18 (mech-lead 2/6, 缺 B2/B3/B4/B5)·你填完就 18/18**★ ★ **交卷页 B0~B6 现在全是「(施工中)」占位 ⇒ 必须填满 + 占位符 0** ★"
    ),
}


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        applied = []
        for iid, (agent, fn, note) in CONT.items():
            it = idx.get(iid)
            if not it:
                applied.append("%s 不存在 (★异常★)" % iid); continue
            body = open(os.path.join(HERE, "dispatch_briefs", fn), encoding="utf-8").read()
            tb = it.get("task_brief") or ""
            if MARK not in tb:
                it["task_brief"] = tb + "\n\n---\n\n" + body
                applied.append("%s task_brief += %s (★原 brief 全文保留★) · status 保持 fixing" % (iid, MARK))
            else:
                applied.append("%s %s 已在 brief 里 (跳过)" % (iid, MARK))
            it["dispatched_at"] = NOW
            it["note"] = (it.get("note") or "") + ("\n★**%s 16:25 · cron fb67af40 续做重派** ★ %s" % (NOW, note))

        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_cont_325_326" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        for iid, (agent, fn, note) in CONT.items():
            if not any(isinstance(d, dict) and d.get("issue") == iid and MARK in str(d.get("brief")) for d in disp):
                disp.append({
                    "issue": iid, "agent": agent, "at": NOW,
                    "brief": MARK + " " + note,
                    "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 16:25 · "
                            "★**续做重派 (★两条 cont 都在最后一口气上挂掉·但已落不少盘·本轮从已完成位置续·"
                            "status 保持 fixing ⇒ 无 open 窗口·兄弟 job 775d9893 不会重复派★)** ★"),
                })
                applied.append("dispatch_log 追加 %s cont" % iid)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_cont_325_326" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
