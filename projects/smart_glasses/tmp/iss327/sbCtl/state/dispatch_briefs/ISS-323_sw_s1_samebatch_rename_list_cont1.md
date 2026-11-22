# ISS-323 · sw-lead · ★★cont1 续做: 补写分片 + 修 §4 标题乱码 + 重跑闸链★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-323 (★**cont1**★)
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 12:1x** ★
> ★**性质**: 内部活 · ★**纯分析 / 作业包 / 判据设计类 (SW 侧)** ★ · 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 沙盒只写 `tmp/` + `logs/iss323/` · 零外发 · 不替老板拍板 · 不自签 issue_log
> ★**上游**: `ISS-318` (SW 侧位号引用可达性闸 · verified) · `ISS-315` (判据链收口 · verified) · `ISS-321` (S1 改名对 SW 判据安全性体检 · verified) · `ISS-317` (S1 五侧改名可执行清单 · HW 侧同款范本 · verified)

---

## ★0 · ★★为什么有这一趟 cont (★main 12:1x 本机实读·不猜★)★★

★**上一趟 (11:4x 派出) 的子会话 `agent:sw-lead:subagent:fc903f9a-…` 在 12:0x 被父 cron run 连带 abort (★`status=timeout` · `abortedLastRun=true` · runtimeMs=1438900★)** ⇒ ★**它的工作在【写分片那一步】被打断** ★
★**⇒ 本单只剩 3 件事, 都很小 (§2)。★** ⇒ ★**★不要重做已经做完的活 (§1 那 5 件都已落盘·逐件验过)★** ★

---

## ★1 · main 12:1x 本机实读: ★**已经做完的 5 件 (逐件验过·不用重跑)★**

| # | 交付物 | main 实读结果 (★2026-11-18 12:1x★) |
|---|---|---|
| ① | ★**`SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md`** ★ | ★**73,571 B · 888 行 · §0~§6 七节全在 · 占位符扫描 = 0** ★ (★`§1` 7 件逐件 9 字段 · `§2` 第 7 件机器化改法 · `§3` 第 5 件夹具改法 · `§4` 第 6 件 md5 重锚 · `§5` 执行顺序 + 未决项 · `§6` 证据分级 + 复现命令 + 边界自证★) ★ |
| ② | ★**`HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md`** ★ | ★**32,099 B · 324 行 · B0~B7 七块齐全 · 占位符扫描 = 0** ★ |
| ③ | ★**`logs/iss323/`** ★ | ★**106 件 (★解析 + 沙盒 + 门禁 + 零写板四类都在★)** ★ |
| ④ | ★**`SW/tools/*.py` 全部 md5** ★ | ★**未变 (★零改闸已成立★)** ★ |
| ⑤ | ★**零写板** ★ | ★**板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未变** ★ |

★**★所以这一趟【不要重跑 80 次沙盒】·不要重做 §1 的 7 件清单·不要重新写那两份文档正文★** ★

---

## ★2 · 本单要交的 3 件事 (★做完就算交卷★)

### ★① ★★补写 `state/fragments/sw.yaml` (★本单的第一件事·也是上一趟唯一没做完的那件★)★★

★**main 12:1x 实读**: ★**`state/fragments/sw.yaml` mtime = 2026-11-18 11:12:06 ⇒ 早于本单开工 ⇒ 上一趟【一个字都没写进去】** ★
★**⇒ 交卷页 §B2 第 4 行「`state/fragments/sw.yaml` 已写」与 §B7 那行「只写 `state/fragments/sw.yaml`」, 在盘上【还没有对应事实】⇒ 这一趟必须把它变成真的** ★

★**写什么 (★照上一趟交卷页 §B0 交付物清单第 18 行自己定的口径★)**:
- ★**artifacts (≥3)**: `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (kind=doc) · `HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md` (kind=handoff) · `logs/iss323/` (kind=evidence) ★
- ★**needs_from (≥4)**: ★**ISS-321 交回的 4 条 need 抄进你自己的分片** ★ —— key 必须是这 4 个 (★一个字符都不许改★): `iss321_decide_rename_batch_scope` · `iss321_decide_r6_selftest_fixture_after_reboard` · `iss321_sw_docs_rename_bulk_24files` · `iss321_decide_rename_doc_notation` ★
  ★**★每个 item 必须按【本单的口径】写清「批不批 + 不批的后果」·不许只抄 ISS-321 的原文★** ★
  ★**★并且: `state/fragments/sw.yaml` 里这 4 条 key 可能已经存在 (★上一趟可能在被打断前写进去了一部分, ★main 实读: 4 条全部已存在, 各 1 命中★) ⇒ ★**★不许重复 add 同 key (⇒ merge 会报重复/冲突) ★ ⇒ 你必须先 `--show` 看现状, 只补缺的那几条, 并把 item 更新成你的口径 (★`frag_write.py` 没有 update 语义 ⇒ 若需要改 item, 用 `--set` 整段替换 `needs_from` 并把已有条目原样带上, ★**不许丢别人的条目**★)★** ★
- ★**interface_claims (≥1)**: ★**别人要照抄的东西逐字给** —— 至少一条是「★**第 2 件的别名解析层 / 第 3 件的改名无关探针三件套 / 第 4 件的跨域改法 / 第 7 件的机器化改法**」中的某一条 (★照交卷页 §B4 的写法★) ★
- ★**status**: `phase=delivered progress_pct=100 health=green summary="…"` ★

★**必须走原子写 (★禁 `open(p,"w")`★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/frag_write.py --agent sw-lead --show          # ★先看现状·确认哪几条已存在★
python3 state/frag_write.py --agent sw-lead \
  --add-artifact path=SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md kind=doc summary="…" \
  --add-artifact path="HANDOFF/2026-11-18_sw-lead_ISS323_SW侧同批改动可执行清单.md" kind=handoff summary="…" \
  --add-artifact path=logs/iss323/ kind=evidence summary="…" \
  --add-need key=iss321_decide_rename_batch_scope to=main item="…" since=ISS-321 \
  --add-claim key=… value="…" \
  --status 'phase=delivered progress_pct=100 health=green summary="…"'
# ★写完必须自证: ★
grep -c "iss323" state/fragments/sw.yaml          # ≥1
md5sum state/fragments/hw.yaml state/fragments/mech.yaml state/fragments/pm.yaml   # ★与开工前逐字节相同★
```
★**★`--add-need` 与 `--set` 互斥 (★`frag_write.py` 自己会报错拦你·别混用★)★** ★

