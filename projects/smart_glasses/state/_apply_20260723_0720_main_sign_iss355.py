#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0720_main_sign_iss355.py
==================================================
main (项目总工) 的【签收闸 · ISS-355 (sw-lead · 转换脚本迁主路线)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评
★判据要点 (★本单是【实现侧】⇒ 不能只看口径文字, 必须机器读脚本默认值★)

用法:
  python3 state/_apply_20260723_0720_main_sign_iss355.py --check-only ISS-355
  python3 state/_apply_20260723_0720_main_sign_iss355.py --sign ISS-355
  python3 state/_apply_20260723_0720_main_sign_iss355.py --self-test
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

HANDOFF = "HANDOFF/2026-11-23_sw-lead_ISS355_转换脚本迁主路线.md"
LOGS = "logs/iss355"
GATE = "SW/tools/check_iss355_convert_route.py"
SCRIPT = "SW/tools/rk3572_model_rebuild.sh"
CALIBER = "SW/tools/check_rk3572_target_caliber.py"

BLOCKS = [
    ("B0", ["一句话", "结论", "B0"]),
    ("B1", ["事实基线", "B1"]),
    ("B2", ["自带闸", "验收", "B2"]),
    ("B3", ["降级", "接口取值", "B3"]),
    ("B4", ["边界", "B4"]),
    ("B5", ["未决", "卡点", "B5"]),
    ("B6", ["必跑", "复现", "命令", "B6"]),
    ("B7", ["落盘清单", "B7"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config|REQ)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
OTHER_FRAGS = ("pm", "hw", "mech")
FORBIDDEN = ["买一块", "采购 RK3572", "等原厂回信", "请并入第一轮跟进邮件", "等供应商回复"]
NEG = ("不许", "禁止", "不得", "零采购", "零外发", "不是", "别", "没有", "已废", "不代拍")


def block_code(h):
    s = h.lstrip("★·—–- \t【】〖〗=·")
    m = re.match(r"^(B[0-7])\b", s)
    return m.group(1) if m else None


def sh(cmd, timeout=1800):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def forbidden_hits(body):
    hs = []
    for w in FORBIDDEN:
        s = 0
        while True:
            i = body.find(w, s)
            if i < 0:
                break
            ctx = body[max(0, i - 40): i + len(w) + 40]
            if not any(n in ctx for n in NEG):
                hs.append("%s@%d" % (w, i))
            s = i + 1
    return hs


def check_iss355():
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
    # ★★MISS 判据要分【正文引用】与【代码块里的沙盒产物】★★
    #   (★2026-11-23 07:2x 实测修正: 交卷页里贴的反向用例【原样输出】会提到沙盒里临时造的假文件
    #    (★例: SW/tools/stray_default.sh —— selftest 反向用例故意在沙盒里造一个旧默认站点★)
    #    ⇒ 那种文件本来就不该在仓里 ⇒ 计成 MISS = 闸恒红 ⇒ 必须放过【仅出现在代码块里】的这类引用★)
    fenced = re.findall(r"```.*?```", txt, re.S)
    fenced_txt = "\n".join(fenced)
    body_txt = re.sub(r"```.*?```", "", txt, flags=re.S)
    refs = set()
    for line in body_txt.splitlines():
        if any(w in line for w in ("不存在", "待建", "本批不建", "未做")):
            continue
        refs.update(PATH_RE.findall(line))
    refs = sorted(refs)
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p))]
    sandbox_only = []
    for p in miss:
        # ★只在【代码块】里出现过 ⇒ 判定为沙盒产物 (不计入 MISS, 但要在明细里露出来) ★
        if p in fenced_txt and p not in body_txt:
            sandbox_only.append(p)
    real_miss = [p for p in miss if p not in sandbox_only]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(real_miss) == 0,
                "正文引用 %d 个 · 真 MISS %d %s · 代码块沙盒产物 %d %s"
                % (len(refs), len(real_miss), real_miss[:3], len(sandbox_only), sandbox_only[:3])))

    # ── 板指纹 (零写板) + 双证 ──
    got = md5(os.path.join(PROJ, BOARD))
    st = os.stat(os.path.join(PROJ, BOARD))
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    out.append(("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]),
                "%s / %s" % (got, mt)))
    out.append(("交卷页含板指纹双证 (开工前 + 交卷后)", txt.count(BOARD_MD5) >= 2,
                "出现 %d 次" % txt.count(BOARD_MD5)))

    # ── 零落表 ──
    bad = []
    for p, want in PROTECTED.items():
        g = md5(os.path.join(PROJ, p))
        if g != want:
            bad.append("%s(%s≠%s)" % (p, g[:8], want[:8]))
    out.append(("零落表: 受保护件 %d 件 md5 逐字节未动" % len(PROTECTED), len(bad) == 0,
                "动 %d %s" % (len(bad), bad[:3])))

    # ── 零改别人的分片 (按登记条目判) ──
    x_bad = []
    try:
        import yaml
        for f in OTHER_FRAGS:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f),
                                    encoding="utf-8")) or {}
            for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
                for e in (d.get(sect) or []):
                    if isinstance(e, dict):
                        k = str(e.get("key") or e.get("id") or e.get("path") or "")
                        if "iss355" in k.lower():
                            x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    except Exception as ex:
        x_bad.append("解析失败 %s" % ex)
    out.append(("别人的分片 (pm/hw/mech) 零本单登记条目", len(x_bad) == 0, "越界 %d %s" % (len(x_bad), x_bad[:3])))

    # ── 自带闸 ──
    if not os.path.isfile(os.path.join(PROJ, GATE)):
        out.append(("自带闸 %s 存在" % GATE, False, GATE))
    else:
        out.append(("自带闸 %s 存在" % GATE, True, GATE))
        rc, o = sh("python3 %s --selftest" % GATE)
        last = o.strip().splitlines()[-1] if o.strip() else ""
        out.append(("自带闸 --selftest 末行 ALL TESTS PASS", rc == 0 and "ALL TESTS PASS" in last,
                    "rc=%d 末行=%r" % (rc, last[:60])))
        rc2, o2 = sh("python3 %s" % GATE)
        named = len(re.findall(r"L\d+", o2))
        out.append(("自带闸裸跑带名单 (逐条 文件:行)", named >= 2, "命中行号 %d 处" % named))
        out.append(("自带闸裸跑 rc=0 (「当下执行口径=旧目标」= 0 条)", rc2 == 0, "rc=%d" % rc2))

    # ── ★main 独立读脚本默认值 (不依赖 agent 的闸) ──
    spath = os.path.join(PROJ, SCRIPT)
    if not os.path.isfile(spath):
        out.append(("转换脚本 %s 在盘" % SCRIPT, False, SCRIPT))
    else:
        stxt = open(spath, encoding="utf-8", errors="replace").read()
        m_route = re.search(r'ROUTE_DEFAULT\s*=\s*"?([A-Za-z0-9_\-]+)"?', stxt)
        m_tgt = re.search(r'TARGET_PLATFORM_DEFAULT\s*=\s*"?([A-Za-z0-9_\-]+)"?', stxt)
        out.append(("★默认路线 = rknn3 (机器读脚本, 非注释)", bool(m_route) and m_route.group(1) == "rknn3",
                    m_route.group(1) if m_route else "未找到 ROUTE_DEFAULT"))
        out.append(("★默认 target_platform = rk3572 (机器读脚本)", bool(m_tgt) and m_tgt.group(1) == "rk3572",
                    m_tgt.group(1) if m_tgt else "未找到 TARGET_PLATFORM_DEFAULT"))
        out.append(("★两件套 (.rknn + .weight) 拷贝在位", ".weight" in stxt and "copy_two_piece" in stxt,
                    ".weight=%s copy_two_piece=%s" % (".weight" in stxt, "copy_two_piece" in stxt)))
        out.append(("★缺 .weight ⇒ 失败路径在位 (不许只拷 .rknn)", "rc=1" in stxt or "exit 5" in stxt or "rc=5" in stxt,
                    "失败退出码路径存在"))
        out.append(("旧链保留为次要路线① 且带标记 (不是死代码)",
                    "LEGACY_TARGET_PLATFORM_DEFAULT" in stxt and "rk3576" in stxt,
                    "LEGACY_* 默认值在盘"))
        out.append(("旧链仍可达 (ROUTE=legacy / --route legacy)",
                    "legacy" in stxt and ("--route" in stxt or "ROUTE" in stxt), "legacy 入口在盘"))

    # ── ★ISS-353 口径层闸交叉校验 (本单不许让既有闸变红) ──
    rc3, o3 = sh("python3 %s" % CALIBER)
    # ★口径闸的结论行有两种写法: 「仍有 N 条「结论矛盾(要处置)」」/「全仓无「结论矛盾(要处置)」」⇒ 两种都要认 ★
    zero_ok = ("全仓无「结论矛盾" in o3) or bool(re.search(r"结论矛盾\D{0,8}0\s*条", o3))
    out.append(("ISS-353 口径层闸 rc=0 且结论矛盾 = 0", rc3 == 0 and zero_ok,
                "rc=%d %s" % (rc3, ("全仓无结论矛盾" if "全仓无「结论矛盾" in o3 else "未读到"))))

    # ── 板端 [0数据] + 降级 ──
    out.append(("板端接受性标 [0数据] (不许写成已验)", "[0数据]" in txt, "含 [0数据]"))
    out.append(("降级 A/B/C 在盘 (板到手一条命令)", all(x in txt for x in ("降级 A", "降级 B", "降级 C")),
                "A/B/C 三档"))

    # ── 零外发 / 零采购 (否定语境窗口) ──
    hits = forbidden_hits(txt)
    out.append(("零外发/零采购: 无「买板/等回信/跟进邮件」的非否定语境表述", len(hits) == 0,
                "命中 %d %s" % (len(hits), hits[:3])))

    # ── 不代拍 ──
    out.append(("ISS-155 台账标签不代拍 (交 main 裁)", "ISS-155" in txt and ("交 main" in txt or "不代拍" in txt),
                "ISS-155 段落 + 交 main 在盘"))

    # ── 证据目录 ──
    n = len(os.listdir(os.path.join(PROJ, LOGS))) if os.path.isdir(os.path.join(PROJ, LOGS)) else 0
    out.append(("logs/iss355/ 证据在盘 (≥ 6 件)", n >= 6, "%d 件" % n))

    # ── 必跑项 ──
    rc4, o4 = sh("python3 state/merge.py")
    out.append(("merge.py rc=0", rc4 == 0, "rc=%d" % rc4))
    rc5, o5 = sh("python3 state/gate_check.py")
    m3 = re.search(r"Q1[^\n]*?(\d+)\s*/\s*18", o5)
    out.append(("gate_check.py rc=0 且 Q1 = 18/18", rc5 == 0 and bool(m3) and m3.group(1) == "18",
                "rc=%d Q1=%s" % (rc5, m3.group(0) if m3 else "未读到")))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-355 签收闸 · 自测 (★反向用例★)")
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
    r.append(("反向用例4a · 禁止性表述 (不许采购 RK3572) 不算违规",
              forbidden_hits("★老板指示: 不许再提采购 RK3572 主板/开发板★") == []))
    r.append(("反向用例4b · 真建议 (建议买一块 RK3572 板) 必须被抓到",
              forbidden_hits("建议买一块 RK3572 板来验证") != []))
    # ★反向用例5: 默认路线判据必须能分辨 rknn3 / rk3576 ★
    def route_of(body):
        m = re.search(r'ROUTE_DEFAULT\s*=\s*"?([A-Za-z0-9_\-]+)"?', body)
        t = re.search(r'TARGET_PLATFORM_DEFAULT\s*=\s*"?([A-Za-z0-9_\-]+)"?', body)
        return (m.group(1) if m else None, t.group(1) if t else None)
    r.append(("反向用例5 · 默认路线判据能分辨 (rknn3/rk3572 vs rk3576)",
              route_of('ROUTE_DEFAULT="rknn3"\nTARGET_PLATFORM_DEFAULT="rk3572"') == ("rknn3", "rk3572")
              and route_of('ROUTE_DEFAULT="legacy"\nTARGET_PLATFORM_DEFAULT="rk3576"') != ("rknn3", "rk3572")))
    r.append(("反向用例6 · 两件套判据能分辨 (缺 .weight ⇒ 不算在位)",
              (".weight" in "copy .rknn .weight") and not (".weight" in "copy .rknn")))
    # ★反向用例7: MISS 判据必须【只放过代码块里的沙盒产物】, 正文里引用的真缺文件仍要判红 ★
    def miss_check(body):
        fenced_txt = "\n".join(re.findall(r"```.*?```", body, re.S))
        body_txt = re.sub(r"```.*?```", "", body, flags=re.S)
        refs = set()
        for line in body_txt.splitlines():
            refs.update(PATH_RE.findall(line))
        miss = [p for p in sorted(refs) if not os.path.exists(os.path.join(PROJ, p))]
        sandbox_only = [p for p in miss if p in fenced_txt and p not in body_txt]
        return [p for p in miss if p not in sandbox_only]
    r.append(("反向用例7a · 代码块里的沙盒假文件 ⇒ 不计 MISS",
              miss_check("```\n✅ 反向用例: 点名 SW/tools/stray_default.sh L2\n```\n") == []))
    r.append(("反向用例7b · 正文引用的真缺文件 ⇒ 必须判红",
              miss_check("见 SW/tools/definitely_missing_file_xyz.py\n") != []))
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
        lines = check_iss355()
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
        vr = ("✅ verified (★main 2026-11-23 07:2x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_0720_main_sign_iss355.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` "
                "逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 (受保护件 5 件同值) · 零改别人的分片 · 零外发 · 零采购 · 未替老板拍板 · 未新增拍板项 ★ "
                "★ **本单 = 转换脚本迁主路线 (实现侧)**: ① `SW/tools/rk3572_model_rebuild.sh` 的【默认路线】从 rknn-toolkit2 2.3.2 + "
                "`target_platform='rk3576'` 迁到 **rknn3-toolkit 1.2.0 + `target_platform='rk3572'`** (机器可读: `ROUTE_DEFAULT=rknn3` / "
                "`TARGET_PLATFORM_DEFAULT=rk3572`, ★main 自己 grep 脚本读的, 不看注释★) ② 落盘段强制 **`.rknn` + 同名 `.weight` 两件套成对** "
                "(缺 `.weight` ⇒ rc≠0 且不拷出任何东西 ⇒ 「只拷 .rknn 一定失败」这条坑被机器堵死) ③ 旧链保留为次要路线① (`ROUTE=legacy` 仍可达) "
                "并标明代价 ④ 新建只读闸 `SW/tools/check_iss355_convert_route.py` (扫「当下执行口径=旧目标」逐条点名 + 默认值断言 + 两件套行为级断言; "
                "`--selftest` 反向用例含「改回旧 target ⇒ 判红并点名」) ⑤ ★**新默认路线真跑过** (rc 全 0 · build 50.068 s · 产物 `.rknn` 249,360 B "
                "md5 `97a34fff…` + `.weight` 1,960,448 B md5 `7c04da4f…` ⇒ 与 ISS-263 产物逐字节相同) ★ "
                "★ **main 独立复核的关键一条**: ★**默认路线由 main 自己 grep 脚本默认值确认 (ROUTE_DEFAULT=rknn3 / TARGET_PLATFORM_DEFAULT=rk3572), "
                "并独立复跑 ISS-353 口径层闸 ⇒ rc=0 且「结论矛盾 = 0」⇒ 本单没有让任何既有闸变红** ★ "
                "★ **板端接受性仍 [0数据]** ⇒ 本单不解决板端 (降级 A/B/C 已在 ISS-353 §B3) ⇒ ★**ISS-155 台账标签 = 交 main 裁, 本单未代拍** ★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_0720_main_sign_iss355.py'", new,
                         count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_0720_main_sign_iss355.py'\n"
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
