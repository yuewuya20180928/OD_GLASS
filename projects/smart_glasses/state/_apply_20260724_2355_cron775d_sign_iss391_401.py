#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_2355_cron775d_sign_iss391_401.py
=========================================================
★cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-24 23:5x · ★★11 单独立复核签收★★

★★【★★本单做什么★★】★★
① ★**ISS-391 / ISS-392 / ISS-393 / ISS-394 / ISS-395 / ISS-396 / ISS-397 / ISS-398 /
   ISS-399 / ISS-400 / ISS-401** ★★11 条 (★全部属「板只改一次」纪律 ① 纯分析/作业包/闸类 ⇒ 零写板★)
   的 status: `fixing` → `verified` (★verify_by = main · ★main 本机独立复核·不抄任何 agent 报告★)
② 每条附【追加式 note_addendum】(★老字一字未删★): 本机实跑读数 + 边界双证 + ★main 地界待裁项的采纳值★
③ ★**签收后 sw-lead / mech-lead 两个槽位释放** ⇒ 下一轮 `advance.py` 可派 (★hw-lead 槽位由兄弟 job
   23:44 新开的 ISS-402 占着 ⇒ 不释放也不该释放★)

★★【★★纪律 (★本脚本自己守★)】★★
  ① ★**CAS 并发守卫**: 读-改-写窗口内若台账被第三方改过 ⇒ 零写盘退出
  ② ★**签收前置**: 11 条此刻必须都还是 `fixing` (★若已被别人签过 ⇒ 我的裁决会覆盖别人的 ⇒ 退出★)
  ③ 零写板 (板 md5/mtime(ns)/size 三项开工前后各打一次)
  ④ 零落表 (网表/脚表/BOM 逐字节未动)
  ⑤ 只改这 11 条的 status/verify_* 字段 + 追加 note_addendum (★其余条目逐字节不动·★落盘后逐条回验★)
  ⑥ 零外发 · 不代老板拍板 · 不改 PROJECT_TRACKER.md §0
