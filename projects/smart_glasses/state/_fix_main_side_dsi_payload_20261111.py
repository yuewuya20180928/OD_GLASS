#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main 侧收尾: DSI payload 8× 口径差的最后两处 (2026-11-11 08:4x, 项目总工 main)

★**为什么是 main 的活**: ISS-186 (owner=hw-lead) 的验收范围是 ①②③④⑥ 五处 (全在 hw-lead 的域),
  ★**owner 主动如实报出两处超出范围但同源残留, 交回 main**:
    ① `state/_demo_hw_scheme_landing.py:24/40/70` —— ★★**风险最高的一处**:
       它是**落账器** ⇒ ★**重跑它 = 把 373 Mbps 灌回 PROJECT_TRACKER.md** ⇒
       ★**⇒ 前面 ISS-186 做的 5 处订正会被一次重跑全部抹掉** ⇒ ★**必须改脚本本体, 不是重跑**。
    ② `config/agents/main/MEMORY.md:1979` (= 真值源 `~/MEMORY.md` 同一处) —— main 自己的记忆文件。

★**★遵循"修在产生点, 不许在产物上擦" (MEMORY.md 铁律)**:
  ⇒ ★**产生点 = 落账器脚本 + 记忆文件** ⇒ ★**这两处改掉**;
  ⇒ ★**产物 = PROJECT_TRACKER.md §(1.60) 与 §(1.6x) 那两行 373** ⇒ ★**同步改** (否则 tracker
     与脚本继续互相矛盾 ⇒ 下次谁读了 tracker 拿到的还是错数)。

★**★§0 锁死表一律不碰**: tracker §0 = 第 28~91 行 ⇒ ★**第 75 行 (§0 变量 44) 里那个 373Mbps
  在锁死表内 ⇒ ★**本脚本明确跳过它** ⇒ ★**诚实报出: 全仓仍有 1 处 373 在 tracker §0 内, 是老板
  锁死的历史决策记录, 不由本轮改动** (★**§0 的规矩就是"锁死" ⇒ 里面写的就是当时决策的事实**,
  ★**改了它就等于篡改老板拍过板的东西** ⇒ ★**正确做法是让新数字在 §0 之外生效, 并在 ISS-188
  的验证里把这条列为"已知且故意保留"**)。

★**落账纪律**: ① flock + 原子写 (tmp → fsync → os.replace → fsync(dir))
  ② ★**只改 3 个文件的 6 处字面量** ⇒ 逐条 diff 实测
  ③ **不改 §0 锁死表** (脚本里显式断言: 改前先定位 §0 边界, 落在边界内的行直接跳过)
  ④ 不发邮件 / 不下采购单 / 不碰板子相关文件 / 不写任何子总工的分片
