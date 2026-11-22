#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_s8_target_list.py —— ★★【S8 布线归零 · 目标名单重读器】★★ (★ISS-339 · hw-lead · 2026-11-22★)

★★**这把尺子是干什么的 (★一句话★)** ★★
  ★**板那一趟 (S8 = 布线归零 unc 45→0) 的靶, 不能照抄官方板那 24 条零铜网** ——
  实测 (ISS-337) ★**那 24 条里 21 条在现役链终板 v76mg1 上【已经有铜】** ⇒
  ★**两边都零铜只剩 3 条** (`CSI_D0_D0_N_SRC` / `CSI_D0_D2_N` / `CSI_D0_D3_N`) ⇒
  ★**分母必须在【那一趟的真实基线板】上重读** ⇒ ★**本脚本就是那把重读器** ★★

★★**必须输出 (★一份表, 一行一条网★)** ★★
  网名 · 分级 [必需/可悬空/待定] · 本板有没有铜 (有/无 + 铜长 mm) ·
  参照板有没有铜 (同上) · 备注 (差分腿 / 单端脚 / DNP 预留位 …)

★★**必打印的三行汇总** ★★
  ① N' = 本板 unconnected 条数 (★本板自己跑 DRC 得出·不是照抄 45★)
  ② 两个分母口径都要给 (★不许混着写★): 全部网口径 · pad≥2 焊盘网口径
     ⇒ ★**「24 条零铜网」和「45 条 unconnected」是两个东西, 不许互相替代**★
  ③ 两边都零铜清单 (本板 ∩ 参照板)

★★**必需性分级 (★main 2026-11-22 20:5x 已裁口径·沿用·不许重开·不许自改★)** ★★
  必需 23 条 = ① 15 条高速差分腿 (CSI_D0_* / DSI_D0_* 族) + ② 8 条单端脚
               (CAM_RESET_N · LED_G_D · USB_CC2 · JTAG_TDI · UART_RX ·
                SPI_SCLK_BOOT · SPI_MOSI_BOOT · SPI_MISO_BOOT)
  可悬空 1 条 = FSIN_OUT   (★标 NC 是板那一趟的板侧动作·本单只定口径·不定动作★)
  待定 0 条
  ⇒ 24 条零铜网 = 23 必需 + 1 可悬空

★★**铁律 (★本脚本每次跑都打印★)** ★★
  ★**「靶更小」≠「板子更好」** (★现役链终板自己过不了名单制闸 ⇒ 靶更小只是【工作量口径】变了★)
  ★**判据顺序 = 先可比性 → 再名单 → 最后才看计数有没有变好**
  ★**本单只出尺子 + 现值快照, 不许改板 / 不许跑臂 / 不许对板下判决**

★★**用法** ★★
  python3 HW/check_s8_target_list.py <板路径> [--baseline <参照板>]
      ★参照板只读, 不许改★; 不给 --baseline ⇒ 不出"参照板"两列
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
KICAD_SH = os.path.join(PROJ, "state", "kicad.sh")
CACHE_DIR = os.path.join(PROJ, "tmp", "iss339", "cache")

# ═══════════════════════════════════════════════════════════════════════
# ★**必需性分级 (★main 2026-11-22 20:5x 已裁口径·逐字沿用·不许重开★)** ★*
# ═══════════════════════════════════════════════════════════════════════
REQUIRED_SINGLE = [
    "CAM_RESET_N", "LED_G_D", "USB_CC2", "JTAG_TDI",
    "UART_RX", "SPI_SCLK_BOOT", "SPI_MOSI_BOOT", "SPI_MISO_BOOT",
]
FLOAT_OK = ["FSIN_OUT"]
DIFF_PREFIXES = ("CSI_D0_", "DSI_D0_")

# ★**已裁口径的期望值 (★用来自检本脚本算出来的分级对不对·对不上就如实报出来★)** ★*
EXPECT_REQUIRED = 23
EXPECT_FLOAT = 1
EXPECT_TBD = 0


