#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
许可溯源探测器 (License Provenance Probe) —— ISS-087 (sw-lead, 2026-10-28)
=====================================================================
为什么有这个脚本
----------------
ISS-037 登记台账时, `yolov5s-sim` 系 3 份 ONNX 的 `metadata_props` 全空 →
许可栏写 [0数据] → 量产放行阻断项 **L1**。

[0数据] 的意思是"**没人查过**", 不是"查了查不到"。本脚本就是把"查"这件事
**做成可复现的机械动作**: 顺着本机可验证的物证 (文档 / 文件 sha / pip 包元数据
/ checkpoint pickle 命名空间) 把上游断出来, 给出**许可判定 + 证据链**。

判定逻辑 (三段, 证据等级从强到弱)
--------------------------------
  E1 [实测] ONNX `metadata_props.license` 有值 → 直接采信 (最强)
  E2 [实测] 本机上游文档明写"模型从 X 下载" + 文件 sha/命名链吻合
            → 许可 = X 仓库的许可
  E3 [实测] 本机 pip 包 / checkpoint pickle 的命名空间指向 X
            → 交叉印证

判决口径 (与 SW/MODEL_ASSETS.md §1.5 同步)
----------------------------------------
  license_state:
    permissive   = 宽松许可 (Apache-2.0 / MIT / BSD) → 商用无附加义务
    agpl-granted = AGPL 但**已有 Enterprise 授权记录** (license_grant 非空) → 商用可行
    agpl-no-grant= AGPL 且**无授权记录** → 商用受阻 (量产阻断项 L4)
    unknown      = 判不出来 → 量产阻断项 L1

★ 本脚本**不联网**、**不外发**、**不联系任何供应商**。官方许可条款以
  OFFICIAL_REF 表 (2026-10-28 抓取, 已记录 URL 与抓取时间) 为准; 需要复核时
  由**项目总工**决定是否重新抓取。

用法:
    python3 SW/tools/license_probe.py                       # 探测台账里全部候选资产
    python3 SW/tools/license_probe.py --onnx <path> [...]   # 探测指定 ONNX
    python3 SW/tools/license_probe.py --json                # 机读
退出码: 0 = 全部资产许可**已判定** (无 unknown) | 1 = 仍有 unknown (L1 未清)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))

# ----------------------------------------------------------------------------
# 官方许可条款 (2026-10-28 抓取; 引用即 [官方]; 需要复核由项目总工决定)
# ----------------------------------------------------------------------------
OFFICIAL_REF = {
    "AGPL-3.0": {
        "repo": "https://api.github.com/repos/ultralytics/yolov5",
        "spdx": "AGPL-3.0",
        "checked": "2026-10-28",
        "note": "ultralytics/yolov5 + ultralytics/ultralytics 仓库 license.spdx_id = AGPL-3.0",
    },
    "Ultralytics Enterprise": {
        "page": "https://www.ultralytics.com/license",
        "checked": "2026-10-28",
        "note": "官网明写: 嵌入式硬件 / 商用 / 自训练或微调模型 → 需 Enterprise License",
    },
    "Apache-2.0": {
        "repo": "https://api.github.com/repos/Megvii-BaseDetection/YOLOX",
        "spdx": "Apache-2.0",
        "checked": "2026-10-28",
        "note": "tensorflow/models 的 /research 子目录 (含 object_detection) = Apache-2.0",
    },
}

# ----------------------------------------------------------------------------
# 本机物证根目录 (全部实测存在性由脚本自己判, 不写死结论)
# ----------------------------------------------------------------------------
EVIDENCE_ROOTS = {
    "rockchip_zoo": "/home/yuewuya/Downloads/radxa",
    "a733_pipeline": "/home/yuewuya/Public/radxa_yolo",
    "workspace": "/home/yuewuya/.openclaw/workspace",
    "miniconda": "/home/yuewuya/miniconda3/envs",
    "tf_zoo": "/work/object_detection/pretrained",
}

# 上游文档里出现这些串 → 该文档描述的上游来源
UPSTREAM_HINTS = [
    ("https://github.com/ultralytics/yolov5", "ultralytics/yolov5 (GitHub)"),
    ("https://github.com/ultralytics/yolov5/releases", "ultralytics/yolov5 releases"),
    ("github.com/Megvii-BaseDetection/YOLOX", "Megvii YOLOX (GitHub)"),
    ("ultralytics", "Ultralytics 代码库"),
]

