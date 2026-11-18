#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新老板拍板页 DECISION_PENDING_2026-11-11.md (第 13 次刷新) —— 2026-11-11 08:1x

★**只整理 + 给建议默认值, 不代决** —— 拍板前不动任何采购 / 外发 / 改图 / 改锁死表。
★**本轮 C 段口径: 35 → 36 (新增 1 条: `board_p41_promote` —— 官方板是否换成 `candidate_official_p41`)**。
★**本轮实质**: ① 10 分钟播报里有 3 条待办全是过期的 ⇒ **当轮重跑闸把它们逐条订正** (★v76mx1L 已判 REJECT / 护栏⑨ 05:37 就已完成 / 拍板桶 7→5★)
   ② **新增 1 个真正要老板拍板的项** (板子基线 p41) ⇒ 写进 `state/fragments/pm.yaml` 的 `needs_from` (★走 `frag_write.py` 原子写★)
   ③ 视图层三处口径统一 (★`gen_todo.py` / `gen_status_summary.py` / `gen_start_here.py` 的"等你拍板"桶一律排除 `verified`★)
   ④ `state/CURRENT_TASK.md` 重写 (★播报源★) ⑤ GitHub 发布闸解开 (MEMORY openid 脱敏已同步到副本) + 重推成功
"""
import os
import sys

P = "DECISION_PENDING_2026-11-11.md"
s = open(P, encoding="utf-8").read()
lines = s.split("\n")

NEW_TITLE = (
    "# 待老板拍板页 · 2026-11-11 08:1x (第 13 次刷新 · ★**C 段 35 → 36 (新增 1 条: 板子基线 p41)** "
    "+ ★**播报三条过期待办已当轮订正**★)"
)

NEW_WHAT = (
    "> ★ **本轮我自己动了什么**: ①★**10 分钟播报 (05:10 那轮) 里有 3 条待办全是过期的 ⇒ 我当轮逐条重跑闸订正** "
    "(★**①「v76mx1L 是否晋级」已作废** —— 06:4x 官方对照闸已判 REJECT (退铜 4 网 + 差分死腿 1 对 "
    "`DSI_D0_CK_P_SRC/N_SRC` + 逐网孤岛变多 11 网) ⇒ **唯一可晋级候选是 `candidate_official_p41`** (rc=0 ACCEPT); "
    "★**②「护栏⑨ 注释出处待订正」05:37 就已完成** (`HW/e2e_budget_rk3572.py` md5 `7b820c14` · `--selftest` rc=0 · 10 条护栏全过); "
    "★**③「拍板桶 7 条」实际是 5 条** (ISS-138/ISS-146 你 11-02 就已拍板、main 已验 ⇒ 已移出桶)★ —— "
    "★**⇒ 这三条修在【产生点】: `state/CURRENT_TASK.md` (播报源) 已重写 + `gen_todo.py`/`gen_status_summary.py`/"
    "`gen_start_here.py` 三处「等你拍板」口径统一 (一律排除 `verified`) ⇒ 下一轮播报不会再让你为一块已判死的板做决定**★ "
    "②★**新增 1 个真正要你拍板的项: 官方板是否换成 `candidate_official_p41`** ⇒ 已写进 `state/fragments/pm.yaml` 的 "
    "`needs_from` (★`frag_write.py` 原子写 · 逐条 diff 核过: 只多这一条, 其余一个字节没动★) ⇒ **C 段 35 → 36** "
    "③★**GitHub 发布闸已解开** (真值源 `MEMORY.md:3244` 的微信 openid 已换成占位符 ⇒ 副本被 publish 脚本同步 ⇒ "
    "**真值反查 0 命中 ⇒ 推送成功** `774671f`) ④**没有动任何需要你拍板的东西, 没有发任何邮件, 没有下采购单, "
    "没有改锁死表, 没有写任何总工的分片 (只写 main 自己的 pm.yaml)**。"
    ">   ★ **本轮 C 段口径变化: 35 → 36 项 (1 新增 / 0 移除 / 0 改建议值)** —— ★**新增的那 1 条是板子基线, "
    "当期【不】卡主线 ⇒ 你不必今天回; 但它决定投板时用哪块板 ⇒ 我给了建议默认值, 回一句就行** ★★"
)

NEW_SEC = """## 0.13 ★★★ 本轮: **新增 1 个拍板项 (板子基线 p41)** + ★**播报三条过期待办已订正**⇒ ★**C 段 35 → 36**

