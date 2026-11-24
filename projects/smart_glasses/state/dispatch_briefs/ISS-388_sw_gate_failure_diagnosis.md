# ISS-388 · sw-lead · 两道**已签收** SW 闸今天实测**真的坏了** ⇒ 把「闸的失效」本身变成可判的 (★修在产生点 · 零写板 · 零落表· 零改既有闸的**判据**★)

★**本单性质**: ★**纯分析 + 新建闸 + 诊断 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ① (先派不动板的) ★

---

## ★★一 · 为什么是这一单 (★main 本机实读 · 不抄任何 agent 报告★) ★★

★**本 job 跑例行核验时, 把 SW 域 12 道闸逐个 `--selftest` 跑了一遍 ⇒ ★**有两道【已经签收 verified】的闸, 今天实测真的 FAIL** ★★ ★**这两道闸都【零挂链】(`grep -c` = 0) ⇒ 所以 daily_check / gate_check 全绿 ⇒ ★**没人看见** ★★

★**★闸 1 · `SW/tools/check_debug_pin_order_contract.py` (ISS-375 签收件) ⇒ `--selftest` 10/11 ★★**
```
$ python3 SW/tools/check_debug_pin_order_contract.py --selftest
  [FAIL] M2       把 D2 的算式改成手算常数 (变异本闸源码)   期望红=D2,D4
                  实红=FATAL: 变异体无 JSON 输出 ← 期望集未被完全命中
                  · FATAL: [Errno 2] No such file or directory:
                    '/SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md'
=== selftest 10/11 PASS (共 11 条反向用例, 其中镜像类 3 条) ===
SELFTEST FAILED          rc=1
```
★**main 本机已定位根因 (★你不必重找, 但你要独立复核一遍★)**: ★**该闸的 `ROOT` 是从 `__file__` 往上退两级算出来的** (★`SW/tools/check_debug_pin_order_contract.py` L39★) ★⇒ ★**M2 反向用例把闸源码复制到【沙盒目录】再跑 ⇒ 副本的 `ROOT` 就跟着沙盒目录走 ⇒ 沙盒落在 `/tmp` 时 `ROOT` 退成 `/` ⇒ 它去找 `/SW/BOARD_ONEPASS_DEBUG_PIN_ORDER_CONTRACT.md` ⇒ 不存在 ⇒ FATAL** ★
★**main 本机实测证据 (★这就是「环境依赖」的直接证明★)**:
```
$ python3 SW/tools/check_debug_pin_order_contract.py --selftest                       ⇒ 10/11 FAIL (默认 TMPDIR=/tmp)
$ TMPDIR="$PWD/tmp" python3 SW/tools/check_debug_pin_order_contract.py --selftest    ⇒ 11/11 PASS
```
★★**⇒ 结论: ★**这条自检用例【能不能过】取决于【沙盒临时目录落在哪】⇒ ★**同一份代码、同一块板, 换个环境就红 ⇒ 这条反向用例是【环境敏感】的, 不是【判据敏感】的** ★★ ★**⇒ 而它是 ISS-375 签收时【亲手加的】【变异本闸源码 ⇒ 证明闸真在读 KiCad 变换】那条命门用例** ★★

★**★闸 2 · `SW/tools/check_sw_board_md5_rebase_readiness.py` (ISS-372 签收件) ⇒ 裸跑 5/7 rc=1 + `--selftest` 0/10 ★★**
```
$ python3 SW/tools/check_sw_board_md5_rebase_readiness.py
  [FAIL] H1 · §1 清单漏登记
    ⚠ 扫描到 SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23   但 §1 清单里没有这一行 ⇒ 判红
    ⚠ 扫描到 SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:201  但 §1 清单里没有这一行 ⇒ 判红
    ⚠ 扫描到 SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215  但 §1 清单里没有这一行 ⇒ 判红
    ⚠ 扫描到 SW/tools/check_sw_false_connectivity_gate.py:73   但 §1 清单里没有这一行 ⇒ 判红
  [FAIL] H4 · SW 域每道【真钉板 md5 的判据脚本】必须登记在册
    ⚠ SW 域有闸 SW/tools/check_sw_false_connectivity_gate.py 硬钉了板 md5 但它没进 §2 的账 ⇒ 判红
  闸结果 5/7 通过, rc=1
$ python3 SW/tools/check_sw_board_md5_rebase_readiness.py --selftest
  反向用例: 0/10 通过 ⇒ ★有用例 FAIL ⇒ 本闸不可信 ⇒ rc=1
```
★**main 本机实读出的根因 (★因果链你要自己复核一遍★)**: ★**H1/H4 判红是因为【ISS-381 新建的 `SW/tools/check_sw_false_connectivity_gate.py` 硬钉了板 md5, 且 ISS-381/ISS-385 新建的两份页面里也有板 md5 字面量】⇒ ★**它们都没进 ISS-372 真相页的 §1/§2 账** ⇒ ⇒ ★**H1/H4 判红【不是闸坏了】, 是【账本没跟上】—— ★**这两条判据本来就是干这个用的** ★★ ★★**⇒ 所以真正的病灶是: ★**当 SW 域【新增一道钉板 md5 的闸】时, 没有任何机制提醒「§2 的账要跟着登记」⇒ ★**账与现实漂移 ⇒ ★**闸自己判红 ⇒ ★**而它【零挂链】⇒ 这条红没人看见 ⇒ ★**它就这么烂在盘上** ★★ ★★

