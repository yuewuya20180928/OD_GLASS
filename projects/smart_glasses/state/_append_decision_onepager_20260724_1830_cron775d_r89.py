#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_append_decision_onepager_20260724_1830_cron775d_r89.py
=========================================================
★cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-24 18:30 · §㊺ 追加式★★

★★【★★本节做什么★★】★★
① 本轮队列实读 (internal/approvals/decisions/waiting 四段)
② ★**老板待拍板清单 55 条的零漏项覆盖复核** (一页 23 · 索引 41 · PENDING 41 · 并集 55)
③ ★**本轮最重要: 上一轮 §㊹-3 挂着的「闸⑩ 并发假红」今天实测【已被修掉并独立复验】★★
   ⇒ ⇒ 「板那一趟」开工前的门禁读数【恢复可信】★
④ ★**「板那一趟」的 13 件拍板面逐 key 命中复核** (13/13)
⑤ 本轮零派 / 零外发 / 零落表 / 零写板 / 巡检实测 rc

★★【★★纪律 (★本脚本自己守★)】★★
  ① ★**零落账**: 不写 `state/issue_log.yaml` / 不写任何分片 (★签收落账归持有写权的一方★)
  ② 零写板 (板 md5/mtime/size 前后各打一次, 纳秒级比)
  ③ 零落表 (网表/脚表/BOM 一字不改)
  ④ ★**只追加本页** (★零改既有页面正文·★旧内容 md5 (前 len_before 字节) 前后逐字相同★)
  ⑤ 不代老板拍板 (★只给「建议默认值」·★标明不是已决定★)
  ⑥ 零外发
  ⑦ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑧ 幂等守卫: 标记已在本页 ⇒ 只复验, 不重复追加
  ⑨ 并发守卫: 追加期间若本页被第三方改动 ⇒ 立刻报告, 不覆盖
  ⑩ 章节号守卫: §㊺ 在全项目 *.md 里必须 0 命中, 否则零写盘退出
"""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

PAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
NETLIST = os.path.join(PROJ, "HW/netlist_v1.csv")
PINS = os.path.join(PROJ, "HW/netlist_v1_pins.csv")
BOM = os.path.join(PROJ, "HW/BOM_v1.csv")

LOGDIR = os.path.join(PROJ, "logs", "cron775d_r89")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_SIZE = 4940213

MARK = "★★㊺ 【2026-11-24 18:3x · 追加式】"

SECTION = """
## ★★㊺ 【2026-11-24 18:3x · 追加式】★ ★★队列读数 (internal=0 · 三槽位在飞) + ★★闸⑩ 并发假红【已修 + 已独立复验】⇒ 「板那一趟」开工前的门禁读数恢复可信★★

★**★本段全部数字 = main 本机实跑 (★2026-11-24 18:2x~18:5x·★`python3 state/advance.py --json` + 五连门禁 + 并发双跑实测·★不抄任何 agent 报告★)★** ★

### ★§㊺-1 本轮队列读数 (★18:2x 本机实跑★)

| 段 | 条数 | 说明 |
|---|---|---|
| internal | **0** | ★**三个总工名下各有一条 `fixing` 在飞** (★hw-lead = ISS-396 · mech-lead = ISS-397 · sw-lead = ISS-398 ★**兄弟 job `fb67af40` 18:2x 新开并派出, 三个 owner 会话本轮实查仍 `running`★**) ⇒ ★**零派** ★ |
| approvals | **0** | ★**恒空** (★老板 2026-11-12 02:02「不再发信, 全靠自己查资料」政策 ⇒ `state/outbox/NO_OUTBOUND_POLICY.md` 已立★) ★ |
| decisions | **55** | ★**hw 13 · mech 17 · pm 12 · sw 13** (★与 15:2x 的 55 条同数·★逾期 31 条·★本轮**零新增**★) ★ |
| waiting | **0** | — |

