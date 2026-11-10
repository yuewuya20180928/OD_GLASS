# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

## First Run

If `BOOTSTRAP.md` exists, that's your birth certificate. Follow it, figure out who you are, then delete it. You won't need it again.

## Session Startup

Use runtime-provided startup context first.

That context may already include:

- `AGENTS.md`, `SOUL.md`, and `USER.md`
- recent daily memory such as `memory/YYYY-MM-DD.md`
- `MEMORY.md` when this is the main session

Do not manually reread startup files unless:

1. The user explicitly asks
2. The provided context is missing something you need
3. You need a deeper follow-up read beyond the provided startup context

## Memory

You wake up fresh each session. These files are your continuity:

- **Daily notes:** `memory/YYYY-MM-DD.md` (create `memory/` if needed) — raw logs of what happened
- **Long-term:** `MEMORY.md` — your curated memories, like a human's long-term memory

Capture what matters. Decisions, context, things to remember. Skip the secrets unless asked to keep them.

### 🧠 MEMORY.md - Your Long-Term Memory

- **ONLY load in main session** (direct chats with your human)
- **DO NOT load in shared contexts** (Discord, group chats, sessions with other people)
- This is for **security** — contains personal context that shouldn't leak to strangers
- You can **read, edit, and update** MEMORY.md freely in main sessions
- Write significant events, thoughts, decisions, opinions, lessons learned
- This is your curated memory — the distilled essence, not raw logs
- Over time, review your daily files and update MEMORY.md with what's worth keeping

### 📝 Write It Down - No "Mental Notes"!

- **Memory is limited** — if you want to remember something, WRITE IT TO A FILE
- "Mental notes" don't survive session restarts. Files do.
- When someone says "remember this" → update `memory/YYYY-MM-DD.md` or relevant file
- When you learn a lesson → update AGENTS.md, TOOLS.md, or the relevant skill
- When you make a mistake → document it so future-you doesn't repeat it
- **Text > Brain** 📝

## Red Lines

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever)
- When in doubt, ask.

## External vs Internal

**Safe to do freely:**

- Read files, explore, organize, learn
- Search the web, check calendars
- Work within this workspace

**Ask first:**

- Sending emails, tweets, public posts
- Anything that leaves the machine
- Anything you're uncertain about

## Group Chats

You have access to your human's stuff. That doesn't mean you _share_ their stuff. In groups, you're a participant — not their voice, not their proxy. Think before you speak.

### 💬 Know When to Speak!

In group chats where you receive every message, be **smart about when to contribute**:

**Respond when:**

- Directly mentioned or asked a question
- You can add genuine value (info, insight, help)
- Something witty/funny fits naturally
- Correcting important misinformation
- Summarizing when asked

**Stay silent when:**

- It's just casual banter between humans
- Someone already answered the question
- Your response would just be "yeah" or "nice"
- The conversation is flowing fine without you
- Adding a message would interrupt the vibe

**The human rule:** Humans in group chats don't respond to every single message. Neither should you. Quality > quantity. If you wouldn't send it in a real group chat with friends, don't send it.

**Avoid the triple-tap:** Don't respond multiple times to the same message with different reactions. One thoughtful response beats three fragments.

Participate, don't dominate.

### 😊 React Like a Human!

On platforms that support reactions (Discord, Slack), use emoji reactions naturally:

**React when:**

- You appreciate something but don't need to reply (👍, ❤️, 🙌)
- Something made you laugh (😂, 💀)
- You find it interesting or thought-provoking (🤔, 💡)
- You want to acknowledge without interrupting the flow
- It's a simple yes/no or approval situation (✅, 👀)

**Why it matters:**
Reactions are lightweight social signals. Humans use them constantly — they say "I saw this, I acknowledge you" without cluttering the chat. You should too.

**Don't overdo it:** One reaction per message max. Pick the one that fits best.

## Tools

Skills provide your tools. When you need one, check its `SKILL.md`. Keep local notes (camera names, SSH details, voice preferences) in `TOOLS.md`.

**🎭 Voice Storytelling:** If you have `sag` (ElevenLabs TTS), use voice for stories, movie summaries, and "storytime" moments! Way more engaging than walls of text. Surprise people with funny voices.

