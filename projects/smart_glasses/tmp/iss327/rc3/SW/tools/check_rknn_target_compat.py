#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-250 第5轮 · rk3572 target 兼容性机器门禁 (★本机可跑 · 零外发 · 零板端依赖★)
================================================================================
为什么要有这个闸:
  ★ISS-155 (demo 头号卡点) 的核心事实是「rk3572 不是 rknn-toolkit2 的合法 target」★
  ★这条事实一旦只在交卷单正文里写一句, 下一个人随时可能把两条工具链搞混★
  ★⇒ 本闸把【两条工具链各自的合法 target 全集】+【两代产物的容器格式】+【互斥不变量】★
  ★   做成【可复跑的机器判据】, 任何人 30 秒内自己复现★

判据 (全部本机可跑):
  G1 toolkit2 侧版本 == 2.3.2
  G2 toolkit2 侧合法 target 集合 == 期望 11 个 (含 rk3576; 不含 rk3572 / rk3572b)
  G3 rknn3 侧版本 == 1.2.0
  G4 rknn3 侧合法 target 集合 == 期望 7 个 (含 rk3572; 不含 rk3576)
  G5 ★互斥不变量★: 两条工具链的合法 target 交集 == 空集
  G6 toolkit2 产物容器 magic == b'RKNN' 且内嵌元数据 target_platform == ["rk3576"]
  G7 rknn3 产物容器 magic == b'RKNX' 且伴生 .weight magic == b'RKNX-W' (两件套)
  G8 rknn3 产物 md5 锚点 == 97a34fff0b855b92681f26627dba5354 (3 次转换实测一致)
  G9 ★板端接受性 = 未验★ ⇒ 本闸【永远】打印 BOARD_ACCEPTANCE = NOT_VERIFIED [0数据], 不许绿

用法:
  python3 SW/tools/check_rknn_target_compat.py            # 跑全部门禁
  python3 SW/tools/check_rknn_target_compat.py --selftest # 反向自证 (改坏产物 ⇒ 必须 rc=1)
  python3 SW/tools/check_rknn_target_compat.py --json     # 机器可读输出
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

ENV_TOOLKIT2 = "/home/yuewuya/miniconda3/envs/rknn/bin/python"
ENV_RKNN3 = "/home/yuewuya/miniconda3/envs/rknn3/bin/python"

EXP_TOOLKIT2_SET = {"rv1103", "rv1103b", "rv1106", "rv1106b", "rv1126b",
                    "rk2118", "rk3562", "rk3566", "rk3568", "rk3576", "rk3588"}
EXP_RKNN3_SET = {"gongga2", "rk1820", "rk1828", "rk182x", "rk1860", "rk186x", "rk3572"}

CAND = ["rk3572", "rk3572b", "rk3576", "rk3588", "rk3562", "rk3566", "rk3568", "rk3568b",
        "rk2118", "rk2108", "rk3516", "rk3506", "rk1820", "rk1828", "rk182x", "rk1860",
        "rk186x", "gongga2", "rv1103", "rv1103b", "rv1103c", "rv1106", "rv1106b",
        "rv1109", "rv1126", "rv1126b", "rv1209", "rv1210", "rk1806", "rk1808",
        "rk3399", "rk3399pro", "rk3288"]

ART_TK2 = os.path.join(ROOT, "SW/artifacts/models/"
                             "yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn")
ART_RKNN3_DIR = "/var/tmp/iss263_rknn3/work/out"
# ★rknn3 产物: 优先用【落盘归档】(SW/artifacts/models/rk3572_rknn3/, 抗 /var/tmp 被清), 没有再回落 /var/tmp★
ART_RKNN3_STABLE = os.path.join(ROOT, "SW/artifacts/models/rk3572_rknn3/"
                                      "yolov5n-sim_heads_rk3572_int8_heads.rknn")
ART_RKNN3_VOLATILE = os.path.join(ART_RKNN3_DIR, "yolov5n_heads_int8_rk3572_run1.rknn")
ART_RKNN3 = ART_RKNN3_STABLE if os.path.exists(ART_RKNN3_STABLE) else ART_RKNN3_VOLATILE
ART_RKNN3_MD5 = "97a34fff0b855b92681f26627dba5354"


