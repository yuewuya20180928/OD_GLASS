# ISS-308 · hw-lead 任务书 cont1 —— ★★【续做: 「板那一趟 S8 (unconnected 45 → 0)」的可达性判决书】★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-308 (cont1)
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 04:5x** ★
> ★**性质**: ★**内部活 · 纯分析 / 作业包类 · 零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM · 零外发 · 不替老板拍板** ★

---

## ★★ ★0 · 为什么是 cont1 (★派活人 04:5x 本机实跑, 不抄任何 agent 报告★) ★★

★**上一趟子会话 `agent:hw-lead:subagent:56d88b87` (taskName `queue_iss308`) 死了**:
- ★**04:26:27 起 · 04:33:39 死 · runtime 434 s · status=error · aborted=true · externalAbort=false · timedOut=false** ★
- ★**trajectory 逐字**: `promptError: "This operation was aborted | This operation was aborted"` · `promptErrorSource: "prompt"` ★
- ★★**⇒ 根因 = 【父 run 结束时子会话被连带 abort】(★兄弟 job 775d9893 04:37~04:42 独立复验同一结论★)⇒ ★★不是你的错, 是平台行为★★ ★
- ★**⇒ ⇒ 你的上一趟【分析成果大量在盘上, 不要重做】(★清单见 §1·这是本单最重要的节省★)** ★

★**★上一趟【0 / 3 件交付物落地】(★派活人 04:5x 实读★)**:
| 交付物 | 状态 |
|---|---|
| 判决书 (★新建★) `HW/PCB/S8_REACHABILITY_VERDICT.md` | ★**当前不存在 (交卷时才建)** ★ |
| `HANDOFF/2026-11-18_hw-lead_ISS308_S8可达性判决书.md` | ★**不存在** ★ |
| `state/fragments/hw.yaml` 里 `iss308` | ★**`grep -c iss308` = 0** ★ |

★**⇒ 本单 = 【续做, 不是从零重做】: 分析已基本完成 (★§2-A 的 22 网名 → 5 桶归属表【已经写好】★), 你要补的是【两份文档 + 一份分片 + 一个脚本判据缺陷】** ★

---

## ★1 · ★★上一趟【已经在盘上的成果】(★派活人 04:5x 实跑核对, 直接用, 不要重做★) ★★

### ★1-A · 【最重要】22 网名 → 5 桶归属表【已写好, 就在脚手架脚本里】★

★**`state/_iss308_s8_reachability_check.py`** (★16,024 B · md5 `830f8fe381540c1864697e69cb831f39` · mtime 04:31★)
★**它的 `BUCKETS` 字典 = ISS-308 §2-A 的【22 网名 → 桶 → 根因 → 能不能在板那一趟解 → 解法/卡在谁】五字段全表, 22 条一条不缺** ★
★**每条根因都带【实测数字】(段数 / 层分布 / 零铜 / 抢路者 / 净距)** ⇒ ★**§2-A 的落桶表 = 直接从这个字典抄进判决书, 不许重新推算** ★

★**派活人 04:5x 实跑核对了 22 条根因里的段数与盘上证据文件的一致性**:
```
★两份证据文件 (/tmp 已被派活人抢救到 logs/iss308/evidence/):
  iss308_cand_layers.json  (★候选板 candidate_v76mx1L_pour 的逐网逐层铜量★)
  iss308_ms_layers.json    (★v76ms 臂链的逐网逐层铜量★)
★两份的 22 条目标网【全部覆盖】(各 136 网名) ⇒ 数字可查
★★但两份在 3 条上【不一致】⇒ ⇒ 这是你【必须处理】的一处口径问题, 见 §1-C★★
```

★**★两份证据不一致的 3 条 (★派活人 04:5x 实测★)**:
| 网名 | `iss308_cand_layers.json` | `iss308_ms_layers.json` |
|---|---|---|
| `DSI_D0_D3_N` | 52 段 (F.Cu 15 / In2.Cu 32 / In4.Cu 5) | ★**53 段 (F.Cu 19 / In2.Cu 26 / In4.Cu 8)** ★ |
| `KEY_VOL_M` | 98 段 (F.Cu 13 / In2.Cu 85) | ★**99 段 (F.Cu 13 / In2.Cu 86)** ★ |
| `LED_B` | 27 段 (F.Cu 7 / In2.Cu 20) | ★**0 段 (无铜)** ★ |

