#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_0450_verify_270_271_redispatch_269.py
★main (moli) 落账 · 2026-11-17 04:5x (cron 775d9893 「ARS45 继续执行后继计划」)★

★★**本轮做三件事 (★全部本机实跑, 不抄任何交卷报告的自述★)** ★★
★**① ISS-270 (sw-lead) 落 `verified`** —— ★**独立复验通过** ★
★**② ISS-271 (mech-lead) 落 `verified`** —— ★**独立复验通过** ★
★**③ ISS-269 (hw-lead) = 僵尸 fixing ⇒ 重派** ★ (★会话 compaction 后死, 零交卷物★)

★★**为什么 A 段 internal 段是空的 (★main 04:4x 本机实跑, 不是推测★)** ★★
· ★**`python3 state/advance.py --json` ⇒ `internal: []` · `approvals: []` · `decisions: 40` · `waiting: []`** ★
· ★**根因 = 三个总工名额全被 `fixing` 占着** (★advance.py 的 in_flight 规则: ★**该 agent 名下已有 fixing 的 issue ⇒ 本轮不再给它派新活**★):
  · ★**hw-lead** = ISS-269 (fixing) · ★**sw-lead** = ISS-270 (fixing) · ★**mech-lead** = ISS-271 (fixing) ★
· ⇒ ★**但 main 逐条实测三个会话的盘上实物后, 发现三条的真相各不相同** ★★

★★**三条的实测真相 (★main 04:4x 本机实跑★)** ★★
· ★**ISS-270 (sw-lead) = 真交卷** ★ ⇒ ★**交卷物在盘**: `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` (54,112 B · 04:34) +
  `HANDOFF/2026-11-17_sw-lead_ISS270_SW侧外部依赖自查.md` (37,061 B · 04:35) + `state/fragments/sw.yaml` (★`grep -c iss270` = **3** ★) ★
  ⇒ ★**main 独立复验**: ① §0 判定口径 + §1 主表 + §2 逐条 + §3 顺带清单 + §4 命令清单 + §5 汇总 + §6 复现命令 **七个主节全在** ★
  ② ★**交卷单自己声称的「5 条挂账里 0 条是真·外部依赖」在盘上可查** (★§1.1 主表小结 + §1 表体 5 行逐条有「自己查了什么 / 结论 / 证据等级 / 降级方案」四栏★) ★
  ③ ★**E-3 的实测突破在盘**: 权重 `35,891,401 B` / sha256 `a39c8476…` / 8.62 MB/s / 4 s 下完 (★`[实测]` 级★) ⇒ ★**「卡在 3.48MB 需内网镜像」这个阻塞前提已消失** ★
  ④ ★**分片 4 处追加式订正在盘** (★`grep -c "等原厂\|等外部\|待外部确认" state/fragments/sw.yaml` = **4** · ★**每一处同一行末尾/下一行都跟着「〔★2026-11-17 ISS-270 自查订正★〕」块** · ★**本单自己写入的文本一条命中都不产生** ★)
  ⑤ ★**5 条挂账的路由改对了**: ★**E-4 `ars45_art_galaxy_sdk` (waiting_on vendor ⇒ agent) 与 E-3 姊妹条 `model_toolchain_q9_addendum` (waiting_on boss ⇒ agent) 撤掉挂账形态** ⇒ ★**老板清单因此从 41 → 40** (★main 04:5x 实测: ★**把这两条路由回滚后 advance.py 立刻回到 41 条** ⇒ ★**证明这 1 条的减少正是 ISS-270 的两条路由改动, 不是别的单偷走的★) ★
     ⇒ ★**且老板那一拍没丢**: ★**`model_license_stack_decision` (waiting_on=**boss**) 仍在清单上** ⇒ ★**「三条路给一句话结论」仍然在老板手上, sw-lead 不代拍** ★
  ⑥ ★**受保护 5 件 md5 逐字节不变 (main 04:4x 实测)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `e06c1dd633566aa44732762c2ff99d1c` ·
     脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ ★**零写板 · 零落表成立** ★
  ⑦ ★**门禁实跑**: `python3 state/merge.py` ⇒ **rc=0** (★产出 410 · 阻塞 43 · 未闭合需求 243 · **冲突 0**★) ·
     `python3 state/gate_check.py` ⇒ **rc=0** (★**【Q1 交付齐备率】18/18** · 【Q2 证据分级率】3/3 · **【Q6 硬件真源闸】✅ 通过**★) ★
