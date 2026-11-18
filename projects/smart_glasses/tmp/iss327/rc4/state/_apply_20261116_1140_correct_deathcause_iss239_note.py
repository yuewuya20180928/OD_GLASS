#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1140_correct_deathcause_iss239_note.py
★main 2026-11-16 11:4x (cron 775d9893 继续执行后继计划)★
★订正 ISS-239 / ISS-172 的死因记录 (★旧文字留痕, 只追加订正段, 不删不改原文★)★

★★**为什么要订正 (★main 本轮 11:3x~11:4x 自己逐条实测 transcript, 不猜★)** ★★
· ★**11:0x 那两轮 (sw-lead ISS-172 / hw-lead ISS-239) 的最后一条 message 都是同一个标记**: ★
  `[openclaw] missing tool result in session history; inserted synthetic error result for transcript repair.` ★
  ⇒ ★**这跟老板 11-15 健康检查里报的那条 `EmbeddedAttemptSessionTakeoverError: session file changed while embedded prompt lock was released` 是同一类 (会话文件被抢写) ⇒ 不是任务本身的问题** ★
· ★**★但 main 11:3x 在上一条 note 里写的是「撞 600s 默认 run timeout」⇒ 那个说法不准确 (★runtime 594s/569s 只是巧合, 标记才是证据★) ⇒ 本脚本追加订正段, 旧文字按纪律留痕不删** ★
· ★**11:24 main 自己派的第 1 次重派 (hw-lead ISS-239) 又叠加了第二种死因**: ★
  `overloaded_error「当前服务集群负载较高，请稍后重试」 (2064) (529)` + `unknown error, 715 (1000)` ⇒ ★**上游模型集群过载** ★
  ⇒ ★**★三条 ⇒ 处置从「错峰 + runTimeout 5400s」升级为「错峰 + runTimeout 5400s + ★抗过载原地重试纪律★ + 每拿到一个结论立刻写盘」★★ ★
  ⇒ ★**★且第 1 次重派在死前其实已经摸到根因方向 (★网表里 U_LDO_S28 pin4 的 value 是轨描述「5.0V (F13: 由 CARRIER_BOARD_EN 门控)」, pin5 才是「散热焊盘 (pin5, EP)」; 脚表却把 pin4/pin5 都写成「GND (pin2)」⇒ ★**「同 ref 同 net 复制」解释不了 pin5★ ⇒ ★**这个矛盾已作为【待复核种子】写进第 2 次重派的任务书★) ⇒ ★**没白死** ★ ★
· ★**★两条的盘面都干净 (main 11:3x 逐字节复核)**: ISS-239 = `HW/check_pin_function_labels.py` / `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` / `HANDOFF/*ISS239*` 全不在盘 · 受保护 5 md5 逐字节未变 (34132f7e… / b21b743a… / c195a117… / 611b869e… / 3e504d2b…) ⇒ ★**重派不冲突, 可干净重做** ★ ★

