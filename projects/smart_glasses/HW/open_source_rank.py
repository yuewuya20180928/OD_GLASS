#!/usr/bin/env python3
"""
open_source_rank.py —— 物料「开源数据可得性」评分器 (ISS-138 新判据落地)

判据来源: 老板 2026-11-02 09:23 —— "对比下 C/D 中那个 sensor 的开源数据更多,
优先使用开源数据更多的 sensor, 其他物料同理"

五个数据源 (全部可复算, 默认走本地快照, --refresh 联网刷新):
  D1  mainline Linux `drivers/media/i2c/` 里有无该 sensor 驱动   (上游内核)
  D2  Rockchip BSP kernel `drivers/media/i2c/` (develop-6.1) 里有无该 sensor 驱动 (本项目内核基线)
  D3  rkaiq `iqfiles/` (isp3x / isp32) 里有没有该 sensor 的 ISP tuning JSON (本项目 ISP 基线)
  D4  GitHub 公开仓库命中数 (社区移植实现/参考设计)
  D5  OpenIPC 公开 sensor 库有没有该条目 (公开规格 + 各平台驱动索引)

用法:
  python3 HW/open_source_rank.py                 # 离线, 读 HW/_os_snapshots/
  python3 HW/open_source_rank.py --refresh       # 联网刷新快照后再评
  python3 HW/open_source_rank.py --selftest      # 自检 (快照可解析 + 已知排序成立)
  python3 HW/open_source_rank.py --sensors OV04C10 AR0234CS OV02B10

评分 (满分 10): D1=2 (上游内核驱动) D2=3 (Rockchip BSP 驱动) D3=2 (现成 ISP tuning) D4=2 (社区参考实现) D5=1 (公开规格库)
  —— D1/D2/D3 是「能不能直接用」(权重最高), D4/D5 是「有没有参考」。

退出码: 0 = 正常; 1 = 快照缺失/不可解析 (--refresh 可修)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "_os_snapshots")
UA = {"User-Agent": "openclaw-os-rank/1.0 (ARS45 project)"}

# ---- 传感器名 → 各数据源的检索关键字 (小写, 去掉前缀) --------------------------
ALIASES = {
    "OV04C10": ["ov04c10"],
    "AR0234CS": ["ar0234"],          # AR0234CS / AR0234CT 同源, 驱动与库都用 ar0234
    "AR0234": ["ar0234"],
    "OV02B10": ["ov02b10"],
    "OV02C10": ["ov02c10"],
    "OG02B10": ["og02b10"],
    "OG02C10": ["og02c10"],
    "AR0521": ["ar0521"],
    "OV9281": ["ov9281"],
    "IMX415": ["imx415"],
    "IMX327": ["imx327"],
    "IMX296": ["imx296"],
    "SC1220IOT": ["sc1220"],
}

DEFAULT_SENSORS = ["OV04C10", "AR0234CS", "OV02B10", "OV02C10", "AR0521", "OV9281", "IMX415"]


def _get_json(url: str):
    """优先 curl (chunked 大响应稳), 失败回退 urllib。"""
    try:
        out = subprocess.run(
            ["curl", "-sSL", "--max-time", "90", "-H", "User-Agent: " + UA["User-Agent"], url],
            capture_output=True, timeout=120, check=True).stdout
        return json.loads(out.decode("utf-8", "replace"))
    except Exception:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode("utf-8", "replace"))


def _get_text(url: str) -> str:
    try:
        out = subprocess.run(
            ["curl", "-sSL", "--max-time", "90", "-H", "User-Agent: " + UA["User-Agent"], url],
            capture_output=True, timeout=120, check=True).stdout
        return out.decode("utf-8", "replace")
    except Exception:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.read().decode("utf-8", "replace")


# ---- 刷新 ---------------------------------------------------------------------
def refresh(github_repos=("ar0234", "ov04c10", "ov02b10", "ov02c10", "ar0521", "ov9281", "imx415")):
    os.makedirs(SNAP, exist_ok=True)

    # D1 mainline Linux drivers/media/i2c
    d1 = _get_json("https://api.github.com/repos/torvalds/linux/contents/drivers/media/i2c")
    json.dump(sorted(x["name"] for x in d1), open(os.path.join(SNAP, "linux_mainline_i2c.json"), "w"), indent=1)

    # D2 Rockchip BSP kernel develop-6.1 drivers/media/i2c
    d2 = _get_json(
        "https://api.github.com/repos/rockchip-linux/kernel/contents/drivers/media/i2c?ref=develop-6.1")
    json.dump(sorted(x["name"] for x in d2), open(os.path.join(SNAP, "rockchip_bsp_i2c.json"), "w"), indent=1)

    # D3 rkaiq iqfiles (isp3x / isp32 / isp32_lite)
    d3 = _get_json(
        "https://api.github.com/repos/TinkerBoard/rockchip-linux-external-camera_engine_rkaiq/git/trees/HEAD?recursive=1")
    iq = sorted({t["path"].split("/")[-1] for t in d3.get("tree", []) if t.get("path", "").startswith("rkaiq/iqfiles/")})
    json.dump(iq, open(os.path.join(SNAP, "rkaiq_iqfiles.json"), "w"), indent=1)

    # D4 GitHub 仓库命中数
    counts = {}
    for kw in github_repos:
        u = ("https://api.github.com/search/repositories?q=" + urllib.parse.quote(kw) + "&per_page=1")
        try:
            counts[kw] = _get_json(u).get("total_count", 0)
        except Exception as e:  # rate limit / 网络
            counts[kw] = f"ERR {e}"
    json.dump(counts, open(os.path.join(SNAP, "github_repo_counts.json"), "w"), indent=1)

    # D5 OpenIPC 公开 sensor 库
    try:
        html = _get_text("https://openipc.org/cameras/sensors/")
        import re
        names = sorted(set(re.findall(r'href="/cameras/sensors/([a-z0-9\-]+)"', html)))
        json.dump(names, open(os.path.join(SNAP, "openipc_sensors.json"), "w"), indent=1)
    except Exception as e:
        print(f"[warn] openipc 刷新失败: {e}", file=sys.stderr)
    print("[refresh] 快照已写入", SNAP)


# ---- 读取快照 -----------------------------------------------------------------
def load_snap():
    need = {
        "mainline": "linux_mainline_i2c.json",
        "bsp": "rockchip_bsp_i2c.json",
        "iq": "rkaiq_iqfiles.json",
        "gh": "github_repo_counts.json",
        "opipc": "openipc_sensors.json",
    }
    s = {}
    for k, fn in need.items():
        p = os.path.join(SNAP, fn)
        if not os.path.exists(p):
            print(f"[err] 缺快照 {fn} ⇒ 先跑: python3 HW/open_source_rank.py --refresh", file=sys.stderr)
            sys.exit(1)
        s[k] = json.load(open(p))
    return s


def _has_driver(names, keys):
    for n in names:
        low = n.lower()
        if any(k in low for k in keys):
            return True, n
    return False, None


def _has_iq(names, keys):
    for n in names:
        low = n.lower()
        if low.endswith(".json") and any(k in low for k in keys):
            return True, n
    return False, None


def score_one(name, s):
    keys = ALIASES.get(name, [name.lower()])
    d1, f1 = _has_driver(s["mainline"], keys)
    d2, f2 = _has_driver(s["bsp"], keys)
    d3, f3 = _has_iq(s["iq"], keys)
    gh = 0
    for k in keys:
        v = s["gh"].get(k, 0)
        gh = max(gh, v) if isinstance(v, int) else gh
    d5 = any(k in s["opipc"] for k in keys)
    pts = (2 if d1 else 0) + (3 if d2 else 0) + (2 if d3 else 0) + \
          (2 if gh >= 5 else (1 if gh >= 1 else 0)) + (1 if d5 else 0)
    return {
        "name": name, "keys": keys,
        "d1_mainline": d1, "d1_file": f1,
        "d2_rk_bsp": d2, "d2_file": f2,
        "d3_iq_file": d3, "d3_file": f3,
        "d4_github_repos": gh,
        "d5_openipc": d5,
        "score": pts, "max": 10,
    }


def main():
    args = sys.argv[1:]
    if "--refresh" in args:
        refresh()
    if "--selftest" in args:
        s = load_snap()
        assert len(s["mainline"]) > 150, "mainline 快照异常"
        assert len(s["bsp"]) > 300, "BSP 快照异常"
        assert any("imx415" in f for f in s["iq"]), "iq 快照异常"
        a = score_one("AR0234CS", s)
        o = score_one("OV04C10", s)
        assert a["score"] > o["score"], f"已知排序被打破: {a['score']} vs {o['score']}"
        assert o["d1_mainline"] is False and o["d2_rk_bsp"] is False, "OV04C10 结论变了, 快照要重刷"
        print("[selftest] ✅ 快照可解析 + 已知排序成立 (AR0234CS > OV04C10)")
        return
    s = load_snap()
    sensors = [x for x in args if not x.startswith("-")] or DEFAULT_SENSORS
    rows = [score_one(x, s) for x in sensors]
    rows.sort(key=lambda r: (-r["score"], r["name"]))
    hdr = f"{'sensor':<11}{'总分':>6}  {'D1 内核驱动':<26}{'D2 RK BSP 驱动':<26}{'D3 IQ tuning':<12}{'D4 仓库':>7}{'D5 openipc':>11}"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['name']:<11}{r['score']:>3}/{r['max']}  "
              f"{('✔ ' + str(r['d1_file'])) if r['d1_mainline'] else '✘':<26}"
              f"{('✔ ' + str(r['d2_file'])) if r['d2_rk_bsp'] else '✘':<26}"
              f"{('✔ ' + str(r['d3_file'])) if r['d3_iq_file'] else '✘':<12}"
              f"{r['d4_github_repos']:>7}"
              f"{('✔' if r['d5_openipc'] else '✘'):>11}")
    print("\n判读: D1/D2 = 能不能直接用; D3 = 有没有现成 ISP tuning; D4/D5 = 有没有参考实现/公开规格。")


if __name__ == "__main__":
    main()
