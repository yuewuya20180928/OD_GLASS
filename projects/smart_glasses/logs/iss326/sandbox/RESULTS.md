# ISS-326 · MECH 侧「崩 / 假绿」沙盒实证 · 结果表

> ★**实跑机**: `yuewuya-RedmiBook-14` · Linux 7.0.0-42-generic · Python 3 · 2026-11-18
> ★**铁律**: 判据脚本 + 它读的数据, 整棵树【真拷贝】到 `tmp/iss326/` 再改 ⇒ 真件一个字节不碰
> ★**软链**: 拷贝时 `symlinks=False` + 每文件 `assert not os.path.islink` ⇒ 沙盒内软链数 = 0

| 用例 | 内容 | 期望 | 实际 | 判决 |
|---|---|---|---|---|
| **1A** | ★基线★ 未改名时, 判据脚本的 --selftest 反向用例 ① 应当能抓到 (N2 红) | rc=0 且 反向用例① 判红 | rc=0 · ①行: [OK ] ① 把 S6 目标位 R_SEL_D0_N 挪进 SoM 承载区 ⇒ N2 红: 是 · md5 cb5c2439 ⇒ c488944c (确实改了: True) · N2 错误 2 条 | **✔ 符合期望** |
| **1B** | ★假绿★ 判据脚本里的 `== "R_SEL_D0_N"` 失配 (世界已改名, 脚本没改) ⇒ 判据分支再也匹配不上 | ★期望红不出来 (假绿)★ ⇒ ① 反向用例空转 (N2 红: 否) ★且主判据 N1..N6 仍全绿 ⇒ 缺陷对闸隐形 | 脚本副本字面量改 1 处 · rc=1 · 基线行: [基线] N1=OK N2=OK N3=OK N4=OK N5=OK N6=OK · ①行: [NG ] ① 把 S6 目标位 R_SEL_D0_N 挪进 SoM 承载区 ⇒ N2 红: 否 · md5 cb5c2439 ⇒ 92797a79 (确实改了: True) · N2 错误 0 条 | **✔ 假绿已证实 (判据红不出来, 且主判据仍全绿)** |
| **1C** | ★对照/修复配方★ 字面量与数据同步时, 反向用例 ① 必须能抓到 (⇒ 改名时判据脚本必须一起改) | ★期望 ① 判红 (N2 红: 是)★ | rc=0 · ①行: [OK ] ① 把 S6 目标位 R_SEL_D0_N 挪进 SoM 承载区 ⇒ N2 红: 是 · md5 cb5c2439 ⇒ c488944c (确实改了: True) · N2 错误 2 条 | **✔ 修复配方成立 (字面量同步 ⇒ 能抓)** |
| **1D** | ★反证★ 只改【数据】里的位号 (板不改) ⇒ 必须立刻【响地】红 | ★期望红 (N1/N2 立刻 NG)★ | 数据替换 1 处 · rc=1 · 基线行: [基线] N1=NG N2=NG N3=OK N4=OK N5=OK N6=OK | **✔ 半改必红 (⇒ 假绿只出现在「数据+板同改、脚本漏改」)** |
| **2** | ★崩★ 板上 D_LED_G 改名成 D_LED_G_1 ⇒ `fps[LED_REF]` 必须抛异常 | ★期望红 (抛异常)★ ⇒ KeyError: 'D_LED_G' | 板内改名 1 处 · 默认模式 rc=2 (只红在 md5 闸) · --compute 模式 rc=1 · out["led_space"] = led_space(board, out) ⏎ File "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss326/case2_led_renamed/MECH/check_board_frame_coords.py", line 999, in led_space ⏎ led = fps[LED_REF] ⏎ KeyError: 'D_LED_G' | **✔ 已崩 (异常类型 + 那一行如上)** |
| **3A** | ★只改 186 个改名位号 (32 个不动位号一律不动) ⇒ J_SOM_P1 必须完全不受影响 | ★期望绿 (不动集没被误伤)★ ⇒ 板上 J_SOM_P1 原样在, 且没有 J_SOM 相关异常 | 板上改名 156 处 · 板上 J_SOM_P1 仍在 = True · 无 J_SOM 异常 = True · rc=2 | **✔ 不动集没被误伤** |
| **3B** | ★反证★ 连不动集里的 J_SOM_P1 也改掉 ⇒ 判据必须失配 (证明它确实不该改) | ★期望红 / 判据失配★ ⇒ SoM 焊盘总数 400 → 300, J_SOM_P1 从判据里消失, C3 负向断言判红 | rc=2 (基线 rc=2) · 输出里还有 J_SOM_P1 = False · C3 判红 = True · 【闸】ISS-276 坐标系闸 (C1 帧标签 / C2 不压 SoM / C3 负向断言 / C4 受保护件: 2 件合法改板通道 (ISS-296) + 3 件台账链头) ⏎    窗口 'port_open_debug_bench' (opening) X 137.850..148.050 × Y 54.300..58.900 ⇒ 压住 SoM 焊盘 = **0** {'J_SOM_P2': 0, 'J_SOM_P3': 0, 'J_SOM_P4': 0} ⏎    窗口 'port_open_uart_bench' (opening) X 13.790..23.990 × Y 66.300..70.900 ⇒ 压住 SoM 焊盘 = **0** {'J_SOM_P2': 0, 'J_SOM_P3': 0, 'J_SOM_P4': 0} | **✔ 证实 J_SOM_P1 在不动集里 (改了 ⇒ 判据失配)** |
| **4** | ★注释里的 ref★ 把判据脚本【注释/文档串】里的位号名改成别的 ⇒ 闸必须不受影响 | ★期望绿且输出与基线逐字节相同★ | 改的是 L9: `J_SOM_P1..P4` 焊盘数必须 = 0** · rc 0 → 0 · stdout 完全相同 = True | **✔ 注释里的 ref 无功能影响** |

