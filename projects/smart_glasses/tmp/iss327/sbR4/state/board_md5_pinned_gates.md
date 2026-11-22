# ★全仓「钉着板 md5」的闸清单 ★ (★机器生成 · main 2026-11-17 18:3x·★数据来自真扫全仓, 不许手写★)

> ★**为什么要这张表**: ★**「板只改一次」那一趟 (S1~S13) 合法改板当天, 下面这 9 道闸会同时红** ★
> ⇒ ★**而这些红的真实含义是「板被换了」, 不是「板改坏了」** ⇒ ⇒ ★**现场的人极可能误读成后者 ⇒ 去改板凑绿 ⇒ 板 md5 变第二次 ⇒ 整趟白跑** ★
> ⇒ ★**所以: 板那一趟开工前, 每道钉板 md5 的闸都必须先有【合法改板】通道 (照 ISS-284 的 `reboard` 原子映射形状)** ★
> ⇒ ★**判据不许松**: 通道只允许【有落表台账背书的合法改板】走绿; ★**盘上 ≠ 基线且无合法记录 ⇒ 仍红** ★

## ★清单 (★共 9 处 · ★其中**已建通道 (代码级)** 9 处 · **仍缺通道** 0 处 · (★其中**纯硬钉** 1 处 = 板 md5 写死·连台账口径都没有·优先级最高★)

> ★★**「已建通道」是【代码级】判据 (★文件里能读到 reboard 通道实现★) ⇒ 【不等于】功能已绿★** ★
> ⇒ ★**功能状态必须实跑出来看 rc** ★ (★★下面这 9 道 + `--selftest` 全跑一遍★ ★别看本表就以为齐了★★):
> ```bash
> python3 HW/check_fsin_rootcause.py ; echo "rc=$?"          # ★期望 rc=0★
> python3 HW/check_g1a7_selection_landed.py ; echo "rc=$?"          # ★期望 rc=0★
> python3 HW/check_onepass_commit_order.py ; echo "rc=$?"          # ★期望 rc=0★
> python3 HW/check_onepass_preflight_coverage.py ; echo "rc=$?"          # ★期望 rc=0★
> python3 HW/check_pin_function_labels.py ; echo "rc=$?"          # ★期望 rc=0★
> python3 HW/check_workpack_state_values.py ; echo "rc=$?"          # ★期望 rc=0★
> python3 MECH/check_board_frame_coords.py ; echo "rc=$?"          # ★期望 rc=0★
> python3 MECH/check_demo_struct_truth.py ; echo "rc=$?"          # ★期望 rc=0★
> python3 SW/tools/check_onepass_sw_sync.py ; echo "rc=$?"          # ★期望 rc=0★
> ```
> ★★**判据口径 (★不许松★)**: 「代码级已建通道」只说明【合法改板那天这道闸不会无脑红】 ⇒
> ⇒ ★**真绿还要看两件事: ① 该闸主跑 rc=0 ② 该闸 `--selftest` rc=0 (★反向用例全抓到★)** ★

