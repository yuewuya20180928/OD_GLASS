#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main 登记 ISS-328 (★补一条真能构成对照的臂 + 官方链复测 TP no-op★) · 2026-11-18 16:5x

★**来源**: ISS-325 cont3 交卷里给 main 的两条待拍 (★① 20→10 删减 ② 要不要补真对照臂★)
★**main 的两条拍板** (★已写进 `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` 附录 R★):
  · P-1: ★**暂不删那 10 条 TP 条目** ⇒ 理由: no-op 结论只在演练链成立 (3666 段 vs 14023 段 = 两条产线)
    ⇒ 不能外推到官方链 (18092 段) ⇒ 删它收益 = 0 风险 > 0 ⇒ ★**先在官方链同配方下 fresh 复测 no-op, 再拍删不删** ★
  · P-2: ★**要补真对照臂, 但必须先过【对照有效性自检】** ⇒ 新开本单
★**派活前置**: ★**ISS-325 必须先落 (main 验完签字) 才许派本单** ⇒ 不许跟收尾抢带宽
"""
from __future__ import annotations
import fcntl, os, shutil, tempfile, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261118_1655"

BRIEF = """【ISS-328 · hw-lead · 补一条【真能构成对照】的臂 + 官方链复测 TP no-op】

★**★这是 main 拍板后开的单 (2026-11-18) · 派活前置: ★**ISS-325 必须先落 (main 验完签字), 不许跟收尾抢带宽★ ★**

## ★★★【① 为什么开这一单 (★先读这一段·★省得你重走 ISS-325 的弯路★)★★★】★★★

★**★ISS-325「左上布局沙盒预演」把 §3-5/§3-6/§3-8 的【处方前提】证伪了一部分⇒ ⇒ ★**盘上至今【没有任何实测】能回答「左上布局到底有没有用」★ ★**

| ★**已实测的 (★[实测]★)★** | ★**读数**★ |
|---|---|
| ★**「左上臂 vs 同日对照臂」不是对照** ★ | ★**两臂全板 185 个封装落位【逐个完全相同】(差异行数 = 1)** · 裸板 unc 网名集合 **31 == 31** · 链终 unc 网名集合 **27 == 27** · 链终几何 3544 走线/505 过孔/4 铜皮区全同 · 裸板段内 P/N 翻转 **5/47 == 5/47** ★ |
| ★**「显式钉 `TP_DSI_*`」是 no-op** ★ | ★**机制复核 (`state/gen_pcb_netlist_board.py` L1042~L1109「TP 贴伙伴件」): 不钉 TP 时生成器把 `TP_DSI_*` 自动落到【完全相同】的坐标** ⇒ ★**那 10 条 `PCB_PART_POS` 全是冗余的 (含 `TP_DSI_D0_N` (41.55,3.00))** ★ |
| ★**盘上不存在「右上布局」对照臂** ★ | ★**`state/*v76*arms*.sh` 53 条全部带 `PCB_PART_POS` (全钉左上); `/tmp/chain_v76mz` (11-11 代码) 是同 env 同配方 ⇒ 它测的是【代码漂移】不是布局差异** ⇒ ★**「左上布局」的净效应至今没有任何实测, 连「负的」都没测到** ★ |
| ★**漂移噪声量级** ★ | ★**同配方跨 7 天 = unc 30→29 / 网名 26→27 / viol 4→6 ⇒ 历史板之间 ±1~2 条 unc 的差都在噪声里** ★ |
| ★**同链基线对照的口径陷阱** ★ | ★**候选臂 3666 段 vs 基线 `state/.lastgood/baseline_v76_chain.kicad_pcb` 14023 段 ⇒ 段数差 4 倍 ⇒ 不是同一条产线 ⇒ 那张表的 REJECT 是「【两板不等价】⇒ 复现未成功」, 不是「臂变差」; ⇒ 不许把表里的「unc 46→29」当成「左上布局的功劳」** ★ |

★**★⇒ ⇒ 本单要做的两件 (★就这两件·★不要顺手多跑臂★) ★★**

## ★★★【② 第 ① 件: 补一条【真能构成对照】的臂 (右上臂)★★★】★★★

★**★硬前置 (★不满足就不许开跑·★白跑一小时★)★★**: ★**新臂 vs 基线臂的【全板 185 个封装落位 diff 必须 ≠ 0】⇒ ★**先用现成探针 (`logs/iss325/scripts/` 那套 pcbnew GetPosition 读法) 验落位真的不同 ⇒ ★**落位相同 = 又一条 no-op 对照 ⇒ 不许跑链, 直接写「本单无对照可做」交卷** ★★**

