#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0640_verify228_230_open231_232.py
★main (moli) 手动清账 + 开新单 · 2026-11-16 06:40 (cron 775d9893 继续执行后继计划)★

★★**为什么做这件事 (★本轮实测, 不抄任何交卷报告★)** ★★
· ★**ISS-228 (sw-lead) 子会话** `agent:sw-lead:subagent:4930b32a` ★**status=done · endedAt 06:02:10** ★
  ⇒ 交付物在盘 + 新闸 `SW/tools/check_rk3572_vccio_domain.py` rc=0 + selftest 16/16 + 分片含 answer ⇒ 落 `verified` ⇒ **放掉 sw-lead 名额** ★
· ★**ISS-230 (hw-lead) 子会话** `agent:hw-lead:subagent:9b449129` ★**status=done · endedAt 06:13:13** ★
  ⇒ 交付物 4/4 在盘 + HW 全闸绿 + `--expect-resolved` rc=1 (21 条待落, 预期) + 分片真落盘 ⇒ 落 `verified` ⇒ **放掉 hw-lead 名额** ★
· ★**ISS-229 (mech-lead) 子会话** `agent:mech-lead:subagent:07d81b89` ★**status=timeout (abortedLastRun=true) · endedAt 06:16:15** ★
  ⇒ ★**会话在写文档中途被超时杀掉** ⇒ 交付物①② 已落盘 / ③④ 未落 ⇒ **不落账, 同单续做** ★

★★**本轮新开 2 条 (★都是「原理图/网表/门禁」主线活, 一条都不碰 PCB 布线布局★)** ★★
· ★**ISS-231 (sw-lead)**: SW 侧 R6 锚点过期重锚 (★走 ISS-225 台账 §4 的 H-1 流程, 台账 H-4 明写「main 派 sw-lead 重锚」★) ★
· ★**ISS-232 (hw-lead)**: 板 ↔ 网表 焊盘级等价门禁红的 2 处「多余」(C_VBUS_GND) ⇒ 定位并给网表侧逐字修法 ★

