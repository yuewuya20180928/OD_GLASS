# ISS-309 · sw-lead · ★★cont1 续做说明★★ (★僵尸 fixing 重派 · 不是从零重做★)

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-309
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 05:3x** ★
> ★**性质不变**: ★**内部活 · 纯分析 / 作业包类 · 零写板 · 零落表 · 零改既有判据阈值 · 零外发 · 不替老板拍板** ★

---

## ★0 · ★为什么有这张 cont1 (★main 05:3x 本机实跑, 不抄任何 agent 报告★) ★

★**上一趟子会话**: `agent:sw-lead:subagent:4f1fbe6b` (taskName `queue_iss309`) ⇒ ★**04:55:25 起 · 05:05:48 死** ★
★**死因**: ★**status=timeout · abortedLastRun=true** ⇒ ★**根因 = 父 cron run 结束时子会话被连带 abort (★与 ISS-308 第一趟同一个死法★)** ⇒ ⇒ ★**不是 sw-lead 的错, 是派活机制的错** ★
★**⇒ 上一趟 = 僵尸 fixing**: ★**0 件交付物落地** (★`HANDOFF/2026-11-18_sw-lead_ISS309_R6反向用例5of7归因.md` 不存在 · `state/fragments/sw.yaml` 里 `grep -c iss309` = 0★) ⇒ ⇒ ★**sw-lead 整个被挡 (★advance.py 的 in_flight 规则: 同 agent 名下有 fixing 单 ⇒ 本轮不再派新活★)** ★

★**★但是上一趟的分析成果【已经在盘上】(★main 05:3x 实读核对★) ⇒ ★**本单按【续做, 不是从零重做】处理** ★ ★

| 在盘成果 | 路径 | 内容 |
|---|---|---|
| ★**基线快照** ★ | `logs/iss309/01_before_r6_selftest.txt` | 修前 `SW/tools/check_demo_panel_spec_r6_selftest.py` 的完整实跑输出 (★5/7 通过★) |
| ★**10 件 md5 前值** ★ | `logs/iss309/02_md5_before.txt` | ★板 / `.kicad_pro` / 网表 / 脚表 / BOM / SW 台账 / 落表台账 / 权威判据 / `state/gate_check.py`★ |
| ★**★5 个场景探针 (★最值钱的一件★)** ★ | `logs/iss309/03_probe_r5a_r4_scenarios.txt` | ★**场景 A~E: 每个场景喂一份坏台账给 judge, 看 judge 判绿还是判红** ★ |

★**⇒ 本单的第一步 = 读那三个文件 (★别重跑一遍基线, 别重新想那 5 个场景★)** ★

---

## ★1 · ★★main 05:3x 读 `03_probe` 得到的一条【关键实测】(★你必须独立复核, 但别再从零推一遍★) ★★

★**场景 A (R5a 原样: 只把链头那一行的【显式】单号 `ISS-302` 改成 `ISS-999`)** ★
```
head=6aee500e60ba  head_iss=['ISS-302', 'ISS-999']  producer[head]=['ISS-302', 'ISS-999']
judge 判定: ★绿 (无红项)★
```
★**场景 B (台账里【所有】`ISS-302` 改成 `ISS-999`)** ★
```
head=6aee500e60ba  head_iss=['ISS-999']  producer[head]=['ISS-999']
judge 判定: ★绿 (无红项)★
```
★**★⇒ main 的读法 (★请复核后再采信, 别直接抄★): 链头的落表单号被改坏 (`ISS-302` → `ISS-999`) 之后, 【judge 自己没有判红】⇒ ⇒ R5a 的期望是「必须红」, 而判据在【单号被改坏】这个场景下【漏放】⇒ ⇒ 这不是「夹具假伤」, 这是【真判据缺陷】(★原任务书 §1-② 点名的「最要紧的一问」, 现在有实测证据了★)** ★
★**场景 C/D** = 对照组 (★把锚点副本的单号改坏 ⇒ judge 才红 ⇒ 说明 judge 确实有单号一致性检查, 只是【方向/覆盖面】有洞★) ★
★**场景 E** = R4 现状 (★合成台账只放网表行+脚表行 ⇒ 硬保护段查不到 ⇒ 判红 ⇒ 与原任务书 §1-② 的根因假设一致★) ★

★**★本单最重要的产出就是这一句: R5a 到底是【夹具假伤】还是【真判据缺陷】⇒ ★**三选一, 不许骑墙** ★**
★**★若你的结论 = 「真判据缺陷」⇒ ⇒ 修法必须是【修判据的漏放点】(★在产生点拦★), 不许把断言改松让它变绿 (★原任务书 §7 第 2 条的老教训: 「修夹具 ≠ 放宽判据」·「排查类 bug 要修在产生点, 不许在产物上擦」★)** ★
★**★但 ★★边界★: `SW/tools/check_demo_panel_spec.py` 里的 `check_r6_hard_protected()` 是【权威判据】, 本单不许动★ ⇒ ⇒ **若修判据必须改它 ⇒ 那就出 need 交 main (★挂闸/改判据都是 main 的活★), 不要自己改** ★** ⇒ ★**优先把修法落在【反向用例脚本自己的夹具/断言侧】(★`SW/tools/check_demo_panel_spec_r6_selftest.py` 是本单的产物, 可改★)** ★

---

## ★2 · ★续做清单 (★按这个顺序做, 先交卷再完美★) ★