"""
import hashlib
import os
import shutil
import sys
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(PROJ, "state/issue_log.yaml")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
NETLIST = os.path.join(PROJ, "HW/netlist_v1.csv")
PINS = os.path.join(PROJ, "HW/netlist_v1_pins.csv")
BOM = os.path.join(PROJ, "HW/BOM_v1.csv")
STAMP = time.strftime("%Y%m%d_%H%M")
VDATE = "2026-11-24 23:5x"

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_SIZE = 4940213
BOARD_MTIME_NS = 1793920037362193413

# ★★每条 = (闸路径, 裸跑 rc, selftest rc, selftest 末行, 签名理由)★★
VER = {
    "ISS-391": (
        "HW/check_fts_land_drill_same_batch.py", 0, 0, "ALL TESTS PASS",
        "★**闸判据层加固 + 夹具改真件现读** ⇒ D1/D2/D3 由「关键词命中」改「动作腿命中」(动作词+改动作+目标值三者绑定) ⇒ ★**阈值 0.71/1.27 未动·D4~D7 逐字未改**(机器核过) ⇒ ★**main 19:55 那个决定性实验 (删动作腿留解释括注 ⇒ 必须真红) 已固化进夹具 (用例 ① 与 ⑯)** ⇒ ★**今后谁把判据改松这两条立刻红**"),
    "ISS-392": (
        "SW/tools/check_sw_gate_chain_coverage.py", 0, 0, "ALL TESTS PASS",
        "★**SW 域闸门禁链覆盖率 + 第三道病闸基线漂移** ⇒ 把「哪道闸在链上/基线钉在谁身上」变成可判 ⇒ ★**裸跑 7/7 全绿·selftest 0/7 → 全绿** ⇒ ★**零改判据·零改既有闸阈值**"),
    "ISS-393": (
        "MECH/check_fts_vs_generic_courtyard_delta.py", 0, 0, "ALL TESTS PASS",
        "★**「通用库件 courtyard 被当成厂件」这条前提变成可算的差集** ⇒ 机器块量数 50 · G1~G7 全部通过 ⇒ ★**零写板·零落表·零挂链**"),
    "ISS-394": (
        "HW/check_seat_part_verdict_propagation.py", 1, 0, "ALL TESTS PASS",
        "★**裸跑 rc=1 是按设计** (★日志原话: K2 = 已闭 need 的答案仍指向被推翻的料号 ⇒ 要 main 落订正块; K3 = 未答 need 的选项全错 ⇒ 要 main 改选项★) ⇒ ★**红的是现状·不是闸故障** ⇒ ★**判据本身可信**"),
    "ISS-395": (
        "HW/check_gate10_concurrency_safety.py", 0, 0, "ALL TESTS PASS",
        "★**钉板闸⑩【并发跑必假红】这件事被机器化** ⇒ 裸跑 rc=0 (33 条 item 的 source_iss 全在 SOURCES 11 个来源单里) ⇒ ★**判据零削弱·阈值常量一字未动**"),
    "ISS-396": (
        "HW/check_fts_land_drill_same_batch_sbx.py", 0, 0, "ALL TESTS PASS",
        "★**FTS 改孔 `0.65 → 0.71` 的登记落盘 + 沙盒闸** ⇒ 裸跑 rc=0 ⇒ ★**日志原话: 「§4 #4 现状: WP02_BINDING[③] = (['B33_PIN_LAND_1P27'], []) ⇒ 显式覆盖令牌还没补 ⇒ ★P4 仍靠自动抽 ⇒ 落不落由 main 拍」** ⇒ ★**★main 裁决: 【不补显式令牌】(★自动抽本次已自动生效·补令牌是【冗余】·★真要补只能同板那一趟一起·★现在补 = 改真件一次★)** ★"),
    "ISS-397": (
        "MECH/check_fts_seat_sample_plan.py", 1, 0, "ALL TESTS PASS",
        "★**座体三量 (绝缘体高/外形宽/外形深) 的收样闸** ⇒ ★**日志原话: 「本闸的【预期读数】= rc=1 (红): 红的是【现状】(三量【实测档】仍 [0数据]·收样尚未发生) ⇒ ★**不许为了让它绿而放宽判据**」** ⇒ ★**★main 裁决: 维持红·判据一字不改·三量的收样必须与「板那一趟」同批(★那天才有样可打★)** ★"),
    "ISS-398": (
        "SW/tools/check_sw_ref_reachability_v2.py", 1, 0, "ALL TESTS PASS",
        "★**第三道病闸 `check_sw_ref_reachability_v2.py` 的自测基线无关化** ⇒ ★**核心目标已达成 (selftest 0/7 → 7/7 ALL TESTS PASS)** ⇒ ★**裸跑 rc=1 是按设计 (红因: `VBUS_DET_uA` 被当位号 ⇒ 是现状问题不是闸故障)** ⇒ ★**★main 裁决: 采用 agent 的【口径 C】(登记 `EXEMPT_LEDGER` 而不是改文档字面量·★改字面量不留漏检窗口★)·★判据前缀 md5 逐字未变 (3111dfb2…)** ★"),
    "ISS-399": (
        "MECH/check_mech_signed_append_ledger.py", 1, 0, "ALL TESTS PASS",
        "★**MECH 域【已签收件追加台账】的设计 + 自守闸** ⇒ ★**日志原话: 「预期读数 = rc=1 (红): 红的是【现状】(3 处陈旧 pin 归因不到台账) ⇒ ★**不许为了让它绿而放宽判据**」** ⇒ ★**★main 裁决: M-A 台账落 `MECH/SIGNED_APPEND_LEDGER.md` (★闸已按此实现·改常量即可)·M-B 3 处基线走台账登记值追平·M-C 【先落台账再挂链】(★先挂 = 往官方链挂一道永久红的闸★)·M-D 「追加式订正」合法但必须留原子记录(判据从「不许改」改成「不许**悄悄**改」)** ★"),
    "ISS-400": (
        "MECH/check_machine_block_pointer_resolvable.py", 1, 0, "ALL TESTS PASS",
        "★**「量完填回哪一格」的最后一米清账** ⇒ ★**日志原话: 「预期读数 = rc=1 (红): 红的是【现状】(扫描范围内有悬空/歧义/误指指针) ⇒ ★**不许为了让它绿而放宽判据**」** ⇒ ★**★main 裁决: Q5 = 「量完填回哪一格」的正式答案 = ★**唯一真槽 `degradation.measure_fill_back.*.measured` (★ISS-393 页 §6 登记的三条槽位名一个都不存在 ⇒ ISS-397 §9-④ 挂了两天那条问句即使答「改键名」也改到填不进去)★ ⇒ ★**三个候选落点没有一条通路 ⇒ 收样闸永远红在 B.6** ⇒ ★**本单不新起单·与「板那一趟」同批** ★"),
    "ISS-401": (
        "HW/check_hw_external_dep_closed.py", 0, 0, "ALL TESTS PASS",
        "★**HW 域外部依赖自查收口** (★三个总工里唯一没做过这件事的域★) ⇒ ★**5 条判据全绿** ⇒ ★**网表 109 行 TBD + 36 行 `[待原厂]` 全部改写成【自己查的结果 + 证据等级 + 降级方案】(★老板 2026-11-12 02:02 政策落地的第一条域级证据★) ⇒ ★**★main 裁决: q16_display_iface = `DSI TX (4-lane)` (★事实性闭合·已在 main 自己分片 pm.yaml 代录 answer·★不是代拍老板★)** ★"),
}

NOTE_TMPL = (
    "★★2026-11-24 23:5x cron 775d9893 (ARS45 继续执行后继计划) · main 独立复核签收 (★追加式·老字一字未删★)★★\n"
    "★**本机实跑读数 (★不抄任何 agent 报告·★日志全在 `state/.verify/r92/`★)★**: 新闸 `{gate}` 裸跑 rc={bare} · `--selftest` rc={st} · 末行 `{last}`\n"
    "★**签名理由**: {why}\n"
    "★**边界双证**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / mtime `2026-11-06 07:07:17.362193413` ⇒ **逐字节未动** (18 天) · 网表 `6aee500e…` · 脚表 `9174309d…` · BOM `5b999399…` ⇒ **零落表** ⇒ **零写板**\n"
    "★**交卷页在盘 (★占位符 0★) + 新闸在盘 + owner 分片已登记** ⇒ **零外发 · 零挂链 · 未代老板拍板 · 未改 PROJECT_TRACKER §0**\n"
    "★**签收后**: {slot}"
)

SLOT = {
    "hw-lead": "★hw-lead 槽位**未释放** (★兄弟 job fb67af40 23:44 新开 ISS-402 → hw-lead·★真在飞★) ★",
    "sw-lead": "★sw-lead 槽位**已释放** ⇒ 下一轮 `advance.py` 可派 (★铁律: 一个 agent 同时只允许一个写会话★) ★",
    "mech-lead": "★mech-lead 槽位**已释放** ⇒ 下一轮 `advance.py` 可派 (★铁律: 一个 agent 同时只允许一个写会话★) ★",
}


def md5_bytes(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def md5_file(p: str) -> str:
    return md5_bytes(open(p, "rb").read())


def main() -> int:
    # ---------- ① 零写板 / 零落表 (开工前) ----------
    st = os.stat(BOARD)
    if md5_file(BOARD) != BOARD_MD5 or st.st_size != BOARD_SIZE or st.st_mtime_ns != BOARD_MTIME_NS:
        raise SystemExit("★★板指纹与基线不符 ⇒ 零写盘退出")
    for p, base in ((NETLIST, "6aee500e60ba0732f83a9cf557ba90ab"),
                    (PINS, "9174309df1ec9411ac8e8d9e80ee386a"),
                    (BOM, "5b9993992405904a60ac96a020b375d8")):
        if md5_file(p) != base:
            raise SystemExit("★★真源表被改 ⇒ 零写盘退出: %s" % p)
    print("✓ 开工前: 板三证一致 + 三张真源表 md5 未变")

    # ---------- ② 读台账 (CAS 基线) ----------
    raw0 = open(LOG, "rb").read()
    md5_0 = md5_bytes(raw0)
    shutil.copy2(LOG, LOG + ".bak_%s_cron775d_sign_iss391_401" % STAMP)
    doc = yaml.safe_load(raw0.decode("utf-8"))
    issues = doc.get("issues") if isinstance(doc, dict) else doc
    by = {e.get("id"): e for e in issues if isinstance(e, dict)}
    before_n = len(issues)
    before_snapshot = {e.get("id"): md5_bytes(yaml.safe_dump(e, allow_unicode=True, sort_keys=False).encode())
                       for e in issues if isinstance(e, dict)}

    # ---------- ③ 签收前置: 11 条此刻必须都还是 fixing ----------
    owners = {}
    for iss in VER:
        e = by.get(iss)
        if e is None:
            raise SystemExit("★★台账里没有 %s ⇒ 零写盘退出" % iss)
        if e.get("status") != "fixing":
            raise SystemExit("★★%s 的 status 在我读的时候已是 %s (★不是我写的·可能是别人签收过★) ⇒ 零写盘退出"
                             % (iss, e.get("status")))
        owners[iss] = e.get("owner")

    # ---------- ④ 改这 11 条 ----------
    for iss, (gate, bare, st_rc, last, why) in VER.items():
        e = by[iss]
        e["status"] = "verified"
        e["verify_by"] = "main"
        e["verify_result"] = ("✅ verified (★main %s 本机独立复核 · 不抄任何 agent 报告★) ⇒ ★**新闸 `%s` 裸跑 rc=%d "
                              "(★%s★) + `--selftest` rc=%d · 末行 `%s`** ★ ⇒ %s ★ ⇒ ★**板 md5/mtime/size 三证逐字节未动 (18 天) "
                              "+ 网表/脚表/BOM md5 未变 ⇒ 零写板 · 零落表 · 零挂链 · 零外发** ★"
                              % (VDATE, gate, bare,
                                 "按设计判红 (★红的是现状·不是闸故障★)" if bare else "全绿",
                                 st_rc, last, why))
        e["verify_date"] = VDATE
        e["fix_ref"] = ("main %s 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·零挂链·零外发·未代老板拍板★)"
                        % VDATE)
        notes = e.get("note_addendum") or []
        if not isinstance(notes, list):
            notes = [notes]
        notes = list(notes) + [{
            "at": VDATE,
            "by": "main",
            "text": NOTE_TMPL.format(gate=gate, bare=bare, st=st_rc, last=last, why=why,
                                     slot=SLOT.get(owners[iss], "")),
        }]
        e["note_addendum"] = notes

    # ---------- ⑤ 落盘前 CAS 复核 ----------
    md5_now = md5_bytes(open(LOG, "rb").read())
    if md5_now != md5_0:
        raise SystemExit("★★CAS 失败: 台账在我读之后被改过 (★%s != %s★) ⇒ 有人并发写 ⇒ 零写盘退出·不覆盖别人的写 ★★"
                         % (md5_now[:12], md5_0[:12]))
    print("✓ CAS 通过 (md5 %s 未变)" % md5_0[:12])

    tmp = LOG + ".tmp_main_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=4096)
    os.replace(tmp, LOG)
    print("✓ 落盘: 11 条 status fixing→verified (★条数 %d→%d★)" % (before_n, len(issues)))

    # ---------- ⑥ 落盘后回验 ----------
    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    iss2 = doc2.get("issues") if isinstance(doc2, dict) else doc2
    by2 = {e.get("id"): e for e in iss2 if isinstance(e, dict)}
    bad = []
    for iss in VER:
        e = by2.get(iss) or {}
        if e.get("status") != "verified" or e.get("verify_by") != "main":
            bad.append((iss, e.get("status"), e.get("verify_by")))
    if bad:
        raise SystemExit("★★落盘后回验失败: %s" % bad)
    # 其余条目逐条 md5 不变
    after_snapshot = {e.get("id"): md5_bytes(yaml.safe_dump(e, allow_unicode=True, sort_keys=False).encode())
                      for e in iss2 if isinstance(e, dict)}
    drift = []
    for e in iss2:
        i = e.get("id")
        if i in VER:
            continue
        if before_snapshot.get(i) != after_snapshot.get(i):
            drift.append(i)
    if drift:
        raise SystemExit("★★落盘后: 非目标条目被改动 ⇒ %s" % drift[:10])
    print("✓ 落盘后回验: 11/11 verified + 其余 %d 条逐条 md5 未变" % (len(iss2) - len(VER)))

    st2 = os.stat(BOARD)
    if md5_file(BOARD) != BOARD_MD5 or st2.st_size != BOARD_SIZE or st2.st_mtime_ns != BOARD_MTIME_NS:
        raise SystemExit("★★收工后板指纹变了")
    for p, base in ((NETLIST, "6aee500e60ba0732f83a9cf557ba90ab"),
                    (PINS, "9174309df1ec9411ac8e8d9e80ee386a"),
                    (BOM, "5b9993992405904a60ac96a020b375d8")):
        if md5_file(p) != base:
            raise SystemExit("★★收工后真源表被改")
    print("✓ 收工后: 板三证 + 三张真源表 全部未变")
    return 0


if __name__ == "__main__":
    sys.exit(main())
