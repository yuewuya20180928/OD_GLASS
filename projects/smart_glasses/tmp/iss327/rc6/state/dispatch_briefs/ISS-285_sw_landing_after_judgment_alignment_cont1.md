# ISS-285 · sw-lead 续做任务书 (cont1) · 落表后 SW 侧三道判据口径收口

> ★**派活人**: 项目总工 (main / moli) · ★**派活时刻**: ★**2026-11-17 11:4x** ★ · ★**job**: cron `fb67af40` (ARS45 队列自动派活) ★
> ★**owner**: sw-lead · ★**verify_by**: main · ★**单号**: ISS-285 · ★**零外发** ★
> ★**本单性质**: ★**内部活 · 门禁/判据口径侧** ★ ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM · 不替老板拍板** ★
> ★**完整任务书原文** = `state/dispatch_briefs/ISS-285_sw_landing_after_judgment_alignment.md` (★9607 B · 11:07★) ⇒ ★**开工第一件事先 cat 全文**★

★**★这是【续做】不是【重做】★**: ★**上一趟会话 `agent:sw-lead:subagent:b15754e1` (11:05:28 → 11:35:47 · status=timeout · abortedLastRun=true) 被掐** ⇒ ★**盘上已有半成品, 从盘面继续, 不要从零重做**★

---

## ★0 · 上一趟的实况 (★main 本机实查盘 + 读 transcript, 不抄任何交卷报告★)

| 交付物 | 盘面实况 (main 实测) |
|---|---|
| ★**交卷单** `HANDOFF/2026-11-17_sw-lead_ISS285_落表后SW判据口径收口.md` ★ | ★**1362 B 骨架** (11:21) ⇒ ★**§0 情形判定已填** (★结论 = **情形一**: ISS-283 未落 verified ⇒ 只做只读分析 + 方案页 + 自测设计, 不改锚点 / 不改 `timing_check.py` 判据 / 不改期望值★) · ★**§1~§6 全是「(施工中·待填)」** ★ |
| ★**补丁套用器** `SW/patches/ISS-285_sw_judgment_alignment/apply_iss285_sw_judgment_alignment.py` ★ | ★**24640 B (11:33) 已在盘** ★ ⇒ ★**是半成品, 一次都没跑过**★ (★`logs/iss285/` 目录不存在 ⇒ 证明它没跑过★) · 自述三件事: ★**B1** 网表锚点判据改读【落表台账链头】(与 `check_demo_panel_spec.py` R6 同一判决源 / 同一份实现 ⇒ 真同源) · ★**B2** F4' 期望改成「BAT_DET 三颗必装」并按【器件本体行】逐颗读 dnp · ★**B3** 追加反向用例 REV-11 (三颗改回 DNP ⇒ 必红)★ · 自带 `--dry-run` / `--apply` / `--apply --reanchor` 三档 (★**情形一不许 `--apply`** ★) |
| ★**分片** `state/fragments/sw.yaml` ★ | ★`grep -c ISS-285` = **0** ⇒ ★**分片零写** ★ |
| ★**日志** ★ | ★`logs/iss285/` **不存在** ⇒ 零实测记录 ★ |

★**transcript 末条**: 「Now I'll write the patch (as an idempotent applier) — to `SW/patches/`, not touching any real file yet.」⇒ ★**它写完补丁就断了, 连自己的补丁都没跑过** ★

★**⇒ 情形判定不变 (main 已复查 `state/issue_log.yaml`: ISS-283 = open, ISS-285 = fixing) ⇒ 本单仍是【情形一】★**

---

## ★1 · 本单要收的缺口 (★按这个顺序做, 每步落盘★)

★**① 续填交卷单骨架** (★骨架已在盘 ⇒ ★**接着填, 另起一份 = 交卷不合规**★)

★**② 跑一次补丁套用器的 `--dry-run`** ⇒ ★**贴原样输出** ★ ⇒ ★**若它报错 ⇒ 修补丁套用器本身 (★不许改判据方向★) ⇒ ★不许绕过它直接手改 `SW/tools/timing_check.py`**★

★**③ 在沙盒里端到端验补丁 (★真盘不许动★)**:
- ★**正向**: 沙盒台账链头取 ★**09:58:16 A1+A2 那一跳** (★ISS-283 那三件还没落 ⇒ 沙盒里拿它当链头做演示, 并在方案页写明「这是沙盒; 真链头要等 ISS-283 落表后自动前移」★) ⇒ 沙盒内 `timing_check.py` ⇒ ★**71/71 全绿** ★
- ★**反向 5 条 (★照原任务书 §B3, 一条不许少★)**:
  | # | 构造 | 期望 |
  |---|---|---|
  | ① | 盘上网表 md5 落在台账登记的任何状态之外 (伪造 md5) | ★**红** ★ |
  | ② | 落表台账那一行四项不齐 (单号 / 文件名 / 前后 md5) | ★**红** ★ |
  | ③ | 链头不唯一 (台账里两条指向同一文件) | ★**红** (fail-closed 不许动) ★ |
  | ④ | 把 BAT_DET 三颗改回 DNP (期望值被改坏) | ★**红** ★ |
  | ⑤ | 正向对照: 一切如常 | ★**绿** (证明闸不是恒红) ★ |
