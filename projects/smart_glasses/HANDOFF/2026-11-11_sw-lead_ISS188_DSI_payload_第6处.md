# [sw-lead→PM] ISS-188 · DSI payload 8× 口径差 第 6 处 (SW 分片侧) 闭环
- 发起方: sw-lead
- 日期: 2026-11-11
- 单号: ISS-188 (owner=sw-lead / verify_by=main) · ISS-186 的尾巴
- 结论: ★**本文件改了 2 处 (`SW/DEMO_OD_PIPELINE_SPEC.md` 的 **322 + 379**), 不是 1 处** —— 322 是任务书点名的第 6 处, 379 是 main 08:4x 追加授权的**同文件第二处** ⇒ ★**本文件内 373/560 口径已零残留**
- 依据: `HW/e2e_budget_rk3572.py` §⑥ 实打印 `2986.0 Mbps` (@90Hz `4479.0 Mbps`) · 算式 1920×1080×24×60 = 2985.98 Mbps (RGB888 24bpp)

---

## B1 结论摘要

1. ★**改了 2 处, 都在 `SW/DEMO_OD_PIPELINE_SPEC.md` 一个文件里** (机械证明见 §4: 实际改动行号 = `[322, 379]`, 行数 675 → 675 不变):
   - ★**322 (第 6 处, 任务书点名)**: `**373 Mbps payload**` → `**2986 Mbps payload**` · `@90Hz ≈ 560 Mbps` → `@90Hz ≈ 4480 Mbps` · **尾部追加一句依据注** (口径 = 1920×1080×24×60 = 2985.98 Mbps, 与 `HW/e2e_budget_rk3572.py` §⑥ 同口径, TX 物理下限 7.776ms = 2986 ÷ 60 ÷ 6400 就是按这个 payload 算的)
   - ★**379 (第 7 处, main 08:4x 追加授权)**: `373Mbps 是 RGB888 口径` → `2986Mbps 是 RGB888 口径` (只改数字, 问法/结论一个字未动)