· ★**ISS-271 (mech-lead) = 真交卷** ★ ⇒ ★**交卷物在盘**: `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` (42,686 B · 04:25) +
  `MECH/board_port_opening_s6_check.py` (32,351 B · 04:23) + `HANDOFF/2026-11-17_mech-lead_ISS271_板侧开口S6认领与LED位置约束.md` (54,444 B · 04:29) +
  `state/fragments/mech.yaml` (★`grep -c iss271` = **7** ★) ★
  ⇒ ★**main 独立复验**: ① ★**脚本实跑 `--selftest` ⇒ rc=0 (5 用例全过, 含反向用例「脚数 2×5 vs 1×4 必须给出不同的 jd_x0 上界 (51.090 vs 51.725)」)** ★
  ② ★**脚本实跑 `--json` ⇒ rc=0** (★输出里 `jd_x0=50.5` / `jd_y0=9.5` / `content_w=7.62` / `content_h=2.54` / `pad_y1=10.77` / `body_y1=11.405` / `open_x1=59.41` —— ★**与规格页 §2 的原始 JSON 片段逐字一致** ★) ★
  ③ ★**板框三套判定在盘且与机器输出一致**: 160×100 台架板 = **不能开** (内腔 4.10 < 4.50 · V −68.00 · L −85.50) · 60×30 套A = **能开** (V 最坏 **+1.40**) · 60×15 = **不能开** (★套A 孔心 Y=15.00 = 板边 ⇒ P-5 判据无基准★) ★
  ④ ★**`D_LED_G` 走线 93.49mm 独立复算对得上**: 交卷单写 93.4927 ⇒ ★**main 自己按 `R_LED_G.2`@7.5,62.6 ↔ `D_LED_G.1`@100.8,56.6 复算 = 93.4927** ⇒ ★**口径一致** ★
  ⑤ ★**受保护 8 件 md5 逐字节不变 (main 04:4x 实测)**: 板 `611b869e…` · 网表 `e06c1dd6…` · 脚表 `287e7861…` · BOM `94642d07…` · `.kicad_pro` `3e504d2b…` ·
     `MECH/service_port_check.py` `db58ff6a2afc28b8bf517e3c57c56bc1` · `MECH/check_demo_struct_truth.py` `4ae5827e986f1aebb108c5aa2a475074` ·
     `MECH/cavity_recalc_check.py` `c4bf9151dd59826fb2320c34e8afbd0f` ⇒ ★**零写板 · 零落表 · 零改阈值** ★
· ★**ISS-269 (hw-lead) = 僵尸 fixing (★不是真在飞★)** ★ ⇒ ★**会话 `agent:hw-lead:subagent:534e93ad-3f0b-4ed6-95d2-4b5e996234b9` 实测 status=**done** · abortedLastRun=false · 最后一条消息是【Compaction】系统消息 (★不是交卷报告★)** ★
  ⇒ ★**零交卷物 (main 04:4x 实测)**: ★**`HANDOFF/` 下无任何 ISS-269 文件** · ★**`grep -c iss269 state/fragments/hw.yaml` = 0** ·
     ★**`state/gen_pcb_netlist_board.py` mtime 仍是 11-08 21:11 (★生成器一个字没改★)** · ★**`grep -c "DNP\|dnp" state/gen_pcb_netlist_board.py` = 0 (★X-4 没修★)** ·
     ★**`:591` 仍是 `PCB_LAYERS` 默认 6 (★X-3 没修★)** · ★**磁盘上无 `HW/check_pcb_generator_defaults.py` (★机器闸没建★)** ★
  ⇒ ★**⇒ 它占着 hw-lead 的唯一名额, 却没人干活** ⇒ ★**本轮重派 (★taskName=advance_iss269 · runTimeout 5400s 绕开默认 8 分钟超时★)** ★
  ⇒ ★**不新建单 (★ISS-269 的任务书已在盘 + issue_log 里 task_brief 全文都在★) ⇒ 只重派, 状态保持 `fixing` (★本来就是 fixing, 不重复标★)** ★

