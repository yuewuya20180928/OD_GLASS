#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-395 · 「钉板闸⑩ 并发假红」机器闸
=================================================================================================
派活: state/dispatch_briefs/ISS-395_hw_gate10_concurrency_safety.md (项目总工 2026-11-24 16:3x)

★**它守的是什么**: ★**「并发 ⇒ 假红 ⇒ 板那一趟不许开工」这条结论必须是【假的】才安全** ★

  ★**病根 (★ISS-395 定位·★main 本机实读源码★)**: `HW/check_preflight_regen_idempotent.py`
    (★"钉板闸⑩ · 板侧项全集重跑幂等闸"★) 的沙盒落点是【固定路径】 (`tmp/iss349/regen_gate`)
    ⇒ `shutil.rmtree(dst)` 在【两个 gate_check 并发跑】时抛 `OSError: [Errno 39] Directory not empty`
    ⇒ 闸链判红 ⇒ ★**「板 md5 / 落表链 / 结构真值 漂移 ⇒ 板那一趟不许开工」这条结论是假的** ★

  ★**为什么必撞不是可能撞 (★main 本机实读★)**: `state/daily_check.py` L317 逐字 `jrun("gate_check.py")`
    ⇒ 巡检链内部自己会再跑一遍 gate_check ⇒ 「每日巡检」与「继续执行后继计划」两个 cron job
    同分钟各跑一次 ⇒ ★**必撞** ★

  ★**本闸的立场 (★关键★)**: ★**不许把「红」改成「绿」来掩盖问题** ★
    ⇒ ★**K5 专门盯住「真漂移仍然判红」** ★ ⇒ ★**并发假红消失了, 真漂移必须照样红** ★

★**五条判据 (★每条都要能当场判红, 不许是装饰★)**:
  K0 落点唯一化在位   : `HW/check_preflight_regen_idempotent.py` 的沙盒落点推导里【必须含每次运行唯一 token】
                        ⇒ ★并且【不许】留着裸 `shutil.rmtree(dst)`★ ⇒ 有人偷偷改回写死路径 ⇒ 当场红
  K1 并发两跑双绿     : ★**两个进程并发跑那道闸 ⇒ 两个都必须 rc=0** ★ ⇒ 任一 rc≠0 / 输出含
                        `Traceback` / `Errno 39` / `OSError` ⇒ 判红 (★这就是那条假红本身★)
  K2 落点真的唯一     : ★**从两个并发进程的真实输出里解析出的落点必须不同** ★ ⇒ 相同 ⇒ 判红
                        (★证明「唯一化」不是写在注释里的, 是真在跑★)
  K3 删除不抛未捕获异常: ★**同一个路径被第二个进程 rmtree 时不许抛未捕获异常** ★
                        ⇒ 在【真并发写压力】下调用闸里那个删除函数 ⇒ 抛异常 ⇒ 判红
  K4 板三项零扰动     : 跑前跑后 板 md5 / mtime / size 逐项未变 ⇒ 且等于基线
                        (★板 `611b869e13518c3c023fb178f91a0075` · `2026-11-06 07:07:17.362193413` · `4940213`★)
  K5 真漂移仍然判红   : ★**沙盒里改坏一个真源 ⇒ 那道闸必须 rc=1 (★红★)** ★
                        ⇒ ★**rc=0 ⇒ 判红 (★说明有人把「红」改成「绿」了★)** ★

★**方向纪律 (★本项目铁律★)**: ★**只许【加严】不许【放宽】** ★
  ⇒ ① `HW/check_preflight_regen_idempotent.py` 的判据 C1~C4 / `REQUIRED_ITEMS` 一个字未改
    (★本单只改【落点唯一化】与【rmtree 防御】两类不改变判据的改动★)
  ⇒ ② `HW/check_onepass_preflight_coverage.py` 一个字未改 (★钉板闸⑥·只读★)
  ⇒ ③ `state/gate_check.py` 一个字未改 (★挂载是 main 的地界·挂载行写进交卷页 §B4★)
  ⇒ ④ 本闸【只读盘 + 只写项目盘沙盒】⇒ ★**零写板 · 零落表 · 零改既有闸** ★

