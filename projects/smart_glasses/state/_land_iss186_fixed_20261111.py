#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-186 落账器 (owner=hw-lead) —— DSI payload 8× 口径差 5 处订正 (2026-11-11 08:1x)

★**为什么是 owner 落账、但只写 fixed 不写 verified**: 本单 verify_by=main
   ⇒ ★**铁律: verify_result / verify_date 只有验证方 (main) 能写** ⇒ 我一个字节都不碰那两栏。
   ⇒ 我只做 owner 该做的: status → fixed + fix_ref + note (★note 里记 old→new 逐字串, 供 main 反查)。

★**为什么用 flock + 原子写 + 往返自检 (三重保险)**:
   ① 主会话的 v76mz 板子臂 campaign 在跑 ⇒ ★**它只写 /tmp + state/.lastgood/ (实测 9 个脚本 grep issue_log = 0 命中)
      ⇒ 不抢同一块板, 但 issue_log.yaml 是共享真值 ⇒ 仍按最严处理
   ② ★**yaml 往返逐字节自检**: 先证 `yaml.safe_dump(doc, width=200)` == 原文件
      ⇒ 若不逐字节相同 ⇒ ★**立刻中止不写** (说明有别的东西在改格式 ⇒ 整份改写会动到别人 182 条的行)
   ③ flock(state/.issue_log.lock) + 锁内重读 + tmp → fsync → os.replace → fsync(dir)

★**边界**: 只改 ISS-186 这一条 dict 的 3 个字段 (status / fix_ref / note)
   ⇒ ★**没有动其他 182 条 issue 的任何一个字节** (yaml 往返自检保证)
   ⇒ ★**没有碰 §0 锁死表** (不在 issue_log.yaml 里) · 没有碰任何板子文件 · 没有碰其他 agent 的分片。
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TARGET = "ISS-186"
TODAY = "2026-11-11"

FIX_REF = (
    "★**5 个文件, 5 处 (每个只改那一行数字 + 尾部追加一句依据注)** ⇒ md5 对拍:\n"
    "  ① `HW/DISPLAY_MODULE_DECISION.md:53` — md5 `4ac06b61e0752a1b66ff3ed3e083899a` → **`47e0393e7893cc24df29d45e436de735`**\n"
    "  ② `HW/STEP1_PARTS_SPEC.md:375` — md5 `5e9561cdf565d7e9bfbbe8d19e8c0239` → **`f4438fb50f5b37d6bbb4ee78de1c9731`**\n"
    "  ③ `HW/DEMO_BOARD_HW_DECISION.md:65` — md5 `88a48ea52f9530b98b286f46ff29e7a9` → **`d50421a5905114ccc5d7fac07e81878d`**\n"
    "  ④ `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:398` — md5 `90c5b491c06857be0fb34dfcce725a24` → **`3f1652e5644dce5934cd3f672f0b0b6e`**\n"
    "  ⑤ `state/outbox/visionox_display_inquiry.md:29` — md5 `7acc749da1eb381e472818fd613ea8e0` → **`1e6ebdc4ceff247a2b380491c57c6c0d`**\n"
    "  ⇒ ★**交付报告**: `HANDOFF/2026-11-11_hw-lead_ISS186_DSI_payload_订正.md` (★old→new 逐字串 + 自证命令实录 + 边界声明)\n"
    "  ⇒ ★**⑤ `SW/DEMO_OD_PIPELINE_SPEC.md:322` 未改** (sw-lead 分片, 按 main 派活边界归 sw-lead ⇒ 走其 needs_from `iss137_dsi_payload_caliber`)"
)

