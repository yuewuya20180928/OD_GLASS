#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-393 · mech-lead · 「通用 KiCad 库件 vs Samtec 厂件」对照物差集与判决链重算 · 机器闸

★**本闸只【登记差集与重算清单】, 不代落**★ —— 既有闸 (`MECH/check_debug_seat_3d_fit.py` /
`MECH/check_fts_seat_body_geometry.py`) 与既有页正文一个字节都不许本闸改动。
★**零挂链**: `grep -c check_fts_vs_generic_courtyard_delta state/gate_check.py` ⇒ 0 (挂链是 main 的地界)。

判据:
  G1 机器块每个几何量必须带 source ∈ {generic_library, factory, derived, missing} 且带 class ∈ {A,B,C}
  G2 凡标 generic_library 的数, 页面正文不许用「官方/厂件/原厂」定性 (除非同句有中性词) ⇒ 红并点名行号+数值
  G3 两本对照账必须覆盖判决链实际消费的每一个量 (闸自己实读 MECH/check_debug_seat_3d_fit.py
     与 MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md 抽出被消费的数, 逐个给行号)
  G4 A/B/C 三类必须每个量都有; A 类必须给不变的理由; B 类必须给新旧与差; C 类必须给问题与裁决方
  G5 Y 向缺口必须可复算 (闸自己按机器块的座体深 Y + 判据余量重算) ⇒ 与页面写的不一致 ⇒ 红;
     且「零余量 (缺口 0.0000)」这个结论必须被点名 (因为座体口径下它不成立)
  G6 扩散面扫描: 闸自己实跑全仓 grep, 凡「通用库件数 + 官方定性」组合出现在已签收闸源码/已签收页正文 ⇒
     必须已被登记 (文件+行号+建议新措辞), 且登记项不得陈旧
  G7 零扰动 (板三指纹 + 三表 md5) + 零落表 + 零挂链 + 零挂起措辞 + 证据分级五级白名单 + 判据/事实分开

用法:
  python3 MECH/check_fts_vs_generic_courtyard_delta.py              # 裸跑, rc=0 = 全绿
  python3 MECH/check_fts_vs_generic_courtyard_delta.py --emit       # 打印真相页机器块 (JSON)
  python3 MECH/check_fts_vs_generic_courtyard_delta.py --selftest    # 反向用例, 末行 ALL TESTS PASS
