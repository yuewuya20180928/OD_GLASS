#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
§7 (充电板连接清单) ↔ 网表 双向差集 一次性对拍脚本 (★ISS-230 · 2026-11-16 · hw-lead★)
================================================================================
★**为什么有这个脚本**:
  ① `HW/CHARGE_BOARD_SPEC.md` §7 的 CSV 块原先**本身不是合法 CSV** (★`U_CHG` 那行的 note
     里逗号没加引号 ⇒ 解析成 16 列 ⇒ board 列被读成 `" 0.8mm max height"`★) ⇒ §7.1 的
     计数对账表不能直接用 ⇒ **2026-11-16 已就地修好 (note 补引号) ⇒ 现在 81 行 × 13 列齐★**。
  ② §7 与网表是**两个版本** (★F-5 已订正: ★**对账的错在 §7**★ ⇒ 本脚本只做【清单化】,
     **不自动改网表** —— 改网表归【充电板整页】那一趟★)。

★**这个脚本干什么 (只读, 一律不改任何文件)**:
  ① 解析 §7 的 CSV 块 ⇒ 打印【合法性】体检 (行数 × 列数 × 列名);
  ② 把 §7 的唯一位号 与 网表 `board=CHG_BOARD` 的唯一位号 求双向差集 ⇒ 打成一张表;
  ③ 对交集里的 25 个位号做【逐行对拍】(页 / net / node1 / node2 / value / dnp / board);
  ④ 每条差集给出【处置建议】(★该 §7 补 / 该网表补 / 该改名 / 该归板 / 该留白★)。

★**边界 (★本脚本只读, 不写★)**:
  ★**不许改网表** (★真源 = `state/p10_rows.json`; ★F-5: 错在 §7 ⇒ 只修 §7 侧★) ★
  ★**不许改 §7** (★本单已在 §7 侧修过一处 CSV 合法性, 那处是【引号】不是【语义】★) ★

用法:
    python3 HW/check_chg_spec7_vs_netlist.py            # 打印全部 (rc=0)
    python3 HW/check_chg_spec7_vs_netlist.py --strict    # 差集非空 ⇒ rc=1 (★给将来接门禁用★)
    python3 HW/check_chg_spec7_vs_netlist.py --csv-only   # 只跑 §7 CSV 合法性体检
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SPEC_MD = os.path.join(PROJ, "HW", "CHARGE_BOARD_SPEC.md")
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")

EXPECT_COLS = ["page", "net", "node1", "node2", "ref", "value", "type", "dnp",
               "evidence", "tbd", "note", "conn_id", "board"]

