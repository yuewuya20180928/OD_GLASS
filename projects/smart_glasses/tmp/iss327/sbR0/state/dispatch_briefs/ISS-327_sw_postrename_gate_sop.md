# ISS-327 · sw-lead · ★★【S1 位号改名「SW 侧」改名后【闸链复活】验证】★★

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 14:1x (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: sw-lead (软件总工) · ★**verify_by**: main · ★**单号**: ISS-327 · ★**零外发**
> ★**性质**: ★**内部活 · 门禁/判据口径侧 · 纯沙盒验证类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★

---

## ★① 病灶 (★main 2026-11-18 14:0x 本机实读 · 不抄任何 agent 报告★)

★**背景**: ★**「板只改一次」那一趟的 S1 步 = 位号改名** ★ ⇒ ★**改名会一次性动 218 个表侧器件里的 186 个 (加 `_1` 后缀)** ★
★**★而 SW 侧 10 道闸里, 至少有一道 (★`SW/tools/check_sw_ref_reachability.py`★) 是【按【旧位号名】建的冻结注册表判定】★★** ⇒ ★**改名之后, 这道闸的每一个判据都会重新算一遍 ⇒ 变红是【必然】的** ★
★**★问题不是「会不会红」, 而是【红了以后怎么办】—— 而这件事目前【没有任何一份文档说清】★**

★**main 本机实读的三个事实 (★都是本轮现读的★)**:

★**事实 ① — 改名表**: ★**`HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` §1 = 218 行 ⇒ 改名 186 / 不动 32** ★ (★main 用 python 逐行解析数出来的★)

★**事实 ② — SW 那道闸的判定机制** ★ (`SW/tools/check_sw_ref_reachability.py`):
★**它有三条判据分类**: ★`DESIGNATOR_OK` (C1 · 现在板/网表里找得到) · ★`DESIGNATOR_DRIFT` (C2 · ★**建闸时是真位号, 现在找不到了 = 改名漂移★**) · ★`DESIGNATOR_MISSING` (C14 · ★**形状像位号, 但板/网表里从来没有过 = 真隐患★**) ★
★**★它有一个【建闸日冻结注册表】`DESIGNATOR_REGISTRY` (★C2 的判决源★) ⇒ ★**改名之后, 每一个被改名的 ref 都会【在文档里】变成 `DESIGNATOR_DRIFT` ⇒ ★**红灯数 = 改名涉及的 SW 文档引用数**** ★
★**★它自己写着: 建闸日 `DESIGNATOR_MISSING` 基线 = 3 条, 允许上限 = 建闸日实测数 (★**超了才红**★) ⇒ ★**⇒ 改名后 `MISSING` 也会涨 (旧名变成 MISSING + 新名变成 OK, 或反过来), 上限不会跟着涨 ⇒ ★** ⇒ 必须实测** ★

★**事实 ③ — 这道闸的重建命令是现成的**: ★**`python3 SW/tools/check_sw_ref_reachability.py --freeze-registry`** (★源码 L834 有这个 flag★) ⇒ ★**⇒ 「改名后把注册表按新盘面重建」这条路【已经铺好了】, 但【没有人验证过它重建后这道闸到底读什么】** ★

★**★main 本轮实跑确认的现状**: ★**`python3 SW/tools/check_sw_ref_reachability.py --dump-classification` ⇒ rc=0 绿 · `DESIGNATOR_MISSING` = 3 条 (★`TP_TEMP` / `TP_INT` / `CONN_USB`★) ⇒ ★**今天改名还没发生, 所以看不出来** ★**

---

## ★② 要交的三件 (★每件都能独立验收★)

### ★②-1 · ★★沙盒里把「改名 → 闸链」整条链真跑一遍 (★★不许只在文档里推演★★)

★**★这一单的核心交付物 = 一份【改名后 SW 侧闸链的真实读数表】★★**

★**怎么做 (★沙盒纪律见 §4★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ★沙盒 1: 把整棵树 (HW/ + SW/ + MECH/ + state/) 复制到 tmp/iss327/ 下
# ★沙盒 2: 在沙盒副本里做「改名」—— ★★★照 §1 表逐条改 (218 行 → 186 改名 + 32 不动)★★
#          ★★★改哪些面照 ISS-317 的五侧口径 (板 + 网表 + 脚表 + BOM + 原理图)★★
# ★沙盒 3: 在沙盒副本里跑【全部 10 道 SW 闸】, 逐道贴 rc + 关键输出行
# ★沙盒 4: 在沙盒副本里跑 `--freeze-registry` 重建注册表 ⇒ 再跑一遍 ⇒ 贴第二轮读数
```
★**★SW 侧那 10 道闸 (★照 `logs/iss323/iss323_sb_run_all.sh` 的清单, ★一个不许少★)**:
★`check_demo_panel_spec.py` · ★`check_demo_panel_spec_r6_chainjudge_selftest.py` · ★`check_demo_panel_spec_r6_hardprot_iss315_selftest.py` · ★`check_demo_panel_spec_r6_selftest.py` · ★`check_landing_trace_obligation.py` · ★`check_onepass_sw_sync.py` · ★`check_shutdown_semantics.py` · ★`check_sw_ref_reachability.py` · ★`check_timing_review_adc_sync.py` · ★`timing_check.py` ★

★**★必须给出【三列对照表】★★**:

| 闸 | ★**改名前 (基线)** ★ | ★**改名后 · 重建注册表前** ★ | ★**改名后 · 重建注册表后** ★ |
|---|---|---|---|
| ★每道闸一行★ | ★rc + 关键读数 (★**自己 fresh 测, 不许抄历史表**★) | ★rc + 关键读数 ★ | ★rc + 关键读数 ★ |

★**★★这张表要回答的问题只有一个: ★★「重建注册表这条路, 能不能让 SW 侧 10 道闸在改名后全部回绿?」★★** ⇒ ★**如果能 ⇒ 那 §2-2 的设计稿就是「板那一趟」当天可以直接执行的 SOP; 如果不能 ⇒ ★**你必须指出哪几道红是【改名引起】、哪几道红是【本来就红】(★ISS-321 已经证明「三道 R6 selftest 的红在 S4 vs S8 对照组里同样出现 ⇒ 不是改名特有」★), 并且不许拿「改名引起」当借口把闸调软** ★

★**★★额外必答的一问 (★这是本单最容易被跳过、但最值钱的一问★)★★**:
★**「`--freeze-registry` 重建注册表 = 把判据的判决源换成【改名的结果】⇒ 它会不会把『真隐患』也一起洗白?」** ★
★**⇒ 你必须设计并实跑一条反向用例**: ★**在沙盒里把某个【真隐患】(★`TP_TEMP` / `TP_INT` / `CONN_USB` 之一★) 故意改成一个【新的、从来不存在过的位号形状】⇒ ★**重建注册表之后, 它【必须仍然被抓住】⇒ 如果被洗白了 ⇒ 那就是一条必须报 main 的判据缺陷** ★ (★**这条不许跳过** ★)

### ★②-2 · ★★「板那一趟」当天的 SW 侧 SOP (★可执行, 不许写成一堆注意事项★)

★**★这一单是给【板那一趟当天】用的 ⇒ 必须写成【照着做就能做】的步骤, 不是「注意事项」★★**

★**落点**: ★**`SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md`** ★ (★**新建**; ★`SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` 是 ISS-323 的, 只读·不许改★)

★**必须包含**:
1. ★**执行顺序 (★机器可判, 每步给命令 + 期望读数 + 失败时的下一步★)** ★—— ★**顺序不许你自己重排, 照 ISS-323 §5-1 的 7 件同批顺序来, 你只补【每步的验收命令 + 期望 rc + 期望读数】** ★
2. ★**每道闸改名后的期望读数表** (★就是 §2-1 那张三列表的固化版★)
3. ★**★「重建注册表」这一步的时机与判据★** ⇒ ★**什么时候重建 (★重建前必须先确认哪些东西已经落定★) · 重建后必须重跑哪几道闸 · ★**重建是一次性动作还是每次都要重做** ★**
4. ★**★回滚点★★** ⇒ ★**如果 §2-1 那张表里某道闸【重建注册表之后还是红的】⇒ 当天怎么办? ★**给三档: ① 立刻停 (板 md5 已变 ⇒ 这次就是「板改了一次」⇒ 不许再改板, 只许修 SW 侧) ② 修 SW 侧某一行 (给逐字改法) ③ 报 main 升级 (给需要谁拍什么) ★** ⇒ ★**★不许出现「看情况」这种话★**
5. ★**★留证清单★★** ⇒ ★**当天跑完要落哪几个文件 (★命令 + 路径 + 期望落点★) ⇒ ★**这些留证必须能证明「板只改了一次」★** (★板 md5 前后各一次 + 网表/脚表/BOM 各一次★)

### ★②-3 · ★★判据设计稿 (★只给设计 + 反向用例, ★★不许挂进 `state/gate_check.py`★★)

★**★「SW 侧位号引用闸在改名后怎么长期不自毁」—— 设计稿★★**
★**必须回答**:
★① ★**现状 `--freeze-registry` 是【一次性重建】⇒ 【什么时候必须重建】? 谁负责? 重建前的登记义务是什么? (★照抄 ISS-312 那条「落表单号留痕义务」的口径★)** ★
★② ★**「改名漂移」(`DESIGNATOR_DRIFT`) 这个分类在改名之后【还有意义吗】? ⇒ 如果没有, 它是不是应该被显式退役而不是留着吓人? (★留着的代价 = 每次改名都要手动重建一次, 漏一次就长时间红★)** ★
★③ ★**★`DESIGNATOR_MISSING` 的上限机制在改名后怎么办★** ⇒ ★**现在上限 = 建闸日实测数 (★3 条★) ⇒ 改名后【基线会漂】⇒ 要么跟着重建、要么改成【台账链头】式 (★ISS-275/284 同款★) ⇒ ★**给出方案 + 代价 + 建议默认值 + 不拍的后果** ★**
★④ ★**反向用例 ≥ 5 条 (★每条贴「期望红/绿」与「实际红/绿」★)** ⇒ ★**必须包含上面 §2-1 那条「真隐患不许被洗白」★**

---

## ★③ 交卷物 (4 件)

1. ★**主交付物** ★`SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (★§0~§7 全填 · 占位符 0★) ★**+ 改名后闸链读数表** (★可以是独立文件 `logs/iss327/02_postrename_gate_table.md`★)
2. ★**交卷单** ★`HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md` (★B0~B6 齐全★)
3. ★**证据目录** ★`logs/iss327/` (★逐条原始输出 · 沙盒脚本 · 改名前后 md5 快照★)
4. ★**分片** ★`state/fragments/sw.yaml` (★走 `python3 state/frag_write.py --agent sw-lead` 原子写 · ★**禁 `open(p,"w")`**★ · artifacts / needs_from / interface_claims 各 ≥1 · status 换 ISS-327★)

---

## ★④ 边界 (★违反就是不合格★)

★**零写板** (★`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** (★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` 一个字节不许动★) · ★**零改闸** (★`SW/tools/*.py` 一个字都不许改 —— 本单只跑闸 + 出设计稿★) · ★**零改既有文档正文** (★`SW/**` 既有 md 只读★) · ★**沙盒只写 `tmp/iss327/` + `logs/iss327/`** ★ · ★**只写 `state/fragments/sw.yaml`** (★`hw.yaml` / `mech.yaml` / `pm.yaml` 一个字节都不许碰★) · ★**零改 `state/gate_check.py`** (★挂闸归 main★) · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料 · 需要外部资料一律自己网上查 + 标证据等级 + 查不到写降级方案 ⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** (★§2-3 只给设计稿 + 建议默认值 + 不拍的后果★) · ★**不自签 `state/issue_log.yaml`** (★签字是 main 的活★) · ★**不许把整份大文件读进来** (★只 grep 你要查的行★)

---

## ★⑤ 交卷前必跑 (★原样输出贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py   # rc 必须 0
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
grep -cE "🔄|待填|PLACEHOLDER|施工中" SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md   # 期望 0
grep -c "iss327" state/fragments/sw.yaml                                       # 期望 >= 1
```

---

## ★⑥ 纪律 (★这项目的老教训·今天又踩过一遍★)

★**① 交卷单第一件事就是 `write` 建骨架** (★哪怕只写 3 行标题 + 交付物清单★) · ★**② 长任务一律 `nohup ... > logs/iss327/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**③ 单条 `exec` ≤ ~120 秒** (★★本机现在有两条 ISS-325 的沙盒臂在跑, 各自吃满一个核 ⇒ ★**你跑重活时会更慢 ⇒ 更要短轮询·不许前台长跑★**) · ★**④ 每 10 分钟至少一次写盘** · ★**⑤ 每落一件交付物就把 rc 追加进交卷单** · ★**⑥ 分片写完 `grep` 校验** · ★**⑦ ★★沙盒里做「改名后」的行为, 必须是把【整棵树】复制过去再改 —— 不许在真文件上改·改完再改回来 (★那叫擦产物, 不叫验证★)★★** · ★**⑧ ★★沙盒副本里跑闸时, 闸脚本会去找【项目根下的真文件】⇒ ★**必须确认闸的 `--root` / 路径口径指向沙盒副本 (★`check_sw_ref_reachability.py` / `check_demo_panel_spec.py` / `check_landing_trace_obligation.py` 都支持 `--root`; ★**`timing_check.py` / `check_onepass_sw_sync.py` 不支持 ⇒ 那两道要在沙盒副本目录里 `cd` 进去跑, 且必须贴证据证明它读的是副本不是真件★)★★**

---

## ★★★【续做前必读 · ★★事故与恢复 (★main · 2026-11-18 14:47 本机实读★)】★★★

★**上一趟 (14:21~14:30) 出了真事故: ★★沙盒用软链写穿了真件 ⇒ 真件 `SW/*.md` 被改成「改名后」位号 ⇒ ISS-318 闸红 ⇒ `gate_check` rc=1★★** ★

### ★① 出了什么事 (★根因代码级★)
- 上一趟的造场脚本 `logs/iss327/iss327_sb_make.py`:
  - 第 ② 步 `build_root()`: ★**`SW/*.md` 全部 `os.symlink()` 软链到真件** (★只有 `SW/tools/` 用 `copy_tree` 真拷贝★)
  - 第 ⑤ 步 `build_sw_docs()`: ★**`open(root/SW/<name>.md, "w")` 直接写那个软链路径** ⇒ ★**写穿到真件** ★
  - ★**对照: 板/网表/脚表/BOM 走 `replace()` (先删软链再写真文件) ⇒ 那四件真源没事 (md5 实测未变)** ★
- ★**后果**: 真件 42 份 `SW/*.md` 里 **11 份被改** (★781 处位号引用★) ⇒ ★**板还是旧名 · 文档先变新名 ⇒ ISS-318「SW 侧位号引用可达性闸」红 (58 真隐患 > 基线 3) ⇒ `gate_check` rc=1** ★
- ★**上一趟会话 14:30:05 `Aborted` (父 run 结束连带 abort) ⇒ 僵尸 `fixing`** ★

### ★② main 已做的恢复 (★续做的人不用重做, 但要知道起点★)
- ★**已按精确逆运算回退**: `state/_restore_sw_docs_20261118_1445.py` (映射 = `tmp/iss327/rename_map_iss327.json` 的 186 条 · 逆映射 new→old · 替换算法与事故脚本逐字同款) ⇒ ★**781 处全部改回旧名 · 残留 0** ★
- ★**验证**: `check_sw_ref_reachability.py` **rc=0** 且 ★**分类统计段与事故前 14:23 基线逐字相同** (OK 78 / DRIFT 0 / MISSING 3 / NET_NAME 9 / DOC_INTERNAL 22) ★ · ★**板/网表/脚表/BOM 四个 md5 全程未变** ★
- ★**事故现场留证**: `logs/iss327/04_renamed_docs_backup/` (42 份改名后真件) · 报告 `logs/iss327/05_restore_main_report.txt` · 记录 `HANDOFF/2026-11-18_main_ISS327_软链沙盒写穿真件_事故与恢复.md`
- ⇒ ★**起点状态: 真件 `SW/*.md` = 旧名 (闸绿) · 板 = 旧名 · 网表/脚表/BOM = 旧名** ★

### ★③ 续做时必须遵守 (★本单唯一的新规矩·违反就是第二次事故★)
1. ★**沙盒里凡是要【写】的文件 ⇒ 一律真拷贝 (`shutil.copyfile` / `copy_tree`); 软链只许给【只读】输入** ★
2. ★**写之前加断言 `assert not os.path.islink(path)`** ⇒ 软链当场炸, 不再静默写穿 ★
3. ★**真件 `SW/*.md` 一律不许改名**: ★**「改名后闸链全绿」的验证只能在【真拷贝沙盒】里做** ★ ⇒ ★**SW 文档改名必须与板那一趟【同批】落地 (ISS-321/ISS-323 已定: 清单进 `logs/` + 不写死改名后名)★ ★
4. ★**沙盒跑完必查真件 mtime 漂移** ⇒ ★**零漂移才算零写板** ★
5. ★**闸脚本副本也要是真拷贝** (★上一趟 `SW/tools/` 这条做对了·照抄★) ★

### ★④ 交卷时必须附
- ★**真件 mtime 漂移清单 (必须为空)** ★ + 板/网表/脚表/BOM 四 md5 + `check_sw_ref_reachability.py` rc 与分类统计段
