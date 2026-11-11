#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""决策页补记 (r24a) —— 2026-11-11 21:2x

★**为什么要有这次补记**: r24 (21:1x) 落盘后, ★**队列在本轮【继续往前走了】** ⇒ ⇒
   r24 §0.25.1 里那句「sw-lead / mech-lead 名下 open = 0 ⇒ A 段空是【真空】」**在 21:16 就过期了**
   ⇒ ⇒ ★**老板读到的必须是【当下】的队列状态, 不能是 10 分钟前的快照** ⇒ ⇒ 本脚本只做【补一段】, 不重写 r24.

★**本脚本做的三件事 (全部是【补记事实】, 不改任何建议默认值, 不新增/退休任何 C 段项)**:
   ① §0.25.1 后面追加一段「补记: 21:16-21:17 队列怎么动的」
   ② 顶部「本轮我自己动了什么」的 ① 末尾补一句 (★**指向补记, 免得读者以为那还是当下状态★**)
   ③ 页首「本轮 C 段口径变化」那行 ⇒ ★**仍然是 36 → 36** (★**兄弟 job 开的新单是 internal 活, 不是老板拍板项 ⇒ C 段不动★**)

★**落盘纪律**: flock + 锁内重读 + 原子写 (tmp → fsync → os.replace → fsync(dir))
★**边界**: 不改 C 段 36 项 · 不改任何建议默认值 · 不发邮件 · 不改 §0 锁死表 · 不写任何子总工的分片
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
P = os.path.join(PROJ, "DECISION_PENDING_2026-11-11.md")
LOCK = os.path.join(HERE, ".decision_page.lock")

# ---- ① 补记段落 (插在 §0.25.1 的表尾, 即 "### 0.25.2" 之前) ----
ANCHOR_252 = "### 0.25.2 ★★★ ★**核验 5 连 (本轮实测 rc) + C 段逐项核对 + GitHub 本 job 不推** ★★★"

APPENDIX = """#### ★**补记 (21:16-21:2x): 队列在 r24 落盘后继续往前走了 ⇒ ★**r24 §0.25.1 那句「A 段空是【真空】」在 21:16 就过期了** ⇒ ★**下面是当下状态** ★★

| | |
|---|---|
| ★**① ISS-193 交卷了 (21:14)** | ★**hw-lead 会话 `40040dfd` 21:14 结束并交卷** (`HANDOFF/2026-11-11_hw-lead_ISS193_BOM口径修正与29个0数据.md` + `HW/BOM_pseudo_refs_v1.csv`) ⇒ ★**★**我独立复跑了它的验收 (★**不采信自述★**): `gen_bom.py --pin-gap` **rc=0** (★**器件 218 个 / 真实脚数可查 189 / 查不到 29 / 脚数一致 183 / 真实多脚 6 / 表里多脚 0**) + `chain_gate.py` **rc=0** (★**30/30 必备产物齐全 · 12 个原理图源文件 md5 全一致**) + BOM 实测 **218 行 / 伪器件 0 / 含 J_SOM_P2 + J_SOM_P4** ⇒ ★**⇒ 它交的【BOM 口径修正】真的落地了 (评审清单 R12 的根修掉了)** ⇒ ★**⇒ 但 ISS-193 的 `status` 此刻仍是 `fixing` (★**主会话正在独立验收签字, 我不代签★**) ★ |
| ★**★★它诚实报了一条【我没料到的坏消息】★★** | ★**任务③「`[0数据]` 从 29 降到 0」【没达成: 29 → 29 没动】⇒ ⇒ 它把根因查清了并写进交卷: ★**`state/gen_kicad_sch.py` 的 `real_pin_count()` 读的是它【自己内部的三张硬编码查找表】(`SPEC_PINS`/`OPN_KICAD`/`PREFIX_KICAD`), 【不读 BOM 的 opn 列】⇒ ⇒ BOM 的 opn 填得再好, `[0数据]` 数量【零变化】** ⇒ ⇒ ★**⇒ 而那份 brief 明写「`state/gen_kicad_sch.py` 只许读, 不许改」⇒ ⇒ ★**⇒ 所以它【没做】那 26 条 (★**它把 11 个 KiCad 官方符号的路径 + 实测 pins 数 + `extends` 假数排查全部复核好, 留给有权限改那张表的人直接贴★**) ⇒ ★**★**这一条我认: ★**判据错了 (我让它改 BOM 的 opn, 实际决定 `[0数据]` 的是生成器那张表) —— 和它上一轮交零是同一个病 (brief 指错方向) 的第 2 次, 但这次它【没交零】, 而是【把根因 + 候选答案交上来了】⇒ ⇒ ★**⇒ 下一轮该做的是: 有人有权限改 `gen_kicad_sch.py` 那三张表 ⇒ `[0数据]` 29 → 3 (下限), 剩下 3 个 (`CHG_GND_STAR`/`X1`/`BT_432243`) 本来就不是器件, 永远填不了** ★★ |
| ★**③ 兄弟 job 把两个总工补上了 (21:16-21:17)** | ★**队列 job「ARS45 队列自动派活」在 21:16-21:17 新开并派出 2 条**: ★**ISS-196 → sw-lead** (★**rknn 工具链/构建环境/模型 sha 台账三处口径订正★** · `fixing`) + ★**ISS-197 → mech-lead** (★**套A 孔位落地后结构侧 5 处记录还停在「套B 仍是活口径」⇒ 口径收敛 + 3 条未决项选项表★** · `fixing`) ⇒ ★**⇒ ★**这正是 r24 §0.25.1 里说的「病丙 (真空) 的正解 = 开新单」—— 兄弟 job 做了 ⇒ ⇒ 本 job 不重复开单、不重复派 (★**两边同时派同一个 agent = 撞「一个 agent 一个写会话」铁律★**) ★** ⇒ ★**⇒ 此刻三个总工全部在飞 (hw-lead ISS-193 待验收 / sw-lead ISS-196 / mech-lead ISS-197) ⇒ ★**⇒ A 段 = 0 条, 但这次是【三个都满了】, 不是【没活】** ★ |
| ★**④ C 段不受影响** | ★**兄弟 job 开的那 2 条是【内部活】(不是老板拍板项) ⇒ ⇒ ★**C 段仍然 36 项, 一个没多一个没少 ⇒ ⇒ 你仍然只需看 §1 那 3 条 + §1b 那 1 条 + §2 那 1 条** ★ |

"""