★**★做法 (★照抄 ISS-325 的臂 env·★只改那一个变量★) ★★**:
1. ★**基线臂**: ★**用【同一条产线】的链臂** (★★不是官方板★★) ⇒ ★**对照口径只能用 `state/compare_arm_baseline.sh` (同链基线) 或同配方同链臂★ ⇒ ★★**禁止拿官方板比 (那是另一条产线·不可比·老教训)★★ ★**
2. ★**右上臂**: ★**只把 `R_SEL_*` 那 10 条挪到右上** (★坐标帧照 `HW/PCB/LAYOUT_FIX_SPEC.md` §3 方案 A 的右上那组·★帧声明照 ISS-274★) ⇒ ★**其余一切不许动 (★不许顺手改 TP 那 10 条·★那 10 条本单还要复测 no-op·★见第 ③ 件★)★ ★**
3. ★**跑链后逐条贴读数**: ★裸板 / 链终 的 DRC viol · unc 条数 + 网名集合 · 全板 185 封装落位 diff · 链终几何 (走线/过孔/铜皮区) · 段内 P/N 翻转 · 名单制闸 rc ★

★**★★判据 (★照抄, 不许自创★) ★★**:
- ★**成功判据 = 名单制闸 rc=0 (退铜名单空 + 差分死腿空 + 逐网孤岛空) + DRC viol = 0** ★
- ★★**禁止拿「unc 条数变少」当成功 (★老教训: unc 变少 ≠ 板更好 ⇒ best23 板 unc 最低但名单制闸 REJECT)★★ ★**
- ★**失败也要交 (★「右上臂也是 REJECT」本身就是有价值的读数★) ★**

## ★★★【③ 第 ② 件: 在【官方链同配方】下复测 TP no-op (⇒ 给 main 的 P-1 判决补读数)★★★】★★★

★**★main 已拍板: ★**§3-S6 那条 20 条 `PCB_PART_POS` 串里的 10 条 TP 条目【暂不删】⇒ ★**理由: no-op 结论只在【演练链】成立 (3666 段 vs 14023 段 = 两条产线) ⇒ 不能外推到官方链 (18092 段 / 433 孔 是第三条线) ⇒ ★**删它的收益 = 0 (若 no-op 成立, 删与不删落板结果一样) ⇒ 风险 > 0 (改了已审过的处方串 = 新的逐字差异, 而板只许改一次)★ ★**

★**★⇒ 本单要补的就是这条读数: ★**在【官方链同配方】下, 「钉 TP」与「不钉 TP」两条臂的【全板 185 封装落位 diff】是不是【逐个完全相同】★ ★**
- ★**若逐个完全相同 ⇒ ★**那 10 条 TP 条目在官方链上也是 no-op ⇒ ★**main 下一轮可以把 P-1 改判成「删回 10 条」(★因为此时收益仍 = 0 但处方串变短 = 少 10 处逐字差异★)★ ★
- ★**若【不】完全相同 ⇒ ★**那 10 条 TP 条目在官方链上【有真实作用】⇒ ★**P-1 维持「一条都不许删」★ ★
- ★★**两种结果都必须交卷 (★「无差别」也是结论★) ★★**

## ★★★【④ 交卷物 (4 件)★★★】★★★
| # | 交付物 | 路径 | ★要求 ★ |
|---|---|---|---|
| 1 | ★**主交付页** ★ | ★**`HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md`** (★新建★) ★ | ★§0 口径与边界自证 + §1 唯一变量与落位自检 + §2 读数表 + §3 名单制闸判决 + §4 TP no-op 官方链复测 + §5 给 main 的结论 + §6 证据分级 + §7 文件清单 ★ |
| 2 | ★**交卷页** ★ | ★**`HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md`** (★新建★) ★ | ★**B0~B6 齐全** ★(★**B1 结论摘要 / B2 验收标准自评(逐条 通过/不通过/未验) / B3 证据分级(带 `[实测]`/`[推算]`/`[0数据]` 标签) / B4 接口取值声明 / B5 未决项与卡点 / B6 自证复现命令★) ★★**不许留「(施工中)」占位符** ★ |
| 3 | ★**证据目录** ★ | ★**`logs/iss328/`** ★ | ★每条被引用的读数都有对应 raw 文件 · 悬空引用 = 0 ★ |
| 4 | ★**分片** ★ | ★**`state/fragments/hw.yaml`** ★ | ★**必须走 `python3 state/frag_write.py --agent hw-lead` (★禁止 `open(p,"w")`★)** ★ |