### ★② ★★修 `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` §4 标题里的 1 个乱码字符★★

★**main 12:1x 实读**: ★**第 755 行** ★
```
## §4 · 第 6 件的板 md5 重锚 (★读法与落点 · 归步 S9★)
```
★**★那 2 个 U+FFFD 替换字符 (`\xef\xbf\xbd` ×2) 应该是「属」字 (★正确应为「归属步 S9」★) ⇒ ★**把它修成「归属步 S9」, 不许留替换字符★** ★

★**修法**: ★**只改那 2 个字节, 这一行其余部分逐字不动** ★ ⇒ ★**改完必须自证: 该行不再是 U+FFFD, 且全文 U+FFFD 计数 = 0** ★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 - <<'PY'
p='SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md'
raw=open(p,'rb').read()
bad=raw.count(b'\xef\xbf\xbd')
print('U+FFFD before =',bad)
raw=raw.replace('归步'.encode('utf-8'),'归属步'.encode('utf-8'))
open(p,'wb').write(raw)
raw2=open(p,'rb').read()
print('U+FFFD after =',raw2.count(b'\xef\xbf\xbd'))
PY
sed -n '755p' SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md
```
★**★这是「改既有文档正文」—— 上一趟的交卷页把它列成了边界④「零改既有文档正文」★ ⇒ ★**★所以你必须【在交卷页里明确写这一条例外】: 「★**本单为修 §4 标题的 2 个乱码字节, 对 `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` (本单自己新建的交付物) 做了 1 处定点订正 —— 它是本单自己的产物, 不是别人的既有文档; 其余 `SW/*.md` 真件 md5 全部不变**★」★★ ★

### ★③ ★★重跑闸链 + 补交卷页的 §B6 / §B7 (★因为分片变了, 交卷页里的读数必须是最新的★)★★

★**★上一趟交卷页 §B6 贴的闸链输出是 12:0x 的 —— 那是【分片还没写】时的读数 ⇒ 现在分片写完了, 必须重跑一次并把最新输出贴进去 (★§B2 第 4/5 行的「自评」也要跟着更新为「通过」并给出新读数★)★**

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py     # rc 必须 0 · Q1 必须 18/18
python3 state/issue_check.py                                # rc 必须 0
md5sum HW/PCB/demo_mainboard.kicad_pcb                       # = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb                 # = 2026-11-06 07:07:17.362193413
grep -c "iss323" state/fragments/sw.yaml                    # ≥1
```
★**★然后把交卷页的 §B6 换成这次的原样输出 + §B2 第 4/5 行 + §B7 的分片那行一起更新 (★★不改这两份文档的其它正文★)★** ★

---

## ★3 · 边界 (★一条都不许越★)

| # | 边界 | 自证方式 |
|---|---|---|
| 1 | ★**零写板** ★ | ★板 md5 + mtime 交卷前后逐字节相同 ★ |
| 2 | ★**零落表** ★ | ★网表 / 脚表 / BOM / 原理图源 md5 全部未变 ★ |
| 3 | ★**零改闸** ★ | ★`SW/tools/*.py` 全部 md5 未变 ★ |
| 4 | ★**零改既有文档正文** ★ | ★★**唯一例外 = §2-② 那 1 处乱码字节 (本单自己的产物·必须写进交卷页)★★** ★ |
| 5 | ★**不写别人的分片** ★ | ★**只写 `state/fragments/sw.yaml`** ★ (★`hw.yaml` / `mech.yaml` / `pm.yaml` 一个字节都不许碰★) ★ |
| 6 | ★**零外发** ★ | ★**不许发任何邮件 / 询价 / 问询 / 采购 ⇒ 缺口一律自己网上查 + 标证据等级 + 查不到写降级方案 ⇒ 没有「批一句可以发」这个选项** ★ |
| 7 | ★**不替老板拍板** ★ | ★4 条 need 交 main 拍 ⇒ 本单不代拍 ★ |
| 8 | ★**不自签 issue_log** ★ | ★`state/issue_log.yaml` 一个字节不许动 ★ |

---

## ★4 · 时间盒 (★本项目的老教训★)

★**整单 ≤ 30 分钟** ⇒ ★**本单只有 3 件事 (§2), 都是小活** ★ ⇒ ★**★如果 30 分钟还没做完, 停下来把已完成的部分交上来, 不许硬撑★** ★
★**★若你判断上一趟的沙盒读数需要复现, 只跑最小的那一组 (★`logs/iss323/iss323_verify_fix20.py` 一条即可★), 不许重跑全部 80 次★** ★

---
