#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260723_0735_main_decide_iss155_label.py
======================================================
main (项目总工) 的【台账裁决 · ISS-155 降级标签】
★为什么做这件事 (★ISS-353 交 main 裁的那条 need: `iss353_need_main_decide_iss155_blocker`★):
  ISS-155 的老题面问的是「用 rk3576 target 转的 .rknn 在 RK3572 上能不能跑通」⇒ ★**主路线早已不用
  rk3576 target** ⇒ 那条问法本身已过期 ⇒ 「demo 头号卡点」这个标签已经不成立 ⇒ 剩下的只是
  【板端接受性 [0数据] · 待板】⇒ ★**卡的是「验收何时做」, 不是「能不能做」** ★

★机器判决依据 (★全部是已签收的 verified 单 + main 自己本机复核·不抄 agent 报告★):
  · ISS-263 (已 verified): rknn3-toolkit 1.2.0 的 `config(target_platform='rk3572')` rc=0 · 转换 rc=0
  · ISS-353 (2026-11-23 05:3x main 签收 · 33 条验收线全绿): 全仓旧口径清零 + 板端降级 A/B/C 写死
  · ISS-355 (2026-11-23 07:2x main 签收 · 34 条验收线全绿): 转换脚本默认路线迁到 rknn3 + rk3572
  · ★main 2026-11-23 07:3x 本机复核: 产物真在盘 (`SW/artifacts/models/yolov5n-sim_heads_rk3572_int8_heads.rknn`
    md5 `97a34fff0b855b92681f26627dba5354` 249,360 B + `.weight` md5 `7c04da4f3aa02772651fcbd40c0f2020` 1,960,448 B
    · mtime 2026-11-23 05:48 ⇒ 新默认路线真跑过) ★

★边界:
  · 只改 ISS-155 这一条 (owner=main ⇒ main 地界) · 不关单 (板端仍未验) · 不新增拍板项 · 不代老板拍
  · 老题面与老 note 逐字保留 (★追加式·只改标签/severity/due + 追加裁决段★)
用法:
  python3 state/_apply_20260723_0735_main_decide_iss155_label.py --check-only
  python3 state/_apply_20260723_0735_main_decide_iss155_label.py --apply
