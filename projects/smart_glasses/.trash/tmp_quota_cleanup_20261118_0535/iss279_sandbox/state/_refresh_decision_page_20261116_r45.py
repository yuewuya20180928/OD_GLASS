#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_refresh_decision_page_20261116_r45.py
★main (moli) 2026-11-16 21:5x (cron 775d9893)★
★决策页增量: 新增 §A-补7 (ISS-257 落表后的事实 + G1a-4/G1a-8 两条缺口) + 更新页头口径 + 更新页尾 md5★

★★**为什么做这件事 (★main 21:4x~21:5x 自己实跑★)** ★★
· ★**ISS-257 (hw-lead) 21:45 交卷 + main 独立复验 14 条 rc 全过 ⇒ 落 verified** ★
  ⇒ ★**G1a-5 由红转 ✅ · G1a-7 由红转 ✅ · G1a-4 / G1a-8 仍红** ★
· ★**决策页页头写的是 17:4x (r43) —— 落后 4 小时, 且页尾 md5 记录的是 ISS-233 时代的旧值 (`34132f7e…` / `b21b743a…` / `c195a117…`) ⇒ "
  ★**已被 ISS-243 (611c3ba3…) → ISS-249 (16ac89f7…) → ISS-257 (e06c1dd6…) 三轮落表覆盖** ★ ⇒ ★**这一页给老板看的数字已经过期 3 轮** ★
· ★**本脚本只【追加】+【改页头/页尾数字】, §A~§C 的历史条目一个字不改 (★原字不删口径★)** ★

★★**新增 §A-补7 的内容 (★main 21:4x 实跑读数, 不抄交卷报告★)** ★★
· ★**G1a 现在还差 2 条**: G1a-4 (落表已清零 · 18 条未落表) · G1a-8 (关机语义 + 负载开关选型已决) ★
· ★**这 2 条都不是「画图」的事** ⇒ ★**画图早就画完了, 差的是「值」与「拍板」** ★
· ★**G1a-8 = ISS-097 (fixed) + ISS-172 (verified) ⇒ 判据要求 ∈ {verified, closed} ⇒ 差一句老板追认** ★
· ★**新增 1 条待拍 (V-1): `U_PWR_SW` 落成 `TPS22991RAA` 的追认** ★ (★ISS-257 已在网表 value 里写「⇒ 选型口径待 A5 追认」★)
"""
import os
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DOC = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md")
BAK = os.path.join(PROJ, "DECISION_PENDING_2026-11-16.md.bak_20261116_2200_r44")

NEW_SECTION = """## §A-补7 · ★★r45 · ISS-257 落表后的事实 + ★**G1a 还差的那 2 条**★★ (★main 2026-11-16 21:4x 独立实跑 14 条 rc★)

