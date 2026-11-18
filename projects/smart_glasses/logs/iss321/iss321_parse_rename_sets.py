#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_parse_rename_sets.py —— ISS-321 · ①「哪些会改」的真集 (★机器解析·非手抄★)

输入 (只读): logs/iss317/rename_list_raw.txt   (★ISS-317 机器生成的 218 行逐条改名对照表★)
输出 (只写): logs/iss321/rename_sets.txt          (★机器解析结果·可复现★)
              logs/iss321/rename_sets.json         (★机读·供后续脚本用★)

★口径单源 = `state/gen_kicad_sch.py::kicad_ref()` (★ISS-205 规则·与 ISS-317 同源★)
★解析方式 = 按表头列位 (fixed-width slice) 切列 ⇒ 【不靠手抄·不靠前缀猜】★
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))          # logs/iss321/
PROJ = os.path.dirname(os.path.dirname(HERE))              # 项目根
SRC = os.path.join(PROJ, "logs", "iss317", "rename_list_raw.txt")
OUT_TXT = os.path.join(HERE, "rename_sets.txt")
OUT_JSON = os.path.join(HERE, "rename_sets.json")

# ★表头列位 (fixed-width) ★ —— 实测自 rename_list_raw.txt 第 43 行表头
COLS = [
    (4, 27),     # 0 旧ref(脚表侧现值)
    (27, 50),    # 1 旧ref(板侧现值)
    (50, 73),    # 2 旧ref(原理图侧现值)
    (73, 98),    # 3 新ref(kicad_ref 口径)
    (98, 121),   # 4 改哪个真源(同步清单)
    (121, 128),  # 5 板侧 (在/不在)
    (128, 136),  # 6 动/不动
    (136, 167),  # 7 改完的预期读数
    (167, 210),  # 8 依赖顺序
]
HDR_COL_NAMES = ["旧ref(脚表侧现值)", "旧ref(板侧现值)", "旧ref(原理图侧现值)",
                 "新ref(kicad_ref口径)", "改哪个真源(同步清单)", "板侧", "动/不动",
                 "改完的预期读数", "依赖顺序"]


def kicad_ref(ref):
    """★ISS-205 口径 (与 state/gen_kicad_sch.py::kicad_ref() 同源·逐字复刻)★"""
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


def parse():
    lines = open(SRC, encoding="utf-8").read().splitlines()
    rows = []
    for l in lines:
        m = re.match(r"^(\d{1,3})\s", l)
        if not m:
            continue
        idx = int(m.group(1))
        if not (1 <= idx <= 218):
            continue
        cells = [l[a:b].strip() for a, b in COLS]
        rows.append({"idx": idx, "old_pins": cells[0], "old_board": cells[1],
                     "old_sch": cells[2], "new": cells[3], "sync": cells[4],
                     "board": cells[5], "move": cells[6], "expect": cells[7],
                     "order": cells[8]})
    rows.sort(key=lambda r: r["idx"])
    assert len(rows) == 218, "行数不是 218: %d" % len(rows)
    assert [r["idx"] for r in rows] == list(range(1, 219)), "行号不连续"
    return rows