退出码: 0 = 全过 · 1 = 有不通过项 (★闸红★) · 2 = 用法错 · 3 = ★闸崩 (★与「闸红」严格区分★)
用法:
  python3 -B HW/check_gate10_concurrency_safety.py             # 主模式
  python3 -B HW/check_gate10_concurrency_safety.py --selftest   # 反向用例 (S1~S5 + 正例)
★**沙盒 env 覆盖★:
  GATE10_SANDBOX   本闸沙盒基目录 (★默认 = PROJ/tmp/iss395_sbx/g10·★绝不落 /tmp★★)
  PREFLIGHT_PROJ  既有闸的项目根 (★默认 = 本文件的上一级目录★)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.environ.get("PREFLIGHT_PROJ") or os.path.join(HERE, ".."))
TARGET_GATE = os.path.join(PROJ, "HW", "check_preflight_regen_idempotent.py")
BOARD = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
SANDBOX = os.environ.get("GATE10_SANDBOX") or os.path.join(PROJ, "tmp", "iss395_sbx", "g10")

# ★★板三项基线 (★任务书逐字给的值·★全程不许变★) ★
BOARD_BASELINE = {
    "md5": "611b869e13518c3c023fb178f91a0075",
    "mtime": "2026-11-06 07:07:17.362193413",
    "size": 4940213,
}

TRACEBACK_MARKERS = ("Traceback (most recent call last)", "Errno 39", "OSError", "Errno 2")


# ==============================================================================
# 基础读数
# ==============================================================================
def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fingerprint(path):
    """★(md5, mtime, size) 三元组 (★mtime 用 ns 以免秒级精度糊弄★) ★"""
    st = os.stat(path)
    return {"md5": md5(path), "mtime_ns": st.st_mtime_ns, "size": st.st_size}


def _mtime_str_to_ns(s):
    """★`2026-11-06 07:07:17.362193413` (★9 位纳秒★) ⇒ epoch ns (★本地时区★) ★"""
    import datetime
    date_part, frac = s.split(".")
    base = datetime.datetime.strptime(date_part, "%Y-%m-%d %H:%M:%S")
    return int(base.timestamp()) * 1000000000 + int(frac.ljust(9, "0")[:9])


def baseline_ok(fp):
    """★板指纹是否等于基线 (★md5 / size 逐字比; mtime 按基线字符串解析后比 ns★) ★"""
    problems = []
    if fp["md5"] != BOARD_BASELINE["md5"]:
        problems.append("md5 = %s (基线 %s)" % (fp["md5"], BOARD_BASELINE["md5"]))
    if fp["size"] != BOARD_BASELINE["size"]:
        problems.append("size = %s (基线 %s)" % (fp["size"], BOARD_BASELINE["size"]))
    want_ns = _mtime_str_to_ns(BOARD_BASELINE["mtime"])
    if abs(fp["mtime_ns"] - want_ns) > 1000:
        problems.append("mtime = %s (基线 %s)" % (fp["mtime_ns"], want_ns))
    return (not problems), problems


def judge_landing_uniqueness(paths):
    """★K2 判据本体: ★**落点必须每次运行唯一** ★ ⇒ 相等 ⇒ 判红 ★

    ★**纯函数·单测友好 (★`--selftest` 的 S1 直接喂它★) ★**
    """
    if not paths:
        return False, ["落点一个都没解析到 ⇒ fail-closed 判红"]
    if len(set(paths)) != len(paths):
        dup = sorted({p for p in paths if paths.count(p) > 1})
        return False, ["❌ 落点不唯一 (★并发两跑撞同一目录 ⇒ 假红会回来★): 重复项 = %s" % dup]
    return True, ["落点 %d 个全部互不相同: %s" % (len(paths), " · ".join(paths))]


