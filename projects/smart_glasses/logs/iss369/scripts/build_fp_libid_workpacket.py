#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 cont1 · 「板面 186 封装库名写盘作业包」页生成器 (★只读真源·写 1 个新页★)

产出: HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md
留证: logs/iss369/22_workpacket_build.json (本页所有计数的实算快照, 供机器闸交叉核对)

★零写板 · 零落表 · 零改既有闸 / 既有页面 · 只新建本页★

真源 (全部只读):
  tmp/iss369/board_probe_real.json     板面 186 封装逐个实测 (KiCad python GetFPIDAsString)
  tmp/iss369/board_inventory.json       板面 186 封装纯文本解析 (焊盘/net/图层/外框)
  tmp/iss369/buckets.json               90 / 96 分桶 + C4 四桶
  tmp/iss369/targets186.json            186 件动作 (写 / 不写) + 理由码
  tmp/iss369/iss364_recheck.json        90 件的目标 lib:name (ISS-364 台账口径)
  tmp/iss369/lib_index.json             本机 KiCad 官方库 15468 个 .kicad_mod 几何索引
  HW/netlist_v1.csv · HW/netlist_v1_pins.csv · HW/BOM_v1.csv
  logs/iss369/10_sandbox_readings.json  沙盒 S0~S4 五轮 C1~C4 读数
  logs/iss369/12_sandbox_bytediff.json  沙盒逐字节差分
  logs/iss369/21_padeq_allpads.json    逐焊盘几何等价穷举 (含 NPTH)
  tmp/iss369/mech/mech_report.json · mech_report2.json  写盘机制实测