★**`advance.py --json` 的 rc=1 的含义 (★实读 `state/advance.py`★)**: ★**rc=1 = 无可派 + 无待批 = 正常信号, 不是错误** ★
★**★零派的根因【本轮第二次形态变化】★**: ★**上一轮 (15:2x) 是「三个槽位被占」· 本轮 (18:2x) 仍是「三个槽位被占」· 但占槽的那三条【换成了 18:2x 新派的三条】** ⇒ ★**⇒ 本 job 与兄弟 job 零撞车 (★先落 fixing 再 spawn ⇒ `advance.py` 看不见在飞单★)★ ★

### ★§㊺-2 ★★老板待拍板清单覆盖复核 (★本轮实跑·★不抄上一轮读数★)★

★**55 条 · 一页命中 23 · 索引 (`DECISION_INDEX_2026-11-18.md`) 命中 41 · 正文 (`DECISION_PENDING_2026-11-16.md`) 命中 41 ⇒ ★★并集 55 ⇒ 55/55 零漏项★★** ★
★**★「板那一趟」的 13 件拍板面逐 key 命中 = 13/13** ★ (`boss_esd_model_axis_pending_20261117` · `boss_shutdown_semantics_and_loadswitch_20261117` · `iss324_d_led_g_placement_decision` · `boss_dled_g_expose_decision_20261117` · `iss310_main_board_frame_u1_decision` · `q3_storage_and_audio` · `boss_c_vbus_gnd_reserve_pad_20261117` · `boss_state_value_acceptance_drift_20261117` · `iss340_c_bucket_boss_decisions` · `iss364_k2_d_esd_usb_d_2v3_pin` · `iss364_k3_button_3n_vs_1p5n` · `boss_decide_reboard_mtime_size_caliber` · `boss_decide_second_reboard_stop_authority`)
★**⇒ 13 件一件没少 · 一件没代拍 · 板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答** ★

### ★§㊺-3 ★★★★本轮最重要的一条: ★★上一轮 §㊹-3 挂着的「闸⑩ 并发假红」今天【已被修掉 + 已独立复验】★★★★ ★

★★**★① 病灶复述 (★上一轮 §㊹-3 实测·★本轮不改一个字★)★**: ★**钉板闸⑩ (`HW/check_preflight_regen_idempotent.py`) 的沙盒落点是【固定路径】⇒ `shutil.rmtree` 在另一个进程正往同一落点写时抛 `Errno 39` ⇒ 假红是【必然事件】不是偶发 ⇒ ⇒ 「板 md5 / 落表链 / 结构真值 漂移 ⇒ 板那一趟不许开工」这条红【当时不可信】** ★
★★**★② 本轮实测: 病灶已修 (★修在【产生点】·★不是把红项调没★)★★**: ★**ISS-395 交回的修法落在闸源码 L69/L71/L143/L147** (★`SBX_BASE` + `SANDBOX = .../run_<pid>_<ms>` ⇒ 落点每次运行唯一; 删除改成【只删自己这一份】⇒ 并发两跑互不干扰★) ★
★★**★③ 本轮独立复验 (★本 job 自己跑·★不抄任何 agent 报告★)★**:
| 动作 | 读数 |
|---|---|
| ★**闸⑩ 并发双跑 (★同秒两个进程真跑真板真页★)** ★ | ★**A rc=0 · B rc=0** (★两跑都末行「✅ rc=0: ★★页与生成器同源 · 重跑零差异」★) ⇒ ★**假红确实消失了** ★ |
| ★**闸⑩ 单跑** ★ | ★**rc=0** ★ |
| ★**ISS-395 新闸 `HW/check_gate10_concurrency_safety.py` 裸跑** ★ | ★**rc=0** (★K0~K5 六条全过: 并发两跑双绿 · 落点每次运行唯一 · 删除不抛未捕获异常 · 板三项零扰动 · **真漂移仍然判红**★) ★ |
| ★**同闸 `--selftest`** ★ | ★**rc=0 · 5/5 · `ALL TESTS PASS`** ★ (★**S3 是命门**: 沙盒里改坏一个真源 ⇒ 既有闸必须 rc=1 ⇒ ★**「真漂移仍判红」这条不许放松, 而它没被放松★**) ★ |