"""
import os
import re
import shutil
import sys
import time

import yaml

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOG = os.path.join(PROJ, "state/issue_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")
ISSUE = "ISS-155"

TITLE_SUFFIX = (" ★★【2026-11-23 07:3x main 裁决 · ★★降级 · 本单不再是 demo 头号卡点 · 余项 = "
                "转换链已通 / 板端接受性 [0数据]·待板★★】★**老题面 (rk3576 target 那条问法) 保留作历史留档·"
                "结论不再引用** ★")

NOTE_ADD = (
    " ★★【2026-11-23 07:3x main 裁决 · 降级: 本单不再是 demo 头号卡点 · 余项 = 板端接受性 [0数据]·待板】★★"
    " ★**① 题面已过期**: 老题面问的是「用 rk3576 target 转的 .rknn 在 RK3572 上能不能跑通」⇒ ★**主路线早已不用 "
    "rk3576 target** ⇒ 那条问法本身作废 (保留作历史留档·结论不再引用) ★ "
    "★**② 转换链已通 [实测]**: rknn3-toolkit 1.2.0 的 config(target_platform=rk3572) rc=0 (ISS-263) + "
    "转换脚本默认路线已迁 (ISS-355 verified: ROUTE_DEFAULT=rknn3 / TARGET_PLATFORM_DEFAULT=rk3572) + "
    "产物真在盘 (md5 97a34fff… 249,360 B + .weight 7c04da4f… 1,960,448 B · mtime 2026-11-23 05:48 实跑) + "
    "全仓旧口径已清零 (ISS-353 verified · 口径闸 rc=0) ★ "
    "★**③ 剩下的是什么**: ★**只有板端接受性 [0数据]** ⇒ 降级 A/B/C 已写死 (板到手一条命令出 PASS/FAIL · "
    "板不来 demo 不停只登记待板 · 板端拒收三档代价) ⇒ ★**卡的是「验收何时做」, 不是「能不能做」** ★ "
    "★**④ 裁决**: severity blocker → high · 题面加降级标签 · ★**status 保持 open (板端仍未验·不关单)** · "
    "★**due 顺延到 2026-11-27** (★顺延的是【催办时间】不是【已定时间】· ★绑定「板到手」⇒ 与 ISS-169/ISS-354 "
    "那一趟同批★) ★ "
    "★**⑤ 未代老板拍**: 本裁决只在 main 地界内 (owner=main) 改台账标签与 severity ⇒ ★**不涉及任何老板拍板项, "
    "不新增拍板项** ★ "
    "★**⑥ 证据**: state/_apply_20260723_0720_main_sign_iss355.py (34 条验收线全绿) · "
    "state/_apply_20260723_0535_main_sign_iss353.py (33 条全绿) · "
    "HANDOFF/2026-11-23_sw-lead_ISS355_转换脚本迁主路线.md · "
    "HANDOFF/2026-11-23_sw-lead_ISS353_rk3572目标口径清账.md ★"
)


def segment(src, issue):
    i = src.find("\n- id: %s" % issue)
    if i < 0:
        return None, None
    j = src.find("\n- id: ", i + 10)
    if j < 0:
        j = len(src)
    return i, j


def main():
    apply = "--apply" in sys.argv
    src = open(LOG, encoding="utf-8").read()
    i, j = segment(src, ISSUE)
    print("=" * 78)
    print("★ ISS-155 台账标签降级裁决 (main 地界 · owner=main)")
    if i is None:
        print("  ★段没定位到 ⇒ 不落盘")
        return 1
    seg = src[i:j]
    if "demo 头号卡点" not in seg:
        print("  ★老标签已不在 (已被改过) ⇒ 幂等退出")
        return 0
    new = seg
    # ① 题面追加降级标签 (老题面逐字保留)
    k = new.find("\n  severity:")
    head = new[:k].rstrip("\n")
    tail = new[k:]
    new = head + TITLE_SUFFIX + "\n" + tail
    # ② severity: blocker → high
    new = new.replace("\n  severity: blocker\n", "\n  severity: high\n", 1)
    # ③ due 顺延 (绑定「板到手」)
    new = new.replace("\n  due: '2026-11-19'\n", "\n  due: '2026-11-27'\n", 1)
    # ④ note 末尾追加裁决段 (单引号 YAML 标量 ⇒ 追加内容里不能出现单引号)
    # ★★必须按 YAML 单引号标量的真实结束位置插入 (★内层单引号是成对写成 ''·所以要跳过成对引号★) ★★
    nm = re.search(r"\n  note: '", new)
    if not nm:
        print("  ★note 段没定位到 ⇒ 不落盘")
        return 1
    p = nm.end()          # 标量内容起点
    while True:           # ★扫描到未成对的收尾单引号★
        q = new.find("'", p)
        if q < 0:
            print("  ★note 标量没找到收尾单引号 ⇒ 不落盘")
            return 1
        if q + 1 < len(new) and new[q + 1] == "'":
            p = q + 2      # ★成对的内层引号 ⇒ 跳过 ★
            continue
        break
    note_body = new[nm.end():q]
    new = new[:nm.end()] + note_body + NOTE_ADD + new[q:]
    # ⑤ fix_ref 补证据
    new = new.replace("\n  fix_ref: SW/RKNN_BUILD_ENV_RECOVERY.md §2 · HW/PART_ALTERNATIVES_REGISTRY.md §1\n",
                      "\n  fix_ref: SW/RKNN_BUILD_ENV_RECOVERY.md §2 · HW/PART_ALTERNATIVES_REGISTRY.md §1 · "
                      "state/_apply_20260723_0735_main_decide_iss155_label.py · "
                      "state/_apply_20260723_0720_main_sign_iss355.py · state/_apply_20260723_0535_main_sign_iss353.py\n", 1)
    # ── 校验 (改后逐条对拍) ──
    checks = []
    checks.append(("老题面逐字保留 (原问题仍在)", "[demo 头号卡点] rk3572 不是 rknn-toolkit2 合法 target" in new))
    checks.append(("追加降级标签", "转换链已通 / 板端接受性 [0数据]·待板" in new))
    checks.append(("severity blocker → high", "\n  severity: high\n" in new))
    checks.append(("status 仍 open (不关单)", "\n  status: open\n" in new))
    checks.append(("due 顺延到 2026-11-27", "\n  due: '2026-11-27'\n" in new))
    checks.append(("裁决段写入 note", "main 裁决 · 降级" in new))
    checks.append(("老 note 前缀逐字保留", "note: '2026-11-02 20:2x。" in new))
    checks.append(("老 note 结尾仍在 (追加而非替换)", "★**顺延的是【催办时间】, 不是【已定时间】** ★" in new))
    for name, ok in checks:
        print("  %s %s" % ("✅" if ok else "❌", name))
    if not all(c[1] for c in checks):
        print("  ★有红项 ⇒ 不落盘")
        return 1
    if not apply:
        print("  ⇒ --check-only: 不落盘")
        return 0
    out = src[:i] + new + src[j:]
    # ★改前先做 YAML 解析验证 (落盘前必须能解析) ★
    try:
        d = yaml.safe_load(out)
        items = d if isinstance(d, list) else d.get("issues", d)
        ids = [x.get("id") for x in items]
        assert ISSUE in ids and len(ids) == len(set(ids)), "id 重复或找不到"
    except Exception as e:
        print("  ★落盘前 YAML 解析失败 ⇒ 不落盘: %s" % e)
        return 1
    bak = LOG + ".bak_%s_main_decide_iss155" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(out)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    print("  ★已落裁决: ISS-155 severity blocker → high · 题面加降级标签 · due → 2026-11-27 · status 仍 open · 备份 %s" % bak)
    return 0


if __name__ == "__main__":
    sys.exit(main())
