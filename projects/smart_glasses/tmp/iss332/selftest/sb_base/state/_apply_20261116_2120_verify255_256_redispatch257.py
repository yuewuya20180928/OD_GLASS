#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_2120_verify255_256_redispatch257.py
★main (moli) 2026-11-16 21:2x (cron fb67af40 ARS45 队列自动派活)★
★① ISS-255 (sw-lead) 交卷独立复验 ⇒ 落 verified  ② ISS-256 一并关单 (verified)
★③ ISS-257 (hw-lead) 上一轮 timeout ⇒ 补 note + 续做派活记录 (status 保持 fixing)★

★★**为什么做这件事 (★main 本轮 21:0x~21:2x 自己实跑, 不抄任何交卷报告★)** ★★
· ★**`python3 state/advance.py --json` ⇒ internal = []** ⇒ ★**三个总工名下没有 status=open 的单** ⇒
  ★**但实测两个总工其实已经闲下来了**: sw-lead 的 ISS-255 会话 21:01 已交卷 (status=done) ·
  hw-lead 的 ISS-257 会话 20:53 **status=timeout** (★落表已生效·收尾没交★) ⇒
  ★**⇒ 名额被两条「fixing」占着, 但一条已交卷、一条半途而废 ⇒ 队列名义断线** ★
· ★**sw-lead 的 ISS-255 交卷物实测在盘**: `state/chain_gate.py` (20:55:48) ·
  `state/check_chain_content_anchor.py` (20:55:25 · 37 KB) ·
  `HANDOFF/2026-11-16_sw-lead_ISS255_chain_gate内容锚点.md` (21:00:01 · 26177 B) · 分片 `state/fragments/sw.yaml` ★
· ★**hw-lead 的 ISS-257 实测: 落表成功 (BOM 必装∩[待选型] = 0 ⇒ G1a-7 ✅ · 6 条生成命令 rc=0)，
  但 ① 把落表链的 evidence 词表写成 `[官网]` ⇒ `state/check_netlist.py` rc=1 (G1a-5 由绿转红)
  ② 交付物 5 件只交了 1 件 (§18 台账 / 新门禁 / 交卷单 / 分片 全不在盘) ⇒ 续做重派** ★

★★**ISS-255 为什么能落 verified (★main 自己实跑, 逐条贴数★)** ★★
· `python3 state/merge.py` ⇒ ★**rc=0** ★ (产出 376 · 阻塞 43 · 未闭合需求 217 · **冲突 0**)
· `python3 state/gate_check.py` ⇒ ★**rc=0** ★ (★**【Q1】交付齐备率 18/18** ★ · 【Q2】证据分级率 3/3 · 【Q6】硬件真源闸 ✅ 通过)
· `python3 state/check_chain_content_anchor.py` ⇒ ★**rc=0** ★ (★工具自身健康★) · 四环实读:
  ★**① 网表 ❌** (网表 md5 `7dcf251a10ce…` ≠ 台账最新登记 `16ac89f77c25…` ⇒ ★**落表没进台账 ⇒ 这是 hw-lead ISS-257 的活★**)
  ★**② 原理图 ✅** (位号 218 == 脚表 218 · 标签 584 == 脚 584 · 归一化指纹 `870a4e6cf3ed…` · 11 个 .kicad_sch 归一化后一致 ⇒ ★**uuid 抖动不影响判定**★)
  ★**③ PCB ❌** (网表 480 / 板上带网 482 ⇒ 板是旧网表的板 ⇒ ★**这条是真红 (PCB 那一趟 = 排队不派) ⇒ 必须保持红**★)
  ★**④ BOM ✅** (218 行 (位号,value,dnp) == 脚表聚合 · 逐行一致) ★
· `python3 state/check_chain_content_anchor.py --selftest` ⇒ ★**rc=0 · 用例 14 条 · 通过 14 条 · 失败 0** ★
  (★含 ISS-256 核心反向用例: uuid 抖动 ⇒ 仍绿 + 归一化指纹不变★)