2. ★**为什么 379 必须一起改 (不然口径仍然自相矛盾)**: 379 与 322 在**同一份 spec** 里 ⇒ 322 已写 2986、379 还写 373 ⇒ 下一个读它的人照样会拿到错数 ⇒ ★**这正是 ISS-188 标题说的「同一份 spec 里两处口径打架」** ⇒ main 08:4x 复核全仓时发现并追加授权, ★**不是本单擅自扩范围**。
3. ★**口径统一 (机械验收)**: `grep -n '373Mbps\|373 Mbps\|246 Mbps' SW/DEMO_OD_PIPELINE_SPEC.md` ⇒ **rc=1, 零命中**; 扩大到全 `SW/` (两种写法都查) ⇒ **rc=1, 零命中** ⇒ ★**本文件 373/560 口径彻底清零**。
4. ★**与已签字的 5 处同口径 (依据同源, 不是另立门户)**: ①`HW/DISPLAY_MODULE_DECISION.md:53` ②`HW/STEP1_PARTS_SPEC.md:375` ③`HW/DEMO_BOARD_HW_DECISION.md:65` ④`HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md:398` ⑥`state/outbox/visionox_display_inquiry.md:29` (这 5 处由 hw-lead 在 ISS-186 改完并签字) ⇒ ★**6 处全部 = 2986 Mbps / @90Hz 4480 Mbps**。
5. ★**结论方向一个字未改**: 322 行的引用 `HW/DISPLAY_MODULE_DECISION.md` §D3 逐字保留; 379 行的「带宽 ×3」「是 RGB888 口径」逐字保留; ★**本单只订正数字, 不改任何判断** (★**「不需要 DSC」这个结论本来就成立** —— 2986 Mbps 占 4-lane@2.5Gbps raw 10 Gbps 的 29.9%, 占脚本保守口径 6400 Mbps 的 46.7% ⇒ **两种口径都远低于 100%** ⇒ 这是「**数字错 + 依据虚**」, 不是「结论错」)。
6. ★**自证全绿**: `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ **rc=0** (18 条全绿, 含 ⑧TX 已发布值钉死 / ⑨链路参数钉死 / ⑩默认路径带 TX) ⇒ ★**改前改后 stdout 逐字节相同** (diff 实测) ⇒ ★**脚本一个字节没动** (md5 `7b820c14acfaee08a218cbf85557ef0b` 不变) ⇒ ★**它仍是判据的权威来源**。

---

## B2 验收标准自评

| 验收标准 | 自评 | 依据 |
|---|---|---|
| ① `grep -rn '373 Mbps\|246 Mbps' HW/ SW/ state/outbox/ config/ state/_demo_hw_scheme_landing.py` ⇒ 0 命中 | ⚠️ **本单范围内已达成 (SW/ 全清), 全域剩 1 条命中, 在 main 侧** | ★**SW/ = 零命中 (rc=1)**; ★**全域唯一残留 = `state/_demo_hw_scheme_landing.py:11`** (main 新加的口径钉死注释里留着逐字串「373 Mbps」) ⇒ ★**这是 main 侧 1 行的活, 建议改成「原写的 373」** (详见 §7.3 F4) ⇒ ★**注意: `config/agents/main/MEMORY.md:1979` 已被 main 在 08:4x 并行改掉 (现为 2986 Mbps)** |
| ①b ★**main 08:4x 追加的扩条**: `grep -n '373Mbps\|373 Mbps\|246 Mbps' SW/DEMO_OD_PIPELINE_SPEC.md` ⇒ 0 命中 | ✅ **通过** (rc=1) | §6 命令 ② 实录 |
| ② 322 与 `HW/DISPLAY_MODULE_DECISION.md:53` 口径一致 (都是 2986 / 4480) | ✅ **通过** | §5 结构化断言 |
| ③ `python3 HW/e2e_budget_rk3572.py --selftest` ⇒ rc=0 (**不许改那个脚本**) | ✅ **通过** (rc=0, 脚本 md5 改前改后相同, stdout 逐字节相同) | §6 命令 ③ 实录 |
| ④ 不许重跑 `state/_demo_hw_scheme_landing.py` | ✅ **通过** (★**一次都没跑**; md5/mtime 我只读不写) | §7 边界声明 |
| ⑤ 交付报告含 old→new 逐字串 + 自证命令实录 + 边界声明 | ✅ **通过** | §3 / §6 / §7 |
| ⑥ 走 `state/frag_write.py` 原子写 `state/fragments/sw.yaml` | ✅ **通过** (走 `frag_write.py` 原子写, 未手写分片) | §8 |
| ⑦ 只许改 `SW/DEMO_OD_PIPELINE_SPEC.md` (322 + 379) + 1 份 HANDOFF + 自己分片 | ✅ **通过** (见 §7) | §4 md5 对拍 + §7 |

---

## B3 证据分级

| 结论 | 等级 | 说明 |
|---|---|---|
| 1920×1080@60 RGB888 payload = 2985.98 Mbps | **[推算]** | 算式 1920×1080×24×60, 纯算术, 无需外部数据 |
| 1920×1080@90 RGB888 payload = 4478.976 Mbps (取 4480) | **[推算]** | 算式 1920×1080×24×90 |
| §⑥ 打印 `RGB888 payload = 2986.0 Mbps` / `4479.0 Mbps` | **[实测·脚本实跑]** | `python3 HW/e2e_budget_rk3572.py` §⑥ 实跑输出 (§6 命令 ④) |
| TX 物理下限 7.776ms | **[实测·脚本实跑]** | `--selftest` 实打印 `TX_MIN_1080 = 7.776 (须 =7.776)` (护栏⑧ 钉死) |
| 旧值偏小 8.005× (322) | **[推算]** | 2985.98 / 373 = 8.0045 |
| 旧值偏小 8.004× (379) | **[推算]** | 2985.98 / 373 = 8.0045 (同一错值) |
| 「拿旧值反推 TX 下限 ⇒ 7.776ms 塌成 ~0.97ms」 | **[推算]** | 7.776 × 3/24 = 0.972 (sw-lead 实算, hw-lead 独立复算一致) |
| 占用率 29.9% / 46.7% | **[推算]** | 2985.98 / 10000 与 2985.98 / 6400 |
| 面板是否支持 DSC / 单色还是全彩 | **[0数据]** | **本单不碰** (属面板厂书面答复, 走 `state/outbox/visionox_display_inquiry.md` 草稿, 外发一律经老板) |

---

## B4 接口取值声明

| key | value | note |
|---|---|---|
| `dsi_payload_1080p60_rgb888` | `2986 Mbps` | 1920×1080×24×60 = 2985.98 Mbps (RGB888 24bpp); 与 `HW/e2e_budget_rk3572.py` §⑥ 实打印 2986.0 Mbps、`PROJECT_TRACKER.md:2099`、`HW/DISPLAY_MODULE_DECISION.md:53` 同口径; TX 物理下限 7.776ms 即按此 payload 算出 |
| `dsi_payload_1080p90_rgb888` | `4480 Mbps` | 1920×1080×24×90 = 4478.976 Mbps; 脚本 §⑥ 打印 4479.0 (显示取整差 1 Mbps, 口径同源) |

★**登记位置**: 本单把上表登记进**我自己**的分片 `state/fragments/sw.yaml` 的 `interface_claims` (走 `state/frag_write.py` 原子写) ⇒ ★**没碰 `hw.yaml` / `mech.yaml` / `pm.yaml` 一个字节**。
★**与 hw-lead 的交叉确认**: ★**hw-lead 已在 `hw.yaml` 登记了同名同值的 `dsi_payload_1080p60_rgb888` = `2986 Mbps` 与 `dsi_payload_1080p90_rgb888` = `4480 Mbps`** ⇒ ★**本单在 `sw.yaml` 再登记一次 ⇒ 两个 agent 独立给出同一个规范值 ⇒ 合并器不报 conflict (只在值不同时报) ⇒ ★**这就是「口径已统一」的机器可读证据**。

---

## B5 未决项与卡点

1. ★**【本单范围内, 已闭合】** `SW/DEMO_OD_PIPELINE_SPEC.md` 的 2 处 (322 + 379) ⇒ 373/560 口径零残留。
2. ★**【超出本单范围, ★只报, 不顺手改★】全仓仍有 4 处活的旧 payload 数字, 全部不在 sw-lead 分片** ⇒ 详见 §7.3:
   - `HW/STEP1_LANDING_LIST.md:42` ⇒ `1920×1080@60 RGB888 ≈ 373Mbps ⇒ 4-lane 绰绰有余, 不需 DSC` (**hw-lead 分片**, ★**ISS-186 那 5 处的枚举没扫到它, 因为它写的是无空格写法 `373Mbps`**)
   - `HW/PART_ALTERNATIVES_REGISTRY.md:24` ⇒ `DSI 4-lane 够 1920×1080 RGB888 (373Mbps)` (**hw-lead 分片**, 同一漏网原因)
   - `config/agents/main/MEMORY.md:1979` + `config/agents/main/memory/2026-11-02.md:26` ⇒ **main 自己的文件**
   - ★**`state/_demo_hw_scheme_landing.py:11`** ⇒ main 的口径钉死注释里**留着逐字串「373 Mbps」** ⇒ ★**★这条会让验收命令 ① 永远不为 0** (hw-lead 在 ISS-186 踩过同一个坑, 见其报告 §6 ① 第一遍输出) ⇒ ★**修法: 写成「原写的 373」即可 (那是 main 的文件, 我没碰)**
3. ★**【0数据, 本单不碰】** 面板单色/全彩 (决定 TX 下限用 24bpp 还是更低) · 面板 init code / 时序 ⇒ 仍挂在 `demo_od_p0_4_panel_init_code` (waiting_on=boss, 外发一律经老板) ⇒ ★**本单不阻塞 ISS-137 签字, 也不阻塞任何投板动作** (只改 1 个文件里 2 行的数字)。
4. ★**没有卡点** ⇒ 本单随时可由 main 验收签字。

---

## B6 自证复现命令

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses

# ① 任务书原验收 (全域; ★注意 main 侧那两处还在 ⇒ 全域 rc=0, SW/ 部分 rc=1)
grep -rn '373 Mbps\|246 Mbps' HW/ SW/ state/outbox/ config/ state/_demo_hw_scheme_landing.py; echo "rc=$?"

# ①b ★本单范围 (期望 rc=1, 零命中)
grep -rn '373Mbps\|373 Mbps\|246Mbps\|246 Mbps' SW/; echo "rc=$?"

# ② main 08:4x 追加的扩条 (期望 rc=1, 零命中)
grep -n '373Mbps\|373 Mbps\|246 Mbps' SW/DEMO_OD_PIPELINE_SPEC.md; echo "rc=$?"

# ③ 脚本自检 (期望 rc=0; ★不许改这个脚本)
python3 HW/e2e_budget_rk3572.py --selftest; echo "rc=$?"

# ④ §⑥ 实打印 (期望 2986.0 / 4479.0 Mbps)
python3 HW/e2e_budget_rk3572.py | grep -A3 'DSI 带宽核对'

# ⑤ 两处口径对拍 (期望两行都是 2986)
sed -n '322p' SW/DEMO_OD_PIPELINE_SPEC.md; sed -n '53p' HW/DISPLAY_MODULE_DECISION.md

# ⑥ 只动了 2 行的机械证明 (见 §4)
python3 - <<'PY'
import hashlib
p='SW/DEMO_OD_PIPELINE_SPEC.md'; cur=open(p,encoding='utf-8').read()
print('md5 now =', hashlib.md5(cur.encode()).hexdigest())   # 21c910af69a2a6e3b0cc6bda0d7cf68f
PY
```

