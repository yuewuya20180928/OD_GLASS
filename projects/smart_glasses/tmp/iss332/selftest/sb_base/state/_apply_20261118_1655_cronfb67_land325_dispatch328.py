#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-325 落地 (main 独立复核 ⇒ verified) + ISS-328 派出 (hw-lead) · cron fb67af40 · 2026-11-18 16:55

★**为什么现在能派 ISS-328**: ★**ISS-325 已落 (status=verified) ⇒ 它自己的前置条件「ISS-325 必须先落」满足** ★
★**为什么仍要小心**: ★**hw-lead 的分片在 16:25~16:50 被四个 run 先后写过** ⇒ 本单只写新文件 (`logs/iss328/` + 新交付页) + 分片新增 (走 frag_write 原子写) ★
★**为什么这轮不派 sw-lead**: ★**兄弟 job 775d9893 有一个活的 sw-lead 会话在跑 (★16:52:38 还在写 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md`★) ⇒ 两个 job 两个 sw-lead 会话并发写同一批文件 = 本项目 16:28 那次覆盖事故的根因** ★
★**为什么这轮不落 ISS-327**: ★**兄弟 job 的 sw-lead 还在写 SW 侧文件 ⇒ 交卷页/SOP 处于变动中 ⇒ main 不在文件还在动的时候签字** ★
"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1655"
MARK = "★派活标记=CONT-20261118-1655★"

VERIFY_325 = """✅ verified (★main 2026-11-18 16:5x 独立复核·不抄 agent 报告★) ⇒ 交卷物在盘:
· `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` (116,803 B · §0~§9 十节全在 · ★**§3-4-1 裸板级同口径复核**在 · ★**§7-2-3** 在 · 占位符 0 · U+FFFD 0)
· `HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md` (75,531 B · B0~B8 八块 · ★**B6 已贴实际输出**(22 行实测值·不是命令清单) · 占位符 0)
· `state/fragments/hw.yaml` (iss325 命中 **44** · 新 need `iss325_s8_bare_level_crosscheck` 在)
· `logs/iss325/` (91~99 号 raw 在盘)
★**读数独立复核 (main 直接读 raw, 不抄文档)**: 91 号裸板 lu/ctl 均 **viol 6 · unc 37 · 31 网名 · 段数 3088** · 97 号全板 **185/185 封装落位差异行数 = 1** · 98 号 unc 网名集合 **完全相同 = True** (交集 31 · 仅A 0 · 仅B 0) · 99 号同链基线表 **候选 3666 段 vs 基线 14023 段 ⇒ 差一个量级 ⇒ 不是同一条产线** ⇒ ★**数字与文档逐条吻合** ★
★**过度归因已订正 (main 逐句核过)**: 交付页 L632 把「净效应 = 0」**限定**到【唯一变量 = 显式钉那 10 个 `TP_DSI_*`】, 并写明 **「左上布局本身的净效应至今没有任何实测」** ⇒ ★**没有把「同一块板」偷换成「布局无效」** ★
★**板面四 md5 逐字节未变**: 板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` · 网表 `6aee500e60ba0732f83a9cf557ba90ab` · 脚表 `9174309df1ec9411ac8e8d9e80ee386a` · BOM `5b9993992405904a60ac96a020b375d8` ⇒ **G1 仍开** ★
★**门禁链 (main 16:46 实跑)**: merge rc=0 · gate rc=0 · **Q1 18/18 · Q2 3/3 · Q3 977 · Q6 ✅ · Q7 9/9** · issue_check rc=0 ⇒ ★**★但 Q1 的 18/18 是【结构读数】(★mech-lead 那 4 块当时是骨架顶上去的★) ⇒ 不算本单功劳 (★cont5 自己在 B2-22/B7-2 里也写明了★)★★ ★
★★**并发写入留痕 (必须记)**: 本单的交卷页/交付页在 16:25~16:50 之间被 **cont1 / cont2 / cont3 / cont5 四个 run 先后写过** (★交卷页 50KB→60KB→75KB · 交付页 96KB→110KB→116KB★) ⇒ ★**main 已核: 结构完整 · 占位符 0 · 关键口径已订正 · cont5 的 11 处增量用「唯一锚点 edit」保住 ⇒ 判为 verified★** ⇒ ★★**但把「并发写同一批文件」写进留痕: 下次同一 agent 的同一单不许并发两个 run (★且「判僵尸」不能只看 status + transcript mtime, 要看它最后一次写盘落在哪个文件★)★★ ★
★**main 已据此拍板两条 (★写进 `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` 附录 R★)**: P-1「20 条 `PCB_PART_POS` 串删回 10 条」= **暂不删, 一个字都不许动** (★no-op 结论只在演练链成立·不能外推到官方链·删它收益 = 0 风险 > 0★) · P-2「补真对照臂」= **要, 但必须先过对照有效性自检** ⇒ **已开 ISS-328** ★
★**本单遗留 (已转单, 不在本单)**: ① `logs/iss327/` 不在本单域 ② 4 个生成器产物被闸脚本重写 (★复发型·ISS-280 之后第二次★) ⇒ **ISS-329** (owner=main) ③ 「显式钉 TP 是 no-op」⇒ **ISS-328** 第 ② 件要在官方链上复测 ★"""

DISPATCH_328 = ("★**ISS-325 已于 16:55 落 (status=verified) ⇒ 本单前置条件满足, 现派出** ★ "
                "★**本单是 ISS-325 证伪之后开的唯一一条「把前提补上」的单**: ① 补一条真能构成对照的右上臂 (R_SEL_* 挪右上) "
                "⇒ 硬前置 = 全板 185 封装落位 diff ≠ 0 (否则又是 no-op 对照·白跑) · 只许用同链基线比 (禁止拿官方板比) · "
                "判据 = 名单制闸 rc=0 + DRC 0 (不许拿 unc 变少当成功) ② 在官方链同配方下复测 TP no-op "
                "⇒ 给 main 的 P-1 判决补读数 (★决定 §3-S6 那条 20 条串到底删不删★) ★ "
                "★**status 直接落 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★")


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
        byid = {i.get("id"): i for i in issues}
        applied = []

        # ---------- ① ISS-325 落地 ----------
        i325 = byid.get("ISS-325")
        if i325 and i325.get("status") != "verified":
            i325["status"] = "verified"
            i325["verify_date"] = NOW
            i325["verify_result"] = VERIFY_325
            i325["note"] = (i325.get("note") or "") + "\n★**2026-11-18 16:55 main 落地 ⇒ status=verified** ★ " + VERIFY_325
            applied.append("ISS-325 ⇒ verified (★main 独立复核·含并发写入留痕★)")
        else:
            applied.append("ISS-325 已是 verified (跳过)")

        # ---------- ② ISS-328 派出 ----------
        i328 = byid.get("ISS-328")
        if i328 is None:
            applied.append("ISS-328 不存在 (★异常★)")
        else:
            tb = i328.get("task_brief") or ""
            if MARK not in tb:
                i328["task_brief"] = tb + "\n\n---\n\n" + MARK + "\n\n" + DISPATCH_328
            i328["status"] = "fixing"
            i328["dispatched_at"] = NOW
            i328["note"] = (i328.get("note") or "") + "\n★**2026-11-18 16:55 · cron fb67af40 派出** ★ " + DISPATCH_328
            applied.append("ISS-328 ⇒ status=fixing + task_brief += 派出标记")

        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_land325_dispatch328" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        if not any(isinstance(d, dict) and d.get("issue") == "ISS-328" and MARK in str(d.get("brief")) for d in disp):
            disp.append({
                "issue": "ISS-328", "agent": "hw-lead", "at": NOW,
                "brief": MARK + " " + DISPATCH_328,
                "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 16:55 · "
                        "★**ISS-325 已落 ⇒ 前置满足 (status 直接落 fixing ⇒ 无 open 窗口·兄弟 job 775d9893 不会重复派)** ★"),
            })
            applied.append("dispatch_log 追加 ISS-328")
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_land325_dispatch328" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
