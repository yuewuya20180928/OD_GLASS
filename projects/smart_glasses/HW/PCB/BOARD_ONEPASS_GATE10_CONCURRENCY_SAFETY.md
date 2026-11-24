# 钉板闸⑩ 并发安全真相页 — 「板那一趟不许开工」这条结论曾经是假的

> ★**本页是 ISS-395 的真相页 (hw-lead · 2026-11-24)★**
> ★**结论一句话**: ★**「板 md5 / 落表链 / 结构真值 漂移 ⇒ 板那一趟不许开工」这条结论, 在 2026-11-24 15:2x 之前【是假的】—— 那次闸红是【并发假红】, 不是板漂移 ★★
> ★**本单性质**: ★**纯分析 + 新建真相页 + 新建机器闸 ⇒ 零写板 · 零落表 · 零改既有闸判据/阈值** ★*

---

## §1 事实链 (★逐条可复现 · ★证据分级已标★)

### §1.1 症状 (★`[实测]`·main 本机实跑 2026-11-24 15:2x★)

`state/gate_check.py` 的 ★**Q7 钉板 md5 闸链第 ⑩ 道**★ (`HW/check_preflight_regen_idempotent.py`, ★"板侧项全集重跑幂等闸"★) ★**rc=1**★ ⇒ 闸链据此判定 ★**「板 md5 / 落表链 / 结构真值 出现漂移 ⇒ 板那一趟不许开工」**★。

★**但闸脚本自己的失败行没解析出来, 只余一段 traceback 尾巴**★:

```
OSError: [Errno 39] Directory not empty: '.../tmp/iss349/regen_gate/regen/state'
```

★**注意这句话里【没有「板 md5 变了」这层意思】—— 它说的是【沙盒目录删不掉】★ ★

### §1.2 根因 (★`[实测]`·main 本机实读源码 + 实跑定位·★不是猜★)

- ★**L60 逐字**: `SANDBOX = os.environ.get("PREFLIGHT_SANDBOX") or os.path.join(PROJ, "tmp", "iss349", "regen_gate")` ⇒ ★**落点写死** ★
- ★**L136 逐字**: `shutil.rmtree(dst)` ⇒ ★**在【另一个进程正往同一个 dst 里写】时必抛 `Errno 39` (目录非空)** ★

★**⇒ 这道闸【不是并发安全】的 ⇒ 只要两个 gate_check 同时跑, 必有一个假红 ★**

### §1.3 为什么【必撞】不是【可能撞】 (★`[实测]`·main 本机实读 `state/daily_check.py`★)

- `state/daily_check.py` ★**L317 逐字**: `rc_g, gate = jrun("gate_check.py")` ⇒ ★**巡检链内部自己会再跑一遍 gate_check** ★
- ⇒ ★**「每日巡检」与「继续执行后继计划」两个 cron job 同分钟各跑一次 ⇒ 必撞** ★

### §1.4 板面零漂移 (★`[实测]`·隔离复跑 rc=0★)

用 `PREFLIGHT_SANDBOX` 指向独占路径隔离复跑 ⇒ ★**rc=0**★ ⇒ 末行逐字:

```
✅ rc=0: ★★页与生成器同源 · 重跑零差异 · 来源全在册 · 必需项在场 ★★
```

★**⇒ 板面零漂移 ⇒ 那天判红的不是板, 是【并发】★ · 留证: `logs/main_r87_gate10_isolated.log` ★**

### §1.5 板三项基线 (★`[实测]`·全程逐字不变★)

| 项 | 值 |
|---|---|
| 板 md5 | `611b869e13518c3c023fb178f91a0075` |
| 板 mtime | `2026-11-06 07:07:17.362193413` |
| 板 size | `4940213` |

---

## §2 机器可判判据 (★新闸 `HW/check_gate10_concurrency_safety.py`★)

| 判据 | 判什么 | 判红条件 |
|---|---|---|
| ★**K1**★ | ★**并发两跑 ⇒ 两个进程都 rc=0** ★ | 任一进程 rc≠0 · 或输出含 `Traceback` / `Errno 39` / `OSError` |
| ★**K2**★ | ★**沙盒落点每次运行唯一** ★ | 两个进程解析出的落点相同 · 或落点不在基目录下 |
| ★**K3**★ | ★**同一路径被第二个进程 rmtree 时不许抛未捕获异常** ★ | 任一进程抛未捕获异常 / 非 0 退出 |
| ★**K4**★ | ★**板三项零扰动** ★ | 跑前跑后 md5 / mtime / size 任一变化 · 或偏离 §1.5 基线 |
| ★**K5**★ | ★**真漂移仍然判红 (★不许把「红」改成「绿」★)** ★ | 沙盒里改坏一个真源后, 闸 **rc≠1** ⇒ 判红 |

★**退出码**: 0 = 全过 · 1 = 有不通过项 (★闸红★) · 2 = 用法错 · 3 = ★闸崩 (★与「闸红」严格区分★) ★
★**用法**: `python3 HW/check_gate10_concurrency_safety.py` · `python3 HW/check_gate10_concurrency_safety.py --selftest`

---

## §3 反向用例 (★`--selftest`★)

| 用例 | 证明什么 |
|---|---|
| ★**S1**★ | ★**把落点唯一化拆掉 (★还原成写死固定路径★) ⇒ 唯一性判据必须判红** ★ |
| ★**S2**★ | ★**朴素 `shutil.rmtree` 在并发写压力下必抛 `Errno 39` ⇒ 防御层是真有牙齿的** ★ |
| ★**S3**★ | ★**真漂移 ⇒ 闸必须红 (★K5 反向★)** ★ |
| ★**S4**★ | ★**板指纹比对器在「板被改」时必须判红 (★只动沙盒副本, 不动真板★)** ★ |

---

## §4 边界 (★照抄任务书·★零放宽★)

★**零写板 · 零落表 · 零改既有闸的判据/阈值**★ ⇒ ★**对 `HW/check_preflight_regen_idempotent.py` 只做了两类改动: ①【落点唯一化】②【rmtree 防御】—— 判据 C1~C4 / REQUIRED_ITEMS / 覆盖度闸 一字未改** ★
★**零改既有页面正文 · 零挂链 (★挂不挂 `state/gate_check.py` 是 main 的地界★) · 零外发 · 不代拍 · 未自签 `state/issue_log.yaml` · 只写 `state/fragments/hw.yaml`** ★
★**沙盒只落 `tmp/iss395_sbx/` + `logs/iss395/` (★不落系统 `/tmp`★)** ★

---

## §5 复现命令 (★逐条见交卷页 §B6★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
PREFLIGHT_SANDBOX=$PWD/tmp/iss395_sbx/ctl python3 -B HW/check_preflight_regen_idempotent.py
python3 -B HW/check_gate10_concurrency_safety.py
python3 -B HW/check_gate10_concurrency_safety.py --selftest
python3 state/merge.py && python3 state/gate_check.py
md5sum HW/PCB/demo_mainboard.kicad_pcb
```
