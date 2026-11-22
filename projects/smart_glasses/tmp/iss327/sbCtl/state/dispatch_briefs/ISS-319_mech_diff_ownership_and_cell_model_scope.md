# ISS-319 · mech-lead 任务书 —— ★★【「板只改一次」那一趟的 MECH 侧: ①把 ISS-316 的 26 条差集【逐条落到 owner + 落表批次】 ②电芯型号订正的【真实影响面是 47 行 / 19 个活文件, 不是 8 行】(★ISS-316 只点了 MECH_BUDGET 的 8 行★)★★

> ★**派活人**: 项目总工 (main / moli) · ★**owner**: mech-lead · ★**verify_by**: main · ★**单号**: ISS-319
> ★**job**: cron `fb67af40` (ARS45 队列自动派活) · ★**性质**: ★**内部活 · 纯分析 / 作业包 / 对账类 (MECH 侧)** ★
> ★**边界 (硬)**: ★**零写板 · 零落表 · 零重生成 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log** ★

---

## ★0 · 本单为什么存在 (★main 08:1x 本机实读, 不抄任何 agent 报告★) ★

★**ISS-316 (verified) 交卷页 §B5-3 自己写下了「留给下一轮的三个动作」, 其中第 3 条是**: ★**「§4 的 26 条差集逐条指定 owner ⇒ ★**不然下一轮还是同一张差集★」** ⇒ ★**本单第 1 件就是接住它** ★

★**★而第 2 件是 main 本轮新查出来的 (★ISS-316 漏掉的★)★**:
★**ISS-316 §5-1 说电芯型号订正「影响行 8 行 (★本机实读 L160 / L332 / L340 / L342 / L358 / L775 / L852 / L867★)」⇒ ★**但那是【只数了 `MECH/MECH_BUDGET.md` 一个文件】★ ⇒ ★**main 08:1x 全仓实跑 `grep -rn` (★排除 `tmp/` / `.trash/` / `state/.bak_*`★) 实测: 活文件里共 **47 行**, 分布在 **19 个文件**上★** ★
★**★更要紧的是: `MECH/MECH_BUDGET.md` 自己就有 **9 行**命中 (★ISS-316 给了 8 行, ★**漏了 L1177**★)⇒ ★**更要紧的是: 有 3 处命中落在【脚本】里 (★不是文档★) ⇒ 改文档不改脚本 ⇒ 脚本会继续按旧型号算★** ★**

★**★所以: 「电芯型号写错 ⇒ 到货厚 6.40mm ⇒ 装不进 7.30mm 镜脚 ⇒ H 链最坏 −1.10mm」这笔账, ★**它真正的成本不在 MECH_BUDGET 的 8 行, 而在 19 个文件 / 47 行 / 3 个脚本★ ⇒ ★**ISS-316 给的改法清单【不够】⇒ 不补齐, 采购口径就还是会买错★** ★

---

## ★1 · 交两件 (★每件都必须有机器可判的验收★) ★

### ★★★ 第一件 · 【26 条差集 → 逐条 owner + 落表批次 (★ISS-316 §B5-3 第 3 条的正面回答★)】★★★

★**ISS-316 §4 已经把 26 条差集列出来了 (★D-1 7 条 · D-2 9 条 · D-3 6 条 · D-4 4 条★) ⇒ ★**本单不许重列差集, 只许给它【补三列】** ★
★| 要补的列 | 内容 |
|---|---|
| ★**owner** ★ | ★**这条差集归谁 (★hw-lead / sw-lead / mech-lead / main / boss★) ⇒ ★**归 boss 的必须写出「它要回答的那一句话」★★** ★ |
| ★**落表批次** ★ | ★**这条必须跟板那一趟【同批】改 (★背靠背·不许拆两趟★) / 可以【单独批】改 / 【已经作废·留证不改】★ ⇒ ★**判据: 改它会不会动板 md5? 动 ⇒ 必须同批★** ★ |
| ★**改完的验收判据** ★ | ★**逐条给「改完之后跑哪条命令 ⇒ 期望看到什么」** ★ |

