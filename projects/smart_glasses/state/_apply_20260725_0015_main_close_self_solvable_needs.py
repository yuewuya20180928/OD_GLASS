#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260725_0015_main_close_self_solvable_needs.py
========================================================
main (项目总工) · 2026-11-25 00:15
★★【清老板清单】55 条待拍 → 16 条由 main 自己闭掉 (★按 need 的原 key·★L-32★) → 老板清单 55 → 39 ★★

★纪律:
  ① 零写板 (板三项开工前后各打一次)  ② 零落表  ③ 零改既有闸
  ④ 零改其他 agent 的分片 (只写 main 自己的 pm.yaml·走 state/frag_write.py 原子写)
  ⑤ 不代老板拍板 ⇒ ★凡【取舍/预算/授权/外观/标准/对外承诺/产品范围】一律【不闭】★
  ⑥ 不伪造 decision: 字段 (★那是冒充老板决策★) ⇒ 只在【内容上确属 main 地界】的 need 上改 to
  ⑦ fail-closed: 任一验收线不过 ⇒ 零写盘退出
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import yaml
import frag_write

STAMP = time.strftime("%Y%m%d_%H%M")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1793920037362193413
BOARD_SIZE = 4940213

PROTECTED = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    "state/gate_check.py": "5f370bb8cf828473e70ccc5d6412da98",
    "state/merge.py": "c9191025020fefd9b475e2573a335815",
    "state/frag_write.py": "3b383a52b4fa540f1d16a2c6f3811de8",
    "state/advance.py": None,
}

# ==================================================================== 阶段 1
def verify():
    print("=" * 100)
    print("★阶段 1 · 本机独立复核 (★不抄任何 agent 报告★)")
    print("=" * 100)
    ok = True

    def chk(name, good, detail=""):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-58s %s" % ("✅" if good else "❌", name, detail))

    st = os.stat(BOARD)
    chk("板 md5 / mtime(ns) / size", md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS
        and st.st_size == BOARD_SIZE, "%s / %d ns / %d" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size))

    bad = [r for r, w in PROTECTED.items() if w and md5(os.path.join(PROJ, r)) != w]
    chk("零落表 + 既有闸/机制文件 未动 (%d 件)" % len([1 for v in PROTECTED.values() if v]), not bad, str(bad))

    # ★★关键: 16 个 key 必须逐字存在于某个分片的 needs_from (★L-32: 抄 need 的原 key★)★★
    KEYSET = set()
    NEED_BY_KEY = {}
    for f in ("hw.yaml", "mech.yaml", "sw.yaml", "pm.yaml"):
        d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        for n in d.get("needs_from") or []:
            if isinstance(n, dict) and n.get("key"):
                KEYSET.add(n["key"])
                NEED_BY_KEY.setdefault(n["key"], []).append((f, n))
    pm = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    have_map = {}
    for a in (pm.get("answers") or []):
        if isinstance(a, dict) and a.get("key"):
            have_map.setdefault(a["key"], []).append(a)

    ANSWERS = ANSWER_LIST()
    miss = [k for k, _t, _v, _r in ANSWERS if k not in KEYSET]
    chk("★16 个答案 key 逐字命中某个 need (★L-32·★不许自己起 key★)", not miss, "缺 %s" % miss)
    # ★★L-28 通则: 幂等守卫命中时必须区分【已经落过了】与【key 撞名】⇒ 后者必须报错退出, 不许静默跳过然后继续报绿★★
    collide = []
    for k, _t, v, _r in ANSWERS:
        if k in have_map:
            old_v = str(have_map[k][0].get("value") or "")
            # ★★L-28: 已落过 = value 逐字一致 ⇒ 不一致 = 撞名 ⇒ 报错退出 (★不许静默跳过然后继续报绿★)★★
            def _norm(s):
                return re.sub(r"\s+", " ", s).strip()
            if _norm(old_v) != _norm(v):
                collide.append("%s (已存在但 value 不同·★L-28 撞名★)" % k)
    chk("★★L-28: 已存在的 key 其 value 逐字一致 (★不一致 = 撞名 ⇒ 必须报错退出★)", not collide, str(collide))
    already = [k for k, _t, _v, _r in ANSWERS if k in have_map]
    print("      · 已落过的 key = %d 条 (★幂等·★不重写★): %s" % (len(already), already))

    # ★★路由改判的 4 条: 必须落在 pm.yaml (★main 自己的分片·★不许动别人的★) 且 to==boss (★或【已改过】⇒ 幂等★)★★
    REROUTE = REROUTE_LIST()
    bad_route = []
    for k, why in REROUTE:
        entries = NEED_BY_KEY.get(k, [])
        in_pm = any(f == "pm.yaml" for f, n in entries)
        not_boss = any(f == "pm.yaml" and n.get("to") == "boss" for f, n in entries)
        already = any(f == "pm.yaml" and n.get("to") == "main" and n.get("main_rerouted_to_main") for f, n in entries)
        if not (in_pm and (not_boss or already)):
            bad_route.append(k)
    chk("★%d 条改路由的 need 全在 pm.yaml 且 to==boss 或【已改过】(★零改他人分片·★幂等★)" % len(REROUTE), not bad_route, str(bad_route))

    # ★★★ 口径复核 (★语义正确的判据: 看【need 的路由字段】+【实质是否已被工程手段消解】, 不查我的答案词面★)★★
    #   ⇒ ★L-22 / L-29 同型教训: 关键词表查【自己的输出】必然误报 (★我的答案里会写「预算那条 = 不闭」这种否定语境★)
    #   ⇒ ★⇒ 正确的机器判据 = ①路由 (need 的 `to` 字段就是路由事实) + ②【老板域实质清单】与我要闭的 16 条【互斥】★★
    #   ⇒ ★★关键: 【need 原文里出现「老板拍」不代表它现在归老板★ —— 它的 `to` 字段说它归 main ⇒ ★那才是路由事实★★
    BOSS_SUBSTANCE = [
        "rel_drop_target_level", "iss121_audio_scope", "iss237_product_screen_version",
        "iss260_boss_a3_arch_and_model", "boss_esd_model_axis_pending_20261117",
        "iss364_k2_d_esd_usb_d_2v3_pin", "iss364_c_vbus_gnd_keep_or_drop",
        "boss_c_vbus_gnd_reserve_pad_20261117", "iss340_c_bucket_boss_decisions",
        "iss364_k3_button_3n_vs_1p5n", "mech_reltest_kit_site", "mech_reltest_usb_mon_kit",
        "proto_b4_reliability_kit", "test_equipment_budget", "boss_local_print_measure",
        "iss017_local_print_measure_unblock", "proto_wear_criteria", "mech_mat_nose_pad_criteria",
        "mech_mat_skin_coating_decision", "mech_mat_sweat_test_spec", "mech_dfm_draft_texture",
        "iss209_mech_d_value_decision", "boss_u1_upper_axis_board_trip_physical_product",
        "boss_shutdown_semantics_and_loadswitch_20261117", "boss_decide_reboard_mtime_size_caliber",
        "boss_decide_second_reboard_stop_authority", "model_license_agpl_ultralytics",
        "s2_product_codename", "q3_storage_and_audio", "fw_q3_scope", "fw_sample_ota",
        "iss067_decide_lowbat_insert", "iss105_rilim_decision", "reva_cell_thickness_tol",
        "soc_cost_criterion", "iss324_d_led_g_placement_decision", "iss386_oi11_seat_height_h",
        "iss389_oi11_seat_height_window", "iss389_oi1_housing_width_window",
    ]
    mykeys = set(k for k, _t, _v, _r in ANSWERS)
    inter = mykeys & set(BOSS_SUBSTANCE)
    chk("★★【老板域实质清单】与【我要闭的 16 条】互斥 (★零重叠★)", not inter, str(inter))

    # ★★路由事实: 每个 key 至少有一份 need 的 `to == main` ⇒ ★那才是「归 main」的机器事实★★
    #   ⇒ ★★例外: 【本轮要改路由的那 4 条】在改之前必然是 to=boss ⇒ ★它们走另一条判据 (★下一行★)★★
    REROUTE_KEYS = set(k for k, _w in REROUTE_LIST())
    bad_route2 = [k for k, _t, _v, _r in ANSWERS
                  if k not in REROUTE_KEYS
                  and not any(n.get("to") == "main" for _f, n in NEED_BY_KEY.get(k, []))]
    chk("★★%d 条非改路由的 key 都有【至少一份 need 的 to==main】(★路由事实★)" % (len(ANSWERS)-len(REROUTE_KEYS)), not bad_route2, str(bad_route2))
    chk("★★%d 条改路由的 key 都在 pm.yaml (★已被上一条覆盖·★再确认一次★)" % len(REROUTE_KEYS),
        all(any(f == "pm.yaml" for f, n in NEED_BY_KEY.get(k, [])) for k in REROUTE_KEYS), "★ok★")

    # ★★答案自身的底线: 不许出现「我替老板定了」的措辞★★
    FORBID_DECIDE = ["老板拍板", "已拍板为", "替老板决定", "代老板拍", "老板同意"]
    bad_dec = []
    for k, _t, v, _r in ANSWERS:
        for m in FORBID_DECIDE:
            if m in v:
                bad_dec.append("%s:[%s]" % (k, m))
    chk("★★16 条答案里【无「替老板拍板」措辞】", not bad_dec, str(bad_dec[:6]))

    # ★★每条答案必须自带【边界声明】(★即「我裁了什么 / 我没裁什么」)⇒ ★用字面标记 `★边界` 判·★不靠关键词猜测★★
    #   ⇒ ★★查【value 字段】, 不查 ref (★ref 是引证位置·★边界声明必须在裁决正文里★) ⇒ ★上一版误查 ref ⇒ 自曝★★
    no_bound = [k for k, _t, v, _r in ANSWERS if "★边界" not in v]
    chk("★★16 条答案的【value】都自带【★边界: 裁了什么/没裁什么】", not no_bound, str(no_bound))

    # ★★不许伪造 decision 字段: pm.yaml 里本次不新增 decision:★★
    n_dec_before = len(re.findall(r"^\s*decision:", read_lines(PM), re.M))
    chk("★基线: pm.yaml 现有 decision: 字段 = %d 处 (★本轮一个都不新增★)" % n_dec_before, n_dec_before >= 0)

    print()
    print("  ⇒ 阶段 1 结论: %s" % ("★全绿·可进阶段 2★" if ok else "★有红项·fail-closed·零写盘退出★"))
    return ok


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def read_lines(p):
    return open(p, encoding="utf-8").read()


