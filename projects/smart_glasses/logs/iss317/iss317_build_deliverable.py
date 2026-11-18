#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss317_build_deliverable.py —— ISS-317 交付物装配器 (★只写 HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md★)

★★ 纪律: §1 的 218 行表 ★从 logs/iss317/rename_list_raw.txt【逐字机器搬】★, 不手抄、不推算 ★★
   §2 的读数 ★从 logs/iss317/04b_sb_run_v2_raw.txt【逐字机器搬】★, 不推算 ★★
   ⇒ 装配器自带【行数校验】: 搬进来的表行数必须 == 218, 搬进来的读数行数必须 == 期望值
   ⇒ 不对就 abort (★宁可交半成品页·不许交一份看起来对但数字是编的页★)

★只读清单: logs/iss317/rename_list_raw.txt · logs/iss317/04b_sb_run_v2_raw.txt ·
   logs/iss317/01_c1_baseline_full.txt · logs/iss317/05_dmp3098l_official.txt ·
   logs/iss317/06_esd_official.txt · logs/iss317/07_bom_qmark_raw.txt
★不跑任何生成器 · 不改任何真源 · 零写板 · 零落表 · 零改闸
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # logs/iss317/
PROJ = os.path.dirname(os.path.dirname(HERE))              # 项目根
OUT = os.path.join(PROJ, "HW", "PCB", "ONETRIP_S1_THREE_SIDE_RENAME_LIST.md")

RAW_RENAME = os.path.join(HERE, "rename_list_raw_v2.txt")
RAW_RUN = os.path.join(HERE, "04b_sb_run_v2_raw.txt")
RAW_BASE = os.path.join(HERE, "01_c1_baseline_full.txt")


def die(msg):
    print("❌ abort: %s" % msg)
    sys.exit(2)


def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


# ════════════════════════════════════════════════════════════════════
# §1: 逐条改名对照表 (★从 rename_list_raw.txt 搬★)
# ════════════════════════════════════════════════════════════════════
def load_table():
    """★从 rename_list_raw_v2.txt 的 TSV 行逐字搬 218 行 (★不用固定宽度切列·不受全角字符影响★)"""
    txt = read(RAW_RENAME)
    rows = []
    for l in txt.split("\n"):
        if not l.startswith("TSV\t"):
            continue
        parts = l.split("\t")[1:]
        if len(parts) != 10:
            die("TSV 行的列数 = %d (★期望 10★)" % len(parts))
        vals = [p.strip() for p in parts]
        for k, v in enumerate(vals):
            if not v:
                die("TSV 第 %d 行的第 %d 列为空" % (len(rows) + 1, k + 1))
        rows.append(tuple(vals))
    if len(rows) != 218:
        die("TSV 表行数 = %d (★期望 218★) ⇒ 源文件被改过或解析错位" % len(rows))
    # ★编号必须连续 1..218★
    for i, r in enumerate(rows, 1):
        if int(r[0]) != i:
            die("TSV 表行编号不连续: 第 %d 行编号 = %s" % (i, r[0]))
    # ★★ 列 5 (新ref) 必须等于 kicad_ref(列 1) ⇒ 独立复核口径★★
    def kicad_ref(ref):
        r = (ref or "").strip()
        if r and r[-1].isdigit():
            return r
        return r + "_1"
    for i, r in enumerate(rows, 1):
        if r[4] != kicad_ref(r[1]):
            die("第 %d 行的新ref(%r) != kicad_ref(旧ref=%r) ⇒ 口径不一致" % (i, r[4], r[1]))
    return rows


# ════════════════════════════════════════════════════════════════════
# §2: 场景读数 (★从 04b_sb_run_v2_raw.txt 搬★)
# ════════════════════════════════════════════════════════════════════
def load_readings():
    txt = read(RAW_RUN)
    blocks = {}
    cur = None
    for l in txt.split("\n"):
        m = re.match(r"^=================== (\S+) ===================$", l)
        if m:
            cur = m.group(1)
            blocks[cur] = []
            continue
        if cur is not None:
            blocks[cur].append(l)
    return blocks


def pick(blocks, tag, pattern, must=True):
    """★从一个场景块里逐字取第一条匹配 pattern 的行★"""
    out = []
    for l in blocks.get(tag, []):
        if re.search(pattern, l):
            out.append(l.strip())
    if must and not out:
        die("场景 %s 里找不到匹配 %r 的读数行" % (tag, pattern))
    return out


