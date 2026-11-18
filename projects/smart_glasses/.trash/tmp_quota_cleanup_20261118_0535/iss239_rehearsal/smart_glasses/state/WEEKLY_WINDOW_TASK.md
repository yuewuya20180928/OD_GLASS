# ARS45 周交付窗口 · 三个总工统一任务书

> 版本: 2026-11-06 (周五) · 派发方: 项目总工 (main / moli)
> 适用: hw-lead / sw-lead / mech-lead · 每个 agent 在本窗口**只开这一个写会话**

---

## 0. 先对齐状态 (动笔前必做, 两条命令)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py --for <你的 agentId>        # 谁在等我 / 我欠谁 / 有没有冲突
python3 state/frag_write.py --show --agent <你的 agentId>   # 我自己分片现在长什么样
```

★`merge.py --for` 的结果里已经有的答案**不要重复写**; 你要问的事先确认 STATE.yaml 里真的没有。

---

## 1. 更新自己的分片 (原子写)

**唯一合法写入口**: `python3 state/frag_write.py --agent <你的 agentId> ...`

```bash
# ① 状态: phase / progress_pct / health / summary
python3 state/frag_write.py --agent <id> \
  --status 'phase=<阶段> progress_pct=<0-100> health=<green|yellow|red> summary="<一句话结论>"'

# ② 本周新增的 answers (回答别人给的 key)
python3 state/frag_write.py --agent <id> \
  --add-answer 'key=<对方的need key> to=<对方id> value="<结论>" ref=<产出文件/章节>'

# ③ 新增或变更的 interface_claims (接口取值)
python3 state/frag_write.py --agent <id> \
  --add-claim 'key=<接口键> value="<规范短值>" note="<一句话>"'
#   ★改值前先 --show 看旧值; 同一 key 不同值 = conflict, 合并器会自动暴露

# ④ 需要别人配合的 needs_from
python3 state/frag_write.py --agent <id> \
  --add-need 'key=<你的need键> to=<对方id> item="<要对方做什么>" since=2026-11-06 due=<YYYY-MM-DD>'
#   ★waiting_on + due 必填: to=别人 ⇒ 隐含 waiting_on=对方; to=main ⇒ waiting_on=老板/外部, 写清楚

# ⑤ 本周新增产出
python3 state/frag_write.py --agent <id> \
  --add-artifact 'path=<相对项目库的路径> summary="<一句话>" kind=<文档|代码|数据|测试>'
```

### 写分片铁律
- ★★**禁止 `open(path, "w")` 直接覆盖** —— 并发下合并器读到半截 ⇒ **整个域从快照里静默消失**
  (10-25 压测实测 99.6% 概率)。只走 `frag_write.py`。
- 只改**你自己**那一个分片 (`state/fragments/<你的id>.yaml`)。
- 不碰别人的分片 (`sw.yaml` / `mech.yaml` / `hw.yaml` / `pm.yaml`)。
- 不碰 `STATE.yaml` (合并产物, 下次 merge 会被覆盖)。
- 不碰 `PROJECT_TRACKER.md` 的"已锁死的变量"表 (那是项目总工的权限)。
- 接口值写**规范短值**, 不写长段落 (冲突判定按值比对, 长文本永远冲突)。
- `progress_pct` 和 `summary` 要反映**本周真实进展**, 不许灌水。

---

## 2. 更新 issue_log.yaml 里 owner == 你的 issue

- 写一个你自己的脚本 (例: `state/_close_issues_week_20261106.py`)
- ★**必须**: `flock` (`state/.issue_log.lock`) + **锁内重读** + **原子写** (tmp + fsync + `os.replace`),
  写完核对条数与体积。参考实现: `state/_close_iss120_20261101.py`
- 每条改动填:
  - `status`: `open` → `fixing` → `fixed`
  - `fix_ref`: 指向你的产出 (文件路径 + 章节)
  - `verify_by`: ★★**必须**是**另一个总工或 main**, **不许自己验自己** (verify_by ≠ owner)
  - `verify_result` / `verify_date`: **只能由 verify_by 那一侧写** ⇒ 你写 `fixed` 时这两个留空
- ★你**只能**改 `owner == 你的 agentId` 的 issue; 别人的 issue **一行都不许碰**。
- 逾期 (due < 今天) 且仍 `open`/`fixing` 的: 要么本周关掉, 要么写清**为什么关不掉** + **新的 due**。

---

## 3. 交接单 (B1-B6 结构保持不变)

写到 **`HANDOFF/2026-11-06_<你的 agentId>_周更新.md`** (新建文件; **不要改上周的文件**)

沿用 `HANDOFF/README.md` 的 v2 模板, **六块一个都不能缺**:

| 块 | 内容 |
|---|---|
| **B1 结论摘要** | 3-5 条, 每条带数字 |
| **B2 验收标准自评** | 逐条 ✅通过 / ❌不通过 / ⚠️未验 + 依据章节号 |
| **B3 证据分级** | 每条关键结论标 `[实测]` / `[官方]` / `[推算]` / `[0数据]` |
| **B4 接口取值声明** | 跨模块接口取值 (同时登记进自己分片 interface_claims) |
| **B5 未决项与卡点** | 需要谁回答什么 + 期望时限; 外部对象写明走谁 |
| **B6 自证复现命令** | 别人能**一条命令**复现你的关键数字 |

末尾追加本周进展小节 (沿用上周体例):
`§ 本周新增 needs` / `§ 本周新增产出` / `§ blockers 变化` / `§ 边界声明 (改了什么 · 没改什么)`

★拿不到的数据标 `[0数据]`, **不要编**。

---

## 4. 交付前自证 (数字必须贴进回复)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
python3 state/merge.py        # ★★rc 必须 = 0 (rc=2 = 快照不完整, 别交)
python3 state/gate_check.py   # ★贴关键行
```

★merge rc ≠ 0 = 没写对, 别交, 回去查自己那个分片。

---

## 5. 回执格式 (★只回 5 行以内; 超过 = 没干完)

```
status: <phase> / <progress_pct>% / <health>
answers 新增: N 条 (<key 列表>)
claims 总数: N
未闭环 issue: N (逾期 M)
merge rc: 0
```

---

## 6. 本窗口纪律

- ★**三个总工之间不做直接沟通** (老板 10-25 硬规则)。要跟别人对齐 ⇒ 写 `needs_from` 或写进交接单的"接口请求",
  由项目总工转达。**不要**用 `sessions_send` / `openclaw agent --agent` 找对方 (今天已把守卫下沉到 CLI 入口,
  跨 agent 呼叫会 exit 126)。
- ★本窗口**你是唯一写会话** ⇒ 不要另开写会话去改分片 (两个写会话会互相覆盖, last-writer-wins 丢更新)。
- 不发对外邮件 / 不联系供应商 / 不下采购单 / 不放行 RFQ。
- 不做窗口外的临时活 —— 这一轮只交周更新。