★**★硬约束★**:
- ★**★26 条一条都不许漏 ⇒ 逐条表, 26 行★ (★ISS-316 的分类注要照抄: D-1-2 / D-1-4 归【过期行】不归【两边打架】, ★**但过期行也要在账上**★) ★
- ★**★不许替 boss / main 拍板★ ⇒ 归 boss 的那几条, ★**只写「它要回答的那一句话 + 不回答的后果」★★ ⇒ 不写「建议答案」 (★除非是老板要的那一条★) ★
- ★**★不许改 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` 或任何 HW 文件★ ⇒ ★**MECH 侧该抄的那部分, 出成【可直接抄的逐字段落】交 main, 不许自己抄进去★** ★

### ★★★ 第二件 · 【电芯型号订正的真实影响面 (★47 行 / 19 个活文件 / 3 个脚本★)】★★★

★**要交一份【完整改法清单】**, 逐条给:
★| 字段 | 内容 |
|---|---|
| ★**文件 + 行号** ★ | ★**逐条列, 一个都不许漏 (★★包括脚本里的那一行★)★** ★ |
| ★**这行现在写的是什么** ★ | ★**逐字摘出来 (★不许概括★)** ★ |
| ★**应该改成什么** ★ | ★**逐字改法 (★只换型号名, 尺寸一个字不动 ⇒ 几何与重量结论零变化★)** ★ |
| ★**这行是【口径行】还是【历史留证行】** ★ | ★**★口径行 = 会被后人当现状读的 (★要改★) · 历史留证行 = 记录当时结论的 (★★不改, 改了就是篡改历史★)★ ⇒ 这一列是本件的核心 ⇒ 判错的代价 = 篡改留证链** ★ |
| ★**改完会不会连带影响别的东西** ★ | ★**特别是那 3 个脚本 (★脚本里改注释和改逻辑是两回事 ⇒ 脚本只许改注释里的型号名, 逻辑一个字不许动★) ⇒ 逐条说清楚** ★ |

★**★必须额外做的一步 (★main 08:1x 实测出来的那颗雷★)★**:
> ★**`MECH/service_port_check.py` 的 `BASE["cell_thk"] = 4.60` (★L51, 注释写「§1.6.1 Renata ICP582035PR-01 (315 档)」★) ⇒ ★**这个 4.60 是【ICP422339PR 的厚度】, 不是 ICP582035PR-01 的 (★后者实厚 6.4mm★) ⇒ ★**也就是说: 脚本算的几何【一直是对的】, 错的只是它引用的型号名 ⇒ ★**改型号名时, 脚本里的 4.60 / 23.50 / 40.50 三个数【一个字都不许动】★ ⇒ 你必须逐条确认这一点并写进清单 (★★不许只说「只换名字」, 要逐个脚本说明哪个常量是哪个型号的、为什么不能动★)★** ★
> ★**★同一条纪律适用于 `MECH/fit_check.py` (★L69 `cell_thk: 4.60★) 与 `MECH/fit_check_v3_30mm.py` (★L55 同型★) 与 `MECH/print/gen_print_pack_revb.py` (★L99 `batt_thk: (4.60, "mm", "MECH_BUDGET §1.6.1 Renata ICP582035PR-01 厚", "[官网]")★) ⇒ ★**这 4 个脚本是「打印包/校核链」的输入 ⇒ ★**改它们的注释不許改它们的数, 并且要说明「打印包重出时会带上新型号名」这一条 ⇒ 不然打印出来的那张清单还是旧型号⇒ 采购照样买错**★ ★**

★**★硬约束★**:
- ★**★零改既有文档正文 (★`MECH/MECH_BUDGET.md` / `MECH/PROTOTYPE_PLAN.md` / `MECH/RELIABILITY_TEST_PLAN.md` / `MECH/STRUCT_REVIEW_ISS065.md` / `MECH/CLEARANCE_FIX.md` / `MECH/SOC_CARRIER_EVAL.md` / `MECH/SERVICE_PORT_ISS092.md` / `MECH/BOARD_WIDTH_15MM.md` 一律只读★) ★**
- ★**★零改脚本 (★`MECH/service_port_check.py` / `MECH/fit_check.py` / `MECH/fit_check_v3_30mm.py` / `MECH/verify_budget.py` / `MECH/iss065_check.py` / `MECH/carrier_eval.py` / `MECH/board_width_15mm_check.py` / `MECH/print/gen_print_pack_revb.py` 一律只读★) ★**
- ★**★零跑生成器 / 零重生成打印包 (★`MECH/print/gen_print_pack_revb.py` 不许跑·`MECH/print/verify_pack_revb.py` 不许跑★) ★**
- ★**★本单只交【逐字改法清单】, 不落一个字★** ★

---

## ★2 · 交卷物 (★3 件, 一个都不能少★) ★

1. ★**新建 `MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md`** (★§0 口径与边界自证 · §1 26 条差集 × owner × 落表批次 × 验收判据 (★26 行一条不少★) · §2 电芯型号 47 行 / 19 文件逐条改法 + 口径行/留证行分类 · §3 四个脚本的常量归属说明 · §4 证据分级 · §5 文件清单★) ★
2. ★**新建 `HANDOFF/2026-11-18_mech-lead_ISS319_差集归属与电芯订正影响面.md`** (★B0~B6 齐全 · ★**占位符 0** · ★**必含: 26 行表 + 47 行表 + 给 main 的 need 两行 + 零写板双证★) ★
3. ★**新建 `logs/iss319/`** (★47 行全量扫描原始输出 (★脚本自算, 非手抄★) · ★26 条差集的逐条归属原始输出 · ★四个脚本的常量归属核对原始输出 · ★md5 前后对照 · ★占位符扫描结果★) ★ + ★**改 `state/fragments/mech.yaml`** (★必须用 `python3 state/frag_write.py --agent mech-lead` 原子写★ ⇒ ★**禁止 `open(p,"w")`**★ ⇒ ★**只写自己那一份, `hw.yaml`/`sw.yaml`/`pm.yaml` 一个字节不许碰**★) ★

---

## ★3 · 交卷前必跑 (★输出原样贴进回复★) ★

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss319_tmp          # ★本机 /tmp 是带 usrquota 的 tmpfs, 配额已满 ⇒ 别写 /tmp★
mkdir -p "$TMPDIR"

# ---- ① 电芯型号全量扫描 (★自己写脚本, 排除 tmp/.trash/state 备份, 输出留档★) ----
grep -rn "ICP582035PR-01" MECH/ HW/ SW/ --include="*.py" --include="*.md" \
  | grep -v "/tmp/\|\.trash/\|\.bak_" | tee logs/iss319/cell_model_scan_raw.txt
echo "命中行数 = $(wc -l < logs/iss319/cell_model_scan_raw.txt)"
echo "命中文件数 = $(awk -F: '{print $1}' logs/iss319/cell_model_scan_raw.txt | sort -u | wc -l)"

# ---- ② MECH 侧 7 道闸 (★改完一个都不许红★) ----
for g in MECH/board_frame_feasibility.py MECH/check_onepass_mech_sync.py \
         MECH/check_onepass_struct_crosscheck.py MECH/check_onepass_mech_release.py \
         MECH/check_board_frame_coords.py MECH/check_mech_verdict_freshness.py \
         MECH/service_port_check.py ; do
  printf "%-52s " "$g"; python3 "$g" >/dev/null 2>&1; echo "rc=$?"
done

# ---- ③ 门禁链 (★rc 必须 0 · Q1 必须 18/18★) ----
python3 state/merge.py && python3 state/gate_check.py

# ---- ④ 零写板 / 零落表 / 零改脚本 双证 ----
md5sum HW/PCB/demo_mainboard.kicad_pcb MECH/service_port_check.py MECH/fit_check.py \
       MECH/fit_check_v3_30mm.py MECH/print/gen_print_pack_revb.py \
       MECH/MECH_BUDGET.md HW/netlist_v1.csv HW/BOM_v1.csv
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb

# ---- ⑤ 占位符扫描 (★必须 0★) ----
grep -cE "🔄|待填|PLACEHOLDER" MECH/ONETRIP_MECH_DIFF_OWNERSHIP.md \
  "HANDOFF/2026-11-18_mech-lead_ISS319_差集归属与电芯订正影响面.md"
```

★**★交卷页必须贴: ① 26 行表 (一条不少) ② 47 行表 + 文件数 (★与 main 08:1x 实测的 47/19 对齐, 对不上就说清差在哪★) ③ 四个脚本的常量归属说明 ④ 零写板双证 ⑤ 给 main 的 need 两行★**

---

## ★4 · 硬边界 (★违反就是不合格★) ★

★**零写板** · ★**零落表** (★网表 / 脚表 / BOM / 落表台账一个字节不许动★) · ★**零重生成** (★不许跑 `MECH/print/gen_print_pack_revb.py` / `MECH/print/verify_pack_revb.py` / 任何生成器★) · ★**零改闸** (★`MECH/service_port_check.py` / `MECH/board_frame_feasibility.py` 一律只读★) · ★**零改既有文档正文** · ★**零改脚本** (★本单只交逐字改法, 不落一个字★) · ★**零改 HW 域文件** (★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` / `HW/PCB/ONETRIP_REISSUE_MANIFEST.md` 只读 ⇒ ★**要抄进 HW 作业包的那部分, 出成逐字段落交 main★) ★**零外发** (★不发邮件 / 不询价 / 不问询 / 不采购 ⇒ ★**外部依赖一律【自己网上查】+ 标证据等级 `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` + ★**查不到就写降级方案 (必须项)**★ ⇒ ★**没有「等老板批一句可以发」这个选项**★ ⇒ ★**型号规格一律自己上 renata.com 官网查, 不许写「等原厂回信」★) · ★**不替老板拍板** (★电芯采购型号是 boss 的桶★ ⇒ 只交「买错会怎样」+ 改法, 不替他选) · ★**不自签 issue_log** · ★**只写自己那一份分片** ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

---

## ★5 · 给 main 的 need (★交卷页必含两行: need key + 一句话问法 + 不拍的后果★) ★

★**建议 need key (★两个, 一个都不能少★)**:
- ★**`iss316_mech_diff_ownership`** ★ | ★**问法**: ★**「26 条差集里, D-1-1 的归属表漏记的 18 件归哪个 agent? D-3-1 / D-3-2 (等 hw 的网表/原理图结果) 要不要等? (★本单已逐条给出建议 owner + 落表批次 + 验收判据, 请裁归属口径★)」** ★ | ★**不拍的后果**: ★**下一轮还是同一张 26 条差集 ⇒ 板那一趟照旧会被这 26 条咬 ⇒ 板改第二次 (2-4 周 + ¥4-8K)★** ★
- ★**`iss319_cell_model_rename_scope`** ★ | ★**问法**: ★**「电芯型号订正 (ICP582035PR-01 → ICP422339PR) 按 47 行 / 19 个文件一起改, 还是只改口径行 (★历史留证行不动·留给 main 拍★)? 以及打印包 (`gen_print_pack_revb.py` / `MEASURE_CHECKLIST.md`) 要不要跟板那一趟同批重出?」** ★ | ★**不拍的后果**: ★**① 采购单照现型号买 ⇒ 到货厚 6.40mm (不是 4.60) ⇒ 装不进 7.30mm 镜脚 ⇒ H 链最坏 −1.10mm ⇒ ★**这笔比文档订正本身更贵**★ ② 只改 MECH_BUDGET 不改打印包 ⇒ 打印出来的那张测量清单还是旧型号 ⇒ 采购照样买错 ③ 改了留证行 ⇒ 篡改历史结论链** ★

---

## ★6 · 纪律 (★这项目的老教训★) ★

★**交卷单第一件事就是 `write` 建骨架 (★哪怕只写 3 行标题 + 交付物清单★)** ★ · ★**长任务一律 `nohup ... > logs/iss319/x.log 2>&1 &` + 短轮询 (★前台长 exec = 被掐的头号原因★)** ★ · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★
