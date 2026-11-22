#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/iq_coverage_check.py — rkaiq 公开 IQ 文件「现成覆盖表」机检器 (ISS-139)
=================================================================================
目的: 把「rkaiq 公开 iqfiles 里到底哪些 sensor 有现成 IQ」从**散文断言**变成
      **机器可复核的表** —— 回答 `SW/DEMO_OD_PIPELINE_SPEC.md` §7 附录 A 的
      **P2-2 待办**: 「rkaiq 公开 iqfiles 里 imx415 / ov02b10 的具体文件与适用版本」。

★铁律 (SOUL.md / 本单边界):
  1. **只读本机快照** `HW/_os_snapshots/rkaiq_iqfiles.json` —— **本脚本不联网**。
     (本单明确: 不许联网重抓当新证据)
  2. **不编版本号**: 快照是**扁平 basename 清单**(生成器 `HW/open_source_rank.py`
     写的是 `t["path"].split("/")[-1]`) ⇒ **目录上下文 (isp3x / isp32 / ...) 已丢失**
     ⇒ 快照里查不到的版本一律标 **[0数据]**, 只有**本机既有实测记录**明确写过的
     文件才给目录归属 (逐条标出处)。
  3. 板端相关一律 [0数据] (Radxa 板不可达) —— 本脚本不涉及板端。

用法:
    python3 SW/tools/iq_coverage_check.py             # 核对 + 打覆盖表 (rc=0 全过 / 1 有项不过)
    python3 SW/tools/iq_coverage_check.py --self-test  # 正向 + 反向用例 (rc=0 = 反向用例确实变红)
    python3 SW/tools/iq_coverage_check.py --json      # 机读输出
    python3 SW/tools/iq_coverage_check.py --snapshot <path>   # 换快照 (核对别处导出的清单)

★"适用版本"这一列的口径:
    快照本体 → [0数据] (扁平化丢目录)
    本机既有实测记录 → [实测·本机记录] (出处逐条列在 ATTESTED_SRC)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # .../SW/tools
PROJ = os.path.dirname(os.path.dirname(HERE))              # .../<项目库根>
SNAP_DEFAULT = os.path.join(PROJ, "HW", "_os_snapshots", "rkaiq_iqfiles.json")

# ---------------------------------------------------------------------------
# 候选 sensor 名单 (来自 `HW/OPEN_SOURCE_AVAILABILITY.md` §3.3 原文 + 本单派单)
#   §3.3 原文: "rkaiq 公开 iqfiles/isp3x 与 isp32 目录里, ov04c10 与 ar0234 都没有
#              (有的是 imx415 / imx327 / imx464 / os04a10 / ov02b10 / gc8034 / sc200ai 等)"
# ---------------------------------------------------------------------------
CANDIDATES = [
    # (sensor token, 期望有没有 IQ 文件, 期望的证据出处)
    ("imx415",   True,  "HW/OPEN_SOURCE_AVAILABILITY.md §3.3 (有) + HW/IMX415_DEMO_SENSOR_FACTS.md §3.1"),
    ("imx327",   True,  "HW/OPEN_SOURCE_AVAILABILITY.md §3.3 (有)"),
    ("imx464",   True,  "HW/OPEN_SOURCE_AVAILABILITY.md §3.3 (有)"),
    ("os04a10",  True,  "HW/OPEN_SOURCE_AVAILABILITY.md §3.3 (有)"),
    ("ov02b10",  True,  "HW/OPEN_SOURCE_AVAILABILITY.md §3.3 (有) + HW/AR0234CS_RK3572_PORT_SPEC.md:200"),
    ("gc8034",   True,  "HW/OPEN_SOURCE_AVAILABILITY.md §3.3 (有)"),
    ("sc200ai",  True,  "HW/OPEN_SOURCE_AVAILABILITY.md §3.3 (有)"),
    ("ar0234",   False, "HW/OPEN_SOURCE_AVAILABILITY.md §3.3 (无) = ISS-139 的核心断言"),
    ("ov04c10",  False, "HW/OPEN_SOURCE_AVAILABILITY.md §3.3 (无) = ISS-139 的核心断言"),
]

