#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_0600_main_sign_iss379.py
==========================================
main (项目总工) · 2026-11-24 06:0x
★独立签收 ISS-379 cont1 (hw-lead · J_UART 换官方 P1.27 THT land 落位可行性) + 裁交回的 9 条★

★纪律 (★本脚本自己守★):
  ① 零写板 (板 md5/mtime/size 三项开工前后各打一次, 纳秒级比)
  ② 零落表 (网表/脚表/BOM/落表台账 一字不改)
  ③ 零改既有闸 / 零改既有页面正文
  ④ 分片只走 state/frag_write.py (原子写)
  ⑤ issue_log.yaml / 一页 / LESSONS.md 一律【追加式】(★老字一字未删·★零 churn★)
  ⑥ 不代老板拍板 (★老板侧的板框第一问仍未答⇒ 落点坐标的一切前提都挂在它身上★)
  ⑦ 零外发
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import frag_write  # ★只用它的原子写 ★
import yaml

STAMP = time.strftime("%Y%m%d_%H%M")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
LOG = os.path.join(PROJ, "state/issue_log.yaml")
ONEPAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
LESSONS = os.path.join(PROJ, "state/LESSONS.md")
PM = os.path.join(PROJ, "state/fragments/pm.yaml")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

GATE = "HW/check_juart_land_fit.py"
PAGE = "HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md"
HANDOFF = "HANDOFF/2026-11-24_hw-lead_ISS379_JUART排针换land落位可行性.md"
THIRD = "tmp/iss379/tools/third_path_recheck.py"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def ns_of(s):
    import datetime
    base, _, frac = s.partition(".")
    frac = (frac + "000000000")[:9]
    tz8 = datetime.timezone(datetime.timedelta(hours=8))
    dt = datetime.datetime.strptime(base, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz8)
    return int(dt.timestamp()) * 10 ** 9 + int(frac)


def board_fp():
    st = os.stat(BOARD)
    return md5(BOARD), st.st_mtime_ns, st.st_size


def sh(cmd):
    import subprocess
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def read_lines(path):
    return open(path, encoding="utf-8").read()


# ===================================================================== 阶段 1 · 独立复核
def verify():
    print("=" * 92)
    print("★阶段 1 · main 本机独立复核 (★不抄 agent 报告★)")
    print("=" * 92)
    ok = True
    lines = []

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        lines.append((name, bool(good), detail))
        print("  %s %-44s %s" % ("✅" if good else "❌", name, detail))

    m, ns, sz = board_fp()
    chk("板 md5/mtime/size 三项", m == BOARD_MD5 and ns == ns_of(BOARD_MTIME) and sz == BOARD_SIZE,
        "%s / %s / %d" % (m[:8], BOARD_MTIME, sz))

    # 交付物三件在盘
    for rel in (GATE, PAGE, HANDOFF):
        p = os.path.join(PROJ, rel)
        e = os.path.isfile(p) and os.path.getsize(p) >= 4000
        chk("交付物在盘 (≥4000 B) %s" % rel.split("/")[-1], e,
            "%d B" % (os.path.getsize(p) if os.path.isfile(p) else 0))

    # 交卷页 B1~B6 块标题
    ht = read_lines(os.path.join(PROJ, HANDOFF))
    blocks = [b for b in ("## B1", "## B2", "## B3", "## B4", "## B5", "## B6") if b in ht]
    chk("交卷页 B1~B6 块标题齐全", len(blocks) == 6, "%d/6" % len(blocks))

    # 占位符 = 0 (语境窗口)
    ph = sum(ht.count(w) for w in ("TODO", "TBD", "XXX", "待补", "占位"))
    chk("交卷页占位符 = 0", ph == 0, "命中 %d" % ph)

    # 自带闸裸跑 + selftest
    rc, o = sh("python3 %s" % GATE)
    chk("★自带闸裸跑 rc=0 (K0~K8 全绿)", rc == 0 and "GATE GREEN" in o, "rc=%d" % rc)
    rc2, o2 = sh("python3 %s --selftest" % GATE)
    last = o2.strip().splitlines()[-1] if o2.strip() else ""
    n_case = 0
    for ln in o2.splitlines():
        if "反向用例通过" in ln:
            try:
                n_case = int(ln.split("/")[0].strip())
            except Exception:
                pass
    chk("★自带闸 --selftest 末行 ALL TESTS PASS", rc2 == 0 and "ALL TESTS PASS" in last,
        "rc=%d 末行=%r" % (rc2, last[:46]))

    # ★确定性: 连跑 3 次 K2 读数必须逐字相同 (★防「读数会漂」的闸★)
    reads = []
    for _ in range(3):
        _, oo = sh("python3 %s" % GATE)
        for ln in oo.splitlines():
            if ln.strip().startswith("K2"):
                reads.append(ln.strip())
    chk("★闸读数确定性 (连跑 3 次 K2 逐字相同)", len(set(reads)) == 1,
        "distinct=%d %s" % (len(set(reads)), reads[0][-34:] if reads else ""))

    # ★第三路独立复算 (自写解析 + 自写几何, 不 import 闸) ⇒ 判「证据侧对 · 闸侧错」
    if os.path.isfile(os.path.join(PROJ, THIRD)):
        rc3, o3 = sh("python3 %s" % THIRD)
        ok3 = (rc3 == 0 and "3.1266" in o3 and "3.1267" in o3 and "有损角" in o3)
        chk("★第三路独立复算 (证据对/闸错 双向可复现)", ok3, "rc=%d" % rc3)
    else:
        chk("★第三路独立复算脚本在盘", False, THIRD)

    # 容差不许放宽 (★擦症状≠修根因★) ⇒ 判据里必须还是 1e-6, 且不许出现 1e-4/1e-3 当余量容差
    gt = read_lines(os.path.join(PROJ, GATE))
    chk("★余量容差仍 = 1e-6 (★未放宽★)", 'margin"] - float(c[2])) > 1e-6' in gt, "1e-6 在位")
    chk("★根因修在产生点 (删角度取整 round(…,6))",
        "round(math.radians" not in gt and "math.radians(float(pad.GetOrientation().AsDegrees()))" in gt,
        "角度取整已删")

    # 零落表 + 受保护件
    prot = {
        "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
        "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
        "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
        "state/gate_check.py": "5f370bb8cf828473e70ccc5d6412da98",
        "state/merge.py": "c9191025020fefd9b475e2573a335815",
        "state/frag_write.py": "3b383a52b4fa540f1d16a2c6f3811de8",
    }
    bad = []
    for rel, want in prot.items():
        p = os.path.join(PROJ, rel)
        got = md5(p) if os.path.isfile(p) else "MISSING"
        if got != want:
            bad.append("%s(%s≠%s)" % (rel, got[:8], want[:8]))
    chk("★零落表 + 既有闸/分片工具 未动 (%d 件)" % len(prot), not bad, "动 %d %s" % (len(bad), bad[:3]))

    # 零挂链
    rc4, o4 = sh("grep -c check_juart_land_fit state/gate_check.py")
    zero = o4.strip().splitlines()[0].strip() == "0" if o4.strip() else False
    chk("零挂链 (gate_check.py 命中 0)", zero, o4.strip().splitlines()[0] if o4.strip() else "?")

    # 别人的分片零本单登记 / 自己的分片有登记
    x_bad = []
    for f in ("pm", "sw", "mech"):
        try:
            d = yaml.safe_load(open(os.path.join(PROJ, "state/fragments/%s.yaml" % f), encoding="utf-8")) or {}
        except Exception:
            continue
        for sect in ("answers", "needs_from", "interface_claims", "artifacts", "risks", "blockers"):
            for e in (d.get(sect) or []):
                if isinstance(e, dict):
                    k = str(e.get("key") or e.get("id") or e.get("path") or "")
                    if "iss379" in k.lower() or "juart_land_fit" in k.lower():
                        x_bad.append("%s.yaml[%s] %s" % (f, sect, k))
    chk("别人的分片 (pm/sw/mech) 零本单登记", not x_bad, "越界 %d %s" % (len(x_bad), x_bad[:3]))

    hw = read_lines(os.path.join(PROJ, "state/fragments/hw.yaml"))
    chk("自己的分片 (hw.yaml) 有本单登记", "iss379" in hw or "juart_land_fit" in hw, "命中在位")

    # 证据留证
    lg = os.path.join(PROJ, "logs/iss379")
    n_lg = len(os.listdir(lg)) if os.path.isdir(lg) else 0
    chk("logs/iss379/ 证据在盘 (≥10 件)", n_lg >= 10, "%d 件" % n_lg)

    # 证据 JSON 唯一权威份
    jm = md5(os.path.join(lg, "scan_land_fit.json"))
    others = []
    for root, _, fns in os.walk(lg):
        for fn in fns:
            if fn.endswith(".json") and "scan_land_fit" in fn:
                p = os.path.join(root, fn)
                if os.path.abspath(p) != os.path.abspath(os.path.join(lg, "scan_land_fit.json")):
                    others.append((fn, md5(p)))
    chk("★证据 JSON 唯一权威份 (其余改名归档 _nonauth)",
        all("nonauth" in n for n, _ in others), "权威 %s · 归档 %d" % (jm[:8], len(others)))

    # merge / gate_check
    rc5, _ = sh("python3 state/merge.py")
    chk("merge.py rc=0", rc5 == 0, "rc=%d" % rc5)
    rc6, o6 = sh("python3 state/gate_check.py")
    chk("gate_check.py rc=0 (Q1 18/18)", rc6 == 0 and "18/18" in o6, "rc=%d" % rc6)

    print("  ★阶段 1 结论: %s" % ("★全绿★" if ok else "★★有红项★★"))
    return ok, lines