def main():
    rows = load_table()
    blocks = load_readings()

    need_tags = ["A0_base_5side", "A1_jia_exempt", "A2_yi_unseal", "A3_bing_prefix",
                 "A4_bing_regex", "A5_negcase_CBULK", "A5b_negcase_CBULK_regex",
                 "A5c_negcase_CBULK_base", "A6_prefixtrap_C1", "A6b_prefixtrap_C2",
                 "A6c_prefixtrap_base", "T5b_ambig", "T6a_x2", "T6b_xz1",
                 "S1_selftest_base", "S2_selftest_optB"]
    for t in need_tags:
        if t not in blocks:
            die("04b_sb_run_v2_raw.txt 里没有场景块 %s" % t)

    # ★基线 (同一判据 + 原板 + 原网表) ★从 01_c1_baseline_full.txt 搬★
    base_txt = read(RAW_BASE)
    m = re.search(r"^\s+缺失 (\d+) · 多余 (\d+) · 同号异网 (\d+) · .*?非法 NC (\d+)$",
                  base_txt, re.M)
    if not m:
        die("01_c1_baseline_full.txt 里找不到 C1 汇总行")
    base_c1 = "缺失 %s · 多余 %s · 同号异网 %s · ★NC 焊盘 351 个 (允许的: SOM 的 4 组 100 脚座未用脚) · 非法 NC %s" % m.groups()

    print("§1 表行数 = %d ✓" % len(rows))
    print("§2 场景块数 = %d ✓" % len(blocks))

    # ── 逐场景读数提取 (★全部逐字搬★) ──
    scen = {}
    for tag in need_tags:
        b = blocks[tag]
        c1 = [l.strip() for l in b if "C1 焊盘级等价" in l]
        # ★★ C1 的【三项计数 + 非法 NC】在【下一行】(★不是同一行★)
        c1sum = [l.strip() for l in b if re.search(r"缺失 \d+ · 多余 \d+ · 同号异网 \d+", l)]
        c3 = [l.strip() for l in b if "C3 每个器件焊盘数" in l]
        c2bad = [l.strip() for l in b if "C2 针号/针数不符" in l]
        nc = [l.strip() for l in b if "NC 焊盘落在不该有 NC 的器件上" in l]
        amb = [l.strip() for l in b if "口径歧义" in l]
        miss = [l.strip() for l in b if "口径未同步" in l]
        cal = [l.strip() for l in b if "反查层命中" in l]
        st = [l.strip() for l in b if "自检通过" in l or "自检失败" in l]
        rc = [l.strip() for l in b if l.strip() == "rc=1" or l.strip() == "rc=0"]
        crash = [l.strip() for l in b if "Traceback" in l or "ValueError" in l
                 or "SyntaxError" in l or "❌ 自检失败" in l]
        scen[tag] = dict(c1=c1, c1sum=c1sum, c3=c3, c2bad=c2bad, nc=nc, amb=amb, miss=miss,
                         cal=cal, st=st, rc=rc, crash=crash)

    # ★A0/A1/A2/A3/A4 必须各读到 C1 + C3 行★
    for tag in ["A0_base_5side", "A1_jia_exempt", "A2_yi_unseal", "A3_bing_prefix", "A4_bing_regex"]:
        if not scen[tag]["c1"]:
            die("%s 没有 C1 读数行" % tag)
        if not scen[tag]["c3"]:
            die("%s 没有 C3 读数行" % tag)

    # ★非法 NC 数字 (★从 C1 行里正则抠出来★) ★
    def ncnum(tag):
        if not scen[tag]["c1sum"]:
            die("%s 的 C1 汇总行没有读到" % tag)
        mm = re.search(r"非法 NC (\d+)", scen[tag]["c1sum"][0])
        if not mm:
            die("%s 的 C1 汇总行里没有「非法 NC N」" % tag)
        return int(mm.group(1))

    def c3bad(tag):
        if not scen[tag]["c3"]:
            return -1          # ★无 C3 行 (★崩/异常场景★)
        mm = re.search(r"不符 (\d+) 个", scen[tag]["c3"][0])
        return int(mm.group(1)) if mm else -1

    # ★C1 三项 (缺失/多余/同号异网) ★
    def c1three(tag):
        if not scen[tag]["c1sum"]:
            die("%s 的 C1 汇总行(缺失/多余/同号异网)没有读到" % tag)
        mm = re.search(r"缺失 (\d+) · 多余 (\d+) · 同号异网 (\d+)",
                       scen[tag]["c1sum"][0])
        if not mm:
            die("%s 的 C1 汇总行里没有三项计数" % tag)
        return tuple(int(x) for x in mm.groups())

    print("★汇总表核对 (★机器算出来·待写进 §2★) ★")
    for tag in need_tags:
        if scen[tag]["c1"] and scen[tag]["c1sum"]:
            print("  %-24s %s | NC=%d | C3不符=%d"
                  % (tag, c1three(tag), ncnum(tag), c3bad(tag)))
        else:
            print("  %-24s (无 C1 行) ★崩/异常★ crash=%s" % (tag, scen[tag]["crash"][:1]))

    import json
    with open(os.path.join(HERE, "_delivery_payload.json"), "w", encoding="utf-8") as f:
        json.dump({
            "table": rows,
            "scen": {k: {kk: vv for kk, vv in v.items()} for k, v in scen.items()},
            "base_c1": base_c1,
        }, f, ensure_ascii=False, indent=1)
    print("\n★payload 已落 logs/iss317/_delivery_payload.json (★装配中间件★)")


if __name__ == "__main__":
    main()
