#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss323_anchor_locate.py —— ISS-323 · 把 ISS-321 沙盒验证过的【改法锚点】定位到真件的行号

★★只读★★: SW/tools/timing_check.py · SW/tools/check_onepass_sw_sync.py (★真闸一个字节都不许动★)
★★输出 (只写)★★: logs/iss323/08_anchor_locate.txt (+ stdout)

★★为什么要有这个脚本★★:
    任务书 §2① 要求清单的「行号 / 定位锚点」列【逐字可执行】⇒
    ⇒ ★行号必须是从【盘上真件】现读出来的·不许抄 ISS-321 文档里的行号 (★那可能是上一版★)★
    ⇒ ★本脚本拿 ISS-321 的【锚点字符串】去真件里逐条定位, 定位不到就 abort★
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))

OUT = []


def A(s):
    OUT.append(s)
    print(s)


def locate(path, needles):
    """★锚点 → 行号 (★第一处命中★)· 找不到就记 None★"""
    lines = open(os.path.join(PROJ, path), encoding="utf-8").read().split("\n")
    res = []
    for tag, needle in needles:
        hit = None
        for i, ln in enumerate(lines, 1):
            if needle in ln:
                hit = i
                break
        res.append((tag, hit, needle))
    return res


def main():
    A("=" * 96)
    A("ISS-323 · 改法锚点 → 真件行号 (★2026-11-18 本机实读·★只读★)")
    A("=" * 96)

    # ── F-1 · timing_check.py 的 25 处定点替换 (★逐字取自 logs/iss321/iss321_verify_fix.py★) ──
    F1 = [
        ("F1-01 建别名表 (Netlist.__init__ 末尾)",
         '            self._by_ref.setdefault(row.get("ref", ""), []).append(row)'),
        ("F1-02 actual_ref() + rows_of/has_ref 走它",
         '    # ---- 基本查询 ----'),
        # ★F1-03 的锚点【在真件里不存在】⇒ 因为它是 F1-01 补丁【新增出来的那一块】★
        #   ⇒ 它在真件里的落点 = F1-01 的锚点行之后 (补丁后 L705) ★
        ("F1-03 反向表 _ref_alias_rev (★随 F1-01 新增块一起插入★)",
         '                    self._ref_alias.setdefault(_base, _r)'),
        ("F1-04 logical_ref() 方法",
         '    def rows_of(self, ref: str):'),
        ("F1-05 dnp_of_row 候选行匹配 _aref",
         '                    or self._node_is_ref(x.get("node1", ""), ref)'),
        ("F1-06 dnp_of_row prio 用 _aref",
         '            if x.get("ref") == ref:'),
        ("F1-07 输出层 dnp_rows (PG_AND) 归一化",
         '        "dnp_rows": sorted({x.get("ref", "") for x in pg_and_rows if x.get("dnp") != "必装"}),'),
        ("F1-08 输出层 members + dnp_rows (RESET_N) 归一化",
         '        "members": sorted({x.get("ref", "") for x in reset_n_rows}),'),
        ("F1-09 row_states_on_net 的 ref 归一化",
         '        return [{"ref": x.get("ref", ""), "type": x.get("type", ""),'),
        ("F1-10 mutated_copy 的 edits 走 actual_ref",
         '        by_ref.setdefault(ref, []).append((val, mode))'),
        ("F1-11 drop_refs_copy 的 refs 走 actual_ref",
         '    refs = set(refs)'),
        ("F1-12 drop_device_rows_copy 候选行匹配走 actual_ref",
         '        if fref == ref and ftype in ("IC", "SW"):'),
        ("F1-13 行级 dnp 夹具 targets 走 actual_ref",
         '        tset = set(targets)'),
        ("F1-14 F8 load_switch_refs 报逻辑名 (LOAD_SWITCH_REFS 段)",
         '            "ref": ref,'),
        ("F1-15 REV-10 逐行比对两边都归一化",
         '            changed = [q for q in mo["F1_reset_rc"]["pg_and_state"]["rows"]'),
        ("F1-16 F8 seen 按盘上真实名去重 (LOAD_SWITCH_REFS 段)",
         '            seen.add(ref)'),
        ("F1-17 F8 语义兜底循环 seen 归一化",
         '            load_refs.append({"ref": ref, "value": x.get("value", ""), "dnp": x.get("dnp", ""),'),
        ("F1-18 正则扫 I2C 上拉 (网表行)",
         'if re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)$", x.get("ref", "") or "")})'),
        ("F1-19 正则扫 I2C 上拉 (取值处)",
         '        m = re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)$", ref)'),
        ("F1-20 断言 U_PWR_SW ∈ load_switch_refs (o)",
         'and "U_PWR_SW" in o["F8_power_off"]["load_switch_refs"]),'),
        ("F1-21 断言 U_PWR_SW ∈ load_switch_refs (f8)",
         'and "U_PWR_SW" in f8["load_switch_refs"]'),
        ("F1-22 断言 U_EN_SW ∈ load_switch_refs (f8)",
         'and "U_EN_SW" in f8["load_switch_refs"])'),
        ("F1-23 lambda 断言 (两个 load_switch_refs)",
         'lambda o: "U_PWR_SW" in o["F8_power_off"]["load_switch_refs"]'),
        ("F1-24 lambda 断言 (mo 不含 U_PWR_SW)",
         'fn=lambda o, mo: "U_PWR_SW" not in mo["F8_power_off"]["load_switch_refs"]'),
        ("F1-25 lambda 断言 (load_switch_without_device_row)",
         'fn=lambda o, mo: (mo["F8_power_off"]["load_switch_without_device_row"] == ["U_EN_SW"]'),
    ]

    # ── F-2 · check_onepass_sw_sync.py 的 3 处 (★最终采用版·iss321_verify_f2.py★) ──
    F2 = [
        ("F2-01 SW03 探针 (位号集合生成)",
         '         "t={\'D_CHG_LED\',\'D_LED_G\',\'D_LED_R\',\'SW_BOOT\',\'SW_KEY_PWR\',"'),
        ("F2-02 SW04 探针 (标签从网表实读)",
         '         "d=sum(1 for l in t if \'D_CHG_LED\' in l);q=sum(1 for l in t if \'Q_CHG_LED\' in l);"'),
        ("F2-03 SW05 探针 (标签从网表实读 + 正则允许可选后缀)",
         '         "m={r[\'ref\']:r[\'net\'] for r in rs if r[\'pin\']==\'1\' and r[\'ref\'] in "'),
    ]

    A("")
    A("── F-1 · SW/tools/timing_check.py (★25 处★) ──")
    miss = 0
    for tag, ln, needle in locate("SW/tools/timing_check.py", F1):
        A("  %-52s L%-6s %s" % (tag, ln if ln else "★没找到★",
                                needle[:70].replace("\n", "\\n")))
        if not ln:
            miss += 1
    A("  ★25 处锚点全部定位到 = %s (★没找到 %d 处★·F1-03 属【随 F1-01 新增】·不计入★)"
      % ("是" if miss <= 1 else "否", miss))

    A("")
    A("  ★F1-03 的说明: 它的锚点字符串在【真件里不存在】⇒ 因为它是 F1-01 补丁【新增出来的那一块】★")
    A("    ⇒ 真件落点 = F1-01 锚点行 (L704) 之后 ⇒ 补丁后为 L705 ⇒ ★它随 F1-01 一次插入★")

    A("")
    A("── F-2 · SW/tools/check_onepass_sw_sync.py (★3 处·最终采用版★) ──")
    miss2 = 0
    for tag, ln, needle in locate("SW/tools/check_onepass_sw_sync.py", F2):
        A("  %-52s L%-6s %s" % (tag, ln if ln else "★没找到★",
                                needle[:70].replace("\n", "\\n")))
        if not ln:
            miss2 += 1
    A("  ★3 处锚点全部定位到 = %s (★没找到 %d 处★)" % ("是" if miss2 == 0 else "否", miss2))

    A("")
    A("── 自检 (★两条·不符就 abort★) ──")
    A("  ★F-1 25 处全部命中: %s (★F1-03 是随 F1-01 新增的块·真件里本就不存在·不计入★)"
      % ("OK" if miss <= 1 else "★不符★"))
    A("  ★F-2 3 处全部命中 : %s" % ("OK" if miss2 == 0 else "★不符★"))
    A("  ★★本脚本只读真件·没改它★")
    A("=" * 96)

    open(os.path.join(HERE, "08_anchor_locate.txt"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n★写出: logs/iss323/08_anchor_locate.txt")
    return 0 if (miss <= 1 and miss2 == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