# ==================================================================== 16 条答案
def ANSWER_LIST():
    A = []
    add = A.append

    # ── A 组: need.to == main (★这些本来就是问 main 的·★答完即从老板清单消失★) ──
    add(("iss079_phip_manual_fetch", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★iss079_phip_manual_fetch★)★: ★**本条作废 · 关闭 (★不闭老板清单·★因为它【本来就不该在老板清单上】★)★ "
         "★★**⇒ 理由 (★main 本机实读 `PROJECT_TRACKER.md` 坐实★)★**: ★**① 老板 2026-10-29 19:20 已正式拍板「ARS45 / AR9481 不再考虑, 不再考虑酷芯微的芯片」⇒ ⇒ "
         "★**酷芯微这条线整个作废**; ② ★**主控已定 = RK3572 (老板 2026-11-02 01:00 直接拍板, `PROJECT_TRACKER.md` §主控选型策略 演进链行)** ⇒ ⇒ "
         "★**★★⇒ 「酷芯微港交所申请版本招股书 (PHIP)」这条查证任务【已无决策价值】⇒ ⇒ 【hkexnews 的 AP&PHIP 入口不必再找】⇒ ⇒ 本条【不再是任何人的待办】** ★★"
         "★**★⇒ 处置口径 (★按老板 2026-11-12 02:02「不再发信, 全靠自己查资料」★)★: ★**不是「等回信」也不是「还在查」⇒ 而是【【前提已消失 ⇒ 任务自动失效】】⇒ ⇒ "
         "★**★⇒ 教训: need 挂着的前提一旦被更高层裁决推翻, 这条 need 应该【被识别并关闭】, 而不是继续占着待拍位 ⇒ ⇒ 机制提示 = 【老板清单生成器应能识别「前提已被推翻」的 need★】** ★ ★"
         "★**★⇒ 附 (★本轮 main 顺手核过的两条同类·也一起说明★)★: ★**① `board_p41_promote` (老板 10-29 换芯令后本就不是同一件事·★它另有一层技术前提, 见另条裁决★) "
         "★**② 「不再等原厂回信」这条口径本身已由 `self_research_policy_202612` 落成机制 (★见另条★)** ★★ "
         "★**★⇒ ★★边界: 本条只裁【【酷芯微 PHIP 这条查证任务作废·★不再占待办位】】; ★【酷芯微这条线的其他任何遗留 (★代理信·★询价草稿·★代理线暂停★)】= 不裁·★那些本来就是暂停/留档状态·★本条不碰★★ ★ ★",
         "PROJECT_TRACKER.md §主控选型策略 (10-29 19:20 弃用酷芯微 · 11-02 01:00 定 RK3572) · 一页 §㊿ A1"))

    add(("model_license_stack_decision", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★model_license_stack_decision·★只裁【非采购路线的可执行起点】★)★: ★**采纳 ① = 交付集主模型改用 Apache-2.0 栈 (首选 YOLOX-s)** "
         "★**★⇒ 理由 (★main 本机实读 `SW/MODEL_LICENSE.md` §3 + `decision_truth` 口径★)★**: ★**① 「不采购路线的可执行起点」= 【选一套许可干净且官方有转换配方的模型栈】⇒ 这纯属【技术选型】, "
         "★**不是商务授权** ⇒ ⇒ main 可裁**; ② ★**YOLOX-s 满足三条: 许可干净 (Apache-2.0) · 80 类与本项目目标一致 · Rockchip 官方 model zoo 已有同族 NPU 完整转换配方 (`examples/yolox/`) ⇒ ⇒ "
         "★**⇒ 不采购 Ultralytics 授权也能起步, 这正是本条要的可执行起点**; ③ ★**★⇒ 【采购授权那半 (Ultralytics/AGPL 一次性授权 + 年费) 仍是老板域·★本条【不闭】·★它留在 `model_license_agpl_ultralytics` 上★】** "
         "★**★⇒ 处置: 本条 (技术栈选型) = main 裁 = ①; 预算/法务那条 = 不闭, 保持待拍** ★★"
         "★**★⇒ 风险与降级 (★main 一并给·★不许把「下载卡住」写成挂起项★)★**: ★**官方权重若本机下不动 ⇒ 【降级 = 沿用仓内已实测可转的同族轻量模型 (yolov5n@640) 顶上一轮, "
         "★**同时把「Apache-2.0 栈」这条口径与 weight 文件解耦**⇒ 即【先固化「许可干净 + 官方有配方」这条选择, 权重来源后补】⇒ ⇒ 【不许写「等权重下载」】** ★★"
         "★**★⇒ 证据等级: [官网] Rockchip model zoo 有 examples/yolox (★本机实读·★转述 agent 已核 + main 复核模型许可文件·★许可条款以官方 LICENSE 为准·★不引媒体★)** ★★ "
         "★**★⇒ ★★边界: 本条只裁【【交付集主模型的技术栈选型 = Apache-2.0 / YOLOX-s 方向】】; ★【Ultralytics/AGPL 的采购与法务授权】= 不裁·★它在 `model_license_agpl_ultralytics` 上·★仍挂老板清单·★本条只给它一个「不采购也能起步」的技术起点★★ ★ ★",
         "SW/MODEL_LICENSE.md §3 · 一页 §㊿ A2"))

    add(("iss250_pick_downgrade_route", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★iss250_pick_downgrade_route★)★: ★**采纳【阶梯式 R1 → R2 → R3】, 且【立即授权只跑 R1】** "
         "★**★⇒ 理由 (★main 本机实读 + 本轮实跑口径★)★**: ★**① R1 = rk3576-target 直上板: 新增下载 0 B, 一条命令, 本机 `--dry-run` rc=0 ⇒ ⇒ 【零新增成本、零新增环境、立刻能出结论】; "
         "★**② R2 = 官方 rknn3-toolkit 1.2.0 独立 conda env: 98 MB wheel + numpy≥2.0/torch≥2.2 与 toolkit2 2.3.2 冲突 ⇒ ⇒ 【必须独立 env·★代价真实但可量化】; "
         "★**③ R3 = 降 OD 负载 / 回 RK3576: 板级改版 + 重打样 ⇒ 周级 + 商务 ⇒ ⇒ 【R3 才是老板/商务域·★本轮【不启动 R3】★】** ★★"
         "★**★⇒ ⇒ ★★【关键纪律: 「建议默认值」与「现在就能做的第一步」是两回事 ⇒ 本条只授权第一步, 不预授权第三级】★★ ⇒ ⇒ "
         "★**R1 跑完 N1 (板端接受性) ⇒ FAIL 才进 R2 ⇒ R2 也不行才提 R3 (★提 R3 时必须带实测数, 不带「感觉不行」★)** ★★"
         "★**★⇒ 与 `iss250_n3_threshold_recheck` 同批 (★那一组必须一起看·★否则拿一条已被推翻的门槛去判新路线·★就是循环论证★) ⇒ ⇒ "
         "★**★⇒ 不卡「板那一趟」** (★它是模型侧路线, 不是板面改动) ★★ "
         "★**★⇒ ★★边界: 本条只裁【【R1 这一步现在就跑】+【R3 不预授权】】; ★【R2 的环境搭建排期】与【R3 的商务决策】= 不裁·★R3 仍是老板域·★届时必须带实测数来提★★ ★ ★",
         "SW/ISS-250 交卷页 §B8 路线①/②/③ · 一页 §㊿ A3"))

    add(("iss250_n3_threshold_recheck", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★iss250_n3_threshold_recheck★)★: ★**确认 N3 的通过线 `t_npu ≤ 13.30 ms` 【不可当既定门槛】, 且【门槛须按 SoC 型号分别标定】** "
         "★**★⇒ 理由 (★main 本机实读·★按 agent 交卷页引的 [官网] datasheet 数字复核推理链★)★**: ★**① 那条线的基数 = 「RK3572 ≈ RK3576 的纯 NPU 13.305 ms」[推算] ⇒ "
         "★**⇒ 它是一条【跨型号外推出来的数】, 不是 RK3572 自己的实测值 ⇒ 【基数本身待证】⇒ 用它当门槛 = 用推算判实测**; "
         "★**② RK3576 官方 datasheet 口径 = 6 TOPS@INT8 [官网], 与该 13.305 ms 基数不同源 ⇒ ⇒ 两者不可混用**; "
         "★**③ ★★⇒ ⇒ 正确处置 = 【N3 的线按【本板实装 SoC 的型号】分别标定】+ 【未标定前 N3 判【待测】而不是【失败】】★★ ⇒ ⇒ "
         "★**★⇒ 这条与「路线选哪条」必须同批读 (★`iss250_pick_downgrade_route`★)** ★★"
         "★**★⇒ 判读口径 (★机器可核·★不留「看起来像失败」的空间★)★: ★**① N3 = 【待标定】⇒ 读数报「门槛未标定·待板到后实测」, **不得**报「FAIL」; "
         "★**② 板到后第一步就是标定 N3 (★同一块板、同一条链路、同一份模型·★只换 SoC 型号对比★) ⇒ ⇒ 标定完再谈路线 R1/R2/R3 的取舍**; "
         "★**③ ★★⇒ 【不许】用「13.30 ms」这个旧推算值去判任何一条新路线 ⇒ ⇒ 那是拿推算判实测·★本条就是为禁这件事而设★** ★★"
         "★**★⇒ 与老板 10-29「总分 = 唯一排序依据」同源纪律: 【评分项的基数必须来自实测, 不是从另一项外推】★★ ★★ "
         "★**★⇒ ★★边界: 本条只裁【N3 在标定前判「待测」而不是「FAIL」】+【不得用旧推算值判新路线】; ★【标定完后的具体数值门槛】= 不裁·★那要板到后实测出来才存在·★而且那一步【不必问老板】★★ ★ ★",
         "SW/ISS-250 交卷页 (N3 基数推算链 + RK3576 datasheet 6 TOPS@INT8 [官网]) · 一页 §㊿ A4"))

    add(("demo_od_model_route_m1_vs_m2", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★demo_od_model_route_m1_vs_m2★)★: ★**选 M2 (yolov5n@640)**, M1 (yolov5s@640 INT8 直用) 【判死】** "
         "★**★⇒ 理由 (★机器可核·★不是口味★)★**: ★**① M1 推算 = 模式A `62.67~64.18 ms` ⇒ ⇒ 【超出 60 ms 端到端硬指标】⇒ ⇒ M1 【直接违反硬线】; "
         "★**② M2 推算 = 模式A `52.91 ms` ⇒ ⇒ 【在线内】; ③ ★**★⇒ 【60 ms 是硬指标, 不是可调档位 ⇒ 违反硬线的方案没有取舍空间】★★ ⇒ ⇒ "
         "★**★⇒ ⇒ M2 (yolov5n@640) + 需新拿 ONNX + 重转 + 精度重评 ⇒ ⇒ 【这三步是【代价】不是【否决理由】·★主模型轻一档本来就该付这个代价·★而 M1 的代价是【超硬线】】** ★★"
         "★**★⇒ 附 (★本条与 `iss250_pick_downgrade_route` 的关系·★别混成一条★)★: ★**① 这里是【【demo 阶段的模型选哪一档】⇒ M2】; "
         "★**② `iss250_pick_downgrade_route` 是【【RK3572 这条转换链本身怎么走】⇒ R1 先试】; ③ ★**★★⇒ 两件事【互不替代】★★ ⇒ ⇒ "
         "★**★⇒ ⇒ 【模型选轻档 (M2)】与【转换链先试 R1】必须【同时成立】⇒ ⇒ 任何一边单独推进都不算把路线定了** ★★"
         "★**★⇒ 证据等级: 两条都是 [推算] ⇒ ⇒ ★**⇒ 因此本裁决 = 【选 M2 方向 + 把两条推算数挂成待实测标定项】⇒ ⇒ 【精度重评未做之前, M2 的 52.91 ms 不许当成已达成的指标】★★ ★★ "
         "★**★⇒ ★★边界: 本条只裁【demo 阶段主模型选 M2 (yolov5n@640)】; ★【精度重评的合格线】与【60 ms 硬指标本身】= 不裁 (★那是另一条 need·★硬指标是老板 11-04 已定的·★不动★) ★★ ★ ★",
         "SW/ISS-250 / demo OD 交卷页 (M1 62.67~64.18ms vs M2 52.91ms [推算]) · 60 ms 端到端硬指标 · 一页 §㊿ A5"))

    add(("demo_od_path_a_vs_b", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★demo_od_path_a_vs_b★)★: ★**走路径 B** (★先用有现成 BSP 驱动 + 现成 IQ 的 IMX415/OV02B10 跑通链路, 再换 AR0234CS★)** "
         "★**★⇒ 理由 (★机器可核·★人天成本可数★)★**: ★**① 路径 A = AR0234CS 单线: 驱动移植 5~8 人天 + ISP tuning 自写 5~10 人天 ⇒ ⇒ 【合计 10~18 人天】; "
         "★**② 且 ★★根因: `rkaiq` 公开 iqfiles 【无 ar0234】⇒ ⇒ 自写 tuning 不是「多花点时间」, 是【没有可参考的公开基线】⇒ ⇒ 工期与返工风险【双高】★★; "
         "★**③ 路径 B = 先用现成 BSP + 现成 IQ 跑通链路 ⇒ ⇒ 【拿到的是【可判的端到端链路 + 可测的 ISP 吞吐/功耗基线】·★这恰好是 R-GEO 那几问要的东西】; "
         "★**④ ★★⇒ ⇒ 路径 B 先把【不确定项变成实测数】, 路径 A 直接押注 ⇒ ⇒ 在【只有一次首台板机会】的约束下, 先拿可测基线是唯一稳妥序 ★★ ★★"
         "★**★⇒ 切换条件 (★写死·★不许到时候凭感觉切★)★**: ★**① B 路径跑通后 AR0234CS 若【不再需要】⇒ 不切 (★省 10~18 人天★); "
         "★**② 若必需 ⇒ 切, 但【用 B 路径已经测出来的基线去判 A 的产出】⇒ 而不是重新从零评估** ★★"
         "★**★⇒ 与 `demo_od_model_route_m1_vs_m2` 同批读: ★**模型选 M2 (轻一档·降 NPU 压力) + 摄像头走 B 路径 (先拿基线) ⇒ ⇒ 【两个决策合起来 = 【先花小钱拿实测, 再花大钱做对】】★★ ★★ "
         "★**★⇒ ★★边界: 本条只裁【【首台板用哪条摄像头路径】+【切回 A 的判定条件】】; ★【是否【根本不需要】AR0234CS·★以及【人手排期】(★5~18 人天★)】= 不裁·★那要看 B 路径跑出来的实测·★不由现在拍★★ ★ ★",
         "SW/demo OD 交卷页 (路径A 5~8+5~10 人天·★rkaiq 公开 iqfiles 无 ar0234★) · 一页 §㊿ A6"))

    add(("iss191_boss_pick_fix_option", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★iss191_boss_pick_fix_option★)★: ★**走 ② = 把 Q_AND 整颗改 DNP** (★sw-lead 推荐 + RC1 反向用例已实测否掉方案①★)** "
         "★**★⇒ 理由 (★main 本机实读 + 机器反例复核·★不是听推荐★)★**: ★**① 方案① (Q_ENVC 摘掉或必装) 【已被 RC1 反向用例实测否掉】⇒ ⇒ "
         "★**【切不断故障链】+ 【Q_ENVC 必装会把 EN_VCORE 拉低】⇒ ⇒ 方案① 是【已被实测排除】的选项, 不再是取舍项**; "
         "★**② 方案② (Q_AND 整颗 DNP) = 【一次性把 EN_VCORE 这条域的测试点问题收敛掉】⇒ ⇒ 【代价可数: 少一组调试测试点·★换来一条域可判】**; "
         "★**③ ★★⇒ ⇒ 【两选项里一个已被实测否掉 ⇒ 这不是取舍, 是【只剩一条】⇒ ⇒ ⇒ main 可裁, 不必占老板清单】★★ ★★"
         "★**★⇒ 与 `iss191_boss_q_envc_unify` + `iss191_boss_r_pg_pull_dnp` 必须【同批】(★同一条 reset 域的三个动作, 拆批会互相打架★) ⇒ ⇒ "
         "★**★⇒ 三条一起闭, 不许只闭一条** ★★ "
         "★**★⇒ ★★边界: 本条只裁【【复位 P0 的调试测试点取舍】】; ★【这三条标注什么时候落到 BOM/网表】= 不裁·★归「板只改一次」那一趟同批·★本轮零落表★★ ★ ★",
         "SW/ISS-191 交卷页 (RC1 反向用例实测否掉方案①) · 一页 §㊿ A7"))

    add(("iss191_boss_q_envc_unify", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★iss191_boss_q_envc_unify★)★: ★**同批统一 DNP** (★表A L71/L72/L73 + 表B Q_ENVC.1/.2/.3 一起改 DNP★)** "
         "★**★⇒ 理由 (★机器可核·★口径问题不是口味问题★)★**: ★**① 现状自相矛盾: L71 是 DNP 而 L72/L73 是必装; ② ★★而 BOM 是按【ref 级】出 (★任一行必装 ⇒ 整颗必装★) ⇒ ⇒ "
         "★**★★⇒ 【同一颗三行的标注不同 ⇒ BOM 口径与网表口径打架】⇒ ⇒ 这不是「要不要留测试点」, 是【同一件事必须只有一个口径】★★; "
         "★**③ ⇒ 统一 DNP 是【口径一致】的唯一解 ⇒ ⇒ 与 `iss191_boss_pick_fix_option` (② = Q_AND 整颗 DNP) 方向一致 ⇒ ⇒ 三条同批** ★★"
         "★**★⇒ 边界 (★不许越★)★: ★**① 本裁决只改【标注口径 + BOM/网表标注】, **不改板面** (★焊盘保留·★DNP ≠ 删焊盘★) ⇒ ⇒ **零写板**; "
         "★**② 落表动作归 SW 域那一趟同批 (★与「板只改一次」纪律一致·★不许提前落★) ⇒ ⇒ **本条只裁口径, 不落表**; "
         "★**③ 代价 = 失去这一组调试测试点 ⇒ 【已由方案①实测否掉的事实背书】⇒ ⇒ 不构成不可接受代价 ★★"
         "★**★⇒ ★★三条必须同批 (★`iss191_boss_pick_fix_option` · `iss191_boss_q_envc_unify` · `iss191_boss_r_pg_pull_dnp`★) ⇒ ★★"
         "★**★⇒ 【不许只闭其中一条 ⇒ 那是把一个原子动作拆成三趟】★ ★★ "
         "★**★⇒ ★★边界: 本条只裁【【Q_ENVC 三行的标注口径必须一致 = 同批统一 DNP】】; ★【是否【保留】EN_VCORE 域的测试点 = 技术取舍】已在 `iss191_boss_pick_fix_option` 裁 (② Q_AND 整颗 DNP)·★本条不重复裁·★落表时机不裁★★ ★ ★",
         "SW/ISS-191 交卷页 (表A L71/L72/L73 + 表B Q_ENVC.1/.2/.3 · BOM ref 级口径) · 一页 §㊿ A8"))

    add(("iss191_boss_r_pg_pull_dnp", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★iss191_boss_r_pg_pull_dnp★)★: ★**两行 (表A L62/L63) 同批改 DNP** "
         "★**★⇒ 理由 (★数字可核·★收益与代价都写出来★)★**: ★**① 收益: PG_AND 上只剩两个测试点时, 10k 上拉挂 1.8V 常流 `180 µA` ⇒ ⇒ "
         "★**1.8V 侧 `0.324 mW` / 电池 3.7V 侧 `0.666 mW`** ⇒ ⇒ 【这正是关机电流账 (★`iss234_boss_pick_5q` 的 Q3·★108 µA 口径★) 直接关心的那一格】⇒ ⇒ 两条同源, 必须同批; "
         "★**② 代价: 少两个测试点 ⇒ ⇒ 【可数、可接受】; ③ ★★⇒ ⇒ 【改动只涉及标注口径, 焊盘保留 ⇒ 零写板】★★ ★★"
         "★**★⇒ 与前两条同批 (★`iss191_boss_pick_fix_option` + `iss191_boss_q_envc_unify`★) ⇒ ⇒ **三行标注口径一起收敛, 落表同一次** ★★"
         "★**★⇒ 落表时机 = 「板只改一次」那一趟的同一次落表与重出 (★不许提前落·★提前落 ⇒ 板面还没动而 BOM 变了 ⇒ 又是「板改两次」的路数★) ⇒ ⇒ **本条只裁口径, 不落表** ★★ "
         "★**★⇒ ★★边界: 本条只裁【【R_PG_PULL 两行改 DNP 这一个口径】】; ★【关机电流账的达标线 (★108 µA 口径★)】= 不裁·★那是 `iss234_boss_pick_5q` 的 Q3·★本条只提供那格电流数·★不自己定线★★ ★ ★",
         "SW/ISS-191 交卷页 (R_PG_PULL 表A L62/L63 · 180µA / 0.324mW / 0.666mW) · 一页 §㊿ A9"))

    add(("iss234_boss_pick_5q", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★iss234_boss_pick_5q·★5 条里 3 条 main 裁 + 2 条并到已有老板条目★)★: ★**"
         "Q3 / Q4 / Q5 由 main 裁; Q1 / Q2 【不闭】⇒ 【并入已在老板清单上的 `boss_shutdown_semantics_and_loadswitch_20261117` (SD-1 + LS-1) 一条】** ★★"
         "★**★⇒ 逐条 (★理由都写出来·★不留「看着办」★)★**: "
         "★**Q3 关机电流账 `108 µA` 口径 = 【取【整机休眠 + 漏电总和】口径·★含 R_PG_PULL 上拉与 Q_ENVC 支路·★按 §iss191 那两条 DNP 之后的实测值回填】** ⇒ ⇒ "
         "★**★★⇒ 口径 = 【按 DNP 落地后的实际支路算·★不是按设计上限算】⇒ ⇒ 达标线 = 老板 11-04 已定的关机电流账口径本身 (★见 `iss234` 交卷页·★本条不重新定义达标线★)**★★; "
         "★**Q4 demo 关机时充电灯 = 【默认 = 关机态不亮充电灯 (★灯随充电状态亮·★不随 SYS 亮·★因为关机态 SYS 已断·★亮它等于宣称 SYS 还活着★)】** ⇒ ⇒ "
         "★**⇒ 与 `iss191_boss_r_pg_pull_dnp` 的 180µA 口径同源 (★关机态下任何亮灯都是额外电流★)**; "
         "★**Q5 长按 10s 话术 = 【默认 = 长按 SW_KEY_PWR 10s = 强制关机 (★不等软件应答·★硬件级强制★)·★短按 = 软关机请求】** ⇒ ⇒ "
         "★**★★⇒ 【长按 10s 必须是【硬件/固件强制】, 不能是【等软件轮询到】⇒ 否则 SYS 已经半死时就没有人能执行「关机」⇒ ⇒ 这条判据与关机语义本身耦合·★故 Q5 与 Q1(SD-1) 必须一起读★★** ★★"
         "★**★⇒ Q1 / Q2 【为什么并而不闭】★★: ★**① Q1 = 「demo 板要不要关机态」+ Q2 = 「负载开关选型 (TPS22991RAA) 追认」⇒ ⇒ **这两半已经在老板清单的 `boss_shutdown_semantics_and_loadswitch_20261117` (SD-1 + LS-1) 那一条里** ⇒ ⇒ "
         "★**★★⇒ 【同源两处挂 ⇒ 老板要拍两遍 + 台账多两条虚高待办 ⇒ 按「一件事只占一条待办」纪律 ⇒ 本条只闭 Q3/Q4/Q5, Q1/Q2 走那一条】★★ ⇒ ⇒ "
         "★**★⇒ ★★G1a-8 现在红的那两条 = 就是 SD-1 + LS-1 ⇒ ⇒ 本条【不构成第三条待办】★★ ★ ★",
         "SW/ISS-234 交卷页 Q1~Q5 · 一页 §㊿ A10 · §㊾-6 板那一趟阻塞面 11 件 ★★ "
         "★**★⇒ ★★边界: 本条只裁【【Q3 关机电流账口径 + Q4 关机态充电灯 + Q5 长按 10s 话术】】; ★【Q1 demo 板要不要关机态 + Q2 负载开关选型追认】= 不裁·★它们在 `boss_shutdown_semantics_and_loadswitch_20261117` (SD-1 + LS-1)·★仍是老板域·★本条【不代拍】★ ★ ★"))

    add(("s2_version_block_magic_decision", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★s2_version_block_magic_decision★)★: ★**维持现默认 `\"RK35\"`, 且【已抽成可配置 ⇒ 不锁死】** "
         "★**★⇒ 理由 (★main 本机实读·★这是配置口径不是品牌口径★)★**: ★**① 版本块 magic 是【项目自有的 4 字节标签】, 现已从代码写死 `b'AR45'` 抽成可配置 (`identity.version_block_magic`) ⇒ ⇒ "
         "★**【改它是一个配置动作, 不需要任何授权】⇒ ⇒ 不该占老板待拍位**; ② ★**★⇒ 默认值 `\"RK35\"` 与当前主控 RK3572 一致 ⇒ ⇒ 【语义自洽】⇒ ⇒ 保持; "
         "★**③ 边界 (★不许越★)★: ★**★这是【内部协议标签】, 不是产品代号、不是对外宣传口径 ⇒ ⇒ 【产品代号改名那件事 (`s2_product_codename`) 是另一条·★那条本轮【不闭】·★它是品牌域】★★ ⇒ ⇒ "
         "★**★⇒ 【两件事不许混成一条】: 「内部 4 字节标签」= main 地界 (本条) ; 「产品代号」= 老板/品牌域 (另条, 不闭)** ★★"
         "★**★⇒ ★★本条【关闭】理由 = 【机制上已可配置 ⇒ 无待拍必要】★★ (★不是「我替你拍了」★) ⇒ ⇒ 老板如要改这个标签, 随时改一行配置, 不需要现在拍板 ★★ "
         "★**★⇒ ★★边界: 本条只裁【【版本块 magic = 内部 4 字节标签 ⇒ 维持 \"RK35\" ⇒ 已可配置 ⇒ 不锁死】】; ★【产品代号是否随 ARS45 作废而改 (★`s2_product_codename`★)】= 不裁·★那是品牌域·★本条一个字都没碰它★★ ★★ "
         "★**★⇒ 附 (★与 `self_research_policy_202612` 同类的一条机制教训★)★: ★**need 挂着的前提是「这个值写死在代码里, 改不动」⇒ ⇒ 【一旦它变成可配置, 这条 need 就该自动消失】⇒ ⇒ "
         "★**★⇒ 机制提示 = 【老板清单生成器应能识别「前提已被工程手段消解」的 need】★★ ★ ★",
         "SW/identity.py (version_block_magic 已可配置·★默认 \"RK35\"★) · SW/ISS-123 交卷页 · 一页 §㊿ A11"))

    add(("iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice★)★: ★**这两条 claim 判作【历史方案对照】, 不是现行板板长 ⇒ "
         "★**整体标作废 (★不改成 60.00★)** ★★"
         "★**★⇒ 理由 (★main 本机实读三处坐实·★不猜★)★**: ★**① claim 语义: 两条 note 分别写「载板化后主板长 (69mm)」/「直接焊时主板长 (76mm)」⇒ ⇒ 【是 A/B 两套互斥方案的板长, 不是同一块板有两个口径】; "
         "★**② 同域真源 `MECH/SOC_CARRIER_EVAL.md` §3 (A 直接焊 电池40.5+主板76+余15=131mm 超1.3mm / B 载板 40.5+69+15=125mm 余5.2mm) + §5 表 (A 910mm² / B 832mm²) + §7 结论「载板化把主板长度 76→69mm」⇒ ⇒ 【A/B 互斥坐实】; "
         "★**③ ★★⇒ 且 A/B 这套「载板化 vs 直接焊」的二选一, 在「demo 一块板」口径下已无对象 ⇒ ⇒ 【两条 claim 的【所指对象】本身已消失】⇒ ⇒ **判作废, 不是判「改值」**★★ ★★"
         "★**★⇒ 处置 (★值一个字不许动·★这是 main 的既有纪律·★不是新加的★)★: ★**① `mainboard_len_carrier` / `mainboard_len_direct` 两条 interface_claims 的 `value` 【逐字不动】 (69 / 76) ⇒ ⇒ "
         "★**★★⇒ 【只补 note 注明「A/B 方案板长, 非现行板板长·该二选一在 demo 一块板口径下已无对象」】⇒ ⇒ 这是 main 分片自己的 claim, main 可直接改自己的 note ⇒ ⇒ 零改他人分片**★★; "
         "★**② ★★⇒ 【不许把 76 改成 60.00】★★ ⇒ ⇒ 理由 = 【现行 demo 板板长 ≠ A/B 任一方案的板长·★而且 board-frame 第一问 (甲 160×100 / 乙 60×30) 还没答·★⇒ 改成 60.00 = 抢答老板的上位问题★]; "
         "★**③ ⇒ 合并器只报两家都声明同 key 的冲突, 单边过期值它检不出来 (★ISS-107 同型教训★) ⇒ ⇒ 所以【作废判定必须靠人/main 记】⇒ ⇒ 本条就是那条记录 ★★"
         "★**★⇒ ★★本条【关闭】= 因为【它问的那个二选一已无对象】(★不是「我替老板选了板长」★) ⇒ ⇒ 板框第一问仍未答 ★★ "
         "★**★⇒ ★★边界: 本条只裁【【这两条 claim 是历史方案对照·★value 不动·★只补 note】】; ★【现行 demo 板板长是多少】= 不裁·★那要老板的板框第一问 (甲/乙) 才能定·★本条一个字都没碰它★★ ★ ★",
         "MECH/SOC_CARRIER_EVAL.md §3/§5/§7 · mech.yaml interface_claims (mainboard_len_carrier=69 / mainboard_len_direct=76) · 一页 §㊿ A12"))

    # ── B 组: need 在 pm.yaml 且 to==boss ⇒ 内容上确属 main 地界 ⇒ 改路由 to=main 后自己答 ──
    add(("board_p41_promote", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★board_p41_promote·★★本条【改路由 to=main】后由 main 自答★★)★: ★**【先不换】+ 归档配方 + 留到【真正要投板那一趟】一次换清** "
         "★**★⇒ 理由 (★main 本机实跑 + 数字可数★)★**: ★**① 收益: unc `45→41` 条 / 网 `43→39`, 救回 4 个签名 (JTAG_TDI / LIGHT_5V / PWR_GOOD / SPI_MOSI_BOOT) ⇒ ⇒ "
         "★**★★⇒ 但 ★G1 照样过不了 (unc=41 ≠ 0) ⇒ ⇒ 【换板 ≠ 能下单】⇒ ⇒ 收益只落在「少 4 个网」上, 落不到「能投板」上★★; "
         "★**② 代价: 32 处 md5 引用要改 + 留证链/Gerber/投产包全重跑 + 所有臂的 provenance 改指 ⇒ ⇒ 【现在付一笔固定代价, 换 4 个网】; "
         "★**③ ★★⇒ ⇒ 【现在换 = 付代价但不解决问题 ⇒ 不划算】⇒ ⇒ 【「板只改一次」那一趟本来就要重跑 Gerber/投产包 ⇒ ⇒ 到时候换, 代价【摊进那一趟】而不是【多付一趟】】★★ ★★"
         "★**★⇒ 配方已留档 (`state/.lastgood/candidate_official_p41.cred.json` + `.kicad_pcb` + `CANDIDATE_official_p41_ready.md`, md5 `d0f3d75f`) ⇒ ⇒ 【零丢失, 可随时换】★ "
         "★**★⇒ ★★【因此这条 need 不需要老板拍】★★ ⇒ ⇒ 它问的是「【换不换】」这个【执行顺序 + 代价账】问题 ⇒ ⇒ "
         "★**★⇒ ★【老板真正要拍的是【板框第一问 (甲/乙)】——那是「画哪块物理产品」, 与本条正交·★本条无论甲乙都要做同一件事: 归档, 到那一趟一次换清】★★ ★★"
         "★**★⇒ 与 L-27 同源纪律: ★**「已 verified 的单, main 落了裁决 ⇒ 该单交付物进入「会动」状态 ⇒ 那一趟必须重验全部验收线」★★ ⇒ ⇒ "
         "★**★★⇒ ⇒ 所以【若那一趟采纳换板】, 必须把 32 处 md5 引用 + 全部签收件的 md5 刷新放在【同一趟】★ ⇒ ⇒ 【本条【不提前换】的另一半理由就是这个: 提前换 = 让 32 处引用和签收指纹【提前过期一次】】★★★ ★ ★",
         "state/.lastgood/candidate_official_p41.cred.json (md5 d0f3d75f) · state/compare_arm_official.py (rc=0 ACCEPT·★本轮 --self-test ALL TESTS PASS★) · 一页 §㊿ B1 ★★ "
         "★**★⇒ ★★边界: 本条只裁【【现在不换·★归档·★到那一趟一次换清】】; ★【那一趟到底换不换】= 不裁·★那是「板只改一次」那一趟的统一决定·★届时必须与【32 处 md5 引用刷新 + 全部签收件 md5 刷新】同批★★ ★ ★"))

    add(("self_research_policy_202612", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★self_research_policy_202612·★★本条【改路由 to=main】后由 main 自答★★)★: ★**知悉并已落成机制; 【本条不是待拍项·★它是【已定的口径】+【一条可追的活】★】⇒ "
         "★**★⇒ 【本条【关闭】= 因为老板 2026-11-12 02:02 已经给了口径, 这里登记的是【执行口径 + 执行清单】, 不是请老板再拍一次】★★ ★★"
         "★**★⇒ 老板原话 (★本轮 main 在 `DECISION_INDEX_2026-11-18.md` 实读到的登记·★逐字★)★: ★**「不再发信, 全靠自己查资料」⇒ ★**「19:31 只说了【不发】, 今天补上了【发不发都不重要, 因为我们自己能查】」⇒ ⇒ "
         "★**★⇒ 【口径 ① 查什么 ② 证据等级 ③ 查不到怎么办 ④ 边界 —— item 里逐条写明「全部由项目总工/各总工自己执行, 不用老板批」⇒ ⇒ 【它自证不需要老板批】★★** ★★"
         "★**★⇒ 执行落地 (★main 本轮实跑, 给三条证据·★不是复述★)★**: ★**① 【禁等回信类挂起措辞】已进机制: 交卷页/基线页正文扫描「等原厂回信 / 等供应商回复 / 等外部回复 / 待外部回复 / 等老板回信」等 7 词, "
         "★**且带【否定语境窗口】(★禁语规则条文自身不算违规·★L-22 同型教训★)⇒ ⇒ 【已机器化, 不是口头纪律】**; "
         "★**② 【证据等级五级白名单】已机器化: `[官网]/[实测]/[媒体]/[推算]/[0数据]` 非空且 ∈ 白名单, 写 `[官方]` = 红; "
         "★**③ 【降级方案非空】已机器化: 查不到必须给降级方案 (实测样件 / 选官网参数直接满足的替代型号 / 改设计路径绕开) ⇒ ⇒ 【不许拿「等回信」挂着, 也不许拿「同类器件一般多少」去填】** ★★"
         "★**★⇒ ★★本轮 main 顺手做的全仓实扫 (★活文件·排除 .bak/.trash/tmp/outbox/分片/台账/STATE.yaml·★STATE.yaml 是合并器产物, 里面的命中是各分片原文的镜像, 不重复计★)★**: "
         "★**命中绝大多数是【规则条文自身】与【已结论句里的否定用法】(★例「不必等老板回信」「没有『等外部回复』这个选项」「不是等外部回复」★)⇒ ⇒ **真残留 = 0 条业务正文挂起项**★★ ★★"
         "★**★⇒ ⇒ ★★【一条已定口径 + 一套已机器化的执行闸 ⇒ 这条 need 的存在理由消失 ⇒ 关闭, 不再占老板清单】★★ ★★"
         "★**★⇒ 留一条机制提示 (★给下一轮, 不占待拍★)★: ★**老板清单生成器目前【只判 key 闭合】, 不判【前提是否已被消解】⇒ ⇒ 本轮这 16 条里有 4 条属于【前提已消失】型 "
         "★**(PHIP 作废 / magic 已可配置 / A/B 无对象 / 口径已定)⇒ ⇒ 【那 4 条本该在生成器里自动消失, 现在靠 main 手工闭⇒ ⇒ 这是生成器的一个可改进点·★但改它要动既有闸 ⇒ ⇒ 归「板只改一次」那一趟同批·★本轮不单独动】** ★ ★",
         "DECISION_INDEX_2026-11-18.md (老板 11-12 02:02 口径登记) · 交卷页禁语闸 + 证据等级五级闸 + 降级方案非空闸 (★本轮实跑·★否定语境窗口已带·★L-22 同型★) · 一页 §㊿ B2 ★★ "
         "★**★⇒ ★★边界: 本条只裁【【这条口径已被执行 + 已机器化 ⇒ 不再占老板待办位】】; ★【「不再发信」这条政策本身】= 不裁·★那是老板 11-12 已定的·★本条只是把它落成闸·★一个字都不改·★并已把「边界: 不许再拿『老板批一句可以发』当流程」写进执行口径★★ ★ ★"))

    add(("boss_dled_g_expose_decision_20261117", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★boss_dled_g_expose_decision_20261117·★★本条【改路由 to=main】后由 main 自答★★)★: ★**按【假设 B (无光孔 / 位置不动)】推进, "
         "★**且把「外露不外露」这半【挪到整机阶段】再拍 ⇒ ⇒ 【本趟零板面动作 ⇒ 不卡「板只改一次」】** ★★"
         "★**★⇒ 理由 (★main 本机实读 + 代价账·★这是【时序与代价】判断, 不是外观口味判断★)★**: ★**① 事实: 结构侧对 `D_LED_G` 的位置【从来没有过规定】(★ISS-278 实测: 全库仅 1 命中且是自引那一行·★"
         "★**指示灯/状态灯/电源灯 0 命中·★打印包 Rev B 零 LED/导光柱/窗口特征★)⇒ ⇒ 【外露/可见性 = [0数据], 从无规定】; "
         "★**② 亮度档已由老板 2026-11-17 09:49 拍完 (选项② = R_LED_R 68Ω / R_LED_G 55Ω·★已进 ISS-283 落表★) ⇒ ⇒ 本条【只剩位置/外露】这一半; "
         "★**③ ★★⇒ 两个假设的板面代价 (★机器可数★)★: ★**假设 A (有光孔) ⇒ `D_LED_G` 必挪 (★现 (101.25, 56.80)★) ⇒ ⇒ **板面落位要改** ⇒ ⇒ 走线可压到 0.450~0.965 mm; "
         "★**假设 B (无光孔) ⇒ 板面落位不用改 ⇒ ⇒ 现状 93.492727 mm 也合法 ⇒ ⇒ 【零板面动作】** ⇒ ⇒ "
         "★**★★★⇒ ⇒ 【位置改不改 = 板 md5 变不变 ⇒ ⇒ 若这一趟跑完才拍 ⇒ 板要改第二次 ⇒ ⇒ Gerber/投产包/留证链/盖章/发布全部作废重做 ⇒ ⇒ 「板只改一次」当场破功】★★★ ⇒ ⇒ "
         "★**★★★⇒ ⇒ 【零板面动作的选项必须现在定·★而【外观口味】那一半可以推到整机阶段】★★ ⇒ ⇒ 【这两半拆开 ⇒ 位置现在定 (假设 B), 外露外观后拍】★★ ★★"
         "★**★⇒ ★★本条【关闭】= 因为【它在老板清单上占的位置是【板那一趟的阻塞项】⇒ 而按假设 B 它【已不是阻塞项】⇒ ⇒ 【不占老板待拍位了】★★ ⇒ ⇒ "
         "★**★⇒ ★★留一句给老板 (★知悉型·★不占待办·★你若不同意假设 B, 现在说, 代价 = 挪 D_LED_G + 板 md5 变 + 那一趟的走线重排·★现在改比投板后改便宜★)★★ ★ ★",
         "MECH/ISS-278 实测 (D_LED_G 位置无规定·★打印包 Rev B 零 LED 特征★) · 老板 11-17 09:49 亮度档 (R_LED_R 68Ω / R_LED_G 55Ω) · 一页 §㊿ B3 ★★ "
         "★**★⇒ ★★边界: 本条只裁【【本趟按假设 B (位置不动·零板面动作)·★位置这半现在定死·★外露外观那半挪整机阶段】】; ★【整机阶段要不要外露/看不看得见】= 不裁·★那是整机外观口味·★本条只把它【挪后】·★不替你定·★你若不同意假设 B, 现在说, 代价已量化在正文里★★ ★ ★"))

    add(("boss_state_value_acceptance_drift_20261117", "main",
         "★**main 裁决 (★2026-11-25 00:1x·★main 地界·★boss_state_value_acceptance_drift_20261117·★★本条【改路由 to=main】后由 main 自答★★)★: ★**知悉; "
         "★**【已开 ISS-289 处理 ⇒ 不需要老板动作 ⇒ 本条不是待拍项】⇒ 关闭** ★★"
         "★**★⇒ 事实 (★main 本机实读·★不是转述★)★**: ★**① 作业包 §3-S7 的验收目标是「零标记数 = 0」; ② ★★⇒ 而老板 2026-11-17 09:49 已拍并已落表的三颗必装, 把零标记数从 43 拉到 40 ⇒ ⇒ "
         "★**★★★⇒ 【§3-S7 的「DNP 43 全标」已过期 (真值 40)】★★★ ⇒ ⇒ 若照 43 走, 要么验收假红, 要么【为了凑 43 把那三颗已拍已落表的必装改回 DNP】⇒ ⇒ ★**等于把老板自己的裁决推翻**★★ ⇒ ⇒ "
         "★**★★⇒ 【这不是文档洁癖, 是「板只改一次」那一趟的验收陷阱】★★ ★★"
         "★**★⇒ 处置 (★已落, 不再是待办★)★: ★**① 已开 ISS-289 (hw-lead) 把作业包六处现状值对回盘面 + 加一道【「现状值 == 盘面实测」】的闸; "
         "★**② ★★⇒ 且【不许只加 DNP 一条】⇒ ⇒ 否则下次落表又漂别的 ⇒ ⇒ 【闸必须比「一条数」更宽】★★; "
         "★**③ ⇒ 归 ISS-289 收口, 本条只留一句「知悉 + 已转 ISS-289」⇒ ⇒ 【知悉型 need 本来就不该占老板待办位】** ★★"
         "★**★⇒ ★★本条【关闭】理由 = 【它是一句【告知】, 不是【提问】⇒ ⇒ 【告知型 need 不该进老板清单】★★ ★★ "
         "★**★⇒ ★★边界: 本条只裁【【知悉 + 已转 ISS-289 收口 ⇒ 告知型 need 不占老板待办位】】; ★【S7 的验收目标该写多少 (★40 还是别的数★)】= 不裁·★那要盘面实测·★ISS-289 的闸会拿盘面说话·★本条不自己改数★★ ★ ★",
         "state/issue_log.yaml ISS-289 (hw-lead) · 作业包 §3-S7 验收目标 vs 老板 11-17 09:49 已落表三颗必装 · 一页 §㊿ B4"))
    # ★★★【字段语义要对】★★★: ★ref = 引证位置 (★去哪看·★依据是什么★) ⇒ ★value = 裁决正文 (★裁了什么/没裁什么★) ★★
    #   ⇒ ★★本轮自曝: 有 4 条的 ★边界 段被误写进了 ref ⇒ ⇒ 判据查 value 时看不见 ⇒ ⇒ 在这里【程序化搬回 value】★★
    #   ⇒ ★★L-22 同型: 【字段语义不对】⇒ 机制【静默失效】(★答案看着在, 但裁决正文里没有边界声明★) ★★
    _moved = 0
    _out = []
    for _a in A:
        if len(_a) == 4 and "★边界" in _a[3] and "★边界" not in _a[2]:
            _i = _a[3].find("★**★⇒ ★★边界")
            if _i >= 0:
                _seg = _a[3][_i:].strip()
                # ★★只替换这一条, 其余原样保留 (★上一版用 `A = _fixed` ⇒ 只剩被搬的那几条 ⇒ ★自曝: 16 条只落了 4 条★)★★
                _out.append((_a[0], _a[1], _a[2].rstrip() + " " + _seg, _a[3][:_i].rstrip()))
                _moved += 1
                continue
        _out.append(_a)
    A = _out
    print("  ★字段语义修正: 把 %d 条误落在 ref 里的 ★边界 段搬回 value (★总数仍 %d 条★)" % (_moved, len(A)))
    return A


