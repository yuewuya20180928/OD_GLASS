# ISS-388 · cont1 · sw-lead · 把「两道已签收 SW 闸今天真的坏了」从【诊断已做完 · 零交付物在盘】做到【诊断页 + 闸健康度闸 + 交卷页 + 分片 + 交卷】· 零写板 · 零落表 · 零改既有闸

★**本单 = ISS-388 cont1 (★不是新单 · 不是从零重做 · ★)** ★
★**本单 = 纯分析 + 新建闸 + 诊断 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

★**主线 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**本单是 PCB 主线的【护栏自检层】· 纯分析不动板 ⇒ 属纪律 ①「先派纯分析/作业包类」⇒ 本单【可派】且【不动板】★** ★
★★**★本单的真正价值 (★为什么它必须做完★): ★**这两道闸在「板只改一次」那一趟里各自把关什么** (★`check_debug_pin_order_contract` = 物理针序契约; ★`check_sw_board_md5_rebase_readiness` = 板 md5 引用面自守 ⇒ ★**它们一旦烂掉, 那一趟就没有护栏**★) ★★ ★★

---

## ★★一 · 上一趟怎么死的 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**上一趟 = 2026-11-24 09:45:40 起 · 10:55:12 止 · 墙钟 69.5 分钟** ★
★**子会话** `agent:sw-lead:subagent:54b0b1d5-02b2-4f5f-898a-119e633f0448` / sessionId `d67efde7-8477-4ca6-8e41-acd8f3f0708b` · transcript 141 行 · 77 次 toolCall (71 exec + 3 write + 2 process + 1 update_plan) ★
★★**★死因 = 上一趟在【写本单新闸 `SW/tools/check_sw_gate_health.py` 的那一刻】被掐死** ★★ (★transcript 末行 = 一条 `write` 工具调用的参数里已有新闸源码开头 (`# ISS-388 · SW 域【闸健康度闸】 (★零挂链★)`), ★**但没有 toolResult ⇒ 那个 write 没落盘**★) ★★

### ★★★上一趟的产出: ★**诊断已做完, 但三件交付物【零】在盘** ★★★

| ★项★ | ★状态★ | ★说明★ |
|---|---|---|
| ★**`SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md`** ★ | ★**不在盘** ★ | ★诊断页 ★**未写** ★ |
| ★**`SW/tools/check_sw_gate_health.py`** ★ | ★**不在盘** ★ | ★新闸 ★**write 被掐在落盘前** ★ |
| ★**`HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md`** ★ | ★**不在盘** ★ | ★交卷页 ★**未写** ★ |
| ★**`state/fragments/sw.yaml` 的 ISS-388 登记** ★ | ★**0 条** ★ | ★分片 ★**未写** ★ |
| ★**★但两道的失效已【实测复现】出来了** ★ | ★**在盘 (★main 10:5x 亲手复跑过★)** ★ | ★见 §一 的「main 本机已复核读数」★ |
| ★**SW 域 13 道闸的 roster 画像 (rc / 耗时 / 末行)** ★ | ★**`logs/iss388/roster_profile_20261124_1049.jsonl` (14 行) ★** ★ | ★★**上一趟的产出, main 已从 `/tmp` 抢救到项目盘 `logs/iss388/` (★`/tmp` 会被清★) ⇒ ★★**直接用, 不要重跑一遍 13 道闸**★★ ★ |

★★**★main 本机已复核过的读数 (2026-11-24 10:5x~11:0x 实跑 · ★你要自己再跑一遍, 别只抄本表★)★★ ★★