---

## 1. 本单做了什么 (一句话)

★**只做一件事**: 把 `SW/DEMO_OD_PIPELINE_SPEC.md` 里 **2 行** (322 + 379) 的 DSI payload 旧口径 (373 / 560) 订正成真值 (**2986 / 4480**), 并在 322 行**追加一句依据注** (TX 7.776ms 是按 2986 Mbps 算的) ⇒ ★**结论方向一个字没改, 一个字节都不许多动的约束我守住了**。

## 2. 为什么现在做 (★不是数字洁癖★)

★**ISS-186 (owner=hw-lead) 已于同日 08:3x 验收签字 (pass)**, 它修的是 hw-lead 分片里的 5 处 ⇒ ★**唯独漏掉 SW 分片里的这一处** ⇒ ★**main 不代写别人的分片 (MEMORY.md:3138) ⇒ 为它开了 ISS-188**。
★**为什么它必须补**: 322 行引用的 `HW/DISPLAY_MODULE_DECISION.md` §D3 已改成 2986 ⇒ ★**同一份 spec 里两处口径打架** ⇒ 读 spec 的人拿到 373 ⇒ ★**若有人拿它反推 TX 物理下限, 7.776ms 会塌成 ~0.97ms** ⇒ ★**ISS-137 rev0 那个「显示 TX 从账上消失」的坑会原样回来, 而且更隐蔽**。