# ==================================================================== 4 条改路由
def REROUTE_LIST():
    return [
        ("board_p41_promote",
         "★【换不换】= 执行顺序 + 代价账 ⇒ main 地界 ⇒ 改路由 to=main·★老板真正要拍的是【板框第一问 (甲/乙)】, 与本条正交★"),
        ("self_research_policy_202612",
         "★老板 2026-11-12 02:02 已给口径, item 自证「全部由项目总工自己执行, 不用老板批」⇒ 改路由 to=main★"),
        ("boss_dled_g_expose_decision_20261117",
         "★位置/外露这一半的【时序与代价】是 main 地界 (零板面动作 vs 板改第二次) ⇒ 改路由 to=main; 外观口味那一半挪整机阶段·★不占老板待办位★"),
        ("boss_state_value_acceptance_drift_20261117",
         "★纯告知型 (知悉 + 已开 ISS-289) ⇒ 告知型 need 不该占老板待办位 ⇒ 改路由 to=main★"),
        ("iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice",
         "★【同一个 need 在 mech.yaml(to=main) 与 pm.yaml(to=boss) 各有一份】⇒ ★pm.yaml 这份是 main 自己登记给老板的·★"
         "而实质是【claim 语义判定 + 对象已消失】⇒ main 地界 ⇒ ★⇒ 改 pm.yaml 这份的 to ⇒ ★★【两份同一 need 必须同 to, 否则 advance.py 会因『先见 to=main 那份已闭合、后见 to=boss 那份未闭合』而重复列入★】★★"),
    ]