```
$ python3 SW/tools/check_debug_pin_order_contract.py --selftest          ⇒ rc=1
    === selftest 10/11 PASS (共 11 条反向用例, 其中镜像类 3 条) === / SELFTEST FAILED
$ TMPDIR="$PWD/tmp" python3 SW/tools/check_debug_pin_order_contract.py --selftest ⇒ rc=0
    === selftest 11/11 PASS (共 11 条反向用例, 其中镜像类 3 条) === / ALL TESTS PASS
    ★★同一份源码, 只差 TMPDIR ⇒ 10/11 vs 11/11 ⇒ ★★【闸 1 的病根 = 判据与环境耦合】★★

$ python3 SW/tools/check_sw_board_md5_rebase_readiness.py                ⇒ rc=1
    [PASS] H2 / H3 / H5 / H6 / H7
    [FAIL] H4 · SW 域每道【真钉板 md5 的判据脚本】必须登记在册 (类A 字面量 + 类B 页面内嵌基线)
        ⚠ ★SW 域有闸 SW/tools/check_sw_false_connectivity_gate.py 硬钉了板 md5 (类A·.py 内 32 位字面量) 但它没进 §2 的账 ⇒ 判红★
    ⇒ 闸结果 5/7 通过, rc=1
$ python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest      ⇒ rc=1
    反向用例: 0/10 通过 (★每条都自证「红的集合 == {目标那一条}」★)
    ★有用例 FAIL ⇒ 本闸不可信 ⇒ rc=1★
```

★★**★main 本机实读出的根因 (★因果链你要自己复核一遍, 但别重找★)★★ ★★
★**闸 1 (`check_debug_pin_order_contract.py`)**: ★**该闸的 `ROOT` 是从 `__file__` 往上退两级算出来的 (L39) ⇒ M2 反向用例把闸源码复制到【沙盒目录】再跑 ⇒ 副本的 `ROOT` 就跟着沙盒目录走 ⇒ 沙盒落在 `/tmp` 时 `ROOT` 退成 `/` ⇒ 它去找 `/SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` ⇒ 不存在 ⇒ FATAL** ★
★★**闸 2 (`check_sw_board_md5_rebase_readiness.py`)**: ★**H1/H4 判红是因为【ISS-381 新建的 `SW/tools/check_sw_false_connectivity_gate.py` 硬钉了板 md5, 且 ISS-381/ISS-385 新建的两份页面里也有板 md5 字面量】⇒ 它们都没进 ISS-372 真相页的 §1/§2 账 ⇒ ⇒ H1/H4 判红【不是闸坏了】, 是【账本没跟上】—— 这两条判据本来就是干这个用的** ★★ ⇒ ★**真正的病灶是: 当 SW 域【新增一道钉板 md5 的闸】时, 没有任何机制提醒「§2 的账要跟着登记」⇒ 账与现实漂移 ⇒ 闸自己判红 ⇒ 而它【零挂链】⇒ 这条红没人看见 ⇒ 它就这么烂在盘上** ★★

---

## ★★二 · 本趟的时间预算 (★本项目子会话的真实墙 ★★runTimeout 2400s = 40 分钟★★) ★★

★★**★上一趟跑了 69.5 分钟还是零交付物 ⇒ 本趟【必须先落盘再验证】★★ ★★

★**顺序不许改 (★每一步都落盘★)**:
1. ★**第 1 步 (≤5 分钟) · 复核**: 跑 §四 的 ①②③ ⇒ ★**原样输出落 `logs/iss388/cont1_verify.log`** ⇒ ★**逐条对照 §一 的读数, 对不上就如实写出来★ ★
2. ★**第 2 步 (≤8 分钟) · 诊断页** ★**新建** `SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md` (★§0~§6★) ⇒ ★**这一件先落盘, 因为它承载另外两件的素材★** ★
3. ★**第 3 步 (≤14 分钟) · 新闸** ★**新建** `SW/tools/check_sw_gate_health.py` (★H0~H5 + ≥8 条反向用例★) ⇒ ★**先写文件落盘, 再跑裸跑 + `--selftest` ⇒ 修【误报/漏检/崩溃】, 不许放松任何判据★** ★
4. ★**第 4 步 (≤7 分钟) · 交卷页** ★**新建** `HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md` (★B1~B6 六段齐全 + B6 贴必跑命令原样输出 + rc★) ★
5. ★**第 5 步 (≤3 分钟) · 分片** ⇒ ★**只走 `state/frag_write.py`** (★**禁止 `open(p,"w")` 直接写分片**★) ⇒ ★**产出物 ≥3 + `interface_claims` ≥5 + `needs_from` (`to=main`)★** ★
6. ★**第 6 步 (★最关键★)**: ★**交卷消息 (★上一趟就是死在这★)** ★