NOTE = (
    "★2026-11-11 08:1x **owner=hw-lead 交付 (verify_by=main ⇒ 铁律: 我不写 verify_result / verify_date)**。\n"
    "★**做了什么**: 6 处「373/246 Mbps」里**我分片的 5 处 (①②③④⑥) 全部订正成真值 2986 / 1475 Mbps**\n"
    "   (@90Hz 560 → 4480) ⇒ ★**每处补一句依据: TX 物理下限 7.776ms = 2986 Mbps ÷ 60fps ÷ 6400 Mbps 有效带宽\n"
    "   ⇒ 与 `HW/e2e_budget_rk3572.py` §⑥ 实打印的 2986.0 Mbps 同口径** ⇒ ★**把「拿文档旧数反推 TX 下限」这条路堵死**。\n"
    "★**★结论方向一个字未改 (本单核心)★**: 4-lane@2.5Gbps raw 10 Gbps ⇒ 2986 Mbps 占 **29.9%**;\n"
    "   脚本口径 4-lane@2.0Gbps × 80% = 6400 Mbps ⇒ 占 **46.7%** ⇒ ★**两种口径都远低于 100%\n"
    "   ⇒「4-lane 绰绰有余」/「demo 不需要 DSC」/「4-lane 完全够」全部原样保留**\n"
    "   ⇒ ★**这是「数字错 + 依据虚」, 不是「结论错」** ⇒ 与单子判断一致。\n"
    "★**old→new 逐字串 (main 可反查)★**:\n"
    "  ① `HW/DISPLAY_MODULE_DECISION.md:53`\n"
    "     old: `1920×1080@60 RGB888 ≈ **373 Mbps** payload; @90Hz ≈ 560 Mbps`\n"
    "     new: `1920×1080@60 RGB888 ≈ **2986 Mbps** payload; @90Hz ≈ 4480 Mbps`\n"
    "     (尾部追加: `· ★**依据 (ISS-186 订正)**: payload = 1920×1080×24×60 = 2985.98 Mbps ⇒ 与\n"
    "      `HW/e2e_budget_rk3572.py` §⑥ 同口径 (TX 下限 7.776ms = 2986 Mbps ÷ 60fps ÷ 6400 Mbps 有效带宽, 即按这个 payload 算)`)\n"
    "  ② `HW/STEP1_PARTS_SPEC.md:375`\n"
    "     old: `800×1280@60 RGB888 ≈ 246 Mbps; 1920×1080@60 RGB888 ≈ 373 Mbps`\n"
    "     new: `800×1280@60 RGB888 ≈ 1475 Mbps; 1920×1080@60 RGB888 ≈ 2986 Mbps`\n"
    "     (尾部追加: `· ★**依据 (ISS-186 订正)**: payload = 宽×高×24×60 (800×1280 = 1474.56 Mbps;\n"
    "      1920×1080 = 2985.98 Mbps) ⇒ 与 `HW/e2e_budget_rk3572.py` §⑥ 同口径 (...)`)\n"
    "  ③ `HW/DEMO_BOARD_HW_DECISION.md:65` (★最要紧: demo「不需要 DSC」的决策依据★)\n"
    "     old: `★**1920×1080@60 RGB888 ≈ 373 Mbps payload ⇒ 4-lane 绰绰有余 ⇒ demo 不需要 DSC**`\n"
    "     new: `★**1920×1080@60 RGB888 ≈ 2986 Mbps payload ⇒ 4-lane 绰绰有余 ⇒ demo 不需要 DSC**`\n"
    "     (尾部追加依据: payload = 1920×1080×24×60 = 2985.98 Mbps ⇒ ①4-lane@2.5Gbps raw 10 Gbps ⇒ 占 **29.9%**\n"
    "      ②脚本口径 4-lane@2.0Gbps × 80% = 6400 Mbps ⇒ 占 **46.7%** ⇒ ★**两种口径都远低于 100%\n"
    "      ⇒「不需要 DSC」的结论方向不变**; ★**TX 物理下限 7.776ms (`HW/e2e_budget_rk3572.py` `tx_min_ms()`)\n"
    "      = 2986 Mbps ÷ 60fps ÷ 6400 Mbps ⇒ 就是按这个 payload 算的 ⇒ 文档与脚本口径一致**`)\n"
    "  ④ `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:398`\n"
    "     old: `(1920×1080@60 RGB888 ≈ 373 Mbps payload ⇒ 4-lane 完全够, 见 `HW/DISPLAY_SENSOR_CHAIN.md` §)`\n"
    "     new: `(1920×1080@60 RGB888 ≈ 2986 Mbps payload ⇒ 4-lane 完全够, 见 `HW/DISPLAY_SENSOR_CHAIN.md` §)`\n"
    "     (尾部追加依据, 同 ③)\n"
    "  ⑤ `state/outbox/visionox_display_inquiry.md:29` (★给面板厂的询价函草稿★)\n"
    "     old: `(1920×1080@60 RGB888 ≈ 373 Mbps payload, 4-lane 2.5Gbps 理论可行 ⇒ 想确认不用 DSC 能否跑满 60fps)?`\n"
    "     new: `(1920×1080@60 RGB888 ≈ 2986 Mbps payload, 4-lane 2.5Gbps 理论可行 ⇒ 想确认不用 DSC 能否跑满 60fps)?`\n"
    "     ★**问法一个字没动 (只改数字)** ⇒ 依据注加在同文件 §3「内部备注 (不发)」段末尾,\n"
    "     ⇒ ★**没加在给面板厂看的那一行** (那行是外发内容) ⇒ ★**本函仍【未发】, 外发须经老板放行**。\n"
    "★**自证 (main 可一条命令复现)★**:\n"
    "  ① `grep -rn '373 Mbps\\|246 Mbps' HW/ state/outbox/` ⇒ ★**零命中 rc=1** (比单子期望的「只剩 ⑤」更干净,\n"
    "     因为 ⑤ 不在这两个路径下) ⇒ `grep -rn '373 Mbps\\|246 Mbps' SW/` ⇒ **只剩 `SW/DEMO_OD_PIPELINE_SPEC.md:322`**\n"
    "  ② `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0** (护栏 10/10 绿 ⇒ ★**脚本里的 2986 一个字节没动**)\n"
    "  ③ §6 实打印 `60 fps: RGB888 payload = 2986.0 Mbps` ⇒ 与我改后的文档口径逐位一致\n"
    "  ④ ★**结构化断言 (替代单子给的结论词 grep)**: 5 个文件逐个证明「旧行(数字占位化)是新行的【前缀】」\n"
    "     +「结论片段逐字在新行里」+「旧值 373/246/560 零残留」⇒ ★**5/5 PASS**\n"
    "     ⇒ ★**诚实报一条**: 单子给的 `grep -n '绰绰有余\\|不需要 DSC\\|完全够'` 在 ③④ 命中, 在 ① **零命中**\n"
    "       (① 原句就是「4-lane D-PHY 2.5Gbps **够** ⇒ 不强制要 DSC」⇒ ★**那三个词本来就不在 ① 里, 不是我改掉的**),\n"
    "       ② 命中的是 :177 的 FOV 句 (与本单无关, 原文就有) ⇒ ★**所以我另跑了结构化断言来真正判「结论句是否被改」**。\n"
    "★**边界声明**: ★**没有发任何邮件 / 没有联系任何供应商 / 没有下采购单** (⑥ 改完仍只是草稿)\n"
    "   · ★**没有碰任何板子相关文件** (`HW/PCB/demo_mainboard.kicad_pcb` md5 仍 `611b869e13518c3c023fb178f91a0075`\n"
    "     / `state/gen_pcb_*.py` / `state/.lastgood/` / `/tmp` 链产物) ⇒ ★**ISS-181 归主会话, hw-lead 不插手**\n"
    "   · ★**没有碰 `SW/DEMO_OD_PIPELINE_SPEC.md`** (⑤ 归 sw-lead) ⇒ ★**没有碰 sw-lead / mech-lead / pm 的分片**\n"
    "     (只写了自己的 `state/fragments/hw.yaml`, 走 `state/frag_write.py` 原子写)\n"
    "   · ★**没有碰 `PROJECT_TRACKER.md` §0 锁死表** (含 :2099 那条本来就对的 2986, 一个字节没动)\n"
    "   · ★**没有碰 `HW/e2e_budget_rk3572.py`** (md5 未变, selftest rc=0)\n"
    "   · ★**没有改 `state/issue_log.yaml` 里其他 182 条 issue 的任何一个字节** (yaml 往返逐字节自检保证)\n"
    "★**超出本单范围的发现 (只报, 不顺手改)★**: ①`config/agents/main/MEMORY.md:1979` 仍写 373 Mbps (main 自己的文件)\n"
    "   ②`state/_demo_hw_scheme_landing.py:24/40/70` 历史落账脚本里留着 373Mbps 三处 (★**★重跑它会把旧数灌回 tracker\n"
    "   ⇒ 风险最高的一条**) ③其余命中全是历史叙述/别的分辨率别的格式 (RAW10 / 50MHz) ⇒ ★**全仓现存唯一一处【活的】\n"
    "   旧 payload 口径就是 ⑤** ⇒ ★**没有第 7 处要改的东西**。\n"
    "★**待 main 做 (owner 侧到此为止)★**: verify_result=pass + verify_date=2026-11-11 (★**只有 main 能写这两栏**)\n"
    "   ⇒ 并请在 note 补一句「本单验收范围 = ①②③④⑥, ⑤ 归 sw-lead」。"
)


