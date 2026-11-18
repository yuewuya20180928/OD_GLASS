#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 17:5x · job 775d9893「ARS45 继续执行后继计划」
★决策页追加 §A-补21 (r59) ★
=========================================================================================
★**本段写什么 (★main 本机实读盘面 + 实跑 rc·不抄任何 agent 报告★)**:
  · ① 本轮内部推进 (ISS-294 → verified / ISS-293 派出+重复派撤回 / ISS-295 归兄弟 job / ISS-296 新开待派)
  · ② 待拍板面: ★**44 条一条没动 (44/44 全覆盖·本 job 实跑逐 key 核过)★** + ★**新增 2 条 PM→boss 拍板项
    (ISS-294 交卷单 §B5 留的 4 条几何取舍 + ISS-290/294 口径分叉)★ ⇒ ★**只列选项与代价, 不代拍★**
  · ③ 阶段门 / 链门 / 巡检 rc (main 17:5x 本机实跑)
  · ④ 本 job 派活口径 + ★**与兄弟 job fb67af40 的并发协调记录 (重复派已撤)★**
★**边界**: ★**只追加决策页一个文件** (★老字一行不删·追加式★) ⇒ 不碰 issue_log / 分片 / 板 / 网表 / 脚表 / BOM / outbox ★
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
BAK = PAGE + ".bak_20261117_1755_r59"
TODAY = "2026-11-17"

