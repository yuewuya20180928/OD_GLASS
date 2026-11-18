#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (fb67af40 队列自动派活) 2026-11-16 18:1x: 生成 ISS-246 / ISS-247 的【续做派活单】
=========================================================================================
★**为什么是【续做】而不是【新开】**: ★**上一轮 (兄弟 job 775d9893 17:39:40 spawn) 的两个子会话
  都在 460s 撞 timeout 死掉了** ⇒ mech-lead 的 ISS-246 / hw-lead 的 ISS-247 都处在
  「status=fixing 但会话已死」的僵尸态 ⇒ ★**盘上已有实打实的中间产物** ⇒
  ★**重派时必须把断点写进 brief ⇒ 否则子 agent 会重跑一遍已经绿的门禁 (白烧预算)★**

★**派活铁律 (本 job 硬规则)**: ① **先落 fixing 再 spawn** (本轮两条本来就是 fixing ⇒ 状态已对)
  ② **task 内容 = advance.py 给的 brief 全文 + 固定抬头 + 续做硬规矩块 + 固定纪律脚**
  ③ **brief 里不许出现不存在的命令** ⇒ 生成后过 `state/check_brief_commands.py`
"""
from __future__ import annotations

import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)

HEADER = """【项目总工派活 · 队列自动派活 · 闭环 {iid}】你是 {role}。
"""

FOOTER = """
★额外纪律: ① 写分片必须用 state/frag_write.py (禁止 open(p,"w")) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ⑤ 交卷前跑 python3 state/merge.py (rc 必须 0) && python3 state/gate_check.py (Q1 必须 18/18) 并把输出贴进回复
★**⑥ 主线口径 (★老板 2026-11-11 10:07★)**: 当前主线 = **硬件原理图 demo 绘制** ⇒ ★**PCB 布线 / 布局 / 板框 一律不许碰** (★排队等原理图定稿★) ⇒ 你这一单只在【原理图 / 网表 / 门禁】这一层干活 ★
★**⑦ 时间纪律 (★针对上一轮 460s 撞 timeout★)**: ★**先落盘骨架再填内容** ⇒ 交卷单先写文件头 + B1~B6 六个标题 (★`gate_check.py` 按标题认块★), 再往里填 ⇒ ★**不许把整轮预算全花在想/查上 ⇒ 想不出来就先落骨架 ⇒ 本轮 runTimeout 5400s ⇒ 别把文件写到最后一分钟★ ★
"""

CONT_246 = """
★★**【续做硬规矩 · ★main 2026-11-16 18:0x~18:1x 自己实测的断点★】★★**
★**上一轮会话 `agent:mech-lead:subagent:b56b051e-b0e1-497d-9e28-6fd444c295e5` (session 6c104a66) 17:39:40 → 17:46:46 (460s) ⇒ status=timeout · abortedLastRun=true ⇒ 死在【交卷物② 还没落盘】那一步** ★

★★**★已经落盘的 (★main 18:0x 自己实跑复核过 ⇒ 你不要重做★)** ★★
· `MECH/HW_CROSS_REVIEW_TRIAGE.md` ⇒ ★**第 3 跳重锚已落**: 顶部 ISS-246 注 + §0 **Q-11** 行 + §3.1 **R-04** 行 + §3.1 机器保证段 + §7 G5/G5b 行 + §3.1 第三跳注 (★mtime 2026-11-16 17:43★) ★
· ★**`python3 MECH/check_demo_struct_truth.py` ⇒ rc=0 · 23/23 组全过 (★main 18:0x 实跑原样输出: 「【结论】23/23 组检查通过 | FAIL 0 组」★)** ★
· ★**`python3 MECH/check_demo_struct_truth.py --selftest` ⇒ rc=0 · 「反向用例: 14/14 抓到了」 (★main 18:0x 实跑★)** ★

