# ISS-388 · cont2 · sw-lead · 把「两道已签收 SW 闸今天真的坏了」从【两件交付物已在盘 · 闸有 2 处实测假阳性 · 交卷页与分片零在盘】做到【闸真能挂 · 交卷页 B1~B6 齐全 · 分片登记 · 交卷】· 零写板 · 零落表 · 零改既有闸

★**本单 = ISS-388 cont2 (★不是新单 · ★上一趟半途死在 provider abort · ★)** ★
★**本单 = 纯分析 + 新建闸 + 诊断 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【护栏自检层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★
★★**★本单的真正价值 (★为什么它必须做完★): ★**这两道闸在「板只改一次」那一趟里各自把关什么** (★`check_debug_pin_order_contract` = 物理针序契约; ★`check_sw_board_md5_rebase_readiness` = 板 md5 引用面自守 ⇒ ★**它们一旦烂掉, 那一趟就没有护栏**★) ★★ ★★

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 11:04:38 起 · 11:14:49 止 · 墙钟 10.2 分钟** ★
★**子会话** `agent:sw-lead:subagent:8666b4fa-3bc6-4ad9-bd0f-6fde39128e6c` / sessionId `e7818570-6715-4047-b1d5-ceb526e63531` / runId `399e043d-2da6-4d05-9bc8-89e257a78ca4` ★
★**死因 = ★★provider 级 abort (★不是超时, 不是墙★)★★**: transcript 最后一条是 `openclaw:prompt-error` → `error: 'This operation was aborted | This operation was aborted'` (provider `minimax` / model `minimax/MiniMax-M3.1-Flash` / api `anthropic-messages`) ⇒ ★**transcript 98 行, 死在【写/改新闸源码】那一次 tool_call 前后** ★★

★★**★上一趟的产出: 两件交付物【已在盘】· 两件【零】在盘 ★★**

| ★项★ | ★状态★ | ★main 本机实测读数 (★11:2x~11:4x★) ★ |
|---|---|---|
| ★**`SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md`** ★ | ★**已在盘** ★ | ★**20,941 B @ 11:09** ★★别重做★ ★ |
| ★**`SW/tools/check_sw_gate_health.py`** ★ | ★**已在盘** ★ | ★**30,823 B @ 11:11** · ★**语法 OK (compile 通过)** · ★**`--selftest` ⇒ 22/22 通过 · 末行 `ALL TESTS PASS` · rc=0** ★ ★★别重做★ ★ |
| ★**`HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md`** ★ | ★**不在盘** ★ | ★**本趟必须新建 (★★新闸的 H5 判据写死了这个路径 ⇒ 不写它 H5 必红★★)** ★ |
| ★**`state/fragments/sw.yaml` 的 ISS-388 登记** ★ | ★**0 条** ★ | ★`grep -c iss388 state/fragments/sw.yaml` = **0** ★★本趟必须写★ ★ |

★**★main 本机已复核过的读数 (★你开工要自己再跑一遍, 别只抄本表★) ★★** ★★

