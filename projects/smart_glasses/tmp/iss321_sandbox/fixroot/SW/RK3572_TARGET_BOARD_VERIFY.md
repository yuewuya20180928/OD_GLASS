# SW/RK3572_TARGET_BOARD_VERIFY.md — rk3576-target .rknn 在 RK3572 上能否跑通 (板端验证步骤 + 可执行判定口径)

> 版本: v1.0 (2026-11-06) · owner: sw-lead · 对应 issue: ISS-155 (demo 头号卡点) / ISS-147 (P0-1)
> 上游: `SW/RKNN_BUILD_ENV_RECOVERY.md` (2026-11-02, 环境恢复 + P0-1 闭合)
>
> ★**本单回答什么**: 上游单已把 **P0-1 闭死** (`rk3572` 不是任何已发布版 rknn-toolkit2 的合法
> `target_platform` ⇒ 必须用 `target_platform='rk3576'` 转换)。但**剩下的那条死结**——
> "**用 rk3576 target 转出来的 .rknn, 能不能在 RK3572 板子上跑通**"——**至今 0 次实测**。
>
> ★**本单交的是"板端拿到就能照抄执行的验证步骤 + 判定口径"**, **不是**"验证已通过"。
> ⇒ **板端结果一律标 `[0数据]`**, 直到真在板子上跑过。

---

## 0. 结论摘要 (先看这 6 行)

1. ★**P0-1 复验 (2026-11-06 实测)**: `rknn-toolkit2 2.3.2` 的 `config(target_platform='rk3572')`
   **仍然抛 `ValueError: Invalid target_platform 'rk3572'!`**; 同进程 `rk3576` / `rk3588` **rc=0**
   ⇒ ★**"升级 toolkit 就有 rk3572" 这条路彻底不存在** —— 上游结论成立, 本周复现。
2. ★**PC 侧转换链本周复跑 rc=0** (yolov5n@640): `load 0.18s` / `build(INT8) 38.2s` / 产物
   **4,989,367 B = 4.76 MiB** (装得进 15 MiB 板端槽位) / 量化 `w8a8 · channel`。
3. ★**PC 侧精度复现**: `acc` 步 **281 张 COCO val2017** → `TP=494 FP=765 FN=1623`
   → **P=0.3924 R=0.2333 F1=0.2927** ⇒ **与 11-02 基线逐位一致** (缓存键含指纹修复后有效)。
4. ★**板端实测 = 0 次**: 板子 `192.168.2.5` **不可达** (ping 100% 丢包 + ARP `INCOMPLETE`),
   本机无 `sshpass` ⇒ **本单无法闭合该验证**, 只能交步骤。
5. ⇒ **结论**: 本单把验证步骤写成 **一条命令 + 5 条判定**, 板子一到手即可执行; **本周状态 = `[0数据]`**。
6. ⇒ **升级为需要老板/硬件侧解锁的卡点**: 见 §6 (板子来源 = ISS-151 清单里的公开在售 RK357x 板,
   **Forlinx OK3572-C 首选** —— 一举两得: 既是本条的验证载体, 又是 demo Step1 的载体)。

---

## 1. ★ 前置条件 (缺一条就别开始 —— 否则跑出来的数不可用)

| # | 前置 | 怎么确认 | 缺了会怎样 |
|---|---|---|---|
| **P1** | **一块能启动的 RK3572 板/模组** | `uname -a` + `cat /proc/device-tree/compatible` 里含 `rk3572` | ★**根本没法测** (当前状态) |
| **P2** | **板端 RKNN runtime** (`librknnrt.so`) 版本号 | `strings /usr/lib/librknnrt.so \| grep -i version` + 包管理器版本 | 产物与 runtime 不兼容 ⇒ 加载失败, 白跑 |
| **P3** | **板端 Python + rknn-toolkit-lite2** (与 PC 侧 2.3.2 对齐) | `pip show rknn-toolkit-lite2` | 跑不了 `acc` 步 |
| **P4** | **本条 §3 的 `.rknn` 产物** (PC 侧转好, 带 sha256) | `sha256sum` 与 §2 清单比对 | 测的不是同一个产物 ⇒ 数不能用 |
| **P5** | **COCO val2017 抽 300 张 + instances 标注** | `ls /data/coco/val2017 \| wc -l` ≥ 300 且 `instances_val2017.json` 在 | 算不出 F1 ⇒ 只能测"能加载" |
| **P6** | ★**板端与 PC 侧用同一个 `.rknn`** (不许板端重转) | sha256 比对 | ★重转会掩盖"跨平台兼容"这个待验证命题本身 |

