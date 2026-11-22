#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-260 · hw-lead 分片增量 (★走 frag_write 的原子写★ · 不直接 open(p,w)★)

只做三件事:
  ① 把 `state/land_v_values.py` 那条 artifact 升级成 v1.2 (★ISS-260 修完后的口径★)
  ② 追加 3 条 need (★main 转决策页 / boss 拍 A3+W-1 / sw-lead H-1 重锚★)
  ③ 更新 status (★phase / progress / health / summary★)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "state"))
from frag_write import update_fragment  # noqa: E402

ART_SUMMARY = (
    "★参数化 V 值一键落表器 v1.2 (★ISS-260 修完后的口径★)★ 默认 dry-run · --apply 强制 --boss-decision · "
    "白名单写死 V-3{E,A,D,DEG4} / V-4{680,470,390} / V-2{1,2} · "
    "★**ISS-260 三处改动**: ①【V-2 的锚点改成读当前真源】(定位靠位号+网名, 不再靠 value 串匹配 ⇒ ISS-257 把真源换成真型号之后本工具不会再漂) "
    "②【型号轴与架构轴彻底分开】(型号 = 本工具一个字都不许改, 现值是占位串 ⇒ 拒绝落; 架构 = 归 A3/W-1, 默认按真源现状走, "
    "换架构必须显式 --v2-arch + --v2-model + --v2-evidence 且 --boss-decision 必须写成 A3 = 1/arch=<a>/model=<型号>) "
    "③【落表动作 = 只挪网 USB_D_P_SRC → NET_USB_D_P_TYPEC ⇒ 行数不变 ⇒ 门禁锚点行号一条都不漂移 ⇒ ISS-236 那套 +1 漂移机制整个不需要了】★ "
    "★**新增 --selftest (11 条反向用例, 全在临时副本里做, 真盘零写入)★ · 报错三态分开 (状态漂移 / 已落过 / 重复歧义) · "
    "干跑打逐字 diff + 两轴读数 + 预期 --expect-resolved 变化 + 台账/锚点清单 + H-1 重锚名单 · 落表前备份 + 失败自动回滚 (--rollback) · "
    "落表后 7 道门禁实跑 + 新 md5 打到 stdout★"
)

NEEDS = [
    dict(
        key="iss260_decision_page_a3_w1",
        to="main",
        item=(
            "★请把 ISS-260 §B4 的【A3 / W-1 三个选项表】转进 DECISION_PENDING_2026-11-16.md (★本单一个字没改决策页★)★ "
            "⇒ 顺带做两件事: ①【数字订正】决策页 §A 写「A1+A2+A3 一并拍 ⇒ 一条命令 ⇒ 15 条一次落」⇒ ★**实测【网表侧只能转绿 14 条】"
            "(V-3 13 条 + V-4 1 条) ⇒ 落完仍 4 条 (R4×2 + R9 = V-2 那一趟 + R3 = 板侧那一趟) ⇒ 建议改成【14 条一次落 + 4 条等板那一趟】**★ "
            "②【W-1 拆成三个小问分别拍】W-1a D+ 那颗的架构+型号 / W-1b D− 侧怎么办 (含第四条路 ④ 新增位号 D_ESD_USB_N, ★落表器没有配方, 本单不代拍★) / "
            "W-1c 型号与证据等级 ⇒ 依据: HANDOFF/2026-11-16_hw-lead_ISS260_V2落表路径修复与A3冲突.md §B4 (10 条事实 + 3 个选项表 + 横向对照)"
        ),
        since="2026-11-16",
    ),
    dict(
        key="iss260_boss_a3_arch_and_model",
        to="boss",
        waiting_on="boss",
        since="2026-11-16",
        item=(
            "★ESD 的【架构】与【型号】两件事请分开拍 (★本单只给选项 + 代价, 不代拍★)★ "
            "★**架构轴 (A3 / W-1)**: ① 2脚单通道 (现状 = ISS-257 已落的真源, 零返工, 代价 = D− 仍裸奔) / "
            "② 3脚双通道 (电气上唯一不新增位号就护住 D− 的路, 代价 = 占位 2 焊盘落不下 ⇒ 必须改 footprint + 布线重跑 ⇒ 投板风险最高) / "
            "③ 2脚双向件 PESD5V0S1BA (★对 D_ESD_USB_D 增量价值≈0 —— 它的 pad 序本来就对; 它的正确位置是 D_ESD_CAM★)★ "
            "★**型号轴 (选型级)**: 现状 TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V) = ISS-241 矩阵 ③ 的推荐项 [官网] ★ "
            "★**换架构 ⇒ 必须同时换型号 ⇒ 两轴必须一起拍** ⇒ 落表器侧已做成机器化保证: 凭据不写全两轴就 rc=2 拒绝执行★ "
            "⇒ 依据: HANDOFF/2026-11-16_hw-lead_ISS260_V2落表路径修复与A3冲突.md §B4"
        ),
    ),
    dict(
        key="iss260_h1_reanchor_after_v2_land",
        to="sw-lead",
        since="2026-11-16",
        item=(
            "★V-2 网表侧真落之后要走 H-1 重锚 (★本单没落, 所以现在不用动★)★ ⇒ 沙盒端到端实测的新 md5 (★临时副本实跑★): "
            "网表 02c3cec178d33fdc65e49917b575fe25 / 脚表 2c950b675d1eb52176f00b5ba8e05152 / BOM 94642d07a69e8d60dd2af57f69b93607 (不变) "
            "(旧 网表 e06c1dd633566aa44732762c2ff99d1c / 脚表 287e7861a0d1007748d92d9fbecdd490) ⇒ 四项 (★落表单号 ISS-236 + 文件名 + 新 md5 + 旧 md5★) "
            "要填, 且四项在 HW/SCHEMATIC_LANDING_V1_LANDED.md §16.2 里可查 ⇒ ★**本单没动 SW/ 一个字节 (只登记 need)★**"
        ),
    ),
]