★**★上表 = 你上一趟 `BUCKETS` 里那 3 条根因【引用的是哪一份】的自证 (★派活人逐条核过★)**:
- `DSI_D0_D3_N` 根因写「N 腿 52 段 (F.Cu 15 / In2.Cu 32 / In4.Cu 5)」 ⇒ ★**引用的是 candidate** ★
- `KEY_VOL_M` 根因写「N 腿 98 段 (F.Cu 13 / In2.Cu 85)」 ⇒ ★**引用的是 candidate** ★
- `LED_B` 根因写「27 段 (F.Cu 7 / In2.Cu 20)」 ⇒ ★**引用的是 candidate** ★
⇒ ★**⇒ 你上一趟的口径是【统一用 candidate 板】(★= `state/.lastgood/candidate_v76mx1L_pour.kicad_pcb` · 22 网名的来源板, 与 `state/UNC_TARGET_MAP.md` §「11-11 05:6x 更新」同源★) ★
⇒ ★**★那就把这个口径【写进判决书】(★「本判决书所有逐网铜量数字一律取自 candidate 板」), 不许混用两份文件★ ⇒ ★并把「ms 臂链在 LED_B 上是 0 段」记为【一条差异注记】(★说明两条臂链走法不同, 判决以 candidate 为准★)** ★

### ★1-B · 已有的分析工具 + 证据 (★都在盘上, 别重写★)

```
logs/iss308/evidence/          (★派活人 04:46 从 /tmp 抢救下来的 · /tmp 会清★)
  iss308_cand_layers.json          ★候选板逐网逐层铜量 (seg / pad / vias)★
  iss308_ms_layers.json            ★v76ms 臂链逐网逐层铜量★
  iss308_cand_layers.json.layermap.json   ★层号 → 层名对照 (F.Cu=0 / In2.Cu=6 / In4.Cu=10 ...)★
  iss308_ms_layers.json.layermap.json
  iss308_live.drc.json             ★现役板 DRC 全量★
  iss308_v76ms_fresh.drc.json      ★v76ms 臂链 DRC 全量★
  iss308_readings.py               ★上一趟写的读数抽取器★
  iss308_layerprobe.py             ★上一趟写的逐层探针★
  iss308_analyze.py                ★上一趟写的对比分析★
  iss308_drc_official.log
```

★**★每个 JSON 的结构 (★派活人 04:5x 实读★, 直接照着用★)**:
```json
{ "CSI_D0_CK_N": { "seg": {"F.Cu": 30, "In2.Cu": 12}, "seg_total": 42,
                   "pad": {"F.Cu": 3, "F.Mask": 3, "F.Paste": 3}, "pad_total": 9,
                   "vias": 4 }, ... }
```
⇒ ★**`seg` = 该网在该层的铜段数 · `seg_total` = 该网总铜段数 · `pad` = 焊盘层分布 · `vias` = 过孔数** ★

★**★派活人 04:5x 实测的一行 (★用来验你抄进去的数对不对★)**:
```
python3 -c "import json; d=json.load(open('logs/iss308/evidence/iss308_cand_layers.json'));
            print(d['CSI_D0_CK_N']['seg_total'], d['CSI_D0_CK_N']['seg'])"
⇒ 42 {'F.Cu': 30, 'In2.Cu': 12}      ★与 BUCKETS 里 CSI_D0_CK_N 根因逐字一致★
```

### ★1-C · ★★一个【你必须自己查清】的口径问题 (★原任务书 §1-④ 的第一问, 上一趟没查完★) ★★

