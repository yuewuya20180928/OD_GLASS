# ISS-327 · sw-lead · ★★【cont2 续做 · 交卷收尾】★★

> ★**第二次续做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 15:3x (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: sw-lead (软件总工) · ★**verify_by**: main · ★**单号**: ISS-327 (★**status 保持 fixing**★) · ★**零外发**
> ★**性质**: ★**内部活 · 门禁/判据口径侧 · 纯沙盒验证类** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改既有文档正文** ★

---

## ★★★【★★上一趟 (15:0x) 已经做完了什么 · 这一趟只补什么 ★★★】★★★

★**★上一趟干得很漂亮, 但会话在 14:58 被超时掐掉 ⇒ 你的活是从【已完成的位置】继续★ ★**

★**★main 15:3x 本机实读 (★不抄 agent 报告★) —— 上一趟的成果 (★全部已落盘★)★**:

| 项 | ★读数★ | ★**状态** ★ |
|---|---|---|
| ★`logs/iss327/iss327_sb_make.py` ★ | ★**13,463 B** (★原版 17,757 B 存成 `iss327_sb_make.py.orig_accident_ver` 留证★) ★ | ★**★L126 的 `os.symlink()` 已改成真拷贝 + 加了 `assert_no_symlink_in(root)` (★L67 那个函数★)⇒ 事故根因已修** ★ |
| ★沙盒三臂 ★ | ★`tmp/iss327/sbCtl` (★板 md5 `611b869e…` · 改名后位号命中 **0** 份★) · ★`tmp/iss327/sbR0` (★板 md5 `fadf2c2f…` · 命中 **0** 份★) · ★`tmp/iss327/sbR3` (★板 md5 `fadf2c2f…` · 命中 **6** 份★) ★ | ★**★三臂已建好且互相构成真对照★** ★ |
| ★跑批读数 ★ | ★`logs/iss327/12_sbCtl/` · `13_sbR0/` · `14_sbR3/` · `16_sbR1/` (★每臂 16 份闸读数★) + `19_run_all_cont1.log` (★三臂总表★) + `19b_ctl_rerun.log` (★修 bug 后的 ctl 重跑★) ★ | ★**★已有读数★** ★ |
| ★重建注册表 ★ | ★`15_sbR0_freeze_stdout.txt` (★18 条★) · `17_sbR3_freeze_stdout.txt` (★含 `CONN_CAM_1` / `CONN_LIGHT_1` 等改名后名★) ★ | ★**★重建已跑过★** ★ |
| ★真件快照 ★ | ★`logs/iss327/10_pre_realfile_snapshot.txt` (★7,951 B★) ★ | ★**★真件基线已留证★** ★ |

★**★★你上一趟自己发现并修掉的那个 bug (★很关键, 说明你的自查是有效的★)★**:
★**「`sbCtl` got the HW rename applied, so it wasn't a true control」** ⇒ ★**⇒ 修完的 sbCtl 现在板 md5 = `611b869e…` (★与真件一致★) + 改名后位号命中 0 份 ⇒ ★**它现在才是真对照** ★**

★**★★⇒ ⇒ 【★这一趟的活 ★】★★**:
★**① 把已有读数归并成【三列对照表】+ 补「真隐患不许被洗白」的反向用例 ★**
★**② 写主交付物 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (★现在【不存在】★) ★**
★**③ 写交卷页 (★现在只有 987 B·★没写完★) + 写分片 (★现在 `sw.yaml` 里 `iss327` 命中 **0**★) ★**

---

## ★★① 三列对照表 (★本单的核心交付物·★读数已经有了, 你要归并★★) ★★

★**★你要做的不是重跑, 是【把已有读数归并成一张能下结论的表】★★**

★**★四臂的读数都在 `logs/iss327/1[2-9]_sb*/` 与 `19_run_all_cont1.log` 里 ⇒ ★**先读那些, 不够再补跑★ ★**

| 闸 | ★**改名前 (基线)** ★ | ★**sbCtl** (★整树真拷贝·零改名★) | ★**sbR0** (★五侧改名 + SW 文档未同步 + 旧注册表★) | ★**sbR3** (★五侧改名 + SW 文档已同步 + 重建注册表★) |
|---|---|---|---|---|
| ★10 道闸各一行★ | ★rc + 关键读数 ★★**★直接引用 `logs/iss327/01_baseline/` 的既有读数 (★16 份), 不许重跑基线★**★ | ★rc + 关键读数 ★ | ★rc + 关键读数 ★ | ★rc + 关键读数 ★ |

★**★main 已核到的一件事 (★你要注意它的含义★)★**:
★**`logs/iss327/19b_ctl_rerun.log` (★修 bug 后的 sbCtl 重跑★) 里: `check_demo_panel_spec` rc=0 · `check_onepass_sw_sync` rc=0 · `check_shutdown_semantics` rc=0 · `check_sw_ref_reachability` rc=0 · `timing_check` rc=0 · `check_landing_trace_obligation` rc=0 · `check_demo_panel_spec_r6_selftest` rc=0 ⇒ ★**但 `check_demo_panel_spec_r6_chainjudge_selftest` rc=2 · `check_demo_panel_spec_r6_hardprot_iss315_selftest` rc=2** ★
★**★⇒ ⇒ 而【修 bug 之前】的那份 `19_run_all_cont1.log` 里, sbCtl 那一列【几乎全红】(★`check_demo_panel_spec` rc=1 · `timing_check` rc=1 · `check_sw_ref_reachability` rc=1 …★) ⇒ ★**★⇒ 也就是说: 那份总表里的 sbCtl 那一列是【坏对照臂】的读数, 必须用 `19b_ctl_rerun.log` 那一版★ ⇒ ⇒ ★**★交卷页必须写清「sbCtl 那一列取的是修 bug 后的重跑版」, 不许用旧总表那一列★★ ★**

★**★必须给出的判读 (★逐闸写·不许只写结论★)★**:
★**① 「改名前绿 → 改名后红 → 重建注册表后绿/红」逐闸一行 ⇒ ⇒ **一句话回答: 「重建注册表这条路, 能不能让 SW 侧 10 道闸在改名后全部回绿?」** ★**
★**② 若不能 ⇒ ★**逐闸指出哪几道红是【改名引起】、哪几道红是【本来就红】(★ISS-321 已实测证明「三道 R6 selftest 的红在 S4 vs S8 对照组里同样出现 ⇒ 不是改名特有」★) ⇒ 并且 ★**不许拿「改名引起」当借口把闸调软** ★ ★
★**③ ★★那两道 rc=2 的 (★`r6_chainjudge_selftest` / `r6_hardprot_iss315_selftest`★) 你必须查清 rc=2 到底是什么意思 (★是「反向用例 2 条失败」还是「脚本自己报错」? ★★`logs/iss327/12_sbCtl/check_demo_panel_spec_r6_selftest.txt` 的尾部已经显示「反向用例: 7/7 通过」, 那个文件是 rc=0 的; ⇒ ★★rc=2 的那两个要看它们自己的输出文件★★) ⇒ ⇒ ★**别把 rc=2 当成「红」直接归类, 也不许当绿灯放过** ★ ★

### ★★①-1 ★★「真隐患不许被 `--freeze-registry` 洗白」反向用例 (★本单最要紧的一条·★不许跳过★)★★

★**★在沙盒里把某个【真隐患】(★`TP_TEMP` / `TP_INT` / `CONN_USB` 之一·★建闸日基线那 3 条★) 故意改成一个【新的、从来不存在过的位号形状】⇒ ★**重建注册表之后, 它【必须仍然被抓住】⇒ 如果被洗白了 ⇒ 那就是一条必须报 main 的判据缺陷** ★
★**★你已经有工具了: `logs/iss327/iss327_apply_registry.py` (★1,697 B·★它就是跑 `--freeze-registry` 的★)★ ★

---

## ★★② 主交付物 `SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md` (★现在不存在·★你要新建★) ★★

★**★「板那一趟」当天的 SW 侧 SOP (★照着做就能做, 不是注意事项★)★★**

★**必须包含**:
1. ★**执行顺序 (★机器可判: 每步给命令 + 期望读数 + 失败时的下一步★)** —— ★**顺序不许自己重排, 照 ISS-323 §5-1 的 7 件同批顺序, 你只补【每步的验收命令 + 期望 rc + 期望读数】** ★
2. ★**每道闸改名后的期望读数表** (★就是 §① 那张表的固化版★) ★
3. ★**★「重建注册表」这一步的时机与判据★** ⇒ ★**什么时候重建 · 重建前必须先确认哪些东西已经落定 · 重建后必须重跑哪几道闸 · ★**重建是一次性动作还是每次都要重做** ★ ★
4. ★**★回滚点 (★三档, 不许出现「看情况」★)★** ⇒ ① ★**立刻停** (★板 md5 已变 ⇒ 这次就是「板改了一次」⇒ 不许再改板, 只许修 SW 侧★) ② ★**修 SW 侧某一行** (★给逐字改法★) ③ ★**报 main 升级** (★给需要谁拍什么★) ★ ★
5. ★**★留证清单★★** ⇒ ★**当天跑完要落哪几个文件 (★命令 + 路径 + 期望落点★) ⇒ ★**这些留证必须能证明「板只改了一次」★** (★板 md5 前后各一次 + 网表/脚表/BOM 各一次★) ★
6. ★**★判据设计稿 (★只给设计, 不挂链★)★** ⇒ ★**① 「改名漂移」(`DESIGNATOR_DRIFT`) 这个分类在改名之后【还有意义吗】? ⇒ 没有的话是不是该显式退役 (★留着的代价 = 每次改名都要手动重建一次, 漏一次就长时间红★) ★**② `DESIGNATOR_MISSING` 的上限机制在改名后怎么办 (★现在上限 = 建闸日实测数 3 条 ⇒ 改名后基线会漂 ⇒ 要么跟着重建、要么改成【台账链头】式 (★ISS-275/284 同款★)⇒ 给方案 + 代价 + 建议默认值 + 不拍的后果★** ★**

---

## ★★③ 交卷页 + 分片 (★都还没写完★) ★★

| 产物 | ★现状★ | ★要做的★ |
|---|---|---|
| ★`HANDOFF/2026-11-18_sw-lead_ISS327_改名后SW闸链复活验证.md` ★ | ★**987 B** (★只写了个骨架★) ★ | ★**补齐 B0~B6 六块** (★口径照 `state/gate_check.py` 的 `REQUIRED_BLOCKS`★): B1 结论摘要 · B2 验收标准自评 (★逐条 通过/不通过/未验★) · B3 证据分级 · B4 接口取值声明 · B5 未决项与卡点 · B6 自证复现命令 ★ |
| ★`state/fragments/sw.yaml` ★ | ★`iss327` 命中 **0** ★ | ★**走 `python3 state/frag_write.py --agent sw-lead` 原子写** (★**禁 `open(p,"w")`**★) · artifacts ≥1 · needs_from ≥1 · interface_claims ≥1 · status 换 ISS-327 ★ |
| ★`logs/iss327/` ★ | ★已有 20+ 件★ | ★**追加, 不许覆盖** ★ |

★**★必须交的一条 need (★本单最硬的结论★)★**: ★**`iss327_sw_drift_registry_disposition`** ★ ⇒ ★**「`--freeze-registry` 重建注册表这条路, 能不能让 SW 侧 10 道闸在改名后全部回绿」= 【实测答案】+ 代价 + 建议默认值 + 不拍的后果** ★

---

## ★★④ ★★本单唯一的新规矩 (★违反就是第二次事故★)★★

★**★这 5 条已由兄弟 job 写进原 brief 尾部, 这里再抄一遍 (★因为它比任何技术细节都重要★)★★**:

1. ★**沙盒里凡是要【写】的文件 ⇒ 一律真拷贝 (`shutil.copyfile` / `copy_tree`); 软链只许给【只读】输入** ★
2. ★**写之前加断言 `assert not os.path.islink(path)`** ⇒ ★**软链当场炸, 不再静默写穿** ★
3. ★**真件 `SW/*.md` 一律不许改名** ⇒ ★**「改名后闸链全绿」的验证只能在【真拷贝沙盒】里做** ⇒ ★**★SW 文档改名必须与板那一趟【同批】落地 (★ISS-321/ISS-323 已定: 清单进 `logs/` + 不写死改名后名★)★★ ★
4. ★**沙盒跑完必查真件 mtime 漂移 ⇒ 零漂移才算零写板** ★
5. ★**闸脚本副本也要是真拷贝** (★你上一趟这条做对了·照抄★) ★

★**★★⇒ ⇒ 实操 (★省你一轮★)★★★**:
★**★`logs/iss327/iss327_sb_make.py` 你上一趟已经改好了 (★L126 的 `os.symlink()` → 真拷贝 + L67 的 `assert_no_symlink_in()`★) ⇒ ★**★这一趟【不许再改那个脚本】, 直接用它建臂★ ⇒ ★**但你必须先跑一次 `find tmp/iss327 -type l` 确认它【真的不产软链】(★实测为 0 才继续★) ⇒ ★**并把这条实测贴进交卷页★ ★**

★**★★★⇒ ⇒ 你上一趟自己抓到的那条教训, 这一趟必须写进交卷页★ ★**:
★**★「`sbCtl` got the HW rename applied, so it wasn't a true control」★** ⇒ ★**★★⇒ ⇒ ★★【对照臂必须验它【真的没被施加任何变量】, 这一点本身要成为交卷页里的一节·不是脚注·不是过程说明】★★ ★ ★
★**★⇒ ⇒ 【交卷页必须有一节专讲「对照有效性自检」, 逐条给: 对照臂的板 md5 (必须 = 真件 md5) · 对照臂的改名后位号命中数 (必须 = 0) · 三个臂两两之间的差异是什么】★★ ★ ★**

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
# ★★沙盒里不许有软链 (★证明事故根因已修★) ★★
find tmp/iss327 -type l | wc -l                                                      # 期望 0
grep -cE "🔄|待填|PLACEHOLDER|施工中" SW/ONETRIP_SW_POSTRENAME_GATE_SOP.md   # 期望 0
grep -c "iss327" state/fragments/sw.yaml                                       # 期望 >= 1
```

---

## ★⑦ 纪律 (★★这一趟活也不多, 别再被掐★★)★★

★**① ★★先 `write` 建交卷页骨架 (★把 B0~B6 六个标题先占住★), 再逐块填 (★上一趟两趟都被掐·交卷页一个字没写全★)★★** · ★**② 长任务一律 `nohup ... > logs/iss327/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**③ 单条 `exec` ≤ ~120 秒** · ★**④ 每 10 分钟至少一次写盘** · ★**⑤ 分片写完 `grep` 校验** · ★**⑥ ★★`timing_check.py` / `check_onepass_sw_sync.py` 不支持 `--root` ⇒ 那两道要在沙盒副本目录里 `cd` 进去跑, 且必须贴证据证明它读的是副本不是真件★ ★** · ★**⑦ ★★不许拿「改名引起」当借口把闸调软 —— ISS-321 已实测证明那三道 R6 selftest 的红在 S4 vs S8 对照组里同样出现 ⇒ 不是改名特有★ ★**