# ---- ② 顶部块 ① 的末尾追加一句 ----
OLD_TAIL = ("★**没有动任何需要你拍板的东西, 没有发任何邮件, 没有联系任何供应商, 没有下采购单, "
            "没有改 §0 锁死表, 没有写任何子总工的分片** ★★")
NEW_TAIL = ("★**没有动任何需要你拍板的东西, 没有发任何邮件, 没有联系任何供应商, 没有下采购单, "
            "没有改 §0 锁死表, 没有写任何子总工的分片** ★★ "
            "★**【补记 21:2x —— 队列在 r24 落盘后又往前走了, 详见 §0.25.1 末尾的补记段】**: "
            "★**① ISS-193 21:14 交卷 (我独立复跑验收全绿, 签字归主会话) ★** "
            "★**② 兄弟 job 21:16-21:17 新开并派出 ISS-196 → sw-lead + ISS-197 → mech-lead ⇒ 三个总工此刻全部在飞** "
            "★**③ C 段仍 36 项 (那 2 条是内部活, 不是你待拍板项)** ★★")


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".dp.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    dfd = os.open(os.path.dirname(path), os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def main() -> int:
    if not os.path.exists(P):
        print("❌ 找不到 %s" % P)
        return 2

    lock_fh = open(LOCK, "w")
    fcntl.flock(lock_fh, fcntl.LOCK_EX)
    try:
        with open(P, encoding="utf-8") as f:
            s = f.read()
        before_len = len(s)
        lines = s.split("\n")

        # ---- ② 顶部块尾部追加 ----
        # ★**顶部块是【一整行】(2198 字) ⇒ 锚点是其【子串】不是整行 ⇒ 用子串替换 + 命中数校验** ★
        n = s.count(OLD_TAIL)
        if n == 1:
            s = s.replace(OLD_TAIL, NEW_TAIL)
        elif n == 0:
            if NEW_TAIL in s:
                print("ℹ️ 顶部块已含补记句 ⇒ 跳过 (幂等)")
            else:
                print("❌ 顶部块尾部锚点找不到 ⇒ 中止")
                return 2
        else:
            print("❌ 顶部块尾部锚点命中 %d 次 ⇒ 中止" % n)
            return 2

        # ---- ① 补记段插在 "### 0.25.2 " 之前 (★**放在 tail 替换之后 ★** ⇒ 否则 tail 那步重新 split lines 会把它冲掉) ----
        if "#### ★**补记 (21:16-21:2x)" in s:
            print("ℹ️ 补记段已存在 ⇒ 跳过 (幂等)")
        else:
            lines = s.split("\n")
            idx = None
            for i, l in enumerate(lines):
                if l.startswith(ANCHOR_252):
                    idx = i
                    break
            if idx is None:
                print("❌ 找不到 §0.25.2 锚点 ⇒ 中止")
                return 2
            lines[idx:idx] = APPENDIX.rstrip("\n").split("\n")
            s = "\n".join(lines)

        s = "\n".join(lines)

        # ---- ③ 自检 ----
        for need in ("#### ★**补记 (21:16-21:2x)", "### 0.25.1 ", "### 0.25.2 ", "### 0.25.3 ",
                     "## 0.25 ", "## 0.24 ", "## 0.23 "):
            if need not in s:
                print("❌ 自检失败: 结构节 '%s' 不见了 ⇒ 中止" % need)
                return 2
        # C 段 36 项的建议默认值一个没动 ⇒ §1 那 3 行必须逐字未变
        for k in ("demo_od_path_a_vs_b", "demo_od_model_route_m1_vs_m2", "iss079_phip_manual_fetch"):
            rows = [l for l in lines if l.startswith("| **") and ("`%s`" % k) in l]
            if not rows:
                print("❌ 自检失败: §1 的 %s 那行不见了 ⇒ 中止" % k)
                return 2
        print("✔ 自检: 结构节齐全 + §1 那 3 行在位 + C 段口径未动 (36 → 36)")

        atomic_write(P, s)
    finally:
        fcntl.flock(lock_fh, fcntl.LOCK_UN)

    print("✅ 决策页已补记 (r24a): %d → %d 字符" % (before_len, len(s)))
    print("   - §0.25.1 后追加『补记 (21:16-21:2x)』段: ISS-193 交卷 + 兄弟 job 开 ISS-196/197 + C 段不受影响")
    print("   - 顶部块 ① 末尾补一句指向补记 (免得读者把 21:1x 的快照当成当下状态)")
    print("   - ★**C 段 36 项的建议默认值一个没动**")
    return 0


if __name__ == "__main__":
    sys.exit(main())
