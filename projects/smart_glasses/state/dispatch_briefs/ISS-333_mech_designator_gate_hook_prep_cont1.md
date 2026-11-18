【ISS-333 · mech-lead · ★★cont1 续做单 · ★★只补交卷页 + 分片 + 闸复跑 rc 落盘 · ★★★不许重写那道闸脚本★★★】

★**★这一趟不是从零·是【收卷】·你上一趟 19:40 被掐, 成果大部分在盘, 缺的是【交卷三件套】★★**

---

## ★★★【① 发生了什么 (★先读完这段再动手★)★★★】★★★

★**你的上一趟会话在 19:40:47 被掐断 (★最后一条 toolResult 是「Aborted」★) ⇒ ★**会话没了, 但你落的东西全在盘上** ★★

★**main 20:4x 本机独立复核 (★不抄你的报告★·逐条自己跑过★)**:

| ★件★ | ★main 实读/实跑★ | ★判★ |
|---|---|---|
| ★**闸脚本★** | ★`MECH/tools/check_mech_ref_reachability.py` · **56,550 B · 19:36** ★ ★**main 本机实跑 `--selftest` ⇒ rc=0 · 反向用例 14/14 通过 (MC-1~MC-14)** ★ | ★**在盘且绿** ★ |
| ★**证据目录★** | ★`logs/iss333/` **8 件** (★`baseline_repro.json` / `baseline_repro_raw.txt` / `freeze_guard.txt` / `freeze_registry_output.txt` / `gate_dump_classification.txt` / `gate_main_run.txt` / `repro_baseline.py` / `repro_iss326_caliber.py`★) ★ | ★**在盘** ★ |
| ★**★交卷页★** | ★`HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` ★**不存在** ★ | ★**缺** ★ |
| ★**★分片★** | ★`grep -c "iss333" state/fragments/mech.yaml` ⇒ **0** ⇒ ★**你一个字都没写** ★ | ★**缺** ★ |
| ★**★挂闸★** | ★**main 已于 20:2x 把你这道闸挂进 `state/gate_check.py` 的 `EXTRA_GATES` (★ISS-330, owner=main, 已落 fixed★) ⇒ ★**挂完五道闸 rc 全绿** ★ | ★**已完成** ★ |

★**⇒ main 20:2x 给兄弟 job 的处置指令 (★DECISION_INDEX_2026-11-18.md §P-2 第 1 条逐字★)**:
★**「建议派 mech-lead 一条【只补交卷页与分片·不许重写闸脚本】的续做单 (★★闸脚本本轮已被 main 挂链 ⇒ 【不许再改它】·改了链上那道闸就与盘面不一致了★)」** ★

---

## ★★★【② ★★★这一趟的★绝对边界 (★越线即不合格★)★★★】★★★

★★**① 【★最要紧的一条★】不许改 `MECH/tools/check_mech_ref_reachability.py` 的任何一个字节** ★★
- ★**为什么**: ★**它已经进了 `state/gate_check.py` 的 `EXTRA_GATES` ⇒ 链上跑的就是它** ⇒ ★**你改它 ⇒ 链上那道闸与盘面不一致 ⇒ 全项目门禁失真** ★
- ★**你要是觉得它有 bug** ⇒ ★**不许自己改** ⇒ ★**写进交卷页 B5 (写清: 现象 / 复现命令 / 你建议怎么改 / 为什么不许你自己改) ⇒ 交 main 拍** ★

★★**② 零改 `state/gate_check.py`** (★挂闸 = main 的机制地界·★挂闸已做完★) ★★ · ★★**③ 零改 `SW/tools/check_sw_ref_reachability.py`** (★只读 import·★不许动·它已经在链上) ★★
★★**④ 零写板** (★`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` · mtime 必须还是 `2026-11-06 07:07:17.362193413`★) ★★
★★**⑤ 零落表** (★网表 / 脚表 / BOM / 原理图真源一个字节不许动★) ★★ · ★★**⑥ 零改既有 `MECH/**/*.md` 正文 · 零改既有 `MECH/**/*.py`** (★你只许新建交卷页 + 写分片 + 写 `logs/iss333/` 里的新证据 + 写 `tmp/iss333/`★) ★★
★★**⑦ 零改 `logs/iss326/`** (★那是已落的交卷证据·只读★) ★★ · ★★**⑧ 零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ **没有「批一句可以发」这个选项**★) ★★
★★**⑨ 不替老板拍板 · 不自签 `state/issue_log.yaml` · 不改 `state/gate_check.py` · 不动别人的分片 (★只写 `state/fragments/mech.yaml`★)** ★★
★★**⑩ ★★交卷页必须放在 `HANDOFF/`, 不许放 `MECH/`** (★理由见 ③ 的第 2 条★) ★★

