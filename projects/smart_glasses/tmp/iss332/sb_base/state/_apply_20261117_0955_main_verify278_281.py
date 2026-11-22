#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (moli) 2026-11-17 09:5x · job 775d9893「ARS45 继续执行后继计划」
★ISS-278 (mech-lead) / ISS-281 (hw-lead) 独立复验 ⇒ 落 verified★
★main 自己实跑 2 道闸 + 2 个 selftest + 亲自 md5 受保护 5 件 + 亲自查交卷单 + 亲自读分片 claim★
★**只动 1 个文件: state/issue_log.yaml**★
★**不碰真源 / 分片 / 板 / 网表 / 脚表 / BOM / 任何既有门禁脚本**★
"""
import json
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261117_0955_main_verify278_281"
TODAY = "2026-11-17"


def q(v) -> str:
    return json.dumps(v, ensure_ascii=False)


VERIFY_278 = {
    "fix_ref": ("HANDOFF/2026-11-17_mech-lead_ISS278_MECH侧板侧输入收口.md (30 149 B) · "
                "MECH/BOARD_ONEPASS_MECH_SYNC.md (38 271 B) · "
                "MECH/check_onepass_mech_sync.py (31 303 B)"),
    "verify_note": (
        "★**main 2026-11-17 09:2x~09:4x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
        "① `MECH/check_onepass_mech_sync.py` ⇒ **rc=0** ★实测摘要: M1 坐标系帧标签 + 机器块 frame 字段 · "
        "M2 两条开口 (PORT_OPEN_DEBUG / PORT_OPEN_UART) 各自不压 SoM 座 + 条目齐全 · "
        "M3 三档 h 值判据 · M4 每条 criterion 的判据脚本都在盘上 (MECH-BODY-H / MECH-LED-G / MECH-LED-GD-NET / "
        "MECH-CONN-PARAMS / MECH-LED-BRIGHT-G5 / MECH-LED-HOLE 共 7 个脚本路径全在盘) · "
        "M5 受保护 5 件 md5 **逐字节相同** (板 `611b869e13518c3c023fb178f91a0075` · `.kicad_pro` `3e504d2be83152e337949723e909be1b` · "
        "网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · BOM `94642d07a69e8d60dd2af57f69b93607`) "
        "⇒ **【绿】M1~M5 全过** ★"
        "② `--selftest` ⇒ **rc=0 (反向 8/8 全抓到)** ★逐条: ① 改检修口矩形一个角 ⇒ M2 红 ② 把两条开口合并成一个 ⇒ M2/M3 红 "
        "③ 抽掉正文表头的帧标签 ⇒ M1 红 ④ 抽掉机器块里的 frame 字段 ⇒ M1 红 ⑤ 把 h 三档之一改到不合理 (4.00⇒40.00) ⇒ M3 红 "
        "⑥ 把判据命令改成不存在的脚本 ⇒ M4 红 ⑦ 改受保护件 (HW/BOM_v1.csv) ⇒ M5 红 ⑧ 自检跑完真件 5 件 md5 仍逐字节不变 "
        "★(★每条都实测了 md5 确实变了 + 红判据命中正确, 不是「假红」★)★ "
        "③ ★**受保护 5 件 md5 = main 亲自跑 md5sum 逐字节核对 (跑在闸之前 + 闸之后各一次, 两次都是 5/5 相同)★** ⇒ **板没被碰过** "
        "④ 交卷单 `HANDOFF/2026-11-17_mech-lead_ISS278_MECH侧板侧输入收口.md` (30 149 B) **B1~B6 六块齐全** "
        "⑤ `state/fragments/mech.yaml` 内 **iss278 claim + 3 artifact (MECH/BOARD_ONEPASS_MECH_SYNC.md / "
        "MECH/check_onepass_mech_sync.py / 交卷单) 在位** + need `iss278_mech_to_hw_board_inputs` 已开给 main ⇒ **交卷完整** ⇒ 落 verified ★ "
        "★**本单的价值 (★记一笔★)**: 「板只改一次」那一趟的三条腿 (HW=ISS-277 / MECH=ISS-278 / SW=ISS-279) ⇒ **至此齐** ⇒ "
        "★**板侧输入 (HW / MECH / SW 三域) 全部收成【规格 + 机器闸】⇒ ⇒ 「那一趟」开工前, 三个域各自都有闸替自己说话**★"
    ),
}

VERIFY_281 = {
    "fix_ref": ("HANDOFF/2026-11-17_hw-lead_ISS281_S10投产包清单落地.md (39 591 B) · "
                "HW/PCB/BOARD_ONEPASS_S10_MANIFEST_SPEC.md (20 592 B) · "
                "HW/check_onepass_s10_manifest.py (28 531 B)"),
    "verify_note": (
        "★**main 2026-11-17 09:2x~09:4x 独立复验 (★自己实跑, 不抄交卷报告★)**: "
        "① `HW/check_onepass_s10_manifest.py` (★主模式★) ⇒ **rc=0** ★实测摘要: M1 **❌ 红** = "
        "「★**清单文件不在盘上: HW/PCB/production/MANIFEST.md5 ⇒ S10 那一趟还没生成清单 (★这正是 ISS-281 的病灶本身★)**★」; "
        "M2/M3/M4 = ⏭ 不可判定 (★依赖 M1★) ⇒ ★**★这个红是【正确行为】, 不是闸坏了★: ISS-281 的交付物是【格式契约 + 闸】, "
        "而【清单本身】要等 S10 那一趟 (`state/gen_production_pack.sh`) 才生成 ⇒ ⇒ 闸必须【现在红, S10 跑完才转绿】, "
        "否则闸就是【提前放行】★** ⇒ ★**main 实测确认: 闸自己明说「当前盘面就是 ISS-281 的病灶本身」★** "
        "② `--selftest` ⇒ **rc=0 (用例 10 条 = ★判红 9 条 + 正向对照 1 条★ · 全部符合)** ★逐条: "
        "① 清单里板 md5 改错一位 ⇒ M2 红 ② 清单里某个文件的 md5 改错一位 ⇒ M3 红 ③ 从投产包里删一个文件 ⇒ M3,M4 红 "
        "④ 往投产包里加一个清单没列的文件 ⇒ M4 红 ⑤ 清单少头字段 BOARD_MD5 / GENERATED_AT / FILE_COUNT ⇒ M1 红 (三条) "
        "⑥ 正向对照 (清单与盘面完全一致) ⇒ rc=0 无红判据 ⑦ 历史对照 (盘上没有清单) ⇒ M1 红 "
        "⑧ **板在清单生成之后又改了 (旧货冒充新货) ⇒ M2 红** ★(★这一条正是 ISS-280 D6「留证绑定」要抓的病, 本闸抓得住★)★ "
        "★(★沙盒根已清理★)★ "
        "③ ★**受保护 5 件 md5 = main 亲自跑 md5sum 逐字节核对**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17`) · "
        "`.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `e06c1dd633566aa44732762c2ff99d1c` · 脚表 `287e7861a0d1007748d92d9fbecdd490` · "
        "BOM `94642d07a69e8d60dd2af57f69b93607` ⇒ **5/5 与基线逐字节相同** "
        "④ 交卷单 `HANDOFF/2026-11-17_hw-lead_ISS281_S10投产包清单落地.md` (39 591 B) **B1~B6 六块齐全** "
        "⑤ `state/fragments/hw.yaml` 内 **iss281 claim + 3 artifact (S10_MANIFEST_SPEC / check_onepass_s10_manifest.py / 交卷单) 在位** "
        "+ need `iss281_s10_generator_hook` 已开给 main ⇒ **交卷完整** ⇒ 落 verified ★ "
        "★**本单的价值 (★记一笔★)**: 「板只改一次」那条铁律的【最后一环】补上了 ⇒ ★**S10 跑完之后, 投产包与板之间有了"
        "【内容级绑定】(清单里的 BOARD_MD5 必须 == 盘上板 md5)⇒ ⇒ 板改一次, 旧 Gerber 想靠 mtime 刷新冒充新货 ⇒ 【当场红】**★ "
        "★**★本单【不是】板改完了才需要 ⇒ 它是【板改之前就要把闸立好】, 否则板一改, 旧产物就能蒙混过关** ★"
    ),
}


def main() -> int:
    shutil.copy2(LOG, BAK)
    lines = open(LOG, encoding="utf-8").read().split("\n")

    def bounds(iid):
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

    for iid, spec in (("ISS-278", VERIFY_278), ("ISS-281", VERIFY_281)):
        s, e = bounds(iid)
        if s is None:
            print("❌ 找不到 %s" % iid)
            return 2
        blk = lines[s:e]
        hit = {"status": False, "fix_ref": False, "vr": False, "vd": False, "vb": False}
        for j, ln in enumerate(blk):
            st = ln.strip()
            if st in ('status: fixing', 'status: "fixing"'):
                blk[j] = '  status: "verified"'
                hit["status"] = True
            elif st.startswith("fix_ref:") and ("null" in st or st.split("fix_ref:", 1)[1].strip() == ""):
                blk[j] = "  fix_ref: %s" % q(spec["fix_ref"])
                hit["fix_ref"] = True
            elif st.startswith("verify_result:") and "null" in st:
                blk[j] = '  verify_result: "pass"'
                hit["vr"] = True
            elif st.startswith("verify_date:") and "null" in st:
                blk[j] = "  verify_date: %s" % q(TODAY)
                hit["vd"] = True
            elif st.startswith("verify_by:") and ("null" in st or st.split("verify_by:", 1)[1].strip() in ("", '""')):
                blk[j] = '  verify_by: "main"'
                hit["vb"] = True
        while blk and blk[-1].strip() == "":
            blk.pop()
        blk.append("  verify_note: %s" % q(spec["verify_note"]))
        lines[s:e] = blk
        print("  %s 命中: %s" % (iid, hit))

    open(LOG, "w", encoding="utf-8").write("\n".join(lines))

    # ---------- 自检: 全量复核 ----------
    d2 = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
    ids = {it["id"]: it for it in d2["issues"]}
    print("  问题单总数 = %d" % len(d2["issues"]))
    for iid in ("ISS-277", "ISS-278", "ISS-279", "ISS-280", "ISS-281", "ISS-282"):
        it = ids[iid]
        print("  %s -> %-9s owner=%-9s verify_by=%-6s verify_result=%-5s note=%d字节" % (
            iid, it["status"], it.get("owner"), it.get("verify_by"), it.get("verify_result"),
            len(it.get("verify_note") or "")))
    # 其它条目没被动过: 逐条比 status/verify_result 与 BAK
    d0 = yaml.safe_load(open(BAK, encoding="utf-8")) or {}
    b0 = {it["id"]: it for it in d0["issues"]}
    drift = []
    for iid, it in ids.items():
        b = b0.get(iid)
        if b is None:
            drift.append((iid, "新增"))
            continue
        for k in ("status", "owner", "verify_result", "verify_date", "verify_by", "fix_ref"):
            if (it.get(k) or "") != (b.get(k) or ""):
                drift.append((iid, k))
    print("  与 BAK 比对的字段漂移 = %d 处 %s" % (len(drift), drift))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