> ★**这一节 0.13.1 是【真要你拍板】的那 1 条; 0.13.2 是我这边记账的订正 (不需要你做任何决定)**。

### 0.13.1 ★ 板子基线: 官方板要不要换成 `candidate_official_p41` (★**当期不卡主线, 但它会一直挂在那儿**★)

| | |
|---|---|
| **一句话问题** | ★**官方板 (`md5 611b869e`) 要不要换成 `candidate_official_p41` (`md5 d0f3d75f`)?** |
| **候选是什么** | ★**官方板血脉的【只加不删】增量** —— 官方板原有 18092 段铜**一寸未动**, 只新增 326 段 / 15 个过孔 ⇒ 补回 4 个签名: `JTAG_TDI` · `LIGHT_5V` · `PWR_GOOD` · `SPI_MOSI_BOOT` (★`CSI_D0_D0_P` 没被挤掉, 因为不动已有铜★) |
| **实测三把尺 (★08:0x 我自己重跑, 不是抄上一轮★)** | ★**fresh DRC 0** · ★**unconnected 45条/43网 → 41条/39网** · 零铜网 24→22 · 差分单边零铜 11=11 · 差分Δ超差 3=3 · parity True · ★**`state/compare_arm_official.py` rc=0 · ACCEPT** (退铜名单 0 / 差分死腿 0 / 逐网孤岛变多 0) ★ |
| **★为什么不急 (★关键一句★)** | ★**它也过不了 G1** —— `stage_gate rc=1` ⇒ G1 缺项 = 「PCB 布线未达标: unconnected=45 (需 0)」 ⇒ **换成 p41 是 41, 也不是 0** ⇒ ★**换板 ≠ 能下单** ★ |
| **换板的代价 (★实测过的账★)** | ① **32 处** `md5 611b869e` 引用要改 (含闸门/脚本) ② **留证链全要重跑** (自验 / Gerber / 投产包) ③ **所有臂的 provenance 都要改指** (历史读数的基线漂移) ④ G1 状态要重判 |
| **★我的建议默认值** | ★**「先不换」** —— ① 收益只是 4 个网, 而 G1 反正过不了 ⇒ 现在付固定代价不划算 ② ★**归档 + 配方已留档** (`state/.lastgood/candidate_official_p41.cred.json` + `CANDIDATE_official_p41_ready.md`) ⇒ **真要投板时一次换清, 不会白做** ③ 官方板血脉的增量路线已实测饱和 (四档 margin 全是 41 · 第二轮补 0 条) ⇒ ★**真正的主战场是"把 unc 打到 0", 不是"换不换基线"** ★ |
| **不回的后果** | ★**不卡主线** —— 官方板 `611b869e` 一字未动, G1 仍开, 一切照旧跑; p41 在 `.lastgood/` 归档等着, 不会被任何人动 |
| **★回一句就行 ★** | ★**「先不换」** (我的建议) · **「换」** (我立刻改 32 处引用 + 重跑留证链) · **「先跑完 unc 再一起换」** (同上, 只是时点不同) ★ |

### 0.13.2 ★ 播报三条过期待办的订正 (★不需要你做任何决定★)

| 播报里写的 (05:10) | 实际 (08:0x 实测) |
|---|---|
| ★**①「候选板 v76mx1L 拍板晋级/不晋级」** | ★**已作废** —— `state/compare_arm_official.py` 实测 **rc=1 · REJECT**: 退铜 4 网 (`CARRIER_BOARD_EN`/`DSI_D0_CK_N_SRC`/`SPI_CSn_BOOT`/`USB_CC1`) + ★**差分死腿 1 对** (`DSI_D0_CK_P_SRC/N_SRC`) + 逐网孤岛变多 11 网 ⇒ ★**它 unc 少 (22 vs 43) 是拿差分腿死掉 + 退铜 + 拆碎换来的** ⇒ **不能替换官方板** ★ |
| ★**②「护栏⑨ 注释出处待 main 订正」** | ★**05:37 就已完成** —— `HW/e2e_budget_rk3572.py:248` 注释已指向 `SW/DEMO_OD_TIMING_SPEC.md §3.3.1` + `PROJECT_TRACKER.md:2099` ⇒ md5 `7b820c14acfaee08a218cbf85557ef0b` · `--selftest` rc=0 (护栏 7→10 全过) ⇒ ★**不是待办** ★ |
| ★**③「老板拍板桶 7 条」** | ★**实际 5 条** (ISS-038/041/060/063/106) ⇒ ★**ISS-138 (sensor 选路) + ISS-146 (demo 板形态) 你 11-02 就已拍板、main 已验** ⇒ 已移出桶 ★ |