**📝 Platform Formatting:**

- **Discord/WhatsApp:** No markdown tables! Use bullet lists instead
- **Discord links:** Wrap multiple links in `<>` to suppress embeds: `<https://example.com>`
- **WhatsApp:** No headers — use **bold** or CAPS for emphasis

## 💓 Heartbeats - Be Proactive!

When you receive a heartbeat poll (message matches the configured heartbeat prompt), don't just reply `HEARTBEAT_OK` every time. Use heartbeats productively!

You are free to edit `HEARTBEAT.md` with a short checklist or reminders. Keep it small to limit token burn.

### Heartbeat vs Cron: When to Use Each

**Use heartbeat when:**

- Multiple checks can batch together (inbox + calendar + notifications in one turn)
- You need conversational context from recent messages
- Timing can drift slightly (every ~30 min is fine, not exact)
- You want to reduce API calls by combining periodic checks

**Use cron when:**

- Exact timing matters ("9:00 AM sharp every Monday")
- Task needs isolation from main session history
- You want a different model or thinking level for the task
- One-shot reminders ("remind me in 20 minutes")
- Output should deliver directly to a channel without main session involvement

**Tip:** Batch similar periodic checks into `HEARTBEAT.md` instead of creating multiple cron jobs. Use cron for precise schedules and standalone tasks.

**Things to check (rotate through these, 2-4 times per day):**

- **Emails** - Any urgent unread messages?
- **Calendar** - Upcoming events in next 24-48h?
- **Mentions** - Twitter/social notifications?
- **Weather** - Relevant if your human might go out?

**Track your checks** in `memory/heartbeat-state.json`:

```json
{
  "lastChecks": {
    "email": 1703275200,
    "calendar": 1703260800,
    "weather": null
  }
}
```

**When to reach out:**

- Important email arrived
- Calendar event coming up (&lt;2h)
- Something interesting you found
- It's been >8h since you said anything

**When to stay quiet (HEARTBEAT_OK):**

- Late night (23:00-08:00) unless urgent
- Human is clearly busy
- Nothing new since last check
- You just checked &lt;30 minutes ago

**Proactive work you can do without asking:**

- Read and organize memory files
- Check on projects (git status, etc.)
- Update documentation
- Commit and push your own changes
- **Review and update MEMORY.md** (see below)

### 🔄 Memory Maintenance (During Heartbeats)

Periodically (every few days), use a heartbeat to:

1. Read through recent `memory/YYYY-MM-DD.md` files
2. Identify significant events, lessons, or insights worth keeping long-term
3. Update `MEMORY.md` with distilled learnings
4. Remove outdated info from MEMORY.md that's no longer relevant

Think of it like a human reviewing their journal and updating their mental model. Daily files are raw notes; MEMORY.md is curated wisdom.

The goal: Be helpful without being annoying. Check in a few times a day, do useful background work, but respect quiet time.

## Make It Yours

This is a starting point. Add your own conventions, style, and rules as you figure out what works.

## Related

- [Default AGENTS.md](/reference/AGENTS.default)

## 【铁律】模块/模组内部已实现的项, 母板一律不重复做 (2026-11-03)

★**来源**: 2026-11-03 发现 **Forlinx FET3572-C 自带 PMIC** ⇒ 主板上两颗给 SoC 核心/IO 轨供电的 DC-DC
是纯浪费 (连带整条上电时序链 5 个件) ⇒ ★**这不是孤例** ⇒ 已落清单:
`projects/smart_glasses/HW/PCB/SOM_BUILTIN_CAPABILITY.md`

**规则**:
1. **加任何"供电/时钟/存储/复位/信号生成"件之前, 先查那份清单** ⇒ 模块里已有的 ⇒ 母板不重复做
2. ★**砍之前必须有原厂手册出处** (没出处的**不许砍** —— 砍错了就是板子不工作)
3. 清单里"已砍"的项若又出现在网表里 ⇒ 算**回归缺陷**, 必须写理由
4. 换料/换模组时先过一遍清单 ⇒ 直接影响板面积 / BOM / 热 / 电源树 / 进度

## 【铁律】"量过" ≠ "验过且通过" —— 发布闸必须认后者 (2026-11-05 09:20 实测事故)

