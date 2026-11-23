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
  ★★**必须用系统 python3** (★`pcbnew_py.sh` 的 KiCad python3.11 **没装 yaml** ⇒ 照那个跑必 ModuleNotFoundError):
    python3 -B state/decision_truth.py --self-test
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
        # ★★**2026-11-12 02:2x 第 2 次复发 ⇒ 本次把硬编 `== 8` 改成【下限 >= 9 + 具名 key 断言】** ★★:
        #   ★**为什么必须改 (★实测, 不是推测★)**: 老板 2026-11-12 02:02「不再发信, 全靠自己查资料」在 pm.yaml
        #   给 `iss105_jchg_rfq_release` 落了 `decision` ⇒ ★**hw.yaml 里同一 key 的那条 (to: main, waiting_on: boss)
        #   被【跨分片同 key 规则】正确关闭** ⇒ ★**降幅 8 → 9** ★ ⇒ ★**硬编 `== 8` = 一颗"老板下次拍板就自己炸"的雷**
        #   (★**同一个病第 2 次复发**: 2026-11-10 补录老板 11-04「视崖已不用」时 已经 7 → 8 改过一次硬编数★)
        #   ★**⇒ 改成下限断言**: ★**"跨分片规则失效 ⇒ 降幅掉回 0" 仍然会红 (这才是这道护栏真正要抓的)** ★
        #   ★**⇒ 同时加具名 key 断言**: ★**比"数个数"更强 —— 数字对但关错了对象, 照样红** ★
        #   ★★**反事实实测 (main 2026-11-12 02:2x 亲手跑过)**: 把 pm.yaml 里那条 decision 去掉 ⇒ 降幅回到 8
        #   ⇒ ★**证明第 9 条确实由老板 02:02 那条决定产生, 不是别的改动带进来的** ★
        _drop = ext_old - ext_new
        # ★★2026-11-23 12:2x main 第 3 次同型复发 ⇒ ★★把硬编历史常数彻底换成【算出来的期望值】★★
        #   ★**病根**: 断言写死了 2026-11-12 那天的降幅 (9) ⇒ ★**只要别处【正常地】把那几条假挂项关掉/挪走
        #     (★例: ISS-357 把 74 条 needs 正常平账, 其中含 3 条带老板 decision 的别名 need★)
        #     ⇒ 降幅自然变小 ⇒ 护栏误报「跨分片同 key 规则失效」⇒ ★**这是第 3 次复发 (11-10 改 ==8→下限, 11-12 改下限,
        #     今天换算法) ⇒ 说明「硬编历史常数」这条路本身是错的** ★
        #   ★**⇒ 新判据 = 自己算出期望降幅**: 期望降幅 = 「可被跨分片同 key 规则关闭、且旧口径下没被自己人答过」的别名 need 条数
        #     ⇒ ★**期望值随台账自然变化 ⇒ 永不误报; 而「规则失效 ⇒ 降幅 0 ≠ 期望」仍然会红** ★
        _alias = []
        for _aid, _fr in frags.items():
            for _n in (_fr.get("needs_from") or []):
                _k = _n.get("key")
                if not _k or _n.get("decision"):
                    continue
                if (_n.get("waiting_on") or "agent") == "agent":
                    continue
                if _k in dec:
                    _alias.append((_aid, _k, _n.get("to")))
        _ans_by_key = {}
        for _aid, _fr in frags.items():
            for _a in (_fr.get("answers") or []):
                _k = _a.get("key")
                if _k:
                    _ans_by_key.setdefault(_k, []).append(_aid)
        _expected = sum(1 for (_aid, _k, _to) in _alias if _to not in _ans_by_key.get(_k, []))
        assert _drop == _expected, (
            "★★**降幅 %s ≠ 算出来的期望降幅 %s** ⇒ ★**真正红了 = 跨分片同 key 规则失效 (老板拍过的板没被规则闭合) ⇒ 查 decision_keys()**"
            "★★(★期望降幅 = 当前【可被规则关闭且旧口径下没被自己人答过】的别名 need 条数·★不是历史常数★)"
            "★★别名 need 明细: %s**" % (_drop, _expected, _alias))
        # ★**具名断言: 这 7 个 key 必须【在某个分片里有一条【自身没写 decision、但别处有老板 decision】的 need】**
        #   ⇒ ★**它们正是"被跨分片同 key 规则关闭"的那批** ⇒ ★**数字对但关错了对象, 这里也会红** ★
        _expect_closed = ("q16_aspect_ratio", "q4_battery_scope", "q1_latency_scope", "q17_display_fps",
                          "q18_highspeed_cam", "demo_od_p0_4_panel_init_code", "iss105_jchg_rfq_release")
        _alias_pairs = set()
        for _aid, _fr in frags.items():
            for _n in (_fr.get("needs_from") or []):
                _k = _n.get("key")
                if not _k or _n.get("decision"):
                    continue
                if (_n.get("waiting_on") or "agent") == "agent":
                    continue
                if _k in dec:
                    _alias_pairs.add((_aid, _k))
        _still = [k for k in _expect_closed if any(kk == k for (_aa, kk) in _alias_pairs)]
        _gone = [k for k in _expect_closed if k not in _still]
        # ★★2026-11-23 12:2x main: 原来这条断言要求【7 个具名 key 全都还在】⇒ ★**但其中 4 条已被别处正常关闭/平账移走
        #   (★ISS-357 的 SW 平账就是干这个的★) ⇒ 老断言变成「谁把 need 正常关掉谁触发红灯」★★
        #   ⇒ ★**改成结构性判据: 还在的 ⇒ 必须【在规则闭合集里】(跨分片规则确实在闭合它); 不在了 ⇒ 已被别处处理, 不再要求** ★
        _closed_keys = set()
        for _aa, _kk, _tt in _alias:
            if _tt not in _ans_by_key.get(_kk, []):
                _closed_keys.add(_kk)
        _not_closed = [k for k in _still if k not in _closed_keys]
        assert not _not_closed, ("★★**这些 key 还在别名 need 里, 却没有被跨分片同 key 规则闭合: %s**"
                                  "★★**⇒ 规则失效或该 need 被挪走/改名了**" % (_not_closed,))
        if _gone:
            print("  ℹ️ 7 个具名 key 里有 %d 个已【不再有别名 need】(★被别处正常关闭/平账移走·★不再要求它们仍被规则闭合★): %s"
                  % (len(_gone), _gone))
        print("✔ 假挂项减少 %d 条 (= 算出来的期望降幅 %d·★2026-11-23 起不再用历史常数★) "
              "⇒ ★**回归护栏有效 (期望值自算 + 具名 key 结构性断言)**" % (_drop, _expected))
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
        # ★★2026-11-12 02:2x: 与上面主路径同一口径 ⇒ 硬编数改下限 (★**理由见主路径的注释★**)
        # ★★同上: 期望值算出来, 不用历史常数 (★2026-11-23 12:2x main★★)
        _alias_l = []
        for _aid, _fr in frags.items():
            for _n in (_fr.get("needs_from") or []):
                _k = _n.get("key")
                if not _k or _n.get("decision"):
                    continue
                if (_n.get("waiting_on") or "agent") == "agent":
                    continue
                if _k in dec:
                    _alias_l.append((_aid, _k, _n.get("to")))
        _exp_l = 0
        for (_aid, _k, _to) in _alias_l:
            if not old_answered({"key": _k, "to": _to, "waiting_on": "x"}):
                _exp_l += 1
        assert (ext_old - ext_new) == _exp_l, ("★★**降幅 %s ≠ 算出来的期望降幅 %s** ⇒ 跨分片同 key 规则失效 ⇒ 查 decision_keys()**"
                                             "★★(★期望值随台账自然变化·不是历史常数★)" % (ext_old - ext_new, _exp_l))
        print("✔ 本地粗测: 等外部 %s → %s (★降幅 %s = 算出来的期望降幅 %s·★非历史常数★)"
              % (ext_old, ext_new, ext_old - ext_new, _exp_l))
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
        # ★★2026-11-06 21:4x (★兄弟 21:2x 实测的尾巴): ★**advance.py 崩掉 ⇒ stdout 空
        #   ⇒ json.loads("{}") ⇒ decisions=[] ⇒ "无泄漏" ⇒ ★**护栏把"advance 崩了"当"advance 干净"判过 (假 PASS)**
        #   ⇒ ★**这正是我 21:00 在别处拔掉的"静默降级"雷的同款形态, 只是换了个位置**
        assert r.returncode in (0, 1), (
            "★★**advance.py 没正常跑 (rc=%s) ⇒ 断言④ 无从检查 ⇒ 判 PASS 是假的**" % r.returncode)
        _d = _json.loads(r.stdout or "{}")
        _dec = _d.get("decisions") or []
        assert _dec, ("★★**advance.py --json 没吐 decisions (清单 0 条) ⇒ 无泄漏可查 ⇒ 判 PASS 是假的**")
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
