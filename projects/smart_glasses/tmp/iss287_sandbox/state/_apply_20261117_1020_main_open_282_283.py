#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 10:2x · job 775d9893「ARS45 继续执行后继计划」
★(1) 开 ISS-283 (hw-lead · V-2 落表解锁 + W-4 写法A + G-5 亮度落表)★
★(2) 开 ISS-284 (sw-lead · P10 方案② 落地)★
★(3) 把老板 09:49 的 P9 / P7-P8 决策【追加】进 ISS-278 (mech-lead 在飞) 的 task_brief + note★
★(4) 更新 ISS-181 (板那一趟) 的 note: 恢复条件进度 (还剩什么)★
★**只动 state/issue_log.yaml 一个文件 (文件尾追加 2 块 + 就地替换 2 个多行标量)★**
★**纪律: 多行标量 (note / task_brief) 一律走「yaml 取旧值 → 拼新值 → 单行 json 写回 → 全量复核」★**
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_1020_main_open_282_283_relay_278_181"
TODAY = "2026-11-17"

BRIEF_282 = os.path.join(PROJ, "state", "dispatch_briefs", "ISS-283_hw_v2_unlock_w4_g5_landing.md")
BRIEF_283 = os.path.join(PROJ, "state", "dispatch_briefs", "ISS-284_sw_hard_protected_legal_reboard.md")


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


RELAY_278 = """

---

## ★★⑨ 老板 2026-11-17 09:49 拍板 (★追加 · 你这一趟不用改口径, 照这两条做★★)

★**老板原话: 「按照你的建议执行」⇒ 下面两条已是【已拍板】, 不再是待拍项, 你直接照做★**

| # | 拍板 | 内容 |
|---|---|---|
| ★**P9** ★ | ★**选项 A = 拆成两条** ★ | ★**检修口 / 调试口开口拆成两条, 各自按现役帧 `B160x100` 给坐标** ★ · ★**调试口开口 = X 137.850..148.050 × Y 54.300..58.900** ★ · ★**UART 检修口 = X 13.790..23.990 × Y 66.300..70.900** ★ ⇒ ★**两条都不压 SoM 座**★ · ★**理由 = 合并几何上不可能 (`J_DEBUG`@(144.30,58.00) 与 `J_UART`@(20.74,70.00) 相距 123.56mm ⇒ 合并要清空 126.218mm vs 开口 10.20mm ⇒ 差 116.017mm)**★ |
| ★**P7 / P8** ★ | ★**选项 A = 改现役 160×100 台架板** ★ | ★**那一趟 (S1~S13) 的坐标帧 = `B160x100`** (★不是产品板 60×30/60×15★) ⇒ ★**你出的 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 口径与之一致, 继续按 `B160x100` 出规格**★ |

★**★仍然悬着的那一条 (★不许你替老板拍, 也不许你把它当已定★)**: ★**座体真实高度 h = [0数据]** ★ ⇒ ★**开口 Y 的一切数仍建在「座体高 2.54mm」这个假设上** ⇒ ★**你的 §4b「座体高度参数化」照做 (f(h) + 三档代入 + 降级方案) ⇒ 等你出完规格, 这一条再回来拍** ★
"""

RELAY_181 = (
    " ★**2026-11-17 10:2x 更新 (main) —— 老板 09:49「按照你的建议执行」后的恢复条件进度★**: "
    "★**已清**: A1 (V-3=E) + A2 (V-4=680) ★**已落表** (09:58:16 · rc=0) · P7/P8 (画现役 160×100 台架板) · P9 (开口拆两条) · "
    "W-4/P4 (Q_PG 写法 A) · G-5/P6 (LED 20mA 档 = 红 68Ω / 绿 55Ω) · P10 (方案②) · A3 架构轴 (V-2 = 1) ★"
    "⇒ ★**仍卡这三条 (★所以这一趟【仍不许开工】★)**: ① ★**A4 / A5 老板还没拍** (★关机/待机语义 + 负载开关选型追认 ★ ⇒ G1a-8 还红★) ② "
    "★**ESD 型号轴 + D− 侧 (W-1b / W-1c / W-2) 还没拍** ③ ★**三件落表还没做完** (★A3 的 V-2 被行号锚点守卫拦死 ⇒ ISS-283 · "
    "W-4 与 G-5 同单 ⇒ ISS-283★) ⇒ ★**另: 板那一趟必须带的新坑 (ISS-283 §③ 已列)**: V-2 的 net 改名 (`D_ESD_USB_D` pad1) · "
    "Q_PG land 重画 (pad1↔pad3 互换) · D− 侧 ESD 三件 (R4×2 + R9) ⇒ ★**这三条不清掉, G1a-4 的最后 4 条未落表项就还在**★"
)