```
$ python3 SW/tools/check_sw_gate_health.py --selftest          ⇒ rc=0
    === selftest 22/22 通过 (共 22 条反向用例, 其中专打 H1 命门 5 条) ===
    ALL TESTS PASS

$ python3 SW/tools/check_sw_gate_health.py                       ⇒ rc=1  ★★裸跑红★
    闸结果 1/6 通过
    [FAIL] H0 · check_sw_board_md5_rebase_readiness.py 的 --selftest rc=1 (0/10) ⇒ 判红
    [FAIL] H0 · SW/tools/check_sw_ref_reachability_v2.py 的 --selftest rc=1 (0/10) ⇒ 判红
    [FAIL] H1 · check_debug_pin_order_contract.py 两个 TMPDIR 深度下 rc 不同 (0 vs 1) ⇒ 环境耦合
    [FAIL] H1 · check_sw_board_md5_rebase_readiness.py 两深度 --selftest 输出【逐字不同】
           ⇒ 首个不同的行: 深度A='⚠ H6: ★板 mtime=2026-11-24 11:13:21.502534330 ≠ 基线 2026-11-06 07:07:17.362193413'
                            深度B='⚠ H6: ★板 mtime=2026-11-24 11:13:29.515367442 ≠ 基线 ...'
    [FAIL] H1 · SW/tools/check_sw_ref_reachability.py / SW/tools/check_sw_ref_reachability_v2.py 两深度输出【逐字不同】
           ⇒ 首个不同的行: 深度A='沙盒根: <SBX>/iss318_<SBX>' vs 深度B='沙盒根: /home/.../tmp/iss318_tmp'
    [FAIL] H2 · SW/tools/check_sw_false_connectivity_gate.py 硬钉了板 md5 但没进 ISS-372 §2 的账 ⇒ 判红
    [FAIL] H3 · SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23/:241 + SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215
           三行板 md5 引用面没进 §1 的账 ⇒ 判红
    [PASS] H4 · 板三项指纹未动 + 零落表 + 零挂链
    [FAIL] H5 · 交付页 SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md 用了证据等级 '['H1']' / '[2a]' / '[2b]' /
           '[Errno 2]' / '[FAIL]' / '[PASS]' 不在五级白名单 ⇒ 判红
    [FAIL] H5 · 交付页 HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md 不存在 ⇒ 判红
```

★★**★★main 本机实读的根因 (★因果链你要自己复核一遍, 但别重找★) ★★ ★★
★**闸 1 (`check_debug_pin_order_contract.py`)**: ★**该闸的 `ROOT` 是从 `__file__` 往上退两级算出来的 ⇒ M2 反向用例把闸源码复制到【沙盒目录】再跑 ⇒ 副本的 `ROOT` 就跟着沙盒目录走 ⇒ 沙盒落在 `/tmp` 时 `ROOT` 退成 `/` ⇒ 它去找 `/SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` ⇒ 不存在 ⇒ FATAL** ★
★★**闸 2 (`check_sw_board_md5_rebase_readiness.py`)**: ★**H1/H4 判红是因为【ISS-381 新建的 `SW/tools/check_sw_false_connectivity_gate.py` 硬钉了板 md5, 且 ISS-381/ISS-385 新建的两份页面里也有板 md5 字面量】⇒ 它们都没进 ISS-372 真相页的 §1/§2 账 ⇒ ⇒ H1/H4 判红【不是闸坏了】, 是【账本没跟上】—— 这两条判据本来就是干这个用的** ★★ ⇒ ★**真正的病灶是: 当 SW 域【新增一道钉板 md5 的闸】时, 没有任何机制提醒「§2 的账要跟着登记」⇒ 账与现实漂移 ⇒ 闸自己判红 ⇒ 而它【零挂链】⇒ 这条红没人看见 ⇒ 它就这么烂在盘上** ★★

---

## ★★二 · ★★main 本机实测出来的【两处假阳性】(★本趟必须修在【产生点】= 新闸自己★) ★★

★★**★这两处是本单最值钱的部分: 你不是去把那两道病闸修绿, 你是去修【你的新闸】误判它们★** ★★

### ★★病灶 A (★假阳性 1) · H5 的证据等级扫描【正则太宽】⇒ 把普通方括号 token 当成"证据等级" ★★

★**本机实读**: `SW/tools/check_sw_gate_health.py` **L116** = `EV_TOKEN_RE = re.compile(r"\[[^\]\[]{1,12}\]")` ⇒ ★**它匹配页面上【任何】1~12 字符的方括号内容** ⇒ ★**于是诊断页正文里写的 `[H1]` / `[2a]` / `[2b]` / `[Errno 2]` / `[FAIL]` / `[PASS]` 全被当成"作者声称的证据等级" ⇒ 判红** ★
★★**★这是判据本身写宽了, 不是页面写错了 ★★** ⇒ ★**修法 = 把"证据等级"判据改成【只认真正的等级标记】, 而不是"页面上所有方括号"** ★
★★**★现成形状照抄 (★本机实读, 同域同作者谱系★)★**: `SW/tools/check_sw_false_connectivity_gate.py` 的 **K6** 判据用的是【**逐段检查**「§0~§7 每段至少有一个五级白名单里的等级标记」】(★`EV_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")`★) ⇒ ★**那才是"证据等级白名单"的正确形状: 【白名单里的标记必须被认出来】, 而不是【白名单外的任何方括号都要被当成等级去骂】** ★★

