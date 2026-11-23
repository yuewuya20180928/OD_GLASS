#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★补派 ISS-360 cont1 (cron fb67af40 · 2026-11-23 13:45)★
★**为什么补派**: cont0 (会话 `agent:mech-lead:subagent:66aaa11e-07a4-4272-9833-f44949a4933e`,
   sessionId `b41831b3-2b27-492c-90f1-4b03bc7c9a64`) 于 13:27:02 被掐断
   (sessions_list: status=done + **abortedLastRun=true**; transcript 末两条 assistant 消息正文皆空)
   ⇒ 只落了骨架 ⇒ ISS-360 成【僵尸 fixing】(台账 status=fixing 但零交付物) ⇒ 队列断线。
★**处置**: 沿用本仓既有惯例 (ISS-353/354 cont1 / ISS-358 cont1 / ISS-359 cont1 都是这么救的):
   status 保持 fixing (不落 open ⇒ 下一轮 in_flight 规则看不见本单 ⇒ 不会重复派)
   + 写 dispatch_log (cont: cont1 + dead_cause) + 生成 cont1 任务书 + spawn。
★**边界**: 零写板 · 零落表 (issue_log 本单不改任何字段, 只在 dispatch_log 追加) · 零改闸 · 零外发
★**fail-closed**: 任何自检不过 ⇒ 抛错 ⇒ 不写盘 / 不 spawn。
"""
import hashlib
import os
import shutil
import yaml

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(PROJ, "state")
DL = os.path.join(STATE, "dispatch_log.yaml")
IL = os.path.join(STATE, "issue_log.yaml")
BRIEF_DIR = os.path.join(STATE, "dispatch_briefs")
BRIEF_NAME = "ISS-360_mech_board_frame_default_void_marker_cont1.md"
BRIEF_PATH = os.path.join(BRIEF_DIR, BRIEF_NAME)

ISSUE = "ISS-360"
AGENT = "mech-lead"
AT = "2026-11-23"

# ---------------------------------------------------------------- A 段
A_SECTIONS = r"""
## ★★A. main 订正 (★main 2026-11-23 13:4x 本机实读·★下面 B 段才是 brief 原文·★A 段只【更正事实】与【加安全规则】·不删 brief 任何一条任务项★★)

★★**A-1 · ★【死因与续做位置】★** (★main 逐行实读 transcript + 盘面·★不抄任何 agent 报告★)
- ★**cont0 会话**: `agent:mech-lead:subagent:66aaa11e-07a4-4272-9833-f44949a4933e` (sessionId `b41831b3-2b27-492c-90f1-4b03bc7c9a64`) · ★**13:23:10 起 · 13:27:02 止 · 存活 231.7 s** ★
- ★**死状**: `sessions_list` 报 ★**`status: done` + `abortedLastRun: true`** ★ ⇒ ★**transcript 末两条 assistant 消息正文都是空的** (05:23:51.235Z 与 05:27:02.966Z) ⇒ ★**模型连吐两次空回复 ⇒ 会话被掐断** ⇒ ★**不是 agent 偷懒·不是文件写坏·是它把预算烧在【核实 brief 前提】上** (★同类死法在 2026-11-23 09:2x 的 ISS-358 cont0 上已发生过一次★)
- ★**已落 (2 件, 都是骨架)**:
  - ★**① 交卷页骨架**: `HANDOFF/2026-11-23_mech-lead_ISS360_板框建议默认值作废标注.md` · 416 B · 13:23 ⇒ ★**B1~B6 六个 `##` 标题都在, 但每节正文都是 `(骨架待填)`** ★
  - ★**② `logs/iss360/` 目录已建** ⇒ ★**空目录, 0 件** ★
- ★**未落 (4 件, ★就是你这一趟要做的★)**:
  - ★**① 目标页零改动**: `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md` ★**mtime 仍 `2026-11-18 07:53:30.105521781` · 全文件 md5 仍 `c77cff3f3cd8528f0aa30486270aeb19` · 68,195 B** ⇒ ★**§1-3 里 `ISS-341` 0 命中 = 订正标记一个字都没落** ★
  - ★**② 交卷页 6 节仍是 `(骨架待填)`** ★
  - ★**③ 分片零本单痕迹**: `state/fragments/mech.yaml` ★**`grep -c iss360` = 0 · 全文件 md5 仍 `f1083d47cd76c0621766ccb63e8ad48a`** ★
  - ★**④ `logs/iss360/` 里 0 件读数** ★
