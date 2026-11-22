#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-325 cont3 / ISS-327 cont2 brief 追加 (★status 保持 fixing★) · cron fb67af40 · 2026-11-18 15:30

★**为什么又续做**: 15:0x 派的那两条 (ISS-325 cont2 / ISS-327 cont1) 的子会话【在 15 分钟处被超时掐掉】
  ⇒ 但两趟都【落了不少盘】 ⇒ 本轮按「已完成的位置」续, 不从头来:
    · ISS-325: §9 已生成 + 4 处 `__XXX__` 已填 + 分片已写 ⇒ 只剩 §3-3 数据格 + §2-3/§3-2/§6-2/§7 证伪改写 + 交卷页 B1/B2/B4/B5
    · ISS-327: 造场脚本已修好 (软链→真拷贝) + 三臂沙盒已建 + 跑批读数已落 + 注册表已重建 ⇒ 只剩三列对照表 + 主交付物 + 交卷页 + 分片
  ⇒ ★**ISS-326 (mech-lead) 那一趟还在跑 (15:35 仍 running) ⇒ 本轮不碰它** ★
"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1530"
MARK = "★派活标记=CONT3-20261118-1530★"

CONT = {
    "ISS-325": ("ISS-325_hw_s8_leftupper_layout_rehearsal_cont3.md",
                "ISS-325 · hw-lead · ★★cont3 续做 · 收尾",
                "★**★上一趟 (15:0x) 已完成: §9 已生成 (交付页 42,815→60,381 B) + 4 处 `__XXX__` 已全部填掉 (命中数 0) "
                "+ 分片已写 (hw.yaml 命中 25) ⇒ 这一趟只剩 3 件: ① §3-3 的数据格还是一句待办说明 "
                "(§① 那张表里 main 已实测好的读数: 裸板 lu/ctl 均 viol 6 / unc 37 / 31 网名 / 翻转 5-47; "
                "链终 lu/ctl 均 viol 6 / unc 29 / 27 网名; 现役 0/45/43/17-47; best23 0/23/21/5-47) "
                "② 交卷页 B1/B2/B4/B5 (★mtime 还是 13:24·没动过·★gate Q1 现在 15/18·缺的就是这 3 格★) "
                "③ §2-3/§3-2/§6-2/§7 的【证伪】改写 (★上一趟 agent 临死前说的最后一句就是「Now the core rewrite: §7 (falsification), "
                "plus §3-2/§3-3/§6-2/§2-3 corrections」⇒ 正要干就被掐了★)** ★ "
                "★**★两条臂的落位【逐个完全相同】(pcbnew 逐个读 GetPosition()·20 个器件)⇒ 唯一变量(显式钉 10 个 TP_DSI_*)"
                "在落位上【完全没生效】⇒ unc 网名集合【逐条相同】(裸板 31==31 · 链终 27==27)⇒ ★**「左上臂 vs 同日对照臂」"
                "没有构成对照 ⇒ 「显式钉死 TP_DSI_*」这条处方【被实跑证伪】**★ ⇒ 机制 = gen_pcb_netlist_board.py "
                "L1057~L1063 的「TP 贴伙伴件」规则 (★对照臂不钉 TP·但 TP 会自动跟着 R_SEL_* 走·落位与左上臂自动产生的完全一致★) ★ "
                "★**⇒ 另有一条判据警告 (臂自己写在 chain.json 里)**: 「这块板是【官方补丁链的产物】⇒ 不是独立候选臂 ⇒ "
                "要当候选臂比必须与【同链基线】比 (state/compare_arm_baseline.sh)」⇒ 不许拿 compare_arm_official vs 官方板当臂的功劳证据 ★ "
                "★**⇒ 交 2 条新 need: iss325_s8_tp_pin_noop_proven / iss325_s8_no_valid_control** ★"),
    "ISS-327": ("ISS-327_sw_postrename_gate_sop_cont2.md",
                "ISS-327 · sw-lead · ★★cont2 续做 · 交卷收尾",
                "★**★上一趟 (15:0x) 已完成: 造场脚本已修好 (★L126 的 os.symlink() → 真拷贝 + L67 加了 assert_no_symlink_in()★) "
                "+ 三臂沙盒已建 (★sbCtl 板 md5=611b869e·改名命中 0 · sbR0 板 md5=fadf2c2f·命中 0 · sbR3 板 md5=fadf2c2f·命中 6★) "
                "+ 跑批读数已落 (12_sbCtl/13_sbR0/14_sbR3/16_sbR1 + 19_run_all_cont1.log + 19b_ctl_rerun.log) "
                "+ 注册表已重建 (15_sbR0_freeze_stdout 18 条 / 17_sbR3_freeze_stdout 含改名后名) "
                "+ 真件快照已留证 (10_pre_realfile_snapshot.txt) ★ "
                "★**★上一趟 agent 自己抓到并修掉的 bug (★很关键★)**: 「sbCtl got the HW rename applied, so it wasn't a true control」 "
                "⇒ 修完后 sbCtl 板 md5 = 611b869e… (与真件一致) + 改名后位号命中 0 份 ⇒ 它现在才是真对照 ★ "
                "★**★⇒ ⇒ 这一趟只剩三件: ① 把已有读数归并成【四臂对照表】(★基线/sbCtl/sbR0/sbR3★) + "
                "★★注意: `19_run_all_cont1.log` 里 sbCtl 那一列是【坏对照臂】的读数(几乎全红)·必须用 `19b_ctl_rerun.log` 那一版★ "
                "⇒ 交卷页要写明「sbCtl 那一列取自修 bug 后的重跑版」·并且那两道 rc=2 (r6_chainjudge / r6_hardprot) "
                "★**要查清 rc=2 到底是【反向用例失败】还是【脚本报错】, 不许当红灯也不许当绿灯放过★**★) "
                "② 写主交付物 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (★现在【不存在】★) "
                "③ 写交卷页 (★现在只有 987 B★) + 写分片 (★sw.yaml 里 iss327 命中 0★) + 补【对照有效性自检】一节 ★ "
                "★**★本单唯一的新规矩 (★违反就是第二次事故★)**: 沙盒凡要写的文件一律真拷贝·写前 assert not os.path.islink·"
                "真件 SW/*.md 一律不许改名·跑完必查真件 mtime 漂移 = 0 ★ "
                "★**★⇒ 你上一趟已经把事故根因修掉了 ⇒ 这一趟不许再改那个脚本, 但必须跑一次 `find tmp/iss327 -type l` 证明它真的不产软链** ★"),
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
        for iid, (fn, marker, note) in CONT.items():
            it = idx.get(iid)
            if not it:
                applied.append("%s 不存在 (★异常★)" % iid); continue
            body = open(os.path.join(HERE, "dispatch_briefs", fn), encoding="utf-8").read()
            tb = it.get("task_brief") or ""
            if marker not in tb:
                it["task_brief"] = tb + "\n\n---\n\n" + body
                applied.append("%s task_brief += %s (★原 brief 全文保留★) · status 保持 fixing" % (iid, marker))
            else:
                applied.append("%s %s 已在 brief 里 (跳过)" % (iid, marker))
            it["dispatched_at"] = NOW
            it["note"] = (it.get("note") or "") + ("\n★**%s 15:30 · cron fb67af40 续做重派** ★ %s" % (NOW, note))
        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_cont_325_327" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        for iid, (fn, marker, note) in CONT.items():
            agent = {"ISS-325": "hw-lead", "ISS-327": "sw-lead"}[iid]
            if not any(isinstance(d, dict) and d.get("issue") == iid and MARK in str(d.get("brief")) for d in disp):
                disp.append({
                    "issue": iid, "agent": agent, "at": NOW,
                    "brief": MARK + " " + note,
                    "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 15:30 · "
                            "★**僵尸重派 (★15:0x 那轮的子会话在 15 分钟处被超时掐掉·但已落不少盘·本轮从已完成位置续·"
                            "status 保持 fixing ⇒ 无 open 窗口·兄弟 job 775d9893 不会重复派★)** ★"),
                })
                applied.append("dispatch_log 追加 %s cont" % iid)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_cont_325_327" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