### ★★病灶 B (★假阳性 2) · H1 的"两深度读数必须逐字相同"【比较基没归一沙盒量】⇒ 把沙盒自己产生的差异算成"环境耦合" ★★

★**本机实读** (`logs/iss388/gate_health_live_run1.log` 原文): ★**两处"逐字不同"的第一行差异, 都不是判据读数, 是【沙盒自己产生的东西】** ★
· ★**(甲)** `check_sw_board_md5_rebase_readiness.py` 的 `--selftest` 打印的是【**沙盒副本**的板 mtime】(★`2026-11-24 11:13:21` vs `11:13:29`★ ⇒ 两个深度各拷一次 ⇒ mtime 自然不同★) ⇒ ★**与判据无关** ★
· ★**(乙)** `SW/tools/check_sw_ref_reachability.py` / `SW/tools/check_sw_ref_reachability_v2.py` 打印的沙盒根路径两种写法 (`<SBX>/iss318_<SBX>` vs 真实绝对路径) ⇒ ★**与判据无关** ★
★★**★⇒ 本机实读你的 `normalize()` (★L167~L173★) 只替换了 `sbx_path` 本身和它的 basename ⇒ ★**替换不掉上面这两类形态** ⇒ ★**⇒ H1 现在会【永远红】, 哪怕被扫的闸是健康的** ★★

★★**★★★两处假阳性的共同后果 (★这才是本单真正的命门★) ★★★** ★★
★**你的新闸现在【裸跑恒红 (rc=1)】⇒ ⇒ 它【永远挂不进 `state/gate_check.py`】(★挂链要求 rc=0★) ⇒ ⇒ ★★**它就变成第二个"零挂链 ⇒ 没人看见 ⇒ 烂在盘上"的闸★ ⇒ ★★**你本单的活就白干了** ★★★**
★★**★⇒ 本趟必须让新闸【在今天这个"两道闸真的坏了"的世界上】有一个【能变绿】的读法, 同时【新的坏】仍然必红 ★★**

★**★现成形状照抄 (★本机实读, 同域★)★**: `SW/tools/check_sw_false_connectivity_gate.py` 有 `--phase pre` (默认, **今天 = 基线相, 期望绿**) 与 `--phase post` (**板那一趟验收相, 期望红**) ⇒ ★**⇒ 新闸照这个形状做: 【今天的已知坏状态登记成基线 ⇒ 基线相绿】+【任何【新的】坏 ⇒ 严格相红】** ★★ ★★
★★**★你的基线相必须把"今天已知的坏"显式列出来 (★就是上面 H0/H1/H2/H3 那几行真实病灶★) ⇒ 不许写死成空 ⇒ 不许"全绿就算过"** ★★

---

## ★★三 · 本单的地界事实 (★不许越★) ★★