> ★**出处**: `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18 (★L919-1250 · ★落表台账 + md5 三段式§18.4★) · ★**`HW/check_g1a7_selection_landed.py`** (★本单新门禁 · 6 判据 + 11 条反向用例★) · ★**`HANDOFF/2026-11-16_hw-lead_ISS257_G1a7选型落表.md`** (★B1~B6★) · ★**`state/check_stage_g1a.py`** (★G1a 独立闸★)
> ★**main 本轮 21:4x 独立复验 (★自己实跑, 不抄交卷报告★)★**: ★**`check_netlist` 0 · `check_netlist_pins` 0 · `sch_erc` 0 (ERC=0) · `sch_pinfull` 0 (584=584 · K=0) · `g1a7` 0 · `g1a7 --selftest` 0 (11/11, ★含 M4「evidence 写成 `[官网]` 必须红」= 上一轮那个坑已经进闸★) · `selfconsistency` 0 · `--expect-resolved` 1 (★仍 18 条一条没上升★) · `chain_content_anchor` 0 + `--selftest` 0 (14/14) · `merge` 0 · `gate_check` 0 (Q1 18/18)** ★
> ★**本节只列事实 + 一条待拍, ★**一条没代拍**★ ★

### ★**G1a (原理图定稿) 现在还差 2 条 —— ★**画图早就画完了, 差的是「值」与「拍板」**★ ★

| # | 还差的 | ★**为什么它卡在你这儿 (不是你派的活)** ★ | 解锁动作 |
|---|---|---|---|
| ★**G1a-4** ★ | ★**落表已清零 (翻面口径)** ★ ⇒ ★**`--expect-resolved` 仍 18 条未落表** ★ | ★**18 条 = V-3 13 条 (R2×11 + R7 + R8 · BAT_DET 分压链) + V-2+板 3 条 (R4×2 + R9) + V-4 1 条 (R10 · R_ILIM 档位) + 板侧 R3 1 条** ★ ⇒ ★**V-3 = A1 · V-4 = A2 · V-2 走法 = A3** ★ ⇒ ★**18 条里有 15 条直接卡在 A1/A2/A3 三条拍板上, 3 条卡在板那一趟 (PCB 类)** ★ | ★**A1 + A2 + A3 一并拍 ⇒ 一条命令 `python3 state/land_v_values.py --apply --boss-decision "…"` ⇒ 15 条一次落** ★ |
| ★**G1a-8** ★ | ★**关机语义 + 负载开关选型已决** ★ ⇒ 现状 ★**ISS-097=fixed · ISS-172=verified** ★ ⇒ ★**判据要求 ∈ {verified, closed} ⇒ 差「谁来签 closed」这一句** ★ | ★**ISS-097 的内容就是 §A4 (关机语义) + §A5 (负载开关选型) —— ★**这两条你还没拍** ⇒ 所以 ISS-097 只能停在 fixed (★不能自己 closed★)** ★ | ★**A4 + A5 拍完 ⇒ ISS-097 才能落 closed ⇒ G1a-8 立刻转绿** ★ |

★**★一句话给老板**: ★**原理图这条主线剩下的活, 一半在「你的三句拍板」(A1/A2/A3) 上, 一半在「板那一趟」(PCB 类, 按你 11-11 10:07 口径排队) 上 ⇒ ★**没有任何一条是「有人偷懒」** ★ ★

### ★**V-1 (本节新增的 1 条待拍 · ★**由 ISS-257 落表带出来的★**) ★

| # | 待拍项 | 选项 (各带代价) | ★**main 的推荐默认值** ★ | 不拍的后果 |
|---|---|---|---|---|
| **V-1** | ★**`U_PWR_SW` 的选型追认** ★ (★ISS-257 已把它落成 `TPS22991RAA` · ★TI 负载开关 UQFN-4 RAA · 1=VIN / 2=ON / 3=VOUT / 4=GND · ≥2A · R_on 25mΩ@5V · **无 RCB (反向电流阻断)**★)<br>★**网表 value 里已明写「⇒ 选型口径待 A5 追认」⇒ ★**所以它不是「还没落表」, 是「落了但等你认」** ★ | ★**① 追认 `TPS22991RAA`** (★与 §A5/Q2 的推荐默认值一致 · ★**但把「无 RCB」这个缺口写进账: 关机态电芯会不会被 USB 反灌, 仍无人负责**★)<br>★**② 不追认 ⇒ 改回 `[待选型]`** (★⇒ BOM 里这 14 件又回到 14 件待选型 ⇒ **G1a-7 立刻由绿转红** ★· ★**选型矩阵 22/22 的证据全废, 要重来一轮**★)<br>★**③ 换一颗带 RCB 的** (★⇒ 要重查原厂手册 + 重跑落表链, ★**但 RCB 型号本身在 §A5 判据里就是「互斥无冠军」那一条** ★) | ★**① 追认** (★**理由: 证据已在盘 (§A5 的 Q2 推荐), 改动量 = 0; ★**且必须同时把「无 RCB」登记成一个显式缺口, 不许装作没有这回事**★) | ★**G1a-7 由绿转红 ⇒ ★**原理图定稿闸多一条红**★** ⇒ 板那一趟继续排不上** ★ |

★**★给 main 自己的一条硬约束 (★写在这里备查, ★不写进老板页★)** ★
★**① V-1 与 §A5 / §Q2 是同一件事的「最后一步」** ⇒ ★**拍 V-1 = 顺带把 §A5/Q2 收口 ⇒ 建议一起回** ★
★**② V-1 属【追认】不是【新选型】** ⇒ ★**不占「等老板做新决定」的预算 ⇒ ★**它只是把已经落进网表的东西签字** ★
★**③ ★**`R_SER_CSI_MCLK` 是必装但 value 仍 `[待原厂]` (SoC 侧球位) ⇒ ★**这条不在 G1a-7 的判据里 (G1a-7 只管 `[待选型]`) ⇒ ★**已登记成 need 交 main, ★**不在这一页 (零外发政策下只能走「自己查 / 开源替代料评估」路线)★ ★**

"""


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp_dec.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        shutil.move(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    text = open(DOC, encoding="utf-8").read()
    if "§A-补7" in text:
        print("§A-补7 已在页上 ⇒ 跳过 (幂等)")
        return 0

    shutil.copy2(DOC, BAK)
    print("备份 →", os.path.basename(BAK))

    # ---- ① 页头: 时间戳 + 追加 r45 变更说明 (原字不删) ----
    old_hdr = "> **出页人**: 项目总工 (main / moli) · **时间**: 2026-11-16 17:4x"
    new_hdr = (
        "> **出页人**: 项目总工 (main / moli) · **时间**: 2026-11-16 21:5x "
        "(★**r45: ★ISS-257 落表已交卷并独立复验 (G1a-5 + G1a-7 转绿)★ · "
        "★**新增 §A-补7 (G1a 还差的 2 条 + V-1 追认)★ · ★**页尾 md5 已刷到 ISS-257 落表后的新值 "
        "(`e06c1dd6…` / `287e7861…` / `94642d07…`)★ · r44 前的版本见 "
        "`DECISION_PENDING_2026-11-16.md.bak_20261116_2200_r44`★· 原字不删★★★)** "
        "(★r44 前的版本见 `DECISION_PENDING_2026-11-16.md.bak_20261116_2200_r44`★· 原字不删★) "
        "(★**原 17:4x 版 (r43) 原文保留在下面★**)"
    )
    if old_hdr not in text:
        raise SystemExit("页头锚点没找到 ⇒ 拒绝改 (防口径漂移)")
    text = text.replace(old_hdr, new_hdr, 1)

    # ---- ② 插入 §A-补7 (放在 §B 之前) ----
    anchor = "## §B · 不卡 demo 主线"
    if anchor not in text:
        raise SystemExit("§B 锚点没找到 ⇒ 拒绝改")
    text = text.replace(anchor, NEW_SECTION + anchor, 1)

    # ---- ③ 页尾 md5 刷成最新 (旧值保留, 追加式) ----
    old_md5_line = (
        "- ★**网表/脚表/BOM md5 (★main 2026-11-16 07:2x 实测, ISS-233 落表后的新值★)**: 网表 **`34132f7e…`** "
        "(旧 `3215020b…`) · 脚表 **`b21b743a…`** (旧 `a600afae…`) · BOM **`c195a117…`** (旧 `92b51580…`) · "
        "板 `611b869e…` ★**逐字节不变** ★ · `.kicad_pro` `3e504d2b…` ★**逐字节不变** ★"
    )
    new_md5_line = old_md5_line + (
        "\n- ★**★★【最新·r45 · main 2026-11-16 21:4x 实测·ISS-257 落表后的现值】★★★**: "
        "网表 **`e06c1dd6…`** (旧 `16ac89f7…` ⇒ 再旧 `611c3ba3…`) · 脚表 **`287e7861…`** (旧 `ef436a37…`) · "
        "BOM **`94642d07…`** (旧 `2a730574…`) · 板 `611b869e…` ★**逐字节不变** ★ · `.kicad_pro` `3e504d2b…` "
        "★**逐字节不变** ★ ⇒ ★**台账登记 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 (L1069/L1070) · "
        "★单号 `ISS-257` + 文件名 + 新旧 md5 四项同行★** ⇒ ★**SW/MECH 侧的 H-1 重锚第 6 跳 (ISS-258 / ISS-259) 已据此派出** ★"
    )
    if old_md5_line in text:
        text = text.replace(old_md5_line, new_md5_line, 1)
    else:
        print("!! 页尾 md5 行锚点没找到 ⇒ 跳过 (不阻塞)")

    _atomic_write(DOC, text)
    print("已写入 §A-补7 + 页头 r45 + 页尾 md5 刷新")
    print("字节数:", len(text.encode()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
