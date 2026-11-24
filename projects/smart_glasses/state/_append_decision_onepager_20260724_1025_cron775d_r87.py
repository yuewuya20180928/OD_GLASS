#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_append_decision_onepager_20260724_1025_cron775d_r87.py
=========================================================
★cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-24 10:25 · §㊶ 追加式★★

★★【★★本节做什么★★】★★
① ★★就地订正 §㊵ (09:4x) 的根因结论★:
   ★**§㊵ 写「本轮 0 派的根因 = 队列真空 (三个总工 open=0 且 fixing=0)」** ⇒ ★**10:2x 实测已不成立** ★
   ★**现在: 三个总工各占 1 条 `fixing` (ISS-387/388/389) ⇒ `internal` 必为 0 的根因回到「槽位被占」★**
   ★**⇒ 老板读 §㊵ 会误读成「没人干活」⇒ 而实况是三个 agent 全有运行中会话★** ★★

② ★★主线新风险: ISS-387 / ISS-389 处于「内容已出、交卷未闭」半开状态★★
   (★真相页/闸已在盘 · ★交卷页 + 分片未落 ⇒ ★兄弟 job fb67af40 10:39 轮负责派 cont1 补齐★)

③ ★★「板那一趟」的晋级判据仍武装★: `state/compare_arm_official.py --selftest` ★**ALL TESTS PASS**★
   (★名单制 · ★v44/v46/v47 真板端到端三条反向用例全过⇒ 「板只改一次」那一趟的验收闸不是空的★)

④ ★★老板待拍板清单 53 条覆盖复核: 一页 21 · 索引 41 · 并集 53 ⇒ ★★53/53 零漏项★

★★【★★纪律 (★本脚本自己守★)】★★
  ① 零写板 (板 md5/mtime/size 三项开工前后各打一次, 纳秒级比)
  ② 零落表 (网表/脚表/BOM 一字不改)
  ③ 零改既有闸 / 零改既有页面正文 (★只追加本页★)
  ④ ★**不改 `state/issue_log.yaml` / 不写任何分片** (★签收是 main 的地界★)
  ⑤ 不代老板拍板 (★只给「建议默认值」·★标明不是已决定★)
  ⑥ 零外发 (老板 2026-11-12 02:02 政策: 不再发信, 全靠自己查资料)
  ⑦ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑧ 幂等守卫: 标记已在本页 ⇒ 只复验, 不重复追加
  ⑨ 追加式证明: 旧内容 md5 (前 len_before 字节) 前后逐字相同
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

PAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
INDEX = os.path.join(PROJ, "DECISION_INDEX_2026-11-18.md")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
LOGD = os.path.join(PROJ, "logs/cron775d_r87")
STAMP = time.strftime("%Y%m%d_%H%M%S")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_SIZE = 4940213

MARK = "㊶ 【2026-11-24 10:2x · 追加式】"

