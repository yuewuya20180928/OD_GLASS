#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 09:5x · job 775d9893「ARS45 继续执行后继计划」
★新开 ISS-282 (hw-lead) = 「板只改一次」的【`FSIN_OUT` 根因订正 + 布线前置闸】★
★**依据 = 决策页 §A-补13 明确把「`FSIN_OUT` 逃逸方向」派给 main 自查, main 本轮自查完 = 根因写错了★**
★**只动 1 个文件: state/issue_log.yaml**★
★**不碰真源 / 分片 / 板 / 网表 / 脚表 / BOM / 任何既有门禁脚本**★
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0950_open_iss282"
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-282_hw_fsin_rootcause_correction.md")
TODAY = "2026-11-17"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


TITLE = ("★★[★主线·PCB 线·纯规格+作业包追加式订正+机器闸类] ★★「板只改一次」的【`FSIN_OUT` 根因订正 + 布线前置闸】★★ "
         "⇒ ★**决策页 §A-补13 把「`FSIN_OUT` 逃逸方向」派给 main 自查, main 本轮自查完 = 盘上写着的根因【是错的】** ★ "
         "⇒ ★**盘上写的是「疑似逃逸方向 bug (两者竖直对齐, 逃逸口互挡)」(作业包 §6.2 S8 行 + ISS-265 §6 桶B-26)★** "
         "⇒ ★**main 本机实跑三条独立实测全部指向【布线排队顺序】: ① 两个焊盘到最近异网焊盘边缘 1.1500/1.3528mm ≫ 0.45 ⇒ 根本不走 `escape_stub()` ⇒ 「逃逸方向」不成立 ② 逐网忽略法: 只忽略 `VDD_3V3_IO` ⇒ A→B 直线净距 0.439 ≥ 0.395 ⇒ PASS ⇒ 唯一挡路者是 `VDD_3V3_IO` (它在 `POWER_NETS` 里 = 第 2 步布, 而 `FSIN_OUT` 第 4 步才布 ⇒ 后挑走廊只剩窄缝) ③ 沙盒 DRC: pristine 0违规/45未连 ⇒ 手工布线后连上 (45→44) 但 18 违规 ⇒ 手工补线不是出路** ★ "
         "⇒ ★**且该根因【早就被实测解过】: `LANE_CONFLICT_WORKLIST.md` L260 实测 `PCB_PRIORITY_NETS` 让 `FSIN_OUT` 一次就通 ★★L=3.0mm = 那条直线★★ (路由器源码 L4790 的用法示例里就写着 `FSIN_OUT`)★** "
         "⇒ ★**⇒ 直接后果: `FSIN_OUT` 从【会改板/要老板拍】那一类里划掉 ⇒ 不进「A 类步」⇒ 老板那一趟要拍的东西【少一条】(好消息) ⇒ 但它没消失, 挪到【布线臂 env 配置】⇒ 「布线 45→0」那一趟仍必须把它布通** ★ "
         "⇒ ★**⇒ 本单 = 订正根因 + 追加式订正作业包 + 一道可复现的机器闸 (零写板 · 零跑布线臂)★** ★")

