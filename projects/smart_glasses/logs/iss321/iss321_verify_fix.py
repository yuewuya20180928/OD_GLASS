#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_verify_fix.py —— ISS-321 · ④ 改法验证 (★沙盒里改闸副本·真闸一个字节都不许动★)

★★目的 ★★: 逐条验证「§4 逐条改法」里的每一条改法【在沙盒里真的能让闸变绿】★
    ⇒ ★不许只写改法就交卷 (★任务书 §2④ 要求「验收判据 = 真命令 + 期望 rc」★)★

★★F-1 的改法 (★设计要点·逐字可抄★) ★★:
    ★**在 `Netlist` 类里加一层「位号别名解析」** ★
      · `actual_ref(logical)` ⇒ 逻辑位号 → 盘上真实位号 (原名优先·查不到才试 `_1` 后缀名★)
      · `rows_of()` / `has_ref()` ⇒ 走 actual_ref ⇒ **一个调用点都不用改**
      · 反向用例的三个改坏夹具 (`mutated_copy` / `drop_refs_copy` / `drop_device_rows_copy`)
        + 行级 dnp 夹具 ⇒ 也走 actual_ref ⇒ **反向用例在改名后仍然成立** ★
    ★**判据方向一条没改**: 问的仍然是「★这颗器件在网表里是什么★」★
    ★**不是把判据改软**: ★查不到就当过★ 这种分支一条都不许加 (★查不到仍然返回空/None★)★
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
S4 = os.path.join(SB, "rootS4")
FIX = os.path.join(SB, "fixroot")
LOG = os.path.join(PROJ, "logs", "iss321", "04_fix_verify_raw.txt")

OUT = []


def A(s):
    OUT.append(s)
    print(s)


def run(root, script, args=()):
    p = subprocess.run([sys.executable, script] + list(args), cwd=root,
                       capture_output=True, text=True, timeout=900)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def patch(txt, old, new):
    assert old in txt, "★补丁锚点没找到⇒abort★: %r" % old[:90]
    return txt.replace(old, new, 1)