1. ★**读** `logs/iss309/01_before_r6_selftest.txt` + `02_md5_before.txt` + `03_probe_r5a_r4_scenarios.txt` (★3 个文件, 别重跑基线★) ★
2. ★**先 `write` 建交卷单骨架** ★ `HANDOFF/2026-11-18_sw-lead_ISS309_R6反向用例5of7归因.md` (★哪怕只写标题 + B1~B6 六个小标题 + 交付物清单★) ⇒ ★**★纪律: 上一趟就是「0 件交付物」死掉的 ⇒ 这次先落骨架★** ★
3. ★**复核** §1 那条关键实测 (★自己跑一遍 judge, 看是不是真漏放★) ⇒ ★**定性 R4 / R5a (★三选一★)** ★
4. ★**修** (★只许修夹具/用例侧; 权威判据要动 ⇒ 出 need 给 main★) ⇒ ★**修完必须【再故意坏一次】证明它仍然能抓** (★原任务书 §7 第 3 条★) ★
5. ★**出判决**: ★**该闸该不该进 `state/gate_check.py` 门禁链** ⇒ ★**只出结论 + 建议挂入位置, 不许自己改 `state/gate_check.py`★** ★
6. ★**落分片**: `state/frag_write.py --agent sw-lead` (★禁止 `open(p,"w")`★) ⇒ ★**needs_from (若要 main 答) / interface_claims / artifacts 三样都写★ ★
7. ★**交卷** (★B1~B6 齐全 + 占位符 0★) ⇒ ★**贴原始输出, 不许只写结论★** ★

---

## ★3 · ★★时间纪律 (★上一趟 10 分钟就死了 ⇒ 这条最要紧★) ★★

| 纪律 | 为什么 |
|---|---|
| ★**长任务一律 `nohup ... > logs/iss309/<x>.log 2>&1 &` + 短轮询** ★ | ★**前台长 exec = 被掐的头号原因** (★原任务书 §纪律同款★) ★ |
| ★**单条 `exec` ≤ ~120 秒** ★ | 同上 |
| ★**每 10 分钟至少一次写盘** ★ | ★**子会话被连带 abort 时, 只有落盘的东西还在** ★ |
| ★**每落一件交付物就把 rc 追加进交卷单** ★ | 同上 |
| ★**分片写完 `grep` 校验** ★ | 防止半截 YAML |
| ★**不要在本单里重跑全仓门禁链** ★ | `state/gate_check.py` 要 1~2 分钟 ⇒ 放后台跑 + 读日志 |

---

## ★4 · ★边界 (★与原任务书 §5 完全一致, 不许放宽★) ★

| 边界 | 怎么自证 |
|---|---|
| ★**零写板** ★ | ★板 / `.kicad_pro` md5 + mtime 两条都贴 (★对照 `logs/iss309/02_md5_before.txt`★)★ |
| ★**零落表** ★ | ★网表 / 脚表 / BOM / 落表台账 md5 对回 `02_md5_before.txt` 的现值★ |
| ★**零改权威判据** ★ | ★`SW/tools/check_demo_panel_spec.py` md5 交卷前后逐字节不变★ |
| ★**零改 SW 台账锚点** ★ | ★`SW/SW_MD5_BASELINE_LEDGER.md` md5 逐字节不变★ |
| ★**零改 `state/gate_check.py`** ★ | ★挂闸是 main 的活 ⇒ ★**本单只出结论 + need** ★ |
| ★**零改 `HW/` 与 `MECH/`** ★ | ★**hw-lead 在飞 ISS-308 cont1 · mech-lead 本轮另有活 (ISS-310)** ⇒ ★**只写 `state/fragments/sw.yaml` + `SW/` 与 `HANDOFF/` 与 `logs/iss309/`★ ★ |
| ★**零外发** ★ | ★没发任何邮件 / 询价 / 问询 / 采购 ⇒ ★**缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案** ★ |
| ★**不替老板拍板** ★ | ★§2-C 只给结论 + 代价 + 风险, 挂不挂归 main★ |
| ★**不自签 issue_log** ★ | ★不写 `state/issue_log.yaml`★ |

---

## ★5 · ★自证命令 (★交卷前逐条跑, 原始输出贴进交卷单 B4★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_demo_panel_spec_r6_selftest.py ; echo "rc=$?"          # ★期望 rc=0 ★
python3 SW/tools/check_demo_panel_spec.py ; echo "rc=$?"                    # ★期望 rc=0 ★(权威判据不许被改坏)
python3 state/merge.py ; echo "rc=$?"                                       # ★期望 rc=0 ★
python3 state/gate_check.py ; echo "rc=$?"                                  # ★期望 rc=0 · Q1 18/18 ★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
       SW/SW_MD5_BASELINE_LEDGER.md HW/SCHEMATIC_LANDING_V1_LANDED.md \
       SW/tools/check_demo_panel_spec.py state/gate_check.py                # ★与 02_md5_before.txt 逐行对比★
grep -c iss309 state/fragments/sw.yaml                                      # ★期望 ≥1 ★
grep -cE "🔄|待填" HANDOFF/2026-11-18_sw-lead_ISS309_R6反向用例5of7归因.md   # ★期望 0 ★
```

---

## ★6 · ★★外发口径 (★老板 2026-11-11 19:31 + 2026-11-12 02:02·硬规则★) ★★

★**不许外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询 / 任何对外沟通** ⇒ ★**没有「老板批一句可以发」这个选项** ⇒ ★**查不到就写 `[0数据]` + 降级方案 (★实测样件 / 选官网参数直接满足的替代型号 / 改设计路径绕开它★)** ⇒ ★**本单不依赖任何外部回复** ★
★**证据等级固定用**: `[官网]` (厂商官网/官方 datasheet) / `[实测]` (本机可复现) / `[媒体]` / `[推算]` / `[0数据]` (查不到) ★
