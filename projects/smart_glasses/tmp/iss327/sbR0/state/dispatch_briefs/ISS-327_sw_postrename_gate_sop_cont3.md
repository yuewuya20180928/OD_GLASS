# ISS-327 · sw-lead · ★★【cont3 续做 · 只写型收尾】★★

> ★**第三次续做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 15:55 (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: sw-lead (软件总工) · ★**verify_by**: main · ★**单号**: ISS-327 (★**status 保持 fixing**★) · ★**零外发**
> ★**性质**: ★**内部活 · 门禁/判据口径侧 · 纯沙盒验证类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★

---

## ★★★【★★上一趟 (cont2) 死在哪儿 · main 15:5x 本机实读, 不抄 agent 报告 ★★★】★★★

★**★cont2 的会话在 15:51:05 被 abort 打断 (★最后一条 assistant 消息 `stopReason=aborted` · `errorMessage="This operation was aborted"`·最后一句话是 "Now I have everything. Let me write the main deliverable — the SOP:"★) ⇒ ★**它的 write 工具调用发出去了但文件没落地** ★**

| 项 | ★main 实读读数 (15:5x)★ | ★状态★ |
|---|---|---|
| ★`SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` ★ | ★**不存在** ★ | ★⬜ 待写 (★上一趟就死在这一次超长 write 上★) ★ |
| ★`logs/iss327/02_postrename_gate_table.md` ★ | ★**不存在** ★ | ★⬜ 待写 ★ |
| ★`HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md` ★ | ★**1,646 B · mtime 15:24** ★ | ★★**只有 B0~B9 的标题骨架, 正文全空**★ ★ |
| ★`state/fragments/sw.yaml` 里 `iss327` 命中 ★ | ★**0** ★ | ★⬜ 待写 (★分片一条没落★) ★ |
| ★`find tmp/iss327 -type l \| wc -l` ★ | ★**0** ★ | ★✅ 事故根因修掉的代码级证据 (★main 本机实测·可直接引用★) ★ |

★**★⇒ ⇒ 这一趟是【纯写型】: 读数已经全部在盘上了, 你【不许重跑】任何闸, 只做【归并 + 落字 + 分片 + 自证】★ ★**

---

## ★★① 已落盘的事实源 (★直接读, 不许重跑·不许重造数据★) ★★

| 事实源 | 大小/时刻 | ★里面有什么★ |
|---|---|---|
| `logs/iss327/24_four_arm_measure.txt` | ★11,946 B · 15:46★ | ★① 四 md5 逐臂表 ② 「改名后位号命中数」逐臂表 ③ **10 道闸 × 6 臂 rc 主表** ④ `check_sw_ref_reachability` 的 DRIFT/MISSING/上限 ⑤ **rc=2 逐闸语义归类** ★ |
| `logs/iss327/25_control_validity.txt` | ★12,400 B · 15:48★ | ★逐臂「唯一变量」定义 (sbCtl/sbR0/sbR3/sbR4) + 逐臂两两 diff + 软链数断言 ★ |
| `logs/iss327/23_rev_selftest_run.log` | ★15:43★ | ★**反向用例实测** (注入新真隐患 `TP_TEMP_ISSX` → 重建注册表前后 rc 都 = 1, 输出里都出现 TP_TEMP_ISSX) ★ |
| `logs/iss327/20_rev_R1_before_rebuild.txt` / `21_rev_R1_freeze_stdout.txt` / `22_rev_R1_after_rebuild.txt` | ★15:43★ | ★重建前/冻结表/重建后 ★ |
| `logs/iss327/iss327_four_arm_measure.py` / `iss327_control_validity.py` / `iss327_rev_selftest.py` | ★15:43~15:48★ | ★你自己写的三个机器化脚本 (★只读, 不许改★) ★ |
| `logs/iss327/19b_ctl_rerun.log` | ★15:02★ | ★修 bug 后的 sbCtl 重跑版 (★★交卷页里 sbCtl 那一列必须注明取自这一版, 不许用 `19_run_all_cont1.log` 里那条坏对照臂的读数★★) ★ |

★**★绿/红合计读数 (★直接抄进交卷页 §B8, 不许自己重算·不许改数★)★**:
```
BASELINE   绿 10 / 红(rc=1) 0 / rc=2 0
sbCtl      绿  8 / 红(rc=1) 0 / rc=2 2
sbR0       绿  1 / 红(rc=1) 5 / rc=2 4
sbR1       绿  1 / 红(rc=1) 5 / rc=2 4   (sbR0 + 重建注册表)
sbR3       绿  3 / 红(rc=1) 3 / rc=2 4
sbR2       绿  3 / 红(rc=1) 3 / rc=2 4   (sbR3 + 重建注册表)
```

---

## ★★★【★★② 这一趟只做四件 (★顺序不许换★) ★★★】★★★

★**★为什么顺序重要 (★本项目反复踩的坑★): 成果写在交付页, 而门禁链读的是【交卷页】⇒ ⇒ 交卷页优先★ ★**

### ★★① 先把交卷页 B0~B9 九块的正文填满 (★最优先·先落骨架再补正文★) ★★

★**★交卷页路径**: `HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md` (★现在 1,646 B·只有标题★) ★
★**★九块各写什么 (★不许空着·不许写「见附件」·不许写「同上」★)★**:

| 块 | ★必须写进去的东西 (★全部来自上面的事实源★) ★ |
|---|---|
| **B0 背景与病灶** | ★ISS-318 (SW 侧位号引用可达性闸) / ISS-321 (S1 改名对 SW 判据安全性体检) / ISS-323 (S1 七件同批清单) / ISS-317 (HW 侧五侧改名清单) 是谁; ★★本单的病灶 = 「改名之后 SW 侧 10 道闸还能不能复活」★ ★ |
| **B1 结论摘要** | ★**一句话回答**: 「重建注册表这条路, 能不能让 SW 侧 10 道闸在改名后全部回绿?」⇒ 按读数如实答 (★逐闸给结论, 不许只写一句总的★) ★ |
| **B2 验收标准自评** | ★逐条 通过 / 不通过 / 未验 ★ |
| **B3 证据分级** | ★全本机实读 ⇒ 标 `[实测]`; 查不到的标 `[0数据]`; 推算标 `[推算]` ★ |
| **B4 接口取值声明** | ★按 ISS-323 §5-1 的七件顺序口径写 (★别自己编一套顺序★) ★ |
| **B5 未决项与卡点** | ★需要谁回答什么 ★ |
| **B6 自证复现命令** | ★逐条可复制的命令 ★ |
| **★B7 对照有效性自检** ★ | ★见下面 §③ (★含一条必须如实写的真发现★) ★ |
| **★B8 四臂对照表** ★ | ★见下面 §④ ★ |
| **★B9 rc=2 语义定案** ★ | ★见下面 §⑤ ★ |

### ★★② 写主交付物 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (★现在不存在★) ★★

★**★SOP 必须能让人照着做**: 造场 → 跑闸 → 读 rc → 判 rc=0/1/2 三种语义 → 重建注册表 → 验反向用例 → 交卷 ⇒ ★**逐闸给命令 + 逐档给判读 + 给「失败时的下一步」三档表 (★上一趟你已经把这份三档表想清楚了, 但没落盘★)★** ★
★**★SOP 里必须写明哪些闸支持 `--root`、哪些不支持 (★实测读数: `check_onepass_sw_sync` / `check_timing_review_adc_sync` / `timing_check` **不支持** `--root` ⇒ 只能 `cd` 进沙盒根跑★)★ ★

### ★★③ 写 `logs/iss327/02_postrename_gate_table.md` (★交卷页交付物清单第 2 项·现在不存在★) ★★

★**★= 四臂对照表的独立成文版 (★交卷页 §B8 引用它★)★** ★

### ★★④ 分片 + 闸链自证 ★★

★**分片**: `python3 state/frag_write.py --agent sw-lead --add-artifact path=... summary="..."` / `--add-need key=... to=... item="..."` ⇒ ★**只写 `state/fragments/sw.yaml` (★禁止 open(p,"w")·禁止写别人的分片★)★** ★
★**闸链**: `python3 state/merge.py` (★rc 必须 0★) && `python3 state/gate_check.py` (★Q1 必须 18/18★) ⇒ ★**把两段输出原样贴进回复★** ★

---

## ★★★【★★③ ★★B7 必须如实写的一条真发现 (★不许改数据迁就判据★) ★★★】★★★

★**★`24_four_arm_measure.txt` §②「改名后位号命中数」那一栏里, ★sbCtl 也是 `797 处 / 12 份`★, 与 ★BASELINE 完全相同★ ⇒ ⇒ ★**「对照臂的改名后位号命中必须 = 0」这条判据, 它的实测口径是错的** ★**

★**★机制**: 它扫的是**整棵树的全量命中** (★BASELINE 自己就有 797 处 / 12 份·HW 五侧 2648 处 / 4 份★) ⇒ **不是「改名引入的增量」** ⇒ ⇒ ★**全量口径下 BASELINE 与各臂同值 ⇒ 这条判据对「改名增量」根本不敏感 ⇒ 不能用它证明对照臂干净** ★

★**★⇒ 你必须做的二选一 (★两个都合法, 但必须写明选了哪个 + 为什么★)★**:
- **(A)** 把判据改成增量口径: ★`臂内命中 − BASELINE 命中 = 0` 才是对照臂干净的判据 ⇒ ★并把 §② 那张表按增量重算一遍 (★重算用已有的 24 号文件里的数就行, 不许重跑闸★)★ ★
- **(B)** 保留全量口径, 但在 §B7 明写: 「全量口径下 BASELINE 与 sbCtl 同值 (797/12) ⇒ 该判据对改名增量不敏感 ⇒ 它【不能】作为对照臂干净的证据; 对照臂干净的真证据是 ① 四 md5 与真件逐字相同 ② 软链数 = 0」★ ★

★**★⇒ ★不许把 797 写成 0★ · 不许删掉这一栏★ · 不许「重跑到好看为止」★ ★**

---

## ★★★【★★④ ★★B8 四臂对照表必须包含的行 (★逐闸一行, 不许只写绿红合计★) ★★★】★★★

★**① 10 道闸 × 6 臂 (BASELINE / sbCtl / sbR0 / sbR1 / sbR3 / sbR2) 的 rc 一行一道闸** ★
★**② 绿/红/rc=2 合计** (★抄上面 §① 的读数★) ★
★**③ `check_sw_ref_reachability` 的 DRIFT / MISSING / 上限 逐臂一行** (★BASELINE 0/3/3 · sbCtl 0/3/3 · sbR0 **58/5/3** · sbR1 **0/56/3** · sbR3 0/3/3 · sbR2 0/3/3★) ⇒ ★**注意 sbR0→sbR1 那一跳: DRIFT 58→0 但 MISSING 5→56 ⇒ 重建注册表把 58 条漂移换成了 56 条缺失 ⇒ 这是【机制上更糟的一跳】, 不许只报「绿了」★** ★
★**④ 逐闸 rc=2 语义归类** (★抄 24 号文件 §⑤·不许自己重判★) ★
★**⑤ 逐臂四 md5 + 「sbCtl == 真件 / sbR0·sbR3 ≠ 真件」的对照有效性判定** ★
★**⑥ 逐臂唯一变量** (★抄 25 号文件: sbCtl = 整树真拷贝零改名 · sbR0 = +HW 五侧改名 · sbR3 = +SW 文档同步改名 · sbR4 = +注入新真隐患 TP_TEMP_ISSX★) ★

★**★⇒ ⇒ B8 的净结论 (★按读数自己组织, 但必须能落到这句话上★)★**: ★**重建注册表能不能让改名后回绿? ⇒ 分闸看: `check_shutdown_semantics` / `check_sw_ref_reachability` 在 sbR3→sbR2 这一跳回绿 (rc 1→0); 但 `check_demo_panel_spec` / `check_onepass_sw_sync` / `timing_check` 在 sbR3/sbR2 仍红 (rc=1) ⇒ ⇒ 重建注册表【不能】让 10 道闸全部回绿 ⇒ ⇒ 剩下的红必须逐闸归因: 哪些是改名引起的, 哪些是沙盒臂天然红 (★板 md5 ≠ 真件 ⇒ R6 硬保护/台账链必然红·而 R6 三道 selftest 在 sbCtl 里也是 rc=2⇒ 属「夹具缺失」不属「改名引起」★)★** ★

---

## ★★★【★★⑤ ★★B9 rc=2 语义定案 (★读数已在盘上, 直接定案★) ★★★】★★★

★**★`24_four_arm_measure.txt` §⑤ 已把每个 rc=2 的最后一条 ❌ 都归类了, 结论 = 「rc=2 = 【脚本报错 / 前置不成立】, 不是闸红」**: ★
- ★`r6_chainjudge_selftest` / `r6_hardprot_iss315_selftest` 的 rc=2 = ★「找不到修前的判据备份 `.bak_iss312` / `.bak_iss315`」⇒ ★**夹具没被真拷贝进沙盒 ⇒ 「不是巧合」自证做不了** ⇒ ★不是判据失败★ ★
- ★`r6_selftest` 在 sbR0/sbR3/sbR2 的 rc=2 = ★「基线就不绿」⇒ ★**R6 硬保护 (板 md5 变了) + 台账链 (真源 md5 与台账记录不符) 在沙盒臂里必然红** ⇒ ★**这是沙盒环境的必然, 不是改名引起的** ⇒ ⇒ ★**⇒ ⇒ 沙盒臂不能用来判定 R6 三道 selftest 的改名安全性; 那三条的改名安全性另有 ISS-321 的 S4 vs S8 对照组实证 (三道红在对照组里同样出现 ⇒ 不是改名特有)⇒ 引用它, 不许在沙盒臂上重判★** ★
- ★`check_timing_review_adc_sync` 的 rc=2 = ★最后一条 ❌ 为空 (★要你自己从它的输出文件里查清是哪一步报错·★这是 §B9 里唯一一条 main 没替你查清的★)★ ★

★**★⇒ ⇒ B9 的定案写法: 「rc=2 = 前置不成立/夹具缺失 ⇒ 【既不算红, 也不等于绿】⇒ 判定时必须逐条看最后一条 ❌ 的原因; 不许把 rc=2 折进红里, 也不许把 rc=2 当绿灯放过」★ ★**

---

## ★★⑥ 边界 (★逐条自证·交卷前贴输出★) ★★

| 边界 | 自证方式 |
|---|---|
| ★**零写板** ★ | `md5sum HW/PCB/demo_mainboard.kicad_pcb` 必须仍是 `611b869e13518c3c023fb178f91a0075` · mtime 必须仍是 `2026-11-06 07:07:17.362193413` |
| ★**零落表** ★ | `HW/netlist_v1.csv` `6aee500e60ba0732…` / `HW/netlist_v1_pins.csv` `9174309df1ec9411…` / `HW/BOM_v1.csv` `5b9993992405904a…` 逐字节不变 |
| ★**零改闸** ★ | `SW/tools/*.py` 全表 md5 与开工前相同 |
| ★**真件 `SW/*.md` 一律不许改名** ★ | ★写任何文件前 `assert not os.path.islink(path)`; 沙盒里要写的文件一律真拷贝; 跑完 `find tmp/iss327 -type l \| wc -l` 必须 = 0★ |
| ★**零改既有文档正文** ★ | ★本趟只许写: 交卷页 / `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` / `logs/iss327/02_postrename_gate_table.md` / `logs/iss327/` 下新证据 / `state/fragments/sw.yaml`★ |
| ★**只写本任务允许的文件** ★ | ★不许写别人的分片 (hw.yaml / mech.yaml / pm.yaml 一个字节都不许动)★ |
| ★**零外发** ★ | ★本单不发任何邮件/询价/问询/采购; 全本机实读; 没有「批一句可以发」这个选项★ |
| ★**不自签 issue_log** ★ | ★`state/issue_log.yaml` md5 不许动 (★landing 是 main 的活★)★ |
| ★**不许改 `iss327_sb_make.py`** ★ | ★上一趟已修好 (★L126 软链→真拷贝 + L67 `assert_no_symlink_in()`★) ⇒ ★**只许验证, 不许再改**★ ★ |

★**★★★一条【操作层面的硬纪律】 (★上一趟就是死在一次超长 write 上★★★**:
★**写交卷页 / 写 SOP ⇒ 一次 write 的内容别超过 ~6000 字 ⇒ 先 write 骨架 (每块标题 + 一句话占位), 再用 edit 逐块补正文 ⇒ ★**这样即使中途被掐, 盘上也有可读的骨架, 下一趟能接着补**★ ★

---

## ★★★【★★⑦ 交卷前必跑 (★输出原样贴进回复★) ★★★】★★★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/frag_write.py --agent sw-lead --add-artifact path=SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md summary="..."
python3 state/frag_write.py --agent sw-lead --add-artifact path=logs/iss327/02_postrename_gate_table.md summary="..."
python3 state/frag_write.py --agent sw-lead --add-artifact path=HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md summary="..."
python3 state/merge.py   # rc 必须 0
python3 state/gate_check.py   # Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb   # 必须 611b869e13518c3c023fb178f91a0075
grep -c "iss327" state/fragments/sw.yaml   # 必须 >= 1
```
★**★另外交卷页必须自检两条: ① 占位符 `__XXX__` 命中 = 0 ② U+FFFD 乱码计数 = 0★ ★**

---

## ★★⑧ 需要 main / 老板拍板的东西 (★只交 need, 不代拍★) ★★

★**★至少这三条 (★写进分片 `--add-need`·key 用 `iss327_` 前缀★)★**:
1. ★`iss327_rc2_fixture_bak_missing` ★: ★沙盒臂里 `.bak_iss312` / `.bak_iss315` 没被真拷贝 ⇒ 三道 R6 selftest 的 rc=2 ⇒ ★**要不要把这两个「受保护资产」纳入沙盒真拷贝清单 (★纳入之后这三道闸在沙盒里就能真跑, R6 硬保护/台账链也会照样红·但那才是【可判】的红★)? 要不要动由 main 拍** ★
2. ★`iss327_r6_selftest_not_judgeable_in_sandbox` ★: ★沙盒臂不能判定 R6 三道 selftest 的改名安全性 (★R6 硬保护/台账链在臂里必然红★) ⇒ ★**这条判据缺口怎么补 (★靠 ISS-321 的 S4 vs S8 对照组? 还是另起一趟在【真件同链】上做?★) ⇒ 交 main** ★
3. ★`iss327_hit_count_metric_is_not_incremental` ★: ★「改名后位号命中数」判据口径是全量不是增量 ⇒ 对照臂干净的判据口径要不要改 (★增量口径 = 臂内 − BASELINE★) ⇒ ★交 main 拍口径 (★这是判据级改动, sw-lead 不自签★)★ ★
