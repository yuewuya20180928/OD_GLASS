# ISS-321 · sw-lead · 任务书 —— ★★【「板只改一次」那一趟的 SW 侧: S1 位号改名【会不会把 SW 判据炸掉】—— 逐条实测 + 逐字改法】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-321
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 10:2x** ★
> ★**性质**: 内部活 · 纯分析 / 作业包 / 判据设计类 (SW 侧) · ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 沙盒只写 `tmp/` · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★0 · ★为什么是这一单 (★main 10:2x 本机实读★) ★

★**主板那一趟要做的事 (★老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」★)**: ★**位号改名 + 板侧同步 + 布局修正 + 布线 45→0 + Gerber/投产包重出 ⇒ 板只改一次 ⇒ 所有前置必须一次查清** ★

★**已知的三个事实 (★前两个已经算清, 第三个没人做★)**:
1. ★**HW 侧**: ISS-314/ISS-317 实测 ⇒ ★**S1 改名 (五侧同口径, 186 个要改) 会把 `state/check_pcb_nets.py` 炸掉** (NC 白名单 `J_USB_C` 撞死 + `--selftest` 自己崩) ★**⇒ SW 侧呢? 没人查过** ★
2. ★**SW 侧**: ISS-318 (verified · main 10:2x 独立复核) 已建 `SW/tools/check_sw_ref_reachability.py` (★改名漂移闸★) · ★**它自己是 rename-safe 的 (反向用例 RC-6 证明)★** ⇒ ★**但 SW 侧【另外 12 道脚本闸】呢? 没人查过** ★
3. ★**main 10:2x 的粗扫起点 (★给你省一半时间, 但别信它的精度★)★**: `grep -rhoE "\b(R|C|U|L|D|Q|TP|CONN|J|SW|K|F|B|T|JP)_[A-Z0-9_]{1,14}\b" SW/tools/*.py` ⇒ ★**13 个文件命中** (`check_demo_panel_spec.py` · `check_load_switch_selection.py` · `check_onepass_sw_sync.py` · `check_shutdown_semantics.py` · `check_sw_ref_reachability.py` · `check_timing_review_adc_sync.py` · `demo_e2e_budget.py` · `isp_budget_solve.py` · `iss263_extra_probe.py` · `model_asset_check.py` · `rknn_bench.py` · `s2_board_judge.py` · `timing_check.py`) ★
   ★**★但这个粗扫【不精确】**: ★**`SW_MD5_ANCHORS` / `Q_AND` / `SW_TIMING_REVIEW` 这类是常量名不是位号 ⇒ 必须拿 §1 的真集逐个核, 不许靠前缀猜** ★

---

## ★1 · 输入 (★全在盘上, ★只读, 不许改★) ★

