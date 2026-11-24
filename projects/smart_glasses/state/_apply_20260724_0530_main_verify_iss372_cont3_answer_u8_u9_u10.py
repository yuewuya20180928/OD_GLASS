#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0530_main_verify_iss372_cont3_answer_u8_u9_u10.py
=====================================================================
main (项目总工) · 2026-11-24 05:3x
★独立复核 ISS-372 cont3 (sw-lead) 的交卷 + 裁 U8 / U9 / U10 三条 + 把【本轮新撞出来的耦合】落进台账★

★纪律 (★本脚本自己守★):
  ① 零写板 (板 md5/mtime/size 三项开工前后各打一次)
  ② 零落表 (网表/脚表/BOM/落表台账 一字不改)
  ③ 零改既有闸 / 零改既有页面正文
  ④ 分片只走 state/frag_write.py (原子写)
  ⑤ issue_log.yaml / 一页 / LESSONS.md 一律【追加式】(★老字一字未删·★零 churn★)
  ⑥ 不自签 (★台账只追加 note_addendum, 不改 status/verify_result★)
  ⑦ 零外发 · 不代老板拍板
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import frag_write  # ★只用它的原子写 ★
import yaml

STAMP = time.strftime("%Y%m%d_%H%M")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
LOG = os.path.join(PROJ, "state/issue_log.yaml")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

# ★cont3 三件交付物 (★child 自报值 + main 本机实测值逐字相同★)
DELIV = [
    ("SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md", 94270, "0ba9dfce5046e131465b4fbd3675614f"),
    ("SW/tools/check_sw_board_md5_rebase_readiness.py", 33655, "2099ca42a946f64b620e896ba8d2be0b"),
    ("HANDOFF/2026-11-23_sw-lead_ISS372_SW侧板md5引用面清账与清单自守.md", 66638,
     "fb7824500ec780f957d9b281e13f94b6"),
]
# ★受保护件基线 (★从 cont3 自己落的留证里读, 不手打★)
BASELINE = os.path.join(PROJ, "logs/iss372/12_boundary_evidence_cont1.txt")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def board_fp():
    st = os.stat(BOARD)
    return md5(BOARD), st.st_mtime_ns, st.st_size


def ns_of(s):
    """★纳秒级 (★铁律⑩-j: 秒级比较会把「同一秒内被改」漏掉, 也会把「没被改」误判成被改★)
    ★本机 TZ = Asia/Shanghai (+08:00) ⇒ 显式按 +08:00 换算, 不依赖 TZ 环境变量★"""
    import datetime
    base, _, frac = s.partition(".")
    frac = (frac + "000000000")[:9]
    tz8 = datetime.timezone(datetime.timedelta(hours=8))
    dt = datetime.datetime.strptime(base, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz8)
    return int(dt.timestamp()) * 10 ** 9 + int(frac)


def sh(cmd):
    import subprocess
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def read_lines(path):
    return open(path, encoding="utf-8").read()


# ===================================================================== 阶段 1 · 独立复核
def verify():
    print("=" * 90)
    print("★阶段 1 · main 本机独立复核 (★不抄 agent 报告★)")
    print("=" * 90)
    ok = True

    # 1.1 板三项 (★开工侧★)
    m, ns, sz = board_fp()
    print("  板 md5      = %s  (期望 %s) ⇒ %s" % (m, BOARD_MD5, "✅" if m == BOARD_MD5 else "❌"))
    print("  板 mtime_ns = %d  (期望 %d) ⇒ %s" % (ns, ns_of(BOARD_MTIME),
                                                "✅" if ns == ns_of(BOARD_MTIME) else "❌"))
    print("  板 size     = %d  (期望 %d) ⇒ %s" % (sz, BOARD_SIZE, "✅" if sz == BOARD_SIZE else "❌"))
    ok &= (m == BOARD_MD5 and ns == ns_of(BOARD_MTIME) and sz == BOARD_SIZE)

    # 1.2 三件交付物 (★md5 + 字节数逐字对拍 child 自报值★)
    for rel, size, want in DELIV:
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "-"
        gs = os.path.getsize(p) if os.path.isfile(p) else -1
        good = (got == want and gs == size)
        ok &= good
        print("  交付物 %-72s %d B md5 %s ⇒ %s" % (rel[-72:], gs, got[:8], "✅" if good else "❌"))

    # 1.3 受保护件 md5 逐条对基线 (★基线从留证文件读, 不手打★)
    base = {}
    for ln in read_lines(BASELINE).split("\n"):
        parts = ln.split(None, 1)
        if len(parts) != 2:
            continue
        h, rel = parts[0].strip(), parts[1].strip()
        if len(h) != 32 or any(c not in "0123456789abcdef" for c in h):
            continue
        if rel == "-" or rel.startswith("="):
            continue  # ★原理图 11 个是聚合成一行 ("-")·★不是单文件路径★
        base[rel] = h
    bad = []
    for rel, want in sorted(base.items()):
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    print("  受保护件 %d 条 md5 逐条对基线 ⇒ 动 %d %s" % (len(base), len(bad), bad[:3]))
    ok &= (len(bad) == 0)

    # 1.4 零落表三件
    for rel in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
        p = os.path.join(PROJ, rel)
        base_rel = rel
        want = base.get(base_rel)
        got = md5(p)
        good = (want is not None and got == want)
        ok &= good
        print("  零落表 %-24s %s ⇒ %s" % (rel, got[:8], "✅" if good else "❌"))

    # 1.5 必跑命令 rc
    rc, out = sh("python3 SW/tools/check_sw_board_md5_rebase_readiness.py")
    ok &= (rc == 0)
    print("  自守闸裸跑 rc=%d ⇒ %s" % (rc, "✅" if rc == 0 else "❌"))
    rc2, out2 = sh("python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest")
    last = out2.strip().splitlines()[-1] if out2.strip() else ""
    ok &= (rc2 == 0 and "ALL TESTS PASS" in last)
    print("  自守闸 --selftest rc=%d 末行=%r ⇒ %s" % (rc2, last, "✅" if ok else "❌"))
    rc3, _ = sh("python3 state/merge.py")
    ok &= (rc3 == 0)
    print("  merge.py rc=%d ⇒ %s" % (rc3, "✅" if rc3 == 0 else "❌"))
    rc4, o4 = sh("python3 state/gate_check.py")
    q1 = "18/18" in o4
    ok &= (rc4 == 0 and q1)
    print("  gate_check.py rc=%d Q1=18/18:%s ⇒ %s" % (rc4, q1, "✅" if (rc4 == 0 and q1) else "❌"))

    # 1.6 零挂链
    rc5, o5 = sh("grep -c check_sw_board_md5_rebase_readiness state/gate_check.py")
    zero = o5.strip().splitlines()[0].strip() == "0" if o5.strip() else False
    ok &= zero
    print("  零挂链 (gate_check.py 命中 %s) ⇒ %s" % (o5.strip().splitlines()[0] if o5.strip() else "?",
                                                "✅" if zero else "❌"))

    # 1.7 state/board_md5_pinned_gates.json/.md 未动
    for rel in ("state/board_md5_pinned_gates.json", "state/board_md5_pinned_gates.md"):
        p = os.path.join(PROJ, rel)
        got = md5(p)
        want = base.get(rel)
        good = want is not None and got == want
        ok &= good
        print("  main 域清单 %-34s %s ⇒ %s" % (rel, got[:8], "✅" if good else "❌"))

    print("  ★阶段 1 结论: %s" % ("★全绿★" if ok else "★★有红项★★"))
    return ok


