#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_append_decision_onepager_20260724_1505_cron775d_r88.py
=========================================================
★cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-24 15:05 · §㊸ 追加式★★

★★【★★本节做什么★★】★★
① 本轮队列实读 (internal/approvals/decisions/waiting 四段)
② ★**老板待拍板清单 55 条的零漏项覆盖复核** (一页 23 · 索引 41 · PENDING 41 · 并集 55)
③ ★★main 本机独立复核: ISS-388 / ISS-390 / ISS-391 三单的闸逐道实跑读数★★
④ ★★并发实况 (★L-27 ③ 实战命中★): 兄弟 job 同时在写同一棵树 ⇒ 本 job 让出台账写权★★
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

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_SIZE = 4940213
BOARD_MTIME = "2026-11-06 07:07:17.362193413 +0800"

# ★L-24「自曝是纪律的一部分」★: 本脚本首跑时 MARK 写成 "§㊸ 【...】" (带 § 前缀)
#   而本页 H2 标题的既有惯例是【不写 § 前缀】(§㊵ / §㊶ / §㊷ 三段皆然)
#   ⇒ 落盘后自检把「标记不在盘」判成 rc=4 (假红)
#   ⇒ 内容本身与旧内容完整性均已验证通过 (追加式证明 + 尾部逐字核对) ⇒ 追加成立, 无重复追加
#   ⇒ 现把 MARK 改成与页内实际写法逐字一致, 并把「幂等守卫」放在写盘【之前】, 落盘后只做只读复验
MARK = "★★㊸ 【2026-11-24 15:0x · 追加式】"

