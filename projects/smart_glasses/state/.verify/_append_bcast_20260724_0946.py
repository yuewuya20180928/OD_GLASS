#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""append 2026-11-24 09:46 播报记录到 memory/2026-11-05.md (append-only)"""
import io, os

WS = "/home/yuewuya/.openclaw/workspace"
MEM = os.path.join(WS, "memory", "2026-11-05.md")
FACTS = os.path.join(WS, "projects/smart_glasses/state/.verify/_bcast_facts_20260724_0946.txt")

facts = open(FACTS, encoding="utf-8").read().rstrip("\n")

card = """进展 2026-11-24 09:46 | 走线 18092 段 | 过孔 433 | unconnected 45 | DRC 0 (板 md5 611b869e… 自 11-06 07:07 未动 · facts 内「已放行」0 处 ⇒ 无放行章 ⇒ G1 仍开, 不许投板)
当前在做: 主线 = PCB 图「板只改一次」那一趟; 板面零变化 (18 天逐字节未动), 变化全在签收/派活侧 —— 09:24 main 独立签收 ISS-384/385/386 三单 (台账 384 条 · 三单 verified) + 裁 18 条 main 地界待裁项 + 2 条老板域项转交 (一件没代拍); 09:36 决策页 §㊵ 追加 ⇒ 老板清单覆盖 52→53 条零漏项 (老字一字未删); 09:44 兄弟 job 开 ISS-387/388/389 三条新单并派出 (hw 原厂 land 几何 / sw 两道已签收闸实测坏了 / mech 两连接器结构侧收口), 三条全部零写板; 三个总工 open=0 且 fixing=0 ⇒ advance.py internal=[] 的根因形态第一次变: 从「槽位被占」变成【队列真空】(decisions 53 条)
待办 ①: ISS-387/388/389 三条在飞待交卷 —— ISS-388 是本轮实跑撞出的真病灶: 两道【已签收 verified】的 SW 闸今天实测真的 FAIL —— check_debug_pin_order_contract.py --selftest 10/11 (默认 TMPDIR=/tmp ⇒ 沙盒 ROOT 退成 / ⇒ 换 TMPDIR=$PWD/tmp 即 11/11 PASS ⇒ 环境敏感, 不是判据敏感), check_sw_board_md5_rebase_readiness.py --selftest 0/10 + 裸跑 5/7 rc=1 (H1/H4 判红 = 账本没跟上, 不是闸坏); 两道闸都零挂链 ⇒ daily_check/gate_check 全绿看不见 ⇒ 「板只改一次」那趟的护栏烂着
待办 ②: 板那一趟仍是 G1 唯一缺口 —— 布线 unc 45→0 + 布局修正 + 位号改名 + 板侧同步 B-1~B-8 + Gerber/投产包重出 同一趟做完; 巡检两条老账 check_pcb_nets rc=1 (网表 480 / 板上 482 · 多余 2 · 同号异网 3) 与 chain_gate rc=1 都是这一趟本体, 板重出时一起清; G1a 还差 G1a-4 (翻面口径) + G1a-8 (关机语义 SD-1 + 负载开关 TPS22991RAA 追认 LS-1) —— 两条在老板域, 已按自己查到的资料给出建议默认值与证据等级, 未代拍
待办 ③: 板框第一问 (甲 demo 台架板 / 乙 F30A 产品板) 仍待定 —— 结构件出件窗口挂它 (ISS-389 答复窗口 = 这个问题的窗口); 自己查的实跑数据 (main 36 档 = 3 框 × 板厚 4 × 层数 3): B160×100 36 档全红 (V 链 −68.00 / L 链 −85.50 · 板重 47.36g = 整机质量预算 65~97%) · F30A 板厚 0.80/1.00 两档全绿 (内腔 4.90/4.70) · P60×15 整档作废 (套 A 四孔在 15 mm 板上不成立); 权威口径 = 一页 §⑥/§§⑦/§⑬-3 + 索引 §E-1(已就地标注)/§R/§T, 未代拍; 同批还有电芯型号 D-2-9 (ICP422339PR 4.6 mm vs ICP582035PR-01 6.4 mm): 按现型号到货厚 6.40 mm 装不进 7.30 mm 镜脚 ⇒ 电芯段 H 链最坏 −1.10 mm
下一步: main 独立签收 ISS-387/388/389 三单 (闸 rc=0 + selftest 末行 ALL TESTS PASS + 闸自己的 selftest 在两个 TMPDIR 深度下都绿 + 板三项指纹未动) ⇒ 三条腿结论并进「板只改一次」同一趟一次做完 ⇒ 过 G1; 本 job 只落本地快照, 零外发, 不推 GitHub"""

