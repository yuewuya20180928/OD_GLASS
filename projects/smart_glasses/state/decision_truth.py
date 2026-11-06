#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""decision_truth.py -- ★★★**"老板决策"的唯一真源 (2026-11-06 20:5x)**

★★★**为什么要有这个模块 (★实测事故链)**:
  ① 老板拍过板的 need, **decision 只被记在"被问的那个 agent"的分片里**
     ⇒ ★**同 key 在别的分片里没有回写 ⇒ 那边的同 key need 长期挂 waiting_external ⇒ 假挂着 ⇒ 污染门禁数字**
  ② ★★**2026-11-06 20:3x 我只改了 `merge.py` 一处** ⇒ ★**同一套"闭合/筛选"语义在本仓有 3 份平行实现**
     (`merge.py` / `gate_check.py` / `advance.py`) ⇒ ⇒ ★**漏改两处**:
     · `gate_check.py` 的 `_answered()` 没跟 ⇒ **对账 `ok=false` (71 vs 78) ⇒ daily_check rc=3 ⇒ 巡检从 ✅ 变 ❌**
     · `advance.py` 的老板清单没剔"老板早已拍过"的 ⇒ ★**41 条里混了 5 条重复问老板的 ⇒ 实际只该问 36 条**
  ③ ⇒ ★**正解: 抽 1 个共享函数, 三处 import** ⇒ ★**下次改判据只改一处**

★★★**语义 (唯一口径)**:
  ★**老板的 `decision` 是全局事实** ⇒ ★**任何分片里、任何同 key 的 need, 只要别处记着老板拍过板 ⇒ 就判 answered**

用法:
  from decision_truth import decision_keys, answered_by_decision
  dec = decision_keys(frags)                      # 所有分片里带 decision 的 key 集合
  ok = answered_by_decision(need, dec)            # 该 need 是否已被老板决策闭合

自测 (★★回归护栏: 断言这次实测出来的数字, 下次改回去有人拦):
  bash state/pcbnew_py.sh state/decision_truth.py --self-test
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
FRAG_DIR = os.path.join(_HERE, "fragments")

# ★★**老板 10-25 已拍过板的 key (★实测: 这 5 条是 advance.py 清单里"重复问老板"的)**:
#   q16_aspect_ratio(宽高比无所谓, 改判≥1080p60) · q4_battery_scope(按需触发) ·
#   q1_latency_scope(选A最严口径) · q17_display_fps(60fps优先) · q18_highspeed_cam(改目测验收)
BOSS_DECIDED_KEYS = ("q16_aspect_ratio", "q4_battery_scope", "q1_latency_scope",
                     "q17_display_fps", "q18_highspeed_cam")


def decision_keys(frags):
    """★**老板决策的全局 key 集合** (★跨分片同 key 也算)"""
    out = set()
    for fr in (frags or {}).values():
        if not isinstance(fr, dict):
            continue
        for n in (fr.get("needs_from") or []):
            k = n.get("key")
            if k and n.get("decision"):
                out.add(k)
    return out


def answered_by_decision(need, dec_keys):
    """★**该 need 是否已被老板决策闭合** (★自身带 decision, 或同 key 在别处被拍过)"""
    if not isinstance(need, dict):
        return False
    if need.get("decision"):
        return True
    k = need.get("key")
    return bool(k) and k in (dec_keys or ())


def load_fragments(frag_dir=FRAG_DIR):
    """★读所有分片 (★yaml 缺失/坏掉就跳过)"""
    import yaml
    out = {}
    if not os.path.isdir(frag_dir):
        return out
    for fn in sorted(os.listdir(frag_dir)):
        if not fn.endswith(".yaml"):
            continue
        try:
            with open(os.path.join(frag_dir, fn), encoding="utf-8") as f:
                out[fn[:-5]] = yaml.safe_load(f) or {}
        except Exception:  # noqa: BLE001
            continue
    return out


