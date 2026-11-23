#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20260723_0545_cron775d_open_iss355.py —— main 开 1 单 (ISS-355 → sw-lead) + ISS-155 台账口径裁决

★本单只做 3 件 (★不动板·不改网表真源·不外发·不替老板拍板★):
  ① 开 ISS-355 (owner=sw-lead, status=open) —— 任务书 = state/dispatch_briefs/ISS-355_sw_rk3572_convert_script_落地.md
  ② ISS-155 台账口径裁决 (main 的裁决, 不是老板拍板): severity blocker → high + note 追加式留痕
     ★依据 = ISS-263 (rknn3-toolkit 1.2.0 支持 target_platform='rk3572') + ISS-353 (转换链已通 · 板端 [0数据])
  ③ 零 churn 落盘 (★只改 ISS-155 那一个 segment, 其余字节一字不动★)

★为什么开这一单 (事实全部本机实读, 不抄任何 agent 报告):
  · advance.py --json ⇒ internal=[] (hw-lead 名下 ISS-354 在飞 · sw-lead/mech-lead 域内 open=0)
  · sw-lead 自己交卷 (ISS-353) 写下 need `iss353_need_followup_convert_script_rk3572`:
    「主路线 (rknn3-toolkit 1.2.0 + rk3572) 还没落到脚本上」⇒ main 本机实读:
      SW/tools/rk3572_model_rebuild.sh L13/L86/L136 = target_platform=rk3576 · TOOLKIT_VER=2.3.2
      SW/RKNN_BENCH.md §2.2/§3 = toolkit2 2.3.2 + rk3576 + 产物落 /tmp
    ⇒ 纯脚本类 · 零写板 ⇒ 符合「板只改一次」纪律 (先派纯分析/脚本类)