- ⇒ ★**⇒ 本单是【续做】不是【从零】**: 前置事实 main 已替你验完 (见 A-2) ⇒ ★**你的预算全花在【产出三件】上, 别再花预算去证伪 main 的前提** ★

★★**A-2 · ★【main 本机实读已验证的事实】★** (★2026-11-23 13:4x · ★**这些不必重跑, 直接用**★) ★★

★★**(1) 目标文件 = `MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md`** ★
- 全文件 **387 行 · 68,195 B · md5 `c77cff3f3cd8528f0aa30486270aeb19` · mtime `2026-11-18 07:53:30.105521781`** ★
- ★**§1-3 的确切行号 (main 逐行数过)**: ★**L105** = `### ★1-3 · 建议默认值 (★建议 ≠ 拍板★)` · ★**L107** = 「★**建议默认值 = 选项 ② `F30A` (60×30 套 A) + 板厚 1.00mm (≤1.00) + 层数 6** ★ (★**只作参考·本单不代拍**★)」 · ★**L108** = 「★**理由 (逐条)**…」 · ★**L109** = 建议的拍板顺序 · ★**L110** = 「★**为什么板厚必须随框同拍**…」 · ★**L111** = 空行 · ★**L112** = `### ★1-4 · 不拍的后果` ★
- ⇒ ★**追加位置 = L110 之后 / L112 之前** (★即 §1-3 段落末尾★) ⇒ ★**L105~L110 一个字节都不许动** ★
- ★★★**老字零改动的机器判据 (main 已取基线 ⇒ 你直接对拍)**: ★**`sed -n '100,110p' MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md | md5sum` = `543c4d7fb001c66ea2ce6b80bebb6769`** ★ ⇒ ★**你追加完之后这条必须还是 `543c4d7fb001c66ea2ce6b80bebb6769`** (★你只在 L110 之后加内容 ⇒ 100~110 行一个字节都不变 ⇒ md5 必须恒等★) ⇒ ★**这就是「零删除既有行」的机器证据, 贴进交卷页 B6** ★ ★

★★**(2) ISS-341 机器判决 (★main 13:4x **实跑** `MECH/check_board_frame_candidate_compat_gate.py` ⇒ **rc=0**; `--selftest` ⇒ **rc=0** · 末行 `★结论: 11/11 条用例与预期一致` + `ALL TESTS PASS`★ ⇒ ★**闸已验, 你不必重跑** (★要贴自己的输出就只跑一次, 别跑两遍★))** ★
- 闸 §8 结论逐字: 「现役板 = 160.00 × 100.00 mm · 8 铜层 · 1.60 mm · 186 封装 · SOM 承载区形态 (RK3572 SOM 直插 BTB 座)」 + 「只有与现役板【同框同层同厚】的那一帧才可能让「板那一趟」= 改现役板一次 ⇒ 本机实测: B160x100」 + 「F30A (60.00×30.00 / 6 层 / 1.00 mm) ⇒ 这一趟 = 重画一块新板 (现役板 186 封装 / 45 条未连接 / 作业包 S1~S13 全部作废)」 + 「P60x15 … 同」 + 「页尾铁律: 「板只改一次」只有在【框不变】时成立 —— 换框 = 新板第一版, 不是修一次」
- 闸 §6 交叉核对逐字: 「已落表建议默认值 指向帧 : F30A」 + 「该帧的机器判决 : 这一趟 = 重画一块新板 (现役板 186 封装 / 45 条未连接 / 作业包 S1~S13 全部作废)」
- 闸 §6 口径分层提醒逐字: 「★**口径分层提醒** : ★建议·非已决定★; 本闸只判【该帧与现役板的相容性】, 不替老板拍『这一趟画台架板还是产品板』这个上位问题」
- ★★★**ISS-341 交卷页 §B1-4 的结论逐字 (★这一条决定你的标注该怎么写·★照它写, 不许自己发挥★)★★★**:
  「★**结论: 【站在它自己那一层上没算错, 但放在【U-1 这一个键】上答不了【这一趟画哪块板】这个问题】⇒ 建议改的是【分层与题面】, 不是【那一档的几何数】。** ★」
  + 「F30A 的几何数 (60×30 / 6 层 / ≤1.00) 算错了吗? | ★**没算错** ★ | 36 档结构外形判据下 F30A 确实唯一全绿 (板重 3.33 g = 整机 4.6~6.8%)」
  + 「拿它当「这一趟该画 F30A」的依据, 推理跳了几步? | ★**跳了一步** ★ | ★**中间缺「这一趟的物理对象」这一层** ★」
  + 「机器判决 | ★**F30A = 重画一块新板** ★」
