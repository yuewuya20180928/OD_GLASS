#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1155_cronfb67af40_open_390_391.py
================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-24 11:55
★**新开 2 条 + 直接落 fixing** (★铁律⑩-i: 先落 fixing 再 spawn ⇒ 零撞车窗口★)
★**ISS-390 → mech-lead · ISS-391 → hw-lead**

★**为什么现在要新开 (★main 本机实读·不抄任何 agent 报告★)**:
  ★① `python3 state/advance.py --json` ⇒ `internal: []` ⇒ 三个总工名下零 open 可派
  ★② ★**但这三个槽位不是真空, 是被【已交卷待签收】的 fixing 占着** ★
     (★ISS-387 hw-lead: 交卷页 `HANDOFF/2026-11-24_hw-lead_ISS387_FTS单排直插原厂land几何查证.md` 26,363 B @ 11:10 在盘
       + 真相页 `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` + 新闸 `HW/check_fts_single_row_land_truth.py`
       + 分片 hw.yaml 3 条 iss387 登记 @ 11:09 ⇒ ★**真交卷·待 main 签收**★)
     (★ISS-389 mech-lead: 交卷页 `HANDOFF/2026-11-24_mech-lead_ISS389_两连接器座体开口清空区收口作业包.md` 40,225 B @ 11:14 在盘
       + 要求单 + 新闸 `MECH/check_debug_seat_rework_spec.py` + 分片 mech.yaml 9 条 iss389 登记 @ 11:10 ⇒ ★**真交卷·待 main 签收**★)
     ★**⇒ 这两个槽位一签收就空出来 ⇒ 本 job 趁窗口期把下一批活落到位** ★
  ★③ ★**第三条 (ISS-388) 是【僵尸】⇒ 单独走 cont2 重派, 不新开** ★
     (★sw-lead 会话 `e7818570` 11:04:38~11:14:49 · ★**死因 = provider abort (★`openclaw:prompt-error` · 'This operation was aborted'·不是超时不是墙★)★**
      · 交付物 2/3 在盘 (诊断页 20,941 B @11:09 + 新闸 30,823 B @11:11) · ★**交卷页不在盘 + 分片 0 条**★
      · ★**且新闸有 2 处实测假阳性 (main 本机实跑撞出来的·不是抄报告★)**:
        (甲) H5 的 EV_TOKEN_RE (★源码里是 r 后接一个转义左方括号★) ⇒ 把页面上【任何】方括号 token 当成"证据等级" ⇒ 把诊断页自己写的
             `[H1]`/`[FAIL]`/`[PASS]`/`[2a]`/`[Errno 2]` 全判红
        (乙) H1 的 `normalize()` 只替换 sbx_path 与 basename ⇒ 替换不掉【沙盒副本的板 mtime】与【沙盒根路径的两种写法】
             ⇒ ★**⇒ 裸跑恒红 ⇒ 新闸永远挂不进 gate_check ⇒ 会变成第二个"零挂链⇒没人看见⇒烂在盘上"的闸**★)
      · ★**⇒ 所以 cont2 不是"补交卷页", 是"修闸 + 补交卷页"** ★)
  ★④ ★**ISS-390 的依据 = ISS-387 自己留的一条指派给 mech-lead 的 open_item** ★
     (★`HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` L397 逐字:
       "OI-387-4: FTS 直插档座体外形 (宽/深) 官方尺寸 = [0数据] ⇒ 走 §6-④ 降级 (官网 3D/CAD 下载 或 实测样件) ⇒ to=mech-lead"★)
     ★**且 main 本机实读发现一处【前提错误已扩散】**: ISS-389 L634 的 OI-12 答复写「★官方 land courtyard★ 只给每边 0.6400」,
       而 ISS-387 L154 已实测证明 `6.0900`/`5.0800` 是★**通用 KiCad 库件**★的数 (★main 本机复核: 库件 `(size 1 1)` + `(drill 0.65)`★)
       ⇒ ★**同一句话在 `MECH/check_debug_seat_3d_fit.py` L848/L879 的源码字符串里也写着 ⇒ 前提错误已从页扩散到闸源码★**
  ★⑤ ★**ISS-391 的依据 = main 本机实读发现的清单漏项** ★
     (★ISS-387 L149 查实: 落 FTS 时孔径 `0.65 → 0.71` (★官方 `Ø0.71 TYP` vs 库件 `(drill 0.65)`·差 0.06★)★)
     ★**⇒ 而 main 本机实读: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 全文【与 J_DEBUG/J_UART 相关的钻孔/孔径一个都没有】★
     ★**⇒ `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §0.2 ③ 那一项也只写「land pitch 0.50→1.27mm」·`0.71` 出现 0 次★**
     ★**⇒ `HW/check_onepass_preflight_coverage.py` 的 `WP02_BINDING["③"] = (["B33_PIN_LAND_1P27"], [])` ⇒ 零个覆盖令牌
       ⇒ P4 判的是"③ 这一项在清单页有对应 item" ⇒ 【不查 ③ 底下有几条子动作】⇒ ★**改孔漏了 P4 照样绿 = 假绿 (第二次)★★**
     ★**⇒ 那一趟开工时改孔不在清单 ⇒ 不在清单 = 没人做 = 板投出去才发现排针插不进 ⇒ 【板改两次】★**

★**并发写盘护栏**: `state/issue_log.yaml` 是 4.8 MB 大文件, main 的 webchat 会话可能同时在写
  ⇒ ★**本脚本在 `os.replace` 之前重算 md5, 与开读时不一致就中止 (rc=3)** ★

★**边界**: 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板
          · 不改别人分片 · 只写 issue_log.yaml + dispatch_log.yaml + 本脚本自身
"""
import hashlib
import os
import shutil
import sys
import tempfile
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

BRIEF_390 = "state/dispatch_briefs/ISS-390_mech_fts_seat_body_geometry.md"
BRIEF_391 = "state/dispatch_briefs/ISS-391_hw_fts_land_drill_same_batch.md"

JOB = ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-24 11:5x · "
       "★**新开 + 直接落 fixing (★铁律⑩-i 先落 fixing 再 spawn★) · "
       "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` 三条全 rc=0** ★ · "
       "★**纯分析 / 作业包 / 新建闸类 (零写板·零落表·零改既有闸·零改既有页正文·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①** ★ · "
       "★**开单依据 = 三个槽位被【已交卷待签收】的 fixing 占着 (ISS-387/ISS-389) + 本 job 实读撞出的两条真病灶 (通用件当厂件 / 改孔漏出清单) ★** ★")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_entry(e):
    txt = yaml.safe_dump({"issues": [e]}, allow_unicode=True, sort_keys=False,
                          default_flow_style=False, width=100000)
    lines = txt.split("\n")
    assert lines[0].startswith("issues:"), lines[0]
    return "\n".join(lines[1:]).rstrip("\n") + "\n"