DESC = """★main 2026-11-17 09:2x~09:5x 本机实读 + 实跑 (不抄交卷报告, 不抄历史臂报告)★
★**① 盘上写着的根因是错的** ★: `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §6.2 S8 行 (L387) 写「★**疑似逃逸方向 bug, 不是布局问题 ⇒ 找错方向会白跑一轮路由**★」; `HANDOFF/2026-11-17_hw-lead_ISS265_...md` §6 桶B-26 (L343) 写得更具体「★**两者竖直对齐, 逃逸口互挡**★ ⇒ 要查 `_emit_path` 逃逸方向规则」⇒ ★**两条都把锅甩给「逃逸方向」★** ★
★**② main 实测推翻「逃逸方向」** ★: 路由器 `escape_stub()` 只在「到最近异网焊盘边缘 < 0.45mm」时才被调用 (`state/gen_pcb_routing.py` L2061 起, `if self._nearest_other_pad(net, cx, cy) >= 0.45: return None`); main 实跑量到 `R_SER_FSIN.1`(93.300,46.600) 距离 = ★**1.1500mm**★ (最近 `R_SER_FSIN.2`/FSIN), `TP_FSIN.1`(93.500,49.600) 距离 = ★**1.3528mm**★ (最近 `CONN_LIGHT.30`/LIGHT_5V) ⇒ ★★**两者都 ≫ 0.45 ⇒ 这两个焊盘根本不进 `escape_stub()` 分支 ⇒ 「逃逸方向 bug」不成立★★** ★
★**③ main 实测定位真因 = 布线排队顺序** ★: 净距口径 0.125+0.20+0.07 = ★**0.395mm**★ (照 `ROUTING_REPORT.md` §1); main 跑「A→B 直线最小净距, 每次只忽略一个网」: ★**只忽略 `VDD_3V3_IO` ⇒ 0.439 ≥ 0.395 ⇒ PASS**★, 其余任何单网都 FAIL (0.118 或 -0.118) ⇒ ★**唯一挡路者 = `VDD_3V3_IO`**★; 而 `VDD_3V3_IO` 在 `POWER_NETS` 列表里 (L4657) ⇒ 路由器第 2 步就把它布掉, `FSIN_OUT` 这种普通信号网第 4 步才布 ⇒ ★**后挑走廊的只剩那条被压掉的窄缝**★ ★
★**④ 该根因早就被实测解过 (只是没跟本单对上)** ★: `state/LANE_CONFLICT_WORKLIST.md` L260 实测 `PCB_PRIORITY_NETS` 让 19 个网提前布, ★**其中 `FSIN_OUT` 一次就通, L=3.0mm**★ ⇒ ★★**3.0mm 恰好就是 A→B 那条直线 (main 实测 3.007mm) ⇒ ⇒ 「提前布」时它就是沿直线走通的★★**★; 路由器源码 L4790 的用法示例里就直接写着 `PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;I2C_A_SCL"` ★
★**⑤ main 沙盒交叉验证 (真盘零触碰)** ★: `tmp/` 副本手工布一条 (F.Cu→过孔→In4.Cu→过孔→F.Cu) 跑真 `kicad-cli pcb drc`: pristine = ★**0 违规 / 45 未连**★, 手工布线后 = ★**18 违规 / 44 未连**★ ⇒ ★**连是能连的, 但手工布踩净距 ⇒ 【手工补线】不是出路, 【换排队顺序】才是**★; 再跑 4 个信号层 (F.Cu/In2.Cu/In4.Cu/In6.Cu) 只读 A\* ⇒ NO ROUTE ⇒ ★**但那是【假阴性】: A\* 是在现状铜已布好的板面上找路, 而现状板上 `VDD_3V3_IO` 的铜已把直线压死 ⇒ 恰恰印证 ③**★ ★
★**⑥ 对「板只改一次」那一趟的直接含义 (三条)** ★: (a) `FSIN_OUT` 从【会改板/要老板拍】那一类里划掉 ⇒ 不进「A 类步」⇒ ★**老板那一趟要拍的东西少一条**★ (b) 它没消失, 挪到【布线臂 env 配置】⇒ ★**「布线 45→0」那一趟仍必须把它布通, 而布通它不需要改板 ⇒ 「板只改一次」铁律不受影响**★ (c) ★**`LANE_CONFLICT_WORKLIST.md` §8 实测「走廊是零和的」⇒ 优先布给了 `FSIN_OUT`, 被挤掉的可能是差分主干 (实测 v76p1 臂 `CSI_D0_CK_P_SRC/N_SRC` 成死腿 ⇒ 整板 unc 46→47) ⇒ 【给 `FSIN_OUT` 提前不会自动让整板 unc 变小】⇒ 那一趟的「unc→0」判据必须【按名单制】看 ⇒ ★**这一条是判据口径问题, 归 main, 不许代拍**★ ★
★**⑦ 为什么现在能派** ★: hw-lead 与 mech-lead 名下本轮 in-flight 均已交卷 (ISS-278 / ISS-281 两份交卷单已在盘, main 已实跑复验: `MECH/check_onepass_mech_sync.py` rc=0 + `--selftest` 8/8 全抓到, `HW/check_onepass_s10_manifest.py --selftest` 10/10 (判红9+正向1), 受保护 5 件 md5 逐字节不变) ⇒ ★**hw-lead 名下真空** ★ ★
★**⑧ 与别的单的分界** ★: 本单只【新建 2 个文件 + 作业包追加 1 行】; ★**不许跑任何布线臂 / 生成器 / 投产包** ★ (★跑一次 = 板全变 = 板 md5 第二次变 = 「板只改一次」破功★); ★**ISS-278 / ISS-281 的交付物一个字不许动** ★ ★"""

