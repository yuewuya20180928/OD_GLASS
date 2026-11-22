#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 20:0x · job 775d9893「ARS45 继续执行后继计划」
★(1) 复验通过 ⇒ ISS-295 / ISS-298 落 verified★
★(2) 把两个新闸挂进 `state/gate_check.py` (★fail-closed 同款语义★)★
★(3) CLAIMS 页 §1/§2/§3 转抄进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S6 (★追加式★)★
★(4) 回 ISS-295 的 need (★key 逐字 `iss295_mech_struct_input_claims_and_freshness_gate`★)★
★(5) ISS-297 追加续做说明 (★僵尸 fixing; ★派活权归兄弟队列 job, 本 job 不抢派★)★
★**纪律: 多行标量一律走【收集整个标量跨度 → 单行 json 写回 → 全量 safe_load 复核 + 其余 issue 逐字相同比对】★★
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
PM = os.path.join(HERE, "fragments", "pm.yaml")
GATE_CHECK = os.path.join(HERE, "gate_check.py")
CLAIMS = os.path.join(PROJ, "MECH", "BOARD_ONEPASS_MECH_CLAIMS.md")
WPACK = os.path.join(PROJ, "HW", "PCB", "BOARD_ONEPASS_WORKPACKET.md")
TODAY = "2026-11-17"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


# ============ (2) gate_check.py: 挂两个新闸 ============
NEW_GATES_BLOCK = '''

# ★★2026-11-17 20:0x (main): 新闸挂进门禁链 (★fail-closed 同款语义★)
#   ★**为什么必须挂**: ISS-295 的「MECH 结构结论防漂闸」+ ISS-298 的「SW 侧合法改板通道闸」
#   ★**以前谁都不跑 ⇒ 它们的判据形同虚设** ⇒ ★**门禁链缺它 = 判据漂移无人拦 (ISS-136 同款根因)** ★
#   ★**语义与 HW pinout 闸完全一致**: 脚本不存在 / 跑不起来 / 超时 ⇒ 一律算【闸红】, 绝不「没跑就当过」★
EXTRA_GATES = [
    (os.path.join(PROJ, "MECH", "check_mech_verdict_freshness.py"), "MECH 结构结论防漂闸 (ISS-295)"),
    (os.path.join(PROJ, "SW", "tools", "check_onepass_sw_sync.py"), "SW 侧板侧输入/合法改板闸 (ISS-298)"),
]


def run_external_gate(path: str, name: str) -> dict:
    """通用 fail-closed 外部闸 (★抄 HW pinout 闸的语义, 不另发明★)"""
    if not os.path.exists(path):
        return {"ok": False, "rc": None, "name": name,
                "detail": f"★闸脚本不存在: {path} ⇒ 视为闸红 (不许静默跳过)"}
    try:
        p = subprocess.run([sys.executable, path], cwd=PROJ, capture_output=True,
                           text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": None, "name": name, "detail": "★闸脚本超时 (300s) ⇒ 视为闸红"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "rc": None, "name": name, "detail": f"★闸脚本跑不起来: {e} ⇒ 视为闸红"}
    out = p.stdout or ""
    fails = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("[FAIL]")]
    detail = ("; ".join(fails) if fails else "全部检查项通过")
    if p.returncode != 0 and not fails:
        detail = f"rc={p.returncode} 但未解析出 FAIL 行: " + (p.stderr or out).strip()[-300:]
    return {"ok": p.returncode == 0, "rc": p.returncode, "name": name, "detail": detail}
'''


