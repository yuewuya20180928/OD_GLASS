# ISS-312 · sw-lead 任务书 —— ★★【ISS-309 的 need 落地: 权威判据「链头落表单号」漏放 ⇒ 修判据 + 3 条反向用例 (★本单是 main 对 ISS-309 need 的拍板落地★)】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-312
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**性质**: ★**内部活 · 判据修复类 (SW 侧)** ★
> ★**边界 (硬)**: ★**零写板 · 零落表 · 零改网表真源 · 零改 `state/gate_check.py` · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★1 · 病灶 (★ISS-309 已 verified · main 05:5x 本机实跑复核★) ★

★**ISS-309 交付的结论 (已 verified)**: ★**R5a 是【真判据缺陷·漏放】而不是夹具假伤** ★
★**它交出来的实测 (main 05:4x 本机复跑 `python3 SW/tools/check_demo_panel_spec_r6_selftest.py` ⇒ rc=0 · 7/7 ✅)**: ★

```
覆盖缺口诊断 (★ISS-309 · 已登记 need · 本单不改判据★):
  场景: 锚点副本 e06c1dd63356/ISS-257 (★停在历史值★) · 链头 6aee500e60ba/['ISS-302']
  ⇒ ★★判据对【链头落表单号】只有「非空」这一道检查 ⇒ 没有任何交叉核对 ★★
  变体 ① 只改一处 (⇒ 台账自相矛盾): 改了 1 处 ⇒ 链头产出单号 = ['ISS-302','ISS-999'] ⇒ 判据: ★绿 (无红项) ⇒ ★漏放★
  变体 ② 每一处都改 (⇒ 台账自洽但单号是假的): 改了 2 处 ⇒ 链头产出单号 = ['ISS-999'] ⇒ 判据: ★绿 (无红项) ⇒ ★漏放★
```

★**⇒ 病灶一句话**: ★**权威判据 `SW/tools/check_demo_panel_spec.py` 对【链头落表单号】只查「非空」⇒ 单号被改坏 (假号 / 多个号 / 与真源不一致) 一律判绿 ⇒ 这是漏放 (假绿), 必须修** ★

---

## ★2 · 本单要做什么 (★main 拍板口径: 修法 = A + B 都要★) ★

★**ISS-309 交了三选一 (A / B1 / B2) 给 main 拍; ★**main 拍: ★**A + B 一起做** ★** —— 因为: ★**A 治「台账自相矛盾」(变体①) · B 治「台账自洽但单号是假的」(变体②) · 只做 A 治不了变体②, 只做 B 治不了多值★** ★

| 修法 | 内容 (★ISS-309 原话逐字★) | 本单落地要求 |
|---|---|---|
| ★**A** ★ | ★**判据加【链头产出单号不唯一 ⇒ 判红】 (⇒ 治变体①)★** | ★**必须加** ★ |
| ★**B** ★ | ★**链头单号必须与【独立信源】对上 (⇒ 锚点副本每次落表都跟到链头 / 或查 issue_log 真单号)★** | ★**必须加** ★ |

★**★B 的「独立信源」口径 (★本单最重要的一条纪律·不许偷懒★)★**:
★**信源必须独立于被测对象** ⇒ 具体: ★**链头落表单号 ↔ `state/issue_log.yaml` 里该单的真实 status / 落表记录** ★
★**绝对不许**: ★**拿「桶名拼写」当反向用例 (★ISS-308 那次踩过: 改了桶还判绿⇒闸形同虚设★)· 不许拿判据自己判自己 · 不许拿「同一份台账的两个副本」互证 (★那还是自证★)** ★

---

## ★3 · 交卷物 (4 件) ★