★★**本轮共同边界 (★写死★)** ★★
零外发 (★老板 2026-11-12 02:02「不再发信, 全靠自己查资料」★) · 零采购 · 零写板 · 零落表 · 零改网表/脚表/BOM ·
零改判据脚本阈值 · 不写任何 agent 的分片 (★只读它们的 grep 计数作证据★) · 不改 `PROJECT_TRACKER.md` §0 ·
不改 `state/issue_log.yaml` 之外的真值文件 (★只写它 + dispatch_log★) · **不替老板拍板** (★A1/A2/A3 + W-1/W-2/W-4 + P7 + G-5 一个值都不落★) ★
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"

VERIFY_270 = (
    "★main 2026-11-17 04:4x 独立复验 (★本机实跑, 不采信自述★) ★\n"
    "· ★**交卷物在盘**: `SW/EXTERNAL_DEPENDENCY_SELFCHECK.md` (54,112 B · 04:34) · "
    "`HANDOFF/2026-11-17_sw-lead_ISS270_SW侧外部依赖自查.md` (37,061 B · 04:35) · "
    "`state/fragments/sw.yaml` (★`grep -c iss270` = 3★) ★\n"
    "· ★**文档结构完整**: §0 判定口径 + §0.1 证据等级 (固定五级) + §1 主表 (5 条 + 顺带清单) + §1.1 小结 + "
    "§2 逐条展开 (E-1/E-2/E-3/E-4/E-5 五节全在) + §3 顺带清单 (S-1~S-28) + §4 板到手即跑命令清单 + §5 汇总 + §6 复现命令 ★\n"
    "· ★**核心结论可查**: §1.1 主表小结原文「5 条挂账里 0 条是真·外部依赖」; ★**§1 表体每条都带「自己查了什么 / 结论 / 证据等级 / 降级方案 (必须项)」四栏** ★\n"
    "· ★**E-3 的实测突破在盘 (★本轮唯一改变老板那条拍板前提的事实★)**: 权重实测下载成功 ⇒ **http=200 · 35,891,401 B · 8.62 MB/s · 4 s 下完** · "
    "sha256 `a39c8476d10c242298d6a8654cb29937a9cc3c062358f4d96367689df23d1796` · md5 `9f29ae623a0d9b0263b24cdba02e98d5` ⇒ "
    "★**「卡在 3.48MB / 需内网镜像或公司代理」这个阻塞前提已不存在** ★ (★`[实测]` 级·不是 [推算]★) ★\n"
    "· ★**分片 4 处追加式订正在盘且口径正确**: `grep -c \"等原厂\\|等外部\\|待外部确认\" state/fragments/sw.yaml` = **4** ⇒ "
    "★**四处每一处同一行末尾/下一行都跟着「〔★2026-11-17 ISS-270 自查订正★〕」块 · 本单自己写入的文本一条命中都不产生** ★ (★追加式 · 老字一字未删★) ★\n"
    "· ★**路由改对了 ⇒ 老板清单 41 → 40 (★main 04:5x 实测证明, 不是猜★)**: 把 E-4 `ars45_art_galaxy_sdk` (waiting_on vendor ⇒ agent) 与 "
    "E-3 姊妹条 `model_toolchain_q9_addendum` (waiting_on boss ⇒ agent) 两条路由**回滚**后 `advance.py` 立刻回到 **41 条** ⇒ "
    "★**证明这 1 条的减少正是本单的路由改动, 不是别的单偷走的** ★ ⇒ ★**且老板那一拍没丢**: "
    "`model_license_stack_decision` (waiting_on=**boss**) 仍在清单上 ⇒ ★**「三条路给一句话结论」仍在老板手上, sw-lead 不代拍** ★\n"
    "· ★**受保护 5 件 md5 逐字节不变 (main 04:4x 实测)**: 板 `611b869e13518c3c023fb178f91a0075` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · "
    "脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ⇒ "
    "★**零写板 · 零落表成立** ★\n"
    "· ★**门禁实跑**: `python3 state/merge.py` ⇒ **rc=0** (★产出 410 · 阻塞 43 · 未闭合需求 243 · **冲突 0**·健康度 red★) · "
    "`python3 state/gate_check.py` ⇒ **rc=0** (★**【Q1 交付齐备率】18/18** · 【Q2 证据分级率】3/3 · **【Q6 硬件真源闸】✅ 通过**★) ★\n"
    "· ★**边界自证 (★交卷单自己声明的, main 逐条对照盘上实物★)**: 零外发 (★只做公开 GET + web_search★) · 零写板 · 零落表 · "
    "零改既有 SW 文档的既有结论 · 零采购 · 只写 `state/fragments/sw.yaml` (走 `frag_write.py` 原子写) · 未碰 HW/MECH/板/判据阈值 ★"
)

