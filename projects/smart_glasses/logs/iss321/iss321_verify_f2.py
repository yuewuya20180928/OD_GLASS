#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss321_verify_f2.py —— ISS-321 · F-2 改法的【改名无关】版本验证 (★沙盒副本·真闸零改★)

★★为什么要有这个版本 (★本单最关键的一步·由 §2③ 的实跑读数逼出来的★) ★★:
    F-2 v1 (把 8 颗位号各写一个 `_1` 变体) ⇒ ★SW03 转绿·但 SW04/SW05 仍红★
    ⇒ 根因: ★探针【打印出来的标签】与【清单 current_state 里的标签】两边都要跟着改名★
    ⇒ ★正解: 探针不该写死任何标签 ⇒ ★从网表实读★ ⇒ ★改名前后输出【完全一致】★
    ⇒ ★**这才是「本来就该 rename-safe」的真改法**★

★★三个探针的改名无关改法 (★逐字·可抄★) ★★:
    SW03  ★位号集合用「基名 + 基名加后缀」生成 ⇒ 不写死任何改名后名★
    SW04  ★标签从网表实读 (★网表里那颗叫什么就打印什么★) ⇒ 改名后自动跟着变★
    SW05  ★同上 + 抽取正则允许可选后缀★
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
S4 = os.path.join(SB, "rootS4")
FIX = os.path.join(SB, "fixroot2")
LOG = os.path.join(PROJ, "logs", "iss321", "06_f2_rename_agnostic_raw.txt")

OUT = []


def A(s):
    OUT.append(s)
    print(s)


def patch(txt, old, new):
    assert old in txt, "★锚点没找到⇒abort★: %r" % old[:100]
    return txt.replace(old, new, 1)


def apply_f2(txt):
    n = 0
    # ── SW03: 位号集合用「基名 + 基名加后缀」生成 (★不写死任何改名后名★) ──
    txt = patch(txt,
                '         "t={\'D_CHG_LED\',\'D_LED_G\',\'D_LED_R\',\'SW_BOOT\',\'SW_KEY_PWR\',"\n'
                '         "\'SW_KEY_VM\',\'SW_KEY_VP\',\'SW_RST\'};"',
                '         "t={r for n in (\'D_CHG_LED\',\'D_LED_G\',\'D_LED_R\',\'SW_BOOT\',\'SW_KEY_PWR\',\'SW_KEY_VM\',\'SW_KEY_VP\',\'SW_RST\') for r in (n,n+\'_\'+chr(49))};"')
    n += 1
    # ── SW04: 标签从网表实读 (★网表里那颗叫什么就打印什么★) ──
    txt = patch(txt,
                '         "p=\'SW/SHUTDOWN_SEMANTICS_SPEC.md\';t=open(p,encoding=\'utf-8\').read().splitlines();"\n'
                '         "d=sum(1 for l in t if \'D_CHG_LED\' in l);q=sum(1 for l in t if \'Q_CHG_LED\' in l);"\n'
                '         "print(\'D_CHG_LED %d 次 · Q_CHG_LED %d 次\' % (d,q))"],\n'
                '        r"(D_CHG_LED \\d+ 次 · Q_CHG_LED \\d+ 次)"),',
                '         "p=\'SW/SHUTDOWN_SEMANTICS_SPEC.md\';t=open(p,encoding=\'utf-8\').read().splitlines();"\n'
                '         "bs=lambda x:x[:-2] if x.endswith(\'_\'+chr(49)) else x;"\n'
                '         "import csv;inv={bs(r[\'ref\']):r[\'ref\'] for r in csv.DictReader(open(\'HW/netlist_v1.csv\')) if r.get(\'ref\')};"\n'
                '         "dn=inv.get(\'D_CHG_LED\',\'D_CHG_LED\');qn=inv.get(\'Q_CHG_LED\',\'Q_CHG_LED\');"\n'
                '         "d=sum(1 for l in t if dn in l);q=sum(1 for l in t if qn in l);"\n'
                '         "print(\'%s %d 次 · %s %d 次\' % (dn,d,qn,q))"],\n'
                '        r"(D_CHG_LED(?:_\\d+)? \\d+ 次 · Q_CHG_LED(?:_\\d+)? \\d+ 次)"),')
    n += 1
    # ── SW05: 标签从网表实读 + 正则允许可选后缀 ──
    txt = patch(txt,
                '         "m={r[\'ref\']:r[\'net\'] for r in rs if r[\'pin\']==\'1\' and r[\'ref\'] in "\n'
                '         "{\'SW_BOOT\',\'SW_KEY_PWR\',\'SW_KEY_VM\',\'SW_KEY_VP\',\'SW_RST\'}};"\n'
                '         "print(\' · \'.join(\'%s→%s\'%(k,m[k]) for k in "\n'
                '         "[\'SW_BOOT\',\'SW_KEY_PWR\',\'SW_KEY_VM\',\'SW_KEY_VP\',\'SW_RST\'] if k in m))"],\n'
                '        r"(SW_BOOT→\\S+ · SW_KEY_PWR→\\S+ · SW_KEY_VM→\\S+ · SW_KEY_VP→\\S+ · SW_RST→\\S+)"),',
                '         "bs=lambda x:x[:-2] if x.endswith(\'_\'+chr(49)) else x;"\n'
                '         "inv={bs(r[\'ref\']):r[\'ref\'] for r in csv.DictReader(open(\'HW/netlist_v1.csv\')) if r.get(\'ref\')};"\n'
                '         "m={k:r[\'net\'] for r in rs if r[\'pin\']==\'1\' for k in [bs(r[\'ref\'])] "\n'
                '         "if k in (\'SW_BOOT\',\'SW_KEY_PWR\',\'SW_KEY_VM\',\'SW_KEY_VP\',\'SW_RST\')};"\n'
                '         "print(\' · \'.join(\'%s→%s\'%(inv.get(k,k),m[k]) for k in "\n'
                '         "[\'SW_BOOT\',\'SW_KEY_PWR\',\'SW_KEY_VM\',\'SW_KEY_VP\',\'SW_RST\'] if k in m))"],\n'
                '        r"(SW_BOOT(?:_\\d+)?→\\S+ · SW_KEY_PWR(?:_\\d+)?→\\S+ · SW_KEY_VM(?:_\\d+)?→\\S+'
                ' · SW_KEY_VP(?:_\\d+)?→\\S+ · SW_RST(?:_\\d+)?→\\S+)"),')
    n += 1
    return txt, n