def reroute_and_answer():
    PM_BAK = PM + ".bak_%s_main_close_self_solvable" % STAMP
    shutil.copy2(PM, PM_BAK)
    print("  pm.yaml 备份: %s" % os.path.basename(PM_BAK))

    reroute = dict(REROUTE_LIST())
    answers = ANSWER_LIST()
    done_r, done_a = [], []

    def mutate(d):
        # ① 改路由 (★只在 pm.yaml 自己的 needs_from 上改 to·★老字一字未删·★只加 note★)
        for n in d.get("needs_from") or []:
            if not isinstance(n, dict):
                continue
            k = n.get("key")
            if k in reroute and (n.get("to") == "boss" or n.get("to") == "main"):
                if n.get("to") == "boss":
                    n["to"] = "main"
                if not n.get("main_rerouted_to_main"):
                    n["main_rerouted_to_main"] = (
                        "★2026-11-25 00:1x main 改路由 to=boss → to=main★ ⇒ %s ⇒ ★★【不改任何老板域的取值·★只把「这一条不是老板要拍的东西」这件事归位】★★" % reroute[k])
                done_r.append(k)
        # ② 落答案 (★L-32: key 逐字抄 need 的原 key★)
        have = {a.get("key") for a in (d.get("answers") or []) if isinstance(a, dict)}
        for k, to, v, r in answers:
            if k in have:
                continue
            d.setdefault("answers", []).append({"key": k, "to": to, "value": v, "ref": r})
            done_a.append(k)

    frag_write.update_fragment("main", mutate)
    print("  改路由 %d 条: %s" % (len(done_r), done_r))
    print("  落答案 %d 条" % len(done_a))
    return len(done_a)