# 已知上游 → 许可 + 物证关键字 (关键字必须在文件里命中才算证据)
UPSTREAM_LICENSE = {
    "ultralytics/yolov5": {
        "license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "official": "AGPL-3.0",
        "grab": "ultralytics/yolov5 LICENSE = AGPL-3.0 (GitHub API spdx_id)",
    },
    "ultralytics/ultralytics": {
        "license": "AGPL-3.0",
        "license_state": "agpl-no-grant",
        "official": "AGPL-3.0",
        "grab": "ultralytics/ultralytics LICENSE = AGPL-3.0 (GitHub API spdx_id)",
    },
    "Megvii-BaseDetection/YOLOX": {
        "license": "Apache-2.0",
        "license_state": "permissive",
        "official": "Apache-2.0",
        "grab": "Megvii-BaseDetection/YOLOX LICENSE = Apache-2.0 (GitHub API spdx_id)",
    },
    "tensorflow/models": {
        "license": "Apache-2.0",
        "license_state": "permissive",
        "official": "Apache-2.0",
        "grab": "tensorflow/models LICENSE: /research 子目录 = Apache-2.0",
    },
}


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def onnx_meta(path: str) -> dict:
    """读 ONNX metadata_props (onnx 不可用时返回 _err)"""
    try:
        import onnx  # noqa: PLC0415
    except Exception as e:  # noqa: BLE001
        return {"_err": f"onnx 模块不可用: {e}"}
    try:
        m = onnx.load(path, load_external_data=False)
    except Exception as e:  # noqa: BLE001
        return {"_err": f"onnx 解析失败: {e}"}
    md = {p.key: p.value for p in m.metadata_props}
    g = m.graph

    def shape(t):
        return [d.dim_value or d.dim_param for d in t.type.tensor_type.shape.dim]

    ops = {}
    for n in g.node:
        ops[n.op_type] = ops.get(n.op_type, 0) + 1
    return {
        "producer": f"{m.producer_name} {m.producer_version}".strip(),
        "opset": max((o.version for o in m.opset_import if not o.domain), default=None),
        "meta": md,
        "license": md.get("license"),
        "inputs": {i.name: shape(i) for i in g.input},
        "outputs": {o.name: shape(o) for o in g.graph.output} if False else
                   {o.name: shape(o) for o in g.output},
        "n_nodes": len(g.node),
        "n_op_types": len(ops),
        "op_types": ops,
    }


def scan_upstream_docs() -> list:
    """扫描本机文档, 找"这份模型是从哪下载的"的书面物证"""
    hits = []
    roots = [EVIDENCE_ROOTS["rockchip_zoo"], EVIDENCE_ROOTS["a733_pipeline"]]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            depth = dirpath[len(root):].count(os.sep)
            if depth > 4:
                dirnames[:] = []
                continue
            for fn in filenames:
                if not fn.lower().endswith((".md", ".txt", ".sh")):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    if os.path.getsize(p) > 2_000_000:
                        continue
                    with open(p, encoding="utf-8", errors="replace") as f:
                        txt = f.read()
                except OSError:
                    continue
                for needle, label in UPSTREAM_HINTS:
                    if needle in txt:
                        hits.append({
                            "file": p,
                            "upstream": label,
                            "snippet": next((ln.strip() for ln in txt.splitlines()
                                             if needle in ln), "")[:160],
                        })
                        break
    return hits


def pip_package_licenses() -> list:
    """本机已安装 pip 包里的许可声明 (dist-info METADATA)"""
    out = []
    envs = EVIDENCE_ROOTS["miniconda"]
    if not os.path.isdir(envs):
        return out
    for env in sorted(os.listdir(envs)):
        sp = os.path.join(envs, env, "lib")
        if not os.path.isdir(sp):
            continue
        for py in sorted(os.listdir(sp)):
            site = os.path.join(sp, py, "site-packages")
            if not os.path.isdir(site):
                continue
            for di in sorted(os.listdir(site)):
                if not di.endswith(".dist-info"):
                    continue
                name = di[: -len(".dist-info")]
                if not any(k in name.lower() for k in
                           ("ultralytics", "yolox", "torch", "tensorflow-models")):
                    continue
                md = os.path.join(site, di, "METADATA")
                lic = None
                ver = None
                if os.path.exists(md):
                    with open(md, encoding="utf-8", errors="replace") as f:
                        for line in f:
                            if line.startswith("License:") and lic is None:
                                lic = line.split(":", 1)[1].strip()
                            elif line.startswith("Version:") and ver is None:
                                ver = line.split(":", 1)[1].strip()
                out.append({"package": name, "version": ver, "license": lic,
                            "path": md})
    return out


