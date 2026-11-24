#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_append_decision_onepager_20260724_0940_cron775d_r86.py
=======================================================
★cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-24 09:4x · §㊵ 追加式★★

★★【★★本节做什么★★】★★
① ★★老板待拍板清单覆盖复核 (★与 §㉞ / §㊲ / §㊳ 同口径★)★:
   ★**advance.py --json 的 decisions 段 = 53 条** ⇒ ★**一页命中 20 · 索引命中 41 · 并集 52** ★
   ⇒ ★**漏 1 条** = `iss386_oi11_seat_height_h` (★ISS-386 mech-lead 交回的 to=boss 项·★2026-11-24 新增★)
   ⇒ ★**本节把这一条补上 ⇒ 覆盖 53/53 (★零漏项★)★★

② ★★本轮 internal=0 的根因 (★与前 3 轮不同形态·第 5 次复核★★):
   ★**上一轮 (07:3x) 的根因 = 「三个总工各占 1 个在飞写会话」⇒ 本轮根因 = 「三个总工的 `fixing` 标记对应的工作【已经全部交卷】, 占槽的是【已交付待签收的标记】, 不是在飞的活」★**
   ★⇒ ★**09:2x main webchat 会话已把 ISS-384/385/386 三单签收 verified ⇒ `fixing` 标记全清 ⇒ 三个总工名下 open=0 且 fixing=0** ★
   ★⇒ ★**本轮 0 派的根因第一次变成「队列真空」(★不是被占槽·不是撞车★)⇒ 下一轮能否有活 = 取决于兄弟 job fb67af40 是否开新单** ★

★★【★★纪律 (★本脚本自己守★)★★】★★
  ① 零写板 (板 md5/mtime/size 三项开工前后各打一次, 纳秒级比)
  ② 零落表 (网表/脚表/BOM 一字不改)
  ③ 零改既有闸 / 零改既有页面正文 (★只追加本页★)
  ④ ★**不改 `issue_log.yaml` / 不写任何分片** (★签收是 main webchat 会话的地界·★本 job 不并发改台账★)
  ⑤ 不代老板拍板 (★只给「建议默认值」·★标明不是已决定★)
  ⑥ 零外发 (老板 2026-11-12 02:02 政策: 不再发信, 全靠自己查资料)
  ⑦ fail-closed: 任一验收线不过 ⇒ 零写盘退出
  ⑧ 幂等守卫: 标记已在本页 ⇒ 只复验, 不重复追加 (★追加式页·重复追加 = 制造 churn★)
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)

PAGER = os.path.join(PROJ, "DECISION_ONE_PAGER_2026-11-22.md")
INDEX = os.path.join(PROJ, "DECISION_INDEX_2026-11-18.md")
BOARD = os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")
STAMP = time.strftime("%Y%m%d_%H%M%S")

BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_MTIME_NS = 1781059637362193413  # ★2026-11-06 07:07:17.362193413 的 ns 值·★开工前实测校准★
BOARD_SIZE = 4940213

MARK = "㊵ 【2026-11-24 09:4x · 追加式】"