"""
from __future__ import annotations
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE_REL = "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md"
PAGE = os.path.join(ROOT, PAGE_REL)
CONSUMED = ("MECH/check_debug_seat_3d_fit.py", "MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md")
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
TABLES = {"HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
          "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
          "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8"}
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = "4940213"
SOURCES = ("generic_library", "factory", "derived", "missing")
CLASSES = ("A", "B", "C")
EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
QUALIFIER = ("官方", "厂件", "原厂")
NEUTRAL = ("通用", "库件", "KiCad", "误认", "错认", "订正", "作废", "禁止", "不许", "≠")
PENDING = ("等原厂回信", "待原厂回信", "待外部确认", "等待原厂", "等放行", "待确认")
KW = ['铜箔 X','铜箔包络','铜箔宽','清空区 X','清空区 Y','罩开口','开口 Y','F.CrtYd','F.Fab',
      'courtyard','钻孔','焊盘','绝缘体','柱高','座体本体','真 land','判据要求']
MARK = ("官方 land courtyard","官方 land 的 F.Fab","官方 land 的 `F.Fab`","官方 land 的 `F.CrtYd`",
        "官方 land 自己的","官方 1x4 THT 的 F.CrtYd","官方 1x2 THT 的 F.CrtYd",
        "官方 1x4 THT 座体本体","官方 1x2 THT 座体本体","官方 1×4 THT 座体本体","官方 1×2 THT 座体本体",
        "IPC 的 courtyard","比 courtyard `6.0900` 还小")
SCAN_SKIP = ('MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md','MECH/check_fts_seat_body_geometry.py',
             PAGE_REL, 'MECH/check_fts_vs_generic_courtyard_delta.py')

def rd(p):
    with open(os.path.join(ROOT, p), encoding='utf-8', errors='replace') as f:
        return f.read()

def page_text():
    with open(PAGE, encoding='utf-8', errors='replace') as f:
        return f.read()

def block_of(text):
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None

def consumed(root=ROOT):
    out = {}
    for rel in CONSUMED:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            continue
        with open(p, encoding='utf-8', errors='replace') as f:
            for i, l in enumerate(f, 1):
                if any(k in l for k in KW):
                    for n in re.findall(r'(?<![\d.])\d+\.\d{4}(?![\d])', l):
                        out.setdefault(n, []).append('%s:%d' % (os.path.basename(rel), i))
    return out

def scan(root=ROOT):
    hits = []
    for base in ('MECH','HW'):
        for dp, dn, fn in os.walk(os.path.join(root, base)):
            dn[:] = [d for d in dn if d not in ('__pycache__','.git')]
            for f in sorted(fn):
                if not f.endswith(('.md','.py')):
                    continue
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, root)
                if rel in SCAN_SKIP:
                    continue
                with open(p, encoding='utf-8', errors='replace') as fh:
                    for i, l in enumerate(fh, 1):
                        for m in MARK:
                            if m in l:
                                hits.append((rel, i, m))
    return hits

def md5_of(p):
    return subprocess.run(['md5sum', p], cwd=ROOT, capture_output=True, text=True).stdout.split()[0]

def stat_of(p):
    out = subprocess.run(['stat','-c','%y %s', p], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out

def f4(x):
    return "%.4f" % float(x)

def check(text, root=ROOT, over=None):
    """★核心判定★ · over = {'board_md5':..,'board_stat':..,'hook_count':..} (只给自测用)"""
    over = over or {}
    fails = []
    def bad(cid, msg):
        fails.append((cid, msg))
    blk = block_of(text)
    if blk is None:
        bad("G0", "真相页机器块 (```json```) 解析失败或缺失")
        return fails, 0
    dims = blk.get("dimensions") or {}
    # ---------------- G1 source/class ----------------
    for k, v in dims.items():
        if v.get("source") not in SOURCES:
            bad("G1", "机器块 %s 的 source 非法 (现=%r, 须 %s)" % (k, v.get("source"), "|".join(SOURCES)))
        if v.get("class") not in CLASSES:
            bad("G1", "机器块 %s 的 class 非法 (现=%r, 须 A|B|C)" % (k, v.get("class")))
        if not str(v.get("note", "")).strip():
            bad("G1", "机器块 %s 缺 note (每个量都要说清它是什么)" % k)
    # ---------------- G2 官方定性 ----------------
    lines = text.split("\n")
    for k, v in dims.items():
        if v.get("source") != "generic_library":
            continue
        val = str(v.get("value", ""))
        if not val:
            continue
        for i, l in enumerate(lines, 1):
            if val in l and any(q in l for q in QUALIFIER) and not any(n in l for n in NEUTRAL):
                bad("G2", "标 generic_library 的数 %s 在第 %d 行被用『%s』定性 (须写通用 KiCad 库件): %s"
                    % (val, i, "/".join(q for q in QUALIFIER if q in l), l.strip()[:110]))
                break
    # ---------------- G3 覆盖率 ----------------
    cons = consumed(root)
    covered = set()
    for v in dims.values():
        covered.add(str(v.get("value", "")))
        covered.add(str(v.get("old_value", "")))
    excl = blk.get("excluded_quantities") or {}
    for n, where in sorted(cons.items()):
        if n not in covered and n not in excl:
            bad("G3", "判决链实际消费的量 %s 未入两本对照账 (出处 %s)" % (n, ",".join(where[:3])))
    for n, r in sorted(excl.items()):
        if n not in cons:
            bad("G3", "excluded_quantities 里的 %s 不是判决链实际消费的量 (陈旧登记)" % n)
        if not str(r).strip():
            bad("G3", "excluded_quantities 里的 %s 缺排除理由" % n)
    reg_cons = blk.get("consumed_quantities") or {}
    for n in cons:
        if n not in reg_cons:
            bad("G3", "机器块 consumed_quantities 缺 %s (登记与实读不一致)" % n)
    for n in reg_cons:
        if n not in cons:
            bad("G3", "机器块 consumed_quantities 里的 %s 实读不到 (陈旧)" % n)
    # ---------------- G4 A/B/C 分类 ----------------
    dbc = blk.get("delta_by_class") or {}
    A = dbc.get("A_unchanged") or []
    B = dbc.get("B_changed") or []
    C = dbc.get("C_pending_main") or []
    seen = {}
    for e in A:
        k = e.get("key")
        seen[k] = seen.get(k, 0) + 1
        if not str(e.get("why_unchanged", "")).strip():
            bad("G4", "A 类 %s 缺 why_unchanged (不许空着)" % k)
    for e in B:
        k = e.get("key")
        seen[k] = seen.get(k, 0) + 1
        if e.get("old_value") is None or e.get("new_value") is None:
            bad("G4", "B 类 %s 缺 old_value/new_value" % k)
        if "delta" not in e:
            bad("G4", "B 类 %s 缺 delta" % k)
    for e in C:
        k = e.get("key")
        seen[k] = seen.get(k, 0) + 1
        if not str(e.get("question", "")).strip():
            bad("G4", "C 类 %s 缺 question (要 main 回答什么)" % k)
        if not str(e.get("decision_owner", "")).strip():
            bad("G4", "C 类 %s 缺 decision_owner" % k)
    for k in dims:
        if k not in seen:
            bad("G4", "量 %s 没有 A/B/C 分类" % k)
    for k, c in seen.items():
        if c > 1:
            bad("G4", "量 %s 被分类了 %d 次 (一个量只能归一类)" % (k, c))
    # ---------------- G5 Y 向缺口可复算 ----------------
    y = blk.get("y_direction_gap") or {}
    try:
        crit = float(dims["crit"]["value"]); tol = float(dims["tol_fdm_part"]["value"])
        m = crit + tol
        body = float(dims["seat_body_y"]["value"])
        opening = float(dims["cover_opening_y"]["value"])
        cupy = float(dims["copper_env_y"]["value"])
        req_body = body + 2 * m
        max_fit = opening - 2 * m
        gap_body = req_body - max_fit
        gap_cup = (cupy + 2 * m) - max_fit
        cb = (y.get("caliber_seat_body") or {}); cc = (y.get("caliber_copper") or {})
        if f4(gap_body) != str(cb.get("gap")):
            bad("G5", "Y 缺口复算不符: 闸算 %s (座体深 %s + 2x%s - (%s - 2x%s)) ≠ 页面写的 %s"
                % (f4(gap_body), f4(body), f4(m), f4(opening), f4(m), cb.get("gap")))
        if f4(gap_cup) != str(cc.get("gap")):
            bad("G5", "罩铜箔口径 Y 缺口复算不符: 闸算 %s ≠ 页面写的 %s" % (f4(gap_cup), cc.get("gap")))
        if f4(gap_cup) != "0.0000":
            bad("G5", "零余量结论必须被点名: 罩铜箔口径下 Y 缺口应是 0.0000, 现为 %s" % f4(gap_cup))
        if f4(gap_body) == "0.0000":
            bad("G5", "座体口径下 Y 缺口不得为 0.0000 (装不下才是真值)")
        if "零余量" not in text:
            bad("G5", "页面未点名『零余量』这个结论 (零余量在新口径下不成立, 必须被点名)")
    except Exception as e:
        bad("G5", "Y 向缺口复算失败: %r" % (e,))
    # ---------------- G6 扩散面登记完整性 ----------------
    hits = scan(root)
    reg = blk.get("spread_sites") or []
    hset = set(hits); rset = set((r.get("file"), r.get("line"), r.get("marker")) for r in reg)
    for h in hits:
        if h not in rset:
            bad("G6", "扩散面未登记: %s:%d (措辞 %r)" % (h[0], h[1], h[2]))
    for r in reg:
        key = (r.get("file"), r.get("line"), r.get("marker"))
        if r.get("status") == "resolved":
            if key in hset:
                bad("G6", "登记项已标 resolved 但现场仍在: %s:%d" % (r.get("file"), r.get("line")))
        elif key not in hset:
            bad("G6", "登记项已陈旧 (现场已无此处): %s:%d" % (r.get("file"), r.get("line")))
        if not str(r.get("new_text", "")).strip():
            bad("G6", "登记项 %s:%d 缺建议新措辞 (只登记不给改法不算数)" % (r.get("file"), r.get("line")))
    # ---------------- G7 零扰动 / 零挂起 / 证据分级 / 判据事实分开 ----------------
    bmd5 = over.get("board_md5") or md5_of(os.path.join(root, BOARD))
    if bmd5 != BOARD_MD5:
        bad("G7", "板 md5 被动了: %s ≠ %s (零写板)" % (bmd5, BOARD_MD5))
    bstat = over.get("board_stat") or stat_of(os.path.join(root, BOARD))
    if BOARD_MTIME not in bstat or BOARD_SIZE not in bstat:
        bad("G7", "板 mtime/size 被动了: %r ≠ %s / %s" % (bstat, BOARD_MTIME, BOARD_SIZE))
    for t, m in TABLES.items():
        got = md5_of(os.path.join(root, t))
        if got != m:
            bad("G7", "真源表 %s 被动了: %s ≠ %s (零落表)" % (t, got, m))
    hook = over.get("hook_count")
    if hook is None:
        gc = os.path.join(root, "state/gate_check.py")
        hook = 0
        if os.path.exists(gc):
            with open(gc, encoding='utf-8', errors='replace') as f:
                hook = sum(1 for l in f if "check_fts_vs_generic_courtyard_delta" in l)
    if int(hook) != 0:
        bad("G7", "本闸被挂进 state/gate_check.py (%s 处) ⇒ 挂链是 main 的地界" % hook)
    for p in PENDING:
        if p in text:
            bad("G7", "页面含零挂起禁语 %r (缺口一律自己算 + 写降级方案)" % p)
    for k, v in dims.items():
        for ev in str(v.get("evidence", "")).split("+"):
            if ev.strip() and ev.strip() not in EVIDENCE_WHITELIST:
                bad("G7", "量 %s 的证据等级 %r 不在五级白名单里" % (k, ev.strip()))
    for lst in (A, B, C):
        for e in lst:
            for ev in str(e.get("evidence", "")).split("+"):
                if ev.strip() and ev.strip() not in EVIDENCE_WHITELIST:
                    bad("G7", "分类项 %s 的证据等级 %r 不在五级白名单里" % (e.get("key"), ev.strip()))
    if "判据侧" not in text or "事实侧" not in text:
        bad("G7", "页面未把【判据侧】与【事实侧】分开标注")
    return fails, len(dims)

def mut(text, fn):
    """只给自测用: 改机器块里的 JSON, 再写回页面文本"""
    blk = block_of(text)
    fn(blk)
    new = json.dumps(blk, ensure_ascii=False, indent=2)
    return re.sub(r"```json\s*\{.*?\}\s*```", "```json\n" + new + "\n```", text, flags=re.S)

def selftest():
    base = page_text()
    cases = []
    def add(name, cid, fn, over=None):
        cases.append((name, cid, fn, over))
    def del_source(b):
        del b["dimensions"]["copper_env_x_4pos"]["source"]
    def bad_source(b):
        b["dimensions"]["copper_env_x_4pos"]["source"] = "library"
    def del_class(b):
        del b["dimensions"]["copper_env_x_4pos"]["class"]
    def g2_note(b):
        b["dimensions"]["lib_courtyard_x_4pos"]["note"] = "官方 6.0900 courtyard"
    def g2_note2(b):
        b["dimensions"]["lib_drill"]["note"] = "官方 0.6500 钻孔 (当厂件规格用)"
    def g2_body(t):
        return t.replace("| 座体本体上限 (J_DEBUG) | `5.0800 × 2.1000` |",
                         "| 座体本体上限 (J_DEBUG) | 官方 `5.0800 × 2.1000` |")
    def g5_gap(b):
        b["y_direction_gap"]["caliber_seat_body"]["gap"] = "1.1500"
    def g5_body(b):
        b["dimensions"]["seat_body_y"]["value"] = "2.1500"
    def g3_del(b):
        del b["dimensions"]["copper_env_x_2pos"]
    def g4_del(b):
        b["delta_by_class"]["A_unchanged"] = [e for e in b["delta_by_class"]["A_unchanged"]
                                              if e.get("key") != "cover_opening_y"]
    def g6_del(b):
        b["spread_sites"] = b["spread_sites"][1:]
    def g7_pending(t):
        return t.replace("## §5 降级方案", "## §5 降级方案\n\n等原厂回信")
    def g7_ev(b):
        b["dimensions"]["cover_opening_y"]["evidence"] = "[传闻]"
    add("c01 G1 删掉 source 字段", "G1", lambda t: mut(t, del_source))
    add("c02 G1 source 取非法值", "G1", lambda t: mut(t, bad_source))
    add("c03 G1 删掉 class 字段", "G1", lambda t: mut(t, del_class))
    add("c04 G2 把库件数写成官方 (note)", "G2", lambda t: mut(t, g2_note))
    add("c05 G2 把钻孔写成官方 (note)", "G2", lambda t: mut(t, g2_note2))
    add("c06 G2 正文把库件数写成官方", "G2", g2_body)
    add("c07 G5 改 Y 缺口那个数", "G5", lambda t: mut(t, g5_gap))
    add("c08 G5 改座体深 Y 让复算对不上", "G5", lambda t: mut(t, g5_body))
    add("c09 G3 删掉一个被消费的量", "G3", lambda t: mut(t, g3_del))
    add("c10 G4 删掉一个 A 类归类", "G4", lambda t: mut(t, g4_del))
    add("c11 G6 少登记一处扩散面", "G6", lambda t: mut(t, g6_del))
    add("c12 G7 板 md5 被动", "G7", lambda t: t, {"board_md5": "deadbeef" * 4})
    add("c13 G7 页面出现零挂起禁语", "G7", g7_pending)
    add("c14 G7 证据等级不在白名单", "G7", lambda t: mut(t, g7_ev))
    ok = True
    fails, n = check(base)
    if fails:
        ok = False
        print("[SELFTEST] 基准页必须全绿, 但有 %d 条失败:" % len(fails))
        for cid, m in fails:
            print("   [%s] %s" % (cid, m))
    else:
        print("[SELFTEST] 基准页全绿 ✔ (机器块量数 %d)" % n)
    for name, cid, fn, over in cases:
        txt = fn(base)
        f2, _ = check(txt, over=over)
        hit = [x for x in f2 if x[0] == cid]
        if hit:
            print("[SELFTEST] %-40s ⇒ 红 ✔  (%s: %s)" % (name, cid, hit[0][1][:96]))
        else:
            ok = False
            print("[SELFTEST] %-40s ⇒ ★★没变红★★ (应为 %s 红)" % (name, cid))
    print("[SELFTEST] 正向 1 + 反向 %d" % len(cases))
    if ok:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1

def main():
    if "--selftest" in sys.argv:
        return selftest()
    if "--emit" in sys.argv:
        blk = block_of(page_text())
        if blk is None:
            print("机器块解析失败")
            return 1
        print(json.dumps(blk, ensure_ascii=False, indent=2))
        return 0
    fails, n = check(page_text())
    if fails:
        print("── ISS-393 FTS vs 通用库件 对照物闸 ⇒ 红 (%d 条失败)" % len(fails))
        for cid, m in fails:
            print("  [%s] %s" % (cid, m))
        return 1
    print("── ISS-393 FTS vs 通用库件 对照物闸 ⇒ 全绿")
    print("   真相页: %s" % PAGE_REL)
    print("   机器块量数: %d · G1~G7 全部通过 · 零写板 · 零落表 · 零挂链" % n)
    return 0

if __name__ == "__main__":
    sys.exit(main())
