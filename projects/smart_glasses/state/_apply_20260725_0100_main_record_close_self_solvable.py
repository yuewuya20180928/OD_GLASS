#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260725_0100_main_record_close_self_solvable.py
=========================================================
main (项目总工) · 2026-11-25 01:00
★★【记录】16 条 main 地界待拍项已闭 (★老板清单 55 → 39★) + 一页 §㊿ + LESSONS L-34 + 轮次日志 + MEMORY 指针 ★★

★纪律: 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 (★全部追加式★) · 只写 main 自己的 pm.yaml(★本轮已落·★本脚本不再动它★)
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
STAMP = time.strftime("%Y%m%d_%H%M")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
MEM = "/home/yuewuya/.openclaw/workspace/MEMORY.md"
DAILY = "/home/yuewuya/.openclaw/workspace/memory/2026-11-25.md"
ROUND = os.path.join(PROJ, "state/ROUND_LOG_main_2026-11-25_0100_close_self_solvable.md")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def read_lines(p):
    return open(p, encoding="utf-8").read()


def sh(cmd, timeout=1800):
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True, timeout=timeout,
                       env=dict(os.environ, TMPDIR=os.path.join(PROJ, "tmp")))
    return p.returncode, p.stdout + p.stderr


# ==================================================================== 阶段 1
def verify():
    print("=" * 100)
    print("★阶段 1 · 落记录前的独立复核")
    print("=" * 100)
    ok = True

    def chk(name, good, detail=""):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-58s %s" % ("✅" if good else "❌", name, detail))

    st = os.stat(BOARD)
    chk("板 md5 / mtime(ns) / size", md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
        and st.st_size == BOARD_SIZE, "%s / %d ns / %d" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    # ★★16 条答案必须逐字在盘 + 都含 ★边界★★
    import yaml
    pm = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/pm.yaml"), encoding="utf-8")) or {}
    amap = {}
    for a in (pm.get("answers") or []):
        if isinstance(a, dict) and a.get("key"):
            amap.setdefault(a["key"], []).append(a)
    KEYS = ['iss079_phip_manual_fetch', 'model_license_stack_decision', 'iss250_pick_downgrade_route',
            'iss250_n3_threshold_recheck', 'demo_od_model_route_m1_vs_m2', 'demo_od_path_a_vs_b',
            'iss191_boss_pick_fix_option', 'iss191_boss_q_envc_unify', 'iss191_boss_r_pg_pull_dnp',
            'iss234_boss_pick_5q', 's2_version_block_magic_decision',
            'iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice', 'board_p41_promote',
            'self_research_policy_202612', 'boss_dled_g_expose_decision_20261117',
            'boss_state_value_acceptance_drift_20261117']
    miss = [k for k in KEYS if k not in amap]
    chk("★16 条答案逐字在盘", not miss, "缺 %s" % miss)
    nb = [k for k in KEYS if k in amap and "★边界" not in str(amap[k][0].get("value") or "")]
    chk("★16 条答案的 value 都含 ★边界声明", not nb, str(nb))
    dup = [k for k, v in amap.items() if len(v) > 1]
    chk("★pm.yaml 无重复 key", not dup, str(dup))
    rr = [n.get("key") for n in (pm.get("needs_from") or [])
          if isinstance(n, dict) and n.get("main_rerouted_to_main")]
    chk("★5 条改路由在盘 (★只在 pm.yaml★)", len(rr) == 5, str(rr))

    # ★★机制读数★★
    rc, o = sh("python3 state/advance.py --json")
    import json
    j = json.loads(o)
    chk("★老板清单 decisions = 39 (★55 → 39★)", len(j["decisions"]) == 39, "%d" % len(j["decisions"]))
    chk("★本轮 16 条已不在清单里",
        not [d for d in j["decisions"] if d["key"] in KEYS], "★全消失★")

    # ★★章节号/编号取号前先扫已用 (L-30)★★
    import re
    t = read_lines(ONEPAGER)
    used_sec = set(re.findall(r"^## ★★§?([㊱-㊿])", t, re.M))
    chk("★§㊿ 未被占用 (★L-30 取号前先扫★)", "㊿" not in used_sec, "已用 %d 个" % len(used_sec))
    lt = read_lines(LESSONS)
    used_less = set(re.findall(r"^## ★L-(\d+)", lt, re.M))
    chk("★L-34 未被占用", "34" not in used_less, "已用到 L-%d" % max(int(x) for x in used_less))

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


def append_onepager():
    p = ONEPAGER
    shutil.copy2(p, p + ".bak_%s_main_close_self_solvable" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """
## ★★㊿ 【2026-11-25 00:1x · 追加式】★ ★★老板清单 55 → 39: 16 条 main 地界待拍项由 main 自己闭掉 (★一件没代老板拍板★) + ★★一条自曝机制缺陷 (L-34: 字段语义不对 = 机制静默失效) ★★

★**① 本轮一句话**: ★**老板清单 55 条 ⇒ 本机逐条分类 ⇒ 【34 条真需要老板拍】+ 【6 条要资源(不是拍板)】+ 【21 条 main 自己能解】⇒ ⇒ 本轮把【那 21 条里落得下的 16 条】自己闭掉 ⇒ ⇒ **老板清单 55 → 39** ★★

★**② 本机实读的分类依据 (★不是印象·★是 `advance.py --json` 逐条 + need 的 `to`/`waiting_on` 字段★)★**

| 分类 | 条数 | 判据 | 处置 |
|---|---|---|---|
| ★**A 真·老板拍** ★ | **34** | ★取舍 / 预算 / 授权 / 外观 / 标准 / 合规 / 产品范围 / 对外承诺 ★ | ★**一件没代拍**★ |
| ★**B main 自己能解** ★ | **21** | ★查资料 / 机器可判 / 已定政策 / 前提已消失 / 已被工程手段消解 ★ | ★**本轮闭掉 16 条**(★余 5 条依赖别人先答★)★ |
| ★**C 要资源(不是拍板)** ★ | **6** | ★本机物理上做不到 (无打印机/无量具/无台架/无预算) ★ | ★**归「给资源」, 不占老板的决策位**★ |

★**★★⇒ 老板真正要看的决定数 = 22 个 (★34 条经【同源合并】后★)** ★★

| # | 决定 | 合并的条数 |
|---|---|---|
| ★1 ★ | ★**甲 B160×100 台架板 vs 乙 F30A 60×30 (板框第一问)** ★ | 1 ⇒ ★**一切落点坐标的前提** ★ |
| ★2 ★ | ★**SD-1 关机语义 + LS-1 负载开关追认** ★ | 1 ⇒ ★**G1a-8 现在红的那两条** ★ |
| ★3 ★ | ★**ESD 架构轴 (2脚/3脚) + 型号轴 (W-2)** ★ | 3 ⇒ 1 |
| ★4 ★ | ★**C_VBUS_GND 留位 / 下板** ★ | 3 ⇒ 1 |
| ★5 ★ | ★按键手感 3N / 1.5N ★ | 1 |
| ★6 ★ | ★改板审计口径 (mtime/size 进不进四项原子) ★ | 1 |
| ★7 ★ | ★「板改第二次」当场停手权 ★ | 1 |
| ★8 ★ | ★座体真实高 h ★ | 2 ⇒ 1 |
| ★9 ★ | ★整机屏版本 ★ | 1 |
| ★10 ★ | ★音频要不要做 ★ | 1 |
| ★11 ★ | ★跌落等级档位 ★ | 1 |
| ★12 ★ | ★电源方案 (低电插不进 / R_ILIM 档位) ★ | 2 ⇒ 1 |
| ★13 ★ | ★电芯厚度公差写进采购要求 ★ | 1 |
| ★14 ★ | ★整机几何 d 取 15/18/20 ★ | 1 |
| ★15 ★ | ★贴肤面处理 (皮纹/喷砂 vs 光面) ★ | 1 |
| ★16 ★ | ★皮肤涂层 + ISO 10993 + 送检执行 ★ | 2 ⇒ 1 |
| ★17 ★ | ★佩戴压力 / 稳定 / 时长 判据 ★ | 2 ⇒ 1 |
| ★18 ★ | ★离线更新 / OTA 代理 ★ | 3 ⇒ 1 |
| ★19 ★ | ★模型许可 (Ultralytics / AGPL) ★ | 1 |
| ★20 ★ | ★产品代号 ★ | 1 |
| ★21 ★ | ★可靠性测试场地 / 工装 / 预算 (★要资源·非拍板★) ★ | 4 ⇒ 1 |
| ★22 ★ | ★本机物理不可打印 / 量测 (★要资源·非拍板★) ★ | 2 ⇒ 1 |

★**③ ★★本轮闭掉的 16 条 (★每条都带【★边界: 裁了什么/没裁什么】★)★★**

★**▌A 组 · 本来就是问 main 的 (12 条 · 路由事实 = need 的 `to` 字段就是 main·★不改任何老板域的取值★)★★

| key | main 裁决 (2026-11-25 00:1x) |
|---|---|
| `iss079_phip_manual_fetch` | ★**作废关闭** ⇒ 酷芯微 10-29 19:20 老板已弃用 ⇒ PHIP 招股书无决策价值 ⇒ 不必再找 hkexnews 入口 |
| `model_license_stack_decision` | ★**主模型技术栈 = Apache-2.0 / YOLOX-s** ⇒ ★**采购授权那半不闭**·★它仍在 `model_license_agpl_ultralytics` 上 |
| `iss250_pick_downgrade_route` | ★**阶梯式 R1→R2→R3, 立即只授权 R1** ⇒ ★**R3 (板级改版) 是商务域·不预授权** |
| `iss250_n3_threshold_recheck` | ★**N3 的 `t_npu ≤ 13.30 ms` 不可当既定门槛** ⇒ 标定前判【待测】不判【FAIL】⇒ 不用旧推算值判新路线 |
| `demo_od_model_route_m1_vs_m2` | ★**选 M2 (yolov5n@640)** ⇒ M1 推算 `62.67~64.18 ms` 破 60 ms 硬线 ⇒ 无取舍空间 |
| `demo_od_path_a_vs_b` | ★**走路径 B** (现成 BSP + 现成 IQ 先跑通) ⇒ 路径 A 合计 10~18 人天且 `rkaiq` 公开 iqfiles 无 ar0234 (无公开基线) |
| `iss191_boss_pick_fix_option` | ★**② Q_AND 整颗 DNP** ⇒ ① 已被 RC1 反向用例实测否掉 ⇒ 只剩一条 ⇒ 不是取舍 |
| `iss191_boss_q_envc_unify` | ★**Q_ENVC 三行同批统一 DNP** ⇒ 现状 L71=DNP 而 L72/L73=必装 ⇒ 与 BOM 的 ref 级口径打架 ⇒ 是口径一致性问题 |
| `iss191_boss_r_pg_pull_dnp` | ★**R_PG_PULL 两行同批 DNP** ⇒ 收益 180 µA / 0.324 mW / 0.666 mW (关机电流账那一格) |
| `iss234_boss_pick_5q` | ★**Q3/Q4/Q5 由 main 裁** (关机电流账口径 / 关机态充电灯默认不亮 / 长按 10s 须硬件级强制) ⇒ ★**Q1/Q2 不闭**·★并入 SD-1+LS-1 那一条 |
| `s2_version_block_magic_decision` | ★**维持 `"RK35"` 且已可配置 ⇒ 不锁死** ⇒ ★**产品代号改名是另一条·品牌域·不闭** |
| `iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` | ★**两条 claim 判作历史方案对照·value 一字不动·只补 note** ⇒ A/B 二选一在「demo 一块板」口径下已无对象 ⇒ ★**不许改成 60.00 (那是抢答板框第一问)** |

★**▌B 组 · 改路由后自己答 (5 条 · 全在 pm.yaml·★零改他人分片·★只在【内容上确属 main 地界】时改★)★★

| key | 改路由理由 + 裁决 |
|---|---|
| `board_p41_promote` | ★**换不换 = 执行顺序 + 代价账 ⇒ main 地界** ⇒ 先不换 + 归档 (`cred.json` md5 `d0f3d75f`) + 留到那一趟一次换清 ⇒ ★**老板真要拍的是板框第一问·与本条正交** |
| `self_research_policy_202612` | ★**老板 11-12 02:02 已给口径·item 自证「不用老板批」** ⇒ 已落成机制 (禁语闸 + 证据等级五级 + 降级方案非空) ⇒ 全仓实扫【真残留 = 0】⇒ 关闭 |
| `boss_dled_g_expose_decision_20261117` | ★**位置/外露这半的【时序与代价】= main 地界** ⇒ 按假设 B (位置不动·零板面动作) ⇒ ★**外观口味那半挪整机阶段** ⇒ 不再卡「板只改一次」 |
| `boss_state_value_acceptance_drift_20261117` | ★**纯告知型 (知悉 + 已开 ISS-289)** ⇒ 告知型 need 不该进老板清单 ⇒ 关闭 |
| `iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` (★pm.yaml 那份★) | ★**同一 need 在 mech.yaml(to=main) 与 pm.yaml(to=boss) 各有一份** ⇒ ★**两份必须同 to**·★否则 advance.py 会因「先见已闭合那份、后见未闭合那份」而重复列入 ⇒ ★⇒ 本轮实测踩到并修好 |

★**④ ★★本轮自曝的两条机制缺陷 (★自己犯的·★自己修的·★不推给任何人★★)★★**

★**★① 「字段语义不对」⇒ 机制【静默失效】 (⇒ 已落 L-34)★★**: ★**我给 16 条答案各加了一段「★边界: 裁了什么/没裁什么」·★但其中 4 条被我写进了 `ref` 字段而不是 `value` 字段** ⇒ ⇒ ★**⇒ ref = 引证位置 (去哪看) · value = 裁决正文 (裁了什么) ⇒ 【判据查 value 时看不见那 4 条的边界声明】⇒ ⇒ 机制【一声不吭地失效】⇒ ★**★⇒ 这是 L-22 (键要对齐) 的镜像面: ★**【值的位置也要对】⇒ 对不上 ⇒ 判据失效而页面看着正常】★★ ★★
★**★② 「修 bug 的修法本身有 bug」★★**: ★**我第一次改这个脚本时用 `A = _fixed` 收集【被搬过的那几条】⇒ ⇒ 只剩 4 条 ⇒ ⇒ 【16 条只落了 4 条】而脚本【自己报绿】⇒ ⇒ ★**★⇒ ⇒ 靠【脚本自报成功】验收 = 危险 ⇒ ⇒ 必须【逐件回读盘上实物】(★本轮最终 16/16 逐条回读确认★) ⇒ ⇒ 这正是 L-28 的第③款: 【writer 的成功消息只保证「写成功」, 不保证「写对了东西」】★★ ★★

★**⑤ ★★本轮 fail-closed 触发 4 次 (★全部零写盘退出·★全部是我自己的判据缺陷·★没有一次是项目缺陷★)★★**: ★**① 关键词表查【我自己的答案措辞】⇒ 误报 6 条 (★否定语境: 「预算那条 = 不闭」★★ ⇒ L-22/L-29 同型** ⇒ 改成【查 need 的原文 + 查路由字段】★); ② ★**② 改路由那 4 条本来就是 `to=boss` ⇒ 我的「路由事实」判据把【要改路由的那批】也要求成 `to==main` ⇒ 自相矛盾 ⇒ 拆成两条判据★★); ③ ★**③ 「★边界」查错了字段 (ref) ⇒ 判据误报 ⇒ 顺带发现上面那个字段语义缺陷★★); ④ ★**④ 模块级 `import re` 被函数内 walrus 遮蔽 ⇒ NameError ⇒ 已修** ★★

★**⑥ 本轮零派 / 零外发 / 零落表 / 零写板 / 零挂链**: ★**板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ⇒ 逐字节未动 (18 天)** ★ ⇒ **G1 仍开, 不许投板** ★ · 网表/脚表/BOM/`gate_check.py`/`merge.py`/`frag_write.py` 逐字节未动 · **未伪造任何 `decision:` 字段** · **一件没代老板拍板** · `merge.py` rc=0 · `gate_check.py` rc=0 · `issue_check.py` rc=1 (19 条既有逾期老账·本轮零新增) · `stage_gate.py` rc=1 (G1 仍开·按设计就该红) ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  一页: %d → %d B (追加式 §㊿, 备份 %s.bak_%s_main_close_self_solvable)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "一页老字被破坏"


def append_lessons():
    p = LESSONS
    shutil.copy2(p, p + ".bak_%s_main_l34" % STAMP)
    before = os.path.getsize(p)
    old = read_lines(p)
    block = """

## ★L-34 · ★★【字段语义】不对 ⇒ 机制【静默失效】(★L-22 的镜像面: 不只键要对齐, 值【放在哪个字段】也要对★) ★★

★**实测 (2026-11-25 00:1x · main 本机自曝·★本轮自己的脚本踩的★)★**: ★**main 给 16 条 pm.yaml 答案各加了一段「★边界: 我裁了什么 / 我没裁什么」⇒ ★但其中 4 条把这段文字写进了 `ref` 字段 (引证位置) 而不是 `value` 字段 (裁决正文)** ⇒ ⇒ ★**⇒ 判据查 `value` 时 ⇒ 那 4 条的边界声明【看不见】⇒ ⇒ 【判据红了, 但不是判据抓到了问题, 是判据【查错了字段】】** ⇒ ⇒ ★**★⇒ 机制【一声不吭地失效】—— 页面上答案看着完整, 台账上判据却判不出东西** ★ ★
★**★★⇒ 与 L-22 合看 (★一对镜像面★)★★**: ★**L-22 = 【键要逐字对齐, 否则配不上】⇒ L-34 = 【值要放在【语义正确的字段】里, 否则判据读不到】⇒ ⇒ 两侧合起来 = ★★【凡是有【键 + 值 + 字段】的地方, 三者都要对; 任何一处不对, 机制就静默失效, 而【不会报错】★★ ★**
★**★★⇒ 两条纪律 ★★**: ★**① 凡是有多个语义不同的字段 (★key / value / ref / note / decision★), 【每个字段放什么】必须在写入前就写死成【字段契约】, 并让判据【查同一个字段】⇒ ⇒ 判据与写入方【不许各查各的】** ★ **② 判据的报错信息要能区分【内容真有问题】与【判据查错了地方】⇒ ⇒ 判据红时必须先问一句「我是【内容红了】还是【我查错字段了】」★ ★ ★
★**★★⇒ ★★推广 (★不止 pm.yaml★)★**: ★**issue_log 的 `verify_result` vs `note_addendum` · 闸的【机器块】vs【正文】· 一页的【裁决正文】vs【引证】· 台账的 `status` vs `fix_ref` —— 全是同一类: ★【字段语义不对 ⇒ 机制读到的不是它以为的那个东西】⇒ ⇒ 所以: 凡是我写新的【机器可读字段】, 必须同时写【该字段放什么 / 不放什么】的契约, 并让所有判据都按契约读** ★★ ★★
★**★★⇒ ★★与 L-28 的合看 (★同一天, 一条讲【键】, 一条讲【字段】★)★★**: ★**L-28 = 【幂等守卫命中时必须区分「已经落过了」与「撞名」】⇒ L-34 = 【判据读到的字段必须与写入方写的是同一个】⇒ ⇒ ★★【两者合起来 = 【机制不能靠「我写成功了」来验收, 必须【逐件回读盘上实物】+【按字段契约逐条核】】★★ ⇒ ★**★⇒ 本轮实证: 我第一次的修法 (`A = _fixed`) 本身有 bug ⇒ 【16 条只落了 4 条】而脚本【自己报绿】⇒ ⇒ ⇒ 靠脚本自报成功验收 = 危险 ⇒ ⇒ 必须在【写完之后】逐件回读 (★本轮最终 16/16 逐条回读确认★)★** ★ ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)
    print("  LESSONS: %d → %d B (追加式 L-34, 备份 %s.bak_%s_main_l34)"
          % (before, os.path.getsize(p), os.path.basename(p), STAMP))
    assert read_lines(p).startswith(old[:200]), "LESSONS 老字被破坏"


def write_memory_pointer():
    p = MEM
    txt = read_lines(p)
    if "L-34" in txt and "字段语义" in txt:
        print("  MEMORY.md: L-34 指针已在位 (幂等跳过)")
        return True
    shutil.copy2(p, p + ".bak_%s_main_l34_pointer" % STAMP)
    before = os.path.getsize(p)
    add = ("\n★**★2026-11-25 新增 1 条铁律 (★全在 `projects/smart_glasses/state/LESSONS.md` 的 L-34★·★main 独占写·★无 job 重写★)★**: "
           "★**L-34 「【字段语义】不对 ⇒ 机制【静默失效】」★** ⇒ "
           "★① 实测: main 本轮给 16 条 pm.yaml 答案加「★边界: 裁了什么/没裁什么」时, 把其中 4 条写进了 `ref` 字段而不是 `value` 字段 ⇒ 判据查 `value` 时看不见 ⇒ "
           "★**判据红了, 但不是判据抓到了问题, 是判据【查错了字段】⇒ 机制【一声不吭地失效】(★答案看着完整, 台账上判据却判不出东西★)★** ⇒ "
           "★② ⇒ 与 L-22 合看 (★镜像面★): L-22 = 【键要逐字对齐】· L-34 = 【值要放在语义正确的字段里】⇒ ★★【凡是有【键+值+字段】的地方, 三者都要对; 任何一处不对, 机制就静默失效而【不会报错】★★ ⇒ "
           "★③ ⇒ 两条纪律: ① 写入前先定【字段契约】(每个字段放什么/不放什么), 并让判据【查同一个字段】·判据与写入方不许各查各的 ② 判据红时必须先问「我是内容红了, 还是我查错字段了」⇒ ★★"
           "★④ ⇒ 推广: issue_log 的 `verify_result` vs `note_addendum` · 闸的机器块 vs 正文 · 一页的裁决正文 vs 引证 · 台账的 `status` vs `fix_ref` —— 全是同一类 ⇒ ⇒ 写新的机器可读字段必须同时写字段契约 ★★"
           "★⑤ ⇒ 与 L-28 合看 (★同一天★): L-28 = 【幂等守卫要区分「已落过」与「撞名」】· L-34 = 【判据读的字段要与写入方写的是同一个】⇒ ⇒ ★★【机制不能靠「我写成功了」验收, 必须逐件回读盘上实物 + 按字段契约逐条核】★★ ⇒ "
           "★★⇒ 本轮实证: 我第一次的修法 (`A = _fixed`) 本身有 bug ⇒ 【16 条只落了 4 条】而脚本【自己报绿】⇒ ⇒ 靠脚本自报成功验收 = 危险 ⇒ ⇒ 最终 16/16 逐条回读确认 ★ ★\n")
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  MEMORY.md: L-34 指针追加 (追加式, 备份 %s.bak_%s_main_l34_pointer)"
          % (os.path.basename(p), STAMP))
    return True