★★**★本单的一句话定位★**: ★**闸不是坏了, 是【账本与现实漂移】+【判据与环境耦合】⇒ ★**这两类失效【今天没人能看见】(零挂链) ⇒ ★**本单把「闸的失效」本身变成可判的** ★★

---

## ★★二 · 本单要交 3 件 ★★

1. ★**`SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md`** (★诊断页★)
2. ★**`SW/tools/check_sw_gate_health.py`** (★新闸 · 零挂链★)
3. ★**`HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md`** (★交卷页 · B1~B6★)

### ★★① 诊断页 `SW/BOARD_ONEPASS_GATE_FAILURE_DIAGNOSIS.md` ★★
★**§0 一句话结论** (★两道闸各一句 + 一句「为什么没人看见」★) ★
★**§1 闸 1 诊断**: ★`ROOT` 反推机制 → 沙盒目录依赖 → 为什么默认 `/tmp` 会 FAIL → **为什么签收当天是绿的** (★你要查清: ★**签收当天 main 跑的时候 TMPDIR 是什么** ★) ★
★**§2 闸 2 诊断**: ★H1/H4 的红项逐条对应到【哪个新文件、哪一行、什么时候建的】⇒ **登记漂移账** ★
★**§3 两道闸的共同失效模式抽象**: ★**「闸的失效」有两类: ① 判据与环境耦合 ② 账本与现实漂移 ⇒ 两类都不会被 daily_check 看见 (零挂链) ⇒ 需要一条【闸的自检健康度】判据** ★
★**§4 影响面**: ★**这两道闸在「板只改一次」那一趟里各自把关什么** (★`check_debug_pin_order_contract` = 物理针序契约; ★`check_sw_board_md5_rebase_readiness` = 板 md5 引用面自守 ⇒ ★**它们一旦烂掉, 那一趟就没有护栏**★) ★
★**§5 降级方案 + 待裁项** (★`to=main`★) ★
★**§6 复跑命令 + 机器块** ★

### ★★② 新闸 `SW/tools/check_sw_gate_health.py` ★★
★**零挂链** (★`state/gate_check.py` 命中 = 0★) ★
★**本单的命门: ★**它要判的是「**闸自己坏了**」, 所以它必须能【发现别的闸的 selftest 坏了】⇒ ★**做法: 逐个跑 SW 域闸的 `--selftest`, 判【每道闸的 selftest 末行必须是 `ALL TESTS PASS` / `SELFTEST FAILED` 不许出现】** ★
★**判据建议 (★fail-closed★)**:
- ★**H0** SW 域闸清单在盘且每个闸的 `--selftest` **rc=0** + ★**末行含 `ALL TESTS PASS`** ⇒ ★**任一闸 selftest 非 0 ⇒ 判红并点名是哪个闸 + 它的原文末行** ★
- ★**H1** ★**★本单的第二个命门★**: ★**每道被扫的闸, 都要在【两个不同 TMPDIR 深度】下各跑一次 selftest ⇒ 两次读数必须逐字相同** ⇒ ★**⇒ 这条直接把「闸 1 的环境敏感」变成可判的** (★★**这一条是本单最有价值的判据: ★**它让「环境敏感」这个失效模式从此有护栏**★★) ★
- ★**H2** 「钉板 md5 的闸清单」与【盘上真实存在的钉板 md5 闸】必须一致 (★**读 §2 的账 + 实扫 SW 域 `.py`/页面 md5 字面量 ⇒ 两边对不上 ⇒ 判红并点名差集** ★) ⇒ ★**⇒ 这条直接接住闸 2 的病灶 (H4 判红 ⇒ §2 账本漂移 ⇒ 这里点出差集)** ★
- ★**H3** 页面 md5 引用面 (§1 清单) 与盘上真实引用行必须一致 (★**接住 H1 判红那四行** ★) ★
- ★**H4** 板三项指纹未动 + 零落表 + ★**零挂链** (★`state/gate_check.py` 命中 = 0★) ★
- ★**H5** 证据分级白名单 + 零挂起措辞 (★**语境判据**★) ★
★**`--selftest` 至少 8 条反向用例**, ★**至少 2 条专打命门**: ★① 把被扫闸的 selftest 末行伪造掉 ⇒ 必须 H0 红 ★② ★**故意让某道闸在浅 TMPDIR 下 FAIL ⇒ 必须 H1 红 (证明「两个深度读数必须相同」这条判据真的活着)** ★
★★**★你的新闸自己必须【环境无关】★** (★★**你自己就是 H1 那条判据的执行者 ⇒ ★**你自己要是环境敏感的, 那条判据就没人信了★★** ★★)
★★**★★本单必踩的坑 (★main 本机实测★)★**: ★**沙盒临时目录必须落在【项目盘】(★`tmp/` 下面★) 且深度要能被 `__file__` 反推对 ⇒ ★**不许依赖系统 `/tmp` 的深度** ⇒ ★**最稳的写法: 沙盒路径从【本闸自己的 `ROOT`】推出来, 而不是从 `tempfile.gettempdir()`** ★★

