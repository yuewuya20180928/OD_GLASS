#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1300_verify239_revive172_240_fixbriefs.py
★main (moli) 2026-11-16 13:0x (cron fb67af40 ARS45 队列自动派活)★
★① ISS-239 (hw-lead) 独立复验 ⇒ 落 verified  ② ISS-172 / ISS-240 两条僵尸 fixing 复活重派  ③ 两条 brief 的 HANDOFF 产出路径加「★新建★」标记 (过命令存在性守卫)★

★★★**为什么做这三件事 (★main 本轮 12:1x~13:0x 自己实跑, 不抄任何交卷报告★)** ★★
· ★**`python3 state/advance.py --json` ⇒ internal = [] · approvals = [] · waiting = []** ⇒ rc=1
  ⇒ ★**根因 = 三个总工名额全被【僵尸/已交卷未验的 fixing】占着** ★
· ★**① ISS-239 (hw-lead) 其实已经交卷完了 (★会话自己跑完了, 不是在飞★)**:
  ★**会话 `agent:hw-lead:subagent:1c662a78` (session ed081370) 11:28:37 起 · 12:01:10 止 · runtime 1951s · status=done · abortedLastRun=false** ★
  ⇒ ★**main 本轮 12:2x~12:4x 独立实跑复验 (★不抄交卷报告★)**: `HW/check_pin_function_labels.py` rc=1 (★**15 条 = 已知缺陷基线**★ · --expect-known rc=0 · 15/15 逐条一致 · --selftest **10/10 全过**) ·
  `state/check_netlist.py` rc=0 · `state/check_netlist_pins.py` rc=0 · `state/check_sch_erc.py` rc=0 (ERC=0) · `state/check_sch_pinfull.py` rc=0 ·
  `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (【Q1】18/18) · ★**5 个受保护 md5 逐字节未变** (34132f7e… / b21b743a… / c195a117… / 611b869e… / 3e504d2b…) ★
  ⇒ ★**⇒ 本单落 verified (★main 实跑, 不是抄 agent 自述★)** ★
· ★**② ISS-172 (sw-lead) = 半落地僵尸 (★比上一轮前进了一大截★)**: 会话 `agent:sw-lead:subagent:4180ade4` (session a725f6d0) 11:41:38 起 · 11:59:47 止 · runtime 1090s · ★**status=timeout · abortedLastRun=true · prompt-error "This operation was aborted"** ★
  ⇒ ★**main 12:1x~12:4x 逐文件实跑**: ★**`SW/LOAD_SWITCH_SELECTION_FACTS.md` 74809 B (mtime 11:56 ⇒ §0~§6 正文真写出来了: 8 条判据 / 3 候选 + 3 alternates / 2 条降级 / 出处表 / 基准块都在)** ★ ·
  ★**`SW/tools/check_load_switch_selection.py` 26693 B (mtime 11:56)** ★ · ★**交卷单不在盘** ★ · ★**分片 sw.yaml 未写 (mtime 08:39)** ★
  ⇒ ★**main 在 /tmp 沙盒副本上把 4 处缺陷逐个定位并实跑验证 (★真盘一行没动★) ⇒ 4 处全改后门禁 rc=0 且 --selftest 8/8** ★
  ⇒ ★**③ ISS-240 (mech-lead) = 半落地僵尸**: 会话 `agent:mech-lead:subagent:f70c6e17` (session 4fa212e3) 11:52:03 起 · 12:10:38 止 · runtime 1111s · ★**status=timeout · abortedLastRun=true** ★
  ⇒ ★**main 12:2x 实跑**: ★**`MECH/check_hinge_fpc_truth.py` 在盘 27912 B (12:03) + `MECH/HINGE_FPC_GEOMETRY_TRUTH.md` 24980 B (12:01) + 正文已补标** ★ ⇒ ★**门禁 FAIL 1/9 (G3) · --selftest 9/10 (T3 抓不到)** ★ · ★**交卷单不在盘** ★
  ⇒ ★**main 在 /tmp 沙盒副本上把 2 处缺陷定位并实跑验证 ⇒ 改后门禁 9/9 PASS 且 --selftest 10/10** ★
· ★**④ 派活前命令存在性守卫 (`python3 state/check_brief_commands.py`) ⇒ 2 条 brief 报错**: ISS-240 / ISS-241 的 brief 里写了【本单要新建的交卷单路径】, 但那行前面挂的是「★**交卷单**」⇒ ★**不在守卫的白名单词表里 (新建/新增/产出/交付物/…) ⇒ 被当成"引用了不存在的路径"** ★
  ⇒ ★**修法 = 把那两行改成「★**新建交卷单**」⇒ 命中守卫的"本单产出"白名单 ⇒ 闸不再误报 (★闸的设计意图就是这个: 由 brief 作者显式背书★)** ★
  ⇒ ★**★不动任何命令/路径本身★ · 只加"新建"二字 ⇒ 不改任务范围** ★

★★**边界 (本脚本)★★ ★★
· ★**只写 `state/issue_log.yaml` (3 条单的状态/备注/brief 一处措辞) + `state/dispatch_log.yaml` (追加 2 条续派记录)** ★
· ★**不改任何交付物文件** · ★**不碰 PROJECT_TRACKER.md §0** · ★**不写任何 agent 的分片** · ★**不碰板 / 布线 / 布局 / 网表 / 脚表 / BOM** ★
· ★**零外发** · ★**未替老板拍板** (ISS-239 的 3 条待 main 裁决项本脚本一条没拍) ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
IL_LOCK = os.path.join(HERE, ".issue_log.lock")
DL_LOCK = os.path.join(HERE, ".dispatch_log.lock")
TODAY = "2026-11-16"

# ─────────────────────────────────────────────────────────────────────────────
VERIFY_239 = (
    "★main (moli) 2026-11-16 12:2x~12:4x **独立实跑复验** (★不抄交卷报告★) ⇒ **落 verified** ★\n"
    "· ★**会话**: `agent:hw-lead:subagent:1c662a78` (session ed081370) 11:28:37 起 · 12:01:10 止 · runtime 1951s · status=done · abortedLastRun=false ⇒ ★**这一轮是真交卷, 不是僵尸** ★\n"
    "· ★**11 道验收命令全部 main 自己实跑**: `HW/check_pin_function_labels.py` rc=1 (★**15 条缺陷 = 已知缺陷基线**★ · 与冻结快照 15/15 逐条一致) · "
    "`--expect-known` rc=0 (★「当前状态确为已知缺陷基线」★) · `--selftest` rc=0 ★**10/10 全过**★ · "
    "`state/check_netlist.py` rc=0 · `state/check_netlist_pins.py` rc=0 (★每个针脚归属唯一★) · `state/check_sch_erc.py` rc=0 (★ERC=0★) · "
    "`state/check_sch_pinfull.py` rc=0 (★逐器件脚数全相等★) · `state/merge.py` rc=0 · `state/gate_check.py` rc=0 (★【Q1】18/18★)\n"
    "· ★**5 个受保护 md5 main 亲测逐字节未变**: `HW/netlist_v1.csv` 34132f7e… · `HW/netlist_v1_pins.csv` b21b743a… · `HW/BOM_v1.csv` c195a117… · "
    "`HW/PCB/demo_mainboard.kicad_pcb` 611b869e… · `HW/PCB/demo_mainboard.kicad_pro` 3e504d2b… ★\n"
    "· ★**本单零落表** (★脚表里 pin4/pin5 的功能名串号 + U_LDO_S28 缺 pin3 都还在 ⇒ 落表等 main 排期★) · ★**未替老板拍板** ★\n"
    "· ★**留给 main 的 3 条裁决项 (★本单一条没拍★)**: ① `U_LDO_S28.pin3` 走 A(动板+脚数基线 584→585) 还是 B(不动板+闸里留显式豁免) ② pin1 要不要改 (★改了会炸 BOM★) "
    "③ 落表批次 owner 与排期 (★含 MECH `§1` / SW `§1` 两个 H-1 重锚★) ★"
)

NOTE_172 = (
    "\n\n★2026-11-16 13:0x (cron fb67af40 队列自动派活) ★**僵尸 fixing 复活 + 重派 (★半落地·病灶已由 main 在沙盒定位到 4 处★)** ★\n"
    "· ★**上一轮会话**: `agent:sw-lead:subagent:4180ade4` (session a725f6d0) 11:41:38 起 · 11:59:50 止 · runtime 1090s · ★**status=timeout · abortedLastRun=true · prompt-error 'This operation was aborted'** ★\n"
    "· ★**main 12:1x~12:4x 逐文件实跑 (★≠ 零交付物·比上轮前进一大截★)**: `SW/LOAD_SWITCH_SELECTION_FACTS.md` **74809 B** (mtime 11:56 ⇒ §0~§6 正文真写出来了: 8 条判据 / 3 候选 + 3 alternates / 2 条降级 / 出处表 / 机器基准块都在) · "
    "`SW/tools/check_load_switch_selection.py` **26693 B** (mtime 11:56) ⇒ ★**这两件别重写, 只把它们修到绿**★ · ★**交卷单不在盘** ★ · ★**分片 sw.yaml 未写 (mtime 08:39)** ★\n"
    "· ★**main 在 /tmp 沙盒副本上把 4 处缺陷逐个定位并实跑验证 (★真盘一行没动★) ⇒ 4 处全改后: 门禁 rc=0 · --selftest 8/8 全过** ★\n"
    "  ① ★**C0 (真凶)**: 文档 L272 写的是 `<!-- BEGIN 选型证据基准块 -->` (★带尾部 ` -->`★) 而脚本 L59 `BASELINE_BEGIN = \"<!-- BEGIN 选型证据基准块\"` (★不带★) ⇒ 切出来的块以 ` -->` 开头 ⇒ `strip_fence()` 只在**开头就是 ``` 时**才剥围栏 ⇒ 围栏没剥 ⇒ `json.loads` 报 char 0 ⇒ "
    "**改法二选一 (★都实测过★)**: (a) 脚本 `BASELINE_BEGIN` 改成 `\"<!-- BEGIN 选型证据基准块 -->\"` (★1 行·推荐·文档 HTML 注释保持完整★) 或 (b) 文档 BEGIN 行去掉尾部 ` -->` ★\n"
    "  ② ★**C6 崩 (ValueError)**: 脚本 L286 `toks += re.findall(r\"@\\s*([\\d.]+)\\s*V\", live_val)` 返回的是**单元素元组**, 而 L288 `for num, unit in toks` 要两个 ⇒ 直接抛异常 ⇒ "
    "**改法**: `toks += [(m, \"V\") for m in re.findall(r\"@\\s*([\\d.]+)\\s*V\", live_val)]` ★\n"
    "  ③ ★**C8**: 判据是 `^#{2,4}\\s*<候选id>\\b` ⇒ 标题必须**以候选 id 开头**; 而文档 §2.3/§2.4/§2.5 写的是 `### 2.3 TPS22991RAA …` ⇒ 不匹配 ⇒ "
    "**改法**: 把候选小节标题改成 `### TPS22991RAA …` (★去掉 `2.x ` 编号前缀·§2.2 表头那行不用动★) ★\n"
    "  ④ ★**M3/M4 是假用例 (自证失败)**: helper `_drop_obj_keep_json` (脚本 L333~346) 的**最后一个数组元素**分支 `return head + text[start:end]` 把要删的对象又拼回去了 ⇒ 变异后 JSON 非法 ⇒ 门禁只报 C0 ⇒ 打不中 C1/C5 ⇒ "
    "**改法**: 该分支改成 `return head[:-1] + text[end:]` (★★删掉尾逗号 + 不再拼回对象★★) ⇒ 实跑 M3 → C1 变红 / M4 → C5 变红 ⇒ selftest 8/8 ★\n"
    "· ★**续做范围 = 改这 4 处 + 补交卷单 + 补分片 ⇒ 四件交付物齐** ★ · ★**零外发** · ★**未替老板拍型号/优先级序 (★决策页 §A5: 老板先拍优先级序, 不是拍型号★)** ★\n"
    "· ★**★命中「不许落表」: 网表 L50 的 `[待选型]` 判据串本单一个字都不许改 (★等老板拍完型号再由落表批次改★)** ★"
)

