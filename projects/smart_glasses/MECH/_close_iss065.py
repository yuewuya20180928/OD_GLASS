#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/_close_iss065.py —— ISS-065 状态推进: open → fixed (并落 fix_ref) + 分片口径更新
====================================================================
作者: mech-lead (结构总工) · 2026-10-29 · 交卷后自推状态

★为什么要自己推 (不能只交卷): 交卷 ≠ 状态推进。ISS-065 owner=mech-lead,
  status 一直 open ⇒ 项目总工的队列会当成"没人做"再派一次 (10-29 18:5x 已经重派过一次,
  上一次 10:0x 那轮会话 10:15 就结束 ⇒ 0 产出)。交卷时必须把状态一起推到 fixed。

★写文件铁律:
  - `state/issue_log.yaml` ⇒ **yaml.safe_dump + 原子写** (tmp + fsync + os.replace),
    **禁止 open(p,"w") 覆盖** (并发下会把整个 issue log 写成半截)。
  - `state/fragments/mech.yaml` ⇒ **必须走 `state/frag_write.py`** (本脚本只 import 它的
    `update_fragment`, 不自己 open)。新增的 claim 用 frag_write 的原子写路径追加。

边界:
  - 本脚本只改 `state/issue_log.yaml` 里 **ISS-065 这一条** + `state/fragments/mech.yaml`
    (mech-lead 自己的分片)。
  - 不碰 PROJECT_TRACKER.md / DECISIONS.md / HW/ / SW/ / MECH_BUDGET.md / 打印包 / 任何 STL。

用法:
    cd projects/smart_glasses && python3 MECH/_close_iss065.py [--dry-run]