# ----------------------------------------------------------------------------- probe
def probe(py: str) -> dict:
    """在指定 conda env 的 python 下枚举 target_platform 合法性 (子进程隔离, 两个 rknn 包同名不能同进程)"""
    code = (
        "import json,os,sys\n"
        "from rknn.api.rknn import RKNN\n"
        "import rknn as _r\n"
        "v=os.path.join(_r.__path__[0],'VERSION')\n"
        "ver=open(v).read().strip() if os.path.exists(v) else '?'\n"
        "CAND=json.loads(sys.argv[1])\n"
        "ok=[];bad={}\n"
        "for t in CAND:\n"
        "    r=RKNN(verbose=False)\n"
        "    try:\n"
        "        ret=r.config(target_platform=t)\n"
        "        if ret==0: ok.append(t)\n"
        "        else: bad[t]='ret=%r'%(ret,)\n"
        "    except Exception as e:\n"
        "        bad[t]='%s'%type(e).__name__\n"
        "    finally:\n"
        "        try: r.release()\n"
        "        except Exception: pass\n"
        "print('@@JSON@@'+json.dumps({'version':ver,'accepted':ok,'rejected':bad}))\n"
    )
    p = subprocess.run([py, "-c", code, json.dumps(CAND)],
                       capture_output=True, text=True, timeout=600)
    for line in p.stdout.splitlines():
        if line.startswith("@@JSON@@"):
            return json.loads(line[len("@@JSON@@"):])
    return {"error": "probe_failed", "rc": p.returncode,
            "stderr": p.stderr[-400:], "stdout": p.stdout[-400:]}


# ----------------------------------------------------------------------------- helpers
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def magic_of(path: str, n: int = 8) -> bytes:
    with open(path, "rb") as f:
        return f.read(n)


def tk2_embedded_target(path: str):
    """toolkit2 产物内嵌 JSON 元数据里的 target_platform / version (读原文件, 不修改)"""
    try:
        with open(path, "rb") as f:
            blob = f.read()
    except OSError:
        return None, None
    tgt, ver = None, None
    key_t = b'"target_platform":'
    key_v = b'"version":'
    i = blob.find(key_t)
    if i >= 0:
        seg = blob[i:i + 80]
        a = seg.find(b"[")
        b = seg.find(b"]")
        if a >= 0 and b > a:
            try:
                tgt = json.loads(seg[a:b + 1].decode("utf-8", "replace"))
            except Exception:
                tgt = seg[a + 1:b].decode("utf-8", "replace").strip().strip('"')
    j = blob.find(key_v)
    if j >= 0:
        seg = blob[j:j + 60]
        m = re.search(rb'"version"\s*:\s*"([^"]+)"', seg)
        if m:
            ver = m.group(1).decode("utf-8", "replace")
    return tgt, ver


# ----------------------------------------------------------------------------- gate
class Gate:
    def __init__(self):
        self.rows = []

    def add(self, gid, ok, title, detail, level="FAIL"):
        self.rows.append({"id": gid, "ok": bool(ok), "title": title,
                          "detail": detail, "level": level})
        print("[%s] %-4s %s" % ("PASS" if ok else level, gid, title))
        if detail:
            print("        %s" % detail)

    def note(self, gid, title, detail):
        """既不是 PASS 也不是 FAIL —— 事实陈述 (★[0数据] 状态不许被算成绿★)"""
        self.rows.append({"id": gid, "ok": None, "title": title,
                          "detail": detail, "level": "NOTE"})
        print("[NOTE] %-4s %s" % (gid, title))
        if detail:
            print("        %s" % detail)


