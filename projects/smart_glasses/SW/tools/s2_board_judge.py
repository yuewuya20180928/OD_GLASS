#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s2_board_judge.py —— S2 救砖链路 CB-01 ~ CB-09 机械判定器 (板端)

================================================================================
它解决什么
--------------------------------------------------------------------------------
ISS-080 交付的是**方案** (判据写清楚了), 但没人能在板子回来后"照着判"。
本脚本把 EVT_TEMPLATE.md §11.2 的 9 条子判据 + §11.4 的机械规则, 变成
**一条命令就能出结论**的判定器:

    python3 SW/tools/s2_board_judge.py --evidence-dir <目录> \
        --config SW/tools/s2_rescue_config.json

它读板端跑测脚本 (s2_board_run.sh) 落下的证据文件, 逐条判 CB-01~CB-09,
输出 s2_br01_verdict.json + 一张人读的表。

三态判定 (严格按 EVT §11.4 的 R1/R2/R3)
--------------------------------------------------------------------------------
    PASS        有有效实测数据, 且满足判过标准            → 折算 ✅
    FAIL        有有效实测数据, 但违反标准                → 折算 ❌
    UNVERIFIED  没有有效实测数据 (文件缺失 / 只有推算)     → 折算 ⚠️ 未验

★ 关键纪律 (本脚本的三条硬规则):
  1) **缺失就是 UNVERIFIED, 绝不判 PASS**。文件不在 → 判"未验", 不是"通过"。
  2) ★ **generic-example 签名不算证据**。usb_signatures 里标 source=generic-example
     的条目 (别的平台的通用示例) 即使命中了设备, CB-01 也只判 UNVERIFIED ——
     防止"用通用示例冒充真值"这条 ISS-080 口径被绕过。
  3) ★ **P4 未填 ⇒ CB-02/CB-06 判 UNVERIFIED**。partition_layout 现在是 [推算] 占位,
     拿占位表去判回读 CRC 通过 = 拿推算冒充实测。
  4) ★ **"修复人不能自验"**: 本脚本只出 CB 级结论; BR-01 总判定与"判过"由
     项目总工 (main) 签 (state/issue_log.yaml ISS-120 verify_by=main)。