★**原任务书 §1-④ 要求查清**: 「`state/UNC_TARGET_MAP.md` 原文写『`PCB_PAIR_LAYERSEL` 目前无效但无害』 ⇒ ⇒ **『无效』这个判断【谁写的 / 哪一天写的 / 有没有实测支撑】= 本单必须查清的第一件事**」 ★
★**上一趟的 transcript 里你查了 `PCB_PAIR_LAYERSEL` 在 `state/gen_pcb_routing.py` 的实现 (★L1060~L1140 一带★), 但【结论没落进任何文件】⇒ ★**这一问【还没答完】, 你要答** ★

★**★还有一条你上一趟【没写下来】的重要发现 (★派活人从 transcript 里读出来的, 你自己确认后写进判决书★)** ★
★**`logs/iss308/evidence/` 里 `iss308_live.drc.json` 与 `iss308_v76ms_fresh.drc.json` 两份都在 ⇒ ★你可以直接对比【现役板】与【v76ms 臂链】的 unc 清单 ⇒ ★这比重新跑 DRC 快得多 (★跑一次 DRC 要 ~40 s 且写临时文件★)** ★

### ★1-D · ★★上一趟【唯一真 bug】: `check()` 抓不住「改了桶」★ (★派活人 04:5x 实跑复现★) ★★

★**上一趟 `--selftest` 的用例①【失败】, 你自己没来得及看 ⇒ ★派活人 04:5x 实跑复现了根因★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/_iss308_s8_reachability_check.py --selftest ; echo "rc=$?"
```
★**实测输出 (★派活人原样 rc★)**:
```
=== ISS-308 selftest (★反向用例★) ===
  ✘ 用例① 失败: ★改了桶居然还判绿 ⇒ 脚本是摆设★
  ✔ 用例② 「删掉 USB_CC1」 ⇒ 脚本判红 (★1 条错★)
  ✔ 用例③ 「塞一个盘上没有的网名 FAKE_NET_XYZ」 ⇒ 脚本判红 (★1 条错★)
  ✔ 用例④ 「原样不改动」 ⇒ 脚本判绿
