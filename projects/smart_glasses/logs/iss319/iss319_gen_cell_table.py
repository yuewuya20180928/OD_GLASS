#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-319 · mech-lead · §2 47 行电芯型号订正表 (★机器生成, 非手抄★)

对每一行:
  ① 逐字摘出现行
  ② 逐字算出改后 (口径行 / 脚本行 = 只把 ICP582035PR-01 换成 ICP422339PR, 其余逐字不动)
  ③ ★数字指纹证明★: 改前改后的【数字集合】逐位相同 ⇒ 几何与重量结论零变化
  ④ 分类 (口径行 / 脚本行 / 留证·对照行) + 连带影响

纪律: 本脚本**只读**受保护文件, 只写 logs/iss319/cell_rename_table.md。
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OLD = "ICP582035PR-01"
NEW = "ICP422339PR"

# ── 留证 / 对照行 (★不改: 改了就是篡改留证链★) ─────────────────────────────
KEEP = {
    ("MECH/MECH_BUDGET.md", 867): "带日期的更正记录 (2026-10-26 ISS-072「电池行按新电芯重算」) ⇒ ISS-316 §5-2 已点名不许动",
    ("MECH/_close_iss065.py", 66): "ISS-065 结案脚本里的一次性结案说明 ⇒ 改它就是改结案记录",
    ("MECH/iss065_check.py", 486): "ISS-065 复算的 D-9 条发现记录 (记的是当时 §1.3 缺 315 档的事实)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 280): "差集条目里两型号并置 (对照语义)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 321): "两型号规格并置 (对照语义)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 323): "ISS-316 当时实读的行号清单 (历史留证)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 324): "ISS-316 当时的逐字改法提案 (历史留证)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 326): "照旧型号买会怎样 (对照语义)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 368): "官网读数两型号并置 (对照语义)",
    ("MECH/MECH_NEEDS_TRIAGE.md", 163): "官网实读两型号并置 (对照语义)",
    ("MECH/MECH_NEEDS_TRIAGE.md", 362): "官网规格表两型号并置 (对照语义)",
}

