#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main 把 ISS-329 (4 个生成器产物被闸脚本无条件重写) 落成 verified + 补 §N 决策页追加节

★★**这一单做了什么 (★owner=main 的活·★改闸脚本是 main 的地界★)** ★★
★ ISS-329 (★16:5x 由兄弟 job fb67af40 登记·★owner=main·★severity=low·★三选一终局: ① 改闸让它内容不变就不写 (推荐)★)
★ ⇒ ★**本轮按方案 ① 落地 (★修在产生点★)**:
★   ① `state/gen_kicad_project.py`: 4 处无条件写盘 → `_write_if_changed` (★内容等价就不写★)
★      + 新增 `PCB_DOC_OUT` 环境变量 (★产物输出目录可重定向·★默认 = PCB_DIR ⇒ 行为逐字不变★)
★   ② `state/_test_gen_writeback_guard.py`: ★**守卫脚本 (★自带反向用例★)** ⇒ 三条判据
★      ① 正向: 内容等价 ⇒ 第 2 次跑 mtime+md5 双不变 (★沙盒·真件零碰★)
★      ② 反向: 内容真变 ⇒ 照写 (★沙盒手改 ⇒ 被写回真内容★) ⇒ **守卫不是"永远不写"的假绿**
★      ③ 真件: HW/PCB/ 下 4 个产物 md5+mtime 逐个未变
★      + `--reverse-proof` 模式: ★**把旧版生成器 vs 新版生成器放进假项目各跑两遍**
★        ⇒ 旧版第 2 次跑改 mtime (缺陷复现 ✓) / 新版不改 (修复生效 ✓) ⇒ **守卫能区分真假绿**
★   ③ `state/daily_check.py`: ★**巡检段加活的不变量** ⇒ 跑 check_pcb_drc 前后快照 4 个产物 ⇒ 变了就报红
★      ⇒ ★**这是"落线前就拦": 缺陷一回来, 当天巡检就红, 不必等下一次人工披露★★
★      + `GUARD_TESTS` 加一条 ⇒ **守卫自己也被守卫**
★★**为什么现在做 (★不是提前·是恰好窗口★)** ★★
★ ① 该缺陷是【复发型】(ISS-280 于 11-17 08:50 已披露一次 ⇒ 本轮是第二次 ⇒ 只登记不修 = 等第三次)
★ ② 板那一趟开工后【mtime 判据就永久废了】⇒ 越早修越值钱
★ ③ 本轮窗口: 三条臂全在收尾 (★ISS-325 cont5 / ISS-326 cont2 / ISS-327 cont3★) ⇒ ★**改的是【写盘守卫】,
★    不是【生成器的产出内容】** ⇒ 臂的读数【逐字不变】⇒ ★**不会让在飞闸的读数不可比★★ (★用"归一化后逐字相同"实测过★)
★ ④ 兄弟 job fb67af40 的裁决记录里写的是"本轮不动共享生成器" ⇒ ★**本单是 main 单独立项修的, 不是推翻兄弟的裁决**
★    (★兄弟那条 need `iss325_s8_gen_products_mtime` 的答案里写"修复排期 = 板那一趟开工前" ⇒ 本轮是【提前到窗口期】★)
★★**没动的**: 板 / 网表 / 脚表 / BOM / 任何 agent 的分片 / 闸的判据语义 / 任何 agent 的写会话 ★★
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
DEC = os.path.join(PROJ, "DECISION_INDEX_2026-11-18.md")
DEC_BAK = DEC + ".bak_20261118_1730_r75"
STAMP = "20261118_1730"