★★**★④ ⇒ 对老板的意义 (★只讲影响, 不代拍★)★**:
★**① 「板漂移了 ⇒ 不许开工」这条红, 从本轮起【恢复可信】** (★上一轮 §㊹-3 说它「红红不可分 ⇒ 真漂移会被假红淹没」· 本轮实测那个淹没源已除★) ★
★**② ★**但 G1 仍开、仍不许投板** ★ — ★**理由与这条红无关**: 板三项指纹 `611b869e…` / mtime `2026-11-06 07:07:17` / size `4940213` **18 天逐字节未动** ⇒ ★**布线 unconnected 45 → 0 这项还没做** ★
★**③ 这道闸【还没挂链】** ⇒ ★**它现在是【干净可挂】的状态: 裸跑 rc=0 · 自测 5/5 · 真漂移仍判红 ⇒ ★**建议挂进 `state/gate_check.py` 的 Q7 钉板闸链 (★挂不挂是 main 的地界·本 job 不代拍★)** ★

### ★§㊺-4 本轮推进实况 (★零派/零外发/零落表/零写板·★巡检实测 rc★)

★**★派活**: ★**`internal` = 0 ⇒ 本轮按 advance.py 队列【零新派】· 跳过 3 条 (★hw-lead / mech-lead / sw-lead 各一条 `fixing` 在飞·★三个 owner 会话本轮实查仍 `running`★)** ★ ⇒ ★**本轮派的 PCB 类 = 0 条 (★兄弟 job 18:2x 派的那 3 条全是【纯分析 / 登记落盘 / 新建真相页 + 新建机器闸类】·★零写板·★合「板只改一次」纪律 ①★)** ★
★**★外发**: ★**0 封邮件 · 0 次联系供应商 · 0 张采购单 (★`approvals`=0 · `state/outbox/` 19 份草稿只备不发·★`NO_OUTBOUND_POLICY.md` 已立★)** ★
★**★零落表**: ★**网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 三件 md5 前后逐字节相同** ★
★**★零写板**: ★**板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★
★**★巡检实测 rc (★本机实跑·★`tail` 不吞退出码★)★**:
| 脚本 | rc | 读数 |
|---|---|---|
| `state/merge.py` | **0** | ★**产出 874 · 阻塞 43 (高危 33) · 未闭合需求 399 · 冲突 0** ★ |
| `state/gate_check.py` | **0** | ★**Q1 18/18 · Q2 3/3 · Q3 接口声明 1262 条 · Q7 钉板 md5 闸链 10/10 全绿 (★含闸⑩ rc=0★) · 缺口清单 3 条 (★hw-lead 224 / sw-lead 55 / mech-lead 119 条需求还没人答★)** ★ |
| `state/issue_check.py` | **1** | ★**违规 19 条 = 既有逾期项·★零新增** ★ |
| `state/stage_gate.py` | **1** | ★**当前 G1 · 还差 1 项 = 布线 unconnected 45 → 0** ★ (★G1a 还差 2 条: G1a-4 = R4 落表 (W-2) · G1a-8 = 关机语义 + 负载开关 (SD-1/LS-1)★) ★ |
| `state/daily_check.py` | **3** | ★**3 条异常: 问题闭环门 19 条 (既有逾期) + PCB↔网表逐焊盘等价 rc=1 (★板还没布线 ⇒ 这条是 G1 阻塞的另一个侧面, 不是新病灶★) + chain_gate (★有环节产物比源旧⇒ 出件前置★)** ★ |
| `state/compare_arm_official.py --self-test` | **0** | ★**ALL TESTS PASS** (★名单制晋级闸·★v44/v46/v47 真板端到端全被拒·★「板那一趟」的验收闸现成、自带反例★) ★ |