## ★★★【⑤ 边界 (★违反就是不合格★)★★★】★★
- ★**零写板**: ★**`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` · mtime 必须还是 `2026-11-06 07:07:17.362193413`** ★(★**官方板只许在「板那一趟」改一次·本单是沙盒预演·G1 仍开★**)
- ★**零落表** (★网表/脚表/BOM/原理图真源一个字节不许动★) · ★**零改闸** (★`state/gate_check.py` / `state/compare_arm_*.py` / `state/check_*.py` 一个字不许改★) · ★**零改生成器代码** (★`state/gen_*.py` 只读★) · ★**零改既有文档正文** (★**本单只许新建 `HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` + 本单自己的交卷页★; ★`HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` 附录 R / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/LAYOUT_FIX_SPEC.md` 只读★) ★
- ★**沙盒只写 `tmp/iss328/` + `logs/iss328/`** · ★**只写 `state/fragments/hw.yaml`** · ★**零改 `state/gate_check.py`** · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★
- ★**★★沙盒里凡要【写】的文件 ⇒ 一律真拷贝; 写前 `assert not os.path.islink(path)`** ⇒ ★**sw-lead 那边已经因为软链写穿过一次真件 (11-18 14:39·11 份 `SW/*.md` 被改)★** ★
- ★**★一次 write 别超过 ~6000 字 ⇒ 先 write 骨架, 再 edit 逐块补** ⇒ ★**ISS-326 连挂两趟都是死在超长 write 上·★先落骨架, 再干活★ ★**

## ★★★【⑥ 交卷前必跑 (原样输出贴进交卷页)★★★】★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py   # rc 必须 0
python3 state/gate_check.py   # rc 必须 0 (★若红在 SW 侧 SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md ⇒ 那不是本单的红·原样贴出来 + 说明归属即可★)
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb   # 必须 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md "HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md"   # 必须 0 0
grep -c "iss328" state/fragments/hw.yaml   # 必须 >= 1
find tmp/iss328 -type l | wc -l   # 必须 0 (★不许有软链★)
```
★额外纪律: ★**证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标** ★ · ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ 缺口一律自己网上查 + 标证据等级 + 写降级方案** ★ · ★**交卷前跑 merge.py (rc=0) && gate_check.py 并把输出贴进回复** ★"""


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        if any(i.get("id") == "ISS-328" for i in issues):
            print("· ISS-328 已存在 (跳过)")
            return 0
        new = {
            "id": "ISS-328",
            "title": "★补一条【真能构成对照】的右上臂 (R_SEL_* 挪右上) + 在官方链同配方下复测 TP no-op (⇒ 给 ISS-325 的 P-1「20→10 删不删」补读数)",
            "severity": "high",
            "source_blocker": "HW-S8",
            "source_agent": "hw-lead",
            "desc": ("ISS-325 证伪了两条前提: ①「左上臂 vs 同日对照臂」不是对照 (全板 185 封装落位逐个相同 · "
                     "unc 网名集合 31==31 / 27==27) ⇒ 盘上至今【没有任何实测】能回答「左上布局到底有没有用」; "
                     "②「显式钉 TP_DSI_*」是 no-op (生成器自动落到完全相同坐标) ⇒ §3-S6 那条 20 条 PCB_PART_POS 串里的 10 条 TP 条目冗余. "
                     "⇒ 本单做两件: ① 补一条真能构成对照的右上臂 (硬前置: 全板 185 封装落位 diff ≠ 0, 否则又白跑) "
                     "② 在官方链同配方下复测 TP no-op (两种结果都必须交卷)"),
            "owner": "hw-lead",
            "reporter": "main",
            "raised": "2026-11-18",
            "due": "2026-11-20",
            "status": "open",
            "external": False,
            "need_keys": [],
            "task_brief": BRIEF,
            "fix_ref": "HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md (★新建★) · HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md (★新建★) · logs/iss328/ (★新建★)",
            "verify_by": "main",
            "verify_result": None,
            "verify_date": None,
            "note": ("★2026-11-18 16:5x 项目总工登记: ISS-325 cont3 交卷给 main 两条待拍 ⇒ main 已拍板 (★详见 "
                     "HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md 附录 R★): "
                     "P-1 「20 条 PCB_PART_POS 串删回 10 条」= ★**暂不删, 一个字都不许动** ⇒ 理由: no-op 结论只在演练链成立 "
                     "(候选 3666 段 vs 基线 14023 段 = 两条产线) ⇒ 不能外推到官方链 (18092 段) ⇒ 删它收益 = 0 风险 > 0 ⇒ 先复测再拍; "
                     "P-2 「要不要补真对照臂」= ★**要, 但必须先过【对照有效性自检】(全板 185 封装落位 diff ≠ 0) + 只许用同链基线比 "
                     "(禁止拿官方板比) + 判据 = 名单制闸 rc=0 且 DRC 0 (不许拿 unc 变少当成功)★ ⇒ 故开本单. "
                     "★**派活前置: ISS-325 必须先落 (main 验完签字) 才许派本单, 不许跟收尾抢带宽** ★"),
            "dispatched_at": None,
        }
        issues.append(new)
        out = dict(log); out["issues"] = issues
        shutil.copy2(LOG, LOG + ".bak_cronfb67_%s_open328" % STAMP)
        atomic_write(LOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100000))
        print("· ISS-328 已登记 (owner=hw-lead · status=open · 派活前置=ISS-325 先落)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
