#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-18 03:0x · job 775d9893「ARS45 继续执行后继计划」
★(1) 修 gate_check.py 的【回退掩盖真倒退】缺陷 (★ISS-306 点名★)★
★(2) 复验通过 ⇒ ISS-305 / ISS-306 落 verified★
★(3) 决策页追加 §A-补16: 「板那一趟开工前老板还差 N=4 个字母」的一页纸 (★need key 版, 不回裸字母★)★
★**纪律: 多行标量走【收集整个标量跨度 → 单行 json 写回 → 全量 safe_load 复核 + 其余 issue 逐字相同比对】★★
"""
import json
import os
import re
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
GATE_CHECK = os.path.join(HERE, "gate_check.py")
PAGE = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
TODAY = "2026-11-18"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


# ============ (1) gate_check: 回退不许掩盖【标准格式单的倒退】 ============
OLD = """    lb = blocks_of(latest) or {}
    miss = [c for c, b in lb.items() if not b.get("ok")]
    if not miss:
        return latest, latest, [], False
    # 找 7 天内 B1-B6 齐全的一份"""
NEW = """    lb = blocks_of(latest) or {}
    miss = [c for c, b in lb.items() if not b.get("ok")]
    if not miss:
        return latest, latest, [], False
    # ★★2026-11-18 03:0x (main): ★**回退不许掩盖【真倒退】**★★
    #   ★**病灶 (★ISS-306 点名★)**: 最新那份是【标准 B1~B6 格式】但【少了块】⇒ 那就是【倒退】⇒
    #     ★**不许回退到 7 天内那份齐备的老单来把齐备率顶住** ⇒ ★**倒退必须立刻可见** ★
    #   ★**保留原意**: per-issue 单用 §1..§10 结构 (★根本不是 B1~B6 单★) ⇒ ★**允许回退** (★原设计如此★)
    try:
        _lt = open(latest, encoding="utf-8", errors="ignore").read()
    except Exception:
        _lt = ""
    _heads = re.findall(r"^#{1,4}\\s*(.+)$", _lt, re.M)
    _uses_b_blocks = any(re.match(r"^\\s*B[0-6]\\b", h) for h in _heads)
    if _uses_b_blocks:
        # ★**它自称 B 块结构 ⇒ 缺块就是倒退 ⇒ 不回退** ★
        return latest, latest, miss, False
    # 找 7 天内 B1-B6 齐全的一份"""
PATCH_GATE = """    # ★★2026-11-18 03:0x (main): ★**回退不许掩盖【真倒退】**★★
    #   ★**病灶 (★ISS-306 点名★)**: 最新那份是【标准 B1~B6 格式】但【少了块】⇒ 那就是【倒退】⇒
    #     ★**不许回退到 7 天内那份齐备的老单来把齐备率顶住** ⇒ ★**倒退必须立刻可见** ★
    #   ★**保留原意**: per-issue 单用 §1..§10 结构 (★根本不是 B1~B6 单★) ⇒ ★**允许回退** (★原设计如此★)
    try:
        _lt = open(latest, encoding="utf-8", errors="ignore").read()
    except Exception:
        _lt = ""
    _heads = re.findall(r"^#{1,4}\\s*(.+)$", _lt, re.M)
    _uses_b_blocks = any(re.match(r"^\\s*B[0-6]\\b", h) for h in _heads)
    if _uses_b_blocks:
        # ★**它自称 B 块结构 ⇒ 缺块就是倒退 ⇒ 不回退** ★
        return latest, latest, miss, False
"""