---

## 2. ★ PC 侧产物清单 (2026-11-06 实测, 可直接取用)

| 项 | 值 | 证据 |
|---|---|---|
| 转换链工具 | `rknn-toolkit2 2.3.2` (conda env `rknn`, python 3.10.22) | [实测] |
| **源 ONNX** | `~/Public/rknn_assets/yolov5n-sim.onnx` · **7,931,774 B** · sha16 `dfb5d060ca36fc27` · 640×640 · 245 节点 | [实测] |
| 切后处理模型 | `/tmp/rknn_bench/yolov5n-sim_heads_d730e558d3dfe25c.onnx` (缓存键含指纹) | [实测] |
| ★**`.rknn` 产物** | `/tmp/rknn_bench/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn` · **4,989,367 B = 4.76 MiB** | [实测] |
| 量化配置 | `w8a8` · 算法 `normal` · 方法 `channel` · **`target_platform='rk3576'`** | [实测] |
| 转换耗时 | `load 0.18s` + `build(INT8) 38.2s` ⇒ **总 40.7s** | [实测] |
| 校准集 | `/tmp/rknn_bench/dataset.txt` · **99 张** (自动补跑 calib 步生成) | [实测] |
| ★**PC 侧 F1 (基线)** | **281 张 COCO val2017** → TP=494 FP=765 FN=1623 → **P=0.3924 R=0.2333 F1=0.2927** | [实测] |

★**注意**: `/tmp` **会被系统清理** ⇒ ★**产物必须在下板前先拷到项目库** (`SW/artifacts/models/`) 并记 sha256,
否则板子到手时产物已经没了。

---

## 3. ★★ 板端验证步骤 (照抄执行, 5 步)

### 步骤 0 — 确认板子 + 记录环境 (必做, 否则数据不可追溯)

```bash
# 0.1 板子身份
uname -a
cat /proc/device-tree/compatible; echo
# 0.2 RKNN runtime 版本 (★P2 前置)
ls -l /usr/lib/librknnrt.so* 2>/dev/null
strings /usr/lib/librknnrt.so 2>/dev/null | grep -iE "version|rknn_api" | head -5
python3 -c "import importlib.metadata as m; print('lite2', m.version('rknn-toolkit-lite2'))"
# 0.3 供电与散热条件 (★影响降频 ⇒ 影响 NPU 耗时可比性)
cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null
```
★**0.3 必须记**: 眼镜腔体无主动散热 ⇒ 板端 NPU 耗时**与散热条件强相关** ⇒ 不记这个, 测出来的
S5 没有可比性 (ISS-129 明确要求"供电方式与散热条件"作为实测项之一)。

### 步骤 1 — 把 PC 侧产物搬上板 (不许在板上重转)

```bash
# 在 PC 侧
sha256sum /tmp/rknn_bench/yolov5n-sim_heads_d730e558d3dfe25c_rk3576_int8_heads.rknn
# 拷贝 (方式按现场: scp / u盘 / 串口), 然后在板上
sha256sum ./yolov5n_rk3576_int8_heads.rknn     # ★必须与 PC 侧逐字节相同
```

### 步骤 2 — 加载探针 (★**最先判的一条**: 能不能加载)

```bash
python3 - <<'PY'
from rknnlite.api import RKNNLite
import os
m = RKNNLite()
# ★RKNNLite 的 init 签名按板端 runtime 版本微调; 失败时先读错误串
ret = m.load_rknn("./yolov5n_rk3576_int8_heads.rknn")
print("load_rknn ret =", ret)
print("target_platform 回显:", m.get_sdk_version() if hasattr(m, "get_sdk_version") else "n/a")
PY
```
★**判据 N1**: `load_rknn` 返回 **0** ⇒ 通过; **非 0** ⇒ ★**失败**, 立刻抓错误串
(典型三类: "**Invalid target platform**" ⇒ 板端 runtime 也不认 rk3576 产物 / "**version mismatch**"
⇒ runtime 与 2.3.2 产物不匹配 / "**model invalid**" ⇒ 产物本身有问题)。

### 步骤 3 — 精度复现 (★**判据 N2**: 精度不塌)