NOTE = ("2026-11-17 09:5x (cron 775d9893 继续执行后继计划) 新开 ★**依据 = 决策页 §A-补13 (2026-11-17 08:5x) 明确把「`FSIN_OUT` 逃逸方向」判为"
        "「工程项不是决策项 ⇒ 由 main 自查, 查到需要老板拍架构再上页」★ ⇒ ★**main 本轮自查完 = 盘上写着的根因【是错的】⇒ 必须订正, 否则"
        "「板只改一次」那一趟会照着错的根因排期** ★\n"
        "⇒ ★**任务书 `state/dispatch_briefs/ISS-282_hw_fsin_rootcause_correction.md`** ★\n"
        "★**类别**: 内部活 · PCB 线 · 纯规格 + 作业包追加式订正 + 机器闸类 ⇒ ★**零写板 · 零跑布线臂 · 零落表 · 零改既有判据阈值** ★\n"
        "★**★本单【零新增待拍项】⇒ 不用问老板, hw-lead 自己做完交卷, main 独立复验后落 verified** ★\n"
        "★**★但 §③ 第 3 条那个「unc→0 判据该按名单制还是看总数」= 判据口径问题 ⇒ 归 main 排期 (★或另开一单★), hw-lead 只登记 need, 不许代拍** ★\n"
        "★**注意**: 本单交付的 D2/D3 判据要【能复现 main 那三条实测】, 不许把数字写死成常量 ⇒ 闸必须自己实跑复算 ⇒ 防止「订正页变成第二份过期文档」 ★")

FIELDS = [
    ("id", "ISS-282"),
    ("title", TITLE),
    ("severity", "high"),
    ("source_blocker", None),
    ("source_agent", "main"),
    ("desc", DESC),
    ("owner", "hw-lead"),
    ("reporter", "main"),
    ("raised", TODAY),
    ("due", "2026-11-20"),
    ("status", "open"),
    ("external", False),
    ("need_keys", []),
    ("fix_ref", None),
    ("verify_by", None),
    ("verify_result", None),
    ("verify_date", None),
    ("note", NOTE),
    ("dispatched_at", TODAY),
]


def main() -> int:
    brief = open(BRIEF, encoding="utf-8").read()

    shutil.copy2(LOG, BAK)
    lines = open(LOG, encoding="utf-8").read().split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()

    block = []
    for k, v in FIELDS:
        if k == "id":
            block.append("- id: ISS-282")
        elif v is None:
            block.append("  %s: null" % k)
        elif isinstance(v, bool):
            block.append("  %s: %s" % (k, "true" if v else "false"))
        elif isinstance(v, list):
            block.append("  %s: []" % k)
        else:
            block.append("  %s: %s" % (k, q(v)))
    block.append("  task_brief: %s" % q(brief))

    lines.extend(block)
    open(LOG, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    # ---------- 自检 ----------
    d = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    ids = {it["id"]: it for it in d["issues"]}
    it = ids["ISS-282"]
    print("  问题单总数 = %d" % len(d["issues"]))
    print("  ISS-282 status=%s owner=%s severity=%s due=%s external=%s"
          % (it["status"], it["owner"], it["severity"], it["due"], it["external"]))
    print("  task_brief 字节 = %d (源文件 %d, 一致=%s)"
          % (len(it["task_brief"]), len(brief), it["task_brief"] == brief))
    print("  verify_by=%s verify_result=%s (★必须都不是 hw-lead★)" % (it["verify_by"], it["verify_result"]))
    print("  其它条目状态没变 =", sum(1 for i in d["issues"] if i["id"] != "ISS-282"))
    for i in d["issues"]:
        if i["id"] in ("ISS-278", "ISS-281"):
            print("  %s status=%s (未被本脚本改动)" % (i["id"], i["status"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