def dump_block(d) -> str:
    lines = ["- id: %s" % d["id"]]
    for k, v in d.items():
        if k == "id":
            continue
        if v is None:
            lines.append("  %s: null" % k)
        elif isinstance(v, bool):
            lines.append("  %s: %s" % (k, "true" if v else "false"))
        elif isinstance(v, (int, float)):
            lines.append("  %s: %s" % (k, v))
        else:
            lines.append("  %s: %s" % (k, q(v)))
    return "\n".join(lines)


def main() -> int:
    raw = open(LOG, encoding="utf-8").read()
    before = yaml.safe_load(raw) or {}
    bmap = {it["id"]: it for it in before.get("issues", [])}
    for iid in ("ISS-283", "ISS-284"):
        if iid in bmap:
            print("❌ %s 已存在 ⇒ 不许重复开单" % iid)
            return 2

    lines = raw.split("\n")

    def block_range(iid):
        start = end = None
        for i, ln in enumerate(lines):
            if ln.startswith("- id: "):
                if start is not None:
                    end = i
                    break
                if ln[len("- id: "):].strip() == iid:
                    start = i
        if start is None:
            return None, None
        if end is None:
            end = len(lines)
        return start, end

    def replace_scalar(iid, key, newval):
        s, e = block_range(iid)
        if s is None:
            print("❌ 找不到 %s" % iid)
            return False
        blk = lines[s:e]
        ki = None
        for j, ln in enumerate(blk):
            if ln.strip().startswith(key + ":"):
                ki = j
                break
        if ki is None:
            print("❌ %s 块内找不到 %s" % (iid, key))
            return False
        k = ki + 1
        while k < len(blk):
            ln = blk[k]
            if ln.startswith("- id: "):
                break
            ind = len(ln) - len(ln.lstrip(" "))
            if ind == 2 and ":" in ln:
                break
            k += 1
        blk[ki:k] = ["  %s: %s" % (key, q(newval))]
        lines[s:e] = blk
        return True

    # ---------- 3) ISS-278 追加决策 (mech-lead 在飞) ----------
    old278 = bmap["ISS-278"]
    tb = old278.get("task_brief") or ""
    if "⑨ 老板 2026-11-17 09:49 拍板" not in tb:
        replace_scalar("ISS-278", "task_brief", tb + RELAY_278)
    nt = old278.get("note") or ""
    if "老板 2026-11-17 09:49 拍板" not in nt:
        replace_scalar("ISS-278", "note", nt + (
            " ★**2026-11-17 10:2x 追加 (main)**: 老板 09:49 拍板 P9 (★开口拆两条★) + P7/P8 (★坐标帧 = 现役 160×100 台架板 `B160x100`★) "
            "⇒ ★**这两条不再是待拍项, 直接照做**★ ⇒ 任务书已追加「⑨ 老板拍板」节 (★详见任务书末尾★) ⇒ ★**座体高度 h 仍 [0数据] ⇒ 你出 f(h) + 三档 + 降级方案, 那一条之后再回来拍**★"))

    # ---------- 4) ISS-181 note 更新 ----------
    nt181 = bmap["ISS-181"].get("note") or ""
    if "老板 09:49「按照你的建议执行」后的恢复条件进度" not in nt181:
        replace_scalar("ISS-181", "note", nt181 + RELAY_181)

    # ---------- 1/2) 追加两个新单 ----------
    NEW = [
        {
            "id": "ISS-283",
            "title": ("★★[主线内·HW/落表侧·内部活] ★★【三件落表 + 一个工具接口死锁】★★ ★**B1: V-2 (A3) 落表被行号锚点守卫拦死, 必须解锁** ★ "
                      "(★根因 = V-2 落表动作 = 把 `D_ESD_USB_D` pad1 的网名 `USB_D_P_SRC` 改成 `NET_USB_D_P_TYPEC` ⇒ 改的是守卫的【实体身份 (ref+net)】⇒ 判 RED ⇒ 落表器自动回滚★) ★ "
                      "★★ **B2: W-4 (P4/G-1) `Q_PG` 写法 A 落表** ★ (★S=BAT_SW / D=ON / G=PG★ ⇒ ★**并且 pad1↔pad3 的网要互换**★ ⇒ ★DMP3098L 引脚序 1=G/2=S/3=D★ ⇒ ★**板那一趟必须重画 Q_PG 的 land**★) ★ "
                      "★★ **B3: G-5 (P6/W-6) LED 亮度档落表** ★ (★R_LED_R 1k→68Ω · R_LED_G 1k→55Ω = 20mA 档★) ★★ ★"
                      "(★老板 2026-11-17 09:49「按照你的建议执行」⇒ 这 8 条已落账★) ★"),
            "severity": "high",
            "owner": "hw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-19",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": (
                "2026-11-17 10:1x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = 老板 2026-11-17 09:49「按照你的建议执行」+ main 本机实跑** ★\n"
                "⇒ ★**任务书 `state/dispatch_briefs/ISS-283_hw_v2_unlock_w4_g5_landing.md`** ★\n"
                "⇒ ★**本机实测证据**: ① A1+A2 落表 **rc=0** (V-3=E + V-4=680 · 09:58:16 · 台账 §16 有老板凭据机器化留痕) "
                "② A3 (V-2=1) 落表 **rc=1 ⇒ 工具自动回滚** ⇒ ★**五条锚点全红在 L417 = `D_ESD_USB_D` 那行** ★ "
                "③ ★**半回滚的后遗症已修**: 回滚没还原 registry ⇒ 216 条 gen 锚点漂移 ⇒ `--reanchor` 修回 PASS=310/DRIFT=0/RED=0 (★只动 registry, 板与网表逐字节不变★) ★\n"
                "⇒ ★**边界**: 零写板 (★板 `611b869e…` / `.kicad_pro 3e504d2b…` 一个字节不许动★) · 零改既有判据阈值 · "
                "★**不许弱化行号锚点守卫的 fail-closed 三条** ★ · 不碰 MECH/SW 的分片与文件 · 零外发 · ★**不替老板拍板 (★ESD 型号轴 + D− 侧仍待拍★)** ★ · 不自签 issue_log ★"
            ),
            "dispatched_at": None,
            "task_brief": open(BRIEF_282, encoding="utf-8").read(),
        },
        {
            "id": "ISS-284",
            "title": ("★★[主线内·SW 侧·门禁/台账机制·内部活] ★★【P10 落地: SW 台账 `hard_protected` 怎么合法跟上「板只改一次」】★★ ★"
                      "⇒ ★**老板 2026-11-17 09:49 拍板 = 方案 ② (保留纯 md5 + 显式单号背书的合法改板动作)** ★ ⇒ ★**自带一条缝必须一起堵**: "
                      "「单号与 md5 可各自独立编辑 ⇒ 有缝 ⇒ 必须做成【一个字段两个值】且台账里查得到」★ ⇒ ★**三条红线一条不许动** (不许「随手改 md5 就绿」/ 不许放宽「盘上≠链头⇒红」/ 不许把「取不准」放宽成「取最近一条」★ ★"),
            "severity": "high",
            "owner": "sw-lead",
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-19",
            "status": "open",
            "external": False,
            "need_keys": [],
            "fix_ref": None,
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": (
                "2026-11-17 10:1x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = 老板 2026-11-17 09:49「按照你的建议执行」+ ISS-279 交卷单 §4/§5 (★三方案 + 三条红线 + 那条缝★)** ★\n"
                "⇒ ★**任务书 `state/dispatch_briefs/ISS-284_sw_hard_protected_legal_reboard.md`** ★\n"
                "⇒ ★**现状 (main 10:0x 实测)**: 网表/脚表/BOM 走的是 ISS-275 的「台账为准」新口径 ⇒ A1+A2 落表后 SW R6 仍绿 ⇒ "
                "★**本单只解决板那两件** (`611b869e…` + `3e504d2b…` · 走【独立纯 md5 比对】`check_demo_panel_spec.py` L459~L472) ★\n"
                "⇒ ★**边界**: 零写板 · 零落表 (网表/脚表/BOM 一个字节不许动★) · ★**不许动 ISS-275 那条已跑通的链头逻辑** ★ · "
                "★**不许放宽 fail-closed 三条** ★ · 不碰 HW/MECH 的文件与分片 · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
            ),
            "dispatched_at": None,
            "task_brief": open(BRIEF_283, encoding="utf-8").read(),
        },
    ]

    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    text += "\n".join(dump_block(d) for d in NEW) + "\n"

    shutil.copy2(LOG, BAK)
    open(LOG, "w", encoding="utf-8").write(text)

    # ---------- 复核 ----------
    after = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    amap = {it["id"]: it for it in after.get("issues", [])}
    ok = True
    for iid, it in bmap.items():
        a = amap.get(iid, {})
        for k, v in it.items():
            if iid == "ISS-278" and k in ("note", "task_brief"):
                continue
            if iid == "ISS-181" and k == "note":
                continue
            if a.get(k) != v:
                print("❌ %s 的 %s 变了" % (iid, k))
                ok = False
    for d in NEW:
        it = amap[d["id"]]
        print("  %s -> %s owner=%s severity=%s due=%s brief=%d B" % (
            d["id"], it["status"], it["owner"], it["severity"], it["due"], len(it.get("task_brief") or "")))
    print("  ISS-278 task_brief 含拍板节 =", "⑨ 老板 2026-11-17 09:49 拍板" in (amap["ISS-278"].get("task_brief") or ""))
    print("  ISS-181 note 含恢复条件进度 =", "老板 09:49" in (amap["ISS-181"].get("note") or ""))
    print("  其余 issue 全部字段逐字相同 =", ok)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