```bash
# 板端跑 acc 步 (口径与 PC 侧完全一致: 逐类 IoU 贪心匹配, score_thr/IoU 参数照抄)
python3 SW/tools/rknn_bench.py acc --images 300 \
    --onnx /data/models/yolov5n-sim.onnx \
    --rknn ./yolov5n_rk3576_int8_heads.rknn
# ★口径: 必须是**同一套** COCO 抽图 (前 281 张有标注的) + 同一 score_thr + 同一 IoU 阈值
```

### 步骤 4 — NPU 纯耗时 (★**判据 N3**: 与预算对得上)

```bash
# 纯 NPU 耗时: ★必须只算网络执行, 不含 SDK 总耗时 (SOUL.md 铁律)
# 板端同时报两个数: t_npu (纯 NPU) 与 t_sdk_total (含反量化/搬运)
# 参考 A733: vip_run_network 27.19ms vs awnn_run total 36.51ms ⇒ 差 9.29ms = 25%
```

### 步骤 5 — 记录归档 (★不留证据 = 不算测过)

```bash
mkdir -p evidence/ISS155_$(date +%Y%m%d)
cp yolov5n_rk3576_int8_heads.rknn evidence/ISS155_$(date +%Y%m%d)/
sha256sum evidence/ISS155_$(date +%Y%m%d)/*.rknn | tee evidence/ISS155_$(date +%Y%m%d)/sha256.txt
# 环境 + 结果 + 散热条件全部落盘
```

---

## 4. ★★ 判定口径 (可执行, 5 条; 全部满足才算通过)

| # | 判据 | **通过线** | 不过线说明什么 | 证据等级 |
|---|---|---|---|---|
| **N1** | **能加载** | `load_rknn` ret == **0** | ★**跨平台兼容命题直接被否** ⇒ 唯一出路 = 换 SoC(RK3576) / 找原厂出 rk3572 专用编译 | [实测] (板端) |
| **N2** | **精度不塌** | 板端 F1 ≥ **PC 侧 F1 0.2927 − 0.05** ⇒ **≥ 0.2427** | 掉超过 0.05 ⇒ 量化在不同 NPU 实现上有偏 ⇒ 反量化路径不对 | [实测] (板端) |
| **N3** | **NPU 耗时对得上** | 板端 `t_npu` ≤ **RK3576 基线 8.87ms × (6/4) = 13.30ms** [推算] | ★**若 > 20.33ms ⇒ 命中老板 10-29 定的 T2 翻案条件 ⇒ 60ms 硬指标不保** (ISS-129) | [实测] (板端) vs [推算] (阈值) |
| **N4** | **两个数都报** | `t_npu` **和** `t_sdk_total` 都有, 且分开 | 只报一个 ⇒ 违反 SOUL.md 铁律 ⇒ 数字不可用 | [实测] |
| **N5** | **散热条件已记录** | 步骤 0.3 的温度 + 频率 + 供电方式都在证据里 | 没记 ⇒ N3 的数没有可比性 | [实测] |

★**通过线不许事后调**: 上表在**板子到手之前**就定死, 跑完只填数, 不改线。

### 4.1 ★ 三种结局与各自出路 (提前写好, 免得到时候现想)

| 结局 | 组合 | 结论 | 出路 (按代价从小到大) |
|---|---|---|---|
| **✅ 通过** | N1+N2+N3+N4+N5 全过 | ★**rk3576-target 路线成立** | 继续 demo 链; ★**但 60ms 仍要看 ISS-129 的实测 S5** |
| **⚠️ 部分通过** | N1 过 + **N3 不过** (> 20.33ms) | ★**命中 T2 翻案条件** ⇒ 60ms 硬指标在 RK3572 上不保 | ①降 OD 负载 (640×480@60→@30, 或换更小模型) ②ISP 侧降载 ③**回 RK3576** (74 分, 但面积装不下 ⇒ 须 PCB 厂确认 6 层板能否塞下) |
| **❌ 失败** | **N1 不过** (加载失败) | ★**跨平台兼容命题被否** | ①查板端 runtime 有无 rk3572 专用编译 ②**换 RK3576 做 demo 载体** (整链换 SoC, 代价大) ③改 CPU 推理 (yolov5n INT8 在 8×A72 不现实, 量化 int8 + NNAPI/ORT 可试) ⇒ ★**三条都贵** |

---