### 0.13.3 ★ 修在【产生点】, 不在产物上擦 (★下一轮播报不会再说错话★)

| 动作 | 落点 | 实测 |
|---|---|---|
| ★**播报源重写** | ★`state/CURRENT_TASK.md` (★`board_progress.py` 的 `task_head()` 读它★) | ★**只留当前口径 + 4 条待办** ⇒ ★**实测 `task_head()` 现在吐出的就是正确那 4 条** ⇒ ★**旧长台账挪到 `state/CURRENT_TASK_ARCHIVE_2026-11-10.md` (没删)★** |
| ★**"等你拍板"口径统一 (3 处)** | ★`gen_todo.py` / `gen_status_summary.py` / `gen_start_here.py` | ★**一律排除 `verified`** ⇒ ★**B 桶 7 → 5** ⇒ ★**issue_log 真值层一个字节没动** (★`verified` = 老板已拍板 + main 已验, 这个语义本身是对的★) ⇒ ★**实测 diff: 只有那两行 + 三个计数变** ★ |
| ★**新铁律入库** | ★`MEMORY.md` (★两条★) | ★**①「等你拍板」桶必须与真值层的"闭环"口径一致 (★同一个系统里不许有两套"未闭环"★)** ② ★**「要老板拍板的板子」必须在发出去的那一刻重跑闸 (★几小时前的快照会让老板为一块已判死的板做决定★)** ★ |
| ★**GitHub 发布闸解开** | ★`MEMORY.md:3244` 微信 openid → `<wechat-openid>` 占位符 ⇒ 副本被 publish 脚本同步 ⇒ **真值反查 0 命中** | ★**推送成功 `774671f`** ⇒ ★**你的兜底视线 (GitHub) 已恢复且是最新的** ★ |

### 0.13.4 ★ 核验 5 连 (本轮实测 rc)

| 门 | rc | 一句话 |
|---|---|---|
| `merge.py` | **0** | 快照完整 (产出 159 · 阻塞 43 (高危 33) · 未闭合需求 76 · **冲突 0**) |
| `gate_check.py` | **0** | 齐备率 18/18 · 证据分级 3/3 · 接口声明 475 条 |
| `issue_check.py` | **1** | ★**违规 33 条, 全是同一类: 逾期未闭环** (★**不是新造的问题, 是老账**★) |
| `stage_gate.py` | **1** | ★**当前 G1 原理图/PCB 定稿, 还差 1 项进 G2** (★**p41 也过不了 (unc=41≠0) ⇒ 换板 ≠ 能下单**★) |
| `daily_check.py` | **3** | ★**异常已记录 (非崩溃)**: 问题闭环门违规 33 条 (★与 07:5x 同一笔账, 无新增★) |