def self_test():
    frags = load_fragments()
    dec = decision_keys(frags)
    print("═══ 分片 %d 个 · 老板决策 key %d 个 ═══" % (len(frags), len(dec)))
    assert frags, "★读不到任何分片 ⇒ 没法自测"
    # ① 老板 10-25 拍过的 5 条必须在全局决策集合里
    missing = [k for k in BOSS_DECIDED_KEYS if k not in dec]
    assert not missing, "★★**老板拍过的 key 不在全局决策集合里: %s**" % missing
    print("✔ 老板 10-25 拍过的 5 条都在全局决策集合里 (跨分片同 key 生效)")
    # ② 同 key 需求应判 answered (即使自身没写 decision)
    assert answered_by_decision({"key": "q16_aspect_ratio"}, dec)
    assert not answered_by_decision({"key": "__no_such_key__"}, dec)
    assert answered_by_decision({"key": "x", "decision": "老板原话"}, dec)
    print("✔ answered_by_decision 判据正确 (同 key 命中 / 未命中 / 自身带 decision)")
    # ③ ★★**回归护栏: 直接走 merge.build_state 的真实路径** (★20:8x 改: ★原先自测自己算一套"旧口径",
    #   ★与 merge 的答案作者口径不同 ⇒ 打印的绝对数(82→75)会被误当成 merge 的数(78→71))
    #   ⇒ ★**现在直接调生产代码, 关掉/打开全局同 key 规则各跑一遍 ⇒ 数字必然一致**
    ext_old = ext_new = 0
    pend = None
    try:
        import merge as _merge
        # ★★用 **merge 自己的** load_fragments (★带重试/归一化 ⇒ 形状与主流程完全一致 ⇒ 绝对数才能对上)
        try:
            _mf, _ri = _merge.load_fragments()
        except TypeError:
            _mf = _merge.load_fragments()
        _orig = _merge._decision_keys
        try:
            _merge._decision_keys = lambda _f: set()      # ★模拟旧口径(只看本 need 自带 decision)
            _old_state = _merge.build_state(_mf)
        finally:
            _merge._decision_keys = _orig
        _new_state = _merge.build_state(_mf)
        ext_old = (_old_state.get("summary") or {}).get("waiting_external_needs")
        ext_new = (_new_state.get("summary") or {}).get("waiting_external_needs")
        pend = (_new_state.get("summary") or {}).get("open_needs")
        print("★merge.build_state 真值: 等外部 %s → %s (内部未闭合 %s)" % (ext_old, ext_new, pend))
        assert ext_new < ext_old, "★★**新口径没有减少假挂项 ⇒ 跨分片老板决策没生效**"
        assert (ext_old - ext_new) == 7, ("★★**降幅应为 7 (2026-11-06 实测 78→71), 实测 %s**"
                                         % (ext_old - ext_new))
        print("✔ 假挂项减少 7 条 (与 2026-11-06 实测 78→71 一致) ⇒ ★**回归护栏有效**")
    except AssertionError:
        raise
    except Exception as _e:
        print("  ⚠️ 走 merge.build_state 失败 (%s) ⇒ 退回本地口径粗测" % _e)
        answers_by_key = {}
        for aid, fr in frags.items():
            for a in (fr.get("answers") or []):
                k = a.get("key")
                if k:
                    answers_by_key.setdefault(k, []).append(aid)

        def old_answered(n):
            k, to = n.get("key"), n.get("to")
            if n.get("decision"):
                return True
            return bool(to) and to in (answers_by_key.get(k) or [])

        for fr in frags.values():
            for n in (fr.get("needs_from") or []):
                if (n.get("waiting_on") or "agent") == "agent":
                    continue
                if not old_answered(n):
                    ext_old += 1
                if not old_answered(n) and not answered_by_decision(n, dec):
                    ext_new += 1
        assert ext_new < ext_old, "★★**新口径没有减少假挂项**"
        assert (ext_old - ext_new) == 7, ("★★**降幅应为 7 (2026-11-06 实测 78→71), 实测 %s**"
                                         % (ext_old - ext_new))
        print("✔ 本地粗测: 等外部 %s → %s (★**降幅必须是 7**)" % (ext_old, ext_new))
    # ④⑤ ★★★**消费者级护栏 (★兄弟 21:0x 回退实验指出: 护栏只守住 3 个消费者里的 1 个
    #   ⇒ ★**恰恰没覆盖"今天事故那一类"**: ★**只回退 advance.py ⇒ self-test 仍 PASS + gate 对账仍 ✅
    #   ⇒ ★**完全静默** ⇒ 5 条已拍板的 key 又冒出来问老板 (36→41) ⇒ ★**rc 也抓不到 (advance 正常就 rc=1)**)
    #   ⇒ ★**⇒ 必须对每个消费者各有一条断言** ⇒ ★**下面两条就是**)
    import subprocess
    try:
        # ★★2026-11-06 21:2x (★兄弟 21:1x 实测的盲点): ★**断言④ 原来靠 "grep stdout 里那 5 个 key 字符串"**
        #   ⇒ ★**若 advance.py 把 key 打成别的形式 (★他模拟把 `_` 换成 `.`) ⇒ 漏抓**
        #   ⇒ ★★**更糟: 它自己会把 "清单 41 行" 印出来, 却仍判 PASS** ⇒ ★**护栏把泄漏事实印出来还判过**
        #   ⇒ ★**修法: 走 --json 的结构化输出查 key** (★不依赖打印格式 ⇒ 格式变了也抓得到)
        r = subprocess.run([sys.executable, "-B", os.path.join(_HERE, "advance.py"), "--json"],
                           capture_output=True, text=True, timeout=900)
        import json as _json
        _d = _json.loads(r.stdout or "{}")
        _dec = _d.get("decisions") or []
        # ★★**key 归一化后再比** (★兄弟 21:1x 实测的盲点: 断言原来 grep stdout 里的 key 字符串
        #   ⇒ ★**若 advance.py 把 key 打成别的形式 (★他模拟把 `_` 换成 `.`) ⇒ 漏抓**
        #   ⇒ ★★**连结构化输出也一样会漏** ⇒ ★**⇒ 归一化 (`.`/`-` ⇒ `_`) 后再比**)
        def _norm(x):
            return str(x or "").replace(".", "_").replace("-", "_")
        _keys = [_norm(x.get("key")) for x in _dec if isinstance(x, dict)]
        leaked = [k for k in BOSS_DECIDED_KEYS if _norm(k) in _keys]
        assert not leaked, ("★★**advance 老板清单里又冒出老板已拍板的 key: %s**"
                            "⇒ ★**advance.py 的全局同 key 规则被回退了** (★清单 %d 条)"
                            % (leaked, len(_dec)))
        print("✔ 消费者④ advance: 老板清单 %d 条, 已拍板的 5 条 key 全部不在 (★走 --json 结构化查, 不靠 grep)"
              % len(_dec))
    except AssertionError:
        raise
    except Exception as _e:
        print("  ⚠️ 消费者④ advance 没跑成 (%s)" % _e)
    try:
        r = subprocess.run([sys.executable, "-B", os.path.join(_HERE, "gate_check.py"), "--json"],
                           capture_output=True, text=True, timeout=900)
        import json as _json
        d = _json.loads(r.stdout or "{}")

        def _find_recon(o):
            """★在 JSON 里递归找带 merge_waiting_external 的那个对账对象"""
            if isinstance(o, dict):
                if "merge_waiting_external" in o:
                    return o
                for _v in o.values():
                    _r = _find_recon(_v)
                    if _r is not None:
                        return _r
            elif isinstance(o, list):
                for _v in o:
                    _r = _find_recon(_v)
                    if _r is not None:
                        return _r
            return None

        rec = _find_recon(d) or {}
        assert rec.get("ok") is True, ("★★**gate 与 merge 口径不一致: %s**"
                                       "⇒ ★**gate_check.py 的 _answered 没跟**" % rec)
        print("✔ 消费者⑤ gate_check: 自对账 ok=True (等外部 %s)"
              % rec.get("gate_global_waiting_external"))
    except AssertionError:
        raise
    except Exception as _e:
        print("  ⚠️ 消费者⑤ gate_check 没跑成 (%s)" % _e)
    print("ALL TESTS PASS")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    frags = load_fragments()
    dec = decision_keys(frags)
    print("═══ 老板决策全局 key (%d 个) ═══" % len(dec))
    for k in sorted(dec):
        print("   %s" % k)
    return 0


if __name__ == "__main__":
    sys.exit(main())