=== selftest 结束: 1 个用例失败 ===
rc=1
```
★**★根因 (★派活人 04:5x 实跑复现★)**: ★**`check()` 只校验「桶 ∈ VALID_BUCKETS」+「根因/解法非空」+「网名集合 == 靶表」+「板 md5/mtime 未变」⇒ ⇒ 它【从不校验某条网名【应该落在哪个桶】】⇒ ⇒ 把 `CSI_D0_D2_N` 的桶从 B3 改成 B5 (★B5 也是合法桶★) ⇒ 【判绿】⇒ ⇒ 反向用例① 抓不住★** ★
★**派活人实测复现 (★原样★)**:
```python
mut = dict(BUCKETS); mut['CSI_D0_D2_N'] = ('B5',) + tuple(BUCKETS['CSI_D0_D2_N'][1:])
check(mut)   # ⇒ 返回 [] (★空 = 无错 = 判绿★) ★★这就是用例① 抓不住的原因★★
```

★**★★你要做的修法 (★本单唯一允许改的代码★)**: ★**给 `check()` 加一条【桶归属的独立权威源】⇒ 改任一条网名的桶必须判红** ★
★**★铁律 (★本项目的老教训, 不许踩★)**: ★**判据必须有【独立于被测对象的第二来源】, 否则就是摆设** ★
★**★推荐修法 (★你自选其一, 但必须让用例① 转绿★)**:
- ★**方案甲 (★推荐★)**: ★**在脚本里另存一份【桶归属的权威副本】(★例如 `BUCKET_AUTHORITY: dict[str, str]` = 22 网名 → 桶★) ⇒ `check()` 逐条比对【被测 buckets 的桶】vs【这份权威副本的桶】⇒ 不一致 ⇒ 判红** ★
  ★**★为什么推荐甲**: ★**它把「桶归属」变成【脚本自己钉住的一条可复算断言】⇒ 任何人改一个桶都会红 ⇒ 【一条命令复算】这个交付要求才真正成立** ★
- ★**方案乙**: ★**把权威归属写进【新建判决书 `HW/PCB/S8_REACHABILITY_VERDICT.md`】的落桶表 ⇒ 脚本去读那份表逐条比对 ⇒ 文档与脚本互相锁** ★
- ★**★注意 (★本项目的老坑★)**: ★**不许把「桶改成非法值」当反向用例** (★那测的是「桶名拼写」, 不是「桶归属对不对」★) ⇒ ★**用例① 必须保持「B3 → B5 这种【另一个合法桶】」的形状★** ★
★**★不许放宽任何现有判据** (★`VALID_BUCKETS` / 字段非空 / 网名集合比对 / 板 md5+mtime 四条一个都不许动★) ★

### ★1-E · ★★上一趟【时间预算】的教训 ⇒ 本单的工作方式 ★★

★**上一趟 434 秒里, 你把【几乎全部时间花在逐层探针上】⇒ ⇒ 交卷物一个都没写出来 ⇒ ⇒ 白跑** ★
★**★本单的工作方式 (★按这个顺序做, 别改★)**:
1. ★**第一步就 `write` 建交卷单骨架** (★哪怕只有 B0~B6 六个标题 + 交付物清单, 3 分钟内落盘★) ⇒ ★**先把「交卷物存在」这件事变成事实, 再去填内容** ★
2. ★**第二步把 `BUCKETS` 22 条抄进【新建判决书 `HW/PCB/S8_REACHABILITY_VERDICT.md`】** (★抄, 不是重算★)
3. ★**第三步补 §2-B (N 个字母) + §2-C (技术活清单) + §1-④ 的 `PCB_PAIR_LAYERSEL` 查清结论** ★
4. ★**第四步修 `check()` (★§1-D★) ⇒ 跑 `--selftest` 必须 rc=0** ★
5. ★**第五步写交卷单 + 跑闸 + 写分片** ★
★**★每落一件交付物, 立刻把它的 rc 追加进交卷单 (★别攒到最后一起写★)** ★
★**★单条 `exec` ≤ ~120 秒** ★ · ★**长活一律 `nohup ... > logs/iss308/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) ★ · ★**每 10 分钟至少一次写盘** ★

---

## ★2 · 本单要交的三件东西 (★唯一目标★)

★**原任务书 §2-A / §2-B / §2-C 的内容要求【一字不改地继续有效】, 下面是给续做人的精简版★**:

### ★2-A · 【判决 1】残余 22 网名 → 5 桶, 逐条落桶 (★主交付★)
★**每个网名一行, 必须有**: 网名 · 桶 · 根因 (一句话 + 依据行号/坐标/实测数) · 能不能在「板那一趟」这一趟里解 · 若能: 解法一句话 (env 键 / 落铜前拦 / 落位坐标 / 老板字母) · 若不能: 卡在谁 ★
★**★落桶表【已经在 `BUCKETS` 里写好了】⇒ ★你只需抄进判决书 + 每条补上「实测出处 (★命令 + 文件 + 字段★)」★** ★

| 桶 | 判据 (原任务书 §2-A 逐字) |
|---|---|
| ★**B1 · 差老板字母** ★ | 死因是 `BAT_DET` 终点 / ESD 钉位 / `Q_PG.3` 极性 / `D_LED_G` 位置 / 板形层数 ⇒ 引用作业包 §6.2 的登记行 |
| ★**B2 · GND 卡死 (铜皮 / 下拉孔)** ★ | 净距 < 0.20 mm 且抢路者是 GND ⇒ ★**解法只许是「落铜前拦」: GND 铜皮局部 keepout / 缩形 / 挪下拉孔 ⇒ 不许在产物上擦** ★ |
| ★**B3 · 差分 N 腿互掐 (层分配)** ★ | P 腿有铜 / N 腿无铜 或 N 腿净距被 P 腿压 ⇒ ★**必须实测【N 腿的层占比 vs P 腿的层占比】(★从最佳候选板逐段读层★)** ★ |
| ★**B4 · 让路闸靶子 (普通信号网互掐)** ★ | 抢路者非 GND 且 k ≤ 3 ⇒ 给 env 配方 (`PCB_YIELD_VICTIMS` / `PCB_PRIORITY_NETS` / `PCB_PAIR_BEFORE_PWR` 等) |
| ★**B5 · 其它 (逐条单列)** ★ | 不许塞进上面四桶 ⇒ 每条自己给判据 |