# ===================================================================== 阶段 2 · pm.yaml (main 自己的分片)
ANS_U8 = (
    "★**main 裁决 (★2026-11-24 05:3x·★main 地界·★不代老板拍★)★: ★**批 = 6 件 (★不是 5 件★) ⇒ 合成【一批】落, "
    "批内顺序 = ① 先落 5 条通道补丁 (P-C/P-D/P-E/P-F/P-G) → ② 再重生成清账页 §1 机器块 + 逐行同步 §1 表格 "
    "→ ③ 再刷 state/board_md5_pinned_gates.json/.md → ④ 再挂新闸进 EXTRA_GATES → ⑤ 最后 issue_log 留痕 "
    "→ ⑥ 落完重跑 T0~T5 七闸读数表★** ⇒ ★**拆批即红 ⇒ 必须一次改齐★** ★ "
    "★**★为什么是 6 件 (★本轮 main 亲自在沙盒实测撞出来的★·★不在 child 的 U8 答案里★)★**: ★**child 找到的耦合是 "
    "「P-F 移动闸 F 的函数行号 ⇒ 闸 G 的 W2 红」(★main 已复现: 插 6 行 ⇒ d1_current_board 287⇒293 ⇒ W2 5 行全红★)★; "
    "★**main 另撞出第二层耦合: ISS-372 自守闸自己的 §1 清单钉的是 (file, line) 对 ⇒ H1 双向判红 ★**(★扫到而清单没登记 ⇒ 红★; "
    "★清单登记了而盘上扫不到 ⇒ 红★) ⇒ ★**P-C/P-D/P-F/P-G 每一条都在插行, 每一条都会把 §1 钉的那一行挪走 ⇒ "
    "改板当天自守闸【自己】当场红★ ⇒ ★**现场又多一次「误读成板坏了」的窗口 ⇒ 而 child 建议的「落完重跑 T0~T5」覆盖的是 7 道板闸, "
    "【不包含】自守闸自己 ⇒ 光重跑 T0~T5 抓不到这一层★** ★ "
    "★**★第 6 件 = 重生成 §1 (★且有一个工具缺口要补★): 现有两条重生成路都不够★** —— ① 闸里的 write_manifest() 注释写明 "
    "「★只用于 --selftest 的沙盒副本★」⇒ 不许写真件 ★ ② tmp/iss372/gen_manifest.py 只写 tmp/iss372/manifest.json + sec1_table.md "
    "⇒ 不回写清账页 ★ ⇒ ★**⇒ 批次前必须先把「真件重生成」这条路走通 (★谁走通归 sw-lead·★main 只给规格★)★; 不走通 ⇒ "
    "批次落完 §1 必然是过期的 ⇒ 自守闸必红★** ★ "
    "★**★工具缺口的规格 (★交 sw-lead·★不代做★)★**: 重生成必须① 从 SW 域真扫 (★不许手写行号★) ② 回写清账页的 §1 机器块 "
    "(MANIFEST_BEGIN/END 之间) ③ 同时逐行同步 §1 表格里的行号列 ④ 重生成后自守闸 rc=0 且 §1 表格与机器块【逐条一致】 "
    "⑤ 批次内 5 条补丁落完 ⇒ 重生成一次 ⇒ 【不许手工改行号】★ "
    "★**★落批时机 = 「板那一趟」开工前同批 (★承 main 11-23 22:5x 对 U2 的裁决·★不提前单独落★)★** ⇒ "
    "★**⇒ 不落的后果 = 改板当天 5 道板闸 + 【自守闸自己】共 6 处红 ⇒ 现场误读 ⇒ 板 md5 变第二次 ⇒ 整趟白跑★** ★"
)