## 3. ★old → new 逐字串 (★main 可反查★)

### ① `SW/DEMO_OD_PIPELINE_SPEC.md:322` (★第 6 处, 任务书点名★)

**old (逐字)**:
```
| 带宽 | 1920×1080@60 RGB888 ≈ **373 Mbps payload** (@90Hz ≈ 560 Mbps) | `HW/DISPLAY_MODULE_DECISION.md` §D3 · [推算] |
```
**new (逐字)**:
```
| 带宽 | 1920×1080@60 RGB888 ≈ **2986 Mbps payload** (@90Hz ≈ 4480 Mbps) | `HW/DISPLAY_MODULE_DECISION.md` §D3 · [推算] · ★**依据 (ISS-188 订正)**: payload = 1920×1080×24×60 = 2985.98 Mbps (@90Hz = 1920×1080×24×90 = 4478.98 Mbps ⇒ 取 4480; 脚本 §⑥ 实打 4479.0, 差 1Mbps 纯显示取整, 同真值) ⇒ 与 `HW/e2e_budget_rk3572.py` §⑥ 同口径 (TX 物理下限 7.776ms = 2986 Mbps ÷ 60fps ÷ 6400 Mbps 有效带宽, 即按这个 payload 算) ⇒ 与 `HW/DISPLAY_MODULE_DECISION.md` §2.2 (ISS-186 已订正处) 口径一致 |
```
**数字变化**: `**373 Mbps payload**` → `**2986 Mbps payload**` · `@90Hz ≈ 560 Mbps` → `@90Hz ≈ 4480 Mbps` · ★**`HW/DISPLAY_MODULE_DECISION.md` §D3 引用逐字保留 + `[推算]` 证据等级逐字保留 + 尾部追加依据注** ⇒ ★**其余一字未动**。

### ② `SW/DEMO_OD_PIPELINE_SPEC.md:379` (★第 7 处, main 08:4x 追加授权★)