# ===================================================================== 阶段 2 · main 的裁决
ANS_1 = (
    "★**main 裁决 (★2026-11-24 06:0x·★main 地界·★不代老板拍板★)★: ★**换·★这一问不用再问·★已有既定裁决★** ⇒ "
    "★**`B33_PIN_LAND_1P27` (★11-17 已拍·★那一页 §D3 逐字写着「板侧项已在 ISS-343 B33_PIN_LAND_1P27 (★11-17 已拍改 land 到 1.27★) "
    "⇒ 那一趟带上」★) ⇒ ★**换 land 这件事本身是【已决】的, 本单不需要重新拍★** ⇒ "
    "★**★但 main 要给一句【本单真正新增的东西】(★即「代价与结构红灯』这层★)★**: 本单挖出来的是「换了之后要挪多少、挪完还剩什么」⇒ "
    "★**① `J_UART` 的 1×2 铜箔包络 X 宽 `2.2700` vs 座体必须清空区宽 `2.5400` ⇒ 每边余量 `0.1350` < `CRIT` `0.60` ⇒ 结构红灯 (★与 J_DEBUG 侧同款★)** ⇒ "
    "★**② 现位 `UART_TX` 那串 `In2.Cu` 在 rot 90 落点处与新 pad2 【恰好压线 `0.0000`】⇒ 必须改道** ⇒ "
    "★**⇒ 这两条是「换了 land 之后要付的代价」, 属于【那一趟必须一起算进去的账】, 不是「要不要换」的依据★ ⇒ ★**main 把这两条并进「板那一趟」的同一批★** ★"
)