VERIFY_271 = (
    "★main 2026-11-17 04:4x 独立复验 (★本机实跑, 不采信自述★) ★\n"
    "· ★**交卷物在盘**: `MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md` (42,686 B · 04:25) · `MECH/board_port_opening_s6_check.py` (32,351 B · 04:23) · "
    "`HANDOFF/2026-11-17_mech-lead_ISS271_板侧开口S6认领与LED位置约束.md` (54,444 B · 04:29) · "
    "`state/fragments/mech.yaml` (★`grep -c iss271` = 7★) ★\n"
    "· ★**脚本实跑 `--selftest` ⇒ rc=0** (★5 用例全过 · 含反向用例「脚数 2×5 vs 1×4 必须给出不同的 jd_x0 上界 (51.090 vs 51.725)」⇒ 公式对 content_w 敏感★) ★\n"
    "· ★**脚本实跑 `--json` ⇒ rc=0** (★输出 `jd_x0=50.5` / `jd_y0=9.5` / `content_w=7.62` / `content_h=2.54` / `pad_y1=10.77` / "
    "`body_y1=11.405` / `open_x1=59.41` ⇒ ★**与规格页 §2 的原始 JSON 片段逐字一致** ★) ★\n"
    "· ★**板框三套判定在盘且与机器输出一致**: 160×100 台架板 = **不能开** (盖板内腔 4.10 < 4.50 · V 链 −68.00 · L 链 −85.50 三处判红) · "
    "60×30 套A = **能开** (H/V/L 三链全绿 · V 最坏 **+1.40**) · 60×15 = **不能开** (★几何绿但套A 孔心 Y=15.00 = 板边 ⇒ 开口 Y 的 P-5 判据无基准★) ★\n"
    "· ★**`D_LED_G` 走线 93.49mm 独立复算对得上**: 交卷单写 **93.4927** ⇒ ★**main 自己按 `R_LED_G.2`@7.5,62.6 ↔ `D_LED_G.1`@100.8,56.6 复算 = 93.4927** ⇒ 口径一致 ★\n"
    "· ★**`D_LED_G` 结构侧零规定 ⇒ 结论成立**: `D_LED_G` 在 MECH 域只 1 命中且是 ISS-267 自己引述作业包那行 · 「指示灯」/「状态灯」0 命中 · 打印包 Rev B 零 LED 窗口特征 ⇒ "
    "★**域内查无此规定** (★交卷单诚实标注: 这是「域内查无」不是「宇宙里没有」★) ★\n"
    "· ★**受保护 8 件 md5 逐字节不变 (main 04:4x 实测)**: 板 `611b869e…` · 网表 `e06c1dd6…` · 脚表 `287e7861…` · BOM `94642d07…` · `.kicad_pro` `3e504d2b…` · "
    "`MECH/service_port_check.py` `db58ff6a2afc28b8bf517e3c57c56bc1` · `MECH/check_demo_struct_truth.py` `4ae5827e986f1aebb108c5aa2a475074` · "
    "`MECH/cavity_recalc_check.py` `c4bf9151dd59826fb2320c34e8afbd0f` ⇒ ★**零写板 · 零落表 · 零改阈值** ★\n"
    "· ★**门禁实跑**: `python3 state/merge.py` ⇒ **rc=0** (冲突 0) · `python3 state/gate_check.py` ⇒ **rc=0** (★Q1 18/18 · Q6 ✅★) ★\n"
    "· ★**本单自发现的隐藏前置 (★已登记, 不代拍★)**: ★**`D_LED_G` 亮度档 G-5 未拍** (★1 kΩ + 3.3 V ⇒ 1.10 mA ⇒ 绿光 `KP-2012SGC` 仅 0.7~0.9 mcd ⇒ 白天看不见★) "
    "⇒ ★**一改就改串阻 ⇒ 改网表 ⇒ 改 BOM ⇒ 改板面落位 ⇒ 若排在 S6 之后, 板要再改一次 ⇒ 「板只改一次」破** ★ ⇒ "
    "★**建议 main 把 G-5 排进 S6 前置** (★该条已在决策页 §A-补4 W-6 / P6 上, 本单只是把「排在 S6 之前」这个顺序要求写实★) ★"
)

