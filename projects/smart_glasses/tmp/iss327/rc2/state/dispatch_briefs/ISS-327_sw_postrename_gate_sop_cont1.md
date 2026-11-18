# ISS-327 · sw-lead · ★★【cont1 续做 · 事故后重做】★★

> ★**这是续做, 不是从零重做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 14:5x (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: sw-lead (软件总工) · ★**verify_by**: main · ★**单号**: ISS-327 (★**status 保持 fixing**★) · ★**零外发**
> ★**性质**: ★**内部活 · 门禁/判据口径侧 · 纯沙盒验证类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★

---

## ★★★【★★★先读这一段: 上一趟出了真事故 ★★★】★★★

★**★兄弟 job `775d9893` (main) 已在 14:47 把事故恢复完毕, 并且【已经把这个 brief 的尾部追加了「续做前必读」一节】★★** ⇒ ★**★开工前请把整个 brief 读完 (★尾部那节是事故记录 + 5 条新规矩★)★★ ★

★**★你必须先知道的三件事 (★main 14:5x 本机实读·不抄任何 agent 报告★)★★**:

★**① 事故是什么**: ★**上一趟的造场脚本 `logs/iss327/iss327_sb_make.py` 第 ② 步把 `SW/*.md` 全部 `os.symlink()` 软链到真件, 随后第 ⑤ 步 `build_sw_docs()` 用 `open(root/SW/<name>.md, "w")` 直接写那个软链路径 ⇒ ★**写穿到真件** ⇒ ★**真件 42 份 SW 文档里 11 份被改成「改名后」位号 (781 处) ⇒ 板还是旧名 ⇒ ISS-318 位号可达性闸红 (58 真隐患 > 基线 3) ⇒ `gate_check` rc=1** ★

★**② 现在的起点状态 (★main 已逐项独立复核过, 不需要你重做恢复★)**:
| 项 | ★读数★ |
|---|---|
| ★真件 `SW/*.md` 的改名后位号残留★ | ★**0 处** (★main 用 `tmp/iss327/rename_map_iss327.json` 的 186 条 new 名逐个扫全部 `SW/*.md` 实测★) ★ |
| ★`SW/tools/check_sw_ref_reachability.py`★ | ★**rc=0 绿** (★分类统计段与事故前 14:23 基线**逐字相同** ⇒ OK 78 / DRIFT 0 / MISSING 3 / NET_NAME 9 / DOC_INTERNAL 22★) ★ |
| ★板 / 网表 / 脚表 / BOM 四 md5★ | ★`611b869e13518c3c023fb178f91a0075` / `6aee500e60ba0732f83a9cf557ba90ab` / `9174309df1ec9411ac8e8d9e80ee386a` / `5b9993992405904a60ac96a020b375d8` ⇒ ★**全程未变** ★ |
| ★事故现场留证★ | ★`logs/iss327/04_renamed_docs_backup/` (42 份改名后真件) · `logs/iss327/05_restore_main_report.txt` · `HANDOFF/2026-11-18_main_ISS327_软链沙盒写穿真件_事故与恢复.md` ★ |
| ★**上一趟留下的可复用产物★** | ★`logs/iss327/iss327_run_gates.sh` (★跑 10 道闸的脚本★) · `logs/iss327/01_baseline/` (★**16 份**事故前基线读数★) · `logs/iss327/01_baseline_run.log` (★10 道闸 rc 全 0 的总表·★直接可以当「改名前」那一列★) · `logs/iss327/iss327_apply_registry.py` · `tmp/iss327/rename_map_iss327.json` (★218 行 / 改名 186 / 不动 32 / 板侧 186·板侧改名 156★) ★ |

★**③ 上一趟的会话 14:30:05 被父 cron run 连带 abort ⇒ 僵尸 `fixing`** ⇒ ★**★这一趟你必须【先落盘, 再干活】★★** ★

---

## ★★① 上一趟已经做完的 (★不许重做★)

★**★基线已经跑完了 (★14:23★) ⇒ 「改名前」那一列【已经有了】★★** ⇒ ★**`logs/iss327/01_baseline_run.log` 里 10 道闸 rc 全 0, 每道闸的完整输出在 `logs/iss327/01_baseline/<闸名>.txt` ⇒ ★**直接引用, 不许重跑基线★** ★
★**★`tmp/iss327/rename_map_iss327.json` 已经生成 (★218 行 → 改名 186 / 不动 32★) ⇒ ★**「改名后」那一列的映射【已经有了】★★ ★
★**★`logs/iss327/iss327_run_gates.sh` 已经写好 ⇒ ★**跑「改名后」那一列直接用它 (★但你必须先读它、确认它不会写到真件★)★★ ★
★**★★⇒ ⇒ 你这一趟真正要做的只有三件 (★不是从头来★)★★**:
★**① 把「改名后」那一列跑出来 (★真拷贝沙盒★)** ★
★**② 跑「改名后 · 重建注册表后」那一列 (★`--freeze-registry` 后的读数★)** ★
★**③ 出三列对照表 + 当天 SOP + 那条「真隐患不许被洗白」的反向用例** ★

---

## ★★② ★★本单唯一的新规矩 (★违反就是第二次事故★)★★

★**★这 5 条已由兄弟 job 写进本 brief 尾部, 这里再抄一遍 (★因为它比任何技术细节都重要★)★★**:

1. ★**沙盒里凡是要【写】的文件 ⇒ 一律真拷贝 (`shutil.copyfile` / `copy_tree`); 软链只许给【只读】输入** ★
2. ★**写之前加断言 `assert not os.path.islink(path)`** ⇒ ★**软链当场炸, 不再静默写穿** ★
3. ★**真件 `SW/*.md` 一律不许改名** ⇒ ★**「改名后闸链全绿」的验证只能在【真拷贝沙盒】里做** ⇒ ★**★SW 文档改名必须与板那一趟【同批】落地 (★ISS-321/ISS-323 已定: 清单进 `logs/` + 不写死改名后名★)★★ ★
4. ★**沙盒跑完必查真件 mtime 漂移 ⇒ 零漂移才算零写板** ★
5. ★**闸脚本副本也要是真拷贝** (★上一趟 `SW/tools/` 这条做对了·照抄★) ★

★**★★★⇒ ⇒ 实操建议 (★省你一轮★)★★★**:
★**★先把 `logs/iss327/iss327_sb_make.py` 整个读一遍 (★它 17,757 B★) ⇒ ★**找到第 ② 步那个 `os.symlink()` (★main 已定位: ★**L126★**)★ ⇒ ★**把那一步改成 `copy_tree` (★脚本里 L148 已经有现成的 `copy_tree` 函数★, ★L286 已经在用它拷 `SW/tools/`★) ⇒ ★**★然后在每个写文件的入口加 `assert not os.path.islink(path)` ★ ★
★**★★改这个脚本是可以的 (★它在 `logs/iss327/` 里·是你自己上一趟的产物·不是判据脚本·不是真件★) ⇒ ★★★但 ★**改完必须先用一个【假的目标目录】试跑一遍, 确认不再产生软链★ (★`find <沙盒root> -type l` 必须是空★), 再跑真的★ ★**

---

## ★③ 要交的三件 (★每件都能独立验收★)

### ★③-1 · ★★三列读数表 (★本单的核心交付物★)★★

★**落点**: ★**`logs/iss327/02_postrename_gate_table.md`** ★ (★也可以是 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` 里的一节★)

| 闸 | ★**改名前 (基线)** ★ | ★**改名后 · 重建注册表前** ★ | ★**改名后 · 重建注册表后** ★ |
|---|---|---|---|
| ★每道闸一行 (10 行)★ | ★rc + 关键读数 ★★**★直接引用 `logs/iss327/01_baseline/` 的既有读数, 不许重跑★**★ | ★rc + 关键读数 ★ | ★rc + 关键读数 ★ |

★**★10 道闸 (★照 `logs/iss327/iss327_run_gates.sh` 的清单, 一个不许少★)**:
★`check_demo_panel_spec.py` · ★`check_demo_panel_spec_r6_chainjudge_selftest.py` · ★`check_demo_panel_spec_r6_hardprot_iss315_selftest.py` · ★`check_demo_panel_spec_r6_selftest.py` · ★`check_landing_trace_obligation.py` · ★`check_onepass_sw_sync.py` · ★`check_shutdown_semantics.py` · ★`check_sw_ref_reachability.py` · ★`check_timing_review_adc_sync.py` · ★`timing_check.py` ★

★**★★必须给出【三列的差值判读】★★** ⇒ ★**逐闸写: 「改名前绿 → 改名后红 → 重建后绿/红」⇒ ⇒ **一句话回答: 「重建注册表这条路, 能不能让 SW 侧 10 道闸在改名后全部回绿?」** ★**
★**★如果不能 ⇒ ★**必须逐闸指出哪几道红是【改名引起】、哪几道红是【本来就红】(★ISS-321 已实测证明「三道 R6 selftest 的红在 S4 vs S8 对照组里同样出现 ⇒ 不是改名特有」★) ⇒ 并且 ★**不许拿「改名引起」当借口把闸调软** ★ ★

★**★必须额外贴「真件 mtime 漂移清单」(★必须为空★)+ 板/网表/脚表/BOM 四 md5 + `check_sw_ref_reachability.py` 的 rc 与分类统计段★**

### ★③-2 · ★★「板那一趟」当天的 SW 侧 SOP (★可执行★)★★

★**落点**: ★**`SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md`** ★ (★**新建**; ★`SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` 是 ISS-323 的, 只读·不许改★)

★**必须包含**:
1. ★**执行顺序 (★机器可判: 每步给命令 + 期望读数 + 失败时的下一步★)** —— ★**顺序不许自己重排, 照 ISS-323 §5-1 的 7 件同批顺序, 你只补【每步的验收命令 + 期望 rc + 期望读数】** ★
2. ★**每道闸改名后的期望读数表** (★就是 §③-1 那张三列表的固化版★) ★
3. ★**★「重建注册表」这一步的时机与判据★** ⇒ ★**什么时候重建 · 重建前必须先确认哪些东西已经落定 · 重建后必须重跑哪几道闸 · ★**重建是一次性动作还是每次都要重做** ★ ★
4. ★**★回滚点 (★三档, 不许出现「看情况」★)★** ⇒ ① ★**立刻停** (★板 md5 已变 ⇒ 这次就是「板改了一次」⇒ 不许再改板, 只许修 SW 侧★) ② ★**修 SW 侧某一行** (★给逐字改法★) ③ ★**报 main 升级** (★给需要谁拍什么★) ★ ★
5. ★**★留证清单★★** ⇒ ★**当天跑完要落哪几个文件 (★命令 + 路径 + 期望落点★) ⇒ ★**这些留证必须能证明「板只改了一次」★** (★板 md5 前后各一次 + 网表/脚表/BOM 各一次★) ★

### ★③-3 · ★★判据设计稿 + 「真隐患不许被洗白」反向用例 (★只给设计, 不挂链★)★★

★**★必须回答**:
★① ★**现状 `--freeze-registry` 是【一次性重建】⇒ 【什么时候必须重建】? 谁负责? 重建前的登记义务是什么? (★照抄 ISS-312 那条「落表单号留痕义务」的口径★)** ★
★② ★**「改名漂移」(`DESIGNATOR_DRIFT`) 这个分类在改名之后【还有意义吗】? ⇒ 如果没有, 它是不是应该被显式退役而不是留着吓人? (★留着的代价 = 每次改名都要手动重建一次, 漏一次就长时间红★)** ★
★③ ★**★`DESIGNATOR_MISSING` 的上限机制在改名后怎么办★** ⇒ ★**现在上限 = 建闸日实测数 (★3 条★) ⇒ 改名后【基线会漂】⇒ 要么跟着重建、要么改成【台账链头】式 (★ISS-275/284 同款★) ⇒ ★**给方案 + 代价 + 建议默认值 + 不拍的后果** ★ ★

★**★★「真隐患不许被 `--freeze-registry` 洗白」这条反向用例 (★本单最要紧的一条·★不许跳过★)★★**:
★**在沙盒里把某个【真隐患】(★`TP_TEMP` / `TP_INT` / `CONN_USB` 之一·★建闸日基线那 3 条★) 故意改成一个【新的、从来不存在过的位号形状】⇒ ★**重建注册表之后, 它【必须仍然被抓住】⇒ 如果被洗白了 ⇒ 那就是一条必须报 main 的判据缺陷** ★

★**★反向用例 ≥ 5 条 (★每条贴「期望红/绿」与「实际红/绿」★)**

---

## ★④ 交卷物 (4 件)

1. ★**主交付物** ★`SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (★§0~§7 全填 · 占位符 0★) ★**+ 三列读数表** (★`logs/iss327/02_postrename_gate_table.md`★)
2. ★**交卷单** ★`HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md` (★B0~B6 齐全★)
3. ★**证据目录** ★`logs/iss327/` (★逐条原始输出 · 沙盒脚本 · 真件 mtime 漂移清单★)
4. ★**分片** ★`state/fragments/sw.yaml` (★走 `python3 state/frag_write.py --agent sw-lead` 原子写 · ★**禁 `open(p,"w")`**★ · artifacts / needs_from / interface_claims 各 ≥1 · status 换 ISS-327★)

---

## ★⑤ 边界 (★违反就是不合格★)

★**零写板** (★板 md5 必须还是 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**零改闸** (★`SW/tools/*.py` 一个字都不许改★) · ★**零改既有文档正文** (★`SW/**` 既有 md 只读★) · ★**沙盒只写 `tmp/iss327/` + `logs/iss327/`** ★ · ★**只写 `state/fragments/sw.yaml`** ★ · ★**零改 `state/gate_check.py`** ★ · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★
★**★★★⇒ ★★真件 `SW/*.md` 一个字都不许改 (★上一趟就是栽在这★) ⇒ ★★沙盒里凡要写的文件一律真拷贝 + 写前 `assert not os.path.islink(path)` + 跑完必查真件 mtime 漂移 = 0 ★★★ ★**

---

## ★⑥ 交卷前必跑 (★原样输出贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py
python3 SW/tools/check_sw_ref_reachability.py --dump-classification                     # 基线 (期望 rc=0 · MISSING=3)
python3 SW/tools/check_demo_panel_spec.py && python3 SW/tools/check_demo_panel_spec.py --selftest
python3 SW/tools/timing_check.py
python3 SW/tools/check_onepass_sw_sync.py --selftest
python3 SW/tools/check_landing_trace_obligation.py
python3 SW/tools/check_shutdown_semantics.py
python3 SW/tools/check_timing_review_adc_sync.py
python3 SW/tools/check_demo_panel_spec_r6_selftest.py
python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py
python3 SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★真件 mtime 漂移必须 = 0 (★这一条是本单的新验收项·上一趟就是栽在这★) ★★
find SW -newermt "<你的沙盒开工时刻>" -type f -name "*.md" | grep -v __pycache__      # 期望: 空
grep -cE "🔄|待填|PLACEHOLDER|施工中" SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md   # 期望 0
grep -c "iss327" state/fragments/sw.yaml                                       # 期望 >= 1
```

---

## ★⑦ 纪律 (★这项目的老教训·今天连踩两遍★)

★**① ★★交卷单第一件事就是 `write` 建骨架** (★哪怕只写 3 行标题 + 交付物清单★) ★ · ★**② 长任务一律 `nohup ... > logs/iss327/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**③ 单条 `exec` ≤ ~120 秒** ★ · ★**④ 每 10 分钟至少一次写盘** (★★★上一趟两趟都被 abort ⇒ ★**这趟务必先把【交卷页骨架 + 三列表的框架 + 沙盒脚本改对】做完, 再去跑那一列读数★ ⇒ ★**这样就算又被 abort, 本单也已经推进过半★) ★** · ★**⑤ 分片写完 `grep` 校验** · ★**⑥ ★★沙盒脚本改完先在假目录试跑一遍, 确认 `find <root> -type l` 为空★ ★ · ★**⑦ ★★`timing_check.py` / `check_onepass_sw_sync.py` 不支持 `--root` ⇒ 那两道要在沙盒副本目录里 `cd` 进去跑, 且必须贴证据证明它读的是副本不是真件★ ★**
