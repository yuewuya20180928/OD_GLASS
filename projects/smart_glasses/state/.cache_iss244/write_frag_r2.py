#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-244 第 2 轮分片登记 (走 state/frag_write.py 的原子写 API; 只加自己的 key)"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "state"))
from frag_write import update_fragment  # noqa: E402

ART_POST_LANDING = {
    "path": "state/.cache_iss244/post_landing.py",
    "kind": "tool",
    "version": "v1.0",
    "updated_at": "2026-11-17",
    "summary": ("★ISS-244 第 2 轮 (2026-11-17 05:0x) 新建: 落表后回归计算模块 (只读) ⇒ 把「板占位 land (pad→net) ↔ "
                "落地器件引脚序 ↔ 网表 note 定的端子角色」三方逐件交叉核对 ⇒ 查出 3 条实物级 P0 (Q_PG 角色本身错 + land 不对 "
                "⇒ 开机路径不通 / Q_AND 栅漏对调 ⇒ 复位链硬件 AND 门不成立 / D_ESD_CAM ESD 器件接反 ⇒ 保护失效 + CSI lane 被钳) "
                "⇒ 每条都给了最小修法 (多是「两个外侧 pad 对调」) ⇒ 只出依据 + 代价, 一条未代拍"),
}
ART_GATE = {
    "path": "HW/check_part_selection_gaps.py",
    "kind": "gate",
    "version": "v1.1",
    "updated_at": "2026-11-17",
    "summary": ("★ISS-244 第 2 轮: 门禁加 C7 (落表后回归表: 已落表的件逐件有行 + 判定 + 出处 + 有引脚序不符必须有修法) + "
                "加两条反向用例 M9/M10 (删一行 / 清空出处 ⇒ C7 红) + 全部用例加「红因指名」自证 (红的那一条必须指名道姓说是哪个目标, "
                "防「随便塌一条也算过」) ⇒ C0~C7 八条断言 rc=0 / selftest 10/10"),
}
CLAIM = {
    "key": "iss244_post_landing_p0_qpg_qand_esdcam",
    "value": ("Q_PG: 写法A (S=BAT_SW / D=ON / G=PG) 才电学自洽; 落地件 DMP3098L 引脚序 1=G/2=S/3=D ⇒ land 目标 = pad1=PWR_GOOD(G) / "
              "pad2=BAT_SW(S) / pad3=PWR_ON(D) (两个外侧 pad 对调, pad2 不动) + 网表 note 角色同批改写法A | "
              "Q_AND: note 角色对 (D=RESET_N/S=GND/G=PG_AND) 但 AO3400A 是 G-S-D ⇒ land 目标 = pad1=PG_AND/pad2=GND/pad3=RESET_N "
              "(两个外侧 pad 对调) | D_ESD_CAM: TPD1E05U06DPYR pin1=I/O / pin2=GND, 而占位 pad1=GND / pad2=CSI_D0_CK_P ⇒ 正好相反 ⇒ "
              "正向 ESD 失效 + CSI lane 负向摆幅被钳到地 | Q_ENVC 与 D_ESD_USB_D 两颗已对上, 不用动 land"),
    "note": ("★[官网]+[实测] 2026-11-17 sw-lead · 依据 = TI SLVSBO7O Table 4-1 (本轮实读, 落盘 state/.cache_iss244/led/tpd4e05u06.pdf) "
             "+ AOS AO3400A p1 Pin Configuration 图 + Diodes DMP3098L p1 Pin Configuration 图 (图上未印引脚号 ⇒ 编号按 JEDEC TO-236 "
             "记 [推算], 与排布 [官网·图读] 分开标注) + 板文件逐焊盘实读 + 网表 L58~L60 / L64~L66 / L161~L162 / L412~L413 实读; "
             "计算模块 state/.cache_iss244/post_landing.py 一条命令可复跑"),
    "ref": "HW/PART_SELECTION_GAPS_CLOSEOUT.md §5.1/§5.2",
}
ANSWER = {
    "key": "iss244_h1_reanchor_round1",
    "to": "main",
    "value": ("★ISS-244 第 2 轮 (2026-11-17 05:0x) = 落表后回归 + H-1 重锚第 1 跳: "
              "① 触发 = 板侧又落了一批选型件 (网表/脚表/BOM 落盘时刻 2026-11-16 22:25:14) ⇒ 登记范围 22 件里 14 件已落表 / 8 件仍待落 "
              "⇒ 本单门禁 C5 按设计变红 (开工时实测 rc=1, 6/7 PASS, C5 红 14 条) ⇒ 走 H-1 重锚 (重算 landed_note + 重判十条缺口 + 留痕), "
              "不许把红灯调没; "
              "② 新增 §5 落表后回归: 三方交叉核对 (板占位 land ↔ 落地器件引脚序 ↔ 网表 note 端子角色) ⇒ 查出 3 条实物级 P0 "
              "(Q_PG 角色本身错 ⇒ 开机路径不通 / Q_AND 栅漏对调 ⇒ 复位链硬件 AND 门不成立 / D_ESD_CAM ESD 器件接反 ⇒ 保护失效 + CSI lane 被钳) "
              "⇒ 每条给了最小修法 (多是「两个外侧 pad 对调」); "
              "③ 门禁加 C7 + 反向用例 M9/M10 ⇒ 交卷绿 = 上游 ISS-241 门禁 8/8 + selftest 9/9 / merge+gate_check rc=0 (Q1 18/18) / "
              "本单门禁 C0~C7 8/8 / selftest 10/10 / LED 数字化自证 2/2 / G-10 分压表 rc=0; "
              "④ 受保护 7 件 md5 与第 1 轮交卷时逐字节相同 (网表 e06c1dd6… / 脚表 287e7861… / BOM 94642d07… / 板 611b869e… / "
              "矩阵 da609d7d… / ISS-241 门禁 fb286e5f…) ⇒ 本轮零落表、零外发、实物 [实测]=0 条; "
              "★V-2 / V-3 / V-4 / G-1 写法 / G-10 / LED 亮度档 一条未代拍"),
    "ref": "HANDOFF/2026-11-16_sw-lead_ISS244_选型缺口自查补全与OPN回填清单.md §7",
}


def mutate(d):
    d.setdefault("artifacts", []).append(ART_POST_LANDING)
    d.setdefault("artifacts", []).append(ART_GATE)
    d.setdefault("interface_claims", []).append(CLAIM)
    d.setdefault("answers", []).append(ANSWER)


if __name__ == "__main__":
    update_fragment("sw-lead", mutate)
    print("sw.yaml 已原子更新 (只加 sw-lead 自己的 key)")
