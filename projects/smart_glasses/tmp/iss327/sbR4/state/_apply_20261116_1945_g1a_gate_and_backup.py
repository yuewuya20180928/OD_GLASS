#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261116_1945_g1a_gate_and_backup.py —— ★main 19:4x 记账 (★G1a 闸 + 原理图评审包备份★)

★**本脚本只做两件事** ★
  ① 在 `state/issue_log.yaml` 登记 ★**ISS-252** (★owner=main · status=verified · 依据=main 本机实跑★)
  ② ★**不改任何真源** (板/网表/脚表/BOM/`.kicad_pro` 一个字节都没动) ★

★**为什么登记** ★: 项目的规矩是「先落盘再干活」+ 「每件产出都要在台账里可追踪」⇒
★**新闸 `state/check_stage_g1a.py` 与给老板的评审包备份, 都得有台账痕迹** ★

★**写法**: 照抄 19:15 那次记账脚本的规矩 (★yaml.safe_dump 整体重写 + 原子替换 + 先备份★)
"""
import hashlib
import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
TODAY = "2026-11-16"


def md5(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def main() -> int:
    if not os.path.exists(LOG):
        print("✗ issue_log 不存在")
        return 2
    with open(LOG, encoding="utf-8") as f:
        log = yaml.safe_load(f)
    issues = log.get("issues") if isinstance(log, dict) else log
    if issues is None:
        print("✗ issue_log 结构异常")
        return 2
    by_id = {it.get("id"): it for it in issues}

    iid = "ISS-252"
    if iid in by_id:
        print(f"⚠ {iid} 已存在 ⇒ 幂等跳过")
        return 0

    gate = os.path.join(HERE, "check_stage_g1a.py")
    dc = os.path.join(HERE, "daily_check.py")
    note = (
        "★★**main 2026-11-16 19:4x 落账 (★依据 = main 本机实跑, 不是抄交卷报告★)**★★\n"
        "★**① 新闸 `state/check_stage_g1a.py` (★G1a「原理图定稿」独立闸★)** ⇒ md5 `" + md5(gate) + "`\n"
        "  ★**起因**: 老板 11-16 问「原理图和 PCB 不是同一个概念, 原理图是不是已经绘制好了?」⇒ 揭穿 "
        "`stage_gate.py` 的 G1 一关卡两件事 + 老板 11-11 10:07「PCB 布线类排队不派」⇒ ★**结构性死锁: "
        "原理图画完了 G1 也永远红**★ ⇒ ⇒ **把 G1a 单独切出来**\n"
        "  ★**8 条判据**: ERC=0 / 脚数 K=0 / loadable / 落表已清零(★`--expect-resolved` 翻面口径★) / "
        "网表尺子 / 脚表尺子 / 选型已落表(BOM 必装件无「[待选型]」) / 关机语义+负载开关已决(ISS-097+ISS-172)\n"
        "  ★**自测 11/11 rc=0** (★6 条命令类判据逐条证明「它真在被读」+ BOM 篡改红 + 台账篡改红 + "
        "临时 root 判定与真盘一致 + 修好后变绿 + 连跑两次一致★)\n"
        "  ★**本机实跑现状: ❌ 还差 3 条 = G1a-4(落表未清零 18 条) + G1a-7(必装件仍写「[待选型]」14 件) + "
        "G1a-8(ISS-097=fixed 未 verified)** ⇒ ★**原理图【画】已画完, 差的是「值」与「拍板」** ★\n"
        "★**② 原理图评审包备份 (★给老板翻看★)** ⇒ `/home/yuewuya/Public/work/ars45_schematic_2026-11-16/`\n"
        "  ★**31 个文件**: 原理图 PDF (11 页 A2, 19:33) + sch_src 12 个源文件 + sch_svg 11 个 + "
        "网表/脚表/BOM CSV + KiCad netlist + `README_评审指引.md` (★含「第一遍只看 3 条」★) + md5 清单\n"
        "  ★**sch_src 与项目真源逐字节一致** (★已逐文件 md5 对拍 OK★)\n"
        "★**③ `state/daily_check.py` 本轮新增一行「原理图 G1a」** ⇒ md5 `8a6c649b082a41b60752c95b33bf570d`\n"
        "  ★**诚实缺口**: ★**改前 md5 未留档 (本轮动它之前没取基线) ⇒ 记为已知缺口, 后续以当前 md5 为基线** ★\n"
        "  ⇒ ★**G1a 的三条红是【待拍/待落表】, 不是【有人失职】⇒ 打进巡检行但★不记进 problems★ "
        "(★不然每天都成新异常 = 噪音★) ★\n"
        "★**边界**: 零落表 · 零外发 · 零实物 · 板/网表/脚表/BOM/`.kicad_pro` 一个字节没动 · "
        "不碰别人分片 · 不替老板拍板 ★\n"
        "★**下一步**: ★**老板把 A1/A2/A3 三条拍了 ⇒ G1a-4 能退 13+1 条** ⇒ ★**再落 OPN ⇒ G1a-7 退 ⇒ "
        "★**拍 A4/Q1~Q5 ⇒ G1a-8 绿** ⇒ ★**G1a 全绿 = 原理图侧定稿** ★"
    )

    issues.append({
        "id": iid,
        "title": ("★★[主线内·原理图侧·阶段门口径·内部活] ★★**G1「原理图定稿 / PCB 定稿」拆关** ⇒ "
                  "新闸 `state/check_stage_g1a.py` (★8 条判据 + 自测 11/11★) ⇒ ★**原理图侧今天就能独立判绿/判红, "
                  "不再被 PCB 的 unconnected=45 拖住** ★ + ★**原理图评审包备份到 `/home/yuewuya/Public/work/` (给老板翻看)** ★"),
        "severity": "medium",
        "owner": "main",
        "status": "verified",
        "due": "2026-11-18",
        "source_blocker": "G1-口径死锁",
        "verify_result": "pass",
        "verify_by": "main",
        "verify_date": TODAY,
        "note": note,
    })
    print(f"＋ 新开 {iid} (owner=main · verified)")

    bak = LOG + ".bak_20261116_1945_g1a"
    shutil.copy2(LOG, bak)
    tmp = LOG + ".tmp_20261116_1945"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=100000)
    os.replace(tmp, LOG)
    print(f"✔ 已写盘 (备份: {os.path.basename(bak)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
