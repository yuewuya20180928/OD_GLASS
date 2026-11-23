# ISS-370 · sw-lead · 「板那一趟」腿 B（网表节点具名）对 SW 侧影响面 · 交卷页

★**状态: 已交付 (CONT1 重派 · 2026-11-23 19:43 起 · 19:5x 收工)** ★
★**上一趟会话 `agent:sw-lead:subagent:87136475` (sessionId `a24912b8`) 于 19:29:27 死 (status=timeout + abortedLastRun=true + runtimeMs=715,084) ⇒ 交付物 0/3 ⇒ 本页是 CONT1 续做的交卷页** ★
★**本趟读数全部为本单自己 2026-11-23 19:4x~19:5x 本机实跑** ★

---

## B1 · 结论摘要

### B1-1 · 一句话

★**腿 B 真落盘那天, SW 侧会打红的不是 15 条, 是 16 条** ——
★**13 条语义破坏** (根因 = `timing_check.py` 的 `resolve_chain_landing()` 判中点网靠【精确字符串相等】, 腿 B 把裸位号改成具名脚 `R_BAT_DET_2 pin1` ⇒ 中点网取不到 ⇒ 落点/判决对象/源阻抗/τ 一整串 ADC 判据全塌, 外加 4 条反向用例被连带打红)
★**+ 3 条落表义务** (行数锚点 + md5 锚点 + 三方对账 ⇒ **合法落表即解**)
★**⇒ 而这一趟本来就必须做腿 B ⇒ 不提前查清, 开工当天 SW 门禁当场红 ⇒ 要么硬改闸(把红项调没) 要么板 md5 变第二次(违「板只改一次」)** ★
★**⇒ 本单交付: ① 一页影响面 (§0~§6) ② 一条机器闸 (G0~G8 + `--selftest` 10/10) ③ 一份 10 件同批清单 (跨域那几件只给改法·没代做)** ★

### B1-2 · 交了三件 (★三件·不许扩项★)

| # | 交付物 | 路径 | 大小 | md5 | 状态 |
|---|---|---|---|---|---|
| ① | 一页影响面 | `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` | 54,215 B | `bf234cf397017110adce63385fde8dab` | ★**已落盘** ★ |
| ② | 机器闸 | `SW/tools/check_onepass_legb_sw_impact.py` | 24,850 B | `7059f19d7397bf6039d9f87c9ec8ca8f` | ★**已落盘** ★ |
| ③ | 交卷页 + 分片 + 留证 | 本页 + `state/fragments/sw.yaml` + `logs/iss370/` (36 件) | — | — | ★**已落盘** ★ |

★**★本单与派活书的两处差异 (★本单以实测为准·已写进一页★)** ★
| # | 派活书说 | ★**本单实测** ★ | 处置 |
|---|---|---|---|
| ① | 腿 B 全量红 = **15 条** | ★**`--netlist` 口径 = 15 条 ✓; 落表仿真口径 = 16 条** ★ ⇒ 差的那条是 `网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立` ⇒ ★**该判据直接读【盘上真源】(`timing_check.py` L325) ⇒ `--netlist` 覆盖改不到它★** | 一页 §0-5 / §1-补 专章登记; 新闸 G2 **两套口径都查** |
| ② | G4 判「只改名变体的红项里没有落表义务红」 | ★**实测不成立** ⇒ 只改名变体【确实】含 1 条落表义务红 (md5 锚点·因为它判的是「内容变了没有」)★ | ★**新闸 G4 改成实测成立的分离关系** (只补行变体全落表义务 / 只改名变体其余 13 条全语义 / 全量 = 两者并集) ★ ⇒ ★**照抄派活书措辞会让闸恒红 = 判据自毁** ★ |

### B1-3 · ★**必跑命令原样 rc (★2026-11-23 19:4x~19:5x 本机实跑★)** ★

```bash
python3 SW/tools/timing_check.py                                                      # ★rc=0 · 85/85 全绿★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_REAL_copy.csv      # ★rc=0 · 85/85 (对照组·证明不是路径问题)★
python3 SW/tools/timing_check.py --netlist tmp/iss364_sbx/netlist_v1_legB.csv        # ★rc=1 · 70/85 · 15 条红★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_v1_rename_only.csv # ★rc=1 · 71/85 · 14 条红★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_v1_rowadd_only.csv # ★rc=1 · 73/85 · 2 条红★
python3 tmp/iss370_sbx/gen_landing_sim.py        # ★落表仿真: 改前 69/85 (16 红) · 对照 85/85 · 改后 82/85 (3 红)★
python3 tmp/iss370_sbx/gen_gate_battery.py       # ★闸电池: 对照全绿 · 改前 4 道闸红 + 1 汇总闸红★
python3 SW/tools/check_onepass_legb_sw_impact.py          # ★rc=0 · 9/9 通过★
python3 SW/tools/check_onepass_legb_sw_impact.py --selftest  # ★rc=0 · 10/10 通过★
python3 SW/tools/check_fp_truth_read.py           # ★rc=0 · 绿 7 / 红 0★
python3 SW/tools/check_sw_fp_truth_impact.py      # ★rc=0 · 八条全过★
python3 SW/tools/check_onepass_sw_sync.py         # ★rc=0★
python3 state/merge.py                            # ★rc=0 ★
python3 state/gate_check.py                       # ★rc=0 · Q1 = 18/18★
python3 state/check_brief_commands.py             # ★rc=0 · 9 条待办单 · 有问题的 0 条★
```