"""
import os
import re
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
BRIEF = os.path.join(PROJ, "state/dispatch_briefs/ISS-355_sw_rk3572_convert_script_落地.md")
STAMP = time.strftime("%Y%m%d_%H%M")

B355 = open(BRIEF, encoding="utf-8").read()

TITLE_355 = (
    "★★[★新主线·PCB 线·模型链·rk3572 转换链落到脚本·纯脚本·零写板] ★★【ISS-353 交卷页自己写下的: 「口径清了 ≠ 实现改了」⇒ "
    "`SW/tools/rk3572_model_rebuild.sh` (L13/L86/L136) + `SW/RKNN_BENCH.md` §2.2/§3 仍锁在 toolkit2 2.3.2 + "
    "`target_platform='rk3576'` ⇒ 主路线 (rknn3-toolkit 1.2.0 + `target_platform='rk3572'`) 还没落到任何脚本上; 且 rknn3 产物是 "
    "`.rknn` + 同名 `.weight` 两件套 ⇒ 只拷 `.rknn` 一定失败 ⇒ 本单 = ① 转换/重建脚本切 rknn3 分支 (旧路线降为显式回退并标注已取代) "
    "② 两件套落盘 + sha256 + 缺 `.weight` 报错退出 ③ 文档追加式订正 ④ 「板到手一条命令出 PASS/FAIL」的降级脚本收口 + 自带闸 "
    "(--selftest 反向用例)】★★ ★**只改脚本与文档·不动板·不改网表真源·不改脚表/BOM·零落表·零外发·零采购·不代老板拍**★"
)

DESC_355 = (
    "★**main 2026-11-23 05:3x~05:4x 本机实读 (不抄任何 agent 报告)★** ⇒ ★**① ISS-353 (sw-lead, 已由 main 05:3x 签收落 verified) "
    "自己写下的三条 need 里, 有两条是本单的活**: `iss353_need_followup_convert_script_rk3572` (主路线还没落到脚本上) + "
    "`iss353_need_main_apply_caliber_patch` (★该补丁已过期: main 05:3x 实跑 `logs/iss353/apply_caliber_dispositions.py` dry-run ⇒ "
    "15 条条目里 13 条旧片段命中 0 次 ⇒ 那些文档已被别的会话清过 ⇒ 补丁的「必须恰好命中 1 次」校验直接判失败 ⇒ ★**不许再跑 --apply**★ "
    "⇒ 剩下 2 条在 `state/fragments/hw.yaml` L5226/L5227 = hw-lead 地界 ⇒ 转 hw-lead (main 另派)) + "
    "`iss353_need_main_decide_iss155_blocker` (★main 已裁: 降级成立 ⇒ 台账里 ISS-155 由 blocker 降为 high, note 留痕★) ★ "
    "★**② 本机实读三处旧路线**: `SW/tools/rk3572_model_rebuild.sh` L13/L86/L136 = `target_platform=rk3576` · 头部 "
    "`TOOLKIT_VER=2.3.2` · `SW/RKNN_BENCH.md` §2.2「工具链 rknn-toolkit2 2.3.2」/§3「target_platform rk3576 ✅」/ 产物落 `/tmp/rknn_bench/` "
    "⇒ ★**照它做的板端流程一定失败** ★ ★**③ 两件套**: rknn3-toolkit 1.2.0 产物 = `.rknn` + 同名 `.weight` ⇒ 只拷 `.rknn` 一定失败 "
    "⇒ 落盘/拷贝/sha256 三条规则都要改 ⇒ ★**脚本里要加自检: 缺 `.weight` ⇒ 报错退出** ★ ★**④ 官方层已坐实 (别重查)**: toolkit2 无 "
    "rk3572 target (README 支持列表) · rknn3-toolkit 1.2.0 支持 `rk3572` (README `Supported Platforms` + CHANGELOG V1.0.4 "
    "`Added RK3572 platform support (Beta)`) · RK3572 = `librknn3_api_native.so` vs RK3576/3588 = `librknn3_api_rkcp.so` ⇒ 官方无互换表述 "
    "⇒ 跨芯片接受性 [0数据] ⇒ 降级 = 板到手一条命令出 PASS/FAIL ★ ★**⑤ 已在盘别重做**: `logs/iss353/` 三份日志 · "
    "`SW/tools/iss263_rknn3_convert.py` · `SW/tools/rk3572_rknn3_board_smoke.sh` · `SW/tools/check_rk3572_target_caliber.py` "
    "(selftest 12/12) ★ ★**⑥ 边界**: 零写板 (md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` 双证) · "
    "零落表 (issue_log / 网表 / 脚表 / BOM / 原理图 / 任何既有闸脚本 都归 main 与其它域) · 只写 SW/tools 两个脚本 + SW 两份文档追加段 + "
    "HANDOFF + logs/iss355/ + sw.yaml 分片 (只走 frag_write.py) · 零外发 · 零采购 · 不代老板拍 · "
    "★**沙盒一律落项目盘 `$PWD/tmp` (不许写 /tmp: 2026-11-23 04:4x 实测配额已打满, 写 /tmp 会让闸门拿到假读数)★★"
)

NOTE_355 = (
    "★★2026-11-23 05:4x · cron 775d9893 (ARS45 继续执行后继计划) 开单 (★项目总工 main★) ★★ ★**开单依据**: ① `state/advance.py --json` ⇒ "
    "internal=[] (★hw-lead 名下 ISS-354 真在飞 · sw-lead/mech-lead 域内 open=0 ⇒ 队列断线★) ② sw-lead 自己交卷 (ISS-353) 留了 need "
    "`iss353_need_followup_convert_script_rk3572` 交 main 排期 ⇒ ★**本单就是那条 need 的落地产物** ★ ③ main 本机实读三处旧路线仍锁在 "
    "toolkit2 + rk3576 ⇒ ★**「板到手就跑」这条路今天还是断的** ★ ★**判定**: 纯脚本/文档类 · 零写板 · 零落表 · 零外发 · 零新增拍板项 "
    "(★ISS-155 的台账标签是 main 的口径裁决, 不是老板拍板★) · 派活时刻 2026-11-23 05:4x · ★**status 落 fixing ⇒ 兄弟 job 的 "
    "advance.py --json 看不见本单 ⇒ 不会重复派** ★ ★**另**: main 本轮同时实跑了 `logs/iss353/apply_caliber_dispositions.py` (dry-run) ⇒ "
    "★**该补丁已过期 (13/15 条旧片段命中 0) ⇒ 不许再 --apply**★ ⇒ 剩 2 条在 hw.yaml ⇒ 转 hw-lead 另派 ★"
)

ENTRIES = [
    {
        "id": "ISS-355",
        "title": TITLE_355,
        "severity": "high",
        "source_blocker": "ISS-353",
        "source_agent": "main",
        "desc": DESC_355,
        "owner": "sw-lead",
        "reporter": "main",
        "raised": "2026-11-23",
        "due": "2026-11-24",
        "status": "open",
        "external": "false",
        "task_brief": B355,
        "dispatched_at": None,
        "verify_by": "main",
        "verify_result": None,
        "note": NOTE_355,
    },
]

# ★★ISS-155 台账口径裁决 (main 的裁决; 追加式留痕; 状态仍 open, 只降严重度) ★★
ISS155_NOTE_APPEND = (
    " ★★2026-11-23 05:4x · ★**main 台账口径裁决 (★不是老板拍板★)**★★ ⇒ ★**ISS-155 由 `blocker` 降为 `high`** ★ ⇒ "
    "★**依据 (本机实读, 不抄任何 agent 报告)**: ① ISS-263 (★已 verified★) 实测 `rknn3-toolkit 1.2.0` 的 "
    "`config(target_platform='rk3572')` rc=0 · 反向自证 `rk3576` 抛 `ValueError: Unsupported target_platform 'rk3576'. Supported "
    "target_platform: gongga2, rk1820, rk1828, rk182x, rk1860, rk186x, rk3572` ⇒ ★**本单标题里的「rk3572 不是合法 target」这个前提"
    "已被新工具链打掉** ★ ② ISS-353 (★已 verified★) 实测转换链 4 步 rc=0 · 产物 249,360 B md5 `97a34fff0b855b92681f26627dba5354` "
    "· 与 ISS-263 三次逐字节一致 ⇒ ★**转换链这一环已通** ★ ③ ★**板端接受性仍 [0数据]** (本机 0 台 RK3572 设备) ⇒ 按老板 2026-11-12 "
    "02:02「不发信·全靠自己查资料」口径 ⇒ ★**降级方案 = 板到手一条命令出 PASS/FAIL** (`SW/tools/rk3572_rknn3_board_smoke.sh` 在盘) "
    "⇒ ★**板不来 ⇒ demo 路线不被这条卡住, 卡的是「验收何时做」** ★ ★**残留代价 (诚实登记)**: 板端 N1~N5 无数据 · "
    "转换脚本未切 rknn3 (★已开 ISS-355 → sw-lead 本机实跑★) · 跨芯片 runtime 不可互换 (RK3572 = `librknn3_api_native.so` vs "
    "RK3576/3588 = `librknn3_api_rkcp.so` ⇒ 官方无互换表述) ⇒ ★**本单保持 `open`** (★板端数据未到前不许关★) ⇒ ★**降的是「严重度」, "
    "不是「结论」; 标题原文一字未删, 保留作历史留档★ ⇒ ★**ISS-155 的历史叙述原文 (含「demo 头号卡点」字样) 保留 ⇒ 结论不再引用** ★"
)


def _seg_bounds(src: str, issue_id: str):
    i = src.find("\n- id: %s\n" % issue_id)
    if i < 0:
        raise SystemExit("★台账里找不到 %s" % issue_id)
    j = src.find("\n- id: ", i + 5)
    if j < 0:
        j = len(src)
    return i, j


def _patch_iss155(src: str):
    """★只改 ISS-155 这一个 segment: severity + note 追加 (★其余字节一字不动★)"""
    i, j = _seg_bounds(src, "ISS-155")
    seg = src[i:j]
    if "  severity: blocker" not in seg:
        raise SystemExit("★ISS-155 segment 里找不到 severity: blocker")
    seg = seg.replace("  severity: blocker", "  severity: high", 1)
    m = re.search(r"\n  note: '", seg)
    if not m:
        raise SystemExit("★ISS-155 segment 里找不到 note 字段")
    start = m.end()
    m2 = re.search(r"\n  [a-zA-Z_]+:", seg[start:])
    if not m2:
        raise SystemExit("★ISS-155 segment 里找不到 note 之后的下一个字段")
    field_end = start + m2.start()
    close = seg.rfind("'", start, field_end)
    if close < 0:
        raise SystemExit("★找不到 note 标量的收尾引号")
    esc = ISS155_NOTE_APPEND.replace("'", "''")
    seg = seg[:close] + esc + seg[close:]
    # ★自检: 解析回 YAML ⇒ severity/note 对得上, 其余字段一字不动
    before = yaml.safe_load(src[i:j])
    after = yaml.safe_load(seg)
    assert after.get("severity") == "high", "severity 改写失败"
    assert after.get("note", "").startswith(before.get("note", "")), "note 追加不是前缀保持"
    for k in before:
        if k in ("severity", "note"):
            continue
        assert before[k] == after.get(k), "★字段被误改: %s" % k
    return src[:i] + seg + src[j:], before, after


def main():
    src = open(LOG, encoding="utf-8").read()
    dup = [e["id"] for e in ENTRIES if ("\n- id: %s" % e["id"]) in src]
    if dup:
        print("★已在台账 ⇒ 不重复开单: %s" % dup)
        return 0
    chunk = yaml.safe_dump(ENTRIES, allow_unicode=True, sort_keys=False, width=100)
    if not src.endswith("\n"):
        chunk = "\n" + chunk

    # ★先做 ISS-155 的零 churn 手术 (★在追加新单之前做, 免得 seg 边界跟着挪★)
    patched, before155, after155 = _patch_iss155(src)

    shutil.copy2(LOG, LOG + ".bak_%s_cron775d_open_iss355" % STAMP)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(patched + chunk)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)

    # ★落盘后全量复核: 只有 ISS-155.severity/note 变了 + 新增 ISS-355 ★
    d = yaml.safe_load(open(LOG, encoding="utf-8"))
    items = d if isinstance(d, list) else d.get("issues", d)
    if isinstance(items, dict):
        items = list(items.values())
    ids = [i.get("id") for i in items]
    i155 = [i for i in items if i.get("id") == "ISS-155"]
    i355 = [i for i in items if i.get("id") == "ISS-355"]
    assert len(i155) == 1 and len(i355) == 1, "ISS-155/ISS-355 命中数不对"
    print("台账条数 = %d · 零重复 id = %s" % (len(ids), len(ids) == len(set(ids))))
    print("ISS-155: severity %s → %s · note 追加 %d 字符 (前缀保持 ✔)"
          % (before155.get("severity"), i155[0].get("severity"),
             len(i155[0].get("note", "")) - len(before155.get("note", ""))))
    print("ISS-355: owner=%s status=%s severity=%s task_brief=%d 字符"
          % (i355[0].get("owner"), i355[0].get("status"), i355[0].get("severity"),
             len(i355[0].get("task_brief") or "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