**old (逐字)**:
```
| plane 格式 | NV12 (若 DSI 链路吃 NV12) 或 RGB888 (带宽 ×3, 373Mbps 是 RGB888 口径) | 同左 |
```
**new (逐字)**:
```
| plane 格式 | NV12 (若 DSI 链路吃 NV12) 或 RGB888 (带宽 ×3, 2986Mbps 是 RGB888 口径) | 同左 |
```
**数字变化**: `373Mbps 是 RGB888 口径` → `2986Mbps 是 RGB888 口径` · ★**「带宽 ×3」「是 RGB888 口径」「同左」逐字保留, 只改数字**。
★**依据**: 与 322 行同源 (payload = 1920×1080×24×60 = 2985.98 Mbps ⇒ 2986 Mbps, 与 `HW/e2e_budget_rk3572.py` §⑥ 同口径) ⇒ ★**这两处现在互相自洽, 也与 `HW/DISPLAY_MODULE_DECISION.md:53` 自洽**。

## 4. ★机械证明「只动了 2 行」 (main 可反查)

★**方法**: 把当前文件按本单 2 处替换**反向还原**成 before, 再与改前 md5 对拍 ⇒ ★**还原结果 md5 = `2fe3be4c55bda369a56a13ef6d00565d` = 我改前记录的 md5 ⇒ 逐字节一致** ⇒ ★**下面的 diff 因此是权威的**.

```
--- before
+++ after
@@ -322 +322 @@
-| 带宽 | 1920×1080@60 RGB888 ≈ **373 Mbps payload** (@90Hz ≈ 560 Mbps) | `HW/DISPLAY_MODULE_DECISION.md` §D3 · [推算] |
+| 带宽 | 1920×1080@60 RGB888 ≈ **2986 Mbps payload** (@90Hz ≈ 4480 Mbps) | `HW/DISPLAY_MODULE_DECISION.md` §D3 · [推算] · ★**依据 (ISS-188 订正)**: ...
@@ -379 +379 @@
-| plane 格式 | NV12 (若 DSI 链路吃 NV12) 或 RGB888 (带宽 ×3, 373Mbps 是 RGB888 口径) | 同左 |
+| plane 格式 | NV12 (若 DSI 链路吃 NV12) 或 RGB888 (带宽 ×3, 2986Mbps 是 RGB888 口径) | 同左 |
```

| 项 | before | after |
|---|---|---|
| `SW/DEMO_OD_PIPELINE_SPEC.md` md5 | `2fe3be4c55bda369a56a13ef6d00565d` | `21c910af69a2a6e3b0cc6bda0d7cf68f` |
| 行数 | 675 | **675 (不变)** |
| 实际改动行号 | — | **`[322, 379]` (改动行数 = 2)** |
| 322 行 `\|` 数 | 4 | **4 (表格结构未坏)** |
| 379 行 `\|` 数 | 4 | **4 (表格结构未坏)** |
| `HW/e2e_budget_rk3572.py` md5 | `7b820c14acfaee08a218cbf85557ef0b` | **`7b820c14acfaee08a218cbf85557ef0b` (未动)** |

## 5. ★结构化口径断言 (替代人工读 diff)

```
[口径] SW:322 与 HW/DISPLAY_MODULE_DECISION.md:53 同为 2986 Mbps   = OK
[口径] SW:322 @90Hz 与 HW:53 @90Hz 同为 4480 Mbps                  = OK
[口径] SW:379 的 RGB888 口径 = 2986 Mbps (与 SW:322 同值)          = OK
[残留] SW/ 内 373Mbps / 373 Mbps / 246 Mbps / 560 Mbps 命中数      = 0
[结构] 行数不变 (675) + 两行 | 数不变 (4/4)                        = OK
[脚本] e2e_budget_rk3572.py md5 改前改后相同                       = OK
★总判定: PASS
```

| 文件:行 | 新值 | 与 `HW/DISPLAY_MODULE_DECISION.md:53` 一致? |
|---|---|---|
| `SW/DEMO_OD_PIPELINE_SPEC.md:322` | `2986 Mbps` / `@90Hz ≈ 4480 Mbps` | ✅ |
| `SW/DEMO_OD_PIPELINE_SPEC.md:379` | `2986Mbps 是 RGB888 口径` | ✅ |
| `HW/DISPLAY_MODULE_DECISION.md:53` (ISS-186 已签字, 本单未碰) | `2986 Mbps` / `@90Hz ≈ 4480 Mbps` | (基准) |
| `HW/e2e_budget_rk3572.py` §⑥ 实跑 (权威来源, 本单未碰) | `2986.0 Mbps` / `4479.0 Mbps` | ✅ |

## 6. ★自证命令实际输出 (逐条粘贴, 不写「已清理」★)

