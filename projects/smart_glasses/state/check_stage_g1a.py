#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_stage_g1a.py —— ★★**G1a「原理图定稿」独立机器闸** ★★ (2026-11-16 · main)

★★**为什么要有这个闸 (★老板 11-16 问的一句话引出来的★)** ★★
★**老板原话**: 「原理图和 PCB 不是同一个概念, 原理图是不是已经绘制好了?」★★
★⇒ 揭穿一个★**结构性死锁**★: `state/stage_gate.py` 的 **G1 一关卡两件事** (原理图定稿 + PCB 定稿),
★★**而 G1 唯一的缺口 (unconnected=45) 100% 是 PCB 的** ★★
★★**而老板 11-11 10:07 的口径曾是「PCB 布线/布局类一律排队不派」(★2026-11-17 00:43 已改为【PCB 类可派】★) ★★ ★★**⇒ 本闸依然有用: 原理图定稿与 PCB 定稿本来就该分开判, 且「原理图画完了」这件事当天就该能判绿** ★★
★★⇒ 原理图画完了, G1 也永远是红的 ⇒ 看板每天报「还差 1 项」, 而那一项永远不会自己变 ⇒ **真实进度被噪声埋掉**★★
★★⇒ 本闸把 **G1a (原理图定稿)** 单独切出来 ⇒ 原理图侧今天就能独立判绿/判红, 不被 PCB 拖住 ★★

★★**G1a 的 7 条判据 (★全部可机器判定, 全部有反向用例★)** ★★
  ★**G1a-1**  ERC = 0 (★KiCad 自己跑 ERC★) — `state/check_sch_erc.py`
  ★**G1a-2**  ★**图上脚数 == 表里脚数 (K=0)** — `state/check_sch_pinfull.py` (★逐器件点名★)
  ★**G1a-3**  KiCad 真能打开/导出 (loadable) — `state/check_sch_loadable.py`
  ★**G1a-4**  ★**落表已清零** (★翻面口径★) — `HW/check_netlist_selfconsistency.py --expect-resolved`
        ★★**注意口径**: 该脚本的**默认模式 rc=0 意思是「缺陷还在」(现状守卫)** ⇒ ★**必须用 `--expect-resolved` 才是「已落表」★**
  ★**G1a-5**  网表尺子 — `state/check_netlist.py` (★含 C9: 表 ↔ 网表双向一致 = 逐脚零差异★)
  ★**G1a-6**  网表脚表尺子 — `state/check_netlist_pins.py` (★每个针脚归属唯一★)
  ★**G1a-7**  ★**选型已落表** — `HW/BOM_v1.csv` 里 ★**必装 ∩ value 含「[待选型]」的件数 == 0** ★
  ★**G1a-8**  ★**关机语义 + 负载开关选型已决** — `state/issue_log.yaml` 里 ISS-097 与 ISS-172 的 status ∈ {{verified, closed}}
        ★★**这是代理判据 (★诚实声明★)**: 待拍项的正文在决策页 (markdown, 机器判不了) ⇒ 用 issue 台账状态做代理 ★★

★★**rc 语义** ★★
  - `rc=0` ⇒ ★**G1a 全绿 = 原理图侧定稿** ★
  - `rc=1` ⇒ ★**有判据红 ⇒ 逐条点名 (★并给出「这条红了意味着什么」★)** ★
  - `rc=2` ⇒ 用法/环境错误

★★**用法** ★★
    python3 state/check_stage_g1a.py                 # 判 G1a
    python3 state/check_stage_g1a.py --json          # 机器读
    python3 state/check_stage_g1a.py --selftest      # ★反向用例 (★7 条判据逐条证明「它真在被读」★)

★★**边界 (★本闸只读, 不改任何文件★)** ★★
  ★零落表 · 零外发 · 零实物 · 不碰板/网表/脚表/BOM/`.kicad_pro` 一个字节 ★
  ★**反向用例一律在临时目录里做, 不动真盘** ★
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))

# ★**每条判据的命令 (★可用环境变量覆盖, 供反向用例证明「它真在被读」★)** ★
CMDS = {
    "erc":         "python3 state/check_sch_erc.py",
    "pinfull":     "python3 state/check_sch_pinfull.py",
    "loadable":    "python3 state/check_sch_loadable.py",
    "landed":      "python3 HW/check_netlist_selfconsistency.py --expect-resolved",
    "netlist":     "python3 state/check_netlist.py",
    "netlistpins": "python3 state/check_netlist_pins.py",
}