★**写完分片后的复跑**: ★`python3 state/merge.py` ⇒ **rc=0** (产出 782 · 阻塞 43 · 未闭合需求 313 · 冲突 0) ★
★`python3 state/gate_check.py` ⇒ **rc=0** · **Q1 = 18/18 个必填验收块齐全** (★交卷页落盘后 Q1 没跌★) ★

### B1-4 · ★**写盘闸实测 (★本单零写真件 ⇒ 改用「边界 md5 前后对照」自证★)** ★

★**本单对【受保护资产】的写入次数 = 0** ⇒ 不适用「写盘闸拒写路径」那种自证 (★那是写盘型单的验收项★)
★**⇒ 改用【开工前 + 交卷后各打一次 md5 + mtime + size 逐字节对照】, 见 §B6-2** ★
★**四份真源 + 12 个既有闸脚本 + 5 份既有页面 + 2 份 main 地界台账 ⇒ 全部逐字节未变** ★

### B1-5 · ★**本单最有价值的一条发现 (★必须让 main 知道★)** ★

★**「腿 B 会打红 SW 门禁」这件事, 派活书给的是 15 条, 本单独立实跑落表仿真给的是 16 条** ★
★**⇒ 差的那一条恰恰是【真落盘那天才出现的那一条】⇒ ★只跑 `--netlist` 的沙盒会【系统性低估】破坏面★** ★
★**⇒ 同理, 派活书 §0⑤ 列的「哪些闸不受影响」也只在 `--netlist` 口径成立** ——
★**本单实跑落表仿真后补出两件派活书没写的: ① `check_timing_review_adc_sync.py` 会从 rc=0 变 rc=2 (ADC 字段全 None ⇒ fail-closed) ⇒ 【补丁修好第 1 件后自动回绿】 ② `check_onepass_sw_release.py` 汇总闸从 rc=0 变 rc=1 (7 道子闸红)★** ★

---

## B2 · 验收标准自评 (★逐条 通过 / 不通过 / 未验★)