ANS_U9 = (
    "★**main 裁决 (★2026-11-24 05:3x·★main 地界·★不代老板拍★)★: ★**U9 与 U3 是【同一个问题的第二个受影响闸】 ⇒ "
    "★**并进既有老板待拍项 `boss_decide_reboard_mtime_size_caliber`, 不新造第二个 key (★防撞名·★一页的「待拍板面」件数不变·★仍 11 件★)★** ★ "
    "★**★为什么是同一个问题 (★本轮 main 本机实读闸 G 源码确认★)★**: 闸 G (`SW/tools/check_debug_header_fw_impact.py`) 的 W7 "
    "判据【同时】比三项: 机器块里的 `baseline.board_md5` + `baseline.board_size` + `baseline.board_mtime`(纳秒) ⇒ "
    "⇒ ★**reboard 四项原子 (by/file/prev_md5/md5) 不含 size ⇒ 合法改板后 W7 仍红在 board_size ⇒ 与 F5 的 mtime/size 同款⇒ "
    "⇒ 老板那一票 (「mtime/size 要不要进 reboard 原子」) 【一次拍完两个闸】★ ⇒ "
    "★**main 倾向 (★仅供参考·★不是拍板★)**: ① 把 mtime + size 一并纳入 reboard 原子 (★它本就是「这次改板换了什么」的完整描述·"
    "★不涉及放宽任何净距/电气/板框判据★) ⇒ ★**这一条同时解掉 F5 与 W7 两处红⇒ 老板只需拍一票·★不是两票★** ★ "
    "★**★本条只是【把闸 G 加进那一票的受影响闸清单】, 老板侧待拍板面【件数不变】(★仍 11 件·★§㉞ 表里的 ⑤ 已就地追加★)★** ★"
)

ANS_U10 = (
    "★**main 裁决 (★2026-11-24 05:3x·★main 地界·★不代老板拍★)★: ★**收集口径【放宽】⇒ 放宽到「闸自己算盘上板 md5 且期望值来自文档」"
    "(★类 B·★ISS-372 自守闸 H4 的类 B 判据就是蓝本★)★ ⇒ ★**理由 (★本轮 main 本机实读确认★)★**: 现有口径只收「.py 里含 32 位字面量」 ⇒ "
    "★**闸 G (`check_debug_header_fw_impact.py`) 源码里【零个 32 位字面量】(★grep 命中 0·★它自己算 md5 再比★) ⇒ 靠页面内嵌基线钉板 md5 "
    "⇒ 不放宽 ⇒ 这道闸永远收不进那张表 ⇒ 下一道同类的闸照样从缝里溜过去 ⇒ 收进去【等于把这道闸变成可审计项】★** ★ "
    "★**★刷新增的口径 (★本轮 main 亲扫·★不在 child 的清单里★)★**: 现有 9 条 + ★**新增 5 条**★ (F5 `check_fp_truth_read.py` / "
    "G8 `check_onepass_legb_sw_impact.py` / A-5 `HW/check_iss354_manufacturability.py` / D7 `check_debug_pin_order_contract.py` / "
    "W7 `check_debug_header_fw_impact.py`) + ★**口径补 2 条**★ (① `state/land_v_values.py` L96 也硬钉板 md5 ⇒ 收进去 "
    "★**② 类 B 闸 (闸自己算 md5 + 期望值来自页面内嵌基线) ⇒ 收进去**) ⇒ ★**刷新后应有内容 = 9 + 5 + 2 = 16 条** ★ "
    "★**刷新时机 = 与 6 件批同批 (★承 11-23 22:5x 裁决 + 本轮 U8 的 6 件批·★不提前单独改★)** ⇒ ★**不刷新 ⇒ 那张表继续漏新闸 ⇒ "
    "下一个新闸再硬钉板 md5 时还是没人拦★** ★ "
    "★**★收口办法 (★main 给口径·★不代做★)★**: 现有生成器 `state/_gen_board_md5_pinned_gates.py` 只收 `check_*.py`/`*_check.py` "
    "且只按字面量 ⇒ ★**收口时要么改这个生成器的收集口径, 要么换用 ISS-372 自守闸 H4 的类 B 判据做收集器 (★二选一·★建议后者·★"
    "因为它已被 10/10 反向用例证明过★)★ ⇒ ★**★刷新前必须先把生成器改对 (★否则刷出来的还是漏的★) ⇒ 这也是第 6 件批的一环★** ★"
)

