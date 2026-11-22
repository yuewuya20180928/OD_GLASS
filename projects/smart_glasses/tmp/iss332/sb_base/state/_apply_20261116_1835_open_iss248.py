#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (775d9893 继续执行后继计划) 2026-11-16 18:3x: 新开 ISS-248 (SW 侧判据口径收口)
=========================================================================================
★**本脚本只做一件事**: 在 `state/issue_log.yaml` 里追加一条 ISS-248 (owner=sw-lead · status=open)
  ★**不改任何已有 issue 的字段** (★一条都没改★) ★
  ★**不碰任何真源 / 分片 / 板 / 网表 / 判据脚本** ★
  ★**写盘方式 = 锁 + 备份 + 临时文件 + os.replace (原子)** ★

★**为什么开这一单 (★main 2026-11-16 18:2x~18:3x 自己实跑核出来的, 不抄任何交卷报告★)** ★
★**① 病灶 (main 本机实跑, 原样输出)**: ★
· `python3 SW/tools/timing_check.py` ⇒ ★**rc=0 · SELFTEST 71/71 通过** ★ (★权威判据没坏★)
· `python3 SW/tools/timing_check.py --reverse-demo` ⇒ ★**rc=1** ★
  末行: ★**「反向演示: ❌ 没变红 ⇒ 有问题」** ★
  中段: ★**「改坏: 从副本里删掉 U_PWR_SW 全部行 ⇒ 改后: 装机开关数 rail_switching_devices = 1 (基线 2)
  ⇒ 断电主开关判据 未变红」** ★
★**② 根因 = 【演示段的期望值过期】(★不是权威判据坏了★)**: ★
· 权威判据 (★同文件★) `L1573~L1576` REV-3 明写: ★**删掉 U_PWR_SW 后必须掉到 1 (不是 0)** ★
  且断言就是 `mo["F8_power_off"]["rail_switching_devices"] == 1` ★
· `L1594~L1597` REV-3b: 两个都删 ⇒ 0 (★不受影响★) ★
· 但 `--reverse-demo` 演示段的 `L1742` (打印文案) + `L1762` (聚合 ok 判据) 仍写 `== 0` ★
  ⇒ ★**演示段永远判「没变红」⇒ rc=1** ★
★**③ 与锚点无关 (★ISS-245 已做隔离实测★)**: 把 §1 锚点 md5 改回旧值, `--reverse-demo` 仍是 rc=1 ★
★**④ 与本单的关系**: ISS-245 (sw-lead) 交卷时实测到并登记 need `iss245_reverse_demo_stale_agg` (to=main) ★
  ⇒ ★**本单 = 把那条 need 变成一条可执行单 (★sw-lead 名下当前没有 open 单, 且无运行中的写会话★)** ★
★**⑤ 附带一条派活口径订正 (★ISS-245 实测发现的★)**: `timing_check.py` ★**没有 `--selftest` 这个 flag** ★
  (argparse rc=2) ⇒ ★**它的 71 条 selftest 就是默认路径, 裸跑即 71/71** ⇒ ★**brief 里不许写 `--selftest`★ ★
"""

import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_1835_open_iss248"
TODAY = "2026-11-16"

BRIEF = """★★**目标 (★内部活·不是 PCB 布线/布局类·不是老板级拍板★)**: 把 ★**`SW/tools/timing_check.py --reverse-demo` 从 rc=1 拉回 rc=0**★ ⇒ ★**只准改【演示段】那 2 处过期期望值 (★判据逻辑 0 改动★)★** ⇒ ★**零落表 · 零外发 · HW/ 与 MECH/ 0 字节写入**★

★★**① 病灶 (★main 2026-11-16 18:2x 本机实跑, 原样输出★)** ★★
· `python3 SW/tools/timing_check.py` ⇒ ★**rc=0 · 「SELFTEST 71/71 通过, rc=0」** ★ (★**权威判据没坏**★)
· `python3 SW/tools/timing_check.py --reverse-demo` ⇒ ★**rc=1** ★
  · 末行: ★**「反向演示: ❌ 没变红 ⇒ 有问题」** ★
  · 中段: ★**「改坏: 从副本里删掉 U_PWR_SW 全部行 ⇒ 改后: 装机开关数 rail_switching_devices = 1 (基线 2) ⇒ 断电主开关判据 未变红」** ★
