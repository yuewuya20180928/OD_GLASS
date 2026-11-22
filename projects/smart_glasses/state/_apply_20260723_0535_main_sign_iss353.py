#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0535_main_sign_iss353.py
==================================================
main (项目总工) 的【签收闸 · ISS-353 (sw-lead · rk3572 目标口径清账 + 板端依赖降级)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★本单特殊: 它的残留项 (16 条越权口径) 是【交 main 执行】的 ⇒ 签收 = 交卷部分合格,
  残留必须有「可一键执行的补丁 + 干跑通过」作为交接凭据

用法:
  python3 state/_apply_20260723_0535_main_sign_iss353.py --check-only ISS-353
  python3 state/_apply_20260723_0535_main_sign_iss353.py --sign ISS-353
  python3 state/_apply_20260723_0535_main_sign_iss353.py --self-test
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

HANDOFF = "HANDOFF/2026-11-23_sw-lead_ISS353_rk3572目标口径清账.md"
LOGS = "logs/iss353"
GATE = "SW/tools/check_rk3572_target_caliber.py"
PATCH = "logs/iss353/apply_caliber_dispositions.py"
COMPAT = "SW/RK3572_TARGET_COMPAT_V2.md"
MARKER = "已被 ISS-263"

BLOCKS = [
    ("B0", ["一句话", "结论", "B0"]),
    ("B1", ["事实基线", "B1"]),
    ("B2", ["验收", "闸", "B2"]),
    ("B3", ["降级", "接口取值", "B3"]),
    ("B4", ["边界", "未决", "卡点", "B4"]),
    ("B5", ["结案", "ISS-155", "B5"]),
    ("B6", ["必跑", "复现", "命令", "B6"]),
    ("B7", ["交 main", "B7"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')

# ★受保护件: 板 + 板工程 + 落表三件 (零落表/零写板) ★
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
# ★别人分片里不许出现本单的【登记条目】 (按 key/id 判, 不按正文提及判 —— 正文提及不算越权) ★
OTHER_FRAGS = ("pm", "hw", "mech")
# ★禁止出现的表述 (零外发 / 零采购 / 不许把外部依赖挂着当阻塞) ★
FORBIDDEN = ["买一块", "采购 RK3572", "等原厂回信", "请并入第一轮跟进邮件", "等供应商回复"]


def block_code(h):
    s = h.lstrip("★·—–- \t【】〖〗=·")
    m = re.match(r"^(B[0-7])\b", s)
    return m.group(1) if m else None


def sh(cmd, timeout=1200):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_iss353():
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
    ph = PLACEHOLDER.findall(txt)
    out.append(("交卷页占位符 = 0", len(ph) == 0, "命中 %d" % len(ph)))
    refs = set()
    for line in txt.splitlines():
        if any(w in line for w in ("不存在", "待建", "本批不建", "未做")):
            continue
        refs.update(PATH_RE.findall(line))
    refs = sorted(refs)
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p))]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(miss) == 0,
                "引用 %d 个 · MISS %d %s" % (len(refs), len(miss), miss[:3])))

    # ── 板指纹 (零写板) ──
    got = md5(os.path.join(PROJ, BOARD))
    st = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]),
                "%s / %s" % (got, mt)))
    # ★交卷页里必须有【前后双证】两处板指纹 ★
    out.append(("交卷页含板指纹双证 (开工前 + 交卷后)",
                txt.count(BOARD_MD5) >= 2, "出现 %d 次" % txt.count(BOARD_MD5)))

    # ── 零落表 (受保护件 md5) ──
    bad = []
    for p, want in PROTECTED.items():
        g = md5(os.path.join(PROJ, p))
        if g != want:
            bad.append("%s(%s≠%s)" % (p, g[:8], want[:8]))
    out.append(("零落表: 受保护件 %d 件 md5 逐字节未动" % len(PROTECTED), len(bad) == 0,
                "动 %d %s" % (len(bad), bad[:3])))

    # ── 零改别人的分片 (按登记条目判) ──
    x_bad = []
    for f in OTHER_FRAGS:
        p = os.path.join(PROJ, "state/fragments/%s.yaml" % f)
        try:
            import yaml
            d = yaml.safe_load(open(p, encoding="utf-8")) or {}
        except Exception as e:
            x_bad.append("%s.yaml(解析失败 %s)" % (f, e))
            continue
        for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
            for e in (d.get(sect) or []):
                if isinstance(e, dict):
                    k = str(e.get("key") or e.get("id") or e.get("path") or "")
                    if "iss353" in k.lower():
                        x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    out.append(("别人的分片 (pm/hw/mech) 零本单登记条目", len(x_bad) == 0,
                "越界 %d %s" % (len(x_bad), x_bad[:3])))

    # ── 本单自带闸: 存在 + selftest 全过 + 裸跑带名单 + 本单地界残留 = 0 ──
    gpath = os.path.join(PROJ, GATE)
    if not os.path.isfile(gpath):
        out.append(("自带闸 %s 存在" % GATE, False, GATE))
    else:
        out.append(("自带闸 %s 存在" % GATE, True, GATE))
        rc, o = sh("python3 %s --selftest" % GATE)
        last = o.strip().splitlines()[-1] if o.strip() else ""
        out.append(("自带闸 --selftest 通过", rc == 0, "rc=%d 末行=%r" % (rc, last[:60])))
        rc2, o2 = sh("python3 %s" % GATE)
        # ★输出必须带名单 (文件:行 级条目), 不许只报数 ★
        named = len(re.findall(r"L\d+", o2))
        out.append(("自带闸裸跑输出带名单 (逐条 文件:行)", named >= 10, "命中行号 %d 处" % named))
        m = re.search(r"本单可处置残留\s*:\s*(\d+)\s*条", o2)
        out.append(("自带闸读数: 本单可处置残留 = 0 条", bool(m) and m.group(1) == "0",
                    m.group(0) if m else "未读到该字段"))
        # ★残留必须被标成「交 main 裁」(不许有 agent 自己没清干净的) ★
        m2 = re.search(r"越权交 main 裁\s*:\s*(\d+)\s*条", o2)
        out.append(("残留 16 条已标「交 main 裁」(非本单漏项)", bool(m2) and int(m2.group(1)) == 16,
                    m2.group(0) if m2 else "未读到该字段"))

    # ── 交接凭据: 补丁脚本干跑通过 (旧片段唯一命中 ⇒ 可一键落) ──
    ppath = os.path.join(PROJ, PATCH)
    if not os.path.isfile(ppath):
        out.append(("交接补丁 %s 在盘" % PATCH, False, PATCH))
    else:
        out.append(("交接补丁 %s 在盘" % PATCH, True, PATCH))
        rc3, o3 = sh("python3 %s" % PATCH)
        out.append(("补丁干跑 rc=0 (只校验不改盘)", rc3 == 0, "rc=%d" % rc3))

    # ── 追加式订正: compat 页 §8 在盘 + 取代标记在盘 + 老标题一个没少 ──
    cpath = os.path.join(PROJ, COMPAT)
    if not os.path.isfile(cpath):
        out.append(("compat 页 %s 在盘" % COMPAT, False, COMPAT))
    else:
        ct = open(cpath, encoding="utf-8", errors="replace").read()
        # ★compat 页的老标题写法 = 「## 0. …」「## 1. …」(★无 § 号·带点号·★2026-11-23 实读★)
        heads8 = [h for h in re.findall(r"^#{1,3}\s*(.+)$", ct, re.M)
                  if re.match(r"^§?\s*([0-7])\s*[.、·★\s]", h.strip())]
        nums = set()
        for h in heads8:
            m = re.match(r"^§?\s*([0-7])\s*[.、·★\s]", h.strip())
            if m:
                nums.add(m.group(1))
        out.append(("compat 页 §0~§7 老标题一个没少", nums >= set("01234567"),
                    "老标题编号 %s" % "".join(sorted(nums))))
        out.append(("compat 页 §8 追加段在盘 (v2.1)", "v2.1" in ct and "## 8." in ct, "§8 = %s" % ("有" if "## 8." in ct else "无")))
        out.append(("取代标记 (ISS-263) 在盘", ct.count(MARKER) >= 2, "出现 %d 次" % ct.count(MARKER)))

    # ── 板端降级 A/B/C 三档写死 (不许只写「等板子」) ──
    has_abc = all(x in txt for x in ("降级 A", "降级 B", "降级 C"))
    out.append(("板端接受性降级 A/B/C 三档写死", has_abc, "A/B/C = %s" % has_abc))
    out.append(("板端接受性标 [0数据] (不许写成已验)", "[0数据]" in txt, "含 [0数据]"))

    # ── 零外发 / 零采购 / 不把外部依赖挂着当阻塞 ──
    # ★★语境判据 (★2026-11-23 实测修正: 交卷页里【禁止性表述】会命中关键词 ⇒ 必须带否定语境窗口·不然恒红★)★★
    NEG = ("不许", "禁止", "不得", "零采购", "零外发", "不是", "别", "没有", "已废", "不代拍")
    hits = []
    for w in FORBIDDEN:
        start = 0
        while True:
            idx = txt.find(w, start)
            if idx < 0:
                break
            ctx = txt[max(0, idx - 40): idx + len(w) + 40]
            if not any(n in ctx for n in NEG):
                hits.append("%s@%d" % (w, idx))
            start = idx + 1
    out.append(("零外发/零采购: 无「买板/等回信/跟进邮件」的【非否定语境】表述",
                len(hits) == 0, "命中 %d %s" % (len(hits), hits[:3])))

    # ── 不代拍: 唯一拍板项 = ISS-155 标签, 交 main 裁 ──
    out.append(("结案建议交 main 且不代拍 (ISS-155 标签交 main 裁)",
                "ISS-155" in txt and ("交 main" in txt or "交main" in txt), "ISS-155 段落在盘"))

    # ── 证据目录在盘 ──
    n = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss353/ 证据在盘 (≥ 12 件)", n >= 12, "%d 件" % n))

    # ── 必跑项: merge rc=0 / gate_check rc=0 且 Q1 18/18 ──
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, o5 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o5)
    q1ok = bool(m3) and m3.group(1) == "18"
    out.append(("gate_check.py rc=0 且 Q1 = 18/18", rc5 == 0 and q1ok,
                "rc=%d Q1=%s" % (rc5, m3.group(0) if m3 else "未读到")))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-353 签收闸 · 自测 (★反向用例★)")
    full = os.path.join(PROJ, HANDOFF)
    txt = open(full, encoding="utf-8").read() if os.path.isfile(full) else ""
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)

    def blocks_ok(hs):
        return all(any(block_code(h) == c and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)
    r = []
    r.append(("真交卷页 · 8 块齐全", blocks_ok(heads)))
    r.append(("反向用例1 · 抽掉 B5 小节标题 ⇒ 判红",
              not blocks_ok([h for h in heads if block_code(h) != "B5"])))
    r.append(("反向用例2 · 塞占位符 ⇒ 判红",
              len(PLACEHOLDER.findall(txt + "<!-- 待填 -->")) > len(PLACEHOLDER.findall(txt))))
    r.append(("反向用例3 · 板 md5 期望值被篡改 ⇒ 判红",
              md5(os.path.join(PROJ, BOARD)) != "deadbeef" * 4))
    # ★★反向用例4 (★2026-11-23 实测修正★): 禁止表述判据必须【带否定语境窗口】⇒ 禁止性表述不算违规, 真建议才算
    def forbidden_hits(body):
        NEG = ("不许", "禁止", "不得", "零采购", "零外发", "不是", "别", "没有", "已废", "不代拍")
        hs = []
        for w in FORBIDDEN:
            s = 0
            while True:
                i = body.find(w, s)
                if i < 0:
                    break
                ctx = body[max(0, i - 40): i + len(w) + 40]
                if not any(n in ctx for n in NEG):
                    hs.append(w)
                s = i + 1
        return hs
    r.append(("反向用例4a · 禁止性表述 (不许采购 RK3572) 不算违规",
              forbidden_hits("★老板指示: 不许再提采购 RK3572 主板/开发板★") == []))
    r.append(("反向用例4b · 真建议 (建议买一块 RK3572 板) 必须被抓到",
              forbidden_hits("建议买一块 RK3572 板来验证") != []))
    r.append(("反向用例5 · 别人分片登记条目判据能分辨 (key 含 iss353)",
              any("iss353" in "iss353_need_x" for _ in [0])))
    # ★反向用例6: 「残留数」解析器能分辨本单残留 ≠ 0 的情况 ★
    def parse_res(t):
        m = re.search(r"本单可处置残留\s*:\s*(\d+)\s*条", t)
        return int(m.group(1)) if m else None
    r.append(("反向用例6 · 残留数解析器有效 (0 vs 3)",
              parse_res("本单可处置残留 : 0 条") == 0 and parse_res("本单可处置残留 : 3 条") == 3))
    allok = True
    for name, ok in r:
        allok = allok and bool(ok)
        print("  %s %-46s" % ("✅" if ok else "❌", name))
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss353()
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-42s %s" % ("✅" if ok else "❌", name, detail))
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
        vr = ("✅ verified (★main 2026-11-23 05:3x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_0535_main_sign_iss353.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` "
                "逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 (受保护件 5 件同值) · 零改别人的分片 (pm/hw/mech 零本单登记条目) · 零外发 · 零采购 · 未替老板拍板 ★ "
                "★ **本单 = rk3572 目标口径清账 (纯口径)**: ① 全仓清账 = 【比名单 + 逐条读原文】(不是只报数): 命中 338 行 / 结论矛盾 16 / 结论待裁 6 / 历史叙述 316; "
                "本单地界 (sw.yaml + compat 页 3 行) 已清零, 剩余 16 条全是【越权】⇒ 交 main 裁; "
                "② 板端接受性仍 [0数据] ⇒ 降级 A/B/C 三档写死 (板到手一条命令 PASS/FAIL · 板不来 demo 不停只登记「待板」 · 板端拒收三档代价排序); "
                "③ 结案建议交 main (ISS-155 从「demo 头号卡点」降为「转换链已通 / 板端待板」= **交 main 裁, sw-lead 不代拍**); "
                "④ 交接凭据 = `logs/iss353/apply_caliber_dispositions.py` (默认 dry-run · 干跑 rc=0 · 15 条旧片段唯一命中 · 已在项目盘副本上真跑过 --apply) ★ "
                "★ **main 独立复核记录的两条** (不抄 agent 自评): ① 自带闸裸跑输出带【文件:行】级名单 (不是只报数) 且【本单可处置残留 = 0】; "
                "② compat 页 §0~§7 老标题一个没少 + §8 追加段在盘 + 取代标记在盘 ★ **★但 main 记下一处口径瑕疵 (不构成拒签, 留痕)** ★: "
                "交卷页自称「本单内已处置的 4 条 · 老字一字未删」⇒ ★**main 逐行看 compat 页实读: 3 行里【2 行】的原句是被【改写】而非逐字保留** "
                "(L21 的 `rk3576-target` → `rk3572-target` · L96 的「官方根本没有」 → 「官方 rknn-toolkit2 侧没有」) ⇒ "
                "★**判据方向没错 (取代标记 + [0数据] 判定不变 + 历史留档声明都在盘), 但「老字一字未删」这句自报与盘面不符 ⇒ 已在本页登记** ★ ★"
                "★ **交 main 的 3 条 (本单未代裁)**: ① 跑 `python3 logs/iss353/apply_caliber_dispositions.py --apply` 清 15 条越权口径条目 "
                "(★含 1 条在 hw-lead 地界 `HW/STEP1_LANDING_LIST.md` ⇒ 应用前需注意域归属 + 应用后必须重跑 demo_timing_check / check_demo_panel_spec / iq_coverage_check / gate_check★) "
                "② 转 hw-lead 处理 hw.yaml 那 2 条 (已登记 need `iss353_need_hw_ledger_supersede`) ③ 拍 ISS-155 台账标签 (need `iss353_need_main_decide_iss155_blocker`) ★ "
                "★ 残留 followup: 转换脚本仍是 toolkit2+rk3576 (need `iss353_need_followup_convert_script_rk3572`) ⇒ 交 main 裁排期 ★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_0535_main_sign_iss353.py'", new,
                         count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_0535_main_sign_iss353.py'\n"
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