### ① 任务书原验收 grep (★全域; SW/ 已清, 剩余 1 条在 main 侧★)

```
===== grep -rn '373 Mbps|246 Mbps' HW/ SW/ state/outbox/ config/ state/_demo_hw_scheme_landing.py =====
state/_demo_hw_scheme_landing.py:11:# ⇒ ★**所以这里的每一个 payload 数字都必须是对的** ⇒ ★**原来写 373 Mbps (偏小 8.0×)
rc=0
```
★**⇒ `HW/` `SW/` `state/outbox/` 三处 rc=1 零命中 (本单范围内彻底干净); 全域只剩 1 条 = main 落账器里那条新加的口径钉死注释** ⇒ ★**它会让验收 ① 永远不为 0 ⇒ 改成「原写的 373」即可 (main 侧 1 行)**。
★**注 (main 08:4x 并行收尾后的最终快照)**: `config/agents/main/MEMORY.md:1979` 已被 main 改成 **2986 Mbps** ✔ · `state/_demo_hw_scheme_landing.py` 的 3 个 payload 值 (现 31/47/77 行) 已被 main 改成 **2986Mbps** ✔ ⇒ ★**只剩上面那 1 条注释里的逐字串**。

### ①b ★本单范围 grep (★两种写法都查: 带空格 + 不带空格★)

```
===== grep -rn '373Mbps|373 Mbps|246Mbps|246 Mbps|560 Mbps' SW/ =====
rc=1 (1 = 零命中)
```
★**⇒ 整个 `SW/` 目录零命中 ⇒ 本单范围内 373/560 口径彻底清零**。

### ② ★main 08:4x 追加的验收扩条

```
===== grep -n '373Mbps|373 Mbps|246 Mbps' SW/DEMO_OD_PIPELINE_SPEC.md =====
rc=1 (1 = 零命中)
```

### ③ `python3 HW/e2e_budget_rk3572.py --selftest`

```
【自检】复现 sw-lead 已发布数字 (容差 0.6ms)
  ✅ RK3576 yolov5s@640: 模式A 54.98~56.99 (发布 54.98~56.99)
  ✅ RK3576 yolov5s@640: 模式B 67.34 (发布 67.01)
  ✅ RK3576 yolov5n@640: 模式B 50.67 (发布 50.34)
  ✅ 模式A 阈值 S5 ≤ 20.40 (原文 20.33)
【自检】ISS-137 拆分护栏
  ✅ 拆分恒等: 24.67+1.0+3.0+5.0+0.3299999999999983 = 34.00 == T_FIXED 34.00
  ✅ 判据↔算账互逆 @S5=10.0: 输出侧上限 13.400 ⇒ 模式A 60.000000
  ✅ 判据↔算账互逆 @S5=17.39: 输出侧上限 6.010 ⇒ 模式A 60.000000
  ✅ 判据↔算账互逆 @S5=26.085: 输出侧上限 -2.685 ⇒ 模式A 60.000000
  ✅ 判据↔算账互逆 @S5=13.305: 输出侧上限 10.095 ⇒ 模式A 60.000000
  ✅ 代入 800×600 基线 (合成 1.20 + TX 1.80) ⇒ 与旧模型逐位一致 (52.9050 vs 52.9050) ⇒ ★拆分无副作用★
  ✅ TX 在账里: 同一合成值下 加/不加 TX 差 7.776 ms (= TX 物理下限 7.776) ⇒ ★**显示 TX 没被漏掉**★
  ✅ 合成上限 2.319 = 输出侧上限 10.095 − TX 7.776
  ✅ 输出侧线性上界 12.96 > yolov5n 输出侧上限 10.09 ⇒ ★真需要实测才判得了★
  ✅ TX 随像素数比 = 4.3200 (像素比 4.3200) ⇒ ★TX 是按比特随分辨率涨的★
  ✅ TX 已发布值钉死: TX_MIN_800 = 1.800 (须 =1.800) · TX_MIN_1080 = 7.776 (须 =7.776) ⇒ ★**物理下限不许被悄悄改小**★
  ✅ 链路参数钉死: 4-lane @ 2.0 Gbps × 0.8 有效 (须 = 4-lane@2.0Gbps×0.8) ⇒ ★**带宽不许被悄悄加倍**★
  ✅ 默认路径带 TX: modeA_with_compose(13.305, 2.0) = 59.6810 须 == 显式传 TX 的 59.6810 ⇒ ★**默认值不许把 TX 踢掉**★

✅ 自检通过
rc=0
```
★**⇒ 改前 stdout 与改后 stdout `diff` 逐字节相同 (实测) ⇒ ★**脚本一个字节没动, 它仍是判据的权威来源**。

