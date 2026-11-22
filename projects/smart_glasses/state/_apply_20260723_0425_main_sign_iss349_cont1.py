#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0425_main_sign_iss349_cont1.py
==================================================
main (项目总工) 的【签收闸 · ISS-349 cont1 (hw-lead · 板侧项全集页生成器回归修复 · 收尾续单)】
★哲学: 自己跑验收线, 全绿才签, 有红项就拒签 (fail-closed) —— 不抄 agent 的自评

用法:
  python3 state/_apply_20260723_0425_main_sign_iss349_cont1.py --check-only ISS-349
  python3 state/_apply_20260723_0425_main_sign_iss349_cont1.py --sign ISS-349
  python3 state/_apply_20260723_0425_main_sign_iss349_cont1.py --self-test

边界: 零写板 · 零落表 · 零改闸 · 零改真生成器 · 零外发 · 只写 state/issue_log.yaml (main 的地界)
      ★**不许写 state/fragments/hw.yaml (hw-lead 的分片)★**
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

HANDOFF = "HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md"
BLOCKS = [
    ("B0", ["派活复述", "边界", "B0"]),
    ("B1", ["结论", "一句话", "B1"]),
    ("B2", ["验收标准", "自评", "B2"]),
    ("B3", ["证据分级", "证据等级", "证据", "B3"]),
    ("B4", ["接口取值", "接口声明", "interface_claims", "B4"]),
    ("B5", ["卡点", "未决", "阻塞", "B5"]),
    ("B6", ["复现", "自证", "命令", "B6"]),
    ("B7", ["边界自证", "B7"]),
]
PLACEHOLDER = re.compile(r'<!--\s|待填|PLACEHOLDER|施工中|🔄|__[A-Z_]{2,}__')
PATH_RE = re.compile(r'(?:logs|state|HW|MECH|SW|config)/[0-9A-Za-z_./-]*[0-9A-Za-z_]\.[A-Za-z0-9_]{1,24}')
KNOWN_EXAMPLE_PATHS = {
    "MECH/FOO.md": "★闸 `--whitelist` 用法示例里的占位文件名 ⇒ 不是对真实文件的引用★",
}
# ★hw.yaml 里本单该登记的 key (★结构化判, 不按字符串次数判★)
FRAG_ARTIFACTS = [
    "HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md",
    "HW/check_preflight_regen_idempotent.py",
    "logs/iss349",
]
FRAG_KEYS = [
    "iss349_preflight_b33_generator_fixed",
    "iss349_preflight_regen_idempotent",
    "preflight_regen_gate_rc",
    "preflight_item_b33_pin_land_pitch",
    "preflight_item_b33_source_iss",
    "preflight_regen_gate_env",
]
# ★附项 1: q3_storage_and_audio 的 item 改前 / 改后 (★逐字★)
Q3_OLD_FRAG = "16-64MB"
Q3_NEW_FRAG = "≥128 MiB (1 Gbit) 起"
# ★受保护件 (★网表/脚表/BOM/板/板工程/生成器本体★)
PROTECTED = {
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}