NOTE_240 = (
    "\n\n★2026-11-16 13:0x (cron fb67af40 队列自动派活) ★**僵尸 fixing 复活 + 重派 (★半落地·病灶已由 main 在沙盒定位到 2 处★)** ★\n"
    "· ★**上一轮会话**: `agent:mech-lead:subagent:f70c6e17` (session 4fa212e3) 11:52:03 起 · 12:10:38 止 · runtime 1111s · ★**status=timeout · abortedLastRun=true** ★\n"
    "· ★**main 12:2x 逐文件实跑**: ★**`MECH/check_hinge_fpc_truth.py` 27912 B (12:03) + `MECH/HINGE_FPC_GEOMETRY_TRUTH.md` 24980 B (12:01) + 正文已补标 (★都在盘·别重写★)** ★ ⇒ "
    "★**门禁实跑 = FAIL 1/9 (只红 G3) · --selftest = 9/10 (只抓不到 T3)** ★ · ★**交卷单不在盘** ★ · ★**分片两条新 claim 还没写** ★\n"
    "· ★**main 在 /tmp 沙盒副本上把 2 处缺陷定位并实跑验证 (★真盘一行没动★) ⇒ 改后: 门禁 9/9 PASS · --selftest 10/10 全过** ★\n"
    "  ① ★**G3 红 = 分片缺两条新 claim**: `state/fragments/mech.yaml` 里没有 `mech_hinge_stack_truth_mm` / `mech_hinge_stack_demo_mm` ⇒ "
    "**改法**: 走 `python3 state/frag_write.py --agent mech-lead --add-claim 'key=mech_hinge_stack_truth_mm value=25.30 note=…'` 与 `--add-claim 'key=mech_hinge_stack_demo_mm value=5.00 note=…'` "
    "(★**必须走 frag_write.py 原子写, 不许手改 yaml·不许动别人已有的 key★★) ⇒ 实跑 G3 转绿 ★\n"
    "  ② ★**T3 抓不到 = 判据漏比一处 (★不是假用例, 是门禁少比了一个字段★)**: T3 变异的是**收口页机器块 `claims:` 块里**的 `mech_hinge_stack_truth_mm: \"25.30\"` ⇒ 而 G3 只比了**分片 claim** 和 `computed` 块 ⇒ "
    "★**压根没读收口页的 claims 块** ⇒ 变异打不到 G3 ⇒ **改法: G3 里补一段把 `truth[\"claims\"]` 里的 `mech_hinge_stack_truth_mm` / `mech_hinge_stack_demo_mm` 也拿来跟重算值比** (★★判据只加不减·G1/G2/G4~G9 一条都不许动★★) ⇒ 实跑 T3 变红 ★\n"
    "· ★**旧 claim `mech_hinge_stack_fixed_mm` = 25.00 一律不许改值** (★它已在收口页 `legacy_divergences` 登记 ⇒ 那是 main 要裁的 M-04 三档选项·本单不许代拍★) ★\n"
    "· ★**受保护脚本一个都不许碰** (hinge_usb_check.py / check_demo_struct_truth.py / cavity_recalc_check.py / service_port_check.py / hw_cross_review_check.py / display_biosafety_v2_check.py / DISPLAY_BIOSAFETY_CRITERIA_V2.md) ★ · ★**零外发** · ★**不碰 PCB 布线/布局/板框** ★\n"
    "· ★**★不许改网表 / 脚表 / BOM / 板 (★改了会打断 MECH C21 三方对账与 SW R6 锚点★)** ★"
)