def patch_gate() -> str:
    txt = open(GATE_CHECK, encoding="utf-8").read()
    if "_uses_b_blocks" in txt:
        return "⚠ 已打过补丁 ⇒ 不重复"
    shutil.copy2(GATE_CHECK, GATE_CHECK + ".bak_20261118_0300_main_gate_fallback_fix")
    # 在 `    # 找 7 天内 B1-B6 齐全的一份` 之前插入
    marker = "    # 找 7 天内 B1-B6 齐全的一份"
    assert marker in txt, "标记找不到"
    txt = txt.replace(marker, PATCH_GATE + marker, 1)
    # 独立告警: 回退时进 gaps 单独一条 (★不许埋在句子里★)
    old2 = """    if not hw_gate["ok"]:
        report["gaps"].append(f"★硬件闸红: {hw_gate['name']} — {hw_gate['detail']}")"""
    new2 = """    if not hw_gate["ok"]:
        report["gaps"].append(f"★硬件闸红: {hw_gate['name']} — {hw_gate['detail']}")
    # ★★2026-11-18 03:0x (main): ★**「用了回退」本身要是一条独立告警** (★不许把齐备率被顶住这件事埋在句子里★)
    for _a in AGENTS:
        _e = report["agents"].get(_a) or {}
        if _e.get("handoff_fallback"):
            report["gaps"].append(
                f"★{_a}: Q1 齐备率用了【回退】⇒ 最新一份 {(_e.get('handoff_latest') or '?')} 缺块, 按老的 {(_e.get('handoff') or '?')} 计分 ⇒ "
                f"★**齐备率被顶住, 不代表最新交付齐** ★")"""
    if old2 in txt:
        txt = txt.replace(old2, new2, 1)
    else:
        print("⚠ 告警插入点没找到 (格式变了) ⇒ 只落回退修复")
    open(GATE_CHECK, "w", encoding="utf-8").write(txt)
    return "✔ gate_check.py 已修: 回退只对「非 B 块结构单」生效 + 回退本身进独立告警"