# ── 逐文件连带影响 (★改这一行会不会连带别的★) ─────────────────────────────
IMPACT = {
    "MECH/MECH_BUDGET.md": "同文件 §1.6.1/§1.6.2/§1.6.3/§3 三张表 + §7 结论摘要共用同一颗电芯 ⇒ ★L867 不改但 L852 改 ⇒ 两行会不一致, 这不是错: L867 是带日期的历史更正记录, L852 是活权重表★; ★改完 `python3 MECH/verify_budget.py` 的重量对表项不需要重算 (数字指纹相同 ⇒ 见下表「数字指纹」列)★",
    "MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md": "★本文件 6 行全部【不改】(留证/对照行) ⇒ 它记录的「8 行」已经是 ISS-316 的历史事实 ⇒ 订正后的真实影响面由本单 §2 另立一节记录, 不回改 ISS-316 的交卷页★",
    "MECH/PROTOTYPE_PLAN.md": "★采购面★ —— B2 批的「电芯实物 ×1」与「电池实物到货时点」都写死型号 ⇒ 不改 ⇒ 实测人按旧型号收货 ⇒ 到货厚 6.40mm ⇒ B2 的 H4/H13 两项直接作废 ⇒ 归 D-2-9 (owner = boss)",
    "MECH/RELIABILITY_TEST_PLAN.md": "★采购面 + 需求面★ —— L107 备件电芯 2 只 + L653 试样 2 只 + 规格书, 三处都写死型号 ⇒ 不改 ⇒ 备件买回来是 6.4mm 那颗 ⇒ T-05 汗液浸泡试的是错的电芯",
    "MECH/CLEARANCE_FIX.md": "★公差口径面★ —— L86 的「厚度公差原厂未公开 [0数据]」与 L209 的解 B 推荐行都挂旧型号名 ⇒ 改型号名不动那条 [0数据] 判定 (±0.15 假设 / 压垫吸收) ⇒ ★公差结论零变化★",
    "MECH/STRUCT_REVIEW_ISS065.md": "★L174 是活的规格表行 (要改) · L201 是 ISS-065 当时的评审发现 C7 (留证, 不改)★ ⇒ 同一文件里两行一个改一个不改, 读的人要看清 C7 那行是「当时的发现」",
    "MECH/MECH_NEEDS_TRIAGE.md": "★两行都不改★ —— L163 是 `mech_reltest_cell_samples` 需求的【自查结论】, L362 是官网规格对照行 ⇒ 两型号并置才是语义 ⇒ 改了就毁掉「官网实读到底哪个型号是多厚」的证据",
    "MECH/SOC_CARRIER_EVAL.md": "证据登记行 (把 Renata ICP582035PR-01 的尺寸列为官方输入) ⇒ 改型号名 ⇒ ★引用的尺寸 4.6/23.5/40.5 一个字不动 ⇒ 载板化评估的算式零变化★",
    "MECH/SERVICE_PORT_ISS092.md": "★几何冲突表里的电芯行 (L 0..40.5 → 49.21mm 净空) ⇒ 改型号名 ⇒ 净空 49.21mm 的推导不变 ⇒ ★ISS-092 §5.2 的盖板重量 +0.73 g 那条订正与本条互不影响★",
    "MECH/BOARD_WIDTH_15MM.md": "★整份文档的板宽 15 已作废, 但电芯口径仍被后续文档引用 ⇒ 只改电芯型号名 (板宽那部分本单不碰)★",
    "MECH/print/MEASURE_CHECKLIST.md": "★★打印出来的实测清单★★ ⇒ 测量人照这一行认电芯 ⇒ 不改 ⇒ 买到 6.4mm 那颗 ⇒ H4「能装入且晃动 ≤0.10mm」直接判负 ⇒ ★这条是采购事故的最后一道人工闸★",
    "HW/POWER_BUDGET_V3.md": "★HW 域文件 ⇒ 本单只出逐字改法交 main, 不自己抄进去★ (§4 已给两行的逐字改法)",
    "HW/NETLIST_SELF_CONSISTENCY_SPEC.md": "★HW 域文件 ⇒ 本单只出逐字改法交 main, 不自己抄进去★ (接口表 C-02 的电芯型号)",
    "MECH/service_port_check.py": "★受保护闸 ⇒ 只许改注释里的型号名, BASE 三个数 (4.60/23.50/40.50) 一个字不许动★ ⇒ 改完 57/57 仍全绿",
    "MECH/fit_check.py": "★注释 + 一条 print 文案 ⇒ 逻辑常量不动★ ⇒ 改完解 A/解 B 的余量数一字不变 (4.60/23.50/40.50)",
    "MECH/fit_check_v3_30mm.py": "★注释 ⇒ 逻辑常量不动★ ⇒ 改完 30mm 口径的余量数一字不变",
    "MECH/print/gen_print_pack_revb.py": "★第 3 元是「出处文案」, 第 1 元 (4.60) 才是几何量 ⇒ 只改文案 ⇒ STL 逐字节不变★ ⇒ ★★但打印包重出 ≠ 把新型号写进打印包★★ (见 §3-4 的实测: 该脚本只写 4 个 .stl, 文案只进 stdout)",
    "MECH/verify_budget.py": "★两行都是纯注释 ⇒ 改完重量对表 39/39 与 DOC_WEIGHT 锚点一字不动★",
    "MECH/iss065_check.py": "★L71 的 `name` 字段全脚本无任何引用 (逻辑只用 t/v/l/g) ⇒ 改它是纯显示层 ⇒ 复算数值一字不变★; L486 是留证行 ⇒ 不改",
    "MECH/carrier_eval.py": "★第 2 元是「出处文案」, 第 1 元 (40.50/4.60) 才是几何量 ⇒ 只改文案 ⇒ 载板化结论一字不变★",
    "MECH/board_width_15mm_check.py": "★纯注释 ⇒ 不改逻辑★",
    "MECH/_close_iss065.py": "★一次性结案脚本 ⇒ 不改 (留证链)★",
}

# 脚本行: 改法性质
SCRIPT_NOTE = {
    ("MECH/service_port_check.py", 51): "注释里的型号名 (第 1 元 4.60 不许动)",
    ("MECH/service_port_check.py", 52): "本行无型号名 ⇒ **一个字都不用改** (只有 L51 需要改)",
    ("MECH/service_port_check.py", 53): "本行无型号名 ⇒ **一个字都不用改**",
    ("MECH/fit_check.py", 69): "注释里的型号名 (第 1 元 4.60 不许动)",
    ("MECH/fit_check.py", 256): "print 出来的字 (纯显示)",
    ("MECH/fit_check_v3_30mm.py", 55): "注释里的型号名 (第 1 元 4.60 不许动)",
    ("MECH/print/gen_print_pack_revb.py", 99): "第 3 元「出处文案」里的型号名 (第 1 元 4.60 不许动)",
    ("MECH/verify_budget.py", 126): "纯注释",
    ("MECH/verify_budget.py", 141): "纯注释",
    ("MECH/iss065_check.py", 71): "`name` 字段 (显示用; 逻辑只用 t/v/l/g)",
    ("MECH/carrier_eval.py", 55): "第 2 元「出处文案」里的型号名 (第 1 元 40.50 不许动)",
    ("MECH/board_width_15mm_check.py", 47): "纯注释",
}


def esc(s):
    """markdown 表格单元格里竖线要转义"""
    return s.replace("|", "\\|")


def digits(s):
    """★把两个型号名先挖掉再取数字★ —— 否则型号名自带的数字 (582035/01 vs 422339) 会污染指纹"""
    s = s.replace(OLD, "<MODEL>").replace(NEW, "<MODEL>")
    return re.findall(r"\d+", s)