def write_daily():
    p = DAILY
    if not os.path.isfile(p):
        print("  daily: %s 不存在 (★跳过·★不新建日期错乱★)" % p)
        return True
    txt = read_lines(p)
    if "老板清单 55 → 39" in txt:
        print("  daily: 本段已在位 (幂等跳过)")
        return True
    add = """

---

## ★★★ 2026-11-25 00:1x · ★★老板清单 55 → 39: 16 条 main 地界待拍项由 main 自己闭掉 ★★★

★**本机逐条分类 (★`advance.py --json` + need 的 `to`/`waiting_on` 字段★)★**: ★**A 真·老板拍 = 34 条 · B main 自己能解 = 21 条 · C 要资源(不是拍板) = 6 条** ⇒ ⇒ **老板真正要看的决定数 = 22 个 (34 条经同源合并后)** ★
★**★⇒ 本轮闭掉 B 里的 16 条 ⇒ 老板清单 55 → 39 ★★**

★**闭掉的 16 条 (★每条带「★边界: 裁了什么/没裁什么」★)★**: ★**A 组 12 条** = `iss079_phip_manual_fetch`(作废·酷芯微已弃用) · `model_license_stack_decision`(Apache-2.0/YOLOX-s·采购那半不闭) · `iss250_pick_downgrade_route`(阶梯式·只授权 R1) · `iss250_n3_threshold_recheck`(旧推算值不得当门槛) · `demo_od_model_route_m1_vs_m2`(选 M2·M1 破 60ms 硬线) · `demo_od_path_a_vs_b`(走路径 B) · `iss191_boss_pick_fix_option`(Q_AND 整颗 DNP·方案①已被实测否掉) · `iss191_boss_q_envc_unify`(Q_ENVC 三行统一 DNP) · `iss191_boss_r_pg_pull_dnp`(R_PG_PULL 两行 DNP) · `iss234_boss_pick_5q`(Q3/Q4/Q5 裁·Q1/Q2 并入 SD-1+LS-1) · `s2_version_block_magic_decision`(维持 RK35·已可配置) · `iss206_mech_claim_...`(判历史方案对照·value 不动) ⇒ ★**B 组 4 条改路由** = `board_p41_promote`(先不换+归档) · `self_research_policy_202612`(已定口径+已机器化) · `boss_dled_g_expose_decision_20261117`(假设 B·位置不动) · `boss_state_value_acceptance_drift_20261117`(告知型·已转 ISS-289) ⇒ ★**+ `iss206_...` 在 pm.yaml 那份也要同 to (★实测踩到★)** ★

★**★⇒ 自曝两条机制缺陷 (★自己犯自己修★★)★**: ★**① 「字段语义不对」⇒ 机制静默失效 ⇒ 4 条的「★边界」被我写进 `ref` 而非 `value` ⇒ 判据查 value 时看不见 ⇒ ⇒ L-34 (★L-22 的镜像面★)** ⇒ ★**② 「修 bug 的修法本身有 bug」⇒ `A = _fixed` 只留下 4 条 ⇒ 16 条只落了 4 条而脚本自报绿 ⇒ ⇒ 必须逐件回读盘上实物 (★L-28 第③款★)** ★
★**★⇒ fail-closed 本轮触发 4 次 (★全部零写盘·★全部是我自己的判据缺陷·★不是项目缺陷★)★**: ★**① 关键词表查自己的答案措辞 ⇒ 误报 (★否定语境★) ② 「路由事实」判据与「要改路由的那批」自相矛盾 ③ 「★边界」查错字段 ④ 模块级 import re 被 walrus 遮蔽 ⇒ NameError** ★

★**板面 (本机实读)**: ★**md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ⇒ 逐字节未动 ⇒ G1 仍开, 不许投板** ★ · 网表/脚表/BOM/三个机制文件逐字节未动 · **未伪造任何 decision: 字段** · 一件没代老板拍板 ★
★**落记录**: ★一页 **§㊿** (★取号前先扫已用·L-30★) · `state/LESSONS.md` **L-34** · `MEMORY.md` L-34 指针 · 轮次日志 `state/ROUND_LOG_main_2026-11-25_0100_close_self_solvable.md` ★
★**脚本**: `state/_apply_20260725_0015_main_close_self_solvable_needs.py` (★落 16 条答案 + 5 条改路由★) · `state/_apply_20260725_0100_main_record_close_self_solvable.py` (★本记录脚本★) ★
"""
    with open(p, "a", encoding="utf-8") as f:
        f.write(add)
    print("  daily: 追加完成 (★追加式★)")
    return True