- ⇒ ★★★**⇒ 你的订正标注必须写「【这一栏答错了层·不该替上位问题作答】」, 严禁写成「F30A 的几何数算错了 / 建议值本身是错的」** ★★★ ⇒ ★**因为那是 ISS-341 明文否定过的说法 (★它自己写着「没算错」★)** ⇒ ★**写错了 = 本单交的是假口径 = main 签收时直接打回** ★

★★**(3) 权威页 (★main 13:4x 实测行号★)**: `DECISION_ONE_PAGER_2026-11-22.md` ★**§⑥ L89** / ★**§⑦ L131** / ★**§⑬-3 L370** ★ · `DECISION_INDEX_2026-11-18.md` ★**§E-1 L177** / ★**§R L1000** / ★**§T L1053** ★ (★§R 标题逐字 = 「★【2026-11-23 05:3x · 追加式 · ★★U-1 建议默认值【分层化】订正 (★§E-1 那一行的建议默认值已被 ISS-341 机器判决推翻·★保留作历史留档·结论不再引用★)】★★」★)

★★**(4) 板面双证 (★main 13:4x 实读★)**: `HW/PCB/demo_mainboard.kicad_pcb` md5 = ★**`611b869e13518c3c023fb178f91a0075`** ★ · mtime = ★**`2026-11-06 07:07:17.362193413`** ★ · 4,940,213 B ⇒ ★**交卷时必须仍是这三个值** ★

★★**(5) 分片基线 (★并发哨兵★)**: `state/fragments/mech.yaml` md5 = ★**`f1083d47cd76c0621766ccb63e8ad48a`** ★ (★cont0 13:23 实读·与 main 一致★) ⇒ ★**你写之前再记一次; 若与这个值不同 ⇒ 有人并发写过 ⇒ 停下 + 在交卷页 B5 写清「分片被并发改动, 已停止」·不许静默覆盖** ★

★★**(6) `state/frag_write.py` 实测用法 (★main 13:4x 跑 `--help` 实读★)**: `--agent` / `--add-need key=... to=... item="..." [since=...]` / `--add-answer key=... to=... value="..." [ref=...]` / `--add-artifact path=... summary="..." [kind=...] [version=...]` / `--add-claim key=... value="..." [note=...]` / `--status phase=... progress_pct=N health=... summary="..."` / `--show` ⇒ ★**一律走它, 零次 `open(p,"w")`** ★

★★**(7) 上游已核 (★main 13:4x 本机实读 `state/issue_log.yaml`·不抄任何 agent 报告★)**: ★**ISS-341 = verified** (owner mech-lead · `fix_ref` 在案) · ★**ISS-316 = verified** (★目标页就是 ISS-316 的交卷页 ⇒ 你是在一个【已被 main 签收的页】上做追加式订正·不是改别人的未签收页★)** ⇒ ★**所以本单绝对不许改写 ISS-316 的任何正文 (★那页已签收·只许追加★)** ★

★★**A-3 · ★【防超时纪律 · ★上一趟就是死在这里★】★★**
- ★**① 先出成果, 后补证据**: ★**第 1 个动作就把订正标记追加进目标页** (★append 一段·★只许追加·不许重写整页★) ⇒ ★**第 2 个动作填交卷页 B1~B6** ⇒ ★**第 3 个动作写 `logs/iss360/`** ⇒ ★**最后才写分片 + 跑闸** ⇒ ★**万一你又被掐断, 盘上已经有真东西, 不是又一颗空壳** ★
- ★**② 不许 `yaml.safe_load` 3 MB 的 `STATE.yaml`** (★2026-11-23 09:2x 那趟 ISS-358 cont0 就是读 STATE.yaml 证伪 brief 撞 120s 无响应死的★) ⇒ ★**要读台账就读小的 `state/issue_log.yaml`** ★
- ★**③ 单条 `exec` ≤ ~120 秒** ⇒ ★**闸跑一次就够** (★rc=0 已由 main 验过, 你要贴输出就跑一次)★ ⇒ ★**绝不跑两遍★**
- ★**④ 目标页只许 append, 其余文件只许走 `state/frag_write.py`** ⇒ ★**零次 `open(p,"w")` 重写** ★
- ★**⑤ `state/merge.py` + `state/gate_check.py` 各跑一次, 把输出贴进交卷页 B6** (★别来回反复跑★)