★★**① 两道病闸【不许改】** —— ★**`SW/tools/check_debug_pin_order_contract.py` (ISS-375 签收件) 与 `SW/tools/check_sw_board_md5_rebase_readiness.py` (ISS-372 签收件) 的判据/阈值一个字都不许动** ⇒ ★**它们现在是红的, 那是【它们的正确行为】(★闸 1 = 环境耦合暴露; 闸 2 = 账本漂移暴露★) ⇒ ★★不许为了让它们变绿去改它们、去改阈值、去改 §1/§2 的账★★ ★
★★**② 本单只【新建/修】一道闸** ⇒ ★**`SW/tools/check_sw_gate_health.py` 是你本单的闸 (★已在盘, 本趟是【修它】不是【重写它】★) · ★**零挂链 (★`grep -c check_sw_gate_health state/gate_check.py` 必须 = 0 · 挂链是 main 的地界★)** ★
★★**③ 零挂链是本单的命根** —— ★**这两道闸烂掉的根本原因就是「零挂链 ⇒ 没人看见」⇒ ★★但挂不挂链是 main 的裁决权 ⇒ ★★你只做【零挂链 + 交卷页里写明「建议挂在 `state/gate_check.py` 的哪个位置 + 挂链后的预期读数」】, 不代拍★★ ★
★★**④ 闸 2 的红项【不是本单要修的】** —— ★**H2/H3 判红是【账本没跟上】(★ISS-381/385 新增的钉板 md5 闸与页面没进 ISS-372 真相页的 §1/§2 账★) ⇒ ★**那两页是已签收件, 本单不许改** ⇒ ★★你只登记「差集是什么 + 归谁修」, 落成 `needs_from` to=main ⇒ 不代修★★ ★
★★**⑤ ★★板只改一次 ⇒ 本单零写板零落表★** —— ★**不许碰 `HW/PCB/demo_mainboard.kicad_pcb` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv`; 也不许碰任何已签收页的正文** ★
★★**⑥ ★★不许把"板被写过"当成真的 (★main 本机实测·直证★)★★** —— ★**你的 H1 日志里那两行 `板 mtime=2026-11-24 11:13:xx ≠ 基线` 是【沙盒副本】的 mtime, 不是真板** ⇒ ★**真板 md5 `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` 逐字未动 (★18 天★) ⇒ ★★**别去追一个不存在的"板被写过"** ★★

---

## ★★四 · 本单要交 3 件 (★三件都要在盘 + 交卷页 B1~B6 齐全★) ★★

### ★★① 修好并交付新闸 `SW/tools/check_sw_gate_health.py` (★在盘, 本趟是修★) ★★
★**本单命门: ★**它要判的是「**闸自己坏了**」, 所以它必须能【发现别的闸的 selftest 坏了】⇒ ★**做法: 逐个跑 SW 域 13 道闸的 `--selftest`, 判【每道闸的 selftest 末行必须是 `ALL TESTS PASS` / `SELFTEST FAILED` 不许出现】** ★

★★**★本趟必须改的两处 (★修在产生点 = 你的新闸★) ★★**
| ★病灶★ | ★改哪★ | ★改完必须成立★ |
|---|---|---|
| ★**A · H5 证据等级正则太宽** ★ | ★`EV_TOKEN_RE` / `judge_h5()` (★L116 / L347~L366★) ★ | ★**页面上写 `[H1]` / `[FAIL]` / `[Errno 2]` 这种普通 token ⇒ 【不许】再被判成"作者用了非法证据等级"** · ★**但真证据等级越界 (★例如写 `[官方]` 而非 `[官网]`★) ⇒ 仍必须判红** ★ |
| ★**B · H1 比较基没归一沙盒量** ★ | ★`normalize()` (★L167~L173★) + H1 比较处 (★L225~L246★) ★ | ★**沙盒副本的 mtime / 沙盒根路径的两种写法 ⇒ 必须被归一掉** · ★**但被扫闸【真的】环境耦合 (★rc 不同 / 判据读数真的变★) ⇒ 仍必须判红** ★ |

★★**★相 (phase) 语义 (★本单第三件硬要求★) ★★**
★★**★你必须让新闸在【今天这个"两道闸真的坏了"的世界上】有【一个能变绿的读法】, 同时【任何新的坏】仍然必红 ★★**
★**现成形状照抄**: `SW/tools/check_sw_false_connectivity_gate.py` 的 `--phase pre` (今天 = 基线相, 期望绿) / `--phase post` (板那一趟验收相, 期望红) ⇒ ★**新闸照这个形状做** ★
★★**★硬约束 (★main 定的·不许自行放宽★)★★** ★
· ★**基线相 (今天) 必须 rc=0** ⇒ ★**⇒ 所以你必须把"今天已知的坏"【显式登记成基线】(★就是 §一 里 H0/H1/H2/H3 那几条真实病灶★) ⇒ ★★**不许写死成空, 不许"全绿才算过", 不许把基线开大到把未来的坏也包进去** ★★**
· ★**严格相 (板那一趟验收线) 必须能对【任何新的坏】判红** ⇒ ★**所以基线必须是一份【可枚举、可逐条比对】的清单 (★不是一句"除了已知的都算红"★) ★★**
· ★**相的名字/参数形态你自己定, 但必须两条都实跑得出 (★本单交卷页要贴两相的原样输出+rc★) ★★**

★★**★`--selftest` 必须扩充 (★现盘是 22 条·全部通过·rc=0★) ★★**
★★**★至少补 4 条反向用例, 且必须逐条自证「该红的红, 不该红的不红」★★** ★
★**① 专打病灶 A**: ★**把交付页里一个普通方括号 token (★例如 `[FAIL]`★) 写进去 ⇒ 【不许】因此判红** ★
★**② 专打病灶 A 的反向面**: ★**把交付页里一个真证据等级越界 (★例如 `[官方]`★) 写进去 ⇒ 【必须】判红** ★★**★(①②合起来 = 证明你是把判据【收窄到只认等级标记】, 不是把判据【删掉】·★不许只做①不做②★)★★ ★
★**③ 专打病灶 B**: ★**造一道夹具闸, 让它的 `--selftest` 输出里带一个【每次都不同的时间戳】⇒ 归一后两深度读数必须判为相同 ⇒ 不许因此判红** ★
★**④ 专打病灶 B 的反向面**: ★**造一道夹具闸, 让它【真的】环境耦合 (★深度 A rc=0 / 深度 B rc=1★) ⇒ 必须判红** ★★**★(③④合起来 = 证明你是把判据【改成比判据读数】, 不是【删掉 H1】·★不许只做③不做④★)★★ ★
★**⑤ (★建议★) 基线相 vs 严格相的对称用例**: ★**基线相: 今天那几条真病灶 ⇒ 绿; 严格相: 同样那几条 ⇒ 红** ★

★★**★`--selftest` 上限 6 分钟 (★超时就引用 `logs/iss388/` 里已有的留证并如实写明★) ★★**

### ★★② 交卷页 `HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md` (★★新建★★) ★★
★**B1~B6 六段齐全** (★**闸认这六段, 缺一段就红**★) + ★**B6 必须贴必跑命令的原样输出 + rc** ★
★★**★B1~B6 的标题必须含 gate_check.py 认的关键词 (★本机实读 `state/gate_check.py` 的 `REQUIRED_BLOCKS`★)★★ ★★**
| 块 | ★标题里必须出现★ |
|---|---|
| B1 | ★`结论摘要` (或 `结论` / `一句话`) ★ |
| B2 | ★`验收标准自评` (或 `自评` / `验收标准`) ★ |
| B3 | ★`证据分级` (或 `证据等级` / `证据`) ★ |
| B4 | ★`接口取值声明` (或 `接口声明` / `interface_claims` / `接口请求`) ★ |
| B5 | ★`未决项` (或 `卡点` / `阻塞` / `待办`) ★ |
| B6 | ★`自证复现命令` (或 `复现` / `复现命令` / `自证`) ★ |
★★**★命门: `state/gate_check.py` 的 `pick_handoff` 规则 = 「取最新一份交接单评分; 若最新一份自称 B 块结构但缺块 ⇒ 【不许回退】⇒ 真倒退 ⇒ Q1 立刻掉」⇒ ★★你这份一旦自称 B1~B6, 六段就必须真齐全, 不许缺一块★ ★★** ★★

★**★交卷页必须写清 4 件 (★main 交卷时按这 4 件验收★) ★★**
★**① 两道病闸的失效模式抽象 (★判据与环境耦合 / 账本与现实漂移 · 两类都不会被 daily_check 看见 ⇒ 所以需要闸的自检健康度★) ★**
★**② 你的新闸两相 (基线相 / 严格相) 的语义 + 基线清单的逐条内容 + 为什么这样切分 (★不许含糊成"除了已知的都算红"★) ★**
★**③ 两处假阳性 (★病灶 A / 病灶 B★) 的修法与【修完后的反例自证】(★①↔② 成对、③↔④ 成对·不许只给一头★) ★**
★**④ 「建议挂进 `state/gate_check.py` 的哪个位置 + 挂链后的预期读数」+ 「归谁修 §1/§2 账本差集」 (★不代拍★) ★**

### ★★③ 分片 ★★
★**只走 `state/frag_write.py`** (★**禁止 `open(p,"w")` 直接写分片**★) ★
★**产出物 ≥3 + `interface_claims` ≥5 + `needs_from` (`to=main`)★** ★
★**★`needs_from` 必须逐条写清「要谁回答什么 + 代价」, 不许只写「请裁决」★** ★
★★**★本单至少要有这三条 need (★照抄底稿即可·★你可以在此基础上补★)★★ ★★
★**① 闸 2 的 §1/§2 账本差集归谁修** (★`SW/tools/check_sw_false_connectivity_gate.py` + ISS-381/385 两页的 md5 字面量没进账 ⇒ ★**归 main** ★★不许自签台账, 不许改已签收页★) ★
★**② 新闸挂不挂 `state/gate_check.py`** (★**归 main** ★★挂链是 main 的地界★ ⇒ ★★本单零挂链★ ⇒ ★★你要在交卷页里写明「建议挂在哪个位置 + 挂链后的预期读数」★★) ★
★**③ 两道病闸的处置归谁** (★闸 1 的 `ROOT` 反推机制 = 改闸 (★属于改已签收件的判据逻辑★ ⇒ main 地界★) 还是改调用约定 (★所有 selftest 都必须 `TMPDIR=$PWD/tmp`★) ⇒ ★**只摆两条路的代价, 不代拍****) ★
★★坑 (★main 本机实测过的★) ★★**: ★**`state/frag_write.py --add-*` 的分隔符是【空格】不是【分号】** (★`shlex.split()` 切参数 ⇒ 写成 `path=…;summary=…` 会把整串吞进 `path` ⇒ **写出畸形条目却照样打印「✅ 已原子更新」**★) ⇒ ★**写完必须 `grep` 复验条目唯一, 不许只信它打印的那行** ★

---

## ★★五 · ★★本单必跑的坑 (★main 本机实测踩过, 你不要重踩★) ★★

★★**坑 1 ★★ 「先验证后写盘」是上一趟的死法** ⇒ ★**【每一件交付物: 先 write 落盘, 再跑它】⇒ 绝不许攒完所有验证再一次性写★** ★
★★**坑 2 ★★ 沙盒必须落项目盘** ⇒ ★**不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★ ⇒ 上一趟把辅助脚本写到 `/tmp` (★main 已抢救到 `logs/iss388/`★) ⇒ ★**本趟不许再往 `/tmp` 写任何东西★** ★
★★**坑 3 ★★ 上一趟死在 provider abort** ⇒ ★**本趟【每完成一件交付物就落盘】+ 交卷页【先写 B1~B5 骨架再补 B6】⇒ ★★这样再死一次也不丢东西★★** ★
★★**坑 4 ★★ 别为了「让闸变绿」去改基线** ⇒ ★**「板只改一次」铁律: 板 md5 当天变更是【合法】的 (走合法改板通道) ⇒ 那 2 道「钉板 md5 闸」当天转红是【正常】⇒ ★★但【绝不许】为了「让闸变绿」去改板 / 改闸里的基线 / 放宽判据 ⇒ 板 md5 变第二次 ⇒ 整趟白跑★★ ★★** ★★**正确做法: 读那道红闸的详情, 按【合法改板通道】落台账, 让判决源跟着板走★** ★
★★**坑 5 ★★ 本单的真板是被沙盒副本"冤枉"的 (★见 §三⑥★)** ⇒ ★**别去追一个不存在的"板被写过"★** ★

---

## ★★六 · 必跑命令 (★全部实测存在的真命令 ★· 不许自己编★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp

# ① 命令存在性守卫 (★派活前 main 已跑过 rc=0, 你开工再跑一遍★)
python3 state/check_brief_commands.py

# ② ★★本单的两道病闸: 你要先自己复现, 不许只抄本 brief★★
python3 SW/tools/check_debug_pin_order_contract.py --selftest          # ★预期 10/11 FAIL (★默认 TMPDIR★)
python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest      # ★预期 0/10 FAIL
python3 SW/tools/check_sw_board_md5_rebase_readiness.py                # ★预期 5/7 rc=1

# ③ ★★环境依赖的对照实验 (★★本单的命门证据★★)
python3 SW/tools/check_debug_pin_order_contract.py --selftest
TMPDIR="$PWD/tmp" python3 SW/tools/check_debug_pin_order_contract.py --selftest

# ④ ★★本单的新闸 (★上一趟已在盘, 本趟是【修它】不是【重写它】★)★★
python3 SW/tools/check_sw_gate_health.py                    # ★基线相 ⇒ 期望 rc=0 (★今天那几条真病灶登记成基线★)
python3 SW/tools/check_sw_gate_health.py --phase post       # ★严格相 ⇒ 期望 rc=1 且逐条点名 (★相名你自己定, 但两条都要实跑得出★)
python3 SW/tools/check_sw_gate_health.py --selftest         # ★期望 rc=0 · 末行 ALL TESTS PASS · ★≥26 条 (★现 22 条 + 本单必补 4 条★)

# ⑤ SW 域其它闸 (★只读对照, 不许改★)
python3 SW/tools/check_sw_false_connectivity_gate.py --selftest
python3 SW/check_evt_charge_current_criterion.py --selftest

# ⑥ 板 / 三表 指纹 (★开工前后各打一次★)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

# ⑦ 收尾 (★rc 必须 0 · Q1 必须 18/18★)
python3 state/frag_write.py --agent sw-lead --show
python3 state/merge.py
python3 state/gate_check.py
```