★**★已核出的桶分布 (★派活人 04:5x 实跑 `BUCKETS` 得★)**: ★**B1: 2 条 · B2: 1 条 · B3: 12 条 · B4: 7 条 · B5: 0 条** ★
★(★B5 = 0 是实测结果, 不是漏填 ★) ★

### ★2-B · 【判决 2】老板还差 N 个字母 (★N 必须是具体数字★)
★**照 ISS-306 (sw-lead) 已 verified 的口径写**: ★**① N = 几** · ★**② 每个字母卡在哪一步 (S4 / S5 / S8) + 对应哪条残余网名** · ★**③ 不拍的后果 (一句话, 要具体)** ★
★**④ 若 N = 0 ⇒ 那就明写 N = 0, 不许为了凑数硬找卡点** ★
★**★提示 (★派活人 04:5x 实读 `BUCKETS` 得到的线索★)**: ★**B1 桶那 2 条 (`CARRIER_BOARD_EN` / `SPI_CSn_BOOT`) 的解法都写着「卡在老板 P7 (C1/C2/C3/C4)」⇒ ⇒ N 至少含 P7 这一个字母 ⇒ ★但【N 的最终数字你自己定】, 逐条给依据, 不许拍脑袋★** ★

### ★2-C · 【判决 3】现在就能做的技术活清单 (★零等老板★)
★**逐条给**: 技术活内容 · 需要哪个 env 键 (逐字) · 落铜前拦 / 落位增补的具体改法 (坐标 / 净距) · 预期能解掉哪几个残余网名 · **预估代价 (臂跑多久 / 要不要改路由器源码 / 要不要改板)** ★
★**★凡是要改板 / 要改网表真源的 ⇒ 不许写进「现在就能做」⇒ 归到 2-B 的老板字母桶** ★
★**★提示**: ★**B3 桶那 12 条的解法【已经逐条写好 env 键了】(★`PCB_PAIR_LAYERSEL` / 成对走廊规划 / 起步格 halo 放宽 / 局部 keepout★) ⇒ ★§2-C 基本是【抄 + 补代价估算】★** ★

---

## ★3 · 交付物 (3 件) (★新建 ⇒ 不许改既有文件正文★)

1. ★**`HW/PCB/S8_REACHABILITY_VERDICT.md`** (★新建 · 判决书正文 ★) ⇒ ★**内容 = §2-A 的落桶表 + §2-B 的 N 个字母 + §2-C 的技术活清单 + 每条数字的实测出处 (★命令 + 文件 + 字段★)** ★
   ★**★必须含一条【口径声明】**: ★**「本判决书所有逐网铜量数字一律取自 `candidate_v76mx1L_pour` 板 ⇒ 证据文件 `logs/iss308/evidence/iss308_cand_layers.json`」+ ★「与 `iss308_ms_layers.json` (v76ms 臂链) 的 3 条差异注记」★** ★
2. ★**`HANDOFF/2026-11-18_hw-lead_ISS308_S8可达性判决书.md`** (★新建 · 交卷单 ★) ⇒ ★**必须按【标准验收块 B1~B6】写** (★`state/gate_check.py` 的 `REQUIRED_BLOCKS` 口径★) ⇒ ★**Q1 必须 18/18** ★ ★ ⇒ ★**占位符判据 = `grep -cE "🔄|待填"` 必须 = 0** (★`state/check_report_placeholders.py` 抓不到这种形态, 这是 main 实测坑★) ★
3. ★**`state/_iss308_s8_reachability_check.py`** (★**已存在** ★★你要改它 ★) ⇒ ★**修完 §1-D 的缺陷后: `python3 state/_iss308_s8_reachability_check.py` ⇒ rc=0** · ★**`python3 state/_iss308_s8_reachability_check.py --selftest` ⇒ rc=0** (★★用例① 必须转绿★★)

