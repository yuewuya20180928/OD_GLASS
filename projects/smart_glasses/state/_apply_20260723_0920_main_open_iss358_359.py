#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20260723_0920_main_open_iss358_359.py —— main 开 ISS-358 (mech-lead) + ISS-359 (hw-lead): 分片重名 key 清理"""
import os
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

B358 = open(os.path.join(PROJ, "state/dispatch_briefs/ISS-358_mech_frag_dup_keys_cleanup.md"),
            encoding="utf-8").read()
B359 = open(os.path.join(PROJ, "state/dispatch_briefs/ISS-359_hw_frag_dup_keys_cleanup.md"),
            encoding="utf-8").read()

T358 = ("★★[★主线内·机制侧·分片卫生类·内部活] ★★【`state/fragments/mech.yaml` 有 4 组 answers 用同一个 key 登记了不同主题的答案 "
        "⇒ 合并器 `state/merge.py` 对同 `_by` 的多条同 key answers 只认第一条 ⇒ 后写的对下游完全不可见 ⇒ 最要命的一条 "
        "`pcb_outline_confirm` ×5 (5 条讲 5 件完全不同的事) 又正好被 `hw.yaml` 与 `mech.yaml` 两条 need 同时问到 ⇒ 板框/尺寸这条"
        "【老板正面临的轴】的真相在合并后只剩第一条露脸 ⇒ 本单 = 拆成语义独立的 key, 一条内容都不许删】★★ ★**零写板·零落表·"
        "零外发·不替老板拍板** ★")
D358 = ("★**main 2026-11-23 09:1x 本机实读 (不抄任何 agent 报告)★** ⇒ ★**① 体检器 (main 新建, 只读): "
        "`state/check_frag_dup_keys.py --agent mech-lead` ⇒ 高危 4 组: `answers[pcb_outline_confirm]` ×5 · "
        "`answers[ntc_placement]` ×3 · `answers[iss219_mech_c7_sink_area_confirm]` ×2 · "
        "`answers[iss251_mech_service_port_pad_y_migrate]` ×2; 另 31 组 artifacts 重名 = 低危★ ⇒ ★**② 为什么危险 (机制读数)**: "
        "`state/merge.py` 用 `answers_by_key.setdefault(k, []).append(...)` 收集, 答 need 时按 `_by == ask_to` 过滤后取**第一条** ⇒ "
        "⇒ **同 key 同作者的重复 answers = 后写的静默不可见** ⇒ ★**③ 最要命的一条**: `pcb_outline_confirm` 的 5 条分别是 "
        "①PCB 50×12mm 厚 0.8/1.0 ②镜脚内腔需求 ③摄像头安装 ④散热接触路径 ⑤M-FIT 结果 ⇒ **没有一条是板框 U-1 的答案** "
        "⇒ 而它被 `hw.yaml` 的 need(to=mech-lead) 与 `mech.yaml` 的 need(to=sw-lead) 同时问到 ⇒ ★**⇒ 老板正面临的板框轴, "
        "合并后只剩第一条 (50×12mm 口径) 露脸 ⇒ 这很可能就是「板框口径到处飘」的根源之一** ⇒ ★**④ 边界**: 只写 mech.yaml (只走 "
        "frag_write.py) · 零写板 · 零落表 · 零外发 · 不许改 merge.py / gate_check.py / frag_write.py (★根治 = 给 frag_write.py 加"
        "乐观并发断言, 那是 main 的地界·本单只清已攒下的重名★) · 不替老板拍板★")
N358 = ("★★2026-11-23 09:2x · main 开单 (★项目总工 main★) ★★ ★**开单依据**: 兄弟 job 09:03 播报里那条「同 agent 两会话并发写同一分片 "
        "⇒ 后写覆盖前写 (ISS-333 cont1/cont3 同时写 mech.yaml)」⇒ ★**main 把它从【说法】做成了【机器可查的账】**: 新建只读体检器 "
        "`state/check_frag_dup_keys.py` (自测 3/3) ⇒ 四片全扫 ⇒ ★**高危段 (answers / needs_from) 重名合计 9 组**, 其中 mech-lead 4 组最严重"
        "⇒ ★**本单只清已攒下的重名 (逐组拆 key, 一条内容不许删)** ⇒ ★**status 落 open (不落 fixing)**: 派活由队列 job 执行 ⇒ 落 fixing 会变成"
        "「没人跑的僵尸 fixing」★ ⇒ ★**待派**: owner = mech-lead ★ ★**不占老板拍板面** ★")

