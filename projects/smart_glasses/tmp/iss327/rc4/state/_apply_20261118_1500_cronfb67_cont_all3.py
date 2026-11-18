#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-325/326/327 cont brief 追加 (★status 全部保持 fixing★) · cron fb67af40 · 2026-11-18 15:00

★**为什么这一轮是「三张 cont」而不是「三张开新单」**:
  · 14:1x 那轮派的三条 (ISS-325 cont1 / ISS-326 / ISS-327) 的子会话【全部被父 cron run 连带 abort】
    (★ISS-327 那一趟还在 abort 之前出了真事故: 软链写穿真件 ⇒ 已由兄弟 job 775d9893 于 14:47 恢复完毕★)
  ⇒ 三条都处在「僵尸 fixing」状态 ⇒ 本 job 按铁律【不抢派兄弟 job 的活, 但僵尸重派是本 job 的活】
  ⇒ ★**status 全部保持 fixing ⇒ in_flight 规则继续把它们挡住 ⇒ 无重复派活窗口★**
"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"
STAMP = "20261118_1500"
MARK = "★派活标记=CONT2-20261118-1500★"

CONT = {
    "ISS-325": ("ISS-325_hw_s8_leftupper_layout_rehearsal_cont2.md",
                "ISS-325 · hw-lead · ★★cont2 续做 · 收割 + 收卷",
                "★**两条臂已经跑完了 (★裸板 14:21/14:28 · 链终 14:36★) ⇒ 本轮不再等臂, 直接收割** ★ "
                "★**★main 逐条核对出的【最重要的一件事】★★: 两臂的 20 个器件落位【逐个完全相同】"
                "(★pcbnew 逐个读 GetPosition() 实测★) ⇒ 【唯一变量 = 显式钉 10 个 TP_DSI_*】在落位上【完全没生效】"
                "⇒ unc 网名集合【逐条相同】(★裸板 31==31 · 链终 27==27·差集两边都空★) ⇒ 「左上臂 vs 同日对照臂」"
                "【没有构成对照】⇒ 【「显式钉 TP_DSI_*」这条处方被实跑证伪】** ★ "
                "★**⇒ 交付页 §7 的结论必须按实测重写, 不许再写「左上布局 ⇒ 翻转 17 → 5」(★那是 best23 板 vs 现役板, 不是本单两臂之间的差★)** ★ "
                "★**⇒ 机制 (main 读源码找到)**: `state/gen_pcb_netlist_board.py` L1057~L1063 的「测试点贴伙伴件」规则 ⇒ "
                "TP_DSI_* 默认就跟着 R_SEL_* 走 ⇒ 对照臂(不钉 TP)的 TP 落位与左上臂(钉 TP)【自动产生的】落位完全一致 ⇒ 显式钉 TP 是冗余的** ★ "
                "★**⇒ 另有一条判据警告 (臂自己写的)**: `chain.json` 里写「这块板是【官方补丁链的产物】⇒ 不是独立候选臂 ⇒ "
                "要当候选臂比必须与【同链基线】比 (state/compare_arm_baseline.sh)」⇒ 不许拿 compare_arm_official vs 官方板当臂的功劳证据** ★ "
                "★**⇒ 4 处 `__XXX__` 占位符用臂的实测读数填掉 (裸板 unc 37 / 链终 unc 29 / 翻转 5/47) + 补 §9 (跑 logs/iss325/scripts/gen_sec9.py) "
                "+ 补交卷页 B1/B2/B4/B5 (★gate Q1 现在 15/18·缺的就是这 3 格★) + 核分片 + 交 2 条新 need "
                "(iss325_s8_tp_pin_noop_proven / iss325_s8_no_valid_control)** ★"),
    "ISS-326": ("ISS-326_mech_s1_rename_safety_audit_cont1.md",
                "ISS-326 · mech-lead · ★★cont1 续做 · 扫描已做完, 补实证与设计稿",
                "★**上一趟的扫描已经做完了 (★14:23~14:27·★被 abort 前留下的 8 件产物全部可复用★) ⇒ 不许重扫** ★ "
                "★**已有**: `logs/iss326/mech_ref_hits.tsv` (★577,679 B · 1,935 行 · 63 个 distinct 文件★ · 逐命中表) + "
                "`mech_ref_universe.json` (41,049 B · 改名真集) + `reconcile_counts_raw.txt` (三口径对账) + 3 个脚本 ★ "
                "★**main 已核**: 顶层口径 == 递归口径 (★都是 112 文件★) ⇒ 「递归全量」这条已满足; "
                "口径A(精确真集·出现次数)=1,934 / 口径B(命中行数)=1,282 / 口径C(形状像位号)=7,553 ★ "
                "★**★main 上一轮自己 grep 的「571」是【前缀白名单】口径 ⇒ 与你的 1,934 不是矛盾, 但交卷页必须把两个口径都写清并说明差在哪★** ★ "
                "★**⇒ 这一趟真正要做的三件**: ① 「崩 vs 假绿」的沙盒实证 (★`check_board_frame_coords.py` L963 `fps.get()` 安全 vs L999 `fps[LED_REF]` 崩 "
                "⇒ 同文件两种写法; `check_onepass_struct_crosscheck.py` L1107 `t[\"ref\"] == \"R_SEL_D0_N\"` 改名后永不匹配 = 假绿·比崩更坏★) "
                "② 把 1,935 行归并成【按文件的处置表】(★三种失效形态逐条判 + 判据脚本/历史脚本/注释里的 ref 分开列★) "
                "③ MECH 侧位号可达性闸设计稿 (★照抄 SW 那道的判据口径 + 5 条反向用例 + 建闸日基线自己 fresh 测, 不许抄 3★) ★"),
    "ISS-327": ("ISS-327_sw_postrename_gate_sop_cont1.md",
                "ISS-327 · sw-lead · ★★cont1 续做 · 事故后重做",
                "★**上一趟出了真事故 (★软链写穿真件 ⇒ 11 份 SW 文档被改·781 处·闸红 rc=1★) ⇒ "
                "兄弟 job 775d9893 已于 14:47 恢复完毕 (★main 14:5x 独立复核: 残留 0 处 + 闸 rc=0 + 分类统计与事故前基线逐字相同 + 四 md5 全程未变★) "
                "⇒ 本趟不用重做恢复, 但必须知道真件被写过** ★ "
                "★**★本单唯一的新规矩 (违反就是第二次事故)★**: ① 沙盒里凡要写的文件一律真拷贝, 软链只许给只读输入 "
                "② 写前 `assert not os.path.islink(path)` ③ 真件 SW/*.md 一律不许改名 (★「改名后闸链全绿」只能在真拷贝沙盒里验★) "
                "④ 沙盒跑完必查真件 mtime 漂移 = 0 ⑤ 闸脚本副本也要真拷贝 (★上一趟 SW/tools 这条做对了, 照抄★) ★ "
                "★**⇒ 实操**: `logs/iss327/iss327_sb_make.py` L126 那个 `os.symlink()` 改成 `copy_tree` (★脚本里 L148/L286 已有现成的★) "
                "⇒ 改完先在假目录试跑, 确认 `find <root> -type l` 为空 ★ "
                "★**上一趟已完成不许重做**: 基线 (★`logs/iss327/01_baseline_run.log` 10 道闸 rc 全 0 + `01_baseline/` 16 份读数★) "
                "+ 改名映射 (★`tmp/iss327/rename_map_iss327.json` 218 行→改名 186/不动 32★) + `iss327_run_gates.sh` ★ "
                "★**⇒ 这一趟只需跑出「改名后」与「改名后·重建注册表后」两列 ⇒ 出三列对照表 + 当天 SOP + 「真隐患不许被 --freeze-registry 洗白」反向用例** ★"),
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
                applied.append("%s task_brief += %s (★原 brief 全文保留★) · status 保持 fixing"
                               % (iid, marker.split("·")[0].strip()))
            else:
                applied.append("%s %s 已在 brief 里 (跳过)" % (iid, marker))
            it["dispatched_at"] = NOW
            it["note"] = (it.get("note") or "") + (
                "\n★**%s 15:00 · cron fb67af40 续做重派** ★ %s" % (NOW, note))
        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_cont_all3" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))

        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        disp = dl.get("dispatches") or []
        for iid, (fn, marker, note) in CONT.items():
            agent = {"ISS-325": "hw-lead", "ISS-326": "mech-lead", "ISS-327": "sw-lead"}[iid]
            if not any(isinstance(d, dict) and d.get("issue") == iid and MARK in str(d.get("brief")) for d in disp):
                disp.append({
                    "issue": iid, "agent": agent, "at": NOW,
                    "brief": MARK + " " + note,
                    "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 15:00 · "
                            "★**僵尸重派 (★14:1x 那轮的子会话被父 run 连带 abort·status 保持 fixing ⇒ 无 open 窗口·兄弟 job 775d9893 不会重复派★)** ★"),
                })
                applied.append("dispatch_log 追加 %s cont" % iid)
        dl["dispatches"] = disp
        shutil.copy2(DL, DL + ".bak_cronfb67_%s_cont_all3" % STAMP)
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
        for a in applied:
            print("· %s" % a)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