DISPATCH_172 = (
    "★**续做派活 (★main 2026-11-16 13:0x 实测: 上一轮会话 11:41:38~11:59:50 撞 timeout (runtime 1090s · abortedLastRun=true · prompt-error 'This operation was aborted') "
    "⇒ ISS-172 是**半落地僵尸**: facts doc 74809 B (§0~§6 正文已写全) + 门禁脚本 26693 B 都在盘, 但门禁 rc=1 (★C0 + C6 崩 + C8★) 且 --selftest 0/8 ⇒ 交卷单与分片缺 ⇒ 本轮重派 · runTimeout 5400s · "
    "★**续做不是从零开始: 门禁脚本与矩阵正文都别重写, 按 main 沙盒定位的 4 处改 (①BASELINE_BEGIN 带 ` -->` ②C6 toks 单元素元组 ③候选小节标题以 id 开头 ④_drop_obj_keep_json 末元素分支) ⇒ 改后门禁 rc=0 且 selftest 8/8, 再补交卷单 + 分片**★)** ★"
)

DISPATCH_240 = (
    "★**续做派活 (★main 2026-11-16 13:0x 实测: 上一轮会话 11:52:03~12:10:38 撞 timeout (runtime 1111s · abortedLastRun=true) ⇒ ISS-240 是**半落地僵尸**: "
    "check_hinge_fpc_truth.py 27912 B + HINGE_FPC_GEOMETRY_TRUTH.md 24980 B + 正文补标都在盘, 但门禁 FAIL 1/9 (只红 G3) 且 --selftest 9/10 (只抓不到 T3) ⇒ 交卷单缺 ⇒ 本轮重派 · runTimeout 5400s · "
    "★**续做不是从零开始: 按 main 沙盒定位的 2 处改 (①分片补 mech_hinge_stack_truth_mm=25.30 + mech_hinge_stack_demo_mm=5.00 (走 frag_write.py) ②G3 补比收口页 claims 块) ⇒ 改后门禁 9/9 PASS 且 selftest 10/10, 再补交卷单 + 分片**★)** ★"
)