| # | 验收项 | 判定 | 依据 |
|---|---|---|---|
| ① | 页存在且非空 | ★**通过** ★ | `SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` · 54,215 B · md5 `bf234cf3…` |
| ② | 三个数 (196 / 改动栏 ⊆ {node1,node2} / 513→517) 与脚本实算一致 | ★**通过** ★ | 新闸 **G1 PASS** (★脚本自己逐格算, 不抄页★) · 留证 `logs/iss370/30_CONT1_g1_numbers.txt` |
| ③ | **15 条红逐条齐全且与自跑集合一致** | ★**通过** ★ | 新闸 **G2 PASS** (★`--netlist` 口径 15 条集合完全相等★) · 留证 `logs/iss370/26_CONT1_fail_sets.txt` |
| ④ | 每条红有归类 (★三类之一★) | ★**通过** ★ | 新闸 **G3 PASS** · 15 + 1 = 16 条全部 ∈ {语义破坏, 落表义务, 反向用例} |
| ⑤ | §2 同批清单每件 8 字段齐全 | ★**通过** ★ | 新闸 **G5 PASS** · 10 件 · 8 字段 (no/file/owner/timing/kind/fix/readback/evidence) 全非空 |
| ⑥ | 跨域那几件归属写「跨域·不是 SW 的域」且你**没碰** `HW/` 任何文件 | ★**通过** ★ | 新闸 G5 强制: `file` 以 `HW/`/`state/` 开头的件 · 归属必须同时含「跨域」与「不是 SW 的域」 ⇒ 件 3/4/6/7/8/9 全合规; ★`HW/` 四个真源 md5 交卷前后逐字节相同 (见 B6-2)★ |
| ⑦ | 改法逐条具体 (★无空洞词★) | ★**通过** ★ | 新闸 G5 的空洞词黑名单 (调整相关逻辑/适当处理/酌情/视情况而定/相关处理/相应修改/同步更新一下/改一下/相关逻辑/按需调整) + 长度 < 20 字 ⇒ 全过 |
| ⑧ | §3 三条反向自证全部自证成功 | ★**通过** ★ | ① 只改名 ⇒ 14 红 (13 语义 + 1 落表义务) ② 只补行 ⇒ 2 红全落表义务 + 语义红 0 ③ 真网表 ⇒ 85/85 三处全绿; ★**本单另加第 ④ 条: 补丁只回绿语义红 (69/85 → 82/85), 落表义务红一条都没被顺手调没** ★ |
| ⑨ | 证据等级全在五级白名单 | ★**通过** ★ | 新闸 **G6 PASS** (白名单 官网/实测/媒体/推算/0数据; `[官方]` 等禁用词全扫) |
| ⑩ | 降级方案逐件非空 | ★**通过** ★ | 一页 §4 · ★**10 件逐件非空** · 9 件「沙盒验证法」+ 1 件「改设计路径绕开」(件 2) ⇒ ★**并写明「没有一件能用『官网参数可满足的等效件』那档, 理由: 这是字符串形态问题不是器件选型问题」** ★ |
| ⑪ | 正文零挂起措辞 | ★**通过** ★ | 新闸 **G7 PASS** (10 个禁词全扫) |
| ⑫ | 自建闸裸跑 rc=0 | ★**通过** ★ | `python3 SW/tools/check_onepass_legb_sw_impact.py` ⇒ **rc=0 · 9/9 通过** · 留证 `logs/iss370/31_CONT1_gate_run.txt` |
| ⑬ | `--selftest` ≥7/7 全 PASS 且每条自证「只红目标那条」 | ★**通过 (★10/10★)** ★ | ①~⑩ 十条全 PASS; ★**每条都断言「红的集合 == {目标那一条}」, 多红一条即判该用例 FAIL** · 留证 `logs/iss370/32_CONT1_gate_selftest.txt` |
| ⑭ | 沙盒在项目盘 `tmp/iss370_sbx/` (★不写 /tmp★) | ★**通过** ★ | 本单沙盒 = `tmp/iss370_sbx/` (含 `land_root/` `land_root_base/` `land_root_fix/` 三个镜像根 + 脚本); ★**新闸自己的沙盒 = `tmp/iss370_gate_sbx/`** ⇒ ★**系统 /tmp 一个字节没写★** |
| ⑮ | **板 md5/mtime 逐字节未变** | ★**通过** ★ | md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17.362193413` · size 4,940,213 B ⇒ 开工前 = 交卷后 |
| ⑯ | **网表/脚表/BOM md5 逐字节未变** | ★**通过** ★ | 网表 `6aee500e60ba…` · 脚表 `9174309df1ec…` · BOM `5b9993992405…` ⇒ 开工前 = 交卷后; ★**脚表 mtime 被顶到 19:19:15 是假象 (内容 md5 = 基线), 已写进一页 §0-7 + 交卷页 B5-3** ★ |
| ⑰ | 既有闸脚本一个字节没改 | ★**通过** ★ | 12 个脚本 md5 开工前 = 交卷后 (含 `timing_check.py` `cf09c921…` `check_demo_panel_spec.py` `4d9c21dd…` `state/gate_check.py` `5f370bb8…` `state/merge.py` `state/frag_write.py`) ⇒ 见 B6-2 |
| ⑱ | `merge.py` rc=0 | ★**通过** ★ | `python3 state/merge.py` ⇒ **rc=0** · 产出 782 · 阻塞 43 · 未闭合需求 313 · 冲突 0 |
| ⑲ | `gate_check.py` rc=0 且 Q1 18/18 | ★**通过** ★ | `python3 state/gate_check.py` ⇒ **rc=0** · **【Q1 交付齐备率】18/18 个必填验收块齐全** · 留证 `logs/iss370/35_CONT1_gate_check.txt` |
| ⑳ | 分片只走 `frag_write.py` + 交卷页 B1~B6 齐全 + `logs/iss370/` 留证在盘 | ★**通过** ★ | ★**分片 100% 走 `state/frag_write.py --agent sw-lead` 的命令行入口** (★脚本 `tmp/iss370_sbx/write_frag_iss370.py` 只做 subprocess 调它, 不碰它的实现·不绕过它写文件★) ⇒ 写了 3 artifacts + 3 needs + 1 interface_claim + status; ★**`hw.yaml` / `mech.yaml` / `pm.yaml` 三个分片 md5 开工前 = 交卷后 ⇒ 本单一个字没写别人的分片** ★; ★**B1~B6 六段齐全** ★; ★**`logs/iss370/` = 36 件** (★上一趟留证 12 件 + 本趟 24 件★) ★ |

### B2-1 · ★**本单实测发现的三个「派活书没写」的事实 (★交上去供 main 裁·不代裁★)** ★

| # | 事实 | 证据 | 影响 |
|---|---|---|---|
| ① | ★**落表仿真的红数是 16 不是 15** ★ | `logs/iss370/28_CONT1_landing_sim.txt` (改前 69/85 · 16 红) | 一页 §0-5 / §1-补; 新闸 G2 两口径都查 |
| ② | ★**`check_timing_review_adc_sync.py` 在落表仿真下 rc=0 → rc=2** ★ (★派活书 §0⑤ 的「不受影响」清单里没有它★) | `logs/iss370/29_CONT1_gate_battery.txt` | 一页 §0-6 + §2 件 2 (随第 1 件自动回绿) |
| ③ | ★**`check_onepass_sw_release.py` 汇总闸 rc=0 → rc=1 (7 道子闸红)** ★ | 同上 | 一页 §0-6; 那一趟开跑前必须复跑它 |

---

## B3 · 证据分级 (★五级白名单: 官网 / 实测 / 媒体 / 推算 / 0数据★)

### B3-1 · 本单的证据分布

| 等级 | 处数 | 本单哪里用的 |
|---|---|---|
| ★**[实测]** ★ | ★**本单全部读数** ★ | ★**三个数 (196 / 改动栏 / 513→517)、五组 timing_check 读数、三套镜像根读数、13 条红项原文、四份真源 md5、新闸 9/9 + selftest 10/10、merge/gate_check rc** ★ |
| ★**[推算]** ★ | 1 处 | ★**§5-1 U1/U2 的「选 A / 选 B 各是什么后果」—— 那是基于实测读数的推演, 不是实测** ★ |
| ★**[官网]** ★ | 0 处 | ★**本单没有引用任何官网参数 ⇒ 不用它** ★ |
| ★**[媒体]** ★ | 0 处 | ★**本单零外部调用 ⇒ 不用它** ★ |
| ★**[0数据]** ★ | 0 处 | ★**本单所有结论都有实测读数 ⇒ 没有「没测」的地方** ★ |

### B3-2 · ★**逐条证据出处 (★每一处都能被 §B6-1 的命令复现★)** ★

| 主张 | 等级 | 出处 |
|---|---|---|
| 改动格数 = 196 (node1 120 + node2 76) · 改动栏 ⊆ {node1,node2} | ★[实测] ★ | `logs/iss370/30_CONT1_g1_numbers.txt` (脚本自己逐格算) |
| 行数 513 → 517 (Δ=+4) | ★[实测] ★ | 同上 + 一页 §0-1 |
| 基线 / 对照组 = 85/85 · rc=0 | ★[实测] ★ | `logs/iss370/21_…` · `logs/iss370/23_…` |
| 腿 B 全量 `--netlist` = 70/85 · 15 红 · rc=1 | ★[实测] ★ | `logs/iss370/22_…` |
| 只改名 = 71/85 · 14 红 · rc=1 | ★[实测] ★ | `logs/iss370/24_…` |
| 只补行 = 73/85 · 2 红 · rc=1 | ★[实测] ★ | `logs/iss370/25_…` |
| 13 条语义红的原文 + 三组红项集合关系 | ★[实测] ★ | `logs/iss370/26_CONT1_fail_sets.txt` |
| 根因 = `resolve_chain_landing()` L1026 精确字符串相等 | ★[实测] ★ | ★**本单实读源码 + 实读两行网表 (基线 L181 / 腿 B L181) + `--json` 实读 `landing_net=""` / `active_chain="(无: fail-closed)"` / `rth_ohm=None`** ★ · `logs/iss370/27_CONT1_legB_json.txt` |
| ★**落表仿真 = 69/85 · 16 红** ★ | ★[实测] ★ | `logs/iss370/28_CONT1_landing_sim.txt` (★自建镜像工程根·真件零改动★) |
| ★**第 16 条 = 三方对账 (只在落表仿真出现)** ★ | ★[实测] ★ | 同上 + ★**源码定位 `timing_check.py` L325 `disk = os.path.join(_PROJECT_ROOT, NETLIST_REL)`** ★ |
| 补丁后 = 82/85 · 3 红 (语义红全回绿) | ★[实测] ★ | 同上 (`land_root_fix`) |
| 4 道闸会红 + 4 道闸不受影响 | ★[实测] ★ | `logs/iss370/29_CONT1_gate_battery.txt` (★三套镜像根对照★) |
| 沙盒完整性自坑 (R6 两道反向用例闸假红 = 缺 `.bak_iss*`) | ★[实测] ★ | 同上 + 本单自修记录 (一页 §0-6 末) |
| 新闸 9/9 绿 · `--selftest` 10/10 | ★[实测] ★ | `logs/iss370/31_…` · `logs/iss370/32_…` |
| 四份真源 md5 未变 | ★[实测] ★ | `logs/iss370/20_CONT1_00_baseline_md5.txt` + `logs/iss370/36_CONT1_final_boundary.txt` |

### B3-3 · ★**一条必须说清的观察 (★不是本单干的·但必须留痕★)** ★

★**`HW/netlist_v1_pins.csv` 的 mtime 被顶到 2026-11-23 19:19:15 (★本单开工前就是这样★), 但内容 md5 仍 = 基线 `9174309df1ec…` ⇒ ★**不是落表**★ ⇒ ★**任何按 mtime 判的闸会假红 ⇒ 一律按内容 md5 判** ★ ★[实测]★

---

## B4 · 接口取值声明 (interface_claims)

### B4-1 · 本单落进分片的 interface_claim (★键名带 `iss370` 前缀★)

★**键**: `iss370_legb_sw_landing_contract` (★写在 `state/fragments/sw.yaml` 的 `interface_claims` 段★)

★**取值 (★摘要·完整版在分片里★)**: ★
★**腿 B 落到 SW 侧是【一个原子动作的六步】不许拆开交班**: ① 腿 B 落表 ② 落表台账链前移 ③ SW 锚点重锚 ④ SW 取链归一化 ⑤ issue_log 留痕 ⑥ 复跑自证 ★
★**六步之间任何一步停 ⇒ 门禁链红着交班**: ①~③ 之间停 = 3 条落表义务红 + R6 红 + W6 红 + 三道 R6 反向用例闸 rc=2; ④ 没做 = 13 条语义红 + `check_timing_review_adc_sync` rc=2 ⇒ ★**合计 16 条红, 不是 15 条** ★
★**只跑 `--netlist` 沙盒看不见第 16 条 (那条判据直接读盘上真源) ⇒ 落表仿真的读数才是真落盘那天的读数** ★
★**四份真源 md5 在 SW 侧本单前后逐字节未变** ★

### B4-2 · ★**本单给下游的取值 (★只声明·不越界拍板★)** ★

| 给谁 | 取什么 | 边界 |
|---|---|---|
| ★**hw-lead** ★ | 腿 B 落表那一跳的【改法 + 时序 + 会红哪道闸】 (一件 need) | ★**只给改法·不许代做**★ ⇒ SW 侧 `HW/` 一个字节没碰 |
| ★**main** ★ | ① 新闸挂不挂链 ② 落表单号谁签 ③ 窗口多长 (一件 need, 三问) | ★**只登记·不代拍**★ |
| ★**sw-lead (自己)** ★ | 一页 §2 的 10 件同批清单 = 那一趟的执行清单 | ★**§2 里写的是「这一趟要怎么改」·本单一个字都没真改**★ |

---

## B5 · 未决项与卡点 (★需要谁回答什么★)

### B5-1 · ★**要老板拍的 (★本单只登记缺口 + 依据 + 代价·**不代拍**★)** ★

| # | 缺口 | 依据 | 代价 (选 A / 选 B 各是什么后果) | 状态 |
|---|---|---|---|---|
| ★**U1** ★ | 腿 B 那一跳: 【落表】与【SW 侧取链归一化】谁先做? | ★实测: 不做归一化 ⇒ 落表做完仍 13 条语义红; 不做落表 ⇒ 4 道闸红 (含 2 道 R6 反向用例闸因「基线不绿」rc=2) ★ | ★**选 A (先落表再改闸)**: 中间窗口门禁链红着, 窗口多长要 hw-lead 排期 ★ **选 B (先改闸再落表)**: 窗口里只剩 13 条语义红, 落表那一步做完就全绿 ⇒ **窗口更干净** ★ | ★**登记·待拍** ★ |
| ★**U2** ★ | 第 513 行数据行锚点改 517: 这是【受保护判据】变更, 谁批? | ★`timing_check.py` L2140 硬写 `netlist_data_rows == 513`; 腿 B 合法补 4 行 ⇒ 判据必须跟着走 ★ | ★**选 A (改成 517)**: 判据跟着真源走, 但属受保护判据 ⇒ 需批准 ★ **选 B (不改)**: 那条红永久挂着 ⇒ **门禁链永远红** ⇒ 不可接受 ★ | ★**登记·待拍** ★ |
| ★**U3** ★ | 要不要取消腿 B (退回裸位号)? | ★§4 件 2 的「改设计路径绕开」 ★ | ★**选 A (照做腿 B)**: 承担 10 件同批清单 + 一次落表 ★ **选 B (取消)**: 200 条具名指令作废, 网表继续裸位号 ⇒ 脚表核对仍靠人眼 ★ | ★**登记·待拍** ★ |

### B5-2 · ★**要 main 裁的 (★写清「要谁回答什么」★)** ★

| # | 要谁 | 回答什么 | 状态 |
|---|---|---|---|
| ★**U4** ★ | main | ★**新闸 `SW/tools/check_onepass_legb_sw_impact.py` 挂不挂进 `state/gate_check.py`? ★** (★本单零挂链⇒`state/gate_check.py` md5 `5f370bb8…` 前后同值★) | ★**登记·待裁** ★ |
| ★**U5** ★ | main | ★**腿 B 落表单号是谁签? ★** (★落表台账链前移 + `state/issue_log.yaml` 留痕都要单号·单号是 main 签的★) | ★**登记·待裁** ★ |
| ★**U6** ★ | main | ★**腿 B 那一趟的「板只改一次」窗口有多长? ★** (★决定 U1 的中间窗口代价★) | ★**登记·待裁** ★ |
| ★**U7** ★ | hw-lead | ★**腿 B 落表那一跳: 网表写盘与落表台账链前移是【同一个原子动作】还是【两步】? ★** | ★**登记·已交 need** ★ |

### B5-3 · ★**并发事实 (★不是本单干的·但必须让 main 知道★)** ★

★**① 本单只写 `state/fragments/sw.yaml`** ⇒ `hw.yaml` `472bb03a…` / `mech.yaml` `0e69d443…` / `pm.yaml` `389ebf7c…` 三个分片 md5 开工前 = 交卷后 ⇒ ★**本单一个字没写别人的分片** ★
★**② `state/issue_log.yaml` `618f0e54…` 与 `state/dispatch_log.yaml` `af241bc6…` 本单一个字没写** ★
★**③ 本单全程【没有起第二个 sw-lead 会话】** ⇒ 遵守 CONT1 并发守卫 (★兄弟 job cron 775d9893 与本单共用 main 这一个 agent·它 19:37 给 hw-lead 派了 ISS-366 CONT2·本单没占第二个槽位★) ★

### B5-4 · ★**本单【没有】做的事 (★防止下一个人误以为已经做过了★)** ★

| # | 没做 | 为什么 |
|---|---|---|
| ★**N1** ★ | ★**没改 `SW/tools/timing_check.py`** ★ | 零改既有闸 ⇒ 一页 §2 件 1 的改法只是【清单里的字】 |
| ★**N2** ★ | ★**没碰 `HW/` 下任何文件** ★ | 零落表 + 不写别人的域 ⇒ md5 见 B6-2 |
| ★**N3** ★ | ★**没把新闸挂进 `state/gate_check.py`** ★ | 零挂链 (main 的机制地界) |
| ★**N4** ★ | ★**没写 `state/issue_log.yaml` / `state/dispatch_log.yaml`** ★ | 那两份是 main 的地界 |
| ★**N5** ★ | ★**没改既有页面正文** ★ (`SW/BOARD_ONEPASS_SW_SYNC.md` / `SW/SW_MD5_BASELINE_LEDGER.md` / `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` / `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md`) | 零改既有页面正文 ⇒ 只在交卷页里给建议 |
| ★**N6** ★ | ★**没发任何邮件 / 询价 / 问询 / 采购** ★ | 零外发 ⇒ 本单零外部调用, 缺口全部自己本机实读 + 沙盒实跑 |

---

## B6 · 自证复现命令

### B6-1 · 逐条照抄跑 (★全部在本项目根下跑★)

```bash
# ★★本单三件交付物 ★★
python3 SW/tools/check_onepass_legb_sw_impact.py                 # ★rc=0 · 9/9★
python3 SW/tools/check_onepass_legb_sw_impact.py --selftest      # ★rc=0 · 10/10★
ls -la SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md "HANDOFF/2026-11-23_sw-lead_ISS370_腿B对SW侧影响面.md"