★★**★① 沙盒只写 `tmp/iss333/` + `logs/iss333/`** ★★ · ★★**② 沙盒里凡要【写】的文件 ⇒ 一律真拷贝; 写前 `assert not os.path.islink(path)`** (★sw-lead 11-18 14:39 因为软链写穿过一次真件★) ★★
★★**③ 一次 write 别超过 ~6000 字 ⇒ 先 write 骨架, 再 edit 逐块补** (★你自己连挂两趟都死在超长 write 上·★先落骨架, 再干活★) ★★
★★**④ 交卷页里不许出现「(施工中)」/「待填」/「PLACEHOLDER」占位符** ★★

★★**★★文档纪律 (★这一条现在【更凶】了·★因为闸已经进链★)★★**:
★★**MECH 侧任何要写「改名后位号」或「形状像位号但不是位号」的文档 ⇒ ★★写进 `logs/iss333/`, 不许写进 `MECH/`★★ ★
★★**理由 (★实测过★)**: ★**闸的扫描面 = `MECH/**/*.md` + `MECH/**/*.py` 递归 ⇒ 你在 `MECH/` 任何一个 .md 里写死一个盘上没有的位号 ⇒ 闸当场判「新增真隐患」⇒ rc=1 ⇒ ★**门禁链当场变红, 而且是你一个人把全项目的门禁弄红的** ★★** ⇒ ⇒ ★**交卷页放 `HANDOFF/` (★不在扫描面里★) 是刻意的, 不许挪进 `MECH/`** ★★**

---

## ★★★【③ 这一趟要交的三件 (★就这三件·★其余都已完成★)★★★】★★★

### ★★★★【第 ① 件: 交卷页 (★新建★)★★★★★★
★**路径**: ★`HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` (★中文名照 ISS-326 交卷页命名法★) ★

★**结构 = B0~B6 齐全 (★照 `HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md` 的章节法★)**:

| ★段★ | ★必须写到什么程度★ |
|---|---|
| ★**B0** ★ | ★**一句话结论 (给 main 的一句话)** + ★**交付物清单 (逐件列路径 + 字节数 + 落盘状态)** ★ |
| ★**B1** ★ | ★**硬指标表** (★至少含这 7 类具体数字: ①闸脚本字节数 ②`--selftest` 反向用例 N/N ③建闸日基线 16 与今天复现值 14 与交付上限 10 三个数各是什么 ④扫描面 md 份数 + py 份数 + 合计 ⑤唯一 token 数 ⑥基线真隐患条数 ⑦C17 已登记非位号条数 + 未登记新增真隐患条数★) + ★**结论条目 (★至少 5 条, 逐条一句话★)** ★ |
| ★**B2** ★ | ★**逐条「通过 / 不通过 / 未验」自评** (★对着原 brief 的 5 条硬要求 + 4 件交付物逐条判★) ★ |
| ★**B3** ★ | ★**每条结论标证据等级** (★`[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`★) ★★**本单几乎全是 `[实测]`** (★MECH 域内部事·没有官网/媒体成分; ★凡是你没亲手跑过的, 老实标 `[0数据]` 或 `[推算]`★) ★ |
| ★**B4** ★ | ★**接口取值声明 (interface_claims)**: ★**这一段改成【事实记录】而不是【挂闸提案】** ★ (★因为 main 已经挂了★) ⇒ ★**逐字抄 `state/gate_check.py` 里 `EXTRA_GATES` 那一行 (★连注释一起·★它写明了挂闸理由与 fail-closed 语义★) + ★**贴挂完之后 `state/gate_check.py --json` 的 `extra_gates` 里这道闸的那一行 (★名字 + ok + detail·★★查法见 ③ 第 ③ 件★★) + ★**贴挂完之后的五门 rc (★merge / gate_check / issue_check / stage_gate / daily_check·★哪个红哪个绿如实写·★别粉饰★)** ★★**并明确写一句: 「挂闸已由 main 于 2026-11-18 20:2x 执行 (ISS-330) ⇒ 本单只交闸脚本与证据, 不再出挂闸提案」** ★ |
| ★**B5** ★ | ★**未决项与卡点**: ★**逐条写清「不写会怎样」** ⇒ ★**若你觉得那道闸还有缺陷 (★但你被禁止自己改·见 ②①★) ⇒ 就在这里提出来交 main 拍** ★★**不许留空** ★ |
| ★**B6** ★ | ★**自证复现命令 (原样贴输出)**: ★**必跑清单见 ④·★每条原样贴 rc 与关键输出★** ★ |

