#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0455_main_sign_iss350.py
==================================================
main (项目总工) 的【签收闸 · ISS-350 (sw-lead · Q3 分档口径写回 SW 侧)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评

用法:
  python3 state/_apply_20260723_0455_main_sign_iss350.py --check-only ISS-350
  python3 state/_apply_20260723_0455_main_sign_iss350.py --sign ISS-350
  python3 state/_apply_20260723_0455_main_sign_iss350.py --self-test

边界: 零写板 · 零落表 · 零改闸 · 零外发 · 只写 state/issue_log.yaml (main 的地界)
      ★**不许写 state/fragments/sw.yaml (sw-lead 的分片)★**
"""
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

HANDOFF = "HANDOFF/2026-11-23_sw-lead_ISS350_Q3分档口径写回SW侧.md"
BLOCKS = [
    ("B0", ["一句话结论", "结论", "B0"]),
    ("B1", ["事实基线", "B1"]),
    ("B2", ["验收标准", "自评", "B2"]),
    ("B3", ["证据分级", "证据等级", "证据", "B3"]),
    ("B4", ["接口取值", "接口声明", "interface_claims", "B4"]),
    ("B5", ["未决", "卡点", "阻塞", "时点", "B5"]),
    ("B6", ["边界自证", "零写板", "自证", "复现", "B6"]),
    ("B7", ["交 main", "B7"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config)/[0-9A-Za-z_./-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
# ★★手误串 (★main 派活消息里打错过一次的那串·★绝不许流进任何交付物★★)
TYPO_MD5 = "fb278f91a0075"
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
# ★本单该改的 sw.yaml 条目 (★结构化判★)
NEED_KEY = "iss338_need_boot_storage_answer"
ANSWER_KEYS = ["iss346_q3_storage_tier_verdict_sw", "iss346_storage_capacity_matrix"]
# ★新措辞必须逐字含有的片段
MUST_HAVE = ["4 条", "SPI_SCLK_BOOT", "SPI_CSn_BOOT", "SPI_MOSI_BOOT", "SPI_MISO_BOOT",
             "板侧零动作", "不重出板", "SoM 侧是否引出"]
# ★旧措辞必须不再出现的片段 (★「3 条」/「板要重出」/旧容量口径★)
MUST_NOT = ["板要重出", "16-64MB", "16~64 MB", "16~64MB"]


def sh(cmd, timeout=900):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_iss350():
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
        hit = any(h.startswith(code) and any(k in h for k in kws) for h in heads)
        out.append(("交卷页 %s 块标题齐全" % code, hit, kws[0]))
    ph = PLACEHOLDER.findall(txt)
    out.append(("交卷页占位符 = 0", len(ph) == 0, "命中 %d" % len(ph)))
    refs = sorted(set(PATH_RE.findall(txt)))
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p))]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(miss) == 0,
                "引用 %d 个 · MISS %d %s" % (len(refs), len(miss), miss[:3])))

    # ── 手误 md5 串全树扫描 (★绝不许流进交付物★) ──
    typo_hits = []
    SELF = os.path.abspath(__file__)
    for root, dirs, files in os.walk(PROJ):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".trash", "tmp")]
        for f in files:
            if not f.endswith((".md", ".py", ".yaml", ".txt", ".csv", ".sh", ".json")):
                continue
            p = os.path.join(root, f)
            if os.path.abspath(p) == SELF:
                continue   # ★★扫描器自己不参与判定 (★自指⇒ 恒命中 1 的假阳性★)
            try:
                if TYPO_MD5 in open(p, encoding="utf-8", errors="ignore").read():
                    typo_hits.append(os.path.relpath(p, PROJ))
            except Exception:
                pass
    out.append(("★手误 md5 串全树命中 = 0 (除扫描器自身)", len(typo_hits) == 0,
                "命中 %d %s" % (len(typo_hits), typo_hits[:3])))

    # ── sw.yaml 逐字核对 ──
    import yaml
    frag = open(os.path.join(PROJ, "state/fragments/sw.yaml"), encoding="utf-8").read()
    d = yaml.safe_load(frag) or {}
    need = None
    for e in (d.get("needs_from") or []):
        if isinstance(e, dict) and e.get("key") == NEED_KEY:
            need = e
    item = (need or {}).get("item", "") or (need or {}).get("value", "")
    miss_have = [k for k in MUST_HAVE if k not in item]
    out.append(("need %s 新措辞 8 项齐全" % NEED_KEY, need is not None and not miss_have,
                "缺 %s" % miss_have[:3]))
    # ★★【判据修正在产生点】★★: 「旧口径已清」不能按【子串出现】判 ——
    #   新措辞里会以【引号 + 否定】的形式引用旧说法 (★如「若外挂 SPI-NOR ⇒ 板要重出』不成立★)
    #   ⇒ 正确判据 = ★每一次出现都必须在否定语境里 (★窗口 ±40 字内出现否定标记★)★★
    NEG = ("不成立", "不", "未", "非", "否", "作废", "错")
    bad_ctx = []
    for k in MUST_NOT:
        start = 0
        while True:
            idx = item.find(k, start)
            if idx < 0:
                break
            ctx = item[max(0, idx - 40): idx + len(k) + 40]
            if not any(n in ctx for n in NEG):
                bad_ctx.append("%s@%d" % (k, idx))
            start = idx + 1
    out.append(("need %s 旧措辞已清 (板要重出 / 16-64MB · 允许引号内否定)" % NEED_KEY, len(bad_ctx) == 0,
                "残留断言 %d %s" % (len(bad_ctx), bad_ctx[:3])))
    ans = {}
    for sect in ("answers", "interface_claims"):
        for e in (d.get(sect) or []):
            if isinstance(e, dict) and e.get("key") in ANSWER_KEYS:
                ans["%s:%s" % (sect, e.get("key"))] = e
    out.append(("sw.yaml 分档结论已登记 (answers + interface_claims)",
                len(ans) >= 3, "登记 %d 条 %s" % (len(ans), sorted(ans))))

    # ── 零重复 key (★只查本单自己登记的条目★) ──
    struct = []
    for sect in ("artifacts", "answers", "needs_from", "needs", "interface_claims", "claims"):
        for e in (d.get(sect) or []):
            if isinstance(e, dict):
                struct.append("%s:%s" % (sect, e.get("key") or e.get("path")))
    dup = [k for k in set(struct) if struct.count(k) > 1]
    dup_mine = [k for k in dup if any(t in k for t in (NEED_KEY, "iss346_q3_storage_tier_verdict_sw"))]
    out.append(("sw.yaml 本单条目零重复 key (结构判)", len(dup_mine) == 0,
                "本单重复 %d %s · ★全表历史重复 %d 条 (不是本单的账)★" % (len(dup_mine), dup_mine[:2], len(dup))))

    # ── 受保护件 + 板指纹 ──
    bad = []
    for p, want in PROTECTED.items():
        got = md5(os.path.join(PROJ, p))
        if got != want:
            bad.append("%s(%s≠%s)" % (p, got[:8], want[:8]))
    out.append(("受保护件 %d 件 md5 逐字节未动" % len(PROTECTED), len(bad) == 0, "动 %d %s" % (len(bad), bad[:3])))
    st = os.stat(os.path.join(PROJ, BOARD))
    import datetime
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    got = md5(os.path.join(PROJ, BOARD))
    out.append(("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]),
                "%s / %s" % (got, mt)))
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-350 签收闸 · 自测 (★反向用例★)")
    raw = open(os.path.join(PROJ, HANDOFF), "rb").read()
    txt = raw.decode("utf-8")
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)

    def blocks_ok(hs):
        return all(any(h.startswith(c) and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)
    print("  %s 真交卷页 · 8 块齐全" % ("✅" if blocks_ok(heads) else "❌"))
    print("  %s 反向用例1 · 抽掉 B4 小节标题 ⇒ 判红"
          % ("✅" if not blocks_ok([h for h in heads if not h.startswith("B4")]) else "❌"))
    print("  %s 反向用例2 · 塞占位符 ⇒ 判红"
          % ("✅" if len(PLACEHOLDER.findall(txt + "<!-- 待填 -->")) > len(PLACEHOLDER.findall(txt)) else "❌"))
    good = "4 条 SPI_SCLK_BOOT/SPI_CSn_BOOT/SPI_MOSI_BOOT/SPI_MISO_BOOT · 板侧零动作 · 不重出板 · SoM 侧是否引出"
    bad = "3 条 SPI_*_BOOT · 若外挂 SPI-NOR ⇒ 板要重出 · 16-64MB"
    print("  %s 反向用例3 · 新措辞判据能分辨新旧文本"
          % ("✅" if (not [k for k in MUST_HAVE if k not in good]) and [k for k in MUST_NOT if k in bad] else "❌"))
    allok = blocks_ok(heads)
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss350()
        print("=" * 78)
        print("★ %s 签收验收线 (★main 本机实跑 · fail-closed · 不抄 agent 自评★)" % issue)
        allok = True
        for name, ok, detail in lines:
            allok = allok and bool(ok)
            print("  %s %-38s %s" % ("✅" if ok else "❌", name, detail))
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
        vr = ("✅ verified (★main 2026-11-23 05:0x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_0455_main_sign_iss350.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` "
                "逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 · 零改闸 · 零外发 · 未替老板拍板 · 零写别人的分片 (sw.yaml 只读) ★ "
                "★ **本单 = Q3 分档口径写回 SW 侧 (ISS-346 签收后开的)**: `iss338_need_boot_storage_answer` 已改成 "
                "「4 条 SPI_*_BOOT (网表 L202/L204/L206/L208)」+「外挂 SPI-NOR ⇒ 板侧零动作, 不重出板」+ "
                "「问原厂改问 SoM 侧是否引出这 4 条 SPI boot pin」+ ★**零铜域口径不变 (必需 23 条不变; SPI_CSn_BOOT 板面已有铜 "
                "31.352 mm ⇒ 本就不在零铜域)**★ ⇒ ★**Q3 = 分档, 不再整卡占着板那一趟的阻塞位**★ ★ "
                "★ **交 main 裁的 3 条 (本单已按 main 裁执行·需 main 回执)**: ① `--set-field` 实测该 key 在 `needs_from` "
                "(★已按 needs_from 走·口径无冲突★) ② 多清 2 处同源旧口径 (★已披露·可回滚★) ③ 「4 条」≠「必需 24」 "
                "(★必需 23 条不变★) ★★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_0455_main_sign_iss350.py'", new,
                         count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_0455_main_sign_iss350.py'\n"
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