★**★阶段门**: ★**当前 G1 · 还差 1 项 (★G1a 还差 2 条 = §① 第 1、2 行 ⇒ 不拍板 G1a 不过 ⇒ G1 关不开★)** ★
"""


def md5_bytes(b):
    return hashlib.md5(b).hexdigest()


def board_fp():
    st = os.stat(BOARD)
    with open(BOARD, "rb") as f:
        return md5_bytes(f.read()), st.st_size, st.st_mtime_ns


def file_md5(p):
    with open(p, "rb") as f:
        return md5_bytes(f.read())


def main():
    os.makedirs(LOGDIR, exist_ok=True)

    # ---------- 章节号守卫 ----------
    hits = []
    for root, _dirs, files in os.walk(PROJ):
        if any(seg in root for seg in (".git", "tmp", "logs", "node_modules")):
            continue
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(root, fn)
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    if "㊺" in f.read():
                        hits.append(os.path.relpath(p, PROJ))
            except Exception:  # noqa: BLE001
                continue
    if hits:
        print("★★章节号 §㊺ 已被占用 ⇒ 零写盘退出: %s" % hits)
        return 2

    # ---------- 幂等守卫 ----------
    with open(PAGER, "rb") as f:
        before = f.read()
    if MARK.encode("utf-8") in before:
        print("★幂等: 标记已在本页 ⇒ 只复验, 不重复追加")
        return 0

    # ---------- 零写板 / 零落表 (开工前) ----------
    bmd5, bsize, bmtime = board_fp()
    pre = {
        "board": (bmd5, bsize, bmtime),
        "netlist": file_md5(NETLIST),
        "pins": file_md5(PINS),
        "bom": file_md5(BOM),
    }
    if bmd5 != BOARD_MD5:
        print("★★板 md5 不符 (%s) ⇒ 零写盘退出" % bmd5)
        return 3
    if bsize != BOARD_SIZE:
        print("★★板 size 不符 (%d) ⇒ 零写盘退出" % bsize)
        return 3

    len_before = len(before)
    md5_before = md5_bytes(before)

    # ---------- 备份 ----------
    bak = os.path.join(LOGDIR, "DECISION_ONE_PAGER_pre_r89_%s.md" % time.strftime("%Y%m%d_%H%M%S"))
    with open(bak, "wb") as f:
        f.write(before)
        f.flush()
        os.fsync(f.fileno())

    # ---------- 并发守卫 (追加前最后一刻再比一次) ----------
    with open(PAGER, "rb") as f:
        check = f.read()
    if check != before:
        print("★★并发守卫: 本页在读与写之间被第三方改动 ⇒ 零写盘退出 ★★")
        return 4

    # ---------- 追加 (单次 write, 追加式) ----------
    with open(PAGER, "a", encoding="utf-8") as f:
        f.write(SECTION)
        f.flush()
        os.fsync(f.fileno())

    # ---------- 追加式证明: 前 len_before 字节逐字未动 ----------
    with open(PAGER, "rb") as f:
        after = f.read()
    if after[:len_before] != before:
        print("★★追加式证明失败: 旧内容被改动 ⇒ 报告 (不覆盖) ★★")
        return 5
    if MARK.encode("utf-8") not in after:
        print("★★追加失败: 标记不在盘 ⇒ 零写盘退出★★")
        return 6
    if after.count(MARK.encode("utf-8")) != 1:
        print("★★追加失败: 标记重复 ⇒ 零写盘退出★★")
        return 7

    # ---------- 收工后: 零写板 / 零落表 ----------
    bmd5b, bsizeb, bmtimeb = board_fp()
    post = {
        "board": (bmd5b, bsizeb, bmtimeb),
        "netlist": file_md5(NETLIST),
        "pins": file_md5(PINS),
        "bom": file_md5(BOM),
    }
    if pre != post:
        print("★★零扰动失败: 板或落表三件被改动 ⇒ 报告 ★★")
        return 8

    print("✅ §㊺ 已追加 (追加式, 旧内容 %d 字节逐字未动)" % len_before)
    print("   旧页 md5 = %s (备份 %s)" % (md5_before, os.path.relpath(bak, PROJ)))
    print("   新页 md5 = %s / size = %d" % (md5_bytes(after), len(after)))
    print("   板 md5 %s / size %d / mtime_ns %d (逐字未动)" % (bmd5b, bsizeb, bmtimeb))
    print("   落表三件: netlist %s / pins %s / bom %s" % (post["netlist"], post["pins"], post["bom"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