★★**★本轮只干这 3 件 (★别重跑已经绿的活, 别再动 §3.1 的锚点数字★)** ★★
★★**交卷物 (3 件 · 下面 ①② 两条路径现在盘上不存在, 就是本单要新建的)** ★★
1. ★**`HANDOFF/2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md`** (★**路径必须一字不差** ★ ⇒ ★**`MECH/HW_CROSS_REVIEW_TRIAGE.md` 顶部的 ISS-246 注里已经引用了它 ⇒ 名字对不上 = 留痕断链★) (★**B1~B6 六个块标题照 `HANDOFF/2026-11-16_sw-lead_ISS245_SW侧H1重锚第4跳.md` 的写法** ★ ⇒ ★**`gate_check.py` 按标题认块: B1 结论摘要 / B2 验收标准自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令★)
2. ★**`state/fragments/mech.yaml`** (★走 `python3 state/frag_write.py --agent mech-lead --add-artifact ...` 原子写★ ⇒ ★**不许手改 yaml★ ★ ⇒ ★**内容必须带上: 本单改动的文件清单 + 门禁 23/23 + selftest 14/14 + 反向自证结果 + 留痕 R-04★)
3. ★**验收标准 ⑤-3 反向自证 (★`/tmp` 沙盒★)**: 在 `/tmp` 沙盒里把 §3.1 锚点改回旧 md5 (`34132f7e40a241e1fae1476be0eafbd5`) ⇒ ★**G5b / C21 那 2 组必须重新红** ⇒ 装回去 ⇒ ★**又绿** ⇒ ★**把三步原样输出贴进交卷单 (★这是证明这两组不是摆设的唯一证据★)** ★

★★**还要补齐的验收输出 (★自己实跑 + 贴原样输出★)** ★★
· ★**`python3 state/merge.py` ⇒ rc=0** (★main 18:0x 实跑已 rc=0 ⇒ 「✅ STATE.yaml 已刷新」★) ★
· ★**`python3 state/gate_check.py` ⇒ rc=0** (★main 18:0x 实跑已 rc=0 ⇒ 【Q1】18/18 口径不变★) ★
· ★**HW/ 下 5 个受保护 md5 交卷前后逐字节不变** (★main 18:0x 实测现值★): 网表 `611c3ba3db3dc7de7213063375b96d01` · 脚表 `ef436a37412ac9b6eac3c9f41f1edca4` · BOM `2a7305741134788dfee9f13f34c656b4` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★
· ★**`landed_at` = `2026-11-16 15:45:45` 的凭据**: ★**`HW/netlist_v1.csv` 的 mtime 实测就是 `2026-11-16 15:45:45` (★`stat -c '%y' HW/netlist_v1.csv`★)** ⇒ ★**台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.4 L656/L657 有新旧 md5 对照** ⇒ ★**不许自己编时间** ★

★★**三条不许动的 (★上一轮已经没动, 这轮也不许动★)** ★★
· ★**不许再改 §3.1 锚点里的 md5 数字** (★现值已经是落表后真值 `611c3ba3…` / `ef436a37…` ⇒ 再改就与台账对不上, **C21 会红**★) ★
· ★**不许改 `MECH/check_demo_struct_truth.py` 的判据逻辑 / 阈值 / 反向用例** (★一个字都不许★) ★
· ★**不许碰 `HW/` 下任何文件 (只读核 md5 用)** · ★**不许碰 SW 分片 / SW 台账 (★那是 ISS-245 sw-lead 的活, 它此刻正在跑★)** · ★**不许碰 `state/issue_log.yaml`** · ★**零外发** ★
"""

CONT_247 = """
★★**【续做硬规矩 · ★main 2026-11-16 18:0x~18:1x 自己实测的断点★】★★**
★**上一轮会话 `agent:hw-lead:subagent:9eab132b-2680-45d1-9249-23fec358194e` (session 2ad65579) 17:39:40 → 17:46:46 (460s) ⇒ status=timeout · abortedLastRun=true ⇒ 死在【写交卷单之前】⇒ ★**盘上 5 件交付物 0 件** ★

★★**★沙盒还在 (★别重做, 直接接着干★)**: `/home/yuewuya/.openclaw/workspace-hw/.sandbox_iss247/` ⇒ ★**`sb0` = 基线副本 · `sb1` = 已按改法改过的副本 (★上一轮 17:42 建好★)** ★

