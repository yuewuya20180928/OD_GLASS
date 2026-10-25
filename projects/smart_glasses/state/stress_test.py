#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STATE 协议 · 并发 / 压力 / 异常输入 测试台
=========================================
老板 10-25 指令: "先压力和并发测试一下各个agent之间的通信是否正常及是否会存在异常通信结果"

本脚本在**沙盒副本**里跑 (不碰 projects/smart_glasses/STATE.yaml 和真实分片), 覆盖:

  T1 并发合并      20 个 merge.py 进程同时跑 → 快照完整 / 无重复 / 无残留 .tmp
  T2 撕裂读        分片非原子写 (truncate + 分块) 与合并并发 → 统计"跳过/解析失败"与**静默丢数据**
  T3 读者一致性    合并风暴中反复读 STATE.yaml → 是否读到半截快照
  T4 配对语义      needs×answers 配对 / 第三方代答 / key 写错 (静默不闭合)
  T5 异常输入      坏 YAML / 空文件 / BOM / 非 dict / 重复 key / 错类型 / agent 名冒名
  T6 同分片并发写  两个进程同时写同一个分片 → 是否损坏文件

用法:  python3 state/stress_test.py [--rounds N] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
# 可用 STRESS_MERGE=/path/to/merge.py 跑别的版本 (回归用)
MERGE_SRC = os.environ.get("STRESS_MERGE") or os.path.join(HERE, "merge.py")
AGENTS = ["main", "hw-lead", "sw-lead", "mech-lead"]
# agent id → 分片文件名 (跟真实项目一致: pm.yaml 里写的 agent 是 main)
FILE_OF = {"main": "pm.yaml", "hw-lead": "hw.yaml", "sw-lead": "sw.yaml", "mech-lead": "mech.yaml"}


# ----------------------------------------------------------------- 沙盒
def mk_sandbox() -> str:
    root = tempfile.mkdtemp(prefix="state_stress_")
    os.makedirs(os.path.join(root, "state", "fragments"))
    shutil.copy2(MERGE_SRC, os.path.join(root, "state", "merge.py"))
    return root


def frag_path(root: str, name: str) -> str:
    return os.path.join(root, "state", "fragments", name)


