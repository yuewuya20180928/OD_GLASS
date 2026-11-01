#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-024 状态推进: fixing -> fixed -> verified (项目总工 main 亲核)。

★为什么必须本轮推: mech-lead 22:23 交卷 (ISS-024 会话 22:24:02 结束), 但它明确写明
  "ISS-024 状态由项目总工写, 我不碰 issue_log" ⇒ issue_log 里 ISS-024 卡在 fixing / fix_ref=None。
  ★advance.py 的 in_flight 规则 = "该 agent 名下只要有 status==fixing 的 issue, 本轮就不再派新活"
  ⇒ mech-lead 名下 5 条 open (ISS-025/047/066/076/103) 全被挡住 = 队列断线。
  ★交卷 ≠ 状态推进 —— 交卷和推状态必须成对, 否则下一轮 cron 干等 30 分钟。

★写文件铁律: 原子写 (tmp + fsync + os.replace), 禁 open(p,"w") 覆盖 issue_log.yaml。

★verify_by 纪律: owner=mech-lead, verify_by=main (≠ owner, 符合 issue_check.py 的 C3 验证分离)。

★诚实边界 (写进 verify_result, 不掩盖): 本单实物 [实测] = 0 条 (本机不能打印/量测) ⇒
  全部耐受结论是"预期等级", 不是合格判定; 40 格里 4 格 [0数据] (UV 胶化学耐受);
  阶段门 G2 仍不通过 (唯一卡点 = T-05~T-08 实测回填, 执行方待 boss)。
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

FIX_REF = (
    "MECH/MATERIAL_SELECTION.md (★新增: 材料选型 + 表面处理耐受主产出, §0-§12 共 13 章 / 481 行 / 52KB; "
    "含 §2.1-§2.6 选型表 (镜框/镜腿/鼻托/胶粘剂 4 类/表面处理 6 类/金属件 6 行, 每项带牌号+理由+本项目硬约束+证据等级) "
    "+ §2.7 皮肤接触面逐件清单 6 项 (全项目第一份) + §3.1-§3.4 耐受表 10 材料×4 介质=40 格 (4 格 [0数据]) + "
    "§4.1-§4.4 P2S 打印件 vs 量产件差异 (2 列耐受等级 + 3 条原型独有差距 + 4 条量产新风险 + P0-P2 抹平优先级) "
    "+ §5 表面处理可执行版 + §5.4 用户清洁剂兼容表 + §9 6 条 needs + §10 证据分级/来源清单 8 条) "
    "+ HANDOFF/2026-11-01_mech-lead_ISS024_材料选型与表面耐受.md (B1-B6 六块齐) "
    "+ state/fragments/mech.yaml (interface_claims 新增 14 条 mech_mat_* 前缀 / needs_from 新增 6 条, 全走 frag_write.py 原子写) "
    "+ state/issue_log.yaml (本脚本, 原子写 tmp+fsync+os.replace)"
)

VERIFY_RESULT = (
    "2026-11-01 22:2x 项目总工亲核通过 (verify_by=main ≠ owner=mech-lead)。"
    "★**先说结论口径**: 本单 'verified' = **选型与耐受判据体系已交付且可执行**, "
    "**不等于**任何一项耐受已实测合格 —— 全文 [实测] = 0 条 (本机打印机跨网段不可达/无切片器/无量具), "
    "阶段门 G2 仍不通过, 这是诚实边界不是本单缺陷。"
    "【我独立核过的 4 件事 (不只看它自己报)】"
    "① **算术复核一致**: PA6-CF 湿态层间 80→45 MPa ⇒ -43.75% (它报 43.8%) ✅; "
    "整体刚度 151→95 MPa ⇒ -37.09% (它报 37.1%) ✅; T-08 2000 h UVA-340 ÷ 24 = 83.3 天 (它报 ≈83 天) ✅; "
    "Mg -2.37 V vs Al -1.66 V 电位序 ✅。⇒ **它没有把推算冒充实测, 数字口径自洽**。"
    "② **验收 3 条逐条对照原文核过**: §2.1-§2.6 选型表每个部位都有 '材料+牌号+理由' (非泛泛而谈) ✅; "
    "§3.2 主表 10×4=40 格且 §3.4 单独列出 8 项 [0数据] ✅ (4 格全在 UV 胶 LOCTITE AA 3311 上 —— "
    "官方只给了固化特性/ISO-10993/间隙<0.25mm, 没给耐汗耐化妆品耐醇耐UV, 而 T-06 硬判据正卡在这); "
    "§4.1 直接接 MECH_BUDGET §5.5 原表补 2 列耐受等级 ✅。"
    "③ **状态源侧核对**: merge rc=0 (产出 117 / 阻塞 34 / 冲突 0); gate rc=0 **Q1 18/18**; "
    "interface_claims 359 条 (mech 159) **冲突 0** —— 新增 14 条 mech_mat_* 与三方既有 key 无重名; "
    "6 条 needs **全部带 waiting_on + due** (vendor 11-10 / boss 11-08,11-12 / jbd 11-10) ✅ 符合协议第 5 条。"
    "④ **边界核对**: 交接单明写未联系任何供应商/原厂、未发邮件、未下采购单 (只读公开官方页 8 个来源) ✅; "
    "未改 HW/ SW/ PROJECT_TRACKER.md / DECISIONS.md / RELIABILITY_TEST_PLAN.md ✅; 未碰 issue_log (交给我写) ✅; "
    "★未擅自改已 verified 的 RELIABILITY_TEST_PLAN.md —— 它把 'T-05 后拉脱 ≥ 干态 80%' 写成**建议**等我裁, 守住了边界。"
    "【★它抓到的 3 条真问题 (我认可并已登记待裁)】"
    "① **'换镁合金更防汗'是错的**: Mg 电位 -2.37 V 比 Al -1.66 V 更活泼, 划伤即点蚀 ⇒ 防汗靠表面处理体系 + 不做贴肤, 不靠换材;"
    "② **阳极 Type III (~50% 堆积) 会吃掉 ≤5 µm 定位面精度** ⇒ 定位孔/面必须阳极后精加工 (或阳极前孔径留 +0.02~0.05 mm), "
    "否则 PIN-SET-2 的 ≤0.046 mm 定位重复性不成立 —— ★**这条与 ISS-122 的板厚 1.22 mm 破锁结论叠加**, "
    "同时说明材料工艺链会吃掉几何公差余量, 已在 needs 里问表面处理方; "
    "③ **PA6-CF 湿态层间掉幅 (43.8%) > 整体刚度掉幅 (37.1%)** ⇒ 螺钉柱沿 Z 拉脱在汗液下余量最小, 建议追加判据 'T-05 后拉脱 ≥ 干态 80%' (待我裁, 未擅自改已 verified 的测试方案)。"
    "【未决 / 卡点】① **T-05~T-08 实物实测仍 0/10 项** —— R6-1..R6-6 材料试样送检执行方待 boss (due 11-08), "
    "T-08 (2000 h ≈ 83 天) 应最先排期; ② UV 胶 4 项化学耐受等原厂 (due 11-10); "
    "③ 鼻托压力/佩戴/稳定/时长 4 项判据它**没有自己拍板** (登记 need 等 boss), 守住了边界 ✅。"
)

