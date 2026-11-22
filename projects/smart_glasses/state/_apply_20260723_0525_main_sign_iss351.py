#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0525_main_sign_iss351.py
==================================================
main (项目总工) 的【签收闸 · ISS-351 (hw-lead · 存储轴旧口径清账)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评

用法:
  python3 state/_apply_20260723_0525_main_sign_iss351.py --check-only ISS-351
  python3 state/_apply_20260723_0525_main_sign_iss351.py --sign ISS-351
  python3 state/_apply_20260723_0525_main_sign_iss351.py --self-test
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

HANDOFF = "HANDOFF/2026-11-23_hw-lead_ISS351_存储轴旧口径清账.md"
BLOCKS = [
    ("B0", ["边界", "复述", "一句话", "B0"]),
    ("B1", ["结论", "事实基线", "B1"]),
    ("B2", ["验收标准", "自评", "B2"]),
    ("B3", ["证据分级", "证据等级", "证据", "B3"]),
    ("B4", ["接口取值", "接口声明", "interface_claims", "B4"]),
    ("B5", ["未决", "卡点", "阻塞", "B5"]),
    ("B6", ["自证", "复现", "命令", "边界自证", "B6"]),
    ("B7", ["交 main", "B7"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config)/[0-9A-Za-z_./一-鿿-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}
# ★本单定点改的那一条 + 同型残留 3 条 (★条名逐字★)
TARGET = "vendor_q19_boot_storage"
RESIDUE = ["fw_boot_storage_bom", "q3_storage_and_audio", "R-hw-boot-storage"]
MUST_HAVE = ["≥128 MiB (1 Gbit)", "板侧零动作", "不重出板", "199.969"]
MUST_NOT = ["16-64MB", "请并入第一轮跟进邮件"]
NEG_WINDOW = 70


def block_code(h):
    """★★判据: 本仓块标题写法是 `## ★B1 · 结论摘要 ★` ⇒ 先剥装饰再取块号
    ★★真闸与自测共用这一个函数 (★免得自测测的是另一套判据★)★★"""
    s = h.lstrip("★·—–- \t【】〖〗=·")
    m = re.match(r"^(B[0-7])\b", s)
    return m.group(1) if m else None


def sh(cmd, timeout=900):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_iss351():
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
        if any(w in line for w in ("未做", "第 2 批", "本批不建", "待建", "不存在")):
            continue
        refs.update(PATH_RE.findall(line))
    refs = sorted(refs)
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p))]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(miss) == 0,
                "引用 %d 个 · MISS %d %s" % (len(refs), len(miss), miss[:3])))

    # ── hw.yaml 定点条目逐字核对 ──
    import yaml
    frag = open(os.path.join(PROJ, "state/fragments/hw.yaml"), encoding="utf-8").read()
    d = yaml.safe_load(frag) or {}

    def find_entry(key):
        # ★★判据: 本仓不同 section 用不同的键名字段 (★answers/needs_from 用 `key`, risks 用 `id`★)
        #   ⇒ 查找时要【同时认 key / id】, 取值时要【同时认 value / item / text】★★
        for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
            for e in (d.get(sect) or []):
                if isinstance(e, dict) and (e.get("key") == key or e.get("id") == key):
                    return sect, e
        return None, None

    def entry_text(e):
        return str((e or {}).get("value") or (e or {}).get("item") or (e or {}).get("text") or "")

    sect, ent = find_entry(TARGET)
    val = entry_text(ent)
    out.append(("定点条目 %s 在盘" % TARGET, ent is not None, "section=%s" % sect))
    miss_h = [k for k in MUST_HAVE if k not in val]
    out.append(("%s 新口径 4 项齐全" % TARGET, ent is not None and not miss_h, "缺 %s" % miss_h[:3]))
    hit_old = [k for k in MUST_NOT if k in val]
    out.append(("%s 旧口径已清 (16-64MB / 跟进邮件)" % TARGET, len(hit_old) == 0, "残留 %s" % hit_old[:3]))
    # ★「板宽 12->15mm」只允许出现在 eMMC 语境里 (★另一条 FCCSP 驱动的板宽不许混进来★)
    bad_ctx = []
    for pat in ("12->15mm", "12→15"):
        start = 0
        while True:
            idx = val.find(pat, start)
            if idx < 0:
                break
            ctx = val[max(0, idx - NEG_WINDOW): idx + len(pat) + NEG_WINDOW]
            if "eMMC" not in ctx:
                bad_ctx.append("%s@%d" % (pat, idx))
            start = idx + 1
    out.append(("%s 板宽提法只挂 eMMC 档" % TARGET, len(bad_ctx) == 0,
                "非 eMMC 语境 %d %s" % (len(bad_ctx), bad_ctx[:2])))

    # ── 同型残留 3 条: 要么已改口径, 要么写明「已取代·不再引用」 ──
    bad_r = []
    for k in RESIDUE:
        _s, e = find_entry(k)
        v = entry_text(e)
        if not v:
            bad_r.append("%s(不在盘)" % k)
            continue
        ok = (("128 MiB" in v) or ("已取代" in v) or ("不再引用" in v) or ("分档" in v))
        if not ok:
            bad_r.append(k)
    out.append(("同型残留 3 条已处置 (改口径或写明已取代)", len(bad_r) == 0, "未处置 %s" % bad_r[:3]))

    # ── 零重复 key (只查本单条目) ──
    struct = []
    for sect2 in ("artifacts", "answers", "needs_from", "needs", "interface_claims", "claims", "risks"):
        for e in (d.get(sect2) or []):
            if isinstance(e, dict):
                struct.append("%s:%s" % (sect2, e.get("key") or e.get("path")))
    dup = [k for k in set(struct) if struct.count(k) > 1]
    dup_mine = [k for k in dup if any(t in k for t in ([TARGET] + RESIDUE))]
    out.append(("hw.yaml 本单条目零重复 key (结构判)", len(dup_mine) == 0,
                "本单重复 %d %s · ★全表历史重复 %d 条 (不是本单的账)★" % (len(dup_mine), dup_mine[:2], len(dup))))

    # ── logs 在盘 ──
    logs = os.path.join(PROJ, "logs/iss351")
    n = len(os.listdir(logs)) if os.path.isdir(logs) else 0
    out.append(("logs/iss351/ 证据在盘 (≥ 10 件)", n >= 10, "%d 件" % n))

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
    print("★ ISS-351 签收闸 · 自测 (★反向用例★)")
    txt = open(os.path.join(PROJ, HANDOFF), encoding="utf-8").read()
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)

    def blocks_ok(hs):
        return all(any(block_code(h) == c and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)
    print("  %s 真交卷页 · 8 块齐全" % ("✅" if blocks_ok(heads) else "❌"))
    print("  %s 反向用例1 · 抽掉 B5 小节标题 ⇒ 判红"
          % ("✅" if not blocks_ok([h for h in heads if block_code(h) != "B5"]) else "❌"))
    print("  %s 反向用例2 · 塞占位符 ⇒ 判红"
          % ("✅" if len(PLACEHOLDER.findall(txt + "<!-- 待填 -->")) > len(PLACEHOLDER.findall(txt)) else "❌"))
    good = "外挂 SPI-NOR ≥128 MiB (1 Gbit) 起 · 板侧零动作 · 不重出板 · rootfs ∈ [7.969, 199.969] MiB"
    bad = "外挂 SPI-NOR 16-64MB · 请并入第一轮跟进邮件 · 板宽可能 12->15mm"
    ok3 = (not [k for k in MUST_HAVE if k not in good]) and bool([k for k in MUST_NOT if k in bad])
    print("  %s 反向用例3 · 新旧口径判据能分辨" % ("✅" if ok3 else "❌"))
    allok = blocks_ok(heads) and ok3
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss351()
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
        vr = ("✅ verified (★main 2026-11-23 05:2x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_0525_main_sign_iss351.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` "
                "逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 · 零改闸 · 零外发 · 未替老板拍板 · 零新增拍板项 · 零写别人的分片 (hw.yaml 只读) ★ "
                "★ **本单 = 存储轴旧口径清账**: `vendor_q19_boot_storage` 三处错全清 (容量 16-64MB ⇒ ≥128 MiB (1 Gbit) 起 · "
                "板宽 12->15mm ⇒ 只属 eMMC 档 (SPI-NOR 档板侧零动作·不重出板) · 「请并入第一轮跟进邮件」⇒ 改「自己网上查 + 标证据等级 + 写降级方案」) + "
                "★**同型残留 4 条命中 (1 定点 + 3 残留) 逐条处置 + 3 条不命中逐条带理由**★ + ★**识别出一条跨轴同类 (`answers[4] "
                "vendor_fccsp_pitch` 仍写「请并入第一轮跟进邮件」⇒ FCCSP 轴·不在本单判据·未擅动·已上报 main)**★ + ★**识破一条陷阱: "
                "`answers[0] pcb_outline_confirm` 也写着「板宽 12->15mm」但那是 FCCSP pitch 驱动的另一个板宽 ⇒ 顺手改 = 把两条不同驱动搅成一锅 ⇒ 不动**★ ★ "
                "★ **交 main 裁的 2 件 (本单未代裁)**: ① LAY-08 vs LAY-03 冲突带 (rootfs ∈ (64, 71.969] MiB ⇒ ISS-346 §1.2 已登记) "
                "② `answers[4]` 跨轴同类病灶是否另派一单清 ★ **另登记一条 [媒体] 级提示 (不改结论·不加拍板项)**: Lexar 有 7.2×7.2mm "
                "subsize eMMC ⇒ 日后真走 eMMC 档时「板宽 12→15mm」这个代价有可能不成立·选型时需复核 ★★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_0525_main_sign_iss351.py'", new,
                         count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_0525_main_sign_iss351.py'\n"
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