# ═══════════════════════════════════════════════════════════════════════════════
# ★**处置建议表 (★唯一真源 = 本表★; ★每一条都写明【为什么】与【归谁】★) ★
# ═══════════════════════════════════════════════════════════════════════════════
# ★**处置档位只有 5 种** (★不许发明第 6 种★):
#   该 §7 补 = §7 漏了 ⇒ 该给 §7 加行
#   该网表补 = 网表漏了 ⇒ 该给网表加行 (★但本单不许动网表 ⇒ 归【充电板整页】那一趟★)
#   该改名   = 两边都有, 只是位号写法不同 ⇒ 该统一写法
#   该归板   = 两边都有, 但 board 列不同 ⇒ 该统一板别归属
#   该留白   = 差集是【比较口径】造成的假差 ⇒ 不动, 但要在 §7 写清为什么
DISPOSITION_S7_ONLY: dict[str, tuple[str, str]] = {
    # ref: (处置档位, 处置说明)
    "BAT_CHG": ("该改名",
                "★§7 用裸网名当 ref, 网表用 `NET_` 前缀 ⇒ §7 改成 `NET_BAT_PROT`; "
                "★且 §7 缺网表那一行 (U_CHG pin13+14 → RAIL_BAT_CHG, CHG_BOARD) ⇒ 该 §7 补"),
    "CHG_STAT": ("该改名",
                 "★§7 用裸网名当 ref, 网表用 `NET_` 前缀 ⇒ §7 改成 `NET_CHG_STAT`; "
                 "★且 §7 缺网表那一行 (U_CHG → R_PU_CHG_STAT, CHG_BOARD) ⇒ 该 §7 补"),
    "PWR_GOOD": ("该改名",
                 "★§7 用裸网名当 ref, 网表用 `NET_` 前缀 ⇒ §7 改成 `NET_PWR_GOOD`; "
                 "★网表的 CHG_BOARD 那一行是 (U_CHG → R_PU_PG) ⇒ §7 缺 ⇒ 该 §7 补"),
    "TS_BAT": ("该改名",
               "★§7 用裸网名当 ref, 网表用 `NET_` 网前缀 ⇒ §7 改成 `NET_TS_BAT`"),
    "USB_CC1": ("该改名", "★§7 用裸网名当 ref ⇒ 改成 `NET_USB_CC1` (网表 P6)"),
    "USB_CC2": ("该改名", "★§7 用裸网名当 ref ⇒ 改成 `NET_USB_CC2` (网表 P6)"),
    "USB_D_P_CHG": ("该留白",
                   "★**两件事, 不是同一件**: §7 是【充电板侧 USB D+】(CONN_USB pin1 → J_TYPE_C A6+B6), "
                   "网表里没有这个网 ⇒ 网表的 USB D+ 是【demo 板载 Type-C 的 D+】"
                   "(`NET_USB_D_P_TYPEC`, MAIN_PCB) ⇒ ★**§7 这两行描述的是【充电板整机阶段】的链, "
                   "现行网表还没有充电板⇒ 归 V-7 充电板整机阶段单, 本单【留白】不删也不改★"),
    "USB_D_N_CHG": ("该留白", "★同上 (D− 侧), 归 V-7 充电板整机阶段单"),
    "NC": ("该改名",
           "★§7 把 `NC` 当【ref】用, 网表里 `NC` 是【node2】(NC_UCHG / HINGE_RSV 的对端) "
           "⇒ §7 的 ref 该写 `NC_UCHG` (pin24) / 其它网对应的 NC 网名"),
    "J_CHG": ("该留白",
              "★**假差 (口径造成)**: §7 的 J_CHG 行 board=HINGE, 网表的 J_CHG 11 行 board 也全是 HINGE "
              "⇒ ★**两侧完全一致** ⇒ 差出来只因为本脚本比的是【网表 board=CHG_BOARD 的子集】"),
    "R_NTC_BAT": ("该留白",
                  "★**假差 (口径造成)**: §7 的 R_NTC_BAT 2 行 board=MAIN_PCB, 网表也是 MAIN_PCB ⇒ 一致"),
    "R_TS1": ("该改名",
              "★§7 的 `R_TS1` (5.24k ±1%, 必装) ↔ 网表的 `R_TS_TOP` (5.24k ±1%, **DNP**) "
              "⇒ 该改名 + ★**必装/DNP 落表差异** (★归【充电板整页】那一趟★)"),
    "R_TS2": ("该改名",
              "★§7 的 `R_TS2` (30.31k ±1%, 必装, MAIN_PCB) ↔ 网表的 `R_TS_PULL` "
              "(30.31k ±1%, **DNP**, MAIN_PCB) ⇒ 该改名 + 必装/DNP 落表差异"),
    "R_VDET_TOP": ("该归板",
                   "★**§7 是旧口径 (2026-11-04 之前)**: §7 把 VBUS 分压放在【充电板侧】"
                   "(R_VDET_TOP/R_VDET_BOT, CHG_BOARD) ⇒ 网表已是【主板本地分压】"
                   "(`R_VBUS_DET_D1`/`R_VBUS_DET_D2`/`C_DET_VBUS_D`, MAIN_PCB) "
                   "⇒ 该改名 + 该归板 (CHG_BOARD → MAIN_PCB) ★**§7 的 note 里那句『已按网表真源订正』"
                   "只改了文字, 没改 board 列 ⇒ 这就是 F-5 说的『错在 §7』★"),
    "R_VDET_BOT": ("该归板", "★同上 (下臂)"),
    "C_VBUS_BULK": ("该改名",
                    "★§7 用【一颗】100µF `C_VBUS_BULK`, 网表拆成【两颗】且【都 DNP】: "
                    "`C_VBUS_OUT` (VBUS_5V_F1 → VBUS_5V_CHG) + `C_VBUS_GND` (VBUS_5V_CHG → GND) "
                    "⇒ 该改名 + ★**落表差异 (必装 vs DNP) 归【充电板整页】那一趟★"),
}