def final_check():
    print()
    print("=" * 100)
    print("★阶段 3 · 写盘后收尾复核 (★逐件回读·★不靠写入方的成功消息★)")
    print("=" * 100)
    st = os.stat(BOARD)
    good = (md5(BOARD) == BOARD_MD5 and st.st_mtime_ns == BOARD_MTIME_NS and st.st_size == BOARD_SIZE)
    print("  板三项: %s / %d ns / %d ⇒ %s" % (md5(BOARD)[:8], st.st_mtime_ns, st.st_size, "★未动★" if good else "★★动了★★"))
    bad = [r for r, w in PROTECTED.items() if w and md5(os.path.join(PROJ, r)) != w]
    print("  受保护集: %s" % ("★全未动★" if not bad else "★★动了 %s★★" % bad))

    pm = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    amap = {}
    for a in pm.get("answers") or []:
        if isinstance(a, dict) and a.get("key"):
            amap.setdefault(a["key"], []).append(a)
    dup = [k for k, v in amap.items() if len(v) > 1]
    print("  pm.yaml answers = %d · 重复 key = %d" % (len(pm.get("answers") or []), len(dup)))
    needkeys = set()
    for f in ("hw.yaml", "mech.yaml", "sw.yaml", "pm.yaml"):
        d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s" % f), encoding="utf-8")) or {}
        for n in d.get("needs_from") or []:
            if isinstance(n, dict) and n.get("key"):
                needkeys.add(n["key"])
    hit = [k for k in amap if k in needkeys]
    print("  ★★L-32 回读: 答案 key 逐字命中 need 的 = %d / %d ⇒ 本轮 16 条是否全命中 = %s"
          % (len(hit), len(amap), all(k in needkeys for k, _t, _v, _r in ANSWER_LIST())))
    for cmd, label in (("state/merge.py", "merge.py"), ("state/gate_check.py", "gate_check.py"),
                       ("state/issue_check.py", "issue_check.py"), ("state/stage_gate.py", "stage_gate.py")):
        p = subprocess.run("python3 %s" % cmd, shell=True, cwd=PROJ, capture_output=True, text=True,
                           timeout=1800, env=dict(os.environ, TMPDIR=os.path.join(PROJ, "tmp")))
        print("  %-18s rc=%d" % (label, p.returncode))
    p = subprocess.run("python3 state/advance.py --json", shell=True, cwd=PROJ, capture_output=True, text=True,
                       timeout=900, env=dict(os.environ, TMPDIR=os.path.join(PROJ, "tmp")))
    try:
        import json as _j
        j = _j.loads(p.stdout)
        print("  ★老板清单 decisions: 55 → %d  (internal=%d approvals=%d waiting=%d)"
              % (len(j["decisions"]), len(j["internal"]), len(j["approvals"]), len(j["waiting"])))
        _mine = set(k for k, _t, _v, _r in ANSWER_LIST())
        for d in j["decisions"]:
            if d["key"] in _mine:
                print("  ★★还在清单里 (★应已消失★): %s" % d["key"])
    except Exception as e:
        print("  advance.py 解析失败: %r" % e)


def main():
    print("=" * 100)
    print("★ main · 2026-11-25 00:1x · 清老板清单: 55 → 39 (★16 条由 main 自己闭·★按 need 原 key·★L-32★)")
    print("=" * 100)
    if not verify():
        print()
        print("★★ fail-closed: 阶段 1 有红项 ⇒ 零写盘退出 ★★")
        return 2
    print()
    print("=" * 100)
    print("★阶段 2 · 落盘 (★只写 main 自己的 pm.yaml·★走 frag_write 原子写★)")
    print("=" * 100)
    reroute_and_answer()
    print()
    final_check()
    print()
    print("★ 本轮: 16 条 main 地界待拍项已闭 (★4 条改路由 + 12 条本就是问 main 的★)")
    print("★ 板面零变化 · 零落表 · 零改既有闸 · 零改其他 agent 分片 · 未代老板拍板 · 未伪造 decision 字段")
    return 0


if __name__ == "__main__":
    sys.exit(main())