证据文件约定 (由 s2_board_run.sh 落盘, 名字与 EVT_TEMPLATE §11.7 对齐)
--------------------------------------------------------------------------------
    s2_step0_normal.json    正常态 USB 枚举基线        (EVT §11.7 #1)
    s2_step1_boot.json      BOOT 态证据 E1/E2           (EVT §11.7 #2)
    <tool>_flash.log        下载工具刷写日志            (EVT §11.7 #3)
    s2_step3_verify.json    版本块回读校验               (EVT §11.7 #4)
    s2_step4_selftest.log   板端自检 + 版本串           (EVT §11.7 #5)
    s2_step4_selftest.json  同上的机器可读版 (本脚本读这个)
    s2_boot_timing.png      BOOT/RESET 时序波形 (人工)   (EVT §11.7 #6)
    ★ 以下为本单新增 (ISS-120):
    s2_step2_flash.json     刷写结果 (rc / 分区级结果)
    s2_step5_reenum.json    刷完后重新枚举 (CB-01 用)
    s2_step6_reboot.json    重启 3 次 (CB-05 用)
    s2_forensics.json       失败现场取证 (串口/工具版本/电流表)

退出码
--------------------------------------------------------------------------------
    0 = BR-01 总判定 ✅ (CB 9/9 全 PASS)
    1 = BR-01 总判定 ❌ (至少 1 条 FAIL)
    2 = BR-01 总判定 ⚠️ 未验 (有 UNVERIFIED, 但无 FAIL) —— **此时板子不得进产线**
    3 = 输入有问题 (证据目录/配置缺失或坏格式)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

VER_FIELDS = ["boot", "kern", "rootfs", "app", "model", "isp"]

# 5 条版本串校验规则 (SW/FLASH_AND_VERSION.md §3.1.3)
R_FORMAT = re.compile(r"^ARS45-SW\s+(\d+\.\d+\.\d+)(?:\+([0-9A-Za-z._-]+))?(\s|$)")
R_SHA8 = re.compile(r"^[0-9a-f]{8}$")

# 日志错误码 (CB-09)
ERR_CODES = ["E_MODEL_MISMATCH", "E_CALIB_MISSING", "E_SN_MISMATCH"]
ERR_RE = re.compile(r"E_VER_[A-Z_]+")

PASS, FAIL, UNVER = "PASS", "FAIL", "UNVERIFIED"


# ------------------------------------------------------------------ 小工具
def load_json(path: str):
    if not os.path.exists(path):
        return None, "文件不存在"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:  # noqa: BLE001
        return None, f"解析失败: {e}"


def param_done(cfg: dict, key: str) -> bool:
    p = (cfg.get("params") or {}).get(key) or {}
    val = p.get("value")
    return val not in (None, "", [], {}) and str(p.get("status", "")).upper() == "DONE"


def split_signatures(cfg: dict) -> tuple[list[dict], list[dict]]:
    """签名表拆成 (真值签名, 通用示例签名)。★ 只有真值签名能当证据。"""
    entries = ((cfg.get("usb_signatures") or {}).get("entries") or [])
    real, generic = [], []
    for e in entries:
        src = str(e.get("source", "")).lower()
        (generic if src == "generic-example" else real).append(e)
    return real, generic


def check_by_name(checks: list, prefix: str) -> list[dict]:
    return [c for c in checks if str(c.get("name", "")).startswith(prefix)]


def worst(results: list[str]) -> str:
    """把一组子判定汇总成一条: 有 FAIL → FAIL; 否则有 UNVERIFIED → UNVERIFIED; 否则 PASS。"""
    if FAIL in results:
        return FAIL
    if UNVER in results:
        return UNVER
    return PASS


# ------------------------------------------------------------------ 版本串 (CB-03)
def parse_version(line: str, cfg: dict) -> dict:
    """
    按 §3.1.3 的 5 条规则判版本串。返回:
        {"rules": [{"id","name","result","detail"}], "fields": {...}}
    ★ 每条规则都能单独判 UNVERIFIED (例如板上没有模型文件 → 算不出 sha8)。
    """
    rules: list[dict] = []
    fields: dict[str, str] = {}

    def add(rid, name, result, detail):
        rules.append({"id": rid, "name": name, "result": result, "detail": detail})

    line = (line or "").strip()
    if not line:
        add("R1_FORMAT", "行首 'ARS45-SW ' + 合法 semver", FAIL, "版本串为空")
        add("R2_SN", "sn= 非空且与板卡丝印一致", UNVER, "无版本串")
        add("R3_MODEL_SHA", "model= 的 sha8 == 板上模型文件 sha256 前 8", UNVER, "无版本串")
        add("R4_INCOMPLETE", "6 分项 (boot/kern/rootfs/app/model/isp) 全非空", FAIL, "无版本串")
        add("R5_MODE", "mode= 与期望一致", UNVER, "无版本串")
        return {"rules": rules, "fields": fields}

    # R1 格式
    m = R_FORMAT.match(line)
    if not m:
        add("R1_FORMAT", "行首 'ARS45-SW ' + 合法 semver", FAIL,
            f"行首不匹配 'ARS45-SW <semver>': {line[:60]!r}")
    else:
        add("R1_FORMAT", "行首 'ARS45-SW ' + 合法 semver", PASS,
            f"semver={m.group(1)}" + (f"+{m.group(2)}" if m.group(2) else ""))

    # 字段切分 (key=value, 值不含空格)
    for tok in line.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            fields[k] = v

    # R2 SN
    sn = fields.get("sn", "")
    expected_sn = ((cfg.get("version_meta") or {}).get("sn")
                   or ((cfg.get("board_test") or {}).get("board_sn")))
    if not sn:
        add("R2_SN", "sn= 非空且与板卡丝印一致", FAIL, "版本串里没有 sn= 字段")
    elif not expected_sn:
        add("R2_SN", "sn= 非空且与板卡丝印一致", UNVER,
            f"版本串 sn={sn}, 但配置里没有板卡丝印/期望 SN, 无法比对")
    elif sn != expected_sn:
        add("R2_SN", "sn= 非空且与板卡丝印一致", FAIL,
            f"版本串 sn={sn} != 板卡/配置 sn={expected_sn} (E_SN_MISMATCH)")
    else:
        add("R2_SN", "sn= 非空且与板卡丝印一致", PASS, f"sn={sn}")

    # R3 模型 sha8
    model = fields.get("model", "")
    sha8 = model.rsplit("-", 1)[-1] if model else ""
    actual_sha8 = None  # 由调用方从证据里塞进来
    rules.append({"id": "R3_MODEL_SHA", "name": "model= 的 sha8 == 板上模型文件 sha256 前 8",
                  "result": UNVER, "detail": "未拿到板上模型文件 sha256 (待板端自检回读)", "_pending": True})

    # R4 六分项齐全
    missing = [f for f in VER_FIELDS if not fields.get(f)]
    if missing:
        add("R4_INCOMPLETE", "6 分项 (boot/kern/rootfs/app/model/isp) 全非空", FAIL,
            f"缺 {missing} (E_VER_INCOMPLETE)")
    else:
        add("R4_INCOMPLETE", "6 分项 (boot/kern/rootfs/app/model/isp) 全非空", PASS, "6/6 非空")

    # R5 mode
    mode = fields.get("mode", "")
    want = (cfg.get("version_meta") or {}).get("mode")
    if not mode:
        add("R5_MODE", "mode= 与期望一致", FAIL, "版本串里没有 mode= 字段")
    elif not want:
        add("R5_MODE", "mode= 与期望一致", UNVER, f"版本串 mode={mode}, 但配置未写期望 mode")
    elif mode != want:
        add("R5_MODE", "mode= 与期望一致", FAIL, f"mode={mode} != 期望 {want} (E_MODE_MISMATCH)")
    else:
        add("R5_MODE", "mode= 与期望一致", PASS, f"mode={mode}")

    return {"rules": rules, "fields": fields, "_r3_pending": True}


def apply_model_sha(parsed: dict, actual_sha8: str | None) -> None:
    """把板端实测到的模型 sha8 填回 R3 规则 (没实测到就保持 UNVERIFIED)。"""
    fields = parsed.get("fields") or {}
    model = fields.get("model", "")
    sha8 = model.rsplit("-", 1)[-1] if model else ""
    for r in parsed.get("rules") or []:
        if r.get("id") != "R3_MODEL_SHA":
            continue
        if not actual_sha8:
            r["result"] = UNVER
            r["detail"] = "板端未回读到模型文件 sha256 (model_path 未配或板上没有 sha256sum)"
            continue
        if not R_SHA8.match(sha8):
            r["result"] = FAIL
            r["detail"] = f"版本串 model={model!r} 里解析不出 8 位十六进制 sha8"
        elif sha8.lower() != actual_sha8.lower():
            r["result"] = FAIL
            r["detail"] = f"版本串 sha8={sha8} != 板上实测 {actual_sha8} (E_MODEL_MISMATCH)"
        else:
            r["result"] = PASS
            r["detail"] = f"sha8={sha8} == 板上实测 {actual_sha8}"


# ------------------------------------------------------------------ CB-01
def judge_cb01(ev: dict, cfg: dict) -> dict:
    """刷完后重新枚举回正常态。"""
    reenum, err = load_json(os.path.join(ev, "s2_step5_reenum.json"))
    if reenum is None:
        return {"id": "CB-01", "name": "设备重新枚举回正常态", "result": UNVER,
                "why": f"缺 s2_step5_reenum.json ({err}) —— 没跑刷后枚举, 不判过",
                "evidence": ["s2_step5_reenum.json"]}

    base, berr = load_json(os.path.join(ev, "s2_step0_normal.json"))
    if base is None:
        return {"id": "CB-01", "name": "设备重新枚举回正常态", "result": UNVER,
                "why": f"缺正常态基线 s2_step0_normal.json ({berr}) —— 没有基线可比",
                "evidence": ["s2_step5_reenum.json", "s2_step0_normal.json"]}

    real_sigs, generic_sigs = split_signatures(cfg)
    matched = reenum.get("matched_boot") or []
    matched_generic = [m for m in matched if str((m or {}).get("source", "")).lower() == "generic-example"]
    matched_real = [m for m in matched if m not in matched_generic]

    now_vid = reenum.get("vidpid")
    base_vid = base.get("vidpid")
    if not now_vid or not base_vid:
        return {"id": "CB-01", "name": "设备重新枚举回正常态", "result": UNVER,
                "why": "枚举结果里没有 VID:PID (刷后或基线缺失)",
                "evidence": ["s2_step5_reenum.json", "s2_step0_normal.json"]}

    if matched_generic:
        return {"id": "CB-01", "name": "设备重新枚举回正常态", "result": UNVER,
                "why": (f"命中了 {len(matched_generic)} 条 source=generic-example 的通用示例签名 "
                        f"—— 那是别的平台的示例, 不是 ARS45 真值, 不算证据 (ISS-080 口径)"),
                "evidence": ["s2_step5_reenum.json"]}

    if matched_real:
        return {"id": "CB-01", "name": "设备重新枚举回正常态", "result": FAIL,
                "why": f"刷完后仍匹配 BOOT 态签名 {[m.get('vid') + ':' + m.get('pid') for m in matched_real]}",
                "evidence": ["s2_step5_reenum.json"]}

    if now_vid != base_vid:
        return {"id": "CB-01", "name": "设备重新枚举回正常态", "result": FAIL,
                "why": f"刷后 VID:PID={now_vid} != 正常态基线 {base_vid}",
                "evidence": ["s2_step5_reenum.json", "s2_step0_normal.json"]}

    return {"id": "CB-01", "name": "设备重新枚举回正常态", "result": PASS,
            "why": f"VID:PID={now_vid} 与基线一致, 且不匹配任何 BOOT 签名",
            "evidence": ["s2_step5_reenum.json", "s2_step0_normal.json"]}


# ------------------------------------------------------------------ CB-02 / CB-06
def judge_verify_checks(ev: str, cfg: dict, prefix: str, cb_id: str, cb_name: str,
                        need_p4: bool) -> dict:
    """从 flash_writer verify 的 JSON 里取某前缀的检查项。"""
    data, err = load_json(os.path.join(ev, "s2_step3_verify.json"))
    if data is None:
        return {"id": cb_id, "name": cb_name, "result": UNVER,
                "why": f"缺 s2_step3_verify.json ({err})", "evidence": ["s2_step3_verify.json"]}
    if need_p4 and not param_done(cfg, "P4_BOOT_STORE"):
        return {"id": cb_id, "name": cb_name, "result": UNVER,
                "why": ("P4_BOOT_STORE 未填 (真实分区表还没有) —— partition_layout 现在是 [推算] 占位, "
                        "用它判回读 CRC 通过 = 拿推算冒充实测"),
                "evidence": ["s2_step3_verify.json"]}
    checks = check_by_name(data.get("checks") or [], prefix)
    if not checks:
        return {"id": cb_id, "name": cb_name, "result": UNVER,
                "why": f"verify 结果里没有 {prefix}* 检查项", "evidence": ["s2_step3_verify.json"]}
    results = [str(c.get("result", "")).upper() for c in checks]
    if FAIL in results:
        bad = [c for c in checks if str(c.get("result", "")).upper() == FAIL]
        return {"id": cb_id, "name": cb_name, "result": FAIL,
                "why": "; ".join(f"{c.get('name')}: {c.get('detail')}" for c in bad),
                "evidence": ["s2_step3_verify.json"]}
    if UNVER in results:
        return {"id": cb_id, "name": cb_name, "result": UNVER,
                "why": f"{prefix}* 检查项里有未验项", "evidence": ["s2_step3_verify.json"]}
    return {"id": cb_id, "name": cb_name, "result": PASS,
            "why": f"{len(checks)} 项全过 ({prefix}*)", "evidence": ["s2_step3_verify.json"]}


# ------------------------------------------------------------------ CB-03
def judge_cb03(ev: str, cfg: dict) -> dict:
    st, err = load_json(os.path.join(ev, "s2_step4_selftest.json"))
    if st is None:
        return {"id": "CB-03", "name": "版本串 6 分项齐全 + 5 条校验规则", "result": UNVER,
                "why": f"缺 s2_step4_selftest.json ({err})", "evidence": ["s2_step4_selftest.json"]}
    parsed = parse_version(st.get("version_string", ""), cfg)
    apply_model_sha(parsed, st.get("model_sha8"))
    rules = parsed.get("rules") or []
    results = [r["result"] for r in rules]
    res = worst(results)
    bad = [f"{r['id']}({r['result']}): {r['detail']}" for r in rules if r["result"] == FAIL]
    unv = [f"{r['id']}({r['result']}): {r['detail']}" for r in rules if r["result"] == UNVER]
    why = "; ".join(bad or unv) or f"5 条规则全过"
    return {"id": "CB-03", "name": "版本串 6 分项齐全 + 5 条校验规则", "result": res,
            "why": why, "rules": rules, "evidence": ["s2_step4_selftest.json"]}


# ------------------------------------------------------------------ CB-04
SELFTEST_ITEMS = [
    ("ddr", "DDR 自检"),
    ("sensor", "sensor 枚举"),
    ("i2c", "光机 I2C 应答"),
    ("npu", "NPU 模型加载"),
    ("od", "OD 跑通 1 帧"),
    ("version", "版本块回显"),
]


def judge_cb04(ev: str, cfg: dict) -> dict:
    st, err = load_json(os.path.join(ev, "s2_step4_selftest.json"))
    if st is None:
        return {"id": "CB-04", "name": "启动自检 6 项", "result": UNVER,
                "why": f"缺 s2_step4_selftest.json ({err})", "evidence": ["s2_step4_selftest.json"]}
    got = st.get("selftest") or {}
    results, bad = [], []
    for key, name in SELFTEST_ITEMS:
        item = got.get(key) or {}
        r = str(item.get("status", "UNVERIFIED")).upper()
        if r not in (PASS, FAIL):
            r = UNVER
        results.append(r)
        if r != PASS:
            bad.append(f"{name}: {r} ({item.get('detail', '无输出')})")
    res = worst(results)
    return {"id": "CB-04", "name": "启动自检 6 项", "result": res,
            "why": "; ".join(bad) if bad else "6/6 全过",
            "evidence": ["s2_step4_selftest.json"]}


# ------------------------------------------------------------------ CB-05
def judge_cb05(ev: str) -> dict:
    rb, err = load_json(os.path.join(ev, "s2_step6_reboot.json"))
    if rb is None:
        return {"id": "CB-05", "name": "重启 3 次自启动", "result": UNVER,
                "why": f"缺 s2_step6_reboot.json ({err})", "evidence": ["s2_step6_reboot.json"]}
    attempts = rb.get("attempts") or []
    ok = sum(1 for a in attempts if a.get("ok"))
    panics = [a for a in attempts if a.get("panic")]
    if len(attempts) < 3:
        return {"id": "CB-05", "name": "重启 3 次自启动", "result": UNVER,
                "why": f"只重启了 {len(attempts)}/3 次", "evidence": ["s2_step6_reboot.json"]}
    if panics:
        return {"id": "CB-05", "name": "重启 3 次自启动", "result": FAIL,
                "why": f"{len(panics)} 次出现 kernel panic", "evidence": ["s2_step6_reboot.json"]}
    if ok < 3:
        return {"id": "CB-05", "name": "重启 3 次自启动", "result": FAIL,
                "why": f"{ok}/3 次进系统成功", "evidence": ["s2_step6_reboot.json"]}
    return {"id": "CB-05", "name": "重启 3 次自启动", "result": PASS,
            "why": "3/3 进系统, 0 次 kernel panic", "evidence": ["s2_step6_reboot.json"]}


# ------------------------------------------------------------------ CB-07
def judge_cb07(ev: str, cfg: dict) -> dict:
    st, err = load_json(os.path.join(ev, "s2_step4_selftest.json"))
    if st is None:
        return {"id": "CB-07", "name": "标定 ID 与出厂台账一致", "result": UNVER,
                "why": f"缺 s2_step4_selftest.json ({err})", "evidence": ["s2_step4_selftest.json"]}
    parsed = parse_version(st.get("version_string", ""), cfg)
    actual = (parsed.get("fields") or {}).get("calib", "")
    ledger = ((cfg.get("board_test") or {}).get("checks") or {}).get("calib_ledger")
    if not actual:
        return {"id": "CB-07", "name": "标定 ID 与出厂台账一致", "result": UNVER,
                "why": "版本串里没有 calib= 字段", "evidence": ["s2_step4_selftest.json"]}
    if not ledger:
        return {"id": "CB-07", "name": "标定 ID 与出厂台账一致", "result": UNVER,
                "why": (f"版本串 calib={actual}, 但工厂标定台账还没建 "
                        f"(board_test.checks.calib_ledger 未填) —— 无从比对"),
                "evidence": ["s2_step4_selftest.json"]}
    if actual != ledger:
        return {"id": "CB-07", "name": "标定 ID 与出厂台账一致", "result": FAIL,
                "why": f"版本串 calib={actual} != 台账 {ledger} (F6: 刷完画质退化的头号坑)",
                "evidence": ["s2_step4_selftest.json"]}
    return {"id": "CB-07", "name": "标定 ID 与出厂台账一致", "result": PASS,
            "why": f"calib={actual} 与台账一致", "evidence": ["s2_step4_selftest.json"]}


# ------------------------------------------------------------------ CB-08
def judge_cb08(ev: str, cfg: dict) -> dict:
    st, err = load_json(os.path.join(ev, "s2_step4_selftest.json"))
    reenum, rerr = load_json(os.path.join(ev, "s2_step5_reenum.json"))
    if st is None:
        return {"id": "CB-08", "name": "mode 位正确", "result": UNVER,
                "why": f"缺 s2_step4_selftest.json ({err})", "evidence": ["s2_step4_selftest.json"]}
    parsed = parse_version(st.get("version_string", ""), cfg)
    mode = (parsed.get("fields") or {}).get("mode", "")
    want = (cfg.get("version_meta") or {}).get("mode")
    if not mode:
        return {"id": "CB-08", "name": "mode 位正确", "result": UNVER,
                "why": "版本串里没有 mode= 字段", "evidence": ["s2_step4_selftest.json"]}
    if not want:
        return {"id": "CB-08", "name": "mode 位正确", "result": UNVER,
                "why": f"版本串 mode={mode}, 配置未写期望 mode", "evidence": ["s2_step4_selftest.json"]}
    if mode != want:
        return {"id": "CB-08", "name": "mode 位正确", "result": FAIL,
                "why": f"mode={mode} != 期望 {want}", "evidence": ["s2_step4_selftest.json"]}
    if reenum is None:
        return {"id": "CB-08", "name": "mode 位正确", "result": UNVER,
                "why": f"缺 s2_step5_reenum.json ({rerr}) —— 没法核 'prod 下插线无 adb 设备'",
                "evidence": ["s2_step4_selftest.json", "s2_step5_reenum.json"]}
    adb = reenum.get("adb_devices")
    if adb is None:
        return {"id": "CB-08", "name": "mode 位正确", "result": UNVER,
                "why": "枚举证据里没有 adb devices 采样 (未执行 adb devices)",
                "evidence": ["s2_step5_reenum.json"]}
    if want == "prod" and adb:
        return {"id": "CB-08", "name": "mode 位正确", "result": FAIL,
                "why": f"mode=prod 但插线仍有 adb 设备 {adb} (adbd 没关)",
                "evidence": ["s2_step5_reenum.json"]}
    return {"id": "CB-08", "name": "mode 位正确", "result": PASS,
            "why": f"mode={mode}, prod 下 adb devices 为空", "evidence": ["s2_step4_selftest.json",
                                                                          "s2_step5_reenum.json"]}


# ------------------------------------------------------------------ CB-09
def judge_cb09(ev: str) -> dict:
    st, err = load_json(os.path.join(ev, "s2_step4_selftest.json"))
    if st is None:
        return {"id": "CB-09", "name": "日志无错误码", "result": UNVER,
                "why": f"缺 s2_step4_selftest.json ({err})", "evidence": ["s2_step4_selftest.json"]}
    scan = st.get("log_scan") or {}
    if "errors" not in scan:
        return {"id": "CB-09", "name": "日志无错误码", "result": UNVER,
                "why": "没做日志扫描 (log_scan 缺失)", "evidence": ["s2_step4_selftest.json"]}
    errors = scan.get("errors") or []
    if errors:
        return {"id": "CB-09", "name": "日志无错误码", "result": FAIL,
                "why": f"日志里出现错误码: {errors}", "evidence": ["s2_step4_selftest.json"]}
    return {"id": "CB-09", "name": "日志无错误码", "result": PASS,
            "why": f"扫了 {scan.get('scanned_lines', '?')} 行, 无 E_MODEL_MISMATCH/E_CALIB_MISSING/E_VER_*/E_SN_MISMATCH",
            "evidence": ["s2_step4_selftest.json"]}


# ------------------------------------------------------------------ 汇总
def judge_all(ev_dir: str, cfg: dict) -> dict:
    cbs = [
        judge_cb01(ev_dir, cfg),
        judge_verify_checks(ev_dir, cfg, "CB-02", "CB-02",
                            "版本块 magic + bootable + payload CRC", need_p4=False),
        judge_cb03(ev_dir, cfg),
        judge_cb04(ev_dir, cfg),
        judge_cb05(ev_dir),
        judge_verify_checks(ev_dir, cfg, "CB-06", "CB-06",
                            "分区回读 CRC = 写入镜像 CRC", need_p4=True),
        judge_cb07(ev_dir, cfg),
        judge_cb08(ev_dir, cfg),
        judge_cb09(ev_dir),
    ]
    results = [c["result"] for c in cbs]
    if FAIL in results:
        overall, verdict = FAIL, "❌ 不通过"
    elif UNVER in results:
        overall, verdict = UNVER, "⚠️ 未验"
    else:
        overall, verdict = PASS, "✅ 通过"

    n_fail = results.count(FAIL)
    n_unver = results.count(UNVER)
    n_pass = results.count(PASS)
    return {
        "tool": "s2_board_judge.py",
        "evidence_dir": os.path.abspath(ev_dir),
        "config": "见运行参数",
        "cbs": cbs,
        "summary": {"total": len(cbs), "pass": n_pass, "fail": n_fail, "unverified": n_unver},
        "br01": {
            "verdict": verdict,
            "result": overall,
            "rule": "EVT_TEMPLATE.md §11.4: R1 9/9 全过才 ✅; 有未验 → 最高 ⚠️; 有 FAIL → ❌",
            "production_redline": ("★ BR-01 判 ⚠️未验 或 ❌ 的板 **不得进产线 / 不得交付**; "
                                   "整批未验 → 不得量产 (EVT §11.4 R5)"),
            "judged_by": "项目总工 (main) —— 修复人不能自验 (issue_log ISS-120 verify_by=main)",
        },
        "evidence": ("[实测] 本判定只反映证据目录里的实测数据; 缺失一律判 UNVERIFIED, "
                     "绝不用推算/通用示例补位"),
    }


def print_table(rep: dict) -> None:
    print("=" * 78)
    print("S2 救砖链路 · BR-01 机械判定 (CB-01 ~ CB-09)")
    print("=" * 78)
    mark = {PASS: "✅", FAIL: "❌", UNVER: "⚠️"}
    for c in rep["cbs"]:
        print(f"{mark[c['result']]} {c['id']}  {c['name']}")
        print(f"      {c['why']}")
    s = rep["summary"]
    print("-" * 78)
    print(f"合计: PASS {s['pass']} / FAIL {s['fail']} / 未验 {s['unverified']}  (共 {s['total']})")
    print(f"BR-01 总判定: {rep['br01']['verdict']}")
    print(f"  {rep['br01']['production_redline']}")
    print(f"  判过: {rep['br01']['judged_by']}")
    print("=" * 78)


# ------------------------------------------------------------------ 自测
def selftest() -> int:
    """纯逻辑自测 (不需要板子)。构造合成证据目录, 验 4 条核心行为。"""
    cases = []

    def make_ev(root: str, mode: str) -> str:
        ev = os.path.join(root, mode)
        os.makedirs(ev, exist_ok=True)
        cfg = {
            "params": {"P4_BOOT_STORE": {"value": "x" if mode == "all" else None, "status": "DONE" if mode == "all" else "TODO"}},
            "version_meta": {"mode": "prod", "sn": "SN-001"},
            "usb_signatures": {"entries": [
                {"vid": "2207", "pid": "330c", "label": "Maskrom", "source": "vendor-official"},
                {"vid": "0451", "pid": "6146", "label": "TI DFU", "source": "generic-example"},
            ]},
            "board_test": {"checks": {"calib_ledger": "CALIB-001"},
                           "board_sn": "SN-001"},
        }
        if mode == "all":
            cfg["params"]["P4_BOOT_STORE"]["value"] = "real"
        with open(os.path.join(ev, "s2_step0_normal.json"), "w", encoding="utf-8") as f:
            json.dump({"vidpid": "2207:350a", "devices": []}, f)
        with open(os.path.join(ev, "s2_step3_verify.json"), "w", encoding="utf-8") as f:
            json.dump({"result": "PASS", "checks": [
                {"name": "CB-02a 版本块 magic == 'AR45'", "result": "PASS", "detail": "ok"},
                {"name": "CB-02b bootable 标志置位", "result": "PASS", "detail": "ok"},
                {"name": "CB-02c 版本块 payload CRC 一致", "result": "PASS", "detail": "ok"},
                {"name": "CB-06 分区 CRC 一致 [bootloader]", "result": "PASS", "detail": "ok"},
                {"name": "CB-06 分区 CRC 一致 [kernel]", "result": "PASS", "detail": "ok"},
            ]}, f)
        with open(os.path.join(ev, "s2_step4_selftest.json"), "w", encoding="utf-8") as f:
            json.dump({
                "version_string": ("ARS45-SW 1.0.0+g1234abc board=EVT1 sn=SN-001 build=20261030T0000+0800 "
                                    "boot=0.0.0 kern=5.10.0-gdeadbee rootfs=R20261030.1 app=1.0.0+g1234abc "
                                    "model=yolov5s-int8-ag2-1a2b3c4d isp=CALIB-001 mode=prod calib=CALIB-001"),
                "model_sha8": "1a2b3c4d",
                "selftest": {k: {"status": "PASS", "detail": "ok"} for k, _ in SELFTEST_ITEMS},
                "log_scan": {"scanned_lines": 100, "errors": []},
            }, f)
        with open(os.path.join(ev, "s2_step5_reenum.json"), "w", encoding="utf-8") as f:
            json.dump({"vidpid": "2207:350a", "matched_boot": [], "adb_devices": []}, f)
        with open(os.path.join(ev, "s2_step6_reboot.json"), "w", encoding="utf-8") as f:
            json.dump({"attempts": [{"n": i, "ok": True, "panic": False} for i in (1, 2, 3)]}, f)
        return ev

    with tempfile.TemporaryDirectory() as root:
        # T1 全 PASS → BR-01 ✅
        ev = make_ev(root, "all")
        rep = judge_all(ev, json.loads(json.dumps(_cfg_all())))
        cases.append(("T1 9/9 全 PASS → BR-01 ✅", rep["br01"]["result"] == PASS))

        # T2 缺证据文件 → 判 UNVERIFIED 而不是 PASS
        ev2 = os.path.join(root, "missing")
        os.makedirs(ev2, exist_ok=True)
        rep2 = judge_all(ev2, json.loads(json.dumps(_cfg_all())))
        cases.append(("T2 证据全缺 → 9 条全 UNVERIFIED, 绝不判 PASS",
                      all(c["result"] == UNVER for c in rep2["cbs"]) and rep2["br01"]["result"] == UNVER))

        # T3 P4 未填 → CB-06 判 UNVERIFIED (不能拿 [推算] 占位表判过)
        ev3 = make_ev(root, "all")
        cfg3 = json.loads(json.dumps(_cfg_all()))
        cfg3["params"]["P4_BOOT_STORE"] = {"value": None, "status": "TODO"}
        rep3 = judge_all(ev3, cfg3)
        cb06 = next(c for c in rep3["cbs"] if c["id"] == "CB-06")
        cases.append(("T3 P4 未填 → CB-06 判未验 (占位分区表不算实测)", cb06["result"] == UNVER))

        # T4 通用示例签名命中 → CB-01 判 UNVERIFIED (不认 generic-example)
        ev4 = make_ev(root, "all")
        with open(os.path.join(ev4, "s2_step5_reenum.json"), "w", encoding="utf-8") as f:
            json.dump({"vidpid": "2207:350a",
                       "matched_boot": [{"vid": "0451", "pid": "6146", "source": "generic-example"}],
                       "adb_devices": []}, f)
        rep4 = judge_all(ev4, json.loads(json.dumps(_cfg_all())))
        cb01 = next(c for c in rep4["cbs"] if c["id"] == "CB-01")
        cases.append(("T4 命中 generic-example 签名 → CB-01 判未验 (不拿通用示例冒充真值)",
                      cb01["result"] == UNVER))

        # T5 版本串缺分项 → CB-03 判 FAIL
        ev5 = make_ev(root, "all")
        p = os.path.join(ev5, "s2_step4_selftest.json")
        d = json.load(open(p, encoding="utf-8"))
        d["version_string"] = d["version_string"].replace("isp=CALIB-001 ", "")
        json.dump(d, open(p, "w", encoding="utf-8"))
        rep5 = judge_all(ev5, json.loads(json.dumps(_cfg_all())))
        cb03 = next(c for c in rep5["cbs"] if c["id"] == "CB-03")
        cases.append(("T5 版本串缺 6 分项 → CB-03 判不通过", cb03["result"] == FAIL))

        # T6 重启不足 3 次 → CB-05 判未验
        ev6 = make_ev(root, "all")
        with open(os.path.join(ev6, "s2_step6_reboot.json"), "w", encoding="utf-8") as f:
            json.dump({"attempts": [{"n": 1, "ok": True, "panic": False}]}, f)
        rep6 = judge_all(ev6, json.loads(json.dumps(_cfg_all())))
        cb05 = next(c for c in rep6["cbs"] if c["id"] == "CB-05")
        cases.append(("T6 只重启 1 次 → CB-05 判未验", cb05["result"] == UNVER))

    print("=" * 78)
    print("s2_board_judge 自测 (纯逻辑, 无需硬件)")
    print("=" * 78)
    n_fail = 0
    for name, ok in cases:
        print(f"{'✅' if ok else '❌'} {name}")
        if not ok:
            n_fail += 1
    print("-" * 78)
    print(f"结论: {'PASS' if n_fail == 0 else 'FAIL'} ({len(cases) - n_fail}/{len(cases)} 通过)")
    print("证据: [实测] PC 侧合成证据自测 (判定逻辑), 不代表板端 S2 已通")
    return 0 if n_fail == 0 else 3


def _cfg_all() -> dict:
    return {
        "params": {"P4_BOOT_STORE": {"value": "real-partition-table", "status": "DONE"}},
        "version_meta": {"mode": "prod", "sn": "SN-001"},
        "usb_signatures": {"entries": [
            {"vid": "2207", "pid": "330c", "label": "Maskrom", "source": "vendor-official"},
            {"vid": "0451", "pid": "6146", "label": "TI DFU", "source": "generic-example"},
        ]},
        "board_test": {"checks": {"calib_ledger": "CALIB-001"}, "board_sn": "SN-001"},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="S2 救砖链路 CB-01~CB-09 机械判定器")
    ap.add_argument("--evidence-dir", default=None, help="板端跑测证据目录")
    ap.add_argument("--config", default="SW/tools/s2_rescue_config.json")
    ap.add_argument("--out", default=None, help="判定结果 JSON 输出路径")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="只跑纯逻辑自测")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not args.evidence_dir:
        print("❌ 需要 --evidence-dir (或用 --selftest)", file=sys.stderr)
        return 3
    if not os.path.isdir(args.evidence_dir):
        print(f"❌ 证据目录不存在: {args.evidence_dir}", file=sys.stderr)
        return 3
    if not os.path.exists(args.config):
        print(f"❌ 配置不存在: {args.config}", file=sys.stderr)
        return 3
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    rep = judge_all(args.evidence_dir, cfg)
    rep["config"] = os.path.abspath(args.config)
    text = json.dumps(rep, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    if args.json:
        print(text)
    else:
        print_table(rep)
    return {PASS: 0, FAIL: 1, UNVER: 2}[rep["br01"]["result"]]


if __name__ == "__main__":
    sys.exit(main())
