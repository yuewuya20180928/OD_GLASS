# ISS-326 · mech-lead · ★★【cont3 续做 · ★★先落骨架再干活★★】★★

> ★**第三次续做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 16:35 (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: mech-lead (结构总工) · ★**verify_by**: main · ★**单号**: ISS-326 (★**status 保持 fixing**★) · ★**零外发**
> ★**性质**: ★**内部活 · 门禁/判据口径侧 · 纯分析 + 沙盒实跑类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★

---

## ★★★【★★① ★★cont2 死因 (★不是你的错, 但必须改打法★)】★★★

★**★cont2 (16:26:04 起 · 6m1s · 72k tokens) 死于 ★**`LLM idle timeout (120s): no response from model`** (★16:32:33·★provider 侧抖动·同刻 sw-lead / hw-lead 两个会话都在正常跑⇒ **不是你的任务有问题**)★ ★
★**★但它 ★一个字节都没落盘★** (★交卷页还是 1,593 B · 交付页还是 4,868 B · 三件证据目录不存在 · 分片 `iss326` 命中 0·★它当时正在读 `SW/tools/check_sw_ref_reachability.py` 的源码★) ★

★**★⇒ ⇒ 连续两趟 (cont1 死在「建沙盒之前」· cont2 死在「读源码途中」) 都栽在同一个模式上: ★**先读一大圈, 再动手写 ⇒ 一挂就什么都没留下★★ ★**

## ★★★【★★② ★★这一趟的打法: ★★第一动作 = 落骨架 (不许先读★★】★★★

★★**★★第 1 个动作 (★5 分钟内必须做完·不许先读任何源码★)★★**:
1. ★**`write` 交卷页骨架**: `HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md` ⇒ ★**B0~B6 六块全在, 每块至少写「结论 + 待补」的实质句子 (★不许留「(施工中)」三个字·★那三个字就是占位符·★闸链会直接判缺块★)★ ★
2. ★**`write` 交付页骨架**: `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` ⇒ ★**§0 已有内容保留 + §1~§6 各留一段小标题 + 一句已知结论 (★从 §2 的命中表结论先填: 「571 / 1,934 / 578 是三个不同口径」·★这句你不用读源码就知道★)★ ★
3. ★**`python3 state/frag_write.py --agent mech-lead --add-need key=iss326_... to=main item="..."` 写 1 条分片** (★`iss326` 命中现在 = 0 ⇒ ★**哪怕只写一条也要先写下来**★) ★
⇒ ★★**做完这三步, 就算这趟再挂, 也留下了一个闸链认的骨架 ⇒ 下一趟就不是从零开始** ★★

★★**★★第 2 步才允许读源码, 且只准 grep 你要查的行 (★不许整文件读进来★)★★**: ★`SW/tools/check_sw_ref_reachability.py` 有 900+ 行 ⇒ ★**只 grep `EXPECTED|class |def |C1|C2|C14|baseline|freeze` 这些行** ★

---

## ★★★【★★③ ★★三件活的优先级 (★上下文/时间不够就按这个顺序砍★★)】★★★

★★**★★① 【处置表】最先交 (★纯归并, 不需要跑任何东西★) → ② 【闸设计稿】次之 (★只读源码, 不跑闸★) → ③ 【沙盒实证】最后 (★最费时★)★★ ★★**★★**交卷页宁可写「沙盒实证本轮未完成·留待下次续做」, ★★也不许留「(施工中)」这种占位符** ★★**

### ★★① 处置表 (★1,935 行 → 按文件归并, ★不重扫只做分类★) ★★

★**★三个必须分开的清单 (不许混在一起) ★★**:
1. ★**判据脚本** (★`MECH/check_*.py` / `cross_review_check.py` / `iss065_check.py` 等·★**要改**★) ★
2. ★**历史落地脚本** (★`_apply_*.py` / `_frag_update_*.py` / `rebase_*.py` / `_append_handoff_*.py` 等·★**跑完就没了 ⇒ 不需要改** ⇒ 列出来但标「历史脚本 · 不改」★) ★
3. ★**注释里的 ref** (★**单独标「注释 · 无功能影响」** ⇒ ★★main 上一轮在 ISS-320 交卷里见过同型事故: `MECH/service_port_check.py` L51 的型号名在注释里·被 md5 钉死·改不了也不该改★★) ★

★**★失效形态三选一, 逐条判, 不许留空★**: ★`红`(直接报错/判红) / ★`静悄悄不查了`(★判据分支再也匹配不上 ⇒ 【假绿】⇒ ★**这是最坏的一类, 排在前面★**) / ★`不受影响` ★
★**★⇒ 证据落 `logs/iss326/mech_ref_disposition.tsv` · 交付页 §4~§5★ ★**

### ★★② 「MECH 侧位号可达性闸」设计稿 (★★只给设计 + 反向用例, ★★不许挂进 `state/gate_check.py`★★) ★★

★**★SW 侧已有同款 `SW/tools/check_sw_ref_reachability.py` ⇒ ★**MECH 版要抄的是【那个闸的判据口径】, 不是重写一个弱版 ⇒ ★**只 grep 它的关键行, 再写设计稿** ★
★**★设计稿必须含: ① 扫描面 (`MECH/**/*.py` + `MECH/**/*.md` 递归·**不许只扫顶层**) ② 分类口径 (照抄 SW 那道的 C1/C2/C14 三类 + 冻结注册表的建闸日基线机制) ③ fail-closed 三条 (取不准必须判红, 不许放宽成「取最近一条」) ④ 反向用例 ≥ 5 条 ⑤ 基线数怎么定 (★SW 那道建闸日 `DESIGNATOR_MISSING` = 3 条 ⇒ ★**MECH 版必须自己 fresh 测, 不许抄 3**★)★ ★
★**★⇒ 证据落 `logs/iss326/gate_design/` · 交付页 §6★ ★**

### ★★③ 「崩 / 假绿」沙盒实证 (★最费时, ★排第三·★但铁律不变★) ★★

★**★铁律: 要验证「改名后」的行为, 就把【脚本 + 它读的数据】整棵树复制到 `tmp/iss326/` 再改 ⇒ ★**不许在真文件上改、改完再改回来 (★那叫擦产物, 不叫验证★)★ ★
★**★至少 4 条反向用例, 每条贴「期望红/绿」与「实际红/绿」★**:
① 把 `R_SEL_D0_N` 改成别的名字 ⇒ 那条判据必须变成不匹配 ⇒ ★**要证明它【红不出来】= 假绿** ★
② 把 `D_LED_G` 改掉 ⇒ `fps[LED_REF]` 必须抛异常 ⇒ ★**贴出异常类型与那一行** ★
③ 改一个【不该改的】ref (★`J_SOM_P1`——它在【不动的 32 个】里★) ⇒ ★**闸必须不受影响** ⇒ 证明你没误伤 ★
④ 注释里的 ref 名改成别的 ⇒ ★**闸必须不受影响** ⇒ 证明「注释里的 ref【不需要改】」 ★
★**★⇒ 证据落 `logs/iss326/sandbox/` · 交付页 §3★ ★**

---

## ★★④ 已落盘可复用 (★不许重扫·不许重数·不许整文件读进来★) ★★

| 产物 | 路径 | ★读数 (main 实读)★ |
|---|---|---|
| ★全量命中表 ★ | `logs/iss326/mech_ref_hits.tsv` | ★577,679 B · **1,935 行** · 63 个 distinct 文件 ★ |
| ★改名真集 + 保持集 ★ | `logs/iss326/mech_ref_universe.json` | ★218 条 (★改名 **186** / 不动 **32**★) ★ |
| ★三口径对账 ★ | `logs/iss326/reconcile_counts_raw.txt` | ★口径A=**1,934** / B=**1,282** / C=**7,553** · 顶层==递归 (112 文件) ★ |
| ★py-only 逐文件计数 ★ | `logs/iss326/reconcile6_raw.txt` | ★**py-only occ = 578** (★与 main grep 的 571 差 7★) · 逐文件: 57 `MECH/hinge_usb_check.py` / 39 `hinge_power_calc.py` / 36 `hw_cross_review_check.py` / 34 `check_board_frame_coords.py` / 34 `cross_review_check.py` / 31 `iss065_check.py` / 30 `board_port_opening_s6_check.py` / … ★ |
| ★中间脚本 ★ | `logs/iss326/iss326_scan_mech_refs.py` · `iss326_reconcile_counts.py` · `iss326_reconcile2.py`~`iss326_reconcile6.py` · `reconcile2~6_raw.txt` | ★都在盘上 ★ |

★**★「571 / 1,934 / 578」是【三个不同口径】, 交卷页三个都要给并写清差在哪★★ ★**
★**★★一个必须写进交卷页的 bug (它就是「脚本会崩」的现成实例)★★**: ★`logs/iss326/iss326_reconcile6.py` L79 崩在 `occ = sum(len(rx.findall(l)) for l in cache[p] for p in sel)` ⇒ `KeyError: '/…/MECH/BOARD_ONEPASS_MECH_CLAIMS.md'` ⇒ ★**要么修它, 要么写明「这一轮口径枚举到此为止 + 为什么」⇒ 不许假装它没崩** ★

---

## ★★⑤ ★★交卷页必须按【闸链的 6 块语义】重排 (★这是 Q1 = 14/18 的原因★★) ★★

★**★main 16:1x 实跑 `gate_check.py`: ★**Q1 = 14/18** ⇒ ★**hw-lead 6/6 · sw-lead 6/6 · ★mech-lead 2/6, 缺 ['B2','B3','B4','B5']**★ ★
★**★⇒ 你现在这版 B 块名字和闸链要的不是一回事 (现在: B2 沙盒实跑原始读数 / B3 边界自证 / B4 needs·answers / B5 交卷前必跑清单 / B6 给 main 的话) ⇒ ⇒ ★**闸链要的是: B1 结论摘要 · B2 验收标准自评(逐条 通过/不通过/未验) · B3 证据分级(实测/官方/推算/0数据) · B4 接口取值声明(interface_claims) · B5 未决项与卡点 · B6 自证复现命令★ ⇒ ★★按这六块重排 (★沙盒原始读数可以放进 B2 自评的证据引用里·但★**闸链要的那六块必须都在且有正文**★)★ ★**
★**★另两条硬指标: ★**Q2 证据分级率 = 2/3 (★mech-lead 无标签★) ⇒ ★**正文里必须出现 `[实测]` / `[官方]` / `[推算]` / `[0数据]` 标签 (★Q2 按标签计★)★** · ★**Q3 接口声明率: mech-lead 317 条 (★最多的三家之一★) ⇒ ★**B4 里要写 interface_claims (★照抄判据脚本里的真实取值, 不许编★)★ ★**

---

## ★★⑥ 边界 (★违反就是不合格★) ★★

★**零写板** (★板 md5 必须还是 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**零改闸** (★`MECH/*.py` 一个字都不许改 ⇒ 本单只出体检 + 设计稿★) · ★**零改既有文档正文** (★`MECH/**` 既有 md 只读 ⇒ ★**只许写 `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` 这一个本单自己的产物★) · ★**沙盒只写 `tmp/iss326/` + `logs/iss326/`** ★ · ★**只写 `state/fragments/mech.yaml`** ★ · ★**零改 `state/gate_check.py`** ★ · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★ · ★**不许把整份大文件读进来** (★只 grep 你要查的行★) ★

★**★★★三条【操作层面的硬纪律】★★★**:
① ★**一次 write 的内容别超过 ~6000 字 ⇒ 先 write 骨架, 再用 edit 逐块补正文** ★
② ★**沙盒里凡要【写】的文件 ⇒ 一律真拷贝; 写前 `assert not os.path.islink(path)`** ⇒ ★**sw-lead 那边已经因为软链写穿过一次真件 (11-18 14:39 事故·11 份 `SW/*.md` 被改)·这个坑在本项目已经踩过, 别踩第二次** ★
③ ★**★这一趟新增: 骨架先落盘 (★见 §② 的第 1 个动作★) ⇒ 宁可交一个"填了七成但块名齐全"的交卷页, 也不要交一个"内容全有但一个字没落盘"的空交卷页** ★

---

## ★★⑦ 交卷前必跑 (★原样输出贴进交卷页★) ★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/frag_write.py --agent mech-lead --add-artifact path=MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md summary="..."
python3 state/frag_write.py --agent mech-lead --add-artifact path="HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md" summary="..."
python3 state/merge.py   # rc 必须 0
python3 state/gate_check.py   # rc 必须 0 · ★★Q1 必须回到 18/18 (★缺的就是你 B2/B3/B4/B5★)★★
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
grep -c "iss326" state/fragments/mech.yaml   # 必须 >= 1
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md" MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md   # 必须 0 0
```
★交卷页另外自检: U+FFFD 乱码计数 = 0 · ★**`find tmp/iss326 -type l | wc -l` 必须 = 0 (★沙盒不许有软链★)★ ★**

★**★★★两条【main 16:33 实跑门禁链得到的现场读数】——你交卷时会对上, 先说清，免得你误判成自己的锅★★★** ★
1. ★**`gate_check.py` 现在 rc=1 (红) ⇒ 红在 SW 侧, 不是 mech 侧**: Q7 行下挂着 ★「新闸红: SW 侧位号引用可达性闸 (ISS-318)」⇒ 命中 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md:535~539` 里的 ★**反向测试夹具假位号** (`TP_TEMP_ISSX` / `TP_TEMP_ISSX2` / `CONN_USB_ISSX` / `U_TEMP_1`) ⇒ 真隐患 8 > 基线上限 3 ⇒ ★**那是 sw-lead 那边正在写 SOP 的中间态, 不是你的缺口 ⇒ ★不许你去改 SW 的文档 / 不许你去改闸 / 不许去动 `state/gate_check.py`★ ⇒ 你交卷时把这条红原样贴出来 + 写一句「红在 SW 侧 SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md, 与 mech 侧无关」即可** ★
2. ★**Q5「硬指标覆盖」现在 = 0/3 (三个总工都没报出 ≥3 类硬指标数字)⇒ ⇒ ★**你的交卷页里必须给出【至少 3 类带数字的硬指标】**(★例: 命中行数 1,935 · 真集 218 (改名 186/不动 32) · 三口径 1,934/1,282/7,553 · py-only 578 · 反向用例 4 条里 N 条红 N 条假绿·★)⇒ ★**Q5 是按页面上出现的数字种类算的 ⇒ 写具体数字, 别只写结论** ★** ⇒ ★★交卷页 B1 或 B2 里把硬指标列成一张小表, 便于 Q5 抓★ ★**

★额外纪律: ① 写分片必须用 state/frag_write.py (禁止 open(p,"w")) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ⑤ 交卷前跑 merge.py (rc=0) && gate_check.py (rc=0) 并把输出贴进回复