DISPOSITION_NET_ONLY: dict[str, tuple[str, str]] = {
    "C_VBUS_GND": ("该改名", "★§7 的 `C_VBUS_BULK` 的地端 ⇒ §7 拆成 `C_VBUS_OUT` + `C_VBUS_GND`"),
    "C_VBUS_OUT": ("该改名", "★同上 ⇒ §7 拆成 `C_VBUS_OUT` + `C_VBUS_GND`"),
    "D_CHG_LED": ("该 §7 补",
                  "★网表 P10 有【充电 LED 整条链】(D_CHG_LED + Q_CHG_LED + R_CHG_LED), "
                  "§7 **一行都没有** ⇒ §7 漏了 ⇒ 该 §7 补 (★亮什么色 / 谁驱动 = V-7 充电板整机阶段单★)"),
    "D_TVS_VBUS": ("该 §7 补",
                   "★网表 P10 有 VBUS 的【TVS 过压钳位】, §7 只有 `D_ESD_TC` (ESD) "
                   "⇒ ★**ESD ≠ TVS** (ESD 管静电脉冲, TVS 管电源过压) ⇒ §7 漏了 ⇒ 该 §7 补"),
    "NET_BAT_PROT": ("该改名", "★↔ §7 的 `BAT_CHG` ⇒ 见 §7 侧那一行"),
    "NET_CHG_STAT": ("该改名", "★↔ §7 的 `CHG_STAT`"),
    "NET_PWR_GOOD": ("该改名", "★↔ §7 的 `PWR_GOOD`"),
    "NET_TS_BAT": ("该改名", "★↔ §7 的 `TS_BAT`"),
    "NET_USB_CC1": ("该改名", "★↔ §7 的 `USB_CC1`"),
    "NET_USB_CC2": ("该改名", "★↔ §7 的 `USB_CC2`"),
    "Q_CHG_LED": ("该 §7 补", "★同 `D_CHG_LED` ⇒ §7 漏了整条充电 LED 链"),
    "R_CHG_LED": ("该 §7 补", "★同 `D_CHG_LED` ⇒ §7 漏了整条充电 LED 链"),
    "R_PU_CHG_STAT": ("该 §7 补",
                      "★网表 P2 有 `R_PU_CHG_STAT` (10k 上拉到 3.3V, CHG_BOARD); "
                      "§7 只在 note 里写了『主板侧 10k 上拉 3.3V』却**没有这一行** ⇒ 该 §7 补"),
    "R_TS_TOP": ("该改名",
                 "★↔ §7 的 `R_TS1` (5.24k) ⇒ 该改名 + ★**必装/DNP 落表差异** "
                 "(网表 3 行全是 DNP) 归【充电板整页】那一趟★"),
    "TP_CHG_STAT": ("该 §7 补",
                    "★网表 P7 有 `TP_CHG_STAT` (CHG_STAT 测点), §7 只列了 `TP_VBUS` / `TP_TS` "
                    "⇒ §7 漏了这个测点 ⇒ 该 §7 补"),
}