def classify(net):
    """★返回 (分级串, 备注) ★
    ★分级串 ∈ {'[必需]', '[可悬空]', '[待定]'} ★"""
    if net in REQUIRED_SINGLE:
        return "[必需]", "单端脚"
    if net in FLOAT_OK:
        return "[可悬空]", "板侧标 NC (★板那一趟动作·本单不定★)"
    for p in DIFF_PREFIXES:
        if net.startswith(p):
            return "[必需]", "高速差分腿"
    return "[待定]", "未列入已裁口径"


# ═══════════════════════════════════════════════════════════════════════
# ★**板文件解析 (★只读·自己写的·同款思路 = state/pair_copper_table.py★)** ★*
# ═══════════════════════════════════════════════════════════════════════
def parse_board(path):
    """★返回 dict:
         net_seg : {net: 段数}
         net_cu  : {net: 铜长 mm}
         pad_cnt : {net: 焊盘数}
         segs / vias / nets_cu
       ★解析思路 = state/pair_copper_table.py + state/compare_net_copper.py 同款 (行级状态机) ★"""
    net_seg = {}
    net_cu = {}
    pad_cnt = {}
    dnp_pads = {}
    segs = 0
    vias = 0
    cur = None
    net = None
    x1 = y1 = x2 = y2 = None
    depth = 0
    fp_depth = None
    fp_dnp = False
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            s = ln.strip()
            # ★★**footprint 上下文 (★只为标 DNP 预留位·不参与任何计数★)** ★★
            if fp_depth is not None and depth < fp_depth:
                fp_depth = None
                fp_dnp = False
            if fp_depth is None and s.startswith("(footprint "):
                fp_depth = depth + s.count("(")
                fp_dnp = False
            elif fp_depth is not None and "exclude_from_bom" in s:
                fp_dnp = True
            delta = s.count("(") - s.count(")")
            try:
                if s == "(segment":
                    cur = "seg"; net = None; x1 = y1 = x2 = y2 = None
                    continue
                if s == "(via":
                    cur = "via"; net = None
                    continue
                if s == "(pad" or s.startswith("(pad "):
                    cur = "pad"; net = None
                    continue
                if cur is None:
                    continue
                if s == ")":
                    if cur == "seg":
                        segs += 1
                        if net:
                            net_seg[net] = net_seg.get(net, 0) + 1
                            if None not in (x1, y1, x2, y2):
                                net_cu[net] = net_cu.get(net, 0.0) + \
                                    math.hypot(x2 - x1, y2 - y1)
                    elif cur == "via":
                        vias += 1
                    elif cur == "pad":
                        if net:
                            pad_cnt[net] = pad_cnt.get(net, 0) + 1
                            if fp_dnp:
                                dnp_pads[net] = dnp_pads.get(net, 0) + 1
                    cur = None
                    net = None
                    continue
                m = re.match(r'\(net\s+(?:"([^"]+)"|(\d+))\)', s)
                if m:
                    net = m.group(1) if m.group(1) else ("#%s" % m.group(2))
                    continue
                if cur == "seg":
                    m = re.match(r"\(start ([-\d.]+) ([-\d.]+)\)", s)
                    if m:
                        x1, y1 = float(m.group(1)), float(m.group(2))
                        continue
                    m = re.match(r"\(end ([-\d.]+) ([-\d.]+)\)", s)
                    if m:
                        x2, y2 = float(m.group(1)), float(m.group(2))
                        continue
            finally:
                depth += delta
    return {
        "path": path,
        "net_seg": net_seg,
        "net_cu": net_cu,
        "pad_cnt": pad_cnt,
        "dnp_pads": dnp_pads,
        "segs": segs,
        "vias": vias,
        "nets_cu": set(net_cu.keys()),
        "nets_pad": set(pad_cnt.keys()),
    }


def zero_copper_pad2(b):
    """★口径② pad≥2 焊盘网口径: 板上零 segment 且焊盘数≥2 的网 (★升序★) ★"""
    return sorted(n for n, c in b["pad_cnt"].items()
                  if c >= 2 and b["net_seg"].get(n, 0) == 0)


def zero_copper_all(b, universe):
    """★口径① 全部网口径: 在给定网名全集 universe 里, 板上零 segment 的网 ★
    ★universe = 两板【有铜网】的并集 (★ISS-337 log 06 的口径★) ★"""
    return sorted(n for n in universe if b["net_seg"].get(n, 0) == 0)