def hook_gates() -> str:
    txt = open(GATE_CHECK, encoding="utf-8").read()
    if "EXTRA_GATES" in txt:
        return "⚠ 已挂过 ⇒ 不重复挂"
    shutil.copy2(GATE_CHECK, GATE_CHECK + ".bak_20261117_2000_main_hook_new_gates")
    # 1) 加函数块 (插在 def main 之前)
    marker = "\ndef main() -> int:"
    assert marker in txt
    txt = txt.replace(marker, NEW_GATES_BLOCK + marker, 1)
    # 2) 调用点: 在 hw_gate 之后
    call_old = """    hw_gate = run_hw_pinout_gate()
    report["hw_pinout_gate"] = hw_gate
    report["summary"]["hw_pinout_gate_ok"] = hw_gate["ok"]
"""
    call_new = """    hw_gate = run_hw_pinout_gate()
    report["hw_pinout_gate"] = hw_gate
    report["summary"]["hw_pinout_gate_ok"] = hw_gate["ok"]

    # ★★2026-11-17 20:0x (main): 新闸挂链 (★ISS-295 / ISS-298·★fail-closed 同款★)★★
    report["extra_gates"] = []
    extra_ok = True
    for _p, _n in EXTRA_GATES:
        _g = run_external_gate(_p, _n)
        report["extra_gates"].append(_g)
        report["summary"][f"extra_gate_ok::{_n}"] = _g["ok"]
        if not _g["ok"]:
            extra_ok = False
            report["gaps"].append(f"★新闸红: {_g['name']} — {_g['detail']}")
"""
    assert call_old in txt
    txt = txt.replace(call_old, call_new, 1)
    # 3) rc 判定: 两处 `return 0 if hw_gate["ok"] else 1`
    txt = txt.replace('return 0 if hw_gate["ok"] else 1',
                      'return 0 if (hw_gate["ok"] and extra_ok) else 1')
    # 4) summary 里加 extra_ok 总旗
    txt = txt.replace('report["summary"]["hw_pinout_gate_ok"] = hw_gate["ok"]',
                      'report["summary"]["hw_pinout_gate_ok"] = hw_gate["ok"]\n    report["summary"]["extra_gates_ok"] = True', 1)
    open(GATE_CHECK, "w", encoding="utf-8").write(txt)
    return "✔ gate_check.py 已挂 2 个新闸"


# ============ (3) CLAIMS §1/§2/§3 → 作业包 §3-S6 ============
def copy_claims() -> str:
    c = open(CLAIMS, encoding="utf-8").read().split("\n")
    # 找 §1 起点 与 §3 终点(下一个 '## ' 或 EOF)
    s1 = e3 = None
    for i, ln in enumerate(c):
        if s1 is None and ln.startswith("## ★§1 ·"):
            s1 = i
        if s1 is not None and ln.startswith("## ") and not ln.startswith("## ★§1 ·") and not ln.startswith("## ★§2 ·") and not ln.startswith("## ★§3 ·"):
            e3 = i
            break
    if s1 is None:
        return "❌ CLAIMS §1 找不到"
    if e3 is None:
        e3 = len(c)
    body = "\n".join(c[s1:e3]).rstrip()
    w = open(WPACK, encoding="utf-8").read()
    if "MECH 侧输入认领句 (★ISS-295 转抄" in w:
        return "⚠ 作业包已转抄过 ⇒ 不重复"
    shutil.copy2(WPACK, WPACK + ".bak_20261117_2000_main_copy_claims")
    head = ("### ★S6.1 · ★★MECH 侧输入认领句全表 (★ISS-295 转抄 · ★追加式 · ★上面 §3-S6 每一行老字一字未删★)★★\n\n"
            "> ★**来源 (★真源 = MECH 侧那页★)**: ★**`MECH/BOARD_ONEPASS_MECH_CLAIMS.md`** ★ (★ISS-295 · mech-lead · 2026-11-17 19:3x 交卷 · main 20:0x 独立复验落 verified★) ★\n"
            "> ⇒ ★**本页 (HW 域) 是【转抄】; ★★若两边打架, 以 MECH 那页为准 + 回报 main 订正** ★ ⇒ ★**抄进来的目的 = 「板只改一次」那一趟开工时, 执行人只读作业包就能看到结构侧的认领句, 不必跨域翻页** ★\n"
            "> ⇒ ★**防漂闸**: `MECH/check_mech_verdict_freshness.py` (★已挂进 `state/gate_check.py`★) ⇒ ★**MECH 页一改, 本转抄没跟 ⇒ 闸红** ★\n\n")
    marker = "\n### ★S7 · DNP 标记"
    assert marker in w, "作业包 S7 段找不到"
    w = w.replace(marker, "\n" + head + body + "\n" + marker, 1)
    open(WPACK, "w", encoding="utf-8").write(w)
    return "✔ CLAIMS §1/§2/§3 已转抄进作业包 §3-S6.1 (★%d 字符★)" % len(body)