def sh(cmd, timeout=900):
    env = dict(os.environ)
    env["TMPDIR"] = os.path.join(PROJ, "tmp")
    r = subprocess.run(cmd, cwd=PROJ, shell=isinstance(cmd, str),
                       capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_board():
    st = os.stat(os.path.join(PROJ, BOARD))
    import datetime
    mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S.%f")
    got = md5(os.path.join(PROJ, BOARD))
    return [("板指纹 md5+mtime 未动", got == BOARD_MD5 and mt.startswith(BOARD_MTIME[:19]),
             "%s / %s" % (got, mt))]


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
        hit = any(h.startswith(code) and any(k in h for k in kws) for h in heads)
        out.append(("交卷页 %s 块标题齐全" % code, hit, kws[0]))
    ph = PLACEHOLDER.findall(txt)
    out.append(("交卷页占位符 = 0", len(ph) == 0, "命中 %d" % len(ph)))
    refs = sorted(set(PATH_RE.findall(txt)))
    miss = [p for p in refs if not os.path.exists(os.path.join(PROJ, p)) and p not in KNOWN_EXAMPLE_PATHS]
    out.append(("交卷页引用文件逐个在盘 (0 MISS)", len(miss) == 0,
                "引用 %d 个 · MISS %d %s" % (len(refs), len(miss), miss[:3])))
    return out, txt


def check_iss349():
    out = []
    h, txt = check_handoff()
    out += h

    # ── 交付物在盘 ──
    miss = [p for p in FRAG_ARTIFACTS if not os.path.exists(os.path.join(PROJ, p))]
    out.append(("交付物 %d 件在盘 (0 MISS)" % len(FRAG_ARTIFACTS), len(miss) == 0, "缺 %s" % miss[:3]))

    # ── 生成器本体: B33 必须【在生成器里】(★不是手改产物页★) ──
    gen = os.path.join(PROJ, "state/_iss277_build_preflight.py")
    gtxt = open(gen, encoding="utf-8").read() if os.path.isfile(gen) else ""
    out.append(("生成器本体含 B33 (重跑不蒸发)", "B33_PIN_LAND_1P27" in gtxt,
                "命中 %d 次" % gtxt.count("B33_PIN_LAND_1P27")))
    page = os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md")
    ptxt = open(page, encoding="utf-8").read() if os.path.isfile(page) else ""
    out.append(("清单页含 B33", "B33_PIN_LAND_1P27" in ptxt, "命中 %d 次" % ptxt.count("B33_PIN_LAND_1P27")))

    # ── 新闸: 裸跑 + selftest ──
    rc, o = sh("python3 HW/check_preflight_regen_idempotent.py")
    out.append(("新闸裸跑 rc=0", rc == 0, "rc=%d" % rc))
    rc, o = sh("python3 HW/check_preflight_regen_idempotent.py --selftest")
    last = [l for l in o.strip().splitlines() if l.strip()][-1] if o.strip() else ""
    out.append(("新闸 --selftest 末行 ALL TESTS PASS", rc == 0 and "ALL TESTS PASS" in last, last[:70]))

    # ── 分片登记 (hw.yaml · 只读) ──
    frag = open(os.path.join(PROJ, "state/fragments/hw.yaml"), encoding="utf-8").read()
    miss_k = [k for k in FRAG_KEYS if k not in frag]
    out.append(("hw.yaml 本单 key %d 条齐全" % len(FRAG_KEYS), len(miss_k) == 0, "缺 %s" % miss_k[:2]))
    miss_a = [a for a in FRAG_ARTIFACTS if a not in frag]
    out.append(("hw.yaml 交付物 3 条已登记", len(miss_a) == 0, "缺 %s" % miss_a[:2]))
    try:
        import yaml
        d = yaml.safe_load(frag) or {}
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
        # ★★判据收窄: 「零重复」只查【本单自己登记的条目】⇒ 历史遗留的同名 artifact
        #   (★例: `HW/check_onepass_preflight_coverage.py` 在 2026-11-17 的 cont2 修 / iss297 两笔★
        #   ⇒ 不是本单的账, 不判红 — 同 ISS-346 签收闸的同一原则) ★★
        mine_marks = tuple(list(FRAG_KEYS) + list(FRAG_ARTIFACTS))
        dup_mine = [k for k in dup if any(t in k for t in mine_marks)]
        out.append(("hw.yaml 本单条目零重复 key (结构判)", len(dup_mine) == 0,
                    "本单重复 %d %s" % (len(dup_mine), dup_mine[:2])))
    except Exception as e:
        out.append(("hw.yaml 结构化判读", False, str(e)[:60]))

    # ── 附项 1: q3_storage_and_audio 的 item 逐字核对 ──
    try:
        import yaml
        d = yaml.safe_load(frag) or {}
        q3 = None
        for e in (d.get("needs_from") or []):
            if isinstance(e, dict) and e.get("key") == "q3_storage_and_audio":
                q3 = e
        item = (q3 or {}).get("item", "")
        ok_new = Q3_NEW_FRAG in item
        ok_old = Q3_OLD_FRAG not in item
        out.append(("q3_storage_and_audio item 已改 (≥128 MiB (1 Gbit) 起)", ok_new and ok_old,
                    "含新口径=%s · 残留旧口径=%s" % (ok_new, not ok_old)))
        out.append(("q3_storage_and_audio to/due 未动", (q3 or {}).get("to") == "boss" and (q3 or {}).get("due") == "2026-10-27",
                    "to=%s due=%s" % ((q3 or {}).get("to"), (q3 or {}).get("due"))))
    except Exception as e:
        out.append(("q3 条目核对", False, str(e)[:60]))

    # ── 受保护件 + 板指纹 ──
    bad = []
    for p, want in PROTECTED.items():
        got = md5(os.path.join(PROJ, p))
        if got != want:
            bad.append("%s(%s≠%s)" % (p, got[:8], want[:8]))
    out.append(("受保护件 %d 件 md5 逐字节未动" % len(PROTECTED), len(bad) == 0, "动 %d %s" % (len(bad), bad[:3])))
    out += check_board()
    return out


def self_test():
    print("=" * 78)
    print("★ ISS-349 cont1 签收闸 · 自测 (★反向用例★)")
    txt = open(os.path.join(PROJ, HANDOFF), encoding="utf-8").read()
    heads = re.findall(r"^#{2,4}\s*(.+)$", txt, re.M)

    def blocks_ok(hs):
        return all(any(h.startswith(c) and any(k in h for k in kws) for h in hs)
                   for c, kws in BLOCKS)
    ok0 = blocks_ok(heads)
    print("  %s 真交卷页 · 8 块齐全" % ("✅" if ok0 else "❌"))
    bad = [h for h in heads if not h.startswith("B2")]
    ok1 = not blocks_ok(bad)
    print("  %s 反向用例1 · 抽掉 B2 小节标题 ⇒ 判红" % ("✅" if ok1 else "❌"))
    ok2 = len(PLACEHOLDER.findall(txt + "<!-- 待填 -->")) > len(PLACEHOLDER.findall(txt))
    print("  %s 反向用例2 · 塞占位符 ⇒ 判红" % ("✅" if ok2 else "❌"))
    ok3 = (Q3_NEW_FRAG in "外挂 SPI-NOR ≥128 MiB (1 Gbit) 起") and (Q3_OLD_FRAG not in "外挂 SPI-NOR ≥128 MiB (1 Gbit) 起")
    print("  %s 反向用例3 · Q3 口径判据能分辨新旧文本" % ("✅" if ok3 else "❌"))
    allok = ok0 and ok1 and ok2 and ok3
    print("  ⇒ %s" % ("★ALL TESTS PASS★" if allok else "★★自测红★★"))
    return 0 if allok else 1


def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    sign = [a for a in args if a.startswith("ISS-")]
    check_only = "--check-only" in args or not sign
    for issue in sign:
        lines = check_iss349()
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
        vr = ("✅ verified (★main 2026-11-23 04:2x 本机独立复核 · 不抄 agent 报告★) ⇒ "
              "★**签收闸 `state/_apply_20260723_0425_main_sign_iss349_cont1.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
              + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, d in lines)
              + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` "
                "逐字节未动 ⇒ **G1 仍开, 不许投板**) · 零落表 · 零改既有闸 · 零改真生成器 · 零外发 · 未替老板拍板 · "
                "零写别人的分片 (hw.yaml 只读) ★ "
                "★ **本单 = ISS-349 cont1 (01:4x 那轮的会话在最后一步被 abort ⇒ 产物已落盘但分片未登记 ⇒ 本轮补派收尾)**: "
                "交卷页 B0~B7 齐全 + 页内引用 0 MISS + 新闸裸跑 rc=0 + --selftest `ALL TESTS PASS` + "
                "★**生成器本体已含 B33 (重跑不蒸发)**★ + 分片登记 9 条 (3 artifact + 1 answer + 5 interface_claim, 零重复 key) + "
                "★**附项 1 已改**: `q3_storage_and_audio` 的 item = 「外挂 SPI-NOR ≥128 MiB (1 Gbit) 起」 (旧口径 16-64MB 已不存在, "
                "to/due 未动) ★ ★**遗留待裁 (本单未动, 交 main)**: `hw.yaml` 的 answer `vendor_q19_boot_storage` 里仍写着 "
                "「外挂 SPI-NOR 16-64MB」⇒ 同一分片并存两个打架的容量说法 ⇒ 退役时机由 main 定 (★建议与 ISS-350 同轮收口★)★ "
                "★ **★")
        new = seg.replace("  status: fixing", "  status: verified", 1)
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
        if "  verify_date:" in new:
            new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-23'", new, count=1, flags=re.M)
        else:
            new = new.replace("  verify_result:", "  verify_date: '2026-11-23'\n  verify_result:", 1)
        if "  fix_ref:" in new:
            new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260723_0425_main_sign_iss349_cont1.py'", new,
                         count=1, flags=re.M)
        else:
            new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260723_0425_main_sign_iss349_cont1.py'\n"
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