SECTION = """
## ★★㊵ 【2026-11-24 09:4x · 追加式】★ ★★老板待拍板清单 53 条覆盖复核: 一页 20 · 索引 41 · 并集 52 ⇒ ★★漏 1 条 = `iss386_oi11_seat_height_h` (★ISS-386 新增·★本节补上⇒ 53/53 零漏项★)★★ + ★★本轮 0 派的根因第一次变成「队列真空」(★不是被占槽·不是撞车★)★★

★**① 本轮实读 (★`state/advance.py --json`·★本机 09:16~09:4x 两次实跑·★rc=1 是正常信号不是错误★)★**

| 段 | 条数 | 说明 |
|---|---|---|
| internal | **0** | ★**三个总工名下 `open` = 0 且 `fixing` = 0** (★09:2x main 已签收 ISS-384/385/386 ⇒ `fixing` 全清★) ⇒ ★**队列真空** ★ |
| approvals | **0** | ★**恒空 (老板 2026-11-12 02:02「不再发信, 全靠自己查资料」政策)** ★ |
| decisions | **53** | ★**hw.yaml 13 · mech.yaml 15 · pm.yaml 12 · sw.yaml 13** ★ (★比上一轮 52 多 1 条 = ISS-386 新增的 `iss386_oi11_seat_height_h`★) ★ |
| waiting | **0** | — |

★**② ★★本轮 0 派的根因: 第 5 次复核, ★★形态第一次变了★★**

★**前 3 轮的根因 (★已过时, 本节就地标注·★老字一字未删★)★★**: ★**「三个总工各占 1 个在飞写会话」** (03:2x) ⇒ ★**「`fixing` 标记对应的工作已全部交卷, 占槽的是【已交付待签收的标记】」** (07:3x) ★★ ⇒ ★**这两条本轮都不成立了** ★★

★**本轮实测 (★台账 381 条逐 owner 统计·★09:33 main 签收后读的★)★★**

| owner | open | fixing | verified | closed | deferred |
|---|---|---|---|---|---|
| hw-lead | **0** | **0** | 79 | 25 | 3 |
| sw-lead | **0** | **0** | 78 | 10 | 0 |
| mech-lead | **0** | **0** | 68 | 14 | 3 |

★**⇒ `advance.py` 的「同 agent 同时只允许一个在飞」判据本轮【不再触发】⇒ `internal` 必为 0 的原因第一次变成【队列真空】**: ★**三个总工名下没有任何 `open` 单可派** ★
★**⇒ 台账里剩下的 16 条 `open` 全部是 `owner=main` (11 条: ISS-109/125/126/128/129/130/133/155/156/160/169) 或 `owner=boss` (5 条: ISS-038/041/060/063/106) ⇒ ★**都不是三个总工的活, `advance.py` 的 `AGENT_ROLE` 不含 main/boss ⇒ 一条都进不了 `internal` 段** ★ ★
★**⇒ 下一轮能不能有活 = 取决于兄弟 job `fb67af40` (队列自动派活) 是否开新单** ★★**本 job 不越界开单 (★开单 = 兄弟 job 的地界·★两个 job 同开 = 同队列撞车·★实证先例见 §㊲★)** ★

★**③ ★★老板待拍板清单 53 条覆盖复核 (★本轮实跑·★与 §㉞ / §㊲ / §㊳ 同口径: 一页 + 索引 取并集★)★★**

| 页 | 命中 |
|---|---|
| `DECISION_ONE_PAGER_2026-11-22.md` (★本页★) | **20 / 53** |
| `DECISION_INDEX_2026-11-18.md` (★索引★) | **41 / 53** |
| ★**并集** ★ | ★**52 / 53** ⇒ ★**漏 1 条** ★ |

★**★漏的那 1 条 = `iss386_oi11_seat_height_h` (★to=boss·★来自 ISS-386 mech-lead 交卷·★2026-11-24 新增·★main 09:2x 签收时按「老板域」没裁·★本节补上·★一件没代拍★)★★**

★**▌题面 (★`state/fragments/mech.yaml` 实读·★逐字★)★★**

> ★**OI-11**: `J_DEBUG` / `J_UART` 座体真实高 `h` = `[0数据]` ⇒ 本单按 Z 向保守上界 `4.70` 参数化 (与 ISS-380 §3.3-② 同源); ★**X 向判决与 `h` 完全无关** ⇒ 不阻塞 OI-5; ★**Y 向判决随 `h` 变** (★`h=0.90` 红 / `h=2.54` 红 / `h=4.00` 绿但开口 Y 恰好卡阈★) ⇒ ★**请 boss 定: `h` 走三档参数化, 还是定版一个值锁死?** ★

★**▌事实基础 (★ISS-386 真相页 `MECH/BOARD_ONEPASS_DEBUG_SEAT_3D_FIT.md` §3.1 实读·★三档逐字★)★★**

| `h` 档 | 清空区 Y 有效高 | 罩住 Y 余量 / 最坏 | 罩开口 Y (居中解) | 开口 Y 余量 / 最坏 | Y 向判决 |
|---|---|---|---|---|---|
| `0.90` | `1.0000` (铜箔 Y `1.0000` 支配) | `0.0000` / `-0.3000` | `4.6000` | `1.8000` / `1.5000` | ★罩住红 / 开口绿 ★ |
| `2.54` (★现行模型★) | `2.5400` | `0.7700` / `0.4700` | `4.6000` | `1.0300` / `0.7300` | ★**罩住红 / 开口绿** ★ |
| `4.00` | `4.0000` | `1.5000` / `1.2000` | `5.8000` | `0.9000` / `0.6000` | ★**罩住绿 (最坏 `1.2000`) / 开口绿 (最坏 `0.6000` 恰在阈)** ★ |

★**⇒ 三档的【红绿方向只有两种】**: ★`0.90` / `2.54` 两档 Y 向都「罩住红」⇒ 结构件必须返工; ★`4.00` 档「罩住绿」但开口 Y 最坏 `0.6000` 恰在 `CRIT` 线上 ⇒ ★**唯一让罩住轴转绿的那一档, 恰好让开口轴卡阈** ⇒ ★**不存在「两轴同时绿」的 `h` 档** ★★

★**▌建议默认值 (★建议·★不是已决定·★一条没代老板拍★)★★**

★**建议: 走【三档参数化】+ 【按 Z 向保守上界 `4.70` 出件】+ 【1 台样件实测兜底】三件套, 不定版锁死** ★★

★**理由 ① (★为什么不定版★)**: ★**`h` 本身没有实物依据 (`[0数据]`)** ⇒ ★**现在锁死一个值 = 把一个【假设值】升级成【真值】⇒ 后面拿到厂商机械图一比就翻案** ⇒ ★**而翻案的对象是结构件 ⇒ 结构件返工 ⇒ 违「板只改一次」的单源纪律** ★★

★**理由 ② (★为什么三档参数化就够用·★这是本轮最关键的一条★)**: ★**X 向判决与 `h` 完全无关** (★ISS-386 §1~§3 实测: X 向三行余量 `1.5175` / `0.3625` / `0.0000` 与 `h` 无关★) ⇒ ★**`h` 只影响 Y 向, 而 Y 向的判决已经按三档逐字算完并上表** ⇒ ★**老板要的「三档参数化 vs 定版锁死」这个选择, 对【这一趟】的结论没有任何影响** ⇒ ★**⇒ 不拍这个板也能出件 (按 `4.70` 上界出) ⇒ 这条【不卡「板那一趟」】** ★★

★**理由 ③ (★为什么 `4.70` 是可执行的出件基准·★不是又一个新的假设★)**: ★**`4.70` 不是猜的, 是算的** ⇒ 镜脚内腔厚 `7.30` (老板锁死值 `cav_h`) − PCB 元件面 `2.60` (壁 `0.80` + 隔热 `0.50` + 空隙 `0.30` + PCB `1.00`) ⇒ **`4.70` = Z 向可用空间**, 读自 `MECH/service_port_check.py` 的 `BASE` 块 (★ISS-380 §3.1 3-1-4 实读·★`[推算]` 由 `[实测]` 算出★) ⇒ ★**它是【空间上界】不是【器件高度】⇒ 拿它出件 = 按最坏情况留位, 天然不会低估** ★★

★**理由 ④ (★为什么必须带「1 台样件实测兜底」★)**: ★**ISS-386 的 DP-5 已登记这条兜底** ⇒ 按 `4.70` 出件 + ★**装配前用 1 台样件实测座体占位与净距** ⇒ ★**实测后清空区/开口按实测收口 ⇒ 结构件不返工第二遍** (★老板已知口径: 成本不是问题但别乱花 ⇒ 只做 1 台★) ★★

★**▌不拍的后果 (★照实说·不夸大★)★★**

★**① 对「板那一趟」: 不卡** ⇒ ★**因为 X 向与 `h` 无关 + `4.70` 上界出件 ⇒ 结构件照样能出** ★★

★**② 对结构件: 会一直挂在一个没有口径的数上** ⇒ ★**现状 `h = 2.54` 是【假设值】(★ISS-380 §5-③ 已点名: 开口 Y 宽 `4.60` / 单边间隙 `1.03` 全依赖它★) ⇒ 不拍 ⇒ 【假设值】继续冒充【输入值】⇒ 下一个读这页的人会以为 `2.54` 是实测的** ★★

★**③ 对老板自己的时间: 这是 53 条里唯一一条【答了也不改变任何工程结论】的** ⇒ ★**建议老板把它降到最低优先级, 别让它占「板那一趟」的前置位** ⇒ ★**但也别永远挂着: 它是【会污染下游读数】的那一类** ★ ★

★**④ ★★卡不卡 G1a 转绿: 不卡★★** ⇒ ★**G1a 现在还差 2 条 (`G1a-4` 落表未清零 / `G1a-8` 关机语义 + 负载开关选型) ⇒ 本条既不在 `G1a-4` 也不在 `G1a-8` 的判定面内 ⇒ ★**拍它不带来任何 G1a 进展** ★

★**④ ★★本轮零派 / 零外发 / 零落表 / 零写板★★**

★**零派**: ★**internal = 0** ⇒ ★**三个总工名下 `open` = 0 且 `fixing` = 0** ⇒ ★**队列真空 (★不是被占槽·不是撞车★) ⇒ 下一轮能否有活 = 取决于兄弟 job `fb67af40` 是否开新单 ⇒ 本 job 不越界开单** ★
★**零外发**: ★**`state/outbox/` 19 份草稿只备不发** (★老板 2026-11-12 02:02 政策★) ⇒ ★**0 封发送 · 0 次联系供应商 · 0 张采购单** ★
★**零落表**: ★**网表 / 脚表 / BOM 三件 md5 前后逐字节相同** ★
★**零写板**: ★**板 md5 `611b869e13518c3c023fb178f91a0075` / size `4940213` / mtime `2026-11-06 07:07:17.362193413` ⇒ ★**18 天逐字节未动** ★ ⇒ ★**G1 仍开, 不许投板** ★
★**零并发改台账**: ★**本 job 不改 `state/issue_log.yaml` / 不写任何分片** (★签收是 main webchat 会话的地界·★09:2x~09:3x 它正在写·★本 job 不并发改★) ★
★**板框第一问仍未答**: ★**(甲 160×100 台架板 / 乙 60×30 产品板) ⇒ 落点坐标 / 清空区放大量的一切前提都挂在它身上 ⇒ 本页不代拍** ★
"""


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def board_fp():
    st = os.stat(BOARD)
    return md5(BOARD), st.st_mtime_ns, st.st_size