# rkaiq iqfiles 下的 ISP 代目录 (本机快照实测条目; 注意 doc 里写 "6 个" 但只列了 5 个)
ISP_GEN_DIRS = ["isp20", "isp21", "isp32", "isp32_lite", "isp3x"]

# ---------------------------------------------------------------------------
# 目录归属 (适用版本) 的**本机既有实测记录**转录 —— 不是本单联网拉的
#   出处 A: HW/IMX415_DEMO_SENSOR_FACTS.md §3.1 表 (E5: "rkaiq IQ 仓库整树" 实拉 2551 项)
#   出处 B: HW/AR0234CS_RK3572_PORT_SPEC.md §2 §C6/§(isp3x 10 个 .json) 实拉记录
# 规则: 只登记**本机文档里逐字写明**了目录的文件; 其余一律 [0数据]。
# ---------------------------------------------------------------------------
ATTESTED_DIR = {
    # file name                                  : (目录, 出处代号)
    "imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json":     ("isp3x", "A"),
    "imx415_YT-RK415-V1_IR0147-60IRC-8M-F20.xml":         ("isp20", "A"),
    "imx415_YT10092_IR0147-28IRC-8M-F20.xml":             ("isp20", "A"),
    "imx415_YT10092_IR0147-28IRC-8M-F20-hdr3.xml":        ("isp20", "A"),
    "imx415_YT10092_IR0147-36IRC-8M-F20.xml":             ("isp20", "A"),
    "imx415_YT10092_IR0147-36IRC-8M-F20-hdr3.xml":        ("isp20", "A"),
    "imx415_YT10092_IR0147-60IRC-8M-F20.xml":             ("isp20", "A"),
    "imx415_YT10092_IR0147-60IRC-8M-F20-hdr3.xml":        ("isp20", "A"),
    "ov02b10_default_default.json":                       ("isp3x", "B"),
}
ATTESTED_SRC = {
    "A": "HW/IMX415_DEMO_SENSOR_FACTS.md §3.1 (E5 实拉 rkaiq 整树 2551 项)",
    "B": "HW/AR0234CS_RK3572_PORT_SPEC.md §2/§C6 (实拉 rkaiq 整树, isp3x 共 10 个 .json)",
}

# mesh (LSC 网格) 目录 —— 文件名锁死分辨率, 是 "现成 IQ 不能直接用" 的根因
MESH_DIRS = [
    "FEC_mesh_3840_2160_imx415_3.6mm",
    "LDCH_mesh_3840_2160_imx415_3.6mm",
    "FEC_mesh_2688_1520_imx347_4IR",
    "FEC_mesh_2688_1520_os04a10_4IR",
    "FEC_mesh_2688_1520_os04a10_6IR",
    "LDCH_mesh_2688_1520_imx347_4IR",
    "LDCH_mesh_2688_1520_os04a10_4IR",
    "LDCH_mesh_2688_1520_os04a10_6IR",
]


class CheckError(Exception):
    pass


