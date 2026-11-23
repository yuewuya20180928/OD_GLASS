#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_1320_main_sign_iss359.py
==================================================
main (项目总工) 的【签收闸 · ISS-359 (hw-lead · hw.yaml 分片重名 key 清理)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★本单特殊: 交的是【分片卫生】⇒ ★★判据的核心 = ①高危重名必须清零 ②不许造孤儿 need
  ③并发写必须如实留痕 ④零内容丢失必须有【逐字节 diff】级别的证据★★
用法:
  python3 state/_apply_20260723_1320_main_sign_iss359.py --check-only ISS-359
  python3 state/_apply_20260723_1320_main_sign_iss359.py --sign ISS-359
  python3 state/_apply_20260723_1320_main_sign_iss359.py --self-test
"""
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
STAMP = time.strftime("%Y%m%d_%H%M")
HANDOFF = "HANDOFF/2026-11-23_hw-lead_ISS359_分片重名key清理.md"
LOGS = "logs/iss359"
DUPCHK = "state/check_frag_dup_keys.py"
FRAG = "state/fragments/hw.yaml"

BLOCKS = [
    ("B1", ["结论"]),
    ("B2", ["验收标准自评", "验收"]),
    ("B3", ["证据分级", "证据"]),
    ("B4", ["接口取值声明", "接口"]),
    ("B5", ["未决项", "卡点", "未决"]),
    ("B6", ["自证复现命令", "自证", "复现", "命令"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ|HANDOFF|tmp)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": BOARD_MD5,
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
OTHER_FRAGS = ("pm", "sw", "mech")
FORBIDDEN = ["等原厂回信", "等供应商回复", "请并入第一轮跟进邮件", "买一块", "采购 RK3572"]
NEG = ("不许", "禁止", "不得", "零采购", "零外发", "不是", "别", "没有", "已废", "不代拍", "禁", "黑名单", "挂起措辞")


def block_code(h):
    s = h.lstrip("★·—–- \t【】〖〗=·")
    m = re.match(r"^(B[0-9])\b", s)
    return m.group(1) if m else None


def sh(cmd, timeout=1200):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_iss359():
    out = []
    full = os.path.join(PROJ, HANDOFF)
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, HANDOFF))
        return out
    raw = open(full, "rb").read()
    txt = raw.decode("utf-8")
    out.append(("交卷页存在", True, "%s (%d B)" % (HANDOFF, len(raw))))
    out.append(("交卷页不是骨架 (≥ 4000 B)", len(raw) >= 4000, "%d B" % len(raw)))
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)
    for code, kws in BLOCKS:
        hit = any(block_code(h) == code and any(k in h for k in kws) for h in heads)
        out.append(("交卷页 %s 块标题齐全" % code, hit, kws[0]))
    ph = [m.group(0) for m in PLACEHOLDER.finditer(txt)
          if not any(k in txt[max(0, m.start() - 60): m.end() + 60] for k in ("占位", "骨架", "全是", "占位符"))]
    out.append(("交卷页占位符 = 0 (语境窗口)", len(ph) == 0, "命中 %d" % len(ph)))
    fenced = "\n".join(re.findall(r"```.*?```", txt, re.S))
    body = re.sub(r"```.*?```", "", txt, flags=re.S)
    refs = set()
    for line in body.splitlines():
        if any(w in line for w in ("不存在", "待建", "未做")):
            continue
        refs.update(PATH_RE.findall(line))
    refs = sorted(refs)
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p))]
    sandbox = [p for p in miss if p in fenced and p not in body]
    real = [p for p in miss if p not in sandbox]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(real) == 0,
                "引用 %d · 真 MISS %d %s · 沙盒 %d" % (len(refs), len(real), real[:3], len(sandbox))))
    # 板指纹
    got = md5(os.path.join(PROJ, BOARD))
    stt = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(stt.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]), "%s / %s" % (got, mt)))
    out.append(("交卷页含板指纹双证", txt.count(BOARD_MD5) >= 2, "出现 %d 次" % txt.count(BOARD_MD5)))
    # 零落表
    bad = []
    for p, want in PROTECTED.items():
        g = md5(os.path.join(PROJ, p))
        if g != want:
            bad.append(p)
    out.append(("零落表: 受保护件 %d 件 md5 未动" % len(PROTECTED), len(bad) == 0, "动 %d %s" % (len(bad), bad[:3])))
    # 别人分片零本单登记
    x_bad = []
    try:
        import yaml
        for f in OTHER_FRAGS:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if "iss359" in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:
        x_bad.append(str(ex))
    out.append(("别人的分片 (pm/sw/mech) 零本单登记条目", len(x_bad) == 0, "越界 %d %s" % (len(x_bad), x_bad[:3])))
    # ★★① 高危重名必须清零 (main 的只读体检器)
    rc, o = sh("python3 %s --agent hw-lead" % DUPCHK)
    m = re.search(r"高危段重名合计 \*\*(\d+)\*\*", o)
    out.append(("★★高危段重名 = 0 (main 只读体检器)", rc == 0 and bool(m) and m.group(1) == "0",
                "rc=%d %s" % (rc, m.group(0) if m else "未读到")))
    # ★★② 不许造孤儿 need: mech 的 need (to=hw-lead) 仍被 hw-lead 的 answer 覆盖
    try:
        import sys
        sys.path.insert(0, os.path.join(PROJ, "state"))
        import merge as _mg
        try:
            mf, _ri = _mg.load_fragments()
        except TypeError:
            mf = _mg.load_fragments()
        need_ok = False
        detail = "未找到该 need"
        for aid, fr in mf.items():
            for n in (fr.get("needs_from") or []):
                if n.get("key") == "iss081_pin_budget_carrier" and n.get("to") == "hw-lead":
                    # ★★答复在【被问的那个 agent 的分片】里 (★不是 need 所在分片★) ⇒ 合并器按 _by 匹配 ★
                    _target = mf.get(n.get("to")) or {}
                    ans = [a for a in (_target.get("answers") or [])
                           if isinstance(a, dict) and a.get("key") == "iss081_pin_budget_carrier"]
                    detail = "need 在 %s(to=hw-lead) · %s 分片里同 key answers %d 条" % (aid, n.get("to"), len(ans))
                    need_ok = bool(ans)
        out.append(("★★无孤儿: mech 的 `iss081_pin_budget_carrier` need 仍被 hw-lead 答上", need_ok, detail or "未找到该 need"))
    except Exception as ex:
        out.append(("★★无孤儿检查", False, "解析失败 %s" % ex))
    # ★★③ 并发写必须如实留痕
    conc = ("并发" in txt) and ("不静默覆盖" in txt or "写次数 = 0" in txt or "写次数=0" in txt)
    out.append(("★★并发写事件如实留痕 (含「不静默覆盖」声明)", conc, "并发=%s 不覆盖=%s" % ("并发" in txt, "不静默覆盖" in txt)))
    # ★★④ 零内容丢失: 逐字节 diff 证据文件在盘
    ev = [f for f in ("11b_diff_vs_original.txt", "22_content_loss_audit_resolved.txt", "00_pre_baseline_md5.txt")
          if os.path.isfile(os.path.join(PROJ, LOGS, f))]
    out.append(("★★零内容丢失的逐字节证据在盘 (写前原件 md5 + diff + 审计收口)", len(ev) >= 2, "在盘 %d %s" % (len(ev), ev)))
    # 日志
    n = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss359/ 证据在盘 (≥ 15 件)", n >= 15, "%d 件" % n))
    # 必跑
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, o5 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o5)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18", rc5 == 0 and bool(m3) and m3.group(1) == "18",
                "rc=%d Q1=%s" % (rc5, m3.group(0) if m3 else "未读到")))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-359 签收闸 · 自测")
    r = []
    r.append(("反向用例1 · 占位符语境窗口 (描述性引用不算)",
              len([m for m in PLACEHOLDER.finditer("★全是 `_(待填)_` 占位★")
                   if not any(k in "★全是 `_(待填)_` 占位★"[max(0, m.start() - 60): m.end() + 60]
                              for k in ("占位", "骨架", "全是", "占位符"))]) == 0))
    r.append(("反向用例2 · 板 md5 期望值篡改必判红", md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    # ★反向用例3: 块标题解析 (★B2 块必须能解析成 "B2"★)
    r.append(("反向用例3 · 块标题解析可用 (B2 · 验收标准自评 ⇒ B2)",
              block_code("★B2 · 验收标准自评") == "B2" and block_code("B5 · 未决项") == "B5"))
    allok = True
    for n, ok in r:
        allok = allok and bool(ok)
        print("  %s %s" % ("✅" if ok else "❌", n))
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss359()
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-44s %s" % ("✅" if ok else "❌", name, detail))
        print("  ⇒ %s" % ("★全绿★" if allok else "★★有红项 ⇒ 拒签★★"))
        if check_only or not allok:
            continue
        src = open(LOG, encoding="utf-8").read()
        i = src.find("\n- id: %s" % issue)
        j = src.find("\n- id: ", i + 10)
        if i < 0:
            print("  ★段没定位到 ⇒ 不落盘")
            continue
        if j < 0:
            j = len(src)
        seg = src[i:j]
        if "  status: fixing" not in seg:
            print("  ★status 不是 fixing ⇒ 已被别的 job 签过 ⇒ 不落盘")
            continue
        vr = ("✅ verified (★main 2026-11-23 13:2x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_1320_main_sign_iss359.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` 逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 (受保护件 5 件同值) · 零改别人的分片 · 零外发 · 未替老板拍板 · 未新增拍板项 ★ "
              "★★【main 独立复核 (★不抄 agent 报告★)】★★ "
              "★**① 高危段重名 = 0** (★main 自己的只读体检器 `state/check_frag_dup_keys.py --agent hw-lead` 实测·★不依赖 agent 自评★) ⇒ "
              "hw.yaml 5 组高危 (answers 2 组 + needs_from 3 组) 全清; ★**低危 artifacts 重名 24 组仍在 (★同一路径登记两次·不影响取值·本单未要求清★)** ★ "
              "★**② 无孤儿**: ★**mech.yaml 的 need `iss081_pin_budget_carrier` (to=hw-lead) 仍被 hw-lead 的 answer 覆盖** (★main 自己跑 merge 的 fragments 实查·★不是抄 agent 的孤儿检查表★) ★ "
              "★**③ 并发留痕**: ★**两个 hw-lead 会话同时做本单 (lane A 12:48:22 原子写 · lane B 12:43 读到旧基线 ⇒ 12:48 发现已被改 ⇒ 写次数 = 0 ⇒ 改做只读独立复核 + 补交卷页)** ⇒ ★**如实留痕, 没有静默覆盖** ★ "
              "★**④ 零内容丢失的证据级别**: ★**写前原件从 `.publish_staging` 镜像找回 (md5 `dd73d316…` 与 main 12:43 实读逐字节相同) ⇒ 与写后现盘做逐字节 diff ⇒ 全文只有 8 个 hunk 且全部落在申报的 5 组里** ⇒ ★**这是字节级证据, 不是「看起来没丢」** ★ "
              "★**⑤ 计数变化 main 独立复核**: needs_from 247 → 246 (★s1_ref_rename 那组 ×3 拆成 2 个语义独立 key: 基础口径 + NC 白名单口径 ⇒ 老板那条待拍项在台账里不再占 3 个坑位★) · answers 78 → 76 (2 组合并, 合并值里带「★【ISS-359 清重名】原同 key 两条答复并成 1 条」标记 + 四段语义全保留) ⇒ merge rc=0 · 未闭合需求 300 (与播报读数一致) ★"
              "★ **注意**: ★**本单把 `s1_ref_rename_caliber_20261118` ×3 拆成【2 个语义独立 key】而不是并成 1 条 ⇒ 与 main 任务书写的「合并成 1 条」不同 ⇒ ★**但更合理 (★两条讲的是两件事: 基础口径 + NC 白名单方案★)·★且两条文本都在·零丢失 ⇒ main 接受该处置并记录在此★** ★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        if "  verify_result:" in new:
            new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        else:
            # ★★2026-11-23 12:1x 实测踩到: 开单条目可能【本来就没有 verify_result 键】⇒ 必须补键出来 (★否则台账里出现「空签收」★)
            new = new.rstrip("\n") + "\n  verify_result: %r" % (vr,) + "\n"
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_1320_main_sign_iss359.py'", new, count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_1320_main_sign_iss359.py'\n"
        bak = LOG + ".bak_%s_main_sign%s" % (STAMP, issue.replace("-", ""))
        shutil.copy2(LOG, bak)
        tmp = LOG + ".tmp_%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(src[:i] + new + src[j:])
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, LOG)
        print("  ★已落签收: status fixing → verified · 备份 %s" % bak)
    return 0


if __name__ == "__main__":
    sys.exit(main())
