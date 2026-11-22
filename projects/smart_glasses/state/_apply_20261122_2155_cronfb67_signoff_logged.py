#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261122_2155_cronfb67_signoff_logged.py
=================================================
cron fb67af40 (ARS45 队列自动派活) 2026-11-22 21:5x ⇒ 三件小事:

① 【记一条签收到 dispatch_log】ISS-339 的签收正文已由兄弟 job cron 775d9893 于 21:51 写进
   `state/issue_log.yaml` (★本 job 的签名脚本被 assert 挡住·**没有双写·没有覆盖**★)
   ⇒ 本脚本只往 `state/dispatch_log.yaml` **追加**一条签收记录 (★flock 保护·RMW 原子★) ⇒ 让下一轮能一眼看出
   「ISS-339 已签收·不是僵尸单」

② 【清掉本 job 自己造的两份冗余备份】(= 当前文件的逐字节副本·纯噪音·本 job 刚建的)

③ 【标注本 job 的签名脚本为「已被 assert 挡住·勿盲目重跑」】

边界:
  ★零写板   ★零落表 (网表/脚表/BOM 不动)   ★零改闸   ★零改真生成器   ★零外发   ★不替老板拍板
  ★**不改 issue_log.yaml** (★775d 已签·我不碰·★避免双写覆盖★)
