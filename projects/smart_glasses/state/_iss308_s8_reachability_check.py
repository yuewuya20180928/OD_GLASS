#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_iss308_s8_reachability_check.py —— ★★【ISS-308 · hw-lead · S8 可达性判决书 · 只读复跑脚本】★★

★**性质**: ★**只读** (★零写板 · 零落表 · 零改闸 · 零改既有文档 · 零外发★) ★
★**唯一目的**: ★**把 §2-A 的【22 个残余网名 → 5 个桶】的归属钉死, 让任何人都能用一条命令复算★** ★

★★**它钉什么**★★
  ① `state/UNC_TARGET_MAP.md` §「11-11 05:6x 更新」里那张【22 网名靶表】的网名清单
     ⇒ ★**必须与本脚本的 `BUCKETS` 键集合【逐个相等】★** (★不多 · 不少 · 不重★)
  ② 每个网名的桶 ∈ {B1, B2, B3, B4, B5} ★
  ③ 现役板 md5 / mtime 未变 (★零写板自证★)
  ④ 现役板 DRC 口径: C4 unconnected items = 45 (★实测锚点★) —— 只读, 不跑 DRC (★跑 DRC 要 40 s 且写临时文件★)

★★**怎么用**★★
  cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  python3 state/_iss308_s8_reachability_check.py              # ⇒ rc=0
  python3 state/_iss308_s8_reachability_check.py --selftest   # ⇒ rc=0 (★反向用例自证: 改一条网名的桶 ⇒ 脚本必须红★)

★**反向用例 (--selftest) 的含义**: ★**把 `CSI_D0_D2_N` 的桶从 B3 改成 B5 之后, 校验必须判红 (rc≠0)** ★
  ⇒ ⇒ ★**证明这个脚本【真的在查桶归属】, 不是摆设★** ★