def run_gate(art_tk2=ART_TK2, art_rknn3=ART_RKNN3, quiet=False) -> int:
    g = Gate()
    if not quiet:
        print("=" * 78)
        print("ISS-250 · rk3572 target 兼容性机器门禁")
        print("root = %s" % ROOT)
        print("=" * 78)

    # G1/G2 —— toolkit2 侧
    t2 = probe(ENV_TOOLKIT2)
    if "error" in t2:
        g.add("G1", False, "toolkit2 侧探测失败", json.dumps(t2, ensure_ascii=False)[:300])
        t2set = set()
    else:
        g.add("G1", t2.get("version") == "2.3.2",
              "toolkit2 版本 == 2.3.2", "实测 = %s (env %s)" % (t2.get("version"), ENV_TOOLKIT2))
        t2set = set(t2.get("accepted", []))
        g.add("G2", t2set == EXP_TOOLKIT2_SET,
              "toolkit2 合法 target 集合 == 期望 11 个",
              "实测 %d 个: %s" % (len(t2set), ",".join(sorted(t2set))))
        g.note("G2b", "toolkit2 对 rk3572 的态度",
               "rk3572 ∈ 合法集 = %s ; rk3572b ∈ 合法集 = %s (★双否 ⇒ 无 b 变体后门★)"
               % ("rk3572" in t2set, "rk3572b" in t2set))

    # G3/G4 —— rknn3 侧
    t3 = probe(ENV_RKNN3)
    if "error" in t3:
        g.add("G3", False, "rknn3 侧探测失败", json.dumps(t3, ensure_ascii=False)[:300])
        t3set = set()
    else:
        g.add("G3", t3.get("version", "").endswith("1.2.0"),
              "rknn3-toolkit 版本 == 1.2.0", "实测 = %s (env %s)" % (t3.get("version"), ENV_RKNN3))
        t3set = set(t3.get("accepted", []))
        g.add("G4", t3set == EXP_RKNN3_SET,
              "rknn3 合法 target 集合 == 期望 7 个",
              "实测 %d 个: %s" % (len(t3set), ",".join(sorted(t3set))))
        g.note("G4b", "rknn3 对 rk3576 / rk3588 的态度",
               "rk3576 ∈ 合法集 = %s ; rk3588 ∈ 合法集 = %s (★与 toolkit2 正好相反★)"
               % ("rk3576" in t3set, "rk3588" in t3set))

    # G5 —— 互斥不变量
    inter = sorted(t2set & t3set)
    g.add("G5", len(inter) == 0,
          "★互斥不变量★: 两条工具链合法 target 交集 == 空集",
          "交集 = %s (★⇒ 一条工具链出不了另一个 target 的模型, 路线不可混用★)"
          % (",".join(inter) if inter else "∅"))

    # G6 —— toolkit2 产物容器
    if os.path.exists(art_tk2):
        mg = magic_of(art_tk2, 4)
        tgt, ver = tk2_embedded_target(art_tk2)
        g.add("G6", mg == b"RKNN" and tgt == ["rk3576"],
              "toolkit2 产物容器 == b'RKNN' 且内嵌 target_platform == [rk3576]",
              "文件 %s (%d B) magic=%r 内嵌 target_platform=%r version=%r"
              % (os.path.basename(art_tk2), os.path.getsize(art_tk2), mg, tgt, ver))
    else:
        g.note("G6", "toolkit2 产物不在盘 ⇒ 本条未验",
               "找不到 %s (★NOTE ≠ 绿★)" % art_tk2)

    # G7 —— rknn3 产物容器 (两件套)
    wgt = art_rknn3[:-5] + ".weight"
    if os.path.exists(art_rknn3):
        mg = magic_of(art_rknn3, 4)
        okw = os.path.exists(wgt)
        mgw = magic_of(wgt, 6) if okw else b""
        g.add("G7", mg == b"RKNX" and okw and mgw == b"RKNX-W",
              "rknn3 产物容器 == b'RKNX' 且伴生 .weight == b'RKNX-W' (★两件套缺一不可★)",
              "文件 %s (%d B) magic=%r ; .weight 存在=%s magic=%r"
              % (os.path.basename(art_rknn3), os.path.getsize(art_rknn3), mg, okw, mgw))
    else:
        g.note("G7", "rknn3 产物不在盘 ⇒ 本条未验",
               "找不到 %s (★/var/tmp 可能被清 ⇒ 重跑 ISS-263 转换脚本即可复现; NOTE ≠ 绿★)" % art_rknn3)

    # G8 —— 可复现锚点
    if os.path.exists(art_rknn3):
        m = md5_of(art_rknn3)
        g.add("G8", m == ART_RKNN3_MD5,
              "rknn3 产物 md5 锚点 == 3 次转换实测一致值",
              "实测 md5 = %s (期望 %s) ; 路径 = %s"
              % (m, ART_RKNN3_MD5, art_rknn3))
    else:
        g.note("G8", "rknn3 产物 md5 锚点", "产物不在盘 ⇒ 本条未验 (不算绿)")

    # G8b —— 落盘归档的 sha256 sidecar 自洽 (两件套都要在)
    side = os.path.join(os.path.dirname(art_rknn3),
                        "yolov5n-sim_heads_rk3572_int8_heads.sha256")
    if os.path.exists(side) and os.path.exists(art_rknn3):
        ok_side = True
        detail = []
        for line in open(side):
            line = line.strip()
            if not line:
                continue
            want, fn = line.split(None, 1)
            fn = fn.lstrip("*").strip()
            p = os.path.join(os.path.dirname(art_rknn3), fn)
            if not os.path.exists(p):
                ok_side = False
                detail.append("%s 缺" % fn)
                continue
            got = hashlib.sha256(open(p, "rb").read()).hexdigest()
            detail.append("%s %s" % (fn, "OK" if got == want else "MISMATCH"))
            ok_side = ok_side and (got == want)
        g.add("G8b", ok_side, "落盘归档 sha256 sidecar 自洽 (两件套都在)",
              " ; ".join(detail))
    else:
        g.note("G8b", "落盘归档 sha256 sidecar",
               "找不到 %s ⇒ 本条未验 (NOTE ≠ 绿)" % side)

    # G9 —— 板端接受性: 永远 NOT_VERIFIED
    g.note("G9", "★板端接受性 = 未验★",
           "BOARD_ACCEPTANCE = NOT_VERIFIED [0数据] (★板不可达; 本闸不许把板端结论算成绿★)")

    fails = [r for r in g.rows if r["ok"] is False]
    print("-" * 78)
    print("SUMMARY: %d 条判据, %d PASS, %d FAIL, %d NOTE (NOTE 不等于绿)"
          % (len(g.rows), sum(1 for r in g.rows if r["ok"] is True),
             len(fails), sum(1 for r in g.rows if r["ok"] is None)))
    print("BOARD_ACCEPTANCE = NOT_VERIFIED [0数据]")
    print("-" * 78)
    return 1 if fails else 0