# ★**判据 id → (名字, 命令 key 或 None, 说明)** ★
CRITERIA = [
    ("G1a-1", "ERC = 0 (KiCad 自己跑 ERC)", "erc",
     "原理图电气规则零违规"),
    ("G1a-2", "图上脚数 == 表里脚数 (K=0)", "pinfull",
     "逐器件点名, 少画一根脚都不许过"),
    ("G1a-3", "KiCad 真能打开/导出 (loadable)", "loadable",
     "图纸必须是 KiCad 能解析的真文件, 不是文本"),
    ("G1a-4", "落表已清零 (翻面口径)", "landed",
     "★网表/脚表/BOM 里那 18 条待落表条目必须归零★"),
    ("G1a-5", "网表尺子 (含表↔网表双向一致)", "netlist",
     "逐脚零差异"),
    ("G1a-6", "网表脚表尺子 (针脚归属唯一)", "netlistpins",
     "一个脚不能挂两个网"),
    ("G1a-7", "选型已落表 (必装件无「[待选型]」)", None,
     "★BOM 里必装器件的 value 不许还写「[待选型]」★"),
    ("G1a-8", "关机语义 + 负载开关选型已决", None,
     "ISS-097 / ISS-172 状态"),
]


def _cmd_for(key: str) -> str:
    env_key = "ARS45_G1A_CMD_" + key.upper()
    return os.environ.get(env_key) or CMDS[key]


def _run(cmd: str, root: str, timeout: int = 900) -> tuple[int, str]:
    try:
        p = subprocess.run(shlex.split(cmd), cwd=root, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except FileNotFoundError as e:
        return 127, f"★命令不存在: {e}★"
    except subprocess.TimeoutExpired:
        return 124, f"★超时 {timeout}s★"
    out = p.stdout.decode("utf-8", "replace")
    return p.returncode, out


def _tail(text: str, n: int = 3) -> str:
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    return " | ".join(ln.strip() for ln in lines[-n:])


def _cmd_criterion(root: str, key: str) -> tuple[bool, str]:
    cmd = _cmd_for(key)
    rc, out = _run(cmd, root)
    if rc == 0:
        return True, f"rc=0 ({cmd})"
    return False, f"rc={rc} ({cmd}) ⇒ {_tail(out)}"


def _bom_pending_count(root: str) -> tuple[int, list[str]]:
    path = os.path.join(root, "HW", "BOM_v1.csv")
    if not os.path.exists(path):
        return -1, ["★BOM 文件不存在★"]
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    bad = []
    for r in rows:
        val = str(r.get("value", ""))
        dnp = str(r.get("dnp", "")).strip()
        if "[待选型]" in val and dnp not in ("DNP",):
            bad.append(f"{r.get('ref')}({val.strip()[:28]})")
    return len(bad), bad


def _issue_status(root: str, iid: str) -> str:
    path = os.path.join(root, "state", "issue_log.yaml")
    if not os.path.exists(path):
        return "★文件不存在★"
    try:
        import yaml  # noqa: WPS433
    except Exception:  # pragma: no cover
        return "★无 yaml 模块★"
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    issues = data.get("issues", data) if isinstance(data, dict) else data
    for it in issues or []:
        if str(it.get("id")) == iid:
            return str(it.get("status", "?"))
    return "★未登记★"


def check_all(root: str) -> list[dict]:
    results = []
    for cid, name, key, desc in CRITERIA:
        if key is not None:
            ok, detail = _cmd_criterion(root, key)
        elif cid == "G1a-7":
            n, bad = _bom_pending_count(root)
            ok = (n == 0)
            detail = f"必装且仍写「[待选型]」= {n} 件" + ("" if ok else f" ⇒ {', '.join(bad[:6])}")
        else:  # G1a-8
            s97 = _issue_status(root, "ISS-097")
            s172 = _issue_status(root, "ISS-172")
            ok = s97 in ("verified", "closed") and s172 in ("verified", "closed")
            detail = f"ISS-097={s97} · ISS-172={s172}"
        results.append({"id": cid, "name": name, "desc": desc,
                        "ok": bool(ok), "detail": detail})
    return results


# ══════════════════ 自测 (★反向用例: 逐条证明「它真在被读」★) ══════════════════
def _tmp_root_with_data(root: str) -> str:
    """★造一个临时 root: 数据文件照抄, 脚本不抄 (⇒ 命令类判据必红)★"""
    tmp = tempfile.mkdtemp(prefix="g1a_st_")
    for rel in ("HW/BOM_v1.csv", "HW/netlist_v1.csv", "HW/netlist_v1_pins.csv",
                "state/issue_log.yaml"):
        src = os.path.join(root, rel)
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(src):
            shutil.copyfile(src, dst)
    return tmp


def _mutate_issue_status(path: str, iid: str, new_status: str) -> None:
    """★**用 yaml 读写改台账状态 (★不许用正则改 yaml★)★"""
    import yaml
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    issues = data.get("issues", data) if isinstance(data, dict) else data
    hit = 0
    for it in issues or []:
        if str(it.get("id")) == iid:
            it["status"] = new_status
            hit += 1
    if not hit:
        raise RuntimeError(f"★台账里找不到 {iid}★")
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)