· `python3 state/daily_check.py --self-test-fast` ⇒ ★**rc=0** ★
· `python3 state/chain_gate.py` ⇒ ★**输出格式一字未改** (四环表 + 「准入:」「准出:」前缀 + 结尾修法文案) ★
  ⇒ ★**③ PCB 仍然红 (硬规矩①: 弄绿即本单作废) ✔** ★
· ★**受保护 md5 逐字节不变 (main 21:1x 实测)**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★
· ★**留给 main 的 3 条 need 已登记在分片**: ① 台账登记口径 (转 hw-lead) ② 「--full 准出段全绿」与「③ 必须红」互斥
  ③ ③ 判据依赖 KiCad python 要不要无 KiCad 兜底 ⇒ ★**main 下一轮裁, 不代拍** ★

★★**ISS-256 为什么能关 (★main 自己 grep 全仓★)** ★★
· ★**grep 全仓 `.kicad_sch` + md5/hashlib**: 只剩 `state/chain_gate.py` (★已改成归一化内容口径★) 与
  `state/check_chain_content_anchor.py` (★本文件任何地方都不用 .kicad_sch 的 md5 当判据★) ⇒ ★**无残留锚点** ★
· ★**其余锚点锚的是【网表/脚表 CSV 的 md5】** (`SW/tools/check_demo_panel_spec.py` R6 · `MECH/check_demo_struct_truth.py` G5b/C21)
  ⇒ ★**不是 .kicad_sch md5** ⇒ ★**不属于本条 ⇒ 归 H-1 重锚那一类 (等 hw-lead 落表定稿后由 main 另派)** ★