★★**★如果时间在第 4 步用完 ⇒ 允许交卷页先写 B1~B5 (B6 可后补) ⇒ ★★但交卷消息【绝对不许省】★★ ★★**

---

## ★★三 · 本单的地界事实 (★不许越★) ★★

★★**① 两道病闸【不许改】** —— ★**`SW/tools/check_debug_pin_order_contract.py` (ISS-375 签收件) 与 `SW/tools/check_sw_board_md5_rebase_readiness.py` (ISS-372 签收件) 的判据/阈值一个字都不许动** ⇒ ★**它们现在是红的, 那是【它们的正确行为】(★闸 1 = 环境耦合暴露; 闸 2 = 账本漂移暴露★) ⇒ ★★不许为了让它们变绿去改它们、去改阈值、去改 §1/§2 的账★★** ★
★★**② 本单只【新建】一道闸, 不改既有闸** ⇒ ★**`SW/tools/check_sw_gate_health.py` 是新文件, 零挂链 (★`grep -c check_sw_gate_health state/gate_check.py` 必须 = 0 · 挂链是 main 的地界★)** ★
★★**③ 零挂链是本单的命根** —— ★**这两道闸烂掉的根本原因就是「零挂链 ⇒ 没人看见」⇒ ★你新闸若也零挂链, 就会重蹈覆辙 ⇒ ★★但挂不挂链是 main 的裁决权 ⇒ ★★你只做【零挂链 + 交卷页里写明「建议挂进 state/gate_check.py 的哪个位置 + 挂链后的预期读数」】, 不代拍★★** ★
★★**④ 闸 2 的红项【不是本单要修的】** —— ★**H1/H4 判红是【账本没跟上】(★ISS-381/385 新增的钉板 md5 闸与页面没进 ISS-372 真相页的 §1/§2 账★) ⇒ ★**那两页是已签收件, 本单不许改** ⇒ ★★你只登记「差集是什么 + 归谁修」, 落成 `needs_from` to=main ⇒ 不代修★★** ★
★★**⑤ 板只改一次 ⇒ 本单零写板零落表** —— ★**不许碰 `HW/PCB/demo_mainboard.kicad_pcb` / `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv`; 也不许碰任何已签收页的正文** ★

---

## ★★四 · 本单要交 3 件 (★三件都要在盘 + 交卷页 B1~B6 齐全★) ★★

### ★★交卷物 (3 件) ★★

1. ★**`SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md`** (★★新建★★ 诊断页) ★
2. ★**`SW/tools/check_sw_gate_health.py`** (★★新建★★ 新闸 · 零挂链) ★
3. ★**`HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md`** (★★新建★★ 交卷页 · B1~B6) ★

### ★★① 诊断页 `SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md` ★★
★**§0 一句话结论** (★两道闸各一句 + 一句「为什么没人看见」★) ★
★**§1 闸 1 诊断**: ★`ROOT` 反推机制 → 沙盒目录依赖 → 为什么默认 `/tmp` 会 FAIL → **为什么签收当天是绿的** (★你要查清: ★**签收当天 main 跑的时候 TMPDIR 是什么** ★) ★
★**§2 闸 2 诊断**: ★H1/H4 的红项逐条对应到【哪个新文件、哪一行、什么时候建的】⇒ **登记漂移账** ★
★**§3 两道闸的共同失效模式抽象**: ★**「闸的失效」有两类: ① 判据与环境耦合 ② 账本与现实漂移 ⇒ 两类都不会被 daily_check 看见 (零挂链) ⇒ 需要一条【闸的自检健康度】判据** ★
★**§4 影响面**: ★**这两道闸在「板只改一次」那一趟里各自把关什么** ⇒ ★**它们一旦烂掉, 那一趟就没有护栏** ★
★**§5 降级方案 + 待裁项** (★`to=main`★) ★
★**§6 复跑命令 + 机器块** ★