| # | 闸文件 | 钉法 | 命中行 | 已有台账口径? | 状态 |
|---|---|---|---|---|---|
| 1 | `HW/check_fsin_rootcause.py` | 1 处 | L78: `"pcb": "611b869e13518c3c023fb178f91a0075",` | ★已有 reboard 通道★ | ★**已建通道** ★ |
| 2 | `HW/check_g1a7_selection_landed.py` | 1 处 | L97: `BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"` | ★已有 reboard 通道★ | ★**已建通道** ★ |
| 3 | `HW/check_onepass_commit_order.py` | 6 处 | L103: `"板":       "611b869e13518c3c023fb178f91a0075",`<br>L505: `bl = ["baseline_md5: 611b869e13518c3c023fb178f91a0075",`<br>L593: `["| ISS-266 | 611b869e13518c3c023fb178f91a0075 | aaaabbbbccccddddeeeeffff00001111 | 1 | 2026-11-17 |",`<br>L604: `["| ISS-266 | 611b869e13518c3c023fb178f91a0075 | %s | 1 | 2026-11-17 |" % newmd5], []))` | ★已有 reboard 通道★ | ★**已建通道** ★ |
| 4 | `HW/check_onepass_preflight_coverage.py` | 1 处 | L62: `"611b869e13518c3c023fb178f91a0075",` | ★已有 reboard 通道★ | ★**已建通道** ★ |
| 5 | `HW/check_pin_function_labels.py` | 1 处 | L148: `"HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",` | ★已有 reboard 通道★ | ★**已建通道** ★ |
| 6 | `HW/check_workpack_state_values.py` | 1 处 | L64: `"611b869e13518c3c023fb178f91a0075"),` | ★已有 reboard 通道★ | ★**已建通道** ★ |
| 7 | `MECH/check_board_frame_coords.py` | 1 处 | L110: `os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"): "611b869e13518c3c023fb178f91a0075",` | ★已有 reboard 通道★ | ★**已建通道** ★ |
| 8 | `MECH/check_demo_struct_truth.py` | 1 处 | L81: `"HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",` | ★已有 reboard 通道★ | ★**已建通道** ★ |
| 9 | `SW/tools/check_onepass_sw_sync.py` | 4 处 | L107: `"HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",`<br>L758: `"611b869e13518c3c023fb178f91a0075", "611b869e13518c3c023fb178f91a0076")`<br>L781: `assert "611b869e13518c3c023fb178f91a0075" in t`<br>L783: `f.write(t.replace("md5: 611b869e13518c3c023fb178f91a0075",` | ★已有 reboard 通道★ | ★**已建通道** ★ |

## ★两侧的活怎么分 (★归口★)

| 域 | 闸 | 单号 |
|---|---|---|
| `HW` | `HW/check_fsin_rootcause.py` | ★**hw-lead** ★ (★已有 reboard 通道★) |
| `HW` | `HW/check_g1a7_selection_landed.py` | ★**hw-lead** ★ (★已有 reboard 通道★) |
| `HW` | `HW/check_onepass_commit_order.py` | ★**hw-lead** ★ (★已有 reboard 通道★) |
| `HW` | `HW/check_onepass_preflight_coverage.py` | ★**hw-lead** ★ (★已有 reboard 通道★) |
| `HW` | `HW/check_pin_function_labels.py` | ★**hw-lead** ★ (★已有 reboard 通道★) |
| `HW` | `HW/check_workpack_state_values.py` | ★**hw-lead** ★ (★已有 reboard 通道★) |
| `MECH` | `MECH/check_board_frame_coords.py` | ★**mech-lead** ★ (★已有 reboard 通道★) |
| `MECH` | `MECH/check_demo_struct_truth.py` | ★**mech-lead** ★ (★已有 reboard 通道★) |
| `SW` | `SW/tools/check_onepass_sw_sync.py` | ★**sw-lead** ★ (★已有 reboard 通道★) |

## ★「合法改板」通道的形状 (★照 ISS-284 已跑通的口径, 不许自创★)

```
reboard: null                     # 还没发生过合法改板 ⇒ 纯 md5 硬保护 (盘上 ≠ 基线 ⇒ 红)
reboard: {by: <单号>, file: <文件名>, prev_md5: <改前>, md5: <改后>}
                                   # ★一个原子映射: 四项缺一 ⇒ 整条记录无效 ⇒ 红★
                                   # ★且四项必须能在落表台账里查到 (单号 + 文件名 + 新旧 md5)★
                                   # ★判据方向不许变: 盘上 ≠ 链头 ⇒ 红 (合法改板只让链头前移)★
                                   # ★fail-closed 三条一条不许动: 链头不唯一 / 链断 / 链头无单号 ⇒ 红★
```

## ★复现命令 (★main 18:3x 实跑, 原样★)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
grep -rln '611b869e13518c3c023fb178f91a0075' --include='*.py' . | grep -v -E '__pycache__|\.bak|/logs/|/tmp/|\.lastgood' | sort
```

> ★**本表的生成脚本**: `state/_gen_board_md5_pinned_gates.py` (★改闸清单后重跑一次即可刷新★) ★
>
> ★**★口径已被证明可行 (★不是猜的★)**: `SW/tools/check_demo_panel_spec.py` ★**在 ISS-284 转成台账口径后, 它已经不再硬钉板 md5 ⇒ 本清单里根本找不到它** ★
> ⇒ ★**⇒ 「不硬钉」不是靠把断言删掉, 是靠判决源换成【落表台账 + reboard 记录】** ★
