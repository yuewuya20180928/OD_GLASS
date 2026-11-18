#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_frag_write.py —— ISS-327 · 分片原子写 (★走 state/frag_write.py·禁 open(p,"w")★)

★做三件事★:
  ① 修 cont1 臂用 `--add-*` 传整串时留下的【畸形条目】(★key/path 字段里塞了整串 "k=v k=v"★
     ⇒ 合并器读不到真 key/path·★数据静默降级★)
  ② 追加本单 (cont2) 的 artifact / need / claim (★键名沿用 cont1 已登记的键·不制造重复 need★)
  ③ status 换成 ISS-327

★原子写 = frag_write.update_fragment() 内部走 tmp + os.replace ⇒ 读者永远看到完整文件★
"""
import os
import re
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment, load_fragment   # noqa: E402

TODAY = "2026-11-18"


FIELDS = ("to", "since", "item", "value", "ref", "note", "kind", "version",
          "updated_at", "summary", "phase", "progress_pct", "health")


def parse_embedded(s):
    """★把 "key=... to=main item=..." 这种整串拆成 dict (★第一个 token 是真 key/path·
    其余字段按 【下一个已知字段名】 切★)★"""
    out = {}
    s = s.strip()
    # ① 第一个 token = 真 key / path
    head, _, rest = s.partition(" ")
    out["__head__"] = head
    rest = rest.strip()
    # ② 按已知字段名切分 (★值里允许有空格·到下一个 "<字段>=" 为止★)
    pat = re.compile(r"(?:^|\s)(%s)=" % "|".join(FIELDS))
    marks = [(m.start(), m.group(1)) for m in pat.finditer(rest)]
    for i, (pos, name) in enumerate(marks):
        vstart = pos + len(name) + 1
        vend = marks[i + 1][0] if i + 1 < len(marks) else len(rest)
        val = rest[vstart:vend].strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        if name not in out:
            out[name] = val
    return out


def fix(d):
    """★修畸形条目 (★只修 key/path 里塞了整串的那些·其余原样保留★)★"""
    nfix = 0
    for a in d.get("artifacts") or []:
        p = str(a.get("path") or "")
        if "=" in p and not p.startswith("/"):
            kv = parse_embedded(p)
            real = kv.get("__head__")
            if real and "=" not in real:
                a["path"] = real
                for f in ("kind", "version", "updated_at", "summary"):
                    if kv.get(f) and not a.get(f):
                        a[f] = kv[f]
                nfix += 1
    for lst in ("needs_from", "interface_claims", "answers", "open_questions", "risks", "blockers"):
        for it in d.get(lst) or []:
            k = str(it.get("key") or "")
            if "=" in k:
                kv = parse_embedded(k)
                if kv.get("__head__"):
                    it["key"] = kv["__head__"]
                    for f in ("to", "item", "value", "ref", "note", "since"):
                        if kv.get(f) and not it.get(f):
                            it[f] = kv[f]
                    nfix += 1
    return nfix


def main():
    print("★修前: artifacts=%d needs=%d claims=%d answers=%d"
          % tuple(len(load_fragment("sw-lead").get(k) or []) for k in
                  ("artifacts", "needs_from", "interface_claims", "answers")))

    def mutate(d):
        n = fix(d)
        print("★修畸形条目 %d 处" % n)

        arts = d.setdefault("artifacts", [])
        have = {a.get("path") for a in arts}
        new_arts = [
            {"path": "SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md", "kind": "note", "version": "1.0",
             "updated_at": TODAY,
             "summary": "★ISS-327 (2026-11-18 16:2x~16:5x cont2 收口) 「板那一趟」当天 SW 侧闸链 SOP "
                        "(§0~§9 全填·占位符 0): §1 顺序照 ISS-323 §5-1 的 7 件同批顺序逐字对齐·"
                        "§2 步 0~步 8 每步给「命令 + 期望读数 + 失败时的下一步」·"
                        "§3 改名后 10 道闸期望读数表 (六列固化版) · "
                        "§4 「重建注册表」的时机/重建前必确认 4 项/重建后只重跑第 8 道闸/登记义务 (ISS-312 N-2 同款) · "
                        "§5 回滚三档 (触发条件机器可判 + 逐字动作 + 不许做的事) · "
                        "§6 留证清单 12 项 + 「板只改了一次」的机器判据 · "
                        "§7 判据设计稿 (重建时机/DRIFT 语义是否退役/MISSING 上限三方案 + 9 条反向用例·只给设计不挂闸)"},
            {"path": "logs/iss327/02_postrename_gate_table.md", "kind": "note", "version": "1.0",
             "updated_at": TODAY,
             "summary": "★ISS-327 六臂读数表 (A0 基线 / A1 对照臂 / A2 改名后·重建前 / A3 改名后·重建后 / "
                        "A4 改名+文档同步·重建前 / A5 当天终态): 10 道闸 rc × 6 臂 + 第 8 道闸的分类读数 "
                        "(DRIFT/MISSING/OK/上限) + 逐闸归因 (哪几道红是改名引起·哪几道归第 2/3/5/6 件) + "
                        "9 条反向用例的「期望 vs 实际」+ 零写板/零落表/零改闸逐条 md5"},
            {"path": "logs/iss327/", "kind": "evidence", "version": "1.0", "updated_at": TODAY,
             "summary": "★ISS-327 机器原始输出 33 项: 01_baseline (真件 10 闸) · 12_sbCtl (对照臂) · "
                        "13_sbR0 / 16_sbR1 (改名后重建前/后) · 14_sbR3 / 18_sbR2 (文档同步两臂) · "
                        "24_four_arm_measure (四臂机器化读数) · 25_control_validity (对照有效性四条断言) · "
                        "15/17 freeze stdout (18 条 / 78 条) · 26~28_rev_RT-* (9 条反向用例前后) · "
                        "29_rev_suite_run · 32_launder_run (RT-9 洗白通道演示) · "
                        "05_restore_main_report (main 的事故回退报告)"},
            {"path": "HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md", "kind": "note",
             "version": "1.0", "updated_at": TODAY,
             "summary": "★ISS-327 交卷单 (B0~B7): 一句话结论 + 8 条带读数的结论 + 20 条验收自评 + "
                        "证据分级 + 4 条接口取值声明 + 6 条 need + 边界自证 (★含 2 处自曝: "
                        "14:25 软链写穿事故 (main 已回退·内容经 41/41 独立副本逐字节验证复原) + "
                        "本单 SOP 自己把闸带红 (按 ISS-321 纪律用反斜杠形状修掉)★)"},
        ]
        for a in new_arts:
            if a["path"] not in have:
                arts.append(a)
                print("  + artifact %s" % a["path"])

        needs = d.setdefault("needs_from", [])
        havek = {str(n.get("key")) for n in needs}
        new_needs = [
            {"key": "iss327_report_c1_c7_c8_c13_launder_faces", "to": "main", "since": TODAY,
             "item": "★ISS-327 cont2 实测: 第 8 道闸 (check_sw_ref_reachability) 的 C1 / C7 / C8 / C13 四条"
                     "规则各有一条洗白面 —— RT-5 把真隐患 TP_TEMP 改成一个【live 位号名】(U_TEMP_1) ⇒ 绿; "
                     "RT-6 改成含小写 (TP_temp) ⇒ 绿; RT-7 改成 SW_ 前缀 ⇒ 绿; RT-8 改成以 _ 结尾 ⇒ 绿。 "
                     "★四条都在【重建注册表之前就已经绿】⇒ 与 freeze 无关 ⇒ 是既有判据缺陷 (★本单只报·不改闸·改闸归 main★)。"
                     " 请拍: 要不要给这四条规则各补一条反向用例 + 收紧 (★收紧方向: 真隐患 token 必须在 BASELINE_TOKENS 里登记过才算白名单★)? "
                     "不拍的后果: 任何把真隐患改个形状的操作都能骗过闸 ⇒ 判据对「真隐患」只有形状检查没有语义检查 ⇒ 永远只能抓「拼写错」抓不到「指错对象」。"
                     " ★另附本单自踩的一条 (★同一类坑★): 方案类文档写进 SW/ 会把 ISS-318 闸带红 —— 本单 16:3x 实测"
                     "「把大写注入名原样写进 SOP」⇒ 闸判 5 条新增真隐患 (MISSING 8 > 上限 3) ⇒ 已按 ISS-321 的"
                     "『方案文档不写死位号』纪律改成反斜杠形状 ⇒ ⇒ 这条本身也是 need iss321_decide_rename_doc_notation 的实测证据。"},
        ]
        for n in new_needs:
            if n["key"] not in havek:
                needs.append(n)
                print("  + need %s" % n["key"])

        claims = d.setdefault("interface_claims", [])
        havec = {str(c.get("key")) for c in claims}
        new_claims = [
            {"key": "SW-ISS327-4",
             "value": "★「--freeze-registry 会不会把真隐患一起洗白」的逐字答案: ★对『板/网表里从来没有过的真隐患』"
                      "不会★ —— RT-1~RT-4 (TP_TEMP / TP_INT / CONN_USB 各改成自己的新形状) 实测: 重建前红 · "
                      "重建后【还是红】· 且重建出来的表【不含】它们; 结构性证明 = 8 条用例每一次重建出来的表里"
                      "【非 live 的 token】都 = 0 条 ⇒ 重建表 ⊆ live(板∪网表) ⇒ 「盘上从来没有过的 token」在物理上"
                      "不可能进表。★但闸另有 4 条洗白面 (C1 / C7 / C8 / C13)★ ⇒ 那 4 条与 freeze 无关 (重建前就绿)。"
                      "★最危险的一条: --freeze-registry 会制造「让人去抬 MISSING 上限」的假红灯 —— 实测把 58 条"
                      "改名漂移重分类成 56 条真隐患后, 只要把 BASELINE_COUNT 抬到 59 并登记那 56 个老名 ⇒ 闸就绿 ⇒ "
                      "58 条真漂移被一次性洗成「已登记基线」 (RT-9 · 只在沙盒演示·真件闸零改)。★",
             "note": "★⇒ SOP 的红线: 重建之后 MISSING 必须仍然 = 3; 一旦 > 3 ⇒ 第一反应是「文档没同步」, 不是「上限要抬」。★",
             "ref": "SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md §7-4 · logs/iss327/29_rev_suite_run.log · "
                    "logs/iss327/32_launder_run.log"},
            {"key": "SW-ISS327-5",
             "value": "★「重建注册表能不能让 10 道闸全绿」的逐字答案: ★不能★。★实测六臂 × 10 道闸 (60 次): "
                      "重建注册表【一道闸的 rc 都没改变】; 它只改第 8 道闸 (check_sw_ref_reachability) 的内部读数 —— "
                      "A2 (改名后·文档未同步·旧表) DRIFT=58 / MISSING=5 / OK=18 / rc=1 ⇒ A3 (同前 + 重建) "
                      "DRIFT=0 / MISSING=56 / OK=18 / rc=1 (★红得更狠·且冻结表只收得到 18 条★); 而 A4 "
                      "(改名后·文档已同步·【旧表】) 已经是 DRIFT=0 / MISSING=3 / OK=78 / rc=0 ⇒ "
                      "★「重建注册表」对这道闸【不是必需的】, 真正决定它绿不绿的是【SW 文档有没有同步改名】★。 "
                      "★其余 3 道红跟注册表完全无关: timing_check 改名特有崩 L1113 (TypeError) · "
                      "check_timing_review_adc_sync 是它的 fail-closed 连带 · check_demo_panel_spec + "
                      "check_onepass_sw_sync 是板/表 md5 没落台账链头 + SW01_PCB_MD5 清单过期 (归 S9 重锚)。★",
             "note": "★⇒ 「板那一趟」当天要全绿, 路径 = ISS-323 §5-1 的 7 件同批 (第 7 件文档同步排在第 1 件重建之前) + 第 6 件 md5 重锚。★",
             "ref": "logs/iss327/02_postrename_gate_table.md §2/§3/§5 · SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md §2/§3"},
        ]
        for c in new_claims:
            if c["key"] not in havec:
                claims.append(c)
                print("  + claim %s" % c["key"])

        # ── status 换 ISS-327 ──
        d["status"] = {
            "phase": "delivered",
            "progress_pct": 100,
            "health": "green",
            "updated_at": TODAY,
            "summary": "★ISS-327 (2026-11-18 14:21~16:5x · 三段续做) 交卷: "
                       "★「板那一趟当天能不能靠 --freeze-registry 让 SW 侧 10 道闸全绿」= 【不能】★ —— "
                       "★实测六臂 60 次闸链: 重建注册表一道闸的 rc 都没改·它只改第 8 道闸 (check_sw_ref_reachability) "
                       "的内部读数 (DRIFT 58→0 / MISSING 5→56 / 冻结表 74→18 条)★; 而这道闸当天能不能绿取决于"
                       "【SW 文档有没有同步改名】(实测: 文档同步后旧注册表就已绿: DRIFT=0 · MISSING=3 · OK=78 · rc=0)★ "
                       "⇒ 「重建注册表」对它是【不是必需的】。★真隐患不会被 freeze 洗白 (4 条反向用例 + 结构证明: "
                       "重建表 ⊆ live ⇒ 盘上从来没有过的 token 物理上进不了表)★, 但闸另有 4 条洗白面 "
                       "(C1/C7/C8/C13·与 freeze 无关) 且 freeze 会制造「抬 MISSING 上限」的假红灯 ⇒ RT-9 实测把 "
                       "58 条真漂移洗成基线。★交付: SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md (§0~§9·步 0~步 8 的"
                       "命令+期望读数+失败时下一步 + 回滚三档 + 留证清单 + 判据设计稿 + 9 条反向用例) + "
                       "logs/iss327/02_postrename_gate_table.md (六臂读数表) + logs/iss327/ (33 项原始输出) + "
                       "HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md (B0~B7)。★零写板·零落表·零改闸·"
                       "零外发; 自曝 2 处: ① 14:25 软链写穿事故 (main 14:39 已精确回退·内容经 41/41 独立副本逐字节"
                       "验证复原·残留只是 mtime) ② 本单 SOP 自己把闸带红 (已按 ISS-321「方案文档不写死位号」纪律"
                       "改成反斜杠形状修掉)。★",
        }

    update_fragment("sw-lead", mutate)
    d = load_fragment("sw-lead")
    print("★写后: artifacts=%d needs=%d claims=%d answers=%d"
          % tuple(len(d.get(k) or []) for k in ("artifacts", "needs_from", "interface_claims", "answers")))
    print("★status.phase=%s progress=%s health=%s"
          % (d["status"].get("phase"), d["status"].get("progress_pct"), d["status"].get("health")))
    n_iss = sum(1 for a in (d.get("artifacts") or [])
                if "ISS327" in str(a.get("path", "")) or "iss327" in str(a.get("path", "")))
    print("★含 iss327 的 artifact 条数 = %d" % n_iss)
    return 0


if __name__ == "__main__":
    sys.exit(main())