ANS_2 = (
    "★**main 裁决 (★2026-11-24 06:0x·★main 地界★)★: ★**落点本单不定 (★因为前提没落·★不是不裁·★是不能裁★)★** ⇒ "
    "★**★三条候选 (rot 270 `(18.6000,68.6000)` 余量 `0.2750` / rot 90 `(18.4000,68.4000)` 余量 `0.1155` / rot 90 `(18.3000,68.6000)` 余量 `0.0447`) "
    "★全部标 [实测]·★逐条数都在真相页 §2.3·★main 已实读核过·★不是抄★★ ⇒ ★**它们【互斥】且【各自带代价】⇒ ★**main 不在这里挑一个**★ ⇒ "
    "★**★为什么现在不能挑 (★硬前提·★main 地界也越不过★)★**: 这三个坐标全部挂在【现役板 160×100 的框】上 (★main 本机实读 Edge.Cuts: X 跨度 `160.0000` · Y 跨度 `100.0000` mm★) "
    "⇒ ★**而「板只改一次」那一趟画的是【甲 = 台架板 160×100】还是【乙 = 产品内板 60×30 / 60×15】那个【上位问题】还没答 (★need key `boss_u1_upper_axis_board_trip_physical_product`·★仍 open★)★ "
    "⇒ ★**⇒ 若甲 ⇒ 这三个坐标全部有效; 若乙 ⇒ 板框全变 (60×30 或 60×15) ⇒ 三个坐标【全部作废】⇒ ★**⇒ 在上位问题落地前挑落点 = 挑一个可能立刻作废的数** ⇒ "
    "★**⇒ main 的处置 = 【三个候选全部【实测】在案·★谁都可以直接用·★但 main 不在上位问题落地前签任一个】⇒ ★**上位问题一答 (★甲 or 乙★) ⇒ "
    "★**① 若甲 ⇒ main 立刻在【这三个已实测候选】里挑一个 (★裁决口径已经写好: 【pin 顺序不变】优先于【落位代价最小】·★理由 = ① pin 顺序变了 ⇒ 固件侧 5 处机器件读数要改 "
    "(★`SW/tools/check_debug_pin_order_contract.py` L231/L287/L312/L466/L552★) + 工装线序说明要改 ⇒ 改的东西越多那一趟越容易二次动板; "
    "② 而【代价】这一侧 rot 90 余量 `0.1155` > 0 ⇒ 【结构上并不比 rot 270 差到不能落】·★⇒ ⇒ ★**在【pin 顺序不变】这个口径下, rot 90 的落点是 (18.4000,68.4000) 余量 `0.1155`·★"
    "比第三个候选 (18.3000,68.6000) 余量 `0.0447` 大 ⇒ ★**main 倾向 = rot 90 + (18.4000,68.4000)·★但【这是倾向·★不是拍板·★要等上位问题落甲才生效★】★) ★ "
    "★**⇒ ★★本条 need 就此【挂起·不是关闭】★★ ⇒ ★**上位问题落甲的那一趟, main 必须回来把这条签掉 (★挂起原因已写明·★不是忘了★)** ★"
)

ANS_3 = (
    "★**main 裁决 (★2026-11-24 06:0x·★main 地界★)★: ★**口径 = 【沿用新 land 的 pin1】·★不用现位从左到右★** ⇒ "
    "★**★为什么 (★main 地界·★这条与落点无关·★所以现在就能定★)★**: 换 land 之后, 「从左到右」这件事在 rot 270 下【物理上不再成立】(★pad1 跑到 X_MAX·★左右顺序整体反过来★) ⇒ "
    "★**⇒ 「沿用现位从左到右」这个口径在新 land 上是【没有定义的】·★不是两条口径都能用·★而是其中一条已经不成立★ ⇒ ⇒ ★**唯一能用的口径 = 沿用新 land 的 pin1** ⇒ "
    "★**⇒ 而 pin1 位置的【物理朝向】由 rot 决定 (★rot 90 ⇒ pad1@X_MIN; ★rot 270 ⇒ pad1@X_MAX★) ⇒ ★**⇒ 落位那一问一旦定了 (rot 90 or rot 270), 本条口径【自动随之确定】·★"
    "★本条【不构成独立的一问】·★它就是落点那问的【下半场】★** ⇒ ★**⇒ main 在这一条上不再单挑: ★**随落点一起落 (★免得两条各自拍、拍出自相矛盾的口径★)** ★ "
    "★**★并且【落点选 rot 90】这件事本身对固件侧有额外好处 (★main 独立复核 ISS-378 结论时看到的·★一并记在这里★)★**: ISS-378 实读结论 = "
    "★**「A 层 网名→pad 映射逐字不变 ⇒ 固件本体 0 行要改; 要改的只有 B 层物理针序 (SW 侧 5 处机器件读数 + 工装线序说明)」** ⇒ "
    "★**⇒ rot 90 (pad 顺序不变) ⇒ 救砖线序/工装线序契约不变 ⇒ 要改的机器件从 5 处降到 0 处 ⇒ ★**这一条正是 ANS_2 里「pin 顺序优先」口径的量化依据★** ★"
)

ANS_7 = (
    "★**main 裁决 (★2026-11-24 06:0x·★main 地界★)★: ★**清·★但【不是这一趟单独做·★是那一趟的布线工序顺手清★】** ⇒ "
    "★**★为什么 (★main 实读确认★)★**: `UART_TX` 的 `F.Cu` 段 `(18.6400,67.4000)→(18.6400,68.6000)` 在板上【重复了 2 次·★几何完全相同·★不是两条不同的线】** ⇒ "
    "★**⇒ 重复段 = 落板时的冗余/手滑 (★同一条同一点到点·★不留价值★)⇒ 换 land 重接时那串 `UART_TX` 本来就要改道 (★本单 §3.2 第 4 条已算出来·★它在 rot 90 落点处与新 pad2 恰好压线 `0.0000`★) ⇒ "
    "★**⇒ 改道的那一道工序里顺手把那 2 段重复的去掉·★【零额外代价】★ ⇒ ⇒ ★**处置 = 并进「板那一趟」布线 45→0 的同一次改道里做·★不单开一条工序 (★单开 = 多动一次板 = 违「板只改一次」★)★** ★ "
    "★**⇒ ★★main 把它登记成【板那一趟的一个必做子项】(★不是可选项★)★★ ⇒ ★**记在 pm.yaml 的 `answers` 里·★并要求那一趟的布线工序自查「每条网有没有重复段」·★"
    "★**【零重复段】应当成为那一趟的验收线之一 (★与 unc 45→0 同级·★不是加分项★)** ★"
)

