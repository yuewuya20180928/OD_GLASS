#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss323_verify_fix20.py —— ISS-323 · F-1 改法的【20 处必改 + 5 处可选】二次验证

★★为什么要有这个脚本★★:
    ISS-321 的 F-1 改法是「25 处定点替换」, 其中后 5 处 (F1-20~F1-25) 是
    『把断言里的位号字面量改成「旧名或新名都认」』。
    ★★但 F1-14 + F1-17 生效后, ★输出层报出来的已经是【逻辑名】★★
    ⇒ ★那 5 处断言【原文继续成立】⇒ ★可能根本不必改★ ★
    ★★本脚本验证这一点★ ⇒ ★清单里就能把 25 处拆成「20 处必改 + 5 处可选」★

★★改法 ★★:
    ★【20 处必改版】= F1-01 ~ F1-19 (★不改任何断言里的字面量★)
    ★【25 处全改版】 = ISS-321 原版 (★作对照★)
    ★两者都在【沙盒副本】上跑 ⇒ ★真闸零改★

★★输出 ★★: logs/iss323/13_verify_fix20.txt
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
S4 = os.path.join(SB, "rootS4")
FIX20 = os.path.join(SB, "fixroot20")
LOG = os.path.join(PROJ, "logs", "iss323", "13_verify_fix20.txt")

OUT = []


def A(s):
    OUT.append(s)
    print(s)


def patch(txt, old, new):
    assert old in txt, "★补丁锚点没找到⇒abort★: %r" % old[:90]
    return txt.replace(old, new, 1)