"""


def replace_line(prefix, new_line, tag, count=1):
    global lines
    hits = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
    if len(hits) != count:
        print(f"❌ {tag}: 前缀匹配到 {len(hits)} 行 (期望 {count})")
        sys.exit(1)
    lines[hits[0]] = new_line
    print(f"✅ {tag} 已替换 (行 {hits[0] + 1})")


def replace_after(anchor_prefix, old_prefix, new_line, tag):
    """在 anchor 行之后的区间里找 old_prefix 行替换 (★避免同名行误伤★)"""
    global lines
    a = None
    for i, ln in enumerate(lines):
        if ln.startswith(anchor_prefix):
            a = i
            break
    if a is None:
        print(f"❌ {tag}: 找不到锚点 {anchor_prefix!r}")
        sys.exit(1)
    for i in range(a, min(a + 40, len(lines))):
        if lines[i].startswith(old_prefix):
            lines[i] = new_line
            print(f"✅ {tag} 已替换 (行 {i + 1})")
            return
    print(f"❌ {tag}: 锚点后找不到 {old_prefix!r}")
    sys.exit(1)


# ---- ① 标题行 ----
if not lines[0].startswith("# 待老板拍板页 · 2026-11-11 07:5x"):
    print(f"❌ 标题行不是预期的 07:5x 版: {lines[0][:80]!r}")
    sys.exit(1)
lines[0] = NEW_TITLE
print("✅ 标题行已替换")

# ---- ② 本轮我动了什么 ----
replace_line("> ★ **本轮我自己动了什么**:", NEW_WHAT, "'本轮我动了什么'")

# ---- ③ 新插 §0.13 (插在 §0.12 之前) ----
anchor = None
for i, ln in enumerate(lines):
    if ln.startswith("## 0.12 "):
        anchor = i
        break
if anchor is None:
    print("❌ 找不到 '## 0.12 ' 锚点")
    sys.exit(1)
lines[anchor:anchor] = NEW_SEC.split("\n")
print(f"✅ §0.13 已插入 (行 {anchor + 1})")

# ---- ④ §0. C 段口径行 ----
replace_line("## 0. ★★ C 段 35 → 35 (0 变化)",
             "## 0. ★★ C 段 35 → 36 (新增 1 条: 板子基线 p41) —— ★**当期卡主线的仍是 3 项, 新增这 1 条不卡主线**",
             "§0 C 段口径行")

# ---- ④ §0. 板子实况块 (★补上"多了一问"★) ----
replace_after("## 0. ★★ C 段 35 → 36", "> ★**板子当前实况",
              "> ★**板子当前实况 (11-11 08:0x 实测)**: 官方板 `md5 611b869e` **一字未动** (mtime 仍 11-06 07:07) · "
              "**unconnected 45 / DRC 0** · `stage_gate rc=1` ⇒ **G1 仍开, 不许投板**。",
              "§0 板子实况行")
replace_after("## 0. ★★ C 段 35 → 36", "> ★**这条线在跑, 缺的是工程动作",
              "> ★**这条线在跑, 缺的是工程动作, 不是你的拍板 —— 你今天不必为它做任何决定** ⇒ "
              "★**唯一新增的一问是「基线要不要换」 (§0.13.1), 我的建议是「先不换」** ★",
              "§0 板子实况结论行")

# ---- ⑤ §1 后新增 §1b (板子基线类) ----
sec1b = """## 1b. ⚪ 板子基线类 (★**当期【不】卡主线, 但它会一直挂在那儿等你**★)

| # | key | 一句话问题 | 建议默认值 (我的口径) | 逾期 | 不拍板的后果 |
|---|---|---|---|---|---|
| **1** | `board_p41_promote` | ★**官方板 (`611b869e`) 要不要换成 `candidate_official_p41` (`d0f3d75f`)?** | ★**「先不换」** (★**p41 过不了 G1 (unc=41≠0) ⇒ 换板 ≠ 能下单**; 归档+配方已留档, 投板时一次换清★) | 无 due | ★**不卡主线** —— 官方板一字未动, 一切照旧跑; p41 在 `.lastgood/` 归档等着不会被任何人动 |

★ **§1 的 3 项 + 本节 1 项 = C 段 36 项 (★其余 32 项属整机/量产阶段 (G2 已于 11-02 19:25 延后) 或方法论 ⇒ 不必今天回★)。**

---
"""
anchor = None
for i, ln in enumerate(lines):
    if ln.startswith("## 2. 🟠 外发类"):
        anchor = i
        break
if anchor is None:
    print("❌ 找不到 '## 2. 🟠 外发类' 锚点")
    sys.exit(1)
lines[anchor:anchor] = sec1b.split("\n")
print(f"✅ §1b 已插入 (行 {anchor + 1})")

# ---- ⑥ §8 一句话汇总 ----
replace_after("## 8. 📌 一句话汇总", "> ★**当期真正卡 demo 板",
              "> ★**当期真正卡 demo 板 → G1 → 可下单的, 只有 3 项** (★**与 11-10 那页完全一致**★)。",
              "§8 首行")
replace_after("## 8. 📌 一句话汇总", "> ★**其余 32 项全部属整机/量产阶段",
              "> ★**新增 1 条 (板子基线 p41, §1b): 当期【不】卡主线 ⇒ 不必今天回; 但它决定投板时用哪块板 ⇒ "
              "★我的建议默认值 = 「先不换」, 回一句就行** ★★",
              "§8 新增说明行")

# ---- ⑦ 附: 逾期分布 ----
replace_after("### 附: 逾期分布", "### 附: 逾期分布",
              "### 附: 逾期分布 (36 项 · 今日实数)",
              "附: 标题行")
replace_after("### 附: 逾期分布", "| 无 due |",
              "| 无 due | 2 | `soc_cost_criterion` · ★`board_p41_promote` (★新项无 due★) |",
              "附: 无 due 行")
replace_after("### 附: 逾期分布", "★ **按来源分",
              "★ **按来源分 (36 项)**: mech 17 · sw 9 · hw 7 · pm 3。",
              "附: 按来源分行")

out = "\n".join(lines)
open(P, "w", encoding="utf-8").write(out)
print(f"✅ 已写回 {P} ({len(out)} 字符)")