★★**A-4 · ★【边界 · 与 brief 一致, 只是重申】★★**: ★**零写板** (板 md5 三个值不许变) · ★**零落表** (★不许改 `state/issue_log.yaml` 的任何字段·★不许改 `PROJECT_TRACKER.md`★) · ★**零改闸** (★`state/gate_check.py` / `state/merge.py` / `state/frag_write.py` / `MECH/check_board_frame_candidate_compat_gate.py` 都不许动★) · ★**零外发 / 零采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·全靠自己查资料⇒**本单没有任何需要外发的缺口**·你要引的事实全在盘上·★不许发信·不许询价·不许问供应商★) · ★**不替老板拍板** (★U-1 还是老板的项·你只加作废/分层标注·★不改任何建议值★) · ★**只写 4 处**: 目标页 (追加式) + 交卷页 + `logs/iss360/` + `state/fragments/mech.yaml` (★只走 `frag_write.py`★) ★
"""

# ---------------------------------------------------------------- 取 brief 原文
log = yaml.safe_load(open(IL, encoding="utf-8")) or {}
issues = log.get("issues") or []
target = [it for it in issues if it.get("id") == ISSUE]
assert len(target) == 1, "台账里 %s 条数 = %d (应为 1)" % (ISSUE, len(target))
rec = target[0]
assert rec.get("status") == "fixing", "%s status = %r (本脚本只处理 fixing 的僵尸单)" % (ISSUE, rec.get("status"))
assert rec.get("owner") == AGENT, "%s owner = %r (应为 %s)" % (ISSUE, rec.get("owner"), AGENT)
ORIG_BRIEF = rec.get("task_brief") or ""
assert len(ORIG_BRIEF) > 800, "原 brief len = %d (异常短·拒绝派)" % len(ORIG_BRIEF)
ORIG_MD5 = hashlib.md5(ORIG_BRIEF.encode("utf-8")).hexdigest()
ORIG_LEN = len(ORIG_BRIEF)

# ---------------------------------------------------------------- 组装 cont1 任务书
HEAD = """# ISS-360 · mech-lead · cont1 · ★★【main 续做任务书】★★ (★brief 原文逐字保留在下方·未删一字★)

★★**派单人**: 项目总工 (main / moli) · ★**派活时间**: 2026-11-23 13:45 GMT+8 · ★**cron fb67af40 (ARS45 队列自动派活)** ★
★★**主线口径**: ★**当前主线 = 绘制 PCB 图** (老板 2026-11-17 00:43) ⇒ PCB 线可派 ⇒ ★**但「板只改一次」⇒ 本单是【纯文档订正类】· 零写板 · 零落表 · 零外发** ★
★★**外发口径**: ★**零外发** (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·全靠自己查资料) ⇒ ★**本单没有任何外发缺口** ★
"""

TAIL = """

---

## ★★B. brief 原文 (★`state/issue_log.yaml` 里 ISS-360 的 task_brief 全文·★md5 `%s` · len %d · ★一字未删未改★★)

