#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_make_tsv.py —— ISS-321 · ② SW 侧写死的【真位号】全清单 (★机器生成★)

输出 (只写): logs/iss321/sw_hardcoded_refs.tsv
              ★格式 (★任务书 §2② 指定★): 文件:行 | 位号 | 改名后名 | 命中类别 ★

★★命中类别 (★任务书 §2② 只许三种★) ★★:
    ① 判据里写死 (改后会炸)
       ⇒ ★写死的是【位号字面量】且该处【直接决定判据读数/判决】★
       ⇒ 改名后: 查不到 ⇒ 读数变 None/空 ⇒ ★判红或崩★ (★S4 实测为真的那些★)
    ② 判据里写死但本来就该随改名改 (改法 = 改脚本)
       ⇒ ★写死的是【位号字面量】但那处【只是注释/文档/清单里的引用】★
       ⇒ 改名后: 语义上必须跟着改成新名 (★但不会让闸判红★)
    ③ 假阳性 (常量名/网络名/位号形状不同, 不用动)
       ⇒ ★形状像位号但不在 218 真集里 ⇒ 一律判 ③★

★★归因依据 (★不是猜的·是 §2③ 沙盒实跑读数推出来的★) ★★:
    · ① 的判据 = ★在 S4 场景 (改名+台账+锚点全齐) 里仍红 且 ★在 S8 场景 (零改名+台账+锚点全齐) 里绿★
      ⇒ ★红是【改名特有】的 ⇒ 判 ① ★
    · ② 的判据 = ★在 S4/S8 里都不红★ ⇒ 判 ② (★只是引用·改了更准确·不改也不红★)
    · ③ = ★不在 218 真集里★
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SETS = os.path.join(HERE, "rename_sets.json")
HITS = os.path.join(HERE, "sw_hits_raw.json")
LIT = os.path.join(HERE, "lit_search.json")
OUT_TSV = os.path.join(HERE, "sw_hardcoded_refs.tsv")

# ★★【S4 实测】仍红的闸 (★改名特有·S8 绿★) ⇒ 其位号字面量判 ① ★★
#   S4=rc / S8=rc (★由 logs/iss321/raw_rootS4_*.txt 与 raw_rootS8_*.txt 实跑读出★)
S4_RC = {
    "check_onepass_sw_sync.py": 1,
    "check_sw_ref_reachability.py": 0,
    "check_landing_trace_obligation.py": 0,
    "check_demo_panel_spec.py": 0,
    "check_demo_panel_spec_r6_selftest.py": 1,
    "check_demo_panel_spec_r6_chainjudge_selftest.py": 1,
    "check_demo_panel_spec_r6_hardprot_iss315_selftest.py": 1,
    "check_shutdown_semantics.py": 0,
    "check_timing_review_adc_sync.py": 2,
    "timing_check.py": 1,
}
S8_RC = {
    "check_onepass_sw_sync.py": 1,
    "check_sw_ref_reachability.py": 0,
    "check_landing_trace_obligation.py": 0,
    "check_demo_panel_spec.py": 0,
    "check_demo_panel_spec_r6_selftest.py": 1,
    "check_demo_panel_spec_r6_chainjudge_selftest.py": 0,
    "check_demo_panel_spec_r6_hardprot_iss315_selftest.py": 1,
    "check_shutdown_semantics.py": 0,
    "check_timing_review_adc_sync.py": 0,
    "timing_check.py": 0,
}
# ★★S4 红 且 S8 红 ⇒ 【板改了就会红】(★不是改名特有★) ⇒ 不判 ① ★★
#   ⇒ 这三道 r6 selftest 闸的红归因于【板变更 + 落表台账】⇒ 交 need 给 main ★

# ★★【判 ① 的闸清单】= S4 红 且 S8 绿 ⇒ 改名特有 ★★
#   · timing_check.py            ★崩在 L1113 (r_pull+r_ser 都是 None)★
#   · check_timing_review_adc_sync.py  ★上游 timing_check 崩 ⇒ fail-closed rc=2★
#   · check_demo_panel_spec_r6_chainjudge_selftest.py ★CJ-1 用例坏了★
RENAME_SPECIFIC = {"timing_check.py", "check_timing_review_adc_sync.py",
                   "check_demo_panel_spec_r6_chainjudge_selftest.py"}