def compare_fingerprint(before, after):
    """★K4 判据本体: ★**板三项零扰动** ★ ⇒ 任一变化 ⇒ 判红 ★"""
    problems = []
    if before["md5"] != after["md5"]:
        problems.append("md5 变了: %s → %s" % (before["md5"], after["md5"]))
    if before["mtime_ns"] != after["mtime_ns"]:
        problems.append("mtime 变了: %s → %s" % (before["mtime_ns"], after["mtime_ns"]))
    if before["size"] != after["size"]:
        problems.append("size 变了: %s → %s" % (before["size"], after["size"]))
    if problems:
        return False, ["❌ 板三项有扰动: " + " · ".join(problems)]
    return True, ["板三项零扰动: md5=%s · mtime_ns=%s · size=%d"
                  % (after["md5"], after["mtime_ns"], after["size"])]


# ==============================================================================
# 跑既有闸 (★只读它·不改它★)
# ==============================================================================
def run_target_gate(sandbox_base, extra_env=None, timeout=900):
    """★跑一次 `HW/check_preflight_regen_idempotent.py` ⇒ (rc, stdout) ★"""
    env = dict(os.environ)
    env["PREFLIGHT_SANDBOX"] = sandbox_base
    env.setdefault("TMPDIR", os.path.join(SANDBOX, "tmp"))
    if extra_env:
        env.update(extra_env)
    p = subprocess.run([sys.executable, "-B", TARGET_GATE], cwd=PROJ, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace")


def parse_landing(out):
    """★从既有闸的输出里解析真实落点 (★它自己打印 `SANDBOX   = <path>`★) ★"""
    for line in out.splitlines():
        if line.strip().startswith("SANDBOX"):
            return line.split("=", 1)[1].strip()
    return None


def load_target_module():
    """★把既有闸当模块加载 (★只为调它那个并发安全删除函数·不改它一个字★) ★"""
    spec = importlib.util.spec_from_file_location("iss395_target_gate", TARGET_GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ==============================================================================
# 五条判据
# ==============================================================================
def check_K0():
    """★K0 · 落点唯一化在位 (★静态读既有闸源码★) ⇒ 有人改回写死路径 ⇒ 当场红 ★"""
    if not os.path.exists(TARGET_GATE):
        return False, ["❌ 找不到既有闸 %s ⇒ fail-closed 判红" % TARGET_GATE]
    with open(TARGET_GATE, encoding="utf-8", errors="replace") as f:
        src = f.read()
    lines = []
    ok = True
    has_unique = ("run_%d_%d" in src) and ("os.getpid()" in src)
    if not has_unique:
        ok = False
        lines.append("❌ 既有闸的沙盒落点推导里没有「每次运行唯一 token」"
                     " (★要找 `run_%d_%d` + `os.getpid()`★) ⇒ 落点又变回写死路径了")
    bare = [i + 1 for i, l in enumerate(src.splitlines())
            if l.strip() == "shutil.rmtree(dst)"]
    if bare:
        ok = False
        lines.append("❌ 既有闸里还留着裸 `shutil.rmtree(dst)` (行 %s) ⇒ 并发假红会回来"
                     % bare)
    for marker, must in (("def check_C1(", True), ("def check_C2(", True),
                          ("def check_C3(", True), ("def check_C4(", True),
                          ("REQUIRED_ITEMS = ", True)):
        if (marker in src) != must:
            ok = False
            lines.append("❌ 既有闸的判据结构被动了 (缺 `%s`)" % marker)
    lines.append("落点唯一化: %s · 裸 rmtree: %s · C1~C4 + REQUIRED_ITEMS 结构: %s"
                 % ("✔ 在位" if has_unique else "❌ 缺",
                    "✔ 无" if not bare else "❌ 有",
                    "✔ 在位"))
    return ok, lines


def check_K1():
    """★K1 · 并发两跑 ⇒ 两个进程都必须 rc=0 (★不许有一个假红★) ★

    ★**两个进程用【同一个】沙盒基目录 (★这才是真的竞态现场★)** ——
      ★**旧版落点写死 ⇒ 两个进程共用同一个 dst ⇒ 第二个的 rmtree 撞上第一个的写 ⇒ Errno 39★ ★
      ★**新版落点每次运行唯一 ⇒ 同一个基目录下开两个子目录 ⇒ 互不踩 ⇒ 双绿** ★
    """
    base = os.path.join(SANDBOX, "k1")
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base, exist_ok=True)
    procs = []
    for i in (1, 2):
        env = dict(os.environ)
        env["PREFLIGHT_SANDBOX"] = base          # ★同一个基目录·★真竞态现场★
        env.setdefault("TMPDIR", os.path.join(base, "tmp"))
        procs.append((i, subprocess.Popen([sys.executable, "-B", TARGET_GATE],
                                          cwd=PROJ, env=env,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT)))
    results = []
    for i, p in procs:
        out = (p.communicate(timeout=900)[0] or b"").decode("utf-8", "replace")
        results.append((i, p.returncode, out))
    ok = True
    lines = []
    landings = []
    for i, rc, out in results:
        land = parse_landing(out)
        landings.append(land)
        hit = [m for m in TRACEBACK_MARKERS if m in out]
        if rc != 0:
            ok = False
            lines.append("❌ 并发跑 #%d rc=%d (★必须 0·不许有假红★)" % (i, rc))
        if hit:
            ok = False
            lines.append("❌ 并发跑 #%d 输出含异常标记 %s (★这就是那条假红的形状★)"
                         % (i, hit))
        tail = " / ".join(l.strip() for l in out.strip().splitlines()[-2:] if l.strip())
        lines.append("并发跑 #%d: rc=%d · 落点=%s · 末行: %s" % (i, rc, land, tail[:160]))
    lines.append("★两进程 rc: %s ⇒ %s"
                 % ([rc for _, rc, _ in results],
                    "✔ 双绿 (★无假红★)" if ok else "❌ 有假红"))
    return ok, lines, landings


def check_K2(landings):
    """★K2 · 落点真的唯一 (★从两个并发进程的真实输出里解析★) ★"""
    paths = [p for p in landings if p]
    if len(paths) < 2:
        return False, ["❌ 只解析到 %d 个落点 ⇒ 无法证明唯一性 ⇒ fail-closed 判红" % len(paths)]
    ok, lines = judge_landing_uniqueness(paths)
    outside = [p for p in paths if not os.path.abspath(p).startswith(os.path.abspath(SANDBOX))]
    if outside:
        ok = False
        lines.append("❌ 落点跑到沙盒基目录外面去了: %s (★不许落系统 /tmp★)" % outside)
    else:
        lines.append("落点全部在沙盒基目录 %s 之下: ✔" % SANDBOX)
    return ok, lines


def check_K3():
    """★K3 · 同一路径被第二个进程 rmtree 时不许抛未捕获异常 ★"""
    try:
        mod = load_target_module()
    except Exception as e:  # noqa: BLE001
        return False, ["❌ ★闸崩★ 加载既有闸失败: %s" % e]
    if not hasattr(mod, "safe_rmtree"):
        return False, ["❌ 既有闸里没有 `safe_rmtree` (★并发安全的删除函数★) ⇒ 判红"]
    victim = os.path.join(SANDBOX, "k3_victim")
    shutil.rmtree(victim, ignore_errors=True)
    os.makedirs(victim, exist_ok=True)
    # ★先在 victim 里塞够多的文件 ⇒ rmtree 的遍历窗口拉长 ⇒ 并发写更容易撞上 ★
    for i in range(2000):
        with open(os.path.join(victim, "f%04d" % i), "w") as f:
            f.write("x")
    stop = threading.Event()

    def writer():
        n = 0
        while not stop.is_set():
            try:
                with open(os.path.join(victim, "w%06d" % n), "w") as f:
                    f.write("y")
                n += 1
            except OSError:
                pass
            time.sleep(0.001)

    th = threading.Thread(target=writer, daemon=True)
    th.start()
    raised = None
    try:
        mod.safe_rmtree(victim)
    except BaseException as e:  # noqa: BLE001
        raised = e
    finally:
        stop.set()
        th.join(timeout=5)
    # ★确定性复核: 朴素 `os.rmdir` 对非空目录必抛 Errno 39 ⇒ 这就是那条假红的机理 ★
    errno39 = None
    d39 = os.path.join(SANDBOX, "k3_errno39")
    shutil.rmtree(d39, ignore_errors=True)
    os.makedirs(d39, exist_ok=True)
    with open(os.path.join(d39, "x"), "w") as f:
        f.write("x")
    try:
        os.rmdir(d39)
    except OSError as e:
        errno39 = e.errno
    shutil.rmtree(d39, ignore_errors=True)
    ok = True
    lines = []
    if raised is not None:
        ok = False
        lines.append("❌ 闸里的删除函数在并发写压力下抛了未捕获异常: %r" % (raised,))
    else:
        lines.append("并发写压力下调用闸里的删除函数: 无未捕获异常 ✔")
    if errno39 == 39:
        lines.append("机理复核: 朴素删除对非空目录必抛 Errno 39 (★这就是假红的成因★) ✔")
    else:
        lines.append("机理复核: 朴素删除的 errno = %s (★不是 39·记录在案★)" % errno39)
    # ★确定性复核: 让删除必然抛 OSError (父目录不可写) ⇒ 闸里的删除函数必须吞掉它 ★
    perm_ok, perm_note = _probe_permission_error(mod)
    if not perm_ok:
        ok = False
        lines.append("❌ " + perm_note)
    else:
        lines.append(perm_note)
    return ok, lines


def _probe_permission_error(mod):
    """★确定性造一个「删除必抛 OSError」的条件 ⇒ 闸里的删除函数必须不抛 ★"""
    if os.geteuid() == 0:
        return True, "确定性复核 (权限错误路径): ★本机是 root ⇒ 该子项跳过 (★[0数据]★)"
    d = os.path.join(SANDBOX, "k3_perm")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "x"), "w") as f:
        f.write("x")
    mode = os.stat(d).st_mode
    try:
        os.chmod(d, stat.S_IRUSR | stat.S_IXUSR)
        try:
            mod.safe_rmtree(d)
        except BaseException as e:  # noqa: BLE001
            return False, "确定性复核 (权限错误路径): ❌ 删除函数把 OSError 抛出来了: %r" % (e,)
        return True, ("确定性复核 (权限错误路径): 删除函数把 OSError 吞掉了 ✔ (★不抛未捕获异常★)")
    finally:
        try:
            os.chmod(d, mode)
        except OSError:
            pass
        shutil.rmtree(d, ignore_errors=True)