BOSS_ITEM_APPEND = (
    " ★★【main 追加式订正 2026-11-24 05:3x·★老字一字未删★】★★ ★**这一票的【受影响闸】从 2 个增加到 3 个 (★§㉞ 表 ⑤ 已就地追加·★"
    "★待拍板面件数【不变】·★仍 11 件★)★**: ★**除 F5 (`check_fp_truth_read.py` 的 F5) 与 A-5 (`HW/check_iss354_manufacturability.py` 的 A-5) "
    "之外, 闸 G (`SW/tools/check_debug_header_fw_impact.py` 的 W7) 也受同一票约束** ★ ⇒ ★**闸 G 的 W7 实读 (★main 2026-11-24 05:1x "
    "本机读源码确认★)**: 它拿机器块 `baseline` 的【board_md5 + board_size + board_mtime(纳秒)】三项跟盘上实测逐项比 ⇒ "
    "⇒ ★**reboard 原子不含 size ⇒ 合法改板后 W7 仍红在 board_size** ⇒ ★**⇒ 老板这一票若采纳「mtime+size 一并进 reboard 原子」, "
    "一次解掉 F5 / A-5 / W7 三处红 (★一票·★不是三票★)★** ⇒ ★**★main 倾向不变 (★仅供参考·★不是拍板★): 加进 reboard 原子·★"
    "它本就是「这次改板换了什么」的完整描述·★不涉及放宽任何净距/电气/板框判据★** ★"
)


def apply_pm():
    print("\n" + "=" * 90)
    print("★阶段 2 · pm.yaml (main 自己的分片·★只走 frag_write 原子写★)")
    print("=" * 90)
    before = md5(PM)
    print("  写前 pm.yaml md5 = %s" % before)

    # ★写前快照 (★铁律⑩-k④: yaml.safe_dump 会重写全文件 ⇒ 追加完必须逐条比对旧条目⇒零内容丢失才可信★)
    d0 = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    snap0 = {}
    for sect in ("answers", "needs_from"):
        for e in (d0.get(sect) or []):
            if isinstance(e, dict) and e.get("key"):
                snap0[(sect, e["key"])] = dict(e)

    def mutate(d):
        ans = d.setdefault("answers", [])
        have = {e.get("key") for e in ans if isinstance(e, dict)}

        def upsert(key, value, ref):
            """★就地扩写 (★追加式·★老字一字未删·★不造重名 key·★mapper locate() 取第一条 ⇒ 重名会把新答案遮住★)"""
            for e in ans:
                if isinstance(e, dict) and e.get("key") == key:
                    old = str(e.get("value") or "")
                    if "【main 追加式订正 2026-11-24 05:3x" not in old:
                        e["value"] = old + value
                        print("  ✅ 就地扩写 answer: %s" % key)
                    else:
                        print("  ★已有本次扩写, 跳过: %s" % key)
                    return
            ans.append({"key": key, "to": "sw-lead", "value": value, "ref": ref})
            print("  ✅ 新增 answer: %s" % key)

        upsert("iss372_need_main_batch_channel_patches", ANS_U8,
               "ISS-372 cont3 清账页 §B5-2 U8 · SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md §6 · "
               "main 沙盒实测 (tmp/iss372_verify, 已清理)")
        upsert("iss372_need_main_decide_reboard_mtime_size", ANS_U9,
               "pm.yaml needs_from[boss_decide_reboard_mtime_size_caliber] (★老板待拍项·★一票解三闸★)")
        upsert("iss372_need_main_refresh_pinned_gates_manifest", ANS_U10,
               "ISS-372 cont3 清账页 §5.1 · state/board_md5_pinned_gates.json/.md (main 域)")

        # ★老板待拍项: 就地追加受影响闸 (★不新造 key·★不代拍★)
        nf = d.setdefault("needs_from", [])
        for n in nf:
            if isinstance(n, dict) and n.get("key") == "boss_decide_reboard_mtime_size_caliber":
                old = str(n.get("item") or "")
                if "【main 追加式订正 2026-11-24 05:3x" not in old:
                    n["item"] = old + BOSS_ITEM_APPEND
                    print("  ✅ 就地追加 boss need item: boss_decide_reboard_mtime_size_caliber")
                else:
                    print("  ★boss need item 已有本次追加, 跳过")
                break

    frag_write.update_fragment("main", mutate)
    after = md5(PM)
    print("  写后 pm.yaml md5 = %s" % after)

    # ★逐条比对: 除本次动的 4 条外, 旧条目零变化★
    d1 = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    touched = {"iss372_need_main_batch_channel_patches",
               "iss372_need_main_decide_reboard_mtime_size",
               "iss372_need_main_refresh_pinned_gates_manifest",
               "boss_decide_reboard_mtime_size_caliber"}
    lost = 0
    for (sect, key), old in snap0.items():
        new = None
        for e in (d1.get(sect) or []):
            if isinstance(e, dict) and e.get("key") == key:
                new = dict(e)
                break
        if new is None:
            print("  ❌ 条目丢了: %s[%s]" % (sect, key))
            lost += 1
            continue
        if key in touched:
            continue
        if {k: v for k, v in old.items() if k != "value"} != {k: v for k, v in new.items() if k != "value"}:
            print("  ❌ 非目标条目被改: %s[%s]" % (sect, key))
            lost += 1
    print("  ★旧条目丢失/被改 = %d ⇒ %s" % (lost, "✅ 零内容丢失" if lost == 0 else "❌"))
    return lost == 0


