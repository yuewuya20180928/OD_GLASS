# ISS-317 · hw-lead · ★★cont2 续做说明★★ (★僵尸 fixing 重派 · 不是从零重做★)

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: hw-lead · ★**verify_by**: main · ★**单号**: ISS-317
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**派活时刻**: ★**2026-11-18 10:4x** ★
> ★**性质**: 内部活 · 纯分析 / 作业包 / 判据设计类 (HW 侧) · 零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 沙盒只写 `tmp/` · 零外发 · 不替老板拍板 · 不自签 issue_log

---

## ★0 · main 10:4x 本机实读的事实 (★你上一趟【已落盘的东西】· 别重做★)

★**子会话 `agent:hw-lead:subagent:189e7a8b-...` 09:17:03 起 · 09:24:28 死 (status=failed · errorMessage="This operation was aborted")** ⇒ **死因 = 父 cron run 结束把子会话连带 abort (不是你的错)** ⇒ ★**本单是续做, 不是从零重做** ★

### ★**已经在盘上的 (★直接用, 不要重跑★)** ★

| 落点 | 状态 |
|---|---|
| `logs/iss317/rename_list_raw.txt` (58,695 B) | ★**218 行逐条改名对照表 (旧ref 脚表侧/板侧/原理图侧 → 新ref + 改哪个真源 + 动/不动 + 预期读数 + 依赖顺序)★ 已机器生成** ★ |
| `logs/iss317/iss317_gen_rename_list.py` (18,666 B) | ★**生成器 (自带口径单源逐字比对不一致即 abort)★** ★ |
| `logs/iss317/iss317_sb_make.py` / `iss317_sb_run.sh` / `iss317_sb_singleinject.py` | ★**沙盒造网表 + 跑判据 + 单注入口★** ★ |
| `logs/iss317/03a_sb_make_raw.txt` / `03b_sb_run_raw.txt` / `03c_singleinject_raw.txt` | ★**★场景矩阵 A0~A5 实跑读数 (含 NC 白名单三选项 甲/乙/丙 + 丙的反向用例)★** ★ |
| `logs/iss317/01_c1_baseline_full.txt` / `02_bom_export_raw.txt` / `07_bom_qmark_raw.txt` | ★**C1 现状基线 / BOM 导出 / BOM 问号行数** ★ |
| `HANDOFF/2026-11-18_hw-lead_ISS317_S1位号改名可执行清单.md` (9,341 B) | ★**★交卷页 B0~B6 已填 (口径/结论/自评/证据分级/接口声明/未决项/复现命令全在)★ ★** ★ |
| `state/dispatch_briefs/ISS-317_hw_s1_three_side_rename_and_nc_whitelist.md` + `_cont1.md` | ★**原任务书 + cont1 说明 (★原文一个字不许删★)★** ★ |

### ★**还没落盘的 (★这就是本趟要干的活★)** ★

| # | 缺口 | 判定 |
|---|---|---|
| 1 | ★**★交付物正文还是骨架★** ★ `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` (813 B) 的 §0~§6 **七节全是「(施工中)」** | ★**★本趟第一件事: 把这七节写实 (数据全部从上面 `rename_list_raw.txt` / `03b_sb_run_raw.txt` 取, 不许手抄·不许推算)★** ★ |
| 2 | ★**交卷页末尾的 ★附 (155 行往后) 只剩一句「各节在交卷过程中逐条回填」** ★ ⇒ §1/§2/§3/§4 的正文没落纸 | ★**把 §1~§4 正文回填进交卷页 (或在交付物里写全 + 交卷页指路)★** ★ |
| 3 | ★**交卷页 B2 自评表引用的 7 个日志不存在**: `04_nc_options_raw.txt` · `05_dmp3098l_official.txt` · `06_esd_official.txt` · `08_zero_write_proof.txt` · `09_merge_gate_output.txt` · `10_placeholder_scan.txt` · `11_frag_write_output.txt` | ★**要么补跑落盘, 要么把 B2 的引用改成真实存在的文件 (★不许留悬空引用★)★** ★ |
| 4 | ★**分片一个字没写**: `state/fragments/hw.yaml` 里 `ISS-317` 命中 **0** 次 (★main 实测★) ⇒ artifacts/needs/claims 全缺 | ★**必须写 (经 `state/frag_write.py --agent hw-lead` 原子写, 禁止 `open(p,"w")`)★** ★ |

---

## ★1 · 本趟的最小可接受交卷线 (★时间不够就交到这个程度, 但必须交★)

1. ★**`HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` §1 = 218 行逐条改名对照表 (★从 `rename_list_raw.txt` 机器搬, 一行不许漏·一行不许手抄★)★**
2. ★**§2 = NC 白名单三选项 (甲/乙/丙) 的 C1/C2/C3 实跑读数 (★从 `03b_sb_run_raw.txt` 抄逐字读数, 不许推算★)★**
3. ★**§3 = BOM 证据回填兜底的机器可判判据写法 (★含至少一条反向用例★)★**
4. ★**§4 = ISS-314 五条未验 (U-2 DMP3098L / U-3 ESD 器件 / U-4 BOM 问号行数 / U-5 落表排期) 的补齐结果 (★官网自查 ⇒ 标 [官网]; 查不到 ⇒ 标 [0数据] + 降级方案·不许挂外部依赖★)★**
5. ★**§5 证据分级 (★[官网]/[实测]/[推算]/[0数据] 四档标齐★) + §6 文件清单**
6. ★**交卷页 B0~B6 齐全 + 附 §1~§4 正文 + 分片写完 + `logs/iss317/` 补齐引用到的日志**

---

## ★2 · ★★纪律 (★本轮针对实测死亡模式的硬约束★★) ★★

- ★**先落纸 —— 每完成一条就把结论回填进交卷页, 宁可交半成品页, 不许一页纸都不落** ★ (★上一趟就是因为「全在脑子里」而一死全丢★)
- ★**零写板**: 板 `HW/PCB/demo_mainboard.kicad_pcb` md5 必须 = `611b869e13518c3c023fb178f91a0075` + mtime = `2026-11-06 07:07:17.362193413` (★交卷前后逐字节相同★)
- ★**零落表**: 网表 / 脚表 / BOM 的 md5 不许动
- ★**零改闸**: `state/gate_check.py` / 任何 `check_*.py` 的判据方向一律不许改
- ★**沙盒只写 `tmp/`** (★不许落 `/tmp`: 本机 `/tmp` 带 usrquota 且配额已满 ⇒ 假红★)
- ★**零外发**: ★**不许发任何邮件/询价/问询/采购 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料) ⇒ 缺口一律【自己网上查】+ 标证据等级 + 查不到就写降级方案 ⇒ 没有「批一句可以发」这个选项** ★
- ★**证据分级** [官网]/[实测]/[媒体]/[推算]/[0数据] 必须标
- ★**不许替老板拍板** · ★**不许自签 issue_log** (★status/verify_result 留给 main★)
- ★**不许改网表真源** (★网表只作为「改名宇宙」的只读输入★)

---

## ★3 · 交卷前必跑 (★原样贴进回复★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py && python3 state/gate_check.py     # rc 必须 0 · Q1 必须 18/18
md5sum HW/PCB/demo_mainboard.kicad_pcb                     # 必须 = 611b869e13518c3c023fb178f91a0075
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb               # 必须 = 2026-11-06 07:07:17.362193413
grep -cE "🔄|待填|PLACEHOLDER|施工中" HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md   # 必须 = 0
grep -c "ISS-317" state/fragments/hw.yaml                  # 必须 >= 1 (★分片写了没有★)
```