def load_snapshot(path: str) -> list:
    if not os.path.exists(path):
        raise CheckError("快照不存在: %s" % path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise CheckError("快照格式不对 (顶层不是 list): %s" % path)
    bad = [x for x in data if not isinstance(x, str)]
    if bad:
        raise CheckError("快照里有非字符串条目: %r" % bad[:3])
    return data


def is_iq_file(name: str) -> bool:
    """IQ 文件 = 带 .json/.xml 扩展名的条目; 无扩展名的是目录条目 (模块/镜头目录)。"""
    return name.lower().endswith((".json", ".xml"))


def sensor_hits(names: list, token: str) -> tuple:
    """→ (iq 文件列表, 目录条目列表)

    ★匹配口径: **前缀匹配** (`^token`, 忽略大小写), 不要求后面紧跟分隔符 ——
      理由: rkaiq 的 IQ 命名规则是 `<sensor名>_<module>_<lens>.(json|xml)`,
      而**我们自己将来要产出的文件叫 `ar0234cs_<module>_<lens>.json`**
      (`HW/AR0234CS_RK3572_PORT_SPEC.md` C6) ⇒ 严格分隔符匹配会漏掉 `ar0234cs_*`。
    """
    pat = re.compile(r"^%s" % re.escape(token), re.IGNORECASE)
    files, dirs = [], []
    for n in names:
        if not pat.match(n):
            continue
        (files if is_iq_file(n) else dirs).append(n)
    return sorted(files), sorted(dirs)


def sensor_related(names: list, token: str) -> list:
    """含 token 但不以 token 开头的条目 (CAC_/FEC_mesh_/LDCH_mesh_ 之类) —— 旁证, 不算 IQ 文件。"""
    pat = re.compile(r"^%s" % re.escape(token), re.IGNORECASE)
    hit = re.compile(r"%s" % re.escape(token), re.IGNORECASE)
    return sorted(n for n in names if hit.search(n) and not pat.match(n))


def version_of(name: str) -> tuple:
    """→ (目录/适用版本, 证据等级)"""
    if name in ATTESTED_DIR:
        d, src = ATTESTED_DIR[name]
        return d, "[实测·本机记录(%s)]" % src
    return "[0数据]", "[0数据]"      # 快照扁平化 ⇒ 目录上下文丢失


def build_rows(names: list) -> list:
    rows = []
    for token, expect, src in CANDIDATES:
        files, dirs = sensor_hits(names, token)
        rows.append({
            "sensor": token,
            "expect_has_iq": expect,
            "source": src,
            "iq_files": files,
            "iq_file_count": len(files),
            "dir_entries": dirs,
            "related_entries": sensor_related(names, token),
            "has_iq": len(files) > 0,
            "files_detail": [
                {
                    "name": f,
                    "format": f.rsplit(".", 1)[-1].lower(),
                    "version": version_of(f)[0],
                    "evidence": version_of(f)[1],
                }
                for f in files
            ],
        })
    return rows


def check(names: list) -> list:
    """返回 [(name, ok, detail), ...] —— 只做**可机器判定**的断言。"""
    res = []
    rows = build_rows(names)

    # --- J1: 每个候选 sensor 的"有没有 IQ"必须与文档断言一致 -----------------
    for r in rows:
        ok = (r["has_iq"] == r["expect_has_iq"])
        res.append((
            "J1:%s" % r["sensor"],
            ok,
            "期望有=%s 实测有=%s (命中 IQ 文件 %d 个, 目录条目 %d 个)"
            % (r["expect_has_iq"], r["has_iq"], r["iq_file_count"], len(r["dir_entries"])),
        ))

    # --- J2: ISS-139 的核心断言必须成立: ar0234 / ov04c10 命中数 = 0 --------
    for tok in ("ar0234", "ov04c10"):
        files, dirs = sensor_hits(names, tok)
        res.append((
            "J2:%s=0" % tok,
            (len(files) == 0 and len(dirs) == 0),
            "ar0234/ov04c10 在 rkaiq 公开 iqfiles 里必须 0 命中 (实测: 文件 %d, 目录 %d)"
            % (len(files), len(dirs)),
        ))

    # --- J3: ISP 代目录条目必须齐全 (isp3x = RK3572 用) --------------------
    present = [d for d in ISP_GEN_DIRS if d in names]
    res.append((
        "J3:isp-gen-dirs",
        sorted(present) == sorted(ISP_GEN_DIRS),
        "ISP 代目录条目: %s (期望 %s)" % (present, ISP_GEN_DIRS),
    ))
    res.append((
        "J3b:isp3x-present",
        "isp3x" in names,
        "isp3x (RK3572 ISP3 代) 目录条目必须在快照里",
    ))

    # --- J4: 命名规则 <sensor>_<module>_<lens>.<json|xml> ------------------
    named = [n for n in names if is_iq_file(n) and re.match(r"^[a-z0-9]+_[^_]+_.+\.(json|xml)$", n, re.I)]
    res.append((
        "J4:naming-rule",
        len(named) >= 3,
        "符合 <sensor>_<module>_<lens>.(json|xml) 的条目 %d 个 (期望 >=3, 实证 3 例见 AR0234CS 规格 C6)" % len(named),
    ))

    # --- J5: 本机既有实测记录的目录归属必须都还在快照里 (attested ⊆ snapshot)
    missing = [f for f in ATTESTED_DIR if f not in names]
    res.append((
        "J5:attested-subset",
        not missing,
        "本机既有记录里登记了 %d 个带目录归属的文件, 快照缺失 %d 个 %s"
        % (len(ATTESTED_DIR), len(missing), missing[:3]),
    ))

    # --- J6: mesh (LSC) 目录必须在快照里 (现成 IQ 的分辨率绑定证据) --------
    mesh_hits = [m for m in MESH_DIRS if m in names]
    res.append((
        "J6:mesh-dirs",
        len(mesh_hits) >= 2,
        "mesh 目录命中 %d 个 (期望 >=2, 用于证明 'mesh 文件名锁死分辨率')" % len(mesh_hits),
    ))
    return res


# ---------------------------------------------------------------------------
# 表格输出
# ---------------------------------------------------------------------------
def print_table(names: list) -> None:
    rows = build_rows(names)
    print("┌─ rkaiq 公开 IQ 覆盖表 (数据源: %s · %d 项)" % (
        os.path.relpath(SNAP_DEFAULT, PROJ), len(names)))
    print("│   ★'适用版本'列: 快照本体是**扁平 basename 清单** ⇒ 目录上下文已丢 ⇒")
    print("│   只有本机既有实测记录写明的才给目录, 其余标 [0数据] (不猜)")
    print("└─" + "─" * 68)
    print()
    print("%-10s %-6s %-5s %s" % ("sensor", "有IQ?", "文件数", "具体文件 (格式 / 适用版本 / 证据)"))
    print("-" * 96)
    for r in rows:
        print("%-10s %-6s %-5d" % (r["sensor"], "✔ 有" if r["has_iq"] else "✘ 无", r["iq_file_count"]))
        if not r["files_detail"]:
            print("            └─ (无命中) ⇒ ★必须自己做 ISP tuning (ISS-139 立项对象)")
        for f in r["files_detail"]:
            print("            ├─ %s  [%s]  %s  %s" % (f["name"], f["format"], f["version"], f["evidence"]))
        if r["dir_entries"]:
            print("            ├─ 目录条目(非 IQ 文件): %s" % ", ".join(r["dir_entries"]))
        if r["related_entries"]:
            print("            └─ 相关条目(CAC/mesh, 不算 IQ 文件): %s" % ", ".join(r["related_entries"]))
    print()
    print("★ 结论 (本机快照实测):")
    for r in rows:
        if r["expect_has_iq"] and not r["has_iq"]:
            print("   ✘ %-9s 文档说有、快照里没有 ⇒ 快照与文档冲突, 必须复核" % r["sensor"])
    no_iq = [r["sensor"] for r in rows if not r["has_iq"]]
    yes_iq = [r["sensor"] for r in rows if r["has_iq"]]
    print("   ✔ 有现成 IQ (%d): %s" % (len(yes_iq), ", ".join(yes_iq)))
    print("   ✘ 无现成 IQ (%d): %s  ⇒ ★这两颗必须自己做 tuning" % (len(no_iq), ", ".join(no_iq)))
    print()
    print("★ mesh (LSC 网格) 目录 —— 文件名锁死分辨率 ⇒ 现成 IQ 不能直接搬到别的档位:")
    for m in MESH_DIRS:
        if m in names:
            print("   - %s  [实测·本机快照]" % m)
    print()
    print("★ 已知文档不一致 (点出来, 不静默取其一):")
    print("   - `HW/AR0234CS_RK3572_PORT_SPEC.md:277` 写 'iqfiles/ 下有 **6 个** ISP 代目录: "
          "isp20 / isp21 / isp32 / isp32_lite / isp3x' —— ★**文中只列了 5 个**, "
          "本机快照实测也是 **5 个** ⇒ 按 5 个记 (以快照为准)")


def print_checks(res: list) -> None:
    print("── 判据 ──")
    for name, ok, detail in res:
        print("  [%s] %-24s %s" % ("PASS" if ok else "FAIL", name, detail))


# ---------------------------------------------------------------------------
# 自检 (含反向用例: 改坏判据必须变红)
# ---------------------------------------------------------------------------
def selftest() -> int:
    names = load_snapshot(SNAP_DEFAULT)
    print("[selftest] 快照: %s (%d 项)" % (os.path.relpath(SNAP_DEFAULT, PROJ), len(names)))

    # --- 正向: 真实快照必须全过 ---
    base = check(names)
    nfail = sum(1 for _, ok, _ in base if not ok)
    print("[selftest] 正向: %d/%d 项通过 (期望全过)" % (len(base) - nfail, len(base)))
    if nfail:
        for name, ok, detail in base:
            if not ok:
                print("   FAIL %s: %s" % (name, detail))
        print("[selftest] ✘ 正向用例就红了 ⇒ 判据本身有问题, 退出非 0")
        return 1

    # --- 反向: 逐个把快照副本改坏, 对应判据必须变红 ---
    def find(sub):
        for name, ok, _ in base:
            if name.startswith(sub):
                return name
        return None

    cases = []

    # R1: 往快照里塞一个 ar0234 的 IQ ⇒ "ar0234 无 IQ" 必须变红
    r1 = sorted(names + ["ar0234cs_default_default.json"])
    c1 = check(r1)
    cases.append(("R1 注入 ar0234cs IQ ⇒ J1:ar0234 / J2:ar0234=0 必须红",
                  all(not ok for name, ok, _ in c1 if name in ("J1:ar0234", "J2:ar0234=0"))))

    # R2: 删掉全部 imx415 ⇒ J1:im415 必须红
    r2 = [n for n in names if not n.lower().startswith("imx415")]
    c2 = check(r2)
    cases.append(("R2 删掉全部 imx415 条目 ⇒ J1:imx415 必须红",
                  (not dict((n, ok) for n, ok, _ in c2)["J1:imx415"])
                  and (not dict((n, ok) for n, ok, _ in c2)["J5:attested-subset"])))

    # R3: 删掉 isp3x 目录条目 ⇒ J3:isp-gen-dirs / J3b 必须红
    r3 = [n for n in names if n != "isp3x"]
    c3 = check(r3)
    d3 = dict((n, ok) for n, ok, _ in c3)
    cases.append(("R3 删掉 isp3x 目录条目 ⇒ J3:isp-gen-dirs 与 J3b:isp3x-present 必须红",
                  (not d3["J3:isp-gen-dirs"]) and (not d3["J3b:isp3x-present"])))

    # R4: 删掉被登记了目录归属的 imx415 isp3x 文件 ⇒ J5 必须红
    key = "imx415_CMK-OT2022-PX1_IR0147-50IRC-8M-F20.json"
    r4 = [n for n in names if n != key]
    c4 = check(r4)
    cases.append(("R4 删掉 '%s' ⇒ J5:attested-subset 必须红" % key,
                  (not dict((n, ok) for n, ok, _ in c4)["J5:attested-subset"])))

    print("[selftest] 反向用例 (期望每个都 '确实变红' —— rc=0 表示反向用例通过):")
    bad = 0
    for desc, caught in cases:
        print("   [%s] %s" % ("OK" if caught else "BAD", desc))
        if not caught:
            bad += 1
    if bad:
        print("[selftest] ✘ %d 个反向用例没被抓住 ⇒ 判据太松, 退出非 0" % bad)
        return 1
    print("[selftest] ✔ 正向 %d/%d + 反向 %d/%d 全部通过" % (len(base), len(base), len(cases), len(cases)))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="rkaiq 公开 IQ 覆盖表机检器 (ISS-139)")
    ap.add_argument("--self-test", action="store_true", help="正向 + 反向用例 (rc=0)")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--snapshot", default=None, help="换一份快照 (默认本机 %s)" % SNAP_DEFAULT)
    a = ap.parse_args()

    if a.self_test:
        return selftest()

    path = a.snapshot or SNAP_DEFAULT
    try:
        names = load_snapshot(path)
    except CheckError as e:
        print("[err] %s" % e, file=sys.stderr)
        return 2

    res = check(names)
    nfail = sum(1 for _, ok, _ in res if not ok)
    if a.json:
        print(json.dumps({
            "snapshot": os.path.relpath(path, PROJ),
            "snapshot_items": len(names),
            "rows": build_rows(names),
            "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in res],
            "failed": nfail,
        }, ensure_ascii=False, indent=1))
    else:
        print_table(names)
        print()
        print_checks(res)
        print()
        print("==> %d/%d 项通过, %d 项失败" % (len(res) - nfail, len(res), nfail))
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