SECTION = """
## ★★㊶ 【2026-11-24 10:2x · 追加式】★ ★★§㊵ (09:4x) 的根因结论【就地订正】: 「队列真空」→ 「槽位被占」 (★三个总工各占 1 条 `fixing` · 三个 agent 全有运行中会话★) + ★★主线新风险: ISS-387 / ISS-389「内容已出、交卷未闭」半开状态★★ + ★★「板那一趟」的晋级判据仍武装 (★名单制 · 12 条反向用例全过★)★★

★**① 本轮实读 (★`state/advance.py --json` · ★10:2x 本机实跑·★rc=1 是正常信号不是错误★)★**

| 段 | 条数 | 说明 |
|---|---|---|
| internal | **0** | ★**根因 = 三个槽位各被一条 `fixing` 占着 (★不是「没活」·★详见 §②★)** ★ |
| approvals | **0** | ★**恒空 (老板 2026-11-12 02:02「不再发信, 全靠自己查资料」政策)** ★ |
| decisions | **53** | ★**hw.yaml 13 · mech.yaml 16 · pm.yaml 12 · sw.yaml 13** ★ (★与 §㊵ 同为 53 条·★零新增·★零减少★) ★ |
| waiting | **0** | — |

★**台账侧实读 (★`state/issue_log.yaml` 384 条逐 owner 统计·★本机实读★)★**

| owner | open | fixing | verified | closed |
|---|---|---|---|---|
| hw-lead | **0** | **1** (ISS-387) | 79 | 25 |
| sw-lead | **0** | **1** (ISS-388) | 78 | 10 |
| mech-lead | **0** | **1** (ISS-389) | 68 | 14 |
| main | 11 | 0 | 20 | 32 |
| boss | 5 | 0 | 2 | 7 |

★**② ★★就地订正 §㊵ 的根因结论 (★老字一字未删·★只在此就地标注★)★**

★**§㊵ (09:4x) 写的是**: ★**「本轮 0 派的根因第一次变成『队列真空』(不是被占槽·不是撞车)」** ★
★**10:2x 实测: 这条结论【已过期】** ⇒ ★**`fixing` 从 0 变回 3 (ISS-387/388/389 三条同时在飞) ⇒ 根因回到「槽位被占」** ★

★**为什么这条订正重要 (★给老板看的那一句★)**: ★**§㊵ 的原话会让老板读成「三个总工都没活干·项目停摆」** ⇒ ★**而实况恰恰相反: 三个 agent 全部有运行中写会话 (★`sessions_list` 实跑: hw-lead `68f65987` / sw-lead `queue_iss381` + `d67efde7` / mech-lead `queue_iss382`·★最后活动都在 02:13~02:18Z★)** ⇒ ★**`internal: []` = 「三个槽位都被占着」≠「没活」** ★ ★

★**⇒ 本 job 本轮【派 0 条】是纪律执行的结果, 不是停滞**: ★**「一个 agent 同时只允许一个写会话」(★R18 压测实证 12%~38% 合并丢失★)⇒ 槽位被占就不叠新单** ★ ★
★**⇒ 下一轮能否有活 = 取决于 ISS-387/388/389 三条何时交卷签收 (★签收 = main 的地界★) + 兄弟 job `fb67af40` 是否开新单** ★★**本 job 不越界开单 (★同队列撞车·先例见 §㊲★)** ★

★**③ ★★主线新风险: ISS-387 / ISS-389 处于「内容已出、交卷未闭」的半开状态★★**

★**判据 (★本 job 立·★可复用★)**: ★**「内容页在盘」≠「这一单交付完了」** ⇒ ★**交卷页 + 分片两件没落 ⇒ 这一单就不能算交卷** ★

| ISS | agent | 会话 | 盘上产物 (★本机实读★) | 缺什么 |
|---|---|---|---|---|
| ISS-387 | hw-lead | `5170b697` (09:45 起) | ★`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` 44,122 B @10:10 ★ | ★`HANDOFF/2026-11-24_hw-lead_ISS387_*.md` 未落盘 · ★`state/fragments/hw.yaml` (★mtime 08:55★) 无 ISS-387 登记 ★ |
| ISS-388 | sw-lead | `d67efde7` (09:45 起) | — | ★**会话仍在跑 (★正常·★还在干★)** ★ |
| ISS-389 | mech-lead | `c6a0fb40` (09:45 起) | ★`MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` 65,851 B @10:08 + ★`MECH/check_debug_seat_rework_spec.py` 47,102 B @10:08 ★ | ★`HANDOFF/2026-11-24_mech-lead_ISS389_*.md` 未落盘 · ★`state/fragments/mech.yaml` (★mtime 08:57★) 无 ISS-389 登记 ★ |

★**归属**: ★**兄弟 job `fb67af40` (队列自动派活) 已在 10:09 的轮次里明确登记: 「下一轮 (10:39) 若发现这两个 agent 的剩余会话已退出, 应派【cont1 续派】把交卷页 + 分片补齐」** ⇒ ★**本 job 不重复派 (★同 agent 两条写会话 = R18 覆盖风险★)** ★
★**★本 job 盯的一件事 (★不动手·只盯★)**: ★**若 10:39 那轮过去后 ISS-387/389 仍是「交卷页未落盘」, 说明续派没生效 ⇒ ★那才是本 job 该升级的信号 (★升级给谁 = 老板 / 兄弟 job★)** ★ ★

★**④ ★★「板那一趟」的晋级判据仍武装 (★本轮实测·★不是抄任何 agent 报告★)★★**

★**`python3 state/compare_arm_official.py --self-test` ⇒ ★★rc=0 · ALL TESTS PASS★★** (★10:2x 本机实跑·★差分对清单实载 22 对★)

★**12 条用例逐条过 (★摘要★)**: ★**v44 被拒 (退铜 9 网 + 差分死腿 1 对) · v46 被拒 (★计数全平 26=26/11=11 但退铜 10 网 + 差分死腿 3 对⇒ 靠名单才抓得到★) · v47 被拒 (退铜 6 网 + 差分死腿 1 对) · 真变好⇒放行 · 打死差分腿⇒拒 (Δ超差对数假降) · 无改善⇒拒 · DRC≠0⇒拒 · 任一计数指标变差⇒拒 · 「补好一条+拆碎一条」总数持平⇒拒 (逐网孤岛名单抓到) · 实测坏板 `_reroute2` ⇒ 名单制闸拒 (I2C_A_SCL / I2C_A_SDA / ID_DETECT_1 / RESET_N / USB_D_N_SRC)** ★

★**⇒ 含义 (★为什么这条值得单独记一页★)**: ★**「板只改一次」那一趟的验收闸不是空的、也不是后来补的临时脚本** ⇒ ★**它【现在】就是武装状态** ⇒ ★**那一趟真开工时, 「这个臂比现状好」的判据是现成的、可跑的、自带 12 条反向用例的** ★ ★
★**★铁律复述 (★`MEMORY.md` 2026-11-06 02:2x 实测事故留下★)**: ★**「unconnected 变少」≠「板子更好」** ⇒ ★**必须同时看 零铜网数 + 差分单边零铜对数 + 退铜名单 + 差分死腿名单** ⇒ ★**「Δ 数字变小」也可能是坏事 (打死一条差分腿 ⇒ 它从「Δ超差」桶移到「单边零铜」桶 ⇒ Δ 假性下降)** ★★

★**⑤ ★★本轮零派 / 零外发 / 零落表 / 零写板 / 巡检实测★★**

★**零派**: ★**internal = 0 ⇒ 派 0 条 · 跳过 3 条 (ISS-387/388/389 · 原因 = 槽位被占 + 三个 agent 全有运行中会话)** ★
★**零外发**: ★**`state/outbox/` 17 份草稿只备不发 (★老板 2026-11-12 02:02 政策·★`NO_OUTBOUND_POLICY.md` 已立★) ⇒ 0 封发送 · 0 次联系供应商 · 0 张采购单** ★
★**零落表**: ★**网表 / 脚表 / BOM 三件 md5 前后逐字节相同** ★
★**零写板**: ★**板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★
★**零并发改台账**: ★**本 job 不改 `state/issue_log.yaml` / 不写任何分片** ★
★**巡检实测 rc (★本机实跑·★`tail` 不吞退出码★)**: ★**`merge` rc=0 · `gate_check` rc=0 (Q1 18/18 · Q7 钉板闸 10/10) · `issue_check` rc=1 (19 条 = 既有逾期项·★零新增★) · `stage_gate` rc=1 (G1 未过 · 还差 1 项) · `daily_check` rc=3 (★PCB↔网表逐焊盘等价 rc=1 + chain_gate 两条 = 老异常·★非本轮引入★)** ★
★**老板待拍板清单覆盖复核**: ★**53 条 · 一页命中 21 · 索引命中 41 · 并集 53 ⇒ ★★53/53 零漏项★** ★
★**板框第一问仍未答**: ★**(甲 160×100 台架板 / 乙 60×30 产品板) ⇒ 落点坐标 / 清空区放大量的一切前提都挂在它身上 ⇒ 本页不代拍** ★
"""


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def board_fp():
    st = os.stat(BOARD)
    return md5(BOARD), st.st_mtime_ns, st.st_size