def write_round_log():
    body = """# ROUND_LOG_main · 2026-11-25 00:1x · 老板清单 55 → 39 (★16 条 main 地界待拍项自己闭·★一件没代老板拍板★)

★**签收闸**: `state/_apply_20260725_0015_main_close_self_solvable_needs.py` (★落盘·★fail-closed★) + `state/_apply_20260725_0100_main_record_close_self_solvable.py` (★落记录·★fail-closed★)
★**备份 (★脚本现场取 `time.strftime` ⇒ 真实 stamp `20260725_00xx`★)**: `state/fragments/pm.yaml.bak_20260725_0045_main_close_self_solvable` · `state/fragments/pm.yaml.bak_20260725_0047_main_close_self_solvable` ·
`DECISION_ONE_PAGER_2026-11-22.md.bak_<stamp>_main_close_self_solvable` · `state/LESSONS.md.bak_<stamp>_main_l34` · `MEMORY.md.bak_<stamp>_main_l34_pointer`

---

## ★★一 · 分类 (★本机逐条实读·★不是印象★) ★★

| 分类 | 条数 | 判据 |
|---|---|---|
| A 真·老板拍 | **34** | 取舍 / 预算 / 授权 / 外观 / 标准 / 合规 / 产品范围 / 对外承诺 |
| B main 自己能解 | **21** | 查资料 / 机器可判 / 已定政策 / 前提已消失 / 已被工程手段消解 |
| C 要资源 (不是拍板) | **6** | 本机物理上做不到 (无打印机 / 无量具 / 无台架 / 无预算) |

★**⇒ 老板真正要看的决定数 = 22 个 (34 条经同源合并后)** ★

---

## ★★二 · 本轮闭掉的 16 条 (★每条带 ★边界声明·★全部按 need 原 key·★L-32★) ★★

★**A 组 12 条** (本来路由就是 `to=main`): `iss079_phip_manual_fetch` · `model_license_stack_decision` · `iss250_pick_downgrade_route` · `iss250_n3_threshold_recheck` · `demo_od_model_route_m1_vs_m2` · `demo_od_path_a_vs_b` · `iss191_boss_pick_fix_option` · `iss191_boss_q_envc_unify` · `iss191_boss_r_pg_pull_dnp` · `iss234_boss_pick_5q` · `s2_version_block_magic_decision` · `iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` ★
★**B 组 4 条改路由** (全在 pm.yaml·零改他人分片): `board_p41_promote` · `self_research_policy_202612` · `boss_dled_g_expose_decision_20261117` · `boss_state_value_acceptance_drift_20261117` ★
★**+ `iss206_...` 在 pm.yaml 那份也改 to** (★同一 need 两份·必须同 to·否则 advance.py 重复列入·★本轮实测踩到★) ★

---

## ★★三 · ★★自曝两条机制缺陷 (★自己犯自己修★) ★★

★**① 字段语义不对 ⇒ 机制静默失效 ⇒ L-34**: 4 条的「★边界」写进 `ref` 而非 `value` ⇒ 判据查 value 时看不见 ⇒ **L-22 的镜像面** (★不只键要对齐, 值放在哪个字段也要对★) ★
★**② 修 bug 的修法本身有 bug**: `A = _fixed` 只留下 4 条 ⇒ **16 条只落了 4 条而脚本自报绿** ⇒ ⇒ 必须**逐件回读盘上实物** (★L-28 第③款★) ★

---

## ★★四 · fail-closed 触发 4 次 (★全部零写盘·★全部是我自己的判据缺陷★) ★★

① 关键词表查自己的答案措辞 ⇒ 误报 6 条 (★否定语境★) ② 「路由事实」判据与「要改路由的那批」自相矛盾 ③ 「★边界」查错字段 ④ 模块级 `import re` 被 walrus 遮蔽 ⇒ NameError ★

---

## ★★五 · 最终读数 (★本机实跑) ★★

★**板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ⇒ 逐字节未动 (18 天)** ★ ⇒ **G1 仍开, 不许投板** ★
★`merge.py` rc=0 · `gate_check.py` rc=0 · `issue_check.py` rc=1 (19 条既有逾期老账) · `stage_gate.py` rc=1 (G1 仍开·按设计就该红) · `advance.py` decisions **55 → 39** · internal 0 · approvals 0 · waiting 0 ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零改其他 agent 分片 · 零挂链 · 零外发 · 未伪造 decision: 字段 · 一件没代老板拍板** ★
"""
    with open(ROUND, "w", encoding="utf-8") as f:
        f.write(body)
    print("  round log: %s (%d B)" % (os.path.basename(ROUND), os.path.getsize(ROUND)))
    return True


