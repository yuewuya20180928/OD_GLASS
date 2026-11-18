# ISS-326 · mech-lead · ★★【cont2 续做 · 补三件 + 交卷页重排】★★

> ★**第二次续做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 16:25 (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: mech-lead (结构总工) · ★**verify_by**: main · ★**单号**: ISS-326 (★**status 保持 fixing**★) · ★**零外发**
> ★**性质**: ★**内部活 · 门禁/判据口径侧 · 纯分析 + 沙盒实跑类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★

---

## ★★★【★★main 16:2x 本机实读: cont1 (14:51→16:12, 跑了 1h21m) 死在哪 ★★★】★★★

★**★cont1 的会话在 16:12 结束, 最后一句话是 "I have the full picture now. Let me build the sandbox — first the builder script." ⇒ ★**它死在【建沙盒】这一步之前 ⇒ ⇒ ★**三件交付物一件都没做★ ★**

| 项 | ★main 实读 (16:2x)★ | ★状态★ |
|---|---|---|
| ★沙盒实证 ★ | ★`logs/iss326/sandbox/` **不存在** ⇒ ★**沙盒没建** ★ | ★⬜ ★ |
| ★处置表 ★ | ★`logs/iss326/mech_ref_disposition.tsv` **不存在** ⇒ ★**没做** ★ | ★⬜ ★ |
| ★闸设计稿 ★ | ★`logs/iss326/gate_design/` **不存在** ⇒ ★**没做** ★ | ★⬜ ★ |
| ★主交付页 `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` ★ | ★**4,868 B · mtime 14:57** · ★**只有 §0 (上一趟做了什么)** ★ | ★⬜ §3/§4/§5/§6 全缺 ★ |
| ★交卷页 `HANDOFF/2026-11-18_mech-lead_ISS326_*.md` ★ | ★**1,593 B · mtime 14:22** · ★B0~B6 **全是「(施工中)」占位** ★ | ★⬜ ★ |
| ★分片 `state/fragments/mech.yaml` 里 `iss326` 命中 ★ | ★**0** ★ | ★⬜ ★ |

★**★⇒ ⇒ 这一趟还是【那三件】(★cont1 的 brief 原样有效, 见 §③ 的三件清单★) + ★★交卷页按闸链口径重排★★ ★**

---

## ★★① ★★已落盘可复用的东西 (★不许重扫·不许重数★) ★★

| 产物 | 路径 | ★读数 (main 实读)★ |
|---|---|---|
| ★**全量命中表** ★ | `logs/iss326/mech_ref_hits.tsv` | ★577,679 B · **1,935 行** · 63 个 distinct 文件 ★ |
| ★**改名真集 + 保持集** ★ | `logs/iss326/mech_ref_universe.json` | ★218 条 (★改名 **186** / 不动 **32**★) ★ |
| ★**三口径对账** ★ | `logs/iss326/reconcile_counts_raw.txt` | ★口径A=**1,934** / 口径B=**1,282** / 口径C=**7,553** · 顶层==递归 (都是 112 文件) ★ |
| ★**扫描脚本 + 中间脚本** ★ | `logs/iss326/iss326_scan_mech_refs.py` · `iss326_reconcile_counts.py` · `iss326_reconcile2.py` · `iss326_reconcile3.py` · `iss326_reconcile4.py` · `iss326_reconcile5.py` · `iss326_reconcile6.py` | ★`reconcile2~6_raw.txt` 各自的读数也在盘上 ★ |
| ★**py-only 逐文件计数** ★ | `logs/iss326/reconcile6_raw.txt` | ★**py-only 精确真集 occ = 578** (★与 main 自己 grep 的 571 差 7★) · 逐文件: 57 `MECH/hinge_usb_check.py` / 39 `hinge_power_calc.py` / 36 `hw_cross_review_check.py` / 34 `check_board_frame_coords.py` / 34 `cross_review_check.py` / 31 `iss065_check.py` / 30 `board_port_opening_s6_check.py` / … ★ |

★**★⇒ ⇒ 「571 vs 1,934 vs 578」三个数是【三个不同口径】★ ★**:
- ★**main 的 571** = ★**前缀白名单**口径 (★`MECH/*.md` + `MECH/*.py` 里的特定前缀命中★) ★
- ★**你的 1,934** = ★**精确真集**口径 (★218 条真集逐条扫·递归★) ★
- ★**你的 578** = ★**py-only** 口径 (★只算 `.py`·不含 `.md`★) ★
★**★⇒ 交卷页三个都要给, 并写清差在哪 (★main 上一轮已经说过这条·别再只给一个数★)★ ★**

★**★★一个必须写进交卷页的 bug (★它就是「脚本会崩」的实例★)★★**:
★`logs/iss326/iss326_reconcile6.py` L79 ★**崩在 `occ = sum(len(rx.findall(l)) for l in cache[p] for p in sel)` ⇒ `KeyError: '/…/MECH/BOARD_ONEPASS_MECH_CLAIMS.md'`** ★ ⇒ ★**成因 = `cache[p]` 里的路径不在 cache 里 (★文件在扫描时点被别的东西改过 / 或缓存 key 与实际路径不一致·★你自己定位★)★ ⇒ ⇒ ★**要么修它, 要么在交卷页写明「这一轮口径枚举到此为止 + 为什么」★ ⇒ ★不许假装它没崩★ ★**

---

## ★★★【★★② ★★交卷页必须按【闸链的 6 块语义】重排 (★这是 Q1 掉到 14/18 的原因★★)】★★★

★**★main 16:1x 实跑 `gate_check.py` 的读数★**: ★**Q1 = 14/18** ⇒ ★**hw-lead 6/6 · sw-lead 6/6 · ★mech-lead 2/6, 缺 ['B2','B3','B4','B5']**★ ★
★**★⇒ ⇒ 你现在的交卷页 B 块名字和闸链要的不是一回事 (★现在: B2 沙盒实跑原始读数 / B3 边界自证 / B4 needs·answers / B5 交卷前必跑清单 / B6 给 main 的话★) ⇒ ⇒ ★**闸链要的是: B1 结论摘要 · B2 验收标准自评(逐条 通过/不通过/未验) · B3 证据分级(实测/官方/推算/0数据) · B4 接口取值声明(interface_claims) · B5 未决项与卡点 · B6 自证复现命令★ ⇒ ★★你必须按这六块重排 (★沙盒原始读数可以放进 B2 自评的证据引用里, 也可以另开 §, 但★**闸链要的那六块必须都在且有正文**★)★ ★

★**★⇒ ⇒ 另一条硬指标: Q2 证据分级率 = 2/3 (★mech-lead 无标签★) ⇒ ⇒ ★**你的交卷页里必须出现 `[实测]` / `[官方]` / `[推算]` / `[0数据]` 这几个标签 (★Q2 是按标签计的★) ⇒ ★**B3 块写全, 且正文里逐条标★ ★**

★**★⇒ ⇒ Q3 接口声明率: mech-lead 317 条 (★最多的三家之一★) ⇒ ★**B4 块里要写 interface_claims (★照抄判据脚本里的真实取值, 不许编★) ★

---

## ★★★【★★③ ★★这一趟要做的三件 (★cont1 的原 brief 原样有效, 这里只给落点与新增约束★) ★★★】★★★

### ★★① 「崩 / 假绿」沙盒实证 (★★不许只做静态推断★★) ★★

★**★铁律: 要验证「改名后」的行为, 就把【脚本 + 它读的数据】整棵树复制到 `tmp/iss326/` 再改 ⇒ ★**不许在真文件上改、改完再改回来 (★那叫擦产物, 不叫验证★)★ ★

★**★至少 4 条反向用例, 每条贴「期望红/绿」与「实际红/绿」★** (★cont1 brief 里的 4 条直接照做★):
① 把 `R_SEL_D0_N` 改成别的名字 ⇒ 那条判据必须变成不匹配 ⇒ ★**要证明它【红不出来】= 假绿** ★
② 把 `D_LED_G` 改掉 ⇒ `fps[LED_REF]` 必须抛异常 ⇒ ★**贴出异常类型与那一行** ★
③ 改一个【不该改的】ref (★`J_SOM_P1`——它在【不动的 32 个】里★) ⇒ ★**闸必须不受影响** ⇒ 证明你没误伤 ★
④ 注释里的 ref 名改成别的 ⇒ ★**闸必须不受影响** ⇒ 证明「注释里的 ref【不需要改】」 ★

★**★⇒ ⇒ 证据落 `logs/iss326/sandbox/`, 交付页 §3 逐条写读数★ ★**

### ★★② 处置表 (★1,935 行 → 按文件的清单·不重扫只做分类归并★) ★★

★**★三个必须分开的清单 (★不许混在一起★)★**:
1. ★**判据脚本** (★`MECH/check_*.py` / `cross_review_check.py` / `iss065_check.py` 等·★**要改**★) ★
2. ★**历史落地脚本** (★`_apply_*.py` / `_frag_update_*.py` / `rebase_*.py` / `_append_handoff_*.py` 等·★**跑完就没了 ⇒ 不需要改** ⇒ 列出来但标「历史脚本 · 不改」★) ★
3. ★**注释里的 ref** (★**单独标「注释 · 无功能影响」** ⇒ ★★main 上一轮在 ISS-320 交卷里见过同型事故: `MECH/service_port_check.py` L51 的型号名在注释里·被 md5 钉死·改不了也不该改★★) ★

★**★失效形态三选一, 逐条判, 不许留空★**: ★`红` (直接报错/判红) / ★`静悄悄不查了` (★判据分支再也匹配不上 ⇒ 【假绿】⇒ ★**这是最坏的一类, 排在前面★**) / ★`不受影响` ★
★**★⇒ 证据落 `logs/iss326/mech_ref_disposition.tsv`, 交付页 §4~§5 逐块写★ ★**

### ★★③ 「MECH 侧位号可达性闸」设计稿 (★★只给设计 + 反向用例, ★★不许挂进 `state/gate_check.py`★★) ★★

★**★SW 侧已有同款 `SW/tools/check_sw_ref_reachability.py` ⇒ ★**MECH 版要抄的是【那个闸的判据口径】, 不是重写一个弱版 ⇒ ★**先读它的源码, 再写设计稿** ★
★**★设计稿必须含: ① 扫描面 (`MECH/**/*.py` + `MECH/**/*.md` 递归·**不许只扫顶层**) ② 分类口径 (照抄 SW 那道的 C1/C2/C14 三类 + 冻结注册表的建闸日基线机制) ③ **fail-closed 三条** (照 SW 那道口径: 取不准必须判红, 不许放宽成「取最近一条」) ④ 反向用例 ≥ 5 条 ⑤ **基线数怎么定** (★SW 那道建闸日 `DESIGNATOR_MISSING` = 3 条 ⇒ ★**MECH 版必须自己 fresh 测, 不许抄 3**★)★ ★
★**★⇒ 证据落 `logs/iss326/gate_design/`, 交付页 §6★ ★**

---

## ★★④ 边界 (★违反就是不合格★) ★★

★**零写板** (★板 md5 必须还是 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**零改闸** (★`MECH/*.py` 一个字都不许改 ★⇒ 本单只出体检 + 设计稿★) · ★**零改既有文档正文** (★`MECH/**` 既有 md 只读★ ⇒ ★**只许写 `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` 这一个本单自己的产物★) · ★**沙盒只写 `tmp/iss326/` + `logs/iss326/`** ★ · ★**只写 `state/fragments/mech.yaml`** ★ · ★**零改 `state/gate_check.py`** ★ · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★ · ★**不许把整份大文件读进来** (★只 grep 你要查的行★)

★**★★★两条【操作层面的硬纪律】★★★**:
① ★**一次 write 的内容别超过 ~6000 字 ⇒ 先 write 骨架, 再用 edit 逐块补正文** ⇒ ★**cont1 就是死在一个超长 write 上 (16:12 lost active execution context)·★这一趟别再死一次★ ★
② ★**沙盒里凡要【写】的文件 ⇒ 一律真拷贝; 写前 `assert not os.path.islink(path)`** ⇒ ★**sw-lead 那边已经因为软链写穿过一次真件 (11-18 14:39 事故·11 份 `SW/*.md` 被改)·⇒ 这个坑在本项目已经踩过, 别踩第二次★ ★**

---

## ★★⑤ 交卷前必跑 (★原样输出贴进交卷页★) ★★

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
★**★交卷页另外自检: U+FFFD 乱码计数 = 0 · ★**`find tmp/iss326 -type l | wc -l` 必须 = 0 (★沙盒不许有软链★)★ ★**