· ★**本条 = 「.kicad_sch 的 md5 永久不可当锚点」这条硬事实的落地** ⇒ ★**已落地且有反向用例 (14/14) ⇒ 关单** ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml` (ISS-255/ISS-256 → verified + ISS-257 追加 note) + `state/dispatch_log.yaml` (追加一条续派记录)** ★
· ★**不改 ISS-257 的 status (本来就是 fixing, 本轮续做不重复标)** ★
· ★**不碰 PROJECT_TRACKER.md** · ★**不写任何 agent 的分片** · ★**不碰板 / 布线 / 布局** · ★**零外发** · ★**不替老板拍板** ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
IL = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".dispatch_log.lock")
TODAY = "2026-11-16"

VERIFY_255 = (
    "★main 2026-11-16 21:0x~21:2x 独立复验 (★自己实跑, 不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· `python3 state/merge.py` ⇒ ★**rc=0**★ (产出 376 · 阻塞 43 · 未闭合需求 217 · ★**冲突 0**★)\n"
    "· `python3 state/gate_check.py` ⇒ ★**rc=0**★ (★**【Q1】交付齐备率 18/18**★ · 【Q2】证据分级率 3/3 · 【Q6】硬件真源闸 ✅ 通过)\n"
    "· `python3 state/check_chain_content_anchor.py` ⇒ ★**rc=0**★ (工具自身健康) · 四环实读: "
    "★**① 网表 ❌** (网表 md5 `7dcf251a10ce…` ≠ 台账最新登记 `16ac89f77c25…` ⇒ ★**落表没进台账 ⇒ 归 hw-lead ISS-257**★) · "
    "★**② 原理图 ✅** (位号 218 == 脚表 218 · 标签 584 == 脚 584 · 归一化指纹 `870a4e6cf3ed…` · 11 个 .kicad_sch 归一化后一致 ⇒ ★**uuid 抖动不影响判定**★) · "
    "★**③ PCB ❌** (网表 480 / 板上带网 482 ⇒ 板是旧网表的板 ⇒ ★**真红, 必须保持红**★) · "
    "★**④ BOM ✅** (218 行 (位号,value,dnp) == 脚表聚合 · 逐行一致) ★\n"
    "· `python3 state/check_chain_content_anchor.py --selftest` ⇒ ★**rc=0 · 用例 14 条 · 通过 14 条 · 失败 0**★ "
    "(★含 ISS-256 核心反向用例: uuid 抖动 ⇒ 仍绿 + 归一化指纹不变★)\n"
    "· `python3 state/daily_check.py --self-test-fast` ⇒ ★**rc=0**★\n"
    "· `python3 state/chain_gate.py` ⇒ ★**输出格式一字未改** (四环表 + 「准入:」「准出:」前缀 + 结尾修法文案) ⇒ ★**③ PCB 仍红 (硬规矩① 弄绿即本单作废) ✔** ★\n"
    "· ★**受保护 md5 逐字节不变 (main 21:1x 实测)**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★\n"
    "· 交付物在盘: `state/chain_gate.py` (20:55:48) · `state/check_chain_content_anchor.py` (20:55:25 · 37 KB) · "
    "`HANDOFF/2026-11-16_sw-lead_ISS255_chain_gate内容锚点.md` (21:00:01 · 26177 B) · 分片 `state/fragments/sw.yaml` ★\n"
    "★**3 条留给 main 裁的 need (不代拍)**: ① 台账登记口径 (转 hw-lead) ② 「--full 准出段全绿」与「③ 必须红」互斥 ⇒ 本单按硬规矩①选③红并如实报 "
    "③ ③ 判据依赖 KiCad python, 要不要无 KiCad 兜底 ★\n"
    "★**注意 (不是本单的锅)**: ⑤ 投产包那盏红 = 投产包比原理图旧 (hw-lead 20:50 重生成所致) ⇒ main 在 ISS-257 收尾后重跑 `state/gen_production_pack.sh` ★"
)

VERIFY_256 = (
    "★main 2026-11-16 21:2x 独立复核 (★自己 grep 全仓, 不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**grep 全仓 `.kicad_sch` + md5/hashlib**: 只剩 `state/chain_gate.py` (★已改成归一化内容口径★) 与 "
    "`state/check_chain_content_anchor.py` (★任何地方都不用 .kicad_sch 的 md5 当判据★) ⇒ ★**无残留锚点** ★\n"
    "· ★**其余锚点锚的是【网表/脚表 CSV 的 md5】** (`SW/tools/check_demo_panel_spec.py` R6 · `MECH/check_demo_struct_truth.py` G5b/C21) "
    "⇒ ★**不是 .kicad_sch md5 ⇒ 不属本条 ⇒ 归 H-1 重锚那一类 (等 hw-lead 落表定稿后由 main 另派)** ★\n"
    "· ★**反向用例已验** (`check_chain_content_anchor.py --selftest` rc=0 · 14/14 · 含「uuid 抖动 ⇒ 仍绿」) ★\n"
    "· ★**本条 = 「.kicad_sch 的 md5 永久不可当锚点」这条硬事实的落地** ⇒ 已落地且有反向用例 ⇒ 关单 ★"
)

NOTE_257 = (
    "\n\n★2026-11-16 21:2x (cron fb67af40 ARS45 队列自动派活) ★**上一轮会话 timeout ⇒ 续做重派**★ ★\n"
    "· ★**上一轮会话 `agent:hw-lead:subagent:ea25d3e9-19f5-4fc5-a0d4-f31c68d09fd9` (session 6728e97b) status=**timeout** · 20:53 结束** ★\n"
    "· ★**main 21:1x 逐项实跑 ⇒ 落表【成功】, 收尾【没交】**: "
    "★**落表成功**: BOM 必装∩[待选型] = **0** ⇒ `state/check_stage_g1a.py` 的 **G1a-7 ✅** · 6 条生成命令全 rc=0 · 脚数 584 / 器件 218 / K=0 没变 · 板 `611b869e…` + `.kicad_pro` `3e504d2b…` 没动 ★\n"
    "· ★**P0 新红 (上一轮自己造的)**: ★**evidence 词表写错 ⇒ `state/check_netlist.py` rc=1** (「非法值 ['[官网]']」) ⇒ **G1a-5 由绿转红** ⇒ "
    "★**根因 = 落表链自己的词表是 `state/check_netlist.py` L30 的 8 档 (`[官方]` 在内, `[官网]` 不在内) ⇒ 你写进网表 evidence 列的 29 行全非法** ⇒ "
    "★**修法 = 在 `state/gen_netlist.py` 真源里把 `[官网]` 改回 `[官方]` + 重生成 6 件 ⇒ check_netlist rc=0 (BOM 的 evidence 列会自动统一)** ★\n"
    "· ★**交付物 5 件只交了 1 件**: ★**缺 ① `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18 (落表台账没登记新 md5 ⇒ `state/chain_gate.py` ① 网表准入红: 「网表 md5 `7dcf251a10ce…` ≠ 台账最新登记 `16ac89f77c25…`」) "
    "② `HW/check_g1a7_selection_landed.py` (新门禁, 不在盘) ③ `HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md` (交卷单, 不在盘) ④ 分片 `state/fragments/hw.yaml` 本单 claim/artifact/need 一条没登记** ★\n"
    "· ★**处置**: 续做重派 (taskName=queue_iss257_r1 · ★**runTimeout=5400s 绕开 600s 默认超时★**) ⇒ ★**status 保持 fixing** ★\n"
    "· ★**brief 全文**: `state/dispatch_briefs/ISS-257_continue_r1.md` ★\n"
    "· ★**零外发** · ★**未替老板拍 A1/A2/A3 (V-2/V-3/V-4 一条没落)** ★"
)