ANS_8 = (
    "★**main 裁决 (★2026-11-24 06:0x·★main 地界·★先例同款·★照 ISS-372 U7 的口径答★)★: ★**挂·★但与「板那一趟」同批挂** ⇒ "
    "★**★理由 (★照搬 ISS-372 的先例·★四处同款先例: ISS-300 / ISS-309 / ISS-312 / ISS-315 四轮都只交写法没人挂★)★**: "
    "★**① 挂链是 main 的机制地界 (★agent 交脚本 + 路径 + 建议, main 挂★) ★ ② ★**但提前单独挂 ⇒ 闸链在【中间态】会红 (★这闸 K2/K5 读的是那一页的机器块; "
    "★那一页在落点/口径定了之前会被改 ⇒ 机器块与实算会短暂不一致⇒ 闸红·★而现场极可能误读成「板坏了」⇒ ★**这就是「板只改一次」那条铁律最怕的窗口**★)★ "
    "★⇒ ★**③ ⇒ 所以: 挂的动作随那一趟走·★但【挂链这件事本身已经定了·★不是「要不要挂」的悬案★】★ ⇒ ★**④ 本轮零动 `state/gate_check.py` (★md5 前后同值★)★** ★"
)

ANS_9 = (
    "★**main 裁决 (★2026-11-24 06:0x·★main 地界★)★: ★**两条都落·★但【追加式】落·★不改正文·★且与「板那一趟」同批落** ⇒ "
    "★**★为什么 (★main 地界★)★**: 两条追加式订正块的内容 = ① MECH 侧那条 `0.1350`/边余量/结构红灯口径 ② PREFLIGHT 侧那条 ⇒ "
    "★**⇒ 它们改的是【既有页面的现行读数口径】·★而那些页面在这一趟本来就要动 (★落点/朝向一改 ⇒ 相关读数全部变★) ⇒ ⇒ ★**单独现在落 = 落一个【马上就要被改掉的数】·★"
    "★【等于制造一次 churn】⇒ ★**正确处置 = 与那一趟同批落 (★落完板、算完新读数, 一次性把订正块落到位★)★** ⇒ ⇒ ★**main 现在做的是: 把「要落什么」记下来 (★本条 need + 交卷页 §6.1 的两个候选块★), "
    "★不现在动既有页面正文 (★那两页本单一个字都没碰·★零改既有页面正文★)★** ★"
)

ANS_MECH = (
    "★**main 转给 mech-lead (★2026-11-24 06:0x·★main 不代裁 3D 装配·★本条只给板侧坐标★)★: ★**两问都要 mech-lead 答, 且【必须在「板那一趟」开工前答完】★★ "
    "★**① `J_UART` 落点横移会不会挤掉 UART 罩开口 (X `13.790..23.990` / Y `66.300..70.900`) 或座体必须清空区 (X `17.620..20.160`)?** "
    "★**板侧本单已给三个候选的 copper bbox (★rot 270 方案 copper X `16.8700..19.1400` · rot 90 方案 copper X `18.1400..20.4100`·★[实测]★) "
    "★⇒ mech-lead 只需判【这三个 bbox 对 3D 座体/开口是否放得下】·★不用重算板侧铜** ⇒ ★**⇒ 板侧这半已交付·★3D 那半是 mech-lead 的域** ★ "
    "★**② 官方 THT land 铜箔 X 宽 `2.2700` vs 座体必须清空区宽 `2.5400` ⇒ 每边余量 `0.1350` < `CRIT` `0.60` ⇒ 结构红灯** "
    "★**⇒ ISS-374 已算出这条·★本单【独立确认板侧数一致】(★[实测]·★不是抄★)⇒ ★**要 mech-lead 确认「那一趟」的结构件怎么办 (★换更宽的座体? ★换铜箔? ★还是接受这盏结构红灯? ★)★ "
    "★**⇒ ★★main 提示: 这一条与 J_DEBUG 侧 (★ISS-377 算出铜箔每边超清空区 `1.5175`★) 是【同源问题】⇒ ★**建议 mech-lead 把两条【合到一件】答 (★一次给座体/开口/清空区的整体结论·★"
    "★而不是分别给两个落点的结论·★否则两个连接器的答案可能互相矛盾·★而两个连接器在【同一趟】里改·★矛盾就得改第二次·★违「板只改一次」★)★** ★ "
    "★**⇒ ★★时限 (★main 硬要求★): 「板那一趟」开工前必须答完·★因为结构件一旦开模/下单就没法回头 ⇒ ★**⇒ 这两条的答复窗口 = 与板框上位问题 (`boss_u1_upper_axis_board_trip_physical_product`) 的答复窗口【同一个】★★ "
    "★**⇒ ★★main 倾向 (★仅供参考·★不是拍板★)★**: ① 座体/开口按【两个连接器一起】解 (★J_DEBUG + J_UART 同批算·★别分两票★) ② 铜箔 X 宽与座体清空区的 `0.1350` 余量差距 "
    "★**优先从【座体选型/开口尺寸】上找解·★而不是从【板侧铜箔形状】上削 (★削铜箔会踩 DRC/信号完整性·★且落点坐标会跟着变·★变一次就是改板第二次★)★** ★"
)

ANS_SW = (
    "★**main 转给 sw-lead (★2026-11-24 06:0x·★main 不代裁固件拓扑·★本条只给板面事实★)★: ★**要 sw-lead 确认 `UART_RX` 这条网的预期拓扑** ⇒ "
    "★**★板面事实 (★[实测]·★main 本机独立复核过 (★板面读数: `UART_RX` 全网铜箔清单 = 0 段走线 0 过孔·★只有 `J_UART.2` + `J_SOM_P2.9` 两个 pad★)★**: "
    "★**⇒ 这条网在板上【一寸铜都没有】⇒ 【现在就没接】⇒ 这是【独立于 land 换装的缺口】(★不是换 land 换出来的·★是本来就有的★)★ ⇒ "
    "★**⇒ ★★要 sw-lead 答: 这条网【本来】就该由板侧接吗? 若「该板侧接」⇒ 【现在就没接】是一个【板级缺口】⇒ ★**它必须并进「板那一趟」·★否则那一趟做完它还是断的·★"
    "★而布线 45→0 的验收线【不会自己发现它】★ (★它现在是 0 段铜·★「0→0」不违反 unc 判据·★⇒ ★**unc 45→0 全绿【不代表】这条网通了★)★★ ⇒ "
    "★**⇒ ★★main 的处置: 这条登记成【板那一趟的额外必做子项】(★与 unc 45→0 同级·★不是可选项★)·★并要求布线工序自查【每条该接的网是否真有铜】·★"
    "★**【零「假连通」】应当成为那一趟的验收线之一★★** ★ "
    "★**⇒ ★★main 提示: 「0 段铜」这类缺口【不会】被 unc 45→0 抓到 (★unc 判据只看「该连的没连」·★看不见「本就不该连却也没连」★) ⇒ "
    "★**⇒ 那一趟的布线验收线要加一条【每条网按预期拓扑逐条列铜】·★不然「45→0」会给人一个「全接上了」的错觉★★** ★"
)