1. ★**改 `SW/tools/check_demo_panel_spec.py`** (★**只改 `check_r6_hard_protected()` 里【链头落表单号】那一段** ★ · 加 A + B 两道检查 · ★**改前先留一份 `SW/tools/check_demo_panel_spec.py.bak_iss312` (★可回退★)** ★)
2. ★**新建 `SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py`** (★**★新增 3 条反向用例 (★本单的核心价值★)★**: ★**① 把链头单号改坏 ⇒ 必须判红** ★ · ★**② 造一个不存在的 ISS 号 ⇒ 必须判红** ★ · ★**③ 把真单号换成另一个【真实存在但对不上】的 ISS 号 ⇒ 必须判红** ★ · ★**④ 原样不改动 ⇒ 必须判绿 (★不许把闸修成永远红★)** ★ · ★**★每条用例必须能证明「它抓的是交叉核对, 不是巧合」⇒ 变体①/②/③ 三条都要红★** ★)
3. ★**新建 `HANDOFF/2026-11-18_sw-lead_ISS312_R6判据漏放修复.md`** (★B1~B6 齐全 · 占位符 0 · ★**必含: 补丁前后【逐字输出 diff】+ 改判据前后 Q1/Q7 全绿证据 + 「是否挂进闸链」的建议 (★由 main 拍, 本单不挂★)** ★)
4. ★**`state/fragments/sw.yaml`** (★★**必须用 `python3 state/frag_write.py --agent sw-lead` 原子写 (★禁止 open(p,"w")★)★** · artifacts + needs_from · 只写自己那一份★)

★**★另交**: ★**`logs/iss312/`** (★改判据前后的原始输出 · 3 条反向用例的逐条判定 · 被测脚本与被测台账的 md5 前后值★) ★

---

## ★4 · 硬边界 (★违反即不算交卷★) ★

- ★**零写板**: 板 `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 (`611b869e13518c3c023fb178f91a0075`) + mtime (`2026-11-06 07:07:17`) 交卷前后逐字节相同 ⇒ **交卷页要贴这两个值** ★
- ★**零落表 / 零改网表真源**: 网表 / 脚表 / BOM / 落表台账 一律不动 ★
- ★**★不许改 `state/gate_check.py` (★挂不挂闸链由 main 拍★)** ★
- ★**★不许改 `SW/tools/check_demo_panel_spec_r6_selftest.py` (★它是本单的回归基线·动了就没有基线了★)** ★
- ★**★不许为了让闸变绿而改台账 / 改锚点副本 / 放宽判据 (★MEMORY 铁律: 排查类 bug 要修在产生点, 不许在产物上擦★)★** ★
  ⇒ ★**若加严之后现有链变红 ⇒ 【那说明它抓到了真的不一致】⇒ 老老实实把「红了 + 红的原因 + 该由谁修」写成交卷页的 need, 不许自己把红抹平** ★
- ★**零外发**: ★**不许发任何邮件 / 询价 / 问询 / 采购 (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ 外部依赖一律【自己网上查】+ 标证据等级 + 查不到就写降级方案** ★
- ★**不替老板拍板 · 不自签 issue_log** (★`state/issue_log.yaml` 只由 main 改★) ★
- ★**只写**: `SW/tools/` 下本单动的两个文件 + 备份 · `HANDOFF/` 本单交卷单 · `logs/iss312/` · `state/fragments/sw.yaml` (★经 frag_write.py★) ★

---

## ★5 · 交卷前必跑 (★把输出原样贴进回复★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_demo_panel_spec_r6_selftest.py        # ★回归基线: 必须 rc=0 · 7/7 (★不许动它★)
python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py   # ★本单新增: 必须 rc=0
python3 state/merge.py && python3 state/gate_check.py         # rc 必须 0 · Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb SW/tools/check_demo_panel_spec.py SW/tools/check_demo_panel_spec_r6_selftest.py
```

★**★额外纪律 (★与所有派活单同款★)★**: ① ★**写分片必须用 `state/frag_write.py` (禁止 open(p,"w"))** ★ ② ★**只写本任务允许的文件, 不碰别人的** ★ ③ ★**证据分级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` 必须标** ★ ④ ★**不许外发任何邮件/询价/问询/采购** ★ ⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★