DISPATCH_257 = (
    "★**续做派活 (★main 2026-11-16 21:2x 实测: 上一轮 20:40 的 spawn status=timeout ⇒ 落表成功但收尾没交 ⇒ 本轮只交「修红 + 4 件缺失交付物」★)** ★\n"
    "★**P0 = 把落表链 evidence 词表 `[官网]` 改回 `[官方]` (29 行, 在 `state/gen_netlist.py` 真源里改) + 重生成 6 件 ⇒ `state/check_netlist.py` rc=0 ⇒ G1a-5 回到 ✅** ★\n"
    "★**补交 4 件: ① `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18 (四字段齐全 · 同一行) ② `HW/check_g1a7_selection_landed.py` + `--selftest` (≥6 反向用例) "
    "③ `HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md` (B1~B6) ④ 分片 `state/fragments/hw.yaml` (含给 sw-lead / mech-lead 各 1 条 need: 新 md5 + §18 行号)** ★\n"
    "★**硬约束不变**: 只改 value/opn/evidence 三列 · 脚数 584 / 器件 218 / K=0 不许变 · 板 `611b869e…` + `.kicad_pro` `3e504d2b…` 逐字节不变 · 不落 V-2/V-3/V-4 · 零外发** ★"
)


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(DL, DL + ".bak_20261116_2120_verify255_256_redispatch257")
    shutil.copy2(IL, IL + ".bak_20261116_2120_verify255_256_redispatch257")

    lock_fh = open(LOCK, "a+")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX)

        # ---- dispatch_log: 追加一条续派记录 ----
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-257", "agent": "hw-lead", "at": TODAY,
            "brief": DISPATCH_257, "redispatch": True,
            "reason": "★上一轮 status=timeout (20:53) ⇒ 落表已生效 (G1a-7 ✅) 但 P0 把落表链 evidence 词表写成 `[官网]` ⇒ `state/check_netlist.py` rc=1 (G1a-5 转红) + 交付物 5 件只交了 1 件 ⇒ 本轮续做「修红 + 补 4 件」★",
            "task_name": "queue_iss257_r1",
            "run_timeout_s": 5400,
            "spawned_by": "fb67af40(本 job 队列自动派活)",
            "status_at_spawn": "fixing (保持 fixing ⇒ 下一轮 in_flight 规则继续挡住重复派)",
        })
        fd, tmp2 = tempfile.mkstemp(dir=HERE, prefix=".dispatch_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp2, DL)
        except Exception:
            if os.path.exists(tmp2):
                os.unlink(tmp2)
            raise

        # ---- issue_log: ISS-255 / ISS-256 → verified ; ISS-257 追加 note (status 不动) ----
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        hit = {"ISS-255": 0, "ISS-256": 0, "ISS-257": 0}
        for it in il.get("issues") or []:
            iid = it.get("id")
            if iid == "ISS-255":
                it["status"] = "verified"
                it["verify_by"] = "main"
                it["verify_date"] = TODAY
                it["verify_result"] = VERIFY_255
                it["note"] = (it.get("note") or "") + (
                    "\n\n★2026-11-16 21:2x (cron fb67af40 ARS45 队列自动派活) ★**main 独立复验后落 verified** ★ "
                    "(★实测: merge rc=0 冲突 0 · gate_check rc=0 Q1 18/18 · check_chain_content_anchor rc=0 + --selftest 14/14 · "
                    "daily_check --self-test-fast rc=0 · chain_gate 输出格式未改且 ③ PCB 仍红 (硬规矩①) ✔ · 板/.kicad_pro md5 逐字节未变★) ★"
                    "★**遗留**: ① 网表准入红 = 台账未登记 (归 hw-lead ISS-257 §18) · ③ PCB 红 = 真红 (排队不派) · ⑤ 投产包红 = 原理图 20:50 重生成 ⇒ main 收尾后重跑 `state/gen_production_pack.sh` ★"
                )
                hit["ISS-255"] += 1
            elif iid == "ISS-256":
                it["status"] = "verified"
                it["verify_by"] = "main"
                it["verify_date"] = TODAY
                it["verify_result"] = VERIFY_256
                it["note"] = (it.get("note") or "") + (
                    "\n\n★2026-11-16 21:2x (cron fb67af40) ★**main 独立 grep 全仓复核后关单 (verified)** ★ "
                    "(★`.kicad_sch` md5 锚点已全部清干净 · 只剩归一化内容口径 · 反向用例 14/14 含「uuid 抖动 ⇒ 仍绿」★) ★"
                    "★**归 H-1 重锚那一类 (网表/脚表 CSV md5 锚点) 不属本条** ⇒ ★**等 hw-lead 落表定稿后由 main 另派 (SW R6 / MECH G5b+C21)** ★"
                )
                hit["ISS-256"] += 1
            elif iid == "ISS-257":
                it["note"] = (it.get("note") or "") + NOTE_257
                it["dispatched_at"] = TODAY
                hit["ISS-257"] += 1
        if any(v != 1 for v in hit.values()):
            raise SystemExit("★命中数异常 = %s ⇒ 中止" % hit)
        _atomic_write(IL, yaml.safe_dump(il, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)
        lock_fh.close()

    chk = yaml.safe_load(open(IL, encoding="utf-8"))
    for iid in ("ISS-255", "ISS-256", "ISS-257"):
        st = [i.get("status") for i in chk["issues"] if i.get("id") == iid][0]
        print("   %s status = %s" % (iid, st))
    print("✅ issue_log.yaml 已原子写: ISS-255 → verified · ISS-256 → verified · ISS-257 note 追加 (status 保持 fixing)")
    print("✅ dispatch_log.yaml 已原子写: 追加 ISS-257 → hw-lead 续做派活记录 (queue_iss257_r1 · runTimeout 5400s)")
    print("★**零外发 · 未替老板拍板 · 不碰 PCB 布线/布局/板 · 不写别人的分片** ★")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