# ===================================================================== 阶段 3 · issue_log (追加式)
ISS372_NOTE = (
    "★2026-11-24 05:3x main 【独立复核 ISS-372 cont3】★★ ★**本条是【追加式留痕】·★老字一字未删·★不改 status/verify_result★**★ "
    "★**① cont3 交卷已独立复核通过 (★main 本机实跑·不抄 agent 报告★)★**: 三件交付物 md5/字节数逐字与 agent 自报值相同 "
    "(清账页 94270 B `0ba9dfce` / 自守闸 33655 B `2099ca42` / 交卷页 66638 B `fb782450`) + 受保护件 19 条 md5 逐条同基线 (★动 0★) + "
    "零落表 3 件同基线 + 自守闸裸跑 rc=0 (7/7) + --selftest rc=0 (10/10 ALL TESTS PASS) + merge rc=0 + gate_check rc=0 (Q1 18/18) + "
    "零挂链 + `state/board_md5_pinned_gates.json/.md` md5 未动 ⇒ ★**板三项 (md5 `611b869e13518c3c023fb178f91a0075` / mtime "
    "`2026-11-06 07:07:17.362193413` / size 4940213) 逐字节未动 ⇒ G1 仍开, 不许投板** ★ "
    "★**② cont3 的两条主张 main 已复现 (★沙盒实跑·★tmp/iss372_verify 已清理★)★**: ① **闸 G 源码零个 32 位字面量** (grep 命中 0) "
    "⇒ 靠页面内嵌基线钉板 md5 ⇒ ★**上一趟只扫 .py 字面量的 H4 确实抓不到它 (★真盲区·★child 修对了★)** ★ "
    "② **P-F 插 6 行 ⇒ 闸 G 的 W2 当场红** (d1_current_board 287⇒293 ⇒ W2 5 行全红) ⇒ **跨闸耦合成立** ★ "
    "★**③ ★★main 本轮另撞出第二层耦合 (★不在 child 的 U8 答案里★)★★**: ISS-372 自守闸自己的 §1 清单钉的是 **(file, line) 对** ⇒ "
    "H1 【双向】判红 (扫到而清单没登记 ⇒ 红; 清单登记了而盘上扫不到 ⇒ 红) ⇒ ★**P-C/P-D/P-F/P-G 每一条都在插行 ⇒ 每一条都会把 §1 "
    "钉的那一行挪走 ⇒ 改板当天自守闸【自己】当场红** ⇒ ★**⇒ 批次不是 5 件, 是 6 件: 第 6 件 = 重生成清账页 §1 机器块 + 逐行同步 §1 表格** "
    "⇒ ★**且现有两条重生成路都不够 (★write_manifest() 注释写明「只用于 --selftest 的沙盒副本」; ★gen_manifest.py 只写 tmp/ ⇒ 不回写真件★) "
    "⇒ 批次前必须先把「真件重生成」这条路走通** ⇒ ★**child 建议的「落完重跑 T0~T5」覆盖 7 道板闸, 【不含】自守闸自己 ⇒ 光重跑抓不到这层★** ★ "
    "★**④ U8 / U9 / U10 三条 main 已裁 (★详见 pm.yaml answers 同 key★)★**: U8 = **6 件批** (★5 补丁 + §1 重生成 + manifest 刷新 + 挂链 + "
    "留痕 + 闸读数表复跑·★批内顺序已给★) · U9 = **与 U3 同一票** ⇒ 并进既有 boss key `boss_decide_reboard_mtime_size_caliber`, "
    "★不新造 key ⇒ 老板侧待拍板面件数不变 (仍 11 件)★ · U10 = **收集口径放宽到类 B** ⇒ 刷新后应有内容 = **9 + 5 + 2 = 16 条** ★ "
    "★**⑤ 一处留证内部不一致 (★不影响结论·★但引用时只准引 md5 不准引件件数★)★**: cont3 交卷页里同一批受保护件出现 **15 / 18 / 19 / 20 / 22** "
    "五个不同件数 (★留证文件 `logs/iss372/12_boundary_evidence_cont1.txt` 的两段标题写「20 件」与「3 件」, 实际列出 19 条与 4 条★) ⇒ "
    "★**但 24 条 md5 逐条实测全同 ⇒ 边界结论成立·★只是计数标签乱**★ ★ "
    "★**⑥ 本单自守闸在签收后 4 小时真的红过一次 (★child 的招牌结论·★机制成立★)★**: ISS-375 (02:05) / ISS-378 (02:45) 新落两道闸都硬钉板 md5 "
    "且无合法改板通道 ⇒ 闸当场红 ⇒ 「下一道新闸再硬钉板 md5 时当场被抓住」不是设计, 是已发生的事实 ★ "
    "★**⑦ 一处闸自己的口径缺陷 (★main 亲撞·★不是 agent 的越界★)★**: 重跑本单签收闸 `state/_apply_20260723_2240_main_sign_iss369_371_372.py` "
    "的「别人的分片零本单登记条目」判据 ⇒ **报红 6 条** ⇒ ★**逐条查实: 那 6 条全是【main 自己】11-23 22:55 写进 pm.yaml 的答案 "
    "(key = `iss372_need_main_*`·★那是 main 回 sw-lead 的 need·★机制上正常·★不是 sw-lead 越界★) ⇒ ★**⇒ 该判据把「main 答过 need」误判成"
    "「agent 越界写别人分片」⇒ ★该签收闸对本单【已不可重跑】(★本单 status 早已 verified·★不需重签★)·★但同类判据在其他单上会误报·★已登记待修★** ★"
    "★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 未替老板拍板 · 未新增拍板项 ★**"
)