★★**边界 (本脚本)★★ ★★
· ★**只往 `state/issue_log.yaml` 的 ISS-172 / ISS-239 两条 note 追加一段订正 (★不改 status / verify_* / fix_ref★)** ★
· ★**不改 PROJECT_TRACKER.md §0** · ★**不写任何 agent 的分片** · ★**不碰板 / 布线 / 布局** · ★**零外发** ★
"""
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

NOTE_239 = (
    "\n\n★★★2026-11-16 11:4x (cron 775d9893 继续执行后继计划) ★**死因订正 (★main 逐条实测 transcript, 旧文字按纪律留痕不删★)** ★★★\n"
    "· ★**订正**: 上面那段写的「★撞 600s 默认 run timeout★」⇒ ★**不准确**★ ⇒ ★**真标记 = 两轮最后一条 message 都是** "
    "`[openclaw] missing tool result in session history; inserted synthetic error result for transcript repair.` "
    "⇒ ★**同一类 = 会话文件被抢写 (老板 11-15 健康检查里的 `EmbeddedAttemptSessionTakeoverError: session file changed while embedded prompt lock was released`)** ⇒ "
    "**不是任务本身的问题, 也不是超时** ★\n"
    "· ★**★另叠加第二种死因 (★main 11:24 自己派的第 1 次重派★)**: `overloaded_error「当前服务集群负载较高，请稍后重试」 (2064) (529)` + "
    "`unknown error, 715 (1000)` ⇒ ★**上游模型集群过载** ★ ⇒ ★**第 1 次重派 runtime 仅 110s 就死 (★它其实已经摸到根因方向★)★ ★\n"
    "· ★**★处置升级 (★第 2 次重派已按此派发, taskName=queue_iss239_r2★)**: ★**① 错峰派发 (不与 sw-lead 同时起跑) ② runTimeout=5400s "
    "③ 抗过载纪律 = 撞 overloaded_error / 715 就原地重试, 别放弃 ④ 每拿到一个结论立刻写盘 (别攒到最后一起写)** ★\n"
    "· ★**★第 1 次重派没白死 (★它的观测已作为【待复核种子】进第 2 次任务书★)**: 网表里 U_LDO_S28 pin4 的 value = `5.0V (F13: 由 CARRIER_BOARD_EN 门控)` (★是轨描述, 不是引脚功能名★) · "
    "pin5 = `散热焊盘 (pin5, EP)` (★这个是对的★) · ★**而脚表把 pin4/pin5 都写成 `GND (pin2)` ⇒ ★**「同 (ref,net) 复制」解释不了 pin5 ⇒ 这正是本单要查清的矛盾点 (★标为待复核种子, ★不许当发现照抄★)** ★\n"
    "· ★**盘面干净 (main 11:3x 逐字节复核)**: `HW/check_pin_function_labels.py` / `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md` / `HANDOFF/*ISS239*` 全不在盘 · "
    "受保护 5 md5 逐字节未变 (34132f7e… / b21b743a… / c195a117… / 611b869e… / 3e504d2b…) ⇒ ★**重派不冲突** ★\n"
    "· ★**status 保持 fixing** (★本轮不重复标★) ★"
)

NOTE_172 = (
    "\n\n★★★2026-11-16 11:4x (cron 775d9893 继续执行后继计划) ★**死因订正 (★main 逐条实测 transcript, 旧文字按纪律留痕不删★)** ★★★\n"
    "· ★**订正**: 上面那段写的「★撞 600s 默认 run timeout★」⇒ ★**不准确**★ ⇒ ★**真标记 = 该轮最后一条 message =** "
    "`[openclaw] missing tool result in session history; inserted synthetic error result for transcript repair.` "
    "⇒ ★**同一类 = 会话文件被抢写 (老板 11-15 健康检查里的 `EmbeddedAttemptSessionTakeoverError: session file changed while embedded prompt lock was released`)** ⇒ "
    "**不是任务本身的问题, 也不是超时** ★\n"
    "· ★**处置**: 本轮重派已按 ★**错峰 (不与 hw-lead 同时起跑) + runTimeout=5400s + 抗过载原地重试 + 每拿到一个结论立刻写盘**★ 派发 (taskName=queue_iss172) ⇒ ★**status 保持 fixing** ★"
)


def _atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_write.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(LOG, LOG + ".bak_20261116_1140_correct_deathcause")

    log = yaml.safe_load(open(LOG, encoding="utf-8"))
    hit = 0
    for it in log.get("issues") or []:
        if it.get("id") == "ISS-239":
            it["note"] = (it.get("note") or "") + NOTE_239
            hit += 1
        elif it.get("id") == "ISS-172":
            it["note"] = (it.get("note") or "") + NOTE_172
            hit += 1
    if hit != 2:
        raise SystemExit("★命中数异常 = %d ⇒ 中止" % hit)

    _atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100000))

    chk = yaml.safe_load(open(LOG, encoding="utf-8"))
    for iid in ("ISS-172", "ISS-239"):
        it = [x for x in chk["issues"] if x.get("id") == iid][0]
        print("   %s status = %s (★未动★)" % (iid, it.get("status")))
    print("✅ issue_log.yaml 已原子写: 两条 note 追加死因订正段 (★旧文字留痕, 只追加★)")
    print("★**零外发 · 未替老板拍板 · 不碰 PCB 布线/布局/板 · 不写别人的分片** ★")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