def required_zero_copper_nets(board_path):
    """★给 `HW/check_board_comparable_gate.py` 的名单层探针用 ★
    ★返回: 必需分级 且 本板零铜 的网名列表 (★命中 ⇒ 这块板有必需的高速/单端脚没铜 ⇒ 必拒★) ★"""
    b = parse_board(board_path)
    out = []
    for n in zero_copper_pad2(b):
        lvl, _note = classify(n)
        if lvl == "[必需]":
            out.append(n)
    return sorted(out)


# ═══════════════════════════════════════════════════════════════════════
# ★**差分对清单 (★只作备注用·读不到就退化到命名推断★)** ★*
# ═══════════════════════════════════════════════════════════════════════
def load_pairs():
    cand = [
        # ★同款路径推导 = state/compare_arm_official.py 的 _AUDIT (★state → smart_glasses
        #   → projects → workspace ⇒ 退三级 + tools/★)
        os.path.normpath(os.path.join(PROJ, "..", "..", "tools", "diff_pair_audit.py")),
        os.path.normpath(os.path.join(PROJ, "..", "..", "..", "tools", "diff_pair_audit.py")),
        os.path.join(PROJ, "tools", "diff_pair_audit.py"),
    ]
    for p in cand:
        if os.path.isfile(p):
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
                m = re.search(r"PAIRS\s*=\s*\[(.*?)\]", txt, re.S)
                if m:
                    out = re.findall(r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', m.group(1))
                    if len(out) >= 20:
                        return out, "★tools/diff_pair_audit.py PAIRS (%d 对)" % len(out)
            except Exception:
                pass
    return [], "★PAIRS 清单读不到 ⇒ 用命名推断 (_P/_N 配对)"


def pair_partner(pairs, net):
    for p, n in pairs:
        if p == net:
            return n
        if n == net:
            return p
    if net.endswith("_P"):
        return net[:-2] + "_N"
    if net.endswith("_N"):
        return net[:-2] + "_P"
    return None


# ═══════════════════════════════════════════════════════════════════════
# ★**unconnected 清单 (★照抄 state/check_pcb_drc.py 的调法★)** ★*
# ═══════════════════════════════════════════════════════════════════════
def _tag(path):
    ab = os.path.abspath(path)
    h = hashlib.sha1(ab.encode("utf-8")).hexdigest()[:8]
    return "%s_%s" % (re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(ab)), h)