def apply_pm():
    print("\n" + "=" * 92)
    print("★阶段 2 · pm.yaml (main 自己的分片·★只走 frag_write 原子写★)")
    print("=" * 92)
    before = md5(PM)
    d0 = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    snap = {}
    for sect in ("answers", "needs_from"):
        for e in (d0.get(sect) or []):
            if isinstance(e, dict) and e.get("key"):
                snap[(sect, e["key"])] = dict(e)

    def mutate(d):
        ans = d.setdefault("answers", [])

        def upsert(key, value, ref, to="sw-lead"):
            for e in ans:
                if isinstance(e, dict) and e.get("key") == key:
                    old = str(e.get("value") or "")
                    if "【main 追加式订正 2026-11-24 06:0x" not in old:
                        e["value"] = old + value
                        print("  ✅ 就地扩写 answer: %s" % key)
                    else:
                        print("  ★已有本次扩写, 跳过: %s" % key)
                    return
            ans.append({"key": key, "to": to, "value": value, "ref": ref})
            print("  ✅ 新增 answer: %s" % key)

        upsert("iss379_q1_swap_or_not", ANS_1,
               "ISS-379 交卷页 B5-① · HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §1.2 · "
               "DECISION_ONE_PAGER_2026-11-22.md §D3 (★`B33_PIN_LAND_1P27` 11-17 已拍★)")
        upsert("iss379_q2_landing_point", ANS_2,
               "ISS-379 交卷页 B5-② · HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §2.3 · "
               "★★挂起原因: 上位问题 `boss_u1_upper_axis_board_trip_physical_product` 未答★")
        upsert("iss379_q3_net_mapping", ANS_3,
               "ISS-379 交卷页 B5-③ · HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §3.3 · "
               "ISS-378 固件影响面结论 (★A 层映射不变·★固件本体 0 行要改★)")
        upsert("iss379_q7_dup_segment", ANS_7,
               "ISS-379 交卷页 B5-⑦ · HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §3.2 第 5 条")
        upsert("iss379_q8_hook_gate", ANS_8,
               "ISS-379 交卷页 B5-⑧ · ★先例同款: ISS-300/309/312/315 + ISS-372 U7★")
        upsert("iss379_q9_correction_blocks", ANS_9,
               "ISS-379 交卷页 B5-⑨ · HW/PCB/BOARD_ONEPASS_JUART_LAND_FIT.md §6.1")

        nf = d.setdefault("needs_from", [])

        def upsert_need(key, item, to, since="2026-11-24"):
            for n in nf:
                if isinstance(n, dict) and n.get("key") == key:
                    old = str(n.get("item") or "")
                    if "【main 追加式订正 2026-11-24 06:0x" not in old:
                        n["item"] = old + item
                        print("  ✅ 就地扩写 need: %s" % key)
                    else:
                        print("  ★need 已有本次扩写, 跳过: %s" % key)
                    return
            nf.append({"key": key, "to": to, "item": item, "since": since})
            print("  ✅ 新增 need: %s (to=%s)" % (key, to))

        upsert_need("iss379_q4_mech_opening_and_clearance", ANS_MECH, "mech-lead")
        upsert_need("iss379_q6_uart_rx_zero_copper", ANS_SW, "sw-lead")

    frag_write.update_fragment("main", mutate)
    print("  ★pm.yaml 写前 md5 = %s" % before)
    print("  ★pm.yaml 写后 md5 = %s" % md5(PM))

    d1 = yaml.safe_load(open(PM, encoding="utf-8")) or {}
    touched = {"iss379_q1_swap_or_not", "iss379_q2_landing_point", "iss379_q3_net_mapping",
               "iss379_q7_dup_segment", "iss379_q8_hook_gate", "iss379_q9_correction_blocks",
               "iss379_q4_mech_opening_and_clearance", "iss379_q6_uart_rx_zero_copper"}
    lost = 0
    for (sect, key), old in snap.items():
        new = None
        for e in (d1.get(sect) or []):
            if isinstance(e, dict) and e.get("key") == key:
                new = dict(e)
                break
        if new is None:
            print("  ❌ 条目丢了: %s[%s]" % (sect, key))
            lost += 1
            continue
        if key in touched:
            continue
        if {k: v for k, v in old.items() if k != "value"} != {k: v for k, v in new.items() if k != "value"}:
            print("  ❌ 非目标条目被改: %s[%s]" % (sect, key))
            lost += 1
    print("  ★旧条目丢失/被改 = %d ⇒ %s" % (lost, "✅ 零内容丢失" if lost == 0 else "❌"))
    return lost == 0