### ★★② 新闸 `SW/tools/check_sw_gate_health.py` (★★本单主交付物★★) ★★
★**零挂链** (★`state/gate_check.py` 命中必须 = 0★) ★
★**本单的命门: ★**它要判的是「**闸自己坏了**」, 所以它必须能【发现别的闸的 selftest 坏了】⇒ ★**做法: 逐个跑 SW 域闸的 `--selftest`, 判【每道闸的 selftest 末行必须是 `ALL TESTS PASS` / `SELFTEST FAILED` 不许出现】** ★
★**判据 (★fail-closed · 每条都要有反向用例★)** ★
| 判据 | ★判什么★ |
|---|---|
| ★**H0** ★ | ★SW 域闸清单在盘且每个闸的 `--selftest` **rc=0** + ★**末行含 `ALL TESTS PASS`** ⇒ ★**任一闸 selftest 非 0 ⇒ 判红并点名是哪个闸 + 它的原文末行** ★ |
| ★**H1** ★ | ★★**本单的第二个命门**★★: ★**每道被扫的闸, 都要在【两个不同 TMPDIR 深度】下各跑一次 selftest ⇒ 两次读数必须逐字相同** ⇒ ★**⇒ 这条直接把「闸 1 的环境敏感」变成可判的** (★★**这一条是本单最有价值的判据: ★**它让「环境敏感」这个失效模式从此有护栏**★★) ★ |
| ★**H2** ★ | ★「钉板 md5 的闸清单」与【盘上真实存在的钉板 md5 闸】必须一致 (★**读 §2 的账 + 实扫 SW 域 `.py`/页面 md5 字面量 ⇒ 两边对不上 ⇒ 判红并点名差集** ★) ⇒ ★**⇒ 这条直接接住闸 2 的病灶 (H4 判红 ⇒ §2 账本漂移 ⇒ 这里点出差集)** ★ |
| ★**H3** ★ | ★页面 md5 引用面 (§1 清单) 与盘上真实引用行必须一致 (★**接住 H1 判红那四行** ★) ★ |
| ★**H4** ★ | ★板三项指纹未动 + 零落表 + ★**零挂链** (★`state/gate_check.py` 命中 = 0★) ★ |
| ★**H5** ★ | ★证据分级白名单 + 零挂起措辞 (★**语境判据**★) ★ |

★★**★`--selftest` 至少 8 条反向用例**, ★**至少 2 条专打命门**: ★① 把被扫闸的 selftest 末行伪造掉 ⇒ 必须 H0 红 ★② ★**故意让某道闸在浅 TMPDIR 下 FAIL ⇒ 必须 H1 红 (证明「两个深度读数必须相同」这条判据真的活着)** ★
★★**★你的新闸自己必须【环境无关】★** (★★**你自己就是 H1 那条判据的执行者 ⇒ ★**你自己要是环境敏感的, 那条判据就没人信了★★ ★★)
★★**★必踩的坑 (★main 本机实测★)★**: ★**沙盒临时目录必须落在【项目盘】(★`tmp/` 下面★) 且深度要能被 `__file__` 反推对 ⇒ ★**不许依赖系统 `/tmp` 的深度** ⇒ ★**最稳的写法: 沙盒路径从【本闸自己的 `ROOT`】推出来, 而不是从 `tempfile.gettempdir()`** ★★
★★**★`H1` 的实现注意 (★main 本机实测过的坑★)★**: ★**两个深度要真的不同 (★例如 `<root>/tmp/iss388_sbx/a/` 与 `<root>/tmp/iss388_sbx/b/c/`★) ⇒ ★**同深度跑两遍不算 H1 通过 ⇒ 必须是【不同的相对深度】★** ★