CLOSE_NOTE = (
    "★2026-11-01 22:2x 项目总工关单 (owner=mech-lead, verify_by=main)。"
    "【交卷时间线】22:06 cron 派活 (ISS-024 → mech-lead) → 22:23 产出落盘 → 22:24:02 会话结束。"
    "★**交卷 ≠ 状态推进**: mech-lead 按边界纪律没碰 issue_log (交给我写) ⇒ issue_log 卡在 fixing/fix_ref=None, "
    "而 advance.py 的 in_flight 规则会让 mech-lead 名下 5 条 open 全被挡 ⇒ **本轮必须由项目总工推状态**, 否则队列断到下一轮 cron。"
    "【交付内容】材料选型 12 项 (原型 PA6-CF+PU 封闭涂层 / 量产 镁合金 ADC12 镜框+PC/ABS 镜腿+Al6063-T6 骨架) "
    "+ 皮肤接触面逐件清单 6 项 (全项目第一份) + 耐受表 10×4=40 格 (4 格 [0数据]) + P2S vs 量产差异 (2 列耐受等级) "
    "+ 表面处理可执行版 + 用户清洁剂兼容表 + 14 条 interface_claims + 6 条 needs。"
    "【诚实边界】[实测] = 0 条 ⇒ 全表是'预期等级'不是合格判定; 阶段门 G2 仍不通过 (卡点 = T-05~T-08 回填, 执行方待 boss due 11-08); "
    "8 项 [0数据] 全部登记 needs, 未编造牌号性能。"
    "【我已裁决的两条待办】① '换镁合金更防汗' = 错 (Mg 更活泼) —— 防汗靠表面处理体系 + 不做贴肤; "
    "② 'T-05 后拉脱 ≥ 干态 80%' 建议判据 —— **我暂不改 RELIABILITY_TEST_PLAN.md (已 verified 的方案), 留到 T-05 用例卡定稿时一并裁**。"
    "未联系任何供应商/原厂/JBD (JBD 相关走 needs 经我); 未改 HW/ SW/ PROJECT_TRACKER.md §0 锁死表。"
)


def atomic_write(path, data):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=100)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main():
    with open(LOG, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    hit = 0
    for it in d.get("issues") or []:
        if it.get("id") != "ISS-024":
            continue
        assert it.get("owner") == "mech-lead", f"owner 不是我, 不该改: {it.get('owner')}"
        assert it.get("status") == "fixing", f"状态不是 fixing, 不该推: {it.get('status')}"
        it["status"] = "verified"
        it["fix_ref"] = FIX_REF
        it["verify_by"] = "main"
        it["verify_result"] = VERIFY_RESULT
        it["verify_date"] = "2026-11-01"
        it["note"] = CLOSE_NOTE
        it["need_keys"] = [
            "mech_mat_vendor_datasheet",
            "mech_mat_skin_coating_decision",
            "mech_mat_anodize_process",
            "mech_mat_waveguide_uv_cosmetic",
            "mech_mat_sweat_test_spec",
            "mech_mat_nose_pad_criteria",
        ]
        hit += 1
    assert hit == 1, f"没找到 ISS-024 (命中 {hit} 条)"
    atomic_write(LOG, d)
    print("✅ ISS-024: fixing → verified, fix_ref 已落, verify_by=main, 6 条 need_keys 已登记")
    return 0


if __name__ == "__main__":
    sys.exit(main())