T359 = ("★★[★主线内·机制侧·分片卫生类·内部活] ★★【`state/fragments/hw.yaml` 有 2 组 answers 与 3 组 needs_from 用了同一个 key 登记多次 "
        "⇒ 合并器只认同 `_by` 多条 answers 的第一条 ⇒ 后写的不可见; needs_from 同 key 登记 N 次 ⇒ 台账里这一条被算成 N 条未闭合 ⇒ "
        "最要命的 `s1_ref_rename_caliber_20261118` ×3 正是「★S1 位号改名口径必须开工前拍★」这条【老板待拍项】⇒ 同一件事占 3 个坑位 ⇒ "
        "未闭合需求数虚高 ⇒ 本单 = 拆成语义独立的 key, 一条内容都不许删】★★ ★**零写板·零落表·零外发·不替老板拍板** ★")
D359 = ("★**main 2026-11-23 09:1x 本机实读 (不抄任何 agent 报告)★** ⇒ ★**① 体检器 (main 新建, 只读): "
        "`state/check_frag_dup_keys.py --agent hw-lead` ⇒ 高危 5 组: `answers[iss081_pin_budget_carrier]` ×2 "
        "(★**被 `mech.yaml` 的 need (to=hw-lead) 问到 ⇒ 合并只认第一条·另一条对下游不可见★**) · `answers[iss287_baseline_readings]` ×2 · "
        "`needs_from[iss249_h1_reanchor_netlist_md5]` ×2 (★收件人不同 sw-lead / mech-lead ⇒ 本来就是两件事, 只是 key 写重了★) · "
        "`needs_from[iss249_kicad_sch_md5_not_anchor]` ×2 (★同上★) · `needs_from[s1_ref_rename_caliber_20261118]` ×3 "
        "(★★2 条逐字相同 + 1 条更长含 NC 白名单方案 ⇒ 老板那边本应只看见 1 件事★★) ⇒ 另 24 组 artifacts 重名 = 低危★ ⇒ "
        "★**② 机制读数**: `state/merge.py` 答 need 时按 `_by == ask_to` 过滤后取**第一条** ⇒ 同 key 重复 answers = 后写的静默不可见; "
        "needs_from 重复 ⇒ 台账未闭合数虚高 ⇒ ★**③ 并发注意**: hw-lead 此刻可能还有别的会话在写 hw.yaml (ISS-356 cont2 在跑) ⇒ "
        "★**写前记 md5 基线, 写后再比; 期间被别人改过 ⇒ 停下并写进交卷页 (不要静默覆盖——这正是本单要治的病)**★ ⇒ ★**④ 边界**: "
        "只写 hw.yaml (只走 frag_write.py) · 零写板 · 零落表 · 零外发 · 不许改 merge.py / gate_check.py / frag_write.py · "
        "★**`s1_ref_rename_caliber_20261118` 是老板要拍的那件事·只清重名登记, 不许自己给口径**★")
N359 = ("★★2026-11-23 09:2x · main 开单 (★项目总工 main★) ★★ ★**开单依据**: 同 ISS-358 的机制读数 (main 新建只读体检器 "
        "`state/check_frag_dup_keys.py` ⇒ 高危段重名 9 组) ⇒ 本单 = hw-lead 那 5 组 ⇒ ★**status 落 open (不落 fixing)**: 派活由队列 job 执行 "
        "⇒ 落 fixing 会变成「没人跑的僵尸 fixing」★ ⇒ ★**待派**: owner = hw-lead (★该 agent 此刻在跑 ISS-356 cont2 ⇒ 排队等槽位★) ★ "
        "★**不占老板拍板面** ★")

ENTRIES = [
    {"id": "ISS-358", "title": T358, "severity": "medium", "source_blocker": "ISS-333",
     "source_agent": "main", "desc": D358, "owner": "mech-lead", "reporter": "main",
     "raised": "2026-11-23", "due": "2026-11-25", "status": "open", "external": "false",
     "task_brief": B358, "dispatched_at": None, "verify_by": "main", "verify_result": None, "note": N358},
    {"id": "ISS-359", "title": T359, "severity": "medium", "source_blocker": "ISS-333",
     "source_agent": "main", "desc": D359, "owner": "hw-lead", "reporter": "main",
     "raised": "2026-11-23", "due": "2026-11-25", "status": "open", "external": "false",
     "task_brief": B359, "dispatched_at": None, "verify_by": "main", "verify_result": None, "note": N359},
]


def main():
    src = open(LOG, encoding="utf-8").read()
    chunk = yaml.safe_dump(ENTRIES, allow_unicode=True, sort_keys=False, width=200)
    if not src.endswith("\n"):
        chunk = "\n" + chunk
    shutil.copy2(LOG, LOG + ".bak_%s_main_open_iss358_359" % STAMP)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(src + chunk)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    d = yaml.safe_load(open(LOG, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("issues", d)
    ids = [i.get("id") for i in items]
    print("台账条数 = %d · ISS-358 在盘 = %s · ISS-359 在盘 = %s · 零重复 id = %s"
          % (len(ids), "ISS-358" in ids, "ISS-359" in ids, len(ids) == len(set(ids))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
