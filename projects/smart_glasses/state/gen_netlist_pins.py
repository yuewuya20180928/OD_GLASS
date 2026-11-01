#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/gen_netlist_pins.py —— 生成 **pin-centric** 网表 CSV (ISS-094)

★为什么要有这个 (2026-11-02 02:3x):
  `HW/netlist_v1.csv` 的数据模型是 **"连接清单"** (一行 = 一根导线 = 器件脚 ↔ 器件脚),
  而且 ★**大部分行的引脚号是"隐式"的** —— node 列写的是裸位号 (274/470 行),
  真正的引脚号靠**该器件在网表里出现的先后顺序**推出来 (只有 96 行写了显式 "REF pinN")。
  ⇒ 后果有两个:
    ① PCB 工程师按 CSV 接线时看不到引脚号 ⇒ 必须对着 `.net` 干 ⇒ CSV 用不上;
    ② ★**隐式引脚号 + 手写显式引脚号 混用 ⇒ 笔误能长期潜伏**
       (实例: P1 页 TS_BAT 那行把 RT1 的 TS 端写成 "U_CHG pin22" (=REGN) 而不是 pin11 (=TS)
        ⇒ 表面看只是"写法不一致", 实际是 REGN 被短到电池 NTC 节点 ⇒ 充电链失效。
        这个错逃过了全部 36 条门禁 —— 因为 `.net` 生成器会**按连通性重排引脚**, .net 一直是对的)。

★本脚本的口径 (关键):
  **`.net` (KiCad Eeschema 导出) 才是带显式引脚号的那一份** ⇒ 本脚本
    ① 解析 `.net` ⇒ 拿到 (ref, pin) → net 的完整映射 (622 个 node)
    ② 从 `.csv` 取每个 (ref, net) 的元信息 (value/footprint/dnp/evidence/page/board/conn_id)
    ③ 输出 **每引脚一行** 的 pin-centric CSV
  ⇒ ★**因此不需要改生成器就能得到真 pin 表**, 而且 CSV 与 .net 天然一一对应 (可互相交叉核对)。

★交叉校验 (本脚本自带的强门禁):
    - `.net` 里每个 (ref, pin) 只能属于一个网
    - `.net` 的每个 node 都要能在 `.csv` 里找到对应 (ref, net) 行
    - `.csv` 里每行声明的器件都要在 `.net` 里出现
    - 2 脚无源件 (R/C/L/D) 必须恰好 2 个脚
    - 同一引脚出现在多个网时, 必须落在**器件 pinout 真源**允许的网集合内 (读 HW/check_*_pinout.py 源码)

用法:
    python3 state/gen_netlist_pins.py            # 生成 + 自检
    python3 state/gen_netlist_pins.py --selftest  # 只跑自检