★**② 根因 = 【演示段的期望值过期】(★不是权威判据坏了★)** ★★
· ★**权威判据在同一个文件里**★: `L1573~L1576` REV-3 明写 ★**「删掉 U_PWR_SW 后必须掉到 1 (不是 0)」**★ 且断言就是 ★**`mo["F8_power_off"]["rail_switching_devices"] == 1`** ★
· `L1594~L1597` REV-3b (两个都删 ⇒ 0) ★**不受影响** ★
· ★**但 `--reverse-demo` 演示段的 `L1742` (打印文案里的判红条件) + `L1762` (聚合 ok 判据) 仍写 `== 0`** ★ ⇒ ★**演示段永远判「没变红」⇒ rc=1** ★
· ★**与锚点无关 (★ISS-245 已做隔离实测★)**: 把 §1 锚点 md5 改回旧值, `--reverse-demo` 仍是 rc=1 ⇒ ★**不是锚点过期, 是演示段自己过期** ★

★★**③ 修法 (★只准动这 2 处 + 必要的打印文案, 别的一个字都不许动★)** ★★
· `L1762` 的 ★**`and mut2["F8_power_off"]["rail_switching_devices"] == 0`** ⇒ ★**改成 `== 1`** ★
· `L1742` 的打印条件 (`"❌变红" if ... == 0 else "未变红"`) ⇒ ★**同步改成 `== 1`** ★ (★不然打印出来会自相矛盾★)
· ★**判据逻辑 0 改动 (★以下不许动★)**: ★**`L1453~L1455` 的 helper · `L1568~L1576` 的 REV-3 · `L1594~L1597` 的 REV-3b · 71 条 selftest 一条不许删** ★
· ★**不许动 `SW/SW_MD5_BASELINE_LEDGER.md` 一行** (★它是 md5 锚点账, 与本单无关; 锚点已是 ISS-243 落表后的真值★) ⇒ ★**留痕写交卷单 + 分片** ★
· ★**零落表**: ★**网表 / 脚表 / BOM / `.net` / 板 / 原理图 一个字都不许改** ★

★★**④ 验收 (★全部实跑, 原样贴进交卷单 B5★)** ★★
1. `python3 SW/tools/timing_check.py` ⇒ ★**rc=0 · 「SELFTEST 71/71 通过, rc=0」** ★
   ★★**派活口径订正 (★ISS-245 实测发现★)**: ★**该脚本【没有】`--selftest` 这个 flag** ★ (argparse rc=2) ⇒ ★**它的 71 条 selftest 就是默认路径, 裸跑即 71/71** ⇒ ★**本单不许写 `--selftest` 进验收命令** ★
2. `python3 SW/tools/timing_check.py --reverse-demo` ⇒ ★**rc=0** 且末行必须是 ★**「反向演示: ✅ 变红 ⇒ 它真在读网表 (不是演常量)」** ★
3. `python3 SW/tools/check_demo_panel_spec.py` ⇒ ★**rc=0** (★ISS-245 已转绿, 不许被改红★)
4. `python3 SW/tools/check_demo_panel_spec.py --selftest` ⇒ ★**rc=0 · 16/16** (★REV-9~REV-15 反向用例一条没删★)
5. `python3 state/merge.py && python3 state/gate_check.py` ⇒ ★**rc=0 · 【Q1】18/18** ★
6. ★**受保护 md5 逐字节不变 (main 本机 md5sum 实测基线)**: 网表 `611c3ba3…` · 脚表 `ef436a37…` · BOM `2a730574…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` · `SW/SW_MD5_BASELINE_LEDGER.md` ★
7. ★**反向自证 (★必做项, 不做不算交卷★)**: 在 ★**/tmp 沙盒副本**★ 上把改后的 `L1762` 改回 `== 0` ⇒ ★**`--reverse-demo` 重新 rc=1 (末行回到「❌ 没变红」)**★ ⇒ 装回 ⇒ ★**rc=0** ⇒ ★**证明这条断言不是摆设** ★ (★沙盒做完清掉★)

★★**⑤ 交付物 (3 件)** ★★
1. ★**交卷单**: `HANDOFF/2026-11-16_sw-lead_ISS248_reverse-demo演示段口径对齐.md` (★**B1~B6 六块齐全**★: 结论摘要 / 验收标准自评 / 证据分级 / 接口取值声明 / 未决项与卡点 / 自证复现命令) ⇒ ★**`gate_check` 按标题关键词认块 ⇒ 标题必须真的带这 6 个语义, 不许只写 B1/B2★** ★
2. ★**分片**: `state/fragments/sw.yaml` ⇒ ★**只走 `python3 state/frag_write.py --agent sw-lead ...` 原子写 (★禁止 `open(p,"w")`★)** ⇒ 至少 +1 artifact / +1 claim / +1 need(to=main, ★若有★) ⇒ ★**别人的 key 一个都不许删改** ★
3. ★**留痕**: 落表台账 / 锚点账 ★**一个字都不许动** ⇒ 留痕全在交卷单 + 分片里 ★

