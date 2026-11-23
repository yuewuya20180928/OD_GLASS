#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_2255_main_answer_iss372_needs.py
==================================================
main (项目总工) 回 ISS-372 登记给 main 的 6 条 need (★只走 `state/frag_write.py` 的原子写·★零写板·零落表★)

★**分两类 (★main 地界 vs 老板地界·★不混★)** ★
★**A 类 = main 地界 (★main 直接答·★答完这 6 条里 4 条就闭合★)** ★
| key | main 的裁决 |
|---|---|
| `iss372_need_main_decide_s9_rebase_batch` | ★**认**: S9 换基线按清账页 §B4-2 四步一次改齐 (① 落表台账链前移 ② 台账锚点 reboard 四项 ③ 规格页引用 17 处 ④ issue_log 留痕); 顺序 = **先落表 → 再换基线 → 最后跑闸** (★顺序错 ⇒ 闸在中间态必红★) ⇒ 拆批即红 ⇒ 一次改齐 |
| `iss372_need_main_schedule_pcd_patch` | ★**排期 = 板那一趟开工前同批**: P-C (`check_fp_truth_read.py` F5) + P-D (`check_onepass_legb_sw_impact.py` G8) + P-E (`HW/check_iss354_manufacturability.py` A-5, ★**跨域 ⇒ 转 hw-lead 本单分片自己改·sw-lead 不越界★) ⇒ 不落 ⇒ 改板当天 3 道闸必红 ⇒ 整趟白跑 |
| `iss372_need_main_hook_readiness_gate` | ★**挂** `SW/tools/check_sw_board_md5_rebase_readiness.py` 进 `state/gate_check.py` 的 `EXTRA_GATES` ⇒ ★**但与那一趟同批挂** (★先例 ISS-300/309/312/315 四轮只交写法没人挂 ⇒ 挂链是 main 地界·★但提前单独挂 ⇒ 闸链在中间态会红★) ⇒ 落盘动作随那一趟 |
| `iss372_need_main_refresh_pinned_gates_manifest` | ★**刷新时机 = 与 P-C/P-D/P-E 三块补丁同批** (★不提前单独改·★单独改 ⇒ 清单与闸不同步 ⇒ 中间态红★); 收集口径 = ★**要把 `state/land_v_values.py` 也收进去** (★它 L96 也硬钉板 md5·★漏收 = 那条闸永远红·★等于没修★) ⇒ 内容按清账页 §5.1 (现有 9 条 + 新增 3 条 + 口径补 1 条) |
★**B 类 = 老板地界 (★main 不代拍·★登记成待拍项·★进老板那一页★)** ★
| key | 为什么必须老板拍 | 新 need key (to=boss) |
|---|---|---|
| `iss372_need_main_decide_reboard_mtime_size` | ★**判据方向要不要放宽** (★mtime/size 要不要进 reboard 原子 ⇒ 要么动权威判据, 要么给 F5/A-5 的 mtime 判据写明文口径·★**两者都是判据方向变化 ⇒ 老板拍·★main 不代拍★**) | `boss_decide_reboard_mtime_size_caliber` |
| `iss372_need_main_decide_pcb_second_reboard_fallback` | ★**现场权责**: 板改第二次时「谁当场判定并停手」⇒ 那是流程权责 ⇒ 老板拍 | `boss_decide_second_reboard_stop_authority` |
★**⇒ 「板那一趟」的老板侧阻塞面: 9 件 → 11 件 (★新增 2 件都是【判据方向/流程权责】级别·★一件没代拍★)** ★
"""
import os
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
sys.path.insert(0, os.path.join(PROJ, "state"))
import frag_write  # ★只用它的原子写 (★纪律: 写分片只走 frag_write.py★)

A_ANSWERS = [
    {
        "key": "iss372_need_main_decide_s9_rebase_batch",
        "to": "sw-lead",
        "value": ("★**main 裁决 (★2026-11-23 22:5x·★main 地界·★不代老板拍★)★: ★**认** ⇒ ★**S9 换基线按清账页 §B4-2 的四步一次改齐** "
                  "(① 落表台账链前移 ② 台账锚点 reboard 四项 ③ 规格页引用那 17 处 ④ issue_log 留痕) ★**顺序 = 先落表 → 再换基线 → 最后跑闸** "
                  "(★顺序错 ⇒ 闸在中间态必红★) ⇒ **拆批即红 ⇒ 必须一次改齐** ★ ⇒ ★**落盘时机 = 板那一趟开工前同批** (★不单独提前改·★提前改 = 清单与闸不同步★) ★ "
                  "⇒ ★**本裁决不含任何「放宽判据」的动作 (★只是确认顺序与批次·★判据方向的变化不在这里★)** ★"),
        "ref": ("ISS-372 清账页 §B4-2 · SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md · "
                "DECISION_ONE_PAGER_2026-11-22.md §㉜/§㉝"),
    },
    {
        "key": "iss372_need_main_schedule_pcd_patch",
        "to": "sw-lead",
        "value": ("★**main 裁决 (★2026-11-23 22:5x·★main 地界★)★: ★**排期 = 板那一趟开工前同批落** ⇒ ★**P-C** (`SW/tools/check_fp_truth_read.py` 的 F5) + "
                  "★**P-D** (`SW/tools/check_onepass_legb_sw_impact.py` 的 G8) + ★**P-E** (`HW/check_iss354_manufacturability.py` 的 A-5) ★ "
                  "⇒ ★**P-E 是跨域 (HW 侧) ⇒ 转 hw-lead 在【自己的分片/自己的脚本】里落, sw-lead 不越界改 HW 域** ★ ⇒ ★**不落的后果 = 改板当天 3 道闸必红 (F5 / G8 / A-5) ⇒ 现场会误读成「板改坏了」⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ "
                  "⇒ ★**落盘时必须同批做 4 件事**: ① 三块补丁落盘 ② `state/board_md5_pinned_gates.json/.md` 刷新 (★口径要含 `state/land_v_values.py`★) "
                  "③ 新闸挂 `EXTRA_GATES` ④ `issue_log` 留痕 ⇒ ★**四件不同批 = 中间态红** ★"),
        "ref": "ISS-372 清账页 §4/§5.1 · SW/tools/check_sw_board_md5_rebase_readiness.py",
    },
    {
        "key": "iss372_need_main_hook_readiness_gate",
        "to": "sw-lead",
        "value": ("★**main 裁决 (★2026-11-23 22:5x·★main 地界★)★: ★**挂** —— `SW/tools/check_sw_board_md5_rebase_readiness.py` 进 "
                  "`state/gate_check.py` 的 `EXTRA_GATES` ★ ⇒ ★**但必须与「板那一趟」同批挂** (★先例 = ISS-300 / ISS-309 / ISS-312 / ISS-315 四轮都只交写法没人挂 ⇒ "
                  "★挂链是 main 地界·★但提前单独挂 ⇒ 闸链在中间态会红★) ⇒ ★**落盘动作随那一趟, 不在本轮动 `gate_check.py`** ★ "
                  "⇒ ★**挂上之后它的作用 = 把「清单过期」从【改板当天才发现】提前到【开工前就报】** ★"),
        "ref": "state/gate_check.py EXTRA_GATES · ISS-372 交卷页 §B5",
    },
    {
        "key": "iss372_need_main_refresh_pinned_gates_manifest",
        "to": "sw-lead",
        "value": ("★**main 裁决 (★2026-11-23 22:5x·★main 地界★)★: ★**刷新时机 = 与 P-C / P-D / P-E 三块补丁同批** (★不提前单独改★ "
                  "★单独改 ⇒ 清单与闸不同步 ⇒ 中间态红★) ⇒ ★**收集口径要放宽: 把 `state/land_v_values.py` 也收进去** (★它 L96 也硬钉板 md5·"
                  "★漏收 = 那条闸永远红 = 等于没修★) ⇒ ★**刷新后应有的内容 = 清账页 §5.1 给的: 现有 9 条 + 新增 3 条 + 口径补 1 条** ★ "
                  "⇒ ★**本轮零改那两份文件 (★那是 main 的域·★但必须与那一趟同批·★提前改必中间态红★)** ★"),
        "ref": "ISS-372 清账页 §5.1 · state/board_md5_pinned_gates.json/.md (main 域)",
    },
]

B_NEEDS = [
    {
        "key": "boss_decide_reboard_mtime_size_caliber",
        "to": "boss",
        "item": ("★**老板拍板: 合法改板时, `mtime` / `size` 这两条要不要进 reboard 的四项原子 (by / file / prev_md5 / md5)?** ★ "
                 "⇒ ★**背景 (★ISS-372 实测·★main 未代拍★)★**: reboard 原子**不含** mtime/size ⇒ ⇒ 合法改板后 **F5 的 mtime + size 两条仍然红** ⇒ "
                 "⇒ P-C 只解决一半 ⇒ **改板当天照样红** ⇒ ★**两条路**: ① ★**动权威判据** (★把 mtime/size 加进 reboard 原子★) ② ★**给 F5 / A-5 的 mtime 判据写明文口径** "
                 "(★= 判据方向放宽·★同样是拍板★) ⇒ ★**⇒ 两条路都是【判据方向变化】⇒ 老板拍, main 不代拍** ★ "
                 "⇒ ★**不拍的后果**: 板那一趟开工当天 SW 域 2 道 (F5/G8) + 跨域 1 道 (A-5) 必红 ⇒ 现场极可能误读成「板改坏了」⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★ "
                 "⇒ ★**main 倾向 (★仅供参考·不是拍板★)**: ① (★把 mtime/size 纳入 reboard 原子·★它本来就是「这次改板换了什么」的完整描述·★不涉及放宽任何净距/电气判据★) ★"),
        "since": "2026-11-23",
    },
    {
        "key": "boss_decide_second_reboard_stop_authority",
        "to": "boss",
        "item": ("★**老板拍板: 「板改第二次」这件事, 现场由【谁】当场判定并停手?** ★ "
                 "⇒ ★**背景 (★ISS-372 实测·★main 未代拍★)★**: 沙盒已证明【当场红】这件事本身可靠 (★T5 全红·★纯 md5 硬保护支路没被放松·★判据没问题★) ⇒ "
                 "⇒ ★**缺的是【流程权责】: 闸红着的时候, 谁来判断「这是第二次改板, 停手」?** ⇒ ★**不定的后果**: 现场第二次改板时闸红着, "
                 "但没人知道那是第二次而不是第一次 ⇒ ⇒ 改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑 ★ "
                 "⇒ ★**⇒ 「板只改一次」是老板 11-17 定的铁律 ⇒ 现场谁来执行这条铁律 = 老板的权责 ⇒ main 不代拍** ★"),
        "since": "2026-11-23",
    },
]


def main():
    def mutate(d):
        ans = d.setdefault("answers", [])
        have = {e.get("key") for e in ans if isinstance(e, dict)}
        for a in A_ANSWERS:
            if a["key"] in have:
                print("  ★已有 answer, 跳过:", a["key"])
                continue
            ans.append({"key": a["key"], "to": a["to"], "value": a["value"], "ref": a["ref"]})
            print("  ✅ answer 落:", a["key"])
        nf = d.setdefault("needs_from", [])
        have_n = {e.get("key") for e in nf if isinstance(e, dict)}
        for n in B_NEEDS:
            if n["key"] in have_n:
                print("  ★已有 need, 跳过:", n["key"])
                continue
            nf.append({"key": n["key"], "to": n["to"], "item": n["item"], "since": n["since"]})
            print("  ✅ need 落 (to=boss):", n["key"])
    frag_write.update_fragment("main", mutate)
    print("★ pm.yaml 已原子更新 (★只走 frag_write.py·★零写板·零落表★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
