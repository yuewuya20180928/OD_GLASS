# ISS-392 · cont1 · sw-lead · 把「真相页 + 新闸已落盘」做到【交卷页占位符填实 + 分片登记 + 交卷消息】· 零写板 · 零落表 · 零改既有闸

★**本单 = ISS-392 cont1 (★不是新单 · 不是从零重做 · ★)** ★
★**本单 = 纯分析 + 新建闸 + 收尾 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【板那一趟·SW 侧护栏自守层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 14:45 起 · ★15:20 止 · 被 `runTimeoutSeconds` 掐死 (★状态 `timeout` · `abortedLastRun=true`★)** ★
★**子会话**: `agent:sw-lead:subagent:34d3606e-4aa5-43e6-8f16-f7bd802fecb8` / sessionId `34ab940c-f26f-4af4-b83-7035b69be78` ⇒ ★**掐死时它正处在【写交卷页 / 写分片】这两步之间**★

★★**★上一趟的产出: ★【真相页 + 新闸已落盘】, 但【交卷页没填实 + 分片零登记 + 交卷消息没有】★★** ★

| ★项★ | ★状态 (main 本机实读)★ | ★说明★ |
|---|---|---|
| ★**`SW/BOARD_ONEPASS_SW_GATE_CHAIN_COVERAGE.md`** ★ | ★**在盘** ★ | ★真相页 §0~§5 + 机器块齐全 (`--emit` 可解析)★ |
| ★**`SW/tools/check_sw_gate_chain_coverage.py`** ★ | ★**在盘** ★ | ★新闸 (★main 已实跑: ★**跑得动, 但很慢 ⇒ 见 §二 时间预算★)★ |
| ★**`HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md`** ★ | ★**在盘 (12,102 B) · 但 B6 里 4 个 `%%CMD_*%%` 占位符【一个都没替换】** ★ | ★★**`grep -c "%%CMD" ⇒ 4`** ★★ (L121 `%%CMD_NEWGATE%%` · L126 `%%CMD_EXISTING%%` · L131 `%%CMD_FINGER%%` · L136 `%%CMD_TAIL%%`) ★★ |
| ★**`state/fragments/sw.yaml` 的 ISS-392 登记** ★ | ★**0 条** ★ | ★`grep -c "iss392" state/fragments/sw.yaml` ⇒ **0** · ★`grep -c "ISS-392" state/fragments/sw.yaml` ⇒ **0**★ |
| ★**交卷消息** ★ | ★**没有** ★ | ★上一趟被掐死前没发出来★ |

★★**★main 本机已复核过的读数 (★你要自己再跑一遍, 别只抄本表★)★★** ★★

```
$ grep -c "%%CMD" HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md
4
$ grep -n "^## " HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md
6:## B1 结论摘要 (一句话结论)
14:## B2 验收标准自评 + 真相页 (路径 / 指纹 / 规模 / §0~§5)
38:## B3 证据分级 + 新闸 (路径 / 指纹 / 规模 / C0~C6 / selftest 用例数)
74:## B4 接口取值声明 + 边界自证
103:## B5 未决项与卡点 (要 main 回话的四条 · 每条带代价)
116:## B6 自证复现命令 (必跑命令原样输出)
⇒ ★★B1~B6 六段都在, 但 B6 是空的 (占位符) ⇒ ★★交卷页【没填实】★★

$ grep -c "iss392\|ISS-392" state/fragments/sw.yaml
0
⇒ ★★分片零登记 ⇒ ★★本单的产出物 / interface_claims / needs_from ★★【一条都没进项目台账】★★

$ python3 SW/tools/check_sw_gate_chain_coverage.py
★★★⚠ 这道闸【很慢】: main 实跑 180 秒【没跑完】(timeout 124) ⇒ ★★你必须给它更长的墙钟, 并把完整输出落盘★★★
```

★★**★main 本机实读出的一个必须点名的事实 (★你不用重找, 但要自己复核·★)★★** ★★
★**ISS-388 的元闸 `SW/tools/check_sw_gate_health.py` 交卷页说「SW 域共 13 道闸」, 而本单真相页 §1 说「盘上 31 道」⇒ ★**这两道闸互相看不见对方的 roster ⇒ 本单把三本账 (31 / 6 / 13) 的差集摆出来是对的, 但【两本账的数为什么对不上】这件事本身, 本单有没有回答? ★**★ **(★如果没有 ⇒ 在 §5 或 B5 里点名, 别装作没有★)**

---

## ★★二 · 本趟的时间预算 (★本项目子会话的真实墙 ★★runTimeout 3600s = 60 分钟★★) ★★

★★**★上一趟 35 分钟被掐死在【收尾】上 ⇒ 本趟【必须先落盘再验证】★★ ★★**