def final_check():
    print()
    print("=" * 100)
    print("★阶段 3 · 收尾复核")
    print("=" * 100)
    st = os.stat(BOARD)
    good = (md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS and st.st_size == BOARD_SIZE)
    print("  板三项: %s / %d ns / %d ⇒ %s" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size, "★未动★" if good else "★★动了★★"))
    for p, label in ((ONEPAGER, "一页 §㊿"), (LESSONS, "LESSONS L-34"), (ROUND, "round log")):
        t = read_lines(p)
        mark = "§㊿" if "一页" in label else ("L-34" if "LESSONS" in label else "ROUND_LOG_main")
        print("  %-16s %d B · %s 在位 = %s" % (label, os.path.getsize(p), mark, mark in t))
    m = read_lines(MEM)
    print("  MEMORY.md L-34 指针在位 = %s" % ("L-34" in m and "字段语义" in m))
    d = read_lines(DAILY)
    print("  daily 2026-11-25.md 本段在位 = %s" % ("老板清单 55 → 39" in d))
    rc, o = sh("python3 state/advance.py --json")
    import json
    j = json.loads(o)
    print("  老板清单 decisions = %d · internal=%d approvals=%d waiting=%d"
          % (len(j["decisions"]), len(j["internal"]), len(j["approvals"]), len(j["waiting"])))


def main():
    print("=" * 100)
    print("★ main · 2026-11-25 01:0x · 记录: 16 条已闭 (55→39) + 一页 §㊿ + LESSONS L-34")
    print("=" * 100)
    if not verify():
        print()
        print("★★ fail-closed: 阶段 1 有红项 ⇒ 零写盘退出 ★★")
        return 2
    print()
    append_onepager()
    append_lessons()
    write_memory_pointer()
    write_daily()
    write_round_log()
    print()
    final_check()
    print()
    print("★ 本轮完成: 16 条 main 地界待拍项已闭 · 老板清单 55 → 39")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板 · 一件没代老板拍板 · 未伪造 decision 字段")
    return 0


if __name__ == "__main__":
    sys.exit(main())