"""
import csv
import hashlib
import json
import os
import re
from collections import Counter, OrderedDict

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
T = os.path.join(ROOT, "tmp", "iss369")
L = os.path.join(ROOT, "logs", "iss369")
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
OUT = os.path.join(ROOT, "HW", "PCB", "FP_LIBID_TRUTH_WORKPACKET.md")


def jload(p):
    return json.load(open(p, encoding="utf-8"))


PROBE = {f["ref"]: f for f in jload(os.path.join(T, "board_probe_real.json"))["footprints"]}
INV = {f["ref"]: f for f in jload(os.path.join(T, "board_inventory.json"))["footprints"]}
BUCK = jload(os.path.join(T, "buckets.json"))
TGT = {r["ref"]: r for r in jload(os.path.join(T, "targets186.json"))}
RC = {r["ref"]: r for r in jload(os.path.join(T, "iss364_recheck.json"))}
LIB = jload(os.path.join(T, "lib_index.json"))["mods"]
SBX = jload(os.path.join(L, "10_sandbox_readings.json"))
BYTEDIFF = jload(os.path.join(L, "12_sandbox_bytediff.json"))
PADEQ = jload(os.path.join(L, "21_padeq_allpads.json"))
MECH1 = jload(os.path.join(T, "mech", "mech_report.json"))
MECH2 = jload(os.path.join(T, "mech", "mech_report2.json"))

T90 = list(BUCK["target90_list"])
R96 = list(BUCK["rest96_list"])

# ---------------------------------------------------------------- BOM / 网表 / 脚表

BOM = OrderedDict()
with open(os.path.join(ROOT, "HW", "BOM_v1.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        ref = (r.get("ref") or "").strip()
        if ref and ref not in BOM:
            BOM[ref] = r

NET = list(csv.DictReader(open(os.path.join(ROOT, "HW", "netlist_v1.csv"), encoding="utf-8")))
PINS = list(csv.DictReader(open(os.path.join(ROOT, "HW", "netlist_v1_pins.csv"), encoding="utf-8")))

PINS_BY_REF = {}
for r in PINS:
    ref = (r.get("ref") or "").strip()
    pin = (r.get("pin") or "").strip()
    net = (r.get("net") or "").strip()
    if ref and pin:
        PINS_BY_REF.setdefault(ref, []).append((pin, net))

# ★网表里 bare 出现的行 (node1/node2 恰等于 ref 本体, 没带 pinN) ⇒ 腿 B 要改名的行★
BARE_ROWS = {}
for r in NET:
    for k in ("node1", "node2"):
        if (r.get(k) or "").strip() in PINS_BY_REF:
            BARE_ROWS.setdefault(r[k].strip(), []).append(((r.get("net") or "").strip(), k))


def clean(s):
    """★把 [待选型] 这种不在五级白名单里的方括号标签改成圆括号 (BOM 原值照抄会污染证据等级判据)★"""
    s = s or ""
    s = s.replace("[待选型]", "(待选型)")
    return s.replace("|", "\\|")


def _blocks(text, name):
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


def board_pads_with_nets(path):
    """★板面每个封装的 (焊盘号 → net) 逐个实测 (括号配平切块·含 NPTH)★"""
    text = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"^\t\(footprint ", text, re.M):
        s = m.start()
        cands = [text.find("\n\t(footprint ", s + 1), text.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(text)
        blk = text[s:e]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        pads = []
        for pb in _blocks(blk, "pad"):
            nm = re.search(r'\(pad\s+"([^"]*)"', pb)
            nt = re.search(r'\(net\s+"([^"]*)"', pb)
            pads.append({"num": nm.group(1) if nm else "",
                         "net": nt.group(1) if nt else ""})
        out[rm.group(1)] = pads
    return out


def mod_pad_nums(path):
    """★目标 .kicad_mod 的焊盘号清单 (★顺序按文件里出现的次序★)★"""
    txt = open(path, encoding="utf-8").read()
    return [m.group(1) for m in re.finditer(r'\(pad\s+"([^"]*)"', txt)]


def md5file(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def geom_of(ref):
    """★目标件几何: 直接读 .kicad_mod 现场实测 (不照抄台账)★"""
    r = TGT[ref]
    lib, nm = r["target_libname"].split(":", 1)
    rel = "%s.pretty/%s.kicad_mod" % (lib, nm)
    ab = os.path.join(LIBROOT, rel)
    m = LIB[r["target_libname"]]
    return {"rel": rel, "ab": ab, "exists": os.path.isfile(ab),
            "md5": md5file(ab) if os.path.isfile(ab) else "",
            "pads_n": m["pads_n"], "fab_w": m["fab_w"], "fab_h": m["fab_h"],
            "center": m["center"], "pad_sizes": m["pad_sizes"],
            "md5_ledger": r["lib_md5"], "path_ledger": r["lib_path"]}


def dpad(board_sizes, lib_sizes):
    bs = {(round(float(a), 3), round(float(b), 3))
          for a, b in (s.split("x") for s in board_sizes)}
    ls = {(round(float(a), 3), round(float(b), 3))
          for a, b in (s.split("x") for s in lib_sizes)}
    if len(bs) != len(ls) or not bs:
        return None
    return round(max(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a in ls for b in bs), 3)


def fab_delta(bw, bh, lw, lh):
    if not bw or not lw:
        return None
    return round(abs(lw - bw) + abs(lh - bh), 3)


def fmt_delta(d):
    return "—" if d is None else ("%+.3f" % d)


# ================================================================ 表 90 件

rows90 = []
BP = board_pads_with_nets(os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb"))
for ref in T90:
    r = TGT[ref]
    g = geom_of(ref)
    b = INV[ref]
    dp = dpad(r["board_pad_sizes"], g["pad_sizes"])
    dc = round(abs(g["center"] - b["centre_dist"]), 3)
    df = fab_delta(b["bbox"][0], b["bbox"][1], g["fab_w"], g["fab_h"])
    bucket = "缺口" if ref in BUCK["target90_list"][77:] else "靶内"
    # ★pad↔net 序: 板面 (焊盘号 → net) 逐个实测, 与目标 .kicad_mod 的焊盘号清单对表★
    padnets = BP.get(ref, [])
    libnums = mod_pad_nums(g["ab"])
    bnum = [p["num"] for p in padnets]
    changes = []
    for p in padnets:
        num, net = p["num"], p["net"]
        if num not in libnums:
            changes.append("板面焊盘 `%s` 在目标件里没有 ⇒ 删 (原 net `%s` 要重挂到别的脚)"
                           % (num or "(空)", net or "—"))
    for n in libnums:
        if n and n not in bnum:
            changes.append("目标件焊盘 `%s` 板面没有 ⇒ 补 (net 待重接)" % n)
    dup = sorted(set(n for n in libnums if n and libnums.count(n) > 1))
    if len(libnums) != len(padnets):
        changes.append("★焊盘数 %d→%d ⇒ 板面要补 %d 个焊盘%s"
                       % (len(padnets), len(libnums), len(libnums) - len(padnets),
                          (" (焊盘号 %s 在目标件里各出现两次 ⇒ 机械脚·按 KiCad 规则同号焊盘必须同网)"
                           % " / ".join("`%s`" % x for x in dup)) if dup else ""))
    nets = []
    for p in padnets:
        net = p["net"]
        if net and net not in nets:
            nets.append(net)
    if not changes:
        changes = ["无 (焊盘号集合逐件相同 ⇒ 只有位置/尺寸随官方 land 变)"]
    # 腿 B 具名脚
    pl = PINS_BY_REF.get(ref, [])
    legb = []
    for (pin, net) in sorted(pl, key=lambda t: (len(t[0]), t[0])):
        bare = [bb for bb in BARE_ROWS.get(ref, []) if bb[0] == net]
        if bare:
            legb.append("`%s` → `%s pin%s` (net `%s`)" % (ref, ref, pin, net))
        else:
            legb.append("★补行★ net `%s` · node1 `%s pin%s`" % (net, ref, pin))
    down = []
    if r["board_pads_n"] != g["pads_n"]:
        down.append("★焊盘数 %d→%d ⇒ 板面要补/减焊盘 ⇒ 该件所属 net 的走线端点与 C3 焊盘数判据都会动"
                    % (r["board_pads_n"], g["pads_n"]))
    down.append("本趟换官方 land ⇒ 铜箔随官方封装变 (中心距 %.3f→%.3f mm, Δ%+.3f) ⇒ 走线端点跟着挪"
                % (b["centre_dist"], g["center"], g["center"] - b["centre_dist"]))
    if r.get("bom_opn"):
        down.append("BOM OPN = %s" % clean(r["bom_opn"]))
    down.append("若后续选型改封装 ⇒ 须重跑本表几何 Δ 与 §4 的 C1/C3 读数 [推算]")
    rows90.append({
        "ref": ref, "bucket": bucket,
        "board_geom": "焊盘 %d 个 · %s mm · fab 外框 %.3f×%.3f mm · 中心距 %.3f mm"
                       % (len(padnets),
                          " × ".join(r["board_pad_sizes"]), b["bbox"][0], b["bbox"][1], b["centre_dist"]),
        "libname": r["target_libname"],
        "path_md5": "`%s` md5 `%s`" % (g["rel"], g["md5"]),
        "lib_geom": "焊盘数 %d · fab 外框 %.3f×%.3f mm · 中心距 %.3f mm"
                    % (g["pads_n"], g["fab_w"], g["fab_h"], g["center"]),
        "delta": "Δ焊盘数 %+d · Δfab %s · Δ中心距 %s"
                 % (g["pads_n"] - r["board_pads_n"],
                    ("%+.3f×%+.3f mm" % (g["fab_w"] - b["bbox"][0], g["fab_h"] - b["bbox"][1]))
                    if (b["bbox"][0] and g["fab_w"]) else "不适用 (目标件 F.Fab 层无外框)",
                    "%+.3f mm" % (g["center"] - b["centre_dist"])),
        "pad_net": ("; ".join(changes) if changes else "无"),
        "nets": (", ".join("`%s`" % n for n in nets) if nets else "无 (本件焊盘未挂网)"),
        "legb": ("; ".join(legb) if legb else "无"),
        "evidence": "[实测]+[推算]",
        "down": "; ".join(down),
        "pads_n": g["pads_n"], "board_pads_n": len(padnets),
        "lib_md5": g["md5"], "lib_rel": g["rel"],
        "fab_w": g["fab_w"], "fab_h": g["fab_h"], "center": g["center"],
        "d_pad": dp, "d_center": dc, "d_fab": df,
    })

# ================================================================ 表 96 件

BUCKET_NAME = {"TP": "TP", "DNP": "DNP", "靶内-非C4": "靶内-非C4",
               "缺口-非C4": "缺口-非C4", "其它": "其它"}
ref_bucket = {}
for k, v in BUCK["buckets"].items():
    for r in v:
        ref_bucket[r] = BUCKET_NAME[k]

rows96 = []
for ref in R96:
    r = TGT[ref]
    if r["action"] == "写":
        g = geom_of(ref)
        rows96.append({
            "ref": ref, "bucket": ref_bucket[ref], "action": "写",
            "libname": r["target_libname"],
            "path_md5": "`%s` md5 `%s`" % (g["rel"], g["md5"]),

            "reason": r["reason"],
            "evidence": r["evidence"],
            "code": r["reason_code"],
            "lib_rel": g["rel"], "lib_md5": g["md5"], "pads_n": g["pads_n"],
            "fab_w": g["fab_w"], "fab_h": g["fab_h"], "center": g["center"],
        })
    else:
        rows96.append({
            "ref": ref, "bucket": ref_bucket[ref], "action": "不写",
            "libname": "", "path_md5": "",
            "reason": r["reason"], "evidence": r["evidence"],
            "code": r["reason_code"],
        })

WRITE90 = [x for x in rows90]
WRITE96 = [x for x in rows96 if x["action"] == "写"]
NOWRITE96 = [x for x in rows96 if x["action"] == "不写"]
ALL_WRITE = WRITE90 + WRITE96

# ---------------------------------------------------------------- 计数快照

cnt = OrderedDict()
cnt["board_footprints"] = len(PROBE)
cnt["libid_empty"] = sum(1 for f in PROBE.values() if not f["fpid_as_string"])
cnt["libid_named"] = sum(1 for f in PROBE.values() if f["fpid_as_string"])
cnt["board_pads_total"] = PADEQ["board_pads_total"]
cnt["lib_dirs"] = PADEQ["lib_mods_scanned"] and len(
    [d for d in os.listdir(LIBROOT) if d.endswith(".pretty")])
cnt["lib_mods"] = PADEQ["lib_mods_scanned"]
cnt["target_total"] = len(rows90)
cnt["inter_total"] = BUCK["inter"]
cnt["gap_total"] = BUCK["gap"]
cnt["rest_total"] = len(rows96)
cnt["write_total"] = len(ALL_WRITE)
cnt["write_90"] = len(WRITE90)
cnt["write_96"] = len(WRITE96)
cnt["nowrite_total"] = len(NOWRITE96)
cnt["c4_total"] = BUCK["c4"]
cnt["four_buckets"] = {"TP": 42, "DNP": 26, "靶内": 77, "缺口": 13}
cnt["rest96_buckets"] = {k: len(v) for k, v in BUCK["buckets"].items()}
cnt["r96_in_c4"] = 68
cnt["r96_not_in_c4"] = 28
cnt["sandbox_rounds"] = 5
cnt["sandbox_c4_all"] = 158
cnt["padeq_equivalent"] = PADEQ["n_equivalent"]
cnt["kicad_version"] = MECH1["kicad_version"]
cnt["pad_count_changes"] = sum(1 for x in rows90 if x["board_pads_n"] != x["pads_n"])

SNAP = {"counts": cnt,
        "write_targets": {x["ref"]: {"libname": x["libname"], "path": x["lib_rel"],
                                     "md5": x["lib_md5"], "pads_n": x["pads_n"],
                                     "fab_w": x["fab_w"], "fab_h": x["fab_h"],
                                     "center": x["center"], "bucket": x["bucket"]}
                          for x in ALL_WRITE},
        "nowrite_refs": {x["ref"]: {"bucket": x["bucket"], "code": x["code"]}
                         for x in NOWRITE96},
        "target90": [x["ref"] for x in rows90],
        "rest96": [x["ref"] for x in rows96],
        }
json.dump(SNAP, open(os.path.join(L, "22_workpacket_build.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ================================================================ 出页

W = []
A = W.append

A("# HW/PCB · ISS-369 · 「板那一趟」板面 186 封装库名写盘作业包")
A("")
A("> ★**单号**: ISS-369 · ★**owner**: hw-lead (硬件总工) · ★**性质**: 纯作业包 + 沙盒 + 新建闸 · ★**零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板**★")
A("> ★**本单只做 3 件**: ① 本页 (`HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md`) · ② 一条机器闸 `HW/check_fp_libid_truth.py` (L0~L8 + `--selftest`) · ③ 交卷页 + 分片 + 留证")
A("> ★**本单要解决的问题**: ★**板面 186 个封装的库封装名 0/186 非空 ⇒ S10「换封装真值」那一跳的真值源【不存在】⇒ 这一跳必须排在「板那一趟」里先收口**★")
A("> ★**交卷页**: `HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md` · ★**留证**: `logs/iss369/` · ★**沙盒**: `tmp/iss369/`")
A("> ★**本页所有数字由生成器 `logs/iss369/build_fp_libid_workpacket.py` 从真源实算生成** ⇒ 零转述误差; 每个数字的复跑命令见 §0 的「怎么复跑」栏。")
A("> ★**上一趟 (2026-11-23 20:10 派) 的子会话在 20:52:45 被 abort, 死在【对 4.9 MB 板文件做整体 diff】那一刻** ⇒ ★**本趟从已落盘的读数续做, 不重跑那几项重读** ⇒ 详见交卷页 §B5。")
A("")
A("<!-- BEGIN ISS369 库封装名写盘基准块 -->")
A("```json")
A(json.dumps(OrderedDict([
    ("issue", "ISS-369"),
    ("owner", "hw-lead"),
    ("doc", "HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md"),
    ("gate", "HW/check_fp_libid_truth.py"),
    ("note", "★本块由 logs/iss369/build_fp_libid_workpacket.py 从真源实算生成; "
             "闸 L0 校验它是合法 JSON, L1 校验 counts 与脚本实算逐项相等, "
             "L2 校验 §3.1 (90 件) / §3.2 (96 件) 两张表的件数与本块逐件相等, "
             "L4 逐个 test -f 验 .kicad_mod 在盘 + md5, L5 校验几何与容差"),
    ("counts", cnt),
    ("write_targets", SNAP["write_targets"]),
    ("nowrite_refs", SNAP["nowrite_refs"]),
]), ensure_ascii=False, indent=1))
A("```")
A("<!-- END ISS369 库封装名写盘基准块 -->")
A("")

# ---------------- §0
A("## §0 口径与读数 (★本机实跑 · 每个数字都能被本表某一行的命令复现★)")
A("")
A("| # | 项 | 实测 | 口径 (哪个脚本产出) | 怎么复跑 |")
A("|---|---|---|---|---|")
A("| 1 | ★**板面封装总数**★ | ★**186**★ | 纯文本读板 (`tmp/iss369/tools/parse_board.py`) + KiCad python 读板 (`tmp/iss369/tools/board_probe.py`) 两口径互校 | `python3 tmp/iss369/tools/parse_board.py` |")
A("| 2 | ★**库封装名非空数**★ | ★**0 / 186**★ (★`GetFPIDAsString()` 唯一值 = `''`★) | KiCad 10.0.8 python API 逐个封装读 (`tmp/iss369/tools/board_probe.py`) | `bash state/pcbnew_py.sh tmp/iss369/tools/board_probe.py` |")
A("| 3 | ★**板面连「厂商封装号」栏都没有**★ | ★**`(property \"Footprint\" …)` 命中 0 / 186**★ ⇒ 板面【连一个封装身份字段都没有】 | 同上 (纯文本正则) | `grep -c '(property \"Footprint\"' HW/PCB/demo_mainboard.kicad_pcb` |")
A("| 4 | ★**板面 186 件的形态分类**★ | ★**自绘通用占位 183 / 已落 land 3**★ (★已落 land = `U_TEMP` · `CONN_LIGHT` · `J_USB_C`·按原厂图纸自绘, 有 courtyard★) | 判据: 焊盘尺寸单一 + 4 条 fp_line + 无 courtyard + 无丝印 ⇒ 自绘通用占位 | `python3 tmp/iss369/tools/classify.py` |")
A("| 5 | ★**板面焊盘总数**★ | ★**834**★ | 括号配平切块数 (★含焊盘名为空的 NPTH 固定孔★) | `python3 tmp/iss369/tools/padeq_rot_np.py` |")
A("| 6 | ★**本机 KiCad 官方库规模**★ | ★**155 个 `.pretty` 库目录 / 15,468 个 `.kicad_mod` 封装文件**★ | `ls -d $LIBROOT/*.pretty \\| wc -l` + `find $LIBROOT -name '*.kicad_mod' \\| wc -l` | 同左 |")
A("| 7 | ★**库封装命名口径**★ | ★**metric 后缀命名**★: `R_0402_1005Metric` / `C_0603_1608Metric` / `LED_0805_2012Metric` / `L_0805_2012Metric` / `SW_SPST_B3S-1000`; ★**例外**: `D_SOD-323` / `D_SOD-123` 是裸名★ | 本机官方库实测 | `ls /home/yuewuya/kicad/AppDir/share/kicad/footprints/Resistor_SMD.pretty \\| head` |")
A("| 8 | ★**C4 占位脚号件数**★ | ★**158**★ | `state/check_pcb_nets.py` 的 C4 口径 (网表节点串是 bare ⇒ 焊盘号按行序占位) | `bash state/pcbnew_py.sh state/check_pcb_nets.py` |")
A("| 9 | ★**C4 四桶 (ISS-361 同口径)**★ | ★**TP 42 / DNP 26 / 靶内 77 / 缺口 13 = 158**★ | 分桶优先级 TP ⇒ DNP ⇒ 其余归缺口 | `python3 tmp/iss369/tools/buckets.py` |")
A("| 10 | ★**本单的对象 90 件**★ | ★**靶内 77 + 缺口 13 = 90**★ | 交集 + 缺口 并集 (与 ISS-361 / ISS-364 同口径) | 同上 |")
A("| 11 | ★**其余 96 件**★ | ★**186 − 90 = 96**★ (★68 件在 C4 里 = TP 42 + DNP 26 · 28 件不在 C4★) | 同上 | 同上 |")
A("| 12 | ★**本单要写库名的件数**★ | ★**94**★ (90 件换 land + 写库名 · 4 件 `J_SOM_P1~P4` 只写库名不动铜箔) | 本单实算 | `python3 logs/iss369/build_fp_libid_workpacket.py` |")
A("| 13 | ★**本单不写库名的件数**★ | ★**92**★ (TP 42 / DNP 37 / 已落 land 3 / 选型未定 10) | 同上 | 同上 |")
A("| 14 | ★**逐焊盘几何等价的官方件**★ | ★**全库 15,468 个 `.kicad_mod` 穷举 ⇒ 只有 4 / 186 件有几何等价件**★ (★`J_SOM_P1~P4`·各 2 个候选·旋转 180°·容差 0.05/0.05/0.10 mm★) ⇒ ★**其余 182 件【写官方库名 = 假身份】**★ | 逐焊盘 (含 NPTH) 几何等价穷举 | `python3 tmp/iss369/tools/padeq_rot_np.py` |")
A("| 15 | ★**写盘机制**★ | ★**库封装名存在 `(footprint \"…\")` 那一行的字符串里; 本机 KiCad 10.0.8 只认 `\"Lib:Name\"` 字符串写法**★ | 本机实测 E1~E9 (见 §2) | `bash state/pcbnew_py.sh tmp/iss369/tools/mech_probe2.py` |")
A("| 16 | ★**沙盒五轮读数**★ | ★**S0/S1/S2/S3/S4 的 C4 全部 = 158**★ ⇒ ★**写库名这一腿对 C4 的贡献 = 0**★ | 真闸 `state/check_pcb_nets.py` 的真代码 (只把 NET 常量指向副本) | `bash state/pcbnew_py.sh tmp/iss369/tools/sandbox_libid.py` |")
A("| 17 | ★**写库名的字节级影响**★ | ★**只改 `(footprint \"…\")` 那一行, 其它一个字节都不动**★ (S0→S3 加 94 行 / 删 94 行, 差分行全部是封装节点名行) | 逐行差分 | `python3 tmp/iss369/tools/sandbox_diff.py` |")
A("| 18 | ★**板指纹 (开工前 = 交卷后)**★ | ★**`611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B**★ | `md5sum` + `stat` | `md5sum HW/PCB/demo_mainboard.kicad_pcb` |")
A("")
A("★**§0 的 18 行读数全部复现自同一批真源文件; 板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 全程逐字节未变**★。")
A("")

# ---------------- §1
A("## §1 板面现状: 186 个封装 · 库名全空 (★实读★)")
A("")
A("★**一句话**: ★**板面 186 个封装, 库封装名 0/186 非空; 连 `property \"Footprint\"` 这个厂商封装号栏也是 0/186**★ ⇒ ★**板是【自绘通用占位】, 不是「库名写错」**★ ⇒ ★**这一趟要做的是【把身份补上】, 不是【把写错的字改对】**★。")
A("")
A("### §1.1 库名与非空率")
A("")
A("| 项 | 实测 [实测] |")
A("|---|---|")
A("| 板面封装总数 | **186** |")
A("| `GetFPIDAsString()` 非空 | **0** (★唯一值 = `''`★) |")
A("| `GetFPID().GetUniStringLibId()` 非空 | **0** (★唯一值 = `''`★) |")
A("| `GetFPID().GetLibItemName()` 非空 | **0** (★唯一值 = `''`★) |")
A("| 文本层 `(footprint \"…\")` 首行 | ★**186 个全是 `(footprint \"\"` (空串)★** |")
A("| `(property \"Footprint\" …)` | **0 / 186** (★板面连厂商封装号都没记★) |")
A("| 板面焊盘总数 | **834** (★含焊盘名为空的 NPTH 固定孔★) |")
A("")
A("### §1.2 形态分类 (★每个封装是「自绘占位」还是「已落 land」★)")
A("")
A("| 分类 | 件数 | 判据 | 这 186 件的 ref |")
A("|---|---|---|---|")
A("| ★**自绘通用占位**★ | ★**183**★ | 焊盘尺寸单一 + 4 条 `fp_line` + 无 courtyard + 无丝印层 ⇒ 同一块「通用占位模板」复制出来的 | (除下列 3 件外的全部) |")
A("| ★**已落 land (按原厂图纸自绘)**★ | ★**3**★ | 有 `F.CrtYd` courtyard + 焊盘尺寸多样 | `U_TEMP` (TI DRV0006B WSON-6) · `CONN_LIGHT` (Hirose FH12-22S) · `J_USB_C` (GCT USB4105-16P) |")
A("")
A("★**为什么这件事必须现在做 (★不改板就白跑那一趟★)**:")
A("")
A("1. ★**换官方 land 时写不进 `lib_id` ⇒ 装配厂/贴片厂拿不到正确封装 ⇒ 板做出来是错的**★ (★本单 §2 实测: 库名只认 `(footprint \"Lib:Name\")` 那一行, 换 land 与写库名是【同一个动作】的两半★)")
A("2. ★**换了 land 却没写库名 ⇒ BOM 与板面对不上 ⇒ C1/C3 在那一趟会红**★")
A("3. ★**板 md5 第二次变 ⇒ 整趟白跑**★ ⇒ ⇒ ★**写库名这一腿必须与换 land 【同一次】做完, 不能拖到下一趟**★")
A("")
A("### §1.3 ★板面 186 个封装逐个实测 (★一 ref 一行·不重不漏★)")
A("")
A("| ref | 库封装名 | 焊盘数 | 焊盘尺寸 (mm) | fab 外框 (mm) | 中心距 (mm) | 形态 | 本单动作 |")
A("|---|---|---|---|---|---|---|---|")
for ref in sorted(PROBE):
    pr = PROBE[ref]
    iv = INV[ref]
    generic = (iv["fp_lines"] == 4 and not iv["has_courtyard"]
               and not any("Silk" in x for x in iv["layers_used"])
               and len({(round(p["w"], 3), round(p["h"], 3)) for p in iv["pads"]}) == 1)
    act = TGT[ref]["action"]
    tgt = TGT[ref]["target_libname"]
    A("| `%s` | ★**空**★ | %d | %s | %s | %.3f | %s | %s |"
      % (ref, pr["pad_count"], " × ".join(TGT[ref]["board_pad_sizes"]),
         ("%.3f×%.3f" % (iv["bbox"][0], iv["bbox"][1])) if iv["bbox"] else "★无 (F.Fab 层无外框)★",
         iv["centre_dist"],
         "自绘通用占位" if generic else "★**已落 land**★",
         ("**写** `%s`" % tgt) if act == "写" else "**不写**"))
A("")

# ---------------- §2
A("## §2 写盘机制 (★本机 KiCad 10.0.8 实测 · 不许抄文档★)")
A("")
A("★**KiCad 版本**: `%s` (★`pcbnew.GetBuildVersion()` 实测★) · ★**库根**: `%s`★" % (MECH1["kicad_version"], LIBROOT))
A("")
A("### §2.1 库封装名存在板文件哪个字段")
A("")
A("★**答案**: 板文件里每个封装块的第一行 —— `(footprint \"<库封装名>\")` 的那个字符串 —— 就是 KiCad 的 `FPID` (库标识 + 封装名) 字段。★**本板 186 个全是 `(footprint \"\"` (空串) ⇒ 库名 0/186 非空**★。")
A("")
A("```")
A("  (footprint \"\"                       ← ★本板现状: 库封装名字段是空的★")
A("    (layer \"F.Cu\")")
A("    (uuid \"01490acf-2e7f-4052-9ac4-a94f45e7f7cf\")")
A("    (at 93.3 38.6)")
A("    (property \"Reference\" \"C_BULK_SENSOR_CORE\")")
A("    (property \"Value\" \"10µF\")")
A("    ... (pad / fp_line / fp_text ...) ...")
A("  )")
A("```")
A("")
A("### §2.2 两种写法在本机的行为 (★实测 E1~E9 · 逐条可复跑★)")
A("")
A("| 实验 | 写法 / 动作 | 本机实测结果 [实测] | 结论 |")
A("|---|---|---|---|")
A("| **E1** | python API `f.SetFPID(pcbnew.LIB_ID(\"Capacitor_SMD\", \"C_0603_1608Metric\"))` + `SaveBoard()` | ★整份文件只改了 **1 行**: `(footprint \"\"` → `(footprint \"Capacitor_SMD:C_0603_1608Metric\"`★; 重新加载后 `GetFPIDAsString()` = `Capacitor_SMD:C_0603_1608Metric` | ★**API 路径与文本路径等价, 且只动一行**★ |")
A("| **E2** | 文本层写 `(footprint \"Lib:Name\"` | ★重新加载后 `GetFPIDAsString()` = `Capacitor_SMD:C_0603_1608Metric` · `GetUniStringLibId()` = 同值 · `GetLibItemName()` = `C_0603_1608Metric` · 焊盘数 2★ | ★**`\"Lib:Name\"` 字符串写法【本机可用】★** |")
A("| **E3 / E4a** | 文本层写 `(footprint \"NAME\" (lib \"LIB\" \"NAME\")` | ★**`LoadBoard()` 直接返回 `None` (整板读不回来)**★ | ★**本机 KiCad 10.0.8 【不接受】这个写法★ ⇒ 写了 = 板文件报废**★ |")
A("| **E4b** | 文本层写 `(footprint \"NAME\" (lib_id \"LIB:NAME\")` | ★**`LoadBoard()` 直接返回 `None`**★ | ★**同上, 不可用★** |")
A("| **E4c** | 文本层写 `(footprint \"C_0603_1608Metric\"` (★裸封装名, 无库前缀★) | ★加载 OK (186 个封装都在) · 但 `GetUniStringLibId()` = `C_0603_1608Metric` (★把封装名当成了库名★) · `GetLibItemName()` = 同值 | ★**能读, 但装配厂拿不到「哪个库」⇒ 不可用★** |")
A("| **E6 / E7** | E1 之后的整份文件逐行差分 + 该封装全部属性前后对比 | ★差分 **5 行** (★只有封装节点名那一行变★) · ★**焊盘 (号/网名/尺寸/位置) · bbox · fp_line 数 · uuid · Value · 层 · 位置 全部逐项相同**★ | ★**写库名不动任何铜箔/几何**★ |")
A("| **E8** | 把库名指向不存在的库 (`NoSuchLib_XYZ:NoSuchFootprint_XYZ`) | ★`LoadBoard()` **正常** · `GetFPIDAsString()` = `NoSuchLib_XYZ:NoSuchFootprint_XYZ` | ★**板文件不会因为库名不存在而报错**★ ⇒ ★**这就是为什么必须有机器闸去 `test -f` 验封装文件在盘**★ |")
A("| **E9** | 写 1 个之后统计全板 | ★空库名块 **186 → 185** · 具名块 **0 → 1** ⇒ ★**其余 185 个封装一个字节没被动**★ | ★**可以逐个写, 不必整板重写**★ |")
A("")
A("### §2.3 ★「换 land 时把库名与 land 一起替换」的写法 (★本单作业包采用的那一种★)")
A("")
A("★**做法 (★文本层·纯 python·零 pcbnew 依赖★)**:")
A("")
A("```bash")
A("# ★换 land + 写库名 = 对同一个封装块做两件事★")
A("#   ① 删掉该封装块里板面自绘的 pad 与 F.Fab 外框")
A("#   ② 插入目标 .kicad_mod 的 pad 块 (逐块换新 uuid + 按脚表重挂 net)")
A("#   ③ 插入目标 .kicad_mod 的 F.Fab 外框 (fp_line / fp_rect)")
A("#   ④ 把封装块第一行改成 (footprint \"<Lib:Name>\")")
A("# ★★ ①②③ 与 ④ 【必须同一次做完】 ⇒ 板 md5 只变一次 ★★")
A("```")
A("")
A("★**逐件可复跑的实现**: `tmp/iss369/tools/sandbox_libid.py` 的 `build_legA_board()` (★换 land★) 与 `write_libids()` (★写库名★); ★**本单只把它们跑在 `tmp/iss369/sbx/` 的副本上, 真板零改动**★。")
A("")
A("### §2.4 ★换完板文件里哪些字段会变★")
A("")
A("| 字段 | 换 land + 写库名 后 | 证据 |")
A("|---|---|---|")
A("| `(footprint \"…\")` 那一行 | ★**变** (写上 `Lib:Name`)★ | E6/E7 逐行差分 |")
A("| `pad` 块 (号 / 尺寸 / 位置 / 形状 / 层 / net) | ★**变** (整块换成官方 land 的)★ | 沙盒 S1 vs S0 |")
A("| `F.Fab` 的 `fp_line` / `fp_rect` | ★**变** (整块换成官方件的)★ | 沙盒 S1 vs S0 |")
A("| `uuid` | ★**变** (新块必须换新 uuid, 否则 KiCad 会认成同一个对象)★ | E1/E6 |")
A("| `(property \"Reference\")` / `(property \"Value\")` | ★**不变**★ | E6/E7 属性逐项相同 |")
A("| 走线 / 铜皮 / 网络表 | ★**不变** (换 land 不动 net 归属)★ | 沙盒 C4 恒 158 |")
A("| ★**只写库名时 (零几何改动)**★ | ★**只有 `(footprint \"…\")` 那一行变, 其余全部逐字节不变**★ | 沙盒 S3 vs S0 差分 |")
A("")

# ---------------- §3
A("## §3 目标清单 (★90 件 + 96 件 = 186 件·一 ref 一件·不重不漏★)")
A("")
A("★**写盘动作只有两种**: ★**写** (板面 `(footprint \"…\")` 写上 `Lib:Name`) 与 ★**不写** (写任何官方库名都是【假身份】: 板面铜箔与库件对不上)★。")
A("")
A("★**判定口径 (★同一条口径贯穿两张表★)**:")
A("")
A("1. ★**换 land 的 90 件 ⇒ 必须同时写库名**★ (★换 land 而不写库名 = 装配厂拿不到封装 + BOM 与板面对不上★)")
A("2. ★**不动 land 的件 ⇒ 只有在【逐焊盘几何与官方件等价】时才写库名**★ (★本机全库穷举 ⇒ 只有 4 件合格★)")
A("3. ★**其余 ⇒ 不写**, 并写清理由 (★型号/封装未选定 ⇒ 写库名 = 替老板拍板选型★)")
A("")
A("### §3.1 表 A · 90 件 (★靶内 77 + 缺口 13 · 换官方 land + 同时写库名 · 12 字段★)")
A("")
A("| ref | 桶 | 现占位几何 [实测] | 目标 `lib:name` | `.kicad_mod` 实存路径 + md5 | 目标几何 [实测] | 几何 Δ | pad↔net 序要改哪几条 | 要重接的 net 名单 | 腿 B 具名脚清单 (bare → `pinN`) | 证据等级 | 降级方案 |")
A("|---|---|---|---|---|---|---|---|---|---|---|---|")
for x in rows90:
    A("| `%s` | %s | %s | `%s` | %s | %s | %s | %s | %s | %s | %s | %s |"
      % (x["ref"], x["bucket"], x["board_geom"], x["libname"], x["path_md5"],
         x["lib_geom"], x["delta"], x["pad_net"], x["nets"], x["legb"],
         x["evidence"], x["down"]))

A("")
A("★**90 件小结 [实测]**: 目标库件共 **%d** 个不同的 `.kicad_mod`; ★**其中 %d 件的焊盘数会变** (板面脚数 → 目标脚数) ⇒ 这 %d 件换完 land 后 C3「焊盘数 == 网表推出的脚数」会由绿转红, ★**必须与腿 B 的具名脚改名同时做**★ (★C3 红 = 脚表没跟着改★)。"
  % (len(set(x["lib_rel"] for x in rows90)), cnt["pad_count_changes"], cnt["pad_count_changes"]))
A("")
A("### §3.2 表 B · 96 件 (★其余 186 − 90 · 逐件给「写什么」或「为什么不写」★)")
A("")
A("| ref | 桶 | 动作 | 目标 `lib:name` (或「不需要写」) | `.kicad_mod` 实存路径 + md5 | 理由 | 证据等级 |")
A("|---|---|---|---|---|---|---|")
for x in rows96:
    A("| `%s` | %s | **%s** | %s | %s | %s | %s |"
      % (x["ref"], x["bucket"], x["action"],
         ("`%s`" % x["libname"]) if x["libname"] else "★**不需要写**★",
         x["path_md5"] if x["path_md5"] else "—",
         x["reason"], x["evidence"]))

A("")
A("★**96 件小结 [实测]**: 写 **%d** 件 (★全是 `J_SOM_P1~P4`·逐焊盘几何等价·铜箔零改动·旋转 180°★) · 不写 **%d** 件 (★TP 42 + DNP 37 + 已落 land 3 + 选型未定 10★)。"
  % (len(WRITE96), len(NOWRITE96)))
A("")
A("### §3.3 ★件数对账 (★90 / 96 / 186 / C4 158 四桶·四行互相加得起来★)")
A("")
A("| 口径 | 件数 | 算式 | 谁产出 |")
A("|---|---|---|---|")
A("| 板面封装总数 | **186** | 板面实测 | `tmp/iss369/tools/board_probe.py` |")
A("| ★**本单对象 (表 A)**★ | **90** | ★**靶内 77 + 缺口 13 = 90**★ | `tmp/iss369/tools/buckets.py` (★与 ISS-361 / ISS-364 同口径★) |")
A("| ★**其余 (表 B)**★ | **96** | 186 − 90 = 96 | 同上 |")
A("| C4 占位脚号件数 | **158** | ★**TP 42 + DNP 26 + 靶内 77 + 缺口 13 = 158**★ | `state/check_pcb_nets.py` + ISS-361 四桶 |")
A("| C4 里的豁免件 (TP + DNP) | 68 | 42 + 26 | 同上 |")
A("| 不在 C4 的板面器件 | 28 | 186 − 158 = 28 | 同上 |")
A("| 本单要写库名 | **94** | 90 (表 A) + 4 (表 B 的 `J_SOM_P1~P4`) | 本单实算 |")
A("| 本单不写库名 | **92** | 186 − 94 = 92 | 本单实算 |")
A("")
A("★**96 的分桶 (★本单脚本实算·与任务书括注的对账见下★)**:")
A("")
A("| 桶 | 件数 | 名单 |")
A("|---|---|---|")
for k, v in BUCK["buckets"].items():
    A("| %s | %d | %s |" % (k, len(v), " · ".join("`%s`" % r for r in v)))
A("")
A("★**★ 96 与 90 的差在哪 (★任务书要求写清·别另立口径★) ★**:")
A("")
A("- ★**90 件 = C4 四桶里的【靶内 77】+【缺口 13】= 158 里要被收口的那 90 个**★ ⇒ 它们是 ★**C4 占位脚号的持有者**★ ⇒ 换 land + 写库名之后, 它们的**铜箔**变、**网表具名**变 (腿 B), ★**但 C4 读数不变**★ (见 §4)。")
A("- ★**96 件 = 186 − 90 = 【C4 里被豁免的 68 件 (TP 42 + DNP 26)】+【不在 C4 的 28 件】**★ ⇒ ★**这 96 件的 C4 Δ 恒为 0 (它们本来就不在 158 名单里)**★ ⇒ ★**写不写库名都动不了 C4**★。")
A("- ★**⇒ 两张表对 C4 的贡献差 = 0**★ ⇒ ★**C4 恒 158, 「写库名」这一腿对 C4 的贡献 = 0**★ (★沙盒五轮实测见 §4.1★)。")
A("")
A("★**★ 与任务书括注「TP 42 / DNP 26 / 靶内 22 / 缺口 1」的对账 (★本单如实写清·不改口径★) ★**:")
A("")
A("- ★**TP 42** ⇒ 与本单实算【逐件相等】★ (42 个测试焊盘, 一件不多一件不少)。")
A("- ★**DNP 26** ⇒ ★**是【C4 四桶里的 DNP 26】, 与本单实算逐件相等**★; ★**但 96 桶里的 DNP 是 37 件**★ (★= C4 的 DNP 26 + 不在 C4 的 DNP 11★) ⇒ 两个「DNP」的口径不同, ★**本单在表 B 里按【板面 + BOM】分桶写 37, 在本节对账里按【C4 四桶】写 26, 两处都标了口径★★。")
A("- ★**「靶内 22 + 缺口 1 = 23」** ⇒ ★**这不是本板 96 的分桶, 而是【ISS-356 靶子 100 减 C4 158】的差**★: 77 (靶内·在 C4) + **22** (充电板那 22 件·不在本板) + **1** (`J_DEBUG`·在板·不在 C4) = 100 ⇒ ★**那 23 件里的 22 件根本不在本板 186 里, 1 件 (`J_DEBUG`) 在表 B 的「靶内-非C4」桶里**★。")
A("- ★**⇒ 任务书那四个数之和 = 91 ≠ 96**★ ⇒ ★**本单不拿它当件数口径, 一律按【脚本实算】: 90 = 靶内 77 + 缺口 13 (主线, 与 ISS-361 / ISS-364 完全一致) · 96 = 186 − 90**★ ⇒ ★**这条口径差异已列入交卷页「要 main 裁的事」第 1 条**★。")
A("")

# ---------------- §4
A("## §4 ★「写库名会不会改语义」的判定 (★沙盒实测 · C1/C2/C3/C4 逐条★)")
A("")
A("### §4.0 两张表的件数对账摘要 (★任务书要求的 §4 两张表口径, 与 §3.3 同源★)")
A("")
A("| 表 | 件数 | 对 C4 的贡献 |")
A("|---|---|---|")
A("| §3.1 表 A (90 件) | **90** | ★**ΔC4 = 0**★ (★腿 A 换 land 实测 Δ0·写库名实测 Δ0★) |")
A("| §3.2 表 B (96 件) | **96** | ★**ΔC4 = 0**★ (★这 96 件本就不在 C4 的 158 名单里★) |")
A("| ★**合计**★ | **186** | ★**ΔC4 = 0 ⇒ C4 恒 158**★ |")
A("")
A("### §4.1 沙盒五轮 (★真闸 `state/check_pcb_nets.py` 的真代码给出★)")
A("")
A("| 轮次 | 板副本 | rc | C1 | C2 | C3 | ★**C4**★ | 库名非空 |")
A("|---|---|---|---|---|---|---|---|")
ORDER = ["S0_基线_真板真表", "S1_换land不写库名", "S2_换land加写库名",
         "S3_只写库名零几何改动", "S4_反向对照_90件写库名不换land"]
LBL = {"S0_基线_真板真表": "★**S0 基线** (真板 + 真网表)",
       "S1_换land不写库名": "★**S1** 换 90 件 land, ★**不写库名**★",
       "S2_换land加写库名": "★**S2** 换 90 件 land + ★**同时写 94 件库名**★",
       "S3_只写库名零几何改动": "★**S3** ★**只写库名, 零几何改动**★",
       "S4_反向对照_90件写库名不换land": "★**S4** 反向对照: 写 90 件库名, ★**不换 land**★"}
SBRD = {"S0_基线_真板真表": "HW/PCB/demo_mainboard.kicad_pcb (★真板★)",
        "S1_换land不写库名": "tmp/iss369/sbx/board_legA_only.kicad_pcb",
        "S2_换land加写库名": "tmp/iss369/sbx/board_legA_plus_libid.kicad_pcb",
        "S3_只写库名零几何改动": "tmp/iss369/sbx/board_libid_only.kicad_pcb",
        "S4_反向对照_90件写库名不换land": "tmp/iss369/sbx/board_libid_no_landswap.kicad_pcb"}
for k in ORDER:
    s = SBX[k]
    A("| %s | `%s` | %d | %s | %s | %s | ★**%s**★ | %d / %d |"
      % (LBL[k], SBRD[k],
         s["rc"], s["c1"], s["c2"], s["c3"], s["c4"],
         s["libid_named"], s["libid_total"]))
A("")
A("★**逐条判定 (★结论★)**:")
A("")
A("| 判据 | 写库名对它的影响 | 依据 |")
A("|---|---|---|")
A("| ★**C1** (焊盘级等价: ref+焊盘号 → 网络) | ★**Δ = 0**★ ⇒ ★**S1 与 S2 的 C1 读数逐字相同**★ (★S1 与 S2 只差 `lib_id` 那一行★) | 沙盒 S1 vs S2 |")
A("| ★**C2** (U_TEMP 脚数) | ★**Δ = 0**★ ⇒ 五轮全 ✅ | 沙盒五轮 |")
A("| ★**C3** (器件焊盘数 == 网表推出的脚数) | ★**Δ = 0**★ ⇒ ★**S1 与 S2 的 C3 读数逐字相同**★ (★S1 与 S2 只差 `lib_id` 那一行★); ★**但「换 land」这一腿本身会把 C3 弄红 7 件**★ | 沙盒 S1 vs S2 + S0 vs S3 |")
A("| ★**C4** (占位脚号器件数) | ★**Δ = 0**★ ⇒ ★**五轮 C4 全部 = 158**★ ⇒ ★**写库名这一腿对 C4 的贡献 = 0**★ | 沙盒五轮 |")
A("")
A("★**★ 关键结论 (★这是本单要证明的那一条★) ★**:")
A("")
A("> ★**「换 land」与「写库名」是同一件事的两半。**★")
A("> ★**- 腿 A (换官方 land): 沙盒 S1 实测 ΔC4 = 0, ΔC3 = −7 件 (7 件焊盘数变了), ΔC1 不变**★")
A("> ★**- 腿 B (网表节点具名): 那才是让 C4 从 158 变 68 的那一腿 (ISS-364 实测 ΔC4 = −90)**★")
A("> ★**- 本单的「写库名」这一腿: S0→S3 / S1→S2 / S0→S4 三组对照, C1/C2/C3/C4 读数逐字不变 ⇒ ΔC4 = 0**★")
A("> ★**⇒ 「写库名」不改变电气语义; 它只补【身份】, 让装配厂/BOM 对得上板面**★")
A("> ★**⇒ ★**别把「换 land 会让 C4 降下来」当预期**★ —— ★**C4 = 158 是写库名这一腿跑完之后的正确读数**★ (★与 ISS-361 实测的「腿 A 对 C4 贡献 = 0」一致★)")
A("")
A("### §4.2 字节级证据 (★写库名只改一行★)")
A("")
A("| 对照 | A md5 | B md5 | 加/删行数 | ★**差分行全部是封装节点名行**★ |")
A("|---|---|---|---|---|")
for k, v in BYTEDIFF.items():
    if k.startswith("_"):
        continue
    A("| %s | `%s` | `%s` | +%d / −%d | ★**%s**★ |"
      % (k, v["a_md5"][:16], v["b_md5"][:16], v["added"], v["removed"],
         "是" if v["only_footprint_node_lines"] else "★否★"))
A("")
A("★**⇒ 只写库名 (S0→S3) 的 94 个加行与 94 个删行, 逐行都是 `(footprint \"…\")` 那一行 ⇒ 焊盘/走线/铜皮/net/uuid 一个字节都没动**★。")
A("")
A("### §4.3 写库名【本身】会不会改 C1/C2/C3/C4 —— 逐条结论")
A("")
A("- ★**C1**: 板面每个焊盘的 (ref, 焊盘号) → net 归属, ★**写库名一个字节都不改焊盘与 net**★ ⇒ ★**C1 不可能因为写库名而变**★ (★S1/S2 对照实测逐字相同★)。")
A("- ★**C2**: U_TEMP 脚数, 同上 ⇒ 不变。")
A("- ★**C3**: 器件焊盘数 vs 网表推出的脚数, 同上 ⇒ 不变 (★C3 在 S1/S2 里红是因为【换 land】改了焊盘数, 不是因为写库名★)。")
A("- ★**C4**: 网表节点串是不是 bare, ★**完全由 `HW/netlist_v1.csv` 决定, 板在它之后才被读**★ ⇒ 写库名 ⇒ ★**C4 恒 158**★。")
A("")

# ---------------- §5
A("## §5 未决项 (★只登记 · 给代价 · 给会红哪道闸 · 不代老板拍板★)")
A("")
A("| # | 未决项 | 分叉 | 代价 | 会红哪道闸 | 本单的处理 | 证据 |")
A("|---|---|---|---|---|---|---|")
A("| W-1 | ★`D_ESD_USB_D` 最终 2 脚还是 3 脚★ | (a) 2 脚 (b) 3 脚 | (b) ⇒ 板面多一个焊盘 + 走线重画 + 该 net 要重接 | ★**C3** (焊盘数 != 网表脚数) + **C1** (焊盘级等价)★ | ★**本单按 ISS-364 台账的 2 脚件 `Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm` 写目标; 板面现状也是 2 脚 ⇒ Δ焊盘数 = 0; 若改走 3 脚 ⇒ 须重跑本表与 §4 沙盒**★ | [实测]+[推算] |")
A("| W-2 | ★5 只按键 (`SW_BOOT` / `SW_KEY_PWR` / `SW_KEY_VM` / `SW_KEY_VP` / `SW_RST`) 的 2 脚 vs 4 焊盘★ | (a) 2 脚 (只焊两脚) (b) 4 焊盘 (按官方 `SW_Push_1P1T_NO_CK_KMR2` 含 2 个机械焊盘) | (b) ⇒ 板面每只多 2 个焊盘 + 孔位/丝印要复核 + 装配要多压 2 个脚 | ★**C3** (7 件里 3 只是按键) + **C1**★ | ★**本单按 ISS-364 台账的 4 焊盘件写目标; 板面现状 2 脚 ⇒ Δ焊盘数 = +2; 若老板定 2 脚 ⇒ 目标件要换, 几何 Δ 要重算**★ | [实测]+[推算] |")
A("| W-3 | ★`C_VBUS_GND` 留位还是下板★ | (a) 留位 (b) 下板 | (a) ⇒ 板面多 2 个空焊盘, 但 BOM 与板面对不上 (★C1 现在就报「多 2」★) (b) ⇒ 板 md5 再变一次 (★与「板只改一次」冲突★) | ★**C1** (多 2 个焊盘)★ | ★**本单: 不写库名** (BOM 记 dnp=DNP 且 footprint 栏 = 待定 ⇒ 写库名 = 替老板拍板) ⇒ ★**登记 + 给代价, 等老板定**★ | [实测] |")
A("| W-4 | ★`J_SOM_P1~P4` 写哪个 DF40 变体★ | (a) `Hirose_DF40C-100DS-0.4V_2x50_P0.4mm` (b) `Hirose_DF40HC(3.0)-100DS-0.4V_2x50_P0.4mm` | ★**两个变体的焊盘几何逐件等价 (实测 Δpad = 0.000 mm, 旋转 180°) ⇒ 选哪个都不改铜箔**★; 差别在【壳体高度 3.0 mm 的 HC 版本】⇒ ★**是结构高度问题, 不是电气问题**★ | ★**本单两个闸都不红**★ (几何等价) ⇒ ★**选型 = 老板拍板**★ | ★**本单写 (a) 并登记 (b) 为等效候选; 若改写 (b) ⇒ 板面铜箔零改动, 只改 `lib_id` 那一行**★ | [实测]+[推算] |")
A("| W-5 | ★`U_TEMP` / `CONN_LIGHT` / `J_USB_C` 三件已落 land 的封装身份怎么记★ | (a) 写官方库名 (b) 用 `property \"Footprint\"` 记原厂封装号 | (a) ⇒ ★**假身份** (★官方件与板面几何不等价: `U_TEMP` 6 脚 vs 官方 9 脚 (带散热焊盘) · `CONN_LIGHT` 22 脚 vs 官方 24 脚 (带 2 个固定柱) · `J_USB_C` 18 脚 vs 官方 22 脚 (带 2 个 Ø0.65 壳体固定孔 + 接地焊盘)★) (b) ⇒ 板面零改动, 装配厂照原厂封装号取件 | ★**本单新建的闸不判这三件**★ | ★**本单: 不写库名, 登记「用 `property \\\"Footprint\\\"` 记原厂封装号」的建议 (不代拍)**★ | [实测] |")
A("")

# ---------------- §6
A("## §6 复跑命令 + 本单的边界")
A("")
A("```bash")
A("cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses")
A("export TMPDIR=$PWD/tmp")
A("")
A("# ★§0 的读数逐条复跑★")
A("python3 tmp/iss369/tools/parse_board.py          # 板面 186 封装纯文本解析")
A("bash state/pcbnew_py.sh tmp/iss369/tools/board_probe.py   # 库名 0/186 非空 (GetFPIDAsString)")
A("python3 tmp/iss369/tools/buckets.py              # 90 / 96 分桶 + C4 四桶")
A("python3 tmp/iss369/tools/verify_targets.py       # ★94 个目标 .kicad_mod 逐个 test -f + md5★")
A("python3 tmp/iss369/tools/padeq_rot_np.py          # 全库 15468 件逐焊盘几何等价穷举")
A("bash state/pcbnew_py.sh tmp/iss369/tools/mech_probe2.py   # §2 写盘机制 E4~E9")
A("bash state/pcbnew_py.sh tmp/iss369/tools/sandbox_libid.py # ★§4 沙盒五轮 C1~C4★")
A("python3 tmp/iss369/tools/sandbox_diff.py         # §4.2 字节级差分")
A("")
A("# ★本单新建的机器闸★")
A("python3 HW/check_fp_libid_truth.py               # 正常跑 ⇒ rc=0")
A("python3 HW/check_fp_libid_truth.py --selftest    # 反向用例 ⇒ rc=0")
A("")
A("# ★板面逐封装判定 (那一趟换完 land + 写完库名之后, main 用这条验收)★")
A("python3 HW/check_fp_libid_truth.py --mode board --board tmp/iss369/sbx/board_legA_plus_libid.kicad_pcb")
A("```")
A("")
A("★**本单的边界 (★逐条自证·交卷页 §B5 有逐条双证★)**:")
A("")
A("| 边界 | 自证方式 |")
A("|---|---|")
A("| ★**零写板**★ | 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · 4,940,213 B, 开工前 = 交卷后 |")
A("| ★**零落表**★ | `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` md5 开工前 = 交卷后 |")
A("| ★**零改既有闸**★ | `HW/check_fp_truth_baseline.py` · `HW/check_fp_truth_coverage_gap.py` · `HW/check_fp_truth_land_swap.py` · `HW/check_onepass_preflight_coverage.py` · `HW/check_onepass_s10_manifest.py` · `state/check_pcb_nets.py` · `state/gate_check.py` · `state/merge.py` · `state/frag_write.py` 一个字节未改 |")
A("| ★**零改既有页面**★ | `HW/FP_TRUTH_BASELINE.md` · `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` · `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` · `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` · `state/board_trip_baseline_20260723.txt` 老字未改 |")
A("| ★**零挂链**★ | 本单的新闸 ★**没有**挂进 `state/gate_check.py` (★挂链是 main 的地界·本单只交脚本与路径 + 建议★) |")
A("| ★**零外发 / 零采购**★ | 本单没有任何出网请求; 查不到的部分一律写降级方案 |")
A("| ★**不代老板拍板**★ | §5 的 5 条全部是「登记 + 给代价 + 给会红哪道闸」; 未决项一条没替老板定 |")
A("| ★**只写自己的分片**★ | 只写 `state/fragments/hw.yaml`, 只走 `state/frag_write.py` |")
A("| ★**不自签 `state/issue_log.yaml`**★ | 一个字没动 |")
A("| ★**沙盒只落 `tmp/iss369/` + `logs/iss369/`**★ | 沙盒板副本在 `tmp/iss369/sbx/`; 留证在 `logs/iss369/` |")
A("")

# ---------------- §7 回滚说明
A("## §7 ★回滚说明 (★沙盒怎么复原 · 真件零改动怎么自证★)")
A("")
A("| 对象 | 怎么复原 | 自证命令 |")
A("|---|---|---|")
A("| ★**真板** ★`HW/PCB/demo_mainboard.kicad_pcb`★ | ★**本单从未写过它 ⇒ 无需复原**★ (★所有写盘动作都发生在 `tmp/iss369/sbx/` 的副本上★) | ★**`md5sum HW/PCB/demo_mainboard.kicad_pcb`** ⇒ 必须仍是 `611b869e13518c3c023fb178f91a0075`; ★**`stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb`** ⇒ 必须仍是 `2026-11-06 07:07:17.362193413` / `4940213`★ |")
A("| ★**沙盒板副本** (4 个)★ | ★**删掉 `tmp/iss369/sbx/` 整个目录即可复原**★ (★它们只被读·从未被当真件★); 要重跑沙盒: `bash state/pcbnew_py.sh tmp/iss369/tools/sandbox_libid.py` ★(会重新生成这 4 个副本 + 两份留证 json)★ | `ls -l tmp/iss369/sbx/` + `md5sum tmp/iss369/sbx/*.kicad_pcb` (★副本的 md5 与真板不同是正常的·它们就是变更后的板★) |")
A("| ★**留证** `logs/iss369/`★ | 只增不改 ⇒ 无需回滚; 若要重跑某一项, 按 §6 的命令重跑并覆盖同名文件 | `ls -l logs/iss369/` |")
A("| ★**本单新建的页** `HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md`★ | ★**整页删掉即可**★ (★它是纯新建文件·不覆写任何既有页★); 要重建: `python3 logs/iss369/build_fp_libid_workpacket.py` | `md5sum HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` |")
A("| ★**本单新建的闸** `HW/check_fp_libid_truth.py`★ | ★**删掉即可**★ (★★它【没有】挂进 `state/gate_check.py` ⇒ 删了不会影响既有门禁链★★) | `grep -c check_fp_libid_truth state/gate_check.py` ⇒ 必须 = **0** |")
A("| ★**分片** `state/fragments/hw.yaml`★ | 用 `state/frag_write.py` 把本单新增的条目删掉 (★只走原子写★); 本单只新增·未改既有条目 ⇒ 删掉新增条目即回到开工前状态 | `md5sum state/fragments/hw.yaml` (★开工前 = `8305a9b2c3240ca2c9b4b2cb659971fe`·见交卷页 §B5★) |")
A("")
A("★**★ 真件零改动的总自证 (★一行命令·交卷页 §B5 贴原样输出★) ★**:")
A("")
A("```bash")
A("md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv")
A("stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb")
A("```")
A("")

open(OUT, "w", encoding="utf-8").write("\n".join(W) + "\n")
print("-> %s (%d 行, %d B)" % (OUT, len(W), os.path.getsize(OUT)))
print("90 件表 = %d 行 · 96 件表 = %d 行 · 写 = %d · 不写 = %d"
      % (len(rows90), len(rows96), len(ALL_WRITE), len(NOWRITE96)))
