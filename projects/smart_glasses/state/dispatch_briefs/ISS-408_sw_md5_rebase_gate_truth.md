# ★ISS-408 · sw-lead · 板那一趟【板 md5 重锚定的守门闸自己坏了】—— 病闸修可信 + 4 处漏登记引用面收口 ★

★**单号**: ISS-408 · ★**派活**: 项目总工 (main / moli) · ★**执笔**: sw-lead (软件总工) · ★**日期**: 2026-11-25
★**性质**: ★**纯查证 + 纯分析 + 追加式订正 + 反向用例 + 自有分片收口** ★ ⇒ ★**零写板 · 零落表 · 零改既有闸判据(★除非本单明确授权的那一处, 且必须追加式留痕★) · 零改既有页正文(★只许追加式★) · 零挂链 · 零外发 · 不代拍 · 不自签 `state/issue_log.yaml`** ★
★**主线关系**: ★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ 本单属 ★**「板只改一次」纪律 ① (先派纯分析/作业包类, 不动板)** ★

---

## ★0 · 一句话题面 ★

★★**「板那一趟」一旦重跑生成器, 板 md5 就会变 ⇒ SW 侧凡是引用板 md5 的地方都必须重锚定 ⇒ 守这道口的闸就是 `SW/tools/check_sw_board_md5_rebase_readiness.py` —— 而它自己今天就是红的 (5/7), 漏登记 4 处板 md5 引用面 + 漏登记 1 道硬钉板 md5 的闸 ⇒ ISS-388 交卷的 H0 点名的 2 道病闸里, ISS-398 修了另一道 (`check_sw_ref_reachability_v2.py`), 这一道至今没修 ⇒ 板那一趟当天, 「SW 侧有没有漏网的板 md5 引用」这件事零保证 ★★**

---

## ★★一 · 题面 (★main 2026-11-25 01:5x~02:0x 本机实跑, 不抄任何 agent 报告★) ★★

### ★1.1 · 本机实跑读数 (★main 亲手跑的原样读数★) ★

```bash
$ python3 SW/tools/check_sw_board_md5_rebase_readiness.py ; echo "rc=$?"
  [FAIL] H1 · SW 域板 md5 引用面必须被 §1 清单逐处覆盖 (★漏一处就红★)
        ⚠ ★扫描到 SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:23 (命中 1 处) 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红★
        ⚠ ★扫描到 SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md:241 (命中 1 处) 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红★
        ⚠ ★扫描到 SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md:215 (命中 1 处) 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红★
        ⚠ ★扫描到 SW/tools/check_sw_false_connectivity_gate.py:73 (命中 1 处) 但 §1 清单里没有这一行 ⇒ 漏登记 ⇒ 判红★
  [PASS] H2 · 每一处都必须标了【三类归属】+【处置】+ 备注
  [PASS] H3 · 【历史留证】类必须真的不许改 (★活判据不许伪装成历史留证★)
  [FAIL] H4 · SW 域每道【真钉板 md5 的判据脚本】必须登记在册 (类A 字面量 + 类B 页面内嵌基线)
        ⚠ ★SW 域有闸 SW/tools/check_sw_false_connectivity_gate.py 硬钉了板 md5 (类A·★.py 内 32 位字面量★) 但它没进 §2 的账 ⇒ ★下一道新闸再硬钉板 md5 就是从这儿溜过去的★ ⇒ 判红★
  [PASS] H5 · 每道闸要么已有合法改板通道, 要么在 §2 被登记成已知缺口
  [PASS] H6 · 板面零写板自证 (md5 / mtime / size 三项)
  [PASS] H7 · 证据等级五级白名单 + 正文零挂起措辞 + 零空洞词
闸结果 5/7 通过, rc=1
```

★**两条红的性质 (★这是本单的题★)** ★:
- ★**H1 红 = 真的漏登记 4 处** ⇒ ★**这不是假红, 是真漏** ⇒ 板 md5 一变, 这 4 处没人管 ★
- ★**H4 红 = 真的漏登记 1 道闸** ⇒ ★**`SW/tools/check_sw_false_connectivity_gate.py` 硬钉了板 md5 (源码内 32 位字面量) 但没进 §2 的账 ⇒ 「下一道新闸再硬钉板 md5 就是从这儿溜过去的」这条防线今天没有★**

### ★1.2 · ★为什么它偏偏卡在板那一趟的命门上 ★

