# ISS-326 · mech-lead · ★★【cont5 续做 · ★★第一动作 = 写 (不许先读)★★】★★

> ★**第五次续做** ★ · ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: 2026-11-18 17:08 (Asia/Shanghai) · ★**job**: cron `fb67af40` (ARS45 队列自动派活)
> ★**owner**: mech-lead (结构总工) · ★**verify_by**: main · ★**单号**: ISS-326 (★**status 保持 fixing**★) · ★**零外发**

---

## ★★★【★★① ★★main 17:0x 实读: cont4 一个字节都没留下 (★★6m28s 就被 abort★)★★】★★★

★**★cont4 (16:59:47→17:06:14) 死于 `This operation was aborted`, 最后一句 = "Now let me run the required self-verification commands to capture actual outputs for B6." ⇒ ★**它读了 6 分钟, 一个字节都没写** ★ ★
★**★⇒ ⇒ 上一条铁律没被执行到位: ★**「先落骨架再干活」的第一动作是【写】, 不是【读】★ ⇒ ★**这一趟: 第一动作就是 write, 读只在写完之后补** ★ ★

★**★但好消息: ★**cont3 那一趟其实把【B1 硬指标表】写完了 (★12 类硬指标·每类都带具体数字★) ⇒ ★**这一趟不用再补数字, 只补【哪条判据脚本的哪一行产出它】那一列 + B6 的实际输出 + 最终回复** ★ ★

## ★★★【★★② ★★这一趟只做三件 (★按顺序做·★不许插队★)】★★★

### ★★第 1 步 (★先做这个·★不许先读任何文件★): ★★B6 贴【实际输出】★★

★**★在交卷页 B6 下面直接写一段 (★用 `edit` 往 B6 那一节末尾追加, ★**不要整文件 write**★), 内容 = 下面这些命令的真实输出 (★你跑一次, 把输出原样贴进去; ★**不许编·不许抄旧值★)★★**:
```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py ; echo "MERGE_RC=$?"
python3 state/gate_check.py ; echo "GATE_RC=$?"
python3 state/issue_check.py ; echo "ISSUE_RC=$?"
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
grep -cE "🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__" "HANDOFF/2026-11-18_mech-lead_ISS326_S1改名MECH侧安全性体检.md" MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md
find tmp/iss326 -type l | wc -l
```
★**★期望值 (★对不上就是有问题·★要写进交卷页★)★★**: ★MERGE_RC=0 · ★GATE_RC=0 (★若红在 SW 侧 ⇒ 原样贴 + 写一句「红在 SW 侧, 与 mech 无关」★) · ★ISSUE_RC=0 · 板 md5 **`611b869e13518c3c023fb178f91a0075`** · 板 mtime **`2026-11-06 07:07:17.362193413`** · 占位符 **0 0** · 软链数 **0** ★

### ★★第 2 步: ★★给 B1 硬指标表加一列「★产出它的判据脚本 + 行号 + 复算命令★」★★

★**★B1-1 那张表已经有 12 行硬指标 (★1,934 行 / 218 条 (186+32) / 三口径 1,934·1,282·7,553 / 口径D 571 / py-only 578 / 假阳性 5,619 / 三清单 383·164·1,356·31 / 三形态 1,588·87·259 / 沙盒 8 条 / C14 60→56→16 / 暴露面 68+7 / 扫描面 113 份·230 token★) ⇒ ★**你只要给每一行补上「哪道判据脚本 + 行号 + 复算命令」三样★★ ★
- ★**不许新读源码**: ★**行号与命令从你已落盘的 `logs/iss326/gate_design/GATE_DESIGN.md` · `logs/iss326/mech_ref_disposition.tsv` · `logs/iss326/sandbox/*.log` 里抄** ★
- ★**找不到对应脚本/行号的 ⇒ 写「无单一出处·见 <文件>」★★ ★**不许编行号** ★

### ★★第 3 步: ★★最终回复 (★一句话结论 + 自证输出 + 交付物清单 + 给 main 的 3 条★) ★★

★**★给 main 的三条 (★你必须自己写·★内容方向已定★)★**:
1. ★**「假绿」已被实证** (★case1B★): ★**判据脚本里的字面量与【数据+板】不同步 ⇒ 判据分支再也匹配不上 ⇒ 闸红不出来, 而主判据 N1..N6 仍全绿** ⇒ ★**缺陷对闸隐形** ⇒ ★**⇒ 改名时判据脚本必须与数据同批改 (case1C 证明这条配方成立)** ★
2. ★**「崩」已被实证** (★case2★): ★**板上 `D_LED_G` 改名 ⇒ `fps[LED_REF]` 抛异常 ⇒ 默认模式 rc=2 (只红在 md5 闸) · `--compute` 模式 rc=1** ⇒ ★**⇒ 崩不一定红在判据上 ⇒ 别指望崩会自己暴露** ★
3. ★**「半改必红」与「注释里的 ref 无功能影响」已被实证** (★case1D / case4★): ★**只改数据不改板 ⇒ N1/N2 立刻 NG** · ★**改注释里的 ref ⇒ 输出与基线逐字节相同** ⇒ ★**⇒ 「注释里的 ref 不需要改」成立** ★

---

## ★★★【★★③ ★★边界 (★逐条自证, 交卷前贴输出★)】★★★】★★★

- ★**零写板** (★md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413`★) · ★**零落表** · ★**零改闸** (★`MECH/*.py` 一个字都不许改★) · ★**零改既有文档正文** (★`MECH/**` 既有 md 只读 ⇒ ★**只许写 `MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md` 这一个本单自己的产物 + 本单交卷页★)★ ★**零改生成器/判据脚本** ★
- ★**沙盒只写 `tmp/iss326/` + `logs/iss326/`** · ★**只写 `state/fragments/mech.yaml`** (★必须 `state/frag_write.py --agent mech-lead`·★禁止 `open(p,"w")`★) · ★**零改 `state/gate_check.py`** · ★**零外发** · ★**不替老板拍板** · ★**不自签 `state/issue_log.yaml`** ★
- ★**★★不许重跑沙盒用例 (★证据全在 `logs/iss326/sandbox/` + `logs/iss326/gate_design/` + `logs/iss326/mech_ref_disposition.tsv`·★重跑 = 白烧一小时 + 有把读数跑歪的风险★)★★ ★
- ★**★★只做「补」不做「重写」: ★**用带唯一锚点的 `edit` 往里补, 不许整文件 `write` 覆盖 (★ISS-325 那边刚出过四个 run 并发写同一批文件的事故★)★★ ★
- ★**★一次 write 别超过 ~6000 字 ⇒ 先 write 骨架, 再 edit 逐块补** ★
- ★**★★第一动作 = 写 (★读一次就够·★读完马上写·★别把「先摸清」当第一步★)★★ ★**