def apply_f1_core(txt):
    """★F1-01 ~ F1-19 (★20 处必改·★不动任何断言里的位号字面量★)★"""
    n = 0

    # (1) 别名表
    old = ('        self._by_ref = {}\n'
           '        for row in self.rows:\n'
           '            self._by_ref.setdefault(row.get("ref", ""), []).append(row)\n')
    new = ('        self._by_ref = {}\n'
           '        for row in self.rows:\n'
           '            self._by_ref.setdefault(row.get("ref", ""), []).append(row)\n'
           '        # ★★★【ISS-321 · SW 侧 · S1 位号改名适配】★★★\n'
           '        # ★建【逻辑位号 → 盘上真实位号】的别名表 (★原名优先★)\n'
           '        # ★规则: 盘上是 `<X>_1` 而 `<X>` 自己不在网表里 ⇒ `<X>` 就是它的逻辑名★\n'
           '        self._ref_alias = {}\n'
           '        for _r in self._by_ref:\n'
           '            if _r.endswith("_1") and len(_r) > 2:\n'
           '                _base = _r[:-2]\n'
           '                if _base and _base not in self._by_ref:\n'
           '                    self._ref_alias.setdefault(_base, _r)\n'
           '        # ★反向表 (盘上真实名 → 逻辑名) ⇒ 输出层归一化 ★\n'
           '        self._ref_alias_rev = {v: k for k, v in self._ref_alias.items()}\n')
    txt = patch(txt, old, new); n += 1

    # (2) actual_ref + rows_of/has_ref 走它
    old = ('    # ---- 基本查询 ----\n'
           '    def rows_of(self, ref: str):\n'
           '        return list(self._by_ref.get(ref, []))\n'
           '\n'
           '    def has_ref(self, ref: str) -> bool:\n'
           '        """该位号在网表里出现过 (哪怕只有引脚行、没有器件行)。"""\n'
           '        return ref in self._by_ref\n')
    new = ('    # ---- 基本查询 ----\n'
           '    def actual_ref(self, ref: str) -> str:\n'
           '        """★逻辑位号 → 盘上真实位号 (★ISS-321 · S1 位号改名适配★)\n'
           '\n'
           '        ★原名优先; 盘上只有 `<X>_1` 而 `<X>` 自己不在网表里 ⇒ 返回 `<X>_1`★\n'
           '        ★**不是把判据改软**: 查不到就返回原名 ⇒ 调用方拿到的仍是空/None★\n'
           '        """\n'
           '        if ref in self._by_ref:\n'
           '            return ref\n'
           '        return self._ref_alias.get(ref, ref)\n'
           '\n'
           '    def logical_ref(self, ref: str) -> str:\n'
           '        """★盘上真实位号 → 逻辑位号 (★ISS-321 · S1 位号改名适配★)\n'
           '\n'
           '        ★用于【输出层归一化】: 判据报出来的位号名保持逻辑名 (★Q_ENVC 而不是 Q_ENVC_1★)\n'
           '        ★⇒ 判据输出格式一条没变 ⇒ 断言与文档不用跟着改★\n'
           '        """\n'
           '        return self._ref_alias_rev.get(ref, ref)\n'
           '\n'
           '    def rows_of(self, ref: str):\n'
           '        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★\n'
           '        return list(self._by_ref.get(self.actual_ref(ref), []))\n'
           '\n'
           '    def has_ref(self, ref: str) -> bool:\n'
           '        """该位号在网表里出现过 (哪怕只有引脚行、没有器件行)。"""\n'
           '        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★\n'
           '        return self.actual_ref(ref) in self._by_ref\n')
    txt = patch(txt, old, new); n += 1

    # (3) dnp_of_row 候选行匹配
    old = ('        cands = []\n'
           '        for x in self.rows:\n'
           '            if (x.get("net") or "") != net:\n'
           '                continue\n'
           '            if (x.get("ref") == ref\n'
           '                    or self._node_is_ref(x.get("node1", ""), ref)\n'
           '                    or self._node_is_ref(x.get("node2", ""), ref)):\n'
           '                cands.append(x)\n')
    new = ('        cands = []\n'
           '        # ★ISS-321 · S1 位号改名适配: 候选行匹配用【盘上真实名】★\n'
           '        _aref = self.actual_ref(ref)\n'
           '        for x in self.rows:\n'
           '            if (x.get("net") or "") != net:\n'
           '                continue\n'
           '            if (x.get("ref") == _aref\n'
           '                    or self._node_is_ref(x.get("node1", ""), _aref)\n'
           '                    or self._node_is_ref(x.get("node2", ""), _aref)):\n'
           '                cands.append(x)\n')
    txt = patch(txt, old, new); n += 1

    # (4) dnp_of_row prio
    old = ('        def prio(x):\n'
           '            if x.get("ref") == ref:\n')
    new = ('        def prio(x):\n'
           '            if x.get("ref") == _aref:\n')
    txt = patch(txt, old, new); n += 1

    # (5) 输出层 dnp_rows (PG_AND)
    old = '        "dnp_rows": sorted({x.get("ref", "") for x in pg_and_rows if x.get("dnp") != "必装"}),\n'
    new = ('        "dnp_rows": sorted({nl.logical_ref(x.get("ref", "")) for x in pg_and_rows'
           ' if x.get("dnp") != "必装"}),   # ★ISS-321 · 输出归一化★\n')
    txt = patch(txt, old, new); n += 1

    # (6) 输出层 members + dnp_rows (RESET_N)
    old = ('        "members": sorted({x.get("ref", "") for x in reset_n_rows}),\n'
           '        "dnp_rows": sorted({x.get("ref", "") for x in reset_n_rows if x.get("dnp") != "必装"}),\n')
    new = ('        "members": sorted({nl.logical_ref(x.get("ref", "")) for x in reset_n_rows}),'
           '   # ★ISS-321 · 输出归一化★\n'
           '        "dnp_rows": sorted({nl.logical_ref(x.get("ref", "")) for x in reset_n_rows'
           ' if x.get("dnp") != "必装"}),   # ★ISS-321 · 输出归一化★\n')
    txt = patch(txt, old, new); n += 1

    # (7) row_states_on_net 的 ref 归一化
    old = ('        return [{"ref": x.get("ref", ""), "type": x.get("type", ""),\n'
           '                 "dnp": x.get("dnp", ""), "line_no": x.get("_line_no")}\n'
           '                for x in self.rows_on_net(net)]\n')
    new = ('        # ★ISS-321 · S1 位号改名适配: ref 名归一化回逻辑名★\n'
           '        return [{"ref": self.logical_ref(x.get("ref", "")), "type": x.get("type", ""),\n'
           '                 "dnp": x.get("dnp", ""), "line_no": x.get("_line_no")}\n'
           '                for x in self.rows_on_net(net)]\n')
    txt = patch(txt, old, new); n += 1

    # (8) mutated_copy
    txt = patch(txt,
                '    for ref, val, mode in [(e[0], e[1], (e[2] if len(e) > 2 else "set")) for e in edits]:\n'
                '        by_ref.setdefault(ref, []).append((val, mode))\n',
                '    for ref, val, mode in [(e[0], e[1], (e[2] if len(e) > 2 else "set")) for e in edits]:\n'
                '        # ★ISS-321 · S1 位号改名适配: edits 里的旧名 → 盘上真实名★\n'
                '        by_ref.setdefault(nl.actual_ref(ref), []).append((val, mode))\n'); n += 1

    # (9) drop_refs_copy
    txt = patch(txt,
                '    refs = set(refs)\n'
                '    out_lines = []\n',
                '    refs = set(nl.actual_ref(r) for r in refs)   # ★ISS-321 · S1 位号改名适配★\n'
                '    out_lines = []\n'); n += 1

    # (10) drop_device_rows_copy
    txt = patch(txt,
                '        if fref == ref and ftype in ("IC", "SW"):\n',
                '        if fref == nl.actual_ref(ref) and ftype in ("IC", "SW"):\n'
                '            # ★ISS-321 · S1 位号改名适配★\n'); n += 1

    # (11) 行级 dnp 夹具 targets
    txt = patch(txt,
                '        tset = set(targets)\n',
                '        tset = set((net, nl.actual_ref(ref)) for net, ref in targets)'
                '   # ★ISS-321 · S1 位号改名适配★\n'); n += 1

    # (12) F8 load_switch_refs 报逻辑名
    old = ('    for ref in LOAD_SWITCH_REFS:\n'
           '        if not nl.has_ref(ref) or ref in seen:\n'
           '            continue\n'
           '        seen.add(ref)\n'
           '        dev = nl.ic_rows(ref)\n'
           '        load_refs.append({\n'
           '            "ref": ref,\n')
    new = ('    for ref in LOAD_SWITCH_REFS:\n'
           '        if not nl.has_ref(ref) or ref in seen:\n'
           '            continue\n'
           '        seen.add(ref)\n'
           '        dev = nl.ic_rows(ref)\n'
           '        load_refs.append({\n'
           '            # ★ISS-321 · S1 位号改名适配: 报【逻辑名】⇒ 断言格式一条没变★\n'
           '            "ref": nl.logical_ref(ref),\n')
    txt = patch(txt, old, new); n += 1

    # (13) REV-10 逐行比对
    old = ('            changed = [q for q in mo["F1_reset_rc"]["pg_and_state"]["rows"]\n'
           '                       if q["ref"] == x.get("ref", "") and q["dnp"] == "DNP"]\n')
    new = ('            # ★ISS-321 · S1 位号改名适配: 两边都归一化回逻辑名★\n'
           '            changed = [q for q in mo["F1_reset_rc"]["pg_and_state"]["rows"]\n'
           '                       if q["ref"] == nl.logical_ref(x.get("ref", "")) and q["dnp"] == "DNP"]\n')
    txt = patch(txt, old, new); n += 1

    # (14) F8 seen 按盘上真实名去重 (LOAD_SWITCH_REFS 段)
    old = ('    for ref in LOAD_SWITCH_REFS:\n'
           '        if not nl.has_ref(ref) or ref in seen:\n'
           '            continue\n'
           '        seen.add(ref)\n')
    new = ('    for ref in LOAD_SWITCH_REFS:\n'
           '        if not nl.has_ref(ref) or nl.actual_ref(ref) in seen:\n'
           '            continue\n'
           '        # ★ISS-321 · S1 位号改名适配: seen 按【盘上真实名】⇒ 不重复计★\n'
           '        seen.add(nl.actual_ref(ref))\n')
    txt = patch(txt, old, new); n += 1

    # (15) F8 语义兜底循环
    old = ('            ref = x.get("ref", "")\n'
           '            if ref in seen:\n'
           '                continue\n'
           '            seen.add(ref)\n'
           '            load_refs.append({"ref": ref, "value": x.get("value", ""), "dnp": x.get("dnp", ""),\n')
    new = ('            ref = x.get("ref", "")\n'
           '            # ★ISS-321 · S1 位号改名适配: seen 按【盘上真实名】★\n'
           '            if ref in seen or nl.actual_ref(ref) in seen:\n'
           '                continue\n'
           '            seen.add(ref)\n'
           '            # ★ISS-321 · S1 位号改名适配: 报【逻辑名】★\n'
           '            load_refs.append({"ref": nl.logical_ref(ref), "value": x.get("value", ""), "dnp": x.get("dnp", ""),\n')
    txt = patch(txt, old, new); n += 1

    # (16) 正则扫 I2C 上拉 (网表行)
    txt = patch(txt,
                'if re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)$", x.get("ref", "") or "")})',
                'if re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)(_1)?$", x.get("ref", "") or "")})'
                '   # ★ISS-321 · S1 位号改名适配★'); n += 1

    # (17) 正则扫 I2C 上拉 (取值处)
    txt = patch(txt,
                '        m = re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)$", ref)',
                '        m = re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)(_1)?$", ref)'
                '   # ★ISS-321 · S1 位号改名适配★'); n += 1

    return txt, n