★**来源**: 2026-11-05 09:11 从 cron 日志里发现 —— ★**带焊盘短路的 v25 板 + 它出的 30 个 Gerber 被推上了 GitHub** (commit f31814b)

★**事故链** (★每一步单看都"合理", 串起来就放行了未验证产物):
1. `auto_release_if_ready.sh` 自验 rc=1 但 ★**无条件**写 `.verified_board_mtime` ⇒ 语义变成"**量过**"
2. 发布闸判据 "板 mtime ≤ `.verified_board_mtime` ⇒ 通过" ⇒ ⇒ **从没通过自验的板, 因为是最后量过的, 就过了闸**
3. ★**发布闸从不检查 DRC / unconnected** ⇒ ⇒ 焊盘短路完全不在它视野里
4. ⇒⇒ cron 自己把它推上去了

★**规则**:
1. ★**两个标记必须分工**: `.verified_board_mtime` = 量过 (只用于"别重复烧 CPU") · ★`.verified_board_ok_mtime` = **验过且通过 (rc=0 才写)** ⇒ ★**发布闸只认后者**
2. ★**发布闸判据必须含 DRC + unconnected == 0** (`.layout_done.json`) ⇒ ⇒ **且 ok 标记的 mtime 必须等于板 mtime** (⇒ 自验后被改过的板要拦住)
3. ★**板 + 派生产物 (Gerber/钻孔/坐标/贴片) 一起管** ⇒ ⇒ 拦下时一起撤 ⇒ ★**"仓库里没有板" = 诚实状态**
4. ★**rsync 排除板/Gerber, 闸门通过时才显式 cp** ⇒ ⇒ 不会"抄回来又删掉"
5. ★**闸门逻辑写成独立脚本 (`state/board_publish_gate.sh`) 再单测** ⇒ ⇒ ★**发布脚本本身是"会真推 GitHub 的", 绝不能靠跑全脚本来测**
6. ★**写完必须跑**: ★我这次写完就踩了三个坑 (闸门跑错树 / 路径语义混 / 用 python 跑 bash) ⇒ ⇒ **单测要覆盖"该 BAD 的场景"**

## 【铁律】实验轮不许拿官方板当输出槽 (2026-11-05)

★**来源**: 2026-11-05 06:53 v23 8 层 A/B 臂**没带 `PCB_OUT`** ⇒ 生成器的中途落盘
(`gen_pcb_routing.py:2242` `_save_board_progress`) 直接写官方板 ⇒ 官方板被冲成 **0 段骨架**
⇒ 好板只剩 `/tmp/board_last_good.kicad_pcb` (在 /tmp ⇒ 重启即失)。

**规则**:
1. ★**任何实验/对比轮必须带 `PCB_OUT=/tmp/xxx.kicad_pcb`** ⇒ 官方板只由"赢家轮"落盘
2. 官方板被中途冲掉 ⇒ 第一动作: `cp /tmp/board_last_good.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb`
   并**立刻把好板存到 `state/.lastgood/`** (持久位置) ⇒ 别指望 /tmp
3. ★**发布/自验都要看"这块板是不是刚落的那块"** ⇒ 用 `state/.verified_board_mtime` (一直在维护)
   或落盘时刻印 `.layout_landed.json` ⇒ 中途被存盘覆盖过的板**既不许量、也不许推**
4. 跑长脚本 ⇒ **`python3 -u`** ⇒ 否则重定向到文件的日志是块缓冲, 跑几十分钟也是 0 字节 ⇒ 监控全瞎

## 【铁律】要按 PID 杀进程, 先用 /proc/<pid>/environ 认准是哪个 (2026-11-05 10:45 实测事故)

★**事故**: 想停"臂 F"(10层那条线), 因为 PWD 猜 PID ⇒ ★**把最好的臂 E (8层 + F7 + 出脚修复) 一起杀了**
  (E 当时已经布到 17/22 对 · 10 对全耦合 Δ=0.000 ⇒ ★**是当天最好的成绩**)

★**为什么不能靠猜**: 启动脚本里 `wrapper → timeout → python` 三层, ★**python 的 PID 不等于 wrapper+2**
  ⇒ 同一个脚本多次启动后 PID 完全对不上 ⇒ ★**猜错就杀错臂**