★**★B4-3 特别要求 (★原 brief 第 ③ 件的第 3 小问·★main 已经替你实测了·你把数字对上★)**:
★**「挂了会不会把现在的门禁链带红」⇒ ★**答案 = 【不会·实测带绿】** ⇒ ★**你写交卷页时必须把【挂闸后五门 rc】的原样输出放进去 ⇒ ★**这就是「没带红」的直接证据·★不许只写一句「没红」** ★

★**★B1 里必须回答的那个算术 (★main 20:1x 已独立复算过·你照实写并把两边的数都放上去★)**:
★**「ISS-326 设计稿说基线 16 ⇒ 你的闸为什么交付 10?」** ⇒ ★**答案 = 【16 是建闸日口径, 你今天同口径复现 = 14 (★剔本单自污染 10 + 剔 py 变量名 38★); 交付上限 10 = 建闸日 16 里活着的 9 条 + 从 py-only 粗口径扫回来的 1 条 `D_ESD_CHG` ⇒ ★**净效果是【上限 16→10, 收 6 条】且多抓一条 py 真隐患 ⇒ **方向是收紧不是放宽**★** ★

### ★★★★【第 ② 件: 分片 (★`state/fragments/mech.yaml`·★现在命中 0 处·★必须写进去★)】★★★★
★**必须走**: ★`python3 state/frag_write.py --agent mech-lead ...` (★★禁止 `open(p,"w")`★★) ★
★**至少写这四类** (★格式照 `state/fragments/mech.yaml` 里 `iss326_*` 那几条的写法★):
- ★**artifact**: ★`MECH/tools/check_mech_ref_reachability.py` (★path + summary + kind + version★) · ★`logs/iss333/` (★目录·kind=logs★) · ★`HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` (★交卷页★) ★
- ★**claim**: ★**至少 3 条** ⇒ ★**① 基线口径 (建闸日 16 / 今天复现 14 / 交付上限 10·逐条带出处) ② 反向用例 14/14 与「假绿」那条 (MC-14) 的判读 ③ 挂闸事实 (main 20:2x 已挂进 EXTRA_GATES·★本单不改它·★)** ★
- ★**need**: ★**若你发现需要 main 拍板的事 (★尤其是那道闸的缺陷·因为你被禁止自己改★) ⇒ 在这里登记 `to=main` 的 need ⇒ ★**不许自己改闸** ★★**若没有 ⇒ 老实写「无」** ★
- ★**status**: ★`--status phase=... progress_pct=... health=... summary=...` ⇒ ★**phase 照项目既有口径填 (★先读 `state/fragments/mech.yaml` 里最近几条的 phase 取值★)·progress_pct 你自己判·★不许写 100 (★交卷还没签字★)** ★

### ★★★★【第 ③ 件: 挂闸后的闸复跑 rc 落盘 (★新增的一件·★因为闸已经进链了★)】★★★★
★**原来的 `logs/iss333/gate_main_run.txt` 是 19:38 的【挂闸前】读数 ⇒ ★**挂闸后必须重跑一遍, 落成新文件** ⇒ ★**新文件叫 `logs/iss333/gate_run_posthook.txt`** (★★不许覆盖旧的 19:38 那份·★那是你交卷前的原始证据·★删了等于毁证据★★) ★
★**跑法**: ★`python3 MECH/tools/check_mech_ref_reachability.py` (★裸跑·★不带 `--selftest`★) ★ + ★`python3 MECH/tools/check_mech_ref_reachability.py --selftest` (★自测★) ★
★**并把 `python3 state/gate_check.py` 的完整输出落成 `logs/iss333/gate_check_posthook.txt`** ⇒ ★**从里面摘出「那道闸那一行」贴进交卷页 B4** ★

