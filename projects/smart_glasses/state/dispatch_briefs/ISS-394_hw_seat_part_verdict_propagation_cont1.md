# ISS-394 · cont1 · hw-lead · 把「真相页 + 新闸已落盘」做到【交卷页 + 分片 + 交卷消息】· 零写板 · 零落表 · 零改既有闸

★**本单 = ISS-394 cont1 (★不是新单 · 不是从零重做 · ★)** ★
★**本单 = 纯分析 + 新建真相页 + 新建机器闸 + 收尾 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【板那一趟·HW 侧选型结论传播自守层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 14:45 起 · ★15:15 止 · 被 `runTimeoutSeconds` 掐死 (★状态 `timeout` · `abortedLastRun=true`★)** ★
★**子会话**: `agent:hw-lead:subagent:557dc7a1-9440-480b-adab-92887eba7856` / sessionId `94acd096-afbc-4694-b4b5-ec4f9e6f4558` ⇒ ★**掐死时它正处在【真相页与新闸刚落盘 · 交卷页还没写】这一步★**

★★**★上一趟的产出: ★【真相页 + 新闸已落盘】, 但【交卷页零 · 分片零登记 · 交卷消息没有】★★** ★

| ★项★ | ★状态 (main 本机实读)★ | ★说明★ |
|---|---|---|
| ★**`HW/PCB/BOARD_ONEPASS_SEAT_PART_VERDICT_PROPAGATION.md`** ★ | ★**在盘** ★ | ★真相页 §0~§6 + 机器块齐全 (`--emit` 可解析)★ |
| ★**`HW/check_seat_part_verdict_propagation.py`** ★ | ★**在盘** ★ | ★新闸 K0~K6 ⇒ ★**main 实跑 rc=1, 4/7 绿 (K1/K2/K3 红) ⇒ 【红的是现状, 不是闸故障】★** ★ |
| ★**`HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md`** ★ | ★**不在盘** ★ | ★★**交卷页【一个字都没写】** ★★ (★`ls -t HANDOFF/ \| head` ⇒ 最新是 ISS-391 那份·★本单没留下任何东西★)★ |
| ★**`state/fragments/hw.yaml` 的 ISS-394 登记** ★ | ★**0 条** ★ | ★`grep -c "iss394" state/fragments/hw.yaml` ⇒ **0** · ★`grep -c "ISS-394" state/fragments/hw.yaml` ⇒ **0**★ |
| ★**交卷消息** ★ | ★**没有** ★ | ★上一趟被掐死前没发出来★ |

★★**★main 本机已复核过的读数 (★你要自己再跑一遍, 别只抄本表★)★★** ★★

```
$ python3 HW/check_seat_part_verdict_propagation.py ; echo "rc=$?"
  [K0] ✔ GREEN ...
  [K1] ✘ RED  ★命门★ ... L67 / L73 / L112 仍以【首选 / 板侧真值档】的身份主张被推翻的料号
  [K2] ✘ RED  ★命门★ 已闭 need 的答案不许指向被推翻的料号 (key='iss377_oi10_vendor_part_numbers')
  [K3] ✘ RED  ★命门★ 未答 need 的选项里必须至少有一个满足板侧真值档 (key='iss380_board_trip_bom_part_fill')
  [K4] ✔ GREEN 正确结论已登记 + 带证据等级 + 全部 not_decided_here
  [K5] ✔ GREEN 证据分级 / 零挂起 / 零挂链 / 判据与事实分开
  [K6] ✔ GREEN 既有件零扰动 + 机器块三字段 none
══ ISS-394 座体选型结论传播自守闸: 4/7 条绿
❌ 有 3 条判据红
★红的是【现状】, 不是闸故障:
  K1 = 被推翻的料号仍以「首选/真值档」身份活在活副本里 ⇒ 要 main 落订正块
  K2 = 已闭 need 的答案仍指向被推翻的料号 ⇒ 要 main 落订正块
  K3 = 未答 need 的选项全错 ⇒ 要 main 改选项 (改选项 ≠ 答这条 need)
★main 落完那 5 处订正 + 把机器块 protected_files / live_copies 同步 ⇒ 同一条命令即转绿
rc=1
```

★★**★★main 最重要的一句提醒 (★本单最容易踩的坑★)★★** ★★
★**K1/K2/K3 这三条红, 要修的是【活副本】(★`HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md` L18/L62/L67/L73/L112 · `state/fragments/hw.yaml` L5271-5272 · L4346-4347 · L8097 · `HW/check_debug_uart_seat_alignment.py` L397★) ⇒ ★★**那是 main 的地界 (★改既有页面正文 / 改分片里已闭答案 / 改已签收闸源码★) ⇒ ★★你【不许】去动它们** ★★ ⇒ ★★**你这一趟的活是【把病灶清点 + 闸 + 交卷】, 不是【把病灶修掉】** ★★ ★★ ★★**★你要是把 K1/K2/K3 改成绿了, main 反而看不出你交的是什么 ⇒ 你要交的是【红的读数 + 每处该改什么 + 代价】★★** ★

★★**★main 本机实读出的一个必须点名的事实 (★不用重找, 但要自己复核·★)★★** ★★
★**你上一趟的真相页 §1 里记了一条降级**: `FTSH-102-01-F-DV` 的官网单品页 ★**两次 HTTP 429 (Cloudflare 1015 限流) ⇒ 降级读盘上已签收页 L47 的逐字记录★** ⇒ ★★**这条降级在 §3「本单独立复核」里是否被点名? ⇒ 若你的结论把 `FTSH-102-01-F-DV` 也判成「被推翻」⇒ 那它的证据等级是【官网记录转述】而不是【本单直抓】⇒ ★★**你在交卷页 B3 里必须把这个证据等级差写清楚** ★★**