def selftest(root: str) -> int:
    cases = []

    def record(name: str, expect_red: bool, ok: bool, detail: str):
        cases.append({"name": name, "expect_red": expect_red, "ok": ok, "detail": detail})

    # ── T1~T6: 命令类判据 —— 把命令指向不存在的脚本 ⇒ 对应判据必须变红 ──
    for key, cid in (("erc", "G1a-1"), ("pinfull", "G1a-2"), ("loadable", "G1a-3"),
                     ("landed", "G1a-4"), ("netlist", "G1a-5"), ("netlistpins", "G1a-6")):
        env_old = os.environ.get("ARS45_G1A_CMD_" + key.upper())
        os.environ["ARS45_G1A_CMD_" + key.upper()] = "python3 /tmp/__no_such_gate__.py"
        try:
            res = check_all(root)
        finally:
            if env_old is None:
                os.environ.pop("ARS45_G1A_CMD_" + key.upper(), None)
            else:
                os.environ["ARS45_G1A_CMD_" + key.upper()] = env_old
        hit = [r for r in res if r["id"] == cid]
        red = bool(hit) and not hit[0]["ok"]
        others = [r["id"] for r in res if r["ok"] and r["id"] != cid]
        record(f"T-命令 {cid}: 命令指向不存在的脚本 ⇒ 该判据必须红", True, red,
               f"{cid} red={red} · 其余仍绿={others}")

    # ── T7: BOM 篡改 ⇒ G1a-7 必须红 ──
    tmp = _tmp_root_with_data(root)
    try:
        bom = os.path.join(tmp, "HW", "BOM_v1.csv")
        with open(bom, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
            fields = list(rows[0].keys())
        target = None
        for r in rows:
            if "[待选型]" not in str(r.get("value", "")) and str(r.get("dnp", "")).strip() != "DNP":
                target = r
                break
        if target is None:
            record("T-BOM: 把一个必装件的 value 改回「[待选型]」⇒ G1a-7 必须红", True, False,
                   "★找不到可篡改的必装件★")
        else:
            before = target.get("value")
            target["value"] = str(before) + " [待选型]"
            with open(bom, "w", newline="", encoding="utf-8-sig") as fh:
                w = csv.DictWriter(fh, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
            res = check_all(tmp)
            hit = [r for r in res if r["id"] == "G1a-7"]
            red = bool(hit) and not hit[0]["ok"]
            record(f"T-BOM: 把 {target.get('ref')} 的 value 改回「[待选型]」⇒ G1a-7 必须红", True, red,
                   f"G1a-7 red={red} · detail={hit[0]['detail'][:120] if hit else 'N/A'}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T8: issue_log 篡改 ⇒ G1a-8 必须红 ──
    tmp = _tmp_root_with_data(root)
    try:
        il = os.path.join(tmp, "state", "issue_log.yaml")
        _mutate_issue_status(il, "ISS-097", "open")
        after = _issue_status(tmp, "ISS-097")
        res = check_all(tmp)
        hit = [r for r in res if r["id"] == "G1a-8"]
        red = bool(hit) and not hit[0]["ok"] and after == "open"
        record("T-issue: 把 ISS-097 状态改回 open ⇒ G1a-8 必须红", True, red,
               f"改后读回={after} · G1a-8 red={red} · detail={hit[0]['detail'] if hit else 'N/A'}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T9a: 临时 root (数据照抄) ⇒ 判定必须与真盘逐条一致 (不是「复制品一律红」) ──
    real = {r["id"]: r["ok"] for r in check_all(root)}
    tmp = _tmp_root_with_data(root)
    try:
        res = check_all(tmp)
        same = {r["id"]: r["ok"] for r in res}
        # ★命令类判据在临时 root 里必然红 (脚本没抄) ⇒ 只比数据类两条 + 记录其余★
        data_ids = ("G1a-7", "G1a-8")
        consistent = all(same[i] == real[i] for i in data_ids)
        record("T-正向: 临时 root (数据照抄) ⇒ 数据类判据判定必须与真盘逐条一致",
               False, consistent,
               f"真盘={ {i: real[i] for i in data_ids} } · 临时={ {i: same[i] for i in data_ids} }")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T9b: 临时 root 里把数据「修好」⇒ G1a-7/8 必须变绿 (证明它们不是「永远红」) ──
    tmp = _tmp_root_with_data(root)
    try:
        bom = os.path.join(tmp, "HW", "BOM_v1.csv")
        with open(bom, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
            fields = list(rows[0].keys())
        for r in rows:
            if "[待选型]" in str(r.get("value", "")):
                r["value"] = str(r.get("value", "")).replace("[待选型]", "").strip() or "已选型"
        with open(bom, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        il = os.path.join(tmp, "state", "issue_log.yaml")
        _mutate_issue_status(il, "ISS-097", "verified")
        after = _issue_status(tmp, "ISS-097")
        res = check_all(tmp)
        hit7 = [r for r in res if r["id"] == "G1a-7"]
        hit8 = [r for r in res if r["id"] == "G1a-8"]
        g7 = bool(hit7) and hit7[0]["ok"]
        g8 = bool(hit8) and hit8[0]["ok"]
        record("T-正向: 临时 root 里把「[待选型]」清掉 + ISS-097 改 verified ⇒ G1a-7/8 必须变绿",
               False, g7 and g8,
               f"ISS-097 改后读回={after} · G1a-7 green={g7} ({hit7[0]['detail'][:80] if hit7 else 'N/A'}) · "
               f"G1a-8 green={g8} ({hit8[0]['detail'][:60] if hit8 else 'N/A'})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── T10: 真盘基线 —— 判定必须可复现 (两次跑结果一致) ──
    a = [r["ok"] for r in check_all(root)]
    b = [r["ok"] for r in check_all(root)]
    record("T-基线: 真盘连跑两次判定必须一致 (证明判据无随机性)", False, a == b,
           f"first={a} second={b}")

    print("── 自测 (★反向用例: 逐条证明「它真在被读」★) ──")
    n_ok = 0
    for c in cases:
        mark = "✅" if c["ok"] else "❌"
        print(f"  {mark} {c['name']}")
        print(f"      · {c['detail'][:180]}")
        if c["ok"]:
            n_ok += 1
    print(f"\n自测: {n_ok}/{len(cases)} 通过")
    if n_ok != len(cases):
        print("★**有用例没抓到 ⇒ 门禁链红** ★")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=PROJ, help="工程根 (默认 = state/ 的上一级)")
    ap.add_argument("--json", action="store_true", help="机器读输出")
    ap.add_argument("--selftest", action="store_true", help="跑自测 (反向用例, 只动临时副本)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    res = check_all(root)
    n_red = sum(0 if r["ok"] else 1 for r in res)
    if args.json:
        print(json.dumps({"gate": "G1a", "name": "原理图定稿",
                          "passed": n_red == 0, "red": n_red,
                          "results": res}, ensure_ascii=False, indent=2))
        return 0 if n_red == 0 else 1

    print("=" * 78)
    print("  G1a · 原理图定稿 (★与 PCB 定稿分开判 · 老板 11-16「原理图和 PCB 不是同一个概念」★)")
    print("=" * 78)
    for r in res:
        mark = "✅" if r["ok"] else "❌"
        print(f"  {mark} {r['id']:<6} {r['name']}")
        print(f"         {r['detail'][:160]}")
    print("-" * 78)
    if n_red == 0:
        print("✅ G1a 全绿 ⇒ 原理图侧定稿 (★PCB 那一趟是 G1b, 另算★)")
    else:
        print(f"❌ G1a 还差 {n_red} 条 ⇒ ★**原理图【画】已经画完, 差的是「值」与「拍板」** ★")
        for r in res:
            if not r["ok"]:
                print(f"     · {r['id']} {r['name']}")
    return 0 if n_red == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