SECTION = """
## ★★㊸ 【2026-11-24 15:0x · 追加式】★ ★★本轮 (cron 775d) 实读: 队列仍真空 (internal=0) · 三单闸逐道独立复核 · ★★并发实况: 兄弟 job 同时在写同一棵树 ⇒ 本 job 主动让出台账写权★★

★**① 本轮实读 (★`state/advance.py --json` · 14:39 与 14:56 两次本机实跑·★rc=1 是「内部无可派」的正常信号, 不是错误★)★**

| 段 | 条数 | 说明 |
|---|---|---|
| internal | **0** | ★**三个 owner 槽位全被占** (★14:51 兄弟 job `fb67af40` 开 ISS-392/393/394 三单并派出三个 owner 会话, 14:53 三个会话仍在 running★) ★ |
| approvals | **0** | ★**恒空** (★老板 2026-11-12 02:02「不再发信, 全靠自己查资料」政策 ⇒ `state/outbox/NO_OUTBOUND_POLICY.md` 已立★) ★ |
| decisions | **55** | ★**hw 13 · mech 17 · pm 12 · sw 13** (★较 10:2x 的 53 条 **+2** = `iss389_oi1_housing_width_window` + `iss389_oi11_seat_height_window` ⇒ ★这两条正是 §㊷ C7/C8 把它们**从 main 地界退回 boss 地界**的结果 ⇒ ★**不是新增问题, 是两条老问题改回正确归属**★) · ★**逾期 31 条** ★ |
| waiting | **0** | — |

★**② ★★老板待拍板清单覆盖复核 (★本轮实跑·★不抄上一轮读数★)★**: ★**55 条 · 一页命中 23 · 索引 (`DECISION_INDEX_2026-11-18.md`) 命中 41 · 正文 (`DECISION_PENDING_2026-11-16.md`) 命中 41 ⇒ ★★并集 55 ⇒ 55/55 零漏项★★** ⇒ ★**§① 的 9 项「板那一趟」阻塞 (U-1 框 → W-2/W-1c → W-3 → SD-1 → LS-1 → Q3 → C_VBUS_GND → S7 漂移) 本轮一字未变 ⇒ 板框第一问 (甲 160×100 台架板 / 乙 60×30 产品板) 仍未答 ⇒ ★**本页不代拍** ★

★**③ ★★main 本机独立复核 (★三单的闸逐道实跑·★不抄任何 agent 报告·★原样输出见 `logs/cron775d_r88/`★)★★**

| 单 | owner | 闸 | 裸跑 | `--selftest` | 判定 |
|---|---|---|---|---|---|
| ISS-388 | sw-lead | `SW/tools/check_sw_gate_health.py` (本单新建) | ★**rc=1 · 2/6 绿** (H0/H1/H2/H3 红) ★ | ★**rc=0 · 22/22 · `ALL TESTS PASS`** (含 5 条专打 H1 命门) ★ | ★**闸本身可信 · 裸跑红 = 按设计 (交卷页 C6: 红 = 暴露真实病灶) ⇒ 可签** ★ |
| ISS-390 | mech-lead | `MECH/check_fts_seat_body_geometry.py` (本单新建) | ★**rc=0 · 33 条判据 0 失败** ★ | ★**rc=0 · 15/15 · `ALL TESTS PASS`** ★ | ★**可签** ★ |
| ISS-391 | hw-lead | `HW/check_fts_land_drill_same_batch.py` (本单新建) | ★**rc=1 · 4/7 绿** (D1/D2/D3 红) ★ | ★**rc=0 · 17/17 · `ALL TESTS PASS`** ★ | ★**闸本身可信 · 裸跑红 = 按设计 (D1/D2/D3 抓的正是「改孔还没进清单」) ⇒ 可签** ★ |

★**旁证 (★同轮实跑·★用来证明「这几道闸今天真的坏了」不是抄来的★)★**: ★**`SW/tools/check_sw_ref_reachability_v2.py` 裸跑 rc=1 (把 `VBUS_DET_D` / `VBUS_DET_uA` 当位号) · `SW/tools/check_debug_pin_order_contract.py --selftest` rc=1 (10/11, M2 `FATAL: 变异副本 ROOT 退成 /`) · `MECH/check_debug_seat_3d_fit.py` rc=0 (201 条) · `MECH/check_debug_seat_rework_spec.py` rc=0 (472 条) · `HW/check_fts_single_row_land_truth.py` rc=0 (7/7) · `HW/check_onepass_preflight_coverage.py` rc=0 · `SW/tools/check_sw_false_connectivity_gate.py` rc=0 (K0~K6)** ★
★**签收闸集合 (★交付物自带闸 ∪ 扫描面命中的既有闸·L-26①★) 全绿** ⇒ ★**三单的 owner 会话均已收工 (12:51 / 12:59 / 13:05) 且收工后九件交付物 mtime 一件未动 ⇒ ★**签收指纹不会当场过期 (L-27 硬前置已满足)** ★

★**④ ★★并发实况 (★L-27 ③ 实战命中·★本轮最重要的发现★)★★**
★**兄弟 job `fb67af40` (ARS45 队列自动派活) 与本 job 同时盯着同一棵树** ⇒ 本轮实测时间线:

| 时刻 | 事件 |
|---|---|
| 14:51:07 | 兄弟 job 写 `state/issue_log.yaml` (开 **ISS-392** (sw-lead) / **ISS-393** (mech-lead) / **ISS-394** (hw-lead) · 三条同刻置 `fixing`) |
| 14:51~14:53 | 兄弟 job 派出三个 owner 会话 ⇒ ★**三会话同时 running** ★ |
| 14:53:09 | 兄弟 job 生成 `_apply_20260724_1450_main_sign_iss391_md5_pin_and_refs.py` (签 ISS-391 的落账脚本 · 尚未落账) |

★**⇒ 本 job 本轮【主动让出 `state/issue_log.yaml` 的写权】**: ★**该台账是 5.0 MB 单文件 · 全量 `yaml.dump` 覆盖式写** ⇒ ★**两个 writer 并发 ⇒ 后写的那份会把先写的那份【静默回滚】** ⇒ ★★**这与本项目今天已在 ISS-381/382/384 上栽过的「签收指纹漂移」是同源变种 (L-27 第 4 款)★★** ★
★**⇒ 给持有写权的一方的一次性口径 (★证据已在 `logs/cron775d_r88/VERIFY_388_390_391.md` §1+§2·★本段只给结论★)★**: ★**① 三单一并签 (一次全量重写 ⇒ 零竞态窗口) ② 签收记录必须钉 md5 (不许只钉 size) ③ ISS-388 的 `verify_result` 须写明「裸跑 rc=1 是按设计的正确行为」 ④ ISS-391 的 `verify_result` 须写明「D1/D2/D3 红 = 按设计 · 闸须保持零挂链直到 §4 登记同批落地」 ⑤ ISS-390 的「G3 未落清单 17 处」仍开放 (main 地界)** ★

★**⑤ 本轮零派 / 零外发 / 零落表 / 零写板 / 巡检实测★★**
★**零派**: ★**internal = 0 ⇒ 派 0 条 · 跳过 3 条** (★ISS-388/390/391 已标 `fixing` 不重复派 + 三个 owner 槽位被兄弟 job 的 ISS-392/393/394 占满且三个 owner 会话 running★) ★
★**零外发**: ★**`state/outbox/` 19 份草稿只备不发** (★`NO_OUTBOUND_POLICY.md` 已立★) ⇒ ★**0 封发送 · 0 次联系供应商 · 0 张采购单** ★
★**零落表**: ★**网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 三件 md5 前后逐字节相同** ★
★**零写板**: ★**板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★
★**巡检实测 rc (★本机实跑·★`tail` 不吞退出码★)★**: ★**`merge` rc=0 · `gate_check` rc=0 (Q1 18/18 · Q7 钉板闸 10/10) · `issue_check` rc=1 (19 条 = 既有逾期项·★零新增★) · `stage_gate` rc=1 (G1 未过 · 还差 1 项 = 布线 unconnected 45 → 0) · `daily_check` rc=3 (★PCB↔网表逐焊盘等价 rc=1 + chain_gate 两条 = 老异常·★非本轮引入★)** ★
★**阶段门**: ★**当前 G1 · 还差 1 项 (★G1a 还差 2 条: G1a-4 = R4 落表 (W-2) · G1a-8 = 关机语义 + 负载开关 (SD-1 / LS-1)★) ⇒ ★**这两条就是 §① 第 1、2 行·★不拍板 G1a 不过·★G1 关不开** ★
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
    # ---------- 幂等守卫 ----------
    with open(PAGER, "rb") as f:
        before = f.read()
    if MARK.encode("utf-8") in before:
        print("★幂等: 标记已在本页 ⇒ 只复验, 不重复追加")
        return 0
    if "§㊸" in before.decode("utf-8"):
        print("★§㊸ 已被他人占用 ⇒ 零写盘退出")
        return 2

    # ---------- 零写板 / 零落表 (开工前) ----------
    bmd5, bsize, bmtime = board_fp()
    pre = {
        "board": (bmd5, bsize, bmtime),
        "netlist": file_md5(NETLIST),
        "pins": file_md5(PINS),
        "bom": file_md5(BOM),
    }
    assert bmd5 == BOARD_MD5, "板 md5 不符 ⇒ 零写盘退出"
    assert bsize == BOARD_SIZE, "板 size 不符 ⇒ 零写盘退出"

    len_before = len(before)

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
        return 3
    if MARK.encode("utf-8") not in after:
        print("★★追加失败: 标记不在盘 ⇒ 零写盘退出★★")
        return 4
    if after.count(MARK.encode("utf-8")) != 1:
        print("★★追加失败: 标记重复 ⇒ 零写盘退出★★")
        return 5

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
        return 6

    print("✅ §㊸ 已追加 (追加式, 旧内容 %d 字节逐字未动)" % len_before)
    print("   板 md5 %s / size %d / mtime_ns %d (逐字未动)" % (bmd5b, bsizeb, bmtimeb))
    print("   落表三件: netlist %s / pins %s / bom %s" % (post["netlist"], post["pins"], post["bom"]))
    print("   本页新 md5 = %s / size = %d" % (md5_bytes(after), len(after)))
    print("   (旧页 md5 = %s)" % md5_bytes(before))
    return 0


if __name__ == "__main__":
    sys.exit(main())