STATUS = dict(
    phase="delivered",
    progress_pct=100,
    health="绿",
    summary=(
        "★ISS-260 交卷 (2026-11-16 22:42~23:3x, hw-lead)★ 目标: 把 state/land_v_values.py 的 V-2 落表路径修回可用 + 补 --selftest ⇒ "
        "老板拍完 A1/A2/A3 后决策页承诺的「一条命令 ⇒ 一次落」必须重新成立 ★ "
        "★**只改了 state/land_v_values.py 一个文件** (V-2 段整段重写 + --selftest + --v2-arch/--v2-model/--v2-evidence + 报错三态)· V-3/V-4 两套配方一个字没动 ★ "
        "★**三处核心改动**: ① 锚点改成【读当前真源】(靠位号+网名, 不再靠 value 串匹配 ⇒ ISS-257 改了真源也不会再漂) "
        "②【型号轴与架构轴彻底分开】(型号 = 本工具一个字都不许改 ⇒ 现值原样保住 ⇒ ISS-257 的真型号不会被降级成判据串; 现值是占位串 ⇒ 拒绝落; "
        "架构 = 归 A3/W-1 ⇒ 默认按真源现状走, 换架构必须显式 --v2-arch + --v2-model + --v2-evidence 且 --boss-decision 必须同时覆盖两轴) "
        "③ 落表动作 = 只挪网 ⇒ 行数不变 ⇒ 门禁锚点行号一条都不漂移 (ISS-236 那套 +1 漂移机制整个不需要了) ★ "
        "★**实测**: --decision V-2=1 干跑 rc=0 · V-2=2 rc=2 · V-3=E rc=0 · V-4=680 rc=0 · --apply 缺凭据 rc=2 · --selftest rc=0 (11 条反向用例) "
        "· 沙盒端到端 --apply rc=0 (★老板明天拍 A3=① 不会再撞 rc=3★) · 联合 A1+A2+A3 一次落 rc=0 (落完 --expect-resolved = 4 条) "
        "· 门禁 9 条全按预期 (expect-resolved rc=1 仍 18 条一条没上升 / check_stage_g1a rc=1 只差 G1a-4+G1a-8 / ERC=0 / K=0 / G1a-7 rc=0) "
        "· merge rc=0 + gate_check rc=0 (Q1 18/18) ★ "
        "★**边界**: 真盘全程没带过 --apply ⇒ 网表/脚表/BOM/板/原理图一个字节没动 (5 个受保护 md5 逐字节不变) · 没改 gen_netlist.py · "
        "没改 check_netlist_selfconsistency.py 的 EXPECT 判据 · 没碰 SW/ MECH/ · 没碰 issue_log / 决策页 / 别人的分片 · 零外发 · 不代拍 ★ "
        "★**第三件交付物 = A3/W-1 决策材料** (10 条事实 + 3 个选项表 + 横向对照 + 建议把 W-1 拆三个小问 + 数字订正 15→14) 在交卷单 §B4, 由 main 转决策页 ★"
    ),
)


def mutate(d: dict) -> None:
    # ① artifact 升级 (原地升级, 不追加重复条目)
    for a in d.get("artifacts", []):
        if a.get("path") == "state/land_v_values.py":
            a["kind"] = "tool"
            a["version"] = "1.2"
            a["updated_at"] = "2026-11-16"
            a["summary"] = ART_SUMMARY
            break
    else:
        d.setdefault("artifacts", []).append({
            "path": "state/land_v_values.py", "kind": "tool", "version": "1.2",
            "updated_at": "2026-11-16", "summary": ART_SUMMARY,
        })
    # ② needs
    have = {n.get("key") for n in d.get("needs_from", [])}
    for n in NEEDS:
        if n["key"] not in have:
            d.setdefault("needs_from", []).append(n)
    # ③ status
    d["status"] = STATUS
    d["updated_at"] = "2026-11-16"
    d["updated_by"] = "hw-lead"


if __name__ == "__main__":
    update_fragment("hw-lead", mutate)
    print("[iss260_frag] ✅ hw.yaml 已原子更新 → 再跑 python3 state/merge.py")
