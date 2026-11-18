# ★★⑮ · ISS-295 cont2 续做说明 (★2026-11-17 19:0x 由 main (moli) 追加★)

> ★**为什么有这一段**: 上一趟子会话 `agent:mech-lead:subagent:f0b68fcc` (sessionId 4d2565ef) 18:13:48 → 18:28:32 · runtime 881s · **status=timeout / abortedLastRun=true** ⇒ ★**transcript 最后两行 = assistant「Backing up the two pages before the append-only edit, then generating the correction sections:」→ toolResult「[openclaw] missing tool result in session history…」** ⇒ ★**死在「两页追加订正节」之后、「填交卷单 + 写分片」之前** ★
> ★**⚠ ⑭ 节 (cont1) 的「盘面实况」表已过期 ⇒ 【以下面 ⑮ 节为准】★**

## ★★⑮-1 · 盘面实况 (★main 2026-11-17 18:5x~19:1x 本机实跑 + 实读, 不抄任何 agent 报告★)

| 交付物 | main 实测状态 (19:1x) | 本趟动作 |
|---|---|---|
| ① `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` | ★**37114 B · 结构 §0~§8 齐全** ★ (含 §5 还没主的输入 / §6 main 该做什么 / §8 机器判据入口) | ★**复核即可, 不许重做★** |
| ② `MECH/check_mech_verdict_freshness.py` | ★**21330 B · 存在但【跑不通】** ★ ⇒ ★**本趟主战场★** | ★**见 ⑮-2 的三条缺陷, 逐条修★** |
| ③ 两页追加订正节 | ★**已追加 (mtime 18:25)** ★ ⇒ `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` L2170 + `MECH/BOARD_ONEPASS_MECH_SYNC.md` L801 都有 `§ISS-295-订正覆盖表` 小节; ★**两页「现状句」逐字一致 (main 实测 True)** ★; 两页 md5 都已从 `logs/iss295/pages_md5_before.txt` 记录的旧值变过 ⇒ ★**追加这步已做对** ★ | ★**★不许再追加一遍★ (会造出第二份覆盖表 ⇒ 闸反而红)** ★ |
| ④ 交卷单 `HANDOFF/2026-11-17_mech-lead_ISS295_结构输入认领与防漂闸.md` | ★**5368 B · B0~B6 七节标题都在, 但 B3-1 分叉全表 / B4 原样 rc / B5 / B6 是占位** ★ (B4 只写「见下方 §B4 正文」而下方没有 §B4 正文) | ★**填满 + 贴原样 rc★** |
| ⑤ 分片 `state/fragments/mech.yaml` | ★**`grep -c iss295` = 0 ⇒ 一条都没写** ★ | ★**走 `state/frag_write.py --agent mech-lead` 原子写★** |

★**受保护 5 件基线 (★main 19:1x 实测, 直接当你的验收基线★)**:
板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · `.kicad_pro` `3e504d2b…` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ★★**必须逐字节不变**★★

## ★★⑮-2 · 新闸的三条缺陷 (★main 19:1x 实跑原样 rc, 逐条带行号★)

★**闸本体已经写完了 (21330 B) ⇒ 本趟【只修不重写】★**

### ★缺陷 A · 主模式直接崩 (rc=1) ★

```
$ python3 MECH/check_mech_verdict_freshness.py
...
  File ".../MECH/check_mech_verdict_freshness.py", line 437, in main
    for k, r in res["detail"]:
ValueError: too many values to unpack (expected 2, got 7)
rc=1
```
★**根因**: `check()` 往 `res["detail"]` 里 append 的是 **dict** (★`{"check": ..., "id": ..., "page": ..., "anchor": ..., "where": ..., "kept_outside": ..., "quoted_in_corr": ...}` 7 个键★) ⇒ ★**L437 的 `for k, r in ...` 按 2-元组解包 ⇒ 炸** ★
★**修法**: 按 dict 迭代 (★`res["detail"]` 里 F2/F3 / F4 / F5 / F6 四种 check 的键还不一样 ⇒ 打印分支要按 `r["check"]` 走, 别假设只有一种形状★) ⇒ ★**判据一个字不许改** ★

### ★缺陷 B · 闸自己的清单违反它自己写的规则 ⇒ 现状被判红 (rc=1) ★

```
$ python3 MECH/check_mech_verdict_freshness.py --json
  "ok": false,
  "errs": [
    "F2 锚点 XC-3 长度 12 < 14 ⇒ 清单自身不合规 ⇒ 红",
    "F2 锚点 XC-6 长度 10 < 14 ⇒ 清单自身不合规 ⇒ 红"
  ]
```
★**根因**: 该闸 L89 自己写着「★锚点必须是页内【唯一】的逐字串, 且长度 ≥ 14★」⇒ ★**但 `MANIFEST` 里 XC-3 的锚点只有 12 字 / XC-6 只有 10 字 ⇒ 闸自己判自己红** ★
★**修法 = 把这两条锚点换成【≥14 字】的逐字串, 且必须同时满足 3 条 (★main 已把候选量好, 你不必重找★)**:
1. ★**逐字出现在【订正节之外】的老行里** (★⇒ F2 的「kept_outside」要真, 证明老留痕没被改写★)
2. ★**逐字出现在【同页订正节】里** (★⇒ F3 的「quoted_in_corr」要真★)
3. ★**长度 ≥ 14** ★
★**main 19:1x 实测过的两个候选 (★共 40/23 字, 页内各只出现 2 次 = 1 次老行 + 1 次订正节覆盖表★)**:
- ★**XC-3**: 老行 L188 与覆盖表 L2186 的公共子串 `1 个: \`J_USB_C\` (16p @0.50 + 2×Ø0.65 对上, ` (★40 字★) —— ★**另一段公共子串 `但结构侧缺一条边开口规格` 只有 12 字, 不够★**
- ★**XC-6**: 老行 L298 与覆盖表 L2189 的公共子串 `现有 MECH 规格 (检修口 / 调试口两条` (★23 字★) —— ★**另一段公共子串 `) 里【没有】这条边开口` 只有 12 字, 不够★**
★**⚠ 换锚点后, 覆盖表里的「逐字锚点」列要同步写成同一串 (★两处一致才不漂★) ★** ★**★不许把 ≥14 这条规则调低来凑绿 (★那就是把判据改松★)★**