★★**基线 (★main 2026-11-24 11:2x~11:4x 本机实跑, 你自己再核一遍★) ★★**
```
板 md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 · size = 4940213
网表 6aee500e60ba0732f83a9cf557ba90ab · 脚表 9174309df1ec9411ac8e8d9e80ee386a · BOM 5b9993992405904a60ac96a020b375d8
state/gate_check.py md5 = 5f370bb8cf828473e70ccc5d6412da98 (★本单不许碰★)
state/merge.py      ⇒ rc=0 (产出 839 | 阻塞 43 | 冲突 0)
state/gate_check.py ⇒ rc=0 (【Q1】18/18 · 【Q7】钉板 md5 闸链 10/10)
★SW 域 13 道闸 roster 画像已在盘: logs/iss388/roster_profile_20261124_1049.jsonl (14 行)
  ★★**直接用, 不要重跑一遍 13 道闸** (★合计耗时 ~2 分钟·而且其中 check_sw_fp_truth_impact 单道就 32 秒★)★★ ★★
★★上一趟留下的现成留证 (★直接用, 别重跑★): logs/iss388/gate_health_live_run1.log (★上一趟的裸跑原样输出·5,645 B★)
★★上一趟已建的两件交付物 (★别重做★): SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md (20,941 B @11:09) + SW/tools/check_sw_gate_health.py (30,823 B @11:11)
```