★★**⑥ 边界 (★逐条自证★)** ★★
· ★**零落表** (网表/脚表/BOM/板/原理图 0 字节写入) · ★**零外发** (★一次邮件/询价/采购都不许发★) · ★**零实物 (本单全部 [实测], [实测] 条数 = 0)** ★
· ★**不碰 `HW/` · 不碰 `MECH/` · 不碰别人的分片** · ★**不碰 `state/issue_log.yaml` (★verify_by=main, status 留给 main 落 verified★)** ★
· ★**不碰 `PROJECT_TRACKER.md` §0** · ★**不碰 `SW/tools/check_demo_panel_spec.py`** · ★**不碰 `SW/SW_MD5_BASELINE_LEDGER.md`** ★
· ★**不许替老板拍板 (★本单不涉老板级项★)** ★
"""

ISS = {
    "id": "ISS-248",
    "title": ("★★[主线内·SW 侧·判据口径收口·内部活] ★★`SW/tools/timing_check.py --reverse-demo` rc=1 "
              "(★末行「反向演示: ❌ 没变红 ⇒ 有问题」· 演示段还判 `rail_switching_devices == 0`· "
              "★ISS-235 已把 REV-3 基线翻正成 2→1 ⇒ **权威判据 (REV-3/REV-3b) 是对的, 过期的是演示段**★) "
              "⇒ 把演示段 L1742/L1762 对齐到权威口径 (== 1) + 订正派活口径 (`--selftest` flag 不存在, 71/71 是默认路径)"),
    "severity": "medium",
    "source_blocker": "ISS-245",
    "source_agent": "main",
    "desc": ("★main 2026-11-16 18:2x~18:3x **自己实跑核出来的** (★不抄任何交卷报告★) ★\n"
             "★**① 病灶**: `python3 SW/tools/timing_check.py` ⇒ **rc=0 · SELFTEST 71/71 通过** (权威判据没坏) ; "
             "`python3 SW/tools/timing_check.py --reverse-demo` ⇒ **rc=1** · 末行「反向演示: ❌ 没变红 ⇒ 有问题」· "
             "中段「删掉 U_PWR_SW 全部行 ⇒ 装机开关数 rail_switching_devices = 1 (基线 2) ⇒ 断电主开关判据 未变红」\n"
             "★**② 根因 = 演示段期望值过期 (不是判据坏, 不是锚点过期)**: 同文件 `L1573~L1576` REV-3 明写"
             "「删掉 U_PWR_SW 后必须掉到 1 (不是 0)」且断言就是 `== 1` ; `L1594~L1597` REV-3b (两个都删 ⇒ 0) 不受影响 ; "
             "而 `--reverse-demo` 演示段 `L1742` (打印文案) + `L1762` (聚合 ok 判据) 仍写 `== 0` ⇒ 演示段永远判「没变红」\n"
             "★**③ 与锚点无关**: ISS-245 已做隔离实测 (锚点 md5 改回旧值 ⇒ `--reverse-demo` 仍 rc=1)\n"
             "★**④ 来源**: ISS-245 (sw-lead) 交卷时实测到并登记 need `iss245_reverse_demo_stale_agg` (to=main) ⇒ "
             "★**本单 = 把那条 need 变成一条可执行单 (sw-lead 名下当前无 open 单、无运行中的写会话)**\n"
             "★**⑤ 附带订正派活口径**: `timing_check.py` **没有 `--selftest` 这个 flag** (argparse rc=2) ⇒ "
             "它的 71 条 selftest 就是默认路径, 裸跑即 71/71 ⇒ brief 里不许写 `--selftest`"),
    "owner": "sw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-20",
    "status": "open",
    "external": False,
    "need_keys": [],
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "note": ("★main 2026-11-16 18:3x 开单 (job 775d9893「继续执行后继计划」): advance.py 的 internal 段为空 "
             "(hw-lead ISS-247 / mech-lead ISS-246 各自 fixing 在飞, sw-lead 名下无 open 单) ⇒ "
             "★**本单 = sw-lead 空闲位上的软件类内部活 (★不是 PCB 类, 不违反老板 11-11 10:07 主线口径★)** ★\n"
             "★**判据方向不变**: 只改演示段的过期期望值, REV-3/REV-3b/helper/71 条 selftest 一个都不许动 ★"),
    "dispatched_at": TODAY,
    "task_brief": BRIEF,
}


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        if any(it.get("id") == "ISS-248" for it in issues):
            print("⚠ ISS-248 已存在 ⇒ 幂等跳过")
            fcntl.flock(lk, fcntl.LOCK_UN)
            return
        issues.append(ISS)
        log["issues"] = issues
        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("✅ ISS-248 已追加 (status=open, owner=sw-lead)")
    print("   备份: %s" % BAK)


if __name__ == "__main__":
    main()