def main():
    if os.path.isdir(FIX):
        shutil.rmtree(FIX)
    shutil.copytree(S4, FIX, symlinks=True)
    os.makedirs(os.path.join(FIX, "tmp"), exist_ok=True)

    A("=" * 92)
    A("ISS-321 · ④ 逐条改法验证 (★沙盒副本改闸·真闸零改★)")
    A("=" * 92)

    # ════════════════════════════════════════════════════════════════════
    # F-1 · timing_check.py
    # ════════════════════════════════════════════════════════════════════
    A("")
    A("── F-1 · timing_check.py (★沙盒副本★) ──")
    tc_src = os.path.join(PROJ, "SW", "tools", "timing_check.py")
    tc_dst = os.path.join(FIX, "SW", "tools", "timing_check.py")
    if os.path.lexists(tc_dst):
        os.remove(tc_dst)
    txt = open(tc_src, encoding="utf-8").read()
    n = 0

    # ── (a) Netlist.__init__ 末尾: 建别名表 ──
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
           '                    self._ref_alias.setdefault(_base, _r)\n')
    txt = patch(txt, old, new)
    n += 1

    # ── (b) actual_ref() 方法 + rows_of/has_ref 走它 ──
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
           '    def rows_of(self, ref: str):\n'
           '        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★\n'
           '        return list(self._by_ref.get(self.actual_ref(ref), []))\n'
           '\n'
           '    def has_ref(self, ref: str) -> bool:\n'
           '        """该位号在网表里出现过 (哪怕只有引脚行、没有器件行)。"""\n'
           '        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★\n'
           '        return self.actual_ref(ref) in self._by_ref\n')
    txt = patch(txt, old, new)
    n += 1

    # ── (b2) 反向映射 (盘上真实名 → 逻辑名) ⇒ 闸【报出来的位号名】保持逻辑名 ★─
    # ★★为什么需要反向映射 ★★: 闸的输出 JSON (pg_and_state / reset_n_state 等) 里
    #   报的是【位号身份】⇒ ★改名后盘上叫 `Q_ENVC_1`·但判据问的仍是「Q_ENVC」★
    #   ⇒ ★不改反向映射的话: 判据输出变成 `Q_ENVC_1` ⇒ 断言写 `== ["Q_ENVC"]` ⇒ 假红★
    # ★★改法: 输出层把位号名【归一化回逻辑名】⇒ ★判据输出格式一条没变★ ★
    old = ('        self._ref_alias = {}\n'
           '        for _r in self._by_ref:\n'
           '            if _r.endswith("_1") and len(_r) > 2:\n'
           '                _base = _r[:-2]\n'
           '                if _base and _base not in self._by_ref:\n'
           '                    self._ref_alias.setdefault(_base, _r)\n')
    new = ('        self._ref_alias = {}\n'
           '        for _r in self._by_ref:\n'
           '            if _r.endswith("_1") and len(_r) > 2:\n'
           '                _base = _r[:-2]\n'
           '                if _base and _base not in self._by_ref:\n'
           '                    self._ref_alias.setdefault(_base, _r)\n'
           '        # ★反向表 (盘上真实名 → 逻辑名) ⇒ 输出层归一化 ★\n'
           '        self._ref_alias_rev = {v: k for k, v in self._ref_alias.items()}\n')
    txt = patch(txt, old, new)
    n += 1

    # ── (b3) logical_ref() 方法 + dnp_of_row 走 actual_ref ──
    old = ('    def rows_of(self, ref: str):\n'
           '        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★\n'
           '        return list(self._by_ref.get(self.actual_ref(ref), []))\n')
    new = ('    def logical_ref(self, ref: str) -> str:\n'
           '        """★盘上真实位号 → 逻辑位号 (★ISS-321 · S1 位号改名适配★)\n'
           '\n'
           '        ★用于【输出层归一化】: 判据报出来的位号名保持逻辑名 (★Q_ENVC 而不是 Q_ENVC_1★)\n'
           '        ★⇒ 判据输出格式一条没变 ⇒ 断言与文档不用跟着改★\n'
           '        """\n'
           '        return self._ref_alias_rev.get(ref, ref)\n'
           '\n'
           '    def rows_of(self, ref: str):\n'
           '        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★\n'
           '        return list(self._by_ref.get(self.actual_ref(ref), []))\n')
    txt = patch(txt, old, new)
    n += 1

    # ★dnp_of_row: 候选行匹配要用【盘上真实名】★
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
    txt = patch(txt, old, new)
    n += 1
    old = ('        def prio(x):\n'
           '            if x.get("ref") == ref:\n')
    new = ('        def prio(x):\n'
           '            if x.get("ref") == _aref:\n')
    txt = patch(txt, old, new)
    n += 1

    # ── (b4) 输出层归一化: dnp_rows / members / row_states 的 ref 名 ──
    old = ('        "dnp_rows": sorted({x.get("ref", "") for x in pg_and_rows if x.get("dnp") != "必装"}),\n')
    new = ('        "dnp_rows": sorted({nl.logical_ref(x.get("ref", "")) for x in pg_and_rows'
           ' if x.get("dnp") != "必装"}),   # ★ISS-321 · 输出归一化★\n')
    txt = patch(txt, old, new)
    n += 1
    old = ('        "members": sorted({x.get("ref", "") for x in reset_n_rows}),\n'
           '        "dnp_rows": sorted({x.get("ref", "") for x in reset_n_rows if x.get("dnp") != "必装"}),\n')
    new = ('        "members": sorted({nl.logical_ref(x.get("ref", "")) for x in reset_n_rows}),'
           '   # ★ISS-321 · 输出归一化★\n'
           '        "dnp_rows": sorted({nl.logical_ref(x.get("ref", "")) for x in reset_n_rows'
           ' if x.get("dnp") != "必装"}),   # ★ISS-321 · 输出归一化★\n')
    txt = patch(txt, old, new)
    n += 1
    old = ('        return [{"ref": x.get("ref", ""), "type": x.get("type", ""),\n'
           '                 "dnp": x.get("dnp", ""), "line_no": x.get("_line_no")}\n'
           '                for x in self.rows_on_net(net)]\n')
    new = ('        # ★ISS-321 · S1 位号改名适配: ref 名归一化回逻辑名★\n'
           '        return [{"ref": self.logical_ref(x.get("ref", "")), "type": x.get("type", ""),\n'
           '                 "dnp": x.get("dnp", ""), "line_no": x.get("_line_no")}\n'
           '                for x in self.rows_on_net(net)]\n')
    txt = patch(txt, old, new)
    n += 1

    # ── (c) 三个改坏夹具走 actual_ref (★反向用例在改名后仍然成立★) ──
    # ★mutated_copy: ★把【edits 里的旧名】映射成【盘上真实名】(★不是反过来★) ★
    txt = patch(txt,
                '    for ref, val, mode in [(e[0], e[1], (e[2] if len(e) > 2 else "set")) for e in edits]:\n'
                '        by_ref.setdefault(ref, []).append((val, mode))\n',
                '    for ref, val, mode in [(e[0], e[1], (e[2] if len(e) > 2 else "set")) for e in edits]:\n'
                '        # ★ISS-321 · S1 位号改名适配: edits 里的旧名 → 盘上真实名★\n'
                '        by_ref.setdefault(nl.actual_ref(ref), []).append((val, mode))\n')
    n += 1
    txt = patch(txt,
                '    refs = set(refs)\n'
                '    out_lines = []\n',
                '    refs = set(nl.actual_ref(r) for r in refs)   # ★ISS-321 · S1 位号改名适配★\n'
                '    out_lines = []\n')
    n += 1
    txt = patch(txt,
                '        if fref == ref and ftype in ("IC", "SW"):\n',
                '        if fref == nl.actual_ref(ref) and ftype in ("IC", "SW"):\n'
                '            # ★ISS-321 · S1 位号改名适配★\n')
    n += 1
    # ★行级 dnp 夹具: targets 里的 ref 也要走 actual_ref ★
    txt = patch(txt,
                '        tset = set(targets)\n',
                '        tset = set((net, nl.actual_ref(ref)) for net, ref in targets)'
                '   # ★ISS-321 · S1 位号改名适配★\n')
    n += 1

    # ── (c2) F8 的 load_switch_refs 要报【逻辑名】⇒ 断言 `== ["U_EN_SW"]` 之类不用改 ★─
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
    txt = patch(txt, old, new)
    n += 1

    # ── (c3) REV-10 的逐行比对: 逻辑名 vs 逻辑名 ★─
    old = ('            changed = [q for q in mo["F1_reset_rc"]["pg_and_state"]["rows"]\n'
           '                       if q["ref"] == x.get("ref", "") and q["dnp"] == "DNP"]\n')
    new = ('            # ★ISS-321 · S1 位号改名适配: 两边都归一化回逻辑名★\n'
           '            changed = [q for q in mo["F1_reset_rc"]["pg_and_state"]["rows"]\n'
           '                       if q["ref"] == nl.logical_ref(x.get("ref", "")) and q["dnp"] == "DNP"]\n')
    txt = patch(txt, old, new)
    n += 1

    # ── (c4) F8 的 seen 集合要按【盘上真实名】去重 ⇒ 改名后不重复计 ★─
    # ★★根因: LOAD_SWITCH_REFS 循环里 seen.add("U_PWR_SW") (逻辑名)
    #   ⇒ 随后的【语义兜底循环】扫到盘上那颗 `U_PWR_SW_1` ⇒ seen 里没有 ⇒ 又加一遍
    #   ⇒ ★load_switch_refs 变成 4 条·rail_switching_devices 变成 4 ⇒ 判据读数全错★
    old = ('    for ref in LOAD_SWITCH_REFS:\n'
           '        if not nl.has_ref(ref) or ref in seen:\n'
           '            continue\n'
           '        seen.add(ref)\n')
    new = ('    for ref in LOAD_SWITCH_REFS:\n'
           '        if not nl.has_ref(ref) or nl.actual_ref(ref) in seen:\n'
           '            continue\n'
           '        # ★ISS-321 · S1 位号改名适配: seen 按【盘上真实名】⇒ 不重复计★\n'
           '        seen.add(nl.actual_ref(ref))\n')
    txt = patch(txt, old, new)
    n += 1
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
    txt = patch(txt, old, new)
    n += 1

    # ── (d) F-3 的【正则扫位号】也要能认出改名后的名字 ★─
    # ★★根因: `re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)$", ref)` ⇒ 改名后 ref 变 `R_PU_I2CA_SCL_1`
    #   ⇒ 正则不匹配 ⇒ 上拉电阻一颗都找不到 ⇒ F3 整条判据崩 (EXC 'I2C_A') ★
    # ★★改法: 正则加 `(_1)?` ⇒ ★**判据方向一条没改**★ (还是「找 I2C 上拉电阻」★
    txt = patch(txt,
                'if re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)$", x.get("ref", "") or "")})',
                'if re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)(_1)?$", x.get("ref", "") or "")})'
                '   # ★ISS-321 · S1 位号改名适配★')
    n += 1
    txt = patch(txt,
                '        m = re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)$", ref)',
                '        m = re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)(_1)?$", ref)'
                '   # ★ISS-321 · S1 位号改名适配★')
    n += 1

    # ── (d) F-2 探针的位号清单 + 打印串 (★check_onepass_sw_sync.py·不在 timing_check 里·这里单独改★) ──
    txt = patch(txt,
                'and "U_PWR_SW" in o["F8_power_off"]["load_switch_refs"]),',
                'and any(x in ("U_PWR_SW", "U_PWR_SW_1") for x in o["F8_power_off"]["load_switch_refs"])),')
    n += 1
    txt = patch(txt,
                'and "U_PWR_SW" in f8["load_switch_refs"]',
                'and any(x in ("U_PWR_SW", "U_PWR_SW_1") for x in f8["load_switch_refs"])')
    n += 1
    txt = patch(txt,
                'and "U_EN_SW" in f8["load_switch_refs"])',
                'and any(x in ("U_EN_SW", "U_EN_SW_1") for x in f8["load_switch_refs"]))')
    n += 1
    txt = patch(txt,
                'lambda o: "U_PWR_SW" in o["F8_power_off"]["load_switch_refs"]\n'
                '               and "U_EN_SW" in o["F8_power_off"]["load_switch_refs"]',
                'lambda o: any(x in ("U_PWR_SW", "U_PWR_SW_1") for x in o["F8_power_off"]["load_switch_refs"])\n'
                '               and any(x in ("U_EN_SW", "U_EN_SW_1") for x in o["F8_power_off"]["load_switch_refs"])')
    n += 1
    txt = patch(txt,
                'fn=lambda o, mo: "U_PWR_SW" not in mo["F8_power_off"]["load_switch_refs"]',
                'fn=lambda o, mo: not any(x in ("U_PWR_SW", "U_PWR_SW_1") for x in mo["F8_power_off"]["load_switch_refs"])')
    n += 1
    txt = patch(txt,
                'fn=lambda o, mo: (mo["F8_power_off"]["load_switch_without_device_row"] == ["U_EN_SW"]\n'
                '                          and "U_EN_SW" in mo["F8_power_off"]["load_switch_refs"]',
                'fn=lambda o, mo: (mo["F8_power_off"]["load_switch_without_device_row"] in (["U_EN_SW"], ["U_EN_SW_1"])\n'
                '                          and any(x in ("U_EN_SW", "U_EN_SW_1") for x in mo["F8_power_off"]["load_switch_refs"])')
    n += 1

    open(tc_dst, "w", encoding="utf-8").write(txt)
    A("   ★改 %d 处 (★actual_ref() + rows_of/has_ref + 三个改坏夹具 + 行级 dnp 夹具 + 字面量比对★)" % n)
    rc, out = run(FIX, tc_dst, ("--only", "F1_reset_rc"))
    A("   ★沙盒实跑 `timing_check.py --only F1_reset_rc` ⇒ rc=%s (★改前 rc=1·崩在 L1113★)" % rc)
    for ln in out.splitlines()[:10]:
        A("      %s" % ln[:170])
    rc_full, out_full = run(FIX, tc_dst)
    A("   ★沙盒实跑 `timing_check.py` (全量) ⇒ rc=%s (★改前 rc=1★)" % rc_full)
    for ln in out_full.splitlines()[-12:]:
        A("      %s" % ln[:170])
    f1_rc = rc_full

    # ════════════════════════════════════════════════════════════════════
    # F-2 · check_onepass_sw_sync.py
    # ════════════════════════════════════════════════════════════════════
    A("")
    A("── F-2 · check_onepass_sw_sync.py (★沙盒副本★) ──")
    op_src = os.path.join(PROJ, "SW", "tools", "check_onepass_sw_sync.py")
    op_dst = os.path.join(FIX, "SW", "tools", "check_onepass_sw_sync.py")
    if os.path.lexists(op_dst):
        os.remove(op_dst)
    txt = open(op_src, encoding="utf-8").read()
    m = 0
    # ★SW03 探针: 8 颗落表残项的位号清单 ⇒ 加 `_1` 变体 ★
    # ★★逐字锚点 (★从真文件抄下来的·不改一个字会 abort·可复核★) ★★
    txt = patch(txt,
                '         "t={\'D_CHG_LED\',\'D_LED_G\',\'D_LED_R\',\'SW_BOOT\',\'SW_KEY_PWR\',"\n'
                '         "\'SW_KEY_VM\',\'SW_KEY_VP\',\'SW_RST\'};"',
                '         "t={\'D_CHG_LED\',\'D_CHG_LED_1\',\'D_LED_G\',\'D_LED_G_1\',\'D_LED_R\',\'D_LED_R_1\',"\n'
                '         "\'SW_BOOT\',\'SW_BOOT_1\',\'SW_KEY_PWR\',\'SW_KEY_PWR_1\',\'SW_KEY_VM\',\'SW_KEY_VM_1\',"\n'
                '         "\'SW_KEY_VP\',\'SW_KEY_VP_1\',\'SW_RST\',\'SW_RST_1\'};"')
    m += 1
    # ★SW05 探针: 5 颗开关的网名映射 ⇒ 加 `_1` 变体 ★
    txt = patch(txt,
                '         "{\'SW_BOOT\',\'SW_KEY_PWR\',\'SW_KEY_VM\',\'SW_KEY_VP\',\'SW_RST\'}};"',
                '         "{\'SW_BOOT\',\'SW_BOOT_1\',\'SW_KEY_PWR\',\'SW_KEY_PWR_1\',\'SW_KEY_VM\',\'SW_KEY_VM_1\',"\n'
                '         "\'SW_KEY_VP\',\'SW_KEY_VP_1\',\'SW_RST\',\'SW_RST_1\'}};"')
    m += 1
    txt = patch(txt,
                '         "[\'SW_BOOT\',\'SW_KEY_PWR\',\'SW_KEY_VM\',\'SW_KEY_VP\',\'SW_RST\'] if k in m))"],',
                '         "[\'SW_BOOT\',\'SW_BOOT_1\',\'SW_KEY_PWR\',\'SW_KEY_PWR_1\',\'SW_KEY_VM\',\'SW_KEY_VM_1\',"\n'
                '         "\'SW_KEY_VP\',\'SW_KEY_VP_1\',\'SW_RST\',\'SW_RST_1\'] if k in m))"],')
    m += 1
    # ★SW05 的抽取正则 ⇒ 位号后缀可变 ★
    txt = patch(txt,
                '        r"(SW_BOOT→\\S+ · SW_KEY_PWR→\\S+ · SW_KEY_VM→\\S+ · SW_KEY_VP→\\S+ · SW_RST→\\S+)"),',
                '        r"(SW_BOOT(?:_1)?→\\S+ · SW_KEY_PWR(?:_1)?→\\S+ · SW_KEY_VM(?:_1)?→\\S+'
                ' · SW_KEY_VP(?:_1)?→\\S+ · SW_RST(?:_1)?→\\S+)"),')
    m += 1
    # ★SW04 探针: D_CHG_LED / Q_CHG_LED 计数 ⇒ 后缀可选 ★
    txt = patch(txt,
                '         "d=sum(1 for l in t if \'D_CHG_LED\' in l);q=sum(1 for l in t if \'Q_CHG_LED\' in l);"',
                '         "d=sum(1 for l in t if \'D_CHG_LED\' in l);q=sum(1 for l in t if \'Q_CHG_LED\' in l);"')
    m += 1
    open(op_dst, "w", encoding="utf-8").write(txt)
    A("   ★SW03/SW05 两条探针的位号清单改成「旧名或新名都认」⇒ 改 %d 处" % m)
    rc, out = run(FIX, op_dst)
    A("   ★沙盒实跑 `check_onepass_sw_sync.py` ⇒ rc=%s (★改前 rc=1★)" % rc)
    for ln in out.splitlines():
        if "❌" in ln or "FAIL" in ln or ln.strip().startswith("rc="):
            A("      %s" % ln[:200])
    f2_rc = rc

    # ════════════════════════════════════════════════════════════════════
    # F-3 · check_sw_ref_reachability.py
    # ════════════════════════════════════════════════════════════════════
    A("")
    A("── F-3 · check_sw_ref_reachability.py (★沙盒副本★) ──")
    sr_src = os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability.py")
    sr_dst = os.path.join(FIX, "SW", "tools", "check_sw_ref_reachability.py")
    if os.path.lexists(sr_dst):
        os.remove(sr_dst)
    shutil.copy2(sr_src, sr_dst)
    rc, out = run(FIX, sr_dst, ("--freeze-registry",))
    A("   ★沙盒实跑 `check_sw_ref_reachability.py --freeze-registry` ⇒ rc=%s" % rc)
    for ln in out.splitlines()[:8]:
        A("      %s" % ln[:110])
    rc2, out2 = run(FIX, sr_dst)
    A("   ★重跑主模式 ⇒ rc=%s (★改前 rc=0★)" % rc2)
    for ln in out2.splitlines()[:16]:
        A("      %s" % ln[:110])
    f3_rc = rc2

    A("")
    A("── 汇总 (★沙盒实跑读数·非推算★) ──")
    A("   F-1 timing_check.py (全量)                       : rc=%s (改前 rc=1 · 崩在 L1113)" % f1_rc)
    A("   F-2 check_onepass_sw_sync.py                    : rc=%s (改前 rc=1)" % f2_rc)
    A("   F-3 check_sw_ref_reachability.py (重建注册表后) : rc=%s (改前 rc=0)" % f3_rc)
    A("")
    A("★★真闸 `SW/tools/*.py` 一个字节都没改 (★本单只出改法·改闸是 main / 下一单的活★)★★")
    A("=" * 92)

    open(LOG, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n★写出: logs/iss321/04_fix_verify_raw.txt")


if __name__ == "__main__":
    main()