---

## ★★七 · 边界自证 (★交卷页里必须有这一段★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5/mtime/size 前后逐字相同★ |
| ★零落表★ | ★网表/脚表/BOM 三件 md5 前后逐字相同★ |
| ★零改既有闸的判据/阈值★ | ★`SW/tools/check_debug_pin_order_contract.py` / `SW/tools/check_sw_board_md5_rebase_readiness.py` md5 与基线同★ |
| ★零改既有页面正文★ | ★ISS-372/375/381/385 已签收页 md5 与基线同★ |
| ★零挂链★ | ★`grep -c check_sw_gate_health state/gate_check.py` = 0★ |
| ★零外发★ | ★全程只读本机 + 自己上网查资料; ★`state/outbox/` 一个字节未动★ |
| ★不代拍★ | ★★**闸 2 的账本差集归谁修 / 新闸挂不挂链 / 闸 1 的环境敏感在源头修还是在调用约定修 —— 三条全是 main 的裁决权 ⇒ ★★你只摆代价, 不写「应该 X」★★ ⇒ ★机器块里要有 `*_decision = not_decided_here` 这类字段★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 你一个字节未动★ |
| ★没写别人的分片★ | ★只写 `state/fragments/sw.yaml`★ |
| ★沙盒纪律★ | ★只落 `tmp/iss388_sbx/` 与 `logs/iss388/`; ★不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★ |
| ★证据分级★ | ★每条结论标五级之一★ |