---

## ★★二 · 本趟的时间预算 (★本项目子会话的真实墙 ★★runTimeout 3600s = 60 分钟★★) ★★

★★**★上一趟 30 分钟被掐死在【交卷页那一步】⇒ 本趟【必须先落盘再验证】★★ ★★**

★**顺序不许改 (★每一步都落盘★)**:
1. ★**第 1 步 (≤10 分钟) · 跑闸并留证**: 跑新闸裸跑 + `--selftest` ⇒ ★**原样输出落 `logs/iss394/cont1_verify.log`** ★
2. ★**第 2 步 (≤20 分钟) · 交卷页 (★★先写文件落盘, 再补内容★★)**: ★**新建** `HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md` (★B1~B6 齐全 + ★B7 cont1 补记★) ⇒ ★★**这一件必须在本趟【前 40 分钟内】落盘 ⇒ 不许放到最后★** ★
3. ★**第 3 步 (≤15 分钟) · 写分片**: ★**走 `state/frag_write.py --agent hw-lead`** ⇒ 登记 ★**产出物 (真相页 + 新闸 + 交卷页 + 日志) + interface_claims (★至少覆盖: 被推翻的料号 / 5 处活副本的清单 / 新闸的 7 条判据与当前读数 / `not_decided_here` 不代拍★) + needs_from (★要 main 回话的, 每条带代价★)★** ⇒ ★**写完 `grep -c "iss394" state/fragments/hw.yaml` 必须 ≥1, 且条目唯一★**
4. ★**第 4 步 (≤10 分钟) · 交卷消息**: ★**发交卷消息 (B1~B7 齐全 · 含 4 条必跑命令的 rc)★**

★★**★超时纪律 (★上一趟就是死在这★)★**: ★**第 2 步和第 3 步做完之前, 绝对不要去跑长命令** ★

---

## ★★三 · 本趟的必跑命令 (★main 已实跑过命令存在性守卫 rc=0★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 新闸裸跑 (★预期 rc=1 = 现状红, 不是闸故障★)
timeout 600 python3 HW/check_seat_part_verdict_propagation.py 2>&1 | tee logs/iss394/cont1_newgate.log
# ② 新闸自测
timeout 600 python3 HW/check_seat_part_verdict_propagation.py --selftest 2>&1 | tee logs/iss394/cont1_newgate_selftest.log
# ③ 板三项 + 三张表零扰动 + 零挂链
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
grep -c check_seat_part_verdict_propagation state/gate_check.py
# ④ 交卷页 + 分片登记 自检
ls -la HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md
grep -c "iss394" state/fragments/hw.yaml
# ⑤ 收尾
python3 state/merge.py
python3 state/gate_check.py
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-394_hw_seat_part_verdict_propagation_cont1.md
```

★★**★板三项基线 (★本单全程必须逐字不变★)★**: ★板 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ ★**板 18 天逐字节未动, G1 仍开, 不许投板**★

---

## ★★四 · 纪律 (★照抄, 不许放宽★) ★★

★**零写板 · 零落表 · 零改既有闸的判据/阈值 (★★包括 `HW/check_debug_uart_seat_alignment.py` L397 那个硬编码样本——★**它是被推翻的料号, 但它是 main 的地界, 你只登记不修**★★) · 零改既有页面正文 (★★包括 `HW/PCB/BOARD_ONEPASS_DEBUG_UART_SEAT_PART_TRUTH.md`——★**同上, 你只清账不修**★★) · 零挂链 (★挂不挂 `state/gate_check.py` 是 main 的地界★) · 零外发 (★无邮件/询价/问询/采购★) · 不代拍 (★BOM 型号栏填哪颗是 main+boss 的地界·★机器块三字段保持 `none`/`not_decided_here`★) · 未自签 `state/issue_log.yaml` · 只写 `state/fragments/hw.yaml` (★走 `frag_write.py`·不碰别人分片★) · 沙盒只落 `tmp/iss394_sbx/` + `logs/iss394/` (★不落系统 `/tmp`★)** ★

---

## ★★五 · 交卷要求 (★gate_check 认的关键词全含★) ★★

★**交卷页 `HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md`**: ★**B1 结论摘要 / B2 验收标准自评 + 真相页 (路径 / 指纹 / 规模 / §0~§6) / B3 证据分级 + 新闸 (路径 / 指纹 / 规模 / K0~K6 / selftest 用例数 / ★★K1-K3 三条红的【逐条读数 + 该谁修 + 代价★★) / B4 接口取值声明 + 边界自证 / B5 未决项与卡点 (要 main 回话的, 每条带代价) / B6 自证复现命令 (必跑命令原样输出) / B7 cont1 补记 (★上一趟怎么死的 + 本趟补了什么)** ★

★**交卷消息里必须逐字给出**: ★**① 4 条必跑命令的 rc (★新闸 rc=1 要**如实写成「预期红=现状」★, 不许写成 PASS★) ② 板三项指纹前后对比 ③ `grep -c "iss394" state/fragments/hw.yaml ⇒ ≥1` ④ 零挂链 `grep -c` 读数 ⑤ 要 main 回话的几条 (每条带代价, 不代拍) ⑥ ★**你**没有去修那 5 处活副本的边界自证** ★