def check_K4(before):
    """★K4 · 板三项零扰动 (★跑前跑后 + 对基线★) ★"""
    ok1, lines1 = compare_fingerprint(before, fingerprint(BOARD))
    ok2, lines2 = baseline_ok(fingerprint(BOARD))
    lines = lines1 + lines2
    return (ok1 and ok2), lines


def check_K5():
    """★K5 · 真漂移仍然判红 (★沙盒里改坏一个真源 ⇒ 那道闸必须 rc=1★) ★"""
    base = os.path.join(SANDBOX, "k5")
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base, exist_ok=True)
    real_page = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
    bad_page = os.path.join(base, "BOARD_ONEPASS_PREFLIGHT_BROKEN.md")
    with open(real_page, encoding="utf-8") as f:
        txt = f.read()
    broken = txt.replace("pitch 0.50", "pitch 9.99")
    if broken == txt:
        broken = txt.replace('"B33_PIN_LAND_1P27"', '"B33_PIN_LAND_1P27" ', 1)
    with open(bad_page, "w", encoding="utf-8") as f:
        f.write(broken)
    rc, out = run_target_gate(os.path.join(base, "sb"),
                              extra_env={"PREFLIGHT_CHECKLIST": bad_page})
    ok = True
    lines = []
    if rc != 1:
        ok = False
        lines.append("❌ 沙盒里改坏一个真源后, 那道闸 rc=%d (★必须 rc=1 = 判红★) ⇒ "
                     "★**有人把「红」改成「绿」了** ★" % rc)
    else:
        lines.append("沙盒里改坏一个真源 (清单页 JSON 的 pitch 改成假值) ⇒ 既有闸 rc=1 (★真漂移仍然判红✔★)")
    tail = " / ".join(l.strip() for l in out.strip().splitlines()[-6:] if l.strip())
    lines.append("既有闸输出末尾: %s" % tail[:400])
    return ok, lines