def write_frag(root: str, name: str, data: dict) -> None:
    with open(frag_path(root, name), "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def frags_of(root: str) -> None:
    """按真实命名写全部分片 (pm/hw/sw/mech)。"""
    for a in AGENTS:
        write_frag(root, FILE_OF[a], base_frag(a, 0))


def write_frag_nonatomic(root: str, name: str, data: dict, chunk_sleep=0.004) -> None:
    """故意用非原子写法: 先 truncate, 再分块慢写 → 制造"半截 YAML"窗口。"""
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    with open(frag_path(root, name), "w", encoding="utf-8") as f:
        for i in range(0, len(text), 512):
            f.write(text[i:i + 512])
            f.flush()
            time.sleep(chunk_sleep)


def run_merge(root: str) -> tuple[int, str, str]:
    p = subprocess.run([sys.executable, "state/merge.py"], cwd=root,
                       capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout, p.stderr


def load_state(root: str):
    with open(os.path.join(root, "STATE.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def base_frag(agent: str, n_art: int = 0, marker: str | None = None) -> dict:
    arts = []
    for i in range(n_art):
        arts.append({
            "path": f"stress/{agent}_{i}.md",
            "kind": "stress",
            "version": "1.0",
            "updated_at": "2026-10-25",
            "summary": f"stress {agent} #{i}" + (f" MARK={marker}" if marker and i == 0 else ""),
        })
    return {
        "agent": agent,
        "role": agent,
        "updated_at": "2026-10-25T09:10:00+08:00",
        "updated_by": agent,
        "status": {"phase": "stress", "progress_pct": 1, "health": "green", "summary": f"stress {agent}"},
        "artifacts": arts,
        "blockers": [],
        "needs_from": [],
        "answers": [],
        "interface_claims": [],
    }


# ----------------------------------------------------------------- T1
def t1_concurrent_merge(rounds: int = 20) -> dict:
    root = mk_sandbox()
    for a in AGENTS:
        write_frag(root, FILE_OF[a], base_frag(a, 50))
    errs, rcs = [], []
    lock = threading.Lock()

    def one():
        rc, out, err = run_merge(root)
        with lock:
            rcs.append(rc)
            if err.strip():
                errs.append(err.strip())

    ts = [threading.Thread(target=one) for _ in range(rounds)]
    t0 = time.time()
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    dt = time.time() - t0

    st = load_state(root)
    counts = {a: len(st["domains"][a]["artifacts"]) for a in AGENTS}
    all_paths = [ar["path"] for d in st["domains"].values() for ar in d["artifacts"]]
    leftovers = [f for f in os.listdir(root) if f.endswith(".tmp")]
    res = {
        "rounds": rounds,
        "elapsed_s": round(dt, 2),
        "returncodes": sorted(set(rcs)),
        "stderr_lines": len(errs),
        "artifact_count_per_agent": counts,
        "total_artifacts": len(all_paths),
        "expected_artifacts": 50 * len(AGENTS),
        "duplicates": len(all_paths) - len(set(all_paths)),
        "lost": (50 * len(AGENTS)) - len(all_paths),
        "tmp_leftovers": leftovers,
        "domains_present": sorted(st["domains"].keys()),
        "state_valid": True,
    }
    shutil.rmtree(root, ignore_errors=True)
    return res


# ----------------------------------------------------------------- T2
def t2_torn_read(duration_s: float = 6.0) -> dict:
    """分片非原子写 × 并发合并 → 找 '跳过/解析失败' 与 静默丢数据。"""
    root = mk_sandbox()
    for a in AGENTS:
        write_frag(root, FILE_OF[a], base_frag(a, 3))
    stop = threading.Event()
    stats = {"merge_runs": 0, "skips": 0, "loss_events": 0, "stale_events": 0, "rc_nonzero": 0,
             "skip_examples": [], "loss_examples": []}
    lock = threading.Lock()
    committed = []          # 已完整落盘的 marker 列表
    committed_lock = threading.Lock()

    def writer():
        i = 0
        while not stop.is_set():
            marker = f"MK{i}"
            d = base_frag("hw-lead", 3, marker=marker)
            write_frag_nonatomic(root, "hw.yaml", d)
            with committed_lock:
                committed.append(marker)
            i += 1
            time.sleep(0.01)

    def merger():
        while not stop.is_set():
            rc, out, err = run_merge(root)
            with lock:
                stats["merge_runs"] += 1
                if rc != 0:
                    stats["rc_nonzero"] += 1
                if "解析失败" in err or "跳过" in err:
                    stats["skips"] += 1
                    if len(stats["skip_examples"]) < 3:
                        stats["skip_examples"].append(err.strip()[:200])
            # 静默丢数据检测: 区分"整域消失" vs "数据过期(回退到旧快照)"
            with committed_lock:
                last = committed[-1] if committed else None
            if last:
                try:
                    st = load_state(root)
                    dom = st["domains"].get("hw-lead")
                    if dom is None:
                        with lock:
                            stats["loss_events"] += 1
                            if len(stats["loss_examples"]) < 3:
                                stats["loss_examples"].append("hw-lead 整个域从快照里消失")
                    else:
                        summ = [str(ar.get("summary", "")) for ar in dom.get("artifacts", [])]
                        if not any("MARK=" in s for s in summ):
                            with lock:
                                stats["loss_events"] += 1
                                if len(stats["loss_examples"]) < 3:
                                    stats["loss_examples"].append("域在但一条 marker 都没有")
                        elif not any(f"MARK={last}" in s for s in summ):
                            with lock:
                                stats["stale_events"] += 1
                except Exception as e:  # noqa: BLE001
                    with lock:
                        stats["loss_events"] += 1
                        if len(stats["loss_examples"]) < 3:
                            stats["loss_examples"].append(f"STATE.yaml 读失败: {e}")
            time.sleep(0.01)

    wt = threading.Thread(target=writer)
    mt = threading.Thread(target=merger)
    wt.start()
    mt.start()
    time.sleep(duration_s)
    stop.set()
    wt.join()
    mt.join()
    stats["duration_s"] = duration_s
    stats["writer_iterations"] = len(committed)
    shutil.rmtree(root, ignore_errors=True)
    return stats


# ----------------------------------------------------------------- T3
def t3_reader_consistency(duration_s: float = 5.0) -> dict:
    root = mk_sandbox()
    for a in AGENTS:
        write_frag(root, FILE_OF[a], base_frag(a, 5))
    stop = threading.Event()
    st_ = {"reads": 0, "invalid": 0, "missing_domains": 0, "examples": []}
    lock = threading.Lock()

    def churner():
        while not stop.is_set():
            for a in AGENTS:
                write_frag(root, FILE_OF[a], base_frag(a, 5))
            run_merge(root)

    def reader():
        while not stop.is_set():
            try:
                st = load_state(root)
                with lock:
                    st_["reads"] += 1
                    if not st or "meta" not in st:
                        st_["invalid"] += 1
                    elif any(a not in st.get("domains", {}) for a in AGENTS):
                        st_["missing_domains"] += 1
            except Exception as e:  # noqa: BLE001
                with lock:
                    st_["reads"] += 1
                    st_["invalid"] += 1
                    if len(st_["examples"]) < 3:
                        st_["examples"].append(str(e)[:160])
            time.sleep(0.002)

    run_merge(root)          # 先落一份快照, 否则读者会误报 "文件不存在" (假阳性)
    ct = threading.Thread(target=churner)
    rt = threading.Thread(target=reader)
    ct.start()
    rt.start()
    time.sleep(duration_s)
    stop.set()
    ct.join()
    rt.join()
    st_["duration_s"] = duration_s
    shutil.rmtree(root, ignore_errors=True)
    return st_


# ----------------------------------------------------------------- T4
def t4_pairing_semantics() -> dict:
    root = mk_sandbox()
    hw = base_frag("hw-lead")
    hw["needs_from"] = [
        {"key": "K1", "to": "sw-lead", "item": "正常需求", "since": "2026-10-25"},
        {"key": "K2", "to": "sw-lead", "item": "第三方代答需求", "since": "2026-10-25"},
        {"key": "K3", "to": "sw-lead", "item": "key 写错需求", "since": "2026-10-25"},
    ]
    sw = base_frag("sw-lead")
    sw["answers"] = [
        {"key": "K1", "to": "hw-lead", "value": "ok", "ref": "x"},
        {"key": "K2", "to": "hw-lead", "value": "越权代答", "ref": "x"},
        {"key": "K3_typo", "to": "hw-lead", "value": "写错key", "ref": "x"},
    ]
    mech = base_frag("mech-lead")
    mech["answers"] = [{"key": "K1", "to": "hw-lead", "value": "第三方插队", "ref": "x"}]
    write_frag(root, "hw.yaml", hw)
    write_frag(root, "sw.yaml", sw)
    write_frag(root, "mech.yaml", mech)
    write_frag(root, "pm.yaml", base_frag("main"))
    rc, out, err = run_merge(root)
    st = load_state(root)
    needs = {n["key"]: n for n in st["domains"]["hw-lead"]["needs_from"]}
    res = {
        "rc": rc,
        "K1_state": needs["K1"]["state"],
        "K1_foreign": [f["by"] for f in needs["K1"]["foreign_answers"]],
        "K2_state": needs["K2"]["state"],
        "K2_foreign": [f["by"] for f in needs["K2"]["foreign_answers"]],
        "K3_state": needs["K3"]["state"],
        "lint_keys": [l["key"] for l in st.get("lint", [])],
        "open_needs": st["summary"]["open_needs"],
    }
    shutil.rmtree(root, ignore_errors=True)
    return res


# ----------------------------------------------------------------- T5
def t5_abnormal_inputs() -> list:
    cases = []

    def run_case(name: str, mutate, expect_note: str):
        root = mk_sandbox()
        for a in AGENTS:
            write_frag(root, FILE_OF[a], base_frag(a, 2))
        mutate(root)
        rc, out, err = run_merge(root)
        entry = {"case": name, "rc": rc, "expect": expect_note}
        try:
            st = load_state(root)
            entry["state_valid"] = isinstance(st, dict) and "domains" in st
            entry["domains"] = sorted(st.get("domains", {}).keys())
            entry["lint"] = len(st.get("lint", []))
            entry["conflicts"] = len(st.get("conflicts", []))
            entry["summary"] = st.get("summary", {})
        except Exception as e:  # noqa: BLE001
            entry["state_valid"] = False
            entry["error"] = str(e)[:200]
        entry["stderr"] = err.strip()[:300]
        cases.append(entry)
        shutil.rmtree(root, ignore_errors=True)

    def bad_yaml(root):
        with open(frag_path(root, "hw.yaml"), "w", encoding="utf-8") as f:
            f.write("agent: hw-lead\nneeds_from: [ {key: 'x', to: 'sw-lead'\n")  # 半截

    def empty(root):
        open(frag_path(root, "hw.yaml"), "w").close()

    def bom(root):
        with open(frag_path(root, "hw.yaml"), "w", encoding="utf-8-sig") as f:
            yaml.safe_dump(base_frag("hw-lead", 1), f, allow_unicode=True)

    def nondict(root):
        with open(frag_path(root, "hw.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump([1, 2, 3], f)

    def dup_key(root):
        d = base_frag("hw-lead")
        d["needs_from"] = [{"key": "DUP", "to": "sw-lead", "item": "a", "since": "x"},
                           {"key": "DUP", "to": "mech-lead", "item": "b", "since": "x"}]
        write_frag(root, "hw.yaml", d)

    def wrong_type(root):
        d = base_frag("hw-lead")
        d["needs_from"] = "这应该是列表"
        d["answers"] = [{"key": 123, "to": ["a"], "value": {"x": 1}}]
        write_frag(root, "hw.yaml", d)

    def impersonate(root):
        """hw.yaml 里冒名成 mech-lead → 看会不会把 mech 的数据吞掉。"""
        d = base_frag("mech-lead", 2)
        d["status"]["summary"] = "我是冒名的 mech"
        write_frag(root, "hw.yaml", d)

    def claim_none_value(root):
        d = base_frag("hw-lead")
        d["interface_claims"] = [{"key": "K", "value": None, "note": "没有值"}]
        write_frag(root, "hw.yaml", d)

    def prose_value(root):
        d = base_frag("hw-lead")
        d["interface_claims"] = [{"key": "K", "value": "根据规范应当控制在 38 到 40 摄氏度之间才行", "note": ""}]
        write_frag(root, "hw.yaml", d)

    run_case("坏 YAML (半截)", bad_yaml, "跳过该分片, 其余正常, rc=0")
    run_case("空文件", empty, "跳过或当空, rc=0")
    run_case("UTF-8 BOM", bom, "能读最好, 读不了就跳过, rc=0")
    run_case("非 dict (list)", nondict, "跳过, rc=0")
    run_case("同分片重复 key", dup_key, "不崩, 两条都要在")
    run_case("字段类型错", wrong_type, "不崩")
    run_case("分片冒名 (hw 冒成 mech)", impersonate, "hw 的数据不该消失, mech 也不该被冒名覆盖")
    run_case("interface_claims value 为 None", claim_none_value, "不崩")
    run_case("散文 value", prose_value, "lint 提示, 不参与冲突比较")
    return cases


# ----------------------------------------------------------------- T6
def t6_same_fragment_concurrent_write() -> dict:
    root = mk_sandbox()
    for a in AGENTS:
        write_frag(root, FILE_OF[a], base_frag(a, 2))
    errs = []
    lock = threading.Lock()

    def writer(tag: str):
        for i in range(30):
            d = base_frag("hw-lead", 5)
            d["artifacts"][0]["summary"] = f"stress hw-lead #{i} WRITER={tag}"
            write_frag(root, "hw.yaml", d)
            time.sleep(0.002)

    def merger():
        for _ in range(40):
            rc, out, err = run_merge(root)
            if err.strip():
                with lock:
                    errs.append(err.strip()[:160])

    ts = [threading.Thread(target=writer, args=(t,)) for t in ("A", "B")]
    mt = threading.Thread(target=merger)
    for t in ts:
        t.start()
    mt.start()
    for t in ts:
        t.join()
    mt.join()
    try:
        st = load_state(root)
        valid = True
        n = len(st["domains"]["hw-lead"]["artifacts"])
    except Exception as e:  # noqa: BLE001
        valid = False
        n = -1
        errs.append(str(e)[:160])
    res = {"state_valid": valid, "hw_artifacts": n, "stderr_lines": len(errs),
           "stderr_examples": errs[:3]}
    shutil.rmtree(root, ignore_errors=True)
    return res


# ----------------------------------------------------------------- T7
def t7_torn_fragment_trace() -> dict:
    """分片被读到半截时, 快照里必须**留痕** (不能让读者误以为那个 agent 没交作业)。"""
    root = mk_sandbox()
    for a in AGENTS:
        write_frag(root, FILE_OF[a], base_frag(a, 2))
    with open(frag_path(root, "hw.yaml"), "w", encoding="utf-8") as f:
        f.write("agent: hw-lead\nartifacts: [ {path: 'x', kin")   # 半截
    rc, out, err = run_merge(root)
    try:
        st = load_state(root)
        valid = True
    except Exception as e:  # noqa: BLE001
        st, valid = {}, False
    inc = (st.get("meta") or {}).get("incomplete_fragments") or []
    res = {
        "rc": rc,
        "state_valid": valid,
        "hw_domain_present": "hw-lead" in (st.get("domains") or {}),
        "incomplete_fragments": len(inc),
        "incomplete_files": [i.get("file") for i in inc],
        "stderr_has_warning": "不完整" in err or "跳过" in err,
        "cli_reports_incomplete": "不完整" in out,
    }
    shutil.rmtree(root, ignore_errors=True)
    return res


# ----------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quick", action="store_true", help="缩短压测时长")
    args = ap.parse_args()

    dur = 3.0 if args.quick else 6.0
    report = {
        "T1_concurrent_merge": t1_concurrent_merge(args.rounds),
        "T2_torn_read": t2_torn_read(dur),
        "T3_reader_consistency": t3_reader_consistency(dur),
        "T4_pairing_semantics": t4_pairing_semantics(),
        "T5_abnormal_inputs": t5_abnormal_inputs(),
        "T6_same_fragment_concurrent_write": t6_same_fragment_concurrent_write(),
        "T7_torn_fragment_trace": t7_torn_fragment_trace(),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        return 0

    print("=" * 72)
    print("STATE 协议 · 并发/压力/异常输入 测试报告")
    print("=" * 72)

    t1 = report["T1_concurrent_merge"]
    print(f"\n[T1] 并发合并 ({t1['rounds']} 个 merge.py 同时跑, {t1['elapsed_s']}s)")
    print(f"     returncode={t1['returncodes']}  快照产出={t1['total_artifacts']}/{t1['expected_artifacts']}"
          f"  丢失={t1['lost']}  重复={t1['duplicates']}  .tmp残留={t1['tmp_leftovers']}")
    print(f"     domain 齐全={t1['domains_present'] == sorted(AGENTS)}")

    t2 = report["T2_torn_read"]
    print(f"\n[T2] 撕裂读 (分片非原子写 × 并发合并, {t2['duration_s']}s)")
    print(f"     合并跑 {t2['merge_runs']} 次 | 写分片 {t2['writer_iterations']} 次")
    print(f"     ⚠️ 跳过/解析失败: {t2['skips']} 次 | 🔴 整域消失/静默丢数据: {t2['loss_events']} 次"
          f" | 🕐 数据过期(域在但最新数据不在): {t2.get('stale_events', 0)} 次 | rc!=0: {t2['rc_nonzero']}")
    for e in t2["skip_examples"]:
        print(f"       跳过样例: {e}")
    for e in t2["loss_examples"]:
        print(f"       丢数据样例: {e}")

    t3 = report["T3_reader_consistency"]
    print(f"\n[T3] 读者一致性 (合并风暴中反复读, {t3['duration_s']}s)")
    print(f"     读 {t3['reads']} 次 | 无效/半截 {t3['invalid']} 次 | 缺 domain {t3['missing_domains']} 次")
    for e in t3["examples"]:
        print(f"       例: {e}")

    t4 = report["T4_pairing_semantics"]
    print(f"\n[T4] 配对语义")
    print(f"     K1 (被问方回答)      → {t4['K1_state']}   第三方代答: {t4['K1_foreign']}")
    print(f"     K2 (第三方代答)      → {t4['K2_state']}   记入 foreign: {t4['K2_foreign']}")
    print(f"     K3 (key 写错)        → {t4['K3_state']}   lint keys: {t4['lint_keys']}")

    print("\n[T5] 异常输入")
    for c in report["T5_abnormal_inputs"]:
        print(f"     - {c['case']:<28} rc={c['rc']} 快照有效={c.get('state_valid')} "
              f"domains={len(c.get('domains', []))} lint={c.get('lint')} 冲突={c.get('conflicts')}")
        if c.get("error"):
            print(f"         ❌ {c['error']}")
        if c.get("stderr"):
            print(f"         stderr: {c['stderr'][:180]}")

    t6 = report["T6_same_fragment_concurrent_write"]
    print(f"\n[T6] 同分片并发写 (两个进程同时写 hw.yaml)")
    print(f"     快照有效={t6['state_valid']}  hw artifacts={t6['hw_artifacts']}  stderr={t6['stderr_lines']}")
    for e in t6["stderr_examples"]:
        print(f"       {e}")

    t7 = report["T7_torn_fragment_trace"]
    print(f"\n[T7] 半截分片是否留痕")
    print(f"     rc={t7['rc']} 快照有效={t7['state_valid']} hw domain还在={t7['hw_domain_present']} "
          f"留痕={t7['incomplete_fragments']} {t7['incomplete_files']}")
    print(f"     stderr 有警告={t7['stderr_has_warning']}  CLI 报不完整={t7['cli_reports_incomplete']}")

    print("\n" + "=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