def sh(cmd):
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    print("=" * 92)
    print("★ cron 775d9893 · 2026-11-24 10:25 · §㊶ 追加式 (根因订正 + 半开状态 + 晋级判据武装)")
    print("=" * 92)
    os.makedirs(LOGD, exist_ok=True)

    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-58s %s" % ("✅" if good else "❌", name, detail))

    m0, ns0, sz0 = board_fp()
    chk("板 md5 / size (开工前)", m0 == BOARD_MD5 and sz0 == BOARD_SIZE,
        "%s / %d" % (m0[:12], sz0))

    with open(PAGER, encoding="utf-8") as f:
        before = f.read()
    before_md5 = hashlib.md5(before.encode("utf-8")).hexdigest()
    before_len = len(before)

    if MARK in before:
        print("  ✔ 幂等: §㊶ 已在本页 (不重复追加)")
        print("    当前长度 %d" % before_len)
        return 0

    # ---- 阶段 1 · 独立复核 (fail-closed) ----
    rc, o = sh("python3 state/advance.py --json")
    try:
        j = json.loads(o)
    except Exception:
        print("  ★ advance.py 输出解析失败 ⇒ 零写盘退出")
        return 2
    keys = [d["key"] for d in j["decisions"]]
    with open(INDEX, encoding="utf-8") as f:
        idx = f.read()
    hp = [k for k in keys if k in before]
    hi = [k for k in keys if k in idx]
    un = [k for k in keys if k not in before and k not in idx]
    chk("decisions 段 = 53 条", len(keys) == 53, "%d 条" % len(keys))
    chk("★覆盖并集 53/53 · 零漏项★", len(set(hp) | set(hi)) == 53 and not un,
        "一页 %d · 索引 %d · 并集 %d · 漏 %d" % (len(hp), len(hi), len(set(hp) | set(hi)), len(un)))
    chk("internal = 0", len(j["internal"]) == 0, "internal=%d" % len(j["internal"]))
    chk("approvals = 0 (★恒空·不发信政策★)", len(j["approvals"]) == 0, "approvals=%d" % len(j["approvals"]))
    chk("waiting = 0", len(j["waiting"]) == 0, "waiting=%d" % len(j["waiting"]))

    # 台账侧: 三个总工 fixing 各 1 (ISS-387/388/389)
    import yaml
    with open(os.path.join(PROJ, "state/issue_log.yaml"), encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    iss = doc.get("issues") or list(doc.values())
    fix = [i for i in iss if i.get("status") == "fixing"]
    chk("★台账 fixing = 3 且 = ISS-387/388/389★",
        sorted(i.get("id") for i in fix) == ["ISS-387", "ISS-388", "ISS-389"],
        "%s" % sorted(i.get("id") for i in fix))
    chk("★三个总工名下 open = 0★",
        all(not [i for i in iss if i.get("owner") == ag and i.get("status") == "open"]
            for ag in ("hw-lead", "sw-lead", "mech-lead")),
        "hw/sw/mech open 均为 0")

    # 半开状态: 真相页在盘, 但交卷页 + 分片未落
    handoff_387 = [f for f in os.listdir(os.path.join(PROJ, "HANDOFF")) if "ISS387" in f]
    handoff_389 = [f for f in os.listdir(os.path.join(PROJ, "HANDOFF")) if "ISS389" in f]
    chk("★ISS-387 交卷页未落盘 (★半开状态成立·★归兄弟 job 10:39 轮★)",
        not handoff_387, "HANDOFF ISS387 命中 %d" % len(handoff_387))
    chk("★ISS-389 交卷页未落盘 (★半开状态成立·★归兄弟 job 10:39 轮★)",
        not handoff_389, "HANDOFF ISS389 命中 %d" % len(handoff_389))
    chk("★ISS-387 真相页在盘 (★内容已出★)",
        os.path.exists(os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md")),
        "BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md")
    chk("★ISS-389 真相页 + 闸在盘 (★内容已出★)",
        os.path.exists(os.path.join(PROJ, "MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md"))
        and os.path.exists(os.path.join(PROJ, "MECH/check_debug_seat_rework_spec.py")),
        "2 件")

    # 晋级判据武装
    rc, o2 = sh("python3 state/compare_arm_official.py --self-test")
    chk("★晋级判据 compare_arm_official --selftest 全绿★",
        rc == 0 and "ALL TESTS PASS" in o2, "rc=%d" % rc)
    with open(os.path.join(LOGD, "compare_arm_selftest.log"), "w", encoding="utf-8") as f:
        f.write(o2)

    # 零落表: 三张表 md5 (开工前实测)
    tables = {}
    for rel, exp in (("HW/netlist_v1.csv", "6aee500e60ba0732f83a9cf557ba90ab"),
                     ("HW/netlist_v1_pins.csv", "9174309df1ec9411ac8e8d9e80ee386a"),
                     ("HW/BOM_v1.csv", "5b9993992405904a60ac96a020b375d8")):
        p = os.path.join(PROJ, rel)
        tables[rel] = (md5(p), os.stat(p).st_mtime_ns)
        chk("★零落表 %s md5 = 基线★" % os.path.basename(rel),
            tables[rel][0] == exp, tables[rel][0][:12])

    # outbox 只备不发
    ob = os.path.join(PROJ, "state/outbox")
    drafts = [f for f in os.listdir(ob) if f.endswith(".md")
              and f not in ("README.md", "NO_OUTBOUND_POLICY.md")]
    chk("★outbox 草稿 17 份只备不发★", len(drafts) == 17, "%d 份" % len(drafts))

    if not ok:
        print("  ★★任一验收线不过 ⇒ 零写盘退出 (fail-closed)")
        return 2

    # ---- 阶段 2 · 写盘 (追加式 + 备份 + 旧内容逐字不变) ----
    bak = os.path.join(LOGD, "DECISION_ONE_PAGER_pre_r87_%s.md" % STAMP)
    shutil.copy2(PAGER, bak)
    print("  ✔ 备份 → %s" % os.path.relpath(bak, PROJ))

    with open(PAGER, "a", encoding="utf-8") as f:
        f.write(SECTION)

    # ---- 阶段 3 · 验收 ----
    with open(PAGER, encoding="utf-8") as f:
        after = f.read()
    chk("★追加成功: 长度 %d → %d★" % (before_len, len(after)), len(after) > before_len, "delta=%d" % (len(after) - before_len))
    chk("★标记已在本页 (★幂等标记★)", MARK in after, MARK[:24])
    chk("★旧内容逐字未动 (★追加式证明·前 %d 字节 md5 相同★)" % before_len,
        hashlib.md5(after[:before_len].encode("utf-8")).hexdigest() == before_md5,
        "prefix md5 %s" % before_md5[:12])
    if hashlib.md5(after[:before_len].encode("utf-8")).hexdigest() != before_md5:
        shutil.copy2(bak, PAGER)
        print("  ★★并发写盘冲突 ⇒ 已从备份回滚本页 (★零写盘状态★)")
        return 2

    m1, ns1, sz1 = board_fp()
    chk("★零写板 (板 md5/mtime/size 三项开工前后逐字同)★",
        m1 == m0 and ns1 == ns0 and sz1 == sz0, "%s / %d" % (m1[:12], sz1))
    for rel, (md, ns) in tables.items():
        p = os.path.join(PROJ, rel)
        chk("★零落表 %s 收工后仍同★" % os.path.basename(rel),
            md5(p) == md and os.stat(p).st_mtime_ns == ns, md5(p)[:12])

    print("  ✔ §㊶ 追加完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