"""
from __future__ import annotations

import fcntl
import hashlib
import os
import re
import sys
import tempfile

WS = "/home/yuewuya/.openclaw/workspace"
PROJ = os.path.join(WS, "projects/smart_glasses")
LANDING = os.path.join(PROJ, "state/_demo_hw_scheme_landing.py")
TRACKER = os.path.join(PROJ, "PROJECT_TRACKER.md")
MEM_TRUTH = os.path.join(WS, "MEMORY.md")
LOCK = os.path.join(PROJ, "state/.main_side_fix.lock")

BASIS = ("payload = 宽×高×24×60 (RGB888 24bpp) ⇒ 1920×1080@60 = 2985.98 Mbps ≈ 2986 Mbps "
         "⇒ 与 `HW/e2e_budget_rk3572.py` §⑥ 同口径 (TX 物理下限 7.776ms = 2986/60/6400) "
         "⇒ ★**ISS-186 订正**")

# ---- tracker §0 边界 (锁死表) ----
S0_START = "## 0. 已锁死的变量"
S1_START = "## 1. 技术架构"


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".md")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(d, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def s0_line_range(lines: list[str]) -> tuple[int, int]:
    a = next(i for i, l in enumerate(lines) if l.startswith(S0_START))
    b = next(i for i, l in enumerate(lines) if i > a and l.startswith(S1_START))
    return a, b


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        report: list[str] = []

        # ═══ 1. 落账器脚本 (风险最高: 重跑会把旧数灌回 tracker) ═══
        with open(LANDING, encoding="utf-8") as f:
            src = f.read()
        before = hashlib.md5(src.encode()).hexdigest()
        n1 = src.count("373Mbps")
        src2 = src.replace(
            "373Mbps 负载, demo 不需要 DSC",
            "2986Mbps 负载, demo 不需要 DSC")
        src2 = src2.replace(
            "373Mbps ⇒ 4-lane 绰绰有余, **demo 不需要 DSC**",
            "2986Mbps ⇒ 4-lane 绰绰有余, **demo 不需要 DSC**")
        src2 = src2.replace(
            "373Mbps ⇒ 不需 DSC",
            "2986Mbps ⇒ 不需 DSC")
        # 在脚本头部加一条口径钉死 (防重跑再灌旧数)
        if "★ISS-186 口径钉死" not in src2:
            anchor = "PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'"
            pin = (anchor + "\n"
                   "# ★★★**ISS-186 口径钉死 (2026-11-11, 项目总工 main)** ★★★\n"
                   "# ★**本脚本是【落账器】⇒ 重跑它 = 把它写的字串灌回 PROJECT_TRACKER.md**\n"
                   "# ⇒ ★**所以这里的每一个 payload 数字都必须是对的** ⇒ ★**原来写 373 Mbps (偏小 8.0×)\n"
                   "#   会把 ISS-186 订正过的 5 处全部重新灌回错数** ⇒ ★**已订正为 2986**\n"
                   "# ★**口径**: " + BASIS + "\n"
                   "# ★**不许重跑本脚本**: 它是 2026-11-02 的一次性落账器 (无幂等护栏) ⇒ 重跑会重复追加\n")
            src2 = src2.replace(anchor, pin, 1)
        if "373Mbps" in src2:
            print("❌ 落账器脚本里还有 373Mbps 残留 ⇒ 中止")
            return 1
        atomic_write(LANDING, src2)
        report.append(f"落账器脚本: 改 {n1} 处 373Mbps → 2986Mbps + 加 1 条口径钉死 (md5 {before[:8]} → "
                      f"{hashlib.md5(src2.encode()).hexdigest()[:8]})")

        # ═══ 2. tracker: 只改 §0 之外的两处 ═══
        with open(TRACKER, encoding="utf-8") as f:
            tlines = f.read().split("\n")
        a, b = s0_line_range(tlines)
        changed_t = []
        for i, line in enumerate(tlines):
            if "373Mbps" not in line:
                continue
            if a <= i < b:
                changed_t.append((i + 1, "★§0 锁死表内 ⇒ 跳过 (老板拍过板的历史决策记录, 不由本轮改)★"))
                continue
            tlines[i] = line.replace("373Mbps", "2986Mbps")
            changed_t.append((i + 1, "已改 373Mbps → 2986Mbps (依据: " + BASIS + ")"))
        # ★★踩坑记录 (2026-11-11 08:4x 实测): 上面读回的是**改动前**的内容 ⇒ ★**写回去等于没改**
        #   ⇒ ★**必须把改过的 tlines 拼回去写** (第一版就是这么写的 ⇒ tracker diff 为空)
        atomic_write(TRACKER, "\n".join(tlines))
        for ln, msg in changed_t:
            report.append(f"tracker 第 {ln} 行: {msg}")

        # ═══ 3. MEMORY.md (真值源; 副本由 publish_github.sh 自动同步) ═══
        with open(MEM_TRUTH, encoding="utf-8") as f:
            mem = f.read()
        n_m = mem.count("373 Mbps")
        # ★★踩坑记录 (2026-11-11 08:4x 实测): ★**替换文本里不能再出现 "373 Mbps"** ——
        #   第一版我在依据注里写了「原写 373 Mbps」⇒ ★**新值自己带着旧串** ⇒
        #   守卫 `if "373 Mbps" in mem2` 判成"没清干净" ⇒ ★**脚本自己把自己卡死** (已中止, 没写坏)
        #   ⇒ ★**正确做法: 依据注里写「原写的 373」(不带 Mbps) 或用零宽分隔**
        mem2 = mem.replace(
            "②DSI 带宽要算 (1920×1080@60 RGB888 ≈ 373 Mbps payload)",
            "②DSI 带宽要算 (1920×1080@60 RGB888 ≈ **2986 Mbps** payload "
            "★**ISS-186 订正** (原写的 373 偏小 8.0× ⇒ 依据虚到 8 倍 ⇒ 拿它反推 TX 物理下限 "
            "会从 7.776ms 塌成 ~0.97ms)")
        if "373 Mbps" in mem2:
            print("❌ MEMORY.md 里还有 373 Mbps 残留 ⇒ 中止")
            return 1
        atomic_write(MEM_TRUTH, mem2)
        report.append(f"MEMORY.md (真值源): 改 {n_m} 处 '373 Mbps' → '2986 Mbps' (含口径依据注)")

        fcntl.flock(lf, fcntl.LOCK_UN)

    print("=== 落账报告 ===")
    for r in report:
        print("  ·", r)
    print()
    print("=== 全仓复核 (DSI payload 口径) ===")
    import subprocess
    out = subprocess.run(
        ["grep", "-rn", "373Mbps\\|373 Mbps\\|246 Mbps", PROJ, "--include=*.md", "--include=*.py",
         "--include=*.yaml", "--include=*.json"],
        capture_output=True, text=True).stdout
    hits = [l for l in out.splitlines() if l.strip()]
    for h in hits:
        print("  ", h[:170])
    print(f"  合计残留 {len(hits)} 处 (预期: 1 = tracker §0 锁死表内, 故意保留)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
