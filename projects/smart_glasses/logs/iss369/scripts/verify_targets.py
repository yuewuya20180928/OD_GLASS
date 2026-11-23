#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 cont1 · 目标 lib:name 逐个独立复核 (★只读·不写板★)

复核四件事 (★不采信 targets186.json 自述·全部重新从盘上文件算★):
  ① 逐个 `test -f` 验【封装文件】(.kicad_mod) 真的在盘 (不是只验库目录)
  ② 重算 md5 并与台账值比对
  ③ 重新解析 .kicad_mod 的焊盘数, 与板面该封装焊盘数比对
  ④ 从 ISS-364 §1 的 markdown 表**独立抽表**, 与本单目标 lib:name 对账

产出: logs/iss369/20_target_verify.json
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
OUT = os.path.join(ROOT, "logs", "iss369", "20_target_verify.json")
T186 = os.path.join(ROOT, "tmp", "iss369", "targets186.json")
WP364 = os.path.join(ROOT, "HW", "PCB", "FP_TRUTH_LAND_SWAP_WORKPACKET.md")


def blocks(text, name):
    out = []
    i = 0
    while True:
        m = re.search(r"\(%s\b" % re.escape(name), text[i:])
        if not m:
            break
        s = i + m.start()
        depth = 0
        j = s
        while j < len(text):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(text[s:j + 1])
        i = j + 1
    return out


def mod_pads_n(path):
    t = open(path, encoding="utf-8").read()
    return len(blocks(t, "pad"))


def parse_iss364():
    """★从 ISS-364 §1 markdown 表独立抽 (ref -> lib:name, path, md5)★"""
    txt = open(WP364, encoding="utf-8").read()
    sec = txt.split("## §1 ")[1].split("## §2 ")[0]
    out = {}
    for ln in sec.splitlines():
        if not ln.startswith("| `"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        ref = cells[0].strip("`")
        m = re.search(r"`([^`]+:[^`]+)`", cells[3])
        if not m:
            continue
        libname = m.group(1)
        mp = re.search(r"`([A-Za-z0-9_]+\.pretty/[A-Za-z0-9_.+-]+\.kicad_mod)`\s*md5\s*`([0-9a-f]{32})`",
                       cells[4])
        out[ref] = {"libname": libname,
                    "path": mp.group(1) if mp else "",
                    "md5": mp.group(2) if mp else ""}
    return out


def main():
    rows = json.load(open(T186, encoding="utf-8"))
    wp = parse_iss364()
    res = {"libroot": LIBROOT,
           "libroot_exists": os.path.isdir(LIBROOT),
           "pretty_dirs": len([d for d in os.listdir(LIBROOT) if d.endswith(".pretty")]),
           "kicad_mod_files": sum(
               1 for _ in subprocess.run(
                   ["find", LIBROOT, "-name", "*.kicad_mod", "-type", "f"],
                   capture_output=True, text=True).stdout.splitlines()),
           "iss364_rows_parsed": len(wp),
           "checks": [], "n_write": 0, "n_write_pass": 0,
           "n_notwrite": 0, "mismatch": [], "iss364_diff": []}

    for r in rows:
        if r["action"] != "写":
            res["n_notwrite"] += 1
            continue
        res["n_write"] += 1
        libname = r["target_libname"]
        lib, nm = libname.split(":", 1)
        rel = "%s.pretty/%s.kicad_mod" % (lib, nm)
        abs_p = os.path.join(LIBROOT, rel)
        exists = os.path.isfile(abs_p)
        md5 = hashlib.md5(open(abs_p, "rb").read()).hexdigest() if exists else ""
        pads = mod_pads_n(abs_p) if exists else -1
        ok = (exists and md5 == r["lib_md5"] and rel == r["lib_path"]
              and pads == r["lib_pads_n"])
        rec = {"ref": r["ref"], "libname": libname, "rel": rel,
               "test_f": exists, "md5": md5, "md5_ledger": r["lib_md5"],
               "md5_match": md5 == r["lib_md5"],
               "pads_in_mod": pads, "pads_ledger": r["lib_pads_n"],
               "pads_match": pads == r["lib_pads_n"],
               "board_pads_n": r["board_pads_n"],
               "pad_count_board_vs_mod": pads == r["board_pads_n"],
               "reason_code": r["reason_code"], "ok": ok}
        res["checks"].append(rec)
        if not ok:
            res["mismatch"].append(rec)

    # ---- 与 ISS-364 §1 对账 (只看 90 件 R90) ----
    r90 = [r for r in rows if r.get("reason_code") == "R90"]
    for r in r90:
        w = wp.get(r["ref"])
        if not w:
            res["iss364_diff"].append({"ref": r["ref"], "why": "ISS-364 §1 表里没有这一行"})
            continue
        if w["libname"] != r["target_libname"]:
            res["iss364_diff"].append({"ref": r["ref"], "iss364": w["libname"],
                                       "iss369": r["target_libname"], "why": "lib:name 不一致"})
        elif w["md5"] and w["md5"] != r["lib_md5"]:
            res["iss364_diff"].append({"ref": r["ref"], "iss364_md5": w["md5"],
                                       "iss369_md5": r["lib_md5"], "why": "md5 不一致"})

    res["n_write_pass"] = sum(1 for c in res["checks"] if c["ok"])
    res["n_r90"] = len(r90)
    res["r90_iss364_aligned"] = len(r90) - len(res["iss364_diff"])
    json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("=== 目标 lib:name 逐个独立复核 ===")
    print(" 库根 %s" % res["libroot"])
    print(" .pretty 库目录 = %d  · .kicad_mod 封装文件 = %d"
          % (res["pretty_dirs"], res["kicad_mod_files"]))
    print(" 要写的件 = %d  · test -f + md5 + 焊盘数 全过 = %d  · 不过 = %d"
          % (res["n_write"], res["n_write_pass"], len(res["mismatch"])))
    print(" 不写的件 = %d" % res["n_notwrite"])
    print(" 90 件与 ISS-364 §1 表对账: %d/%d 一致" % (res["r90_iss364_aligned"], res["n_r90"]))
    if res["mismatch"]:
        print(" ★不过明细:")
        for m in res["mismatch"][:20]:
            print("   ", json.dumps(m, ensure_ascii=False))
    if res["iss364_diff"]:
        print(" ★与 ISS-364 不一致:")
        for m in res["iss364_diff"][:20]:
            print("   ", json.dumps(m, ensure_ascii=False))
    # 焊盘数与板面不一致的件 (★换 land 会改变焊盘数的那几件★)
    diff = [c for c in res["checks"] if not c["pad_count_board_vs_mod"]]
    print(" 板面焊盘数 != 目标件焊盘数 的件 = %d:" % len(diff))
    for c in diff:
        print("   %-16s 板 %d 脚 -> 目标 %d 脚 (%s)"
              % (c["ref"], c["board_pads_n"], c["pads_in_mod"], c["libname"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
