#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · cont2 分片增量 (走 state/frag_write.py · ★禁 open(p,"w")★)

纪律:
  ① 只写 state/fragments/mech.yaml (别人的分片一个字节不碰)
  ② ★零重复 add 同 key★ ⇒ 已存在的 need / claim / artifact 一律【就地追加】, 不再 append 第二条
  ③ 原子写 (state/frag_write.atomic_write_yaml)
  ④ 自签 issue_log = 禁止 ⇒ 本脚本不碰 state/issue_log.yaml
"""
import importlib.util
import os
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
FW = os.path.join(ROOT, "state", "frag_write.py")

spec = importlib.util.spec_from_file_location("frag_write_mod", FW)
fw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fw)

CALIBER = "MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md"
HANDOFF = "HANDOFF/2026-11-18_mech-lead_ISS324_D_LED_G落位口径.md"

CALIBER_ADD = (
    " ★★cont2 (2026-11-18 16:4x) 重建并追加三条★: "
    "(a) ★§1.3 死因归属拆解★ = G12 登记的两条死因只有第 1 条 (`LED_G_D` 93.49mm) 是 `D_LED_G` 落位能解的; "
    "第 2 条「`LED_G` 被 `LED_B` 掐 0.200mm」的根因是 `J_SOM_P4` 连接器的 0.40mm 针距 (pad19 `LED_G` (31.20,50.96) ↔ pad21 `LED_B` (30.80,50.96), 焊盘宽 0.200 ⇒ 边缘净距 0.400−0.200=0.200) ⇒ ★挪 `D_LED_G` 解不了它, 归 hw-lead 逃逸策略 ⇒ 落位拍完 45→0 仍可能不成立★ "
    "(b) ★§3.1 下半带新登记★ = 「最近落位带」其实有上下两块 (既有文档只登记上半块 X 6.940..8.250 × Y 63.700..67.900; "
    "本单自写 s-expr 解析器重扫后查出下半块 X 6.940..8.250 × Y 59.700..61.900, 根因是既有闸代理量相对 `R_LED_G` 上下不对称) ★ "
    "(c) ★§5.5 现状落位合法性自查★ = 现状 (101.25,56.80) 本身就在可放行空间内 (窄带 X 101.240..101.250 × Y 47.700..70.800) ⇒ 假设 B 下「不动」合法 "
    "★★cont2 没有推翻 cont1 的任何结论 (首选仍 C3 8.420,64.200 · pad2 仍 = 原点+1.85 · M1/M2/M3 三口径与 netclass 0.20 全保留)★★"
)
HANDOFF_ADD = (
    " ★★cont2 追加块 C (2026-11-18 16:4x)★: C-1 主交付物重建 (cont1 13:0x 的 63,412 B 版被 11:4x 那趟在 15:5x 覆盖 ⇒ 按 cont1 结论 + cont1 原始读数 + cont2 新算重建为 43,671 B 合并版, 章节编号与分片交叉引用对齐) · "
    "C-2 ★★门禁链 rc=1 的逐字归因★★ (唯一红 = Q1 14/18 中 mech-lead 2/6, 根因 = `state/gate_check.py` 的 `pick_handoff()` 按文件名倒序取最新一份交接单 ⇒ 扫到的是并发单 ISS-326 的骨架页 (14:22, 1,593 B, B 块全是「(施工中)」) ⇒ 按「自称 B 块结构 ⇒ 不回退」规则不回退到本单那份 ⇒ ★与本单内容无关, 本单不越界替它补★; 同理 Q2 证据分级 2/3 与 Q5 硬指标 0/3 也是扫那份骨架 ⇒ 本单自己的两份文档有 22 条证据分级标签 + 7 类硬指标) · "
    "C-3 零写板/零落表/零改闸/零改既有文档正文的交卷前后双证 (含并发单导致 hw.yaml/sw.yaml/pm.yaml/issue_log.yaml 变更的逐字 mtime 归因) · "
    "C-4 cont2 对分片的增量 (零重复 add 同 key) · C-5 cont2 的复现命令 · C-6 自查表 10 条★"
)
NEED_ADD = (
    " ★★cont2 (2026-11-18 16:4x) 补一句★: ★本单查清了「不拍的后果」里那【两条】死因的归属 —— 只有第 1 条 (`LED_G_D` 93.49mm) 是 `D_LED_G` 落位能解的; "
    "第 2 条 (`LED_G` 被 `LED_B` 掐 0.200mm) 的根因是 `J_SOM_P4` 连接器的 0.40mm 针距 (pad19↔pad21 边缘净距 0.200) ⇒ ★挪 `D_LED_G` 解不了它, 归 hw-lead 的逃逸策略★ "
    "⇒ ★即使本条拍完, S8 的 45→0 仍可能不成立 ⇒ 老板拍这一条时, 请连同「`LED_G` 逃逸归 hw-lead」一起排★ (证据: MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md §1.3 + logs/iss324/01c_probe_som_pad_pitch.log)★"
)
CLAIM_SOM = {
    "key": "iss324_d_led_g_som_escape_criterion",
    "value": "J_SOM_P4 pad19(LED_G) <-> pad21(LED_B) 边缘净距 >= 0.20mm (逃逸判据·与 D_LED_G 落位无关)",
    "note": (
        "★ISS-324 cont2 新增的接口取值 (给 hw-lead 的逃逸口径, 零改闸·本单未建闸)★ "
        "· 口径 = `J_SOM_P4` 同排相邻两脚 pad19(net LED_G) @ (31.20,50.96) 与 pad21(net LED_B) @ (30.80,50.96), "
        "焊盘 0.200 x 0.700 ⇒ 中心距 0.400 ⇒ 边缘净距 0.200 (★同排 50 脚最小相邻针距 = 0.400mm★) "
        "· ★关键: 这是 G12 第二条死因的根因, 与 `D_LED_G` 落在哪一点无关 ⇒ 挪 `D_LED_G` 解不了它 ⇒ 归 hw-lead 逃逸策略 (换层/换过孔/让 LED_B 改道)★ "
        "· 新闸设计 = §8.1 D8 (必须独立于 D1, 不许被 D1 的判红掩盖) + 反向用例 R8 (挪 pad19 0.5mm ⇒ D8 红而 D1 仍绿) "
        "· 出处: MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md §1.3 / §8.1 D8 / §8.2 R8 · 原始输出 logs/iss324/01c_probe_som_pad_pitch.log"
    ),
    "ref": "MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md#18",
}

STATUS_SUMMARY = (
    "★ISS-324 (2026-11-18 · mech-lead · cron fb67af40) cont2 续做交卷 (16:4x)★: "
    "cont1 (12:1x~13:0x) 已交卷, 15:52 一次 gateway reload 后 cont2 接手重建主交付物并补三条新算的东西。 "
    "★主交付物 MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md (§0~§9, 43,671 B, 章节编号与本分片交叉引用对齐) + 交卷页 "
    "HANDOFF/2026-11-18_mech-lead_ISS324_D_LED_G落位口径.md (B0~B6 + cont2 追加块 C) + 分片★ ⇒ 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log。 "
    "★cont1 的结论全部保留 (首选 C3 8.420,64.200 · 次选 C2 8.050,63.900 · 备选 C5 8.250,66.000 · 假设B专属 C6 2.500,60.000 · C1/C4 因异网零净距 DRC 必红淘汰 · pad2 真值 = 原点+1.85 · M1/M2/M3 三口径 · netclass 0.20)★ "
    "★cont2 唯一新算三条★: ① §1.3 G12 两条死因的归属拆解 ⇒ 只有 `LED_G_D` 93.49mm 那条是 `D_LED_G` 落位能解的; 第 2 条 (`LED_G` 被 `LED_B` 掐 0.200mm) 根因在 `J_SOM_P4` 0.40mm 针距 (pad19↔pad21) ⇒ 挪 `D_LED_G` 解不了 ⇒ 落位拍完 45→0 仍可能不成立 ★ "
    "② §3.1 「最近落位带」下半块 (X 6.940..8.250 × Y 59.700..61.900) 新登记 (既有闸代理量上下不对称所致) ★ "
    "③ §5.5 现状落位合法性自查 (现状 101.25,56.80 本身在可放行空间内 ⇒ 假设 B 下「不动」合法)。 "
    "★门禁链逐条 rc 已落盘 logs/iss324/07_gate_chain.log: 三道 MECH 闸 + merge 全 rc=0; ★state/gate_check.py rc=1, 唯一红 = Q1 14/18 中 mech-lead 2/6 ⇒ 逐字归因 = gate_check 的 pick_handoff() 取【最新一份】交接单 ⇒ 扫到的是并发单 ISS-326 的骨架页 (14:22, 1,593 B, B 块全是「(施工中)」) ⇒ 与本单内容无关, 本单不越界替它补★ (Q2 2/3 与 Q5 0/3 同因)。 "
    "★板 md5 611b869e… / mtime 2026-11-06 07:07:17 未变; 受保护真源 5 件内容变更 0; MECH/*.py 59 件变更 0; MECH/*.md 既有真件变更 0; 别人的分片与 issue_log 的并发变更已按 mtime 逐字归因★。"
)


def mutate(d):
    # ---- ① 两个已存在的 artifact: 就地追加 cont2 摘要 (不新增条目) ----
    hit = 0
    for a in d.get("artifacts", []):
        if a.get("path") == CALIBER:
            a["summary"] = (a.get("summary", "") + CALIBER_ADD)
            a["version"] = "v1.1"
            a["updated_at"] = "2026-11-18"
            hit += 1
        elif a.get("path") == HANDOFF:
            a["summary"] = (a.get("summary", "") + HANDOFF_ADD)
            a["version"] = "v1.1"
            a["updated_at"] = "2026-11-18"
            hit += 1
    if hit != 2:
        raise SystemExit("[cont2_frag] 预期就地追加 2 个 artifact, 实到 %d ⇒ 停手" % hit)
    # ---- ② 已存在的 need: 就地追加一句 (key 不变, 原文一字不删) ----
    hit = 0
    for n in d.get("needs_from", []):
        if n.get("key") == "iss324_d_led_g_placement_decision":
            if "cont2 (2026-11-18 16:4x) 补一句" not in n.get("item", ""):
                n["item"] = n.get("item", "") + NEED_ADD
            hit += 1
    if hit != 1:
        raise SystemExit("[cont2_frag] 预期找到 1 条 need, 实到 %d ⇒ 停手" % hit)
    # ---- ③ 新增一条 interface_claim (新 key, 不重复) ----
    keys = {c.get("key") for c in d.get("interface_claims", [])}
    if CLAIM_SOM["key"] in keys:
        raise SystemExit("[cont2_frag] claim key 已存在 ⇒ 停手")
    d.setdefault("interface_claims", []).append(CLAIM_SOM)
    # ---- ④ status ----
    st = d.setdefault("status", {})
    st["phase"] = "done"
    st["progress_pct"] = 100
    st["health"] = "green"
    st["summary"] = STATUS_SUMMARY
    d["updated_at"] = "2026-11-18T16:45:00+08:00"
    d["updated_by"] = "mech-lead"


def main():
    fw.update_fragment("mech-lead", mutate)
    print("[cont2_frag] ★state/fragments/mech.yaml 已原子更新 (走 state/frag_write.update_fragment, 禁 open(p,'w'))★")
    print("[cont2_frag] · artifact 就地追加 2 (无重复条目)")
    print("[cont2_frag] · need `iss324_d_led_g_placement_decision` 就地追加 1 句 (key 不变)")
    print("[cont2_frag] · interface_claims 新增 1 (iss324_d_led_g_som_escape_criterion)")
    print("[cont2_frag] · status 已更新")
    return 0


if __name__ == "__main__":
    sys.exit(main())