- ★**每条都要贴「期望红组 vs 实际红组」原样输出** ★

★**④ 方案页**: ★**「等 ISS-283 落表后一次性套用」的补丁说明 + 反向用例设计 + 落表台账接口格式 (单号/文件名/改前 md5/改后 md5 四件同行) + 套用步骤 + 回滚步骤 + 「为什么现在不套」的时序理由** ★ ⇒ ★**落点**: 与交卷单同目录下, 文件名 = 交卷单文件名 + `_方案页` 后缀 (★不要新建目录★) ★

★**⑤ 交卷单 B1~B6 填满** (★每块都要有实测 rc, ★**不许留「(施工中·待填)」**★)

★**⑥ 分片** `state/fragments/sw.yaml` ⇒ ★**走 `python3 state/frag_write.py --agent sw-lead` 原子写** (★禁止 `open(p,"w")`★) ⇒ ★**写完 `grep` 校验 `iss285` 在不在** ★

★**⑦ 登记 need 给 main**: ★**「等 ISS-283 落 verified 后套用本补丁 + 锚点前移到链头」** (★说清等哪个单号★) ★

---

## ★2 · 边界 (★违反就是不合格★)

★**零写板** (★板 `611b869e…` / `.kicad_pro` `3e504d2b…` 必须逐字节不变★) · ★**零落表** (★网表 / 脚表 / BOM 一个字节不许动★) ·
★**★情形一硬约束: 不许改 `SW/SW_MD5_BASELINE_LEDGER.md` 的锚点 · 不许改 `SW/tools/timing_check.py` 的判据 · 不许改任何期望值★** ·
★**不许动 `HW/` 与 `MECH/` 的文件与分片** (★`HW/check_onepass_preflight_coverage.py` 的红归 ISS-283 (hw-lead) ⇒ **你不要碰它**★) ·
★**不许弱化 ISS-275 已跑通的链头逻辑** (★改完 `check_demo_panel_spec.py` 算出的【链头 / 链 / 产出单号】必须与改前逐字相同★) ·
★**不许放宽 fail-closed 三条** (链头不唯一 / 链断 / 链头无单号 ⇒ 红) · ★**不许把落表台账当「锚点可写集合」** (★append-only + 链完整性防线不许松★) ·
★**零外发** · ★**不替老板拍板** · ★**不自签 issue_log** (★签字是 main 的活★) · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)

---

## ★3 · 验收 (★贴原样 rc★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 SW/tools/check_demo_panel_spec.py; echo "rc=$?"            # 期望 rc=0 (R1~R7 全过)
python3 SW/tools/check_demo_panel_spec.py --selftest; echo "rc=$?"   # 期望 rc=0 (★条数只许增不许减★)
python3 SW/tools/timing_check.py; echo "rc=$?"                     # ★★期望 rc=1 · 68/71★★ (★见下面红字★)
python3 HW/check_step1_parts_spec.py; echo "rc=$?"                 # 期望 rc=0
python3 state/merge.py; echo "rc=$?"                              # 期望 rc=0
python3 state/gate_check.py; echo "rc=$?"                          # 期望 rc=0 (Q1 18/18)
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

★★**红字 (★本单最容易出的错★)**: ★**真盘上 `timing_check.py` 本来就该红 (68/71) ⇒ 交卷时它【必须还是 68/71】★** ★**只有沙盒里才该 71/71** ★ ⇒ ★**真盘变绿 = 你偷偷改了判据 = 不合格** ★ ⇒ ★**方案页写清「套用时机 = ISS-283 落 verified 之后」** ★

★**受保护件读数 (★交卷时贴出来★)**: 板 `611b869e…` · `.kicad_pro` `3e504d2b…` (★板 mtime 应仍是 2026-11-06 07:07:17★) · 网表 / 脚表 / BOM = ★**落表后值 `2f17650c…` / `6ea65fec…` / `ea5f4f58…`** (★台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16.2 登记★) ⇒ ★**这三个不许被你改回去★**

---

## ★4 · 纪律 (★这项目的老教训★)

★**交卷单第一件事就是 `write` 建骨架** (★骨架已在 ⇒ 直接续填★) · ★**长任务一律 `nohup ... > logs/iss285/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**单条 `exec` ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**分片写完 `grep` 校验** ★ · ★**被掐了就留下盘面实况, 别怕交一半** ★

---

## ★5 · 外发口径 (★硬规则★)

★**不许外发任何邮件 / 询价 / 问询 / 采购 / 原厂问询 / 任何对外沟通** (★老板 2026-11-11 19:31 + ★★2026-11-12 02:02: 「不再发信, 全靠自己查资料」★) ⇒ ★**没有「老板批一句可以发」这个选项** ★ ⇒ ★**缺口一律【自己网上查】+ 标证据等级** (★`[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`★) ★**+ 查不到就写降级方案** ★ ⇒ ★**零外发** ★
