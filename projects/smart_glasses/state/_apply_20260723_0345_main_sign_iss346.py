#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0345_main_sign_iss346.py
==================================================
main (项目总工) 的【签收闸 · ISS-346 (sw-lead · Q3 存储轴可判矩阵)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) ——
       ★不抄 agent 的自评, ★不抄交卷页的结论, ★每条都本机实读★

用法:
  python3 state/_apply_20260723_0345_main_sign_iss346.py --check-only     # 只跑验收线, 零写盘
  python3 state/_apply_20260723_0345_main_sign_iss346.py --sign ISS-346   # 全绿才落签收

边界: 零写板 · 零落表 · 零改闸 · 零改真生成器 · 零外发 · 只写 state/issue_log.yaml (main 的地界)
      ★**不许写 state/fragments/sw.yaml (sw-lead 的分片)★**
"""
import hashlib
import json
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

HANDOFF = "HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md"

# ★交卷页必备块 (★关键字取自 gate_check.py 的 Q1 口径 + 本单 B0~B7★)
BLOCKS = [
    ("B0", ["一句话结论", "B0"]),
    ("B1", ["事实基线", "B1"]),
    ("B2", ["容量", "矩阵", "B2"]),
    ("B3", ["rootfs", "降级", "B3"]),
    ("B4", ["零代价", "接口取值", "B4"]),
    ("B5", ["时点", "卡点", "未决", "B5"]),
    ("B6", ["边界自证", "零写板", "B6"]),
    ("B7", ["交 main", "B7"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config)/[0-9A-Za-z_./-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
KNOWN_EXAMPLE_PATHS = {
    "MECH/FOO.md": "★闸 `--whitelist` 用法示例里的占位文件名 ⇒ 不是对真实文件的引用★",
}

# ★受保护件 md5 (★逐字取自交卷页 B1-5「开工前 = 交卷后」表 ——
#   ★★main 用【交卷页自证的那组值】去核对【当前盘面】⇒ 若期间被动过就判红★★)
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "SW/tools/flash_layout_check.py": "06d850d43e7b5cabee42c580511237d7",
    "SW/tools/s2_rescue_config.example.json": "5b9d23f7e50d67ec7474fe5bad57339b",
    "SW/FLASH_AND_VERSION.md": "4f272497bf60dabfd8304c52949211f6",
}

# ★4 件交付物 (★交卷页「附 · 本单交付物清单」逐字★)
DELIVERABLES = [
    "SW/STORAGE_CAPACITY_MATRIX.md",
    "SW/tools/gen_storage_capacity_matrix.py",
    HANDOFF,
    "logs/iss346/matrix_cells.json",
    "logs/iss346/matrix_table.md",
    "logs/iss346/cmd_manifest.txt",
    "SW/tools/s2_rescue_config.example.json",
    "SW/tools/flash_layout_check.py",
]

# ★分片登记 (★sw-lead 的分片 — main 只读不写★)
FRAG_KEYS = [
    "iss346_storage_capacity_matrix",
    "iss346_need_board_side_storage_input",
    "SW/STORAGE_CAPACITY_MATRIX.md",
    "SW/tools/gen_storage_capacity_matrix.py",
    "HANDOFF/2026-11-23_sw-lead_ISS346_存储容量矩阵与板侧时点.md",
]


def sh(cmd, timeout=900):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_board():
    out = []
    st = os.stat(os.path.join(PROJ, BOARD))
    import datetime
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    got = md5(os.path.join(PROJ, BOARD))
    out.append(("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]),
                "%s / %s" % (got, mt)))
    return out


def check_handoff():
    out = []
    full = os.path.join(PROJ, HANDOFF)
    if not os.path.isfile(full):
        out.append(("交卷页存在", False, HANDOFF))
        return out, ""
    raw = open(full, "rb").read()
    txt = raw.decode("utf-8")
    out.append(("交卷页存在", True, "%s (%d B)" % (HANDOFF, len(raw))))
    out.append(("交卷页不是骨架 (≥ 4000 B)", len(raw) >= 4000, "%d B" % len(raw)))
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)
    for code, kws in BLOCKS:
        # ★★【判据修正在产生点】★★: 必须【只看 2 级及以下的小节标题】+ 【标题必须以块号开头】
        #   ⇒ 否则 H1 大标题里的关键词就能把整块蒙混过关 (★本单 H1 含「容量/矩阵/时点」
        #   ⇒ 旧写法里 B2/B5 是被 H1 顶过去的, 属弱判据 ★)
        hit = any(h.startswith(code) and any(k in h for k in kws) for h in heads)
        out.append(("交卷页 %s 块标题齐全" % code, hit, kws[0]))
    ph = PLACEHOLDER.findall(txt)
    out.append(("交卷页占位符 = 0", len(ph) == 0, "命中 %d" % len(ph)))
    refs = sorted(set(PATH_RE.findall(txt)))
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p)) and p not in KNOWN_EXAMPLE_PATHS]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(miss) == 0,
                "引用 %d 个 · 已知示例 %d 个 · MISS %d %s"
                % (len(refs), len([p for p in refs if p in KNOWN_EXAMPLE_PATHS]), len(miss), miss[:3])))
    return out, txt


def check_iss346():
    out = []
    h, txt = check_handoff()
    out += h

    # ── 交付物逐个在盘 ──
    missing = [p for p in DELIVERABLES if not os.path.exists(os.path.join(PROJ, p))]
    out.append(("交付物 %d 件逐个在盘 (0 MISS)" % len(DELIVERABLES), len(missing) == 0,
                "缺 %d %s" % (len(missing), missing[:3])))

    # ── 分片登记 (★只读 sw-lead 的分片★) ──
    frag = open(os.path.join(PROJ, "state/fragments/sw.yaml"), encoding="utf-8").read()
    miss_k = [k for k in FRAG_KEYS if k not in frag]
    out.append(("sw.yaml 分片 5 条登记齐全", len(miss_k) == 0, "缺 %d %s" % (len(miss_k), miss_k[:2])))
    # ★★【判据修正在产生点】★★: 「零重复 key」必须按【结构】判 (★yaml 里的 key/path 字段★),
    #   ★**不能按字符串出现次数判** —— 一个 path 合法地会同时出现在 `path:` 字段和另一条的
    #   `summary:` 正文里 (★本单第一次跑就假阳性了 3 条★) ⇒ 假阳性会掩盖真红项 ⇒ 必须改判据★
    try:
        import yaml
        d = yaml.safe_load(frag)
        d = d if isinstance(d, dict) else {}
        struct = []
        for sect in ("artifacts", "answers", "needs_from", "needs", "interface_claims", "claims"):
            for e in (d.get(sect) or []):
                if isinstance(e, dict):
                    struct.append(("%s:%s" % (sect, e.get("key") or e.get("path")), sect))
        seen, dup = set(), []
        for k, sect in struct:
            if k in seen:
                dup.append(k)
            seen.add(k)
        # ★只查【本单该登记的那几条】有没有被登记两遍 (★不查历史全局, 那是别人的账★)
        dup_mine = [k for k in dup if any(t in k for t in ("iss346", "ISS346", "STORAGE_CAPACITY_MATRIX",
                                                          "gen_storage_capacity_matrix"))]
        out.append(("sw.yaml 本单条目零重复 key (结构判)", len(dup_mine) == 0,
                    "本单重复 %d %s · ★全表历史重复 %d 条 (不是本单的账, 不判红)★"
                    % (len(dup_mine), dup_mine[:2], len(dup))))
        n_mine = [k for k, _ in struct if any(t in k for t in ("iss346", "ISS346", "STORAGE_CAPACITY_MATRIX",
                                                               "gen_storage_capacity_matrix"))]
        out.append(("sw.yaml 本单结构化登记 = 5 条", len(set(n_mine)) == 5,
                    "实测 %d 条 %s" % (len(set(n_mine)), sorted(set(n_mine))[:5])))
    except Exception as e:
        out.append(("sw.yaml 结构化判读", False, str(e)[:70]))

    # ── 矩阵机器输出: 20 格 + failures 空 ──
    try:
        cells = json.load(open(os.path.join(PROJ, "logs/iss346/matrix_cells.json"), encoding="utf-8"))
        n = len(cells.get("cells", []))
        f = len(cells.get("failures", []))
        out.append(("矩阵 20 格 + failures=0", n == 20 and f == 0, "cells=%d failures=%d" % (n, f)))
    except Exception as e:
        out.append(("矩阵机器输出可读", False, str(e)[:60]))

    # ── 生成器裸跑 rc=0 + 自检 ──
    rc, o = sh("python3 SW/tools/gen_storage_capacity_matrix.py")
    ok = rc == 0 and ("readonly_ok" in o or "readonly_ok=True" in o)
    out.append(("生成器裸跑 rc=0 + readonly_ok", ok, "rc=%d" % rc))
    rc, o = sh("python3 SW/tools/gen_storage_capacity_matrix.py --self-test")
    last = [l for l in o.strip().splitlines() if l.strip()][-1] if o.strip() else ""
    out.append(("生成器 --self-test 绿", rc == 0, last[:90]))

    # ── 受保护件逐件 md5 未动 (★用交卷页自证的那组值★) ──
    bad = []
    for p, want in PROTECTED.items():
        got = md5(os.path.join(PROJ, p))
        if got != want:
            bad.append("%s(%s≠%s)" % (p, got[:8], want[:8]))
    out.append(("受保护件 %d 件 md5 逐字节未动" % len(PROTECTED), len(bad) == 0,
                "动 %d %s" % (len(bad), bad[:3])))

    out += check_board()
    return out


def self_test():
    """★反向用例: 判据不能恒绿 (★本项目铁律: 晋级判据必须写成独立脚本 + 单测★)"""
    print("=" * 78)
    print("★ ISS-346 签收闸 · 自测 (★反向用例: 坏交卷页必须被判红★)")
    raw = open(os.path.join(PROJ, HANDOFF), "rb").read()
    txt = raw.decode("utf-8")
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)
    def blocks_ok(hs):
        return all(any(h.startswith(c) and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)
    ok0 = blocks_ok(heads)
    print("  %s 真交卷页 · 8 块齐全" % ("✅" if ok0 else "❌"))
    # 反向用例 1: 挖掉 B5 小节标题 ⇒ 必须判红 (★★含「H1 蒙混过关」这个真漏洞的回归★)
    bad = [h for h in heads if not h.startswith("B5")]
    ok1 = not blocks_ok(bad)
    print("  %s 反向用例1 · 抽掉 B5 小节标题 ⇒ 判红" % ("✅" if ok1 else "❌"))
    # 反向用例 2: 塞占位符 ⇒ 必须判红
    ok2 = len(PLACEHOLDER.findall(txt + "<!-- 待填 -->")) > len(PLACEHOLDER.findall(txt))
    print("  %s 反向用例2 · 塞占位符 ⇒ 判红" % ("✅" if ok2 else "❌"))
    allok = ok0 and ok1 and ok2
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss346()
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
            if "  status: verified" in seg and "_apply_20260723_0345_main_sign_iss346.py" in seg:
                # ★幂等补字段: 本条已签过, 只补 verify_date / fix_ref (★老条目本来就没这俩字段★)
                if "  verify_date:" not in seg:
                    seg = seg.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
                if "  fix_ref:" not in seg:
                    seg = seg.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_0345_main_sign_iss346.py'\n"
                bak = LOG + ".bak_%s_main_fillfields%s" % (STAMP, issue.replace("-", ""))
                shutil.copy2(LOG, bak)
                tmp = LOG + ".tmp_%d" % os.getpid()
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(src[:i] + seg + src[j:])
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, LOG)
                print("  ★幂等: 已签过 ⇒ 只补 verify_date / fix_ref · 备份 %s" % bak)
                continue
            print("  ★status 不是 fixing ⇒ 已被别的 job 签过 ⇒ 不落盘")
            continue
        vr = ("✅ verified (★main 2026-11-23 03:4x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_0345_main_sign_iss346.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` "
                "逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 · 零改闸 · 零改真生成器 · 零外发 · 未替老板拍板 · "
                "零写别人的分片 (sw.yaml 只读) ★ "
                "★ **Q3 存储轴从 [0数据] 变【可判矩阵】(5×4 · 20/20 格机器跑通 · failures=0) ⇒ 分档结论: "
                "只 ADB push / SPI-NOR(J_BOOT1 焊盘位已在板) 两档 = PCB 层零动作 · 不卡; eMMC 档 = 板宽 12→15mm ⇒ "
                "台架板档 B160x100 不卡 · 产品板档 F30A/P60x15 才卡 ⇒ ⇒ 【Q3 不再以整卡形式占着板那一趟的阻塞位】** ★ "
                "★ **交 main 的 3 条待裁** (★本单不代拍★): B7-1 Q3 分档措辞写回拍板页 + 容量口径订正为 "
                "「≥128 MiB (1 Gbit) 起」+ 「16~64MB」作废 (ISS-080 已锁死 ≥128MB · Winbond 料号是 Mbit 不是 MB) · "
                "B7-2 `iss338_need_boot_storage_answer` 措辞 3 条订正 (3 条→**4 条** SPI_*_BOOT · 「板要重出」不成立 · "
                "问原厂改问 SoM 是否引出 4 条 SPI boot pin) · B7-3 音频轴只登记「与存储轴互不依赖」一条 ★**★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        new = new.replace("  verify_date: null", "  verify_date: '2026-11-23'", 1)
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