## 5. ★ 本周 PC 侧已做完的部分 (板端不用重做)

| 步骤 | 状态 | 证据 |
|---|---|---|
| P0-1 `rk3572` 非法 target 复验 | ✅ **本周复现** (2.3.2, 2 个 conda env, `ValueError`) | §0-1 |
| PC 侧转换 (`target_platform='rk3576'`) | ✅ **本周复跑 rc=0** | §2 |
| PC 侧 F1 基线 | ✅ **本周复现 0.2927** (逐位一致) | §2 |
| 板端 N1~N5 | ❌ **板子不可达 ⇒ 0 次** | §6 |

★**这三条的意义**: 板子一到手, **只需要跑步骤 0~5**, PC 侧不用重来 ⇒ **省 1~2 人天**。

---

## 6. ★★ 当前卡点 = 需要老板/硬件侧解锁 (不假装有结论)

### 6.1 卡点本体

| 项 | 事实 | 证据 |
|---|---|---|
| 板子不可达 | `ping 192.168.2.5` → **100% 丢包**; `ip neigh` → **INCOMPLETE** (ARP 都没应答) | [实测] 2026-11-06 10:35 |
| 本机缺 sshpass | `TOOLS.md` 写的 `sshpass -p <BOARD_SSH_PASSWORD>` 调用方式**在这台机上不可用** | [实测] |
| mDNS 不解析 | `radxa-cubie-a7s.local` 不解析 ⇒ IP 还会变 | 上游单 2026-11-02 实测 |
| ★**板端 runtime 版本未知** | 不知道板端 `librknnrt.so` 版本 ⇒ 不知道 2.3.2 产物能不能加载 (P2 前置未满足) | ★**[0数据]** |

### 6.2 ★ 解锁路径 (走项目总工, sw-lead 不自己买板)

| 方案 | 内容 | 代价 | 建议 |
|---|---|---|---|
| **★推荐** | **用 ISS-151 清单里的公开在售 RK357x 板** (**Forlinx OK3572-C 首选** —— 项目已经在用它做 demo Step1 载体) | 一次采购, 但**一举两得**: 既解本条验证, 又是 demo 载板 | ★**推荐** |
| 备选 A | 等 Radxa A7S 回到同一网段 + 装 sshpass | 0 采购, 但**时间不可控** | 顺手做 (装 sshpass), 不作为主线 |
| 备选 B | 借/租一块 RK3576 板先验 N1/N2 (验"rk3576 产物在 RK3576 上必然通", 顺带测 N3 基线) | 低 | ★**可立刻做**, 但**不能代替 N1** (那是跨平台命题) |

⇒ ★**N1 是"rk3576 产物能不能在 RK3572 上加载"这个特定命题** ⇒ ★**用 RK3576 板子测, 无论结果如何都不构成 N1 的证据**
(那只是同平台自洽) ⇒ ★**必须 RK3572 板**。

### 6.3 ★ 对 boss 的一句话

> 头号卡点不是"软件写得好不好", 是"**模型能不能上板**"。
> PC 侧我已经把能做的全做完了 (转换 rc=0 · 4.76 MiB · F1 0.2927 复现),
> ★**剩下的唯一一件事是给我一块能启动的 RK3572 板** —— 板子一到手, **一条命令 + 5 条判定** 就能结案。

---

## 7. 自证复现命令 (一条命令)

```bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
# ★本单所有 PC 侧数字的复现 (板端步骤见 §3)
python3 SW/tools/rknn_bench.py convert --onnx /home/yuewuya/Public/rknn_assets/yolov5n-sim.onnx
python3 SW/tools/rknn_bench.py acc --onnx /home/yuewuya/Public/rknn_assets/yolov5n-sim.onnx --images 300
```

★**注意**: `/tmp/rknn_bench` **会被系统清理** ⇒ 重跑前先 `mkdir -p /tmp/rknn_bench`;
产物落 `/tmp/rknn_bench/*.rknn`, **用完立刻拷到 `SW/artifacts/models/` 并记 sha256**。

---

> **本单纪律声明**: 本单**未修改** `PROJECT_TRACKER.md` / `state/issue_log.yaml` / `HW/` / `MECH/` /
> 网表 / 板文件 / 任何既有 SW 脚本; **未联系任何供应商**; **未下单**。
> 板端结果一律标 **`[0数据]`**; 所有 PC 侧结论标 **[实测]** 并给复现命令。