★★**★main 18:0x 亲自复核过的沙盒事实 (★可直接引用, 但**结论仍要你自己再跑一遍贴原样输出**★)** ★★
· ★**改法落点在 `state/gen_netlist.py` (★真源, 不许手改 CSV★)** ★★`sb1/state/gen_netlist.py` 的 ★**L381 + L393 两行 `add()` 的第 4 个参数 (node2)★** ★★
  · L381: `add("P1", "VBUS_5V_F1", "FB_VBUS", ★**"C_VBUS_OUT"**★, "FB_VBUS", ...` ⇒ 改成 ★**`"VBUS_5V_F1"`**★ ★
  · L393: `add("P1", "VBUS_5V_CHG", "C_VBUS_GND", ★**"C_VBUS_OUT"**★, "C_VBUS_GND", ...` ⇒ 改成 ★**`"VBUS_5V_CHG"`**★ ★
  · ★**注意**: brief 正文里写的 "L369/L381" 与真盘现号 (★L381 / L393★) 不一致 ⇒ ★**以你自己 grep 出来的行号为准, 不许照抄 brief★** ★
· ★**沙盒实跑结果 (★上一轮跑的, 你要自己再核一遍★)**: sb1 里 `HW/check_netlist_contradiction_r3.py` ⇒ ★**findings 由 3 条降到 2 条 (★F1 消失, 剩 F2 + F3★) · R3-A1 / R3-A2 双绿** ⇒ 脚表 md5 `ef436a37…` 逐字节不变 · BOM md5 `2a730574…` 逐字节不变 · `--expect-resolved` 仍 ★**18 条**★ · `HW/check_netlist_selfconsistency.py` rc=0 · 脚数完整性闸 rc=0 (★沙盒里要把 `state/kicad.sh` 拷进去, 上一轮踩过这个坑: 「No such file or directory」★) ★
· ★**上一轮挖出一个必须写进作业包的坑**: ★**`HW/check_netlist_contradiction_r3.py` 的 `--selftest` 里 T7 / T8 断言的是【落表前现状】** (★T7 = 恰 3 条 findings · T8 = A1+A2 红★) ⇒ ★**F1 一落表, T7 / T8 必红** ⇒ ★**下一批落表必须同时改这两条断言** ⇒ ★**这条要写进「下一批落表清单 v1」** ★
· ★**上一轮看到一个待查现象**: ★**`sb0` / `sb1` 的 `HW/PCB/demo_mainboard*.kicad_sch` 逐字节不同** (★脚表 / `.net` 没变却变了图★) ⇒ ★**要么查清原因写进作业包, 要么明写「待查」** ★

★★**★真盘 5 个受保护 md5 (★main 18:0x 实测现值, 交卷前后必须逐字节不变★)** ★
· 网表 `611c3ba3db3dc7de7213063375b96d01` · 脚表 `ef436a37412ac9b6eac3c9f41f1edca4` · BOM `2a7305741134788dfee9f13f34c656b4` · 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ★

★★**★交卷物 (5 件 · 下面 ③④ 两条路径现在盘上不存在, 就是本单要新建的)** ★★
1. ★**落表作业包 v1** (★含 ★**`sb0` → `sb1` 的 diff 原文**★ + 影响面: 网表 / 脚表 / BOM / `.net` / `SCHEMATIC_V1.md` 各变几行 + 新旧 md5 + 复现命令 + 回滚方法) ⇒ ★**落 `HW/SCHEMATIC_LANDING_F1_WORKPACKET_V1.md` (★新建★)** ★
2. ★**下一批落表清单 v1** (★F1 + V-2/V-3/V-4 的落表顺序 + 互斥/撞车分析 + 各自前置条件 + ★**T7 / T8 那条坑★**★) ⇒ ★**落 `HW/SCHEMATIC_LANDING_NEXT_BATCH_V1.md` (★新建★)** ★
3. ★**机器门禁 (★判「F1 是否已落」· 挂在【语义】上不许挂 md5 · `--selftest` ≥5 条反向用例, 每条自证「真的改到了目标」★)** ⇒ ★**落 `HW/check_iss247_f1_landed.py` (★新建★)** ★
4. ★**交卷单 `HANDOFF/2026-11-16_hw-lead_ISS247_F1落表作业包v1.md` (★新建★)** (★**B1~B6 六个块标题照 `HANDOFF/2026-11-16_sw-lead_ISS245_SW侧H1重锚第4跳.md` 的写法** ★ ⇒ ★**`gate_check.py` 按标题认块: B1 结论摘要 / B2 验收标准自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令★) ★
5. ★**`state/fragments/hw.yaml`** (★走 `python3 state/frag_write.py --agent hw-lead --add-artifact ...` 原子写★ ⇒ ★**不许手改 yaml★ ★ ⇒ ★**不许碰 mech.yaml / sw.yaml★) ★