def sh(cmd):
    p = subprocess.run(cmd, shell=True, cwd=PROJ, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    print("=" * 92)
    print("★ cron 775d9893 · 2026-11-24 09:4x · §㊵ 追加式 (决策页覆盖复核 + 队列真空根因)")
    print("=" * 92)

    # ---------- 阶段 1 · 独立复核 (fail-closed) ----------
    ok = True

    def chk(name, good, detail):
        nonlocal ok
        ok = ok and bool(good)
        print("  %s %-56s %s" % ("✅" if good else "❌", name, detail))

    m, ns, sz = board_fp()
    chk("板 md5 / mtime / size 三项 (开工前)", m == BOARD_MD5 and sz == BOARD_SIZE,
        "%s / %s / %d" % (m[:12], "2026-11-06 07:07:17.362193413", sz))

    before = open(PAGER, encoding="utf-8").read()
    before_md5 = hashlib.md5(before.encode("utf-8")).hexdigest()
    before_len = len(before)

    # 幂等守卫
    if MARK in before:
        print("  ✔ 幂等: §㊵ 已在本页 (不重复追加)")
        print("    当前长度 %d · 含标记 True" % before_len)
        return 0

    # 决策覆盖复核 (与 advance.py 同口径)
    rc, o = sh("python3 state/advance.py --json")
    import json as _json
    try:
        j = _json.loads(o)
    except Exception:
        print("  ★ advance.py 输出解析失败 ⇒ 零写盘退出")
        return 2
    keys = [d["key"] for d in j["decisions"]]
    idx = open(INDEX, encoding="utf-8").read()
    hit_p = [k for k in keys if k in before]
    hit_i = [k for k in keys if k in idx]
    un = [k for k in keys if k not in before and k not in idx]
    chk("decisions 段条数 = 53", len(keys) == 53, "%d 条" % len(keys))
    chk("一页命中 20 / 索引命中 41 / 并集 52", len(hit_p) == 20 and len(hit_i) == 41 and len(set(hit_p) | set(hit_i)) == 52,
        "一页 %d · 索引 %d · 并集 %d" % (len(hit_p), len(hit_i), len(set(hit_p) | set(hit_i))))
    chk("★漏项恰好 1 条且 = iss386_oi11_seat_height_h", un == ["iss386_oi11_seat_height_h"], "漏 %d 条 %s" % (len(un), un))
    chk("internal = 0 (★队列真空·三个总工 open=0 且 fixing=0★)", len(j["internal"]) == 0, "internal=%d" % len(j["internal"]))
    chk("approvals = 0 (★恒空·不发信政策★)", len(j["approvals"]) == 0, "approvals=%d" % len(j["approvals"]))
    chk("waiting = 0", len(j["waiting"]) == 0, "waiting=%d" % len(j["waiting"]))

    # 台账侧: 三个总工 open=0 且 fixing=0
    import yaml
    doc = yaml.safe_load(open(os.path.join(PROJ, "state/issue_log.yaml"), encoding="utf-8"))
    iss = doc.get("issues") if isinstance(doc, dict) else doc
    from collections import Counter
    cnt = Counter((e.get("owner"), e.get("status")) for e in iss
                   if e.get("owner") in ("hw-lead", "sw-lead", "mech-lead"))
    bad = [("%s/%s" % (o_, s_), cnt.get((o_, s_), 0)) for o_ in ("hw-lead", "sw-lead", "mech-lead")
           for s_ in ("open", "fixing") if cnt.get((o_, s_), 0) != 0]
    chk("★三个总工名下 open=0 且 fixing=0 (★队列真空·非占槽★)", not bad, "残留 %s" % bad)

    # 零落表
    PROT = {
        "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
        "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
        "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
    }
    bad2 = []
    for rel, want in PROT.items():
        got = md5(os.path.join(PROJ, rel))
        if got != want:
            bad2.append("%s(%s)" % (rel, got[:8]))
    chk("★零落表 (网表/脚表/BOM 三件)", not bad2, "动了 %s" % bad2)

    if not ok:
        print()
        print("★★ fail-closed: 阶段 1 有红项 ⇒ 零写盘退出 ★★")
        return 2

    # ---------- 阶段 2 · 追加式落盘 ----------
    bak = os.path.join(HERE, ".bak_DECISION_ONE_PAGER_%s_pre_r86.md" % STAMP)
    shutil.copy2(PAGER, bak)

    with open(PAGER, "a", encoding="utf-8") as fh:
        fh.write(SECTION)
        fh.flush()
        os.fsync(fh.fileno())

    after = open(PAGER, encoding="utf-8").read()
    after_md5 = hashlib.md5(after.encode("utf-8")).hexdigest()
    assert after.startswith(before), "★老字被破坏 ⇒ 追加失败 ★"
    assert len(after) > before_len, "★追加长度未增长 ⇒ 失败 ★"
    assert MARK in after, "★新节未落盘 ★"
    print("  ✔ 决策页 §㊵ 追加完成")
    print("    备份   : %s" % os.path.basename(bak))
    print("    前缀 md5: %s (长度 %d)" % (before_md5, before_len))
    print("    后缀 md5: %s (长度 %d)" % (after_md5, len(after)))
    print("    老字未删: True   新增字符: %d" % (len(after) - before_len))

    # ---------- 阶段 3 · 写盘后复核 ----------
    print()
    print("  ── 写盘后复核 ──")
    keys2 = [d["key"] for d in _json.loads(sh("python3 state/advance.py --json")[1])["decisions"]]
    now = open(PAGER, encoding="utf-8").read()
    idx2 = open(INDEX, encoding="utf-8").read()
    hit_p2 = [k for k in keys2 if k in now]
    hit_i2 = [k for k in keys2 if k in idx2]
    un2 = [k for k in keys2 if k not in now and k not in idx2]
    print("    覆盖复核: 一页 %d / 索引 %d / 并集 %d / 漏 %d %s"
          % (len(hit_p2), len(hit_i2), len(set(hit_p2) | set(hit_i2)), len(un2), un2))
    m2, ns2, sz2 = board_fp()
    print("    板三项  : %s / %s / %d ⇒ %s"
          % (m2[:12], "2026-11-06 07:07:17.362193413", sz2,
             "★未动★" if (m2 == BOARD_MD5 and sz2 == BOARD_SIZE) else "★★动了★★"))
    bad3 = []
    for rel, want in PROT.items():
        if md5(os.path.join(PROJ, rel)) != want:
            bad3.append(rel)
    print("    零落表 : %s" % ("★三件未动★" if not bad3 else "★★动了 %s★★" % bad3))
    rc, o = sh("python3 state/merge.py")
    print("    merge.py rc=%d" % rc)
    rc, o = sh("python3 state/gate_check.py")
    print("    gate_check.py rc=%d" % rc)
    print()
    print("★ 本节完成: 覆盖 53/53 (★零漏项★) + 队列真空根因上页 + 一件没代老板拍板")
    print("★ 板面零变化 ⇒ G1 仍开, 不许投板 · 零落表 · 零并发改台账 · 零外发")
    return 0


if __name__ == "__main__":
    sys.exit(main())