# ★★五组对照 (★本单自己跑的读数出处★) ★★
python3 SW/tools/timing_check.py                                                      # ★85/85 rc=0★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_REAL_copy.csv      # ★85/85 rc=0★
python3 SW/tools/timing_check.py --netlist tmp/iss364_sbx/netlist_v1_legB.csv        # ★70/85 15红 rc=1★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_v1_rename_only.csv # ★71/85 14红 rc=1★
python3 SW/tools/timing_check.py --netlist tmp/iss370_sbx/netlist_v1_rowadd_only.csv # ★73/85  2红 rc=1★
grep '\[FAIL\]' logs/iss370/22_CONT1_timing_legB_full.txt
grep '\[FAIL\]' logs/iss370/24_CONT1_timing_rename_only.txt
grep '\[FAIL\]' logs/iss370/25_CONT1_timing_rowadd_only.txt

# ★★落表仿真 (★自建镜像工程根·真件零改动★) ★★
python3 tmp/iss370_sbx/gen_landing_sim.py      # ★改前 69/85 (16 红) · 对照 85/85 · 改后 82/85 (3 红)★
python3 tmp/iss370_sbx/gen_gate_battery.py     # ★闸电池三套镜像根对照★

# ★★既有闸 (只读用 · 读完须仍 rc=0) ★★
python3 SW/tools/check_fp_truth_read.py         # ★rc=0★
python3 SW/tools/check_sw_fp_truth_impact.py    # ★rc=0★
python3 SW/tools/check_onepass_sw_sync.py       # ★rc=0★
python3 state/merge.py                          # ★rc=0★
python3 state/gate_check.py                     # ★rc=0 · Q1 18/18★
python3 state/check_brief_commands.py           # ★rc=0★

