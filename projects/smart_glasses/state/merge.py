#!/usr/bin/env python3
"""
STATE 合并器 — 共享状态源 (老板 2026-10-25 指示)

读 state/fragments/*.yaml  →  原子写 ../STATE.yaml

设计要点:
  * 纯函数, 无锁, 任何 agent 任何时候都能跑
  * 原子写 (tmp + os.replace) → 读者永远看到完整快照
  * needs_from × answers 按 key 配对 → 自动标 answered/pending
  * interface_claims 同 key 不同 value → 自动检出 conflict
  * --for <agentId> 输出"我被点名了什么 / 我欠谁什么 / 当前冲突"

用法:
    python3 state/merge.py                # 刷新 STATE.yaml
    python3 state/merge.py --for hw-lead  # 我的切片
    python3 state/merge.py --json         # 机器可读
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone, timedelta

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
FRAG_DIR = os.path.join(HERE, "fragments")
# 上次成功解析的分片副本 —— 分片读失败时回退, 免得整域凭空消失 / 已闭合需求翻回 pending
LASTGOOD_DIR = os.path.join(HERE, ".lastgood")
STATE_PATH = os.path.join(PROJ, "STATE.yaml")
TZ = timezone(timedelta(hours=8))

AGENT_ORDER = ["main", "hw-lead", "sw-lead", "mech-lead"]
AGENT_NAMES = {
    "main": "项目总工",
    "hw-lead": "硬件总工",
    "sw-lead": "软件总工",
    "mech-lead": "结构总工(带散热)",
}
SEV_RANK = {"high": 0, "medium": 1, "low": 2}


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


LIST_FIELDS = ("artifacts", "blockers", "needs_from", "answers", "interface_claims",
               "open_questions", "risks")
ENTRY_FIELDS = {"needs_from": ("key",), "answers": ("key",), "interface_claims": ("key",),
                "artifacts": (), "blockers": (), "open_questions": (), "risks": ()}


def normalize_frag(data: dict, fn: str, issues: list) -> dict:
    """字段类型校验 + 归一化 —— 一个分片写错类型不能拖垮整个状态源。"""
    for key in LIST_FIELDS:
        v = data.get(key)
        if v is None:
            data[key] = []
        elif not isinstance(v, list):
            issues.append({"file": fn, "kind": "type", "field": key,
                           "hint": f"{key} 应该是列表, 实际是 {type(v).__name__} → 已忽略该字段"})
            data[key] = []
        else:
            good = []
            for it in v:
                if not isinstance(it, dict):
                    issues.append({"file": fn, "kind": "type", "field": key,
                                   "hint": f"{key} 里有非字典条目 ({type(it).__name__}) → 已忽略"})
                    continue
                missing = [f for f in ENTRY_FIELDS.get(key, ()) if not it.get(f)]
                if missing:
                    issues.append({"file": fn, "kind": "schema", "field": key,
                                   "hint": f"{key} 条目缺字段 {missing} → 已忽略"})
                    continue
                good.append(it)
            data[key] = good
    return data


def load_fragments() -> tuple:
    """读全部分片。返回 (frags, read_issues)。

    ⚠️ 2026-10-25 压测修复:
      旧版一次读, 解析失败就跳过 → **并发写分片时该 agent 整份数据从快照里消失,
      且快照无任何标记 (静默丢数据)**。
      修法: ① 解析失败**重试** (对方可能正在写, 等 80ms 再读)
            ② 重试仍失败 → 跳过但**在快照里留痕** (meta.incomplete_fragments)
            ③ 字段类型错 → 归一化 + 记 lint, 不再让整个合并崩掉
            ④ 两个分片声明同一个 agent id → 记 lint (静默覆盖)
    """
    frags = {}
    read_issues = []
    if not os.path.isdir(FRAG_DIR):
        return frags, read_issues
    for fn in sorted(os.listdir(FRAG_DIR)):
        if not fn.endswith((".yaml", ".yml")):
            continue
        path = os.path.join(FRAG_DIR, fn)
        data = None
        last_err = None
        for attempt in range(5):
            try:
                # 读之前后各 stat 一次: 文件在读的过程中被改过 → 说明对方正在写
                # → 这次读到的是"合法但残缺"的半截快照, 必须重读
                st_before = os.stat(path)
                if st_before.st_size == 0:
                    last_err = RuntimeError("分片是 0 字节 (对方正在写)")
                    time.sleep(0.08)
                    continue
                with open(path, "rb") as f:
                    raw = f.read().decode("utf-8", errors="replace")
                st_after = os.stat(path)
                changed = (st_before.st_size != st_after.st_size
                           or st_before.st_mtime_ns != st_after.st_mtime_ns)
                data = yaml.safe_load(raw)
                last_err = None
                if not changed:
                    break
                # 变了 → 丢掉这一次的解析结果, 等对方写完再读
                last_err = RuntimeError("分片在读取过程中被修改 (对方正在写)")
            except Exception as e:  # noqa: BLE001
                last_err = e
                time.sleep(0.08)      # 对方可能正在写 → 等一下重读
        if last_err is not None:
            # 回退到上次成功解析的副本 (宁可给旧数据, 也不给"这个 agent 不存在")
            lg = os.path.join(LASTGOOD_DIR, fn)
            stale = False
            if os.path.exists(lg):
                try:
                    with open(lg, "r", encoding="utf-8") as f:
                        alt = yaml.safe_load(f)
                    if isinstance(alt, dict):
                        data = alt
                        stale = True
                        last_err = None
                except Exception:  # noqa: BLE001
                    pass
            if last_err is not None:
                read_issues.append({"file": fn, "kind": "parse",
                                     "error": str(last_err)[:300],
                                     "hint": "分片读失败 (可能正被并发写) 且无上次快照 → 该 agent 本次缺席, 重跑合并即可恢复"})
                print(f"[merge] ⚠️ 跳过 {fn}: 解析失败 {last_err}", file=sys.stderr)
                continue
            read_issues.append({"file": fn, "kind": "stale",
                                 "hint": "分片读失败 → 本次用上次成功解析的快照 (数据可能过期, 修好分片写会自动恢复)"})
            print(f"[merge] ⚠️ {fn} 读失败, 回退到上次成功快照 (数据可能过期)", file=sys.stderr)
        if not isinstance(data, dict):
            read_issues.append({"file": fn, "kind": "type",
                                 "hint": f"分片顶层不是 dict ({type(data).__name__}) → 已忽略"})
            continue
        data = normalize_frag(data, fn, read_issues)
        try:
            os.makedirs(LASTGOOD_DIR, exist_ok=True)
            _lg = os.path.join(LASTGOOD_DIR, fn)
            _fd, _tmp = tempfile.mkstemp(prefix=fn + ".", suffix=".tmp", dir=LASTGOOD_DIR)
            with os.fdopen(_fd, "w", encoding="utf-8") as _f:
                yaml.safe_dump(data, _f, allow_unicode=True, sort_keys=False)
            os.replace(_tmp, _lg)
        except Exception:  # noqa: BLE001
            pass
        aid = data.get("agent") or os.path.splitext(fn)[0]
        stem = os.path.splitext(fn)[0]
        if data.get("agent") and str(data["agent"]) != stem:
            # 只记一条 info (文件名和 agent id 允许是别名关系, 如 pm.yaml/main);
            # **不改 id** —— 冒名靠下面的"两个分片声明同一个 id"检测兜住
            read_issues.append({"file": fn, "kind": "identity", "severity": "info",
                                 "hint": f"分片内 agent={data['agent']} 与文件名 {stem} 不一致 (允许别名, 仅记录)"})
        data["_file"] = fn
        if aid in frags:
            read_issues.append({"file": fn, "kind": "duplicate_id",
                                 "hint": f"两个分片都声明 agent={aid} → 后者 ({fn}) 覆盖前者 ({frags[aid].get('_file')}), 前者数据本次缺席"})
            print(f"[merge] ⚠️ agent id 重复: {fn} 覆盖 {frags[aid].get('_file')} (agent={aid})", file=sys.stderr)
            continue
        frags[aid] = data
    return frags, read_issues


def atomic_write(path: str, text: str) -> None:
    """原子写: **唯一 tmp 文件名** + os.replace。

    ⚠️ 2026-10-25 压测修复: 旧版用固定名 `path + ".tmp"` →
    两个 merge.py 进程并发写同一个 tmp → 互相覆盖 → 一方 os.replace
    找不到文件 → rc=1 崩溃; 极端情况两份内容交错 → 快照写坏。
    修法: tmp 名带 PID + 随机数, 且失败只删自己那一个 tmp。
    """
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def canon_of(v) -> str:
    """把 interface_claims 的值规范化, 用于机器比较。

    规则: 去掉圆括号内的注释、去掉中英文标点空白、lower、去掉单位后缀差异。
    目的: 避免 "50x12mm" vs "50x12mm (待确认)" 这种**假冲突**。
    """
    if v is None:
        return ""
    s = str(v)
    s = re.sub(r"[（(][^）)]*[）)]", " ", s)   # 去括号注释
    s = re.sub(r"[\s,，;；、/|]+", "", s)          # 去空白与分隔符
    s = s.lower()
    s = s.replace("×", "x").replace("＊", "*")
    return s


PROSE_MARKERS = ("。", "！", "？", "；", "建议", "根据", "如果", "需要", "现按", "应该")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
# 中文占比阈值: 规范值以 ASCII (数字/字母/符号) 为主, 散文以中文为主
# 实测: 合法规范值 CJK 占比 0.00~0.27; 真散文 0.41~1.00 → 0.35 是干净的分割线
CJK_RATIO_PROSE = 0.35


def is_prose(v) -> bool:
    """判断一个 claim 的 value 是不是散文 (而非短规范值)。

    ⚠️ 2026-10-25 修正史:
      v1 用"含 >=3 个中文字"判 → **误伤大量合法规范值**
         ("无桥接340-575mAh/有桥接575-675mAh"、"口径A:55.7/...ms" 全被误报)
      v2 用"长度>40 或 含句读词"判 → 短中文散文漏判
      v3 (现在) = 长度超限 OR 含中文句读/散文词 OR **中文占比 > 0.35**
    宁可漏判 (最多报个 conflict 让人看见并修), 也不可误判 (会漏掉真冲突)。
    """
    if v is None:
        return False
    s = str(v)
    if not s:
        return False
    if len(s) > 40:
        return True
    if any(m in s for m in PROSE_MARKERS):
        return True
    cjk = len(CJK_RE.findall(s))
    return (cjk / len(s)) > CJK_RATIO_PROSE


def build_state(frags: dict) -> dict:
    # ---------- 1. needs_from × answers 配对 ----------
    answers_by_key = {}
    for aid, fr in frags.items():
        for a in fr.get("answers") or []:
            k = a.get("key")
            if not k:
                continue
            answers_by_key.setdefault(k, []).append({**a, "_by": aid})

    domains = {}
    all_needs = []
    # 所有被声明过的 needs_from key (用于校验 answers 的 key 有没有被引用)
    referenced_keys = set()
    for _aid, _fr in frags.items():
        for _n in _fr.get("needs_from") or []:
            if _n.get("key"):
                referenced_keys.add(_n["key"])
    for aid in AGENT_ORDER + [a for a in frags if a not in AGENT_ORDER]:
        fr = frags.get(aid)
        if not fr:
            continue
        st = fr.get("status") or {}
        needs = []
        for n in fr.get("needs_from") or []:
            k = n.get("key")
            ask_to = n.get("to")
            # ⚠️ 只有**被问的那个 agent** 的回答才能闭合这个需求
            ans = [a for a in answers_by_key.get(k, []) if a["_by"] == ask_to]
            # ★ 老板 (人) 的决策: 不走 agent 间的 needs/answers 配对, 由项目总工代录
            #   需求上带 `decision` 字段 = 老板已拍板 (原话) → 直接判 answered
            if not ans and n.get("decision"):
                ans = [{"value": n.get("decision"), "_by": ask_to or "boss",
                        "ref": f"老板决策 {n.get('decided_at') or ''} (项目总工代录)"}]
            # 目标 agent 缺席 (分片没读到) → 标出来, 别让需求"凭空蒸发"
            # 只对"确实是 agent 的目标"判缺席 —— to: boss/vendor/jbd 是外部对象, 不算
            target_missing = bool(ask_to) and ask_to in AGENT_ORDER and ask_to not in frags
            # waiting_on: agent(等另一个总工) | boss | vendor | jbd (等外部)
            waiting_on = n.get("waiting_on") or "agent"
            due = n.get("due")
            overdue = False
            if due and not ans:
                try:
                    overdue = datetime.fromisoformat(str(due)).date() < datetime.now(TZ).date()
                except Exception:  # noqa: BLE001
                    overdue = False
            needs.append({
                "key": k,
                "to": ask_to,
                "item": n.get("item"),
                "since": n.get("since"),
                "state": "answered" if ans else ("waiting_external" if waiting_on != "agent" else "pending"),
                # 目标 agent 的分片没读到 → 单独标出来 (别让需求"凭空蒸发"时没人知道)
                "target_missing": target_missing,
                "waiting_on": waiting_on,
                "due": due,
                "overdue": overdue,
                "decision": n.get("decision"),
                "decided_at": n.get("decided_at"),
                "answers": [
                    {"by": a["_by"], "value": a.get("value"), "ref": a.get("ref")}
                    for a in ans
                ],
                "foreign_answers": [
                    {"by": a["_by"], "value": a.get("value")}
                    for a in answers_by_key.get(k, []) if a["_by"] != ask_to
                ],
            })
            all_needs.append({**n, "_by": aid, "state": "answered" if ans else ("waiting_external" if n.get("waiting_on", "agent") != "agent" else "pending")})

        blockers = fr.get("blockers") or []
        domains[aid] = {
            "agent": aid,
            "role": fr.get("role") or AGENT_NAMES.get(aid, aid),
            "updated_at": fr.get("updated_at"),
            "updated_by": fr.get("updated_by", aid),
            "status": {
                "phase": st.get("phase"),
                "progress_pct": st.get("progress_pct"),
                "health": st.get("health"),
                "summary": st.get("summary"),
            },
            "artifacts": fr.get("artifacts") or [],
            "blockers": sorted(blockers, key=lambda b: SEV_RANK.get(b.get("severity"), 9)),
            "needs_from": needs,
            "answers": fr.get("answers") or [],
            "open_questions": fr.get("open_questions") or [],
            "risks": fr.get("risks") or [],
        }

    # ---------- 2. interface_claims 冲突检测 ----------
    claims = {}
    lint = []
    needs_norm = []
    # answers 的 key 必须有对应的 needs_from, 否则说明 key 写错了 → 静默不闭合的风险
    for _aid, _fr in frags.items():
        for _a in _fr.get("answers") or []:
            _k = _a.get("key")
            if _k and _k not in referenced_keys:
                lint.append({
                    "agent": _aid, "key": _k, "value": _a.get("value"),
                    "hint": "这个 answers.key 没有任何 needs_from 引用它 → 需求不会闭合, 多半是 key 写错了",
                })
    for aid, fr in frags.items():
        for c in fr.get("interface_claims") or []:
            k = c.get("key")
            if not k:
                continue
            prose = is_prose(c.get("value"))
            if prose:
                lint.append({
                    "agent": aid, "key": k, "value": c.get("value"),
                    "hint": "value 必须是短规范值 (用于机器比较), 说明请写到 note",
                })
            claims.setdefault(k, {})[aid] = {
                "value": c.get("value"),
                "note": c.get("note"),
                "ref": c.get("ref"),
                "canon": c.get("canon") or canon_of(c.get("value")),
                "noncanonical": prose,
            }
    interface_claims = {}
    conflicts = []
    for k, by_agent in claims.items():
        vals = {a: v.get("value") for a, v in by_agent.items()}
        canons = {a: v.get("canon") for a, v in by_agent.items()}
        # 只用**规范值**参与比较; 散文值不参与 (否则假冲突)
        comparable = {a: c for a, c in canons.items() if not by_agent[a].get("noncanonical")}
        uniq = set(comparable.values())
        raw_uniq = set(canons.values())      # 含散文侧的原始规范串
        is_conflict = len(uniq) > 1
        entry = {
            "values": vals,
            "notes": {a: v.get("note") for a, v in by_agent.items()},
            "by": sorted(by_agent.keys()),
            "noncanonical_by": [a for a, v in by_agent.items() if v.get("noncanonical")],
            "conflict": is_conflict,
        }
        interface_claims[k] = entry
        if is_conflict:
            conflicts.append({
                "key": k,
                "values": {a: vals[a] for a in comparable},
                "canon_values": comparable,
                "refs": {a: by_agent[a].get("ref") for a in comparable},
                "status": "open",
            })
        elif len(raw_uniq) > 1:
            # 两边值不同, 但有一边是散文 → 不能直接判冲突, 提示规范化
            needs_norm.append({
                "key": k,
                "values": vals,
                "canon_values": canons,
                "hint": "有一方写成散文, 没法机器比较; 请统一成短规范值后重新比较",
            })

    # ---------- 3. 风险汇总 ----------
    all_risks = []
    for aid, d in domains.items():
        for r in d.get("risks") or []:
            all_risks.append({**r, "owner": aid})
    all_risks.sort(key=lambda r: SEV_RANK.get(r.get("severity"), 9))

    # ---------- 4. 全局汇总 ----------
    art_count = sum(len(d.get("artifacts") or []) for d in domains.values())
    blockers = [
        {**b, "owner": aid}
        for aid, d in domains.items()
        for b in (d.get("blockers") or [])
    ]
    blockers.sort(key=lambda b: SEV_RANK.get(b.get("severity"), 9))
    pending = [n for n in all_needs if n.get("state") == "pending"]
    waiting_ext = [n for n in all_needs if n.get("state") == "waiting_external"]
    overdue = [n for n in all_needs if n.get("overdue")]
    # 健康度: 有 high 阻塞或冲突 → red; 有 medium → yellow
    if any(b.get("severity") == "high" for b in blockers) or conflicts:
        health = "red"
    elif any(b.get("severity") == "medium" for b in blockers):
        health = "yellow"
    else:
        health = "green"

    import hashlib
    frag_fp = {}
    for aid, fr in frags.items():
        fp = os.path.join(FRAG_DIR, fr.get("_file", ""))
        try:
            b = open(fp, "rb").read()
            frag_fp[aid] = {"file": fr.get("_file"), "size": len(b),
                            "sha1": hashlib.sha1(b).hexdigest()[:12],
                            "mtime_ns": os.stat(fp).st_mtime_ns}
        except OSError:
            pass

    state = {
        "meta": {
            "version": 1,
            "generated_at": now_iso(),
            "generator": "state/merge.py",
            "source_of_truth": "PROJECT_TRACKER.md",
            "note": (
                "STATE.yaml 是机器可读的状态快照, 由 state/merge.py 从 state/fragments/*.yaml 合并生成, "
                "**不要手改** (会被下次合并覆盖)。决策理由 / 证据链 / 锁死变量在 PROJECT_TRACKER.md; "
                "本文件每项都带 ref 指过去。"
            ),
            "write_rule": "每个总工只写 state/fragments/<自己的id>.yaml; STATE.yaml 由合并器唯一写",
            "fragments": frag_fp,
        },
        "project": {
            "name": "ARS45 智能眼镜",
            "phase": (domains.get("main") or {}).get("status", {}).get("phase"),
            "health": health,
            "tracked_by": "main",
            "locked_variables_ref": "PROJECT_TRACKER.md#0 已锁死的变量",
        },
        "domains": domains,
        "interface_claims": interface_claims,
        "needs_matrix": {
            "pending": pending,
            "answered_count": len(all_needs) - len(pending),
            "total": len(all_needs),
        },
        "blockers": blockers,
        "conflicts": conflicts,
        "needs_normalization": needs_norm,
        "lint": lint,
        "risks": all_risks,
        "summary": { "health": health,
            
            "artifacts": art_count,
            "blockers": len(blockers),
            "high_blockers": sum(1 for b in blockers if b.get("severity") == "high"),
            "open_needs": len(pending),
            "waiting_external_needs": len(waiting_ext),
            "overdue_needs": len(overdue),
            "target_missing_needs": sum(1 for d in domains.values() for x in d.get("needs_from", []) if x.get("target_missing")),
            "conflicts": len(conflicts),
            "needs_normalization": len(needs_norm),
            "lint": len(lint),
            "agents_reporting": len(domains),
        },
    }
    return state


def digest_for(state: dict, agent: str) -> str:
    d = state["domains"].get(agent)
    L = []
    L.append(f"═══ STATE 切片 · {agent} ({d['role'] if d else '?'}) ═══")
    inc = state.get("meta", {}).get("incomplete_fragments") or []
    if inc:
        L.append(f"⚠️ 本次快照不完整: {len(inc)} 个分片有问题 (别当全量真相) → " +
                 ", ".join(f"{i.get('file')}:{i.get('kind')}" for i in inc))
    if not d:
        L.append("⚠️ 你还没有分片, 去写 state/fragments/%s.yaml" % agent)
        return "\n".join(L)
    st = d["status"]
    L.append(f"状态: {st.get('summary') or '-'}  | phase={st.get('phase')} progress={st.get('progress_pct')}% health={st.get('health')}")
    L.append(f"更新: {d.get('updated_at')} by {d.get('updated_by')}")

    waiting_me = []
    for aid, dd in state["domains"].items():
        for n in dd.get("needs_from") or []:
            if n.get("to") == agent and n.get("state") == "pending":
                waiting_me.append((aid, n))
    L.append("")
    L.append(f"【别人在等我】{len(waiting_me)} 项")
    for aid, n in waiting_me:
        L.append(f"  ← {aid}: {n.get('item')}   (key={n.get('key')}, since {n.get('since')})")

    L.append("")
    L.append("【我欠别人的】")
    mine = [n for n in d.get("needs_from") or [] if n.get("state") == "pending"]
    if not mine:
        L.append("  (无)")
    for n in mine:
        L.append(f"  → {n.get('to')}: {n.get('item')}  (key={n.get('key')})")

    L.append("")
    L.append(f"【全局冲突】{len(state['conflicts'])} 项")
    if not state["conflicts"]:
        L.append("  (无)")
    for c in state["conflicts"]:
        L.append(f"  ⚠️ {c['key']}: {c['values']}")

    if state.get("needs_normalization"):
        L.append("")
        L.append(f"【待规范化】{len(state['needs_normalization'])} 项 (值不同但有一方是散文, 未判冲突)")
        for c in state["needs_normalization"]:
            L.append(f"  ✏️ {c['key']}: {c['values']}  → {c['hint']}")

    if state.get("lint"):
        L.append("")
        L.append(f"【规范值 lint】{len(state['lint'])} 项 (value 写成了散文, 没法机器比较)")
        for l in state["lint"]:
            L.append(f"  ✏️ [{l['agent']}] {l['key']}: {l['value']}  → {l['hint']}")

    hb = [b for b in state["blockers"] if b.get("severity") == "high"]
    L.append("")
    L.append(f"【高危阻塞】{len(hb)} 项")
    for b in hb:
        L.append(f"  🔴 [{b.get('owner')}] {b.get('desc')}")

    L.append("")
    L.append(f"【项目健康度】{state['project']['health']}  | 产出 {state['summary']['artifacts']} | "
             f"未闭合需求 {state['summary']['open_needs']} | 冲突 {state['summary']['conflicts']}")
    L.append(f"下次刷新: python3 state/merge.py  (纯函数, 随时可跑)")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--for", dest="agent", help="输出某个 agent 的切片")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    # 并发 merge 串行化 (fcntl.flock): 旧版两个进程同抢固定名 STATE.yaml.tmp →
    # 一方 os.replace 找不到文件 → rc=1 崩溃, 且 STATE.yaml 不刷新 (全员读过期快照)
    lock_path = os.path.join(HERE, ".merge.lock")
    lock_fh = None
    try:
        import fcntl
        lock_fh = open(lock_path, "w")
        fcntl.flock(lock_fh, fcntl.LOCK_EX)
    except Exception:  # noqa: BLE001
        lock_fh = None

    frags, read_issues = load_fragments()
    if not frags:
        print("[merge] ⚠️ 没有找到任何分片", file=sys.stderr)
    state = build_state(frags)
    _warn = [i for i in read_issues if i.get("severity") != "info"]
    state["summary"]["incomplete_fragments"] = len(_warn)
    state["meta"]["incomplete_fragments"] = [i for i in read_issues if i.get("severity") != "info"]
    if _warn:
        print(f"[merge] ⚠️ 本次快照不完整: {len(_warn)} 个分片有问题 "
              f"(见 STATE.yaml meta.incomplete_fragments) → 读者别把它当全量真相", file=sys.stderr)

    if args.json:
        print(json.dumps(state, ensure_ascii=False, indent=2, default=str))
        if lock_fh:
            lock_fh.close()
        if state.get("meta", {}).get("incomplete_fragments"):
            return 2
        return 0

    header = yaml.safe_dump(
        {"__merged_at__": state["meta"]["generated_at"], "note": "完整内容见下方 auto-generated 段"},
        allow_unicode=True,
    )
    body = yaml.safe_dump(state, allow_unicode=True, sort_keys=False, width=100)
    atomic_write(STATE_PATH, body)

    if args.agent:
        print(digest_for(state, args.agent))
    else:
        s = state["summary"]
        print(f"✅ STATE.yaml 已刷新 ({state['meta']['generated_at']})")
        print(f"   产出 {s['artifacts']} | 阻塞 {s['blockers']} (高危 {s['high_blockers']}) | "
              f"未闭合需求 {s['open_needs']} | 冲突 {s['conflicts']} | 健康度 {state['project']['health']}")
        if state["conflicts"]:
            for c in state["conflicts"]:
                print(f"   ⚠️ 冲突 {c['key']}: {c['values']}")
        if state.get("meta", {}).get("incomplete_fragments"):
            print(f"   ⚠️ 快照不完整: {len(state['meta']['incomplete_fragments'])} 个分片有问题 "
                  f"→ 读者别把它当全量真相")
    if lock_fh:
        lock_fh.close()
    if state.get("meta", {}).get("incomplete_fragments"):
        return 2      # 2 = 刷新了但快照不完整 (0=完整, 1=崩了, 2=残缺)
    return 0


if __name__ == "__main__":
    sys.exit(main())