★★**边界 (两单共同)★★ ★★
★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到写降级方案 ★
★**不许替老板拍板** ⇒ V-2 / V-3 / V-4 / 集热面材质 / u8 / d 值 / 板长 全部只出选项 + 量化代价, 不代拍 ★
★**不许碰 PCB 布线 / 布局 / 板框** ⇒ 板侧 8 项 (B-1~B-8) 继续**排队**, 本 job 不派 ★
★**受保护 md5 交卷前后必须逐字节不变** ★
"""
import os
import shutil
import datetime as dt
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"

BRIEF_231 = """★★**目标 (★内部活·软件/门禁侧·不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把 SW 侧的门禁锚点【重锚】到盘上真值** —— 因为 ISS-223 落表后这盏灯【按设计变红了】, 现在没人管它 ★★
⇒ ★**目标状态: `python3 SW/tools/check_demo_panel_spec.py` rc=0 (R1~R7 全过) + `--selftest` rc=0 (16/16) + R7 留痕在场** ★

★★**为什么是现在 (★main 2026-11-16 06:2x~06:3x 自己实跑, 不是抄交卷报告★)** ★★
· ★**main 实跑 `python3 SW/tools/check_demo_panel_spec.py` ⇒ rc=1, 唯一红项就是 R6** ★:
  `R6 盘上真源 md5 HW/netlist_v1.csv = 3215020b6d4120e1b7728227effdc6d3 ≠ 锚点登记 13f59a43dbd35dc6cb16e897c8c891ab (真源被换了或锚点过期)`
· ★**main 实跑 `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ rc=1 (15/16)** ⇒ ★**基线红 ⇒ 反向用例只能过 15 条 (第 16 条正好就是基线那盏灯)** ★
· ★**根因 = 上游合法落表, 不是门禁坏了 (★有据★)**: `HW/netlist_v1.csv` 现值 md5 = `3215020b6d4120e1b7728227effdc6d3` (main 实测) ⇒ ★**这是 ISS-223 (落表第 2 批) 改的** ⇒ ★**SW 侧锚点还钉在 ISS-220 (第 1 批) 的 `13f59a43…`** ★
· ★**项目里早写好了处置流程 (★不是 main 现编的★)**: `SW/SW_MD5_BASELINE_LEDGER.md` §4 流程表 **H-1** (四步重锚) + **H-4** (★逐字写「ISS-223 (落表第 2 批) 落表后 ⇒ R6 会自动红 (★**这是设计**★) ⇒ main 派 sw-lead 重锚 (走 H-1)」★) ★
· ★**脚表不用动 (★main 实测★)**: `HW/netlist_v1_pins.csv` 现值 md5 = `a600afae493f5a7a6c55f46ad35ac89c` ⇒ ★**与台账 §1 锚点 `entries[1].md5` 一致 ⇒ 只有网表那一条要改** ★

★★**你要做的 (★四件交付物, 少一件即无效★)** ★★
① ★**按 H-1 重锚台账 (★只改 3 个字段 + 加 1 行留痕, 一个字都不许多改★)** ★
  ⇒ ★**台账文件 = `SW/SW_MD5_BASELINE_LEDGER.md`** ★
  ⇒ ★**§1 机器可读锚点块 (`# BEGIN SW_MD5_ANCHORS` … `# END SW_MD5_ANCHORS`) 里 `anchors.source_ledger.entries[]` 中 `file: HW/netlist_v1.csv` 那一条**: ★
    · `md5` ⇒ 改成 **盘上实测值** (★交卷那一刻实测, 写 32 位全值★) ★
    · `prev_md5` ⇒ 改成 `13f59a43dbd35dc6cb16e897c8c891ab` (★就是现在的旧锚点★) ★
    · `by` ⇒ 改成 `ISS-223` (★落表单号★) ★
    · `landed_at` ⇒ 写落表时刻 (★照 ISS-223 交接单里的时刻, 别自己编★) ★
  ⇒ ★**§1 `landing_records` 已有 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 与 `HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md` 两处 ⇒ 若 ISS-223 的落表记录还在别处, 把它补进去 (★R6 判据 ⑥ 要求「登记的位置一个都不存在 ⇒ 红」★)** ★
  ⇒ ★**§3 留痕账加一行** (★格式照抄已有的 R-01/R-02/R-03 三行★): 单号 + 新 md5 + 旧 md5 + ★**判别证据**★ + 复现命令 ★
  ⇒ ★**★关键纪律★**: ★**R6 的判据逻辑 (三方对账那 6 条) 一个字不许动** ★ ⇒ ★**不许把 `--skip-md5` 设成默认跳过** ★ ⇒ ★**不许为了让门禁变绿去改 `HW/` 下任何文件** ★
② ★**交卷前必须处理这条【并发警告】(★main 06:3x 实测到的真冲突★)** ★
  ⇒ ★**hw-lead 的 ISS-232 同时在飞 (它要改网表的节点串写法 ⇒ 网表 md5 可能再变一次)** ★
  ⇒ ★**所以: 你重锚用的 md5 必须是【交卷那一刻盘上实测的 md5】, 并且必须能在落表台账里查到 (R6 判据 ②/③/④/⑤ 的硬要求)** ★
  ⇒ ★**若 ISS-232 已经落了网表 (盘上 md5 已不是 `3215020b…`) ⇒ 必须用 ISS-232 交接单里登记的新 md5 来重锚, 并在留痕里写明「ISS-232 并发变更」** ★
  ⇒ ★**不许为了「锚一个稳定值」去卡住/等待/干预另一个 agent 的单** ★
③ ★**机器门禁实跑 (★交卷前最后一件事, 输出原样贴进交接单★)** ★
  · `python3 SW/tools/check_demo_panel_spec.py` ⇒ ★**rc=0** ★ (R1~R7 全过, R6 绿 + R7 留痕在场)
  · `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ ★**rc=0, 16/16 全过** ★ (★基线绿了之后第 16 条才可能过⇒ 这是你真修好的证据★)
  · `python3 SW/tools/timing_check.py` ⇒ rc=0 (★70/70★, ★不许它变红★)
  · `python3 state/merge.py && python3 state/gate_check.py` ⇒ rc=0 (★Q1 18/18★)
  ⇒ ★**★反向自证 (★必做, 否则交卷不算数★)★**: 拿一份**网表副本**把盘上 md5 改回 `13f59a43…` ⇒ R6 必须红 ⇒ ★**证明「你改的是锚点, 不是把红灯调没」** ★
④ ★**交接单 + 分片** ★
  · ★**新建 `HANDOFF/2026-11-16_sw-lead_ISS231_SW侧R6锚点重锚.md`** (★B1~B6 六块齐全, ★格式照抄上一份 sw-lead 交接单★) ★
  · ★**分片** `state/fragments/sw.yaml` ⇒ ★**必须走 `python3 state/frag_write.py` 原子写 (★不许 `open(p,"w")`★)** ★ ⇒ ★**只回本单相关的一条 need (若台账里有对应的未闭合 need 就回掉它), 不许删别人的条目** ★

★★**边界 (★越界即无效★)** ★
· ★**不改 `HW/` 下任何文件** (网表 / 脚表 / BOM / 板 / `.kicad_pro` / 原理图 一律不碰) ★
· ★**不改 `MECH/`** (★mech-lead 的 ISS-229 正在改 MECH 侧同名锚点, 地界零交集★) ★
· ★**不碰 PCB 布线 / 布局 / 板框** ★
· ★**不改 `state/issue_log.yaml`** (★status 留给 main 落 verified★) ★
· ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别人的分片** · ★**不发信 / 不联系供应商 / 不下采购单** ★
· ★**实物 [实测] = 0 条** (★板与屏不在本机; 凡是标 [实测] 的, 一律是「本机脚本/本机文件实读」★) ★
"""

BRIEF_232 = """★★**目标 (★内部活·原理图/网表侧·不是 PCB 布线/布局类·不是老板级拍板★)** ★★
★**把「板子 ↔ 网表 焊盘级等价」这道门禁红的 2 处「多余」定位掉, 并给出【网表侧】的逐字修法** ★★
⇒ ★**目标状态: `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ rc=0 (C1 焊盘级等价全过), 且原理图侧四道尺子全绿** ★

★★**为什么是现在 (★main 2026-11-16 06:2x~06:3x 自己实跑, 不是抄交卷报告★)** ★★
· ★**main 实跑 `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ rc=1**, 输出逐字: ★*
  `❌ C1 焊盘级等价 (ref,焊盘号)→网络 — 网表 480 / 板上(带网) 482` ★
  `缺失 0 · 多余 2 · 同号异网 0 · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC 0` ★
  `★多: C_VBUS_GND pad1 = GND` ★
  `★多: C_VBUS_GND pad2 = VBUS_5V_CHG` ★
  ⇒ ★**结论: 板上有这两个焊盘, 但【网表推出的 (器件,焊盘号)→网络 集合】里推不出来 ⇒ 判「多余」** ★
· ★**★命令必须这么跑 (★踩过的坑★)★**: ★**必须走 `bash state/pcbnew_py.sh state/check_pcb_nets.py`** ★
  ⇒ ★**系统 python3.14 没有 pcbnew ⇒ 直接 `python3 state/check_pcb_nets.py` 会 ModuleNotFoundError ⇒ ★**门禁会静默失效**★** ★
  (★`state/daily_check.py` 的 `run_sh()` 就是这么包的★)
· ★**脚表侧其实是对的 (★main 实读★)**: `HW/netlist_v1_pins.csv` L148 `C_VBUS_GND.1,GND,C_VBUS_GND,1,P1,...` · L149 `C_VBUS_GND.2,VBUS_5V_CHG,C_VBUS_GND,2,P1,...` ★
  ⇒ ★**⇒ 脚表已经写明「1 号脚 = GND / 2 号脚 = VBUS_5V_CHG」, 与板上两个焊盘的网名一致 ⇒ ★**板侧与脚表是自洽的** ★
· ★**网表 CSV 侧的两行 (★main 实读 `HW/netlist_v1.csv`, 列序 = page,net,node1,node2,ref,value,type,dnp,…★)** ★:
  · L10 `P1,GND,C_VBUS_GND,GND,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,...`
  · L12 `P1,VBUS_5V_CHG,C_VBUS_GND,C_VBUS_OUT,C_VBUS_GND,[待选型] 100µF,C,DNP,[推算],,...`
  ⇒ ★**两行的节点串都写的是【裸器件名】(`C_VBUS_GND` / `C_VBUS_OUT`), 没有写 `pin<N>`** ★
· ★**门禁自己的规则 (★`state/check_pcb_nets.py` 头部注释「网表 → 焊盘编号规则」, main 实读★)** ★:
  ★**编号脚 (节点串含 `pin<N>`) ⇒ 焊盘号 = 网表真实针号** ★ · ★**命名脚 / 裸端 (节点串是裸器件名) ⇒ 焊盘号 = 按出现顺序的占位号 1..M** ★
  ⇒ ★**⇒ main 的推断 (★你必须自己复现验证, 不许照抄★): C_VBUS_GND 的两行走的是「裸端」分支 ⇒ 网表侧推不出真实焊盘号 ⇒ 板上有、网表没有 ⇒ 判「多余」⇒ 修法在【网表 CSV 的节点串写法】, 不在板** ★
· ★**★这盏灯为什么现在才亮★**: ISS-223 (落表第 2 批) 05:18 重生成过网表 ⇒ ★**网表 md5 从 `13f59a43…` 变成 `3215020b…` ⇒ 这道门禁重新按新网表算了一遍, 才把这 2 处翻出来** ★

★★**你要做的 (★四件交付物, 少一件即无效★)** ★★
① ★**根因定位 (★自己实跑, 不许抄 main 的推断★)** ★
  ⇒ ★**先自己复现**: 用 `HW/netlist_v1.csv` 的副本做实验 (★只在 `/tmp` 副本上改, 真盘先别动★) ⇒ ★**把 C_VBUS_GND 两行的节点串改成编号脚写法 (`C_VBUS_GND pin1` / `C_VBUS_GND pin2` 这类) ⇒ 跑 `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ 看 C1 的「多余」是不是变成 0** ★
  ⇒ ★**如果实验证明不是这个 ⇒ 继续挖, 挖到真因为止 (★比如占位号分配规则 / 裸端去重规则 / DNP 是否计入★)** ★
  ⇒ ★**结论里必须写清: 【是网表侧写法错, 还是板侧错】—— ★**不许含糊** ★
② ★**网表侧逐字修法 (★格式照抄 ISS-230 作业包的口径★)** ★
  ⇒ ★**文件 + 行号 + 旧值 + 新值 (逐字) + 影响面** ★ ⇒ ★**影响面必须包含: 脚表会不会变 / BOM 会不会变 / `state/check_netlist.py` 判据 5 (A 组 20 条) 会不会变 / `--expect-resolved` 的 21 条会不会变 / 板侧要连带改什么 (★只列, 不许自己改板★)** ★
  ⇒ ★**★不许落表任何 V 值 (V-2 / V-3 / V-4 都还在等老板拍)★** ⇒ ★**不许顺手改板** ★
③ ★**机器门禁实跑 (★交卷前最后一件事, 输出原样贴进交接单★)** ★
  · `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ ★**rc=0** ★ (C1 焊盘级等价全过 + C2/C3 全过)
  · `python3 state/check_netlist.py` ⇒ rc=0 · `python3 state/check_netlist_pins.py` ⇒ rc=0 ★
  · `python3 state/check_sch_erc.py` ⇒ rc=0 (★ERC=0★) · `python3 state/check_sch_pinfull.py` ⇒ rc=0 (★584 脚 = 584 脚★)
  · `python3 HW/check_netlist_selfconsistency.py` ⇒ rc=0 · `--selftest` ⇒ rc=0 (★21/21★) ★
  · `python3 state/merge.py && python3 state/gate_check.py` ⇒ rc=0 (★Q1 18/18★)
  ⇒ ★**★反向自证 (★必做★)★**: 拿**网表副本**把改动的两行改回旧写法 ⇒ C1 必须重新红 ⇒ ★**证明「你真修好了等价性, 不是把门禁调没」** ★
④ ★**交接单 + 分片** ★
  · ★**新建 `HANDOFF/2026-11-16_hw-lead_ISS232_板网表焊盘级等价2处多余定位.md`** (★B1~B6 六块齐全★) ★
  · ★**分片** `state/fragments/hw.yaml` ⇒ ★**必须走 `python3 state/frag_write.py` 原子写 (★不许 `open(p,"w")`★)** ★ ⇒ ★**不许删别人的条目** ★

★★**★必须写进交接单的【下游连锁影响】(★main 06:3x 实测到的真冲突, 不写就会有人踩★)** ★★
· ★**你改网表 ⇒ 网表 md5 会再变一次 ⇒ SW 侧 R6 锚点与 MECH 侧 G5b/C21 会【再次】过期** ★
  ⇒ ★**⇒ 你必须在交接单里写清【新旧 md5 + 落表单号 + 影响到的两处台账位置】(★供 SW / MECH 侧走 H-1 重锚★)** ★
  ⇒ ★**★但不许你自己去动 `SW/SW_MD5_BASELINE_LEDGER.md` 与 `MECH/HW_CROSS_REVIEW_TRIAGE.md` (★那分别是 sw-lead / mech-lead 的地界, 且 sw-lead 的 ISS-231 正在并发重锚★)★** ★
  ⇒ ★**⇒ 走 `state/fragments/*.yaml` 登记 need, 把「谁的锚点要跟着重锚」写清楚** ★

★★**边界 (★越界即无效★)** ★
· ★**不许改板** (★`HW/PCB/demo_mainboard.kicad_pcb` / `.kicad_pro` / 布线 / 布局 / 板框 一律不碰★) ⇒ ★**若查出来是板侧的锅 ⇒ 登记 need 给 main, 不许自己动板** ★
· ★**不改 `MECH/`** · ★**不改 `SW/`** (★except 登记 need★) ★
· ★**不改 `state/issue_log.yaml`** (★status 留给 main 落 verified★) · ★**不改 `PROJECT_TRACKER.md` §0** · ★**不写别人的分片** ★
· ★**不发信 / 不联系供应商 / 不下采购单** ★ · ★**实物 [实测] = 0 条** ★
· ★**受保护 md5 交卷前后必须逐字节不变**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · 脚表 `a600afae493f5a7a6c55f46ad35ac89c` · BOM `92b51580867deca9f8b04af88d925d96` ★
"""


def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log["issues"]
    by_id = {i.get("id"): i for i in issues}

    # ---------- 1. ISS-228 → verified ----------
    i228 = by_id["ISS-228"]
    assert i228.get("status") == "fixing", i228.get("status")
    i228["status"] = "verified"
    i228["verify_by"] = "main"
    i228["verify_date"] = TODAY
    i228["verify_result"] = (
        "★main 2026-11-16 06:2x~06:3x 自测验收 (★本轮自己实跑, 不抄交卷报告★)★\n"
        "· 交付物在盘: `HANDOFF/2026-11-16_sw-lead_ISS228_RK3572_GPIO0_VCCIO官方映射自查.md` (53113 B, 06:02, B1~B6 六块齐全) + "
        "`SW/RK3572_GPIO0_VCCIO_DOMAIN_FACTS.md` + `SW/tools/check_rk3572_vccio_domain.py` ★\n"
        "· 门禁 (main 自己跑的): `python3 SW/tools/check_rk3572_vccio_domain.py` ⇒ **rc=0** (C1~C8 全过; 实跑输出: 本板 I2C_A = I2C5_M3 (GPIO3_C4/C1, 球 AH33/AL33) ⇒ Forlinx 官方 SoM 逐脚 VOL = 1.8V; "
        "GPIO0_B0/B1 (球 1K21/U32) ⇒ PMUIO0_VCC1V8 = 1.8V only (abs-max 1.98V) 且这两脚脚本板未引出; B-01/B-02 最终取值 = imp 上拉 2.2k 到 1.8V / level 1.8V) ; "
        "★`--selftest` ⇒ **rc=0, 16/16 全过** (REV-12 抹 D-3 解锁 / REV-13 删 [0数据] 条目 / REV-14 改 covers / REV-15 夸大球位数 / REV-16 抹官方出处 ⇒ 全红) ★\n"
        "· ★**结论要点 (main 实读门禁输出, 不是我转述)**: ★**need 问错了问题** ⇒ ① 本板 I2C_A 走 I2C5_M3 (官方 VOL 1.8V), need 里说的 GPIO0_B0/B1 (球 1K21/U32) **本板 SoM 根本没引出** ⇒ "
        "「3.3V/2.8V 超 abs-max ⇒ 整条 I2C_A 要重设计」的推论链**从根上不成立** ; ② 「VCCIO1_VCC 属 1.8V only (max 1.98V)」**是错的** ⇒ 1.8V only 档只有 PMUIO0_VCC1V8 + VCCIO0_VCC1V8 ⇒ "
        "「VCCIO1_VCC 能上 3.3V (max 3.63V)」才是官方口径 ★\n"
        "· ★**分片真落盘 (main 实查)**: `state/fragments/sw.yaml` (mtime 05:58) ⇒ answer `iss148_rk3572_gpio0_vccio_domain_check` (★回掉了那条逾期 13 天的跨域 need★) + claim + 6 条 need ★\n"
        "· ★**它登记给 hw-lead 的勘误待办 (不归本单)**: `HW/AR0234CS_OPEN_SOURCE_FACTS.md` L241/L474 的 I2C0 提法 + 全文 VCCIO1_VCC 1.8V only 提法 ⇒ ★**已随本轮新开 ISS-232 派给 hw-lead** ★\n"
        "· ★**不在本单账上的红 (★按设计, 不是本单造成的★)**: `python3 SW/tools/check_demo_panel_spec.py` ⇒ rc=1 (唯一红项 R6 = 锚点过期, 根因 ISS-223 落表) + `--selftest` ⇒ rc=1 (15/16, 基线红) ⇒ ★**本轮新开 ISS-231 (sw-lead) 走 H-1 重锚收口** ★"
    )
    i228["note"] = (i228.get("note") or "") + (
        "\n2026-11-16 06:40 (cron 775d9893 继续执行后继计划) ★main 独立实测验收 ⇒ 落 verified★ "
        "⇒ ★放掉 sw-lead 名额 ⇒ 同轮新开 ISS-231 派出★"
    )

    # ---------- 2. ISS-230 → verified ----------
    i230 = by_id["ISS-230"]
    assert i230.get("status") == "fixing", i230.get("status")
    i230["status"] = "verified"
    i230["verify_by"] = "main"
    i230["verify_date"] = TODAY
    i230["verify_result"] = (
        "★main 2026-11-16 06:2x~06:3x 自测验收 (★本轮自己实跑, 不抄交卷报告★)★\n"
        "· 交付物在盘: `HANDOFF/2026-11-16_hw-lead_ISS230_第3批作业包v2与加强断言.md` (28328 B, 06:10, B1~B6 六块齐全) + "
        "`HW/SCHEMATIC_LANDING_BATCH3_WORKPACKET_V2.md` (落点 = 作业包 §2/§3/§4) + `HW/check_chg_spec7_vs_netlist.py` + `HW/check_netlist_selfconsistency.py` 的 F-3 加强断言 ★\n"
        "· 门禁 (main 自己跑的): `python3 HW/check_netlist_selfconsistency.py` ⇒ **rc=0** (现状守卫 + 作业包 28 条 8 栏齐 + 三方对齐全过) ; "
        "★`--selftest` ⇒ **rc=0, 21/21 全过** (★含 ISS-230 新增的用例19 (清空 A-01 的 z_diff ⇒ 红) + 用例20 (把差分阻抗塞回 A-13 的 imp ⇒ 红)★) ★ ; "
        "★`--expect-resolved` ⇒ **rc=1** (★**预期**: 21 条未落表 = R2×11 + R3×4 + R4×2 + R7×1 + R8×1 + R9×1 + R10×1 ⇒ ★**卡的是老板拍 V-2/V-3/V-4, 不是技术障碍**★) ★ ; "
        "`python3 HW/check_chg_spec7_vs_netlist.py` ⇒ **rc=0** (★§7 CSV 合法性已修 + 双向差集已清单化★) ; "
        "`python3 state/check_netlist.py` ⇒ rc=0 ; `python3 state/check_netlist_pins.py` ⇒ rc=0 ; `python3 state/check_sch_erc.py` ⇒ rc=0 (ERC=0) ; "
        "`python3 state/check_sch_pinfull.py` ⇒ rc=0 (图上 584 脚 / 表里 584 脚, K=0, 218 器件 / 153 网) ★\n"
        "· ★**受保护 md5 交卷前后逐字节不变 (main 实测)**: 板 `611b869e13518c3c023fb178f91a0075` ✓ · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ✓ · "
        "脚表 `a600afae493f5a7a6c55f46ad35ac89c` ✓ · BOM `92b51580867deca9f8b04af88d925d96` ✓ · 网表 `3215020b6d4120e1b7728227effdc6d3` (★= ISS-223 落表后的值, 本单没再改★) ★\n"
        "· ★**分片真落盘 (main 实查)**: `state/fragments/hw.yaml` (mtime 06:11) ⇒ artifact `HW/SCHEMATIC_LANDING_BATCH3_WORKPACKET_V2.md` + claim `iss230_batch3_landing_map_v2` + "
        "claim `iss230_a_group_field_discipline_assertion` + claim `iss230_v2_netlist_side_turns_zero_green` + claim `iss230_chg_spec7_csv_legal_and_diff_listed` + 4 条 need (含 `iss230_row_shift_false_green` / `iss230_v2_netlist_side_turns_zero_green` / `iss230_chg_spec7_reconcile_deferred` / `iss230_skin_temp_void_marked`) ★\n"
        "· ★**交卷报告里 3 条要 main 看的实测结论 (main 已复核, 认)★**: ① 任务书「4 条 = R4/R9 = V-2」算术差 1 ⇒ 实测 R4×2 + R9×1 = 3 条 (4 条是 R3) ⇒ 13+3+1+4=21 ✓ ; "
        "② ★**V-2 的网表侧落表一条判据都转不绿 (实测 7→7)** ⇒ R4/R9 读的是 `.kicad_pcb` ⇒ V-2 必须写成【网表侧落表 + 板侧那一趟】两段 ★ ; "
        "③ ★**行号漂移会造假绿** ⇒ 落表那趟必须逐条改行号 ★ ⇒ ★**这三条正是本轮新开 ISS-232 要接着处理的** ★\n"
        "· ★**板侧 8 项 (B-1~B-8) 继续排队** (★老板 11-11 10:07 口径: PCB 类不派★) ⇒ ★**但本轮新开 ISS-232 抓到板↔网表不等价的 2 处 (C_VBUS_GND), 那是网表侧写法问题, 不是布线问题** ★"
    )
    i230["note"] = (i230.get("note") or "") + (
        "\n2026-11-16 06:40 (cron 775d9893 继续执行后继计划) ★main 独立实测验收 ⇒ 落 verified★ "
        "⇒ ★放掉 hw-lead 名额 ⇒ 同轮新开 ISS-232 派出★"
    )

    # ---------- 3. ISS-229: 会话被超时杀掉 ⇒ 不落账, 同单续做 ----------
    i229 = by_id["ISS-229"]
    assert i229.get("status") == "fixing", i229.get("status")
    i229["note"] = (i229.get("note") or "") + (
        "\n2026-11-16 06:40 (cron 775d9893 继续执行后继计划) ★**子会话被超时杀掉 ⇒ 本单不落账, 同单续做** ★\n"
        "· ★**子会话实况 (main 实读 sessions_list)**: `agent:mech-lead:subagent:07d81b89-dcb1-4c86-b37a-a6c3e8216f0d` ★**status=timeout · abortedLastRun=true · endedAt 06:16:15 · runtimeMs=1158643** ★\n"
        "· ★**已落盘 (main 实测 mtime/大小)**: `MECH/hinge_power_calc.py` (06:09, 22417 B) · `MECH/hinge_power_calc.json` (06:10, 49972 B) · `MECH/HINGE_POWER_CALC.md` (06:13, 40569 B) "
        "⇒ ★**交付物 ①② 已落** (★main 实读 py L46~L49: `ICHG_FACTOR_VBAT_370 = 1.216` / `ICHG_FACTOR_VBAT_420 = 1.071` / `ICHG_FACTOR = 1.216` / `ICHG_FACTOR_VOID_LEGACY = 0.822` 只留痕不参与计算★) ★\n"
        "· ★**未落 (main 实测)**: ③ 交接单 `HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md` ★**不存在** ★ ; "
        "④ 分片 `state/fragments/mech.yaml` mtime 仍是 **05:27** (= 上一单 ISS-227 的时刻) ⇒ ★**本单一条分片都没写** ★ ; "
        "⑤ 同型旧数清理 `MECH/FPC_FAB_NOTES.md` mtime 仍是 **11-12 03:35** ⇒ 未改 ★ ; "
        "⑥ MECH 闸重锚未做 (★`python3 MECH/check_demo_struct_truth.py` 仍 **rc=2, 21/23, FAIL 2 组 = G5b + C21**★) ★\n"
        "· ★**会话死在哪一步 (main 实读该会话 transcript 的最后一条助手文本)★**: 「Now let me fix the same-class stale numbers in `MECH/FPC_FAB_NOTES.md` (same MECH domain, same root cause — leaving it would create a contradictory doc set):」 ⇒ ★**死在 ⑤** ★\n"
        "· ★**续做要点 (main 06:3x 实测)★**: ★**已完成 ①② ⇒ 续做只补 ③④⑤⑥, 不许重做 ①② (★重做会覆盖已落盘的正确数★)** ★; "
        "★**⑥ 的重锚按 ISS-224 的 H-1 流程**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` §1 `MECH_ANCHORS.source_ledger.entries[]` 里 `HW/netlist_v1.csv` 那一条 ⇒ md5 / prev_md5 / by / landed_at 四项 + §3.1「已修复 (留痕)」加一行 ★ "
        "★**⚠️ 并发警告 (main 实测到的真冲突)★**: hw-lead 的 ISS-232 在飞 (要改网表节点串 ⇒ 网表 md5 可能再变) ⇒ ★**重锚用的 md5 必须是交卷那一刻的盘上实测值, 且必须能在落表台账里查到** ★"
    )

    # ---------- 4. 新开 ISS-231 (sw-lead) ----------
    assert "ISS-231" not in by_id, "ISS-231 已存在"
    issues.append({
        "id": "ISS-231",
        "title": "★★[主线内·软件/门禁侧·内部活] SW 侧 R6 锚点重锚 (★ISS-223 落表后【按设计】变红的一盏灯, 走 ISS-225 台账 H-1 流程★) ⇒ 收口 `check_demo_panel_spec.py` 的 rc=1 (基线红 ⇒ selftest 只有 15/16)",
        "severity": "high",
        "source_blocker": "ISS-223",
        "desc": "★**main 2026-11-16 06:2x~06:3x 实跑 (不是抄交卷报告)**:\n"
                "· `python3 SW/tools/check_demo_panel_spec.py` ⇒ **rc=1**, 唯一红项 = R6: ★**盘上真源 `HW/netlist_v1.csv` md5 = `3215020b6d4120e1b7728227effdc6d3` ≠ 锚点登记 `13f59a43dbd35dc6cb16e897c8c891ab`** ★ (真源被换了或锚点过期)\n"
                "· `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ **rc=1 (15/16)** ⇒ ★**基线红 ⇒ 第 16 条正好是基线那盏灯, 只能过 15 条** ★\n"
                "· ★**根因 = 上游合法落表 (★不是门禁坏了★)**: 现值 `3215020b…` 是 ISS-223 (落表第 2 批, 05:18) 改的 ⇒ SW 侧锚点还钉在 ISS-220 (第 1 批) 的 `13f59a43…` ★\n"
                "· ★**处置流程项目里早写好了**: `SW/SW_MD5_BASELINE_LEDGER.md` §4 **H-1** (四步重锚) + **H-4** (逐字写「ISS-223 落表后 ⇒ R6 会自动红 (★这是设计★) ⇒ main 派 sw-lead 重锚 (走 H-1)」) ★\n"
                "· ★**脚表不用动 (main 实测)**: `HW/netlist_v1_pins.csv` md5 = `a600afae493f5a7a6c55f46ad35ac89c` ⇒ 与台账锚点 entries[1] 一致 ⇒ 只改网表那一条 ★\n"
                "· ★**本单 = 内部活 · 零外发 · 只改台账锚点 3 个字段 + 1 行留痕 · 判据语义一个字不许动** ★",
        "owner": "sw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-16 06:40 (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮自己实跑 `check_demo_panel_spec.py` (rc=1, 唯一红项 R6) + `--selftest` (rc=1, 15/16) + 自己 md5sum 三个真源文件 + 自己读台账 H-1/H-4** ★\n"
                "★**sw-lead 名额的上一条 ISS-228 本轮 06:40 落 verified (main 实跑: 新闸 rc=0 + selftest 16/16 + 交接单 53113 B 在盘 + 分片含 answer) ⇒ 名额空出来 ⇒ 本单接档** ★\n"
                "★**边界**: 不改 `HW/` 任何文件 · 不改 `MECH/` (mech-lead 的 ISS-229 正在改 MECH 侧同名锚点, 地界零交集) · 不碰 PCB 布线布局 · 不改 R6/R7 判据语义 · 不写别人分片 · 不发信 · 不自签 issue_log ★\n"
                "★**并发提醒**: hw-lead 的 ISS-232 在飞 (要改网表节点串 ⇒ md5 可能再变) ⇒ ★**重锚的 md5 必须取交卷那一刻的盘上实测值, 且必须能在落表台账里查到** ★",
        "task_brief": BRIEF_231,
        "dispatched_at": None,
    })

    # ---------- 5. 新开 ISS-232 (hw-lead) ----------
    assert "ISS-232" not in by_id, "ISS-232 已存在"
    issues.append({
        "id": "ISS-232",
        "title": "★★[主线内·原理图/网表侧·内部活] 板↔网表【焊盘级等价】门禁红的 2 处「多余」(C_VBUS_GND pad1=GND / pad2=VBUS_5V_CHG) ⇒ 定位根因 + 给网表侧逐字修法 (★板侧不许碰★)",
        "severity": "high",
        "source_blocker": "ISS-223",
        "desc": "★**main 2026-11-16 06:2x~06:3x 实跑 (不是抄交卷报告)**:\n"
                "· `bash state/pcbnew_py.sh state/check_pcb_nets.py` ⇒ **rc=1**: ★**C1 焊盘级等价: 网表 480 / 板上(带网) 482 · 缺失 0 · 多余 2 · 同号异网 0 · NC 焊盘 351 · 非法 NC 0** ★ ⇒ "
                "★**★多: `C_VBUS_GND pad1 = GND` / `C_VBUS_GND pad2 = VBUS_5V_CHG`** ★ ⇒ ★**板上有这两个焊盘, 网表推不出 ⇒ 板子与网表不等价 ⇒ 不许投板** ★\n"
                "· ★**脚表侧是对的 (main 实读)**: `HW/netlist_v1_pins.csv` L148/L149 ⇒ `C_VBUS_GND.1` = GND · `C_VBUS_GND.2` = VBUS_5V_CHG ⇒ ★**与板上两焊盘的网名一致 ⇒ 板侧与脚表自洽** ★\n"
                "· ★**网表 CSV 侧两行 (main 实读 `HW/netlist_v1.csv` L10/L12)**: 节点串写的是【裸器件名】(`C_VBUS_GND` / `C_VBUS_OUT`), ★**没有写 `pin<N>`** ★ ⇒ "
                "★**按门禁自己的规则 (裸端 ⇒ 焊盘号 = 按出现顺序的占位号; 编号脚 ⇒ 焊盘号 = 网表真实针号) ⇒ 网表侧进不了「真实针号」分支 ⇒ 判「多余」** ★ ⇒ ★**疑似修法在网表 CSV 侧, 不在板** ★\n"
                "· ★**这盏灯是 ISS-223 落表后重新按新网表算才翻出来的** ★ ⇒ ★**本单 = 内部活 · 零外发 · 板侧不许碰 · 不许落表任何 V 值** ★",
        "owner": "hw-lead",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-19",
        "status": "open",
        "external": False,
        "need_keys": [],
        "fix_ref": None,
        "verify_by": "main",
        "verify_result": None,
        "verify_date": None,
        "note": "2026-11-16 06:40 (cron 775d9893 继续执行后继计划) 新开 ★**依据 = main 本轮自己实跑 `check_pcb_nets.py` (rc=1, C1 网表 480 / 板上 482, 多余 2) + 自己读网表 L10/L12 + 自己读脚表 L148/L149 + 自己读门禁脚本的「网表→焊盘编号规则」** ★\n"
                "★**hw-lead 名额的上一条 ISS-230 本轮 06:40 落 verified (main 实跑: 现状守卫 rc=0 + selftest 21/21 + expect-resolved rc=1(21 条, 预期) + check_chg_spec7 rc=0 + 交接单 28328 B 在盘 + 分片真落盘) ⇒ 名额空出来 ⇒ 本单接档** ★\n"
                "★**边界**: 不改板 (`.kicad_pcb` / `.kicad_pro` / 布线 / 布局 / 板框 一律不碰 ⇒ 若是板侧的锅, 登记 need 给 main) · 不改 `MECH/` · 不改 `SW/` (except 登记 need) · 不落表 V-2/V-3/V-4 的值 · 不写别人分片 · 不发信 · 不自签 issue_log ★\n"
                "★**顺带收 ISS-228 (sw-lead) 登记给 hw-lead 的勘误**: `HW/AR0234CS_OPEN_SOURCE_FACTS.md` L241/L474 的 I2C0 提法 + 全文 VCCIO1_VCC 1.8V only 提法 (★ISS-228 已用 Forlinx 官方手册 + RK3572 datasheet §2.6 三重交叉验证证伪★) ★\n"
                "★**并发提醒**: sw-lead 的 ISS-231 同时在飞 (重锚 SW 侧 R6) ⇒ ★**改网表会让 SW / MECH 侧锚点再过期一次 ⇒ 交接单必须写清新旧 md5 + 单号 (供 H-1 重锚), 但不许自己动 SW / MECH 台账** ★",
        "task_brief": BRIEF_232,
        "dispatched_at": None,
    })

    # ---------- 写回 ----------
    shutil.copy2(LOG, LOG + ".bak_20261116_0640_verify228_230_open231_232")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print("OK: ISS-228 → verified / ISS-230 → verified / ISS-229 续做(不落账) / ISS-231 新开 (owner=sw-lead) / ISS-232 新开 (owner=hw-lead)")
    print("issues total:", len(log["issues"]))


if __name__ == "__main__":
    main()