### ★★③ 交卷页 `HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md` (★★新建★★) ★★
★**B1~B6 六段齐全** (★**闸认这六段, 缺一段就红**★) + ★**B6 必须贴必跑命令的原样输出 + rc** ★
★★**★B1~B6 的标题必须含 gate_check.py 认的关键词 (★本机实读 `state/gate_check.py` 的 `REQUIRED_BLOCKS`★)★★ ★★
| 块 | ★标题里必须出现★ |
|---|---|
| B1 | ★`结论` (或 `结论摘要` / `一句话`) ★ |
| B2 | ★`验收标准自评` (或 `自评` / `验收标准`) ★ |
| B3 | ★`证据分级` (或 `证据等级` / `证据`) ★ |
| B4 | ★`接口取值` (或 `接口声明` / `interface_claims` / `接口请求`) ★ |
| B5 | ★`未决` (或 `卡点` / `阻塞` / `待办`) ★ |
| B6 | ★`复现` (或 `复现命令` / `自证`) ★ |
★★**★命门: `state/gate_check.py` 的 `pick_handoff` 规则 = 「取最新一份交接单评分; 若最新一份自称 B 块结构但缺块 ⇒ 【不许回退】⇒ 真倒退 ⇒ Q1 立刻掉」⇒ ★★你这份一旦自称 B1~B6, 六段就必须真齐全, 不许缺一块★ ★★** ★★

---

## ★★五 · 分片 ★★
★**只走 `state/frag_write.py`** (★**禁止 `open(p,"w")` 直接写分片**★) ★
★**产出物 ≥3 + `interface_claims` ≥5 + `needs_from` (`to=main`) ★**
★**★`needs_from` 必须逐条写清「要谁回答什么 + 代价」, 不许只写「请裁决」★** ★
★★**★本单至少要有这三条 need (★照抄底稿即可·★你可以在此基础上补★)★★ ★★
★**① 闸 2 的 §1/§2 账本差集归谁修** (★`SW/tools/check_sw_false_connectivity_gate.py` + ISS-381/385 两页的 md5 字面量没进账 ⇒ ★**归 main** ★★不许自签台账, 不许改已签收页★) ★
★**② 新闸挂不挂 `state/gate_check.py`** (★**归 main** ★★挂链是 main 的地界★ ⇒ ★★本单零挂链★ ⇒ ★★你要在交卷页里写明「建议挂在哪个位置 + 挂链后的预期读数」★★) ★
★**③ 闸 1 的环境敏感要不要在【源头上修】** (★`ROOT` 反推机制 ⇒ ★**修法有两档: 改闸 (★属于改已签收件的判据逻辑★ ⇒ main 地界★) 或 改调用约定 (★所有 selftest 都必须 `TMPDIR=$PWD/tmp`★) ⇒ ★**只摆两条路的代价, 不代拍****) ★
★★**坑 (★main 本机实测过的★) ★★**: ★**`state/frag_write.py --add-*` 的分隔符是【空格】不是【分号】** (★`shlex.split()` 切参数 ⇒ 写成 `path=…;summary=…` 会把整串吞进 `path` ⇒ **写出畸形条目却照样打印「✅ 已原子更新」**★) ⇒ ★**写完必须 `grep` 复验条目唯一, 不许只信它打印的那行** ★

---

## ★★六 · ★★本单必跑的坑 (★main 本机实测踩过, 你不要重踩★) ★★