"""
import fcntl
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
DLOG = os.path.join(PROJ, "state/dispatch_log.yaml")
LOCK = os.path.join(PROJ, "state/.dispatch_log.lock")
SCRIPT = os.path.join(PROJ, "state/_apply_20261122_2150_cronfb67_sign_iss339.py")

ENTRY = {
    "issue": "ISS-339",
    "agent": "hw-lead",
    "at": "2026-11-22 21:5x",
    "brief": (
        "★2026-11-22 21:5x 项目总工签收 (★兄弟 job cron fb67af40 记录·★**签收正文由 cron 775d9893 于 21:51 写入 "
        "`state/issue_log.yaml`·本 job 的签名脚本被 assert 挡住·零双写·零覆盖**★): "
        "★**背景**: 派活 cron fb67af40 (本 job) 21:48 看到 ISS-339 仍停在 `fixing`·而 hw-lead 子会话 "
        "`agent:hw-lead:subagent:35c16b5d` (runId `b91835c0`) 已于 **21:35:46 status=done** (runtime 622 s·abortedLastRun=false) 交卷 ⇒ "
        "本 job 一度判为「僵尸 fixing」并准备签收 ⇒ ★**21:51 兄弟 job cron 775d9893 抢先签收 (fixing → verified)** ⇒ "
        "本 job 的 `assert status == 'fixing'` **当场挡住** ⇒ ★**没双写·没覆盖·零损坏** ★ "
        "⇒ ★**结论: agent 是活着交卷的 ⇒ 本单不是僵尸单 ⇒ 与 775d 的记载一致** ★ "
        "★**fb67af40 本机独立复核 (不抄任何 agent/兄弟 job 报告) 7 项全绿**★: "
        "① `python3 HW/check_board_comparable_gate.py --selftest` ⇒ rc=0 末行 `ALL TESTS PASS` "
        "(★用例 0 常量自检对 `tmp/iss337/seg_parity_selfcheck.py` L59-61 真值 SEG [2300,3200]/CU [4600,5900]/VIA [380,520]; "
        "用例 1 官方终板 18092/2649/433/5726.9 放行; ★用例 2 v44 实测坏臂板 norm=2280/via=371/cu=4568.5 三项全低于下界 ⇒ 被可比性层直接拦; "
        "用例 3 v44 综合判据 = 拒 (★名单层另独立命中 19 条必需零铜网 ⇒ 双保险★)★) "
        "② `python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb --baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb` ⇒ rc=0 "
        "(★N'=45 本板自己跑 DRC 非照抄 · 口径① 全部网 本板 21/参照 4 · 口径② pad≥2 本板 24/参照 7 · 两边都零铜 3 条 CSI_D0_D0_N_SRC / CSI_D0_D2_N / CSI_D0_D3_N★) "
        "③ `state/merge.py` rc=0 (产出 712 · 阻塞 43 高危 33 · 未闭合 340 · 冲突 0) · `state/gate_check.py` rc=0 (★Q1 **18/18** · Q2 3/3 · Q7 9/9 · hw-lead 6/6 缺: 无★) "
        "④ 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板** "
        "⑤ 零改闸 (`gate_check.py` 5ccdcd5f / `compare_arm_official.py` 1471bce6 / `chain_gate.py` 7644a3d3 / `check_pcb_drc.py` 1088fa4f ⇒ 与 main 21:16 记录逐字同) "
        "⑥ 交卷页 26,988 B · B0~B7 八块齐全 · 占位符/未闭合标记 grep = **0** · 页面引用 24 个路径逐个在盘 ⇒ **0 MISS** "
        "(★2 处 `logs/iss339/0[12]_...txt` 是缩略写法·同页 L56/L57/L241 有全名 ⇒ 不是假引用★) "
        "⑦ 分片只写 hw.yaml (`grep -c iss339` = 16) · ★sw.yaml / mech.yaml / pm.yaml 一个字节没被碰 (mtime 11-19 01:42 / 11-19 01:21 / 11-22 21:16) ⇒ 零写别人的分片★ "
        "★**本轮 A 段派活 = 0 条** (★`advance.py --json` ⇒ internal=0 / approvals=0 / waiting=0 / decisions=40 ⇒ "
        "★issue_log 里 16 条 open 全是 boss(5)/main(11) 自留·三个总工名下零 open★ ⇒ ★派活方不开新单 (★开新单是 cron 775d9893 的地界·"
        "且『板只改一次』那一趟还卡着 7 条老板决策 + 板厚/层数/U-1 三件前置 + `q3_storage_and_audio` 外挂 eMMC 进网表★)★) ★"
        "★**775d 已裁的两条 (★本 job 不重开·只复述★)**: ① 可比性闸**不挂** `state/gate_check.py` 日常链 ⇒ 板那一趟开工前单次跑 + 进作业包前置清单 "
        "② 参照板锁死 `state/.lastgood/best_v76mg1_clrfix.kicad_pcb` ★ ★零外发 · 不替老板拍板 ★"
    ),
}


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main() -> int:
    # ---------------- ① dispatch_log 追加 (flock 保护 RMW) ----------------
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
        try:
            with open(DLOG, encoding="utf-8") as f:
                dlog = yaml.safe_load(f)
            if isinstance(dlog, dict):
                dlog = dlog.get("dispatches", [])
            if not isinstance(dlog, list):
                print("dispatch_log 结构异常, 拒绝写")
                return 1
            # 幂等: 已存在同 issue+at 的签收条就不重复追加
            dup = [e for e in dlog
                   if isinstance(e, dict) and e.get("issue") == ENTRY["issue"]
                   and str(e.get("at", "")).startswith("2026-11-22 21:5x")]
            if dup:
                print("dispatch_log: 已存在本轮签收条, 跳过追加")
            else:
                bak = DLOG + ".bak_%s_cronfb67_signoff_log" % time.strftime("%Y%m%d_%H%M")
                shutil.copy2(DLOG, bak)
                dlog.append(ENTRY)
                atomic_write(DLOG, yaml.safe_dump(dlog, allow_unicode=True, sort_keys=False, width=10 ** 6))
                print("dispatch_log: +1 条签收记录 (备份 %s)" % os.path.basename(bak))
            print("dispatch_log 总条数:", len(dlog))
        finally:
            fcntl.flock(lk.fileno(), fcntl.LOCK_UN)

    # ---------------- ② 清本 job 自己造的冗余备份 ----------------
    for name in ("state/issue_log.yaml.bak_20261122_2151_cronfb67_sign_iss339",
                 "state/dispatch_log.yaml.bak_20261122_2151_cronfb67_sign_iss339"):
        p = os.path.join(PROJ, name)
        if os.path.exists(p):
            os.remove(p)
            print("removed redundant backup:", name)

    # ---------------- ③ 标注签名脚本 ----------------
    if os.path.exists(SCRIPT):
        with open(SCRIPT, encoding="utf-8") as f:
            head = f.read()
        marker = "★★【本脚本已于 2026-11-22 21:5x 被自己的 assert 挡住 · 勿盲目重跑】★★"
        if marker not in head:
            inject = (
                '"""' + "\n" +
                marker + "\n"
                "ISS-339 已由兄弟 job cron 775d9893 于 2026-11-22 21:51 签收 (fixing → verified) ⇒ "
                "本脚本的 `assert it.get(\"status\") == \"fixing\"` 当场挡住 ⇒ 零双写 · 零覆盖 · issue_log.yaml 未被本脚本碰过。\n"
                "★★ 重跑本脚本 = 再被 assert 挡住 (status 已是 verified) ⇒ 无害, 但也无用。\n"
                "★★ 真正的签收正文在 state/issue_log.yaml (ISS-339.verify_result) 与 state/dispatch_log.yaml (同一条签收记录)。\n"
                '"""\n'
            )
            # 替换掉原 docstring 的开引号 + 第一行说明
            new_head = head.replace('"""\n', inject, 1)
            atomic_write(SCRIPT, new_head)
            print("annotated:", os.path.basename(SCRIPT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