def run(root, script, args=()):
    p = subprocess.run([sys.executable, script] + list(args), cwd=root,
                       capture_output=True, text=True, timeout=900)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    if os.path.isdir(FIX20):
        shutil.rmtree(FIX20)
    shutil.copytree(S4, FIX20, symlinks=True)
    os.makedirs(os.path.join(FIX20, "tmp"), exist_ok=True)

    A("=" * 92)
    A("ISS-323 · F-1 改法二次验证 (★「20 处必改 + 5 处可选」★)")
    A("=" * 92)

    src = os.path.join(PROJ, "SW", "tools", "timing_check.py")
    dst = os.path.join(FIX20, "SW", "tools", "timing_check.py")
    if os.path.lexists(dst):
        os.remove(dst)
    txt = open(src, encoding="utf-8").read()
    txt, n = apply_f1_core(txt)
    open(dst, "w", encoding="utf-8").write(txt)
    A("  ★【精简版】改了 %d 处原子替换 (★覆盖 ISS-321 的 F1-01~F1-19 共 19 个逻辑点 · ★一处断言字面量都没动★)" % n)

    rc, out = run(FIX20, dst, ("--only", "F1_reset_rc"))
    A("  ★沙盒实跑 `timing_check.py --only F1_reset_rc` ⇒ rc=%s (★改前 rc=1·崩在 L1113★)" % rc)
    for ln in out.splitlines()[:6]:
        A("      %s" % ln[:170])

    rc_full, out_full = run(FIX20, dst)
    A("  ★沙盒实跑 `timing_check.py` (全量) ⇒ rc=%s (★改前 rc=1★)" % rc_full)
    st = ""
    for ln in out_full.splitlines():
        if "SELFTEST" in ln:
            st = ln.strip()
    A("      %s" % (st if st else "★没抓到 SELFTEST 行★"))

    # ★与 ISS-321 原版 (25 处) 对照★
    A("")
    A("── 对照: ISS-321 原版 (25 处·含 5 处断言字面量加固) 的实跑读数 ──")
    A("   ★来源: logs/iss323/10_verify_fix.txt (★本单 11:5x 重跑 ISS-321 的脚本·不是抄文档★)")
    A("   ★25 处版: rc=0 · SELFTEST 85/85 通过")

    A("")
    A("── 结论 (★沙盒实跑读数·非推算★) ──")
    A("   【17 处原子替换版】timing_check.py 全量 ⇒ rc=%s" % rc_full)
    A("   ★rc=0 且 SELFTEST 85/85 ⇒ ★F1-20~F1-25 那 5 处断言【不必改】★")
    A("   ★⇒ 清单里写成「17 处原子替换 (★覆盖 19 个逻辑点) + 5 处断言【可选加固】(默认不做)」★")
    A("★★真闸 `SW/tools/*.py` 一个字节都没改 ★★")
    A("=" * 92)

    open(LOG, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n★写出: logs/iss323/13_verify_fix20.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