def _load_drc_json(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(d, dict) or "unconnected_items" not in d:
        return None
    return d


def drc_unconnected(board_path, allow_run=True, timeout=900):
    """★返回 (json_path, data, reused: bool, note: str) ★
    ★复用顺序: ① 本沙盒缓存 ② 主本机 /tmp 的同板 DRC JSON (★同板名+源名一致才复用★)
    ★都没 ⇒ 现跑 (★照抄 check_pcb_drc.py 的调法★) ★"""
    tag = os.path.basename(board_path).replace("/", "_").replace(" ", "_")
    cands = [
        os.path.join(CACHE_DIR, "drc_%s.json" % _tag(board_path)),
        "/tmp/_pcb_drc_latest_%s.json" % tag,
        "/tmp/_pcb_drc_%s.json" % tag,
    ]
    for p in cands:
        if not os.path.isfile(p):
            continue
        d = _load_drc_json(p)
        if d is None:
            continue
        src = os.path.basename(str(d.get("source") or ""))
        if src and src != os.path.basename(board_path):
            continue
        return p, d, True, "复用现成 DRC JSON (%s)" % p
    if not allow_run:
        return None, None, False, "无 DRC JSON 且不跑"
    os.makedirs(CACHE_DIR, exist_ok=True)
    out = os.path.join(CACHE_DIR, "drc_%s.json" % _tag(board_path))
    cmd = ["bash", KICAD_SH, "pcb", "drc", "--output", out,
           "--severity-error", "--severity-warning", "--format", "json", board_path]
    try:
        r = subprocess.run(cmd, cwd=PROJ, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=timeout)
    except Exception as e:
        return None, None, False, "DRC 跑失败: %s" % e
    d = _load_drc_json(out)
    if d is None:
        return out, None, False, "DRC 跑完但 JSON 读不到 (rc=%s)" % r.returncode
    return out, d, False, "现跑 DRC (rc=%d)" % r.returncode


def net_unc_map(items):
    """★逐网未连接条目数 (★同款思路 = state/compare_arm_official.py 的 net_unc_map_from★) ★"""
    out = {}
    for it in items or []:
        names = []
        for x in (it.get("items") or []):
            m = re.search(r"\[([^\]]+)\]", x.get("description") or "")
            if m:
                names.append(m.group(1))
        if not names:
            continue
        s = sorted(set(names))
        k = s[0] if len(s) == 1 else "|".join(s)
        out[k] = out.get(k, 0) + 1
    return out


# ═══════════════════════════════════════════════════════════════════════
def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    base = None
    if "--baseline" in argv:
        i = argv.index("--baseline")
        if i + 1 < len(argv):
            base = argv[i + 1]
    if not args:
        print(__doc__)
        return 2
    board = args[0]
    if not os.path.isfile(board):
        print("❌ 板不存在: %s" % board)
        return 2
    if base and not os.path.isfile(base):
        print("❌ 参照板不存在: %s" % base)
        return 2

    b = parse_board(board)
    bb = parse_board(base) if base else None
    pairs, pairs_note = load_pairs()

    print("═══ S8 布线归零 · 目标名单重读器 (★ISS-339·hw-lead·零写板★) ═══")
    print("  本板   : %s" % board)
    print("          md5 %s" % md5_of(board))
    if base:
        print("  参照板 : %s (★只读·不改★)" % base)
        print("          md5 %s" % md5_of(base))
    else:
        print("  参照板 : (未给 --baseline ⇒ 不出参照列)")
    print("  必需性分级: ★main 2026-11-22 20:5x 已裁口径 (23 必需 = 15 差分腿 + 8 单端脚 / "
          "1 可悬空 FSIN_OUT / 0 待定) ⇒ 沿用·不重开★")
    print("  差分对备注来源: %s" % pairs_note)
    print("  本板统计: 段数 %d · 过孔 %d · 焊盘网 %d · 有铜网 %d"
          % (b["segs"], b["vias"], len(b["nets_pad"]), len(b["nets_cu"])))
    if bb:
        print("  参照统计: 段数 %d · 过孔 %d · 焊盘网 %d · 有铜网 %d"
              % (bb["segs"], bb["vias"], len(bb["nets_pad"]), len(bb["nets_cu"])))

    # ── ① 目标名单表 (★pad≥2 焊盘网口径 · 本板零铜网★) ──
    zc = zero_copper_pad2(b)
    print("\n── ① 目标名单 (★pad≥2 焊盘网口径·本板零铜网 %d 条★) ──" % len(zc))
    if not zc:
        print("  (本板没有 pad≥2 零铜网)")
    else:
        print("  %-26s %-10s %-8s %10s %-10s %10s  %s"
              % ("网名", "分级", "本板有铜", "本板铜长mm", "参照有铜", "参照铜长mm", "备注"))
        for n in zc:
            lvl, note = classify(n)
            cu = b["net_cu"].get(n, 0.0)
            has = "有" if b["net_seg"].get(n, 0) > 0 else "无"
            if bb is not None:
                bcu = bb["net_cu"].get(n, 0.0)
                bhas = "有" if bb["net_seg"].get(n, 0) > 0 else "无"
                pt = pair_partner(pairs, n)
                if pt and (note == "高速差分腿" or pt.startswith(DIFF_PREFIXES)):
                    note = "%s (对: %s)" % (note, pt)
                if b.get("dnp_pads", {}).get(n, 0) >= b["pad_cnt"].get(n, 0) \
                        and b["pad_cnt"].get(n, 0) > 0:
                    note += " · DNP 预留位"
                print("  %-26s %-10s %-8s %10.1f %-10s %10.1f  %s"
                      % (n, lvl, has, cu, bhas, bcu, note))
            else:
                pt = pair_partner(pairs, n)
                if pt and (note == "高速差分腿" or pt.startswith(DIFF_PREFIXES)):
                    note = "%s (对: %s)" % (note, pt)
                if b.get("dnp_pads", {}).get(n, 0) >= b["pad_cnt"].get(n, 0) \
                        and b["pad_cnt"].get(n, 0) > 0:
                    note += " · DNP 预留位"
                print("  %-26s %-10s %-8s %10.1f %-10s %10s  %s"
                      % (n, lvl, has, cu, "-", "-", note))

    # ── 分级自检 (★与 main 已裁口径逐条对·对不上如实报★) ──
    cnt = {"[必需]": 0, "[可悬空]": 0, "[待定]": 0}
    for n in zc:
        cnt[classify(n)[0]] += 1
    print("\n  ★分级自检: 必需 %d (期望 %d) · 可悬空 %d (期望 %d) · 待定 %d (期望 %d) ⇒ %s"
          % (cnt["[必需]"], EXPECT_REQUIRED, cnt["[可悬空]"], EXPECT_FLOAT,
             cnt["[待定]"], EXPECT_TBD,
             "一致 ✔" if (cnt["[必需]"] == EXPECT_REQUIRED
                          and cnt["[可悬空]"] == EXPECT_FLOAT
                          and cnt["[待定]"] == EXPECT_TBD)
             else "★不一致 ⇒ 如实上报·不硬凑 (★交 main 裁★)"))

    # ── ② 汇总三行 ──
    print("\n── ② 汇总 (★三行必给·不许混着写★) ──")

    # ②-1 N' = 本板 unconnected
    jp, d, reused, note = drc_unconnected(board)
    if d is None:
        print("  ★N' = 本板 unconnected 条数: [0数据] (%s)" % note)
        unc_n = -1
        unc_map = {}
        viol = -1
    else:
        items = d.get("unconnected_items") or []
        unc_map = net_unc_map(items)
        unc_n = len(items)
        viol = len(d.get("violations") or [])
        print("  ★N' = 本板 unconnected 条数 = %d  (★本板自己跑 DRC 得出·不是照抄 45★·%s)"
              % (unc_n, note))
        print("     ★同时: DRC violations = %d" % viol)
        if unc_map:
            print("     ★逐条 unconnected 网名 (%d 个网):" % len(unc_map))
            for k in sorted(unc_map, key=lambda x: (-unc_map[x], x)):
                print("        · %-34s %d 项" % (k, unc_map[k]))
    # ②-2 两个分母口径
    if bb is not None:
        universe = b["nets_cu"] | bb["nets_cu"]
    else:
        universe = b["nets_cu"] | b["nets_pad"]
    zc_all = zero_copper_all(b, universe)
    print("  ★分母口径① 全部网口径 (★对照宇宙 = 两板有铜网并集·共 %d 个网名★): 本板零铜 %d 条"
          % (len(universe), len(zc_all)))
    if bb is not None:
        zc_all_b = zero_copper_all(bb, universe)
        print("                               参照板零铜 %d 条" % len(zc_all_b))
    print("  ★分母口径② pad≥2 焊盘网口径 (★板自身焊盘网·官方板实测 24★): 本板零铜 %d 条"
          % len(zc))
    if bb is not None:
        print("                               参照板零铜 %d 条" % len(zero_copper_pad2(bb)))
    print("  ★★**「24 条零铜网」和「45 条 unconnected」是两个东西, 不许互相替代**★")

    # ②-3 两边都零铜
    if bb is not None:
        both = sorted(set(zc) & set(zero_copper_pad2(bb)))
        print("  ★两边都零铜 (本板 ∩ 参照板 · pad≥2 口径) = %d 条: %s"
              % (len(both), " / ".join(both) if both else "(无)"))
        both_all = sorted(set(zc_all) & set(zc_all_b))
        print("  ★两边都零铜 (全部网口径) = %d 条: %s"
              % (len(both_all), " / ".join(both_all) if both_all else "(无)"))
    else:
        print("  ★两边都零铜: (★未给 --baseline ⇒ 不出本项★)")

    # ── ③ 铁律 ──
    print("\n── ③ 铁律 (★必须带进板那一趟★) ──")
    print("  ★**「靶更小」≠「板子更好」** (★现役链终板自己过不了名单制闸 ⇒ 靶更小只是【工作量口径】变了★)")
    print("  ★**判据顺序 = 先可比性 → 再名单 → 最后才看计数有没有变好**")
    print("  ★**本单只出尺子 + 现值快照, 不许改板 / 不许跑臂 / 不许对板下判决**")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