| 事实 | 出处 |
|---|---|
| ★**ISS-388 交卷的 `SW/tools/check_sw_gate_health.py` H0 点名 2 道病闸: `check_sw_board_md5_rebase_readiness.py` + `check_sw_ref_reachability_v2.py`** ★ | ISS-388 交卷页 B3 (★main 本机复读该闸输出确认: H0 仍点名这两道★) |
| ★**ISS-398 已修好 `check_sw_ref_reachability_v2.py` (7/7 → ALL TESTS PASS)** ⇒ ★**只剩本单这一道病闸** ★ | ISS-398 交卷页 |
| ★**板那一趟 ⇒ 板 md5 必变 ⇒ SW 侧板 md5 引用面必须重锚定 ⇒ 这道闸就是那道守门闸** ★ | ★**它今天红 ⇒ 守门闸自己不可信 ⇒ 「板 md5 变了之后 SW 侧有没有漏网」零保证** ★ |
| ★**板 md5 18 天未动**: `611b869e13518c3c023fb178f91a0075` / mtime `2026-11-06 07:07:17.362193413` / size `4940213` ★ | 本机 `md5sum` + `stat` |

### ★1.3 · ★坏结局 ★

① ★**板那一趟当天板 md5 变了, 而 SW 侧有 4 处引用面从没人登记过** ⇒ ★**新 md5 落不进去 ⇒ 要么固件/台账拿着旧 md5 跑 (⇒ 改板闸误判), 要么没人说得清哪些地方要改 (⇒ 漏改)** ★
② ★**下一道新闸再硬钉一次板 md5, 一样从 §2 的账外溜过去** ⇒ ★**漏网机制本身没有守卫** ★
③ ★**「板只改一次」纪律被打破**: 板出去后才发现 SW 侧要跟着改 ⇒ 二次改动 (★代码侧虽不花板钱, 但会让板那一趟的收工判据失真⇒ 白跑一次 Gerber/投产包重出★)

---

## ★★二 · 本单交付 (★4 件 · 全部零写板★) ★★

| # | 交付物 | 路径 | 验收口径 |
|---|---|---|---|
| ① | 真相页 | ★**新建** `SW/BOARD_ONEPASS_SW_MD5_REBASE_GATE_TRUTH.md` ★ | §0~§6 + 机器块; ★**逐条**写清: H1 那 4 处漏登记【分别是什么内容 · 属于三类归属的哪一类 · 该怎么处置 · 谁负责】 ★ H4 那道漏登记的闸【它硬钉的板 md5 是哪个字面量 · 为什么该进 §2 · 登记后怎么防下一道新闸再溜】 ★ ★**另附: 「板 md5 变了之后 SW 侧要动哪几处」的总清单** ★ |
| ② | ★**收口动作 (★本单的核心★)** ★ | ★**追加式** 写进 `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 的 §1 / §2 ★ | ★**4 处漏登记逐条补进 §1 清单 + `check_sw_false_connectivity_gate.py` 补进 §2 账** ⇒ ★**追加式: 老字一字未删 (★用 md5 前缀比对自证★) ★** ⇒ ★**正文若需要改, 一律写成追加式订正块, 不许改正文 ★** ★ |
| ③ | 交卷页 | ★**新建** `HANDOFF/2026-11-25_sw-lead_ISS408_板md5重锚定守门闸修可信.md` ★ | B1~B7 全填 (★标题用仓里规范口径, gate_check Q1 六块齐全★) ★★**必须贴出收口前后 `check_sw_board_md5_rebase_readiness.py` 的原样输出 + rc 对比** ★★ |
| ④ | 自有分片收口 | `state/fragments/sw.yaml` | ★**只走 `state/frag_write.py`** ★ (★禁止 `open(p,"w")`★) · 写后四项自检: 条数 / 丢 key / 多的 key / 内容有变的条 (★老条目逐字比对★) |
| ⑤ | 留证 | `logs/iss408/` + 沙盒 `tmp/iss408/` | ★**不硬链接真件 · 不写系统 `/tmp`** ★ |

### ★2.1 · ★必须有的自证 (★本单的关键在于「证明这条闸真的有牙齿」★) ★

| 判据 | 要求 |
|---|---|
| ★**S1 收口前红 ⇒ 收口后绿** ★ | ★**`python3 SW/tools/check_sw_board_md5_rebase_readiness.py` 收口前 rc=1 (H1/H4 红) ⇒ 收口后必须 rc=0** ★ (★若收口后仍红, 说明漏的不止这 5 条 ⇒ 继续查, 查到绿为止, 或如实写明还剩什么★) ★ |
| ★**S2 反向用例 (★防「把红灯调没」★)** ★ | ★**必须构造至少 3 条反向用例**: ① 把 §1 清单里某一行删掉 ⇒ 闸必须红 (⇒ 证明 H1 真在读清单) ② 把 §2 账里 `check_sw_false_connectivity_gate.py` 那行删掉 ⇒ 闸必须红 (⇒ 证明 H4 真在读账) ③ 在盘上某处新加一处板 md5 引用面而不登记 ⇒ 闸必须红 (⇒ 证明「漏登记会被抓」这条机制活着) ★★**三条逐条贴原样输出★** ★ |
| ★**S3 追加式自证** ★ | 收口前后 `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 的 md5 前缀比对 (★改前全文 = 改后前缀★) ⇒ 老字一字未删 |
| ★**S4 板三证不动** ★ | 板 / 网表 / 脚表 / BOM md5 与基线逐字相同 (★基线板 md5 = `611b869e13518c3c023fb178f91a0075`★) |
| ★**S5 零挂链 + 零外发自证** ★ | ★**本单不许把自己的名字挂进 `state/gate_check.py`** (★`check_sw_board_md5_rebase_readiness.py` 本来就没挂 ⇒ 本单也不许挂⇒ `grep -c` = 0★) ★; `state/outbox/` 未动 |
| ★**S6 证据分级** ★ | 每条结论标 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` |

★**★注意 (★主线的纪律, 别踩★)★**: ★**本单【不许】为了让闸变绿去改那 4 处引用面的正文** (★`SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` / `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` 是已签收页, 正文一字不许改★) ⇒ ★**只补登记 (让漏登记消失), 不改被登记的内容★** ⇒ ★**若某处的内容本身是错的 (⇒ 该由谁修), 写成 needs_from 交 main, 一条都不许代拍★** ★

### ★2.2 · 必跑命令 (★交卷页 B6 要贴原样输出 + rc★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-408_sw_md5_rebase_gate_truth.md   # 期望 rc=0
python3 SW/tools/check_sw_board_md5_rebase_readiness.py            # ★收口前 rc=1 (★H1/H4 红★) ⇒ 收口后必须 rc=0★
python3 SW/tools/check_sw_gate_health.py                            # ★ISS-388 那道闸不许被本单弄红 (★H0 点名的病闸名单不许变长★)
python3 SW/tools/check_onepass_sw_sync.py                          # ★SW 侧合法改板通道闸不许被本单弄红 (★读数须与开工前一致★)
python3 state/merge.py                                              # rc 必须 0
python3 state/gate_check.py                                         # rc 必须 0 · Q1 必须 18/18
```