★**正确做法 (唯一姿势)**:
```bash
for p in $(pgrep -f "gen_pcb_netlist_board.py"); do
  echo "$p -> $(tr '\0' '\n' < /proc/$p/environ | grep '^PCB_OUT=')"
done
```
⇒ ★**每个实验臂都用 `PCB_OUT=/tmp/<轮>_<臂>.kicad_pcb` ⇒ PCB_OUT 就是这个进程的唯一身份**
⇒ ⇒ ★**杀之前先认领, 杀完再确认** ⇒ ★**绝不凭"哪个 PID 像哪个臂"**

★**附带**: `EXIT=143` = SIGTERM(被人杀) · `EXIT=137` = SIGKILL(常是 OOM) · `EXIT=124` = timeout

## 【铁律】同一图元只能进板一次 (记账必须和落板同源) + 豁免圈不许盖住别人的铜 (2026-11-05 12:30)

★**来源**: v28_H 板实测 DRC 147 = **65 处同点重复过孔** + **21 处差分 P/N 自短路** ⇒ 两个都不是"路由器算错", 而是**记账/豁免**问题

★**坑① (同一图元进板两次)**:
- GND 下拉那一路**直接 `board.Add(过孔)`**, 同时又把元组塞进 `self.vias`
  ⇒ 之后 `commit()` 遍历 `self.vias` **又画一遍同一个孔** ⇒ **板上 453 孔 vs 内存 385 孔 (差 68)**
  ⇒ ⇒ DRC `holes_co_located` ×65 ⇒ ⇒ **官方板上一直挂的那 2 处 DRC 就是这个 bug, 一直"修了"但没修到根上**
- ★**规则**: ★**凡是把图元直接 Add 到板上的地方, 必须同时登记进 `_committed` (按对象 id)** ⇒ commit 就会跳过它
  ⇒ ★**判据**: ★**落板自检的"板上 N 段/M 孔 vs 内存 N 段/M 孔"必须两边完全相等** ⇒ 不等 ⇒ **一定有图元进板两次或漏画**
  ⇒ ★**不要只看内存里的数** —— ★**板上的数才是真相** (`grep -c '(via' 板文件`)

★**坑② (豁免圈盖住别人的铜)**:
- 差分对的"伙伴禁入格"原本豁免 N 焊盘周围 **1.20mm** ⇒ ★**N 侧的出脚直道可以从 P 的通道上横穿过去** ⇒ P/N 铜直接叠上 ⇒ 短路
  (实测: `R_SEL_CK_P` 的通道 y=6.70 横穿 x 94.95~99.20, 而 `R_SEL_CK_N` 的出脚从 y=5.60 往下走到 7.20 ⇒ **必然横穿**)
- ★**规则**: ★**豁免半径只能豁免"自己的那一格"**, 不许豁免到别人的铜箔上 ⇒ ★**豁免参数要可调且默认取最小值**
- ★**通用判据**: ★**任何"为了让某条线走通"而放宽的规则, 都要问一句: ★它会不会让别人短路?** ⇒ ⇒ **放宽规则的当轮, 必须同时跑一次 DRC, 看短接类违规有没有暴涨**

★**顺带**: ★**"量过"和"修到根上"是两回事** ⇒ ★**同一个 DRC 现象反复出现 ⇒ 别再"加查重/加判据", 要去查"是不是同一个图元/同一段铜被算了两遍"**

## 【铁律】晋级判据不能只看 ratsnest 数量 + DRC (2026-11-06 02:0x 实测事故)

★**来源**: 2026-11-06 01:28 `auto_promote_when_done.sh` 判据只有 (unconnected, DRC)
⇒ v44_R (UNC 55 < 57, DRC 0 == 0) 被判"更好" ⇒ **自动晋级成了官方板**
⇒ ★**但逐网实测: v44 把 9 个网打成零铜, 只救回 7 个** ⇒ ★**差分对净 -1 / 普通信号网净 -2**
⇒ ⇒ **官方板实际变差** ⇒ ⇒ 已回滚 v37_R ⇒ ⇒ 判据已换成独立闸 `state/compare_arm_official.py`