def apply_issue_log():
    print("\n" + "=" * 90)
    print("★阶段 3 · issue_log.yaml (★追加式·★老字一字未删★)")
    print("=" * 90)
    src = read_lines(LOG)
    before = md5(LOG)
    i = src.find("\n- id: ISS-372")
    if i < 0:
        raise SystemExit("★ISS-372 段没定位到 ⇒ 中止★")
    j = src.find("\n- id: ", i + 10)
    if j < 0:
        j = len(src)
    seg = src[i:j]
    if "  note_addendum:" in seg:
        print("  ★本单已有 note_addendum ⇒ 不重复追加 (★跳过★)")
        return True
    anchor = "\n  dispatched_at:"
    k = seg.find(anchor)
    if k < 0:
        raise SystemExit("★ISS-372 段里找不到 dispatched_at ⇒ 中止★")
    add = "\n  note_addendum: '%s'\n" % ISS372_NOTE.replace("'", "''")
    new_seg = seg[:k] + add + seg[k:]
    new_src = src[:i] + new_seg + src[j:]

    bak = LOG + ".bak_%s_main_iss372_cont3_note" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(new_src)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, LOG)

    after = md5(LOG)
    # ★自检: 除 note_addendum 外其余字节必须完全一致★
    d0 = yaml.safe_load(src)
    d1 = yaml.safe_load(read_lines(LOG))
    i0 = {x.get("id"): x for x in (d0.get("issues", d0) if isinstance(d0, dict) else d0)}
    i1 = {x.get("id"): x for x in (d1.get("issues", d1) if isinstance(d1, dict) else d1)}
    assert set(i0) == set(i1), "★issue_log 条目集合变了 ⇒ 中止★"
    for iid in i0:
        a = dict(i0[iid])
        b = dict(i1[iid])
        if iid == "ISS-372":
            a.pop("note_addendum", None)
            b.pop("note_addendum", None)
        assert a == b, "★%s 除 note_addendum 外还有别的变化 ⇒ 中止★" % iid
    print("  ★issue_log 写前 md5 = %s" % before)
    print("  ★issue_log 写后 md5 = %s" % after)
    print("  ★备份 = %s" % os.path.basename(bak))
    print("  ★自检: 条目集合不变 + 除 ISS-372.note_addendum 外零变化 ⇒ ✅")
    return True


# ===================================================================== 阶段 4 · 一页 (追加式)
ONEPAGER_SECTION = """

## ★★㉟ 【2026-11-24 05:3x · 追加式】★ ISS-372 cont3 (sw-lead) 独立复核通过 + ★★main 另撞出【第二层耦合】⇒ 批次从 5 件变 6 件★★ + ★★U8 / U9 / U10 三条已裁★★

★**① cont3 已独立复核通过 (★main 本机实跑·不抄 agent 报告★)★**: 三件交付物 md5/字节数逐字与 agent 自报值相同 · 受保护件 19 条 md5 逐条同基线 (动 0) · 零落表 3 件同基线 · 自守闸裸跑 rc=0 (7/7) · `--selftest` rc=0 (10/10 ALL TESTS PASS) · merge rc=0 · gate_check rc=0 (Q1 18/18) · 零挂链 · `state/board_md5_pinned_gates.json/.md` md5 未动 ⇒ ★**板三项逐字节未动 ⇒ G1 仍开, 不许投板** ★

★**★★② ★★main 本轮撞出【第二层耦合】(★不在 agent 的答案里·★本轮最要紧的一条★)★★★**: ISS-372 自守闸自己的 §1 清单钉的是 **(file, line) 对** ⇒ H1 【双向】判红 (★扫到而清单没登记 ⇒ 红; ★清单登记了而盘上扫不到 ⇒ 红★) ⇒ ★**P-C / P-D / P-F / P-G 每一条都在插行 ⇒ 每一条都会把 §1 钉的那一行挪走 ⇒ 改板当天自守闸【自己】当场红** ⇒ ★**⇒ 「板那一趟」的通道补丁批 = 【6 件】不是 5 件: ① 5 条通道补丁 → ② 重生成清账页 §1 机器块 + 逐行同步 §1 表格 → ③ 刷 `state/board_md5_pinned_gates.json/.md` → ④ 挂新闸进 `EXTRA_GATES` → ⑤ `issue_log` 留痕 → ⑥ 重跑 T0~T5 七闸读数表** ⇒ ★**且现有两条重生成路都不够 (★`write_manifest()` 注释写明「只用于 --selftest 的沙盒副本」·★`gen_manifest.py` 只写 `tmp/` ⇒ 不回写真件★) ⇒ 批次前必须先把「真件重生成」这条路走通** ⇒ ★**★agent 建议的「落完重跑 T0~T5」覆盖 7 道板闸, 【不包含】自守闸自己 ⇒ 光重跑抓不到这一层★★** ★

★**③ U8 / U9 / U10 三条 main 已裁 (★main 地界·★一件没代老板拍★)★**
| # | need key | main 的裁决 |
|---|---|---|
| U8 | `iss372_need_main_batch_channel_patches` | ★**批 = 6 件** (★不是 5 件★) ⇒ 合成一批落 · 批内顺序已给 (★补丁 → §1 重生成 → manifest 刷新 → 挂链 → 留痕 → 闸读数表复跑★) ⇒ ★**时机 = 「板那一趟」开工前同批** (★承 11-23 22:5x 裁决★) |
| U9 | `iss372_need_main_decide_reboard_mtime_size` | ★**与 U3 是同一个问题的第二个受影响闸** ⇒ 并进既有老板待拍项 `boss_decide_reboard_mtime_size_caliber` · ★**不新造 key** ⇒ ★**老板侧待拍板面件数不变 (仍 11 件)** ⇒ 闸 G 的 W7 实读确认: 它比 `board_md5` + `board_size` + `board_mtime`(纳秒) 三项 ⇒ 那一票若采纳「mtime+size 一并进 reboard 原子」⇒ ★**一票解掉 F5 / A-5 / W7 三处红** |
| U10 | `iss372_need_main_refresh_pinned_gates_manifest` | ★**收集口径放宽到类 B** (★闸自己算盘上板 md5 且期望值来自文档★) ⇒ 刷新后应有内容 = ★**9 + 5 + 2 = 16 条**★ (★新增 5 道闸 + 口径补 `state/land_v_values.py` 与类 B 闸★) ⇒ ★**刷新前必须先改生成器的收集口径, 否则刷出来的还是漏的** ⇒ ★**时机 = 与 6 件批同批** |

★**④ 一处留证内部不一致 (★不影响结论★)★**: cont3 交卷页里同一批受保护件出现 **15 / 18 / 19 / 20 / 22** 五个不同件数 (★留证文件两段标题写「20 件」「3 件」, 实际列出 19 条与 4 条★) ⇒ ★**24 条 md5 逐条实测全同 ⇒ 边界结论成立·★只是计数标签乱⇒ 引用时只准引 md5, 不准引件件数** ★

★**⑤ 一处闸自己的口径缺陷 (★main 亲撞·★不是 agent 越界★)★**: 本单签收闸的「别人的分片零本单登记条目」判据, 在本单已由 main 自己答过 need 之后重跑 ⇒ 报红 6 条 ⇒ ★**逐条查实: 那 6 条全是 main 自己 11-23 22:55 写进 pm.yaml 的答案 (key = `iss372_need_main_*`·★机制上正常★) ⇒ 该判据把「main 答过 need」误判成「agent 越界写别人分片」⇒ 同类判据在其他单上会误报·★已登记待修★** ★

★**板面**: md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ ★**19 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★
★**外发段**: ★**恒空** (★老板 2026-11-12 02:02「不再发信, 全靠自己查」★)
"""