# ===================================================================== 阶段 3 · issue_log 签收
def sign_issue_log(lines):
    print("\n" + "=" * 92)
    print("★阶段 3 · issue_log.yaml · ISS-379 签收 (★fixing → verified·★fail-closed★)")
    print("=" * 92)
    src = read_lines(LOG)
    before = md5(LOG)
    i = src.find("\n- id: ISS-379")
    if i < 0:
        raise SystemExit("★ISS-379 段没定位到 ⇒ 中止★")
    j = src.find("\n- id: ", i + 10)
    if j < 0:
        j = len(src)
    seg = src[i:j]
    if "  status: fixing" not in seg:
        print("  ★status 不是 fixing ⇒ 已被别的 job 签过 ⇒ 不落盘 (★防撞车★)")
        return False
    if not all(ok for _, ok, _ in lines):
        print("  ★验收线有红项 ⇒ 拒签 (★fail-closed★)")
        return False

    vr = ("✅ verified (★main 2026-11-24 06:0x 本机独立复核 · 不抄 agent 报告★) ⇒ "
          "★**签收闸 `state/_apply_20260724_0600_main_sign_iss379.py` 自跑验收线, 全绿才签 (fail-closed)★** ⇒ "
          + "; ".join("%s=%s" % (n, "✅" if ok else "❌") for n, ok, _ in lines)
          + " ★ **零写板** (板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4940213 三项未动 ⇒ **G1 仍开, 不许投板**) · "
            "零落表 (网表/脚表/BOM/gate_check/merge/frag_write 六件 md5 同基线) · 零改既有闸 · 零改既有页面正文 · 零挂链 · 别人的分片零越界 · 零外发 · 未替老板拍板 · 未新增拍板项 ★ "
            "★★【main 独立复核的三条要点】★★ ① **K2 那条红的根因 = 闸自己把 pad 角度取整到 6 位 (★`round(math.radians(90),6)` ⇒ -3.268e-7 rad ⇒ 铜-铜距离偏 +1.25e-7 mm ⇒ "
            "在 rot 90 格 (7.4000,75.8000) 把余量 3.1266499666 顶成 3.1266500913 ⇒ round4 由 3.1266 翻成 3.1267) ⇒ 【证据侧对 · 闸侧错】** ⇒ "
            "★**main 亲跑第三路独立复算 (`tmp/iss379/tools/third_path_recheck.py` · ★自写 s-表达式扫描器 + 自写凸多边形间距算法 · 不 import 闸 · 不 import 扫描脚本★) "
            "⇒ 精确角 ⇒ 3.1266 / 有损角 ⇒ 3.1267 ⇒ 双向都复现 ⇒ 根因独立成立** ⇒ **修在产生点 (删角度取整·扫描脚本一字未动·证据 JSON 一个数都没手工改)·★余量容差仍 1e-6 未放宽★** "
            "② **闸读数确定性: 连跑 3 次 K2 逐字相同** (★防「读数会漂」的闸★) ③ **证据 JSON 唯一权威份** (其余三份改名归档带 `_nonauth`) · "
            "★★【一处留证内部不一致 (★已登记·★不影响结论★)★★**: 交卷页 B6 贴的那段自证读数写「边界环 `12000` 格」, 而闸现读是「边界环 `3010` 格」 ⇒ "
            "★**main 本机穷举验证: ① 连跑 3 次闸 ⇒ 逐字都是 3010 (★确定性成立★) ② 把页面 `FEAS.evidence_json` 指针逐个指向【四份 JSON】(live + 三份归档) 各跑一遍 ⇒ "
            "★**四份全部都是 3010 ⇒ 这个数与「读哪份 JSON」无关** ⇒ ③ `logs/iss379/gate_run_20261124.txt` (05:17) 落盘的也是 3010 ⇒ "
            "★**⇒ 结论: B6 那段贴的是【过期读数】(★大概来自边界环抽样预算 `BUDGET=12000` 生效前的版本或更早的一次跑★)·★而 B8 段与真相页 §10.1 写的都是 3010 (★与现读一致★) "
            "⇒ ★**⇒ 留证链以 B8/§10 与盘上日志为准·★B6 那段是【追加式留下的老读数·★按纪律不能改老字·★故就地标注** ⇒ ★**不影响任何结论 (★K0~K8 全绿是读数判定·★"
            "边界环是抽样复核·★现读 3010 也是绿的★)★** ⇒ ★**★引用时只准引 3010 (★现读·★日志·B8·§10 三处一致★)·★不许引 12000★** ★ "
            "★★【main 的裁决 (★详见 pm.yaml 同 key 的 answers·★一件没代老板拍板★)★★**: ① 换 land = 【已决】(★`B33_PIN_LAND_1P27` 11-17 已拍·★不用重问·★本单新增的是「代价与结构红灯」这层·★并进那一趟★) "
            "② 落点 = 【挂起·不是不裁】(★三个候选全 [实测] 在案·★但坐标全挂在现役板 160×100 的框上·★而【板框上位问题 `boss_u1_upper_axis_board_trip_physical_product` 仍未答】·★"
            "若乙则三个坐标全部作废 ⇒ ★**上位问题落甲的那一趟 main 必须回来签掉这条★·★main 已写好裁决口径 (【pin 顺序不变】优先·★倾向 rot 90 + (18.4000,68.4000) 余量 0.1155·★但那是倾向不是拍板★)**) "
            "③ net 映射口径 = 【沿用新 land 的 pin1】(★「沿用现位从左到右」在 rot 270 下物理上不成立·★不是两条都能用·★这条随落点一起落·★免得自相矛盾★) "
            "④⑤ 转 mech-lead (★要求把 J_DEBUG + J_UART 两连接器的座体/开口/清空区【合到一件】答·★别分两票·★同批改的板两个答案不能互相矛盾★) "
            "⑥ 转 sw-lead (★`UART_RX` 板面 0 段铜 = 独立于 land 换装的缺口·★且 unc 45→0 【抓不到它】⇒ 那一趟要加一条【每条网按预期拓扑逐条列铜】的验收线·★防「假连通」★) "
            "⑦ 重复段 = 清·★但并进那一趟布线改道的同一次工序 (★不单开一条工序·★单开 = 多动一次板 = 违「板只改一次」★) ⑧ 新闸 = 挂·★但与那一趟同批挂 "
            "⑨ 两条订正块 = 落·★但追加式·★与那一趟同批落 (★现在落 = 落一个马上就要被改掉的数 = 制造 churn★) ★ "
            "★★【另记一条 main 实测事实 (★给「板那一趟」用·★零写板★)★★**: 本机实读盘上 `Edge.Cuts` ⇒ ★**X 跨度 `160.0000` mm · Y 跨度 `100.0000` mm** ⇒ "
            "★**⇒ 现役板就是【甲 = 160×100 台架板】那个框 ⇒ 落点坐标的三条候选全部在现役板框内·★但【这一趟画甲还是画乙】仍未拍 (★坐标有效与否取决于那一拍·★不是取决于盘上现在是什么★) ★"
    )

    new = seg.replace("  status: fixing", "  status: verified", 1)
    if "  verify_result:" in new:
        new = new.replace("  verify_result: null", "  verify_result: %r" % (vr,), 1)
    else:
        new = new.rstrip("\n") + "\n  verify_result: %r" % (vr,) + "\n"
    if "  verify_date:" in new:
        import re
        new = re.sub(r"^  verify_date: .*$", "  verify_date: '2026-11-24'", new, count=1, flags=re.M)
    else:
        new = new.replace("  verify_result:", "  verify_date: '2026-11-24'\n  verify_result:", 1)
    if "  verify_by:" in new:
        import re
        new = re.sub(r"^  verify_by: .*$", "  verify_by: main", new, count=1, flags=re.M)
    else:
        new = new.replace("  verify_result:", "  verify_by: main\n  verify_result:", 1)
    if "  fix_ref:" in new:
        import re
        new = re.sub(r"^  fix_ref: .*$", "  fix_ref: 'state/_apply_20260724_0600_main_sign_iss379.py'",
                     new, count=1, flags=re.M)
    else:
        new = new.rstrip("\n") + "\n  fix_ref: 'state/_apply_20260724_0600_main_sign_iss379.py'\n"

    bak = LOG + ".bak_%s_main_sign_iss379" % STAMP
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(src[:i] + new + src[j:])
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, LOG)

    d0 = yaml.safe_load(src)
    d1 = yaml.safe_load(read_lines(LOG))
    i0 = {x.get("id"): x for x in (d0.get("issues", d0) if isinstance(d0, dict) else d0)}
    i1 = {x.get("id"): x for x in (d1.get("issues", d1) if isinstance(d1, dict) else d1)}
    assert set(i0) == set(i1), "★条目集合变了 ⇒ 中止★"
    for iid in i0:
        a, b = dict(i0[iid]), dict(i1[iid])
        if iid != "ISS-379":
            assert a == b, "★%s 有别的变化 ⇒ 中止★" % iid
    e = i1["ISS-379"]
    assert e.get("status") == "verified", "★status 没落 verified ⇒ 中止★"
    print("  ★issue_log 写前 md5 = %s" % before)
    print("  ★issue_log 写后 md5 = %s" % md5(LOG))
    print("  ★备份 = %s" % os.path.basename(bak))
    print("  ★自检: 条目集合不变 + 仅 ISS-379 变 + status=verified ⇒ ✅")
    return True


