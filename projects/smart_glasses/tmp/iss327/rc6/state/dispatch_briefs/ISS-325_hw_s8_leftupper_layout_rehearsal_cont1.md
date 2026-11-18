# ISS-325 · hw-lead · ★★【cont1 续做 · 收卷】★★

> ★**这是续做, 不是从零重做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 14:2x (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: hw-lead (硬件总工) · ★**verify_by**: main · ★**单号**: ISS-325 (★**status 保持 fixing**★) · ★**零外发**
> ★**性质**: ★**内部活 · PCB 线 · 纯沙盒预演 / 作业包 / 判据设计类 (HW 侧)** ★ ⇒ ★**零写板 · 零落表 · 零改闸 · 零改生成器代码** ★

---

## ★① 上一趟走到哪 / 死在哪 (★main 2026-11-18 14:2x 本机实读·不抄任何 agent 报告★)

★**上一趟**: ★**`agent:hw-lead:subagent:a1789e10-…` 12:59 起 → 13:35 被父 cron run 连带 abort** ★ (★`status=timeout` · `abortedLastRun=true` · `runtimeMs=2118969`★)

★**★★但它启动的两条沙盒臂【还在后台真跑】★★** (★main 14:0x `ps -ef --forest` 实测★):
| 臂 | PID | 启动 | 产物 |
|---|---|---|---|
| ★**左上臂** ★ | ★**1043798** ★ (父 `1043783` = `state/iss325_s8_leftupper_arms.sh`) | ★**13:01** ★ | ★`/tmp/iss325_s8lu_R.kicad_pcb` · 日志 `/tmp/iss325_s8lu_R.log` · DRC `/tmp/iss325_s8lu_R.drc.json` ★ |
| ★**同日对照臂** ★ | ★**1044628** ★ (父 `1044613` = `state/iss325_s8_control_v76mz_arms.sh`) | ★**13:06** ★ | ★`/tmp/iss325_s8ctl_R.kicad_pcb` · 日志 `/tmp/iss325_s8ctl_R.log` · DRC `/tmp/iss325_s8ctl_R.drc.json` ★ |

★**★⇒ ⇒ 第一条纪律: ★★绝对不许重跑那两条臂★★** ⇒ ★**它们已经跑了 1 小时 20 分 (两个核各吃满) ⇒ 重跑 = 白烧一小时 + 覆盖掉已有的 /tmp 产物★**
★**★⇒ ⇒ 正确做法: ★★等它们跑完 → 收割读数 → 补完那 4 处占位符 + 补 §9 + 补交卷页 B1/B2/B4/B5 + 写分片★★**

★**★⇒ 第二条纪律: ★★等臂的时候不许闲着 ★★** ⇒ ★**本单还有 4 件【与臂无关】的活, 现在就能做 (见 §③) ⇒ ★**先做那 4 件, 再去收割臂** ★**

---

## ★② 收割臂的读数 (★臂跑完之后)

★**跑完之后, 按这条命令收割 (★照臂脚本自己的流程★)**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ① 板 + DRC + 段数 + 铜量 (★臂脚本已经跑完裸 DRC, 这里只是复读★)
ls -la /tmp/iss325_s8lu_R.kicad_pcb /tmp/iss325_s8ctl_R.kicad_pcb
ls -la /tmp/iss325_s8lu_R.drc.json /tmp/iss325_s8ctl_R.drc.json
# ② 套链产物 (臂脚本的 replay_patch_chain.sh + clrfix_iter.sh 跑完才有)
ls -la /tmp/chain_iss325_s8lu/ /tmp/chain_iss325_s8ctl/
# ③ 三方 fresh DRC 汇总 (★臂脚本自带的测量脚本★)
bash logs/iss325/scripts/iss325_measure.sh          # ⇒ 落 logs/iss325/09_threeway_fresh_drc.txt
# ④ 名单制闸 (★三条都要抄出来·不许只写「通过/不通过」★)
python3 state/compare_arm_official.py --self-test            # ⇒ 必须 rc=0 · ALL TESTS PASS
python3 state/compare_arm_official.py /tmp/iss325_s8lu_R.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb
python3 state/compare_arm_official.py /tmp/iss325_s8ctl_R.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb
# ⑤ 网名集合三层口径对照
python3 state/cmp_unc_sets.py /tmp/iss325_s8lu_R.drc.json /tmp/iss325_s8ctl_R.drc.json
# ⑥ 段内 P/N 顺序翻转 (★候选板版·ISS-322 的归档原件一个字没改★)
bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py /tmp/iss325_s8lu_R.kicad_pcb lu
bash state/pcbnew_py.sh logs/iss325/scripts/probe_pn_order_cand.py /tmp/iss325_s8ctl_R.kicad_pcb ctl
# ⑦ 零铜 / 有铜未连通 机制表
python3 logs/iss325/scripts/unc_mech_table.py /tmp/iss325_s8lu_R.kicad_pcb
```

★**★`logs/iss325/scripts/iss325_measure.sh` 与 `logs/iss325/scripts/unc_mech_table.py` 的命令行参数口径你必须自己核一遍 (★main 本轮只确认了这两个文件存在 (6,764 B / 3,291 B), ★**没有逐行读过它们的 argv 口径**★) ⇒ ★**不许照抄上面的示例参数, 必须先读脚本再跑**★**

---

## ★③ ★★必须补完的 4 件 (★与臂无关, 现在就能做★)★★

### ★③-1 · ★★交付页 §3-3 的数据格 + 那 4 处占位符 (★`__FLIP__` / `__TOTAL__` / `__UNC__` / `__ZEROREACH__`★)

★**main 本轮实读**: ★**`HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md` 42,815 B · §0~§8 八节 · 但 §3-3 的数据格是空的 (§3-2 表里左上臂/对照臂两行的每个数字都写着 `§3-3`)** ★
★**★而且交付页里有 4 处 `__XXX__` 占位符 (★main 实测位置: §8-1 第 481 行 1 处 + §8-2 第 18 行 3 处★)** ★
★**★⇒ 【重要】★ 那 4 处 `__XXX__` ★**逃过了本项目标准的占位符扫描**★ ⇒ ★**main 实测 `grep -cE "🔄|待填|PLACEHOLDER|施工中"` = **0** ⇒ 但 `grep -oE "__[A-Z_]+__"` = **4** ★ ⇒ ⇒ **★标准扫描有盲区: `__XXX__` 这种下划线包裹的写法抓不到★★** ⇒ ★**本单交卷前必须把这 4 处填掉 (用臂的真实读数), 并且交卷页里要如实写一句「标准占位符扫描对 `__XXX__` 无效 ⇒ 本单额外自查了 `__[A-Z_]+__`」** ★

★**★这 4 处具体要填什么 (★main 已读上下文, 逐条给你★)**:
| 位置 | ★现在长什么样★ | ★要填成★ |
|---|---|---|
| §8-1 第 481 行 | ★`段内 P/N 顺序翻转 = __FLIP__ / __TOTAL__` ★ | ★**左上臂的实跑读数** (★对照臂也要给一份, 放同一句里对比★) ★ |
| §8-2 第 18 行 | ★`左上布局臂 = unc __UNC__ (★对照: 现役 45 / 盘上最好板 23·★三块板都是 fresh DRC★)` ★ | ★**左上臂的 fresh unc** ★ |
| §8-2 第 18 行 | ★`【挪器件】单独能不能归零 = __ZEROREACH__` ★ | ★**能 / 不能 / 读数不够不能判 (★三选一·必须给依据★)** ★ |
| §8-2 第 18 行 | (★同一句里的第三个 `__XXX__`★) | ★**同上·逐个定位·不许留空★** |

★**★★铁律: ★★这 4 处的值必须来自【臂的实跑读数】, 不许从 §6-2 的 `best_unc23_clrfix` 读数 (5/47) 或任何历史板抄过来★★** ⇒ ★**§6-2 那张表量的是【盘上已有的 best23 板】, 而 §3-2/§3-3 量的是【本单新跑的两条臂】⇒ 两者不是同一块板, 不许混用★** ★

### ★③-2 · ★★交付页补 §9 (★证据分级与零写板双证与文件清单★)

★**★main 本轮实读: `grep -c "^## §9"` = **0** ⇒ 交卷页 B0-2 自己写的「§0 … §9」里, ★**§9 根本不存在** ★** ⇒ ★**这是【交卷页与交付页对不上】的实锤, 补上★**
★**§9 必须有**: ★① 逐条证据分级 (★`[实测]` / `[推算]` / `[0数据]` 三档, ★不许出现 `[官网]` / `[媒体]` —— 本单没查外部资料, 出现了就是编的★) ★② 零写板双证 (★板 md5 + mtime, ★交卷前后各一次, 两次都贴进页里★) ★③ 本单产出的文件清单 (★`logs/iss325/` 逐个文件列出来★) ★④ 边界自证 (★哪些既有文件逐字节没变·哪些变了·为什么★) ★

### ★③-3 · ★★交卷页补 B1 / B2 / B4 / B5 (★main 本轮实读: 现在只有 B0 / B3 / B6 三段★)

★**★这是本项目门禁链 `state/gate_check.py` 的 Q1「6 项必填验收块」★★** ⇒ ★**main 本轮实跑 `gate_check.py` ⇒ ★**Q1 = 15/18, 掉的那 3 格就是本单 (hw-lead: 缺 [B2] 验收标准自评 · 缺 [B4] 接口取值声明 · 缺 [B5] 未决项与卡点) ★** ⇒ ⇒ ★**⇒ 本单补完 B1/B2/B4/B5, Q1 就能回到 18/18 ⇒ ★**这条闸现在就在红着等你补, 不是装饰★

| 块 | ★**内容 (★照 `state/gate_check.py` 的 `REQUIRED_BLOCKS` 口径★)** |
|---|---|
| ★**B1** ★ | ★**结论摘要** (★一句话★) ★ |
| ★**B2** ★ | ★**验收标准自评 (★逐条「通过 / 不通过 / 未验」★)** ★ —— ★**不许只写一句「全部通过」★** ⇒ ★**每个验收项都要单独一行 + 判定 + 依据读数★** ★ |
| ★**B3** | ★**证据分级** ★ (★**已有·本轮不用动★**) |
| ★**B4** ★ | ★**接口取值声明 (★`interface_claims`★)** ★ ⇒ ★**照 §4 里那几条逐字给 (★网名 / 坐标 / 数值 / 判据来源★)** ★ |
| ★**B5** ★ | ★**未决项与卡点 (★需要谁回答什么★)** ★ ⇒ ★**照 §7-5 那张表逐条列 (★归 main + 老板的 7 条 need·一条不许漏★)** ★ |
| ★**B6** | ★**自证复现命令** ★ (★**已有·本轮不用动★**) |

### ★③-4 · ★★写分片 (★现在 `state/fragments/hw.yaml` 里 `iss325` 命中 = **0** ★)

★**★main 本轮实读: `grep -c "iss325" state/fragments/hw.yaml` = **0** ⇒ 交卷页 B6 第 ⑩ 条自己写的那条命令现在会返回 0 ⇒ ★**分片一个字没写★** ★
★**必须写**: ★走 `python3 state/frag_write.py --agent hw-lead` (★**禁 `open(p,"w")`**★) ★· artifacts ≥1 · needs_from ≥1 · interface_claims ≥1 · status 换 ISS-326 之前先换 ISS-325 · ★**写完必须 `grep -c "iss325" state/fragments/hw.yaml` ≥ 1 并把读数贴进交卷页★**

---

## ★④ ★★一个必须如实说明的边界事实 (★main 本轮实读·★不许装没发生★)★★

★**★HW/PCB/ 下有 4 个文件被重写了 (★mtime 一直在动: 13:49 → 13:52 → 14:07★)★**

★**main 定位到的根因链 (★逐段读过源码★)**:
★**`state/replay_patch_chain.sh` L240 → 跑 `state/check_pcb_drc.py` → 它的 C5 自检 → 跑 `state/gen_kicad_project.py` → 该脚本无条件写 `HW/PCB/` 下 4 个文件★★**:
★`HW/PCB/STACKUP.md` (★`gen_kicad_project.py` L286★) · ★`HW/PCB/LAYOUT_RULES.md` (★L303★) · ★`HW/PCB/GEN_SELF_CHECK.txt` (★L369★) · ★`HW/PCB/_frame_reference.kicad_pcb` (★L256★)
★**★⇒ ⇒ 你的臂脚本跑了 `replay_patch_chain.sh` ⇒ ⇒ 这 4 个文件被你的臂重写, 不是别人改的★★**

★**★但内容实情是 (★main 实测★)**: ★**`HW/PCB/STACKUP.md` 除首行时间戳外与 11-17 08:34 的旧副本逐字相同** ★ (★`diff <(tail -n +2 旧) <(tail -n +2 新)` ⇒ 无差异★) ⇒ ★**⇒ ⇒ 这 4 个文件是【生成器产物】, 内容等价, 只有时间戳变 ⇒ 不是语义改动★**

★**★★你必须做的事 (★两条, 缺一不可★)★★**:
1. ★**在交卷页 §9 的「边界自证」里如实写**: ★**「本单的臂经 `replay_patch_chain.sh` → `check_pcb_drc.py` → `gen_kicad_project.py` 重写了 `HW/PCB/` 下 4 个生成器产物 (`STACKUP.md` / `LAYOUT_RULES.md` / `GEN_SELF_CHECK.txt` / `_frame_reference.kicad_pcb`); ★**除时间戳外内容逐字相同** (`STACKUP.md` 已实测 diff 确认) ⇒ ★**板面/网表/脚表/BOM 一个字节未动**」 ★**
2. ★**★顺手查一件事并如实报 (★这是本项目的老账★)**: ★**`state/gen_kicad_project.py` 是不是每次跑 `check_pcb_drc.py` 都会无条件重写这 4 个文件? ⇒ ⇒ 如果是 ⇒ ★**这就是一条【复发型缺陷】: 任何跑 `check_pcb_drc.py` 的动作 (包括 `state/daily_check.py`!) 都会改这 4 个文件的 mtime ⇒ ★**本项目每天的巡检都在动这 4 个文件** ★ ⇒ ★**你只需要【如实登记】这件事 (交给 main 判断要不要修), 不许你去改 `gen_kicad_project.py`** ★** ★

★**★★绝对不许做的事★★**: ★**不许把这 4 个文件的改动手动「恢复」回去 (★那叫擦产物·且下一次巡检又会被改·治不了根★)** ★ · ★**不许改 `state/gen_kicad_project.py` / `state/check_pcb_drc.py` / `state/replay_patch_chain.sh` (★零改生成器代码★)** ★

---

## ★⑤ 交卷前必跑 (★原样输出贴进交卷页★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py && python3 state/issue_check.py
python3 state/compare_arm_official.py --self-test      # 必须 rc=0 · ALL TESTS PASS
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb            # 必须 = 2026-11-06 07:07:17.362193413
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
# ★★占位符: 标准扫描 + ★★额外的 `__XXX__` 扫描 (★本单教训★) ★★
grep -cE "🔄|待填|PLACEHOLDER|施工中" HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md   # 期望 0
grep -oE "__[A-Z_]+__" HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md | wc -l          # ★期望 0★
grep -cE "🔄|待填|PLACEHOLDER|施工中" "HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md"   # 期望 0
grep -c "iss325" state/fragments/hw.yaml                                        # 期望 >= 1
grep -c "^## §9" HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md                        # 期望 1
grep -oE "^## B[0-9]" "HANDOFF/2026-11-18_hw-lead_ISS325_左上布局沙盒预演.md" | wc -l   # 期望 6
```

★**★交卷前 ★★`gate_check.py` 的 Q1 必须回到 18/18★★** ⇒ ★**这是本单补 B1/B2/B4/B5 的验收判据 (★main 本轮实跑实测 = 15/18, 缺的那 3 格就是本单★)** ★

---

## ★⑥ 边界 (★违反就是不合格★)

★**零写板** (★`HW/PCB/demo_mainboard.kicad_pcb` md5 必须还是 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**零改闸** (★`state/gate_check.py` / `state/compare_arm_official.py` / `state/cmp_unc_sets.py` / `state/merge.py` / `state/issue_check.py` 只读★) · ★**零改生成器代码** (★`state/gen_pcb_netlist_board.py` / `state/gen_pcb_routing.py` / `state/gen_kicad_project.py` / `state/check_pcb_drc.py` / `state/replay_patch_chain.sh` 只读★) · ★**零改既有文档正文** (★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/LAYOUT_FIX_SPEC.md` / `HW/PCB/BOARD_ONEPASS_S8_ROUTING_WORKPACKET.md` 只读 ⇒ §8 只给逐字改法·不动原文★) · ★**沙盒只写 `tmp/iss325/` + `logs/iss325/`** ★ · ★**只写 `state/fragments/hw.yaml`** ★ · ★**零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料·需要外部资料一律自己网上查 + 标证据等级 + 查不到写降级方案⇒ **没有「批一句可以发」这个选项**★) · ★**不替老板拍板** (★G7 `iss322_s8_rsel_lane_order` 的落板归 main + 老板★) · ★**不自签 `state/issue_log.yaml`** (★签字是 main 的活★)

---

## ★⑦ 纪律 (★这项目的老教训·今天又踩过一遍★)

★**① ★★绝对不许重跑那两条臂 (★PID 1043798 / 1044628 还活着·已经在跑 1h20m·重跑 = 白烧 + 覆盖 /tmp 产物★)★★** · ★**② 交卷单第一件事就是 `write` 建骨架** (★哪怕只写 3 行标题 + 交付物清单★) · ★**③ 长任务一律 `nohup ... > logs/iss325/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**④ 单条 `exec` ≤ ~120 秒** ★ · ★**⑤ 每 10 分钟至少一次写盘** (★★上一趟就是死在「写了一半」的状态上·你要是又被打断, 至少已经写了骨架和分片★) · ★**⑥ 分片写完 `grep` 校验** · ★**⑦ ★★先做 §③ 那 4 件 (与臂无关的), 再去收割臂 ★★** ⇒ ★**⇒ 这样就算你也被 abort, 本单也已经从「4 处占位符 + 缺 §9 + 缺 B1/B2/B4/B5 + 分片未写」推进到「只差臂的读数」★** ★