def apply_onepager():
    print("\n" + "=" * 90)
    print("★阶段 4 · DECISION_ONE_PAGER_2026-11-22.md (★追加式·★老字一字未删★)")
    print("=" * 90)
    src = read_lines(ONEPAGER)
    before = md5(ONEPAGER)
    if "§㉟" in src:
        print("  ★§㉟ 已存在 ⇒ 跳过 (★防重复★)")
        return True
    bak = ONEPAGER + ".bak_%s_main_iss372_cont3" % STAMP
    shutil.copy2(ONEPAGER, bak)
    tmp = ONEPAGER + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(src + ONEPAGER_SECTION)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, ONEPAGER)
    after = md5(ONEPAGER)
    assert read_lines(ONEPAGER).startswith(src), "★一页老字被改 ⇒ 中止★"
    print("  ★一页 写前 md5 = %s" % before)
    print("  ★一页 写后 md5 = %s" % after)
    print("  ★备份 = %s" % os.path.basename(bak))
    print("  ★自检: 老字逐字保留 + 只在末尾追加 ⇒ ✅")
    return True


# ===================================================================== 阶段 5 · LESSONS (main 独占写)
LESSON = """

## ★L-21 · ★★闸清单钉 (file, line) 对 ⇒ 任何「往被钉文件里插行」的补丁都会让清单自己过期 ⇒ 清单与补丁必须同批重生成★★

★**实测 (2026-11-24 05:1x, main 本机沙盒 `tmp/iss372_verify` 实跑 · 已清理)★**: ★**ISS-372 自守闸的 §1 机器块钉的是 (file, line) 对** ⇒ H1 【双向】判红:
① 扫到而清单没登记 ⇒ 红 ② ★**清单登记了而盘上扫不到 ⇒ 红 (★这才是「清单过期」★)** ★
★**⇒ 往 `SW/tools/check_fp_truth_read.py` 文件头插 3 行 ⇒ 板 md5 字面量从 `:87` 挪到 `:90` ⇒ 自守闸当场红 (★两条错误: 漏登记 + 清单过期★)** ★
★**⇒ 往 `SW/tools/check_debug_pin_order_contract.py` 插 6 行 ⇒ 闸 G 的 W2 当场红 (★`d1_current_board` 287⇒293 ⇒ 5 行全红★)** ★
★**⇒ 通则 ①**: ★**凡是「清单钉行号」型资产 (★SW 域板 md5 引用面清单 / `board_md5_pinned_gates` 表 / 闸 G 的「需改代码」行号表★), 一旦有补丁要往被钉文件里插行 ⇒ ★**那份清单就同批过期 ⇒ 补丁与清单重生成必须同批落 (★拆批即红·★而且红的是【清单自己】·★现场最容易误读成「板坏了」★)★** ★
★**⇒ 通则 ②**: ★**「改完跑一遍闸」不等于「改完这套机制自洽」·★闸的读数表覆盖几道闸要逐条数清 (★本轮 T0~T5 覆盖 7 道板闸, 【不含】第 8 道自守闸自己 ⇒ 光重跑抓不到第二层耦合★)★** ★
★**⇒ 通则 ③**: ★**清单的重生成工具必须真的能写回真件** ⇒ ★**只写沙盒副本的工具 (★`write_manifest()` 注释自己写明「只用于 --selftest 的沙盒副本」★) 或只写 `tmp/` 的脚本 (★`gen_manifest.py`★) ⇒ 【都不算】·★批次前必须先把这条路走通★** ★
★**⇒ 通则 ④**: ★**「代拍板面件数」这类数不许因一个闸受影响就 +1** ⇒ ★**同一票能解多个闸 ⇒ 并进既有 key ⇒ 件数不变 (★本轮 U9 并进 `boss_decide_reboard_mtime_size_caliber` ⇒ 仍 11 件★)** ★

## ★L-22 · ★★闸自己的口径缺陷: 「别人的分片零本单登记」会把【main 自己答过的 need】误判成【agent 越界】★★

★**实测 (2026-11-24 05:2x, main 本机重跑签收闸发现)★**: 重跑 `state/_apply_20260723_2240_main_sign_iss369_371_372.py ISS-372 --check-only` ⇒ ★**报红 1 条: 「别人的分片 (pm/hw/mech) 零本单登记条目 — 越界 6」** ★ ⇒ ★**逐条查实: 那 6 条全是【main 自己】11-23 22:55 写进 pm.yaml 的答案 (key = `iss372_need_main_*`·★机制上完全正常: main 答 sw-lead 的 need 就落在 main 自己的分片 pm.yaml★) ⇒ ★**⇒ 该判据按「key 里含本单单号」扫, 分不清「main 答过 need」与「agent 越界写别人分片」⇒ 同一个 key 在 pm.yaml 的【answers】段是正常、在【artifacts】段才可疑 ⇒ 判据须按 section 区分 (★或按「to == 本单 owner」排除★)** ★
★**⇒ 通则**: ★**判据里的「谁的锅」要落到 section / to 字段上, 不能只落到 key 子串上·★否则 main 答一次 need 就让那道签收闸永久不可重跑 (★本单 status 早已 verified ⇒ 不影响结论·★但同类判据在其他单上会误报·★已登记待修★)** ★
★**★与 L-21 合看**: ★**两条都是同一类病: 【闸自己的口径】没写清 ⇒ 闸报的红不能直接读成「产物坏了」·★必须逐条查实归属 (★铁律⑩-j 的又一次复现★)** ★
"""