# ==============================================================================
# 主流程
# ==============================================================================
def banner():
    print("=" * 98)
    print("  ISS-395 · 「钉板闸⑩ 并发假红」机器闸 (★K0 唯一化在位 · K1 并发双绿 · K2 落点唯一 · "
          "K3 删除不抛异常 · K4 板三项零扰动 · K5 真漂移仍判红★)")
    print("=" * 98)


def run_all():
    res = []
    k0, l0 = check_K0()
    res.append(("K0 落点唯一化在位 (★静态读既有闸源码★)", k0, l0))

    before = fingerprint(BOARD)
    k1, l1, landings = check_K1()
    res.append(("K1 并发两跑 ⇒ 两个进程都 rc=0 (★不许有假红★)", k1, l1))

    k2, l2 = check_K2(landings)
    res.append(("K2 沙盒落点每次运行唯一 (★从真实输出解析★)", k2, l2))

    k3, l3 = check_K3()
    res.append(("K3 同一路径被第二个进程 rmtree ⇒ 不许抛未捕获异常", k3, l3))

    k4, l4 = check_K4(before)
    res.append(("K4 板三项零扰动 (★md5 / mtime / size 逐项未变 + 对基线★)", k4, l4))

    k5, l5 = check_K5()
    res.append(("K5 真漂移仍然判红 (★不许把「红」改成「绿」★)", k5, l5))
    ok = all(c for _, c, _ in res)
    return ok, res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="★反向用例 (S1~S5 + 正例)★")
    args = ap.parse_args(argv)
    banner()
    print("  PROJ        = %s" % PROJ)
    print("  TARGET_GATE = %s" % TARGET_GATE)
    print("  SANDBOX     = %s" % SANDBOX)
    print("  BOARD       = %s" % BOARD)
    print("-" * 98)
    if args.selftest:
        return selftest()
    if not os.path.exists(TARGET_GATE):
        print("★闸崩: 找不到既有闸 %s" % TARGET_GATE)
        return 3
    if not os.path.exists(BOARD):
        print("★闸崩: 找不到板 %s" % BOARD)
        return 3
    os.makedirs(SANDBOX, exist_ok=True)
    try:
        ok, res = run_all()
    except Exception as e:  # noqa: BLE001
        import traceback
        print("★闸崩: %s" % e)
        print(traceback.format_exc())
        return 3
    for name, c, lines in res:
        print("  %s  %s" % ("OK  " if c else "FAIL", name))
        for l in lines:
            print("    %s" % l)
    print("-" * 98)
    if ok:
        print("  ✅ rc=0: ★★并发两跑双绿 · 落点每次运行唯一 · 删除不抛未捕获异常 · "
              "板三项零扰动 · 真漂移仍然判红 ★★")
        return 0
    print("  ❌ rc=1: ★**闸红 (★上面点名的那几条就是不许过的那几条★)** ★")
    return 1