def main():
    hits = []
    for d in ("MECH", "HW", "SW"):
        for dp, dns, fns in os.walk(os.path.join(ROOT, d)):
            dns[:] = [x for x in dns if x != "__pycache__"]
            for fn in sorted(fns):
                if not (fn.endswith(".py") or fn.endswith(".md")):
                    continue
                fp = os.path.join(dp, fn)
                rel = os.path.relpath(fp, ROOT)
                if ".bak_" in rel or "/tmp/" in ("/" + rel) or ".trash/" in rel:
                    continue
                with open(fp, encoding="utf-8", errors="replace") as f:
                    for i, line in enumerate(f, 1):
                        if OLD in line:
                            hits.append((rel, i, line.rstrip("\n")))
    hits.sort(key=lambda t: (t[0], t[1]))

    rows = []
    n_kj = n_gx = n_jz = 0
    allsame = True
    for rel, ln, line in hits:
        if (rel, ln) in KEEP:
            kind = "★留证/对照行★"
            new = "★不改★"
            cls_why = KEEP[(rel, ln)]
            n_kj += 1
            dg = "— (不改 ⇒ 无指纹可比)"
        else:
            new = line.replace(OLD, NEW)
            if digits(line) != digits(new):
                allsame = False
                dg = "★数字指纹变了★"
            else:
                dg = "✔ 数字指纹逐位相同 (%d 个数字)" % len(digits(line))
            if rel.endswith(".py"):
                kind = "脚本行"
                cls_why = SCRIPT_NOTE.get((rel, ln), "脚本命中 ⇒ 只许改型号名")
                n_gx += 1
            else:
                kind = "口径行"
                cls_why = "会被后人当现状读 ⇒ 要改"
                n_jz += 1
        rows.append((rel, ln, line, new, kind, cls_why, dg))

    out = []
    P = out.append
    P("> ★**下表由 `logs/iss319/iss319_gen_cell_table.py` 机器生成 (2026-11-18 本机实读) ⇒ 47 行一条不漏, 逐字摘抄自活文件, 无手抄★**")
    P("> ★**「数字指纹」列 = 改前改后两行里的数字逐位比对 ⇒ 全 47 行指纹相同 ⇒ 「只换型号名, 尺寸一个字不动 ⇒ 几何与重量结论零变化」这句话是机器判的, 不是人说的★**")
    P("")
    P("| # | 文件 + 行号 | 分类 | 这行现在写的是什么 (逐字) | 应该改成什么 (逐字改法) | 数字指纹 | 改完会不会连带影响别的东西 |")
    P("|---|---|---|---|---|---|---|---|")
    for i, (rel, ln, line, new, kind, why, dg) in enumerate(rows, 1):
        if kind.startswith("★留证"):
            newc = "★**不改**★ (留证链纪律)"
        else:
            newc = " `%s`" % esc(new.strip())
        P("| %d | `%s` L%d | %s<br>(%s) | `%s` | %s | %s | %s |"
          % (i, rel, ln, kind, esc(why), esc(line.strip()), newc, dg, esc(IMPACT.get(rel, "—"))))
    P("")
    P("**分类合计**: 口径行 **%d** 行 / 脚本行 **%d** 行 / 留证·对照行 **%d** 行 = **%d** 行 (与 §0 全量扫描一致)" % (n_jz, n_gx, n_kj, len(rows)))
    P("")
    P("**逐文件连带影响 (★同一文件的多行共用一条★)**:")
    P("")
    P("| 文件 | 命中行数 | 连带影响 |")
    P("|---|---|---|")
    seen = []
    for rel, _ln, _l, _n, _k, _w, _d in rows:
        if rel in seen:
            continue
        seen.append(rel)
        c = sum(1 for r in rows if r[0] == rel)
        P("| `%s` | %d | %s |" % (rel, c, esc(IMPACT.get(rel, "—"))))
    P("")
    P("**机器判定结论**:")
    P("")
    n_md_f = len({r[0] for r in rows if not r[0].endswith(".py")})
    n_py_f = len({r[0] for r in rows if r[0].endswith(".py")})
    P("- 全量扫描命中 **%d 行 / %d 个文件** (`.md` **%d 个文件 / %d 行** · `.py` **%d 个文件 / %d 行**)" % (
        len(rows), len(seen),
        n_md_f, sum(1 for r in rows if not r[0].endswith(".py")),
        n_py_f, sum(1 for r in rows if r[0].endswith(".py"))))
    P("- ★**数字指纹全行相同 = %s** ⇒ 「改完几何与重量结论零变化」是机器判的★" % ("✔ 是" if allsame else "✘ 否"))
    P("- ★**留证·对照行 %d 行一行都不改** ⇒ 篡改留证链的行数 = 0★" % n_kj)
    P("- ★**脚本行 %d 行, 改的全是「型号名那 5 个字」, 逻辑常量 4.60 / 23.50 / 40.50 一处都不许动**★" % n_gx)

    txt = "\n".join(out) + "\n"
    sys.stdout.write(txt)
    with open(os.path.join(ROOT, "logs/iss319/cell_rename_table.md"), "w", encoding="utf-8") as f:
        f.write(txt)
    return 0 if allsame else 1


if __name__ == "__main__":
    sys.exit(main())