def main():
    if os.path.isdir(FIX):
        shutil.rmtree(FIX)
    shutil.copytree(S4, FIX, symlinks=True)
    os.makedirs(os.path.join(FIX, "tmp"), exist_ok=True)

    A("=" * 92)
    A("ISS-321 · F-2「改名无关」改法验证 (★沙盒副本改闸·真闸零改★)")
    A("=" * 92)

    src = os.path.join(PROJ, "SW", "tools", "check_onepass_sw_sync.py")
    dst = os.path.join(FIX, "SW", "tools", "check_onepass_sw_sync.py")
    if os.path.lexists(dst):
        os.remove(dst)
    txt = open(src, encoding="utf-8").read()
    txt, n = apply_f2(txt)
    open(dst, "w", encoding="utf-8").write(txt)
    A("  ★改 %d 处 (★SW03/SW04/SW05 三条探针·全部改成【从网表实读】·不写死任何改名后名★)" % n)

    p = subprocess.run([sys.executable, dst], cwd=FIX, capture_output=True, text=True,
                       timeout=600)
    out = (p.stdout or "") + (p.stderr or "")
    A("  ★沙盒实跑 `check_onepass_sw_sync.py` (S4 盘面: 改名+台账+锚点全齐) ⇒ rc=%s" % p.returncode)
    for ln in out.splitlines():
        if "❌" in ln or "FAIL" in ln or ln.strip().startswith("rc="):
            A("      %s" % ln[:210])
    f2_rc = p.returncode

    A("")
    A("── 逐条探针读数 (★从输出里逐条抽★) ──")
    for pid in ("SW01_PCB_MD5", "SW03_LAND8_DNP", "SW04_CHG_LED_REF",
                "SW05_KEY_NETNAMES", "SW06_TP_INT", "SW08_ESD_USB_D"):
        mm = re.search(r"❌ %s[^\n]*" % pid, out)
        A("   %-20s %s" % (pid, (mm.group(0)[:150] if mm else "★绿 (无红项)★")))

    A("")
    A("── 汇总 ──")
    A("   F-2 改名无关版 (S4 盘面) : rc=%s" % f2_rc)
    A("   ★对比: 改前 (S4 原闸) rc=1 · 残留红 = SW01(板md5·改数据) + SW08(HW 跨域)")
    A("★★真闸 `SW/tools/*.py` 一个字节都没改 ★★")
    A("=" * 92)

    open(LOG, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n★写出: logs/iss321/06_f2_rename_agnostic_raw.txt")


if __name__ == "__main__":
    main()