### ④ §⑥ 实打印 (payload 口径权威来源)

```
⑥ DSI 带宽核对 (1920×1080 显示输出)
====================================================================================================
   25 fps: RGB888 payload =  1244.2 Mbps  | 4-lane D-PHY@2.0Gbps 够? ✅  (假设 2.0Gbps/lane, 按 80% 效率留余量)
   60 fps: RGB888 payload =  2986.0 Mbps  | 4-lane D-PHY@2.0Gbps 够? ✅  (假设 2.0Gbps/lane, 按 80% 效率留余量)
   90 fps: RGB888 payload =  4479.0 Mbps  | 4-lane D-PHY@2.0Gbps 够? ✅  (假设 2.0Gbps/lane, 按 80% 效率留余量)
```

### ⑤ 两处口径对拍

```
| 带宽 | 1920×1080@60 RGB888 ≈ **2986 Mbps payload** (@90Hz ≈ 4480 Mbps) | `HW/DISPLAY_MODULE_DECISION.md` §D3 · [推算] · ★**依据 (ISS-188 订正)**: ...
| **DSI 带宽** | 1920×1080@60 RGB888 ≈ **2986 Mbps** payload; @90Hz ≈ 4480 Mbps | 4-lane D-PHY 2.5Gbps **够** ⇒ 不强制要 DSC ⇒ ... · ★**依据 (ISS-186 订正)**: ...
```

## 7. ★边界声明 (逐条自查)

### 7.1 我动了什么 (全清单)

| 文件 | 动作 | 说明 |
|---|---|---|
| `SW/DEMO_OD_PIPELINE_SPEC.md` | ★**改 2 行** (322 + 379) | 本单唯一被改的交付物; md5 `2fe3be4c…` → `21c910af…`; 行数 675 不变 |
| `HANDOFF/2026-11-11_sw-lead_ISS188_DSI_payload_第6处.md` | 新建 | 本报告 |
| `state/fragments/sw.yaml` | 走 `state/frag_write.py` 原子写 | 登记 interface_claims + artifact + status + 2 条 needs_from (见 §8) |

### 7.2 我**没有**动什么 (逐条自查)

| 禁项 | 自查 |
|---|---|
| ★**不许碰 hw-lead 的分片** (ISS-186 已签字的 5 处) | ✅ **一个字节没碰** (`HW/DISPLAY_MODULE_DECISION.md` / `HW/STEP1_PARTS_SPEC.md` / `HW/DEMO_BOARD_HW_DECISION.md` / `HW/PCB/WAVESHARE_2P8_INIT_AND_BACKLIGHT.md` / `state/outbox/visionox_display_inquiry.md` / `state/fragments/hw.yaml` 全部只读) |
| ★**不许碰 mech-lead / main 的分片** | ✅ **一个字节没碰** (`state/fragments/mech.yaml` / `state/fragments/pm.yaml` / `config/agents/main/MEMORY.md` / `state/_demo_hw_scheme_landing.py` 全部只读) |
| ★**不许改 `PROJECT_TRACKER.md §0` 锁死表** | ✅ **整个 `PROJECT_TRACKER.md` 我只读了一次都没写** (§0 = 第 28~91 行, 全文未动) |
| ★**不许发邮件 / 外发** | ✅ **没发任何邮件、没动 `state/outbox/`** (询价函仍是草稿, 外发一律经老板) |
| ★**不许碰任何板子相关文件** | ✅ **一个字节没碰** (`demo_mainboard.kicad_pcb` / `gen_pcb_*.py` / `state/.lastgood/` / `/tmp` 链产物 全未触碰) |
| ★**不许重跑 `state/_demo_hw_scheme_landing.py`** | ✅ **一次都没跑** (只 `sed`/`grep` 读了它) ⇒ ★**没有把任何旧数灌回 tracker** |
| ★**不许改 `HW/e2e_budget_rk3572.py`** (判据权威来源) | ✅ **md5 改前改后相同** (`7b820c14acfaee08a218cbf85557ef0b`), stdout 逐字节相同 |
| ★**不许把 `state/issue_log.yaml` 的 ISS-188 状态自己落了** | ✅ **没落** (本单输出只列了 ①文件 ②报告 ③分片三样 ⇒ ISS-188 的 `status`/`verify_result` 留给 main 落账) ⇒ ★**如实报出, 不假装已签** |