★★**坑 1 ★★ 「先验证后写盘」是上一趟的死法** ⇒ ★**【每一件交付物: 先 write 落盘, 再跑它】⇒ 绝不许攒完所有验证再一次性写★** ★
★★**坑 2 ★★ 沙盒必须落项目盘** ⇒ ★**不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★ ⇒ 上一趟把自己的辅助脚本写到了 `/tmp/iss388_*.py` (★main 已抢救到 `logs/iss388/`★) ⇒ ★**本趟不许再往 `/tmp` 写任何东西★** ★
★★**坑 3 ★★ H1 那条判据要真跑两遍** ⇒ ★**两个 TMPDIR 深度必须真的不同 ⇒ 同深度跑两遍不算通过★** ★
★★**坑 4 ★★ 别为了「让闸变绿」去改基线** ⇒ ★**「板只改一次」铁律: 板 md5 当天变更是【合法】的 (走合法改板通道) ⇒ 那 2 道「钉板 md5 闸」当天转红是【正常】⇒ ★★但【绝不许】为了「让闸变绿」去改板 / 改闸里的基线 / 放宽判据 ⇒ 板 md5 变第二次 ⇒ 整趟白跑★★ ★★** ★★**正确做法: 读那道红闸的详情, 按【合法改板通道】落台账, 让判决源跟着板走★** ★

---

## ★★七 · 必跑命令 (★全部实测存在的真命令 ★· 不许自己编★) ★★

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

# ④ 本单新闸 (★你自己写的★)
python3 SW/tools/check_sw_gate_health.py
python3 SW/tools/check_sw_gate_health.py --selftest

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

★★**基线 (★main 2026-11-24 10:5x 本机实跑, 你自己再核一遍★)** ★★
```
板 md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 · size = 4940213
网表 6aee500e60ba0732f83a9cf557ba90ab · 脚表 9174309df1ec9411ac8e8d9e80ee386a · BOM 5b9993992405904a60ac96a020b375d8
merge.py ⇒ rc=0 · gate_check.py ⇒ rc=0 · 【Q1】18/18 · 【Q7】钉板 md5 闸链 10/10 道绿
★SW 域 13 道闸 roster 画像已在盘: logs/iss388/roster_profile_20261124_1049.jsonl (14 行)
  ★★直接用, 不要重跑一遍 13 道闸 (★合计耗时 ~2 分钟·而且其中 check_sw_fp_truth_impact 单道就 32 秒★)★★
```

---

## ★★八 · 边界自证 (★交卷页里必须有这一段★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5/mtime/size 前后逐字相同★ |
| ★零落表★ | ★网表/脚表/BOM 三件 md5 前后逐字相同★ |
| ★零改既有闸的判据/阈值★ | ★`SW/tools/check_debug_pin_order_contract.py` / `SW/tools/check_sw_board_md5_rebase_readiness.py` md5 与基线同★ |
| ★零改既有页面正文★ | ★ISS-372/375/381/385 已签收页 md5 与基线同★ |
| ★零挂链★ | ★`grep -c check_sw_gate_health state/gate_check.py` = 0★ |
| ★零外发★ | ★全程只读本机; ★`state/outbox/` 一个字节未动★ |
| ★不代拍★ | ★★**闸 2 的账本差集归谁修 / 新闸挂不挂链 / 闸 1 的环境敏感在源头修还是在调用约定修 —— 三条全是 main 的裁决权 ⇒ ★★你只摆代价, 不写「应该 X」★★ ⇒ 机器块里要有 `*_decision = not_decided_here` 这类字段★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 你一个字节未动★ |
| ★没写别人的分片★ | ★只写 `state/fragments/sw.yaml`★ |
| ★沙盒纪律★ | ★只落 `tmp/iss388_sbx/` 与 `logs/iss388/`; ★不许写系统 `/tmp`·不许 `cp -al`·不许硬链接★ |
| ★证据分级★ | ★每条结论标五级之一★ |