★**★分片纪律★**: ★**只写 `state/fragments/hw.yaml`** (★用 `python3 state/frag_write.py --agent hw-lead ...` 原子写, ★**禁止 open(p,"w")★**) ⇒ ★**claim / answer / artifact 各至少一条** ⇒ ★**`grep -c iss308` 必须 ≥ 5** ★
★**★不许写**: `state/fragments/mech.yaml` / `sw.yaml` / `pm.yaml` / 任何别人的分片 ★

---

## ★4 · 验收命令 (★全部【实测存在】, 逐条给期望 rc★)

★**★工作目录 = `/home/yuewuya/.openclaw/workspace/projects/smart_glasses`★** ★

```bash
# ① 现役板底数 (零写板自证)
bash state/pcbnew_py.sh state/check_pcb_drc.py HW/PCB/demo_mainboard.kicad_pcb ; echo "rc=$?"
# ★期望 rc=0 · C4 unconnected items = 45 · C3 DRC violations = 0 · C6 Gerber 32 个★

# ② 名单制晋级闸自测 (★判据本体不许改★)
python3 state/compare_arm_official.py --self-test ; echo "rc=$?"
# ★期望 rc=0 (★派活人 04:5x 实跑: ALL TESTS PASS★)★

# ③ 本单第 3 件 (★修完之后★)
python3 state/_iss308_s8_reachability_check.py ; echo "rc=$?"
# ★期望 rc=0 (★派活人 04:5x 实跑: 现在已经 rc=0, 别改坏★)★
python3 state/_iss308_s8_reachability_check.py --selftest ; echo "rc=$?"
# ★★期望 rc=0 (★派活人 04:5x 实跑: 现在是 rc=1 ★用例① 失败★ ⇒ ★你必须修绿★)★★

# ④ 交卷前必跑 (★三条的原始输出都要贴进交卷单 B4★)
python3 state/merge.py ; echo "rc=$?"          # ★期望 rc=0★
python3 state/gate_check.py ; echo "rc=$?"      # ★期望 rc=0 · Q1 18/18 · Q7 9/9★
python3 state/issue_check.py ; echo "rc=$?"    # ★期望 rc=0★
```

★**★板零写板双证 (★交卷单 B4 必须贴这两行★)**:
```bash
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
# ★期望: 611b869e13518c3c023fb178f91a0075 · 2026-11-06 07:07:17 (一字未动)★
```
★**★落表四件也要贴 md5 (★派活人 04:5x 实跑的现值★)**:
```bash
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/SCHEMATIC_LANDING_V1_LANDED.md
# ★期望: 6aee500e60ba0732f83a9cf557ba90ab / 9174309df1ec9411ac8e8d9e80ee386a /
#        5b9993992405904a60ac96a020b375d8 / (台账 mtime 2026-11-17 12:30:23)★
```

★**★不许新跑布线臂 (★本单是【分析 / 判决】单, 不是开臂单·理由见原任务书 §1-⑤★)** ⇒ ★**所有数字必须来自【已在盘上的东西】: 现役板读数 / `state/.lastgood/` 的候选板 / `state/ARM_LEDGER_2026-11-10.md` / `state/UNC_TARGET_MAP.md` / `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/LAYOUT_FIX_SPEC.md` / `HW/PCB/FSIN_OUT_ROOTCAUSE.md` / `HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md` / `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` / `HW/PCB/BOARD_FRAME_CALIBER.md` / ★**`logs/iss308/evidence/` 的两份逐层 JSON**★** ★
★**★若某个数字在盘上找不到 ⇒ 不许估 ⇒ 标 [0数据] + 写清「要拿到它得跑什么 / 代价多少」★** ★

---

## ★5 · 边界 (★逐条自证, 写进交卷单 B6★)