NOTE_269 = (
    "\n★**2026-11-17 04:5x (cron 775d9893 继续执行后继计划) · main 实测本单是【僵尸 fixing】⇒ 本轮重派** ★\n"
    "★**实测**: 会话 `agent:hw-lead:subagent:534e93ad-3f0b-4ed6-95d2-4b5e996234b9` status=**done** · abortedLastRun=false · "
    "★**最后一条消息是【Compaction】系统消息, 不是交卷报告** ★ ⇒ ★**零交卷物**: `HANDOFF/` 下无任何 ISS-269 文件 · "
    "`grep -c iss269 state/fragments/hw.yaml` = **0** · `state/gen_pcb_netlist_board.py` mtime 仍是 **11-08 21:11** (★一个字没改★) · "
    "`grep -c \"DNP\\|dnp\" state/gen_pcb_netlist_board.py` = **0** (★X-4 没修★) · `:591` 仍是 `PCB_LAYERS` 默认 **6** (★X-3 没修★) · "
    "磁盘上无 `HW/check_pcb_generator_defaults.py` (★机器闸没建★) ★\n"
    "★**⇒ 它占着 hw-lead 的唯一名额却没人干活** ⇒ ★**本轮重派** (★taskName=`advance_iss269` · runTimeout **5400s** 绕开默认 8 分钟超时★) ★\n"
    "★**不新建单**: 任务书 `state/dispatch_briefs/ISS-269_hw_gen_three_landmines.md` (10,682 B) 与 issue_log 里的 task_brief 全文都在 ⇒ "
    "★**只重派, status 保持 `fixing` (★本来就是 fixing, 不重复标★)** ★\n"
    "★**重派时的三条硬纪律 (★main 追加, 因为上一轮就死在这三处★)**: ① ★**先写盘再补自证输出** (★上一轮死在「先验证后写盘」★) ★ "
    "② ★**不许整文件读大文件** (★`gen_pcb_netlist_board.py` 68KB · 只读病灶行段 ★`:575~:595`★) ★ "
    "③ ★**沙盒复现必须用 `PCB_OUT=/tmp/...`, 不许写盘上板** ★"
)


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main():
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") or []
    by_id = {it.get("id"): it for it in issues}

    # ---------------- ISS-270: 落 verified ----------------
    it270 = by_id["ISS-270"]
    assert it270.get("status") == "fixing", "ISS-270 状态不是 fixing (实际 %s)" % it270.get("status")
    it270["status"] = "verified"
    it270["verify_by"] = "main"
    it270["verify_date"] = TODAY
    it270["verify_result"] = VERIFY_270
    it270["fix_ref"] = (
        "SW/EXTERNAL_DEPENDENCY_SELFCHECK.md (54,112 B) · "
        "HANDOFF/2026-11-17_sw-lead_ISS270_SW侧外部依赖自查.md (37,061 B) · "
        "state/fragments/sw.yaml (frag_write.py 原子写 · grep -c iss270 = 3)"
    )
    it270["note"] = (it270.get("note") or "") + (
        "\n★**2026-11-17 04:5x (cron 775d9893 继续执行后继计划) · main 独立复验后落 verified** ★ "
        "(★实测: 交卷物在盘 · 文档七节齐全 · E-3 权重实测 35,891,401 B / sha256 a39c8476… · "
        "分片 4 处追加式订正 · merge rc=0 · gate_check rc=0 Q1 18/18 · "
        "受保护 5 件 md5 逐字节未变 611b869e/e06c1dd6/287e7861/94642d07/3e504d2b★) "
        "★**⇒ 老板清单 41 → 40 (本单两条路由改动; 回滚即回 41, 已实测) · sw-lead 名额由此释放** ★"
    )

    # ---------------- ISS-271: 落 verified ----------------
    it271 = by_id["ISS-271"]
    assert it271.get("status") == "fixing", "ISS-271 状态不是 fixing (实际 %s)" % it271.get("status")
    it271["status"] = "verified"
    it271["verify_by"] = "main"
    it271["verify_date"] = TODAY
    it271["verify_result"] = VERIFY_271
    it271["fix_ref"] = (
        "MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md (42,686 B) · "
        "MECH/board_port_opening_s6_check.py (32,351 B · --selftest rc=0 5/5) · "
        "HANDOFF/2026-11-17_mech-lead_ISS271_板侧开口S6认领与LED位置约束.md (54,444 B) · "
        "state/fragments/mech.yaml (frag_write.py 原子写 · grep -c iss271 = 7)"
    )
    it271["note"] = (it271.get("note") or "") + (
        "\n★**2026-11-17 04:5x (cron 775d9893 继续执行后继计划) · main 独立复验后落 verified** ★ "
        "(★实测: 交卷物在盘 · board_port_opening_s6_check.py --selftest rc=0 5/5 · --json rc=0 与规格页逐字一致 · "
        "板框三套判定与机器输出一致 · 93.49mm 独立复算 = 93.4927 · "
        "merge rc=0 · gate_check rc=0 Q1 18/18 · "
        "受保护 8 件 md5 逐字节未变 (含 3 个 MECH 脚本 db58ff6a/4ae5827e/c4bf9151)★) "
        "★**⇒ 检修口开口在「板只改一次」那一趟里有人认领了 (S6) · mech-lead 名额由此释放** ★ "
        "★**本单自发现的隐藏前置 (G-5 亮度档须排在 S6 之前) 已登记 ⇒ 归 main 排期, 不代拍** ★"
    )

    # ---------------- ISS-269: 僵尸 fixing ⇒ 重派 (状态保持 fixing) ----------------
    it269 = by_id["ISS-269"]
    assert it269.get("status") == "fixing", "ISS-269 状态不是 fixing (实际 %s)" % it269.get("status")
    it269["note"] = (it269.get("note") or "") + NOTE_269

    # ---------------- ISS-272: 落 fixing (本轮派出) ----------------
    it272 = by_id["ISS-272"]
    assert it272.get("status") == "open", "ISS-272 状态不是 open (实际 %s)" % it272.get("status")
    it272["status"] = "fixing"
    it272["dispatched_at"] = TODAY

    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)

    # ---------------- dispatch_log: 追加两条派活记录 ----------------
    with open(DL, encoding="utf-8") as f:
        dl = yaml.safe_load(f) or {"dispatches": []}
    dl.setdefault("dispatches", [])
    dl["dispatches"].append({
        "issue": "ISS-269",
        "agent": "hw-lead",
        "at": TODAY,
        "brief": ("★**重派 (★main 04:5x 实测本单是僵尸 fixing: 会话 compaction 后死, 零交卷物★)** ★ "
                  "taskName=advance_iss269 · runTimeout 5400s · "
                  "★**三条硬纪律**: ① 先写盘再补自证输出 ② 不许整文件读大文件 (只读 :575~:595) ③ 沙盒用 PCB_OUT=/tmp 不许写盘上板 ★"),
    })
    dl["dispatches"].append({
        "issue": "ISS-272",
        "agent": "sw-lead",
        "at": TODAY,
        "brief": ("★**派活 (★main 04:5x · sw-lead 名额由 ISS-270 verified 释放★)** ★ "
                  "taskName=advance_iss272 · runTimeout 5400s · "
                  "★**独立复核 main 亲手改的 state/delivery_truth.py 口径① 归类 (验证分离: main 不能自签)★**"),
    })
    atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))

    print("★落盘完成:")
    print("   ISS-270 fixing → verified (main 独立复验)")
    print("   ISS-271 fixing → verified (main 独立复验)")
    print("   ISS-269 fixing 保持 (僵尸 → 本轮重派, note 追加实测证据)")
    print("   ISS-272 open → fixing (本轮派出 sw-lead)")
    print("   dispatch_log.yaml 追加 2 条派活记录")


if __name__ == "__main__":
    fcntl.flock(open(LOCK, "w"), fcntl.LOCK_EX)
    main()