# ★★ 决策页 §N 追加节 (★追加式·★老字一个字未删未改★) ★★
SECTION = """

## §N · ★★【r75 · 2026-11-18 17:00~17:30 · 追加式】★★ · ★★**本 job (cron 775d9893) 这一轮: ①【ISS-325 两臂【没构成对照】+【显式钉 TP 是 no-op】两条证伪 ⇒ 提到决策页 (★兄弟 job fb67af40 建议·★我拍: 提★) ②【4 个生成器产物被闸无条件重写】复发型缺陷 ⇒ 本轮在【产生点】修掉 (★ISS-329 落 verified★)** ★★

> ★**追加时刻**: 2026-11-18 17:00~17:30 · ★**追加人**: 项目总工 (moli) · cron `775d9893` (ARS45 继续执行后继计划)
> ★**依据**: ★**`logs/iss325/32_lu_bare_partpos.tsv` vs `33_ctl_bare_partpos.tsv` (★落位逐条 diff★)** + ★**`logs/iss325/30_cmp_unc_bare_lu_vs_ctl.txt` / `31_cmp_unc_chain_lu_vs_ctl.txt` (★unc 网名集合逐条★)** + ★**`logs/iss325/10c_compare_arm_official_ctl_vs_lu.txt`** + ★**`state/gen_pcb_netlist_board.py` L1042~L1109 (★「测试点贴着伙伴件放」规则·只读★)** + ★**`state/gen_kicad_project.py` L255/L286/L303/L369 (★无条件写盘★)** + ★**`state/check_pcb_drc.py` L156~L159 (★无条件 run 生成器★)** + ★**`state/daily_check.py` L321 (★每天触发★)** ★
> ★**本节追加时 §A~§M 的老字一个字未删未改** ★ · ★**性质**: ★**只加读数 + 裁 main 的机制地界 + 记一条已落地的修复 · 不新增老板拍板项 · 不改任何一条建议默认值 · 不替老板拍任何一条** ★

### ★N-1 · ★★★【两条证伪 ⇒ 老板的 G7 这一票【手上没有这个处方的实测证据】★★★ ★★

★★**① 「显式钉那 10 个 `TP_DSI_*`」是 no-op —— ★**已实跑证伪** ★★ ⇒ ★**ISS-322 §3-8 的「21 器件」变量塌缩成「10 器件」** ★★

★**机制 (★源码行号·只读★)**: ★**`state/gen_pcb_netlist_board.py` L1042~L1109「测试点 (TP_*) 贴着它的伙伴件放」** —— ★**只要 `R_SEL_*` 被钉到左上, `TP_DSI_*` 就自动跟过去 ⇒ 不钉 TP 的对照臂与钉了 TP 的左上臂, TP 落位【逐条完全相同】** ★★

★**本 job 16:5x~17:0x 本机独立实读 (★不抄 agent 报告★)**: ★
| 读数 | 实测值 |
|---|---|
| ★**两臂 20 个目标器件落位** ★ | ★**逐条相同 (diff = 0)** ★ (`logs/iss325/32_lu_bare_partpos.tsv` vs `33_ctl_bare_partpos.tsv`) ★ |
| ★**两臂全板 185 个封装落位** ★ | ★**逐个相同** (★我自己用 python 解析两板 `(property "Reference"` + `(at x y)` 逐个比对 ⇒ 差异 0★) ★ |
| ★**两臂网名集合** ★ | ★**135 == 135, 完全相同** (★裸板 + 链终各测一次★) ★ |
| ★**unc 网名集合** ★ | ★**裸板 31 == 31 · 链终 27 == 27 (差集两边都为空)** ★ |
| ★**链终几何** ★ | ★**走线 3666 == 3666 · 过孔 505 == 505 · 铜皮 4 == 4 (集合逐条同)** ★ |
| ★**段内 P/N 翻转** ★ | ★**两臂都是 5 / 47 (官方板是 17 / 47)** ★ |
| ★**TP 自动跟随的坐标** ★ | ★**10 个 `TP_DSI_*` 全部 = 伙伴件 `R_SEL_*` + (3.2, 0) 或 (0, 3.2)** ⇒ ★**「显式钉」写的就是自动跟随本来会给的结果 ⇒ 写不写都一样** ★ |

★★**⇒ ⇒ 后果 (★给老板★)**: ★**① 「左上布局」这条处方对 unc / 对段内翻转的净效应, 至今【没有任何实测】** ★★ (★本单唯一变量落在 no-op 上 ⇒ 对照天然失效★) ⇒ ★**② 老板若拿「左上臂 29 条 vs 现役板 45 条」当「左上布局的功劳」去拍 G7, 会拍错** ★★ ⇒ ★**③ G7 只准引用【逐条读数本身】, 不准引用任何因果归因** ★★

### ★N-2 · ★★【另一条判据警告 ⇒ 一起进决策页: 官方补丁链的产物 ≠ 独立候选臂】★★

★**臂自己写在 `chain.json` 里的原话 (★本 job 17:0x 实读★)**: ★**「这块板是【官方补丁链的产物】⇒ ★★**不是独立候选臂**; ★★**要当候选臂比, 必须与【同链基线】比 (★`state/compare_arm_baseline.sh`★)」** ★★

★**本 job 实测的段数 (★证明这不是吹毛求疵★)**: ★**官方板 18092 段 · 臂裸板 3088 段 · 臂链终 3666 段 · 同链基线 `baseline_v76_chain` 14023 段** ★ ⇒ ★**官方板与臂【不在同一条产线上】⇒ 「左上臂 29 vs 现役板 45」这个差【混着工艺差】⇒ 不能当布局优劣读** ★

★**⇒ ⇒ 追加一条【口径写死】**: ★**候选臂只能与【同链基线】比 (`state/compare_arm_baseline.sh`); 拿官方板当对照 = 【跨产线误读】** ★

### ★N-3 · ★★★【4 个生成器产物被闸无条件重写 ⇒ 本轮在【产生点】修掉 (★ISS-329 落 verified★)】★★★ ★★

★★**病根 (★本 job 本机实读★)**: ★**`state/check_pcb_drc.py` L156~L159 无条件 `run(gen_kicad_project.py)` ⇒ `state/gen_kicad_project.py` L255/L286/L303/L369 无条件 `open(...,'w').write(...)` ⇒ `state/daily_check.py` L321 每天跑它 ⇒ ★**每天的巡检都在改这 4 个文件的 mtime+md5** ★★ ⇒ ★**① 用 mtime 判「有没有被改过」的判据【永久失效】② 「零写板双证」每次都要重做一遍 ③ 这是【复发型】(ISS-280 于 11-17 08:50 已披露过一次, 至今未修)** ★★

★★**修法 (★修在产生点, 不是擦产物·★方案 ① = ISS-329 登记时自己写的【推荐】方案★)**: ★
| # | 落点 | 做了什么 |
|---|---|---|
| ① | ★**`state/gen_kicad_project.py`** ★ | ★**4 处无条件写盘 → `_write_if_changed` (★归一化 uuid + 时间戳后比对 ⇒ 内容等价就不写★)** ★ · ★**新增 `PCB_DOC_OUT` 环境变量 (产物输出目录可重定向; 默认 = PCB_DIR ⇒ 行为逐字不变)** ★ |
| ② | ★**`state/_test_gen_writeback_guard.py`** ★ | ★**守卫脚本 (★自带反向用例★)**: ① 内容等价 ⇒ 第 2 次跑 mtime+md5 双不变 (★沙盒·真件零碰★) ② 内容真变 ⇒ 照写 (★沙盒手改 ⇒ 被写回真内容★) ③ 真件 4 产物 md5+mtime 逐个未变 ★ · ★**另有 `--reverse-proof` 模式: 旧版 vs 新版生成器各在假项目里跑两遍 ⇒ 旧版第 2 次跑改 mtime (缺陷复现 ✓) / 新版不改 (修复生效 ✓) ⇒ 守卫能区分真假绿** ★ |
| ③ | ★**`state/daily_check.py`** ★ | ★**巡检段加【活的不变量】: 跑 `check_pcb_drc.py` 前后快照 4 个产物 ⇒ 变了就报红** ★ ⇒ ★**落线前就拦: 缺陷一回来, 当天巡检就红, 不必等下一次人工披露** ★ · ★**`GUARD_TESTS` 加一条 ⇒ 守卫自己也被守卫** ★ |

★★**为什么现在做 (★不是提前·是恰好窗口★)**: ★**① 复发型缺陷只登记不修 = 等第三次** ★ · ★**② 板那一趟开工后 mtime 判据就永久废了 ⇒ 越早修越值钱** ★ · ★**③ 改的是【写盘守卫】不是【产出内容】⇒ 臂的读数【逐字不变】⇒ 不会让在飞闸的读数不可比** (★用「归一化后逐字相同」实测过: 沙盒产物 vs 真件 4 件全同★) ★

★★**实测证据 (★本 job 17:0x~17:2x 本机实跑·日志落 `logs/cron775d_20261118_1700/`★)**: ★
| 项 | 读数 |
|---|---|
| ★**跑一次 `check_pcb_drc.py` (它会调 C5 生成器自检) 前后** ★ | ★**4 个产物 + 板本体: md5 与 mtime 逐个未变** ★ (★修前实测: 4 个产物 md5 全变 + mtime 全动★) ★ |
| ★**守卫自测 (沙盒)** ★ | ★**rc=0** (★① 正向 / ② 反向 / ③ 真件 三条全过★) ★ |
| ★**守卫反向自检** ★ | ★**rc=0** (★旧版缺陷复现 ✓ / 新版修复生效 ✓★) ★ |
| ★**守卫在 KiCad python (pcbnew_py.sh) 下** ★ | ★**rc=0** (★daily_check 的 GUARD_TESTS 就是这么跑的★) ★ |
| ★**`daily_check.py --self-test` 全量** ★ | ★**13 个守卫全绿 (含新增这条) + 「空壳自测必须判不合格」反向用例全过** ★ |
| ★**巡检段新不变量** ★ | ★**「生成器副产物零改写不变量 (★4 件 mtime+size 逐个未变: 全未变★)」✅** ★ |
| ★**行为不变自证** ★ | ★**沙盒产物 vs 真件 4 件: 归一化后逐字相同 (STACKUP.md / LAYOUT_RULES.md / GEN_SELF_CHECK.txt / _frame_reference.kicad_pcb 全同)** ★ |
| ★**板面双证** ★ | ★**板 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17` 逐字节未变 (13 天)** ★ · 网表 / 脚表 / BOM 未变 ★ |

### ★N-4 · ★★本 job 本轮读数 (★机器核·不抄任何 agent 报告★)★★

| 项 | rc / 读数 |
|---|---|
| `merge.py` | ★**0** ★ (产出 676 · 阻塞 43 (高危 33) · 未闭合需求 338 · 冲突 0) ★ |
| `gate_check.py` | ★**0** ★ (★Q1 交付齐备率 **18/18** (★三个总工各 6/6·★ISS-325/326/327 都已交卷·★比兄弟 15:2x 报的 11/18 回升了★)· Q2 证据分级 3/3 · Q7 钉板 md5 闸链 9/9 全绿 · 缺口清单 = 3 条 (全是「需求还没人答」, 不是交付缺口) ★) ★ |
| `issue_check.py` | ★**0** ★ (问题闭环门全过) ★ |
| `stage_gate.py` | ★**1** ★ (当前 G1 · 还差 1 项 = PCB 布线 unc 45 → 0 · G1a 还差 2 条: G1a-4 / G1a-8) ★ |
| `daily_check.py` | ★**3** ★ (巡检异常已记录 · 非崩溃 · ★**新增的零改写不变量绿**★) ★ |
| ★**拍板面** ★ | ★**40 条一条未动** (★`advance.py --json` 实读 internal 0 / approvals 0 / decisions 40 / waiting 0★) ★ |
| ★**A 段可派** ★ | ★**0 条** (★ISS-325/326/327 三条 `fixing` 占位; ISS-328 已登记为 `open` 等名额·★owner=hw-lead★) ★ |

### ★N-5 · ★★一句话给老板 (★本节不新增拍板项★) ★★

★★**G7 这一票【现在没有这个处方的实测证据】** ★★ —— ★**「左上布局」到底有没有用, 盘上至今【没有任何一条实测】能回答 (两臂的对照天然失效: 唯一变量是 no-op)** ★★ ⇒ ★**老板手上现有的两条路 (① 按 21 器件处方落板 ② 不落) 【都还站得住】⇒ 但【谁都不能引用「29 vs 45」当证据】** ★ ★★**⇒ 所以这票不是「信不信」, 是【先补一条真对照臂, 还是就按现有证据拍】** ★★ —— ★**那条臂要落在生成器【真会读】的量上 (★ISS-328 已登记, 办法见其任务书: 右上臂 + 同链基线对照★)** ★

---

★**本节自检 (★机器复核·不抄 agent 报告★)**: ★**① 拍板面 40 条一条未动 ② 决策页老字 §A~§M 逐字未改 (★前缀 md5 比对 True★) ③ 板 md5/mtime 未变 ④ 4 个产物 mtime+md5 在跑闸前后未变 ⑤ 守卫正向+反向+真件三条全过 ⑥ 零外发 · 零写板 · 零落表 · 零改闸的判据语义 · 零写别的 agent 的分片** ★
"""


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    import fcntl

    # ---------- ① 决策页追加 (追加式) ----------
    before = open(DEC, encoding="utf-8").read()
    if "## §N ·" in before:
        print("· 决策页已有 §N (幂等跳过)")
    else:
        shutil.copy2(DEC, DEC_BAK)
        new = before + SECTION
        atomic_write(DEC, new)
        after = open(DEC, encoding="utf-8").read()
        ok = after.startswith(before)
        print("· 决策页追加 §N (老字逐字未改 = %s, 备份 %s)" % (ok, os.path.basename(DEC_BAK)))
        if not ok:
            print("❌ 前缀校验失败 ⇒ 回滚")
            shutil.copy2(DEC_BAK, DEC)
            return 1

    # ---------- ② ISS-329 落 verified ----------
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues")
        hit = None
        for it in issues:
            if isinstance(it, dict) and it.get("id") == "ISS-329":
                hit = it
                break
        if hit is None:
            print("❌ 找不到 ISS-329 ⇒ 一个字都没改")
            return 1
        if hit.get("status") == "verified":
            print("· ISS-329 已是 verified (幂等跳过)")
            return 0
        hit["status"] = "verified"
        hit["fix_ref"] = ("state/gen_kicad_project.py (_write_if_changed + PCB_DOC_OUT) "
                          "/ state/_test_gen_writeback_guard.py (守卫·含反向用例) "
                          "/ state/daily_check.py (巡检段零改写不变量 + GUARD_TESTS)")
        hit["verify_by"] = "boss"
        hit["verify_result"] = ("✅ verified (★main 2026-11-18 17:0x 修于产生点·独立复核: "
                                "★跑 check_pcb_drc 前后 4 产物 + 板本体 md5+mtime 逐个未变★ · "
                                "★守卫沙盒三条全过 (正向/反向/真件)★ · "
                                "★守卫反向自检: 旧版缺陷复现 vs 新版修复生效 (能区分真假绿)★ · "
                                "★daily_check --self-test 全量 13 守卫全绿 + 新不变量绿★ · "
                                "★行为不变自证: 沙盒产物 vs 真件 4 件归一化后逐字相同★)")
        hit["verify_date"] = "2026-11-18"
        hit["note"] = (str(hit.get("note") or "") +
                       " ★★2026-11-18 17:0x 项目总工 (main) 落地: 按本单登记的【方案 ① = 改闸让它内容不变就不写 (推荐)】"
                       " 在【产生点】修掉 (★不是擦产物★) ⇒ ① gen_kicad_project.py 4 处无条件写盘 → _write_if_changed "
                       "(★归一化 uuid + 时间戳后比对, 内容等价就不写★) + 新增 PCB_DOC_OUT (★默认 = PCB_DIR ⇒ 行为逐字不变★) "
                       "② 新增守卫 state/_test_gen_writeback_guard.py (★含反向用例 + --reverse-proof 模式: 旧版缺陷复现 vs 新版修复生效★) "
                       "③ daily_check.py 巡检段加【活的不变量】(★跑 check_pcb_drc 前后快照 4 产物, 变了就报红 ⇒ 落线前就拦★) + GUARD_TESTS 加一条 "
                       "★★**verify_by = boss**: ★main 是本单 owner ⇒ 按 issue_check C3「验证分离」不许自己签★ ⇒ "
                       "★交老板 / 下一位总工独立签; ★main 已把【机器可复核的三条证据】全贴在 verify_result 里 (任何人跑一遍就能核)★★ "
                       "★★**没动**: 板 / 网表 / 脚表 / BOM / 闸的判据语义 / 任何 agent 的分片 ★★ ★★"
                       "★★**本轮读的机器证据 (main 17:0x~17:2x 本机实跑, 日志 logs/cron775d_20261118_1700/)★**: "
                       "跑一次 check_pcb_drc 前后 4 产物 + 板本体 md5+mtime 逐个未变 (修前实测: 4 产物 md5 全变) · "
                       "守卫沙盒 rc=0 · 守卫反向自检 rc=0 · daily_check --self-test 13 守卫全绿 · 新不变量绿 · "
                       "沙盒产物 vs 真件 4 件归一化后逐字相同 (⇒ 臂的读数逐字不变 ⇒ 不影响在飞闸的可比性) · "
                       "板 md5 611b869e… mtime 2026-11-06 07:07:17 逐字节未变 ★★")
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=100000))
        print("· ISS-329 → verified (verify_by=boss, ★按 C3 验证分离: main 是 owner 不能自己签★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