★★**★验收标准 (★全部自己实跑 + 贴原样输出★)** ★★
· ★**`python3 state/merge.py` ⇒ rc=0** (★main 18:0x 实跑已 rc=0★) · ★**`python3 state/gate_check.py` ⇒ rc=0** (★main 18:0x 实跑已 rc=0★) ★
· ★**你的新门禁: 正向 rc=0 + `--selftest` rc=0 (≥5/5)** ★
· ★**不许把已有门禁的既有红数调没**: `HW/check_netlist_contradiction_r3.py` (★真盘仍恰 3 条★) · `HW/check_netlist_selfconsistency.py --expect-resolved` (★仍 18 条★) · 脚数完整性闸 · ERC · `HW/check_netlist.py` · `HW/check_netlist_pins.py` · ★**`HW/check_part_selection_matrix.py` (仍 8/8)** ★

★★**★边界 (★重申, 逐条自证★)** ★★
· ★**真盘零写入**: 网表 / 脚表 / BOM / 板 / `.kicad_pro` / 原理图 / `HW/PCB/` 下任何文件 **一个字都不许改** ⇒ ★**本单只允许新增作业包 / 门禁 / 交卷单 3 类文件 + 写分片** ★
· ★**沙盒收尾**: ★**先把 diff 原文抄进作业包, 再把 `/home/yuewuya/.openclaw/workspace-hw/.sandbox_iss247/` 清掉** ⇒ ★**交卷单里写清「已清 + 真盘 md5 前后对照」** ★
· ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 查不到就写降级方案, 不许挂「等回复」 ★
· ★**不许碰 PCB 布线 / 布局 / 板框** · ★**不许碰 F2 (J_CHG 位号消歧) / F3 (板侧 DNP 标记) —— 本单只登记, 不做** · ★**不许碰 SW / MECH 分片与台账** · ★**不许改已有门禁脚本的判据逻辑** · ★**不替老板拍板 (V-2/V-3/V-4 一条没拍)** · ★**`state/issue_log.yaml` 不自改 (verify 留给 main)** ★
"""

TARGETS = {
    "ISS-246": {"role": "结构总工 (mech-lead, 带散热)", "cont": CONT_246},
    "ISS-247": {"role": "硬件总工 (hw-lead)", "cont": CONT_247},
}


def main() -> int:
    log = yaml.safe_load(open(os.path.join(HERE, "issue_log.yaml"), encoding="utf-8"))
    by_id = {i.get("id"): i for i in (log.get("issues") or [])}
    outdir = os.path.join(HERE, "dispatch_briefs")
    os.makedirs(outdir, exist_ok=True)
    import check_brief_commands as cbc

    rc_all = 0
    for iid, cfg in TARGETS.items():
        it = by_id[iid]
        brief = it.get("task_brief") or ""
        text = (HEADER.format(iid=iid, role=cfg["role"]) + brief + cfg["cont"] + FOOTER)
        p = os.path.join(outdir, "%s_redispatch.md" % iid)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        rc, miss = cbc.check_text(text, p)
        print("── %s ⇒ %s (%d 字符) · 命令存在性闸 rc=%d %s"
              % (iid, p, len(text), rc, miss or ""))
        if rc:
            rc_all = 1
    return rc_all


if __name__ == "__main__":
    sys.exit(main())