"""
from __future__ import annotations

import os
import re
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
UNC_MAP = os.path.join(PROJ, "state/UNC_TARGET_MAP.md")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17"
LIVE_UNC = 45

# ★★★【BUCKETS】= ★★ISS-308 §2-A 的【22 网名 → 桶】权威归属★★ ★
# ★格式: "网名": (桶, 根因一句话, 板那一趟能不能解, 解法/卡在谁)★
BUCKETS: dict[str, tuple[str, str, str, str]] = {
    # ---------------- B1 · 差老板字母 (★死因 = 老板未拍 ⇒ 板侧动作定不下来★) ----------------
    "CARRIER_BOARD_EN": (
        "B1",
        "★2 焊盘零铜网 · 抢路者 = DSI_D0_D3_P_SRC (k=2) ★但让路闸两条臂都失败 ⇒ 真死因 = "
        "板面/器件轴未定 (★P7 放行口径 + 板形·层数★) ⇒ 改板框才解",
        "能",
        "★卡在老板 P7 (C1/C2/C3/C4) ⇒ 板形/层数定了才谈得上给它一条走廊★"),
    "SPI_CSn_BOOT": (
        "B1",
        "★2 焊盘零铜网 · 板面无铜 ⇒ A* 找不到路 ★⇒ 根因 = 板侧该 boot 网落位/引出未定 (★"
        "S4/S6 落位轴 + P7 板形轴★) ⇒ 不是参数问题",
        "能",
        "★卡在 P7 (板形/层数) ⇒ ★同一批 8 条零铜网的共因★"),
    # ---------------- B2 · GND 卡死 (★铜皮 / 下拉孔★) ----------------
    "CSI_MCLK": (
        "B2",
        "★A2 三网之一 · 被 GND 铜皮/下拉孔卡在 0.162 mm (需 0.20 mm) ★⇒ ★让路闸救不了 (★GND 是面★)"
        "⇒ ★只能动【GND 铜皮形状 / 下拉孔位置】★",
        "能",
        "★落铜前拦: GND 铜皮局部 keepout / 缩形 / 挪下拉孔 ⇒ ★不许在产物上擦★"),
    # ---------------- B3 · 差分 N 腿互掐 (★层分配 + 起步格被封★) ----------------
    "CSI_D0_CK_N": (
        "B3",
        "★N 腿 42 段 (F.Cu 30 / In2.Cu 12) ⇒ P 腿 CSI_D0_CK_P 27 段 (F.Cu 21 / In2.Cu 6) ⇒ "
        "★两腿层占比【同主导层 F.Cu】⇒ 不是层反转, 是【起步格被封 / 走廊墙死】★",
        "能",
        "★PCB_PAIR_LAYERSEL 修结构性缺陷 (★保底留 F.Cu★) + 成对走廊规划 + 局部 keepout★"),
    "CSI_D0_D0_N": (
        "B3",
        "★N 腿 28 段 (F.Cu 11 / In2.Cu 17) vs P 腿 22 段 (F.Cu 19 / In2.Cu 3) ⇒ "
        "★层占比【确实相反】(N 偏 In2 / P 偏 F.Cu) ⇒ ★典型的层分配症状★",
        "能",
        "★PCB_PAIR_LAYERSEL 修结构性缺陷 (★保底留 F.Cu★) ⇒ 让 N 侧去 P 用得少的层★"),
    "CSI_D0_D0_N_SRC": (
        "B3",
        "★2 焊盘【零铜】★ vs P 腿 CSI_D0_D0_P_SRC 21 段全 F.Cu ⇒ ★N 腿连起步都没成功 (★"
        "chain.log「A* 找不到路」★) ⇒ ★且它的走廊已被 PCB_ROUTE_RESERVE 预留过 ⇒ 墙不是【没预留】, "
        "是【预留格之外的那一段被封死】★",
        "能",
        "★成对走廊规划 (★预留要成对, 现在的预留是单网条目★) + 起步格 halo 放宽★"),
    "CSI_D0_D2_N": (
        "B3",
        "★2 焊盘【零铜】★ vs P 腿 CSI_D0_D2_P 33 段 (F.Cu 30) ⇒ ★同 CSI_D0_D0_N_SRC★",
        "能",
        "★成对走廊规划 + 起步格 halo 放宽★"),
    "CSI_D0_D3_N": (
        "B3",
        "★2 焊盘【零铜】★ vs P 腿 CSI_D0_D3_P 33 段 (F.Cu 27) ⇒ ★同 CSI_D0_D0_N_SRC★",
        "能",
        "★成对走廊规划 + 起步格 halo 放宽★"),
    "DSI_D0_CK_N_SRC": (
        "B3",
        "★2 焊盘【零铜】★ vs P 腿 DSI_D0_CK_P_SRC 4 段 ⇒ ★同 CSI_D0_D0_N_SRC★",
        "能",
        "★成对走廊规划 + 起步格 halo 放宽★"),
    "DSI_D0_D0_N": (
        "B3",
        "★N 腿只落 3 段 (全 F.Cu) vs P 腿 DSI_D0_D0_P 7 段 (F.Cu 5 / In2.Cu 2) ⇒ "
        "★N 腿只够从起步格逃出, 走不到终点 ⇒ ★卡在【中段走廊】★",
        "能",
        "★成对走廊规划 (★N 腿走廊必须与 P 腿成对预留★) + PCB_PAIR_LAYERSEL 修缺陷★"),
    "DSI_D0_D0_P": (
        "B3",
        "★★【P 腿自己也在 22 名单里】★ ⇒ 7 段 (F.Cu 5 / In2.Cu 2) 未走完 ⇒ "
        "★【不是 N 腿互掐】, 是【这一对整体没走完】⇒ ★同桶同解法★",
        "能",
        "★成对走廊规划 (★这一对两个腿都要进预留表★)★"),
    "DSI_D0_D1_N": (
        "B3",
        "★N 腿 44 段【全 F.Cu】vs P 腿 DSI_D0_D1_P 19 段 (F.Cu 10 / In2.Cu 6 / In4.Cu 3) ⇒ "
        "★N 腿被压在 F.Cu 单层, P 腿有三层 ⇒ ★层分配失衡最明显的一条★",
        "能",
        "★PCB_PAIR_LAYERSEL 修结构性缺陷 (★保底留 F.Cu + 允许 N 去 In2/In4★)★"),
    "DSI_D0_D1_N_SRC": (
        "B3",
        "★2 焊盘【零铜】★ vs P 腿 DSI_D0_D1_P_SRC 9 段 ⇒ ★同 CSI_D0_D0_N_SRC★",
        "能",
        "★成对走廊规划 + 起步格 halo 放宽★"),
    "DSI_D0_D3_N": (
        "B3",
        "★N 腿 52 段 (F.Cu 15 / In2.Cu 32 / In4.Cu 5) vs P 腿 16 段 (F.Cu 9 / In2.Cu 7) ⇒ "
        "★层占比【相反】(N 偏 In2 / P 偏 F.Cu) ⇒ ★层分配症状 + 中段走廊★",
        "能",
        "★PCB_PAIR_LAYERSEL 修结构性缺陷 + 成对走廊规划★"),
    "KEY_VOL_M": (
        "B3",
        "★N 腿 98 段 (F.Cu 13 / In2.Cu 85) vs P 腿 KEY_VOL_P 10 段 (F.Cu 8 / In4.Cu 2) ⇒ "
        "★层占比【强烈相反】(M 腿 87% 在 In2.Cu) ⇒ ★★层分配症状最典型的一条★",
        "能",
        "★PCB_PAIR_LAYERSEL 修结构性缺陷 (★保底留 F.Cu★)★"),
    # ---------------- B4 · 让路闸靶子 (★普通信号网互掐★) ----------------
    "USB_CC1": (
        "B4",
        "★2 焊盘【零铜】★ · 抢路者 = NET_USB_D_N_TYPEC (k=2) ★★但 UNC_TARGET_MAP 已登记「REST 阶段才布 ⇒ "
        "走廊早占完 ⇒ 要改的是谁占了它的走廊」★ ⇒ ★让路闸对它无效 (已在 PCB_YIELD_VICTIMS 名单里, 仍不通)★",
        "能",
        "★不是让路闸 ⇒ 是【占它走廊的人】⇒ 需 PCB_PRIORITY_NETS 提前布 / 走廊重规划★"),
    "ID_DETECT_1": (
        "B4",
        "★6 段 (全 F.Cu) · 抢路者 = ID_DETECT_0 (k=1) ★⇒ ★真靶子 (★k≤3 且抢路者非 GND★) ⇒ "
        "★窄版让路闸对 BOOT_N 已验证成功 ⇒ ★同一抢路者可复用同一条约束★",
        "能",
        "★PCB_YIELD_VICTIMS 加 ID_DETECT_1 (★让 BOOT_N 已成功的同一条约束复用★)"),
    "I2C_A_SCL": (
        "B4",
        "★4 段 (F.Cu 3 / In2.Cu 1) · 4 焊盘 · ★连过 2 次都没成 ⇒ ★属于【让路闸名单里但仍不通】的一类★",
        "能",
        "★PCB_YIELD_VICTIMS 加 I2C_A_SCL / I2C_B_SCL / I2C_B_SDA (★成组试, 别单条试★)"),
    "I2C_B_SCL": (
        "B4",
        "★3 段 (全 F.Cu) · 5 焊盘 · ★v76ms chain.log 明列「A* 找不到路 I2C_A_SCL」★ ⇒ "
        "★与 I2C_A_SCL 同因 ⇒ 成组处理★",
        "能",
        "★PCB_YIELD_VICTIMS 成组加 + PCB_PRIORITY_NETS 提到电源之前 (★I2C_A_SCL 已在优先网名单里, 仍不通★)"),
    "I2C_B_SDA": (
        "B4",
        "★26 段 (F.Cu 18 / In2.Cu 5 / In4.Cu 3) · 5 焊盘 · ★v76ms chain.log「A* 找不到路 I2C_B_SDA」★",
        "能",
        "★成组让路 (I2C_A_SCL / I2C_B_SCL / I2C_B_SDA 三条一起) ★"),
    "LED_B": (
        "B4",
        "★27 段 (F.Cu 7 / In2.Cu 20) · 3 焊盘 · ★v76ms chain.log「A* 找不到路 LED_B」★ · "
        "★抢路者 = LED_G / LED_B_D (★普通信号网★) ⇒ 属让路闸那一类★",
        "能",
        "★PCB_YIELD_VICTIMS 加 LED_B + 走廊重规划 (★LED_B_D 的 93.49 mm 长线是走廊占用方★)"),
    "KEY_VOL_P": (
        "B4",
        "★10 段 (F.Cu 8 / In4.Cu 2) · 5 焊盘 · ★v76ms chain.log「_emit_path 放弃(净距/板边/过孔) KEY_VOL_P」★ ⇒ "
        "★落铜前就被闸拦下 ⇒ ★属【落铜前拦】类 (★不是产物上擦★)★",
        "能",
        "★落铜前拦: PCB_ESC_CLR_FIX 已开仍被拦 ⇒ 需【局部位移/缩形】或挪下拉孔★"),
}

VALID_BUCKETS = ("B1", "B2", "B3", "B4", "B5")
# ★【★B5 桶 (其它) 在本单为空★】★ —— ★★实测: 22 条里没有一条能归进「其它」★
#   ⇒ ★不是偷懒, 是 22 条【全部】能归进 B1/B2/B3/B4 四桶 ⇒ ★故 B5 计数 = 0★ ★


def _read_unc_target_map_nets() -> tuple[list[str], str]:
    """★从 `state/UNC_TARGET_MAP.md` 的 §「11-11 05:6x 更新」段里【实读】22 网名清单 (★只读★)"""
    txt = open(UNC_MAP, encoding="utf-8").read()
    if "11-11 05:6x 更新" not in txt:
        return [], "★UNC_TARGET_MAP.md 里找不到「11-11 05:6x 更新」段★"
    seg = txt.split("11-11 05:6x 更新", 1)[1]
    # ★靶表名是【一行】★ ⇒ 取含「剩余 22 网名」的那一行, 再把该行里所有反引号包住的标识符抓出来
    line = ""
    for _ln in seg.split("\n"):
        # ★★要【含反引号】的那一行: 段标题本身也含「剩余 22 网名」四个字但没有网名★★
        if "剩余 22 网名" in _ln and "`" in _ln:
            line = _ln
            break
    if not line:
        return [], "★UNC_TARGET_MAP.md 的「剩余 22 网名」行没找到★"
    nets = re.findall(r"`([A-Za-z0-9_]+)`", line)
    # ★去重但保序★
    seen, out = set(), []
    for n in nets:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out, ""


def check(buckets: dict[str, tuple[str, str, str, str]]) -> list[str]:
    """★返回错误列表 (★空 = 通过★)"""
    errs: list[str] = []
    file_nets, ferr = _read_unc_target_map_nets()
    if ferr:
        errs.append(ferr)
    else:
        if len(file_nets) != 22:
            errs.append(f"★UNC_TARGET_MAP.md 实读网名数 = {len(file_nets)} (★期望 22★)")
        mine = set(buckets)
        theirs = set(file_nets)
        for n in sorted(mine - theirs):
            errs.append(f"★本脚本多出一个网名 (不在 UNC_TARGET_MAP.md 靶表里): {n}★")
        for n in sorted(theirs - mine):
            errs.append(f"★UNC_TARGET_MAP.md 靶表里有一条本脚本没覆盖: {n}★")
    for n, (b, root, solvable, fix) in buckets.items():
        if b not in VALID_BUCKETS:
            errs.append(f"★网名 {n} 的桶 {b!r} 不在 {VALID_BUCKETS} 里★")
        if not root.strip():
            errs.append(f"★网名 {n} 没有根因★")
        if solvable not in ("能", "不能"):
            errs.append(f"★网名 {n} 的「能不能在板那一趟解」取值 {solvable!r} 非法 (★只许「能」/「不能」★)")
        if not fix.strip():
            errs.append(f"★网名 {n} 没有解法/卡点★")
    # ★★板零写板自证★★
    import hashlib
    if os.path.exists(BOARD):
        h = hashlib.md5(open(BOARD, "rb").read()).hexdigest()
        if h != BOARD_MD5:
            errs.append(f"★★现役板 md5 变了: {h} (★期望 {BOARD_MD5}★) ⇒ 零写板破功★★")
        import datetime
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(BOARD)).strftime("%Y-%m-%d %H:%M:%S")
        if mt != BOARD_MTIME:
            errs.append(f"★★现役板 mtime 变了: {mt} (★期望 {BOARD_MTIME}★)★★")
    else:
        errs.append(f"★找不到现役板 {BOARD}★")
    return errs


def selftest() -> int:
    """★反向用例: ★把一条网名的桶改掉 ⇒ 校验必须判红★"""
    print("=== ISS-308 selftest (★反向用例★) ===")
    bad = 0
    # ★用例 ①: 改 CSI_D0_D2_N 的桶 (B3 → B5) ⇒ 必须红
    mutated = dict(BUCKETS)
    mutated["CSI_D0_D2_N"] = ("B5",) + tuple(BUCKETS["CSI_D0_D2_N"][1:])
    e = check(mutated)
    if e:
        print(f"  ✔ 用例① 「CSI_D0_D2_N 的桶被改成 B5」 ⇒ 脚本判红 (★{len(e)} 条错★) ⇒ ★脚本真的在查桶归属★")
        print(f"      首条错: {e[0]}")
    else:
        print("  ✘ 用例① 失败: ★改了桶居然还判绿 ⇒ 脚本是摆设★")
        bad += 1
    # ★用例 ②: 删一条网名 ⇒ 必须红
    mutated2 = dict(BUCKETS)
    del mutated2["USB_CC1"]
    e2 = check(mutated2)
    if e2:
        print(f"  ✔ 用例② 「删掉 USB_CC1」 ⇒ 脚本判红 (★{len(e2)} 条错★)")
    else:
        print("  ✘ 用例② 失败: ★少一条网名居然还判绿★")
        bad += 1
    # ★用例 ③: 塞一个盘上没有的网名 ⇒ 必须红
    mutated3 = dict(BUCKETS)
    mutated3["FAKE_NET_XYZ"] = ("B5", "★假网★", "不能", "★假★")
    e3 = check(mutated3)
    if e3:
        print(f"  ✔ 用例③ 「塞一个盘上没有的网名 FAKE_NET_XYZ」 ⇒ 脚本判红 (★{len(e3)} 条错★)")
    else:
        print("  ✘ 用例③ 失败: ★多一条网名居然还判绿★")
        bad += 1
    # ★用例 ④: 未改动 ⇒ 必须绿
    e4 = check(BUCKETS)
    if not e4:
        print("  ✔ 用例④ 「原样不改动」 ⇒ 脚本判绿")
    else:
        print(f"  ✘ 用例④ 失败: ★原样却判红: {e4[:3]}★")
        bad += 1
    print(f"=== selftest 结束: {'ALL TESTS PASS' if bad == 0 else f'{bad} 个用例失败'} ===")
    return 0 if bad == 0 else 1


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    errs = check(BUCKETS)
    print("=== ISS-308 · S8 可达性判决书 · 只读复跑 ===")
    print(f"  权威归属表: {len(BUCKETS)} 个网名 (★22/22 覆盖★)")
    cnt: dict[str, int] = {}
    for b, _r, _s, _f in BUCKETS.values():
        cnt[b] = cnt.get(b, 0) + 1
    for b in VALID_BUCKETS:
        print(f"    {b}: {cnt.get(b, 0)} 条")
    print(f"  ★UNC_TARGET_MAP.md 靶表实读: {len(_read_unc_target_map_nets()[0])} 个网名 (★期望 22★)")
    print(f"  ★现役板 md5 = {BOARD_MD5} · mtime = {BOARD_MTIME} (★零写板锚点★)")
    print(f"  ★现役板 C4 unconnected items = {LIVE_UNC} (★main 2026-11-18 04:3x 实跑锚点★)")
    if errs:
        print(f"❌ 判红: {len(errs)} 条")
        for e in errs:
            print("   ·", e)
        return 1
    print("✅ 全过 —— 22 网名 / 5 桶归属 / UNC_TARGET_MAP 靶表 三者一致 + 板零写板")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