| 边界 | 怎么自证 |
|---|---|
| ★**零写板** ★ | ★板 md5 + mtime 两条都贴 (见 §4★)★ |
| ★**零落表** ★ | ★`HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` / `HW/SCHEMATIC_LANDING_V1_LANDED.md` 一个字节没动 (★md5 对回 §4 的现值★)★ |
| ★**零改闸 / 零改判据脚本** ★ | ★`state/compare_arm_official.py` / `state/check_pcb_drc.py` / `state/gate_check.py` / `HW/check_onepass_commit_order.py` / `HW/check_workpack_state_values.py` 一个字节没动★ ★★**唯一例外 = `state/_iss308_s8_reachability_check.py` (★本单第 3 件交付物, 本来就是本单自己建的, 修它是你的活★)★** ★ |
| ★**零改既有文档正文** ★ | ★本单只【新建】两份文档 + 【只改】自己那个脚手架脚本 ⇒ 作业包 / 清单页 / `state/UNC_TARGET_MAP.md` / 臂总账 一律不碰 (★要追加就追加到你自己的新文件里★)★ |
| ★**零外发** ★ | ★没发任何邮件 / 询价 / 问询 / 采购 / 原厂问询 ⇒ 本单不依赖任何外部回复 ⇒ 【查不到就写 [0数据] + 降级方案】★ |
| ★**不替老板拍板** ★ | ★§2-B 只给 N + 卡点 + 后果, 不给决策码★ |
| ★**不自签 issue_log** ★ | ★不写 `state/issue_log.yaml` (★验收由 main 签★)★ |
| ★**不改别人分片** ★ | ★只写 `state/fragments/hw.yaml`★ |

---

## ★6 · 交卷格式 (★照 ISS-307 那份交卷单的形状写★)

★**交卷单 = `HANDOFF/2026-11-18_hw-lead_ISS308_S8可达性判决书.md`**, 必须含:
★**B0** 结论摘要 (★三行: S8 可行 / 需 N 处布局修正后可 / 需老板 P7 选 C4 —— ★三选一, 必须选一个, 不许骑墙★) ★
★**B1** 验收标准自评 (★逐条对 §4 的期望 rc, 贴原始输出★) ★
★**B2** 证据分级 (★`[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]` 逐条标★) ★
★**B3** 接口取值声明 (★本单声明的网名清单 / 落位坐标 / env 键名 —— 这些是别人要照抄的东西, 必须逐字给★) ★
★**B4** 闸复跑原始输出 (★§4 那几条 + 板 md5/mtime 双证 + 落表四件 md5★) ★
★**B5** 未决项与卡点 (★每条写: 卡在谁 / 要什么 / 不做的后果 ★**含本单自己没做完的部分 (★时间预算不够就写这里, 不许装完成★)★) ★
★**B6** 边界自证 (★§5 那张表逐行★) ★

★**★交卷纪律★**: ★**先交卷, 再完美** ★ · ★**占位符 0 (`grep -cE "🔄|待填"` = 0)** ★ · ★**Q1 必须 18/18** ★

---

## ★7 · 给续做人的 5 条提醒 (★派活人 04:5x 实跑总结★)

1. ★**★别重做分析★** —— `BUCKETS` 22 条已写好, `logs/iss308/evidence/` 的证据已抢救好 ⇒ ★**你的活是【抄 + 补文档 + 修一个判据缺陷 + 写分片】** ★
2. ★**★先建骨架★** —— 上一趟把 434 秒全花在探针上, 交卷物 0 件 ⇒ ★**第一件事就是 `write` 建交卷单** ★
3. ★**★判据要有第二来源★** —— `check()` 现在抓不住「改桶」⇒ ★**给桶归属加一份独立权威副本, 别去测「桶名拼写」** ★
4. ★**★3 条数字差异要交代★** —— `DSI_D0_D3_N` / `KEY_VOL_M` / `LED_B` 在两份证据里不一样 ⇒ ★**统一用 candidate + 写差异注记** ★
5. ★**★别替老板拍板 + 零外发★** —— §2-B 只给 N 和后果; ★**本单不许发任何邮件/询价/问询 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有"批一句可以发"这个选项** ★