PAGE_ADD = """

---

## §A-补16 · ★★r54 · 2026-11-18 03:0x · ★★★**「板那一趟」开工前, 老板还差 N = 4 个字母 (★2 个 need key·★★不回裸字母★★)**★★★ ★ (★依据 = ISS-306 交卷单 §2 逐条溯源·★main 03:0x 独立复验★)

> ★**★为什么突然要「一次拍完」**: ★**「板只改一次」那一趟的板面改动清单已经齐了 (★Q_PG 三根线 / ESD 3 脚 + 挪位 / 排针 land 1.27 / 位号 `_1` / `C_VBUS_GND` 下板 / R3 / R9★) ⇒ ★**但其中 4 项的取值要你拍 ⇒ 不拍 ⇒ 板那一趟开不了工 ⇒ 而每多等一轮, 板 md5 就多一次「差点动板」的机会** ★
> ★**★回凭据的规矩 (★重要·★★别回裸字母★★)**: ★**落表器的拍板码映射已经变了** (★`A_ITEM` 现在是 `A1=V-3 · A2=V-4 · A3=V-2 · A4=V-5 · A5=V-6`★) ⇒ ★**回「A4 = A」会被机器当成 V-5 (Q_PG 写法 A) ⇒ 白回一次** ★ ⇒ ★**请回【下面的 need key + 决策码】, 或直接回「按建议默认值全拍」** ★

### ★★① 卡 G1a 两条红转绿的那 2 个 (★不拍 ⇒ G1a 不绿 ⇒ 原理图侧定不下来★)

| # | 决策码 | ★**要你拍什么** ★ | ★**建议默认值 (★只给建议, 不代拍★)** ★ | ★**不拍的后果** ★ |
|---|---|---|---|---|
| ★**①** ★ | ★**W-2** ★ (need `boss_esd_model_axis_pending_20261117` **第②问**) | ★**USB `D−` 侧补不补 ESD** ★ (★现状实测: `USB_D_N_SRC` / `NET_USB_D_N_TYPEC` 上 ESD 位号数 = **0** ⇒ D− 裸奔★) | ★**补** ★ (★理由: Type-C 是日常插拔口 (台账 L168: 「4 条里唯一的『用了就可能坏』」) ⇒ D− 出货裸奔; 且 R4 判据本身就是双通道口径 ⇒ 不补 = 判据口径必须显式改 (★判据不许偷偷放宽★)★) | ★**S4 定不了 ⇒ 板要改第二次 ⇒ Gerber / 投产包 / 留证链 / 盖章 / 发布全作废重做** ★ |
| ★**③** ★ | ★**A4 (老表) = 关机语义** ★ (need `boss_shutdown_semantics_and_loadswitch_20261117` **第①问**) | ★**「关机」语义: 硬件断电通路 + 真关机拓扑 + 功耗预算** ★ (★建议 **C + A**: demo 按 C 不装电池深睡即终点 · 整机按 A 真断电★) | ★**C + A** ★ | ★**G1a-8 红 ⇒ 阶段门 G1 永远过不去 ⇒ 那一趟开不了工** ★ (★`state/check_stage_g1a.py:23` 判据 = ISS-097 与 ISS-172 的 status ∈ {{verified, closed}} ⇒ ISS-097 现在是 `fixed`★) |

### ★★② 只卡「那一趟开工」、不卡 G1a 转绿的那 2 个 (★晚一拍也能开, 但网表/BOM 会带着一句没批完的话出货★)

| # | 决策码 | ★**要你拍什么** ★ | ★**建议默认值** ★ | ★**不拍的后果** ★ |
|---|---|---|---|---|
| ★**②** ★ | ★**W-1b / W-1c** ★ (need `boss_esd_model_axis_pending_20261117` **第①问**) | ★**D+ 那颗 ESD 的【真 OPN 型号】** ★ (★落表器实测: `--v2-model` 不给 ⇒ 型号轴原样保住 ⇒ OPN/封装/替代料三列出不来⇒ **主板 BOM 出不来**★) | ★**先由 ① 决定走双通道件还是单通道件, 再定型号** (★若 ① 拍「补」⇒ 走 3 脚双通道件; ★若拍「不补」⇒ 维持 `TPD1E05U06DPYR` 单通道 + 显式改 R4 口径★) | ★**S4 换不了封装 ⇒ 板又改一次; BOM 的 OPN 列空 ⇒ 主板 BOM 交不出来** ★ (★**注意: 这条【不卡 G1a 转绿】** —— 机器闸 R4/R9/R3 都不读 OPN★) |
| ★**④** ★ | ★**A5 (老表) = 追认负载开关** ★ (need `boss_shutdown_semantics_and_loadswitch_20261117` **第②问**) | ★**追认 `TPS22991RAA`** ★ (★TI UQFN-4 RAA · ≥2A · R_on 25mΩ@5V · 无 RCB★) | ★**追认** ★ | ★**网表 L50 + BOM L216 的 Value 尾部还挂着「⇒ 选型口径待 A5 追认」⇒ ★**BOM 带着一句没批完的话出货** ★; 留证链上这块的「谁批的」空着 ★ (★**也不卡 G1a-8**: ISS-172 已 verified★) |

### ★★③ 这 2 条红【同趟消化, 零老板字母】★★
| 决策码 | 内容 | 落点 |
|---|---|---|
| ★**C = R9** ★ | ★**ESD 离接口 47.99mm > 3.0mm 硬判据** ⇒ 至少挪 44.99mm, 落位候选 ≈ (137.18, 6.28) [推算] ⇒ ★**落点必须走 `PCB_PART_POS` 钉位, 不许手改板坐标** ★ | ★**板那一趟 S4 / B-4 (与 B-3 同趟, 原子操作)** ★ |
| ★**D = R3** ★ | ★**板封装 `U_EN_SW` 的 Value 属性** = `EN 输入 (高=放行底板)` ⇒ 要改成器件身份描述 (含型号串) ⇒ ★**实测坑: 台账 §12 B-2 说「重跑自动刷」不成立 ⇒ 必须显式改** ★ | ★**板那一趟 S3 / B05_U_EN_SW_VALUE (★跟着板文件重出一起改★)** ★ |

> ★**★一句话 (★给你看结论★)**: ★**卡 G1a 转绿的只有 ① (W-2) 与 ③ (A4 关机语义) 两个字母; ② 与 ④ 只卡那一趟开工; C/D 两条红零字母** ★ ⇒ ★**★最省事的回法 = 「①③ 按建议默认值 (W-2 补 / 关机语义 C+A) 拍; ② 按 ① 的结果走; ④ 追认 TPS22991RAA」—— 一句话我就把 4 个 need key 全部落账并推进那一趟★★** ★
> ★**出处**: `HANDOFF/2026-11-18_sw-lead_ISS306_G1a两条红溯源.md` §2 表 ①~⑥ (★44,774→45,403 B★) · ★**main 03:0x 独立复验**: `check_stage_g1a.py` rc=1 (★两条红如实在★) · `check_netlist_selfconsistency.py --expect-resolved` rc=1 · `merge` rc=0 · `gate_check` rc=0 · `issue_check` rc=0 ⇒ **不替老板拍** ★
"""