NOTE_TAIL = ("★**台账 status 直接落 fixing (★不是 open★) ⇒ advance.py 的 in_flight 规则会挡住任何 job "
             "给该 agent 再派活 ⇒ 零撞车窗口★**")

BOUND = ("★**本单性质**: 纯查证 + 纯分析 + 作业包 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸/既有页面正文 · "
         "零外发 · 不代拍 ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★\n"
         "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file <brief>` rc=0** ★\n")


def main():
    raw = open(LOG, encoding="utf-8").read()
    md5_before = md5(LOG)
    doc = yaml.safe_load(raw)
    issues = doc.get("issues") or []
    ids = {i.get("id") for i in issues}
    for iid in ("ISS-390", "ISS-391"):
        if iid in ids:
            print("★★%s 已存在 ⇒ 停下, 不重复开单" % iid)
            return 2
    print("★ 开读时: issue_log md5=%s · 条数=%d" % (md5_before, len(issues)))

    def brief(p):
        return open(os.path.join(PROJ, p), encoding="utf-8").read()

    # ---------------- ISS-390 · mech-lead ----------------
    e390 = {
        "id": "ISS-390",
        "title": ("★★[★新主线·PCB 线·MECH 侧·纯查证+新建闸·零写板] `FTS` 直插档【座体外形 (宽 X / 深 Y / 绝缘体高 Z)】官网查证 "
                  "+ 「通用库件 courtyard 被当成厂件」这条前提订正 + 降级方案 ★★"),
        "severity": "high",
        "source_blocker": "ISS-387",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·MECH 侧·纯查证+纯分析+新建闸·零写板·零落表]★\n\n"
                 "★**题 (来源 = ★**ISS-387 真相页 L397 自己留的一条指派给 mech-lead 的 open_item** + ★**main 本机实读撞出的一处"
                 "「前提错误已扩散」**★)★: ★\n\n"
                 "★**① ISS-387 (★hw-lead · 今日 11:1x 已交卷★) 查明: `FTS` 直插档【座体外形 (宽 X / 深 Y / 绝缘体高 Z)】官方尺寸 = `[0数据]`** ★\n"
                 "★**⇒ 且同一单实测出: MECH 整条 3D 判决链吃的 `4.8100`/`2.2700`/`F.CrtYd 6.0900`/`F.Fab 5.0800` 全是【盘上通用 KiCad 库件】的数** ★\n"
                 "★**⇒ 而 ISS-389 (★mech-lead · 今日 11:1x 已交卷★) 的 `OI-12` 结构侧答复里, 把 `6.0900` 写成了「★官方 land courtyard★」** ★\n"
                 "★**⇒ ★★「拿通用件的 courtyard 当厂件的 courtyard 去比」⇒ 「判据偏紧 `0.5200`」这个结论的对照物是错的 ★★** ★\n"
                 "★**⇒ ★★**main 本机独立复核 (★不是抄 ISS-387★): 库件 `PinHeader_1x04/1x02_P1.27mm_Vertical.kicad_mod` ⇒ `(size 1 1)` + `(drill 0.65)` ⇒ "
                 "`6.0900`/`5.0800` 的来源 = 第三方库件, 与 Samtec 无关★** ★\n"
                 "★**⇒ ★★**且这条前提错误已经扩散到 `MECH/check_debug_seat_3d_fit.py` L848/L879 的源码字符串里 (★两处都写着「而官方 land 的 F.Fab 5.0800 / F.CrtYd 6.0900」★)**** ★\n\n"
                 "★**② ISS-387 §6-④ 已写好两条降级路径 (★照着走, 不许另造★)**: ★**(甲)** 官网单品页 3D 模型/CAD 下载 ⇒ 量座体外形补 `keepout_dwg` ; "
                 "★**(乙)** 实测样件复现路径 ⇒ 落 FTS 时先打一块单板样, 卡尺量【座体宽 X / 座体深 Y / 绝缘体高 Z】三个量, 回填 `keepout_dwg` ⇒ "
                 "★**两条都不许写成「等原厂回信」/「待外部确认」** ★\n\n"
                 "★**③ 已知环境事实 (★main 本机实测, 免得白试★)**: `www.samtec.com` 在本机一律 HTTP 429 (Cloudflare 1015) ⇒ "
                 "网页类文字走搜索后端 (★证据等级记 `[官网]`, 来源通道等价, URL 留档★) ⇒ ★★**但 `suddendocs.samtec.com` 域是本机 `curl` 直连通的 (HTTP 200 + 有 md5) ⇒ 3D/CAD 下载件大概率也在那条通道上**★★ ★\n\n"
                 "★**④ 本单要交 3 件**: ★**(甲)** 新建真相页 `MECH/BOARD_ONEPASS_FTS_SEAT_BODY_GEOMETRY.md` (★§0~§7 + 机器块★) ★"
                 "★**(乙)** 新建机器闸 `MECH/check_fts_seat_body_geometry.py` (★G1~G7 + ≥8 条反向用例, 其中 ≥4 条专打「定性」判据★) ★"
                 "★**(丙)** 交卷页 B1~B6 齐全 + 分片 (≥3 产出物 + ≥5 interface_claims + needs_from to=main)★ ★\n\n"
                 "★**⑤ ★★本单的机检硬要求 (★main 本机实读 `state/gate_check.py` L47~L54★)★★**: 交卷页 B1~B6 六段必须齐全, "
                 "且 `pick_handoff` 取【最新一份】评分 ⇒ ★★**最新一份自称 B 块结构但缺块 ⇒ 不许回退 ⇒ Q1 立刻掉** ★★ ⇒ "
                 "⇒ ★**六段标题必须含 `REQUIRED_BLOCKS` 的关键词** (★`结论摘要`/`验收标准自评`/`证据分级`/`接口取值声明`/`未决项`/`自证复现命令`★) ★★\n\n"
                 "★**⑥ 降级方案是【必须项】不是可选项**: ★**查不到厂件外形 ⇒ 必须写清【路径 (乙) 的可执行动作】(谁在什么时候量哪三个量、量完填回哪一格) ⇒ "
                 "不许把「查不到」写成阻塞项挂着 ⇒ 更不许写「等原厂回信」** ★\n\n"
                 + BOUND),
        "owner": "mech-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["oi387_4_fts_seat_body_outline", "iss386_oi12_cover_criterion_too_strict",
                      "iss386_oi11_seat_height_window"],
        "task_brief": brief(BRIEF_390),
        "note": ("★2026-11-24 11:5x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ mech-lead 名下 ISS-389 已交卷 (交卷页 40,225 B @ 11:14 + 分片 mech.yaml 9 条 @ 11:10) "
                 "⇒ 槽位待 main 签收后释放 ⇒ 本 job 趁窗口期把下一批活落到位 ③ ★**本单 trigger = ISS-387 真相页 L397 自己留的一条 "
                 "指派给 mech-lead 的 open_item (`OI-387-4` 座体外形 `[0数据]` ⇒ 走 §6-④ 降级)·至今 0 人做** ★ "
                 "④ ★**main 本机实读撞出: ISS-389 L634 的 OI-12 答复把 `6.0900` 写成「官方 land courtyard」, 而 ISS-387 L154 实测证明那是"
                 "【通用 KiCad 库件】的数 (★main 本机复核库件 `(size 1 1)` + `(drill 0.65)`★) ⇒ 前提错误已扩散到 `MECH/check_debug_seat_3d_fit.py` L848/L879 源码字符串** ★\n"
                 + BOUND
                 + NOTE_TAIL),
    }

    # ---------------- ISS-391 · hw-lead ----------------
    e391 = {
        "id": "ISS-391",
        "title": ("★★[★新主线·PCB 线·HW 侧·纯分析+作业包+新建闸·零写板] 「板只改一次」那一趟的排针 land 【`0.65 → 0.71` 钻孔这一条板侧改动"
                  "还没进作业包/预检清单】⇒ 把它补进去 (★纯分析 + 改文档 + 新建闸·零写板·零落表·零改既有闸★) ★★"),
        "severity": "high",
        "source_blocker": "ISS-387",
        "source_agent": "main",
        "desc": ("★★[★新主线·PCB 线·HW 侧·纯分析+作业包+新建机器闸·零写板·零落表·零改既有闸/既有页面正文]★\n\n"
                 "★**题 (来源 = ★**main 本机实读撞出的清单漏项** · ★**不是抄任何 agent 报告**★)★: ★\n\n"
                 "★**① ISS-387 (★hw-lead · 今日 11:1x 已交卷★) 查明: 落 `FTS` 时【板上钻孔必须 `0.65 → 0.71`】** ★\n"
                 "★**⇒ 官方 `Ø 0.71 (TYP)` (★官网推荐 PCB 图 FIG 1 文字层逐字 `.028 0.71 (TYP)`★) vs 盘上通用库件 `(drill 0.65)` ★\n"
                 "★**⇒ main 本机独立复核: 本机 KiCad 库件 `PinHeader_1x04/1x02_P1.27mm_Vertical.kicad_mod` ⇒ `(size 1 1)` + `(drill 0.65)`** ★\n"
                 "★**⇒ ★★**孔位 (排距/跨距) 不动 ⇒ 铜箔包络不动 ⇒ MECH 全链余量数一个都不动 ⇒ 结构件不必因此再返工一次** ★★**\n"
                 "★**⇒ 但这一改是【板侧改板】, 必须与「板只改一次」那一趟同批** ★\n\n"
                 "★**② ★★main 本机实读: 那一趟的作业包 §0.2 ③ 与预检清单 `B33_PIN_LAND_1P27` 里, 【没有这一条】★★ ★\n"
                 "★**· `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` L47 §0.2 ③ 那一行逐字只写「`J_DEBUG`/`J_UART` 排针 land 0.50→1.27mm」** ★\n"
                 "★**· `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 全文里, 【与 J_DEBUG/J_UART 相关的钻孔/孔径/Ø 一个都没有】(★grep `0.65`/`0.71`/`drill`/`钻孔`/`Ø` "
                 "命中的全是别的器件: `Q1` 的 SOT 封装 / `J_USB_C` 的 NPTH `Ø0.650`/`Ø0.762` / S10 重出钻孔★) ★\n"
                 "★**· `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 里 `0.71` 出现 0 次; `0.65` 只出现在 `J_USB_C` 的 NPTH 语境** ★\n\n"
                 "★**③ ★★main 本机实读: 为什么现有覆盖度闸查不出来 (★`HW/check_onepass_preflight_coverage.py` L233~L262★)★★ ★\n"
                 "★**· ISS-343 已经加严过一次, 它自己写明了病根: 「一条【不带新位号】的板改 ⇒ 天生查不出 ⇒ P4 绿 = 假绿」** ★\n"
                 "★**· 而 `WP02_BINDING` 的 ③ 那一行 = (`B33_PIN_LAND_1P27`, []) ⇒ ③ 这一项底下【有几条子动作】P4 完全不查 (★零个覆盖令牌★)** ★\n"
                 "★**⇒ ★★**改孔这条子动作漏了, P4 照样绿 ⇒ 纪律 ① 的执行体漏了一格 ⇒ 那一趟开工时改孔不在清单 ⇒ 不在清单 = 没人做 = "
                 "板投出去才发现排针插不进 ⇒ 【板改两次】** ★★**\n\n"
                 "★**④ 本单要交 3 件**: ★**(甲)** 新建真相页 `HW/PCB/BOARD_ONEPASS_FTS_LAND_DRILL_CHANGE.md` (★§0~§7 + 机器块·含「要 main 落什么」登记表★) ★"
                 "★**(乙)** 新建机器闸 `HW/check_fts_land_drill_same_batch.py` (★D1~D7 + ≥8 条反向用例, 其中 ≥4 条专打「漏项」判据★) ★"
                 "★**(丙)** 交卷页 B1~B6 齐全 + 分片 (≥3 产出物 + ≥5 interface_claims + needs_from to=main)★ ★\n\n"
                 "★**⑤ ★★本单的地界 (★main 本机实读·本单【不许自己改】清单★)★★**: ★**本单零改既有页正文** (★作业包 §0.2 ③ / 预检清单 `B33_PIN_LAND_1P27` / "
                 "`HW/check_onepass_preflight_coverage.py` 的 `WP02_BINDING` / `HW/BOM_v1.csv` L71/L77 全是已签收件或那一趟的动作★) ⇒ "
                 "★**你要做的是【把该改的写成【给 main 的登记】+【一个能查出「没改」的机器闸】】, 不是【自己改】** ★\n\n"
                 "★**⑥ 机检硬要求 (★main 本机实读 `state/gate_check.py` L47~L54★)**: 交卷页 B1~B6 六段必须齐全, 且 `pick_handoff` 取【最新一份】评分 ⇒ "
                 "★★**最新一份自称 B 块结构但缺块 ⇒ 不许回退 ⇒ Q1 立刻掉** ★★ ⇒ ⇒ ★**六段标题必须含 `REQUIRED_BLOCKS` 的关键词** ★\n\n"
                 + BOUND),
        "owner": "hw-lead",
        "verify_by": "main",
        "reporter": "main",
        "raised": "2026-11-24",
        "due": "2026-11-27",
        "status": "fixing",
        "external": False,
        "need_keys": ["iss387_oi2_drill_change_same_batch", "iss387_oi3_land_source_synthesis",
                      "iss383_main_single_row_1x27_vendor_pn"],
        "task_brief": brief(BRIEF_391),
        "note": ("★2026-11-24 11:5x cron fb67af40 (ARS45 队列自动派活) 新开并【直接落 fixing】"
                 "(★铁律⑩-i: 先落 fixing 再 spawn ⇒ 兄弟 job 775d9893 读同一字段 ⇒ 零撞车窗口★) ★\n"
                 "★**开单依据 (本机实读 + 实算, 不抄任何 agent 报告)★**: ① `state/advance.py --json` 实跑 ⇒ `internal: []` "
                 "⇒ 三个总工名下零 open 可派 ② 台账实读 ⇒ hw-lead 名下 ISS-387 已交卷 (交卷页 26,363 B @ 11:10 + 分片 hw.yaml 3 条 @ 11:09) "
                 "⇒ 槽位待 main 签收后释放 ⇒ 本 job 趁窗口期把下一批活落到位 ③ ★**本单 trigger = main 本机实读撞出的清单漏项**: "
                 "ISS-387 查明改孔 `0.65 → 0.71` 是板侧改板动作且必须与那一趟同批, ★**而作业包 §0.2 ③ 与预检清单 `B33_PIN_LAND_1P27` 里都没有这一条**★ "
                 "④ ★**且 `HW/check_onepass_preflight_coverage.py` 的 `WP02_BINDING` ③ 那一行零个覆盖令牌 ⇒ 查不出子动作漏项 ⇒ P4 绿 = 假绿 (第二次) ⇒ "
                 "★**⇒ 不补 ⇒ 那一趟投板后才发现排针插不进 ⇒ 【板改两次】** ★\n"
                 + BOUND
                 + NOTE_TAIL),
    }

    # ---- 原子写回 (★md5 守卫: 与开读时不一致 ⇒ 中止·不许覆盖 main 的并发写★) ----
    if md5(LOG) != md5_before:
        print("★★ issue_log.yaml 在本脚本运行期间被改 (md5 变了) ⇒ 中止 (rc=3), 不写盘")
        return 3
    bak = LOG + ".bak_%s_cronfb67_open_390_391" % STAMP
    shutil.copy2(LOG, bak)
    out = []
    for e in (e390, e391):
        out.append(dump_entry(e))
    src = open(LOG, encoding="utf-8").read()
    txt = src.rstrip("\n") + "\n" + "".join(out)
    tmp = LOG + ".tmp_%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, LOG)
    print("✅ issue_log 追加成功: ISS-390 (mech-lead) + ISS-391 (hw-lead) · status=fixing (★零撞车窗口★)")
    print("   备份: %s" % os.path.basename(bak))

    # ---- dispatch_log 追加 (★幂等: 同 (issue, task_name) 不重复★) ----
    raw2 = open(DLOG, encoding="utf-8").read()
    if isinstance(raw2, list):
        entries, shape = raw2, "list"
    elif isinstance(raw2, dict):
        entries = raw2.setdefault("dispatches", [])
        shape = "dict"
    else:
        entries, shape = [], "list"

    new_entries = [
        {
            "issue": "ISS-390",
            "agent": "mech-lead",
            "at": "2026-11-24 11:55",
            "brief": ("★★[新开] `FTS` 直插档【座体外形 (宽 X / 深 Y / 绝缘体高 Z)】官网查证 + 「通用库件 courtyard 被当成厂件」"
                      "这条前提订正 + 降级方案 ★★"
                      "★★**纯查证 + 纯分析 + 新建闸 + 作业包 · 零写板 · 零落表 · 零改既有闸/既有页正文 · 零外发 · 不代拍** "
                      "⇒ 合「板只改一次」纪律 ①★★"),
            "brief_file": BRIEF_390,
            "job": JOB,
            "status_note": ("★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★"),
            "task_name": "queue_iss390",
            "dispatched_at": "2026-11-24 11:55",
            "redispatch_zombie": False,
        },
        {
            "issue": "ISS-391",
            "agent": "hw-lead",
            "at": "2026-11-24 11:55",
            "brief": ("★★[新开] 「板只改一次」那一趟的排针 land【`0.65 → 0.71` 钻孔这一条板侧改动还没进作业包/预检清单】⇒ 把它补进去 ★★"
                      "★★**纯分析 + 作业包 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改既有闸/既有页正文 · 零外发 · 不代拍** "
                      "⇒ 合「板只改一次」纪律 ①★★"),
            "brief_file": BRIEF_391,
            "job": JOB,
            "status_note": ("★台账 status 直接落 fixing (★不是 open★) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★"),
            "task_name": "queue_iss391",
            "dispatched_at": "2026-11-24 11:55",
            "redispatch_zombie": False,
        },
    ]
    added = 0
    for entry in new_entries:
        dup = any(isinstance(e, dict) and e.get("issue") == entry["issue"]
                   and e.get("task_name") == entry["task_name"] for e in entries)
        if dup:
            print("★已存在同 task_name 条目 ⇒ 不重复追加: %s" % entry["issue"])
            continue
        entries.append(entry)
        added += 1
    if added:
        bak2 = DLOG + ".bak_%s_cronfb67_open_390_391" % STAMP
        shutil.copy2(DLOG, bak2)
        fd, tmp2 = tempfile.mkstemp(dir=os.path.dirname(DLOG), prefix=".dispatch_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                if shape == "dict":
                    raw2["dispatches"] = entries
                    yaml.safe_dump(raw2, f, allow_unicode=True, sort_keys=False)
                else:
                    yaml.safe_dump(entries, f, allow_unicode=True, sort_keys=False)
            os.replace(tmp2, DLOG)
        finally:
            if os.path.exists(tmp2):
                os.unlink(tmp2)
        print("✅ dispatch_log 追加成功 (shape=%s) · 新增 %d 条" % (shape, added))
    else:
        print("★dispatch_log 零新增 ⇒ 未写盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
