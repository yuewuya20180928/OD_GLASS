#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_spec_page_367.py —— ★★【ISS-367 · CONT1 · 规格页定点补写】★★
  目标页: MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md (★本单新建页·非老页★)
  动作:
    ① §2 三张表/段补【证据等级】五级白名单标记 (⇒ 本单机器闸 L4 的「§2 一个都没标」真红要消)
    ② §1.3 / §5.1 三处算错的差值按实算改正 (⇒ 本趟实跑复核出来的)
    ③ §3.1 item 8「最近落位封装原点」后三档改正 (★上一趟写错了 ⇒ 实算值见 logs/iss367/08_nearest_origin.json★)
    ④ §2.1 / §3.1 各补一条漏掉的改写行 (★上一趟清单漏了 items[].spec 与 S6_CALIBER 的 S6 落位约束行★)
    ⑤ 新增 §2.4 = 本趟 (CONT1) 的自审更正记录
  ★只改这一个文件 · 行号 = 改前文件的原始行号 ★
"""
from __future__ import annotations
import os
import shutil
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SPEC = os.path.join(PROJ, "MECH", "BOARD_ONEPASS_S10_LED_SPEC_SYNC.md")
LOGD = os.path.join(PROJ, "logs", "iss367")

E_MEASURE = " | ★`[实测]`★ |"
E_INFER = " | ★`[推算]`★ |"

# (行号, [(old, new), ...])
OPS = [
    # ---- ① §1.3 差值改正 (★本趟实跑复核★) ----
    (87, [('★X 对称化 · Y 上下各长★', '★X 对称化 (★铜箔宽 2.900 → 2.850★) · Y 向下多长 0.050 / 向上多长 0.450★')]),
    (88, [('★X 左沿 +0.675 / 右沿 +0.725 · Y 两端各内缩 0.050★',
           '★X 左沿 +0.675 / 右沿 +0.725 · Y 下沿内缩 0.050 / 上沿内缩 0.450★')]),
    (90, [('★**宽 +0.050** · 整体右移 +0.675★', '★**宽 +0.050** · 左沿 +0.675 / 右沿 +0.725 (★带心 +0.700★)★')]),
    (91, [('★整体右移 +0.675 · Y 向各压 0.025★',
           '★X 左沿 +0.675 / 右沿 +0.300 (★带宽 1.310 → 0.935 = −0.375★) · Y 下沿 −0.025 / 上沿 −0.575 (★带高 4.200 → 3.650 = −0.550★)★')]),
    # ---- ② §2.1 表头 + 13 行证据级 + 补第 14 行 ----
    (136, [('| # | 位置 | 改什么 | 性质 |', '| # | 位置 | 改什么 | 性质 | 证据级 |')]),
    (137, [('|---|---|---|---|', '|---|---|---|---|---|')]),
    # ---- ③ §2.3 表头 ----
    (239, [('| # | 位置 | 改前 | 改后 |', '| # | 位置 | 改前 | 改后 | 证据级 |')]),
    (240, [('|---|---|---|---|', '|---|---|---|---|---|')]),
    # ---- ④ §3.1 item 8「最近落位封装原点」后三档 = 实算值 (★上一趟写错★) ----
    (267, [('(8.550, 63.675) / (8.475, 63.775) / (8.375, 63.875) / (8.775, 64.175)',
            '(8.550, 63.675) / (7.715, 63.775) / (7.815, 63.875) / (8.115, 64.175)')]),
    # ---- ⑤ §5.1 最近落位带「窄 0.405」⇒ 实算 0.375 ----
    (349, [('★比旧口径窄 0.405·右沿 +0.300★', '★比旧口径窄 0.375 (★带宽 1.310 → 0.935★)·左沿 +0.675 / 右沿 +0.300★')]),
]

# (行号, 追加文本)  ★追加在该行末尾★
APPENDS = (
    [(ln, E_MEASURE) for ln in (138, 139, 140, 141, 142, 143, 145, 146, 147, 148, 149, 150)]
    + [(144, E_INFER)]
    + [(ln, E_MEASURE) for ln in (241, 242, 243, 244, 245, 246, 247, 248)]
)

# (插入锚点行号, 追加文本)  ★追加在锚点行之后★
INSERTS = [
    # §2.1 第 14 行 (★上一趟清单漏掉的一处同源行★)
    (150, '| ★**14** ★ | ★机器块 `items[]` 里 `MECH-LED-G` 的 `spec` 字段 (一行) ★ '
          '| ★两假设空间 + 走线范围 → §1.3 AFTER (★它与 `led.hypothesis_hole` / `led.hypothesis_nohole` 是同一份空间数据·不改就自相矛盾★)★ '
          '| ★定点替换★' + E_MEASURE + ' |'),
    # §2.2 末尾的证据声明
    (235, '★**★ ⇒ 本节七个块的每一个数 = `python3 MECH/check_onepass_s10_led_spec_sync.py --compute` 的实跑读数 '
          '(★输出留证 `logs/iss367/07_compute_after.json`★) ⇒ ★`[实测]`★; 「改前值」= 2026-11-23 18:30 的两页原文 '
          '(★逐字节备份 `logs/iss367/10_pre_MECH_SYNC.md` / `10_pre_S6_CALIBER.md`★) ⇒ ★`[实测]`★; '
          '改后的两页已由本单机器闸的 **L3** 逐条对账 (★`logs/iss367/13_gate_run_after_rewrite.txt`·L3 绿★) ⇒ ★`[实测]`★ ★'),
    # §3.1 第 16 行 (★上一趟清单漏掉的一处同源行★)
    (274, '| ★**16** ★ | ★§9.3 S6 落位约束第 ④ 条 (★`D_LED_G` 窗口行★) ★ '
          '| ★整高自由带 X 1.550..3.450 + X 72.540..73.660 (Y 1.450..98.950); 最近落位带 X 6.940..8.250 × Y 63.700..67.900 ★ '
          '| ★整高自由带 X 2.225..3.250 + X 73.215..74.385 (Y 1.500..98.500); 最近落位带 X 7.615..8.550 × Y 63.675..67.325 ★ '
          '| ★定点替换★' + E_MEASURE + ' |'),
    # §3.1 末尾的更正声明
    (275, '★**★ ⇒ 【ISS-367 CONT1 实跑复核 · 更正】★ ★: 上表 item 8 的「最近落位封装原点」后三档 ★**上一趟写成 '
          '(8.475, 63.775) / (8.375, 63.875) / (8.775, 64.175) ⇒ 是按「x1 ± clr」硬推的, 不是 `led_space()` 的 '
          '`nearest_to_r_led_g[0].origin` 实跑值** ★ ⇒ ★**实算值 = (7.715, 63.775) / (7.815, 63.875) / (8.115, 64.175)** ★ '
          '(★逐档留证 `logs/iss367/08_nearest_origin.json`·同一函数同一口径复跑 BEFORE 得 (8.250, 63.700) / (8.150, 63.800) / '
          '(8.050, 63.900) / (8.420, 64.200) 与改前页逐字相同 ⇒ 证明这次复核与上一趟同源★) ⇒ ★**已按实算值改写 ★** '
          '(★`[实测]`★) ⇒ ★**本单两页的落位原点一栏以实算值为准** ★'),
    # §2.4 = 本趟自审更正记录 (★追加在 §2.3 末尾★)
    (250, '### ★§2.4 【ISS-367 CONT1 · 本趟实跑复核的自审更正记录】 (★2026-11-23 18:3x · ★每一行都有留证路径★) ★\n'
          '\n'
          '| # | 上一趟的问题 | 本趟怎么处理 | 留证 | 证据级 |\n'
          '|---|---|---|---|---|\n'
          '| ★**1** ★ | ★**本单机器闸的 L4 有【自身假红】** ★ —— 它把「方括号包裹的数值区间 / 数组字面量」(`[−0.750, +2.150]` · '
          '`["placeable"]`) 也当「证据等级标记」来判 ⇒ 9 条假红 ★ | ★**修法只落在产生点** ★: 只把「内容全为中文表意文字 + ASCII 数字」的 '
          '方括号 token 当等级候选 ⇒ ★**五级白名单方向 (五级) 一字未改** ★ ⇒ `[官方]` / `[推断]` 这类非白名单标签照样红 | '
          '`MECH/check_onepass_s10_led_spec_sync.py` (★`_evidence_tokens()`★) | ★`[实测]`★ |\n'
          '| ★**2** ★ | ★**§2 一节一个证据等级都没标** (★机器闸 L4 的真红★) | ★**§2.1 / §2.2 / §2.3 三张表逐行补了证据级** ★ | '
          '`logs/iss367/13_gate_run_after_rewrite.txt` (★L4 绿★) | ★`[实测]`★ |\n'
          '| ★**3** ★ | ★**上一趟 §2.1 / §3.1 的改写清单漏了两处同源行** ★ ⇒ ★**① `MECH/BOARD_ONEPASS_MECH_SYNC.md` 机器块 '
          '`items[]` 里 `MECH-LED-G` 的 `spec` 字段** (★它与 `led.hypothesis_*` 是同一份空间数据★) ★**② '
          '`MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 的 §9.3 S6 落位约束第 ④ 条 (`D_LED_G` 窗口行)** ★ | '
          '★**两条都补进清单并已改写** ★ (★§2.1 第 14 条 / §3.1 第 16 条★) ⇒ ★**留在这两处不改就与机器块自相矛盾** ★ | '
          '`logs/iss367/11_diff_MECH_SYNC.txt` · `logs/iss367/11_diff_S6_CALIBER.txt` | ★`[实测]`★ |\n'
          '| ★**4** ★ | ★**§3.1 item 8 的「最近落位封装原点」后三档写错了** (★硬推, 不是实跑★) | ★**按 `led_space()` 的 '
          '`nearest_to_r_led_g[0].origin` 实跑改正** ★ ⇒ (7.715, 63.775) / (7.815, 63.875) / (8.115, 64.175) | '
          '`logs/iss367/08_nearest_origin.json` | ★`[实测]`★ |\n'
          '| ★**5** ★ | ★**§1.3 与 §5.1 有三处差值算错** (★「Y 两端各内缩 0.050」/「整体右移 +0.675」/「Y 向各压 0.025」/「窄 0.405」★) '
          '| ★**全部按实算改正** ★ | 同上 (`logs/iss367/07_compute_after.json` · `08_nearest_origin.json`) | ★`[实测]`★ |\n'
          '\n'
          '★**★ ⇒ ★**本单规格页 + 两处定点改写 + 一条机器闸 = 同一套数 (★`2183` / `2.225..3.250` + `73.215..74.385` / '
          '`2183·2241·2253·2197` / 「不再单调」★) ⇒ ★**三份同源 · 不可能打架** ★'),
]


def main() -> int:
    apply = "--apply" in sys.argv
    with open(SPEC, encoding="utf-8") as fh:
        orig = fh.read()
    lines = orig.split("\n")
    for ln, subs in OPS:
        idx = ln - 1
        if idx >= len(lines):
            raise AssertionError("行号 %d 越界" % ln)
        cur = lines[idx]
        for old, new in subs:
            if cur.count(old) != 1:
                raise AssertionError("第 %d 行待改串出现 %d 次 (必须恰好 1 次): %r"
                                     % (ln, cur.count(old), old))
            cur = cur.replace(old, new, 1)
        if cur == lines[idx]:
            raise AssertionError("第 %d 行改完没变" % ln)
        lines[idx] = cur
    # 追加证据级列 (★按原始行号 · 先做 · 因为它不增行 · 所以不破坏插入锚点★)
    for ln, text in sorted(APPENDS, key=lambda x: -x[0]):
        idx = ln - 1
        if not lines[idx].rstrip().endswith("|"):
            raise AssertionError("第 %d 行不是表格行: %r" % (ln, lines[idx]))
        lines[idx] = lines[idx].rstrip() + text
    # 追加 (★按原始行号, 倒序插入以免行号漂移★)
    for ln, text in sorted(INSERTS, key=lambda x: -x[0]):
        lines.insert(ln, text)
    new = "\n".join(lines)
    print("★ 规格页: 定点改写 %d 行 · 追加 %d 处" % (len(OPS), len(INSERTS)))
    print("  · 改前字节 = %d · 改后字节 = %d" % (len(orig.encode()), len(new.encode())))
    if not apply:
        print("★ dry-run (未写盘) · 加 --apply 真改")
        return 0
    shutil.copy2(SPEC, os.path.join(LOGD, "10_pre_SPEC_PAGE.md"))
    with open(SPEC, "w", encoding="utf-8") as fh:
        fh.write(new)
    print("★ 已写入 (改前备份 = logs/iss367/10_pre_SPEC_PAGE.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