# ===================================================================== 阶段 4 · 一页 (追加式)
ONEPAGER_SECTION = """

## ★★㊱ 【2026-11-24 06:0x · 追加式】★ ISS-379 (hw-lead · `J_UART` 换官方 P1.27 THT land 落位可行性) 独立复核签收 + ★★K2 那条红的根因 = 闸自己把角度取整到 6 位★★ + ★★九问已裁 (★一件没代老板拍板★)★★

★**① 签收 (★main 本机实跑 · fail-closed · 不抄 agent 报告★)★**: 自带闸 `HW/check_juart_land_fit.py` 裸跑 rc=0 (★K0~K8 九条全绿★) · `--selftest` rc=0 (★19/19 · 末行 `ALL TESTS PASS★`) · merge rc=0 · gate_check rc=0 (★Q1 **18/18**★) · 板三项逐字节未动 ⇒ ★**G1 仍开, 不许投板** ★

★**★★② ★★本轮最要紧的一条: K2 那条红的根因 = 【闸自己】把 pad 角度取整到 6 位 (★不是证据错·★是闸错★)★★**: ★**原码 `round(math.radians(90),6)` ⇒ -3.268e-7 rad ⇒ 铜-铜距离偏 +1.25e-7 mm ⇒ 在 rot 90 格 `(7.4000, 75.8000)` 把余量 `3.1266499666` 顶成 `3.1266500913` ⇒ `round4` 由 `3.1266` 翻成 `3.1267` ⇒ 【证据侧对 · 闸侧错】** ★ ⇒ ★**main 亲跑第三路独立复算 (`tmp/iss379/tools/third_path_recheck.py` · ★自写 s-表达式扫描器 + 自写凸多边形间距算法 · **不 import 闸 · 不 import 扫描脚本**★) ⇒ 精确角 ⇒ `3.1266` / 有损角 ⇒ `3.1267` ⇒ 双向都复现 ⇒ **根因独立成立** ★ ⇒ ★**⇒ 修在产生点 (删角度取整 · 扫描脚本一字未动 · 证据 JSON 一个数都没手工改) · ★**余量容差仍 `1e-6` 未放宽 (★擦症状 ≠ 修根因★)** ★ ⇒ ★**★这正是「板那一趟」最需要的形态: 闸红的时候, 红的是闸自己·★不是板坏了·★这一条被独立复算钉住了★** ★

★**③ 九问 main 已裁 (★main 地界·★一件没代老板拍板★·★全文见 `state/fragments/pm.yaml` 同 key 的 answers★)★**
| # | 问的 | main 的裁决 |
|---|---|---|
| ① | `J_UART` 换不换官方 1×2 THT land? | ★**换·★已决·★不用重问** (`B33_PIN_LAND_1P27` 11-17 已拍) ⇒ 本单新增的是「代价与结构红灯」这层 ⇒ 并进那一趟 ★ |
| ② | 落点定哪个? | ★**挂起·不是不裁** ⇒ 三个候选全 [实测] 在案, 但坐标全挂在现役板 `160×100` 框上 ⇒ ★**板框上位问题 (`boss_u1_upper_axis_board_trip_physical_product`) 仍未答 ⇒ 若乙则三个坐标全作废** ⇒ ★**落甲那趟 main 回来签掉; 裁决口径已写好: 【pin 顺序不变】优先 ⇒ 倾向 rot 90 + `(18.4000, 68.4000)` 余量 `0.1155` (★倾向·不是拍板★)** ★ |
| ③ | pad1/pad2 的 net 映射按哪个口径? | ★**沿用新 land 的 pin1** ⇒ 「沿用现位从左到右」在 rot 270 下物理上不成立 ⇒ 这条随落点一起落 (★免得两条各自拍、拍出自相矛盾★) ★ |
| ④⑤ | 罩开口/座体清空区挤不挤? 铜箔 X 宽 `2.2700` vs 清空区 `2.5400` ⇒ 每边 `0.1350` < `CRIT` `0.60` ⇒ 结构红灯 | ★**转 mech-lead** ⇒ ★**要求把 J_DEBUG (★`1.5175`★) 与 J_UART 两条【合到一件】答·★别分两票·★同批改的板两个答案不能互相矛盾★** ★ |
| ⑥ | `UART_RX` 板面 0 段铜 (0 走线 0 过孔, 只有两个 pad) | ★**转 sw-lead** ⇒ ★**这是独立于 land 换装的缺口·★且 unc 45→0 【抓不到它】⇒ 那一趟要加一条【每条网按预期拓扑逐条列铜】的验收线 (★防「假连通」★)** ★ |
| ⑦ | `UART_TX` 的 `F.Cu` 段在板上重复 2 次 (几何完全相同) | ★**清·★但并进那一趟布线改道的同一次工序** (★不单开一条工序·★单开 = 多动一次板 = 违「板只改一次」★) ⇒ 并登记为那一趟必做子项 ★ |
| ⑧ | 新闸挂不挂 `state/gate_check.py`? | ★**挂·★但与那一趟同批挂** (★先例 ISS-300/309/312/315 + ISS-372 U7 同款·★提前单独挂 ⇒ 中间态红·★现场误读成「板坏了」★) ⇒ 本轮零动 `gate_check.py` ★ |
| ⑨ | 两条追加式订正块要不要现在落? | ★**落·★但追加式·★与那一趟同批落** (★现在落 = 落一个马上就要被改掉的数 = 制造 churn★) ⇒ 本轮零碰既有页面正文 ★

★**④ 一处留证内部不一致 (★已就地标注·★不影响结论★)★**: 交卷页 B6 贴的自证读数写「边界环 `12000` 格」, 而闸现读是「边界环 `3010` 格」 ⇒ ★**main 穷举验证: 连跑 3 次闸逐字都是 `3010` (★确定性成立★) + 页面 `FEAS.evidence_json` 指针逐个指向【四份 JSON】各跑一遍 ⇒ 四份全是 `3010` (★与读哪份无关★) + `logs/iss379/gate_run_20261124.txt` (05:17) 也是 `3010`** ⇒ ★**⇒ B6 那段是追加式留下的老读数·★B8 段与真相页 §10.1 写的都是 `3010` (★与现读一致★)⇒ ★**引用时只准引 `3010`, 不许引 `12000`** ★

★**⑤ main 实读盘上板框 (★给「板那一趟」用·★零写板★)★**: `Edge.Cuts` ⇒ ★**X 跨度 `160.0000` mm · Y 跨度 `100.0000` mm** ⇒ ★**现役板就是【甲 = 160×100 台架板】那个框** ⇒ 落点三条候选全在现役板框内 ⇒ ★**但「这一趟画甲还是画乙」仍未拍 (★坐标有效与否取决于那一拍·★不是取决于盘上现在是什么★)** ★

★**板面**: md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ ★**19 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★
★**外发段**: ★**恒空** (★老板 2026-11-12 02:02「不再发信, 全靠自己查」★)
"""