# ==============================================================================
# ★★反向用例 (★端到端·不许只测纯函数★) ★★
# ==============================================================================
def selftest():
    cases = []

    # ★S1 · 落点唯一性判据本体: 喂两个相同落点 ⇒ 必须判红; 喂两个不同落点 ⇒ 必须判绿 ★
    ok1, _ = judge_landing_uniqueness(["/x/run_1", "/x/run_1"])
    ok1b, _ = judge_landing_uniqueness(["/x/run_1", "/x/run_2"])
    cases.append(("S1 · 落点唯一性判据: 两个相同落点必须判红 · 两个不同落点必须判绿",
                  (not ok1) and ok1b,
                  "★相同落点判红=%s · 不同落点判绿=%s★" % (not ok1, ok1b)))

    # ★S2 · 朴素删除对非空目录必抛 Errno 39 (★假红的机理·确定性★) ⇒ 闸里的删除函数必须不抛 ★
    d = os.path.join(SANDBOX, "s2_errno39")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "x"), "w") as f:
        f.write("x")
    errno39 = None
    try:
        os.rmdir(d)
    except OSError as e:
        errno39 = e.errno
    shutil.rmtree(d, ignore_errors=True)
    try:
        mod = load_target_module()
        has_safe = hasattr(mod, "safe_rmtree")
        raised = None
        try:
            mod.safe_rmtree(os.path.join(SANDBOX, "s2_missing_dir"))
        except BaseException as e:  # noqa: BLE001
            raised = e
    except Exception as e:  # noqa: BLE001
        has_safe = False
        raised = e
    cases.append(("S2 · 朴素删除必抛 Errno 39 (★假红机理★) · 闸里的删除函数不许抛未捕获异常",
                  (errno39 == 39) and has_safe and (raised is None),
                  "★朴素 errno=%s (★要 39★) · 闸里有并发安全删除函数=%s · 它抛异常=%s★"
                  % (errno39, has_safe, raised)))

    # ★S3 · 真漂移仍然判红 (★K5 的反向: 改坏真源 ⇒ 闸必须 rc=1★) ★
    k5ok, k5lines = check_K5()
    cases.append(("S3 · 沙盒里改坏一个真源 ⇒ 既有闸必须 rc=1 (★真漂移仍判红·不许改成绿★)",
                  k5ok, " / ".join(k5lines)[:400]))

    # ★S4 · 板指纹比对器: 板被改了必须判红 (★只喂数字·绝不动真板★) ★
    fake_before = {"md5": BOARD_BASELINE["md5"], "mtime_ns": 1, "size": BOARD_BASELINE["size"]}
    fake_after = {"md5": "0" * 32, "mtime_ns": 2, "size": BOARD_BASELINE["size"]}
    ok4, l4 = compare_fingerprint(fake_before, fake_after)
    cases.append(("S4 · 板指纹比对器: md5 变了必须判红 (★只喂数字·真板零触碰★)",
                  (not ok4), " / ".join(l4)[:200]))

    # ★S5 · 正例: 现状必须是绿的 (★闸不许永远红★) ★
    ok_all, res = run_all()
    fails = [name for name, c, _ in res if not c]
    cases.append(("S5 · 正例: 现状全绿 (★K0~K5 六条全过·闸不是永远红的★)",
                  ok_all, "★不过的判据: %s★" % (fails or "无")))

    print("-" * 98)
    print("  ★反向用例 (★端到端·跑真闸★):")
    allok = True
    for name, ok, note in cases:
        allok = allok and ok
        print("  %s  %s" % ("PASS" if ok else "FAIL", name))
        for l in str(note).split("\n"):
            print("      %s" % l)
    print("-" * 98)
    if allok:
        print("  ALL TESTS PASS")
        return 0
    print("  ★自测不过 (★不许进交卷★)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