REASON_172 = (
    "★上一轮 status=timeout/aborted (runtime 1090s) ⇒ 半落地僵尸: facts doc + 门禁脚本在盘但门禁 rc=1 (C0/C6/C8) 且 selftest 0/8 ⇒ 交卷单与分片缺 ⇒ 仍无交卷★"
)
REASON_240 = (
    "★上一轮 status=timeout/aborted (runtime 1111s) ⇒ 半落地僵尸: 门禁脚本 + 收口页在盘但 G3 红 (分片缺两条 claim) 且 T3 抓不到 ⇒ 交卷单缺 ⇒ 仍无交卷★"
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
    shutil.copy2(IL, IL + ".bak_20261116_1300_verify239_revive172_240")
    shutil.copy2(DL, DL + ".bak_20261116_1300_verify239_revive172_240")

    # ── 1) issue_log: 复验 ISS-239 + 复活两条僵尸 + 修两条 brief 的产出标记 ──
    lf = open(IL_LOCK, "a+")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        il = yaml.safe_load(open(IL, encoding="utf-8"))
        hit239 = hit172 = hit240 = hit241 = 0
        for it in il.get("issues") or []:
            iid = it.get("id")
            if iid == "ISS-239":
                it["status"] = "verified"
                it["verify_by"] = "main"
                it["verify_date"] = TODAY
                it["verify_result"] = VERIFY_239
                hit239 += 1
            elif iid == "ISS-172":
                it["note"] = (it.get("note") or "") + NOTE_172
                it["dispatched_at"] = TODAY
                hit172 += 1
            elif iid == "ISS-240":
                it["note"] = (it.get("note") or "") + NOTE_240
                it["dispatched_at"] = TODAY
                # ★brief: 交卷单那行改成「★新建交卷单」⇒ 命中派活前守卫的"本单产出"白名单★
                tb = it.get("task_brief") or ""
                old = "★**交卷单** `HANDOFF/2026-11-16_mech-lead_ISS240_跨铰链FPC几何三口径收口.md`"
                new = "★**新建交卷单** `HANDOFF/2026-11-16_mech-lead_ISS240_跨铰链FPC几何三口径收口.md`"
                if old in tb:
                    tb = tb.replace(old, new, 1)
                it["task_brief"] = tb
                hit240 += 1
            elif iid == "ISS-241":
                tb = it.get("task_brief") or ""
                old = "★**交卷单** `HANDOFF/2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md`"
                new = "★**新建交卷单** `HANDOFF/2026-11-16_sw-lead_ISS241_BOM待选型21件OPN选型矩阵.md`"
                if old in tb:
                    tb = tb.replace(old, new, 1)
                it["task_brief"] = tb
                hit241 += 1
        if (hit239, hit172, hit240, hit241) != (1, 1, 1, 1):
            raise SystemExit("★命中数异常 (239=%s 172=%s 240=%s 241=%s) ⇒ 中止"
                             % (hit239, hit172, hit240, hit241))
        _atomic_write(IL, yaml.safe_dump(il, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()

    # ── 2) dispatch_log: 追加两条续派记录 ──
    df = open(DL_LOCK, "a+")
    try:
        fcntl.flock(df, fcntl.LOCK_EX)
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": []}
        dl.setdefault("dispatches", []).extend([
            {"issue": "ISS-172", "agent": "sw-lead", "at": TODAY,
             "brief": DISPATCH_172, "redispatch": True, "reason": REASON_172},
            {"issue": "ISS-240", "agent": "mech-lead", "at": TODAY,
             "brief": DISPATCH_240, "redispatch": True, "reason": REASON_240},
        ])
        _atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))
    finally:
        fcntl.flock(df, fcntl.LOCK_UN)
        df.close()

    chk = yaml.safe_load(open(IL, encoding="utf-8"))
    for iid in ("ISS-239", "ISS-172", "ISS-240", "ISS-241"):
        st = [x.get("status") for x in chk["issues"] if x.get("id") == iid][0]
        print("   %s status = %s" % (iid, st))
    print("✅ issue_log.yaml 已原子写: ISS-239 → verified (★main 独立实跑复验★) · ISS-172/ISS-240 追加 note (★status 保持 fixing★) · ISS-240/ISS-241 brief 交卷单加「新建」标记")
    print("✅ dispatch_log.yaml 已原子写: 追加 ISS-172 → sw-lead / ISS-240 → mech-lead 两条续派记录 (redispatch=True)")
    print("★**零外发 · 未替老板拍板 · 不碰板/布线/布局/网表/脚表/BOM · 不写任何 agent 的分片** ★")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