| 落点 | 内容 |
|---|---|
| ★**`logs/iss317/rename_list_raw.txt` (58,695 B)** ★ | ★**★218 行逐条改名对照表 (脚表侧旧ref / 板侧旧ref / 原理图侧旧ref → 新ref(kicad_ref 口径) + 改哪个真源 + 动/不动 + 改完的预期读数 + 依赖顺序)★ ★** ⇒ ★**这是「哪些会改」的真集 (要改 186 / 不动 32)★** |
| ★**`logs/iss317/iss317_sb_make.py` + `iss317_sb_run.sh` + `iss317_sb_singleinject.py`** ★ | ★**改名沙盒: 造一份改名后的网表/脚表, 跑判据读 C1/C2/C3 读数** ⇒ ★**★拷进 `logs/iss321/` 改 (★不许改 `logs/iss317/`·那是 hw-lead 的单★)★** ★ |
| ★**`logs/iss317/03b_sb_run_raw.txt`** ★ | ★**★场景矩阵 A0~A5 实跑读数 (含 NC 白名单三选项 + 反向用例)★** ★ |
| ★**`SW/tools/check_sw_ref_reachability.py`** ★ | ★**ISS-318 的改名漂移闸 (★rename-safe·你的对照基准★)★** |
| ★**`HANDOFF/2026-11-18_sw-lead_ISS318_SW位号引用闸与挂链体检.md`** ★ | ★**你上一单的交卷页 (★§B1-1 已扫过 SW/*.md 里的位号引用·本单是【脚本侧】, 不重复★)★** ★ |

---

## ★2 · 本单要交的 5 件事 (★逐条都有验收判据★) ★

### ★① 「哪些会改」的真集 ★
从 `rename_list_raw.txt` 解析出 ★**要改 186 / 不动 32** 两组 (★机器解析·不许手抄·输出放 `logs/iss321/rename_sets.txt`★) ⇒ ★**并把「哪些是板侧有、表侧无 (CHG_BOARD 件)」单列** (★ISS-317 已查清: 板侧 186 / 表侧 218·差 32★) ★

### ★② SW 侧写死的【真位号】全清单 ★
★**把 `SW/tools/*.py` + `SW/*.md` 里出现的每一个「真位号」逐个对上 §2① 的真集** ⇒ ★**输出 `logs/iss321/sw_hardcoded_refs.tsv` (★格式: `文件:行 | 位号 | 改名后名 | 命中类别★`)★**
★**命中类别只许三种**: ★**① 判据里写死 (改后会炸)** · ★**② 判据里写死但本来就该随改名改 (改法 = 改脚本)** · ★**③ 假阳性 (常量名/网络名/位号形状不同, 不用动)** ★
★**★不许用前缀猜 ★** ⇒ ★**每个位号都要能在表里找到或明确判成 ③** ★

### ★③ ★★沙盒实跑 (★不许推算★)★★ ★
★**拷 `logs/iss317/` 的改名沙盒脚本进 `logs/iss321/` (★只读复制★), 在沙盒里把网表/脚表改名 (★沿用 iss317 的 `kicad_ref` 口径, 不许自己另发明★) ⇒ ★**逐道跑 SW 侧判据, 记【改名前 rc / 改名后 rc / 首条红在哪一行】★★**
★**至少要跑这 8 道 (★就是链上的 + ISS-318 新挂的那几道★)**: `check_onepass_sw_sync.py` · `check_sw_ref_reachability.py` (★裸跑 + `--selftest`★) · `check_landing_trace_obligation.py` · `check_demo_panel_spec.py` (★裸跑 + `--selftest`★) · `check_demo_panel_spec_r6_selftest.py` · `check_demo_panel_spec_r6_chainjudge_selftest.py` · `check_demo_panel_spec_r6_hardprot_iss315_selftest.py` · `check_shutdown_semantics.py` · `check_timing_review_adc_sync.py` · `timing_check.py` ★
★**★注意坑 (★ISS-318 实测过·别再踩★)★**: ★**三道 selftest 闸【必须裸跑】(带 `--selftest` ⇒ rc=2 usage 错误) + `--tmpdir` 必须指项目内 `tmp/` (★本机 `/tmp` 带 usrquota 且配额已满 ⇒ 不指会 EDQUOT 假红★)** ★

### ★④ 逐条改法 + 执行顺序 (★★这是本单最值钱的一节★★) ★
★**每道会炸的闸给**: ★**炸在哪一行 (逐字) · 改法是【改脚本】还是【改数据】还是【本来就该 rename-safe】· 逐字改法 (能直接抄的那种) · 验收判据 (真命令 + 期望 rc)· 归属步 (S1~S13 里的一步)★**
★**★并给一条【执行顺序表】: 哪些 SW 侧改动【必须与板那一趟同批】(★改晚了 ⇒ 板已经出了·闸红在投产包上★), 哪些可以板出之后再补★** ★
★**★不许代拍: 涉及「能不能改受保护判据脚本」的, 只给【建议 + 代价 + 不改的后果】, 由 main 拍** ★

### ★⑤ 交卷物 4 件 ★
1. ★**`SW/ONETRIP_SW_RENAME_SAFETY.md` (新建 · §0~§6)** ★
2. ★**`HANDOFF/2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md` (新建 · ★B0~B6 齐全 · 占位符 0·★给 main 的 need 一行 (key + 一句话问法 + 不拍的后果)★)** ★
3. ★**`logs/iss321/` (原始输出 + 沙盒脚本副本 + 逐条读数)** ★
4. ★**`state/fragments/sw.yaml` (★经 `state/frag_write.py --agent sw-lead` 原子写·禁 `open(p,"w")`·★只写自己那一份★)** ★

---

## ★3 · ★★边界 (★硬★★) ★★

- ★**零写板**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 必须 = `611b869e13518c3c023fb178f91a0075` + mtime = `2026-11-06 07:07:17.362193413` ★
- ★**零落表**: 网表 / 脚表 / BOM / 原理图 一律不许改 ★
- ★**★零改闸: `SW/tools/*.py` 一个字节都不许改 (★本单只出改法, 改闸是 main / 下一单的活★)★** ★
- ★**零改既有文档正文**: `SW/*.md` 只许读, 不许改正文 (★本单只出「建议改法」★) ★
- ★**沙盒只写 `tmp/` + `logs/iss321/`** (★不许落 `/tmp`★) ★
- ★**零外发**: ★**不许发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★
- ★**证据分级** [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 (★本单几乎全是 [实测]·实跑读数; 推算的部分要标 [推算] 并写依据★) ★
- ★**不许替老板拍板** · ★**不许自签 issue_log** (★status/verify_result 留给 main★) ★
- ★**不许碰别人的域**: `HW/` · `MECH/` · `pm.yaml` · `issue_log.yaml` 一律不许动; ★**`logs/iss317/` 只读, 要用就拷进 `logs/iss321/`** ★

---

## ★4 · 交卷前必跑 (★原样贴进回复★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py     # rc 必须 0 · Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb                     # 必须 = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb               # 必须 = 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|待回填" HANDOFF/2026-11-18_sw-lead_ISS321_SW侧改名安全性体检.md   # 必须 = 0
grep -rc "iss321" state/fragments/sw.yaml                  # 必须 >= 1 (★分片写了没有★)
```

★额外纪律: ① 写分片必须用 state/frag_write.py (禁止 open(p,"w")) ② 只写本任务允许的文件, 不碰别人的 ③ 证据分级 [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标 ④ ★**不许外发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ⑤ 交卷前跑 python3 state/merge.py (rc 必须 0) && python3 state/gate_check.py (Q1 必须 18/18) 并把输出贴进回复 ⑥ ★**先落纸: 每完成一条就回填进交卷页, 宁可交半成品, 不许一页纸都不落** ⑦ ★**零外发 / 不替老板拍板 / 不自签 issue_log** ★