def read_spec7_block() -> tuple[list[str], int]:
    """取 §7 的 ```csv``` 块 ⇒ (块文本, 起始物理行号)。"""
    with open(SPEC_MD, encoding="utf-8") as fh:
        text = fh.read()
    i = text.index("## 7.")
    m = re.search(r"```csv\n(.*?)\n```", text[i:], re.S)
    if not m:
        raise SystemExit("★在 §7 里找不到 ```csv``` 块")
    start_line = text[:i + m.start()].count("\n") + 1
    # 块首行 (```csv) 的物理行号
    block_start = text[:i + m.start()].count("\n") + 2
    return m.group(1), block_start


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="差集非空 ⇒ rc=1")
    ap.add_argument("--csv-only", action="store_true", help="只跑 §7 CSV 合法性体检")
    args = ap.parse_args()

    block, block_start = read_spec7_block()
    rows = list(csv.reader(io.StringIO(block)))
    header = rows[0]
    data = rows[1:]

    print("═══ ① §7 CSV 块 合法性体检 (★来源 = HW/CHARGE_BOARD_SPEC.md §7★) ═══")
    print(f"   块起始物理行: L{block_start}   块行数: {len(rows)} (表头 1 + 数据 {len(data)})")
    bad = [(block_start + n, len(r)) for n, r in enumerate(rows) if len(r) != len(EXPECT_COLS)]
    print(f"   表头列名: {','.join(header)}")
    print(f"   期望列数: {len(EXPECT_COLS)}   实测: 每行 {'齐' if not bad else '不齐'}")
    if bad:
        for ln, n in bad:
            print(f"   ★★行 L{ln}: 解析成 {n} 列 (应为 {len(EXPECT_COLS)}) ⇒ 这块【不是合法 CSV】★★")
        return 1
    print("   ✅ 判定: ★**合法 CSV**★ (81 行 × 13 列齐) ⇒ §7.1 的计数对账表现在可以直接用")
    if args.csv_only:
        return 0

    # ---- §7 的位号宇宙 ----
    i_ref = header.index("ref")
    i_board = header.index("board")
    i_page = header.index("page")
    s7_refs = {r[i_ref] for r in data}
    s7_board_cnt: dict[str, int] = {}
    for r in data:
        s7_board_cnt[r[i_board]] = s7_board_cnt.get(r[i_board], 0) + 1

    with open(NETLIST, encoding="utf-8", newline="") as fh:
        nl = list(csv.DictReader(fh))
    for _n, _r in enumerate(nl, start=2):      # 表头 = 第 1 行
        _r["_line"] = _n
    chg = [r for r in nl if (r.get("board") or "") == "CHG_BOARD"]
    nl_refs = {r["ref"] for r in chg}

    inter = sorted(s7_refs & nl_refs)
    only_s7 = sorted(s7_refs - nl_refs)
    only_nl = sorted(nl_refs - s7_refs)

    print()
    print("═══ ② §7 ↔ 网表 双向差集 (★口径 = 网表 board=CHG_BOARD 子集★) ═══")
    print(f"   §7 唯一位号: {len(s7_refs)}   (§7 行数 {len(data)}; 板别分布 {s7_board_cnt})")
    print(f"   网表 board=CHG_BOARD 唯一位号: {len(nl_refs)}   (网表 CHG_BOARD 行数 {len(chg)})")
    print(f"   交集: {len(inter)}")
    print(f"   ★**§7 有而网表没有: {len(only_s7)}**★")
    print(f"   ★**网表有而 §7 没有: {len(only_nl)}**★")

    def side_rows(ref: str, board_filter: str | None = None) -> list[dict]:
        out = []
        for n, r in enumerate(data, start=block_start + 1):
            if r[i_ref] == ref and (board_filter is None or r[i_board] == board_filter):
                out.append({"page": r[i_page], "net": r[header.index("net")],
                            "node1": r[header.index("node1")], "node2": r[header.index("node2")],
                            "value": r[header.index("value")], "dnp": r[header.index("dnp")],
                            "board": r[i_board], "_line": n})
        return out

    print()
    print(f"─── ②a §7 有而网表没有 ({len(only_s7)} 个) ───")
    print(f"{'ref':<18}{'处置':<10}{'§7 行':<8}{'§7 board':<11}{'说明'}")
    for ref in only_s7:
        d, why = DISPOSITION_S7_ONLY.get(ref, ("该留白", "★未分类 ⇒ 人工看★"))
        rs = side_rows(ref)
        lines = ",".join(str(x["_line"]) for x in rs)
        boards = "/".join(sorted({x["board"] for x in rs}))
        print(f"{ref:<18}{d:<10}{lines:<8}{boards:<11}{why}")

    print()
    print(f"─── ②b 网表有而 §7 没有 ({len(only_nl)} 个) ───")
    print(f"{'ref':<18}{'处置':<10}{'网表行数':<10}{'网表 board':<11}{'说明'}")
    for ref in only_nl:
        d, why = DISPOSITION_NET_ONLY.get(ref, ("该留白", "★未分类 ⇒ 人工看★"))
        rs = [r for r in chg if r["ref"] == ref]
        boards = "/".join(sorted({r["board"] for r in rs}))
        print(f"{ref:<18}{d:<10}{len(rs):<10}{boards:<11}{why}")

    # ---- ③ 交集逐行对拍 ----
    print()
    print(f"─── ③ 交集 {len(inter)} 个位号 逐行对拍 (★只看页 / net / node1 / node2 / value / dnp / board★) ───")
    mismatch = 0
    for ref in inter:
        s7 = side_rows(ref)
        nn = [r for r in chg if r["ref"] == ref]
        s7_sig = sorted((x["net"], x["node1"], x["node2"], x["dnp"], x["board"]) for x in s7)
        nn_sig = sorted((r["net"], r["node1"], r["node2"], r["dnp"], r["board"]) for r in nn)
        same = s7_sig == nn_sig
        if not same:
            mismatch += 1
        print(f"  {ref:<18} §7 {len(s7)} 行 / 网表 {len(nn)} 行  "
              f"{'✅ 结构一致' if same else '★ 结构有差 (见下)'}")
        if not same:
            for x in s7:
                print(f"      §7  L{x['_line']}  net={x['net']:<14} {x['node1']} → {x['node2']:<24} "
                      f"dnp={x['dnp']:<5} board={x['board']}")
            for r in nn:
                print(f"      网表 L{r['_line']}  net={r['net']:<14} {r['node1']} → {r['node2']:<24} "
                      f"dnp={r['dnp']:<5} board={r['board']}")
    print(f"   ⇒ 结构不一致的交集位号: {mismatch} / {len(inter)}")

    # ---- ④ 为什么本单【没有】做双向对账 ----
    print()
    print("═══ ③ 本单【没有】做双向对账 (★原因, 不是遗漏★) ═══")
    print("   ★**§7 与网表是两个版本, 对账的起点不成立★**:")
    print("     · §7 = 【充电板整机阶段的镜像清单】(80 行, 目标是把充电板整页落进网表);")
    print("     · 网表 = 【现行 demo 主 PCB 网表】(513 行, 充电链只落了 94 行 CHG_BOARD);")
    print("     · ⇒ 两边的【行数 / 页结构 / 位号命名约定】本来就不同 (例: §7 用裸网名当 ref,")
    print("       网表用 `NET_` 前缀; §7 有 `USB_D_P_CHG` 这条【充电板侧】链, 网表还没有充电板);")
    print("     · ⇒ ★**强行对账 = 拿两个不同版本的表互相判错** ⇒ 本单只做【清单化】(把差集摊开 +")
    print("       给处置建议), 【不改网表】 (★真源 = `state/p10_rows.json`; ★F-5 已订正: ★错在 §7★)")
    print("       ⇒ 真正的双向对账 + 改网表, 归【充电板整页】那一趟★ ★")
    print("     · ⇒ ★**本单对 §7 只改了 1 处**: CSV 合法性 (note 补引号) —— ★**那处是【格式】, 不是【语义】★**")

    if args.strict and (only_s7 or only_nl):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