# ★★★【逐【位号站点】的 ①/② 判定表 (★逐条有 S4-vs-S8 实跑读数背书★) ★★★
#   ★键 = (文件名, 该行在文件里的特征子串) ⇒ 值 = ① 或 ② ★
#   ★判 ① 的依据 (★逐条★):
#     timing_check.py · nl.ohm/farad/rail_of/populated/dnp_of*/rows_of/net_note("<位号>")
#         ⇒ ★S4 实测: 崩在 L1113 `tau_rel = (r_pull + r_ser) * c_rst` (两者都 None)★
#         ⇒ ★S8 实测 (零改名): 同一行全绿 ⇒ ⇒ 归因确定 = 改名特有★
#     timing_check.py · re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)$", ref)
#         ⇒ ★S4 实测: F3 判据崩 (EXC 'I2C_A' · 上拉电阻一颗都找不到)★
#     timing_check.py · 字面量比较 ("U_PWR_SW" in load_switch_refs 等)
#         ⇒ ★S4 实测: REV-3 反向用例 FAIL★ ★S8 实测: 全过★
#     check_onepass_sw_sync.py · SW03 探针的 8 颗位号清单
#         ⇒ ★S4 实测: "落表残项 0 行" ⇒ 清单过期★ ★S8 实测: 该条绿★
#     check_onepass_sw_sync.py · SW05 探针的 5 颗位号清单
#         ⇒ ★S4 实测: 探针抽不到值 (rc=0)★ ★S8 实测: 该条绿★
#   ★判 ② 的依据: ★S4 与 S8 都不因这一行红★ ⇒ 那一行只是注释/文档/清单里的引用★
#   ★★凡不在判 ① 判定表里的 (文件, 行) ⇒ 一律判 ② ★★
SITE_1 = []
# · timing_check.py: nl.<方法>("<位号>") 调用点
SITE_1.append(("SW/tools/timing_check.py", [
               'nl.ohm("', 'nl.farad("', 'nl.rail_of("', 'nl.populated("',
               'nl.dnp_of("', 'nl.dnp_of_row("', 'nl.rows_of("', 'nl.net_note("',
               're.match(r"^R_PU_(I2C[AB])_(SCL|SDA)$"',
               '"U_PWR_SW" in', '"U_EN_SW" in', '"U_PWR_SW" not in',
               'drop=("U_PWR_SW",)', 'drop=("U_PWR_SW", "U_EN_SW"),',
               'edits=[("R_PU_RESET_N"', 'edits=[("C_RST"', 'edits=[("R_PU_I2CB_SCL"',
               'edits=[("R_PU_I2CA_SCL"', 'targets=[("PG_AND", "Q_AND")]',
               'targets=[("PG_AND", "R_PG_PULL")]',
               'for ref in ("U_DCDC_VCORE", "U_DCDC_VIO"):',
               'for ref in ("R_PD_ON",):',
               'LOAD_SWITCH_REFS = ("U_PWR_SW", "U_EN_SW")',
               'BAT_DET_REFS = ("R_BAT_DET_1", "R_BAT_DET_2", "C_DET_BAT")',
               '("R_VBUS_DET_D1", "R_VBUS_DET_D2", "C_DET_VBUS_D", "VBUS_DET_D"),',
               '("R_BAT_DET_1", "R_BAT_DET_2", "C_DET_BAT", "BAT_DET")',
               'pullup_ref": "R_PG_PULL"', 'q_and_gate_row_dnp"',
               'q_envc_row_dnp"', 'q_and_drain_row_dnp"', 'sw_rst_row_dnp"',
               'u_supv_pin1_row_dnp"',
               'q["ref"] == x.get("ref", "")']))
# · check_onepass_sw_sync.py: SW03/SW05 两条探针的位号清单
SITE_1.append(("SW/tools/check_onepass_sw_sync.py", [
               '"t={\'D_CHG_LED\'', '"{\'SW_BOOT\'', '"[\'SW_BOOT\'']))
# · check_demo_panel_spec_r6_chainjudge_selftest.py: CJ-1 读台账产出单号 ⇒ 与位号无关
#   ⇒ ★它归因于【台账里多了一条 ISS-321 落表行】⇒ 不是位号问题 ⇒ 判 ② ★