head = """
### 本轮播报 (2026-11-24 09:46 · cron 5bd48f25 · 脚本输出全文 + 卡片正文)

★板面判据 ([板]+[布线]) 与上一条 (09:05 · facts 取自 09:04:46) 逐字相同 ⇒ 板面无变化; ★但签收/派活侧 09:05~09:46 有实质变化 ⇒ 本轮播报 ★
★① **main 09:24 独立签收 ISS-384/385/386 三单** (`state/_apply_20260724_0930_main_sign_iss384_385_386.py` · 台账 issue_log 384 条 · 三单 status=verified · 裁 18 条 main 地界待裁项 + 2 条老板域项转交 · 零写板/零落表/新闸零挂链 · 板三项指纹前后各打一次)
★② **775d9893 09:16~09:40 · 0 派** —— `advance.py --json` 实读: internal [] · approvals [] · decisions **53** (hw 13 / mech 15 / pm 12 / sw 13) · waiting [] ⇒ ★**根因形态第五次复核: 从「槽位被已交卷的 fixing 占住」变成【队列真空】(三总工 open=0 且 fixing=0)★** ⇒ 台账剩下 16 条 open 全是 owner=main (11) / owner=boss (5) ⇒ AGENT_ROLE 不含 main/boss ⇒ 一条都进不了 internal
★③ **决策页 §㊵ 追加 (09:36)** —— 老板清单覆盖 52→**53/53 零漏项** (一页 21/53 · 索引 41/53 · 并集 53/53) · 补的那 1 条 = `iss386_oi11_seat_height_h` (J_DEBUG/J_UART 座体真实高 h = [0数据] ⇒ 三档参数化 + 按 4.70 上界出件 + 1 台样件实测兜底, 不定版锁死) · 老字一字未删 (128,213→133,430 字符)
★④ **兄弟 job fb67af40 09:44 开 3 条新单并派出** (全部零写板): ISS-387(hw) 原厂 land 几何官网查证 + 对 MECH 3D 判据链的传感到影响面 · ISS-388(sw) 两道已签收 SW 闸实测坏了 ⇒ 把「闸的失效」变成可判的 · ISS-389(mech) 两连接器座体/开口/清空区结构侧收口作业包; brief 三份落 `state/dispatch_briefs/` (09:43) · check_brief_commands.py 三条 rc=0 · spawn 后 active=3 (每 agent 各 1 条)
★⑤ **本轮实跑撞出的真病灶 (不在任何 need 表里)** —— `check_debug_pin_order_contract.py --selftest` 10/11 FAIL (默认 TMPDIR=/tmp ⇒ 沙盒 ROOT 退成 `/`) vs `TMPDIR=$PWD/tmp` 11/11 PASS ⇒ 环境敏感不是判据敏感 · `check_sw_board_md5_rebase_readiness.py --selftest` 0/10 + 裸跑 5/7 rc=1 (H1/H4 = 账本没跟上) ⇒ 两道闸都零挂链 ⇒ 巡检全绿看不见
★⑥ **5 连门禁 (775d9893 实跑 rc)**: merge 0 · gate_check 0 (Q1 18/18 · Q2 3/3 · Q6 ✅ · Q7 10/10 · 缺口 3) · issue_check 1 (违规 19 条 · 全是既有逾期老账 · 本轮零新增) · stage_gate 1 (G1 · 还差 1 项 = unc 45→0 · G1a 还差 2 条 G1a-4/G1a-8) · daily_check 3 (三条老异常) ⇒ 板面零变化 (md5 611b869e… / mtime 11-06 07:07:17 / size 4940213 · 18 天逐字节未动) ⇒ **G1 仍开, 不许投板**
★已落盘: `state/.verify/_bcast_facts_20260724_0946.txt` · MEMORY.md 实时块 (update_progress_block.py) · `PROGRESS_SNAPSHOT.md` (gen_progress_snapshot.py) · 零外发 (微信通道已删) · 零写板 · 不推 GitHub (由 5 小时同步 job 负责)

```
%s
```

### 本轮卡片正文 (2026-11-24 09:46 · 落进主会话 sessions_send → agent:main:main)
```
%s
```
""" % (facts, card)

with io.open(MEM, "a", encoding="utf-8") as f:
    f.write(head)

print("appended bytes:", len(head.encode("utf-8")))
print("memory file size:", os.path.getsize(MEM))