%s
""" % (ORIG_MD5, ORIG_LEN, ORIG_BRIEF)

body = HEAD + A_SECTIONS + TAIL

# ---------------------------------------------------------------- 自检 (fail-closed)
assert ORIG_BRIEF in body, "自检失败: 原 brief 未逐字嵌入"
assert body.count(ORIG_BRIEF) == 1, "自检失败: 原 brief 出现次数 != 1"
assert body.endswith("\n"), "自检失败: 末尾缺换行"
for banned in ("请放行外发", "等原厂回信", "走 main 外发", "open(p,\"w\")"):
    assert banned not in body or banned == "open(p,\"w\")", "自检失败: 出现外发字样 %r" % banned

os.makedirs(BRIEF_DIR, exist_ok=True)
if os.path.exists(BRIEF_PATH):
    shutil.copy2(BRIEF_PATH, BRIEF_PATH + ".bak_20261123_1345")
with open(BRIEF_PATH, "w", encoding="utf-8") as f:
    f.write(body)

# 回读校验
back = open(BRIEF_PATH, encoding="utf-8").read()
assert back == body, "自检失败: 落盘后回读不一致"
assert ORIG_BRIEF in back, "自检失败: 回读后原 brief 不在"
assert len(back) > len(ORIG_BRIEF), "自检失败: 续做稿比原 brief 还短"

# ---------------------------------------------------------------- dispatch_log 追加
raw = yaml.safe_load(open(DL, encoding="utf-8"))
assert isinstance(raw, list), "dispatch_log.yaml 顶层不是 list ⇒ 拒绝写"
before = len(raw)
assert not [e for e in raw if e.get("issue") == ISSUE and e.get("cont") == "cont1"], \
    "自检失败: dispatch_log 里已有 ISS-360 cont1 条目 ⇒ 拒绝重复追加"

DEAD_CAUSE = (
    "★cont0 (会话 66aaa11e-07a4-4272-9833-f44949a4933e / sessionId b41831b3-2b27-492c-90f1-4b03bc7c9a64) "
    "于 2026-11-23 13:27:02 被掐断 (sessions_list: status=done + abortedLastRun=true; transcript 末两条 assistant 消息正文皆空) "
    "⇒ 只落骨架 (交卷页 416 B 全是「(骨架待填)」+ logs/iss360/ 空目录) ⇒ 目标页零改动 (mtime 仍 2026-11-18 07:53:30 / md5 仍 c77cff3f3cd8528f0aa30486270aeb19) "
    "+ 分片零本单痕迹 (grep -c iss360 = 0 / md5 仍 f1083d47cd76c0621766ccb63e8ad48a) ⇒ ISS-360 成【僵尸 fixing】, 队列断线。★"
    "★main 13:4x 本机实读补齐了全部前置事实 (闸 rc=0 + selftest 11/11 实跑 / 目标页 §1-3 逐行行号 L105~L112 / "
    "老字零改动基线 md5 543c4d7fb001c66ea2ce6b80bebb6769 / ISS-341 §B1-4 结论逐字 / 权威页行号 / frag_write.py 用法) "
    "⇒ cont1 只需【产出三件】, 不必再花预算证伪前提。★★**口径修正 (关键)**: 订正标注必须写「答错了层·不该替上位问题作答」, "
    "严禁写「F30A 几何数算错了」⇒ 那是 ISS-341 明文否定过的说法 (它自己写着「没算错」) ⇒ 写错 = 交假口径 = 签收打回。★★"
)

raw.append({
    "issue": ISSUE,
    "agent": AGENT,
    "at": AT,
    "cont": "cont1",
    "dead_cause": DEAD_CAUSE,
    "brief": body[:300],
    "job": ("cron fb67af40 (ARS45 队列自动派活) · ★补派 cont1 时刻 2026-11-23 13:45 · "
            "★status 保持 fixing ⇒ 下一轮 advance.py 的 in_flight 规则看不见本单 ⇒ 不会重复派 ★"
            "★brief 文件 = state/dispatch_briefs/%s ★" % BRIEF_NAME),
})

old = open(DL, encoding="utf-8").read()
chunk = yaml.safe_dump(raw[before:], allow_unicode=True, sort_keys=False, width=200)
if old and not old.endswith("\n"):
    chunk = "\n" + chunk
with open(DL, "a", encoding="utf-8") as f:
    f.write(chunk)

# 回读校验
chk = yaml.safe_load(open(DL, encoding="utf-8"))
assert len(chk) == before + 1, "dispatch_log 条目数不符: %d != %d" % (len(chk), before + 1)
last = chk[-1]
assert last.get("issue") == ISSUE and last.get("cont") == "cont1", "dispatch_log 末条不对"
assert last.get("agent") == AGENT, "dispatch_log 末条 agent 不对"

# issue_log 必须一个字没动
il2 = yaml.safe_load(open(IL, encoding="utf-8")) or {}
rec2 = [it for it in (il2.get("issues") or []) if it.get("id") == ISSUE][0]
assert rec2.get("status") == "fixing", "issue_log status 被改了 ⇒ 越界"
assert rec2.get("task_brief") == ORIG_BRIEF, "issue_log task_brief 被改了 ⇒ 越界"

print("OK  brief=%s  bytes=%d  orig_md5=%s  orig_len=%d" % (BRIEF_NAME, len(body.encode("utf-8")), ORIG_MD5, ORIG_LEN))
print("OK  dispatch_log: %d -> %d  (ISS-360 cont1 / mech-lead)" % (before, len(chk)))
print("OK  issue_log: ISS-360 status=%s 未动" % rec2.get("status"))