★★**★那条线在哪 (★main 20:5x 本机实跑踩过这个坑·★省你一趟★)★★**:
★**`extra_gates` 这一段【只出现在 `--json` 模式里】⇒ ★**默认 stdout (62 行那种) 【根本不打印 extra_gates】⇒ 你要是只 `grep` 默认输出, 会以为「链上没这道闸」⇒ ★**那是找错地方了, 不是闸没挂上** ★★
★**正确的查法 (★main 20:5x 实跑·rc=0·8 道 extra_gates 全绿★)**:
```bash
python3 state/gate_check.py --json > /tmp/gc.json
python3 -c "import json; d=json.load(open('/tmp/gc.json')); [print(g.get('ok'), '|', g.get('name'), '|', str(g.get('detail'))[:120]) for g in d.get('extra_gates') or []]"
```
★**main 20:5x 实跑的读数 (★你落盘时应当能逐字对上·★对不上要写进 B5★)**:
```
True | MECH 结构结论防漂闸 (ISS-295) | 全部检查项通过
True | SW 侧板侧输入/合法改板闸 (ISS-298) | 全部检查项通过
True | SW 侧位号引用可达性闸 (ISS-318) | 全部检查项通过
True | SW 侧落表留痕义务闸 (ISS-315) | 全部检查项通过
True | SW 侧 R6 硬保护路径反向用例 (ISS-315) | 全部检查项通过
True | SW 侧 R6 链头落表单号交叉核对反向用例 (ISS-312) | 全部检查项通过
True | SW 侧 R6 判决源反向用例 (ISS-309 · 7/7) | 全部检查项通过
True | MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现) | 全部检查项通过     ← ★★就是这一行★★
```
★**⇒ 你交卷页 B4 要贴的那一行, 就是最后那一行 (名字 = 「MECH 侧位号引用可达性闸 (ISS-326 设计稿 / ISS-333 实现)」· ok=true · detail=「全部检查项通过」) ★ ★**

---

## ★★★【④ 交卷前必跑 (★原样输出贴进交卷页 B6★)★★★】★★★
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/tools/check_mech_ref_reachability.py --selftest   # 必须 rc=0 (★反向用例 14/14★)
python3 MECH/tools/check_mech_ref_reachability.py               # 必须 rc=0
python3 state/merge.py                                          # rc 必须 0
python3 state/gate_check.py                                     # rc 必须 0 (★★这道闸已经在链上了·★它红就是链红★)
python3 state/issue_check.py                                    # rc 必须 0
md5sum HW/PCB/demo_mainboard.kicad_pcb                          # 必须 611b869e13518c3c023fb178f91a0075
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb                    # 必须 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md"   # 必须 0
grep -c "iss333" state/fragments/mech.yaml                      # 必须 >= 1 (★现在 0★)
find tmp/iss333 -type l | wc -l                                 # 必须 0
git status --porcelain MECH/tools/check_mech_ref_reachability.py state/gate_check.py SW/tools/check_sw_ref_reachability.py   # ★必须证明你一个字节都没动★
```
★**★最后一条 (`git status`) 是本单的自证核心: ★**证明那道闸 + 门禁链 + SW 那道闸 你都没碰** ★★**

★**★另外两件必须留痕的 (★main 会核★)**:
1. ★**闸脚本字节数与 mtime 必须还是 56,550 B / 2026-11-18 19:36** ⇒ ★**变了 = 你改过它 = 直接不合格** ★
2. ★**`MECH/**/*.md` 与 `MECH/**/*.py` 逐字节未变** ⇒ ★**main 挂闸前跑过一次「114 份文件跑闸前后逐字节未变」·你这一趟做完也要能证明这一点 (★`git status --porcelain MECH/` 必须只出现 `MECH/tools/check_mech_ref_reachability.py` 一个新增项★) ★

---

## ★★★【⑤ 一句话 (★这一趟到底在回答什么★)★★★】★★★
★**不是「再把闸做一遍」·★是「你那道闸已经由 main 挂进全项目门禁链了 ⇒ 现在缺的是【交卷页 + 分片 + 挂闸后 rc 落盘】⇒ ★**把这三样补上, 这一单才算交卷 (★「磁盘上已落表」与「这一单交卷了」是两件事★)」★ ★**

★**★交完 main 会做三件事 (★你交的时候可以按这个口径组织 B5★)★**:
1. ★**main 独立复核交卷页 + 分片 + 闸复跑 rc (★不抄你的报告★) ⇒ 通过 ⇒ 签 `fixing → verified` (★这一单不归你签★)** ★
2. ★**main 把你这道闸挂链后的最终读数写进项目台账 ⇒ 下一轮「板只改一次」那一趟时, MECH 侧的漂移会被机器当场抓住** ★
3. ★**main 把你 B5 里提的 need 逐条拍板 (★派给谁 / 改不改 / 降级方案·★不许挂「等外部回复」★)** ★