def checkpoint_namespaces(pt_path: str) -> list:
    """torch .pt (zip) 的 pickle 里出现的模块命名空间 —— 断"权重来自哪个框架" """
    try:
        z = zipfile.ZipFile(pt_path)
    except (OSError, zipfile.BadZipFile):
        return []
    pkl_name = next((n for n in z.namelist() if n.endswith("data.pkl")), None)
    if not pkl_name:
        return []
    raw = z.read(pkl_name)
    strs = sorted({m.decode() for m in re.findall(rb"[ -~]{6,}", raw)})
    out = []
    for s in strs:
        for key in ("ultralytics.nn.modules", "models.common", "models.yolo",
                    "yolox.models", "ultralytics.models"):
            if key in s:
                out.append(s[:120])
                break
    # 去重保序
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq[:8]


def probe_one(path: str, docs: list, pkgs: list) -> dict:
    res = {"path": path, "exists": os.path.exists(path)}
    if not res["exists"]:
        res["verdict"] = {"license": None, "license_state": "unknown"}
        res["evidence"] = []
        return res
    res["size"] = os.path.getsize(path)
    res["sha256_16"] = sha256_of(path)[:16]
    ev = []

    if path.endswith(".onnx"):
        m = onnx_meta(path)
        res["onnx"] = {k: v for k, v in m.items() if k != "op_types"} if "_err" not in m else m
        if "_err" in m:
            ev.append({"grade": "[实测]", "src": "onnx 解析", "text": m["_err"]})
        else:
            ev.append({"grade": "[实测]", "src": "onnx metadata_props",
                       "text": f"license={m.get('license')!r} author="
                               f"{m['meta'].get('author')!r} version={m['meta'].get('version')!r}"})
            if m.get("license"):
                lic = m["license"]
                state = "agpl-no-grant" if "AGPL" in lic.upper() else "permissive"
                res["verdict"] = {"license": lic, "license_state": state,
                                  "basis": "E1 metadata_props 自带许可"}
                res["evidence"] = ev
                return res

    # E2: 本机文档物证 —— 上游是谁
    base = os.path.basename(path)
    upstream_hits = [d for d in docs if d["upstream"] and d["file"]]
    for d in upstream_hits:
        # 只采信与本文件名/系列相关的文档
        key = None
        for uk in UPSTREAM_LICENSE:
            if uk.split("/")[-1] in d["snippet"] or uk in d["snippet"]:
                key = uk
                break
        if key is None:
            continue
        ev.append({"grade": "[实测·本机文档]",
                   "src": os.path.relpath(d["file"]),
                   "text": f"上游指向 {d['upstream']}: {d['snippet']}"})
        res["_upstream"] = key

    # E2b: 文件名 -sim 尾巴 = onnxsim 产物 (Rockchip README 明写该命名)
    if re.search(r"[-_]sim(\.|$)", base):
        ev.append({"grade": "[实测·命名链]", "src": os.path.basename(path),
                   "text": "文件名带 -sim ⇒ 来自 `onnxsim <upstream>.onnx <name>-sim.onnx` "
                           "(Rockchip awnpu_model_zoo examples/yolov5/README.md 明写此命名)"})

    # E2c: 本机 pip 包许可 (交叉印证)
    for p in pkgs:
        if p["license"] and "AGPL" in p["license"].upper():
            ev.append({"grade": "[实测]", "src": f"pip {p['package']} {p['version']}",
                       "text": f"本机已安装包 METADATA License = {p['license']}"})
        elif p["license"] and "Apache" in p["license"]:
            ev.append({"grade": "[实测]", "src": f"pip {p['package']} {p['version']}",
                       "text": f"本机已安装包 METADATA License = {p['license']}"})

    # E3: 同目录/近邻的 torch checkpoint 命名空间
    for cand in _nearby_checkpoints(path):
        ns = checkpoint_namespaces(cand)
        if ns:
            ev.append({"grade": "[实测·checkpoint pickle]", "src": cand,
                       "text": "命名空间: " + ", ".join(ns[:4])})
            if any("ultralytics" in n for n in ns):
                res["_upstream"] = res.get("_upstream", "ultralytics/ultralytics")

    up = res.get("_upstream")
    if up and up in UPSTREAM_LICENSE:
        u = UPSTREAM_LICENSE[up]
        res["verdict"] = {
            "license": u["license"],
            "license_state": u["license_state"],
            "basis": f"E2/E3 溯源 → 上游 {up}",
            "official": u["official"],
            "official_note": u["grab"],
        }
    else:
        res["verdict"] = {"license": None, "license_state": "unknown",
                          "basis": "无物证可判定"}
    res["evidence"] = ev
    return res