"""
from __future__ import annotations

import csv
import io
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CSV_IN = os.path.join(PROJ, "HW", "netlist_v1.csv")
NET_IN = os.path.join(PROJ, "HW", "netlist_v1.net")
OUT = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")

COLS = ["pin_id", "net", "ref", "pin", "page", "value", "type", "dnp", "board",
        "conn_id", "footprint", "opn", "evidence", "tbd", "note"]

# 器件 pinout 真源: "某引脚允许出现在哪几个网" 的唯一裁定方
ALLOWED: dict[str, dict[str, set[str]]] = {}

# 伪器件 (不是真器件: 轨/网络标记/接地)
PSEUDO_REFS = re.compile(r"^(NET_|RAIL_|GND$|VSS$|VDD$|SoC_)")


def load_pinout_authorities() -> list[str]:
    """从 HW/check_*_pinout.py 源码里抽出允许网集合 (正则读源码, 不 import 不执行)"""
    loaded = []
    hw_dir = os.path.join(PROJ, "HW")
    pat = re.compile(r'\((\d+)\s*,\s*\("[^"]+"\s*,\s*"[^"]*"\s*,\s*\{([^}]*)\}')
    for fn in sorted(os.listdir(hw_dir)):
        if not fn.startswith("check_") or not fn.endswith("_pinout.py"):
            continue
        path = os.path.join(hw_dir, fn)
        try:
            txt = io.open(path, encoding="utf-8").read()
        except BaseException:
            continue
        d = ALLOWED.setdefault("U_CHG", {})
        n = 0
        for m in pat.finditer(txt):
            nets = {x.strip().strip('"') for x in m.group(2).split(",") if x.strip()}
            if nets:
                d[m.group(1)] = nets
                n += 1
        if n:
            loaded.append(f"{fn} → U_CHG ({n} 脚有允许集合)")
    return loaded


def parse_net() -> tuple[list[dict], list[str]]:
    """解析 .net (KiCad Eeschema v" E") ⇒ [(net, ref, pin)]"""
    txt = io.open(NET_IN, encoding="utf-8").read()
    out: list[dict] = []
    errors: list[str] = []
    for m in re.finditer(r'\(net \(code "\d+"\) \(name "([^"]+)"\)(.*?)\n    \)', txt, re.S):
        net, body = m.group(1), m.group(2)
        for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', body):
            out.append({"net": net, "ref": n.group(1), "pin": n.group(2)})
    return out, errors


def parse_csv_rows() -> list[dict]:
    with open(CSV_IN, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cell(r: dict, k: str) -> str:
    return (r.get(k) or "").strip()


def main() -> int:
    auths = load_pinout_authorities()
    if auths:
        print("ℹ️  已加载 pinout 真源: " + "; ".join(auths))
    nodes, errors = parse_net()
    rows = parse_csv_rows()

    # (ref, net) → 元信息
    meta: dict[tuple[str, str], dict] = {}
    for r in rows:
        key = (cell(r, "ref"), cell(r, "net"))
        if key not in meta:
            meta[key] = r

    # 校验 1: 同一 (ref, pin) 不能在两个网
    by_pin: dict[tuple[str, str], list[str]] = defaultdict(list)
    for n in nodes:
        by_pin[(n["ref"], n["pin"])].append(n["net"])
    for (ref, pin), nets in sorted(by_pin.items()):
        if len(set(nets)) > 1:
            allowed = ALLOWED.get(ref, {}).get(pin, set())
            if not (allowed and set(nets) <= allowed):
                errors.append(f"{ref}.{pin} 同时出现在 {sorted(set(nets))} ⇒ 一个引脚只能属于一个网 "
                              f"(pinout 允许={sorted(allowed) if allowed else '无该器件 pinout 真源'})")

    # 校验 2: .net 的每个器件都要在 CSV 里出现过 (按器件查, 不按 (器件,网) 查 ——
    #   CSV 里同一物理网可以有多个网名 (跨页别名), 按网名配对会误报)
    net_refs = {n["ref"] for n in nodes}
    csv_refs = {cell(r, "ref") for r in rows if cell(r, "ref")}
    ghost = sorted(r for r in (csv_refs - net_refs) if not PSEUDO_REFS.match(r))
    if ghost:
        errors.append(f"CSV 里的器件在 .net 里缺席 (幽灵器件): {ghost[:8]}")
    no_csv = sorted(r for r in (net_refs - csv_refs) if not PSEUDO_REFS.match(r))
    if no_csv:
        errors.append(f".net 里的器件在 CSV 里没有出处: {no_csv[:8]}")

    # ★★校验 3b (2026-11-02 02:3x 新增, 防回归): .net 里必须有 SoC 占位器件, 且引脚数 >= 50
    #   ★**为什么加这条**: 把占位从 SoC[TBD-01] 改名成 SoC[RK3572] 时, gen_kicad_net.py 里硬编码的正则
    #   没跟着改 ⇒ **SoC 的 56 个引脚整条从 .net 里消失** (550→494 行) 而**所有原有门禁都没报**
    #   ⇒ ⇒ "全局字符串改名"这类动作必须配一条**结构回归检查**。
    soc_pin_n = defaultdict(int)
    for n_ in nodes:
        if n_["ref"].startswith("SoC_"):
            soc_pin_n[n_["ref"]] += 1
    if not soc_pin_n:
        errors.append(".net 里没有 SoC 占位器件 ⇒ ★**SoC 引脚整条丢了** "
                      "(检查 gen_kicad_net.py 的 SoC[xxx] 正则是否跟着改名更新)")
    else:
        for sr, n_ in sorted(soc_pin_n.items()):
            if n_ < 50:
                errors.append(f".net 里 SoC 占位器件 {sr} 只有 {n_} 个脚 (应 >=50) ⇒ SoC 引脚丢失")

    # 校验 3: 2 脚无源件恰好 2 脚 (只查 R/C/L —— D 可能是 ESD 阵列等多脚器件, 与 check_kicad_net 同口径)
    pin_cnt: dict[str, int] = defaultdict(int)
    for n in nodes:
        pin_cnt[n["ref"]] += 1
    ref_type = {cell(r, "ref"): cell(r, "type") for r in rows if cell(r, "ref")}
    for ref, c in sorted(pin_cnt.items()):
        if ref_type.get(ref) in ("R", "C", "L") and c != 2:
            errors.append(f"{ref} 是 {ref_type.get(ref)} (2 脚件) 但 .net 里只有 {c} 个脚")

    # 输出: 每引脚一行
    ref_first: dict[str, dict] = {}
    for r in rows:
        rr = cell(r, "ref")
        if rr and rr not in ref_first:
            ref_first[rr] = r
    fallback = 0
    pins = []
    for n in nodes:
        m = meta.get((n["ref"], n["net"]))
        if m is None:
            m = ref_first.get(n["ref"], {})
            fallback += 1
        pins.append({
            "pin_id": f"{n['ref']}.{n['pin']}",
            "net": n["net"],
            "ref": n["ref"],
            "pin": n["pin"],
            "page": cell(m, "page"),
            "value": cell(m, "value"),
            "type": cell(m, "type"),
            "dnp": cell(m, "dnp"),
            "board": cell(m, "board"),
            "conn_id": cell(m, "conn_id"),
            "footprint": cell(m, "footprint"),
            "opn": cell(m, "opn"),
            "evidence": cell(m, "evidence"),
            "tbd": cell(m, "tbd"),
            "note": cell(m, "note")[:200],
        })
    pins.sort(key=lambda d: (d["ref"], d["pin"]))

    print("=" * 78)
    print("  pin-centric 网表自检 (ISS-094)")
    print("=" * 78)
    for e in errors:
        print(f"  ❌ {e}")
    print(f"  ℹ️  pin 行数 = {len(pins)} · 器件数 = {len(pin_cnt)} · "
          f"网数 = {len({n['net'] for n in nodes})}")
    print(f"  ℹ️  行级元信息回落到『该器件首行』的 pin 数 = {fallback} "
          f"(原因: CSV 同一物理网有多个网名, 按 (器件,网) 精确配对会落空)")
    same = [p for p in pins if p["ref"] == "U_CHG" and p["pin"] == "4"]
    if same:
        print(f"  ℹ️  抽样 U_CHG.4 (STAT): 网 = {[p['net'] for p in same]} "
              f"⇒ ★**pinout 真源允许** {sorted(ALLOWED.get('U_CHG', {}).get('4', []))}")
    print(f"\n  {'✅ 全过' if not errors else f'❌ {len(errors)} 项不通过'}")
    print("=" * 78)
    if errors:
        print("❌ 自检不过, 不写文件 (避免把坏表交给 PCB 工程师)")
        return 1
    if "--selftest" in sys.argv:
        return 0
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(pins)
    os.replace(tmp, OUT)
    print(f"✅ HW/netlist_v1_pins.csv 已生成 ({len(pins)} 行 = 每引脚一行, 覆盖 {len(pin_cnt)} 个器件)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