## 逐条原始读数

### 1A · ★基线★ 未改名时, 判据脚本的 --selftest 反向用例 ① 应当能抓到 (N2 红)

- **期望**: rc=0 且 反向用例① 判红
- **实际**: rc=0 · ①行: [OK ] ① 把 S6 目标位 R_SEL_D0_N 挪进 SoM 承载区 ⇒ N2 红: 是 · md5 cb5c2439 ⇒ c488944c (确实改了: True) · N2 错误 2 条
- **判决**: ✔ 符合期望
- **原始日志**: `logs/iss326/sandbox/case1A_baseline.log`

### 1B · ★假绿★ 判据脚本里的 `== "R_SEL_D0_N"` 失配 (世界已改名, 脚本没改) ⇒ 判据分支再也匹配不上

- **期望**: ★期望红不出来 (假绿)★ ⇒ ① 反向用例空转 (N2 红: 否) ★且主判据 N1..N6 仍全绿 ⇒ 缺陷对闸隐形
- **实际**: 脚本副本字面量改 1 处 · rc=1 · 基线行: [基线] N1=OK N2=OK N3=OK N4=OK N5=OK N6=OK · ①行: [NG ] ① 把 S6 目标位 R_SEL_D0_N 挪进 SoM 承载区 ⇒ N2 红: 否 · md5 cb5c2439 ⇒ 92797a79 (确实改了: True) · N2 错误 0 条
- **判决**: ✔ 假绿已证实 (判据红不出来, 且主判据仍全绿)
- **备注**: 新名 = R_SEL_D0_N_1 · ★主判据仍全绿这一点才是「假绿」的要害: 缺陷存在但闸看不见★
- **原始日志**: `logs/iss326/sandbox/case1B_literal_stale.log`

### 1C · ★对照/修复配方★ 字面量与数据同步时, 反向用例 ① 必须能抓到 (⇒ 改名时判据脚本必须一起改)

- **期望**: ★期望 ① 判红 (N2 红: 是)★
- **实际**: rc=0 · ①行: [OK ] ① 把 S6 目标位 R_SEL_D0_N 挪进 SoM 承载区 ⇒ N2 红: 是 · md5 cb5c2439 ⇒ c488944c (确实改了: True) · N2 错误 2 条
- **判决**: ✔ 修复配方成立 (字面量同步 ⇒ 能抓)
- **原始日志**: `logs/iss326/sandbox/case1C_literal_synced.log`