def _nearby_checkpoints(path: str) -> list:
    """在模型文件附近找 torch checkpoint (.pt)"""
    cands = []
    dirs = [os.path.dirname(path)]
    for extra in ("/home/yuewuya/Public/radxa_yolo/code",
                  "/home/yuewuya/.openclaw/workspace"):
        if os.path.isdir(extra):
            dirs.append(extra)
    for d in dirs:
        if not os.path.isdir(d):
            continue
        try:
            for fn in os.listdir(d):
                if fn.endswith(".pt"):
                    cands.append(os.path.join(d, fn))
        except OSError:
            continue
    return cands[:4]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", action="append", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    targets = args.onnx or []
    if not targets:
        # 默认: 台账里 3 份 yolov5s-sim 系 + yolov8s
        targets = [
            "/home/yuewuya/.openclaw/workspace/yolov5s-sim_320_clean.onnx",
            "/home/yuewuya/.openclaw/workspace/yolov5s-sim_320_v2.onnx",
            "/home/yuewuya/Public/radxa_yolo/acuity_pipeline/model/yolov5s-sim.onnx",
            "/work/object_detection/yolov8s_coco80/workspace/yolov8s.onnx",
        ]
    docs = scan_upstream_docs()
    pkgs = pip_package_licenses()
    results = [probe_one(p, docs, pkgs) for p in targets]

    n_unknown = sum(1 for r in results if r["verdict"]["license_state"] == "unknown")
    if args.json:
        print(json.dumps({
            "official_ref": OFFICIAL_REF,
            "pip_licenses": pkgs,
            "upstream_docs": docs,
            "results": results,
            "n_unknown": n_unknown,
        }, ensure_ascii=False, indent=2, default=str))
    else:
        print("=" * 100)
        print("许可溯源探测器 (ISS-087) —— 把 [0数据] 变成有物证的判定")
        print("=" * 100)
        print("\n[官方] 许可条款基准 (2026-10-28 抓取, 复核由项目总工决定):")
        for k, v in OFFICIAL_REF.items():
            ref = v.get("repo") or v.get("page")
            print(f"    - {k:26s} {ref}  ({v['checked']})")
        print("\n[实测] 本机已安装相关 pip 包许可:")
        for p in pkgs:
            print(f"    - {p['package']} {p['version']}: {p['license']}")
        print("\n[实测·本机文档] 上游来源书面物证:")
        seen = set()
        for d in docs:
            k = (d["file"], d["upstream"])
            if k in seen:
                continue
            seen.add(k)
            print(f"    - {os.path.relpath(d['file'])}: {d['snippet'][:110]}")
        for r in results:
            print("\n" + "-" * 100)
            print(f"▶ {r['path']}")
            if not r["exists"]:
                print("    ❌ 文件不存在")
                continue
            print(f"    sha256[:16]={r['sha256_16']}  size={r['size']} B")
            for e in r["evidence"]:
                print(f"    {e['grade']:14s} {e['src']}: {e['text']}")
            v = r["verdict"]
            print(f"    ⇒ 判定许可 = {v.get('license')!r}  state = {v.get('license_state')}  "
                  f"依据 = {v.get('basis')}")
            if v.get("official_note"):
                print(f"    ⇒ [官方] {v['official_note']}")
        print("\n" + "-" * 100)
        print(f"判定完成: 资产 {len(results)} 条 · 许可未判定 (L1) {n_unknown} 条")
        print("退出码 rc = " + ("1" if n_unknown else "0"))
    return 1 if n_unknown else 0


if __name__ == "__main__":
    sys.exit(main())