★**顺序不许改 (★每一步都落盘★)**:
1. ★**第 1 步 (≤10 分钟) · 跑闸并留证**: 跑新闸裸跑 + `--selftest` ⇒ ★**原样输出落 `logs/iss392/cont1_verify.log`** ⇒ ★**这道闸慢 ⇒ 给它 `timeout 1800` 以上, 别用 180★**
2. ★**第 2 步 (≤10 分钟) · 填实交卷页 B6**: ★**把 4 个 `%%CMD_*%%` 占位符替换成真实命令输出** ⇒ ★**只【追加/替换占位符】, 不许删改 B1~B5 正文★** ⇒ ★**替换后 `grep -c "%%CMD" <交卷页>` 必须 = 0 (★这条要写进 B7 自证★)★**
3. ★**第 3 步 (≤15 分钟) · 写分片**: ★**走 `state/frag_write.py --agent sw-lead`** ⇒ 登记 ★**产出物 (真相页 + 新闸 + 交卷页 + 日志) + interface_claims (★至少覆盖: 新闸的挂链状态 / 覆盖率的数 / v1-vs-v2 的差集 / 第三道病闸的基线漂移读数★) + needs_from (★要 main 回话的, 每条带代价★)★** ⇒ ★**写完 `grep -c "iss392" state/fragments/sw.yaml` 必须 ≥1, 且条目唯一 (★不许重复★)★**
4. ★**第 4 步 (≤10 分钟) · 交卷消息**: ★**发交卷消息 (B1~B7 齐全 · B7 = 本趟补的「占位符填实 + 分片登记 + 自证」段)★** ⇒ ★**消息里必须逐字贴出 4 条必跑命令的 rc★**

★★**★超时纪律 (★上一趟就是死在这★)★**: ★**第 2 步和第 3 步做完之前, 绝对不要去跑长命令** ★ ⇒ ★**新闸那一次长跑放在第 1 步, 且必须带 `nohup`/后台 + 日志落盘, 跑完再回来看结果** ★

---

## ★★三 · 本趟的必跑命令 (★main 已实跑过命令存在性守卫 rc=0★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 新闸裸跑 (★慢 ⇒ 给足墙钟★)
timeout 1800 python3 SW/tools/check_sw_gate_chain_coverage.py 2>&1 | tee logs/iss392/cont1_newgate.log
# ② 新闸自测
timeout 1800 python3 SW/tools/check_sw_gate_chain_coverage.py --selftest 2>&1 | tee logs/iss392/cont1_newgate_selftest.log
# ③ 板三项 + 三张表零扰动 + 零挂链
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
grep -c check_sw_gate_chain_coverage state/gate_check.py
# ④ 占位符填实 + 分片登记 自检
grep -c "%%CMD" HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md
grep -c "iss392" state/fragments/sw.yaml
# ⑤ 收尾
python3 state/merge.py
python3 state/gate_check.py
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-392_sw_gate_chain_coverage_cont1.md
```

★★**★板三项基线 (★本单全程必须逐字不变★)★**: ★板 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size `4940213` ⇒ ★**板 18 天逐字节未动, G1 仍开, 不许投板**★

---

## ★★四 · 纪律 (★照抄, 不许放宽★) ★★

★**零写板 · 零落表 · 零改既有闸的判据/阈值 · 零改既有页面正文 · 零挂链 (★挂不挂 `state/gate_check.py` 是 main 的地界★) · 零外发 (★无邮件/询价/问询/采购★) · 不代拍 (★挂链选项 / 基线通则 / 四条 need 的答复全是 main 的地界★) · 未自签 `state/issue_log.yaml` · 只写 `state/fragments/sw.yaml` (★走 `frag_write.py`·不碰别人分片★) · 沙盒只落 `tmp/iss392_sbx/` + `logs/iss392/` (★不落系统 `/tmp`★)** ★

★**★若你的新闸自己【跑不完】(★像 main 实跑那样 180 秒没完★) ⇒ ★**不许把超时说成「PASS」· 也不许把超时说成「FAIL」· 如实写「本闸在 main 的 180s 墙内未跑完, 本趟给了 1800s, 读数如下」★★**

---

## ★★五 · 交卷要求 (★gate_check 认的关键词全含★) ★★

★**交卷页 `HANDOFF/2026-11-24_sw-lead_ISS392_SW域闸门禁链覆盖率与第三道病闸基线漂移.md`**: ★**B1 结论摘要 / B2 验收标准自评 + 真相页 / B3 证据分级 + 新闸 / B4 接口取值声明 + 边界自证 / B5 未决项与卡点 / B6 自证复现命令 (★填实★) / B7 cont1 补记 (★占位符填实 + 分片登记 + 超时交代★)** ★

★**交卷消息里必须逐字给出**: ★**① 4 条必跑命令的 rc ② 板三项指纹前后对比 ③ `grep -c "%%CMD" ⇒ 0` ④ `grep -c "iss392" state/fragments/sw.yaml ⇒ ≥1` ⑤ 零挂链 `grep -c` 读数 ⑥ 要 main 回话的几条 (每条带代价, 不代拍)** ★