def apply_lessons():
    print("\n" + "=" * 90)
    print("★阶段 5 · state/LESSONS.md (★main 独占写·★追加式★)")
    print("=" * 90)
    src = read_lines(LESSONS)
    before = md5(LESSONS)
    if "L-21" in src and "L-22" in src:
        print("  ★L-21/L-22 已存在 ⇒ 跳过")
        return True
    bak = LESSONS + ".bak_%s_main_iss372_cont3" % STAMP
    shutil.copy2(LESSONS, bak)
    tmp = LESSONS + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(src + LESSON)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, LESSONS)
    assert read_lines(LESSONS).startswith(src), "★LESSONS 老字被改 ⇒ 中止★"
    print("  ★LESSONS 写前 md5 = %s" % before)
    print("  ★LESSONS 写后 md5 = %s" % md5(LESSONS))
    print("  ★备份 = %s" % os.path.basename(bak))
    print("  ★自检: 老字逐字保留 + 只在末尾追加 ⇒ ✅")
    return True


def main():
    # ★开工侧板指纹 (★纳秒★)★
    m0, ns0, sz0 = board_fp()
    print("★开工侧板指纹: md5=%s mtime_ns=%d size=%d" % (m0, ns0, sz0))

    ok = verify()
    if not ok:
        print("\n★★阶段 1 有红项 ⇒ 中止落盘 (★fail-closed★)★★")
        return 1

    apply_pm()
    apply_issue_log()
    apply_onepager()
    apply_lessons()

    # ★收工侧板指纹 (★三项必须与开工侧逐字相同★)★
    m1, ns1, sz1 = board_fp()
    print("\n" + "=" * 90)
    print("★收工侧板指纹: md5=%s mtime_ns=%d size=%d" % (m1, ns1, sz1))
    same = (m0 == m1 == BOARD_MD5 and ns0 == ns1 == ns_of(BOARD_MTIME) and sz0 == sz1 == BOARD_SIZE)
    print("★零写板自证: %s" % ("✅ 三项逐字节未动" if same else "❌ 板动了 ⇒ 中止"))
    if not same:
        return 1

    rc, _ = sh("python3 state/merge.py")
    print("★收尾 merge.py rc=%d" % rc)
    rc2, o2 = sh("python3 state/gate_check.py")
    print("★收尾 gate_check.py rc=%d (Q1 18/18: %s)" % (rc2, "18/18" in o2))
    print("\n★全流程收工 (★零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 未代老板拍板★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