# ★★边界自证 ★★
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
md5sum SW/tools/timing_check.py SW/tools/check_demo_panel_spec.py state/gate_check.py state/merge.py state/frag_write.py
md5sum state/fragments/sw.yaml state/fragments/hw.yaml state/fragments/mech.yaml state/fragments/pm.yaml
```

### B6-2 · 边界自证读数 (★期望值 vs 实测值★)

| 边界 | 期望 | ★**实测 (开工前 → 交卷后)** ★ | 判定 |
|---|---|---|---|
| ★**板 md5** ★ | `611b869e13518c3c023fb178f91a0075` | ★`611b869e13518c3c023fb178f91a0075` → `611b869e13518c3c023fb178f91a0075` ★ | ★**未变** ★ |
| ★**板 mtime / size** ★ | `2026-11-06 07:07:17.362193413` / 4,940,213 B | ★`2026-11-06 07:07:17.362193413` / 4,940,213 B → 同值 ★ | ★**未变** ★ |
| ★**网表 md5** ★ | `6aee500e60ba0732f83a9cf557ba90ab` | ★同值 → 同值 ★ | ★**未变** ★ |
| ★**脚表 md5** ★ | `9174309df1ec9411ac8e8d9e80ee386a` | ★同值 → 同值 ★ (★mtime 19:19:15 是开工前就有的假象·内容没变★) | ★**未变** ★ |
| ★**BOM md5** ★ | `5b9993992405904a60ac96a020b375d8` | ★同值 → 同值 ★ | ★**未变** ★ |
| ★**`SW/tools/timing_check.py`** ★ | `cf09c921002937920bfa40701d523b33` | ★同值 → 同值 ★ | ★**未改既有闸** ★ |
| ★**`SW/tools/check_demo_panel_spec.py`** ★ | `4d9c21dd0125b3b0e1a7e567852287b8` | ★同值 → 同值 ★ | ★**未改既有闸** ★ |
| ★**`SW/tools/check_shutdown_semantics.py`** ★ | `e8b22d9ecf2b312853e288896785b681` | ★同值 → 同值 ★ | ★**未改既有闸** ★ |
| ★**`SW/tools/check_sw_ref_reachability_v2.py`** ★ | `1c4043ea26a1182b210e85f1b5130d8d` | ★同值 → 同值 ★ | ★**未改既有闸** ★ |
| ★**`SW/tools/check_onepass_sw_sync.py`** ★ | `3984cab48cea0201a5187abaaa4c9499` | ★同值 → 同值 ★ | ★**未改既有闸** ★ |
| ★**`SW/tools/check_fp_truth_read.py`** ★ | `cab7a6f17c1da35f4e54185ad8b62089` | ★同值 → 同值 ★ | ★**未改既有闸** ★ |
| ★**`SW/tools/check_sw_fp_truth_impact.py`** ★ | `94fa1fbb0124921df1ad391f894beacb` | ★同值 → 同值 ★ | ★**未改既有闸** ★ |
| ★**`state/gate_check.py`** ★ | `5f370bb8cf828473e70ccc5d6412da98` | ★同值 → 同值 ★ | ★**零挂链** ★ |
| ★**`state/merge.py` / `state/frag_write.py`** ★ | `c9191025020fefd9b475e2573a335815` / `3b383a52b4fa540f1d16a2c6f3811de8` | ★同值 → 同值 ★ | ★**未改** ★ |
| ★**既有页面 5 份** ★ | `SW/SW_MD5_BASELINE_LEDGER.md` `83fafcf7…` · `SW/BOARD_ONEPASS_SW_SYNC.md` `b8f935db…` · `SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md` `d6708382…` · `HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md` `1e9c9350…` · `HW/SCHEMATIC_LANDING_V1_LANDED.md` `d1a7765b…` | ★同值 → 同值 ★ | ★**未改既有页面正文** ★ |
| ★**main 地界台账 2 份** ★ | `state/issue_log.yaml` `618f0e54…` · `state/dispatch_log.yaml` `af241bc6…` | ★同值 → 同值 ★ | ★**没写 main 的台账** ★ |
| ★**别人的分片 3 份** ★ | `hw.yaml` `472bb03a…` · `mech.yaml` `0e69d443…` · `pm.yaml` `389ebf7c…` | ★同值 → 同值 ★ | ★**没写别人的分片** ★ |
| ★**本单分片** ★ | 允许变 | ★`2a717d10…` → `37f8663e…` (★只经 `state/frag_write.py --agent sw-lead` 写★) | ★**只走 frag_write** ★ |
| ★**本单新建 3 件** ★ | 新增 | ★`SW/BOARD_ONEPASS_LEGB_SW_IMPACT.md` `bf234cf3…` · `SW/tools/check_onepass_legb_sw_impact.py` `7059f19d…` · 本页 `137d6d43…` → 落盘后重算 ★ | ★**本单唯一新增** ★ |
| ★**沙盒位置** ★ | 项目盘 | ★`tmp/iss370_sbx/` + `tmp/iss370_gate_sbx/` ⇒ ★**系统 /tmp 一个字节没写** ★ | ★**通过** ★ |

### B6-3 · 留证路径 (★`logs/iss370/` = **36 件** ★)

★**上一趟 (12 件 · 本单没重跑·只续写)**: ★`00_baseline_md5.txt` · `01_timing_baseline.txt` · `02_timing_REAL_copy.txt` · `03_timing_legB_full.txt` · `04_timing_rename_only.txt` · `05_timing_rowadd_only.txt` · `06_check_*_sbxroot.txt` (4 件) · `07_collected.txt` · `08_check_*_sbxroot.txt` (3 件) · `09_sw_sync_legB.txt` · `10_sw_release_CONTROL_real.txt` · `11_patch_fix_sandbox.txt` · `12_patch_fix_sandbox_v2.txt` ★

★**本趟 CONT1 (24 件 · 全部本单自己实跑)**: ★

| 文件 | 内容 |
|---|---|
| `20_CONT1_00_baseline_md5.txt` | ★开工前边界 md5 基线 (四份真源 + 12 个既有闸 + 5 份既有页面)★ |
| `21_CONT1_timing_baseline.txt` | ★基线 85/85 rc=0★ |
| `22_CONT1_timing_legB_full.txt` | ★腿 B 全量 `--netlist` 70/85 · 15 红★ |
| `23_CONT1_timing_REAL_copy.txt` | ★对照组 (真网表内容换路径) 85/85 rc=0★ |
| `24_CONT1_timing_rename_only.txt` | ★只改名 71/85 · 14 红★ |
| `25_CONT1_timing_rowadd_only.txt` | ★只补行 73/85 · 2 红★ |
| `26_CONT1_fail_sets.txt` | ★★三组红项原文逐条 + 集合关系 (13/1/1)★ ★ |
| `27_CONT1_legB_json.txt` | ★`--json` 机读: `landing_net=""` / `active_chain="(无: fail-closed)"` / `rth_ohm=None` / `NETLIST_ANCHOR`★ |
| `28_CONT1_landing_sim.txt` | ★★落表仿真三读数 (改前 69/85 16 红 · 对照 85/85 · 改后 82/85 3 红)★ ★ |
| `29_CONT1_gate_battery.txt` | ★闸电池 (三套镜像根 × 7 道闸) + 真实件 md5 前后对照★ |
| `30_CONT1_g1_numbers.txt` | ★三个数逐格计算 (196 / node1 120 + node2 76 / 513→517)★ |
| `31_CONT1_gate_run.txt` | ★新闸裸跑 9/9 rc=0★ |
| `32_CONT1_gate_selftest.txt` | ★新闸 `--selftest` 10/10★ |
| `33_CONT1_frag_write.txt` | ★分片写入 (前后 md5 + 别人的分片未变)★ |
| `34_CONT1_existing_gates.txt` | ★既有闸复跑 rc (4 道全 0)★ |
| `35_CONT1_gate_check.txt` | ★`state/gate_check.py` rc=0 · Q1 18/18★ |
| `36_CONT1_final_boundary.txt` | ★交卷前边界自证 (全部 md5 + mtime + size)★ |
| `99_CONT1_resume_20260723_1946.md` | ★上一趟留下的 CONT1 恢复说明★ |

★**沙盒脚本 (★都在项目盘 `tmp/iss370_sbx/`★)**: `gen_landing_sim.py` (落表仿真) · `gen_gate_battery.py` (闸电池) · `probe_copy_root.py` (拷贝式镜像根探针) · `write_frag_iss370.py` (分片写入) ★
★**新闸自己的沙盒**: `tmp/iss370_gate_sbx/land_root/` (★新闸每次跑都重建它★) ★

---

★**交卷完毕 · ISS-370 · sw-lead · 2026-11-23 CONT1 · 交付 3 件 · 20 条验收全通过 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零挂链 · 零外发** ★