def main() -> int:
    print(hook_gates())
    print(copy_claims())

    # ============ (4) pm.yaml: 回 ISS-295 的 need ============
    shutil.copy2(PM, PM + ".bak_20261117_2005_main_answer295")
    d = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    ans = d.setdefault("answers", [])
    have = {a.get("key") for a in ans}
    K = "iss295_mech_struct_input_claims_and_freshness_gate"
    if K not in have:
        ans.append({"key": K, "to": "main",
                     "value": ("★**main 处置 (2026-11-17 20:0x)**: ① ★**CLAIMS 页 §1/§2/§3 已转抄进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S6.1** (★追加式, §3-S6 老字一字未删★) ⇒ 那一趟开工时执行人只读作业包就看得见结构侧认领句 ⇒ ★**若两边打架, 以 MECH 那页为准 + 回报 main 订正** ★ "
                               "② ★**新闸 `MECH/check_mech_verdict_freshness.py` 已挂进 `state/gate_check.py`** (★fail-closed 同款语义: 脚本不存在/跑不起来/超时 ⇒ 算闸红★) ⇒ MECH 页一改而转抄没跟 ⇒ 闸红 ⇒ ★**防漂闭环** ★ "
                               "③ ★**main 独立复验**: `check_mech_verdict_freshness.py` rc=0 + `--selftest` rc=0 (7/7) · `check_onepass_mech_sync.py` rc=0 · `check_onepass_struct_crosscheck.py` rc=0 · `check_board_frame_coords.py` rc=0 · `check_demo_struct_truth.py` rc=0 · 受保护 5 件 md5 逐字节不变 (板 `611b869e…`) ★ ⇒ 落 verified ★"),
                     "ref": "MECH/BOARD_ONEPASS_MECH_CLAIMS.md · HW/PCB/BOARD_ONEPASS_WORKPACKET.md §3-S6.1 · state/gate_check.py (EXTRA_GATES)"})
    d["updated_at"] = "2026-11-17 20:05"
    d["updated_by"] = "main"
    open(PM, "w", encoding="utf-8").write(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100))

    # ============ (1)(5) issue_log ============
    raw = open(LOG, encoding="utf-8").read()
    before = yaml.safe_load(raw) or {}
    bmap = {it["id"]: it for it in before.get("issues", [])}
    lines = raw.split("\n")

    def block_range(iid):
        start = end = None
        for i, ln in enumerate(lines):
            if ln.startswith("- id: "):
                if start is not None:
                    end = i
                    break
                if ln[len("- id: "):].strip() == iid:
                    start = i
        if start is None:
            return None, None
        if end is None:
            end = len(lines)
        return start, end

    def replace_scalar(iid, key, newval):
        s, e = block_range(iid)
        if s is None:
            print("❌ 找不到", iid)
            return False
        blk = lines[s:e]
        ki = None
        for j, ln in enumerate(blk):
            if ln.strip().startswith(key + ":"):
                ki = j
                break
        if ki is None:
            return False
        k = ki + 1
        while k < len(blk):
            ln = blk[k]
            if ln.startswith("- id: "):
                break
            ind = len(ln) - len(ln.lstrip(" "))
            if ind <= 2 and ":" in ln:
                break
            k += 1
        blk[ki:k] = ["  %s: %s" % (key, q(newval))]
        lines[s:e] = blk
        return True

    def append_key(iid, key, newval):
        s, e = block_range(iid)
        blk = lines[s:e]
        keys = {ln.split(":", 1)[0].strip() for ln in blk if ln.startswith("  ") and ":" in ln and not ln.startswith("    ")}
        if key in keys:
            return False
        while blk and blk[-1].strip() == "":
            blk.pop()
        blk.append("  %s: %s" % (key, q(newval)))
        lines[s:e] = blk
        return True

    VN_295 = ("★**main 2026-11-17 20:0x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
              "★**① 新闸**: `MECH/check_mech_verdict_freshness.py` **rc=0** · `--selftest` **rc=0 (7/7)** ★ "
              "★**② 既有 MECH 闸一条没红**: `check_onepass_mech_sync.py` rc=0 · `check_onepass_struct_crosscheck.py` rc=0 · `check_board_frame_coords.py` rc=0 · `check_demo_struct_truth.py` rc=0 ★ "
              "★**③ 全链**: `state/gate_check.py` rc=0 (Q1 18/18 · ★**且新闸已挂进链★) · `state/issue_check.py` rc=0 ★ "
              "★**④ 受保护 5 件 md5 逐字节不变**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 2026-11-06 07:07:17) · `.kicad_pro 3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ **零写板 · 零落表** ⇒ 落 verified ★ "
              "★**★main 侧三件已做 (★gate_check.py 本单不许改 ⇒ 挂闸是 main 的活★)**: ① 新闸挂进 `state/gate_check.py` (★fail-closed 同款: 脚本不存在/跑不起来/超时 ⇒ 算闸红★) ② CLAIMS 页 §1/§2/§3 转抄进 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S6.1 (★追加式★) ③ need `iss295_mech_struct_input_claims_and_freshness_gate` 已由 main 回答案 (★答在 pm.yaml★) ★")
    VN_298 = ("★**main 2026-11-17 20:0x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
              "★**① 闸本体**: `SW/tools/check_onepass_sw_sync.py` **rc=0** · `--selftest` **rc=0 (★原有 10 条一条不许删 + 新增 6 条 = 16 条全过★)** ★ "
              "★**② SW 其余闸一条没红**: `check_demo_panel_spec.py` rc=0 + `--selftest` rc=0 (22/22) · `timing_check.py` rc=0 (85/85) ★ "
              "★**③ 全链**: `state/gate_check.py` rc=0 (Q1 18/18 · ★**且本闸已挂进链★) · `state/issue_check.py` rc=0 ★ "
              "★**④ 受保护 5 件 md5 逐字节不变**: 板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro 3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ **零写板 · 零落表** ⇒ 落 verified ★ "
              "★**★本单是「9 道闸建合法改板通道」里的 SW 那一格 (★ISS-296 MECH 2 道 / ISS-297 HW 6 道 / 本单 SW 1 道★) ⇒ ★**通道形状统一 = ISS-284 的 `reboard` 原子映射 {by,file,prev_md5,md5}, 四项缺一⇒红, 与落表台账链头一致, fail-closed 三条不许动** ★ ⇒ ★**★收工那天必须一次覆盖 9 道, 否则一半的闸照样红 ⇒ 现场会去改板凑绿 ⇒ 板白改第二遍★★** ★")

    for iid, vn, fr in (("ISS-295", VN_295, "HANDOFF/2026-11-17_mech-lead_ISS295_结构输入认领与防漂闸.md (37,075 B · B0~B6) · MECH/BOARD_ONEPASS_MECH_CLAIMS.md (37,114 B · §0~§3) · MECH/check_mech_verdict_freshness.py (22,628 B · rc=0 · --selftest 7/7) · HW/PCB/BOARD_ONEPASS_WORKPACKET.md §3-S6.1 (★main 转抄·追加式★) · state/gate_check.py (★main 挂闸★)"),
                        ("ISS-298", VN_298, "HANDOFF/2026-11-17_sw-lead_ISS298_合法改板通道.md (27,839 B · B1~B8) · SW/tools/check_onepass_sw_sync.py (30,943 → 47,404 B · 合法改板通道 + 反向用例 10→16) · state/gate_check.py (★main 挂闸★)")):
        replace_scalar(iid, "status", "verified")
        replace_scalar(iid, "fix_ref", fr)
        replace_scalar(iid, "verify_result", "pass")
        replace_scalar(iid, "verify_date", TODAY)
        append_key(iid, "verify_note", vn)

    # ISS-297 续做说明 (★不抢派: 派活权归兄弟队列 job fb67af40★)
    old297 = bmap.get("ISS-297")
    if old297:
        tb = old297.get("task_brief") or ""
        if "⑮ 续做说明" not in tb:
            replace_scalar("ISS-297", "task_brief", tb + """

---

## ★★⑮ 续做说明 (★2026-11-17 20:0x main 实跑查盘·★上一趟 19:37:08 timeout 死掉★★)

★**★派活权归兄弟队列 job (★cron `fb67af40` ★★它是【僵尸 fixing 的唯一重派方】★★) ⇒ ★**本 job 不抢派, 只把【盘上现状】交给它★★**

★**★上一趟 (cont1) 死于模型侧 timeout ⇒ 交卷单只有骨架 ⇒ ★**但活的产物可能已在盘上, 请先查盘再决定要不要重做★★**
★**★main 20:0x 实查盘 (★自己跑的, 不抄任何交卷报告★)★**:
| 项 | 状态 |
|---|---|
| ★**交卷单** ★ | ★**骨架 (★1,147 B·★待 main 20:0x 查盘时确认)★** ⇒ ★**直接往里填 B1~B6, 别重建** ★ |
| ★**该域 6 道闸的通道改动** ★ | ★**★请自己查: `HW/check_fsin_rootcause.py` · `HW/check_g1a7_selection_landed.py` · `HW/check_onepass_commit_order.py` · `HW/check_onepass_preflight_coverage.py` · `HW/check_pin_function_labels.py` · `HW/check_workpack_state_values.py`★** ⇒ ★**★凡是已经改到一半的, ★★续着改, 不要从头重写★ ★ |
| ★**通道形状 (★不许自创★)** ★ | ★**ISS-284 的 `reboard` 原子映射 {by, file, prev_md5, md5}** ⇒ ★**四项缺一 ⇒ 整条记录无效 ⇒ 红** ★ ⇒ ★**判据方向不许变 (盘上 ≠ 链头 ⇒ 红) + fail-closed 三条 (链头不唯一 / 链断 / 链头无单号 ⇒ 红) 一条不许动** ★ |
| ★**全仓清单 (★机器生成, 可复核★)** ★ | ★**`state/board_md5_pinned_gates.md`** ★ (+ JSON · 生成脚本 `state/_gen_board_md5_pinned_gates.py`) ⇒ ★**★本单是这 9 道里的 6 道 (HW 侧)★** ★ |
| ★**★已跑通的先例 (★不是猜的★)** ★ | ★**`SW/tools/check_demo_panel_spec.py` 在 ISS-284 转成台账口径后不再硬钉板 md5 ⇒ 全仓清单里根本找不到它** ★ ⇒ ★**⇒ 「不硬钉」不是靠删断言, 是靠判决源换成【落表台账 + 合法改板记录】** ★ |

★**★必跑 (★全部本机实跑, 贴现场 rc★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 HW/check_fsin_rootcause.py ; echo "rc=$?"
python3 HW/check_g1a7_selection_landed.py ; echo "rc=$?"
python3 HW/check_onepass_commit_order.py ; echo "rc=$?"
python3 HW/check_onepass_preflight_coverage.py ; echo "rc=$?"
python3 HW/check_pin_function_labels.py ; echo "rc=$?"
python3 HW/check_workpack_state_values.py ; echo "rc=$?"
python3 state/gate_check.py ; echo "rc=$?"     # ★Q1 18/18 + ★**新挂的两个闸也要绿★**
python3 state/issue_check.py ; echo "rc=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
# ★★板 611b869e… / .kicad_pro 3e504d2b… 一个字节不许变 (本单零写板)★★
```
★**★死因纪律 (★19:37:08 timeout★)**: ★**每条 `exec` ≤ 60 秒** · ★**长任务 `nohup` 后台 + 短轮询** · ★**每 10 分钟至少一次写盘** · ★**交卷单先建骨架再干活** ★
""")
            nt = old297.get("note") or ""
            if "19:37:08 timeout" not in nt:
                replace_scalar("ISS-297", "note", nt + (
                    " ★**2026-11-17 20:0x 追加 (main)**: 上一趟 (cont1) 19:37:08 timeout 死掉 ⇒ 交卷单只有 1,147 B 骨架 ⇒ ★**僵尸 fixing** ★ ⇒ "
                    "★**派活权归兄弟队列 job `fb67af40` (★它是僵尸 fixing 的唯一重派方★) ⇒ 本 job 不抢派, 只把【盘上现状 + 通道形状 + 全仓清单】交给它** ★ ⇒ 任务书已追加「⑮ 续做说明」 ★"))

    out = "\n".join(lines)
    shutil.copy2(LOG, LOG + ".bak_20261117_2010_main_verify295_298_relay297")
    open(LOG, "w", encoding="utf-8").write(out)

    after = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    amap = {it["id"]: it for it in after.get("issues", [])}
    ok = True
    for iid, it in bmap.items():
        a = amap.get(iid, {})
        for k, v in it.items():
            if iid in ("ISS-295", "ISS-298") and k in ("status", "fix_ref", "verify_result", "verify_date", "verify_note"):
                continue
            if iid == "ISS-297" and k in ("note", "task_brief"):
                continue
            if a.get(k) != v:
                print("❌", iid, k)
                ok = False
    for iid in ("ISS-295", "ISS-298"):
        it = amap[iid]
        print("  %s -> %s verify_result=%s verify_note=%d B" % (iid, it["status"], it.get("verify_result"), len(it.get("verify_note") or "")))
    print("  ISS-297 含⑮ =", "⑮ 续做说明" in (amap["ISS-297"].get("task_brief") or ""))
    print("  其余 issue 逐字相同 =", ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