### 7.3 ★超出本单范围的发现 (★只报, 不顺手改★ —— 这些都不在我的分片)

★**这是本单最有价值的副产物: 任务书的验收 grep 只查「带空格」写法, 漏掉了「不带空格」写法 ⇒ 全仓还有 4 处活的旧 payload 数字**:

| # | 位置 | 内容 | 归属 | 我的判断 |
|---|---|---|---|---|
| F1 | `HW/STEP1_LANDING_LIST.md:42` | `1920×1080@60 RGB888 ≈ 373Mbps ⇒ 4-lane 绰绰有余, 不需 DSC` | ★**hw-lead 分片** | ★**ISS-186 的 5 处枚举没扫到它 (它写的是无空格写法 `373Mbps`) ⇒ 建议 hw-lead 补改 1 行** |
| F2 | `HW/PART_ALTERNATIVES_REGISTRY.md:24` | `DSI 4-lane 够 1920×1080 RGB888 (373Mbps)` | ★**hw-lead 分片** | ★**同一漏网原因 ⇒ 建议 hw-lead 补改 1 行** |
| F3 | `config/agents/main/memory/2026-11-02.md:26` | `4-lane DSI, 373Mbps ⇒ 不需 DSC` | ★**main 自己的文件** | ★**main 收尾时自己改** (★同文件的 `config/agents/main/MEMORY.md:1979` **已被 main 在 08:4x 改成 2986 Mbps** ✔ ⇒ ★**只剩这一条 daily memory 里的**)|
| F4 | ★**`state/_demo_hw_scheme_landing.py:11`** | main 的口径钉死注释里留了**逐字串「373 Mbps」** | ★**main 的文件** | ★**★这条会让验收命令 ① 永远不为 0 ⇒ hw-lead 在 ISS-186 踩过同一个坑 (其报告 §6 ① 第一遍输出) ⇒ 修法: 写成「原写的 373」即可** |

★**我已把 F1/F2 (to=hw-lead) 与 F3/F4 (to=main) 各登记成一条 `needs_from` 进我自己的分片** ⇒ ★**按 STATE 协议, 需求由被问的那一方回答才算闭合 ⇒ 我不代答、不代改**。

## 8. ★分片登记 (走 `state/frag_write.py` 原子写)

| 动作 | 内容 |
|---|---|
| `--add-claim` | `dsi_payload_1080p60_rgb888` = `2986 Mbps` (★**与 hw-lead 在 `hw.yaml` 的登记同名同值 ⇒ 交叉确认, 合并器不报 conflict**) |
| `--add-claim` | `dsi_payload_1080p90_rgb888` = `4480 Mbps` (同上, 与 hw-lead 同名同值) |
| `--add-artifact` | `HANDOFF/2026-11-11_sw-lead_ISS188_DSI_payload_第6处.md` (kind=handoff) |
| `--add-need` | `iss188_dsi_payload_nospace_sweep` → to=hw-lead (F1/F2 两处无空格写法 373Mbps) |
| `--add-need` | `iss188_dsi_payload_main_side_grep_dirty` → to=main (F3/F4; ★其中 F4 会让验收 ① 不为 0) |
| `--status` | phase / progress_pct / health **不变**, summary 追加一句「ISS-188 第 6+7 处已闭环」 |

★**未碰 `hw.yaml` / `mech.yaml` / `pm.yaml`** ⇒ ★**没代写别人的分片**。

---

★**一句话交卷**: ★**`SW/DEMO_OD_PIPELINE_SPEC.md` 改了 2 处 (322 + 379), 不是 1 处** —— 322 的 373/560 → 2986/4480 (附 TX 7.776ms 依据注), 379 的 `373Mbps 是 RGB888 口径` → `2986Mbps 是 RGB888 口径`; ★**全 `SW/` 目录 373/560 口径零残留 (rc=1)**, ★**`HW/e2e_budget_rk3572.py --selftest` rc=0 且脚本 md5 未变**, ★**另如实报出 4 处不属于我分片的残留 (其中落账器注释那条会让验收 grep ① 不为 0, 请 main 顺手把「373 Mbps」写成「原写的 373」)**。