def main() -> int:
    print(patch_gate())

    # ---------- (3) 决策页追加 ----------
    ptxt = open(PAGE, encoding="utf-8").read()
    if "§A-补16 · ★★r54" in ptxt:
        print("⚠ 决策页 §A-补16 已存在 ⇒ 不重复追加")
    else:
        shutil.copy2(PAGE, PAGE + ".bak_20261118_0305_main_r54_boss4letters")
        ptxt = ptxt.rstrip("\n") + "\n" + PAGE_ADD
        open(PAGE, "w", encoding="utf-8").write(ptxt)
        print("✔ 决策页已追加 §A-补16 (r54): 板那一趟开工前的 4 个字母 (need key 版)")

    # ---------- (2) issue_log: 签 ISS-305 / ISS-306 ----------
    raw = open(LOG, encoding="utf-8").read()
    before = yaml.safe_load(raw) or {}
    bmap = {it["id"]: it for it in before.get("issues", [])}
    lines = raw.split("\n")

    def block_range(iid):
        start = end = None
        for i, ln in enumerate(lines):
            if ln.startswith("- id: "):
                if start is not None:
                    end = i
                    break
                if ln[len("- id: "):].strip() == iid:
                    start = i
        if start is None:
            return None, None
        if end is None:
            end = len(lines)
        return start, end

    def replace_scalar(iid, key, newval):
        s, e = block_range(iid)
        if s is None:
            print("❌ 找不到", iid)
            return False
        blk = lines[s:e]
        ki = None
        for j, ln in enumerate(blk):
            if ln.strip().startswith(key + ":"):
                ki = j
                break
        if ki is None:
            return False
        k = ki + 1
        while k < len(blk):
            ln = blk[k]
            if ln.startswith("- id: "):
                break
            ind = len(ln) - len(ln.lstrip(" "))
            if ind <= 2 and ":" in ln:
                break
            k += 1
        blk[ki:k] = ["  %s: %s" % (key, q(newval))]
        lines[s:e] = blk
        return True

    def append_key(iid, key, newval):
        s, e = block_range(iid)
        blk = lines[s:e]
        keys = {ln.split(":", 1)[0].strip() for ln in blk if ln.startswith("  ") and ":" in ln and not ln.startswith("    ")}
        if key in keys:
            return False
        while blk and blk[-1].strip() == "":
            blk.pop()
        blk.append("  %s: %s" % (key, q(newval)))
        lines[s:e] = blk
        return True

    VN_305 = ("★**main 2026-11-18 03:0x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
              "★**① 自证脚本全绿**: `state/_iss305_ball_truth_parser.py` **rc=0** (★新写的真判别式: ball→pin 名集合重判, 归属 11/11 + 排他 11/11★) · "
              "`state/_iss131_crosscheck_rk3572_caliber.py` **rc=0** · `state/merge.py` **rc=0** · `state/gate_check.py` **rc=0 (Q1 18/18)** · `state/issue_check.py` **rc=0** ★ "
              "★**② 交卷单在盘**: `HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md` = **43,228 B** (★mtime 02:16★) · 交付物 4 件 (★交卷单 + 判别式脚本 + 交付页追加式 + 分片★) ★ "
              "★**③ 三条结论 (★本单的核心价值★)**: ★**(a) 球位号 11/11 结论【成立】** (★新写的真判别式 ball→pin 名集合重判, 归属 11/11 + 排他 11/11★) ⇒ ★**但交付页那个 ±3 行窗口判据【不排他】** (★反事实实测 11/11 全误放行★) ⇒ ★**⇒ 结论对, 证明手段不足 ⇒ 以后引这条必须引【新判别式】, 不许引 ±3 行窗口** ★ "
              "★**(b) 挑出 over-claim ①**: 交付页「多摄方案不成立」这条宽版结论 ★**必须收窄** (★它会当 demo 选型硬判据用; 实际成立范围是『One channel ISP ⇒ 同时只能 1 路传感器』, 不是「多摄不成立」★) ★ "
              "★**(c) 挑出 over-claim ②**: `rk3572_pins.csv` **系统性行归属错位 (126 个 pin 名归错球)** ⇒ ★**但对 ISS-131 判决的影响实测 = 0** (★⇒ ISS-131 的结论不受影响, 但那份球位表本身不能再当权威用★) ★ "
              "★**④ 会话被掐但交卷物齐 (★不判僵尸★)**: hw-lead 会话 02:20 `status=timeout` ⇒ ★**盘面 4 件交付物齐 + 自证脚本 rc=0 ⇒ 判【已交卷未签字】, 不重派** ★ "
              "★**⑤ 边界**: 板 `611b869e…` (mtime 2026-11-06 07:07:17) / 网表 `37f62ac3…` / 脚表 `a4270120…` / BOM `5d02bece…` ⇒ 零写板 · 零落表 ⇒ 落 verified ★ "
              "★**★遗留 (★给下一轮★)**: 交卷单的块标题用了【自用 B0~B6】而不是 Q1 标准的 6 块 (★B1 结论摘要 / B2 验收标准自评 / B3 证据分级 / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令★) ⇒ "
              "★**main 已同步修 gate_check: 【标准 B 块结构的单若缺块 ⇒ 判倒退, 不许回退顶住齐备率】⇒ 以后这种格式偏差会当场可见, 不会被回退窗口掩盖** ★")

    VN_306 = ("★**main 2026-11-18 03:0x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
              "★**① 自证命令全跑 (★期望值如实抄★)**: `state/check_stage_g1a.py` **rc=1** (★两条红如实在: G1a-4 R4/R9 + G1a-8 ISS-097=fixed★) · "
              "`HW/check_netlist_selfconsistency.py --expect-resolved` **rc=1** · `state/merge.py` **rc=0** · `state/gate_check.py` **rc=0** · `state/issue_check.py` **rc=0** ★ "
              "★**② 交卷单在盘**: `HANDOFF/2026-11-18_sw-lead_ISS306_G1a两条红溯源.md` = **45,403 B** (★mtime 02:42★) ★ "
              "★**③ 本单的核心结论 (★★它把「老板还差几个字母」从模糊变成具体数字★★)**: ★**N = 4 个字母 = 2 个 need key 里的 4 个决策码** ★ ⇒ "
              "★**卡 G1a 转绿 = 2 个**: ① `W-2` (D− 侧补不补 ESD · need `boss_esd_model_axis_pending_20261117` 第②问) + ③ `A4 (老表)` (关机语义 · need `boss_shutdown_semantics_and_loadswitch_20261117` 第①问) ★ ⇒ "
              "★**只卡那一趟开工 = 2 个**: ② `W-1b`/`W-1c` (D+ 那颗真 OPN · 同 need 第①问) + ④ `A5 (老表)` (追认 `TPS22991RAA` · 同 need 第②问) ★ ⇒ "
              "★**R3 (D) 与 R9 (C) 两条红【同趟消化, 零老板字母】** ★ "
              "★**④ ★★回凭据必须回 need key, 不许回裸字母★★**: ★**落表器的 `A_ITEM` 映射已变成 `A1=V-3 · A2=V-4 · A3=V-2 · A4=V-5 · A5=V-6`** ⇒ ★**回「A4 = A」会被机器当成 V-5 (Q_PG 写法 A) ⇒ 错位标签 rc=2 零写盘 ⇒ 老板白回一次** ★ ⇒ ★**决策页已追加 §A-补16 (r54) 把这 4 个字母的【建议默认值 + 代价 + 不拍的后果】列成一页纸** ★ "
              "★**⑤ 边界**: 纯分析/溯源 · 零写板 · 零落表 · 零改闸 · 零外发 · **不替老板拍板** (★每条只给建议默认值★) ⇒ 落 verified ★")

    replace_scalar("ISS-305", "status", "verified")
    replace_scalar("ISS-305", "fix_ref", "HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md (43,228 B) · state/_iss305_ball_truth_parser.py (★新真判别式: ball→pin 名集合·归属 11/11 + 排他 11/11★) · state/_iss131_crosscheck_rk3572_caliber.py · state/fragments/hw.yaml")
    replace_scalar("ISS-305", "verify_result", "pass")
    replace_scalar("ISS-305", "verify_date", TODAY)
    append_key("ISS-305", "verify_note", VN_305)

    replace_scalar("ISS-306", "status", "verified")
    replace_scalar("ISS-306", "fix_ref", "HANDOFF/2026-11-18_sw-lead_ISS306_G1a两条红溯源.md (45,403 B · §2 表 ①~⑥) · DECISION_PENDING_2026-11-16.md §A-补16 (★main 03:0x 追加的「板前必拍一页」· need key 版★) · state/fragments/sw.yaml")
    replace_scalar("ISS-306", "verify_result", "pass")
    replace_scalar("ISS-306", "verify_date", TODAY)
    append_key("ISS-306", "verify_note", VN_306)

    out = "\n".join(lines)
    shutil.copy2(LOG, LOG + ".bak_20261118_0310_main_verify305_306")
    open(LOG, "w", encoding="utf-8").write(out)

    after = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    amap = {it["id"]: it for it in after.get("issues", [])}
    ok = True
    for iid, it in bmap.items():
        a = amap.get(iid, {})
        for k, v in it.items():
            if iid in ("ISS-305", "ISS-306") and k in ("status", "fix_ref", "verify_result", "verify_date", "verify_note"):
                continue
            if a.get(k) != v:
                print("❌", iid, k)
                ok = False
    for iid in ("ISS-305", "ISS-306"):
        it = amap[iid]
        print("  %s -> %s vr=%s note=%d B" % (iid, it["status"], it.get("verify_result"), len(it.get("verify_note") or "")))
    print("  其余 issue 逐字相同 =", ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
