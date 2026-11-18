#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-15 21:4x · 修尺子自测 + 把位号口径改成【单一真源】(main 改)
=====================================================================
★★**发现 (★main 2026-11-15 21:3x daily_check 抓到, 不是推测★)** ★★
`daily_check` 报 ★**`check_sch_pinfull --self-test` 没过 (rc=1, 输出 3 行): SELFTEST FAILED**★
⇒ ★**这不是本轮造成的** (★脚本 mtime 2026-11-12 03:43 · 原理图 mtime 2026-11-12 03:36 · 本轮只改了 issue_log + pm.yaml★)
⇒ ★**⇒ 它从落库那天起就一直是红的, 三天没人管** ★★

★★**根因 (★main 独立读代码 + 真板实测, 不是推测★)** ★★
★**① 自测样例本身写错了 (★主因★)**: 自测 ④ 拿表侧 ref = `{U1, C1, R1}` ⇒ ★**这 3 个末字符本来就是数字**
  ⇒ 按生成器规则 `kicad_ref()` 【根本不会给它们加 "_1"】 ⇒ ★**"U1_1 → U1" 这个期望本身就是错的** ★
  ⇒ ★**⇒ 自测红, 而生产路径是对的 (★真板实测: 表侧 218 个 ref 里 32 个末字符是数字 (不加后缀) · 186 个加 "_1"
  ⇒ 映射条数 186 ⇒ 图上 187 个带 "_1" (186 映射 + 1 个 `R_BAT_DET_1` 天然以 _1 结尾) ⇒ 零碰撞 218→218★)** ★

★★**② 还有一个更隐蔽的洞 (★必须一起补★)**: 闸里的 `kicad_ref()` 是 ★**生成器同名函数的复制粘贴副本**★
  ⇒ ★**两边之间没有任何断言** ⇒ ★**生成器一改后缀规则, 闸就静默按旧规则跑 ⇒ 假绿** ★
  ⇒ ★**这正是本项目反复踩的坑 ("绿得莫名其妙")** ★

★★**本脚本做 3 件事 (★全是【修尺子】, 不改判据阈值, 不改真源文件★)** ★★
  ① 闸的 `kicad_ref()` 改为 ★**委托给生成器的 `kicad_ref()` (单一真源)**, import 失败 ⇒ **响亮失败, 不静默降级**
     ⇒ ★**闸自己的严格策略 (`k not in tbl` ⇒ 宁可点名也不乱映射) 保留** ★
  ② 自测 ④ 样例改成与生成器规则一致 (末字符非数字) + 新增 ④b (末字符是数字 ⇒ 不许还原)
  ③ 新增自测 ⑤ (★**真板端到端**★): ★**按本项目铁律「自测要端到端跑真板, 不能只测纯函数」★**
     ⇒ ★**闸 vs 生成器口径逐个 ref 零差异 + 真表映射零碰撞 + 真图 218 个 Reference 集合 == 规则推出的图上位号集合** ★
     ⇒ ★**这条断言直接守住「图 = 表」这个主线结论** ★