### ★★③ 交卷页 `HANDOFF/2026-11-24_sw-lead_ISS388_两道签收闸失效诊断与闸健康度闸.md` ★★
★**B1~B6 六段齐全** + ★**B6 贴必跑命令原样输出 + rc** ★

---

## ★★三 · 分片 ★★
★**只走 `state/frag_write.py`** (★禁止 `open(p,"w")`★) ★
★**产出物 ≥3 + `interface_claims` ≥5 + `needs_from` (`to=main`) ★**

---

## ★★四 · 必跑命令 (★全部实测存在的真命令 · 不许自己编★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 命令存在性守卫
python3 state/check_brief_commands.py

# ② ★★本单的两道病闸: 你要先自己复现, 不许只抄本 brief★★
python3 SW/tools/check_debug_pin_order_contract.py --selftest          # ★预期 10/11 FAIL
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

★★**基线 (★main 2026-11-24 09:1x 本机实跑, 你自己再核一遍★)** ★★
```
板 md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413 · size = 4940213
⇒ ★**板 18 天逐字节未动 ⇒ G1 仍开, 不许投板** ★
gate_check.py ⇒ rc=0 · 【Q1 交付齐备率】18/18 · 【Q7 钉板 md5 闸链】10/10 道绿
⇒ ★**注意: ★**这两道坏闸【零挂链】⇒ 所以 gate_check 照样全绿 ⇒ ★**本单做完后 gate_check 【也必须还是】全绿 (你的新闸也零挂链)★ ★
```

---

## ★★五 · 边界自证 (★交卷页里必须有这一段★) ★★

| 边界 | 怎么自证 |
|---|---|
| ★零写板★ | ★板 md5/mtime/size 前后逐字相同★ |
| ★零落表★ | ★网表/脚表/BOM 三件 md5 前后逐字相同★ |
| ★**零改两道病闸的判据/阈值**★ | ★★**这两道闸的【判据】一个字不许动** ★ — ★★**本单是【诊断 + 加新闸】, 不是【把它们改绿】** ★★ ⇒ ★`SW/tools/check_debug_pin_order_contract.py` 与 `SW/tools/check_sw_board_md5_rebase_readiness.py` 的 md5 前后必须相同★ (★**除非你在交卷页里逐条论证「这处修改是修在产生点、且不放宽任何判据」并获 main 单独批准 ⇒ ★**默认不许改**★) ★ |
| ★零改既有页面正文★ | ★`SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 等已签收页 md5 与基线同★ |
| ★零挂链★ | ★`grep -c check_sw_gate_health state/gate_check.py` = 0★ |
| ★零外发★ | ★全程只读本机; ★`state/outbox/` 一个字节未动★ |
| ★不代拍★ | ★「要不要把那两道闸挂进门禁链 / 要不要修它们的 selftest」只登记 + 给代价, 不代裁★ |
| ★不自签台账★ | ★`state/issue_log.yaml` 你一个字节未动★ |
| ★没写别人的分片★ | ★只写 `state/fragments/sw.yaml`★ |
| ★证据分级★ | ★每条结论标五级之一★ |

★★**★你交卷时必须明确写一句: ★**这两道病闸【我修了没有、为什么修或不修】★ (★★**只诊断不修 = 可以接受, 但必须写清留给谁修、为什么本单不修**★★) ★★
