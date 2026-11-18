#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-304 · 台账口径 `fresh` 值同步脚本 (★路 B·永不再漂★)

=====================================================================
★**为什么需要它 (★ISS-304 · hw-lead · 2026-11-18★)** ★★:

    ★**清单页 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 是生成器 `state/_iss277_build_preflight.py` 的产物** ★
    ⇒ ★它由生成器自己从落表台账现读 (★ISS-304 已把这条接进生成器★)★ ★
    ★**但作业包页 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 不是那个生成器写的** ★
    ⇒ ★**它是 ISS-289 那次用 `state/_append_iss289_state_values.py` 追加进去的** ★
    ⇒ ★**那 4 条台账口径登记在作业包页里 ⇒ 必须靠本脚本同步 (★另一条途径★)★ ★

★**本脚本干三件事 (★顺序不许换★)** ★★:
    ① ★**生成器的输入 sidecar** `state/_iss277_preflight_appendix.md` ⇒ ★把那 4 条的 `fresh` 格刷成台账现值★ ★
       (★sidecar 是生成器的输入·不是产物 ⇒ 刷它不违反「不许手改生成器产物」★) ★
    ② ★**作业包页** `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` ⇒ ★把那 4 条的 `fresh` 格刷成台账现值★ ★
       (★就地改那 4 个 32 位十六进制串·长度不变 ⇒ 行号不动★) ★
    ③ ★**作业包页追加 ISS-304 的订正块** (★从 sidecar 取·保证两份页面同一份文字★) ★
       ⇒ ★说明「§附录 ④ / §8.2.3 ⑬ 那三个数 = ISS-283 那一跳的快照, 现行值以登记表那 4 格为准」★ ★

★**三条铁律** ★★:
    ① ★**fail-closed** ★ ⇒ ★台账读不到 / 块认不出 ⇒ ★一个字节都不写·rc≠0★ ★
    ② ★**幂等** ★ ⇒ ★再跑一次 ⇒ 页 md5 逐字节相同 (★不写就不算改★)★ ★
    ③ ★**两份页面的登记表必须逐字节一致** ★ ⇒ ★跑完自检一遍·不一致 ⇒ rc≠0★ ★

★**用法** ★:
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    python3 state/_iss304_sync_state_baseline_md5.py            ; echo "rc=$?"
    ★★沙盒跑法★★: ★`WORKPACKET_PROJ=<沙盒根> python3 state/_iss304_sync_state_baseline_md5.py`★
"""

from __future__ import annotations

import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import _iss304_ledger_fresh as lf                       # noqa: E402

REAL_ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PROJ = os.environ.get("WORKPACKET_PROJ") or os.environ.get("PREFLIGHT_PROJ") or REAL_ROOT

SIDECAR_REL = "state/_iss277_preflight_appendix.md"
WP_REL = "HW/PCB/BOARD_ONEPASS_WORKPACKET.md"
ISS304_TAG = "ISS304:MD5_ANCHOR"


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def extract_block(txt: str, tag: str) -> str | None:
    """★取 `<!-- <tag>:BEGIN -->` 与 `<!-- <tag>:END -->` 之间的整块原文 (★含标记★) ★"""
    m = re.search(r"<!-- %s:BEGIN -->\n(.*?)<!-- %s:END -->" % (tag, tag), txt, re.S)
    return m.group(0) if m else None


def main() -> int:
    sidecar_p = os.path.join(PROJ, SIDECAR_REL)
    wp_p = os.path.join(PROJ, WP_REL)
    for p in (sidecar_p, wp_p):
        if not os.path.exists(p):
            print("★✘ %s 不存在 ⇒ 拒写 (★fail-closed★)" % p)
            return 1

    # ---------------------------------------------------------------- ① sidecar
    sc_md5_before = md5(sidecar_p)
    sc = read(sidecar_p)
    block304_raw = extract_block(sc, ISS304_TAG)
    if not block304_raw:
        print("★✘ sidecar 里读不到 `%s:BEGIN/END` 块 ⇒ 拒写 (★fail-closed·追加式订正块不许丢★)"
              % ISS304_TAG)
        return 1
    # ★ISS-304 块里的台账现值占位符 ⇒ 现读 (★读不到 ⇒ 拒写★) ★
    try:
        block304 = lf.resolve_placeholders(block304_raw, PROJ)
    except lf.LedgerResolveError as e:
        print("★✘ %s" % e)
        return 1
    try:
        sc_new, sc_ch = lf.resolve_state_block_text(sc, PROJ)
    except lf.LedgerResolveError as e:
        print("★✘ %s" % e)
        return 1
    if sc_new != sc:
        write(sidecar_p, sc_new)
    print("★① sidecar %s: %d 处台账口径 fresh 改了 (★md5 %s ⇒ %s★)"
          % (SIDECAR_REL, len(sc_ch), sc_md5_before, md5(sidecar_p)))

    # ---------------------------------------------------------------- ② 作业包页
    wp_md5_before = md5(wp_p)
    wp = read(wp_p)
    try:
        wp_new, wp_ch = lf.resolve_state_block_text(wp, PROJ)
    except lf.LedgerResolveError as e:
        print("★✘ %s" % e)
        return 1
    # ★③ ISS-304 订正块: 在位 ⇒ 原样对齐; 不在位 ⇒ 追加在页尾 (★追加式·老字一字不删★) ★
    old_block = extract_block(wp_new, ISS304_TAG)
    if old_block is None:
        sep = "" if wp_new.endswith("\n") else "\n"
        wp_new = wp_new + sep + "\n" + block304.rstrip("\n") + "\n"
        print("★③ 作业包页: 追加 ISS-304 订正块 (★页尾·老字一字未删★)")
    elif old_block != block304:
        wp_new = wp_new.replace(old_block, block304)
        print("★③ 作业包页: ISS-304 订正块与 sidecar 不一致 ⇒ 已对齐")
    else:
        print("★③ 作业包页: ISS-304 订正块已在位且与 sidecar 一致 (★不重复追加★)")
    if wp_new != wp:
        write(wp_p, wp_new)
    print("★② 作业包页 %s: %d 处台账口径 fresh 改了 (★md5 %s ⇒ %s★)"
          % (WP_REL, len(wp_ch), wp_md5_before, md5(wp_p)))
    for c in wp_ch:
        print("     - %s (%s): %s ⇒ %s" % (c["id"], c["target"], c["old"], c["new"]))

    # ---------------------------------------------------------------- 自检: 两份页面逐字节一致
    scj, _ = lf.read_registry_json(read(sidecar_p))
    wpj, _ = lf.read_registry_json(read(wp_p))
    if scj is None or wpj is None:
        print("★✘ 自检失败: 读不到某一份的 `state_baseline` JSON 块 ⇒ rc≠0")
        return 1
    if scj != wpj:
        print("★✘ 自检失败: sidecar 与作业包页的 `state_baseline` 登记表不逐字节一致 ⇒ rc≠0")
        return 1
    print("★✔ 自检: sidecar 与作业包页的 `state_baseline` 登记表逐字节一致 (%d 字节)" % len(wpj))
    print("★★落表后重锚流程: ① python3 state/_iss277_build_preflight.py ② python3 %s"
          % os.path.relpath(__file__, REAL_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