### ★缺陷 C · `--selftest` 6/7 ⇒ 唯一失败的那条是缺陷 B 的连带 ★

```
$ python3 MECH/check_mech_verdict_freshness.py --selftest
  -- 合计 7 条 · 通过 6 · 失败 1
  -- 失败用例: ['④ 正向对照: 现状原样 ⇒ 必须绿']
rc=1
```
★**根因**: ④ 是「现状原样 ⇒ 必须绿」⇒ ★**现状被缺陷 B 的 2 条 F2 判红 ⇒ ④ 自然红** ⇒ ★**修好缺陷 B, ④ 自动转绿 (⇒ 7/7 rc=0)★** ⇒ ★**★不许为了让 ④ 绿去改 ④ 的期望值或削弱 F2/F3★** ★

### ★已经全绿的部分 (★main 19:1x 实测 ⇒ 不许动, 也不许重做★) ★
- ★**F2/F3 九条锚点全部 `kept_outside=true` + `quoted_in_corr=true`** ★ (MS-1/2/3 · XC-1/2/4/5 六条已合规; XC-3/XC-6 只差长度)
- ★**F4 九条漂移扫描全部 `covered=true`** ★
- ★**F5 两页 `canon_found=true`** ★ (订正节都带新鲜度标记)
- ★**F6 机器块矩形 `132.995/147.005/0.000/7.300` == 期望** ★ ⇒ ★**ISS-290 的机器块一个字没被改 (正确)★**
- ★**两页现状句逐字一致** ★

## ★★⑮-3 · 本趟只做 4 件 (★顺序不许换★)

1. ★**修缺陷 A + B** ⇒ `python3 MECH/check_mech_verdict_freshness.py` ⇒ **rc=0** 且 `--json` 的 `ok=true` · `errs=[]`
2. ★**`--selftest` ⇒ rc=0 且 7/7** ⇒ ★**★不许把任何一条反向用例改松★**
3. ★**填交卷单**: B3-1 分叉全表 (贴原样 grep) + B4 六道闸原样 rc + B5 边界自证 + B6 (★**B6 要写清「新闸挂进 `state/gate_check.py` 是 main 的活」★**)
4. ★**分片**: `python3 state/frag_write.py --agent mech-lead` 原子写 ⇒ ★**`grep -c iss295 state/fragments/mech.yaml` ≥ 4** ★ + 4 条 need 的汇总 answer key 与被问方开单时用的 key 逐字一致

## ★★⑮-4 · 验收 (★原样 rc 贴进交卷单 B4★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 MECH/check_mech_verdict_freshness.py;             echo "rc=$?"   # 期望 0
python3 MECH/check_mech_verdict_freshness.py --selftest;  echo "rc=$?"   # 期望 0 (7/7)
python3 MECH/check_onepass_mech_sync.py;                  echo "rc=$?"   # 期望 0
python3 MECH/check_onepass_struct_crosscheck.py;          echo "rc=$?"   # 期望 0
python3 state/merge.py;                                   echo "rc=$?"   # 期望 0
python3 state/gate_check.py;                              echo "rc=$?"   # 期望 0 (Q1 18/18)
grep -c iss295 state/fragments/mech.yaml
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
```

## ★★⑮-5 · 边界 (★违反就是不合格★)

★**零写板** · ★**零落表** (★网表/脚表/BOM 一个字节不许动★) · ★**未改 `HW/`** · ★**未改既有 MECH 判据脚本** (★`MECH/check_onepass_mech_sync.py` / `MECH/check_onepass_struct_crosscheck.py` 一个字节不许动★) · ★**未改 `state/gate_check.py`** (★挂闸是 main 的活★) · ★**未改 STRUCT_CROSSCHECK 机器块** (★`openings[]` / `rect` / `tiers` / `verdict`★) · ★**两页的「老行」一个字不许删/不许改** (★只在订正节里改★) · ★**两页不许再追加第二份订正节** · ★**零外发** · ★**不替老板拍板** · ★**不自签 issue_log** (★签字是 main 的活★) · ★**只写自己的分片** · ★**实物 `[实测]` = 0 条**

## ★纪律 (★上一趟就是这么栽的★)

★**长任务一律 `nohup ... > logs/iss295/x.log 2>&1 &` + 短轮询** (★前台长 exec = 被掐的头号原因★) · ★**单条 exec ≤ ~120 秒** ★ · ★**每 10 分钟至少一次写盘** ★ · ★**每落一件交付物就把 rc 追加进交卷单** ★ · ★**交卷单第一件事就是 `write` 补骨架** ★ · ★**分片写完 `grep` 校验** ★ · ★**不许把整份大文件读进来** (★只 grep 你要改的那几行★)