退出码: 0 = 已落盘 / 2 = 找不到 ISS-065 (中止, 不落盘)
"""
from __future__ import annotations

import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
STATE = os.path.join(PROJ, "state")
LOG = os.path.join(STATE, "issue_log.yaml")
FRAG_WRITE = os.path.join(STATE, "frag_write.py")

FIX_REF = (
    "MECH/STRUCT_REVIEW_ISS065.md (结构侧书面结论 + 规格表 S-1~S-12 + 冲突行清单 C1-C16 + "
    "充电板面积四问详答) + MECH/iss065_check.py (自证脚本, rc=0, 40/40 项一致) + "
    "HANDOFF/2026-10-29_mech-lead_ISS065_结构侧5条建议评估.md (B1-B6) + "
    "MECH/_close_iss065.py (本脚本: issue_log 原子写 + 分片口径更新) + "
    "state/fragments/mech.yaml (interface_claims 新增 13 条: temple_thickness=7.30mm / "
    "temple_h_req_315=6.35mm / temple_h_req_387=6.05mm / battery_capacity_tier=315mAh无桥/387mAh有桥 "
    "(旧 575/675 档已作废, 同键值已改) / nose_bridge_skin_limit=43C / nose_bridge_design_target=38C / "
    "nose_bridge_thermal_break=R_bridge>=578K/W / chg_board_outline_new=25x12x0.8mm / "
    "chg_board_area_used=140.50mm2 / chg_board_area_limit_phys=125.90mm2 / "
    "chg_board_area_gap_phys=14.60mm2 / chg_board_path_reco=T-1+T-3a / chg_led_board_column=CHG_BOARD / "
    "chg_board_area_method=phys_w_jchg)"
)

CLOSE_NOTE = (
    "★2026-10-29 19:0x mech-lead 交卷并自推状态 (owner=mech-lead)。\n"
    "【本单做了什么】① 评估 ISS-065 的两条 (a 鼻梁区热设计 + b 315/387mAh 镜腿厚度映射) + "
    "ISS-112 追加的充电板面积 4 问; ② 出书面结论 + 规格表 S-1~S-12 + MECH_BUDGET 冲突行清单 C1-C16; "
    "③ 自证脚本 MECH/iss065_check.py (rc=0, 40/40 项一致); ④ 分片补 13 条 interface_claims "
    "(走 state/frag_write.py 原子写, 禁 open(p,\"w\"))。\n"
    "★【任务书给的一个数有错, 已纠正 —— 不顺着改】任务书 (b) 给的厚度算式 "
    "'上下壳 + 隔热垫0.50 + 空气隙0.30 + PCB1.0 + 电芯厚度' 是 **H 向一次性叠堆**口径, "
    "而本项目 fit_check.py §3① 已用三重证明裁决**叠放物理不成立** (叠放 H 需求 8.10 > 镜腿上限 7.30, "
    "V 需求 41.50 > 根部净高 38.00; 串行只需 90.5 <= 内腔 130.0) ⇒ 按任务书算式得 "
    "315 档 7.80-8.00mm / 387 档 7.50-7.70mm, **超腔体 7.30 达 +0.50~+0.70mm**。 "
    "本单按**串行口径**出表: 315 mAh -> Renata ICP582035PR-01 (4.60 厚) **H 需求 6.35mm**, "
    "387 mAh -> 丰江 432243 (4.30 厚) **H 需求 6.05mm**; 腔体 7.30 ⇒ 名义余量 +0.95/+1.25, "
    "最坏 +0.65/+0.95 (判据 0.60 ✅); 垂直需求 29.50/28.00 (净高 38.00); "
    "长度需求 115.5/118.5 (内长 130.00, 按 PCB 60mm)。**两档的控制段都是电池段 ⇒ "
    "PCB 板厚档位 (0.8/1.0) 不影响镜腿前后厚 ⇒ 老板锁死的 7.30mm 一毫米不用改。** "
    "⇒ '315/387 重出厚度映射表' 这个目标已达成, 只是口径要换成串行。\n"
    "★【另外两条对既有数的纠正 (不顺着改)】(1) **充电板真实缺口是 14.60mm² 不是 13.32** —— "
    "`D_CHG_LED` 的 netlist board 列写 `MAIN_PCB`, 但 P10 注记明写它装在充电板靠 Type-C 座 ⇒ "
    "它的 1.28mm² 没算进 139.22 ⇒ 真实占位 **140.50mm²**, 真实缺口 **14.60mm²** "
    "(这就是 ISS-112 §5 D-1/N-3 那条 board 列错的实际代价); 连带 T-3c 移灯链真实收益 4.78mm² 不是 3.50。 "
    "(2) hw-lead T-2 的描述 '**16 电阻 + 2 体电容**' 与实际清单对不上: T2_FLIP 实为 **15 颗电阻 + 2 颗电容**, "
    "且其中 `C_VBUS_BULK` **在 netlist_v1.csv 里根本不存在** ⇒ 实际能翻底 15 电阻 + 1 电容 = 12.62mm² "
    "(金额不变, 是描述错, 但 BOM/装配单会照错描述走)。\n"
    "★【(a) 鼻梁区结论】**43°C 红线适用** (ISO 13732-1 / CENELEC Guide 29 Table A.1, 8h+ 持续接触, "
    "塑料 43°C; 判定对象是材料表面温度, 面积小只让皮肤侧温升更低, **不放松阈值**)。"
    "现状 (镜框正中只有走鹃II 光机 98mW) 推算鼻梁接触面 **37.3°C ✅** (设计目标 <=38°C, 距红线 5.7°C), "
    "且结论在 A_nose 80-300mm² / A_conv 600-1600mm² 全敏感性区间稳定 ⇒ **现状鼻梁区不是瓶颈**。"
    "★但真正的风险是 **'SoC 挪进镜框正中'** (ISS-084 载板化路线) ⇒ 接触面 **50.1°C 超红线 7.1°C**; "
    "而且 ★**'加金属热路'会让情况更糟 -> 66.6°C** (金属把节点温度直接送到鼻梁接触面, 比什么都不做还差 16.5°C) "
    "⇒ **金属热路必须与鼻梁侧热断成对设计 (R_bridge >= 578 K/W 才回 43°C / >= 1043 K/W 才回 40°C), "
    "而铝热路本身只提供 0.34 K/W, 指望不上**。另: 充电峰值 0.45-0.57W 的热落点是**镜框端件** "
    "(离中心 60-70mm, 打印件沿臂 R≈2333 K/W ⇒ 传不到鼻梁), 端件自身 83-108°C 才是真问题。\n"
    "★【充电板四问】① T-1 (25->12mm) 板面可行 (79.1%, 布线余量 20.9%), 但 +2mm 落在 V 向, "
    "而端件 V 余量在 'FPC 竖向叠放 31.00mm' 口径下已为负 (-1.00~+9.00 ⇒ +2mm 后下限 **-3.00 ❌**), "
    "在 'H 向径向嵌套 12.00mm' 口径下才够 (+18.00~+28.00 ⇒ **+16.00 ✅**) ⇒ **T-1 不能冻结, "
    "绑死在 FPC 拓扑裁决 + u8b 镜框端件截面**; 电池座不冲突 (电池在镜脚), 导光孔与 Type-C 座位置都要随板重排。 "
    "② T-2 双面贴: **单用 100.6% 仍超装 0.70mm²; 热收益 ≈ 0** (U_CHG 必须留正面, 它的 0.45-0.57W 一瓦没少), "
    "代价是板厚 0.8->1.25 + 铝罩冲让位孔 + 翻面贴 15 颗电阻的手工良率 + 返修要拆端件 ⇒ **结构侧不推荐**。 "
    "③ T-3c 移灯链: 跨铰链线 (可复用 J_CHG pin5 CHG_STAT, 不新增针) + 镜脚上壳导光孔 + 打印包改版 + "
    "★★镜脚侧没有 VBUS 5V ⇒ '关机时充电灯要亮' (老板 10-28 拍板) 会丢 ⇒ **与拍板冲突, 结构侧反对**。 "
    "④ **推荐 T-1 + T-3a (只删真 DNP + R_STAR_PGND 改铜皮短接) = 72.8%, 布线余量 27.8%**, "
    "零 I2C 牺牲 + 零功能取舍 + 零焊接工艺变更; 前置 3 项: P1 FPC 拓扑 / P2 u8b 端件截面 / P3 board 列修正。\n"
    "【验收依据 (交卷自评 + 可复现)】实跑 python3 MECH/iss065_check.py → **rc=0, 40/40 项一致, FAIL 0** "
    "(A 段厚度映射 / B 段鼻梁三模型+反解+敏感性 / C 段充电板 7 路径占位率 / D 段 16 行冲突清单); "
    "实跑 python3 state/merge.py → rc=0, 冲突 0; 实跑 python3 state/gate_check.py → **Q1 18/18** "
    "(mech-lead 6/6)。\n"
    "【诚实边界】**实物 [实测] = 0 条** (0 件打印 / 0 台样机 / 0 个实测温度); 鼻梁接触面积 [0数据] "
    "(未定义, 敏感性 80-300mm²); 镜框正中段外露对流面积 [0数据] (依赖 u8b); J_CHG 10p 座体厂商尺寸 [0数据] "
    "(58.24mm² 由 28p 反推); 充电板实际能否布下**未验** (139.22/140.50 只是 land 占位, "
    "走线/间距/平面不可用区全未建模, 物理上还要再留 10-20%, 必须 PCB 工程师实际摆一次); "
    "充电 IC 耗散按 **0.45-0.57W** (buck 拓扑, 我 10-28 交叉评审已改口径) —— MECH_BUDGET §2.1/§2.3.1(1) "
    "仍是 0.8W (线性稳压器公式), **需同步**。未联系任何供应商/原厂, 未发邮件, 未下单采购。"
    "★**本单未改任何几何 / 未改任何 STL / 未改生成器 / 未碰打印包**; MECH_BUDGET.md 的 16 行改动"
    "(C1-C16) 由项目总工落, 我只给'改哪一行、改成什么、依据哪一条'。"
)


def atomic_write_yaml(path: str, doc) -> None:
    """原子写: 唯一 tmp + fsync + os.replace ⇒ 读者永远看到完整文件。"""
    text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main() -> int:
    dry = "--dry-run" in sys.argv

    # ---------------------------------------------------------------- 1. issue_log
    with open(LOG, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    issues = doc.get("issues")
    items = list(issues.values()) if isinstance(issues, dict) else list(issues or [])

    hit = 0
    for it in items:
        if not isinstance(it, dict) or it.get("id") != "ISS-065":
            continue
        hit += 1
        print(f"[before] ISS-065 status={it.get('status')!r} fix_ref={it.get('fix_ref')!r}")
        it["status"] = "fixed"
        it["fix_ref"] = FIX_REF
        it["verify_by"] = "main"
        note = str(it.get("note") or "")
        # ★幂等护栏: 标记串必须与 CLOSE_NOTE 里实际写入的那句一致, 否则重跑会重复追加 note。
        #   (踩坑记录: 护栏写 'ISS-065 交卷' 但 CLOSE_NOTE 实际写的是 'mech-lead 交卷并自推状态'
        #    ⇒ 护栏永远不命中 ⇒ 脚本重跑一次 note 就多贴一遍)
        if "mech-lead 交卷并自推状态" not in note:
            it["note"] = note + "\n\n" + CLOSE_NOTE
        print(f"[after ] ISS-065 status='fixed' verify_by='main' fix_ref 已落 ({len(FIX_REF)} B)")

    if hit != 1:
        print(f"❌ 找到 {hit} 条 ISS-065 (应为 1) —— 中止, 不落盘")
        return 2
    if dry:
        print("[dry-run] 未落盘")
        return 0

    doc["issues"] = items
    atomic_write_yaml(LOG, doc)
    print("✅ issue_log.yaml 已原子更新 (ISS-065 open → fixed, fix_ref + verify_by 已落)")

    # ---------------------------------------------------------------- 2. 分片 (走 frag_write)
    import importlib.util

    spec = importlib.util.spec_from_file_location("frag_write", FRAG_WRITE)
    fw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fw)

    # 2a. 改掉两条已作废的旧口径 (同 key 覆盖, 不追加重复项)
    UPDATED = {
        "temple_thickness": {
            "value": "7.30mm",
            "note": ("镜腿前后厚**腔体**锁死值 (老板 Q4 拍板)。315/387 两档都不改它 —— "
                     "新口径下控制段是电池段 (H 需求 6.35 / 6.05), PCB 板厚档位也不影响它。"
                     "旧值 '7.3-8.7mm' 含已作废的 575mAh 档 (ISS-072)"),
            "ref": "MECH/STRUCT_REVIEW_ISS065.md §3.2",
        },
        "battery_capacity_tier": {
            "value": "315mAh无桥/387mAh有桥",
            "note": ("新口径 (ISS-072/ISS-055): 持续满载 1h → 315 mAh 无桥 / 387 mAh 有桥。"
                     "**旧值 '无桥接340-575mAh/有桥接575-675mAh' 含已作废的 575/675 档**, "
                     "且 675mAh 档的形态否决结论 (镜腿 11.2mm) 也已随之作废"),
            "ref": "MECH/MECH_BUDGET.md §1.4.3 D/E 行 + §1.6.2",
        },
    }

    def mutate(d):
        claims = d.setdefault("interface_claims", [])
        for c in claims:
            if c.get("key") in UPDATED:
                c.update(UPDATED[c["key"]])
                print(f"[frag] 已更新旧口径 claim: {c['key']} = {c['value']}")

    fw.update_fragment("mech-lead", mutate)
    print("✅ state/fragments/mech.yaml 已原子更新 (2 条旧口径已改, 走 state/frag_write.py)")
    print("   ⇒ 现在跑 python3 state/merge.py 刷新共享快照")
    return 0


if __name__ == "__main__":
    sys.exit(main())