### ★2.3 · 边界 (★违反任一条 = 本单不算交卷★) ★

| 边界 | 怎么自证 |
|---|---|
| ★**零写板** ★ | 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` + size `4940213` 三项逐字未动 |
| ★**零落表** ★ | 网表 / 脚表 / BOM md5 逐字未动 |
| ★**零改既有页正文 (★只许追加式★)** ★ | `SW/BOARD_ONEPASS_SW_MD5_REBASE_READINESS.md` 的 md5 前缀比对 (★老字一字未删★) + `SW/BOARD_ONEPASS_ZERO_FALSE_CONNECTIVITY.md` / `SW/EVT_CHARGE_CURRENT_CRITERION_CALIBER.md` / `SW/tools/check_sw_false_connectivity_gate.py` 三件 md5 逐字未动 |
| ★**零挂链** ★ | `grep -c check_sw_board_md5_rebase_readiness state/gate_check.py` = 0 (★它本来就没挂★) |
| ★**零外发** ★ | ★**不许发任何邮件 / 询价 / 问询 / 采购** (★老板 2026-11-11 19:31 + 2026-11-12 02:02★) ⇒ `state/outbox/` 22 件逐字未动 ⇒ **没有「批一句可以发」这个选项** ★ |
| ★**不代拍** ★ | 「这 4 处该怎么处置 / 那道闸归不归 §2 / 板 md5 变了以后谁先动」 ⇒ 交 main, 机器块写 `not_decided_here` |
| ★**不自签** ★ | ★**不许写 `state/issue_log.yaml`** ★ |

---

## ★★三 · 纪律 (★与其它单一样的硬规矩★) ★★

① ★**写分片必须用 `state/frag_write.py`** (★禁止 `open(p,"w")`★)
② ★**只写本任务允许的文件, 不碰别人的** (★`HW/` · `MECH/` 一页都不许写★)
③ ★**证据分级** `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 必须标
④ ★**不许外发任何邮件/询价/问询/采购** ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案
⑤ ★**交卷前跑 `python3 state/merge.py` (rc 必须 0) && `python3 state/gate_check.py` (Q1 必须 18/18) 并把输出贴进回复** ★

## ★★四 · 留给 main 的问句 (★你只摆代价, 一条都不许代拍★) ★★

- ★**Q1**: H1 那 4 处漏登记的引用面, 该按「历史留证」还是「活判据」归属? (★归属不同 ⇒ 板 md5 变了以后要不要跟着改, 结论相反★)
- ★**Q2**: `check_sw_false_connectivity_gate.py` 硬钉板 md5 ⇒ 是补进 §2 账, 还是把它改成走合法改板通道 (★后者要动已签收闸 ⇒ 需重签★)?
- ★**Q3**: 这道守门闸要不要挂进 `state/gate_check.py`? (★它今天红 ⇒ 挂上去当天链会红★)
- ★**Q4**: 「板 md5 变了以后 SW 侧要动哪几处」的总清单要不要成为板那一趟的必过项?
- ★**Q5**: 本单要不要再补一道独立新闸 (★守「漏登记机制本身」★), 还是把反向用例固化进既有闸的 `--selftest`?