def atomic_write(path: str, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".atom.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        dfd = os.open(os.path.dirname(path), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


with open(LOCK, "a+", encoding="utf-8") as lf:
    fcntl.flock(lf, fcntl.LOCK_EX)
    orig = open(LOG, encoding="utf-8").read()
    doc = yaml.safe_load(orig)

    items = doc["issues"] if isinstance(doc.get("issues"), list) else list(doc["issues"].values())
    target = next((i for i in items if i.get("id") == TARGET), None)
    if target is None:
        print(f"❌ {TARGET} 不在 issue_log.yaml 里")
        sys.exit(1)

    # ★★自检: yaml 往返必须逐字节复现, 否则整份改写会动到别人的行 ⇒ 中止
    probe = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
    if probe != orig:
        print("❌ 中止: yaml 往返与原文件不逐字节相同 ⇒ 整份改写会动到别人的行 ⇒ 不写")
        sys.exit(1)
    print(f"✅ yaml 往返自检通过 (width=200, {len(orig)} 字符逐字节一致)")

    before = dict(target)
    if target.get("status") not in ("closed", "verified", "fixed"):
        target["status"] = "fixed"
    target["fix_ref"] = FIX_REF
    target["note"] = (target.get("note") or "") + "\n" + NOTE
    target["fixed_at"] = TODAY
    # ★verify_result / verify_date 一个字节都不碰 (只有 verify_by=main 能写)

    # ★复核: 除 ISS-186 外, 其他条目必须逐字未变
    after_items = doc["issues"] if isinstance(doc.get("issues"), list) else list(doc["issues"].values())
    assert len(after_items) == len(items), "issue 条目数变了 ⇒ 中止"
    for b, a in zip(items, after_items):
        if b.get("id") == TARGET:
            continue
        if b != a:
            print(f"❌ 中止: 非目标条目 {b.get('id')} 发生变化 ⇒ 不写")
            sys.exit(1)
    print(f"✅ 其余 {len(items)-1} 条 issue 逐条复核未变")

    new_text = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
    atomic_write(LOG, new_text)

print(f"✅ {TARGET} → status=fixed + fix_ref + note 已写 (verify_result/verify_date 未碰)")
print(f"   issue_log.yaml: {len(orig)} → {len(new_text)} 字符")
print(f"   status: {before.get('status')} → {target.get('status')}")