★**规则**:
1. ★**"unconnected 变少"不等于板子更好** ⇒ 必须同时看 **零铜网数** + **差分单边零铜对数**
   (★**把有铜的腿砍成零铜 ⇒ ratsnest 变少, 板子更烂**)
2. ★**"Δ 数字变小"也可能是坏事** ⇒ ★**审计器不算零铜对**
   ⇒ v44 的 "DSI_D0_D0 Δ 76.197→1.612" 是**砍掉配平铜、让一侧归零换来的**
   ⇒ ⇒ **看 Δ 汇总前, 必须先看单边零铜对数**
3. ★**晋级判据必须写成独立脚本 + 单测** ⇒ `state/compare_arm_official.py --self-test`
   ⇒ ★**自测用"实测的坏案例"当回归用例** (v44 必须被拒)
4. ★**单边零铜的差分对比 Δ 超差更致命** ⇒ **单边零铜 ⇒ 那条高速通道根本不存在**
5. ★**闸脚本自己也会有 bug**: 差分对清单路径少退一级 ⇒ 指标恒为 0 ⇒ 闸门形同虚设
   ⇒ ⇒ **必须加"清单加载到了 ≥N 对"的断言**, 且 ★**自测要端到端跑真板, 不能只测纯函数**

★★**2026-11-06 02:2x 第二次同型事故 (v46_R 又被放行) ⇒ 判据第三版 (名单制)**:
- ★★**"计数"完全看不出问题**: v46 的 零铜网 26=26 · 单边零铜对 11=11 (全平) ⇒ **但名单变了**
  ⇒ ★**v46 把 10 个本来通的网打成零铜 (含 3 条本来通的差分腿)** ⇒ ⇒ **判据必须比"名单"**
- ★★**硬指标**: DRC=0 · parity 过 · **退铜名单为空** · **差分死腿为空** · unc/零铜网/单边零铜对 不变差
- ★★**"变好"只认 unc 与 zero_copper** ⇒ ★**`diff_over` (Δ超差对数) 只做参考**
  (★**打死一条差分腿 ⇒ 它从"Δ超差"桶移到"单边零铜"桶 ⇒ Δ超差对数假性下降**)
- ★★**终点线也必须自检 + 自动回滚**: "晋级时 DRC=0" ≠ "终点线跑完 DRC=0" (★终点线还要加铜皮/叠层)
6. ★**回滚后必须重写 `.layout_done.json`** (★它被阶段门 G1 读) ⇒ 否则播报和门禁都读着旧数

### 【铁律】多个臂在同一批网/差分对上失败 ⇒ 先查"它们共享的东西", 别急着调路由参数 (2026-11-06 02:1x 实测)
- ★★**实测**: v44 / v46 / v47 / v48 **四个臂全部打死同样三条差分对** (`DSI_D0_CK` · `DSI_D0_CK_SRC` · `DSI_D0_D1`)
  ⇒ ★**四个臂共享的只有 env 和基线** ⇒ ★**根因在布局, 不在路由算法**
- ★★**挖法 (可复用)**: ① 比对四臂的 fail_detail `start`/`goal` ⇒ **坐标全一样 ⇒ 同一原因**
  ② 读官方板里同一张网的铜在哪 (x/y 范围 + 层) ⇒ ★**官方板走右上, 臂走左上 ⇒ 布局被改过**
  ③ 查各臂 env 的差异 ⇒ ★**`PCB_PART_POS` 把 `R_SEL_*` 挪到左上 (x5.5..38.35,y3.0)**
  ⇒ 那条纵向走廊 **x21..35, y6..60 正好穿过 `SOM_AREA=(8,6,68,50)`** ⇒ ★**几何上必布不通**
- ★★**推论**: ★**"同一批失败"是布局级线索, 不是调参线索** ⇒ ★**先改布局, 再谈路由参数**
- ★★**配套**: ★**"落板后剔违规铜"是负收益** (实测 DRC 12→8, 剔链中间段会留悬空端 ⇒ 又生新违规)
  ⇒ ★**只有"落线前就拦"是正收益** ⇒ ★**排查类 bug 要修在产生点, 不许在产物上擦**