# ----------------------------------------------------------------------------- selftest
def selftest() -> int:
    """反向自证: 沙盒里把产物 magic 改坏 ⇒ 判据必须变红 (rc=1) ⇒ 证明判据跟盘上真值走"""
    print("=" * 78)
    print("SELFTEST: 反向用例 —— 改坏产物 magic ⇒ 门禁必须 FAIL")
    print("=" * 78)
    tmp = tempfile.mkdtemp(prefix="iss250_gate_selftest_")
    try:
        bad_tk2 = os.path.join(tmp, "bad_rk3576.rknn")
        shutil.copyfile(ART_TK2, bad_tk2)
        with open(bad_tk2, "r+b") as f:
            f.seek(0)
            f.write(b"XXXX")
        print("[SELFTEST] 已造坏副本: %s (magic 改 RKNN -> XXXX)" % bad_tk2)
        rc = run_gate(art_tk2=bad_tk2, quiet=True)
        print("[SELFTEST] 改坏后 rc = %d (期望 1)" % rc)
        ok = (rc == 1)
        print("[SELFTEST] %s" % ("PASS 判据抓得住坏产物" if ok else "FAIL 判据抓不住坏产物"))
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    rc = run_gate()
    if args.json:
        print("@@JSON@@" + json.dumps({"rc": rc}))
    return rc


if __name__ == "__main__":
    sys.exit(main())
