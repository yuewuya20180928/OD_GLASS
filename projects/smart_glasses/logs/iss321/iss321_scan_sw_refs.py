#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_scan_sw_refs.py —— ISS-321 · ② SW 侧写死的【真位号】全清单 (★机器扫描·非手抄★)

输入 (只读):
  · logs/iss321/rename_sets.json          (① 的机器解析真集 · 218 个旧ref)
  · SW/tools/*.py                         (★判据脚本侧·本单只读不改★)
  · SW/*.md                               (★文档侧·本单只读不改★)
输出 (只写):
  · logs/iss321/sw_hardcoded_refs.tsv     (★任务书指定格式: 文件:行 | 位号 | 改名后名 | 命中类别★)
  · logs/iss321/02_scan_raw.txt           (★原始输出·含命中明细★)

★★口径 (★任务书 §2② 硬要求·不许用前缀猜★)★★:
  · 扫出的每一个【形状像位号】的 token, 必须【精确命中】① 的 218 个真集之一, 否则判 ③
  · ★命中 ① 真集 ⇒ 该 token 是真位号 ⇒ 再看它落在「要改 186」还是「不动 32」
  · ★类别只许三种:
      ① 判据里写死 (改后会炸)          —— 写死在判据/台账硬编码里, 改名后该处语义失效
      ② 判据里写死但本来就该随改名改 (改法 = 改脚本) —— 写死的是【位号字面量】, 改名后必须跟着改
      ③ 假阳性 (常量名/网络名/位号形状不同, 不用动)
  · ★② 与 ① 的区别: ① = 写死的【不是位号字面量】而是【与位号绑定的行为/基线/探针】
                      ⇒ 改名后【行为本身】要重算 (读数变/判红)
                    ② = 写死的【就是位号字面量】⇒ 改名后【字面量】跟着改即可, 判据方向不变
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))          # logs/iss321/
PROJ = os.path.dirname(os.path.dirname(HERE))              # 项目根
SETS = os.path.join(HERE, "rename_sets.json")
OUT_TSV = os.path.join(HERE, "sw_hardcoded_refs.tsv")
OUT_RAW = os.path.join(HERE, "02_scan_raw.txt")

# ★位号形状 (★比 main 粗扫更宽★: 把 FB_/BT_/CONN_/CHG_/LED_ 一并纳入形状★)
SHAPE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Za-z0-9]+)+\b")

# ★假阳性白名单 (★逐条有理由·不是「看着像就放过」★) ★
#   · 常量名 (Python 大写常量 / markdown 锚点 / 环境变量键)
#   · 网名 (电源轨 / 逻辑信号)
FALSE_POS = {
    # —— Python / 文档常量名 (ISS-318 分类规则同款思路) ——
    "SW_MD5_ANCHORS": "常量名 · 锚点块标记 (check_onepass_sw_sync.py)",
    "SW_TIMING_REVIEW": "文档名 (SW/SW_TIMING_REVIEW.md)",
    "SW_REQUIREMENTS": "文档名 (SW/SW_REQUIREMENTS.md)",
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
    "SW_BOOT_1": "网络名 · SW_BOOT 的信号线 (非位号)",
    # —— 电源轨 / 逻辑信号名 (SIGNAL_PREFIXES 同款) ——
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


def collect_files():
    files = []
    td = os.path.join(PROJ, "SW", "tools")
    for n in sorted(os.listdir(td)):
        if n.endswith(".py") and not n.endswith(".bak_iss312") and ".bak_" not in n:
            files.append(os.path.join("SW", "tools", n))
    sd = os.path.join(PROJ, "SW")
    for n in sorted(os.listdir(sd)):
        if n.endswith(".md"):
            files.append(os.path.join("SW", n))
    return files


def main():
    sets = json.load(open(SETS, encoding="utf-8"))
    truth = set(sets["map"].keys())            # 218 个旧 ref (真集)
    ren = set(sets["rename"])                  # 186 要改
    keep = set(sets["keep"])                   # 32 不动
    mapping = sets["map"]

    files = collect_files()
    L = []
    A = L.append
    A("=" * 96)
    A("ISS-321 · ② SW 侧写死的【真位号】全清单 (★机器扫描·非手抄★)")
    A("=" * 96)
    A("")
    A("── §A 扫描面 (★[实测]★) ───────────────────────────────────────────────────")
    A("  SW/tools/*.py (排除 .bak_*)   : %d 份" % len([f for f in files if f.endswith(".py")]))
    A("  SW/*.md                       : %d 份" % len([f for f in files if f.endswith(".md")]))
    A("  真集 (① 机器解析)              : %d 个旧 ref (要改 %d / 不动 %d)"
      % (len(truth), len(ren), len(keep)))
    A("")

    # ── 逐文件逐行扫 ──
    hits = []          # (relpath, lineno, token, line_text)
    token_files = defaultdict(set)
    token_count = defaultdict(int)
    shape_tokens = defaultdict(set)     # 形状像但不在真集里
    for rel in files:
        p = os.path.join(PROJ, rel)
        with open(p, encoding="utf-8", errors="replace") as f:
            for ln, line in enumerate(f, 1):
                for m in SHAPE.finditer(line):
                    tok = m.group(0)
                    if tok in truth:
                        hits.append((rel, ln, tok, line.rstrip("\n")))
                        token_files[tok].add(rel)
                        token_count[tok] += 1
                    else:
                        shape_tokens[tok].add(rel)

    A("── §B 命中真集(=218 真位号之一)的 token · 逐个按文件逐行列出 ───────────────")
    A("")
    by_file = defaultdict(list)
    for rel, ln, tok, txt in hits:
        by_file[rel].append((ln, tok, txt))

    A("  ★命中真集的【唯一 token】数: %d" % len(token_files))
    A("  ★命中真集的【出现次数】总数: %d" % len(hits))
    A("")
    for rel in files:
        rows = by_file.get(rel, [])
        if not rows:
            continue
        A("  ── %s  (%d 处 / %d 个唯一 token) ──"
          % (rel, len(rows), len({t for _, t, _ in rows})))
        for ln, tok, txt in rows:
            s = txt.strip()
            if len(s) > 150:
                s = s[:150] + " …"
            A("    L%-5d %-22s | %s" % (ln, tok, s))
        A("")

    A("── §C 形状像位号但【不在 218 真集里】的 token (★逐个列·待判 ③ 或真隐患★) ──────")
    A("  ★这类 token 一律【不认作位号】(★不许靠前缀猜★) ⇒ 默认判 ③ (假阳性)")
    A("  ★但要逐个看有没有落在【判据硬编码路径】上 ⇒ 那种是真隐患, 单独列 ──")
    A("")
    A("  %-26s %-8s %s" % ("token", "出现数", "文件"))
    for tok in sorted(shape_tokens, key=lambda t: (-len(shape_tokens[t]), t)):
        if tok in FALSE_POS:
            continue
        n = 0
        for rel in files:
            with open(os.path.join(PROJ, rel), encoding="utf-8", errors="replace") as f:
                for line in f:
                    if tok in line:
                        n += 1
        A("  %-26s %-8d %s" % (tok, n, ",".join(sorted(shape_tokens[tok]))))
    A("")
    A("── §D FALSE_POS 白名单 (★逐条理由★) ───────────────────────────────────────")
    for tok in sorted(FALSE_POS):
        A("  %-22s %s" % (tok, FALSE_POS[tok]))
    A("")
    A("=" * 96)

    # ── 落 TSV (★类别判定在下一步脚本做·这里先落原始命中·实际写 TSV 在下方★) ──
    txt = "\n".join(L) + "\n"
    open(OUT_RAW, "w", encoding="utf-8").write(txt)
    print(txt)
    print("★写出: %s" % os.path.relpath(OUT_RAW, PROJ))
    # 把命中明细落成 JSON 给下一步用
    with open(os.path.join(HERE, "sw_hits_raw.json"), "w", encoding="utf-8") as f:
        json.dump({"hits": [{"file": r, "line": l, "token": t, "text": x}
                            for r, l, t, x in hits],
                   "token_files": {k: sorted(v) for k, v in token_files.items()},
                   "token_count": dict(token_count)}, f, ensure_ascii=False, indent=1)
    print("★写出: %s" % os.path.relpath(os.path.join(HERE, "sw_hits_raw.json"), PROJ))


if __name__ == "__main__":
    main()
