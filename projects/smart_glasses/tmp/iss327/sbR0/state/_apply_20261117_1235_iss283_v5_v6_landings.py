#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-283 · 把 V-5 (W-4 写法A) / V-6 (G-5 亮度档) 两个落表配方塞进 state/land_v_values.py

★**为什么要机器塞 (★不许人手抄·抄错就崩★)**:
  · V5 的【旧块】必须与 `state/gen_netlist.py` 里的原文【逐字节相同】⇒ 本脚本从真源现读
  · V5/V6 的【新块】从 logs/iss283/v5_new_block.txt / v6_new_block.txt 现读
  ⇒ 塞完自己再逐字节对一遍 ⇒ 对不上就当场报错 (★零写盘★)
"""
import io
import os
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
GEN = os.path.join(ROOT, "state/gen_netlist.py")
LV = os.path.join(ROOT, "state/land_v_values.py")
V5NEW = os.path.join(ROOT, "logs/iss283/v5_new_block.txt")
V6NEW = os.path.join(ROOT, "logs/iss283/v6_new_block.txt")

gen_txt = open(GEN, encoding="utf-8").read()
gen_lines = gen_txt.split("\n")

# ── 旧块: Q_PG 三条 add() (PWR_ON / BAT_SW / PWR_GOOD) ──
i_pwron = next(i for i, l in enumerate(gen_lines) if l.strip().startswith('add("P1", "PWR_ON", "Q_PG"'))
i_batsw = next(i for i, l in enumerate(gen_lines) if l.strip().startswith('add("P1", "BAT_SW", "Q_PG"'))
i_pgood = next(i for i, l in enumerate(gen_lines) if l.strip().startswith('add("P1", "PWR_GOOD", "Q_PG"'))
assert i_pwron < i_batsw < i_pgood, (i_pwron, i_batsw, i_pgood)
# PWR_GOOD 块结束于下一个非空行之前
j = i_pgood
while j < len(gen_lines) and gen_lines[j].strip():
    j += 1
V5_OLD = "\n".join(gen_lines[i_pwron:j]) + "\n"

# ── 旧块: P7 LED 串阻那条 add() ──
i_led = next(i for i, l in enumerate(gen_lines)
             if l.strip().startswith('add("P7", f"LED_{col}_D"'))
V6_OLD = "\n".join(gen_lines[i_led:i_led + 3]) + "\n"

V5_NEW = open(V5NEW, encoding="utf-8").read()
V6_NEW = open(V6NEW, encoding="utf-8").read()
if not V5_NEW.endswith("\n"):
    V5_NEW += "\n"
if not V6_NEW.endswith("\n"):
    V6_NEW += "\n"

# ── 自检: 新块必须是合法 Python 片段, 且行数与旧块一致 (★不许引发行号漂移★) ──
n_old5, n_new5 = V5_OLD.count("\n"), V5_NEW.count("\n")
n_old6, n_new6 = V6_OLD.count("\n"), V6_NEW.count("\n")
assert n_old5 == n_new5, ("V5 行数变了", n_old5, n_new5)
assert n_old6 == n_new6, ("V6 行数变了", n_old6, n_new6)
for name, blk in (("V5_NEW", V5_NEW), ("V6_NEW", V6_NEW)):
    if "'''" in blk or "\\" in blk:
        sys.exit("★★ 块里有 ''' 或反斜杠 ⇒ 不能用三引号字面量 (★换 repr 写法★)")

# ── 塞进 land_v_values.py ──
lv = open(LV, encoding="utf-8").read()
if "V5_BLOCK_OLD" in lv:
    print("✅ 已经塞过了 (★幂等·不重复塞★)")
    sys.exit(0)

ANCHOR = "# ═══════════════════════════════════════════════════════════════════════════\n# 5 · 白名单\n"
if ANCHOR not in lv:
    sys.exit("★★ 锚点没找到 (★白名单段标题变了?★)")

BLOCK = (
    "# ═══════════════════════════════════════════════════════════════════════════\n"
    "# 4-B · V-5 (W-4 / G-1: `Q_PG` 写法 A) + V-6 (G-5 / W-6: LED 亮度档)\n"
    "#\n"
    "# ★★**为什么这两个也走落表器 (★而不是人手改 CSV·★2026-11-17 12:1x 实测★)** ★★:\n"
    "#   ① ★**落表 = 机器留痕** ⇒ 备份/回滚/台账 §16 新旧 md5/老板凭据/门禁实跑 全部自动 ★\n"
    "#   ② ★**人手改 CSV 会被下次生成覆盖** ⇒ 改的必须是【真源 `state/gen_netlist.py`】★★\n"
    "#   ③ ★**两条都改了【实体身份 / 器件阻值】** ⇒ 必须过【行号锚点守卫】与【落表后门禁】★ ★\n"
    "#\n"
    "# ★**老板凭据 (★机器转录·不代拍★)** ★:\n"
    "#   · V-5 / W-4 / G-1 = `boss_w4_q_pg_topology_20261117` (★pm.yaml ★2026-11-17 09:49★) ★\n"
    "#   · V-6 / G-5 / W-6 = `boss_g5_led_brightness_20261117` (★pm.yaml ★2026-11-17 09:49★) ★\n"
    "# ═══════════════════════════════════════════════════════════════════════════\n"
    "\n"
    "V5_BLOCK_OLD = '''" + V5_OLD + "'''\n"
    "\n"
    "V5_BLOCK_NEW = '''" + V5_NEW + "'''\n"
    "\n"
    "V6_BLOCK_OLD = '''" + V6_OLD + "'''\n"
    "\n"
    "V6_BLOCK_NEW = '''" + V6_NEW + "'''\n"
    "\n"
    "\n"
    "def netlist_auth_records(root: str, specs: list[tuple[str, str, str]]) -> list[dict]:\n"
    "    '''★网表身份变更授权记录 (★通用版·身份列 = [ref, net]★) ★\n"
    "\n"
    "    ★**为什么要有它 (★ISS-283 · B1·V-5 落表改的是 pad↔net 的对调★)**:\n"
    "      落表改 net ⇒ 那一行的实体身份 (ref+net) 变了 ⇒ 行号锚点守卫会判红\n"
    "      ⇒ 必须在台账里登记【旧身份 → 新身份】⇒ 守卫查到授权记录才放行 ★\n"
    "    ★**旧行号按 (ref, old_net) 现读真源** ⇒ 不许手抄行号 ★\n"
    "    '''\n"
    "    out: list[dict] = []\n"
    "    cols = [\"ref\", \"net\"]\n"
    "    try:\n"
    "        with open(os.path.join(root, NETLIST_CSV), encoding=\"utf-8\") as fh:\n"
    "            rows = list(csv.DictReader(fh))\n"
    "    except Exception:\n"
    "        return out\n"
    "    for ref_want, old_net, new_net in specs:\n"
    "        line = None\n"
    "        row = None\n"
    "        for i, r in enumerate(rows, start=2):\n"
    "            if ((r.get(\"ref\") or \"\").strip() == ref_want\n"
    "                    and (r.get(\"net\") or \"\").strip() == old_net):\n"
    "                line, row = i, r\n"
    "                break\n"
    "        if line is None or row is None:\n"
    "            continue\n"
    "        old_vals = [(row.get(c, \"\") or \"\").strip() for c in cols]\n"
    "        new_vals = list(old_vals)\n"
    "        ni = cols.index(\"net\")\n"
    "        old_vals[ni] = old_net\n"
    "        new_vals[ni] = new_net\n"
    "        out.append({\"file\": NETLIST_CSV, \"table\": \"netlist\", \"line\": line,\n"
    "                    \"old\": old_vals, \"new\": new_vals})\n"
    "    return out\n"
    "\n"
    "\n"
    "def _q_pg_pad_nets(root: str) -> list[str]:\n"
    "    '''★读盘: `Q_PG` 的三条 `add()` 在网表里落成哪三个网 (★行序 = pad 序★)'''\n"
    "    out: list[str] = []\n"
    "    try:\n"
    "        with open(os.path.join(root, NETLIST_CSV), encoding=\"utf-8\") as fh:\n"
    "            for r in csv.DictReader(fh):\n"
    "                if (r.get(\"ref\") or \"\").strip() == \"Q_PG\":\n"
    "                    out.append((r.get(\"net\") or \"\").strip())\n"
    "    except Exception:\n"
    "        return out\n"
    "    return out\n"
    "\n"
    "\n"
    "def v5_recipe(value: str, root: str = \"\", arch_req: str = \"\", model_req: str = \"\",\n"
    "              ev_req: str = \"\") -> Decision:\n"
    "    '''★V-5 (W-4 / G-1): `Q_PG` 写法 A = S=BAT_SW / D=ON / G=PG ★'''\n"
    "    d = Decision(v=\"V-5\", value=value)\n"
    "    if value != \"A\":\n"
    "        d.rejected = (\"★★**V-5 只认 `A` (★写法 A = S=BAT_SW / D=ON / G=PG★)**★★ ⇒ \"\n"
    "                      \"★**老板 2026-11-17 09:49 只拍了写法 A** (★pm.yaml \"\n"
    "                      \"`boss_w4_q_pg_topology_20261117`★) ⇒ 其它取值一律打回★\")\n"
    "        return d\n"
    "    d.delta = 0          # ★网表侧 0 条转绿 (★pad 序要对 ⇒ 板那一趟重画 land 才转绿★)★\n"
    "    d.board_delta = 0\n"
    "    d.v2_readout.append(\n"
    "        \"★★**落表动作 (W-4 / G-1 写法 A)**: `state/gen_netlist.py` 里 `Q_PG` 的三条 `add()` \"\n"
    "        \"★**整块重排 (★pad1↔pad3 的网互换★) + 三行 note 改写成写法A**★ ⇒ \"\n"
    "        \"★**pad1 = PWR_GOOD (G) · pad2 = BAT_SW (S) · pad3 = PWR_ON (D)**★\")\n"
    "    d.v2_readout.append(\n"
    "        \"★★**老板凭据**: 2026-11-17 09:49「按照你的建议执行」⇒ pm.yaml \"\n"
    "        \"`boss_w4_q_pg_topology_20261117` (★已录★) ⇒ ★**落表器只机器转录·不代拍**★\")\n"
    "    if root:\n"
    "        _cur = _q_pg_pad_nets(root)\n"
    "        if _cur == [\"PWR_GOOD\", \"BAT_SW\", \"PWR_ON\"]:\n"
    "            d.errors.append(\"★★【已落过】`Q_PG` 的 pad 序已经是写法 A \"\n"
    "                            \"(PWR_GOOD / BAT_SW / PWR_ON) ⇒ ★**拒绝重复落 (★零写盘★)**★\")\n"
    "            return d\n"
    "        if _cur != [\"PWR_ON\", \"BAT_SW\", \"PWR_GOOD\"]:\n"
    "            d.errors.append(\"★★【状态漂移】`Q_PG` 的 pad 序不是预期的那两档之一 ⇒ \"\n"
    "                            f\"★**期望: ['PWR_ON','BAT_SW','PWR_GOOD'] (旧) 或 \"\n"
    "                            f\"['PWR_GOOD','BAT_SW','PWR_ON'] (写法A·已落过)★** ⇒ \"\n"
    "                            f\"★**实际: {_cur}**★ ⇒ 拒绝落 (★零写盘★)\")\n"
    "            return d\n"
    "    d.patches.append(Patch(GEN_NETLIST, V5_BLOCK_OLD, V5_BLOCK_NEW,\n"
    "                            \"V5-1 `Q_PG` 写法 A (★pad1↔pad3 网互换 + 三行 note 改写★)\"))\n"
    "    d.auth_changes += netlist_auth_records(root, [(\"Q_PG\", \"PWR_ON\", \"PWR_GOOD\"),\n"
    "                                                   (\"Q_PG\", \"PWR_GOOD\", \"PWR_ON\")])\n"
    "    if root and not d.auth_changes:\n"
    "        d.errors.append(\"★★★【落表授权】V-5 的身份变更授权记录生成不出来 ⇒ \"\n"
    "                        \"★**不许硬落** (★守卫查不到授权 ⇒ 一定判红·落表器会自回滚★) ⇒ 拒绝落 (★零写盘★)★★\")\n"
    "        return d\n"
    "    d.v2_readout.append(\n"
    "        \"★**身份变更授权 (★ISS-283 B1 通道★)**: \"\n"
    "        + \"; \".join(f\"L{a['line']} {a['old']} → {a['new']}\" for a in d.auth_changes))\n"
    "    d.warnings.append(\"★★**V-5 的板那一趟本工具【不做】** (★板一个字节都不碰★) ⇒ \"\n"
    "                      \"★**板上的 `Q_PG` land 仍按旧接法画 (pad1→PWR_ON / pad3→PWR_GOOD) ⇒ \"\n"
    "                      \"板那一趟必须重画 `Q_PG` 的 3 根线**★\")\n"
    "    d.warnings.append(\"★★**连带 (★如实登记·不瞒★)**: 板那一趟要么重画 land, 要么改选 D-S-G 序器件 \"\n"
    "                      \"(★那也是换封装 ⇒ 同样是板那一趟★) ⇒ ★**板只改一次那一趟的 S 步清单必须带上它**★\")\n"
    "    return d\n"
    "\n"
    "\n"
    "def v6_recipe(value: str, root: str = \"\", arch_req: str = \"\", model_req: str = \"\",\n"
    "              ev_req: str = \"\") -> Decision:\n"
    "    '''★V-6 (G-5 / W-6): LED 亮度档 = `R_LED_R` 68Ω · `R_LED_G` 55Ω (★20 mA 档★) ★'''\n"
    "    d = Decision(v=\"V-6\", value=value)\n"
    "    if value != \"20mA\":\n"
    "        d.rejected = (\"★★**V-6 只认 `20mA`**★★ ⇒ ★**老板 2026-11-17 09:49 拍的是 \"\n"
    "                      \"「选项 ② = 改 R 到 20 mA 档」**★ (★pm.yaml \"\n"
    "                      \"`boss_g5_led_brightness_20261117`★) ⇒ 其它取值一律打回★\")\n"
    "        return d\n"
    "    d.delta = 0\n"
    "    d.board_delta = 0\n"
    "    d.v2_readout.append(\n"
    "        \"★★**落表动作 (G-5 亮度档)**: `R_LED_R` = ★**68Ω ±1%**★ (红) · \"\n"
    "        \"`R_LED_G` = ★**55Ω ±1%**★ (绿) ⇒ ★**蓝 (`R_LED_B`, DNP) 不在老板拍板范围 ⇒ 保持 1k ±1%**★\")\n"
    "    d.v2_readout.append(\n"
    "        \"★★**老板凭据**: 2026-11-17 09:49「按照你的建议执行」⇒ pm.yaml \"\n"
    "        \"`boss_g5_led_brightness_20261117` (★已录★) ⇒ ★**落表器只机器转录·不代拍**★\")\n"
    "    if root:\n"
    "        try:\n"
    "            with open(os.path.join(root, NETLIST_CSV), encoding=\"utf-8\") as fh:\n"
    "                _v = {}\n"
    "                for r in csv.DictReader(fh):\n"
    "                    _rf = (r.get(\"ref\") or \"\").strip()\n"
    "                    if _rf in (\"R_LED_R\", \"R_LED_G\"):\n"
    "                        _v[_rf] = (r.get(\"value\") or \"\").strip()\n"
    "        except Exception:\n"
    "            _v = {}\n"
    "        if _v.get(\"R_LED_R\") == \"68Ω ±1%\" and _v.get(\"R_LED_G\") == \"55Ω ±1%\":\n"
    "            d.errors.append(\"★★【已落过】`R_LED_R` / `R_LED_G` 的阻值已经是 68Ω / 55Ω ⇒ \"\n"
    "                            \"★**拒绝重复落 (★零写盘★)**★\")\n"
    "            return d\n"
    "    d.patches.append(Patch(GEN_NETLIST, V6_BLOCK_OLD, V6_BLOCK_NEW,\n"
    "                            \"V6-1 LED 串阻改 20 mA 档 (★红 68Ω / 绿 55Ω★)\"))\n"
    "    d.patches.append(Patch(SPEC_JSON, '\"imp\": \"1k 串阻 → LED → GND\",',\n"
    "                            '\"imp\": \"68Ω 串阻 → LED → GND\",',\n"
    "                            \"V6-2a SPEC.json B-12 (LED_R) 的 imp\",\n"
    "                            ctx='\"signal\": \"LED_R\",'))\n"
    "    d.patches.append(Patch(SPEC_JSON, '\"imp\": \"1k 串阻 → LED → GND\",',\n"
    "                            '\"imp\": \"55Ω 串阻 → LED → GND\",',\n"
    "                            \"V6-2b SPEC.json B-13 (LED_G) 的 imp\",\n"
    "                            ctx='\"signal\": \"LED_G\",'))\n"
    "    d.warnings.append(\"★★**连带 (★如实登记·不瞒★)**: 每颗功耗 2.2 mW → 66 mW (★两颗 ≈ 0.13 W 进电池账★) · \"\n"
    "                      \"★**亮度 ×14 ⇒ 眼旁光源的 IEC 62471 分级要重算 ⇒ 登记 need 给 main (★本工具不代拍★)**★\")\n"
    "    d.warnings.append(\"★★**这两个阻值进 BOM ⇒ 板那一趟要重出 BOM + 投产包** (★但 footprint 不变 ⇒ \"\n"
    "                      \"不构成额外板改★)\")\n"
    "    return d\n"
    "\n"
    "\n"
)

lv = lv.replace(ANCHOR, BLOCK + ANCHOR, 1)
open(LV, "w", encoding="utf-8").write(lv)
print("✅ 已塞入 V-5 / V-6 配方 (★行数: V5 %d→%d / V6 %d→%d★)" % (n_old5, n_new5, n_old6, n_new6))