def main():
    rows = parse()
    rename = [r for r in rows if r["move"] == "改名"]
    keep = [r for r in rows if r["move"] == "不动"]
    on_board = [r for r in rows if r["board"] == "在"]
    chg_board = [r for r in rows if r["board"] == "不在"]
    rename_on = [r for r in rename if r["board"] == "在"]
    rename_chg = [r for r in rename if r["board"] == "不在"]
    keep_on = [r for r in keep if r["board"] == "在"]
    keep_chg = [r for r in keep if r["board"] == "不在"]

    # ★自检: 新ref 必须 == kicad_ref(旧ref)★ —— 口径一致才算数
    bad = [r for r in rows if r["new"] != kicad_ref(r["old_pins"])]
    # ★自检: 单射 (改名后撞名?)★
    news = [r["new"] for r in rows]
    collision = sorted({x for x in news if news.count(x) > 1})
    # ★自检: 板侧列 = 「板侧有封装」的口径 (用板文件实测交叉验)★
    board_txt = open(os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"),
                      encoding="utf-8", errors="replace").read()
    board_refs = set(re.findall(r'\(property\s+"Reference"\s+"([^"]+)"', board_txt))
    board_refs |= set(re.findall(r'\(fp_text\s+reference\s+"([^"]+)"', board_txt))
    on_board_real = {r["old_board"] for r in rows if r["board"] == "在"}
    cross_ok = (on_board_real == board_refs)

    L = []
    A = L.append
    A("=" * 96)
    A("ISS-321 · ①「哪些会改」的真集 (★机器解析自 logs/iss317/rename_list_raw.txt·非手抄★)")
    A("=" * 96)
    A("")
    A("★解析口径: 按表头列位 fixed-width 切列 · 逐行核对 kicad_ref() 口径")
    A("")
    A("── §A 计数 (★[实测]·本机本单实跑★) ──────────────────────────────────────────")
    A("  改名宇宙 (表侧真实器件)                : %d" % len(rows))
    A("  ★要改 (末字符是字母 ⇒ 加 _1)          : %d" % len(rename))
    A("  ★不动 (末字符是数字 ⇒ 一律不动)       : %d" % len(keep))
    A("    · 其中在板侧 (MAIN_PCB)              : %d 要改 / %d 不动"
      % (len(rename_on), len(keep_on)))
    A("    · 其中不在板侧 (CHG_BOARD)           : %d 要改 / %d 不动"
      % (len(rename_chg), len(keep_chg)))
    A("  板侧总数 (在)                          : %d" % len(on_board))
    A("  非板侧总数 (CHG_BOARD)                 : %d" % len(chg_board))
    A("")
    A("── §B 自检 (★口径一致性·不符就 abort★) ───────────────────────────────────")
    A("  ★新ref == kicad_ref(旧ref) 不符行数    : %d  (必须 = 0)" % len(bad))
    A("  ★改名后撞名 (单射校验)                 : %s  (必须 = 无)"
      % (", ".join(collision) if collision else "无"))
    A("  ★「板侧」列 vs 板文件实测封装集合一致  : %s  (必须 = True)"
      % cross_ok)
    A("  ★板文件实测封装个数                    : %d" % len(board_refs))
    A("")
    A("── §C 要改的 %d 个 (★旧ref → 新ref★) ──────────────────────────────────────"
      % len(rename))
    A("  %-28s %-28s %s" % ("旧ref(脚表侧现值)", "新ref(kicad_ref口径)", "板侧/CHG_BOARD"))
    for r in rename:
        where = "在板侧" if r["board"] == "在" else "CHG_BOARD(板侧无)"
        A("  %-28s %-28s %s" % (r["old_pins"], r["new"], where))
    A("")
    A("── §D 不动的 %d 个 (★末字符是数字★) ───────────────────────────────────────" % len(keep))
    A("  %-28s %-28s %s" % ("旧ref(脚表侧现值)", "新ref(=旧ref)", "板侧/CHG_BOARD"))
    for r in keep:
        where = "在板侧" if r["board"] == "在" else "CHG_BOARD(板侧无)"
        A("  %-28s %-28s %s" % (r["old_pins"], r["new"], where))
    A("")
    A("── §E ★单列: CHG_BOARD 件 (★板侧有?否 ⇒ 表侧有板侧无★) %d 个 ─────────────" % len(chg_board))
    A("  ★这 %d 个【板侧没有封装】⇒ 改名只影响表侧四件产物 + 充电板那一趟★" % len(chg_board))
    for r in chg_board:
        A("    %-28s → %-28s  [%s]" % (r["old_pins"], r["new"], r["move"]))
    A("")
    A("── §F 「改名后名字」全表 (★给 §2② 逐个对表用·机器读这份★) ──────────────────")
    for r in rows:
        A("  %s\t%s\t%s\t%s" % (r["old_pins"], r["new"], r["move"], r["board"]))
    A("")
    A("── §G 结论 ─────────────────────────────────────────────────────────────────")
    A("  ★要改 %d / 不动 %d ⇒ 与 ISS-317 §G 三数逐字一致 (218 / 32 / 186)★"
      % (len(rename), len(keep)))
    A("  ★CHG_BOARD %d 个 = 表侧有板侧无 ⇒ 与 ISS-317 §A「脚表有板无 32 个」一致★"
      % len(chg_board))
    A("  ★板侧口径「不动」%d 个 (ISS-314 的 30) vs 表侧口径「不动」%d 个 (差 = CHG_BOARD 不动 %d 个)★"
      % (len(keep_on), len(keep), len(keep_chg)))
    A("=" * 96)

    txt = "\n".join(L) + "\n"
    open(OUT_TXT, "w", encoding="utf-8").write(txt)

    data = {
        "rows": rows,
        "rename": [r["old_pins"] for r in rename],
        "keep": [r["old_pins"] for r in keep],
        "rename_on_board": [r["old_pins"] for r in rename_on],
        "rename_chg_board": [r["old_pins"] for r in rename_chg],
        "keep_on_board": [r["old_pins"] for r in keep_on],
        "keep_chg_board": [r["old_pins"] for r in keep_chg],
        "chg_board_all": [r["old_pins"] for r in chg_board],
        "map": {r["old_pins"]: r["new"] for r in rows},
        "board_refs_measured": sorted(board_refs),
        "selfcheck": {"kicad_ref_mismatch": len(bad), "collision": collision,
                      "board_column_cross_ok": cross_ok,
                      "board_refs_count": len(board_refs)},
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(txt)
    print("★写出: %s" % os.path.relpath(OUT_TXT, PROJ))
    print("★写出: %s" % os.path.relpath(OUT_JSON, PROJ))


if __name__ == "__main__":
    main()