SEC = """

---

## §A-补21 · ★★r59 · 2026-11-17 17:5x · ★★★**ISS-294 收口 + ISS-293 重派 (★重复派已撤★) + ISS-296 新开待派 + 待拍板面 44 条一条没动 + 新增 2 条 PM→boss 拍板项**★★★ (★cron 775d9893 本机实跑★)

### ★① 本轮内部推进 (★main 17:4x~17:6x 本机实查盘面, 不抄任何交卷报告★)

★| 单号 | owner | 状态 | 本轮发生了什么 | ★
|---|---|---|---|---|
| ★**ISS-292** ★ | hw-lead | **fixing** | ★**在飞** (会话 `4a4fade6` status=running · 队列 job fb67af40 派) ⇒ ★**本 job 不重复派 (★一个 agent 同时只能有一个写会话★)** ★ | ★
| ★**ISS-293** ★ | sw-lead | **fixing** | ★**17:18 那一趟 failed (★交卷单只剩 935 B 骨架★) ⇒ 17:4x 被重开为 open ⇒ 本 job 17:45 派出 (taskName `advance_iss293`) ⇒ ★**17:48 兄弟 job fb67af40 并发也派了一趟 (会话 `347ae23f` "ISS-293 cont1")⇒ ⇒ 两个 sw-lead 写会话同时在飞 = 本项目 R18 已知风险 (分片互相覆盖·合并丢 12%~38%) ⇒ ⇒ ★**本 job 已把自己的那一趟 `subagents kill` 撤回 (★保留兄弟 job 那趟·它的 brief 与 issue_log 登记一致 = 18003 B★)⇒ 冲突已解除** ★ | ★
| ★**ISS-294** ★ | mech-lead | **verified** | ★**已由 main 17:4x 独立复验落 verified** (★9 条 rc 自跑: 交卷自证脚本 rc=0 · M2/N3 两道闸 + 各自 `--selftest` 12/12 rc=0 · 回归 rc=0 · 板 md5/mtime 未动★) ⇒ ★**mech-lead 名额空出来** ★ | ★
| ★**ISS-295** ★ | mech-lead | **fixing** | ★**本 job 17:5x 打算开的那一单, 被兄弟 job fb67af40 抢先开了 (★scope = 「结构侧输入一次性收口 + 过期结论防漂闸」· brief = `state/dispatch_briefs/ISS-295_mech_claims_and_verdict_freshness.md`★) ⇒ ★**本 job 把误写进 `state/dispatch_log.yaml` 的那条重复条目删掉了 (★错 scope 的条目会误导以后复盘★) ⇒ ISS-295 归兄弟 job 所有, 本 job 不碰** ★ | ★
| ★**ISS-296** ★ | mech-lead | **open (★本轮【不派】★)** | ★**本 job 新开** (★任务书 = `state/dispatch_briefs/ISS-296_mech_legal_reboard_mechanism.md` · 12394 B · 已过 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★) ⇒ ★**为什么不派: mech-lead 名额被 ISS-295 占着 ⇒ 一个 agent 同时只能有一个写会话 ⇒ ★**★**且状态【留 open】而不是先落 fixing (★先落 fixing 再不派 = 造【僵尸 fixing】⇒ 永久占住 mech-lead 名额★)⇒ 等名额空出来由 `state/advance.py` / 队列 job 正常派出** ★ | ★

★**★★ISS-296 的病灶 (★main 17:4x~17:5x 本机实读, 逐条带行号·这是板那一趟开工前 MECH 侧的最后一件前置★)★★**:
- ★**`MECH/check_board_frame_coords.py` L79** `PROTECTED` 字典: ★`"demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075"` ★ (共 2 件: 板 + `.kicad_pro`) ⇒ ★**基线写死 ⇒ 板一改 ⇒ C4 必红** ★
- ★**`MECH/check_demo_struct_truth.py` L81** `MD5_EXPECTED`: 同一个板 md5 ★ (共 6 件) ⇒ ★**基线写死 ⇒ 板一改 ⇒ 必红** ★
- ★**同一个文件里已经治过同一种病, 但只治了一半**: `MECH/check_board_frame_coords.py` L76~L80 自己写着 ★「★**ISS-286 · 2026-11-17** ★★ 原先这里是 5 件 (板 / `.kicad_pro` + 网表 / 脚表 / BOM 三件写死 md5) ★★⇒ 网表 / 脚表 / BOM 三件【移出】写死基线, 改走【落表台账链头】★★」 ★ ⇒ ★**★★★同一个病, 同一个文件, 只治了三件, 板那两件没治 ⇒ 现在板要合法变了, 缺口暴露★★★ ★**
- ★**MECH 侧【没有】「合法改板」机制**: `grep -rn "reboard" MECH/*.py | wc -l` ⇒ ★**实测 = 0** ★ ⇒ ★**而 SW 侧 ISS-284 早就有了 (★`check_r6_hard_protected()` 四条判据 + `SW/SW_MD5_BASELINE_LEDGER.md` §1 的 `hard_protected[].reboard` 四项原子映射 + 判决源 = 落表台账链头★) ⇒ ★**ISS-296 = 把这套【已验证的形状】接到 MECH 侧两道闸 + 把 MECH 侧「收工后同一次重锚」写成收工清单强制项** ★
- ★**为什么这条必须在板那一趟【之前】落地**: ★**那趟一开工板 md5 就变 ⇒ MECH 两道闸当场假红 ⇒ ⇒ 收工验收时的假红会被读成「板改坏了」⇒ ⇒ 有人去改板凑绿 ⇒ ⇒ 最坏 = 把 `C_VBUS_GND` 装回板上 (★ISS-289 交卷单点名的 2-4 周 + ¥4-8K 返工★)** ★

### ★② ★★待拍板面: 44 条一条没动 (★44/44 全覆盖·本 job 17:5x 逐 key 核过★)★★

★**★`python3 state/advance.py --json` ⇒ `decisions` = 44 条; 本 job 把 44 个 key 逐个在决策页里 grep ⇒ ★**未覆盖 = 0 条** ⇒ ★**⇒ 待拍板面与 r58 完全一致, 一条没动★** ★

★★**但本轮新增 2 条 PM→boss 拍板项 (★来自 ISS-294 交卷单 §B5 + ISS-290 §4 的口径分叉·【只列选项与代价, 不代拍】★)★★:

★| # | 待拍板项 | 选项与代价 (★main 17:4x 实读交卷单原文★) | main 的建议默认值 (★**待老板一句话确认**★) | ★
|---|---|---|---|---|
| ★**① USB-C 边开口的缺口 X 取值** ★ | ★**`J_USB_C` 结构件板边开口的缺口 X 范围** ★ | ★**(a) 取最小合法值** ⇒ 开口 X **132.995..147.005** (宽 **14.010**) ★**(b) 按立柱/螺钉头外扩** ⇒ D=2.60 ⇒ 132.020..147.980 · D=3.00 ⇒ 131.820..148.180 · D=3.80 ⇒ 131.420..148.580 ⇒ ★**代价 = 每侧多让约 1 mm** ★ | ★**(a) 最小合法值** ★ | ★
| ★**② 边开口深度 7.300 的假设** ★ | ★**开口 Y 深度** ★ | ★**(a) 7.300 = 最坏假设 (内壁齐平板边)** ★**(b) 按座体实际深度** ⇒ ★**代价 = (a) 保守占位 · (b) 需要座体 3D/实物确认 (★本机量不到★)** ★ | ★**(a) 7.300 最坏假设** ★ | ★
| ★**③ Z 向窗口 `OPEN_Y_eff(h)` = 4.60/4.60/5.80** ★ | ★**它不在板面坐标里** ⇒ ★**结构侧只能登记、不能机器验** ★ | ★**(a) 保留登记 + 写进作业包 §3-S6 (★需 hw-lead 抄★)** ★**(b) 不写进作业包 ⇒ 收工时无人核** ★ | ★**(a) 写进作业包 §3-S6** ★ | ★
| ★**④ `BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §4 的 `J_USB_C` verdict 口径分叉** ★ | ★**ISS-290 那一页写着「结构侧缺一条边开口规格」, 而 ISS-294 已把它补上 ⇒ 两页两种说法** ★ | ★**(a) 追加式订正节 (★老字保留·ISS-295 正在干这一件★)** ★**(b) 直接改老行** ⇒ ★**违反追加式铁律, 不采纳** ★ | ★**(a) 追加式订正节 (★ISS-295 在干★)** ★ | ★

★★**★这 4 条为什么必须排在「板只改一次」那一趟【之前】拍**: ★**① ② 直接决定板边开口几何 (★那是板的一处改动★) ⇒ 拍晚了 = 板要改第二遍** ★ · ★**③ 决定它进不进作业包 (★不进 = 收工时无人核★)** ★ · ★**④ 是口径分叉 (★不是几何·不卡板·但会误导下一个读页的人★)** ★

### ★③ 阶段门 / 链门 / 巡检 (★main 17:5x 本机实跑·原样 rc★)

| 项 | rc | 读数 |
|---|---|---|
| ★`state/merge.py` ★ | ★**0** ★ | ★STATE.yaml 已刷新 (17:50:25) · 产出 517 · 阻塞 43 (高危 33) · 未闭合需求 297 · 冲突 0 · 健康度 red ★ |
| ★`state/gate_check.py` ★ | ★**0** ★ | ★全部检查项通过 · 缺口清单 3 条 (★hw 127 / sw 73 / mech 95 条需求还没人答★) ★ |
| ★`state/issue_check.py` ★ | ★**0** ★ | ★问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖) ★ |
| ★`state/stage_gate.py` ★ | ★**1** ★ | ★当前 **G1 原理图 / PCB 定稿** · 还差 **1** 项才能进 G2 (★G1a-4 / G1a-8 两条红·与昨日同★) ★ |
| ★`state/daily_check.py` ★ | ★见本 job 汇报 ★ | ★(★PCB↔网表 rc=1 · 投产包准入 ❌ ⇒ 板还是旧网表的板·不许投板★)★ |
| ★板 md5 / mtime ★ | — | ★**`611b869e13518c3c023fb178f91a0075` · mtime 仍 `2026-11-06 07:07:17` ⇒ 零写板仍成立** ★ |

### ★④ 本 job 本轮派活口径 (★`state/advance.py --json` 17:5x 实跑 + 会话实查★)

- ★**17:43 首次 `--json` ⇒ `internal: []`** (★三个名额全被 `fixing` 占着) ★ → ★**17:45 复跑 ⇒ `internal: [ISS-293 → sw-lead]`** (★ISS-293 被兄弟 job 在 17:4x 重开为 open★) ⇒ ★**已派** ★
- ★**17:5x 复跑 ⇒ `internal: []`** (★三个名额又占满: hw=ISS-292 / sw=ISS-293 / mech=ISS-295★) ⇒ ★**⇒ 本轮净派活 = 1 条 (ISS-293) + 撤回 1 条 (重复派) + 新开 1 条待派 (ISS-296)** ★
- ★**★并发协调记录 (★本项目第一次把这种事写进决策页★)★**: ★**兄弟 job `fb67af40`(ARS45 队列自动派活) 与本 job `775d9893`(继续执行后继计划) 在 17:4x~17:5x 同时动了同一批单 ⇒ ⇒ 出现过【同一个 issue 被两个 job 各派一趟】⇒ ⇒ 本 job 已把自己的重复那趟 kill 掉, 并把误写进 dispatch_log 的错 scope 条目删掉 ⇒ ⇒ ★**规矩 (★建议写进 AGENTS.md★): 两个 job 同时动同一批单时, 【先落 fixing 再 spawn】的那一方是主, 另一方必须撤自己的会话, 不许两个写会话并行★** ★
- ★**★零外发**: ★**本 job 全程没发任何邮件 / 询价 / 采购 / 联系供应商** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 政策★) ⇒ ★**`approvals` 段本轮恒为空 (★实跑 0 条·与政策一致★) ⇒ outbox 草稿只备不发** ★
- ★**★GitHub**: ★**本 job 不推 (★老板 2026-11-11 09:5x 口径: 间隔 5 小时且有进展才推 ⇒ 由独立 job `ARS45 GitHub 同步 (每 5 小时 · 有进展才推)` 负责★) ⇒ 本 job 只落本地快照 `PROGRESS_SNAPSHOT.md`** ★
"""


def main() -> int:
    if not os.path.exists(PAGE):
        print("⚠ 决策页不存在: %s ⇒ 中止" % PAGE)
        return 1
    shutil.copy2(PAGE, BAK)
    before = os.path.getsize(PAGE)
    with open(PAGE, "a", encoding="utf-8") as f:
        f.write(SEC)
    after = os.path.getsize(PAGE)
    print("· 决策页已追加 §A-补21 (r59): %d → %d B (+%d)" % (before, after, after - before))
    with open(PAGE, encoding="utf-8") as f:
        txt = f.read()
    assert "§A-补21" in txt, "追加节未落地"
    print("· 校验: §A-补21 在页内 = True · 老字保留 (追加式)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