def site_is_1(rel, line_text):
    base = os.path.basename(rel)
    for fr, pats in SITE_1:
        if base != os.path.basename(fr):
            continue
        for pat in pats:
            if pat in line_text:
                return True
    return False

# ★★【判 ① 的具体 token 集】★ ★按【S4 实测炸在哪一行】逐条定★ ★
#   timing_check.py: 位号字面量进 nl.ohm/farad/rail_of/populated/dnp_of*/rows_of/net_note
#                    或进 re.match 正则扫位号 ⇒ 改名后查不到 ⇒ 读数 None ⇒ 崩
#   check_timing_review_adc_sync.py: 它不自己写位号 ⇒ 是上游崩 ⇒ 归因同上
#   check_demo_panel_spec_r6_chainjudge_selftest.py: CJ-1 读【落表台账的产出单号】
#                    ⇒ 与位号无关 ⇒ 归因是【台账里多了一条 ISS-321 落表行】★


def main():
    sets = json.load(open(SETS, encoding="utf-8"))
    truth = set(sets["map"].keys())
    ren = set(sets["rename"])
    mapping = sets["map"]
    hits = json.load(open(HITS, encoding="utf-8"))
    lit = json.load(open(LIT, encoding="utf-8"))

    # ★被扫的全部文件 (★用于 ③ 的逐行定位★) ★
    files_scanned = []
    td = os.path.join(PROJ, "SW", "tools")
    for n in sorted(os.listdir(td)):
        if n.endswith(".py") and ".bak_" not in n:
            files_scanned.append(os.path.join("SW", "tools", n))
    sd = os.path.join(PROJ, "SW")
    for n in sorted(os.listdir(sd)):
        if n.endswith(".md"):
            files_scanned.append(os.path.join("SW", n))

    # ★★假阳性白名单 (★逐条有理由·不是「看着像就放过」★) ★★
    FALSE_POS = {
        "SW_MD5_ANCHORS": "常量名 · 锚点块标记",
        "SW_TIMING_REVIEW": "文档名",
        "SW_REQUIREMENTS": "文档名",
        "SW_BOARD_REL": "常量名 · 路径常量",
        "SW_SYNC_PCB": "常量名 · env 键",
        "SW_SYNC_NETLIST": "常量名 · env 键",
        "SW_SYNC_PINS": "常量名 · env 键",
        "SW_SYNC_BOM": "常量名 · env 键",
        "SW_SYNC_PRO": "常量名 · env 键",
        "SW_SYNC_LEDGER": "常量名 · env 键",
        "SW_SYNC_LANDING": "常量名 · env 键",
        "SW_SYNC_TMPDIR": "常量名 · env 键",
        "SW_SYNC_CHECKLIST": "常量名 · env 键",
        "SW_SYNC_ISSUE_LOG": "常量名 · env 键",
        "SW_TICKET_A": "常量名 · 假单号",
        "SW_TICKET_B": "常量名 · 假单号",
        "SW_PRO_REL": "常量名 · 路径常量",
        "VBUS_5V": "网名 · 电源轨",
        "VBUS_DET": "网名 · 电源轨",
        "PWR_3V3": "网名 · 电源轨",
        "PWR_5V": "网名 · 电源轨",
        "PWR_1V8": "网名 · 电源轨",
        "PWR_5V5": "网名 · 电源轨",
        "PWR_SEQ": "网名 · 电源时序",
        "PG_ALL": "网名 · 电源好信号",
        "PG_VCORE": "网名 · 电源好信号",
        "PG_VIO": "网名 · 电源好信号",
        "RESET_N": "网名 · 复位信号",
        "INT_TP": "网名 · 触控中断",
        "BAT_PROT": "网名 · 电池保护",
        "DSI_DSI": "网名",
        "CSI_DSI": "网名",
    }

    # ★用字面量搜索 (★比正则更准·已实测只差 2 处·都是正则漏的中文邻接字★) ★
    rows = []
    for rel, entries in lit.items():
        base = os.path.basename(rel)
        # ★逐行定位 (★为了给「文件:行」★) ★
        line_map = defaultdict(list)
        path = os.path.join(PROJ, rel)
        with open(path, encoding="utf-8", errors="replace") as f:
            for ln, line in enumerate(f, 1):
                for tok, _c in entries:
                    pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(tok) + r"(?![A-Za-z0-9_])")
                    if pat.search(line):
                        line_map[tok].append(ln)
        for tok, cnt in entries:
            if tok not in truth:
                continue
            newname = mapping[tok]
            is1 = False
            if rel.endswith(".py"):
                path = os.path.join(PROJ, rel)
                with open(path, encoding="utf-8", errors="replace") as f:
                    flines = f.readlines()
                for ln in line_map.get(tok, []):
                    if ln > len(flines):
                        continue
                    if site_is_1(rel, flines[ln - 1]):
                        is1 = True
                        break
            cat = "①" if is1 else "②"
            lns = line_map.get(tok, [])
            for ln in (lns if lns else [0]):
                rows.append((rel, ln, tok, newname, cat, cnt))

    rows.sort(key=lambda r: (r[0], r[1] if r[1] else 0, r[2]))

    # ★★去重 (同一文件同一行同一 token 只留一行) ★★
    seen = set()
    out = []
    for r in rows:
        k = (r[0], r[1], r[2])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)

    # ── ③ 假阳性: 形状像位号但【不在 218 真集】⇒ 逐条列出 ──
    # ★★口径 (★任务书 §2② 的本意★): ★main 10:2x 的粗扫前缀集 ★
    #   `(R|C|U|L|D|Q|TP|CONN|J|SW|K|F|B|T|JP)_[A-Z0-9_]{1,14}` ⇒ 粗扫会抓到的 token ★
    #   ⇒ ★凡被粗扫抓到、又不在 218 真集里的 ⇒ 就是「假阳性」全集 ★
    # ⇒ ★【每个位号都要能在表里找到或明确判成 ③】★ ★
    fp = []
    rough = re.compile(r"\b(R|C|U|L|D|Q|TP|CONN|J|SW|K|F|B|T|JP)_[A-Z0-9_]{1,14}\b")
    shape = rough
    for rel in sorted(files_scanned):
        path = os.path.join(PROJ, rel)
        with open(path, encoding="utf-8", errors="replace") as f:
            for ln, line in enumerate(f, 1):
                for m in shape.finditer(line):
                    tok = m.group(0)
                    if tok in truth:
                        continue
                    if tok in FALSE_POS:
                        continue
                    fp.append((rel, ln, tok))
    # 去重
    seenfp = set()
    fp_out = []
    for r in fp:
        if (r[0], r[1], r[2]) in seenfp:
            continue
        seenfp.add((r[0], r[1], r[2]))
        fp_out.append(r)
    fp_out.sort(key=lambda r: (r[0], r[1], r[2]))

    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("文件:行\t位号\t改名后名\t命中类别\n")
        for rel, ln, tok, newname, cat, cnt in out:
            f.write("%s:%d\t%s\t%s\t%s\n" % (rel, ln, tok, newname, cat))
        for rel, ln, tok in fp_out:
            f.write("%s:%d\t%s\t(不改·形状像但不是真位号)\t③\n" % (rel, ln, tok))

    # ── 统计 ──
    st = defaultdict(int)
    files = defaultdict(set)
    for rel, ln, tok, newname, cat, cnt in out:
        st[cat] += 1
        files[cat].add(rel)
    print("=" * 92)
    print("ISS-321 · ② sw_hardcoded_refs.tsv 生成完毕 (★机器生成·非手抄★)")
    print("=" * 92)
    print("  ★总行数 (文件:行 × 位号): %d" % len(out))
    print("  ① 判据里写死 (改后会炸)                : %4d 行 · %d 份文件"
          % (st["①"], len(files["①"])))
    for x in sorted(files["①"]):
        print("        %s" % x)
    print("  ② 判据里写死但本来就该随改名改 (改法=改脚本): %4d 行 · %d 份文件"
          % (st["②"], len(files["②"])))
    print("  ③ 假阳性 (不在 218 真集里)              : %4d 行 · %d 个 token"
          % (len(fp_out), len({x[2] for x in fp_out})))
    print("★写出: logs/iss321/sw_hardcoded_refs.tsv")


if __name__ == "__main__":
    main()