"""
import io
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "check_sch_pinfull.py")

# ── 补丁 1: 单一真源 ────────────────────────────────────────────────────────
OLD1 = '''def kicad_ref(ref: str) -> str:
    """★图上位号 = 表侧 ref (+ "_1" 后缀, ★末字符不是数字时才加★)
    ★★**与 `state/gen_kicad_sch.py` 的 `kicad_ref()` 同口径 (★两边必须一致, 否则本闸会误报★)** ★★"""
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"
'''

NEW1 = '''def kicad_ref(ref: str) -> str:
    """★图上位号 = 表侧 ref (+ "_1" 后缀, ★末字符不是数字时才加★)

    ★★**2026-11-15 21:4x main 改: 【复制粘贴副本】→ 【单一真源委托】★★
    ★**原实现是把 `state/gen_kicad_sch.py` 的同名函数抄了一份** ⇒ ★**两边之间没有任何断言** ★
    ⇒ ★**生成器一改后缀规则, 本闸就静默按旧规则跑 ⇒ 假绿** ★ (★本项目反复踩的坑★)
    ⇒ ⇒ ★**现在直接委托生成器的那一个** ⇒ ★**口径不可能再漂** ★
    ⇒ ★**闸自己那条更严的策略 (`k not in tbl` ⇒ 宁可点名也不乱映射) 保留在 `normalize_sch_refs` 里** ★
    ⇒ ★**import 失败 ⇒ 响亮失败, 不静默降级 (★防口径漂移★)** ★
    """
    return _gen_kicad_ref(ref)
'''

# ── 补丁 2: import 生成器 ───────────────────────────────────────────────────
OLD2 = '''HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
SCH = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_sch")
KICAD_SH = os.path.join(HERE, "kicad.sh")
TABLE = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
'''

NEW2 = '''HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
SCH = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_sch")
KICAD_SH = os.path.join(HERE, "kicad.sh")
TABLE = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")

# ★★**位号口径的【单一真源】 = 生成器的 kicad_ref()** ★★
# ★★2026-11-15 21:4x main 改 (★原实现是复制粘贴副本 ⇒ 口径会漂 ⇒ 假绿★) ★★
# ★**import 失败 ⇒ 响亮失败 (★照 advance.py 里的 decision_truth 守卫那套风格★)** ★★
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    import gen_kicad_sch as _gen
except Exception as _e:  # noqa: BLE001
    sys.exit("★生成器导入失败 ⇒ 拒绝跑 (★防位号口径漂移 ⇒ 宁可直接挂★): %s" % _e)
_gen_kicad_ref = _gen.kicad_ref
'''

# ── 补丁 3: 自测 ④ 改样例 + 加 ④b ─────────────────────────────────────────
OLD3 = '''    # ④ 位号口径还原 (★ISS-205★): 还原必须【精确】⇒ 表里没有的位号还原不了 ⇒ 照样被点名 (★尺子没放松★)
    norm_counts, norm_map, n_mapped = normalize_sch_refs(
        {"U1_1": 2, "C1_1": 1, "R1_1": 1, "GHOST_1": 3}, {"U1", "C1", "R1", "J_GHOST"})
    if (norm_counts.get("U1") != 2 or norm_counts.get("C1") != 1 or norm_counts.get("R1") != 1):
        fails.append("④ 口径还原失败: 加了后缀的位号没还原 (U1=%s C1=%s R1=%s)"
                     % (norm_counts.get("U1"), norm_counts.get("C1"), norm_counts.get("R1")))
    if "GHOST_1" not in norm_counts:
        fails.append("④ 表里没有的位号被凭空还原了 (GHOST_1) ⇒ 尺子被放松")
    nrc, _, nmm, _ = evaluate(norm_counts, {"U1": 2, "C1": 1, "R1": 1, "J_GHOST": 2})
    if nrc != 1 or not any(m["ref"] == "GHOST_1" for m in nmm):
        fails.append("④ 还原不了的多余位号没被点名 (GHOST_1) ⇒ 尺子被放松")
'''

NEW3 = '''    # ④ 位号口径还原 (★ISS-205★): 还原必须【精确】⇒ 表里没有的位号还原不了 ⇒ 照样被点名 (★尺子没放松★)
    # ★★2026-11-15 21:4x main 改 (★原自测样例写错了, ⇒ 从落库那天起就一直红★)**:
    # ★**原样本拿表侧 ref = {U1, C1, R1} ⇒ 这 3 个末字符本来就是数字 ⇒ 按生成器规则【根本不会加 "_1"】**
    # ⇒ ★**"U1_1 → U1" 这个期望本身就是错的 ⇒ 生产路径对、自测错** ★
    # ⇒ ★**真板实测 (★main 21:3x 独立跑★): 表侧 218 个 ref 里 32 个末字符是数字 (不加后缀) · 186 个加 "_1"
    #   ⇒ 图上 187 个带 "_1" (186 映射 + 1 个 R_BAT_DET_1 天然以 _1 结尾) ⇒ 映射零碰撞 218→218** ★
    # ⇒ ★**新样本: 表侧 ref 末字符一律【非数字】(与生成器规则一致)** ★
    norm_counts, norm_map, n_mapped = normalize_sch_refs(
        {"UA_1": 2, "CA_1": 1, "RA_1": 1, "GHOST_1": 3}, {"UA", "CA", "RA", "J_GHOST"})
    if (norm_counts.get("UA") != 2 or norm_counts.get("CA") != 1 or norm_counts.get("RA") != 1):
        fails.append("④ 口径还原失败: 加了后缀的位号没还原 (UA=%s CA=%s RA=%s)"
                     % (norm_counts.get("UA"), norm_counts.get("CA"), norm_counts.get("RA")))
    if "GHOST_1" not in norm_counts:
        fails.append("④ 表里没有的位号被凭空还原了 (GHOST_1) ⇒ 尺子被放松")
    nrc, _, nmm, _ = evaluate(norm_counts, {"UA": 2, "CA": 1, "RA": 1, "J_GHOST": 2})
    if nrc != 1 or not any(m["ref"] == "GHOST_1" for m in nmm):
        fails.append("④ 还原不了的多余位号没被点名 (GHOST_1) ⇒ 尺子被放松")
    # ④b 【末字符是数字 ⇒ 生成器不加后缀 ⇒ 尺子不许把 "X_1" 还原成 "X"】
    # ★★这是本项目最容易被"还原"这一步悄悄放松的一条 (★反着用就会把两个器件并成一个★) ★★
    d_counts, d_map, _ = normalize_sch_refs({"U1": 2, "U1_1": 1}, {"U1"})
    if d_counts.get("U1") != 2 or d_counts.get("U1_1") != 1:
        fails.append("④b 末字符是数字的位号被错误还原 (U1=%s U1_1=%s)"
                     % (d_counts.get("U1"), d_counts.get("U1_1")))

    # ⑤ ★★【真板端到端】★★ (★本项目铁律: 自测要端到端跑真板, 不能只测纯函数★)
    # ★★2026-11-15 21:4x main 加 (★纯函数自测全绿, 但真板那一层没人验★)★★
    if not os.path.exists(TABLE):
        fails.append("⑤ 真表不在: %s" % TABLE)
    else:
        with open(TABLE, encoding="utf-8") as f:
            trows = list(csv.DictReader(f))
        trefs = []
        tseen = set()
        for row in trows:
            rf = (row.get("ref") or "").strip()
            if rf and rf not in tseen:
                tseen.add(rf)
                trefs.append(rf)
        # ⑤a 闸的口径 vs 生成器的口径 ⇒ 逐个 ref 零差异 (★单一真源没接上就会红★)
        diff = [r for r in trefs if kicad_ref(r) != _gen.kicad_ref(r)]
        if diff:
            fails.append("⑤a 闸的位号口径与生成器不一致 (前 5 个: %s)" % diff[:5])
        # ⑤b 映射零碰撞 (★两个表侧 ref 映射到同一个图上位号 ⇒ 图上会撞名★)
        seen_k = {}
        for r in trefs:
            k = _gen.kicad_ref(r)
            if k in seen_k:
                fails.append("⑤b 位号映射碰撞: %s 与 %s 都映射成 %s" % (seen_k[k], r, k))
                break
            seen_k[k] = r
        # ⑤c ★★真图上的 Reference 集合 == 按规则推出的图上位号集合★★ (★守住「图 = 表」★)
        import glob
        import re as _re
        sch_refs = set()
        for path in sorted(glob.glob(os.path.join(PROJ, "HW", "PCB", "demo_mainboard*.kicad_sch"))):
            with open(path, encoding="utf-8") as f:
                sch_refs |= set(_re.findall(r'\\(property "Reference" "([^"]+)"', f.read()))
        expect = set(_gen.kicad_ref(r) for r in trefs)
        only_sch = sorted(sch_refs - expect)
        only_tbl = sorted(expect - sch_refs)
        if only_sch or only_tbl:
            fails.append("⑤c 图/表位号集合不等 (图多 %d 个: %s · 表多 %d 个: %s)"
                         % (len(only_sch), only_sch[:5], len(only_tbl), only_tbl[:5]))
'''

PATCHES = [(OLD1, NEW1), (OLD2, NEW2), (OLD3, NEW3)]


def main():
    with open(TARGET, encoding="utf-8") as f:
        src = f.read()
    for i, (old, new) in enumerate(PATCHES, 1):
        n = src.count(old)
        assert n == 1, "补丁 %d 命中 %d 次 (期望 1)" % (i, n)
        src = src.replace(old, new)
    shutil.copy2(TARGET, TARGET + ".bak_20261115_2145")
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(src)
    print("补丁 3 处已落: %s" % TARGET)


if __name__ == "__main__":
    main()