### 1D · ★反证★ 只改【数据】里的位号 (板不改) ⇒ 必须立刻【响地】红

- **期望**: ★期望红 (N1/N2 立刻 NG)★
- **实际**: 数据替换 1 处 · rc=1 · 基线行: [基线] N1=NG N2=NG N3=OK N4=OK N5=OK N6=OK
- **判决**: ✔ 半改必红 (⇒ 假绿只出现在「数据+板同改、脚本漏改」)
- **原始日志**: `logs/iss326/sandbox/case1D_data_only.log`

### 2 · ★崩★ 板上 D_LED_G 改名成 D_LED_G_1 ⇒ `fps[LED_REF]` 必须抛异常

- **期望**: ★期望红 (抛异常)★ ⇒ KeyError: 'D_LED_G'
- **实际**: 板内改名 1 处 · 默认模式 rc=2 (只红在 md5 闸) · --compute 模式 rc=1 · out["led_space"] = led_space(board, out) ⏎ File "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss326/case2_led_renamed/MECH/check_board_frame_coords.py", line 999, in led_space ⏎ led = fps[LED_REF] ⏎ KeyError: 'D_LED_G'
- **判决**: ✔ 已崩 (异常类型 + 那一行如上)
- **备注**: ★注★ 默认模式 (run_checks) 不走 LED 空间复算 ⇒ 只红在 C4 md5; ★`--compute` 才进 `led_space()` ⇒ 崩在那里★
- **原始日志**: `logs/iss326/sandbox/case2_led_renamed.log`

### 3A · ★只改 186 个改名位号 (32 个不动位号一律不动) ⇒ J_SOM_P1 必须完全不受影响

- **期望**: ★期望绿 (不动集没被误伤)★ ⇒ 板上 J_SOM_P1 原样在, 且没有 J_SOM 相关异常
- **实际**: 板上改名 156 处 · 板上 J_SOM_P1 仍在 = True · 无 J_SOM 异常 = True · rc=2
- **判决**: ✔ 不动集没被误伤
- **原始日志**: `logs/iss326/sandbox/case3A_plan_only.log`

### 3B · ★反证★ 连不动集里的 J_SOM_P1 也改掉 ⇒ 判据必须失配 (证明它确实不该改)

- **期望**: ★期望红 / 判据失配★ ⇒ SoM 焊盘总数 400 → 300, J_SOM_P1 从判据里消失, C3 负向断言判红
- **实际**: rc=2 (基线 rc=2) · 输出里还有 J_SOM_P1 = False · C3 判红 = True · 【闸】ISS-276 坐标系闸 (C1 帧标签 / C2 不压 SoM / C3 负向断言 / C4 受保护件: 2 件合法改板通道 (ISS-296) + 3 件台账链头) ⏎    窗口 'port_open_debug_bench' (opening) X 137.850..148.050 × Y 54.300..58.900 ⇒ 压住 SoM 焊盘 = **0** {'J_SOM_P2': 0, 'J_SOM_P3': 0, 'J_SOM_P4': 0} ⏎    窗口 'port_open_uart_bench' (opening) X 13.790..23.990 × Y 66.300..70.900 ⇒ 压住 SoM 焊盘 = **0** {'J_SOM_P2': 0, 'J_SOM_P3': 0, 'J_SOM_P4': 0}
- **判决**: ✔ 证实 J_SOM_P1 在不动集里 (改了 ⇒ 判据失配)
- **原始日志**: `logs/iss326/sandbox/case3B_keep_broken.log`

### 4 · ★注释里的 ref★ 把判据脚本【注释/文档串】里的位号名改成别的 ⇒ 闸必须不受影响

- **期望**: ★期望绿且输出与基线逐字节相同★
- **实际**: 改的是 L9: `J_SOM_P1..P4` 焊盘数必须 = 0** · rc 0 → 0 · stdout 完全相同 = True
- **判决**: ✔ 注释里的 ref 无功能影响
- **原始日志**: `logs/iss326/sandbox/case4_comment.log`