def apply_onepager():
    print("\n" + "=" * 92)
    print("★阶段 4 · DECISION_ONE_PAGER_2026-11-22.md (★追加式★)")
    print("=" * 92)
    src = read_lines(ONEPAGER)
    before = md5(ONEPAGER)
    if "§㊱" in src:
        print("  ★§㊱ 已存在 ⇒ 跳过")
        return True
    bak = ONEPAGER + ".bak_%s_main_sign_iss379" % STAMP
    shutil.copy2(ONEPAGER, bak)
    tmp = ONEPAGER + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(src + ONEPAGER_SECTION)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, ONEPAGER)
    assert read_lines(ONEPAGER).startswith(src), "★一页老字被改 ⇒ 中止★"
    print("  ★一页 写前 md5 = %s" % before)
    print("  ★一页 写后 md5 = %s" % md5(ONEPAGER))
    print("  ★备份 = %s" % os.path.basename(bak))
    return True


def main():
    m0, ns0, sz0 = board_fp()
    print("★开工侧板指纹: md5=%s mtime_ns=%d size=%d" % (m0, ns0, sz0))

    ok, lines = verify()
    if not ok:
        print("\n★★验收线有红项 ⇒ 不落盘 (★fail-closed·★拒签★)★★")
        return 1

    apply_pm()
    signed = sign_issue_log(lines)
    apply_onepager()

    m1, ns1, sz1 = board_fp()
    same = (m0 == m1 == BOARD_MD5 and ns0 == ns1 == ns_of(BOARD_MTIME) and sz0 == sz1 == BOARD_SIZE)
    print("\n★收工侧板指纹: md5=%s mtime_ns=%d size=%d" % (m1, ns1, sz1))
    print("★零写板自证: %s" % ("✅ 三项逐字节未动" if same else "❌"))
    rc, _ = sh("python3 state/merge.py")
    print("★收尾 merge.py rc=%d" % rc)
    rc2, o2 = sh("python3 state/gate_check.py")
    print("★收尾 gate_check.py rc=%d (Q1 18/18: %s)" % (rc2, "18/18" in o2))
    print("\n★全流程收工 (★零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 未替老板拍板★)")
    return 0 if (same and signed) else 1


if __name__ == "__main__":
    sys.exit(main())
